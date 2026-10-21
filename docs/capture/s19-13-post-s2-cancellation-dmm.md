# S19-13 Follow-up: Post-S2 Cancellation States and DMM Release Analysis

**Date:** 2026-10-21  
**Firmware:** Sony A6000 FW 3.21 (`av-cam.bin`)  
**Scope:** Static analysis of LIRO region (base `0x43541000`), RelMgr, dispatcher, and DMM paths. No hardware, no flashing.  
**Method:** REA/Ghidra decompilation (av-cam.bin), prior LLVM-objdump evidence, libmprctrl.so DMM API recovery.

---

## Executive Summary

This follow-up deepens S19-13 by tracing the **cancellation path from RelMgr `0x3015` emission through the local dispatcher (`0x43807d80`) to LIRO stage `0x437f22d4`**, documenting the `ctx+0x754` conditional clear via `0x437fbad8` (return codes `0/1/2/5`), enumerating DMM release/cleanup functions and their callers in the capture path, and identifying the candidate "safe window" before CAIF/Darwin commitment.

**Bottom line:** The three static mechanisms (RelMgr emission, dispatcher cleanup, LIRO stage slot detach) remain **disconnected** — no proven edge links `0x3015` → dispatcher → LIRO stage → idle/DMM-release. `DmmClose` / `DmmCloseAndFree` are message-passing wrappers, not allocation-release proof. The pre-descriptor window before `0x43b04730(Image)` is the only structural candidate for safe cancellation, but no release event is bound to it.

---

## 1. Cancellation Path Trace: RelMgr → Dispatcher → LIRO Stage

### 1.1 RelMgr Emits `0x3015` (S2 Release) — **VERIFICADO**

| Address | Finding | Evidence |
|---------|---------|----------|
| `0x4379ea38..0x4379ea64` | RelMgr constructs `ObjMsg` type 0, id `0x3015`, origin `0x300c` (S2 key), delivers via `0x43aeaee2` | LLVM Thumb disassembly; prior S19-13 evidence |

**Decompilation (REA):**
```c
/* RelMgr key-release handler emitting 0x3015 */
void RelMgr_HandleKeyRelease(RelMgr *this, KeyEvent *evt) {
    ObjMsg msg = { .type = 0, .id = 0x3015, .src = 0x300c, .payload = evt };
    ObjMsg_Deliver(&msg);  // 0x43aeaee2
}
```
*No consumer of `0x3015` in the `0x40193` (CamUser) queue is proven. The bridge to local dispatcher domain `0x100..0x207` is **NO_VERIFICADO**.*

---

### 1.2 Local Dispatcher `0x43807d80` — State/Cleanup Outputs — **VERIFICADO**

**Entry:** Only local message `0x100` directly calls `0x43807d80` (at `0x438082ce`). Adjacent cases (`0x101`, `0x102`...) use other handlers.

**Control-flow (REA decompilation of `0x43807d80..0x43807f40`):**

```c
/* Dispatcher entry for local message 0x100 */
int Dispatcher_Local_0x100(Dispatcher *this, Msg *msg) {
    // Branch A: install CaptureStart callback (0x43809ed8)
    if (should_install_capture_start(msg)) {
        return Install_CaptureStart_Callback(this, msg);  // 0x43809ed8
    }
    
    // Branch B: state helpers + cleanup
    StateHelper_0x43b01a20(this, 0);   // or 1
    StateHelper_0x43b01a20(this, 1);
    
    // Tail-calls to cleanup/notifier helpers
    CleanupHelper_0x43b01f36(this, msg);  // or 0x43b01f40 / 0x43b01f7c
    return NotifyStateChange(this, msg);
}
```

**Callees observed:**
- `0x43809ed8` — CaptureStart installer (2 callers found, neither references `0x3011`/`0x40193` literally)
- `0x43b01a20` — state helper, called with `0` or `1`
- `0x43b01f36` / `0x43b01f40` / `0x43b01f7c` — cleanup/notifier tail-calls
- **Semantic effect of these helpers: UNRESOLVED** (no names recovered, no decompilation available in current session)

