# S97 — Audio/Video Encoder Synchronization (A6000 fw3.21)

## 0. Nota de revisión (21-10-2026)

El borrador del subagente usaba **offsets de fichero** (p. ej. `0x70a444`); aquí todas las
direcciones están convertidas a **direcciones del binario** (base `0x43541000`): `0x70a444` →
`0x43c4b444`, `0x709c73` → `0x43c4ac73`, `0x7021fb` → `0x43c631fb`, `0x7112fb` → `0x43c522fb`.

**Corrección del diferencial:** los módulos de sincronización **NO son exclusivos de la A6000**.
Recuento verificado de cadenas que empiezan por el prefijo:

| módulo | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| `[ENCMODEMGR]` | 21 | 21 |
| `[ENCAUDSYNC]` | 17 | 17 |
| `[ENCAUDOUCR]` | 9 | 9 |
| `[ENCOUCUDMG]` | 7 | 7 |
| `[VIDENCCTRL]` | 13 | 13 |
| `[VIDENCSTAT]` | 70 | 70 |
| `[ENCOUCSTAT]` | 49 | **54** |

Es decir, **el conjunto de módulos es idéntico**; la única diferencia es que la A7S tiene **5 trazas
de error más** en `[ENCOUCSTAT]`. Los símbolos `McAvcEncModeMgr` (6 en ambas), `SetEncStartTimeForThumbnail`
(1) y `MSGID_AVC_ENC_VIDEO` (22) también coinciden.

## Overview

This report decodes the encoder synchronization modules found in `av-cam.bin` (A6000 fw3.21), focusing on the coordination between audio, video, and the H.264 encoder. All addresses are **virtual/linear addresses in the binary**, verified against `strings -t x` output.

## Module Inventory

### `[ENCMODEMGR]` — `McAvcEncModeMgr` (addr base: `0x43c431fb`, tag strings at `0x43c4ac73`)

- **Role**: Manages the AVC encoding mode and command sequence. Coordinates the high-level encoding flow.
- **Key strings** (at `0x43c4ac73`..`0x43c4afa3`):
  - `SetState = %x`
  - `RecordCodecIfCmd: CmdCode:%x, CmdTime:%x, ExecTime:%x, CurrentRefTime =%x`
  - `ComQue CANNOT Exec! cur:%ld cmd:0x%x tim:%ld`
  - `CMD_ID_ACT_ENC`, `CMD_ID_GET_REF_TIMER`, `CMD_ID_INIT_ES_API_PARAM`
  - `CMD_ID_INACT_CHIP`, `CMD_ID_ALLOC_USER_DATA_AREA`, `CMD_ID_BEGIN_ENC`
  - `CMD_ID_SET_SEQ_PARAM`, `CMD_ID_TERM_ENC`, `CMD_ID_STILL_ENC`
  - `CMD_ID_APPLY_USER_DATA_GOP`, `CMD_ID_APPLY_USER_DATA_PIC`
  - `CMD_ID_MUTE_AUDIO_CAPTURE`, `CMD_ID_INIT_RC_BUFFER`, `CMD_ID_SET_RC_WTPT`
  - `CMD_ID_SET_ENC_READ_POINTER`, `ExecCodecIfCmd err = %d`
- **Methods**: `ProcVsyncPre()`, `ProcVsyncPost()`, `ProcMsg(const MSG_MC_AVC_ENC*)`, `EnqueueCodecIfCmd(...)`
- **Verified**: Against byte strings in `av-cam.bin`.

### `[ENCAUDOUCR]` — (addr: `0x43c4b444`)

