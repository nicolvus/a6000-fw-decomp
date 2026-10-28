#!/usr/bin/env python3
"""T052-B0 — recolector de solo lectura para el VTS y el predicado de cuadro extra.

Objetivo: cuando la cámara vuelva a estar accesible, leer **solo** las regiones
RAM verificadas de T052-A, inmediatamente después de una foto normal, sin
escribir nada en la cámara y sin dejar temporales en ella.

Transporte físico previsto: el telnet root de OpenMemories Tweak ya usado en
T048–T050 (`dd if=/dev/mem ... | base64`). El script **no** escribe en
`/dev/mem`: solo usa `dd if=...` y `base64`. No hay `of=`, ni `tee`, ni
redirecciones a ficheros de la cámara.

Modo offline: `--offline analysis/t052-b0/offline-sample.json` decodifica un
ejemplo sintético claramente marcado. Nunca se mezcla con una lectura física.

Uso físico (cuando la cámara esté disponible):
    python3 scripts/t052_b0_readonly.py --confirm-readonly \
        --host 192.168.1.29 --label 1_4000

El operador fija la velocidad, dispara una foto normal y ejecuta el comando.
El script lee todo dos veces y guarda los bytes, los valores decodificados, el
orden, la hora y los errores en el PC.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import struct
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "analysis/t052-b0"
FW_SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
RAM_OFF = 0x40000000          # virtual = físico - 0x40000000 (objetos de av-cam)
VTS_REF = 4219                # referencia efectiva medida T046/T047
LINE_US = 15.2

# Objetos verificados en T052-A. Direcciones físicas = virtual + RAM_OFF.
OBJECTS = {
    "record_a": (0x83EA5B4C, 0x158),
    "record_b": (0x83EEE770, 0x158),
    "settings": (0x83F79F94, 0x4C0),
    "imager": (0x83EA976C, 0x520),
    "gate_b": (0x83F6E5C2, 0x100),
    "predicate": (0x83DEB360, 0x100),
}

# Sitios de T050: si no coinciden, no se ejecuta la fase física.
T050 = {
    "shutmode_site": (0x836D6FB6, 4, "91f80990"),
    "r5_site": (0x836D7000, 6, "28125ffa85fe"),
}

# GOT: si no coinciden los punteros, el firmware/objeto no es el esperado.
GOT_CHECKS = {
    "record_a": (0x84022648, 0x43EA5B4C),
    "record_b": (0x84025DFC, 0x43EEE770),
    "settings": (0x840207E8, 0x43F79F94),
    "imager": (0x84021BA8, 0x43EA976C),
    "gate_b": (0x84024E58, 0x43F6E5C2),
    "predicate": (0x840253CC, 0x43DEB360),
}

# Campos que pide el protocolo B0. Offset, tipo y nombre.
FIELDS = {
    "record_a": [
        (0x0C, "<I", "periodo_linea_q8"),
        (0x1C, "<H", "suelo"),
        (0x20, "<H", "vts"),
        (0x64, "<I", "r5"),
        (0x68, "<H", "frames"),
        (0x6A, "<H", "aux_6a"),
        (0x6C, "<B", "aux_6c"),
        (0x6D, "<B", "shutmode"),
        (0xD8, "<H", "d8"),
        (0xDA, "<H", "da"),
        (0xDC, "<H", "dc"),
        (0xF0, "<I", "lineas"),
        (0xF6, "<H", "tv"),
    ],
    "record_b": [
        (0x0C, "<I", "periodo_linea_q8"),
        (0x1C, "<H", "suelo"),
        (0x20, "<H", "vts"),
        (0x64, "<I", "r5"),
        (0x68, "<H", "frames"),
        (0x6A, "<H", "aux_6a"),
        (0x6C, "<B", "aux_6c"),
        (0x6D, "<B", "shutmode"),
        (0xD8, "<H", "d8"),
        (0xDA, "<H", "da"),
        (0xDC, "<H", "dc"),
        (0xF0, "<I", "lineas"),
        (0xF6, "<H", "tv"),
    ],
    "settings": [
        (0x162, "<H", "tv"),
        (0x15E, "<H", "modo"),
        (0x164, "<H", "cuadro"),
    ],
    "imager": [
        (0x4B8, "<B", "factor"),
        (0x504, "<B", "modo_504"),
        (0x134, "<H", "periodo_134"),
    ],
    "gate_b": [(0x8C, "<B", "b_8c")],
    "predicate": [(0x10, "<B", "byte_10")],
}


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clean_telnet(data: bytes) -> str:
    """Quita las secuencias IAC del telnet de OpenMemories."""
    out, i = bytearray(), 0
    while i < len(data):
        if data[i] == 255 and i + 2 < len(data):
            i += 3
        else:
            out.append(data[i])
            i += 1
    return out.decode("utf-8", "replace").replace("\r", "")


class ReadError(RuntimeError):
    pass


class TelnetTransport:
    """Telnet root de la cámara; solo lectura.

    Cada comando se envía con un marcador final. El comando usa
    `dd if=/dev/mem ... | base64`; nunca `of=/dev/mem` ni redirecciones a
    ficheros de la cámara.
    """

    def __init__(self, host: str, port: int = 23, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _run(self, command: str, n: int) -> str:
        import socket  # import perezoso: el modo offline no abre red

        s = socket.create_connection((self.host, self.port), timeout=self.timeout)
        s.settimeout(0.5)
        try:
            time.sleep(0.2)
            try:
                s.recv(65536)
            except TimeoutError:
                pass
            mark = f"__T052B0_{n}__"
            s.sendall(f"{command}; echo {mark}\n".encode())
            buf, end = b"", time.time() + self.timeout
            while time.time() < end:
                try:
                    chunk = s.recv(65536)
                except TimeoutError:
                    continue
                if not chunk:
                    break
                buf += chunk
                if f"\n{mark}".encode() in buf or mark.encode() in buf:
                    break
            text = _clean_telnet(buf)
            # Quita el eco del comando y el marcador.
            text = re.sub(rf"^.*?echo {mark}\n", "", text, count=1, flags=re.DOTALL)
            text = text.rsplit(mark, 1)[0]
            return text
        finally:
            s.close()

    def read(self, phys: int, size: int, n: int) -> bytes:
        # T026: el `dd` de la cámara falla con `bs=1` y skip > 2^31. Se usa
        # `bs=2` (todas las direcciones y tamaños son pares) y skip/2.
        if phys % 2 or size % 2:
            raise ReadError(f"región no alineada a 2 B: {phys:#x} +{size:#x}")
        # `base64` de toybox puede partir en líneas; se limpian los espacios.
        cmd = f"dd if=/dev/mem bs=2 skip={phys // 2} count={size // 2} 2>/dev/null | base64"
        text = self._run(cmd, n)
        payload = "".join(text.split())
        if not payload:
            raise ReadError(f"salida vacía en {phys:#x} (+{size:#x})")
        try:
            data = base64.b64decode(payload, validate=True)
        except Exception as exc:
            raise ReadError(f"base64 inválido en {phys:#x}: {exc}") from exc
        if len(data) != size:
            raise ReadError(f"longitud {len(data)} != {size} en {phys:#x}")
        return data


class OfflineTransport:
    """Datos de ejemplo; no es una lectura física."""

    def __init__(self, path: Path):
        self.path = path
        self.doc = json.loads(path.read_text())
        if self.doc.get("source") != "offline-sample" or not self.doc.get("not_physical"):
            raise ReadError("el JSON offline debe declarar source=offline-sample y not_physical=true")
        self.by_addr: dict[int, bytes] = {}
        for name, (obj_phys, _obj_size) in OBJECTS.items():
            raw = self.doc["regions"].get(name)
            if raw is None:
                raise ReadError(f"el ejemplo offline no tiene {name}")
            self.by_addr[obj_phys] = bytes.fromhex(raw)
        for addr, raw in self.doc.get("checks", {}).items():
            self.by_addr[int(addr, 16)] = bytes.fromhex(raw)

    def read(self, phys: int, size: int, n: int) -> bytes:
        data = self.by_addr.get(phys)
        if data is None:
            raise ReadError(f"región no incluida en el ejemplo offline: {phys:#x}")
        if len(data) < size:
            raise ReadError(f"ejemplo corto en {phys:#x}: {len(data)} < {size}")
        return data[:size]


def decode(name: str, data: bytes) -> dict:
    out = {}
    for off, fmt, label in FIELDS.get(name, []):
        try:
            out[label] = struct.unpack_from(fmt, data, off)[0]
        except struct.error:
            out[label] = None
    return out


def derive(readings: dict) -> dict:
    """Valores derivados y comprobaciones del protocolo B0."""
    a = readings["record_a"]["decoded"]
    b = readings["record_b"]["decoded"]
    st = readings["settings"]["decoded"]
    im = readings["imager"]["decoded"]
    pr = readings["predicate"]["decoded"]
    gate = readings["gate_b"]["decoded"]

    def active(rec: dict) -> bool:
        return rec.get("tv") not in (None, 0) and (rec.get("r5") not in (None, 0) or rec.get("vts") not in (None, 0))

    bank = "A" if active(a) and not active(b) else "B" if active(b) and not active(a) else None
    rec = a if bank == "A" else b if bank == "B" else a
    lines = rec.get("lineas") or 0
    c3b = VTS_REF - lines if lines else None
    extra = pr.get("byte_10")
    return {
        "banco_activo_heuristico": bank,
        "tv_coincide_settings": rec.get("tv") == st.get("tv"),
        "periodo_esperado_3891": rec.get("periodo_linea_q8") == 3891,
        "vts_en_rango_conocido": rec.get("vts") in (4219, 4266),
        "predicado_extra_frame": None if extra is None else int(extra < 2),
        "predicado_byte": extra,
        "c3b_r5_desde_lineas": c3b,
        "c3b_representable": None if c3b is None else int(2 <= c3b),
        "c3a_r5_nativo": rec.get("r5"),
        "c3a_valido": None if rec.get("r5") is None or rec.get("vts") is None else int(2 <= rec["r5"] < rec["vts"]),
        "gate_esperada": None
        if gate.get("b_8c") is None or im.get("modo_504") is None
        else (1 if gate["b_8c"] == 1 else 0 if gate["b_8c"] == 2 else int(im["modo_504"] == 3)),
        "lineas": lines,
        "fraccion_cuadro_pct": None
        if not lines
        else round(lines / VTS_REF * 100.0, 2),
    }


def collect(transport, label: str, repeats: int, interval: float) -> dict:
    result: dict[str, Any] = {
        "schema": "t052-b0-readonly/v1",
        "label": label,
        "started_utc": now(),
        "firmware_sha256_expected": FW_SHA,
        "ram_offset": f"0x{RAM_OFF:08x}",
        "vts_ref": VTS_REF,
        "reads": [],
        "checks": {},
        "errors": [],
    }

    # 1. Comprobar los sitios de T050 y la GOT antes de leer los objetos.
    order: int = 0
    for name, (phys, size, expected) in T050.items():
        order += 1
        t0 = time.time()
        try:
            data = transport.read(phys, size, order)
            got = data.hex()
            result["checks"][name] = {
                "physical": f"0x{phys:08x}",
                "expected": expected,
                "got": got,
                "ok": got == expected,
            }
            if got != expected:
                result["errors"].append(f"{name}: {got} != {expected}")
        except Exception as exc:  # noqa: BLE001 - se preserva el error
            result["errors"].append(f"{name}: {exc}")
    for name, (phys, expected_ptr) in GOT_CHECKS.items():
        order += 1
        try:
            data = transport.read(phys, 4, order)
            got = struct.unpack("<I", data)[0]
            result["checks"][f"got_{name}"] = {
                "physical": f"0x{phys:08x}",
                "expected": f"0x{expected_ptr:08x}",
                "got": f"0x{got:08x}",
                "ok": got == expected_ptr,
            }
            if got != expected_ptr:
                result["errors"].append(f"got_{name}: 0x{got:08x} != 0x{expected_ptr:08x}")
        except Exception as exc:  # noqa: BLE001 - se preserva el error
            result["errors"].append(f"got_{name}: {exc}")

    if result["errors"]:
        result["aborted"] = True
        result["finished_utc"] = now()
        return result

    # 2. Leer los objetos dos veces (el protocolo pide comprobar estabilidad).
    for rep in range(repeats):
        if rep:
            time.sleep(interval)
        snapshot: dict[str, Any] = {}
        for name, (phys, size) in OBJECTS.items():
            order += 1
            t0 = time.time()
            try:
                data = transport.read(phys, size, order * 100 + rep)
                snapshot[name] = {
                    "physical": f"0x{phys:08x}",
                    "size": size,
                    "order": order,
                    "timestamp_utc": now(),
                    "duration_ms": round((time.time() - t0) * 1000, 1),
                    "sha256": sha256(data),
                    "hex": data.hex(),
                    "decoded": decode(name, data),
                    "ok": True,
                }
            except Exception as exc:  # noqa: BLE001 - se preserva el error
                snapshot[name] = {
                    "physical": f"0x{phys:08x}",
                    "size": size,
                    "order": order,
                    "timestamp_utc": now(),
                    "duration_ms": round((time.time() - t0) * 1000, 1),
                    "ok": False,
                    "error": str(exc),
                }
                result["errors"].append(f"{name}: {exc}")
        result["reads"].append(snapshot)

    # 3. Estabilidad entre lecturas.
    if len(result["reads"]) >= 2:
        stable = {}
        for name in OBJECTS:
            a = result["reads"][0].get(name, {})
            b = result["reads"][1].get(name, {})
            stable[name] = bool(a.get("ok") and b.get("ok") and a.get("sha256") == b.get("sha256"))
        result["checks"]["estable_entre_lecturas"] = stable

    result["derived"] = [derive(r) for r in result["reads"] if all(v.get("ok") for v in r.values())]
    result["aborted"] = bool(result["errors"])
    result["finished_utc"] = now()
    return result


def protocol() -> str:
    return """T052-B0 — lectura de VTS, período, línea y predicado (SOLO LECTURA)
