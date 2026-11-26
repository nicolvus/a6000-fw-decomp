# G116 — LUT solo desde la SD: cueva, máquina y curva al hueco G18, y app web (26-11-2026)

Cierra **LUT-C** (estático) y **LUT-T-1** por la vía que quedaba abierta tras G107 §3: sacar el ajuste «LUT» de
`ZONA_A`/`ZONA_B` (tabla T1 de estabilización y tablas BOKS del YC), que están **vivas**, y dejar de meter tablas en el `.dat`.
El ajuste pasa a ser **solo SD**: la tabla (y, si la hay, la curva 1D) sale del blob de Backup `0x150005` que escribe el
userland con los `.cube` o los `.LUT` de la tarjeta (G89/G95). Sin tarjeta no hay LUT y el ajuste queda en fábrica.

Incluye la **app web** (`site/lut/`), que convierte un `.cube` al `.LUT` de la tarjeta y previsualiza la foto con la misma
cadena y la misma tabla que aplica la cámara.

## 1. Reparto de memoria (av-cam)

| Qué | Dónde | Tamaño |
|---|---|---|
| Cueva del ajuste (desempaqueta la tabla del blob) | `0x43FB8800`… (`ZONA_L18`) | ~250 B |
| Celda de 8 B (búfer ISP 0x654 + búfer del blob 16 KB) | `0x43FB8800` (`LUT_CELDA`) | 8 B |
| Cueva de la máquina de estados | tras la cueva, dentro de `ZONA_L18` | ~270 B |
| Celda de la curva (búfer de 2048 B) | `0x43FB8360` (`T_CELDA`) | 4 B |
| Cueva de la curva | `0x43FB8368` (`T_CODIGO`) | ~450 B |

`ZONA_L18 = (0x43FB8800, 0x43FB8EE0)` es la cola libre del hueco G18: detrás de la tabla de ISO
(`iso_avcam_patch` acaba en `0x43FB8360`) y con la curva T (`lut_t.ZONA_T18`) por debajo. `ZONA_G18` completa sigue siendo
`0x43FB7E80…0x43FB8EE0`; `apply_bytes` exige que **todo** lo que escribe caiga en `ZONA_L18` o `ZONA_T18` y que esas zonas
estén a cero en el fichero.

`ZONA_A` y `ZONA_B` quedan **intactas**: el parche ya no escribe ni un byte en ellas. Eso cierra la deuda ZONA-1 en lo que
toca a la LUT (HLG sigue con su propia cueva en `ZONA_A`, fuera de este cambio).

## 2. Por qué el escáner basta como prueba estática

`scripts/lut/zonas.py` busca referencias reales a una zona: literales alineados que caen dentro y direcciones PC-relativas
(`adr`, y el par `ldr rX,[pc,#i]` + `add rX, pc`). Control positivo y negativo sobre `av-cam.bin`:

| Zona | Referencias encontradas |
|---|---|
| `ZONA_A` (`0x43BE3B28…`) | `0x43705A3C` (`ldr+add` → `0x43BE3B28`) |
| `ZONA_B` BOKS (`0x43C1FF24…`) | `0x438F6FBA`, `0x438F6FD2` |
| `ZONA_L18` (`0x43FB8800…0x43FB8EE0`) | **ninguna** |
| `ZONA_T18` (`0x43FB8360…0x43FB8EE0`) | **ninguna** |

Límite del escáner (y del test): no ve `movw`/`movt` absolutos ni punteros calculados en ejecución. La prueba fuerte es la
emulación: el parche completo se ejecuta con Unicorn y entrega la tabla del blob byte a byte (`test_g71_lut.py`,
`test_g89_lut_sd.py`).

## 3. Cambios de comportamiento

- El menú «LUT» tiene **siempre** 7 opciones: `Off`, `LUT 1`…`LUT 6` (`sd_lut.ajustes_sd()`); desaparecen los looks de
  fábrica `Teal&Orange`/`Película`/`Neutro`, que vivían en las tablas del `.dat`.
