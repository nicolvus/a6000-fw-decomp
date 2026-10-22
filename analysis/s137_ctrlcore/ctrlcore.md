# S137 — El token `[CTRLCORE]`: el núcleo de control de códec (Cd / McSens / AmSens)

> Milestone **S137** de la línea de ingeniería inversa **general** del firmware A6000 fw3.21.
> Todas las direcciones son **vaddr = 0x43541000 + file_offset** dentro de
> `analysis/rea-independent/input/av-cam.bin` y se han comprobado contra bytes con
> `analysis/s137_ctrlcore/scan_ctrlcore.py` y `verify_sites.py`.
> **Estado:** VERIFICADO = contra bytes · INFERENCIA = lectura razonada · NO_VERIFICADO = pendiente.

Artefactos: `ctrlcore.json` (datos estructurados), `ctrlcore_raw.json` (volcado del escáner),
`scan_ctrlcore.py`, `verify_sites.py`. Test: `tests/test_s137_ctrlcore.py`.

---

## 1. Resumen (VERIFICADO)

`[CTRLCORE]` **no es un módulo de primer nivel**: es una **sub-etiqueta de segundo nivel**,
igual que `[APL]` dentro de `[CAMERA_SA]` (S119). Aparece siempre detrás de un módulo
contenedor y designa la clase **núcleo de control (`*CtrlCore`)** de ese contenedor:

| prefijo contenedor | cadenas | clase(s) que la emiten |
|---|---|---|
| `[CDIAG][CTRLCORE]` (`[ERR]` incl.) | **51** | `CdCtrlCore` (12 funciones) |
| `[MCSENS][CTRLCORE]` | **1** | `McSensCtrlCore` (1 función) |
| `[AMSENS][CTRLCORE]` | **3** | `AmSensCtrlCore` (3 funciones) |

- **55 cadenas** con el token, en `0x43c3b82d`–`0x43cdb492`.
- **74 sitios PIC** que las referencian, **74/74 verificados de forma independiente**
  (regla **estricta**: se localiza el `ldr rX,[pc,#imm]` del mismo registro, se lee su
  literal `W` y se calcula `destino = W + (add + 4)`; los 74 textos coinciden).
- **16 funciones emisoras**, todas con prólogo Thumb `push {…,lr}`.
- **4 ficheros fuente** embebidos: `cdCtrlCore.cpp` `0x43c3b86c`,
  `mcSensCtrlCore.cpp` `0x43c73689`, `amSensCtrlCore.cpp` `0x43cdb45a`,
  `mcAvCtrlCore.cpp` `0x43c454e8` (este último sin cadena `[CTRLCORE]`).

## 2. Inventario de cadenas (VERIFICADO)

Reparto de las 51 de `[CDIAG]`: 2 guardas `p_prm is NULL`, `DbgDiagAvc` 4, `No Support
EXEC MODE` 1, `ConfirmDoneCodec` 4, `CmpData` 7, `RunCodec` 7, `RelMemArea` 7,
`SetMemArea` 7, `SetData` 6, trazas de despacho 3 (`ExecCmd !!`,
`ExecCmd !! ConfirmDoneCodec`, `ExecCmd !! [0x%04X] mode[…] func[…]`), `SetDiagMode` 2 y
el log de memoria `memIdx[%d] fileId[%02d:%02d] unitHandle[…] unitType[…] size[…]` 1.
Las 3 de `[AMSENS]`: 2 guardas (`is NULL` y `is NULL file[…] func[…] line[…]`) y
`[AMSENS][CTRLCORE][AVCE][PARAM] adr[0x%08X] size[%d]`; la de `[MCSENS]` es la guarda
larga `p_prm is NULL file[…] func[…] line[…]` `0x43c73649`.

**Escenarios** (idénticos a S109): `HD REC`, `HD DEC`, `SD REC`, `SD DEC`, `JPEG/JPG ENC`,
`JPEG DEC`, `JPEG ENCDEC`; **operaciones**: `DbgDiagAvc`, `ConfirmDoneCodec`, `CmpData`,
`RunCodec`, `RelMemArea`, `SetMemArea`, `SetData`, `SetDiagMode`.

