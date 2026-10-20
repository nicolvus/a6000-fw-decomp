"""S59: decodificador P2S parametrizado por base (S58 fijaba 0xf3c00300, artefacto del objeto sintético)."""
import sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 's58'))
def transactions(writes, base):
    fifo, end, trig = base + 0x40, base + 0x300, base + 0x508
    txs, cur = [], {}
    for pc, a, sz, v, tag in writes:
        if fifo <= a < end: cur[(a - fifo) // 4] = v & 0xff
        elif a == trig and pc == 0x436f26f0:
            txs.append(bytes(cur[i] for i in range(max(cur) + 1)) if cur else b''); cur = {}
    if cur: txs.append(bytes(cur[i] for i in range(max(cur) + 1)))
    return txs
