"""S71-14: localiza en el av-cam de A7S la secuencia homóloga de una ventana A6000 comparando mnemónicos+registros (sin inmediatos)."""
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

A6 = Path("analysis/rea-independent/input/av-cam.bin").read_bytes()
A7 = Path("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
base = 0x43541000
lo, n = int(sys.argv[1], 16), int(sys.argv[2])
if len(sys.argv) > 3 and sys.argv[3] == 'rev':  # ventana A7S -> busca en A6000
    A6, A7 = A7, A6
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True


def norm(i):
    return i.mnemonic + " " + re.sub(r"#?-?0x[0-9a-f]+|#\d+", "#", i.op_str)


win = [norm(i) for i in list(md.disasm(A6[lo - base:lo - base + 400], lo))[:n]]
ins7 = list(md.disasm(A7[:0x9c0000], base))
seq7 = [norm(i) for i in ins7]
best = []
for s in range(len(seq7) - n):
    sc = sum(a == b for a, b in zip(win, seq7[s:s + n]))
    if sc >= n * 0.8:
        best.append((sc, hex(ins7[s].address)))
print(sorted(best, reverse=True)[:5])
