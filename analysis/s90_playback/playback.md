# S90 — Reproducción y visor de fotos (fw3.21)

**Alcance:** línea de ingeniería inversa **general** del subsistema PLAY / MPLAY / VDISP en la A6000 fw3.21. Sin SilentShutter, sin montura (S66), sin AF (S63), sin JPEG (S64), sin service mode/NVRAM, sin ADJ_CMD, sin ZPD (S75), sin ZIT (S80), sin ADF (S81), sin API del SA (S84), sin clk_vph/VPH (S85), sin visor LCD/EVF (S85/86), sin caras (S71), sin wireless (S72), sin Creative Style (S77), sin modos de disparo (S88), sin IDT (S89), sin AutoFraming (S82), sin almacenamiento (S87).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** Documento del subagente verificado por muestreo (15/15 nombres
> de clase en sus direcciones, las cadenas `bid=MPLAY`, `Issue VFCCmd to MPLAY.` y los cuatro modos
> `VDISP`): **15/15 correctos**, sin correcciones necesarias. Se le añaden los enlaces cruzados
> con S79 (mapa de módulos), S85 (`CLK_CTRL` y los dos VFC) y S86 (el visor).

---

## 1. Inventario de clases y direcciones del blob

Clases RTTI identificadas en `analysis/s65_video/strings_all.tsv` (base virtual 0x43541000):

| Clase | Dirección | Comentario |
|---|---|---|
| `20AbstractPlayArranger` | `0x43c43c7c` | Organizador base de reproducción |
| `12PlayArranger` | `0x43c43c93` | Organizador de reproducción concreto |
| `22VideoReserveCmdCreator` | `0x43c43ca2` | Creador de comandos de reserva de vídeo |
| `20VideoArrangerAdapter` | `0x43c43cbb` | Adaptador del arranger de vídeo |
| `19PlayArrangerAdapter` | `0x43c43cd2` | Adaptador del play arranger |
| `21DecTcubEventRequester` | `0x43c43ce8` | Solicitante de eventos DecTcub |
| `16NullPlayArranger` | `0x43c43d00` | Play arranger nulo |
| `20NullDecAugiConverter` | `0x43c43d13` | Convertidor Augi nulo |
| `16DecAugiConverter` | `0x43c43d2a` | Convertidor Augi |
| `24AbstractVpTableSequencer` | `0x43c43d3d` | Secuencer de tabla VP abstracto |
| `16VpTableSequencer` | `0x43c43d58` | Secuencer de tabla VP |
| `6VPInfo` | `0x43c43d6b` | Información de vídeo |
| `10VPInfoCore` | `0x43c43d73` | Núcleo de información de vídeo |
| `17EverythingHandler` | `0x43c43d80` | Manejador de todo |
| `21AbstractTblMsgHandler` | `0x43c43d94` | Manejador de mensaje de tabla abstracto |
| `13TblMsgHandler` | `0x43c43dac` | Manejador de mensaje de tabla |
| `24AbstractDecCmdDelayChain` | `0x43c43dbc` | Cadena de retraso de comando Dec abstracta |
| `16DecCmdDelayChain` | `0x43c43dd7` | Cadena de retraso de comando Dec |
| `20AbstractVFCCmdIssuer` | `0x43c43dea` | Emisor abstracto de comando VFC |
| `12VFCCmdIssuer` | `0x43c43e01` | Emisor concreto de comando VFC |
| `12VFCConverter` | `0x43c43e10` | Conversor de VFC |
| `24VideoFieldCounterFactory` | `0x43c43e1f` | Factoría de contador de campos de vídeo |
| `14VFCScheCmdList` | `0x43c43e3a` | Lista de comandos programados de VFC |
| `16VFCReScheCmdList` | `0x43c43e4b` | Lista de comandos re-programados de VFC |
| `20UpdatableEVFCFactory` | `0x43c43e5e` | Factoría EVFC actualizable |
| `29UpdatableRenewIntervalFactory` | `0x43c43e75` | Factoría de intervalo renovable actualizable |
| `12VFCScheduler` | `0x43c43e95` | Programador de VFC |
| `16VFCSchedulerCore` | `0x43c43ea4` | Núcleo del programador de VFC |
| `10ILogWriter` | `0x43c43eb7` | Escritor de log |
| `9VFCScheIf` | `0x43c43ec4` | Interfaz VFC programado |
| `10MPlayState` | `0x43c43ecf` | Estado de reproducción de películas |
| `14VPInfoPeriodic` | `0x43c43edc` | Información de vídeo periódica |
| `8VPInfoBB` | `0x43c43eed` | Información de vídeo BB |
| `10VPInfoFunc` | `0x43c43ef7` | Función de información de vídeo |
| `18ResumePointChanger` | `0x43c43f04` | Cambiador de punto de reanudación |
| `20RestartParamModifier` | `0x43c43f19` | Modificador de parámetros de reinicio |
| `20AVRendezvousNotifier` | `0x43c43f30` | Notificador de randezvous AV |
| `18ReserveCmdRegister` | `0x43c43f47` | Registro de comando de reserva |
| `13IpcmMsgSender` | `0x43c43f5c` | Enviador de mensaje IPCM |
| `19DecRestartRequester` | `0x43c43f6c` | Solicitante de reinicio Dec |
| `17DecBBCmdRequester` | `0x43c43f82` | Solicitante de comando BB Dec |
| `23EOPProhibiterForNextThm` | `0x43c43f96` | Prohibidor EOP para siguiente miniatura |
| `13EOPProhibiter` | `0x43c43fb0` | Prohibidor EOP |
| `31NopPiUnderflowForcePauseHandler` | `0x43c43fc0` | Manejador de pausa por subflujo NO Pi |
| `28PiUnderflowForcePauseHandler` | `0x43c43fe2` | Manejador de pausa por subflujo Pi |
| `N6vpInfo12CodecAdapterI9CodecBaseEE` | `0x43c44001` | Adaptador de código VP info |
| `21NopPiUnderflowChecker` | `0x43c44025` | Comprobador de subflujo Pi nulo |
| `18PiUnderflowChecker` | `0x43c4403d` | Comprobador de subflujo Pi |
| `11VPInfoCodec` | `0x43c44052` | Código de información de VP |
| `15VPInfoCodecCore` | `0x43c44060` | Núcleo del código de información de VP |
| `18VFCSchedulerFacade` | `0x43c44072` | Fachada del programador de VFC |
| `21DecFrameCounterFacade` | `0x43c44087` | Fachada de contador de cuadros Dec |
| `10VPInfoHost` | `0x43c4409f` | Anfitrión de información de VP |
| `23StrmEngDecCdcCtrlFacade` | `0x43c440ac` | Fachada CDC del decodificador de cadena de medios |
| `19StrmEngDecCdcCtrlIf` | `0x43c440c6` | Interfaz CDC del decodificador de cadena de medios |
| `19StrmEngDecCdcFacade` | `0x43c440dc` | Fachada CDC del decodificador de cadena de medios |
| `14StrmEngDecCIIf` | `0x43c440f2` | Interfaz CI del decodificador de cadena de medios |

