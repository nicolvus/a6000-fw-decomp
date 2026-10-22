# Progreso — sistema de conocimiento Sony A6000

## Investigación S140 — mapa de registros IMX210

- Objetivo acotado: enumerar el vector `0x43fe995c` y revisar los dos rangos de filas de 16 bytes sin asignar semántica física.
- REA Evidence del vector: `ev_3e4a16b351da4229205a68b4225aedf7ff70d9edb3e89440d91314576341614b`; `0x43b0893c`: `ev_b376d03662f3edddb3c528e4fa223070270ef09dbc71e5ef8ccc7d012e05857b`.
- Resultado: 119 punteros, cero terminador en `0x43fe9b38`; los rangos BSS examinados están a cero; selector `S[0]` indexa fila y copia a `S+0xc4`. No se recupera el contenido runtime.
- Artefactos: `analysis/s140_imager_regmap/{extract_regmap.py,imager_regmap.json}`, `tests/test_s140_imager_regmap.py`, `docs/capture/s140-imager-register-map.md`.
- Verificación: unittest del hito 3/3 y suite `tests/knowledge` 67/67 PASS; `git diff --check` PASS. Commit `6f064d93` publicado en `origin/main`; no se incluyeron archivos ajenos S138/S139.
- Siguiente paso exacto: seguir selectivamente `0x43843a44` por REA/bytes desde una sesión que mapee las direcciones virtuales, identificando stores de `S[0]` y origen de la fila, sin tocar la asignación física.

## Investigación S141 — selección de fila y límite del origen runtime

- Objetivo: confirmar selección/copias de fila y determinar si REA podía cerrar el store/condiciones del selector.
- REA `0x43b0893c`: `ev_b376d03662f3edddb3c528e4fa223070270ef09dbc71e5ef8ccc7d012e05857b`; caller `0x43b08750`: `ev_b1bd068317fa32b2167455cc5189065e7d50b48f6e99b20ffde5dd250cfd3513`; constructor `0x43849fb8`: `ev_158664de14075207b8688292074cd88ef3ba64d4e12caeac876ffc695254c9f9`.
- Resultado PARCIAL: bytes confirman `S[0]`→`S+4+16·índice`→copia 16 B a `S+0xc4`; `0x43849fb8` copia las 4 palabras a la salida. `0x43843a44` no quedó resuelto por REA; eso no es evidencia de ausencia. Stores, gates y cadena G→S siguen abiertos.
- Artefactos: `analysis/s141_imager_row_trace/{verify_instructions.py,row_trace.json}`, `tests/test_s141_imager_row_trace.py`, `docs/capture/s141-imager-row-copy.md`.
- Pruebas: 3/3 unittest PASS, suite S140+S141+knowledge 73/73 PASS; `git diff --check` PASS. Commit `47147952` publicado en `origin/main`.
- Siguiente: localizar una coordenada Thumb aceptada por REA para el código candidato `0x43843a44`; seguir únicamente stores de `S[0]` y transferencias G→S, con contraste de bytes.

## Investigación S142 — xrefs directas al estado S

- Pregunta: qué significan las dos referencias directas REA a `0x43eb35d0` y si revelan el escritor del selector.
- Evidencia REA: xrefs `ev_c003561cd210577dc1bc7acc5d8edee0f20991a28f194009e2bd8d4f278b19ab`; función de memset `0x437b5614`, lector `0x437b59b8`, thunk `0x43b08748`, consumidor `0x4383c638`; Evidence IDs adicionales y límites en `docs/capture/s142-imager-s-init.md`.
- Resultado: VERIFICADO reset de 0x148 B a cero; VERIFICADO lectura/consumo de `S+0xda`; PARCIAL para escritor `S[0]` (xrefs directas no cubren aliases/punteros argumentos).
- Artefactos: `analysis/s142_imager_s_init/{verify_s_accesses.py,s_accesses.json}`, `tests/test_s142_imager_s_init.py`, `docs/capture/s142-imager-s-init.md`.
- Pruebas: unittest S142 3/3; suite S140–S142 + knowledge 76/76 PASS; `git diff --check` PASS. Commit `bf199b15` publicado en `origin/main`.
- Siguiente: REA para recuperar coordenada de procedimiento Thumb de staging `0x43843a44` y seguir el store al selector.

## Investigación S145 — gap de procedimiento en el staging

- Objetivo: determinar si REA asigna un procedimiento a `0x43843a44` y si hay caller alternativo con entry observable.
- REA Evidence: `resolve_containing_procedure(0x43843a38)` → `FUN_43843a38` `ev_5c7ff69e20724a19d3273ec66911ffab44d75d2d245c9f19b102447a114121b6`; `0x43843a44` → `not_in_procedure` `ev_ea22a2182a4e3d23312394b402b358789ae6a158f2c91f4dd012453fd50de7ed`; caller/callsite fuera de procedimiento `ev_1a8bf1980c534d35a1e20f267840577c270f73f4cd59c18c6df98299d631737a`/`ev_bf964a553c23c814671cdfb6585c400508017bf07914746b9f4ab0cb1b420ac1`.
- Bytes REA corroborados: prólogo `ev_1341f2fcb0c98ed30d51646e21fd980c2c7fdd917c14493817665a26e707173a`; BL `ev_51665d015dc585c586b3ef325ee488b0a7dbe64ea0c74cf3f7519e63649a6336`; staging candidate `ev_f6cf7574b2e3b18fcec3ebf5f5fc14bbfd36049e3fdc90b9ac37a20541919ebb`.
- Resultado PARCIAL: bytes demuestran una llamada codificada, no ejecución. El código candidato queda en zona no representada por funciones REA, así que no hay pseudocódigo/call graph para el store a S[0].
- Artefactos: `analysis/s145_imager_unanalyzed_code/{verify_code_gap.py,code_gap.json}`, `tests/test_s145_imager_unanalyzed_code.py`, `docs/capture/s145-imager-code-gap.md`.
- Pruebas: unittest S145 3/3 PASS; suite S140–S143/S145 + knowledge 79/79 PASS; `git diff --check` PASS. Commit `a0955258` publicado en `origin/main`.
- Siguiente (revisado por S146): recorrido estático reproducible de bytes REA en `0x437b617e`/`0x43843a44`; la superficie disponible no permite sembrar funciones.

## Investigación S146 — capacidad REA para selectores de offset

- Pregunta: si `procedure_pseudo_code`/`procedure_info`/`procedure_assembly` admiten entradas no reconocidas vía selector `file-offset:` o si existe capacidad de seeding.
- Resultado: `procedure_pseudo_code` mapea offset y falla explícitamente si no hay procedimiento; `procedure_info`, `procedure_assembly`, `analyze_function` rechazan ese selector; no hay herramienta de crear procedimiento/entry en la sesión actual. No se mutó sesión ni artefacto.
- Evidencia: error de cobertura `ev_ea22a2182a4e3d23312394b402b358789ae6a158f2c91f4dd012453fd50de7ed`; mapeo staging `ev_adf4d88907eb3ff81fba796af3f1ddac9680ffe4aded30e67aa18febd79e3417`; caller real `ev_26bca5083b40a7c16bcf21eec1635a774c20532c95739f7acd57aa3649d06ad7`; offset equivocado `0x27617e` → `0x437b717e`, procedimiento no relacionado `ev_b0d6874334a9baa4823bb7b150b77290a5434ef146c37fcd58858065b1babd63`.
- Artefactos: `analysis/s146_rea_seed_capability/{verify_offsets.py,rea_seed_capability.json}`, `tests/test_s146_rea_seed_capability.py`, `docs/capture/s146-rea-seed-limit.md`.
- Pruebas: unittest S146 3/3 PASS; suite S140–S146 + knowledge 82/82 PASS; `git diff --check` PASS. Commit `0a865472` publicado en `origin/main`.
- Siguiente: recorrido estático de bytes con `read_bytes` REA para localizar stores/gates, o mover a otra pregunta independiente; no repetir `file-offset:` como seeding.

## Investigación S147 — referencias y writer de filas G

- Pregunta: clasificar cinco xrefs REA a `G+0x224` y comprobar si alguno escribe las cuatro filas.
- Evidencia REA: xrefs `ev_7375812f6a63afe1d0db14b91c6cec50187e7d53a2f6bd7a4436500fb2ec9df0`; builder `0x4383bf2c` `ev_5305a4dbabf37e02baec4bd8b258137d9e733c0817ce4b373defe5a8ecc12203`; writer `0x4383c9dc` `ev_cd6567d4fb0af5c12b4d8d21ee30a574ca5bd289cfba828745757f185d89ecb2`, pseudocode paginado `ev_d4653d3615add43984db5b04eb31c812b23d2a5865e6038908736caf291fd05a` + `ev_9caa8366dd8aa3149c26482110e5523aa6132b3fd299d39fb05de95a2003380e`.
- Resultado: un path observado escribe en cuatro filas 16 B, offset base `G+0x224+0x2c`, stores relativos 0/4/6/a/c/e; no se atribuye semántica física. Los otros xrefs son pasos/lecturas; por cobertura limitada se conserva PARCIAL.
- Artefactos: `analysis/s147_imager_g_rows/{verify_g_rows.py,g_rows.json}`, `tests/test_s147_imager_g_rows.py`, `docs/capture/s147-imager-g-rows.md`.
- Pruebas: unittest S147 3/3 PASS; suite S140–S147 + knowledge 85/85 PASS; `git diff --check` PASS. Commit `ffdba84b` publicado en `origin/main`.
- Siguiente: revisar helpers `0x4383bfd4`, `0x4383c818`, `0x43b08786` para cerrar escrituras faltantes por evidencia, sin semántica física.

## Investigación S149 — auditoría de helpers por fila

- Pregunta: si cuatro helpers del builder modifican `+8/+9` u otros campos de filas; verificación adversarial del número de iteraciones del writer.
- Corrección interna: el primer pase S149 confundió la vuelta inicial con el loop completo; instructions y bytes muestran count=4, `r4+=0x10`, `bne.w` al loop head. `0x4383c9dc` escribe las cuatro filas; no se afirma que solo se modifique una.
- Helpers/gates auditados: `0x4383b790`, `0x4383bfd4`, `0x43b08786` si `[G+0x50]==2`, `0x4383c818` si `[GOT+0xca]==1`. No tienen stores en `+0x2c..+0x6b`; S149 acota que no existen en esos cuerpos, no globalmente.
- Evidencia del loop: `read_function_instructions` `ev_05541f7fa796e9902a584d283765f42028aa618772a3ece2a2b2e519b172211b`; pseudocode page 1/2 y cada dossier/helper en S149 report. Los bytes `0x4383c9ec`, `0x4383cbfa`, `0x4383cbbe` se reproducen desde el blob.
- Artefactos: `analysis/s149_imager_row_helpers/{verify_helper_stores.py,row_helper_stores.json}`, `tests/test_s149_imager_row_helpers.py`, `docs/capture/s149-imager-row-helpers.md`.
- Pruebas: unittest S149 3/3 PASS; suite S140–S149 + knowledge 88/88 PASS; `git diff --check` PASS. Commit `c4193a2a` publicado en `origin/main`.
- Siguiente: búsqueda de writers alternos de los bytes `G+0x234/+0x235` (hueco relativo +8/+9 del primer row), con REA/bytes y sin inferir ausencia por scans vacíos.

## Investigación S150 — xrefs directas y literales a los gaps

- Pregunta: xrefs directas para los ocho bytes `+8/+9` de las filas y presencia de palabras absolutas con esos destinos.
- Resultado parcial: 8/8 xrefs exactas vacías; REA control positivo a la base de una fila; bytes BSS cero. Búsqueda de imagen completa encontró dos words `0x43eb0850` en `0x4400812c`/`0x4400b27c`; son literales dentro de datos sin xrefs/instrucción consumidora identificada. No convertirlo en lectura/escritura efectiva.
- Evidencia: xrefs exactas `ev_c42a7d7fd9a1e599c8d0b74992d387d3f1e7164896d259abe3a6ef0f7e68f68c` … `ev_55c7c05551f922a8af96f3b4d7dbae64da5be5e55e55eacc780eb55d0149416b`; control `ev_afcfff7678cf182ee835cd1ed4dfd1b2f55fdb0872a6bfc51817b3a9ab9f3b55`; búsqueda literal completa `ev_201b0a5e0f16fe153da29642e861f41b0a7cebeb611865db65540927452d7668`.
- Artefactos: `analysis/s150_imager_row_gaps/{verify_gap_refs.py,gap_refs.json}`, `tests/test_s150_imager_row_gaps.py`, `docs/capture/s150-imager-row-gaps.md`.
- Pruebas: unittest S150 3/3 PASS; suite S140–S150 + knowledge 91/91 PASS; `git diff --check` PASS. Commit `feb767e5` publicado en `origin/main`.
- Siguiente: identificar consumidores de las celdas `0x4400812c` y `0x4400b27c`; seguir el word inicial `0x43eb0850` con REA xrefs/lecturas y evidencia de índice/call path.

## Investigación S152 — consumidor del descriptor gap

- Pregunta: si los literales en dos tablas de descriptores alcanzan un consumidor que lee/escribe el byte de gap.
- Resultado: tablas A[32]/B[6] se decodifican `{id=0x30,size=1,addr=0x43eb0850}`. `FUN_43858338` selecciona formato raw/hex; raw `FUN_43b09c7a` lee desde addr y copia a buffer; size=1 implica lectura de un byte. Sin store al origen en ese copiador. Gates de runtime dependen de dos bits y permanecen PARCIAL.
- Evidencia REA: tabla A `ev_f8bd0f66f1e8d90f997d6ea0c37e47e3911c40c8dc9de66f9652bfca536f4289`, B `ev_01d929687b87aa4343c193261123044fac8ffad3ae264dda33a77826adfffa90`, copiador `ev_2d31ad1d2d49ace2985775034cfc294bb17251c7e6930056dfb4cb9c47716ffa`, hex formatter `ev_6efbdb9318dab3f4c890adbbc9f1e066ffa8905d6ccb639967336a706653e212`.
- Artefactos: `analysis/s152_imager_descriptor_reads/{verify_descriptor_reads.py,descriptor_reads.json}`, `tests/test_s152_imager_descriptor_reads.py`, `docs/capture/s152-imager-gap-descriptor-read.md`.
- Pruebas: unittest S152 3/3 PASS; suite S140–S152 + knowledge 94/94 PASS; `git diff --check` PASS. Commit `024bb46f` publicado en `origin/main`.
- Siguiente: localizar escritores de flags `0x43f72d05&2` y `0x43f72d08&0x20`; no reabrir asignación física del byte gap.

## Investigación S153 — gates del volcado de descriptores

- Pregunta: localizar escritores y condiciones de los bits `0x43f72d05&2` y `0x43f72d08&0x20` que gobiernan el volcado del byte gap.
- Resultado PARCIAL: instrucciones verifican lecturas/tst/beq en `0x438583b0`/`0x438584f0`; xrefs exactas a ambos bytes son solo los lectores del dispatcher. El estado está a cero en la imagen. No hay escritor reproducible ni valor runtime confirmado; no se declara ausencia global.
- Evidence: función/cuerpo `ev_74804f459247fbbe0d22d0b1e7e58bba3e8ee690e33a1b6d20ffacc7020ba7fc`; refs byte+3 `ev_2988fcffcf7768198b5e5d25f616294bfa4ee489710012b6f85b06434aabfde4`; byte+6 `ev_7a31d71d07dc687daced9c48fe2a917ae8a24bf330dd09d4cb5d966c77a1669a`; BSS bytes `ev_498f8dc63dab90ff677e302176e0737dcbb3d54be6fc4bc97ad00cafe4ce158d`.
- Artefactos: `analysis/s153_imager_dump_gates/{verify_gates.py,dump_gates.json}`, `tests/test_s153_imager_dump_gates.py`, `docs/capture/s153-imager-dump-gates.md`.
- Pruebas: unittest S153 3/3 PASS; suite S140–S153 + knowledge 97/97 PASS; `git diff --check` PASS. Commit `7ce7f329` publicado en `origin/main`.
- Siguiente: inspeccionar consumidores/copiadores del bloque state `0x43f72d02` para detectar escrituras estructuradas a +3/+6; no equiparar xrefs vacíos con ausencia.

## Investigación S154 — clasificación del xref a estado

- Pregunta: qué instrucción representa `0x438363e6` a `0x43f72d02` y si su procedimiento escribe los gates.
- Resultado: `ldr r0,[r5,r3]` lee el slot GOT `0x4401f990`; segundo edge DATA apunta al valor base, no a un store/read directo del objeto. La función lee campos +0x38..+0x3b y escribe en otros targets; no hay store +3/+6 en ese procedimiento. PARCIAL global.
- Evidencia: instructions `ev_98aa775d3c95df94438bb40d89c729bddd5b0493c30968d146bfee6243fb3c63`; typed refs `ev_e8a264c61f10ca8c40c32e8171a4b743ec4bfa571f23898386dd5ab4a8ec7efa`; slot `ev_ef0ae04fe4e640945736ea7bd40211f7cbdc4dbc7865e58ec0051c994f67bc7f`.
- Artefactos: `analysis/s154_imager_state_ref/{verify_state_ref.py,state_ref.json}`, `tests/test_s154_imager_state_ref.py`, `docs/capture/s154-imager-state-ref.md`.
- Pruebas: unittest S154 3/3 PASS; suite S140–S154 + knowledge 100/100 PASS; `git diff --check` PASS. Commit `9030811f` publicado en `origin/main`.
- Siguiente: seleccionar otro xref de base y clasificar con typed references/instructions, buscando stores estructurados a los flags.

## Investigación S155 — lectores/accesores del estado

- Pregunta: clasificar `0x43857f90`, `0x43857fb0`, `0x43858134` frente a estado/gates.
- Resultado: dos readers de `+0` como predicados; el tercero carga la base desde GOT y lee +4/+1c, stores a otras estructuras. Ninguno escribe +3/+6 dentro de su procedimiento. Sin conclusión global.
- Evidencia REA: funciones `ev_50ec9a795fdeee1871d4df7045a9bc37b0e30b6187a21faef21c2d7d3fd3734a`, `ev_671901b96f062bf27c18b5a5db2b60b04f8131fde5cb02090e128ff818624502`, `ev_b38e559657d05b6ab4a57389988c5f11f0adae407c47ecaa4e30cd3bfccd740c`; refs tipadas `ev_9975507315e3e9ae8b0b12ed371553fbde517212c7deab61373a08b5fdd07e0c`, `ev_8af01bde84b54dc562aa3f33aacbc80ffbc8e7e2ca7f89e26e51b8143ca3dd92`, `ev_8e30d1b8e05356a533217a31f3da3ec92df520c6aa1e9eb79cca3dbd31c18132`.
- Artefactos: `analysis/s155_imager_state_readers/{verify_state_readers.py,state_readers.json}`, `tests/test_s155_imager_state_readers.py`, `docs/capture/s155-imager-state-readers.md`.
- Pruebas: unittest S155 3/3 PASS; suite S140–S155 + knowledge 103/103 PASS; `git diff --check` PASS. Commit `d0888afd` publicado en `origin/main`.
- Siguiente: clasificar un próximo xref restante, manteniendo alcance local.

## Investigación S157 — accesores de snapshot del estado

- Pregunta: clasificar `0x43859954` y determinar stores a gates en el procedimiento contenedor.
- Resultado PARCIAL: instrucción `ldr r2,[r4,r3]` carga base del objeto desde GOT; edge a base es PARAM, no write. Procedimiento lee +5/+0xf y escribe a otros destinos, sin stores a +3/+6 en ese cuerpo.
- Evidencia REA: función `ev_ec6f97762141815f395c4f95495973ab27f5327ae5c1aab1c33e5f7593780ece`, refs `ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d`, slot `ev_a2be1dc38d7278043336827bd87c0991eeccbd13742659906de531563db077dd`.
- Artefactos: `analysis/s157_imager_state_snapshot/{verify_snapshot_ref.py,snapshot_ref.json}`, `tests/test_s157_imager_state_snapshot.py`, `docs/capture/s157-imager-state-snapshot.md`.
- Pruebas: unittest S157 3/3 PASS; suite S140–S157 + knowledge 106/106 PASS; `git diff --check` PASS. Commit `6d8680c8` publicado en `origin/main`.
- Siguiente: inspeccionar otro xref al estado, distinguiendo base-pointer loads de field writes.

## Investigación S158 — spill del puntero en xref de estado

- Pregunta: clasificar `0x4385b268` en `FUN_4385b234` y ver si escribe gates.
- Resultado: `ldr` previo obtiene objeto desde GOT; el xref es `str r3,[sp,#0x20]`, edge de valor/stack, no store a `0x43f72d02`. El cuerpo lee +0x26/+0x28/+0x29 y escribe otros objetos; no gates +3/+6 en el cuerpo.
- Evidencia REA: función `ev_633b2499c1f64a98ef9dd1dee3a8785a4eb185e877a01886c8f80b10ecfb5551`, instrucción `ev_a1843181423095ac768e124db07db27e4259ffb8776b681caea4238fdb06414e`, refs `ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d`.
- Artefactos: `analysis/s158_imager_state_ref/{verify_gate_accessor.py,state_accessor.json}`, `tests/test_s158_imager_state_ref.py`, `docs/capture/s158-imager-state-ref.md`.
- Pruebas: unittest S158 3/3 PASS; suite S140–S158 + knowledge 109/109 PASS; `git diff --check` PASS. Commit `3affd7cc` publicado en `origin/main`.
- Siguiente: clasificar xref restante a base, evitando confundir edge al valor con acceso a memoria.

## Investigación S159 — segundo spill del estado

- Pregunta: clasificar `0x4386001c` y el uso posterior del puntero a `0x43f72d02` en su procedimiento.
- Resultado: `FUN_4385fff0` lee el GOT slot y derrama `r3` a `[sp+0x1c]`; lee +0/+0x1c/+0xa2 y stores a otros targets. Ningún store a +3/+6 en ese cuerpo; no se infiere ausencia global.
- Evidencia REA: contenedor `ev_5b0f148005650c3e22de895825765d726859466967149bcff370c3d43ddd1f73`; instrucción `ev_3c2f0fbe550810719bf22e531025709d7c0ca323e91ab8635e60f9afca166181`; referencias `ev_eb099b43bb1c2559ab27672e7a60d390533927b72af8b8a486614aaee8090843`; slot `ev_ef0ae04fe4e640945736ea7bd40211f7cbdc4dbc7865e58ec0051c994f67bc7f`.
- Artefactos: `analysis/s159_imager_state_ref/{verify_state_spill.py,state_spill.json}`, `tests/test_s159_imager_state_ref.py`, `docs/capture/s159-imager-state-spill.md`.
- Pruebas: unittest S159 3/3 PASS; suite S140–S159 + knowledge 112/112 PASS; `git diff --check` PASS. Commit `98262cd6` publicado en `origin/main`.
- Siguiente: escoger un xref restante, preferiblemente uno con typed WRITE directo, y verificar si base-pointer edge es spill u objeto efectivo.

## Investigación S160 — writer de `state+0`

- Pregunta: clasificar la referencia `0x4383ac90` a `0x43f72d02` y su condición local.
- Resultado VERIFIED local: slot GOT `0x4401f990→0x43f72d02`; `strb r3,[r2,#0]` WRITE a `state+0`, valor 0 cuando expira el contador. No escribe +3/+6. Callers estáticos encontrados, sin prueba dinámica.
- Evidencia: procedure `ev_134be2dfce4598770fe1825386a5899cfad96fb794784e8673a5c3f42e37bd3b`; WRITE instruction `ev_3992433ca320c9303ec5bd74990f7e8e53f481516afd812000138c8654f83014`; pseudocode `ev_d9486547d0d47dc8039f483cc2e75d37bee5fd8e82c1044c8d033137462f0946`.
- Artefactos: `analysis/s160_state_open_flag_writer/{verify_open_flag_store.py,open_flag_store.json}`, `tests/test_s160_state_open_flag_writer.py`, `docs/capture/s160-state-open-flag.md`.
- Pruebas: unittest S160 3/3 PASS; suite S140–S160 + knowledge 115/115 PASS; `git diff --check` PASS. Commit `0a7daba9` publicado en `origin/main`.
- Siguiente: analizar otro xref al estado con mismo criterio tipado; priorizar stores/copia a +3/+6 si aparece ruta.

## Investigación S161 — segundo spill en el objeto de flags

- Pregunta: clasificación local de `0x4384cb06/0a` dentro de `FUN_4384b268`.
- Resultado: `ldr.w r3,[r8,r3]` carga el puntero GOT; `str r3,[sp,#0x20]` lo derrama en pila. Luego lee +0x40/+0xa5/+0x42; stores a otros destinos, no gates +3/+6 en el cuerpo.
- Evidencia REA: procedimiento `ev_1e8e048eb0f0141cf4d85e3688d89fe80dba6b0653e5ad1a7171f615be7c3de4`; instrucciones `ev_e619946dcb53ed41e95f05e0c71ea3c2c80e31a62fec960cff765160d0789e49`; refs `ev_3303b18d85c46c4e2f17bbd020bc6d05f0c6ea1dcb7fee814e779e672f12ab01`.
- Artefactos: `analysis/s161_imager_state_spill/{verify_state_spill.py,state_spill.json}`, `tests/test_s161_imager_state_spill.py`, `docs/capture/s161-imager-state-spill.md`.
- Pruebas: unittest S161 3/3 PASS; suite S140–S161 + knowledge 118/118 PASS; `git diff --check` PASS. Commit `0a26c130` publicado en `origin/main`.
- Siguiente: clasificar otro xref pendiente por edge tipado y destino efectivo.

## Investigación S162 — lectores de `state+0x1c`

- Pregunta: clasificar xrefs `0x438d933e/9378` al estado y sus efectos.
- Resultado: ambos usan `ldrh [state+0x1c]`; devuelven default 3 si cero y almacenan el halfword en `0x43f7c702/704`. No escriben state/gates en esos dos cuerpos. “Notificación” queda INFERENCIA; alcanzabilidad PARTIAL.
- Evidencia: xrefs `ev_4db80d5468d11118561f766f8d8699b7d85f44889d368fd8c5eacd01aae0454d`; lectores `ev_02d7e5d7893000bd111b30f25f386665394b5759bfb5ae161c19b78576267719` / `ev_59bc79c25846b1f1541a2e92f6dc4702c4546864117f903afa9c76c5a9ee6dfd`.
- Artefactos: `analysis/s162_imager_state_event_readers/{verify_state_event_readers.py,event_readers.json}`, `tests/test_s162_imager_state_event_readers.py`, `docs/capture/s162-imager-state-event-readers.md`.
- Pruebas: unittest 3/3 PASS; falta suite/commit/push.
- Siguiente: clasificar otro xref restante con evidencia de edge y bytes.

Checkpoint persistente. Actualizar al terminar cada etapa, antes de continuar
con la siguiente. No reescribir historial: añadir entradas nuevas.

## Fases (ver plan completo en el mensaje del usuario, 2026-10-18)

| # | Fase | Estado |
|---|------|--------|
| 1 | Validar/mejorar indexación FTS5 existente | COMPLETA |
| 2 | Indexación jerárquica (estilo PageIndex, sin dependencia) | COMPLETA |
| 3 | Grafo de conocimiento en SQLite | COMPLETA |
| 4 | Reconciliación de hallazgos (S19–S30, Darwin, EFCS, GPIO, WriteStill) | COMPLETA |
| 5 | Recuperación adaptativa (router de métodos) | COMPLETA |
| 6 | CLI unificada + servidor MCP | COMPLETA |
| 7 | Skills compartidas Claude/Codex | COMPLETA (ver caveat de verificación) |
| 8 | Memoria persistente / checkpoints de sesión | COMPLETA |
| 9 | Benchmarks reproducibles | COMPLETA |
| 10 | Validación final | COMPLETA |

## Archivos creados hasta ahora

- `scripts/knowledge/index_docs.py` — indexador incremental SHA-256 → SQLite FTS5
  + tablas jerárquicas `documents`/`nodes` (Repositorio→Subsistema→Documento→Sección).
  IDs estables = sha1(path::heading::occurrence)[:16]; no dependen del orden global.
- `scripts/knowledge/search.py` — CLI: `exact` (ripgrep), `text` (BM25),
  `tree` (navega subsistema/documento/sección sin cargar cuerpo),
  `section` (recupera texto original por rango de líneas, sin duplicar contenido en la DB).
- `tests/knowledge/test_index_docs.py` — 4 tests unittest, verdes (roundtrip, incremental,
  poda de borrados, jerarquía+recuperación exacta).
- `.knowledge-cache/knowledge.sqlite` — DB regenerable (gitignorada): 355 documentos,
  2684 secciones/nodos, 32 subsistemas (derivados de los 2 primeros componentes de ruta).
- S107 — `Camera::CamCore` y la pila `ResourceStack` (31-10-2026, línea general)
  - Hecho: integración del hito S107 (subagente `nemotron-3.5-lightning-free`) **con revisión**.
    37 cadenas `[CAMCORE]` en A6000 fw3.21, rango `0x43c905ca` → `0x43cebcb2`; **0** en A7S fw3.20.
    Subsistemas: SGC (3), RDC/PFR (8), AIF (7), Memory/Resource (2), ExlHelper (5), DMA Setter (6),
    Powersave (1), Defect correction (2). 4 strings de ResourceStack dentro de `[IMAGING_CAP]` S106
    (vaddrs `0x43ca10d1` → `0x43ca120f`). RTTI confirmado: `N6Camera7CamCore8RdcImageE` (0x43c906b6),
    `N6Camera7CamCore13SplitRdcImageE` (0x43cb0b94). Diferencial A7S: etiqueta de instrumentación.
    - Informe: `analysis/s107_camcore/camcore_resources.md` + JSON (`camcore_resources.json`).
    - Tests: `tests/test_s107_camcore.py` 8/8 verdes (conteos, direcciones, textos, RTTI, A7S diff).
    - Nota breve: `docs/capture/s107-camcore-resources.md`.
    - Script reproducible: `analysis/s107_camcore/scan_camcore.py`.
  - Abierto: semántica exacta de SGC; formato interno de ResourceStack; 2 ExlHelper sin xref PIC;
    significado de `loadDefectPos` con bytes binarios.
  - Relacionado: S104 (`CAMCORE` entre 6 prefijos S104), S106 (ResourceStack consumo en IMAGING_CAP),
    S84 (sa_func_* interacción), A7S fw3.20 comparación.
- `.venv/` + `knowledge/requirements-dev.txt` — entorno aislado con ruff/mypy/pytest.

## Fase 3 — Grafo de conocimiento (detalle)

- `scripts/knowledge/build_graph.py` — añade tablas `entities`/`relations` a la MISMA DB
  (no hay sistema paralelo). Dos fuentes, ambas deterministas:
  1. **Function/CALLS** desde JSON con forma `{binary, sha256, address_space, symbol_value,
     original_name, outgoing}` (detectado por forma, no por ruta fija). Una relación CALLS
     solo se crea si el nombre del destino en `outgoing` coincide EXACTAMENTE con el nombre
     de otra entidad del MISMO binario (misma sha256); si no hay coincidencia exacta se
     descarta (no se inventan destinos). Con los 3 dossiers reales: 3 entidades, 1 relación.
  2. **CORRECTS/SUPERSEDES** desde Markdown: busca palabras clave que los propios
     investigadores ya escribieron (CORRECCIÓN/corrige, superad[ao]/supera) línea por línea
     (no por sección completa — una sección larga como el índice del README NO genera
     relaciones falsas solo por contener la palabra en otro punto). El objetivo se resuelve
     por: (a) enlace Markdown en una ventana de ±2 líneas alrededor del marcador, o
     (b) referencia de sesión (`sesión N`/`SN`) en la MISMA línea del marcador (no en la
     ventana: el número de sesión del encabezado de la propia sección no debe colarse como
     objetivo — bug real detectado y corregido con test de regresión). Si una referencia de
     sesión es ambigua (más de 2 documentos candidatos), se descarta en vez de adivinar.
  - Cada relación guarda: `owner_source` (archivo que la genera; al reindexar/eliminar ese
    archivo se regeneran/eliminan solo sus relaciones, incluyendo huérfanos de archivos ya
    borrados), `source_path`, rango de líneas, `status` (del vocabulario controlado,
    detectado en el texto si está presente, `NO_VERIFICADO` por defecto) y `evidence`
    (cita textual literal).
  - Con los datos reales: 31 relaciones CORRECTS/SUPERSEDES (antes de la corrección del
    bug de ventana: 410 — la mayoría falsos positivos por proximidad de sección completa).
- `scripts/knowledge/search.py` gana `graph` (relaciones entrantes/salientes de un doc,
  con evidencia) y `claim` (conclusión vigente de un documento: qué lo corrige/supera).
  Verificado con consultas reales del plan: "¿qué corrigió S28?" → S23/S25 con cita exacta;
  conclusión vigente de S27 → corregido por README y superado según CONTEXT.md.
- `tests/knowledge/test_build_graph.py` — 4 tests: filtrado CALLS por nombre+binario exacto,
  no-confusión encabezado-vs-cuerpo en referencias de sesión, resolución por enlace Markdown
  + consulta de conclusión vigente, y poda de relaciones al eliminar el documento que las originó.

## Fase 4 — Reconciliación (detalle, PARCIAL)

Hecho y verificado:
- Respaldo íntegro de `CONTEXT.md`: `docs/history/CONTEXT.md.2026-10-18.bak` +
  `docs/history/CONTEXT.md.sha256.orig`. Verificado con `sha256sum -c --strict` → OK,
  y `diff` contra el original → idéntico.
- `scripts/knowledge/export_corrections.py` (nuevo): genera `docs/CORRECTIONS.md` (31 filas,
  derivado de `relations` tipo CORRECTS/SUPERSEDES) y `docs/OPEN-QUESTIONS.md` (382 filas,
  secciones con marcador NO_VERIFICADO/CONFLICTO_PENDIENTE vía FTS5). Documentos regenerables,
  marcados "no editar a mano". Test de regresión: `test_export_corrections.py` (1 test), verde.
- `docs/STATE.md` (nuevo): estado breve con enlaces a fuentes canónicas ya existentes
  (no reinterpreta nada, solo cita y enlaza): corrección Darwin base ROM 0x4200,
  SetImageWrited 0x1007 (no 0x1009), mapeo GPIO P4D/P4E/P4C/P4B, EFCS→IMX210, y la tabla
  de flujos completos/incompletos de `docs/estado-y-viabilidad-2026-10-17.md`.

Completado también:
- `CONTEXT.md` reducido de 1263 a 116 líneas: conserva verbatim solo S28–S30 (investigación
  activa) + punteros a `docs/STATE.md`, `docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md` y al
  historial íntegro. **Verificación de integridad:** `sha256sum` de
  `docs/history/CONTEXT-full-2026-10-18.md` (copia legible íntegra) coincide EXACTAMENTE
  con el hash original pre-edición (`5bd41bb4...`) — ningún contenido se perdió, solo se
  reubicó. El `.bak` binario-idéntico se conserva aparte.
- **Bug de auto-contaminación detectado y corregido:** al reindexar el propio
  `docs/CORRECTIONS.md` (que por diseño contiene la palabra "CORRECTS" y decenas de enlaces),
  el grafo generaba 121 relaciones circulares a partir de su propio export. Corregido
  excluyendo `docs/CORRECTIONS.md`/`docs/OPEN-QUESTIONS.md` de la extracción como fuentes
  primarias (`GENERATED_DOCS` en `build_graph.py`), con test de regresión que verifica
  reconstrucción estable (idempotente) tras reindexar los documentos generados.
- Total final estable tras dos pasadas consecutivas: 39 relaciones CORRECTS/SUPERSEDES,
  3 entidades Function, 1 CALLS. `docs/CORRECTIONS.md` y `docs/OPEN-QUESTIONS.md` regenerados.

No hecho (límite de alcance, no omisión):
- No se añadieron extractores para los JSON con esquema distinto al de `dossiers.json`
  (ver límite documentado en Fase 3): GPIO/IMX210/REA no están en el grafo todavía.

## Fase 5 — Recuperación adaptativa (detalle)

- `search.py ask <consulta> [--budget N]` (nuevo): clasifica la consulta con
  `classify_query` — `identifier` (dirección hex o símbolo sin espacios) → `exact`;
  `doc` (ruta `.md`) → relaciones entrantes (`claim`) + árbol (`tree`); `concept`
  (texto libre) → BM25 (`text`) + correcciones relacionadas de cada resultado vía grafo.
  Deduplica por `(ruta, línea)`, recorta por presupuesto de caracteres configurable
  (`--budget`, por defecto 2000) e informa cuántos resultados se mostraron vs. el total.
- Robustez corregida: `ask` ahora degrada sin fallar si `build_graph.py` no se ha
  ejecutado todavía (tabla `relations` ausente) — bug real encontrado por el test
  de regresión al indexar sin construir el grafo primero.
- `tests/knowledge/test_adaptive_search.py` (nuevo, 5 tests): clasificación de los
  3 tipos de consulta + recorte por presupuesto con aviso de truncado.
- Verificado con consultas reales: `ask "0x932a44"` (identifier), `ask
  "docs/capture/s27-effect-postprocess-rewire.md"` (doc), `ask "Darwin base ROM"`
  (concept, con corrección relacionada vía grafo incluida automáticamente).
- Total suite tras esta fase: 15/15 tests, ruff/mypy sin avisos.

## Fase 6 — CLI unificada + servidor MCP (detalle)

- CLI unificada: `search.py` ya cubre exact/text/tree/section/graph/claim/ask (fase 5);
  no se creó un entrypoint adicional porque multiplicaría comandos sin necesidad
  (`index_docs.py`/`build_graph.py`/`export_corrections.py` son operaciones de
  mantenimiento separadas a propósito, ejecutadas explícitamente, nunca disparadas
  desde una búsqueda de solo lectura).
- `scripts/knowledge/mcp_server.py` (nuevo): servidor MCP de solo lectura con el SDK
  oficial `mcp==2.3.0` (API `MCPServer`, antes `FastMCP` en mcp 1.x — instalado en
  `.venv/`, versión fijada en `knowledge/requirements.txt`). **No reimplementa lógica**:
  cada tool captura la salida de la función `cmd_*` correspondiente de `search.py` vía
  `contextlib.redirect_stdout` — una sola fuente de verdad para CLI y MCP.
  9 tools: `search_exact`, `search_documents`, `search_hybrid`, `find_symbol`,
  `get_document_section`, `query_graph`, `find_corrections`, `get_open_questions`,
  `get_current_state` — exactamente las operaciones mínimas pedidas, sin duplicar.
- **Verificado de verdad, no solo importado:**
  - `tests/knowledge/test_mcp_server.py` (4 tests) usa el servidor real en memoria:
    `list_tools()` confirma que las 9 herramientas se descubren vía protocolo MCP;
    `call_tool("search_exact", ...)` y `call_tool("get_current_state", ...)` devuelven
    datos reales del repositorio; una llamada con parámetro fuera de rango
    (`direction="sideways"`) no tira el servidor.
  - Arranque real por stdio: `python3 scripts/knowledge/mcp_server.py < /dev/null`
    sale con código 0 y sin stderr (smoke test de inicialización del transporte).
- Integración de clientes:
  - **Claude Code:** `.mcp.json` en la raíz del proyecto (nuevo), apunta al Python del
    venv del proyecto — no se tocó ninguna configuración MCP previa (no existía ninguna).
  - **Codex:** su configuración MCP vive en `~/.codex/config.toml` (fuera del proyecto,
    global del usuario); no se modificó un archivo global sin instrucción explícita.
    Snippet exacto para que el usuario lo añada si quiere usar el mismo servidor desde Codex:
    ```toml
    [mcp_servers.sony-a6000-knowledge]
    command = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/.venv/bin/python3"
    args = ["/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/knowledge/mcp_server.py"]
    ```
- Total suite tras esta fase: 19/19 tests, ruff/mypy sin avisos.

## Fase 7 — Skills compartidas (detalle)

- Fuente canónica única: `.claude/skills/{knowledge-navigation,contradiction-audit,
  knowledge-maintenance,session-checkpoint}/SKILL.md`. `.agents/skills/*` son enlaces
  simbólicos relativos a esa fuente (`ln -s ../../.claude/skills/<nombre> ...`),
  confirmado que no son copias divergentes: `readlink -f` de cada uno resuelve al
  archivo canónico real.
- Solo 4 skills, no las ~10 que enumera el plan original: se consolidaron
  `firmware-evidence`+`context-retrieval` dentro de `knowledge-navigation` y
  `graph-navigation` dentro de `contradiction-audit` porque todas invocan los
  mismos 2-3 scripts (`search.py`, `build_graph.py`) — crear una skill por
  subcomando de CLI habría sido redundante sin aportar procedimiento distinto.
  NO se crearon `firmware-comparison` ni `retrieval-benchmark`: no existe todavía
  una herramienta de comparación de firmware ni un harness de benchmarks que
  esas skills pudieran describir honestamente (ver Fase 9 pendiente).
- `CLAUDE.md` y `AGENTS.md` de proyecto (nuevos, no existían): breves, solo
  apuntan a las skills y a `knowledge/PROGRESS.md`/`docs/STATE.md`, sin duplicar
  contenido técnico.
- Validación estática de las 8 rutas (4 canónicas + 4 symlinks): frontmatter
  `name`/`description` presente y bien formado en todas — verificado con un
  parser real, no solo "se ve bien".
- **Caveat honesto de verificación:** no se pudo confirmar el descubrimiento EN
  CALIENTE por un Claude Code o Codex reales, porque esta misma sesión ya había
  cargado su listado de skills antes de que estos archivos existieran, y no hay
  forma de reiniciar la sesión desde aquí para re-listarlas; tampoco hay un
  binario de Codex disponible en este entorno para lanzarlo. Queda pendiente que
  el usuario confirme en una sesión nueva que `/knowledge-navigation` (u otro
  nombre de invocación de su cliente) aparece en el listado.

## Fase 8 — Memoria persistente / checkpoints (detalle)

- `scripts/knowledge/checkpoint.py` (nuevo): checkpoints estructurados JSON en
  `knowledge/checkpoints/` (directorio ya existía, vacío desde la Fase 1). Campos
  obligatorios según el plan: goal, done, files, findings, evidence, corrections,
  tests, blockers, next_actions, permissions_state. Nunca se edita el JSON a mano:
  se crea con flags de CLI (`create --goal ... --done ... --file ... ...`).
- `list`/`latest`/`show <id>` para leer sin tener que abrir archivos JSON directamente.
- **Bug real encontrado y corregido:** el timestamp inicial tenía resolución de
  segundo; dos checkpoints creados en el mismo segundo se ordenaban por el sufijo
  UUID aleatorio en vez de por orden de creación, así que `latest` podía devolver
  el equivocado. Corregido con microsegundos en el timestamp; test de regresión
  (`test_list_and_latest_reflect_created_checkpoint`) que crea dos seguidos y
  verifica el orden.
- `tests/knowledge/test_checkpoint.py` (3 tests: campos completos, list/latest,
  show por id parcial). Total suite: 22/22, ruff/mypy sin avisos.
- Primer checkpoint real creado: `knowledge/checkpoints/2026-10-18T05-10-01-412803Z-fe6147e3.json`,
  cubre las fases 1-8 de esta misma sesión con hallazgos, archivos, tests y bloqueos reales.

## Fase 9 — Benchmarks (detalle)

- `scripts/knowledge/benchmark.py` (nuevo): 7 consultas de referencia reales
  (SetImageWrited por dirección y por código corregido, GPIO cortinillas, EFCS,
  Darwin base ROM, comparación A6300, corrección de S27), cada una con una
  verdad de referencia fijada MANUALMENTE antes de ejecutar el script (ver
  campo `note` por consulta) — nunca "lo que el propio sistema devolvió".
  Compara ripgrep crudo sobre todo el repo vs `search.py text`(FTS5)/`exact` vs
  `ask` (adaptativo), midiendo latencia real, líneas, caracteres y una
  estimación de tokens (caracteres/4, marcada explícitamente como aproximación:
  no hay tokenizador real en este entorno). Salida regenerable:
  `knowledge/benchmarks/report.md` + `.json`.
- **Bug real encontrado y corregido durante la propia ejecución:** 2 de 21
  comparaciones daban "fallo" porque el snippet BM25 resalta coincidencias
  insertando `[corchetes]` DENTRO del token (`1ST_[CURTAIN]_MG`), rompiendo la
  subcadena esperada (`1st_curtain_mg`). El sistema sí encontraba el documento
  correcto (verificado manualmente); el defecto estaba en el criterio de acierto
  del benchmark, no en la recuperación. Corregido quitando `[`/`]` antes de
  comparar. Resultado final real: **21/21 aciertos**.
- Resultado honesto más relevante (sin inventar porcentajes): para consultas
  conceptuales, ripgrep crudo sobre todo el repo devuelve decenas de MB (p. ej.
  "darwin-rom-base": 191.760.545 caracteres, ~47.9M tokens estimados) porque
  coincide con logs de sesiones de cientos de miles de líneas; `search.py text`
  (FTS5) y `ask` devuelven ~2-3 KB (~250-670 tokens estimados) para la MISMA
  consulta, con el documento correcto entre los primeros resultados. La
  reducción es una consecuencia medida de indexar por sección en vez de grepear
  archivos completos, no una optimización ad-hoc para la demo.
- `tests/knowledge/test_benchmark.py` (1 test, verifica estructura del reporte
  con un corpus de prueba pequeño, no valores absolutos que dependen de la
  máquina). Total suite: 23/23, ruff/mypy sin avisos.

## Fase 10 — Validación final (detalle)

Ejecutado en una sola pasada, 18-10-2026:
1. Reconstrucción completa desde cero (`rm .knowledge-cache/knowledge.sqlite` +
   index→graph→export→reindex→rebuild): 359 archivos, 2697 secciones, 3 entidades,
   40 relaciones — estable, mismos totales que ejecuciones anteriores.
2. `pytest tests/knowledge -q`: 23/23 passed.
3. `ruff check scripts/knowledge tests/knowledge` + `mypy --ignore-missing-imports`:
   sin avisos.
4. `python3 scripts/knowledge/mcp_server.py < /dev/null`: exit=0, sin stderr
   (arranque real por stdio).
5. Integridad de `CONTEXT.md`: `sha256sum docs/history/CONTEXT-full-2026-10-18.md`
   == hash original pre-edición (`5bd41bb4...`) — confirmado de nuevo, no solo
   en la Fase 4.
6. `firmware/` y `analysis/ghidra/*.gpr` listados (no leídos/modificados):
   estructura intacta, ningún archivo binario tocado por este trabajo.
7. Sin repositorio `.git` en el proyecto: no hubo riesgo de commit/push accidental;
   ninguna operación de git se ejecutó en ninguna fase.

## Entorno de desarrollo

- `.venv/` creado en la raíz del proyecto (autorizado por el usuario, aislado, sin sudo).
- Versiones fijadas en `knowledge/requirements-dev.txt`: ruff 0.17.1, mypy 2.4.0, pytest 9.1.1.
- Activar con `source .venv/bin/activate` antes de `ruff check` / `mypy` / `pytest`.

## Pruebas ejecutadas

- `python3 -m unittest tests.knowledge.test_index_docs` → OK (3/3), 2026-10-18.
- Búsqueda exacta sobre `0x4383fd6c` y `SetImageWrited`: resultados correctos,
  incluida la corrección S12 (`0x1007` no `0x1009`).
- Búsqueda textual BM25 sobre "SilentShutter EFCS" y "Darwin base ROM": resultados pertinentes.
- `ruff`/`mypy`: NO DISPONIBLES en este entorno (solo quedan cachés `.ruff_cache`/`.mypy_cache`
  de sesiones previas, sin binarios instalados). Pendiente: crear venv del proyecto
  (autorizado por el usuario) e instalar ahí antes de validar estilo.

## Bloqueos activos

- Ninguno crítico. `ruff`/`mypy` ausentes (no bloquea funcionalidad, sí la validación de estilo).

## Límite de alcance documentado (Fase 3)

Solo se incorporaron JSON con la forma exacta `{binary, sha256, address_space,
symbol_value, original_name}` (3 entidades reales, en `analysis/functions/dossiers.json`).
Otros JSON de análisis con esquemas distintos (p. ej. `rea-takePicture-decompile.json`,
`silent-shutter-converter.json`, tablas IMX210/GPIO) NO están todavía en el grafo:
cada esquema heterogéneo necesitaría su propio extractor, y generalizar a ciegas
violaría el requisito de "no generar miles de relaciones irrelevantes". Pendiente:
añadir extractores específicos por esquema cuando se prioricen (candidatos naturales
para la Fase 4: GPIO fm3-gpio-shutter-mapping, EFCS capture-selector, WriteStill/SetImageWrited).

## Archivos nuevos de la Fase 4

- `docs/STATE.md` — estado breve con enlaces a fuentes canónicas.
- `docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md` — generados, regenerar con
  `export_corrections.py` tras cada `build_graph.py`.
- `scripts/knowledge/export_corrections.py` + `tests/knowledge/test_export_corrections.py`.
- `docs/history/CONTEXT-full-2026-10-18.md` (copia legible íntegra, indexada),
  `docs/history/CONTEXT.md.2026-10-18.bak` + `.sha256.orig` (respaldo binario-verificado).
- `CONTEXT.md` reescrito (116 líneas: S28–S30 + punteros).

## Fase 11 — auditoría independiente y corrección de defectos (2026-10-18)

Una auditoría del usuario (no de este mismo sistema) encontró defectos reales de
exactitud y de evaluación en lo entregado en las fases 1-10. Se corrigieron con
pruebas de regresión nuevas (39 tests totales, antes 23); cada fix documenta el
bug reproducido en el docstring/comentario del propio código.

**P1 — Exactitud del grafo (CERRADO):**
- `build_graph.py::build_function_graph` indexaba CALLS por nombre corto de método en
  un `dict` que se sobrescribía: si dos clases del mismo binario compartían nombre de
  método (p. ej. `A::run()` y `B::run()`), la llamada podía apuntar a la clase
  equivocada según el orden de inserción — el caso exacto que describió la auditoría.
  Fix: `qualified_name()` nuevo (conserva el calificador `ns::Clase::metodo`); se
  intenta primero resolución por nombre calificado exacto, y solo se cae a nombre
  corto cuando es ÚNICO en el binario; si es ambiguo, NO se genera arista (ni la
  correcta ni la incorrecta). Tests:
  `test_ambiguous_short_name_in_same_binary_is_discarded_not_misrouted`,
  `test_qualified_outgoing_name_disambiguates_same_short_name`.
- CORRECTS/SUPERSEDES: antes el status se detectaba buscando el vocabulario en toda
  la ventana de ±2 líneas, pudiendo atribuir un status de una oración vecina no
  relacionada. Ahora se busca primero en la línea del propio marcador. Además se
  separaron relaciones con enlace en la MISMA línea del marcador (evidencia directa)
  de relaciones cuyo enlace solo aparece en la ventana (proximidad, no demostración):
  estas últimas se marcan `CONFLICTO_PENDIENTE` y `extraction_method` distinto
  (`...window_candidate` vs `...same_line`), nunca heredan un status más fuerte por
  cercanía. Test: `test_link_only_in_window_is_candidate_not_verified`.

**P2 — Recuperación de contexto (PARCIAL, ver pendientes):**
- `ROOT = Path.cwd()` en los 6 scripts dependía del directorio desde el que se
  invocara el proceso. Nuevo `scripts/knowledge/_paths.py::find_root()`: busca hacia
  arriba desde cwd el marcador `CLAUDE.md`; cae a cwd si no lo encuentra (preserva el
  comportamiento de los fixtures de test, que deliberadamente no tienen marcador).
- `_budget_print` (router `ask`): un primer resultado más grande que el presupuesto se
  imprimía completo (la condición `shown > 0` lo eximía del recorte) — el presupuesto
  quedaba sin efecto real. Ahora se trunca también el primer bloque. Tests:
  `test_single_oversized_block_is_truncated_not_printed_whole`,
  `test_budget_print_never_exceeds_budget_across_multiple_blocks`.
- `cmd_exact`/rama `identifier` de `ask`: `rg --max-count N` limita POR ARCHIVO, no en
  total; con muchos archivos la salida combinada podía seguir siendo enorme. Ahora el
  límite se aplica en Python sobre el total de líneas combinadas (límite global real).
  Test: `test_global_limit_caps_total_lines_across_all_files`.
- `cmd_section` ganó `--subtree` (y la tool MCP `get_document_section` el parámetro
  `subtree`): por defecto devuelve solo el contenido PROPIO de la sección (hasta su
  primer sub-encabezado); con `--subtree` incluye todos los descendientes hasta el
  siguiente encabezado del mismo nivel o superior. Antes solo existía el modo "propio"
  sin forma de pedir el árbol completo. Tests: `test_default_section_excludes_children`,
  `test_subtree_includes_children_but_not_next_sibling`.
- `cmd_text` ganó `--offset` (paginación real sobre FTS5 `LIMIT`/`OFFSET`). Test:
  `test_offset_returns_different_page`.
- Nuevo comando `search.py freshness` + tool MCP `check_index_freshness`: compara el
  SHA-256 actual de cada doc contra la tabla `files` y reporta archivos
  modificados/añadidos/eliminados desde el último `index_docs.py`. Antes no había
  ninguna forma de saber si el índice estaba desincronizado. Tests en
  `tests/knowledge/test_freshness.py` (4 casos).
- `split_sections` (`index_docs.py`) descartaba TODO el texto anterior al primer
  encabezado Markdown. Ahora se conserva como sección `(preámbulo)` (nivel -1, nunca
  ancestro de un encabezado real en `build_tree`, para no corromper la jerarquía).
  Tests: `test_preamble_before_first_heading_is_preserved`,
  `test_preamble_does_not_become_parent_of_first_heading`.
- Límite MCP global: `mcp_server.py::_captured` ahora trunca cualquier salida a
  `MCP_MAX_CHARS = 20000` (antes una tool podía devolver una respuesta de tamaño
  arbitrario si el cliente pedía un `--limit`/`--budget` grande).
- **Pendiente real (no cerrado):** "ampliación de fragmentos por identificador" más
  allá de `--subtree`/`--offset` (p. ej. pedir N líneas de contexto arbitrarias
  alrededor de un `node_id`) no se implementó — el alcance actual cubre los dos casos
  concretos que pidió la auditoría (subárbol completo, paginación de `text`), no un
  mecanismo general de contexto configurable.

**P3 — Calidad del conocimiento (CERRADO en lo señalado):**
- `export_open_questions` generaba `docs/OPEN-QUESTIONS.md` buscando por TEXTO LIBRE
  las palabras NO_VERIFICADO/CONFLICTO_PENDIENTE en cualquier sección indexada: una
  sección que solo EXPLICA el vocabulario de status (sin ser una relación real del
  grafo) se contaba como pregunta abierta. Con el corpus real esto causaba 384 "filas"
  falsas. Ahora sale de la tabla `relations` (solo relaciones con ese status): tras
  rebuild completo, `docs/OPEN-QUESTIONS.md` pasó de 384 a **39 filas reales**.
  Test: `test_open_questions_ignores_sections_that_only_mention_the_word`.
- Mensaje de `cmd_claim`/`find_corrections` cuando no hay relaciones entrantes: antes
  decía "se mantiene como fuente vigente" (afirmación no demostrada por la ausencia de
  datos). Ahora aclara explícitamente que la ausencia de correcciones registradas NO
  demuestra vigencia.
- Tests de contradicción/corrección parcial/referencia histórica: ya existían
  parcialmente en `test_build_graph.py` (resolución de sesión, no auto-contaminación);
  se añadieron los de ambigüedad de nombre y candidata-vs-verificada arriba. No se
  amplió a un conjunto de "contradicciones narrativas" más allá de lo que el grafo
  determinista puede detectar (sigue siendo deliberadamente NO basado en inferencia de
  LLM: ver diseño original).

**P4 — Benchmarks (NO ABORDADO esta sesión):** sigue comparando presencia de
subcadena en la salida, no precisión de fuentes/rangos/evidencias, y no distingue
tokens estimados de tokens realmente consumidos por un agente real. Rediseñarlo es
trabajo no trivial (requiere una verdad de referencia estructurada, no solo una
subcadena esperada) y se deja pendiente explícitamente, no se improvisó una versión
a medias.

**P5 — Integración y memoria (PARCIAL):**
- Checkpoint actualizado con esta fase (ver `knowledge/checkpoints/`, el de esta
  sesión referencia fases 9-11 como completas, no pendientes).
- Verificación real de MCP/skills desde una sesión NUEVA de Claude Code o Codex sigue
  sin poder hacerse desde dentro de esta misma sesión (limitación estructural, igual
  que en la Fase 7).
- Extractores por esquema para GPIO/IMX210/OSAL/REA/Ghidra: NO implementados. Sigue
  siendo trabajo futuro (ver límite de Fase 3 arriba), ahora con la ambigüedad de
  nombres ya resuelta en el extractor existente para cuando se añadan.

## Fase 12.1-12.2 — segunda auditoría: negación, duplicados, raíz y streaming (2026-10-18)

Segunda auditoría independiente (Fase 12), con casos reproducidos nuevos distintos
de los de la Fase 11. Se corrigieron todos los de 12.1 (crítico) y los de 12.2 con
reproducción concreta; 12.3 ya estaba sustancialmente cubierto por la Fase 11 y no
se tocó sin necesidad. 12.4-12.10 (extractores por esquema, consultas multietapa,
rediseño de benchmark, verificación cruzada de clientes, `CURRENT.md`) **NO se
abordaron esta vuelta** — alcance explícitamente fuera de esta sesión, ver abajo.

**12.1.A — Negación en CORRECTS/SUPERSEDES (CERRADO):** `VERIFICADO: esta revisión
NO corrige [el informe antiguo](old.md).` generaba igualmente `CORRECTS` con status
`VERIFICADO`, ignorando la negación. `build_graph.py` ahora detecta una partícula
negativa (`no/nunca/jamás/tampoco`) en las ~4 palabras previas al marcador, sin
cruzar el final de la oración anterior; si está negado, el status se fuerza a
`CONFLICTO_PENDIENTE` y el `extraction_method` queda marcado `..._negated`, nunca
`VERIFICADO` pese al vocabulario cercano. Test:
`test_negated_correction_mention_is_not_verified`.

**12.1.B — Identidad ambigua de funciones:** ya resuelta en la Fase 11 (nombre
calificado completo + descarte si el nombre corto es ambiguo en el binario). La
auditoría pide además modelo de cámara, versión de firmware, hash de binario, base
de carga y modo ARM/Thumb como parte de la identidad — **no se añadieron**: el único
dossier de función real del repo (`analysis/functions/dossiers.json`, 3 items) no
contiene esos campos. Añadirlos ahora sería inventar estructura que el dato real no
tiene; se deja documentado para cuando los extractores de 12.4 (Ghidra/REA) los
aporten con datos reales.

**12.1.C — `UNIQUE constraint failed: entities.id` con dossiers duplicados
(CERRADO):** la misma función (misma identidad técnica: sha256+address_space+
symbol_value) en dos JSON distintos hacía fallar el segundo `INSERT`. Se añadió la
tabla `entity_sources` (entity_id, owner_source, original_name, confidence) para
procedencia múltiple: la entidad se crea una sola vez (primera fuente = canónica),
cada dossier adicional solo añade/actualiza su fila de procedencia vía `INSERT ...
ON CONFLICT DO UPDATE` (idempotente, no vuelve a fallar al re-ejecutar). Si dos
fuentes dan `original_name` distinto para la misma identidad técnica, se registra el
conflicto en `entities.extra` (`name_conflict`) en vez de sobrescribir en silencio o
descartar la segunda fuente. Al eliminar un dossier, la entidad solo se borra si
NINGUNA fuente viva la sigue aportando. Tests:
`test_duplicate_function_across_dossiers_does_not_crash_and_keeps_both_sources`,
`test_contradictory_metadata_between_dossiers_is_flagged_not_silently_overwritten`,
`test_removing_one_of_two_dossiers_keeps_entity_alive_via_remaining_source`.
Verificado además con `build_graph.py` ejecutado dos veces seguidas sobre el repo
real: idempotente, mismo resultado (3 entidades, 1 CALLS, 39 CORRECTS/SUPERSEDES).

**12.2.A — Resolución de raíz rota fuera del proyecto (CERRADO):** caso reproducido
y verificado manualmente: ejecutar cualquier script desde `/tmp` (cwd ajeno, sin
`CLAUDE.md` en ningún ancestro) hacía que `find_root()` devolviera ese mismo `/tmp`
como raíz (fallback antiguo), con 0 documentos indexados. `_paths.py` ahora
prioriza: (1) variable de entorno `SONY_A6000_KB_ROOT` explícita, validada contra
`CLAUDE.md`; (2) ascenso desde cwd buscando `CLAUDE.md` (comportamiento previo); (3)
**nuevo** — si (2) no encuentra nada, ascenso desde la ubicación de INSTALACIÓN del
propio `_paths.py`, que sí resuelve al proyecto real; (4) cwd sin resolver, último
recurso solo para fixtures de test que deliberadamente no tienen `CLAUDE.md` propio.
Verificación manual: `cd /tmp && python3 .../search.py freshness` ahora imprime
"Índice al día" contra el proyecto real, no "0 archivos". Todos los fixtures de test
que simulaban un proyecto aislado (`test_adaptive_search.py`, `test_build_graph.py`,
`test_checkpoint.py`, `test_export_corrections.py`, `test_freshness.py`,
`test_index_docs.py`, `test_benchmark.py`) ahora escriben su propio `CLAUDE.md`
vacío, para no depender implícitamente del fallback. Tests nuevos en
`test_paths.py`: ascenso normal, fallback a instalación, override por entorno válido
e inválido (`SystemExit`).

**12.2.B — `rg` bufferizaba toda la salida en memoria (CERRADO):** `cmd_exact` y la
rama `identifier` de `cmd_ask` usaban `subprocess.run(capture_output=True)`, que
bufferiza TODO el stdout de `rg` antes de devolver nada — con miles de coincidencias,
cientos de MB en memoria por solo mostrar `--limit`. Nuevo helper `_rg_stream()`
(compartido por ambos) usa `Popen` y lee el pipe línea a línea, cortando en cuanto se
alcanza `RG_MAX_SCAN = 5000` líneas leídas o `RG_TIMEOUT_S = 10s`, lo que ocurra
primero — sin esperar a que `rg` termine de buscar en todo el corpus. El límite
mostrado (`--limit`) sigue aplicándose en Python, ahora sobre el stream, no sobre una
lista ya completa. Test: `ExactStreamingCapTest` (genera >5000 líneas coincidentes,
verifica que se corta y que el aviso de tope aparece).

**12.2.C — Límites de contexto en todas las rutas:** ya cubiertos por `budget`
(`ask`), `limit` (`exact`/`text`/`identifier`), `--subtree`/`--offset` (`section`),
y el tope global MCP de 12.2.D. Las consultas del grafo (`cmd_graph`) y
`find_corrections`/`cmd_claim` ya tenían `LIMIT` explícitos desde la Fase 11; no se
tocaron sin necesidad.

**12.2.D — Tools MCP sin tope (CERRADO):** `get_current_state()` devolvía
`docs/STATE.md` COMPLETO sin pasar por `MCP_MAX_CHARS` (único tool que no usaba
`_captured`); `get_open_questions` tampoco pasaba por el tope global de caracteres
(solo recortaba por líneas). Nuevo helper `_cap_chars(texto, offset)` compartido por
`_captured` y ambas tools: aplica el mismo tope global Y admite paginación por
`offset` (en caracteres) para seguir leyendo más allá del corte. Tests:
`test_get_current_state_respects_global_mcp_char_limit`,
`test_get_current_state_offset_paginates`.

**12.3 — Calidad del conocimiento:** ya cubierto en Fase 11 (mensaje de `cmd_claim`
sobre no-vigencia por ausencia; `OPEN-QUESTIONS.md` basado en grafo, no en texto
libre). No se reescribió sin necesidad.

**Verificación real ejecutada:** rebuild completo (`index_docs.py --rebuild`
implícito vía reindex normal: 359 archivos, 2727 secciones, sin cambios de conteo —
esperado, ya eran correctos desde la Fase 11), `build_graph.py` dos veces seguidas
(idempotente: 3 entidades, 1 CALLS, 39 CORRECTS/SUPERSEDES ambas veces, "0 entidades"
nuevas en la segunda), `export_corrections.py` (CORRECTIONS.md 39 filas,
OPEN-QUESTIONS.md 39 filas, sin regresión a 384), `search.py freshness` (al día tras
reindexar), suite completa: **50/50 tests** (eran 39 al cierre de la Fase 11; +11
nuevas: 1 negación, 3 duplicados/conflicto, 4 resolución de raíz, 1 streaming, 2
límite MCP), `ruff check` y `mypy` limpios sobre `scripts/knowledge` y
`tests/knowledge`. Verificado que ningún archivo fuera de
`scripts/knowledge`/`tests/knowledge`/`knowledge/`/`docs/CORRECTIONS.md`/
`docs/OPEN-QUESTIONS.md` fue modificado (firmware, proyectos Ghidra/REA y evidencias
originales intactos).

**Pendiente real, explícitamente NO abordado esta vuelta (Fase 12.4-12.10):**
- Extractores por esquema para GPIO, IMX210, OSAL/CAIF, REA, Ghidra (12.4): requiere
  primero inspeccionar los ~2146 JSON reales bajo `analysis/` (solo se hizo un
  muestreo puntual para confirmar que no hay campos de identidad extendida) y diseñar
  un esquema de extracción por formato — trabajo de varias sesiones, no un parche.
- Consultas técnicas multietapa (12.5): dependen de que 12.4 aporte entidades/
  relaciones reales más allá de las 3 funciones actuales; prematuro sin esos datos.
- Rediseño de benchmark con verdad de referencia estructurada (12.6): sigue
  pendiente desde la Fase 11, sin cambios esta vuelta.
- Validación real desde sesión nueva de Claude Code/Codex (12.7): no se puede
  ejecutar desde dentro de esta misma sesión; requiere confirmación del usuario desde
  fuera.
- `knowledge/CURRENT.md` + reescritura de `AGENTS.md`/`CLAUDE.md` para leer el resumen
  breve primero (12.8): no implementado.

## Fase 12.4-12.5 — inventario, extractores Ghidra/REA y consultas multietapa (2026-10-18)

**12.4.A — Inventario determinista (CERRADO):** nuevo `scripts/knowledge/inventory_json.py`
agrupa los 2146 JSON bajo `analysis/` por FIRMA ESTRUCTURAL (forma de claves+tipos, no
contenido ni nombre de archivo) en ~0.4s, sin leer ninguno con el contexto del LLM. Salida:
`knowledge/catalog/JSON-CATALOG.md` (108 familias, tabla legible) y
`json_inventory.json` (detalle completo por archivo). Hallazgo clave: el 60% de los
archivos (`analysis/elf-cache/*`, 1282) son solo metadatos ELF (exports/imports/soname),
sin relaciones verificables — registrados, sin extractor. Una familia de 61 archivos
(`coverage, function_count, targets`, xrefs Ghidra) tiene referencias reales en 52/61
pero SIN campo de hash de binario: identidad insuficiente para anclar a un binario
concreto sin riesgo de colisión de direcciones entre binarios distintos — registrada,
sin extractor, por decisión explícita (no inventar binary_sha256).

**12.4.B — Extractor Ghidra (CERRADO, impacto principal):** la familia dominante real
(`{source_sha256: str, functions: [...]}`, ~430 de los 2146 archivos, detectada por FORMA)
resultó ser pseudocódigo decompilado real con direcciones, no solo nombres: cada función
trae `pseudo_code` con llamadas `FUN_<dirección>(...)` y, en varios archivos,
`firmware_profile` (p. ej. "ILCE-6000 3.21"), `rom_base`/`raw_base`. Nuevo
`build_ghidra_function_graph()` en `build_graph.py`: crea entidades Function por
(binary_sha256, dirección) — SOLO para `status == "decompiled"` (sin inventar evidencia
donde Ghidra no la produjo) — y relaciones CALLS resolviendo `FUN_<hex>` contra el grafo
completo (no solo el archivo actual, ya que el mismo binario se analiza en decenas de
JSON temáticos distintos), descartando toda dirección con 0 o >1 candidatos. Identidad
parcial explícita: `address_space = "unknown"` (Ghidra no lo reporta aquí; nunca se
adivina ARM/Thumb). Tests: `test_ghidra_functions_family_creates_entities_and_address_based_calls`,
`test_ghidra_function_without_decompiled_status_is_not_an_entity`,
`test_ghidra_call_to_address_without_evidence_is_discarded`,
`test_ghidra_calls_resolve_across_different_owner_files_same_binary`,
`test_rerunning_ghidra_extractor_is_idempotent`.

**12.4.B — Extractor REA (CERRADO):** familia real de 5 archivos con forma
`{subject: {digest: {sha256}}, operation, normalized_result}`, en dos variantes:
`procedure_pseudo_code` (una función; nombre extraído del comentario
`/* ns::Clase::metodo() */`) y `batch_decompile` (varias funciones NOMBRADAS por archivo,
con `status`/`procedure.status` propios — solo se usan entradas `"ok"`/`"resolved"`).
Cubre, con datos reales, exactamente los dominios OSAL (`osal_snd_msg`,
`osal_reg_sync_msg_queue_cb`, `reg_sync_msg_queue_cb`) y NFC/CAIF
(`nfc_rsrc_sio_init`, `nfc_rsrc_dev_send_data`, `nfc_rsrc_dev_recv_data`) pedidos en
prioridad 2. Nuevo `build_rea_evidence_graph()`: mismas garantías que el extractor Ghidra,
más resolución de llamadas POR NOMBRE (no solo por dirección) cuando el nombre es único en
el binario — encontró una relación real: `osal_reg_sync_msg_queue_cb --CALLS-->
reg_sync_msg_queue_cb`. Tests: `test_rea_procedure_pseudo_code_shape_creates_entity`,
`test_rea_batch_decompile_shape_resolves_named_call`,
`test_rea_unresolved_batch_item_is_not_an_entity`, `test_rerunning_rea_extractor_is_idempotent`.

**Por qué NO se construyeron extractores separados para Darwin/GPIO e IMX210/IMX284
(prioridades 3-4):** se inspeccionaron sus JSON reales (`a6000-darwin-adc-phase-
notification.json`, `a6300-imx284-readout-helpers.json`, `a6300-shared-queue-
producers.json`, etc.) y comparten EXACTAMENTE la misma forma estructural que la familia
Ghidra de 12.4.B (`source_sha256` + `functions` con `pseudo_code`) — ya quedan cubiertos
por ese mismo extractor sin duplicar código. Las variantes de GPIO específicas vistas
(`darwin-dma-gpio-checkpoint.json`, `a6000-darwin-phase-table-verified.json`) son
documentos únicos (count=1 en el catálogo), sin estructura repetida que justifique un
extractor dedicado — permanecen como conocimiento solo en Markdown/texto libre.

**Refactor de deduplicación:** se extrajo `_upsert_function_entity()` (idempotencia +
conflicto de metadatos de la Fase 12.1.C) a una función compartida por los TRES
extractores (dossiers.json, Ghidra, REA), evitando triplicar esa lógica.

**12.1.A ampliado — límite de la ventana de negación corregido tras la observación del
usuario:** "analizar solo 4 palabras antes del marcador no demuestra cobertura
completa" era correcto — se cambió a buscar la negación en TODA la oración (acotada por
`.`/`;` con límite de palabra real, no un punto dentro de `old.md`) en AMBOS lados del
marcador, cubriendo también matices adversativos posteriores ("corrige, pero nunca de
forma completa"). Tests:
`test_negation_further_than_four_words_before_marker_is_still_detected`,
`test_adversative_hedge_after_marker_in_same_clause_is_not_verified`. Sigue siendo un
filtro léxico determinista, no semántico: negación doble o ironía compleja puede seguir
sin detectarse (limitación documentada, no resoluble sin inferencia de LLM, fuera del
diseño de este sistema).

**12.5 — Consultas multietapa (demostrado):** nuevo subcomando `search.py trace` +ool MCP
`trace_relations`: recorrido BFS real sobre `relations` hasta N saltos, sin ciclos, con
evidencia y procedencia por arista; si no hay relación registrada, lo dice explícitamente
en vez de inventar un salto. Demostrado contra el grafo real:
`python3 scripts/knowledge/search.py trace <eid de osal_reg_sync_msg_queue_cb> --direction out`
devuelve la cadena real `osal_reg_sync_msg_queue_cb --CALLS--> reg_sync_msg_queue_cb` con
el pseudocódigo como evidencia. Tests: `test_two_hop_chain_is_followed`,
`test_max_hops_limits_depth`, `test_disconnected_node_reports_no_relations_not_an_error`,
`test_reverse_direction_follows_incoming_edges`. **No implementado:** las consultas en
LENGUAJE NATURAL que pide 12.5 como ejemplo ("¿qué funciones participan en 0x50004?")
requerirían mapear primero esas constantes/strings a entidades — el mecanismo de
recorrido (`trace`) ya existe y es real, pero traducir una pregunta en prosa a un nodo de
partida sigue siendo manual (vía `search.py exact "0x50004"` primero para ubicar el nodo).

**Resultado medido del grafo, antes/después de 12.4 (mismo corpus real, sin binarios
reanalizados — solo extracción de evidencia YA EXISTENTE en `analysis/`):**

| | antes (Fase 11) | después (Fase 12.4) |
|---|---|---|
| Entidades Function | 3 | **1189** |
| Relaciones CALLS | 1 | **2643** (incluye 39 CORRECTS/SUPERSEDES; CALLS puro: 2603 netas) |
| Fuentes de evidencia usadas | 1 dossier | 1 dossier + ~430 JSON Ghidra + 5 JSON REA |

Verificado: `build_graph.py` ejecutado dos veces seguidas → idempotente (segunda vez:
"0 entidades" nuevas, mismo total). 65/65 tests, ruff/mypy limpios. Firmware/Ghidra/REA
originales intactos (no se reanalizó ningún binario; solo se leyeron JSON ya exportados).

**Pendiente real, explícitamente NO abordado esta vuelta:**
- 12.6 (rediseño de benchmark con verdad de referencia estructurada): AHORA SÍ tiene
  sentido abordarlo, porque el grafo ya tiene datos reales que medir (antes solo había 1
  relación CALLS). Sigue sin implementarse.
- 12.7 (validación MCP/skills desde sesión nueva Claude Code/Codex): no ejecutable desde
  esta misma sesión.
- 12.8 (`knowledge/CURRENT.md` + reescritura de `AGENTS.md`/`CLAUDE.md`): no implementado.
- Consultas multietapa en lenguaje natural (mapeo automático de constantes/direcciones
  mencionadas en prosa a nodos del grafo): no implementado, ver nota en 12.5 arriba.

## Fase 12.6 — validación del grafo ampliado + rediseño del benchmark (2026-10-18)

### 1. Validación del grafo real (muestreo estratificado, antes de tocar el benchmark)

Verificado contra la DB real (1189 entidades, 2604 relaciones CALLS antes de la corrección
siguiente):

- **Evidencia localizada en todas las CALLS:** `evidence` nunca NULL/vacío (0 filas).
- **Mismo binario origen/destino:** 0 relaciones con `binary_sha256` distinto entre src/dst
  (comprobado con JOIN sobre las 2604 relaciones, no una muestra).
- **`FUN_<hex>` no conecta espacios de direcciones distintos:** por diseño, la resolución
  siempre filtra por `binary_sha256` antes de buscar la dirección — confirmado.
- **OSAL `0x50004` y Darwin `0x4200` NO son direcciones de función:** `SELECT ... WHERE
  address IN ('0x50004','0x4200')` → 0 filas. Ambos solo existen como texto en Markdown
  (identificador de mensaje OSAL y base ROM Darwin respectivamente), nunca como entidad
  Function — correcto, el grafo no los confunde.
- **BUG REAL encontrado y corregido — relaciones duplicadas sin deduplicar:** la misma
  llamada `FUN_X -> FUN_Y` reanalizada en varios JSON de sesión (el mismo binario se
  exporta repetidamente) creaba una fila `relations` POR ARCHIVO (`relation_id` incluía
  `source_path`), violando el requisito explícito de la auditoría ("relaciones repetidas
  deduplicadas sin perder procedencia"). Medido en la DB real: 616 grupos duplicados, 840
  filas sobrantes. **Corregido:** nueva tabla `relation_sources` (mismo patrón que
  `entity_sources`) + helper `_upsert_call_relation()` — una sola fila `relations` por
  `(src,dst,type)`, con cada archivo que la respalda registrado en `relation_sources` sin
  perder procedencia. Tras la corrección: **1764 relaciones CALLS reales** (2604 fuentes de
  evidencia conservadas en `relation_sources`), 0 duplicados, idempotente (segunda
  reconstrucción: 0 entidades/0 relaciones nuevas). Test de regresión:
  `test_same_call_reported_by_two_owner_files_deduplicates_but_keeps_both_provenances`.
- **Llamadas directas vs. indirectas (vía trampolín):** Ghidra nombra el trampolín en una
  dirección como `thunk_FUN_<addr>`; antes se fusionaba silenciosamente con una llamada
  directa `FUN_<addr>(`. Ahora `_is_thunk_call()` distingue
  `ghidra:pseudo_code_call_same_binary_via_thunk` de la variante directa (comprobado que no
  hay falsos positivos por falta de `\b`: 0 coincidencias con prefijo alfanumérico tipo
  `PTR_FUN_`; sí existen `thunk_FUN_` reales, verificados caso por caso — el destino al que
  apuntan en el corpus actual no coincide con ninguna entidad conocida, por lo que ninguna
  relación quedó finalmente etiquetada `_via_thunk`: hallazgo documentado, no inventado).
  Test: `test_ghidra_call_through_thunk_is_tagged_as_indirect_not_direct`.
- **Cobertura faltante identificada, NO inventada:** la cadena EncodeStill documentada
  manualmente en `CONTEXT.md:26` (`90b248→90a810→90ad20→8fe6f8→71cf58→44f834`) no tiene
  NINGUNA de esas direcciones como entidad Function en el grafo (ese binario/rango no fue
  parte del corpus Ghidra/REA decompilado). `trace` sobre esas direcciones devuelve "Sin
  relaciones", correctamente — no se fabricó la ruta. Ver caso `multi-encodestill-chain-no-coverage`
  en el benchmark v2.

### 2-5. Benchmark rediseñado (`scripts/knowledge/benchmark_v2.py`)

- Línea base previa (`baseline-2026-10-18-pre-12.6.md`, metodología de subcadena) **conservada
  sin modificar**, tal como exigía la instrucción.
- Verdad de referencia estructurada en `knowledge/benchmarks/reference_queries_v2.json`:
  16 consultas, 8 categorías (exact/conceptual/historical/relational/multietapa/negative/
  ambiguous/partial), subsistemas Darwin, GPIO, IMX210, OSAL, EncodeStill, WriteStill. Cada
  entrada cita su fuente manual (`note`), fijada ANTES de ejecutar el benchmark y SIN pedirle
  la respuesta al propio grafo/`ask`.
- Scoring real, no subcadena: exact/conceptual/historical exigen afirmación Y ruta fuente;
  relational/multietapa exigen la arista/cadena CALLS exacta; negative exige que el método
  NO afirme el hecho fabricado; ambiguous exige >=2 fuentes distintas expuestas (no una
  respuesta falsamente única); partial exige abstención.
- 4 métodos, mismo presupuesto (`--budget 1000` para `ask`; sin recorte para `rg` a
  propósito, para medir el costo real de "sin motor"): `rg` crudo, `fts5` (`search.py
  text`/`exact`), `graph` (`search.py trace`/`graph` — SOLO cuando la consulta tiene un
  nodo/documento real; si no aplica, se omite esa fila en vez de simular con otro método
  bajo la misma etiqueta).
- **Resultado (Precision@1):** `graph` 5/6 = 0.83 — pero ese 6 son EXACTAMENTE las
  consultas relacionales/multietapa que `rg`/`fts5` no pueden resolver en absoluto (una
  arista CALLS entre dos funciones, o una cadena de 2 saltos). `fts5` y `ask` 8/17 = 0.47
  cada uno (dominan en conceptual/histórico, donde el grafo no tiene nodo aplicable). `rg`
  7/17 = 0.41, con un costo real desproporcionado: en consultas genéricas ("callback",
  "init") recorre TODO el repo sin recorte y devuelve >100M caracteres — ilustra
  exactamente el problema que motiva el proyecto, no es un error de medición.
- **Limitaciones documentadas explícitamente en el propio reporte, SIN ajustar el
  benchmark para forzar mejores números** (instrucción explícita del usuario): el criterio
  `partial` exige salida vacía, lo que no distingue "afirmé algo falso" de "listé archivos
  reales sin resolver una relación concreta" — probablemente subestima el acierto real de
  `rg`/`fts5` ahí. La memoria (RSS Δ) es una aproximación por diferencia de
  `ru_maxrss` acumulado entre procesos hijo, no una medición aislada. Los tokens son
  SIEMPRE estimados (caracteres/4): no hay tokenizador real ni reporte de uso de un agente
  real disponible en este entorno, y el reporte lo dice explícitamente para no declarar un
  ahorro de tokens real a partir de bytes.
- **Conclusión de utilidad del grafo (punto 5 de la auditoría):** las 1764 relaciones CALLS
  SÍ aportan información que ningún `grep`/FTS5 puede reconstruir — llamadas entre
  funciones decompiladas (`osal_reg_sync_msg_queue_cb -> reg_sync_msg_queue_cb`, cadenas de
  2+ saltos) no están escritas en ningún documento Markdown, solo existen en el pseudocódigo
  Ghidra/REA ya procesado. El grafo NO ayuda (y no se le pidió que ayudara) en consultas
  conceptuales/históricas que dependen de prosa de investigación, ahí FTS5/`ask` siguen
  siendo el método correcto. Esto confirma que el valor del grafo es específico a relaciones
  de llamada verificables, no un reemplazo general de la búsqueda textual.

## Fase 12.7 — validación MCP/skills (lo verificable desde esta sesión)

- `.mcp.json` (Claude Code): rutas absolutas al Python del venv del proyecto; arranque real
  `python3 scripts/knowledge/mcp_server.py < /dev/null` desde `/tmp` (fuera del repo) sale
  sin error — confirma que el fix de resolución de raíz (Fase 12.3) también cubre el
  arranque MCP desde un cwd ajeno al proyecto.
- `.claude/skills/*/SKILL.md` (4 skills): frontmatter `name`/`description` presente y
  específico en las 4; directorios reales, no symlinks rotos; sin implementaciones
  duplicadas.
- `test_mcp_server.py`: protocolo real en memoria (`list_tools`, `call_tool`) — 11 tools
  descubiertas, llamadas reales devuelven datos del repo, entrada inválida no tira el
  servidor.
- **Hallazgo re-confirmado (no nuevo, ya documentado en la Fase 6): Codex sigue sin tener
  registrado el servidor MCP.** `~/.codex/config.toml` no tiene
  `[mcp_servers.sony-a6000-knowledge]` (solo `trust_level` para este proyecto); el snippet
  exacto para añadirlo está en la Fase 6 de este documento. No se editó el archivo global
  sin autorización explícita.
- **Única limitación real, documentada y no resuelta desde aquí:** el descubrimiento de
  skills/MCP por un cliente Claude Code o Codex RECIÉN iniciado (sesión nueva, fuera de este
  proceso) no es verificable desde dentro de esta misma sesión — requiere que el usuario lo
  confirme.

## Fase 12.8 — optimización de inicio

- `knowledge/CURRENT.md` (nuevo): resumen operativo de ~2.7 KB (2678 bytes) vs. 43962 bytes
  de `PROGRESS.md` completo — reducción del 94% en lo que una sesión nueva necesita leer
  primero. `CLAUDE.md`/`AGENTS.md` actualizados para leer `CURRENT.md` primero y recurrir a
  `PROGRESS.md` solo si se necesita el detalle histórico completo.

## Verificación final de esta vuelta

67/67 tests (eran 65; +2 por los bugs encontrados en 12.6), ruff/mypy limpios,
`build_graph.py` idempotente (dos reconstrucciones seguidas sobre la DB real: 0
entidades/0 relaciones nuevas en la segunda). Firmware/Ghidra/REA/evidencias originales
intactos — solo se editó `scripts/knowledge/`, `tests/knowledge/`, `knowledge/`,
`CLAUDE.md`, `AGENTS.md`.

## Fase 12.9 — registro real del servidor MCP en Codex (2026-10-18, autorizado por el usuario)

Usuario autorizó explícitamente editar `~/.codex/config.toml` (fuera del scope normal del
proyecto) con condiciones concretas (respaldo previo, no tocar otros servidores/credenciales,
usar el Python del `.venv`, validar sintaxis, confirmar con `codex mcp list`, probar con una
sesión real, verificar skills, no modificar firmware/evidencias, restaurar respaldo si falla).

1. **Respaldo:** `~/.codex/config.toml.bak-20261018T114752` (copia íntegra previa a cualquier
   edición).
2. **Estado previo confirmado:** no existía ningún bloque `[mcp_servers.sony-a6000-knowledge]`
   (grep antes de editar); no había duplicado posible.
3. **Cambio aplicado:** añadido al final del archivo, sin tocar ningún otro
   `[mcp_servers.*]`/`[projects.*]`/credencial existente:
   ```toml
   [mcp_servers.sony-a6000-knowledge]
   command = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/.venv/bin/python3"
   args = ["/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/knowledge/mcp_server.py"]
   startup_timeout_sec = 30
   ```
   Se usó la ruta del `.venv` (no su `realpath`, que resuelve a `/usr/bin/python3.14` sin el
   `sys.path`/paquetes del venv — `mcp_server.py` depende del paquete `mcp` instalado ahí).
4. **Validación de sintaxis:** `tomllib.load()` sobre el archivo completo, sin errores.
5. **`codex mcp list`:** `sony-a6000-knowledge` aparece listado, estado `enabled`, comando y
   args correctos; el resto de servidores (`rea`, `context-mode`, `codex_app`, etc.) intactos.
6. **Sesión Codex real** (`codex exec --skip-git-repo-check`, no interactiva — el proyecto no
   es un repositorio git por diseño del proyecto, confirmado en entorno; se usó el flag de
   solo-lectura para permitir la ejecución, no para saltar ninguna verificación de seguridad):
   - Descubrió exactamente **11 tools**: `check_index_freshness`, `find_corrections`,
     `find_symbol`, `get_current_state`, `get_document_section`, `get_open_questions`,
     `query_graph`, `search_documents`, `search_exact`, `search_hybrid`, `trace_relations`.
   - `search_exact("0x50004")` y `get_current_state()` devolvieron datos reales del repo
     (README.md:93, docs/OPEN-QUESTIONS.md, docs/STATE.md), sin fabricación.
   - Segunda sesión: `search_exact("P4D")` localizó
     `docs/capture/fm3-gpio-shutter-mapping.md:16` (P4D/PDOR4 bit13/`0x42668234` →
     1ST_CURTAIN_MG); `query_graph(doc=..., rel_type="CALLS")` devolvió "Sin resultados" y
     Codex lo reportó como abstención explícita, **sin inventar una relación CALLS** para
     completar la respuesta — comportamiento correcto, no un fallo a corregir.
7. **Skills compartidas:** las 4 skills de `.agents/skills/` (`contradiction-audit`,
   `knowledge-maintenance`, `knowledge-navigation`, `session-checkpoint`) son enlaces
   simbólicos directos a `.claude/skills/<misma-skill>` — correspondencia 1:1 confirmada por
   `readlink`, no copias que puedan desincronizarse.
8. **Sin errores que corregir:** no hubo fallo de integración; no fue necesario restaurar el
   respaldo. Firmware/Ghidra/REA/evidencias no se tocaron (ningún archivo fuera de
   `~/.codex/config.toml` + `knowledge/CURRENT.md` + esta sección).

**Limitación real no resuelta:** lo anterior usa `codex exec` (modo no interactivo). El
descubrimiento de tools/skills en una sesión **interactiva** normal del cliente Codex (la UI
de chat, no `exec`) sigue sin confirmación directa desde dentro de este proceso — sería
necesario que el usuario lo abra y lo confirme.

## Fase 12.10 — prueba de integración extremo a extremo (2026-10-18)

Objetivo: validar el ciclo completo grafo→checkpoint→recuperación cruzada Claude Code↔Codex
con medición de contexto, sin modificar firmware ni evidencias.

1. **Relación CALLS positiva con evidencia exacta:** `trace 6dec9cf1a9f52b76 --direction out
   --type CALLS` → `SCALARDAEMON::CommandProcessorCameraTakePicture::AsyncProcessor::execute()`
   `--CALLS-->` `SCALARDAEMON::SystemEventIssuerCamera::captureStart()`, estado `PARCIAL`,
   fuente `analysis/functions/dossiers.json`, evidencia "via PLT at callsite 0x108144".
   **Relación inexistente no inventada:** `trace d8c6c582d352e037 --direction out --type
   CORRECTS` → "Sin relaciones... no es evidencia de que no exista relación" (abstención
   explícita, correcta).
2. **Checkpoint Claude Code → Codex:** se escribió un marcador temporal identificable
   (`CKPT-CC-20261018T150425Z`) en `docs/STATE.md` (fuente real de `get_current_state`).
   Una sesión nueva `codex exec --skip-git-repo-check`, instruida a usar SOLO tools MCP (sin
   leer archivos a mano), citó el id exacto vía `get_current_state`, localizó la evidencia
   original de la afirmación GPIO citada en el checkpoint con `search_exact` en
   `docs/capture/fm3-gpio-shutter-mapping.md:16` y `:24`, y distinguió correctamente ese
   hallazgo **VERIFICADO** de una pregunta real **NO_VERIFICADO** (SilentShutter → final de
   exposición, `get_open_questions`, fuente `docs/capture/README.md:40`) — no las confundió.
3. **Checkpoint Codex → Claude Code (sentido inverso):** una sesión nueva `codex exec`
   escribió, con una edición de archivo real (no solo texto de respuesta), el marcador
   `CKPT-CODEX-20261018T151044Z` al final de `docs/STATE.md`. Desde Claude Code se invocó
   la función `get_current_state` real del servidor MCP (misma lógica que expone la tool;
   la tool en sí aparece como "Pending approval" en `claude mcp list` para esta sesión no
   interactiva — ver limitación abajo) y se recuperó el id exacto sin leer `CONTEXT.md` ni
   `PROGRESS.md`.
4. **Medición de contexto por recuperación:**

   | Recuperación | Caracteres | Tokens estimados (chars/4) | Tokens reales |
   |---|---:|---:|---:|
   | Codex recupera CKPT-CC + evidencia + pregunta abierta (sesión completa) | — | — | **29 247** (reportado por `codex exec`) |
   | Codex escribe CKPT-CODEX (sesión completa) | — | — | **16 805** (reportado por `codex exec`) |
   | Claude Code recupera CKPT-CODEX vía `get_current_state` | **4024** | **1006** | sin cifra real disponible (este entorno no expone tokens reales por llamada de Claude Code) |

   Los tokens reales de Codex son de la **sesión `exec` completa** (razonamiento + varias
   llamadas a tools), no solo de `get_current_state`; no son comparables 1:1 con los 1006
   estimados de una sola llamada de Claude Code — se reportan ambos sin forzar una
   equivalencia que no existe.
5. **Codex interactivo:** no verificable desde este proceso (mismo límite que Fase 12.9);
   no se declara fallo del sistema por esto.
6. **Limpieza:** ambos marcadores `CKPT-CC-*`/`CKPT-CODEX-*` se eliminaron de
   `docs/STATE.md` al terminar la prueba; no se tocó ningún otro contenido del archivo ni
   del historial real.
7. **Hallazgo nuevo, no corregido aún (no bloquea la prueba):** el servidor MCP
   `sony-a6000-knowledge` aparece como **"⏸ Pending approval"** en `claude mcp list` para
   esta sesión de Claude Code — requiere que el usuario lo apruebe desde una sesión
   interactiva (`claude`) para que las tools MCP (no solo la CLI equivalente) estén
   disponibles aquí. La prueba de este apartado usó la función Python real del servidor
   (idéntica lógica, mismo archivo fuente) como sustituto exacto mientras tanto.

## S33 — origen YC por handles Rendezvous (18-10-2026)

AllocShare `0x4390366c/0x43902df8` completo; 26 llamadas a `0x4379b44c`
desde 12 funciones, 13 inputs locales borrados por `0x43b03a5e` (0x104 bytes).
`+0x10` apunta a handles del trabajo; helper `0x43814ea0` puede activar
`+0xc8` y escribir `+0xd4=P+0xbc` en tres productores, propagado por copia.
APL llega a traducción de prefijos y configuración MMIO en bancos
`0xf3850400/0xf3950400/0xf3a50400`; no se identificó fin DMA físico.
Rastreados AllocRendezvous y despacho Image de VD_Sequence; segunda publicación
desde HS_Sequence `0x43790b68`. El backend DMM está importado y su entrada
inicial contiene cero: no se inventa destino ni dirección raster.
Auditor S33 PASS (SHA, 29 llamadas totales, inputs y proyecto idéntico).
Ruff: nueve avisos anteriores ajenos; auditor sin avisos nuevos; mypy PASS.
Sin cámara, instalaciones, commit (no hay `.git`) ni push.
[Informe S33](../docs/capture/s33-yc-rendezvous-producer.md).

## S35 — Objetos DFE y frontera estática APL/IRQ (18-10-2026)

Resueltos los cuatro objetos a Ofmt/Ifmt por constructores y RTTI, así como
sus vtables y +8 de OfSgc/OutSgc/RcvSgc/LnkSgc. Lectura/RMW de bit 0 en
SGC `0xfc0a1210/1310/1610/1710` y +0x1000 para unidad 1. No lectura/ack
APL recuperado ni cadena a EC/LM. Barrido: 49 instrucciones con inmediatos
objetivo y 479 coincidencias crudas; bit `0x00200000` sin semántica física
demostrada en `fact`. Sus usos en enable/disable IRQ no identifican esa causa.
**FRONTERA ESTATICA AGOTADA para esta vía concreta**, sin afirmar
imposibilidad estática universal. Hace falta routing/semántica hardware o
traza pasiva APL/DFE/IRQ/VD con identidad de handle/frame, sin flashear.
Siguiente incógnita: proveedor DMM `0x43561524`, entrada `tabla+0x2e4`,
productor Rendezvous y consumidor YC. No investigada en esta tanda.
[Informe S35](../docs/capture/s35-dfe-objects-static-frontier.md), exports
`analysis/ghidra/s35-objects*.{json,c}` y `s35-causes-scan.json`.
SHA verificado antes de exportar; proyecto `-readOnly -noanalysis` preservado.
Auditor primero falla por evidencia ausente, luego PASS. Sin cámara,
ejecución de firmware, instalaciones, flasheo ni push; sin `.git`, sin commit.
Tests de conocimiento: 67 PASS. Ruff auditor y mypy src/auditor PASS;
nueve avisos Ruff previos en tests ajenos. Mantenimiento de índice/grafo y
derivados ejecutado en cinco pasos, con totales estables.

## Pendiente real (no resuelto esta vuelta, con causa documentada)

- **Vigente S40 — contexto de modo:** API4000/4036/3023 y staging43edf684
  resueltos; faltan productores de snapshots alternativos y semántica exacta
  de bytes. No equiparar configuración software con exposición, habilitación
  de lectura o generación de cuadro IMX210. Cobertura de alias PARCIAL;
  no frontera estática agotada. Detalle al final en S40.

- **Actualización S37:** el definidor C++ ya es `libmprctrl.so`; no repetir su
  búsqueda. Getters DmmAccessPLA leen palabras de respuesta, sin conversión ni
  uso raster local que determine físico/lógico. AllocDmmMemory produce paquetes;
  el servicio OSAL 0x61003c entrega los pares. Su payload 0x18 comparte campos
  con S33, pero no su envoltura ni validaciones: identidad del slot av-cam y
  enlace a P+0x18c/+0x194/+0xbc y APL siguen NO_VERIFICADO. El enlace nominal
  de DmmCloseAndFree S30 sí queda verificado por símbolo, PLT/relocación y
  DT_NEEDED. [Informe S37](../docs/capture/s37-libmprctrl-dmm-extents.md).
- **S36 — proveedor DMM ausente de libInfraScalarMpr:** AllocDmmMemory y
  FreeDmmMemory son UND. El `void**` de SharedMemory viene de SysV `shmat`,
  con copia still demostrada; no cierra identidad con YC/Rendezvous ni
  cmd 2/id 0x55/longitud 0x70 del slot av-cam.
- Confirmación de descubrimiento MCP/skills desde una sesión **interactiva** (no `exec`) de
  Claude Code o Codex verdaderamente nueva: requiere al usuario, fuera de esta sesión.
- Aprobación del servidor MCP `sony-a6000-knowledge` en esta sesión de Claude Code (aparece
  "Pending approval"): requiere al usuario en una sesión interactiva de `claude`.
- Mapeo de lenguaje natural a nodo de `trace` (ver Fase 12.5): sigue siendo manual.
- La cadena EncodeStill documentada en `CONTEXT.md:26` no tiene cobertura en el grafo
  (direcciones fuera del corpus Ghidra/REA decompilado actual); analizarla requeriría
  decompilar ese rango, no es un bug del extractor.

## Fase 12.11 — retorno a la investigación principal: EFCS/SilentShutter/CAMERA_MAIN_SYNC (2026-10-18)

Instrucción del usuario: dar por cerrada la ampliación del sistema de conocimiento
y retomar la ingeniería inversa del shutter completamente electrónico, usando
Codex + MCP + índices existentes, sin repetir investigaciones cerradas.

1. **SetRead IMX210 descartada como consumidor de Silent.** `0x436d7e08` decompilada
   íntegra vía `codex exec` (proyecto `analysis/ghidra/silent-liro.gpr`, solo lectura):
   rechaza estado 0x11, calcula parámetros de registros sombra (`0x43ad9262` x4),
   escribe `0x4401c73a`, llama `GetImagerTemperature`; ningún tramo lee Silent+0x238/
   +0x210/+0x280 ni el switch de configuración 0x438b8902 (casos 1→11,2→8,4→12,8→13).
   No produce ni referencia buffer YC/DMA. Exports: `analysis/ghidra/
   imx210-setread-config-static-20261018.json` y 5 más con mismo prefijo. Añadido a
   `docs/capture/silent-imager-consumers.md`.
2. **Corrección de `CONTEXT.md`:** la sección "Próximo paso de investigación vigente"
   seguía pidiendo localizar "el alta/callback de 0x50004", pese a que S28 (17-10-2026)
   ya lo había cerrado (receptor InfraImaging en `0x4379744c`). Se corrigió para no
   reabrir trabajo cerrado; queda solo el productor sensor/DMA como pendiente real.
3. **Descartado un driver de kernel separado para el sensor.** Se listaron los ~90
   módulos `.ko` de las tres variantes de firmware disponibles (a6000/a6300/a7s) y se
   buscaron cadenas `IMX210`/`exposure`/`SilentShutter`/`EFCS`/`C_ImagerCtrl` en cada
   uno: cero coincidencias. `dmm.ko` (gestor de buffers, ya analizado en S16-S18) y
   `mcmn_drv.ko` (resultó ser GPIO de tarjeta MMC/ROM-write-protect, no "MechaCommon"
   como se había hipotetizado) se revisaron explícitamente y se descartaron. Esto
   refuerza que todo el control del sensor vive en `av-cam.bin` y las bibliotecas de
   servicio ya analizadas, no en un driver V4L2 independiente.
4. **Hallazgo nuevo: subsistema `CAMERA_MAIN_SYNC`/`DFECore`** (`docs/capture/
   s31-camera-main-sync-strings.md`). Búsqueda de cadenas en `av-cam.bin` (no
   decompilación) reveló un motor de temporización VD del sensor con logs
   (`VD_Drive`, `EC_VD_Post`, `VD_Post`, `No Read. cause:no expose/1st expose`,
   `camIntHandler0/1`) que ninguna sesión S16–S30 había tocado: todas se centraron en
   la capa de servicio (`libObj.so`/`libBizFw.so`/`dataflowInfraFramework.so`) en vez
   de este motor interno de `av-cam.bin`. Decompiladas 8 funciones vía `codex exec`
   (30 funciones totales exportadas, headless `-readOnly -noanalysis`, SHA-256
   verificado):

   | Función | Dirección | Rol verificado |
   |---|---|---|
   | `VD_Pre` | `0x43792a0c` | Prepara estado/callbacks, señala evento `0x1a/0x40` |
   | `VD_Sequence` | `0x4379155c` | Espera `0x40`, ejecuta secuencia, señala `0x100` |
   | `VD_Post` | `0x4379210c` | Espera `0x100`, encola `VD_Drive` |
   | `VD_Drive` | `0x4378f410` | Espera `0x1a/0x80`, comprueba VD actual, ejecuta trabajos pendientes |
   | `EC_VD_Post` | `0x4378f848` | Evita reprocesar un VD ya hecho; guarda su número en `0x43e992dc` |
   | `int_LM_Send1st_Handler` | `0x43792750` | Compara `0x43e992dc` con el VD actual; reprograma o marca EC pendiente |
   | `camIntHandler0` | `0x436cf954` | Acumula causas de interrupción (máscara `0x03380000`), despacha 4 slots de callback |
   | `camIntHandler1` | `0x436cf780` | Cuenta llamadas, log cada 1000 |

   Secuencia real: **`VD_Pre` →evento 0x40→ `VD_Sequence` →evento 0x100→ `VD_Post`
   →cola→ `VD_Drive`**, asíncrona y condicionada (no una llamada lineal). La variante
   EC llega por `0x437926fc` o el callback `0x43791454`, condicionado al predicado
   `0x4378e90c`.

   **VERIFICADO — acceso MMIO real:** `0x436ccd9c→0x43ad6006` escribe registros
   físicos entre `0xf3c30110` y `0xf3c3015c`. Es la primera evidencia estática de
   escritura directa a hardware mapeado en memoria encontrada en esta línea de
   investigación (su efecto físico no se ha observado: no hay cámara conectada).

   **PARCIAL — candidato a productor YC:** `VD_Sequence→0x43796954→0x4379bb90`
   (diagnóstico `SyncYCout.cpp`) envía parámetros por
   `0x43797afc/0x7b10/0x7b24/0x7b38→0x435a9928`; aquí vive la cadena "YC out window
   overflow". Es el candidato más cercano al productor sensor/DMA buscado desde S22/S30
   (`docs/capture/s22-sensor-to-yc.md`, `s30-pipelines-capture-encode.md`), pero no
   entrega dirección de píxeles, plano, pitch ni finalización DMA.

   **NO_VERIFICADO:** si `VD_Drive`/`VD_Post` marcan fin de lectura/DMA o solo
   temporización — recorren listas de trabajo con llamadas indirectas vía
   `0x43ad6034` cuyos destinos concretos no se resolvieron. Dato que falta y
   procedimiento no destructivo: resolver estáticamente esos destinos (siguiente paso
   recomendado) y, para comportamiento físico, una captura pasiva correlacionada de
   VD/lectura/interrupciones en hardware real sin flashear.

   Exports: `analysis/ghidra/camera-main-sync-final-decompilation.{c,json}`,
   `camera-main-sync-final-evidence.json`, `camera-main-sync-string-xrefs.json`,
   `camera-main-sync-entry-xrefs.json`.

Mantenimiento ejecutado tras ambas ediciones de documentación (`index_docs.py` →
`build_graph.py` → `export_corrections.py` → `index_docs.py` → `build_graph.py`):
total estable en 1226 entidades / 1977 relaciones en el paso de confirmación.

## S34 — APL/DMA, VD e interrupciones (18-10-2026)

Tres BL al helper `0x43814ea0` contrastados con blob/listing; direcciones,
registros MMIO y kick 0/1 ocurren síncronamente en el productor Image.
Ruta VD_Sequence demostrada; selección condicional de categoría HS para dos
productores, sin prueba de factibilidad conjunta de todos los predicados.
Sin llamador directo desde Post/Drive. El evento Drive `0x80` puede preceder
Sequence o venir de timer 4: no acredita fin DMA ni identifica cuadro físico.
Registrador `0x436cfae0`, cuatro slots y conversor `0x43ad68e0` resueltos;
falta correspondencia banco APL→estado/causa IRQ→callback→handle/VD→EC/LM.
Baseline propio anterior a apertura y hashes persistentes idénticos; 116
consultas exportadas (incluyen datos/interiores, no 116 funciones distintas).
Auditor primero falló por evidencia ausente; después PASS.
[Informe S34](../docs/capture/s34-apl-dma-vd-interrupts.md).
Ruff del auditor y mypy src/auditor PASS; nueve avisos Ruff previos en tests
ajenos sin tocar. Tests de conocimiento: 67 PASS. Mantenimiento en cinco pasos,
grafo 1419 entidades / 2725 relaciones antes de reindexar derivados.
Sin cámara/ejecución/flasheo/instalaciones/push. Sin `.git`, sin commit.

## Pendiente real (no resuelto esta vuelta, con causa documentada)

- **Cierre físico APL/VD:** S35 agota la vía de los cuatro objetos DFE:
  tipos y métodos resueltos, bancos SGC distintos de APL. Falta routing/estado
  hardware, semántica del bit `0x00200000` en `fact`, callback con handle/VD y
  latch frente a VD físico. Requiere especificación o traza pasiva correlacionada;
  no repetir resolución de vtables como pendiente. Ciclo físico NO_VERIFICADO.
- **Productor físico sensor/DMA del YC:** S33 cierra la construcción de input y
  su referencia Rendezvous, no quién llena los píxeles. Falta resolver proveedor
  importado DMM (`base+0x14`, entrada `+0x2e4`), quien satisface claves de
  `P+0x18c/+0x194` y del secundario `P+0xbc`, extents/pitch/formato y señal
  física de fin de escritura.
- Confirmación de descubrimiento MCP/skills desde una sesión interactiva nueva
  (no `exec`): requiere al usuario, fuera de esta sesión.
- Aprobación del servidor MCP `sony-a6000-knowledge` en esta sesión de Claude Code
  (aparece "Pending approval"): requiere al usuario en sesión interactiva de `claude`.
- Mapeo de lenguaje natural a nodo de `trace`: sigue siendo manual.
- La cadena EncodeStill documentada en `CONTEXT.md:26` no tiene cobertura en el grafo;
  decompilarla no es un bug del extractor.

## S58 — continuación de Claude y cierre offline (20-10-2026)

- Recuperados productores AE y emulación A7S bajo condiciones explícitas; seis informes en `docs/capture/s58-*.md`, 24 evidencias y 12 hipótesis. Se conservan exportaciones REA heredadas y firmware original.
- Correcciones S57: identidad SetExposure/SetRead, matriz IMX235; auditoría adicional corrige parser que omitía DEV83 y equivalencia incondicional de fórmulas productor/host. Consumidor de petición AGC `0x436f459c` probado en cinco modos.
- Verificación: 23 tests S58 y 60 S56/S57; campañas 600/600 y 300/300; ruff F/E9 y mypy con imports omitidos limpios en 25 archivos. Integridad: firmware 5/5, silent-liro 9/9, Ghidra 1328/1328. Detalle y comandos en [conclusiones](../docs/capture/s58-conclusions.md).
- Mantenimiento de índice/grafo/derivados ejecutado; correcciones A7S documentadas con enlaces explícitos. S51 A=NO/B=NO/C=NO; sin hardware, instalaciones ni push. Constructor A7S y semántica eléctrica permanecen fuera de cobertura.
- Validación de conocimiento: 61 tests ajenos al archivo MCP pasan. `test_mcp_server.py` se detiene por timeout de 15 s en `test_call_tool_get_current_state_reads_real_file` (espera asyncio/AnyIO); la suite completa se interrumpió tras 53 tests. No se modificó esa infraestructura; esta limitación queda abierta y el índice se comprobó mediante CLI.

## Próximo paso exacto

**Vigente tras S58 (20-10-2026):** recuperar el escritor del bloque `0x437876dc()+0xdd0` que `0x437aa65c` copia como 12 u16, y sus restricciones por modo hasta M/Tv/clk. Reutilizar `analysis/s58/rea-out/` y `analysis/s58/reproduce.py`; no repetir matriz de S57 ni apertura REA en frío sin necesidad. Inicialización real A7S y efecto eléctrico de integración siguen pendientes. Las instrucciones S40 de abajo son históricas, no el próximo paso vigente.

0. **Vigente después de S40:** seguir productores originales de mensajes
   case1/10 de438069f0 (43806a80/43806d50 toman mensaje+4/+8;
   43804cc8 toma staging43edf684), conservando offsets de snapshot+8
   frente al objeto contenedor. Fuentes API4000/4036/3023 del staging
   +24/+48/+458 ya demostradas. Seguir bloque+450..+458 hacia selectores
   IMX210 con identidad de objeto/campo/llamada; no inferir SetExposure,
   read-enable ni generación de cuadro desde copia de configuración.
   Alias y nombres de opción/FPS/píxel PARCIAL/NO_VERIFICADO.
   No reabrir AllocShare ni discriminación APL; no agotamiento universal.

0. **Después de S38 (antecedente):** resolver enum de formato PARCIAL S33:
   input+38←P+1b4←context[2]+28 y conversor 43814d24 hasta consumidores
   APL de formato, stride y tamaño. Asignar nombres solo con evidencia
   inequívoca. La vía ELF del slot DMM +2e4 en av-cam quedó agotada;
   receptor y productor YC siguen NO_VERIFICADO. Los pasos siguientes
   S37/S36/S35 son antecedentes, no prioridad vigente.

0. **Después de S37 (vigente):** localizar receptor OSAL **0x61003c** y
   resolver proveedor `av-cam base+0x14/+0x2e4`; seguir quién escribe los pares
   `reply+0x10/+0x14`, contrastar adaptadores/envolturas y una misma clave/ID
   hasta Rendezvous y YC/APL. Probar dominio y unidades con consumidor o mapeo;
   después pitch/formato, caché/reciclaje y fin DMA. La lectura de un campo
   llamado Adrs no sustituye esas pruebas. Los pasos S36/S35 debajo se
   conservan como historia; la búsqueda del definidor S36 ya está resuelta.

0. **Después de S36:** localizar definidor de
   `_ZN9DmmAccess14AllocDmmMemoryEiPt` y `_ZN9DmmAccess13FreeDmmMemoryEi`;
   verificar símbolo definido y seguir asignación/mapeo/mensajes. Resolver el
   slot av-cam independientemente antes de afirmar backend común. No confundir
   SharedMemory SysV con DMM. Ver [S36](../docs/capture/s36-libinfra-scalar-mpr-memory.md).

1. **Después de S35:** resolver proveedor DMM importado `0x43561524`, tabla
   `base+0x14`, entrada `+0x2e4`; seguir productor que satisface Rendezvous
   `P+0x18c/+0x194` y secundario `P+0xbc`, hasta lector YC real con handle,
   extents/pitch/formato y reciclaje. No investigado en S35. Ver
   [S35](../docs/capture/s35-dfe-objects-static-frontier.md).
   Para frontera física agotada: documentación hardware o traza pasiva
   correlacionada APL/IRQ/VD/handle en cámara sin flashear. No reabrir los
   26 llamadores S33 ni atribuir fin DMA al evento Drive `0x80`.
2. No ampliar más la arquitectura del sistema de conocimiento salvo defecto importante
   (instrucción explícita del usuario, Fase 12.10/12.11).
3. Si se prioriza: mapeo de constantes/direcciones en lenguaje natural a nodos de `trace`.
4. Si se prioriza, embeddings locales SOLO si un benchmark futuro demuestra mejora real
   sobre BM25+grafo (el benchmark v2 actual no lo justifica).

## S37 — definidor DMM y frontera de extents (18-10-2026)

SHA original/copia libmprctrl verificado antes de nm. Proyecto Ghidra nuevo,
copia 0444, cero dependencias y export final readOnly; silent-liro intacto.
1066 entradas exportadas con pseudocódigo/listing, incluyendo PLT y externos.
AllocDmmMemory/GetDmmExtList, cuerpo allocate/open/share, getters PLA y
close/free completos. Corregida atribución inicial de los getters a DmmAccess:
los mangled son DmmAccessPLA. Modo12 pide tipo 0x8125b/subarea3, no bytes.
Layout de paquetes distinto de respuesta raw. Dirección/tamaño son palabras
externas, no valores físicos demostrados. OSAL 0x61003c/payload0x18;
campos compatibles con S33, envoltura y validación diferentes. Slot av-cam
sin resolver. PLT libObj 0xdc180→JUMP_SLOT 0x102d024 importa el mismo símbolo
definido aquí, con dependencia directa; runtime no observado.
Auditor: primer fallo por findings ausente, luego PASS. Sin .git, sin commit.
PT_LOAD nativo confirma endpoint/tabla mode12; relocación y dependencia S30
auditadas. Ruff/mypy auditor y mypy src PASS; Ruff src/tests conserva nueve
avisos previos en tests ajenos. Conocimiento 67 PASS; mantenimiento en cinco
pasos estable en 1455 entidades / 2763 relaciones.
Sin firmware ejecutado/cámara/flasheo/instalaciones/push. Ver informe S37.

## S38 — frontera DMM/OSAL del blob (18-10-2026)

SHA original y memoria Ghidra coinciden. Solo silent-liro readOnly/noanalysis;
script sin mutaciones de programa, manifiestos .gpr/.rep intactos.
85 literales 61003c, 16 sin referencias; pool compartido y clientes DMM
exportados con helpers completos. Ningún servidor/alta recuperado: las
lagunas de referencias impiden afirmar ausencia universal.
readelf -d/-r y nm fallan: ORIL/LIRO, no ELF. PIC→440205c0→base→tabla
435410b4; slot 2e4 en 43541398 cero en archivo. **FRONTERA ESTATICA
AGOTADA** para resolución ELF/valor externo de ese slot en este blob.

**Pendiente real:** servidor/escritor de reply+10/+14 y binding externo
siguen sin identidad; ninguna misma clave/handle une extents a P/APL.
**Próximo paso exacto:** enum de formato PARCIAL S33,
input+38←P+1b4←context[2]+28 y 43814d24 hasta bits APL, stride y tamaño.
No atribuir formato por geometría ni fin DMA por evento Drive.
Ver [S38](../docs/capture/s38-dmm-osal-static-frontier.md), exports
`analysis/ghidra/s38-*.json/.c` y auditor con tabla stdout clasificada.
Auditor primero falló por consulta del export incorrecto, luego por findings
ausente; corregidos. Sin .git, cambios sin commit ni push.

Validación final S38: auditor PASS; Ruff/mypy auditor y mypy src PASS;
Ruff src/tests mantiene nueve avisos previos. Conocimiento 67 PASS.
Mantenimiento en cinco pasos estable: 1455 entidades / 2768 relaciones.

## S39 — enum de formato y discriminador APL (18-10-2026)

Ocho exports JSON/pseudocódigo s39-, SHA y memoria cotejados antes de cada
export. Proyecto silent-liro readOnly/noanalysis; ningún cambio de funciones,
contexto ni permisos de memoria. Manifiestos S38 coinciden antes/después.
Tres llamadores43814d24 pasan config+0c a4387a1fc/4387a758; actual43ef71a4,
anterior43ef71a0.4387a6c4 convierte grupos0/1/2/3→0/1/2/4 y436bec28
solo compara/guarda caché43e77ccc+unidad*4. Cambio→43acb7be→invalidación
y reset de referencias/perfiles; sin enlace demostrado a bits MMIO/pitch.
P+1b4 e input+38 usan índices distintos: conservar remapeo S33 separado.
Strings YUV/RAW/RTTI vecinas no establecen tabla de nombres por índice.
43ae8d56 confirma root43e9b548/context43e99208/context[2]=43e9baec;
VD_Pre43792a0c escribe43e9bb14 en437934b4/4379357c/437935aa/437935ea:
copia de contexto0+24, remapeo de+48/+458, o cero condicional.

**Pendiente real:** nombres de píxel, pitch, fuente tipada de opciones/FPS;
alias/copias masivas no resueltos exhaustivamente. Ningún cierre físico nuevo.
**Próximo paso exacto:** origen de context[0]+24/+48/+458 hasta solicitud o
tabla tipada y cálculo real de pitch por separado. Prioridad global S31–S39:
misma clave/handle/VD desde productor físico hasta fin DMA y cierre de
integración. No reabrir AllocShare ni tomar detección de cambio como registro.
No se declara rama estática universalmente agotada.
Ver [S39](../docs/capture/s39-image-format-apl.md),
`analysis/ghidra/s39-findings.json` y auditor con tabla stdout clasificada.
Auditor primero falla por findings ausente; luego verifica hashes, PIC,
TBB, consumidores y manifiestos. No hay .git: cambios sin commit ni push.

Validación S39: auditor PASS; Ruff y mypy del auditor PASS; mypy src PASS.
Ruff src/tests conserva los nueve avisos previos en cuatro tests sin tocar.
Conocimiento: 67 PASS. Mantenimiento de cinco pasos: 1455 entidades /
2771 relaciones, comprobación de estabilidad al cierre. Proyecto y binario
intactos; sin firmware ejecutado, cámara, flasheo, instalaciones ni push.

## S40 — origen del contexto de modo y frontera IMX210 (18-10-2026)

Solo silent-liro.gpr, av-cam.bin, -readOnly -noanalysis; SHA original y bytes
cargados cotejados. Manifiestos persistentes .gpr/.rep idénticos antes/después.
Sin releer S31–S38 ni reabrir AllocShare/AllocRendezvous/APL como hardware.

**VERIFICADO:** 43804cdc copia560B desde staging43edf684 a raíz43e9b548;
43804c82/43804d12→43b00d06 copian snapshotobjeto+8. Contiene los tres
campos+24/+48/+458; no basta consultar sus xrefs absolutas. Escritores
staging:438040bc←u8(solicitud+0a),comando4000;438040e8←cero condicional;
43803958←u8(solicitud+09),comando4036;43809378←u8(solicitud+0e),
comando3023 si solicitud+8!=0.437935ae fuerza raíz+48=0 localmente.
43b00cd0 alimenta snapshot+8 por copia560B;43b00bba lo inicializa a cero.
Tabla despacho43fff30c,220filas×12B: u16comando+0,punteroThumb+4,
byteflag+8; bytes restantes sin significado inventado. Filas4000/4036
resueltas a43804059/4380394d. Selector43ca3c21={1,1,0,1}, índice
raíz+450-1, condicionado por bit7(context[2]+269). Layout3023:
+450:u32←u8+8,+454:u16←u16+a,+456:u16←u16+c,+458:u32←u8+e.

**PARCIAL:** exhaustividad frente a alias/bases desplazadas/stores múltiples;
productores de cada snapshot alternativo. Barrido Ghidra215candidatos
450/454/458 y8977al añadir24/48, con función y xrefs por instrucción.
Otros objetos con+458 no son escritores de raíz por coincidencia numérica.
**INFERENCIA:** bloque alternativo con geometría (fallback320×240).
**NO_VERIFICADO:** opción de menú/FPS/nombre de píxel, enlace SetMode o
SetExposure, habilitación física de lectura y generación de cuadro.
La rama no está agotada estáticamente; no se sustituye por búsqueda genérica.

**Pendiente real:** contrato externo de bytes API y procedencia completa de
snapshots alternativos; no cerrar exposición/lectura/generación por copia.
**Próximo paso exacto:** productores de mensajes case1/10 de438069f0;
43804cc8 toma staging,43806a80/43806d50 toman mensaje+4/+8.
Después consumidores del bloque+450..+458 hacia
selectores IMX210 con identidad demostrada de objeto/campo/llamada.
Ver [informe S40](../docs/capture/s40-context-origin-imx210.md),
`analysis/ghidra/s40-findings.json` y exports JSON/.c s40-.

Validación: auditor primero falla por findings ausente, luego PASS;
Ruff del auditor PASS, mypy src/auditor PASS. Ruff src/tests mantiene nueve
avisos previos en tests ajenos sin tocar. Pytest conocimiento:67PASS.
Mantenimiento obligatorio en cinco pasos completado:1455entidades /
2772relaciones tanto en paso2 como en paso5; grafo estable tras derivados.
Sin .git: cambios sin commit. Sin ejecución firmware/cámara/flasheo/
instalaciones/producción/push. **VEREDICTO: CAMBIOS** para exhaustividad y
semántica IMX210; ACEPTO origen API/copia y RECHAZO equivalencia con sensor.

## S41 — productores de mensajes y valores IMX210 (18-10-2026)

Solo silent-liro.gpr/av-cam.bin con -readOnly -noanalysis, SHA y memoria
cargada contrastados en cada export. Sin releer S31–S39 completos.
Exports s41- JSON/.c, inventario y auditor en analysis/ghidra; informe
[S41](../docs/capture/s41-message-origin-imx210.md).

**VERIFICADO:** cola30001, hilo437fee08, alta437ff098; snapshot3030f,
hilo43806e38/alta43806e68.4356120c envío indirecto slot1d4,
43561260 recepciónslot1e0,435612ec liberaciónslot1f4.
Productores4000/4036:43816448/43818c1c/43817e20→4381a138
→435aa20c→4356120c, destino30001. Tablas43bc59e0={1,0,5} y
43bc5a50={1,2,0,3}, entrada de claves numéricas vía435613b0.
VD_Pre selecciona R+458/R+48 y remapea0,1,2,3→0,2,1,4 en+5cc.

**VERIFICADO:** productorcase1 43b01026:objeto+4/564B; productorcase10
largo43b00f62:objeto+6c0/5e0B, con copia previa43b00cd0→objeto+6c4.
Case10corto43b00f22:objeto+ca0/28B, sin bloque560B. Reciben mensaje+4
y mensaje+8 en43806a80/43806d50, este último soloestado2.
**PARCIAL:** envíos a8003030f frente a recepción3030f; bit31 de OSAL
sin resolver. No se presenta como un bucle local probado.
**INFERENCIA:** intercambio entre roles y almacén de configuración.
**NO_VERIFICADO:** nombre UI/PTP, constructor original3023, campo tipado
SetMode/SetExposure/VMAX/HMAX, lectura y cierre físico de integración.

**Pendiente real:** destino con bit31 y otro participante del protocolo,
productor3023 y origen de las claves4000/4036; valores+5cc hasta sensor.
**Próximo paso exacto:** resolver tablaOSAL slots1d4/1e0 y reserva;
tipar datos43bf37c4/43bf344e/43bf3736/43bf341e de filas3023 en
43ffe020/340/6d0/740: sus destinos437fd5e4/437fd3b0/437fd0b0/437fd11c
son getters Thumb de tres instrucciones, no productores de solicitudes.
Seguir lectores con identidadR+5cc hasta bloque44B4380f440/SetSequenceMode.
Slots de importación OSAL435410b4+1d4/+1e0 son cero en el blob;
frontera de implementación/enrutamiento, sin agotamiento universal A/B.
Se activa Línea C y se contrastan selector43842158, configuración43844e80
y consumidor438c828c/436d6f6c, sin convertir clase2 en captura validada.

Auditor primero FAIL por manifiesto ausente, después rechaza ARM temporal;
corregido Thumb sin modificar el proyecto: auditor PASS. Ruff auditor PASS,
mypy src/auditor PASS; nueve avisos Ruff previos en cuatro tests ajenos.
Pytest conocimiento67PASS; mantenimiento completo cinco pasos:
1455entidades/2774relaciones en ambas reconstrucciones, grafo estable.
SHA y manifiestos .gpr/.rep intactos. Sin .git: cambios sin commit; sin push.
**VEREDICTO: CAMBIOS** para cierre extremo a extremo y semántica IMX210.

Línea C contrastada:43845f30/34 común+210→banco+41c;
4384215e/19e flags+4bc y+41c seleccionanclase1/3 normalmente.
438421f0 diagnóstico+7e=3 fuerza2;438422bc/d2 control+36=1/+37=2
también permite2.438c830c llamaSetExposure salvo+4b9c!=0;
dispositivo2/3 fuerza0en+655.436d6fb6 leeparámetro+9 y backendacepta0..4:
clases1/3/2 producenmáscaras c4/d4/94; clase2 ademásusa+8/+14.
**NO_VERIFICADO:** fin electrónico, factibilidad de clase2 y cuadro válido.
**Pendiente real actualizado:** productores de los controles+36/+37 y
contrato de argumentosclase2, metadatos3023 y valoresR+5cc.
**Próximo paso exacto actualizado:** seguir llamadores de43842158 hasta
escritores+36/+37 valor2, y clase2 de436d6f6c hasta sincronía de cortinas.
OSAL bit31 requiere proveedor adicional; no repetir la resolución de slotcero.

## S42 — identidad de exposición y productores de control (18-10-2026)

Proyecto único silent-liro.gpr, av-cam.bin, readOnly/noanalysis; SHA esperado
antes/después y bytes cargados verificados. Manifiestos S38 .gpr/.rep intactos.
Sin releer S31–S40 completos, firmware ejecutado, cámara, flasheo, instalaciones,
producción ni push. Exports nuevos `analysis/ghidra/s42-*` e informe
[S42](../docs/capture/s42-exposure-call-identity.md).

**CORRECCIÓN VERIFICADA de S41:**436d6320 es wrapper y436d6f6c otro cuerpo.
436d6344/46/48/4a desreferencia contenedor/objeto/vtable y llama slot+28.
Constructor436d72e8 instala43fcc090;43fcc0b8 contiene436d6f6d.
Factoría436d6504 construye43e7f4a8 y43ad9054 lo publica en43e7f858,
contenedor devuelto por436d6118.438c830c llama wrapper: vínculo virtual
demostrado para ese backend; no BL directo ni alias ni traza física.

**VERIFICADO:**clase2 lee BYTE parámetro+08/+14 en436d7136/7142;
escribe buffers4401c6d2/4401c7ce y calcula u16objeto+3a0 en436d71e0.
No se transforma el ushort* decompilado en cargas u16 inexistentes.
**NO_VERIFICADO:**transporte físico, cortinas, sincronía VD_Drive/VD_Post,
unidades del tiempo, cierre electrónico y YC válido.

**VERIFICADO/PARCIAL:**4382e3a8/b2 copia C+94/+95 desde C=*(contexto+50)
a B43eae270+36/+37;437b5b14 conserva B para4384b268 y4384cb58→437b0480
publica c14B enG43ea6ad4.438412d0 pasa G al selector43842158.
Valor2 original y realizabilidad de rama pendientes.43845b68/70 son otro objeto,
no prueba del escritorG. Inventario ampliado de stores byte+36/+37 en listado;
no exhaustivo frente a código sin listar, copias o bases desplazadas.

**VERIFICADO:**R43e9b548+5cc=43e9bb14=ImgState43e9baec+28.
Lectores438553dc/4385558a pertenecen a43e18c60, descartados por identidad.
4380f440 copia0x44=68B a43e994d0;4378ea8c copia a43e99320,
4378eac6→4378e334 y4378e360→43795a60. Dependencia desdeR+5cc
**NO_VERIFICADO**, cadena solicitada se corta antes del bloque fuente43eea2e4.
Getters3023 devuelven secuencias compactas; descripción/metadatos es INFERENCIA,
parser/consumidor tipado NO_VERIFICADO. No confundir con configuración de sensor.

**Pendiente real:**escritor original C+94/C+95 y valor2, lectores IMX210+3a0
y transporte de los dos buffers, parser3023 y lectorR+5cc por aliasImgState+28.
**Próximo paso exacto:**seguir C=*(contexto+50) del productor4382dd78,
manteniendo B43eae270→G43ea6ad4→43842158; identificar stores C+94/+95
antes de atribuir modo mecánico/EFCS/clase2 a opción de usuario. En paralelo
lógico, sin aperturas simultáneas del proyecto, lectores objeto+3a0 y
ImgState+28 con identidad; consumidor indirecto de filas3023.
Sin agotamiento estático declarado; Línea E no activada aunque existe
firmware/extracted/a6300-fw201. No reabrir bit31 OSAL sin evidencia distinta.

Auditor primero FAIL por manifiesto ausente y después PASS. Ruff: nueve avisos
previos en tests ajenos, ninguno nuevo en auditor. Mypy src/auditor PASS.
Sin .git: cambios sin commit. **VEREDICTO: CAMBIOS** para cierre físico/origen2;
ACEPTO identidad virtual/usos byte, RECHAZO equivalencia de cuerpos y
consumidores por offset sin identidad. Validación del grafo al cierre debajo.

## S43 — PIC de exposición y revisión de códigos de modo (18-10-2026)

Proyecto silent-liro.gpr/av-cam.bin exclusivamente readOnly/noanalysis;
SHA esperado antes/después y memoria cargada contrastados. Auditor comprueba
manifiestos históricos .gpr/.rep. Sin releer S31–S42 completos, ejecutar firmware,
cámara, flasheo, instalaciones, producción ni push. Sin .git, sin commit.
Exports `analysis/ghidra/s43-*`; [informe S43](../docs/capture/s43-exposure-mmio-and-lock-codes.md).

**VERIFICADO:** PIC4401eee4, slots436d72a0..dc resueltos a estructuras
4401c6xx–4401caxx con IDu16 y valorbyte+2; primeros IDs3..8, segundo grupo144..149.
Clasificación b3: registros preparados en software, sin MMIO literal ni vtables.
Formato completo/transporte físico PARCIAL; nombres de registros INFERENCIA.
43ad9a40/43ad99d4 solo guardan estado: iVar18 ya es objeto+fc, no base PIC.

**ACEPTO**4380e020/43902718 como log/trace. **RECHAZO** hipótesis AF/lock:
43ca2585 contiene SetSequenceMode img/fratechg/clamp/bb_out/cap_end;
4380e43c tiene ImgMode/IMAGE_FRAME_RATE/SYNC_RAW_OUTPUT_SIZE y consulta
virtual+94→43ad95ce→43ad9438 (búsqueda en tabla de modos, devuelve ff si ausente).
No asignar nombre SetSequenceMode a4380e43c: cadena pertenece a4378e334.
Relación R+5cc→bloque y escritura física desde esta rama NO_VERIFICADO.

Virtual+4c436d92e0 busca dos modos y llama virtual+a8 con índices/flags.
Virtual+10436d8ff4 copia0x70B desdeobjeto+180, sin transporte. Listados temporales
sin crear funciones; primer rango atravesó pool, reintento con parada en retorno.
Inventario515 matches+3a0/stores+94/+95: candidatos sin identidad, no exhaustivo.

**Pendiente real:**transporte de registros preparados, lector IMX210+3a0,
escritor original C+94/+95 y valor2, dependencia R+5cc y parser3023;
cortinas/VD/fin electrónico y YC válido NO_VERIFICADO.
**Próximo paso exacto:**consumidores de registros4401c6xx–4401caxx por slots PIC;
resolver virtual+a8 llamado436d938c desde436d92e0 con índices de modos/flags.
Después C=*(contexto+50) en4382dd78 y stores originales+94/+95, conservando
B43eae270→G43ea6ad4→43842158. No reabrir OSALbit31; Línea E no activada,
sin agotamiento estático global. Virtual+10 queda cerrado como getter software.

Auditor S43 PASS tras distinguir listado de decompilación en dos métodos no
definidos. **VEREDICTO: CAMBIOS** para cierre físico, tareas1–3 documentadas.

Validación final S43: mantenimiento completo index_docs→build_graph→
export_corrections→index_docs→build_graph. Ambos builds:1455 entidades,
2777 relaciones,58 CORRECTS/SUPERSEDES; grafo estable. Export56 filas de
correcciones y55 preguntas; índice372 archivos/2833 secciones.
`pytest tests/knowledge -q`:67 PASS (11.50s). Auditor SHA/PIC/.gpr/.rep PASS.
Ruff auditor PASS; comando solicitado src/tests conserva9 avisos anteriores en
tests ajenos, sin cambios allí. Mypy src+auditor:sin problemas en6 archivos.
Sin avisos nuevos en lo tocado. No se ejecutó otro agente ni revisión Claude.

## S44 — consumidor de registros y tabla de modos (18-10-2026)

Solo silent-liro.gpr/av-cam.bin, readOnly/noanalysis; SHA esperado antes/después,
memoria cargada y manifiestos históricos .gpr/.rep contrastados. Sin guardar,
ejecutar firmware, cámara, flasheo, instalaciones, producción ni push.
Sin releer S31–S43 completos ni reabrir AF/OSALbit31.
Exports `analysis/ghidra/s44-*`; [informe S44](../docs/capture/s44-register-consumer-mode-table.md).

**VERIFICADO:**436d839c→getter436d79b0→tabla43fe995c,119 punteros;
436d75f8 consumeIDu16 y byte+2, backendobjeto+298 empaqueta con
436d5e04→43ad8fe0→43ad8fa2. Fin/overflow→436d5cdc→436d5ed0
escribe bytes como palabras en bancoA+40+4*i;436d5f60 pulsa1→0→1 enB+8.
Tabla43bc14e8 da bancosf3c00300/fc088300/fc089300 y controles asociados;
constructor mapea variantes a canales{1,2,0}. Esperas evento18 no prueban
fin de integración. Clasificaciónb3 de S43 permanece correcta.

**VERIFICADO:**virtual+a8=436d65b8 compara nibbles altos de fila43fe9b74,
destino4401c6ae=registroID0+2, usando dos índices sobre13 modos;
ignora flags, devuelve1 si difieren,0 si coinciden. Sin escritura/transporte.
**PARCIAL:**4385cf2c produceP+95=2 con condiciones de campos y sobrescritura
posterior posible a8;P=raíz+2bc en437b43b4.4385ca3c inicializaP+94/+95.
Alias conC=*(contexto+50) de4382dd78 sin demostrar;43ef2474 es snapshot
condicional de0x6b0B, no identidad probada.44004894 es tablaID/puntero.

**Pendiente real:**identidadP/C y escritor originalC+94/+95;lectoresIMX210+3a0,
semántica físicaID0/IDs3–8/144–149 y enlace a integración/VD/cortinas;
dependenciaR+5cc/parser3023 sin cerrar. Captura electrónica NO_VERIFICADO.
**Próximo paso exacto:**resolver origen del contexto pasado a437b5b14 y su
campo+50 hasta raíz+2bc/snapshot43ef2474. Solo entonces trasladar condiciones
de4385cf2c aC y seguir valor2 haciaB43eae270→G43ea6ad4→43842158.
Después lectoresIMX210+3a0 y significado físicoID0. No repetir consumidor ni
virtual+a8. Sin frontera estática agotada: Línea E no activada.

Auditor S44 primero FAIL por manifiesto ausente y después PASS:119 registros,
13 modos, nibbles,MMIO,SHA y .gpr/.rep. ACEPTO consumidor/MMIO/virtual+a8;
RECHAZO alias por offset y cierre físico. **VEREDICTO: CAMBIOS** para estos
pendientes. No hay .git utilizable: cambios sin commit;sin revisión por agente.

Validación S44:pytest tests/knowledge67 PASS(6.15s);ruff auditor PASS,
mypy src/auditor PASS;ruff src/tests conserva9 avisos previos en tests ajenos.
Auditor de SHA/.gpr/.rep PASS. Primer ciclo estable1455/2778, pero contenía
un falso CORRECTS generado por una frase de auditoría sobre S43;se reformuló
esa frase sin tocar el extractor. Mantenimiento completo repetido:
ambos builds1455 entidades/2777 relaciones/58 CORRECTS/SUPERSEDES;estable.
Índice373 archivos/2844 secciones;export56 correcciones/55 preguntas.

## S45 — identidad del contexto y consumidor del timing (18-10-2026)

Solo silent-liro.gpr/av-cam.bin, readOnly/noanalysis; SHA esperado y memoria
contrastados por exportador, manifiestos .gpr/.rep intactos por auditor.
Sin guardar, cámara, firmware ejecutado, instalaciones ni push.
Exports `analysis/ghidra/s45-*`;
[informe S45](../docs/capture/s45-context-identity-and-physical-closure.md).

**VERIFICADO:**437b4eb4 construye contexto43eaadd8→437b4df0→437b5b14;
437b4f2c copia0xb0 desde43e993a4, reconstruido enVD_Pre desde raíz
copiada43e99514.43ae8d56 fija contexto+50=raíz+1e6c=C43e9b380;
43ae8faa copia1a4 desde raíz original43e9b548+1e6c=43e9d3b4.
**PARCIAL:**P de437b43b4=padre+1454 en dos llamadores;falta copiaP→C,
sin atribuir aC condiciones de4385cf2c ni alias con snapshot43ef2474.

**VERIFICADO:**vtableIMX210+74=43ad9203;getter43ad9202 leeobjeto+3a0.
Wrapper43ad90b6, llamado438c835e, conserva retorno para cálculo de
captura+570;43795dec→43ad3b92→436c74c8 lo consume hasta43ad2bd6,
escritura base+220, condicional por caché. Controlador43e16d28 publicado
desde owner43e15f18+e10. **PARCIAL:**base=*(43e16d2c),cero enarchivo,
sin escritor inicial identificado;MMIO/integración/VD/cortinas NO_VERIFICADO.
Semántica eléctricaID0/IDs3–8/144–149 no recuperada ni agotada.

**Pendiente real:**escritor/copia de43e9d3b4+94/+95 hastaP/B/G y base
43e16d2c hasta destino físico+220;semántica de integración/lectura/cortinas.
La serie explícitaS40–S45 termina aquí;hito continúa abiertoS46+.
No hay agotamiento estático real: no se activa Línea E ni se abre A6300.
**Próximo paso exacto:**resolver escritores43e9d3b4+94/+95,incluyendo offsets
partidos y copias,antes de transportar valor2 desdeP=padre+1454/snapshot.
Resolver inicialización43e16d2c desde owner43e15f18;después contrastar
base+220 con controladorVD. No repetir getter+74,consumidor/virtual+a8,
OSALbit31 niAF. No inferir captura electrónica desde escritura indirecta.

Auditor S45:FAIL por resumen ausente;FAIL por transcripción decimal de raíz/C;
corregida contra literales;PASS de SHA/memoria/.gpr/.rep/contexto/getter.
ACEPTO identidad del contexto y consumidor de timing;RECHAZO aliasP/C por
offset y cierre físico. **VEREDICTO: CAMBIOS**. Sin .git utilizable:sin commit.

Validación S45:pytest tests/knowledge67 PASS(6.72s);ruff del auditor PASS;
mypy src+auditor PASS(6 archivos). Ruff src/tests conserva los9 avisos previos
en tests ajenos,sin avisos nuevos en lo tocado. Auditor final SHA/.gpr/.rep PASS.
Mantenimiento completo:index_docs→build_graph→export_corrections→index_docs→
build_graph;ambos builds1455 entidades/2777 relaciones/58 CORRECTS/SUPERSEDES,
grafo estable. Export56 correcciones/55 preguntas. Índice374 archivos/2856 secciones.

## S46 — base VD y escritor directo de C (18-10-2026)

[Informe S46](../docs/capture/s46-vd-base-and-context-identity.md),
exports `analysis/ghidra/s46-*`. Solo silent-liro.gpr, siempre readOnly/noanalysis,
sin guardar ni crear funciones. Firmware ORIL en base lógica `0x43541000`;
SHA esperado verificado antes/después y memoria cargada contrastada por exportador.
Manifiestos S46 de los 10 archivos protegidos (firmware, .gpr y .rep) idénticos.
Sin cámara, firmware ejecutado, flasheo, instalaciones ni git.

**VERIFICADO:** `0x436c2250` llama inicialización `0x436c6f3c` con owner
`0x43e15f18`. En `0x436c6f74` entrega owner+e10=`0x43e16d28` y
literal `0x436c71f8=0xf3120000` a `0x436c7950`. BL `0x436c7964`
→ `0x43acee66` escribe base en `0x43e16d2c`; r1 conservado en ensamblador,
aunque el pseudocódigo lo omita. La escritura condicional de S45 en
`0x43ad2bd6` tiene destino `0xf3120220`. Sin atribuir fin de integración.

**VERIFICADO:** C fuente=`0x43e9d3b4`, construido por raíz+1e40+2c
en `0x43792f8e/0x43792f94` y entregado a `0x437da078` en `0x43792f9c`.
Dispatcher `0x43ed461c`, callback vía `0x437da314` con r1=C.
Tabla `0x43ff8308`, fila `0x43ff8adc={0xce,0x43ff7414,1}`;
slot contiene `0x437dad79`. Callback Thumb `0x437dad78` copia payload4B
desde `0x43ed4620` a scratch `0x43f7bbf4`. Primer u16!=0 →
`0x43e9d448=1`, `0x43e9d449=low8(segundo u16)`; primer u16=0 → ambos cero.
Stores exactos `0x437dad92/0x437dad9a/0x437dad9e`, selección de tabla con
byte `0x43e959eb=0`, clave0xce y cursor de callback válido.

**PARCIAL:** propagación condicional de (1,2) por copia1a4 a C consumido
`0x43e9b380` y copias B=`0x43eae270`→G=`0x43ea6ad4`→`0x43842158`.
No prueba un payload concreto, ausencia de sobrescritura en toda ejecución,
factibilidad dinámica ni efectos eléctricos. P=padre+1454 y snapshot
`0x43ef2474` siguen sin alias/copia a C; no se transplantan condiciones de P.
El scratch nuevo tampoco es ese snapshot.

**Pendiente real:** productor de los dos u16 del payload clave0xce;
orden completo de preparación/copia; relación P/C no demostrada;
semántica eléctrica de `0xf3120220`, integración y cortinas NO_VERIFICADO.
**Próximo paso exacto S47:** argumento4 de `0x437da100`, copia a
`0x43ed4620=0x43ed461c+4`, localizar productor de clave0xce y demostrar
sus dos u16/orden frente a `0x43792f9c/0x4379409e`; después semántica VD.
No reabrir OSALbit31, hipótesis AF ni consumidor/virtual+a8; sin agotamiento/Línea E.

**Validación:** auditor FAIL inicial por resumen ausente, luego PASS;
contrasta bytes del setter, literal base, PIC, fila de tabla, slot Thumb,
scratch y ramas/stores del escritor. Integridad final PASS en 10 archivos.
Pytest tests/knowledge:67 PASS(5.16s). Ruff de ambos scripts S46 PASS tras
corregir dos comparaciones constantes del auditor; src/tests conserva nueve
avisos previos en cuatro tests ajenos, sin cambios en ellos. Mypy src+ambos
scripts:PASS(7 archivos). Listados temporales suplen funciones no definidas;
no se confunden exports .c vacíos con decompilación válida.
ACEPTO base VD y escritor C con identidad/condiciones; RECHAZO alias P/C
y cierre físico. **VEREDICTO: CAMBIOS** para el hito físico. Sin git/commit.

Mantenimiento completo S46: index_docs→build_graph→export_corrections→
index_docs→build_graph. Ambos builds:1455 entidades/2777 relaciones,
58 CORRECTS/SUPERSEDES; total de relaciones idéntico, sin autocontaminación.
Export56 correcciones/55 preguntas; índice375 archivos/2866 secciones.
La anotación final de resultados se reindexa con el mismo ciclo completo.

## S47 — entrada del payload y orden de copia C (19-10-2026)

Informe: `docs/capture/s47-payload-producer-and-order.md`.
**VERIFICADO:** nuevas llamadas `0x437896ce/0x4378975a` a `0x437d9f9c`,
recuperadas de bytes Thumb fuera de funciones definidas. Callback receptor
`0x43789cc0` registrado en `0x4378a3e6` con ID `0x301d7`.
Tabla índice0 `0x43ff23b0`, fila `0x43ff29b8={0xce,0x43789709}`;
handler `0x43789708` copia0x140B a `0x43e95420` por slot GOT `0x4401f0c0`.
Payload en `0x43e9543c/+2` → argumento4 de `0x437da100` → copia0x124B
a `0x43ed4620` → despacho `0x437da078/0x437da2d8` → `0x437dad78`.
Solicitud sintética `0x43ed44dc` es otra entrada; no es el buffer recibido.

**VERIFICADO:** callback ANTES de copia C en misma invocación de VD_Pre.
CFG con2276 nodos y5TBB: `0x43792f9c` domina `0x43794096`; no hay retorno
desde `0x4379409a` al despacho. Raíz destino `0x43e99514`, origen `0x43e9b548`;
subcopia `+0x1e6c`,0x1a4B en `0x43ae90ce`, desde `0x43e9d3b4` a
`0x43e9b380`. Incluye `+0x94/+0x95` → destino `0x43e9b414/0x43e9b415`.
No se refuta S46 por orden; `0x4379409e` es llamada posterior, no la subcopia.

**PARCIAL:** productor original de u16 en paquete+1c/+1e anterior a entrada
`0x43789cc0`, valor2 y propagación a B/G. Nuevo servicio+1ec del registrador
`0x435612b4`: slot `0x435412a0=0`; proveedor/contrato sin resolver.
No se reabren bit31/S41, AF/S43, consumidor/virtual+a8/S44 ni alias P/C/snapshot.
**NO_VERIFICADO:** relación VD/cortinas; punto opcional3 aplazado porque1 sigue
incompleto. No se concluyen rutas independientes. Clases1–3 sin nuevo cierre físico.
**Próximo exacto S48:** proveedor/contrato del registro ID0x301d7, entrada+1ec,
y productor del paquete clave0xce, stores+1c/+1e antes de `0x43789cc0`.
Hito S46–S52 abierto. ACEPTO cadena interna/orden; RECHAZO productor original
identificado y cierre físico. **VEREDICTO: CAMBIOS**.

**Validación S47:** auditor FAIL inicial (findings ausente), después PASS:
2787 registros de listado contrastados con firmware, tablas/PIC, thunk mixto
Thumb/ARM, rango y dominancia. Huellas antes/después PASS,10 archivos protegidos.
Ruff scripts S47 sin avisos nuevos; src/tests conserva9 avisos en4tests ajenos.
Mypy src+4scripts S47 PASS(9archivos). Una consulta concurrente fue rechazada
por bloqueo del proyecto; se repitió secuencialmente, sin forzar locks ni guardar.
Sin git/commit/push, firmware ejecutado, cámara, flasheo ni instalaciones.
Pytest conocimiento: **67 PASS** (6.01s), log `s47-pytest.log`.
Mantenimiento completo index→graph→export→index→graph: **1455 entidades y
2778 relaciones en ambos builds**, idénticos;59CORRECTS/SUPERSEDES.
Export57correcciones/56preguntas; índice376archivos/2875secciones antes de
esta anotación final. Log final `s47-maintenance.log`; se repite el ciclo completo
tras registrar resultados, sin editar fuentes entre sus dos builds.


## Hito REA independiente (19-10-2026)

REA 6.5.0 usado como Línea B sin tocar `silent-liro.gpr/.rep` ni S1–S48. Experimentos en
`analysis/rea-independent/` (pre-registro, guiones, salidas, manifiestos SHA-256 inicial/final idénticos).
Resultados, tiempos, coincidencias/diferencias y recomendaciones: `docs/capture/rea-independent-milestone.md`.
Resumen: libmprctrl (8 funciones) coincide; av-cam completa en ~8 min con timeout ampliado y 78 % de cobertura de entradas históricas;
sin evidencia nueva de obturador electrónico. No se rediseñó el sistema de conocimiento.


## S50 — investigación paralela Claude + Codex (19-10-2026)

Dos procesos con sesiones REA propias (`analysis/s50/`). Resultado y límites en `docs/capture/s50-parallel-conclusions.md`. `0xb6` inerte; filas `1/2/3/6` = nº de callbacks (corrige S49); override `C+0x94/95`→modo 0..7 solo hacia estado; pregunta final NO_VERIFICADO. SHA 1490/1490 intactos. Próximo S51: consumidor físico del modo / `C_Imager::SetMode` y semántica ID1/100/101.

## S52 — trazado de cortinas y propagación de clase 0 (Claude + Codex, 19-10-2026)

Agentes: A Claude (Opus 5.5, medium, `work/claude/`), B Codex (`gpt-5.6-terra`, medium, `work/codex/`; R1 superficial → R2 dirigida
con REA+Unicorn → validación cruzada). Sesiones REA separadas y cerradas. Instalado `~/.venvs/re` (capstone/unicorn/keystone/lief, ruff), ver
`environment/`. `session_daemon.py` admite `REA_DAEMON_RSS_MAX_MB`. Resultado: Silent A7S marca el paquete CAIF y omite esperas
mecánicas (no suprime envíos); `+0x748`≙A6000 `+0x740` latente; clase 0→`param+9` VERIFICADA (discrepancia A/B resuelta por el
coordinador, `analysis/s52_coordinator_check.py`); corrección `cfg2+4|=8` en todos los ShutMode IMX235. P5 NO VERIFICADO, S51 vigente.
Detalle: `docs/capture/s52-parallel-conclusions.md`. Hashes 8/8 y manifiestos intactos. Próximo: parser CAIF Darwin (bit `0x20`).

## S53 — Darwin: transporte MSS y parser CAIF (Claude, 19-10-2026)

Solo Claude (Opus 5.5), sin subagentes ni Codex. Ghidra headless sobre las tres ROM Darwin (`analysis/s53/`), capstone y LLVM;
REA no se abrió (mismo motor; lote directo más rápido para ROM pequeñas). Vista ELF nueva `analysis/a7s-darwin-rom-analysis-view.elf`.
Resultado: receptor = mss-async ID `0x0c` sobre MFS5; parser A7S `0x18396` / A6000 `0x17f8c`; A7S consume el bit Silent `0x20`
y deja de accionar P4D/P4E; A6000 no. Escenario B; S51 vigente. Detalle: `docs/capture/s53-conclusions.md`. Suite 42/42.
Próximo (no iniciado): traza pasiva autorizada de `MSS_SO_DWN`/bobinas, consumidor LIRO de `CA_1ST_CURTAIN_START`, efecto del tipo 0.


## S54 — P4C, tipo 0 y sincronización BIONZ (20-10-2026)
- Hecho: rastreo de escritores P4C en ambas ROM Darwin (`analysis/s54/p4c_scan.py`), esquema BIONZ (SENS_B/GPIO_9, A6000 y A7S), diff tipo 0 ↔ Silent, origen del byte de tipo,
  primitivas GPIO de BIONZ (`analysis/s54/bionz_gpio_calls.py`, REA sesión única 440 s cerrada). Informes `docs/capture/s54-*.md`, matriz `analysis/s54-evidence-matrix.json`, tests `tests/test_s54_p4c.py` (21/21).
- Herramienta: REA `rq.py` (cliente compacto del demonio) en `analysis/s54/rq.py`; ruff instalado en `~/.local/bin` (sin avisos en archivos nuevos); sin dependencias nuevas de proyecto.
- Frontera: consumidor BIONZ de P4C (pares pin→(canal,bit) sin inicializar en `av-cam`), escritor del byte de tipo, polaridad/rearme P4C, IMX210 (sin datasheet).
- Próximo exacto: `av-cam` A7S 3.20 — barrido `gpio_get` y localizar el inicializador de `0x43e77298…`.


## S55 — origen de pares GPIO, A7S vs A6000 (20-10-2026)
- Hecho: equivalentes GPIO en A7S (`get 0x43b585c2, cfg 0x43b58534, set 0x43b585a0`), tabla de sitios (`analysis/s55/gpio_calls_diff.py`), descubrimiento de la base de backup BK4 (`analysis/s55/bk4.py`), inicializador de pines
  (`pin_init.py`), usuarios de variables (`var_users.py`), eventos/MMIO (`events_mmio.py`). Informes `docs/capture/s55-*.md`, matriz `analysis/s55-evidence-matrix.json`, tests 16/16.
- Herramientas: REA (1 sesión, `GHIDRA_MAXMEM=6G`, cerrada) para confirmar wrapper `+0x2e0` y empaquetado de pines; capstone/readelf/llvm-objdump para el resto; sin dependencias nuevas.
- Corrección: «variables sin escritor» de S54 es incorrecta (escritor `0x436bcef4`, store vía GOT).
- Frontera: banco de los `GPIO_n` (sin «S»), `SENS_B`, valores por unidad (`Backup.bak`), IMX210.
- Próximo exacto: escritores de `0xf2a10000–0xf2a30000`/`0xf2400000` (candidato SENS_B); IDs dinámicos de `0x43716dd0`; traza pasiva autorizada.


## S56 — transporte de registros del IMX210 (20-10-2026)
- Hecho: cadena `SetExposure → registros sombra → Execute → consumidor 0x436d75f8 → formateador P2S → RAM P2S(DFE0) 0xfc088340` reconstruida y **emulada con Unicorn** (`analysis/s56/{p2s_emu,setexp_emu,rec_users,xr,rq}.py`); REA (sesión única `GHIDRA_MAXMEM=6G`, cerrada) confirmó consumidor y llamadores. Informes `docs/capture/s56-*.md`, matriz `analysis/s56-evidence-matrix.json` (`build_matrix.py`), tests 26/26. Dependencia nueva: `unicorn` (pip --user).
- Hallazgos: IDs = direcciones 16 bit; trama `81|len|81|AH AL|datos`; `svd/shd/spl` = IDs 3–8; ShutMode→ID1; pulso SSB; CISIF = receptor; A7S mismo P2S con registro de 5 B.
- Frontera: semántica de registros IMX210 y de `CIS0_SHT_RST→XPI`; consumidor SENS_B; origen de `0x43eb35d0` (tiempo→banco).
- Próximo exacto: traza pasiva CIS0/XPI/VD (decodificable con `p2s_emu.frames`) o rastreo estático de `0x43eb35d0+0xc4..0xd8`. S51 se mantiene.


## S57 — semántica de ID1, SSB, svd/shd/spl, Silent IMX235, XPI y sincronía P2S (20-10-2026)
- Hecho: escritores y bits de ID1 (seguimiento GOT→registro `analysis/s57/bitops.py`), rejilla 13 modos × 5 ShutMode × SSB con el código real (`analysis/s57/{emu57,id1_grid}.py`, 130 casos con dos rellenos de memoria), productores/orden de SSB, mapeo exacto svd/shd/spl (`c_timing.py`, 400/400), cadena de producción hasta el banco `0x43eb35d0`, matriz efectiva IMX235 (`imx235_matrix.py`), esquema XPI, modos de SyncMode del P2S (`sync_modes.py`).
  Informes `docs/capture/s57-*.md`, matriz `analysis/s57-evidence-matrix.json` (33 entradas, H57-1…10), tests `tests/test_s57_imx210_exposure.py` 34/34.
- Herramientas: REA (1 sesión, `GHIDRA_MAXMEM=6G`, cerrada; salidas en `analysis/s57/rea-out/`; cliente `analysis/s57/rq.py`), Capstone y Unicorn; sin dependencias nuevas; `ruff --select F,E9` limpio; mypy no instalado.
- Hallazgos: ID1 combinado; SSB = strobe de aplicación de exposición (no fin); svd cuenta pasos del host/VD; Silent A7S = modos de lectura; AdjustCmd fija las banderas +0x277…+0x27c; XPI sin controlador visible.
- Correcciones: B de ID1 es copia de A (no valor propio); no se reproduce «ShutMode 4 escrito en captura»; el pulso ocupa dos bloques de trama separados por una cabecera de 5 B.
- Frontera: productor AE de las filas de banco (`S+0xC4…0xD8`), unidades de svd/shd/spl, ID1 eléctrico, XPI, evento que activa las banderas del P2S, tabla de categorías de AdjustCmd.
- Próximo exacto: `trace_native_values` sobre el pipeline AE; o traza pasiva CIS0/XPI/VD autorizada. S51 se mantiene.


## S59 — Claude + GPT-6.1 Sol: bloque IMX210 `+0xDD0` y constructor real C_Imager A7S (20-10-2026)
- Hecho: GPT (`codex exec`, gpt-6.1-sol/medium) recuperó el escritor `0x43b00da0` del bloque `0x437876dc()+0xdd0` (publicación `0x43b00dd4`, fuente `obj+0xd64`), corrigió la atribución de `clk` de S58 y delimitó VdNum/host (`docs/capture/s59-sol.md`, `tests/test_s59_sol.py` 11/11). Claude localizó y emuló el constructor real `C_Imager` `0x436f3fc0` y rehízo los escenarios (`analysis/s59/claude/`, `tests/test_s59_claude.py` 9/9). Revisión cruzada de GPT (solo lectura) → CAMBIOS aplicados.
- Hallazgos: M no es constante de construcción (payload externo); S58-C base/tramas P2S eran artefactos (real `0xfc088300`, 3 tramas), registros intactos (100 escrituras); mensajes `0x1000/0x1001` = lista blanca de modos; Execute sin ramas de registros exclusivas de Silent bajo depuración `0xff`; consumidor de ganancia con único llamador directo.
- Herramientas: REA (1 sesión A7S + 1 sesión A6000 de GPT, cerradas), Capstone, Unicorn; sin dependencias nuevas.
- Frontera: emisor del payload de `0x438069f0` (origen M/Tv/clk), receptores de `0x1000/0x1001`, servicios Darwin/OSAL stub, física del sensor.
- Próximo exacto: sembrar Thumb en los emisores/receptores anteriores; traza pasiva CIS0+XPI+VD autorizada. S51 se mantiene.

## S60 — emisor de mensajes IMX210 y receptores A7S (20-10-2026)
- Hecho: GPT-6 Sol (`codex exec`, medium) localizó la tarea receptora `0x43806e38` y los emisores de respuesta (`docs/capture/s60-sol.md`, 6 tests); cortó por límite de uso antes de su mensaje final y la auditoría cruzada no se obtuvo. Claude (`docs/capture/s60-claude.md`, 12 tests) resolvió la naturaleza de `0x1000/0x1001` (trazas) y localizó los productores del bloque `obj+0xe20`.
- Hallazgos: ver `docs/capture/s60-conclusions.md`. Corrección a Sol: TBH base `0x43806a08`.
- Herramientas: Capstone, Unicorn (OSAL sustituido), sin REA nuevo ni dependencias nuevas.
- Frontera: petición caso 3/9 y bit 31 del handle, productores de `obj+0x168/0x16a`, consumidor de la cola de trazas, física.
- Próximo exacto: repetir `analysis/s60/sol-audit/task.md` al renovarse el cupo. S51 se mantiene.

## S61 — origen de parámetros IMX210 y flujo de mensajes (20-10-2026)
- Hecho: corrección TBH de S60-Sol; puertas y cadena de los productores A/B del bloque `obj+0xe20` (`analysis/s61/{e3_chain,e4_producer_a,cfg_refs,g_writers,xr,rea}.py`); tabla del 6.º par = BK4 `0x300AB`; productor de la petición 9 (`HS_Main`) y publicador (`VD_Pre`). Informes `docs/capture/s61-*.md`, matriz `analysis/s61-evidence-matrix.json` (16 entradas, H61-1…4), tests `tests/test_s61_imx210.py` 22/22 + regresión S56–S60.
- Herramientas: REA (1 sesión, `GHIDRA_MAXMEM=6G`, cerrada), Capstone, Unicorn; sin dependencias nuevas; ruff limpio en lo nuevo.
- Correcciones: base TBH de Sol; `obj+0x168/0x16A` de S60 = global G; «campos de otro objeto» de B = `obj+0x2cc`.
- Frontera: escritores de `obj+0x2be..`, `G+0x168`, `G[0xD]`, `stage+0x3a`; petición 3; bit 31 del handle; unidad de los pares; ningún estado ALCANZABLE.
- Próximo exacto: leer `HS_Main`/`VD_Pre` (fin de exposición), sembrar Thumb, `trace_native_values` sobre P0. S51 se mantiene.

## S62 — PMCA: updatershell, service shell y `modelName` (20-10-2026)
- Hecho: lectura de `references/pmca` (v0.17) y `references/fwtool`: mecanismo de inyección de código (fdat propio, cramfs `/bodylib/libupdaterbody.so`, header 0x30 B por modelo, guard CRC + modelo/región/versión sin firma, shell USB `0x23` con SHEL/PULL/PUSH/RMEM/BK*) y service shell (senser, HASP, adjust-control `0x603`, terminal `0x601/0x1f`, ficheros/memoria). Verificación del fdat A6000 3.21: `model = 0x41030035`, versión 3.21, `firmwareOffset = 0x23200`; preset BK4 con `0x003e0005` = `ILCE-6000` (16 B, attr `0x01`). Documento `docs/capture/s62-pmca-injection.md`, matriz `analysis/s62-evidence-matrix.json` (11 entradas), test `tests/test_s62_backup_modelname.py` 5/5.
- Procedimiento reportado: `bk w 0x003e0005` a `ILCE-6001` y reversión con `-m ILCE-6000` (coherente con la selección de fdat por nombre reportado).
- Frontera: el efecto «shell mode» no está verificado; `ILCE-6001` no existe en el firmware; falta leer los consumidores de `Backup_read(0x3e0005)`.
- Próximo exacto: REA sobre lectores de backup de `modelName` o traza pasiva autorizada; S51 se mantiene.

## S66 — montura de lente E-mount en A6000 (línea general, 20-10-2026)
- Hecho: línea de RE **general** (independiente de SilentShutter) sobre el subsistema de montura del `av-cam.bin`: 646 logs en `0x43c95659`–`0x43c9a900`, código `0x436dfe6c`–`0x436e9ea4`, ficheros internos `Mount_Controller.cpp`/`Mount_DividedInfo.cpp`; **trama del bus UART cuerpo↔lente** (`0xF0` | len LE | commtype | ID de comando | datos | checksum u16 LE | `0x55`) con IDs `0x07/0x0A/0x15/0x16/0x2B`; tipo de lente por 2 bits (4.8 V / no registrada / desconocido `0xFF`); ciclo de vida de 63 logs; FW de la lente por CAIF/C3P (`0x436fe070`) y bus BonoboDSP al DSP (`0x43708cc4`, MMIO `0xf292d000`); formato de los 18 `VX91xx_lensfile.bin` (cabecera `LF`, secciones `ED`/`CS`/`LC`, parser `0x43907c7c`); sombreado por lente con tabla `tbb` 69→14 ShdMode. Informe `docs/capture/s66-lens-mount.md` + 6 sub-informes en `analysis/s66/`, test `tests/test_s66_lens_mount.py` 31/31, suite completa 323 passed + 39 subtests.
- Herramientas: REA 6.5.0 + Ghidra 12.1.4 (sesión demonio, `GHIDRA_MAXMEM=2G`), Capstone sobre bytes; 3 subagentes en paralelo (deepseek-v4.1-flash, glm-5.3-flash, mimo-v2.6-flash) más trabajo propio.
- Entorno (20-10-2026): máquina nueva preparada (`~/.venvs/re`, capstone/unicorn/keystone/lief, npm 12.2.1, codex-cli 0.162.1, `gh` autenticado); **límite Ghidra a 2 GB** en opencode/codex/Claude Code + demonio (`REA_DAEMON_RSS_MAX_MB` 2600) por OOM con varias instancias; rutas de caché portables (`/tmp/claude-1000` → `tempfile`); `.gitignore` para caches de barrido y logs del demonio.
- Correcciones: `u32@4` de los ficheros de lente = `filesize−0x10` (no tamaño total) y `u32@8` no constante; la tabla de nombres está en `0x43C22BF2` (2 B antes del primer nombre); la longitud de la trama es **little-endian** (byte bajo en `+1`).
- Frontera: pines GPIO de CS/DATA y de la alimentación 4.8 V (memoria reubicada fuera del blob); unidades de `UART_HZ 750/1500`; nombre de cada ID de comando (tabla de descriptores en runtime); servicio userland que abre los ficheros de lente; semántica de ED/CS/LC.
- Próximo exacto: (a) pines del bus de lente vía backup BK4 o esquema del manual de servicio; (b) `libInfraMediaMount.so`/`libInfraLensCommunicator.so`: qué servicio sirve `/lens/VX91xx_lensfile.bin`; (c) abrir línea nueva: AF (`analysis/s63_af/`), codificación de imagen (`analysis/s64_jpeg/`) y vídeo (`analysis/s65_video/`). S51 se mantiene (fin electrónico NO VERIFICADO).

## S69 — subsistema de audio de la A6000 (línea general, 21-10-2026)
- Hecho: RE general del bloque de audio del `av-cam.bin`: arranque `AUDIOIP INIT COMP` (`0x43c26411`, IP del driver de sensor con configs VGS/PR/MF/CONS/BANDI), micrófono (`0x43c26dc1`, `0x43cddad4`, `0x43cddd49`), niveles (`0x43c26df4`, `0x43c26e91`, `0x43cdddf3`, `0x43929fa4`), WNR/cancelación de voz (`0x43cddea7`–`0x43cddf9a`), códecs (`0x43c6909d`/`0x43c690c8`/`0x43c690f1`), diagnóstico (`0x43c5c68e`/`0x43c5c6b1`/`0x43c5ca62`), enlace con vídeo (`0x43c28d29`, `AVBB_SCN_START/STOP_AUDIO`), backup (`0x43cdd82e`, `0x43cddfbc`). Informe `docs/capture/s69-audio-subsystem.md` + `analysis/s69_audio/{audio_subsystem.md,json}`, test `tests/test_s69_audio.py` 9/9.
- Hallazgo diferencial: la A7S (fw3.20) tiene **códec externo** (`15AbbExtCodecCtrl` `0x43cd582e`, `ConvChSsau2AudioIpCh` `0x43c2f48a`) que la A6000 (fw3.21) **no tiene**; el resto del audio es equivalente (235 vs 237 cadenas).
- Herramientas: subagente (`beam-free`) con Capstone sobre bytes; sin REA nuevo (RAM: 4 sesiones Ghidra ya abiertas).
- Frontera: muestreo/bits/canales reales; "reduce voltage" del micrófono; muxer de audio en el contenedor; coeficientes WNR; ganancia/calibración; semántica de VGS/PR/MF/CONS/BANDI.
- Próximo exacto: muestreo/canales desde la configuración de `AUDIOIP`; contenedor de vídeo y audio (AVCHD/MP4) y su muxer; `libInfra*.so` de userland para el códec externo que solo tiene la A7S. S51 se mantiene.

## S70 (reconocimiento) — EIS/gyro (21-10-2026, línea abierta)
- Hecho: mapa del subsistema de estabilización del `av-cam.bin`: tres capas con prefijo propio (`[CAMERA_IS][AS]` 0x436fecbe–0x436ffab4 con cola OSAL y factor `upm_get_hcrn_ura`; `[CAMERA_IS][EIS]` 0x43702dac–0x437046a4 con `rcct_SetStblzPower`, `rcct_SetStblzGridH` y lecturas `GyroAD[p],GyroAD[y]`; `[CAMERA_IS][DIST]` 0x436ea470–0x436ea65c), puente con la montura (`IS_LensMountExpStartCB` 0x436ea2d0, `IS_LensMountPanoramaGyro` 0x43705dd0), cadena de time control (`GyroStitScl` 0x437d0768, `JudgeBrkGyro` 0x43874c50) y **fichero de calibración IS por lente `/mnt/FILE_IS_%04x.dat`** (0x43707152). Nota `analysis/s70_is/is_gyro_recon.md`, test `tests/test_s70_is.py` 4/4.
- Verificado: direcciones y textos de los logs anteriores (bytes). Inferencia: "AS" ≠ "EIS"; el EIS se coordina con el disparo y con el barrido panorámico.
- Abierto: formato de `FILE_IS_%04x.dat` y quién lo escribe; unidades de `GyroStitScl`; rail `EIS_RC1V`; relación con el OSS del objetivo y con `LensShdOn`/`PzShdOn` (S66).
- Próximo exacto: parsear `/mnt/FILE_IS_*.dat` (si existe en el firmware) y localizar al escritor; trazar `GyroAD` → `GyroStitScl`. S51 se mantiene.

## Plan de trabajo continuo (21-10-2026, instrucción del usuario)
- Regla: **oleadas de 2 subagentes** en líneas de ingeniería inversa **general** de la cámara (no SilentShutter), integrando cada ola antes de lanzar la siguiente (verificar bytes → `docs/capture/sNN-*.md` → README + `knowledge/CURRENT.md` + PROGRESS → `knowledge-maintenance` → tests → commit **por rutas** → push). Continuar hasta agotar el límite de uso del modelo.
- Restricciones operativas heredadas: sin abrir sesiones Ghidra nuevas (RAM: 4 sesiones ya abiertas, `GHIDRA_MAXMEM=2G`); solo Capstone sobre bytes; los subagentes **no** escriben en `docs/` ni `knowledge/`; stagear por ruta (nunca `git add -A`) porque hay pushes paralelos de otros agentes.
- Estado: S67 (AF, `deepseek-v4.1-flash-free`) y S68 (batería/energía, `nemotron-3.5-super-vl-free`) en marcha; S69 (audio) y S70-recon (EIS/gyro) ya integrados.
- Candidatos para las siguientes olas (elegir por oleada, sin solapar): FRC/detección de caras (`[FACE]`/`FC/*`, `fc_alg_*`), multi-frame/HDR/bracketing (`ZAG`, `DRO`, `Marge`), picture profiles/creative style/balance de blancos, Wi-Fi/PlayMem remoto (`libWlan*`), MTP/USB y transferencia, DCF/reproducción y gestión de medios, panorama, GPS, reloj/RTC, tarjeta SD/filesystem, codificación de vídeo (AVCHD/MP4) y su muxer, IBIS/EIS (continuar S70), ZPD/detección de placa de zona, calibración de sensor (SA), enfoque de peso/fase.

## Mapa de temas en vuelo (21-10-2026) — regla anti-colisión antes de lanzar cada ola
- **Otros agentes (no duplicar ni tocar sus ficheros)**: (a) *service mode / RAM / periféricos / volcados de cámara / NVRAM / firmware propio* → `analysis/camera-dumps/`, `scripts/*service*`, `docs/capture/s62-pmca-injection.md`, `s64-silent-ram-nvram-test.md`, `s65-nvram-incident-diff.md`, `custom-fw-recovery-and-install.md`, `liveview-silent-capture-via-cameraex.md`; (b) *línea SilentShutter / VD / IMX210 / Darwin cortinas* → `docs/capture/rea-tema1-vd-integracion.md`, `rea-tema2-imx210-parametros.md`, `rea-tema3-cortinas-darwin.md`, `docs/agent/*`; (c) *AF (S63), JPEG/codificación (S64), vídeo (S65)* → `analysis/s63_af/`, `analysis/s64_jpeg/`, `analysis/s65_video/`; (d) han parcheado `analysis/rea-independent/bin/session_daemon_patched.py` (no tocar).
- **Mío (este agente)**: S66 montura de lente ✅, S69 audio ✅, S70 recon EIS/gyro ✅, S67 AF (en marcha; **tema solapado con su S63**: se integrará como validación cruzada, no como doc duplicado), S68 batería/energía (en marcha).
- **Libres (verificados contra `docs/` y `analysis/`, 0 documentos y sin directorio de otro agente)**: FRC/detección de caras (`FC/*`, `fc_alg_*`, `[FACE]`, `[TRK]`), Wlan/PlayMem/CameraOnDemand (`libWlan*`, `libInfraDlnaControl`, `libGOConnectionManager`), picture profile/CreativeStyle/balance de blancos, ZIT/defect correction, ZPD, exFAT/almacenamiento.
- **Procedimiento antes de cada ola**: (1) `grep -ril "<tema>" docs/` → 0 o solo menciones superficiales; (2) `ls analysis/ | grep <tema>` → sin dir activo de otro agente; (3) `find . -newermt "-60 minutes"` para ver ficheros que otros agentes están tocando ahora; (4) elegir el número de hito libre en `origin/main` (`git ls-tree origin/main docs/capture/`) y renombrar si colisiona.

## S68 — gestión de batería, energía y carga (NP-FW50) (21-10-2026, línea general)
- Hecho: RE general del subsistema de batería/energía del `av-cam.bin`. **Resultado negativo verificado**: no hay modelo del pack NP-FW50 (0 hits `NP-FW`/`NPFW`/`FW50`); sí nivel de batería vía UPM (`0x43ca2dfd`, fn `0x4378f364`), códigos de estado a MCU (`ACV_BATT_Snd` `0x43c8f95e`, `BATT_AUTH_Snd` `0x43c8f96b`, `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`, `Box_Temperature_Snd` `0x43c8f9fc`, `ACV Error Voltage` `0x43c8f83b`), **carga de flash** (`SB_CHARGE` `0x43cb4c23`, `uc_Charge*`), power save del imager y coordinación lente↔voltaje (`Wait E-MountLens ReduceVoltage` `0x43cc7aa4`, `CaptureCancel_PowerOffDetect` `0x43ca9d85`). Informe `docs/capture/s68-battery-power.md` + `analysis/s68_power/{battery_power.md,json}`, test `tests/test_s68_battery.py` 7/7.
- Corrección de revisión: (a) la cadena ReduceVoltage está en `0x43cc7aa4`, no `0x43cc2ca6`; (b) la A7S **sí** tiene `ACV Error Voltage` (`0x43c982d3`) y `ACV_BATT_Snd` (`0x43c983f6`): el informe inicial del subagente era incorrecto en ambos puntos.
- Comparativa: la A7S conserva el bloque de estado y la carga de flash, pero no `BatteryInfo` ni los `Battery Info` de IRLight/VideoLight.
- Frontera: modelo del pack fuera de `av-cam.bin`; destino de `BATT_*_Snd`; carga por USB/base sin modelo en el firmware; perfiles de consumo y apagado automático no localizados.
- Próximo exacto: el modelo del pack NP-FW50 está en userland o en el MCU (buscar `BatteryInfo` en `libInfra*.so` y en el firmware del MCU); el bloque de "carga" es del flash, no de la batería. S51 se mantiene.
- S67 (AF) **cancelado**: el subagente agotó el cupo de uso y, además, el tema AF lo cubre otro agente (`analysis/s63_af`); artefactos parciales eliminados para no duplicar ni colisionar.

## S73 (reconocimiento) — protocolo de ajuste `ADJ_CMD` (21-10-2026, línea general)
- Hecho: mapa del protocolo de comandos de ajuste de fábrica del `av-cam.bin`: **38** comandos `ADJ_CMD_AVBB_PANELEVF_*` (`0x43c76c93`–`0x43c774b2`, todos referenciados por el manejador `0x4363524c`) para **panel/EVF/OLED** (VCOM, WB por sub-bloques R/G/B — `WB_SubB_{R,G,B}_Adrs=%02X` `0x43c76e31`/`0x43c76e87`/`0x43c76ddb`—, CALDAC, termistores OLED/EVF con secuencia INIT/START/CNFM/INFO/END, test de fábrica, detección de panel y de tipo de EVF); **4** comandos `ADJ_CMD_LIRO_DRIVERS_ADC_*` (`0x43ce4ff2`–`0x43ce507e`, manejador `0x4398e578`); y `ContrastPlus_Base` (`0x43cc7bc4`, ref `0x438c2dc4`) como función de procesado en el camino de captura. Estructura del manejador: ID u16 en `[r6+0x18]` (compara con `0x302`), sub-comando u8 en `[r6+0x1a]` (rango 0..0x28), 4 búferes de 8 B. Nota `analysis/s73_adj/adjust_cmd_recon.md`, test `tests/test_s73_adj.py` 7/7.
- Verificado: recuentos y direcciones de las 45 cadenas, y las instrucciones del manejador.
- Abierto: **ID numérico de cada comando** (los nombres se cargan con literales PIC uno a uno, no hay tabla de punteros → el mapa ID↔nombre está en el flujo de control); semántica de `TEST_*`; registro de destino de los sub-bloques WB; qué es `ContrastPlus_Base`; destino de los comandos ADC de LIRO; comparación con A7S.
- Próximo exacto: recorrer el flujo del manejador `0x4363524c` y emparejar cada `cmp` de ID con el literal de nombre que carga la rama siguiente (mapa ID↔nombre de los 38 comandos); después el destino de `WB_SubB_*`. S51 se mantiene.
- Nota de cuota: las olas de subagentes S67/S68/S71/S72 chocaron con "Rate limit exceeded" del proveedor; S68 se integró con revisión manual, S67 (AF) se canceló por colisión de tema con `analysis/s63_af` de otro agente, y S71/S72 quedan pendientes de reintento.

## S74 (reconocimiento) — despacho del protocolo ADJ_CMD por máscara (21-10-2026)
- Hecho: estructura del manejador `ADJ_CMD` de panel/EVF (`0x4363524c`): **un solo ID de comando** (u16 `0x302` en `[r6+0x18]`) y **8 sub-comandos** (u8 en `[r6+0x1a]`, 1..8) que se traducen a una **máscara acumulativa** mediante `tbb` (`0x436354fc`, tabla de 8 bytes `04 06 08 0a 0c 0e 10 12` en `0x43635500`): `0x01,0x03,0x07,0x0F,0x1F,0x3F,0x7F,0xFF` (stubs en `0x43635508`+4k, `subs r2,#1` @ `0x436354f6`, `cmp r2,#7` @ `0x436354f8`). Los 38 nombres `ADJ_CMD_AVBB_PANELEVF_*` son **etiquetas de elementos de ajuste**, no comandos: el código recorre los elementos y registra los habilitados por la máscara; un segundo `tbb` (`0x436357b2`) despacha los canales R/G/B del WB de display (`WB_SubB_{R,G,B}_Adrs`). Scripts: `analysis/s73_adj/{adj_cmd_map.py,adj_subcmd_map.py}`; nota ampliada en `analysis/s73_adj/adjust_cmd_recon.md` §1.4; test `tests/test_s73_adj.py` 10/10.
- Inferencia: el ajuste de panel/EVF es **por bits** y el sub-comando *n* habilita los *n* primeros elementos (VCOM, WB, CALDAC, VO, termistor, test…).
- Abierto: **emparejamiento elemento→bit** (no sale de Capstone con fiabilidad; requiere decompilación REA de `0x4363524c`, sin sesión libre: RAM con 6 Ghidra abiertos); destino de `WB_SubB_*`; `ContrastPlus_Base`; comparación con A7S.
- Próximo exacto: decompilar `0x4363524c` con REA cuando haya sesión libre y extraer el mapa elemento→bit→máscara; después los 4 comandos `ADJ_CMD_LIRO_DRIVERS_ADC_*` (`0x4398e578`). S51 se mantiene.

## S75 — ZPD (Zone Plate Detection): calibración del sensor con datos de la lente (21-10-2026, línea general)
- Hecho: mapa del subsistema ZPD del `av-cam.bin`: namespace `Camera::ZPD` con 14 clases (`MemObj`, `MemUnit`, `MemUnitBackup`, `MemFileLoadObj`, `Control::Detect`, `Control::WorkerBase`, `Control::SequencerBase`→`Sync`/`Async`/`Sequencer`, `ITrace` y **`ZPD::Lens::LensInterpretChunk`/`…ChunkEd`**, nombres en `0x43ccf318`–`0x43ccf420` y `0x43cd1b51`–`0x43cd1c3b`); **tres orígenes de datos**: `[ZPD]: load lens data from lens.` (`0x43ccf2c7`), `[ZPD]: load lens data from body.` (`0x43ccf2e8`) y `[ZPD]: load dra data.` (`0x43ccf2a0`), más `[ZPD]: lens attach sequence end.` (`0x43ccf27f`); consumo en el DFE: factores de interrupción por canal `SetZPD0/1IntFactor` / `ClearZPD0/1IntFactor` (`0x43c91781`–`0x43c91925`), carga de posiciones de defecto en la **SRAM del sensor** (`ImgDdcSetter::loadDefectPos ZPD_SRAM shortage` `0x43cf75ee`) y trazas APB/AIF (`CPU IRQ : ZPD0/ZPD1`, `CPU APB : ZPD_APB0/1 …(Min/Max addr)`, `CPU AIF : ZPD W-ch0/R-ch1/W-ch2/R-ch2`); coordinación con el **bus de la lente** (`[BL]ZPD change EclipseDataComState from STANDBY to START` `0x43c976b5`; y el volcado del protocolo de montura incluye el campo **`LC T.O. Cnt`** `0x43c96c1e` → el canal LC (calibración de lente) vive dentro de MOUNT) y con el **AF híbrido** (`NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable` `0x43c9d07e`, `zpd_mario_afa.cpp` `0x43c9db6a`, `LC_GetZpdResultInfo:Error` `0x43ca78b6`, `area[60].zpd_flags/defocus` `0x43ca777c`). Nota `analysis/s75_zpd/zpd_subsystem.md`, test `tests/test_s75_zpd.py` 7/7.
- **Diferencial A7S (fw3.20)**: sin namespace `Camera::ZPD` (0 hits de `N6Camera3ZPD`) ni logs `[ZPD]:`, pero **con** los factores de interrupción ZPD en el DFE (`0x43c9a689`/`0x43c9a7b2`): la fw3.21 añade la capa de aplicación que carga el chunk de calibración desde la lente.
- Abierto: formato del chunk de lente (`LensInterpretChunk`/`ChunkEd`) y si es el mismo tipo de bloque que `/lens/VX91xx_lensfile.bin`; qué es "dra data"; cómo se calculan las posiciones de defecto; relación ZPD0/ZPD1 con los subcanales W/R ch0..ch2.
- Próximo exacto: emparejar `LensInterpretChunk` con el formato de los ficheros de lente (S66) y localizar el escritor de los datos ZPD en el cuerpo (`load lens data from body` → qué fichero/backup). S51 se mantiene.
- Cuota de subagentes agotada en el proveedor (6 intentos con "Rate limit exceeded"); el trabajo continúa en el agente principal.

## Revisión de S68 y cierre de huecos (21-10-2026)
- El test canónico del hito es `tests/test_s68_power.py` (19/19); el duplicado `tests/test_s68_battery.py` se eliminó (el subagente ya había generado el suyo antes de agotarse el cupo).
- Correcciones aplicadas al test/informe del subagente: (a) la cadena `Wait E-MountLens ReduceVoltage` está en `0x43cc7aa4` (no `0x43cc2ca6`, que apuntaba a otra cadena de SHD); (b) la **A7S sí tiene** `ACV_BATT_Snd` (`0x43c983f6`) y `ACV Error Voltage` (`0x43c982d3`) — lo que la A6000 añade es `BatteryInfo` y los `Battery Info` de IRLight/VideoLight; (c) en la A7S la cadena de nivel de batería va **sin** el prefijo `[CAMERA_MAIN_SYNC]: `; (d) el bloque de nombres de carga empieza con un `#` en `0x43ccd8aa`; (e) rango de búsqueda de las cadenas ACV (0x43c8f83b/0x43c8f95e) por debajo de 0x43c90000.
- **Hallazgo adicional (S68)**: la carga de flash está controlada por **PWM** con realimentación del condensador: `uc_AcvOn` `0x43ccd8ff`, `uc_UnregVolltage` `0x43ccd908`, `uc_CapacitorStatus` `0x43ccd919`, `uc_PwmStatus` `0x43ccd92c`, `us_ActivePwmDutySlope` `0x43ccd949`, `us_ActiveChargeSlope` `0x43ccda10`, `uc_ChargeRequest` `0x43ccda49`, `uc_ChargeStopRequest` `0x43ccda5a`.
- **Hallazgo adicional (S75)**: el origen "from body" de los datos ZPD es el fichero **`/setting/psd.bin`** (cadena contigua a los logs `[ZPD]:`).
- Suite completa: **383 passed + 49 subtests**.

## S76 — etapas del procesado de captura (`Stage_*`) y funciones SA (21-10-2026, línea general)
- Hecho: inventario de la **cadena de desarrollo de imagen** de la A6000 según los nombres de clase/fichero fuente embebidos: **73** entradas `Stage_*` (`0x43c9ee6c`–`0x43cca4d9`): SACC/Common/DevLater/DualRec/Notify/WaitControl, Panorama(+CcnrEncode), ramas de disparo (SweepAndSpool, DummyPreReview, MkOpen, FaceDetectPreReview), Raw/ResizeHV + `Rch*`/`Rcv_Dist*`, Adjust, Apollo, AutoFraming, BDRO, BFNR, BOKS(+BoksPre/Post), CaComm, CameraHAPI, Decomp(+4SA_ForDualRec, LoadDeconvPsfTbl, ExpandDeconvParam), Develop, SCNEnc/THMEnc/THMCopy/SCNEncWithTHM, FaceDetect, KKNR, MARBLE, OPD(+DevOPDAfterCap), Orientation, SPICA(+ExpandSpicaParam), STAR, SoftFocus, SetDateImageParam/StillDate, TBOX, YKNR. **26** funciones `sa_func_*` distintas, con correspondencia nominal etapa↔SA (BOKS, DECOMP, SPICA, STAR, YKNR, LFNR, DUALREC_BAYER/CLEARVID, BDEX). El orden de las cadenas sigue el **orden del pipeline** (INFERENCIA). extras: `Stage_SPICA` carga `/usr/sabin/spica_*_tap_step*.bin`; `Stage_Adjust` contiene `ContrastPlus_Base` (S73). Nota `analysis/s76_stages/stage_pipeline.md`, test `tests/test_s76_stages.py` 5/5.
- Abierto: grafo real de dependencias entre etapas; SA de las etapas con nombre distinto (PreDCV, CasNr, ZIT, CONTP, sftfcs); contenido de los `spica_*_tap_step*.bin` y `star_kernel_param.bin`; salida del pipeline (SCNEnc vs THMEnc).
- Próximo exacto: grafo de etapas con REA (requiere sesión libre; RAM con varias Ghidra abiertas) y emparejar cada etapa con su función SA y sus ficheros de parámetros.

## S78 — parámetros `apc_*` del motor de imagen YC (21-10-2026, línea general)
- Hecho: inventario del espacio de nombres de parámetros de imagen que calcula el motor `Camera::YC` (logs `[CAMERA_MAIN_YC]: YAP:`): **50 parámetros** en **7 módulos** entre `0x43cc44cb` y `0x43cc4fe4` — `apc_lpf` (2: vaplpf/haplpf), `apc_mask` (6: v/hmaskgain, v/hmaskoffset, hmasksel_l/h), `apc_yld` (9: yld_vlpf/hlpf/base_gain/slope_l-h/sofst_l-h/ofst_l-h), `apc_acm` (4: acmpm_th_en/acmpm_th/acmpm/acmpp), `apc_zoukou` (18: size_adj, dist_ofst_start/end, pgainy, cgain_{v,h}{h,m,l,s}, egain_slope_{v,h}{h,m,l,s}), `apc_coring` (8: {v,h}coring_p0/p1/p2/aplk), `apc_gain` (3: apgain/vapgain/hapgain). El **nombre del parámetro va embebido en la cadena de formato** del log (no hay tabla de nombres). Job por módulo (por el prefijo `YAP:` referenciado): `0x438b0f80` (lpf), `0x438b1058` (mask), `0x438b11f0` (yld), `0x438b177c` (acm), `0x438b2070` (zoukou), `0x438b2ac4` (coring; firma `void Camera::YC::job_apc_coring_stl(...)` `0x43cc513d`), `0x438b3570` (gain; firma `void Camera::YC::job_apc_gain_stl(...)` `0x43cc40df`), `0x438b3ea8` (`job_apc_main_stl`), `0x438b5810` (`job_apc_main_mov`). Contexto: `bdro_sequence error` `0x43cc4d37`, `aus_X_ISO` `0x43cc4d68`, `picture_effect` `0x43cc4d8c`, `AgcContStdBase`/`AgcContBlend` `0x43cc4428`/`0x43cc446e`. Nota `analysis/s78_apc/yc_apc_params.md`, test `tests/test_s78_apc.py` 6/6.
- Abierto: significado de `acmpm` vs `acmpp`; dónde se materializan los parámetros (probable `Camera::YC::T_AdjRam`, vista en `sjob_GetDetectArea` `0x438ea230`); tabla de valores por modo de captura; comparación con A7S.
- Próximo exacto: emparejar cada parámetro `apc_*` con su celda en `T_AdjRam` y con la función `sa_func_*` que lo consume. S51 se mantiene.
- Cuota de subagentes: los 8 modelos `free` disponibles (deepseek-v4.1-flash, nemotron-3.5-super-vl, nemotron-3.5-lightning, beam, mimo-v2.6, longcat-2.5-preview, glm-5.3-flash, big-pickle) devuelven "Rate limit exceeded"; se relanza por tandas de 3 mientras se trabaja en paralelo en el agente principal.

## S79 — mapa de módulos del firmware por prefijos de log (21-10-2026, línea general)
- Hecho: tabla de módulos del `av-cam.bin` deducida de los prefijos `[MÓDULO]` de sus cadenas: **348 prefijos** en A6000 fw3.21 y **277** en A7S fw3.20. Descomposición de `CAMERA_MAIN` en **8 submódulos** (nº de trazas + rango): `CAMERA_MAIN_YC` 970 (motor de imagen: `api_YC_*`, `job_YC_*`), `CAMERA_MAIN_SYNC` 429 (`SyncResMgr::Lock/Unlock/Free`, `CAMDEV(0|1)`), `CAMERA_MAIN` 135, `CAMERA_MAIN_TC` 127 (giro: `GyroStitScl`, `LmtGyroVect`, `calib_r_ave`), `CAMERA_MAIN_LC` 72 (calibración de lente: `lc_Movie_DM_AF_Util_getMiniRawAddr|getResizedYAddr|getBufferAddr|getSaIfAddr`), `CAMERA_MAIN_CC` 49 (`ExtractCaptureData()`, `CaptureInit()`, `SetReadImageParam()`, `SetNRParam()` con `CapMode/ExposureID/ContID/BDROSeq`), `CAMERA_MAIN_IM` 42 (`movie thermal diffTemp`, `environmentalTemp`), `CAMERA_MAIN_FC` 9 (`Eye data is invalid, but lc flag is true`). Familias mayores: `ADF` 1231, `IMAGING_CAP` 697, `SDF` 477, `CAM_IMAGER` 371, `IDT` 298, `IDT_OPD` 274, `CDIAG` 270, `VDF` 243, `CAMERA_SA` 231, `TRK` 216, `VEF` 149, `MOUNT_DEBUG` 132, `MOUNT_ERROR` 80, `SFRS` 117, `SFRA` 100, `VPH_API` 106, `ACCY` 106, `DBGCMD` 102, `STK` 76, `FACE` 70, `VIDENCSTAT` 70, `CLK_CTRL` 66, `GOLFSHOT` 65, `WSX` 59, `CTRLCORE` 55, `CAM_DMM` 54, `SAD` 45, `CAM_FUNC_MGR` 43, `APL` 42, `PNL` 41. Diferencial: 83 prefijos exclusivos de A6000 y 12 exclusivos de A7S (`APL_PARM`, `APL_ESR`, `NLAP`, `PINCOUNT`…). Nota `analysis/s79_modules/module_map.md` + `module_map.json` (tabla completa de los dos modelos), test `tests/test_s79_modules.py` 5/5.
- Abierto: significado de las siglas `ADF`, `IDT`, `VDF`, `VEF`, `SFRS`/`SFRA`, `WSX`, `GOLFSHOT`, `ACCY`, `AUGI`, `SAD`, `APL`; correspondencia prefijo↔tarea del OSAL; renombrados entre fw3.20 y fw3.21.
- Próximo exacto: usar la tabla para fechar cada bloque de código por módulo (p. ej. `CAMERA_MAIN_LC` ↔ S75) y abrir los prefijos "exclusivos de A6000" restantes. S51 se mantiene.

## S80 — ZIT: corrección de defectos del sensor (DDC) (21-10-2026, línea general)
- Hecho: mapa del motor de corrección de defectos del imager: 118 trazas `ZIT`/`Zit` en A6000 fw3.21 (75 en A7S fw3.20); clases `N6Camera6Imager12ZitMemBufferE` `0x43cf768e`, `N6Camera6Imager18ZitZphDefectBufferE` `0x43cf81a1`, `N6Camera6Imager21ZitZphLineTableBufferE` `0x43cf96ef`; cuatro áreas de memoria (`ZIT:: shadowAddr adj:%x usr:%x slow:%x mend:%x` `0x43cf7706`) y bancos por *read mode* (`<read:%d bank:%d>` `0x43cf7771`); puente al motor de imagen con `Camera::Imager::ZitSaFunctionDriver` (`ZIT_SaOpen`/`ZIT_SaStart`/`ZIT_SaClose` `0x43cfa2a7`–`0x43cfa2ee`, firma `ZIT_SaClose()` `0x43cfa312`, `dmmHandleList is Full` `0x43cf9cd3`, MMU propio `CloseFreeZitMMUParam` `0x43cfa210`); operaciones ejecutadas en el SA: `Merge` `0x43a13be8`, `ConvThin` `0x43a194c4`, `ConvUnity` `0x43a19908`, `ConvZ1C` `0x43a19c58`, `Det` `0x43a1a364` (`DetectInfo [ch1..ch4]`, `RAWInfo [AVE/MIN/MAX]`), `Hist` `0x43a1a834`, `ZphSA` `0x43a1aafc`, más `ZitSA_ConvDdc` `0x43a139c8`; trazas de registro de defectos `SetZitLog_DetectSequencePre/MassiveDefectDetectNum/DefectLvAndPos/DefectPosNum` `0x43cf7e5f`–`0x43cf7f2e`; búferes `Zph*` (`ZphAdj_Merge_Req` `0x43cf9717`, `ZphAdj_Det_Req` `0x43cf97f4`, `ZphDetSA` `0x43cf97c2`); variantes long exposure (`buildLongExpCapData_DDC`) y vídeo (`MovieAdj_SpreadDefectsOverSharedPixels`); drivers `ZitDdcDriver` `0x4386bbee` y `ZitZ1cDriver` `0x437b93c0` en `CAMERA_MAIN_IM`. Nota `analysis/s80_zit/zit_defect_correction.md`, test `tests/test_s80_zit.py` 9/9.
- Abierto: significado de las siglas ZIT/Zph; qué es un *read mode* y cuántos hay; formato y origen de fábrica de los datos de defecto; enlace exacto con ZPD (S75); algoritmos del SA de las conversiones.
- Próximo exacto: emparejar `ZitZphDefectBuffer` con el bloque de posiciones de defecto que S75 localiza en la SRAM del sensor (`ImgDdcSetter::loadDefectPos ZPD_SRAM shortage`) y con `read mode` ↔ modo de lectura del sensor. S51 se mantiene.

## S71 — subsistema de detección de caras y objetos (FC/FRC) (21-10-2026, línea general)
- Hecho: integración del hito de caras (subagente `nemotron-3.5-lightning-free`) **con revisión completa contra bytes**. Contenido verificado: **99 ficheros `FC/…`** (Alg/Seq/Drv/SaFuncDrv/Feature/Api/Lib/Misc) **idénticos en A6000 fw3.21 y A7S fw3.20**; puente con el **acelerador Scalar**: `AcquireRes … Core2 user[0]` `0x43cf094a`, `Core3 user[1]` `0x43cf0981`, `release res error: RES_SA_FOR_FRC2 = 0` `0x43cf09b8`, `s_sa_temp_icon_mem.Alloc` `0x43cf0bd8`, `s_sa_param_mem.Alloc` `0x43cf0bc3`, `MakeMmu - SA_MMU_NUM_MEM_ERR` `0x43cf0c11`, `MakeMmu - MakeExtentError` `0x43cf0cf9`, `ddl_saCalcCancel` `0x43cf0afb`, `alloc size:%d, expected:%d` `0x43cf0b39`, `SA result: NULL` `0x43cf0b54`, `FRC: Init FaceIcon` `0x43cf0d6c`, `FaceIconInfo::Alloc() handle:%d` `0x43cf0db8`; módulo `[FACE]` (INIT/BASE/MON/IMME/ATTR/STOP) y `[TRK]` con DETSA (Core2), EDTSA (Core3: `face : [%d,%d,%d,%d]`, `angle`, `node`, `hue_range`…), IRO2G, PMV (`Affine_err_thresh`, `Vector_thresh`, `Motion_frame_num`), STK (`Saliency CB`, `TouchSimilarity CB`, `ColorSimilarity CB`) y BT (`fg_area`, `bg_area`, `bayes_map_level`, `big_obj_size_thres`); algoritmo FRC (`FRC algo: recognized ID`, `swap ID`, `[record_rank:%d]`, `CREATE_ICON & PRIORITY_RECOGNIZED`); parpadeo (`fc_alg_blink.cpp`); Pre-FDT (`African`, `Scene`, `Bunri`, `Hist1`, `Light_backlight_*`); alternancia cara↔objeto (`Face -> ObjTracking`, `ObjTracking->FaceTracking`); MakerNote (`FC MakerNote address`). Informe `analysis/s71_frc/frc_subsystem.md` + JSON regenerado, test `tests/test_s71_frc.py` 20/20.
- **Correcciones aplicadas al borrador del subagente**: (a) direcciones en espacio de ficheros `0x8060839` → direcciones del binario `0x43cf0db8`; (b) búferes inexistentes `s_temp_icon_mem`/`s_param_mem` → `s_sa_temp_icon_mem`/`s_sa_param_mem`; (c) "SA (Secure Area)" → **SA = acelerador Scalar** (SFRA = *ScalarA-ScalarInfra*, `sa_dfdet.bin` = detección de caras en el Scalar, coherente con `FeatureScalarAOneshot` y `fc_scalara_detect_cb_handler.cpp`); (d) semántica inventada de BT/FAT/IRO/PMV/STK → sustituida por la evidencia de sus parámetros; (e) **diferencial A7S falso**: `fc_drv_iro2g.c` y `fc_feature_panorama_face_meta.cpp` existen también en la A7S (`0x43ce9972`, `0x43ce5963`).
- Abierto: siglas FDT/VAT/PRC/VAE/VOT; formato de los mensajes al Scalar; reparto Core2/Core3; algoritmos del SA para FRC; enlazar con `analysis/s63_af/` (otro agente) sin duplicar su trabajo.
- Siguiente línea libre: WLAN/PlayMem (S72) y Picture Profile/Creative Style (S77), pendientes por cuota de subagentes; en paralelo el agente principal trabaja S80 (ZIT) y S81 (ADF).

## S81 — ADF: framework de arranque, MSGQ, MMGR y comandos DBGCMD (21-10-2026, línea general)
- Hecho: mapa del **framework base** del firmware (el módulo más grande por trazas): 1220 cadenas `[ADF]` en A6000 fw3.21 (1269 en A7S fw3.20) en `0x43c26366`–`0x43c37a62`; sub-niveles raíz 934, `[DBGCMD]` 102, `[ERR]` 70, `[SYSND]` 27, `[ADJ]` 24, `[SAN]` 23, `[OUT]` 15, `[ADF]` 11, `[SYS]` 3, `[INIT]` 2, `[DEBUG]` 2, `[GS]` 2, `[AFNR]` 2, `[FACE]` 2, `[CH_SRC]` 1. Arranque: `BootInit` `0x43c26366`, `InitWaitVsync SelectCompo msgId %x` `0x43c26375`, `NoMSGQ %x` `0x43c2639e`, `[INIT]AVIO INIT COMP` `0x43c263f6`, `[INIT]AUDIOIP INIT COMP` `0x43c26411`, `BootExit` `0x43c263c9`; reenvío de mensajes `INIT Resend MsgqNum` `0x43c263d8`, `Resend header cateId/msgId/msgLength/version` `0x43c2642f`, `Resend to Adf src/reply/msgId` `0x43c2648f`, `Resend No Fifo Data` `0x43c264c1`. IP de audio (enlace S69): `AUDIO_IP_CONFIG_TYPE_VGS/PR/MF/BANDI_BASEDON_CONS/CONS/BANDI` `0x43c264fa`–`0x43c2659e`. MMGR: `MMGR COMM INFO` `0x43c265ce`, `indexNo, unitType, handle, allocNum, openNum` `0x43c265e3`, `Total Info Num %x` `0x43c26638`, `AdfMemMgrCtrl::SetMemMgrCommResult` `0x43c26652`, `FreeUnit Handle=0` `0x43c266bd`. MSGQ: `MSGQ Set:srcId %08X ,msgId %08X` `0x43c26788`, `MSGQ Get:msgId %08X` `0x43c267d5`, `SendImmediateComp` `0x43c268a8`, `ClearAllComp` `0x43c2691c`, `MSGQ_GID_HOTSHOE_INFRA1` `0x43c266e6`. DBGCMD (102, `0x43c2a443`–`0x43c2b315`): `System*`, `CPU2 ExecTime 60Hz/48Hz max|over m/s` `0x43c2a465`/`0x43c2a4ca`, `Input*`/`InputPro*`, `Output*`/`OutputPro*`, `Proc SetLinearPhase` + `LinearPhase{SetDec0/1,SetAip0/1,GetSa0/1,GetPin0/1,SetMb,SetSa,Nomatch0/1}Print` `0x43c2a795`–`0x43c2a930`, `SetPath`/`SetMixRatio`/`SetFader`/`SetZoomNr`/`ZOOM[0..2]`, `SystemSound*`, `SoundAnalyzer StartGolfShot` `0x43c2b143`/`StopGolfShot`/`AnalyzeGolfShot`/`SetSoundAnalyze`. Nota `analysis/s81_adf/adf_framework.md`, test `tests/test_s81_adf.py` 9/9.
- Abierto: significado de `ADF`/`MMGR`/`Compo`/`AIP`/`MB`; formato del mensaje y tabla de destinos; lista completa de `MSGQ_GID_*`; contenido de `ADF][ADJ]`, `[SAN]`, `[SYSND]`, `[GS]`, `[AFNR]`, `[FACE]`, `[CH_SRC]`; cómo se invocan los DBGCMD.
- Próximo exacto: seguir el arranque con la máquina de fases (`LinearPhase*`) para obtener la **secuencia real de inicialización**, y cruzar `SoundAnalyzer`/`GOLFSHOT` (65 trazas) con `sa_func_GOLFSHOT_start` (pista de golf por sonido). S51 se mantiene.

## S83 — los módulos "menores" del firmware, decodificados (21-10-2026, línea general)
- Hecho: decodificación por evidencia de los módulos de tamaño medio que S79 dejó sin descripción. `[ACCY]` (106 trazas) = **accesorios por UART** (`[ACCY][INFO][HW]:AD=%d, ID=%d` `0x43c24cac`, `NotifyAttachedUart(%08X)` `0x43c24cca`, `NotifyDetached` `0x43c24d1e`, `NotifyUartCommand[%c%c%c...]` `0x43c24d41`, `NotifyUartResponse` `0x43c24d94`) — mismo hardware que el grupo `MSGQ_GID_HOTSHOE_INFRA1` de ADF. `[CAM_FUNC_MGR]` (43) = **gestor de funciones de captura**: `SyncProcMargin[usec] HS0:%u HS1:%u HS2:%u HS3@CPU2:%u HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u` `0x43ca12f6`, `SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d]` `0x43caf036`, `receive[%d,%d] before comp[%d,%d] (QUEUEING)` `0x43caf077`. `[ENCOUCSTAT]` (49) = **errores del codificador AVC**: `AVC_ENC_VIDEO_ERR_STATE/MEMORY/PARAM/INDEX` `0x43c50693`–`0x43c50730`, `ES Overflow!!` `0x43c5066b`. `[VIDENCSTAT]` (70) = **estado del encoder de vídeo**: `[VIDEO INFO] Pts = 0x%08x EndFlug = 0x%02x` `0x43cd680b`, `augi,paddingAreaLength:%#x` `0x43cd6861`, `ExecuteEncPictureFailure` `0x43cd6888`, `Use 2nd Latest Index` `0x43cd68af`. `[ENCSEQCTRL]` (46) = **secuenciador de encoding**: `[O/U Crank] Table[%d] fR[0x%x] sR[0x%x]` `0x43c4bd2b`, `OuCrank Config Err: FrameRate/SamplingRate` `0x43c4bd5f`, `[state]0x%x -> 0x%x` `0x43c4bda2`, corrección forzada de estado `0x43c4bdc4`. `[SAD]` (45) = **programas del motor de imagen con cabecera**: `Same Unit Handle Get` `0x43ce546b`, `CdcSaPrg/NmlSaPrg/RsdSaPrg Hdr Err` `0x43ce55bc`/`0x43ce55db`/`0x43ce55fa`, `DbgPrt CmdRcv` `0x43ce564c`. `[PNL]` (41) = **panel/display**: `Backup_read() b_id %08X` `0x43c76155`, `cmd_set_conf_dev/rev/cb/id` `0x43c76185`–`0x43c761f3` (enlaza con ADJ_CMD, S73). `[AUGI]` (75 token / 26 con prefijo) = **formato de bloque con cabecera**: `length`/`Reserved2`/`end_flag`/`PS_flag`/`EP_flag` `0x43cd9968`–`0x43cd99f4`. `[WSX]` (59) = **búsqueda en fichero "BSFS"**: `BSFS INIT: TG: %x` `0x43ce41bd`, `BSFS CLOSE: MEMMAN FREE err` `0x43ce41d6`, `BSFS SEARCH LOOP ERROR` `0x43ce41fe`, `BsfsWSXClear Err` `0x43ce4250`. Nota `analysis/s83_modules/minor_modules.md`, test `tests/test_s83_modules.py` 10/10.
- Abierto: siglas BSFS/AUGI/SAD/WSX/ENCOUCSTAT; qué son los programas `Cdc/Nml/Rsd` del SA; los 4 sub-valores de `CapMode`; tabla "O/U Crank" completa; cabecera AUGI exacta; módulos aún sin decodificar (`IDT`, `VDF`, `VEF`, `CLK_CTRL`, `SFRS`/`SFRA`, `GOLFSHOT`, `SAN`, `GS`, `CH_SRC`, `AFNR`).
- Próximo exacto: decodificar `VDF` (243) y `VEF` (149) — el subsistema de display — y `CLK_CTRL` (66) con `SFRS`/`SFRA` (117/100). S51 se mantiene.

## S84 — el API del motor de imagen (SA): catálogo de `sa_func_*` (21-10-2026, línea general)
- Hecho: catálogo de la superficie del driver `Camera::SaFuncDrv` del motor de imagen: firma uniforme `Camera::SaFuncDrv::SA_FUNCDRV_ERR Camera::SaFuncDrv::sa_func_<X>_<op>(__uint8_t, __uint16_t, Camera::SaFuncDrv::<X>_START_PARAM*)` (unidad, código de función, parámetros) y **19 familias**: `BFNR` (`sa_func_BFNR_init(SaFuncDrvCmn*, BFNR_START_PARAM*, BFNR_PARAM*, __uint16_t)` `0x43cec98b`), `BOKS`, `CONTP` (`0x43ced65e`), `DECOMP` (`0x43ced8ac`), `DUALREC_BAYER`/`DUALREC_CLEARVID`, `GOLFSHOT` (dos sobrecargas: `SSP_START_PARAM*`+`SSP_START_MBX*` `0x43cedc91` y `BGEST_START_PARAM*`+`SA_MBX_0123*` `0x43cedff6`; release `0x43cedf67`), `KKNR` (`0x43cee1f4`, `0x43cee27b`), `LFNR`, `NFLASH` (flash: `flash_add`/`amb_add`/`int_add`/`rc_line_ofs`; firma `0x43cee4ca`), `PreDCV` (`0x43cee7ec`), `SFTFCS` (`preinit(__uint16_t)` `0x43ceeaa0`; mailbox `cha_mbx0/1/2` `0x43cc9df0`–`0x43cc9e58`; llamadas en minúsculas `sa_func_sftfcs_start error (%d)` `0x43cc93c2`), `SPICA` (fases PRE/MAPPING/POST), `STAR`, `TBOX` (`0x43ceeea8`), `YKNR`, `BDEX`; errores `SA_FUNCDRV_E_OSAL`/`_RSLTCODE`/`_ERRCODE`. Consumidores: `IMAGING_CAP` (697 trazas, p. ej. `sa_func_NFLASH_start error` `0x43c9ef73`, `sa_func_BFNR_acquire()` `0x43cc7390`, `sa_func_KKNR_acquire error` `0x43cc8e85`, `sa_func_YKNR_acquire error` `0x43cca388`) y el driver con prefijo `[CAMERA_SA]` (231 trazas). 92 cadenas con `sa_func_` en A6000 (109 en A7S).
- **Diferencial (VERIFICADO):** la fw3.21 de A6000 elimina por completo `NLAP` (0 ocurrencias de "NLAP"; la A7S tiene 13: `[YC][NLAP]isNLAP:true, iso_cont=0x%04x` `0x43cbbf71`, `[YC][NLAP]Param:…` `0x43cbc008`, `sa_func_NLAP_acquire error` `0x43cc4197`, `sa_func_NLAP_start error (%d)` `0x43cc41d8`, `sa_func_NLAP_release error` `0x43cc4252`) y `sa_func_MOTIONSHOT_*` (0 ocurrencias; la A7S los llama desde IMAGING_CAP `0x43cc403e`/`0x43cc4063` y tiene la firma `sa_func_MOTIONSHOT_release(...)` `0x43ce3448`). En la A6000 queda **`MOTIONSHOTVIDEO`** (24 cadenas, p. ej. `[SFRS][ERR] ***FUNC_CMD_SET_MOTIONSHOTVIDEO_PARAM_PARAMETER_ERROR` `0x43ce99ab`), que es del módulo SFRS y no es lo mismo.
- Abierto: significado de las siglas por familia; estructura de los `<X>_START_PARAM`; algoritmo del SA correspondiente; fases PRE/MAPPING/POST de SPICA; por qué A6000 conserva SFRS/MOTIONSHOTVIDEO.
- Próximo exacto: emparejar cada familia `sa_func_*` con su etapa `Stage_*` (S76) y con los parámetros `apc_*` (S78) para reconstruir el grafo completo del motor de imagen. S51 se mantiene.

## S72 — wireless y transferencia remota (WLAN / PlayMem / Camera on Demand) (21-10-2026, línea general)
- Hecho: integración del hito de wireless (subagente `nemotron-3.5-lightning-free`) **con revisión completa contra los binarios**. Contenido verificado en el userland fw3.21 (`.../nflasha15_unpacked_unpacked/lib`, 157 `.so`): `libWlanAdjust.so` 60 492 B (`WlanAdjust_Init/Res/Sus`, 11 `wpa_ctrl_*`, `wlanLoadFirmware`, `wlanSetSsid/TxCh/TxMode/TxRate/TxPower` + `wlanGet*`, `wlanStartTx/StopTx`, `m_fixed_psk`, `SetMacAddress`); `libWlanControlCommon.so` 23 840 B (`initializePort/finalizePort`, `setPortToStartWlan/StopWlan`, `installWlanDrivers/uninstallWlanDrivers`, `loadWlanFirmware`, 25 × "BMI", GPIO); `libWlanResource.so` 63 656 B (`wlanResource_init/res/sus`, `WlanResourceMainThread`, `GetMacAddress` = `_Z13GetMacAddressPN12WlanResource15ST_MSG_SYNC_REQE`, `startWlan/stopWlan`, 9 × "DFS", colas `OSAL_MSGQ_GID_WLAN_RSRC_DBG`/`_TEST`); `libGOConnectionManager.so` 106 016 B (**348 símbolos mangled, idénticos a los de la A7S**): `GOConnectionManager` (200) con estados Idle→Init→Auth→Wait→ChgKey→AuthConn→Finalizing→Stop y `startGO/stopGO/disconnect/reconnect/authPush/changeKey/cancel`, `GOConnectionManagerCmdMgr` (`IsExec*`, `ChangeState`, `ChkReturnCode`, `ChkFatalError`, `ProcInitialize/ProcStartGO/ProcIdleToAuthReq/ProcWaitAuthReqToChgKey/ProcStopGO/ProcIssueCompErrSequence/ProcIssueFatalError/ProcIgnoreEvt`) y `NetServiceWrapper` (83: WPS `StartWpsCmd/CancelWpsCmd/InputPin/AuthPush/ChangeKey`, eventos `SendStartEvt/SendLostEvt/SendStopCmp/SendFinalizeCmp/SendStartWpsCmp/SendReqWpsEvtPush/ShowPin/InputPin/SendCoonectedEvt/SendRefuseWpsCmp/SendHwErrEvt/SendSwErrEvt/SendWpsCompleteEvt`, consultas `GetSSIDEv/GetTargetDeviceName/GetOwnDeviceName/GetKeyInfo/IsState*`); `libInfraDlnaControl.so` 525 892 B (1971 símbolos; `dc_statetbl`, `dc_evtTbl`, 9 `m_lid_*_caller`, `sendMsgToControlpoint/MediaServer/ContentHandler`, 274 × "DLNA"); `CameraOnDemandSaver.so` 20 084 B (28 símbolos; `CAM_ONDEMAND_SAVER`, hilo `cam_ondemand_saver_thread`, `/dev/ms1`, `/mnt/dcim/100msdcf`, **`/setting/psd.bin`**, `%04d_%02X`, modos FT/YC/normal fsys); `libHapiLib.so` 89 628 B. `netconf/` = directorio con `bss.conf` (WPS `manufacturer=Sony Corporation`, `model_name=SonyImagingDevice`, `device_name=WCM-Sample-Device`, `device_type=1-0050F204-1`, `config_methods=physical_display virtual_push_button`, `uuid=12345678-9abc-def0-1234-56789abcdef0`, `ctrl_interface=/tmp_network/run/wpa_supplicant`, `ap_scan=0`, `wps_cred_processing=1`), `p2p.conf` (`p2p_go_intent=10`, `max_num_sta=1`, `p2p_ssid_postfix=-WCM`, `device_type=4-0050F204-1`, `config_methods=virtual_push_button physical_display keypad`), `dhcpd.conf` (subred `10.0.0.0/16`, rango `10.0.1.1-254`, lease 600/7200) y `pump.conf` (cliente DHCP `ath0`/`ath1`). Informe `analysis/s72_wlan/wlan_playmem.md` + JSON regenerado, test `tests/test_s72_wlan.py` 16/16.
- **Hallazgo nuevo:** el `psd.bin` que escribe `CameraOnDemandSaver.so` es **el mismo** que S75 identificó como origen "from body" de los datos ZPD → el "Camera on Demand" escribe en el almacén de ajustes de la cámara.
- **Correcciones aplicadas al borrador del subagente:** (a) `getMacAddress` → símbolo real `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`; (b) colas `OSAL_MSGQ_GID_WLAN_RSRC_DBG`/`_TEST` (no `…_API`); (c) **`libgps_rsrc.so` SÍ está en el firmware de la A6000** (109 384 B); (d) la cadena GO está **más desarrollada en la A6000** (106 016 B vs 64 580 B de la A7S, mismo esquema de 348 símbolos), no al revés; (e) `netconf` no es idéntico: 3 de 4 ficheros iguales por SHA-256, solo difiere `dhcpd.conf`; (f) la biblioteca HAPI es `libHapiLib.so`, no `libInfraHapiLib.so`.
- Abierto: enlace entre `libGOConnectionManager` y `CameraOnDemandSaver`; motivo del mayor tamaño en fw3.21; destino del `psd.bin`; 10 símbolos de DLNA exclusivos de A6000; 460 `.so` en el firmware A6000 frente a 474 en A7S.

## S85 — CLK_CTRL (control de reloj) y VPH_API (API del vídeo del visor) (21-10-2026, línea general)
- Hecho: mapa de dos módulos **nuevos en la fw3.21 de A6000** (0 trazas en la A7S fw3.20). `[CLK_CTRL]` 66 trazas `0x43c3a1df`–`0x43c3b09c`: 12 llamadas `ddl_clkctrl_*` (`get_clk_chg_enable` `0x43c3a1df`, `unlock_sync_signal` `0x43c3a220`, `lock_sync_signal` `0x43c3a261`, `set_sysv_delay_changing` `0x43c3a2a6`, `set_sysv_delay` `0x43c3a2f2`, `set_sync_signal` `0x43c3a335`, `set_sync_initial_signal` `0x43c3a379`, `set_sysv_initial_delay` `0x43c3a3bf`, `close_dly` `0x43c3a40a`, `open_dly` `0x43c3a442`, `close_clk` `0x43c3a479`, `open_clk` `0x43c3a4b1`); estados `STATE_INIT1(InitDelay)` `0x43c3a534`, `STATE_NORMAL(InitSignal)` `0x43c3a55d`, `STATE_LOCK` `0x43c3a588`, `STATE_CHANGE_CLK` `0x43c3a6e9`, `STATE_CHANGE_CLK_LOCKING` `0x43c3a768`; gestión por subsistema `open subsytem = 0x%04x` `0x43c3a91a`, `close subsytem` `0x43c3a97e`, `Busy!! 0x%04x already opened` `0x43c3a93d`, `lock/unlock_sync_signal subsystem` `0x43c3a5a5`/`0x43c3a5d1`; cambios `CHANGE_CLK dly … clk … change_vfc=0x%x` `0x43c3a71b`, `ClkChgExec` `0x43c3a811`, `DelayChgExec` `0x43c3a8c3`; dos VFC `m_vfc.main=0x%0x, m_vfc.sub=0x%0x` `0x43c3ac2f`; maestro/esclavo `Receive Message from Master` `0x43c3abd0`, `Send Message to Slave` `0x43c3ac86`, `Send HTP at` `0x43c3aae7`, `vph stat:%d,mode:%d` `0x43c3aa69`. `[VPH_API]` 106 trazas `0x43ce32e7`–`0x43ce3dfc`: 49 comandos + 46 gemelos `_sub` + 11 estados (`>hw_status<`, `>mode_status<`, `>preset_area<`, `>histogram_result<`, `>yuv_delay<`, `>osdmix_size_panel/line<`, `>black_frame<`, `>panel_brightness_status<`, `>shutter_mute<`, `>shutter_mute_status<`): `<mode>` `0x43ce32e7`, `<line_out>` `0x43ce32f7`, `<panel_out>` `0x43ce3311`, `<dualpanel_out>` `0x43ce3c84`, `<update_yuv>` `0x43ce332c`, `<mix_mode>` `0x43ce3346`, `<osd_on>` `0x43ce335a`, `<osdarea>` `0x43ce3382`, `<faceframe_on>` `0x43ce33af`, `<update_faceframe>` `0x43ce33c7`, `<faceframe_color>` `0x43ce35e3`, `<timecode_on>` `0x43ce33e3`, `<yuv_mute>` `0x43ce3415`, `<chroma_mute>` `0x43ce344e`, `<shutter_mute_param>` `0x43ce3634`, `<line_closedcaption>` `0x43ce3465`, `<line_macrovision>` `0x43ce3483`, `<line_vbidwss>` `0x43ce349f`, `<line_sync_setup>` `0x43ce34b7`, `<line_fchr>` `0x43ce3652`, `<line_hdmi_still_range>` `0x43ce3667`, `<panel_brightness>` `0x43ce34d2`, `<panel_cabc>` `0x43ce34ee`, `<panel_depth>` `0x43ce3504`, `<panel_reverse>` `0x43ce351b`, `<panel_ysetup>` `0x43ce3534`, `<pictureeffect>` `0x43ce354c`, `<ylevel_caution>` `0x43ce3565`, `<zebra>` `0x43ce357f`, `<peaking>` `0x43ce3590`, `<gridline>` `0x43ce35a3`, `<histogram>` `0x43ce35b7`, `<testpattern>` `0x43ce35cc`, `<diceic_arb>` `0x43ce35fe`, `<parallax_adjust>` `0x43ce3688`, `<set_extblackframe>` `0x43ce36a3`, `<set_color_temperature>` `0x43ce36c0`, `<set_panel_osd_luminance>` `0x43ce3728`. Nota `analysis/s85_clk_vph/clk_ctrl_vph_api.md`, test `tests/test_s85_clk_vph.py` 11/11.
- Enlace con S71 (VERIFICADO): el visor dibuja el marco de la cara detectada (`<faceframe_on>`, `<update_faceframe>`, `<faceframe_color>`).
- Abierto: `laxo`, `diceic_arb`, `ylevel_caution`, `vbidwss`, `fchr`, `extblackframe`, `eomainsub`, `htp`; correspondencia de los canales línea/panel; identidad del "master"; si VPH_API es contrato con hardware o con VDF; motivo de la incorporación en fw3.21.
- Próximo exacto: cruzar `VPH_API` con el módulo `VDF` (243 trazas) y con `PNL`/`ADJ_CMD` (S73) para reconstruir la cadena completa del visor. S51 se mantiene.

## S86 — el subsistema del visor: VDF y VEF (21-10-2026, línea general)
- Hecho: mapa del framework de display y del visor electrónico. **`[VDF]`** (243 trazas, desde `0x43c813fc`): framework C++ con ~200 clases RTTI `N3VDF*` — núcleo (`VDF::SubsystemMain::Main()` `0x43c8221b`, `VDF::SubsystemMain::SendCommandOsal` `0x43c8224a`, `VDF::SubsystemFactory::ExecCmd` `0x43c83b7f`, `N3VDF17SubsystemExportIfE` `0x43c81367`), framework de mensajes (`VDF::MsgAccessor::*` Get/Set…, `VDF::MsgIterator::SendCommandOsal/SendResponseOsal/SendPinOsal/SetStatus/SetCounter`, `VDF::WaitQueue::Enqueue/Dequeue`, `N3VDF11MsgAccessorE`, `N3VDF11MsgIteratorE`), cmds del sistema (`VDF::SystemCmdPinConnect` `0x43c83fd5`, `PinRequestConnect` `0x43c8405b`, `PinSend` `0x43c84318`, `PinGet` `0x43c85f18`, `PinDisconnect` `0x43c85e40`, `Trigger`, `Receive`, `Sysv`, `Debug`, `CipaModeOut`, `NotifyDisplayInfoReady`), cmds de display (`N3VDF24VdfDisplayCmdSetPanelOutE` `0x43c8714a`, `N3VDF31VdfDisplayCmdSetPanelBrightnessE` `0x43c86eea`, `N3VDF36VdfDisplayCmdSetPanelBrightnessSlopeE` `0x43c86836`, `N3VDF37VdfDisplayCmdSetPanelColorTemperatureE` `0x43c86886`, `N3VDF24VdfDisplayCmdSetParallaxE` `0x43c86e1c`, `N3VDF28VdfDisplayCmdSetDetectExtEvfE` `0x43c862b9`, `N3VDF24VdfDisplayCmdSetOsdAlphaE` `0x43c866ef`, `N3VDF31VdfDisplayCmdGetPanelBrightnessE` `0x43c86209`), cmds de entrada (`N3VDF20VdfInputCmdUpdateYuvE` `0x43c888ef`, `N3VDF23VdfInputCmdUpdateYuvPinE` `0x43c89169`, `N3VDF29VdfInputCmdUpdateFaceFramePinE` `0x43c887e9`, `VDF::VdfInputCmdSetOsdArea` `0x43c88066`, `SetYuvLayout`, `SetYuvMute`, `SetShutterMute` `0x43c8818e`, `SetHdTrimming` `0x43c87eec`, `SetBlackFrameNotify`), cmds de servicio (`N3VDF18VdfSrvcCmdSetZebraE` `0x43c8ad68`, `N3VDF20VdfSrvcCmdSetPeakingE` `0x43c8acb7`, `N3VDF22VdfSrvcCmdSetHistogramE` `0x43c8aaad`, `N3VDF22VdfSrvcCmdSetFaceFrameE` `0x43c8a979`, `SetEvfParallax`, `SetLiveDemo`, `SetPanelZoom`, `SetTimeCode`, `SetYcRecControl`), rutas de imagen (`N3VDF14VdfPathSetPathE` `0x43c89fca`, `N3VDF22VdfPathThroughTransferE`, `VdfPath4KResizeTransfer`, `VdfPathLimitCopyTransfer`), memoria (`N3VDF20YuvIndexDoubleBufferE` `0x43c817b5`, `N3VDF29YuvIndexQfhdMemoryManagerImplE`, `N3VDF28VfxRgba8888ToYuv422ProcessorE`, `N3VDF28YuvWorkMemCloseFreeProcessorE`), dispositivos (`N3VDF12EoLineDeviceE`, `N3VDF13EoPanelDeviceE`, `N3VDF11LRMixDeviceE`, `N3VDF27MirrorSubsystemSynchronizerE` `0x43c84c0c`, `N3VDF22EoLineParallaxRepeaterE`) y utilidades (`N3VDF28VdfDefineConverterE` `0x43c83e15`, `N3VDF21VdfSafeMemoryReleaserE`, `N3VDF24VdfDataStructureSnapshotE`, `N3VDF27PerformanceCountAccumulatorE`, `N3VDF21DebugExecCountMonitorE`). Puentes: **VPH** (S85) con `VDF::VdfDisplayCmdSetPanelOut::VphSetZebraCall` `0x43c87294`, `::VphSetPeakingCall` `0x43c872f9`, `::VphSetPanelDepthCall` `0x43c870e0`, `::VphSetTimeCodeCall` `0x43c87360`, `::VphSetPanelOsdLuminanceCall` `0x43c8706f`, `N3VDF20VphUpdateYuvFunctionE` `0x43c85017`, `N3VDF29DrvCallVphLatestCmdHolderImplE` `0x43c8305e`; trazas `CallVphUpdateYuv size_x/size_y` `0x43c82fd7`, `vph_set_yuv_mute_immediately ON/OFF` `0x43c83004`/`0x43c83031`, `adjust BigImage Line/Panel Layout` `0x43c82f27`/`0x43c82f53`; **ADF** (S81) con `N3VDF20VdfToAdfYcDataSenderE` `0x43c86165` y persistencia en el bus **SSBI** (`ssbi_read(%x)` `0x43c814f0`, `ssbi_write(%x)` `0x43c81547`, `Backup_read(BKID_UPM_BOOT_CIPA_FLAG)` `0x43c82329`); **CLK_CTRL** (S85) con `CheckUpdateYuvTiming(VDF::VDF_PRM_SUBSYSTEM_CLKCTRL_INFO)` `0x43c847d1`, `IsCallVphMode(...)` `0x43c8482c`, `N3VDF28HtpVfcMainPerformanceCounterE` `0x43c855f1`; **caras** (S71) con `N3VDF29VdfInputCmdUpdateFaceFramePinE` `0x43c887e9`, `VDF::VDF_ERR UpdateFaceFrameNormal(...)` `0x43c8880f`, `VDF::VdfFaceFrameUtility::UpdateFaceFrameNormal` `0x43c8c014`, `N3VDF34VdfSrvcCmdSetFaceFrameCommonDesignE` `0x43c8a998`. **`[VEF]`** (149 trazas, `0x43c8c26a`+): `reply_osal_id/mirror_osal_id` `0x43c8c36e` (espejo EVF↔panel), `MsgInfoUniqueIdImplanter::Implant` `0x43c8c6b7`, `SubsystemAccessorIf::SetMode` `0x43c8d03a`, multicast de pausa `0x43c8d0dd`–`0x43c8d20f`, `Map Area alloc %x err` `0x43c8d310`, down-conversion `DOWNCON: PAL 50i50p` `0x43c8d394`, `PAL 25p` `0x43c8d3ae`, `NTSC 60i60p` `0x43c8d3e8`, `NTSC 30p24p` `0x43c8d403`, `Invalid clk_rate (%d)` `0x43c8d3c5`, modos `3D/2D/INIT` `0x43c8d5cf`/`0x43c8d5ff`/`0x43c8d62f`, `free DMM_UNITTYPE_DATEREC_WORK_YC` `0x43c8da6b`, cancelación de efectos con **VFC Sync** `0x43c8dc56` (`currentVfc >= targetVfc` `0x43c8dcfd`), `exec time max/ave` `0x43c8d56b`. Nota `analysis/s86_vdf_vef/vdf_vef_viewfinder.md`, test `tests/test_s86_vdf_vef.py` 14/14.
- Abierto: significado del modo "3D" del visor; formato de los mensajes VDF (`VDF_MSG_INFO`, `CATE_ID`, `MSG_ID`, `TRIGGER_TYPE`); implementación del espejo EVF↔panel; efectos de vídeo más allá de la cancelación; si este VDF es el mismo que el citado en S16-S18.
- Próximo exacto: reconstruir el **grafo de módulos del visor** (VDF → VPH → CLK_CTRL → ADF → SSBI) con las dependencias ya conocidas, y cerrar el tema del modo 3D. S51 se mantiene.

## S77 — Creative Style y balance de blancos (21-10-2026, línea general)
- Hecho: integración del hito de picture profile/creative style (subagente `nemotron-3.5-lightning-free`) **con revisión completa contra bytes**. Contenido verificado: dos tablas de estilos en `av-cam.bin` — tabla 1 `0x43ca6702`–`0x43ca676d` (13: Vivid `0x43ca6702`, Neutral `0x43ca6709`, Portrait `0x43ca6712`, Landscape `0x43ca671c`, Clear `0x43ca672b`, Deep `0x43ca6732`, Light `0x43ca6738`, Sunset `0x43ca673f`, Nightview `0x43ca6747`, Autumnleaves `0x43ca6752`, **Real** `0x43ca6760`, Sepia `0x43ca6766`, Standard `0x43ca676d`) y tabla 2 `0x43ca678b`–`0x43ca67f0` (12, sin `Real`); mismas tablas en la A7S fw3.20 (`0x43cb540e`…, `0x43cc5ab8`…). Bloque `wb_*` del **display** (dentro de ADJ_CMD, S73): `wb_b_data=%02X` `0x43c76c26`, `wb_data_tmp=%02X` `0x43c76c36`, `wb_r_data=%02X` `0x43c76c48`, `wb_g_data=%02X` `0x43c76c6b`, `wb_w_data=%02X,` `0x43c76dca`, `wb_mask=%02X,` `0x43c76dbb`, `wb_w_data=%02X` `0x43c76e21`, `wb_mask=%02X` `0x43c76e13`. Userland: `wrapperCreativeStyle.so` 8 420 B (`WrapperCreativeStyle::getCreativeStyle/setCreativeStyle/convertProcessValueIdToValue/convertValueToProcessValueId/isInhOn`, `CmnViewProcessDataMgr::getInstance`, `stella::8BitArray<unsigned int>`, `stella_print_log`, ruta `/home/jp10239/git-work/build/141H/141H.DSLR.DM_UUD3.reco.LATEST.diadem.set/Guiengine_131H/`), `wrapperWhiteBalance.so` 15 556 B (`getWhiteBalance`, `setWhiteBalance(...,int,int,int)`, `resetAdjustmentValue`, `isInhOn`, `WrapperSettingUtil::readBackup/writeBackup` → `BackupManager::Bkup_Read_Setting_Attr`, `ViewBase::requestModelExecute`, `getModelInfo`, `ParamBase`/`PrmNumber`/`ParamList`), `cmnShift{Exposure,Flash}Compensation.so`, `cmnShiftIris.so`, `cmnShiftIso.so`, `cmnShiftShutterSpeed.so`. Informe `analysis/s77_pp/picture_profile_creative_style.md` + JSON regenerado, test `tests/test_s77_pp.py` 10/10.
- **Correcciones de la revisión:** la "tabla de Picture Profile" del borrador (offset `0xaa8d50`) es **código Thumb**; `Highlight`/`Saturation`/`Sharpness`/`CreativeStyle`/`PictureProfile`/`ColorTone`/`wb_shift` tienen **0 apariciones** en `av-cam.bin`; los presets de WB (`Auto`, `Daylight`, …) **no aparecen** en el firmware; los offsets del borrador son de fichero (aquí direcciones del binario).
- Abierto: qué tabla de estilos usa el código y qué es la entrada `Real`; valores por estilo; enumerados `WRAPPER_CREATIVE_STYLE`/`WRAPPER_WHITE_BALANCE`; mapeo PP1..PP6/Off; presets fotográficos de WB; rangos de la compensación.
- Próximo exacto: localizar en el userland el módulo que *posee* los valores de estilo (posiblemente en el GUI engine "Diadem" o en el modelo de ajuste) y el `WRAPPER_WHITE_BALANCE` completo. S51 se mantiene.

## S88 — GOLFSHOT y MOTIONSHOT (21-10-2026, línea general)
- Hecho: integración del hito de modos de disparo (subagente `nemotron-3.5-lightning-free`) **con revisión contra bytes**. Verificado: 72 cadenas con `GOLFSHOT` en ambos modelos, pero en la A6000 la etiqueta va **anidada** en `[IMAGING_RSRC]:` (`SA_LPF Exec` `0x43ca492f`, `SA_BGEST Exec` `0x43ca4984`, `SA_SSP Exec` `0x43ca49d5`, `correctSndDetResult… Out of SoundDetBuff` `0x43ca4a2a`, `vfc2indx: Shot Timing Transform Error` `0x43ca4a8a`), `[IMAGING_CAP]:` (`FREE_ERR[%d]: SSP_IMAGE[%d]` `0x43cacc82`) y `[CAMERA_MAIN_SYNC]:` (`shot_time_vfc error!` `0x43cb18a9`, `Seq._SndDetEE: FATAL ERR` `0x43cb18de`, `ALOCK_ERR…` `0x43cb1915`–`0x43cb1af6`, `Seq._BgestPre: JPEG_DEC OPEN OFF(for debug)` `0x43cb1ba1`, `ADF_START: …` `0x43cb1c5b`–`0x43cb1dd6`); en la A7S las mismas 65 van con `[GOLFSHOT]` como prefijo principal (0 en A6000). Módulo `[SAN]`: `StartGolfShot` `0x43c2c72e`, `StopGolfShot` `0x43c2c77a`, `AnalyzeGolfShot` `0x43c2c792`, `SetSoundAnalyze` `0x43c2c7dd`, `CLAP DETECT SCORE = %d (%d[deg]) DIFF = %d` `0x43ce2f27`; comandos ADF `[ADF][DBGCMD]SoundAnalyzer Start/Stop/AnalyzeGolfShot`, `SetSoundAnalyze` `0x43c2b143`/`0x43c2b16c`/`0x43c2b194`/`0x43c2b1bf`; `[ADF]SAN START/STOP/ANALYZE GOLFSHOT` `0x43c327a6`/`0x43c3287d`/`0x43c36d0a`. API SA: `sa_func_GOLFSHOT_start(SSP_START_PARAM*, SSP_START_MBX*)` `0x43cedc91`, `sa_func_GOLFSHOT_start(BGEST_START_PARAM*, SA_MBX_0123*)` `0x43cedff6`, `sa_func_GOLFSHOT_release` `0x43cedf67`. **MOTIONSHOT eliminado** en la A6000 (0 apariciones de `sa_func_MOTIONSHOT`; A7S: 5) y permanece `MOTIONSHOTVIDEO` (24, módulo SFRS) `0x43ce99ab`. Informe `analysis/s88_shotmodes/golfshot_motionshot.md` + JSON regenerado, test `tests/test_s88_shotmodes.py` 9/9.
- Corrección de la revisión: el borrador citaba etiquetas de Ghidra (`s__GOLFSHOT__…`) en vez de cadenas reales y atribuía el prefijo de módulo sin comprobar que en la A6000 va anidado.
- Abierto: qué es "ALOCK" y cómo se combinan los búferes; unidad de `vfc2indx`; significado de `deg`; si el `JPEG_DEC` de BGEST es el decodificador del proyecto; motivo de la eliminación de MOTIONSHOT.

## S89 — el módulo IDT/IDT_OPD (21-10-2026, línea general)
- Hecho: mapa del módulo que calcula y entrega al imager los mapas de parámetros. Hallazgo: `[IDT]` (297 cadenas) y `[IDT_OPD]` (273) son **el mismo código con dos prefijos**: cada mensaje aparece dos veces contiguas (`4cmap.adrs Err:%X` `0x43cf2c2e`/`0x43cf2c4b`; `histmap` `0x43cf2c64`/`0x43cf2c83`; `summap` `0x43cf2c9e`/`0x43cf2cbc`; `shade_map` `0x43cf2bf0`/`0x43cf2c11`; `imgmap` `0x43cf1e45`/`0x43cf1e63`; `refmap` `0x43cf1eb5`/`0x43cf1ed3`; `backImgData` `0x43cf1e03`/`0x43cf1e26`; `miniRAW` `0x43cf40e0`/`0x43cf4100`; `msain0` `0x43cf463d`/`0x43cf4652`; `msain1` `0x43cf4663`/`0x43cf4678`; `msaout` `0x43cf4689`/`0x43cf469e`; `p_backImgData` `0x43cf46ff`/`0x43cf471b`; `refmap` `0x43cf47cb`/`0x43cf47e0`). Mapas entregados: `backImgData`, `imgmap`, `refmap`, `shade_map`, `4cmap`, `histmap`, `summap`, `miniRAW`, `msain0/1`, `msaout`, `ie_in/ie_out`, `lc_in/lc_out/lc_miniraw`, `mapRC_in`, `p_img_map`, `out_opd_cc/out_opd_ec`. `miniRAW` consumido por el AF híbrido (`[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle` `0x43c9c8ba`). FOPD: `FOPD_AIF_R0/W0/W1/W2_ERROR:%x` `0x43c91547`/`0x43c91567`/`0x43c91587`/`0x43c915a7`, `KickFOPD error` `0x43cadd2d`/`0x43cadd60`, reparto por `SyncResMgr` (`[IDT]r0:…[FOPD]r0:…[PRC]r0…` `0x43ca2939`). Split/IDTSA: `GetIDTSA Unknown aspect:%d` `0x43cf3306`/`0x43cf332c`, `calc SplitIDTSA error` `0x43cf34d4`/`0x43cf3508`, `IDTSA Invalid Ch select` `0x43cf3538`/`0x43cf3562`, `Illegal FRM mode for IDTSA` `0x43cf5147`, `Split Movie Cannot use AIF/Insel`, `Fatal Not Copiled for Split Cap`. Regiones de detección (enlace con `[TRK]: [STK]` de S71): `kido_th[%d].up/dn` `0x43cf2962`/`0x43cf2983`, `ratio_wak[%d].up/dn/rgt/lft` `0x43cf29de`/`0x43cf2a01`/`0x43cf2a62`/`0x43cf2a86`, `sel_hist` `0x43cf2b54`/`0x43cf2b6f`, `sel_sum`, `sel_wak`, `sel_waku[%d]`, `idealWidth/idealHeight`, `mask.x_end/.y_end`. VATR: `VATR Error det:%x gle:%x` `0x43cf3ec8`, `VATR released when moving` `0x43c91609`, `SyncResMgr::Free: MODE_EE(01), IDT_STOP_ERR(VATR)` `0x43c9b5ab`. NSX_OPD: `FRM set SGC unknown %d` `0x43c915c7`, `FRM start unknown %d` `0x43c915e9`, `IDT AIF illegal address`. Nota `analysis/s89_idt/idt_opd_maps.md`, test `tests/test_s89_idt.py` 11/11.
- Abierto: qué distingue `[IDT]` de `[IDT_OPD]`; `kido_th`/`ratio_wak`/`waku`/`gle`; formato de los mapas; qué es FOPD; coordenadas del modo Split; `NSX`/`SGC`.
- Próximo exacto: emparejar los mapas del IDT con los que consume el ZIT (S80) y el motor de imagen (S84) para cerrar la cadena imager↔defectos. S51 se mantiene.

## S82 — AutoFraming y las etapas de control del pipeline (21-10-2026, línea general)
- Hecho: integración del hito de AutoFraming (subagente `nemotron-3.5-lightning-free`) **con revisión contra bytes**. Verificado: tres etapas `Stage_AutoFraming.cpp` `0x43cc71a3`, `Stage_AutoFraming_ResizeRotate` `0x43cc71b9`, `Stage_AutoFraming_Branch` `0x43cc71d8` — **las mismas en la A7S fw3.20** (`0x43cc26ac`/`0x43cc26c2`/`0x43cc26e1`); log de encuadre forzado `[IMAGING_CAP]: Debug) ResizeRotate Framing size force set: offset[%d,%d] size[%d,%d] rotate[%d]` `0x43cc7143` (A7S `0x43cc265b`); validación previa `ResizeRotate Paramter Error: ImageAreaResize.us_Size_X = %d` `0x43cc6e5f`, `us_Size_Y` `0x43cc6eaa`, `canvas_size.ul_SizeX(%d) < ImageAreaResize.us_Frame_X(%d)` `0x43cc6ef5`, `ul_SizeY` `0x43cc6f79`, `Align Error us_Frame_X/us_Frame_Y/us_Size_X/us_Size_Y` `0x43cc6ffd`–`0x43cc70f2`. Ocho etapas de control (iguales en A7S): `Stage_CaComm.cpp` `0x43cc7b9c`/`0x43cc2d53`, `Stage_CameraHAPI.cpp` `0x43cc7bad`/`0x43cc2d83`, `Stage_Notify.cpp` `0x43caccd6`/`0x43cb07bb`, `Stage_NotifyLongExpNRCapturing` `0x43caccb7`/`0x43cb079c`, `Stage_WaitControl.cpp` `0x43cad784`/`0x43cb0f69`, `Stage_SACC` `0x43c9ee6c`/`0x43ca484d`, `Stage_SACC.cpp` `0x43c9f18a`/`0x43ca4a8a`, `Stage_Common.cpp` `0x43cac363`/`0x43cb0098`, `Stage_DevLater.cpp` `0x43cac51b`/`0x43cb01ef`, `Stage_DualRec.cpp` `0x43cac9f8`/`0x43cb0591`. Relación SA (INFERENCIA por proximidad en rodata): `CaComm`→`sa_func_CONTP_acquire error` `0x43cc7bfa`, `DualRec`→`sa_func_DUALREC_BAYER_acquire` `0x43cac9c1` y `sa_func_DUALREC_CLEARVID_start` `0x43cac867`, `SACC`→`sa_func_NFLASH_start error` `0x43c9ef73`. Informe `analysis/s82_autoframing/autoframing_stages.md` + JSON regenerado, test `tests/test_s82_autoframing.py` 8/8.
- **Correcciones:** (a) `Stage_WaitControl.cpp` está en `0x43cad784`, no `0x43cad6fd` (esa es `Stage_RchRcv_ResizeTrim`) — el error estaba **también en S76** y se ha corregido allí con test; (b) es **falso** que en la A7S el AutoFraming esté disperso o ausente: tiene las mismas tres etapas y el mismo log.
- Abierto: cómo se calcula el encuadre y qué es la rotación impuesta; su relación con los `apc_*`; qué intercambian `CaComm`/`CameraHAPI` con la app; qué es "SACC".
- Siguiente línea libre: S87 (almacenamiento/exFAT), pendiente por cuota de subagentes; en paralelo el agente principal puede emparejar el encuadre con los `apc_*` del motor YC.

- **2.ª entrega (subagente, ya con las correcciones de la revisión aplicadas):** el informe incluye
  ahora la tabla completa de las **ocho etapas de control** con direcciones en A6000 **y** A7S
  (`Stage_CaComm.cpp` `0x43cc7b9c`/`0x43cc2d53`, `Stage_CameraHAPI.cpp` `0x43cc7bad`/`0x43cc2d83`,
  `Stage_Notify.cpp` `0x43caccd6`/`0x43cb07bb`, `Stage_WaitControl.cpp` `0x43cad784`/`0x43cb0f69`,
  `Stage_SACC` `0x43c9ee6c`/`0x43ca484d`, `Stage_Common.cpp` `0x43cac363`/`0x43cb0098`,
  `Stage_DevLater.cpp` `0x43cac51b`/`0x43cb01ef`, `Stage_DualRec.cpp` `0x43cac9f8`/`0x43cb0591`) y la
  relación con el motor de imagen por proximidad en rodata (`CaComm`→`CONTP`,
  `DualRec`→`DUALREC_BAYER`/`DUALREC_CLEARVID`, `SACC`→`NFLASH`); confirma que **en AutoFraming no
  hay ninguna llamada `sa_func_*`** (el encuadre se aplica con parámetros de imagen propios,
  `ImageAreaResize`). Test `tests/test_s82_autoframing.py` 8/8.
## S91 — submódulos del framework ADF (21-10-2026, línea general)
- Hecho: cierre de los submódulos de ADF que S81 dejó abiertos. `[ADF][ADJ]` (24 trazas) = ajuste del sensor de audio: `AdfSenserCtrl::SetParamSetMicMode err %x` `0x43c26dc1`, `SetParamSetRecLevel` `0x43c26df4`, `SetParamSetChSource` `0x43c26e28`, `SetParamSetInputType` `0x43c26e5c`, `SetParamSetRecLevelMode` `0x43c26e91`, `SetParamSetHpMonitor` `0x43c26ec9`, `SetParamSetInputTrim` `0x43c26efe`, `SetParamSetLowCut` `0x43c26f33` → es la implementación de los comandos `[ADF][DBGCMD] InputPro Set*` (S81) y enlaza con S69. `[ADF][SYSND]` (27) = sonido del sistema: `PS ON` `0x43c278f0`, `SET PATH SendComp Err` `0x43c27904`, `m_dummySetOutputSysndDelay` `0x43c27941`, `m_StartTransDelay60` `0x43c279a4`, `m_StartTransDelay50` `0x43c279f9` → retardo según el estándar de TV (60/50 Hz), en el mismo eje que el `DOWNCON` PAL/NTSC del visor (S86). `[ADF][GS]` (2) = `START PROC PATH ERR` `0x43c327d3`, `START STATE ERR state : %x` `0x43c327f2`. `[ADF][FACE]` (2) = `StartExecFace` `0x43c32a3b`, `StopExecFace` `0x43c32a54` → el ADF arranca/detiene la detección de caras (puente ADF↔S71). `[ADF][AFNR]` (2) = `StartExecAfnr:%x` `0x43c32990`, `StopExecAfnr` `0x43c329ac` → proceso de reducción de ruido del AF. `[ADF][CH_SRC]` (1) = `AvioMicStateStart fifoErr %x` `0x43c2e99a` → micrófono AVIO. Nota `analysis/s91_adf/adf_submodules.md`, test `tests/test_s91_adf_submods.py` 8/8.
- Abierto: qué es "GS"; el modo de AFNR; los 24 mensajes de ADJ completos; la relación de los retardos 60/50 Hz con el estándar de TV.
- Próximo exacto: con S87 (almacenamiento, subagente en curso) cierra el mapa de subsistemas; queda por hacer el grafo de dependencias entre módulos a partir de `analysis/s79_modules/module_map.json` y `analysis/s71_frc`/`analysis/s86_vdf_vef`.

## S87 — almacenamiento, sistema de archivos y tarjeta (21-10-2026, línea general)
- Hecho: integración del hito de almacenamiento (subagente `nemotron-3.5-lightning-free`) **con revisión contra bytes**. Verificado en `av-cam.bin`: `ExternalStorageStart/Acquire/Release() Error` `0x43cb3148`/`0x43cb317f`/`0x43cb31b8` (A7S `0x43cb4372`) → el medio externo es un recurso sincronizado de `CAMERA_MAIN_SYNC`; `DCIM/100MSDCF/DSC%05d.ARW` `0x43cac566` (A7S `0x43cb022b`); ejemplo literal `DCIM/100MSDCF/DSC00001.ARW` `0x4401ea7f` (A7S `0x440241e5`); `/setting/psd.bin` `0x43ccf2b6` (**0 en A7S** → novedad fw3.21, coherente con S75/S72); `LiroSequencerMovieFileFormat : %d` `0x43ca3b3a`; **negativo**: 0 hits de `exFAT`/`EXFAT`/`FAT32`/`CLIP_` en `av-cam.bin`. Verificado en el userland: `libInfraFsys.so` 375 524 B (51 × "EXFAT", 8 × "FAT32", BPB `BPB_Media`/`BPB_TotSec16/32`/`block size|start (org|adj)`, `FSYS_ATTRIB_{ALL,ARCHIVE,DIRECTORY,HIDDEN,NONE,READONLY,SYSTEM,VOLUME}`, `create UTC Offset`, `create time_10ms`); `libObj.so` 17 436 172 B (13 × "CLIP_", `contentType`, `p_entryIdList`, `entryCondition`, `p_listInfo`, `mediaSizeOnDstDisc`, `remainSizeOnDstDisc`, `forcastUseSizeOnDstDisc`, `isExistUnsupportedContent`, `dubbingProhibitionFactor`, `mainJpg`, `thumJpg`, `screenNail`, `exifSrcArea`, `lensModel`, `pimInfo`, `publicMakerNote`, `secretMakerNote`, `software`, `mpfSrcArea`); `libmpr.so` 10 321 204 B (`category folder`, `content num`, `date num`, `entry num`, `last content`, `last date folder`, `playlist num/folder/category folder/content num`, `total mark num`, `creationTime`, `bckPropFileModTime`, `orgPropFileModTime`, `thumbPictFileModTime`, `aviFileModTime`, `seekPoint 0x%08x: packLength 0x%08x PH %d PF%d`). Las tres bibliotecas existen también en la A7S (373 900 / 16 184 848 / 10 321 412 B). Informe `analysis/s87_storage/storage_filesystem.md` + JSON regenerado, test `tests/test_s87_storage.py` 9/9.
- **Correcciones de la revisión:** el borrador daba **offsets de fichero** (`0x772148`…) en vez de direcciones del binario; afirmaba que `CLIP_` estaba en `av-cam.bin` (está en `libObj.so`/`libmpr.so`); y daba la implementación de exFAT por no localizada (está en `libInfraFsys.so` con BPB y atributos FSYS).
- Abierto: MBR/particiones y formateo; máximo de imágenes por carpeta y regla "reducir/divide"; prefijos de nombre más allá de `DSC%05d.ARW`; formato binario de `Index/`/`SceneInfo`/`DCF`; contenedores de vídeo en tarjeta.

## S93 — el bus de mensajes OSAL del userland (21-10-2026, línea general)
- Hecho: mapa de los servicios del lado Linux de la cámara y sus colas de mensajes. **16 grupos (GID)**: `OSAL_MSGQ_GID_AIRPLANE_MODE_SCALAR_API`/`_TEST` (libInfraAirplaneMode.so), `OSAL_MSGQ_GID_APP_VIEW_SCALAR`/`INFRA_VDF`/`CAMERA_RAW_DEVELOP`/`NET_BACKUP_SERVER` (libObj.so), `OSAL_MSGQ_GID_DETECT_FACE`/`DMM_CTRL`/`SADRIVER` (libBizFw.so, + DMM_CTRL en libInfraHdmi.so), `OSAL_MSGQ_GID_GPS_GET` (libmpr.so), `OSAL_MSGQ_GID_NETSERVICE_SCALAR_API`/`SYNC_EMU`/`TEST` (libNetService.so), `OSAL_MSGQ_GID_TASK_ADC` (libRsrcHotshoe.so), `OSAL_MSGQ_GID_WLAN_RSRC_DBG`/`_TEST` (libWlanResource.so). **13 colas (LID)**: `AIRPLANE_MODE_API`, `DLNACONTROL_CP`/`_MAIN`/`_MEDIASVR` (libInfraDlnaControl.so), `GPS_GET` (libmpr.so), `MDNS_CONTROL_MAIN` (libInfraMDnsControl.so), `NETFUNCTIONMGR_MAIN` (libInfraNetFunctionManager.so), `NETSERVICE_ASYNC_REQ`/`SYNC_REQ` (libNetService.so), `NET_BACKUP_SERVER_INFRA_NET_SERVICE_CMP` (libObj.so), `R_HOTSHOE_API` (libRsrcHotshoe.so), `WEBAPI_MAIN` (libInfraWebApi.so), `WLAN_RSRC_API` (libWlanResource.so). Hallazgos: (a) `libBizFw.so` orquesta la **detección de caras** y el driver del escalar; (b) la A6000 **incluye GPS en el firmware** (`libgps_rsrc.so` + `OSAL_MSGQ_GID_GPS_GET`) aunque no tenga hardware (código heredado de la A7S); (c) la cámara **se anuncia por mDNS y expone una API web**. Nota `analysis/s93_osal_bus/osal_message_bus.md`, test `tests/test_s93_osal_bus.py` 6/6.
- Abierto: los mensajes concretos de cada cola; qué sirven `CAMERA_RAW_DEVELOP` y `NET_BACKUP_SERVER`; si el bus OSAL del userland es el mismo que el ADF del firmware; el protocolo de la API web.
- Próximo exacto: enumerar las categorías/IDs de mensaje del `libBizFw.so` (el orquestador) para cerrar el puente userland↔firmware. S51 se mantiene.

## S90 — reproducción de vídeo: PlayArranger, VFC y VDISP (21-10-2026, línea general)
- Hecho: integración del hito de reproducción (subagente `nemotron-3.5-lightning-free`) **verificado por muestreo (15/15)**: organización de reproducción (`20AbstractPlayArranger` `0x43c43c7c`, `12PlayArranger` `0x43c43c93`, `19PlayArrangerAdapter` `0x43c43cd2`, `16NullPlayArranger` `0x43c43d00`, `20VideoArrangerAdapter` `0x43c43cbb`, `22VideoReserveCmdCreator` `0x43c43ca2`); programador de VFC (`20AbstractVFCCmdIssuer` `0x43c43dea`, `12VFCCmdIssuer` `0x43c43e01`, `12VFCScheduler` `0x43c43e95`, `12VFCSchedulerCore` `0x43c43ea4`, `14VFCScheCmdList` `0x43c43e3a`, `16VFCReScheCmdList` `0x43c43e4b`, `24VideoFieldCounterFactory` `0x43c43e1f`); estado de reproducción (`10MPlayState` `0x43c43ecf`, `MPlay` `0x43c66542`, `bid=MPLAY cid=%#hx flg=%d dvfc=%#x ivfc=%#x edge=%#hx` `0x43c660e0`, `Issue VFCCmd to MPLAY.` `0x43c7291e`); cuatro modos de salida VDISP (`VDISP24p` `0x43c4811f`, `VDISP30p25p` `0x43c481c2`, `VDISP60i50i` `0x43c48341`, `VDISP60p50p` `0x43c4856a`) con `[DiscardTcub] [cnt:t/b/p][%d] tc[%d][0x%02x%02x…]`; bloque AUGI (`21DecTcubEventRequester` `0x43c43ce8`, `20NullDecAugiConverter` `0x43c43d13`, `16DecAugiConverter` `0x43c43d2a`); tabla VP (`24AbstractVpTableSequencer` `0x43c43d3d`, `16VpTableSequencer` `0x43c43d58`, `6VPInfo` `0x43c43d6b`, `10VPInfoCore` `0x43c43d73`, `21AbstractTblMsgHandler` `0x43c43d94`, `13TblMsgHandler` `0x43c43dac`); y otros (`24AbstractDecCmdDelayChain` `0x43c43dbc`, `18ResumePointChanger` `0x43c43f04`, `20RestartParamModifier` `0x43c43f19`, `20AVRendezvousNotifier` `0x43c43f30`, `18ReserveCmdRegister` `0x43c43f47`, `13IpcmMsgSender` `0x43c43f5c`, `19DecRestartRequester` `0x43c43f6c`, `19DecBBCmdRequester` `0x43c43f82`). Informe `analysis/s90_playback/playback.md` + JSON, test `tests/test_s90_playback.py` 23/23.
- Revisión: **sin correcciones** (15/15 nombres de clase y las cadenas clave verificados en sus direcciones). Enlaces: el VFC es el mismo reloj que `CLK_CTRL` (S85) y los modos VDISP el mismo eje PAL/NTSC que el visor (S86); el bloque AUGI conecta con S83.
- Abierto: la semántica de `cid`/`flg`/`dvfc`/`ivfc`/`edge`; qué son los cubos TCUB; `VPInfo` ↔ AUGI; el punto de reanudación y la reserva.

## S95 — los ficheros que la cámara lee y escribe (21-10-2026, línea general)
- Hecho: inventario de las 43 rutas de fichero que usa el firmware de la A6000 fw3.21. `/usr/sabin/` (27): **22 ficheros SPICA** `spica_musashi_<modo>_<canal>_tap_step<N>.bin` (modos still, mov, mov_4k, mov_interlace, dualrec, dualrec_4k; canales C e Y; dos pasos) — `still_c_tap_step1` `0x43cc3774`, `still_c_tap_step2` `0x43cc3834`, `still_y_tap_step1` `0x43cc3894`, `still_y_tap_step2` `0x43cc3315`, `mov_c_tap_step1` `0x43cc3375`, `mov_c_tap_step2` `0x43cc33d5`, `mov_y_tap_step1` `0x43cc3435`, `mov_y_tap_step2` `0x43cc34f5`, `mov_4k_c_tap_step1` `0x43cc35f4`, `mov_4k_c_tap_step2` `0x43cc3495`, `mov_4k_y_tap_step1` `0x43cc36b4`, `mov_4k_y_tap_step2` `0x43cc3714`, `mov_interlace_c_tap_step1` `0x43cc3654`, `mov_interlace_y_tap_step1` `0x43cc37d4`, `dualrec_c_tap_step1` `0x43cc3b3a`, `dualrec_c_tap_step2` `0x43cc3cba`, `dualrec_y_tap_step1` `0x43cc3ada`, `dualrec_y_tap_step2` `0x43cc3bfa`, `dualrec_4k_c_tap_step1` `0x43cc38f4`, `dualrec_4k_c_tap_step2` `0x43cc3b9a`, `dualrec_4k_y_tap_step1` `0x43cc3954`, `dualrec_4k_y_tap_step2` `0x43cc3c5a`; `star_kernel_param.bin` `0x43cc3d1a`; `dcv_psf_table_still.bin` `0x43cb9a34`, `dcv_psf_table_movie.bin` `0x43cba98a`, `dcv_psf_table_movie_4k.bin` `0x43cbaa4a`, `dcv_psf_table_dualrec.bin` `0x43cba9ea`. `/mnt/` (11): trazas de la propia cámara — `/mnt/%s.%4d%02d%02d_%02d%02d%02d.dat` `0x43cb4eeb` (con fecha/hora), `/mnt/FILE%04x.dat` `0x43cbe562`, `/mnt/FILE_IS_%04x.dat` `0x43c9a535`, `/mnt/FILE_TC_COMMON_%04x.dat` `0x43ca84f2`, `/mnt/lc_mslog_%04x.dat` `0x43ca7a7d`, `/mnt/Mount_ms_log_%03d.dat` `0x43c97146`, `/mnt/cc_ms_log%04x.dat` `0x43cb5004`, `/mnt/cc_ms_log%s.dat` `0x43cb4f4d`, `/mnt/detect_ms_log%04x.dat` `0x43c9162e`, `/mnt/log.bin` `0x43c8f789`. `/setting/psd.bin` `0x43ccf2b6` (0 en A7S). `/usr/dfe/dfe.bin` `0x43cd1b94`. `/etc/localtime` `0x43bd5744`, `/usr/share/zoneinfo` `0x43bd5754`, `/usr/share/locale` `0x43bd92b4`. Nota `analysis/s95_files/file_inventory.md` + JSON, test `tests/test_s95_files.py` 7/7.
- **Hallazgo operativo:** la cámara escribe sus propias trazas en el disco RAM con nombre por módulo y fecha/hora → deben estar en los volcados de `analysis/camera-dumps/` (S64/S65) → fuente primaria para contrastar montura (S66), ZPD (S75), IS/EIS (S70) y detección (S71) sin más instrumentación.
- Abierto: formato binario de los `spica_musashi_*` y de las tablas PSF; qué es "musashi"; formato de `/mnt/*.dat`; supervivencia de esas trazas en el volcado; por qué 4K/dualrec tienen parameter sets propios.

## Mapa de temas en vuelo y estado (21-10-2026, fin de ronda)

**Cuota de subagentes (re-verificada 21-10-2026 20:30-20:40, 10 modelos probados uno a uno):**
con cuota **solo 2**: `opencode/nemotron-3.5-lightning-free` (sigue entregando hitos; **ya no
aparece en el catálogo** del `models` tool, pero sigue enrutando — id histórico) y
`opencode/minimax-m3.1-flash-free` (el propio modelo del agente principal). **Rate limit
exceeded** en los 8 restantes: `flint-40b-free`, `nemotron-3.5-super-vl-free`, `beam-free`,
`longcat-2.5-preview-free`, `mimo-v2.6-flash-free`, `deepseek-v4.1-flash-free`,
`glm-5.3-flash-free`, `big-pickle` (dos rondas, resultado estable). El catálogo actual
expone 9 modelos `free` (ya no incluye `nemotron-3.5-lightning-free`); los ids sin sufijo
`-free` (p. ej. `deepseek-v4.1-flash`, `beam`) dan "Model not available". El límite es
**por modelo**, no global: los 8 agotados fallan mientras los 2 con cuota responden en
paralelo. Se lanzan tandas de hasta 3 subagentes y, en paralelo, el agente principal trabaja
en los mismos temas (sin sesiones REA: 0 Ghidra abiertas, 9 GiB libres).

**Ventana de reinicio (21-10-2026 20:40, medido sobre `~/.local/share/opencode/opencode.db`):**
el límite es **por modelo** (cada modelo free tiene su propio cupo) y **no se reinicia solo**:
reconstruyendo los mensajes `assistant` (ok/err por modelo y hora) se ve que cada modelo muere
al agotar su cupo y sigue muerto muchas horas después — `longcat-2.5-preview-free` último OK
01:14 y 429 desde entonces, `mimo-v2.6-flash-free` 01:35, `glm-5.3-flash-free` 01:47,
`big-pickle` 01:49, `beam-free`/`nemotron-3.5-super-vl-free`/`deepseek-v4.1-flash-free` 03:16-03:17,
`nemotron-3-ultra-free` 09:37 (932 OK previos) — **sin recuperación en 11-20 h**. Único caso de
recuperación observado: `nemotron-3.5-super-vl-free` 429 a las 01:23 y OK otra vez a las 01:28
(+5 min) → componente de **ráfaga** (~15-20 rpm) además del cupo. No hay `Retry-After` visible:
el CLI no lo expone y la llamada directa a `https://opencode.ai/zen/v1` con `curl` devuelve
**403 `FreeTierError`** (el free tier solo se puede usar desde dentro de OpenCode). Según la
documentación pública de OpenCode/Comunidad, la ventana gratuita es diaria y se reinicia a las
**00:00 UTC** (mediciones del `Retry-After` en issues de opencode apuntan al siguiente 00:00 UTC;
el soporte de OpenCode remite a help@anoma.ly para el dato exacto de cuenta). **Sonda en marcha**:
`/tmp/opencode/quota-probe.sh` (PID en background) comprueba cada 10 min dos modelos centinela
(`longcat-2.5-preview-free`, `deepseek-v4.1-flash-free`) y, al primer OK, prueba los 8; el
resultado queda en `/tmp/opencode/quota-probe.log` con sello UTC.

**Hitos de esta ronda (todos publicados en `origin/main`):**

| hito | tema | origen |
|---|---|---|
| S71 | caras / FC-FRC (99 ficheros, puente con el escalar) | subagente + revisión |
| S72 | wireless / PlayMem / Camera on Demand | subagente + revisión |
| S73/S74 | protocolo `ADJ_CMD` y su máscara de 8 sub-comandos | propio |
| S77 | Creative Style y WB (tablas de estilos; `wb_*` del display) | subagente + revisión |
| S78 | los 50 parámetros `apc_*` del motor YC | propio |
| S79 | mapa de los 348 módulos del firmware | propio |
| S80 | ZIT: corrección de defectos (DDC) | propio |
| S81 | ADF: framework, MSGQ, MMGR, 102 DBGCMD | propio |
| S82 | AutoFraming y etapas de control | subagente + revisión |
| S83 | módulos menores (ACCY, CAM_FUNC_MGR, VIDENCSTAT, ENCSEQCTRL, SAD, PNL, AUGI, WSX) | propio |
| S84 | API del motor de imagen (`sa_func_*`, 19 familias) | propio |
| S85 | `CLK_CTRL` + `VPH_API` (nuevos en fw3.21) | propio |
| S86 | `VDF` + `VEF` (el visor) | propio |
| S87 | almacenamiento, sistema de archivos, tarjeta | subagente + revisión |
| S88 | GOLFSHOT y MOTIONSHOT | subagente + revisión |
| S89 | `IDT`/`IDT_OPD` (mapas del imager, FOPD, Split) | propio |
| S90 | reproducción de vídeo (PlayArranger, VFC, VDISP) | subagente + revisión |
| S91 | submódulos del framework ADF | propio |
| S92 | base de datos de medios (SceneInfo/MovieFile) | subagente + revisión |
| S93 | bus de mensajes OSAL del userland (16 GID, 13 LID) | propio |
| S94 | API HAPI de la app remota | subagente + revisión |
| S95 | inventario de ficheros que la cámara lee y escribe | propio |
| S96 | modos de captura (`drive_mode`, `CapMode`, 69→14 ShdMode) | propio |

**Correcciones de revisión aplicadas a hitos previos:** S76 (`Stage_WaitControl.cpp` en `0x43cad784`,
no `0x43cad6fd`) y S68 (test canónico, direcciones y el diferencial A7S).

**Líneas libres para la siguiente ola** (verificadas sin colisión con `docs/` ni con `analysis/`):
- `SceneInfo`/índice de medios (S92, en curso), API HAPI (S94, en curso), modos de captura (S96, en curso).
| S97 | sincronización audio-vídeo del codificador (`ENCMODEMGR`/`ENCAUDSYNC`/`SYNCENCSTART`) | subagente (en curso) |

- Todavía sin tocar: `libBizFw.so` (el orquestador de servicios: sus categorías/IDs de mensaje y su
  puente con el ADF del firmware), y el grafo de dependencias entre módulos a partir de
  `analysis/s79_modules/module_map.json`.

## S92 — la base de datos de medios: SceneInfo, MovieFile e índice (21-10-2026, línea general)
- Hecho: integración del hito de base de datos de medios (subagente `nemotron-3.5-lightning-free`) **verificado por muestreo**: en `av-cam.bin`, `[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` `0x43ca3b3a` (el secuenciador LIRO, que además lee la **posición del dial de diafragma**: `LiroSequencer cannot read IRIS_DIAL_POS` `0x43ccadbf`) y `Scene%02d.txt` `0x43ccb21b`; en el userland, `libmpr.so` con la interfaz `MprIf` (1525 apariciones), `PreRegisterDcfContentSync` (8), `GetHighlightSceneInfo` (2) y `SceneInfo` (10), y `libObj.so` con `SceneInfo`/`HighlightScene` (5). Enlaza con S87 (modelo de objetos e índice). Informe `analysis/s92_mediadb/media_database.md` + JSON, test `tests/test_s92_mediadb.py` 10/10.
- Revisión: **sin correcciones**; se añade el dato de `IRIS_DIAL_POS`.
- Abierto: contenido y ubicación de los `Scene%02d.txt`; la relación con la especificación DCF (`xDCF`/`D2FxDCF`); `MovieFileFormat` vs la nomenclatura de clips; el formato del índice en disco (`Index/`).

## S94 — la API HAPI de la app remota (21-10-2026, línea general)
- Hecho: integración del hito de la API HAPI (subagente `nemotron-3.5-lightning-free`) **verificado por muestreo**: `libHapiLib.so` 89 628 B (A7S 77 380 B) con `HapiLibMain` (5), `Cam::CamService` (19), `Sdf::SdfService` (34), `CamApi` (197 apariciones; **139 símbolos mangled** `Camera::CamApi*`), tipos de mensaje `REQ_MSGE` (29), `EVT_MSGE` (3), `COMP_MSGE` (53), `SDF_MSG_SENDE` (6), `MAIN_MSG_RECVE` (4), `CATEID_HAPI` (1) + `CATEID_SDF_ACK/COMP/NEXT`, y primitivas OSAL (`osal_snd_msg`, `getTargetQId`, `mainLoop`, `interrupt`). La API de cámara: `CamApiBase::apiFactory`, `stmDepositYc`, `stmDepositRaw`, `stmInquire`, `stmWithdraw`, `checkOneTicket`/`checkThreeRawTickets`, `convertErrorCode`, `freeImageInstance`/`freeExif`/`freeStdYc`, `setHapiCommon`. En la cámara, la etapa `Stage_CameraHAPI.cpp` `0x43cc7bad` (S82). Informe `analysis/s94_hapi/hapi_api.md` + JSON, test `tests/test_s94_hapi.py` 6/6.
- Revisión: **sin correcciones**; se añade la interfaz `Camera::HAPI` (`processReq`, `processComp`, `processCaptureEvent`).
- Abierto: los IDs numéricos de `msg_id`; el mapeo cola OSAL ↔ `Stage_CameraHAPI`.

## S96 — modos de captura: drive_mode, CapMode y la tabla 69 → 14 ShdMode (21-10-2026, línea general)
- Hecho: dos niveles de modo. **imager**: `drive_mode` 0..0x44 = 69 valores (`Invalid SetExposure Error!! [drive_mode:%2d]` `0x43c9397a`, `Invalid Execute` `0x43c93a6c`, `Invalid SetRead` `0x43c93d30`, `GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]` `0x43c94a9f`, `Invalid GetModeParam` `0x43c94aff`, `eyePtn:%d is unusable in driveMode:%d` `0x43c92bde`, `GetPrelightImagerDriveMode` `0x43cae26b`, `getDriveModeSizeRatio Error!` `0x43cae2b7`). **captura**: `CapMode`/`ExposureID`/`ContID`/`FrameID`/`BDROSeq` en `CAMERA_MAIN_CC` (`ExtractCaptureData()` `0x43ca54c8`, `CaptureInit()` `0x43ca552b`, `SetReadImageParam()` `0x43ca55a9`, `SetNRParam()` `0x43ca5627`, `SetOPDParam()` `0x43ca56a5`). **Cruce con el sombreado**: `SHD::GetShdMode` `0x438ef40e` con `cmp r3,#0x44` + `tbb [pc,r3]` y tabla de 69 bytes en `0x438ef418` → 14 ShdMode (S66). Modos nombrados: `SDF_RECMODE_STILL_REC` `0x43c7effb`, `REQ_MOVIE_REC` `0x43ca13be`, `REPLY_MOVIE_REC` `0x43ca15b6`, `BURST_CNT` `0x43cb4bfe`, `Burst_` `0x43ccaf9b`, `MSG_ID_SDF_PANORAMA_CCNR_ENCODE` `0x43c781e4`, `ApiPanoramaCcnrEncode.cpp` `0x43c79fd2`, `ModulePanoramaCcnrEncode.cpp` `0x43c7b926`, `PanoramaSweepStart` `0x43cab054`, `still_cnt_panoramaSweep.cpp` `0x43cab088`, `lc_BracketAF.cpp` `0x43ca79ba`, `[SDF] interval(PTM) %ld` `0x43c7a1a5`. Nota `analysis/s96_modes/capture_modes.md`, test `tests/test_s96_modes.py` 7/7.
- Abierto: la tabla de 69 `drive_mode` con nombre (no está en el blob); rango de `CapMode`/`ContID`; cálculo de `BDROSeq`; equivalencia `drive_mode` ↔ `CapMode`.

## S97 — sincronización audio/vídeo del codificador (21-10-2026, línea general)
- Hecho: integración del hito de sincronización del codificador (subagente `nemotron-3.5-lightning-free`) **con revisión y corrección de direcciones**. Contenido verificado: `[ENCMODEMGR]` 21 trazas `0x43c4ac73` (`15McAvcEncModeMgr` `0x43c431fb`) con la secuencia de comandos `RecordCodecIfCmd: CmdCode/CmdTime/ExecTime/CurrentRefTime` y 14 `CMD_ID_*` (`ACT_ENC` `0x43c4b0xx`, `GET_REF_TIMER`, `INIT_ES_API_PARAM`, `INACT_CHIP`, `ALLOC_USER_DATA_AREA`, `BEGIN_ENC`, `SET_SEQ_PARAM`, `TERM_ENC`, `STILL_ENC`, `APPLY_USER_DATA_GOP`, `APPLY_USER_DATA_PIC`, `MUTE_AUDIO_CAPTURE`, `INIT_RC_BUFFER`, `SET_RC_WTPT`, `SET_ENC_READ_POINTER`) y métodos `ProcVsyncPre/ProcVsyncPost/ProcMsg(MSG_MC_AVC_ENC*)/EnqueueCodecIfCmd`; `[ENCAUDOUCR]` 9 trazas `0x43c4b444` (`IsOuCrank/Sampling/FrameRate/ImagingRate`, `TermEnc(vfc24/vfc32/cnt): NormalTerm/OuCrankTerm/GopNum`, `Begin Enc: StartAdr/BuffAdr/BuffSize`, `AUGI(AVCODEC-AVSC) OverFlowFile:%s`, `WriteAugi : AUGI FLAG END`, `[AUDIO INFO] Pts = 0x%08x EndFlug = 0x%02x, Num Au = %x`); `[ENCAUDSYNC]` 17 `0x43c526d3` (`McSyncEncStart::SetEncStartTimeForThumbnail`, `MC[%d] comes later/earlier`); `[ENCOUCUDMG]` 7 `0x43c522fb`; `[VIDENCCTRL]` 13 `0x43cd6070` (22 × `MSGID_AVC_ENC_VIDEO_*`); más `[VIDENCSTAT]` 70 y `[ENCOUCSTAT]` 49. Informe `analysis/s97_encsync/encoder_sync.md` + JSON, test `tests/test_s97_encsync.py` 12/12.
- **Correcciones de la revisión:** (a) el borrador usaba **offsets de fichero** (`0x70a444`…) → convertidos a direcciones del binario (`0x43c4b444`, `0x43c4ac73`, `0x43c431fb`, `0x43c522fb`); (b) es **falso** que estos módulos sean exclusivos de la A6000: la A7S fw3.20 tiene los mismos módulos con los mismos recuentos (`ENCMODEMGR` 21, `ENCAUDSYNC` 17, `ENCAUDOUCR` 9, `ENCOUCUDMG` 7, `VIDENCCTRL` 13, `VIDENCSTAT` 70) y los mismos símbolos (`McAvcEncModeMgr` 6, `SetEncStartTimeForThumbnail` 1, `MSGID_AVC_ENC_VIDEO` 22); la única diferencia es que la A7S tiene **5 trazas más** en `[ENCOUCSTAT]` (54 vs 49).
- Abierto: el formato de los mensajes `MSG_MC_AVC_ENC*`; el formato del bloque AUGI en la tarjeta; cómo se eligen los parámetros de sincronización.

## Catálogo de la línea general (21-10-2026)
- Nuevo documento `docs/capture/linea-general-re.md`: índice navegable de los **27 hitos** de
  ingeniería inversa general (S66–S97) con su tema, su hallazgo central, el enlace a su informe en
  `analysis/` y a su test en `tests/`, más una nota sobre cómo se sostiene el rigor (separación
  VERIFICADO/INFERENCIA/NO_VERIFICADO, test de bytes por hito y re-verificación de los entregables
  de subagentes). Enlazado desde el `README.md` raíz.

## S99 — la arquitectura del userland: las capas de libObj.so (21-10-2026, línea general)
- Hecho: mapa por namespaces de la mayor biblioteca del userland. `libObj.so` 17 436 172 B (A7S 16 184 848 B) con **2507 símbolos mangled en 167 namespaces** (A7S: 2538 en 168) → el userland de la A6000 es esencialmente el mismo que el de la A7S. Capas: `MprIf` 318 (medios), `MWF` 241 (`ObjMsgList`/`ObjMsg`/`ObjMsgEntry`/`RsrcAcsr`), `ux` 227 (`GraphicsImage`, `GraphicsSystem::setOSDGainParam`, `TextLayout::registerFontFaceFile`), `AVBIZ` 138 (`AVBIZ::UNIVERSE::UActiveObject` con `onStarting`/`onStopping`/`SendMsgToApp`/`eventProcessing`, `UBbSuspend`/`UBbResume`, `SelectorProxy`, `ULog_u16x5`/`ULog_u8x10`), `OBJAVBBCBASECLASS` 128, `MprCtrl` 58, `ViewBase` 53, `LayoutableWidgetBase` 45, `GEN_GridList` 45, `C_DataflowInfra_Entry_ImageSizeInfo` 44, `InputService` 36, `UFW` 34 (`DfsWrapper`, `MsgReceiver::RcvMsg/PostMsg`, `RsrcWrapper::AcquireSingle/ReleaseAll`), `GEN_Calendar` 34, `GEN_Button` 29, `AppWidgetBase` 27, `NetCommonLibrary_` 25 (A7S 35), `GCM_` 24, `GEN_Label` 24, `CmnViewMenuData` 23, `SequenceBase` 23, `DefRootView` 22, `GEN_Balloon` 22, `ObjAvbbcCmn` 22, `NetContUtil` 20, `HighlightManager` 19, `GlobalAccessor` 18, `ScalarView` 17. Nota `analysis/s99_userland/userland_architecture.md`, test `tests/test_s99_userland.py` 6/6.
- Abierto: qué separa `MprIf` de `MprCtrl` y `MWF` de `UFW`; los 167 namespaces completos; cómo se registran las apps del `UNIVERSE`.

## S98 — libBizFw.so: el orquestador userland y el puente con el ADF (21-10-2026, línea general)
- Hecho: integración del hito del orquestador de servicios (subagente `nemotron-3.5-lightning-free`) **verificado por muestreo y con una corrección**: `libBizFw.so` 332 600 B; tres colas OSAL (`OSAL_MSGQ_GID_DETECT_FACE`, `OSAL_MSGQ_GID_DMM_CTRL`, `OSAL_MSGQ_GID_SADRIVER`); **9 `CATEID_*`** (`PIN`, `RENDERER`, `DISPLAY`, `SYSTEMSOUND`, `AUDIOPROCESSOR`, `MIC`, `MIXER`, `SPEAKER`, `EFFECT`); **1 `MSG_ID_*`** (`MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL`); **11 `REQ_*`** (`DEPOSITE`, `DEPOSIT_MULTIE`, `DESTRUCTE`, `INQUIREE`, `OVERWRITEE`, `PARSEE`, `PEEKE`, `POKEE`, `RAW_PARSEE`, `SHAREE`, `WITHDRAWE`); clase de estado `StmCh`; y el puente `OBJAVBBCBASECLASS::AdfCh` con métodos `PrcSetPath`, `SysRequest`, `SysSetPath`, `SysSetTable`, `InSetInput`, `InSetIVoice`, `InSetLowCut`, `InSetWindNr`, `PrcSetFader`, `OutSetOutput`, `OutSetSpSwap`, `OutSetVolume` → **mismo vocabulario de prefijos que los comandos DBGCMD del ADF del firmware (S81) = el contrato userland↔firmware**. Destinos de los mensajes: `ADF`, `DETECT`, `DMM`, `HAPI`, `HDMI`, `SA`, `SDF`, `SDI`, `VDF`, `VEF`. En el firmware: **125 nombres RTTI `NS_SCALAR_INFRA*`** (p. ej. `N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE` `0x43ce59d2`, `…23ScalarInfraSequenceIdleE` `0x43ce5c4d`, `…26ScalarInfraSequenceStageIfE` `0x43ce5c7a`). Vocabulario idéntico en la A7S fw3.20. Informe `analysis/s98_bizfw/bizfw_bridge.md` + JSON, test `tests/test_s98_bizfw.py` 9/9.
- **Corrección de la revisión:** las trazas `PrcSetPath to ADF` / `Snd Msg to ADF` **no están en `av-cam.bin`** (0 hits) sino en `libBizFw.so` → es el userland quien envía al ADF (el subagente las atribuía al firmware).
- Abierto: el formato binario de los mensajes ADF; qué distingue `SA` de `SADRIVER`; el mapeo de `MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL` al visor.

## S100 — el contrato de comandos del ADF ↔ AdfCh (21-10-2026, línea general)
- Hecho: catálogo completo de la interfaz de control userland↔firmware. Firmware: **90 comandos `[ADF][DBGCMD]`** por familias (`Input` 16, `InputPro` 8, `Output` 9, `OutputPro` 3, `System` 12, `SystemSound` 7, `Proc` 19, `SoundAnalyzer` 4, `CPU2` 4). Userland: clase `OBJAVBBCBASECLASS::AdfCh` con **35 métodos** (`Prc` 8, `Sys` 4, `In` 8, `InPro` 7, `Out` 8) y correspondencia **uno a uno** con los comandos del firmware (`PrcSetPath`↔`Proc SetPath`, `SysSetTable`↔`SystemSound SetTable`, `InSetInput`↔`Input SetInput`, `InProSetAgcLink`↔`InputPro SetAgcLink`, `OutSetOutput`↔`Output SetOutput`, `OutProSetHpMonitor`↔`OutputPro SetHpMonitor`). Excepciones: solo-userland `PrcSetPeakDetect`, `PrcSetAudioOutpinMute`, `OutSetVolume`, `SysSetVolume`; solo-firmware `InputPro SetManualGainLink`. Nota `analysis/s100_adf_contract/adf_command_contract.md`, test `tests/test_s100_adf_contract.py` 7/7.
- Abierto: el formato binario de los comandos y su equivalencia con las 11 `REQ_*` (S98); el submódulo `Prc`; `PrcSetPeakDetect`.

## S109 — el módulo `[CDIAG]` (270 trazas): el banco de diagnóstico del códec (21-10-2026, línea general)
- Hecho: integración del hito del subagente **con revisión**. 270 tokens `[CDIAG]` (`0x43c3b0d4`–`0x43c3e86a`): 255 con prefijo `[CDIAG]` y 15 `[ERR][CDIAG]`; **7 escenarios** (HD REC/DEC, SD REC/DEC, JPEG ENC/DEC/ENCDEC) × **8 operaciones** (`DbgDiagAvc` `0x43c3b6df`, `CmpData` `0x43c3b72a`, `RunCodec` `0x43c3c123`, `RelMemArea` `0x43c3b768`, `SetMemArea` `0x43c3b7ec`, `SetData` `0x43c3c162`, `ConfirmDoneCodec`, `SetDiagMode` `0x43c3bf5c`); **27 firmas `CDIAGER`**, **16 clases** (RTTI) y 2 ficheros (`cdCtrlIf.cpp` `0x43c3b1a8`, `cdCtrlCore.cpp` `0x43c3b86c`); **tabla de registro de clases** `0x43fda6a0` (16 pares `{vtable base común, nombre}`; en la A7S `0x43fdb6ec`); 118 funciones (`0x435a127a`–`0x435a50b6`), 295 sitios, 226/255 cadenas referenciadas y 29 muertas; transporte **OSAL** (`osal_rcv_msg` `0x43561260`, `osal_snd_msg` `0x4356120c`) con el núcleo de la tarea en `0x435a1318` → `0x435a9f4c`; escritor `0x435ab880` (310 llamadas), nivel `0xbe`, id `0xbad`. **Diferencial A7S fw3.20**: 270/270 cadenas comunes, 0 exclusivas → módulo idéntico; el A6300 añade 40 de 4K. Informe `analysis/s109_cdiag/cdiag.md` + JSON, doc en `docs/capture/s109-cdiag.md`, test `tests/test_s109_cdiag.py` 22/22.
- **Corrección de la revisión (agente principal)**: el informe daba la tabla de `0x43fda6a0` como "16 pares {vptr, nombre}" pero|下载 that the first word is the **same value** (`0x43fd04f8`) in all 16 pairs → no es una tabla de vtables por clase sino una tabla de **resolución clase→nombre** con puntero base compartido.
- Abierto: formato de `MSG_SENS_COMMAND`/`DIAGINFO`; codificación de `cmd`/`mode`/`func`; emisor de los `SENS_*`; fichero fuente de las clases de códec (no embebido).

## S116 — el módulo `[SFRS]` (117 trazas) de control por *pins* (21-10-2026, línea general)
- Hecho: integración del hito del subagente (reintento con deepseek tras el `rate limit` de nemotron) **con revisión**. 117 cadenas `[SFRS]` `0x43ce7661`–`0x43ceb8c4`; **131 puntos de emisión PIC** y **52 funciones** todas en `0x439a0000`–`0x439c0000`; 0 cadenas sin referencia; sub-bloques SUPERSTABLEMOVIE 37, MOTIONSHOTVIDEO 25, EFFECTMOVIEREC 23, PINSEND 12, SET_PATH_STATUS 9, SA 6, RC_AIC_TRIGGER 3, MULTIPLEXTRIGGER 2. Evidencia: `SETPIN` `cmp r1,#1` `0x439aada4`, `GETPIN` `0x439aae3c` (línea 56), cola `EXECUTE_PIN_SEND` `0x439b1f4c`–`0x439b1f6c` (lee `[r4,#0x3f4..0x3ff]`, escribe `[r4,#0x410]=1`, `[r4,#0x40c]`, traza `0x43ceb80d`). **Diferencial A7S fw3.20**: 151 cadenas en la A7S, **117 comunes, 0 solo-A6000 y 34 solo-A7S** → el módulo de la A6000 es un subconjunto. Informe `analysis/s116_sfrs/sfrs.md` + JSON, doc en `docs/capture/s116-sfrs.md`, test `tests/test_s116_sfrs.py` 23/23.
- **Acierto del subagente**: detectó y corrigió tres expectativas erróneas de sus propios tests (nº de sitios `add`, el PC que se suma en el esquema PIC —el del `add`, no el del `ldr`— y el formato `0x%08x` en la normalización).
- Abierto: significado de SFRS/AIC/RC/VFX/IIB/PINSEND; tabla de líneas de los `.cpp`; semántica de los tres modos de grabación.

## S117 — `[AUGI]`: la cabecera de 32 B del códec (21-10-2026, línea general)
- Hecho: 75 apariciones de `[AUGI]` → **26 cadenas** con el prefijo y **49** con `[CodecIF][AUGI]…`; dos clusters (impresores de estructura `0x43c6a909`–`0x43c6b517` y volcado `[AUGI] campo = %d` `0x43cd993d`–`0x43cd9c8d`); **AUGI es el nombre de una cabecera de bloque de códec**, con los conversores `DecExAugiConverter` `0x43c6a8db`, `DecInAudioAugiConverter` `0x43c6acc5`, `DecInVideoAugiConverter` `0x43c6b02e`, `EncExAugiConverter` `0x43c6b554` y la API `StrmEngEncCIIf::CodecEventCreateVAUGI` `0x43c66fbf`; 86 puntos de emisión, 0 cadenas sin referencia, comprobación aritmética 86 = 75 + 2 + 9. **A7S fw3.20: idéntico** (mismas 75 apariciones y 26 cadenas). Informe `analysis/s117_augi/augi.md` + JSON, doc en `docs/capture/s117-augi.md`, test `tests/test_s117_augi.py` 27/27.
- Abierto: qué cuenta `length`; layout binario de la cabecera; emisor de `CodecEventCreateVAUGI`; la sigla AUGI no está expandida en ningún byte.

## S118 — el módulo `[SFRA]` (100 trazas) de la infraestructura escalar (21-10-2026, línea general)
- Hecho: 100 trazas `[SFRA]` `0x43ce5a16`–`0x43ce7723`, 11 sub-bloques, 11 ficheros fuente (`ScalarInfraAsyncMain.cpp`, `SfrJpegBuffer.h`, 7× `ScalarInfraSequence*.cpp`, `SfrYc.cpp`, `DrvCallRc.cpp`), 47 funciones; `SFR` = `NS_SCALAR_INFRA` verificado por los nombres de clase C++; **17 comandos con ids decodificados de los bytes** (`0x0100`/`0x10` GET_INFO, `/0x20` GET_JPEG, `/0x22` SET_JPEG_PARAM, `/0x30` GET_SA_RESULT, `/0x32` SET_SA_NOTIFY, `/0x42` LiveView SET_JPEG, `0x8110` SET_PATH(CLOSE), `0x8120` SET_PATH(OPEN), `0x9010` GET_INFO_CMP); despachador de finalizaciones `0x439a1640` con `TBB` de 5 bytes `0x439a1654`; núcleo `ScalarInfraAsyncMain` `0x439a1864`. **A7S fw3.20: 100/100 mensajes idénticos** y en el mismo orden (el subagente corrigió la premisa del encargo, que asumía que la A7S no tenía el prefijo); el A6300 añade 8 con nomenclatura antigua. Informe `analysis/s118_sfra/sfra.md` + JSON, doc en `docs/capture/s118-sfra.md`, test `tests/test_s118_sfra.py` 22/22.
- **Hallazgo metodológico (arrastrado a S106/S110):** la regla PIC "ancha" produce falsos positivos (186 pares en `[SFRA]` frente a 118 verificados a mano) por reutilización del registro → se añadió el escáner canónico `scan_pic_refs_v2.py` con kill analysis y la nota `analysis/s106_imaging_cap/pic_xref_methodology.md`, y se rectificaron los recuentos de S106, S110, S112, S113 y S115.
- Abierto: correspondencia de los 5 casos del `TBB` con los nombres `[CMP]`; 5 ids de sub-comando sin traza propia; papel de `RC`/`VFX`/`IIB`.

## S124 — el bloque de parámetros de exposición/lectura por `drive_mode` (imager) (21-10-2026, línea general)
- Hecho: origen de cada campo de la traza `SetExps` (`0x43c93cc2`), leída de `FUN_436d6f70` (sitios PIC `0x436d7242`/`0x436d7280`): `PrevDrv`/`NowDrv`/`NextDrv` = u16 en [r1+4]/[r1+0]/[r1+6] y **`shut` = byte [r1+9]**; `svd`/`shd`/`spl` = u32 del contexto en +0x178/+0x174/+0x170 (`0x436d725c`/`0x436d726a`/`0x436d7274`). **Diferencial A6000/A7S**: el conjunto de parámetros (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`, `epdsel`) es **el mismo** (5 trazas de `[CAMERA_MAIN_SYNC]` idénticas texto a texto); la fw3.21 reescribe la instrumentación (`SetExps`/`SetRead`/`Execute` con drive mode anterior frente a `Exposure.`/`Change ImagerMode.` de la A7S), cambia el layout del contexto (`+0x13c` → `+0xfc`), añade `[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d` `0x43ca7836` y retira `b8_shutter_limit` `0x43c9f01c`. **Para el obturador**: `shut` es el índice/contador de obturación (junto a `shutter mute on/off` `0x43c8253b`, `shutCycleCount`, `uc_shut_idx_num`), **no** un selector de mecanismo → **sin efecto en S51**. Informe `analysis/s124_exposure_params/exposure_params.md` + `result.json`, doc en `docs/capture/s124-exposure-params.md`, test `tests/test_s124_exposure_params.py` 7/7.
- Abierto: la tabla de valores por `drive_mode` (sin ella no puede afirmarse que ningún modo difiera entre A6000 y A7S); `sint` y `gs`; si `zaf_now_shut_cycle` cuenta obturaciones mecánicas o electrónicas.

## S120 — `[IDT_OPD]`: la segunda instancia del módulo IDT (21-10-2026, línea general)
- Hecho: 274 apariciones del token `[IDT_OPD]` (273 cadenas que empiezan por él, 274 textos distintos) `0x43cf11f9`–`0x43cf5810`, con **274 gemelos `[IDT]` contiguos** byte a byte → el etiquetado es la única diferencia. **`IDT_OPD` no es una sigla inventada**: es un recurso del `SyncResMgr` (`RESOURCE_IDT_OPD` `0x43c9c461`, offset `0x761b67` en la A7S) y comandos (`IDT_OPD_TOP_Sync_OPDAcquire` `0x43c9c2fc`, `IDT_OPD_TOP_Sync_SetFOPD`); la fw3.21 de la A6000 es la única de las tres que etiqueta así. 165 funciones (`0x439dde84`–`0x439fcf9c`), 271/274 cadenas con referencia (3 muertas: `0x43cf150f`, `0x43cf1557`, `0x43cf274a`); bloques IE `0x439e80c8` (19 campos) y MAP `0x439ee7e8` (18 campos) verificados, 18 punteros de volcado. **Diferencial**: 0 trazas `[IDT_OPD]` en A7S (306 `[IDT]`) y A6300 (382); 270/274 mensajes comunes, 4 solo-A6000, 36 solo-A7S. Informe `analysis/s120_idt_opd/idt_opd.md` + JSON, doc en `docs/capture/s120-idt-opd.md`, test `tests/test_s120_idt_opd.py` 97/97.
- **Corrección de herramienta (agente principal)**: la kill analysis de `scan_pic_refs_v2.py` estaba **inerta** (`md.detail` apagado → `ins.operands` lanzaba CsError; además `op.reg & 0xF` confunde r1 con r3). Corregida: coincide con la regla estricta en el conjunto de cadenas y en los sitios verificados a mano.
- Abierto: qué distingue la instancia OPD de la IDT normal; layout del bloque LC y del array `waku`; tamaño de cada mapa; `tar_num`, `isSpectRef`, `msain0/1`, `msaout`, `kido_th`, `sel_hist/sel_sum`.

## S126 — `[CAMERA_MAIN]`: el módulo raíz de la cámara (21-10-2026, línea general)
- Hecho: 135 trazas `[CAMERA_MAIN]` `0x43c9c57b`–`0x43ccae46`, **48 funciones** emisoras y **148 ficheros fuente** embebidos en la zona; es la capa de coordinación (AF/calibración, seguimiento `waku`, keymap, carga de parámetros): `calibration_fc_pos` `0x43c9c57b`, `Calibration start` `0x43c9c6d5`, `Scanless NG because of Face AF` `0x43c9cd3f`, `waku area is %d` `0x43c9d53f`, `keymap size is under 0` `0x438d16b0`, `LoadNum %x, Ch %x` `0x4378a68c` (51 trazas); puente con el ZPD (S75) en `NOT_DETECT from ZPD MODULE … lc_HybridAF.cpp` `0x43c9d07e`. Ficheros: `CamResource.cpp`, `CamSyncResource.cpp`, `SyncTask.cpp`, `ClockControl.cpp`, `init_cam_SetCamParam_main.cpp`, `ImagingMain.cpp`, `lc_AF_Scan.cpp`… **Diferencial**: la etiqueta es nueva en fw3.21 (A7S 0 trazas / 92 mensajes sin etiqueta; A6300 0 / 121). Informe `analysis/s126_camera_main/camera_main.md` + JSON, doc en `docs/capture/s126-camera-main.md`, test `tests/test_s126_camera_main.py` 7/7.
- Abierto: subdivisión de los 82 mensajes sin etiqueta; fichero fuente por función; `waku`, `ympc`, `csum`, `cpeak`, `LoadNum`/`Ch`.

## S122 — el módulo `[CAMERA_MAIN_TC]` (127 trazas) de tiempo y giroscopio (21-10-2026, línea general)
- Hecho: 127 tokens `[CAMERA_MAIN_TC]` en 6 tramos `0x43ca7fd7`–`0x43ccb350`; 123 vivas / 4 muertas; 256 sitios PIC en 41 funciones (estricta); reparto GYRO/CALIB 32, DIST 13, APL/ApolloSA 47, SMART ZOOM 16, DDT 18; **17 publicadores** uniformes (prólogo `push {r3}` + `osal_try_valloc_msg` `0x435612d0`); despachador **`ApolloSA_Main` `0x438730b0`** (`tbb` de 9 casos en `0x4387333e`, `tbh` en `0x4387348e`) desde el que salen los **6 clientes de `[APL]`** (S119); llamadores: panorámica (`bl` en `0x437f1324`, `cmp r7,#2` en `0x437f12f6`) y `0x438bdeac`. **Diferencial**: 0 apariciones del token en A7S y A6300 con 126/127 textos literales y 123 sitios. **Sin efecto en S51** (0 menciones de shut/silent/electro/mech/sensor/exposure/drive/readout…). Informe `analysis/s122_camera_main_tc/camera_main_tc.md` + JSON, doc en `docs/capture/s122-camera-main-tc.md`, test `tests/test_s122_camera_main_tc.py` 40/40.
- Abierto: sitios perdidos en A7S/A6300 (idx 2, 32, 108); llamadas por puntero a `0x438786c4`/`0x43879204`/`0x438792dc`/`0x4387938e`; significado de TC/DDT/DIST/ARC/Gmv/Lmv; pipeline de calibración/DIST/DDT/SMART ZOOM.

## S128 — el mapa de etiquetado de la fw3.21 (21-10-2026, línea general)
- Hecho: comparación texto a texto de los **98 prefijos** con ≥ 8 cadenas entre A6000 fw3.21 y A7S fw3.20: **58 IGUAL**, **18 RENOMBRADO** (la A7S no usa el prefijo pero los textos coinciden: `[CAMERA_MAIN_YC]` 958/968, `[IMAGING_CAP]` 678/697, `[CAMERA_MAIN_SYNC]` 412/428, `[CAMERA_SA]` 228/231, `[CAMERA_MAIN]` 97/134, `[CAMERA_MAIN_TC]` 122/125, `[IMAGING]` 115/120, `[MOUNT_ERROR]` 78/80), 2 PARCIAL (`[CAM_IMAGER]` 179/371) y 20 NUEVO/PROPIO. **Conclusión**: la fw3.21 de la A6000 **reescribe el logging, no el firmware**. Informe `analysis/s128_label_map/label_map.md` + `label_map.json`, doc en `docs/capture/s128-label-map.md`, test `tests/test_s128_label_map.py` 6/6.
- Abierto: comprobar uno por uno los 20 "NUEVO/PROPIO".

## S123 — el módulo `[CAMERA_MAIN_CC]` (49 trazas) de control de captura (21-10-2026, línea general)
- Hecho: 49 tokens `[CAMERA_MAIN_CC]` en 6 tramos de `.rodata` (control 21, LUT 12, IE 8, miniRaw 2, MakerNote 2, CamCore-3DLUT 4); 47/49 referenciadas (estricta) en 29 funciones; 2 huérfanas con par ancho demostrado como falso positivo (`GetKDZMode()` `0x43ca5bb7`, `SetMovDevelopParam()` `0x43ca5d31`). **Máquina de estados de 10 etapas** (`ExtractCaptureData`→`CaptureInit`→`SetReadImageParam`→`SetNRParam`→`SetOPDParam`→`AfterOPDAfterNR`→`SetDevelopParam`→`SetDualRecParam`→`SetDevDetectDevelopParam`→`WriteExifMakernote`), estado en `obj+0xb` y sub-paso en `obj+0xa`. **Identidad de captura**: `CapMode`@`0x1c0`, `ExposureID`@`0x1b8`, `ContID`@`0x1bc`, `BDROSeq`@`0x6ec`, `BDRObase`@`0x6f4`, `FrameID`@`0x701`. Clase `CC` (nombres verificados: `CcEncryptedTagData` `0x43ca9242`, `ImageParam_Capture` `0x43ca9802`; `0x43ff8ee4`/`0x43ff8f24` son tablas de vptrs). Grafo entrante: 37 llamadas desde 22 funciones (`Stage_SACC.cpp`, `Stage_OPD.cpp`, `Stage_MARBLE.cpp`, `Stage_Orientation.cpp`, `CaptureUtilityModuleAPI.cpp`), 0 llamadas directas a `[CAM_DMM]`/`[CAM_IMAGER]`/`[CAMERA_MAIN_YC]` → enlace por tabla de parámetros compartida `0x43ae9226` (ids `0x9408`/`0x9409`/`0x9410`). **Diferencial**: 0 cadenas con prefijo en A7S y A6300 (no tienen familia `[CAMERA_MAIN_*]`), 47/49 mensajes idénticos sin etiqueta. Informe `analysis/s123_camera_main_cc/camera_main_cc.md` + JSON, doc en `docs/capture/s123-camera-main-cc.md`, test `tests/test_s123_camera_main_cc.py` 32/32.
- Abierto: fichero fuente de la clase `CC`; significado de la sigla; rangos de `CapMode`/`ContID`/`BDROSeq`/`FrameID`; `drive_mode`↔`CapMode`; flujo de la LUT 3D.

## S130 — los 20 módulos "nuevos" del mapa de etiquetado (21-10-2026, línea general)
- Hecho: buscando el **núcleo** de cada mensaje en la A7S fw3.20 y el A6300 fw2.01, de los 20 módulos `NUEVO/PROPIO` de S128 solo **2 son cambio de etiqueta** (`[IDT_OPD]` 270/273 → `[IDT]`; `[DFE]` 11/11), **1 parcial** (`[JPEG]` 4/17) y **17 con contenido ausente en los otros dos firmwares** (`[MOUNT_DEBUG]` 2/132, `[CAMERA_MAIN_LC]` 1/72, `[SAD]` 3/44, `[TP_R]` 2/18, `[ILLUMI]` 1/34; `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]`, `[CAMERA_IS]`, `[DEPTH]`, `[JOG]`, `[ADC_DEBUG]`, `[LIF_DEBUG]`, `[PANDA]`, `[CAMERA_MAIN_FC]` con 0). Tokens `ACCY`/`VPH_API`/`CLK_CTRL`/`CAMERA_MAIN_LC`/`MOUNT_DEBUG`/`ILLUMI`/`PANDA`: 0 apariciones en A7S y A6300. **Línea del obturador**: `[VPH_API]` trae API **nueva** de silenciador (`<shutter_mute_param>` `0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc`; 0 en A7S/A6300) mientras la traza `shutter mute on/off` (S118) está en los tres → se añade el **parámetro de API**, no el mecanismo (silenciador mecánico). **Advertencia**: la comparación mezcla versión y modelo (no hay fw anterior de la A6000 en el repo). Informe `analysis/s130_new_modules/new_modules.md` + JSON, doc en `docs/capture/s130-new-modules.md`, test `tests/test_s130_new_modules.py` 7/7.
- Abierto: qué son `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[DEPTH]`, `[PANDA]`; quién consume la API nueva de silenciador.

## S127 — el módulo `[CAMERA_MAIN_LC]` (72 trazas): AF, ZPD y DM AF (21-10-2026, línea general)
- Hecho: 72 cadenas `[CAMERA_MAIN_LC]` `0x43c9c6f6`–`0x43ca7e0b`, 78 sitios PIC (estricta) en 37 funciones, 1 cadena muerta `0x43c9c779`, 13 sub-bloques (reparto 32/40). **Corrección de premisa**: el módulo **no calibra la lente** sino que es la capa de **AF + ZPD + DM AF** (`Camera::LC` por RTTI, sigla sin desarrollar). Puente con el ZPD (S75): `LC_GetZpdResultInfo` (cadena `0x43ca78c8`, función `0x437c1e48`), gate `ldrb.w [rX,#0xc0]`+`tst.w #2`, 10 lecturas de campo y 10 trazas. **Diferencial**: 0 prefijos y 0/72 mensajes coincidentes en A7S/A6300 → propio de la A6000 fw3.21. Sin efecto en S51. Informe `analysis/s127_camera_main_lc/camera_main_lc.md` + JSON, doc en `docs/capture/s127-camera-main-lc.md`, test `tests/test_s127_camera_main_lc.py` 22/22.
- Abierto: layout completo del resultado ZPD; qué consume `LC_GetZpdResultInfo`; significado de `lc_Movie_DM_AF_Util_*`.

## S131 — `[VPH_API]`: la API de parámetros del subsistema VPH (21-10-2026, línea general)
- Hecho: 106 trazas `[VPH_API]` contiguas `0x43ce32e7`–`0x43ce3dfc` con sintaxis de API explícita: 49 entradas `<nombre>`, 42 `_sub`, 11 salidas `>nombre<`, 4 `=x=` → **60 familias**; emitidas por **48 manejadores** (uno por parámetro) en `0x4395aab8`–`0x4395b5f4` (39) y `0x4395e1b8`–`0x4395e34c` (9). **Línea del obturador**: API del **silenciador** (`<shutter_mute_param>` `0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc`), **nueva en fw3.21** (0 apariciones en A7S/A6300) mientras la traza `shutter mute on/off` (S118) está en los tres → se añade el **parámetro de API**, no el mecanismo (obturador mecánico). **Diferencial**: 0 trazas `[VPH_API]` y 24 apariciones de `VPH` en A7S/A6300 frente a 106 y 134 en la A6000 fw3.21. Sin efecto en S51. Informe `analysis/s131_vph_api/vph_api.md` + JSON, doc en `docs/capture/s131-vph-api.md`, test `tests/test_s131_vph_api.py` 7/7.
- Abierto: referencia de la tabla de manejadores y quién la invoca; `laxo`, `diceic_arb`, `line_fchr`, `set_eomainsub_inverse`; qué hace `shutter_mute_param` y quién lo consume.

## S129 — el módulo `[CAMERA_MAIN_IM]` (42 trazas) de control térmico (21-10-2026, línea general)
- Hecho: 42 cadenas `[CAMERA_MAIN_IM]:` (40 contiguas `0x43ca6b32`–`0x43ca71e7` + 2 sueltas), 43 sitios PIC (estricta) en 10 funciones, 0 sin referencia, 1 con doble referencia (`0x43ca70f6` desde `0x437b90fe` y `0x437b9268`). **Despachador** `0x437b8384` (id u16 de `[ctx+0x10]` → 24 pares en `0x43befc32`; defecto `0xa00`; `0xa20`→`0x437b9064`, `0xa21`→`0x437b915c`). Enlaces con S115 (`0x437b877a bl 0x436d6118`, `0x437b8780 bl 0x436d648c`, `vldr s14` ×100.0f) y con S124 (`ldrb` +6/+4 en `0x437b87f6`/`0x437b87fe`, intervalos `×0x186a0`). **Negativo verificado**: el módulo **no expone el obturador** (las únicas `shut` son la subcadena de `shutdownTh` `0x43ca6ca8`/`0x43ca6d3f`) → **sin efecto en S51**. **Diferencial**: 34/42 textos idénticos en A7S y 33/42 en A6300 → **renombrado**, no nuevo. Informe `analysis/s129_camera_main_im/camera_main_im.md` + JSON, doc en `docs/capture/s129-camera-main-im.md`, test `tests/test_s129_camera_main_im.py` 21/21.
- Abierto: invocación de `0x437b8774` (sin `bl` ni puntero); slot `0x6c` ↔ `GetImagerTemperature` (inferido); los 24 ids del despachador; helper `0x4378dd78`.

## S134 — la aritmética de los parámetros del imager (21-10-2026, línea general)
- Hecho: en la función validadora `0x4381106c` de `[CAMERA_MAIN_SYNC]`, la relación **`shut`→`svd` es aritmética**: `svd_esperado = (svd==9 ? 1 : shut) * svr_num − 1` (`svr_num` u8 en `[estado+0x14e]`) o `/ VdNum − 1` (`VdNum` u16 en `[estado+0xcc]`, si > 1), división sin signo en `0x4355faf0`. Desbordamiento → `Imager param error shut:%d, svr_num:%d, VdNum:%d` `0x43cb11d2` (`0x4381110e`) e `Imager svd error. shut:%d, svd:%d -> %d` `0x43cb1217` (`0x43811162`). Procedencia: `shd`=`[estado+0x24]`, `svd`=u16 bajo y `spl`=u16 alto de `[estado+0x28]` (**empaquetados**), `sint`=u8 de `[estado+0x2c]`, `gs`=**flag** (`svd==9`), `shut`=`[ctx+0x1f8]`; estado por singleton `0x4378f9b4` → global `0x43e99208`. **Descarta** la tabla por `drive_mode` de S124 (el bloque de modo sigue sin localizar). Sin efecto en S51. Informe `analysis/s134_imager_params/imager_params.md`, doc en `docs/capture/s134-imager-params.md`, test `tests/test_s134_imager_params.py` 8/8.
- Abierto: qué son `svr_num`/`VdNum` y quién los escribe; por qué `svd==9`; si la A7S usa la misma fórmula.

## S125 — `[IMAGING_REL]` y `[IMAGING]`: el liberador de recursos y el motor de panorama (21-10-2026, línea general)
- Hecho: **"REL" = RELease verificado en el RTTI** (`N6Camera11ReleaseLock9RelLockS1E` `0x43ca5489`). `[IMAGING_REL]`: 31 cadenas, 34 sitios, 26 funciones; gestor `RelMgr` `0x4379d114`–`0x4379e600` con despachador `REL_EVT` `0x4379d83a` (ids `0x01`–`0x27`) y `CapIdTblMgr`/`RelQueue`/`RelLock` `0x4381c30c`–`0x4381d150`; fichero `Spinal.cpp` `0x43c9c54f`; programa LIRO (S105); 1 cadena muerta `0x43c9c520` (también muerta en la A7S). `[IMAGING]`: 120 cadenas, **608 sitios en 346 funciones**; 3 genéricas (`FATAL! %s:%d` `0x43c9b487` con **443 sitios**, `FATAL! %s:%d [0x%x]` `0x43c9f6d9` con 29, `%s:%d \n` `0x43cabafb` con 1) y 117 del **motor panorama/stitch** (`still_cnt_panoramaSweep.cpp`, `still_seq_panoramaStitch.cpp`, `src/stitch/ddl_stitch.cpp`…); el motor de secciones de S114 no emite mensajes específicos. **Diferencial**: 0 etiquetas en A7S/A6300; `[IMAGING]` 115/120 comunes y 5 nuevas de fw3.21; `[IMAGING_REL]` 30/31 en A7S y 22/31 en A6300. Sin efecto en S51. Informe `analysis/s125_imaging_rel/imaging_rel.md` + JSON, doc en `docs/capture/s125-imaging-rel.md`, test `tests/test_s125_imaging_rel.py` 38/38.
- Abierto: `irp/cidx/rp/wp/wpd/dm` e `InnerRP`; ids de `REL_EVT`; por qué la fw3.21 etiqueta el `FATAL!` genérico.

## S135 — el subsistema `ElecShutter` del A6300 como control positivo (21-10-2026, línea general + obturador)
- Hecho: barrido literal de términos de obturador electrónico en los tres `av-cam.bin`. El **A6300 fw2.01 sí tiene** `ElecShutter/EC_ElecShutter_Main.cpp` `0x43dcfa41`, `EC_NonlinearElecShutter_MechShutterTable.cpp` `0x43dcfa65`, tabla de velocidades no lineales `0x43dcfa9e`, y los ajustes `SET Silent Shutter Type` `0x43dc4f43`, `[SilentShutterMode]` `0x43dc9a14`, `[shutterType]` `0x43dca61f`, `[front_eshutter]` `0x43dc821d`, `CheckSetSilentShutterMode` `0x43dca9ad`, `CheckSetShutterType` `0x43dcb09c`, `CheckSetFrontEshutter` `0x43dca84a`; la **A6000 fw3.21 y la A7S fw3.20 tienen 0** (la A7S solo el diagnóstico `SET Silent Shutter Type` `0x43ca4b6b`, ya documentado en `work/claude/a7s_silent_execution_trace.md`). **Ausencia selectiva**: la A6000 sí tiene el motor `EC` (`EC::EcTagData` `0x43ca91ce`, `api_EC_GetApolloLapNum` `0x43caa193`); sus 15 `shutter` son del **mecánico** (silenciador, disparo táctil). **Control positivo** que refuerza S51 (A/B/C = NO) y complementa a S101; la ausencia estática no demuestra incapacidad del hardware. Informe `analysis/s135_elec_shutter/elec_shutter_scan.md` + JSON, doc en `docs/capture/s135-elec-shutter.md`, test `tests/test_s135_elec_shutter.py` 25/25.
- Abierto: ejecución real del módulo `ElecShutter` del A6300; relación con la política EFCS de la A6000 en `libObj.so` (E012); fw anteriores de la A6000.

## S133 — el módulo `[MOUNT_DEBUG]` (132 trazas) de diagnóstico de la montura (21-10-2026, línea general)
- Hecho: 132 cadenas `[MOUNT_DEBUG]` `0x43c9648d`–`0x43c9a10f`, 148 sitios PIC (estricta) en 65 funciones, 9 sinks; con `[MOUNT_ERROR]` 80, `[MOUNT_INFO]` 6 y `[MOUNT_WARNING]` 5 son **223 trazas `[MOUNT_*]`**, **inexistentes** en A7S y A6300 (0/132 mensajes coincidentes). El mecanismo de captura (`/mnt/Mount_ms_log_%03d.dat`) y Eclipse son preexistentes en las tres cámaras → lo nuevo es la instrumentación. Ninguna traza menciona obturador/sensor/apertura → sin efecto en S51. Informe `analysis/s133_mount_debug/mount_debug.md` + JSON, doc en `docs/capture/s133-mount-debug.md`, test `tests/test_s133_mount_debug.py` 42/42.
- Abierto: atribución de los puentes `0x4377e0e8`/`0x437d24c8`; consumidor de `osal_snd_msg`; semántica de `CS_*`/`PowerSeq`.

## S137 — `[CTRLCORE]`: la sub-etiqueta del núcleo de control de códec (21-10-2026, línea general)
- Hecho: 55 cadenas con el token `[CTRLCORE]` `0x43c3b82d`–`0x43cdb492`, 74 sitios PIC (estricta) en 16 funciones, **74/74 verificados de forma independiente** (`verify_sites.py`). **Corrección de premisa**: es una **sub-etiqueta de segundo nivel** (como `[APL]` dentro de `[CAMERA_SA]`): `[CDIAG][CTRLCORE]` 51 (`CdCtrlCore`), `[MCSENS][CTRLCORE]` 1, `[AMSENS][CTRLCORE]` 3; capas `CdCtrlIf`/`*CtrlCore` con `ExecCmd` `0x435a1424`, `ExecSensCmd` `0x435a15e8`, `ExecSensComp` `0x435a17e8`; ficheros `cdCtrlCore.cpp` `0x43c3b86c`, `mcSensCtrlCore.cpp` `0x43c73689`, `amSensCtrlCore.cpp` `0x43cdb45a`, `mcAvCtrlCore.cpp` `0x43c454e8`. **Diferencial**: A7S 55/55 idénticas; A6300 90 (55 + 14 `[CDIAG][CTRLCORE] … 4K` + 21 `[CDEXT][CTRLCORE]`, `CdExtCtrlCore` inexistente en la A6000). Sin efecto en S51. Informe `analysis/s137_ctrlcore/ctrlcore.md` + JSON, doc en `docs/capture/s137-ctrlcore.md`, test `tests/test_s137_ctrlcore.py` 54/54.
- Abierto: nombre de `0x439b4244`; ids `0x32`/`0x33` de `ExecSensCmd`; entrada indirecta a `ExecSensCmd`/`ExecSensComp`.

## S132 — el módulo `[CLK_CTRL]` (66 trazas): el control de reloj (21-10-2026, línea general)
- Hecho: `[CLK_CTRL]` es **etiquetado de un subsistema existente**: gestor de reloj **ClkCtrl** con 14 funciones DDL (`ddl_clkctrl_*`), tarea propia, máquina de estados, arbitraje (abrir/cerrar, bloquear/desbloquear sync) e intercambio maestro/esclavo. 66 trazas `0x43c3a1df`–`0x43c3b09c`, 62 referenciadas, **85 sitios** en 36 funciones (cluster `0x4359ee24`–`0x435a1150`); 4 cadenas muertas (`0x43c3a2a6`, `0x43c3afc0`, `0x43c3afe4`, `0x43c3b007`) sin referencia PIC ni puntero absoluto. Cadillas: `CALL CB3` `0x43c3acae`, `ClkCtrl` `0x43c3aef0`, `init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus` `0x43ca3be5`, `ddl_clkctrl_set_sync_signal err = %d` `0x43c3aea5`, despachador `0x435a0880`. **Diferencial**: 66 en A6000 / 0 en A7S / 0 en A6300, pero **misma tabla de 14 API DDL** y mismos mensajes de init en los tres → lo nuevo es la **instrumentación**, no la función (26 vs 14/15 apariciones de `ddl_clkctrl_`). Fija `CLKTYPE` (24P/25P/30P/50I/50P/60I/60P) y `sysv_delay` (µs) → duración del frame y presupuesto temporal de exposición; **sin efecto en S51**. Informe `analysis/s132_clk_ctrl/clk_ctrl.md` + JSON, doc en `docs/capture/s132-clk-ctrl.md`, test `tests/test_s132_clk_ctrl.py` 180/180.
- Abierto: efecto exacto de `sysv_delay` sobre el presupuesto de exposición; relación `CLKTYPE` ↔ `change_vfc`/`subVFC` (solo A6000).

## S136 — el módulo `[ACCY]` (106 trazas) de accesorios (21-10-2026, línea general)
- Hecho: 106 cadenas `[ACCY]` `0x43c24cac`–`0x43c26319`, 111 sitios PIC (estricta) en 61 funciones, 0 muertas, 15 sub-bloques (`REMOTE` 32, `HELLO` 16, `UART` 13, `MAIN` 9, `FACTORY` 7, `BASE` 7, `HOUSING` 5, `SENSER` 3, AVOUT 2, AVR 2, UTILITY 2, JIRO 2, NULL 1, HW1, MAIN 4); **9 clases RTTI `AccyUm*`** (`AccyUmDeviceBase` + `WaterHousing`/`AvOut`/`Avr`/`Hello`/`Jiro`/`Null`/`Remote`; tabla `type_info` `0x43fd7c8c`–`0x43fd7dbc`; `AccyUmKeyStatusMgr` sin clase base); taxonomía de ID (`FACTORY` `0x435646a4`: 0=AvOut, 1=JIRO1.5, 4=HELLO, 5=LANC-AVR) y máscara `0x80`=Remote / `0x40`=WaterHousing; UART propio (`AccyUartOpen` `0x43563bf8`) + OSAL, GID `0x008F0139`, `NotifyInput` `0x43565814` entrega `{KeyCode,ID,State,INFO}`. **Corrección de premisa**: 0 trazas `[ACCY]` en A7S/A6300 y 0/106 textos, pero **el módulo ya existía** (mismas 9 clases `AccyUm*` en los tres blobs, sin trazas; allí además 2 clases `AccyMi*` que la A6000 no tiene) → lo nuevo es el **logging**. El disparador remoto es solo **tecla del mando** (`START STOP OFF` `0x43c260b0` → `KEY:0x0A00000D`), no un camino de disparo → sin efecto en S51. Informe `analysis/s136_accy/accy.md` + JSON, doc en `docs/capture/s136-accy.md`, test `tests/test_s136_accy.py` 16/16.
- Abierto: `ACCY`/`UM`/`Spinal`/`GF`/`SS`/`Tally`/`JIRO`/`AVR`/`LANC`/`AISATSU`; tabla de teclas `0x0A0000xx` → acción; cola OSAL destino (`0x007A0020`); papel de `AccyMi*`.

## S139 — el módulo `[ENCSEQCTRL]` (46 trazas): el control de secuencias de codificación (21-10-2026, línea general)
- Hecho: 46 cadenas `[ENCSEQCTRL]` `0x43c4bce5`–`0x43c4c796`, 46/46 referenciadas, **96 sitios PIC** (estricta, reconfirmados 96/96 de forma independiente) en 32 funciones `0x435d6ad0`–`0x435d90ac`; clase **`McAvcEncSeqCtrl`** (RTTI `0x43c4320f`), fichero `seqCtrl/mcAvcEncSeqCtrl.cpp` `0x43c4bd0f`, componente `Avbb-MovieCodec_131H` `0x43c41227`; **18 ids** `0x8101`–`0x8112` (`tbh` `0x435d8d50`, `ProcAvcMsg` `0x435d8d38`), estado u32 en `obj+0x15B84`, tabla **O/U Crank** 57×8 B `0x43b93bf4`, 35 nº de línea del `.cpp` (89–2237). Relaciones: S132 solo temporal (VFC), S137 por `mcAvCtrlIf` + evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT` `0x43c4c332`, S106 vía `[SYNCENCSTART]`, S114/S115 sin relación. **Diferencial**: A7S **idéntico** (46/46, 96 sitios, `tbh` byte a byte igual `0x435d69e0`); A6300 superset (50, 100 sitios, 5 nuevas). Sin efecto en S51. Informe `analysis/s139_encseqctrl/encseqctrl.md` + JSON, doc en `docs/capture/s139-encseqctrl.md`, test `tests/test_s139_encseqctrl.py` 35/35.
- Abierto: qué es `VFC`; semántica de la tabla O/U Crank; los 6 ids sin nombre; quién crea el objeto (0 punteros absolutos).

## S138 — el módulo `[CAMERA_MAIN_FC]` (9 trazas): el glue hacia `Camera::FC` (22-10-2026, línea general)
- Hecho: 9 cadenas `[CAMERA_MAIN_FC]:` `0x43ca6944`–`0x43ca6aec` (0 en A7S/A6300), 13 sitios PIC (estricta, **recalculados a mano 13/13**) en 7 funciones (`0x437b7200`–`0x437b821e`), logger propio `0x437b7158`; contenido: datos de ojo + flag `lc` (`[ctx+0xde]`/`[ctx+0xdf]`), temporizador OSAL (`0x437b74a4`/`0x437b7778`), `APP MODE ERROR: face_on, obj_on` (`0x437b7844`, `[ctx+0x49c]`/`[ctx+0x49e]`), `BatteryInfo` (`0x437b7d6c`) y tres de disparo táctil. **La sigla `FC` tiene base textual**: namespace C++ `Camera::FC` (45 apariciones y 101 de `FC/` en **los tres** firmwares) → lo nuevo es el *logging* del glue. **Negativo acotado**: **no participa en la cadena de disparo táctil `0x3011`** (ninguna de las 8 funciones de la cadena llama al módulo ni a `Camera::FC`); tiene **API propia** (`ReplyForTouchShutter`/`SetRequestReplyForTouchShutter`, cableada por `wrapper/Face.cpp`) → camino distinto. Informe `analysis/s138_camera_main_fc/camera_main_fc.md` + JSON, doc en `docs/capture/s138-camera-main-fc.md`, test `tests/test_s138_camera_main_fc.py` 53/53.
- Abierto: quién invoca la API de respuesta al disparo táctil del módulo y su relación con la cadena `0x3011`; significado de `[ctx+0xde]`/`[ctx+0xdf]`.

## S143 — el módulo `[CAM_UTIL_ADJ]` (22 trazas): la utilidad de ajuste de la cámara (22-10-2026, línea general)
- Hecho: 22 cadenas `[CAM_UTIL_ADJ]` `0x43ccdcee`–`0x43cce0f2`, 22/22 referenciadas, 22 sitios (1 por cadena) en 3 funciones (`0x439007b0`–`0x439008ac` Table Write/Read, `0x43900a24` `cam_adjcmd_handle_cb()`, `0x43900c44` `tsk_cam_adjctrl`); tabla de despacho `0x440121f8` (idx 1 → `0x439007b0`; idx 0 y 2 → stub `0x43b2a0b8` → **1 de 3 operaciones**), puntero de callback `0x43900a25` en `0x4401f7a4`; **51 comandos «Sens»** de 12 B en `0x43fe858c` (`Sens:AdjCmd CAIF` `0x04020180`, `Sens:RAM Write` `0x04000188`, `Sens:RAM Read` `0x04020189`, `Sens:AdjCmd DwnCamera` `0x0400018a`). **Diferencial**: la etiqueta es propia de la fw3.21 (22/0/0; interiores 0/22 en A7S y A6300; tampoco existen `[CAM_UTIL_SENS]`, `[CAM_UTIL]`, `[CAMERA_ADJ]`), pero la **capa «Sens» es común a los tres** (27 cadenas `Sens:*` idénticas, 51 entradas con los mismos cmd/size; única diferencia: cmd `0x04000167` = `Reserved` vs `POFF return`) → lo nuevo es la **instrumentación**. **Línea del obturador**: no toca obturación/iris/ISO/lectura → vía genérica de escritura de calibración en la RAM del sensor → sin efecto en S51. **Colateral**: la convención vaddr = 0x43541000 + offset también vale para A7S y A6300 (verificado con los punteros de la tabla `Sens`). Informe `analysis/s143_cam_util_adj/cam_util_adj.md` + JSON, doc en `docs/capture/s143-cam-util-adj.md`, test `tests/test_s143_cam_util_adj.py` 30/30.
- Abierto: qué `Module ID` corresponde a iris/ISO/shutter/WB; ids OSAL `0x008f013a` y plantilla `0x43c04d70`; índices 0 y 2 de la tabla de despacho; módulo `[CAMERA_ADJ]`.

## S144 — el módulo `[CAM_UTIL_SENS]` (21 trazas): la interfaz de ajuste hacia el sensor (22-10-2026, línea general)
- Hecho: 21 cadenas `[CAM_UTIL_SENS]` `0x43cce1ea`–`0x43cce66b` (con 3 `[CAM_UTIL]` intercaladas en `0x43cce282`–`0x43cce2f3`); 21/21 referenciadas, **39 sitios** (estricta) en 5 funciones (`0x439012d0` CB de BKID, `0x43901d50` Debug IM ASync Open, `0x43902168` SET FILE NUM, `0x439023b8` UTIL MS Mgr Call CB, `0x43902418` Debug IM Sync Open); globales `0x43f062c8`, `0x43fa29f0`, `0x43fa2d23`, `0x43f062d4`, `0x4401eee4`; **ids OSAL compartidos con ADJ** (log `0x008f0139`, comando `0x008f013a`, módulo `0xb5`); dependencia cruzada ADJ→SENS `0x43900c9c` y SENS→ADJ/`[CAMERA_ADJ]` `0x439012fa`/`0x43901302` → mismo par. **17 llamadas** a `0x43901d50` desde `[CAMERA_MAIN_LC]`, `[IMAGING_CAP]`, `[CAMERA_MAIN_TC]`, `[CAMERA_MAIN_YC]`, `[IDT]`/`[IDT_OPD]` → `cam_util_debug_file_write` vuelca imagen (RAW/YC) en la memoria del sensor. **Diferencial**: 21/0/0 y interiores 0/21, pero la función ya existía (3/2/2, `MemAreaMSDebug` 4/4/10, `Sens:` 27/27/27) → instrumentación. Sin efecto en S51. Informe `analysis/s144_cam_util_sens/cam_util_sens.md` + JSON, doc en `docs/capture/s144-cam-util-sens.md`, test `tests/test_s144_cam_util_sens.py` 22/22.
- Abierto: siglas «IM»/«MS»; `BKID`/`SWFLG`/`MODEFLG`/`MountSTAT`/`FsysMode`; tabla de `0x44022d84`; canal hacia el driver.

## S148 — el módulo `[DEPTH]` (16 trazas): el medidor de profundidad (22-10-2026, línea general)
- Hecho: 16 cadenas `[DEPTH]` `0x43c249ec`–`0x43c24c73` (11 INFO, 2 DEBUG, 3 WARN; 0 en A7S/A6300); 17 sitios (estricta, **verificados a mano**) en 11 funciones (`0x43541b00`, `0x4356228c`, `0x435622d4`, `0x4356230c`, `0x43562354`, `0x435623bc`, `0x43562424`, `0x43562454`, `0x43562634`, `0x43562660`, `0x435626d4`); 0 sin referencia. **No es un módulo nuevo**: clase `DepthGaugeMain` (RTTI `14DepthGaugeMain` `0x43c24b85`, `type_info` `0x43fd7c84`, vtable `0x43fb8f50`, **1/1/1 en los tres firmware**), registrada como `depth` (`0x43c24b46`) en `0x435ab6f0`, **tabla de 6 comandos** de 12 B `0x43fd7c30`, GID `0x018b04dc`, ids 1=GET/2=NOTIFY_ON/3=NOTIFY_OFF (`0x435626d4`), `valueDepth` ≤ 4000 (`0x43541b04`) → la fw3.21 solo añade el **logging**. **Consumidor real**: `CS_ExifMakerNote.cpp` `0x43cc56dc` → `getMsg` `0x438b900a` → tag EXIF **0x5001** = `(valueDepth*10 : 1000)` y **0x5002** = estado; segundo consumidor `[ACCY]` (`0x43564dc0`/`0x43564ed2`). **Negativo acotado**: 0 menciones de obturador/sensor/exposición/AF/lectura y 26 destinos de llamada que no salen del módulo → sin efecto en S51. Informe `analysis/s148_depth/depth.md` + JSON, doc en `docs/capture/s148-depth.md`, test `tests/test_s148_depth.py` 25/25.
- Abierto: magnitud física de `valueDepth` y de `status`; receptor final del GID fuera de av-cam.bin; por qué `[ACCY]` publica `update` con `status=2`; sentido de `0x80`/`0x81` en el MakerNote.

## S151 — el módulo `[PANDA]` (10 trazas): el gestor de mensajes del drive de iris (22-10-2026, línea general)
- Hecho: 10 cadenas `[PANDA]` `0x43c9a599`–`0x43c9a7c8` (`Panda_SendMessage: <canal> osal_valloc_msg error!`, canales Pre1/Pre2/Post1/Post2/Async); 10/10 referenciadas, **15 sitios** (estricta) en 4 funciones (`F1_init` `0x437073cc`, `F4_pre` `0x43707f8c`, `F5_post` `0x437081b8`, `F6_async` `0x437083e4`) y logger privado `0x43707324`; **7 colas OSAL** (`0x00f900bc`…`0x00f90521`), 5 buffers de 0x40 B con GID `0x00740017` (tabla `0x4401eee4`), envío por thunk `0x43561228`, log por GID `0x008f0139` id `0x16`; lo inicializa `Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` `0x43721624` (`bl` `0x4372163e`). **Base textual**: nombre de función `Panda_SendMessage` (10/0/0) y parámetros de iris `uc_PandaADErrorOpen` `0x43c99267` / `uc_PandaADErrorClose` `0x43c9927b` (1/1/1); **0 RTTI, 0 ficheros** → `[PANDA]` **no es un módulo de logging registrado**; sigla sin desarrollar. **Diferencial**: token 10/0/0 y 0/10 interiores, pero el **código existe en los tres** (7 ids de cola 1 vez por blob; `F1_init` equivalente en `0x43729910` (A7S) y `0x437648d0` (A6300), mismo prólogo y misma secuencia de `bl` salvo el reporter: F1 19 vs 14, F4 7 vs 6, F5 5 vs 4) → lo nuevo es el logging. **Negativo acotado**: 0/10 menciones de obturador/sensor/exposición/tiempos; los 47 `bl` van a thunks OSAL, helpers propios y `[CAM_UTIL]`; único vínculo físico: el drive del iris → sin efecto en S51. Informe `analysis/s151_panda/panda.md` + JSON, doc en `docs/capture/s151-panda.md`, test `tests/test_s151_panda.py` 26/26.
- Abierto: Pre/Post/Async; ids de cola `0x00f9xxxx`; GID `0x00740017`; id de log `0x16`; `0x00910042`; receptor final del log.

## S121 — el módulo `[AIP]` (37 trazas): la interfaz de audio con el escalado (21-10-2026, línea general)
- Hecho: 37 cadenas `[AIP]` `0x43cdd844`–`0x43cdec50`; **16 funciones** y 6 sub-bloques RTTI (SaWrapper 8, SaBackUpCtrl 12, SaDriverBase 4, LPS 11, SaDriverZoomNr 1, SetFader 1); callbacks `Ack`/`Comp`/`Err` en SA (`0x43926d1c`/`0x43926de8`, predicados `[r1,#1]==0x14`/`0x13`), LPS (`0x4392b16c`/`0x4392b254`) y driver; **tabla de backup de 350 entradas de 12 B** en `0x43bd1964` (`{id = 0x10c0000+n, offset, size}`), `WriteShadow2BakcupArea` vuelca `0x10c` B (`0x4392ab78`), `SetAudioNrType` publica el bit 3 de `bkId = 0x10e0000`; comandos al escalar en `0x4392ac30` y `0x4392acb4`; `SetFader` `0x4355ae98` divide por 100/20/otro. Cliente: el **ADF** (S81, `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`); **no** es el «SA» de S108. **Diferencial**: A7S con las mismas 37; A6300 con 63 (37 + 26 de `ZNR_EE`). Informe `analysis/s121_aip/aip.md` + JSON, doc en `docs/capture/s121-aip.md`, test `tests/test_s121_aip.py` 97/97.
- **Aporte metodológico (rectificó todo el repo)**: cuantificó los falsos positivos por regla (estricta 37/37; kill analysis 60 = 37 + 23 falsos) y el caso concreto `0x4355bcb2`; con la calibración de S118 se declaró la regla canónica estricta y se rectificaron S106, S110, S113 y S115.
- Abierto: significado de AIP/SA/LPS/ANR/ZNR/Zma/Ext/Mbx; formato de la cola `AudioIpCmdQueue`; contenido de las 350 entradas.

## S119 — `[APL]`: apertura/cierre de SA y HW dentro de `[CAMERA_SA]` (21-10-2026, línea general)
- Hecho: las **42 apariciones de `[APL]` no son un módulo propio** — las 42 están dentro de cadenas que empiezan por `"[CAMERA_SA]: "` (`[CAMERA_SA]: [APL] HW Open Err %d` `0x43cebde1`, `… SA Open Err` `0x43cebe03`, `… Calloc InputPrm Err` `0x43cebe46`) → **etiqueta de segundo nivel**; la entrada "APL 42" de S79 es una sub-etiqueta. 5 funciones emisoras (`0x439cea30` 7, `0x439cebe4` 9, `0x439cedd0` 4, `0x439ceeb8` 20, `0x439cf3b8` 2) con 42/42 referencias 1:1 (estricta) y las 5 equivalentes de la A7S (`0x439bcd80`…`0x439bd3a4`); API SA (`ExecuteOpenMSG` `0x439d143c`, `ExecuteCloseMSG` `0x439d133c`, `ExecuteCalcStartMSG` `0x439d185c`, `CallocCamSaParam` `0x439d0f58`, `GetMemInfo` `0x439d1bd0`, `GetExecUnit` `0x439d168c`); `unit_hndl` = handles del DMM (S113). **Consumidor único**: `[CAMERA_MAIN_TC]` ("ApolloSA"), un solo llamador por función; ni S106 ni S107 lo llaman. **Diferencial A7S**: los mismos 42 textos pero allí **empiezan por `[APL]`** → la fw3.21 antepone `[CAMERA_SA]: `. Informe `analysis/s119_apl/apl.md` + JSON, doc en `docs/capture/s119-apl.md`, test `tests/test_s119_apl.py` 47/47.
- **Tercera calibración de la regla PIC**: la "ancha" da 67 pares para 42 cadenas reales (25 falsos verificados a mano). Con S118 y S121 son tres módulos donde la regla estricta coincide con la verdad medida.
- Abierto: el módulo `[CAMERA_MAIN_TC]` ("ApolloSA"), su consumidor, sin hito propio; layout de `InputPrm`; GetZimaNo vs GetExecUnit; códigos de error.

## S111 — el módulo `[TRK]` (215 cadenas) de tracking y detección (21-10-2026, línea general)
- Hecho: integración del hito del subagente **con revisión**. 216 apariciones de `[TRK` → **215 cadenas** (214 que empiezan por `[TRK` + 1 anidada) → **207 textos distintos** (8 duplicados) en `0x43cebceb`–`0x43cfe31c`; **288 sitios** (283 strict + 5 relaxed) y **47 funciones**; sub-bloques STK 76, BT 44, EDTSA 19, PMV 16, IRO2G 13, DETSA 9, VAE/VAT/VOT 3; código en `0x43a30000`–`0x43a39000` (284 sitios, 43 funciones) + 4 wrappers de sesión en `0x439c0000`; **99 ficheros `FC/*.cpp`** embebidos. **Diferencial A7S fw3.20**: mismas 215 cadenas y 207 textos, mismos recuentos → módulo idéntico. Informe `analysis/s111_trk/trk.md` + JSON, doc en `docs/capture/s111-trk.md`, test `tests/test_s111_trk.py` 17/17.
- **Correcciones/ajustes de la revisión**: (a) el subagente usó la regla estricta (*nearest-ldr*); con la regla canónica del repo son 214 referenciadas y 657 sitios (criterio de atribución, no discrepancia de hechos); (b) **se ensanchó el rango de cadenas válidas de `scan_pic_refs.py`** (estaba fijo a `0x43c90000`–`0x43cd0000` y excluía la zona de `[TRK]`, dando 0 referencias) → ahora acepta `LO HI RUTA_SALIDA` y cubre toda la imagen (95 711 destinos).
- Abierto: límites de las funciones `0x43a376d8`/`0x437a37734`; los 2 sitios *relaxed*; correspondencia 1:1 de los 99 ficheros `FC/*.cpp` con funciones.

## S115 — `[CAM_IMAGER]`: el driver del imager de la cámara (21-10-2026, línea general)
- Hecho: 371 trazas `[CAM_IMAGER]` (79 del ZIT de S80 → **292 del driver**) en **94 funciones** (`0x43543568`–`0x436dbd66`): **P2S** (canales DFE0/DFE1, datos por páginas `P2SData[Page:%01x]` `0x43c931d6`, `P2SFormatter` `0x43c932ac`, `P2S CheckAddrOrder` `0x43c9327c`, `P2SWaitTransComp` `0x43c93180`), **interrupciones** (`int_p2s_handler`/`int_timer_handler`, temporizador por canal `CH`), **SIF** (sync code en serie `0x43c94e55` o en paralelo `0x43c94e92`, `SetSIFMode`, `AD_MODE`), **`ImagerCommon`** (16 trazas, API macro hacia el CISIF, 8 con `do not use CH_1` → un solo canal) y **`SubLVDS`** (9). **Máquina de lectura/exposición por `drive_mode`**: `SetExps` `0x43c93cc2` con el campo **`shut`**, `SetExpsZ` `0x43c939b5`, `SetRead` `0x43c93fcb`, `SetReadZ` `0x43c93d67`, `Execute` `0x43c94076` (`SSBRK_ON`, `SLEEP_ON`), `Execute.` `0x43c940d7` (`SSBRK_ON`, `SIFSyncCode`), `Execute0/1` `0x43c93ae2`/`0x43c9413a` (`ssb`, `read`, `svr`), `SetMode` `0x43c93b2f` (`ntpal`). **Diferencial A7S fw3.20**: 0 con el prefijo; el mismo driver sin etiqueta y sin `SetExps`/`Execute0`/`AGainCont` (0 apariciones). Informe `analysis/s115_cam_imager/imager_driver.md` + JSON, doc en `docs/capture/s115-cam-imager.md`, test `tests/test_s115_cam_imager.py` 9/9.
- Abierto: significado de `svd`, `shd`, `spl`, **`shut`**, `epd`, `epdsel`, `ssb`, `read`, `svr`, `ntpal`; tabla de parámetros por `drive_mode`; prefijo del módulo equivalente en la A7S.

## S112 — el módulo `[CAMERA_MAIN_SYNC]` (429 trazas) de sincronización de recursos (21-10-2026, línea general)
- Hecho: integración del hito del subagente **con revisión y correcciones**. 429 cadenas `[CAMERA_MAIN_SYNC]` `0x43c9b409`–`0x43cb5616` (el borrador apuntaba un byte después del inicio real y no cortaba el texto en el NUL → reextracción con `reextract.py`); 101 sub-bloques (160 sin etiqueta, `SyncResMgr` 55, `APL_ERR` 17, `jpeg` 13, `DFS` 11, `Sequence_Movie` 9); **mapa función→traza completado** (430 funciones, 1 407 pares) y **diferencial A7S verificado byte a byte**: 0 con el prefijo, **418/429** mensajes comunes y **11** exclusivos de la A6000 (`CamOutV` `0x43ca2de1`, `CamV` `0x43ca35b6`, `CONNETCT_COMP err` `0x43ca3fe7`, `DISCONNETCT err` `0x43ca4045`, `SuperSlowMotion[Buffering] error` `0x43cb0ded`, `Sync_Kick_IDT: overflow` ×2, `Sync_Cam_Setting: DIST_RSLT_NG` `0x43cb10f7`, `Sync_Kick_RCH: overflow` ×2, `EC::CapISO Error` `0x43cb55dd`). Informe `analysis/s112_camera_main_sync/camera_main_sync.md` + JSON, doc en `docs/capture/s112-camera-main-sync.md`, test `tests/test_s112_camera_main_sync.py` 12/12.
- Abierto: significado de `Sync_Kick_IDT/RCH/RCV`, de las abreviaturas `HS`/`VD` y del contador `%d/8V`.

## S114 — el motor de secciones de la captura: 17 ids ↔ 17 etapas (21-10-2026, línea general)
- Hecho: cierre de la pregunta abierta de S106 (asignación id↔etapa). **15 de las 17 secciones** de la tabla `{id, manejador}` de `0x43ff8fb4` nombradas: `0x01` = **Prelight** (identificado porque el manejador `0x437eb144` llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) y las 14 restantes por su propio `*_Selector.cpp` (`0x02` Exposure, `0x03` Read, `0x04` AfterRead, `0x05` DevEntry, `0x07` CorrectRaw, `0x08` OpdBeforeNR, `0x09` Develop, `0x0a` Marble, `0x0b` FeatureEffect, `0x0c` AfterEffect, `0x0d` Encode, `0x0e` AfterEnc, `0x0f` SortJpeg, `0x10` DevExit). `0x00` (`0x437eabfc`, selector puro de perfil: solo `0x43ae75dc` y `0x43ae76ca`) y `0x06` (`0x437eaa5c`, misma forma que `0x01` sin el selector de Prelight) **no tienen nombre** en el firmware. 5 de los 16 selectores los registra código **fuera** de la tabla (`SequenceFilter` en 5 funciones con 14 registros) → selectores auxiliares. Informe `analysis/s114_sections/section_engine.md` + `section_map.json`, doc en `docs/capture/s114-section-engine.md`, test `tests/test_s114_sections.py` 9/9.
- Abierto: significado de `0x00`/`0x06`; la tabla de 20 B (5 u32) por sección; relación entre secciones (`SectionQueueManager.cpp`, `SectionEndFunc.cpp`); si `SequenceFilter` es sección o filtro externo.

## S113 — `[CAM_DMM]`: el gestor de memoria dinámico de la cámara (21-10-2026, línea general)
- Hecho: decodificación de las 54 trazas `[CAM_DMM]` (`0x43cce6ae`–`0x43ccf1c3`, todas de error) y de su implementación, **25 funciones contiguas** `0x439011d8`–`0x43903d5c`: **11 operaciones** (`AllocNew`, `AllocNewRdv` = rendezvous, `AllocShare`, `Free`, `FreeRdv`, `Open`, `Close`, 4 `MemoryHandle::*`, `AsyncAllocNew` `0x439037c0`, `AsyncAllocRule` `0x43903b80`, `LoadExtraMap` `0x43903d5c`), **4 clases de error DMM** (`ERR_DMM_RET_CODE` 10, `ERR_DMM_DIFFERENT_COMP` 10 con `msg_id`/`my_id`, `ERR_DMM_HANDLE` 4, `ERR_DMM_OPEN` 5) y **4 de capa OSAL** en las asíncronas → frontera DMM↔OSAL real (S38). El userland `DmmAccess` de `libmprctrl.so` (S37) es **cliente** de este servidor. **Diferencial A7S fw3.20**: 0 trazas con prefijo, 50/54 mensajes equivalentes sin etiqueta; las 4 de `AllocNew` sustituyen a `AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x` (`0x43cb4f99`). Informe `analysis/s113_cam_dmm/dmm_module.md` + JSON, doc en `docs/capture/s113-cam-dmm.md`, test `tests/test_s113_cam_dmm.py` 11/11.
- Abierto: valores numéricos de `ERR_DMM_*`/`ERR_OSAL_*`; formato del mensaje OSAL asíncrono; tabla de reglas de `AsyncAllocRule`; qué carga `LoadExtraMap`.

## S108 — el módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar (21-10-2026, línea general)
- Hecho: integración de las 231 trazas `[CAMERA_SA]` (`0x43cc5286`–`0x43cef0d8`) en 13 sub-bloques (APL 27, memoria 20, `GetAddr` 35, alineación 29, mailbox 18, DUALREC 14, handles 20, `sa_func_*` 8, `SA_FUNCDRV_E_*` 3, otros 51; suma verificada = 231). 8 de las 19 familias `sa_func_*` de S84 aparecen con traza directa (`BDEX_exit`, `BFNR_release`, `BOKS`, `LFNR`, `KKNR`, `NFLASH`, `YKNR`, `DUALREC_BAYER`). **Diferencial**: A7S fw3.20 y A6300 fw2.01 tienen 0 trazas con la etiqueta y los 231/231 mensajes idénticos sin ella. Informe `analysis/s108_camera_sa/camera_sa.md` + JSON, doc en `docs/capture/s108-camera-sa.md`, test `tests/test_s108_camera_sa.py` 4/4.
- **Correcciones de la revisión (agente principal):** (a) la tabla de sub-bloques ponía "Parámetros Inválidos: 17" y omitía "Otros" (sumaba 195, no 231) → corregida a 2 y 51; (b) `ExlHelper` y `MonPowersave` no aparecen en `[CAMERA_SA]` (son de `[CAMCORE]`, S107); (c) el A6300 no tiene "más trazas": tiene los mismos 231 mensajes sin etiqueta.
- Abierto: atribución función→traza (pendiente de aplicar el esquema PIC de S110) y formato binario del mailbox del SA.

## S110 — `Camera::YC`: el motor de imagen de la A6000 (21-10-2026, línea general)
- Hecho: decodificación de las 970 trazas `[CAMERA_MAIN_YC]` (`0x43ca88f6`–`0x43ccd469`, 4 bloques): **API de 8 funciones** `api_YC_*` (`api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`, `api_YC_SetCapStar` `0x437cfe94`, `api_YC_SetCapTbox` `0x437d88e4`, `api_YC_SetSaCamDsp` `0x437ce0cc`/`0x437d77a8`/`0x437d8940`, `api_YC_SetVdPreParam` `0x437d0768`/`0x437d5608`/`0x437d9a04`, `api_YC_LfnrSetParam` `0x437d8bd4`, `api_YC_DEV_SetCoodinate` `0x437d9d1c`) y **12 jobs** `job_YC_*` (`job_YC_Initialize` `0x438aa574`, `job_YC_ModeManager` `0x4389f29e`, `job_YC_SetParam` 15 sitios, `job_YC_CalcParam` 14, `job_YC_GetTagPointer` 19, `job_YC_SetCapBoks` `0x4387f4b0`, `job_YC_SetCapStar` `0x438aec84`, `job_YC_SetParamOn` `0x438b7c48`, `job_YC_SetParamOff` `0x438b7ba4`, `job_YC_SetParamPrelight` `0x4389b80c`, `job_YC_SetPreParam` `0x4388bb54`, `job_YC_SetSaCamDspParam` `0x4388b2c4`); **141 sub-módulos etiquetados** (`SHD` 219, `ITP` 90, `YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19); mapa **función→traza** con 251 funciones (regla estricta) y 954 de las 968 cadenas referenciadas; **119 ficheros fuente** embebidos (`Sequence_Common.cpp` `0x43cb14a1`, `Sequence_Movie.cpp` `0x43cb31f1`, `yc_clp_common.cpp` `0x43cb81ac`, `init_cam_SetCamParam.cpp` `0x43cb40b8`, `SyncLoader.cpp` `0x43cb397a`, `CS_ExifMakerNote.cpp` `0x43cc56dc`, `ddl_stitch.cpp` `0x43cc6964`…). **Comprobación cruzada con S78** (Ghidra vs método PIC): `job_apc_main_stl` → `0x438b3ea8` y `job_apc_main_mov` → `0x438b5810`, idénticos. **Diferencial A7S fw3.20**: 969 de las 970 cadenas son comunes (sin la etiqueta de módulo); la única nueva de la fw3.21 es `HD_SWEEP_HOLD  =%x` `0x43cbc27c`. Informe `analysis/s110_camera_main_yc/yc_engine.md` + JSON, test `tests/test_s110_camera_main_yc.py` 15/15.
- **Corrección de método (arrastrada a S106):** el escáner PIC emparejaba cada `add rX,pc` con el `ldr` más cercano del registro y se detenía en el primer destino válido; como el registro se reutiliza, atribtaba mal algunas referencias. Corregido (se prueban todos los `ldr` del registro en 4 KB y solo se aceptan destinos en el inicio de una cadena): S106 pasa de 694/697 a **696/697** (de 3 cadenas muertas a **1**, `0x43ca9b12`) y el mapa de YC de 958 a **960** referencias.
- Abierto: significado de las siglas (SHD, ITP, DCV, OLC, CLP, PFR, ZDL, OAC, OPB, ARC); tabla de despacho de jobs (no localizada, ni absoluta ni PIC); enlace por código `api_YC_SetCapBoks/Star/Tbox` ↔ `Stage_BOKS/STAR/TBOX`; sentido de `HD_SWEEP_HOLD`.

## S107 — `Camera::CamCore` y la pila de recursos `ResourceStack` (21-10-2026, línea general)
- Hecho: decodificación de las 37 trazas `[CAMCORE]` de la fw3.21 de la A6000 (`0x43c905ca`→`0x43cebcb2`; 0 en la A7S fw3.20): SGC (`SgcTable`), RDC/PFR (memoria PFR, `PFR in width[%d] > 596` `0x43c90ca3`), AIF (`AIF%d out[%d] > memsize[%d]` `0x43c90a96`, `pbl_aif_set_func` `0x43c90abd`), `MemoryPool has no space.` `0x43c908e7`, `ResourceBase::Release was called without acquire` `0x43c90ec5`, `ExlHelper` (5), *setter* de DMA (6), `MonPowersave` `0x43c90f07`, corrección de defectos (`Acl::CAMHEAD_Z1C::setDefectPt` `0x43cebcb2`); RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6` y `N6Camera7CamCore13SplitRdcImageE` `0x43cb0b94`. **Pila `ResourceStack`**: 4 mensajes en el bloque `[IMAGING_CAP]` (`0x43ca10d1`–`0x43ca120f`) → la consume el gestor de captura still (S106). Informe `analysis/s107_camcore/camcore_resources.md` + JSON, test `tests/test_s107_camcore.py` 9/9.
- **Correcciones de la revisión (agente principal):** (a) el borrador daba por expandidas las siglas SGC/RDC/PFR/AIF ("Sensor Gate Controller", "Raw Data Converter", "Arterial Image Framework") — el firmware **no las expande**: se marcan como hipótesis; (b) los sitios de referencia citados para las trazas `sa_func_DUALREC_*` eran funciones, no referencias → los reales son `0x437ed95e`, `0x437ee4ae`, `0x437ee716`, `0x437eeb34`, `0x437ee84e`; (c) el diferencial A7S daba por "no verificado" `ExlHelper` (5) y `MonPowersave` (1) — **existen** en la A7S sin etiqueta, igual que los mensajes `ResourceStack)` (`0x43ca61fa`, `0x43ca6226`, `0x43ca6252`): la fw3.21 solo añade etiquetas de módulo.
- Abierto: significado de SGC/RDC/PFR/AIF/Exl; formato interno de la ResourceStack; por qué 2 de las 5 cadenas `ExlHelper` no tienen referencia PIC.

## S106 — `IMAGING_CAP`: el gestor de captura still de la A6000 (21-10-2026, línea general)
- Hecho: reconstrucción del subsistema de captura still a partir de sus **697 trazas** (`0x43c9b335`–`0x43ccab72`) y de los **83 nombres de fichero fuente embebidos** (`0x43ca8e14`–`0x43cb0cbe`): 16 `*_Selector.cpp`, 10 `CaptureUtility*.cpp`, 9 manejadores, 6 `RawMemManager*.cpp`, 8 `Stage_*.cpp`, `CaptureManager*.cpp`, `SectionController.cpp`, `CaifCom_Control.cpp`, `NotifyController.cpp`, `ImageParamCapture*.cpp`. **Motor de secciones**: tabla de 17 entradas `{id u32, manejador u32}` en `0x43ff8fb4`; el despachador `FUN_437e534c` copia `0x88` B y busca el id entre 17; cada manejador devuelve 20 B (5 u32) de parámetros según el modo de captura; 14 manejadores referencian su `Capture<Etapa>_Selector.cpp`. **CapMgr** con tabla de salto de 16 entradas en `0x43bc4e08`; **CAIF** (`CAP_REQ`, `CAP_REQ_CLR`, `CAP_SETTING`, `CAP_START`, `CAP_DATA`, `CAP_V_COM` con dirección `[EN->CA]`/`[CA->EN]`/`[CA->AVIP]`); **8 modos `MODE_CAP*`** del CamCore; capa `ImageParam_Capture`/`RawMemManager`/DMM. **Método**: esquema **PIC** de referencias a cadenas (`destino = literal_del_pool + (add rX,pc + 4)`) verificado con dos casos; `690/697` cadenas referenciadas y **7 sin referencia confirmada** (los cuatro `DistV_RC`/`DistH_RC`, `0x43ca9b12`, `0x43cc7d5c`, `0x43cc839c`; sin puntero absoluto ni destino PIC). *(La «corrección» de S110 —694→696— se apoyaba en la regla «ancha», que inventa referencias; la kill analysis tampoco es exacta. Regla canónica: la estricta, validada a mano en `[SFRA]` y `[AIP]`. Ver `analysis/s106_imaging_cap/pic_xref_methodology.md`.)* **Diferencial A7S fw3.20**: 0 cadenas con el prefijo `[IMAGING_CAP]`; los mismos mensajes existen sin etiqueta → la fw3.21 añade la etiqueta; los 16 selectores están en A6000/A7S/A6300. Informe `analysis/s106_imaging_cap/imaging_cap_architecture.md` + JSON, test `tests/test_s106_imaging_cap.py` 18/18.
- **Negativo verificado:** 0 apariciones de `shutter`/`silent`/`EFCS`/`curtain`/`mechan` en las 697 trazas → el gestor de captura no registra nada del obturador; **S51 sin efecto (A/B/C = NO)**.
- Abierto: ids de sección `0x00`, `0x01`, `0x06` sin nombre de selector; significado de los 20 B por sección; formatos binarios de CAIF y `MSG_ID_SDF_*`; por qué 3 cadenas quedaron sin referencia.

## S105 — panorámica/barrido (sweep), bracketing e intervalo (21-10-2026, línea general)
- Hecho: `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un campo de 2 bits del contexto `0x43e9b548`; en el valor 2 pide la petición `0x301f` (`movw r0,#0x301f` en `0x437df7a2`; `[IMAGING_CAP]: !!! Can't send Panorama cmd` `0x43caa019`). Cadena `Stage_InitializeSweepAndSpoolBranch` `0x437f0838` → `Stage_Panorama::PanoramaSweepStart` `0x43549020` → `PanoramaSweepStart` `0x437e6b3c` → `UpdateSweepCanvas` `0x437e751c` → `PanoramaSweepEnd` `0x437e6e78` → `seq_panoramaClippingDecode` `0x43780eb4` → `PanoramaStitch` `0x438bcef8` → `PanoramaResize`/`PanoramaResizeEncode`; stitch por tiras (`PanoramaStripSequence::StripInfo` `0x438f4bcc`, `PreProcessResult::Strip[]` `0x43ccd5fa`). Bracketing: solo `lc_BracketAF.cpp` `0x43ca79ba` (2 métodos de `Camera::LC` `0x437c74b6`/`0x437c7554`); el resto lo orquesta `libObj.so`. Intervalo: `GetCaptureIntervalResource` `0x437df338`, semáforo OSAL `CAPTURE_INTERVAL` `0x43caa2b1`–`0x43caa3f8`, control por PTM (`[SDF] interval(PTM) %ld` `0x43c7a1a5`, límite 900000 → `[SDF_ERR] interval_ptm over 10[sec]` `0x43c7a1be`). Informe `analysis/s105_panorama/panorama_bracket_interval.md` + JSON (260 cadenas), test `tests/test_s105_panorama.py` 305/305.
- Abierto: N de capturas (lo decide el userland), acrónimo CCNR, unidad del timer OSAL y del PTM, valor del campo de 2 bits, clase LC del bracketing, ids `0x3005`/`0x301f`, algoritmo de `exec_tanzaku`.

## S104 — prefijos de traza exclusivos de la A6000 (21-10-2026, línea general)
- Hecho: integración del hito de los prefijos exclusivos (subagente `deepseek-v4.1-flash`, variante low, tareas cortas) **con revisión**: `ADC_DEBUG` 14 (`0x43ce50dd`→`0x43ce5273`; ADC de 12 canales del LIRO, `TSK_ADC`, `boot_exit_adcliro`, mensaje OSAL de 0x20 B con cabecera `0xfff1` en `0x4398eb22`), `AVR` 2 (`0x43c25502`→`0x43c25528`; accesorio LANC-AVR de `ACCY`, `0x43c252b4`, handlers `0x43565680`/`0x435656d4`), `ADR` 1 (`0x43cce3fa`; campo de dirección dentro de un mensaje de `0x43901d50`, no un módulo), `BKID` 4 (`0x43cce1ea`→`0x43cfb1a8`; *backup ID*, `BKID_SDF_QTBL_C`), `AVOUT` 2 (`0x43c2549e`→`0x43c254c6`; accesorio AvOut de `ACCY`, `0x43c25260`), `CAMCORE` 37 (`0x43c905ca`→`0x43cebcb2`; `Camera::CamCore` — SGC, RDC/PFR, AIF/DMA, `ExlHelper`; RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6`). Los seis están ausentes en A7S fw3.20. Informe `analysis/s104_prefixes/a6000_prefixes.md` + JSON, test `tests/test_s104_prefixes.py` 6/6.
- **Corrección de la revisión:** S73 decía cuatro cadenas `ADJ ADC`; son **cinco**, y `GET_DATA` (`0x43ce4fc7`) no está referenciada.
- Abierto: el formato del mensaje del ADC y qué hace con cada canal; qué accesorios concretos son AVR/AvOut.

## S103 — el subsistema SDF: la capa de dataflow de imagen still (21-10-2026, línea general)
- Hecho: integración del hito de SDF (subagente `nemotron-3.5-lightning-free`) **con revisión y tres correcciones**. `[SDF]` 477 trazas `0x43c7785b`→`0x43c806f9` y 15 `[SDF_ERR]` `0x43c7a145`→`0x43c7eb78`; **33 `MSG_ID_SDF_*` distintos** en `0x43c78000`→`0x43c78350` (resize/rotate, JPEG encode/decode, CCNR, panorama, THM, develop resize, dist, face resize, PTM); los errores son comprobaciones de **PTM** (`PTM_FIRST_ZONE`/`PTM_SECOND_ZONE`, `interval PTM`, `check stop PTM`). Funciones `FUN_43638308` (init, base `0x43c77857` = `"sdf"`), `FUN_435ab6f0` (dispatcher), `FUN_4363c730` (factoría de jobs JPEG), `FUN_4363ca28` (ejecutor), `FUN_43639c78` (mensajes); userland `OBJAVBBCBASECLASS::SdfCh` (S99). A7S fw3.20: mismo módulo, 479 trazas, `0x43c7a1eb`→`0x43c83082`. Informe `analysis/s103_sdf/sdf_module.md` + JSON, test `tests/test_s103_sdf.py` 51/51.
- **Correcciones de la revisión:** (a) el borrador afirmaba que `IMAGING_CAP` era el pipeline de **vídeo** y SDF su equivalente still — es falso, `IMAGING_CAP` (S106) es el gestor de captura **still**; (b) el rango A7S estaba **invertido** (`0x43c83082`→`0x43c7a1eb`), corregido; (c) el recuento de mensajes decía **48** y el test era tautológico (`actual=48`); el conteo real por bytes es **33** y el test ahora cuenta con `re` sobre el binario. También se corrigió «SA = Secure Area» → SA es el **acelerador escalar**.
- Abierto: el acrónimo SDF (hipótesis *Still DataFlow*), el formato de los mensajes, y las 2 trazas de diferencia con la A7S.

## S102 — menú principal (botón MENU): cadena de carga y apertura (21-10-2026, línea de RE general)
- Hecho: APK de la cámara organizadas por función y decompiladas (jadx; WifiSettings no decompila por odex optimizado); cadena `libObj`→`viewUnified2`→`viewUnified3..8` y registro de vistas verificados contra el log real; vistas de menú; `DefRootView` identificado como árbitro de arranque (hipótesis previa de `ActionOpenSettingMenu` = tecla MENU, refutada); conversión de teclas `0x1501xxxx` (base+1/+2/+4).
- Abierto: código de evento de MENU y la vista de disparo que abre BASE_MENU; significado de los tokens `@Vxxx`; volcar el log de RAM tras pulsar MENU. Doc: `docs/capture/s102-menu-principal.md`.

## S101 — selector del tipo de mecanismo y consumidores de los campos de ajuste (21-10-2026, línea del obturador)
- Hecho: análisis estático de `+0x238`/`+0x280`, del tipo de mecanismo de Darwin (A6000/A7S/A6300), de los 12 puntos abiertos, del grafo de módulos y del selector de tipo de A6000/A7S. Plan de pruebas físicas redactado, sin ejecutar. Detalle: [docs/capture/s101-conclusions.md](../docs/capture/s101-conclusions.md). Nota: en commits aparece como S70/S71/S72 (numeración usada además por otros hitos).
- Abierto: qué ajuste gobierna `G+0x808` y quién lo rellena; P0–P8 del plan físico.
