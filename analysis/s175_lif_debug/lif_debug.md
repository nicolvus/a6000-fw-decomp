# S175 — el módulo `[LIF_DEBUG]` (13 trazas): el diagnóstico del sensor de luz de la cámara

> Hito de la **línea de ingeniería inversa general**. Solo bytes de la A6000 fw3.21
> (`analysis/rea-independent/input/av-cam.bin`), con la A7S fw3.20 y el A6300 fw2.01 como
> comparación. Convención: `vaddr = 0x43541000 + file_offset`. Regla de referencias:
> **estricta** (mapa global en `analysis/s106_imaging_cap/pic_refs_strict_global.json`).

## 1. Resumen / veredicto

`[LIF_DEBUG]` es la traza de diagnóstico del **subsistema de sensor de luz de la cámara**
(`CAM LIF SENSER`): su inicialización, el registro/desregistro de los *callbacks* de **backup**
(`BK`, con identificador `BKID`) y las **copias «shadow»** entre el estado de *backup* y el
«shadow». Es el último de los 17 módulos «de contenido nuevo» que S130 identificó.

| etiqueta | cadenas | A6000 | A7S | A6300 | sitios PIC | funciones |
|---|---|---|---|---|---|---|
| `[LIF_DEBUG]` | 13 | 13 | **0** | **0** | 14 | 3 |

**Las 13 cadenas están vivas** (0 muertas) con **14 sitios** en **3 funciones** muy contiguas
(`0x43a1c9d8`, `0x43a1cb0c`, `0x43a1cb3c`) y usan un **logger propio con id `0x125`**
(`0x43a1c92c`), igual que hizo `[TP_R]` (S156) y `[SAD]` (S167).

**Base textual**: los nombres de las dos funciones de copia aparecen **solo dentro de las propias
trazas** (`cam_lif_senser_copy_bk2shadow` `0x43cfb14d`, `cam_lif_senser_copy_shadow2bk`
`0x43cfb18a`): hay **0** apariciones como símbolo independiente, así que **no** son símbolos
resueltos por el enlazador sino **texto literal**.

## 2. Las 13 cadenas y sus sitios

| # | cadena | sitio(s) | función | qué informa |
|---|---|---|---|---|
| 1 | `[LIF_DEBUG]: Finish BK CB ` | `0x43a1c9f2` | `0x43a1c9d8` | fin de un *callback* de backup |
| 2 | `[LIF_DEBUG]:  :[BKID] %x, [DataSize] %x` | `0x43a1ca02` | `0x43a1c9d8` | id de backup y tamaño del dato |
| 3 | `[LIF_DEBUG]: Start CAM LIF SENSER Init` | `0x43a1ca28` | `0x43a1ca18` | arranque de la inicialización del sensor de luz |
| 4 | `[LIF_DEBUG]: Reg CB func result [BKID]:%x, [Erro]:%x` | `0x43a1ca9c` | `0x43a1ca18` | resultado de registrar el *callback* |
| 5 | `[LIF_DEBUG]:  ::[Count]:%x` | `0x43a1ca80`, `0x43a1cb7a` | `0x43a1ca18`, `0x43a1cb3c` | número de elementos copiados |
| 6 | `[LIF_DEBUG]:  ::[HandleValue]:%x` | `0x43a1cac8` | `0x43a1ca18` | valor del *handle* |
| 7 | `[LIF_DEBUG]: Finish Reg CB func ` | `0x43a1cb20` | `0x43a1cb0c` | fin del registro del *callback* |
| 8 | `[LIF_DEBUG]: Finish BK2Shadow @cam_lif_senser_copy_bk2shadow` | `0x43a1cac8`… | `0x43a1ca18` | fin de la copia backup→shadow |
| 9 | `[LIF_DEBUG]: Finish Shadow2BK @cam_lif_senser_copy_shadow2bk` | `0x43a1cb94` | `0x43a1cb3c` | fin de la copia shadow→backup |
| 10 | `[LIF_DEBUG]: UnReg CB func result [BKID]:%x, [Erro]:%x` | `0x43a1cba8` | `0x43a1cb3c` | resultado de desregistrar el *callback* |
| 11 | `[LIF_DEBUG]:  ::[HandlerValue]:%x` | `0x43a1cbb8` | `0x43a1cb3c` | valor del *handler* |
| 12 | `[LIF_DEBUG]: Finish UnReg CB func ` | `0x43a1cba8`… | `0x43a1cb3c` | fin del desregistro |
| 13 | `[LIF_DEBUG]: CAM LIF Subsystem backup close` | `0x43a1cbb8` | `0x43a1cb3c` | cierre del *backup* del subsistema |

