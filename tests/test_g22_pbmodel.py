"""G22-PBMODEL — qué es `@M010` y quién debería llenarlo, leído de los ELF 3.21, sin QEMU.

Fija lo que el informe `docs/gui/g22-pbmodel-modelobrowser.md` da por VERIFICADO:

1. **`@Mxxx` no es un nombre, es el id**: `IdGenerator::Get` (libObj+0x12d670) compara 5 B contra el literal
   `@MFFE` (libObj+0xbcf1e1, el marcador de «sin id») y, si no coincide, toma `name[2]`, `name[3]`, `name[4]` como
   tres dígitos hex (`cmp r,#0x40` · `subs r,#0x37` para letras · `subs r,#0x30` para dígitos) y los compone
   `((d2<<8) | (d3<<4)) + d4`. Por eso `@M010` vale 0x10 y `@M00A` vale 0x0A: el nombre **es** el número.
2. **La tabla id → clase está en `libObj`**, en una única función Thumb que arranca en `libObj+0x401f78` y va
   llamando `IdGenerator::Get("@Mxxx")` (PLT `0xdffb8`) + `IdSoTable::add(id, "<clase>.so", "<Clase>ToInstance")`
   (PLT `0xdf58c`). La entrada de `@M010` está en `libObj+0x40210c..0x402126` y resuelve
   `@M010` → `modelBrowser.so` → `ModelBrowserToInstance`.
3. **`@M010` es la clase `ModelBrowser`**, que vive en `libObj.so` (RTTI `12ModelBrowser` en `0xcdf62c`, cola de
   log `[M_Browser] %s() ModelBrowser Info` en `0xcdf695`), no en un `modelBrowser.so` aparte — el nombre del
   módulo de la tabla es el de antes de la fusión de modelos, igual que pasa con las vistas
   ([`g22-pbvista-carga-bajo-demanda`](../docs/gui/g22-pbvista-carga-bajo-demanda.md) §3).
4. **La fábrica**: `ModelBrowserToInstance` exportada en `libObj+0x47fa79` (bit Thumb), `new(0x134)` +
   constructor `libObj+0x47fa48`; el objeto mide **0x134 B**.

Los binarios viven en `analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados): si falta `libObj.so`, el
módulo se salta entero. No arranca ninguna VM; lo medido en el invitado está en el informe y en
`reports/evidence/g22-pbmodel-20261128/`.
"""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

import capstone  # dependencia del proyecto (la usan tests/test_g104_iso_ui.py y otros)

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"

if not (LIB / "libObj.so").exists():
    pytest.skip("falta libObj.so del arnés (analysis/gui/g22/harness/stage): test estático", allow_module_level=True)

# ---------------------------------------------------------------- direcciones (VA del ELF 3.21; 1.er PT_LOAD VA == desplazamiento)
POOL_M010 = 0x00CBCA32      # .rodata: «@M010\0modelBrowser.so\0ModelBrowserToInstance\0»
POOL_MFFE = 0x00BCF1E1      # .rodata: «@MFFE» (marcador de «sin id» que compara IdGenerator::Get)
TABLA_FN = 0x00401F78       # entrada de la función de registro de modelos de libObj
ENTRADA_M010 = 0x0040210C   # ldr r0,[pc] de la entrada @M010 de esa tabla
GET_ID = 0x0012D670         # IdGenerator::Get(const char*)
FABRICA_MB = 0x0047FA78     # ModelBrowserToInstance (Thumb)
CTOR_MB = 0x0047FA48        # constructor de ModelBrowser
RTTI_MB = 0x00CDF62C        # «12ModelBrowser»
LOG_MB = 0x00CDF695         # «[M_Browser] %s() ModelBrowser Info»
PLT_IDGET = 0x000DFFB8      # stub de IdGenerator::Get dentro de libObj
PLT_IDSADD = 0x000DF58C     # stub de IdSoTable::add dentro de libObj


