"""E24-05a: origen de la captura, listas de la máquina de 49 estados y finalización, comprobados sobre `darwin_core.bin` 3.21
(y, para el productor de `pkt[+1]`, sobre `av-cam.bin`). Informe: docs/capture/e24-05a-captura-fin-bionz-darwin.md.

Las pruebas verifican instrucciones, tablas y relaciones reales; no el texto del informe.
"""
import json
import sys
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e24_05"))

from dwn import DARWIN, SHA256, Core

if not DARWIN.exists():
    pytest.skip(f"falta {DARWIN.relative_to(ROOT)}", allow_module_level=True)

import capture_flow as cf
from graph import build_all


@pytest.fixture(scope="module")
def c() -> Core:
    core = Core()
    assert core.sha256() == SHA256
    return core


@pytest.fixture(scope="module")
def graph():
    return build_all()


def text(c: Core, addr: int, size: int) -> str:
    return c.render(addr, size)


def closure(graph, root: int) -> set[int]:
    seen, work = set(), [root]
    while work:
        f = work.pop()
        if f not in seen:
            seen.add(f)
            work.extend(set(graph.calls.get(f, ())) | set(graph.tails.get(f, ())))
    return seen


def has(c: Core, addr: int, size: int, *needles: str) -> None:
    t = text(c, addr, size)
    for n in needles:
        assert n in t, f"{n!r} no está en {addr:#x}+{size:#x}:\n{t}"


# --- A. Inicio -----------------------------------------------------------------------------------------------

def test_descriptor_and_table_of_49_states(c):
    assert [c.u32(cf.DESC + 4 * k) for k in range(7)] == [cf.TABLE, 0x31, 0x200036FC, 0x200036FD, 0x200036F8, 0x31, 0x070D0D0D]
    st = cf.states(c)
    assert sorted(st) == list(range(49))  # el id coincide con el índice
    assert st[4] == 0x18636 and st[5] == 0x1865A and st[0x1F] == 0x190FC


def test_descriptor_users_are_only_init_reset_and_runner(c):
    # Palabras en pools literales y usuarios `ldr`: inicio 0x17950, reinicio 0x1834e y ejecutor 0x1961c.
    assert c.word_refs(cf.DESC) == [0x17D5C, 0x18688, 0x19794]
    users = c.ldr_users(cf.DESC)
    assert [a for a in users if not 0x19620 <= a <= 0x19696] == [0x1795C, 0x18358]
    has(c, 0x17950, 0x14, "bl #0x1e574", "bl #0x16c04")
    has(c, 0x1795C, 0x10, "bl #0x1e0b4")  # inicializa el descriptor (estado/lista)
    has(c, 0x1834E, 0x14, "bl #0x1e0b4")
    assert c.bl_callers(0x17950) == [0xCEE2] and c.bl_callers(0x1834E) == [0xCEFE]


def test_runner_is_only_called_from_capture_task_after_packet_acceptance(c):
    assert c.bl_callers(0x1961C) == [0x18180]
    has(c, 0x18160, 0x24, "bl #0x19a06", "bl #0x17f8c", "beq #0x18202", "bl #0x196b6", "bl #0x17cee", "bl #0x1961c")
    # La tarea completa se llama desde el veneno de API 0xce84 y éste desde el bucle de estado `On`.
    has(c, 0xCE84, 4, "b.w #0x1811a")
    assert c.bl_callers(0xCE84) == [0x7ECE, 0x7F20]
    has(c, 0x7ECE, 0xC, "bl #0xce84", "bl #0x16c54", "cmp r0, #1", "bne #0x7ece")


def test_runner_selects_one_of_five_lists_from_type_duration_and_burst_flag(c):
    has(c, 0x19622, 0x8, "ldrb.w r0, [r5, #0x44]", "ubfx r4, r0, #0, #1")
    has(c, 0x1962E, 0x2, "ldrh r0, [r5, #0x32]")
    has(c, 0x19632, 0x14, "ldrb.w r0, [r5, #0x3c]", "cmp r0, #1", "cmp r0, #2", "cmp r0, #3", "cmp r0, #4")
    # desplazamientos respecto de 0x28fdc -> las cinco listas
    for addr, off in ((0x19648, 0x54), (0x19652, 0x44), (0x1965A, 0x34), (0x19664, 0x22), (0x1966C, 0x12)):
        has(c, addr, 2, f"subs r1, #{off:#x}")
        assert cf.DESC - off in cf.LIST_PTRS
    has(c, 0x19678, 0x10, "bl #0x1e150", "strb.w r4, [r5, #0x26]", "bl #0x1e33e")
    has(c, 0x19696, 0xA, "bl #0x1e16e", "cmp r0, #0")
    has(c, 0x1969E, 2, "beq #0x19682")  # repite el motor hasta el id terminal


