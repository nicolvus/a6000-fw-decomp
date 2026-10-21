# S111 — Módulo de trazas `[TRK]` (A6000 fw3.21)

**Alcance.** Reconstruir la estructura del módulo `[TRK]` a partir de sus cadenas y de
las referencias PIC que las cargan: cuántas son, en qué sub-bloques se agrupan, qué
funciones las emiten, en qué zona del firmware viven esas funciones y en qué se
diferencia la A7S. No se re-deriva la semántica de FRC/DETSA/EDTSA/IRO2G/PMV/STK/BT
(eso está en `analysis/s71_frc/frc_subsystem.md` §5); aquí se fija el inventario y la
topología de código.

**Método.** Solo bytes de `analysis/rea-independent/input/av-cam.bin` (vaddr =
`0x43541000` + offset). Sin ejecutar firmware, sin cámara, sin REA/Ghidra. Cada
afirmación de este informe se apoya en un sitio `add rX, pc` cuyo destino coincide
**exactamente** con una cadena `[TRK]`; los agregados están en `trk.json` y los sitios
individuales en `refs.json`.

## 1. Cifras verificadas

| Métrica | Valor | Evidencia |
|---|---|---|
| Ocurrencias del literal `[TRK` | **216** | `scan_strings.py` |
| Inicios de cadena | **215** | la ocurrencia extra es el segundo `[TRK` de `0x43cfda0e` |
| Textos distintos | **207** | 8 textos `[STK] PARAM ERR - box …` repetidos ×2 |
| Cadenas referenciadas por PIC | **213** | 288 parejas `ldr`→`add` |
| Sitios de referencia | **288** | 283 `strict` + 5 `relaxed`, 0 sin dueño |
| Funciones emisoras | **47** | 45 con dueño `strict` + 2 `relaxed` |
| Rango de las cadenas | `0x43cebceb`–`0x43cfe31c` | `[CAM INIT]` … `[BT] ddl_saCalcCancel` |
| Nombres de fuente embebidos `FC/*.cpp` | **99** | `0x43cef12a`–`0x43cf707a` |

Las dos cadenas sin referencia PIC son `0x43cfb3e9` `"[TRK]: [EDTSA] Stop Message Alloc
Error"` y `0x43cfc7ea` `"[TRK]: [STK] Stop Message Alloc Error"`. Tampoco tienen
literal absoluto ni `adr`, y los únicos pares `ldr`→`add` que las alcanzarían recargan
el registro entre medias (`0x43a32a4c`, `0x43a32b5c` para la segunda) → no se aceptan.
Se reportan como **sin referencia PIC**, no como código muerto demostrado.

## 2. Corrección metodológica (importante para hitos previos)

La primera pasada emparejaba cada `add rX, pc` con **cualquier** `ldr rX` anterior
dentro de una ventana de `0x1000` B. Eso produce referencias falsas cuando el registro
se recarga: el `add` solo puede usar el **último** `ldr` del mismo registro.

| Regla | Sitios | Cadenas |
|---|---|---|
| ventana `MAX_GAP=0x1000` (descartada) | 330 | 214 |
| solo el `ldr` más reciente, `MAX_GAP=0x40` (S111) | **288** | **213** |

Se eliminan **42 sitios espurios**. Los 288 válidos tienen separación `site - ldr`
entre 2 y 14 B (4 B: 105, 8 B: 75, 10 B: 47, 6 B: 43, 2 B: 8, 12 B: 8, 14 B: 2), muy
por debajo del límite. Consecuencia: `sa_stubs`, `fc` y `apl_osal` quedan con **0
sitios**; las cifras anteriores de esas zonas eran artefactos de la pasada amplia.

Caso demostrativo: `0x43a37c06` **no** referencia `"[BT] cmn.af_rect_thres:%d"`
(`0x43cfe135`). Su `add` usa el `ldr` `0x43a37c00` (pool `0x43a37ce8`, valor
`0x52965a`), que calcula `0x43f61264`: no es ninguna cadena `[TRK]`. La cadena la carga
`0x43a38720` (`ldr` `0x43a3871c`, pool `0x43a389b4`) dentro de `0x43a380ac`. Emparejar
hacia atrás fabricaba la referencia falsa.

## 3. Sub-bloques (215 cadenas / 288 sitios)

El prefijo de la traza decide el sub-bloque. Los rangos se solapan porque las cadenas
de los sub-bloques STK están intercaladas en el mismo pool; una misma función puede
emitir trazas de varios sub-bloques.

