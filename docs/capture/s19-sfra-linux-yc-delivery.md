# S19-SFRA — Entrega SFRA → Linux: caracterización del YC interno y entrega JPEG DMM

**Alcance:** Firmware A6000 3.21, análisis estático local y de solo lectura.  
**Herramientas:** REA (Ghidra 12.1.4) sobre `av-cam.bin` (base 0xF3000000), `libInfraStreamingServer.so`, `libScalarDaemon.so`, `libObj.so`.  
**Restricciones:** Sin firmware ejecutado, sin cámara, sin flasheo, sin `git push`.  
**Política:** REA primero; verificación contra bytes/instrucciones. Separación estricta VERIFICADO / NO_VERIFICADO / INFERENCIA.  
**Objetivo:** Caracterizar la ruta SFRA→Linux (YC interno por pines EE/Rec → JPEG READY en DMM → `pubSfrGetJpeg` → `pubMmap` `/dev/mem`), manteniéndola separada de la ruta Camera/Effect.

---

## 1. Resumen de la ruta SFRA→Linux (VERIFICADO)

```
YC interno (pines EE/Rec, ADF/SFRS)
        │
        ▼
SFRA (ScalarInfraAsyncMain, av-cam.bin)
  ├─ Ring de buffers DMM: estados EMPTY/WRITE/READY (12 slots, pool 0x276)
  ├─ GET_JPEG (0x439a282c) saca slot READY, devuelve {handle u16, tamaño >> 7, 0x274}
  └─ Path abierto por SET_PATH(OPEN) (ancho 320/640/1024, alto ≤0x1D00/256)
        │
        ▼ Mensaje OSAL 0x2009/0x100 (servicio SFRA, cmd GET_JPEG)
libInfraStreamingServer.so (ISS, Linux)
  ├─ pvtScalarInfraIF (ELF 0xCA28): alloc msgq 0x2a/0x171 → DataflowInfraSender::SendASync → ReceiveASync
  ├─ pubSfrGetJpeg (ELF 0x19714 thunk → 0x1CC58): parámetros (ushort* handle, uint* size, uint* counter)
  │     └─ Respuesta: handle u16, size = u16 << 7 (bloques 128 B), counter u8
  ├─ MmapLiveViewJpeg / ContentHandlerEEImpl::GetLiveViewJpeg (ELF 0x24568)
  │     └─ pubDmmOpenUnit (ELF 0x19BE0 thunk → 0x21E38): envía msg DMM tipo 5, recibe dmm_extent {phys, size}
  └─ pubMmap (ELF 0x199B4 thunk → 0x2235C): open /dev/mem → mmap(MAP_SHARED|PROT_READ|PROT_WRITE)
        │
        ▼
Cliente Linux (InfraStreamingServerUser / ContentHandlerEEImpl)
  └─ Puntero mapeado + delta → lectura JPEG → release: pubDmmCloseAndFreeUnit / pubDmmFreeUnit
```

---

## 2. Evidencia REA: Funciones críticas en `libInfraStreamingServer.so`

### 2.1 `pubSfrGetJpeg` (ELF 0x1CC58, thunk 0x19714)

**VERIFICADO** — Firma: `void pubSfrGetJpeg(ushort *handle, uint *size_blocks128, uint *counter)`

**Pseudocode REA (0x1CC58):**
```c
int pubSfrGetJpeg(ushort *param_1, uint *param_2, uint *param_3) {
  undefined4 local_190, local_18c, local_188, local_184;
  uchar local_180[368];           // 0x170 B payload OSAL
  uVar2 = 0;
  FUN_0001A378(0x171, 0, 4, 0xA02, &local_190);  // osal_dynamic_id(0x2a,0x171)
  if (local_18c == 0) {           // msgq creado OK
    uVar2 = 0x1A1;
    *param_2 = local_180;         // param_2 = puntero a respuesta (handle en +0x14)
    uVar2 = 0x1A1;
    *param_1 = local_188;         // param_1 = handle u16
    uVar1 = local_18A << 7;       // param_3 = size = blocks128 << 7
    uVar2 = 0x1A1;
    *param_3 = uVar1;
  }
  return uVar2;
}
```

- **Caller 1:** `jobGetLiveView` (ELF 0x1CD0C) — camino Live View
- **Caller 2:** `ContentHandlerSingleEEImpl::Open` (ELF 0x22E20) — camino single EE
- **Servicio OSAL:** 0x2A (categoría), 0x171 (id) — idéntico al lado LIRO (`FUN_439A282C` usa `osal_dynamic_id(0x2A,0x171)`)
- **Payload:** 0x170 B (368 bytes) — coincide con `pvtScalarInfraIF` (ELF 0xCA28)

