# S314 — Procedencia real del selector silent y tabla `0x43fee3f8` (carril B)

**Resultado en una línea:** la premisa «objeto/vtable de `r0` en `0x43549084`, slot `0x64`»
mezcla tres cosas distintas. En `0x43549084` no se carga `r0` sino **`r1`** (campo `+0x21c`
del objeto `[ctx+8]`); el thunk del **slot `0x64`** es `0x43ad96f8` y **no** se llama en
`0x435490c4` (esa llamada va a `0x43ad9704 → 0x43ad9ada`, que usa `vtable+0x24`). La tabla
`0x43fee3f8` tiene **95 registros de 6 B**, no 19 filas. Todo verificado por bytes
(`analysis/s314_selector_object/`, 58 comprobaciones, 10 tests).

---

## 1. Corrección de la premisa (VERIFICADO)

La llamada al selector está en `0x4354908c`, no en `0x43549084`:

| Dirección | Bytes | Instrucción | Papel |
|---|---|---|---|
| `0x4354904e` | `d0 6e` | `ldr r0, [r2, #0x6c]` | `r0 = [[ctx]] + 0x6c` (con `r2 = [ctx]`) |
| `0x43549082` | `bb 68` | `ldr r3, [r7, #8]` | `r3 = [ctx+8]` |
| `0x43549084` | `d3 f8 1c 12` | `ldr.w r1, [r3, #0x21c]` | **`r1`**, no `r0` |
| `0x43549088` | `d3 f8 20 22` | `ldr.w r2, [r3, #0x220]` | `r2` |
| `0x4354908c` | `dd f2 64 fe` | `bl #0x43826d58` | selector `sel(r0, r1, r2)` |

`ctx` es el valor devuelto por el getter `0x437b38ec`:

```
0x437b38ec  ldr r0, [pc, #4]      ; literal en 0x437b38f4 = 0x006f37ae
0x437b38ee  add r0, pc            ; PC = 0x437b38f0
0x437b38f0  bx lr                 ; r0 = 0x43ea709e
```

`ctx = 0x43ea709e` vive en BSS; `[ctx]` y `[ctx+8] = 0x43ea70a6` son **punteros** que el
blob deja a cero. La función que contiene la llamada (`0x43548c70`) recibe además `this` en
`r0` y lee `this+0xd78`, `this+0xd70`, `this+0x3e8`, etc.; es otra clase distinta del `ctx`.

### 1b. El slot `0x64` (VERIFICADO)

| Entrada | Bytes | Semántica |
|---|---|---|
| `0x43ad96f8` | `00 68 08 b5 03 68 5b 6e 98 47 08 bd` | `r0=*r0; (*r0)->vtable[0x64]()` |
| `0x43ad9704` | `10 b5 03 9c 00 68 bd e8 10 40 00 f0 e4 b9` | `r0=*r0; tail-call 0x43ad9ada` |
| `0x43ad9ada` | `... 5b 6a 98 47 ... 5b 6a 98 47` | `vtable+0x24` **dos veces** (cálculo de tamaños) |

**Corrige S310 y la fila 13 de S313:** `0x43ad9704` no es el thunk del slot `0x64`; lo es
`0x43ad96f8`. La llamada de `0x435490c4` pasa el resultado del selector como tercer
argumento a `0x43ad9ada` (dimensiones), no a un despacho `vtable+0x64`.
Callers: selector → `0x4354908c`, `0x43826df2`; wrapper `0x43ad9704` → `0x435490c4`,
`0x43826e3e`.

---

## 2. Tabla de decisión del selector `0x43826d58` (VERIFICADO)

Firma real: `int sel(int a /*r0*/, int b /*r1*/, int c /*r2*/)`.

| `a` (r0) | `b` (r1) | `c` (r2) | Devuelve | Instrucción que lo fija |
|---|---|---|---|---|
| `5` | * | * | `0x0c` | `0x43826da2 movs r0,#0xc` |
| `0x1b` | * | * | `0x35` | `0x43826daa movs r0,#0x35` |
| otro | `0` | `2` | **`0x4e`** | `0x43826d7c movs r0,#0x4e` |
| otro | `1` | `2` | **`0x4f`** | `0x43826da6 movs r0,#0x4f` |
| otro | `>=2` | `2` | `0x4e` + log | `0x43826d78 bl 0x438f7114`, cae a `0x43826d7c` |
| otro | `1` | `!=2` | `0x35` | `0x43826d82 beq 0x43826daa` |
| otro | `2` | `!=2` | `0x17` | `0x43826d8c movs r0,#0x17` |
| otro | `0` | `!=2` | `0x0b` | `0x43826d9e movs r0,#0xb` |
| otro | `>=3` | `!=2` | `0x0b` + log | `0x43826d90 bl 0x438f7114`, cae a `0x43826d9e` |

En la llamada real: `a = [[ctx]]+0x6c`, `b = [[ctx+8]]+0x21c`, `c = [[ctx+8]]+0x220`.
Por tanto el modo silent (`0x4e`/`0x4f`) se elige con **`c == 2` y `b ∈ {0,1}`**; no con el
«tipo» genérico que sugería la lectura de S302. El valor `b` es un índice 0/1.

---

## 3. Los objetos `[ctx]` y `[ctx+8]` (NO_VERIFICADO)

* Se leen en 88 sitios del blob A7S (barrido `ldr/add pc`, formas de 16 y 32 bits); los
  campos de `[ctx+8]` usados son `+0x18c, +0x21c, +0x220, +0x494, +0x56c, +0x570, +0x7b8,
  +0x7cc, +0xc0, +0xc8`.
