"""Núcleo del Eye AF de cámara (Java puro): compilación y pruebas estáticas.

Compila `tools/eye-af/camera/src/eyeaf/{AfPoint,AfTracker,WebApiMsg,SelfTest}.java` **sin
`android.jar`** (si compila, el núcleo no depende de Android) y ejecuta sus comprobaciones.
Se omite si no hay `javac` en la máquina.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "eye-af" / "camera" / "src" / "eyeaf"
CORE = ["AfPoint.java", "AfTracker.java", "WebApiMsg.java", "SelfTest.java"]


def _javac() -> str | None:
    candidatos = [
        os.environ.get("JAVA_HOME", "") and Path(os.environ["JAVA_HOME"]) / "bin" / "javac",
        Path.home() / ".local" / "jdk17" / "bin" / "javac",
        Path.home() / ".local" / "android-build",
    ]
    for c in candidatos:
        if c and Path(c).is_file():
            return str(c)
    if shutil.which("javac"):
        return "javac"
    for d in sorted((Path.home() / ".local").glob("jdk*/bin/javac")):
        return str(d)
    return None


@pytest.fixture(scope="module")
def compilado(tmp_path_factory):
    javac = _javac()
    if not javac:
        pytest.skip("no hay javac en esta máquina (instala un JDK 17 para estas pruebas)")
    out = tmp_path_factory.mktemp("eyeaf-core")
    srcs = [str(SRC / f) for f in CORE]
    r = subprocess.run([javac, "-d", str(out)] + srcs, check=False, capture_output=True, text=True)
    assert r.returncode == 0, f"javac falló:\n{r.stderr}"
    return Path(javac), out


def test_nucleo_compila_sin_android(compilado):
    _javac, out = compilado
    clases = sorted(p.name for p in out.glob("eyeaf/*.class"))
    assert "AfPoint.class" in clases and "AfTracker.class" in clases and "WebApiMsg.class" in clases
    # el núcleo no puede haber necesitado android.jar: se compiló sin él y no lo importa
    for f in CORE:
        texto = (SRC / f).read_text(encoding="utf-8")
        assert "import android" not in texto, f"{f} importa Android y debería ser Java puro"


def test_autopruebas_del_nucleo_pasan(compilado):
    javac, out = compilado
    java = str(Path(javac).with_name("java"))
    r = subprocess.run([java, "-cp", str(out), "eyeaf.SelfTest"], check=False, capture_output=True, text=True)
    assert r.returncode == 0, f"las autopruebas fallaron:\n{r.stdout}\n{r.stderr}"
    assert "0 fallos" in r.stdout, r.stdout
    # 32 comprobaciones: si se añaden o quitan, actualizar aquí a propósito
    assert "32 comprobaciones" in r.stdout, r.stdout


def test_constantes_del_protocolo_coinciden_con_el_re():
    """Las constantes del mensaje son las verificadas en orb-server fw3.21."""
    w = (SRC / "WebApiMsg.java").read_text(encoding="utf-8")
    for esperado in ("SIZE = 1568", "OFF_MSGID = 0x00", "OFF_PARAMID = 0x08",
                     "OFF_PAYLOAD = 0x10", "MSGID_SET_TOUCH_AF = 0x192",
                     "PARAMID_SET_TOUCH_AF = 0x8d", "MSGID_CANCEL_TOUCH_AF = 0x195",
                     "PARAMID_CANCEL_TOUCH_AF = 0x90"):
        assert esperado in w, f"falta {esperado} en WebApiMsg.java"
    p = (SRC / "AfPoint.java").read_text(encoding="utf-8")
    assert "MAX_PERCENT = 100.0" in p, "el rango verificado es 0..100"
