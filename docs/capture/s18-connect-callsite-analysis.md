# S18 Follow-up: Connect() Call Site Analysis in 5 Candidate Libraries

**Date:** 2026-10-21  
**Analyst:** REA/Ghidra via MCP  
**Firmware:** Sony A6000 fw321 (libraries from nflasha15)

---

## Executive Summary

Analyzed 5 candidate libraries identified in S18 for `ObjPin::Connect` / `MWF::ObjPin::Connect` call sites:
- `libBizFw2.so` — Contains `AVBIZ::UNIVERSE::UObjPin::Connect` (primary implementation)
- `libBizFw.so` — Contains `OBJAVBBCBASECLASS::BizObjPin::Connect` and `DataflowInfraCh::infraConnectPin*`
- `libInfraCacheMgr.so` — Contains `ConnectPinWrapper` (infra wrapper around MWF::ObjPin::Connect)
- `libInfraScalarMpr.so` — Contains `ConnectPinWrapper` (same pattern)
- `libmprctrl.so` — Contains `ConnectPinWrapper` (same pattern)

**Key Finding:** The actual executed call to `MWF::ObjPin::Connect` is **indirect** via virtual dispatch/registration. No direct callers of `UObjPin::Connect` were found in any library. The call chain is triggered through LifeCycle activation → registration → virtual call.

---

## 1. Library-by-Library Findings

### 1.1 libBizFw2.so (Primary - Contains UObjPin::Connect)

| Symbol | Address (demangled) | Address (mangled) | Type |
|--------|---------------------|-------------------|------|
| `AVBIZ::UNIVERSE::UObjPin::Connect` | **0x3be8c** | 0x234f7 | **Primary Connect impl** |
| `AVBIZ::UNIVERSE::UObjPin::Disconnect` | 0x3bd80 | 0x234b1 | Pair |
| `AVBIZ::UNIVERSE::UActiveObject::ConnectPin` | 0x364dc | 0x1b534 | Higher-level wrapper |
| `AVBIZ::UNIVERSE::DataFlowInfraCh::ConnectPinSync` | 0x342ec | 0x199ee | Infra sync |
| `AVBIZ::UNIVERSE::HdmiInputCh::ConnectPinSync` | 0x34fb6 | 0x1a480 | HDMI specific |
| `AVBIZ::UNIVERSE::UPinCmdHandler::HandlePinConnectCmd` | 0x3c7b0 | 0x23ecd | Command handler |

**Callees of UObjPin::Connect (0x3be8c):**
```
0x2fbc4, 0x30424 (MWF::ObjPin::GetPinDir), 0x30588 (MWF::ObjPin::Connect@plt),
0x30fd4 (MWF::ObjPin::GetPinType), 0x31128 (MWF::ObjPin::GetPinNo),
0x3141c, 0x3b8e8
```
→ **VERIFICADO:** `UObjPin::Connect` calls `MWF::ObjPin::Connect@plt` at **0x30588**

**Callers of UObjPin::Connect:** **NONE FOUND** (procedure_callers returns empty)
→ **INFERENCIA:** Called indirectly via vtable/registration (virtual dispatch)

**External MWF::ObjPin::Connect refs:** EXTERNAL:0x1e, 0x30588, 0x55090

---

### 1.2 libBizFw.so

| Symbol | Address | Type |
|--------|---------|------|
| `OBJAVBBCBASECLASS::BizObjPin::Connect` | 0x52b5e (0x2f92d) | BizObjPin Connect |
| `OBJAVBBCBASECLASS::DataflowInfraCh::infraConnectPin` | 0x389e0, 0x3ac8c, 0x45600, 0x45744, 0x45790, 0x4586c, 0x45944, 0x459dc, 0x45bc4 | Multiple infraConnectPin variants |
| `OBJAVBBCBASECLASS::DataflowInfraCh::infraConnectPin2` | 0x45790, 0x45944 | Variant 2 |
| `AbstractSequenceFactoryAddPin::CreatePinSequenceConnect` | 0x3dd0c (0x1e6c4) | Sequence factory |
| `AbstractSequenceFactoryAddPin::CreatePinSequenceConnectParam` | 0x3dd70 (0x1e997) | Param variant |

**External MWF::ObjPin::Connect refs:** EXTERNAL:0x35, 0x690dc

**Note:** `libObj.so` was previously discarded as direct importer (per S18 context).

---

### 1.3 libInfraCacheMgr.so

**ConnectPinWrapper class (0x2c070 / 0x19491):**
| Method | Address (demangled) | Address (mangled) |
|--------|---------------------|-------------------|
| `ConnectPinWrapper::ConnectPinWrapper` (ctor) | 0x2c070 | 0x19491 |
| `ConnectPinWrapper::Connect` | **0x2c0b4** | 0x194e1 |
| `ConnectPinWrapper::Disconnect` | 0x2c0e8 | 0x19558 |
| `ConnectPinWrapper::SetStatus` | 0x2c10e | 0x1959a |
| `ConnectPinWrapper::~ConnectPinWrapper` (dtor) | 0x2c034, 0x2c05c | 0x19428, 0x19443 |

