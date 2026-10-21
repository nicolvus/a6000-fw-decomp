# S19-14 Follow-up — Stage_RawPlayInit Reconstruction and Stage Reuse

**Firmware:** Sony A6000 FW 3.21 (`av-cam.bin`, base LIRO `0x43541000`)  
**Scope:** Reconstruct `Stage_RawPlayInit` and stage reuse to recover init/termination contracts and ownership without inferring curtain movement  
**Sources:** Sessions S18–S20 (Ghidra decompilation, REA exports, LIRO initializer analysis), `silent-liro.gpr` (readOnly)  
**Classification:** VERIFICADO / NO_VERIFICADO / INFERENCIA — SilentShutter NOT declared functional

---

## 1. Executive Summary

This report consolidates findings from sessions S18–S20 on the `Stage_RawPlayInit` symbol, the LIRO capture sequence table (`0x43edccf8` initialized by `0x437ebed8`), and the stage initialization/reuse mechanisms. The investigation was driven by task D ("reutilizar etapas") and specifically S19-14.

**Key conclusions:**
- `Stage_RawPlayInit` string exists at `0x43cad51b` but has **zero registered code references** in the Ghidra project (auto-analysis limited to 300s, partial). Absence of references ≠ dead code.
- The `Stage_DevLater` pathway (caller `FUN_43afe192` → `FUN_437edd44` → `FUN_437edaf8`) **reads `.ARW` files from SD card**, not from in-memory YC buffers. This closes the hypothesis that this route enables mechanical-shutter-free capture from Live View YC.
- A **real 3-word descriptor save/restore mechanism** exists at `ctx+0x4b54/+0x4b58/+0x4b5c` ↔ `ctx+0x4ad0+0x16cc/+0x16e0/+0x16e4`, shared by `Stage_Notify`, `Stage_Apollo`, `Stage_Orientation`, and generic helpers `FUN_43afe9f4`/`FUN_43afe11a`. This is **metadata only** (pointer + 2 fields); no evidence it transports pixel data.
- The LIRO sequence table (15 rows, 20 bytes each) is **statically reconstructible** via initializer `0x437ebed8` + GOT descriptors, not "BSS-only unrecoverable." Four rows are dynamically selectable at offsets `0xa0, 0xc8, 0xdc, 0x104` (corrected from earlier recollection).
- Stage state machine contract: each row is `uint32 f(Image*)` with `switch(FUN_43afdf16())` dispatching on current state. Verified states for row 8 (`0x43b1be36`): 0=capture request/retry, 1=sensor/exposure setup, 2=parameter prep, 3=Linux notify (0x1000), 4=RAW stage startup, 5=per-image accounting, 6=NextSection advance.
- **No evidence** that any LIRO row or Stage_* function bypasses CAIF/Darwin/SACC for sensor acquisition. Stage reuse for SilentShutter would require replacing states 1/2/4 (sensor/RAW) with "take retained YC and encode" while preserving 0/3/5/6 (request, notify, accounting, advance).

---

## 2. Stage_RawPlayInit and Related Strings — VERIFICADO

| String | File Offset | VA (LIRO base `0x43541000`) |
|--------|-------------|------------------------------|
| `Stage_RawPlayInit` | `0x76c51b` | `0x43cad51b` |
| `ycc_rawplay: %x` | `0x76c4dc` | `0x43cad4dc` |
| `sds_ycc_handle: %x` | `0x76c508` | `0x43cad508` |

**VERIFICADO** — Strings exist literally in `av-cam.bin` (confirmed via `strings -a`).  
**VERIFICADO** — Ghidra project `QuerySilentReferences.java` reports **0 references** to all three addresses.  
**INFERENCIA** — Absence of references does not prove dead code: Ghidra auto-analysis is partial (300s limit, warnings documented). References may exist via indirect jump, pointer table, or non-literal address calculation not resolved by auto-analysis.  
**VERIFICADO** — Neighboring diagnostic strings in same cluster DO have registered references:
- `Stage_DevLater.cpp` (`0x43cac51b`, 2 refs → `FUN_437edaf8`)
- `Stage_Notify.cpp` (`0x43caccd6`, 8 refs → `0x437ef8cc`/`0x43b1ad32`/`0x43b1bb4c`)
- `Stage_SACC`/`Stage_SACC.cpp` (`0x43c9ee6c`/`0x43c9f18a`, 34 refs → `0x43b196c8`)
- `Stage_NotifyLongExpNRCapturing` (`0x43caccb7`, 4 refs → `0x43b1ae2a`)

