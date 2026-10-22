# S121 — `[AIP]`: el Audio IP de la cámara

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Solo análisis estático de bytes: no se ha ejecutado firmware,
> no se ha usado la cámara y no se ha consultado REA ni Ghidra.
> Sin efecto en S51 (A/B/C = NO).

Datos: [`aip.json`](aip.json) · subconjunto reproducible de la comparación metodológica:
[`kill_refs_aip.json`](kill_refs_aip.json) · escáner: [`scan_aip.py`](scan_aip.py) ·
Nota de captura: [`docs/capture/s121-aip.md`](../../docs/capture/s121-aip.md) ·
Test: [`tests/test_s121_aip.py`](../../tests/test_s121_aip.py).

## 1. Qué es `[AIP]`

`[AIP]` es el **Audio IP**: la capa de audio del firmware de la cámara, con una jerarquía
`SaWrapper` → `SaDriverBase`/`SaDriverZoomNr`/`SaDriverLinearPhase` → `SaBackUpCtrl`/`SaSysvCtrl`
y un submódulo **LPS**.

La lectura **AIP = Audio IP** no es una expansión de siglas documentada en el firmware
(§9, NO VERIFICADO), sino una inferencia por contexto, con tres pruebas textuales en el mismo
bloque de datos:

1. Los nombres de clase RTTI **`9AudioIpIf`** (`0x43cdd82e`) y **`9SaWrapper`** (`0x43cdd839`)
   están **inmediatamente antes** de la primera cadena del módulo, `[AIP]SA OpenConfigCb Ack`
   (`0x43cdd844`).
2. En el mismo bloque conviven las trazas de los submódulos `Abb*` con prefijo **`[AudioIp]`**
   (`0x43cde614` `[AudioIp]SaBackUpCtrl ChangeBackUp Sa FINISH err %x`) y **`[AudioIP]`**
   (`0x43cde9e6` `[AUDIOIP]SaDriverFactory Err %x`): el firmware alterna `AIP` / `AudioIp` /
   `AudioIP` para el mismo subsistema.
3. S81 ya documentó el mismo nombre en la interfaz de depuración del ADF: las fases lineales de
   arranque `LinearPhaseSetAip0/Aip1Print` y `SetAip0/1` (§7).

El «SA» de `[AIP]` (`SaWrapper`, `SaDriverBase`, `SaBackUpCtrl`, `SaSysvCtrl`,
`SaDriverLinearPhase`) es la **capa `Sa*` del Audio IP**, **no** el acelerador escalar
`Camera::SaFuncDrv` de `[CAMERA_SA]` (S108): ninguna de las 37 trazas contiene `sa_func_*`
(§7).

## 2. Inventario

| cifra | valor |
|---|---|
| cadenas `[AIP]` | **37** |
| rango vaddr | `0x43cdd844` – `0x43cdec50` |
| rango file offset | `0x79c844` – `0x79dc50` |
| sitios PIC (regla estricta) | **37** (1 por cadena, 0 muertas) |
| funciones | **16** |
| sub-bloques por clase RTTI | **6** |

Todas las cadenas están referenciadas y cada una tiene **exactamente un** sitio de emisión bajo
la regla declarada (§8). Rango de código: `0x4355ae98` (SetFader, en el bloque de audio de
primer nivel) y `0x43926d1c`–`0x4392b6ac` (módulo `Sa*`, bloque `0x4392xxxx`).

## 3. Las 37 trazas

`sitio` = dirección del `add rX, pc` que materializa el puntero; `función` = prólogo Thumb
`push` más cercano hacia atrás.

