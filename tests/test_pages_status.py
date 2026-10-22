"""Public Pages data must remain traceable to local documentation."""

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def test_public_session_index_has_real_sources() -> None:
    subprocess.run([sys.executable, "scripts/build_pages_status.py"], cwd=ROOT, check=True)
    data = json.loads((ROOT / "site/status.json").read_text(encoding="utf-8"))
    sessions = data["sessions"]
    ids = [int(item["id"][1:]) for item in sessions]

    assert ids == sorted(set(ids), reverse=True)
    assert data["documented_count"] == len(sessions)
    assert data["latest"] == "S102"
    assert {"S51", "S74", "S101", "S102"} <= {item["id"] for item in sessions}
    assert "Cancelada" in data["exceptions"]["S67"]["label"]
    assert data["physical_tests"]["done"] == 0
    assert data["physical_tests"]["total"] == 8

    prefix = "/nicolvus/a6000-fw-decomp/blob/main/"
    for item in sessions:
        url = urlparse(item["source"])
        assert url.hostname == "github.com" and url.path.startswith(prefix)
        assert (ROOT / url.path.removeprefix(prefix)).is_file()
