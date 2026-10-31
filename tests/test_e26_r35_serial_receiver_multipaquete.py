"""E26-R35: `serial_receiver`/`rx_packet` (`0xffff0876`) puede recibir varios paquetes por llamada."""

import struct
from pathlib import Path

import capstone

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin").read_bytes()
BASE = 0xFFFF0000


def b(a: int, n: int) -> bytes:
    return ROM[a - BASE : a - BASE + n]


def lit(pc_addr: int, imm: int) -> int:
    """Resuelve un `ldr r,[pc,#imm]` Thumb: literal en align4(pc_addr+4)+imm."""
    file_off = ((pc_addr + 4) & ~3) + imm - BASE
    return struct.unpack_from("<I", ROM, file_off)[0]


def test_solo_dos_saltos_llegan_al_punto_de_resincronizacion():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    saltos = []
    for a0, b0 in ((0x876, 0x944), (0x9A0, 0xBD4)):
        for i in md.disasm(ROM[a0:b0], BASE + a0):
            if i.mnemonic.startswith("b") and "#0x" in i.op_str:
                try:
                    saltos.append((i.address, int(i.op_str.rsplit("#", 1)[1], 16)))
                except ValueError:
                    pass
    hacia_resync = sorted(a for a, t in saltos if t == 0xFFFF089C)
    assert hacia_resync == [0xFFFF0B90, 0xFFFF0B96]


def test_tipo_0_guarda_el_valor_y_activa_get_flag0():
    assert b(0xFFFF0B6C, 4) == bytes.fromhex(
        "049808b3"
    )  # ldr r0,[sp,0x10]; cbz r0,0xbb4
    assert b(0xFFFF0BB4, 14) == bytes.fromhex(
        "0899039a0a6001210f4a1160e0e7"
    )  # motivo=valor; [lit]=1; b 0xb84
    assert lit(0xFFFF0BBC, 0x3C) == 0xC0010004  # get_flag0()


def test_tipo_0xffff_guarda_el_destino_de_salto_y_activa_get_flag1():
    assert b(0xFFFF0B70, 8) == bytes.fromhex("a0f57f42ff3a05d1")  # tipo == 0xffff?
    assert b(0xFFFF0B78, 6) == bytes.fromhex(
        "1f4a0399d160"
    )  # [0xc0005000+0xc] = direccion
    assert b(0xFFFF0B7E, 6) == bytes.fromhex("01221e494a60")  # [lit+4] = 1
    assert lit(0xFFFF0B78, 0x7C) == 0xC0005000  # base del destino de salto
    assert lit(0xFFFF0B80, 0x78) == 0xC0010004  # base de get_flag1() (+4)


def test_primer_paquete_siempre_fuerza_otra_vuelta_sea_el_tipo_que_sea():
    """`fp==0` -> `sl=tipo; fp=1; b 0x89c` incondicional, no hay salida en el primer paquete."""
    assert b(0xFFFF0B84, 12) == bytes.fromhex(
        "bbf1000f04bf82464ff0010b"
    )  # cmp fp,#0; itt eq; sl=r0; fp=1
    assert b(0xFFFF0B90, 4) == bytes.fromhex(
        "3ff484ae"
    )  # beq.w 0x89c (incondicional si fp==0)


def test_tipo_distinto_del_primero_tambien_vuelve_a_recibir():
    assert b(0xFFFF0B94, 6) == bytes.fromhex("82457ff481ae")  # cmp sl,r0; bne.w 0x89c


def test_chequeo_final_es_un_or_no_exige_el_tipo_salto():
    """Corrige una lectura propia de esta sesión: no hace falta un paquete 0xFFFF, basta
    con que algun paquete haya puesto a 1 `[0xc0010004]` O `[0xc0010008]` (get_flag0/1)."""
    assert b(0xFFFF0B9A, 10) == bytes.fromhex("1848d0e9001008430ed0")
    assert (
        lit(0xFFFF0B9A, 0x60) == 0xC0010004
    )  # ldrd r1,r0,[r0] lee [0xc0010004] y [0xc0010008]


def test_get_flag0_y_get_flag1_comparten_la_unica_otra_copia_del_literal_en_la_rom():
    """Ninguna otra parte del ROM escribe en `[0xc0010004]`/`[0xc0010008]` salvo esta funcion
    y las rutinas `get_flag0`/`get_flag1` (que solo leen)."""
    objetivo = {0xC0010004}
    copias = [
        off
        for off in range(0, len(ROM) - 3, 4)
        if struct.unpack_from("<I", ROM, off)[0] in objetivo
    ]
    assert copias == [0x948, 0xBFC]
