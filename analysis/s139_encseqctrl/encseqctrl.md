# S139 — el módulo `[ENCSEQCTRL]` (46 trazas): el control de secuencias de codificación

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 **fw3.21**); convención
> **vaddr = 0x43541000 + file_offset** (verificada también en la A7S y el A6300).
>
> Regla de referencias: **estricta** (canónica del repo,
> `analysis/s106_imaging_cap/scan_pic_refs_strict.py`, mapa global
> `analysis/s106_imaging_cap/pic_refs_strict_global.json`).
> Los 96 sitios se han **recalculado de forma independiente** con
> `analysis/s139_encseqctrl/verify_sites.py` → **96/96 confirmados**.

---

## 1. Resumen

| Magnitud | Valor |
|---|---|
| Trazas `[ENCSEQCTRL]` (A6000 fw3.21) | **46** (46 textos distintos) |
| Rango de las trazas en `.rodata` | `0x43c4bce5` – `0x43c4c796` |
| Referenciadas (regla estricta) | **46 / 46** (0 muertas) |
| Sitios de emisión | **96** |
| Funciones emisoras | **32** (código en `0x435d6ad0` – `0x435d90ac`, span 0x25DC = 9 692 B) |
| Fichero fuente | **`seqCtrl/mcAvcEncSeqCtrl.cpp`** (`0x43c4bd0f`) |
| Clase (RTTI) | **`McAvcEncSeqCtrl`** (`0x43c4320f`) |
| Componente (ruta de build) | `Avbb-MovieCodec_131H` (`0x43c41227`) |
| Id del módulo en el logger | `0x0e` (`movs r1,#0xe` en las **82** llamadas al logger del módulo) |
| Ids de mensaje atendidos | **18** (`0x8101`–`0x8112`), 12 con nombre |
| Nº de línea del `.cpp` recuperados | **35** (líneas 89 … 2237) |

**La sigla `ENCSEQCTRL` NO se desarrolla**: no hay ninguna base textual en el binario
para expandirla. Lo que sí está en los bytes es la **clase de C++** que la implementa
(`McAvcEncSeqCtrl`, nombre RTTI en `0x43c4320f`), de donde se lee que el prefijo `Mc`
corresponde al componente **MovieCodec** (`Avbb-MovieCodec_131H`, ruta de build en
`0x43c41227`) y que `Avc`/`Enc`/`SeqCtrl` son lostokens `Avc`, `Enc` y `SeqCtrl` de los
nombres de clase. Eso es **desarrollo por RTTI**, no por conjetura.

---

## 2. Qué es `[ENCSEQCTRL]`

`[ENCSEQCTRL]` es el **etiquetado de trazas** de la clase `McAvcEncSeqCtrl`: el
**controlador de la secuencia de codificación AVC/H.264** (vídeo) del subsistema
MovieCodec. No es un módulo de primer nivel con su propio "gerente de recursos": es la
clase que **recibe los comandos del codificador y los ejecuta como una secuencia
maquinada**, midiendo todo en unidades **VFC** (*video frame counter*).

Las 46 trazas viven en un **bloque contiguo** de `.rodata` (`0x43c4bce5`–`0x43c4c796`,
2738 B). La **única cadena intercalada** en ese bloque que no es `[ENCSEQCTRL]` es el
propio nombre del fichero fuente, `seqCtrl/mcAvcEncSeqCtrl.cpp` (`0x43c4bd0f`). Los
nombres de clase y las firmas `__PRETTY_FUNCTION__` de la misma unidad vienen **justo
después** del bloque (`0x43c4c7dd`–`0x43c4caae`).

### 2.1 Arquitectura (verificada en los bytes)

```
McAvcEncModeMgr        (mcAvcEncModeMgr.cpp)      → gestor de MODO  [ENCMODEMGR]
   └─ McAvcEncModeReady / McAvcEncModeEncErr      → estados        [ENCMODESTT]/[ENCMODEERR]
        └─ McAvcEncSeqCtrl  (seqCtrl/mcAvcEncSeqCtrl.cpp)  → SECUENCIA  [ENCSEQCTRL]   ← este hito
             ├─ McAvcEncVideo24P/30P25P/60I50I/60P50PSeqCtrl  → vídeo  [ENCVIDSEQ ]
             └─ McAvcEncAudioSeqCtrlState*                     → audio  [ENCAUDSTAT]/[ENCAUDOUCR]
```

Cadena de llamadas verificada (patrón `bl` de 32 bits, decodificación manual):

* `McAvcEncModeReady::ExecCodecIfBeginEnc` → `McAvcEncSeqCtrl::ExecSeqBeginEnc`
  (`bl 0x435d90ac` en `0x435d6188`).
* `McAvcEncModeReady::ExecCodecIfStillEnc` → `McAvcEncSeqCtrl::ExecSeqStillEnc`
  (`bl 0x435d7d60` en `0x435d6100`).
* `McAvcEncModeEncErr` → `McAvcEncSeqCtrl::ExecSeqTermEnc` (`bl 0x435d84cc` en `0x435d3d30`).
* `McAvcEncSeqCtrl::ProcMsg` (`0x435d900e`) despacha por **tipo de mensaje**:
  `cmp r3,r2` → `ProcMCMsg` (`0x435d882c`, llamada en `0x435d9022`);
  `movw r2,#0x2103` + `cmp r3,r2` → `ProcAvcMsg` (`0x435d8d38`, llamada en `0x435d9028`);
  cualquier otro tipo → traza de error con `Line:%d` = **1052** (`0x435d9048`).

### 2.2 Los estados

El estado de la secuencia es un **u32 en `obj+0x15B84`**:

