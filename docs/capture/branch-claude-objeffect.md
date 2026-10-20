# Rama A — ObjEffect: EffectInternalMode, escritores y topología (sesión Claude)

Alcance: análisis estático de `libObj.so` fw 3.21. Direcciones **ELF** salvo que se indique "Ghidra VA" (= ELF + 0x10000). Herramienta: `scripts/libobj_dec.sh libObj.so <salida.json> 0xADDR_GHIDRA_VAt` (el sufijo `t` fuerza modo Thumb; sin él Ghidra produce `halt_baddata()` porque el código es Thumb puro). Evidencia cruda en `analysis/ghidra/branch-claude-*.json` y en `llvm-objdump -d --triple=thumbv7-linux` sobre
`firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so`.

**Corrección de direccionamiento (importante para continuar esta rama):** el wrapper `scripts/libobj_dec.sh` NO convierte direcciones ELF→Ghidra automáticamente: hay que pasarle la **dirección Ghidra VA (= ELF + 0x10000)** con sufijo `t` para Thumb (p. ej. para decompilar ELF `0x1e9880` hay que invocar `0x1f9880t`). Confirmado empíricamente: con `0x1e9880t` (ELF crudo) Ghidra falla (`halt_baddata`); con `0x1f9880t` decompila correctamente y coincide con el contexto de sesión 14. Todas las direcciones citadas abajo como "ELF 0x…" ya están convertidas de vuelta.

## 0. Estructura real de EffectInternalMode (afina sesión 14) — VERIFICADO (decompilado propio)

Sesión 14 decía "byte en el bloque 1 de this+0x14, +4". El decompilado real del parser (ELF `0x1e9880`, re-decompilado por mí con `0x1f9880t`) y de dos funciones auxiliares muestra que hay **un nivel más de indirección**:

```
this (handler YcPinCommand de ObjEffect)
 └─ +0x14 → "block" (objeto con vtable, probablemente registro de sub-estados)
      └─ block.vtable[+0x3c](block, code)  // accesor "GetSubState(code)" — código observado: 1, 4, 0x16, 0x17, 0x19
            code=1 → devuelve el "holder" de EffectInternalMode
                holder+4 (byte) = EffectInternalMode   ← getter/setter genéricos de abajo
            code=0x17 → holder cuyo valor se copia a this+0x4c ("tipo" del comando)
            code=0x19 → holder cuyo valor se copia a this+0x50 ("nº de pin")
            code=0x16 → holder que se pasa a func 0xbc31fc(valor,1) (gestor de pines)
            code=4    → holder usado en func 0x152664(valor,0) (log/assert)
```

- Getter genérico: ELF `0x14011c` (Ghidra `0x15011c`). Decompilado propio:
  ```c
  undefined1 FUN_0015011c(int param_1) {
    puVar2 = *(undefined4**)(...);      // objeto de lock global
    func_0x00150100(*puVar2);           // lock
    uVar1 = *(undefined1*)(param_1+4);  // LECTURA del byte de estado
    func_0x0015010e(*puVar2);           // unlock
    return uVar1;
  }
  ```
  Confirmado también en bruto por `llvm-objdump`: `140124 589c ldr r4,[r3,r2]; 140126 6820 ldr r0,[r4]; 140128 bl 0x140100; 140130 792d ldrb r5,[r5,#0x4]; 140132 ldr r0,[r4]; 140134 bl 0x14010e; mov r0,r5; pop`. VERIFICADO: offset **+4** del holder es el byte real. Esta función es **genérica**: tiene decenas de llamadores en módulos totalmente distintos (p. ej. `0x14e560`, `0x1918fe`, `0x19a3a0`), así que por sí sola NO identifica EffectInternalMode — identifica el *mecanismo* (clase utilitaria de estado con lock), no el campo.
