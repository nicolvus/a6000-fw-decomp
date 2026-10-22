"""Tests de S132 — el módulo `[CLK_CTRL]` (66 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: se lee el firmware, se resuelven los pares PIC y se
comprueban direcciones, textos y recuentos. Si una dirección del módulo cambia,
los tests fallan.

Regla de referencias: **estricta** (canónica del repo) — para cada `add rX, pc`
se toma el `ldr rX, [pc, #imm]` más cercano hacia atrás sobre el mismo registro;
destino = valor_del_pool + (dir_add + 4).

Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
GLOBAL_REFS = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
JSON_S132 = "analysis/s132_clk_ctrl/clk_ctrl.json"
JSON_CALLERS = "analysis/s132_clk_ctrl/callers.json"

PREFIX = "[CLK_CTRL]"


# ----------------------------------------------------------------- utilidades
def _data():
    return (ROOT / BIN_PATH).read_bytes()


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _cstr(data, vaddr):
    off = vaddr - BASE_VADDR
    end = data.index(b"\x00", off)
    return data[off:end].decode("latin1")


def _bl_target(data, vaddr):
    """Destino de una instrucción `bl` (Thumb-2, 32 bits)."""
    h1 = _u16(data, vaddr)
    h2 = _u16(data, vaddr + 2)
    assert (h1 >> 11) == 0x1E, hex(h1)          # op = BL
    assert (h2 & 0xD000) == 0xD000, hex(h2)
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    imm11 = h2 & 0x7FF
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    v = (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        v -= 1 << 24
    return (vaddr + 4 + v) & 0xFFFFFFFF


def _pic_dest(data, add_addr):
    """Destino de un `add rX, pc` según la regla estricta: el `ldr rX,[pc,#imm]`
    más cercano hacia atrás sobre el mismo registro (ventana 4 KB)."""
    h = _u16(data, add_addr)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(h)
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    best = None
    a = add_addr - 2
    while a > add_addr - 4096:
        hh = _u16(data, a)
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
            best = a
            break
        if (hh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            if ((h2 >> 12) & 0xF) == reg:
                best = a
                break
        a -= 2
    assert best is not None, f"sin ldr para r{reg} antes de 0x{add_addr:x}"
    hh = _u16(data, best)
    if (hh & 0xF800) == 0x4800:
        pool = ((best + 4) & ~3) + (hh & 0xFF) * 4
    else:
        h2 = _u16(data, best + 2)
        pool = ((best + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    return (_u32(data, pool) + (add_addr + 4)) & 0xFFFFFFFF


def _insn(data, vaddr):
    """(mnemático, operandos) de la instrucción Thumb en `vaddr`."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    off = vaddr - BASE_VADDR
    for i in md.disasm(data[off:off + 4], vaddr):
        return (i.mnemonic, i.op_str)
    raise AssertionError(f"no se pudo desensamblar 0x{vaddr:x}")


def _imm_last_before(data, vaddr, reg, span=12):
    """Valor del último `mov <reg>, #inmediato` anterior a `vaddr` (None si no hay)."""
    for a in range(vaddr - 2, vaddr - span - 1, -2):
        try:
            mnem, ops = _insn(data, a)
        except AssertionError:
            continue
        if not mnem.startswith("mov") or not ops.startswith(f"r{reg}, #"):
            continue
        try:
            return int(ops.split("#")[1].strip(), 0)
        except ValueError:
            continue
    return None


def _imm_near(data, vaddr, reg, value, span=12):
    """True si en la ventana [vaddr-span, vaddr+span] hay un
    `mov <reg>, #value` (inmediato exacto)."""
    for a in range(vaddr - span, vaddr + span, 2):
        try:
            mnem, ops = _insn(data, a)
        except AssertionError:
            continue
        if not mnem.startswith("mov"):
            continue
        if not ops.startswith(f"r{reg}, #"):
            continue
        try:
            val = int(ops.split("#")[1].strip(), 0)
        except ValueError:
            continue
        if val == value:
            return True
    return False


def _json(name=JSON_S132):
    return json.loads((ROOT / name).read_text())


def _all_clk_strings(data):
    """[(vaddr, texto)] de todas las cadenas [CLK_CTRL]."""
    return [(BASE_VADDR + m.start(), m.group().decode("latin1"))
            for m in re.finditer(rb"\[CLK_CTRL\][\x20-\x7e]*", data)]