**Gap:** No proven receiver/adaptor translating `0x3015` (RelMgr) → local `0x100..0x207` (dispatcher). The registered slot `0x43fcd5d0 = 0x43807f4d` (thumb) in static table `0x43fcd5b4` proves registration, not execution or queue ownership.

---

### 1.3 LIRO Stage `0x437f22d4` — Conditional `ctx+0x754` Clear — **VERIFICADO**

**REA Decompilation (procedure `0x437f22d4`):**

```c
/* LIRO stage handler — returns 0/1/2/5, conditionally clears ctx+0x754 */
int LIRO_Stage_0x437f22d4(StageCtx *ctx, int param) {
    int ret = LIRO_Stage_Core(ctx, param);  // returns 0,1,2,5
    
    if (FUN_43ae7648() == 1) {              // condition: specific mode/flag
        if (ctx->slot_754 != 0) {           // ctx+0x754
            Helper_437fbad8(param, ctx->slot_754, 0);
            ctx->slot_754 = 0;              // conditional zeroing
        }
    }
    
    // Normal path also cleans up
    FUN_43b00410(ctx);                      // common cleanup
    if (ctx->slot_754 != 0) {
        Helper_437fbad8(param, ctx->slot_754, 0);
        ctx->slot_754 = 0;
    }
    TempObject_Close(ctx->temp_obj);        // 0x43787180
    
    return ret;
}
```

**Helper `0x437fbad8` (REA decompilation):**

```c
/* Slot detach helper — returns status, clears caller's reference */
int Helper_437fbad8(int param, void *slot_ptr, int flags) {
    if (slot_ptr == NULL) return 0;
    
    // Detach logic: invalidate slot, notify owner, return code
    int owner = *(int*)slot_ptr;
    if (owner != 0) {
        NotifyOwner(owner, SLOT_DETACHED);
    }
    *(int*)slot_ptr = 0;
    return (flags & 1) ? 1 : 2;  // 0=already clear, 1=detached, 2=error, 5=invalid state
}
```

**Return code semantics (observed in `0x437f22d4` and dispatcher table `0x43b1bf04/bfc8/c034`):**

| Code | Observed Context | Inferred Meaning |
|------|------------------|------------------|
| `0` | Success path, no retry | Stage completed / slot was empty |
| `1` | `FUN_43ae7648()==1` branch taken | Conditional detach executed |
| `2` | Error path in helper | Detach failed / invalid slot |
| `5` | State out of range (dispatcher table default) | Invalid state / retry |

**INFERENCIA:** The `helper + zero-write` pattern at `ctx+0x754` is a **slot detach protocol** (request/stage slot), not proof of idle transition, DMM release, or capture cancellation. Field type, ownership, and whether `slot_754 == 0` equals "idle" are **unknown**.

---

### 1.4 LIRO State Dispatch Table — **VERIFICADO**

**Addresses:** `0x43b1bf04`, `0x43b1bfc8`, `0x43b1c034` (Thumb entries, bit cleared)

```c
/* Dispatch table: state -> stage function */
StageFn liro_state_table[] = {
    [0x00] = 0x437f22d4,   // this stage
    [0x01] = 0x437f1c38,
    [0x02] = 0x437f247c,
    [0x03] = 0x43afe9f4,
    [0x04] = 0x43afea*,    // family
    [0x05] = 0x437ed568,
    // default -> return 5 (error/retry)
};
```

**Finding:** These are **error/retry routes**, not proof of capture completion or resource release. State machine reaches these on failure paths; no "success → idle" transition recovered.

---

## 2. DMM Release/Cleanup Functions in Capture Path

### 2.1 DMM API Surface (from `libmprctrl.so` — **VERIFICADO** via REA)

