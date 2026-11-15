#!/usr/bin/env python3
"""G67: tablas de gamma HLG1/HLG2/HLG3 con el formato de las curvas de vídeo del núcleo `av-cam.bin` (0x101a B). NO instala nada.

Formato (VERIFICADO con la curva S-Log3 de la A6300 y las de la A7S): 2048 u16 (entrada = luz de escena lineal de 11 bits, salida = código de 10 bits)
+ cola de 26 B donde `+0x1012` = 4 (vídeo) y `+0x1014` = número de gamma. La curva S-Log3 de la A6300 es exactamente `S-Log3(i·0,00271)` en 10 bits
(18 % de gris en i ≈ 66; error ≤ 3,4 códigos fuera de las ~30 primeras entradas, donde baja por debajo del negro nominal): se usa la misma escala de entrada.

HLG = OETF de ARIB STD-B67 / BT.2100 con E = 0,265·x (blanco difuso 100 % = 0,265; gris 18 % ≈ 38 % de señal), código = 64 + 876·y (rango legal).
Nivel máximo de Sony (HLG1 87 %, HLG2 95 %, HLG3 100 %, dado por el encargo, sin fuente Sony verificable aquí): a partir de y = 0,80 la señal sigue una recta
hasta (E = 1, y = nivel); es una rodilla lineal APROXIMADA, no la de Sony. Uso: pp_hlg_curves.py [n] (imprime resumen)."""
import math
import struct
import sys

A_, B_, C_ = 0.17883277, 0.28466892, 0.55991073
K = 0.00271          # luz de escena (x, 1 = blanco 100 %) por entrada de la tabla
BLANCO = 0.265       # E de HLG para x = 1
RODILLA = 0.80
NIVEL = {1: 0.87, 2: 0.95, 3: 1.00}
N, CURVE = 2048, 0x101A


def oetf(e: float) -> float:
    e = min(max(e, 0.0), 1.0)
    return math.sqrt(3 * e) if e <= 1 / 12 else A_ * math.log(12 * e - B_) + C_


def tabla(n: int) -> list[int]:
    nivel = NIVEL[n]
    out = []
    for i in range(N):
        y = oetf(BLANCO * i * K)
        if y > RODILLA:
            y = RODILLA + (y - RODILLA) * (nivel - RODILLA) / (1 - RODILLA)
        out.append(round(64 + 876 * y))
    return out


def bloque(n: int, cola: bytes, gamma: int) -> bytes:
    """Curva completa: tabla + cola de una curva de vídeo existente (`cola` = sus 26 B finales) con `+0x1014` = `gamma`."""
    c = bytearray(struct.pack("<2048H", *tabla(n)) + cola)
    assert len(c) == CURVE and cola[0x12] == 4, "la cola debe venir de una curva de vídeo con +0x1012 = 4"
    c[0x1014] = gamma
    return bytes(c)


if __name__ == "__main__":
    for n in ([int(sys.argv[1])] if len(sys.argv) > 1 else (1, 2, 3)):
        t = tabla(n)
        print(f"HLG{n}: 0→{t[0]} 66(18 %)→{t[66]} 242(100 %)→{t[242]} máx→{t[-1]}")
