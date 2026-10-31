"""E26-R38 — guard de versión del actualizador de `nflasha1`, escritura de `dat4`/`comp` y entrada mínima `\\updater\\mode`.

Leen el volcado histórico de NAND (2026-10-20) y el cuerpo del actualizador 3.21 (no versionados); se
omiten si faltan.  Comprueban bytes e imágenes locales, no la cámara.
"""

import hashlib
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "references/fwtool"), str(ROOT / "scripts/e26_recovery")]

NAND = ROOT / "analysis/camera-dumps/nand-20261020"
BODY = ROOT / "firmware/extracted/fw321/updater.img_unpacked"
SAUU_SHA = "799a94d6e03313b80ef901cc268892ea8004dbc01274b493738dc3fff70f1858"


def _need(*paths: Path) -> None:
    for p in paths:
        if not p.exists():
            pytest.skip(f"falta {p.relative_to(ROOT)} (no versionado)")


def _fat(path: Path) -> dict[str, bytes]:
    from fwtool.archive.fat import readFat  # type: ignore[import-not-found]

    return {
        f.path: f.contents.read()
        for f in readFat(io.BytesIO(path.read_bytes()))
        if f.contents
    }


def _initrd() -> dict[str, bytes]:
    from fwtool.archive.cramfs import readCramfs  # type: ignore[import-not-found]

    _need(NAND / "dev_nflasha1.bin")
    img = _fat(NAND / "dev_nflasha1.bin")["/boot/initrd.img"]
    return {
        f.path: f.contents.read() for f in readCramfs(io.BytesIO(img)) if f.contents
    }


@pytest.fixture(scope="module")
def initrd() -> dict[str, bytes]:
    return _initrd()


def _at(elf: bytes, va: int, n: int, base: int = 0x8000) -> str:
    return elf[va - base : va - base + n].hex()


def test_sauu_guard_estricto_salvo_minor_y_verskip(initrd):
    sauu = initrd["/usr/bin/sauu"]
    assert hashlib.sha256(sauu).hexdigest() == SAUU_SHA
    # UpdaterHandler(arg): "-m" -> [this+0x14]=1 ; "-s" -> [this+0x15]=1
    assert sauu[0x1704A - 0x8000 :].startswith(b"-m\0-s\0")
    assert (
        _at(sauu, 0xD1A8, 6) == "10b901232375"
        and _at(sauu, 0xD1B8, 6) == "08b901236375"
    )
    # isVersionOK: +0x15 -> acepta; mayor nueva < actual -> rechaza; igual -> +0x14 o firmware actual no válido
    assert (
        _at(sauu, 0xD3E2, 30)
        == "707d002831d1aa696b689a422ed32cd1ea69ab689a4229d327d1347d2cbb"
    )
    # la versión actual sale de <nflasha2>/updater/dat4 y la validez de updater/comp
    common = initrd["/usr/lib/libupdatercommon.so"]
    assert b"updater/dat4\0" in common and b"updater/comp\0" in common
    ufp = initrd["/usr/bin/execute_ufp.sh"].decode()
    assert (
        "sauu -s" in ufp and "sauu -m" in ufp and "rm -rf /setting/updater/mode*" in ufp
    )


def test_el_actualizador_se_apaga_a_los_30_min(initrd):
    tmo = initrd["/usr/bin/ud_timeout_poweroff.elf"]
    assert (
        _at(tmo, 0x86F8, 10) == "4ff4e16000affff7a8ef"
    )  # mov.w r0,#1800; ...; blx sleep


def test_complete_update_escribe_version_del_fdat_y_borra_mode():
    lib = BODY / "bodylib/libupdaterbody.so"
    _need(lib)
    b = lib.read_bytes()
    # setVersion(info.major << 8 | info.minor) por la vtable (+0x1c)
    assert b[0x152A8:0x152B8].hex() == "2b6828467168b268db6942ea01219847"
    # el paquete 3.2x no trae updater_sum ni loader_sum: nunca reescribe nflasha1
    config = (BODY / "config/config.xml").read_text()
    assert "updater_sum" in config and "loader_sum" in config
    tar = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked"
    _need(tar)
    assert not [p for p in tar.iterdir() if "updater" in p.name or "loader" in p.name]


def test_nflasha2_historico_dat4_comp_y_mode_borrado():
    _need(NAND / "dev_nflasha2.bin")
    import updater_mode_entry as U

    img = (NAND / "dev_nflasha2.bin").read_bytes()
    files = _fat(NAND / "dev_nflasha2.bin")
    assert files["/updater/dat4"] == b"\x21\x03" and files["/updater/comp"] == b""
    assert not U.loader3_finds_mode(img)
    out, changes = U.add_mode(img)
    assert U.loader3_finds_mode(out)
    # entrada MODE borrada (0xE5) recuperada con un solo byte en el sector 132 de nflasha2
    assert changes == [
        {"offset": 0x108A0, "sector": 132, "antes": 0xE5, "despues": 0x4D}
    ]
    assert "/updater/MODE" in _fat_paths(out)


def _fat_paths(img: bytes) -> set[str]:
    from fwtool.archive.fat import readFat  # type: ignore[import-not-found]

    return {f.path for f in readFat(io.BytesIO(img))}


def test_add_mode_usa_hueco_libre_y_rechaza_duplicado():
    import updater_mode_entry as U

    _need(NAND / "dev_nflasha2.bin")
    img = bytearray((NAND / "dev_nflasha2.bin").read_bytes())
    off, _ = U.updater_dir(bytes(img))
    img[off + 4 * 32 : off + 6 * 32] = img[
        off + 6 * 32 : off + 8 * 32
    ]  # quita el MODE borrado
    img[off + 6 * 32 : off + 8 * 32] = bytes(64)
    out, changes = U.add_mode(bytes(img))
    assert U.loader3_finds_mode(out) and {c["offset"] // 32 * 32 for c in changes} == {
        off + 6 * 32
    }
    with pytest.raises(ValueError):
        U.add_mode(out)