| Sub-bloque | Cadenas | Sitios | Funciones dueñas | Rango de cadenas |
|---|---:|---:|---:|---|
| sesión | 4 | 4 | 4 | `0x43cebceb`–`0x43cebd60` |
| DETSA | 9 | 9 | 3 | `0x43cfb27d`–`0x43cfb3ac` |
| EDTSA | 19 | 19 | 3 | `0x43cfb3c6`–`0x43cfb64d` |
| IRO2G | 13 | 13 | 4 | `0x43cfc363`–`0x43cfc505` |
| PMV | 16 | 16 | 4 | `0x43cfc51f`–`0x43cfc7a5` |
| STK | 76 | 145 | 8 | `0x43cfc7c9`–`0x43cfd8ad` |
| STK_AUTO_SAL | 4 | 4 | 1 | `0x43cfc9cb`–`0x43cfd2f5` |
| STK_COLOR_SIM | 3 | 3 | 1 | `0x43cfd324`–`0x43cfd635` |
| STK_C_SIM | 1 | 1 | 1 | `0x43cfd380` |
| STK_TOUCH_SIM | 3 | 3 | 1 | `0x43cfd668`–`0x43cfd8ed` |
| STK_T_SIM | 1 | 1 | 1 | `0x43cfd6c4` |
| VAE | 3 | 3 | 2 | `0x43cfd920`–`0x43cfd956` |
| VAT | 3 | 3 | 2 | `0x43cfd970`–`0x43cfd9a5` |
| VOT | 3 | 3 | 2 | `0x43cfd9bf`–`0x43cfd9f2` |
| motor | 5 | 5 | 4 | `0x43cfda0e`–`0x43cfda90` |
| BT | 44 | 48 | 6 | `0x43cfdabb`–`0x43cfe31c` |
| TIMER | 8 | 8 | 5 | `0x43cfdb00`–`0x43cfdcf8` |
| **Total** | **215** | **288** | **47 únicas** | |

La columna de funciones suma 52 porque `0x43a36a06`, `0x43a3588e` y `0x43a36156`
emiten varias familias STK a la vez; las funciones únicas son 47.

Ejemplos por bloque (cita textual y vaddr):

- **sesión** — `0x43cebceb` `"[TRK]: [CAM INIT] Message Alloc Error"`,
  `0x43cebd60` `"[TRK]: [VSYNC CLOSE] Message Alloc Error"`. Cuatro wrappers
  independientes, uno por evento.
- **DETSA** — `0x43cfb304` `"[TRK]: [DETSA] CORE2 RESOURCE CONTENTION : %d"`,
  `0x43cfb332` `"[TRK]: [DETSA] PARAM ERR !! face_num : %d"`.
- **EDTSA** — `0x43cfb479` `"[TRK]: [EDTSA] CORE3 RESOURCE CONTENTION : %d"`,
  `0x43cfb5ea` `"[TRK]: [EDTSA] hue_range : %d"`.
- **IRO2G** — `0x43cfc45f` `"[TRK]: [IRO2G] ALIGNMENT ERR : %d"`,
  `0x43cfc4bc` `"[TRK]: [IRO2G] ValidWidth ERR : %d"`.
- **PMV** — `0x43cfc6e6` `"[TRK]: [PMV] Param Affine_err_thresh ERR : %d, %d"`,
  `0x43cfc718` `"[TRK]: [PMV] Param Vector_thresh ERR : %d, %d, %d"`.
- **STK** — `0x43cfc810` `"[TRK]: [STK] Saliency CB is NULL (COMP)"`,
  `0x43cfcf09` `"[TRK]: [STK] PARAM ERR - box af_island_num : %d"`.
- **motor** — `0x43cfda0e` `"[TRK]: [TRK] cb_func == NULL"` (dos `[TRK` en la misma
  cadena), `0x43cfda4d` `"[TRK]: CAM MODE IS ALREADY OPEN!"`.
- **BT** — `0x43cfdf82` `"[TRK]: [BT] fg_area : %d, %d, %d, %d"`,
  `0x43cfe098` `"[TRK]: [BT] cmn.min/max_bayes_map_level:%d, %d"`,
  `0x43cfe31c` `"[TRK]: [BT] ddl_saCalcCancel:%d"`.
- **TIMER** — `0x43cfdb88` `"[TRK]: osal_alloc_timer(): %d"`,
  `0x43cfdcf8` `"[TRK]: osal_can_timer(): %d"`.

## 4. Funciones emisoras (47)

