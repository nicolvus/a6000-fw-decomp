#!/usr/bin/env python3
"""Actualiza los JSONs S605–S627 con verification_status basado en la evidencia del firmware."""
import json
from pathlib import Path

json_dirs = sorted(
    d for d in Path("analysis").glob("s6[0-2][0-9]_*")
    if 605 <= int(d.name[1:4]) <= 627
)

for jd in json_dirs:
    json_files = list(jd.glob("*.json"))
    if not json_files:
        continue
    jp = json_files[0]
    with open(jp) as f:
        jdata = json.load(f)

    # Cargar resultados de verificación
    res_file = Path("analysis/s6xx_verification_results.json")
    with open(res_file) as f:
        results = json.load(f)

    # Encontrar resultado para este módulo
    module_name = jdata.get("module", jd.name)
    res = next((r for r in results if r["module"] == module_name), None)

    if res:
        jdata["verification_status"] = {
            "trace_strings": {
                "verified": res["strings_verified"],
                "count_ok": res["strings_ok"],
                "count_total": res["strings_total"],
                "basis": "lectura directa de bytes en av-cam.bin (base 0x43541000)",
                "details": res["string_details"],
            },
            "logger_dual": {
                "claimed": res["logger_dual_claimed"],
                "verified": res["logger_dual_verified"],
                "status": "NO_VERIFICADO",
                "reason": "requiere xrefs/REA sobre instrucciones BL al logger global; la presencia de cadenas no demuestra duplicación",
                "global_logger": res["logger_global"],
                "global_logger_verified": res["logger_global_verified"],
                "global_logger_msg": res["logger_global_msg"],
            },
            "equivalencia_funcional": {
                "claimed": True,
                "verified": res["equiv_func_verified"],
                "status": "NO_VERIFICADO",
                "reason": "requiere análisis de A7S fw3.20 y A6300 fw2.01; presencia de cadenas núcleo no demuestra equivalencia de código",
            },
            "equivalencia_codigo": {
                "claimed": True,
                "verified": res["equiv_code_verified"],
                "status": "NO_VERIFICADO",
                "reason": "requiere comparación de instrucciones (disassembly/xrefs) entre modelos",
            },
            "linea_obturador": {
                "claimed": True,
                "verified": res["shutter_verified"],
                "status": "VERIFICADO" if res["shutter_verified"] else "RECHAZADO",
                "basis": "búsqueda de palabras clave del obturador únicamente en cadenas de traza del módulo",
                "keywords_found_in_traces": res["shutter_found_in_traces"],
            },
        }

    with open(jp, "w") as f:
        json.dump(jdata, f, indent=2, ensure_ascii=False)

    print(f"Actualizado: {jp}")

print("\nTodos los JSONs actualizados con verification_status.")