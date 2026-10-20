# Sesión 16 (Claude, hilo principal, sin subagentes) — Escritor del modo 1, auditoría de topología y exclusión interna de ObjEffect

Alcance: análisis estático exclusivo de `libObj.so` fw 3.21 (Sony A6000). **No se afirma que SilentShutter funcione.** No hay cámara conectada, no se flashea nada. Direcciones **ELF** salvo que se indique "Ghidra VA" (= ELF + 0x10000). Herramientas usadas directamente por mí (sin delegar a ningún agente ni subagente): `llvm-objdump -d --triple=thumbv7-linux-gnueabi` sobre todo `.text` de `libObj.so` (0xe2b70–0xbc9598, ~11 MB desensamblados a un único archivo), `scripts/libobj_dec.sh` (Ghidra headless, `DecompAt.java`, proyecto local `analysis/ghidra/a6000-libs`), y Python 3 (`-I`) para los cálculos sobre la tabla de topología y los barridos de patrones en el desensamblado.

Continúo directamente el trabajo de sesión 15 (`docs/capture/branch-claude-objeffect.md`, `docs/capture/liveview-encodestill-parallel-verdict.md`, `analysis/branch-claude-effect-states.json`, `analysis/yc-pin-delivery-flow.json`), que dejó tres bloqueos explícitos: (1) ningún escritor localizado de `EffectInternalMode=1`; (2) 318 sitios de `createTopology`/`destroyTopology` revisados solo parcialmente; (3) sin verificar si ObjEffect impone una exclusión interna entre su entrada de Camera y su salida al Recorder.

**Confirmo que no delegué ningún trabajo a otro agente ni subagente en esta sesión** (restricción explícita del encargo). Todo el desensamblado, los scripts de extracción de patrones y las decompilaciones se ejecutaron directamente con Bash/Read/Write/Edit y el script `scripts/libobj_dec.sh` desde este mismo hilo.

---

## A1 — Escritor de `EffectInternalMode=1`

### Corrección respecto a sesión 15

Sesión 15 revisó los 20 sitios de llamada directa (`bl`) al setter genérico `0x140144` en todo el binario, pero **descartó 19 de los 20 por estar "fuera del rango estimado de ObjEffect" (0x15e000–0x1e9900) sin decompilarlos**, concluyendo "NO_VERIFICADO (no localizado)".

Esta sesión re-desensambló `.text` completo de forma independiente, recuperó los mismos 20 sitios (cifra verificada de nuevo: exactamente 20 `bl 0x140144` reales en todo el binario), y en vez de descartar por rango de dirección, **decompilé con Ghidra las 6 funciones contenedoras de los sitios con valor literal de interés** (`push`-entry localizado por retroceso en el desensamblado, función creada en esa dirección exacta con `createFunction`). El resultado contradice la conclusión de sesión 15.

### Hallazgo principal — VERIFICADO

Existen **dos escritores dinámicos** de `EffectInternalMode=1`, identificados sin ambigüedad porque cada uno está registrado en una vtabla de `.data.rel.ro` cuyo bloque RTTI contiene el **nombre mangled real de la clase C++**, leído directamente de `.rodata` (no inferido por heurística):

| Función (ELF) | Clase RTTI real | Mecanismo | Dirección del `bl 0x140144` |
|---|---|---|---|
| `0x154990` | `OBJEFFECT::ExecCmdAppFaderEfctEndEvt` | Al finalizar un evento de fundido (fader) de la app: si un contador/estado (`GetSubState(block,0xb)`) no alcanza un umbral, escribe `EffectInternalMode=1` directamente. Si sí alcanza el umbral, en vez de escribir el modo, **encola un mensaje por el mismo gestor de pines `0xbc3208`** que usa la rama de acción de modo=1 en el parser REQ_DELIVER. | `0x154b24` |
| `0x1e069c` | `OBJEFFECT::SequencePinDeliverBase` | Dentro de la rama que atiende submensaje `0x1017` con pin `0x50==0` y `0x54==0`: si el modo actual ya es 0 (getter `0x15011c`), lo pone a 1. | `0x1e0b60` |