---

## 3. Stage_DevLater Call Chain — VERIFICADO (Closed Path)

**Full verified call chain** (decompilation: `analysis/session20/evidence/s20-rawplay-dec2.json`, `s20-rawplay-dec3.json`):

```
FUN_43afe192 (case 0, ctx+0x3c==0 gate)
  → FUN_437edd44()          // Opens/parses .ARW from SD card
  → FUN_437edd1c()          // Gate: returns 1 iff DAT_4401eabf!=0 && *(DAT_4402546c+0x73)!=0
  → FUN_437edd04(&buf)      // Copies 0x70 bytes from DAT_43ede284 (static config block from lookup 0x1c3)
  → FUN_43561604(buf)       // Vtable call
  → FUN_437edaf8(ctx, uVar4, 0)  // Stage_DevLater, param_3=0
```

**FUN_437edd44 behavior (VERIFICADO):**
- Constructs path `DCIM/100MSDCF/DSC%05d.ARW` (string `0x43cac566`)
- Opens via `FUN_439005b8`, parses TIFF tags `0x111` (StripOffsets) and `0x117` (StripByteCounts) via `FUN_437edaa4`
- Verifies strip size against `param_1+0x4e64`, copies raw strip bytes to `param_1+0x4e60+0x4e58`
- Sets global `DAT_4401eabf` = 1 on success, 0 on any failure

**Conclusion (VERIFICADO, negative for this route):** This pathway **develops an existing `.ARW` file on SD card** — it requires a prior RAW capture (mechanical or not). It does NOT accept an in-memory YC buffer from Live View. The `uVar4` passed to `Stage_DevLater` is a 0x70-byte config block, not a pixel descriptor.

**DESCARTADO:** Mechanical independence via this specific route.

---

## 4. Descriptor Save/Restore Mechanism — VERIFICADO (Metadata Only)

**Function:** `FUN_437ef8cc` (Stage_Notify helper, also called from `FUN_43afe9f4`, `FUN_43afe11a`)

**Shared context fields (VERIFICADO):**
- `ctx+0x4ad0` → secondary object (base for saved descriptor)
- `ctx+0x4ad4` → circular array with cursor (`+0x20` size, `+0x28` cursor)
- `ctx+0x4b54/+0x4b58/+0x4b5c` → 3-word descriptor (pointer + 2 fields)
- `ctx+0x4b60` → mode selector (0/1 = save, 2 = restore)

**Mechanism (VERIFICADO from decompilation):**
```
if *(ctx+0x4b60) < 2:      // 0 or 1
    save:  *(ctx+0x4ad0+0x16cc) = *(ctx+0x4b54)
           *(ctx+0x4ad0+0x16e0) = *(ctx+0x4b58)
           *(ctx+0x4ad0+0x16e4) = *(ctx+0x4b5c)
elif *(ctx+0x4b60) == 2:   // restore
    *(ctx+0x4b54) = *(ctx+0x4ad0+0x16cc)
    *(ctx+0x4b58) = *(ctx+0x4ad0+0x16e0)
    *(ctx+0x4b5c) = *(ctx+0x4ad0+0x16e4)
if *(ctx+0x1e0) in {3,9,0x1c}:  // capture type values seen elsewhere
    FUN_437e0b88()  // additional word-range copy
```

**Stage_Notify (`FUN_43b1ad32`) cases (VERIFICADO):**
- **Case 0:** Reads circular array at `ctx+0x4ad4`, extracts 3-word tuple from entry `+0x44/+0x48` → `ctx+0x4b58/+0x4b5c`, builds and sends message **0x1003** via `FUN_437feef8(..., 0x1c, &DAT_00020002)` (LIRO command send pattern).
- **Case 1:** References `Stage_Orientation.cpp` (`0x43cc97b4`), reads `ctx+0x4ad0+0x1c`/`+0x1c0d`.
- **Case 2:** Calls `FUN_437873a4(..., 0xe0b00, 1, ...)` — **SDS unit `0xe0b00`** (0x800 B control block for PbCap/SDF, confirmed S19-05), inside SPICA/TAP calibration parameter path (`Stage_ExpandSpicaParam`, `SPICA_PCOEF`, `TAP1_ODL_GetBinaryData`).
- **Case 4:** Uses unit-types `0x50b0b` and `0x50b2e` (raster/resize family, distinct from `0x50b3f`).

