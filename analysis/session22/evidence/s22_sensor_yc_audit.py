"""Auditor reproducible del límite estático sensor -> YC de S22.

No declara un productor: comprueba tanto las copias observadas como el hueco
que los informes anteriores documentan explícitamente.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
AV_CAM = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
PROBE = Path(__file__).with_name("s22-liro-producer-probe.json")
CONTRACT = ROOT / "analysis/encodestill-yc-contract.json"
S21 = ROOT / "docs/capture/s21-codex-exposure-to-library.md"


def function(probe: dict[str, Any], query: str) -> dict[str, Any]:
    for row in probe["functions"]:
        if row["query"] == query:
            return row
    raise AssertionError(f"falta consulta Ghidra {query}")


def require(text: str, token: str, scope: str) -> None:
    if token not in text:
        raise AssertionError(f"{scope}: falta {token!r}")


def main() -> None:
    probe = json.loads(PROBE.read_text())
    digest = hashlib.sha256(AV_CAM.read_bytes()).hexdigest()
    assert probe["firmware_profile"] == "ILCE-6000 3.21"
    assert probe["source_sha256"] == digest == (
        "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
    )

    notify = str(function(probe, "437efe78")["pseudo_code"])
    for token in ("FUN_43afe932", "0x28c", "FUN_437feef8", "0x2a8", "0x4b54", "0x4b58", "0x4b5c"):
        require(notify, token, "Stage_Notify")
    require(str(function(probe, "43afe932")["pseudo_code"]), "0x28c", "copiador")
    require(str(function(probe, "43b1bdb4")["pseudo_code"]), "FUN_437f7ff0", "fila LIRO 0x78")

    contract = json.loads(CONTRACT.read_text())
    assert contract["mensaje_entrada_execute"]["grupos"]["0x1017"]["0x1018"].startswith("struct 12 B")
    assert "formato de pixel" in contract["no_hay_validacion_de"]
    assert "stride/pitch" in contract["no_hay_validacion_de"]

    s21 = S21.read_text()
    require(s21, "No se recuperó aquí el callback de última línea/DMA", "límite S21")
    require(s21, "NO_VERIFICADO (producción y fin DMA)", "límite S21")
    print("PASS: serialización LIRO y precontrato EncodeStill verificados; productor sensor/DMA permanece NO_VERIFICADO")


if __name__ == "__main__":
    main()
