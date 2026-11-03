"""Public Pages data must remain traceable to local documentation."""

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def test_public_session_index_has_real_sources(tmp_path: Path) -> None:
    out = tmp_path  # la salida va a un directorio temporal: la prueba no ensucia `site/` versionado
    subprocess.run([sys.executable, "scripts/build_pages_status.py", str(out)], cwd=ROOT, check=True)
    data = json.loads((out / "site/status.json").read_text(encoding="utf-8"))
    sessions = data["sessions"]
    ids = [int(item["id"][1:]) for item in sessions]

    assert ids == sorted(set(ids), reverse=True)
    assert data["documented_count"] == len(sessions)
    assert ids[0] >= 180
    assert data["latest"] == f"S{ids[0]}"
    assert {"S51", "S74", "S101", "S102", "S180"} <= {item["id"] for item in sessions}
    assert "Cancelada" in data["exceptions"]["S67"]["label"]
    executed = data["physical_tests"]["executed"]
    assert data["physical_tests"]["done"] == len(executed) >= 1
    assert set(executed) <= set(range(1, 25))  # P0 es respaldo, no plan
    assert data["physical_tests"]["total"] == 24
    coverage = data["module_coverage"]
    assert coverage["covered"] + coverage["pending"] + coverage["excluded"] == coverage["total"]
    assert coverage["excluded"] == 0  # [MODE_CAP*] (S632) y [D0]-[D7] (S636) pasaron a sub-etiqueta
    assert (out / "site/progress/index.html").read_bytes() == (out / "docs/progress/index.html").read_bytes()
    svg = (out / "site/progress/progress.svg").read_text(encoding="utf-8")
    assert svg.count("<rect") == 1 + coverage["total"] + data["latest_number"] + data["physical_tests"]["total"]
    badge = json.loads((out / "site/badge-modulos.json").read_text(encoding="utf-8"))
    assert badge["schemaVersion"] == 1 and f"{coverage['covered']}/{coverage['total']}" in badge["message"]

    page = (out / "site/progress/index.html").read_text(encoding="utf-8")
    assert page.count('class="cell m-') == coverage["total"]
    covered = sum(page.count(f'class="cell {k}"') for k in ("m-hito", "m-sub", "m-ver"))
    assert covered == coverage["covered"] and page.count('class="cell m-ver"') == coverage["verified"]
    assert page.count('class="cell m-rejected"') == coverage["excluded"]
    assert "más cadenas = más código" not in page
    assert "Cobertura documental" in page
    assert "Módulos decodificados" not in page
    assert "mando a distancia" in page  # nombre del hito S180 tomado del catálogo

    prefix = "/nicolvus/a6000-fw-decomp/blob/main/"
    for item in sessions:
        url = urlparse(item["source"])
        assert url.hostname == "github.com" and url.path.startswith(prefix)
        assert (ROOT / url.path.removeprefix(prefix)).is_file()


def test_real_progress_is_bounded_and_covers_documented_labels():
    from scripts.build_pages_status import ROOT as _root
    data = json.loads((_root / "site/status.json").read_text(encoding="utf-8"))
    rp, cov = data["real_progress"], data["module_coverage"]
    assert 0 <= float(rp["index"]) <= float(cov["percent"])
    assert len(rp["by_label"]) >= cov["covered"] - 1  # [OSD] cuenta como cubierta sin informe propio
