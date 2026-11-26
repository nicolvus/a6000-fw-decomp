# Eye AF: diferencial A6000 fw3.21 vs A6300 fw2.01 (solo estático)

Convención: **VERIFICADO** = bytes citados (fichero, offset, VA y cadena exacta);
**INFERENCIA** = lectura razonada del código sin ejecución; **NO_VERIFICADO** = no acreditado aquí.
Base de direcciones usada en todo el documento: `av-cam.bin` es una imagen LIRO que carga en
**0x43541000 para el offset de fichero 0**: el u32 de +0x04 vale `0x4C49524F` (la magia `LIRO`, que en
memoria se lee `4F 52 49 4C`) y en +0x0C hay un puntero `0x43541044` que cae en el propio offset 0x44
(VERIFICADO en los dos modelos); por tanto `VA = offset + 0x43541000`. Los slots de vtable son
punteros Thumb (bit 0 = 1): la entrada de código real es `slot & ~1`.
Los `.elf` de vista previos del repo (`analysis/av-cam-analysis-view.elf`) restan 0x1F0/0x218;
este informe **no** los usa.

Binarios y hashes (VERIFICADO):

| Modelo | Fichero | sha256 |
|---|---|---|
| A6000 | `.../fw321/.../nflasha3_unpacked_unpacked/av-cam.bin` | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` |
| A6300 | `.../a6300-fw201/.../nflasha3_unpacked_unpacked/av-cam.bin` | `6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16` |
| A6000 | `.../nflasha15_unpacked_unpacked/lib/libObj.so` | `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a` |
| A6300 | `.../nflasha15_unpacked_unpacked/lib/libObj.so` | `c70b635bcbd386b4b34b6a5c37ef941a1463253aebb43d83fada7fe4e9fe9073` |
| A6000 | `.../nflasha15_unpacked_unpacked/lib/libScalarDaemon.so` | `ca28cbf4c5c6402160ad80f6ad9f5e99052f42c3fabc382c557fcded18addc29` |
| A6300 | `.../nflasha15_unpacked_unpacked/lib/libScalarDaemon.so` | `9009bb9b8fa5defb7d3d7d27fe8a7b8f6743dccc6511c655396d8b414a1b30a9` |

## 0. Respuesta en 12 líneas

1. La orden es **`MSGID_SET_EYE_START_AF_CMD`** (con `MSGID_SET_EYE_START_AF_CMP` y
   `MSGID_NOTIFY_EYE_START_AF_EVT`) y su carga es la propiedad **`PARAMID_CAMSETTING_EYE_START_AF` = ON/OFF**.
2. Id numérico **VERIFICADO**: **`0x5008`** en la A6000 y **`0x8008`** en la A6300 (tabla `(const char*, u32)`
   de `libScalarDaemon.so`; entradas `0x1b201c/0x1b2020` y `0x1da9ec/0x1da9f0`).
3. Lo emite el **userland de la propia cámara** (`libObj.so`: `CamUser::SequenceSetEyeStartAF` →
   `ObjCamera::MSGID_SET_EYE_START_AF_CMD` → `SetEyeStartAFForLiro`), no la app: la API remota no
   tiene ni un método de ojos (carril `orb_touchaf`, ya cerrado).
4. **`EYE_START_AF` no es Eye AF**: es *Eye-Start AF* (el sensor del visor arranca el AF) y está en **los dos**
   modelos, con receptor propio.
5. Lo que la A6300 **sí añade** y la A6000 **no** tiene: `Camera2LC::PhaseAF::State::CPafStateEyeFocus`,
   la ruta LiroSeq del parámetro (`CheckSetEyeStartAF`, `SET_EYE_START_AF[%d]`,
   `LiroSeq ParamCheckErr@%s[eye_start_af]`), el factor `INH_FACTOR_CAM_AF_KEY_EYE_PRIORITY_AF_TYPE_P`
   y los campos de **pupila** del imager (`b8_pupil_information_data0..5`).
6. Receptor en la A6000: **sí existe `CPafStateEyeStart`** (RTTI `0x43ca7b3a`, vtable `0x43fcd0bc`) y la FC
   con detección de ojos (`idt_edt_*`, `EyeDetection`, `[CAMERA_MAIN_FC]: Eye data is invalid…`), pero
   **no hay receptor de la orden de prioridad de ojos** ni estado `EyeFocus`.
7. Continuo: en la A6300 la persistencia es un **modo** (AF-C + PhaseAF/FC), no una orden repetida; por eso
   añade `PARAMID_FOCUS_RELEASE_PRIORITY_AF_C` y `VALUEID_{FOCUS,RELEASE,BALANCE}_PRIORITY_AF_C`, ausentes en la A6000.
8. Canal: **Scalar/UIPC** (`libScalarDaemon.so` → `av-cam.bin` por LIRO). Ni app ni HTTP: la API de la app no
   publica ojos (0 métodos `EyeAF`/`pupil`/`faceDetection`).
9. Pieza mínima para activar Eye AF en la A6000: **no es un mensaje, es el receptor** — portar
   `CPafStateEyeFocus` + la ruta del parámetro `eye_start_af` al `av-cam.bin` de la A6000 y engancharla
   a la salida de ojos de la FC. El emisor ya está presente en la A6000.
10. Si solo se permite emitir: `0x5008 = ON` (`PARAMID_CAMSETTING_EYE_START_AF`) reproduce *Eye-Start AF*,
    no Eye AF. **NO_VERIFICADO** su efecto real en la A6000 (requiere ejecución o decompilación).
11. Los ids **no son portables**: de 919 nombres comunes entre las dos tablas de `libScalarDaemon.so`,
    **492 cambian de número** (p. ej. `PARAMID_BKUP_AE_METER_MODE` 0x201F → 0x5017).
12. **NO_VERIFICADO** aquí: el id numérico del `MSGID` de CamMsgConv (el `0x4054` del enunciado no se
    pudo reproducir en ninguna tabla) y la cadena de llamada a `CheckSetEyeStartAF` (REA no ejecutado:
    1 GB de RAM libre y otra sesión Ghidra cargando).

## 1. Método (y por qué no hay salida de REA)

- Exploración byte a byte con lector ELF propio (`analysis/eyeaf/data/diff/elfmap.py`), índice de
  punteros absolutos e índice `movw/movt` (`mwx.py`), desensamblado puntual con capstone Thumb.
- **Base corregida**: los punteros de la cabecera LIRO (`0x43541044` en +0x0C) demuestran que el offset 0
  carga en `0x43541000`. Con esa base, 70/300 cadenas al azar de la A6300 tienen puntero absoluto (con
  `+0x43540DE8` daban 3/300): la base anterior estaba desplazada y por eso los xrefs de cadenas salían vacíos.
- **REA no se usó para decompilar**: el host tenía **1 GB de RAM disponible** (15 GB totales, 13 en uso) y
  había una sesión Ghidra de otro carril cargando (`/tmp/rea-ghidra-*/target-2ef500ba5871.bin`); abrir
  `av-cam.bin` (13 MB, ~8 min en frío por binario) arriesgaba OOM sobre el trabajo en curso. Todo lo que
  se afirma abajo se reproduce con `grep`/`dd` sobre los ficheros y las direcciones citadas.
- **Corrección de un resultado previo de esta misma ruta**: la A6000 **sí** tiene `CPafStateEyeStart`.
  Un `grep` de `CPafStateEye*` sí lo encuentra en los dos modelos; lo que falta en la A6000 es `EyeFocus`.

## 2. Vocabulario: *Eye-Start AF* ≠ *Eye AF*

| Nombre en el binario | Qué es | A6000 | A6300 |
|---|---|---|---|
| `PARAMID_EYE_START_AF(_SET/_ACT)`, `MSGID_SET_EYE_START_AF_CMD/CMP`, `VALUEID_EYE_START_AF_ON/OFF` | *Eye-Start AF*: el sensor de ojo del visor arranca el AF | **sí** (`libObj.so`) | sí |
| `PARAMID_CAMSETTING_EYE_START_AF` | la misma propiedad en el espacio del daemon Scalar | **sí = 0x5008** | sí = **0x8008** |
| `VALUEID_AF_KEY_EYE_PRIORITY_AF` | **Eye AF**: tecla de función "prioridad al ojo" | sí (nombre presente) | sí |
| `INH_FACTOR_CAM_AF_KEY_EYE_PRIORITY_AF_TYPE_P` | factor que **habilita** esa tecla en la UI (InhMgr/Caution) | **ausente** | **presente** |
| `CPafStateEyeFocus` | estado del PhaseAF que enfoca al ojo | **ausente** | **presente** |
| `CheckSetEyeStartAF` / `SET_EYE_START_AF[%d]` / `…[eye_start_af]` | receptor LiroSeq del parámetro en `av-cam` | **ausente** | **presente** |
| `b8_pupil_information_data0..5` | campos de pupila del imager | ausente (solo `ZAF … pupil:%d`) | **presente** |

Cuidado con el falso amigo: el "Eye AF" de la UI de la A6300 **no** viaja por `EYE_START_AF`; el
discriminante real es `AF_KEY_EYE_PRIORITY_AF` (UI) + `CPafStateEyeFocus` (motor).

## 3. P1 — A6300: localizar la orden, el id y el emisor

**Nombres (VERIFICADO, cadena exacta y offset de fichero)**

| Cadena | A6300 (`libObj.so`) | A6000 (`libObj.so`) |
|---|---|---|
| `PARAMID_EYE_START_AF` | `0xe02237` | `0xe49a25` |
| `PARAMID_EYE_START_AF_SET` | `0xe0224c` | `0xe49a3a` |
| `PARAMID_EYE_START_AF_ACT` | `0xe02265` | `0xe49a53` |
| `MSGID_SET_EYE_START_AF_CMD` | `0xe0b1f9` | `0xe50e08` |
| `MSGID_SET_EYE_START_AF_CMP` | (contiguo al anterior) | (contiguo) |
| `MSGID_NOTIFY_EYE_START_AF_EVT` | presente | presente |
| `VALUEID_AF_KEY_EYE_PRIORITY_AF` | `0xdff786` | `0xe487d7` |
| `SetEyeStartAFForLiro NON SUPPORTED MsgID[0x%04x]` | `0xdbfa2f` | `0xe0de65` |
| RTTI `N7CamUser21SequenceSetEyeStartAFE` | `0xe208c7` | `0xe2492b` |
| `SeqSetEyeStartAF) ##### [%d] SEND MSG ERROR #####` | `0xe208d9` | `0xe24948` |

