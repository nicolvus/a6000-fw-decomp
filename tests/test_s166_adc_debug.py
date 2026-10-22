"""Tests for S166 — el módulo `[ADC_DEBUG]` (14 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: cada comprobación lee el binario en la dirección exacta y
comprueba el contenido (texto, semiword Thumb, palabra del pool de literales o destino
de un `bl`), de modo que si cambia una dirección, una cadena o una instrucción, el test
falla.  Nada de comparaciones tautológicas contra el propio JSON del hito.

Referencia canónica: analysis/s166_adc_debug/adc_debug.md y adc_debug.json.
"""

import pathlib
import re
import struct

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)

U16S = struct.Struct("<H")
U32S = struct.Struct("<I")

DATA = (ROOT / BIN).read_bytes()
DATA_A7S = (ROOT / A7S).read_bytes()
DATA_A6300 = (ROOT / A6300).read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False

# Las 14 cadenas del modulo: (vaddr, texto exacto tal y como esta en el binario)
STRINGS = [
    (0x43CE50DD, "[ADC_DEBUG]: few arg\n"),
    (0x43CE50F3, "[ADC_DEBUG]: ADC DATA0  = %04x\n"),
    (0x43CE5113, "[ADC_DEBUG]: ADC DATA1  = %04x\n"),
    (0x43CE5133, "[ADC_DEBUG]: ADC DATA2  = %04x\n"),
    (0x43CE5153, "[ADC_DEBUG]: ADC DATA3  = %04x\n"),
    (0x43CE5173, "[ADC_DEBUG]: ADC DATA4  = %04x\n"),
    (0x43CE5193, "[ADC_DEBUG]: ADC DATA5  = %04x\n"),
    (0x43CE51B3, "[ADC_DEBUG]: ADC DATA6  = %04x\n"),
    (0x43CE51D3, "[ADC_DEBUG]: ADC DATA7  = %04x\n"),
    (0x43CE51F3, "[ADC_DEBUG]: ADC DATA8  = %04x\n"),
    (0x43CE5213, "[ADC_DEBUG]: ADC DATA9  = %04x\n"),
    (0x43CE5233, "[ADC_DEBUG]: ADC DATA10 = %04x\n"),
    (0x43CE5253, "[ADC_DEBUG]: ADC DATA11 = %04x\n"),
    (0x43CE5273, "[ADC_DEBUG]: ADC DATA = %04x\n"),
]

# Los 15 pares PIC: (sitio del `add rX,pc`, cadena destino)
PIC_PAIRS = [
    (0x4398EB32, 0x43CE50DD),
    (0x4398EB6A, 0x43CE50F3),
    (0x4398EB7C, 0x43CE5113),
    (0x4398EB8E, 0x43CE5133),
    (0x4398EBA0, 0x43CE5153),
    (0x4398EBB2, 0x43CE5173),
    (0x4398EBC4, 0x43CE5193),
    (0x4398EBD6, 0x43CE51B3),
    (0x4398EBE8, 0x43CE51D3),
    (0x4398EBFA, 0x43CE51F3),
    (0x4398EC0C, 0x43CE5213),
    (0x4398EC1E, 0x43CE5233),
    (0x4398EC30, 0x43CE5253),
    (0x4398EC8E, 0x43CE50DD),
    (0x4398ECCE, 0x43CE5273),
]

# Registro ADJ del driver LIRO ADC: (offset de la entrada, nombre, handler)
ADJ_TABLE = 0x440189BC
ADJ_ENTRIES = [
    (0x10, "get_d", 0x43CE5299, 0x43CE529F, 0x4398EC7C),
    (0x1C, "get_da", 0x43CE52BE, 0x43CE52C5, 0x4398EB20),
    (0x28, "set_da", 0x43CE52DE, 0x43CE52E5, 0x4398E9DC),
    (0x34, "exit", 0x43C39847, 0x43CE5315, 0x43B5E0B0),
]

# Los 11 puntos de llamada al servicio LIRO_ADC (handle 0x720018)
LIRO_ADC_CLIENTS = [
    0x43562A44, 0x435AD4A6, 0x43636CC0, 0x436F9F6E, 0x4385EB80,
    0x438D14E8, 0x438D1514, 0x438D2204, 0x4398EA60, 0x4398EB5A, 0x4398ECBE,
]

