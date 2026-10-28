"""E25-11 — bytes de av-cam.bin (fw 3.21) en los que se apoya el análisis offline de r5 y ShutMode (docs/capture/e25-11-r5-bionz-analisis.md).
Se omite si el firmware no está disponible (no se versiona)."""
from pathlib import Path

import pytest

FW = Path(__file__).resolve().parents[1] / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
pytestmark = pytest.mark.skipif(not FW.exists(), reason="firmware no versionado")


def at(addr: int, n: int) -> str:
    with FW.open("rb") as f:
        f.seek(addr - BASE)
        return f.read(n).hex()


@pytest.mark.parametrize("addr,expected", [
    (0x436D6FAA, "8e88bc4b0d88cf88"),   # SetExposure IMX210: r6=h[1,#4]... r5=h[r1], r7=h[r1,#6], fp=uxtb r6
    (0x436D6FB6, "91f80990"),           # ldrb.w sb,[r1,#9]  (ShutMode = param+9)
    (0x436D7000, "28125ffa85fe"),       # asrs r0,r5,#8; uxtb.w lr,r5  (r5 = param+0)
    (0x438C82AC, "022803d0"),           # cmp r0,#2; beq 0x438c82b8   (clasificador de modo)
    (0x438C82B4, "03280bd1"),           # cmp r0,#3; bne 0x438c82d0
    (0x438C82B8, "00230221"),           # movs r3,#0; movs r1,#2      (ShutMode 0, r5=2)
    (0x438C82BC, "84f85536a4f85036c4f84c16a4f8523684f85436"),  # strb 0x655; strh 0x650; str 0x64c; strh 0x652; strb 0x654
    (0x43A12C64, "0f4b7b441b68bc2b"),   # clasificador: ldr r3,[global]; cmp r3,#0xbc
    (0x438CC868, "e5f6a6ff"),           # único llamador del constructor del parámetro LV 0x437b27b8
])
def test_bytes(addr, expected):
    assert at(addr, len(expected) // 2) == expected


def test_tv_a_tiempo_emulado():
    """0x4382fac8(x) = 1e6·2^((4096−x)/256) µs y 0x4382fa94 = lo mismo ×256 (−1 si x ≤ 0xC00); verificado por emulación."""
    pytest.importorskip("unicorn")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import e25_11_tv_emu as E

    mu = E.emulator()
    assert E.call(mu, 0x4382FA94, 0xC00) == 0xFFFFFFFF
    for x in (0xE00, 0x1000, 0x1200, 0x1400, 0x17F6):
        us = E.call(mu, 0x4382FAC8, x)
        assert abs(us - 1e6 * 2 ** ((4096 - x) / 256)) <= 1
        assert abs(E.call(mu, 0x4382FA94, x) - 256 * us) <= 256