### 2.2 `pubDmmOpenUnit` (ELF 0x21E38, thunk 0x19BE0)

**VERIFICADO** — Firma: `int pubDmmOpenUnit(dmm_extent *extent, ushort handle)`

**Pseudocode REA (0x21E38):**
```c
int pubDmmOpenUnit(dmm_extent *param_1, ushort param_2) {
  int iVar3 = osal_dynamic_id(0x2A, 0x171, &local_24);
  if (iVar3 == 0) {
    iVar3 = osal_valloc_msg_wait(0x61003C, &local_1C, 0x18, 1);
    if (iVar3 == 0) {
      FUN_00021D6C(local_1C, local_24);  // prepara msg DMM
      memset(local_1C, 0, 0x18);
      local_1C[1] = param_2;             // handle u16 en offset 2
      *local_1C = 5;                     // comando DMM_OPEN_UNIT = 5
      local_1C[10] = 0; local_1C[11] = 0;
      *(uint*)(local_1C+6) = 0xFFFFFFFF;
      osal_snd_msg(0x61003C, local_1C);
      iVar3 = osal_rcv_msg_tmo(local_24, &local_20, 0xFFFFFFFF);
      if (iVar3 == 0) {
        if (*(short*)(local_20+2)==0 && *(short*)(local_20+4)!=-1 && *(short*)(local_20+8)!=0) {
          *(uint*)param_1     = *(uint*)(local_20+0x10);  // base física
          *(uint*)(param_1+4) = *(uint*)(local_20+0x14);  // tamaño
        }
        osal_free_msg(local_24, local_20);
        osal_dynamic_id(0x4A, 0, local_24);
        return 0;
      }
    }
  }
  // manejo de errores → NetworkTraceRecordError
}
```

- **dmm_extent:** 8 bytes `{phys_addr:uint32, size:uint32}` (offsets +0x10/+0x14 en respuesta DMM)
- **Comando DMM:** 5 = OPEN_UNIT (coherente con `pubDmmCloseUnit`=6, `pubDmmFreeUnit`=7)

### 2.3 `pubMmap` (ELF 0x2235C, thunk 0x199B4)

**VERIFICADO** — Firma: `void pubMmap(uint **base, uint **end, uint **delta, uint *size, ushort handle)`

**Flujo verificado (strings + referencias):**
1. `pubDevMemOpen` → `open("/dev/mem", O_RDWR|O_SYNC)` → fd
2. `pubDmmOpenUnit(&extent, handle)` → obtiene `{phys, size}`
3. Alinea `phys` y `size` a página (`sysconf(_SC_PAGESIZE)`)
4. `mmap(NULL, size_aligned, PROT_READ|PROT_WRITE, MAP_SHARED, fd, phys_aligned)`
5. Calcula `delta = phys - phys_aligned`
6. Retorna `base_mmap + delta` en `*base`, `base_mmap + size_aligned` en `*end`
7. `pubDevMemClose` → `close(fd)` al liberar

**Strings de error confirmados:**
- `"(%04d)[ERR:ISS/MMAP: %04d](%s:%d) mmap() error : phy=%08x, size=%ld"` (0x2A9DA)
- `"(%04d)[ERR:ISS/MMAP: %04d] mask=%08x, ofs=%08x, l=%ld"` (0x2AA1E)

### 2.4 `pubDmmCloseAndFreeUnit` / `pubDmmFreeUnit` (ELF 0x222F0 / 0x222FE)

**VERIFICADO** — Distinción por segundo argumento:
- `pubDmmCloseAndFreeUnit(handle)` → envía comando DMM con arg2=2 (close+free)
- `pubDmmFreeUnit(handle)` → envía comando DMM con arg2=0 (solo free)
- **Implicación:** El handle requiere operación explícita de liberación; no hay refcount transferido automáticamente a MPR.

---

## 3. Entrada YC a SFRA: Pines EE/Rec (PinSend 0x439ABBFE)

**Fuente:** `sfra-electronic-frame-source.md`, export `sfra-pinsend.json` (REA sobre `av-cam.bin`)

### 3.1 `PinSend` (av-cam.bin 0x439ABBFE) — VERIFICADO

