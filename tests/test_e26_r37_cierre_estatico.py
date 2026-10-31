"""E26-R37 — cierre estático tras R36: entrada al actualizador, paquete 3.26, consola UART y Darwin al encender.

Leen binarios y paquetes locales no versionados; se omiten si faltan.  Comprueban bytes, no la cámara.
"""

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "analysis" / "e26-recovery")]

BL = ROOT / "analysis/camera-dumps/updater-20261020-175427/bootloader.bin"
DARWIN = (
    ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)
DARWIN_325 = ROOT / "analysis/e25-27/artifacts/darwin_core.integrated.bin"
REC324 = ROOT / "analysis/darwin-patch/fdat/recuperacion-324"
L3, L2 = 0xC01F0000, 0xC0030000


def _need(*paths: Path) -> None:
    for p in paths:
        if not p.exists():
            pytest.skip(f"falta {p.relative_to(ROOT)} (no versionado)")


def _l3() -> bytes:
    return BL.read_bytes()[0x22800:0x38000]


def _h(data: bytes, base: int, addr: int, n: int) -> str:
    return data[addr - base : addr - base + n].hex()


def test_a_modo_3_solo_con_updater_mode_y_carga_de_nflasha1():
    _need(BL)
    d = _l3()
    # c01f1e10: bl chk_updater; cbz r0 -> sigue; movs r0,#3; b fijar_modo
    assert _h(d, L3, 0xC01F1E14, 4) == "08b10320"
    # tabla tbb de c01f1312: modo 3 -> c01f1334 (bl c01f1378, UPDATER); el resto de 1..12 -> Normal load o error
    table = d[0xC01F1320 - L3 : 0xC01F1320 - L3 + 13]
    targets = {m: 0xC01F1320 + 2 * b for m, b in enumerate(table)}
    assert targets[3] == 0xC01F1334 and all(
        targets[m] == 0xC01F132E for m in (1, 2, 4, 5, 6, 10, 11, 12)
    )
    # c01f068a monta el dispositivo 1 (movs r0,#1; bl fat_mount)
    assert _h(d, L3, 0xC01F0696, 2) == "0120"
    # \updater\mode y \boot\loadaddr.txt están donde los usa el código
    assert d[0xC01F19A4 - L3 :].startswith(b"\\updater\\mode\0")
    assert d[0xC01F092C - L3 :].startswith(b"\\boot\\loadaddr.txt\0")


def test_c_consola_uart_depende_de_backup_510015_en_loader2_y_loader3():
    _need(BL)
    raw = BL.read_bytes()
    d3, d2 = _l3(), raw[0x600:0x7200]
    lit = struct.pack("<I", 0x510015)
    assert lit in d3 and lit in d2
    # Loader3 c01f4edc: lee 0x510015 y solo devuelve 1 si vale 1
    assert struct.unpack_from("<I", d3, 0xC01F4F50 - L3)[0] == 0x510015


def test_c_backup_historico_desactiva_la_consola():
    from r14_backup import BK4

    dumps = sorted(ROOT.glob("analysis/camera-dumps/**/backup_flash.bin"))
    if not dumps:
        pytest.skip("sin volcados BK4")
    assert {BK4.load(p).read(0x510015) for p in dumps} == {b"\x00"}


def test_d_selector_de_darwin_se_pone_a_cero_al_reiniciar_y_sus_irq_no_se_habilitan():
    _need(DARWIN, DARWIN_325)
    o, n, base = DARWIN.read_bytes(), DARWIN_325.read_bytes(), 0x4200
    a, b = struct.unpack_from("<ii", o, 0x4430 - base)
    regions = [
        struct.unpack_from("<IIII", o, off - base)
        for off in range(0x4430 + a, 0x4430 + b, 16)
    ]
    zero_init = [(dst, size) for _src, dst, size, fn in regions if fn == 0x4494]
    assert any(dst <= 0x20003716 < dst + size for dst, size in zero_init)
    # cueva: ldr r2,=S+0x3e; ldrb; cbz -> b.w 0x1b080; si no, devuelve 0
    assert struct.unpack_from("<I", n, 0x4330 - base)[0] == 0x20003716
    # vectores 70–73 y 76 eran cero en Sony y ninguna escritura alcanza NVIC ISER1 (IRQ 32–63)
    assert [k for k in range(80) if struct.unpack_from("<I", o, 4 * k)[0] == 0] == [
        70,
        71,
        72,
        73,
        76,
    ]
    assert struct.pack("<I", 0xE000E104) not in o


def test_b_paquete_326_solo_cambia_version_y_sumas():
    _need(REC324 / "firmware_packed.dat", REC324 / "firmware_packed.fdat")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_326", ROOT / "scripts/e26_recovery/build_326.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from e25_06 import audit_packages as A

    dat, fdat = (
        (REC324 / "firmware_packed.dat").read_bytes(),
        (REC324 / "firmware_packed.fdat").read_bytes(),
    )
    keys = A.load_keys()
    new_dat, new_fdat = mod.bump(dat, fdat, 0x26, keys)
    assert all(mod.verify(new_dat, new_fdat, keys, "3.26").values())
    assert [i for i in range(1024) if fdat[i] != new_fdat[i]] == [8, 9, 10, 11, 32]
    assert len(A.diff_ranges(dat, new_dat)) == 3
