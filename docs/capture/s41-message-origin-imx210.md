# S41 — productores de mensajes, snapshots y valores de modo IMX210

18-10-2026. **PARCIAL:** productores internos de `4000/4036`, transporte
y productores de snapshots recuperados. Origen último de `3023`, resolución
del destino con bit 31 y enlace de sus valores a integración física pendientes.
La frontera de implementación OSAL activa una comprobación de Línea C;
no se declara agotamiento universal de las líneas A/B.

## VERIFICADO — método e integridad

Solo `analysis/ghidra/silent-liro.gpr`, programa `av-cam.bin`, con
`-readOnly -noanalysis`. Sin crear funciones, tipos, referencias ni guardar
el programa. `S41Export.java` y `S41Scan.java` consultan memoria/listado;
la primera exportación reutiliza `S39Export.java` (su comentario identifica
el exportador). Cada ejecución comprueba el SHA y todos los bytes cargados.

SHA-256 esperado antes/después:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
También se contrastan los manifiestos persistentes S38 del `.gpr/.rep`.
Sin firmware ejecutado, cámara, flasheo, instalaciones ni push.

Se leyó CURRENT antes de CONTEXT/STATE y únicamente S40 como antecedente
técnico reciente; no se leyeron S31–S39 completos. Aplicadas las skills
knowledge-navigation, contradiction-audit y knowledge-maintenance.
`claim S40` devuelve una relación **CONFLICTO_PENDIENTE** desde CONTEXT:
su cita cruza al encabezado S30; no constituye evidencia técnica de corrección.
Los hallazgos siguientes se contrastan con nuevos exports.

Evidencia primaria: `analysis/ghidra/s41-*.json` y `.c`, inventario
`s41-inventory.json`, manifiesto `s41-findings.json`, auditor `s41-audit.py`.
El inventario de constantes contiene coincidencias no alineadas y opcodes:
no se interpretan automáticamente como IDs ni estructuras.

## VERIFICADO — receptor, API de mensajes y productores internos

| Hallazgo | Dirección exacta / contrato | Estado |
|---|---|---|
| Alta del hilo principal | `437ff098`: puntero Thumb `437fee09` calculado en `437ff09e`; `43acac1a`, luego `43acac02` con número `45` en `437ff0a6` | VERIFICADO; no es una llamada síncrona al hilo |
| Recepción principal | `437fee12→43561260(30001,&mensaje,-1)`; literal `437feedc=00030001` | VERIFICADO |
| Metadato de origen inmediato | `437fee40` lee `mensaje-4`; `43b0091c` escribe exactamente esa palabra | VERIFICADO; no confundir con comando+2 |
| Fin de vida | `437feed4→435612ec(30001,mensaje)` tras el despacho | VERIFICADO |
| API de envío | `4356120c` llama indirectamente `tabla+1d4`; recepción `43561260→tabla+1e0`; reserva `435612d0`; liberación `435612ec→tabla+1f4`; consulta `43561340→tabla+204` | VERIFICADO; implementación externa no recuperada aquí |
| Envío genérico | `437feef8`: tamaño 0x8..0x407, reserva en destino argumento 3, copia solicitud, `mensaje-4=30001`, envía al destino argumento 3 | VERIFICADO; destino no siempre 30001 |
| Envío local auxiliar | `437fefb8`: reserva/copia/envía a `30001`, origen en argumento 1; llamadores `437ff038/437ff064` construyen `402d/40ab` | VERIFICADO; no son productores de los tres comandos buscados |
| Transporte de configuración | `4381a138→435aa20c→435612d0/439c5320/4356120c`; destino 30001; metadato almacenado mediante `43a49628` | VERIFICADO |

La raíz de importación cargada es `GOT[440205c0]=43541000`, cuyo
campo +14 apunta a `435410b4`. Slots de envío `43541288` (+1d4),
recepción `43541294` (+1e0), consulta `435412b8` (+204, incluido en el
dump contiguo) y configuración `4354134c` (+298) son cero en el blob.
Frontera estática concreta: no se puede asignar un cuerpo al destino
indirecto ni explicar bit31 a partir del valor de esos slots. No es
prueba de ausencia de implementación en el sistema ni de agotamiento de
los metadatos de mensajes todavía sin tipar.

`435aa20c` toma el tamaño de la envoltura (`+1a` o `+8`, según tipo),
copia desde `envoltura+10`, conserva origen y envía. Por tanto los bytes
de las solicitudes de los constructores siguientes alcanzan la cola del
hilo; no se deduce UI/PTP por el nombre genérico de la API.