Atribución por prólogo `push {..,lr}` / `push.w {..,lr}` y cierre en el primer
`pop {..,pc}` / `bx lr`. `strict` = el sitio cae dentro de `[inicio, fin)`;
`relaxed` = no cae, pero hay un prólogo a ≤`0x4000` B por detrás (colas de error tras
un retorno temprano o tail-call `b.w`). `fin = —` significa que el cierre calculado
queda antes del último sitio: los límites exactos de esa función no están verificados.

| # | Inicio | Fin | Cadenas | Sitios | Sub-bloques |
|---:|---|---|---:|---:|---|
| 1 | `0x43a36a06` | `0x43a37288` | 53 | 53 | STK, STK_TOUCH_SIM, STK_T_SIM |
| 2 | `0x43a3588e` | `0x43a3612c` | 48 | 48 | STK, STK_AUTO_SAL |
| 3 | `0x43a36156` | `0x43a36946` | 45 | 45 | STK, STK_COLOR_SIM, STK_C_SIM |
| 4 | `0x43a380ac` | `0x43a38950` | 34 | 38 | BT |
| 5 | `0x43a3059c` | `0x43a308ec` | 15 | 16 | EDTSA |
| 6 | `0x43a34f5c` | `0x43a35350` | 13 | 13 | PMV |
| 7 | `0x43a347d8` | `0x43a34990` | 8 | 8 | IRO2G |
| 8 | `0x43a301e4` | `0x43a303c6` | 6 | 6 | DETSA |
| 9 | `0x43a37f08` | `0x43a3809a` | 4 | 4 | BT |
| 10 | `0x43a34680` | `0x43a347be` | 3 | 3 | IRO2G |
| 11 | `0x43a3541c` | `0x43a355bc` | 3 | 3 | STK (callback saliency) |
| 12 | `0x43a355d0` | `0x43a3573e` | 3 | 3 | STK (callback touch) |
| 13 | `0x43a3574c` | `0x43a3587e` | 3 | 3 | STK (callback color) |
| 14 | `0x43a37ea4` | — | 3 | 3 | BT (abort, `relaxed`) |
| 15 | `0x43a300f4` | `0x43a301d0` | 2 | 2 | DETSA |
| 16 | `0x43a3046c` | `0x43a3056e` | 2 | 2 | EDTSA |
| 17 | `0x43a373dc` | `0x43a3742e` | 2 | 2 | VAE (alloc) |
| 18 | `0x43a37474` | `0x43a374c8` | 2 | 2 | VAT (alloc) |
| 19 | `0x43a37518` | `0x43a3756c` | 2 | 2 | VOT (alloc) |
| 20 | `0x43a375d8` | — | 2 | 2 | motor (`relaxed`) |
| 21 | `0x43a37bb8` | `0x43a37bf2` | 2 | 2 | TIMER (`almhdl`) |
| 22 | `0x43a37c02` | `0x43a37ce2` | 2 | 2 | TIMER (osal alloc) |
| 23 | `0x43a37d0c` | `0x43a37db2` | 2 | 2 | TIMER (osal free/set/can) |
| 24 | `0x439ce7d8` | `0x439ce808` | 1 | 1 | sesión (CAM INIT) |
| 25 | `0x439ce80c` | `0x439ce83c` | 1 | 1 | sesión (CAM CLOSE) |
| 26 | `0x439ce840` | `0x439ce872` | 1 | 1 | sesión (VSYNC OPEN) |
| 27 | `0x439ce878` | `0x439ce8ae` | 1 | 1 | sesión (VSYNC CLOSE) |
| 28 | `0x43a300ac` | `0x43a300ee` | 1 | 1 | DETSA |
| 29 | `0x43a303f8` | `0x43a30466` | 1 | 1 | EDTSA |
| 30 | `0x43a345f4` | `0x43a3463e` | 1 | 1 | IRO2G |
| 31 | `0x43a34644` | `0x43a3467a` | 1 | 1 | IRO2G |
| 32 | `0x43a34dbc` | `0x43a34dfe` | 1 | 1 | PMV |
| 33 | `0x43a34e04` | `0x43a34e3a` | 1 | 1 | PMV |
| 34 | `0x43a34e40` | `0x43a34f46` | 1 | 1 | PMV |
| 35 | `0x43a35384` | `0x43a353cc` | 1 | 1 | STK |
| 36 | `0x43a353d0` | `0x43a35418` | 1 | 1 | STK |
| 37 | `0x43a37450` | `0x43a3746a` | 1 | 1 | VAE (free) |
| 38 | `0x43a374e4` | `0x43a374fe` | 1 | 1 | VAT (free) |
| 39 | `0x43a37584` | `0x43a3759e` | 1 | 1 | VOT (free) |
| 40 | `0x43a376d8` | `0x43a3786e` | 1 | 1 | motor (CAM MODE open) |
| 41 | `0x43a37734` | `0x43a3786e` | 1 | 1 | motor (CAM MODE close) |
| 42 | `0x43a37874` | `0x43a37970` | 1 | 1 | motor (Vsync close) |
| 43 | `0x43a379dc` | `0x43a37a42` | 1 | 1 | BT |
| 44 | `0x43a37a48` | `0x43a37a7e` | 1 | 1 | BT |
| 45 | `0x43a37dd6` | `0x43a37e14` | 1 | 1 | TIMER (`osal_set_timer`) |
| 46 | `0x43a37e2c` | `0x43a37e7a` | 1 | 1 | TIMER (`osal_can_timer`) |
| 47 | `0x43a389f0` | `0x43a38a60` | 1 | 1 | BT (`ddl_saCalcCancel`) |

