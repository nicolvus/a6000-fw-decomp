"""E26-R22 — el mapa del BootROM nombra todas las funciones descubiertas y las constantes clave."""

import importlib.util
import struct
from pathlib import Path

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin")
B = 0xFFFF0000


def _map():
    spec = importlib.util.spec_from_file_location(
        "r22", "analysis/e26-recovery/r22_bootrom_map.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ninguna_funcion_descubierta_sin_nombre():
    m = _map()
    _, _, _, _, _, funcs = m.build()
    assert all(f in {B + a for a in m.NAMES} or f == B + 0x116 for f in funcs)
    assert len(m.NAMES) == 57


def test_reloj_de_4mhz_por_las_dos_variantes_del_parpadeo():
    """Temporizador: 0x1e8480/0x7a1200 ticks; delay en ms: 500/2000 ms ⇒ 4 ticks/µs."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

    d = ROM.read_bytes()
    words = {struct.unpack_from("<I", d, o)[0] for o in range(0, 0x1A80, 4)}
    assert {0x1E8480, 0x7A1200} <= words
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ops = {
        i.op_str.split("#")[-1]
        for a in (0xE28, 0xE4A, 0xE6A)
        for i in md.disasm(d[a : a + 4], B + a, 1)
    }
    assert ops == {"0x1f4", "0xfa", "0x7d0"}  # 500 ms, 250 ms y pausa de 2000 ms
    assert 0x1E8480 / 500 == 0x7A1200 / 2000 == 4000  # ticks por ms


def test_cadena_de_version():
    assert b"Musashi Loader1 Ver.01.00 Dec  2 2011 10:45:17" in ROM.read_bytes()
