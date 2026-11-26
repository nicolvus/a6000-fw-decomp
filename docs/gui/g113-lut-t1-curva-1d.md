# G113 — LUT-T-1: curva 1D tras la gamma en el ajuste «LUT» (26-11-2026)

Petición: cerrar **offline** el pendiente LUT-T-1 (curva 1D tras la gamma dentro del ajuste «LUT» genérico, con la curva guardada
de forma compacta, elección T sí/no por LUT y paquete `.LUT` ampliado). Solo PC: Unicorn sobre `av-cam.bin`, estático y compilación
ARM del userland; **sin cámara, sin CFW construido ni instalado, sin flashear**.

Código: `scripts/lut/lut_t.py` (nuevo: cueva, registros compactos, zona y emulación), `lut_patch.py` (integración en el ajuste),
`lut_pkg.py` (paquete v2), `userland/lutsd.c` (validación v2 y compactado en el blob). Tests: `tests/test_g113_lut_t1.py` (11)
y ajustes en `tests/test_g71_lut.py` y `tests/test_g95_lut_pkg.py`. Contexto: [g92](g92-auditoria-cadena-color-lut-general.md) §3-4,
[g107](g107-causas-pp-ids-zonas.md) §3, [g98](g98-film-auditoria-curva-apps.md), [g111](g111-film-receta-gui-iconos.md), [g95](g95-lut-paquete-precalculado.md).

## 1. Conclusión

- **La curva está integrada y verificada en Unicorn sobre el código real**, no solo propuesta: con el ajuste «LUT» en la LUT que
  lleva curva, el firmware compone `T∘gamma` en los **dos** consumidores de la cadena de tono (la curva de 512 puntos `FUN_438538e4`
  y la rejilla de 96 nodos `FUN_43853200` que va al hardware). Con Off, o con una LUT sin curva, no se escribe **ni un byte** del
  objeto ni de `c68[8]`: el resultado es idéntico al de fábrica (test contra la imagen sin parchear).
- **No hay cueva nueva**: se reutiliza el mecanismo que G98/G111 ya puso en producción para la función Film —cuatro ganchos en las
  llamadas a `FUN_43852f7c` y la ranura `c68[8]` (`0x440013ec`) de la gamma extendida de Sony— en lugar de los dos ganchos sobre
  `FUN_438538e4` que proponía G92 §3. Ventaja: una sola pareja de ganchos sirve a los dos consumidores (G98 midió que el 3.87 solo
  reescribía la curva de 512 puntos y la rejilla quedaba sin la curva).
- **Elección T por LUT**: `True` solo para la película. Medido (ΔE2000 sobre 20 000 colores uniformes): teal & orange 0,065 → 0,201
  e identidad 0,027 → 0,072 **empeoran** con T; película 0,793 → 0,198 **mejora 4×**.
- **Almacenamiento**: curva de 1024 u16 → 33 nodos (68 B) con el extremo copiado tal cual; registros en el `.dat` y en el blob de la
  SD; paquete `.LUT` **v2** (3128 B) con la curva completa y el flag; v1 sigue valiendo tal cual.
- **La integración está BLOQUEADA por ZONA-1 para instalarse en cámara** (§5): la cueva histórica de la LUT y sus 3 tablas siguen
  escribiendo en `ZONA_A` (tabla T1 de estabilización) y `ZONA_B` (tablas BOKS del YC de captura), que **no son huecos**. Todo lo que
  añade G113 va a una ventana verificada del hueco G18. No se cierra LUT-T-1 como instalable.

## 2. Mecanismo, direcciones y bytes exactos