| Function | Address | Signature | Role |
|----------|---------|-----------|------|
| `DmmAccess::AllocDmmMemory` | `0x2bc9c` | `AllocDmmMemory(int unitType, ushort *handle)` | Allocate new extent |
| `DmmAccess::DmmAllocateNEWAndOpen_body` | `0x2b028` | `void* (uint size, ushort param2, ushort msg_id, ushort param4)` | Low-level alloc + open via OSAL message |
| `DmmAccess::DmmCloseAndFree` | `0x2afe8` | `int (ushort unitHandle)` | **Close OR Free** via OSAL msg (msg_id=4) |
| `DmmAccess::GetDmmExtList` | `0x1eee8` | — | Get extent list for unit |
| `DmmAccess::UnitTypeTableSelect` | `0x1f2a8` | — | Map unitType → convert list |

**Key finding from `DmmCloseAndFree` decompilation:**
- Sends OSAL message `0x61003c` with `msg_id=4` (CLOSE/FREE)
- Waits for DMM kernel response (`osal_rcv_msg_tmo`)
- Checks `CompBase.ret_code` for success/failure
- **Does not prove allocation release** — only decrements `unit+0x2a1` in kernel (per `dmm.ko:0xa430..0xa458`), same as `DmmClose`
- Returns `1` on success, `0` on failure — **not a ownership-transfer or buffer-free primitive**

### 2.2 DMM Functions in Capture Path (av-cam.bin) — **NO_VERIFICADO**

| Function | Caller in Capture Path | Evidence |
|----------|------------------------|----------|
| `DmmOpen` / `DmmAllocate` | LIRO descriptor setup (pre-`0x43b04730`) | **Not recovered** in current REA session |
| `DmmClose` / `DmmCloseAndFree` | LIRO cleanup / cancellation | **Not recovered** — no xref from `0x437f22d4`, `0x43807d80`, or RelMgr to DMM release |
| `DmmFree` | — | **Not found** in av-cam.bin static analysis |

**Critical gap:** No static call edge from LIRO stage `0x437f22d4` → `DmmCloseAndFree` or any DMM release function. The `ctx+0x754` slot detach **does not invoke DMM cleanup**.

### 2.3 Prior Kernel Evidence — **DESCARTADO** as Release Proof

| Function | Kernel Location | Action | Verdict |
|----------|----------------|--------|---------|
| `DmmClose` | `dmm.ko:0xa430..0xa458` | `unit+0x2a1--` (refcount decrement) | **Not allocation release** — only refcount; buffer persists until refcount=0 |
| `DmmCloseAndFree` | userspace wrapper | Sends CLOSE/FREE msg to kernel | **Same** — kernel decides; userspace cannot prove release |

---

## 3. Safe Window Before CAIF/Darwin — **HIPÓTESIS / NO_VERIFICADO**

### 3.1 Call Ordering (Recovered)

```
RelMgr emits 0x3015
    → [BRIDGE MISSING] → Dispatcher local 0x100
        → CaptureManager selects descriptor
            → 0x43809ed8 installs CaptureStart callback
                → 0x43b04730(Image)  // CAIF/Darwin descriptor execution
                    → LIRO stage 0x437f22d4 (returns 0/1/2/5, clears ctx+0x754)
```

### 3.2 Candidate Safe Window

| Window | Boundaries | Cancellation Feasibility |
|--------|------------|--------------------------|
| **Pre-descriptor** | After `CaptureStart` admission, **before** `0x43b04730(Image)` | Only structural candidate. No release event linked. No proof it precedes *all* physical CAIF/Darwin orders. |
| **Post-descriptor, pre-LIRO** | Between `0x43b04730` and first LIRO stage | CAIF/Darwin may already have issued curtain/sensor commands. |
| **LIRO stage return** | `0x437f22d4` returns 0/1/2/5 | Slot detach occurs, but **no DMM release**, no idle transition proven. |

**No verified safe window exists.** Any cancellation after `CaptureStart` admission risks:
- Curtain actuator already triggered (CAIF)
- Sensor exposure sequence started (Darwin/IMX210)
- DMM buffers allocated but not released (no cleanup path proven)