**Stage_Apollo (`FUN_43b1bb4c`, newly identified):**
- Operates on same `ctx+0x4ad0` at fields `+0x1bfc/+0x1c00/+0x16bc/+0x16be/+0x170c`
- Conditional on `*(ctx+0x534c)` ∈ `{2,4}`

**VERIFICADO:** Fields `ctx+0x4ad0`, `+0x4ad4`, `+0x4b54/58/5c` are shared by Stage_Notify, Stage_Apollo, Stage_Orientation, and generic helpers `FUN_43afe9f4`/`FUN_43afe11a` (cited in S19-07 as called from multiple LIRO rows).

**INFERENCIA:** This is a **metadata descriptor** mechanism (3 words = pointer + 2 fields). No verification that it points to valid YC pixel buffers, their size, or format.

**NO_VERIFICADO:** Whether any Live View path (not RawPlay/DevLater) writes these descriptor fields before `FUN_437ef8cc` saves them.

---

## 5. LIRO Sequence Table (0x43edccf8) — VERIFICADO

**Initializer:** `0x437ebed8` (master table initializer, VERIFICADO via `scripts/ghidra_dec.sh` and `llvm-objdump`)

**Pattern:** Iterates ≥9 tables, calls `FUN_43afb46a(row_ptr, GOT_descriptor)` per 20-byte row (`+0x14` increments). `FUN_43afb46a` → `FUN_437de944` initializes each row as:
```
row[0] = DAT_44020894  // shared vptr
row[1] = 0             // initial state = 0
row[2] = GOT_descriptor // function pointer from GOT slot
```

**Capture sequence table at `DAT_44022934` → `0x43edccf8` (VERIFICADO):**

| Row Offset | GOT Descriptor | Real Thumb Function (ptr-1) |
|------------|----------------|----------------------------|
| `0x00`     | `0x440236b8`   | `0x43b1bc0d` |
| `0x14`     | `0x440223a4`   | `0x43b1bc25` |
| `0x28`     | `0x44026110`   | `0x43b1bc71` |
| `0x3c`     | `0x44021940`   | `0x43b1bcc7` |
| `0x50`     | `0x440241a0`   | `0x43b1bd13` |
| `0x64`     | `0x440268e0`   | `0x43b1bd5f` |
| `0x78`     | `0x44020b28`   | `0x43b1bdb5` |
| `0x8c`     | `0x44025d08`   | `0x43b1be01` |
| **`0xa0`** | `0x44023a6c`   | **`0x43b1be37`** |
| `0xb4`     | `0x440265b8`   | `0x43b1be99` |
| **`0xc8`** | `0x4401f664`   | **`0x43b1bf05`** |
| **`0xdc`** | `0x44023054`   | **`0x43b1bf67`** |
| `0xf0`     | `0x44026070`   | `0x43b1bfc9` |
| **`0x104`**| `0x44022dd4`   | **`0x43b1c035`** |
| `0x118`    | `0x44023c3c`   | `0x43b1c097` |

**Correction (VERIFICADO, S18 §4):** Dynamically selectable rows (via selector `0x437eabfc` logic `iVar7*0x14` with `iVar7 ∈ {8,0xa,0xb,0xd}`) are **`0xa0, 0xc8, 0xdc, 0x104`** (bold above). Row `0xb4` reached via separate direct branch (first condition).

**VERIFICADO:** Each entry is a **trampoline** (`push {r2}; b <far_target>`) jumping to dense implementations at `~0x43b1c2c9`–`0x43b1c32b`. Ghidra follows transparently; decompilation shows real logic.

**Selector logic (VERIFICADO, S17/S18):** `0x437eabfc` — 4-level decision tree on capture request fields (`+0x4b70`, `+0x54a5`, `+0x1d8`, `+0x1e0`, `+0x70`). No Silent/EFCS mode flag in selector. Normal single-shot → row 8; `+0x1d8≠0` → 0xb; `+0x1e0==7` → 0xa/0xd; burst → 8/12; `+0x4b70==7` → 15; other `+0x4b70` → 14.

---

## 6. Stage State Machine Contract (Row 8 / 0x43b1be36) — VERIFICADO/INFERENCIA

**Function:** `0x43b1be36` (row 8, normal capture) — 399 lines decompiled (`liro-seqrows.json`)

**Contract:** `uint32 f(Image*)` → returns next state (0,1,2,3,5 observed). Dispatch via `FUN_43afdf16()` (current state getter) + `tbb`.

