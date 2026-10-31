"""E26-R34: emulación de `serial_entry` (`0xffff0fa0`) con todas las combinaciones de banderas."""

from pathlib import Path

import pytest

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin").read_bytes()
BASE = 0xFFFF0000

import sys

sys.path.insert(0, "analysis/e26-recovery")
from r33_serial_entry_flags import run


def b(a: int, n: int) -> bytes:
    return ROM[a - BASE : a - BASE + n]


def test_solo_dos_saltos_llegan_a_la_recepcion_ninguno_desde_el_tramo_de_error():
    """Confirma por bytes que no hay bucle de reintento dentro de `serial_entry`."""
    import capstone

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    saltos = []
    for i in md.disasm(ROM[0xFA0:0x1062], 0xFFFF0FA0):
        if i.mnemonic.startswith("b") and "#0x" in i.op_str:
            try:
                saltos.append((i.address, int(i.op_str.split("#")[1], 16)))
            except ValueError:
                pass
    hacia_recepcion = [a for a, t in saltos if t == 0xFFFF0FF2]
    assert hacia_recepcion == [0xFFFF0FB8, 0xFFFF1032]


def test_flag1_primera_lectura_1_salta_la_recepcion():
    assert b(0xFFFF0FC6, 2) == bytes.fromhex("0128")  # cmp r0, #1
    assert b(0xFFFF0FC8, 2) == bytes.fromhex("03d0")  # beq 0xfd2
    assert b(0xFFFF0FDA, 2) == bytes.fromhex(
        "37e0"
    )  # b 0x104c (jump_ram, sin rx_packet)
    sec, fin = run(get_flag0=0, get_flag1_seq=[1], rx_packet_seq=[0])
    assert fin == "jump_ram"
    assert not any(x.startswith("rx_packet") for x in sec)


def test_flag1_segunda_lectura_distinta_de_0_y_1_es_error_directo():
    assert b(0xFFFF0FCE, 2) == bytes.fromhex("40b9")  # cbnz r0, 0xfe2
    sec, fin = run(get_flag0=1, get_flag1_seq=[2, 2], rx_packet_seq=[0])
    assert fin == "error_led"
    assert not any(x.startswith(("get_flag0", "rx_packet")) for x in sec)


def test_get_flag0_distinto_de_0_es_error_antes_de_recibir():
    """Sentido opuesto al de `main` (R23): aquí `!=0` es el error, no `==0`."""
    assert b(0xFFFF0FE0, 2) == bytes.fromhex("18b3")  # cbz r0, 0x102a
    sec, fin = run(get_flag0=1, get_flag1_seq=[0, 0], rx_packet_seq=[0])
    assert fin == "error_led"
    assert not any(x.startswith("rx_packet") for x in sec)


def test_rx_packet_con_error_distinto_de_0x3001_propaga_su_propio_codigo():
    _sec, fin = run(get_flag0=0, get_flag1_seq=[0, 0], rx_packet_seq=[0x3005])
    assert fin == "error_led"


def test_rx_packet_0x3001_se_reescribe_a_0x1001():
    assert b(0xFFFF1008, 12) == bytes.fromhex("43f20100844205d108210220")
    _sec, fin = run(get_flag0=0, get_flag1_seq=[0, 0], rx_packet_seq=[0x3001])
    assert fin == "error_led"


def test_recepcion_aceptada_sin_flag1_es_error_no_reintento():
    """Corrige R23 §2: no hay bucle; `get_flag1()==0` tras aceptar un paquete es error 0x1001."""
    assert b(0xFFFF1026, 2) == bytes.fromhex("68b9")  # cbnz r0, 0x1044
    assert b(0xFFFF1028, 2) == bytes.fromhex("04e0")  # b 0x1034 (error), NO b 0xff2
    _sec, fin = run(get_flag0=0, get_flag1_seq=[0, 0, 0], rx_packet_seq=[0])
    assert fin == "error_led"


def test_recepcion_aceptada_con_flag1_fijado_llega_a_jump_ram():
    _sec, fin = run(get_flag0=0, get_flag1_seq=[0, 0, 1], rx_packet_seq=[0])
    assert fin == "jump_ram"


@pytest.mark.parametrize(
    "kw",
    [
        {"get_flag0": 0, "get_flag1_seq": [1], "rx_packet_seq": [0]},
        {"get_flag0": 0, "get_flag1_seq": [0, 0, 1], "rx_packet_seq": [0]},
    ],
)
def test_todos_los_caminos_a_jump_ram_coinciden_con_el_emulador_de_r20(kw):
    """`jump_ram` es terminal aquí igual que en `r20_bootrom_selector.py` (R20); no se
    reemulan sus rutinas internas (`load_payload`, etc.), solo el punto de llegada."""
    _, fin = run(**kw)
    assert fin == "jump_ram"