Los nombres viven en sendas **matrices de punteros** (`const char*[]`, orden de enum, sin huecos):
A6300 `PARAMID_*` desde `0xfbdbf8` (1624 entradas), `MSGID_*` desde `0xfbd3ec` (515),
`VALUEID_*` desde `0xfc03f8` (1491); A6000 `0xfdc144` (1350), `0xfdb5f0` (725), `0xfdd65c` (1288).
`PARAMID_EYE_START_AF` ocupa **el índice 244** desde `PARAMID_ZOOM_SPD` **en los dos modelos**.

**Id numérico (VERIFICADO)**: `PARAMID_CAMSETTING_EYE_START_AF`, tabla `(const char* nombre; u32 id)`
de `libScalarDaemon.so`:

| Modelo | Tabla | Entrada | Cadena | id |
|---|---|---|---|---|
| A6000 | `0x1b05a4`–`0x1b23a4` (960) | `0x1b201c` / id en `0x1b2020` | `PARAMID_CAMSETTING_EYE_START_AF` | **`0x5008`** |
| A6300 | `0x1d82ec`–`0x1dadbc` (1370) | `0x1da9ec` / id en `0x1da9f0` | `PARAMID_CAMSETTING_EYE_START_AF` | **`0x8008`** |

**Quién lo emite (VERIFICADO el texto, INFERENCIA la cadena)**: el userland de la cámara
(`libObj.so`) expone el emisor `CamUser::SequenceSetEyeStartAF` con el diagnóstico
`SetEyeStartAFForLiro NON SUPPORTED MsgID[0x%04x]`, es decir, hay una rutina que construye un mensaje
para *Liro* (= `av-cam.bin`) y avisa si el MsgID no está soportado. La app (`SmartRemote.odex`,
`orb-server`) **no** lo envía: en la A6300 no hay ni un método de ojos en la API (0 `EyeAF`, 0 `pupil`,
0 `faceDetection`; ver `analysis/eyeaf/orb_touchaf.md`). La tecla existe en la UI:
`VALUEID_AF_KEY_EYE_PRIORITY_AF` (nombre en `libObj.so` de los dos modelos) es la tecla, y en la A6300
está habilitada por `INH_FACTOR_CAM_AF_KEY_EYE_PRIORITY_AF_TYPE_P`
(`InhInfo_InhMgr.db` offset `0x031fb2`, `0x03c297`, y `com.sony.scalar.sysutil.didep.Caution.odex`
`0x060e35`: `INH_FACTOR_ID_CAM_AF_KEY_EYE_PRIORITY_AF_TYPE_P`).

