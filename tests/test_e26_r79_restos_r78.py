"""E26-R79: cierra los restos de R78 (handlers de tabla 0x295c4/0x25b70, acciones 04-06/0x2f de S, reejecución de S)."""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parents[1]
DZ = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
pytestmark = pytest.mark.skipif(not DZ.is_file(), reason="firmware original ausente")
from test_e26_r78_limites_r77 import B, _calls_to, _closure, _func, _text, _u32
from test_e26_r78_limites_r77 import fw as _fw

fw = _fw


def test_tabla_295c4_es_el_evento_0x16_de_la_tarea_principal(fw):
    d = fw[0]
    assert _u32(d, 0x1BB0C) == 0x29514 and 0x29514 + 8 * 0x16 == 0x295C4  # tabla (fn, máscara), índice 0x16
    assert (_u32(d, 0x295C4), _u32(d, 0x295C8)) == (0x1B137, 0x18A) and (_u32(d, 0x295CC), _u32(d, 0x295D0)) == (0x1B123, 0x18A)
    assert _text(fw, 0x1BA1E, 3)[:2] == ["cmp r6, #0x2c", "bhs #0x1bb04"] and _calls_to(fw, 0x1BA00) == [0x7E38, 0x7F84]
    assert _text(fw, 0x7DF6, 5)[:3] == ["mov r1, sp", "movs r0, #2", "bl #0x4530"]  # cola 2 de la tarea 0x7de2
    assert _text(fw, 0x7E18, 1) == ["ldrh r0, [r4, #2]"] and _text(fw, 0x7E36, 3)[1:] == ["bl #0x1ba00", "ldrh r0, [r4, #2]"]
    assert _text(fw, 0x1B994, 7)[3:] == ["ldr r1, [sp]", "mov.w r0, #2", "cbnz r4, #0x1b9ac", "bl #0x452c"]  # publica (1, id) en la cola 2
    # la acción de evento 0x16 = 0x1984e(1) (paso por 0x197ce) y fija la bandera [0x20002e74+8] = 0
    assert _text(fw, 0x1B138, 5)[:1] == ["bl #0x197ce"] and _text(fw, 0x197CE, 2) == ["movs r0, #1", "b.w #0x1984e"]
    assert _u32(d, 0x1B258) == 0x20002E74


def test_evento_0x16_solo_lo_publica_0x1bc12_tras_un_paquete(fw):
    d = fw[0]
    sites = [a for a, _, m, o in fw[1] if m == "bl" and o == "#0x1b97c"]
    ids = {}
    for a in sites:
        prev = [x for x in fw[1] if x[0] < a][-1]
        ids[a] = prev[3]
    assert [a for a, v in ids.items() if v == "r0, #0x16"] == [0x1BCBE]
    assert _text(fw, 0x1BCA4, 3) == ["bl #0x1b104", "cmp r0, #1", "bne #0x1bcc4"]  # 0x1b104: bandera==1 y [bloque 0xa+5] bit2==0
    assert _text(fw, 0x1B10A, 3) == ["ldr r0, [r0, #8]", "cmp r0, #1", "bne #0x1b11e"]
    assert _text(fw, 0x1B118, 2) == ["lsls r0, r0, #0x1d", "bmi #0x1b11e"]
    # 0x1bc12 no tiene llamadores ni punteros directos; solo ocupa el hueco 0x2831c de la lista que ejecuta 0x127b8
    assert not _calls_to(fw, 0x1BC12) and _u32(d, 0x2831C) == 0x1BC13 and _u32(d, 0x282FC) == 0xDB01
    assert _u32(d, 0x282E0) == 0x1BE43 and _u32(d, 0x282F8) == 0
    assert _u32(d, 0x127E4) == 0x282E0 and _text(fw, 0x124FE, 3) == ["ldr r0, [pc, #0x2e4]", "adds r0, #0x1c", "bl #0x127b8"]
    assert _text(fw, 0x127BE, 3) == ["ldr.w r0, [r5, r4, lsl #2]", "cmp r0, #0", "beq #0x127ce"] and _text(fw, 0x127C6, 1) == ["blx r0"]
    # cadena: paquete con cabecera 0x31 -> 0x11f22 -> 0x12330 -> 0x124a6 (aplica y llama a las lista de ganchos)
    assert _text(fw, 0x11F42, 3) == ["cmp r0, #0x31", "beq #0x11f4a", "movs r0, #2"] and _calls_to(fw, 0x12330) == [0x11F4A, 0x120A8]
    assert _text(fw, 0x12330, 3)[2:] == ["b.w #0x124a6"] and _calls_to(fw, 0x11F22) == [0x1269C, 0x12712, 0x1272A]
    assert _calls_to(fw, 0x125F6) == [0x7C68] and _calls_to(fw, 0x11F58) == [0x7BBA]
    # el cierre de la secuencia de captura no contiene la cadena de paquetes ni los consumidores de 0x1984e
    roots = [_u32(d, _u32(d, t) + 8 * k + 4) & ~1 for t in (0x28FDC, 0x28DD4) for k in range(0x32)] + [0x1961C, 0x190FC, 0x1811A]
    seen, _ = _closure(fw, roots)
    assert not seen & {0x124A6, 0x127B8, 0x12330, 0x11F22, 0x1BC12, 0x1BA00, 0x1984E, 0x1FEE2, 0x1B260, 0xCEE6, 0x197CE}


