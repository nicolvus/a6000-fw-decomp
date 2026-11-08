"""G10 — `build_nflasha15.replace_files` conserva modo, uid y gid del fichero de Sony (3.39/3.40 dejaban 0644)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
pytestmark = pytest.mark.skipif(not (shutil.which("mke2fs") and shutil.which("debugfs")), reason="e2fsprogs no disponible")


def _stat(image: Path, path: str) -> str:
    return subprocess.run(["debugfs", "-R", f"stat {path}", str(image)], capture_output=True, text=True, check=True).stdout


def test_replace_files_conserva_modo(tmp_path: Path) -> None:
    import build_nflasha15

    image = tmp_path / "usr.ext2"
    subprocess.run(["mke2fs", "-q", "-t", "ext2", "-b", "1024", str(image), "512"], check=True)
    original = tmp_path / "orig.so"
    original.write_bytes(b"sony")
    script = tmp_path / "seed.dbg"
    script.write_text(f"mkdir lib\nwrite {original} lib/x.so\nset_inode_field lib/x.so mode 0100555\n"
                      "set_inode_field lib/x.so uid 57285\nset_inode_field lib/x.so gid 1000\n")
    subprocess.run(["debugfs", "-w", "-f", str(script), str(image)], capture_output=True, check=True)
    package = tmp_path / "pkg"
    (package / "lib").mkdir(parents=True)
    (package / "lib/x.so").write_bytes(b"parcheado")  # 0644 en el host, como en el paquete real

    build_nflasha15.replace_files(image, package, ["lib/x.so"])

    attrs = build_nflasha15.stat_fields(image, "/lib/x.so")
    assert (attrs["mode"], attrs["uid"], attrs["gid"]) == (0o555, 57285, 1000), _stat(image, "/lib/x.so")
