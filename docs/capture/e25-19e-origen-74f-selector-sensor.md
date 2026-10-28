# E25-19e — Origen de `cap+0x74f=1` y selector 3/4 del controlador VD

Fecha: 28-10-2026. Modalidad: estático (Capstone) + **lectura física de solo lectura** (2 fotos normales de 4 s, `/dev/mem`; sin escrituras RAM, sin parche). Etiquetas: V = bytes, F = lectura física, I = inferencia.

Evidencia: `analysis/e25-19e/` (`plan142.json`, `cubren-74f.json`, `campos-g.json`, `selector-vd.json`, `lectura-4s-*.json`). Scripts: `scripts/e25_19e/` (`desmontar.py`, `plan142.py`, `cubren_74f.py`, `campos_g.py`, `selector_vd.py`, `lectura_ro.py`). Pruebas: `tests/test_e25_19e.py` (5) + `test_e25_19d.py` (5), verdes.

## 1. Resumen

* **W1 no puede ser el origen del 1 (V).** Copia `plan[0x13f..0x142]` → `cap[0x74c..0x74f]` byte a byte, y `plan+0x142` es `2×lookup` en las 8 ramas (`lsls r0,r0,#1` antes de cada `strh`): su byte bajo es par.
* **19d contó mal los escritores (V).** Faltan stores `strh` en `+0x74e` (cubren `+0x74f`): `0x4354af88` y `0x4354b0ac` (callback `EndExps` `0x4354a678`, VD_Post según S32) y `0x4354c868` (secuenciador `0x4354c6d0`). Además 5 `str.w` en `+0x74c` (`0x439c8254…`) de **otro objeto** (valores negados, punteros en `+4/+8`). Total de stores que cubren `74f`: 11 (`cubren-74f.json`).
* **`74c/74e` no son flags sino halfwords de geometría** (V): en `0x4354c6d0` son ancho/alto leídos de la tabla global `0x43e9515e` (en reposo `d0 02 f0 00` = 720×240; `0x43e95182` = 720×288). El físico `00 01 00 01` = halfwords `0x0100,0x0100`. **Consecuencia (I):** `74f` puede ser el byte alto de una altura/valor ≥256, no un flag; los 21 manejadores que hacen `ldrb 74f` lo leen como booleano.
* **Origen del 1: no demostrado.** Candidato principal: `EndExps` bloque 2 (`0x4354b0ac`, `74e ← sp+0x312`), cuyo valor no se evaluó. Bloque 1 y el secuenciador de vídeo quedan descartados para la foto normal (§3).
* **Selector 3/4 resuelto:** va al controlador VD/imager (`0xf3120000`), no es un comando por bus al IMX210; 3 y 4 difieren en `+0x208` bit 0, `+0x258` y una llamada virtual (§5).
* **`G+0x60/+0x7e/+0x7f`: no hay ningún escritor** que los active (solo lectores y un clear de `+0x7e`).

## 2. W1 y plan+0x142 (P0, P1)

Mapa de la copia `0x438acc40..0x438accfc` (V, `plan142.py`): `cap[0x74c]=plan[0x13f]`, `74d=plan[0x140]`, `74e=plan[0x141]`, `74f=plan[0x142]`.

Ramas del constructor `0x438ab3e8` (r4 = plan): `strh r0,[r4,#0x13e]=lookup(0x4389a018)`, `[0x140]=lookup(0x4387b520)`, `[0x142]=2×lookup(0x4387b520)` (stores en `0x438ab824, 0x438ab8be, 0x438abcbe, 0x438abd56, 0x438ac1f0, 0x438ac28c, 0x438ac7c8, 0x438ac85c`), `[0x146]=lookup(0x4387b5dc)`. Con ellas, `cap[74c]=0`, `cap[74d]=lookup` (puede ser 1 ✓) y `cap[74e]=0` ✓, pero **`cap[74f]` = 2×lookup mod 256 = par**. Un 1 en `74f` es imposible por W1 (V). El valor de las tablas de configuración (`r7+0x550…`) no se evaluó.

**Alias (A):** W1 escribe el objeto devuelto por `0x43b13b2c` = `0x43ae9226([mgr+0x4a5c], id 0x9405)` (búsqueda por ID en una tabla de entradas de 12 B). El `cap` en vuelo es una **copia** (`0x437f0978 bl 0x4378764c(pool, r4)`, con `r4=[M]=0x43ae75dc(r0)`, luego `0x4381ba9c` fija `[M']=copia`). Que el objeto 0x9405 sea `r4` **no está demostrado**; tampoco que W1 corra antes de la copia. Veredicto A: no demostrado.

## 3. Otros escritores y lectura física (P2, P5)