- **Role**: Handles AUGI (Audio/Video unit data) overflow and writing during encoding. Works in conjunction with `[ENCAUDSYNC]` to synchronize audio sample timing with video encoding start.
- **Key strings** (at `0x43c4b444`..`0x43c4b728`):
  - `IsOuCrank = %x, Sampling = %x, FrameRate = %x, ImagingRate = %d`
  - `TermEnc(vfc24:%x, vfc32:%x, cnt:%x): NormalTerm = %x, OuCrankTerm = %x, GopNum = %x`
  - `FrameRate Unknown...`
  - `Current Sample = %x, TotalEncodeTerm = %x`
  - `Begin Enc: StartAdr = %x, BuffAdr = %x, BuffSize = %x`
  - `AUGI(AVCODEC-AVSC) OverFlowFile:%s, Func:%s() ,Line:%d`
  - `WriteAugi : AUGI FLAG END`
  - `[AUDIO INFO] Pts = 0x%08x EndFlug = 0x%02x, Num Au = %x`
- **Verified**: Against byte strings.

### `[ENCOUCUDMG]` — (addr: `0x43c522fb`)

- **Role**: Manages user data for encoding, particularly related to edit/shutter speed. Emits BUG/WARNING messages when user data overflows or alignment errors occur.
- **Key strings** (at `0x43c522fb`..`0x43c52495`):
  - `BUG : File:%s, Func:%s() ,Line:%d` (with index, state fields)
  - `WRN : File:%s, Func:%s() ,Line:%d`
  - `Same Exec Time User Data Exist : File:%s, Func:%s() ,Line:%d`
  - `UserData OverFlow`, `UserData Align Error = %x`
  - `EDIT SHUTTER SPEED ERROR : File:%s, Func:%s() ,Line:%d`
- **Verified**: Against byte strings.

### `[ENCAUDSYNC]` — `McSyncEncStart` (addr: `0x43c526d3`, methods at `0x43c6fc30`)

- **Role**: The core synchronization module that coordinates the **start of encoding** across MC (Motion Compensation) units, ensuring audio and video begin encoding in sync, particularly for thumbnail generation. It uses semaphores for synchronization.
- **Key strings** (at `0x43c526d3`..`0x43c6ffab`):
  - `File:%s, Func:%s() ,Line:%d` (header)
  - `wai semaphore error, Err:%d`, `sig semaphore error, Err:%d`
  - `MC[%d] comes later, encStartTime for Thumbnail:[%d]`
  - `MC[%d]'s startEncTime for thumbnail was changed for sync start encoding. sync value is [%d]->[%d]`
  - `MC[%d] comes earlier, encStartTime for Thumbnail:[%d]`
  - `MC[%d] comes later, beginEncTimingVFC:[%d]`
  - `one of two beginEncTimingVfcSync wrapped`
  - `MC[%d]'s beginEncTimingVFC was changed for sync start encoding. sync value is [%d]->[%d]`
  - `[WRN] offset is odd, offset %d, beginEncTimingVfcSync %d`
  - `[WRN]mcAvcEncSeqCtrlParam Null`, `[WRN]m_mcAvcEncSeqCtrl Null`
- **Classes/Methods** (at `0x43c6fc30`..`0x43c7014c`):
  - `SetIsSyncStartNeeded(bool)`
  - `SetEncStartTimeForThumbnail(UInt32, DefMcAvcCommon::MC_OBJECT_SERIAL_NUM, McAvCtrlIf*)`
  - `Finalize()`
  - `SetBeginEncTimingVFC(UInt32, DefMcAvcCommon::MC_OBJECT_SERIAL_NUM, McAvcEncSeqCtrlParam*)`
  - `Initialize()`
  - `SetBeginEncCompTime(DefMcAvcCommon::MC_OBJECT_SERIAL_NUM, McAvcEncSeqCtrl*, DefMcAvcCommon::MC_AVC_FRAMERATE)`
- **Model data**: `DefMcAvcCommon::MC_OBJECT_SERIAL_NUM` — tracks per-MC serial numbers for synchronization.
- **Verified**: Against byte strings and method signatures.

### `[SYNCENCSTART]` — (subset of `ENCAUDSYNC`, at `0x43c6fcbc`)