- Setter genérico (inmediatamente después del getter en el binario): ELF `0x140144` (Ghidra `0x150144`). Desensamblado propio:
  ```
  140144: push {r4,r5,r6,r7,r8,lr}; sub sp,#8
  140150: mov r6,r1        ; r6 = nuevo valor (16 bits, truncado a byte)
  140152: mov r5,r0        ; r5 = holder (this)
  140154: movs r4,#0
  140156: ldr.w r8,[r3,r2] ; objeto de lock
  15c: ldr.w r0,[r8]; bl 0x140100        ; lock
  164: ldrb r1,[r5,#4]     ; valor ANTERIOR
  166: uxth r2,r6
  16a: ldr r0,[pc,#0x1c]
  170: bl 0x142420         ; callback/log de transición (old,new,0,0)
  174: strb r6,[r5,#4]     ; ESCRITURA real del nuevo valor
  176: ldr.w r0,[r8]; bl 0x14010e        ; unlock
  180: mov r0,r4(=0); pop  ; siempre devuelve 0 (éxito fijo)
  ```
  VERIFICADO por desensamblado directo: escribe `*(holder+4) = nuevo_valor` tras pasar por un callback de notificación de transición (`0x142420`, no identificado más a fondo — NO VERIFICADO su rol exacto). Solo 20 sitios de llamada en todo `libObj.so` (mucho menos que el getter), pero también es **genérico** (usado por clases muy distintas, p. ej. `0xbbf3f4`, `0xbc4556`, muy lejos del rango de ObjEffect).

## 1. Constructor que inicializa EffectInternalMode

**NO VERIFICADO en esta sesión.** No se localizó el constructor que inicializa el holder ni su valor de reposo. Los 20 llamadores del setter genérico (`0x140144`) se repasaron por dirección y solo un subconjunto (ver §2) cae dentro del rango de código de ObjEffect (`0x15e000–0x1e9900` aprox., delimitado por las direcciones ya conocidas de sesión 14: `0x15ebfc, 0x15f290, 0x15f37c, 0x15fa74, 0x15fd50, 0x17b004, 0x1e8244, 0x1e82b6, 0x1e9880, 0x1e96c0, 0x1e96f8`); ninguno de ellos tiene forma de constructor (todos son manejadores de mensaje). Pendiente para siguiente sesión: localizar la vtable de ObjEffect (candidata: la tabla de punteros a función en `.data.rel.ro` ELF `0xfef50c…0xfef590`, ver §2) y desde ahí su constructor por xrefs al `new`/`operator new` que la instala.

## 2. Escritor real localizado de EffectInternalMode — VERIFICADO (decompilado + desensamblado propios)

**Función escritora: ELF `0x173158`** (Ghidra VA `0x183158`, Thumb). Entrada real confirmada por desensamblado (prólogo `push.w {r4-r11,lr}; sub sp,#0x64; add r7,sp,#0x10; mov r5,r0` en `0x173158`; la dirección usada por error en un primer intento, `0x173368`, es un bloque intermedio de ESTA MISMA función, no un punto de entrada — Ghidra produce variables `unaff_rN` basura si se le pide decompilar ahí directamente).

Es una **función virtual**: aparece como puntero (con bit Thumb) en una tabla de `.data.rel.ro`, file-offset `0xfe754c` → vaddr ELF `0xfef54c` (verificado: `0xfef54c` contiene el word `0x173159`, es decir ELF `0x173158` con bit Thumb). La tabla circundante (`0xfef50c…0xfef590`) tiene más punteros a funciones vecinas de ObjEffect: `0x171b65, 0x171b81, 0x172d79, 0x172d9d, 0x172e6d, 0x172d5d, 0x172eb1, 0x173159`. Es decir, `0x173158` es **un manejador de mensaje más del mismo objeto** que expone el parser de REQ_DELIVER (`0x1e9880`), registrado en una vtable distinta. **NO VERIFICADO** qué MSGID concreto dispara esta vtable (no se localizó el sitio que la invoca; es indirecta).

Decompilado completo (Ghidra, `scripts/libobj_dec.sh libObj.so analysis/ghidra/branch-claude-fn173158.json 0x183158t`), resumido:

```c
undefined4 FUN_00173158(int this) {              // this = handler YcPinCommand (mismo layout que 0x1e9880)
  // obtiene, vía GetSubState(block,codigo), varios holders y los copia a campos del handler:
  holder16 = GetSubState(block, 0x16); pinmgr_0xbc31fc(holder16, 1);
  this->campo_0x4c /*tipo*/ = GetSubState(block, 0x17);
  if (this->campo_0x4c == 0) { log_error(0x62); return 1; }
  this->campo_0x50 /*pin*/  = GetSubState(block, 0x19);
  if (this->campo_0x4c == 0) { log_error(0x68); return 1; }     // (rama duplicada, código muerto)

  func_0x183ef8(this->campo_0x4c);
  v4 = GetSubState(block, 4); log_0x152664(v4, 0);

  if (leer_submensaje(this->campo_0xc, 0x1025, &sub /*1 byte*/) == 0) {
    holder_modo = GetSubState(block, 1);           // == el MISMO holder que lee/escribe el getter/setter genérico
    switch (sub) {
      case 0: nuevo_modo=2; exito=1; hay_imagen=true;  variante_campo_0x1023=2; break;
      case 1: nuevo_modo=3; exito=1; hay_imagen=true;  variante_campo_0x1023=2; break;
      case 2: nuevo_modo=4; exito=1; hay_imagen=true;  variante_campo_0x1023=0; break;
      case 3: nuevo_modo=5; exito=1; hay_imagen=true;  variante_campo_0x1023=0; break;
      case 4: nuevo_modo=7; exito=0; sin_respuesta=true; func_0x1402d8(holder_modo,1); break;
      case 5: nuevo_modo=0xe; exito=1; hay_imagen=true; variante_campo_0x1023=0; break;
      case 6: nuevo_modo=0xf; exito=1; hay_imagen=true; func_0x183a8c(this->campo_0x50); variante_campo_0x1023=0; break;
      default: nuevo_modo=0; exito=1; error_code=3; sin_respuesta=true; break;
    }
    ok = Setter_0x150144(holder_modo, nuevo_modo);   // ESCRITURA de EffectInternalMode
    if (ok != 0) { log_error(...); return 1; }
    if (hay_imagen) {
      // construye ObjMsg(0x2001,0x1011){0x1021=1,0x1022=1,0x1024=1,0x1316=3,0x1321=exito,0x1023=variante}
      pin_in0 = GetInputPin0(this->campo_0x14 /* == 0x1e8244 de sesión 14 */);
      pin_in0.vtbl[0x10](pin_in0, 0x2002, &msg);   // notifica aguas arriba (pin de entrada 0)
    } else {
      func_0x183060(this, 0xd0);                    // camino de error / sin notificación
    }
    if (error_code) func_0x182f60(this, error_code);
    return 0x111;
  }
  ...
}
```

Confirmado también en **bruto** (sin Ghidra) en el salto `tbb` de `0x1732ca`: cada caso del `switch` fija `r11` a los mismos valores (`2,4,5,7,0xe,0xf,0,3`) antes de saltar a `0x173364`, que llama `Setter(r0=holder_modo, r1=r11)` — coincide exactamente con el decompilado. Doble verificación independiente (asm crudo + Ghidra).

**Tabla de valores escritos por esta función** (según campo de mensaje `0x1025`, leído del campo `this+0xc`, el mismo mensaje `0x1011` documentado en sesión 14 como enviado por el recorder):

| `0x1025` entrante | EffectInternalMode escrito | ¿Responde con imagen (0x1011 aguas arriba)? | Extra |
|---|---|---|---|
| 0 | 2 | Sí | — |
| 1 | 3 | Sí | — |
| 2 | 4 | Sí | — |
| 3 | 5 | Sí | — |
| 4 | **7** | No (`sin_respuesta`) | `func_0x1402d8(holder,1)` |
| 5 | **0xe** (14) | Sí | — |
| 6 | **0xf** (15) | Sí | `func_0x183a8c(this+0x50)` (usa el nº de pin) |
| otro | 0 | Sí pero con `error_code=3` | — |

Clasificación: **VERIFICADO** la estructura, el switch y la escritura; **NO VERIFICADO** el significado semántico de los valores 7/0xe/0xf fuera de "no son 0..6 puros"; **NO VERIFICADO** qué dispara la llamada a esta función (no hallado el caller).

## 3. Significado de los valores 0..6 (consumidor, parser REQ_DELIVER ELF `0x1e9880`)

Re-decompilado por mí (antes solo se tenía el resumen de sesión 14); el `switch` real sobre EffectInternalMode:

```c
(**vtbl)(block,1);                 // marca "en uso" (igual accesor GetSubState(block,1))
switch (GetMode()) {                // func_0x15011c() — getter genérico ya descrito
  case 0: log(0x9d); break;                              // SOLO registro
  case 1:
    log(0xa1);
    if (submensaje_tipo(iVar4) == 0x1011) {
      log(0xa6);
      func_0xef454(iVar4, 0x3900, 0x600d);               // construye ObjMsg(0x3900,0x600d)
      func_0xbc3208(this+0x58, iVar4, this+4);           // lo encola en el gestor de pines
    }
    break;                                                 // ACCIÓN real solo si el mensaje entrante es 0x1011
  case 2: case 3: case 4: case 5:
    log(0xb4);
    r = SequencePinReqestDeliverSaveStillEditCmd(this, iVar4);  // ELF 0x1e96c0, factoría 0x17b004
    if (r != 0 && r != 0x111) return r;                    // ACCIÓN real: dispara la secuencia
    break;
  case 6: log(0xbe); break;                                // SOLO registro
  default: log(0xc2); break;                               // SOLO registro (incluye 7, 0xe, 0xf)
}
```