| Comando | Productor y campos | Envío / clasificación |
|---|---|---|
| `4000` | `43816448`: solicitud de `17` bytes, tipo 5, comando en `43816832`; `solicitud+a` viene de `4381ad40` | `4381685a→4381a138`, literal `438168cc=30001`; VERIFICADO |
| `4036` | `43818c1c`: solicitud de `b` bytes, tipo 5; `solicitud+9` viene de `4381a648` | `43818cf2→4381a138`, literal `43818d14=30001`; VERIFICADO |
| `4036` alternativo | `43817e20`: solicitud de `b` bytes, inicializada a cero, tipo 5; fija `solicitud+a=1`, deja `solicitud+9=0` | `43817e48→4381a138`, literal `43817e50=30001`; VERIFICADO |
| `3023` | receptor/escritor `43809148`, sin constructor inequívoco recuperado | PARCIAL; no atribuir las coincidencias de inmediato a este mensaje |

Los inmediatos `3023` de `43aea938` y `43a74e80` pertenecen a otros
contratos (log/RelMgr y llamada virtual); no construyen esta solicitud.
Las tablas en `43ffe020/340/6d0/740` contienen claves `3023`, pero sus
destinos `437fd5e4/437fd3b0/437fd0b0/437fd11c` son getters de tres
instrucciones Thumb (`ldr/add pc/bx lr`), no productores. Devuelven,
respectivamente, `43bf37c4/43bf344e/43bf3736/43bf341e`: datos binarios,
no cadenas con nombres de comandos. Se exportaron mediante desensamblado
temporal con contexto TMode, sin insertar instrucciones en el proyecto.
El auditor rechaza la primera decodificación temporal ARM inválida y
acepta solo los tres opcodes Thumb contrastados.

**Clasificación de origen:** VERIFICADO el productor inmediato interno de
`4000/4036`; INFERENCIA que lee un almacén de configuración, por las claves
y conversiones de `435613b0`. UI/menú, USB/PTP, nombres de parámetros y
productor último de `3023`: **NO_VERIFICADO**. Las referencias de llamadas
`438199a2/43819a78/4381a04e`, `43819ec6` y `4381a05c` se conservan en
los exports. Ghidra asigna algunas al cuerpo no contiguo `43794e0c` y no
recupera su switch: el pseudocódigo no permite afirmar su semántica.

## VERIFICADO/PARCIAL — casos 1 y 10: protocolo de snapshots

El segundo hilo comienza en `43806e38`: recibe en `43806e48` con literal
`43806e64=3030f`, llama `438069f0` en `43806e54`, libera en `43806e5c`.
Su puntero Thumb está en `440200f4=43806e39`; alta `43806e68`, número `69`.

| Mensaje | Constructor demostrado | Contenido y consumo |
|---|---|---|
| caso 1 | `43b01026`, si `objeto+568==1` | tipo 1 en `objeto+4`, rol en +5, secuencia en +6; envía desde `objeto+4`, tamaño `564`, vía `43806400` |
| recepción caso 1 | `43806a80→43b00cd0(objeto,mensaje+4)` | copia `560` bytes a `objeto+8`; antes fija mensaje+b8 al estado; respuesta caso 2 mediante `43806668` |
| caso 10, bloque completo | `43b00f62`, si `objeto+568==1` | tipo 10 en `objeto+6c0`, rol +6c1, secuencia +6c2; envía `5e0` bytes desde +6c0 mediante `43806400` |
| caso 10, bloque corto | `43b00f22`, si `objeto+568==2` | tipo 10 en `objeto+ca0`; envía `28` bytes. No contiene por sí solo un bloque de `560` bytes |
| recepción caso 10 | `43806d50→43b00cd0(objeto,mensaje+8)` solo si `objeto+568==2` | copia bloque completo; si estado 1 toma otros campos mediante `43b00dac`, no esa copia; respuesta caso 11 por `43806590` |

El productor del bloque conservado es `43b00cd0`: cuando estado 1,
copia `564` bytes desde `objeto+4` a `objeto+6c4`, antes de reemplazar
la configuración de `objeto+8`. Por tanto el caso 1 lleva configuración
vigente; el caso 10 largo lleva la configuración previamente conservada:
su `mensaje+8` corresponde a `objeto+6c8`. Ambos participan del gestor
de snapshots; no son escrituras independientes de registros del sensor.
El gestor puede alimentarse desde staging mediante `43804cc8` (S40).