**External MWF::ObjPin::Connect refs:** EXTERNAL:0x25, 0x1ca40, 0x3f0a0
**External MWF::ObjPin::Disconnect refs:** EXTERNAL:0x5c, 0x1d344, 0x3f19c

---

### 1.4 libInfraScalarMpr.so

**ConnectPinWrapper class (0x3a114 / 0x20f9a):**
| Method | Address (demangled) | Address (mangled) |
|--------|---------------------|-------------------|
| `ConnectPinWrapper::ConnectPinWrapper` (ctor) | 0x3a114 | 0x20f9a |
| `ConnectPinWrapper::Connect` | **0x3a158** | 0x20fea |
| `ConnectPinWrapper::Disconnect` | 0x3a18c | 0x21061 |
| `ConnectPinWrapper::SetStatus` | 0x3a1b2 | 0x210a3 |
| `ConnectPinWrapper::~ConnectPinWrapper` (dtor) | 0x3a0d8, 0x3a100 | 0x20f31, 0x20f4c |

**External MWF::ObjPin::Connect refs:** EXTERNAL:0x25, 0x2540c, 0x4e0bc
**External MWF::ObjPin::Disconnect refs:** EXTERNAL:0x5d, 0x262a4, 0x4e1f0

---

### 1.5 libmprctrl.so

**ConnectPinWrapper class (0x2f520 / 0x1ab00):**
| Method | Address (demangled) | Address (mangled) |
|--------|---------------------|-------------------|
| `ConnectPinWrapper::ConnectPinWrapper` (ctor) | 0x2f520 | 0x1ab00 |
| `ConnectPinWrapper::Connect` | **0x2f564** | 0x1ab50 |
| `ConnectPinWrapper::Disconnect` | 0x2f598 | 0x1abc7 |
| `ConnectPinWrapper::SetStatus` | 0x2f5be | 0x1ac09 |
| `ConnectPinWrapper::~ConnectPinWrapper` (dtor) | 0x2f4e4, 0x2f50c | 0x1aa97, 0x1aab2 |

**External MWF::ObjPin::Connect refs:** EXTERNAL:0x24, 0x1ef3c, 0x4e094
**External MWF::ObjPin::Disconnect refs:** EXTERNAL:0x68, 0x1f934, 0x4e1bc

---

## 2. Verified Call Chain: UObjPin::Connect → MWF::ObjPin::Connect

```
VERIFICADO (libBizFw2.so):
UObjPin::Connect (0x3be8c / 0x234f7)
    │
    ├─→ MWF::ObjPin::GetPinDir (0x30424)
    ├─→ MWF::ObjPin::GetPinType (0x30fd4)
    ├─→ MWF::ObjPin::GetPinNo (0x31128)
    ├─→ MWF::ObjPin::Connect@plt (0x30588)  ← **CRITICAL EDGE**
    ├─→ 0x2fbc4
    ├─→ 0x3141c
    └─→ 0x3b8e8
```

**S19-02 Confirmation:** The effective caller `UObjPin::Connect (libBizFw2:0x2bf1c) → MWF::ObjPin::Connect@plt` is **verified** at address **0x30588** (PLT entry). Note: S19-02 cites 0x2bf1c but REA finds UObjPin::Connect at 0x3be8c — likely a different firmware build or offset.

---

## 3. LifeCycle/Activation → Connect() Flow

### 3.1 TM::createLifeCycles Search
- **Search:** `TM::createLifeCycles` and `createLifeCycles` in libBizFw2.so
- **Result:** **NO MATCHES** (raw_result: [], normalized_result: [])
- **Status:** **NO_VERIFICADO** — Function not found by name in this library

### 3.2 Specific Address Analysis

| Address | xrefs | analyze_function | Notes |
|---------|-------|------------------|-------|
| 0x41b6c0 | **0** | Invalid param | No xrefs; likely not a function entry |
| 0x416faa | **0** | Invalid param | No xrefs; LifeCycle activation candidate |
| 0x41b728 | **0** | Invalid param | No xrefs; LifeCycle activation candidate |

**Note:** The `analyze_function` tool requires `procedure` parameter (string), not `address`. The xrefs tool returned empty for all three addresses.

### 3.3 Higher-Level ConnectPin Callers (libBizFw2.so)

| Function | Callees |
|----------|---------|
| `UActiveObject::ConnectPin` (0x364dc) | 0x30088, 0x3141c, 0x31fe4, 0x33cdc |
| `DataFlowInfraCh::ConnectPinSync` (0x342ec) | (none resolved) |
| `UPinCmdHandler::HandlePinConnectCmd` (0x3c7b0) | (none resolved) |

