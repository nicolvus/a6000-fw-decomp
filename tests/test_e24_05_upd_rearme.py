"""E24-05: ruta InitCom → Upd → bootloader y origen de la máquina de rearme, comprobados sobre los bytes de `darwin_core.bin`.

Lee el binario oficial 3.21 (no versionado); se omite si falta. Informe: docs/capture/e24-05-upd-y-rearme.md.
Las pruebas verifican instrucciones, tablas y relaciones de llamada reales, no el texto del informe.
"""
import re
import struct
import sys
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e24_05"))

from dwn import DARWIN, SHA256, Core

if not DARWIN.exists():
    pytest.skip(f"falta {DARWIN.relative_to(ROOT)}", allow_module_level=True)

from graph import BASE, build, build_all
from reach import ERR, PRIMS, Reach, Scenario


@pytest.fixture(scope="module")
def c() -> Core:
    core = Core()
    assert core.sha256() == SHA256
    return core


@pytest.fixture(scope="module")
def graph():
    return build_all()


@pytest.fixture(scope="module")
def reach(c):
    return Reach(c)


def asm(c: Core, addr: int, n: int) -> dict[int, str]:
    return {i.address: f"{i.mnemonic} {i.op_str}" for i in c.dis(addr, n)}


def lit(c: Core, insn_addr: int) -> int:
    return next(c.lit_of(i) for i in c.dis(insn_addr, 2))


# ---------------------------------------------------------------------------------------------- A


def test_state_engine_walks_init_main_next_exit(c):
    ins = asm(c, 0x4950, 0x30)
    assert lit(c, 0x4950) == 0x25BB0 and ins[0x4954] == "subs r7, #0x60"      # tabla = 0x25bb0 - 0x60 = 0x25b50
    assert lit(c, 0x4952) == 0x20002A04                                        # variable de estado
    assert ins[0x4966] == "add.w r4, r7, r0, lsl #4"                           # entrada de 16 B por estado
    assert (ins[0x496a], ins[0x496c]) == ("ldr r0, [r4]", "blx r0")            # init
    assert (ins[0x496e], ins[0x4970]) == ("ldr r0, [r4, #4]", "blx r0")        # main (bloquea; devuelve el evento)
    assert (ins[0x4972], ins[0x4974]) == ("ldr r1, [r4, #8]", "blx r1")        # next(evento) → nuevo estado
    assert ins[0x4976] == "str r0, [r5]"                                       # única escritura de la variable de estado
    assert (ins[0x4978], ins[0x497a]) == ("ldr r0, [r4, #0xc]", "blx r0")      # exit del estado anterior
    assert [hex(a) for a in c.ldr_users(0x20002A04)] == ["0x4952"]


def test_state_table_names_and_upd_entry(c):
    names = {}
    for s in range(6):
        for j in range(4):
            cb = c.u32(0x25B50 + 16 * s + 4 * j)
            if cb:
                for i in c.dis(cb & ~1, 0x400):
                    if i.mnemonic == "adr":
                        t = ((i.address + 4) & ~3) + int(re.search(r"#(0x[0-9a-f]+)", i.op_str).group(1), 0)
                        names[(s, j)] = c.data[t - BASE:t - BASE + 20].split(b"\0")[0].decode()
                        break
    assert [names[(s, 1)].split()[0] for s in range(6)] == ["Init", "Seton", "On", "Exiton", "Off", "Upd"]
    assert c.u32(0x25BA0) == 0x8DA5 and c.u32(0x25BA4) == 0x8DA9 and c.u32(0x25BA8) == c.u32(0x25BAC) == 0
    assert asm(c, 0x8DA4, 4) == {0x8DA4: "movs r0, #0", 0x8DA6: "bx lr"}      # init de Upd: no hace nada


def test_seton_next_table_maps_event2_to_upd_and_no_other_state_reaches_it(c):
    nxt = {}
    for s in range(5):
        fn = c.u32(0x25B50 + 16 * s + 8) & ~1
        tabs = [i for i in c.dis(fn, 0x30) if c.lit_of(i) is not None and 0x27000 < c.lit_of(i) < 0x28000]
        nxt[s] = c.lit_of(tabs[0])
        assert any("lsl #2" in i.op_str for i in c.dis(fn, 0x30))             # ldr r0, [tabla, evento, lsl #2]
    assert nxt == {0: 0x274A4, 1: 0x274A8, 2: 0x274B8, 3: 0x27624, 4: 0x27628}
    assert [c.u32(0x274A8 + 4 * k) for k in range(4)] == [2, 3, 5, 3]          # Seton: evento 2 → Upd (5)
    assert c.u32(0x274A4) == 1 and c.u32(0x27624) == 4 and c.u32(0x27628) == 1  # Init→Seton, Exiton→Off, Off→Seton
    assert [c.u32(0x274B8), c.u32(0x274BC)] == [3, 3]                          # On→Exiton
    assert 5 not in [c.u32(a) for a in (0x274A4, 0x27624, 0x27628, 0x274B8, 0x274BC)]


