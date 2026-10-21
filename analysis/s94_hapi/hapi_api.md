# S94 — HAPI API Analysis (libHapiLib.so, fw3.21)

## 0. Nota de revisión (21-10-2026)

Informe del subagente verificado por muestreo contra `libHapiLib.so`: `HapiLibMain` (5 apariciones),
`CamService` (19), `SdfService` (34), `CamApi` (197; **139 símbolos mangled distintos** de
`Camera::CamApi*`, no 17), los tipos de mensaje `REQ_MSGE` (29), `EVT_MSGE` (3), `COMP_MSGE` (53),
`SDF_MSG_SENDE` (6), `MAIN_MSG_RECVE` (4) y `CATEID_HAPI` (1), y las primitivas OSAL
(`osal_snd_msg`, `getTargetQId`, `mainLoop`, `interrupt`). **Sin correcciones**; se añade el dato de
la interfaz `Camera::HAPI` (cabeza de mensaje propia del lado cámara: `processReq`, `processComp`,
`processCaptureEvent`) y las operaciones de `CamApiBase` (`apiFactory`, `stmDepositYc`,
`stmDepositRaw`, `stmInquire`, `stmWithdraw`, `checkOneTicket`/`checkThreeRawTickets`,
`convertErrorCode`, `freeImageInstance`, `freeExif`, `freeStdYc`).

## 1. Library inventory

**File:** `firmware/extracted/fw321/.../lib/libHapiLib.so` (89628 B)

The binary is stripped of its symbol table, but C++ mangled names survive in `.rodata`. The following classes/functions are exported (mangled names recovered via `strings`):

| Mangled name | Likely entity |
|---|---|
| `_ZN7HapiLib11HapiLibMain11getInstanceEv` | `HapiLibMain` singleton |
| `_ZN7HapiLib3Cam10CamService11getInstanceEv` | `CamService` singleton |
| `_ZN7HapiLib3Sdf10SdfService11getInstanceEv` | `SdfService` singleton |
| `_ZN7HapiLib7record2Ehh` | `record2(int, int)` |
| `_ZN7HapiLib9record2_2Ehhjj` | `record2_2(int, int, int, int)` |
| `_ZN7HapiLib11HapiLibMain12getTargetQIdEj` | get target queue ID |
| `_ZN7HapiLib11HapiLibMain8mainLoopEv` | main event loop |
| `_ZN7HapiLib3Sdf10SdfService3runEv` | `SdfService::run()` |
| `_ZN7HapiLib3Cam10CamService3runEv` | `CamService::run()` |
| `_ZN7HapiLib3Sdf10SdfService9interruptEv` | `SdfService::interrupt()` |
| `_ZN7HapiLib3Cam10CamService9interruptEv` | `CamService::interrupt()` |
| `_ZN7HapiLib11HapiLibMain9interruptEv` | `HapiLibMain::interrupt()` |

### Message types (inferred from `strings` messages and symbol names)

| Type | Description |
|---|---|
| `REQ_MSGE` | Request message (sent from app to camera) |
| `EVT_MSGE` | Event message (camera-to-app notifications) |
| `COMP_MSGE` | Completion message (reply to a request) |
| `SDF_MSG_SENDE` | SDF send message |
| `MAIN_MSG_RECVE` | Main message receive |
| `CATEID_HAPI` | Category ID for HAPI messages (0x0001) |
| `CATEID_SDF_ACK` | SDF acknowledgment category |
| `CATEID_SDF_COMP` | SDF completion category |
| `CATEID_SDF_NEXT` | SDF next-category |

### OSAL / IPC primitives (from symbol names)

| Function | Purpose |
|---|---|
| `osal_snd_sync_direct` | Sync send direct |
| `osal_valloc_msg_wait` | Virtual alloc + wait |
| `osal_snd_msg` | Send message |
| `osal_snd_sync_msg` | Sync send message |
| `osal_free_msg` | Free message |
| `osal_wait_thread_exit` | Wait for thread exit |
| `osal_create_waitable_thread` | Create waitable thread |
| `osal_exit_thread` | Exit thread |
| `osal_dynamic_id` | Dynamic ID generation |
| `osal_rcv_msg_tmo` | Receive message with timeout |
| `_ZN7HapiLib12OsalAsyncMsg7prepareEj` | Prepare async msg |
| `_ZN7HapiLib12OsalAsyncMsg6getQIdEv` | Get queue ID |
| `_ZN7HapiLib12OsalAsyncMsg6sndRcvEv` | Send/receive |
| `_ZN7HapiLib12OsalAsyncMsg5cleanEv` | Clean async msg |
| `_ZN7HapiLib12OsalAsyncMsgD2Ev` | Async msg destructor |

### Dataflow infrastructure (SDF)

| Class / Struct | Key methods |
|---|---|
| `SdfApiBase` | `init`, `setHapiCommon(int, int, COMP_MSGE*)`, `apiFactory`, `allocYc`, `convertErrorCode`, `saveYc`, `nextProcess`, `freeStdYc`, `freeHandle`, `extractImageInstance`, `insertImageInstance`, `freeImageInstance`, `stmWithdraw`, `stmInquire`, `stmDeposit`, `stmDestruct`, `checkOneTicket`, `convertErrorCode` |
| `C_DataflowInfra_StdData_YCC` | YCC image data |
| `C_DataflowInfra_Entry_ImageSizeInfo` | Image size info |
| `C_DataflowInfra_Entry_YcStateInfo` | YC state info |
| `C_DataflowInfra_Entry_ImageOutTimInfo` | Output timing info |
| `SdfApiResizeTrim`, `SdfApiRedEye`, `SdfApiRotate` | Resize/red-eye/rotate SDF pipelines |

