# Auditoría del repositorio — 23-10-2026

Base: `main` en `f4dc706262de807f6a9502cd5abc37af469747e0`. Cuenta GitHub activada y verificada: `nicolvus`. `git pull --ff-only`: ya actualizado. Árbol inicial limpio, sin archivos no ignorados pendientes. Los archivos ignorados (firmware, volcados, cachés y herramientas locales) no son trabajo pendiente por sí mismos.

## Alcance y criterio

Revisión estructural de todos los Python, JSON y Markdown versionados; pruebas locales; coherencia del censo y de Pages; integridad SHA-256 de originales y Ghidra; contraste de bytes de S382/S384 y de las trazas estructuradas S605–S627. No constituye reverificación semántica de cada conclusión de las cientos de sesiones. La presencia de cadenas no demuestra identidad funcional, equivalencia entre modelos ni duplicación de loggers.

## Hallazgos y acciones

| Veredicto | Hallazgo | Evidencia y acción |
|---|---|---|
| RECHAZO | S382: `0x7484dc` llama a `RecordStill::Execute` | Bytes `99 f5 ea e0` = `blx #0xe16b4`, dentro de PLT. El test aplicaba PC + inmediato × 2 a un destino ya absoluto. Retirado y reemplazado por regresión exacta. |
| RECHAZO | S382: `0x755af8` llama a `0x90de2c` | Bytes `86 f5 4e e3` = `blx #0xdc198`, también PLT. Retirado; `0x90de2c` no queda demostrado como entrada de función. |
| ACEPTO | Dos sitios BL hacia `0x90b248` | `0x90de2e`: `fd f7 0b fa`; `0x91634e`: `f4 f7 7b ff`. Las ventanas confirman llamadas; no prueban exhaustividad ni límites de función. |
| RECHAZO | S380/S381: PLT de 1914 entradas, por índice × 16; cero llamadas a registradores OSAL | El ELF tiene 2420 cuerpos ARM de 12 B y 391 veneers Thumb. Los `r_offset` son GOT; se resuelven los cuerpos hasta GOT y se regeneran ambos mapas. El barrido recupera 83/53 candidatos a los registradores síncrono/asíncrono. Corregidos tres scripts, añadida regresión y retirado el supuesto bloqueo dinámico. |
| RECHAZO | S384: cero MOVW #0x193, MOVT #0x40 para construir el ID | Encodings Thumb incorrectos y mitad alta equivocada: `0x40193 >> 16 = 4`. `40 f2 93 13` es MOVW r3,#0x193 y existe. Corregidos informe y tests. |
| ACEPTO | Negativo acotado para datos de `0x40193` | Sin palabra LE en `.rodata`/`.data` de A6000 y A7S; sin cadena ASCII. Corregido `.data` A7S: offset `0xefb9e0`, tamaño `0x736a0`, distinto de A6000. No demuestra ausencia del ID en flujo de código. |
| DUDOSO | Identificación de `RecordStill::Execute` en A7S | NO_VERIFICADO. Referencias PC-relativas: `0xcb6f2b` → `0x847e26`; `0xcb7bbb` → seis sitios `0x847f4e`…`0x84803a`. `.ARM.exidx` agrupa esos sitios en la candidata `0x847e1c..0x84814c`, prólogo Thumb y stack `0x358`, distinto del A6000. Falta comparar el contrato y el cuerpo para demostrar identidad de método. |
| RECHAZO | Direcciones publicadas de 94 trazas S605–S627 | Las 94 cadenas existen una sola vez; ninguna estaba en su dirección declarada. Corregidos 22 JSON y las direcciones coincidentes de sus informes desde `base + offset`. Regresión nueva contra bytes reales. |
| RECHAZO | Longitudes de prefijos en 21 JSON | Recalculadas desde la cadena literal; tests anteriores copiaban constantes equivocadas. Actualizadas sus expectativas y añadida validación contra los datos. |
| RECHAZO | Triaje automático equivale a revisión | Se reabren 141 clasificaciones automáticas como VIGENTE (pendiente de revisión). Se conservan 132 clasificaciones manuales anteriores, sin reafirmar su exactitud. Nuevas filas quedan pendientes; dos regresiones fallan antes del arreglo y pasan después. |
| RECHAZO | El tablero y el censo estaban sincronizados | El detalle tenía 58 hitos + 38 subetiquetas = 96, frente a 133 del resumen. Reconstruido desde títulos e informes: 94 + 39 = 133; 239 pendientes, 372 etiquetas. Esto mide cobertura documental de etiquetas, no funcionalidades verificadas. |
| RECHAZO | Solo existen ocho pruebas físicas propuestas | P1–P8, P9–P12 de S402 y P13–P21 del plan 2. Pages pasa a 21 propuestas, ninguna ejecutada dentro de estos planes. S64 es un antecedente distinto. |
| RECHAZO | Todos los JSON eran válidos | `analysis/s68_power/battery_power.json` usaba un literal hexadecimal sin comillas. Corregido a cadena hexadecimal. |
| RECHAZO | Rutas de tests portables y errores de lectura visibles | S108 y S600–S604 apuntaban a `/home/nicolas/Documentos/` en lugar del proyecto real. Los tests de exclusividad ignoraban el fallo de `strings` y lo convertían en cero coincidencias. Corregidas rutas desde `__file__` y lectura con `Path.read_bytes()`, también en sus copias de análisis. Los nueve casos antes fallidos pasan. |
| RECHAZO | Enlaces de análisis correctos | Reparadas rutas relativas de `docs/capture/` cuando el destino real existe. No se inventan documentos ausentes ni se modifican informes protegidos S1–S48. |
| DUDOSO | Semántica reciente S619/S622/S625 y logger dual | SENSER no demuestra sensor de imagen/audio; AVR no se identifica con AV rendezvous por compartir sigla; ADR es un campo de traza. Corregidas interpretaciones y marcados los límites. Las afirmaciones históricas de logger dual y equivalencia de código requieren xrefs/instrucciones. |
| ACEPTO | Originales y Ghidra preservados | Pasan los manifiestos `firmware.final.sha256`, `silent-liro.final.sha256` y `ghidra-dir.final.sha256`. |
| ACEPTO | Publicación remota de la base | La ejecución `39975391488` de «Publicar estado» terminó correctamente para `f4dc7062`. Ese flujo publica Pages; no ejecuta la suite de Python. |

