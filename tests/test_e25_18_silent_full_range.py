"""E25-18 — modelo de plan Silent de todo el rango, diferencial sobre StartExposure real y comprobaciones de bytes (offline)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in ("scripts/e25_18", "scripts/e25_17", "scripts/e25_16"):
    sys.path.insert(0, str(ROOT / p))

pytest.importorskip("unicorn")
pytest.importorskip("capstone")
import matriz as M
import secuencia as S
import silent_plan as P
from emu_core import FW

pytestmark = pytest.mark.skipif(not FW.exists(), reason="firmware fw321 no disponible")

TODO = P.Capacidades(True, True, True)
EVID = json.loads((ROOT / "analysis/e25-18/evidencia.json").read_text()) if FW.exists() else {}
REPORT = ROOT / "docs/capture/e25-18-integracion-silent-todas-velocidades.md"
RAPIDAS = ["1/8000", "1/4000", "1/1000", "1/250", "1/60", "1/30"]


def test_evidencia_bytes_sin_fallos():
    assert EVID["fallos"] == 0 and len(EVID["sitios"]) >= 35


@pytest.mark.parametrize("n", list(M.VEL))
def test_normalizacion_equivale_al_productor_con_predicado_0(n):
    tv = P.tv_code(M.VEL[n])
    n0 = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 0)
    n1 = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 1)
    assert n1["shd"] == n0["shd"] + P.VTS_MEDIDO and n1["svd"] == n0["svd"] + 1 and n1["lineas"] == n0["lineas"]
    nn = P.normalizar(n1, P.VTS_MEDIDO, 1)
    assert all(nn[k] == n0[k] for k in ("shd", "svd", "lineas"))
    assert n0["d8"] + n0["svd"] * P.VTS_MEDIDO == n0["lineas"] + n0["shd"]


@pytest.mark.parametrize("n", RAPIDAS)
def test_rapidas_coinciden_con_c3b_y_no_exigen_capacidades(n):
    pl = P.planificar(P.tv_code(M.VEL[n]), pred=1)
    assert isinstance(pl, P.Plan) and pl.ruta == "rapida" and pl.svd == 0 and pl.requiere == ()
    assert pl.shd == P.c3b_r5(pl.lineas)
    assert abs(pl.exposicion_us / (M.VEL[n] * 1e6) - 1) < 0.05            # objetivo ±5 %


@pytest.mark.parametrize("n", [k for k in M.VEL if k not in RAPIDAS])
def test_largas_se_rechazan_sin_capacidad_y_c3b_no_las_representa(n):
    tv = P.tv_code(M.VEL[n])
    r = P.planificar(tv, pred=1)
    assert isinstance(r, P.Rechazo) and "capacidad no demostrada" in r.motivo
    c = r.candidato
    assert c.shd >= 1 and 0 <= c.svd <= P.SVD_MAX                          # nunca r5 negativo, saturado o truncado
    with pytest.raises(ValueError):
        P.c3b_r5(c.lineas)
    pl = P.planificar(tv, pred=1, caps=TODO)
    assert isinstance(pl, P.Plan) and pl.lineas_totales - pl.shd == pl.lineas


def test_valores_clave_de_e25_17():
    f = {n: P.planificar(P.tv_code(M.VEL[n]), pred=1, caps=TODO) for n in ("1/15", "1/8", "1 s", "30 s")}
    assert (f["1/15"].shd, f["1/15"].svd, f["1/15"].vts_inicial) == (1, 0, 4389)
    assert (f["1/8"].svd, f["1/8"].vts_inicial) == (0, 8225)
    assert (f["1 s"].svd, f["1 s"].vts_inicial) == (14, 6727)
    assert (f["30 s"].svd, f["30 s"].vts_inicial) == (472, 7737)
    assert abs(f["30 s"].exposicion_us / 30e6 - 1) < 0.05                  # Tv del firmware ≈ 30,39 s, no 30 s exactos


def test_rechazos_limpios():
    tv = P.tv_code(1 / 250)
    assert isinstance(P.planificar(tv, bulb=True), P.Rechazo)
    assert isinstance(P.planificar(tv, modo="liveview"), P.Rechazo)
    assert isinstance(P.planificar(tv, periodo_q8=3000), P.Rechazo)
    assert isinstance(P.planificar(tv, vts=4266), P.Rechazo)
    assert isinstance(P.planificar(tv, pred=2), P.Rechazo)
    assert P.normalizar({"shd": 100, "svd": 0}, 4219, 1) is None           # estructura inconsistente
    assert P.normalizar({"shd": 100, "svd": 1}, 4219, 1) is None


def test_vts_por_cuadro_suma_total():
    for n in M.VEL:
        nat = P.productor(P.tv_code(M.VEL[n]), P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 0)
        v = M.vts_por_cuadro(nat["svd"], nat["d8"], nat["da"], nat["dc"])
        assert sum(v) == nat["lineas"] + nat["shd"] and len(v) == nat["svd"] + 1


@pytest.mark.parametrize("shd,svd", [(1, 14), (1, 472), (2025, 0), (4211, 0), (16383, 4095)])
def test_setexposure_real_reparte_svd_y_shd_en_ID3_ID8(shd, svd):
    r = S.setexposure(shd, svd)
    assert r["decod"] == {"svd": svd, "shd": shd, "spl": 0} and r["obj_3a8_svd"] == svd


def test_setexposure_descarta_bits_altos():
    r = S.setexposure(0xFFFF, 0xFFFF)
    assert r["decod"]["svd"] == 0xFFF and r["decod"]["shd"] == 0x3FFF


def test_diferencial_original_candidata():
    d = M.diferencial()
    assert d and all(x["misma_secuencia_de_llamadas"] for x in d)
    for x in d:
        assert set(x["bytes_distintos_en_cap"]) <= {"0x64c", "0x64d"}      # solo cambia shd en cap+0x64c
        tv = P.tv_code(M.VEL[x["vel"]])
        pl = P.planificar(tv, pred=1, caps=TODO)
        assert x["candidata"]["registros"]["shd"] == pl.shd and x["candidata"]["registros"]["svd"] == pl.svd
        assert x["candidata"]["cap650_final"] == x["original"]["cap650_final"]   # el svd del host no se altera
        assert x["candidata"]["cap73b"] == x["original"]["cap73b"]


def test_orden_del_enganche_0x438c82fe():
    h = M.hook_sitio()
    assert h["cap504_1_sin_hook"]["svd_a_SetExposure"] == 0                    # E25-17: cap+0x504 == 1 anula el svd
    assert h["cap504_1_hook_escribe_svd14"]["svd_a_SetExposure"] == 14         # tras 0x82f0: el hook prevalece
    assert h["cap504_1_hook_en_0x438c82a0"]["svd_a_SetExposure"] == 0          # antes de 0x82f0: se anularía
    assert h["cap740_0"]["cap650_final"] == 0                                  # 0x438c83c4 anula el contador del host
    assert h["cap73b_nativo3_hook_en_82fe_fuerza0"]["cap73b"] == 1             # 0x43b1e520 ya calculó con el ShutMode nativo
    assert h["cap73b_nativo3_hook_en_82a0_fuerza0"]["cap73b"] == 0             # un hook anterior cambiaría esa condición
    assert h["forzado2"]["shd"] == 2                                           # bloque forzado: sobrescribe antes del hook


def test_secuencia_1s_completa():
    s = M.secuencia_1s()
    assert s["llamadas"][s["llamadas"].index("SetExposure"):][:4] == ["SetExposure", "imager", "SetRead", "imager"] or \
        [c for c in s["llamadas"] if c in ("SetExposure", "SetRead", "SSB", "Execute")] == ["SetExposure", "SetRead", "SSB", "Execute"]
    assert s["svd_a_SetExposure"] == 14 and s["registros_sensor"]["decod"]["svd"] == 14
    assert s["vts_por_cuadro"][0] == 6727 and set(s["vts_por_cuadro"][1:]) == {4219} and len(s["vts_por_cuadro"]) == 15


def test_sumidero_vts_solo_escritor_en_host():
    c = json.loads((ROOT / "analysis/e25-18/consumidores_vts_host.json").read_text())
    assert {x["acceso"] for x in c} == {"0x436ef62c"}                          # único acceso literal a 0x43e849c0+0x40


def test_informe_y_entregables():
    txt = REPORT.read_text()
    for k in ("## 13. Veredictos", "Decisión final: C", "0x438c82fe", "E25-19", "0x438d0e64"):
        assert k in txt
    for f in ("scripts/e25_18/silent_plan.py", "scripts/e25_18/secuencia.py", "scripts/e25_18/matriz.py",
              "analysis/e25-18/matriz.json", "analysis/e25-18/diferencial.json", "analysis/e25-18/hook.json"):
        assert (ROOT / f).exists(), f
