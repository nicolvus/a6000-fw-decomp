"""E2E-12 / G75 T34: canal UART de la montura (PL011 `0xf2001000` + DMAC `0xf0102000`) en la LIRO VM y trama `CS_CHECK_CMD` del cuerpo."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))


def _vm():
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    from test_avcam_ee_start import _corre

    return _corre()


def test_cs_check_cmd_sale_por_dmac_y_pl011_con_formato_bl() -> None:
    """MEDIDO: tras el handshake, `0x43a1c5f4` programa el DMAC (canal 1, 12 palabras `0x43e0bd30` → `0xf2001000`) y activa TXDMAE; el modelo lo mueve al PL011 y
    el objetivo recoge la trama `F0 len 00 tipo param ID datos cksum16 55` (tipo 2 = síncrono, ID 1 = CS_CHECK_CMD, checksum = suma de `buf[1:len-3]`).
    Antes de T34 la tarea `tsk0x62` moría en `0x43991d1a` con INSN_INVALID (ITSTATE roto por un gancho Python de lectura de FR dentro de `ldrhne`)."""
    vm = _vm()
    txt = "\n".join(vm.log)
    assert "UC_ERR_INSN_INVALID" not in txt
    assert "[BL]DRV_SEND[1]" in txt
    f = vm.objetivo.tramas[0]
    assert (f[0], f[1], len(f), f[3], f[5], f[-1]) == (0xF0, 0x29, 0x29, 2, 1, 0x55)
    assert int.from_bytes(f[-3:-1], "little") == sum(f[1:-3]) & 0xFFFF
    assert f[6:14] == bytes.fromhex("ffffffffffffff7f")  # mapa de comandos que el cuerpo declara
    assert vm.irqs[0xAE] >= 1  # fin de transferencia del DMAC canal 1 (irq 0xad+canal) → arma el plazo de respuesta (temporizador 0xa)


def test_pl011_rx_pasa_por_dmac_y_deja_el_resto_en_la_fifo() -> None:
    """INFERENCIA (umbral 1/2 de la FIFO de 16 B): con RX-DMA armado (canal 0, 0x200 transferencias de 1 B) llegan 41 B; el DMAC vacía la FIFO hasta
    quedar por debajo de la ráfaga (7 B) y el PL011 levanta el tiempo de espera de recepción (RT, bit 6 de RIS)."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    import montura as M

    vm = L.carga(L.AVCAM, L.BK)
    u = vm.uart_montura
    base = M.DMAC + 0x100
    buf = vm.malloc(0x100)
    vm.wr(base, M.UART)
    vm.wr(base + 4, buf)
    vm.wr(base + 0xC, 0x9940B200)  # 0x200 transferencias, origen 1 B, destino 4 B (empaquetado)
    vm.wr(base + 0x10, 0x100D019)
    vm.wr(M.UART + 0x30, 0x301)
    vm.wr(M.UART + 0x48, 1)
    datos = bytes(range(41))
    u.recibe(datos)
    u.avanza(vm)
    assert bytes(vm.uc.mem_read(buf, 34)) == datos[:34]
    assert len(u.fifo) == 7 and u.ris & M.RTIS
    assert vm.rd(base + 4) == buf + 34 and vm.rd(base + 0xC) & 0xFFF == 0x200 - 34
    assert vm.rd(M.UART + 0x18) & 0x10 == 0  # RXFE bajo: quedan datos para la lectura por PIO
    assert vm.rd(M.UART + 0x3C) & M.RTIS


