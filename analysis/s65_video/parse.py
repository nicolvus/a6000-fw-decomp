#!/usr/bin/env python3
"""Parsea la salida .jsonl del demonio REA y extrae el resultado útil por llamada."""
import sys, json

def extract(out):
    r = out.get("result", {})
    # MCP envuelve en content[].text (JSON string) o structuredContent
    sc = r.get("structuredContent")
    if isinstance(sc, dict):
        if "value" in sc:
            return sc["value"]
        if "text" in sc:
            return sc["text"]
        return json.dumps(sc)[:4000]
    content = r.get("content")
    if content:
        t = content[0].get("text", "")
        try:
            j = json.loads(t)
            if isinstance(j, dict) and "value" in j:
                return j["value"]
        except Exception:
            pass
        return t[:4000]
    return json.dumps(r)[:4000]

def main(path):
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception as e:
            print("PARSE_ERR", e); continue
        call = rec.get("call", {})
        tool = call.get("tool")
        args = call.get("args", {})
        out = rec.get("result", rec)
        err = rec.get("error")
        print("=" * 80)
        print(f"TOOL {tool} ARGS {json.dumps(args)}")
        if err:
            print("ERROR", json.dumps(err)[:1000])
            continue
        if tool in ("procedure_pseudo_code", "procedure_disassembly", "procedure_bytes",
                    "read_bytes", "instruction_disassembly"):
            print(extract(out))
        else:
            print(extract(out))

if __name__ == "__main__":
    main(sys.argv[1])
