"""G94 — misma LUT en vista en vivo (MON/MOV) y en la foto (CAP/SA): tabla por modo precalculada en el PC.

`Create3DLUT` (`0x437a1d7c`) aplica «ConvSD» (`cfg+0xd9`, `FUN_437a1d14`) solo en MOV/MON (nunca con `cfg+2 = 2`, SA/CAP):
convierte la salida de la LUT de BT.709 a BT.601 (matriz de croma 709→601, medida en Unicorn sobre el generador real).
En esos modos la entrada de la LUT es YCbCr 709 y la salida se lee como 601 (INFERIDO de la conversión).
Entregar la misma tabla a todos los modos (gancho G71) deja la vista en vivo con el desajuste 709/601;
`tabla_convsd(q)` da la tabla para ConvSD = 1, compuesta en el PC, y la cámara solo elige puntero por `cfg+0xd9`.
"""
from __future__ import annotations

import cube_a6000 as C
import lut3d_emu as E
import numpy as np

K = {"601": (0.299, 0.114), "709": (0.2126, 0.0722)}
U = np.array([C.UY, C.UC, C.UC])
NODOS = np.array([(C.EJE_Y[j], C.EJE_C[a], C.EJE_C[b]) for j in range(5) for a in range(9) for b in range(9)])


def enc(rgb: np.ndarray, k: str) -> np.ndarray:
    kr, kb = K[k]
    y = rgb @ np.array([kr, 1 - kr - kb, kb])
    return np.stack([y, (rgb[..., 2] - y) / (2 * (1 - kb)), (rgb[..., 0] - y) / (2 * (1 - kr))], -1)


def dec(t: np.ndarray, k: str) -> np.ndarray:
    kr, kb = K[k]
    y, cb, cr = t[..., 0], t[..., 1], t[..., 2]
    r, b = y + 2 * (1 - kr) * cr, y + 2 * (1 - kb) * cb
    return np.stack([r, (y - kr * r - kb * b) / (1 - kr - kb), b], -1)


def aplica(q: np.ndarray, u: np.ndarray) -> np.ndarray:
    """LUT 5×9×9 (s7 [405,3], trilineal) sobre YCbCr normalizado."""
    idx, w = C.pesos(u)
    return u + np.einsum("mk,mkc->mc", w, np.asarray(q, float)[idx] * U)


def convsd_fabrica(q: np.ndarray) -> np.ndarray:
    """Lo que el generador real deja con ConvSD = 1 partiendo de la referencia `q` (Unicorn)."""
    ref = b"".join(q[:, k].astype(np.int8).tobytes() for k in range(3))
    return np.array(E.decodificar(E.generar(ref, pkt={0x23: 8}, cfg={0xD9: 1}), E.perm(E.BIN.read_bytes())))


def tabla_convsd(q: np.ndarray, x: np.ndarray | None = None) -> tuple[np.ndarray, int]:
    """Tabla para MOV/MON con ConvSD (entrada 709, salida leída como 601) ajustada por mínimos cuadrados a la salida de CAP con `q`.
    (Muestrear `q` en el nodo convertido duplica el error en LUT con curva: película 0,88 frente a 0,43.) → (s7, recortados)."""
    x = C.rejilla(21) if x is None else x
    u = enc(x, "709")
    return C.a_unidades(C.ajusta_lut3d(u, aplica(q, enc(x, "601")) - u))           # objetivo = salida 601 de CAP


def fidelidad(q: np.ndarray, x: np.ndarray) -> dict[str, np.ndarray]:
    """ΔE2000 por color entre la foto (CAP, 601) y la vista en vivo con ConvSD según qué tabla recibe."""
    foto = np.clip(dec(aplica(q, enc(x, "601")), "601"), 0, 1)
    vivo = lambda t: np.clip(dec(aplica(t, enc(x, "709")), "601"), 0, 1)
    return {"misma_tabla": C.de2000(foto, vivo(q)), "convsd_fabrica": C.de2000(foto, vivo(convsd_fabrica(q))),
            "precalculada": C.de2000(foto, vivo(tabla_convsd(q)[0]))}


if __name__ == "__main__":
    x = C.rejilla(21)
    for nom in ("identidad", "teal_orange", "pelicula"):
        q = C.descompone(C.SINT[nom], usa_M=False, usa_T=False, usa_L=True, metodo="mc").q
        print(nom, {k: f"{v.mean():.2f}/{np.percentile(v, 95):.2f}/{v.max():.1f}" for k, v in fidelidad(q, x).items()})
