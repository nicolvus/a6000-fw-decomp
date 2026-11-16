"""E2E-1: el av-cam que carga el arnés sale del artefacto que se instalaría (nflasha3 / tar / .dat) y la VM arranca con él."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))
sys.path.insert(0, str(ROOT / "scripts/gui"))
F321 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3"
BASE_TAR = ROOT / "analysis/gui/g22/base-380.tar"
STOCK = ROOT / "analysis/rea-independent/input/av-cam.bin"
SHA321 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def test_extraccion_3_21_identica_al_av_cam_de_fabrica() -> None:
    if not F321.exists():
        pytest.skip("falta firmware/extracted/fw321 (no versionado)")
    fu = pytest.importorskip("avcam_fuente")
    img = fu.avcam_de(F321)
    assert fu.sha(img) == SHA321
    if STOCK.exists():
        assert img == STOCK.read_bytes()


@pytest.fixture(scope="module")
def av_parcheado(tmp_path_factory: pytest.TempPathFactory) -> Path:
    if not BASE_TAR.exists():
        pytest.skip("falta analysis/gui/g22/base-380.tar (no versionado)")
    import build_base_pp
    out = tmp_path_factory.mktemp("e2e1") / "base-pp.tar"
    build_base_pp.main(BASE_TAR, out)
    return out


def test_nflasha3_construido_da_otro_sha_y_vm_arranca(av_parcheado: Path, tmp_path: Path) -> None:
    fu = pytest.importorskip("avcam_fuente")
    p = pytest.importorskip("puente")
    if not p.L.LIRO_KO.exists():
        pytest.skip("falta liro.ko")
    img = fu.avcam_de(av_parcheado)  # tar completo → nflasha3 → av-cam
    assert fu.sha(img) != SHA321 and len(img) == len(STOCK.read_bytes() if STOCK.exists() else img)
    ruta = tmp_path / "av-cam.bin"
    ruta.write_bytes(img)
    vm, _ = p.arranca(ruta)
    assert vm.calls["CRE_TSK"] == 113 and any("[CAMERA_MAIN]: Liro Start" in x for x in vm.log)  # entry(pre)/entry(main) sin fallo
    assert not [x for x in vm.log if "ERROR" in x] and not [x for x in vm.tasks.values() if x.estado == "lista"]
    log = tmp_path / "avcam.jsonl"
    pu = p.Puente(lambda _b: None, log, None, ruta)
    primera = log.read_text().splitlines()[0]
    assert hashlib.sha256(img).hexdigest() in primera and '"arranque": "carga"' in primera and '"origen": "av-cam"' in primera
    assert pu.vm is not None


def test_salidas_de_ae_py_marcadas_como_sinteticas(tmp_path: Path) -> None:
    """E2E-7: lo que emite ae.py lleva origen «ae.py»; el tráfico de la LIRO VM, «av-cam»; el contenido enviado no cambia."""
    p = pytest.importorskip("puente")
    if not p.L.AVCAM.exists() or not p.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    import json
    enviado: list[bytes] = []
    log = tmp_path / "avcam.jsonl"
    pu = p.Puente(enviado.append, log, p.A.Emisor(None))
    pu._envia_ae(b"Q 20002 000000000000000000000000 aabb\n")
    filas = [json.loads(x) for x in log.read_text().splitlines()]
    assert enviado == [b"Q 20002 000000000000000000000000 aabb\n"]
    assert [f["origen"] for f in filas if f.get("tarea") == "ae.py"] == ["ae.py"]
    assert all(f["origen"] == "av-cam" for f in filas if f.get("tarea") != "ae.py")


def test_huella_cambia_con_el_av_cam(tmp_path: Path) -> None:
    sys.path.insert(0, str(ROOT / "scripts/gui/harness"))
    pytest.importorskip("live")
    import live
    assert live.huella(tmp_path, "", "x", "aa") != live.huella(tmp_path, "", "x", "bb") != live.huella(tmp_path, "", "x")
