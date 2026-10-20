"""Comprobaciones estáticas acotadas; solo lee el ELF y escribe a stdout."""
from pathlib import Path
import hashlib
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from rtti_vtables import Elf  # noqa: E402

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
elf = Elf(str(LIB))
digest = hashlib.sha256(elf.d).hexdigest()
assert digest == "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"
print("ELF", LIB.relative_to(ROOT))
print("SHA256", digest)
print(subprocess.run(["llvm-objdump", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0])


def raw(addr, size):
    off = elf.off(addr)
    assert off is not None
    return elf.d[off:off + size]


def dis(start, end, isa="thumb"):
    cmd = ["llvm-objdump", "-d", f"--triple={isa}v7-linux-gnueabi", "--no-show-raw-insn",
           f"--start-address={start:#x}", f"--stop-address={end:#x}", str(LIB)]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("COMMAND", " ".join(cmd))
    print(result.stdout)
    return result.stdout


for start, end in [(0x13dbb0, 0x13dbbc), (0x13de98, 0x13df58),
                   (0x13ef58, 0x13f088), (0x13f08c, 0x13f170),
                   (0x13f34a, 0x13f354), (0x143fb0, 0x143fd8)]:
    dis(start, end)
dis(0x11e3f8, 0x11e3fc)
dis(0x11e3fc, 0x11e408, "arm")

print("LITERALS (VA -> u32; no tablas completas reextraídas)")
for addr in [0x13df14, 0x13df18, 0x13df1c, 0x13df50, 0x13df54, 0x143fd4]:
    print(hex(addr), hex(elf.u32(addr)))

# El stub Thumb hace BX PC y entra al bloque ARM siguiente, no al símbolo anterior.
assert raw(0x11e3f8, 4) == bytes.fromhex("7847c046")
w0, w1, w2 = struct.unpack("<III", raw(0x11e3fc, 12))
assert w0 & 0xfffff000 == 0xe28fc000
assert w1 & 0xfffff000 == 0xe28cc000
assert w2 & 0xfffff000 == 0xe5bcf000


def arm_imm(word):
    value, rotation = word & 255, ((word >> 8) & 15) * 2
    return ((value >> rotation) | (value << ((32 - rotation) % 32))) & 0xffffffff


got = 0x11e3fc + 8 + arm_imm(w0) + arm_imm(w1) + (w2 & 0xfff)
rel = elf.secs[".rel.plt"]
matches = []
for offset in range(0, rel["size"], 8):
    where, info = struct.unpack_from("<II", elf.d, rel["off"] + offset)
    if where == got:
        matches.append(elf.syms[info >> 8])
assert got == 0x9c3934
assert matches == [("_ZN11CS_AviMprIf10MPR2AVIErrEN3MPR5ErrCdE", 0x143fb1)]
print("PLT_VERIFICADA", hex(got), matches)

# Control positivo: el helper escribe cero, y el consumidor comprueba ese argumento.
assert raw(0x13ef5a, 2) == bytes.fromhex("0023")  # movs r3,#0
assert raw(0x13ef5e, 2) == bytes.fromhex("1360")  # str r3,[r2]
assert raw(0x13efa2, 2) == bytes.fromhex("0029")  # cmp r1,#0
assert raw(0x13f13a, 2) == bytes.fromhex("cd2b")  # cmp r3,#0xcd
assert hashlib.sha256(LIB.read_bytes()).hexdigest() == digest
print("PASS: hash antes/después, interworking PLT/relocación, stub cero y guardas diagnósticas")
