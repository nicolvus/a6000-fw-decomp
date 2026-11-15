# G40 — G38-D: ¿de dónde sale el tope 1/4000 del dial? UI descartada, tope fuera de la librería de la UI (15-11-2026, ESTÁTICO, sin parche)

Continúa [G38 §3](g38-obturacion-1-8000.md). Resultado: **PARCIAL**. Se descarta la capa de la UI con bytes y se acota el tope a `av-cam` (AE) o al modelo `ModelCamera` de `libObj`; el generador concreto sigue sin localizar, así que **no hay parche de lista ni prueba en el arnés**. Sin CFW, sin cámara.

## 1. (iii) La UI no tiene lista ni tope: descartada (bytes de `wrapperShutterSpeed.so` 3.21)

| Función | Dirección | Qué hace (desensamblado Capstone) |
|---|---|---|
| `getShutterSpeed` | `+0x18c4` | `getModelInfo(vista, 0x35)`, lee las claves `0x27f` y `0x1b8…0x1bd` y copia seis enteros a los punteros de salida (`+0x1990…+0x19c0`). Sin comparaciones, sin tablas: **no filtra ni recorta** el máximo |
| `setShutterSpeed` | `+0x1a64` | `ViewBase::requestModelExecute("@M00B", 0x2c, ParamList{0x1a8: PrmNumber(±1)})` (`0x1a84…0x1acc`; el argumento enum 0 → −1, 1 → +1). Es un **paso relativo**: la UI no calcula la velocidad nueva |
| `getTvValue` | `+0x1b50` | `(log(a) − log(b))/k` con `vdiv.f32`, conversión a índice Tv; sin límites |
| `getStep` | `+0x1aec` | clave `0x286` del info `0x51`: 3 → 0, 2 → 1, otro → 2 (resolución 1/3, 1/2, 1 EV) |

Otras hipótesis de texto: no existe ninguna cadena `4000` ni lista de velocidades en `analysis/camera-extract` (la UI construye «1/n» desde numerador y denominador). Conclusión: el dial «termina» donde termine el modelo; un parche en la librería de la UI (`wrapper*Shutter*.so`, `.uxc`) no puede dar 1/8000.

## 2. Camino real del paso y dónde se decide el tope

UI (paso ±1, evento `0x2c` de `@M00B` ≡ `model/CAMERA`, [G20](g20-menu-pp-construccion.md)) → `ModelCamera` (`libObj`) → `ObjCamera`/`av-cam` (AE). La velocidad vigente y su rango (`SHUT_SPEED_NUMER/DENOM`, `MIN_`, `MAX_`, `0x2014` → `0x8531`, [g22-avcam-puente §5.18](g22-avcam-puente.md)) los publica `av-cam`; `libObj` los guarda (`0x4d1984`, `+0x1fc…0x218`) y los sirve. Cualquier parche de 1/8000 tiene que cambiar el MIN (`1/4000`) que sale de `av-cam` o la guarda del paso en `ModelCamera`; no es una tabla de la UI.

**Artefacto del arnés (importante para la prueba):** `scripts/gui/avcam/ae.py:107` (`msg_velocidad(..., (1, 4000), (30, 1))`) y `VELOCIDADES` (empieza en 1/4000) **fijan el 1/4000 con nuestro propio código**, porque en el arnés `av-cam` no emite el `0x2014` (la AE no corre en la LIRO VM; ninguno de los 20 `avcam.jsonl` revisados en `analysis/gui/g22/harness/live/` contiene el id `0x2014`). El tope que se vería en el arnés es, por tanto, el de ese atajo y no demuestra nada sobre la cámara. Además el arnés abre la vista de grabación en P (modo S no se alcanza: el dial de modos manda el evento pero `ObjCamera` no cambia el modo, [g22-t7-mapa-teclas §5](g22-t7-mapa-teclas.md)) y `getShutterSpeed` no llega a ejecutarse ([g22-avcam-puente §5.31](g22-avcam-puente.md)), de modo que **no se puede girar el dial en S ni capturar 1/4000 → 1/8000**.

## 3. (ii) `av-cam`: lo que se barrió y lo que no apareció

Imagen `av-cam` 3.21 (base `0x43541000`) comparada con A6300 (también 1/4000 mecánico) y A7S (1/8000):