* el **getter** es la función `0x43a5d2da` (`add.w r0,r0,#0x15800` en `0x43a5d2da`,
  `add.w r0,r0,#0x384` en `0x43a5d2de`, `ldr r0,[r0]` en `0x43a5d2e2`, `bx lr`): lee un
  u32 en `obj+0x15B84`;
* el **setter** es la función `0x435d715c`: calcula `r4 = obj+0x15800+0x384`
  (`add.w r4,r4,#0x15800` en `0x435d7160` + `add.w r4,r4,#0x384` en `0x435d7166`),
  anuncia `[ENCSEQCTRL][state]0x%x -> 0x%x` (`0x43c4bda2`) y **escribe** el valor nuevo
  (`str r5,[r4]` en `0x435d7180`);
* tiene **17 llamadores** en toda la imagen: 14 dentro del módulo (`0x435d5f86`,
  `0x435d72c0`, `0x435d740e`, `0x435d74e0`, `0x435d75d0`, `0x435d7972`, `0x435d7b3a`,
  `0x435d7be4`, `0x435d7d04`, `0x435d7eee`, `0x435d87f4`, `0x435d8de0`, `0x435d8f90`,
  `0x435d9476`) y **3 fuera**, en los *accesores inline* de la misma clase emitidos en
  otra unidad de traducción (`0x43a5d2ca` → estado 2, `0x43a5d38c` → estado 3,
  `0x43a5d3e2` → estado 3);
* los **valores de estado observados** son **0, 1, 2, 3, 4, 6, 7, 8, 10 y 11**
  (p. ej. `movs r1,#7` en `0x435d7bb4` → `ExecSeqEncReady2StillState` → setter en
  `0x435d7be4`; `movs r1,#0xb` (=11) en `0x435d8f8e`; `movs r1,#8` en `0x435d87e4`).
  Los estados 5 y 9 no aparecen como destino del setter → **NO VERIFICADO** si existen.

Los métodos `Exec*State` (`ExecSeqStillEncState`, `ExecSeqErrEncReadyState`,
`ExecSeqEncodeState`, `ExecSeqEncReady2StillState`, `ExecSeqInactiveState`,
`ExecSeqEncReadyState`) **no tienen ningún `bl` directo**: se invocan por tabla
(virtual / tabla de estados), no por llamada directa. **NO VERIFICADO**: qué valor de
estado corresponde a cada método.

### 2.3 Los mensajes: 18 ids, `0x8101`–`0x8112`

`ProcAvcMsg` (`0x435d8d38`) lee el id de mensaje como **u16 en `[msg+2]`**
(`ldrh r2,[r1,#2]` en `0x435d8d3e`) y el error en **`[msg+0xc]`**
(`ldr r3,[r4,#0xc]` en `0x435d8d78`). El índice se calcula con
`mvn r3,#0x8100` (`0x435d8d3a`) + `adds r3,r2,r3` (`0x435d8d44`), es decir
`idx = msgid − 0x8101`, y se acota con `cmp r3,#0x11` / `bhi` (`0x435d8d46`).
El salto es `tbh [pc,r3,lsl#1]` (`0x435d8d4c`) con **18 entradas** en `0x435d8d50`:

| id | destino del `tbh` | nombre registrado | cadena |
|---|---|---|---|
| `0x8101` | `0x435d8d74` | `MSGID_AVC_ENC_VIDEO_OPEN_COMP` | `0x43c4c3a3` |
| `0x8102` | `0x435d8de6` | `MSGID_AVC_ENC_VIDEO_CLOSE_COMP` | `0x43c4c3d8` |
| `0x8103` | `0x435d8e08` | `MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE_COMP` | `0x43c4c40e` |
| `0x8104` | `0x435d8e2a` | `MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP` | `0x43c4c44f` |
| `0x8105` | `0x435d8e4c` | `MSGID_AVC_ENC_VIDEO_ENC_PICTURE_COMP` | `0x43c4c490` |
| `0x8106` | `0x435d8e6e` | `MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE_COMP` | `0x43c4c4cc` |
| `0x8107` | `0x435d8e90` | `MSGID_AVC_ENC_VIDEO_FINALIZE_COMP` | `0x43c4c50e` |
| `0x8108` | `0x435d8eb2` | `MSGID_AVC_ENC_VIDEO_RELEASE_ES_COMP` | `0x43c4c547` |
| `0x8109` | `0x435d8f1e` | `MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO_COMP` | `0x43c4c5fd` |
| `0x810a` | `0x435d8f40` | `MSGID_AVC_ENC_VIDEO_SET_FACE_INFO_COMP` | `0x43c4c644` |
| `0x810b`–`0x8110` | `0x435d8f62` (rama por defecto) | *sin nombre* | — |
| `0x8111` | `0x435d8ed4` | `MSGID_AVC_ENC_VIDEO_RELEASE_PICTURE_NOTIFY` | `0x43c4c582` |
| `0x8112` | `0x435d8ef6` | `MSGID_AVC_ENC_VIDEO_GET_ES_NOTIFY` | `0x43c4c5c4` |

Los 12 nombres se **verifican por el propio código**: cada rama del `tbh` carga
literalmente la cadena con el nombre del mensaje que registra. Los 6 ids sin nombre
(`0x810b`–`0x8110`) caen en la rama por defecto, que registra
`[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d` (`0x43c4bce5`) y
`[ENCSEQCTRL]ProcAvcMsg: Err = %x, MsgId = %x` (`0x43c4c682`).

### 2.4 La tabla O/U Crank (57 entradas)

