"""E15/E12: receptor del buzón OSAL 0x0110027c. Emisores en av-cam (Thumb), libObj.so y upm.ko; receptor en kikilog.ko.
Solo bytes originales (más `nm`/`readelf` para símbolos y relocaciones del módulo). Salida: e15_kikilog.json."""
import json
import re
import struct
import subprocess
from pathlib import Path

import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ID = 0x0110027C
ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
OUT = Path(__file__).with_name("e15_kikilog.json")
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def thumb_refs(blob: bytes, base: int = 0) -> list[int]:
    """Direcciones de `ldr rN,[pc,#imm]` (Thumb-16) cuya palabra de pool vale ID."""
    out = []
    for o in range(0, len(blob) - 1, 2):
        h = struct.unpack_from("<H", blob, o)[0]
        if h & 0xF800 == 0x4800:
            p = ((o + 4) & ~3) + (h & 0xFF) * 4
            if p + 4 <= len(blob) and struct.unpack_from("<I", blob, p)[0] == ID:
                out.append(base + o)
    return out


def arm_refs(blob: bytes, text_off: int, text_size: int) -> list[int]:
    """Offsets (en .text) de `ldr rN,[pc,#imm]` ARM (cond AL) cuya palabra de pool vale ID."""
    out = []
    for o in range(0, text_size, 4):
        w = struct.unpack_from("<I", blob, text_off + o)[0]
        if w & 0x0F7F0000 == 0x051F0000 and w >> 28 == 0xE:
            imm = w & 0xFFF
            p = o + 8 + (imm if w & 0x00800000 else -imm)
            if 0 <= p < text_size and struct.unpack_from("<I", blob, text_off + p)[0] == ID:
                out.append(o)
    return out


def emitters(blob: bytes) -> list[dict]:
    refs = [r for r in thumb_refs(blob, pic.BASE)]
    out = []
    for alloc, send in zip(refs[::2], refs[1::2]):
        regs: dict[str, int] = {}
        wr: dict[int, int | str] = {}
        for i in CS.disasm(blob[alloc - pic.BASE:send - pic.BASE + 4], alloc):
            m = re.match(r"(r\d+), #(-?(?:0x)?[0-9a-f]+)$", i.op_str)
            if i.mnemonic in ("movs", "mov", "movw") and m:
                regs[m.group(1)] = int(m.group(2), 0)
            m = re.match(r"(r\d+), \[(r\d+)(?:, #(-?(?:0x)?[0-9a-f]+))?\]$", i.op_str)
            if i.mnemonic in ("strh", "str") and m and m.group(2) != "sp":
                wr[int(m.group(3) or "0", 0)] = regs.get(m.group(1), "arg")
        out.append({"alloc": hex(alloc), "send": hex(send),
                    "campos": {hex(k): (hex(v) if isinstance(v, int) else v) for k, v in sorted(wr.items())}})
    return out


def relocs_in(path: Path, symbol: str) -> list[str]:
    nm = subprocess.run(["nm", "-S", str(path)], capture_output=True, text=True, check=True).stdout
    m = re.search(rf"^([0-9a-f]+) ([0-9a-f]+) [Tt] {symbol}$", nm, re.MULTILINE)
    assert m, symbol
    lo, sz = int(m.group(1), 16), int(m.group(2), 16)
    rel = subprocess.run(["readelf", "-rW", str(path)], capture_output=True, text=True, check=True).stdout
    return [r.split()[-1] for r in rel.splitlines()
            if re.match(r"^[0-9a-f]{8} ", r) and lo <= int(r.split()[0], 16) < lo + sz and "R_ARM_CALL" in r]


def section(path: Path, name: str) -> tuple[int, int]:
    out = subprocess.run(["readelf", "-SW", str(path)], capture_output=True, text=True, check=True).stdout
    m = re.search(rf"\] {re.escape(name)}\s+PROGBITS\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)", out)
    assert m, name
    return int(m.group(1), 16), int(m.group(2), 16)


def main() -> None:
    av = pic.load("a6000")
    lib = (DEV / "lib/libObj.so").read_bytes()
    upm = (DEV / "kmod/upm.ko").read_bytes()
    kik_path = DEV / "kmod/kikilog.ko"
    kik = kik_path.read_bytes()
    kt_off, kt_size = section(kik_path, ".text")
    kd_off, kd_size = section(kik_path, ".data")
    ut_off, ut_size = section(DEV / "kmod/upm.ko", ".text")
    data_hits = [hex(kd_off + o) for o in range(0, kd_size, 4) if struct.unpack_from("<I", kik, kd_off + o)[0] == ID]
    av_emisores = emitters(av)
    res = {
        "id": hex(ID),
        "av_cam": {"palabras_de_pool": len([o for o in range(0, len(av) - 3, 4) if struct.unpack_from("<I", av, o)[0] == ID]),
                   "emisores": av_emisores},
        "libObj_refs_ldr": len(thumb_refs(lib)),
        "upm_ko_refs_ldr": len(arm_refs(upm, ut_off, ut_size)),
        "kikilog_ko": {
            "main_thread_llamadas": relocs_in(kik_path, "kikilog_main_thread"),
            "record_log_llamadas": relocs_in(kik_path, "record_log"),
            "init_udate_datechg_llamadas": relocs_in(kik_path, "init_udate_datechg"),
            "exit_kikilog_llamadas": relocs_in(kik_path, "exit_kikilog"),
            "refs_ldr_en_text": len(arm_refs(kik, kt_off, kt_size)),
            "id_en_data_offsets": data_hits,
        },
    }
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "av_cam"}, indent=1))
    print(len(av_emisores), "emisores av-cam")


if __name__ == "__main__":
    main()
