"""FAT16 de `nflasha3`: localización y parcheo en sitio de `av-cam.bin`.

`nflasha3` (TPZL) descomprime a una imagen FAT16 de 24 182 784 B.  El firmware
BIONZ (`av-cam.bin`, 11 427 236 B) ocupa la cadena de clústeres que empieza en el
clúster 3.  El parche conserva el tamaño y la cadena, así que basta con
sobrescribir los bytes en sus posiciones; no se toca el directorio, la FAT ni la
geometría.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass


class FatError(ValueError):
    """Imagen FAT inválida o archivo no encontrado."""


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


@dataclass(frozen=True)
class FatFile:
    """Archivo localizado en la imagen FAT (nombre 8.3 y cadena de clústeres)."""

    name: str
    size: int
    clusters: tuple[int, ...]

    @property
    def cluster_count(self) -> int:
        return len(self.clusters)


@dataclass(frozen=True)
class Fat16:
    """Imagen FAT12/FAT16 (la partición de `nflasha3` es FAT12 con 1472 clústeres)."""

    data: bytes
    bytes_per_sector: int
    sectors_per_cluster: int
    reserved_sectors: int
    num_fats: int
    root_entries: int
    fat_size: int
    root_offset: int
    data_offset: int

    @property
    def cluster_size(self) -> int:
        return self.bytes_per_sector * self.sectors_per_cluster

    @property
    def fat_type(self) -> int:
        clusters = (len(self.data) - self.data_offset) // self.cluster_size
        if clusters < 4085:
            return 12
        if clusters < 65525:
            return 16
        raise FatError("FAT32 no soportado")

    @classmethod
    def parse(cls, data: bytes) -> Fat16:
        if len(data) < 512:
            raise FatError("imagen menor que un sector")
        if data[510:512] != b"\x55\xaa":
            raise FatError("falta la firma 0x55aa")
        bps = _u16(data, 0x0B)
        spc = data[0x0D]
        reserved = _u16(data, 0x0E)
        num_fats = data[0x10]
        root_entries = _u16(data, 0x11)
        fat_size = _u16(data, 0x16) or _u32(data, 0x24)
        if bps not in (512, 1024, 2048, 4096) or spc == 0:
            raise FatError(f"geometría no soportada: bps={bps} spc={spc}")
        if not 1 <= num_fats <= 4 or not 1 <= root_entries <= 4096:
            raise FatError("número de FAT o entradas de raíz fuera de rango")
        if fat_size == 0:
            raise FatError("tamaño de FAT cero")
        root_offset = (reserved + num_fats * fat_size) * bps
        root_size = root_entries * 32
        data_offset = root_offset + root_size
        if data_offset >= len(data):
            raise FatError("región de datos fuera de la imagen")
        return cls(data, bps, spc, reserved, num_fats, root_entries, fat_size, root_offset, data_offset)

    def _fat_entry(self, cluster: int) -> int:
        if cluster < 0 or cluster >= (0xFF8 if self.fat_type == 12 else 0xFFF8):
            raise FatError(f"clúster fuera de rango: {cluster}")
        fat_start = self.reserved_sectors * self.bytes_per_sector
        if self.fat_type == 12:
            offset = fat_start + (cluster * 3) // 2
            if offset + 2 > len(self.data):
                raise FatError("entrada FAT fuera de la imagen")
            word = _u16(self.data, offset)
            return (word >> 4) if cluster & 1 else (word & 0x0FFF)
        offset = fat_start + cluster * 2
        if offset + 2 > len(self.data):
            raise FatError("entrada FAT fuera de la imagen")
        return _u16(self.data, offset)

    @property
    def _eoc(self) -> int:
        return 0xFF8 if self.fat_type == 12 else 0xFFF8

    def cluster_offset(self, cluster: int) -> int:
        if cluster < 2:
            raise FatError(f"clúster reservado: {cluster}")
        offset = self.data_offset + (cluster - 2) * self.cluster_size
        if offset + self.cluster_size > len(self.data):
            raise FatError(f"clúster {cluster} fuera de la imagen")
        return offset

    def _entries(self):
        for index in range(self.root_entries):
            offset = self.root_offset + index * 32
            entry = self.data[offset:offset + 32]
            if entry[0] == 0x00:
                return
            if entry[0] == 0xE5 or entry[11] & 0x08:
                continue
            yield entry

    @staticmethod
    def _decode_name(entry: bytes) -> str:
        base = entry[:8].decode("ascii", "replace").rstrip()
        ext = entry[8:11].decode("ascii", "replace").rstrip()
        return f"{base}.{ext}" if ext else base

    def find(self, name: str) -> FatFile:
        wanted = name.upper()
        for entry in self._entries():
            if self._decode_name(entry).upper() != wanted:
                continue
            first = _u16(entry, 26)
            size = _u32(entry, 28)
            clusters: list[int] = []
            cluster = first
            while 2 <= cluster < self._eoc:
                if cluster in clusters:
                    raise FatError(f"cadena de clústeres cíclica en {name}")
                clusters.append(cluster)
                cluster = self._fat_entry(cluster)
            needed = (size + self.cluster_size - 1) // self.cluster_size
            if len(clusters) < needed:
                raise FatError(f"cadena corta para {name}: {len(clusters)} < {needed}")
            return FatFile(wanted, size, tuple(clusters[:needed]))
        raise FatError(f"archivo no encontrado: {name}")

    def read(self, name: str) -> bytes:
        entry = self.find(name)
        out = bytearray()
        remaining = entry.size
        for cluster in entry.clusters:
            offset = self.cluster_offset(cluster)
            take = min(remaining, self.cluster_size)
            out += self.data[offset:offset + take]
            remaining -= take
            if remaining == 0:
                break
        if len(out) != entry.size:
            raise FatError(f"lectura incompleta de {name}")
        return bytes(out)

    def offsets_for(self, name: str) -> list[int]:
        """Desplazamientos absolutos de cada byte del archivo, en orden."""
        entry = self.find(name)
        out: list[int] = []
        remaining = entry.size
        for cluster in entry.clusters:
            base = self.cluster_offset(cluster)
            take = min(remaining, self.cluster_size)
            out.extend(range(base, base + take))
            remaining -= take
            if remaining == 0:
                break
        return out

    def patch(self, name: str, patched: bytes) -> tuple[bytes, dict]:
        """Sobrescribe un archivo con el mismo tamaño y devuelve la imagen nueva."""
        original = self.read(name)
        if len(patched) != len(original):
            raise FatError(f"{name}: {len(patched)} B != {len(original)} B")
        offsets = self.offsets_for(name)
        out = bytearray(self.data)
        changed = 0
        for offset, before, after in zip(offsets, original, patched):
            if before != after:
                out[offset] = after
                changed += 1
        result = bytes(out)
        check = Fat16.parse(result)
        if check.read(name) != patched:
            raise FatError(f"{name}: la imagen parcheada no reproduce el archivo")
        return result, {
            "name": name,
            "size": len(patched),
            "clusters": list(self.find(name).clusters),
            "first_cluster_offset": self.cluster_offset(self.find(name).clusters[0]),
            "changed_bytes": changed,
        }