def test_seton_main_waits_on_queue0_and_returns_event2_for_state4(c):
    ins = asm(c, 0x74D8, 0x60)
    assert ins[0x74E0] == "movs r0, #3" and ins[0x74E4] == "bl #0x452c"       # envía {0,0} a la cola 3 (arranca InitCom)
    assert ins[0x74EA] == "movs r0, #0" and ins[0x74EC] == "bl #0x4530"       # recibe de la cola 0 (bloqueante)
    assert ins[0x74F2] == "cbz r0, #0x7520"                                    # tipo 0 → mira el dato
    ins = asm(c, 0x7520, 0x22)
    assert ins[0x7522] == "cmp r0, #4" and ins[0x7526] == "movs r4, #2"        # dato 4 → evento 2
    assert ins[0x7528] == "b #0x74fa" and asm(c, 0x751C, 4)[0x751C] == "mov r0, r4"   # el evento sale como valor de retorno
    assert asm(c, 0x752A, 0x10)[0x752C] == "beq #0x74e8"                       # datos 1/2/3: sigue esperando
    assert asm(c, 0x7536, 0x10)[0x7536] == "movs r4, #0"                       # cualquier otro dato → evento 0 (On)


def test_com_task_runs_initcom_and_publishes_state_to_queue0(c, graph):
    ins = asm(c, 0xECE4, 0x34)
    assert ins[0xECEC] == "movs r0, #3" and ins[0xECEE] == "bl #0x4530"        # espera en la cola 3
    assert ins[0xECFE] == "bl #0x4bca"                                         # único llamador de InitCom
    assert ins[0xED06] == "strh r5, [r4]" and ins[0xED0C] == "strh r0, [r4, #2]"  # mensaje {tipo 0, dato = estado}
    assert ins[0xED0E] == "movs r0, #0" and ins[0xED12] == "bl #0x452c"        # publica en la cola 0
    assert c.bl_callers(0x4BCA) == [0xECFE]
    assert lit(c, 0x7460) == 0xECE5 and asm(c, 0x745E, 2)[0x745E] == "movs r1, #8"   # tarea COM creada en Seton init (prio 8)
    assert c.word_refs(0xECE5) == [0x75BC]                                     # y el literal de creación está en la propia zona de Seton


def test_initcom_state4_and_state7_end_the_handshake_and_unknown_ids_force_state7(c):
    ins = asm(c, 0x4D20, 0x24)
    assert ins[0x4D28] == "strb r0, [r5]"                                      # guarda el estado recibido
    assert (ins[0x4D36], ins[0x4D38]) == ("cmp r0, #4", "beq #0x4e0c")
    assert (ins[0x4D3A], ins[0x4D3C]) == ("cmp r0, #7", "beq #0x4d38")         # estado 7 también cae en el beq anterior
    assert asm(c, 0x4E0C, 2)[0x4E0C] == "b #0x4ea6" and asm(c, 0x4EA6, 0x18)[0x4EB8] == "mov r0, r4"
    ins = asm(c, 0x4EC0, 0x18)
    assert ins[0x4ED2] == "movs r0, #7" and ins[0x4ED4] == "strb r0, [r5]"     # id desconocido → estado 7
    assert asm(c, 0x4C74, 2)[0x4C74] == "movs r4, r0"                          # r4 = resultado de la recepción (0 = ok)
    assert asm(c, 0x4CDC, 0x10)[0x4CDC] == "cmp r1, #0x11"                     # despacho: 0x11, 0x12, 0x13, 0x16 solamente
    assert asm(c, 0x4EA4, 2)[0x4EA4] == "movs r4, #1"                          # salida por bandera de parada: retorna 1


def test_initcom_disarms_hw_watchdog_after_each_valid_frame(c):
    ins = asm(c, 0x4C8A, 0x4C)
    assert ins[0x4C8E] == "bl #0xa1dc" and ins[0x4C96] == "cmp r2, r0" and ins[0x4C98] == "beq #0x4cb4"   # CRC válido
    assert asm(c, 0x4CD4, 2)[0x4CD4] == "bl #0xa4ac"                           # → desarma el watchdog (control = 0)
    ins = asm(c, 0xA4AC, 0x18)
    assert ins[0xA4BA] == "movs r1, #0" and ins[0xA4BC] == "strb r1, [r0, #8]"  # HWWDT+8 (control) = 0


