"""E25-19: lector de solo lectura y controlador (sin cámara: transporte simulado)."""
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e25_19_readonly as rd
import e25_19_test as ct


def hd(data: bytes) -> str:
    """Salida con el formato de `hd` de la cámara (incluye la línea de error final)."""
    lines = [f"{i:08x}: " + " ".join(f"{b:02x}" for b in data[i:i + 16]) + "  " + "".join(
        chr(b) if 32 <= b < 127 else "." for b in data[i:i + 16]) for i in range(0, len(data), 16)]
    return "\n".join(lines) + f"\nRead error on /proc/self/fd/0, offset {len(data)} len 4096, No such file or directory\n"


def test_parse_hd_roundtrip_and_ascii_ambiguity():
    data = bytes(range(0x30, 0x30 + 40))  # el ASCII ("0123…") parece hexadecimal: no debe contarse
    assert rd.parse_hd(hd(data), 40) == data


def test_parse_hd_rejects_short_output():
    with pytest.raises(rd.ReadError):
        rd.parse_hd(hd(b"\x00" * 8), 16)


class FakeTelnet(rd.Telnet):
    """Memoria simulada; `run` imita `dd | hd` y registra los comandos."""

    def __init__(self, mem: dict[int, bytes]):
        self.mem, self.cmds = mem, []

    def run(self, cmd: str) -> str:
        self.cmds.append(cmd)
        out = []
        for part in cmd.split("; "):
            if part.startswith("echo @@"):
                out.append(part.removeprefix("echo ") + "\n")
            elif "dd if=/dev/mem" in part:
                skip, count = (int(x.split("=")[1]) for x in part.split()[3:5] if x.startswith(("skip", "count")))
                phys, size = skip * 2, count * 2
                base = next(b for b in self.mem if b <= phys < b + len(self.mem[b]))
                out.append(hd(self.mem[base][phys - base:phys - base + size]))
        return "".join(out)


def test_read_many_one_command_and_order():
    tr = FakeTelnet({0x1000: bytes(range(64))})
    a, b = tr.read_many([(0x1000, 4), (0x1010, 6)])
    assert (a, b) == (bytes(range(4)), bytes(range(16, 22)))
    assert len(tr.cmds) == 1  # una sola ida y vuelta


def test_read_is_readonly():
    tr = FakeTelnet({0x1000: bytes(32)})
    tr.read(0x1000, 8)
    assert all("of=" not in c and ">" not in c.replace("2>/dev/null", "") for c in tr.cmds)


def test_unaligned_region_rejected():
    with pytest.raises(rd.ReadError):
        FakeTelnet({0x1000: bytes(8)}).read(0x1001, 4)


def memory(originals_ok: bool = True) -> dict[int, bytes]:
    mem = {phys: bytes.fromhex(exp) for _, (phys, _s, exp) in rd.T050.items()} if originals_ok else {
        phys: bytes(size) for _, (phys, size, _e) in rd.T050.items()}
    for (phys, ptr) in rd.GOT_CHECKS.values():
        mem[phys] = struct.pack("<I", ptr)
    return mem


def test_verify_originals_ok_and_mismatch():
    assert rd.verify_originals(FakeTelnet(memory()))["ok"]
    assert not rd.verify_originals(FakeTelnet(memory(originals_ok=False)))["ok"]


def record_bytes(**kw) -> bytes:
    b = bytearray(0x158)
    for off, fmt, label in rd.FIELDS["record_a"] + rd.EXTRA_RECORD:
        if label in kw:
            struct.pack_into(fmt, b, off, kw[label])
    return bytes(b)


def test_snapshot_light_decodes_only_read_fields_and_diff():
    mem = memory()
    for name, (phys, size) in rd.OBJECTS.items():
        mem[phys] = record_bytes(vts=4176, svd=0, shd=1, tv=5376) if name == "record_a" else bytes(size)
    s1 = rd.snapshot(FakeTelnet(mem), "a", light=True)
    rec = s1["objects"]["record_a"]["decoded"]
    assert (rec["vts"], rec["shd"], rec["svd"], rec["tv"]) == (4176, 1, 0, 5376)
    mem[rd.OBJECTS["record_a"][0]] = record_bytes(vts=4176, svd=14, shd=1, tv=4011)
    s2 = rd.snapshot(FakeTelnet(mem), "b", light=True)
    assert rd.diff(s1, s2) == {"record_a": {"svd": [0, 14], "frames": [0, 14], "tv": [5376, 4011]}}  # frames = alias de svd (+0x68)


def test_speed_args():
    assert ct.speed_args("1/30") == (1, 30)
    assert ct.speed_args("4") == (4, 1)
