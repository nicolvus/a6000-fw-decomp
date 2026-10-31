> **Archivo histórico (solo lectura).** Versión íntegra de `docs/STATE.md` anterior a la reorganización documental del 26-10-2026 (Git: `git show 93745c92:docs/STATE.md`). Los enlaces relativos se ajustaron a esta ubicación; el texto no se modificó. Vigente: [docs/STATE.md](../STATE.md).

# Estado vigente — Sony A6000 reverse engineering

## Estado vigente — 26-10-2026 (auditoría integral)

El índice maestro [PENDIENTES](../PENDIENTES.md) manda sobre los resúmenes siguientes, que son instantáneas de su fecha.
Estáticos cerrados con límite: E2–E5, E7, E8, E10 (a–c), E12, E14–E20, D1, D3, D4 y D6 ([evidencia](../capture/s403-cierre-pendientes.md));
E1 queda `NO_VERIFICADO` sin vías estáticas. Bloqueados por datos o hardware: E6, E9, E11, E13, D5; físicos F1–F6; respaldo R1–R3 (R3: historial con un binario de Sony).
Datos de auditoría y memoria temporal: [estado.json](../../knowledge/audit/estado.json) y [memoria.json](../../knowledge/audit/memoria.json)
(se regeneran con `scripts/audit/repo_audit.py`). Sin firmware ejecutado ni cámara.

## Captura: estado vigente — 25-10-2026

[Seguimiento y evidencia de los cinco puntos](../capture/capture-static-followup-2026-10-25.md):
servicio LIRO +0x3c = `sta_tsk` y transporte userland/ioctl/OSAL kernel
identificados; consumidor LIRO usa recepción bloqueante. Mapeadas 43 llamadas
de RecordStill; entrada estado2/mensaje0x10000005. S205: escritor S[0] y G→S
resueltos estáticamente. S305 original inválido por sesgo+0x58; tabla148/fila18
enlazada con Backup0x3000b, callback de copia y Backup_read. Constructor CAIF
A7S y condición del bit0x20 localizados. S176 reproducido con entregables nuevos.
Restan productor del mensaje, equivalencia de ocho parejas locales, datos
efectivos Backup, origen UI/entrega CAIF y aristas IMX210/YC/archivo/cortina.
Los 133/372 miden documentación; P1–P21 diferidas y S51 A/B/C=NO. No se
ejecutó firmware ni se validó captura física. Las secciones anteriores en fecha
son históricas; sus pendientes pueden estar superados por este bloque.

## Cobertura estática antes de pruebas físicas — 24-10-2026

[Matriz de rutas y límites REA/Unicorn](../capture/s51-static-coverage-and-tool-limits.md):
la descompilación de la cadena de disparo sigue incompleta (registro Linux de
`0x40193`, activación de RecordImage/RecordStill, productor de modo 1 y pin
`0x2a`, semántica IMX210). El censo 133/372 mide documentación, no código
recuperado. Por instrucción del usuario, ninguna prueba física hasta cerrar
la ingeniería inversa necesaria. S51 A/B/C permanece NO.

## Cola 0x40193 — 23-10-2026

[Informe vigente](../capture/queue-40193-flow-2026-10-23.md), S384 actualizado:
literales `.text` con LDR en ambos modelos, transporte de 16 B hasta OSAL y
receptor LIRO `0x4381d16c` verificados. Inicializador `0x4379e93c` instala su
puntero en descriptor `0x43ea048c` (campo+0x14=`0x46`). El inicializador ocupa
la fila 189 de una tabla contigua de 372 punteros Thumb. `0x4379e8f4`
consume el descriptor mediante `0x43b2a162 → 0x43560bb0`, que entrega
`0x46` y el descriptor a un servicio indirecto. NO_VERIFICADO: destino y efecto
de ese servicio, registro callback OSAL Linux y enlace Linux↔LIRO.
El consumidor de la **tabla de inicializadores** sí se recuperó: entrada de
cabecera LIRO `0x4354101c` → `0x4356082c` → 372 llamadas indirectas,
incluida la fila 189. No se observó ejecución real de esa entrada.
Prevalece sobre pendientes históricos; S51 sin cambios.