Verificación: en ambos casos localicé el puntero de función con bit Thumb en `.data.rel.ro` (único hit en todo el archivo, confirmado por búsqueda binaria exacta), retrocedí hasta la cabecera de bloque RTTI contigua (patrón `0x8, <ptr-a-cadena>, ...`) y leí la cadena apuntada directamente de `.rodata`: `N9OBJEFFECT25ExecCmdAppFaderEfctEndEvtE` (ELF `0xbd69fa`) y `N9OBJEFFECT22SequencePinDeliverBaseE` (ELF `0xc0c1e8`). Doble verificación: decompilado Ghidra + desensamblado crudo coinciden en ambos casos.

Además localicé **tres funciones que resetean el modo de 1 a 0** (mismo mecanismo, también identificadas por RTTI):

| Función (ELF) | Clase RTTI | Condición de reset |
|---|---|---|
| `0x1df55c` | `OBJEFFECT::SequencePinClose` | Si tipo/pin/dir == 0 y modo actual == 1, lo pone a 0. |
| `0x1e5edc` | `OBJEFFECT::SequencePinDisconnect` | Igual condición, en la secuencia de desconexión de pin. |
| `0x1ae070` | `OBJEFFECT::SequenceAppZoomCmd` (comparte vtabla con `0x1ae91c`) | Reset **incondicional** del holder si existe, dentro de un comando de zoom de la app — confirma que el campo es compartido/genérico de ObjEffect, no exclusivo de REQ_DELIVER. |

### Respuesta a la pregunta de A1

**El modo 1 SÍ tiene escritor dinámico accesible** (dos, de hecho), contrariamente a la conclusión "no localizado" de sesión 15. No es un valor de reposo sin escritor. Clasificación: **VERIFICADO** (existencia y mecanismo exacto de los dos escritores, con decompilado + desensamblado + RTTI cruzados). **NO_VERIFICADO**: no se encontró el `bl` directo que invoca estas funciones virtuales (son llamadas indirectas vía vtabla, igual que `0x173158` en sesión 15) — no pude trazar qué MSGID/evento de alto nivel las dispara, ni si son alcanzables durante disparo fotográfico/EE en vez de durante PbCap/edición/zoom de la UI. Esto es un bloqueo distinto del que planteaba sesión 15 ("no hay escritor") — ahora el bloqueo es "hay escritor, pero no se sabe si se alcanza desde EE".

Evidencia cruda completa (desensamblado y decompilados) en `research/s16-claude-effect-control/mode1_decomp.txt` y `analysis/s16-claude-effect-mode1.json`.

---

## A2 — Auditoría de `createTopology`/`destroyTopology`

### Método (reproducible, documentado en detalle en `analysis/s16-claude-topology-audit.json`)

Localicé los dos wrappers reales por desensamblado directo: `0x420630` (createTopology, reordena argumentos y salta a `0x41a26c`) y `0x420656` (destroyTopology, salta a `0x41a3b8`). Conté **213 sitios totales** (`93` create + `120` destroy) con `bl` directo a estos dos wrappers en todo el binario — **no 318** como cita sesión 15; no pude determinar la causa exacta de la discrepancia en el tiempo disponible (posible inclusión de llamadas indirectas o de los thunks vecinos `0x41ac24`/`0x41a7a4` en el conteo anterior). Lo declaro como discrepancia **no resuelta**, no como corrección.

Para cada sitio, el ID de fila de topología no va en un registro directo sino en el campo `+4` de un struct pasado por referencia (confirmado contra el sitio ya conocido de `ModelPbCap`, ELF `0x613680–0x613694`: `movs r3,#0x2a; str r3,[r6,#4]; ...; bl 0x420630`). Escribí un script Python que busca este patrón (inmediato → store en `+4`) en una ventana de 50 instrucciones antes de cada llamada.

### Resultados

