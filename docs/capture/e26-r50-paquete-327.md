# E26-R50 — Paquete 3.27 (contenido del 3.25c) para instalar en la cámara recuperada

Fecha: 03-11-2026. Continúa [R49](e26-r49-cierre-recuperacion-326.md) (cámara en 3.26) y [R45](e26-r45-firmware-325c-experimental.md) (3.25c). **Solo offline**: construido y verificado, **no instalado**.

## 1. Por qué 3.27

La cámara está en 3.26 y el actualizador solo acepta una versión mayor ([R37](e26-r37-cierre-estatico-tras-r36.md)). El 3.25c (cabecera 3.25) ya no se aceptaría; se reempaqueta con cabecera **3.27** y exactamente el mismo contenido.

## 2. Resultado (DATOS)

| Elemento | Valor |
|---|---|
| Orden | `PYTHONPATH=scripts .venv/bin/python -m e25_27.build --out analysis/e25-27/artifacts-327 --package --version 3.27` |
| `.dat` (no versionado) | `analysis/e25-27/artifacts-327/package-3.27/firmware_packed.dat`, SHA-256 `0a5145a7fad1fdd268d1ca0c298d99cd15284ac68457781d9099ba46d8856f28` |
| `.fdat` | `eadaa91afbb5a0ef84ea51c9caba6ede758fc364b2bc4575c7af175d2f940516` |
| Contenido | tar, `nflasha3`, BIONZ, Darwin y sumas **idénticos byte a byte** a `artifacts-325c` (tar `affacce5…`); solo cambia la versión de cabecera |
| Verificación | `verify_325c.py --dat … --out analysis/e25-27/verify-327.json`: 30/30, `todo_ok: true` (emulación Loader3+ARM7: 0 fallos) |

Cambio de código: `verify_325c.py` acepta cabecera 3.25 o 3.27 y tiene `--out` (para no pisar `verify-325c.json`).

## 3. Límites

- **NO VERIFICADO en hardware**: el 3.25c nunca arrancó; la cámara ya recuperada vuelve a correr el riesgo de R36 si el modelo del LDEC falla.
- Si falla el arranque, la recuperación es la de R49 (SWD, sonda aún soldada) y un paquete **3.28** mayor que el 3.27 (el 3.26 ya no valdría): construirlo antes de instalar.
- Instalar requiere autorización expresa del usuario. Primer intento de R49 cortó con `0x1063` (Darwin NG) sin explicar.
