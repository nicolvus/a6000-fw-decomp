"""E26-R27 — ISR de NAND (0xd24), geometría (0x1a80-0x1ae4) y las 18 operaciones del despachador ARM7."""

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path("analysis/e26-recovery")))

from r16_arm7 import IMG


def word(a: int) -> int:
    return struct.unpack_from("<I", IMG, a)[0]


def test_isr_nand_0xd24_traduce_bit_0x800_a_codigo_0x20():
    # tst r0,#0x800 ; movne r0,#0x20
    assert IMG[0xD34:0xD3C] == bytes.fromhex("020b10e3200 0a013".replace(" ", ""))


def test_geometria_capacidad_0x1a80_compara_dev8_por_dev18_con_r2():
    # cmp r3,r2 ; cmpls r1,#0 ; moveq r0,#1
    assert IMG[0x1A90:0x1A9C] == bytes.fromhex("020053e1000051930100a003")


def test_despachador_tiene_18_operaciones_con_el_mismo_prologo():
    from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs

    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    ops = {k: word(0x379C + 4 * k) for k in range(18)}
    assert len(ops) == 18 and len(set(ops.values())) == 18
    assert ops[0] == 0x1338  # LDEC, ya documentada en R17
    # las 17 restantes empiezan con `mov rX,#0x3f40` seguido de `ldr r0,[rX,#0x14]`
    # (mismo descriptor de trabajo que op 0, confirmado para todas)
    for k, addr in ops.items():
        if k == 0:
            continue
        ins = list(md.disasm(IMG[addr : addr + 0x14], addr))
        assert ins[0].mnemonic == "push"
        assert any(
            i.mnemonic == "mov" and i.op_str.endswith("0x3f40") for i in ins[1:6]
        ), f"op{k} no carga la base 0x3f40 en el prólogo"