| Pieza | Dirección | Bytes / tamaño | Notas |
|---|---|---|---|
| Ganchos de curva (4) | `0x438548b0`, `0x43854c46`, `0x43854ff6`, `0x43b098cc` | `fef764fb → 63f3bef5`, `fef799f9 → 63f3f3f3`, `fdf7c1ff → 63f31bf2`, `49f556fb → aef0b0f5` | eran `bl 0x43852f7c`; pasan a `bl 0x43fb8430` |
| Cueva de la curva | `0x43fb8430` | 304 B (build sin SD) · 456 B (build con SD) | termina en `b.w 0x43852f7c` (cola: no toca la pila del llamante) |
| Registros de curva del `.dat` | `0x43fb8360` | 3 × 68 B = 204 B | `u16 nº de nodos` (0 = sin curva) + 33 u16 |
| Celda del búfer | `0x43fb842c` | 4 B | puntero al búfer de 2048 B (`malloc` una vez) |
| Curva aplicada | `0x440013ec` = `c68[8]` | 4 B (puntero) | `c68[8]` de fábrica = identidad `0x43bfaf2a` |
| Blob de la SD: curvas | `+0x1900`…`+0x1a98` (id Backup `0x150005`) | 6 × 68 B = 408 B | justo detrás de las 6 tablas de 1064 B |

La cueva, con el ajuste en la ranura `k` (Off = 0):

1. lee el byte del ajuste (`Backup_read`, el `leer_asm` de `cfw_ajustes`); si `k = 0` → sale sin tocar nada;
2. busca el registro: con SD, primero el blob (ranuras 1…6, si su byte de validez de `+8` es 1) y, si no hay, el `.dat` (ranuras 1…3);
   sin SD, el `.dat`;
3. si el registro no tiene 33 nodos → sale sin tocar nada (esa LUT no lleva curva);
4. si no hay búfer, `malloc(2048)` una vez y lo guarda en la celda; expande los 33 nodos a 1024 u16 (interpolación lineal, redondeo
   `+16 >> 5`, y el extremo `T[1023]` copiado tal cual);
5. escribe `obj+0xbd5 = 1`, `obj+0xbe1 = 8`, `obj+0xbd1 = obj+0xbd3 = 0`, `c68[8] = búfer`;
6. salta a `FUN_43852f7c`.

Al volver a Off (o a una LUT sin curva) si `c68[8]` es nuestro búfer se restaura la identidad `0x43bfaf2a`; los indicadores no se
escriben nunca hacia atrás: el firmware los vuelve a copiar de la config en el siguiente paso (`bd1`/`bd3` tienen prioridad sobre
`bd5`, y con la identidad en `c68[8]` el resultado es el de fábrica, que es lo que comprueba el test).

**Precedencia con Film (mismo mecanismo y mismo id de Backup).** `film_patch` ocupa los *mismos* cuatro ganchos, los dos ganchos de
la LUT 3D, el gancho de la máquina y el blob `0x150005`. Un build lleva **Film o LUT, no los dos**: `lut_patch.apply_bytes` rechaza
la imagen si los ganchos de curva ya no son `bl 0x43852f7c` (y `film_patch` hace lo propio con los de la LUT), así que el conflicto
se ve como error de construcción, no como cámara rara. El ACK de 1 B de Film (`cfw.ID_LIBRES[8]`) no lo usa la LUT: la LUT lee su
propia fila del menú.

## 3. Layout del paquete `.LUT` v2 y del blob

**Fichero `LUT/LUT<n>.LUT`** (little-endian):

| Desplazamiento | v1 (1080 B) | v2 (3128 B) |
|---|---|---|
| 0 | `A6LT` (u32) `0x544c3641` | igual |
| 4 | versión **1** | versión **2** |
| 5 | 0 | `usa_T`: 0 = la LUT no lleva curva, 1 = sí |
| 6 | 1064 (u16), longitud de la tabla | igual |
| 8 | CRC32 IEEE de los 1064 B siguientes | CRC32 IEEE de los **3112** B siguientes (tabla + curva) |
| 12 | 0 (u32) | igual |
| 16 | tabla 405 × 21 bits | igual |
| 1080 | — | curva T: 1024 u16 sobre el código de gamma |

