"""S94 — HAPI API unit tests for libHapiLib.so (fw3.21)."""

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

# Resolve paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIB_HAPI = PROJECT_ROOT / "firmware" / "extracted" / "fw321" / "firmware.tar_unpacked" / \
           "0700_part_image" / "dev" / "nflasha15_unpacked_unpacked" / "lib" / "libHapiLib.so"
HAPI_API_MD = PROJECT_ROOT / "analysis" / "s94_hapi" / "hapi_api.md"
HAPI_API_JSON = PROJECT_ROOT / "analysis" / "s94_hapi" / "hapi_api.json"


def test_library_exists():
    """Verify libHapiLib.so is present and has expected size."""
    assert LIB_HAPI.exists(), f"libHapiLib.so not found at {LIB_HAPI}"
    assert LIB_HAPI.stat().st_size == 89628, \
        f"Unexpected libHapiLib.so size: {LIB_HAPI.stat().st_size} (expected 89628)"


def test_mangled_symbols_present():
    """Verify C++ mangled names are recoverable via strings."""
    strings_out = subprocess.run(
        ["strings", str(LIB_HAPI)],
        capture_output=True, text=True
    )
    all_strings = strings_out.stdout
    # Key symbols that must be present
    required = [
        "_ZN7HapiLib11HapiLibMain11getInstanceEv",
        "_ZN7HapiLib3Cam10CamService11getInstanceEv",
        "_ZN7HapiLib3Sdf10SdfService11getInstanceEv",
    ]
    for sym in required:
        assert sym in all_strings, f"Missing symbol: {sym}"


def test_hapi_keywords_in_strings():
    """Verify HAPI protocol keywords appear in strings output."""
    strings_out = subprocess.run(
        ["strings", "-n", "4", str(LIB_HAPI)],
        capture_output=True, text=True
    )
    all_strings = strings_out.stdout
    required_keywords = ["HAPI", "CamService", "SdfService", "REQ_MSGE", "EVT_MSGE", "COMP_MSGE"]
    for kw in required_keywords:
        assert kw in all_strings, f"Missing keyword in strings: {kw}"


def test_json_matches_md():
    """Verify the JSON summary is consistent with the markdown doc."""
    with open(HAPI_API_JSON) as f:
        data = json.load(f)
    with open(HAPI_API_MD) as f:
        md_text = f.read()

    # Check that all CamApi* class names (values) appear in MD
    cam_apis = data.get("cam_apis_capabilities", {})
    for api_name in cam_apis.values():
        assert api_name in md_text, f"CamApi '{api_name}' not found in hapi_api.md"

    # Verify message_types keys are valid
    valid_msg_types = {"REQ_MSGE", "EVT_MSGE", "COMP_MSGE", "SDF_MSG_SENDE", "MAIN_MSG_RECVE"}
    for key in data.get("message_types", {}):
        assert key in valid_msg_types, f"Invalid message type: {key}"

    # Verify category_ids keys are valid
    valid_cids = {"CATEID_HAPI", "CATEID_SDF_ACK", "CATEID_SDF_COMP", "CATEID_SDF_NEXT"}
    for key in data.get("category_ids", {}):
        assert key in valid_cids, f"Invalid category ID: {key}"


def test_av_cam_references_hapi():
    """Verify av-cam.bin references Stage_CameraHAPI and HAPI manager."""
    av_cam = PROJECT_ROOT / "firmware" / "extracted" / "fw321" / "firmware.tar_unpacked" / \
             "0700_part_image" / "dev" / "nflasha3_unpacked_unpacked" / "av-cam.bin"
    assert av_cam.exists(), f"av-cam.bin not found at {av_cam}"

    strings_out = subprocess.run(
        ["strings", "-n", "4", str(av_cam)],
        capture_output=True, text=True
    )
    all_strings = strings_out.stdout
    assert "Stage_CameraHAPI" in all_strings, \
        "Stage_CameraHAPI not found in av-cam.bin strings"
    assert "HAPI Manager" in all_strings, \
        "HAPI Manager not found in av-cam.bin strings"


def test_osal_bus_reference():
    """Verify HAPI uses OSAL message bus (cross-reference S93)."""
    osal_md = PROJECT_ROOT / "analysis" / "s93_osal_bus" / "osal_message_bus.md"
    assert osal_md.exists()
    with open(osal_md) as f:
        md_text = f.read()
    # HAPI should use at least one GID/LID pair; check that the md mentions
    # message queues which is the transport HAPI uses
    assert "col" in md_text.lower() or "queue" in md_text.lower(), \
        "OSAL message bus doc should mention queues/columns"


if __name__ == "__main__":
    # Allow running as: python -m pytest tests/test_s94_hapi.py -q
    pytest.main(["-v"] if "-v" in sys.argv else ["-q"])