"""Tests S108 — módulo [CAMERA_SA] (231 trazas)."""
import pytest

BASE_VADDR = 0x43541000
AV_CAM_PATH = "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin"


def _read_and_extract():
    data = open(AV_CAM_PATH, "rb").read()
    pattern = b"[CAMERA_SA]"
    pos = 0
    vaddr_to_text = {}
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        fo = pos
        vaddr = BASE_VADDR + fo
        end = pos
        while end < len(data) and data[end:end+1] != b"\x00" and (end - pos) < 200:
            end += 1
        text = data[pos:end].decode("latin-1", errors="replace")
        if vaddr not in vaddr_to_text:
            vaddr_to_text[vaddr] = text
        pos += 1
    return vaddr_to_text


@pytest.fixture(scope="session")
def vaddr_to_text():
    return _read_and_extract()


def test_s108_total_count(vaddr_to_text):
    assert len(vaddr_to_text) == 231


def test_s108_vaddr_range(vaddr_to_text):
    MIN_V = 0x43cc5286
    MAX_V = 0x43cef0d8
    for vaddr in vaddr_to_text:
        assert MIN_V <= vaddr <= MAX_V


def test_s108_all_have_prefix(vaddr_to_text):
    for vaddr, text in vaddr_to_text.items():
        assert text.startswith("[CAMERA_SA]:")


def test_key_vaddrs(vaddr_to_text):
    # Verify key vaddrs have expected content (case-insensitive substring checks)
    t = vaddr_to_text[0x43cc5286]
    assert "open error" in t.lower()
    t = vaddr_to_text[0x43cc529f]
    assert "close error" in t.lower()
    t = vaddr_to_text[0x43cebde1]
    assert "hw open err" in t.lower()
    t = vaddr_to_text[0x43cedae3]
    assert "rawhsize" in t.lower()
    t = vaddr_to_text[0x43ced103]
    assert "sp_cnt is over 4095" in t.lower()
    t = vaddr_to_text[0x43ced44e]
    assert "sa_funcdrv_e_osal" in t.lower()