## Contrato RecordStill / RecordImage — actualizado 24-10-2026

[Comparación por contrato, cuerpo, cadenas y bytes](../capture/recordstill-contract-audit-2026-10-23.md): A6000 `0x90b248` es RecordImage por sus diagnósticos; antigua etiqueta C++ `RecordStill::Execute` no demostrada. Pareja A7S `0x84a568`. A7S `0x847e1c` es RecordStill, pareja A6000 `0x908afc`, llamado desde RecordImage en ambos. Los dos contenedores A6000 se delimitan con unwind/prólogos; `0x91631e` es tabla TBB. Los 25 punteros Thumb a `0x90d7e8` son `call_fn` de `StateMgr::_FuncEntry`; `StateMgr::CallFunc` ejecuta el puntero con `blx r3` en `libmprctrl.so:0x1cef2`. Activación real, equivalencia física y origen `0x40193` NO_VERIFICADO; S51 sin cambios. Prevalece sobre los resúmenes históricos siguientes.

## Auditoría 23-10-2026

[Resultados y pendientes](../auditoria-2026-10-23.md): corregidos destinos BL S382, encodings S384, direcciones de 94 trazas, 21 longitudes y censo detallado. Triaje automático reabierto; equivalencia A7S y flujo `0x40193` siguen NO_VERIFICADO. El logger dual de S607/S611/S616 está verificado estáticamente; las otras 20 fichas siguen abiertas. Las cadenas prueban presencia textual; el censo de 133/372 mide documentación de etiquetas. P1–P21 propuestas, sin nuevas pruebas físicas. Esta actualización prevalece sobre los resúmenes históricos siguientes.

Documento breve de orientación. No reemplaza las fuentes: cada afirmación enlaza al
documento canónico donde está comprobada, con su rango de líneas cuando aplica.
Para el historial íntegro de sesiones ver `docs/history/` y las correcciones completas
en [docs/CORRECTIONS.md](../CORRECTIONS.md) (generado del grafo, no editar a mano).
Para preguntas abiertas ver [docs/OPEN-QUESTIONS.md](../OPEN-QUESTIONS.md).
Para el estado operativo actualizado, ver [knowledge/CURRENT.md](../../knowledge/CURRENT.md);
para el obturador, la decisión [S51](../capture/s51-decision.md) y el
[plan de ocho pruebas físicas pendientes](../capture/physical-test-plan.md).

## Avance S300–S617 (22-10-2026) — carriles de agentes autónomos

- **B (S300–S342):** el estado IMX210 `0x43f72d02` y su equivalente A7S `0x43f7bce6` tienen gates `+3/+6` idénticos y **sin escritor** (S300/S301) → no son el mecanismo silent. La A7S tiene código de selector/tiempos ausente en la A6000 (S307–S312); el mecanismo por modo (matriz, T1/T2/T3, máscara u16, MMIO DFE/CISIF `0xfc02a00c`) existe en ambos con datos distintos (S329–S341). Corrige varias lecturas previas (bases T2/T3, `obj+0x2b4`, `w0`); `0x43fef404` no es tabla de tiempos (S342).
- **C (S401–S402):** ruta de control `SilentShutter`: handler LIRO `0x40e3` ausente en A7S; `…ForLiro` rechazado en ambos; diferencias mapeadas a P1–P8.
- **D/E (S500–S515, S600–S617):** cobertura de módulos de trazas; sin efecto en el obturador.
- Decisión [S51](../capture/s51-decision.md) sin cambios; P1–P8 siguen sin ejecutarse.

## Avance S343–S627 (23-10-2026)

