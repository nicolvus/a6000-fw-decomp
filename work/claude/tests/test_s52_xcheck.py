#!/usr/bin/env python3
"""S52 fase C (Claude): comprobación independiente de las afirmaciones de Codex que resultaron CONFIRMADAS.

Bytes/capstone sobre work/claude/input + arnés Unicorn propio (work/claude/s52/xcheck_emu.py, arranca en la entrada
real de SetExposure). Uso: ~/.venvs/re/bin/python -I work/claude/tests/test_s52_xcheck.py
"""
import csv
import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[3]
B = 0x43541000
BIN = {k: (ROOT / f'work/claude/input/{k}-av-cam.bin').read_bytes() for k in ('a7s', 'a6000')}
assert hashlib.sha256(BIN['a7s']).hexdigest().startswith('b857d338')
assert hashlib.sha256(BIN['a6000']).hexdigest().startswith('b60c845c')
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def seq(fw, addr, texts):
    d = BIN[fw]
    got = [f'{i.mnemonic} {i.op_str}' for i in CS.disasm(d[addr - B:addr - B + 4 * len(texts) + 8], addr)][:len(texts)]
    assert got == texts, f'{fw} {addr:#x}: {got} != {texts}'


def u32(fw, a):
    return struct.unpack_from('<I', BIN[fw], a - B)[0]


def tbb(fw, table, n=5):
    return [table + 2 * b for b in BIN[fw][table - B:table - B + n]]


checks = []


def check(f):
    checks.append(f)
    return f


@check
def tbb_targets():
    seq('a7s', 0x436f423e, ['cmp r6, #4', 'bhi #0x436f42fc', 'tbb [pc, r6]'])
    assert tbb('a7s', 0x436f4246) == [0x436f424c, 0x436f425c, 0x436f42fc, 0x436f4290, 0x436f42c4]
    seq('a6000', 0x436d70be, ['cmp.w sb, #4', 'bhi.w #0x436d728e', 'tbb [pc, sb]'])
    # caso 3 IMX210 empieza en 0x436d717a (no en 0x436d7114, que es el caso 2)
    assert tbb('a6000', 0x436d70ca) == [0x436d70d0, 0x436d70e0, 0x436d7114, 0x436d717a, 0x436d71ae]


@check
def imx235_case_bits():
    seq('a7s', 0x436f424c, ['ldrb r1, [r3, #4]', 'bfc r1, #2, #1', 'strb r1, [r3, #4]', 'ldrb r1, [r3, #4]',
                            'bfc r1, #6, #1', 'b #0x436f42d2'])
    seq('a7s', 0x436f42d2, ['strb r1, [r3, #4]', 'ldrb r1, [r3, #4]', 'bfc r1, #4, #1', 'strb r1, [r3, #4]',
                            'ldrb r3, [r2, #4]', 'orr r3, r3, #8', 'strb r3, [r2, #4]'])
    seq('a7s', 0x436f425c, ['ldrb r1, [r3, #4]', 'orr r1, r1, #4'])
    seq('a7s', 0x436f42a0, ['ldrb r1, [r3, #4]', 'orr r1, r1, #0x10'])
    # `cfg2+4 |= 8` es común a 0/1/3/4 (no exclusivo de ShutMode 0)
    for a in (0x436f4276, 0x436f42aa, 0x436f42de):
        seq('a7s', a, ['orr r3, r3, #8'])
    seq('a7s', 0x436f42fc, ['ldr r0, [pc, #0xb4]', 'mov r1, r6', 'add r0, pc', 'bl #0x438f7114'])


@check
def imx210_case_bits():
    seq('a6000', 0x436d70d0, ['ldrb r2, [r3, #2]', 'bfc r2, #2, #1', 'strb r2, [r3, #2]', 'ldrb r2, [r3, #2]',
                              'bfc r2, #7, #1', 'b #0x436d71bc'])
    seq('a6000', 0x436d71bc, ['strb r2, [r3, #2]', 'ldrb r2, [r3, #2]', 'bfc r2, #4, #1', 'strb r2, [r3, #2]',
                              'ldrb r2, [r3, #2]', 'orr r2, r2, #0x40'])
    seq('a6000', 0x436d717a, ['ldrb r2, [r3, #2]', 'orr r2, r2, #4', 'strb r2, [r3, #2]', 'ldrb r2, [r3, #2]',
                              'orr r2, r2, #0x80', 'strb r2, [r3, #2]', 'ldrb r2, [r3, #2]', 'orr r2, r2, #0x10'])
    seq('a6000', 0x436d7136, ['ldrb.w r2, [sl, #8]'])
    seq('a6000', 0x436d7142, ['ldrb.w r2, [sl, #0x14]'])