# Regiones de codigo del subsistema IS (modulo [CAMERA_IS], S164)
IS_REGIONS = ((0x436E8000, 0x43708000), (0x4371D000, 0x43721000))


def off(addr):
    return addr - BASE


def u16(data, addr):
    return U16S.unpack_from(data, off(addr))[0]


def u32(data, addr):
    return U32S.unpack_from(data, off(addr))[0]


def cstr(data, addr):
    o = off(addr)
    e = o
    while e < len(data) and data[e] != 0:
        e += 1
    return data[o:e].decode("latin1")


def bl_target(data, addr):
    """Decodifica un BL Thumb-2 de 32 bits y devuelve su destino."""
    hw1, hw2 = struct.unpack_from("<HH", data, off(addr))
    assert (hw1 & 0xF800) == 0xF000 and (hw2 & 0xD000) == 0xD000, hex(addr)
    s = (hw1 >> 10) & 1
    imm10 = hw1 & 0x3FF
    j1 = (hw2 >> 13) & 1
    j2 = (hw2 >> 11) & 1
    imm11 = hw2 & 0x7FF
    i1 = 1 - (j1 ^ s)
    i2 = 1 - (j2 ^ s)
    val = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        val -= 1 << 25
    return addr + 4 + val


def pic_dest(data, site):
    """Recodifica el par (ldr rX,[pc,#imm] + add rX,pc) del sitio `site`.

    Devuelve (destino, dir_del_ldr, dir_del_pool, registro_del_ldr)."""
    for back in range(0, 40, 2):
        a = site - back
        h = u16(data, a)
        if (h >> 11) == 0b01001 and ((h >> 8) & 7) != 0:
            reg = (h >> 8) & 7
            imm = (h & 0xFF) * 4
            pool = ((a + 4) & ~3) + imm
            return site + 4 + u32(data, pool), a, pool, reg
    raise AssertionError("sin ldr literal antes de %08x" % site)


def service_calls(data, lo, hi, target):
    """Llamadas `bl <target>` en [lo,hi) con el handle que carga r0."""
    insns = list(MD.disasm(data[off(lo):off(hi)], lo))
    out = []
    for i, ins in enumerate(insns):
        if ins.mnemonic == "bl" and ins.op_str.startswith("#0x"):
            if int(ins.op_str[1:], 16) != target:
                continue
            handle = None
            for j in range(i - 1, max(i - 25, 0), -1):
                m = re.match(r"^r0, \[pc, #(0x[0-9a-f]+)\]$", insns[j].op_str)
                if m:
                    imm = int(m.group(1), 16)
                    lit = ((insns[j].address + 4) & ~3) + imm
                    handle = u32(data, lit)
                    break
            out.append((ins.address, handle))
    return out


# --------------------------------------------------------------------------
# 1. Las 14 cadenas, en su direccion exacta, con su texto exacto
# --------------------------------------------------------------------------
def test_las_14_cadenas_estan_en_su_direccion():
    for addr, text in STRINGS:
        assert cstr(DATA, addr) == text, hex(addr)


def test_el_token_apararece_14_veces_y_solo_14():
    assert DATA.count(b"[ADC_DEBUG]") == 14


def test_las_cadenas_son_un_bloque_contiguo():
    for i in range(len(STRINGS) - 1):
        gap = STRINGS[i + 1][0] - STRINGS[i][0]
        # 0x20 bytes entre cadenas, salvo la primera (0x16) por el final de 'few arg\n'
        assert gap in (0x16, 0x20), hex(STRINGS[i][0])


# --------------------------------------------------------------------------
# 2. Los 15 pares PIC, recodificados desde los bytes
# --------------------------------------------------------------------------
def test_los_15_pares_pic_resuelven_a_su_cadena():
    for site, dest in PIC_PAIRS:
        got, ldr, pool, reg = pic_dest(DATA, site)
        assert got == dest, "%08x -> %08x (esperado %08x)" % (site, got, dest)
        # el `add` debe usar el registro que cargo el `ldr`
        insn = next(MD.disasm(DATA[off(site):off(site) + 4], site))
        assert insn.mnemonic == "add", hex(site)
        assert insn.op_str == "r%d, pc" % reg, "%08x: %s" % (site, insn.op_str)
        assert 0 < site - ldr <= 8, hex(site)