| State | Verified Actions | Sensor/Mechanical? |
|-------|------------------|-------------------|
| 0 | Capture request: `Capture Req Retry exp_id`, retry counter `+0x750<0x14`, `Capture Cancel`, wait `0x4372a73c(0x13)`, sets `FUN_436e9b08` (mode by `+0x1e0`) | No (request mgmt) |
| 1 | `0x43ae8220`, `0x43901a8c(4,..)`, wait `RawDevInit WAIT IMG PARAM` if `+0x4b70≠0`, `0x437f7ff0`, `0x43b00410`, **`0x436d6168`**, `0x43783764`, `0x436c2270`, `0x43ae9226(…0x9400…)` | **Probable:** sensor/exposure config (0x436d61xx = SetExposure/SetRead per S19-12) |
| 2 | `0x43795a60`, `0x436d6118`/`0x436d61a4`, `0x4383fd6c`, `0x438d0420` | Config |
| 3 | Linux notify: msg type 4, id **0x1000**, seq `+0x4b64`, result `0xf000`, 4-byte status; `0x437feef8(msg,0x1c,0x20002)` | No (differs from Stage_Notify 0x1006) |
| 4 | `Stage_Raw.cpp`: `0x438bf1bc`, `0x43782f10`, `0x437dd400`, `0x437dd4dc`, `0x43afb276` (RAW stage reserve/start; FATAL error `Stage_Raw.cpp:0x109`) | **Yes:** acquisition startup |
| 5 | `0x43afe8a4(+0x4b64, +0x4b54, idx)` per-image (result accounting) | Post-acquisition |
| 6 | `NextSection`: `0x43afbf44`, `0x437e58c4`; msg `Stage_NextSection CapInit1st` (`Stage_Common.cpp`) | Section advance |

**INFERENCIA (strong):** Row does NOT contain Stage_* functions directly — each state invokes sections (`0x437dd400` etc.). Stage_Notify 0x1006 (`0x437efe78`) is in a later section.

**INFERENCIA (Silent row design):** A Silent row should reproduce states 0/3/5/6 (request, 0x1000 notify, accounting, advance) and **replace** 1/2/4 (sensor/exposure/RAW) with "take retained YC → encode → Stage_Notify 0x1006".

**NO_VERIFICADO:** States 1, 4+ full bodies (which emit CAIF/SetMode/SACC). Exact Stage_* mapping per state.

---

## 7. Stage Initialization/Termination Contracts — VERIFICADO/INFERENCIA

### 7.1 Row Object Structure (VERIFICADO)
Each 20-byte row = LifeCycle-like object:
- `+0x00`: vptr (`DAT_44020894`, shared constant)
- `+0x04`: state (initial 0, updated by `FUN_43afdf16`/`FUN_436e9b08`)
- `+0x08`: function pointer (from GOT descriptor)
- `+0x0c..+0x13`: unused/padding in this pattern

**Ownership:** Rows live in BSS (`0x43edccf8`), initialized once at boot by `0x437ebed8`. Selector `0x437eabfc` returns `row_ptr` to caller (`CaptureManager` → `0x43b04730`). Caller owns the `Image*` passed to row function.

### 7.2 Stage_* Section Functions (INFERENCIA from naming + S20 findings)
| Stage | Function(s) | Context Fields | Notes |
|-------|-------------|----------------|-------|
| Stage_DevLater | `0x437edaf8` | `ctx+0x4b70..+0x4fe0` ← `ctx2+0x27e4..+0x28e4` | Copies capture context block; **reads .ARW from SD** |
| Stage_Notify | `0x437ef8cc`, `0x43b1ad32`, `0x43b1bb4c` | `ctx+0x4ad0`, `+0x4ad4`, `+0x4b54/58/5c`, `+0x4b60` | Descriptor save/restore, msg 0x1003/0x1006, SDS 0xe0b00 |
| Stage_Apollo | `0x43b1bb4c` (self-identified) | `ctx+0x4ad0+0x1bfc/1c00/16bc/16be/170c` | Conditional on `ctx+0x534c ∈ {2,4}` |
| Stage_Orientation | Referenced in `FUN_43b1ad32` case 1 | `ctx+0x4ad0+0x1c/0x1c0d` | Newly identified |
| Stage_Raw | `0x438bf1bc`, `0x437dd400`, `0x437dd4dc` | Via row state 4 | RAW acquisition startup (FATAL `Stage_Raw.cpp:0x109`) |
| Stage_SACC | `0x43b196c8` | 34 refs | Separate cluster |
| Stage_NextSection | `0x437e58c4` | `Stage_Common.cpp` string | Section advance |

