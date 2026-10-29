# E25-25 — Validación de cuevas, carga del firmware y canal de modalidad

28-10-2026. Continuación de [E25-24b](e25-24b-implementacion-selector.md). Solo análisis de
bytes, emulación y pruebas offline. **No se conectó la cámara, no se escribió RAM/NVRAM ni
firmware, no se generó un paquete instalable.**

Base: `e71df5b3`. Firmware A6000 3.21: `av-cam.bin` SHA-256 `b60c845c…e56bb9`,
`darwin_core.bin` SHA-256 `5f2be06d…0bf4`. Comparación: `av-cam.bin` de la A7S 3.20
(`b857d338…`, 11 455 416 B).

Etiquetas: **V** = bytes/emulación del código real · **I** = inferencia · **N** = no
verificado · **B** = bloqueado por una dependencia no demostrable.

---

## 0. Resumen y corrección de E25-24

1. **La cueva de E25-24 no era segura (V).** El «relleno» `0x435418e4–0x43541aff` no está
   libre: contiene un objeto de 512 B cuyo inicio `0x43541900` tiene una entrada en la GOT
   (`0x44020f00 → 0x43541900`). La misma entrada existe en la A7S. La cueva del selector
   (`0x43541a80`) quedaba **dentro** de ese objeto.
2. **Se reubicaron las cuevas (V).** Nueva zona: `0x4354141c–0x435418d8`, cero en A6000 y
   A7S, sin punteros literales, después del `memcpy` de la tabla API del cargador
   (`0x435410d8–0x4354141c`) y antes del puntero final de la cabecera (`0x435418d8`).
   - selector E25-24: `0x43541800` (20 B).
   - C3-B E25-26: `0x43541840` (58 B).
3. **La carga es compatible con las cuevas, con un límite (V/I).** `liro.ko` (`tsk_entry`)
   lee `av-cam.bin` completo (`filp_open`/`vfs_read`), comprueba `LIRO`/versión 4 y hace
   `memcpy(blob+0x14+0x24, tabla_API, 0x344)`; el stub ARM de `0x0` se ejecuta desde el mismo
   buffer. Por tanto cabecera y texto comparten imagen y permisos de ejecución. **No** se ha
   demostrado que el cargador no use los campos reservados `0x141c–0x18d8`; no hay ninguna
   referencia estática ni tabla conocida que los alcance.
4. **Canal de modalidad (V/E).** `cap+0x41c` se copia del ajuste global `+0x210` al construir
   la captura; el paquete `0x0c` (22 B) lleva el byte en `+0x0e`; Darwin lo copia a `S+0x3e`
   (`0x20003716`). No hay lector estático de `S+0x3e` (barrido de desplazamiento `0x3e` y de
   literales a `0x200036d8`/`0x20003716`). El cambio de menú durante una captura no altera el
   paquete ya emitido.
5. **Darwin (V).** Las entradas 70–73 y 76 de la tabla de vectores (`0x4318`/`0x4330`) son
   cero; 74/75/77 sí se usan. No hay literales ni ramas a `0x4318–0x4326` ni a
   `0x4330–0x4334`. La cueva solo se alcanza por `bl`; si un IRQ usara esas entradas, el
   original ya provocaría un fault.

---

## 1. Región antigua: por qué no era relleno

| Comprobación | Resultado | Estado |
|---|---|---|
| `0x435418e4–0x43541aff` todo cero en A6000 | sí | V |
| Misma zona cero en A7S | sí | V |
| Palabras alineadas que apuntan a la zona | `0x43541900` (GOT `0x44020f00`), `0x43541a64` (falso positivo: mitad de instrucción en `0x43adeee4`) | V |
| `0x43541900` en la GOT de la A7S | sí (`0xAE5608` de archivo) | V |
| Tamaño del objeto | 512 B (0x900–0xB00) por alineación y por el inicio de texto en `0xB00`; **no demostrado** por una tabla de símbolos | I |
| ¿La cueva de E25-24 cae dentro? | sí: `0x43541a80` ∈ `0x43541900–0x43541b00` | V |

**Conclusión:** escribir código en `0x43541900–0x43541aff` puede corromper un objeto global
compartido con la A7S. No se mantiene esa ubicación.

## 2. Región nueva: `0x4354141c–0x435418d8`

| Comprobación | Resultado | Estado |
|---|---|---|
| Cero en A6000 y A7S | sí (1212 B) | V |
| Punteros literales (incluidos GOT) | 0 | V |
| Destinos de rama `bl`/`b.w` | 1 falso positivo: `0x4361d67c → 0x4354167e` (bytes de datos); fuera de las cuevas | V/I |
| `memcpy` del cargador | `0x435410d8–0x4354141c` (0x344 B); no alcanza la zona | V |
| Puntero final de cabecera | `0x435418d8–0x435418e4`; la zona termina antes | V |
| Cuevas | selector `0x43541800` (20 B), C3-B `0x43541840` (58 B) | V |

**Límite:** no existe una tabla de símbolos/segmentos que demuestre que el cargador ignora
los campos reservados. La evidencia es estructural (cero, sin referencias, después del
`memcpy` conocido), no una garantía del cargador. Se clasifica **apta para offline**; la
instalación física exige la comprobación de arranque de E25-27.

## 3. Carga, checksums y recuperación (E24-04)

