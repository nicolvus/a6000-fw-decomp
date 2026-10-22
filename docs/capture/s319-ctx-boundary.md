# S319 — Frontera estática del `ctx 0x43ea70a0` (carril B)

**Resultado en una línea:** el `ctx` corregido (`0x43ea70a0`, +2 respecto de S314) tiene
**40** sitios `ldr/add pc` en `av-cam.bin`: 31 lecturas de campo, 1 store (a `+0x44`, no a
`+0`/`+8`), 3 pasos como argumento y 5 indirectos. **Ningún** sitio escribe `[ctx]` ni
`[ctx+8]`. **0** literales absolutos de `0x43ea70a0`/`0x43ea70a8` en `av-cam` y **0** en los
`kmod/*` y `lib/*` del firmware A7S. Veredicto: **NO_VERIFICADO** (la ausencia de literales
no prueba ausencia de escritura cross-module).

16 comprobaciones, 5 tests: `analysis/s319_ctx_boundary/`.

---

## 1. Corrección del `ctx` (VERIFICADO)

La regla de `add rX,pc` de 16 bits es `PC = (dirección + 4)` con **bit0 a 0**, no alineado a
4. Con alineado a 4 se obtenía `0x43ea709e` (sesgo de +2). REA/Ghidra lo confirma:

```
FUN_437b38ec: return DAT_437b38f4 + 0x437b38f2
            = 0x006f37ae + 0x437b38f2 = 0x43ea70a0
```

Por tanto `ctx = 0x43ea70a0`, `ctx+4 = 0x43ea70a4`, `ctx+8 = 0x43ea70a8`. Los campos
`[ctx]`, `[ctx+4]` y `[ctx+8]` son punteros; el código los usa como tales.

## 2. Barrido en `av-cam.bin` (VERIFICADO)

| Clase | Nº | Detalle |
|---|---|---|
| lectura (`ldr`) | 31 | acceso a `[ctx+off]`, incluido `[ctx+8]` |
| store | 1 | `0x437b5d4a` → `str r4,[r6,#0x44]` (**no** `[ctx]`) |
| paso como argumento | 3 | `0x437b3812`, `0x437b383a`, `0x437b3f5e` |
| indirecto | 5 | sin operación de memoria con el registro base en la ventana |

Sitios directos a `ctx+8` **calculados como base**: **0** (el acceso a `[ctx+8]` se hace
siempre con base `ctx` y desplazamiento 8).

**No hay store a `[ctx]` ni a `[ctx+8]`** entre los 40 sitios.

## 3. Literales absolutos (VERIFICADO)

| Binario | `0x43ea70a0` | `0x43ea70a8` |
|---|---|---|
| `av-cam.bin` | 0 | 0 |
| `kmod/*` (incl. `liro.ko`) | 0 | 0 |
| `lib/*` (incl. `libObj.so`) | 0 | 0 |

## 4. Alcance del resultado (NO_VERIFICADO)

Que no haya literales ni stores visibles **no prueba** que nadie escriba esos punteros:

* el escritor puede recibir `ctx` como argumento en una función (los 3 sitios «arg» y los
  llamadores de éstas no se han seguido hasta el fondo);
* puede ir por memoria compartida, OSAL o un mapeo del kernel (`liro.ko`) sin literales
  absolutos;
* puede ser una copia `memcpy`/`stm` no cubierta por la ventana de clasificación.

Por eso el veredicto es **NO_VERIFICADO**, no «imposible». Los candidatos concretos a seguir
son `0x437c7b0c` (recibe `ctx` y llama a `0x437c83e8`) y `0x437ca5c8` (recibe `ctx` con
muchos punteros GOT).

## 5. Impacto

* Confirma que el `ctx` es un array de punteros a subobjetos (`+0`, `+4`, `+8`) y que su
  inicialización no está en el código visible de `av-cam`.
* No cambia S51 (A=NO, B=NO, C=NO).

---

## 6. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s319_ctx_boundary/build_ctx_boundary.py
.venv/bin/python analysis/s319_ctx_boundary/verify_ctx_boundary.py   # 16 comprobaciones
.venv/bin/python -m unittest tests.test_s319_ctx_boundary             # 5 tests
.venv/bin/ruff check analysis/s319_ctx_boundary tests/test_s319_ctx_boundary.py
.venv/bin/mypy --ignore-missing-imports analysis/s319_ctx_boundary
```

SHA-256 A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