# ----------------------------------------------------------------- inventario
# Las 66 trazas: vaddr -> texto exacto.
TRAZAS = {
    0x43C3A1DF: "[CLK_CTRL]: Call:ddl_clkctrl_get_clk_chg_enable(0x0%x),ret=0x%0x",
    0x43C3A220: "[CLK_CTRL]: Call:ddl_clkctrl_unlock_sync_signal(0x0%x),ret=0x%0x",
    0x43C3A261: "[CLK_CTRL]: Call:ddl_clkctrl_lock_sync_signal(0x0%x,0x0%x),ret=0x%0x",
    0x43C3A2A6: "[CLK_CTRL]: Call:ddl_clkctrl_set_sysv_delay_changing(0x0%x,0x0%x),ret=0x%0x",
    0x43C3A2F2: "[CLK_CTRL]: Call:ddl_clkctrl_set_sysv_delay(0x0%x,0x0%x),ret=0x%0x",
    0x43C3A335: "[CLK_CTRL]: Call:ddl_clkctrl_set_sync_signal(0x0%x,0x0%x),ret=0x%0x",
    0x43C3A379: "[CLK_CTRL]: Call:ddl_clkctrl_set_sync_initial_signal(0x0%x),ret=0x%0x",
    0x43C3A3BF: "[CLK_CTRL]: Call:ddl_clkctrl_set_sysv_initial_delay(0x0%x,0x0%x),ret=0x%0x",
    0x43C3A40A: "[CLK_CTRL]: Call:ddl_clkctrl_close_dly(0x0%x),ret=0x%0x",
    0x43C3A442: "[CLK_CTRL]: Call:ddl_clkctrl_open_dly(0x0%x),ret=0x%0x",
    0x43C3A479: "[CLK_CTRL]: Call:ddl_clkctrl_close_clk(0x0%x),ret=0x%0x",
    0x43C3A4B1: "[CLK_CTRL]: Call:ddl_clkctrl_open_clk(0x0%x),ret=0x%0x",
    0x43C3A4E8: "[CLK_CTRL]: [ERR]OSAL_SEM_ERR %08x L=%d",
    0x43C3A510: "[CLK_CTRL]: [ERR]State Error:0x%02x",
    0x43C3A534: "[CLK_CTRL]: State:STATE_INIT1(InitDelay)",
    0x43C3A55D: "[CLK_CTRL]: State:STATE_NORMAL(InitSignal)",
    0x43C3A588: "[CLK_CTRL]: State:STATE_LOCK",
    0x43C3A5A5: "[CLK_CTRL]: lock_sync_signal subsystem = %x",
    0x43C3A5D1: "[CLK_CTRL]: unlock_sync_signal subsystem = %x",
    0x43C3A5FF: "[CLK_CTRL]: Tsk ClkCtrl Initial",
    0x43C3A61F: "[CLK_CTRL]: Main routine start!!",
    0x43C3A640: "[CLK_CTRL]: [ERR] osal rcv err %08x L=%d",
    0x43C3A669: "[CLK_CTRL]: [ERR]osal_sig_sem 0x%08x L=%d",
    0x43C3A693: "[CLK_CTRL]: set sync signal... clk = %d",
    0x43C3A6BB: "[CLK_CTRL]: [ERR]osal_try_wai_sem 0x%08x L=%d",
    0x43C3A6E9: "[CLK_CTRL]: tsk state = STATE_CHANGE_CLK , L = %d",
    0x43C3A71B: "[CLK_CTRL]: CHANGE_CLK dly 0x%x -> 0x%x , clk 0x%x -> 0x%x : change_vfc=0x%x",
    0x43C3A768: "[CLK_CTRL]: tsk state = STATE_CHANGE_CLK_LOCKING , L = %d",
    0x43C3A7A2: "[CLK_CTRL]: CHANGE_CLK2 dly %x -> %x , clk %x -> %x",
    0x43C3A7D6: "[CLK_CTRL]: clk_now=%d, clk_next=%d, change_vfc=0x%x, L=%d",
    0x43C3A811: "[CLK_CTRL]: ClkChgExec at %x clk=%x, delay=%x->%x",
    0x43C3A843: "[CLK_CTRL]: tsk state = %d(%d:NORMAL,%d:LOCK) , L = %d",
    0x43C3A87A: "[CLK_CTRL]: clk_now=%x, clk_next=%x, delay_now=%x, change_vfc=0x%x, L=%d",
    0x43C3A8C3: "[CLK_CTRL]: DelayChgExec at 0x%x, delay=%x",
    0x43C3A8EE: "[CLK_CTRL]: [ERR]osal_wai_sem_tmo %08x L=%d",
    0x43C3A91A: "[CLK_CTRL]: open subsytem = 0x%04x",
    0x43C3A93D: "[CLK_CTRL]: [ERR]Busy!! 0x%04x already opened, 0x%04x can't open",
    0x43C3A97E: "[CLK_CTRL]: close subsytem = 0x%04x",
    0x43C3A9A2: "[CLK_CTRL]: [ERR]Busy!! 0x%04x already opend...0x%04x can't close",
    0x43C3A9E4: "[CLK_CTRL]: [ERR]0x%04x request open... CLK already opend by 0x%04x",
    0x43C3AA28: "[CLK_CTRL]: 0x%04x request open... DELAY already opend by 0x%04x",
    0x43C3AA69: "[CLK_CTRL]: vph stat:%d,mode:%d",
    0x43C3AA89: "[CLK_CTRL]: 10Count:%d, subVFC:%d",
    0x43C3AAAB: "[CLK_CTRL]: 10Count:%d",
    0x43C3AAC2: "[CLK_CTRL]: Now:0x%08x,target:0x%08x",
    0x43C3AAE7: "[CLK_CTRL]: Send HTP at 0x%08x",
    0x43C3AB06: "[CLK_CTRL]: [ERR] osal_try_valloc_msg 0x%0x",
    0x43C3AB32: "[CLK_CTRL]: [ERR] osal_snd_msg 0x%0x",
    0x43C3AB57: "[CLK_CTRL]: [ERR] osal_free_msg 0x%0x",
    0x43C3AB7D: "[CLK_CTRL]: [ERR] osal_rcv_msg 0x%0x",
    0x43C3ABA2: "[CLK_CTRL]: [ERR] unknown message?? src=0x%0x",
    0x43C3ABD0: "[CLK_CTRL]: Receive Message from Master src=0x%0x",
    0x43C3AC02: "[CLK_CTRL]: targetVfc=0x%0x, delay_req=0x%0x",
    0x43C3AC2F: "[CLK_CTRL]: m_vfc.main=0x%0x, m_vfc.sub=0x%0x",
    0x43C3AC5D: "[CLK_CTRL]: [ERR] SndMsgPublic request??",
    0x43C3AC86: "[CLK_CTRL]: Send Message to Slave 0x%0x",
    0x43C3AEF8: "[CLK_CTRL]: [ERR]osal_try_wai_sem %08x L=%d",
    0x43C3AF24: "[CLK_CTRL]: [ERR]CLKCTRL_ERR_BUSY...State is LOCK L=%d",
    0x43C3AF5B: "[CLK_CTRL]: Delay is no change(delay=%x) L=%d",
    0x43C3AF89: "[CLK_CTRL]: set sysv delay subsystem = %x , delay = %d",
    0x43C3AFC0: "[CLK_CTRL]: [ERR]dly_now = 0.5 L=%d",
    0x43C3AFE4: "[CLK_CTRL]: [ERR]clk_now = %x L=%d",
    0x43C3B007: "[CLK_CTRL]: [ERR]Not Changing state= %x L=%d",
    0x43C3B034: "[CLK_CTRL]: clk_now=%d, ret=%d, id=0x%x, clk_req=%d, L=%d",
    0x43C3B06E: "[CLK_CTRL]: [ERR]normal_delay MAX OVER:0x%08x",
    0x43C3B09C: "[CLK_CTRL]: [ERR]special_delay MAX OVER:0x%08x",
}