`[ENCSEQCTRL][O/U Crank] Table[%d] fR[0x%x] sR[0x%x]` (`0x43c4bd2b`) y
`[ENCSEQCTRL]OuCrank Config Err: FrameRate = %x,SamplingRate = %x` (`0x43c4bd5f`) se
emiten desde `0x435d70a2`, que busca en una **tabla de 57 entradas de 8 B en
`0x43b93bf4`** (`add r1,pc` en `0x435d70aa` → `0x43b93bf4`; bucle `adds r3,#8` /
`cmp r4,#0x39` en `0x435d7116`/`0x435d7118`).

Layout de cada entrada (verificado):
* `+0` u32 = «frame rate» (valores **2, 3, 4, 5, 6, 7, 8, 9, 10**);
* `+4` u32 cuyo **byte bajo** es el código de «sampling rate» comparado
  (**0x3c, 0x32, 0x1e, 0x18, 0x14, 0x10, 0x0c, 0x0a, 0x08, 0x06, 0x04, 0x02, 0x01**);
* `+5` u8 = valor devuelto (0x01 en las 57 entradas);
* el emparejamiento es `u32@+0 == r8` **y** `byte@+4 == r7`
  (`ldr r2,[r5,r3]` / `ldrb r2,[r2,#4]` en `0x435d70e8`/`0x435d70f0`).

**NO VERIFICADO**: la semántica de los valores (no hay texto que los nombre) y por qué el
campo de +4 es de 32 bits si sólo se compara su byte bajo.

### 2.5 Números de línea del fuente (35, verificados)

La macro de log tiene esta firma (verificada desensamblando el logger `0x43a4e534`):
`log(logger /*r0*/, module_id /*r1*/, level /*r2*/, format /*r3*/, varargs en pila)`.
`Line:%d` es una **constante de compilación** (`movw r3,#imm` + `str r3,[sp,#k]`), así que
se puede recuperar la línea del `.cpp` de cada traza. `analysis/s139_encseqctrl/line_numbers.py`
recupera **35** líneas de `seqCtrl/mcAvcEncSeqCtrl.cpp`, de la **89** a la **2237**:

| línea | función | traza |
|---|---|---|
| 89, 149, 166, 211, 229 | `0x435d7608` `ExecSeqActEnc` | `File:%s, Func:%s() ,Line:%d` |
| 321 | `0x435d6ad0` `ExecSeqAllocUserDataArea` | `File:%s, Func:%s() ,Line:%d` |
| 429 | `0x435d90ac` `ExecSeqBeginEnc` | `File:%s, Func:%s() ,Line:%d` |
| 655, 673 | `0x435d84cc` `ExecSeqTermEnc` | `File:%s, Func:%s() ,Line:%d` |
| 713, 725, 741, 763 | `0x435d7d60` `ExecSeqStillEnc` | `File:…` / `File:…, State:0x%x->0x%x` |
| 790 | `0x435d6bc8` `ExecSeqApllyUserDataGop` | `File:%s, Func:%s() ,Line:%d` |
| 834 | `0x435d6c94` `ExecSeqApplyUserDataPic` | `File:%s, Func:%s() ,Line:%d` |
| 858 | `0x435d6d60` `ExecSeqMuteAudioCapture` | `File:%s, Func:%s() ,Line:%d` |
| 923, 943 | `0x435d6df8` `ExecSeqSetEncReadPt` | `File:%s, Func:%s() ,Line:%d` |
| 997, 1025 | `0x435d6f04` `ExecSeqInitEsApi` | `File:%s, Func:%s() ,Line:%d` |
| 1052, 1058 | `0x435d900e` `ProcMsg` | `File:…` / `File:…, Stat` |
| 1143 | `0x435d8d38` `ProcAvcMsg` | `File:%s, Func:%s() ,Line:%d` |
| 1245 | `0x435d882c` `ProcMCMsg` | `File:%s, Func:%s() ,Line:%d` |
| 1265, 1315 | `0x435d7bf8` `ExecSeqInactiveState` | `File:%s, Func:%s() ,Line:%d` |
| 1370, 1386, 1402 | `0x435d8a84` `ExecSeqEncReadyState` | `File:%s, Func:%s() ,Line:%d` |
| 1510 | `0x435d7b70` `ExecSeqEncReady2StillState` | `Func:%s() ,Line:%d, State:0x%x->0x%x` |
| 1593 | `0x435d72f8` (auxiliar) | `File:%s, Func:%s() ,Line:%d` |
| 1629 | `0x435d7040` `ExecSeqStillEncState` | `File:%s, Func:%s() ,Line:%d` |
| 1697 | `0x435d79cc` `ExecSeqEncodeState` | `File:%s, Func:%s() ,Line:%d,Err = %x` |
| 2168, 2237 | `0x435d7f34` `CalcEncStartStopTimingForSysHS` | `Invalid syshsCnt File:%s, Func:%s() ,Line:%d` |

Esto acota el `.cpp` original: **≥2237 líneas**.

---

## 3. Las 46 trazas, con dirección y sub-bloque

