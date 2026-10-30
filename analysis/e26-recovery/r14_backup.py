"""E26-R14 — Offline BK4 (Backup) reader that mirrors Loader3's accessors.

Mirrors c01fa070 (item lookup), c01fa052 (size), c01fa02c (data), c01fa004 (capacity) and
c01f68bc (read by ID).  Works only on files; never touches the camera.
"""

import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC_OFF = 0xC  # c01fa0c4: strcmp(base+0xc, "BK4")


def u16(d: bytes, o: int) -> int:
    return struct.unpack_from("<H", d, o)[0]


def u32(d: bytes, o: int) -> int:
    return struct.unpack_from("<I", d, o)[0]


@dataclass(frozen=True)
class Item:
    group: int
    index: int
    raw_ptr: int
    size: int
    data_off: int


class BK4:
    def __init__(self, data: bytes):
        self.d = data
        if data[MAGIC_OFF : MAGIC_OFF + 3] != b"BK4":
            raise ValueError("no BK4 magic")
        self.ngroups = u32(
            data, 0x10
        )  # c01fa07c: ldr [base+0x10] bound check on id>>16
        self.groups = 0x100  # [r6+4] = base+0x100, 6-byte entries
        self.items = self.groups + self.ngroups * 6  # c01fa11a: [r6+8]

    @classmethod
    def load(cls, path: Path) -> "BK4":
        return cls(path.read_bytes())

    def lookup(self, bid: int) -> Item | None:
        """c01fa070: id = group<<16 | item; -1 pointer means 'absent'."""
        g, i = bid >> 16, bid & 0xFFFF
        if g >= self.ngroups:
            return None
        go = self.groups + g * 6
        if i >= u16(self.d, go):
            return None
        first = u32(self.d, go + 2)
        eo = self.items + (first + i) * 6
        ptr = u32(self.d, eo + 2)
        if ptr == 0xFFFFFFFF:
            return None
        top, off = ptr >> 24, ptr & 0xFFFFFF
        if top == 0:  # c01fa052/c01fa02c: size at off, capacity at off+2, data at off+4
            size, data = u16(self.d, off), off + 4
        elif top == 0xFF:  # size at off, data at off+2
            size, data = u16(self.d, off), off + 2
        else:  # inline size in the top byte, data at off
            size, data = top, off
        return Item(g, i, ptr, size, data)

    def read(self, bid: int) -> bytes | None:
        it = self.lookup(bid)
        return None if it is None else self.d[it.data_off : it.data_off + it.size]


ENT = 0x90  # c01f30cc: adds r4,#0x90; count = size/0x90 (c01f3026)


@dataclass(frozen=True)
class CfgEntry:
    n: int
    part: int
    dest: int
    end: int
    flags: int
    path: str


