# S20 — Correcciones obligatorias a documentación de sesión 19

Alcance: revisión directa por Claude (sin Codex, sin subagentes) de tres
inconsistencias señaladas al inicio de la sesión 20, contrastando los
documentos de sesión 19 contra los datos crudos ya exportados
(`analysis/topology-table-libobj.json`, `s18-main-init-437ebed8.md`,
`s19-liro-remaining-sequences.md`) y los informes mismos. No se usó Ghidra en
esta tarea: alcanzó con los exports JSON/Markdown ya producidos.

## C1 — ObjId 53 no es ObjStillRecorder

**Confirmado como error real.** La fila de topología `0x43+0xcc4210+0xb4*0x20`
(`id=180` en `analysis/topology-table-libobj.json`) decodifica como:

```
pin_type=0, sts_id=6, src_obj=53 (0x35), src_dir=1 (out), src_no=2,
dst_obj=11 (0x0b), dst_dir=0 (in), dst_no=0
```

Es decir: **ObjId 53 es el objeto ORIGEN**, **ObjId 11 (0x0b) es el objeto
DESTINO**. `ObjStillRecorder_Create`/constructor `0x9178f0` corrobora la
clase del **destino** (ObjId 11), no la de ObjId 53.

`docs/capture/s19-objid53-registration.md` (S19-03) decía en su "Estado" e
INFERENCIA: *"La clase del extremo identificado como ObjId 53 ... queda
corroborada como ObjStillRecorder"* / *"El ObjId 53 ... es la instancia
topológica de la clase ObjStillRecorder"*. Esto conflactaba el objeto origen
(53) con la clase del objeto destino (11). El propio diagrama ASCII del mismo
documento (`ObjId 53.out2 ──> ObjStillRecorder.in0`) ya mostraba la dirección
correcta, pero el texto en prosa no era consistente con su propia tabla.

Las menciones en sesiones 16/18 (`s16-claude-effect-control.md`,
`s18-claude-d-topology.md`, `silent-architecture-comparison.md`,
`RESEARCH_TASKS.md:67`) usan la forma "objeto 53 → StillRecorder", que es
direccionalmente correcta (origen→destino) y no requiere corrección.

**Corregido:** `docs/capture/s19-objid53-registration.md` (Estado + fila
INFERENCIA), reescritos para que ObjId 53 quede explícitamente como objeto
origen de clase NO_VERIFICADA, y ObjId 11 como el destino cuya clase
(`ObjStillRecorder`) sí está corroborada.

**No se reconstruyó la clase real de ObjId 53** en esta tarea — eso sigue
siendo NO_VERIFICADO, igual que antes de la corrección. Solo se corrigió la
atribución errónea, no se cerró el bloqueo original de sesión 19.

## C2 — La tabla `0x43edccf8` SÍ es recuperable estáticamente

**Confirmado como contradicción real entre S19-07 y S19-12.**

- `docs/capture/s18-main-init-437ebed8.md` §1/§3 (sesión 18, VERIFICADO)
  demuestra que `DAT_44022934` — el slot GOT que apunta al selector de
  captura `0x437eabfc`/tabla `0x43edccf8` — es poblado por el inicializador
  `0x437ebed8`, que resuelve sus 15 filas (`0x0`..`0x118`, paso `0x14`) a
  punteros Thumb reales y contiguos (`0x43b1bc0d`..`0x43b1c097`).
- `docs/capture/s19-liro-remaining-sequences.md` (S19-07, VERIFICADO)
  decompiló las diez filas no seleccionadas por sesión 18 usando exactamente
  esas direcciones Thumb resueltas, y confirmó que son máquinas de estados
  reales (`FUN_43afdf16` + `tbb`), no trampolines.
- `docs/capture/s19-mechanical-shutter-decision-points.md` (S19-12) afirmaba
  en cambio: *"La tabla/filas no son recuperables desde la imagen estática"* —
  esto contradice directamente la evidencia de sesión 18 y S19-07 ya citada en
  el propio proyecto.

La confusión real: los *bytes en reposo* de la tabla en `.bss`
(`0x43edccf8`) sí son cero en la imagen estática — eso es cierto. Pero "cero
en BSS antes de inicializar" no equivale a "no reconstruible estáticamente":
el contenido se reconstruye leyendo el inicializador `0x437ebed8` y
resolviendo los descriptores GOT que usa, los cuales viven en secciones
estáticas de solo lectura. Esta distinción (tabla BSS vacía vs. contenido
reconstruible vía inicializador+GOT) ya estaba establecida en sesión 18 y
S19-12 la perdió.

**Corregido:** `docs/capture/s19-mechanical-shutter-decision-points.md`, fila
de la tabla `0x437eabfc`/`0x43edccf8` y párrafo de "Veredicto", con referencia
cruzada a `s18-main-init-437ebed8.md` y `s19-liro-remaining-sequences.md`. Lo
que sigue genuinamente NO_VERIFICADO (y no se corrigió porque sigue siendo
cierto) es la correspondencia fila→primer comando CAIF/Darwin.

## C3 — Modos 2/4/5 de ObjEffect: error inválidos solo en un dispatcher concreto

**Confirmado como generalización excesiva, pero NO en el informe fuente
S19-11** (`docs/capture/s19-objeffect-modes-2-5.md`), que ya scopeaba
correctamente cada hallazgo como *"DESCARTADO para este recorrido"* y
dedicaba una sección completa de "Límites y descartes" a advertir contra la
generalización. La pérdida de matiz ocurrió al condensar S19-11 en los
documentos centrales:

- `docs/capture/RESEARCH_TASKS.md:149` decía *"el rango efectivo del
  dispatcher ObjEffect es 2–5 ... 2/4/5 toman error"* sin acotar que esto
  aplica solo al dispatcher `0x176294`/filtro `0x176cc6` examinado, dando la
  impresión de una conclusión general sobre todo ObjEffect.
- `CONTEXT.md:999` tenía la misma formulación sin el calificador de alcance.

El propio S19-11 identificó un **dispatcher y filtro concretos** (`0x176cc6`
resta 2 y acepta `<=3`; solo el valor 3 pasa el segundo filtro en `0x176294`);
no analizó todos los dispatchers/secuencias posibles de ObjEffect, por lo que
no se puede afirmar que los modos 2/4/5 sean inválidos en **toda** ruta
ObjEffect — solo en la que efectivamente se inspeccionó.

**Corregido:** `docs/capture/RESEARCH_TASKS.md:149` y `CONTEXT.md:999`,
añadiendo el calificador de alcance ("en este dispatcher/recorrido
concreto") y remitiendo a esta corrección. `s19-objeffect-modes-2-5.md` no
requirió cambios: ya estaba correctamente acotado.

## Resumen de archivos modificados

| Archivo | Cambio |
|---|---|
| `docs/capture/s19-objid53-registration.md` | C1: Estado + fila INFERENCIA reescritos (origen/destino correctos) |
| `docs/capture/s19-mechanical-shutter-decision-points.md` | C2: fila de tabla + párrafo de veredicto corregidos |
| `docs/capture/RESEARCH_TASKS.md` | C3: línea de resumen S19-11 acotada |
| `CONTEXT.md` | C3: línea de resumen S19-11 acotada |

Ningún binario original fue modificado. No se usó Codex ni subagentes en esta
tarea. SilentShutter no se declara funcional.
