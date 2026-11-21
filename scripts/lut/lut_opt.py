"""G90 — ajuste de la LUT 3D 5×9×9 (405 nodos × 3 deltas s7) directamente en ΔE2000 (no en RGB) y modelo de interpolación.

Entrada: colores `c` que llegan a la LUT (salida de M y T) y objetivo `y` (el `.cube`). Pasos: (1) solución inicial por mínimos cuadrados (cube_a6000.ajusta_lut3d);
(2) Gauss-Newton sobre ε = (ΔL/SL, ΔC/SC, ΔH/SH) con caja ±64 (L-BFGS-B sobre el cuadrático, recorte de canal RGB respetado); (3) refinamiento entero por
coordenadas sobre el ΔE2000 exacto ponderado. `modelo`: "tri" (trilineal), "tetra" (tetraédrica) o "ambos" (promedia las dos: robusto mientras la cámara no decida, g90 §A).
shortcut: pesos de muestra sintéticos (piel = nube HSV aproximada); sustituir por pixeles reales cuando haya más pares RAW+JPG.
uso: lut_opt.py [--rapido]  → tabla de ΔE antes/después sobre 4 LUT a 17³ y 32³ (g90 §B).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp  # type: ignore[import-untyped]  # sin stubs instalados (PEP 668)
from scipy.optimize import minimize  # type: ignore[import-untyped]

sys.path.insert(0, str(Path(__file__).parent))
import cube_a6000 as C

MODELO_DEFECTO = "ambos"          # g90 §A: la cámara no ha decidido tri/tetra; 'ambos' acota la pérdida (cambiar a "tri"/"tetra" cuando decida exp_interp)
U = np.array([C.UY, C.UC, C.UC])
LO, HI = -64.0, 63.0
_T = np.stack([C.ycc2rgb(e) for e in np.eye(3)], 1)       # rgb = _T @ ycc (lineal)
ESTRIDE = np.array([81, 9, 1])


# ---------- interpolación ----------
def pesos_tetra(u: np.ndarray):
    """Tetraédrica (6 tetraedros por celda, diagonal 000→111): (índices [M,4], pesos [M,4])."""
    gy = np.clip(u[:, 0], 0, 1) * (C.NY - 1)
    gc = (np.clip(u[:, 1:], -0.5, 0.5) + 0.5) * (C.NC - 1)
    g = np.column_stack([gy, gc])
    i0 = np.minimum(g.astype(int), np.array([C.NY - 2, C.NC - 2, C.NC - 2]))
    f = g - i0
    o = np.argsort(-f, 1, kind="stable")
    fs = np.take_along_axis(f, o, 1)
    base = i0 @ ESTRIDE
    paso = ESTRIDE[o]
    idx = np.stack([base, base + paso[:, 0], base + paso[:, 0] + paso[:, 1], base + paso.sum(1)], 1)
    w = np.stack([1 - fs[:, 0], fs[:, 0] - fs[:, 1], fs[:, 1] - fs[:, 2], fs[:, 2]], 1)
    return idx, w


def pesos_m(u, modelo):
    return pesos_tetra(u) if modelo == "tetra" else C.pesos(u)


def aplica(q, c, modelo="tri"):
    """Salida RGB (sin recortar) de la LUT cuantizada `q` [405,3] sobre colores `c`. 'ambos' = media de las dos interpolaciones."""
    if modelo == "ambos":
        return 0.5 * (aplica(q, c, "tri") + aplica(q, c, "tetra"))
    u = C.rgb2ycc(c)
    idx, w = pesos_m(u, modelo)
    d = q.astype(float) * U
    return C.ycc2rgb(u + np.einsum("mk,mkc->mc", w, d[idx]))


# ---------- ΔE2000 y linealización ----------
def lab(rgb):
    """Lab sin recortar RGB (para derivadas)."""
    l = C.a_lineal(rgb)
    xyz = l @ np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]]) / np.array([0.95047, 1, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(np.abs(xyz)) * np.sign(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def _mapa_eps(L, a, b):
    """Matriz [M,3,3]: ΔLab → (ΔL/SL, ΔC'/SC, ΔH'/SH) en el color objetivo (CIEDE2000 linealizada, sin el término RT)."""
    C0 = np.hypot(a, b)
    G = 0.5 * (1 - np.sqrt(C0 ** 7 / (C0 ** 7 + 25 ** 7)))
    ap = (1 + G) * a
    Cp = np.hypot(ap, b)
    h = np.degrees(np.arctan2(b, ap)) % 360
    T = 1 - 0.17 * np.cos(np.radians(h - 30)) + 0.24 * np.cos(np.radians(2 * h)) + 0.32 * np.cos(np.radians(3 * h + 6)) - 0.20 * np.cos(np.radians(4 * h - 63))
    Sl = 1 + 0.015 * (L - 50) ** 2 / np.sqrt(20 + (L - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cp, 1 + 0.015 * Cp * T
    ok = Cp > 1e-6
    ca = np.where(ok, ap / np.where(ok, Cp, 1), 1.0)
    sb = np.where(ok, b / np.where(ok, Cp, 1), 0.0)
    S = np.zeros((len(L), 3, 3))
    S[:, 0, 0] = 1 / Sl
    S[:, 1, 1] = ca * (1 + G) / Sc; S[:, 1, 2] = sb / Sc
    S[:, 2, 1] = -sb * (1 + G) / Sh; S[:, 2, 2] = ca / Sh
    return S


def _jac_lab(rgb, h=1e-3):
    """dLab/dRGB [M,3,3] por diferencias centrales sin recorte."""
    J = np.zeros((len(rgb), 3, 3))
    for k in range(3):
        d = np.zeros(3); d[k] = h
        J[:, :, k] = (lab(rgb + d) - lab(rgb - d)) / (2 * h)
    return J


def objetivo(q, c, y, w, modelo="tri"):
    e = C.de2000(y, np.clip(aplica(q, c, modelo), 0, 1))
    return float(np.sum(w * e) / np.sum(w))


# ---------- muestras ----------
def piel(n, rng):
    """Nube HSV aproximada de tonos de piel (h 8°–38°, s 0,15–0,65, v 0,2–1): n colores RGB."""
    h, s, v = rng.uniform(8, 38, n) / 360, rng.uniform(0.15, 0.65, n), rng.uniform(0.2, 1.0, n)
    f = h * 6                                                                   # sector 0 de HSV: (v, t, p)
    return np.stack([v, v * (1 - s * (1 - f)), v * (1 - s)], 1)


def muestras(n_unif=12000, seed=11, foto: np.ndarray | None = None):
    """Muestras de entrenamiento (x [M,3] RGB de pantalla, peso [M]): uniformes 45 %, neutros 20 %, piel 20 %, foto 15 % (si hay). Pesos suman 1."""
    rng = np.random.default_rng(seed)
    xs, ws = [rng.random((n_unif, 3))], [0.45]
    g = np.linspace(0, 1, 257)
    xs.append(np.repeat(g[:, None], 3, 1)); ws.append(0.20)
    xs.append(piel(3000, rng)); ws.append(0.20)
    if foto is not None:
        xs.append(foto); ws.append(0.15)
    else:
        ws = [x / 0.85 for x in ws]
    w = np.concatenate([np.full(len(x), wk / len(x)) for x, wk in zip(xs, ws)])
    return np.concatenate(xs), w


# ---------- Gauss-Newton ΔE ----------
def _estructura(c, modelo):
    """(índices, pesos) por muestra; 'ambos' concatena las dos con la mitad de peso cada una."""
    u = C.rgb2ycc(c)
    if modelo == "ambos":
        i1, w1 = C.pesos(u)
        i2, w2 = pesos_tetra(u)
        return np.concatenate([i1, i2], 1), np.concatenate([w1, w2], 1) / 2
    return pesos_m(u, modelo)


def laplaciano():
    L = np.zeros((C.N, C.N))
    for j in range(C.NY):
        for a in range(C.NC):
            for b in range(C.NC):
                i = j * 81 + a * 9 + b
                for dj, da, db in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    if j + dj < C.NY and a + da < C.NC and b + db < C.NC:
                        k = i + dj * 81 + da * 9 + db
                        L[i, i] += 1; L[k, k] += 1; L[i, k] -= 1; L[k, i] -= 1
    return L


def _gn(v, c, y, w, idx, wt, modelo, lam, lab_y, S):
    """Un paso Gauss-Newton: devuelve v nuevo (unidades enteras, flotante, dentro de la caja)."""
    M = len(c)
    u = C.rgb2ycc(c)
    d = v * U
    out = C.ycc2rgb(u + np.einsum("mk,mkc->mc", wt, d[idx]))
    mask = ((out > 0) & (out < 1)).astype(float)
    res = np.einsum("mij,mj->mi", S, lab(np.clip(out, 0, 1)) - lab_y)
    E = np.einsum("mij,mjk->mik", S, _jac_lab(np.clip(out, 1e-3, 1 - 1e-3))) * mask[:, None, :]
    E = np.einsum("mik,kl->mil", E, _T)                                     # [M,3(eps),3(ycc)]
    sw = np.sqrt(w)[:, None]
    K = idx.shape[1]
    rows = np.repeat(np.arange(3 * M), K * 3)
    # columna = idx·3 + c ; valor = sqrt(w)·wt·E[m,e,c]·U[c]
    cols = (idx[:, None, :, None] * 3 + np.arange(3)[None, None, None, :]).repeat(3, 1).reshape(-1)
    val = (sw[:, :, None, None] * wt[:, None, :, None] * E[:, :, None, :] * U[None, None, None, :]).reshape(-1)
    A = sp.csr_matrix((val, (rows, cols)), shape=(3 * M, C.N * 3))
    H = (A.T @ A).toarray()
    g = -(A.T @ (sw * res).reshape(-1))
    Lp = np.kron(laplaciano(), np.eye(3)) * lam
    H = H + Lp + 1e-9 * np.eye(C.N * 3)
    vf = v.reshape(-1)
    rhs = g - Lp @ vf

    try:
        dl = np.linalg.solve(H, rhs)                       # sin caja: Cholesky/LU directo, casi siempre basta
    except np.linalg.LinAlgError:
        dl = np.zeros_like(vf)
    lb, ub = LO - vf, HI - vf
    if (dl < lb - 1e-9).any() or (dl > ub + 1e-9).any():  # la caja ±64 muerde: cuadrático con límites, arrancando del recorte
        def f(x):
            return 0.5 * x @ H @ x - rhs @ x, H @ x - rhs

        dl = minimize(f, np.clip(dl, lb, ub), jac=True, method="L-BFGS-B", bounds=list(zip(lb, ub)), options={"maxiter": 400, "ftol": 1e-13, "gtol": 1e-8}).x
    return (vf + dl).reshape(C.N, 3)


def ajusta_de(c, y, w=None, modelo="tri", v0=None, iters=6, lam=None, entero=True, pasadas=3, ver=False):
    """Tabla s7 [405,3] (int8) que minimiza el ΔE2000 medio ponderado de LUT(c) frente a y. `v0` = inicio flotante en unidades enteras (por defecto, el ajuste LSQ)."""
    w = np.full(len(c), 1.0 / len(c)) if w is None else w / w.sum()
    lam = 1e-7 if lam is None else lam
    modelo_i = modelo
    idx, wt = _estructura(c, modelo_i)
    lab_y = lab(y)
    S = _mapa_eps(*np.moveaxis(lab_y, -1, 0))
    if v0 is None:
        u = C.rgb2ycc(c)
        v0 = C.ajusta_lut3d(u, C.rgb2ycc(y) - u) / U
    v = np.clip(v0, LO, HI)
    def obj(vv):
        out = C.ycc2rgb(C.rgb2ycc(c) + np.einsum("mk,mkc->mc", wt, (vv * U)[idx]))
        return float(np.sum(w * C.de2000(y, np.clip(out, 0, 1))))
    best, vb = obj(v), v
    for it in range(iters):
        vn = _gn(v, c, y, w, idx, wt, modelo, lam, lab_y, S)
        paso = 1.0
        while paso > 0.1:
            cand = v + paso * (vn - v)
            o = obj(cand)
            if o < best - 1e-9:
                best, vb, v = o, cand, cand
                break
            paso /= 2
        else:
            break
        if ver:
            print(f"  GN {it}: ΔE medio ponderado {best:.4f}")
    q = np.clip(np.round(vb), LO, HI)
    if entero:
        q = refina_entero(q, c, y, w, idx, wt, pasadas)
    return q.astype(np.int8)


def refina_entero(q, c, y, w, idx, wt, pasadas=3):
    """Descenso por coordenadas enteras (±1, ±2) sobre el ΔE2000 exacto ponderado, solo con las muestras que tocan cada nodo."""
    q = q.copy()
    u = C.rgb2ycc(c)
    K = idx.shape[1]
    muestras_de = [[] for _ in range(C.N)]
    nodo_m = np.argsort(idx.reshape(-1), kind="stable")
    cuenta = np.bincount(idx.reshape(-1), minlength=C.N)
    ini = np.concatenate([[0], np.cumsum(cuenta)])
    for n in range(C.N):
        muestras_de[n] = np.unique(nodo_m[ini[n]:ini[n + 1]] // K)
    oy = u + np.einsum("mk,mkc->mc", wt, (q * U)[idx])                 # salida en YCC
    e = C.de2000(y, np.clip(C.ycc2rgb(oy), 0, 1))
    for _ in range(pasadas):
        mejoras = 0
        for n in range(C.N):
            ms = muestras_de[n]
            if len(ms) == 0:
                continue
            pw = np.where(idx[ms] == n, wt[ms], 0).sum(1)
            base = float(np.sum(w[ms] * e[ms]))
            for ch in range(3):
                for dl in (-1, 1, -2, 2):
                    nv = q[n, ch] + dl
                    if nv < LO or nv > HI:
                        continue
                    o2 = oy[ms].copy()
                    o2[:, ch] += pw * dl * U[ch]
                    e2 = C.de2000(y[ms], np.clip(C.ycc2rgb(o2), 0, 1))
                    nuevo = float(np.sum(w[ms] * e2))
                    if nuevo < base - 1e-12:
                        q[n, ch] = nv
                        oy[ms] = o2
                        e[ms] = e2
                        base = nuevo
                        mejoras += 1
                        break
        if not mejoras:
            break
    return q


# ---------- métricas ----------
def zonas(y_ref, e):
    """ΔE por zona del objetivo: sombras/medios/altas luces y neutros/saturados (medio, p95, máx, n)."""
    L, a, b = np.moveaxis(C.a_lab(np.clip(y_ref, 0, 1)), -1, 0)
    ch = np.hypot(a, b)
    out = {}
    for nombre, m in (("todo", np.ones(len(e), bool)), ("sombras L<30", L < 30), ("medios 30-70", (L >= 30) & (L <= 70)), ("altas L>70", L > 70),
                      ("neutros C<10", ch < 10), ("saturados C>40", ch > 40)):
        if m.sum() > 10:
            out[nombre] = (float(e[m].mean()), float(np.percentile(e[m], 95)), float(e[m].max()), int(m.sum()))
    return out


# ---------- LUT de prueba (g90): suave, película, teal&orange, agresiva ----------
def lut_suave(x):
    y = (x @ np.array([0.299, 0.587, 0.114]))[:, None]
    g = y + (x - y) * 1.08
    return np.clip(np.clip(g, 0, 1) ** 1.06 + 0.01 * np.array([1.0, 0.0, -1.0]), 0, 1)


def lut_agresiva(x):
    """Contraste duro + saturación ×1,8 + giro de tono: excede el rango ±64 en muchos nodos."""
    s = lambda v, k: 1 / (1 + np.exp(-k * (v - 0.5)))
    v = (s(x, 9.0) - s(0, 9.0)) / (s(1, 9.0) - s(0, 9.0))
    y = (v @ np.array([0.299, 0.587, 0.114]))[:, None]
    v = y + (v - y) * 1.8
    th = np.radians(25)
    cb, cr = (v[:, 2:3] - y) , (v[:, 0:1] - y)
    cb2, cr2 = cb * np.cos(th) - cr * np.sin(th), cb * np.sin(th) + cr * np.cos(th)
    r = y + cr2
    b = y + cb2
    g = (y - 0.299 * r - 0.114 * b) / 0.587
    return np.clip(np.concatenate([r, g, b], 1), 0, 1)


PRUEBA = {"suave": lut_suave, "pelicula": C.lut_pelicula, "teal_orange": C.lut_teal_orange, "agresiva": lut_agresiva}
ARW = [Path("/home/nicolas/Desktop/16161111") / n for n in ("DSC03779.ARW", "DSC03799.ARW", "DSC03767.ARW")]


def conjuntos_eval():
    """Conjuntos de evaluación independientes del entrenamiento: uniforme (semilla 7, como sd_lut), fotos 2 y 3, neutros, piel (semilla distinta)."""
    ev = {"uniforme": np.random.default_rng(7).random((20000, 3))}
    for k, a in enumerate(ARW[1:]):
        if a.exists():
            ev[f"foto{k + 1}"] = C.foto(a, 360)
    g = np.linspace(0, 1, 513)
    ev["neutros"] = np.repeat(g[:, None], 3, 1)
    ev["piel"] = piel(3000, np.random.default_rng(99))
    return ev


def stats(e):
    return float(e.mean()), float(np.percentile(e, 95)), float(e.max())


def caso(args):
    nombre, n, metodos = args
    import tempfile
    f0 = PRUEBA[nombre]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.cube"
        C.escribe_cube(p, f0, n, nombre)
        tab, lo, hi = C.lee_cube(p)
    f = lambda x: C.aplica_cube(tab, lo, hi, x)
    ch = C.Cadena()
    foto = C.foto(ARW[0], 320) if ARW[0].exists() else None
    xt, w = muestras(foto=foto)
    c, y = ch.pre_lut(xt), f(xt)
    ev = conjuntos_eval()
    res = {}
    for met in metodos:
        if met == "viejo":
            u = C.rgb2ycc(c)
            raw = C.ajusta_lut3d(u, C.rgb2ycc(y) - u)
            q, rec = C.a_unidades(raw)
        else:
            q = ajusta_de(c, y, w, met)
            rec = int(np.sum((q == -64) | (q == 63)))
        fila = {"rec": rec}
        for mod in ("tri", "tetra"):
            for k, x in ev.items():
                fila[(mod, k)] = stats(C.de2000(f(x), np.clip(aplica(q, ch.pre_lut(x), mod), 0, 1)))
        res[met] = fila
    return nombre, n, res


def tabla(resultados):
    for nombre, n, res in sorted(resultados):
        for met, fila in res.items():
            s = f"{nombre:11s} {n:2d}³ {met:6s} rec/borde {fila['rec']:3d} | "
            for mod in ("tri", "tetra"):
                u, f1, ne, pi = (fila[(mod, k)] for k in ("uniforme", "foto1", "neutros", "piel"))
                s += f"[{mod}] unif {u[0]:.2f}/{u[1]:.2f}/{u[2]:.1f} foto {f1[0]:.2f}/{f1[1]:.2f} neutr {ne[0]:.2f} piel {pi[0]:.2f}  "
            print(s)


def nodos_directo(f) -> np.ndarray:
    """Muestreo directo de los 405 nodos en flotante (el algoritmo de lutsd.c ANTES de G90), redondeado a s7."""
    j, a, b = np.meshgrid(range(5), range(9), range(9), indexing="ij")
    nodo = np.stack([j.ravel() / 4, (a.ravel() - 4) / 8, (b.ravel() - 4) / 8], 1)
    rgb = np.clip(C.ycc2rgb(nodo), 0, 1)
    u = C.rgb2ycc(rgb)
    return np.clip(np.round((C.rgb2ycc(f(rgb)) - u) / U), LO, HI).astype(np.int8)


def tabla_de_blob(blob: bytes) -> np.ndarray:
    """405×3 s7 de los 1064 B de 21 bits por nodo (formato del blob de g89)."""
    bits = int.from_bytes(blob, "little")
    sg = lambda v: v - 128 if v & 64 else v
    return np.array([[sg(bits >> (21 * i + s) & 127) for s in (14, 7, 0)] for i in range(405)], np.int8)


def camara(args):
    """Camino de la cámara (lutsd.c): muestreo directo (antes) vs con corrección de 2.ª diferencia (G90, `referencia` Python = ARM byte a byte)."""
    nombre, n = args
    import tempfile

    import lut_sd_userland as SD
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.cube"
        C.escribe_cube(p, PRUEBA[nombre], n, nombre)
        texto = p.read_text()
        tab, lo, hi = C.lee_cube(p)
    f = lambda x: C.aplica_cube(tab, lo, hi, x)
    ch = C.Cadena()
    ev = {k: v for k, v in conjuntos_eval().items() if k in ("uniforme", "foto1", "neutros", "piel")}
    out = {}
    for nom, q in (("directo", nodos_directo(f)), ("G90", tabla_de_blob(SD.referencia(texto)))):
        out[nom] = {(m, k): stats(C.de2000(f(x), np.clip(aplica(q, ch.pre_lut(x), m), 0, 1))) for m in ("tri", "tetra") for k, x in ev.items()}
    return nombre, n, out


def atribuye(args):
    """Descomposición del error de una LUT en etapas (g90 §B): cada fila añade una limitación del hardware. ΔE2000 sobre muestras uniformes (semilla 7)."""
    nombre, n = args
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.cube"
        C.escribe_cube(p, PRUEBA[nombre], n, nombre)
        tab, lo, hi = C.lee_cube(p)
    f = lambda x: C.aplica_cube(tab, lo, hi, x)
    ch = C.Cadena()
    xt, w = muestras()
    c, y = ch.pre_lut(xt), f(xt)
    xe = np.random.default_rng(7).random((20000, 3))
    ce, ye = ch.pre_lut(xe), f(xe)
    u = C.rgb2ycc(c)
    raw = C.ajusta_lut3d(u, C.rgb2ycc(y) - u)                       # unidades normalizadas
    def ev(d_int, modelo="tri"):
        return stats(C.de2000(ye, np.clip(aplica(d_int, ce, modelo), 0, 1)))
    filas = [("cadena de fábrica (LUT=0)", ev(np.zeros((405, 3))))]
    filas.append(("(a) LSQ-RGB flotante, sin cuantizar ni recortar", ev(raw / U)))
    filas.append(("(b) + cuantización a s7 (sin recorte)", ev(np.round(raw / U))))
    q_old, rec = C.a_unidades(raw)
    filas.append((f"(c) + recorte ±64 ({rec} nodos) = método anterior", ev(q_old)))
    q_gn = ajusta_de(c, y, w, "tri", entero=False)
    filas.append(("(d) ΔE-GN con caja ±64 y redondeo (modelo tri)", ev(q_gn)))
    q_new = ajusta_de(c, y, w, "tri")
    filas.append(("(e) + refinamiento entero en ΔE2000 = método nuevo", ev(q_new)))
    filas.append(("(f) el mismo método nuevo evaluado con interpolación tetraédrica", ev(q_new, "tetra")))
    q_t = ajusta_de(c, y, w, "tetra")
    filas.append(("(g) tabla ajustada tetraédrica, evaluada tetraédrica", ev(q_t, "tetra")))
    filas.append(("(h) tabla ajustada tetraédrica, evaluada trilineal", ev(q_t, "tri")))
    return nombre, n, filas


if __name__ == "__main__":
    from multiprocessing import Pool
    if "--camara" in sys.argv:
        with Pool(8) as p:
            for nombre, n, out in sorted(p.map(camara, [(k, n) for k in PRUEBA for n in (17, 32)])):
                for nom, r in out.items():
                    print(f"{nombre:11s} {n:2d}³ {nom:8s} " + " | ".join(f"[{m}] unif {r[(m, 'uniforme')][0]:.2f}/{r[(m, 'uniforme')][1]:.2f} foto {r[(m, 'foto1')][0]:.2f} neutr {r[(m, 'neutros')][0]:.2f} piel {r[(m, 'piel')][0]:.2f}" for m in ("tri", "tetra")))
        sys.exit()
    if "--atribucion" in sys.argv:
        with Pool(4) as p:
            for nombre, n, filas in p.map(atribuye, [(k, 32) for k in PRUEBA]):
                print(f"== {nombre} {n}³")
                for t, (m, p95, mx) in filas:
                    print(f"  {t:62s} medio {m:.3f} p95 {p95:.2f} máx {mx:.1f}")
        sys.exit()
    metodos = ["viejo", "tri", "ambos"] if "--rapido" not in sys.argv else ["viejo", "tri"]
    trabajos = [(k, n, metodos) for k in PRUEBA for n in (17, 32)]
    with Pool(min(8, len(trabajos))) as p:
        tabla(p.map(caso, trabajos))