Mecanismo por modo (B): idéntico en código entre A7S y A6000, la diferencia está en los datos (matriz 69/59 filas, T1/T2/T3, 34/13 modos). `libObj.so` (S380–S385): mapeado, sin efecto en S51. Cobertura de módulos al 35.75 % (133/372) por D y E. Decisión [S51](../capture/s51-decision.md) sin cambios; P1–P8 y [P13–P21](../capture/physical-test-plan-2.md) sin ejecutar.

## Avance S138–S174 (22-10-2026) — línea de RE general, controles positivos del obturador y una regla metodológica

**Línea de RE general** (catálogo con 105 hitos: [docs/capture/linea-general-re.md](../capture/linea-general-re.md)).
Hitos nuevos decodificados con bytes y tests propios: `[CAMERA_MAIN_FC]` (S138), `[CAM_UTIL_ADJ]` (S143),
`[CAM_UTIL_SENS]` (S144), `[DEPTH]` (S148), `[PANDA]` (S151), `[TP_R]` (S156), `[CAMERA_IS]` (S164),
`[JOG]` (S165), `[ADC_DEBUG]` (S166), `[SAD]` (S167), `[CAM_UTIL]`/`[CAMERA_ADJ]` (S173).

**Patrón consolidado**: en los módulos de trazas, la **etiqueta de módulo es propia de la fw3.21** pero la
**funcionalidad ya existía** en la A7S fw3.20 o el A6300 fw2.01 → la fw3.21 de la A6000 **reescribe el logging,
no el firmware** (S128/S130, con 9 ejemplos más). Casos notables: `[CAM_UTIL_ADJ]`/`[CAM_UTIL_SENS]` son **el
mismo par** (dependencia cruzada `0x43900c9c`, `0x439012fa`/`0x43901302`; id de módulo `0xb5`) y escriben
**calibración en la RAM del sensor** (51 comandos «Sens» en `0x43fe858c`); `[DEPTH]` sale a la **EXIF** (tags
`0x5001`/`0x5002`); `[TP_R]` es un **reporter** y **corrige un falso positivo de S130**; `[CAMERA_IS]` es **la
capa que aplica la estabilización** (17/17 pares PIC a mano → **valida el mapa de S70**); `[JOG]` es la **fuente
de eventos de la rueda** (el A6300 sustituye `JogVGrip` por `JogCaif`); `[ADC_DEBUG]` es el **volcado del driver
LIRO ADC** y **corrige una lectura de S164**; `[SAD]` es el **diagnóstico de la biblioteca «SA»** con la sigla
**sin base textual** (sin desarrollar).

**Controles positivos del obturador electrónico** (todos con bytes, sin ejecutar firmware):

* **S168** — la cadena `position num in rolling is strange %d` del A6300 (`0x43d9fe03`) tiene **0 referencias de
  código** (regla estricta, punteros absolutos, pares `movw`/`movt` y un método inverso independiente) → **cadena
  muerta**; de las 5 de su banda, 4 sí lo están (el único código vivo es el cálculo de ancho del **número de
  posición del VD**, `0x4372914c`). **Corrige** el colateral de S164.
* **S169** — el A6300 tiene una **capa de validación de parámetros de cámara** (`LiroSeq`) con **201** propiedades
  `CheckSet*` y **370** comprobaciones, con parámetros de obturador `sc_ShutDrive` (`+0x1dd`), `uc_ShutDriveMode`
  (`+0x1dc`), **`front_eshutter`** (`+0x23c`), **`SilentShutterMode`** (`+0x264`), **`shutterType`** (`+0x268`),
  `ul_ShutLowLimit`, `sc_IrisDrive`, `uc_IrisDriveMode`, `sc_ExposureDrive`. **La A6000 fw3.21 y la A7S fw3.20
  tienen 0/0 de todo eso** → **falta el parámetro, no solo la traza**. Refuerza S135 con evidencia de **parámetros
  en runtime**.