* **No se localiza un `str` estático** a `0x43ea709e` ni a `0x43ea70a6` en `av-cam.bin`
  (ni directo ni por `add pc`). Tampoco hay literales absolutos con esas direcciones.
  La inicialización parece cruzar módulo o hacerse por una copia no visible como store.
* Consecuencia: la **identidad de clase y el vtable** de esos dos objetos queda
  **NO_VERIFICADO**. No se puede afirmar que el consumidor del modo silent sea una clase
  concreta sin runtime o sin el módulo que inicializa el `ctx`.
* El objeto de `0x43ad9704` sí se resuelve por bytes: `r0 = [0x4402d564] = 0x43e8dd98`
  (BSS), y `0x43ad9ada` usa `vtable+0x24`; su constructor/vtable tampoco es visible
  estáticamente (misma limitación).

---

## 4. Tabla `0x43fee3f8`: 95 registros, no 19 (VERIFICADO)

* Es un **array terminado en NULL** de **95 punteros** (`0x43fee3f8 … 0x43fee570`;
  terminador `0x43fee574 = 0`).
* Cada puntero apunta a un **registro de 6 B** alineado a 6 desde `0x44021ebc`:
  `u8 dev | u8 0 | u16 reg | u8 data | u8 0`. Los dos bytes de relleno son 0 en los 95.
* Reparto de dispositivo: **94 × `0x81`** y **1 × `0x83`** (registro 94:
  `83 00 17 00 4a 00`, reg `0x0017`, data `0x4a`).
* Consumidor: bucle en `0x436f4526`/`0x436f455c` que lee `ldrb [r3]`, `ldrh [r3,#2]`,
  `ldrb [r3,#4]` y avanza con `ldr r3,[r6],#4` hasta NULL. Confirma el formato lógico de
  5 B de S56, pero el **almacenamiento es de 6 B** (con relleno).
* La cifra «19 filas» de S313 **no es reproducible** en ninguno de los dos blobs.
  En la A6000, la misma VA `0x43fee3f8` pertenece a otra tabla: 71 punteros desde
  `0x43fee300` hasta `0x43fee418`, terminador `0x43fee41c = 0`.

### 4b. Tabla de 68 filas en `0x43fee5ac` (VERIFICADO el recuento; semántica NO_VERIFICADA)

Estructura de `0x14` B: `{ptr, 16 B}`. Hay **68 filas** (`0x43fee5ac … 0x43feeae8`),
terminador en `0x43feeafc`. Los punteros caen **2 B antes** de un registro de 6 B
(p. ej. fila 0 → `0x440220ac`, y el registro empieza en `0x440220ae`), por lo que el
significado del prefijo de 2 B y de los 16 B de cola queda **NO_VERIFICADO**.

---

## 5. Contraste A7S ↔ A6000 (VERIFICADO)

| Hecho | A7S 3.20 | A6000 3.21 |
|---|---|---|
| Par `ldr.w [#0x21c]` + `ldr.w [#0x220]` sobre el mismo objeto | **1** sitio (`0x43549084`) | **0** sitios |
| Código en `0x43549084` | carga `r1` para el selector | `add.w r3,r5,#0x1700` (otra función) |
| Tabla en `0x43fee3f8` | 95 punteros a registros de 6 B | run de 71 punteros, otra tabla |
| Terminador | `0x43fee574 = 0` | `0x43fee41c = 0` |

Esto refuerza S309/S312: el selector y su sitio de llamada son **código exclusivo** de la
A7S; la A6000 no tiene el par de campos que alimenta la decisión.

---

## 6. Impacto en la pregunta del silent shutter

* **No cambia S51 (A=NO, B=NO, C=NO).** Sigue sin demostrarse una ruta electrónica de
  integración a resolución completa ni un parche justificable.
* Lo que sí queda más preciso: el modo `0x4e/0x4f` se selecciona por
  `(c == 2, b ∈ {0,1})` leídos de `[ctx+8]+0x21c/+0x220`, y la salida se pasa a un cálculo
  de dimensiones (`vtable+0x24`), no a un despacho `vtable+0x64`.
* La tabla `0x43fee3f8` es la **lista de registros del sensor** (95 entradas, formato
  6 B) consumida por el formateador `0x436f25f0`/`0x43ad968a`; **no** es una tabla de
  tiempos de 19 filas.

---

## 7. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s314_selector_object/build_selector.py
.venv/bin/python analysis/s314_selector_object/verify_selector.py   # 58 comprobaciones
.venv/bin/python -m unittest tests.test_s314_selector_object          # 10 tests
.venv/bin/ruff check analysis/s314_selector_object tests/test_s314_selector_object.py
.venv/bin/mypy --ignore-missing-imports analysis/s314_selector_object
```

SHA-256 de los blobs usados:

* A7S 3.20 `av-cam.bin`: `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`
* A6000 3.21 `av-cam.bin`: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`

REA: sesión única sobre el A7S (`analysis/rea-independent/input/av-cam-a7s.bin`, base
`0x43541000`), cerrada al acabar; las conclusiones de este informe no dependen de REA.

---

## 8. Límites explícitos

* Análisis **estático** de los blobs; no se ejecutó firmware, no se usó la cámara, no se
  flasheó y no hay traza física.
* La identidad de clase de `[ctx]`/`[ctx+8]` y de `[0x43e8dd98]` es **NO_VERIFICADA**:
  no se encontró su escritor/vtable estático.
* Que no se encuentre un `str` no prueba ausencia universal: puede haber inicialización
  cruzada de módulo, copia por `memcpy` o código no cubierto por el barrido.
* La semántica física de los registros y del cluster A7S `+0xae/+0xde/+0xe6..+0xea`
  sigue **NO_VERIFICADA** (sin datasheet ni traza).
