# S40 — origen de context[0]+0x24/+0x48/+0x458 y frontera IMX210

18-10-2026. **PARCIAL:** origen de API y copias de los tres campos recuperados;
no se demuestra exhaustividad universal de escritores ni equivalencia con
FPS, exposición o formato de píxel. La rama estática sigue abierta.

## VERIFICADO — método e integridad

Lectura limitada a CURRENT, CONTEXT breve, informe S39 y final de PROGRESS;
sin releer S31–S38. Aplicadas knowledge-navigation/contradiction-audit:
`search.py claim docs/capture/s39-image-format-apl.md` no registra correcciones;
esto no garantiza ausencia de correcciones en prosa.

Único proyecto `analysis/ghidra/silent-liro.gpr`, proceso `av-cam.bin`, siempre
`-readOnly -noanalysis`. No se crean funciones, tipos, referencias ni
transacciones. Se reutiliza `S39Export.java` para exports con prefijo `s40-`;
su comentario S39 identifica el exportador, no una sesión anterior del resultado.
`S40Scan.java`, `S40Tables.java` y `S40Snapshots.java` solo consultan el programa.
Los exports de funciones/tablas cotejan SHA y todos los bytes cargados.

SHA-256 antes/después:
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Manifiestos persistentes `s38-project-before.sha256` y `s38-rep-before.sha256`
comprobados antes y después. No se guarda el proyecto; no se modifica firmware.

Evidencia primaria: `analysis/ghidra/s40-{origin,writers,source,api,dispatch,
snapshots,aliases,derived}.json` y sus `.c`; tablas literales en `s40-tables.json/.c`,
inventarios en `s40-offset-xrefs.json` y `s40-offset-all-xrefs.json`.

## VERIFICADO — raíz, staging y escritores por copia

Se conserva la identidad S39: raíz `R=0x43e9b548`, contexto `0x43e99208`,
`context[2]=0x43e9baec`. Objetivos absolutos:
`R+24=43e9b56c`, `R+48=43e9b590`, `R+458=43e9b9a0`.

`0x43792d84/43792d9e` entrega R a `0x43804c5c`. Esta función **sobrescribe
el bloque completo de 0x560 bytes**, no solo los campos con xrefs individuales.
La copia incluye los tres objetivos. Fuente staging `S=0x43edf684`:
literal `43804d70` más PC `43804cde`; getter `43804de8` devuelve S.

| Hallazgo | Dirección exacta | Origen/efecto | Estado |
|---|---|---|---|
| Copia staging→raíz | `43804cdc`, longitud en `43804cd4` | `memcpy(R,S,0x560)`, rama sin snapshot activo | VERIFICADO |
| Copia alternativa→raíz | `43804c82` y `43804d12` → `43b00d06` | `memcpy(R,objeto+8,0x560)` | VERIFICADO |
| Selección de alternativa | `43b00cba` | byte `objeto+0x57c`; no es habilitación del sensor demostrada | VERIFICADO |
| Alimentación del snapshot | `43b00cd0` | copia argumento 2 a `objeto+8`, longitud `0x560` | VERIFICADO |
| Inicialización del snapshot | `43b00bba` | cero en `objeto+4`, longitud `0x564`; cubre los tres campos relativos a `objeto+8` | VERIFICADO |
| Excepción local de VD_Pre | `437935ae` | `R+48=0`, independiente del staging | VERIFICADO |

`43b00cd0` también conserva `0x564` bytes de `objeto+4` en `objeto+0x6c4`
si `objeto+568==1`. Sus llamadores recuperados son `43804cc8`, `43806a80`
y `43806d50`; estos dos últimos están dentro de `438069f0`. La familia
`43b00b48..43b010a0` está exportada íntegra para distinguir metadatos,
snapshots y subestructuras. No llamar a todas ellas registros del IMX210.

Procedencia inmediata del snapshot alternativo, contrastada con listado:
`43804cc8` recibe **S** (`literal43804d68+PC43804cca=43edf684`), no R;
`43806a80` recibe `mensaje+4` en case 1 de `438069f0`;
`43806d50` recibe `mensaje+8` en case 10 y `objeto+568==2`.
Por tanto los campos del segundo caso vienen de `mensaje+28/+4c/+45c`,
y los del tercero de `mensaje+2c/+50/+460`. Son bloques de configuración
aportados al gestor, no constantes locales. El productor original de esos
mensajes y su eventual elección de tablas sigue PARCIAL.