def test_pl011_tx_por_dmac_completa_y_avisa() -> None:
    """MEDIDO en el modelo: un canal memoria → UART con TXDMAE y TXE habilitados vuelca `n·ancho` bytes al objetivo, baja el bit de habilitación y sube IntStatus."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    import montura as M

    vm = L.carga(L.AVCAM, L.BK)
    u = vm.uart_montura
    vistos: list[bytes] = []
    u.al_transmitir = vistos.append
    src = vm.malloc(0x40)
    vm.uc.mem_write(src, bytes(range(0x30)))
    base = M.DMAC + 0x120  # canal 1
    vm.wr(base, src)
    vm.wr(base + 4, M.UART)
    vm.wr(base + 0xC, 0x9609900C)  # 12 palabras de 32 bit
    vm.wr(base + 0x10, 0x100CB41)
    vm.wr(M.UART + 0x30, 0x301)
    vm.wr(M.UART + 0x48, 2)
    u.avanza(vm)
    assert b"".join(vistos) == bytes(range(0x30))
    assert vm.rd(base + 0x10) & 1 == 0 and vm.rd(M.DMAC) >> 1 & 1 and u.ris & M.TXIS


def test_el_flanco_de_data_in_dispara_la_irq_0x7e_y_el_cierre_de_rx() -> None:
    """VERIFICADO (irqs.h del núcleo OSS: IRQ_GPIO_BASE 121 + bit; puerto 0 = GPIO_S → DATA_IN (0,5) = 0x7e) y MEDIDO: el manejador de 0x7e (tabla `0x43fd5e10`,
    thunk `0x43ae746f` → `0x436e8314` → cierre de RX `0x43ada04c`) corre con los flancos de subida de DATA_IN. Con `ref_sem` modelado (antes devolvía semcnt = -1) el DMAC
    se cierra/abre sin los avisos `pbl_dmac_close() is not open` / `pbl_dmac_open() is open` del controlador."""
    vm = _vm()
    txt = "\n".join(vm.log)
    assert vm.irqs[0x7E] >= 3  # CS_CHECK_CMD (2 flancos del acoplamiento) y su respuesta
    assert "pbl_dmac_open() is open" not in txt and "irq0x7e: LOG [DMAC0]pbl_dmac_close() is not open" not in txt


def test_el_objetivo_contesta_el_acoplamiento_y_la_montura_llega_a_5() -> None:
    """MEDIDO (E2E-12, T35): el objetivo contesta CS_CHECK_CMD, ATTACH_INFO1/2, UART_HZ, CS_POWER, STARTUP_INFO, SYSTEM_HZ, CS_RESET y CS_CREDIT por UART + flanco de DATA_IN;
    el analizador `0x436e2678` las acepta (`SYNC RECIVE`), `[0x43e81240]` pasa 0 → 4 → 1 → 5 y no hay SYNC TIMEOUT."""
    vm = _vm()
    txt = "\n".join(vm.log)
    for marca in ("[L->B]CS_CHECK_CMD", "[L->B]ATTACH_INFO1", "[L->B]ATTACH_INFO2", "[L->B]STARTUP_INFO", "[L->B]SYSTEM_HZ", "[L->B]CS_RESET", "[L->B]CS_CREDIT", "LENS_WEAR_END",
                  "UART_HS_COMPLETE"):
        assert marca in txt, marca
    for malo in ("SYNC TIMEOUT", "DETACH RETRY", "UART_HZ NG", "_NG"):
        assert malo not in txt, malo
    assert vm.rd(0x43E81240) == 5
    assert vm.rd(0x4401B1F0) == 0xE1  # 1500k, como la RAM real


def test_modulo_11_sube_a_0xc01_y_no_vuelve() -> None:
    """MEDIDO: con la montura en 5 la puerta `0x436e5828` deja pasar la orden 0xC01 una vez y el módulo 11 no retrocede a 0xC00 (antes lo hacía con cada reintento)."""
    vm = _vm()
    cambios = [ln.split("LIF Command Change : ")[1] for ln in vm.log if "LIF Command Change" in ln]
    assert cambios[:2] == ["0x0 >>> 0xC00", "0xC00 >>> 0xC01"] and "0xC01 >>> 0xC00" not in cambios and "0x0 >>> 0xC00" not in cambios[1:]


def test_respuestas_del_objetivo_tienen_formato_bl_y_el_tamano_del_descriptor() -> None:
    """VERIFICADO contra el descriptor `{id,size,extra}` de `0x4401ca4a` (static en av-cam.bin): cada respuesta mide `extra+8` y su checksum es el del cuerpo."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    if not L.AVCAM.exists():
        pytest.skip("falta av-cam.bin")
    import struct

    import objetivo as O

    img = L.AVCAM.read_bytes()
    for ident, extra in ((1, 33), (7, 35), (8, 202)):
        assert struct.unpack_from("<HHH", img, 0x4401CA4A + 6 * ident - L.BASE) == (ident, {1: 33, 7: 2, 8: 9}[ident], extra)
        f = O.respuestas(O.trama(2, ident, bytes(extra - 1 if ident == 1 else {7: 1, 8: 8}[ident])), extra)[0]
        assert len(f) == extra + 8 and f[0] == 0xF0 and f[-1] == 0x55 and f[5] == ident
        assert int.from_bytes(f[-3:-1], "little") == sum(f[1:-3]) & 0xFFFF


