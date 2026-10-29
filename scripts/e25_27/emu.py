"""E25-27 — emulación integrada EFCS / Electronic (offline, sin cámara).

Encadena los tres componentes ya verificados sobre las imágenes integradas:

    selector BIONZ -> pkt[0x0e] -> compuertas Darwin -> C3-B -> SetExposure

No modela el IMX210 ni el movimiento físico.  Comprueba que la modalidad de una
captura queda congelada, que EFCS es idéntico al original y que Electronic
produce los parámetros normalizados de C3-B.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for path in ("scripts", "scripts/e25_18", "scripts/e25_16", "scripts/e25_17"):
    sys.path.insert(0, str(ROOT / path))

from e25_24 import emu as E24
from e25_24.selector import InvalidSelection, Mode, Selector
from e25_25.channel import ModalityChannel
from e25_26 import emu as E26

VTS = E26.VTS
RAPIDAS = {"1/8000": 1 / 8000, "1/4000": 1 / 4000, "1/1000": 1 / 1000,
           "1/250": 1 / 250, "1/125": 1 / 125, "1/60": 1 / 60, "1/30": 1 / 30}


def run(bionz: bytes, darwin: bytes, *, field: int, r1: int = 1, shd: int = 8422,
        svd: int = 1, shutmode: int = 3, vts: int = VTS) -> dict[str, Any]:
    """Un disparo completo: selector -> paquete -> Darwin -> C3-B -> SetExposure."""
    from e25_24.selector import mode_from_field

    mode_from_field(field)  # 0/1; cualquier otro valor se rechaza antes de emular
    sel = E24.run_bionz_selector(bionz, r1, field)
    flag = sel.packet[0x0E]
    coil = E24.run_darwin(darwin, 0x20C74, flag)
    motor = E24.run_darwin(darwin, 0x1FE66, flag)
    exp = E26.run(bionz, flag=flag, shd=shd, svd=svd, shutmode=shutmode, vts=vts)
    return {
        "field": field,
        "r1": r1,
        "packet_flag": flag,
        "packet": sel.packet.hex(),
        "branch": hex(sel.stopped_at),
        "r0_selector": sel.r0,
        "coil": coil,
        "motor": motor,
        "shd_SetExposure": exp["shd_a_SetExposure"],
        "svd_SetExposure": exp["svd_a_SetExposure"],
        "shutmode_SetExposure": exp["shutmode_a_SetExposure"],
        "shd_native": exp["shd_a_SetExposure"] if flag == 0 else shd,
        "cap650_final": exp["cap_650_final"],
        "cap655_final": exp["cap_655_final"],
        "cap73b": exp["cap73b"],
        "param_bytes": exp["param_bytes"],
    }


def matrix(bionz: bytes, darwin: bytes, original_bionz: bytes) -> dict[str, Any]:
    """Matriz integrada: modos, ramas, alternancia, errores y velocidades."""
    out: dict[str, Any] = {}

    # EFCS: las dos ramas del constructor y el plan nativo intacto.
    out["efcs"] = [run(bionz, darwin, field=0, r1=r1) for r1 in (1, 0)]
    out["efcs_baseline"] = [
        run(original_bionz, darwin, field=0, r1=r1) for r1 in (1, 0)
    ]
    out["efcs_identical"] = all(
        (a["coil"], a["motor"], a["shd_SetExposure"], a["svd_SetExposure"],
         a["shutmode_SetExposure"], a["cap650_final"], a["cap655_final"])
        == (b["coil"], b["motor"], b["shd_SetExposure"], b["svd_SetExposure"],
            b["shutmode_SetExposure"], b["cap650_final"], b["cap655_final"])
        for a, b in zip(out["efcs"], out["efcs_baseline"])
    )

    # Electronic: plan nativo con predicado 1 -> 4203/0/0 y compuertas a 0.
    out["electronic"] = [run(bionz, darwin, field=1, r1=r1) for r1 in (1, 0)]
    out["electronic_normalized"] = all(
        (r["packet_flag"], r["coil"], r["motor"], r["shd_SetExposure"],
         r["svd_SetExposure"], r["shutmode_SetExposure"])
        == (1, 0, 0, 4203, 0, 0)
        for r in out["electronic"]
    )

    # Predicado 0 (plan ya normalizado): no se resta VTS dos veces.
    out["electronic_pred0"] = run(bionz, darwin, field=1, shd=4203, svd=0)
    out["electronic_pred0_ok"] = (
        out["electronic_pred0"]["shd_SetExposure"] == 4203
        and out["electronic_pred0"]["svd_SetExposure"] == 0
        and out["electronic_pred0"]["shutmode_SetExposure"] == 0
    )

    # Alternancia con congelación por captura: cambiar el selector después de
    # empezar no altera el paquete ya emitido.
    from e25_24.selector import TransitionRejected

    selector = Selector()
    channel = ModalityChannel()
    sequence = []
    pairs = ((0x2B4, 0x2B5), (0x2B5, 0x2B4), (0x2B4, 0x2B5),
             (0x2B5, 0x2B4), (0x2B4, 0x2B5))
    for model, next_model in pairs:
        mode = selector.select(model)
        channel.select(0 if mode is Mode.EFCS else 1)
        ticket = selector.begin_capture()
        packet = channel.begin_capture()
        rejected = False
        try:
            selector.select(next_model)      # cambio durante la captura: prohibido
        except TransitionRejected:
            rejected = True
        # El campo global puede cambiar; el paquete de esta captura no.
        channel.select(0 if next_model == 0x2B4 else 1)
        active = channel.capture
        assert active is not None
        frozen = packet.flag == ticket.packet_flag == active.flag
        selector.end_capture()
        channel.end_capture()
        selector.select(next_model)
        sequence.append({
            "mode": mode.value,
            "ticket_flag": ticket.packet_flag,
            "packet_flag": packet.flag,
            "change_during_capture_rejected": rejected,
            "frozen": frozen,
        })
    out["alternation"] = sequence
    out["alternation_ok"] = (
        all(item["frozen"] and item["change_during_capture_rejected"] for item in sequence)
        and [item["packet_flag"] for item in sequence] == [0, 1, 0, 1, 0]
    )

    # Errores: VTS 0, underflow, ruta larga y modalidad inválida.
    out["errors"] = {
        "zero_vts": run(bionz, darwin, field=1, vts=0),
        "underflow": run(bionz, darwin, field=1, shd=100, svd=1),
        "long_route": run(bionz, darwin, field=1, shd=1, svd=2),
    }
    out["errors_ok"] = (
        out["errors"]["zero_vts"]["shd_SetExposure"] == 8422
        and out["errors"]["underflow"]["shd_SetExposure"] == 100
        and out["errors"]["long_route"]["svd_SetExposure"] == 2
        and out["errors"]["long_route"]["shutmode_SetExposure"] == 3
    )
    try:
        run(bionz, darwin, field=2)
    except InvalidSelection as exc:  # el selector debe rechazar el valor
        out["invalid_field"] = type(exc).__name__
    else:
        out["invalid_field"] = None
    out["invalid_field_ok"] = out["invalid_field"] is not None

    # Matriz de velocidades rápidas (misma tabla que E25-26).
    import silent_plan as P  # type: ignore[import-not-found]

    speeds: dict[str, Any] = {}
    for name, seconds in RAPIDAS.items():
        tv = P.tv_code(seconds)
        native = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 1)
        r = run(bionz, darwin, field=1, shd=native["shd"], svd=native["svd"], shutmode=3)
        expected = native["shd"] - P.VTS_MEDIDO if native["svd"] == 1 else native["shd"]
        speeds[name] = {
            "tv_code": tv,
            "vts": P.VTS_MEDIDO,
            "period_q8": P.PERIODO_Q8,
            "native": native,
            "electronic": {
                "shd": r["shd_SetExposure"],
                "svd": r["svd_SetExposure"],
                "shutmode": r["shutmode_SetExposure"],
                "r5": P.VTS_MEDIDO - native["lineas"],
                "expected_shd": expected,
                "ok": r["shd_SetExposure"] == expected
                and r["svd_SetExposure"] == 0
                and r["shutmode_SetExposure"] == 0,
            },
            "efcs": {
                "shd": run(bionz, darwin, field=0, shd=native["shd"], svd=native["svd"])["shd_SetExposure"],
                "note": "plan nativo sin cambios",
            },
        }
    out["speeds"] = speeds
    out["speeds_ok"] = all(v["electronic"]["ok"] for v in speeds.values())
    out["cap73b"] = {"value": out["electronic"][0]["cap73b"],
                     "note": "calculado por 0x43b1e520 antes del enganche con ShutMode nativo; "
                             "C3-B no lo modifica (E25-28)"}
    out["all_ok"] = all(out[k] for k in (
        "efcs_identical", "electronic_normalized", "electronic_pred0_ok",
        "alternation_ok", "errors_ok", "invalid_field_ok", "speeds_ok"))
    return out
