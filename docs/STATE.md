# Estado vigente — Sony A6000 reverse engineering

Documento breve de orientación. No reemplaza las fuentes: cada afirmación enlaza al
documento canónico donde está comprobada, con su rango de líneas cuando aplica.
Para el historial íntegro de sesiones ver `docs/history/` y las correcciones completas
en [docs/CORRECTIONS.md](CORRECTIONS.md) (generado del grafo, no editar a mano).
Para preguntas abiertas ver [docs/OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).

## Avance S138–S169 (22-10-2026) — línea de RE general y controles positivos del obturador

**Línea de RE general** (catálogo con 100 hitos: [docs/capture/linea-general-re.md](capture/linea-general-re.md)).
Nueve hitos nuevos decodificados con bytes y tests propios: `[CAMERA_MAIN_FC]` (S138),
`[CAM_UTIL_ADJ]` (S143), `[CAM_UTIL_SENS]` (S144), `[DEPTH]` (S148), `[PANDA]` (S151), `[TP_R]` (S156),
`[CAMERA_IS]` (S164), `[JOG]` (S165), `[ADC_DEBUG]` (S166).

**Patrón consolidado**: en los siete módulos de trazas, la **etiqueta de módulo es propia de la
fw3.21** pero la **funcionalidad ya existía** en la A7S fw3.20 o el A6300 fw2.01 → la fw3.21 de
la A6000 **reescribe el logging, no el firmware** (conclusión de S128/S130, con 7 ejemplos más).
Casos notables: `[CAM_UTIL_ADJ]`/`[CAM_UTIL_SENS]` son **el mismo par** (dependencia cruzada
`0x43900c9c`, `0x439012fa`/`0x43901302`; ids OSAL compartidos) y escriben **calibración en la RAM
del sensor** (51 comandos «Sens» en `0x43fe858c`); `[DEPTH]` sale a la **EXIF** (tags `0x5001`/`0x5002`);
`[TP_R]` es un **reporter** y **corrige un falso positivo de S130** (plantillas OSAL ≠ mismo código);
`[CAMERA_IS]` es **la capa que aplica la estabilización** (17/17 pares PIC verificados → **valida el
mapa de S70**) y su infraestructura RC es **común a los tres**; `[JOG]` es la **fuente de eventos de
la rueda** (el A6300 sustituye `JogVGrip` por `JogCaif`); `[ADC_DEBUG]` es el **volcado del driver
LIRO ADC** y **corrige una lectura de S164** (el «ADC» del giroscopio no es ese servicio).

**S168 — la cadena de *rolling shutter* del A6300 está MUERTA.** `position num in rolling is strange %d`
(`0x43d9fe03`) tiene **0 referencias de código** (regla estricta, punteros absolutos, pares
`movw`/`movt` y un método inverso independiente); de las 5 cadenas de su banda, **4 sí están
referenciadas** (el único código vivo es el cálculo de ancho del **número de posición del VD**,
`0x4372914c`). **Corrige** el colateral de S164: la cadena del A6300 **no** demuestra que ese
firmware implemente *rolling shutter*.

**S169 — la API de *drive* del A6300 no existe en la A6000.** El A6300 fw2.01 tiene una **capa de
validación de parámetros de cámara** (`LiroSeq`) con **201 propiedades** `CheckSet*` y **370**
comprobaciones `ParamCheckErr`, entre ellas los **parámetros de obturador** `sc_ShutDrive` (`+0x1dd`),
`uc_ShutDriveMode` (`+0x1dc`), **`front_eshutter`** (`+0x23c`), **`SilentShutterMode`** (`+0x264`),
**`shutterType`** (`+0x268`), `ul_ShutLowLimit`, `sc_IrisDrive`, `uc_IrisDriveMode`, `sc_ExposureDrive`.
**La A6000 fw3.21 y la A7S fw3.20 tienen 0/0 de todo eso** → **no falta la traza, falta el parámetro**.
Refuerza **S135** con evidencia de **parámetros en runtime**, no solo de configuración del HAL.
Matiz: la A6000 **sí** tiene el módulo LiroSeq (2 trazas) y el `drive_mode` del imager (S134).

**S51 se mantiene: A=NO, B=NO, C=NO.** Todos estos hallazgos son **sobre el firmware**: la ausencia
estática de un módulo, una cadena o un parámetro **no** demuestra incapacidad del hardware. El plan
de pruebas físicas (P1–P8, [capture/physical-test-plan.md](capture/physical-test-plan.md)) sigue
**pendiente de autorización** y ninguna prueba se ha ejecutado.

## Avance IMX210 S140–S155 (22-10-2026)

**VERIFICADO:** vector `0x43fe995c` con 119 registros; `S[0]` selecciona una fila y el builder `0x4383c9dc` procesa 4 filas de 16 B desde G+`0x224`, con stores relativos 0/4/6/a/c/e. Dos tablas de diagnóstico incluyen `{id=0x30,size=1,addr=0x43eb0850}`; un copier raw puede leer ese byte y copiarlo a un buffer.

