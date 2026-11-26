import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import live


def test_im_elf_caido_es_arranque_fallido_de_inmediato():
    assert live.arranque_fallido("LIVE=/dev/vport0p1\nIMEXIT im_s 139\n", 40, 0, 240)


def test_sin_pantalla_pasado_el_limite_es_arranque_fallido():
    assert live.arranque_fallido("LIVE=/dev/vport0p1\n", 241, 0, 240)
    assert not live.arranque_fallido("LIVE=/dev/vport0p1\n", 200, 0, 240)


def test_con_osd_de_verdad_nunca_es_fallido():
    assert not live.arranque_fallido("LIVE=/dev/vport0p1\n", 900, live.LISTAS_OK, 240)
    assert not live.arranque_fallido("IMEXIT im_s 0\n", 900, 1400, 240)


def test_el_cuelgue_de_dos_listas_es_arranque_fallido():
    """G22-CUELGUE: el invitado que se cuelga SÍ pinta 1-2 fotogramas («2 listas», 0,0046 opacos) y luego no crece; darlo por
    arrancado deja la sesión inservible, así que pasado el límite cuenta como fallo y el vigilante reinicia."""
    assert live.arranque_fallido("LIVE=/dev/vport0p1\n", 241, 2, 240)
    assert not live.arranque_fallido("LIVE=/dev/vport0p1\n", 200, 2, 240)  # aún dentro del plazo: se le da tiempo


def test_autoguardado_no_antes_del_instante_del_arranque_lento():
    """Con CALMA la primera pantalla llega ≈ 60 s antes, pero guardar el estado entonces deja la restauración sin pantalla (medido 2 de 2;
    sin CALMA restaura en 7 s): el guardado sigue 20 s después de la primera pantalla y nunca antes de GUARDA_MIN s desde que arrancó QEMU."""
    assert live.plazo_guardado(1000.0, 1107.0) == 1000.0 + live.GUARDA_MIN  # primera pantalla temprana: espera al mínimo
    assert live.plazo_guardado(1000.0, 1200.0) == 1220.0  # primera pantalla tardía: 20 s después, como antes