| # | vaddr | texto | sitio | función |
|---|---|---|---|---|
| 1 | `0x43cdd844` | `[AIP]SA OpenConfigCb Ack` | `0x43926d2c` | `0x43926d1c` |
| 2 | `0x43cdd85e` | `[AIP]SA OpenConfigCb Ack Err errCode %x errState %x` | `0x43926d4a` | `0x43926d1c` |
| 3 | `0x43cdd893` | `[AIP]SA OpenConfigCb Comp` | `0x43926d7a` | `0x43926d1c` |
| 4 | `0x43cdd8ae` | `[AIP]SA OpenConfigCb Comp Err errCode %x errState %x` | `0x43926d98` | `0x43926d1c` |
| 5 | `0x43cdd8e4` | `[AIP]SA OpenConfigCb Err` | `0x43926db4` | `0x43926d1c` |
| 6 | `0x43cdd8fe` | `[AIP]SA CloseConfigCb Done` | `0x43926df8` | `0x43926de8` |
| 7 | `0x43cdd91a` | `[AIP]SA CloseCallback Err errCode %x errState %x` | `0x43926e16` | `0x43926de8` |
| 8 | `0x43cdd94c` | `[AIP]SA CloseCallback Err uniqueId %x ` | `0x43926e42` | `0x43926de8` |
| 9 | `0x43cdd9e3` | `[AIP][SA ANR MGR]SetAudioNrType %x` | `0x4392732a` | `0x439272dc` |
| 10 | `0x43cddab5` | `[AIP]SetFader m_fader.count %x` | `0x4355af04` | `0x4355ae98` |
| 11 | `0x43cde67a` | `[AIP]SaBackUpCtrl::UnREG CB OK` | `0x4392a722` | `0x4392a712` |
| 12 | `0x43cde69a` | `[AIP]SaBackUpCtrl::UnREG CB err %d` | `0x4392a73a` | `0x4392a712` |
| 13 | `0x43cde6be` | `[AIP]SaBackUpCtrl GetBackUp err bkId %x` | `0x4392a7b0` | `0x4392a76e` |
| 14 | `0x43cde77b` | `[AIP]SaBackUpCtrl::CreateBackUpLpsList Err` | `0x4392a9ca` | `0x4392a98c` |
| 15 | `0x43cde7a7` | `[AIP]SaBackUpCtrl::Init Sa OK id num = %d` | `0x4392aa46` | `0x4392aa00` |
| 16 | `0x43cde7d2` | `[AIP]SaBackUpCtrl::Init Sa err %d` | `0x4392aa5c` | `0x4392aa00` |
| 17 | `0x43cde7f5` | `[AIP]SaBackUpCtrl::Init Lps OK id num = %d` | `0x4392aa86` | `0x4392aa00` |
| 18 | `0x43cde821` | `[AIP]SaBackUpCtrl::Init Lps err %d` | `0x4392aa9c` | `0x4392aa00` |
| 19 | `0x43cde845` | `[AIP]SaBackUpCtrl::REG CB OK` | `0x4392aaec` | `0x4392aa00` |
| 20 | `0x43cde863` | `[AIP]SaBackUpCtrl::REG CB err %d` | `0x4392ab04` | `0x4392aa00` |
| 21 | `0x43cde885` | `[AIP]SaBackUpCtrl::WriteShadow2BakcupArea OK id num = %d` | `0x4392ab8e` | `0x4392ab76` |
| 22 | `0x43cde8bf` | `[AIP]SaBackUpCtrl::WriteShadow2BackupArea err %d` | `0x4392aba4` | `0x4392ab76` |
| 23 | `0x43cde900` | `[AIP]Sa OpenConfig Cmd %x Func %x` | `0x4392ac3a` | `0x4392ac30` |
| 24 | `0x43cde923` | `[AIP]Zma %x Ext %x Mbx %x` | `0x4392ac46` | `0x4392ac30` |
| 25 | `0x43cde957` | `[AIP]Sa Close Cmd %x Func %x Unq %x` | `0x4392acbe` | `0x4392acb4` |
| 26 | `0x43cde97c` | `[AIP]SaDriver CloseConfig` | `0x4392ace4` | `0x4392acb4` |
| 27 | `0x43cdea9e` | `[AIP]LPS OpenConfigCb Ack` | `0x4392b17c` | `0x4392b16c` |
| 28 | `0x43cdeab9` | `[AIP]LPS OpenConfigCb Ack Err errCode %x errState %x` | `0x4392b19a` | `0x4392b16c` |
| 29 | `0x43cdeaef` | `[AIP]Lps OpenConfigCb Comp OK` | `0x4392b1ce` | `0x4392b16c` |
| 30 | `0x43cdeb0e` | `[AIP]LPS OpenConfigCb Comp ErrCode %x ErrStatus %x` | `0x4392b1f8` | `0x4392b16c` |
| 31 | `0x43cdeb63` | `[AIP]LPS CloseConfigCb Comp` | `0x4392b25e` | `0x4392b254` |
| 32 | `0x43cdeb80` | `[AIP]LPS CloseCallback Err errCode %x errState %x` | `0x4392b27c` | `0x4392b254` |
| 33 | `0x43cdebb3` | `[AIP]LPS CloseCallback Err uniqueId %x ` | `0x4392b2a8` | `0x4392b254` |
| 34 | `0x43cdebdc` | `[AIP]LPS SetMailBox Err` | `0x4392b416` | `0x4392b392` |
| 35 | `0x43cdec04` | `[AIP]LPS GetMailBox Err` | `0x4392b4de` | `0x4392b46c` |
| 36 | `0x43cdec1c` | `[AIP]LPS GetMb Callback TimeOut Err` | `0x4392b512` | `0x4392b46c` |
| 37 | `0x43cdec50` | `[AIP]LPS SetLpsSysv Err` | `0x4392b6ac` | `0x4392b660` |