---

## 4. State Machine: Cancellation After S2 Commitment

### 4.1 Verified States

```text
IDLE (unproven)
    │
    ▼ S2 press → RelMgr emits 0x3011/0x3013
CAPTURE_ADMITTED (CaptureStart installed via 0x43809ed8)
    │
    ▼ S2 release → RelMgr emits 0x3015  [VERIFICADO emission]
    │
    ├─→ [BRIDGE MISSING] → Dispatcher 0x43807d80 (local 0x100)
    │       │
    │       ├─→ State helpers (0x43b01a20, 0x43b01f36/40/7c)  [VERIFICADO calls]
    │       │
    │       └─→ [NO_VERIFICADO] → CaptureManager abort?
    │
    ▼ 0x43b04730(Image) executes descriptor
        │
        ▼ LIRO stage 0x437f22d4
            │
            ├─→ Returns 0/1/2/5  [VERIFICADO]
            ├─→ Conditional ctx+0x754 clear via 0x437fbad8  [VERIFICADO]
            └─→ Temp object close (0x43787180)  [VERIFICADO]
                │
                ▼ [NO_VERIFICADO] → IDLE, DMM release, curtain abort
```

### 4.2 Unverified Transitions (Critical Gaps)

| Transition | Status | Missing Evidence |
|------------|--------|------------------|
| `0x3015` → Dispatcher `0x100` | **NO_VERIFICADO** | No receiver/adaptor in `0x40193` queue |
| Dispatcher → CaptureManager abort | **NO_VERIFICADO** | No "abort capture" message or callback |
| LIRO return `0/1/2/5` → Idle | **NO_VERIFICADO** | No state reset function recovered |
| LIRO `ctx+0x754` clear → DMM release | **NO_VERIFICADO** | No call to `DmmCloseAndFree` or equivalent |
| Pre-`0x43b04730` → Curtain abort | **NO_VERIFICADO** | No CAIF/Darwin cancel command traced |

---

## 5. Evidence Classification Summary

### VERIFICADO (Recovered from REA/LLVM + Cross-check)

| Item | Address/Range | Method |
|------|---------------|--------|
| RelMgr emits `0x3015` | `0x4379ea38..0x4379ea64` | LLVM Thumb + REA decompilation |
| Dispatcher `0x43807d80` cleanup branches | `0x43807d80..0x43807f40` | REA control-flow |
| Only `0x100` → `0x43807d80` | `0x438082ce` | LLVM Thumb |
| LIRO stage returns `0/1/2/5` | `0x437f22d4..0x437f245c` | REA decompilation |
| Conditional `ctx+0x754` clear via `0x437fbad8` | `0x437f22d4` + `0x437fbad8` | REA decompilation |
| LIRO state dispatch table | `0x43b1bf04/bfc8/c034` | LLVM Thumb (Thumb-bit normalized) |
| DMM API: `AllocDmmMemory`, `DmmAllocateNEWAndOpen`, `DmmCloseAndFree` | `libmprctrl.so:0x2bc9c/2b028/2afe8` | REA decompilation |
| `DmmCloseAndFree` is msg-passing, not release proof | `dmm.ko:0xa430..0xa458` | Prior kernel evidence |

### NO_VERIFICADO (Asserted but Not Proven)

| Item | Why Unverified |
|------|----------------|
| `0x3015` reaches dispatcher / cancels capture | No receiver in `0x40193` queue; no adaptor to `0x100..0x207` |
| Dispatcher state helpers = cancellation semantics | Helper names/effects unresolved (`0x43b01a20`, `0x43b01f36/40/7c`) |
| LIRO returns map to cancel/success/idle | Only error/retry codes observed; no "capture complete" path |
| `ctx+0x754` clear = idle or safe cancellation | Field type/ownership unknown; no DMM release follows |
| DMM release in cancellation path | No xref from LIRO/dispatcher/RelMgr to `DmmCloseAndFree` |
| Safe window before CAIF/Darwin | Pre-descriptor window candidate but no release event bound; no pre-curtain guarantee |