## 4. P2 — Comparación de las tablas PARAMID/MSGID (familia EYE)

Existencia por nombre (VERIFICADO, `strings` de `libObj.so` de cada modelo):

| Nombre | A6000 | A6300 | ¿Cambia el número? |
|---|---|---|---|
| `PARAMID_EYE_START_AF` / `_SET` / `_ACT` | sí | sí | **sí**: `PARAMID_CAMSETTING_EYE_START_AF` 0x5008 → 0x8008 |
| `MSGID_SET_EYE_START_AF_CMD` / `_CMP` | sí | sí | número no acreditado (ver §8) |
| `MSGID_NOTIFY_EYE_START_AF_EVT` | sí | sí | ídem |
| `VALUEID_EYE_START_AF_ON` / `_OFF` | sí | sí | ídem |
| `VALUEID_AF_KEY_EYE` / `VALUEID_AF_KEY_EYE_PRIORITY_AF` | sí | sí | ídem |
| `VALUEID_FOCUSING_STATE_EYE_START`, `VALUEID_EYE_BLINK_*` | sí | sí | ídem |
| `PARAMID_FOCUS_RELEASE_PRIORITY_AF_C`, `VALUEID_FOCUS_PRIORITY_AF_C`, `VALUEID_RELEASE_PRIORITY_AF_C`, `VALUEID_BALANCE_PRIORITY_AF_C` | **no** | sí | — (no existe en la A6000) |
| `VALUEID_AF_KEY_IR` | no | sí | — |