## VERIFICADO — escritores anteriores y procedencia API/constante

| Campo staging → raíz | Escritor exacto | Procedencia | Clasificación |
|---|---|---|---|
| `S+24=43edf6a8` → `R+24` | `438040bc`, handler `43804058` | byte `solicitud+0x0a`, ampliado a u32; comando `0x4000` | VERIFICADO: API, no valor fijo |
| Mismo campo | `438040e8` | cero bajo condición de estado en un objeto consultado por GOT; no se atribuye significado al flag | VERIFICADO: constante condicional |
| `S+48=43edf6cc` → `R+48` | `43803958`, handler `4380394c` | byte `solicitud+0x09`, ampliado a u32; comando `0x4036` | VERIFICADO: API |
| `S+458=43edfadc` → `R+458` | `43809378`, handler `43809148` | byte `solicitud+0x0e`, ampliado a u32; comando `0x3023`, si byte `+8 != 0` | VERIFICADO: API |
| `R+48` | `437935ae` | cero en la rama VD_Pre ya diferenciada en S39 | VERIFICADO: constante condicional |

El hilo `437fee08` recibe mensajes en `437fee12` (ver listado exportado),
despacha tipos 0/2 hacia `43809148` en `437feeaa`, y tipo 5 hacia
`438052d8`. El comando del mensaje se lee como u16 en `solicitud+2`;
la cabecera ocupa al menos 8 bytes. No se demuestra qué acción de interfaz
de usuario origina cada mensaje ni que un valor sea FPS.

Las xrefs exactas de S+24 contienen las dos escrituras anteriores; S+48
contiene una escritura y lecturas en `438038d8`; S+458 no tiene xrefs
absolutas, aunque el escritor por getter está demostrado. Este último caso
es evidencia concreta de que xrefs vacías **no** significan ausencia de escritor.

## VERIFICADO — layouts recuperados

La tabla de despacho está en `0x43fff30c`, 220 filas (`0xdc`), stride
`0x0c`. `438052f4` lee la clave; `43805300/43805302` cargan/invocan el
handler; `43805304` comprueba el byte de control. Se exportan los 12 bytes
de **cada** fila; los bytes no consumidos no reciben tipos semánticos inventados.

| Offset de fila | Tamaño | Interpretación demostrada |
|---|---|---|
| `+0` | 2 | comando u16, compara con solicitud+2 |
| `+2` | 2 | bytes observados, significado no establecido |
| `+4` | 4 | puntero Thumb al handler, incluye bit 0 |
| `+8` | 1 | si no cero evita llamada posterior `4375dcd4` |
| `+9` | 3 | bytes observados, significado no establecido |

Filas relevantes: `43fff30c`: `4000→43804059`, flag 1;
`43fff564`: `4036→4380394d`, flag 1;
`43fff7e0`: `4074→43804e09`, flag 0 (paquete agregado, sin atribuirle
los tres campos por proximidad). `0x3023` pertenece al otro switch,
no se inventa una fila suya en esta tabla.

| Offset en S/R | Tamaño escrito | Fuente en solicitud 3023 |
|---|---|---|
| `+450` | u32 | u8 `+8` |
| `+454` | u16 | u16 `+0xa` |
| `+456` | u16 | u16 `+0xc` |
| `+458` | u32 | u8 `+0xe` |

Para selector `+8==4`, el handler puede sustituir `+450/+454/+456` por
`1` y dimensiones desde `context[10]+80/+82`, o por `3,320,240`.
No sobrescribe `+458` en esas ramas. **INFERENCIA:** configuración alternativa
con geometría, por el par 320×240 y la copia de dos dimensiones; los nombres
precisos de modo y formato siguen NO_VERIFICADO.

Tabla independiente de selección en `0x43ca3c21`: cuatro bytes
`01 01 00 01`; `43794a44` exige bit 7 de `context[2]+269`, comprueba
`R+450` en 1..4 y lee `tabla[(R+450)-1]`. Esto decide si tomar R+458;
no es una tabla de secuencias de integración del sensor.