| Sitio | Qué escribe en `74e` | En foto normal |
|---|---|---|
| `0x4354c868` (`0x4354c6d0`, modo 0xa) | alto de la tabla global (240/288) | **descartado**: nunca da `0x0100` |
| `0x4354af88` (`EndExps` bloque 1) | `cap[0x19c]` y pone `cap+0xc30/0xc34/0xd54=1` | **descartado (F)**: `cap[0x19a..0x19d]=0` y `0xc30/0xd54=0` en vuelo y al terminar |
| `0x4354b0ac` (`EndExps` bloque 2) | `sp+0x312` (geometría de `0x43af54d8/0x43af5504`, usa `cap+0x19a/0x19c/0x1dc/0x1e0`) | **candidato**, valor sin evaluar |
| `0x439c80xx` | otro objeto | sin alias |

Lectura física (F, `cap=0x952db580`, 2 fotos de 4 s, cadena `gestor→M→[M]→cap`; originales T050 íntegros; `G`/tabla idénticos antes y después):

* `cap+0x74c..0x74f` = `00 01 00 01` durante toda la exposición y `00 00 00 01` en la última muestra (tras acabar). **`74f=1` en todas las muestras; `74d` pasa de 1 a 0.** Coincide con 19b (`cap-2s/4s/8s`: mismos dos estados).
* `cap+0x744=04`, `0x748/74a/750..757=0`, `cap+0x19a..0x19d=0`, `cap+0x1a0=0x0001`, `cap+0x1d8=0`, `cap+0x4fd0=0`.
* La transición `74d: 1→0` ocurre al terminar, compatible con `EndExps` (VD_Post de fin de exposición) con `74c←0` y `74e←0x0100`. **Es una inferencia**: no se ha visto el store.
* No se vieron las primeras fracciones de segundo de la petición (primera muestra a ≈1,3–3,5 s): el orden W1→copia→secuenciador no está observado.

## 4. Global G (P3)

`G=0x43e95950` solo se alcanza por el slot GOT `0x4402546c` (offset `0x6588`); ningún otro slot GOT apunta dentro de `G-0x100..G+0x200` salvo `G+0x100/+0x180`, y no hay literales directos ni `movw/movt` a `G`. Barrido de `campos_g.py` (patrón `ldr [pc]`=0x6588 → `ldr rY,[rPIC,rX]` → accesos en ventana de 260 instrucciones):

| Campo | Escritor | Valor | Condición | Consumidor | Evidencia |
|---|---|---|---|---|---|
| `G+0x60` | **ninguno** | — | — | `0x438c83d8` (selector 3/4: 0→4, ≠0→3) | V; `0x438cc95e` (`[r4+0x1e8]+0x60`) y `0x438146c8` (datos) son falsos positivos |
| `G+0x7e` | solo `0x438c2724` → 0 | 0 | tras gestionar la petición | `0x438c254e`, `0x438c26ac`, `0x438c26d4` | V |
| `G+0x7f` | **ninguno** | — | — | `0x438c2554`, `0x438c26da` (compara con `cap[0x1d8]`) | V |

En reposo (F) `G+0x58..+0x87` = 0 y no cambia durante una foto normal. Semántica: consumidor confirmado (`7e≠0` y `7f==cap[0x1d8]` ⇒ `74f←0`; `7e∈{1,2,3}` ⇒ avisa/cap y limpia `7e`); **quién activa `7e`/`7f`/`+0x60` no existe en el binario por esta vía** (I: lo escribe código no alcanzado por el patrón, o se rellena fuera de BIONZ). Preguntas A–E: A `G+0x60` = selector, sin productor; B/C sin productor; D consumidor sí, productor no; E `7e` se limpia en `0x438c2724`, los otros no se limpian. No se provocó cancelación.

## 5. Selector 3/4 (P4)

Cadena (V): `0x438c83ce` fija `r6` (4 si `74f≠0` ∧ `G+0x60==0`; si no 3) → `0x43795dec(r6, cap+0x548, r8, …)` → `0x43ad3b92(obj=0x436c2270(), sel, blk, …)` → `0x436c74c8(obj, sel, blk+0x24, blk+0x28, …)`. `obj` es el singleton del **controlador VD/imager** (base `0xf3120000`, `[obj+4]`; S46/S55).

`0x436c74c8`: guarda `sel` en `obj+0x20`, **omite el trabajo si `sel` es igual al anterior y ≤2** (3 y 4 siempre se reejecutan) y despacha con `tbb` sobre `sel-1` (tabla `0x436c75d2/7672/76e0/770a`).

| | sel 3 | sel 4 |
|---|---|---|
| común | `0x436c72e4`: `[0xf3120000+0x38]` bit0←0; `0x43ad381e` ×2 (otros dos periféricos, `+0x38` bit0←0); `[base+0x224]←obj+0x34`; `[base+0x220]←(obj+0x34)<<16 \| obj+0x38`; ventana `0x43ad3952`; `+0x38`… | igual |
| `base+0x208` bit0 | **1** | **0** |
| `base+0x258` | **0** | **1** |
| tras la ventana | omite la llamada virtual (`r7≠0`) | `[vtbl+0x14](obj)`; si ≠0 → `0x43ad390c(base,1,0,0)` y retorno `0x108` |

