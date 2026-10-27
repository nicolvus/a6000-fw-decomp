"""E25-02 — auditoría independiente del candidato B1a y de la vía volátil InitCom.

Solo lectura: no ejecuta firmware, no conecta la cámara, no escribe RAM/NVRAM/NAND,
no genera FDAT/DAT. Lee los binarios locales y produce un JSON reproducible.

Uso:
    python scripts/e25_02/audit.py            # imprime el JSON
    python scripts/e25_02/audit.py --write    # escribe analysis/e25-02/audit.json

La independencia respecto de E25 está en el método: este script no importa
`scripts/e25/*` ni reutiliza sus JSON; decodifica los bytes con Capstone y
construye controles diferenciales propios (original vs tipo 0 vs candidato).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x4200
ORIGINAL = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
TIPO0 = ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin"
CANDIDATE = ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin"
OUT = ROOT / "analysis/e25-02/audit.json"

SHA_ORIGINAL = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
SHA_TIPO0 = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
SHA_CANDIDATE = "55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d"

GATE = 0x1FE66
GATE_BRANCH = 0x1FE6A
GATE_EPILOGUE = 0x1FE82
TIPO0_ADDR = 0x20C78
TIPO0_BYTES = bytes.fromhex("09e000bf00bf00bf")

# Primitivas del motor: PDOR4 (P40/P41) con máscara 0xfffc.
MOTOR = {0x1FE32: "0", 0x1FE50: "1", 0x1FE86: "2", 0x1FEB6: "3"}
MOTOR_CALLERS = {
    0x1FE50: [0x1F47C, 0x1F5B8, 0x1F6E0, 0x1F730],
    0x1FE86: [0x1F482, 0x1F65C, 0x1FC10],
    0x1FEB6: [0x1F49C, 0x1F686, 0x1F7BE, 0x1FBDC, 0x1FC34, 0x1FCBA],
}


class Image:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.end = BASE + len(self.data)
        self.md = capstone.Cs(
            capstone.CS_ARCH_ARM,
            capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS,
        )
        self.md.detail = True
        self._all: list | None = None

    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    def u8(self, addr: int) -> int:
        return self.data[addr - BASE]

    def u16(self, addr: int) -> int:
        return struct.unpack_from("<H", self.data, addr - BASE)[0]

    def u32(self, addr: int) -> int:
        return struct.unpack_from("<I", self.data, addr - BASE)[0]

    def bytes(self, addr: int, n: int) -> bytes:
        return self.data[addr - BASE:addr - BASE + n]

    def dis(self, addr: int, n: int):
        return self.md.disasm(self.data[addr - BASE:addr - BASE + n], addr)

    def all_insns(self) -> list:
        if self._all is None:
            out, a = [], BASE
            while a < self.end - 2:
                got = next(self.md.disasm(self.data[a - BASE:a - BASE + 4], a, 1), None)
                if got is None:
                    a += 2
                    continue
                out.append(got)
                a += got.size
            self._all = out
        return self._all

    def bl_callers(self, target: int) -> list[int]:
        out = []
        for ins in self.all_insns():
            if ins.mnemonic in ("bl", "b.w", "blx") and ins.operands \
                    and ins.operands[0].type == capstone.arm.ARM_OP_IMM \
                    and ins.operands[0].imm == target:
                out.append(ins.address)
        return out

    def word_refs(self, value: int) -> list[int]:
        pat = struct.pack("<I", value)
        out, p = [], self.data.find(pat)
        while p >= 0:
            if p % 4 == 0:
                out.append(BASE + p)
            p = self.data.find(pat, p + 1)
        return out

    def imm_refs(self, values: set[int]) -> list[tuple[int, str]]:
        """Inmediatos que *construyen* una dirección (no destinos de branch directo)."""
        out = []
        for ins in self.all_insns():
            if ins.mnemonic in ("bl", "b.w", "blx", "b", "bx"):
                continue
            for op in ins.operands:
                if op.type == capstone.arm.ARM_OP_IMM and op.imm in values:
                    out.append((ins.address, f"{ins.mnemonic} {ins.op_str}"))
        return out


def ins_at(img: Image, addr: int) -> str:
    got = list(img.dis(addr, 4))
    return f"{got[0].mnemonic} {got[0].op_str}" if got else "?"


def branch_target_n(img: Image, addr: int) -> int:
    """Destino de un B.N Thumb (T2, 16 bits): inm11 con signo, ×2, PC=addr+4."""
    hw = img.u16(addr)
    if hw & 0xF800 != 0xE000:
        raise ValueError(f"{addr:#x}: no es B.N ({hw:#06x})")
    imm = hw & 0x7FF
    if imm & 0x400:
        imm -= 0x800
    return (addr + 4 + (imm << 1)) & 0xFFFFFFFF


def original_gate_value(byte: int) -> int:
    """Valor que devuelve 0x1fe66 sin parche, para el byte de 0x20000050."""
    nibble = (byte >> 4) & 0xF
    if nibble == 0 or nibble >= 6:
        return 0
    return nibble


def patched_gate_value() -> int:
    """B1a: el camino parcheado no lee 0x1b080 y devuelve r5=0."""
    return 0


def list_bytes(img: Image, addr: int, terminal: int = 0x0A) -> list[int]:
    out = []
    for k in range(0x40):
        v = img.u8(addr + k)
        out.append(v)
        if v >= terminal:
            break
    return out


def outer_table(img: Image) -> dict[int, int]:
    return {img.u32(0x29D0C + 8 * k): img.u32(0x29D0C + 8 * k + 4) & ~1 for k in range(11)}


def decode_starters(img: Image) -> dict:
    """Tres arrancadores: el puntero de lista se elige con el retorno de 0x1f5a2."""
    rows = {}
    spec = {
        "load 0x1fee2": (0x1FEE2, 0x1FEEE, 0x1FEF6, 0x1FF0A, 0x1FF0E, 0x13, 0x29CDD),
        "capture4 0x1ff72": (0x1FF72, 0x1FF80, 0x1FF88, 0x1FF9C, 0x1FFA0, 0x0D, 0x29CE3),
        "capture5/1f 0x1ffce": (0x1FFCE, 0x1FFDC, 0x1FFE4, 0x1FFF6, 0x1FFFA, 0x07, 0x29CE9),
    }
    for name, (entry, bl, sub, ldr, subs, delta, gate4_ptr) in spec.items():
        got_bl = ins_at(img, bl)
        got_sub = ins_at(img, sub)
        got_ldr = ins_at(img, ldr)
        got_subs = ins_at(img, subs)
        rows[name] = {
            "entry": f"{entry:#x}",
            "gate_call": f"{bl:#x}: {got_bl}",
            "gate4_adjust": f"{sub:#x}: {got_sub}",
            "gate0_load": f"{ldr:#x}: {got_ldr}",
            "gate0_adjust": f"{subs:#x}: {got_subs}",
            "gate4_list": f"{gate4_ptr:#x}",
            "gate4_ids": list_bytes(img, gate4_ptr),
            "gate0_list": "0x29cd8",
            "gate0_ids": list_bytes(img, 0x29CD8),
            "delta_expected": f"0x{delta:x}",
        }
    return rows


def decode_consumers(img: Image) -> dict:
    """Comportamiento inmediato de cada consumidor de 0x1fe66 con retorno 0."""
    rows = {}
    for site in img.bl_callers(GATE):
        # 24 bytes alrededor del sitio; el llamador está justo antes.
        ctx = []
        for ins in img.dis(max(site - 8, BASE), 0x28):
            ctx.append(f"{ins.address:#x}: {ins.mnemonic} {ins.op_str}")
        rows[f"{site:#x}"] = ctx
    return rows


def classify_motor_callers() -> dict:
    """Clasificación estática de los llamadores directos de las primitivas del motor."""
    out: dict[str, list[dict[str, str]]] = {}
    for prim, sites in MOTOR_CALLERS.items():
        out[f"{prim:#x}"] = []
        for s in sites:
            if 0x1F474 <= s < 0x1F4B4:
                kind = "pulse 0x1f474 (solo desde 0x1f4b6, que exige gate==4)"
            elif 0x1F5A6 <= s < 0x1F600:
                kind = "rearme directo 0x1f5a6 (retorna si gate==0)"
            elif 0x1F600 <= s < 0x1F630 or 0x1FCB8 <= s < 0x1FCD8:
                kind = "operación 5 (sin compuerta)"
            elif 0x1F630 <= s < 0x1F800:
                kind = "máquina interior 27 estados"
            elif 0x1FB00 <= s < 0x1FCC0:
                kind = "máquina de 6 estados (dentro de la interior)"
            else:
                kind = "otro"
            out[f"{prim:#x}"].append({"site": f"{s:#x}", "class": kind})
    return out


def initcom_model(img: Image) -> dict:
    """Modelo byte a byte del handler InitCom 0x16 (escritura/lectura)."""
    # Dispatch 0x4cd8..0x4cea: cmp r1,#0x11/#0x12/#0x13/#0x16.
    dispatch = [ins_at(img, a) for a in (0x4CDC, 0x4CE0, 0x4CE4, 0x4CE8)]
    # 0x16: address=u32(frame[1..4]), length=frame[5], bit7=escritura.
    write = {
        "length_load": ins_at(img, 0x4CFC),
        "mask_check": ins_at(img, 0x4D02),
        "bit7_test": ins_at(img, 0x4D0A),
        "copy_len": ins_at(img, 0x4DC8),
        "copy_call": ins_at(img, 0x4DCE),
        "copy_function": "0x255a6 (memcpy(dst,src,n))",
        "frame_bytes": 0x80,
        "write_length_byte": 0x81,
        "copy_length_with_bit7": 0x81,
        "copy_length_masked": 0x01,
        "destination_start": "0x20000050",
        "destination_end_exclusive": "0x200000d1",
        "bytes_written": 0x81,
        "selective_one_byte": False,
        "note": (
            "El chequeo previo usa length&0x7f, pero el memcpy usa r4 completo. "
            "Con 0x81 (bit7=1, longitud 1) copia 129 B, no 1 B. El modelo de E25 "
            "que asumía 1 B es incorrecto."
        ),
    }
    read = {
        "bit7_test": ins_at(img, 0x4D0A),
        "memset": ins_at(img, 0x4DDC),
        "copy_len": ins_at(img, 0x4DE0),
        "copy_call": ins_at(img, 0x4DE6),
        "copy_length": 0x01,
        "selective": True,
        "note": "Con bit7=0 y longitud 1 lee 1 B de la dirección y lo devuelve en la trama.",
    }
    block = {
        "handler": "0x4d40",
        "destination_rule": "0x20000000 + n*0x78 (resto 0x78 == 0)",
        "copy_len": ins_at(img, 0x4D4A) + " / " + ins_at(img, 0x4D68),
        "block_bytes": 0x78,
        "gate_offset": "0x50",
        "watchdog_offsets": ["0x31", "0x32", "0x40", "0x41", "0x42", "0x43"],
        "selective": False,
        "note": "Escribe el bloque completo; para tocar +0x50 hay que enviar >=0x51 B y el resto (WDG incluido) queda a merced del payload.",
    }
    return {
        "dispatch": dispatch,
        "command_0x16_write": write,
        "command_0x16_read": read,
        "command_0x12_block": block,
        "window": {
            "initcom": "0x4bca",
            "initcom_callers": [f"{a:#x}" for a in img.bl_callers(0x4BCA)],
            "com_task": "0xece4",
            "com_task_created_in_seton": "0x7462 (literal 0xece5)",
            "states_without_initcom": ["On", "Off", "Upd", "captura"],
        },
    }


def initcom_write_demo() -> dict:
    """Control diferencial del modelo de escritura: 1 B declarado vs 129 B copiados."""
    frame = bytearray(0x80)
    frame[1:5] = (0x20000050).to_bytes(4, "little")
    frame[5] = 0x81
    frame[6:] = bytes([0xAA]) * (0x80 - 6)
    length = frame[5]
    masked = length & 0x7F
    copied = length  # 0x4dc8: mov r2,r4
    return {
        "declared_length": masked,
        "written_bytes": copied,
        "destination": "0x20000050",
        "end_exclusive": f"{0x20000050 + copied:#x}",
        "first_byte": "0xaa",
        "overwrites_gate_and_next_128_bytes": True,
    }


def build() -> dict:
    original = Image(ORIGINAL)
    tipo0 = Image(TIPO0)
    candidate = Image(CANDIDATE)

    for img, sha, name in ((original, SHA_ORIGINAL, "original_321"),
                           (tipo0, SHA_TIPO0, "tipo0_322"),
                           (candidate, SHA_CANDIDATE, "candidato_e25")):
        if img.sha256() != sha:
            raise SystemExit(f"{name}: SHA-256 {img.sha256()} != {sha}")

    patch_before = tipo0.bytes(GATE_BRANCH, 2)
    patch_after = candidate.bytes(GATE_BRANCH, 2)
    target = branch_target_n(candidate, GATE_BRANCH)

    # Diferencial: tipo 0 -> candidato solo 2 bytes.
    diff_tipo0 = [
        (i + BASE, tipo0.data[i], candidate.data[i])
        for i in range(len(tipo0.data)) if tipo0.data[i] != candidate.data[i]
    ]
    # Diferencial: original -> candidato = tipo 0 + compuerta.
    diff_original = [
        (i + BASE, original.data[i], candidate.data[i])
        for i in range(len(original.data)) if original.data[i] != candidate.data[i]
    ]

    gate_path = []
    for ins in candidate.dis(GATE, 0x22):
        gate_path.append(f"{ins.address:#x}: {ins.mnemonic} {ins.op_str}")

    # El camino parcheado no debe contener 0x1b080 ni la tabla.
    patched_insns = [i for i in candidate.dis(GATE, 0x20)
                     if i.address in (0x1FE66, 0x1FE68, 0x1FE6A, GATE_EPILOGUE, 0x1FE84)]
    patched_text = " | ".join(f"{i.address:#x}: {i.mnemonic} {i.op_str}" for i in patched_insns)

    starters = decode_starters(candidate)
    outer = outer_table(candidate)
    consumers = decode_consumers(candidate)

    # Semántica diferencial de la compuerta: 256 valores de byte.
    gate_semantics = {
        "original": {f"0x{b:02x}": original_gate_value(b) for b in range(256)},
        "candidato": {f"0x{b:02x}": patched_gate_value() for b in range(256)},
        "original_summary": "0 si nibble alto 0 o >=6; nibble alto 1..5 en otro caso",
        "candidato_summary": "0 siempre",
    }

    # Tipo 0: bytes y filtro de P4D/P4E.
    tipo0_state = {
        "bytes": candidate.bytes(TIPO0_ADDR, len(TIPO0_BYTES)).hex(),
        "expected": TIPO0_BYTES.hex(),
        "unchanged_vs_tipo0": candidate.bytes(TIPO0_ADDR, len(TIPO0_BYTES)) == TIPO0_BYTES,
        "gate_20c74": [
            f"{i.address:#x}: {i.mnemonic} {i.op_str}"
            for i in candidate.dis(0x20C74, 0x20)
        ],
        "p4d_writer_20c90": [
            f"{i.address:#x}: {i.mnemonic} {i.op_str}"
            for i in candidate.dis(0x20C90, 0x20)
        ],
    }

    # Llamadores directos del motor y prueba de ausencia de punteros absolutos.
    motor_refs = {}
    for addr in list(MOTOR_CALLERS) + [GATE, 0x1F5A6, 0x1FCB8]:
        motor_refs[f"{addr:#x}"] = {
            "word_refs": [f"{x:#x}" for x in candidate.word_refs(addr)],
            "imm_refs": [f"{x:#x}: {t}" for x, t in candidate.imm_refs({addr})],
        }

    # Operación 5: 0x1f600 -> 0x1fcb8 -> 0x1feb6 -> 0x51cc(4,3,0xfffc).
    op5 = {
        "entry": "0x1f600",
        "calls_1fcb8": ins_at(candidate, 0x1F606),
        "wait_1fcb8": ins_at(candidate, 0x1FCBE),
        "brake_call_1fcb8": ins_at(candidate, 0x1FCBA),
        "write_1feb6": [f"{i.address:#x}: {i.mnemonic} {i.op_str}"
                         for i in candidate.dis(0x1FEB6, 0x18)],
        "p40": 1,
        "p41": 1,
        "xor": 0,
        "value": 3,
        "meaning": "XOR=0: la salida del IC6800 no excita Q6801; no es una orden de movimiento. El efecto físico (coast/brake) no está medido.",
        "circuit": "Manual de servicio: IC6800 TC7SH86FU, IN_A=SC_M_2 (P41), IN_B=SC_M_1 (P40), OUT_Y -> Q6800 -> Q6801 -> CHARGE MOTOR.",
    }

    # P4B/P4C: escritores y llamadores; el parche no los toca.
    pins = {
        "P4C": {
            "writer": "0x1ecec -> 0x51c0(0x230, r1)",
            "callers": [f"{a:#x}" for a in candidate.bl_callers(0x1ECEC)],
            "patch_untouched": candidate.bytes(0x1ECEC, 0x10) == original.bytes(0x1ECEC, 0x10),
        },
        "P4B": {
            "writer": "0xd176/0xd1e8 -> 0x51c0(0x22c, r1)",
            "mask": "0x800 (bit 11, ocupación)",
            "readers": "0xd276/0x1ecdc -> 0x51c6(0x22c)",
            "patch_untouched": candidate.bytes(0xD176, 0x10) == original.bytes(0xD176, 0x10),
        },
        "P4D": {"writer": "0x20c90/0x20cb2", "filter": "0x20c74 con tipo 0"},
        "P4E": {"writer": "0x20d00/0x20cd4", "filter": "0x20c74 con tipo 0"},
    }

    # Cancelación: el único llamador de 0x4ed8 es 0xed18 (epílogo de Seton main).
    cancellation = {
        "e25_claimed": "COM 0xed18 / 0x4ed8",
        "actual": "bandera de parada de InitCom, no una cancelación de captura",
        "callers_4ed8": [f"{a:#x}" for a in candidate.bl_callers(0x4ED8)],
        "callers_ed18": [f"{a:#x}" for a in candidate.bl_callers(0xED18)],
        "seton_main_range": "0x747a-0x755c",
        "real_abort_candidate": "estado 0x17 (0x189d4) -> 0x16e26 -> 0x16dc0 -> 0x16558(2,0x30) -> op5",
        "real_abort_verified_bytes": [
            f"{i.address:#x}: {i.mnemonic} {i.op_str}"
            for i in candidate.dis(0x16DC0, 0x30)
        ],
        "real_abort_effect": "op5 (P40/P41=3, XOR=0), sin compuerta; no se identificó una cancelación de usuario que mueva el motor por otra vía.",
    }

    # InitCom: no hay escritor estático de 0x20000050 en el core.
    static_writer = {
        "literal_0x20000050": [f"{x:#x}" for x in candidate.word_refs(0x20000050)],
        "literal_0x22000a00": [f"{x:#x}" for x in candidate.word_refs(0x22000A00)],
        "note": "Sin literal ni alias de bit; el byte solo lo escriben InitCom 0x12/0x16 o el arranque (sin binario).",
    }

    # Arranque/Seton: InitCom solo existe en la tarea COM creada en Seton.
    seton = {
        "com_task_literal": ins_at(candidate, 0x7460) + " / " + ins_at(candidate, 0x7462),
        "initcom_callers": [f"{a:#x}" for a in candidate.bl_callers(0x4BCA)],
        "gate_consumers_outside_capture": {
            "reset": False,
            "initcom": False,
            "upd": False,
            "off": False,
        },
    }

    return {
        "schema": "a6000.e25_02.audit.v1",
        "scope": "offline; sin cámara, sin USB, sin RAM/NVRAM/NAND, sin FDAT/DAT",
        "binaries": {
            "original": {"path": str(ORIGINAL.relative_to(ROOT)), "sha256": original.sha256(), "size": len(original.data)},
            "tipo0": {"path": str(TIPO0.relative_to(ROOT)), "sha256": tipo0.sha256(), "size": len(tipo0.data)},
            "candidate": {"path": str(CANDIDATE.relative_to(ROOT)), "sha256": candidate.sha256(), "size": len(candidate.data)},
        },
        "patch": {
            "address": f"{GATE_BRANCH:#x}",
            "file_offset": GATE_BRANCH - BASE,
            "old": patch_before.hex(),
            "new": patch_after.hex(),
            "target": f"{target:#x}",
            "expected_target": f"{GATE_EPILOGUE:#x}",
            "diff_vs_tipo0": [{"rom": f"{a:#x}", "before": f"{b:02x}", "after": f"{c:02x}"} for a, b, c in diff_tipo0],
            "diff_vs_original_count": len(diff_original),
            "gate_path": gate_path,
            "patched_instructions": patched_text,
            "path_executes_0x1b080": False,
            "path_executes_table": False,
            "stack_push": ins_at(candidate, GATE),
            "stack_pop": ins_at(candidate, 0x1FE84),
            "r5_init": ins_at(candidate, 0x1FE68),
            "return_value": "0",
        },
        "gate_semantics": {
            "original_summary": gate_semantics["original_summary"],
            "candidate_summary": gate_semantics["candidato_summary"],
            "original_values_0_to_15": {hex(b >> 4): original_gate_value(b) for b in range(0, 256, 16)},
            "candidate_values_0_to_15": {hex(b >> 4): 0 for b in range(0, 256, 16)},
        },
        "starters": starters,
        "lists": {
            "L0": {"addr": "0x29cd8", "ids": list_bytes(candidate, 0x29CD8)},
            "L1": {"addr": "0x29cdd", "ids": list_bytes(candidate, 0x29CDD)},
            "L2": {"addr": "0x29ce3", "ids": list_bytes(candidate, 0x29CE3)},
            "L3": {"addr": "0x29ce9", "ids": list_bytes(candidate, 0x29CE9)},
        },
        "outer": {
            "handlers": {f"{k:#x}": f"{v:#x}" for k, v in outer.items()},
            "state2_handler": f"{outer.get(2, 0):#x}",
            "state4_handler": f"{outer.get(4, 0):#x}",
            "state2_starts_inner": f"{candidate.bl_callers(0x1F396)[0]:#x}" if candidate.bl_callers(0x1F396) else None,
            "state4_starts_inner": f"{candidate.bl_callers(0x1F3B6)[0]:#x}" if candidate.bl_callers(0x1F3B6) else None,
            "inner_entry_word_refs": {
                "0x1f396": [f"{x:#x}" for x in candidate.word_refs(0x1F396)],
                "0x1f3b6": [f"{x:#x}" for x in candidate.word_refs(0x1F3B6)],
            },
        },
        "consumers": consumers,
        "tipo0": tipo0_state,
        "motor_callers": classify_motor_callers(),
        "motor_absolute_refs": motor_refs,
        "operation5": op5,
        "pins": pins,
        "cancellation": cancellation,
        "initcom": initcom_model(candidate),
        "initcom_write_demo": initcom_write_demo(),
        "static_gate_writer": static_writer,
        "seton": seton,
        "verdicts": {
            "A_volatile": "NO",
            "A_reason": "No hay emisor BIONZ de InitCom 0x16 en el software oficial; el updater solo envía 0x11/0x14/0x15 y el servicio Micon (0x40) es un NoAction. Además, 0x16 no es una escritura selectiva de 1 B: copia 129 B con length=0x81.",
            "B1a_static": "VÁLIDO ESTÁTICAMENTE",
            "B1a_reason": "2 bytes, salto al epílogo, r5=0, pila/registros/retorno conservados, sin lectura de 0x1b080, L0 en los tres arrancadores, tipo 0 intacto.",
            "M0_normal_static": "SÍ",
            "M0_physical": "NO MEDIDO",
            "M1_capture_complete": "NO DEMOSTRADO",
            "recovery": "NO DEMOSTRADA",
            "installable": "NO",
        },
    }


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    data = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
        print(f"escrito {OUT.relative_to(ROOT)}")
    else:
        print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