# sin referencia (regla estricta) ni puntero absoluto
SIN_REF = (0x43C3A2A6, 0x43C3AFC0, 0x43C3AFE4, 0x43C3B007)

# (cadena, sitio PIC) verificados a mano por desensamblado
PICOS = [
    (0x43C3A1DF, 0x4359EE48), (0x43C3A220, 0x4359EEA2),
    (0x43C3A261, 0x4359EEFC), (0x43C3A2F2, 0x4359EF52),
    (0x43C3A335, 0x4359EFAE), (0x43C3A379, 0x4359F016),
    (0x43C3A3BF, 0x4359F068), (0x43C3A40A, 0x4359F0B2),
    (0x43C3A442, 0x4359F0FA), (0x43C3A479, 0x4359F142),
    (0x43C3A4B1, 0x4359F18A), (0x43C3A534, 0x4359F314),
    (0x43C3A55D, 0x4359F3C0), (0x43C3A588, 0x4359F556),
    (0x43C3A5A5, 0x4359F580), (0x43C3A5D1, 0x4359F632),
    (0x43C3A5FF, 0x4359F7BA), (0x43C3A61F, 0x4359F7E2),
    (0x43C3A693, 0x4359F922), (0x43C3A6E9, 0x4359F9F0),
    (0x43C3A71B, 0x4359FA14), (0x43C3A768, 0x4359FA46),
    (0x43C3A7A2, 0x4359FAA2), (0x43C3A7D6, 0x4359FAC2),
    (0x43C3A811, 0x4359FB70), (0x43C3A843, 0x4359FBC2),
    (0x43C3A87A, 0x4359FBE4), (0x43C3A8C3, 0x4359FC4E),
    (0x43C3A91A, 0x4359FDE4), (0x43C3A93D, 0x4359FDFE),
    (0x43C3A97E, 0x4359FE98), (0x43C3A9A2, 0x4359FEB2),
    (0x43C3A9E4, 0x4359FF0E), (0x43C3AA28, 0x4359FF56),
    (0x43C3AA69, 0x435A00AC), (0x43C3AA89, 0x435A00B8),
    (0x43C3AAAB, 0x435A016C), (0x43C3AAC2, 0x435A02A2),
    (0x43C3AAE7, 0x435A0306), (0x43C3AB7D, 0x435A05CC),
    (0x43C3ABD0, 0x435A064E), (0x43C3AC5D, 0x435A0758),
    (0x43C3AC86, 0x435A07B2), (0x43C3AF24, 0x435A0DEE),
    (0x43C3AF5B, 0x435A0E38), (0x43C3AF89, 0x435A0E5E),
    (0x43C3B034, 0x435A0FDC), (0x43C3B06E, 0x435A115C),
    (0x43C3B09C, 0x435A1174),
]