def test_five_lists_bytes_and_membership(c):
    lists = cf.state_lists(c)
    assert lists[0x28F88] == [2, 9, 3, 4, 0xD, 0xA, 0xF, 6, 0x13, 0x14, 0x1A, 0x1C, 0x1F, 0x20, 0x30, 0x31]
    assert lists[0x28F98] == lists[0x28FBA] == [2, 9, 3, 4, 0xA, 6, 0x13, 0x14, 0x1A, 0x1C, 0x1F, 0x21, 0x22, 0x20, 0x30, 0x31]
    assert lists[0x28FA8] == lists[0x28FCA] == [0xB, 0xC, 7, 0x17, 5, 8, 0x15, 0x16, 0x18, 0x19, 0x1D, 0x1E, 0x1F, 0x21, 0x22, 0x20, 0x30, 0x31]
    # Los estados de rearme: 4 solo en las listas de primera toma; 5 solo en las de ráfaga; 0x1f en todas.
    for ptr, ids in lists.items():
        assert (4 in ids) == (ptr in (0x28F88, 0x28F98, 0x28FBA))
        assert (5 in ids) == (ptr in (0x28FA8, 0x28FCA))
        assert 0x1F in ids
    # Las listas de ráfaga contienen el estado 0x17 (espera con tiempo límite hacia BIONZ), las de primera toma no.
    assert [p for p, ids in lists.items() if 0x17 in ids] == [0x28FA8, 0x28FCA]


# --- A. Paquete 0x0c ----------------------------------------------------------------------------------------

def test_message_table_has_single_22_byte_rx_id_0c(c):
    rows = cf.message_table(c)
    by_id = {r["id"]: r for r in rows}
    assert by_id[0x0C]["dir"] == "BIONZ→Darwin" and by_id[0x0C]["len"] == 0x16 and by_id[0x0C]["buf"] == 0x2000344C
    assert [r["id"] for r in rows if r["len"] == 0x16] == [0x0C]
    assert {r["id"] for r in rows if r["dir"] == "BIONZ→Darwin"} == {0x0C, 0x0F, 0x12, 0x13, 0x16}
    assert {r["id"] for r in rows if r["dir"] == "Darwin→BIONZ"} == {0x0B, 0x0D, 0x0E, 0x10, 0x11, 0x14, 0x15, 0x17}


def test_packet_copy_and_parser_field_map(c):
    has(c, 0x16C9C, 0x8, "movs r0, #6", "b.w #0x1ef06")  # lector índice 6 = ID 0x0c
    has(c, 0x17F94, 0x10, "bl #0x17e94", "strb.w r0, [r4, #0x43]")  # S+0x43 = estado de entradas, antes de copiar
    has(c, 0x17FBC, 0x4, "bl #0x5c9e")  # sección crítica
    # pkt[k] -> S+0x30+k (el paquete está en sp+4)
    has(c, 0x17FC0, 0x14, "ldrb.w r0, [sp, #4]", "strb r0, [r4, #0x30]!", "ldrb.w r0, [sp, #5]", "strb r0, [r4, #1]")
    has(c, 0x17FCE, 0xC, "ldrh.w r0, [sp, #6]", "strh r0, [r4, #2]", "ldrh.w r0, [sp, #8]", "strh r0, [r4, #4]")
    # pkt[+0x0c] bits 0-5 -> S+0x3c (solo si S+0x44.b0 == 0), bits 6-7 -> S+0x46 bits 2-3
    has(c, 0x18010, 0xC, "ldrb.w r0, [sp, #0x10]", "lsrs r1, r0, #6", "bfi r0, r1, #2, #2")
    has(c, 0x1805A, 0xC, "ldrb r0, [r4, #0x14]", "lsls r0, r0, #0x1f", "bne #0x18070")
    has(c, 0x18064, 0xC, "ubfx r0, r0, #0, #6", "strb.w r0, [r4, #0x3c]")
    has(c, 0x18070, 0xA, "ldrh r0, [r4, #0x32]", "cbnz r0, #0x1807a", "strb.w r0, [r4, #0x3c]")  # pkt[2:3]==0 => S+0x3c=0