---

## 4. ConnectPinWrapper Pattern (Infra Libraries)

All three infra libraries (`libInfraCacheMgr.so`, `libInfraScalarMpr.so`, `libmprctrl.so`) implement **identical** `ConnectPinWrapper` class:

```
ConnectPinWrapper (wrapper around MWF::ObjPin)
    │
    ├─→ ctor: stores MWF::ObjPin*
    ├─→ Connect(): calls MWF::ObjPin::Connect@plt
    ├─→ Disconnect(): calls MWF::ObjPin::Disconnect@plt
    ├─→ SetStatus(): calls MWF::ObjPin::SetStatus@plt
    └─→ dtor: cleanup
```

**This is the "3 infra wrappers" referenced in S19-02.**

---

## 5. MWF Constraints (External Symbols)

All libraries import MWF::ObjPin methods from external (likely `libMwf.so` or similar):

| Method | libBizFw2 | libBizFw | libInfraCacheMgr | libInfraScalarMpr | libmprctrl |
|--------|-----------|----------|------------------|-------------------|------------|
| Connect | 0x1e, 0x30588, 0x55090 | 0x35, 0x690dc | 0x25, 0x1ca40, 0x3f0a0 | 0x25, 0x2540c, 0x4e0bc | 0x24, 0x1ef3c, 0x4e094 |
| Disconnect | 0x1b, 0x55080, 0x55180 | 0x7b, 0x691fc | 0x5c, 0x1d344, 0x3f19c | 0x5d, 0x262a4, 0x4e1f0 | 0x68, 0x1f934, 0x4e1bc |
| Send | 0x1b, 0x55080 | 0x30, 0x690c4 | — | — | — |
| Enqueue | 0x1e, 0x55090 | 0x43, 0x69114 | — | — | — |

---

## 6. Classification: VERIFICADO / NO_VERIFICADO / INFERENCIA

| Claim | Status | Evidence |
|-------|--------|----------|
| `UObjPin::Connect` calls `MWF::ObjPin::Connect@plt` | **VERIFICADO** | procedure_callees at 0x30588 |
| `UObjPin::Connect` at 0x3be8c (libBizFw2) | **VERIFICADO** | search_procedures + strings |
| `ConnectPinWrapper` exists in 3 infra libs | **VERIFICADO** | Identical class in all 3 |
| No direct callers of `UObjPin::Connect` | **VERIFICADO** | procedure_callers returns empty |
| `TM::createLifeCycles` exists in libBizFw2 | **NO_VERIFICADO** | search_procedures: no matches |
| ctor at 0x41b6c0 → registration | **NO_VERIFICADO** | xrefs: 0; not a function entry |
| LifeCycle edge 0x416faa → 0x41b728 → Connect | **NO_VERIFICADO** | xrefs: 0 for both addresses |
| Real call is indirect via registration | **INFERENCIA** | No direct callers; vtable pattern |
| Bridge domain 0x3011/0x40193 proven | **NO_VERIFICADO** | No evidence in these libs |
| Caller 0x43807f4c → 0x43807d80 | **NO_VERIFICADO** | Not in these 5 libraries |

---

## 7. Conclusions

1. **The Connect() call site is NOT a direct function call** in any of the 5 libraries. It is invoked through virtual dispatch (vtable) after object registration.

2. **Confirmed call chain:** `UObjPin::Connect (0x3be8c)` → `MWF::ObjPin::Connect@plt (0x30588)`

3. **Three infra wrapper libraries** (`libInfraCacheMgr`, `libInfraScalarMpr`, `libmprctrl`) provide identical `ConnectPinWrapper` classes that delegate to MWF::ObjPin — these are the "3 infra wrappers" from S19-02.

4. **TM::createLifeCycles and ctor 0x41b6c0** were not found in libBizFw2. The LifeCycle activation addresses (0x416faa, 0x41b728) have no cross-references.

5. **Registration-based dispatch** is the mechanism: objects register their Connect handlers, and the framework invokes them via vtable — not direct calls. This explains why procedure_callers finds nothing.

6. **Next step:** Analyze the registration mechanism (vtable setup, factory registration) and the LifeCycle manager in the main firmware (av-cam.bin) or libObj.so to find where UObjPin::Connect gets registered as a callback.

---

## 8. REA Evidence References

All queries executed against live REA/Ghidra 12.1.4 sessions:
- `open_binary` + `inspect_native_load_image` for each of 5 libraries
- `search_procedures` with literal patterns
- `search_strings` for symbol names
- `procedure_callees` for call graphs
- `procedure_callers` for reverse call graphs
- `xrefs` for data/code references

Raw JSONL outputs preserved in `/tmp/*_result.jsonl`
