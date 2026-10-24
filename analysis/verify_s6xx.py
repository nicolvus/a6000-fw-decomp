#!/usr/bin/env python3
"""Verificación detallada S605–S627: cadenas, logger dual, equivalencia, obturador.

Corrige el problema de búsqueda del obturador: solo busca en las cadenas de
traza del módulo, no en todo el binario.
"""
import json
import struct
from pathlib import Path

FW_A6000 = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
BASE = 0x43541000

data = FW_A6000.read_bytes()
fw_size = len(data)


def vaddr_to_offset(vaddr: int):
    off = vaddr - BASE
    if off < 0 or off >= fw_size:
        return None
    return off


def read_cstring(off: int):
    if off is None:
        return None
    try:
        end = data.index(b"\x00", off)
        return data[off:end].decode("ascii", errors="replace")
    except ValueError:
        return None


def norm(s: str):
    """Normaliza para comparación: elimina trailing whitespace."""
    if s is None:
        return None
    return s.rstrip()


json_dirs = sorted(
    d for d in Path("analysis").glob("s6[0-2][0-9]_*")
    if 605 <= int(d.name[1:4]) <= 627
)

results = []

for jd in json_dirs:
    json_files = list(jd.glob("*.json"))
    if not json_files:
        continue
    jp = json_files[0]
    with open(jp) as f:
        jdata = json.load(f)

    module_name = jdata.get("module", jd.name)
    trace_strings = jdata.get("trace_strings", [])
    logger_dual = jdata.get("logger_dual", False)
    global_logger = jdata.get("global_logger", None)
    prefix = jdata.get("prefix", "")

    # --- 1. Verificar cadenas ---
    strings_ok = 0
    strings_total = len(trace_strings)
    string_details = []
    for ts in trace_strings:
        vaddr = int(ts["vaddr"], 16) if isinstance(ts["vaddr"], str) else ts["vaddr"]
        expected = norm(ts["text"])
        off = vaddr_to_offset(vaddr)
        found = norm(read_cstring(off))
        if found is not None and found == expected:
            strings_ok += 1
            string_details.append({"vaddr": ts["vaddr"], "ok": True, "text": expected[:50] if expected else ""})
        else:
            string_details.append({
                "vaddr": ts["vaddr"],
                "ok": False,
                "expected": expected[:50] if expected else "",
                "found": found[:50] if found else "NOT_FOUND",
            })

    strings_verified = strings_ok == strings_total and strings_total > 0

    # --- 2. Línea del obturador: buscar SOLO en las cadenas de traza del módulo ---
    # Usar límites de palabra (\b) para evitar coincidencias parciales.
    # Falsos positivos conocidos (documentados):
    #   - "shot" en "Shot Timing Transform" (S611) = contexto de ráfaga GOLFSHOT, no obturador
    #   - "sync" en "osal_reg_sync_msg_queue_cb" (S620) = registro sincrónico, no vsync
    import re
    shutter_patterns = [
        r"\bshutter\b", r"\bsilent\b", r"\bcurtain\b", r"\belectro\b", r"\bmech\b",
        r"\bobtur\b", r"\bsensor\b", r"\breadout\b", r"\bimager\b", r"\biso\b",
        r"\bapert\b", r"\bexpos\b", r"\bbrack\b", r"\bdrive\b", r"\brelease\b",
        r"\bflash\b", r"\bvsync\b", r"\bcapture\b", r"\bstill\b", r"\bmovie\b",
        r"\bfocus\b", r"\bsvd\b", r"\bshd\b", r"\bspl\b", r"\bframe\b",
    ]
    # "shot" y "sync" se excluyen de los patrones por falsos positivos conocidos
    # (ver comentario arriba). Se añaden solo como contexto si aparecen con palabras
    # claramente de obturador.
    shutter_found_in_traces = []
    for ts in trace_strings:
        text = ts["text"].lower()
        for pat in shutter_patterns:
            if re.search(pat, text) and pat not in shutter_found_in_traces:
                shutter_found_in_traces.append(pat)

    shutter_verified = len(shutter_found_in_traces) == 0

    # --- 3. Logger global ---
    logger_ok = False
    logger_msg = "no_global_logger"
    if global_logger:
        lg = global_logger
        if isinstance(lg, str):
            try:
                lg_int = int(lg, 16)
            except ValueError:
                lg_int = None
        else:
            lg_int = lg
        if lg_int:
            off = vaddr_to_offset(lg_int)
            if off is not None:
                b = data[off:off + 4]
                if b != b"\x00\x00\x00\x00" and b != b"\xff\xff\xff\xff":
                    logger_ok = True
                    logger_msg = f"code @0x{off:06x}"
                else:
                    logger_msg = "zero_or_fill"
            else:
                logger_msg = "out_of_range"

    results.append({
        "module": module_name,
        "dir": jd.name,
        "json": str(jp),
        "strings_total": strings_total,
        "strings_ok": strings_ok,
        "strings_verified": strings_verified,
        "logger_dual_claimed": logger_dual,
        "logger_dual_verified": False,  # NV: requiere xrefs/REA
        "logger_global": global_logger,
        "logger_global_verified": logger_ok,
        "logger_global_msg": logger_msg,
        "equiv_func_verified": False,   # NV: requiere A7S/A6300
        "equiv_code_verified": False,   # NV: requiere comparación de instrucciones
        "shutter_verified": shutter_verified,
        "shutter_found_in_traces": shutter_found_in_traces,
        "string_details": string_details,
    })

# Guardar resultados
out = Path("analysis/s6xx_verification_results.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Tabla
print("=" * 110)
print("TABLA DE HALLAZGOS S605–S627")
print("=" * 110)
print(f"{'Módulo':<24} {'Cadenas':<14} {'LoggerDual':<14} {'EquivFunc':<14} {'EquivCode':<14} {'Obturador':<12}")
print("-" * 110)
for r in results:
    s = "V" if r["strings_verified"] else "X"
    ld = "NV"
    ef = "NV"
    ec = "NV"
    sh = "V" if r["shutter_verified"] else "X"
    print(f"{r['module']:<24} {s:<14} {ld:<14} {ef:<14} {ec:<14} {sh:<12}")

print()
print("Leyenda: V = Verificado contra firmware, X = Rechazado (no coincide), NV = NO_VERIFICADO")
print()
print("Detalle por módulo:")
for r in results:
    print(f"\n--- {r['module']} ---")
    print(f"  Cadenas: {r['strings_ok']}/{r['strings_total']} verificadas")
    for sd in r["string_details"]:
        if not sd["ok"]:
            print(f"    FALLA: {sd['vaddr']} esperado='{sd.get('expected','?')}' encontrado='{sd.get('found','?')}'")
    print(f"  Logger dual: reclamado={r['logger_dual_claimed']}, verificado=NV (requiere xrefs/REA)")
    print(f"  Logger global: {r['logger_global_msg']}")
    print(f"  Equivalencia funcional: NV (requiere A7S/A6300)")
    print(f"  Equivalencia de código: NV (requiere comparación de instrucciones)")
    if r["shutter_verified"]:
        shutter_msg = "VERIFICADO (0 kw en trazas)"
    else:
        shutter_msg = f'RECHAZADO: {r["shutter_found_in_traces"]}'
    print(f"  Línea del obturador: {shutter_msg}")

print(f"\nResultados guardados en {out}")