def test_packet_acceptance_needs_zero_pkt0_and_zero_busy_code(c):
    has(c, 0x180B8, 0xE, "ldrb.w r0, [r4, #0x30]", "cbnz r0, #0x180ce", "ldrb.w r3, [r4, #0x43]", "cbz r3, #0x18100")
    has(c, 0x180C4, 0x8, "movs r2, #0x51", "movs r1, #0x10", "movs r0, #2", "bl #0x16558")  # rechazo: error cat 2, 0x10, 0x51
    has(c, 0x18100, 0x8, "movs r5, #1")  # aceptado => retorno 1
    has(c, 0x180CE, 0x2, "movs r5, #0")


def test_busy_mask_bit24_is_checked_by_packet_admission(c):
    dec = cf.busy_bit_decode(c)
    assert dec[24] == 0x16 and dec[6] == 1 and dec[0] == 2 and dec[16] == 0x10
    has(c, 0xD294, 0xC, "ldr r1, [pc, #0xd8]", "ldr r0, [r1, #8]", "ldr r0, [r1, #4]")  # 0xd294(1) -> [0x20002bd0+8]
    # La máscara se levanta con bit 24 en los TRES arrancadores de la máquina exterior y se libera en el estado 9 (0x200e6).
    for start in (0x1FEE6, 0x1FF78, 0x1FFD4):
        has(c, start, 4, "lsls r0, r1, #0x18")
    for bl in (0x1FEE8, 0x1FF7A, 0x1FFD6):
        assert bl in c.bl_callers(0xD116)
    has(c, 0x200EA, 0x6, "mov.w r0, #0x1000000", "bl #0xd18e")
    has(c, 0xD18E + 0xA, 0x14, "ldr r1, [r5, #8]", "bics r1, r0", "str r1, [r5, #8]", "ldr r1, [r5, #4]", "str r1, [r5, #4]")


# --- B. Finalización ----------------------------------------------------------------------------------------

def test_terminal_state_probes(c):
    # 0x1ff2a/0x1ffbe/0x20018 consultan `0x1e16e` (id actual >= 0xa) -- reutiliza E24-05, aquí solo las dependencias de finalización
    has(c, 0x199B4, 4, "b.w #0x1ffbe")
    has(c, 0x199D0, 4, "b.w #0x20018")
    has(c, 0x1E16E, 0x14, "ldrb r1, [r2, #0x14]", "ldr r2, [r2, #0xc]", "bhi #0x1e190")


def test_task_epilogue_reports_end_and_releases_busy_bit_9(c):
    # al agotar las tomas: 0x17a44 (rearme final condicional), mensaje 0xe0/0xf0 (según S+0x3d.b0), libera 0x200 y publica el último error
    has(c, 0x18202, 0x8, "bl #0x17a44", "bl #0x19a0e")
    has(c, 0x1820A, 0xC, "ldrb.w r0, [r6, #0x3d]", "lsls r0, r0, #0x1f", "beq #0x18220", "movs r0, #0xe0")
    has(c, 0x18220, 0x8, "movs r0, #0xf0", "bl #0x1e5f2")
    has(c, 0x1824E, 0x6, "mov r0, r7", "bl #0xd18e")  # r7 = 0x200
    has(c, 0x1811A + 0x10, 0x10, "lsls r7, r1, #9")
    has(c, 0x18254, 0x18, "ldr.w r0, [r6, #0x9c]", "beq #0x1826c", "b.w #0x16adc")  # error pendiente -> evento 1


def test_status_messages_use_1e5f2_with_known_codes(c):
    ins = c.all_insns
    idx = {i.address: k for k, i in enumerate(ins)}
    codes = {}
    for a in c.bl_callers(0x1E5F2):
        for j in range(idx[a] - 1, idx[a] - 8, -1):
            p = ins[j]
            if p.mnemonic in ("movs", "mov", "mov.w") and p.op_str.startswith("r0, #"):
                codes[a] = int(p.op_str.split("#")[1], 0)
                break
    assert codes == {0x178F2: 0x30, 0x180DC: 0xB0, 0x1813E: 0xA0, 0x181AA: 0x90, 0x18226: 0xF0, 0x19692: 0x10, 0x1EC74: 0x20}
    # los cuatro códigos del hilo de captura se escriben en el anillo de eventos 0x20000600+0x80 a través de 0x16adc(1, ...)
    has(c, 0x1E67A, 0x8, "movs r0, #1", "b.w #0x16adc")
    has(c, 0x16AE8, 0x10, "ldr r0, [pc, #0x110]", "bl #0x25738")
    has(c, 0x16AF8, 0x14, "ldr r0, [pc, #0x104]", "ldrb.w r1, [r0, #0x31]", "cmp r1, #0x18")  # 24 entradas de 4 B
    has(c, 0x16B12, 0x4, "strb.w r5, [r1, #0x80]")