- **Sistema de pines:** «SFRS» (`SystemCmdPinConnect/Disconnect/Get/RequestConnect/RequestDisconnect/PinSend`)
- **Objeto pin:** Contadores `GetCounter`, `nowVfc`, `osalID`, `Handle`
- **Dos caminos registrados:**
  - **Send RecPin** (grabación) — camino de still
  - **Send EEPin** (EE = visor/Live View) — camino de preview
- **Mensaje emitido:** `0x2009/0xB012` (longitud 0x28, handle de pin, índice de path) hacia el siguiente eslabón
- **Liberación YC:** `FUN_43B63566(handle, -1, -1)` tras enviar

### 3.2 Modo "shutter mute thru" — VERIFICADO

- Función `0x439AC2FA...`, cadena `0x43CE955E`
- Durante apagón de obturador / revisión rápida, SFRA decide *thru* según máscara de tipo de fotograma (`0x20`, `0x01`, `0x30/0x31`)

### 3.3 Productor del YC — INFERENCIA FUERTE

- El YC **no** lo genera SFRA (no «tira» del sensor).
- Llega por pines EE/Rec del sistema de imagen (ADF: `DefDataflowInfraPin.h`).
- **Productor real:** Pipeline de vídeo/EE (DFE/CamCore → ADF pin EE).
- SFRA depende de: (a) path abierto (`SET_PATH(OPEN)`), (b) Live View activo.
- **NO_VERIFICADO:** Quién emite `SystemCmdPinConnect` para EE en modo foto sin Wi-Fi.

### 3.4 Separación de la ruta Camera/Effect — VERIFICADO

| Aspecto | Ruta SFRA (este doc) | Ruta Camera/Effect (ObjCamera→Effect) |
|---------|---------------------|--------------------------------------|
| Entrada YC | Pines EE/Rec internos (ADF/SFRS) | `ObjCamera.out0 → Effect.in0` (topología 0x0A) |
| Productor | Pipeline vídeo/EE (DFE/CamCore) | `ObjCamera` / `ObjRenderer` (NO_VERIFICADO) |
| Salida | JPEG READY (unidad DMM u16) | YC crudo / SDS (contrato abierto) |
| Cliente Linux | ISS (`libInfraStreamingServer.so`) | `CameraSequence` / SDCom / ScalarDaemon |
| Formato probado | JPEG comprimido (handle DMM) | NO_VERIFICADO (unitType, stride, planos) |
| Dimensiones | Ancho 320/640/1024 (ISS) | NO_VERIFICADO |

---

## 4. Gestión de buffers JPEG en SFRA (Ring DMM) — VERIFICADO

**Fuente:** `sfra-linux-client.md`, `sfra-mpr-buffer-bridge.md`, export `sfra-bufmgr.json`

### 4.1 Estructura del ring

- **12 slots** de 0xC bytes cada uno: `{estado:u8, handle:u16@+2, tamaño:u32@+8}`
- **Estados:** EMPTY=0, WRITE=1/2, READY=3
- **Pool DMM:** 0x276 (reservado en `SET_PATH(OPEN)` en `0x439A26BA`)
- **Límite buffers:** 2–256 (`param_1[0xC]`)

### 4.2 `GET_JPEG` (0x439A282C) — VERIFICADO

1. **Dump estado** → itera 12 slots
2. **`getReadyBuf` (0x439A23D0):** Extrae slot READY=3 vía `FUN_43B62A5A`
   - Devuelve `handle u16` y `tamaño`
   - **Retira del ring** con `FUN_43B62A40` → estado EMPTY, handle=0xFFFF **SIN liberar DMM**
3. **Respuesta:** Cabecera 0x14 B + N entradas de 8 B: `{u16 handle, u16 ceil(size/128), u32 0x274}`
4. **`freeReadyBufAll` (0x439A235C):** Libera READY restantes con `FUN_43B6358A(handle,-1,-1)`

### 4.3 Propiedad y lifetime — VERIFICADO

| Fase | Dueño | Acción |
|------|-------|--------|
| WRITE → READY | SFRA | Reserva unidad DMM, llena JPEG HW |
| GET_JPEG respuesta | **Cliente (ISS/Linux)** | Adquiere propiedad; **debe liberar** |
| READY no pedidos | SFRA | Liberados en `freeReadyBufAll` al siguiente GET_JPEG |
| Cierre path (`SET_PATH(CLOSE)`) | SFRA | `freeReadyBufAll` libera todo |

