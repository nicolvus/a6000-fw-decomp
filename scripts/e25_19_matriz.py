#!/usr/bin/env python3
"""E25-19: matriz física (disparos reales) frente al productor nativo `0x4383fa40` emulado (E25-18) con los parámetros leídos.

Entrada: el último `analysis/e25-19/disparos-*.json` por velocidad (los que tengan `--speeds` completos).
Salida: `analysis/e25-19/matriz.json`. Niveles que NO se mezclan: observado en RAM (`record`) / nativo emulado con los
parámetros reales / valor temporal que recibiría SetExposure (no observado: requiere `cap`)."""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts" / "e25_18"), str(ROOT / "scripts" / "e25_16")]
from silent_plan import productor  # type: ignore[import-not-found]


def latest_by_speed() -> dict[str, dict]:
    shots: dict[str, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "analysis/e25-19/disparos-*.json"))):
        for s in json.loads(Path(f).read_text())["shots"]:
            if s["completada"] and s["salud"]["ok"]:
                shots[s["speed"]] = s  # el último completado de cada velocidad
    return shots


def main() -> None:
    rows = []
    for sp, s in latest_by_speed().items():
        rec = s["post"]["objects"]["record_a"]["decoded"]
        imager = s["post"]["objects"]["imager"]["decoded"]
        pred = s["post"]["objects"]["predicate"]["decoded"]["byte_10"]
        row = {"velocidad": sp, "duracion_s": s["duracion_s"], "log_ms": int(s["log_remoteshutter"][0].split(",")[2]),
               "observado_record_a": {k: rec[k] for k in ("tv", "periodo_linea_q8", "vts", "suelo", "r5", "shd", "svd", "shutmode", "lineas", "d8", "da", "dc")},
               "predicado_byte": pred, "imager_factor": imager["factor"]}
        # El predicado devuelve 1 si el byte es 0 (E25-18 §5, T052-A).
        p = 1 if pred == 0 else 0
        nat = productor(rec["tv"], rec["periodo_linea_q8"], rec["vts"], rec["suelo"], imager["factor"], p)
        row["nativo_emulado_con_parametros_reales"] = {"predicado": p, **nat}
        rows.append(row)
    out = ROOT / "analysis/e25-19/matriz.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    for r in rows:
        o, n = r["observado_record_a"], r["nativo_emulado_con_parametros_reales"]
        print(f"{r['velocidad']:>5} tv={o['tv']} obs: shd={o['shd']} svd={o['svd']} vts={o['vts']} r5={o['r5']} sm={o['shutmode']} | "
              f"nativo(p={n['predicado']}): lineas={n['lineas']} shd={n['shd']} svd={n['svd']} d8/da/dc={n['d8']}/{n['da']}/{n['dc']}")


if __name__ == "__main__":
    main()
