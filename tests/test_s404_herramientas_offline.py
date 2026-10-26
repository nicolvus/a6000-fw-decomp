"""C7: herramientas fuera de línea de `scripts/` con ELF/volcados sintéticos (sin firmware ni cámara)."""
import ast
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE, OFF = 0x43541000, 0x1F0  # thumb_callers: base de carga y desplazamiento del ELF de análisis av-cam


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_elf(secs: list[tuple[str, int, bytes]]) -> bytes:
    """ELF32 ARM mínimo con VA == offset: la sección k vive en 0x100·(k+1) (cada una ≤ 0x100 B); `secs` = (nombre, tipo, datos)."""
    names, body, hdrs, pos = b"\0", b"", [(0,) * 10], 0x100
    for name, typ, data in secs + [(".shstrtab", 3, b"")]:
        n = len(names)
        names += name.encode() + b"\0"
        data = names if name == ".shstrtab" else data
        hdrs.append((n, typ, 6 if name == ".text" else 0, pos, pos, len(data), 0, 0, 1, 0))
        body += data.ljust(0x100, b"\0")
        pos += 0x100
    shoff = pos
    head = b"\x7fELF\x01\x01\x01".ljust(16, b"\0") + struct.pack("<HHIIIIIHHHHHH", 2, 40, 1, 0, 0, shoff, 0, 52, 0, 0, 40, len(hdrs), len(hdrs) - 1)
    return head.ljust(0x100, b"\0") + body + b"".join(struct.pack("<10I", *h) for h in hdrs)


def bl(at: int, target: int, blx: bool = False) -> bytes:
    """BL (o BLX) Thumb-2 desde `at` hacia `target`."""
    imm = target - (at + 4)
    s, i1, i2 = (imm >> 24) & 1, (imm >> 23) & 1, (imm >> 22) & 1
    j1, j2 = ~(i1 ^ s) & 1, ~(i2 ^ s) & 1
    hw1 = 0xF000 | s << 10 | (imm >> 12) & 0x3FF
    hw2 = (0xC000 if blx else 0xD000) | j1 << 13 | j2 << 11 | (imm >> 1) & 0x7FF
    return struct.pack("<HH", hw1, hw2)


NOP = b"\x00\xbf"


def test_elf_thumb_callers_finds_forward_and_backward_bl():
    tool = load("elf_thumb_callers")
    code = bl(0x100, 0x140) + NOP * 8 + bl(0x114, 0x108) + NOP * 20
    b = make_elf([(".text", 1, code)])
    assert tool.text_range(b) == (0x100, 0x100, len(code))
    assert list(tool.callers(b, {0x140, 0x108})) == [(0x100, 0x140), (0x114, 0x108)]
    assert list(tool.callers(b, {0x999})) == []


def test_thumb_callers_distinguishes_bl_from_blx():
    tool = load("thumb_callers")
    d = bytes(OFF) + bl(BASE, BASE + 0x40) + bl(BASE + 4, BASE + 0x80, blx=True) + NOP * 4
    assert list(tool.bl_targets(d)) == [(BASE, BASE + 0x40), (BASE + 4, BASE + 0x80)]


def test_elf_string_xrefs_resolves_pc_relative_string():
    tool = load("elf_string_xrefs")
    text = struct.pack("<HH", 0x4801, 0x4478) + NOP * 2 + struct.pack("<I", 0x120 - 0x106) + NOP * 40  # ldr r0,[pc,#4]; add r0,pc
    b = make_elf([(".text", 1, text)])
    assert tool.sections(b)[".text"][3] == 0x100
    assert tool.xrefs(b, {0x120, 0x130}) == {0x120: [0x100], 0x130: []}


def test_func_owner_attributes_address_to_previous_start():
    tool = load("func_owner")
    ordered, starts, names = [0x1000, 0x1100], {0x1000: ["Foo::run"]}, {0x1100: "export_fn"}
    assert tool.owner(0x1010, ordered, starts, names) == {"addr": "0x1010", "func": "0x1000", "gap": 0x10, "export": None, "virtual_of": ["Foo::run"]}
    assert tool.owner(0x1100, ordered, starts, names)["export"] == "export_fn"
    m = tool.BL.match("  1006:\tbl\t0x2000 <foo@plt>")
    assert (m[1], m[2], m[3]) == ("1006", "2000", "foo@plt")


def test_pin_signatures_reads_immediates_before_mwf_constructor(tmp_path, monkeypatch):
    tool = load("pin_signatures")
    ctor = next(k for k, v in tool.KINDS.items() if v == ("r1", "r2", "r3"))
    dis = tmp_path / "dis.txt"
    dis.write_text(f"    1000:\tmovs\tr1, #5\n    1002:\tmovs\tr2, #0\n    1004:\tmovs\tr3, #1\n    1006:\tbl\t0x9999 <{ctor}@plt>\n")
    rtti = tmp_path / "rtti.json"
    rtti.write_text(json.dumps({"methods_by_entry": {"0x1000": ["Foo::bar"]}}))
    monkeypatch.chdir(ROOT)
    pin_name = {p["type"]: p["name"] for p in json.loads((ROOT / "analysis/topology-table-libobj.json").read_text())["pin_tbl"]}
    assert tool.signatures(str(tmp_path / "no-existe.so"), str(dis), str(rtti)) == {"0x1000": [(pin_name.get(5, 5), 0, "out")]}


