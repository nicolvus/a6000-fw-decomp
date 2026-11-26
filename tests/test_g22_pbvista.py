"""G22-PBVISTA — el registro de vistas y el cargador bajo demanda de `viewUnified2.so`, leído de los ELF 3.21, sin QEMU.

Fija lo que el informe `docs/gui/g22-pbvista-carga-bajo-demanda.md` da por VERIFICADO, y **corrige** una premisa que
el repo arrastraba («la tabla del ViewManager son tripletes `view/…`, `viewX.so`, `ViewXToInstance` seguidos en
`.rodata`», `tests/test_g22_repro.py` y [G22-REPRO]):

1. La zona `0x391a18..0x3a2bea` de `viewUnified2.so` es un **pozo de cadenas ordenado**, no una tabla de tripletes:
   los vecinos de `view/INDEX_PLAYBACK` son `viewIndexPb.so` y `ViewIndexPbToInstance`, y ese `viewIndexPb.so`
   **no existe** en el `/usr/lib` de la cámara 3.21 (sólo hay `viewUnified2..8.so`). Ningún word de 4 bytes del fichero
   contiene la dirección de esas cadenas: no hay tabla de punteros.
2. El registro se construye en **código**: una función Thumb (entrada de `.ARM.exidx` `viewUnified2+0x194844`) que,
   por cada vista, llama a `IdGenerator::Get("view/NOMBRE")` (PLT `0xe71b8`) y a
   `IdSoTable::add(id, "<modulo>.so", "<Clase>ToInstance")` (PLT `0xe5b4c`).
3. Se hace en **dos pasadas**: la 1.ª registra el nombre del módulo *de antes de la fusión* (`viewIndexPb.so` en
   `+0x194fdc`) y la 2.ª lo **sobrescribe** con el bundle que de verdad existe (`viewUnified3.so` en `+0x196796`,
   mismo `ViewIndexPbToInstance`). El prólogo de la 2.ª pasada (`+0x1960e8`) carga los siete bundles en registros,
   en el mismo orden que la lista de `.rodata` `0x3a2b8a`.
4. El cargador bajo demanda vive en `libObj`: `ViewIdSoTable`/`IdSoTable` (exportados) y, por vista,
   `dlopen([this+0x10], 0x101)` en `libObj+0x7f11d8` → `dlsym(h, [this+0x14])` en `+0x7f11e6` → llamada al
   constructor con `([this], [this+0x20])`; el handle se guarda en `[this+0x18]` y la instancia en `[this+0x1c]`.
   `ViewIdSoTable::getInstance` (`libObj+0x7f22d1`) es el singleton que consume ese registro.
5. `ViewIndexPbToInstance` la exporta **`viewUnified3.so`** (y no `viewUnified2.so`): por eso el `dlopen` que se
   mide en el invitado al abrir `view/INDEX_PLAYBACK` es `viewUnified3.so`.

Los binarios viven en `analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados): si faltan, el módulo se salta.
No arranca ninguna VM; el comportamiento en el invitado (qué dlopen sale, qué se pinta) está en el informe y en
`reports/evidence/g22-pbvista-20261126/`.
"""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

import capstone  # dependencia del proyecto (la usan tests/test_g104_iso_ui.py y otros)

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"

if not (LIB / "libObj.so").exists() or not (LIB / "viewUnified2.so").exists():
    pytest.skip("faltan los binarios del arnés (analysis/gui/g22/harness/stage): test estático", allow_module_level=True)

# ---------------------------------------------------------------- direcciones (VA = desplazamiento, ELF 3.21)
LISTA_BUNDLES = 0x3A2B8A  # .rodata: los 7 «viewUnifiedN.so», de 16 en 16 bytes
LISTA_ORDEN = ["viewUnified8.so", "viewUnified3.so", "viewUnified4.so", "viewUnified7.so",
               "viewUnified6.so", "viewUnified2.so", "viewUnified5.so"]
