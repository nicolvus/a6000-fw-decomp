"""G23: menú Gamma PP — CautionConfig.so parcheado (listas, `NumOf`, array de hijos y sus relocaciones) y ranuras de texto (offline)."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import build_pp_gamma_menu as B

DEV = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
LIB = DEV / "lib/CautionConfig.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="CautionConfig.so de Sony ausente")
IDS = {k: 0xF000 + i for i, k in enumerate(B.TEXTOS)}


def _symbols(path):
    out = subprocess.run(["nm", "-D", "-S", str(path)], capture_output=True, text=True, check=True).stdout
    return {f[3]: (int(f[0], 16), int(f[1], 16)) for f in (l.split() for l in out.splitlines()) if len(f) == 4}


@needs
def test_array_de_hijos_nuevo_apunta_a_los_siete_nodos(tmp_path):
    new, _ = B.patch_caution(LIB.read_bytes(), IDS)
    p = tmp_path / "c.so"
    p.write_bytes(new)
    s = _symbols(p)
    segs = A._segments(new)
    _, dyn = A._dynamic(new, segs)
    t = {k: v for k, v in dyn if k}
    arr, size = s["cmnViewSettingNodesAfIlluminatorDefault"]
    assert size == 4 * len(B.OPCIONES) and struct.unpack_from("<I", new, A._off(segs, s["cmnViewSettingNodesNumOfAfIlluminatorDefault"][0]))[0] == 7
    o = A._off(segs, t[0x11])
    rels = {struct.unpack_from("<I", new, o + i)[0]: struct.unpack_from("<I", new, o + i + 4)[0] for i in range(0, t[0x12], 8)}
    symtab, strtab = A._off(segs, t[6]), A._off(segs, t[5])
    for i, (nodo, _) in enumerate(B.OPCIONES):
        info = rels[arr + 4 * i]
        assert info & 0xFF == A.R_ARM_ABS32
        so = struct.unpack_from("<I", new, symtab + 16 * (info >> 8))[0]
        name = new[A._off(segs, t[5]) + so:].split(b"\0")[0].decode()
        assert name == f"cmnViewSettingNode{nodo}"


@needs
def test_listas_editadas_en_sitio_conservan_tamano(tmp_path):
    new, _ = B.patch_caution(LIB.read_bytes(), IDS)
    p = tmp_path / "c.so"
    p.write_bytes(new)
    s, segs = _symbols(p), A._segments(new)
    root = s["cmnViewSettingPropertyListAfIlluminatorRoot"]
    assert root[1] == 60 and struct.unpack_from("<15I", new, A._off(segs, root[0]))[-3:] == (0xE, 1, B.PID)
    gamma = A._off(segs, s["cmnViewSettingPropertyListAfTrackingSpeed1"][0])
    assert struct.unpack_from("<18I", new, gamma)[12:] == (0xF, 1, 6, 0x10, 1, 6)        # Cine4 = opción 6
    assert len(set(B.pp_gamma_descriptor.GAMMAS)) == len(B.OPCIONES) == 7


@needs
def test_carpeta_pagina_ajuste_es_una_cadena_de_nodos_de_datos(tmp_path):
    new, delta = B.patch_caution(LIB.read_bytes(), IDS)
    p = tmp_path / "c.so"
    p.write_bytes(new)
    s, segs = _symbols(p), A._segments(new)
    rd = lambda va, n=1: struct.unpack_from(f"<{n}I", new, A._off(segs, va))
    carpeta = s["cmnViewSettingNodeRootAelWShutter"][0] + delta
    vt, kids, n, props = rd(carpeta, 4)
    assert vt == s["_ZTV18CmnViewSettingNode"][0] + 8 and n == len(B.PAGINAS_PP) == 1
    assert rd(props, 2)[1] == 4 and rd(rd(props)[0] + 12 * 2, 3) == (0xB, 1, 0)             # etiqueta, ayuda, 0xb=0, 0xc=3 (como CustomLensComp)
    pagina = rd(kids)[0]
    assert rd(pagina + 8)[0] == 1 and rd(rd(pagina + 4)[0])[0] == s["cmnViewSettingNodeRootAfIlluminator"][0]
    assert rd(rd(rd(carpeta + 12)[0])[0] + 12 * 3, 3) == (0xC, 1, 3)