def test_upd_main_leaves_through_the_bootloader_vector(c):
    ins = asm(c, 0x8DA8, 0x58)
    assert ins[0x8DBA] == "cpsid i" and ins[0x8DDA] == "cmp r0, #0x2f"         # IRQ off y borrado de pendientes 0..0x2f
    assert ins[0x8DE2] == "bl #0x5d70" and ins[0x8DE8] == "cmp r4, #0x1f"      # 32 llamadas con r0 = 0..0x1f
    assert (ins[0x8DEE], ins[0x8DF0]) == ("movs r0, #4", "strb r0, [r5, #6]")  # buzón[6] = 4
    assert (ins[0x8DF2], ins[0x8DF4]) == ("movs r0, #0", "strb r0, [r5, #7]")  # buzón[7] = 0
    assert ins[0x8DF6] == "bl #0x45bc" and lit(c, 0x8DAC) == 0x20000700
    assert c.bl_callers(0x45BC) == [0x8DF6]
    assert asm(c, 0x45BC, 0xA) == {0x45BC: "ldr r1, [r0]", 0x45BE: "ldrh r0, [r1]", 0x45C0: "ldr.w pc, [r0, #4]"} or \
        asm(c, 0x45BC, 0xA)[0x45C2] == "ldr.w pc, [r0, #4]"


def test_kernel_receive_blocks_without_timeout_and_poll_variant_exists(c):
    # svc #0x21 (recv) → r2 = 0 → bloquea; svc #0x22 → r2 = 1 → devuelve 4 si no hay mensaje
    assert asm(c, 0x4530, 2)[0x4530] == "svc #0x21" and asm(c, 0x4534, 2)[0x4534] == "svc #0x22"
    assert asm(c, 0x66F8, 4)[0x66F8] == "movs r2, #0" and asm(c, 0x65EE, 2)[0x65EE] == "movs r2, #1"
    ins = asm(c, 0x653E, 8)
    assert ins[0x653E] == "cbz r2, #0x6544" and ins[0x6540] == "movs r0, #4"   # r2 = 1: no bloquea; r2 = 0: sigue y suspende


def test_dispatch_sets_are_closed_and_upd_is_unreachable_from_on(c):
    # InitCom solo existe mientras vive la tarea COM, y esa tarea la crea Seton init y la borra Seton exit
    assert [hex(a) for a in c.bl_callers(0x4504) if 0x73CC <= a < 0x75F0] == ["0x7452", "0x7462", "0x7470"]
    assert [hex(a) for a in c.bl_callers(0x4518) if 0x73CC <= a < 0x75F0] == ["0x7580", "0x7586", "0x758c"]
    on_tasks = [hex(a) for a in c.bl_callers(0x4504) if 0x75F0 <= a < 0x8044]
    assert len(on_tasks) == 5 and 0xECE5 not in [c.lit_of(i) for i in c.all_insns if 0x75F0 <= i.address < 0x8044]


def test_recovery_closure_contains_the_whole_chain_and_not_the_runtime_feeder(graph):
    c1 = [0x45C8, 0x46AC, 0x4538, 0x4562] + [graph.c.u32(0x25B50 + 16 * s + 4 * j) - 1 for s in (0, 1) for j in range(4)] + \
         [graph.c.u32(0x25BA4) - 1, 0xEC42, 0xECE4, 0xECA0]
    _, s1 = build(c1, graph)
    for f in (0xECE4, 0x4BCA, 0x4F92, 0x4A2C, 0xA1DC, 0x8DA8, 0x45BC, 0x6580, 0x255A6, 0xA4AC, 0xA4C4, 0x48E0):
        assert f in s1, hex(f)
    assert 0xA524 not in s1 and 0x1F0A0 not in s1 and 0x1FEE2 not in s1       # ni el alimentador del WDT ni el rearme
    assert 400 < len(s1) < 600


# ---------------------------------------------------------------------------------------------- B


LISTS = {0x29CD8: [0, 7, 8, 9, 10], 0x29CDD: [0, 2, 3, 6, 9, 10], 0x29CE3: [0, 4, 5, 6, 9, 10], 0x29CE9: [0, 1, 4, 5, 6, 9, 10]}


def test_outer_machine_state_lists_and_handlers(c):
    for p, ids in LISTS.items():
        assert list(c.data[p - BASE:p - BASE + len(ids)]) == ids
    handlers = {c.u32(0x29D0C + 8 * k): c.u32(0x29D0C + 8 * k + 4) & ~1 for k in range(11)}
    assert handlers == {0: 0x20100, 1: 0x2011C, 2: 0x20120, 3: 0x200E2, 4: 0x20134, 5: 0x200E2, 6: 0x20148, 7: 0x2014C, 8: 0x200E2,
                        9: 0x200E6, 10: 0x200FC}
    assert [c.u32(0x29CF0 + 4 * k) for k in range(2)] == [0x29D0C, 0xA]


