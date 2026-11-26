"""Especificación y validación de un `.cube` antes de meterlo en la cámara (G114).

Comprueba lo que el pipeline real necesita: rejilla 3D de 2…129, filas completas, dominio coherente, valores finitos y en rango,
sin LUT 1D embebida (ni el ISP 5×9×9 ni `lutjpg` la aplican) y sin LUTs degeneradas (identidad o constante).
`python3 cube_spec.py A.cube B.cube …` imprime el informe; `valida()` devuelve (Spec, errores, avisos).

Límites que impone la cámara (no se comprueban aquí, se documentan en docs/gui/g114):
- ISP: rejilla fija 5×9×9 en YCbCr (G90 §C, G93); cualquier `.cube` mayor se ajusta en el PC.
- Software (`lutjpg`): 2…129³, interpolación tetraédrica, solo JPEG.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path

N_MIN, N_MAX = 2, 129
N_RECOMENDADAS = (17, 33, 65)
TOL = 1e-3


@dataclass
class Spec:
    ruta: str
    sha256: str
    titulo: str = ""
    n: int = 0
    dom_lo: tuple[float, float, float] = (0.0, 0.0, 0.0)
    dom_hi: tuple[float, float, float] = (1.0, 1.0, 1.0)
    filas: int = 0
    tiene_1d: bool = False
    rango_datos: tuple[float, float] = (0.0, 0.0)
    identidad: bool = False
    constante: bool = False
    uniforme: bool = False  # 1D declarada: la salida depende de un solo eje
    entrada_log: bool = (
        False  # TITLE/comentario dice V-Log/S-Log: espera entrada logarítmica
    )
    max_linea: int = 0  # la línea más larga; el lector de la cámara corta en 95
    comentarios: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @property
    def kb(self) -> float:
        return self.filas * 3 * 8 / 1024


def _lee(ruta: Path) -> tuple[Spec, list[str], list[str]]:
    """Parser estricto. Devuelve (spec, errores, avisos)."""
    b = Path(ruta).read_bytes()
    s = Spec(str(ruta), hashlib.sha256(b).hexdigest())
    err: list[str] = []
    filas: list[tuple[float, float, float]] = []
    try:
        texto = b.decode("utf-8")
    except UnicodeDecodeError:
        return s, ["no es texto UTF-8"], []
    for lin in texto.splitlines():
        s.max_linea = max(s.max_linea, len(lin))
        if lin.lstrip().startswith("#") and len(s.comentarios) < 4:
            s.comentarios.append(lin.strip())
        t = lin.split("#")[0].split()
        if not t:
            continue
        k = t[0]
        if k == "TITLE":
            s.titulo = " ".join(t[1:]).strip('"')
        elif k == "LUT_3D_SIZE":
            try:
                s.n = int(t[1])
            except (IndexError, ValueError):
                err.append("LUT_3D_SIZE sin entero")
        elif k == "LUT_1D_SIZE":
            s.tiene_1d = True
        elif k == "LUT_1D_INPUT_RANGE":
            s.tiene_1d = True
            s.avisos.append("LUT_1D_INPUT_RANGE: el pipeline solo aplica 3D")
        elif k == "LUT_3D_INPUT_RANGE":
            s.avisos.append(
                "LUT_3D_INPUT_RANGE presente (se interpreta como dominio 0…1)"
            )
        elif k == "DOMAIN_MIN":
            s.dom_lo = tuple(float(v) for v in t[1:4])  # type: ignore[assignment]
        elif k == "DOMAIN_MAX":
            s.dom_hi = tuple(float(v) for v in t[1:4])  # type: ignore[assignment]
        else:
            try:
                filas.append((float(t[0]), float(t[1]), float(t[2])))
            except (IndexError, ValueError):
                err.append(f"línea sin 3 números: {lin[:40]!r}")
    s.filas = len(filas)
    if not err:
        if not (N_MIN <= s.n <= N_MAX):
            err.append(f"LUT_3D_SIZE {s.n}: fuera de {N_MIN}…{N_MAX}")
        if s.filas != s.n**3:
            err.append(f"{s.filas} filas para LUT_3D_SIZE {s.n} (esperadas {s.n**3})")
        for i in range(3):
            if not s.dom_lo[i] < s.dom_hi[i]:
                err.append(f"DOMAIN_MIN/MAX incoherentes en el eje {i}")
        if s.filas:
            vals = [v for f in filas for v in f]
            s.rango_datos = (min(vals), max(vals))
            if any(math.isnan(v) for v in vals):
                err.append("hay valores NaN")
            elif (
                s.rango_datos[0] < min(s.dom_lo) - TOL
                or s.rango_datos[1] > max(s.dom_hi) + TOL
            ):
                err.append(
                    f"datos {s.rango_datos[0]:.3f}…{s.rango_datos[1]:.3f} fuera del dominio"
                )
            if s.rango_datos[1] - s.rango_datos[0] < 1e-4:
                s.constante = True
                err.append("salida constante: no aporta")
            if s.n >= N_MIN and s.filas == s.n**3:
                s.identidad = _es_identidad(filas, s.n, s.dom_lo, s.dom_hi)
                s.uniforme = _es_uniforme(filas, s.n)
        estilo = next(
            (c.upper() for c in s.comentarios if "LUMIXPHOTOSTYLE" in c.upper()), ""
        )
        meta = (s.titulo + " " + estilo).upper()
        s.entrada_log = (
            "VLOG" in meta or "V-LOG" in meta or "SLOG" in meta or "S-LOG" in meta
        ) and "STD" not in estilo
        if s.entrada_log:
            s.avisos.append(
                "entrada logarítmica (V-Log/S-Log): en la A6000 el look sale lavado; usa la variante STD"
            )
        if s.max_linea > 95:
            s.avisos.append(
                f"línea de {s.max_linea} caracteres: el lector de la cámara corta en 95 (usa %0.6f y líneas cortas)"
            )
        if s.n > 64:
            s.avisos.append(
                f"{s.n}³ no cabe en el lector .cube de la cámara (≤64): usa el paquete .LUT o lutjpg"
            )
        if s.n and s.n not in N_RECOMENDADAS:
            s.avisos.append(
                f"rejilla {s.n}³: el pipeline la acepta; 17³/33³/65³ son las habituales"
            )
        if s.n > 65:
            s.avisos.append(
                f"{s.n}³ = {s.n**3} nodos: el ajuste en el PC tarda y el software usa {s.n**3 * 6 / 1e6:.1f} MB"
            )
    return s, err, s.avisos


def _es_identidad(filas, n, lo, hi) -> bool:
    for i in range(n):
        for j in range(n):
            for k in range(n):
                r, g, b = filas[i * n * n + j * n + k]
                esperado = (
                    lo[0] + (hi[0] - lo[0]) * i / (n - 1),
                    lo[1] + (hi[1] - lo[1]) * j / (n - 1),
                    lo[2] + (hi[2] - lo[2]) * k / (n - 1),
                )
                if (
                    max(
                        abs(r - esperado[0]), abs(g - esperado[1]), abs(b - esperado[2])
                    )
                    > TOL
                ):
                    return False
    return True


def _es_uniforme(filas, n) -> bool:
    """La salida no cambia al mover el eje R (típico de un .cube 1D convertido a 3D)."""
    if n < 2:
        return True
    for j in range(n):
        for k in range(n):
            base = filas[j * n + k]
            for i in range(1, n):
                if (
                    max(
                        abs(filas[i * n * n + j * n + k][c] - base[c]) for c in range(3)
                    )
                    > TOL
                ):
                    return False
    return True


def valida(ruta: str | Path) -> tuple[Spec, list[str], list[str]]:
    try:
        return _lee(Path(ruta))
    except OSError as e:
        return Spec(str(ruta), ""), [f"no se puede leer: {e}"], []


def apta(spec: Spec, errores: list[str]) -> str:
    """Clasificación para la cámara: HARDWARE, SOLO SOFTWARE o NO APTA."""
    if errores:
        return "NO APTA"
    if spec.tiene_1d or spec.uniforme:
        return "SOLO SOFTWARE"
    return "HARDWARE"


def _main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit("uso: cube_spec.py A.cube [B.cube …]")
    print(
        f"{'fichero':28s} {'n':>3s} {'filas':>6s} {'dominio':>13s} {'resultado':>14s}  avisos"
    )
    for ruta in argv:
        s, err, av = valida(ruta)
        dom = f"{s.dom_lo[0]:g}…{s.dom_hi[0]:g}" if s.n else "—"
        res = (
            "ERR: " + err[0] if err else ("identidad" if s.identidad else apta(s, err))
        )
        extra = "; ".join((err[1:] if len(err) > 1 else []) + av)
        print(
            f"{Path(ruta).name[:28]:28s} {s.n:3d} {s.filas:6d} {dom:>13s} {res:>14s}  {extra[:90]}"
        )


if __name__ == "__main__":
    import sys

    _main(sys.argv[1:])