def _d() -> bytes:
    return (LIB / "libObj.so").read_bytes()


def _cstr(d: bytes, va: int, maxlen: int = 120) -> str | None:
    if not 0 < va < len(d):
        return None
    fin = d.find(b"\0", va)
    if fin < 0 or fin - va > maxlen:
        return None
    b = d[va:fin]
    if not b or not all(32 <= c < 127 for c in b):
        return None
    return b.decode("ascii")


def _pool_target(d: bytes, ldr_addr: int, add_addr: int) -> int:
    """Idioma PIC de estos binarios: `ldr rX,[pc,#imm]` + `add rX, pc` (PC = dirección + 4, sin alinear)."""
    hw1, hw2 = struct.unpack_from("<HH", d, ldr_addr)
    if hw1 == 0xF8DF:
        slot = ((ldr_addr + 4) & ~3) + (hw2 & 0xFFF)
    elif (hw1 & 0xF800) == 0x4800:
        slot = ((ldr_addr + 4) & ~3) + (hw1 & 0xFF) * 4
    else:
        raise AssertionError(f"{ldr_addr:#x} no es un ldr [pc,#imm]")
    return (struct.unpack_from("<I", d, slot)[0] + add_addr + 4) & 0xFFFFFFFF


def _stub_got(d: bytes, va: int) -> int:
    """Stub ARM de la PLT (`add ip,pc` / `add ip,ip` / `ldr pc,[ip,#imm]`) → dirección del slot GOT."""
    w0, w1, w2 = struct.unpack_from("<III", d, va)

    def imm32(w: int) -> int:
        rot = ((w >> 8) & 0xF) * 2
        v = w & 0xFF
        return ((v >> rot) | (v << (32 - rot))) & 0xFFFFFFFF if rot else v

    if (w0 & 0xFFFFF000) != 0xE28FC000 or (w1 & 0xFFFFF000) != 0xE28CC000 or (w2 & 0xFFFFF000) != 0xE5BCF000:
        raise AssertionError(f"{va:#x} no es un stub de la PLT")
    ip = (va + 8 + imm32(w0)) & 0xFFFFFFFF
    ip = (ip + imm32(w1)) & 0xFFFFFFFF
    return (ip + (w2 & 0xFFF)) & 0xFFFFFFFF


def _simbolo_de_stub(d: bytes, va: int) -> str | None:
    """Nombre del símbolo importado al que salta un stub, leyendo .rel.plt del propio fichero."""
    from elftools.elf.elffile import ELFFile  # noqa: PLC0415  (solo en este test)

    e = ELFFile(open(LIB / "libObj.so", "rb"))
    got = _stub_got(d, va)
    dyn = e.get_section_by_name(".dynsym")
    for r in e.get_section_by_name(".rel.plt").iter_relocations():
        if r["r_offset"] == got:
            return dyn.get_symbol(r["r_info_sym"]).name
    return None


def _id_de_estrella(nombre: str) -> int:
    """Réplica del parser medido en `IdGenerator::Get`: `@M` + 3 dígitos hex → id (0xFFE = «sin id» = -1)."""
    if len(nombre) != 5 or nombre[0] != "@" or nombre[1] != "M" or nombre == "@MFFE":
        return -1
    v = 0
    for c in nombre[2:5]:
        if "0" <= c <= "9":
            v = (v << 4) | (ord(c) - 0x30)
        elif "A" <= c <= "F":
            v = (v << 4) | (ord(c) - 0x37)
        else:
            return -1
    return v