Conclusión P2: **en la familia EYE casi todo cambia de número y casi nada aparece/desaparece**; lo que
la A6300 añade a nivel de datos es el factor de inhibición de la tecla y los `*_PRIORITY_AF_C` de AF-C.
Y no es un caso aislado: **492 de 919** nombres comunes a las dos tablas `(nombre, id)` del daemon
tienen id distinto (VERIFICADO; datos en `analysis/eyeaf/data/diff/scalar_param_table.json`), p. ej.
`PARAMID_BKUP_AE_METER_MODE` `0x201F` (A6000) → `0x5017` (A6300), `PARAMID_CAMSETTING_AE_LOCK`
solo existe con ese nombre en la A6000. **Los ids del protocolo no son portables entre modelos.**

## 5. P3 — ¿Implementa el `av-cam` de la A6000 el receptor?

### 5.1 Lo que **sí** tiene la A6000 (VERIFICADO)

| Objeto | Dirección (VA) | Evidencia |
|---|---|---|
| RTTI `N6Camera2LC17CPafStateEyeStartE` | `0x43ca7b3a` (off `0x766b3a`) | cadena exacta |
| `type_info` de `CPafStateEyeStart` | `0x43ff6e4c` | apuntada por la vtable en `0x43fcd0bc` |
| **vtable** `CPafStateEyeStart` | `0x43fcd0bc` | 7 métodos, tabla de abajo |
| `idt_edt_start/stop/get_result` + `EyeDetection` | `0x43cf7022` (off `0x7b6022`) | cadena exacta: `idt_edt.cpp … EyeDetection idt_edt_start rtn=%d FC/Drv/fc_drv_iro2g.cpp` |
| `[CAMERA_MAIN_FC]: Eye data is invalid, but lc flag is true.` | `0x43ca6944` | cadena exacta (ya documentada en S138) |