Las etiquetas de papel entre paréntesis se infieren **solo** de las cadenas que la
función carga (p. ej. `0x43a373dc` carga `"Vae_Work Alloc_Error"`); no se atribuye
comportamiento no observado.

Las funciones 40 y 41 comparten `fin = 0x43a3786e` porque el prólogo de la segunda
está anidado en el cuerpo de la primera: los límites exactos de ambas son **NO
VERIFICADO**. Las funciones 14 y 20 son colas tras un retorno temprano
(`pop {r4,pc}` en `0x43a375e2`; `pop.w {r4,r5,r6,lr}` en `0x43a37ec8`), no funciones
distintas mal atribuidas. Caso límite de la regla: `0x43a37c02` tiene su `ldr` en
`0x43a37c00`, 2 B **antes** del prólogo; el `add` de `0x43a37c06` lo usa igualmente
porque el `push.w {r4-r8,lr}` de `0x43a37c02` no toca `r1`.

## 5. Zonas de código

| Zona | Rango | Sitios | Funciones | Interpretación |
|---|---|---:|---:|---|
| `trk_face` | `0x43a30000`–`0x43a39000` | **284** | **43** | módulo `[TRK]` propio |
| `apl_sa` | `0x439c0000`–`0x439d0000` | **4** | **4** | wrappers de sesión `[CAM INIT/CLOSE]`, `[VSYNC OPEN/CLOSE]` |
| `sa_stubs` | `0x43a1a000`–`0x43a1e000` | 0 | 0 | sin sitios con la regla corregida |
| `fc` | `0x437c0000`–`0x437d0000` | 0 | 0 | sin sitios verificados |
| `apl_osal` | `0x439d0000`–`0x439e0000` | 0 | 0 | sin sitios verificados (los temporizadores viven en `trk_face`) |

El módulo es, por tanto, **una sola región de código contigua** más cuatro wrappers
de sesión en la capa APL/SA. El barrido PIC de `0x43541000`–`0x43ceb000` no devuelve
sitios `[TRK]` fuera de esas dos zonas.

## 6. Nombres de fuente embebidos

99 cadenas `FC/<dir>/<fichero>.cpp` en `0x43cef12a`–`0x43cf707a`. Las que casan con
los sub-bloques:

| Fichero | vaddr |
|---|---|
| `FC/Api/fc_api_tracking.cpp` | `0x43cefa43` |
| `FC/Alg/fc_alg_tracking.cpp` | `0x43cf0472` |
| `FC/Drv/fc_drv_detsa.cpp` | `0x43cf03fa` |
| `FC/Drv/fc_drv_vat.cpp` | `0x43cf03e4` |
| `FC/Drv/fc_drv_vae.cpp` | `0x43cf06d1` |
| `FC/Seq/fc_seq_touch.cpp` | `0x43cf082f` |
| `FC/Drv/fc_drv_bt.cpp` | `0x43cf603a` |
| `FC/Drv/fc_drv_stk.cpp` | `0x43cf627a` |
| `FC/Seq/fc_seq_pmv.cpp` | `0x43cf697b` |
| `FC/Drv/fc_drv_edt.cpp` | `0x43cf6fd9` |
| `FC/Drv/fc_drv_iro2g.cpp` | `0x43cf7044` |
| `FC/Drv/fc_drv_pmv.cpp` | `0x43cf707a` |

La correspondencia fichero↔función **no** está establecida: los nombres están en un
pool común y no se ha verificado qué unidad compiló cada función. Solo se afirma que
el módulo declara esos ficheros.

## 7. Relación con otros hitos