**PARCIAL:** bytes +8/+9 de fila sin store en los cuerpos auditados, con xrefs directas vacías; el literal en tabla demuestra una ruta diagnóstica que puede leer `0x43eb0850`. El dumper está condicionado por flags `0x43f72d05&2`/`0x43f72d08&0x20`; se clasificaron varios xrefs locales, pero no se halló escritor ni valor runtime. La superficie REA no permite sembrar las funciones candidatas no reconocidas. No se infiere ausencia global ni semántica física.

Informes principales: [S140](capture/s140-imager-register-map.md), [S147](capture/s147-imager-g-rows.md), [S149](capture/s149-imager-row-helpers.md), [S150](capture/s150-imager-row-gaps.md), [S152](capture/s152-imager-gap-descriptor-read.md), [S153](capture/s153-imager-dump-gates.md), [S154](capture/s154-imager-state-ref.md), [S155](capture/s155-imager-state-readers.md). S51 A/B/C=NO y sin cambios.

Mecanismo de PMCA identificado y contrastado con el firmware 3.21: `updatershell` inyecta un fdat propio (cramfs con `libupdaterbody`, header de 0x30 B por modelo, guard CRC + modelo/región/versión **sin firma**; CXD90014) que el updater ejecuta y expone un shell USB `0x23`; `serviceshell` (senser, HASP) da terminal, backup `0x603`, ficheros y memoria. `bk w 0x003e0005` escribe la propiedad BK4 `modelName` (subsistema `0x3e`/índice 5, 16 B, attr solo-lectura) en el almacén `/setting` (`nflasha2`), no una dirección de código; el preset de fábrica la trae como `ILCE-6000` (verificado). El cambio a `ILCE-6001` está reportado pero su efecto «shell mode» queda **NO VERIFICADO**: la cadena no existe en el firmware. S51 **A=NO, B=NO, C=NO**. [Documento](capture/s62-pmca-injection.md) · [matriz](../analysis/s62-evidence-matrix.json).

## Avance S58 (20-10-2026)

Productores numéricos IMX210 recuperados y contrastados con código original; SetMode/SetExposure/SetRead/Execute A7S emulados con objeto sintético y servicios stub. La comparación efectiva actualiza matriz e identidad de métodos A7S de S57. Se conserva la frontera física: fin electrónico de integración **NO VERIFICADO**, S51 **A=NO, B=NO, C=NO**. [Conclusiones y límites S58](capture/s58-conclusions.md).

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
[Informe S47](capture/s47-payload-producer-and-order.md).

## Avance S46 — antecedente (18-10-2026)

VERIFICADO: inicialización explícita `0x43e16d2c=0xf3120000`, destino
condicional `0xf3120220`. Callback `0x437dad78`, clave `0xce`, escribe
C=`0x43e9d3b4`+94/+95 desde dos u16: enable!=0 → (1,low8(modo));
enable=0 → (0,0). Registro y destino concretos demostrados.
PARCIAL: propagación (1,2) a B/G; productor del payload y orden pendientes.
Sin alias P/C/snapshot ni cierre físico demostrado. S47: productor4B
`0x43ed4620` vía argumento4 de `0x437da100`; después semántica VD.
[Informe S46](capture/s46-vd-base-and-context-identity.md).

## Avance S45 — antecedente (18-10-2026)

VERIFICADO: contexto43eaadd8 preparado enVD_Pre; C=43e9b380,
copia1a4 desde43e9d3b4. Getter virtual+74 leeIMX210+3a0;
438c828c calcula timing y llega a436c74c8→43ad2bd6(base+220).
PARCIAL: base del controlador43e16d28 en43e16d2c sin escritor recuperado;
alias/copiaP→C sin demostrar. Integración y cortinas NO_VERIFICADO.
Serie explícitaS40–S45 terminada; hito abiertoS46+, sin agotamiento/Línea E.
Próximo:escritores43e9d3b4+94/+95 y43e16d2c desde owner43e15f18.
[Informe S45](capture/s45-context-identity-and-physical-closure.md).

## Avance S44 — antecedente (18-10-2026)

VERIFICADO: los registros preparados IMX210 tienen consumidor ID/valor,
empaquetador y transporte a MMIO. Virtual+a8 compara el nibble alto de
una fila de modos, sin consumir flags. PARCIAL: productor local de+95=2,
sin identidad P/C cerrada. Integración y supresión de cortinas NO_VERIFICADO.
Próximo: contexto+50 de437b5b14 y alias hasta raíz+2bc/snapshot43ef2474;
después lectores IMX210+3a0 y significado físico de ID0.
[Informe S44](capture/s44-register-consumer-mode-table.md).

## Conclusión general vigente (17-10-2026)

S157 añade otra clasificación local: `0x43859954` carga `0x43f72d02` desde GOT; `FUN_43859944` lee `+5/+0xf`, copia a buffers y stores a otros objetos, no a gates `+3/+6`. No cierra escritores restantes. [Informe S157](capture/s157-imager-state-snapshot.md).