def test_barrera_del_guion_es_el_byte_0x43eaeecd() -> None:
    """MEDIDO (E2E-12b): la lista `0x43ede340` (índice 28) espera que el estado del módulo 3 (`0x43e9c7d8`) pase de 0x325 a 0x326; esa transición (`0x43859d2a`) exige
    `[0x43eaee84+0x49]`==1 (campo +7 del bloque de entrada de `0x43b09d10`). Con ese byte a 1 el guion llega al final y `[0x43ede338]` pasa a 2 (el paso que acepta `0x3003`).
    Diagnóstico: el productor real del byte aún no está identificado (E2E-12c)."""
    import liro_vm as L

    vm = _vm()
    assert vm.rd(0x43EAEECD, 1) == 0 and vm.rd(0x43E9C7D8, 2) == 0x325 and vm.rd(0x43EDE338) == 0
    for _ in range(2):  # el índice del guion avanza 28→30→42 (una barrera por ronda de V)
        vm.wr(0x43EAEECD, 1, 1)
        vm.limite += 1000
        L.planifica(vm, 100_000_000)
    assert vm.rd(0x43EDE338) == 2


def test_orden_de_arranque_0x3006_lleva_av_cam_al_paso_1_y_el_modulo_3_pasa_por_0x301() -> None:
    """MEDIDO (E2E-12c): la RAM real en reposo tiene `[0x43ede338]`=1, última petición `0x3006` y lista `0x43bf3648` ([2,0x1b,1]); la captura EE_START (seq 2..15) no trae
    esa orden (seq 0/1). Entregada antes (formato INFERIDO de la `0x3024`: `00 00 id_lo id_hi seq 00 00 80 00`), av-cam recorre 0→0x1b→1, la contesta y el módulo 3 pasa por `0x301`
    (`0x43844f e0`→`0x43b09b4e`→`0x43b098c0`, reinicio de parámetros que la VM sin esa orden nunca ejecutaba). La barrera del guion 1→2 (byte `0x43eaeecd`) sigue abierta."""
    pytest.importorskip("unicorn")
    from unicorn import UC_HOOK_CODE

    import liro_vm as L
    import puente as P
    from test_avcam_ee_start import _secuencia

    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    vm, t0 = P.arranca()
    vm.limite = t0
    hits: dict[int, int] = {}
    for a in (0x43B098C0,):
        vm.uc.hook_add(UC_HOOK_CODE, lambda uc, ad, sz, u: hits.__setitem__(ad, hits.get(ad, 0) + 1), None, a, a + 2)
    cab = bytes.fromhex("000000000100000002000200")

    def envia(q: int, c: bytes, d: bytes) -> None:
        vm.limite += 400
        L.planifica(vm, 20_000_000)
        m = vm.malloc(max(len(d), 0x40) + 12 + 0x20) + 12
        vm.uc.mem_write(m - 12, c)
        vm.uc.mem_write(m, d)
        vm.msz[m] = len(d)
        L.entrega(vm, q, m)

    envia(0x30001, cab, bytes([0, 0, 0x06, 0x30, 0x80, 0, 0, 0x80, 0]))
    for q, c, d in _secuencia():
        envia(q, c, d)
    vm.limite += 3000
    L.planifica(vm, 50_000_000)
    assert vm.rd(0x43EDE338) == 1  # paso de reposo, como la RAM real
    assert hits.get(0x43B098C0, 0) >= 1
    assert vm.rd(0x43EAEECD, 1) == 0  # barrera 1→2 (E2E-12c) todavía sin productor