POOL_INDEX_PB = 0x3A14C1  # .rodata: «view/INDEX_PLAYBACK»
POOL_INDEX_PB_SO = 0x3A14D5  # .rodata: «viewIndexPb.so» (módulo de antes de la fusión; no existe en disco)
POOL_INDEX_PB_CTOR = 0x3A14E4  # .rodata: «ViewIndexPbToInstance»
REGISTRO_FN = 0x194844  # entrada de .ARM.exidx: la función que registra las vistas
ENTRADA_PASADA1 = 0x194FDC  # blx IdSoTable::add de la 1.ª pasada para view/INDEX_PLAYBACK
ENTRADA_PASADA2 = 0x196796  # blx IdSoTable::add de la 2.ª pasada para view/INDEX_PLAYBACK
PLT_IDGENERATOR_GET = 0xE71B8
PLT_IDSOTABLE_ADD = 0xE5B4C
CARGADOR_OPEN = 0x7F11CA  # libObj: dlopen([this+0x10], 0x101) + dlsym + constructor
CARGADOR_DLOPEN = 0x7F11D8
CARGADOR_DLSYM = 0x7F11E6
VIEWIDSO_GETINSTANCE = 0x7F22D1


def _d(nombre: str) -> bytes:
    return (LIB / nombre).read_bytes()


def _cstr(d: bytes, va: int, maxlen: int = 100) -> str | None:
    if not 0 < va < len(d):
        return None
    fin = d.find(b"\0", va)
    if fin < 0 or fin - va > maxlen:
        return None
    b = d[va:fin]
    if not b or not all(32 <= c < 127 for c in b):
        return None
    return b.decode("ascii")


def _pool_target(d: bytes, ldr_addr: int, add_addr: int) -> int | None:
    """Resuelve el idioma PIC de estos binarios: `ldr rX,[pc,#imm]` + `add rX, pc`.

    OJO: para `add rX, pc` (Thumb, ADD registro con PC) el PC vale **dirección + 4 sin alinear**; con la base
    alineada a 4 los literales de `sb`/`sl`/`r8` del prólogo de la segunda pasada caen 2 bytes antes y devuelven
    un trozo de la cadena anterior (medido: `'o'`, la cola de `viewUnified8.so`).
    """
    hw1, hw2 = struct.unpack_from("<HH", d, ldr_addr)
    if hw1 == 0xF8DF:  # ldr.w Rt,[pc,#imm12]
        slot = ((ldr_addr + 4) & ~3) + (hw2 & 0xFFF)
    elif (hw1 & 0xF800) == 0x4800:  # ldr Rt,[pc,#imm8*4]
        slot = ((ldr_addr + 4) & ~3) + (hw1 & 0xFF) * 4
    else:
        return None
    if not 0 <= slot < len(d) - 4:
        return None
    return (struct.unpack_from("<I", d, slot)[0] + add_addr + 4) & 0xFFFFFFFF