@check
def unicorn_own_harness():
    spec = importlib.util.spec_from_file_location('xe', ROOT / 'work/claude/s52/xcheck_emu.py')
    xe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xe)
    exp = {('imx235', 0x440220ac): {0: (0x00, 0xab), 1: (0x04, 0xaf), 3: (0x14, 0xbf), 4: (0x40, 0xeb)},
           ('imx210', 0x4401ca2e): {0: (0x40, 0x6b), 1: (0xc4, 0xef), 2: (0x94, 0xbf), 3: (0xd4, 0xff), 4: (0xc0, 0xeb)}}
    for (s, field), modes in exp.items():
        for m, (v0, vf) in modes.items():
            r0 = xe.run(s, m, {field: 0x00})
            rf = xe.run(s, m, {field: 0xff})
            assert r0['final'].get(hex(field)) == hex(v0), (s, m, r0['final'])
            assert rf['final'].get(hex(field)) == hex(vf), (s, m, rf['final'])
    r = xe.run('imx235', 3, None)
    assert int(r['final']['0x44021ff2'], 16) & 8  # bit 3 puesto (valor inicial del blob conserva otros bits)
    r = xe.run('imx210', 2, None)
    assert r['final'].get('0x4401c6d2') == '0x12' and r['final'].get('0x4401c7ce') == '0x34'


@check
def csv_48_fields_match_bytes():
    got = u32('a7s', 0x436f3968) + 0x436f392e + 4
    t = u32('a7s', got + u32('a7s', 0x436f396c))
    assert t == 0x43fee598
    rows = []
    while u32('a7s', t + 20 * len(rows)):
        rows.append(t + 20 * len(rows))
    d = BIN['a7s']
    cs = list(csv.DictReader((ROOT / 'work/codex/s52_sensor_register_trace.csv').open()))
    assert len(cs) == 48 and len(rows) == 69
    for r in cs:
        a = rows[int(r['row'])]
        p = u32('a7s', a)
        assert hex(struct.unpack_from('<H', d, p - 2 - B)[0]) == r['field']
        assert [int(r[k], 16) for k in ('values_col0_0x0b', 'values_col12_0x4e', 'values_col13_0x4f')] == \
            [d[a + 4 - B], d[a + 16 - B], d[a + 17 - B]]
    seq('a7s', 0x436f393a, ['adds r5, r2, r1', 'adds r2, #0x14', 'ldrb r5, [r5, #4]', 'strb r5, [r4]', 'ldr r4, [r2]'])


@check
def b1_dispatch_closed():
    seq('a7s', 0x436f294c, ['ldr r0, [r0]', 'ldr r3, [r0]', 'ldr r3, [r3, #0x28]', 'blx r3'])
    assert u32('a7s', 0x43fce050 + 0x28) == 0x436f4169
    seq('a7s', 0x436f4198, ['ldrb.w r6, [sl, #9]'])
    seq('a7s', 0x4386218c, ['bl #0x43861f58'])
    seq('a7s', 0x438633f8, ['bl #0x43861f58'])


@check
def drive_mode_only_in_read_flags():
    seq('a7s', 0x438b68da, ['ldr.w r3, [r5, #0x4d0]', 'add r6, pc', 'subs r3, #0x37', 'cmp r3, #1'])
    seq('a6000', 0x438c7406, ['ldr.w r3, [r5, #0x4d0]'])


if __name__ == '__main__':
    bad = 0
    for f in checks:
        try:
            f()
            print(f'OK   {f.__name__}')
        except AssertionError as e:
            bad += 1
            print(f'FAIL {f.__name__}: {e}')
    print(f'{len(checks) - bad}/{len(checks)} OK')
    sys.exit(1 if bad else 0)