def test_schematic_pin_nets_groups_words_by_row():
    tool = load("schematic_pin_nets")
    ws = [(30.0, 10.4, "B"), (10.0, 10.0, "A"), (10.0, 50.0, "C")]
    assert tool.rows(ws) == {5: [(10.0, "A"), (30.0, "B")], 25: [(10.0, "C")]}


def test_rtti_vtables_elf_reads_relocations_and_symbols(tmp_path):
    tool = load("rtti_vtables")
    dynstr = b"\0_ZTI3Foo\0"
    dynsym = struct.pack("<IIIBBH", 0, 0, 0, 0, 0, 0) + struct.pack("<IIIBBH", 1, 0x120, 0, 0, 0, 1)
    data = bytearray(0x100)
    struct.pack_into("<II", data, 0x10, 0x140, 4)  # destino de R_RELATIVE y adendo de R_ABS32
    rel = struct.pack("<II", 0x210, tool.R_RELATIVE) + struct.pack("<II", 0x214, 1 << 8 | tool.R_ABS32)
    path = tmp_path / "lib.so"
    path.write_bytes(make_elf([(".text", 1, NOP * 8), (".data", 1, bytes(data)), (".dynsym", 11, dynsym), (".dynstr", 3, dynstr), (".rel.dyn", 9, rel)]))
    e = tool.Elf(str(path))
    assert e.syms == [("", None), ("_ZTI3Foo", 0x120)]
    assert e.rel == {0x210: (0x140, None), 0x214: (0x124, "_ZTI3Foo")}
    assert e.is_code(0x105) and not e.is_code(0x300)


@pytest.mark.skipif(not shutil.which("llvm-objdump"), reason="requiere llvm-objdump")
def test_thumb_pc_strings_prints_string_loaded_pc_relative(tmp_path):
    text = struct.pack("<HH", 0x4801, 0x4478) + NOP * 2 + struct.pack("<I", 0x120 - 0x106) + NOP * 10 + b"hello\0"
    lib = tmp_path / "lib.so"
    lib.write_bytes(make_elf([(".text", 1, text)]))
    out = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/thumb_pc_strings.py"), str(lib), "0x100", "0x110"], capture_output=True, text=True, check=True).stdout
    assert out.strip() == "102: 'hello'"


def test_dump_dmm_unit_types_reads_records_until_terminator(tmp_path, monkeypatch):
    tool = load("dump_dmm_unit_types")
    ko = tmp_path / "dmm.ko"
    blob = bytearray(b"\xff" * (tool.RODATA_OFF + tool.CONFIG_OFF + tool.CONFIG_SIZE))
    struct.pack_into("<8I", blob, tool.FIRST_RECORD, 0x50B3F, 0, 0xED, 0xFFFFFFFF, 0xE0B00, 0, 0xE4, 0xFFFFFFFF)
    ko.write_bytes(blob)
    monkeypatch.setattr(tool, "KO", ko)
    tool.main(str(tmp_path / "out.json"))
    out = json.loads((tmp_path / "out.json").read_text())
    assert out["unit_types"] == {"0x50b3f": [0xED], "0xe0b00": [0xE4]} and out["count"] == 2


def test_dump_topology_table_extracts_rows_from_libobj(tmp_path, monkeypatch):
    tool = load("dump_topology_table")
    with open(tmp_path / "libObj.so", "wb") as f:
        f.truncate(tool.TOPO_BASE + tool.TOPO_ROWS * 0x20)
        f.seek(tool.TOPO_BASE + 0x2A * 0x20 + 2 * 4)  # src_obj
        f.write(struct.pack("<I", 9))
        f.seek(tool.TOPO_BASE + 0x2A * 0x20 + 5 * 4)  # dst_obj
        f.write(struct.pack("<I", 11))
    (tmp_path / "libSysDef.so").write_bytes(bytes(0x14000))
    monkeypatch.setattr(tool, "LIBDIR", tmp_path)
    tool.main(str(tmp_path / "out.json"))
    out = json.loads((tmp_path / "out.json").read_text())
    assert len(out["topology_rows"]) == tool.TOPO_ROWS and len(out["pin_tbl"]) == tool.SYSDEF_PIN_N
    assert out["topology_rows"][0x2A]["src_obj"] == 9 and out["obj_tbl_libsysdef"][0]["obj_name"] == ""


def test_fdat_guard_probe_never_writes_to_the_camera():
    called = {n.attr for n in ast.walk(ast.parse((ROOT / "scripts/fdat_guard_probe.py").read_text())) if isinstance(n, ast.Attribute)}
    assert "checkGuard" in called and not called & {"switchMode", "writeFirmware"}