class TestInventario:
    def test_hay_66_trazas_y_son_las_esperadas(self):
        data = _data()
        found = dict(_all_clk_strings(data))
        assert len(found) == 66
        assert set(found) == set(TRAZAS)

    @pytest.mark.parametrize("vaddr,text", sorted(TRAZAS.items()))
    def test_texto_exacto_en_su_direccion(self, vaddr, text):
        data = _data()
        assert _cstr(data, vaddr) == text
        # y no hay otra copia del texto (terminado en NUL) en la imagen
        assert data.count(text.encode("latin1") + b"\x00") == 1

    def test_bloque_contiguo(self):
        data = _data()
        vaddrs = sorted(v for v, _ in _all_clk_strings(data))
        assert vaddrs[0] == 0x43C3A1DF
        assert vaddrs[-1] == 0x43C3B09C
        # todas empiezan por "[CLK_CTRL]: "
        assert all(t.startswith("[CLK_CTRL]: ") for _, t in _all_clk_strings(data))

    def test_sin_apariciones_de_obturador(self):
        """El módulo no habla del obturador: no hay obturador electrónico aquí."""
        data = _data()
        for v, texto in _all_clk_strings(data):
            t = texto.lower()
            assert "shut" not in t
            assert "silen" not in t
            assert "imager" not in t


class TestReferencias:
    @pytest.mark.parametrize("s,site", PICOS)
    def test_par_pic_resuelve_a_la_cadena(self, s, site):
        data = _data()
        assert _pic_dest(data, site) == s
        assert _cstr(data, _pic_dest(data, site)) == TRAZAS[s]

    def test_mapa_global_estricto_coincide(self):
        refs = json.loads((ROOT / GLOBAL_REFS).read_text())
        data = _data()
        total = 0
        for v, _t in _all_clk_strings(data):
            sites = refs.get(f"0x{v:x}", [])
            total += len(sites)
            for s in sites:
                assert _pic_dest(data, s) == v
        assert total == 85

    def test_cuatro_cadenas_muertas(self):
        refs = json.loads((ROOT / GLOBAL_REFS).read_text())
        data = _data()
        for v in SIN_REF:
            assert refs.get(f"0x{v:x}", []) == []
            # ni puntero absoluto de 4 bytes
            assert data.count(struct.pack("<I", v)) == 0
            # pero el texto sí existe
            assert _cstr(data, v).startswith("[CLK_CTRL]: ")

    def test_solo_62_de_66_referenciadas(self):
        refs = json.loads((ROOT / GLOBAL_REFS).read_text())
        data = _data()
        ref = [v for v, _ in _all_clk_strings(data) if refs.get(f"0x{v:x}")]
        assert len(ref) == 62
        assert len(set(ref) & set(SIN_REF)) == 0