Las tres cadenas con espacio final (`0x43cdd94c`, `0x43cdebb3`) y la errata
`WriteShadow2BakcupArea`/`WriteShadow2BackupArea` (`0x43cde885`/`0x43cde8bf`) están tal cual en
los bytes; no se normalizan.

## 4. Mapa función → traza

| función | n | trazas |
|---|---|---|
| `0x4355ae98` | 1 | 10 |
| `0x43926d1c` | 5 | 1–5 (`SA OpenConfigCb`: Ack / Ack Err / Comp / Comp Err / Err) |
| `0x43926de8` | 3 | 6–8 (`SA CloseConfigCb Done`, `CloseCallback Err` errCode/errState, `…Err uniqueId`) |
| `0x439272dc` | 1 | 9 (`SetAudioNrType`) |
| `0x4392a712` | 2 | 11–12 (`UnREG CB` OK/err) |
| `0x4392a76e` | 1 | 13 (`GetBackUp err bkId`) |
| `0x4392a98c` | 1 | 14 (`CreateBackUpLpsList Err`) |
| `0x4392aa00` | 6 | 15–20 (`Init Sa` OK/err, `Init Lps` OK/err, `REG CB` OK/err) |
| `0x4392ab76` | 2 | 21–22 (`WriteShadow2BakcupArea`) |
| `0x4392ac30` | 2 | 23–24 (`Sa OpenConfig Cmd`, `Zma/Ext/Mbx`) |
| `0x4392acb4` | 2 | 25–26 (`Sa Close Cmd`, `SaDriver CloseConfig`) |
| `0x4392b16c` | 4 | 27–30 (`LPS OpenConfigCb`) |
| `0x4392b254` | 3 | 31–33 (`LPS CloseConfigCb`/`CloseCallback`) |
| `0x4392b392` | 1 | 34 (`LPS SetMailBox Err`) |
| `0x4392b46c` | 2 | 35–36 (`LPS GetMailBox Err`, `GetMb Callback TimeOut`) |
| `0x4392b660` | 1 | 37 (`LPS SetLpsSysv Err`) |

Nota: la llamada de `0x439272f2` apunta a `0x4392a76c` (2 B antes del prólogo `push` de
`0x4392a76e`; el `ldr r3,[pc,#0x60]` previo). La tabla cita el prólogo real.

## 5. Sub-bloques (clases RTTI)

Las cadenas están agrupadas en memoria; cada frontera coincide con el nombre de clase RTTI
contiguo en el mismo bloque de datos.

| sub-bloque | n | rango | marcador RTTI |
|---|---|---|---|
| `SaWrapper` | 8 | `0x43cdd844`–`0x43cdd94c` | `9AudioIpIf` `0x43cdd82e`, `9SaWrapper` `0x43cdd839` |
| `SaDriverZoomNr` | 1 | `0x43cdd9e3` | `14SaDriverZoomNr` `0x43cdda06` (tras la cadena) |
| `SetFader` | 1 | `0x43cddab5` | entre `14SaDriverZoomNr` y `3Abb` `0x43cddaf3` |
| `SaBackUpCtrl` | 12 | `0x43cde67a`–`0x43cde8bf` | `12SaBackUpCtrl` `0x43cde564` |
| `SaDriverBase` | 4 | `0x43cde900`–`0x43cde97c` | `12SaDriverBase` `0x43cde8f1` |
| `LPS` | 11 | `0x43cdea9e`–`0x43cdec50` | tras `10SaSysvCtrl` `0x43cdea07` y `19SaDriverLinearPhase` `0x43cdea14` |

