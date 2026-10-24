"""Auditoría estática S605–S627. No ejecuta firmware ni modifica archivos."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
SUFFIX = "firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
FIRMWARE = {
    "a6000_fw321": ROOT / "firmware/extracted/fw321" / SUFFIX,
    "a7s_fw320": ROOT / "firmware/extracted/a7s-fw320/payload" / SUFFIX,
    "a6300_fw201": ROOT / "firmware/extracted/a6300-fw201/payload" / SUFFIX,
}


def module_files():
    return sorted(
        p for p in (ROOT / "analysis").glob("s6[0-2][0-9]_*/*.json")
        if 605 <= int(p.parent.name[1:4]) <= 627
    )


def check_string(blob, address, text):
    """Compara todos los bytes, incluido NUL, sin normalizar espacios."""
    off = int(address, 16) - BASE
    expected = text.encode("ascii") + b"\0"
    return off >= 0 and blob[off:off + len(expected)] == expected


def occurrences(blob, text):
    """Direcciones de coincidencias exactas de texto terminado en NUL."""
    needle = text.encode("ascii") + b"\0"
    offsets = []
    off = 0
    while (off := blob.find(needle, off)) != -1:
        offsets.append(hex(BASE + off))
        off += 1
    return offsets


def pending(reason):
    return {"verified": False, "status": "NO_VERIFICADO", "reason": reason}


def verify_module(data, blobs):
    blob = blobs["a6000_fw321"]
    traces = data["trace_strings"]
    details = [
        {"vaddr": t["vaddr"], "ok": check_string(blob, t["vaddr"], t["text"])}
        for t in traces
    ]
    twins = [
        {
            "vaddr": t["twin_vaddr"],
            "ok": check_string(blob, t["twin_vaddr"], t["twin_text"]),
            "delta_ok": int(t["twin_vaddr"], 16) - int(t["vaddr"], 16) == t["delta"],
            "core_ok": t["text"].removeprefix(data["prefix"])
            == t["twin_text"].removeprefix(data["twin_prefix"]),
        }
        for t in traces if "twin_vaddr" in t
    ]
    cores = []
    for t in traces:
        if "core_text" in t:
            address = hex(int(t["vaddr"], 16) + len(data["prefix"].encode("ascii")))
            cores.append({
                "vaddr": address,
                "ok": t["text"] == data["prefix"] + t["core_text"]
                and check_string(blob, address, t["core_text"]),
                "matches_by_firmware": {
                    model: occurrences(raw, t["core_text"]) for model, raw in blobs.items()
                },
            })
    metadata_errors = []
    if data["traces"] != len(traces):
        metadata_errors.append("traces")
    for name in ("prefix", "twin_prefix", "core_prefix"):
        if name in data and data[name + "_length"] != len(data[name].encode("ascii")):
            metadata_errors.append(name + "_length")
    if "composite_prefix_length" in data:
        size = len((data["prefix"] + data["core_prefix"]).encode("ascii"))
        if data["composite_prefix_length"] != size:
            metadata_errors.append("composite_prefix_length")
    if "prefix_lengths" in data and data["prefix_lengths"] != [
        len(p.encode("ascii")) for p in data["prefixes"]
    ]:
        metadata_errors.append("prefix_lengths")
    logger = data.get("global_logger")
    off = int(logger, 16) - BASE if logger else -1
    logger_bytes = blob[off:off + 24].hex() if 0 <= off < len(blob) else None
    status = {
        "trace_strings": {
            "verified": bool(details) and all(d["ok"] for d in details),
            "count_ok": sum(d["ok"] for d in details),
            "count_total": len(details),
            "basis": "bytes ASCII exactos + NUL; base 0x43541000; sin rstrip",
            "details": details,
        },
        "twin_strings": {
            "verified": bool(twins) and all(
                d["ok"] and d["delta_ok"] and d["core_ok"] for d in twins
            ),
            "count_ok": sum(d["ok"] and d["delta_ok"] and d["core_ok"] for d in twins),
            "count_total": len(twins),
            "details": twins,
            "scope": "datos y deltas; no prueba emisión ni logger dual",
        },
        "core_strings": {
            "verified": bool(cores) and all(d["ok"] for d in cores),
            "count_total": len(cores),
            "details": cores,
            "scope": "sufijos NUL en A6000 y coincidencias por modelo; no equivalencia funcional",
        },
        "metadata": {"verified": not metadata_errors, "errors": metadata_errors},
        "logger_dual": {
            **pending("faltan cadenas de carga/llamada y flujo que demuestren ambas emisiones"),
            "claimed": bool(logger),
            "global_logger": logger,
            "global_logger_verified": False,
            "global_logger_msg": "bytes no demuestran identidad de logger ni duplicación",
            "bytes_hex": logger_bytes,
        },
        "equivalencia_funcional": pending("sin contratos, entradas, salidas y callees comparados"),
        "equivalencia_codigo": pending("sin comparación de cuerpos/instrucciones entre modelos"),
        "linea_obturador": pending(
            "un negativo léxico, incluso vacío, no prueba ausencia de una ruta de obturador"
        ),
        "differential": {
            **pending("recuentos históricos sin criterio de selección reproducible"),
            "fields": {
                model: list(fields) for model, fields in data["differential"].items()
            },
        },
        "other_claims": {
            **pending("símbolos, semántica, sitios emisores y funciones requieren evidencia propia"),
            "fields": [
                k for k in data
                if k not in {
                    "verification_status", "trace_strings", "differential", "module",
                    "traces", "prefix", "prefix_length", "twin_prefix", "twin_prefix_length",
                    "core_prefix", "core_prefix_length", "composite_prefix_length",
                    "prefixes", "prefix_lengths", "logger_dual", "global_logger", "shutter_line",
                }
            ],
        },
    }
    return status


def audit():
    blobs = {model: path.read_bytes() for model, path in FIRMWARE.items()}
    fingerprints = {
        model: {"path": str(FIRMWARE[model].relative_to(ROOT)),
                "size": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
        for model, blob in blobs.items()
    }
    results = []
    for path in module_files():
        data = json.loads(path.read_text())
        results.append({
            "module": data["module"], "json": str(path.relative_to(ROOT)),
            "firmware": fingerprints, "verification_status": verify_module(data, blobs),
        })
    if len(results) != 23 or len({r["json"][10:13] for r in results}) != 23:
        raise ValueError("Inventario S605–S627 incompleto o duplicado")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emitir evidencia JSON a stdout")
    args = parser.parse_args()
    results = audit()
    failures = []
    for result in results:
        status = result["verification_status"]
        for category in ("trace_strings", "twin_strings", "core_strings"):
            evidence = status[category]
            if evidence["count_total"] and not evidence["verified"]:
                failures.append(result["module"] + ":" + category)
        if not status["metadata"]["verified"]:
            failures.append(result["module"] + ":metadata")
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        total = sum(r["verification_status"]["trace_strings"]["count_ok"] for r in results)
        twins = sum(r["verification_status"]["twin_strings"]["count_ok"] for r in results)
        print(f"{len(results)} fichas; {total} trazas; {twins} gemelas; errores: {failures}")
        print("Logger dual, equivalencias y ausencia funcional del obturador: NO_VERIFICADO")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
