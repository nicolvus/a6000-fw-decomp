"""Contrastar stubs ARM y veneers Thumb con sus relocaciones GOT reales."""

import json
from pathlib import Path

from analysis.s380_libobj_map.elf_plt import resolve_plt
from scripts.elf_string_xrefs import sections

ROOT = Path(__file__).resolve().parents[1]


def test_resolve_libobj_plt_from_got_relocations():
    data = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so").read_bytes()
    report = json.loads((ROOT / "analysis/s380_libobj_map/map.json").read_text())
    got = {int(k, 16): v for k, v in report.get("got_map", report["plt_map"]).items()}
    section = sections(data)[".plt"]
    entries = resolve_plt(data, section[3], section[4], section[5], got)
    assert entries[0xdb3dc] == got[0x102cbdc]
    assert entries[0xdb3d8] == entries[0xdb3dc]  # bx pc; nop -> cuerpo ARM
    assert len(entries) == 2811  # 2420 cuerpos + 391 entradas Thumb
    assert all(section[3] <= address < section[3] + section[5] for address in entries)