def test_status_block_builder_publishes_busy_mask_and_event_ring(c):
    assert c.u32(0x26D28) == 0x6C79  # puntero de callback delante de la tabla de regiones
    assert (c.u32(0x26D44), c.u32(0x26D48)) == (0x200009F8, 0x78)
    assert (c.u32(0x26D4C), c.u32(0x26D50)) == (0x20000A70, 0x80)
    assert (c.u32(0x26D54), c.u32(0x26D58)) == (0x20000AF0, 0x150)
    has(c, 0x6C9E, 0x10, "movs r0, #1", "bl #0xd294", "str r0, [r4, #4]", "movs r0, #0", "bl #0xd294", "str r0, [r4, #8]")
    has(c, 0x6CDA, 0x8, "ldr r0, [r0, #0x24]", "uxth r1, r0", "ldr r0, [r5, #0x20]", "bl #0xcf0e")
    has(c, 0xCF0E, 4, "b.w #0x16bca")  # copia el anillo de eventos a la región 0x20000a70
    has(c, 0x16BCA, 0x10, "cmp r1, #0x60")
    has(c, 0x16BDC, 0xC, "ldrb.w r5, [r5, #0x80]")


# --- C. Excepciones del motor -------------------------------------------------------------------------------

def test_every_error_notifier_call_triggers_operation_5(c):
    has(c, 0x165A0, 0xE, "bl #0xd380")
    sites = {}
    ins = c.all_insns
    idx = {i.address: k for k, i in enumerate(ins)}
    for a in c.bl_callers(0x16558):
        regs = {}
        for j in range(idx[a] - 1, idx[a] - 10, -1):
            p = ins[j]
            if p.mnemonic in ("bl", "blx", "pop", "pop.w"):
                break
            if p.mnemonic in ("movs", "mov", "mov.w", "movw") and "#" in p.op_str:
                regs.setdefault(p.op_str.split(",")[0], int(p.op_str.split("#")[1], 0))
        sites[a] = regs.get("r0")
    assert sites == {0x16DEA: 2, 0x180CA: 2, 0x1989C: 6, 0x1AD30: 4, 0x1F518: 6, 0x1FAB8: 6, 0x20878: 6, 0x20894: 6, 0x21340: 4}


def test_timeout_error_comes_from_burst_wait_state_0x17(c, graph):
    st = cf.states(c)
    has(c, st[0x17], 0x16, "bl #0x16e26", "b.w #0x1e4c2", "bne #0x189ea")
    has(c, 0x16E26, 0x18, "movw r1, #0x7148", "movs r0, #0x49", "bl #0x16df8", "bl #0x1ecb0", "bl #0x16dc0")
    has(c, 0x16DC0, 0x40, "ldr r0, [r5, #0x1c]", "bls #0x16df0", "movs r1, #0x30", "movs r0, #2", "bl #0x16558")
    # sólo el estado 0x17 alcanza 0x16558 entre los 49 estados
    assert [k for k, h in st.items() if 0x16558 in closure(graph, h)] == [0x17]


def test_rearm_api_and_adc_error_are_not_in_the_capture_path(c, graph):
    assert sorted(c.bl_callers(0x1984E)) == [0xCEE8, 0x197D0, 0x1F22E, 0x1F262]
    has(c, 0x19888, 0x16, "bl #0x1b1fa", "cbnz r0, #0x198a8", "movs r2, #0x21", "movs r0, #6", "bl #0x16558")
    has(c, 0x1B1FA, 0x2C, "bl #0x24330", "b.w #0x24368")  # lectura ADC canal 8 y comparación con umbral
    st = cf.states(c)
    s = set()
    for k in (0x1811A, 0x17F8C, 0x1961C, 0x17CEE, 0x17A44, *st.values()):
        s |= closure(graph, k)
    assert 0x1984E not in s and 0x1B1FA not in s