# ---------------------------------------------------------------- 1. el nombre es el id
def test_get_de_idgenerator_saca_el_id_de_los_tres_digitos_del_nombre() -> None:
    """`IdGenerator::Get` (+0x12d670): `name[0] == '@'` → compara 5 B con `@MFFE` y parsea 3 dígitos hex."""
    d = _d()
    # cmp r3,#0x40 justo después de ldrb r3,[r0]: la marca del nombre «@…»
    assert d[GET_ID + 0x8:GET_ID + 0xA] == b"\x03\x78"  # ldrb r3,[r0]
    assert d[GET_ID + 0xA:GET_ID + 0xC] == b"\x40\x2b"  # cmp r3,#0x40
    # el literal que compara (5 B) es @MFFE, el centinela que devuelve -1
    assert _pool_target(d, GET_ID + 0x9E, GET_ID + 0xA2) == POOL_MFFE
    assert _cstr(d, POOL_MFFE) == "@MFFE"
    # los tres dígitos: `cmp r,#0x40` + `subs r,#0x37` (letra) / `subs r,#0x30` (dígito)
    tramo = d[GET_ID + 0x9C:GET_ID + 0xDC]
    assert tramo.count(b"\x40\x2c") + tramo.count(b"\x40\x2b") == 3, tramo.hex()  # tres cmp contra 0x40
    assert d.count(b"\x37\x3c", GET_ID, GET_ID + 0x200) >= 1 and d.count(b"\x30\x3c", GET_ID, GET_ID + 0x200) >= 1
    # y el resultado es (d2<<8 | d3<<4) + d4: `lsls r4,r4,#8` y `lsls r2,r3,#4`
    assert b"\x24\x02" in d[GET_ID:GET_ID + 0x200] and b"\x1a\x01" in d[GET_ID:GET_ID + 0x200]


def test_los_ids_medidos_salen_del_nombre() -> None:
    """@M00A=0x0A (model/MEDIA medido), @M010=0x10 (@M010 medido), @M02F=0x2F (model/CONT_SHOTS_PB medido)."""
    assert _id_de_estrella("@M00A") == 0x0A
    assert _id_de_estrella("@M010") == 0x10
    assert _id_de_estrella("@M02F") == 0x2F
    assert _id_de_estrella("@MFFE") == -1  # el centinela
    assert _id_de_estrella("model/MEDIA") == -1  # los nombres largos van por la tabla, no por el parser


# ---------------------------------------------------------------- 2. la tabla id → clase
def test_la_entrada_de_m010_resuelve_modelbrowser() -> None:
    """libObj+0x40210c: `@M010` → `modelBrowser.so` → `ModelBrowserToInstance` (idioma `ldr`+`add rX,pc`)."""
    d = _d()
    assert _pool_target(d, ENTRADA_M010, ENTRADA_M010 + 2) == POOL_M010
    assert _cstr(d, POOL_M010) == "@M010"
    modulo = _pool_target(d, 0x00402114, 0x00402116)
    ctor = _pool_target(d, 0x0040211C, 0x0040211E)
    assert _cstr(d, modulo) == "modelBrowser.so"
    assert _cstr(d, ctor) == "ModelBrowserToInstance"
    # el nombre va seguido del módulo y del constructor en el pozo (misma entrada)
    assert d[POOL_M010:POOL_M010 + 0x1E] == b"@M010\0modelBrowser.so\0ModelBrowserToInstance"[0:0x1E]


def test_la_tabla_de_modelos_es_una_sola_funcion_y_usa_las_dos_plt() -> None:
    """Habla con `IdGenerator::Get` (0xdffb8) y `IdSoTable::add` (0xdf58c) —las mismas dos PLT que las vistas—."""
    d = _d()
    assert _simbolo_de_stub(d, PLT_IDGET).endswith("11IdGenerator3GetEPKc")
    assert _simbolo_de_stub(d, PLT_IDSADD).endswith("9IdSoTable3addEiPKcS1_")
    # el prólogo de la tabla es el de la función de registro (push múltiple + reserva de 0x54)
    assert d[TABLA_FN:TABLA_FN + 4] == b"\x2d\xe9\xf0\x4f"  # push.w {r4-r11,lr}
    assert d[TABLA_FN + 4:TABLA_FN + 6] == b"\x95\xb0"      # sub sp,#0x54
    # y en la entrada de @M010 se ve el orden: Get(@M010) → add(id, modulo, ctor)
    import capstone  # noqa: PLC0415

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    llamadas = [i.op_str for i in md.disasm(d[ENTRADA_M010:0x0040212C], ENTRADA_M010) if i.mnemonic.startswith("bl")]
    assert llamadas == ["#0xdffb8", "#0xdf58c"], llamadas


