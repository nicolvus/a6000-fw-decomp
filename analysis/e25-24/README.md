# E25-24 — evidencia offline del selector EFCS / Electronic

Generado por `python -m scripts.e25_24.build_evidence --out analysis/e25-24`.
No contiene binarios parcheados; solo hashes, diferencias byte a byte, bytes de los
caves y la matriz de emulación.

| Archivo | Contenido |
|---|---|
| `evidence.json` | Manifiestos BIONZ/Darwin, diff, caves, regiones protegidas y emulación |
| `README.md` | Este índice |

Regenerar:

```bash
source .venv/bin/activate
python -m scripts.e25_24.build_evidence --out analysis/e25-24
python -m pytest -q tests/test_e25_24_selector.py
```

Informe: `docs/capture/e25-24b-implementacion-selector.md`.
Protocolo físico: `docs/capture/e25-24c-protocolo-fisico-selector.md`.