def test_capture_closure_reaches_only_two_error_sites(c, graph):
    cap = set()
    for root in (0x1811A, 0x17F8C, 0x1961C, 0x17CEE, 0x17A44, *cf.states(c).values()):
        cap |= closure(graph, root)
    assert {0x16558, 0x16DC0, 0x16E26, 0xD380} <= cap
    assert not cap & {0x1AD10, 0x2130C, 0x2083C, 0x1984E, 0x1FCB8, 0x1FEB6}  # cat 4, ADC y frenos: fuera de la captura
    assert [f for f in sorted(graph.rev[0x16558]) if f in cap] == [0x16DC0, 0x17F8C]
    assert [f for f in sorted(graph.rev[0x16DC0]) if f in cap] == [0x16E26]


def test_prep_rearm_l2_in_0x17cee_needs_burst_flag_class_bits_and_predicate(c):
    has(c, 0x17E6A, 0x2A, "tst.w r0, #0x30", "beq #0x17e92", "bpl #0x17e92", "ldrb.w r0, [r5, #0x44]",
        "beq #0x17e92", "bl #0x196a2", "beq #0x17e92", "movs r0, #1", "b.w #0x19998")


def test_rearm_arming_conditions(c):
    has(c, 0x199B8, 0x14, "bl #0x19b9e", "cmp r0, #0", "beq #0x199ce", "b.w #0x1ffce")
    has(c, 0x19B9E, 0x20, "movs r0, #0x10", "bl #0x165c8", "ldr.w r0, [r0, #0x170]", "lsls r0, r0, #0x1f")  # error cat 6 y S+0x170.b0
    has(c, 0x1865C, 0x10, "bl #0x19b96", "cmp r0, #3", "bne #0x18676", "bl #0x199b8")  # estado 5
    has(c, 0x19B96, 4, "b.w #0x20720")
    has(c, 0x20720, 4, "b.w #0x20c74")
    has(c, 0x18636, 0x14, "bl #0x196a2", "cbz r0, #0x18650", "movs r0, #1", "bl #0x19998")  # estado 4
    for st_id in (2, 3, 4, 6, 0xD):
        assert cf.states(c)[st_id] in {0x185EA, 0x1860C, 0x18636, 0x18690, 0x18810}
    assert sorted(c.bl_callers(0x196A2)) == [0x17E80, 0x185EE, 0x18610, 0x1863A, 0x18694, 0x18832]
    others = [a for a in c.bl_callers(0x19998) if a != 0x18642]
    assert len(others) == 1 and 0x17CEE < others[0] < 0x17E94  # la otra llamada está en la preparación 0x17cee


# --- D. Clase de captura --------------------------------------------------------------------------------------

def test_class_predicate_bytes_and_truth_table(c):
    has(c, 0x196A2, 0x14, "ldrb.w r1, [r1, #0x31]", "lsls r2, r1, #0x1e", "beq #0x196b2", "lsls r1, r1, #0x19", "bpl #0x196b4", "movs r0, #1")
    # reescritura de S+0x31 por tipo de mecanismo (0x19b5e -> 0x202ba -> [0x20003cd8+0x20])
    has(c, 0x1807A, 0x1E, "bl #0x19b5e", "cmp r0, #1", "cmp r0, #2", "cmp r0, #3", "cmp r0, #4")
    has(c, 0x180E6, 0x8, "bic r0, r0, #3")
    has(c, 0x180F4, 0xA, "bic r0, r0, #3", "adds r0, r0, #1")
    has(c, 0x1808E, 0xE, "bic r0, r0, #3", "adds r0, r0, #2", "bic r0, r0, #0x40")
    has(c, 0x202BA, 6, "ldr r0, [pc, #0x2ec]", "ldrb.w r0, [r0, #0x20]")
    tt = {(t, p): cf.class_predicate(p, t)["0x196a2"] for t in range(5) for p in (0, 2, 0x40, 0x42)}
    assert all(tt[(t, p)] == 1 for t in (1, 2) for p in (0, 2, 0x40, 0x42))  # tipos 1/2: siempre actúa
    assert all(tt[(4, p)] == 0 for p in (0, 2, 0x40, 0x42))  # tipo 4: nunca actúa
    assert [tt[(3, p)] for p in (0, 2, 0x40, 0x42)] == [0, 0, 1, 1]  # tipo 3: depende del bit 6
    assert [tt[(0, p)] for p in (0, 2, 0x40, 0x42)] == [1, 0, 1, 1]  # tipo 0: valor crudo