- **(1) Modelos que crean la fila `0x2a`**: de los 213 sitios, **solo uno** tiene el id `0x2a` como literal resuelto: el ya conocido `ModelPbCap` (`0x613694`). Re-confirmado byte a byte. **No se encontró ningún otro modelo** que cree `0x2a` por esta vía. Clasificación: NO_VERIFICADO que exista otro (no descartado), porque el 82 % de los sitios de create (76/93) no resolvieron id literal por este método.
- **(2) Construcción dinámica de listas**: **VERIFICADO** — la mayoría de los sitios (76/93 create, 116/120 destroy) construyen el struct desde un registro cuyo valor no es un literal visible en la ventana de búsqueda: en create, muchos usan `new[]` con un campo llenado desde un registro externo a la función; en destroy, lo habitual es que se pase un **handle ya almacenado** en un campo de instancia (ej. `*(this+0x94)`), no un id crudo — es decir, destroyTopology normalmente no repite el id, reutiliza el handle devuelto por el create correspondiente.
- **(3) Combinación `0x0a`+`0x07`+`0x2a` en la misma secuencia**: **NO_VERIFICADO** — ninguno de los 17 sitios con id literal resuelto usa `0x0a` o `0x07`; los literales encontrados fueron `{0:6, 1:6, 2:1, 6:1, 0x2a:1}`. No pude confirmar ni descartar la combinación.
- **(4) Transiciones a ModelRec/StillRec**: **NO_VERIFICADO** — ningún cluster de llamadas examinado cae cerca de símbolos `ModelMovieRec*`/`ModelStillRec*`; el cluster más grande (10 llamadas, ELF `0x65a732–0x65a9ee`) está cerca de `ModelScalarCameraPatchToInstance`, ya descartado para `0x2a` en sesión 14.
- **(5) Otros usos de `StsId=6`** — **VERIFICADO (hallazgo nuevo)**: recalculando directamente la tabla de 211 filas, existe una **segunda fila con `sts_id=6`**: la fila `0xb4` (`src_obj=53` salida#2 → `dst_obj=11` StillRecorder entrada#0 — el mismo destino que `0x2a`). Las **dos únicas** filas con `sts_id=6` en toda la tabla comparten destino. Esto refuerza que `StsId` agrupa por destino compartido (StillRecorder entrada única), y abre una hipótesis nueva — **no verificada** — de que el arbitraje real entre fuentes hacia ese pin único ocurra vía el `StsViewer` asociado a `StsId=6` (función `0x4294cc`, no decompilada esta sesión) en vez de (o además de) una exclusión interna de ObjEffect.
- **(6) Conexiones temporales crear+destruir en la misma secuencia**: identifiqué 26 clusters con ≥3 llamadas create/destroy próximas en dirección (posibles "listas de topología" de un modelo), pero no decompilé cada uno individualmente por falta de tiempo — **VERIFICADO su existencia, NO_VERIFICADO su contenido semántico**.
- **(7) Otras creaciones de `0x2a` fuera de PbCap/edición**: no encontradas por este método; mismo matiz que (1) y (3): cobertura parcial, no se puede descartar vía construcción dinámica no resuelta.

Cobertura real declarada: 213/213 sitios de llamada enumerados (100 % de los `bl` directos), pero solo 17/93 create y 4/120 destroy con id de fila resuelto a un literal (18 % y 3 %). Esto es explícitamente un barrido dirigido, no una revisión semántica exhaustiva de los 213 sitios.

Datos completos en `analysis/s16-claude-topology-audit.json`.

---

## A3 — Exclusión interna de ObjEffect entre su entrada de Camera y su salida al Recorder

Revisé el gestor de pines de ObjEffect (`0xbc3208`, `0xbc31fc`, ya citados en sesión 15 pero no decompilados) y las 7 funciones hermanas de `0x173158` en la misma vtabla de `.data.rel.ro` (`0xfef50c–0xfef590`), ninguna decompilada hasta ahora:

- `0xbc3208`: solo construye un mensaje y llama a `vtbl[8]` de `this+0x44` (el gestor de colas). **No contiene ninguna comprobación de estado de otro pin.**
- `0xbc31fc`: solo escribe un byte de flag en `this+0x108`. No encontré ningún lector de ese flag en las funciones revisadas esta sesión (no se puede descartar que exista en otra función no revisada).
- Las 7 funciones hermanas de `0x173158` (`0x171b64, 0x171b80, 0x172d78, 0x172d9c, 0x172e6c, 0x172d5c, 0x172eb0`): son constructores/destructores triviales, un setter de campo y una función "no implementada" que solo registra y devuelve `0x111`. **Ninguna contiene lógica de exclusión de pines.**

**Conclusión de A3**: no encontré, en el gestor de pines ni en la vtabla de manejadores de mensaje de ObjEffect revisada esta sesión, ningún guard que compruebe el estado del pin de entrada #0 (Camera) antes de permitir servir la salida #1 (Recorder). Esto **extiende** (no solo repite) el hallazgo de sesión 15 a nivel de TopologyManager: la ausencia de guard se confirma ahora también en dos piezas adicionales del propio ObjEffect. Sin embargo, **no es una prueba completa**: no decompilé `ObjIf::ConnectPin` (`0x41c25e`) ni `0x4294cc` (GetStsViewer, candidato real de arbitraje según el hallazgo A2.5 de la fila `0xb4`), que son los candidatos más probables para contener cualquier exclusión real.

Clasificación: **NO_VERIFICADO (ampliado); NO_DESCARTADO**. La hipótesis más prometedora para continuar no es ya "dentro de ObjEffect" sino **"dentro del StsViewer compartido por `StsId=6`"** (hallazgo A2.5), que arbitra entre ObjEffect (fila `0x2a`) y el objeto 53 desconocido (fila `0xb4`) por el mismo pin de destino.

---

## Clasificación global de esta sesión

| # | Afirmación | Clasificación |
|---|---|---|
| Existen dos escritores dinámicos de `EffectInternalMode=1`: `ExecCmdAppFaderEfctEndEvt` (0x154990) y `SequencePinDeliverBase` (0x1e069c) | VERIFICADO (decompilado + RTTI + asm cruzados) |
| Existen tres funciones que resetean modo 1→0: `SequencePinClose`, `SequencePinDisconnect`, `SequenceAppZoomCmd` | VERIFICADO |
| `EffectInternalMode` es un campo compartido/genérico reusado por secuencias no relacionadas con REQ_DELIVER (ej. zoom) | VERIFICADO |
| Alcanzabilidad de modo=1 desde EE/disparo fotográfico (vs. PbCap/UI/zoom) | NO_VERIFICADO |
| 213 sitios totales de create/destroyTopology (vs. 318 citados en sesión 15) | VERIFICADO (conteo propio) / discrepancia no resuelta |
| Único creador literal de la fila `0x2a` = ModelPbCap | VERIFICADO (re-confirmación); otros creadores NO descartados |
| Construcción dinámica (no literal) de ids de topología es mayoritaria | VERIFICADO |
| Combinación `0x0a+0x07+0x2a` en una misma secuencia | NO_VERIFICADO |
| Segunda fila con `StsId=6` (`0xb4`, objeto 53 → StillRecorder, mismo destino que `0x2a`) | VERIFICADO (cálculo directo de tabla) |
| StsViewer de `StsId=6` arbitra el acceso compartido al pin de StillRecorder | HIPÓTESIS (no verificada) |
| Gestor de pines y vtabla de mensajes de ObjEffect sin guard de exclusión Camera/Recorder | NO_VERIFICADO (ampliado, no descartado) — candidatos pendientes: `ConnectPin` (0x41c25e) y `GetStsViewer` (0x4294cc) |
| Arquitectura E (Live View → EncodeStill vía Effect) | **Sin cambio de veredicto**: ni viable ni descartada. Esta sesión añade un escritor real de modo=1 y una pista nueva (StsViewer compartido) pero no conecta ninguno de los dos con EE/disparo fotográfico. |

## Siguiente bloqueo técnico

Decompilar `ObjIf::ConnectPin` (ELF `0x41c25e`) y `GetStsViewer` (ELF `0x4294cc`) para determinar si el StsViewer compartido por `StsId=6` arbitra entre las filas `0x2a` y `0xb4`, y trazar el `bl` indirecto (vía vtabla) que invoca `ExecCmdAppFaderEfctEndEvt` y `SequencePinDeliverBase` para saber si son alcanzables fuera de PbCap/edición/zoom de UI.

## Confirmación de proceso

No lancé ningún agente ni subagente durante esta sesión. Todo el desensamblado completo de `.text`, los scripts de extracción de patrones (`research/s16-claude-effect-control/`), y las decompilaciones Ghidra se ejecutaron directamente con mis propias herramientas (Bash, Read, Write, `scripts/libobj_dec.sh`) desde este mismo hilo, sin invocar la herramienta Agent en ningún momento.