class TestMaquinaDeEstados:
    """Valores del estado (u8 en +0x04 de la estructura de estado)."""

    def test_state_init1(self):
        data = _data()
        assert _u16(data, 0x4359F308) == 0x2101      # movs r1,#1
        assert _bl_target(data, 0x4359F30A) == 0x43A48772   # str r1,[r0,#4]

    def test_state_normal(self):
        data = _data()
        assert _u16(data, 0x4359F3B4) == 0x2102      # movs r1,#2
        assert _bl_target(data, 0x4359F3B6) == 0x43A48772

    def test_state_change_clk(self):
        data = _data()
        assert _insn(data, 0x4359F9DE) == ("movs", "r3, #3")
        assert _insn(data, 0x4359F9E0) == ("str", "r3, [r0, #4]")

    def test_state_change_clk_locking(self):
        data = _data()
        assert _insn(data, 0x4359FA34) == ("movs", "r3, #4")
        assert _insn(data, 0x4359FA36) == ("str", "r3, [r0, #4]")

    def test_state_lock(self):
        data = _data()
        assert _u16(data, 0x4359F548) == 0x2105      # movs r1,#5
        assert _bl_target(data, 0x4359F54A) == 0x43A48772

    def test_comparacion_estado_lock(self):
        data = _data()
        # cmp r0,#5 en 0x435a0dde -> "CLKCTRL_ERR_BUSY...State is LOCK"
        assert _u16(data, 0x435A0DDE) == 0x2805


class TestApiDdl:
    """Las 14 entradas de la API, la tabla y el despachador."""

    TABLA = [
        (0x43C3ACB7, "0)ddl_clkctrl_open_clk(id)\n"),
        (0x43C3ACD3, "1)ddl_clkctrl_close_clk(id)\n"),
        (0x43C3ACF0, "2)ddl_clkctrl_open_dly(id)\n"),
        (0x43C3AD0C, "3)ddl_clkctrl_close_dly(id)\n"),
        (0x43C3AD29, "4)ddl_clkctrl_set_sync_signal(id , clk)"),
        (0x43C3AD51, "5)ddl_clkctrl_set_sysv_delay(id , delay)"),
        (0x43C3AD7A, "6)ddl_clkctrl_lock_sync_signal(id)"),
        (0x43C3AD9D, "7)ddl_clkctrl_unlock_sync_signal(id)"),
        (0x43C3ADC2, "8)ddl_clkctrl_set_sysv_initial_delay(normal,special)"),
        (0x43C3ADF7, "9)ddl_clkctrl_set_sync_initial_signal(CLKTYPE)"),
        (0x43C3AE26, "10)ddl_clkctrl_printf_info"),
        (0x43C3AE41, "12)total test clk->cly id,clk,dly_tsk"),
        (0x43C3AE67, "13)total test clk->lock id,clk"),
        (0x43C3AE86, "14)total test lock->clk id,clk"),
    ]

    @pytest.mark.parametrize("vaddr,text", TABLA)
    def test_entrada_de_la_tabla(self, vaddr, text):
        assert _cstr(_data(), vaddr) == text

    def test_call_cb3(self):
        assert _cstr(_data(), 0x43C3ACAE) == "CALL CB3"

    def test_nombre_del_modulo(self):
        assert _cstr(_data(), 0x43C3AEF0) == "ClkCtrl"

    DESPACHO = [
        (0x435A0916, 0x4359F174),   # id 0  -> open_clk
        (0x435A0936, 0x4359F12C),   # id 1  -> close_clk
        (0x435A0956, 0x4359F0E4),   # id 2  -> open_dly
        (0x435A0976, 0x4359F09C),   # id 3  -> close_dly
        (0x435A09A0, 0x4359EF88),   # id 4  -> set_sync_signal
        (0x435A09CA, 0x4359EF2C),   # id 5  -> set_sysv_delay
        (0x435A09EE, 0x4359EED0),   # id 6  -> lock_sync_signal
        (0x435A0A0E, 0x4359EE78),   # id 7  -> unlock_sync_signal
        (0x435A0A38, 0x4359F048),   # id 8  -> set_sysv_initial_delay
        (0x435A0A4C, 0x4359F000),   # id 9  -> set_sync_initial_signal
        (0x435A0A5A, 0x43A486B6),   # id 10 -> printf_info
    ]

    @pytest.mark.parametrize("site,target", DESPACHO)
    def test_despachador_llama_a_la_implementacion(self, site, target):
        assert _bl_target(_data(), site) == target

    def test_todas_las_trazas_call_usan_la_misma_convencion(self):
        """Cada envoltorio de la API imprime su traza con r0=0xc0 (id de módulo)."""
        data = _data()
        for site in (0x4359EE48, 0x4359EEA2, 0x4359EEFC, 0x4359EF52, 0x4359EFAE,
                     0x4359F016, 0x4359F068, 0x4359F0B2, 0x4359F0FA, 0x4359F142,
                     0x4359F18A):
            assert _imm_near(data, site, 0, 0xC0, span=14), hex(site)
            assert _imm_near(data, site, 2, 1, span=14), hex(site)