| # | vaddr | sub-bloque | texto (inicio) |
|---|---|---|---|
| 1 | `0x43c4bce5` | LOG_MACRO | `[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d ` (48 sitios) |
| 2 | `0x43c4bd2b` | O_U_CRANK | `[ENCSEQCTRL][O/U Crank] Table[%d] fR[0x%x] sR[0x%x]` |
| 3 | `0x43c4bd5f` | O_U_CRANK | `[ENCSEQCTRL]OuCrank Config Err: FrameRate = %x,SamplingRate = %x ` |
| 4 | `0x43c4bda2` | STATE | `[ENCSEQCTRL][state]0x%x -> 0x%x ` |
| 5 | `0x43c4bdc4` | TIMING_WARNING | `[ENCSEQCTRL]Warning, m_beginEncCompTime < refTime, change state forcibly` |
| 6 | `0x43c4be0e` | LOG_MACRO | `[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d,Err = %x ` |
| 7 | `0x43c4be41` | STATE | `[ENCSEQCTRL]Func:%s() ,Line:%d, State:0x%x->0x%x ` |
| 8 | `0x43c4be74` | CHIP_MODE | `[ENCSEQCTRL][AVC ENC SEQ CTRL] Chip Mode = %x ` |
| 9 | `0x43c4bea4` | STATE | `[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d, State:0x%x->0x%x ` |
| 10 | `0x43c4bee0` | SYSHS | `[ENCSEQCTRL]Invalid syshsCnt File:%s, Func:%s() ,Line:%d ` (2 sitios) |
| 11 | `0x43c4bf1b` | PIN_SUPPLY | `[ENCSEQCTRL]WRN: Pin Supply Timing UNKNOWN ` (2 sitios) |
| 12 | `0x43c4bf48` | PIN_SUPPLY | `[ENCSEQCTRL]EXEC TIME = %x PIN SUPPLY TIMING = %x REVISED VFCNUM = %d` (2 sitios) |
| 13 | `0x43c4bf8f` | OU_STOP | `[ENCSEQCTRL]OU StopInfo(NrmlTerm:%x,OuTerm:%x=((%x+%x)*smpl(%x)),Stt:%x,Stp:%x(%x)->%x ` |
| 14 | `0x43c4bfe8` | FRAME_DEBUG | `[ENCSEQCTRL]abcd[%d] eTime[0x%x] cTime[0x%x] revFA[%d] FramePos[%d] revTA[%d] vNum[%d]` |
| 15 | `0x43c4c040` | REVISE_NUM | `[ENCSEQCTRL][Begin][odd] ReviseNum Set to zero [%d]` |
| 16 | `0x43c4c075` | REVISE_NUM | `[ENCSEQCTRL][Begin][odd] ReviseNum Set to one  [%d]` |
| 17 | `0x43c4c0aa` | REVISE_NUM | `[ENCSEQCTRL][Begin][even] ReviseNum Set to zero [%d]` |
| 18 | `0x43c4c0e0` | REVISE_NUM | `[ENCSEQCTRL][Begin][even] ReviseNum Set to one  [%d]` |
| 19 | `0x43c4c116` | REVISE_NUM | `[ENCSEQCTRL][Term][odd] ReviseNum Set to one [%d]` |
| 20 | `0x43c4c149` | REVISE_NUM | `[ENCSEQCTRL][Term][odd] ReviseNum Set to zero  [%d]` |
| 21 | `0x43c4c17e` | REVISE_NUM | `[ENCSEQCTRL][Term][even] ReviseNum Set to one [%d]` |
| 22 | `0x43c4c1b2` | REVISE_NUM | `[ENCSEQCTRL][Term][even] ReviseNum Set to zero  [%d]` |
| 23 | `0x43c4c1e8` | SYSHS | `[ENCSEQCTRL]HighSpeed Rec is set to zero [%d]` |
| 24 | `0x43c4c217` | TERM_VFC | `[ENCSEQCTRL]MCodec%d changed termEncodeVfc %d->%d` |
| 25 | `0x43c4c24a` | TERM_VFC | `[ENCSEQCTRL]TermEnc TimeInfo = %x, RefTime(VFC) = %x, EnsStopTime(VFC) = %x EnsStopTimeAudio(VFC) = %x ` |
| 26 | `0x43c4c2b3` | REF_TIMER | `[ENCSEQCTRL]CheckSendFirstRefTimer = %x ` |
| 27 | `0x43c4c2dd` | REF_TIMER | `[ENCSEQCTRL]CheckSendFirstRefTimer NOP ` |
| 28 | `0x43c4c306` | REPLY_ID | `[ENCSEQCTRL]%s() [%s] Invalid replyId !!!!` |
| 29 | `0x43c4c332` | SA_CONFIRM | `[ENCSEQCTRL]AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT(msgId:0x%x)::mid:0x%x,cid:0x%x,err:%x,cdcId:0x%x,replyId:0x%x` |
| 30 | `0x43c4c3a3` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_OPEN_COMP ERR = %x ` |
| 31 | `0x43c4c3d8` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_CLOSE_COMP ERR = %x ` |
| 32 | `0x43c4c40e` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE_COMP ERR = %x ` |
| 33 | `0x43c4c44f` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP ERR = %x ` |
| 34 | `0x43c4c490` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_ENC_PICTURE_COMP ERR = %x ` |
| 35 | `0x43c4c4cc` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE_COMP ERR = %x ` |
| 36 | `0x43c4c50e` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_FINALIZE_COMP ERR = %x ` |
| 37 | `0x43c4c547` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_RELEASE_ES_COMP ERR = %x ` |
| 38 | `0x43c4c582` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_RELEASE_PICTURE_NOTIFY ERR = %x ` |
| 39 | `0x43c4c5c4` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_GET_ES_NOTIFY ERR = %x ` |
| 40 | `0x43c4c5fd` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO_COMP ERR = %x ` |
| 41 | `0x43c4c644` | MSGID_COMP | `…MSGID_AVC_ENC_VIDEO_SET_FACE_INFO_COMP ERR = %x ` |
| 42 | `0x43c4c682` | PROCAVCMSG | `[ENCSEQCTRL]ProcAvcMsg: Err = %x, MsgId = %x ` |
| 43 | `0x43c4c6b1` | BEGIN_TIMEINFO | `[ENCSEQCTRL]BeginEnc TimeInfo = %x, RefTime(VFC) = %x, EnsStartTime(VFC) = %x , EncStartTimeAudio(VFC) = %x ` |
| 44 | `0x43c4c71f` | LOG_MACRO | `[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d, Stat ` |
| 45 | `0x43c4c74f` | SEMAPHORE | `[ENCSEQCTRL]wai semaphore error, Err:%d, File:%s, Func:%s() ,Line:%d ` |
| 46 | `0x43c4c796` | SEMAPHORE | `[ENCSEQCTRL]sig semaphore error, Err:%d, File:%s, Func:%s() ,Line:%d ` |

**Reparto por sub-bloque** (18 sub-bloques, mutuamente excluyentes):
`MSGID_COMP` 12, `REVISE_NUM` 8, `LOG_MACRO` 3, `STATE` 3, `O_U_CRANK` 2, `SYSHS` 2,
`PIN_SUPPLY` 2, `TERM_VFC` 2, `REF_TIMER` 2, `SEMAPHORE` 2, y 1 cada uno de
`BEGIN_TIMEINFO`, `CHIP_MODE`, `FRAME_DEBUG`, `OU_STOP`, `PROCAVCMSG`, `REPLY_ID`,
`SA_CONFIRM`, `TIMING_WARNING`.

---

## 4. Funciones que las referencian (32) y su método

El nombre de cada función se ha obtenido de la cadena `__PRETTY_FUNCTION__` que la
función referencia por PIC (mismo mapa estricto): es la **firma completa** que el
firmware guarda en `.rodata`.

| función | sitios | método (firma RTTI) |
|---|---|---|
| `0x435d6ad0` | 1 | `McAvcEncSeqCtrl::ExecSeqAllocUserDataArea(CMD_ALLOC_USER_DATA_AREA*)` |
| `0x435d6b3c` | 1 | `McAvcEncSeqCtrl::ExecSeqSetSeqParam(CMD_SET_SEQ_PARAM*)` |
| `0x435d6bc8` | 2 | `McAvcEncSeqCtrl::ExecSeqApllyUserDataGop(CMD_APPLY_USER_DATA_GOP*)` |
| `0x435d6c94` | 2 | `McAvcEncSeqCtrl::ExecSeqApplyUserDataPic(CMD_APPLY_USER_DATA_PIC*)` |
| `0x435d6d60` | 1 | `McAvcEncSeqCtrl::ExecSeqMuteAudioCapture(CMD_MUTE_AUDIO_CAPTURE*)` |
| `0x435d6df8` | 2 | `McAvcEncSeqCtrl::ExecSeqSetEncReadPt(CMD_SET_ENC_READ_POINTER*)` |
| `0x435d6f04` | 3 | `McAvcEncSeqCtrl::ExecSeqInitEsApi(CMD_INIT_ES_API_PARAM*)` |
| `0x435d7040` | 1 | `McAvcEncSeqCtrl::ExecSeqStillEncState()` |
| `0x435d70a2` | 2 | *(auxiliar: tabla O/U Crank)* |
| `0x435d715c` | 1 | *(setter del estado)* |
| `0x435d7190` | 3 | `McAvcEncSeqCtrl::ExecSeqErrEncReadyState()` |
| `0x435d72f8` | 2 | *(auxiliar)* |
| `0x435d7488` | 1 | *(auxiliar: aviso de `m_beginEncCompTime`)* |
| `0x435d74f4` | 2 | `McAvcEncSeqCtrl::ExecSeqInActChip(CMD_INACT_CHIP*, callback_if*)` |
| `0x435d7608` | 5 | `McAvcEncSeqCtrl::ExecSeqActEnc(CMD_ACT_ENC*, callback_if*)` |
| `0x435d79cc` | 3 | `McAvcEncSeqCtrl::ExecSeqEncodeState()` |
| `0x435d7b70` | 1 | `McAvcEncSeqCtrl::ExecSeqEncReady2StillState()` |
| `0x435d7bf8` | 4 | `McAvcEncSeqCtrl::ExecSeqInactiveState()` |
| `0x435d7d60` | 4 | `McAvcEncSeqCtrl::ExecSeqStillEnc(CMD_STILL_ENC*, callback_if*)` |
| `0x435d7f34` | 4 | `McAvcEncSeqCtrl::CalcEncStartStopTimingForSysHS(UInt32, UInt8)` |
| `0x435d8128` | 1 | *(auxiliar: OU StopInfo)* |
| `0x435d8206` | 1 | *(auxiliar: volcado `abcd[…]`)* |
| `0x435d832c` | 11 | *(auxiliar: `ReviseNum` par/impar)* |
| `0x435d84cc` | 5 | `McAvcEncSeqCtrl::ExecSeqTermEnc(CMD_TERM_ENC*, callback_if*)` |
| `0x435d882c` | 2 | `McAvcEncSeqCtrl::ProcMCMsg(const MSG_MC_AVC_ENC*)` |
| `0x435d8988` | 3 | *(auxiliar: `CheckSendFirstRefTimer`)* |
| `0x435d8a84` | 3 | `McAvcEncSeqCtrl::ExecSeqEncReadyState()` |
| `0x435d8c08` | 1 | `McAvcEncSeqCtrl::GetReplyId()` |
| `0x435d8c3c` | 1 | *(auxiliar: evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT`)* |
| `0x435d8d38` | 14 | `McAvcEncSeqCtrl::ProcAvcMsg(const MSG_MC_AVC_ENC*)` |
| `0x435d900e` | 2 | `McAvcEncSeqCtrl::ProcMsg(const MSG_MC_AVC_ENC*)` |
| `0x435d90ac` | 7 | `McAvcEncSeqCtrl::ExecSeqBeginEnc(CMD_BEGIN_ENC*, callback_if*)` |