**PARCIAL:** `43806400` reserva/envía a **8003030f**, con procedencia
`mensaje-4=3030f`; `438064c8` usa el mismo par; `438061c4` envía a
3030f sin bit alto. `43805870` reenvía comandos principales a **80030001**
con procedencia 3030f. La implementación de OSAL es indirecta: no se ha
demostrado aquí cómo enruta bit 31 ni que todo emisor con ese ID termine
en el receptor local. No eliminar ese bit por intuición, ni presentar el
intercambio como un bucle local cerrado. Los constructores/layouts quedan
VERIFICADO, la entrega extremo a extremo de ese intercambio queda PARCIAL.

**INFERENCIA:** sincronización entre roles del gestor, por estado 1/2,
secuencia, respuestas y conservación/restauración. No se identifica el
otro participante como UI, USB, otro procesador o copia local sin resolver OSAL.

## VERIFICADO — propagación de valores; límite hacia IMX210

| Campo / selección | Valor concreto recuperado | Alcance |
|---|---|---|
| `4000 solicitud+a→S+24` | `4381ad40`, tabla `43bc59e0`, u32 `{1,0,5}` para entrada 0..2; fuera de rango devuelve 0 | VERIFICADO; no son tres modos físicos identificados |
| Entrada de esa conversión | `43816448` lee mediante `435613b0` clave `010703f1` (`438168c0`) | VERIFICADO como clave numérica; nombre de opción NO_VERIFICADO |
| `4036 solicitud+9→S+48` | `4381a648`, tabla `43bc5a50`, u32 `{1,2,0,3}` para entrada 0..3; resto devuelve 1 | VERIFICADO |
| Entradas de esa conversión | claves `01070832` o `01070012` según rama de `43818c1c`; variante `43817e20` produce 0 | VERIFICADO; almacenista externo no resuelto |
| `3023 solicitud+e→S/R+458` | sigue variable; sustitución selector4: `+450/+454/+456=1,dimX,dimY` o `3,320,240`; no sustituye +458 | VERIFICADO; no confundir dimensiones con exposición |
| Selección en VD_Pre | `43793516→43794a44`; `4379351c` toma R+458 si habilitado, de lo contrario `43793522` toma R+48 | VERIFICADO |
| Remapificación | `43793524/28` y `437935be/c4`: entrada 0,1,2,3 → salida 0,2,1,4; escritura +5cc en `4379357c` / `437935ea` | VERIFICADO software; entrada >3 entra en diagnóstico |

La condición sigue siendo bit7 de `context[2]+269` y tabla
`43ca3c21={1,1,0,1}` indexada por `R+450-1`. No se transforma esto en
una tabla VMAX/HMAX. En la segunda rama VD_Pre primero fuerza R+48=0
en `437935ae`, y solo utiliza R+458 cuando lo permite el selector.

Se exportaron consumidores `43796954`, `4380e43c`, `4380f440` y funciones
`43795a60`, `436d6b50` (SetMode), `436d6f6c` (SetExposure), junto con
las referencias de las cadenas SetMode/SetExposure en `43c933ba/43c9341d`.
`4380f440` llama `4380e43c` y copia un bloque de `44` bytes; eso no es
una llamada directa a SetMode. `43795a60` empaqueta parámetros, no acredita
por su nombre una escritura hardware. No se recuperó una cadena con
identidad de campo que lleve estos valores a los argumentos de
`436d6b50/436d6f6c`, ni a registros de integración, VMAX o HMAX.

**NO_VERIFICADO:** llamada demostrable desde R+450..R+458 a SetMode,
SetExposure/Integration/Readout, habilitación física o fin electrónico de
integración. La búsqueda de cadenas solo ofrece candidatos; no acredita
ausencia universal de consumidores. SilentShutter no demuestra ruta funcional.

## Línea C — condiciones de obturación contrastadas

Activada al encontrar los slots OSAL sin destino en este blob. Se consultó
la vigencia de [E020](efcs-capture-selector.md) y solo sus secciones
de recorrido/selección; no registra correcciones explícitas. Nueva evidencia
en `s41-shutter-conditions.json/.c`, siempre en el mismo proyecto de lectura.

