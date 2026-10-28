"""E25-18 — matriz de velocidades, diferencial original/candidata sobre StartExposure real, secuencia de 1 s y selección de VTS.

Salida: analysis/e25-18/{matriz,diferencial,secuencia_1s,hook}.json. Solo emulación de software (Unicorn); no toca la cámara.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import secuencia as S
import silent_plan as P

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/e25-18"
VEL = {"1/8000": 1 / 8000, "1/4000": 1 / 4000, "1/1000": 1 / 1000, "1/250": 1 / 250, "1/60": 1 / 60, "1/30": 1 / 30,
       "1/15": 1 / 15, "1/8": 1 / 8, "1/4": 0.25, "1/2": 0.5, "1 s": 1.0, "2 s": 2.0, "4 s": 4.0, "8 s": 8.0, "15 s": 15.0,
       "30 s": 30.0}
TODO = P.Capacidades(True, True, True)


def vts_por_cuadro(svd: int, d8: int, da: int, dc: int) -> list[int]:
    """Regla de 0x437b21b8 (bytes 0x437b2254..0x437b22be): cuadro 0 -> d8; cuadro == svd -> dc; resto -> da."""
    return [d8 if i == 0 else dc if i == svd else da for i in range(svd + 1)]


def matriz() -> dict:
    filas = {}
    for n, t in VEL.items():
        tv = P.tv_code(t)
        f: dict = {"tv": tv}
        for pred in (0, 1):
            nat = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, pred)
            f[f"nativo_p{pred}"] = nat
            f[f"vts_cuadros_p{pred}"] = vts_por_cuadro(nat["svd"], nat["d8"], nat["da"], nat["dc"])
        sin = P.planificar(tv, pred=1)
        con = P.planificar(tv, pred=1, caps=TODO)
        pl = con
        assert isinstance(pl, P.Plan) and isinstance(sin, (P.Plan, P.Rechazo))
        f["sin_capacidades"] = {"ok": isinstance(sin, P.Plan), "motivo": getattr(sin, "motivo", None)}
        f["plan"] = {k: getattr(pl, k) for k in ("lineas", "shd", "svd", "vts_inicial", "vts_intermedio", "vts_final", "ruta",
                                                  "requiere", "exposicion_us")}
        f["error_pct"] = round((pl.exposicion_us / (t * 1e6) - 1) * 100, 2)
        try:
            f["c3b_r5"] = P.c3b_r5(pl.lineas)
        except ValueError as ex:
            f["c3b_r5"] = None
            f["c3b_rechazo"] = str(ex)
        # coincidencia con C3-B donde C3-B es válido
        f["c3b_igual_plan"] = f["c3b_r5"] == pl.shd if f["c3b_r5"] is not None else None
        # normalización algebraica contra el productor real con predicado 0
        nn = P.normalizar(f["nativo_p1"], P.VTS_MEDIDO, 1)
        f["normaliza_igual_p0"] = nn is not None and all(nn[k] == f["nativo_p0"][k] for k in ("shd", "svd", "lineas"))
        filas[n] = f
    return filas


def _cap(nat: dict, v504: int, v740: int, shutmode: int | None = None, x38: int = 0) -> dict:
    return {0x64C: (4, nat["shd"]), 0x650: (2, nat["svd"]), 0x652: (2, nat["spl"]), 0x654: (1, nat["sint"]),
            0x655: (1, nat["shutmode"] if shutmode is None else shutmode), 0x504: (4, v504), 0x740: (4, v740), 0x4B9C: (4, 0),
            0x12F8: (2, x38), 0x56C: (4, 100)}


def diferencial() -> list[dict]:
    """Original (plan nativo, predicado 1) frente a candidata (hook en 0x438c82fe escribe el plan normalizado)."""
    res = []
    for n in ("1/8000", "1/4000", "1/1000", "1/250", "1/60", "1/30", "1/15", "1 s", "30 s"):
        tv = P.tv_code(VEL[n])
        nat = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 1)
        plan = P.planificar(tv, pred=1, caps=TODO)
        assert isinstance(plan, P.Plan)
        for v504 in (0, 1):
            for v740 in (0, 1):
                ori = S.start_exposure(_cap(nat, v504, v740))

                def hook(uc, plan=plan):
                    uc.mem_write(S.CAP + 0x64C, struct.pack("<I", plan.shd))
                    uc.mem_write(S.CAP + 0x650, struct.pack("<H", plan.svd))
                can = S.start_exposure(_cap(nat, v504, v740), hook=(0x438C82FE, hook))
                dif = [hex(i) for i in range(0x5000) if ori["mem"][i] != can["mem"][i]]
                reg_o = S.setexposure(ori["shd_a_SetExposure"], ori["svd_a_SetExposure"])["decod"]
                reg_c = S.setexposure(can["shd_a_SetExposure"], can["svd_a_SetExposure"])["decod"]
                res.append({"vel": n, "cap504": v504, "cap740": v740, "original": {k: ori[k] for k in (
                    "shd_a_SetExposure", "svd_a_SetExposure", "cap650_final", "cap73b")} | {"registros": reg_o},
                    "candidata": {k: can[k] for k in ("shd_a_SetExposure", "svd_a_SetExposure", "cap650_final", "cap73b")}
                    | {"registros": reg_c},
                    "misma_secuencia_de_llamadas": ori["llamadas"] == can["llamadas"], "llamadas": can["llamadas"],
                    "bytes_distintos_en_cap": dif})
    return res


def hook_sitio() -> dict:
    """Condiciones del punto 0x438c82fe: orden frente a cap+0x504, restauración de svd y cap+0x73b según ShutMode."""
    tv = P.tv_code(1.0)
    nat = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 0)           # 1 s: shd 1, svd 14

    def escribe(svd):
        return lambda uc: uc.mem_write(S.CAP + 0x650, struct.pack("<H", svd))

    out: dict = {"plan_1s": {k: nat[k] for k in ("shd", "svd")}}
    sin = S.start_exposure(_cap(nat, 1, 1))
    out["cap504_1_sin_hook"] = {"svd_a_SetExposure": sin["svd_a_SetExposure"], "cap650_final": sin["cap650_final"]}
    con = S.start_exposure(_cap(nat, 1, 1), hook=(0x438C82FE, escribe(14)))
    out["cap504_1_hook_escribe_svd14"] = {"svd_a_SetExposure": con["svd_a_SetExposure"], "cap650_final": con["cap650_final"]}
    ant = S.start_exposure(_cap(nat, 1, 1), hook=(0x438C82A0, escribe(14)))
    out["cap504_1_hook_en_0x438c82a0"] = {"svd_a_SetExposure": ant["svd_a_SetExposure"], "cap650_final": ant["cap650_final"]}
    z = S.start_exposure(_cap(nat, 0, 0))
    out["cap740_0"] = {"cap650_final": z["cap650_final"], "svd_a_SetExposure": z["svd_a_SetExposure"]}
    # cap+0x73b: 0x43b1e520 con cfg=0x0010 y [cap+0x12f8]=0x0008 (≤ cfg)
    for modo in (0, 3):
        r = S.start_exposure(_cap(nat, 0, 1, shutmode=modo, x38=8), cfg_u16=0x10)
        out[f"cap73b_shutmode{modo}"] = r["cap73b"]
    # un hook que fuerza ShutMode 0 tras 0x43b1e520 no cambia cap+0x73b calculado con el ShutMode nativo 3
    f0 = S.start_exposure(_cap(nat, 0, 1, shutmode=3, x38=8), cfg_u16=0x10,
                          hook=(0x438C82FE, lambda uc: uc.mem_write(S.CAP + 0x655, b"\0")))
    out["cap73b_nativo3_hook_en_82fe_fuerza0"] = {"cap73b": f0["cap73b"], "shutmode_a_SetExposure": f0["shutmode_a_SetExposure"],
                                                  "cap655_final": f0["cap655_final"]}
    f1 = S.start_exposure(_cap(nat, 0, 1, shutmode=3, x38=8), cfg_u16=0x10,
                          hook=(0x438C82A0, lambda uc: uc.mem_write(S.CAP + 0x655, b"\0")))
    out["cap73b_nativo3_hook_en_82a0_fuerza0"] = {"cap73b": f1["cap73b"], "shutmode_a_SetExposure": f1["shutmode_a_SetExposure"]}
    # bloque forzado 0x43a12c64 = 2/3 sobrescribe cap+0x64c..0x655 antes de 0x438c82fe
    fz = S.start_exposure(_cap(nat, 0, 1), forzado=2)
    out["forzado2"] = {"shd": fz["shd_a_SetExposure"], "svd": fz["svd_a_SetExposure"], "shutmode": fz["shutmode_a_SetExposure"]}
    return out


def secuencia_1s() -> dict:
    nat = P.productor(P.tv_code(1.0), P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 0)
    r = S.start_exposure(_cap(nat, 0, 1))
    r.pop("mem")
    r["registros_sensor"] = S.setexposure(r["shd_a_SetExposure"], r["svd_a_SetExposure"])
    r["vts_por_cuadro"] = vts_por_cuadro(nat["svd"], nat["d8"], nat["da"], nat["dc"])
    return r


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    m, d, h, s = matriz(), diferencial(), hook_sitio(), secuencia_1s()
    for nombre, obj in (("matriz", m), ("diferencial", d), ("hook", h), ("secuencia_1s", s)):
        (OUT / f"{nombre}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False))
    for n, f in m.items():
        p = f["plan"]
        print(f"{n:7s} L={p['lineas']:7d} shd={p['shd']:5d} svd={p['svd']:3d} vts0={p['vts_inicial']:5d} err={f['error_pct']:+.2f}% "
              f"{p['ruta']:6s} c3b={f['c3b_r5']} norm={f['normaliza_igual_p0']}")
    print(json.dumps(h, indent=0)[:1800])
    print(sum(1 for x in d if not x["misma_secuencia_de_llamadas"]), "diferencias de secuencia;",
          max(len(x["bytes_distintos_en_cap"]) for x in d), "bytes máx. distintos en cap")
