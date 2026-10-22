# S320 — Modo 2 no cambia la trama: reintenta el mismo formateador (carril B)

**Resultado en una línea:** los dos aplicadores de listas de S315 usan el **mismo**
formateador. `0x43ad968a` (modo ≠ 2) fija `obj[3]=arg1`, llama a `0x43ad931c` y a
`0x43ad9666`. `0x436f25f0` (modo 2) hace exactamente lo mismo (7 instrucciones idénticas) y
sólo añade un **reintento** si el formateador devuelve `2` (ocupado): llama a `0x43ad92e6`,
repite `0x43ad9666` y registra un log si vuelve a fallar. Por tanto el modo elige **qué
lista** se aplica, no una trama distinta. Todo exclusivo A7S.

20 comprobaciones, 5 tests: `analysis/s320_frame_retry/`.

---

## 1. Prefijo común (VERIFICADO)

| Dirección (`0x43ad968a`) | Dirección (`0x436f25f0`) | Instrucción |
|---|---|---|
| `0x43ad968a` | `0x436f25f0` | `push {r0,r1,r4,r5,r6,lr}` |
| `0x43ad968c` | `0x436f25f2` | `mov r4,r0` |
| `0x43ad968e` | `0x436f25f4` | `mov r5,r2` |
| `0x43ad9690` | `0x436f25f6` | `mov r6,r3` |
| `0x43ad9692` | `0x436f25f8` | `strb r1,[r0,#3]` |
| `0x43ad9694` | `0x436f25fa` | `mov r1,r4` |
| `0x43ad9696` | `0x436f25fc` | `add r0,sp,#4` |

Después ambos llaman a `0x43ad931c` y a `0x43ad9666` con `(sp+4, r5, r6)`.

## 2. Bloque extra del modo 2 (VERIFICADO)

```
0x436f260c  cmp r0,#2
0x436f260e  bne 0x436f262c      ; si no esta ocupado, fin
0x436f2610  mov r0,r4
0x436f2612  bl 0x43ad92e6       ; libera/reintenta
0x436f2616  add r0,sp,#4
0x436f2618  mov r1,r5
0x436f261a  mov r2,r6
0x436f261c  bl 0x43ad9666       ; segundo intento
0x436f2620  cmp r0,#2
0x436f2622  bne 0x436f262c
0x436f2624  ldr r0,[pc,#8]
0x436f2626  add r0,pc
0x436f2628  bl 0x438f7114       ; log si sigue ocupado
```

`0x43ad9666` es el constructor de trama; delega en `0x436f2554` y `0x43ad9628` (no se
decodifica aquí el contenido byte a byte).

## 3. Contraste A7S ↔ A6000 (VERIFICADO)

Firmas de 24–48 B: `0x436f25f0`, `0x43ad968a`, `0x43ad9666` y `0x43ad92e6` tienen **0
coincidencias** en la A6000 3.21. El par «aplicador con reintento / aplicador simple» es
exclusivo A7S.

## 4. Lectura y límites

* **VERIFICADO:** misma trama, mismo formateador; modo 2 añade un reintento con
  `0x43ad92e6` y log.
* **NO_VERIFICADO:** el contenido exacto de la trama, el significado de «ocupado» (`r0==2`) y
  el enlace de `modo 2` con el silent shutter. S51 sin cambios.

---

## 5. Reproducción

```sh
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s320_frame_retry/build_frames.py
.venv/bin/python analysis/s320_frame_retry/verify_frames.py   # 20 comprobaciones
.venv/bin/python -m unittest tests.test_s320_frame_retry       # 5 tests
.venv/bin/ruff check analysis/s320_frame_retry tests/test_s320_frame_retry.py
.venv/bin/mypy --ignore-missing-imports analysis/s320_frame_retry
```

SHA-256 A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`,
A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

**Límite global:** análisis estático; sin firmware ejecutado, sin cámara, sin flasheo y sin
pruebas físicas.