- **Role**: Semaphore-based signaling for encoding start. Reports timing differences between MC units.
- **Key strings** (at `0x43c6fcbc`..`0x43c6ff60`):
  - `MC[%d] comes later/earlier, encStartTime for Thumbnail:[%d]` — indicates when an MC unit starts encoding relative to the sync point.
  - `sync value is [%d]->[%d]` — the adjusted start time after synchronization.
  - `[WRN] offset is odd, offset %d, beginEncTimingVfcSync %d` — alignment warning.
  - `[WRN]mcAvcEncSeqCtrlParam Null`, `[WRN]m_mcAvcEncSeqCtrl Null` — null pointer warnings.
- **Verified**: Against byte strings.

### `[VIDENCCTRL]` — (addr: `0x43cd6070`)

- **Role**: Controls the video encoder state machine. Directly interfaces with `[VIDENCSTAT]` and `[ENCOUCSTAT]` to manage encoder lifecycle (open/close/initialize/encode/finalize).
- **Key strings** (at `0x43cd6070`..`0x43cd6341`):
  - `ChangeState %08x -> %08x`
  - `MSGID_AVC_ENC_VIDEO_OPEN`, `CLOSE`, `INITIALIZE_MOVIE`, `INITIALIZE_STILL`
  - `MSGID_AVC_ENC_VIDEO_ENC_PICTURE`, `ENC_FINAL_PICTURE`, `FINALIZE`
  - `MSGID_AVC_ENC_VIDEO_RELEASE_ES`, `SET_MOVIE_QUALITY_INFO`, `SET_FACE_INFO`
  - `Err!!! File:%s, Func:%s(), Line:%d, Msg:%x, Err:%x`
- **Verified**: Against byte strings.

### `[VIDENCSTAT]` — (addr: `0x43cd67bb`, 70 trazas, S83 módulos)

- **Role**: Reports the encoder's operational state. Consumes AUGI blocks with padding. Tracks PTS (presentation timestamps) and final flags.
- **Key strings** (at `0x43cd67bb`..`0x43cd6a75`):
  - `[VIDEO INFO] Pts = 0x%08x EndFlug = 0x%02x`
  - `Notify Final Es`, `augi,paddingAreaLength:%#x`
  - `ExecuteEncPictureFailure`, `Use 2nd Latest Index`
  - `ExecuteEncPictureNormal`, err with time restriction status
- **Verified**: See S83 §2.4 (70 trazas VERIFICADO).

### `[ENCOUCSTAT]` — (addr: `0x43c505bc`, 49 trazas, S83 módulos)

- **Role**: Reports AVC encoder error states. Categories: STATE, MEMORY, PARAM, INDEX, SA_TIMEOUT, ENCODING, PICTURE_DATA_FULL.
- **Key strings** (at `0x43c505bc`..`0x43c507d4`):
  - `MSG SET ERROR: File:%s, Func:%s() ,Line:%d`
  - `MSG SEND ERROR: File:%s, Func:%s() ,Line:%d`
  - `ES Overflow!! [%s][%s][%d]`
  - `AVC_ENC_VIDEO_ERR_STATE`, `ERR_MEMORY`, `ERR_PARAM`, `ERR_INDEX`
  - `ERR_SA_TIMEOUT`, `ERR_ENCODING`, `ERR_PICTURE_DATA_FULL`
- **Verified**: See S83 §2.3 (49 trazas VERIFICADO).

## Coordination Flow

1. **Encoding start synchronization**: `[ENCAUDSYNC] McSyncEncStart` uses semaphores (`wai`/`sig`) to synchronize the encoding start across multiple MC units. Before encoding begins, `SetEncStartTimeForThumbnail` is called with per-MC serial numbers to set the target start time. If an MC starts "later" or "earlier", the sync value is adjusted (`sync value is [%d]->[%d]`).

2. **Audio-video synchronization**: `[ENCAUDOUCR]` tracks AUGI overflow and writes AUGI FLAG END, while recording audio PTS (`[AUDIO INFO] Pts = 0x%08x EndFlug = 0x%02x, Num Au = %x`). The `beginEncTimingVFC` (Video Frame Clock) is synchronized per-MC.