## 3. Capas: `CdCtrlIf` despacha, `*CtrlCore` ejecuta (VERIFICADO)

El modelo correcto **no** es "`CdCtrlCore` despacha": los tres despachadores están en
`cdCtrlIf.cpp` (`0x43c3b1a8`) y llevan su propia firma embebida.

| función | vaddr | firma | guarda `line` | argumento |
|---|---|---|---|---|
| `CdCtrlIf::ExecCmd` | `0x435a1424` | `0x43c3b647` | `0xc2` | `CdCtrlIf::MSG_SENS_COMMAND*` |
| `CdCtrlIf::ExecSensCmd` | `0x435a15e8` | `0x43c3b688` | `0x41` | `(__uint32_t id, const OsalRequestPacket*, __uint32_t)` |
| `CdCtrlIf::ExecSensComp` | `0x435a17e8` | `0x43c3b688` | `0x12d` | `(__uint32_t id, OsalResponsePacket*, __uint32_t)` |

Guardas: formato `[%s] -- file[%s] func[%s] line[%d]` `0x43c3b176`; el `line` se carga con
`movs r3,#0xc2` en `0x435a142a`, `movs r3,#0x41` en `0x435a15f4` y `movw r3,#0x12d` en
`0x435a17f4`.

### 3.1 `ExecCmd` — comandos con estructura `MSG_SENS_COMMAND` (`0x435a1424`)

Lee `id` como `u16` en `[prm+0]`, `mode` en `+2`, `func` en `+3` y un `u32` en `+4`.

| id | acción | destino |
|---|---|---|
| 2 | `SetMemArea` | `0x435a2200` (`b.w` en `0x435a1482`) |
| 3 | `RelMemArea` | `0x435a20b0` (`b.w` en `0x435a14a2`) |
| `0x11` | `RunCodec` | `0x435a1f18` (`b.w` en `0x435a14c2`) |
| otro | log `[ERR][CDIAG][CTRLIF]NOT SUPPORTED…` `0x43c3b238`, `return 1` | — |

### 3.2 `ExecSensCmd` — comandos de mensajería OSAL (`0x435a15e8`)

`id` en `r5` (mitad baja de `r1`), sub-id en `r7` (`r1>>16`), paquete en `r4`.

| id | acción | destino |
|---|---|---|
| 1 | `SetDiagMode` | `0x435a2354` |
| 2, 3, `0x11` | construye **trama de 12 B** y la envía | `0x435a157c` |
| `0x12` | `CmpData` | `0x435a1de0` |
| `0x21` sub 1 / sub 4 | `SetData` | `0x435a23b4` |
| `0x22` sub 1 | `SetData` | `0x435a23b4` |
| `0x32` | handler | `0x43a48d16` |
| `0x33` | handler | `0x43a48cf2` |
| `0x41` | `ConfirmDoneCodec` | `0x435a1d1c` |
| `0xd1` | `DbgDiagAvc` | `0x435a1c5c` |
| otro | log `NOT SUPPORTED`, `return 1` | — |

La trama de `0x435a157c` es `strh id` en `+0`, `strb mode` en `+2`, `strb func` en `+3`,
`u32` en `+4` (`movs r2,#0xc` en `0x435a1586`), enviada con `0x435a1510`.

### 3.3 `ExecSensComp` — constructor de respuestas (`0x435a17e8`)

No ejecuta: **responde**. Por cada id registra su nombre `SENS_*` y compone la respuesta
con los `SetComp*` de `CdCtrlCore`.