**VERIFICADO (decompilado propio):**
- Modos con **acción real** sobre REQ_DELIVER: **1** (encola `0x3900/0x600d`, pero solo si el submensaje recibido es exactamente `0x1011`) y **2, 3, 4, 5** (lanzan la secuencia `SequencePinReqestDeliverSaveStillEditCmd`, `0x3900/0x6013`).
- Modos **0, 6 y cualquier otro valor (incluye 7, 0xe, 0xf)**: solo registran (`BizPrintf`), sin tocar el pin de salida.
- Cruce con el escritor (§2): el escritor de `0x173158` **nunca** fija el modo a `1`; solo a `{2,3,4,5,7,0xe,0xf,0}`. Esto significa que, por esta vía, `0x1025 ∈ {0,1,2,3}` (→ modo 2,3,4,5) **sí** habilita la entrega real; `0x1025 ∈ {4,5,6}` (→ modo 7,0xe,0xf) deja a ObjEffect en un modo que el parser de REQ_DELIVER trata como "solo log" (igual que 0 y 6). El modo **1** (el único que usa la cola directa `0x600d` en vez de la secuencia) debe fijarlo **otro escritor no localizado** — NO VERIFICADO.

## 4. Live View / ModelBootEE

**NO VERIFICADO.** No se localizó ningún escritor de EffectInternalMode activado desde `ModelBootEE` (ELF `0xcdb108`, lista `{0xa,0x7}` de sesión 14) ni desde las 20 llamadas al setter genérico de las que doce caen en el rango de ObjEffect (`0x173158` y, si existieran, otras funciones de la misma familia): todas las que se identificaron pertenecen a la única función `0x173158` (el resto de direcciones del listado de 20 llamadas al setter — `0x148532,0x14e550,0x14e636,0x154b24,0x15551a,0x1ae510…0x1e6100,0xbbf3f4,0xbc4556,0xbc5856` — están fuera del rango de ObjEffect o no se pudieron atribuir por falta de tiempo). Dado que el escritor encontrado consume el campo de mensaje `0x1025` del propio `REQ_DELIVER`/`0x1011`, **no parece ser una ruta de Live View** sino parte del mismo flujo de entrega documentado en sesión 14 (PbCap). Sigue sin encontrarse relación con EE.

## 5. PbCap

**NO VERIFICADO directamente desde el código de `ModelPbCap` (`0x6135dc`/`0x613680`)**: no se encontró una llamada explícita desde esa función al setter `0x150144` ni al escritor `0x173158` (ModelPbCap opera a nivel de topología/creación de pines, no de `EffectInternalMode`). Es **plausible** (INFERENCIA, no verificada) que el mensaje `0x1011` que dispara `0x173158` sea precisamente el `ObjMsg(0x2000,0x1011)` que `ObjStillRecorder::YcPinReqDeliver` (ELF `0x90a668`, ya verificado en sesión 14) envía durante PbCap, pero no se trazó la cadena completa de despacho (vtable→MSGID) por falta de tiempo en esta sesión.

## 6. Modos que dan respuesta real a REQ_DELIVER

Confirmado en §3 con el decompilado real (no solo el resumen previo): **1, 2, 3, 4, 5**. Los modos **0 y 6** están CONFIRMADOS ahora como "solo log" por decompilado directo (antes eran inferencia de sesión 14); el **default** (que incluye 7, 0xe, 0xf, los únicos valores adicionales que el escritor puede fijar) también es "solo log".

## 7. Condiciones para el envío por el pin YC de salida nº1

No se encontró, en el propio `0x1e9880`, ninguna comprobación explícita de "pin de salida nº1" antes de las ramas de acción — el envío por ese pin concreto ocurre **dentro** de `SequencePinReqestDeliverSaveStillEditCmd` (ELF `0x1e96c0`) y de la cola `0xbc3208`, ninguna de las dos decompiladas en esta sesión (NO VERIFICADO el detalle interno). Lo que SÍ se verificó: para llegar a esas rutas se necesita (a) `EffectInternalMode ∈ {1,2,3,4,5}` y (b) para el modo 1, que el mensaje entrante tenga submensaje exactamente `0x1011` (verificado en el decompilado de §3).