**Evidencia cadenas (av-cam.bin):**
- `[SFRA][BUF] getWriteBuf: Alloc READY(hdl=0x%04x)`
- `[SFRA][BUF] getReadyBuf: id/handle/addr`
- `[SFRA][BUF] getReadyBuf: NO READY JPEG BUF`
- `[SFRA][BUF] freeReadyBufAll: Free(handle)`
- `[SFRA][BUF] freeWriteBuf: FreeOnly(handle)`
- `ERROR(user should free jpeg handles.)`

---

## 5. Entrega al cliente Linux: DMM + mmap — VERIFICADO

### 5.1 Contrato de respuesta GET_JPEG

```
{ handle: u16, size_blocks128: u16, counter: u8 }
```
- `size_bytes = size_blocks128 << 7` (redondeo al alza a 128 B)
- **NO_VERIFICADO:** Tamaño JPEG exacto, firma SOI/EOI, APP/EXIF, resolución

### 5.2 Mapeo DMM → Linux

```
pubSfrGetJpeg → handle u16
       │
       ▼
MmapLiveViewJpeg(handle, size)
       │
       ▼
pubDmmOpenUnit(&extent, handle)  ──► dmm_extent {phys, size}
       │
       ▼
pubMmap(/dev/mem, extent) ──► mmap(MAP_SHARED, RW)
       │
       ▼
Puntero usuario = base_mmap + delta
```

### 5.3 Liberación (VERIFICADO)

- `pubDmmCloseAndFreeUnit(handle)` (arg2=2) — close + free
- `pubDmmFreeUnit(handle)` (arg2=0) — solo free
- **ISS usa:** `pubDmmCloseAndFreeUnit` tras consumo (ELF 0x122F0)

---

## 6. Ruta paralela: CameraSequence / SDCom — SEPARADA

**VERIFICADO** (s19-camerasequence-sdcom.md):

| Elemento | CameraSequence/SDCom | SFRA/ISS |
|----------|---------------------|----------|
| Mensaje inicio | `0x124` (startPreviewSequence) | `SET_PATH(OPEN)` 0x2009/0x1 |
| Mensaje frames | `0x127` (getPreviewSequenceFrames) | `GET_JPEG` 0x2009/0x100 |
| Respuesta | `DeviceMemoryDiadem` (ticket + 3 vectores) | `{handle, size>>7, counter}` |
| Lectura | `mapSharedMemory` + `memcpy` + `unmap` | `pubMmap` `/dev/mem` + mmap |
| Liberación | SDCom `0x3` con ticket | `pubDmmCloseAndFreeUnit` |
| Backend | `libsdcom.so` (SDCom) | OSAL + DataflowInfra + DMM |
| Formato | **NO_VERIFICADO** (640×480/JPEG no probado) | JPEG READY (handle DMM) |
| Productor | **NO_VERIFICADO** | SFRA (HW JPEG en path YC) |

**Conclusión:** Son dos rutas **independientes**. CameraSequence no se enlaza estáticamente a SFRA/ISS.

---

## 7. Caracterización del YC de SFRA (resumen)

| Campo | Valor | Estado | Evidencia |
|-------|-------|--------|-----------|
| **Origen** | Pipeline vídeo/EE → ADF pin EE/Rec | INFERENCIA FUERTE | `PinSend` 0x439ABBFE, cadenas "Send EEPin/RecPin" |
| **Formato entrada** | YC (SDS + raster) | NO_VERIFICADO | Contrato SDS `0xE0B00` + raster `0x50B3F` conocido en ruta Effect, no probado para SFRA |
| **unitType entrada** | NO_VERIFICADO | NO_VERIFICADO | No recuperado de `PinSend` |
| **Dimensiones entrada** | Ancho 320/640/1024 (config ISS) | VERIFICADO (límite ISS) | `jobLiveViewStartCmd` valida ancho ∈ {0x140,0x280,0x400} |
| **Salida SFRA** | JPEG READY (HW) | VERIFICADO | Cadenas `[SFRA][CMD] ***GET_JPEG***`, ring buffers |
| **Formato salida** | JPEG comprimido | VERIFICADO | Handle DMM u16, tamaño en bloques 128 B |
| **Resolución salida** | ≤ ancho ISS (320/640/1024) | VERIFICADO | ISS no pide anchos >1024 |
| **Unidad DMM** | u16 handle (índice unidad DMM) | VERIFICADO | `pubDmmOpenUnit(dmm_extent*, u16)` |
| **dmm_extent** | `{phys:u32, size:u32}` 8 B | VERIFICADO | Respuesta DMM comando 5 en offsets +0x10/+0x14 |
| **Lifetime YC entrada** | Reciclado por pipeline cámara | VERIFICADO | `PinSend` libera con `FUN_43B63566(handle,-1,-1)` |
| **Lifetime JPEG salida** | Propiedad transferida a cliente en GET_JPEG | VERIFICADO | `GET_JPEG` saca del ring; cliente debe liberar |
| **Ownership final** | Cliente Linux (ISS/MPR) tras GET_JPEG | VERIFICADO | `user should free jpeg handles`, `pubDmmCloseAndFreeUnit` |
| **S2 / EFCS / MPR / DCF** | NO_VERIFICADO | NO_VERIFICADO | Sin arista estática a LIRO convencional |