def test_los_sitios_pic_estan_dentro_de_las_dos_funciones_emisoras():
    # get_da: 0x4398eb20 (prologo 0x4398eb22) -> 13 sitios
    get_da = [s for s, _ in PIC_PAIRS if 0x4398EB22 <= s < 0x4398EC44]
    assert len(get_da) == 13, get_da
    # get_d: 0x4398ec7c (prologo 0x4398ec7e) -> 2 sitios
    get_d = [s for s, _ in PIC_PAIRS if 0x4398EC7E <= s < 0x4398ED00]
    assert len(get_d) == 2, get_d


# --------------------------------------------------------------------------
# 3. Los handlers: bytes de entrada, id de mensaje y llamada al servicio
# --------------------------------------------------------------------------
def test_handlers_get_da_y_get_d():
    # 0x4398eb20: cmp r0,#1 ; push {r4,r5,lr}
    assert u16(DATA, 0x4398EB20) == 0x2801
    assert u16(DATA, 0x4398EB22) == 0xB530
    # 0x4398ec7c: cmp r0,#2 ; push {r4,r5,lr}
    assert u16(DATA, 0x4398EC7C) == 0x2802
    assert u16(DATA, 0x4398EC7E) == 0xB530
    # 0x4398e9dc (set_da): push {r0,r1,r2,r4,r5,lr}
    assert u16(DATA, 0x4398E9DC) == 0xB537


def test_ids_de_mensaje_de_la_servicio_adc():
    # get_da -> 0xfff1 ; get_d -> 0xfff0 ; set_da -> 0xfff2  (MOVW Rd,#imm16)
    assert DATA[off(0x4398EB48):off(0x4398EB4C)] == bytes.fromhex("4f f6 f1 73")
    assert DATA[off(0x4398ECA4):off(0x4398ECA8)] == bytes.fromhex("4f f6 f0 73")
    assert DATA[off(0x4398E9EE):off(0x4398E9F2)] == bytes.fromhex("4f f6 f2 73")


def test_los_handlers_llaman_al_servio_con_el_handle_liro_adc():
    for site in (0x4398EB5A, 0x4398ECBE, 0x4398EA60):
        assert bl_target(DATA, site) == 0x43561228, hex(site)
    # pool con el handle 0x720018 (LIRO_ADC)
    assert u32(DATA, 0x4398EC44) == 0x720018
    assert u32(DATA, 0x4398ECE4) == 0x720018


# --------------------------------------------------------------------------
# 4. El registro ADJ: los handlers son los de get_d / get_da / set_da
# --------------------------------------------------------------------------
def test_registro_adj_del_driver_adc():
    assert u32(DATA, ADJ_TABLE + 0x08) == 3          # nº de comandos
    assert u32(DATA, ADJ_TABLE + 0x0C) == 0xFF       # mascara
    for ent_off, name, name_addr, help_addr, handler in ADJ_ENTRIES:
        assert u32(DATA, ADJ_TABLE + ent_off) == name_addr, name
        assert cstr(DATA, name_addr) == name
        assert u32(DATA, ADJ_TABLE + ent_off + 4) == help_addr, name
        assert u32(DATA, ADJ_TABLE + ent_off + 8) == handler | 1, name


def test_ayuda_de_los_comandos_adj():
    assert cstr(DATA, 0x43CE529F) == "ADC_GET_DATA     unit_no ch_no"
    assert cstr(DATA, 0x43CE52C5) == "ADC_GET_DATA_ALL unit_no"
    assert cstr(DATA, 0x43CE52E5) == "ADC_SET_DATA_ALL unit_no data0 data1 ... data11"
    assert cstr(DATA, 0x43CE5291) == "TSK_ADC"
    assert cstr(DATA, 0x43CE5315) == "boot_exit_adcliro"