## 8. Condiciones para 0x3900/0x600D vs 0x3900/0x6013

- **0x600D** (modo 1): solo si el mensaje recibido por el parser es `MSGID 0x1011` Y `EffectInternalMode == 1` en ese instante. Acción: `func_0xef454(msg,0x3900,0x600d)` + `func_0xbc3208(this+0x58, msg, this+4)` (cola directa, sin pasar por una secuencia).
- **0x6013** (modos 2–5): `EffectInternalMode ∈ {2,3,4,5}`. Acción: se delega a la factoría de secuencias `SequencePinReqestDeliverSaveStillEditCmd` (`0x1e96c0`/`0x17b004`), que internamente debe emitir `0x3900/0x6013` (verificado en sesión 14, no re-verificado aquí a nivel de instrucción).

## A. Verificación directa de las filas de topología 0x0A, 0x07 y 0x2A — VERIFICADO (cálculo reproducible)

Recalculado directamente desde `analysis/topology-table-libobj.json` (fila = `.rodata` ELF `0xcc4210 + id*0x20`, columnas `pin_type, sts_id, src_obj, src_dir, src_no, dst_obj, dst_dir, dst_no`):

| id | pin_type | sts_id | src_obj/dir/no | dst_obj/dir/no |
|---|---|---|---|---|
| `0x0a` | 0 (YC) | **0** | 8 (Camera) / out(1) / #0 | 9 (Effect) / in(0) / #0 |
| `0x07` | 0 (YC) | **0** | 9 (Effect) / out(1) / #0 | 5 (Renderer) / in(0) / #0 |
| `0x2a` | 0 (YC) | **6** | 9 (Effect) / out(1) / #1 | 11 (StillRecorder) / in(0) / #0 |

## B. StsId: mismo o distinto, y su papel — VERIFICADO (distinto) / INFERENCIA fuerte (papel)

**`0x0a` y `0x07` comparten `sts_id=0`; `0x2a` tiene `sts_id=6` (distinto).** VERIFICADO por cálculo directo de la tabla (arriba).

Papel de `sts_id`: decompilé `TM::createLifeCycles` (ELF `0x4195c0`, Ghidra `0x4295c0`) con éxito:

```c
void FUN_004295c0(undefined4 param_1) {   // param_1 = ¿id de evento/topología a crear?
  tabla = _DAT_00429700;                  // base de filas de topología (mismo layout de 8×u32)
  lock(0x14);
  n = ListSize(*tabla + 0x60);
  for (i=0;i<n;i++) {
    fila_id = ListGet(*tabla+0x60, i);
    srcLife = ObjectLifeCycle(fila[fila_id].src_obj_offset_8, param_1);
    dstLife = ObjectLifeCycle(fila[fila_id].dst_obj_offset_0x14, param_1);
    stsViewer = GetStsViewer(fila[fila_id].sts_id_offset_4);   // ELF 0x4294cc: lookup por StsId
    if (condición_evento) {
      if (srcLife==0 || dstLife==0) { log_error(...); }
      else {
        lt = new TopologyLifeCycle(0x14);
        LT::LT(lt, fila_id, srcLife, dstLife, stsViewer);      // ELF 0x42b6c0
        ...
      }
    }
  }
  unlock(0x15);
}
```

(offsets de fila confirmados por el propio decompilado: `+4`→sts_id pasa a `func_0x4294cc`, `+8`→src_obj pasa a `func_0x4294cc`... en realidad el decompilado usa `func_0x4294cc` tanto para offset`+4` como para convertir — leer con cautela: el decompilado real indexa `fila_id*0x20 + base`, luego aplica `+8` y `+0x14` a una función `0x42920c` (ObjectLifeCycle lookup) y `+4` a `0x4294cc` (StsViewer lookup). Esto coincide exactamente con las columnas documentadas en sesión 14.)

**INFERENCIA fuerte:** `sts_id` selecciona (o crea) el `StsViewer` compartido que se pasa al constructor de `TopologyLifeCycle`. Topologías con el mismo `sts_id` (aquí `0x0a` y `0x07`, ambas `0`) muy probablemente comparten o se agrupan bajo el mismo `StsViewer`/seguimiento de estado; `0x2a` (sts_id `6`) se rastrea de forma independiente. **NO VERIFICADO** si esto implica some gating de ciclo de vida (p.ej. que deban crearse/destruirse juntas) — no se decompiló `0x4294cc` ni `0x42b6c0` en esta sesión por falta de tiempo.