Es decir: **el motor de PhaseAF de la A6000 tiene un estado de arranque de AF por ojo y la FC tiene
detección de ojos**; la máquina de estados tiene 9 clases (`TrackSelect, EyeStart, S1, Smile, CPafState,
None, SelfTimer, Normal, Enter`).

### 5.2 Lo que **falta** en la A6000 y sí está en la A6300 (VERIFICADO por ausencia de cadena)

| Objeto | A6000 | A6300 (VA / offset) |
|---|---|---|
| `CheckSetEyeStartAF` | **0 ocurrencias** | `0x43dcadd6` / off `0x889dd6` |
| `SET_EYE_START_AF[%d]` | **0** | `0x43dac049` / off `0x86b049` |
| `LiroSeq ParamCheckErr@%s[eye_start_af] cur:%d req:%d` | **0** | `0x43dc6ca3` / off `0x885ca3` |
| cualquier `CheckSet*` (201 en A6300) / `LiroSeq ParamCheckErr@%s` (370) | **0** | presentes |
| `CPafStateEyeFocus` (RTTI + vtable) | **0** | RTTI `0x43dcfc27`, vtable `0x4418daf4` |
| `b8_pupil_information_data0..5`, `b8_SHD_EY_data0..5` | **0** (solo `pupil:%d` en log ZAF) | `0x43e012cb` / off `0x8612cb` |
| `CheckSetFacePriorityTrackingMode`, `CheckSetObjectTrackingMode` | **0** | presentes |

Respuesta a P3: el `av-cam` de la A6000 **no implementa el receptor de la orden de Eye AF**. Su
`CPafStateEyeStart` es el estado de *Eye-Start AF* (arranque de AF por el sensor del visor), no el
estado de prioridad de ojos; el estado que enfoca al ojo (`CPafStateEyeFocus`) no existe, y no hay
ninguna ruta de parámetro `eye_start_af` en la capa LiroSeq (esa capa entera — 201 `CheckSet*` +
370 mensajes `ParamCheckErr` — falta en la A6000). **INFERENCIA**: una orden `EYE_START_AF` recibida por
la A6000 no encuentra handler nombrado; como mucho entraría por la lógica interna de la FC/visor.

### 5.3 Tabla de funciones (dirección, tamaño, qué hace, evidencia)

Los slots de vtable son punteros Thumb (bit 0 = 1): la **entrada real es `slot & ~1`**; se dan ambas.

`av-cam.bin` A6300 — `Camera2LC::PhaseAF::State::CPafStateEyeStart`, vtable `0x4418dab4`
(`+0x00` = puntero a `type_info` `0x441d9470`; el `offset-to-top` en `0x4418dab0` vale `0`):

| Slot / entrada | Tamaño | Qué hace | Evidencia |
|---|---|---|---|
| `0x43bd04b3` / `0x43bd04b2` | 32 B | entrada/ejecución: si `[r1,#0x10]` es 0 llama virtual `[vt]+4` (consulta de actividad); si `[this+4]==4` lo decrementa y limpia `[this+8]` → **temporizador del estado** | desensamblado Thumb `0x43bd04b2`–`0x43bd04d2` |
| `0x43bd0465` / `0x43bd0464` | 4 B | `movs r0,#0; bx lr` (consulta: falso) | `0x43bd0464` |
| `0x43bd04a7` / `0x43bd04a6` | 4 B | `movs r0,#7; bx lr` → **id de estado 7** | `0x43bd04a6` |
| `0x43bd04e7` / `0x43bd04e6` | 6 B | `strb.w r1,[r0,#0x23]` (setter de un flag del contexto) | `0x43bd04e6` |
| `0x43bd046d` / `0x43bd046c` | 2 B | `bx lr` (no-op) | `0x43bd046c` |
| `0x43bd04ed` / `0x43bd04ec` | 6 B | `ldrb.w r0,[r0,#0x23]` (getter del mismo flag) | `0x43bd04ec` |
| `0x43bd0591` / `0x43bd0590` | 8 B | calcula estado siguiente y lo guarda en `[r0+0x14]`: `[r0+4]` 0 → +1; si `[r0+0x20]` → +7; si no 9 | `0x43bd0590` |

`av-cam.bin` A6300 — `CPafStateEyeFocus` (**solo A6300**), vtable `0x4418daf4`
(`+0x00` = `type_info` `0x441d9494`):

