"""G29: `pp_ram.sh` idempotente y con vigilancia del hueco (la cueva 0x43FB7400 leyó ceros con los ganchos presentes). Memoria falsa = fichero; offline."""
from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
import pp_color_patch as C
import pp_curves_patch as P

BASE_338 = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"
needs = pytest.mark.skipif(not (BASE_338.is_file() and P.A7S.is_file() and P.A6300.is_file() and C.PRESET_A6300.is_file()), reason="faltan imágenes")
LO, HI = P.SLOT0, C.CAVE + 0x100


@pytest.fixture(scope="module")
def datos():
    from g22 import patch_tristate
    base, _ = patch_tristate.apply_bytes(BASE_338.read_bytes())
    ps = P.patches(base, P.A7S.read_bytes(), P.A6300.read_bytes()) + C.patches(base, C.PRESET_A6300.read_bytes())
    sh, blob = P.camera_files(base, ps, None)
    return base, P.apply(base, ps), sh, blob


def entorno(tmp, base, sh, blob, mem=None):
    mem = mem or tmp / "mem"
    if not mem.exists():
        with mem.open("wb") as f:
            f.seek(P.BASE + P.PHYS)
            f.write(base)
    (tmp / "pp_ram.sh").write_text(sh)
    (tmp / "pp_curvas.bin").write_bytes(blob)
    (tmp / "uptime").write_text("123.45 99.0\n")
    env = {"PATH": "/usr/bin:/bin", "PP_MEM": str(mem), "PP_DATOS": str(tmp / "pp_curvas.bin"), "PP_LOG": str(tmp), "PP_BB": "env",
           "PP_UPTIME": str(tmp / "uptime"), "PP_PERIODO": "0.2", "PP_DDW": "conv=notrunc"}
    return mem, env


def leer(mem, a, n):
    with mem.open("rb") as f:
        f.seek(a + P.PHYS)
        return f.read(n)


def poner(mem, a, d):
    with mem.open("r+b") as f:
        f.seek(a + P.PHYS)
        f.write(d)


def correr(tmp, env, vueltas):
    return subprocess.run(["sh", str(tmp / "pp_ram.sh")], check=False, env={**env, "PP_VUELTAS": str(vueltas)}, capture_output=True, text=True, timeout=120)


@needs
def test_primera_ejecucion_y_repeticion_son_idempotentes(tmp_path, datos):
    base, nuevo, sh, blob = datos
    mem, env = entorno(tmp_path, base, sh, blob)
    r = correr(tmp_path, env, 1)
    assert "pp_ram: OK" in r.stdout and r.returncode == 0, r.stdout + r.stderr
    assert leer(mem, LO, HI - LO) == nuevo[LO - P.BASE:HI - P.BASE]
    r = correr(tmp_path, env, 1)          # segunda vez sobre memoria ya parcheada (reinicio de Linux sin recarga del núcleo)
    assert "pp_ram: OK" in r.stdout and "no es el original" not in r.stdout, r.stdout


@needs
def test_cueva_a_cero_con_ganchos_presentes_se_repara_al_relanzar(tmp_path, datos):
    base, nuevo, sh, blob = datos
    mem, env = entorno(tmp_path, base, sh, blob)
    correr(tmp_path, env, 1)
    poner(mem, C.CAVE, bytes(0x100))
    r = correr(tmp_path, env, 1)
    assert "pp_ram: OK" in r.stdout, r.stdout
    assert leer(mem, C.CAVE, 0x100) == nuevo[C.CAVE - P.BASE:][:0x100]


@needs
def test_vigilancia_detecta_repara_y_vuelca_el_hueco(tmp_path, datos):
    base, nuevo, sh, blob = datos
    mem, env = entorno(tmp_path, base, sh, blob)
    p = subprocess.Popen(["sh", str(tmp_path / "pp_ram.sh")], env={**env, "PP_VUELTAS": "12"}, stdout=subprocess.PIPE, text=True)
    out = []
    for linea in p.stdout:
        out.append(linea)
        if "pp_ram: OK" in linea:
            threading.Timer(0, poner, (mem, C.CAVE, bytes(0x100))).start()
    p.wait(timeout=120)
    txt = "".join(out)
    assert "hueco alterado a los 123 s" in txt and "hueco reparado" in txt, txt
    assert leer(mem, LO, HI - LO) == nuevo[LO - P.BASE:HI - P.BASE]
    vuelco = (tmp_path / "pp_hueco_1.bin").read_bytes()
    assert len(vuelco) > C.CAVE - LO + 0x80 and not any(vuelco[C.CAVE - LO:])   # el vuelco es el hueco ya alterado (cueva a cero)


@needs
def test_nucleo_distinto_no_escribe_nada(tmp_path, datos):
    base, _, sh, blob = datos
    mem, env = entorno(tmp_path, base, sh, blob)
    poner(mem, P.SLOT0 + 0x10, b"\xaa\xbb")           # curva ni original ni parcheada
    r = correr(tmp_path, env, 1)
    assert r.returncode == 1 and "av-cam distinto" in r.stdout
    assert leer(mem, C.CAVE, 0x100) == bytes(0x100)
