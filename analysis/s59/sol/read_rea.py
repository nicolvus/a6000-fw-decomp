"""Extrae resultados normalizados conservando el JSONL REA original."""
import json
import sys
from pathlib import Path


def extract(path):
    path = Path(path)
    seen = set()
    for line in path.read_text().splitlines():
        record = json.loads(line)
        key = json.dumps(record["call"], sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        result = record.get("result", {})
        content = result.get("content", [])
        parsed = json.loads(content[0]["text"]) if content else result
        value = parsed.get("normalized_result", parsed) if isinstance(parsed, dict) else parsed
        call = record["call"]
        name = call["tool"] + "_" + call["args"]["procedure"]
        text = value if isinstance(value, str) else json.dumps(value, indent=2)
        path.with_name(name + ".txt").write_text(text or "null")
        print(name, len(text or ""), (text or "null")[:350])


if __name__ == "__main__":
    extract(sys.argv[1])