# --------------------------------------------------------------------------
# 5. Geometria del ADC: 2 unidades x 12 canales, array y registros de HW
# --------------------------------------------------------------------------
def test_array_de_valores_adc_y_limites_de_canal_y_unidad():
    # pool -> base del array de valores (2 unidades x 12 canales, u16)
    assert u32(DATA, 0x4398E6F4) == 0x005F64B8
    assert 0x4398E6C4 + 4 + 0x005F64B8 == 0x43F84B80
    # limites: unidad <= 1, canal <= 0xb
    assert u16(DATA, 0x4398E6B2) == 0x2901     # cmp r1,#1
    assert u16(DATA, 0x4398E6B8) == 0x2A0B     # cmp r2,#0xb
    assert u16(DATA, 0x4398E6BC) == 0x250C     # movs r5,#0xc  (12 canales)


def test_bloque_de_hardware_del_adc():
    assert u32(DATA, 0x4398ED24) == 0xF2406000   # base unidad 0
    assert u32(DATA, 0x4398EE24) == 0xF2406010   # base registro por canal (unidad 0)
    # la unidad 1 esta 0x1000 mas lejos: el calculo es (unidad<<12)
    assert 0xF2406010 + 0x1000 == 0xF2407010


def test_las_trazas_del_driver_usan_el_modulo_0xadc():
    # movw r1,#0xadc  -> identificador de modulo del propio driver
    assert DATA[off(0x4398E5A8):off(0x4398E5AC)] == bytes.fromhex("40 f6 dc 21")


# --------------------------------------------------------------------------
# 6. Clientes del servicio LIRO_ADC
# --------------------------------------------------------------------------
def test_los_clientes_del_servicio_liro_adc():
    for s in LIRO_ADC_CLIENTS:
        assert bl_target(DATA, s) == 0x43561228, hex(s)
        insn = next(MD.disasm(DATA[off(s):off(s) + 4], s))
        assert insn.mnemonic == "bl" and insn.op_str == "#0x43561228", hex(s)


def test_trazas_de_los_clientes_representativos():
    assert cstr(DATA, 0x43C24CAC) == "[ACCY][INFO][HW]:AD=%d, ID=%d"
    assert cstr(DATA, 0x43C40945) == "[ILLUMI]AD MAXOVER. ADwork=0x%x, line=%d"
    assert cstr(DATA, 0x43C7751A) == "Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)\n"
    assert cstr(DATA, 0x43CCABD8) == "[CAMERA_MAIN]: osal_alloc_msg(liro_adc) error:%d\n"


# --------------------------------------------------------------------------
# 7. Relacion con [CAMERA_IS] (S164): el giroscopio NO usa el ADC LIRO
# --------------------------------------------------------------------------
def test_el_giroscopio_del_is_no_usa_el_servicio_liro_adc():
    # 0x436eace0 lee una tabla de constantes en .rodata (0x43bdc0a6)
    assert u32(DATA, 0x436EAD00) == 0x004F13B4
    assert 0x436EACEE + 4 + 0x004F13B4 == 0x43BDC0A6
    assert u16(DATA, 0x43BDC0A6) == 0x0032
    assert u16(DATA, 0x43BDC0A8) == 0x0030
    # y la region IS no tiene ninguna llamada al servicio con handle 0x720018
    for lo, hi in IS_REGIONS:
        for site, handle in service_calls(DATA, lo, hi, 0x43561228):
            assert handle != 0x720018, "%08x usa el handle 0x720018" % site


# --------------------------------------------------------------------------
# 8. Diferencial A6000 / A7S / A6300
# --------------------------------------------------------------------------
def test_el_token_adc_debug_es_exclusivo_de_la_a6000():
    assert DATA.count(b"[ADC_DEBUG]") == 14
    assert DATA_A7S.count(b"[ADC_DEBUG]") == 0
    assert DATA_A6300.count(b"[ADC_DEBUG]") == 0


def test_los_textos_de_adc_debug_no_existen_en_los_otros_firmwares():
    for addr, text in STRINGS:
        tb = text.encode("latin1")
        assert tb not in DATA_A7S, text
        assert tb not in DATA_A6300, text


def test_las_etiquetas_adj_del_driver_adc_son_nuevas():
    assert DATA.count(b"ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA") == 2
    assert DATA_A7S.count(b"ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA") == 0
    assert DATA_A6300.count(b"ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA") == 0


