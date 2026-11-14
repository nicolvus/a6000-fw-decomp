import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import live  # noqa: E402


def variables(env: str) -> dict[str, str]:
    return dict(t.split("=", 1) for t in env.split() if "=" in t)


def test_shimenv_por_defecto_trae_la_sd_emulada():
    v = variables(live.construye_shimenv(True, ""))
    for k in ("SDIMG", "SDSECT", "FRONTRM", "BKMULTIPTR", "INSHORT", "NULLMWF"):
        assert k in v, k
    assert v["SDSECT"] == "8388608"  # 4 GB / 512 B
    assert v["SKIPFN"].startswith("7fa3d4=0,") and "826ed0=0" in v["SKIPFN"]  # el SKIPFN base se amplía, no se duplica
    assert live.construye_shimenv(True, "").count("SKIPFN=") == 1


def test_shimenv_sin_sd_es_el_anterior():
    v = variables(live.construye_shimenv(False, ""))
    assert "SDIMG" not in v and "FRONTRM" not in v and "TABLE0" not in v
    assert v["SKIPFN"] == "7fa3d4=0"


def test_shimextra_manda_sobre_el_conjunto():
    assert variables(live.construye_shimenv(True, "FRONTRM=9"))["FRONTRM"] == "9"


def test_dial_inicial_2_iauto_plus_y_keyiniton_vacio():
    """§5.23: el dial se informa al activarse InputService (KEYINITON vacío) y con la posición medida 2 = iAUTO+ (vista rica)."""
    env = live.construye_shimenv(True)
    assert "KEYINIT=7000001:1:177,7025:2:27 " in env and "KEYINITON= " in env and "KEYINITAFTER=not_user_operation " in env
    assert live.DIAL_INICIAL == 2


def test_giro_automatico_del_dial_desactivado_por_defecto():
    """§5.24: el giro a P tras el arranque no es fiable (perfil z1); solo es opt-in."""
    assert live.MODO_TRAS_ARRANQUE is None  # solo con LIVE_MODO_TRAS=n en el entorno


def test_vista_de_grabacion_se_abre_con_el_modo_p():
    """§5.31: el segundo argumento de openView es el modo de grabación (medido: 3 = P)."""
    assert live.VISTA_REC == 3 and "OPENVIEWARG=3 " in live.construye_shimenv(True)


def test_quita_retira_variables_y_direcciones_de_skipfn():
    """§5.35: LIVE_QUITA (opt-in de diagnostico) permite medir sin un atajo concreto sin tocar el codigo."""
    env = live.construye_shimenv(True, quita="NULLMWF,SKIPFN:7fa3d4")
    assert "NULLMWF" not in env and "7fa3d4=0" not in env and "826ed0=0" in env
    assert "NULLMWF=1" in live.construye_shimenv(True)


def test_atajos_de_objcntmgr_sustituidos_por_senddbcommand():
    """§5.35: con SendDbCommand (0x826ed0) forzado a OK, onStarting crea de verdad 0x4b8, 0x4e8 y la tabla 0x117c: TABLE0 y los SKIPFN del componente de estado sobran."""
    env = live.construye_shimenv(True, quita="")
    assert "826ed0=0" in env and "TABLE0" not in env
    for a in ("81685a", "829d78", "829da0", "829de8", "829e70", "829eb8", "829f00", "829faa", "829fc0"):
        assert f"{a}=0" not in env
    assert "84569a=0" not in env and "84570e=0" not in env  # el aviso de temperatura ya no cae: el objeto existe