En el mismo bloque `0x43cdcc00`–`0x43cdf400` hay otras clases que **no** emiten `[AIP]`:
`Abb` (`3Abb`), `AbbBackUpCtrl`, `AbbMicSensAdjustCtrl`, `AbbRecLevelCtrl`, `AbbSysvCtrl`,
`AbbWaitInitialize`, `AbbSysnd`, `AbbSysndBackUpCtrl`, `SaDriverDummy`, y las infraestructuras
`15AudioIpCmdQueue`, `13AudioIpDfsMgr`, `10AudioIpLog`, `14AudioIpLogCore`. Sus mensajes usan
`[AudioIp]`/`[AudioIP]`/`[SA]` y quedan **fuera** de este recuento (p. ej.
`[AudioIp]SaBackUpCtrl ChangeBackUp Sa FINISH err %x` `0x43cde614`,
`[SA]Lps WriteBackup` `0x43cde9xx`).
De ahí que en el bloque `0x43cdd844`–`0x43cdec50` haya **123 destinos PIC distintos** y solo 37
sean `[AIP]` (§8).

## 6. Vocabulario y estructura

### 6.1 Callbacks `OpenConfig` / `CloseConfig`

El patrón se repite en tres capas —`SA` (`SaWrapper`), `LPS` y el driver— con el mismo
vocabulario:

- **`Ack`**: el driver aceptó la petición de configuración (`Ack`, `Ack Err errCode %x errState %x`).
- **`Comp`**: la configuración se completó (`Comp`, `Comp Err errCode %x errState %x`;
  en LPS `Comp OK` / `Comp ErrCode %x ErrStatus %x`).
- **`Err`**: fallo sin más datos, o cierre anómalo (`CloseCallback Err uniqueId %x`).
- **`Done`**: cierre completado (`SA CloseConfigCb Done`).

Campos verificados en el desensamblado de `0x43926d1c` y `0x43926de8`:

- `0x43926d1c` despacha por el byte `[r1,#1] == 0x14`; toma `id` de `[r4,#4]`,
  `errState` de `[r4,#6]` y `errCode` de `[r4,#7]`.
- `0x43926de8` despacha por `[r1,#1] == 0x13`, lee `uniqueId` con `ldrb [r4,#4]`
  (`0x43926e4c`) y lo compara con el campo `[r5,#0x2c]` del objeto antes de loguear.

`ErrCode`/`ErrStatus` (LPS) y `errCode`/`errState` (SA) son **dos parejas de nombres para el
mismo contrato** mensaje→resultado; la semántica de cada valor no está en el firmware (§9).

### 6.2 Comandos: `Cmd` / `Func` / `Unq` / `Zma` / `Ext` / `Mbx`

- `0x4392ac30` (`Sa OpenConfig`) loguea `Cmd = [r4,#1]` y `Func = [r4,#9]`, y después
  `Zma = [r4,#0xa]`, `Ext = [r4,#0xb]`, `Mbx = [r4,#0xc]`; a continuación llama a
  `0x43b5e7f6` (open config del SaDriver).
- `0x4392acb4` (`Sa Close`) loguea `[r4,#1]`, `[r4,#9]` y `Unq = [r4,#8]`, y llama a
  `0x43b5e7ea` (close config).

Es decir: el mensaje de configuración lleva un **código de comando**, un **selector de función**
y tres campos de direccionamiento (`Zma`/`Ext`/`Mbx`); el de cierre repite comando y función y
añade un **identificador único** (`Unq`). Son los mismos nombres que usa el resto de
`SaDriverBase` (`SaDriver OpenConfig Err` `0x43cde93e`, `SetMailBox Err` `0x43cde997`,
`GetMailBox Err` `0x43cde9b0`, `SetVsyncSelect Err` `0x43cde9c9`).

### 6.3 `bkId` y la tabla de backup

`0x4392a76e` (`GetBackUp`) busca un `bkId` en una tabla de **350 (`0x15e`) entradas**;
`0x4392a98c` (`CreateBackUpLpsList`) recorre la misma tabla en **`0x43bd1964`**, con entradas de
**12 B** `{id u32 = 0x10c0000+n, offset u32, size u32}`, y copia ids y bases a la lista LPS.
`0x4392ab76` (`WriteShadow2BakcupArea`) vuelca con `0x43561458` un bloque de **`0x10c` B**.