class TestConsumidores:
    """Quién llama a la API y con qué id de subsistema."""

    LLAMADAS = [
        # (sitio de la llamada, destino, id de subsistema en r0)
        (0x4378DFFC, 0x4359F174, 0x03),   # CAMERA_MAIN_SYNC: open_clk(3)
        (0x4378E058, 0x4359F12C, 0x03),   # CAMERA_MAIN_SYNC: close_clk(3)
        (0x4378E012, 0x4359EED0, 0x03),   # CAMERA_MAIN_SYNC: lock_sync_signal(3,0)
        (0x4378E066, 0x4359EE78, 0x03),   # CAMERA_MAIN_SYNC: unlock_sync_signal(3)
        (0x4378E08C, 0x4359EE78, 0x03),   # CAMERA_MAIN_SYNC: unlock_sync_signal(3)
        (0x4378E0C2, 0x4359EF88, 0x03),   # CAMERA_MAIN_SYNC: set_sync_signal(3,clk)
        (0x4368B3F6, 0x4359F174, 0x0A),   # VDF: open_clk(0x0a)
        (0x4368B408, 0x4359EF88, 0x0A),   # VDF: set_sync_signal(0x0a,clk)
        (0x436AFBB2, 0x4359F174, 0x0D),   # VEF: open_clk(0x0d)
        (0x436AFBC4, 0x4359EF88, 0x0D),   # VEF: set_sync_signal(0x0d,clk)
        (0x4366BD5C, 0x4359F174, 0xC2),   # SYSV/TP_R: open_clk(0xc2)
        (0x43628436, 0x4359F174, 0x57),   # MC shell: open_clk(0x57)
        (0x43628E9E, 0x4359F174, 0x57),   # McMsgAvscDec::ClockChange
    ]

    @pytest.mark.parametrize("site,target,subsys", LLAMADAS)
    def test_llamada_con_id_de_subsistema(self, site, target, subsys):
        data = _data()
        assert _bl_target(data, site) == target
        # el id de subsistema se carga antes con "movs r0,#id"
        assert _imm_last_before(data, site, 0) == subsys, hex(site)

    def test_camara_main_inicializa_el_reloj(self):
        data = _data()
        # init_cam_clkctrl -> set_sysv_initial_delay y set_sync_initial_signal
        assert _bl_target(data, 0x43794964) == 0x4359F048
        assert _bl_target(data, 0x43794970) == 0x4359F000
        # CLKTYPE masked con 0x7f
        assert _insn(data, 0x43794924) == ("and", "r4, r3, #0x7f")
        # retardo mínimo 4000 us
        assert _insn(data, 0x437948C8) == ("cmp.w", "r5, #0xfa0")
        assert _insn(data, 0x437948CE) == ("mov.w", "r5, #0xfa0")

    def test_gancho_con_camera_main_sync(self):
        data = _data()
        # "init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus"
        assert _cstr(data, 0x43CA3BE5) == \
            "[CAMERA_MAIN]: init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus"
        # eventos 0x2012..0x2015 emitidos tras abrir/cerrar/bloquear
        assert _insn(data, 0x4378E008) == ("movw", "r1, #0x2012")
        assert _insn(data, 0x4378E05E)[1].endswith("#0x2013")
        assert _insn(data, 0x4378E06C)[1].endswith("#0x2015")
        assert _insn(data, 0x4378E096)[1].endswith("#0x2015")