| id | nombre `SENS_*` (vaddr) | respuesta |
|---|---|---|
| 1 | `SENS_SET_DIAG_MODE` `0x43c3b518` | `SetCompNormal` `0x435a1b64` |
| 2 | `SENS_SET_DATA_AREA` `0x43c3b540` | `SetCompNormal` |
| 3 | `SENS_REL_DATA_AREA` `0x43c3b568` | `SetCompNormal` |
| `0x11` | `SENS_RUN_CODEC` `0x43c3b590` | `SetCompNormal` |
| `0x12` | `SENS_CMP_DATA` `0x43c3b5b4` | `SetCompNormal` |
| `0x21` | `SENS_SET_DATA` `0x43c3b601` | sub 1 → `SetCompNormal` + `0x435a1bac` + `SENS_MODE_PROC_START` `0x43c3b37f`; sub 4 → `SetCompNormal` + `SENS_MODE_FIN_SEND_DATA` `0x43c3b3b2` |
| `0x22` | `SENS_GET_DATA` `0x43c3b624` | sub 1 → `SetCompNormal` + `0x435a1be0` + `SENS_MODE_PROC_START`; sub `0x10` → `0x435a1c14` + `SENS_MODE_FIN_RECV_DATA` `0x43c3b433` |
| `0x32` | `SENS_CNFM_SET_DATA_AREA` `0x43c3b497` | `SetCompNormal` |
| `0x33` | `SENS_CNFM_REL_DATA_AREA` `0x43c3b4c4` | `SetCompNormal` |
| `0x41` | `SENS_CNFM_DONE_CODEC` `0x43c3b5d7` | `SetCompNormal` |
| `0xd1` | `SENS_DBG_DIAG_AVC` `0x43c3b4f1` | `SetCompNormal` |
| otro | `[ERR][CDIAG][CTRLIF]NOT SUPPORTED…` `0x43c3b238` | `return 1` |

## 4. Las 16 funciones emisoras (VERIFICADO)

| función | clase | nombre | firma (vaddr) | sitios | cadenas | llamadores `bl` |
|---|---|---|---|---|---|---|
| `0x435a1b64` | Cd | `SetCompNormal` | `0x43c3b7a9` | 1 | 1 | `0x435a18b8`, `0x435a18d6`, `0x435a190e`, `0x435a1952` |
| `0x435a1bac` | Cd | — (guard corto) | — | 1 | 1 | `0x435a18c4` |
| `0x435a1be0` | Cd | — (guard corto) | — | 1 | 1 | `0x435a191a` |
| `0x435a1c14` | Cd | `SetCompDeleteData` | `0x43c3c19c` | 1 | 1 | `0x435a192c` |
| `0x435a1c5c` | Cd | `DbgDiagAvc` | `0x43c3b6df` | 5 | 5 | `0x435a177c` |
| `0x435a1d1c` | Cd | `ConfirmDoneCodec` (por traza) | — | 5 | 5 | `0x435a172e` |
| `0x435a1de0` | Cd | `CmpData` | `0x43c3b72a` | 9 | 9 | `0x435a16ac` |
| `0x435a1f18` | Cd | `RunCodec` | `0x43c3c123` | 9 | 9 | `0x435a14c2` |
| `0x435a20b0` | Cd | `RelMemArea` | `0x43c3b768` | 9 | 9 | `0x435a14a2` |
| `0x435a2200` | Cd | `SetMemArea` | `0x43c3b7ec` | 9 | 9 | `0x435a1482` |
| `0x435a2354` | Cd | `SetDiagMode` (por trazas) | — | 2 | 2 | `0x435a1684` |
| `0x435a23b4` | Cd | `SetData` | `0x43c3c162` | 16 | 9 | `0x435a16c4`, `0x435a16f0` |
| `0x43629c4c` | McSens | `SetCompNormal` | `0x43c7369c` | 1 | 1 | `0x43620044` |
| `0x43920bcc` | AmSens | `SetCompNormal` | `0x43cdb4c7` | 1 | 1 | `0x4391ad28`, `0x4391ad46`, `0x4391ad7c`, `0x4391ada0` |
| `0x43920c2c` | AmSens | — | — | 2 | 2 | `0x4391ad32` |
| `0x43920c9c` | AmSens | — | — | 2 | 2 | `0x4391ad86` |

