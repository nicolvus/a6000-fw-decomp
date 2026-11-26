"""G22-REPRO — de la tecla Reproducción (`0x1f7`) a la vista de reproducción, medido en los binarios, sin QEMU.

Lo que se fija aquí es el tramo estático del camino, leído de los ELF del firmware 3.21 que el arnés ya tiene copiados en
`analysis/gui/g22/harness/stage/cam/usr/lib` (artefactos no versionados: si no están, los tests se saltan):

1. el arnés entrega la clave que el firmware nombra `KEY_TACT_PLAY` (`0x1f7`) con el índice físico `0x1f`;
2. `viewUnified2.so` registra esa clave con el evento `0x150100f0` (tabla `InfraInput` de `.data`, triplete
   `{0x7ffffffe, clave, evento}`);
3. la tabla estática evento → acción de `viewUnified2.so` (`.rodata`) manda `0x150100f0` a la acción `4`;
4. el pozo de cadenas de `.rodata` conserva el trío *de antes de la fusión* `view/INDEX_PLAYBACK`,
   `viewIndexPb.so`, `ViewIndexPbToInstance` (vecinos, NO una tabla de registros: ver
   `docs/gui/g22-pbvista-carga-bajo-demanda.md` §1), y `viewIndexPb.so` **no existe** en el `/usr/lib` del firmware,
   mientras `ViewIndexPbToInstance` sí la exporta `viewUnified3.so`, que es el bundle que el registro real
   (`IdSoTable::add`, dos pasadas) asocia a `view/INDEX_PLAYBACK`; `view/SINGLEPB` se sirve de `viewUnified2.so`;
5. `libObj.so` exporta los modelos de reproducción (`ModelIndexPbToInstance`, `ModelSinglePbToInstance`,
   `ModelScrollSinglePbToInstance`).

El comportamiento en el invitado (qué vista se pinta, qué pide el modelo) se mide en QEMU y se documenta en
`docs/gui/g22-repro-reproduccion-sd.md`; estos tests no arrancan la VM.
"""
from __future__ import annotations

import ast
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"
sys.path.insert(0, str(ROOT / "scripts/gui/harness"))

if not (LIB / "libObj.so").exists() or not (LIB / "viewUnified2.so").exists():
    pytest.skip("faltan los binarios del arnés (analysis/gui/g22/harness/stage): test estático", allow_module_level=True)

KEY_TACT_PLAY = 0x1F7
EVENTO_REPRODUCCION = 0x150100F0
ACCION_REPRODUCCION = 4
# Direcciones del ELF 3.21 (VA = desplazamiento de fichero en el primer PT_LOAD; el segundo lleva +0x8000, por eso se usa v2o).
ENTRADA_CLAVE_PLAY = 0x10A6054  # libObj: {clave, puntero al nombre} medido, nombre «KEY_TACT_PLAY»
TABLA_EVENTO_ACCION = 0x3A03D4  # viewUnified2 .rodata: 19 pares {evento, acción}
TABLA_INFRAINPUT = (0x4AA000, 0x4AB400)  # viewUnified2 .data: tripletes {0x7ffffffe, clave, evento}
POZO_VIEWMANAGER = (0x3A1300, 0x3A1700)  # viewUnified2 .rodata: pozo ordenado de «view/…», «viewX.so», «ViewXToInstance»