* **S171** — la API del imager del A6300 tiene **7** entradas y las de la A6000/A7S **4** (`GetImagerStabilizationTime`
  viva en `0x43718d04`; clase `Camera::Sync::SyncUtilityUpm` **0/0/3**; tipo `IMAGER_DRIVEMODE` **0/0/2**) y el
  A6300 tiene un **canal de estabilización del objetivo** (`SteadyShotInfo` **0/0/7**) que la A6000 no tiene.
* **S172** — el módulo `ElecShutter/` del A6300, que S135 solo había localizado por sus nombres de fichero, queda
  **caracterizado**: `EC_ElecShutter_Main.cpp` (`0x4391d67c`) devuelve un **código de modo de obturador**
  (`0x80`→3, `0x100`→4) y `EC_NonlinearElecShutter_MechShutterTable.cpp` implementa la **equivalencia no lineal
  electrónica/mecánica** (32 bits por fila, escalas 10000/1000 y punto fijo 16.16 con escala `0x8000`).
  **Corrige a S135**: los 128 bytes de `0x43dcfa9e` **no tienen ninguna referencia de código**.
* **S174** — el conversor `CamMsgConv` del `libObj.so` conoce **216/221/240** nombres `…ForLiro` y **soporta
  0/0/6**; en la A6000 y la A7S **todos** están en la lista de **rechazo**.

**Regla metodológica que deja S174**: **la presencia de una cadena no prueba una funcionalidad**. Tres casos ya
en el repo: la cadena muerta del *rolling shutter* (S168), el bloque de 128 bytes sin referencias (S172) y los
nombres `…ForLiro` de la A6000, todos rechazados (S174).

**S51 se mantiene: A=NO, B=NO, C=NO.** Todos estos hallazgos son **sobre el firmware**: la ausencia estática de
un módulo, una cadena o un parámetro **no** demuestra incapacidad del hardware. El plan de pruebas físicas (P1–P8,
[capture/physical-test-plan.md](../capture/physical-test-plan.md)) sigue **pendiente de autorización**.

## Avance IMX210 S140–S155 (22-10-2026)

**VERIFICADO:** vector `0x43fe995c` con 119 registros; `S[0]` selecciona una fila y el builder `0x4383c9dc` procesa 4 filas de 16 B desde G+`0x224`, con stores relativos 0/4/6/a/c/e. Dos tablas de diagnóstico incluyen `{id=0x30,size=1,addr=0x43eb0850}`; un copier raw puede leer ese byte y copiarlo a un buffer.

**PARCIAL:** bytes +8/+9 de fila sin store en los cuerpos auditados, con xrefs directas vacías; el literal en tabla demuestra una ruta diagnóstica que puede leer `0x43eb0850`. El dumper está condicionado por flags `0x43f72d05&2`/`0x43f72d08&0x20`; se clasificaron varios xrefs locales, pero no se halló escritor ni valor runtime. La superficie REA no permite sembrar las funciones candidatas no reconocidas. No se infiere ausencia global ni semántica física.

Informes principales: [S140](../capture/s140-imager-register-map.md), [S147](../capture/s147-imager-g-rows.md), [S149](../capture/s149-imager-row-helpers.md), [S150](../capture/s150-imager-row-gaps.md), [S152](../capture/s152-imager-gap-descriptor-read.md), [S153](../capture/s153-imager-dump-gates.md), [S154](../capture/s154-imager-state-ref.md), [S155](../capture/s155-imager-state-readers.md). S51 A/B/C=NO y sin cambios.

