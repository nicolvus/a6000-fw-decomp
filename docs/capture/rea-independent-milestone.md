# Hito REA independiente (Línea B) — 2026-10-19

Informe único. Línea A = Ghidra histórico (S1–S48 parcial, intacto). Línea B = REA 6.5.0 + Ghidra 12.1.4
(proveedor `ghidra`, proyecto temporal `-readOnly -deleteProject`, nunca el persistente).
Artefactos: `analysis/rea-independent/` (guiones en `bin/`, salidas en `out/`, manifiestos en `manifests/`,
pre-registro en `PREREGISTRO-av-cam.md`). Clasificación: VERIFICADO / PARCIAL / INFERENCIA / NO_VERIFICADO;
procedencia entre corchetes. **Aviso de independencia:** REA usa Ghidra; el acuerdo A↔B en
desensamblado prueba coherencia de configuración, no un segundo motor. El único decodificador realmente
independiente usado es LLVM (`llvm-objdump` 23.1.1) y una búsqueda de bytes propia en Python.

## 1. Preparación de REA
- Paquete local `tools/rea` (rea-agents 6.5.0), `scripts/rea` fija `GHIDRA_INSTALL_DIR`=`tools/providers/ghidra_12.1.4_PUBLIC`
  y JDK 21.0.12. MCP `rea mcp` inicializa y expone **207 herramientas** (`out/tools-list.json`).
  Las herramientas REA no están registradas en esta sesión de Claude; se usaron por un cliente MCP stdio mínimo
  propio (`bin/mcpc.py`), sin modificar REA.
- Arranque: `DEFAULT_GHIDRA_STARTUP_TIMEOUT_MS = 330000` (código `providerStartupTimeout`); **`REA_GHIDRA_STARTUP_TIMEOUT_MS`
  está soportada** (entero positivo, máx. 2147483647). Heap por defecto `-Xmx2G`; `GHIDRA_MAXMEM` lo cambia (se usó 3G).
- ARM/Thumb: `raw-binary`+`arm` → `ARM:LE:32:v7` (admite Thumb). REA documenta como no soportados Thumb-only/Cortex-M.
  No hay herramienta REA para crear funciones Thumb; solo `REA_GHIDRA_SEED_FILE` (requiere reabrir en frío; no usado).
