#!/usr/bin/env python3
"""S52 (Agente A): hechos VERIFICADOS sobre captura+0x748, clase de obturación y CAIF (A7S 3.20 vs A6000 3.21).

Comprueba con capstone (Thumb-2) sobre las copias de entrada de work/claude/input/ (base 0x43541000) y las ROM Darwin
(base 0x4200). Uso: ~/.venvs/re/bin/python -I work/claude/tests/test_s52_curtain_facts.py
"""
import hashlib
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[3]
INP = ROOT / 'work/claude/input'
FW = ROOT / 'firmware/extracted'
B = 0x43541000
SHA = {'a7s': 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e',
       'a6000': 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9'}
BIN = {k: (INP / f'{k}-av-cam.bin').read_bytes() for k in SHA}
for k, h in SHA.items():
    assert hashlib.sha256(BIN[k]).hexdigest() == h, f'hash {k}'
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def ins(fw, addr, n=1, base=B, cs=CS):
    """n instrucciones desde addr como lista de (dir, 'mnem ops')."""
    d = BIN[fw] if isinstance(fw, str) else fw
    out = [(i.address, f'{i.mnemonic} {i.op_str}') for i in cs.disasm(d[addr - base:addr - base + 4 * n + 8], addr)]
    return out[:n]


def at(fw, addr, text, **kw):
    got = ins(fw, addr, **kw)[0]
    assert got[0] == addr and got[1] == text, f'{fw} {addr:#x}: {got[1]!r} != {text!r}'


def seq(fw, addr, texts, **kw):
    got = ins(fw, addr, len(texts), **kw)
    assert [t for _, t in got] == texts, f'{fw} {addr:#x}:\n{got}\n!=\n{texts}'


def u32(fw, a):
    return struct.unpack_from('<I', BIN[fw], a - B)[0]


def pic(fw, ldr, add):
    """valor de `ldr rX,[pc,#i]` (T1/T2) + `add rX,pc` en ADD."""
    h, h2 = struct.unpack_from('<HH', BIN[fw], ldr - B)
    if h >> 11 == 0b01001:  # T1
        lit = ((ldr + 4) & ~3) + (h & 0xff) * 4
    else:  # T2 ldr.w rt,[pc,#+imm12]
        assert h == 0xf8df, hex(h)
        lit = ((ldr + 4) & ~3) + (h2 & 0xfff)
    return (u32(fw, lit) + add + 4) & 0xffffffff


def t3_stores(fw, imm, op=0xf8c0):
    """direcciones de STR.W (T3, op 0xf8c0) con imm12 dado en todo el binario (alineación 2)."""
    d, res = BIN[fw], []
    for o in range(0, len(d) - 4, 2):
        h1, h2 = struct.unpack_from('<HH', d, o)
        if h1 & 0xfff0 == op and h2 & 0xfff == imm:
            res.append(B + o)
    return res


checks = []
def check(f):
    checks.append(f); return f


@check
def silent_writer_748():
    seq('a7s', 0x43813e94, ['bl #0x4379ec04', 'cmp r0, #2', 'str.w r0, [r4, #0x78c]', 'bne #0x43813ea6',
                            'movs r3, #1', 'str.w r3, [r4, #0x748]'])
    # único STR.W de 32 bits con imm 0x748 en todo av-cam A7S (strh/strb a +0x748 son otras estructuras)
    assert t3_stores('a7s', 0x748) == [0x43813ea2], t3_stores('a7s', 0x748)
    # A6000: el homólogo (copia +0x1bc/+0x1bd a +0x4d4/+0x4d5) no contiene la rama Silent
    seq('a6000', 0x43afa1c6, ['ldr r3, [r5, #8]', 'mov r0, r4', 'ldrb.w r2, [r3, #0x1bc]', 'strb.w r2, [r4, #0x4d4]'])


@check
def field_shift_748_is_a6000_740():
    # misma secuencia en ambos: A7S +0x748/+0x743/+0x750 == A6000 +0x740/+0x73b/+0x748 (desplazamiento +8)
    seq('a7s', 0x43b1d99a, ['ldr.w r3, [r4, #0x748]', 'cbnz r3, #0x43b1d9ac', 'ldrb.w r3, [r4, #0x743]'])
    seq('a6000', 0x43b1e7b0, ['ldr.w r3, [r4, #0x740]', 'cbnz r3, #0x43b1e7c2', 'ldrb.w r3, [r4, #0x73b]'])
    at('a7s', 0x43b1d9be, 'ldr.w r1, [r4, #0x748]'); at('a6000', 0x43b1e7d4, 'ldr.w r1, [r4, #0x740]')
    at('a7s', 0x438b74a4, 'str.w r3, [r4, #0x750]'); at('a6000', 0x438c7fc6, 'str.w r3, [r5, #0x748]')
    # A6000 no tiene STR.W a +0x740 en código de captura: solo dos en otra estructura (0x4373662a/0x43736738)
    assert t3_stores('a6000', 0x740) == [0x4373662a, 0x43736738], t3_stores('a6000', 0x740)


@check
def stage_c8_skips_ev3_wait_in_silent():
    seq('a7s', 0x438b1cb2, ['movs r1, #0xc8', 'mov r4, r0', 'bl #0x43ae826e', 'ldr.w r3, [r4, #0x748]',
                            'cbnz r3, #0x438b1cc6', 'mov r0, r4', 'bl #0x438be5f8'])
    seq('a6000', 0x438c28a2, ['movs r1, #0xc8', 'mov r4, r0', 'bl #0x43ae769a', 'mov r0, r4', 'bl #0x438d08e8'])


@check
def ev3_wait_helper():
    seq('a7s', 0x438be5f8, ['push {r0, r1, r2, r3, r4, lr}', 'ldrb.w r3, [r0, #0x757]', 'cbnz r3, #0x438be61e'])
    seq('a7s', 0x438be61e, ['add.w r3, r0, #0x4a00', 'movs r0, #3', 'ldr.w r1, [r3, #0xe8]', 'bl #0x4379b6ac'])
    seq('a6000', 0x438d08e8, ['ldrb.w r3, [r0, #0x74f]'])
    seq('a6000', 0x438d0910, ['add.w r3, r0, #0x4a00', 'movs r0, #3', 'ldr.w r1, [r3, #0xd8]', 'bl #0x437db9f0'])


@check
def stage_c9_adds_ev3_wait_in_silent():
    seq('a7s', 0x43b1c926, ['movs r1, #0xc9', 'mov r4, r0', 'bl #0x43ae826e', 'ldr.w r3, [r4, #0x748]',
                            'cmp r3, #1', 'bne #0x43b1c93c', 'mov r0, r4', 'bl #0x438be5f8', 'mov r0, r4',
                            'bl #0x438be6e8'])
    seq('a6000', 0x43b1d958, ['movs r1, #0xc9', 'mov r4, r0', 'bl #0x43ae769a', 'mov r0, r4', 'bl #0x438d0a2c'])
    # 0x438be6e8 / 0x438d0a2c envían evento CAIF 5 por el emisor (0x4379b590 / 0x437db858)
    seq('a7s', 0x438be6f4, ['movs r0, #5', 'ldr.w r1, [r3, #0xe8]', 'bl #0x4379b590'])


@check
def read_execute_skips_800000_wait():
    seq('a7s', 0x438b7268, ['ldr r3, [r6, #8]', 'cbz r3, #0x438b727c', 'ldr.w r3, [r4, #0x748]', 'cbnz r3, #0x438b727c',
                            'ldrb r3, [r6, #5]', 'cbnz r3, #0x438b727c', 'mov r0, r4', 'bl #0x438be76c'])
    seq('a6000', 0x438c7d56, ['ldrb r3, [r6, #5]', 'cbnz r3, #0x438c7d60', 'mov r0, r4', 'bl #0x438d0acc'])
    seq('a7s', 0x438be79e, ['mov.w r1, #0x800000', 'str r3, [sp]', 'movs r2, #1', 'add r3, sp, #0xc', 'movs r0, #0x13',
                            'add.w r4, r4, #0x4f00', 'bl #0x4355f0a0'])


@check
def capture_event_100_102_and_tail():
    seq('a7s', 0x438b7ec2, ['ldr.w r3, [r4, #0x748]', 'cbnz r3, #0x438b7ed8'])
    seq('a6000', 0x438c89bc, ['add.w r3, r4, #0x4b00', 'ldr.w r3, [r3, #0x9c]', 'cbnz r3, #0x438c89cc'])
    seq('a7s', 0x438b8054, ['ldr.w r3, [r4, #0x748]', 'cbnz r3, #0x438b8078', 'ldrb.w r3, [r4, #0x743]'])
    seq('a6000', 0x438c8b4e, ['ldrb.w r3, [r4, #0x73b]', 'cbz r3, #0x438c8b5c'])
    at('a6000', 0x438c8b5e, 'bl #0x43b1e474'); at('a7s', 0x438b806a, 'bl #0x43b1d5de')


@check
def caif_packet_silent_bits():
    # +0x12 = ((cap+0x78c)==2)<<5 | (r8[0]==1)
    seq('a7s', 0x4386329a, ['ldr.w r2, [r6, #0x76c]', 'sub.w r1, r2, #2', 'rsbs r2, r1, #0', 'adc.w r2, r2, r1',
                            'ldrb.w r1, [r8]', 'lsls r2, r2, #5', 'cmp r1, #1', 'it eq', 'addeq r2, #1',
                            'strb r2, [r4, #0x12]'])
    # +0xd: componente <<6 forzado a 2 por tipo Silent (además de 0x19 y 0x313)
    seq('a7s', 0x43863258, ['ldr.w r2, [r6, #0x76c]', 'cmp r2, #2', 'it eq', 'moveq r3, #2'])
    at('a7s', 0x43863286, 'strb r3, [r4, #0xd]')
    # A6000: +0x12 solo 0/1 (strbne/strbeq), +0xd=2 solo con 0x1c0==0x19
    seq('a6000', 0x43841496, ['ldrb r3, [r5]', 'cmp r3, #1', 'ite ne', 'strbne r2, [r4, #0x12]', 'strbeq r3, [r4, #0x12]'])
    seq('a6000', 0x43841468, ['cmp r1, #0x19', 'it eq', 'moveq r2, #2'])


@check
def caif_packet_byte1_class0_joins_class3():
    assert pic('a7s', 0x43863140, 0x43863144) == 0x43f04c8c and pic('a6000', 0x43841360, 0x43841364) == 0x43eedecc
    seq('a7s', 0x4386315c, ['cmp r3, #3', 'beq #0x43863162', 'cbnz r3, #0x43863178'])
    seq('a6000', 0x4384137c, ['cmp r3, #3', 'bne #0x43841396'])
    seq('a7s', 0x43863172, ['movs r3, #2', 'strb r3, [r4, #1]'])


@check
def policy_class0_and_globals():
    seq('a7s', 0x438649d4, ['ands r1, r2, #0x80', 'beq #0x438649f0'])
    seq('a7s', 0x438649f0, ['ldr.w r2, [r7, #0x404]', 'cmp r2, #2', 'bne #0x438649fe'])
    at('a7s', 0x43864a48, 'str r1, [r2, #0x5c]')
    G = pic('a7s', 0x438649f8, 0x438649fa); assert G == 0x43f06bc8, hex(G)
    seq('a7s', 0x43864ad0, ['ldr.w r3, [r7, #0x404]', 'cmp r3, #2', 'bne #0x43864ae0'])
    seq('a7s', 0x43864ad8, ['ldr r3, [pc, #0x128]', 'movs r2, #0', 'add r3, pc', 'b #0x43864b00'])
    at('a7s', 0x43864b00, 'strb.w r2, [r3, #0x60]')
    # getter de clase y su único llamador copia a 0x43f04c8c
    seq('a7s', 0x43864c78, ['ldr r0, [r3, #0x5c]', 'bx lr'])
    at('a7s', 0x43861bfc, 'bl #0x43864c74'); assert pic('a7s', 0x43861c00, 0x43861c02) == 0x43f04c8c


@check
def class_to_param9_copy():
    seq('a7s', 0x43862190, ['mov r3, r6', 'ldr lr, [r3], #4', 'add.w r2, r0, #0x60', 'mov r5, r0', 'ldm r2, {r0, r1, r2}',
                            'stm.w lr, {r0, r1, r2}'])
    seq('a7s', 0x43863478, ['add r3, pc', 'ldr r3, [r3]', 'strb.w r3, [r8, #0x69]'])
    seq('a7s', 0x43b1c8e2, ['bl #0x43862158', 'ldr r3, [sp]', 'ldrb r3, [r3, #9]', 'str.w r3, [r4, #0x4cc]'])
    seq('a7s', 0x438b77a4, ['add.w r1, r4, #0x648', 'ldrh.w r2, [r5, #0xb0]', 'bl #0x436f2938'])


@check
def class_event_consumer():
    seq('a7s', 0x438627d2, ['ldr r3, [pc, #0x9c]', 'add r3, pc', 'ldr r3, [r3]', 'cmp r3, #1', 'beq #0x438627ea',
                            'cmp r3, #3', 'bne #0x438627fe'])
    seq('a7s', 0x438627fe, ['ldr.w r3, [r4, #0x76c]', 'cmp r3, #2', 'beq #0x43862814'])
    seq('a7s', 0x437c3130, ['movs r3, #3'])
    at('a7s', 0x437c3138, 'movs r3, #0x22')


@check
def ev3_tag12_and_gpio():
    seq('a7s', 0x436d8304, ['ldr r1, [sp, #4]', 'movs r3, #0x12'])
    seq('a7s', 0x43b585b6, ['cmp r0, #0x11', 'bhi #0x43b585c0', 'movs r2, #0', 'b.w #0x4397d4c0'])
    seq('a7s', 0x4397d4d8, ['add.w r4, r4, #-0xe000000', 'lsls.w r1, r5, r1', 'add.w r4, r4, #0x910000', 'str r1, [r4, #0x48]'])
    seq('a6000', 0x4398f9bc, ['add.w r4, r4, #-0xe000000', 'lsls.w r1, r5, r1', 'add.w r4, r4, #0x910000', 'str r1, [r4, #0x48]'])


@check
def darwin_hw_type_selector():
    cm = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    def dw(rel):
        p = FW / rel; return p.read_bytes()
    a7 = dw('a7s-fw320/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin')
    a63 = dw('a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin')
    t7 = [x for _, x in ins(a7, 0x216f4, 7, base=0x4200, cs=cm)]
    assert t7 == ['cmp r0, #1', 'beq #0x21702', 'cmp r0, #2', 'beq #0x21702', 'cmp r0, #3', 'beq #0x21702',
                  'movs r0, #0'], t7
    t63 = [x for _, x in ins(a63, 0x24718, 2, base=0x4200, cs=cm)]
    assert t63 == ['cmp r0, #4', 'beq #0x2471e'], t63


if __name__ == '__main__':
    bad = 0
    for f in checks:
        try:
            f(); print(f'OK   {f.__name__}')
        except AssertionError as e:
            bad += 1; print(f'FAIL {f.__name__}: {e}')
    print(f'{len(checks) - bad}/{len(checks)} OK')
    sys.exit(1 if bad else 0)