En las dos versiones el CRC cubre **todo lo que sigue a la cabecera**, así que la regla es única. Un paquete v2 en una cámara con el
código v1 se rechaza por longitud y se cae al `.cube` (no rompe nada). `usa_T = 0` guarda la curva igualmente (mismo tamaño): la
cámara solo la usa si vale 1.

**Blob del Backup `0x150005`** (16 KB, lo escribe el hilo de la SD):

| Desplazamiento | Campo |
|---|---|
| 0 | `LUTS` (u32) · 4: versión 1 · 6: nº de ranuras (6) · 8…13: máscara de válidas · 14: letra de la unidad |
| 16 + (k−1)·1064 | tabla de la ranura `k` (1064 B) |
| **0x1900 + (k−1)·68** | **curva de la ranura `k`**: `u16 nº de nodos` (0 o 33) + 33 u16 (nuevo en G113) |
| 0x2000 | diagnóstico de rutas/lecturas de G89 (lo ignora `av-cam`) |

`av-cam` desempaqueta la tabla como siempre y ahora expande el registro de la curva. El `.cube` **no** lleva curva (la cámara no puede
calcular una curva tonal en punto fijo): con `.cube` el ajuste funciona sin T, como hasta ahora.

## 4. Elección T por LUT y calidad medida

`lut_t.t_por_defecto()` fija la elección de las 3 tablas del `.dat` con las cifras de abajo; `lut_pkg.elige_t(f)` hace la misma
comparación (ΔE medio con y sin T sobre 4000 uniformes) para cada `.cube` que se empaqueta, y `lut_pkg.py ENTRADA.cube SALIDA.LUT`
la usa por defecto (`--t` / `--sin-t` la fuerzan).

ΔE2000 **medio / p95 / máx** frente a la función de la LUT (la misma que genera los `.cube` 33³ de G95, para poder comparar con
G92 §4), 20 000 colores uniformes (semilla 7), LUT 5×9×9 ajustada en ΔE
(`cube_a6000.descompone`, modelo de interpolación «ambos»):

| LUT | solo LUT | T + LUT (curva exacta) | T de 65 nodos | **T de 33 nodos (la que se guarda)** | ¿T? |
|---|---|---|---|---|---|
| teal & orange | **0,065 / 0,151 / 0,399** | 0,201 / 0,590 / 6,118 | 0,200 / 0,585 / 6,118 | 0,205 / 0,617 / 5,938 | **no** |
| película | 0,793 / 1,808 / 6,030 | **0,198 / 0,508 / 1,260** | 0,198 / 0,509 / 1,260 | **0,202 / 0,522 / 1,187** | **sí** |
| identidad | **0,027 / 0,060 / 0,265** | 0,072 / 0,154 / 0,736 | 0,076 / 0,163 / 0,736 | 0,078 / 0,157 / 0,578 | **no** |

Coste de compactar: con 33 nodos la desviación máxima de la curva es de 3 códigos de 1023 (0,3 %) y el ΔE sube 0,004 en la película
(0,198 → 0,202); con 65 nodos, 2 códigos y 0,000. Se eligen 33 nodos porque 3 × 68 B caben en la ventana de 2944 B de G18 y 6 × 68 B
en el hueco de 1792 B del blob; con 65 nodos no cabría en el `.dat` sin volver a una zona ocupada.

Estas cifras reproducen las de G92 §4 (película 0,79 → 0,19) con el modelo actualizado: la curva se aplica **sobre el código de gamma**
(1024 u16), no como segunda etapa lineal, y ahí la compactación se paga en códigos, no en ΔE.

## 5. Seguridad de zonas: ZONA-1 (esto es lo que impide instalarlo)

La auditoría paralela de G107 §3 (posterior a G71/G73) demostró que **`ZONA_A` y `ZONA_B` no son huecos**:

- `ZONA_A` (`0x43be3b28…0x43be4330`) es la **tabla T1 de estabilización** (1025 u16, la lee `0x43705a34` en un modo EIS).
- `ZONA_B` (`0x43c1ff24…0x43c20c8c`) son **dos tablas s16 6×13×11 del YC de captura BOKS** (descriptor `0x438f6fa4`, interpoladas en
  `0x43881290`).

Estado tras G113:

| Pieza de la LUT | Dónde | ¿Seguro? |
|---|---|---|
| Cueva de la tabla (desempaquetado + 2 ganchos) y cueva de la máquina | `ZONA_A` `0x43be3f28…` | **NO** (pisa T1[512…1024]); deuda anterior a este informe |
| 3 tablas de 21 bits (3192 B) | `ZONA_B` `0x43c1ff24…0x43c20b9c` | **NO** (primera mitad de BOKS); deuda anterior |
| **Curva T (registros + celda + cueva)** | **`0x43fb8360…0x43fb8ee0`** | **sí** (ventana nueva, dentro del hueco G18) |

La ventana de la curva: `lut_t.ZONA_T18 = (0x43fb8360, 0x43fb8ee0)`, 2944 B, elegida como el tramo de G18 que ningún otro parche
usa. Ocupantes conocidos de G18 (y test que comprueba que no se solapan): PP color `0x43fb7400`, PP tone `0x43fb7500…0x43fb7ec0`,
bulb timer `0x43fb7f00…0x43fb7f80`, gancho JPEG `0x43fb7f80…0x43fb7fc4`, Film `0x43fb7e80…0x43fb811c`, ISO `0x43fb8280…0x43fb8360`.
Lo usado por la curva son 512 B de los 2944 en el build sin SD (204 + 4 + 304) y 664 B con SD (204 + 4 + 456).

**Verificación y su límite (no se maquilla):** G107 §3 da el hueco G18 por libre con «0 referencias relativas al PC ni `adr`», y los
bytes están a cero en el fichero (lo comprueba `apply_bytes`, que aborta si no). **No he re-hecho** aquí un barrido independiente de
`ldr/add pc` sobre `av-cam`: el barrido lineal en Thumb que probé (`capstone` desde `0x43541000`) no decodifica alineado y da 0
referencias incluso en `ZONA_A`/`ZONA_B`, que sí las tienen, así que no vale como prueba. La seguridad de la ventana se apoya en
G107 y en que varios parches conviven ya en G18 y esas builds arrancaron en cámara (3.86 con la LUT y el hilo de la SD, G95 §4; 3.89 con
Film/ISO en G18, [G99](g99-film-receta-nativa.md)). `test_g74_cuevas_seguros.py` **no** se usa como prueba:
es ciego a `ldr/add pc`, como avisó la auditoría.

**Consecuencia para LUT-T-1:** implementado y verificado offline, **no instalable** hasta reubicar la cueva de la tabla y las 3
tablas de 3192 B (ZONA-1). La ruta más corta, medida con los tamaños reales de este informe: en el build **sin SD**, cueva de la tabla
(354 B) + cueva de la máquina (128 B) + registros, celda y cueva de la curva (512 B) = 994 B y, con las 3 tablas, **4186 B ≤ 4192 B**
de G18: entran con **6 B de margen** (demasiado justo para darlo por bueno). En el build **con SD** el desempaquetado crece
(472 + 132 + 664 = 1268 B) y con las tablas serían 4460 B: **no caben** (268 B de más). Para la SD habría que dejar las tablas de
respaldo en el montón o recortar una ranura del `.dat`.

## 6. Qué solo la cámara confirma (LUT-T-2)

1. Que `0x440013ec` (`c68[8]`) es **escribible** desde `av-cam` (`HLG-3b`, abierto desde G73: nadie ha escrito todavía en
   `0x44001404…`).
2. Que la curva compuesta llega al procesador en vídeo, vista en vivo y foto: carta de grises/colores con LUT Off / Teal&Orange (sin
   T) / Película (con T) medida con la misma escena, y comparación con `tono_post`/`cube_a6000` en el PC.