La identificación no es una inferencia por vecindad: la guarda de cada función le pasa a
`0x435ab880` el **fichero** (p. ej. `cdCtrlCore.cpp` `0x43c3b86c`) y la **firma de la propia
función** (p. ej. `0x43c3b7a9` = `CDIAGER CdCtrlCore::SetCompNormal(OsalResponsePacket*, __uint32_t)`)
junto al `line` (`0x2bd`). En las funciones con traza propia la firma se referencia además
dentro del cuerpo (`0x435a1cf0` → `0x43c3b6df`, `0x435a1ede` → `0x43c3b72a`,
`0x435a2074` → `0x43c3c123`, `0x435a21ba` → `0x43c3b768`, `0x435a230c` → `0x43c3b7ec`,
`0x435a1c26` → `0x43c3c19c`, `0x435a23e6`/`0x435a2784` → `0x43c3c162`).

## 5. Trama de respuesta (VERIFICADO)

`SetCompNormal` Cd (`0x435a1b64`) escribe en el `OsalResponsePacket`:
`+0x00` tipo `8`, `+0x01` `1`, `+0x04` `0`, `+0x06` `u16 0`, `+0x08` `u32 0`,
`+0x0c` `u32 1`, `+0x10` byte de estado leído de `[obj+0x1480+0x18]`.
Variantes: `0x435a1bac` tipo `2` (estado en `[obj+0x1480+0x18]`, `+0x0c` de `[obj+0x1480+0x14]`),
`0x435a1be0` tipo `8` (`+0x08`/`+0x0c` de `[obj+0x1480+0x10]`/`+0x14`),
`0x435a1c14` tipo `0x20`. McSens lee `[obj+8]`; AmSens `SetCompNormal` lee `[obj+4]`.
Los errores devuelven `2` (guarda) o `1` (id no soportado).

## 6. Grafo entrante (VERIFICADO / parcial)

`0x435a121c` es un **switch por id de mensaje**: si coincide con el primer literal llama a
`0x435a13d8` (registro perezoso vía `0x439b4244`) y salta a `CdCtrlIf::ExecCmd`
(`b.w 0x435a1424` en `0x435a1242`); con el segundo salta a `0x43a48c40` (`b.w` en
`0x435a1234`). Se invoca **una vez por paquete** en el bucle `0x435a136e`–`0x435a1388`
(`bl` en `0x435a1382`).

`ExecSensCmd` y `ExecSensComp` **no tienen ningún `bl` directo ni puntero absoluto de 4 B**:
su entrada es indirecta (mensajería/vtable PIC). El **sitio exacto no está verificado**.

## 7. Accesor, constructor y registro (VERIFICADO)

- Accesor `0x435a1b18`: flag en `0x43e4a768` (`tst r3,#1` en `0x435a1b24`), objeto estático
  en `0x43e4a76c` (ceros en fichero), construido por `0x435a1a68`, registrado con
  `0x439b4244` leyendo dos palabras de la tabla en `0x4401eee4` + `{0x6c4c, 0x65e8}`
  (carga en `0x435a1b3c`/`0x435a1b40`). **18 llamadores** `bl`, todos desde `0x435a14xx`–`0x435a19xx`.
- Constructor `0x435a1a68`: escribe el vptr en `[obj]` y pone a cero, además del estado en
  `obj+0x1480`, los bloques `+8` (`0x3a4`), `+0x3ac` (`0x330`), `+0x6dc` (`0x3a4`),
  `+0xa80` (`0x330`), `+0xdb0` (`0x160`), `+0xf10` (`0x160`) y `+0x1070` (`0x418`).

## 8. McSens y AmSens (VERIFICADO)

- **McSens**: una sola función, `0x43629c4c` (guarda `line 0x13`, `0x43629c52`), llamada
  desde `0x43620044` dentro de `McPinMain::ExecMsgDfPin` (`0x4361f394`, `mcPinMain.cpp`),
  sub-id 1; el error devuelve `0x1f`.