| Slot / entrada | Tamaño | Qué hace | Evidencia |
|---|---|---|---|
| `0x43bd05c1` / `0x43bd05c0` | 18 B | si `[this+4]==4` resta 2 y limpia `[this+8]` → **temporizador del estado de enfoque al ojo** | `0x43bd05c0`–`0x43bd05d0` |
| `0x43bd0465`, `0x43bd04e7`, `0x43bd046d`, `0x43bd04ed` | 4–6 B | mismos auxiliares que `EyeStart` (falso / setter / no-op / getter) | ídem |
| `0x43bd04af` / `0x43bd04ae` | 4 B | `movs r0,#9; bx lr` → **id de estado 9** (frente al 7 de `EyeStart`) | `0x43bd04ae` |
| `0x43bd04f3` / `0x43bd04f2` | 8 B | estado siguiente: `[r0+4]` 0 → +1; si no `cmp r3,#6` y `tbb [pc,r3]` (tabla de 6 saltos) | `0x43bd04f2`, `tbb` en `0x43bd0506` |

`av-cam.bin` A6000 — `CPafStateEyeStart`, vtable `0x43fcd0bc` (`+0x00` = `type_info` `0x43ff6e4c`):

| Slot / entrada | Tamaño | Qué hace | Evidencia |
|---|---|---|---|
| `0x43af45df` / `0x43af45de` | 6 B | `strb.w r1,[r0,#0x43]` (guarda el flag de entrada) | `0x43af45de` |
| `0x43af45c5` / `0x43af45c4` | 2 B | `bx lr` | `0x43af45c4` |
| `0x43af45c7` / `0x43af45c6` | 4 B | `movs r0,#0; bx lr` | `0x43af45c6` |
| `0x43af45e5` / `0x43af45e4` | 6 B | `ldrb.w r0,[r0,#0x43]` (lee el flag) | `0x43af45e4` |
| `0x43af46cb` / `0x43af46ca` | 8 B | estado siguiente en `[r0+0x34]`: `[r0+4]` 0 → +1; si `[r0+0x40]` → +7; si no 9 | `0x43af46ca`–`0x43af46e0` |
| `0x43af4727` / `0x43af4726` | 48 B | **entrada/ejecución**: copia contexto (`bl 0x43af3b7a` sobre `[r0+4]` y `[r0+0x1c]`), evalúa `[r5+0x1a]`, `[r5+0x1c]==1` y `ldrh r2,[r5,#0x20]−0x24c ≤ 1` → escribe `[r4+0x40]`, llama virtual `[vt]+0x20` con `[r5+0x19]` y decrementa el temporizador `[r4+4]` si `[r5+0x18]` | `0x43af4726`–`0x43af4774` |
| `0x43af45b1` / `0x43af45b0` | 2 B | `bx lr` | `0x43af45b0` |

Lectura: las dos clases son máquinas de estado mínimas (getter/setter de flag, "estado siguiente" y
temporizador). En la A6000 el ejecutor (`0x43af4726`) valida el contexto con `−0x24c ∈ {0,1}` antes de
escribir el flag y llamar al virtual `+0x20`; en la A6300 esa misma función es el temporizador
(`0x43bd04b2`) y el despacho por tabla vive en el `EyeFocus` (`0x43bd04f2`). **INFERENCIA**: la
diferencia de comportamiento no está en el *tipo* de estado (los dos existen) sino en que la A6300
añade el estado de enfoque (`EyeFocus`, id 9) y la ruta de parámetro que lo alcanza.

`libScalarDaemon.so` (ambos) — tablas de nombre→id: A6000 `0x1b05a4` (960 entradas, 7 680 B),
A6300 `0x1d82ec` (1 370 entradas, 10 960 B); entrada de `PARAMID_CAMSETTING_EYE_START_AF` en
`0x1b201c`/`0x1b2020` y `0x1da9ec`/`0x1da9f0` (VERIFICADO).