- `lut_patch.apply_bytes(data)` ya no acepta `tablas`, `sd` ni `curvas`: no hay modo `.dat`. `build_fn_lut.py` pierde
  `--cubes`/`--sd` y `build_cfw_objetivos.py` deja de alternar `MODO_SD` (siempre SD).
- La **curva T** sale también del blob (registro de 68 B por ranura, `BK_T_OFF = 0x1900`), con la misma regla que la tabla:
  ranura inválida → sin curva. Antes caía a los registros del `.dat`, que ya no existen; con una tabla de fábrica y una curva
  de película el resultado habría sido un color erróneo.
- `lut_t.escrituras()` ya no escribe los 3 registros de 68 B: solo la celda y el código (204 B menos en G18).

## 4. App web (`site/lut/`)

Publicada con el resto de `site/` por `.github/workflows/pages.yml` (GitHub Pages).

- **Entrada**: uno o varios `.cube` 3D (2³…64³) arrastrados o elegidos en el navegador. Validación con el mismo criterio que
  `cube_spec.py`/`lutsd.c`: tamaño, filas completas, dominio, rechazo de 1D.
- **Salida**: paquete v1 `A6LT` de 1080 B (cabecera + 405 nodos × 21 bits + CRC32), descargable como `LUT1.LUT`…`LUT6.LUT`
  para `LUT/` en la raíz de la tarjeta.
- **Tabla**: réplica entera de `lutsd.c` (`referencia()`): muestreo de los 405 nodos, corrección Δ²/12, saturación a ±63.
  El test `tests/test_g116_web.py` compara el paquete que genera Node con `lut_sd_userland.referencia` para 2³, 5³ y 33³:
  **byte a byte**.
- **Previsualización**: foto subida por el usuario; se aplica la tabla en la cadena modelada del proyecto
  (`cube_a6000.Cadena` con M = I y T = sRGB: sRGB → YCbCr BT.601 → LUT 5×9×9 de deltas s7 → RGB) y se puede comparar con el
  `.cube` exacto (trilineal), que es el techo teórico, no lo que hace la cámara.

**Qué es idéntico y qué no.** Idénticos: los bytes del `.LUT` y la tabla 5×9×9 (mismo redondeo y misma corrección que el
ARM), y por tanto la transformación de color que aplica el ISP en el modelo del repo. No modelados: demosaico, reducción de
ruido, gamma propia del JPEG. Es el modelo del PC: **no se ha medido en cámara** (LUT-C cerrado solo en estático).

## 5. Verificación estática

```
pytest tests/test_g71_lut.py tests/test_g86_fn_lut.py tests/test_g86_lut_caliente.py \
       tests/test_g89_lut_sd.py tests/test_g95_lut_pkg.py tests/test_g115_lut_t1.py \
       tests/test_g88_sd_lut.py tests/test_g116_zonas.py tests/test_g116_web.py
node --test site/lut/
```

Cubre: ganchos originales, zonas nuevas sin referencias, parche confinado y determinista, tabla del blob servida por las dos
cuevas (SA/MOV) en Unicorn con reservas de memoria y fallos, Off/ranura inexistente → fábrica, curva por ranura (con y sin
`malloc`), menú de 7 opciones, userland y build sin `.dat`, escáner con control positivo, y el `.LUT` de la web igual al del
firmware.

## 6. Límites y pendientes que quedan

- **Nada de esto está probado en cámara.** El CFW 3.86 instalado lleva el parche histórico (cueva y tablas en T1/BOKS):
  **no usar LUT con ese CFW**. Hace falta un build con G116 y las pruebas de cámara LUT-SD-2/LUT-T-2.
- LUT-A (matriz M), LUT-2C-1 (segunda curva de 512 puntos) y LUT-OPT-1 (pesos de entrenamiento) siguen como estaban: son
  mejoras del ajuste en el PC, no bloquean esta vía. LUT-DE-1 (ΔE con `C2'`) tampoco cambia la tabla que consume la cámara.
- La previsualización no sustituye a revelar el RAW; el JPEG de la cámara ya trae su propia gamma y nitidez.
