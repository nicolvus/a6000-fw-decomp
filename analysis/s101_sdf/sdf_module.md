# SDF Subsystem (S101)

## What is SDF?

**SDF** stands for **Still DataFlow**. It is the firmware subsystem responsible for processing still-image data flows, including resize/rotate, super-resolution, JPEG encoding, color correction, and other image processing operations for still capture modes. The module has **477 traces** (A6000 fw3.21, prefix `[SDF]`) in the `av-cam.bin` binary, spanning vaddrs `0x43c7785b` → `0x43c806f9`.

SDF is the **dataflow** layer that executes the still-image jobs requested by the capture manager (`IMAGING_CAP`, see S104): resize/rotate, JPEG encode/decode, CCNR, THM. The capture manager owns the *sequence* (which stage runs when); SDF owns the *worker* side that consumes `MSG_ID_SDF_*` jobs and feeds the `OBJAVBBC` (`ObjAVBBCBaseClass::SdfCh`) interface for saving JPEGs. Both belong to the still path — `IMAGING_CAP` is not a video pipeline.

## Key Evidence (vaddr + bytes)

### Module range (A6000)
- **Lo vaddr**: `0x43c7785b` (file offset `0x7785b - 0x43541000 = 7563355`)
- **Hi vaddr**: `0x43c806f9` (file offset `0x806f9 - 0x43541000 = 7566377`)
- **String prefix**: `[SDF]` first appears at file offset `0x7563355` → vaddr `0x43c7785d`
- **SDF_ERR** range: vaddrs `0x43c7a145` → `0x43c7eb78` (file offsets `7573829` → `7592824`)

### MSG_ID_SDF_* message IDs (strings at vaddrs below, all derived from file offset minus `0x43541000`)

| Message ID | Vaddr | Description |
|---|---|---|
| `MSG_ID_SDF_PAINT_IMAGE` | `0x43c78000` | Paint image command |
| `MSG_ID_SDF_COPY_IMAGE` | `0x43c78017` | Copy image command |
| `MSG_ID_SDF_RESIZE_ROTATE` | `0x43c7802d` | Resize/rotate command |
| `MSG_ID_SDF_RESIZE_ROTATE_LOWSPEED` | `0x43c78046` | Low-speed resize/rotate |
| `MSG_ID_SDF_ENCODE_JPEG` | `0x43c78068` | Encode JPEG command |
| `MSG_ID_SDF_DECODE_JPEG` | `0x43c7807f` | Decode JPEG command |
| `MSG_ID_SDF_ENCODE_JPEG_REC` | `0x43c78096` | Encode JPEG rec command |
| `MSG_ID_SDF_DECODE_JPEG_RSS` | `0x43c780b1` | Decode JPEG RSS command |
| `MSG_ID_SDF_ENCODE_JPEG_WITH_WORK` | `0x43c780cc` | Encode JPEG with work |
| `MSG_ID_SDF_REDEYE` | `0x43c780ed` | Red-eye reduction |
| `MSG_ID_SDF_BEAUTY_EFFECT` | `0x43c780ff` | Beauty effect |
| `MSG_ID_SDF_IMAGE_EFFECT` | `0x43c78118` | Image effect |
| `MSG_ID_SDF_IMAGE_MIX` | `0x43c78130` | Image mix |
| `MSG_ID_SDF_SPLIT_ENCODE` | `0x43c78145` | Split encode |
| `MSG_ID_SDF_DEVELOP_RESIZE` | `0x43c7815d` | Develop resize |
| `MSG_ID_SDF_SCN_ENCODE` | `0x43c78177` | Scene encode |
| `MSG_ID_SDF_SCN_ENCODE_WITH_THM` | `0x43c7818d` | Scene encode with THM |
| `MSG_ID_SDF_CCNR_ENCODE` | `0x43c781ac` | CCNR encode |
| `MSG_ID_SDF_CCNR_ENCODE_WITH_MODE` | `0x43c781c3` | CCNR encode with mode |
| `MSG_ID_SDF_PANORAMA_CCNR_ENCODE` | `0x43c781e4` | Panorama CCNR encode |
| `MSG_ID_SDF_THM_COPY` | `0x43c78204` | THM copy |
| `MSG_ID_SDF_THM_ENCODE` | `0x43c78218` | THM encode |
| `MSG_ID_SDF_JPEG_SORT` | `0x43c7822e` | JPEG sort |
| `MSG_ID_SDF_DIST_ENCODE` | `0x43c78243` | Distort encode |
| `MSG_ID_SDF_SPLIT_RESIZE` | `0x43c7825a` | Split resize |
| `MSG_ID_SDF_FACE_RESIZE` | `0x43c78272` | Face resize |
| `MSG_ID_SDF_CCNR_RESIZE` | `0x43c78289` | CCNR resize |
| `MSG_ID_SDF_SET_DATE_IMAGE_PARAM` | `0x43c782a0` | Set date image param |
| `MSG_ID_SDF_SET_DATE_IMAGE_PARAM_DUAL` | `0x43c782c0` | Set date image param dual |
| `MSG_ID_SDF_DIST_RESIZE` | `0x43c782e5` | Distort resize |
| `MSG_ID_SDF_DEVELOP_RESIZE_APL` | `0x43c782fc` | Develop resize APL |
| `MSG_ID_SDF_PTM_COUNT` | `0x43c78350` | PTM count |