def test_three_wrappers_pick_the_list_with_the_same_gate(c):
    # 0x1f5a2 es un salto a 0x1fe66: la compuerta de los tres arrancadores es la misma función
    assert asm(c, 0x1F5A2, 4)[0x1F5A2] == "b.w #0x1fe66"
    for wrapper, gate_call, taken, other in ((0x1FEE2, 0x1FEEE, 0x13, 0x18), (0x1FF72, 0x1FF80, 0xD, 0x18), (0x1FFCE, 0x1FFDC, 0x7, 0x18)):
        ins = asm(c, wrapper, 0x70)
        assert ins[gate_call] == "bl #0x1f5a2"
        sub_taken = [v for v in ins.values() if v == f"subs r1, r6, #{taken:#x}" or v == f"sub.w r1, r5, #{taken:#x}" or v == f"subs r1, r6, #{taken}"
                     or v == f"subs r1, r6, #{taken:#x}"]
        assert sub_taken or any(f"#{taken:#x}" in v and "r1" in v for v in ins.values()), hex(wrapper)
        assert any(f"#{other:#x}" in v and "r1" in v for v in ins.values()), hex(wrapper)


def test_gate_zero_selects_0_7_8_9_10_for_every_rearm_starter(reach):
    sel = {}
    for name, ent, r0 in (("A", 0x1984E, 0), ("A1", 0x1984E, 1), ("B", 0x19998, 0), ("C", 0x199B8, 0), ("D", 0x199D8, 0)):
        for gate in (0, 4):
            res = reach.run(ent, Scenario(gate, 0), r0)
            sel[(name, gate)] = sorted({p for d, p in res.lists if d == 0x29CF0})
    assert all(v == [0x29CD8] for (n, g), v in sel.items() if g == 0)
    assert sel[("A", 4)] == [0x29CDD] and sel[("B", 4)] == [0x29CE3] and sel[("C", 4)] == [0x29CE9] and sel[("D", 4)] == [0x29CE3]


def test_inner_machine_is_started_only_by_outer_states_2_and_4(c):
    assert c.bl_callers(0x1F396) == [0x20126] and c.bl_callers(0x1F3B6) == [0x2013A]
    assert c.bl_callers(0x20120) == [] and c.bl_callers(0x20134) == []         # solo la tabla del motor exterior los llama
    assert c.word_refs(0x20121) == [0x29D20] and c.word_refs(0x20135) == [0x29D30]
    assert c.u8(0x29797) == 0x18 and c.u8(0x297AC) == 0x01                     # primer id de cada secuencia interior
    assert list(c.data[0x29797 - BASE:0x29797 - BASE + 21]) == [0x18, 0x19, 0, 0x15, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 2, 3, 4, 0x17, 0x1A]
    assert list(c.data[0x297AC - BASE:0x297AC - BASE + 18]) == [1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 2, 3, 4, 0x17, 0x1A]
    # descriptor interior: cinco tablas id→manejador sobre las mismas variables de estado
    assert [c.u32(0x297C0 + 0x1C * k) for k in range(5)] == [0x29868, 0x29940, 0x29A18, 0x29AF0, 0x29BC8]


def test_every_caller_of_a_motor_primitive_is_known(c, graph):
    inner = {c.u32(0x29868 + 8 * k + 4) & ~1 for k in range(27)}
    inner |= {c.u32(t + 8 * k + 4) & ~1 for t in (0x29940, 0x29A18, 0x29AF0, 0x29BC8) for k in range(27)}
    six = {c.u32(0x29CA0 + 8 * k + 4) & ~1 for k in range(7)}
    def own(a):  # 0x1f474 (pulsos de servicio) no es destino de BL: se agrupa por rango
        return 0x1F474 if 0x1F474 <= a < 0x1F4B2 else (graph.owner.get(a) or a)
    owners = {p: sorted(own(a) for a in c.bl_callers(p)) for p in (0x1FE50, 0x1FE86, 0x1FEB6)}
    allowed = inner | six | {0x1F5A6, 0x1FCB8, 0x1F474}
    for p, fs in owners.items():
        assert fs and all(f in allowed for f in fs), (hex(p), [hex(f) for f in fs])
    assert owners[0x1FE50] == [0x1F474, 0x1F5A6, 0x1F68A, 0x1F6E4]
    assert owners[0x1FE86] == [0x1F474, 0x1F636, 0x1FBFC] and owners[0x1FEB6] == [0x1F474, 0x1F660, 0x1F794, 0x1FBC8, 0x1FC30, 0x1FCB8]
    assert c.bl_callers(0x1F5A6) == [0x2063A] and c.bl_callers(0x1FCB8) == [0x1F5FA, 0x1F606]
    # pulsos de servicio: solo por 0x2008e/0x200a6 (órdenes BIONZ 0x90/0x91, tras la compuerta) y 0x1f4b6 (exige compuerta 4)
    assert c.bl_callers(0x1F4B2) == [0x200A0] and c.bl_callers(0x1F4B6) == [0x200B8]
    assert c.bl_callers(0x2008E) == [0x19A32] and c.bl_callers(0x200A6) == [0x19A36]
    assert asm(c, 0x2008E, 0x14)[0x20092] == "bl #0x1f5a2" and asm(c, 0x200A6, 0x14)[0x200AA] == "bl #0x1f5a2" 
    # 0x1fe86 consulta la compuerta (4, 1 o 2); 0x1fe50 y 0x1feb6 no
    assert [i.address for i in c.dis(0x1FE86, 0x18) if i.mnemonic == "bl"] == [0x1FE88, 0x1FE90, 0x1FE98]
    assert not [i for i in c.dis(0x1FE50, 0x16) if i.mnemonic == "bl" and i.operands[0].imm == 0x1FE66]
    assert not [i for i in c.dis(0x1FEB6, 0x18) if i.mnemonic == "bl" and i.operands[0].imm == 0x1FE66]