`libObj.so` (ambos) — matrices `const char*` de nombres de enum: A6300 `PARAMID` `0xfbdbf8`
(1624 × 4 B), `MSGID` `0xfbd3ec` (515), `VALUEID` `0xfc03f8` (1491); A6000 `0xfdc144` (1350),
`0xfdb5f0` (725), `0xfdd65c` (1288) (VERIFICADO).

## 6. P4 — ¿Eye AF continuo por una orden distinta o por un modo?

**Por un modo, no por una orden repetida** (INFERENCIA sólida, con tres apoyos VERIFICADOS):

1. La A6300 modela el ojo como **estado** de `Camera2LC::PhaseAF::State` (`CPafStateEyeStart` →
   `CPafStateEyeFocus`); un estado permanece hasta que la máquina sale, no se refresca por mensaje.
2. La A6300 añade los parámetros de prioridad de AF-C que la A6000 no tiene:
   `PARAMID_FOCUS_RELEASE_PRIORITY_AF_C`, `VALUEID_FOCUS_PRIORITY_AF_C`,
   `VALUEID_RELEASE_PRIORITY_AF_C`, `VALUEID_BALANCE_PRIORITY_AF_C` (`libObj.so` A6300; 0 en A6000).
   Son los ajustes de "prioridad AF-C/disparo/balance" que acompañan al Eye AF de la A6300.
3. La A6300 añade además el **seguimiento** que arrastra el ojo: `setTrackingFocus` (API nueva, 3 filas
   en `InhInfo_InhMgr.db`), `CheckSetFacePriorityTrackingMode`, `CheckSetObjectTrackingMode`.

La A6000 **sí tiene AF-C** (`PARAMID_FOCUS_MODE` con valores en `libObj.so` de los dos modelos), pero
no tiene la variable "prioridad al ojo" ni el estado `EyeFocus`, así que **AF-C no basta**: en la A6300
el modo es AF-C **más** la tecla/factor de prioridad de ojo **más** el estado `EyeFocus` del PhaseAF.

## 7. P5 — Conclusión operativa

- **Orden concreta (si sólo se puede emitir una)**: `PARAMID_CAMSETTING_EYE_START_AF = 1` con
  `MSGID_SET_EYE_START_AF_CMD`. Id por modelo: **A6000 `0x5008`**, **A6300 `0x8008`** (VERIFICADO).
  Payload: entero ON/OFF (`VALUEID_EYE_START_AF_ON`/`_OFF`).
- **Canal**: **Scalar/UIPC** — `libScalarDaemon.so` (parámetro) → LIRO → `av-cam.bin`. **No** la app ni
  HTTP: la API remota no publica ojos (0 `EyeAF`/`pupil`/`faceDetection` en `orb-server` de A6000, A7S y A6300).
- **Qué consigue eso en la A6000**: *Eye-Start AF* (arranque de AF por el sensor del visor), porque el
  receptor nombrado que existe es ese. **No** activa detección de ojos ni mueve el área de AF al ojo:
  para eso hace falta `CPafStateEyeFocus`, que la A6000 no tiene. **NO_VERIFICADO** el efecto exacto
  (falta ejecución o decompilación del handler A6000 del id 0x5008).
- **Pieza mínima para Eye AF persistente en la A6000**: **el receptor**, no el emisor.
  1. El emisor ya está: `CamUser::SequenceSetEyeStartAF` + `PARAMID/MSGID/VALUEID` de la familia EYE
     existen en el `libObj.so` de la A6000 (VERIFICADO).
  2. Falta en `av-cam.bin`: el estado `CPafStateEyeFocus` (A6300 `0x4418daf4`) y la ruta LiroSeq del
     parámetro (`CheckSetEyeStartAF` / `SET_EYE_START_AF` / `eye_start_af`).
  3. Puente natural: la FC de la A6000 ya produce datos de ojos (`idt_edt_*`, flags `[ctx+0xde]`/`[ctx+0xdf]`
     de S138) y el PhaseAF ya tiene `CPafStateEyeStart`: el injerto es un estado nuevo que consuma esos
     datos y mueva el área de AF, sin tocar Darwin ni el obturador.
- **Alternativa sin parche** (ya implementada, otro carril): dirigir el punto de AF por la API de
  *touch AF* (`setTouchAFPosition`, msgid `0x192`/paramid `0x8d`) con un detector en el PC. Es la única
  vía de "ojo" que hoy existe en la A6000 **por orden**, y es geométrica (mueve el marco), no detección.