Mecanismo de PMCA identificado y contrastado con el firmware 3.21: `updatershell` inyecta un fdat propio (cramfs con `libupdaterbody`, header de 0x30 B por modelo, guard CRC + modelo/región/versión **sin firma**; CXD90014) que el updater ejecuta y expone un shell USB `0x23`; `serviceshell` (senser, HASP) da terminal, backup `0x603`, ficheros y memoria. `bk w 0x003e0005` escribe la propiedad BK4 `modelName` (subsistema `0x3e`/índice 5, 16 B, attr solo-lectura) en el almacén `/setting` (`nflasha2`), no una dirección de código; el preset de fábrica la trae como `ILCE-6000` (verificado). El cambio a `ILCE-6001` está reportado pero su efecto «shell mode» queda **NO VERIFICADO**: la cadena no existe en el firmware. S51 **A=NO, B=NO, C=NO**. [Documento](../capture/s62-pmca-injection.md) · [matriz](../../analysis/s62-evidence-matrix.json).

## Avance S58 (20-10-2026)

Productores numéricos IMX210 recuperados y contrastados con código original; SetMode/SetExposure/SetRead/Execute A7S emulados con objeto sintético y servicios stub. La comparación efectiva actualiza matriz e identidad de métodos A7S de S57. Se conserva la frontera física: fin electrónico de integración **NO VERIFICADO**, S51 **A=NO, B=NO, C=NO**. [Conclusiones y límites S58](../capture/s58-conclusions.md).

Próximo: escritor del bloque de 12 u16 `0x437876dc()+0xdd0`→`0x437aa65c`; recuperar M/Tv/clk de un modo alcanzable. No inferir cierre del sensor a partir de fórmulas ni ausencia de comando final. Estado anterior S47 y siguientes se conserva como historial, no como siguiente tarea vigente.

## Avance S47 (19-10-2026)

VERIFICADO: entrada `0x43789cc0`, registro ID `0x301d7`, fila clave0xce
`0x43ff29b8` → `0x43789708` copia0x140B a `0x43e95420` →
`0x437d9f9c` → `0x437da100` → payload `0x43ed4620` → `0x437dad78`.
Solicitud sintética `0x43ed44dc` distinta. Callback ANTES de copia C:
`0x43792f9c` domina `0x43794096`; `0x43ae90ce` copia0x1a4B desde
`0x43e9d3b4` a `0x43e9b380`, incluye94/95. Orden no refuta S46.
PARCIAL: productor original antes de entrada y valor2/B/G. S48: proveedor
del registro+1ec (`0x435412a0=0`) y stores paquete+1c/+1e para clave0xce.
Evaluación VD opcional aplazada; hito abierto, sin cierre físico de clases1–3.
[Informe S47](../capture/s47-payload-producer-and-order.md).

## Avance S46 — antecedente (18-10-2026)

VERIFICADO: inicialización explícita `0x43e16d2c=0xf3120000`, destino
condicional `0xf3120220`. Callback `0x437dad78`, clave `0xce`, escribe
C=`0x43e9d3b4`+94/+95 desde dos u16: enable!=0 → (1,low8(modo));
enable=0 → (0,0). Registro y destino concretos demostrados.
PARCIAL: propagación (1,2) a B/G; productor del payload y orden pendientes.
Sin alias P/C/snapshot ni cierre físico demostrado. S47: productor4B
`0x43ed4620` vía argumento4 de `0x437da100`; después semántica VD.
[Informe S46](../capture/s46-vd-base-and-context-identity.md).

## Avance S45 — antecedente (18-10-2026)

VERIFICADO: contexto43eaadd8 preparado enVD_Pre; C=43e9b380,
copia1a4 desde43e9d3b4. Getter virtual+74 leeIMX210+3a0;
438c828c calcula timing y llega a436c74c8→43ad2bd6(base+220).
PARCIAL: base del controlador43e16d28 en43e16d2c sin escritor recuperado;
alias/copiaP→C sin demostrar. Integración y cortinas NO_VERIFICADO.
Serie explícitaS40–S45 terminada; hito abiertoS46+, sin agotamiento/Línea E.
Próximo:escritores43e9d3b4+94/+95 y43e16d2c desde owner43e15f18.
[Informe S45](../capture/s45-context-identity-and-physical-closure.md).

