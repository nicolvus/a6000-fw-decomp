"""E24-05d: transporte Darwin→BIONZ y consumidores (solo lectura de bytes de `av-cam.bin` y `darwin_core.bin`).

Reproducible: `python scripts/e24_05d/transport.py` imprime el JSON y lo guarda en analysis/e24-05d/transport.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e24_05"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bz import AVCAM, BASE, ROOT, Bz  # noqa: E402
from capture_flow import message_table  # noqa: E402
from dwn import Core  # noqa: E402

IDX_TABLE, ROWS = 0x43C90100, 0x43FE87F0  # índice [13*clase+sub] -> fila de 16 B
TRACE, CAIF_RECV, RCV_SYS = 0x43ACABE8, 0x437DB9F0, 0x43561260
TAG = 0x1502C7  # etiqueta de bloque CAIF y buzón interno de la tarea CA
STAGE_WAITERS = {0: None, 2: 0x438D06E4, 3: 0x438D08E8, 5: 0x438D0B44, 6: 0x438D050C, 9: 0x438D060C, 0xA: 0x438D06E4, 0xC: 0x438D0BE4}


def trace_code(b: Bz, fn: int, size: int = 0x90) -> int | None:
    """Código de traza (0x1xx) que un manejador pasa a 0x43acabe8 (`movw/mov.w r0,#imm` antes del `bl`)."""
    ins = b.dis(fn, size)
    for k, i in enumerate(ins):
        if i.mnemonic == "bl" and int(i.op_str.lstrip("#"), 16) == TRACE:
            for j in ins[:k][::-1]:
                if j.mnemonic.startswith("mov") and j.op_str.startswith("r0, #"):
                    return int(j.op_str.split("#")[1], 0)
    return None


def caif_rows(b: Bz, d: Core) -> list[dict]:
    out = []
    for r in message_table(d):
        code = d.u32(r["addr"] + 12)
        cls, sub = code & 0xFF, (code >> 8) & 0xFF
        idx = b.u8(IDX_TABLE + 13 * cls + sub)
        row = ROWS + 16 * idx
        w = [b.u32(row + 4 * k) for k in range(4)]
        e = {"id": r["id"], "dir": r["dir"], "len": r["len"], "cls": cls, "sub": sub, "row": idx, "row_n": w[0],
             "fn_getter": w[1] - 1, "fn_rx": w[2] - 1}
        if r["dir"].startswith("Darwin"):
            e["trace"] = trace_code(b, w[2] - 1)
        out.append(e)
    return out


def recv_facts(b: Bz) -> dict:
    ins = b.dis(0x437DBA2E, 0x10)
    return {"tmo_minus1": ins[0].mnemonic == "mov.w" and ins[0].op_str == "r2, #-1",
            "rcv_call": hex(next(i.address for i in ins if i.mnemonic == "bl")), "tag": hex(TAG),
            "slot_by_sub": {k: 0x20 + 4 * _slot(b, k) for k in range(16) if _slot(b, k) is not None},
            "callers": [hex(c) for c in b.bl_callers(CAIF_RECV)]}


def _slot(b: Bz, sub: int):
    t = 0x437DBAF0 + 2 * b.u8(0x437DBAF0 + sub)
    m = re.search(r"movs r5, #(\d+)", b.text(t, 6))
    return int(m.group(1)) if m else None


def rcv_timeouts(b: Bz) -> dict:
    cnt: dict[str, int] = {}
    for c in b.bl_callers(RCV_SYS):
        v = "?"
        for i in [i for i in b.dis(c - 16, 16) if i.address < c][::-1]:
            if i.op_str.startswith("r2,") and i.mnemonic.startswith("mov"):
                v = i.op_str.split(",")[1].strip()
                break
        cnt[v] = cnt.get(v, 0) + 1
    return cnt


def darwin_facts(d: Core) -> dict:
    ins = d.all_insns

    def callers(t):
        return [hex(i.address) for i in ins if i.mnemonic.startswith("b") and i.operands and i.operands[0].type == 2 and i.operands[0].imm == t]

    return {"callers_0xd294_mask_getter": callers(0xD294), "callers_0x6ba4_freeze": callers(0x6BA4), "callers_0x16bca_ring_copy": callers(0xCF0E),
            "callback_list_0x26d24": [hex(d.u32(0x26D24 + 4 * k)) for k in range(2)],
            "mask_literal_users": [hex(i.address) for i in ins if d.lit_of(i) == 0x20002BD0],
            "ring_literal_users": [hex(i.address) for i in ins if d.lit_of(i) == 0x20000680]}


def main() -> dict:
    b, d = Bz(), Core()
    res = {"sha256_av_cam": __import__("hashlib").sha256(AVCAM.read_bytes()).hexdigest(), "sha256_darwin_core": d.sha256(),
           "caif_rows": caif_rows(b, d), "caif_recv": recv_facts(b), "rcv_timeouts": rcv_timeouts(b), "darwin": darwin_facts(d)}
    out = ROOT / "analysis/e24-05d/transport.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str) + "\n")
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
