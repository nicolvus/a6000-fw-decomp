"""AE de av-cam hacia ObjCamera (scripts/gui/avcam/ae.py): disposición de los mensajes tipo 6 `0x2014`/`0x2023` según los conversores de `libObj`
(0x9ac048 y 0x9abe0c, §5.18 de docs/gui/g22-avcam-puente.md) y programa de exposición con luminancia de escena constante."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "avcam"))
import ae


def test_velocidad_0x2014_disposicion_del_conversor():
    m = ae.msg_velocidad(1, 125, (1, 4000), (30, 1), valido=True)
    assert m[:8] == struct.pack("<BBHI", 6, 0, 0x2014, 0)      # notificación espontánea: seq 0 (sin bit de respuesta)
    assert struct.unpack_from("<H", m, 0x08)[0] == 1 and struct.unpack_from("<I", m, 0x0C)[0] == 125   # SHUT_SPEED_NUMER/DENOM
    assert struct.unpack_from("<HxxI", m, 0x10) == (1, 4000)    # MIN_NUMER/DENOM
    assert struct.unpack_from("<HxxI", m, 0x18) == (30, 1)      # MAX_NUMER/DENOM
    assert m[0x20] == 1 and len(m) >= 0x23                      # SHUT_DATA_VALID, SHUT_SPEED_DEGREE en 0x21


def test_f_0x2023_disposicion_del_conversor():
    m = ae.msg_f(350, 350, 2000, 350, 2200, valido=True)
    assert m[:4] == struct.pack("<BBH", 6, 0, 0x2023)
    assert struct.unpack_from("<HHHHH", m, 0x08) == (350, 350, 2000, 350, 2200)   # FNO, CURRENT_MIN, CURRENT_MAX, MIN, MAX
    assert m[0x12] == 1


def test_programa_P_con_escena_constante_es_plausible_y_sigue_la_compensacion():
    e = ae.Escena(ev100=12.0)
    base = ae.programa(e, iso=100, ev_comp=0.0)
    assert 1 / 4000 <= base.t <= 1 / 15 and 3.5 <= base.f / 100 <= 22
    mas = ae.programa(e, iso=100, ev_comp=1.0)       # +1 EV: el doble de luz → tiempo (≈) el doble
    assert 1.7 < mas.t / base.t < 2.4
    alto = ae.programa(e, iso=400, ev_comp=0.0)      # ISO ×4 → tiempo ≈ ÷4
    assert 3.0 < base.t / alto.t < 5.2


def test_escena_oscura_sube_el_iso_automatico():
    p = ae.programa(ae.Escena(ev100=4.0), iso=None, ev_comp=0.0)
    assert p.iso > 100 and p.t <= 1 / 30