def test_tabla_25b70_es_lista_de_arranque(fw):
    d = fw[0]
    assert [_u32(d, 0x25B50 + 4 * k) for k in (0, 8, 9, 21)] == [0x7151, 0x75F1, 0x76CF, 0x8DA9] and _u32(d, 0x25BA8) == 0
    assert not [o for o in range(0, len(d) - 3, 4) if 0x25A00 <= _u32(d, o + B) < 0x25BB0]  # sin consumidor en la imagen
    assert _calls_to(fw, 0x75F0) == [] and _calls_to(fw, 0x1B260) == [0x765E] and _calls_to(fw, 0xCEE6) == [0x1B274]
    assert _text(fw, 0x7654, 4) == ["movs r0, #0", "bl #0xcf14", "cmp r0, #1", "bne #0x7662"]  # una vez, dentro del init
    assert _text(fw, 0x75F0, 1) == ["push {r4, r5, r6, lr}"] and _text(fw, 0x76CC, 1) == ["pop {r4, r5, r6, pc}"]  # vuelve: no es bucle


def test_acciones_04_05_06_2f_30_de_s(fw):
    uc = pytest.importorskip("unicorn")
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

    d = fw[0]
    ids = {i: _func(d, 0x28DD4, i) for i in (4, 5, 6, 0x2F, 0x30)}
    assert ids == {4: 0x171A6, 5: 0x171EA, 6: 0x1725C, 0x2F: 0x17880, 0x30: 0x178AE}
    # ayudantes de hardware de 04-06: stubs de bytes constantes
    for a, v in ((0x241BA, 0), (0x241C2, 0), (0x241CA, 1), (0x241CE, 0), (0x241DC, 1), (0x241E0, 1)):
        assert d[a - B:a - B + 4] == bytes([v, 0x20, 0x70, 0x47])
    ram, S0 = 0x20000000, 0x200036D8

    def run(act, s44=0, fl=0, s8=0):
        u = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB | uc.UC_MODE_MCLASS)
        u.mem_map(0x4000, 0x30000)
        u.mem_write(B, d)
        u.mem_map(ram, 0x100000)
        for a in (0x5C9E, 0x5C88, 0x1E4AA, 0x1E4C2, 0x1E3D2, 0x179D4, 0x94DE):
            u.mem_write(a, b"\x70\x47")
        u.mem_write(0x93E6, b"\x00\x20\x70\x47")  # t = 0: nunca vence un temporizador
        u.mem_write(0x20002E10, bytes([fl]))
        u.mem_write(0x20002E24, struct.pack("<I", 0))
        u.mem_write(S0 + 0x44, bytes([s44]))
        u.mem_write(S0 + 0x1C, struct.pack("<I", 0))
        u.mem_write(S0 + 8, struct.pack("<I", s8))
        u.mem_write(0x20000F00, b"\x70\x47")
        calls = []
        names = {0x1E4AA: "avanza", 0x1E4C2: "retiene", 0x1E3D2: "t200", 0x179D4: "error"}
        for a, n in names.items():
            u.hook_add(uc.UC_HOOK_CODE, lambda _u, _a, _z, n: calls.append(n), begin=a, end=a, user_data=n)
        u.reg_write(UC_ARM_REG_R0, ram + 0x1000)
        u.reg_write(UC_ARM_REG_SP, ram + 0x80000)
        u.reg_write(UC_ARM_REG_LR, 0x20000F01)
        u.emu_start(act | 1, 0x20000F00)
        return calls

    for a in (0x171A6, 0x171EA, 0x1725C):
        assert run(a) == ["avanza"] and run(a, s44=0x10) == ["avanza"]  # nunca retienen con estos stubs
    assert run(0x17880, fl=0) == ["avanza"]  # 0x12240()==0: avanza
    assert run(0x17880, fl=1) == ["retiene", "t200"]  # bandera externa: retiene y rearma 200 us
    assert run(0x178AE) == ["avanza"] and run(0x178AE, s8=500) == ["t200"]  # 0x30: pausa [S+8], no retiene
    # ninguna lee S+0x32/S+0x48 ni escribe P4B-P4E: cierre exacto (sin la ruta de error 0x16558)
    wr = {0xD18E, 0x1ECEC, 0x20C90, 0x20CB2, 0x20CD4, 0x20D00, 0x20D26, 0x20E0E, 0x20E98}
    for r, n in ((0x171A6, 18), (0x171EA, 18), (0x1725C, 13), (0x17880, 62), (0x178AE, 5)):
        seen, body = _closure(fw, [r])
        assert len(seen) == n and not seen & wr  # sin escritores de P4C/P4D/P4E ni de puertos
        if r == 0x17880:  # 0x2f: P4B (0xd116) solo tras 0x16558, que solo llama 0x16dc0 (error de vigilancia)
            assert seen & {0xD116, 0x51C0} == {0xD116, 0x51C0} and 0x16558 in seen
            assert [a for f in seen for a, _, m, o in body(f) if o == "#0x16558"] == [0x16DEA]
        else:
            assert not seen & {0xD116, 0x16558, 0x51C0}
        for f in seen:
            for a, _, m, o in body(f):
                assert not (m.startswith(("ldr", "str")) and re.search(r"\[r\d+, #0x(32|48)\]$", o) and f in (0x182CC, 0x182B4, 0x182BC, 0x182C4, 0x17906, 0x17924))
    assert _text(fw, 0x17934, 4) == ["bl #0x93e6", "str r0, [r4, #0x68]", "movw r0, #0x1388", "strb.w r5, [r4, #0x64]"]
    assert _u32(d, ((0x171B0 + 4) & ~3) + 0x260) == 0x186A0 and _u32(d, ((0x171FC + 4) & ~3) + 0x214) == 0x186A0


