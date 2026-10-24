"""Actualiza los estados desde los tres firmwares, sin reutilizar resultados obsoletos."""
import json

from verify_s6xx import ROOT, audit


def main():
    results = audit()
    for result in results:
        path = ROOT / result["json"]
        data = json.loads(path.read_text())
        if "logger_dual" in data:
            data["logger_dual"] = None  # desconocido, no falso ni demostrado
        data["verification_status"] = result["verification_status"]
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "analysis/s6xx_verification_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"{len(results)} fichas actualizadas; ejecutar verify_s6xx.py para validar.")


if __name__ == "__main__":
    main()