3. Que el `malloc` de 2048 B (curva) —y el de 16 KB del blob y el de 1620 B de la tabla— caben en el montón del SO tras arrancar con
   el resto del CFW (`HLG-3b`).
4. Que la normalización de salida del firmware (`cola`) no se come el look: la rama `bd5` no devuelve `tabla[gamma]` pelado (§7).
5. Que con la curva activa el JPEG no se apaga ni cambia de exponente (la curva va tras la gamma del usuario, pero es una tabla
   compartida por R, G y B y afecta también a la vista en vivo).

## 7. Tests ejecutados

| Fichero | Tests | Resultado |
|---|---|---|
| `tests/test_g113_lut_t1.py` (nuevo) | 11 | verde: ganchos = los de Film, Off y LUT sin curva = fábrica (curva, rejilla, indicadores y `c68[8]`), `T∘gamma` = `tono_post` en los dos consumidores, restaurar identidad al volver a Off, `malloc` = 0 no aplica, curva del blob por ranura, ventana de G18 sin solapes, paquete v1/v2 con CRC y flag, ARM = referencia (v1, v2 y `usa_T = 0`) |
| `tests/test_g71_lut.py` (ajustado) | 12 | verde; su test de zonas ahora incluye `ZONA_T18` y comprueba que la zona sigue dentro de G18 |
| `tests/test_g95_lut_pkg.py` (ajustado) | 3 | verde; `llama()` pasa el 4.º argumento de `lutsd_paquete` y el test del `.cube` fija `usa_t=False` (como G95) |
| `tests/test_g89_lut_sd.py`, `test_g90`, `test_g92`, `test_g93`, `test_g94` | 29 | verde, sin cambios |
| Suite LUT completa (`g71 g89 g90 g92 g93 g94 g95 g113`) | 55 + 6 omitidos | **55 pasan** en 3 min con `env -u CI` |

Aparte y **ajeno a la LUT**: `tests/knowledge` tiene 2 fallos previos por hashes fijados de `docs/capture/*` en
`analysis/s400_open_questions_triage/manual_review.json` (ficheros que este hito no toca); el resto, 76 en verde.

## 8. Límites

- **La rama `bd5` del firmware añade una normalización propia** (`cola`): con la misma tabla, la salida coincide en las sombras y sube
  hasta **+9 códigos de 1023** cerca del blanco (la tabla termina en 1013 y la salida, en 1023). El test lo mide y lo acota
  (`≤ 16`). El modelo del PC (`cube_a6000`, `tono_post`) **no** incluye ese efecto, así que las cifras de §4 predicen el look con ese
  error de escala en las altas luces. No se ha intentado revertir ingeniería de `cola`: es de la rama de gamma extendida, no de la LUT.
- **Una sola curva para R, G y B** (es la limitación del hardware, G92 §2): lo que difiera por canal sigue yendo al residuo de la LUT
  5×9×9. El tope de la rejilla sigue en 5×9×9 (G93).
- **Compactación a 33 nodos**: 3 códigos de 1023 de desviación máxima y +0,004 ΔE. No se guarda la curva de 1024 en el blob porque
  6 × 2048 no caben en 16 KB.
- **Cifras de calidad sin la columna de foto real**: en este worktree no hay `rawpy` ni ningún `.ARW`, así que las tablas son solo de
  colores uniformes (20 000). G92/G95 tenían además `DSC03986`; aquí no se puede reproducir.
- **`.cube` sin curva**: el conversor de la cámara no calcula T. Una LUT que la necesite tiene que llegar como `.LUT` v2 hecho en el PC.
- **Coste por llamada**: la cueva expande los 1024 valores en cada construcción de la curva (≈10 k instrucciones, como el copiado de
  2048 B que hace Film); no se cachea por ranura para no dejar la curva obsoleta si cambia la tarjeta.
- **El paquete v2 no está en ninguna build**: no se ha construido CFW en este hito (solo ficheros y Unicorn).