=====================================================================
Requisitos: cámara con fw 3.23 (Darwin B1a), modo M, ISO fijo, RAW+JPEG,
trípode, escena fija. Sin parche RAM. El script comprueba antes:
  - 0x836d6fb6 = 91f80990  (sitio ShutMode de T050)
  - 0x836d7000 = 28125ffa85fe (sitio r5 de T050)
  - los seis punteros de la GOT de T052-A
Si algo no coincide, aborta sin leer los objetos.

Para cada velocidad (1/4000, 1/250, 1/60):
  1. Fijar la velocidad con los controles normales y esperar a que se estabilice.
  2. Disparar una foto normal (sin parche).
  3. Ejecutar:
       python3 scripts/t052_b0_readonly.py --confirm-readonly \\
           --host 192.168.1.29 --label <velocidad>
     El script lee dos veces, en orden, y guarda los bytes en el PC.
  4. Repetir la lectura inmediata; si cambia, documentar la transición.
  5. No escribir RAM/NVRAM/NAND; no ejecutar 0x4383fa40 en la cámara.

Objetos (físicos; virtual = físico - 0x40000000):
  record A 0x83ea5b4c 0x158 B: +0xc +0x1c +0x20 +0x64 +0x68 +0x6d +0xf0 +0xf6
  record B 0x83eee770 0x158 B: los mismos
  settings 0x83f79f94 0x4c0 B: +0x162
  imager   0x83ea976c 0x520 B: +0x4b8 +0x504 +0x134
  gate B   0x83f6e5c2 0x100 B: +0x8c
  pred     0x83deb360 0x100 B: +0x10 (bloque completo para comparar con NVRAM)