- **S71 (FRC)** ya fijó la lectura semántica de DETSA/EDTSA/IRO2G/PMV/STK/BT a partir
  de sus parámetros (`CORE2/CORE3 RESOURCE CONTENTION`, `bayes_map_level`,
  `Affine_err_thresh`, `p_saliency`…). S111 **no la contradice ni la repite**: añade el
  conjunto exacto de cadenas, la pareja `ldr`→`add` de cada una, la función dueña y la
  zona de código. Las citas de S71 siguen siendo la referencia para el significado.
- **Imager / cara**: las 215 cadenas viven en `0x43cebceb`–`0x43cfe31c`, en el pool de
  datos del módulo; el barrido `0x43541000`–`0x43ceb000` no encuentra sitios `[TRK]`
  fuera de `trk_face` y `apl_sa`. DETSA/EDTSA son los únicos sub-bloques con vocabulario
  de cara (`face`, `angle`, `hue_range`), pero S111 no añade semántica nueva sobre el
  detector.
- **S106 (`[IMAGING_CAP]`)**: módulo distinto por prefijo y por rango
  (`0x43c9b335`–`0x43ccab72`), sin solapamiento con `[TRK]`. S106 usa un emparejamiento
  PIC más laxo (todos los `ldr` del registro); S111 exige el más reciente. La
  diferencia no invalida S106: son reglas distintas y S111 solo acepta coincidencia
  exacta con una cadena `[TRK]`.
- **S79 (`module_map.json`)**: confirma 216 ocurrencias `[TRK]` en A6000 y 216 en A7S;
  S111 desglosa esas ocurrencias en 215 cadenas y 288 sitios.

## 8. Diferencial A6000 fw3.21 / A7S fw3.20

| Métrica | A6000 | A7S |
|---|---:|---:|
| Ocurrencias / cadenas | 216 / 215 | 216 / 215 |
| Cadenas referenciadas | 213 | 213 |
| Sitios | 288 | 288 |
| `strict` / `relaxed` | 283 / 5 | 284 / 4 |
| Funciones | 47 | 47 |
| Rango de cadenas | `0x43cebceb`–`0x43cfe31c` | `0x43ce1492`–`0x43cee615` |
| Primera función de sesión | `0x439ce7d8` | `0x439bcbd4` |
| Última función emisora | `0x43a389f0` | `0x43a1dbe4` |

`identical_texts = true` y `identical_multiset = true`: **mismos 215 inicios de cadena y
mismo multiconjunto de textos**; `only_a6000` y `only_a7s` vacíos. El módulo es común a la
familia, con direcciones de código distintas (el bloque `trk_face` de la A7S está
desplazado). La única diferencia estructural es 284/4 frente a 283/5: un sitio que en
A6000 cae en cola `relaxed` queda dentro de una función `strict` en A7S.

## 9. NO VERIFICADO / abierto

1. **Límites exactos** de `0x43a376d8` y `0x43a37734` (comparten `fin` por prólogo
   anidado) y de las dos funciones `relaxed` (`0x43a37ea4`, `0x43a375d8`, `fin = —`).
2. **Código muerto**: las dos cadenas sin referencia (`0x43cfb3e9`, `0x43cfc7ea`) no
   tienen PIC, literal absoluto ni `adr`; no se ha demostrado que sean inalcanzables
   (podrían cargarse por una tabla no escaneada).
3. **Identidad de `sa_stubs`** (zona ZIT de S80): 0 sitios tras la corrección; no se
   afirma ni se niega que esos stubs pertenezcan a DETSA/EDTSA.
4. **Fichero fuente por función**: los 99 `FC/*.cpp` están inventariados, pero no se ha
   verificado la unidad de compilación de cada función.
5. **Semántica de siglas** VAE/VAT/VOT más allá de sus trazas (`Alloc`, `Free`,
   `RefMap`); no se amplía lo ya dicho en S71.
6. **Verificación dinámica**: nada de esto se ha ejecutado en cámara ni en emulador.
7. **Build de producción**: no se sabe si estas trazas se compilan fuera en release.

## 10. Reproducción

```
.venv/bin/python analysis/s111_trk/scan_strings.py
.venv/bin/python analysis/s111_trk/scan_refs.py
.venv/bin/python analysis/s111_trk/scan_a7s.py
.venv/bin/python analysis/s111_trk/build_trk.py
.venv/bin/python -m pytest tests/test_s111_trk.py
```

Artefactos: `strings_raw.json`, `refs.json`, `a7s_diff.json`, `trk.json`.
Los escáneres usan la regla nearest-`ldr` (`MAX_GAP=0x40`); no reutilizar los números
de la primera pasada (`330`/`214`).

## 11. Revisión del agente principal

_(Pendiente; este informe no ha sido revisado por el agente principal.)_