## Avance S44 — antecedente (18-10-2026)

VERIFICADO: los registros preparados IMX210 tienen consumidor ID/valor,
empaquetador y transporte a MMIO. Virtual+a8 compara el nibble alto de
una fila de modos, sin consumir flags. PARCIAL: productor local de+95=2,
sin identidad P/C cerrada. Integración y supresión de cortinas NO_VERIFICADO.
Próximo: contexto+50 de437b5b14 y alias hasta raíz+2bc/snapshot43ef2474;
después lectores IMX210+3a0 y significado físico de ID0.
[Informe S44](../capture/s44-register-consumer-mode-table.md).

## Conclusión general vigente (17-10-2026)

S157 añade otra clasificación local: `0x43859954` carga `0x43f72d02` desde GOT; `FUN_43859944` lee `+5/+0xf`, copia a buffers y stores a otros objetos, no a gates `+3/+6`. No cierra escritores restantes. [Informe S157](../capture/s157-imager-state-snapshot.md).

S158 clasifica `0x4385b268`: `FUN_4385b234` carga el puntero GOT del estado y lo derrama a stack; lee +0x26/+0x28/+0x29 y escribe otros destinos, no +3/+6 en este cuerpo. Sigue sin cerrar otros escritores. [Informe S158](../capture/s158-imager-state-ref.md).

S159 clasifica `0x4386001c` como otro spill a stack en `FUN_4385fff0`; el cuerpo lee `+0/+0x1c/+0xa2` y escribe a otros destinos, no a +3/+6 en este procedimiento. No es una conclusión global. [Informe S159](../capture/s159-imager-state-spill.md).

S160 confirma un store a `0x43f72d02+0` en `0x4383ac90` cuando expira un contador compartido. Es el único campo escrito por ese sitio; no modifica `+3/+6`. La alcanzabilidad en una captura no está probada. [Informe S160](../capture/s160-state-open-flag.md).

S161 clasifica `0x4384cb0a` como spill del puntero `0x43f72d02` a stack; el procedimiento lee otros offsets y escribe otro objeto, no `+3/+6` localmente. Sin conclusión global. [Informe S161](../capture/s161-imager-state-spill.md).

S162: `0x438d933e/9378` cargan el state pointer y leen `state+0x1c`; los resultados se guardan en `0x43f7c702/704`, no en el estado. Posible notificación es INFERENCIA; runtime no observado. [Informe S162](../capture/s162-imager-state-event-readers.md).

S163 añade `FUN_438d939c`, lector de `state+0x1c/+0x1e` que usa defaults 3/4 si cero y empaqueta los valores en mensaje a otros destinos. No escribe state/gates en ese cuerpo; propósito de notificación/alcanzabilidad permanecen parciales. [Informe S163](../capture/s163-imager-state-event-reader.md).

Proyecto abierto: hay piezas reales y reutilizables, pero **ninguna captura silenciosa
completa validada**; no está demostrada la capacidad ni la imposibilidad de fotografía
totalmente electrónica a resolución completa.
Fuente completa con estimaciones por escenario: [estado-y-viabilidad-2026-10-17.md](../estado-y-viabilidad-2026-10-17.md).

## Hallazgos corregidos con impacto en todo lo posterior (no reusar versiones previas)

