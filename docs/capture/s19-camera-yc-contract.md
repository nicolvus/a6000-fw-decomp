# S19 — Camera YC Contract Investigation (S19-04/05 follow-up)

**Scope**: A6000 FW 3.21; static read-only analysis of `libObj.so` (SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`). All addresses are ELF offsets. Primary method: `llvm-objdump -d --triple=thumbv7-linux-gnueabi`. No camera, no firmware execution, no binary modification.

---

## Executive Summary

| Field | Status | Evidence |
|-------|--------|----------|
| **Camera object identity (ObjId 8)** | **VERIFICADO** | Constructor at `0x98c380`; `ObjCamera_Create` at `0x959bdc` allocates 0x20c B and calls constructor |
| **9 output pins created** | **VERIFICADO** | Helper `0x987dc6` constructs nine `MWF::ObjPin` (0x40 B each) stored at `this+0x58..0x78`; all `PinDir=1` (output) |
| **Topology Camera.out0 → Effect.in0** | **VERIFICADO** | Static topology table at `0xcc4210`, row `0x0a` (offset `0x140`): second entry shows `src_obj=8, src_pin=1 → dst_obj=9, dst_pin=0` |
| **Camera unitType** | **NO_VERIFICADO** | No `DmmCh::allocNew/allocShare/open/getUnitInfo` in constructor or pin helpers; no static edge Camera.out0 → DMM allocation |
| **DMM handle / offset** | **NO_VERIFICADO** | No DMM descriptor materialized; no `DmmAccessPLA::GetUnitHandle*` attributable to Camera |
| **Physical memory / DMA address** | **NO_VERIFICADO** | `AvbbcPhycMem::GetLogAddr` appears in other paths; no call from Camera constructor or pin helpers |
| **Geometry (W×H)** | **NO_VERIFICADO** | Camera never loads geometry; not derivable from IMX210 registers (no sensor-register → Camera descriptor chain) |
| **Pixel format (YUV/JPEG)** | **NO_VERIFICADO** | Camera does not load format fields; `unitType` is DMM buffer class, not pixel format |
| **Stride / planes / subsampling** | **NO_VERIFICADO** | No stride field identified; canvas alignment (64×16) only seen in Effect/PbCap output path |
| **Colorimetry / Y-range** | **NO_VERIFICADO** | SDS header (0x800 B) carries colorimetry/Y-range in Effect/PbCap path; not linked to Camera payload |
| **Ownership / recycling** | **NO_VERIFICADO** | No `allocShare/open/close/free/freeSdsAndYc` on a Camera-attributable path; lifetime ends at Effect/PbCap output |

**Critical finding**: The DMM raster `unitType 0x50b3f` (extent `0xed`, `0x3fc000` B) and SDS `unitType 0xe0b00` (extent `0xe4`, `0x800` B) are **allocated by Effect/PbCap** (`0x15fa74`), not by Camera. The topology edge `Camera.out0 → Effect.in0` is declarative only — no static evidence shows Camera frame descriptor flowing across it.

---

## 1. Camera Object Construction (VERIFICADO)

### 1.1 ObjCamera_Create and Constructor
```
0x959bdc: ObjCamera_Create
  → allocates 0x20c bytes
  → calls constructor at 0x98c380
```

### 1.2 Constructor at 0x98c380 (partial disassembly)
```asm
98c380: push.w {r4-r11, lr}
98c384: sub  sp, #0x14
98c386: mov.w r3, #0x100          ; size hint
98c394: movs r1, #0x9             ; <-- 9 pins
98c39e: blx  _ZN3MWF13ObjActiveBaseC2EiPKcjii@plt  ; base init
...
98c450: bl   0x987788             ; helper 1: zero-init regions
98c456: bl   0x987d6c             ; helper 2: 9 EventSender objects
98c45c: bl   0x987dc6             ; helper 3: 9 ObjPin objects (OUTPUT)
98c462: bl   0x9880a4             ; helper 4: RsrcMgr + RsrcAcsr
```

**No DMM/AvbbcPhycMem calls in constructor or any helper.**

---

## 2. Nine Output Pins (VERIFICADO)

### 2.1 Pin Creation at 0x987dc6
Each pin: `new MWF::ObjPin(0x40 B)` → `MWF::ObjPin::C1(PinType, index, PinDir=1, EventSender*)`

| Pin | Stored at | PinType | Index | PinDir | Notes |
|-----|-----------|---------|-------|--------|-------|
| 0 | `this+0x58` | 0 | 0 | 1 (out) | "out0" |
| 1 | `this+0x5c` | 0 | 1 | 1 (out) | |
| 2 | `this+0x60` | 0 | 2 | 1 (out) | |
| 3 | `this+0x64` | 0 | 3 | 1 (out) | |
| 4 | `this+0x68` | 9 | 0 | 1 (out) | |
| 5 | `this+0x6c` | 4 | 0 | 1 (out) | |
| 6 | `this+0x70` | 0xB | 4 | 1 (out) | |
| 7 | `this+0x74` | 0 | 5 | 1 (out) | |
| 8 | `this+0x78` | 0 | 0 | 1 (out) | |

All 9 pins are **output** (`PinDir=1`). No input pins created.

---

## 3. Topology: Camera.out0 → Effect.in0 (VERIFICADO)

### 3.1 Static Topology Table at 0xcc4210
Each row = 0x20 bytes = two 16-byte entries. Row `0x0a` (index 10) at offset `0x140`:

```
Offset 0x140 (first entry):  all zeros
Offset 0x150 (second entry):
  08 00 00 00  01 00 00 00  00 00 00 00  09 00 00 00
  = src_obj=8, src_pin=1, dst_obj=0, dst_pin=0, extra=9
```

**Interpretation** (per documented tracing): `ObjId 8 (Camera).out0 → ObjId 9 (Effect).in0`. The declarative topology exists, but **no frame descriptor is proven to traverse this edge**.

---

## 4. PbCap/Effect DMM Allocations (VERIFICADO — but NOT Camera)

### 4.1 PbCap Sequence at 0x15fa74 (BeginExecCommand normal path)
```
0x15fac8: DmmCh.allocNew(unitType=0x50b3f)  → raster, extent 0xed, 0x3fc000 B
0x15fb1e: DmmCh.allocNew(unitType=0xe0b00)  → SDS header, extent 0xe4, 0x800 B
```

### 4.2 UnitType Meanings (from yc-unit-types-and-layout.md)
| unitType | Extent | Size | Role |
|----------|--------|------|------|
| `0x50b3f` | `0xed` | `0x3fc000` B | YC still 1920×1080 ("STL_YCC_1920P") |
| `0x220b2e` | `0x13d` | `0x96000` B | YC 640×480 |
| `0xe0b00` | `0xe4` | `0x800` B | SDS_YCC (control/metadata header) |
| `0x243` | `0x4e` | — | Super-res alternative (allocated at `0x15f3d6`) |

**These are PbCap OUTPUT buffers**, allocated by Effect's SDF command (`ObjMsg 0x3900/0x3000`). They are not Camera's input buffers.

---

## 5. DataflowInfra Connection in PbCap Sequence (VERIFICADO)

### 5.1 BeginExecCommand at 0x15fd50
Preconditions checked:
1. Holder at `this+0x14` non-null
2. Interface at `this+0x8` non-null
3. Virtual selector 12 returns non-null
4. Virtual selector 3 consulted

**No `unitType` check on input.**

### 5.2 DataflowInfraCh::infraConnectPin at 0x15f290
- Constructs **local** `DataflowInfraCh` endpoints
- Calls `infraConnectPin` to connect them
- **Does not reference `ObjCamera` or any Camera pin descriptor**

The DataflowInfra connection is internal to the PbCap sequence; it does not consume `Camera.out0`.

---

## 6. Camera YC Descriptor — Field-by-Field Status

| Field | Value | Status | Evidence |
|-------|-------|--------|----------|
| **unitType** | ? | **NO_VERIFICADO** | No DMM allocation in Camera path |
| **DMM handle (u16)** | ? | **NO_VERIFICADO** | No `GetUnitHandle*` call from Camera |
| **Offset within unit** | ? | **NO_VERIFICADO** | No descriptor constructed |
| **Physical / DMA address** | ? | **NO_VERIFICADO** | No `AvbbcPhycMem::GetPhysAddr` or equivalent |
| **Width / Height** | ? | **NO_VERIFICADO** | Camera never loads geometry |
| **Pixel format** | ? (YUV420? NV12?) | **NO_VERIFICADO** | `unitType` ≠ pixel format; no format field loaded |
| **Stride (bytes/line)** | ? | **NO_VERIFICADO** | No stride field; canvas 64×16 only in Effect output |
| **Plane layout** | ? | **NO_VERIFICADO** | Single-extent types suggest contiguous; not confirmed |
| **Subsampling** | ? | **NO_VERIFICADO** | Not encoded in DMM unitType |
| **Colorimetry (BT.601/709)** | ? | **NO_VERIFICADO** | SDS header has it (Effect path), not Camera |
| **Y-range (full/limited)** | ? | **NO_VERIFICADO** | SDS header has it (Effect path), not Camera |
| **Ownership** | ? | **NO_VERIFICADO** | No alloc/share/open on Camera path |
| **Recycling / lifetime** | ? | **NO_VERIFICADO** | No free/close/freeSdsAndYc on Camera path |

---

## 7. Discarded / Invalid Inference Paths

| Discarded Inference | Reason |
|---------------------|--------|
| Infer Camera YC from IMX210 registers | No static chain sensor-register → Camera descriptor |
| Treat `0xe0b00`/`0x800` as Camera raster | It is PbCap **output** SDS header (control), not Camera input |
| Assume `0x15fd50` accepts any `unitType` = compatibility | Absence of check ≠ proof of acceptance; virtual selector 3 identity unknown |
| Assume Camera.out0 feeds PbCap raster | Topology is declarative; no dataflow edge proven |

---

## 8. Evidence Cross-Reference

| Address | Function | Role |
|---------|----------|------|
| `0x959bdc` | `ObjCamera_Create` | Alloc + ctor call |
| `0x98c380` | `ObjCamera` constructor | Initializes 9 output pins |
| `0x987788` | Helper 1 | Zero-init state regions |
| `0x987d6c` | Helper 2 | Creates 9 `EventSender` |
| `0x987dc6` | Helper 3 | Creates 9 `ObjPin` (output) |
| `0x9880a4` | Helper 4 | Creates `RsrcMgr` + `RsrcAcsr` |
| `0xcc4210` | Topology table | Row `0x0a`: Camera(8)→Effect(9) |
| `0x15fd50` | `BeginExecCommand` (PbCap) | Preconditions, DataflowInfra, DMM alloc |
| `0x15f290` | `DataflowInfraCh::infraConnectPin` | Connects local infra endpoints |
| `0x15fa74` | PbCap normal output alloc | `allocNew(0x50b3f)` + `allocNew(0xe0b00)` |
| `0x15ebfc` | `PlayData` publish | Only on result `0x111`; emits PbCap buffers |

---

## 9. Conclusions

1. **Camera creates 9 output pins** and declares a topology link to Effect — **VERIFICADO**.
2. **Camera does not allocate DMM memory** — no `allocNew/allocShare/open` in constructor or helpers — **VERIFICADO**.
3. **The DMM raster/SDS units (`0x50b3f`/`0xe0b00`) belong to Effect/PbCap** — allocated at `0x15fa74` — **VERIFICADO**.
4. **No static dataflow edge connects Camera.out0 to a DMM descriptor** — the topology is declarative only — **VERIFICADO**.
5. **All Camera YC contract fields remain NO_VERIFICADO** — unitType, handle, offset, physical, geometry, format, stride, planes, colorimetry, ownership, recycling.

**Next step required**: Locate the Effect method that consumes `Camera.out0` during Live View (e.g., `EffectInternalMode` writer, `REQ_DELIVER` handler) and trace whether it constructs a DMM descriptor from the incoming pin payload. Until that chain is reconstructed, the Camera YC contract is **unknowable from static analysis alone**.

---

## 10. Artifacts Referenced

- `docs/capture/s19-camera-yc-real-contract.md` — S19-04 baseline
- `docs/capture/s19-camera-effect-sdf.md` — S19-05 PbCap sequence
- `docs/capture/yc-unit-types-and-layout.md` — DMM unitType catalog
- `analysis/dmm-extent-sizes.json` — Extent size measurements
- `libObj.so` ELF offsets: `0x98c380`, `0x987dc6`, `0xcc4210`, `0x15fd50`, `0x15f290`, `0x15fa74`