## Validación y límites

- Inventario inicial: 1172 Python sin errores sintácticos; 3060 JSON revisados, un inválido corregido; 891 Markdown inspeccionados. El barrido de enlaces es heurístico: incluye ejemplos, fragmentos de código y archivo histórico, por lo que sus candidatos no equivalen a enlaces reales rotos.
- S380–S385 y regresión del PLT: 34 tests pasan tras las correcciones. No prueban por sí solos la semántica de todos los informes.
- Trazas S605–S627 y sus tests: 278 pasan; 19 casos de otros esquemas quedan fuera del validador nuevo.
- Conocimiento sin protocolo MCP: 65 tests pasan. Los seis tests de protocolo MCP pasan fuera del sandbox; dentro del aislamiento se bloquea su ejecutor de hilos. No se altera el servidor para ocultar esa limitación.
- Censo/Pages/batería: 28 tests pasan; S104 y atlas: 16 pasan.
- La colección global detecta ocho módulos bloqueados por `unicorn` ausente (S56–S61). No se instalaron paquetes ni se sustituyó esa dependencia con mocks para producir un verde artificial.
- Primera ejecución global disponible, excluidos protocolo MCP y esos ocho módulos: 3311 pasan, 35 omitidos, 1037 subtests pasan; cinco fallos y cuatro errores de rutas posteriormente corregidos y reproducidos en verde con sus nueve tests. Se conserva esta distinción entre ejecución global inicial y regresiones posteriores.
- Segunda ejecución global, con protocolo MCP fuera del sandbox y solo esos ocho módulos excluidos: **3326 pasan, 35 omitidos, 1037 subtests pasan**. El único fallo fue cobertura del triaje: el registro todavía correspondía al grafo anterior a la regeneración. Las filas nuevas se registraron como `VIGENTE`; la reejecución de los cuatro tests de triaje pasa. Por tanto, los **3327 casos disponibles** han pasado entre la ejecución global y la revalidación; no se afirma un único pase global íntegramente verde.
- Validación final del conocimiento completo (incluido MCP), PLT, trazas, S380–S385, censo, Pages y rutas S108/S600–S604/batería: **165 pasan, 19 omitidos**. Los omitidos del validador de trazas usan otros esquemas JSON y no se presentan como evidencia revisada.
- Ruff y mypy del código nuevo y del sistema de conocimiento pasan. Con las herramientas indicadas de GPREMIUM: mypy de `src` pasa; Ruff amplio de `src tests` conserva avisos históricos. Comparación final de los 47 Python tocados contra HEAD: 62 avisos antes, 39 después, **cero avisos nuevos**. No se reformatea código ajeno al arreglo ni se presenta el chequeo global como limpio.
- REA abrió `libObj.so`, SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`; la consulta exacta expiró a los 300 s. Se cerró la sesión al terminar. La evidencia decisiva anterior proviene de bytes y Capstone, no de una supuesta confirmación de REA.
- Se regeneran índice, grafo, correcciones, preguntas abiertas y Pages tras las modificaciones. Los totales de triaje pueden crecer al incorporar esta auditoría; VIGENTE significa revisión pendiente, no una nueva capacidad técnica demostrada.
- El grafo actual tiene cero entidades de función y cero relaciones CALLS. Su cobertura de relaciones documentales no equivale a un grafo completo de llamadas del firmware; las consultas vacías no certifican ausencia de llamadas.

## Pendiente verificable

1. Completar la identificación por cadenas/funciones de `RecordStill::Execute` A7S y los límites de los dos sitios A6000.
2. Rehacer el análisis de flujo del ID `0x40193`; el barrido histórico no justifica declararlo agotado ni exigir cámara.
3. Revisar manualmente las clasificaciones automáticas reabiertas y las atribuciones de logger dual/equivalencia de código de los módulos recientes.
4. Validar los esquemas de evidencia no cubiertos por `trace_strings`; un test que solo relee un JSON no certifica sus direcciones ni interpretaciones.
5. Resolver el entorno de emulación y ejecutar S56–S61 cuando esté disponible la dependencia autorizada. Sin firmware ejecutado ni pruebas físicas en esta auditoría.

VEREDICTO: CAMBIOS. Hay correcciones reproducidas y aplicadas; no se certifica todo el conocimiento histórico como verdadero.
