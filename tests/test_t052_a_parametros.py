"""T052-A — verificación de la cadena de parámetros reales de exposición.

Cubre: identidad del firmware, GOT y objetos, cadena del bloque de 48 B hacia
`record+0xc/+0x1c/+0x20`, compuerta `cap+0x11b0`, predicado de cuadro extra,
escrituras del productor nativo y emulación con VTS 4219/4266.

No toca la cámara. El volcado de RAM real (1 GiB) no se versiona: las pruebas
que lo usan se omiten si no está.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
RAM_OFF = 0x40000000

TV_TO_R5 = 0x4383FA40
GATE_WRITER = 0x437B3B08
PREDICATE = 0x43A12CA8
SETTINGS = 0x43F79F94
IMAGER = 0x43EA976C
GATE_B = 0x43F6E5C2
PRED_OBJ = 0x43DEB360
RECORD_A = 0x43EA5B4C
RECORD_B = 0x43EEE770
GOT = 0x4401EEE4

LINE_Q8 = 3891
VTS_MEASURED = 4219

pytestmark = pytest.mark.skipif(not FW.exists(), reason="firmware A6000 no versionado")


def at(addr: int, n: int) -> bytes:
    with FW.open("rb") as f:
        f.seek(addr - BASE)
        return f.read(n)


def hx(addr: int, n: int) -> str:
    return at(addr, n).hex()


def w16(addr: int) -> int:
    return struct.unpack("<H", at(addr, 2))[0]


def w32(addr: int) -> int:
    return struct.unpack("<I", at(addr, 4))[0]


def sha() -> str:
    h = hashlib.sha256()
    with FW.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_u32(dump: Path, virt: int) -> int:
    phys = virt + RAM_OFF
    with dump.open("rb") as f:
        f.seek(phys - 0x80000000)
        return struct.unpack("<I", f.read(4))[0]


# --- 1. identidad y mapa --------------------------------------------------------

def test_sha_firmware():
    assert sha() == SHA


def test_got_slots_apuntan_a_los_objetos_esperados():
    assert w32(GOT + 0x3764) == RECORD_A
    assert w32(GOT + 0x6F18) == RECORD_B
    assert w32(GOT + 0x1904) == SETTINGS
    assert w32(GOT + 0x2CC4) == IMAGER
    assert w32(GOT + 0x5F74) == GATE_B
    assert w32(GOT + 0x64E8) == PRED_OBJ


def test_mapa_virtual_fisico_por_bytes_de_codigo():
    """Los sitios de T046/T050 están en físico 0x836d6fb6/0x836d7000."""
    # el binario se direcciona en virtual; el volcado real confirma el +0x40000000
    assert hx(0x436D6FB6, 4) == "91f80990"
    assert hx(0x436D7000, 6) == "28125ffa85fe"


# --- 2. Tv: settings+0x162 -> record+0xf6 ---------------------------------------

def test_tv_settings_a_record_f6():
    assert hx(0x437B4662, 4) == "bbf86221"   # ldrh.w r2,[fp,#0x162]
    assert hx(0x437B4670, 4) == "a5f8f620"   # strh.w r2,[r5,#0xf6]


def test_el_segundo_argumento_del_productor_es_el_objeto_imager():
    """0x437b46cc: r1 = r7, no el objeto de ajustes (fp)."""
    assert hx(0x437B46CC, 2) == "3946"       # mov r1,r7
    assert hx(0x437B46CE, 2) == "2846"       # mov r0,r5
    assert hx(0x437B46D0, 4) == "8bf0b6f9"   # bl 0x4383fa40
    # r7 se carga del GOT +0x2cc4 (imager) y fp del GOT +0x1904 (settings)
    assert hx(0x437B4504, 4) == "dff80038"   # ldr.w r3,[pc,#0x800]  -> 0x1904
    assert hx(0x437B450C, 4) == "56f803b0"   # ldr.w fp,[r6,r3]


# --- 3. bloque de 48 B: cap+0x5c8 -> record+8 -----------------------------------

def test_bloque_48b_se_copia_a_record_mas_8():
    assert hx(0x437B4466, 4) == "05f1080c"   # add.w ip,r5,#8
    assert hx(0x437B4478, 4) == "bee80f00"   # ldm.w lr!,{r0-r3}
    assert hx(0x437B447C, 4) == "ace80f00"   # stm.w ip!,{r0-r3}
    # descriptor: [r8] y [r8+2] a record+0/+2; [r8+4] es el puntero al bloque
    assert hx(0x437B4462, 4) == "b8f80230"   # ldrh.w r3,[r8,#2]
    assert hx(0x437B4470, 4) == "d8f80430"   # ldr.w r3,[r8,#4]


def test_bloque_apunta_a_cap_mas_0x5c8_en_los_dos_constructores():
    assert hx(0x437F892C, 4) == "00f5b962"   # add.w r2,r0,#0x5c8
    assert hx(0x437F8930, 2) == "0492"       # str r2,[sp,#0x10]
    assert hx(0x437F89BC, 4) == "04f5b963"   # add.w r3,r4,#0x5c8
    assert hx(0x437F89C0, 2) == "0393"       # str r3,[sp,#0xc]


def test_offsets_del_bloque_a_record():
    """record+0xc = bloque+4; +0x1c = bloque+0x14; +0x20 = bloque+0x18."""
    # el constructor lee +0xc como u32 y +0x1c/+0x20 como u16
    assert hx(0x4383FA46, 2) == "c768"       # ldr r7,[r0,#0xc]
    assert hx(0x4383FA66, 2) == "268c"       # ldrh r6,[r4,#0x20]
    assert hx(0x4383FA8C, 4) == "b4f81c80"   # ldrh.w r8,[r4,#0x1c]


def test_escritor_del_bloque_usa_el_descriptor_de_modo():
    """0x43846e00..12: [src+8]->0x5da, [src+0xa]->0x5dc, [src+4]->0x5de,
    [src+6]->0x5e0. El descriptor es [r5+0x3c]."""
    assert hx(0x43846DD4, 2) == "eb6b"       # ldr r3,[r5,#0x3c]
    assert hx(0x43846E00, 4) == "b3f808e0"   # ldrh.w lr,[r3,#8]
    assert hx(0x43846E04, 2) == "5889"       # ldrh r0,[r3,#0xa]
    assert hx(0x43846E06, 2) == "9988"       # ldrh r1,[r3,#4]
    assert hx(0x43846E08, 2) == "db88"       # ldrh r3,[r3,#6]
    assert hx(0x43846E0A, 4) == "a4f8dae5"   # strh.w lr,[r4,#0x5da]
    assert hx(0x43846E0E, 4) == "a4f8dc05"   # strh.w r0,[r4,#0x5dc]
    assert hx(0x43846E12, 4) == "a4f8e035"   # strh.w r3,[r4,#0x5e0]


# --- 4. compuerta cap+0x11b0 ----------------------------------------------------

def test_compuerta_se_deriva_de_dos_modos():
    """0x437b3b08: gate = ([imager+0x504]==3); luego [gate_b+0x8c] 1/2."""
    assert hx(0x437B3B54, 4) == "d3f80425"   # ldr.w r2,[r3,#0x504]
    assert hx(0x437B3B58, 2) == "032a"       # cmp r2,#3
    assert hx(0x437B3B62, 2) == "2376"       # strb r3,[r4,#0x18]
    assert hx(0x437B3B6A, 4) == "93f88c30"   # ldrb.w r3,[r3,#0x8c]
    assert hx(0x437B3B78, 2) == "2376"       # strb r3,[r4,#0x18]
    # el lector de la compuerta en el constructor normal
    assert hx(0x437B46C6, 4) == "9af81830"   # ldrb.w r3,[sl,#0x18]


def test_compuerta_no_es_un_flag_de_usuario_conocido():
    """El escritor usa [imager+0x504], propiedad LIRO, no un flag Silent."""
    # setter de la propiedad: 0x43802950 escribe [global+0x504] desde [r0+8]
    assert hx(0x4380294A, 2) == "027a"       # ldrb r2,[r0,#8]
    assert hx(0x4380294E, 2) == "7b44"       # add r3,pc
    assert hx(0x43802950, 4) == "c3f80425"   # str.w r2,[r3,#0x504]


# --- 5. productor nativo: escrituras y predicado -------------------------------

def test_productor_escribe_d8_da_dc_ademas_de_r5_y_shutmode():
    assert hx(0x4383FAE8, 4) == "a4f8d810"   # strh.w r1,[r4,#0xd8]
    assert hx(0x4383FAEE, 4) == "a4f8da50"   # strh.w r5,[r4,#0xda]
    assert hx(0x4383FAF2, 4) == "a4f8dc50"   # strh.w r5,[r4,#0xdc]
    assert hx(0x4383FACC, 4) == "c4f864a0"   # str.w sl,[r4,#0x64]
    assert hx(0x4383FAD4, 4) == "84f86d30"   # strb.w r3,[r4,#0x6d]


def test_predicado_de_cuadro_extra_lee_un_byte_global():
    # ldr r3,[pc,#0x14]; ldr r2,[pc,#0x18]; add r3,pc; ldrb r0,[r3,#0x10]
    assert hx(0x43A12CA8, 2) == "054b"
    assert hx(0x43A12CAA, 2) == "064a"
    assert hx(0x43A12CB0, 2) == "187c"       # ldrb r0,[r3,#0x10]
    # 0/1 -> 1 (cuadro extra); >=2 -> 0
    assert hx(0x43A12CB2, 4) == "a0f10101"   # sub.w r1,r0,#1
    assert hx(0x43A12CB6, 2) == "4842"       # rsbs r0,r1,#0
    assert hx(0x43A12CB8, 4) == "40eb0100"   # adc.w r0,r0,r1


# --- 6. emulación ---------------------------------------------------------------

@pytest.fixture(scope="module")
def emu():
    spec = importlib.util.spec_from_file_location("t052_emu", ROOT / "scripts/t052_a_readonly.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_emulacion_4219_reproduce_t047(emu):
    d = emu.emulation()["velocidades"]
    assert d["1/4000"]["vts4219_extra0"]["r5"] == 4203
    assert d["1/250"]["vts4219_extra0"]["r5"] == 3956
    assert d["1/60"]["vts4219_extra0"]["r5"] == 3122
    assert abs(d["1/250"]["vts4219_extra0"]["error_pct_vs_nominal"]) < 1


def test_emulacion_4266_desvia_47_lineas(emu):
    d = emu.emulation()["velocidades"]
    for name in ("1/4000", "1/250", "1/60"):
        assert d[name]["vts4266_extra0"]["r5"] - d[name]["vts4219_extra0"]["r5"] == 47


def test_emulacion_4266_no_es_representable_a_1_4000(emu):
    d = emu.emulation()["velocidades"]["1/4000"]["vts4266_extra0"]
    assert d["representable"] == 0
    assert d["tiempo_ley_4219_ms"] < 0


def test_cuadro_extra_invalida_r5(emu):
    d = emu.emulation()["velocidades"]
    for name in ("1/4000", "1/250", "1/60"):
        for vts in (4219, 4266):
            x = d[name][f"vts{vts}_extra1"]
            assert x["r5"] > vts
            assert x["representable"] == 0


# --- 7. lecturas reales (solo si el volcado existe) -----------------------------

dump_ok = pytest.mark.skipif(not DUMP.exists(), reason="volcado de RAM no disponible")


@dump_ok
def test_volcado_confirma_got_y_objetos():
    assert dump_u32(DUMP, GOT + 0x3764) == RECORD_A
    assert dump_u32(DUMP, GOT + 0x6F18) == RECORD_B
    assert dump_u32(DUMP, GOT + 0x1904) == SETTINGS
    assert dump_u32(DUMP, GOT + 0x2CC4) == IMAGER
    assert dump_u32(DUMP, GOT + 0x5F74) == GATE_B
    assert dump_u32(DUMP, GOT + 0x64E8) == PRED_OBJ


@dump_ok
def test_volcado_valores_de_reposo():
    # Tv 1/60 en el objeto de ajustes; factor 1; modo 2; gate 0; predicado 0
    assert dump_u32(DUMP, SETTINGS + 0x160) & 0xFFFF == 0x1000
    assert (dump_u32(DUMP, SETTINGS + 0x160) >> 16) == 0x15E8
    assert dump_u32(DUMP, IMAGER + 0x4B8) & 0xFF == 1
    assert dump_u32(DUMP, IMAGER + 0x504) & 0xFF == 2
    assert dump_u32(DUMP, GATE_B + 0x8C) & 0xFF == 0
    assert dump_u32(DUMP, PRED_OBJ + 0x10) & 0xFF == 0
    # los dos registros están a cero: no hubo foto desde el arranque
    assert dump_u32(DUMP, RECORD_A + 0x20) & 0xFFFF == 0
    assert dump_u32(DUMP, RECORD_B + 0x20) & 0xFFFF == 0


@dump_ok
def test_compuerta_observada_es_cero():
    b = dump_u32(DUMP, GATE_B + 0x8C) & 0xFF
    a = dump_u32(DUMP, IMAGER + 0x504) & 0xFF
    gate = 1 if b == 1 else 0 if b == 2 else int(a == 3)
    assert gate == 0


# --- 8. el lector no escribe ----------------------------------------------------

def test_lector_no_tiene_escrituras_ni_red():
    src = (ROOT / "scripts/t052_a_readonly.py").read_text()
    for forbidden in ("camera_telnet", "import socket", "subprocess", "os.system", "wr_cmd", "Runtime.exec"):
        assert forbidden not in src
    # no hay ningún dd de escritura en el código (sí la advertencia del protocolo)
    assert "of=/dev/mem" not in src.replace("nunca of=/dev/mem", "")


def test_json_tiene_las_claves_obligatorias():
    p = ROOT / "analysis/t052-a/lecturas.json"
    if not p.exists():
        pytest.skip("lecturas.json no generado")
    d = json.loads(p.read_text())
    assert d["sha256"] == SHA
    assert "emulacion" in d
    assert set(d["emulacion"]["velocidades"]) == {"1/4000", "1/250", "1/60"}