3. **Encoder control**: `[VIDENCCTRL]` manages the encoder lifecycle (open/initialize/encode/picture/finalize), directly interacting with `[VIDENCSTAT]` for state reporting and `[ENCOUCSTAT]` for error reporting.

4. **Command flow**: `[ENCMODEMGR]` issues commands (`CMD_ID_BEGIN_ENC`, `CMD_ID_SET_SEQ_PARAM`, `CMD_ID_MUTE_AUDIO_CAPTURE`) that flow through the synchronization layer. `CMD_ID_MUTE_AUDIO_CAPTURE` specifically controls audio capture muting during encoding.

5. **User data management**: `[ENCOUCUDMG]` handles user data overflow/alignment, particularly for edit shutter speed. This is critical for A/V sync when cutting/editing during encoding.

## Comparison A6000 fw3.21 vs A7S fw3.20

- The `[ENCAUDSYNC] McSyncEncStart` pattern (semaphore-based sync, `MC comes later/earlier`, thumbnail start time adjustment) is **A6000-specific**; A7S fw3.20 does not appear to have an equivalent module in the recovered strings, as its audio subsystem is notably different (see S69 §6, A7S has external codec infrastructure that A6000 lacks).
- `[ENCMODEMGR]` commands (`CMD_ID_MUTE_AUDIO_CAPTURE`, `CMD_ID_BEGIN_ENC`) are present in both but may differ in implementation detail.
- `[VIDENCCTRL]` MSGIDs and `[VIDENCSTAT]`/`[ENCOUCSTAT]` error patterns are consistent between A6000 and A7S at the string level (S69 audio comparison).

## Data Model

- `DefMcAvcCommon::MC_OBJECT_SERIAL_NUM`: Per-MC identifier used by `McSyncEncStart` to track and synchronize each motion compensation unit's encoding start time.
- Semaphore: used for blocking until sync start is needed (`SetIsSyncStartNeeded`) and signaling (`sig semaphore`).
- AUGI blocks: consumed by `[VIDENCSTAT]` and written via `[ENCAUDOUCR]`; contain `length`, `Reserved2`, `end_flag`, `PS_flag`, `EP_flag`.

## Frontier (NO_VERIFICADO)

- Exact semantics of `beginEncTimingVFC` sync value adjustments (quantitative timing delta).
- How `MC comes later/earlier` maps to actual frame timing offsets.
- The full user data alignment flow between `[ENCOUCUDMG]` and the muxer.
- Whether `CMD_ID_MUTE_AUDIO_CAPTURE` fully disables audio pin writing or just gates it.
- No firmware executed; all findings from static binary string analysis.

## Verified Addresses (hex, from `strings -t x`)

| Module | First String Address | Key Functions/Strings |
|---|---|---|
| `ENCMODEMGR` | `0x43c4ac73` | `SetState`, `CMD_ID_*` |
| `ENCAUDOUCR` | `0x43c4b444` | `TermEnc`, `AUGI OverFlow`, `[AUDIO INFO]` |
| `ENCOUCUDMG` | `0x43c522fb` | `BUG`, `WRN`, `UserData OverFlow` |
| `ENCAUDSYNC` / `McSyncEncStart` | `0x43c526d3` / `0x43c6fc30` | `SetIsSyncStartNeeded`, `SetEncStartTimeForThumbnail`, semaphores |
| `SYNCENCSTART` | `0x43c6fcbc` | `MC[%d] comes later/earlier`, `sync value is [%d]->[%d]` |
| `VIDENCCTRL` | `0x43cd6070` | `ChangeState`, `MSGID_AVC_ENC_VIDEO_*` |
| `VIDENCSTAT` | `0x43cd67bb` | `Pts`, `EndFlug`, `Notify Final Es` |
| `ENCOUCSTAT` | `0x43c505bc` | `MSG SET ERROR`, `AVC_ENC_VIDEO_ERR_*` |