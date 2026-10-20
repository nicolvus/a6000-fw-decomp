# Puente de buffers SFRA → MPR — línea B

Investigación estática local, A6000 3.21, 16-10-2026. Sin cámara, ejecución
de firmware, instalaciones ni cambios de originales. Las direcciones LIRO son
VA lógicas; las direcciones de bibliotecas indicadas aquí son **VA ELF**.
Para repetir consultas en Ghidra se suma `0x10000` únicamente a estas últimas.

## Resultado y alcance de aceptación

**VERIFICADO:** el JPEG READY es una unidad DMM que Linux puede abrir y mapear.
El descriptor del protocolo SFRA **no es** un `StillInfo` y la API MPR Linux
trabaja con otra representación. **INFERENCIA:** los mismos bytes pueden
servir como imagen principal mediante conversión de descriptor y retención de
la memoria, o mediante una copia que desacople su vida útil. No se necesita
recomprimir para efectuar esa copia.

**NO VERIFICADO:** que MPR acepte sin cambios la sintaxis del bitstream de SFRA,
que se pueda omitir su SOI/APP o conservarlo íntegro, y que una fotografía así
produzca un archivo reproducible con los metadatos disponibles. Por tanto, la
aceptación fuerte «JPEG SFRA utilizable como mainJpg» **queda pendiente**. Este
documento concreta la conversión de memoria y los bloqueos; no presenta un
puente funcional validado.

## B-01 — comparación de estructuras

| Representación | Campos observados | Evidencia y estado |
|---|---|---|
| Entrada del gestor SFRA, 12 bytes, 12 entradas | `+0 u8 estado`, `+2 u16 handle`, `+4 u32 contador/orden de 24 bits`, `+8 u32 tamaño` | **VERIFICADO:** `0x43b62a5a`, `0x43b62d1c`, `0x43b62d42`, `0x43b62a24` |
| Respuesta GET_JPEG | Cabecera de `0x14` bytes y entradas de 8 bytes: `u16 handle`, `u16 ceil(tamaño/128)`, `u32 0x274` | **VERIFICADO:** `0x439a282c`; longitud total `0x14 + 8*n`, contador en `+0x10` |
| Buffer ISS mapeado, registro de `0x20` bytes | `+0 handle`, `+4 longitud anunciada`, `+8 offset de contenido`; `+0xc base mmap`, `+0x10 ajuste de página`, `+0x14 longitud mmap`, `+0x18 dirección física` | **VERIFICADO** para las asignaciones de `pubSfrGetJpeg(char**,uint*)`, ELF `0xce48`; `+8` se inicializa a cero en esta ruta. El último word no recibe una asignación útil demostrada |
| Imagen recibida por ISS en SET_PICTURE_INFO | JPEG: contador `+0x28`, handle `+0x2c`, tamaño `+0x30`, offset `+0x34`; EXIF y SCN en grupos que empiezan `+0x68` y `+0xa8` | **VERIFICADO:** ELF `0xe95c` y `0xb2c4`; otra ruta distinta de GET_JPEG |
| Notificación LIRO | Copia de `0x28c` bytes en mensaje tipo 4/id `0x1006`, a `+0x14` | **VERIFICADO:** `0x437efe78`, export existente `liro-notify-stillinfo.json` |
| `MPR::StillInfo` del API Linux | Bloque de `0x6b0` bytes, con áreas de dirección virtual y tamaño | **VERIFICADO:** libObj ELF `0x91bb58` copia `0x6b0` del elemento `0x3005`; libmpr ELF `0x73b064` serializa el bloque y luego lee las áreas apuntadas |

**DESCARTADO:** transportar literalmente la entrada de 8 bytes de GET_JPEG
como el descriptor de imagen principal. No incluye offset y su tamaño no es
el número exacto de bytes JPEG. El word `0x274` tampoco es una dirección ni
un tamaño: se reutiliza en la solicitud de asignación DMM de `0x439a2bd4`.
**NO VERIFICADO:** nombre formal de esa clase/pool.

**VERIFICADO:** ISS ELF `0xcc58` reconstruye `size = blocks << 7`, conserva
el handle de 16 bits y pide un JPEG. La diferencia con el tamaño original es
de 0 a 127 bytes. No se puede recuperar el tamaño exacto mediante la operación
inversa. **INFERENCIA:** un adaptador debe conservar el tamaño anterior al
redondeo o analizar la longitud real del stream.