### 7.3 Init/Fini Contracts (INFERENCIA from observed patterns)
- **Init:** Row entry (state 0) → capture request → parameter setup (state 1/2) → Linux notify 0x1000 (state 3) → RAW stage startup (state 4)
- **Per-image:** Accounting (state 5) → NextSection (state 6) → subsequent sections (encode, notify 0x1006, cleanup)
- **Termination:** Conditional cleanup at `0x437f22d4` (S19-13): clears `ctx+0x754` via `0x437fbad8`, returns `{0,1,2,5}`. No unified "stage fini" observed — cleanup distributed across states and cancellation paths.
- **Ownership transfer:** `Image*` passed through row states; descriptor at `ctx+0x4b54/58/5c` saved/restored via `ctx+0x4ad0` for cross-stage metadata continuity. **No evidence of pixel buffer ownership transfer** in this mechanism.

---

## 8. Stage Reuse Patterns — VERIFICADO/INFERENCIA

### 8.1 Verified Reuse Mechanisms
1. **Descriptor save/restore** (`FUN_437ef8cc`): 3-word metadata saved at `ctx+0x4ad0+0x16cc/0x16e0/0x16e4` on first pass (mode 0/1), restored on mode 2. Shared by Notify/Apollo/Orientation/generic helpers.
2. **Circular array** at `ctx+0x4ad4`: Stage_Notify case 0 reads entries (`+0x44/+0x48` per entry) → `ctx+0x4b58/5c` → sends msg 0x1003.
3. **Context block copy** (`Stage_DevLater`, `FUN_437edaf8`): `ctx+0x4b70..+0x4fe0` ← `ctx2+0x27e4..+0x28e4` (0x270 bytes). Same offsets as conventional capture context (S19-12/S19-07).
4. **Row selection reuse:** Selector `0x437eabfc` picks from same 15-row table for all capture types (normal, burst, `+0x1e0==7`, `+0x4b70==7`, etc.). No dedicated Silent row.

### 8.2 Resource Management (INFERENCIA)
- **DMM buffers:** SDS `0xe0b00` (0x800 B control) + raster `0x50b3f`/`0x50b0b`/`0x50b2e` (unit-types). Verified S19-05/S20.
- **Lifecycle:** Row object persists in BSS; `Image*` and `ctx` passed per-capture. Descriptor save/restore enables metadata continuity across stage transitions.
- **Cancellation:** State 0 handles `Capture Cancel`; `0x437f22d4` cleans `ctx+0x754` conditionally. No centralized stage teardown observed.

### 8.3 SilentShutter Reuse Hypothesis (INFERENCIA — NOT VERIFIED)
To reuse stages for SilentShutter (electronic shutter only):
- **Keep:** Row states 0 (request), 3 (0x1000 notify), 5 (accounting), 6 (NextSection), Stage_Notify 0x1006 path, S2Handler/counter cleanup.
- **Replace:** States 1 (sensor config), 2 (exposure params), 4 (RAW stage startup) with "acquire retained YC → configure encoder → Stage_Notify 0x1006".
- **Blocker:** No verified path that feeds Live View YC into this pipeline without sensor acquisition. `Stage_DevLater` reads `.ARW` from SD. Descriptor mechanism is metadata-only. CAIF/Darwin/SACC calls in states 1/2/4 not fully mapped.

---

## 9. Evidence Index