def ramcfg(bk: BK4) -> list[CfgEntry]:
    """RAMCFG = Backup 0xfa0080: 0x90-byte entries; the all-zero entry ends the walk (c01f303a)."""
    blob = bk.read(0xFA0080)
    if blob is None:
        return []
    out = []
    for n in range(len(blob) // ENT):
        e = blob[n * ENT : (n + 1) * ENT]
        w = struct.unpack_from("<4I", e)
        if not any(w):
            break
        out.append(
            CfgEntry(
                n, w[0], w[1], w[2], w[3], e[0x10:].split(b"\0")[0].decode("latin1")
            )
        )
    return out


def selected(entries: list[CfgEntry], mode: int) -> list[CfgEntry]:
    """Entries c01f2fe8 walks for ``mode`` (before the c01f2282 skip test, which needs Backup 0xfa007f+runtime state).

    c01f304c: (mode & 0xf00000) must equal (flags & 0xf00000); c01f3074: flags & (mode & 0xf000000) != 0.
    """
    return [
        e
        for e in entries
        if (mode & 0xF00000) == (e.flags & 0xF00000) and e.flags & (mode & 0xF000000)
    ]


# --- BOS (c01f2b7c / c01f2c98): 512 bytes at device offset 0, signature "8246", 16-byte rows at +0x10.
BOS_SIG = 0x36343238
BOS_ROW0, BOS_ROW = 0x10, 16


@dataclass(frozen=True)
class BosRow:
    n: int
    start: int
    size: int
    kind: int
    tail: int


def bos_parse(sector0: bytes) -> tuple[bool, list[BosRow]]:
    """(signature ok, rows).  Row n lives at 0x10 + 16*n (c01f2c34: base + n<<4 + 0x10)."""
    ok = u32(sector0, 0) == BOS_SIG
    rows = []
    for n in range((0x200 - BOS_ROW0) // BOS_ROW):
        a, b, k, t = struct.unpack_from("<4I", sector0, BOS_ROW0 + n * BOS_ROW)
        rows.append(BosRow(n, a, b, k, t))
    return ok, rows


# --- FAT geometry exactly as Loader3 checks it (c01f3e54 PBR, c01f3d8a FAT, c01f3f6a type)
def fat_checks(vol: bytes) -> dict[str, object]:
    """Mirror of PBR/FAT validation; returns each condition and the -302 verdict."""
    r: dict[str, object] = {}
    r["end_mark_aa55"] = u16(vol, 0x1FE) == 0xAA55
    r["bytes_per_sector"] = u16(vol, 0x0B)
    r["sector_size_ok"] = r["bytes_per_sector"] == 0x200
    spc = vol[0x0D]
    r["cluster_bytes"] = spc << 9
    r["cluster_ok"] = (spc << 9) == 0x4000
    fatsz = u16(vol, 0x16)
    r["sectors_per_fat16"] = fatsz
    r["not_fat32"] = fatsz != 0
    if fatsz:
        fat0 = vol[u16(vol, 0x0E) << 9]
        r["fat_id_vs_bpb"] = (fat0, vol[0x15])
        r["fat_id_ok"] = fat0 == vol[0x15]
        nroot, rsv, nfat = u16(vol, 0x11), u16(vol, 0x0E), vol[0x10]
        tot = u16(vol, 0x13) or u32(vol, 0x20)
        data_start = (
            rsv + nfat * fatsz + (nroot * 32 + (u16(vol, 0x0B) - 1)) // u16(vol, 0x0B)
        )
        clusters = (tot - data_start) // spc
        r["clusters"] = clusters
        r["fat_type"] = 12 if clusters < 0xFF5 else 16 if clusters < 0xFFF5 else None
    ok = all(
        r[k] for k in ("end_mark_aa55", "sector_size_ok", "cluster_ok", "not_fat32")
    )
    ok = ok and bool(r.get("fat_id_ok")) and r.get("fat_type") in (12, 16)
    r["loader3_accepts"] = ok
    return r


class FatVol:
    """Read-only FAT12/16 with 8.3 names and sub-directories (Loader3 matches 11 raw bytes, c01f4544)."""

    def __init__(self, vol: bytes):
        self.v = vol
        self.spc = vol[0x0D]
        self.rsv = u16(vol, 0x0E)
        self.nfat = vol[0x10]
        self.nroot = u16(vol, 0x11)
        self.fatsz = u16(vol, 0x16)
        self.root = (self.rsv + self.nfat * self.fatsz) * 512
        self.data = self.root + self.nroot * 32
        self.fat12 = fat_checks(vol).get("fat_type") == 12

    def _next(self, c: int) -> int:
        base = self.rsv * 512
        if self.fat12:
            w = u16(self.v, base + c * 3 // 2)
            return (w >> 4) if c & 1 else (w & 0xFFF)
        return u16(self.v, base + c * 2)

    def _chain(self, first: int) -> list[int]:
        out, c = [], first
        while 2 <= c < (0xFF8 if self.fat12 else 0xFFF8) and c not in out:
            out.append(c)
            c = self._next(c)
        return out

    def _dir(self, first: int | None) -> bytes:
        if first is None:
            return self.v[self.root : self.data]
        cs = self.spc * 512
        return b"".join(
            self.v[self.data + (c - 2) * cs : self.data + (c - 1) * cs]
            for c in self._chain(first)
        )

    @staticmethod
    def _sfn(part: str) -> bytes:
        b, _, e = part.upper().partition(".")
        return b.ljust(8)[:8].encode() + e.ljust(3)[:3].encode()

    def lookup(self, path: str) -> tuple[int, int, bool] | None:
        """(first cluster, size, chain_covers_size) for ``\\a\\b.ext`` or None when absent."""
        parts = [p for p in path.split("\\") if p]
        cur: int | None = None
        for i, p in enumerate(parts):
            d = self._dir(cur)
            hit = None
            for o in range(0, len(d), 32):
                e = d[o : o + 32]
                if e[0] == 0:
                    break
                if e[0] != 0xE5 and e[:11] == self._sfn(p) and not e[11] & 0x08:
                    hit = e
                    break
            if hit is None:
                return None
            first, size = u16(hit, 26), u32(hit, 28)
            if i == len(parts) - 1:
                need = -(-size // (self.spc * 512))
                return first, size, len(self._chain(first)) >= need
            cur = first
        return None

    def read(self, path: str) -> bytes | None:
        hit = self.lookup(path)
        if hit is None:
            return None
        first, size, _ = hit
        cs = self.spc * 512
        data = b"".join(
            self.v[self.data + (c - 2) * cs : self.data + (c - 1) * cs]
            for c in self._chain(first)
        )
        return data[:size]


@dataclass(frozen=True)
class Verdict:
    entry: CfgEntry
    code: int  # 0 = loader accepts; -302 = Loader3 returns -302 (c01f2f9a)
    reason: str


def entry_verdict(e: CfgEntry, vols: dict[int, "FatVol"]) -> Verdict:
    """What c01f2f24 does with one entry: size <= 0 (open miss, empty file) -> -302; oversize only warns (c01f2fa2)."""
    vol = vols.get(e.part)
    hit = vol.lookup(e.path) if vol else None
    if hit is None:
        return Verdict(e, -302, "apertura/dirent no encontrado (c01f4654 -> <=0)")
    if hit[1] == 0:
        return Verdict(e, -302, "archivo vacío (c01f2f8c: bgt falla)")
    if not hit[2]:
        return Verdict(
            e, -302, "cadena de clústeres más corta que el tamaño (c01f45cc)"
        )
    if hit[1] > e.end - e.dest + 1:
        return Verdict(e, 0, "aviso CFG_W:File size overflow (no aborta)")
    return Verdict(e, 0, "ok")
