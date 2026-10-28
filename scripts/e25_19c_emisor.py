#!/usr/bin/env python3
"""E25-19c — buzón CAIF y paquete 0x0c (Tv hacia Darwin), solo lectura.

Cadena: Darwin -> CAIF (3,3)=ID 0x0e -> receptor 0x436b8ef0 -> osal_snd_msg(0x4356120c, [0x43e77284]) -> caif_recv(3)
0x437db9f0 (cola = [[GOT 0x44023068]] = [0x43ed4cb0]). Se comprueba en vivo si ambas variables son el mismo id de cola
y se decodifica pkt[2..3] (Tv, u16) del último CaptureStartRes en `[cap+0x4ad8]+0x40`.
Uso: e25_19c_emisor.py --confirm-readonly
"""

from __future__ import annotations

import argparse
import json
import struct

from e25_19_readonly import HOST, OUTDIR, Telnet, verify_originals
from e25_19b_cadena import RAM_OFF

VAR_RX, VAR_TX = 0x43E77284, 0x43ED4CB0  # id de cola: receptor Darwin->BIONZ / variable de caif_recv
SLOTS = 0x43ED4908  # [cap+0x4ad8] observado en E25-19b


def tv_a_segundos(tv: int) -> float:
    """Tv = 4096 - 256*log2(t) (E25-19)."""
    return 2 ** ((4096 - tv) / 256)


def decodifica_pkt(pkt: bytes) -> dict:
    tv = struct.unpack_from("<H", pkt, 2)[0]
    return {"pkt": pkt.hex(), "pkt1": pkt[1], "tv": tv, "t_s": round(tv_a_segundos(tv), 4) if tv else None}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    ap.parse_args()
    tr = Telnet(HOST)
    try:
        assert verify_originals(tr)["ok"], "originales T050 alterados"
        def rd(a: int, n: int) -> bytes:
            return tr.read(a + RAM_OFF, n)

        res: dict = {
            "schema": "e25-19c-emisor/v1",
            "rx_var_0x43e77284": rd(VAR_RX, 4).hex(),
            "tx_var_0x43ed4cb0": rd(VAR_TX, 4).hex(),
            "slots_0x43ed4908": rd(SLOTS, 0x40).hex(),
        }
        res["pkt_0c"] = decodifica_pkt(rd(SLOTS + 0x40, 0x16))
        res["originales_ok_final"] = verify_originals(tr)["ok"]
    finally:
        tr.close()
    out = OUTDIR.parent / "e25-19c" / "emisor-vivo.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
