"""S60: recorrido offline de los dos mensajes de temporización, con bytes reales."""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/s58"))
from tdis import B, data
from unicorn.arm_const import UC_ARM_REG_R1, UC_ARM_REG_R2
from wtrace import W

SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
OBJ = 0x45400000
DST = 0x45500000
MEMCPY = [(0x43B7F878, 0x43B7F880), (0x439C5320, 0x439C5A04)]


def case_targets():
    blob = data("A6000")
    table = 0x43806A08
    return {i: 0x43806A04 + 2 * struct.unpack_from("<H", blob, table - B + i * 2)[0]
            for i in range(12)}


def stage_state_one():
    """Ejecuta publicación original: imagen inicial inyectada, no captura real."""
    w = W(ambito=[(0x43B00DD4, 0x43B00E40), (0x43B00D94, 0x43B00DD4)] + MEMCPY)
    w.u.mem_write(OBJ, bytes(0xF00))
    before = bytes(range(80))
    next_value = bytes((i + 80) % 256 for i in range(80))
    w.u.mem_write(OBJ + 0xD64, before)
    w.u.mem_write(OBJ + 0xE04, next_value)
    w.u.mem_write(OBJ + 0x57C, b"\x01")
    w.w32(OBJ + 0x568, 1)
    w.call(0x43B00DD4, OBJ)
    return w, before, next_value


def emit(w, address):
    """Ejecuta constructor original y captura el argumento antes del servicio OSAL."""
    sent = []

    def capture(machine):
        pointer = machine.u.reg_read(UC_ARM_REG_R1)
        size = machine.u.reg_read(UC_ARM_REG_R2)
        sent.append((pointer, machine.rd(pointer, size)))
        return 1

    w.stubfn[0x43806400] = capture
    w.ambito += [(0x43B00CB4, 0x43B00CBA), (address, address + 0x42)]
    w.call(address, OBJ)
    if len(sent) != 1:
        raise AssertionError(f"envíos observados: {len(sent)}")
    return sent[0]


def receiver_copy(payload, offset):
    w = W(ambito=[(0x43B00D94, 0x43B00DA0)] + MEMCPY)
    w.u.mem_write(DST, bytes(0xF00))
    source = 0x45600000
    w.u.mem_write(source, payload)
    w.call(0x43B00D94, DST, source + offset)
    return w.rd(DST + 0xD64, 80), w.stubbed


def publish_state_two(value):
    w = W(ambito=[(0x43B00DD4, 0x43B00E40), (0x43B00D94, 0x43B00DD4)] + MEMCPY)
    w.u.mem_write(DST, bytes(0xF00))
    w.u.mem_write(DST + 0xD64, value)
    w.u.mem_write(DST + 0x57C, b"\x01")
    w.w32(DST + 0x568, 2)
    w.call(0x43B00DD4, DST)
    return w.rd(DST + 0xDD0, 24), w.stubbed


def probe():
    actual = hashlib.sha256(data("A6000")).hexdigest()
    if actual != SHA:
        raise ValueError(f"SHA inesperado: {actual}")
    targets = case_targets()
    w, before, next_value = stage_state_one()
    case4_ptr, case4 = emit(w, 0x43B00FE6)
    case10_ptr, case10 = emit(w, 0x43B00F62)
    copy4, stub4 = receiver_copy(case4, 4)
    copy10, stub10 = receiver_copy(case10, 0x590)
    published4, stubpub4 = publish_state_two(copy4)
    published10, stubpub10 = publish_state_two(copy10)
    return {
        "sha256": actual,
        "case_targets": {str(k): hex(v) for k, v in targets.items()},
        "injected_source": before.hex(),
        "injected_next": next_value.hex(),
        "published_dd0": w.rd(OBJ + 0xDD0, 24).hex(),
        "staged_d64": w.rd(OBJ + 0xD64, 80).hex(),
        "staged_c50": w.rd(OBJ + 0xC50, 80).hex(),
        "case4": {"pointer": hex(case4_ptr), "size": len(case4), "type": case4[0],
                  "payload_4": case4[4:84].hex(), "payload_20": case4[0x20:0x38].hex()},
        "case10": {"pointer": hex(case10_ptr), "size": len(case10), "type": case10[0],
                   "payload_590": case10[0x590:0x5E0].hex(),
                   "payload_5ac": case10[0x5AC:0x5C4].hex()},
        "receiver_4": copy4.hex(), "receiver_10": copy10.hex(),
        "published_4_dd0": published4.hex(), "published_10_dd0": published10.hex(),
        "stubbed": {hex(k): v for k, v in w.stubbed.items()},
        "receiver_stubs": [stub4, stub10, stubpub4, stubpub10],
        "input_kind": "sintético",
        "reachability": "NO VERIFICADO",
    }


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2))