**VERIFICADO:** el dumper de libmpr ELF `0x73b064` copia `0x6b0` bytes, y
`0x73abca` calcula un intervalo desde tres pares `(dirección,tamaño)` situados
a `+0x40`, `+0x48`, `+0x58` del subobjeto que recibe. El dumper le pasa
`StillInfo+8`: los pares están a `StillInfo+0x48/+0x50/+0x60`.
El helper `0x73adfc` relocaliza sus direcciones tras cargar una copia.
**NO VERIFICADO:** asignación nominal definitiva de los tres pares sin el
layout de A; no escribir offsets de `mainJpg` basándose sólo en su orden.

**VERIFICADO:** al cerrar esta línea no existía
`analysis/stillinfo-layout.json`. Se comprobó su presencia varias veces y no
se editó ningún archivo de A. La diferencia `0x28c`/`0x6b0` no demuestra por sí
sola dónde ocurre toda la conversión LIRO→Linux; falta ese tramo.

## B-02 — dominio DMM y resolución

**VERIFICADO:** la secuencia SFRA solicita una unidad mediante
`0x439a66fc`, mensaje de operación 1, pool de mensajes `0x61003c`, payload
de `0x50` bytes. El selector `0x274` llega desde `0x439a2bd4`. El handle
devuelto se guarda en la entrada del gestor; `0x43b63554` abre la unidad
mediante `0x439a6854`, operación 5. **NO VERIFICADO:** responsable último
del backing físico y traducción completa de `0x274` en el servicio DMM.

**VERIFICADO:** `0x439a23d0` extrae ese mismo handle para GET_JPEG. En Linux:

1. ISS `pubSfrGetJpeg` ELF `0xcc58` recibe el handle sin renumerarlo.
2. `MmapLiveViewJpeg` ELF `0x14568` llama a `pubMmap` ELF `0x1235c` con él.
3. `pubMmap` llama a `pubDmmOpenUnit` ELF `0x11e38`, operación DMM 5.
   La respuesta suministra dirección física y tamaño del extent.
4. Se alinea la dirección a página, se hace `mmap` y se devuelve
   `puntero = base_mmap + (dirección_física - base_física_de_página)`.

**VERIFICADO:** esto demuestra interoperabilidad LIRO→Linux del handle SFRA;
no es un puntero local LIRO ni un descriptor SDS YC. La entrada YC que usa SDF
y la unidad comprimida de salida son objetos distintos.

**NO VERIFICADO:** acceso directo de libmpr al handle crudo. Su entrada Linux
es `StillInfo` con áreas apuntadas; que ambos componentes hablen DMM no permite
omitir el mapeo ni asumir propiedad compartida. El hallazgo previo «mismo
dominio DMM, luego mainJpg acepta el handle tal cual» queda **DESCARTADO como
prueba suficiente**, aunque el handle sí llega a Linux.

## B-03 — propiedad, reutilización y caché

| Etapa | Acción y dueño observable | Estado |
|---|---|---|
| Asignación | SFRA busca EMPTY (`1`), obtiene handle y pasa a WRITE (`2`); puede reutilizar un READY (`3`) si faltan buffers | **VERIFICADO:** `0x439a2bd4`, `0x43b62d1c`, `0x43b62d42` |
| READY aún en SFRA | Puede ser reutilizado para escribir otro frame o liberado por limpieza | **VERIFICADO:** `0x439a2bd4`, `0x439a235c` |
| GET_JPEG | Busca READY y devuelve handle/tamaño; `0x43b62a40→0x43b62a24` deja EMPTY y handle `0xffff` | **VERIFICADO:** `0x439a23d0`. Se elimina la asociación al ring, sin liberar ahí el handle entregado |
| READY no entregados | GET_JPEG llama después a `0x439a235c`, que libera los restantes mediante `0x43b6358a` | **VERIFICADO:** no asumir que se conservan fotogramas antiguos pendientes |
| Apertura temporal LIRO | `0x439a68c0` abre (`0x439a6854`), consulta (`0x439a66dc`) y cierra (`0x439a6804`, operación 6) | **VERIFICADO:** esta consulta no es una retención adicional demostrada para MPR |
| Consumidor ISS | Antes del siguiente mapeo, hace `pubMunmap` y `pubDmmFreeUnit` del anterior | **VERIFICADO:** ELF `0xce48` y `0x14568` |
| Desmapeo ISS | `pubMunmap` ELF `0x12124` desmapea y cierra la unidad; liberar es otra operación | **VERIFICADO:** resolver PLT y no confundir close con free |
| MPR | La llamada pasa por `MprIf::WriteStill` y termina de forma asíncrona; `MprCtrl` espera la respuesta | **VERIFICADO:** libmpr ELF `0x71cfd6`, libObj ELF `0x8fe0a0`; devolución inicial no basta para liberar bytes |

