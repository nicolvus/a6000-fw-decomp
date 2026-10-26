"""tests/conftest.py: solo en CI y sin firmware, un fallo por archivo ausente se omite; en cualquier otro caso no."""
from pathlib import Path

import conftest


def test_skips_only_in_ci_without_firmware(monkeypatch, tmp_path):
    monkeypatch.setattr(conftest, "FIRMWARE", tmp_path / "av-cam.bin")
    monkeypatch.delenv("CI", raising=False)
    assert not conftest._skip_in_ci(Path(__file__), missing_file=True)
    monkeypatch.setenv("CI", "1")
    assert conftest._skip_in_ci(Path(__file__), missing_file=True)
    (tmp_path / "av-cam.bin").write_bytes(b"")
    assert not conftest._skip_in_ci(Path(__file__), missing_file=True)
