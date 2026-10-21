# S19-ObjId53 — Class Identification by Self-Registration (Follow-up)

**Estado: NO_VERIFICADO** — La clase concreta asociada al entero 53 (0x35) no se ha recuperado; no se localizó su constructor ni sitio de auto-registro explícito.

---

## 1. Objetos y direcciones de interés

| Elemento | Dirección | Tamaño / notas |
|---|---|---|
| `ObjStillRecorder_Create` | 0x91391c | Exportada; reserva 0x148 B, llama a ctor 0x9178f0 |
| Constructor `ObjStillRecorder` | 0x9178f0 | Inicializa `MWF::ObjActiveBase(0x2f)`, vtable, 3× `ObjPin` + `ConnectPinWrapper` |
| Topología fila 0xb4 | `.rodata` 0xcc5890 (base 0xcc4210 + 0xb4×0x20) | `[0, 6, 0x35, 1, 2, 0xb, 0, 0]` |
| `TM::createLifeCycles` | 0x4195c0 | Obtiene participantes vía `ObjHandover_Create` (0x41920c); crea `LifeCycle` 0x14 B en 0x41b6c0; registra en 0x419028 |
| Placeholder genérico | 0x446e60 | Reserva 0x30 B cuando `ObjHandover_Create` no halla entrada |

---

## 2. Análisis de `ObjStillRecorder_Create` (0x91391c)

```asm
ObjStillRecorder_Create:
  push {r4, r5, r7, lr}
  mov.w r0, #0x148          ; tamaño de asignación
  blx _Znwj@plt             ; operator new(0x148)
  mov r4, r0                ; this → r4
  bl 0x9178f0               ; Constructor ObjStillRecorder
  movs r3, #0
  mov r0, r4
  str r3, [r5]              ; *out_ptr = 0 (inicial)
  pop {r4, r5, r7, pc}
```

**VERIFICADO**: La API pública crea una instancia de 0x148 bytes y delega la inicialización al constructor en 0x9178f0. La identidad de clase del **destino** (ObjId 11) queda corroborada por este constructor.

---

## 3. Análisis del constructor `ObjStillRecorder` (0x9178f0)

Puntos clave del desensamblado (Thumb-2):

```asm
0x9178f0:  ldr r2, =vtable_ObjStillRecorder  ; 0x917af4 (PC-rel)
           movs r1, #8
           push {r4, r5, r7, lr}
           sub sp, #8
           movs r3, #0x2f                     ; literal 0x2f → ObjActiveBase
           ldr r5, =offset_vtable
           add r2, pc
           mov r4, r0
           blx MWF::ObjActiveBase::ObjActiveBase(int, char const*, uint)@plt
           ; ... instala vtable en [r4]
           ; ... crea EventSender/EventReceiver (3×)
           ; ... crea ObjPin (3×) con ConnectPinWrapper
           ; ... CapIdWrapper, UpMWrapper, SetWaitTime, StartThread
```

**VERIFICADO**:
- Inicializa `MWF::ObjActiveBase` con el literal `0x2f` (identificador de clase interno MWF).
- Instala su vtable.
- Crea tres pares `EventSender`/`EventReceiver`/`ObjPin` envueltos en `ConnectPinWrapper` (offsets 0x58/0x5c/0x60, 0x68/0x6c/0x70, 0x78/0x7c/0x80, 0x84).
- No escribe ningún `ObjId` numérico (0x35/53) en el objeto.

---

## 4. Topología fila 0xb4 — ObjId 53 como origen

**Volcado little-endian** (`.rodata` base 0xbc9598, tabla en 0xcc4210):

```
Offset 0xcc5890 (fila 0xb4 = 180 × 0x20):
  dword0: 0x00000000  ; pin_type / reserved
  dword1: 0x00000006  ; sts_id = 6
  dword2: 0x00000035  ; src_obj = 53 (0x35)
  dword3: 0x00000001  ; src_dir = 1 (out), src_no = 2 (bit-field packing)
  dword4: 0x00000002  ; dst_dir = 0 (in), dst_no = 0
  dword5: 0x0000000B  ; dst_obj = 11 (0x0b = StillRecorder)
  dword6: 0x00000000
  dword7: 0x00000000
```

Interpretación (corregida según `s20-s19-corrections.md` C1):

- **Origen**: ObjId 53, pin de salida 2
- **Destino**: ObjId 11 (StillRecorder), pin de entrada 0
- **StsId**: 6 (compartido con topología 0x2a)

**INFERENCIA**: El destino (ObjId 11) es la instancia topológica de `ObjStillRecorder` (clase corroborada por constructor real). ObjId 53 es el **objeto origen**; su clase real **no se recuperó**.

---

## 5. Búsqueda de mecanismos de registro de ObjId 53

### 5.1 `.init_array` (263 entradas `R_ARM_RELATIVE`)

- **VERIFICADO**: `readelf -SW/-rW` confirma 263 entradas relativas; ninguna apunta al rango `0x913900..0x913966` (`ObjStillRecorder_*`).

### 5.2 Punteros directos en secciones asignables

- **VERIFICADO**: Escaneo de palabras little-endian en `.data.rel.ro`, `.data`, `.bss` no halla punteros a `ObjStillRecorder_Create` ni a las 5 APIs exportadas `ObjStillRecorder_*`. Solo aparecen sus propias entradas `.dynsym`.