**VERIFICADO:** LLVM Thumb confirma dos thunks diferentes:
`pubDmmFreeUnit` ELF `0x122fe` pasa segundo argumento 0;
`pubDmmCloseAndFreeUnit` ELF `0x122f0` pasa 2; ambos saltan al mismo wrapper
de `pubDmmFreeUnitSub` ELF `0x12170`. Este último envía operación 4 y ese
segundo argumento. La decompilación automática del thunk `0x122fe` extendió
incorrectamente sus límites; se descartó y se usaron sus instrucciones.

**INFERENCIA:** tras GET_JPEG hay transferencia de responsabilidad de liberar
al consumidor, coherente con la retirada del ring y la liberación explícita
de ISS. No equivale a una transferencia automática a MPR. Un uso simultáneo
por ISS y MPR requiere un contrato de retención o una copia; no liberar ambos
el mismo handle.

**NO VERIFICADO:** barrera de caché específica del productor SA→CPU y del
traspaso CPU→MPR. `pubMmap` usa protección 2 y flags 1 en la llamada observada
(`PROT_WRITE`, `MAP_SHARED` en Linux ARM); no aparece una invalidación explícita
en los wrappers examinados. Que el consumidor de fábrica lea el JPEG hace
plausible que el contrato DMM/driver la proporcione, pero no demuestra dónde.
No sustituirlo por un `msync` inventado ni afirmar coherencia validada.

## B-04 — EXIF, screennail y miniatura

**VERIFICADO:** GET_JPEG `0x439a282c` sólo añade entradas homogéneas
`{handle, bloques128, 0x274}`. ISS `0xcc58` solicita una y devuelve
`{handle, longitud_redondeada, cantidad}`. No hay tres listas ni campos
EXIF/SCN/thumb en esa respuesta observada.

**DESCARTADO:** las cadenas «jpeg/exif/scn count» como evidencia de metadatos
SFRA por fotograma. Sus referencias apuntan a `jobSetPictureInfoCmd` ELF
`0xe95c` y `jobSetPictureInfoOut` ELF `0xb2c4`; reciben tres grupos de handles
en otro mensaje y no los crean. `pubGetJpegData` ELF `0xf774` busca por una
clave y copia un registro `PictData_def` de la colección de fotografías; no
es el productor ni el GET_JPEG de SFRA.

**NO VERIFICADO:** contenido APP/EXIF interno del JPEG SFRA y ausencia global
de metadatos en otras rutas. Tampoco se identificó una miniatura independiente
entregada por GET_JPEG. `screenNail`, `thumJpg` y `exifSrcArea` no se deben
rellenar automáticamente con el mismo handle JPEG.

## B-05 — conversión y copia mínimas propuestas

**INFERENCIA — conversión de descriptor, sin copia de píxeles:** recibir
`(h,n128)` con `h != 0xffff`; abrir/mapear con el contrato DMM de ISS;
obtener `src = mmap_base + page_delta` (offset de contenido cero en esta
ruta), capacidad del extent y límite `R = n128 << 7`. Rechazar `R` fuera del
extent antes de leer. Obtener el tamaño exacto `L <= R` del productor o de un
parser JPEG; convertir la región a `(h, offset=0, size=L)` si se entra por el
adaptador LIRO, o a `(virtTopAddr=src, size=L)` si se entra por el API Linux
de MPR. El nombre/campo exacto de `mainJpg` lo debe fijar el layout de A.
Retener mapeo, unidad y estructuras hasta la respuesta final de MPR; impedir
la liberación automática del consumidor ISS durante ese intervalo.

**HIPÓTESIS — copia que elimina la dependencia de vida útil de ISS:**

1. Obtener y validar `src`, `R` y `L` como arriba mientras el handle está vivo.
2. Reservar una región independiente de al menos `L` bytes en el dominio de
   memoria admitido por el adaptador MPR. Si éste exige DMM, usar su asignador
   DMM y abrir/mapear la unidad destino; no la función homónima de ISS:
   `dmm_alloc_unit` ELF `0xaf98` y `dmm_free_unit` ELF `0xafd0` sólo hacen
   logging en este binario y no constituyen un asignador demostrado.
