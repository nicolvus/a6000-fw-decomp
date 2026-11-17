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