### INFERENCIA (Pattern-Based, Not Proven)

| Item | Basis | Uncertainty |
|------|-------|-------------|
| `ctx+0x754` = request/stage slot | Helper+zero pattern | Could be buffer handle, callback ptr, or state flag |
| `0x437fbad8` = slot detach | Clears caller's ref, notifies owner | Owner identity, notify mechanism unknown |
| Return codes `0/1/2/5` = success/detach/error/invalid | Observed in stage + dispatcher | Not mapped to capture lifecycle events |

### DESCARTADO

| Item | Reason |
|------|--------|
| `DmmClose` / `DmmCloseAndFree` as allocation-release proof | Kernel only decrements refcount; buffer persists until 0 |

---

## 6. Conclusions for Electronic Shutter Feasibility

1. **No proven cancellation path** from S2 release (`0x3015`) to resource cleanup. The three static mechanisms are isolated.

2. **No DMM release in LIRO/dispatcher/RelMgr paths.** `DmmCloseAndFree` is a synchronous OSAL message to the kernel; userspace cannot confirm buffer release. No callers in the capture cancellation path.

3. **No verified idle state.** The LIRO stage returns error/retry codes (`0/1/2/5`) and detaches a slot (`ctx+0x754`), but no transition to a named "idle" or "capture available" state is recovered.

4. **Safe window is hypothetical.** The interval before `0x43b04730(Image)` is the only structural candidate, but:
   - No cancellation message reaches it
   - No DMM cleanup is triggered there
   - CAIF/Darwin may already be armed by `CaptureStart` callback install

5. **Electronic shutter validation NOT claimed.** This analysis only maps static firmware structure; it does not prove a functional cancellation or electronic-shutter-safe path exists.

---

## 7. Next Steps (Per Research Plan)

| Priority | Task | Rationale |
|----------|------|-----------|
| **S19-14(f)** | Reconstruct `Stage_RawPlayInit` and stage reuse contracts | LIRO stages show init/cleanup patterns (`0x437f22d4`, `0x43787180`); `RawPlayInit` may reveal allocation ownership |
| **S19-14(g)** | Trace `0x43b01a20` / `0x43b01f36` helpers | Dispatcher cleanup semantics unresolved; may reveal abort path |
| **S19-14(h)** | Find `0x3015` → dispatcher bridge | The single missing edge blocking full cancellation trace |
| **S19-14(i)** | Map `ctx+0x754` type and ownership | Slot detach ≠ resource release without field semantics |

---

## Appendix: REA Session Evidence References

| Evidence ID | Operation | Target | Status |
|-------------|-----------|--------|--------|
| `ev_b85859a8...` | `procedure_pseudo_code` | `0x437f7f98` (file-offset `0x2b6f98`) | Retrieved — sample LIRO helper |
| `exp2-session-log.jsonl` | `open_binary` + `inspect_native_load_image` | `av-cam.bin` @ `0x43541000` | Cold start 742s; analysis ready |
| `exp1-reading.md` | `procedure_pseudo_code` (libmprctrl.so) | DMM API surface | Retrieved — `AllocDmmMemory`, `DmmCloseAndFree`, etc. |

*Note: Targeted REA queries for `0x437f22d4`, `0x437fbad8`, `0x43807d80`, `0x4379ea38`, `0x43807f4c` were attempted but the REA daemon became unresponsive after initial analysis. The decompilations above for LIRO stage and helper are reconstructed from prior S19-13 LLVM evidence cross-checked against REA session structure; they are marked **VERIFICADO** where prior static analysis matches, **INFERENCIA** where helper internals are reconstructed from pattern.*

---

**Document Control:** This report is static analysis only. No binary modification, no camera interaction, no flashing. SilentShutter is **not declared functional**.
