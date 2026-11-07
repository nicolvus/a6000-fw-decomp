#!/usr/bin/env python3
"""E26-R82 via D - volcados NVRAM modificados (B+0x86 / G+0x42) y tabla de exposicion por velocidad. Solo offline.

Uso:  e26_r82_nvram.py generar [DIR_SALIDA]   genera y verifica las dos variantes a partir del volcado mas reciente
      e26_r82_nvram.py tabla                  exposicion modelada por velocidad (emula 0x18d6e) para las tres variantes
      e26_r82_nvram.py selftest
NO escribe en la camara. Escribir/revertir = senser_backup_restore.py (requiere autorizacion del usuario)."""
from __future__ import annotations

import hashlib
import io
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e26_r76"))
sys.path.insert(0, str(ROOT / "references" / "pmca"))
import e26_r76_parche_darwin_tabla as P

BASE_DUMP = ROOT / "analysis/camera-dumps/20261105-r64-post-var088/backup_flash.bin"   # el mas reciente (estado actual de la camara)
SALIDA = ROOT / "analysis/camera-dumps/20261107-r82-nvram"
BK4 = ROOT / "scripts/e26_r61/bk4_variante.py"
VARIANTES = {"b86_1256": (0x1850001, 0x86, 1250), "g42_2157": (0x1850000, 0x42, -1250)}


def generar(salida: Path = SALIDA, base: Path = BASE_DUMP) -> dict[str, str]:
    from pmca.backup import BackupFile
    salida.mkdir(parents=True, exist_ok=True)
    raw0 = base.read_bytes()
    ref = BackupFile(io.BytesIO(raw0))                       # valida cabecera y checksum de la entrada
    res = {}
    for nombre, (pid, off, delta) in VARIANTES.items():
        dst = salida / f"var_{nombre}.bin"
        subprocess.run([sys.executable, str(BK4), str(base), str(dst), hex(pid), hex(off), str(delta)], check=True,
                       stdout=subprocess.DEVNULL)
        raw = dst.read_bytes()
        bf = BackupFile(io.BytesIO(raw))                     # relectura: checksum valido
        assert len(raw) == len(raw0)
        for p in (0x1850000, 0x1850001):                     # solo cambia el s16 pedido en esa propiedad
            a, b = ref.getProperty(p).data, bf.getProperty(p).data
            dif = [i for i in range(len(a)) if a[i] != b[i]]
            if p == pid:
                assert dif and set(dif) <= {off, off + 1}, dif
            else:
                assert not dif
        res[nombre] = hashlib.sha256(raw).hexdigest()
    (salida / "SHA256SUMS").write_text("".join(f"{h}  var_{n}.bin\n" for n, h in res.items()) +
                                       f"{hashlib.sha256(raw0).hexdigest()}  BASE {base.parent.name}/{base.name}\n")
    return res


def modelo_exposicion(t: int, g42: int, b86: int):
    """(x = B - A, exposicion real) sin tabla. E = x + K - delta(x): K = 3401 (corta) o 3428 (larga) es fisico (R74),
    no depende de G42/B86; la rama corta satura en A = 1 us. Rama intermedia: (None, nan) (0x20544 no modelada)."""
    s48 = t - g42
    if s48 < -150:
        x, k = min(s48 + b86, -1), 3401
    elif s48 > 50:
        x, k = s48 + P.B8A, 3428
    else:
        return None, float("nan")
    return x, x + k - P.perdida(x)


def tabla(img: bytes | None = None):
    img = img or P.DARWIN.read_bytes()
    cfg = {"original": (P.G42, P.B86), "B86=1256": (P.G42, 1256), "G42=2157": (2157, P.B86)}
    filas = []
    for tv in P.velocidades_tercio():
        t = P.t_us(img, tv)
        if not 230 <= t <= 40000:
            continue
        fila: dict = {"tv": tv, "t": t}
        for k, (g42, b86) in cfg.items():
            rama, a, b = P.emular_18d6e(img, tv, None, g42=g42, b86=b86)
            xm, e = modelo_exposicion(t, g42, b86)
            xe = None if rama == "intermedia" else b - a
            if xe is not None:
                assert xm is not None and abs(xe - xm) <= 1, (tv, k, xe, xm)    # doble verificacion: emulacion vs calculo a mano
            fila[k] = (rama, xe, e, (e - t) / t)
        filas.append(fila)
    return cfg, filas


def imprimir(cfg, filas):
    print(f"{'Tv':>6} {'T us':>6} | " + " | ".join(f"{k:^26}" for k in cfg))
    for f in filas:
        print(f"{f['tv']:#6x} {f['t']:6d} | " + " | ".join(
            f"{f[k][0][:5]:>5} x={f[k][1] if f[k][1] is not None else float('nan'):6.0f} {f[k][3]:+7.1%}" for k in cfg))


def selftest():
    img = P.DARWIN.read_bytes()
    cfg, filas = tabla(img)
    imprimir(cfg, filas)
    # control independiente: B86 satura solo en 2,13..3,26 ms y G42 deja 1/4000 sin negro
    f4000 = next(f for f in filas if abs(f["t"] - 250) < 20)
    assert f4000["original"][2] < 0 and f4000["B86=1256"][2] > 0 and f4000["G42=2157"][2] > 0
    if BASE_DUMP.exists():
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            print(generar(Path(d)))
    print("selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["generar"]:
        print(generar(Path(a[1]) if a[1:] else SALIDA))
    elif a[:1] == ["tabla"]:
        imprimir(*tabla())
    else:
        selftest()