- **AmSens**: `0x43920bcc` (guarda `line 0x26`), `0x43920c2c` (tipo `2`, size `0x5000`) y
  `0x43920c9c` (idéntica con size `0x800`); ambas toman `adr` de `0x43a3a9b4(handle, 0x12, 0)`
  y trazan `[AMSENS][CTRLCORE][AVCE][PARAM] adr[0x%08X] size[%d]`. Sus llamadores
  `0x4391ad32`/`0x4391ad86` están en un handler de ids 1/2 con sub-ids 1/4.

## 9. Diferencial (VERIFICADO)

- **A7S fw3.20: 55/55 cadenas idénticas** (0 exclusivas en ambos sentidos), mismas
  operaciones y mismos ficheros.
- **A6300 fw2.01: 90** cadenas = las **55 comunes** + **14 `[CDIAG][CTRLCORE] … 4K`** +
  **21 `[CDEXT][CTRLCORE]`** (memoria `MEM AROOC/ARROC/ALLOC/FREE`, `StartVideoCodecDiag`,
  `LoopbackControl`, `ExecVideoCodecDiag`). `CdExtCtrlCore` **no existe** en la A6000.

## 10. Línea del obturador: sin relación

Ninguna de las 55 cadenas `[CTRLCORE]` menciona obturador, disparo, cortinilla, lectura del
sensor ni tiempos de exposición: el token pertenece al **diagnóstico del códec**. Las únicas
cadenas con "tiempo" del ecosistema están en `mcAvCtrlCore.cpp`
(`CallAvscSetHsRecTime` `0x43c45464`, `CalcSuperSandQRecTime` `0x43c457b3`,
`ReviseMovieEncInfoTimeForSuperSandQ` `0x43c4577a`) y **no llevan** la etiqueta `[CTRLCORE]`.

## 11. NO VERIFICADO

- Nombre de `0x439b4244` (registro de mensaje/clase usado por `0x435a1b18` y `0x435a13d8`).
- Nombres de `0x435a1bac` y `0x435a1be0` (sólo tienen la guarda corta `p_prm is NULL`).
- Sitio exacto de la entrada indirecta a `ExecSensCmd` y `ExecSensComp`.
- Significado funcional de los ids `0x32`/`0x33` de `ExecSensCmd` (handlers `0x43a48d16`/`0x43a48cf2`).

## 12. Reproducción

```
.venv/bin/python analysis/s137_ctrlcore/scan_ctrlcore.py      # regenera ctrlcore_raw.json
.venv/bin/python analysis/s137_ctrlcore/verify_sites.py       # 74/74 sitios, texto 74/74
.venv/bin/python -m pytest tests/test_s137_ctrlcore.py
```

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (54 tests del hito + comprobaciones a mano):**

1. **Recuento y estructura**: 55 cadenas con el token `[CTRLCORE]` entre `0x43c3b82d` y
   `0x43cdb492`, **74 sitios PIC** (regla estricta) en **16 funciones** emisoras; el subagente
   además **recalculó los 74 sitios de forma independiente** (`verify_sites.py`: `ldr` del mismo
   registro → literal → `destino = W + add + 4`) y **74/74** coinciden en texto.
2. **Corrección de la premisa del hito**: `[CTRLCORE]` **no es un módulo de primer nivel**, es una
   **sub-etiqueta de segundo nivel** (igual que `[APL]` dentro de `[CAMERA_SA]`, S119):
   `[CDIAG][CTRLCORE]` (51), `[MCSENS][CTRLCORE]` (1) y `[AMSENS][CTRLCORE]` (3). La premisa que
   yo le di ("el núcleo de control") era correcta en el fondo pero no en la jerarquía de
   etiquetas → **aceptada y documentada**.
3. **Diferencial**: A7S fw3.20 con **55/55** cadenas idénticas (mismas operaciones y mismos
   ficheros); A6300 fw2.01 con 90 = las 55 comunes + 14 `[CDIAG][CTRLCORE] … 4K` + 21
   `[CDEXT][CTRLCORE]` (la clase `CdExtCtrlCore` **no existe** en la A6000).
4. **Negativo acotado**: ninguna de las 55 cadenas menciona obturador, disparo, cortinilla ni
   lectura del sensor → **sin efecto en S51**.