def test_la_tabla_coincide_con_los_otros_ids_medidos() -> None:
    """Cierra el significado de la tabla: @M00A=modelMedia (model/MEDIA=0x0A) y @M02F=modelContShotsPb."""
    d = _d()
    for base, estrella, modulo in (
        (0x00CBC955, "@M00A", "modelMedia.so"),
        (0x00CBCEBC, "@M02F", "modelContShotsPb.so"),
        (0x00CBCB1D, "@M015", "modelIndexPb.so"),
    ):
        texto = d[base:base + 48]
        assert texto.startswith(estrella.encode() + b"\0"), (estrella, texto[:12])
        assert modulo.encode() + b"\0" in texto, (estrella, texto)


# ---------------------------------------------------------------- 3. la clase y la fábrica
def test_modelbrowser_es_una_clase_de_libobj() -> None:
    """`ModelBrowser` está dentro de `libObj.so` (el `modelBrowser.so` de la tabla es el nombre de antes de la fusión)."""
    d = _d()
    assert _cstr(d, RTTI_MB) == "12ModelBrowser"
    assert _cstr(d, LOG_MB).startswith("[M_Browser] %s() ModelBrowser Info")
    assert not (LIB / "modelBrowser.so").exists()


def test_fabrica_y_tamano_del_objeto() -> None:
    """`ModelBrowserToInstance` exportada en libObj+0x47fa79: `new(0x134)` y constructor en +0x47fa48."""
    from elftools.elf.elffile import ELFFile  # noqa: PLC0415

    d = _d()
    e = ELFFile(open(LIB / "libObj.so", "rb"))
    simbolos = {s.name: s["st_value"] for s in e.get_section_by_name(".dynsym").iter_symbols() if s.name}
    assert simbolos.get("ModelBrowserToInstance") == FABRICA_MB + 1  # bit Thumb
    assert d[FABRICA_MB + 2:FABRICA_MB + 6] == b"\x4f\xf4\x9a\x70"  # mov.w r0,#0x134
    # la fábrica llama al constructor (bl +0x47fa48) y guarda el argumento en [objeto+0x20]
    import capstone  # noqa: PLC0415

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    cuerpo = [(i.mnemonic, i.op_str) for i in md.disasm(d[FABRICA_MB:FABRICA_MB + 0x1A], FABRICA_MB)]
    assert ("bl", "#0x47fa48") in cuerpo, cuerpo
    assert ("str", "r5, [r4, #0x20]") in cuerpo, cuerpo


# ---------------------------------------------------------------- 4. el diagnóstico del arnés es inerte
def test_la_orden_g_del_shim_solo_lee() -> None:
    """`«G modelo [max]»` sondea `getModelInfo` por códigos: no escribe nada y no se arma con ninguna variable."""
    fuente = (ROOT / "scripts/gui/harness/shim/sonyshim.c").read_text()
    assert "static void *gmihot(void *a)" in fuente
    assert 'ln[0] == \'G\' && ln[1] == \' \'' in fuente
    tramo = fuente[fuente.index("static void *gmihot(void *a)"):]
    tramo = tramo[:tramo.index("static void *startevhot")]
    assert "getModelInfo" in tramo and "calloc" in tramo
    for prohibido in ("mprotect", "memcpy(", "getenv", "memcpy ("):
        assert prohibido not in tramo, f"la orden de diagnóstico no debe escribir memoria ni leer entorno: {prohibido}"