## PARCIAL — cobertura, alias y controles separados

Se consultaron xrefs de lectura/escritura de R, contexto, objetivos y staging;
se siguieron PIC de bases y llamadores del getter. Barrido del listado Ghidra:
215 candidatos con operandos `450/454/458`; ampliación a `24/48` produce
8977 candidatos (incluye pila y estructuras ajenas). El inventario conserva
dirección, función e xrefs por instrucción. No se filtran solo los cuatro
sitios de S39, que escriben **context[2]+28**, no estos tres campos fuente.

Otras coincidencias de offset, por ejemplo `43ad06a0` (empaqueta dos valores
de 16 bits), `43b3736a` (par de palabras en otro objeto construido desde
`4391d2f0`) y `438149e8` (objeto con bloque de 24 bytes en +468), **no se
añaden como escritores de R sin demostrar identidad de puntero**. Sus cuerpos
y llamadores quedan exportados; atribuirlos a R por el número 458 sería inválido.

No hay prueba universal frente a bases desplazadas, stores múltiples, código
no definido o llamadas indirectas sin resolver. La familia de snapshots y los
escritores de staging concretos quedan resueltos; atribuir cada productor del
argumento 2 de `43b00cd0` a una solicitud original sigue **PARCIAL**.
Esto es trabajo estático pendiente, no una frontera estática agotada.

| Control | Evidencia S40 | Estado |
|---|---|---|
| Configuración de exposición/integración | Ningún enlace cerrado desde estos tres campos a SetExposure/registros de integración | NO_VERIFICADO |
| Habilitación de lectura | `objeto+57c` selecciona fuente de snapshot; no prueba SetRead ni enable físico | NO_VERIFICADO para sensor |
| Generación de datos/cuadro | Copia de configuración y selección de enum no prueban adquisición ni escritura de píxeles | NO_VERIFICADO |
| Configuración software por API | comandos 4000/4036/3023 y copias anteriores | VERIFICADO |

**ACEPTO:** procedencia configurable por API de los tres campos, ceros
condicionales y layouts observados. **RECHAZO:** considerarlos constantes
universales del firmware o identificar detección de cambio APL con un registro.
**RECHAZO:** concluir exposición, read-enable o generación de cuadro solo por
recibir una solicitud. No se reabre AllocShare/AllocRendezvous.

## Pendiente real y próximo paso exacto

Pendiente: contrato externo de los bytes de comandos `4000/4036/3023`,
productores del snapshot alternativo y cobertura de alias no resueltos.
No está demostrado que sean opciones del usuario, FPS o nombres de píxel.

Próximo paso exacto: seguir el productor de los mensajes case 1/10 de
`438069f0` (copias `43806a80/43806d50` desde mensaje+4/+8), conservando
offsets de snapshot `+8/+24/+48/+458` frente a los del contenedor. En paralelo
conceptual, seguir consumidores del bloque `+450..+458` ya resuelto hacia
selectores de modo IMX210; solo asociar SetMode/SetExposure a un valor cuando
coincidan objeto, campo y sitio de llamada. La rama no se declara agotada y
no se justifica sustituirla por búsquedas genéricas del sensor.

## Validación

Auditor `analysis/ghidra/s40-audit.py`: primero falla por findings ausente;
después valida SHA, manifiestos, exports, copia `0x560`, tabla/handlers y
tabla de selección. Auditor PASS; Ruff auditor PASS; mypy src/auditor PASS.
Ruff src/tests conserva nueve avisos previos en cuatro tests ajenos sin tocar.
Pytest conocimiento: 67 PASS. Mantenimiento obligatorio de cinco pasos:
1455 entidades / 2772 relaciones en paso 2 y paso 5, grafo estable.
Integridad SHA y manifiestos persistentes PASS al cierre.

**VEREDICTO: CAMBIOS** para exhaustividad de alias y semántica IMX210;
aceptada la procedencia API/copia de los campos demostrados. Sin `.git`,
cambios sin commit. Sin ejecución de firmware, cámara, flasheo, instalaciones ni push.
