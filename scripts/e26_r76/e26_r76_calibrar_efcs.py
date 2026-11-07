#!/usr/bin/env python3
"""E26-R76 - Calibracion propia de la perdida EFCS: de las medidas de luminancia a los valores a escribir. Sin camara.

Entrada: dos `report.json` de scripts/camera_raw_exposure.py con las MISMAS velocidades/ISO/escena/luz,
uno con EFCS activado y otro con EFCS desactivado (referencia mecanica completa = firmware 3.37 oficial).
Salida: tabla {Tmax, c} para el parche de Darwin (G+0x48, ver e26_r76_parche_darwin_tabla.py) y, como
alternativa sin parche, el valor unico de G+0x42 / B+0x86.
R82: T es el efectivo de 0x19a12 (no el nominal); `c` aplicado = el de la TABLA (no el punto fijo); G+0x42, B+0x86 y
B+0x8a se leen del volcado NVRAM (`--nvram DUMP`; sin el, los de R66 s2).

Uso:  e26_r76_calibrar_efcs.py ajustar ON.json OFF.json [--previo TABLA.json --previo-on ON1.json] [--out TABLA.json] [--nvram DUMP]
      e26_r76_calibrar_efcs.py nvram DUMP_ENTRADA.bin DUMP_SALIDA.bin TABLA.json    (genera el volcado a restaurar)
      e26_r76_calibrar_efcs.py selftest
"""
from __future__ import annotations

import json
import statistics
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e26_r76_parche_darwin_tabla as P

CENSURA = 0.04      # r = L_on / L_off por debajo de esto es negro: el dato solo da una cota inferior de la perdida
AMORT = 0.8         # amortiguacion del refinado


def t_nominal(speed: str) -> int:
    n, d = (int(v) for v in speed.split("/"))
    return round(1e6 * n / d)


_IMG: bytes | None = None


def t_efectivo(speed: str) -> int:
    """T que usa Darwin (0x19a12 emulado) para la velocidad `speed`: 1/4000 -> 244 us, no 250 (R81 hallazgo 5)."""
    global _IMG
    import math
    if _IMG is None:
        _IMG = P.DARWIN.read_bytes() if P.DARWIN.exists() else b""
    if not _IMG:
        return t_nominal(speed)
    k = round(3 * math.log2(1e6 / t_nominal(speed)))               # escalon de 1/3 EV
    return P.t_us(_IMG, 0x1000 + round(256 * k / 3))


def c_tabla(tab: list, t: int) -> int:
    """c que aplica Darwin a T = t: el de la primera entrada con t <= Tmax (0 si ninguna) (R81 hallazgo 4)."""
    return next((c for tm, c in tab if t <= tm), 0)


def leer_unidad(dump: str) -> tuple[int, int, int]:
    """(G+0x42, B+0x86, B+0x8a) del volcado NVRAM (R80 s3)."""
    import io
    import struct
    sys.path.insert(0, str(P.ROOT / "references" / "pmca"))
    from pmca.backup import BackupFile
    bf = BackupFile(io.BytesIO(Path(dump).read_bytes()))
    g, b = bf.getProperty(0x1850000).data, bf.getProperty(0x1850001).data
    return struct.unpack_from("<H", g, 0x42)[0], struct.unpack_from("<h", b, 0x86)[0], struct.unpack_from("<h", b, 0x8A)[0]


def razones(rep_on: dict, rep_off: dict) -> dict[str, float]:
    """Cociente de luminancia lineal (sin negro) EFCS on / off por velocidad, mediana de repeticiones."""
    def med(rep):
        out: dict[str, list[float]] = {}
        for r in rep["resultados"]:
            if "mean_lin" in r:
                out.setdefault(r["speed"], []).append(r["mean_lin"])
        return {k: statistics.median(v) for k, v in out.items()}
    on, off = med(rep_on), med(rep_off)
    return {sp: max(on[sp], 0.0) / off[sp] for sp in on if sp in off and off[sp] > 20}