def test_motor_entry_points_have_a_closed_set_of_references(c):
    # cierre inverso: ningún puntero de datos (tabla/callback) apunta a las primitivas ni a sus envoltorios, y las cadenas de BL son las esperadas
    for f in (0x1FE50, 0x1FE86, 0x1FEB6, 0x1FE32, 0x1FCB8, 0x1F600, 0x200CA, 0x19B6E, 0xCEEC, 0x1F5A6, 0x20638, 0x19B6A, 0x2008E, 0x200A6,
              0x19A32, 0x19A36, 0x1F474, 0x1F4B2, 0x1F4B6, 0x1FEE2, 0x1FF72, 0x1FFCE, 0x1984E, 0x19998, 0x199B8, 0x199D8):
        assert c.word_refs(f | 1) == [], hex(f)
    assert c.word_refs(0xD46F) == [0x2953C]                                   # única entrada: operación 5 de la tabla 0x29514
    assert (c.bl_callers(0x1F600), c.bl_callers(0x200CA), c.bl_callers(0x19B6E), c.bl_callers(0xCEEC)) == ([0x200CC], [0x19B86], [0xCEFA], [0xD470])
    assert (c.bl_callers(0x20638), c.bl_callers(0x19B6A)) == ([0x19B6A], [0xCF02])
    assert (c.bl_callers(0x19A32), c.bl_callers(0x19A36)) == ([0x1F282], [0x1F28A])   # órdenes BIONZ 0x90/0x91
    assert (c.bl_callers(0x1FEE2), c.bl_callers(0x1FF72), c.bl_callers(0x1FFCE)) == ([0x19880], [0x199AA, 0x199E4], [0x199CA])


def test_gate_function_reads_the_high_nibble_every_call_without_cache(c):
    ins = asm(c, 0x1FE66, 0x20)
    assert ins[0x1FE6C] == "bl #0x1b080" and ins[0x1FE70] == "lsrs r4, r0, #4" and ins[0x1FE72] == "cmp r4, #6"
    assert c.data[0x1FE7A - BASE:0x1FE7A - BASE + 6] == bytes([4, 3, 3, 3, 3, 3])   # 0 → 0; 1..5 → el propio nibble; >5 → 0
    ins = asm(c, 0x1B080, 0x18)
    assert lit(c, 0x1B080) == 0x200002C0 and ins[0x1B090] == "ldrb.w r0, [r0, #0x50]"   # [0x20000050 + canal], en cada llamada
    assert ins[0x1B084] == "ldrb r2, [r2, r1]"                                 # y la bandera de presencia [0x200002c0 + canal]
    sites = sorted(a for a in c.bl_callers(0x1FE66))
    assert sites == [0x1F4BA, 0x1F4DE, 0x1F576, 0x1F5A2, 0x1F5A8, 0x1F896, 0x1F908, 0x1FA40, 0x1FE88, 0x1FE90, 0x1FE98, 0x201BC]


def test_differential_reachability_of_motor_primitives(reach):
    motor = set(PRIMS)
    for ent, r0 in ((0x1984E, 0), (0x1984E, 1), (0x19998, 0), (0x199B8, 0), (0x199D8, 0)):
        off = reach.run(ent, Scenario(0, 0), r0)
        on = reach.run(ent, Scenario(4, 0), r0)
        assert not {t for _, _, t, _ in off.calls} & (motor | {0x1F396, 0x1F3B6, 0x1F5A6, 0x1FCB8}), hex(ent)
        assert {t for _, _, t, _ in on.calls} & motor and {t for _, _, t, _ in on.calls} & {0x1F396, 0x1F3B6}, hex(ent)
    for ent in (0x2008E, 0x200A6):                                              # pulsos de servicio (órdenes BIONZ 0x90/0x91)
        assert not {t for _, _, t, _ in reach.run(ent, Scenario(0, 0), 3).calls} & motor
        assert {t for _, _, t, _ in reach.run(ent, Scenario(4, 0), 3).calls} & motor
    # máquina de 49 estados de la secuencia de captura: ninguna primitiva con compuerta 0, sí con 4
    m49 = {c_ for c_ in (reach.c.u32(0x28FF8 + 8 * k + 4) & ~1 for k in range(0x32))}
    for gate, expect in ((0, False), (4, True)):
        hit = set()
        for h in m49:
            hit |= {t for _, _, t, _ in reach.run(h, Scenario(gate, 0)).calls} & motor
        assert bool(hit) == expect, gate