| Condición/control | Evidencia exacta | Clasificación |
|---|---|---|
| Configuración EFCS independiente | `43845f30` lee común+210; `43845f34` escribe banco+41c | VERIFICADO; no es R+458 |
| Selección normal | `4384215e` lee flags banco+4bc; sin bits e0, `4384219e` comprueba +41c: si distinto de 1 selecciona clase3; si 1 parte de clase1, con anulaciones por modo/umbral | VERIFICADO software; clases EFCS/mecánica según el contrato E020, no prueba de movimiento físico |
| Anulación de diagnóstico | `438421f0` lee diagnóstico+7e: valores1..8 fuerzan clase0..7; valor3 fuerza clase2 | VERIFICADO; no opción de usuario demostrada |
| Otra anulación | `438422bc/d2` lee argumento1+36/+37; si +36==1, +37==2 conserva clase2 | VERIFICADO; productor y factibilidad de esta combinación PARCIAL |
| Llamada real de exposición | `438c830c→436d6320(captura+64c,...)`; solo captura+4b9c==0. Clases de dispositivo2/3 fuerzan byte captura+655=0 en `438c82bc` | VERIFICADO; condiciones no omitidas |
| Discriminador del backend | `436d6fb6` lee parámetro+9; switch compara con4 en `436d70be`, rechazo fuera de0..4 | VERIFICADO; dominio distinto de clases0..7 del diagnóstico |

En `436d6f6c`, clase1 fija los bits de máscara d4 a **c4**, clase3 a
**d4**, clase2 a **94**. Clase2 también escribe desde parámetro+8 y
parámetro+14 (hexadecimal), y calcula otra temporización. Se conserva el
resto de bits del byte: son valores bajo máscara, no escrituras completas
constantes del registro. Esto distingue tres ramas de programación, pero
**NO_VERIFICADO** que clase2 signifique final de integración electrónico,
que sus condiciones sean realizables en captura fija, ni que produzca YC
válido sin segunda cortina. No se encontró un comando nuevo demostrado
que cierre esa función física; SilentShutter no se usa como sustituto.

La rama normal EFCS/mecánica tiene condiciones concretas y una llamada
de exposición; la tercera rama candidata solo queda **PARCIAL** por el
control/semántica. Este contraste no enlaza R+450..R+458 con ese selector.

## Pendiente real y próximo paso exacto

Pendiente: resolver bit31 en `4356120c/435612d0` y el participante del
intercambio 3030f; constructor original del paquete `3023`; claves y
disparadores originales de 4000/4036; flujo de valores +5cc hasta parámetros
tipados del sensor. No se declara agotamiento universal de la mensajería:
quedan tablas con contratos sin tipar. La frontera concreta de slots OSAL
cero sí motivó cambiar a Línea C dentro de S41; sus resultados se detallan
antes de esta sección. No repetir la búsqueda del cuerpo de un slot cero
como si el proyecto proporcionara una importación resuelta.

Próximo paso exacto dentro de av-cam: buscar productores de los controles
argumento1+36/+37 de `43842158`, especialmente valor2, y seguir sus
llamadores hasta la selección de captura. Contrastar argumentos+8/+14 de
clase2 de `436d6f6c` con su programación y sincronía de cortinas, sin
forzar valores. En A/B, tipar los datos `43bf37c4/43bf344e/43bf3736/43bf341e`
devueltos por los getters de las filas 3023 y buscar el consumidor de
esas descripciones, distinguiendo metadatos de construcción/envío.
Resolver bit31 de OSAL requiere información adicional del proveedor;
los slots cero por sí solos no permiten continuar ese enlace.
En Línea B, buscar lecturas del campo +5cc **con identidad R** hasta
el bloque de `44` bytes de `4380f440` y su consumidor SetSequenceMode;
solo cerrar SetMode/SetExposure con sitio de llamada y argumento demostrados.

## Validación

Auditor de evidencia creado antes del manifiesto: primer resultado FAIL
por `s41-findings.json` ausente; la ampliación del auditor también rechazó
la decodificación ARM temporal. Exportación corregida Thumb: auditor PASS,
incluidos tablas de valores, opcodes de getters y condiciones de Línea C.
Ruff del auditor PASS; mypy src/auditor PASS. Ruff src/tests conserva los
nueve avisos previos en cuatro tests ajenos, sin cambios allí.
`pytest tests/knowledge -q`: **67 PASS**. Mantenimiento completo
index→graph→corrections→index→graph: **1455 entidades / 2774 relaciones**
en las dos reconstrucciones, grafo estable. SHA del firmware y manifiestos
`.gpr/.rep` verificados al cierre. El índice mantiene su extracción actual;
la evidencia nueva queda en los exports, sin ampliar la arquitectura.

**ACEPTO:** productores internos de 4000/4036, constructores y layouts de
snapshots, tablas de conversión y remapificación software.
**RECHAZO:** identificar 3023 por un inmediato ajeno, borrar el bit31 de IDs
sin resolver OSAL, o convertir copia/configuración en captura electrónica.
**VEREDICTO: CAMBIOS** para cierre extremo a extremo y semántica física.
Sin `.git`: cambios sin commit.