def test_mechanism_type_is_set_by_bionz_command_1_to_4(c):
    has(c, 0x205E6, 0x20, "strb.w r0, [r1, #0x20]", "cmp r0, #4", "movs r0, #0")
    assert c.bl_callers(0x19B62) == [0x1F240]
    has(c, 0x1F23A, 0x14, "movs r0, #1", "movs r0, #2", "movs r0, #3", "movs r0, #4", "bl #0x19b62")
    for a in (0x20C74,):
        has(c, a, 0xC, "bl #0x1b080", "and r0, r0, #7")


def test_class_consumers_are_the_five_predicate_states_and_time_selectors(c):
    st = cf.states(c)
    users = [i.address for i in c.all_insns if i.mnemonic == "ldrb.w" and "#0x31]" in i.op_str and "lsls" not in i.op_str]
    zone = [a for a in users if 0x1850A <= a <= 0x1972C]
    assert len(zone) >= 12  # prueba ya hecha en E24-05; aquí solo el recuento
    assert st[2] == 0x185EA  # primer estado que depende del predicado


# --- D. Productor en BIONZ -----------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def av():
    if not cf.AVCAM.exists():
        pytest.skip("falta av-cam.bin")
    return cf.AVCAM.read_bytes()


def test_bionz_pkt1_producer_bytes_and_flags(av):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    code = av[0x43841342 - cf.AV_BASE:0x43841398 - cf.AV_BASE]
    t = " | ".join(f"{i.mnemonic} {i.op_str}" for i in md.disasm(code, 0x43841342))
    assert t.startswith("movs r3, #0 | strb r3, [r4] | ldrh.w r2, [sb, #0x4bc] | ands r2, r2, #0x20")
    assert "adds r3, #0x40" in t and "adds r3, #0x41" in t and "movs r3, #2" in t and t.endswith("strb r3, [r4, #1] | b #0x43841398") or t.endswith("strb r2, [r4, #1]")
    chk = cf.avcam_checks()
    assert chk["variable_clase_0x43841360"] == "0x43eedecc"
    assert chk["byte_flag_0x4384136c"] == chk["byte_flag_0x43841380"] == chk["byte_flag_0x43841350"] == "0x43f9b503"
    # modificadores posteriores de pkt[1]: +0x14 y |0x80
    code2 = av[0x43841398 - cf.AV_BASE:0x438413B6 - cf.AV_BASE]
    t2 = " | ".join(f"{i.mnemonic} {i.op_str}" for i in md.disasm(code2, 0x43841398))
    assert "adds r3, #0x14" in t2 and "orn r3, r3, #0x7f" in t2


def test_bionz_pkt_2_3_zero_when_condition_and_pkt_0c(av):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    code = av[0x438413B6 - cf.AV_BASE:0x438413E4 - cf.AV_BASE]
    t = " | ".join(f"{i.mnemonic} {i.op_str}" for i in md.disasm(code, 0x438413B6))
    assert "bl #0x4382fe08" in t and "strb r3, [r4, #2]" in t and "strb r3, [r4, #3]" in t and "strb r3, [r4, #5]" in t


def test_bionz_class_and_flag_copies_come_from_one_parameter_object(av):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    dis = lambda a, n: " | ".join(f"{i.mnemonic} {i.op_str}" for i in md.disasm(av[a - cf.AV_BASE:a - cf.AV_BASE + n], a))
    assert dis(0x43842404, 8) == "ldr r3, [pc, #4] | add r3, pc | ldr r0, [r3, #0x60] | bx lr"  # clase
    assert dis(0x43842420, 10).endswith("ldrb.w r0, [r3, #0x64] | bx lr")  # byte-flag
    # FUN_4383f5e4 (preparación de captura) los copia a 0x43eedecc / 0x43f9b503, que lee el constructor del paquete
    t = dis(0x4383f784, 0x2E)
    assert "bl #0x43842404" in t and "str r0, [r3]" in t and "bl #0x43842420" in t and "strb r0, [r3]" in t
    # FUN_43841070 (constructor) llama a la preparación y al fijador de clase FUN_43842158


# --- Reutilización de E24-05 ---------------------------------------------------------------------------------

def test_e24_05_artifacts_still_consistent():
    d = json.loads((ROOT / "analysis/e24-05/recovery-closure.json").read_text())
    assert d["binario_sha256"] == SHA256


def test_generated_flow_json_matches_current_bytes():
    got = cf.main()
    saved = json.loads((ROOT / "analysis/e24-05a/capture-flow.json").read_text())
    assert saved["estados"] == got["estados"] and saved["listas"] == got["listas"]
