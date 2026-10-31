"""E26-R23 — cierre total del BootROM: todo paso de traza y código de error tiene un sitio emisor conocido."""

import json
from pathlib import Path

TRACE = Path("analysis/e26-recovery/r22-trace-steps.json")
ERRORS = Path("analysis/e26-recovery/r22-error-codes.json")


def test_todo_paso_de_traza_etapa_paso_esta_resuelto():
    data = json.loads(TRACE.read_text(encoding="utf-8"))
    assert len(data) == 109
    assert all(not k.startswith("-1:") and not k.endswith(":-1") for k in data)
    assert sum(len(v) for v in data.values()) == 111


def test_todo_codigo_de_error_documentado_tiene_emisor():
    data = json.loads(ERRORS.read_text(encoding="utf-8"))
    assert len(data) == 25
    esperados = {f"0x{c:x}" for c in list(range(0x1001, 0x100F)) if c != 0x1000}
    esperados |= {f"0x{c:x}" for c in range(0x2001, 0x2006)}
    esperados |= {f"0x{c:x}" for c in range(0x3001, 0x3007)}
    assert set(data) == esperados
    assert all(v for v in data.values())