* **Dominio Tv ya llega a 1/8000.** Escala Tv de 1/256 EV con sesgo 16 EV (`Tv = 256·(16 + log2(1/t))`: 1/4000 = `0x1bf7`, 1/8000 = `0x1cf7`). Hay una escalera de 1 EV en `0x43befa0e` (`0x14e8, 0x15e8 … 0x1bf8, 0x1cf8`) y una tabla fina `…0x1bf7, 0x1bf8, 0x1bfa…` en `0x43bf7d30` (y `0x1cf7` en `0x43bf7ec6`): son calibración de tiempos (T052/T046), no un tope; el rango Tv del firmware incluye 1/8000.
* **Inmediatos.** Ningún `movw`/literal `0x1bf7/0x1cf7` (ni sus variantes ×¼, ×1/16, sin sesgo `0xbf7/0xcf7`) es un límite de AE: los pocos aciertos son color (`0x439e92be`), números de línea de `assert` (`0x4364af2a`), desplazamientos de GOT (`0x1bf8`, `0x1cf8` en `0x43577516/0x4357752e`, `0x436813fe`) o el `0x2013/0x2014` de tipo 1 de `0x43887a4a/0x43887aa0` (nivel de exposición, no velocidad; mensaje de 2 palabras por `0x43901a8c`).
* **Diferencia estructural A6000/A6300/A7S.** Se partieron las tres imágenes en funciones (35 255 / 37 207 / 37 899), se enmascararon los inmediatos y se emparejaron las firmas idénticas (4 717 con algún inmediato distinto). Solo 11 son «A6000 = A6300 ≠ A7S» y **todas son desplazamientos de estructura** (`0x2c/0x34`, `0x98/0x9c`, `0xa0/0xa4`, `0x1bc/0x1c4`…), ninguna es un límite. Por tanto el tope no es una constante en código idéntico: o es un dato (tabla/parámetro del modelo), o está en código cuya forma difiere entre A6000 y A7S.
* **Tablas de denominadores** (`0x43bc4904` 36 entradas hasta 204 800, `0x43bc5fa0`, `0x43bc6068`): idénticas en las tres cámaras (G38 §3); no hay ningún acceso resoluble por literal ni por GOT sin relocaciones (`xrefs` de REA vacío; búsqueda `movw/movt+add pc` y `ldr literal+add pc`: 0 aciertos).
* **Emisor del `0x2014` tipo 6.** `0x435eb650` (despachador; caso `0x70` ↔ `0x2014` en `0x435ebe0a`, carga por `0x43a64d60`) solo lo invoca el thunk `0x43a64f12`, desde `0x43a4c2ac`; el módulo que rellena la estructura (num/den/min/max) se invoca por vtable y no se halló con barrido de escrituras (`strh +8, str +0xc, strh +0x10, str +0x14, strh +0x18, str +0x1c` sobre el mismo registro: 4 aciertos, ninguno es la AE).

## 4. Mecánico/EFCS

Sin cambio respecto a [G38 §3](g38-obturacion-1-8000.md): Darwin no recorta T, y la limitación a 1/4000 en mecánico/EFCS sería una guarda separada que hoy no se puede ni localizar ni validar sin cámara (rendija 0,57 mm, ±33 µs frente a ±190 µs medidos). Cualquier parche futuro de la lista debería, si es posible, conservar el MIN de 1/4000 cuando `ShutMode ≠ 0` (Silent); eso exige primero hallar quién escribe el MIN.

## 5. Pendientes que salen de aquí

* **G38-E** — Localizar la guarda del paso `0x2c` en `ModelCamera` y el constructor del MIN/MAX del `0x2014` en `av-cam`. Plan: (a) `libObj` 3.21: la entrada de `ModelCamera` para el evento `0x2c` (vtable `0xff0894`; buscar el lector de `+0x1fc…+0x218` que compare con MIN/MAX); (b) `av-cam`: llamadores de la vtable de `0x43a64f12` con id `0x2014` y la rutina que escribe MIN (`1/4000`) — buscar el código que emite `0x8531` desde la AE usando la sesión REA con `trace_native_values`. Criterio de cierre: dirección, bytes y parche; test que valide los bytes originales (modelo `scripts/gui/quality_exfine_patch.py`).
* **G38-F** (arnés, **no tocado**: es de otra sesión) — Para ver el dial en el arnés hace falta (1) que `ObjCamera` acepte el cambio de modo a S y (2) que `getShutterSpeed` se ejecute; después sustituir `VELOCIDADES`/MIN de `ae.py` por el rango real. Mientras tanto la «captura 1/4000 → 1/8000» no es posible.