class Elf:
    """Lector mínimo de un ELF32 little-endian: secciones por nombre, VA→fichero y símbolos dinámicos."""

    def __init__(self, ruta: Path) -> None:
        self.d = ruta.read_bytes()
        assert self.d[:4] == b"\x7fELF" and self.d[4] == 1 and self.d[5] == 1, f"no es ELF32 LE: {ruta}"
        phoff = struct.unpack_from("<I", self.d, 28)[0]
        phnum = struct.unpack_from("<H", self.d, 44)[0]
        self.segs = []
        for i in range(phnum):
            p_type, p_off, p_va, _pa, p_filesz, _msz, _fl, _al = struct.unpack_from("<IIIIIIII", self.d, phoff + i * 32)
            if p_type == 1:  # PT_LOAD
                self.segs.append((p_off, p_va, p_filesz))
        shoff = struct.unpack_from("<I", self.d, 32)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", self.d, 46)
        crudas = [struct.unpack_from("<IIIIIIIIII", self.d, shoff + i * shentsize) for i in range(shnum)]
        shstr = crudas[shstrndx]
        nombres = self.d[shstr[4] : shstr[4] + shstr[5]]
        self.secs = {}
        for r in crudas:
            fin = nombres.find(b"\0", r[0])
            self.secs[nombres[r[0] : fin].decode()] = {"addr": r[3], "off": r[4], "size": r[5]}

    def v2o(self, va: int) -> int | None:
        for off, base, tam in self.segs:
            if base <= va < base + tam:
                return off + (va - base)
        return None

    def u32(self, va: int) -> int | None:
        o = self.v2o(va)
        return None if o is None else struct.unpack_from("<I", self.d, o)[0]

    def cstr(self, va: int) -> str:
        o = self.v2o(va)
        assert o is not None, f"VA fuera de segmento: {va:#x}"
        return self.d[o : self.d.index(b"\0", o)].decode("utf-8", "replace")

    def cadenas(self, desde: int, hasta: int) -> list[tuple[int, str]]:
        """Cadenas imprimibles de un rango de VA (mismo criterio que `strings`)."""
        salida, va = [], desde
        while va < hasta:
            o = self.v2o(va)
            if o is None:
                break
            j = o
            while j < len(self.d) and 32 <= self.d[j] < 127:
                j += 1
            if j - o >= 3:
                salida.append((va, self.d[o:j].decode()))
            va += max(j - o, 1)
        return salida

    def dinamicos(self) -> dict[str, int]:
        sim, str_ = self.secs.get(".dynsym"), self.secs.get(".dynstr")
        if not sim or not str_:
            return {}
        nombres: dict[str, int] = {}
        for i in range(sim["size"] // 16):
            nombre, valor, _tam, _info, _otro, _shndx = struct.unpack_from("<IIIBBH", self.d, sim["off"] + i * 16)
            if nombre:
                fin = self.d.find(b"\0", str_["off"] + nombre)
                nombres[self.d[str_["off"] + nombre : fin].decode()] = valor
        return nombres


@pytest.fixture(scope="module")
def libobj() -> Elf:
    return Elf(LIB / "libObj.so")


@pytest.fixture(scope="module")
def viewunified2() -> Elf:
    return Elf(LIB / "viewUnified2.so")


def test_el_arnes_entrega_la_clave_key_tact_play() -> None:
    """`live.py` manda `(0x1f7, 0x1f)` para el botón Reproducción: la clave que nombra el firmware y su índice físico."""
    arbol = ast.parse((ROOT / "scripts/gui/harness/live.py").read_text(encoding="utf-8"))
    teclas = next(n for n in arbol.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "TECLAS")
    mapa = ast.literal_eval(teclas.value)
    assert mapa["reproduccion"] == (KEY_TACT_PLAY, 0x1F)


def test_libobj_nombra_la_clave_0x1f7(libobj: Elf) -> None:
    """La tabla `{clave, nombre}` de `libObj.so` da `0x1f7` = `KEY_TACT_PLAY` (medido en `0x10a6054`)."""
    apuntador = libobj.u32(ENTRADA_CLAVE_PLAY + 4)
    assert libobj.u32(ENTRADA_CLAVE_PLAY) == KEY_TACT_PLAY
    assert apuntador is not None and libobj.cstr(apuntador) == "KEY_TACT_PLAY"


def test_el_firmware_registra_0x1f7_con_el_evento_de_reproduccion(viewunified2: Elf) -> None:
    """Triplete `{0x7ffffffe, 0x1f7, 0x150100f0}` en `.data` de `viewUnified2.so`: la clave que registra la vista."""
    desde, hasta = TABLA_INFRAINPUT
    o = viewunified2.v2o(desde)
    assert o is not None
    palabras = [struct.unpack_from("<I", viewunified2.d, o + i * 4)[0] for i in range((hasta - desde) // 4)]
    tripletes = [(palabras[i + 1], palabras[i + 2]) for i in range(len(palabras) - 2) if palabras[i] == 0x7FFFFFFE]
    assert (KEY_TACT_PLAY, EVENTO_REPRODUCCION) in tripletes
    # y la tabla no es un caso aislado: las teclas medidas del arnés salen con los mismos eventos que el documento T7
    assert (0x1F0, 0x15010050) in tripletes  # MOVIE  → KEY_TACT_STARTSTOP
    assert (0x3, 0x15010070) in tripletes  # arriba → KEY_TACT_UP


def test_el_evento_de_reproduccion_es_la_accion_4(viewunified2: Elf) -> None:
    """Tabla estática evento → acción de `viewUnified2.so`: `0x150100f0` → acción `4`, primera de 19 entradas."""
    pares = [(viewunified2.u32(TABLA_EVENTO_ACCION + i * 8), viewunified2.u32(TABLA_EVENTO_ACCION + i * 8 + 4)) for i in range(19)]
    assert pares[0] == (EVENTO_REPRODUCCION, ACCION_REPRODUCCION)
    assert all(ev is not None and 0x15000000 <= ev <= 0x150FFFFF for ev, _ in pares), "todas las entradas son eventos InfraInput"
    assert all(accion is not None and accion < 0x100 for _, accion in pares), "la acción es un número pequeño, no una dirección"
    # la tabla termina justo donde empiezan las cadenas del blob siguiente
    assert pares[-1] == (0x15050050, 12)


def test_pozo_de_cadenas_index_playback_cita_una_biblioteca_que_no_existe(viewunified2: Elf) -> None:
    """En el pozo, tras `view/INDEX_PLAYBACK` vienen `viewIndexPb.so` y `ViewIndexPbToInstance`; el `.so` no existe.

    OJO: es el **pozo ordenado** (trío de antes de la fusión), no el registro; el registro real vive en
    `viewUnified2+0x194844` y asocia la vista al bundle `viewUnified3.so`
    (`docs/gui/g22-pbvista-carga-bajo-demanda.md`, `tests/test_g22_pbvista.py`).
    """
    desde, hasta = POZO_VIEWMANAGER
    cadenas = [s for _va, s in viewunified2.cadenas(desde, hasta)]
    i = cadenas.index("view/INDEX_PLAYBACK")
    assert cadenas[i + 1] == "viewIndexPb.so"
    assert cadenas[i + 2] == "ViewIndexPbToInstance"
    assert not (LIB / "viewIndexPb.so").exists(), "si apareciera, el bloqueo de G22-REPRO cambia: revisar el informe"
    # el símbolo sí existe: otra biblioteca del firmware lo exporta
    assert "ViewIndexPbToInstance" in Elf(LIB / "viewUnified3.so").dinamicos()


def test_singlepb_si_lo_exporta_viewunified2(viewunified2: Elf) -> None:
    """La vista de una foto (`view/SINGLEPB`) no depende de una biblioteca ausente: `viewUnified2.so` la exporta."""
    assert "ViewSinglePbToInstance" in viewunified2.dinamicos()


def test_libobj_exporta_los_modelos_de_reproduccion(libobj: Elf) -> None:
    """Los modelos que necesita la vista de reproducción están en `libObj.so` (no hace falta inventarlos)."""
    simbolos = libobj.dinamicos()
    for modelo in ("ModelIndexPbToInstance", "ModelSinglePbToInstance", "ModelScrollSinglePbToInstance"):
        assert modelo in simbolos, f"falta {modelo} en libObj.so"


def test_la_sd_con_estructura_conserva_la_foto_de_1536x1024(tmp_path: Path) -> None:
    """La SD que recibe el invitado lleva `AVF_INFO`, y la foto del anfitrión entra byte a byte (contenido real, no inventado)."""
    if any(__import__("shutil").which(h) is None for h in ("mkfs.vfat", "mmd", "mcopy", "mdir")):
        pytest.skip("faltan mtools/dosfstools")
    import sd_image

    raiz = tmp_path / "sd"
    (raiz / "DCIM" / "100MSDCF").mkdir(parents=True)
    foto = b"\xff\xd8\xff\xe0" + bytes(range(256)) * 300
    (raiz / "DCIM" / "100MSDCF" / "DSC00001.JPG").write_bytes(foto)
    img = tmp_path / "sd.head"
    sd_image.construye(raiz, img, 0.25, completa=True)
    sacada = tmp_path / "sacada.jpg"
    subprocess.run(["mcopy", "-i", str(img), "::/DCIM/100MSDCF/DSC00001.JPG", str(sacada)], check=True,
                   env={"MTOOLS_SKIP_CHECK": "1", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
    assert sacada.read_bytes() == foto, "la foto del anfitrión se copia encima sin tocarla"
    avf = subprocess.run(["mdir", "-i", str(img), "-/", "::/AVF_INFO"], capture_output=True, text=True, check=True,
                         env={"MTOOLS_SKIP_CHECK": "1", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}).stdout
    for nombre in ("AVIN0001.INP", "AVIN0001.BNP", "AVIN0001.INT", "PRV00001.BIN", "STAT0000.BIN"):
        # mtools pinta los nombres 8.3 con espacio en vez de punto («AVIN0001 INP»)
        assert nombre.replace(".", " ") in avf, f"falta {nombre} en AVF_INFO"


# --- G22-REPRO-3: las listas de teclas por grupo y las trampas de la medición ---------------------------------------
# Medido en el invitado (perfil repro5, puerto 8671, 26-11-2026): InfraInput::SetEventKeyList se llama 17 veces con los
# grupos 1…0x11 y las cuentas 3, 0x1a, 1, 1, 1, 1, 0xca (202), 8, 5, 6, 1, 1, 1, 1, 4 (0xf = la Reproducción), 1, 1.
TABLA_LISTAS = 0x4AA59C  # viewUnified2 .data: descriptores {lista, callback, nº de entradas, 0, 0} de 20 B; el índice es el grupo
CUENTAS_MEDIDAS = {7: 202, 8: 8, 9: 5, 10: 6, 0xF: 4, 0x10: 1, 0x11: 1}


def _lista_de_teclas(viewunified2: Elf, grupo: int) -> tuple[int, int, list[tuple[int, int, int]]]:
    """(callback, nº de entradas, entradas) del grupo `grupo` según la tabla de descriptores de `.data`."""
    base = TABLA_LISTAS + 20 * grupo
    lista, callback, cuantas = viewunified2.u32(base), viewunified2.u32(base + 4), viewunified2.u32(base + 8)
    assert lista is not None and callback is not None and cuantas is not None
    entradas = []
    for i in range(cuantas):
        clave, evento, mascara = (viewunified2.u32(lista + 12 * i + 4 * k) for k in range(3))
        assert clave is not None and evento is not None and mascara is not None
        entradas.append((clave, evento, mascara))
    return callback, cuantas, entradas


def test_la_tecla_de_reproduccion_vive_en_el_grupo_0xf(viewunified2: Elf) -> None:
    """La lista del grupo `0xf` es la de la Reproducción: 4 entradas `{clave, evento, máscara}` y la primera es `0x1f7`."""
    callback, cuantas, entradas = _lista_de_teclas(viewunified2, 0xF)
    assert (callback, cuantas) == (0x181A3D, 4)
    assert entradas[0] == (KEY_TACT_PLAY, EVENTO_REPRODUCCION, 0x7FFFFFFE)
    assert [e[0] for e in entradas] == [0x1F7, 0x7095, 0x0A000022, 0x0A00001C]
    assert all(m == 0x7FFFFFFE for _c, _e, m in entradas), "0x7ffffffe = «sin condición», tercera palabra de la entrada"


def test_la_vista_de_disparo_registra_una_lista_sin_la_tecla_de_reproduccion(viewunified2: Elf) -> None:
    """El grupo 7 (202 entradas) es el que registra la vista de disparo: tiene la tecla de encendido y **no** la de reproducción."""
    callback, cuantas, entradas = _lista_de_teclas(viewunified2, 7)
    assert (callback, cuantas) == (0x1816D5, 202)
    assert (0x2, 0x15010010) in [(c, e) for c, e, _m in entradas], "coincide con el log medido `insert key_code=0x2 event_code=0x15010010`"
    assert KEY_TACT_PLAY not in [c for c, _e, _m in entradas]


def test_las_cuentas_de_los_descriptores_coinciden_con_el_invitado(viewunified2: Elf) -> None:
    """Cada grupo que el invitado registró con su cuenta tiene en `.data` esa misma cuenta (mapea grupo → descriptor)."""
    for grupo, cuantas in CUENTAS_MEDIDAS.items():
        assert _lista_de_teclas(viewunified2, grupo)[1] == cuantas, f"grupo {grupo:#x}"


def test_dispatch_event_es_un_thunk_virtual(libobj: Elf) -> None:
    """`ActionEventMapBase::DispatchEvent` (0xf59f0) solo salta a la ranura +8 de la vtable: la conversión no está en libObj."""
    o = libobj.v2o(0xF59F0)
    assert o is not None
    assert struct.unpack_from("<HHH", libobj.d, o) == (0x6803, 0xB580, 0xAF00)  # ldr r3,[r0] · push {r7,lr} · add r7,sp,#0
    assert struct.unpack_from("<H", libobj.d, o + 6)[0] == 0x689B  # ldr r3,[r3,#8]
    assert struct.unpack_from("<H", libobj.d, o + 8)[0] == 0x4798  # blx r3


def test_las_direcciones_de_las_trampas_son_las_de_la_medicion(libobj: Elf) -> None:
    """Las direcciones que usó la traza del invitado son las de los símbolos (si cambia el binario, hay que rehacerla)."""
    simbolos = libobj.dinamicos()
    esperado = {
        "_ZN10InfraInput15SetEventKeyListEiP18_InfraInputKeyListi": 0x806140,
        "_ZN10InfraInput14GetEventStatusEiiP16_InfraInputEvent": 0x805804,
        "snd_InfraInputEvent_to_InputServant": 0x110138,
        "_ZN12InputService11createEventEmh": 0x1106B8,
        "_ZN12InputService15pushFilterEventEP5Event": 0x1117F4,
        "_ZN11DefRootView18ActionEventMapBase13DispatchEventEm": 0xF59F0,
        "_ZN11DefRootView21ActionCheckerListBase10execActionEi": 0x11817E,
        "_ZN13viewManagerIf8openViewEPKci": 0x1251FC,
    }
    for nombre, va in esperado.items():
        assert nombre in simbolos, f"falta {nombre}"
        assert simbolos[nombre] & ~1 == va, f"{nombre} en {simbolos[nombre]:#x}, se esperaba {va:#x}"