**25 de las 32** referencian además la cadena del fichero
`seqCtrl/mcAvcEncSeqCtrl.cpp` (`0x43c4bd0f`, 61 sitios en toda la imagen); las 7 restantes
son auxiliares que emiten trazas sin el prefijo `File:`.

### 4.1 Quién llama al módulo (entradas)

* `McAvcEncModeReady` (`mcAvcEncModeReady.cpp`) → `ExecSeqBeginEnc` (`0x435d6188`) y
  `ExecSeqStillEnc` (`0x435d6100`).
* `McAvcEncModeEncErr` (`mcAvcEncModeEncErr.cpp`) → `ExecSeqTermEnc` (`0x435d3d30`).
* `McAvcEncSeqCtrl::ProcMsg` → `ProcMCMsg` (`0x435d9022`) y `ProcAvcMsg` (`0x435d9028`).
* `ProcAvcMsg` → `GetReplyId`/`AVSC_CID_…` (vía `0x435d8d9e`), `CheckSendFirstRefTimer`
  (vía `0x435d8dc2`).
* `ExecSeqEncReadyState` → `ExecSeqEncReady2StillState` (`0x435d8ae0`).

**NO VERIFICADO**: quién crea el objeto `McAvcEncSeqCtrl` (no hay punteros absolutos de
4 B a sus métodos en toda la imagen, luego la tabla de métodos está en forma relativa o
se construye en ejecución).