| Source | Type | Key Content |
|--------|------|-------------|
| `analysis/session20/evidence/rawplay-string-refs.json` | Ghidra refs | 0 refs for 3 RawPlay strings; refs for neighbor Stage_* strings |
| `analysis/session20/evidence/s20-rawplay-dec1.json` | Decompilation | `0x437edaf8`, `0x43b1ad32`, `0x43b1bb4c`, `0x437ef8cc`, `0x43b196c8`, `0x43b1ae2a` |
| `analysis/session20/evidence/s20-rawplay-dec2.json` | Decompilation | `0x43afe9f4`, `0x43afe11a`, `0x43afe192` (call chain to Stage_DevLater) |
| `analysis/session20/evidence/s20-rawplay-dec3.json` | Decompilation | `0x437edd44`, `0x437edd1c`, `0x437edd04`, `0x43561604`, `0x43ae7648` (.ARW path) |
| `analysis/session20/evidence/s20-rawplay-callers.json` | Callers | Registered callers of key functions |
| `docs/capture/s18-main-init-437ebed8.md` | Markdown | LIRO initializer, 15-row table, GOT descriptors, trampolines |
| `docs/capture/s19-liro-remaining-sequences.md` | Markdown | 10 non-selected rows decompiled, all conventional family |
| `docs/capture/s19-mechanical-shutter-decision-points.md` | Markdown | Guard points that can block conventional path (C2 corrected) |
| `docs/capture/s19-post-s2-cancellation-states.md` | Markdown | Post-S2 cleanup, `0x437f22d4`, `0x437fbad8` |
| `docs/capture/capture-stage-reuse.md` | Markdown | Row 8 state table, Silent row inference |
| `docs/capture/s20-rawplay-stage-reuse.md` | Markdown | Full S20 investigation (this report's primary source) |

---

## 10. Open Blockers (NO_VERIFICADO)

1. **Real class of ObjId 53** (topology source for row 0xb4/0x2a) — not ObjStillRecorder (C1 corrected). Auto-registration map not found.
2. **CAIF/Darwin/SACC emission points** in LIRO row states 1/2/4 — not fully decompiled.
3. **Live View YC producer → descriptor fields** (`ctx+0x4b54/58/5c`) — who writes them before `FUN_437ef8cc` saves?
4. **Stage_Notify 0x1006 emitter** (`0x437efe78`) — which section/state emits it? Not in row 8 decompilation.
5. **Complete stage teardown contract** — distributed cleanup, no single fini function identified.
6. **Whether any LIRO row bypasses sensor acquisition** — all 15 rows analyzed are conventional family (S19-07).

---

## 11. Classification Summary

| Finding | Classification |
|---------|----------------|
| `Stage_RawPlayInit` string exists at `0x43cad51b` | VERIFICADO |
| Zero Ghidra-registered references to RawPlay strings | VERIFICADO |
| Stage_DevLater call chain reads `.ARW` from SD card | VERIFICADO |
| Stage_DevLater does NOT accept in-memory YC | VERIFICADO |
| 3-word descriptor save/restore at `ctx+0x4b54/58/5c` ↔ `ctx+0x4ad0` | VERIFICADO |
| Descriptor shared by Notify/Apollo/Orientation/helpers | VERIFICADO |
| Descriptor is metadata (ptr+2 fields), not verified as pixel buffer | VERIFICADO |
| LIRO table `0x43edccf8` reconstructed via `0x437ebed8` + GOT | VERIFICADO |
| 15 rows, 4 dynamically selectable at `0xa0,0xc8,0xdc,0x104` | VERIFICADO |
| Row 8 (`0x43b1be36`) state machine: 7 states documented | VERIFICADO |
| Row 8 states 1/2/4 involve sensor/exposure/RAW | INFERENCIA (strong) |
| Row 8 state 3 emits 0x1000 (not 0x1006) | VERIFICADO |
| Silent row would replace states 1/2/4, keep 0/3/5/6 | INFERENCIA |
| No LIRO row has Silent/EFCS mode flag | VERIFICADO |
| Stage_Notify 0x1006 (`0x437efe78`) in later section | INFERENCIA |
| Stage_Apollo (`0x43b1bb4c`) newly identified | VERIFICADO |
| SDS `0xe0b00` used in Stage_Notify case 2 | VERIFICADO |
| Unit-types `0x50b0b`/`0x50b2e` for resize (≠ `0x50b3f`) | VERIFICADO |
| Full init/fini contracts per stage | NO_VERIFICADO |
| Pixel buffer ownership transfer in descriptor mechanism | NO_VERIFICADO |
| Any path feeding Live View YC into capture pipeline | NO_VERIFICADO |

---

## 12. Next Concrete Steps

1. **Decompiler `FUN_43ae75dc`** (context getter used by all stages) to identify what subsystem populates `ctx+0x4b54/58/5c` before `FUN_437ef8cc` saves them. Check if any Live View path writes these fields.
2. **Decompile remaining LIRO row implementations** at `~0x43b1c2c9`–`0x43b1c32b` (targets of trampolines for rows `0xa0/0xc8/0xdc/0x104`) to verify if any has Silent-like logic.
3. **Trace CAIF/Darwin/SACC calls** in row 8 states 1/2/4 and row 0xb4 to map exact mechanical shutter decision points.
4. **Locate Stage_Notify 0x1006 emitter** (`0x437efe78`) and its caller section/state.
5. **Verify descriptor pointer validity** — does `ctx+0x4b54` ever point to a Live View YC buffer (DMM extent handle, offset, size)?

---

**End of Report** — All findings traceable to session evidence files listed in §9. No curtain movement inferred from stage transitions.