---

## 2. Reproducción de vídeo (MPLAY)

### 2.1 ¿Qué es `MPLAY`?

`MPLAY` = *Movie Play* (reproducción de vídeo). Es el subsistema que gestiona la reproducción de contenido de vídeo (archivos AVCHD/MPEG en la tarjeta). Se identificó la cadena `MPlay` a la dirección `0x43c66542` y sus subclases:

- `MPlayBB` a `0x43c6686a` — gestiona la interfaz de buffer/búsqueda
- `MPlayCodec` a `0x43c66883` — control de codecs de vídeo
- `MPlayHost` a `0x43c668f4` — control host/software

### 2.2 Máquina de estados

El estado de reproducción está definido por `10MPlayState` a `0x43c43ecf`. La máquina de estados coordina la transición entre los modos de reproducción, gestionando los recursos de decodificación y visualización. El emisor de comandos VFC está íntimamente acoplado a este estado.

### 2.3 `Issue VFCCmd to MPLAY`

El comando `Issue VFCCmd to MPLAY` se encuentra a la dirección `0x43c7291e`. Este comando emite órdenes al subsistema MPLAY a través del controlador de VFC (Vertical Frequency Counter). Funciones relacionadas:

- `Issue VFCCmd to DEBUG.` a `0x43c72907` — modo de depuración
- `Clear VFCCmd_IVFC=` a `0x43c728e5` — limpieza del IVFC
- `VFCScheCmdList` a `0x43c728f8` — lista de comandos programados de VFC
- `Get_mpl` a `0x43c7295e` — obtención del puntero a la estructura MPLAY

La sintaxis de los comandos MPLAY incluye:
```
bid=MPLAY cid=%#hx flg=%d dvfc=%#x ivfc=%#x edge=%#hx
```
en la dirección `0x43c660e0`, donde:
- `bid` = identificador de bloque
- `cid` = comando ID
- `flg` = flags
- `dvfc` = VFC destino (main)
- `ivfc` = VFC destino (sub/secondario)
- `edge` = borde/edge trigger

### 2.4 Sincronización con el VFC (S85)

El VFC (Vertical Frequency Counter) es gestionado por el módulo `CLK_CTRL` (S85). `MPLAY` coordina con dos canales VFC:
- `m_vfc.main=0x%0x, m_vfc.sub=0x%0x` (dirección `0x43c3ac2f`)
- El `CLK_CTRL` tiene una máquina de estados: `STATE_INIT1` → `STATE_NORMAL` → `STATE_LOCK` → `STATE_CHANGE_CLK` → `STATE_CHANGE_CLK_LOCKING`
- `Receive Message from Master src=0x%0x` (`0x43c3abd0`) y `Send Message to Slave 0x%0x` (`0x43c3ac86`) coordinan el flujo maestro/esclavo
- `set_sync_signal` (`0x43c3a335`) y `set_sync_initial_signal` (`0x43c3a379`) configuran la sincronización

---

## 3. VDISP — Modos de salida de vídeo