`0x439272dc` (`[SA ANR MGR]SetAudioNrType`) obtiene el objeto con `0x4392a6c0`, resuelve
`bkId = 0x10e0000` con `0x4392a76c`, toma el **bit 3** (`and #8`) del byte devuelto y lo escribe
en `[r4,#0xf4]`, que es el `%x` de la traza: la traza publica **un bit de un registro de backup**,
no el tipo ANR completo.

`Init Sa` / `Init Lps` / `REG CB` / `UnREG CB` y `WriteShadow2BakcupArea` describen el ciclo de
vida de esa área de respaldo: crear la lista, inicializar SA y LPS, registrar/desregistrar
callbacks y escribir la sombra en el área de backup. Los `id num = %d` son el **número de
entradas** procesadas.

### 6.4 LPS: buzón y `sysv`

Los tres mensajes de LPS construyen un buffer corto en pila y llaman a `0x4392ad14`/`0x4392ad48`/
`0x4392ad7c`:

| función | tipo | longitud | contenido |
|---|---|---|---|
| `0x4392b392` SetMailBox | `0x82` | `0x2c` | id, campos del objeto |
| `0x4392b46c` GetMailBox | `0x83` | `0x28` | id, timeout |
| `0x4392b660` SetLpsSysv | `0x85` | `0x14` | `0x80\|0x14`, `0x85`, u32 id, `[obj#0x68]`, `0xb1`, `0x10` |

El byte de cabecera `0x80|len` y el segundo byte de tipo identifican el mensaje en la cola; el
`TimeOut Err` de `0x4392b46c` es la espera del callback del buzón. El formato exacto de la cola
`AudioIpCmdQueue` (`15AudioIpCmdQueue`) no se ha reconstruido (§9).

### 6.5 `SetFader`

`0x4355ae98` es la única traza `[AIP]` fuera del bloque `0x4392xxxx`. Valida
`[r0,#0x58] ∈ (2..4)` y `[r1] ≤ 1`, convierte el float `[r1,#4]`, lo divide por **100**, **20** u
otro divisor según `[r0,#0x78]`, guarda el entero en `[r4,#0xc0]` y loguea
`m_fader.count %x`. El campo `m_fader` del nombre de la traza identifica el objeto; el
significado físico de los divisores (dB, pasos, porcentaje) es **NO VERIFICADO**.

## 7. Relación con S81, S107 y S108

- **S81 (`[ADF]`, Audio/Video Data Framework)**: el ADF expone la inicialización del audio
  (`[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`) y los tipos
  `AUDIO_IP_CONFIG_TYPE_{VGS,PR,MF,BANDI_BASEDON_CONS,CONS,BANDI}`
  (`0x43c264fa`–`0x43c2659e`). En su interfaz de depuración `Proc` están las fases lineales
  `SetDec0/1`, **`SetAip0/1`**, **`GetSa0/1`**, `GetPin0/1`, `SetMb`, **`SetSa`** y la ruta de
  audio/zoom **`SetPath`**, `SetMixRatio`, **`SetFader`**, **`SetZoomNr`**, `ZOOM[0..2]`.
  Es el mismo vocabulario que este módulo (`SetFader` `0x4355ae98`, `SetAudioNrType`
  `0x439272dc`, `SaDriverLinearPhase` y `SaDriverZoomNr`): el ADF es el **cliente** que
  configura el Audio IP y recorre sus fases de arranque. `SetAip0/1` nombra el módulo
  directamente y es una de las pruebas de la lectura AIP = Audio IP.
- **S107 (`[CAMCORE]`)**: no hay relación directa en las trazas. `[CAMCORE]` gestiona recursos
  de imagen (SGC, RDC/PFR, AIF, `ResourceStack`) y su vocabulario (`sa_func_*`, `pbl_aif_*`) no
  aparece aquí; las dos «SA» son cosas distintas.
- **S108 (`[CAMERA_SA]`)**: **no es el mismo módulo**. `[CAMERA_SA]` (231 trazas,
  `0x43cc5286`–`0x43cef0d8`) instrumenta el **acelerador escalar** de la cámara
  (`Camera::SaFuncDrv`, API `sa_*`); `[AIP]` instrumenta la capa `Sa*` del **Audio IP**. Las
  dos familias comparten las tres letras «Sa» y el bloque de direcciones `0x43cdxxxx`, pero
  **ninguna** de las 37 trazas `[AIP]` contiene `sa_func_` ni nombres de la API escalar, y las
  clases RTTI de S108 no aparecen en el bloque de §5. La coincidencia de rango es de
  **enlazado**, no de código.