def puntos(r: dict[str, float], tab_prev: list | None = None) -> list[tuple[float, float]]:
    """(x = B - A, perdida) por velocidad. Con tab_prev, Darwin ya trabajaba con T + c(T) (la tabla): x y la perdida se desplazan."""
    pts = []
    for sp, ratio in r.items():
        if ratio < CENSURA:
            continue
        t = t_efectivo(sp)
        c = c_tabla(tab_prev or [], t)
        x = P.separacion(t + c)
        if x is None:
            continue
        pts.append((x, t + c - ratio * t))              # E_on = ratio * T  ->  perdida = T + c - E_on
    return pts


def curva(pts: list[tuple[float, float]], base=(P._X, P._D)):
    """Perdida(x): interpolacion lineal de los puntos medidos; fuera de rango, el modelo R74 desplazado al extremo."""
    pts = sorted(pts)
    xs, ds = [p[0] for p in pts], [p[1] for p in pts]
    if len(pts) < 3:
        return P.perdida
    def f(x):
        if x <= xs[0]:
            return ds[0]                                 # plano hacia lo mas rapido (negro: sin dato, hipotesis R74)
        if x >= xs[-1]:
            return ds[-1]
        return P.perdida(x, xs, ds)
    return f


def ajustar(rep_on: dict, rep_off: dict, previo: dict | None = None, rep_on_prev: dict | None = None,
            unidad: tuple[int, int, int] | None = None):
    if unidad:
        P.usar_unidad(*unidad)
    r1 = razones(rep_on, rep_off)
    pts = puntos(r1, (previo or {}).get("tabla"))
    if previo and rep_on_prev:                           # el pase anterior (sin tabla) tambien aporta puntos
        pts += puntos(razones(rep_on_prev, rep_off))
    f = curva(pts)
    ts = sorted({t_efectivo(sp) for sp in r1})
    tab = P.construir_tabla(ts, perd=f)
    return {"tabla": tab, "c_por_velocidad": {sp: P.resolver_c(t_efectivo(sp), f) for sp in r1}, "unidad": [P.G42, P.B86, P.B8A],
            "puntos": sorted(pts), "razones": r1}


def escribir_tabla_nvram(src: str, dst: str, tab: list[tuple[int, int]]) -> str:
    import hashlib
    import io
    sys.path.insert(0, str(P.ROOT / "references" / "pmca"))
    from pmca.backup import BackupFile
    raw = Path(src).read_bytes()
    buf = io.BytesIO(raw)
    bf = BackupFile(buf)
    g = bytearray(bf.getProperty(0x1850000).data)
    if len(g) != 128 or any(g[P.TAB_OFF:]):     # R81: no assert (se omite con python -O)
        raise SystemExit("G+0x48.. no esta a cero o G no mide 128 B: abortar")
    g42 = struct.unpack_from("<H", g, 0x42)[0]           # Tmax' = Tmax - G42 de ESTE volcado
    try:
        tb = P.tabla_bytes(tab, g42)
    except ValueError as e:
        raise SystemExit(f"tabla fuera de formato (entradas > {P.TAB_MAX}, c fuera de [0, C_MAX] o Tmax' fuera de s16): {e}") from e
    if len(tb) != 128 - P.TAB_OFF:
        raise SystemExit("tabla de tamano inesperado: abortar")
    g[P.TAB_OFF:] = tb
    bf.setProperty(0x1850000, bytes(g))
    bf.updateChecksum()
    Path(dst).write_bytes(buf.getvalue())
    return hashlib.sha256(buf.getvalue()).hexdigest()


# ---------------------------------------------------------------------------------------------- autocomprobacion
def _camara_sintetica(delta_real, tabla=None, a=3.0, ruido=0.004, seed=1):
    """Camara simulada: Darwin usa T' = T + c(T); E = T' - delta_real(x(T')); L = a*E (+ruido). Devuelve un report.json."""
    import random
    rnd = random.Random(seed)
    def rep(efcs):
        res = []
        for sp in ("1/4000", "1/2500", "1/2000", "1/1600", "1/1250", "1/1000", "1/800", "1/640", "1/500", "1/400",
                   "1/320", "1/250", "1/200", "1/160", "1/125", "1/100"):
            t = t_efectivo(sp)
            for k in range(2):
                if efcs:
                    c = c_tabla(tabla or [], t)
                    x = P.separacion(t + c)
                    e = t + c - delta_real(0 if x is None else x)
                else:
                    e = t
                res.append({"speed": sp, "rep": k, "mean_lin": max(a * e * (1 + rnd.gauss(0, ruido)) , 0.0) + 1e-3})
        return {"resultados": res}
    return rep(True), rep(False)