def test_error_recovery_op5_keeps_an_ungated_brake_pulse(c, reach):
    # índice 5 de la tabla de operaciones (0x29514, 8 B por entrada) = 0xd46e; lo publica 0xd380 tras cada error 0x16558
    assert c.u32(0x29514 + 8 * 5) == 0xD46F
    assert asm(c, 0xD3CA, 6)[0xD3CA] == "movs r0, #5" and asm(c, 0xD3CC, 2)[0xD3CC] == "bl #0x1b9b2"
    assert 0x165A8 in c.bl_callers(0xD380) and 0x1BF42 in c.bl_callers(0xD380)   # error 0x16558 y comando BIONZ 0x3e
    assert c.u32(0x2A19C + 8 * 0x3E) == 0x1BF39
    assert asm(c, 0xD46E, 6)[0xD470] == "bl #0xceec" and 0x19B6E in {a for a in c.bl_callers(0x19B6E)} | {0x19B6E}
    off = reach.run(0xD46E, Scenario(0, 0))
    assert {t for _, _, t, _ in off.calls} & {0x1FCB8, 0x1FEB6} == {0x1FCB8, 0x1FEB6}   # 0x1feb6 no pasa por la compuerta
    assert 0x1FE50 not in {t for _, _, t, _ in off.calls} and 0x1FE86 not in {t for _, _, t, _ in off.calls}
    ins = asm(c, 0x1FCB8, 8)
    assert ins[0x1FCBA] == "bl #0x1feb6" and asm(c, 0x1FCD0, 8)[0x1FCD4] == "b.w #0x1fe32"   # freno (P4=3), espera, apaga


def test_category6_error_sites_and_their_conditions(c, reach):
    sites = []
    for a in c.bl_callers(ERR):
        if any(i.mnemonic == "movs" and i.op_str == "r0, #6" for i in c.dis(a - 12, 12)):
            sites.append(a)
    assert sorted(sites) == [0x1989C, 0x1F518, 0x1FAB8, 0x20878, 0x20894]
    seen = {}
    for name, ent, r0 in (("api", 0x1984E, 0), ("inner", 0x1FA3A, None), ("cam", 0x1F4CE, None), ("adc", 0x2083C, None)):
        for gate, coil in ((0, 0), (4, 0), (0, 2)):
            res = reach.run(ent, Scenario(gate, coil), r0)
            seen[(name, gate, coil)] = {s for _, s, t, v in res.calls if t == ERR and v == 6}
    assert 0x1989C in seen[("api", 0, 0)]                                       # tras el rearme, depende del ADC de posición (no de la compuerta)
    assert not seen[("cam", 0, 0)] and seen[("cam", 4, 0)] == {0x1F518}           # comprobación de leva: detrás de la compuerta
    assert seen[("inner", 0, 0)] == {0x1FAB8}                                   # 0x1fa3a emite error 6 si la compuerta != 4 (solo dentro de la máquina interior)
    assert not seen[("adc", 0, 0)] and seen[("adc", 0, 2)] == {0x20878, 0x20894}  # fase ADC: detrás del tipo de bobina (parche tipo 0)
    ins = asm(c, 0x1B1FA, 0x12)
    assert ins[0x1B1FE] == "bl #0x242f8"
    assert 0x1B1FA in {i.operands[0].imm for i in c.all_insns if i.mnemonic == "bl" and i.address in (0x19872, 0x1988E)}


def test_completion_mask_is_a_local_busy_lock_not_a_message_to_bionz(c):
    # cada arrancador toma la máscara 0x01000000 y el estado 9 de la lista (0x200e6) la libera
    for w in (0x1FEE8, 0x1FF7A, 0x1FFD6):
        ins = asm(c, w - 6, 8)
        assert ins[w - 4] == "movs r1, #1" or "movs r1, #1" in ins.values()
        assert asm(c, w, 2)[w] == "bl #0xd116"
    ins = asm(c, 0x200E6, 0x14)
    assert ins[0x200EA] == "mov.w r0, #0x1000000" and ins[0x200EE] == "bl #0xd18e"
    assert lit(c, 0xD122) == 0x20002BD0 and asm(c, 0xD136, 0x10)[0xD136] == "ldr r0, [r5, #8]"   # máscara en RAM local
    for f in (0x200E6, 0x1FEE2, 0x1FF72, 0x1FFCE, 0x2014C, 0x20134, 0x20120):
        assert not [a for a in c.bl_callers(0x452C) if f <= a < f + 0x60], hex(f)       # ninguno envía mensajes
    assert c.u32(0x29D0C + 8 * 9 + 4) & ~1 == 0x200E6


