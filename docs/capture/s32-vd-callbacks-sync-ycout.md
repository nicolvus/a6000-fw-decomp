# S32 — callbacks VD y contrato parcial de SyncYCout (18-10-2026)

Análisis exclusivamente estático de ILCE-6000 3.21. Blob `av-cam.bin`, base
`0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Cada exportación verificó el archivo original y su igualdad con los bytes del
programa Ghidra antes de escribir resultados. Proyecto persistente
`analysis/ghidra/silent-liro.gpr`, siempre `-readOnly -noanalysis`.
Las definiciones/anotaciones auxiliares fueron temporales, con rollback explícito;
no se parcheó ningún byte ni se guardó el proyecto. Sin cámara ni firmware ejecutado.

## Resultado y corrección de S31

**CORRECCIÓN de [S31](s31-camera-main-sync-strings.md):** `0x43ad6034` contiene
código de despacho, no una tabla de callbacks. Sus destinos para las listas VD
se resuelven mediante un adaptador adicional. El log «YC out window overflow»
está en `0x4379bb90`, callsite `0x4379cb2e`, no en `0x435a9928`.
La rama YC transporta parámetros **y referencias a memoria compartida**;
no se puede reducir a contadores. Sigue sin cerrarse un descriptor de píxeles
con dirección/pitch/formato ni un fin de DMA.

Evidencia estructurada y todos los callsites:
[`s32-findings.json`](../../analysis/ghidra/s32-findings.json).
Pseudocódigo íntegro y ensamblador de las funciones solicitadas:
[`s32-final-verified.c`](../../analysis/ghidra/s32-final-verified.c) y
[`s32-final-verified.json`](../../analysis/ghidra/s32-final-verified.json).

## VERIFICADO — despachador, escritores y destinos

`0x43ad6034` lee dos palabras del objeto `q`:

- `q+0`: destino directo u offset de entrada virtual.
- `q+4`: ajuste firmado de `this` desplazado un bit, con flag virtual en bit 0.
- Si el flag es cero, destino=`q[0]`; si es uno,
  destino=`*(*(q+(signed(q[1])>>1))+q[0])`.
- Ajusta `r0=q+(signed(q[1])>>1)` y ejecuta `BLX r3` en `0x43ad604e`.

**INFERENCIA:** este esquema corresponde a un puntero a método C++ de ARM.
El algoritmo está verificado; el tipo original y los nombres Sony no están disponibles.
`0x43ad6052` es el thunk `B.W 0x43ad6034`.

Referencias directas al despachador: `0x43ad6052`, `0x437b6668`,
`0x437d0c18`. Al thunk: **26** saltos/llamadas directos en los bytes originales;
incluye `0x43ad60e6`, ausente del conjunto inicial de xrefs de Ghidra y seguido
en `0x43ad60cc`. No hay ocurrencias crudas del puntero absoluto al despachador
o a su thunk. El barrido cubre instrucciones Thumb B.W/BL alineadas a media
palabra y punteros absolutos, no cualquier cálculo de direcciones posible.
Listado completo en [`s32-raw-evidence.json`](../../analysis/ghidra/s32-raw-evidence.json).

**Construcción:** `0x43b03a74 → 0x4380f5b4 → 0x43acabf4` prepara 20 bytes:
`q[0]=0x43b03a49` (slot original `0x44023940`), `q[1]=0`,
`q[2]=función solicitada`, `q[3]=q[4]=0`.
`0x4379704c`/`0x43797090` copian estas cinco palabras y añaden argumento
en `+0x14` y propietario en `+0x18`.
`0x43ae98d0 → 0x43ae9888` obtiene un nodo y copia siete palabras a
`node+8..+0x20`; `0x43ae984c` enlaza el nodo y aumenta el contador.
La inicialización en `0x437970d4 → 0x43ae96c4 → 0x43ae96b8` prepara las listas.

| Estado | Rama | Lista / registro / ejecución | Destinos concretos recuperados |
|---|---|---|---|
| VERIFICADO | VD_Drive `0x4378f410` | `0x43e9d7a8` / `0x4379704c` / `0x437968b0` | `0x43811324`, `0x43b03abe` |
| VERIFICADO | VD_Post `0x4379210c` | `0x43e9d7e4` / `0x43797090` / `0x437967e8` | `0x438106ec`, `0x43810e7c`, `0x4381061c`, `0x4354a678` |

`VD_Drive` llama al ejecutor en `0x4378f620`; `VD_Post`, en `0x437924f0`.
Los ejecutores invocan el thunk en `0x437968ce` y `0x43796806` respectivamente,
con `r0=node+8`, `r1=*(r0+0x14)`.
El primer destino es **siempre el adaptador `0x43b03a48` para los objetos
construidos por esta ruta**: carga la función de `q+8`, pasa el argumento
de `r1` a `r0` y ejecuta `BLX` en `0x43b03a4e`.

Slots originales: `0x440259b4→0x43811325`, `0x44020ee4→0x43b03abf`,
`0x44026238→0x438106ed`, `0x44023820→0x43810e7d`,
`0x440204b4→0x4381061d`, `0x44021e0c→0x4354a679`.
El bit bajo indica Thumb; la tabla anterior usa entradas pares.
No se presupone que los slots ni el estado de las colas tengan un valor concreto
durante una ejecución real.

Se siguieron **todos los 26 callsites directos recuperados de los registradores**:
12 de Drive y 14 de Post. Productores completos exportados:
`0x43549380`, `0x43549e48`, `0x4354d740`, `0x4354fad8`,
`0x435503b0`, `0x435525c0`, `0x43554590`, `0x4380f754`.
Cada destino/callsite aparece en `registrar_callsites_by_real_target` del JSON.
No significa que todos se ejecuten en el mismo modo o frame.

Ramas nuevas seguidas: `0x43811324` (log `StSyncDvlpPrm`) llama a
`0x43aef4e8`, `0x43aeaf4e`, `0x437d9ae0`; `0x43810e7c` lleva el log
`IDT_Wk_Set`; `0x4381061c`, `JdgBBOut`; `0x4354a678`, `EndExps`.
Todos tienen pseudocódigo/ensamblador exportado. `0x43b03abe` señala evento
`0x1a/0x20`. Los nombres de logs no prueban efectos físicos.
La liberación del propietario (`payload+0x18`, método virtual `vtable+0xc`)
queda sin destino concreto: falta el objeto/vtable efectivo de ejecución.

## VERIFICADO y PARCIAL — SyncYCout y memoria compartida

`0x43796954` se exportó completa (372 líneas de pseudocódigo); llama a
`0x4379bb90` en `0x43796c96`, condicionada por `0x43ae916c()==0`.
`0x4379bb90` se exportó completa (671 líneas): estados de cuatro canales,
parámetros de imagen, rostro/seguimiento, metadatos, transporte y diagnósticos.
La longitud no es prueba semántica; ambos resultados tienen `error` vacío y
sus instrucciones/callsites están conservados en JSON.

**Productor nuevo `0x4379b44c`:** cambia el estado del canal a 2, obtiene una
referencia compartida del puntero `input+0x10` mediante `0x4390366c`
(callsite `0x4379b494`), y otra condicional desde `input+0xd4`
(`0x4379b4c6`). La función registra literalmente `MemoryHandle::AllocShare`;
usa `0x43902df8` y copia ID corto, palabra en `+4` y hasta cuatro pares de
palabras desde `+8` en un objeto de 0x28 bytes.

| Estado | Estructura/campo | Flujo demostrado |
|---|---|---|
| VERIFICADO | Handle compartido por canal | `0x43e9f0d8 + ch*0x28`; segundo en `0x43e9f2e8 + ch*0x28` |
| VERIFICADO | Bloque YC | `0x43e9f388 + ch*0x38`, 56 bytes |
| VERIFICADO | Bloque `+4` y `+8` | Copia de palabra `handle+4` e ID corto `handle+0` |
| VERIFICADO | Bloque `+0x14..+0x2a` | Copias/ajustes de semipalabras de geometría del productor |
| VERIFICADO | Bloque `+0x2e` | Remapeo del enum `input+0x38`: 0→2, 1→0, 2→1, 3→5, 4→3, 5→4 |
| PARCIAL | Dirección de píxeles, pitch y formato exactos | No identificados; el enum y las dimensiones no bastan para etiquetar un formato o stride |

`0x4379bb90 → 0x43a4941e` copia las **14 palabras** del bloque YC al
registro de mensaje. También serializa otros bloques mediante
`0x43a493cc`, `0x43b66058` y funciones enumeradas en los exports.
El mensaje compartido se obtiene vía `0x43903558`; `0x43b2a252` entrega su
dirección a través de `0x43561604`. El borrado de 0x20 bytes observado allí es
del bloque de mensaje recién obtenido; no identifica un raster de píxeles.

Los wrappers `0x43797afc`, `0x43797b10`, `0x43797b24`, `0x43797b38`
usan respectivamente objetos `0x43e9de9c`, `0x43e9de64`, `0x43e9dee0`,
`0x43e9df18`, y pasan ID de mensaje, ID corto y argumento a `0x435a9928`.
Esta última copia campos del pin a un registro de **0x34 bytes**, llama a
`0x435a9460` y envía vía `0x435aa20c` (asignación/copia/envío de mensajes).
No es el lugar del diagnóstico de ventana YC ni una rutina que copie píxeles.

**PARCIAL:** el bloque YC referencia una asignación DMM mediante un handle.
Para resolver el raster falta el handle efectivo en `input+0x10/+0xd4`, su
asignación/mapeo DMM y el significado de los pares de bloques; también falta
etiquetar ancho/alto/pitch/formato con evidencia del consumidor. No se ha
identificado una condición de fin de DMA ni un contrato de caché/propiedad.
Las llamadas indirectas no resueltas impiden afirmar ausencia universal de
accesos a imagen en todos los descendientes.

Se inspeccionó además `0x4379744c`: recibe mensajes de control `0x50004`
y usa `0x435a9b30` para configurar conexión/estado. No se deduce que ese
receptor consuma el payload YC. Falta la tupla remota efectiva de cada pin
en `+8/+0xc/+0x10/+0x14` para fijar un consumidor final; no se inventa esa arista.

## VERIFICADO — condición de ventana, no fin DMA

En `0x4379bb90`, después de un envío con resultado cero:

1. `0x4379caee` obtiene el reloj vía thunk `0x43ad5fba → 0x436cd00c`.
2. `elapsed = now - *(context[1]+8)`.
3. `0x4379cafa` compara con `*(context[1]+0x24)>>1`.
4. Excluye `context[2]+0x1d4` en {4,5} y `context[2]+0x1c == 4`.
5. `0x4379cb2e` imprime `elapsed>>1` y canal. Incrementa un contador limitado
   a cinco avisos adicionales en `0x43e9f468`.

Cadena completa desde `0x43ca519f`; la frase «YC out window overflow» empieza
en `0x43ca51ac`, offset de archivo `0x7641ac`.
El sufijo `%dus` es vocabulario del log; la unidad física del reloj no se midió.
No se consulta aquí ningún flag de DMA terminado, ni se hace poll de transferencia.

## Reproducción, límites y validación

Exportador: [`s32-scripts/S32Export.java`](../../analysis/ghidra/s32-scripts/S32Export.java).
Todos los logs `s32-*-headless.log` conservan el comando/argumentos del script
y el procesamiento read-only. Necesita `JAVA_HOME=tools/providers/jdk-21.0.12.1+1`.
La vista temporal trata `0x43541000..0x43bc0000` como código/pools constantes
para resolver PIC; RAM posterior queda escribible. No confundir esa hipótesis
del decompilador con una protección MMU observada.

[`s32-audit.py`](../../analysis/ghidra/s32-audit.py) verifica SHA, cobertura de las
siete funciones solicitadas, coincidencia de ramas Ghidra con bytes originales,
slots de punteros y cadena literal. `s32-integrity.json` conserva hashes de los
archivos persistentes: baseline capturado después de los primeros exports
read-only y comparación idéntica tras un export posterior; no es un snapshot
previo al inicio de toda la sesión.

Consultas exploratorias `0x43796522`, `0x435498ca`, `0x43549d42` fueron
fragmentos interiores: **no usar como entradas de función**. Se resolvieron
las entradas completas `0x43796518` y `0x43549380`.
`0x4379cdb0` era pool literal y no produjo función; se conserva el fallo
exploratorio. Los siete objetivos requeridos sí están decompilados completos.

Ruff/mypy del auditor: sin avisos. El comando solicitado `ruff check src tests`
detectó nueve avisos existentes en tests ajenos a S32, que no se modificaron;
`mypy --ignore-missing-imports src` pasó (cinco archivos).
Sin `.git` en este workspace: cambios sin commit ni push.

**NO_VERIFICADO:** fin físico de integración, DMA real, disponibilidad de un
YC nuevo y captura completamente electrónica. Ningún nombre/log sustituye
una observación en cámara.