## 8. Método: por qué 37 y no 60

Regla adoptada (estricta, la misma de todo el informe):

> para cada `add rX, pc` (forma registro `0x4478`, `Rm = 15`), el valor del puntero sale del
> `ldr rX, [pc, #imm]` **más cercano hacia atrás sobre el mismo registro**; destino =
> `word_del_pool + (dir_add + 4)`.

En este módulo el hueco real entre el `ldr` y el `add` es de **2–6 B** (nunca más), y la regla
da **37 sitios / 37 cadenas / 0 muertas**.

La *kill analysis* canónica (`analysis/s106_imaging_cap/scan_pic_refs_v2.py`, la que S106 usa
para sus recuentos) da **60 pares**: **37 verdaderos y 23 falsos**. De los 23:

- **21** apuntan a **otra cadena real** del mismo bloque (p. ej. `0x4392a5ac` → `0x43cde614`
  `[AudioIp]SaBackUpCtrl ChangeBackUp Sa FINISH err %x`, no `[AIP]…Init Sa OK`;
  `0x4392ac3a` → `0x43cde900`, no `0x43cdec04`);
- **2** apuntan a una dirección que **no es cadena**: `0x4392a6f0` → `0x43f1c4b4` y
  `0x4392af24` → `0x43f1c5f4`. Ambos son `ldr r0,[pc,#0x18]; add r0,pc; pop {…}` que
  **devuelven** una constante de datos, no emiten log.

El falso positivo más instructivo es `0x4355bcb2` (kill analysis lo asigna a
`[AIP]SaBackUpCtrl::REG CB err %d`): su `ldr r0,[pc,#0x164]` está en `0x4355bcac`, pool
`0x4355be14`, valor `0x78f8d5` → `0x43ceb58b` =
`SA_PARAM_APL_LGR_YRATIO_SET_FIELD!, p_payload->p_movieQualityInf…`. El sitio **real** de
`0x43cde863` es `0x4392ab04` (ya en la tabla, fila 20). En cambio el otro sitio «raro»,
`0x4355af04`, **sí es verdadero**: `ldr r0,[pc,#0x40]` en `0x4355aefe`, pool `0x4355af40`,
`0x782bad` + `0x4355af08` = `0x43cddab5`.

Escaneo independiente propio (todos los `add rX, pc` de la imagen, sin ventana, emparejando con
el `ldr` más cercano del mismo registro):

| medida | valor |
|---|---|
| `add rX, pc` en la imagen | **95 599** |
| con `ldr` resoluble | **88 158** |
| destinos distintos dentro de `0x43cdd844`–`0x43cdec50` | **123** (37 `[AIP]` + 86 de otras familias del bloque) |
| cadenas `[AIP]` con más de un sitio | **0** |

→ confirma **1 sitio por cadena** y que el exceso de la kill analysis es un artefacto de su
ventana de búsqueda, no código real.

## 9. No verificado

- **Desarrollo de las siglas**: `AIP`, `SA`, `LPS`, `ANR`, `ZNR`, `Zma`, `Ext`, `Mbx`.
  `AIP = Audio IP` es inferencia contextual (§1), no una expansión del firmware.
- **Semántica** de cada valor de `errState`, `ErrStatus`, `result_code`, `Cmd`, `Func`, `Unq`,
  `bkId`, `id num` y `uniqueId`.
- **Formato exacto** de los mensajes de LPS y de la cola `AudioIpCmdQueue`; solo se conoce el
  tamaño y los bytes de cabecera de §6.4.
- Si `SetFader` (`0x4355ae98`) y `SetAudioNrType` (`0x439272dc`) operan sobre el **mismo objeto**
  `SaWrapper`; sus funciones están en bloques distintos y no se ha seguido el `this`.
- El **contenido** de las 350 entradas de `0x43bd1964` más allá del layout `{id, offset, size}`.
- Qué significan físicamente los divisores 100/20 de `SetFader`.

## 10. Diferencial

### A7S fw3.20