def _entrada(d: bytes, blx_addr: int, ventana: int = 0x28) -> dict[str, str]:
    """Cadenas que resuelve el bloque que termina en `blx IdSoTable::add` (mira hacia atrás `ventana` bytes)."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    salida: dict[str, str] = {}
    pendiente: dict[str, int] = {}  # registro -> dirección del `ldr rX,[pc,#imm]` que le toca
    for i in md.disasm(d[blx_addr - ventana:blx_addr], blx_addr - ventana):
        if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
            pendiente[i.op_str.split(",")[0].strip()] = i.address
        elif i.mnemonic in ("mov", "movs") and "," in i.op_str:
            destino, origen = [x.strip() for x in i.op_str.split(",", 1)]
            if origen in salida:
                salida[destino] = salida[origen]
        elif i.mnemonic == "add" and i.op_str.endswith(", pc"):
            reg = i.op_str.split(",")[0].strip()
            if reg in pendiente:
                t = _pool_target(d, pendiente[reg], i.address)
                s = _cstr(d, t) if t is not None else None
                if s:
                    salida[reg] = s
    return salida


# ---------------------------------------------------------------- 1. la lista de bundles
def test_lista_de_bundles_en_rodata() -> None:
    """`.rodata 0x3a2b8a`: los siete `viewUnifiedN.so`, de 16 en 16 bytes y en el orden que carga el prólogo."""
    d = _d("viewUnified2.so")
    for k, esperado in enumerate(LISTA_ORDEN):
        assert _cstr(d, LISTA_BUNDLES + 16 * k) == esperado, f"entrada {k} de la lista de bundles"
    # el octavo nombre ya no es un bundle: la lista son exactamente siete
    assert not (_cstr(d, LISTA_BUNDLES + 16 * 7) or "").startswith("viewUnified")


# ---------------------------------------------------------------- 2. no hay tabla de punteros
def test_el_pozo_de_cadenas_no_tiene_punteros() -> None:
    """Ni `view/INDEX_PLAYBACK` ni su módulo ni su constructor tienen un puntero de 4 bytes en todo el fichero.

    Es la prueba de que el registro es CÓDIGO (idioma `ldr`+`add rX,pc`) y no una tabla de tripletes; la
    vecindad de las cadenas es sólo el orden del pozo (que conserva el módulo de antes de la fusión).
    """
    d = _d("viewUnified2.so")
    for va in (POOL_INDEX_PB, POOL_INDEX_PB_SO, POOL_INDEX_PB_CTOR, LISTA_BUNDLES):
        patron = struct.pack("<I", va)
        pos = d.find(patron)
        assert pos < 0, f"hay un puntero a {va:#x} en {pos:#x} (¿vuelve a ser una tabla de punteros?)"


# ---------------------------------------------------------------- 3. las dos pasadas del registro
def test_registro_primera_pasada_modulo_de_fabrica() -> None:
    """`viewUnified2+0x194fdc`: `IdSoTable::add(id(view/INDEX_PLAYBACK), "viewIndexPb.so", "ViewIndexPbToInstance")`."""
    d = _d("viewUnified2.so")
    e = _entrada(d, ENTRADA_PASADA1)
    assert e.get("r0") == "view/INDEX_PLAYBACK", e
    assert e.get("r2") == "viewIndexPb.so", e
    assert e.get("r3") == "ViewIndexPbToInstance", e
    # el módulo de fábrica NO existe en el /usr/lib de la cámara: sólo los siete bundles
    assert not (LIB / "viewIndexPb.so").exists()
    assert sorted(p.name for p in LIB.glob("view*.so")) == [
        "viewUnified2.so", "viewUnified3.so", "viewUnified4.so", "viewUnified5.so",
        "viewUnified6.so", "viewUnified7.so", "viewUnified8.so",
    ]


def test_registro_segunda_pasada_bundle() -> None:
    """`viewUnified2+0x196796`: la 2.ª pasada SOBRESCRIBE el módulo con el bundle `viewUnified3.so`."""
    d = _d("viewUnified2.so")
    # la ventana llega hasta el prólogo de la 2.ª pasada (+0x1960e8), que es donde se cargan los bundles en registros
    e = _entrada(d, ENTRADA_PASADA2, ventana=0x700)
    assert e.get("r0") == "view/INDEX_PLAYBACK", e
    assert e.get("r3") == "ViewIndexPbToInstance", e
    assert e.get("r2") == "viewUnified3.so", e


def test_prologo_de_la_segunda_pasada_carga_los_siete_bundles() -> None:
    """`viewUnified2+0x1960e8`: seis registros con seis bundles (el séptimo es el propio `viewUnified2.so`)."""
    d = _d("viewUnified2.so")
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    regs: dict[str, int] = {}
    vistos: dict[str, str] = {}
    for i in md.disasm(d[0x1960E8:0x19612A], 0x1960E8):
        if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
            regs[i.op_str.split(",")[0].strip()] = i.address
        elif i.mnemonic == "add" and i.op_str.endswith(", pc"):
            rd = i.op_str.split(",")[0].strip()
            if rd in regs:
                t = _pool_target(d, regs[rd], i.address)
                s = _cstr(d, t) if t is not None else None
                if s and s.startswith("viewUnified"):
                    vistos[rd] = s
    assert vistos.get("sb") == "viewUnified3.so", vistos  # el que usa la entrada de INDEX_PLAYBACK
    assert vistos.get("r5") == "viewUnified4.so", vistos
    assert vistos.get("fp") == "viewUnified6.so", vistos
    assert vistos.get("r6") == "viewUnified5.so", vistos


def test_la_funcion_de_registro_es_una_sola_y_usa_las_plt_del_registro() -> None:
    """La entrada de `.ARM.exidx` `0x194844` es la función de registro y llama a las dos PLT del registro."""
    d = _d("viewUnified2.so")
    assert d[REGISTRO_FN:REGISTRO_FN + 2] == b"\x01\x2a"  # cmp r2,#1 (la segunda pasada entra con r2 != 1)
    cuerpo = d[REGISTRO_FN:0x197000]
    for plt, nombre in ((PLT_IDGENERATOR_GET, "IdGenerator::Get"), (PLT_IDSOTABLE_ADD, "IdSoTable::add")):
        imm = (plt - (REGISTRO_FN + 4)) >> 1
        assert -0x800000 <= imm < 0x800000
        # hay al menos una llamada `blx` cuyo desplazamiento relativo cae en esa PLT
        hallado = False
        for off in range(0, len(cuerpo) - 4, 2):
            hw1, hw2 = struct.unpack_from("<HH", cuerpo, off)
            if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xC000) != 0xC000:
                continue
            s = (hw1 >> 10) & 1
            j1, j2 = (hw2 >> 13) & 1, (hw2 >> 11) & 1
            i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
            des = (s << 24) | (i1 << 23) | (i2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
            if s:
                des -= 1 << 25
            if ((REGISTRO_FN + off + 4 + des) & 0xFFFFFFFF) == plt:
                hallado = True
                break
        assert hallado, f"la función de registro no llama a {nombre} (PLT {plt:#x})"


# ---------------------------------------------------------------- 4. el cargador de libObj
def test_cargador_bajo_demanda_de_libobj() -> None:
    """`libObj+0x7f11ca`: `dlopen([this+0x10], 0x101)`; handle en `[this+0x18]`, `dlsym(h,[this+0x14])`, instancia en `[this+0x1c]`."""
    d = _d("libObj.so")
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    texto = {i.address: i for i in md.disasm(d[CARGADOR_OPEN:CARGADOR_DLSYM + 0x30], CARGADOR_OPEN)}
    assert CARGADOR_OPEN in texto and texto[CARGADOR_OPEN].mnemonic == "push"
    # movw r1,#0x101 (RTLD_LAZY|RTLD_GLOBAL) justo antes del ldr del nombre y del dlopen
    assert d[0x7F11D2:0x7F11D6] == bytes.fromhex("40f20111"), d[0x7F11D2:0x7F11D6].hex()
    assert texto[0x7F11D6].mnemonic == "ldr" and texto[0x7F11D6].op_str.replace(" ", "") == "r0,[r0,#0x10]"
    assert texto[CARGADOR_DLOPEN].mnemonic in ("blx", "bl"), texto[CARGADOR_DLOPEN]
    assert texto[CARGADOR_DLSYM].mnemonic in ("blx", "bl"), texto[CARGADOR_DLSYM]
    # el handle va a [this+0x18] y la instancia a [this+0x1c]
    assert d[0x7F11DC:0x7F11DE] == bytes.fromhex("a061")  # str r0,[r4,#0x18]
    assert texto[0x7F11DC].op_str.replace(" ", "") == "r0,[r4,#0x18]"
    assert texto[0x7F11F4].op_str.replace(" ", "") == "r0,[r4,#0x1c]"
    # y el singleton que consume el registro está exportado
    syms = (LIB / "libObj.so").read_bytes()
    assert b"_ZN13ViewIdSoTable11getInstanceEv" in syms and b"_ZN9IdSoTable3addEiPKcS1_" in syms


# ---------------------------------------------------------------- 5. quién exporta el constructor
def _exporta(nombre: str, simbolo: str) -> bool:
    """¿`nombre` define el símbolo `simbolo` en su tabla dinámica? (la cadena puede estar en .rodata sin definirla)"""
    d = _d(nombre)
    shoff = struct.unpack_from("<I", d, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", d, 46)
    secciones = []
    for i in range(shnum):
        secciones.append(struct.unpack_from("<IIIIIIIIII", d, shoff + i * shentsize))
    nombres_off = secciones[shstrndx][4]
    por_nombre: dict[str, tuple[int, ...]] = {}
    for sec in secciones:
        crudo = d[nombres_off + sec[0]:d.index(b"\0", nombres_off + sec[0])]
        por_nombre[crudo.decode()] = sec
    dynsym, dynstr = por_nombre[".dynsym"], por_nombre[".dynstr"]
    for i in range(0, dynsym[5], 16):
        st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", d, dynsym[4] + i)
        fin = d.index(b"\0", dynstr[4] + st_name)
        if d[dynstr[4] + st_name:fin].decode() == simbolo:
            return st_shndx != 0 and st_value != 0
    return False


def test_constructor_de_index_playback_lo_exporta_viewunified3() -> None:
    assert _exporta("viewUnified3.so", "ViewIndexPbToInstance")
    assert not _exporta("viewUnified2.so", "ViewIndexPbToInstance")
    # el nombre está en el pozo de viewUnified2 (por eso una búsqueda de cadenas no basta)
    assert b"ViewIndexPbToInstance" in _d("viewUnified2.so")