## 8. Límites y NO_VERIFICADO

- **Id numérico del `MSGID`**: el espacio CamMsgConv de `libObj.so` sólo publica la **matriz de nombres**
  (sin ids), y las 515/725 entradas no son densas. Con la tabla `(nombre, u16)` de `InhInfo_InhMgr.db`
  como ancla (p. ej. `INH_FEATURE_CAM_MSGID_SET_SILENT_SHUTTER_MODE_CMD=0x0448`,
  `…SET_PICTURE_EFFECT_CMD=0x037a`) las diferencias de índice (0x98) no cuadran con las de valor (0xCE):
  **ese espacio no es el `MSGID`**. Conclusión: **NO_VERIFICADO** el número de `MSGID_SET_EYE_START_AF_CMD`;
  el `0x4054` del enunciado **no se pudo reproducir** (0 tablas ordenadas con `0x4054` en los dos `av-cam.bin`,
  115/113 apariciones sueltas de la constante de 16 bits, ninguna en tabla de parámetros).
- **Quién llama a `CheckSetEyeStartAF`**: no resuelto. En `av-cam.bin` las cadenas del bloque
  `0x86xxxx–0x8Dxxxx` **no** tienen ni puntero absoluto ni pareja `movw/movt` (0/200 cadenas muestreadas en
  esa zona; 70/300 fuera de ella sí lo tienen): se referencian por un mecanismo que exige decompilador.
- **REA**: disponible (`mcp_rea`, 207 herramientas) pero **no ejecutado** para estos dos `av-cam.bin`
  por memoria (1 GB libre) y por la sesión Ghidra ajena en curso. Comandos previstos, para retomarlo:
  `open_binary {path: "<abs>/av-cam.bin", format:"raw-binary", architecture:"arm", entry_point:"0x43541000"}`,
  luego `inspect_address_context` en `0x43dcadd6` / `0x43dac049` / `0x4418dab4` y
  `batch_decompile` de los slots de las dos vtables.
- **Aviso de contradicción**: `knowledge/CURRENT.md` (carril Eye AF, 26-11-2026) cierra H3 con
  "Eye AF nativo por `Camera::FC` descartado". Este informe lo matiza: la FC **sí** tiene ojos en los dos
  modelos y el PhaseAF **sí** tiene `CPafStateEyeStart`; lo que falta en la A6000 es `CPafStateEyeFocus`
  y la ruta LiroSeq del parámetro. No cambia la conclusión operativa (sin parche no hay Eye AF), pero
  sí el motivo.

## 9. Reproducibilidad

```shell
# 42 comprobaciones byte-exactas de este informe (magia LIRO, base, presencia/ausencia de cadenas,
# RTTI, vtables y slots, ids 0x5008/0x8008). Debe imprimir "FALLOS: 0".
python3 analysis/eyeaf/data/diff/verify.py

# tablas (nombre, id) del daemon y comparación de ids entre modelos
python3 analysis/eyeaf/data/diff/dump_tables.py   # -> analysis/eyeaf/data/diff/scalar_param_table.json
                                                  #    960/1370 entradas, 0x5008/0x8008, 919 comunes, 492 con id distinto

# comprobación mínima a mano
python3 - <<'PY'
d=open('firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin','rb').read()
for s in (b'CheckSetEyeStartAF', b'SET_EYE_START_AF[%d]', b'eye_start_af', b'CPafStateEyeFocus'):
    i=d.find(s); print(s, hex(i), hex(i+0x43541000) if i>=0 else '-')
PY
```

Artefactos de esta pasada (en mi ruta, `analysis/eyeaf/data/diff/`): `elfmap.py` (lector ELF),
`mwx.py` (xrefs `movw/movt`), `enum_tables.py` (matrices de nombres), `verify.py` (42 comprobaciones,
0 fallos), `dump_tables.py`, `scalar_param_table.json` (960/1370 entradas `nombre → id`),
`inh_feature_ids.json` (329/493 `INH_FEATURE_* → u16`), `eye_token_sweep.json` (barrido de tokens por
binario en los dos firmwares).