**37/37 textos idénticos**, 0 exclusivos en ambos sentidos
(`firmware/extracted/a7s-fw320/.../av-cam.bin`, file offsets `0x79305f`–`0x794165`; en la A6000
`0x79c844`–`0x79dc50`). El módulo **no cambió** entre fw3.20 y fw3.21: solo se movió de
posición. No es una etiqueta nueva de fw3.21 (a diferencia de `[CAM_IMAGER]` o
`[IMAGING_CAP]`).

### A6300 fw2.01

**63 cadenas** = las 37 de la A6000 **+ 26** (`0x8ae3e1`–`0x8afa6b`), y **ninguna** de la A6000
falta. Las 26 nuevas son del submódulo **ZNR/EE**:

- **25** con prefijo `[AIP][ZNR_EE]` (open/close config, `SetSaZoomNrSysvCallback`,
  `SetSaZoomNrState`, `SA_Start addr/size/iW/iR/oW`, `timingVfc`, `debug_info`, …);
- **1** `[AIP][ZNR]SetInstanceNumberExec Err %d`.

Es decir: la A6300 conserva el Audio IP de la A6000 y le **añade** la instrumentación del
`SaDriverZoomNrEe` (zoom electrónico / reducción de ruido), que en la A6000 no existe con ese
nombre. La A6300 **no** trae nada nuevo de `SaBackUpCtrl` ni de `LPS`.

## 11. Reproducción

```sh
.venv/bin/python analysis/s121_aip/scan_aip.py
.venv/bin/python -m pytest tests/test_s121_aip.py -q
```

`scan_aip.py` regenera `aip.json` y, si existe el mapa completo de la kill analysis, deja el
subconjunto congelado `kill_refs_aip.json` para que la comparación §8 sea reproducible sin
depender de `/tmp`.

---

## Revisión del agente principal (21-10-2026)

**Verificado byte a byte (correcto):**

1. **Recuento**: 37 cadenas `[AIP]` en `0x43cdd844`–`0x43cdec50`; en la A7S fw3.20 **las mismas
   37** (idénticas) y el A6300 fw2.01 tiene **63** = 37 + 26 (25 `[AIP][ZNR_EE]*` y
   `SetInstanceNumberExec Err %d`).
2. **Estructura**: 6 sub-bloques RTTI (SaWrapper 8, SaBackUpCtrl 12, SaDriverBase 4, LPS 11,
   SaDriverZoomNr 1, SetFader 1) y **16 funciones**; callbacks `Ack`/`Comp`/`Err` en tres capas
   (SA `0x43926d1c`/`0x43926de8` con `[r1,#1]==0x14`/`0x13`, LPS `0x4392b16c`/`0x4392b254`).
3. **Tabla de backup**: **350 entradas de 12 B** en `0x43bd1964` (`{id = 0x10c0000 + n, offset,
   size}`), `WriteShadow2BakcupArea` vuelca `0x10c` B (`mov.w r0,#0x10c` en `0x4392ab78`) y
   `SetAudioNrType` publica el **bit 3** de `bkId = 0x10e0000`.
4. **Rigor metodológico**: el subagente cuantificó los falsos positivos de cada regla —
   estricta 37/37 reales, kill analysis 60 pares (37 verdaderos + **23 falsos**, 21 de ellos
   apuntan a otra cadena real) — y además localizó el caso donde la kill analysis se
   equivoca: el sitio `0x4355bcb2` resuelve a `0x43ceb58b` y no a `0x43cde863`, cuyo sitio
   real es `0x4392ab04`.

**Consecuencia asumida en el repo**: con esta calibración (y la de S118 en `[SFRA]`) se
declaró **regla canónica estricta** el escáner
`analysis/s106_imaging_cap/scan_pic_refs_strict.py` y se rectificaron las cifras publicadas
de S106, S110, S113 y S115 (ver `analysis/s106_imaging_cap/pic_xref_methodology.md`).

**Observación**: `AIP` **no** es el mismo módulo que el «SA» de S108 (`Camera::SaFuncDrv`,
`sa_func_*`): ninguna de las 37 trazas de `[AIP]` lo menciona. Y el cliente de `[AIP]` es el
**ADF** (S81): `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411` y los tipos
`AUDIO_IP_CONFIG_TYPE_*` `0x43c264fa`–`0x43c2659e` con los comandos `SetAip0/1`, `GetSa0/1`,
`SetSa`, `SetFader` y `SetZoomNr`.