Con `74f=0` el selector siempre es 3. Así: el 3/4 **no es un comando al sensor ni toca `SetExposure/SetRead`**; configura el generador de temporización VD/imager de BIONZ (ventana `+0x220`, `+0x224`, y los bits de modo `+0x208`/`+0x258`). Si esos bits cambian el reset de filas, el inicio de integración o la lectura **no se demostró** (sin hoja de datos; S46 §124 los vincula al «cierre de integración/cortinas» como hipótesis). Último sumidero confirmado: stores MMIO `[0xf3120000+{0x208,0x220,0x224,0x258}]` por `0x43ad2bbc/2bd6/2be0/2bfc`.

## 6. Cronología del campo (P6)

| Etapa | Valor de `74f` | Fuente | Evidencia |
|---|---|---|---|
| construcción del plan `0x438ab3e8` | `plan[0x142]` par | 2×lookup | V |
| W1 (`0x438acc9c`) en objeto id 0x9405 | par | copia | V; alias con el `cap` no probado |
| copia por petición `0x4378764c` / `[M']` | heredado | copia de `[M]` | V (19b) |
| secuenciadores `0x4354…` | `0x0100` posible | strh `74e` | candidato, no observado |
| primera muestra física (≈1–3 s) | **1** | — | F |
| subestado 9 (toda la espera) | **1** (`74d=1`) | — | F |
| fin (`EndExps`?) | **1** (`74d=0`) | inferido | F, I |
| W2/W3 | 0 | arranque rechazado / cancelación | V, no observados |

## 7. Veredictos (P8)

| | Resp. | Prueba / incertidumbre |
|---|---|---|
| A. ¿W1 escribe el `cap` activo? | **NO demostrado** | escribe el objeto id 0x9405; el activo es una copia (§2) |
| B. ¿origen real de `plan+0x142`? | **SÍ** | `2×lookup(0x4387b520)` en 8/8 ramas; falta el valor de tabla |
| C. ¿W1 puede copiar 1? | **NO** | `lsls #1` ⇒ par (V) |
| D. ¿escritura indirecta que alcanza `74f`? | **SÍ** | 3 `strh@74e` (+5 de otro objeto); ninguno demostrado como productor del 1 |
| E. ¿`74f=1` explicado por completo? | **NO** | falta evaluar `0x4354b0ac` y ver el orden inicial |
| F. ¿escritor de `G+0x60`? | **NO** | ninguno |
| G. ¿de `G+0x7e`? | **Parcial** | solo el clear `0x438c2724` |
| H. ¿de `G+0x7f`? | **NO** | ninguno |
| I. ¿semántica de cancelación? | **Parcial** | consumidor ✓, productor ✗ |
| J. ¿argumento 3/4 decodificado? | **SÍ** | §5 |
| K. ¿destino sensor? | **NO como comando; SÍ hardware** | controlador VD/imager `0xf3120000` (MMIO), no bus al IMX210 |
| L. ¿modifica integración? | **NO demostrado** | cambia bits de modo del VD; efecto físico sin medir |
| M. ¿fin electrónico de integración? | **NO** | no hallado |
| N. ¿host auxiliar de error/cancelación? | **SÍ** | decisión B de 19d se mantiene |
| O. ¿lecturas físicas? | **SÍ** | reposo + 2 fotos de 4 s |
| P. ¿cámara sin modificar? | **SÍ** | solo `/dev/mem` lectura, T050 íntegros; se fijó 4 s por RemoteShutter y se hicieron 2 fotos normales |
| Q. ¿siguiente experimento mínimo? | **SÍ** | §8 |

## 8. Decisión y siguiente paso

**B — Destino 3/4 resuelto** (controlador VD/imager, bits `+0x208`/`+0x258` y llamada virtual; sin comando al sensor). **El origen del 1 queda en D (bloqueo mínimo):** W1 queda excluido; el candidato es el store `0x4354b0ac` de `EndExps`, cuyo valor depende de `0x43af54d8/0x43af5504` y de `cap+0x19a/0x19c/0x1dc/0x1e0/0x51c/0x525`. Para Silent: no cambia la conclusión (host auxiliar, sin integración electrónica demostrada); además `74f` puede ser parte de una altura, no un flag.

Siguiente mínimo (sin escribir nada): una lectura en vuelo de `cap+0x190..0x200` y `+0x510..0x530` en una foto normal, y emular con Unicorn `0x43af54d8` para obtener `sp+0x30c..0x31a`; si `sp+0x312=0x0100` queda explicado el 1 final. Para ver el estado inicial haría falta muestrear antes de ≈1 s (no logrado: la cadena `[M]` aparece tras ≈1,3–3,5 s).

Límites: sin Unicorn de `0x438ab3e8`; tablas de configuración de `plan` no evaluadas; no se leyó el objeto id 0x9405; sin hoja de datos del VD; `G` solo por GOT.