| Pregunta | Respuesta | Base |
|---|---|---|
| ¿La imagen se lee completa? | **SÍ** (`vfs_read` en `liro.ko`), con `memcpy` posterior en `blob+0x38` | V (S49) |
| ¿Hay tabla de segmentos en el ORIL? | **NO demostrada**; el blob es plano, base `0x43541000` | V/I |
| ¿La cabecera y el texto comparten permisos? | **SÍ** (mismo buffer; el stub ARM de `0x0` se ejecuta) | I fuerte |
| ¿Checksum dentro de la imagen? | **NO demostrado**; el actualizador usa CRC-32 del archivo (`us_crc32sum.sh`) | V (E24-03) |
| ¿Firma criptográfica? | **NO demostrada** | N |
| ¿Recuperación tras un Darwin no iniciable? | **NO demostrada** (E24-04 sigue vigente) | B |

El CRC-32 del paquete se puede recalcular offline, pero **eso no autoriza instalar**: la
recuperación independiente de Darwin no está demostrada y el cargador podría rechazar o
usar los campos reservados. Los parches siguen siendo artefactos de desarrollo.

## 4. Canal de modalidad

```
ajuste +0x210 (0/1)
  └─ 0x43845f34  str.w r2,[r4,#0x41c]      (copia al construir cap; por captura)
       ├─ 0x43841070/0x4384133e  cave selector -> pkt[0x0e]  (22 B, mensaje 0x0c)
       │    └─ Darwin 0x17f8c: pkt[0x0e] -> S+0x3e (0x20003716)
       └─ C3-B 0x438c82fe: lee cap+0x41c (misma copia congelada)
```

| Hecho | Evidencia | Estado |
|---|---|---|
| `cap+0x41c = [global+0x210]` | `0x43845f30/0x43845f34` | V |
| El paquete `0x0c` mide 22 B y el byte está en `+0x0e` | constructor `0x43841070`, parser `0x17f8c` (sp+4+k) | V |
| Darwin copia a `S+0x3e` | `0x17ff8/0x17ffc` | V |
| Lectores estáticos de `S+0x3e` | 0 | V (barrido) |
| Cambio de menú durante la captura | no afecta al paquete emitido; `cap+0x41c` es copia | V (modelo) |
| Fallo seguro | paquete ausente/inválido → EFCS | V (modelo) |

La modalidad se congela dos veces (copia de `cap` y paquete). C3-B usa la copia de `cap`, no
el paquete, para no depender de la vida útil del buffer de envío.

## 5. Darwin: cueva y vectores

| Comprobación | Resultado | Estado |
|---|---|---|
| Tabla en `0x4200`; SP `0x20002a00`, reset `0x45c9` | sí | V |
| Entradas 70, 71, 72, 73, 76 | `0`, `0`, `0`, `0`, `0` | V |
| Entradas 74, 75, 77 | `0x4539`, `0x460d`, `0x4563` | V |
| Literales/ramas a `0x4318–0x4326` o `0x4330–0x4334` | 0 | V |
| Cueva 14 B + literal 4 B | cabe en vectores no usados | V |
| VTOR | no se encontró escritura a `0xE000ED08`; si el core usa su tabla, las entradas son las de `0x4200` | N |

La cueva Darwin no toca `0x20c74`, `0x1fe66`, `InitCom`, `Upd`, reset, watchdog ni GPIO.
Restaurar los dos `bl`, la cueva y el literal devuelve el binario original (SHA-256
`5f2be06d…`).

## 6. Veredictos

| | Pregunta | Respuesta | Base |
|---|---|---|---|
| A | ¿La cueva antigua era segura? | **NO** | V |
| B | ¿La nueva zona es estructuralmente apta? | **SÍ para offline** | V/I |
| C | ¿Se demostró que el cargador ignora la zona? | **NO** | B |
| D | ¿La imagen se carga completa y se ejecuta? | **SÍ** (loader conocido) | V/I |
| E | ¿Hay checksum/firma en la imagen? | **NO demostrado** | N |
| F | ¿La modalidad se congela por captura? | **SÍ** | V |
| G | ¿Hay lectores de `S+0x3e`? | **NINGUNO estático** | V (no prueba ausencia) |
| H | ¿La cueva Darwin interfiere con vectores usados? | **NO** (70–73/76 cero) | V |
| I | ¿Se puede instalar? | **NO**: recuperación no demostrada | B |

## 7. Entregables y reproducción

- `scripts/e25_25/references.py`: barrido de ramas y punteros.
- `scripts/e25_25/channel.py`: modelo del paquete y de la copia Darwin.
- `scripts/e25_25/build_evidence.py` → `analysis/e25-25/evidence.json`.
- `tests/test_e25_25_caves.py`, `tests/test_e25_25_channel.py`.
- Reubicación en `scripts/e25_24/patch_bionz.py` (`CAVE = 0x43541800`) y
  `scripts/e25_26/patch_c3b.py` (`CAVE = 0x43541840`).

```bash
python3 scripts/e25_25/build_evidence.py
python3 scripts/e25_26/build_evidence.py
python3 -m pytest -q tests/test_e25_25_caves.py tests/test_e25_25_channel.py tests/test_e25_26_c3b.py
```

## 8. Límites

No demostrado offline: que el cargador ignore los campos reservados; que el CRC-32 del
paquete baste; que un fallo de arranque sea recuperable; que el sensor aplique la exposición;
que EFCS mueva la segunda cortina con el Darwin parcheado. Nada de esto se declara.
