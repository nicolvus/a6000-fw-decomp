"""G22-ZOOM: «Ajuste de zoom» (model/CAMERA) — verificación en bytes de la especificación estática.

Todo lo que se comprueba aquí está leído en instrucciones de `libObj.so` 3.21 (md5 `eb12512e…`, el
del arnés) y en la tabla de despacho de CamMgr de `av-cam.bin` 3.21. Informe:
`docs/gui/g22-ajuste-zoom.md`.

- Emisores del modelo: `libObj+0x4bf108` (precisión) y `libObj+0x4bf230` (inteligente).
- Respuesta esperada: CMP `0x7613`/`0x7615` (categoría `0x3130`) y EVT `0x85b1`/`0x85b2` (`0x3100`),
  las emite `ObjCamera` dentro de `libObj` (secuencias `0x956e2c`/`0xa0d43c`); no pasan por CamMgr.
- La tabla de CamMgr (`av-cam.bin` 0xabcd30, 203 registros de 16 B) no tiene ningún id `0x7xxx`.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIBOBJ = ROOT / "analysis/gui/g22/harness/stage/cam/lib/libObj.so"
LIBOBJ_ALT = ROOT / "analysis/camera-extract/usr/lib/libObj.so"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"

capstone = pytest.importorskip("capstone")

# Tabla de nombres de libObj (.data.rel.ro, 3364 punteros): MSGID desde el índice 1 = 0x7500,
# PARAMID desde el índice 726 = 0x9500, VALUEID desde el índice 2076 = 0. EVT: índice 618 = 0x85a6.
TABLA_NOMBRES = 0xFDB5EC
N_NOMBRES = 3364
PARAMID_BASE, PARAMID_IDX = 0x9500, 726
VALUEID_IDX = 2076
EVT_ANCLA, EVT_ANCLA_IDX = 0x85A6, 618
# Tabla de despacho de CamMgr en av-cam.bin: 203 registros de 16 B {handler, msg_id, tamaño, siguiente}.
CAMGMR_TABLA, CAMGMR_N = 0xABCD30, 203


def _libobj() -> Path:
    for p in (LIBOBJ, LIBOBJ_ALT):
        if p.is_file():
            return p
    pytest.skip("libObj.so 3.21 ausente (harness/stage o camera-extract)")


def _dis(addr: int, n: int = 1) -> list[tuple[int, str, str]]:
    d = _libobj().read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    out = []
    for i in md.disasm(d[addr : addr + 4 * n], addr):
        out.append((i.address, i.mnemonic, i.op_str))
        if len(out) == n:
            break
    return out


def _ins(addr: int) -> str:
    """«mnemónico op_str» de la instrucción que empieza en `addr` (Thumb, 2 o 4 B)."""
    i = _dis(addr)[0]
    return f"{i[1]} {i[2]}"


def _nombres() -> list[str]:
    d = _libobj().read_bytes()
    ptrs = struct.unpack_from(f"<{N_NOMBRES}I", d, TABLA_NOMBRES)
    out = []
    for p in ptrs:
        if not p or p >= len(d):
            out.append("")
            continue
        out.append(d[p : d.find(b"\0", p)].decode("utf-8", "replace"))
    return out


def test_el_modelo_emite_las_dos_ordenes_de_zoom_a_objcamera() -> None:
    """§2: ModelCamera arma ObjMsg(0x3100, 0x7614|0x7612) y la envía al objeto 8 (ObjCamera)."""
    # Precisión: 0x4bf132 mov.w r1,#0x3100 · 0x4bf136 movw r2,#0x7614 · 0x4bf16c conversor · 0x4bf18e envío
    assert _ins(0x4BF132) == "mov.w r1, #0x3100"
    assert _ins(0x4BF136) == "movw r2, #0x7614"
    assert _ins(0x4BF16C) == "bl #0x4da51c"  # añade el parámetro 0x979b (conversión modelo→cámara)
    assert _ins(0x4BF180) == "movs r0, #8"  # objeto 8 = 008_ObjCamera
    assert _ins(0x4BF182) == "bl #0x42067c"  # resolución del objeto por índice
    assert _ins(0x4BF18E) == "bl #0x4bcc54"  # envío (IssueCommandAsync a través de 0x4bcc54)
    # Inteligente: 0x4bf25a/0x4bf25e y 0x4bf294/0x4bf2b6.
    assert _ins(0x4BF25A) == "mov.w r1, #0x3100"
    assert _ins(0x4BF25E) == "movw r2, #0x7612"
    assert _ins(0x4BF294) == "bl #0x4da600"  # parámetro 0x9798
    assert _ins(0x4BF2A8) == "movs r0, #8"
    assert _ins(0x4BF2B6) == "bl #0x4bcc54"


def test_los_ids_del_zoom_en_la_tabla_de_nombres_de_libobj() -> None:
    """§1: categoría 0x3100; CMD 0x7612/0x7614, CMP 0x7613/0x7615, EVT 0x85b1/0x85b2, PARAMID 0x9798/0x979b."""
    n = _nombres()
    assert n[275] == "MSGID_SET_DIRECT_SMART_EZOOM_MODE_CMD"  # 0x7500 + 275 − 1 = 0x7612
    assert n[276] == "MSGID_SET_DIRECT_SMART_EZOOM_MODE_CMP"  # 0x7613
    assert n[277] == "MSGID_SET_DIRECT_PRECISION_EZOOM_MODE_CMD"  # 0x7614
    assert n[278] == "MSGID_SET_DIRECT_PRECISION_EZOOM_MODE_CMP"  # 0x7615
    assert n[EVT_ANCLA_IDX] == "MSGID_NOTIFY_FRONT_ESHUTTER_MODE_EVT"  # ancla: ese índice es 0x85a6
    assert n[629] == "MSGID_NOTIFY_DIRECT_SMART_EZOOM_MODE_EVT"  # 0x85a6 + 11 = 0x85b1
    assert n[630] == "MSGID_NOTIFY_DIRECT_PRECISION_EZOOM_MODE_EVT"  # 0x85b2
    assert n[PARAMID_IDX + (0x9798 - PARAMID_BASE)] == "PARAMID_DIRECT_SMART_EZOOM_MODE"
    assert n[PARAMID_IDX + (0x979B - PARAMID_BASE)] == "PARAMID_DIRECT_PRECISION_EZOOM_MODE"
    # Los SET/ACT que viajan en la respuesta son contiguos (los usa el modelo, §4).
    assert n[PARAMID_IDX + (0x9799 - PARAMID_BASE)] == "PARAMID_DIRECT_SMART_EZOOM_MODE_SET"
    assert n[PARAMID_IDX + (0x979A - PARAMID_BASE)] == "PARAMID_DIRECT_SMART_EZOOM_MODE_ACT"
    assert n[PARAMID_IDX + (0x979D - PARAMID_BASE)] == "PARAMID_DIRECT_PRECISION_EZOOM_MODE_SET"
    assert n[PARAMID_IDX + (0x979F - PARAMID_BASE)] == "PARAMID_DIRECT_PRECISION_EZOOM_MODE_ACT"


def test_valores_del_ajuste_de_zoom() -> None:
    """§3: el valor del menú viaja como VALUEID, no como número: 0→1,4×, 1→2,0×, 2→apagado (inteligente);
    0→precisión activada, 1→desactivada."""
    n = _nombres()
    for vid, nombre in ((0x2D9, "VALUEID_DIRECT_SMART_EZOOM_1_4"), (0x2DA, "VALUEID_DIRECT_SMART_EZOOM_2_0"),
                        (0x2DB, "VALUEID_DIRECT_SMART_EZOOM_OFF"), (0x2DC, "VALUEID_DIRECT_PRECISION_EZOOM_ON"),
                        (0x2DD, "VALUEID_DIRECT_PRECISION_EZOOM_OFF")):
        assert n[VALUEID_IDX + vid] == nombre, hex(vid)
    # Conversores del modelo (VERIFICADO instrucción a instrucción): 0x4e35e8 modelo→cámara (inteligente),
    # 0x4e3694 (precisión) y sus inversos 0x4e3638 / 0x4e36dc que aplican el EVT en el modelo.
    assert _ins(0x4E3610) == "movw r3, #0x2db"  # modelo 2 → apagado
    assert _ins(0x4E3616) == "movw r3, #0x2d9"  # modelo 0 → 1,4×
    assert _ins(0x4E3622) == "movw r3, #0x2da"  # modelo 1 → 2,0×
    assert _ins(0x4E36B6) == "movw r3, #0x2dd"  # precisión modelo 1 → desactivada
    assert _ins(0x4E36C2) == "mov.w r3, #0x2dc"  # precisión modelo 0 → activada
    assert _ins(0x4E3658) == "movw r3, #0x2da"  # inverso (cámara→modelo)


def test_objcamera_responde_en_proceso_y_el_modelo_lee_set_y_act() -> None:
    """§5: el despachador de ObjCamera atiende 0x7612/0x7614 y sus secuencias emiten CMP (0x3130) y
    EVT (0x3100); el modelo aplica SET y ACT a su propiedad. Nada de esto pasa por CamMgr."""
    assert _ins(0xAD58DA) == "movw r3, #0x7612"
    assert _ins(0xAD58DE) == "cmp r6, r3"
    assert _ins(0xAD58E0) == "beq.w #0xad7826"  # caso 0x7612 → secuencia «inteligente»
    assert _ins(0xAD58E4) == "adds r3, #2"  # 0x7614
    assert _ins(0xAD58E8) == "beq.w #0xad7852"  # caso 0x7614 → secuencia «precisión»
    assert _ins(0xAD7842) == "bl #0x956ebc"  # cuerpo de la secuencia inteligente
    assert _ins(0xAD786E) == "bl #0xa0d4b0"  # cuerpo de la secuencia de precisión
    # CMP: se envía con categoría 0x3130 al emisor (misma forma que EFCS, §10 de g22-respuesta-efcs-objcamera).
    assert _ins(0x956E14) == "movw r1, #0x3130"
    assert _ins(0x956E20) == "bl #0xa16042"
    assert _ins(0x956E2E) == "movw r2, #0x85b1"  # EVT difundido
    assert _ins(0x956E58) == "bl #0xa15f98"
    assert _ins(0xA0D424) == "movw r1, #0x3130"
    assert _ins(0xA0D430) == "bl #0xa16042"
    assert _ins(0xA0D43E) == "movw r2, #0x85b2"
    assert _ins(0xA0D468) == "bl #0xa15f98"
    # Modelo: sub-acción de la respuesta inteligente (0x4eafd4) y de la de precisión (0x4eae68).
    assert _ins(0x4EB00C) == "movw r3, #0x9799"  # SET inteligente
    assert _ins(0x4EB012) == "adds r3, #1"  # ACT inteligente = 0x979a
    assert _ins(0x4EAEA4) == "movw r3, #0x979d"  # SET precisión
    assert _ins(0x4EAEAA) == "adds r3, #2"  # ACT precisión = 0x979f
    assert _ins(0x4EAECA) == "movw r2, #0x979e"  # velocidad (RATE) de precisión
    assert _ins(0x4EAF0A) == "movw r2, #0x97a0"  # RATE_ACT


@pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin 3.21 ausente (analysis/rea-independent/input)")
def test_camgmr_no_tiene_ordenes_de_zoom() -> None:
    """§6: la tabla de despacho de CamMgr (cola 0x30001) solo tiene ids 0x3000–0x3036; 0x7612/0x7614
    NO son mensajes de CamMgr: son mensajes internos de libObj (MWF) a ObjCamera."""
    d = AVCAM.read_bytes()
    ids = []
    for k in range(CAMGMR_N):
        _h, mid, _sz, _nx = struct.unpack_from("<IIII", d, CAMGMR_TABLA + 16 * k)
        ids.append(mid)
    assert len(ids) == 203
    assert all(0x3000 <= i <= 0x30FF for i in ids), sorted(hex(i) for i in ids if not 0x3000 <= i <= 0x30FF)
    assert 0x3001 in ids and 0x3006 in ids  # los que ya emula el shim (CAMGREMU)
    assert not any(0x7000 <= i <= 0x7FFF for i in ids)
    assert 0x7612 not in ids and 0x7614 not in ids


def test_shim_emula_la_respuesta_de_objcamera_del_ajuste_de_zoom() -> None:
    """§7: el shim aplica el efecto de CMP+EVT (ranuras SET/ACT de la propiedad del modelo) cuando la
    respuesta de ObjCamera no llega; se engancha en el envío del modelo (libObj+0x4bcc54) y NOZOOM=1 lo apaga."""
    src = (ROOT / "scripts/gui/harness/shim/sonyshim.c").read_text()
    assert "(off & ~1UL) == 0x4bcc68" in src          # llamante = libObj+0x4bcc54 (mov r5,r0 = ModelCamera)
    assert "mid2 == 0x7612 || mid2 == 0x7614" in src  # solo las dos órdenes del ajuste
    assert "0x1480 + (mid2 == 0x7612 ? 0x34 : 0x38)" in src  # propiedades del modelo (modo inteligente / precisión)
    assert "0x4a58b2 + 1" in src and "0x4a5836 + 1" in src and "0x4a5914 + 1" in src  # get/set/sync reales
    assert 'getenv("NOZOOM")' in src
    assert "*a == 0xf247 && *(a + 1) == 0x6214 && *b == 0x4605" in src  # guardia de versión: bytes de 3.21
    # Diagnóstico que descartó que el fallo de la fila fuera de nombre de modelo (§8.2): prueba @M00B con la
    # misma lista y filtro de la vista. Solo registro; no cambia la respuesta.
    assert 'getenv("GMIPROBE3")' in src and 'r("@M00B", b, c, d)' in src


def test_el_modelo_despacha_las_acciones_0x63_y_0x64() -> None:
    """§3: las dos acciones del ajuste se piden por código en el despachador de `ModelCamera`
    (`0x63` = inteligente → `0x4bf230`, `0x64` = precisión → `0x4bf108`). Es lo que el arnés tendría que
    emitir para disparar el bloque «ZOOM» del shim (§7) cuando la fila se pueda abrir (§8)."""
    assert _ins(0x4CFD62) == "cmp r0, #0x63"
    assert _ins(0x4CFD64) == "beq.w #0x4d00d8"
    assert _ins(0x4D00D8) == "mov r0, r5"  # r0 = this (ModelCamera), r1 = ParamList de la acción
    assert _ins(0x4D00DC) == "bl #0x4bf230"  # orden inteligente
    assert _ins(0x4CFD68) == "cmp r0, #0x64"
    assert _ins(0x4CFD6E) == "b #0x4d00e2"
    assert _ins(0x4D00E2) == "mov r0, r5"
    assert _ins(0x4D00E6) == "bl #0x4bf108"  # orden de precisión


SCALAR = (ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/libScalarDaemon.so",
          ROOT / "analysis/camera-extract/usr/lib/libScalarDaemon.so")


def _scalar() -> Path:
    for p in SCALAR:
        if p.is_file():
            return p
    pytest.skip("libScalarDaemon.so 3.21 ausente (harness/stage o camera-extract)")


def test_tabla_paramid_tiene_los_ids_del_zoom() -> None:
    """§6: `libScalarDaemon.so` lleva el enum PARAMID completo (960 entradas `{nombre, id}` en el fichero
    `0x1b05a4`); el ajuste del menú es `PARAMID_BKUP_DIGITAL_ZOOM_SETTING = 0x2093` — el espacio *escalar*
    de ids, distinto del de `libObj` (`0x95xx`/`0x97xx`) para los mismos nombres."""
    from elftools.elf.elffile import ELFFile

    d = _scalar().read_bytes()
    with open(_scalar(), "rb") as f:
        secs = [(s.header.sh_addr, s.header.sh_offset, s.header.sh_size) for s in ELFFile(f).iter_sections()]

    def va2off(v: int) -> int | None:
        for a, o, sz in secs:
            if a <= v < a + sz:
                return o + (v - a)
        return None

    ids: dict[str, int] = {}
    entradas = 0
    for k in range(960):
        ptr, pid = struct.unpack_from("<II", d, 0x1B05A4 + 8 * k)
        o = va2off(ptr)
        assert o is not None
        ids[d[o : d.find(b"\0", o)].decode()] = pid
        entradas += 1
    assert entradas == 960  # el enum completo (5 nombres repetidos: 955 nombres distintos)
    assert ids["PARAMID_INVALID"] == 0  # primera entrada del enum
    assert ids["PARAMID_BKUP_DIGITAL_ZOOM_SETTING"] == 0x2093  # el ajuste del menú
    assert ids["PARAMID_BKUP_EZOOM_MODE"] == 0x2082  # modo de e-zoom (1 B en el Backup)
    assert ids["PARAMID_BKUP_EZOOM_SUPER_RESOLUTION_MODE"] == 0x2083
    assert ids["PARAMID_SYS_DATA_EZOOM_MODE_SET"] == 0x12A2  # datos del sistema: SET
    assert ids["PARAMID_SYS_DATA_EZOOM_MODE_ACT"] == 0x12A3  # …y ACT
    assert ids["PARAMID_CAMSETTING_EZOOM_MODE"] == 0x5002


def test_la_pagina_del_ajuste_es_una_vista_del_arnes() -> None:
    """§8.3: la fila se puede abrir por el atajo del arnés `POST /linea «O view/DIGITAL_ZOOM_SETTING»`
    (medido: id de vista `0x21` en `viewUnified4.so`, que pide `model/CAMERA` info `0x98`). Es un camino
    del ARNÉS, no de la cámara: sirve para saber qué pide la página, no para probar el ajuste."""
    vu2 = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/viewUnified2.so"
    uxc = ROOT / "analysis/gui/g22/harness/stage/cam/usr/share/app/viewDgtlZoomSetting.uxc"
    if not vu2.is_file():
        pytest.skip("viewUnified2.so 3.21 ausente (harness/stage)")
    d = vu2.read_bytes()
    assert b"view/DIGITAL_ZOOM_SETTING\0" in d  # el nombre que acepta openView (medido en caliente)
    assert b"viewDgtlZoomSetting.so\0" in d  # el plugin de la página
    assert b"cmnViewSettingNodeRootZoomSetting\0" in d  # el nodo del recurso
    assert uxc.is_file()
    assert b"Zoom" in uxc.read_bytes() or uxc.stat().st_size > 0