3. Copiar **exactamente `L` bytes**, `dst[0:L] = src[0:L]`, sin padding, sin
   conversión YC y sin nueva compresión. Descriptor destino: offset 0,
   tamaño `L`, handle destino para el adaptador por handles, o dirección
   virtual destino para la representación Linux.
4. Completar el contrato de visibilidad de memoria del asignador elegido;
   entonces cerrar/desmapear/liberar la fuente según ISS. Conservar el
   destino hasta fin de escritura o error de MPR y liberar una sola vez.

**NO VERIFICADO:** la copia anterior resuelve aislamiento y representación de
memoria, pero no prueba compatibilidad JPEG/MPR. Para encontrar `L`, un parser
debe respetar longitudes de APP/otros segmentos, SOS, escapes `ff00`, restart y
EOI; buscar el primer `ffd9` a ciegas puede truncar un APP. Si SFRA entrega un
stream completo y MPR exige otra envoltura, debe aplicarse la selección de
segmentos esperada por MPR después de demostrar ese contrato. No quitar SOI,
APP ni EOI por conjetura. Sin EXIF y layout válidos, no inyectar `0x1006`.

## Evidencia reproducible y límites

**VERIFICADO — fuentes:**

| Archivo | SHA-256 |
|---|---|
| `av-cam.bin` (perfil verificado por QuerySilentLiro) | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` |
| `libInfraStreamingServer.so` | `07158a3dc4d51adb4b7ff88efef6f095d51b989395f8674b9e2f2efe38b62d1f` |
| `libmpr.so` | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` |

Bibliotecas: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/`.
Reutilizados `analysis/ghidra/sfra-jpeg-{seq,open,open2}.json`,
`sfra-msg-helpers.json`, `libmpr-writestill.json`,
`libobj-{recordstill-exec,writestill-callers}.json` y
`liro-notify-stillinfo.json`.

**VERIFICADO — repetición:** copiar `a6000-libs.gpr/.rep` y
`silent-liro.gpr/.rep` a un directorio privado; usar `analyzeHeadless` con
`-process`, `-noanalysis`, `-readOnly`, `-scriptPath analysis/ghidra`.
Para bibliotecas, `DecompAt.java salida.json <VA_ELF+0x10000+bitThumb>`;
para LIRO, `QuerySilentLiro.java salida.json 0x<VA>` verifica el hash.
Importar ISS sólo en la copia si no existe; no ejecutar autoanálisis global.
Consultas nuevas: las entradas nombradas en las tablas y secciones anteriores.
La copia privada se eliminó después; no se modificaron proyectos compartidos.
Los JSON temporales no son salidas permanentes de esta línea.

**VERIFICADO — contraste independiente:** `readelf -Ws/-rW` para nombres y
PLT, `llvm-objdump -d --triple=thumbv7` para los thunks ISS `0x122f0..0x1230c`,
el mapeo `0x14568..0x1466c` y el helper MPR `0x73abaa..0x73abc8`.
Consultas exploratorias con direcciones MPR mal trasladadas `0x00467810` y
`0x00467f92` de Ghidra se descartaron: las válidas usadas para sus helpers son
`0x00457810/0x00457f92`. No interpretar pseudocódigo con `unaff_*` como ABI.

**VERIFICADO — validación:** investigación documental, sin código nuevo ni
tests de implementación. Mypy solicitado: éxito, 5 archivos fuente. Ruff
solicitado: 9 avisos preexistentes en `tests/test_elf_xrefs.py`,
`test_fm3_gpio_literals.py`, `test_imx210_modes.py` y `test_sfra_outcalls.py`;
no se tocaron ni se corrigieron. Ningún aviso nuevo por esta entrega Markdown.
No se actualizan README/CONTEXT/docs ajenos por el contrato específico de B.
No hay repositorio Git utilizable (`git status`: not a git repository), sin commit.

**NO VERIFICADO — bloqueos para cerrar aceptación:** (1) layout nominal de A
y adaptador `0x28c→0x6b0`; (2) sintaxis exacta JPEG requerida por mainJpg;
(3) retención DMM y mantenimiento de caché; (4) metadatos mínimos de MPR.
**INFERENCIA — siguiente tarea:** resolver el productor del elemento Linux
`0x3005` consumido por libObj ELF `0x91bb58` y seguir la imagen principal hasta
`WriteDcfMemory`, contrastando SOI/APP/EOI. Esa traza decide entre entregar el
JPEG completo o adaptar su envoltura; copiar memoria por sí solo no lo decide.
