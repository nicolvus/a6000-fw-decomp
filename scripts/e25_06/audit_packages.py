#!/usr/bin/env python3
"""E25-06 — auditoría independiente de los paquetes 3.23 (B1a) y 3.24 (recuperación).

Solo lectura y offline: no conecta la cámara, no usa USB, no ejecuta actualizaciones, no escribe
RAM/NVRAM/NAND y no modifica ningún paquete (todos los ficheros se abren con `mmap` de solo lectura).

Independencia respecto de E25-05 (`scripts/e25_05/build_packages.py`, `fwtool`):
- no importa `fwtool` ni `scripts/e25_05`; de `fwtool` solo lee las dos claves AES como datos (`ast`);
- el contenedor `.dat`, los bloques cifrados, la cabecera FDAT y el tar se analizan con parsers
  propios (`struct`, `zlib`, AES de `cryptography`, no `Cryptodome`);
- el descifrador se valida primero contra el `.dat` original de Sony (control positivo);
- la semántica de Darwin se comprueba emulando el código con Unicorn (control diferencial
  original / tipo 0 / B1a), no con Capstone/REA/Ghidra como en E25/E25-02.

Uso:
    .venv/bin/python scripts/e25_06/audit_packages.py           # imprime el resumen
    .venv/bin/python scripts/e25_06/audit_packages.py --write   # escribe analysis/e25-06/audit.json

Informe: docs/capture/e25-06-auditoria-independiente-paquetes.md
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import mmap
import struct
import sys
import zlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2]
FDAT_ROOT = ROOT / "analysis/darwin-patch/fdat"
FW = ROOT / "firmware/extracted/fw321"
OUT = ROOT / "analysis/e25-06/audit.json"
MANI = ROOT / "analysis/e25-05"

EXP_DIR = FDAT_ROOT / "experimental-323"
REC_DIR = FDAT_ROOT / "recuperacion-324"
REC323_DIR = FDAT_ROOT / "recuperacion-323"
SONY_DAT = FW.parent / "updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat"
SONY_FDAT = FW / "firmware.fdat"
OFFICIAL_TAR = FW / "firmware.tar"
OFFICIAL_UPDATER = FW / "updater.img"
OFFICIAL_CORE = FW / "firmware.tar_unpacked/0640_darwin/darwin_core.bin"
OFFICIAL_SUM = FW / "firmware.tar_unpacked/0641_darwin_sum/darwin.sum"
TIPO0_CORE = ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin"
TIPO0_SUM = ROOT / "analysis/darwin-patch/darwin.sum.tipo0"
TIPO0_TAR = FDAT_ROOT / "firmware_tipo0.tar"
B1A_CORE = ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin"
CONSTANTS = ROOT / "references/fwtool/fwtool/sony/constants.py"

# Valores declarados por la orden E25-06 (tecleados aparte, no leídos de los manifiestos) ------------
MODEL = 0x41030035
DAT_SIZE = 212_988_056
FDAT_SIZE = 212_155_392
UPDATER_SHA = "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
TIPO0_SHA = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
OFFICIAL_CORE_SHA = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
OFFICIAL_TAR_SHA = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
B1A_SHA = "55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d"
EXP_SUM_LINE = b"0,cf930ac9,0002665c,000001a4,00000000,000003e8,root,root,-1,-1,darwin_core.bin,\n"


@dataclass(frozen=True)
class Expect:
    """Lo que un paquete debe contener según la orden E25-06."""

    name: str
    minor: int
    dat_sha: str
    fdat_sha: str
    tar_sha: str
    core_sha: str
    core_crc: str


EXPECT_EXP = Expect("experimental-323", 0x23,
                    "4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542",
                    "268621fb70948fc58676bb19bcf82e7d73a2634d0085e3032d64833b04fc6e49",
                    "ae6d76eae9ff9363a42a60e37a8703b67c401fa3a81679259c4e73a0f1c402ee",
                    B1A_SHA, "cf930ac9")
EXPECT_REC = Expect("recuperacion-324", 0x24,
                    "e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22",
                    "24ee9b42e9fae29c7a86ec5f17d85d9a5076a8a36698a3766e0b13801126b2c2",
                    OFFICIAL_TAR_SHA, OFFICIAL_CORE_SHA, "9ff7148c")

# Paquetes anteriores: SHA-256 registrados en git antes de E25-05 (commit donde aparecen por primera vez).
PREVIOUS = {
    "fdat/firmware_packed.dat (3.22 instalado, T024)":
        (FDAT_ROOT / "firmware_packed.dat", "c19a1463a14d2b8038289240aa68d62dfa0de7e07b0db5c513e99565db3305a6", "54ad3b7f"),
    "fdat/firmware_packed.fdat (3.22 instalado, T024)":
        (FDAT_ROOT / "firmware_packed.fdat", "ddc2d5db41cfd049be6b64d702f544ecb6b8e92f6150782097ddb95dccb33295", "54ad3b7f"),
    "recuperacion-323/firmware_packed.dat":
        (REC323_DIR / "firmware_packed.dat", "5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf", "fb5a1e3d"),
    "recuperacion-323/firmware_packed.fdat":
        (REC323_DIR / "firmware_packed.fdat", "cfb65c8aad8ac8a3ccb1c4c758d485feee1ebf2e83e503d9c62d59fb96b01ce4", "fb5a1e3d"),
    "darwin_core_tipo0.bin": (TIPO0_CORE, TIPO0_SHA, "fb5a1e3d"),
    "darwin_core.bin oficial 3.21": (OFFICIAL_CORE, OFFICIAL_CORE_SHA, "ee2a3732"),
    "firmware.tar oficial 3.21": (OFFICIAL_TAR, OFFICIAL_TAR_SHA, "ee2a3732"),
    "updater.img oficial 3.21": (OFFICIAL_UPDATER, UPDATER_SHA, "ee2a3732"),
    "FirmwareData_ILCE6000V321.dat (Sony)":
        (SONY_DAT, "29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f", "firmware/hashes/sha256.json"),
    "B1a darwin_core_tipo0_sin_rearme.bin": (B1A_CORE, B1A_SHA, "efaf228b"),
}

DAT_MAGIC = bytes.fromhex("895546550d0a1a0a")
FDAT_HDR = 512
BLOCK = 1024
DARWIN_CORE = "0640_darwin/darwin_core.bin"
DARWIN_SUM = "0641_darwin_sum/darwin.sum"
BASE = 0x4200


class Checks:
    """Lista ordenada de comprobaciones; nunca aborta: una FAIL queda registrada."""

    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(self, cid: str, ok: bool, detail: Any = "") -> bool:
        self.items.append({"id": cid, "result": "PASS" if ok else "FAIL", "detail": detail})
        return ok

    def missing(self, cid: str, detail: str) -> None:
        self.items.append({"id": cid, "result": "MISSING", "detail": detail})

    def failed(self) -> list[str]:
        return [c["id"] for c in self.items if c["result"] != "PASS"]

    def result(self, cid: str) -> str:
        return next(c["result"] for c in self.items if c["id"] == cid)


# ------------------------------------------------------------------------------------------- utilidades
def open_ro(path: Path) -> mmap.mmap:
    with path.open("rb") as f:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)


def sha256_buf(buf: Any) -> str:
    h = hashlib.sha256()
    mv = memoryview(buf)
    for off in range(0, len(mv), 1 << 24):
        h.update(mv[off:off + (1 << 24)])
    return h.hexdigest()


def diff_ranges(a: Any, b: Any, chunk: int = 1 << 20) -> list[list[int]]:
    """Rangos [inicio, fin) donde dos buffers del mismo tamaño difieren."""
    if len(a) != len(b):
        raise ValueError(f"tamaños distintos: {len(a)} != {len(b)}")
    ma, mb = memoryview(a), memoryview(b)
    out: list[list[int]] = []
    for off in range(0, len(ma), chunk):
        ca, cb = bytes(ma[off:off + chunk]), bytes(mb[off:off + chunk])
        if ca == cb:
            continue
        for i, (x, y) in enumerate(zip(ca, cb)):
            if x == y:
                continue
            pos = off + i
            if out and out[-1][1] == pos:
                out[-1][1] = pos + 1
            else:
                out.append([pos, pos + 1])
    return out


def load_keys() -> tuple[bytes, bytes]:
    """Lee `key_aes` y `key_cxd90014` de fwtool como literales (sin importar su código)."""
    tree = ast.parse(CONSTANTS.read_text())
    keys: dict[str, bytes] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, bytes):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    keys[t.id] = node.value.value
    return keys["key_aes"], keys["key_cxd90014"]


# ------------------------------------------------------------------------------------------- contenedor .dat
def parse_dat(buf: Any) -> dict[str, Any]:
    """Contenedor `.dat`: magia, chunks big-endian, DATV/PROV/UDID y CRC-32 de DEND."""
    if bytes(buf[:8]) != DAT_MAGIC:
        return {"magic_ok": False}
    chunks: list[tuple[str, int, int]] = []
    off = 8
    while off + 8 <= len(buf):
        size, ctype = struct.unpack_from(">I4s", buf, off)
        chunks.append((ctype.decode("latin1"), off + 8, size))
        off += 8 + size
        if ctype == b"DEND":
            break
    named = {t: (o, s) for t, o, s in chunks}
    info: dict[str, Any] = {
        "magic_ok": True,
        "chunks": [[t, o, s] for t, o, s in chunks],
        "end": off,
        "trailing": len(buf) - off,
    }
    if "DEND" in named and named["DEND"][1] == 4 and off <= len(buf):
        dend_off = named["DEND"][0]
        info["dend_stored"] = f"{struct.unpack_from('>I', buf, dend_off)[0]:08x}"
        info["dend_computed"] = f"{zlib.crc32(memoryview(buf)[:dend_off - 8]):08x}"
    if "DATV" in named:
        info["datv"] = list(struct.unpack_from(">HH", buf, named["DATV"][0]))
    if "PROV" in named:
        info["prov"] = struct.unpack_from(">H", buf, named["PROV"][0])[0]
    if "UDID" in named:
        o, s = named["UDID"]
        count = struct.unpack_from(">I", buf, o)[0]
        info["udid_raw"] = bytes(buf[o:o + s]).hex()
        info["udid"] = [list(struct.unpack_from(">HHB", buf, o + 4 + 8 * i)) for i in range(count)]
    if "FDAT" in named:
        info["fdat_offset"], info["fdat_size"] = named["FDAT"]
    return info


def check_dat(c: Checks, p: str, info: dict[str, Any], sony: dict[str, Any] | None) -> None:
    c.add(f"{p}.dat.magic", info["magic_ok"], "89 55 46 55 0d 0a 1a 0a")
    if not info["magic_ok"]:
        return
    order = [t for t, _, _ in info["chunks"]]
    c.add(f"{p}.dat.chunk_order", order == ["DATV", "PROV", "UDID", "FDAT", "DEND"], order)
    c.add(f"{p}.dat.no_trailing", info["trailing"] == 0, f"{info['trailing']} B tras DEND")
    c.add(f"{p}.dat.dend_crc", info.get("dend_stored") == info.get("dend_computed") is not None,
          f"almacenado {info.get('dend_stored')} / calculado {info.get('dend_computed')}")
    c.add(f"{p}.dat.datv", info.get("datv") == [0x100, 0], f"dataVersion/isLens = {info.get('datv')} (isLens 0: no es objetivo)")
    c.add(f"{p}.dat.prov", info.get("prov") == 0x100, f"protocolVersion = {info.get('prov')}")
    c.add(f"{p}.dat.fdat_block_multiple", info.get("fdat_size", 1) % BLOCK == 0, f"FDAT cifrado {info.get('fdat_size')} B")
    if sony is not None:
        c.add(f"{p}.dat.udid_equals_sony", info.get("udid_raw") == sony.get("udid_raw"),
              "descriptores USB idénticos byte a byte a los del .dat original de Sony")
        same_layout = [t for t, _, _ in sony["chunks"]] == order and all(
            a[2] == b[2] for a, b in zip(sony["chunks"], info["chunks"]) if a[0] != "FDAT")
        c.add(f"{p}.dat.layout_equals_sony", same_layout, "mismo orden y tamaño de chunks que el .dat de Sony (salvo FDAT)")


# ------------------------------------------------------------------------------------------- bloques cifrados
@dataclass
class Decrypted:
    blocks: int = 0
    bad_sum: list[int] = field(default_factory=list)
    bad_flag: list[int] = field(default_factory=list)
    bad_len: list[int] = field(default_factory=list)
    pad_not_ff: bool = False
    plain_size: int = 0
    sha256: str = ""
    first_mismatch_vs_fdat: int | None = None


def decrypt_fdat(buf: Any, off: int, size: int, keys: tuple[bytes, bytes], compare: Any = None) -> Decrypted:
    """Descifra el FDAT (esquema CXD90014: AES-ECB doble salvo los 512 B iniciales del primer bloque).

    Comprueba en cada bloque de 1024 B la suma de 16 bits, la bandera de último bloque y la longitud.
    No guarda el texto plano: lo resume con SHA-256 y, si se da `compare`, lo compara en streaming.
    """
    d1 = Cipher(algorithms.AES(keys[0]), modes.ECB()).decryptor()
    d2 = Cipher(algorithms.AES(keys[1]), modes.ECB()).decryptor()
    res = Decrypted(blocks=size // BLOCK)
    h = hashlib.sha256()
    mv = memoryview(buf)
    cmp = memoryview(compare) if compare is not None else None
    pos = 0
    step = BLOCK * 1024
    for cstart in range(0, size - size % BLOCK, step):
        enc = mv[off + cstart:off + min(cstart + step, size - size % BLOCK)]
        p1 = d1.update(enc)
        plain = d2.update(p1)
        if cstart == 0:
            plain = p1[:512] + plain[512:]
        for i in range(0, len(plain), BLOCK):
            idx = (cstart + i) // BLOCK
            blk = plain[i:i + BLOCK]
            stored, size_flag = struct.unpack_from("<HH", blk)
            if sum(struct.unpack_from("<511H", blk, 2)) & 0xFFFF != stored:
                res.bad_sum.append(idx)
            last = idx == res.blocks - 1
            if bool(size_flag & 0x8000) != last:
                res.bad_flag.append(idx)
            length = size_flag & 0x7FFF
            if length > BLOCK - 4 or (not last and length != BLOCK - 4):
                res.bad_len.append(idx)
                length = min(length, BLOCK - 4)
            if last and set(blk[4 + length:]) - {0xFF}:
                res.pad_not_ff = True
            data = blk[4:4 + length]
            h.update(data)
            if cmp is not None and res.first_mismatch_vs_fdat is None:
                ref = bytes(cmp[pos:pos + length])
                if ref != data:
                    res.first_mismatch_vs_fdat = pos + next((k for k, (x, y) in enumerate(zip(ref, data)) if x != y), min(len(ref), len(data)))
            pos += length
    res.plain_size = pos
    res.sha256 = h.hexdigest()
    if cmp is not None and res.first_mismatch_vs_fdat is None and pos != len(cmp):
        res.first_mismatch_vs_fdat = min(pos, len(cmp))
    return res


def check_blocks(c: Checks, p: str, d: Decrypted) -> None:
    c.add(f"{p}.blocks.checksums", not d.bad_sum, f"{d.blocks} bloques; suma de 16 bits errónea en {d.bad_sum[:5]}")
    c.add(f"{p}.blocks.last_flag", not d.bad_flag, f"bandera de último bloque errónea en {d.bad_flag[:5]}")
    c.add(f"{p}.blocks.lengths", not d.bad_len, f"longitudes anómalas en {d.bad_len[:5]}")


# ------------------------------------------------------------------------------------------- cabecera FDAT
def parse_fdat_header(h: bytes) -> dict[str, Any]:
    u32 = lambda o: struct.unpack_from("<I", h, o)[0]
    fs = [{"mode": h[64 + 16 * i:65 + 16 * i].decode("latin1"), "offset": u32(68 + 16 * i), "size": u32(72 + 16 * i),
           "pad": h[65 + 16 * i:68 + 16 * i].hex() + h[76 + 16 * i:80 + 16 * i].hex()} for i in range(28)]
    return {
        "magic": h[0:8].decode("latin1"),
        "checksum_stored": f"{u32(8):08x}",
        "checksum_computed": f"{zlib.crc32(h[12:FDAT_HDR]):08x}",
        "format": h[12:16].decode("latin1"),
        "mode": h[16:17].decode("latin1"),
        "luw": h[20:21].decode("latin1"),
        "version_minor": h[32],
        "version_major": h[33],
        "version": f"{h[33]:x}.{h[32]:02x}",
        "model": u32(36),
        "region": u32(40),
        "firmware_offset": u32(48),
        "firmware_size": u32(52),
        "num_filesystems": u32(56),
        "reserved": (h[17:20] + h[21:32] + h[34:36] + h[44:48] + h[60:64]).hex(),
        "filesystems": fs,
    }


def check_fdat_header(c: Checks, p: str, h: bytes, total: int, minor: int, updater_size: int | None = None) -> dict[str, Any]:
    hd = parse_fdat_header(h)
    bcd = lambda v: (v >> 4) <= 9 and (v & 0xF) <= 9
    c.add(f"{p}.fdat.magic", hd["magic"] == "UDTRFIRM" and hd["format"] == "0100", f"{hd['magic']} / {hd['format']}")
    c.add(f"{p}.fdat.header_crc", hd["checksum_stored"] == hd["checksum_computed"],
          f"CRC-32 [12,512): almacenado {hd['checksum_stored']} / calculado {hd['checksum_computed']}")
    c.add(f"{p}.fdat.version_major", hd["version_major"] == 3, f"mayor {hd['version_major']:#x}")
    c.add(f"{p}.fdat.version_minor", hd["version_minor"] == minor and bcd(minor), f"menor {hd['version_minor']:#04x} (esperado {minor:#04x}, BCD)")
    c.add(f"{p}.fdat.model", hd["model"] == MODEL, f"modelo {hd['model']:#010x}")
    c.add(f"{p}.fdat.region", hd["region"] == 0, f"región {hd['region']}")
    c.add(f"{p}.fdat.not_accessory", hd["model"] & 0xFF0000 != 0xA00000, "modelo fuera de la familia de accesorios 0xA0xxxx")
    c.add(f"{p}.fdat.mode_luw", hd["mode"] == "U" and hd["luw"] == "N", f"modo {hd['mode']} / LUW {hd['luw']}")
    c.add(f"{p}.fdat.reserved_zero", set(bytes.fromhex(hd["reserved"])) <= {0}, "campos reservados a cero")
    fs = hd["filesystems"]
    user = fs[0]
    c.add(f"{p}.fdat.filesystems",
          hd["num_filesystems"] == 2 and user["mode"] == "U" and user["offset"] == FDAT_HDR
          and fs[1]["mode"] == "P" and fs[1]["offset"] == FDAT_HDR and fs[1]["size"] == 0
          and all(f["mode"] == "\x00" and f["offset"] == f["size"] == 0 for f in fs[2:])
          and all(set(bytes.fromhex(f["pad"])) <= {0} for f in fs),
          f"{hd['num_filesystems']} FS; U@{user['offset']}+{user['size']}, P@{fs[1]['offset']}+{fs[1]['size']}")
    c.add(f"{p}.fdat.offsets",
          hd["firmware_offset"] == FDAT_HDR + user["size"] and hd["firmware_offset"] + hd["firmware_size"] == total,
          f"updater [{user['offset']},{user['offset'] + user['size']}), tar [{hd['firmware_offset']},{hd['firmware_offset'] + hd['firmware_size']}), total {total}")
    if updater_size is not None:
        c.add(f"{p}.fdat.updater_size", user["size"] == updater_size, f"{user['size']} B")
    return hd


# ------------------------------------------------------------------------------------------- tar
def _octal(field_: bytes) -> int:
    if field_[:1] and field_[0] & 0x80:
        return int.from_bytes(field_[1:], "big")
    txt = field_.split(b"\0")[0].strip()
    return int(txt, 8) if txt else 0


def parse_tar(buf: Any) -> dict[str, Any]:
    """Parser ustar propio: cabeceras, sumas, tipos, padding y bloques de cierre."""
    mv = memoryview(buf)
    members: list[dict[str, Any]] = []
    off = 0
    problems: list[str] = []
    while off + 512 <= len(mv):
        hdr = bytes(mv[off:off + 512])
        if hdr == b"\0" * 512:
            break
        stored = _octal(hdr[148:156])
        computed = sum(hdr[:148]) + 8 * 32 + sum(hdr[156:])
        name = hdr[0:100].split(b"\0")[0].decode("latin1")
        prefix = hdr[345:500].split(b"\0")[0].decode("latin1")
        size = _octal(hdr[124:136])
        typeflag = hdr[156:157].decode("latin1")
        data_off = off + 512
        padded = (size + 511) // 512 * 512 if typeflag in ("0", "\0", "7") else 0
        pad = bytes(mv[data_off + size:data_off + padded]) if padded else b""
        m = {
            "name": f"{prefix}/{name}" if prefix else name,
            "header_offset": off,
            "data_offset": data_off,
            "size": size,
            "type": typeflag,
            "mode": _octal(hdr[100:108]),
            "uid": _octal(hdr[108:116]),
            "gid": _octal(hdr[116:124]),
            "mtime": _octal(hdr[136:148]),
            "magic": hdr[257:265].hex(),
            "uname": hdr[265:297].split(b"\0")[0].decode("latin1"),
            "gname": hdr[297:329].split(b"\0")[0].decode("latin1"),
            "checksum_ok": stored == computed,
            "padding_zero": set(pad) <= {0},
        }
        if not m["checksum_ok"]:
            problems.append(f"suma de cabecera errónea en {m['name']}")
        if not m["padding_zero"]:
            problems.append(f"padding no nulo en {m['name']}")
        if typeflag not in ("0", "\0", "5", "2", "1"):
            problems.append(f"tipo {typeflag!r} inesperado en {m['name']}")
        members.append(m)
        off = data_off + padded
    tail = bytes(mv[off:])
    return {
        "members": members,
        "end_offset": off,
        "tail_size": len(tail),
        "tail_zero": set(tail) <= {0},
        "tail_blocks": len(tail) // 512,
        "problems": problems,
    }


def member_bytes(buf: Any, tar: dict[str, Any], name: str) -> bytes:
    m = next(x for x in tar["members"] if x["name"] == name)
    return bytes(memoryview(buf)[m["data_offset"]:m["data_offset"] + m["size"]])


def check_tar_structure(c: Checks, p: str, tar: dict[str, Any], size: int) -> None:
    c.add(f"{p}.tar.headers_and_padding", not tar["problems"], tar["problems"][:5] or f"{len(tar['members'])} entradas")
    c.add(f"{p}.tar.end_blocks", tar["tail_zero"] and tar["tail_blocks"] >= 2 and tar["end_offset"] + tar["tail_size"] == size,
          f"{tar['tail_blocks']} bloques nulos de cierre")


def compare_tars(c: Checks, p: str, pkg: Any, ref: Any, tpkg: dict[str, Any], tref: dict[str, Any],
                 authorized: set[str]) -> dict[str, Any]:
    """Compara dos tar: orden, cabeceras (512 B crudos) y contenido; solo `authorized` puede diferir."""
    names_p = [m["name"] for m in tpkg["members"]]
    names_r = [m["name"] for m in tref["members"]]
    c.add(f"{p}.tar.same_members_and_order", names_p == names_r,
          f"{len(names_p)} / {len(names_r)} entradas; añadidas {sorted(set(names_p) - set(names_r))[:5]}, "
          f"eliminadas {sorted(set(names_r) - set(names_p))[:5]}")
    ranges = diff_ranges(pkg, ref) if len(pkg) == len(ref) else [[0, max(len(pkg), len(ref))]]
    where: dict[str, list[list[int]]] = {}
    unauthorized: list[str] = []
    for start, end in ranges:
        m = next((x for x in reversed(tpkg["members"]) if x["header_offset"] <= start), None)
        if m is None or start < m["data_offset"] or end > m["data_offset"] + m["size"]:
            unauthorized.append(f"[{start},{end}) fuera del contenido de un miembro")
            continue
        where.setdefault(m["name"], []).append([start - m["data_offset"], end - m["data_offset"]])
        if m["name"] not in authorized:
            unauthorized.append(m["name"])
    c.add(f"{p}.tar.same_size", len(pkg) == len(ref), f"{len(pkg)} / {len(ref)} B")
    c.add(f"{p}.tar.only_authorized_differ", not unauthorized and set(where) <= authorized,
          {"changed": sorted(where), "unauthorized": unauthorized[:10]})
    return {"changed_members": where, "raw_ranges": ranges[:50]}


# ------------------------------------------------------------------------------------------- darwin.sum
def parse_sum(data: bytes) -> dict[str, Any]:
    text = data.decode("ascii", errors="replace")
    fields = text.rstrip("\n").split(",")
    return {"fields": fields, "lf_only": data.endswith(b"\n") and b"\r" not in data and data.count(b"\n") == 1,
            "ascii": all(b < 0x80 for b in data)}


def check_sum(c: Checks, p: str, data: bytes, core: bytes, official: bytes, mode: int) -> None:
    s, o = parse_sum(data), parse_sum(official)
    f = s["fields"]
    c.add(f"{p}.sum.format", s["ascii"] and s["lf_only"] and len(f) == len(o["fields"]) == 12 and f[-1] == "",
          f"{len(f)} campos, ASCII, una línea LF, coma final")
    c.add(f"{p}.sum.crc", len(f) > 1 and f[1] == f"{zlib.crc32(core):08x}", f"campo CRC {f[1] if len(f) > 1 else None} / real {zlib.crc32(core):08x}")
    c.add(f"{p}.sum.size", len(f) > 2 and f[2] == f"{len(core):08x}", f"campo tamaño {f[2] if len(f) > 2 else None} / real {len(core):08x}")
    c.add(f"{p}.sum.mode_matches_tar", len(f) > 3 and f[3] == f"{mode & 0o7777:08x}", f"permisos {f[3] if len(f) > 3 else None} / tar {mode & 0o7777:o}")
    c.add(f"{p}.sum.other_fields_official", [x for i, x in enumerate(f) if i not in (1, 2)] == [x for i, x in enumerate(o["fields"]) if i not in (1, 2)],
          "resto de campos idénticos al darwin.sum oficial")


def verify_all_sums(buf: Any, tar: dict[str, Any]) -> dict[str, Any]:
    """Reproduce `uc_crc32sum -c` sobre cada `NNNN_<clave>_sum/<clave>.sum` del tar.

    Tipo 0 (fichero): existencia, tamaño, CRC-32 y permisos; tipo 5 (directorio): existencia y permisos.
    """
    by_name = {m["name"].rstrip("/"): m for m in tar["members"]}
    dirs = {n.split("/")[0] for n in by_name}
    out: dict[str, Any] = {}
    for m in tar["members"]:
        if not m["name"].endswith(".sum"):
            continue
        key = m["name"].split("/")[-1][:-4]
        target = next((d for d in dirs if d.split("_", 1)[-1] == key), None)
        errors: list[str] = []
        lines = bytes(memoryview(buf)[m["data_offset"]:m["data_offset"] + m["size"]]).decode("ascii").splitlines()
        for line in lines:
            f = line.split(",")
            entry = by_name.get(f"{target}/{f[10]}")
            if entry is None:
                errors.append(f"{f[10]}: no está en el tar")
            elif entry["mode"] & 0o7777 != int(f[3], 16):
                errors.append(f"{f[10]}: permisos {entry['mode']:o} != {f[3]}")
            elif f[0] == "0":
                data = memoryview(buf)[entry["data_offset"]:entry["data_offset"] + entry["size"]]
                if entry["size"] != int(f[2], 16) or zlib.crc32(data) != int(f[1], 16):
                    errors.append(f"{f[10]}: tamaño/CRC no coinciden")
        out[m["name"]] = {"target": target, "entries": len(lines), "errors": errors}
    return out


# ------------------------------------------------------------------------------------------- Darwin (emulación)
def _thumb_bl_targets(core: bytes) -> list[tuple[int, int, str]]:
    """Decodifica BL/B.W (T1/T4) en cada media palabra; devuelve (sitio, destino, tipo)."""
    out = []
    for off in range(0, len(core) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", core, off)
        if h1 & 0xF800 != 0xF000 or h2 & 0xD000 not in (0xD000, 0x9000):
            continue
        s = (h1 >> 10) & 1
        j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        addr = BASE + off
        out.append((addr, addr + 4 + imm, "bl" if h2 & 0x5000 == 0x5000 else "b.w"))
    return out


class Emu:
    """Ejecuta una función de Darwin con Unicorn; las llamadas fuera de `allowed` se sustituyen por stubs."""

    STOP = 0x3FF00

    def __init__(self, core: bytes, allowed: list[tuple[int, int]], stub: Callable[[int, dict[str, int]], int]):
        from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
        from unicorn import arm_const as a

        self.a = a
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.mu.mem_map(0, 0x40000)
        self.mu.mem_write(BASE, core)
        self.mu.mem_map(0x20000000, 0x10000)
        self.mu.mem_map(0x40000000, 0x100000)
        self.allowed = allowed
        self.stub = stub
        self.calls: list[tuple[int, dict[str, int]]] = []
        self.mu.hook_add(UC_HOOK_CODE, self._hook)

    def _hook(self, mu: Any, address: int, size: int, user: Any) -> None:
        if address == self.STOP or any(lo <= address < hi for lo, hi in self.allowed):
            return
        a = self.a
        regs = {r: mu.reg_read(getattr(a, f"UC_ARM_REG_{r.upper()}")) for r in ("r0", "r1", "r2", "r3")}
        self.calls.append((address, regs))
        mu.reg_write(a.UC_ARM_REG_R0, self.stub(address, regs) & 0xFFFFFFFF)
        mu.reg_write(a.UC_ARM_REG_PC, mu.reg_read(a.UC_ARM_REG_LR))

    def run(self, entry: int, args: tuple[int, ...] = ()) -> dict[str, int]:
        a = self.a
        sentinels = {"r4": 0x44444444, "r5": 0x55555555, "r6": 0x66666666, "r7": 0x77777777}
        for r, v in sentinels.items():
            self.mu.reg_write(getattr(a, f"UC_ARM_REG_{r.upper()}"), v)
        for i, v in enumerate(args):
            self.mu.reg_write(getattr(a, f"UC_ARM_REG_R{i}"), v)
        sp = 0x2000F000
        self.mu.reg_write(a.UC_ARM_REG_SP, sp)
        self.mu.reg_write(a.UC_ARM_REG_LR, self.STOP | 1)
        self.mu.emu_start(entry | 1, self.STOP, count=200_000)
        out = {r: self.mu.reg_read(getattr(a, f"UC_ARM_REG_{r.upper()}")) for r in ("r0", "sp", "pc", *sentinels)}
        out["callee_saved_ok"] = int(all(out[r] == v for r, v in sentinels.items()) and out["sp"] == sp)
        return out


def _const_stub(addr_value: int, value: int) -> Callable[[int, dict[str, int]], int]:
    return lambda addr, regs: value if addr == addr_value else 0


def gate_results(core: bytes) -> dict[str, Any]:
    """`0x1fe66` con cada valor posible de `0x1b080` (0..255 y valores de 32 bits)."""
    values = list(range(256)) + [0x100, 0x1234, 0xFFFFFFFF]
    ret: dict[int, int] = {}
    reads = 0
    stack_ok = True
    for v in values:
        e = Emu(core, [(0x1FE66, 0x1FE86)], _const_stub(0x1B080, v))
        out = e.run(0x1FE66)
        ret[v] = out["r0"]
        reads += sum(1 for addr, _ in e.calls if addr == 0x1B080)
        stack_ok &= bool(out["callee_saved_ok"])
        if any(addr != 0x1B080 for addr, _ in e.calls):
            stack_ok = False
    return {"returns": ret, "reads_0x1b080": reads, "callee_saved_ok": stack_ok}


def writer_calls(core: bytes, type_value: int) -> dict[str, list[int]]:
    """Escritores P4D/P4E: ¿llaman a `0x51c0` cuando el tipo leído por `0x1b080` es `type_value`?"""
    out: dict[str, list[int]] = {}
    for w, end in ((0x20C90, 0x20CB2), (0x20CB2, 0x20CD4), (0x20CD4, 0x20CEE), (0x20D00, 0x20D26)):
        e = Emu(core, [(w, end), (0x20C74, 0x20C90)], lambda addr, regs: type_value if addr == 0x1B080 else 0)
        e.run(w, (0, 0, 0, 0))
        out[hex(w)] = [regs["r0"] for addr, regs in e.calls if addr == 0x51C0]
    return out


def cam_check_error6(core: bytes, gate_byte: int) -> bool:
    """`0x1f4ce` (comprobación de leva): ¿emite el error 6 (`0x16558`) con la leva fuera de posición?"""
    def stub(addr: int, regs: dict[str, int]) -> int:
        return {0x1B080: gate_byte, 0x165C0: 0, 0x1FD8C: 0}.get(addr, 0)
    e = Emu(core, [(0x1F4CE, 0x1F51E), (0x1FE66, 0x1FE86)], stub)
    e.run(0x1F4CE, (1, 1, 1))
    return any(addr == 0x16558 and regs["r0"] == 6 for addr, regs in e.calls)


def op5_trace(core: bytes) -> list[list[int]]:
    """Operación 5 (`0x1fcb8`): secuencia de escrituras `0x51cc(puerto, valor, máscara)`."""
    tick = [0]

    def stub(addr: int, regs: dict[str, int]) -> int:
        if addr == 0x93E6:
            tick[0] += 0x100000
            return tick[0]
        return 0
    e = Emu(core, [(0x1FCB8, 0x1FCD8), (0x1FE32, 0x1FE66), (0x1FEB6, 0x1FECC)], stub)
    e.run(0x1FCB8)
    return [[regs["r0"], regs["r1"], regs["r2"]] for addr, regs in e.calls if addr == 0x51CC]


def starter_lists(core: bytes) -> dict[str, list[int]]:
    """Lista de estados que cada arrancador elige con compuerta 0 (rama `cbz r0`)."""
    import capstone

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    out: dict[str, list[int]] = {}
    for start in (0x1FEE2, 0x1FF72, 0x1FFCE):
        ins = list(md.disasm(core[start - BASE:start - BASE + 0x50], start))
        gate = next(i for i in ins if i.mnemonic == "bl" and i.op_str == "#0x1f5a2")
        cbz = next(i for i in ins if i.address > gate.address and i.mnemonic == "cbz" and i.op_str.startswith("r0"))
        between = [i for i in ins if gate.address < i.address < cbz.address]
        r0_clobbered = any("r0" in i.op_str.split(",")[0] for i in between)
        target = int(cbz.op_str.split("#")[1], 16)
        branch = [i for i in ins if i.address >= target][:3]
        ldr, sub = branch[0], branch[2]
        imm = int(ldr.op_str.split("#")[1].rstrip("]"), 16)
        lit = struct.unpack_from("<I", core, ((ldr.address + 4) & ~3) + imm - BASE)[0]
        ptr = lit - int(sub.op_str.split("#")[1], 16)
        states: list[int] = []
        while len(states) < 16:
            states.append(core[ptr - BASE + len(states)])
            if states[-1] == 10:
                break
        out[hex(start)] = states if not r0_clobbered else []
        out[f"{start:#x}.ptr"] = [ptr]
    return out


def audit_darwin(c: Checks, b1a: bytes, tipo0: bytes, orig: bytes) -> dict[str, Any]:
    """Diferencias y semántica de B1a frente al tipo 0 y al original (control diferencial)."""
    d_t0 = [[i, tipo0[i], b1a[i]] for i in range(min(len(b1a), len(tipo0))) if tipo0[i] != b1a[i]]
    d_or = [[i, orig[i], b1a[i]] for i in range(min(len(b1a), len(orig))) if orig[i] != b1a[i]]
    c.add("darwin.size", len(b1a) == len(tipo0) == len(orig) == 157_276, f"{len(b1a)} B")
    c.add("darwin.b1a_vs_tipo0_exactly_two", d_t0 == [[0x1BC6A, 0x28, 0x0A], [0x1BC6B, 0x46, 0xE0]],
          [[hex(i + BASE), f"{x:02x}", f"{y:02x}"] for i, x, y in d_t0][:10])
    tipo0_off = 0x20C78 - BASE
    c.add("darwin.tipo0_preserved", b1a[tipo0_off:tipo0_off + 8] == bytes.fromhex("09e000bf00bf00bf"),
          b1a[tipo0_off:tipo0_off + 8].hex())
    c.add("darwin.b1a_vs_original_is_tipo0_plus_b1a",
          {i for i, _, _ in d_or} <= set(range(tipo0_off, tipo0_off + 8)) | {0x1BC6A, 0x1BC6B}
          and {0x1BC6A, 0x1BC6B} <= {i for i, _, _ in d_or},
          [[hex(i + BASE), f"{x:02x}", f"{y:02x}"] for i, x, y in d_or])
    h1, = struct.unpack_from("<H", b1a, 0x1BC6A)
    imm11 = h1 & 0x7FF
    target = 0x1FE6A + 4 + ((imm11 - 0x800 if imm11 & 0x400 else imm11) << 1)
    c.add("darwin.branch_target", h1 & 0xF800 == 0xE000 and target == 0x1FE82, f"B.N {h1:#06x} -> {target:#x}")
    c.add("darwin.epilogue_intact", b1a[0x1FE82 - BASE:0x1FE86 - BASE] == bytes.fromhex("2846" "70bd")
          and b1a[0x1FE66 - BASE:0x1FE6A - BASE] == bytes.fromhex("70b5" "0025"), "push {r4-r6,lr}; movs r5,#0 … mov r0,r5; pop {r4-r6,pc}")
    c.add("darwin.ver_string", b"VER0.78" in b1a, "cadena VER0.78 conservada (ud_darwin_firmup)")
    c.add("darwin.vectors_intact", b1a[:8] == orig[:8], f"SP/reset {b1a[:8].hex()}")

    g_b1a, g_t0 = gate_results(b1a), gate_results(tipo0)
    expected_t0 = {v: ((v >> 4) if 1 <= (v >> 4) <= 5 else 0) for v in g_t0["returns"]}
    c.add("darwin.emu.tipo0_gate_control", g_t0["returns"] == expected_t0 and g_t0["reads_0x1b080"] == len(expected_t0),
          "control positivo: el tipo 0 devuelve el nibble alto 1..5 de 0x1b080 y 0 en el resto")
    c.add("darwin.emu.b1a_returns_zero", set(g_b1a["returns"].values()) == {0}, f"{len(g_b1a['returns'])} entradas: retorno siempre 0")
    c.add("darwin.emu.b1a_no_0x1b080", g_b1a["reads_0x1b080"] == 0, f"{g_b1a['reads_0x1b080']} llamadas a 0x1b080")
    c.add("darwin.emu.b1a_stack_and_return", g_b1a["callee_saved_ok"], "r4–r7 y SP preservados; retorna a LR")

    lists = starter_lists(b1a)
    c.add("darwin.starters_select_L0", all(lists[hex(s)] == [0, 7, 8, 9, 10] for s in (0x1FEE2, 0x1FF72, 0x1FFCE)),
          {k: v for k, v in lists.items()})

    sites = _thumb_bl_targets(b1a)
    gate_sites = sorted(hex(a) for a, t, _ in sites if t == 0x1FE66)
    thunk_sites = sorted(hex(a) for a, t, _ in sites if t == 0x1F5A2)
    pointer_refs = [hex(BASE + o) for o in range(0, len(b1a) - 3, 4)
                    if struct.unpack_from("<I", b1a, o)[0] in (0x1FE66, 0x1FE67, 0x1F5A2, 0x1F5A3)]
    expected_direct = sorted(hex(a) for a in (0x1F4BA, 0x1F4DE, 0x1F576, 0x1F5A2, 0x1F5A8, 0x1F896, 0x1F908, 0x1FA40,
                                              0x1FE88, 0x1FE90, 0x1FE98, 0x201BC))
    c.add("darwin.gate_consumers", gate_sites == expected_direct and not pointer_refs,
          {"directos": gate_sites, "via_thunk_0x1f5a2": thunk_sites, "punteros_literales": pointer_refs})

    w_b1a = {t: writer_calls(b1a, t) for t in range(8)}
    w_orig = {t: writer_calls(orig, t) for t in range(8)}
    c.add("darwin.emu.p4d_p4e_control", any(v for t in w_orig.values() for v in t.values()),
          "control positivo: el original sí escribe 0x51c0 con tipo 1/2/3")
    c.add("darwin.emu.p4d_p4e_filtered", not any(v for t in w_b1a.values() for v in t.values()),
          "B1a: ningún escritor de P4D/P4E llega a 0x51c0 para ningún tipo 0..7")

    cam = {"original_nibble4": cam_check_error6(orig, 0x40), "tipo0_nibble4": cam_check_error6(tipo0, 0x40),
           "b1a_nibble4": cam_check_error6(b1a, 0x40)}
    c.add("darwin.emu.cam_check_suppressed", cam["tipo0_nibble4"] and not cam["b1a_nibble4"],
          f"0x1f4ce con leva fuera de posición: tipo 0 error 6 = {cam['tipo0_nibble4']}, B1a = {cam['b1a_nibble4']}")
    op5 = {"tipo0": op5_trace(tipo0), "b1a": op5_trace(b1a)}
    c.add("darwin.emu.op5_unchanged", op5["tipo0"] == op5["b1a"] and [4, 3, 0xFFFC] in op5["b1a"],
          {k: [[hex(x) for x in w] for w in v] for k, v in op5.items()})

    regions = {"reset": (0x45C8, 0x4638), "scatter": (0x43FC, 0x4404), "mailbox": (0x45BC, 0x45C8),
               "initcom": (0x4BCA, 0x5000), "gpio_51c0": (0x51C0, 0x51E0), "upd_main": (0x8DA8, 0x8E00),
               "off": (0x8900, 0x8C90), "crc_a1dc": (0xA1DC, 0xA200), "watchdog": (0xA4AC, 0xA540),
               "com_task": (0xECE4, 0xED40), "power_handlers": (0x1578C, 0x157E0), "power_table": (0x28C6C, 0x28D00)}
    changed = [n for n, (lo, hi) in regions.items() if b1a[lo - BASE:hi - BASE] != orig[lo - BASE:hi - BASE]]
    c.add("darwin.critical_regions_untouched", not changed, changed or list(regions))
    return {"diff_vs_tipo0": d_t0, "diff_vs_original": d_or, "gate_b1a": {hex(k): v for k, v in list(g_b1a["returns"].items())[::32]},
            "starters": lists, "gate_sites": gate_sites, "thunk_sites": thunk_sites, "cam_check": cam, "op5": op5,
            "writers_original": {t: v for t, v in w_orig.items() if any(v.values())}}


# ------------------------------------------------------------------------------------------- paquete completo
@dataclass
class Package:
    checks: Checks
    header: dict[str, Any]
    container: dict[str, Any]
    decrypted: Decrypted
    tar_range: tuple[int, int]
    fs_range: tuple[int, int]


def audit_package(p: str, dat: Any, fdat: Any, expect: Expect, keys: tuple[bytes, bytes],
                  sony: dict[str, Any] | None, c: Checks | None = None) -> Package:
    """Integridad estructural de un par .dat/.fdat y coherencia entre ambos."""
    c = c or Checks()
    sd, sf = sha256_buf(dat), sha256_buf(fdat)
    c.add(f"{p}.dat.sha256", sd == expect.dat_sha, f"{sd} ({len(dat)} B)")
    c.add(f"{p}.fdat.sha256", sf == expect.fdat_sha, f"{sf} ({len(fdat)} B)")
    c.add(f"{p}.sizes", len(dat) == DAT_SIZE and len(fdat) == FDAT_SIZE, f"{len(dat)} / {len(fdat)} B")
    info = parse_dat(dat)
    check_dat(c, p, info, sony)
    dec = Decrypted()
    if "fdat_offset" in info:
        dec = decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], keys, compare=fdat)
        check_blocks(c, p, dec)
        c.add(f"{p}.dat_matches_fdat", dec.first_mismatch_vs_fdat is None and dec.plain_size == len(fdat),
              f"FDAT descifrado {dec.plain_size} B; primera diferencia {dec.first_mismatch_vs_fdat}")
    hd = check_fdat_header(c, p, bytes(fdat[:FDAT_HDR]), len(fdat), expect.minor)
    user = hd["filesystems"][0]
    return Package(c, hd, info, dec, (hd["firmware_offset"], hd["firmware_size"]), (user["offset"], user["size"]))


def slice_of(buf: Any, rng: tuple[int, int]) -> memoryview:
    return memoryview(buf)[rng[0]:rng[0] + rng[1]]


def manifest_vs_real(manifest: dict[str, Any], package_dir: Path) -> list[dict[str, Any]]:
    """El manifiesto de E25-05 declara SHA-256 y PASS: se recalculan sobre los ficheros reales."""
    rows = []
    for key in ("dat", "fdat", "config"):
        decl = manifest["outputs"][key]
        path = package_dir / Path(decl["path"]).name
        real = sha256_buf(open_ro(path)) if path.exists() and path.stat().st_size else (
            hashlib.sha256(b"").hexdigest() if path.exists() else None)
        rows.append({"file": path.name, "declared": decl["sha256"], "real": real, "match": real == decl["sha256"]})
    return rows


def files_present(paths: list[Path]) -> dict[str, bool]:
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): p.exists() for p in paths}


# ------------------------------------------------------------------------------------------- auditoría completa
def run() -> dict[str, Any]:
    c = Checks()
    report: dict[str, Any] = {"schema": "a6000.e25_06.audit.v1", "generated_by": "scripts/e25_06/audit_packages.py",
                              "audited_commit": "67fd3a40bcf1786398e23236d9f14d1ea7f8cd3c"}
    needed = [EXP_DIR / "firmware_packed.dat", EXP_DIR / "firmware_packed.fdat", REC_DIR / "firmware_packed.dat",
              REC_DIR / "firmware_packed.fdat", REC323_DIR / "firmware_packed.dat", REC323_DIR / "firmware_packed.fdat",
              SONY_DAT, SONY_FDAT, OFFICIAL_TAR, OFFICIAL_UPDATER, OFFICIAL_CORE, OFFICIAL_SUM, TIPO0_CORE, TIPO0_SUM,
              TIPO0_TAR, B1A_CORE, FDAT_ROOT / "firmware_packed.dat", FDAT_ROOT / "firmware_packed.fdat"]
    present = files_present(needed)
    report["files_present"] = present
    for name, ok in present.items():
        if not ok:
            c.missing(f"input.{name}", "falta el fichero: la comprobación que depende de él no se aprueba")
    if not all(present.values()):
        report["checks"] = c.items
        return report

    keys = load_keys()
    # 0. Control positivo del descifrador: el .dat original de Sony debe dar el firmware.fdat de Sony.
    sony_dat, sony_fdat = open_ro(SONY_DAT), open_ro(SONY_FDAT)
    sony = parse_dat(sony_dat)
    sdec = decrypt_fdat(sony_dat, sony["fdat_offset"], sony["fdat_size"], keys, compare=sony_fdat)
    c.add("control.sony_dat_dend", sony.get("dend_stored") == sony.get("dend_computed"), sony.get("dend_stored"))
    c.add("control.sony_decrypt", not sdec.bad_sum and not sdec.bad_flag and sdec.first_mismatch_vs_fdat is None,
          f"el descifrador propio reproduce el firmware.fdat de Sony ({sdec.blocks} bloques)")
    sony_hdr = parse_fdat_header(bytes(sony_fdat[:FDAT_HDR]))
    report["sony"] = {"chunks": sony["chunks"], "udid": sony["udid"], "header": sony_hdr}

    # 1. Previos intactos.
    prev = {}
    for label, (path, sha, origin) in PREVIOUS.items():
        real = sha256_buf(open_ro(path))
        prev[label] = {"sha256": real, "expected": sha, "recorded_in": origin}
        c.add(f"previous.{label}", real == sha, f"{real[:16]}… registrado en {origin}")
    report["previous"] = prev

    official_tar, updater = open_ro(OFFICIAL_TAR), open_ro(OFFICIAL_UPDATER)
    t_official = parse_tar(official_tar)
    check_tar_structure(c, "official", t_official, len(official_tar))
    b1a, tipo0, orig = B1A_CORE.read_bytes(), TIPO0_CORE.read_bytes(), OFFICIAL_CORE.read_bytes()

    # 2. Paquetes.
    pk: dict[str, Package] = {}
    for p, d, expect in (("exp", EXP_DIR, EXPECT_EXP), ("rec", REC_DIR, EXPECT_REC)):
        dat, fdat = open_ro(d / "firmware_packed.dat"), open_ro(d / "firmware_packed.fdat")
        pkg = audit_package(p, dat, fdat, expect, keys, sony, c)
        pk[p] = pkg
        c.add(f"{p}.fdat.updater_size", pkg.fs_range[1] == len(updater), f"{pkg.fs_range[1]} B")
        tar, fs = slice_of(fdat, pkg.tar_range), slice_of(fdat, pkg.fs_range)
        c.add(f"{p}.updater_official", sha256_buf(fs) == UPDATER_SHA and bytes(fs) == bytes(updater), sha256_buf(fs))
        c.add(f"{p}.tar.sha256", sha256_buf(tar) == expect.tar_sha, sha256_buf(tar))
        t_pkg = parse_tar(tar)
        check_tar_structure(c, p, t_pkg, len(tar))
        authorized = {DARWIN_CORE, DARWIN_SUM} if p == "exp" else set()
        cmp = compare_tars(c, f"{p}.vs_official", tar, official_tar, t_pkg, t_official, authorized)
        core = member_bytes(tar, t_pkg, DARWIN_CORE)
        sum_ = member_bytes(tar, t_pkg, DARWIN_SUM)
        m_core = next(m for m in t_pkg["members"] if m["name"] == DARWIN_CORE)
        c.add(f"{p}.core.sha256", hashlib.sha256(core).hexdigest() == expect.core_sha, hashlib.sha256(core).hexdigest())
        c.add(f"{p}.core.crc32", f"{zlib.crc32(core):08x}" == expect.core_crc, f"{zlib.crc32(core):08x}")
        c.add(f"{p}.core.tar_meta", (m_core["mode"], m_core["uname"], m_core["gname"], m_core["type"]) == (0o644, "root", "root", "0"),
              f"modo {m_core['mode']:o}, {m_core['uname']}/{m_core['gname']}, tipo {m_core['type']!r}")
        check_sum(c, p, sum_, core, OFFICIAL_SUM.read_bytes(), m_core["mode"])
        sums = verify_all_sums(tar, t_pkg)
        c.add(f"{p}.all_sums_uc_crc32sum", len(sums) == 7 and not any(v["errors"] for v in sums.values()),
              {k: f"{v['target']}: {v['entries']} entradas, errores {v['errors'][:3]}" for k, v in sums.items()})
        c.add(f"{p}.no_darwin_boo", not [m for m in t_pkg["members"] if "darwin_boo" in m["name"]], "sin darwin_boo.bin")
        report[p] = {"header": pkg.header, "dat": {k: v for k, v in pkg.container.items() if k != "udid_raw"},
                     "decrypted_sha256": pkg.decrypted.sha256, "tar_vs_official": cmp,
                     "darwin_sum": sum_.decode("ascii", errors="replace"), "tar_members": len(t_pkg["members"])}
        if p == "exp":
            c.add("exp.core_equals_b1a_file", core == b1a, "core integrado = analysis/e25/darwin_core_tipo0_sin_rearme.bin")
            c.add("exp.sum_exact_line", sum_ == EXP_SUM_LINE, sum_.decode("ascii", errors="replace"))
            changed = cmp["changed_members"]
            sum_ranges = diff_ranges(EXP_SUM_LINE, OFFICIAL_SUM.read_bytes())
            c.add("exp.tar_diff_bytes", changed.get(DARWIN_CORE) == [[0x1BC6A, 0x1BC6C], [0x1CA78, 0x1CA7C], [0x1CA7D, 0x1CA80]]
                  and changed.get(DARWIN_SUM) == sum_ranges and all(2 <= s and e <= 10 for s, e in sum_ranges),
                  {k: v for k, v in changed.items()})
            # Frente al 3.22 instalado (aceptado en T024): solo la compuerta B1a y el CRC del sum.
            tipo0_tar = open_ro(TIPO0_TAR)
            t_t0 = parse_tar(tipo0_tar)
            cmp322 = compare_tars(c, "exp.vs_322", tar, tipo0_tar, t_pkg, t_t0, {DARWIN_CORE, DARWIN_SUM})
            report["exp"]["tar_vs_322"] = cmp322
            c.add("exp.vs_322.exact", cmp322["changed_members"].get(DARWIN_CORE) == [[0x1BC6A, 0x1BC6C]]
                  and all(2 <= s and e <= 10 for s, e in cmp322["changed_members"].get(DARWIN_SUM, [[0, 99]])),
                  {k: v for k, v in cmp322["changed_members"].items()})
        else:
            c.add("rec.tar_bytes_equal_official", bytes(tar) == bytes(official_tar), "firmware.tar idéntico byte a byte al oficial")
            c.add("rec.sum_equals_official", sum_ == OFFICIAL_SUM.read_bytes(), sum_.decode("ascii", errors="replace"))

    # 3. Darwin.
    report["darwin"] = audit_darwin(c, b1a, tipo0, orig)
    c.add("darwin.tipo0_sum_format_t024", parse_sum(TIPO0_SUM.read_bytes())["fields"][3:] == parse_sum(EXP_SUM_LINE)["fields"][3:],
          "el darwin.sum del 3.23 tiene el mismo formato que el del 3.22 aceptado en T024")

    # 4. Cabeceras: 3.23/3.24 frente al 3.22 instalado (T024) y al FDAT de Sony.
    fdat322 = open_ro(FDAT_ROOT / "firmware_packed.fdat")
    h322 = bytes(fdat322[:FDAT_HDR])
    hd322 = parse_fdat_header(h322)
    c.add("previous.tipo0_tar_equals_322_payload",
          sha256_buf(slice_of(fdat322, (hd322["firmware_offset"], hd322["firmware_size"]))) == sha256_buf(open_ro(TIPO0_TAR)),
          "firmware_tipo0.tar = tar contenido en el .fdat 3.22 instalado (cuyo SHA está registrado en git)")
    for p, d in (("exp", EXP_DIR), ("rec", REC_DIR)):
        h = bytes(open_ro(d / "firmware_packed.fdat")[:FDAT_HDR])
        r = diff_ranges(h, h322)
        c.add(f"{p}.header_vs_322", [32, 33] in r and all((8 <= s and e <= 12) or [s, e] == [32, 33] for s, e in r),
              f"rangos distintos frente a la cabecera del 3.22 instalado: {r}")
        report[p]["header_vs_sony"] = diff_ranges(h, bytes(sony_fdat[:FDAT_HDR]))
    dat322 = open_ro(FDAT_ROOT / "firmware_packed.dat")
    i322 = parse_dat(dat322)
    for p in ("exp", "rec"):
        c.add(f"{p}.dat_layout_vs_322", [x[:3] for x in pk[p].container["chunks"]] == [x[:3] for x in i322["chunks"]]
              and pk[p].container["udid_raw"] == i322["udid_raw"], "chunks, offsets y descriptores idénticos al 3.22 instalado")

    # 5. Recuperación 3.24 frente a la 3.23 antigua.
    rec_fdat, old_fdat = open_ro(REC_DIR / "firmware_packed.fdat"), open_ro(REC323_DIR / "firmware_packed.fdat")
    rec_dat, old_dat = open_ro(REC_DIR / "firmware_packed.dat"), open_ro(REC323_DIR / "firmware_packed.dat")
    rf, rd = diff_ranges(rec_fdat, old_fdat), diff_ranges(rec_dat, old_dat)
    off = pk["rec"].container["fdat_offset"]
    # Predicción: byte p del FDAT plano va al offset p+4 del primer bloque; la suma (0..1) también cambia.
    aes = sorted({(4 + b) // 16 for s, e in rf for b in range(s, e)} | {0})
    predicted: list[list[int]] = []
    for k in aes:
        lo, hi = off + 16 * k, off + 16 * k + 16
        if predicted and predicted[-1][1] == lo:
            predicted[-1][1] = hi
        else:
            predicted.append([lo, hi])
    predicted.append([len(rec_dat) - 4, len(rec_dat)])
    c.add("rec_vs_323.fdat_ranges", rf == [[8, 12], [32, 33]], rf)
    c.add("rec_vs_323.fdat_bytes", bytes(rec_fdat[32:33]) == b"\x24" and bytes(old_fdat[32:33]) == b"\x23"
          and parse_fdat_header(bytes(old_fdat[:FDAT_HDR]))["checksum_stored"] == parse_fdat_header(bytes(old_fdat[:FDAT_HDR]))["checksum_computed"],
          "versionMinor 0x23 -> 0x24; [8,12) es el CRC-32 recalculado de la cabecera")
    # Cada rango real debe estar contenido en el predicho (un byte AES puede coincidir por azar).
    within = all(any(p_[0] <= s and e <= p_[1] for p_ in predicted) for s, e in rd)
    c.add("rec_vs_323.dat_ranges", rd == [[140, 156], [172, 188], [DAT_SIZE - 4, DAT_SIZE]] and within,
          {"real": rd, "predicho": predicted})
    report["rec_vs_323"] = {"fdat_ranges": rf, "dat_ranges": rd, "predicted_dat_ranges": predicted}

    # 6. Confusión de artefactos (R7).
    cfg_exp, cfg_old = (EXP_DIR / "config-323.yaml").read_bytes(), (REC323_DIR / "config-323.yaml").read_bytes()
    report["r7"] = {
        "config_323_identical_in_both_dirs": cfg_exp == cfg_old,
        "same_filename_in_dirs": sorted(str(p.relative_to(FDAT_ROOT)) for p in FDAT_ROOT.rglob("firmware_packed.dat")),
        "header_version_exp": pk["exp"].header["version"],
        "header_version_old_rec": parse_fdat_header(bytes(old_fdat[:FDAT_HDR]))["version"],
    }
    for name, d in (("exp", EXP_DIR), ("rec", REC_DIR)):
        sums = {ln.split()[1]: ln.split()[0] for ln in (d / "SHA256SUMS").read_text().splitlines() if ln.strip()}
        real_sums = {n: sha256_buf(open_ro(d / n)) for n in sums}
        c.add(f"{name}.SHA256SUMS", sums == real_sums, f"{len(sums)} entradas")

    # 7. Manifiestos de E25-05 frente a los ficheros reales.
    for name, d in (("manifest-experimental-323.json", EXP_DIR), ("manifest-recuperacion-324.json", REC_DIR)):
        rows = manifest_vs_real(json.loads((MANI / name).read_text()), d)
        c.add(f"manifest.{name}", all(r["match"] for r in rows), rows)

    report["checks"] = c.items
    report["summary"] = {"total": len(c.items), "failed": c.failed()}
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help=f"escribe {OUT.relative_to(ROOT)}")
    args = ap.parse_args(argv)
    report = run()
    text = json.dumps(report, indent=1, ensure_ascii=False, default=str) + "\n"
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
    failed = [x for x in report["checks"] if x["result"] != "PASS"]
    print(json.dumps({"total": len(report["checks"]), "failed": failed}, indent=1, ensure_ascii=False, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