---

## 5. Ficheros fuente

* **`seqCtrl/mcAvcEncSeqCtrl.cpp`** (`0x43c4bd0f`) — fichero propio del módulo.
* Hermanos del mismo bloque (verificados en los bytes, no son de este módulo):
  `seqCtrl/mcAvcEncSeqCtrlParam.cpp` (`0x43c4cb12`), `seqCtrl/mcAvcEncUserDataMgr.cpp`
  (`0x43c4cbb0`), `mcAvcEncModeMgr.cpp` (`0x43c4acb9`), `mcAvcEncModeReady.cpp`
  (`0x43c4b169`), `mcAvcEncModeEncErr.cpp` (`0x43c4a980`),
  `seqCtrl/audio/mcAvcEncAudioSeqCtrlState*.cpp` (`0x43c4b36a`, `0x43c4b46e`,
  `0x43c4b5b4`, `0x43c4b6f0`).
* El **módulo hermano de vídeo** es `[ENCVIDSEQ ]` (89 trazas, 129 sitios, 37 funciones
  en `0x435d9bbc`–`0x435dcbc8`), no `[ENCSEQCTRL]`.
* Ruta de build (componente): `…/Avbb-MovieCodec_131H/src/…` (`0x43c41227`).

---

## 6. Relación con los hitos previos