| Tema | Corrección vigente | Fuente |
|---|---|---|
| Darwin — base ROM | La base es `0x4200`, NO `0`. No reusar punteros absolutos de proyectos Ghidra antiguos a6000/a6300-darwin (se conservan solo como análisis fallido). | [CONTEXT.md:354](../../CONTEXT.md#L354), [darwin-shutter-entrypoints.md:1](../capture/darwin-shutter-entrypoints.md) |
| SetImageWrited | Corresponde a `0x6108/0x1007`, **no** `0x1009` (atribución histórica de sesión 12 era errónea; confirmado en S29). | [README.md:91](../../README.md#L91), [pool-write-completion.md](../capture/pool-write-completion.md) |
| GPIO cortinillas | P4D=1ST_CURTAIN_MG, P4E=2ND_CURTAIN_MG, P4C=CA_1ST_CURTAIN_START, P4B=CA_RELEASE_LOCK_MSS — VERIFICADO por coincidencia de coordenadas del esquema + inspección visual, idéntico en A6300. P4D/P4E **no son serie** (descartado estáticamente). | [fm3-gpio-shutter-mapping.md](../capture/fm3-gpio-shutter-mapping.md) |
| EFCS → selector de captura | Recorrido estático cerrado hasta IMX210 (E020); no acredita que todas las ramas se ejecuten en una cámara concreta; SilentShutter +0x238 sigue sin consumidor de captura demostrado. | [efcs-capture-selector.md](../capture/efcs-capture-selector.md) |

## Política de ingeniería inversa: REA primero (vigente desde 2026-10-19)

Canónica para Codex y Claude Code; `AGENTS.md`/`CLAUDE.md` solo la resumen. No sustituye las restricciones activas.

1. **REA primero** para explorar lo nuevo: descubrir funciones, xrefs, llamadas directas/indirectas, grafos
   (`get_call_graph`), dependencias de valores (`trace_native_values`), decompilar (`batch_decompile`,
   `analyze_function`), constantes/estructuras (`search_bytes`, `xrefs`, `resolve_containing_procedure`),
   comparar funciones y recuperar evidencia previa. Hay que *usarlo*, no solo comprobar que está instalado.
2. **Ghidra histórico (`analysis/ghidra/silent-liro.gpr`, readOnly/noanalysis) después**, cuando: REA no
   reconoce una función conocida (p. ej. entradas Thumb sembradas a mano: 0x43789cc0, 0x43789708, 0x437da100,
   0x43792f9c, 0x43794096, 0x43ae90ce; REA cubre 363/464 entradas históricas), su análisis es incompleto o
   ambiguo, hay que verificar bytes/instrucciones ya recuperados, o seguir una investigación conocida es
   más barato que repetir búsquedas fallidas. Una consulta vacía de REA **no** prueba ausencia.
3. **Coste:** `av-cam.bin` cuesta ~8 min en frío y la sesión REA no persiste (rea#1048). Primero buscar
   evidencia ya exportada (`knowledge/`, `analysis/rea-independent/out/`). Si hay que abrirlo: comprobar
   si ya hay demonio (`analysis/rea-independent/run/rea.sock` + `.ready`, proceso `session_daemon.py`);
   si no, abrirlo **una vez** con `bin/session_daemon.py` y consultar por lotes con `bin/q.py`
   (el demonio fija `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=2G`, límite 2,6 GB y 1 h de
   inactividad); cerrar con `q.py SOCK --shutdown` al terminar el hito y comprobar que no quedan
   procesos. Bibliotecas ELF pequeñas (`libmprctrl.so`): MCP `rea` directo (~25 s). Evitar `list_procedures`
   masivo sin paginar. Detalle y parámetros: [rea-independent-milestone.md](../capture/rea-independent-milestone.md).
4. **Rigor:** REA y Ghidra comparten motor: su acuerdo prueba configuración coherente, no independencia
   (el decodificador independiente es LLVM `llvm-objdump` + búsqueda de bytes propia). Verificar los
   hallazgos decisivos contra instrucciones y bytes reales; separar hecho, inferencia y NO_VERIFICADO.
5. **Intactos siempre:** firmware original, `silent-liro.*`, `analysis/ghidra`, informes S1–S48; comprobar con
   SHA-256 (`analysis/rea-independent/manifests/*.final.sha256`). REA trabaja en proyecto temporal
   `-readOnly -deleteProject`. Sin ejecutar firmware, sin flasheo, sin pruebas físicas.
6. **Foco:** obturador completamente electrónico, en hitos grandes y autónomos; no ampliar infraestructura.
7. **MCP:** `rea` en Codex (`~/.codex/config.toml`, `[mcp_servers.rea]`) y en Claude Code (`.mcp.json` del directorio padre `../`, único punto de configuración MCP/permisos; sesiones siempre desde el padre;
   usa `scripts/rea`, requiere aprobación del usuario al abrir `claude`), junto a `sony-a6000-knowledge`.

## Restricciones activas

- No se ha ejecutado firmware en hardware real; no se ha flasheado ninguna cámara.
- **Git**: el usuario ha instruido explícitamente (21-10-2026) **subir cada hito terminado a
  `origin/main`**; sigue vigente la prohibición de subir firmware, de tocar la cámara y de flashear.
  Los hitos se commitean **por ruta** (nunca `git add -A`) y el repositorio se compacta con
  `git gc` (`gc.auto=512`).
- Ningún resultado estático se ha convertido en demostración física sin evidencia adicional explícita.
- EFCS/SilentShutter: hay opciones de software y transporte identificados; **no** hay control físico demostrado ni finalización electrónica de exposición confirmada.

## Próximos pasos de investigación (vigentes al 21-10-2026)

1. **Línea del obturador**: ejecutar el plan de pruebas físicas P0–P2 y P7 (requiere autorización
   explícita del usuario); en estático, seguir el destino de las etapas de captura
   (`0x4385a630`, `0x438e67dc`, `0x43b2335e`) hasta el origen del valor que gobierna el tipo de
   mecanismo (`[G+0x808]&7`, S101).
2. **Línea general**: seguir con los módulos "de contenido nuevo" que quedan sin decodificar
   (`[DEPTH]`, `[PANDA]`, `[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]`, `[TP_R]`, `[CAMERA_IS]`, `[JOG]`,
   `[ADC_DEBUG]`, `[LIF_DEBUG]`, `[CAMERA_MAIN_FC]`) y cerrar las preguntas abiertas de S134
   (quién escribe `svr_num`/`VdNum`; el bloque de modo por `drive_mode`).

### Próximos pasos (histórico al 17-10-2026)

Ver tabla "Flujos incompletos" en [estado-y-viabilidad-2026-10-17.md](../estado-y-viabilidad-2026-10-17.md):
botón físico → orden de cortinas (falta tabla de teclas y puente InfraInput),
EFCS/Silent → sensor (falta demostrar fin de integración electrónica), sensor → imagen
disponible (falta productor final DMA y propiedad de buffer).

## Cómo consultar el sistema de conocimiento

Actualización estática S32: listas VD y seis destinos de callback resueltos;
`0x4379b44c` prepara referencias a memoria compartida para SyncYCout.
El diagnóstico `0x4379cb2e` comprueba una ventana temporal, no fin DMA.
Falta vincular el handle fuente a píxeles/pitch/formato y al consumidor efectivo.
Ver [evidencia S32](../capture/s32-vd-callbacks-sync-ycout.md).

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py exact "0x..."        # dirección/símbolo
python3 scripts/knowledge/search.py text "concepto"       # búsqueda BM25
python3 scripts/knowledge/search.py tree --subsystem docs/capture
python3 scripts/knowledge/search.py claim docs/capture/<doc>.md   # qué lo corrige
```

Ver [knowledge/PROGRESS.md](../../knowledge/PROGRESS.md) para el estado de implementación
del propio sistema de conocimiento (fases completadas/pendientes).

Auditoría vigente de la lista de pendientes:
[sincronización del 24-10-2026](../capture/pending-sync-audit-2026-10-24.md).

Pendientes por cerrar: [PENDIENTES.md](../PENDIENTES.md); se actualiza en cada tarea y cada hallazgo nuevo se añade allí.
