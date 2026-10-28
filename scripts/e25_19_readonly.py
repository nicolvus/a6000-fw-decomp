#!/usr/bin/env python3
"""E25-19 — lector de solo lectura para la verificación física de la exposición larga.

Lee RAM normal de la cámara por el telnet root (OpenMemories Tweak) con
`dd if=/dev/mem ... | chroot /android /system/bin/hd /proc/self/fd/0` (la cámara no tiene
`base64`): nunca `of=`, nunca escritura en `/dev/mem`, nunca ficheros temporales en la cámara.

Antes de leer objetos comprueba los sitios de T050 y la GOT de T052-A; ante cualquier diferencia
o dato inconsistente (longitud, doble lectura de código) se detiene sin leer más.
Cada lectura guarda hora, latencia, SHA-256 y bytes crudos; los campos decodificados llevan el
instante de lectura para que el informe pueda decir cuándo es válido cada valor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import struct
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t052_b0_readonly import FIELDS, GOT_CHECKS, OBJECTS, T050, decode

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "analysis/e25-19"
HOST = "192.168.1.29"
RAM_VIRT_OFF = 0x40000000  # virtual = físico - 0x40000000

# Campos adicionales de E25-19 sobre los registros A/B (offsets del registro de foto).
EXTRA_RECORD = [
    (0x60, "<I", "vts_sel_60"),
    (0x64, "<I", "shd"),
    (0x68, "<H", "svd"),
    (0x6A, "<H", "spl"),
    (0x6C, "<B", "sint"),
    (0x6D, "<B", "shutmode"),
]
CAP_FIELDS = [  # offset en cap, formato, nombre (solo si cap está probado)
    (0x504, "<B", "cap504"), (0x64C, "<I", "shd"), (0x650, "<H", "svd"), (0x652, "<H", "spl"),
    (0x654, "<B", "sint"), (0x655, "<B", "shutmode"), (0x6BC, "<I", "setread"), (0x72C, "<I", "bulb_frames"),
    (0x73B, "<B", "derivado_73b"), (0x740, "<B", "secuenciador"), (0x4B84, "<I", "selector_lectura"),
    (0x4B9C, "<I", "contador_pasos"),
]


class ReadError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def parse_hd(text: str, size: int) -> bytes:
    """Extrae `size` bytes de la salida de `hd`: `00000000: 91 f8 ...  <ascii>`."""
    out = bytearray()
    for line in text.splitlines():
        m = re.match(r"^([0-9a-f]{8}): ((?:[0-9a-f]{2} ?)+)", line)
        if not m or int(m.group(1), 16) != len(out):
            continue
        toks = m.group(2).split()
        out += bytes(int(t, 16) for t in toks[: min(16, size - len(out))])
    if len(out) != size:
        raise ReadError(f"longitud {len(out)} != {size}")
    return bytes(out)


class Telnet:
    """Sesión telnet única y persistente; cada comando termina con un marcador."""

    def __init__(self, host: str = HOST, port: int = 23, timeout: float = 30.0):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(0.5)
        self.timeout = timeout
        self.n = 0
        self._drain()

    def _drain(self, until: bytes | None = None) -> bytes:
        buf, end = b"", time.time() + (self.timeout if until else 0.6)
        while time.time() < end:
            try:
                chunk = self.s.recv(65536)
            except TimeoutError:
                if until is None:
                    break
                continue
            if not chunk:
                break
            buf += chunk
            if until and until in buf:
                break
        return buf

    def run(self, cmd: str) -> str:
        self.n += 1
        mark = f"__E2519_{self.n}__"
        self.s.sendall(f"{cmd}; echo {mark}\n".encode())
        raw = self._drain(f"\n{mark}".encode())
        data, i = bytearray(), 0
        while i < len(raw):  # quita secuencias IAC
            if raw[i] == 255 and i + 2 < len(raw):
                i += 3
            else:
                data.append(raw[i])
                i += 1
        text = data.decode("utf-8", "replace").replace("\r", "")
        if f"\n{mark}" not in text:
            raise ReadError("sin marcador de fin: la cámara no respondió a tiempo")
        text = re.sub(rf"^.*?echo {mark}\n", "", text, count=1, flags=re.DOTALL)
        return text.rsplit(mark, 1)[0]

    def read(self, phys: int, size: int) -> bytes:
        if phys % 2 or size % 2:
            raise ReadError(f"región no alineada a 2 B: {phys:#x} +{size:#x}")
        cmd = (f"dd if=/dev/mem bs=2 skip={phys // 2} count={size // 2} 2>/dev/null"
               " | chroot /android /system/bin/hd /proc/self/fd/0")
        return parse_hd(self.run(cmd), size)

    def read_many(self, regions: list[tuple[int, int]]) -> list[bytes]:
        """Varias regiones en UN comando (una ida y vuelta): menos tiempo entre ellas."""
        parts = []
        for i, (phys, size) in enumerate(regions):
            if phys % 2 or size % 2:
                raise ReadError(f"región no alineada a 2 B: {phys:#x} +{size:#x}")
            parts.append(f"echo @@{i}@@; dd if=/dev/mem bs=2 skip={phys // 2} count={size // 2} 2>/dev/null"
                         " | chroot /android /system/bin/hd /proc/self/fd/0")
        text = self.run("; ".join(parts))
        chunks = re.split(r"@@(\d+)@@\n", text)
        by_idx = {int(chunks[k]): chunks[k + 1] for k in range(1, len(chunks) - 1, 2)}
        return [parse_hd(by_idx.get(i, ""), size) for i, (_, size) in enumerate(regions)]

    def close(self) -> None:
        self.s.close()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def timed_read(tr: Telnet, phys: int, size: int) -> dict:
    """Lectura con latencia, hora y SHA-256."""
    t0 = time.time()
    ts = now()
    data = tr.read(phys, size)
    return {"physical": f"0x{phys:08x}", "size": size, "t_utc": ts, "latency_ms": round((time.time() - t0) * 1000, 1),
            "sha256": sha(data), "hex": data.hex()}


def verify_originals(tr: Telnet) -> dict:
    """Bytes de T050 y GOT de T052-A. `ok` False ⇒ no disparar ni leer objetos."""
    res: dict = {"ok": True, "items": {}}
    for name, (phys, size, expected) in T050.items():
        got = tr.read(phys, size).hex()
        res["items"][name] = {"physical": f"0x{phys:08x}", "expected": expected, "got": got, "ok": got == expected}
    for name, (phys, exp_ptr) in GOT_CHECKS.items():
        got = struct.unpack("<I", tr.read(phys, 4))[0]
        res["items"][f"got_{name}"] = {"physical": f"0x{phys:08x}", "expected": f"0x{exp_ptr:08x}", "got": f"0x{got:08x}",
                                       "ok": got == exp_ptr}
    res["ok"] = all(v["ok"] for v in res["items"].values())
    return res


def decode_all(name: str, data: bytes) -> dict:
    out = decode(name, data)
    if name.startswith("record"):
        for off, fmt, label in EXTRA_RECORD:
            out[label] = struct.unpack_from(fmt, data, off)[0]
    return out


# Lectura ligera para el muestreo durante el disparo: (offset, bytes) por objeto, solo lo decodificado.
LIGHT = {
    "record_a": [(0, 0x100)], "record_b": [(0, 0x100)], "settings": [(0x15E, 0x08)],
    "imager": [(0x134, 2), (0x4B8, 0x4E)], "gate_b": [(0x8C, 2)], "predicate": [(0x10, 2)],
}


def snapshot(tr: Telnet, label: str, cap_phys: int | None = None, light: bool = False) -> dict:
    """Una lectura de los objetos verificados (y de `cap` solo si su dirección está demostrada).

    `light` lee solo los campos decodificados (varias veces más rápido, para muestrear durante la exposición)."""
    spans: list[tuple[str, int, int]] = []  # (objeto, offset, tamaño)
    for name, (_phys, size) in OBJECTS.items():
        spans += [(name, o, n) for o, n in (LIGHT[name] if light else [(0, size)])]
    if cap_phys is not None:
        spans.append(("cap", 0, 0x4BA0))
    phys_of = {n: p for n, (p, _s) in OBJECTS.items()}
    if cap_phys is not None:
        phys_of["cap"] = cap_phys
    snap: dict = {"label": label, "t_utc": now(), "t_epoch": time.time(), "light": light, "objects": {}}
    t0 = time.time()
    datas = tr.read_many([(phys_of[n] + o, size) for n, o, size in spans])
    snap["latency_ms"] = round((time.time() - t0) * 1000, 1)  # todas las regiones, un solo comando
    for (name, off, size), data in zip(spans, datas, strict=True):
        obj = snap["objects"].setdefault(name, {"physical": f"0x{phys_of[name]:08x}", "spans": [], "decoded": {}})
        obj["spans"].append({"offset": off, "size": size, "sha256": sha(data), "hex": data.hex()})
        if name == "cap":
            obj["decoded"] = {lab: struct.unpack_from(fmt, data, o)[0] for o, fmt, lab in CAP_FIELDS}
            continue
        full = bytes(off) + data  # los campos fuera de los tramos leídos quedan fuera de `dec`
        dec = decode_all(name, full.ljust(0x520, b"\0"))
        want = {lab for o, fmt, lab in FIELDS.get(name, []) + (EXTRA_RECORD if name.startswith("record") else [])
                if off <= o and o + struct.calcsize(fmt) <= off + size}
        obj["decoded"].update({k: v for k, v in dec.items() if k in want})
    return snap


def diff(a: dict, b: dict) -> dict:
    """Campos decodificados que cambian entre dos instantáneas (por objeto)."""
    out: dict = {}
    for name, ra in a["objects"].items():
        rb = b["objects"].get(name)
        if not rb:
            continue
        ch = {k: [ra["decoded"][k], rb["decoded"][k]] for k in ra["decoded"] if ra["decoded"][k] != rb["decoded"].get(k)}
        if ch:
            out[name] = ch
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=HOST)
    ap.add_argument("--label", default="lectura")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--cap-phys", type=lambda x: int(x, 0), help="solo con cadena de punteros demostrada")
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    a = ap.parse_args()
    tr = Telnet(a.host)
    try:
        orig = verify_originals(tr)
        res: dict = {"schema": "e25-19-readonly/v1", "label": a.label, "originals": orig, "snapshots": []}
        if orig["ok"]:
            for i in range(max(1, a.repeats)):
                res["snapshots"].append(snapshot(tr, f"{a.label}#{i}", a.cap_phys))
            if len(res["snapshots"]) > 1:
                res["diff_0_1"] = diff(res["snapshots"][0], res["snapshots"][1])
    finally:
        tr.close()
    out = OUTDIR / f"lectura-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{a.label.replace('/', '_')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(f"{out} originales_ok={orig['ok']}")
    return 0 if orig["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