| Hito | Relación | Evidencia |
|---|---|---|
| **S114** (motor de secciones de la captura) | **Ninguna directa**: el motor de secciones (`Capture<Etapa>_Selector.cpp`, ids `0x00`–`0x10`) es de la captura de **still**; `[ENCSEQCTRL]` es del MovieCodec y controla la secuencia de **vídeo**. Comparten el concepto de "etapa" pero no el código: no hay ninguna llamada entre `0x435d6ad0`-`0x435d90ac` y los manejadores de sección de S114 (`0x437e9a70`–`0x437eb470`). | ausencia de `bl` cruzado |
| **S106** `[IMAGING_CAP]` | **Puente indirecto** por el **sincronizador** `[SYNCENCSTART]` (`mcSyncEncStart.cpp`, 13 trazas, 19 sitios, 6 funciones en `0x43620dd0`–`0x43621298`), que es quien fija el instante de inicio del codificador: `McSyncEncStart::SetBeginEncCompTime(MC_OBJECT_SERIAL_NUM, McAvcEncSeqCtrl*, MC_AVC_FRAMERATE)` (`0x43c7014c`), `SetBeginEncTimingVFC(…, McAvcEncSeqCtrlParam*)` (`0x43c700bb`), `SetEncStartTimeForThumbnail(…, McAvCtrlIf*)` (`0x43c7002f`). Trazas: `[SYNCENCSTART]MC[%d] comes earlier, beginEncTimingVFC:[%d]` (`0x43c6ffab`), `[SYNCENCSTART][WRN]m_mcAvcEncSeqCtrl Null…` (`0x43c6ffe7`). | `McAvcEncSeqCtrl*` en la firma |
| **S137** `[CTRLCORE]` / `[CDIAG]` | **Puente por la interfaz de códec**, no por llamada directa: `McAvcEncModeMgr` (`[ENCMODEMGR]`, `mcAvcEncModeMgr.cpp`) registra los comandos con `RecordCodecIfCmd: CmdCode:%x, CmdTime:%x, ExecTime:%x` (`0x43c4accd`) y los ejecuta con `ExecCodecIfCmd err = %d` (`0x43c4afa3`). El **despachador** de esa clase es `0x435d58b4`: lee el código de comando en `[cmd+2]` (`ldrb r6,[r1,#2]` en `0x435d58b8`) y discrimina **13 códigos numéricos** (`0x00, 0x03, 0x05, 0x10, 0x11, 0x13, 0x14, 0x16, 0x17, 0x30, 0x31, 0x60, 0x61`), registrando los **15 nombres `CMD_ID_*`** (`0x43c4ad8a`–`0x43c4af79`): `ACT_ENC`, `GET_REF_TIMER`, `INIT_ES_API_PARAM`, `INACT_CHIP`, `ALLOC_USER_DATA_AREA`, `BEGIN_ENC`, `SET_SEQ_PARAM`, `TERM_ENC`, `STILL_ENC`, `APPLY_USER_DATA_GOP`, `APPLY_USER_DATA_PIC`, `MUTE_AUDIO_CAPTURE`, `INIT_RC_BUFFER`, `SET_RC_WTPT`, `SET_ENC_READ_POINTER`. La capa `CodecIf` es `mcAvCtrlIf.cpp` (`0x43c4588c`) / `mcAvCtrlCore.cpp` (`0x43c454e8`), **distinta** de `cdCtrlCore.cpp` (`0x43c3b86c`) de S137; el cruce es el evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT` (`0x43c4c332`), que es el único `AVSC_CID` del binario. | nombres de fichero y token |
| **S132** `[CLK_CTRL]` | **Relación temporal indirecta y fuerte**: todo el módulo razona en **VFC** (`RefTime(VFC)`, `EnsStartTime(VFC)`, `EnsStopTime(VFC)`, `EnsStopTimeAudio(VFC)`, `REVISED VFCNUM`). El VFC es el contador de frame de vídeo, cuyo ritmo fija el `CLKTYPE`/`sysv_delay` de `[CLK_CTRL]` (`[CAMERA_MAIN]: init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus`, `0x43ca3be5`). El módulo **no menciona** `CLKTYPE` ni `sysv_delay` (0 apariciones en las 46 trazas) → no decide el reloj, **lo consume**. La conversión la hace la clase RTTI `McAvcRefTimerToVFCConverter` (`0x43c42d7f`). | tokens VFC + ruta de build |
| **S115** `[CAM_IMAGER]` | **Sin relación directa**: ninguna de las 46 trazas menciona `imager`, `sensor`, `shutter`, `expos`, `readout` ni `drive`. El módulo es **aguas abajo** del imager: consume los frames ya producidos (pin data) y sólo los **cronometra**. La única coincidencia semántica es `MCodec%d` (`0x43c4c217`) = el índice de instancia de MovieCodec (`MC_OBJECT_SERIAL_NUM`), no el sensor. | recuento de subcadenas |

### 6.1 Línea del obturador: **efecto nulo**

Barrido literal sobre las 46 trazas de `[ENCSEQCTRL]` (y sobre las 50 del A6300):

* `shut`, `silent`, `electro`, `mech`, `curtain`, `flicker` → **0 apariciones**
  (el único `shut` del binario sigue siendo el del silenciador **mecánico**, S131/S135);
* `sensor`, `imager`, `expos`, `drive`, `readout`, `bracket`, `sweep`, `interval`,
  `jpeg`, `liveview` → **0 apariciones**;
* `still` → 1 (`MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP`, `0x43c4c44f`) y
  `movie` → 2 (`…INITIALIZE_MOVIE_COMP` `0x43c4c40e`, `…SET_MOVIE_QUALITY_INFO_COMP`
  `0x43c4c5fd`): son **modos de inicialización del codificador**, no del obturador.

⇒ **Sin efecto en S51 (A/B/C = NO).** El módulo no menciona ni el obturador ni el
disparo ni la lectura del sensor ni tiempos de exposición; sólo **cronometra** los
frames en VFC y gestiona el audio del códec (O/U Crank).

---

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

Comparación **texto a texto** de las trazas (mismo criterio que S109/S110/S121):

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| cadenas con el token | **46** | **46** | **50** |
| textos distintos | 46 | 46 | 50 |
| referenciadas (estricta) | 46 | 46 | 50 |
| sitios de emisión | **96** | **96** | **100** |
| funciones emisoras | **32** | **32** | **34** |
| rango del código | `0x435d6ad0`–`0x435d90ac` | `0x435d4760`–`0x435d6d3c` | `0x435dc168`–`0x435de92c` |
| textos comunes con la A6000 | — | **46 / 46** | **45 / 50** |

### 7.1 A7S fw3.20 — módulo **idéntico**

* Las **46** trazas coinciden **una a una** (mismos textos, mismo orden, mismas
  direcciones relativas dentro del bloque).
* Los **mismos recuentos**: 46 cadenas, 46 referenciadas, **96 sitios, 32 funciones**.
* La **tabla de despacho de `ProcAvcMsg` es byte a byte idéntica**: los 18 `halfword`
  de la tabla `tbh` (`12 00 4b 00 5c 00 6d 00 7e 00 8f 00 a0 00 b1 00 e7 00 f8 00
  09 01 ×6 c2 00 d3 00`) son los mismos en `0x435d69e0` (A7S) que en `0x435d8d50`
  (A6000), y el prólogo `7f b5 6f f4 01 43 4a 88 05 46 0c 46 d3 18 11 2b 00 f2 0b 81
  df e8 13 f0` es idéntico byte a byte; sólo cambian las direcciones de los `bl` y de
  los literales (el código está en otro sitio del blob).
  → **los 12 ids con nombre y los 6 ids sin nombre son los mismos**.

⇒ El módulo `[ENCSEQCTRL]` **existe íntegro en la A7S fw3.20**; la fw3.21 de la A6000
no lo crea ni lo modifica: **no es un cambio de la A6000**.

### 7.2 A6300 fw2.01 — superset con 5 trazas nuevas

* 1 traza **sólo de la A6000** (la versión corta):
  `[ENCSEQCTRL]TermEnc TimeInfo = %x, RefTime(VFC) = %x, EnsStopTime(VFC) = %x
  EnsStopTimeAudio(VFC) = %x ` (`0x43c4c24a`).
* 5 trazas **sólo del A6300** (las 4 primeras son nuevas; la quinta es la versión
  larga de la anterior):

| vaddr (A6300) | texto | función emisora |
|---|---|---|
| `0x43d3b0e7` | `[ENCSEQCTRL]%s Remain=%d gopNum=%d startVfc=0x%x stopVfc=0x%x ouCrankStopVfc=0x%x` | `0x435dd7e4` |
| `0x43d3b13a` | `[ENCSEQCTRL]%s Remain=%d gopNum=%d startVfc=0x%x stopVfc=0x%x quickRestartVfc=0x%x` | `0x435dd8b8` |
| `0x43d3b18e` | `[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d Impossible to come here ` | `0x435dd8b8` |
| `0x43d3b432` | `[ENCSEQCTRL]TermEnc TimeInfo = … EnsRestartTime(VFC) = %x ` | `0x435ddc64` |
| `0x43d3b507` | `[ENCSEQCTRL]Audio Buffer Overflow detected in Terminate encode Sequence` | `0x435de2ac` |

⇒ El A6300 añade al mismo subsistema: **reinicio rápido** de la secuencia
(`quickRestartVfc`), **parada por crank** (`ouCrankStopVfc`), el tiempo de reinicio
(`EnsRestartTime(VFC)`) y una **detección de desbordamiento del buffer de audio** al
terminar la secuencia. Su `ProcAvcMsg` mantiene la **ventana de ids `0x8101`–`0x8112`**
(`mvn r3,#0x8100` en `0x435de58e` y `0x43626af8`) pero con una **tabla `tbh`
distinta** (18 entradas, mismos ids, más casos) → es una implementación ampliada.

---

## 8. NO VERIFICADO / abierto

1. **Significado de la sigla `ENCSEQCTRL`**: no hay base textual; se deja sin desarrollar.
2. **Qué valor de estado corresponde a cada método `Exec*State`**: los estados
   observados son 0, 1, 2, 3, 4, 6, 7, 8, 10, 11; **5 y 9** no aparecen como destino
   del setter. La correspondencia estado↔método no está en los bytes.
3. **Semántica de la tabla O/U Crank** (57 entradas): los valores numéricos no están
   nombrados en ninguna traza; no se puede afirmar qué son `f0` y el byte de `+4`.
4. **Los 6 ids de mensaje sin nombre** (`0x810b`–`0x8110`): caen en la rama por defecto;
   no hay texto que los identifique.
5. **Quién crea el objeto `McAvcEncSeqCtrl`**: no hay punteros absolutos de 4 B a sus
   métodos en toda la imagen.
6. **Qué es exactamente `VFC`** y su relación numérica con `CLKTYPE`/`sysv_delay`
   (S132): sólo se ha verificado que el módulo razona en VFC y que existe la clase
   `McAvcRefTimerToVFCConverter`.
7. **Qué es `m_beginEncCompTime`**: aparece por su nombre en la traza
   `0x43c4bdc4`, pero no se ha localizado su campo en el objeto.
8. **`MCodec%d`** (índice de instancia) y `MC_OBJECT_SERIAL_NUM`: la correlación es
   coherente con `[SYNCENCSTART]MC[%d]…`, pero no verificada byte a byte.
9. **Sentido de `ReviseNum`** (par/impar en `[Begin]`/`[Term]`): no hay texto que lo
   explique; sólo que se pone a 0 o a 1 según la paridad.

---

## 9. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## 10. Ficheros de este hito

* `analysis/s139_encseqctrl/encseqctrl.md` — este informe.
* `analysis/s139_encseqctrl/encseqctrl.json` — datos estructurados.
* `analysis/s139_encseqctrl/encseqctrl_raw.json` — datos crudos del escaneo.
* `analysis/s139_encseqctrl/scan_encseqctrl.py` — escáner principal (cadenas, sitios,
  funciones, diferencial).
* `analysis/s139_encseqctrl/verify_sites.py` — verificación independiente de los 96 sitios.
* `analysis/s139_encseqctrl/build_json.py` — consolida el JSON final.
* `analysis/s139_encseqctrl/line_numbers.py` — recuperación de los nº de línea del `.cpp`.
* `analysis/s139_encseqctrl/func_ident.py` — identifica funciones por sus cadenas.
* `analysis/s139_encseqctrl/pic.py`, `disasm.py`, `callers.py`, `msgid_table.py`,
  `sites_of_tokens.py`, `scan_other.py`, `scan_strings.py` — utilidades.
* `docs/capture/s139-encseqctrl.md` — nota breve.
* `tests/test_s139_encseqctrl.py` — tests sobre bytes reales.

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (35 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 46 apariciones de `[ENCSEQCTRL]` en la A6000 fw3.21 entre `0x43c4bce5` y
   `0x43c4c796`; **46** en la A7S fw3.20 y **50** en el A6300 fw2.01 → la etiqueta existe en las tres
   cámaras (a diferencia de los módulos "nuevos" de S130).
2. **Identidad de la clase verificada**: `McAvcEncSeqCtrl` (RTTI `0x43c4320f`),
   `seqCtrl/mcAvcEncSeqCtrl.cpp` `0x43c4bd0f` y el componente `Avbb-MovieCodec_131H` `0x43c41227`
   están presentes en los bytes; el evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT` `0x43c4c332` y
   la cadena `[SYNCENCSTART]` existen (13 apariciones) → los enlaces con S137 y S106 son reales.
3. **Diferencial**: A7S **idéntico** (46/46 textos, 96 sitios, 32 funciones y la tabla `tbh` de
   `ProcAvcMsg` byte a byte igual: `0x435d8d50` en la A6000 frente a `0x435d69e0` en la A7S);
   A6300 = **superset** (50 cadenas, 100 sitios, 34 funciones; 5 nuevas: `quickRestartVfc`,
   `ouCrankStopVfc`, `Remain/gopNum`, `EnsRestartTime(VFC)`, `Audio Buffer Overflow…`).
4. **Negativo acotado**: 0 apariciones de `shut`/`silent`/`electro`/`mech`/`sensor`/`imager`/
   `expos`/`drive`/`readout`/`bracket`/`sweep`/`flicker`/`curtain` en las 46 trazas → **sin efecto
   en S51**.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