*(Note: vaddrs = 0x43541000 + file_offset; full list of 33 distinct messages extracted from binary.)*

### SDF_ERR strings (vaddr `0x43c7a145` onward)

- `[SDF_ERR] bigger_value.ptm_32==PTM_SECOND_ZONE`
- `[SDF_ERR] smaller_value.ptm_32==PTM_FIRST_ZONE`
- `[SDF] interval PTM %ld .`
- `[SDF] check stop PTM stat .`
- `[SDF] check value PTM : PTM 32 . PTM 31 0 : %08x . %08x .`
- `[SDF] m_stop PTM PTM : PTM 32 . PTM 31 0 : %08x . %08x .`
- `[SDF] m_current PTM PTM : PTM 32 . PTM 31 0 : %08x . %08x .`

### Key SDF functions (from decompiled code in session22 evidence)

- **`FUN_43638308`**: SDF initialization/start function, checks runtime flags (`uRam43e50ac0 & 1`), calls `FUN_435a9d04`, then `FUN_435ab6f0(0x43c77857, ...)` — the `0x43c77857` is the SDF module base address.
- **`FUN_435ab6f0(0x43c77857, ...)`**: SDF executor dispatch.
- **`FUN_4363c730`**: SDF JPEG job factory — creates SDF encode/decode jobs.
- **`FUN_4363ca28`**: SDF executor dispatcher with job management.
- **`FUN_43639c78`**: SDF message handler.
- **ObjAVBBCBaseClass::SdfCh::resizeRotate**, **::paintImage**, **::copyImage** (from `libObj.so` symbols at `0x43cd...`).

### SDF ↔ Other modules

| Interface | Evidence |
|---|---|
| **SDF → VDF** | `VDF::VdfToAdfYcDataSender` at `0x43c86165` sends YC data from SDF to ADF/VDF |
| **SDF → ADF** | SDF sends `MSG_ID_SDF_*` messages; ADF receives via `OSAL_MSGQ_GID_DETECT_FACE` path; `[ADF][FC]` bridge |
| **SDF → IMAGING_CAP** | SDF works with `IMAGING_CAP` (697 traces) for still capture pipeline |
| **SDF → DMM** | Allocates DMM units `0x50b3f` (STL_YCC_1920P) and `0xe0b00` (SDS_YCC) for YC buffer management |
| **SDF → MMGR** | Manages memory units via `MMGR` (`L_PRM_MMGR_UNIT_MEM_HANDLE_YCC_CAP`) |
| **SDF → SA (acelerador escalar)** | Some SDF ops (resize/rotate) go through the SA `sa_func_*` dispatch |
| **SDF ↔ OBJAVBBC** | `OBJAVBBCBASECLASS::SdfCh::*`, the C++ class interface for SDF commands |

### Code flow (high-level)

1. **Still capture request** → ADF initializes SDF pipeline
2. **ObjMsg** sent with `MSG_ID_SDF_*` (e.g., `MSG_ID_SDF_RESIZE_ROTATE`, `MSG_ID_SDF_ENCODE_JPEG`)
3. SDF dispatcher (`FUN_435ab6f0`) processes the message
4. SDF allocates DMM units via MMGR for YC/SDS buffers
5. SA functions (`sa_func_GOLFSHOT_*`, `sa_func_CONTP_*`) may be invoked for sub-operations
6. Result returned via acknowledgment messages (`MSG_ID_SDF_*_COMP`)

### SDF in the firmware architecture

- **Larger than ADF** (477 traces vs ADF's 1231, but ADF includes much more: DBGCMD, INIT, SYS, etc.)
- **Specialized for still-image processing**: resize, rotate, encode, CCNR (corner noise reduction), panorama, THM handling
- **Uses PTM (Picture Timing Mode)** for timing coordination (error checks: "bigger/smaller value PTM 32"; actual strings: `bigger_value.ptm_32==PTM_SECOND_ZONE`, `smaller_value.ptm_32==PTM_FIRST_ZONE`)
- **Bridge to PbCap**: The ultimate output of SDF feeds the `PbCap` (picture-before-capture) mechanism for still preview/jpeg generation
- **A7S difference**: A7S fw3.20 has SDF at `0x43c7a1eb` → `0x43c83082` with 479 traces (2 more than A6000), suggesting slight firmware differences

## Summary

SDF is the **Still DataFlow** subsystem that processes still-image pipelines: resize/rotate, JPEG encoding/decoding, CCNR, scene encoding, panorama, and THM handling. It bridges the camera main pipeline to the `OBJAVBBC`/`PbCap` still-output path, using DMM memory units and optionally the SA (scalar accelerator) for computation. The 477 `[SDF]` traces and 15 `[SDF_ERR]` traces span vaddrs `0x43c7785b` → `0x43c806f9`.

Key messages include resize/rotate, JPEG encode/decode, CCNR, panorama, scene encode, THM operations, and develop resize. Errors relate to PTM (Picture Timing Mode) value checking.