Cuatro modos de salida de vídeo identificados a través de las cadenas de diagnóstico en `0x43c4811f` y siguientes:

| Modo | Dirección | Comentario |
|---|---|---|
| `[VDISP24p]` | `0x43c4811f` | Modo 24p (cine) |
| `[VDISP30p25p]` | `0x43c481c2` | Modo 30p/25p (PAL/NTSC) |
| `[VDISP60i50i]` | `0x43c48341` | Modo 60i/50i (interlazado) |
| `[VDISP60p50p]` | `0x43c4856a` | Modo 60p/50p (progresivo) |

### 3.1 Relación con down-conversion PAL/NTSC (S86)

El subsistema VEF (visor electrónico, S86) reporta las siguientes señales de down-conversion:
- `PAL 50i50p`, `PAL 25p`
- `NTSC 60i60p`, `NTSC 30p24p`

La relación es:
- `[VDISP24p]` → salida **24p** sin down-conversion (modo cine puro)
- `[VDISP30p25p]` → down-conversion PAL/NTSC: 30fps → 25p (PAL) o 24→30NTSC
- `[VDISP60i50i]` → down-conversion interlazada: 60i → 50i (PAL) o 60i → NTSC
- `[VDISP60p50p]` → down-conversion progresiva: 60p → 50p (PAL) o 60p → NTSC 60p

Todos los modos reportan `DISP_PLAY_UNKOWN is NOERR` en `GetPlayState()`, lo que sugiere que el estado de reproducción es interno y no siempre mapeado explícitamente al usuario.

---

## 4. Reproducción de fotos

El flujo de reproducción de fotos sigue esta pipeline:

1. **Lectura de la tarjeta**: datos accedidos mediante `ExternalStorageStart()/Acquire/Release` (S87, direcciones `0x43cb3148`/`0x43cb317f`/`0x43cb31b8`)
2. **Decodificación**: el índice de la cámara está en `libmpr.so` (10.3 MB), que mantiene la base de datos de contenido grabado con carpetas por fecha y contenido. Funciones clave:
   - `9PlayMovieEm` / `9GetRemainEm` — reproducción de películas
   - `6PbStopE` / `6ResumeE` — inicio/cesación
   - `24PlayStillSingleByAddressEm` — reproducción de still por dirección
   - `GetContentsCountSync`, `GetDcfDirectoryCount`, `GetDcfDirectoryName`, `GetDcfFileInfo`, `GetDcfObjectInfo`, `ReadThumbnail`, `PlayThumbnail`, `EnterThumbnailPb`
3. **Escalado**: Las imágenes se escalan desde el tamaño nativo del sensor al tamaño del visor. El parámetro `forcastUseSizeOnDstDstDisc` en `libObj.so` estima el tamaño en el disco destino.
4. **Mostrar**: La imagen se muestra a través del subsistema VDF/VEF (S86/S85), con modos de salida definidos por `VDISP24p/30p25p/60i50i/60p50p`.

La relación con el índice de la cámara (`libmpr.so`) es que `libmpr` provee la enumeración de contenido ya grabado, mientras que el pipeline de reproducción lee los datos crudos de la tarjeta y los decodifica para la display.

---

## 5. Comparación A6000 fw3.21 vs A7S fw3.20

| Característica | A6000 fw3.21 | A7S fw3.20 | Comentario |
|---|---|---|---|
| `CLK_CTRL` módulo | **66 trazas** (`0x43c3a1df`–`0x43c3b09c`) | **0** | Nuevo en fw3.21 |
| `VPH_API` módulo | **106 trazas** (`0x43ce32e7`–`0x43ce3dfc`) | **0** | Nuevo en fw3.21 |
| `MPlay` clases RTTI | Presentes | Desconocido | Verificar en A7S |
| `VDISP` modos (24p/30p25p/60i50i/60p50p) | Identificados | Desconocido | Solo fw3.21 |
| `10MPlayState` | `0x43c43ecf` | Desconocido | Estado de Movie Play |
| `Issue VFCCmd to MPLAY` | `0x43c7291e` | Desconocido | Comando VFC->MPLAY |
| Strings ADF `PlayEnd SendComp` | `0x43c27b55` | Desconocido | Compatibilidad A7S |
| `[CodecSeq][TD] VideoIP Play END(0x1A/0x1B)` | `0x43c3ec70/0x43c3ec9c` | Desconocido | Fin de reproducción de vídeo |

---

## 6. Abierto (NO_VERIFICADO)

- Implementación exacta de la máquina de estados `10MPlayState` y transiciones
- Mapeo preciso de `DISP_PLAY_UNKOWN` a estados de usuario
- Relación detallada entre `dvfc`/`ivfc` en el comando `bid=MPLAY cid=… flg=… dvfc=… ivfc=… edge=…`
- Si `20AbstractPlayArranger` es la clase base única para foto y vídeo playback
- Efecto de `JudgePlayPriority` (`0x43c27b84`) en la selección de contenido para reproducción
- Código de ruta completa: tarjeta → `libmpr.so` índice → decodificador → `VDISP` escalado → visor