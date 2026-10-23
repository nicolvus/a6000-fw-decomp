# S328 — La segunda matriz no tiene productor estático y su bucle no ejecuta

Trigésimo octava sesión del carril B. Cierra el TODO de S323 (segunda matriz de la
puerta `sub`): ¿quién llena el slot `0x44026088` (A7S) / `0x44026694` (A6000) y qué hace
ese bucle con el blob tal cual?

**Resultado:** nadie, en estático. El slot contiene un puntero a una tabla **a cero**
(`0x43e8de00` A7S, `0x43e80160` A6000); el offset que resuelve el slot (`0x1b48` / `0x77b0`)
aparece en **un único sitio** por firmware — el propio bucle del accesor — y el valor del
slot solo aparece como **dato** en el slot. Como la primera palabra de la tabla es el
terminador del bucle, **con el blob tal cual el segundo bucle no ejecuta y no escribe nada**.

---

## 1. Slots y tablas (VERIFICADO)

| | A7S fw3.20 | A6000 fw3.21 |
|---|---|---|
| Base de slots | `0x44024540` | `0x4401eee4` |
| Offset | `0x1b48` | `0x77b0` |
| Slot | `0x44026088` | `0x44026694` |
| Contenido del slot | `0x43e8de00` | `0x43e80160` |
| Bytes no nulos en los primeros 64 B | **0** | **0** |
| Primera palabra (= cabecera/terminador) | `0x00000000` | `0x00000000` |

## 2. Usuarios (VERIFICADO)

* Sitios con el literal del offset: **1** por firmware → `0x436f394e` (A7S, dentro del
  accesor `0x436f3928`) y `0x436d65a0` (A6000, dentro de `0x436d6570`). Son exactamente los
  segundos bucles descritos en S321.
* El valor del slot (`0x43e8de00` / `0x43e80160`) tiene **una sola** referencia absoluta:
  el propio slot. No hay `bl`, ni tabla de punteros, ni otro literal que lo use.
* No hay ningún store estático al slot ni a la tabla (0 bytes no nulos en la región).

## 3. Consecuencia con el blob tal cual (VERIFICADO)

El bucle del accesor es:

```
ldr r2,[r3,r2]      ; tabla desde el slot
bucle:
  ldr r4,[r2]       ; cabecera = destino
  cmp r4,#0
  bne bucle         ; si 0 -> fin
```

Con la tabla a cero, `ldr r4,[r2]` da 0 en la primera iteración → **el bucle no ejecuta
ninguna escritura**. Por tanto, para `sub != 0` (p. ej. el modo `0x4f`) la segunda matriz
**no aporta nada** en estático.

Su activación exigiría un productor en **runtime**: otro módulo, DMA o una inicialización
no visible en `av-cam`. Eso queda **NO_VERIFICADO**.

## 4. Impacto en la pregunta del silent shutter

* **S51 no cambia (A=NO, B=NO, C=NO).**
* Se descarta, en estático, la idea de que la segunda matriz sea el mecanismo que distingue
  `0x4f` de `0x4e`: la puerta existe (`sub != 0`, S324) pero la tabla está vacía y termina
  en su primera palabra. La única diferencia observable entre ambos códigos sigue siendo la
  de la matriz de 16 columnas (S325: columnas 12 vs 13, 4 registros) y la de T2
  (S326: `+0x18` 2 vs 3), ambas sin lectura de mecanismo.

## 5. Límites

* Solo lectura estática; sin runtime, cámara ni flasheo.
* La tabla **podría** llenarse en runtime desde otro módulo, por DMA o por una
  inicialización no visible en `av-cam`: no se descarta, solo no hay productor estático.
* No se interpreta el contenido futuro de la segunda matriz ni su efecto sobre los modos con
  `sub != 0`.
* S51 (A/B/C) no cambia.

## 6. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s328_second_matrix/build_second_matrix.py
.venv/bin/python analysis/s328_second_matrix/verify_second_matrix.py   # 28 comprobaciones
.venv/bin/python -m unittest tests.test_s328_second_matrix              # 6 tests
.venv/bin/ruff check analysis/s328_second_matrix tests/test_s328_second_matrix.py
.venv/bin/mypy --ignore-missing-imports analysis/s328_second_matrix
```

SHA-256 de los blobs:

* A7S fw3.20: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 fw3.21: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

Evidencia: `analysis/s328_second_matrix/second_matrix.json`.