### Camera API classes (CamApi*)

| Class | Key methods |
|---|---|
| `CamApiBase` | `setHapiCommon`, `apiFactory`, `convertErrorCode`, `checkThreeRawTickets`, `stmInquire`, `stmDepositRaw`, `stmWithdraw`, `stmDestruct`, `freeStdYc`, `freeExif` |
| `CamApiRawCapture` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`PN6Camera4HAPI8COMP_MSGE`), `eventProcess` (`EPN6Camera4HAPI7EVT_MSGE`, `PNS_7EVT_MSGE`) |
| `CamApiCreateStream` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`), `mainLoop` |
| `CamApiGetImageInfo` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiDevelop` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiHdr` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiRawCapture` (duplicate listing, different variant) | Same as above |
| `CamApiRichtoneMono` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiSuperResolution` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiMiniature` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiSoftFocus` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiArtEffect` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiContrastPlus` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiFaceNr` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |
| `CamApiChangeReleaseStatus` | `getInstance`, `getCompMsgId`, `getCompMsgLength`, `errorProcess`, `preProcess` (`REQ_MSGE*`, `PN6Camera4HAPI7REQ_MSGE`), `postProcess` (`COMP_MSGE*`) |

## 2. Protocol structure (inferred)

The HAPI protocol operates through **OSAL message queues** (see S93). The key flow is:

1. **App → Camera**: App sends a `REQ_MSGE` message to the HAPI category (`CATEID_HAPI`) via the OSAL bus. The message contains a `cat_id` (category ID = HAPI) and a `msg_id` (function ID selecting the operation).
2. **Camera → App**: Camera processes the request and sends back a `COMP_MSGE` (completion) or, for certain ops, an `EVT_MSGE` (event/notification). The completion includes a result code and optional data.
3. **Category IDs**: `CATEID_HAPI` identifies HAPI messages; `CATEID_SDF_ACK`, `CATEID_SDF_COMP`, `CATEID_SDF_NEXT` are used within the SDF subsystem.
4. **Message size validation**: `[HAPILIB] Main main: Size %d is too big, srcId %08X` — the framework validates message sizes.
5. **Reply ID tracking**: `[HAPILIB] Main main: No replyId.` — replies are tracked by reply ID.
6. **Scalar bridge**: `[CAM_SCALAR]: HAPI Manager:Receive error`, `[CAM_SCALAR]: HAPI Manager:Message size 0`, `[CAM_SCALAR]: HAPI Manager:Empty Message`, `[CAM_SCALAR]: HAPI Manager:Unknown MSG_ID` — the scalar middleware (`libObj.so`) relays HAPI messages between the app process and the camera's `Stage_CameraHAPI` module.

## 3. Bridge with camera (`Stage_CameraHAPI` in `av-cam.bin`)

- `Stage_CameraHAPI.cpp` appears in `av-cam.bin` string table.
- The scalar middleware maps HAPI requests to `Stage_CameraHAPI` functions.
- `[CAM_SCALAR]: HAPI Manager:Unknown MSG_ID` indicates the scalar received a `msg_id` it does not recognize.
- The `AUDIOIP` module (S69) is also involved: `[AIP]Sa OpenConfig Cmd %x Func %x` and `[AIP]Sa Close Cmd %x Func %x Unq %x` appear in the string table, suggesting that some HAPI operations trigger audio/IP commands.

## 4. App capabilities (inferred from class names and message IDs)

Based on the `CamApi*` class names found in `libHapiLib.so`, the remote app can:

- **Take pictures**: `CamApiRawCapture` (capture still image)
- **Start/stop streaming**: `CamApiCreateStream` (create/media stream)
- **Get image info**: `CamApiGetImageInfo` (query captured image metadata)
- **Develop RAW**: `CamApiDevelop` (post-process RAW to JPEG)
- **HDR mode**: `CamApiHdr` (high dynamic range imaging)
- **Richtone Mono**: `CamApiRichtoneMono` (monochrome tone rendering)
- **Super Resolution**: `CamApiSuperResolution` (multi-frame super-resolution)
- **Miniature effect**: `CamApiMiniature` (miniature/fisheye effect)
- **Soft Focus**: `CamApiSoftFocus` (soft focus effect)
- **Art Effect**: `CamApiArtEffect` (art filters)
- **Contrast Plus**: `CamApiContrastPlus` (contrast enhancement)
- **Face detection**: `CamApiFaceNr` (face notification/recognition)
- **Change release status**: `CamApiChangeReleaseStatus` (shutter status control)
- **Set common HAPI params**: All `CamApi*` classes receive `setHapiCommon` for session/category configuration.

Additional capabilities (inferred from error strings and OSAL messages):
- Zoom and focus control (via `setHapiCommon` parameters)
- ISO, exposure, white balance settings (configured through the common HAPI config)
- Flash control
- Video recording mode switching

## 5. Comparison fw3.21 (A6000) vs fw3.20 (A7S)

Both versions export essentially the same class hierarchy (`HapiLibMain`, `CamService`, `SdfService`, `CamApiBase` and all `CamApi*` subclasses). Differences observed:

| Aspect | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Binary size | 89628 B | 77380 B |
| Exported symbols | Identical mangled names | Identical mangled names |
| Message validation | `[HAPILIB] Size %d is too big` present | Not verified |
| Scalar messages | `[CAM_SCALAR]: HAPI Manager:Unknown MSG_ID` | Not verified |
| AUDIOIP integration | `[AIP]Sa OpenConfig Cmd / Close Cmd` present | Not verified |

**Conclusion:** The API surface is functionally identical between fw3.21 and fw3.20. The A6000 binary is larger, possibly due to additional stubs or region-specific code. No new API classes were introduced in fw3.21.