def selftest() -> None:
    real = lambda x: 1.08 * P.perdida(x)                 # la unidad real pierde un 8 % mas que el modelo R74
    on1, off = _camara_sintetica(real)
    r1 = razones(on1, off)
    assert r1["1/1000"] < CENSURA < r1["1/320"] < r1["1/100"], "1/1000 debe salir negro y 1/100 casi completo"
    s1 = ajustar(on1, off)
    print("pase 1:", s1["tabla"])
    on2, _ = _camara_sintetica(real, s1["tabla"], seed=2)
    r2 = razones(on2, off)
    # 1/500 (T = 1953 us) cae junto a la ventana intermedia 0x20544 (T' de 3257 a 3457 us, no modelada): si c ideal queda
    # dentro, se empuja a un borde y el error llega a ~7 % (R80 s3, limite conocido); el resto debe quedar < 6 %
    libres = lambda r: [v for sp, v in r.items() if not 1900 < t_efectivo(sp) < 2300]
    err1 = max(abs(1 - v) for v in libres(r2))
    s2 = ajustar(on2, off, previo=s1, rep_on_prev=on1)
    print("pase 2:", s2["tabla"])
    on3, _ = _camara_sintetica(real, s2["tabla"], seed=3)
    r3 = razones(on3, off)
    err2 = max(abs(1 - v) for v in libres(r3))
    assert abs(1 - r3["1/500"]) < 0.09, "1/500 fuera del limite de la ventana intermedia"
    print(f"error maximo de exposicion: pase 1 {err1:.1%}, pase 2 {err2:.1%}")
    assert min(r2.values()) > 0.4, "tras el pase 1 ninguna velocidad debe seguir negra"
    assert err2 <= err1 + 0.01 and err2 < 0.06
    # escritura NVRAM sobre un volcado real, si existe (lectura/escritura solo de ficheros locales)
    dumps = sorted(P.ROOT.glob("analysis/camera-dumps/*/backup_flash.bin"))
    if dumps:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "v.bin"
            sha = escribir_tabla_nvram(str(dumps[-1]), str(out), s2["tabla"])
            sys.path.insert(0, str(P.ROOT / "references" / "pmca"))
            import io

            from pmca.backup import BackupFile
            g = BackupFile(io.BytesIO(out.read_bytes())).getProperty(0x1850000).data
            assert g[P.TAB_OFF:] == P.tabla_bytes(s2["tabla"]) and g[:P.TAB_OFF] == BackupFile(
                io.BytesIO(dumps[-1].read_bytes())).getProperty(0x1850000).data[:P.TAB_OFF]
            print("NVRAM: volcado de prueba generado", sha[:12], "(no se escribe en la camara)")
    print("selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["selftest"]:
        selftest()
    elif a[:1] == ["ajustar"]:
        on, off = (json.loads(Path(p).read_text()) for p in a[1:3])
        prev = json.loads(Path(a[a.index("--previo") + 1]).read_text()) if "--previo" in a else None
        onp = json.loads(Path(a[a.index("--previo-on") + 1]).read_text()) if "--previo-on" in a else None
        unidad = leer_unidad(a[a.index("--nvram") + 1]) if "--nvram" in a else None
        res = ajustar(on, off, prev, onp, unidad)
        txt = json.dumps(res, indent=1)
        if "--out" in a:
            Path(a[a.index("--out") + 1]).write_text(txt)
        print(txt)
    elif a[:1] == ["nvram"]:
        print(escribir_tabla_nvram(a[1], a[2], [tuple(t) for t in json.loads(Path(a[3]).read_text())["tabla"]]))
    else:
        print(__doc__)