class TestLineasDeCodigo:
    """Los `L=%d` son números de línea: se comprueba el inmediato en los bytes."""

    LINEAS = [
        (0x4359FA38, 0x10E, "tsk state = STATE_CHANGE_CLK_LOCKING"),   # 270
        (0x4359F9E2, 0x103, "tsk state = STATE_CHANGE_CLK"),            # 259
        (0x435A0FD0, 0x06E, "clk_now=%d, ret=%d, id=0x%x, clk_req=%d"),  # 110
    ]

    @pytest.mark.parametrize("addr,imm,traza", LINEAS)
    def test_inmediato_de_linea(self, addr, imm, traza):
        data = _data()
        mnem, ops = _insn(data, addr)
        assert mnem.startswith("mov")
        assert ops.endswith(f"#0x{imm:x}") or ops.endswith(f"#0x{imm:02x}"), ops
        assert any(traza in t for t in TRAZAS.values())


class TestDiferencial:
    def test_a7s_y_a6300_no_tienen_la_etiqueta(self):
        for path in (A7S_BIN, A6300_BIN):
            ruta = ROOT / path
            if not ruta.exists():
                pytest.skip(f"blob no disponible: {path}")
            blob = ruta.read_bytes()
            assert blob.count(b"[CLK_CTRL]") == 0
            # tampoco ningún núcleo de las 66 trazas
            for text in TRAZAS.values():
                assert text[len("[CLK_CTRL]: "):].encode("latin1") not in blob

    def test_los_tres_firmwares_comparten_la_api_ddl(self):
        for path in (A7S_BIN, A6300_BIN):
            ruta = ROOT / path
            if not ruta.exists():
                pytest.skip(f"blob no disponible: {path}")
            blob = ruta.read_bytes()
            assert blob.count(b"CALL CB3") == 1
            for _v, txt in TestApiDdl.TABLA:
                assert txt.encode("latin1") in blob, txt

    def test_a7s_y_a6300_conservan_la_inicializacion_del_reloj(self):
        for path in (A7S_BIN, A6300_BIN):
            ruta = ROOT / path
            if not ruta.exists():
                pytest.skip(f"blob no disponible: {path}")
            blob = ruta.read_bytes()
            assert b"init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus" in blob
            assert b"[DEBUG] Current clock is 24P." in blob

    def test_a7s_tiene_la_misma_estructura_de_despachador(self):
        """La A7S implementa el mismo despachador DDL, pero sin trazas."""
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        blob = ruta.read_bytes()
        off = blob.find(b"0)ddl_clkctrl_open_clk(id)")
        assert off > 0
        assert blob.count(b"ddl_clkctrl_") == 14          # 11 de la tabla + 2 de error + 1
        assert b"[CLK_CTRL]" not in blob
        assert b"STATE_CHANGE_CLK" not in blob


class TestJson:
    def test_cifras_del_informe(self):
        j = _json()
        assert j["conteo"]["cadenas"] == 66
        assert j["conteo"]["cadenas_referenciadas"] == 62
        assert j["conteo"]["cadenas_sin_referencia"] == 4
        assert j["conteo"]["sitios"] == 85
        assert j["conteo"]["funciones"] == 36
        assert j["diferencial"]["nucleo_en_a7s"] == 0
        assert j["diferencial"]["nucleo_en_a6300"] == 0

    def test_subbloques(self):
        j = _json()
        assert j["conteo_subbloques"] == {
            "CHANGE_CLK": 9, "DDL_CALL": 12, "LOCK": 2, "MSG_MASTER_SLAVE": 6,
            "OSAL_ERR": 10, "OTROS": 3, "SET_DELAY_SYNC": 8, "STATE": 3,
            "SUBSYS_OPEN_CLOSE": 6, "TASK": 2, "VPH_HTP": 5,
        }

    def test_llamadores(self):
        j = _json(JSON_CALLERS)
        assert j["ddl_clkctrl_open_clk"]["n_llamadas"] == 11
        assert j["ddl_clkctrl_set_sync_signal"]["n_llamadas"] == 15
        assert j["ddl_clkctrl_lock_sync_signal"]["n_llamadas"] == 6
        assert j["ddl_clkctrl_get_clk_chg_enable"]["n_llamadas"] == 1