S158 clasifica `0x4385b268`: `FUN_4385b234` carga el puntero GOT del estado y lo derrama a stack; lee +0x26/+0x28/+0x29 y escribe otros destinos, no +3/+6 en este cuerpo. Sigue sin cerrar otros escritores. [Informe S158](capture/s158-imager-state-ref.md).

S159 clasifica `0x4386001c` como otro spill a stack en `FUN_4385fff0`; el cuerpo lee `+0/+0x1c/+0xa2` y escribe a otros destinos, no a +3/+6 en este procedimiento. No es una conclusión global. [Informe S159](capture/s159-imager-state-spill.md).

S160 confirma un store a `0x43f72d02+0` en `0x4383ac90` cuando expira un contador compartido. Es el único campo escrito por ese sitio; no modifica `+3/+6`. La alcanzabilidad en una captura no está probada. [Informe S160](capture/s160-state-open-flag.md).

S161 clasifica `0x4384cb0a` como spill del puntero `0x43f72d02` a stack; el procedimiento lee otros offsets y escribe otro objeto, no `+3/+6` localmente. Sin conclusión global. [Informe S161](capture/s161-imager-state-spill.md).

S162: `0x438d933e/9378` cargan el state pointer y leen `state+0x1c`; los resultados se guardan en `0x43f7c702/704`, no en el estado. Posible notificación es INFERENCIA; runtime no observado. [Informe S162](capture/s162-imager-state-event-readers.md).

S163 añade `FUN_438d939c`, lector de `state+0x1c/+0x1e` que usa defaults 3/4 si cero y empaqueta los valores en mensaje a otros destinos. No escribe state/gates en ese cuerpo; propósito de notificación/alcanzabilidad permanecen parciales. [Informe S163](capture/s163-imager-state-event-reader.md).

Proyecto abierto: hay piezas reales y reutilizables, pero **ninguna captura silenciosa
completa validada**; no está demostrada la capacidad ni la imposibilidad de fotografía
totalmente electrónica a resolución completa.
Fuente completa con estimaciones por escenario: [estado-y-viabilidad-2026-10-17.md](../docs/estado-y-viabilidad-2026-10-17.md).

## Hallazgos corregidos con impacto en todo lo posterior (no reusar versiones previas)

| Tema | Corrección vigente | Fuente |
|---|---|---|
| Darwin — base ROM | La base es `0x4200`, NO `0`. No reusar punteros absolutos de proyectos Ghidra antiguos a6000/a6300-darwin (se conservan solo como análisis fallido). | [CONTEXT.md:354](../CONTEXT.md#L354), [darwin-shutter-entrypoints.md:1](capture/darwin-shutter-entrypoints.md) |
| SetImageWrited | Corresponde a `0x6108/0x1007`, **no** `0x1009` (atribución histórica de sesión 12 era errónea; confirmado en S29). | [README.md:91](../README.md#L91), [pool-write-completion.md](capture/pool-write-completion.md) |
| GPIO cortinillas | P4D=1ST_CURTAIN_MG, P4E=2ND_CURTAIN_MG, P4C=CA_1ST_CURTAIN_START, P4B=CA_RELEASE_LOCK_MSS — VERIFICADO por coincidencia de coordenadas del esquema + inspección visual, idéntico en A6300. P4D/P4E **no son serie** (descartado estáticamente). | [fm3-gpio-shutter-mapping.md](capture/fm3-gpio-shutter-mapping.md) |
| EFCS → selector de captura | Recorrido estático cerrado hasta IMX210 (E020); no acredita que todas las ramas se ejecuten en una cámara concreta; SilentShutter +0x238 sigue sin consumidor de captura demostrado. | [efcs-capture-selector.md](capture/efcs-capture-selector.md) |

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
   masivo sin paginar. Detalle y parámetros: [rea-independent-milestone.md](capture/rea-independent-milestone.md).
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

Ver tabla "Flujos incompletos" en [estado-y-viabilidad-2026-10-17.md](../docs/estado-y-viabilidad-2026-10-17.md):
botón físico → orden de cortinas (falta tabla de teclas y puente InfraInput),
EFCS/Silent → sensor (falta demostrar fin de integración electrónica), sensor → imagen
disponible (falta productor final DMA y propiedad de buffer).

## Cómo consultar el sistema de conocimiento

Actualización estática S32: listas VD y seis destinos de callback resueltos;
`0x4379b44c` prepara referencias a memoria compartida para SyncYCout.
El diagnóstico `0x4379cb2e` comprueba una ventana temporal, no fin DMA.
Falta vincular el handle fuente a píxeles/pitch/formato y al consumidor efectivo.
Ver [evidencia S32](capture/s32-vd-callbacks-sync-ycout.md).

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py exact "0x..."        # dirección/símbolo
python3 scripts/knowledge/search.py text "concepto"       # búsqueda BM25
python3 scripts/knowledge/search.py tree --subsystem docs/capture
python3 scripts/knowledge/search.py claim docs/capture/<doc>.md   # qué lo corrige
```

Ver [knowledge/PROGRESS.md](../knowledge/PROGRESS.md) para el estado de implementación
del propio sistema de conocimiento (fases completadas/pendientes).