---

## 8. Puntos abiertos (NO_VERIFICADO)

1. **Formato/dimensiones exactas del YC de entrada** (unitType, planos, stride, colorimetría, dirección física)
2. **Productor concreto del YC** (DFE/CamCore → ADF pin: objeto y llamada exacta)
3. **Tamaño JPEG exacto** (parser SOI/EOI necesario; redondeo 128 B oculta tamaño real)
4. **Compatibilidad con mainJpg** (¿el JPEG SFRA sirve para DCF StillInfo?)
5. **Receptor de `SystemCmdPinConnect` para EE en modo foto** (¿quién abre el path?)
6. **Refcount DMM transferido a MPR** (¿`UnitMemShare`/`DMM Reuse` en libmpr?)
7. **Cache coherency** en mmap `/dev/mem` (¿`__builtin___clear_cache` o `msync`?)
8. **Resoluciones >1024** (requieren anchos 0x500/0x5A0/0x780 de `candidate_439A2DD0`; ISS no los pide)

---

## 9. Veredicto

**PARCIAL.**

| Componente | Estado |
|------------|--------|
| SFRA existe en av-cam.bin (cadenas, comandos) | **VERIFICADO** |
| Entrada YC por pines EE/Rec (PinSend 0x439ABBFE) | **VERIFICADO** |
| Ring buffers DMM (EMPTY/WRITE/READY, 12 slots) | **VERIFICADO** |
| GET_JPEG saca handle del ring, transfiere propiedad | **VERIFICADO** |
| pubSfrGetJpeg (0x2009/0x100) → handle + size>>7 | **VERIFICADO** |
| pubDmmOpenUnit → dmm_extent {phys, size} | **VERIFICADO** |
| pubMmap → /dev/mem + mmap(MAP_SHARED, RW) | **VERIFICADO** |
| Liberación explícita (CloseAndFreeUnit / FreeUnit) | **VERIFICADO** |
| Formato/dimensiones YC entrada | **NO_VERIFICADO** |
| Productor YC (DFE/CamCore → ADF) | **INFERENCIA FUERTE** |
| Tamaño JPEG exacto, EXIF, thumb | **NO_VERIFICADO** |
| Enlace a CameraSequence/SDCom | **DESCARTADO** (rutas independientes) |
| SilentShutter funcional | **NO DECLARADO** |

**Separación confirmada:** La ruta SFRA→Linux entrega **JPEG comprimido en unidad DMM**, no YC crudo. La ruta Camera/Effect (ObjCamera→Effect→EncodeStill→Pool) sigue con contrato YC abierto (`s19-camera-yc-real-contract.md`). No equiparar ambos buffers.

---

## 10. Próximos pasos sugeridos

1. **S19-11 (b) completado:** Modos 2–5 ObjEffect con entrada Camera (ver `s19-objeffect-modes-2-5.md`).
2. **Productor YC EE/Rec:** Decompilar `SystemCmdPinConnect` emisor en modo foto; identificar objeto ADF que conecta pin EE a SFRA.
3. **Tamaño JPEG exacto:** Analizar `FUN_439A282C`/`0x439A23D0` para confirmar que `size` devuelto es tamaño real o solo cota.
4. **Bridge MPR:** Verificar `UnitMemShare`/`DMM Reuse` en libmpr para transferir handle SFRA a StillInfo sin copia.
5. **Resolución >1024:** Probar si `SET_PATH(OPEN)` acepta anchos 0x500/0x5A0/0x780 con flag película=1.

---

*Generado por análisis REA (Ghidra 12.1.4) sobre firmware A6000 3.21.  
Evidencia primaria: `libInfraStreamingServer.so` (ELF 0x1CC58, 0x21E38, 0x2235C), `av-cam.bin` (0x439ABBFE, 0x439A282C, 0x439A23D0, 0x43B63566), `sfra-pinsend.json`, `sfra-bufmgr.json`, `iss-dmm-mmap.json`.*
