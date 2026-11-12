"""Prueba sin VM del núcleo de /dev/uipc compartido (G22-E T5b/T6)."""

import shutil
import subprocess
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "scripts/gui/harness/android"


@pytest.mark.skipif(not shutil.which("cc"), reason="sin compilador C")
def test_uipc_core(tmp_path: Path) -> None:
    exe = tmp_path / "t"
    subprocess.run(
        ["cc", "-std=c11", "-Wall", "-Werror", "-o", str(exe), str(SRC / "uipc_core.c"), str(SRC / "uipc_core_test.c")],
        check=True,
    )
    assert subprocess.run([str(exe)], capture_output=True, text=True, check=True).stdout.strip() == "uipc_core OK"