- Issue [morluto/rea#1048](https://github.com/morluto/rea/issues/1048): abierta, PR #2150 sin fusionar. Cada sesión importa a un proyecto
  temporal; **un snapshot cachea resultados, no una base Ghidra analizada**. No existe reutilización de proyecto persistente en 6.5.0.
  Confirmado empíricamente: cerrar la sesión pierde el análisis (coste de reabrir ≈ el original).

## 2. Experimento 1 — `libmprctrl.so` (SHA `514e1411…011d`, ELF ARM, copia 0444 en `input/`)
| Operación | Tiempo |
|---|---|
| `open_binary` | 0,01–0,05 s |
| Primera consulta (autoanálisis completo, 1219 procedimientos: 153 externos/1066 internos) | 21,6–22,3 s |
| `analyze_function`, `procedure_assembly`, `read_bytes`, `address_to_file_offset`, `resolve_native_call_targets` | 0,0–0,3 s |
| `trace_native_values` (8 funciones) | 0,01–1,04 s |
| `procedure_references` / `get_call_graph` (8×2 direcciones) | 0,0–0,07 s |
Herramientas usadas: `binary_session`, `open_binary`, `binary_overview`, `list_procedures`, `batch_decompile`, `analyze_function`,
`procedure_references`, `get_call_graph`, `procedure_assembly`, `trace_native_values`, `resolve_native_call_targets`,
`address_to_file_offset`, `read_bytes`, `inspect_native_load_image`. 16 llamadas iniciales fallaron por mis valores de
`direction` (REA exige `incoming|outgoing` y `forward|backward`); repetidas bien (`out/exp1c.jsonl`).

Funciones (8): `DmmAccessPLA::GetExtListTop/GetUnitHandle/GetExtSizeFromDmmAlloc/SetExtListPackStatus`,
`DmmAccess::AllocDmmMemory/DmmCloseAndFree/DmmAllocateNEWAndOpen_body`, `MprCtrlMcmd::CtrlAllocDmmMemory`
(direcciones REA = vaddr+0x10000, base idéntica a `s37-library.json`). Comparación en `out/exp1-comparison.json`, `out/exp1-bytes-check.json`.
- **VERIFICADO** [A+B+LLVM]: bytes devueltos por REA == archivo; `file_offset = dirección − 0x10000` (8/8). Mismo nombre y mismo
  nº de instrucciones (4,6,5,7,53,12,331,27) que el export S37; listado idéntico en 7/8 y en el 8º solo difiere el render de 2
  instrucciones (`ldr.w r8,[r5,r3]` sin corchetes en REA). LLVM coincide en direcciones de instrucción en 7/8.
- **Diferencia explicada** (`DmmAllocateNEWAndOpen_body`, LLVM 65 vs 331 instrucciones): el cuerpo tiene `tbb [pc,r3]`;
  Ghidra/REA tratan la tabla como datos (3 rangos no contiguos), el barrido lineal de LLVM la decodifica como código. Limitación del barrido
  lineal, no de REA.
- **Diferencia real (decompilador)**: `DmmCloseAndFree` (0x2afe8, 32 B) acaba en `b.w 0x1fca0` (thunk → `DmmCloseORFree_body` 0x2ada8).
  REA decompila el cuerpo del destino insertado (OSAL `0x61003c`, mensaje de `0x18` bytes, id 4, `unitHandle`) y `analyze_function`
  no lista ese salto como callee (solo `SetUnitHandleLog`). El export S37 muestra solo el envoltorio. Mismos datos, distinta presentación.
  **PARCIAL**: constantes `0x61003c`/`0x18` coinciden con la conclusión S37 (mismo motor).
- **Limitaciones de herramienta**: `resolve_native_call_targets` sobre una entrada de función devuelve `not-call`
  (espera un call site); `trace_native_values` devuelve nodos p-code en `normalized_result` (`raw_result` nulo).
- **Información nueva**: ninguna de comportamiento; solo tiempos y los puntos anteriores.

## 3. Experimento 2 — `av-cam.bin` (SHA `b60c845c…6bb9`, 11 427 236 B)
Presupuesto registrado antes (`PREREGISTRO-av-cam.md`): 15 min de arranque, 30 min total, tope RSS 3,8 GB. Parámetros:
`open_binary format=raw-binary architecture=arm entry_point=0x43541000 provider_id=ghidra`,
`REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=3G`, sin seeds.
- **Intento 1 (guion):** análisis completo en **458,8 s** (<900 s; el límite por defecto de 330 s explica el fallo previo); duración total 470 s;
  pico RSS 2314 MB (`logs/exp2-resources.csv`). Sesión cerrada al terminar el guion.
- **Intento 2 (demonio de sesión `bin/session_daemon.py`, enmienda 1):** listo a los 485,7 s; sesión abierta durante las consultas;
  `export_evidence_bundle` (1020 registros, 247 628 501 B; guardado como `.gz` 13,4 MB, SHA del JSON `270dec5a…6c10`). Único reintento del autoanálisis.
- Reloj total 13:44:39–14:06:49 (22,2 min) dentro del presupuesto. 42 006 procedimientos, 21 186 cadenas.
- **Verificaciones previas VERIFICADO** [B]: SHA original coincide; un único bloque `ram` 0x43541000–0x44026da3, longitud = tamaño del archivo,
  `file_offset 0`; `ARM:LE:32:v7`; `read_bytes` == archivo y `file_offset = dir − 0x43541000` en 12/12 direcciones consultadas.
- **Direcciones vs proyecto histórico:** de **464** entradas de funciones exportadas por Línea A (`analysis/ghidra/s*.json` con este SHA),
  REA encontró **363 exactas (78,2 %)**, 9 dentro de otra función (p. ej. 0x436397a0 en 0x436396b0) y **92 no encontradas (19,8 %)**.
  Faltan las entradas Thumb que Línea A sembró a mano: 0x43789cc0, 0x43789708, 0x437da100, 0x43792f9c, 0x43794096, 0x43ae90ce
  (`inspect_native_instruction` → *undecodable*); 0x437dad78 sí decodifica en Thumb (`push {r3,r4,r5,lr}`) pero no es función.
  No usar consultas vacías de REA como ausencia (confirma el README previo). **VERIFICADO.**
- **Contenido de las 363 coincidentes** (357 con respuesta; 6 superan el presupuesto de respuesta stdio): 234 tenían listado histórico →
  **234/234 con la misma secuencia de direcciones y mismo texto** tras ignorar `[ ] !` (217 idénticas sin normalizar).
  38 708 instrucciones: LLVM decodifica en **todas** las direcciones REA, mnemónico igual en 38 281 (98,9 %; resto sin clasificar, probablemente alias/sufijos). **VERIFICADO** (listado) / NO_VERIFICADO (el 1,1 %).
- **Thumb/ARM:** REA decodifica en Thumb exactamente donde Línea A (234/234) y LLVM-Thumb coincide en todas las direcciones; se verificó por bytes, no por avisos del decompilador.
- **Decompilador:** media de similitud de tokens (`FUN_`/`DAT_`/constantes) 0,60; idéntico en 72/234. Causa documentada en un caso y medida:
  Línea A pliega literales a `_DAT_f3c3xxxx` (19/234 funciones), REA nunca (0/234), muestra `DAT_436cd2c0 + 0x114`. El literal en 0x436cd2c0 es
  `0xf3c30000` (leído del binario): mismo comportamiento, distinta presentación (REA marca el bloque `ram` como rwx; Línea A lo plegó).
  El resto de diferencias de pseudocódigo **no se clasificó** (NO_VERIFICADO).
- **Qué se puede conservar:** bundle de evidencia (resultados de consultas, `.gz` aquí) y snapshots (reproducen consultas ya hechas sin Ghidra; nuevas consultas
  reimportan). **Hay que repetir** el autoanálisis (~8 min) en cada sesión nueva; el bundle no es una base Ghidra abrible.

## 4. Obturador electrónico — evidencia B acotada (VD base `0xf3120000`, base temporizador `0xf3c30000`)
Método independiente: `search_bytes` (cobertura completa 11,4 MB) del literal LE de cada base → `xrefs` → `resolve_containing_procedure`.
- 20 coincidencias de `0xf3120000` (19 alineadas + 1 no alineada en 0x4368147e) y 16 de `0xf3c30000`; la búsqueda alineada en Python da el mismo conjunto. **VERIFICADO** [B+Python].
- 88 instrucciones cargan esos literales, en **25 funciones** (15 con VD, 10 con temporizador) + 6 instrucciones sin función contenedora (código no descubierto).
- Coincide con lo conocido: 0x436c6f3c, 0x436c7950, 0x436c74c8, 0x436c5d2c (S45/S46), 0x43ad6006 (S34). No aparecen en ningún `.md` de investigación:
  0x436c5b28, 0x436c6288, 0x436c6294, 0x436c7490, 0x436c72f4 (los 4 primeros usan literales verificados: 0xf3120000 en 0x436c5bb0/6290/629c/74c0).
  - 0x436c6288/0x436c6294: setters de 6 B que escriben `[0xf3120000+0x48]`/`+0x4c`. **PARCIAL** (semántica del registro NO_VERIFICADO).
  - 0x436c5b28: según `param+0x8c` llama `FUN_43ad2b1a/2ade(base,0,1,1,0,0,0)` o `(…0,0,0,1,1,1)` y fija `param+0x94=1`. **INFERENCIA**: configura habilitaciones por canal del bloque VD.
  - 0x436c7490: negación de `param+0x3c` hacia `FUN_43ad3870/3842` con bases 0xf3120000 y 0xf3100000 y 0xf3000000. **INFERENCIA.**
- **Conclusión sobre el problema principal:** *sin evidencia nueva* de inicio/fin electrónico de exposición independiente de cortinas. Lo anterior son accesos al
  controlador VD; no se muestra relación con cortinas ni se declara modalidad totalmente electrónica. **NO_VERIFICADO.**

## 5. Resumen
- Herramientas MCP efectivas: `binary_session, open_binary, binary_overview, list_procedures, list_segments, inspect_native_load_image, batch_decompile, analyze_function,
  procedure_references, get_call_graph, procedure_assembly, trace_native_values, resolve_native_call_targets, address_to_file_offset, read_bytes,
  resolve_containing_procedure, inspect_native_instruction, search_bytes, xrefs, export_evidence_bundle`.
- Limitaciones de respuesta: `list_procedures` (42 006) y 6 `analyze_function` grandes superan el presupuesto stdio (error `resource_constraint`, conexión usable).
- Hallazgo nuevo con valor práctico: REA/Ghidra completa av-cam en ~8 min si se amplía el arranque; la cobertura de entradas es 78 % sin seeds.

## 6. Recomendación de uso futuro
1. Bibliotecas ELF pequeñas: REA directo (~25 s en frío).
2. `av-cam.bin`: demonio de sesión (`bin/session_daemon.py` + `bin/q.py`) con `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=3G`; abrir una sola vez por sesión (~8 min) y volcar consultas por lotes.
3. Para funciones Thumb no descubiertas, Línea A sigue siendo la referencia; un único experimento futuro con `REA_GHIDRA_SEED_FILE` (reabre en frío) permitiría comparar cobertura, sacrificando independencia parcial.
4. Evitar `list_procedures`/`analyze_function` masivos sin paginar; usar `search_procedures` y `resolve_containing_procedure`.

## 7. Integridad final
- `analysis/ghidra` (1328 archivos), `silent-liro.gpr/.rep` (9 archivos) y los 5 SHA de firmware: manifiestos inicial y final **idénticos** (`manifests/*.initial|final.sha256`).
- Firmware original intacto (SHA de `av-cam.bin` y `libmprctrl.so` coinciden con `firmware/hashes/sha256.json`). Experimentos en `analysis/rea-independent/`, entradas como copias 0444.
- Sin procesos Ghidra/Java/REA propios al cerrar. Tres procesos `rea mcp` de otra sesión (desde 10:55) ya no existían al final; no los toqué.
- Los `.md` previos solo se tocaron para añadir (`CURRENT.md`, `PROGRESS.md`): copias previas en `manifests/pre-edit/`.
- Límite: no hay `.git`, así que la integridad se afirma por SHA-256, no por historial de versiones.