### 5.3 `TM::createLifeCycles` / `ObjHandover_Create` (0x41920c)

- **VERIFICADO**: `TM::createLifeCycles` (0x4195c0) llama a `ObjHandover_Create` (0x41920c) para obtener dos participantes.
- Cuando la entrada no existe, `ObjHandover_Create` reserva **0x30 B** y construye un **placeholder genérico** en **0x446e60** (no específico de ObjId 53).
- Luego crea `LifeCycle` (0x14 B) en 0x41b6c0 y lo registra en 0x419028.
- **DESCARTADO**: 0x41920c no es constructor de ObjId ni factoría estática por ID; solo busca entrada existente y crea placeholder genérico.

### 5.4 Literal `0x35` en código

- **VERIFICADO**: El literal `0x35` en 0x4172d6 pertenece a rutina de diagnóstico de `ObjStatusViewer` (estado ≠ 1), **no** identifica ObjId 53.

### 5.5 Modelo PbCap como creador literal de topología 0x2a

- **VERIFICADO** (sesión 16): Único creador literal de topología 0x2a es `ModelPbCap`.
- Topología 0x2a conecta Camera.out0 → Effect.in0 (misma semántica estructura que 0xb4).
- **INFERENCIA**: El registro de ObjId 53 puede ser **indirecto/externo** vía `ModelPbCap` u otra factoría que instancie el objeto origen antes de crear la topología 0xb4.

---

## 6. Evidencia REA / Desensamblado

| Hallazgo | Dirección | Método | Estado |
|---|---|---|---|
| `ObjStillRecorder_Create` reserva 0x148 B, llama ctor 0x9178f0 | 0x91391c | `llvm-objdump` | VERIFICADO |
| Constructor inicializa `ObjActiveBase(0x2f)`, vtable, 3× `ObjPin`+`ConnectPinWrapper` | 0x9178f0..0x917a68 | `llvm-objdump` | VERIFICADO |
| Fila 0xb4 = `[0,6,0x35,1,2,0xb,0,0]` | `.rodata` 0xcc5890 | `readelf -x .rodata` | VERIFICADO |
| `.init_array` 263 entradas, ninguna para `ObjStillRecorder_*` | `.init_array` 0xfd25a4..0xfd29bf | `readelf -SW/-rW` | VERIFICADO |
| Sin punteros a APIs `ObjStillRecorder_*` en datos asignables | `.data.rel.ro`, `.data`, `.bss` | Escaneo little-endian | VERIFICADO |
| `ObjHandover_Create` (0x41920c) crea placeholder 0x30 B en 0x446e60 | 0x41920c..0x4192e4 | `llvm-objdump` | VERIFICADO |
| Literal `0x35` en 0x4172d6 no es ObjId 53 | 0x4172d6 | `llvm-objdump` + flujo | VERIFICADO |
| Clase real de ObjId 53 (constructor/registro) | — | Búsqueda exhaustiva | **NO_VERIFICADO** |

---

## 7. Conclusiones y clasificación

| Categoría | Hallazgo |
|---|---|
| **VERIFICADO** | `ObjStillRecorder_Create`/`ctor` existen y construyen ObjId 11 (StillRecorder). |
| **VERIFICADO** | Fila 0xb4 conecta ObjId 53 (origen, out2) → ObjId 11 (destino, in0), StsId=6. |
| **VERIFICADO** | No hay auto-registro directo en `.init_array`, datos asignables, ni literal `0x35` como ID de clase. |
| **INFERENCIA** | El registro de ObjId 53 es **indirecto/externo** (posible vía `ModelPbCap` u otra factoría que cree el objeto origen antes de instanciar topología 0xb4). |
| **NO_VERIFICADO** | Clase C++ concreta de ObjId 53, su constructor, y el sitio que asocia el entero 53 a dicha clase. |

---

## 8. Próximos pasos recomendados

1. **Analizar `ModelPbCapToInstance` (0x6131e9)** y su flujo de creación de topologías para ver si instancia el objeto origen (ObjId 53) antes de llamar a `createTopology(0xb4)`.
2. **Rastrear llamadas a `createTopology`** (string en 0xcc3e36 / 0xd04ca7) para localizar el sitio que crea la topología 0xb4 y ver qué objetos pasa como participantes.
3. **Buscar factoría por ObjId** en `libBizFw2.so` / `libMWF.so` / `libInfraScalarMpr.so` (bibliotecas candidatas para `Connect` según sesión 18).
4. **Verificar RTTI / vtable** del objeto creado por `ObjHandover_Create` cuando el ObjId=53 se solicita (si existe un mapa interno `obj_id → factory`).

---

## 9. Límites y advertencias

- Análisis estático, local y de sólo lectura sobre A6000 FW 3.21.
- No se modificó ningún binario, no se abrió ni eliminó proyecto Ghidra, no se conectó ni flasheó cámara.
- **Nada de este análisis declara SilentShutter funcional.**

---

*Generado: 2026-10-21 | Fuente: `libObj.so` (A6000 FW 3.21) | Herramientas: `llvm-objdump`, `readelf`, REA/Ghidra (sesión independiente)*