def test_reejecucion_de_s_no_esta_en_la_imagen(fw):
    d = fw[0]
    assert len(_calls_to(fw, 0x178E6)) == 14 and all(0x16C00 <= a < 0x17100 for a in _calls_to(fw, 0x178E6))
    for t in (0x178E6, 0x17900):
        assert not [o for o in range(0, len(d) - 3, 4) if _u32(d, o + B) in (t, t + 1)]
    users = []
    for a, _, m, o in fw[1]:
        r = re.match(r"r\d+, \[pc, #(0x[0-9a-f]+)\]$", o)
        if m == "ldr" and r and (ea := ((a + 4) & ~3) + int(r.group(1), 16)) < B + len(d) - 3 and _u32(d, ea) == 0x28DD4:
            users.append(a)
    assert users and all(0x16C00 <= a < 0x17910 for a in users)  # 0x28dd4 solo lo usan sus arrancadores y el ejecutor
    assert bytes(d[0x28DD4 + 0x18 - B:0x28DD4 + 0x1C - B]) == bytes([7, 0xD, 0xD, 6])  # temporizadores de S: 7 (hw) y 0xd
    assert _text(fw, 0x1E1BA, 6)[:4] == ["cmp r4, #0xc", "bls #0x1e1c2", "cmp r4, #0xd", "beq #0x1e1d0"]
    assert _text(fw, 0x1E3D2, 3)[2] == "mov r5, r1" and _text(fw, 0x1E400, 3) == ["ldrh r0, [r4, #0x10]", "bic r0, r0, #0x200", "uxth r0, r0"]