Criterios de parada:
  - los sitios de T050 o la GOT no coinciden;
  - record+0x20 no es 4219/4266, o el período no es 3891;
  - record+0xf6 no coincide con settings+0x162;
  - el predicado es >= 2 (sin cuadro extra) y el r5 nativo queda fuera de rango;
  - cualquier lectura incoherente entre A y B.

Decisión C3:
  - C3-A (r5 nativo directo): solo si el predicado es >= 2 y el VTS es coherente.
  - C3-B (r5 = 4219 - record+0xf0): preferido; `lineas` no depende del VTS
    ni del predicado. La referencia 4219 es la medida T046/T047.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="192.168.1.29")
    ap.add_argument("--label", default="sin-etiqueta")
    ap.add_argument("--repeats", type=int, default=2, help="lecturas completas (protocolo: 2)")
    ap.add_argument("--interval", type=float, default=0.2, help="segundos entre lecturas")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--offline", type=Path, help="JSON de ejemplo; no es una lectura física")
    ap.add_argument("--confirm-readonly", action="store_true", help="obligatorio en modo físico")
    ap.add_argument("--protocol", action="store_true", help="imprime el protocolo y sale")
    args = ap.parse_args()

    if args.protocol:
        print(protocol())
        return 0

    transport: OfflineTransport | TelnetTransport
    if args.offline:
        if args.confirm_readonly:
            print("--offline y --confirm-readonly son incompatibles", file=sys.stderr)
            return 2
        transport = OfflineTransport(args.offline)
        mode = "offline-sample"
    else:
        if not args.confirm_readonly:
            print("modo físico exige --confirm-readonly (solo lectura)", file=sys.stderr)
            return 2
        transport = TelnetTransport(args.host)
        mode = "telnet-readonly"

    res = collect(transport, args.label, max(1, args.repeats), max(0.0, args.interval))
    res["mode"] = mode
    res["valid_as_physical_reading"] = mode == "telnet-readonly"
    if mode == "offline-sample":
        res["offline_source"] = str(args.offline)
        res["offline_notice"] = "DATOS DE EJEMPLO: no son una lectura de la cámara"

    out = args.out or (OUTDIR / f"lecturas-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{args.label.replace('/', '_')}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(f"escrito {out}")
    print(f"modo={mode} errores={len(res['errors'])} abortado={res.get('aborted')}")
    if res.get("derived"):
        d = res["derived"][-1]
        print(f"banco={d['banco_activo_heuristico']} vts={d.get('vts_en_rango_conocido')} "
              f"predicado={d['predicado_byte']} extra={d['predicado_extra_frame']} "
              f"lineas={d['lineas']} c3b={d['c3b_r5_desde_lineas']}")
    return 0 if not res["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