def test_rearm_start_points_trace_back_to_bionz_driven_entries(c, graph):
    assert graph.rev[0x1984E] >= {0xCEE6, 0x197CE}
    assert graph.rev[0x19998] >= {0x17CEE, 0x18636} and graph.rev[0x199B8] >= {0x17A44, 0x1865A, 0x190FC}
    assert c.word_refs(0x18637) == [0x2901C] and c.word_refs(0x1865B) == [0x29024] and c.word_refs(0x190FD) == [0x290F4]   # estados 4, 5, 0x1f de la máquina de 49
    assert [c.u32(0x28FF8 + 8 * k) for k in range(3)] == [0, 1, 2] and c.u32(0x28FDC + 4) == 0x31
    assert c.u32(0x29514 + 8 * 22 + 0) == 0x1B137 and c.u32(0x29514 + 8 * 25) == 0xCEB9           # operaciones 22 y 25
    assert 0x1BCBE in c.bl_callers(0x1B97C) and 0x1BFF6 in c.bl_callers(0x1B97C)
    assert 0x75F0 in graph.rev[0x1B260]                                         # "On init" (0x75f0) → 0x1b260 → 0xcee6 → 0x1984e
    assert c.u32(0x25B70) == 0x75F1


def test_dispatcher_commands_0x60_0x67_reach_the_charge_api(c):
    assert c.u32(0x2A19C + 8 * 0x60) == 0x1BFB3 and c.u32(0x2A19C + 8 * 0x67) == 0x1BFB3 and c.u32(0x2A19C + 8 * 0x40) == 0x1BFB3
    assert asm(c, 0x1F362, 0xC)[0x1F366] == "cmp r1, #0x5f" and 0x1BFB6 in c.bl_callers(0x1F362)
    # 0x58+8 = 0x60 → 0x1f22c (movs r0,#1; bl 0x1984e); 0x67 → 0x1f24e (bucle de N cargas)
    tbb = [c.u8(0x1F0F0 + k) for k in range(10)]
    assert 0x1F0F0 + 2 * tbb[8] == 0x1F22C and asm(c, 0x1F22C, 4)[0x1F22E] == "bl #0x1984e"
    assert asm(c, 0x1F0FA, 0x20)[0x1F108] == "beq #0x1f202" and asm(c, 0x1F202, 2)[0x1F202] == "b #0x1f24e"
    assert 0x1F262 in c.bl_callers(0x1984E)


# ---------------------------------------------------------------------------------------------- C


def test_capture_class_byte_lands_at_0x20003a01_and_is_rewritten_per_mechanism(c):
    assert c.u8(0x29784 + 6) == 0x0C                                           # índice 6 del lector = mensaje asíncrono 0x0c
    ins = asm(c, 0x1EFB8, 0x40)
    assert ins[0x1EFC0] == "cmp r0, #5" and ins[0x1EFE0] == "movs r5, #0x16"    # idx 6 copia 0x16 B
    assert lit(c, 0x1EFDE) == 0x20003A66 and ins[0x1EFE2] == "subs r1, #0x66"    # destino 0x20003a00
    assert c.bl_callers(0x1EFB8) == [0x17198, 0x17378, 0x1747E]                 # única función que escribe esa copia
    assert sorted(a for a in (i.address for i in c.all_insns if c.lit_of(i) == 0x20003A66)) == \
        [0x1EF0A, 0x1EF22, 0x1EF2A, 0x1EF32, 0x1EF3E, 0x1EF46, 0x1EF82, 0x1EF8A, 0x1EF92, 0x1EF9A, 0x1EFD0, 0x1EFDE]
    # el analizador 0x17f8c la lee con 0x16c9c → 0x1ef06(6) y guarda pkt[1] en S+0x31
    assert asm(c, 0x16C9C, 6)[0x16CA0] == "b.w #0x1ef06" and asm(c, 0x16C9C, 4)[0x16C9E] == "movs r0, #6"
    ins = asm(c, 0x17FC0, 0x10)
    assert ins[0x17FC4] == "strb r0, [r4, #0x30]!" and ins[0x17FCC] == "strb r0, [r4, #1]"
    # reescritura por tipo de bobina (0x19b5e → 0x202ba): 1/2 limpian bits 0-1; 3 → +1; 4 → +2; tipo 0 la deja intacta
    ins = asm(c, 0x1807A, 0x80)
    assert ins[0x18080] == "beq #0x180e6" and ins[0x18088] == "beq #0x180f4" and ins[0x18092] == "bic r0, r0, #3"
    assert ins[0x18096] == "adds r0, r0, #2" and ins[0x180EA] == "bic r0, r0, #3"
    assert asm(c, 0x19B5E, 4)[0x19B5E] == "b.w #0x202ba" and lit(c, 0x202BA) == 0x20003CD8


