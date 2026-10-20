"""S61: cliente mínimo del demonio REA (sesión única) que devuelve solo el resultado normalizado."""
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOCK = ROOT / "analysis/rea-independent/run/s61.sock"


def run(calls):
    s = socket.socket(socket.AF_UNIX)
    s.connect(str(SOCK))
    s.sendall((json.dumps({"calls": calls}) + "\n").encode())
    out = []
    for line in s.makefile("rb"):
        r = json.loads(line)
        res = r.get("result", {})
        try:
            j = json.loads(res["content"][0]["text"])
            val = j.get("raw_result", j)
            if isinstance(val, dict) and "value" in val:
                val = val["value"]
        except (KeyError, IndexError, ValueError):
            val = res
        out.append({"call": r.get("call"), "value": val})
    return out


if __name__ == "__main__":
    calls = json.loads(Path(sys.argv[1]).read_text())
    for o in run(calls):
        v = o["value"]
        print("##", o["call"]["tool"], o["call"]["args"])
        print(v if isinstance(v, str) else json.dumps(v)[:int(sys.argv[2]) if len(sys.argv) > 2 else 3000])