## 3. El logger propio (`0x43a1c92c`, id `0x125`)

```
0x43a1c92c: push   {r3}
0x43a1c938: mov     r7, r0              ; id de categoria  = 0x125 (293)
0x43a1c93a: mov     r8, r1              ; sub-id           = 0
0x43a1c93c: mov     sb, r2              ; nivel            = 3
0x43a1c946: movs    r2, #0x9a            ; tamano del mensaje OSAL
0x43a1c94a: bl      #0x435612d0          ; osal_try_valloc_msg
0x43a1c974: blx     #0x439c5a04          ; vsnprintf
0x43a1c97e: bl      #0x43561244          ; osal_send_msg
```

Todas las llamadas del módulo pasan `r0 = 0x125`, `r1 = 0`, `r2 = 3` → es un **canal de log
propio**, no el logger global `0x435ab880` que usan `[SFRA]`/`[SFRS]`.

## 4. Las dos funciones de copia «shadow»

* `0x43a1ca18` (`cam_lif_senser_copy_bk2shadow`): recorre **2** elementos (`cmp r7,#2` en
  `0x43a1caa2`), copia un bloque con `bl 0x435614d0` y llama a `bl 0x435613e8` al final.
* `0x43a1cb3c` (`cam_lif_senser_copy_shadow2bk`): simétrico, también **2** elementos
  (`cmp r4,#2` en `0x43a1cb9c`), con `bl 0x435614ec` por elemento.

Es un mecanismo de **copia de seguridad** del estado del sensor de luz: el «shadow» es la copia
de trabajo y el «BK» la copia de *backup*, y se sincronizan en ambos sentidos.

## 5. Diferencial

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[LIF_DEBUG]` | **13** | **0** | **0** |
| `LIF` (cualquier contexto) | 64 | 43 | 81 |
| `BKID` | 28 | 23 | 22 |
| `SENSER` | 12 | 7 | 8 |
| `cam_lif_senser_copy_bk2shadow` / `…shadow2bk` | 1 / 1 | **0** | **0** |

El **subsistema de sensor de luz existe en los tres firmware** (los contadores de `LIF`, `BKID` y
`SENSER` no son cero en ninguno); lo **propio de la fw3.21 de la A6000** es la **etiqueta** y los
dos **nombres de función escritos como texto** dentro de las trazas → otra vez el patrón de
S128/S130: **se reescribe el logging, no el firmware**.

**Salvedad** (S130 §4): la comparación mezcla versión de firmware y modelo.

## 6. Interés para la línea del obturador

**Negativo verificado**: las 13 cadenas hablan de **backup**, *callbacks*, *handles* y copias
«shadow»; no hay ninguna mención de obturador, disparo, lectura del sensor, exposición ni
tiempos → **sin efecto en S51** (A/B/C = NO).

## 7. NO VERIFICADO / abierto

1. Qué es exactamente el «BK» (backup) y quién registra los *callbacks* (el `BKID` es un id de
   *backup*, no se desarrolla).
2. Por qué el subsistema solo copia **2** elementos.
3. El significado de los ids `0x125` (categoría del log), `0x93`/`0xa1` y de los dos helpers
   `0x435613e8` / `0x435614d0` / `0x435614ec`.
4. Si el sensor de luz de la A6000 es el mismo que el de la A7S (los nombres son cero en la A7S,
   pero la función existe: **NO VERIFICADO**).

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s175_lif_debug.py -q
```

## 9. Revisión del agente principal

_(vacía)_