def test_nothing_in_darwin_writes_the_watchdog_config_bytes(c, graph):
    # +0x40..+0x43 de 0x20000000: ningún almacén desde una base 0x20000000; solo los puede fijar 0x12/0x16 de InitCom (o el arranque)
    for body in graph.bodies.values():
        base = set()
        for a in sorted(body):
            i = next(c.md.disasm(c.data[a - BASE:a - BASE + 4], a, 1), None)
            if i is None:
                continue
            m = re.match(r"(r\d+|sb|sl|fp|ip),", i.op_str)
            if c.lit_of(i) == 0x20000000 and m:
                base.add(m.group(1))
                continue
            mm = re.search(r"\[(r\d+|sb|sl|fp|ip), #(0x[0-9a-f]+)\]", i.op_str)
            if i.mnemonic.startswith("str") and mm and mm.group(1) in base:
                assert int(mm.group(2), 0) not in (0x40, 0x41, 0x42, 0x43), hex(a)
    ins = asm(c, 0x4D40, 0x50)                                                   # 0x12: bloques de 0x78 B en 0x20000000 + desplazamiento
    assert ins[0x4D50] == "movs r1, #0x78" and ins[0x4D64] == "add.w r0, r0, #0x20000000" and ins[0x4D68] == "bl #0x255a6"
    ins = asm(c, 0x4CFC, 0x28)                                                   # 0x16: ventana 0x20000000..0x20004000
    assert ins[0x4D0E] == "cmp.w r7, #0x20000000" and lit(c, 0x4D14) == 0x20004000


def test_watchdog_arm_disarm_feed_sites_by_state(c):
    arm = {0x73D4: ("Seton", 0x40), 0x7956: ("On", 0x41), 0x804E: ("Exiton", 0x42), 0x823C: ("Off", 0x43), 0x8460: ("Off", 0x43)}
    for site, (_, off) in arm.items():
        prev = next(c.md.disasm(c.data[site - 4 - BASE:site - BASE], site - 4))
        assert prev.mnemonic.startswith("ldrb") and prev.op_str.endswith(f"#{off:#x}]"), hex(site)
    assert sorted(c.bl_callers(0xA4C4)) == sorted(list(arm) + [0x1BFAE])
    assert sorted(c.bl_callers(0xA4AC)) == [0x4CD4, 0x70DC, 0x7978, 0x81D0, 0x83D4, 0x8C78, 0x1BF74]
    assert sorted(c.bl_callers(0xA524)) == [0x79A6, 0x8A3E]                    # solo se alimenta en On (tarea 0x7915) y en Off
    ins = asm(c, 0xA4C4, 0x62)
    assert ins[0xA4D0] == "muls r0, r1, r0" and lit(c, 0xA4CC) == 0x1869F and lit(c, 0xA4CE) == 0x1ACCE551
    assert ins[0xA4EA] == "cmp r2, #1" and ins[0xA4EC] == "beq #0xa51a"          # [0x20000031] == 1 → carga la cuenta pero no arranca
    assert ins[0xA4F2] == "cmp r0, #1" and ins[0xA4FA].startswith("bic r0, r0, #2") and ins[0xA500].startswith("orr r0, r0, #2")
    assert ins[0xA50A].startswith("orr r0, r0, #1")                               # bit 0 siempre; bit 1 según [0x20000032] != 1
    # el alimentador es un bucle con temporizador sobre la cola 1 de la tarea 0x7915, independiente de la máquina de rearme
    assert asm(c, 0x795A, 8)[0x795E] == "bl #0x4530" and asm(c, 0x795A, 4)[0x795C] == "movs r0, #1"
    assert c.bl_callers(0x1BF6E) == [] and c.u32(0x2A19C + 8 * 0) == 0x1BFBF   # el ejecutor de comandos desarma durante cada comando
    assert asm(c, 0x1BF6E, 8)[0x1BF74] == "bl #0xa4ac"


def test_hw_watchdog_reload_constant_is_one_unit_per_0x1869f_counts(c):
    v = struct.unpack_from("<I", c.data, 0xA540 - BASE)[0]
    assert v == 0x1869F                                               # = 100 kHz × 1 s − 1 (INFERENCIA del reloj; el capítulo HWWDT no está en el repo)
    assert struct.unpack_from("<I", c.data, 0xA538 - BASE)[0] == 0x1ACCE551