def test_los_comandos_adj_existen_en_los_tres_firmwares():
    for t in (b"get_d", b"get_da", b"set_da", b"TSK_ADC", b"boot_exit_adcliro",
              b"ADC_GET_DATA     unit_no ch_no", b"ADC_GET_DATA_ALL unit_no",
              b"ADC_SET_DATA_ALL unit_no data0 data1 ... data11"):
        assert t in DATA, t
        assert t in DATA_A7S, t
        assert t in DATA_A6300, t


def test_los_handlers_de_los_otros_firmwares_no_imprimen():
    # A7S fw3.20: get_da 0x4397c860, get_d 0x4397c89c
    for entry in (0x4397C860, 0x4397C89C):
        assert u16(DATA_A7S, entry) in (0x2801, 0x2802), hex(entry)
    assert b"[ADC_DEBUG]" not in DATA_A7S
    # A6300 fw2.01: get_da 0x43a23480, get_d 0x43a234bc
    for entry in (0x43A23480, 0x43A234BC):
        assert u16(DATA_A6300, entry) in (0x2801, 0x2802), hex(entry)
    assert b"[ADC_DEBUG]" not in DATA_A6300
    # el resto del ecosistema ADC es igual en los tres
    for t in (b"liro_adc", b"CNF_ADC_CH_EVF_TEMP", b"int_ADC_Handler",
              b"ADC::Initialize", b"SendToADCTask", b"jitter NG"):
        assert (t in DATA) == (t in DATA_A7S) == (t in DATA_A6300), t


def test_el_registro_adj_existe_en_los_tres_firmwares():
    # A7S: descriptor en 0x4401e1bc, entradas a partir de 0x4401e1cc
    assert u32(DATA_A7S, 0x4401E1C4) == 3
    assert u32(DATA_A7S, 0x4401E1C8) == 0xFF
    assert u32(DATA_A7S, 0x4401E1CC) == 0x43CDA594      # 'get_d'
    assert u32(DATA_A7S, 0x4401E1D4) == 0x4397C89D      # handler get_d
    assert u32(DATA_A7S, 0x4401E1E0) == 0x4397C861      # handler get_da
    # A6300: descriptor en 0x441e9754, entradas a partir de 0x441e9764
    assert u32(DATA_A6300, 0x441E975C) == 3
    assert u32(DATA_A6300, 0x441E9760) == 0xFF
    assert u32(DATA_A6300, 0x441E9764) == 0x43DF875D     # 'get_d'
    assert u32(DATA_A6300, 0x441E976C) == 0x43A234BD     # handler get_d
    assert u32(DATA_A6300, 0x441E9778) == 0x43A23481     # handler get_da


# --------------------------------------------------------------------------
# 9. Interes para la linea del obturador
# --------------------------------------------------------------------------
def test_las_trazas_de_adc_debug_no_hablan_de_obturador():
    joined = " ".join(t for _, t in STRINGS).lower()
    for w in ("shut", "silent", "electro", "mech", "rolling", "readout",
              "exposure", "sensor", "gyro", "jitter"):
        assert w not in joined, w


def test_secuencia_hs_y_medida_de_jitter_usan_el_adc():
    # HS_Main llama a SendToADCTask (0x4378d3b4)
    assert bl_target(DATA, 0x43790866) == 0x4378D3B4
    # int_ADC_Handler: umbral de jitter cmp.w r8,#0x320
    assert DATA[off(0x4378D4B4):off(0x4378D4B8)] == bytes.fromhex("b8 f5 48 7f")
    # lectura del reloj de ticks
    assert bl_target(DATA, 0x4378D4A4) == 0x43AD5FBA
    assert cstr(DATA, 0x43CA241E) == \
        "[CAMERA_MAIN_SYNC]: int_ADC_Handler #%d jitter NG %d->%d, jitter:%dusec"
    assert cstr(DATA, 0x43CA30FD) == \
        "[CAMERA_MAIN_SYNC]: HS_Main:(TC::Last1st) ADC flg timeout %dV #%d, %04x"


def test_no_hay_canal_de_adc_nombrado_para_obturador():
    # el unico nombre de canal de ADC del firmware es el del EVF
    assert DATA.count(b"CNF_ADC_CH_EVF_TEMP") == 1
    assert DATA.count(b"CNF_ADC_CH_SHUT") == 0
    assert DATA.count(b"CNF_ADC_CH_ELECTRO") == 0