## C. ¿Pueden coexistir 0x0A, 0x07 y 0x2A? — INFERENCIA (estructuralmente sí; sin exclusión hallada)

**INFERENCIA (no se halló ningún guard que lo impida):** las tres filas usan **números de pin distintos** en Effect: `0x0a` es la entrada `in#0` de Effect, `0x07` es la salida `out#0`, `0x2a` es la salida `out#1`. Son tres recursos de pin diferentes (no el mismo slot), así que no hay colisión de recurso evidente en la tabla misma. No se encontró, en el código de `TopologyManager` revisado en esta sesión (`createLifeCycles`), ningún chequeo que impida activar `0x2a` mientras `0x0a`/`0x07` están activas, ni viceversa — pero tampoco se revisó el código de `connectPin`/`disconnectPin` lo suficiente para descartar un guard en otra capa (p. ej. en el propio ObjEffect, que podría rechazar `ConnectPin` en su salida nº1 si su entrada nº0 no está en un estado compatible). **NO VERIFICADO** ninguna exclusión mutua; **NO DESCARTADO** tampoco.

## D. Modelos que combinan Camera/Effect (0x0a/0x07) y StillRecorder (0x2a)

Búsqueda de nombres de modelo de disparo en las cadenas de `libObj.so`:
```
ModelContShotsPbToInstance, ModelMovieRecManualSubToInstance, ModelMovieRecToInstance,
ModelRecPbMixToInstance, ModelRecPbNeutralToInstance, ModelRecRemainInfoToInstance,
ModelStillIntervalRecToInstance, ModelStillRecToInstance
```
Estos SÍ son símbolos **exportados reales** (no solo cadenas) — confirmado con `readelf -sW`:
- `ModelStillRecToInstance` → ELF `0x69d13c`
- `ModelMovieRecToInstance` → ELF `0x5f6bbc`
- `ModelContShotsPbToInstance` → ELF `0x4fd114`
- (referencia conocida) `ModelPbCapToInstance` → ELF `0x6131e8`

**NO VERIFICADO / incompleto:** se intentó localizar la lista de topologías de `ModelStillRec` buscando llamadas a `createTopology`/`destroyTopology` (`0x420630`/`0x420656`) cerca de estas direcciones (hay 318 sitios de llamada en todo el binario a estos wrappers, demasiados para revisar uno a uno en el tiempo disponible). El único sitio cercano a `ModelStillRecToInstance` que se inspeccionó (`0x69d816`) resultó pertenecer a **otro modelo** (`ModelTouchPanel`, símbolo vecino), no a `ModelStillRec` — confirma que la proximidad de direcciones NO implica mismo modelo y que esta búsqueda requiere más tiempo del disponible. **No se pudo confirmar ni descartar** que algún modelo de disparo combine `0x2a` con `0xa`/`0x7` en la misma lista estática. Declarado explícitamente como **NO VERIFICADO**, no como DESCARTADO (a diferencia de la sesión 14, que sí pudo descartarlo para BootEE/MovieRec/ScalarCameraPatch/StillIntervalRec revisando 34 listas — esta sesión no repitió ese barrido exhaustivo).

## Resumen de clasificación

| # | Afirmación | Clasificación |
|---|---|---|
| EffectInternalMode = holder(GetSubState(block,1))+4, no this+0x14+4 directo | VERIFICADO (decompilado+asm propios) |
| Getter genérico 0x14011c, setter genérico 0x140144 | VERIFICADO (asm propio) |
| Escritor 0x173158, mapeo 0x1025→modo | VERIFICADO (decompilado+asm propios) |
| Constructor de ObjEffect / init del holder | NO VERIFICADO |
| Modos con acción real: 1,2,3,4,5; resto solo log | VERIFICADO (decompilado propio) |
| Escritor de modo=1 | NO VERIFICADO (no localizado) |
| Relación con EE/ModelBootEE | NO VERIFICADO |
| Relación con PbCap (cadena completa MSGID→0x173158) | NO VERIFICADO (plausible, INFERENCIA) |
| Filas 0x0a/0x07/0x2a y StsId 0/0/6 | VERIFICADO (cálculo directo) |
| Papel de StsId en TM::createLifeCycles | INFERENCIA fuerte (función decompilada, semántica de 0x4294cc no verificada) |
| Coexistencia 0x0a+0x07+0x2a | INFERENCIA (sin guard hallado, sin exclusión confirmada) |
| Modelo de disparo con 0xa/0x7 + 0x2a juntos | NO VERIFICADO (búsqueda incompleta) |
