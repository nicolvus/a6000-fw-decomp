# S403 — cierre de pendientes: entorno, documental y estático (25-10-2026)

Respuesta al encargo de cerrar los 13 pendientes estáticos, los 5 documentales y los 4 de entorno de [PENDIENTES](../PENDIENTES.md).
«Cerrado» significa lo que el código permite decidir, con el límite escrito; **no** se cerró lo que exige cámara, hoja de datos u
otro MCU. Sin firmware ejecutado, sin cámara, sin flasheo. REA: una sesión por modelo (`av-cam` A6000 y A7S), cerradas al terminar.
Código y datos: [analysis/s403_pendientes/](../../analysis/s403_pendientes/). Pruebas: `tests/test_s403_*.py`, `tests/test_s515_s516_s628_s630.py`.

## Resumen

| ID | Antes | Ahora | Resultado |
|---|---|---|---|
| C1 | ABIERTO | CERRADO | `unicorn 2.1.4` instalado; los 8 módulos S56–S61 pasan (315 pruebas, 36 subpruebas). |
| C2 | ABIERTO | CERRADO | `test_mcp_server.py` colecta y pasa (6) con el `.venv` (que trae `mcp`); no era un fallo del repositorio. |
| C3 | ABIERTO | CERRADO | `mypy scripts/knowledge tests/knowledge` sin errores (21 archivos): 5 aserciones de tipo en los cargadores de módulos y `mypy.ini` para `capstone` sin stubs. |
| C4 | ABIERTO | CERRADO | Suite completa: 3521 aprobadas, 35 omitidas, 0 fallos, 529 s (9 min 20 s con arranque). Pico de ~6,3 GB de RAM. |
| D1 | ABIERTO | PARCIAL | 226 etiquetas revisadas de forma léxico-estructural; 4 `ACEPTO` decodificadas por texto. [Informe](s403-censo-revision.md). |
| D2 | ABIERTO | CERRADO | S515, S516, S628, S629, S630: [informe](s515-s516-s628-s630-modulos.md) y 8 pruebas. |
| D3 | ABIERTO | PARCIAL | Logger dual: 3 fichas verificadas, 19 sin respaldo estático (negativo acotado). Equivalencia: 17 trazas con homólogo, 10 comparadas, ninguna igual. |
| D4 | PARCIAL | PARCIAL | Sin cambio de veredictos; ver §D4. |
| D5 | BLOQUEADO | BLOQUEADO | Las hojas de datos no existen públicamente. |
| E1 | NO_VERIFICADO | NO_VERIFICADO | Sin cambio. |
| E2 | ABIERTO | PARCIAL | El check `0x907ba0` no condiciona la fila `0x10000005`. |
| E3 | ABIERTO | PARCIAL | Cinco sitios de llamada de SetExposure y sus escritores de `params[+9]`. |
| E4 | NO_VERIFICADO | PARCIAL | Tabla booleana por modo y máscaras de `0x4379d37a`. |
| E5 | PARCIAL | CERRADO | Ausencia acotada del lector `+0x238` (A6000) y del almacén `[S+0]` (A7S). |
| E6 | NO_VERIFICADO | BLOQUEADO | Darwin está fuera de `av-cam`. |
| E7 | ABIERTO | CERRADO | Los 14 sitios que acceden al objeto por el slot solo leen; el único productor es el callback de copia de Backup. |
| E8 | ABIERTO | PARCIAL | Los dos lectores S176 enlazados con llamadores; el objeto tiene 14 sitios de lectura. |
| E9 | PARCIAL | BLOQUEADO | La semántica eléctrica exige D5. |
| E10, E11 | — | sin cambio | Sin avance estático nuevo. |
| E12 | ABIERTO | PARCIAL | Buzón `0x0110027c`: 13 sitios emisores, ningún receptor por literal. |
| E13 | ABIERTO | BLOQUEADO | Sin hoja de datos ni símbolos ([S335](s335-mmio-layer.md)). |

## Entorno (C1–C4)

- La suite se ejecutó con `pytest tests -q -x`; el pico de memoria del proceso fue ~6,3 GB. Tiempos: las pruebas más lentas son
  `test_s55_bionz_sync` (52 s de preparación) y `test_s307_a7s_writers` (46 s).
- `mypy.ini` (raíz) contiene solo `[mypy-capstone.*] ignore_missing_imports = True`. Los cinco cargadores de módulos por
  `importlib` llevan `assert spec and spec.loader`.
- El resultado `35 omitidas` son pruebas condicionadas a firmware o herramientas (`skipUnless`); no se auditó una por una.

## Documental

### D1 — censo de etiquetas
Ver [s403-censo-revision.md](s403-censo-revision.md). Cambia el nivel de revisión (de «ninguna» a «léxico-estructural»), no los veredictos.

### D2 — colas S515, S516, S628–S630
Ver [s515-s516-s628-s630-modulos.md](s515-s516-s628-s630-modulos.md). `[BL]` es subetiqueta de trazas de montura (lente), no «backlight».

### D3 — afirmaciones S605–S627
- **Logger dual** ([d3_logger_dual.json](../../analysis/s403_pendientes/d3_logger_dual.json)): con el criterio de S607/S611/S616
  (referencia PIC al inicio de la cadena y otra interior seguida de llamada a `0x43902718`, a ≤ `0x300` B), reproduce S607 (6 de 6),
  S616 (4 de 4) y S611 (4 de 5 por patrón; las 5 ya constan por instrucciones). Las otras 19 fichas con trazas (79 trazas) tienen
  referencia local en 78 y **ninguna** ruta global del mismo tipo; S618 no tiene trazas. Estado: `NO_RESPALDADO_ESTATICO`. No refuta un
  logger dual con otra forma de código; solo deja de sostener la afirmación.
- **Equivalencia** ([d3_equivalence.json](../../analysis/s403_pendientes/d3_equivalence.json)): de las 94 trazas, 17 (S605, S606, S607,
  S611, S615) tienen su texto núcleo también en A7S y A6300. REA resolvió la rutina en ambos modelos para 10 (S606, S607, S611, S615);
  en las 10 el flujo normalizado **difiere** (p. ej. 97 frente a 84 instrucciones en el temporizador `osal_alloc_timer`; el último par, 542 frente a 311). Sin igualdad de instrucciones no hay equivalencia de código para esas rutinas; la equivalencia funcional sigue
  `NO_VERIFICADO`. Las otras 77 trazas no tienen homólogo textual: la comparación por cadenas no es aplicable.
- Efecto sobre las 66 afirmaciones sin verificar: las 20 de logger dual quedan con negativo acotado; de las 46 de equivalencia, las
  de código de 4 fichas quedan refutadas para las rutinas comparadas y el resto no tiene homólogo textual o rutina resuelta.

### D4 — triaje S400
Las 86 filas `VIGENTE` no se modificaron: cada una exige cotejar un hallazgo histórico concreto, y el test del triaje fija sus citas y
hashes. 18 de ellas citan la auditoría global S605–S627; los datos de D3 la respaldan en lo cuantificable, pero no delimitan qué
afirmación de cada ficha rectifican, así que siguen sin certificarse.

### D5
Sin cambio: no hay hojas de datos de IMX210/IMX235 públicas.

## Estático

### E2 — activación de RecordImage/RecordStill
El check `0x907ba0` de la fila de estado `{2, 0x10000005, check 0x907ba1, …}` compara `ObjMsg::GetMessageId()` con la palabra `0x10000003`
(pool `0x907c74`, cargada en `0x907bcc`). Devuelve 0 solo si el mensaje es nulo o si es el `0x10000003` y la búsqueda `0x910e1c`
deja ambos campos en `-1`, o si el segundo argumento es mayor que 1; para `0x10000005` imprime una línea de consola y devuelve 1. La fila no depende, pues, de una condición
de datos. El productor externo de `0x10000005` sigue sin ubicarse (E2 sigue PARCIAL).

### E3 — origen de `params[+9]` en SetExposure (IMX210)
`0x436d6320` tiene **cinco** sitios de llamada directos (`0x438c79fc`, `0x438c830c`, `0x438c8824`, `0x438cc894`, `0x43ae937c`);
cuatro pasan el bloque `ctx+0x64c` (offset `+9` = `ctx+0x655`) y uno, vía `0x43ae935a`, un bloque en pila (`0x43811214`).

| Sitio | Valor de `+9` | Cómo se fija |
|---|---|---|
| `0x438c79fc` | 4 | `0x438c79e0..e2`: `adds r3,#4` sobre 0; bloque a cero salvo `+9` |
| `0x438c8824` | 1 | `0x438c87e6`: `mov.w sb,#1`; `strb sb,[r4,#0x655]` en `0x438c87f0` |
| `0x438c830c` | 0 (si la clase de modelo `0x43a12c64` es 2 o 3; `+0`=2) | `0x438c82bc`; si no, conserva el valor previo |
| `0x438cc894` | valor previo del bloque | sin escritura de `+9` cercana |
| `0x43ae937c` | 1 si `[r4+0x1fc]==9`, si no 0 | `0x43811192..9c`, `strb r3,[sp,#0x21]` |

Los cuatro `strb` con desplazamiento `0x655` de toda la imagen son `0x4389cc28`, `0x438c79e2`, `0x438c82bc` y `0x438c87f0`; el primero copia
bytes de una estructura a **otro** objeto (`FUN_4389cb8c` lo obtiene con la clave `0x9405`, no es el contexto), así que no alimenta este
bloque. Quedan 14 `str`/`strh` con desplazamiento `0x654` (`e3_params9.json`) que también tocan `+9`; no se confirmó el tipo de objeto de
cada uno. Los valores 2 y 3 (el 2 es la rama propia de A6000, ver S207) no tienen constante directa. Nuevo pendiente E14.

### E4 — modos `+8` de la cola `0x40193`
Los manejadores LIRO (`0x4379e47c` y hermanos) escriben el modo en una traza `0x3001` y lo reenvían a `0x4379d838`. Dos consumidores
cercanos lo indexan: `0x4379d364` lee la tabla booleana `0x43ca530e` (modos 0–10: `0,0,1,1,0,1,1,1,1,1,0`) y `0x4379d378` clasifica por
máscara de bit (`0x708` → 1; `0xf3` → 0; modo 2 → dependiente de dos consultas `0x43aea220`; mayor de 10 → traza de error). Los códigos de los
ocho wrappers (`0xc/0xb/0x14/0xa` y `0x6/0x5/0xa/0x4`) **no** están todos en 0–10, así que no se demostró que usen esa tabla. El nombre de cada
modo sigue sin establecerse.

### E5 — `S[0]=&G` (A7S) y lector `+0x238` (A6000)
Barrido sobre las anclas PIC (par `ldr`/`add pc`): A6000, 262 anclas al bloque `0x43edf684` y un único acceso a `+0x238`, el
almacén del manejador `0x40e3` (`0x438032dc`); no hay lector. A7S, 73 anclas a `S=0x43ea70a0` y **ningún** almacén en `[S+0]`; no existe
palabra absoluta con `S` ni `G` en la imagen. Ausencia acotada a las anclas PIC con ventana de 16 instrucciones; un acceso con base
calculada de otra forma no se descarta. Se cierra con ese límite.

### E7 y E8 — objeto de configuración `0x43f72d02` (Backup `0x3000b`)
Barrido de todas las cargas del slot GOT `0x4401f990` (`0x4401eee4`+`0xaac`): **14 sitios**, no los dos de S176, que leen 18 desplazamientos distintos
(`+0x0/1/2/4/5`, `+0xf`, `+0x1c/1e/1f`, `+0x22/24`, `+0x2e`, `+0x39/3a/3b`, `+0x51`, `+0xa3`, `+0xac`) y **ninguno escribe**. Por esa vía el contenido
solo lo produce el callback de copia de Backup (S305, 256 B, §4 de S402), así que E7 queda cerrado en lo estático; los valores efectivos de una
cámara concreta solo existen en ejecución. Detalle por sitio en `static_findings.json` (clave `E7`).

Lectores de E8 (los dos de S176):
Cadenas de llamadores (BL/B.W comprobados): lector 1 `0x43861400` ← `0x437b5e70` ← `0x43aef444` ← `0x4379210c`; lector 2 `0x438690dc` ←
`0x43844e80` ← `0x437b5b14`, la rutina que S42 usa como origen del bloque `B=0x43eae270` (copiado a `G`, la entrada del selector). El lector 2 está,
por tanto, en la ruta de parámetros de captura; la activación efectiva sigue sin observarse.

### E12 — receptores del mensaje de `0x437b0390`
`0x437b0390` reserva 20 B en el buzón `0x0110027c` (`0x435612d0`) y lo envía (`0x4356120c`) con tipo 3 y subtipo `0x22`. Esa constante
aparece **13** veces, todas en pools de emisores (13 pares reserva/envío; 9 en funciones que REA reconoce); no existe `movw/movt` con ella. El receptor no
referencia el buzón por literal, así que se identifica por el registro de tareas, no localizado. Sigue PARCIAL.

### Sin avance: E1, E6, E9, E10, E11, E13
E1 y E10 conservan su límite (ver [S402](static-closure-2026-10-25.md)). E6, E9, E11 y E13 dependen de traza en bus, hojas de datos o
traducción banco/bit del hardware.

## Pendientes nuevos

- **E14:** origen de los valores 2 y 3 de `params[+9]` (14 escritores anchos a `+0x654` y el campo `[r4+0x1fc]` de `0x4381106c`).
- **E15:** receptor del buzón `0x0110027c` por registro de tareas.
- **D6:** 7 trazas con homólogo en A7S cuya rutina REA no resolvió (hilos Thumb sembrados) y 77 sin homólogo textual.

## Adenda 26-10-2026 (E8)
**E8** ([e8_alcance.py](../../analysis/s403_pendientes/e8_alcance.py) → `e8_alcance.json`, prueba `tests/test_s403_e8_alcance.py`): de los 14 sitios que leen el objeto `0x43f72d02`,
7 cuelgan, por llamadores directos hasta 7 niveles (REA), de las raíces de captura `0x437b5b14`, `0x438c7800` y `0x438c828c`: los de las rutinas `0x438363cc` (campos `+0x39/3a/3b`), `0x43857f88`, `0x43857fa8`,
`0x4385812c` (`+0x0`, `+0x4`), `0x43858190` (`+0x4`, `+0x1c`), `0x43859710` (`+0x1/2/5/0x1f/0x24/0x2e`) y `0x43859944` (`+0x5`, `+0xf`, solo hacia SetExposure). Los otros 6 (`+0x22`, `+0xa3`, `+0xac`, `+0x1c/0x1e`) y el sitio `0x438e7088` (rutina sin ubicar) no.
Los valores efectivos y la activación son datos de la cámara (Backup `0x3000b`), solo observables en ejecución. E8 se cierra con ese límite.

**E4** ([e4_trig.py](../../analysis/s403_pendientes/e4_trig.py) → `e4_trig.json`, prueba `tests/test_s403_e4_trig.py`): `0x4379d378` es `IsNeedForceS1ON(trig)`: su rama de error imprime
`[IMAGING_REL]: it is a strange trig in IsNeedForceS1ON : %d` (`0x4379d3b8`) cuando `trig > 10`. Los dos llamadores (`0x4379da66`, `0x4379db72`, dentro del despachador `REL_EVT` `0x4379d838`) le pasan el campo `+0x10`
del registro de evento, que los manejadores LIRO rellenan con el byte `+8` del mensaje de `0x40193` (§3 de S402). Clasificación: fuerzan S1 los `trig` 3, 8, 9 y 10; no lo fuerzan 0, 1, 4, 5, 6 y 7; el 2 depende de dos consultas de estado (`0x43aea220`
con 0xb y 0x13). La tabla booleana `0x43ca530e` (`0,0,1,1,0,1,1,1,1,1,0`) la lee `0x4379d364`, que su único llamador (`0x4379e13e`) indexa con el resultado de `0x43aea264`, no con el `trig`. Los códigos `0xb`, `0xc`, `0x14`, `0x15` de los wrappers no
se demostró que lleguen a `IsNeedForceS1ON`. Queda sin establecer qué evento físico representa cada `trig`. E4 se cierra con ese límite.

## Adenda 26-10-2026 (D6, D3)
**D6** ([d6_homologos.py](../../analysis/s403_pendientes/d6_homologos.py) → `d6_homologos.json`, prueba `tests/test_s403_d6_homologos.py`): las 7 trazas con homólogo en A7S cuya rutina REA no ubicó (S605 ×2, S606 `bt stop`, S607 `s_request is NULL`,
S611 `SA_LPF/SA_BGEST/SA_SSP`) se ubicaron tomando el `push {…, lr}` anterior a la referencia PIC, y se compararon con el mismo motor que D3. Ninguna es igual salvo líneas (p. ej. 97 frente a 52 instrucciones en la rutina de S605 y 83 frente a 47 en la de S611).
Con ellas, las 17 trazas que tienen homólogo textual quedan comparadas y ninguna coincide a nivel de instrucciones. Las 77 restantes no tienen homólogo textual y se declaran sin homólogo. Límite: el inicio de rutina por prólogo es heurístico.
**D3** queda cerrado con límite: logger dual sin respaldo estático en 19 fichas (3 verificadas), equivalencia de código refutada en las 17 comparadas, 77 trazas sin homólogo; la equivalencia funcional no se decide con código.

## Adenda 26-10-2026 (E16)
**E16** ([e16_entradas.py](../../analysis/s403_pendientes/e16_entradas.py) → `e16_entradas.json`, prueba `tests/test_s403_e16_entradas.py`): las 10 rutinas entre `0x43841bf8` y `0x43842440` que leen `[0x43eefb1c+0x60]` (selector `0x43842158`,
getter `0x43842404` y vecinas) tienen un grafo de llamadores finito: 26 nodos y **6 raíces** (`0x43b1ae2a`, `0x43b1aea2`, `0x43b1aeee`, `0x43b1b22e`, `0x43b1bc24`, `0x43b1ce6e`), ninguna con llamador directo y todas con una referencia por puntero
en tablas de la imagen (`0x44021968`, `0x44021000`, `0x440222f0`, `0x44020134`, `0x440223a4`, `0x44023408`). No hay más entradas, directas ni indirectas por puntero de palabra; sí pueden existir llamadas por registro calculado o desde rutinas que REA no ubica.
Quién invoca cada ranura es un dato de ejecución. E16 se cierra con ese límite; no cambia la decisión A/B/C=NO de S51.

## Adenda 26-10-2026 (D4, D1, E10, E1)
**D4** ([d4_resolve.py](../../analysis/s400_open_questions_triage/d4_resolve.py), casos `d4-*` de `manual_review.json`, prueba `tests/knowledge/test_open_questions_triage.py`): las 86 filas del triaje S400 que seguían pendientes se resolvieron una a una. Resultado final del historial: 518 filas, 364 descartadas y 154 con rectificación respaldada, **0 pendientes**.
Las 86 se repartieron así: 15 descartadas por resumen acumulado (README, STATE y checkpoints del carril B que listan varias sesiones), 9 por afirmación ausente en el destino (el informe destino no contiene la lectura rectificada), 15 por procedencia invertida, 3 por adyacencia o negación, y 44 con rectificación respaldada (S116, S307, S60 y S304 ya la llevan en el destino; S130, S41, S46, S57 ×2, S58-AE, S309, S310, S313, S302, S321 ×2, S334 con un aviso añadido al inicio; S605/S607/S616/S625/S627 por la auditoría S605–S627).
Cada rectificación respaldada cita el informe corrector con localizador y SHA-256, y los 218 tests de las sesiones implicadas (S116, S146, S170, S300–S341, S58, S59, S61) pasan. Los avisos se añadieron a 13 informes con redacción neutra para el extractor de relaciones del grafo, para no crear aristas nuevas. **Límite:** una rectificación respaldada acredita que el informe corrector la declara y que su prueba pasa; no recertifica el hallazgo corrector contra los bytes, ni lo físico.

**D1** ([d1_alcance.py](../../analysis/s403_pendientes/d1_alcance.py) → `d1_alcance.json` y `d1_alcance_estricto.json`, prueba `tests/test_s403_d1_alcance.py`): grafo de llamadas directas propio sobre el binario A6000 (64 797 inicios de función, 220 753 aristas BL/B.W, barrido por instrucción) y alcance hacia delante desde las tres raíces de captura de E8. Calibración: reproduce exactamente los 7 de 14 sitios que REA situó bajo esas raíces. De las 226 etiquetas pendientes del censo, **216 no tienen ningún emisor alcanzable** por llamadas directas (en el modo estricto, solo destinos con prólogo `push lr`, el resultado es idéntico) y **10 sí**: `[EXL]` (ya decodificada: comprobaciones de dimensiones de imagen), `[LGA]` (subetiqueta de `[CAMERA_MAIN_YC]`, `GetDfeDrvParam`, función `0x4389b320`, profundidad 4), `[CID]`, `[FILE_NUM]`, `[FSYSMODE]`, `[SIZE]`, `[STAT]` (campos de `[CAM_UTIL_SENS]`, función `0x43901d50`, profundidad 5; S625/S628/S629), `[IN1]`/`[IN2]` (campos de `[CAM_IMAGER]`, ZIT Merge) y `[MODE_SNR_BUS_THROUGH]` (nombre de modo dentro del error `[IMAGING_CAP]`, ya inventariado en S106; función `0x437f5a04`, profundidad 1). Ninguna de las nueve etiquetas de prioridad 1 (`[SDF_ERR]`, `[EVF]`, `[VSYNC]`, …) cuelga de la captura.
Las 10 son subetiquetas o campos de módulos ya conocidos, salvo `[EXL]`; ninguna es un módulo independiente. D1 se cierra con ese límite: **el grafo es un mínimo** (sin llamadas por registro, vtables ni colas OSAL, ni rutinas sin prólogo `push lr`), así que no prueba que las 216 restantes no se ejecuten durante la captura; prueba que no cuelgan de ella por código directo. Qué hace cada una sigue `NO_VERIFICADO`. Pista nueva: E18.

**E10** ([e10_topologias.py](../../analysis/s403_pendientes/e10_topologias.py) → `e10_topologias.json`, prueba `tests/test_s403_e10_topologias.py`): censo de las 300 llamadas a `createTopology`/`destroyTopology` (`0x420630`/`0x420656`) de `libObj.so` A6000 con propietario por vtable y lista de filas resuelta en 149 sitios, más las listas estáticas a las que apunta código por referencia PC-relativa. La fila `0x2a` (YC Effect→ObjStillRecorder) solo figura en listas de seis modelos de **edición**: `ModelBeautyEffect`, `ModelFocusRevision`, `ModelPaint`, `ModelRedEye`, `ModelRetouchArtFilter` y `ModelTrimming` (más `ModelPbCap` en reproducción, ya documentado en S14). `ModelStillRec` crea `[b0,b1,10]`, `[8,10,c6,c7]` y `[8,10]`: la captura llega al grabador por STILL_DATA (filas `0x8`, `0xb0`, `0xb1`), no por YC; `0xb4` no aparece en ninguna lista estática. Con esto se cierra el subpunto «creador del pin `0x2a` en disparo»: **no lo crea ningún modelo de disparo en las listas resueltas**. **Límite:** 151 de los 300 sitios tienen la lista en heap o en otro marco y no se resolvieron (E17); el propietario por cercanía de vtable es heurístico. El resto de E10 (productor de modo 1, formato YC y propiedad del buffer) sigue abierto.

**E1**: reintentado desde dos ángulos nuevos (sin cambios en el resultado). (1) Ninguno de los 92 sitios que llaman al constructor de ids `0x120168` pasa el modelo como constante: el modelo viene siempre de un registro. (2) De los 11 llamadores de `0x12d780` (nombre `@M…` → id), tres son la consola de pruebas `[AppTestcmd]` (`0x1002b6`, `0x100350`, `0x1003e8`; cadenas `model/` y `view/`), que toma el nombre de la línea de comandos; los otros ocho no tienen cadena inmediata. Ningún sitio nombra `@M0EF` ni `@M030`. E1 sigue `NO_VERIFICADO` por exclusión: un emisor sería de datos o de ejecución (p. ej. la consola `[AppTestcmd]`).

## Adenda 26-10-2026 (2) (E18, E17, E10b, E1)

**E18** ([e18_dfe_param.py](../../analysis/s403_pendientes/e18_dfe_param.py) → `e18_dfe_param.json`, prueba `tests/test_s403_e18_dfe_param.py`): `[LGA]` es el mensaje de error de `0x4389b320`. La función llama dos veces a `GetDfeDrvParam` (`0x43ae92ee` → `0x4381b4b0`, copia `0x28` bytes de un registro DFE) y suma los u16 de los desplazamientos `+0xa`, `+0xc` y `+0xe`: el primer id es la constante `0xb` (resultado en `this+0x114`) y el segundo sale de `r8+0x6a4` (resultado en `this+0x116`); si la consulta falla guarda `0xfc4`. Además copia dos bytes del tercer argumento (`+6`, `+7`) a `this+0x118` y `this+0x11a`. El id se traduce por la tabla de `0x4381b3d4` (69 entradas) y por el `tbb` de `0x436d0234` a siete registros estáticos de la imagen. El id `0xb` resuelve a `0x43bb92b4` con campos `4`, `4` y `0xfb8`, suma `0xfc0`; 13 de los 69 ids caen en registros estáticos (sumas `0x23e`, `0x2c4`, `0x326`, `0x474`, `0xec`, `0xfc0`). **Límite:** son los valores iniciales de la imagen; no se ve si el controlador los reescribe en ejecución, y qué id pasa cada modo (`r8+0x6a4`) queda como E19.

**E17 y E10b** ([e17_listas.py](../../analysis/s403_pendientes/e17_listas.py) → `e17_listas.json`, prueba `tests/test_s403_e17_listas.py`): evaluador simbólico lineal sobre los 151 sitios sin lista. Las listas que `createTopology` recibe se completan de cuatro maneras: pila, heap (`operator new[]`), proyección del miembro `this+off` desde las tiendas de la clase y filas dinámicas. Una fila dinámica es el resultado de `0x420688` → `0x415e8c`, que busca la primera de las 210 filas (tabla de `0x20` bytes en `0xcc4210`) cuyo descriptor coincide en los ocho campos (`0x415c54`); con campos de ejecución se informa el conjunto de filas candidatas (hasta 16; si hay más se anota `?`). El propietario pasa a ser vtable, luego llamadores (todos los llamadores etiquetados de la misma clase) y por último cercanía. Resultado: 72 de 151 sitios resueltos (8 pila, 15 heap, 43 miembro proyectado, 2 estáticas con fin `-1`, 4 listas nulas); quedan 79 (51 miembros sin tienda estática, 16 sin valor, 4 de heap dinámico, 4 de miembro de otra base, 4 con puntero devuelto por `0x415f30`).
- **E10b:** `ModelStillRec` (6 sitios), `ModelMovieRec` (8), `ModelBootEE` (2), `ModelBootEE3D` (2) y `ModelCamera` (2) quedan resueltos al 100 % y ninguno contiene las filas YC `0x2a` ni `0xb4`. `0xb4` solo lo crea `ModelScalarPb` (reproducción): el método `0x65a8a4` publica `[fila dinámica, 0xb4, 0]` con el tipo `0x109` (ya descrito en S402) y pertenece a esa clase porque solo lo llaman métodos suyos. `createTopology` (`0x420630`) y su implementación (`0x41a26c`) no tienen punteros en los datos y la implementación solo se llama desde ese envoltorio: no hay otra vía de conexión de filas por llamada directa. **Límite:** `ConnectPin` (`0x41c25e`) no tiene llamadores directos ni punteros absolutos, así que una conexión por vtable o por offset relativo no queda excluida; el grafo de llamadores es mínimo.
- Lo que queda de E10 (escritores de modo 1, arbitraje de `StsViewer`, formato YC y liberación tras `CBID_ENCODE_STILL`) pierde urgencia para el disparo, porque no hay fila YC hacia el grabador, pero no se cierra por ello.

**E1**: sin cambio. Búsqueda de bytes en los 4,6 GB extraídos: el literal de 32 bits (little-endian) de `0x120EF004` no aparece en ningún archivo, y el de `0x12030002` solo en la partición Android (`SmartRemote.odex` y similares, coincidencia). Control positivo: el entry `0x43541000` sí aparece en `av-cam.bin`. Como el id se construye en ejecución (`0x12000000 + modelo<<12 + local`), la ausencia del literal es compatible con un emisor de ejecución; sigue `NO_VERIFICADO` por exclusión.

**Pendiente nuevo:** E19 (id DFE por modo, `r8+0x6a4`).

## Adenda 26-10-2026 (3) (E19, E17, E10 resto, E1)

**E19** ([e19_escritores.py](../../analysis/s403_pendientes/e19_escritores.py) → `e19_escritores.json`, prueba `tests/test_s403_e19_escritores.py`): el lector `0x4389b384` (`ldr r0,[r8,#0x6a4]`) recibe `r8` de `0x4389b3fc` y `0x4389b80c`, que se alcanzan por dos saltos `b.w` desde `0x437d8612` y `0x437d856e`. Los otros lectores del campo (`0x438eff48`, `0x438a6fb0`, `0x43889e94`) pasan el mismo valor a `0x43ae92ee` (id DFE) y leen también `+0x570`, `+0x590` y `+0x6a8`. De los 10 escritores `str.w` de 32 bits del campo, 7 están en el bloque de modo (escriben también `+0x6a8` o `+0x738`; el lector `0x438eff48` lee `+0x6a8`) y guardan siempre la constante **1**; uno es un reinicio masivo (`0x4380d2d0`, valor 0) y dos pertenecen a una matriz de paso `0x74` (`0x4376cf46`, `0x4376d1c8`). El id 1 resuelve al registro estático `0x43bb9264` (suma 574 = `0x23e`, E18). Límites: evaluación lineal (el escritor `0x43550298` se verificó a mano porque la rama `bne 0x43550292` salta la definición lineal), identidad de estructura probable pero no demostrada (los siete escritores son manejadores de estado cuyos punteros están en tablas de la imagen, `0x44022478`, `0x4401f6bc`, `0x44020ae0`, `0x44020064`, `0x44020e70`, `0x44021a2c`, `0x44025530`; el lector recibe `r4+0x20` en `0x438cc66c`) y registro inicial de la imagen. E19 se cierra con ese límite.

**E17** ([e17_listas.py](../../analysis/s403_pendientes/e17_listas.py), ahora con `descarte` por sitio): los 79 sitios sin lista llevan motivo: 44 son vectores de registros en `this+0x9c` armados en bucle por la base `ModelMediaBase` (el generador `0x42a448` copia el primer campo de cada registro de `this+0x9c`, que se rellena fuera de la función), 16 dependen de una rama que el evaluador lineal no sigue, 8 son listas dinámicas, 4 punteros guardados en un miembro, 4 `std::vector` de las clases `ModelDaNeutral` y `ModelRecPbNeutral` (`this+0x84`) y 3 miembros sin tienda estática. Ninguno es de un modelo de disparo (`sin_resolver_de_disparo` = 0). E17 se cierra con ese límite.

**E10 (resto)** ([e10_vtable_refs.py](../../analysis/s403_pendientes/e10_vtable_refs.py), [e10_resto.py](../../analysis/s403_pendientes/e10_resto.py) → `e10_resto.json`, prueba `tests/test_s403_e10_resto.py`): `e10_vtable_refs` localiza, para 3134 de las 3238 vtables de `libObj.so`, las funciones que cargan su base desde la GOT (el constructor suma 8).
- **Escritores de `EffectInternalMode=1`:** `ExecCmdAppFaderEfctEndEvt` (`0x154990`) solo se crea en la fábrica de `ComponentMovieRec` (`0x152168`, llamada desde `0x1521c8`); `SequencePinDeliverBase` (`0x1e069c`) solo se alcanza por las subclases `StillEditBase`, `BigImageOpen`, `VgaCache` y `SplitResizeImage`, todas de reproducción o edición. Ninguno pertenece a los modelos de disparo de fotos.
- **`StsId=6`:** son solo las filas `0x2a` y `0xb4`. Los modelos de disparo usan StsId {0} (`ModelBootEE`, `ModelBootEE3D`, `ModelCamera`), {0, 2} (`ModelMovieRec`) y {1} (`ModelStillRec`), así que el arbitraje del `StsViewer` de ese grupo no se ejerce en disparo.
- **Conexión fuera de la topología:** `ObjIf::ConnectPin` solo se llama en `TopologyLifeCycle` (`0x41c25e`) y en una orden de texto con `StrICmp` (`0x901680`); el grabador (`0x916afc`) acepta entradas de tipo 0 (`this+0x64`) y 9 (`this+0x74`) según el mensaje de conexión.
- **Liberación:** `StillConverter` libera su memoria de trabajo (8 funciones con `DmmFree`, `DmmCloseAndFree` o `BufFree` entre `0x91e000` y `0x920400`); el manejador de `CBID_ENCODE_STILL` (`0x91eb60`) no libera nada y envía un mensaje. El YC de entrada no lo libera el conversor.
- **Sin resolver:** `unitType`/formato del YC de Camera (sin fila hacia el grabador, no hay punto de medida; el catálogo `dmm-unit-types.json` no lo nombra). E10 se cierra con ese límite.

**E1**: sin vías estáticas nuevas. Todos los emisores posibles de `0x120EF004` y `0x12030002` son de datos o de ejecución.

## Adenda 26-10-2026 (4) — auditoría integral del repositorio

Herramienta: [repo_audit.py](../../scripts/audit/repo_audit.py) (prueba `tests/test_repo_audit.py`) → [estado.json](../../knowledge/audit/estado.json) (hallazgos mecánicos) y [memoria.json](../../knowledge/audit/memoria.json) (memoria temporal: pendientes por ID, fechas de los documentos de estado y comprobaciones de coherencia). Alcance: los 23 702 archivos versionados, con comprobaciones mecánicas; no se leyeron uno a uno.

- **Git:** `HEAD` = `origin/main` = `e0c74d13`; el flujo «Publicar estado» terminó con éxito; repositorio público; ramas remotas `copilot/*` ya fusionadas.
- **Suite completa tras los cambios:** 3 582 aprobadas, 35 omitidas, 0 fallos, 1 168 subpruebas, 561 s (3 617 colectadas; 9 más que la ronda anterior: 4 de utilidades de s403, 2 de `build_pages_status` y 3 de la auditoría). Las líneas añadidas a los documentos desplazaron los números de línea del triaje S400; se reasentaron con `extend_triage.py` (518 filas, 0 pendientes).
- **Sin fallos:** 3 108 JSON y 1 248 Python versionados se leen sin error; las sumas SHA-256 de los volcados de cámara (128 archivos) coinciden (cada `SHA256SUMS` lleva una línea de autorreferencia con hash de archivo vacío, ignorada).
- **Discrepancias halladas y resueltas:** documentos de estado sin rastro del 26-10 (D7); tres rutas citadas inexistentes y una cifra de pruebas de S68 (D8); ocho utilidades de `s403_pendientes` sin prueba (tres cubiertas con `tests/test_s403_utilidades.py`; `pic` y `rq` se prueban desde otros módulos; `d3_*` y `e3_params9` desde `test_s403_static_findings.py`) (C5).
- **Discrepancias abiertas, registradas en [PENDIENTES](../PENDIENTES.md):** `libmprctrl.so` de Sony versionado en un repositorio público (R3), cuatro `.zip` obsoletos en la raíz (R4), nueve archivos versionados que `.gitignore` ignora (R5), 11 herramientas fuera de línea sin prueba por nombre (C7), una prueba que reescribe archivos versionados de `site/` (C8) y la etiqueta `[EXL]` alcanzable desde la captura (E20).
- **Cifras que difieren y no se reescriben (D9):** 12 menciones «N pruebas» de informes históricos frente a lo colectado hoy.
- **Límite:** las comprobaciones son mecánicas (existencia de enlaces y rutas, validez de JSON/Python, estados, fechas); no validan el contenido técnico de los informes ni re-ejecutan el análisis de bytes.

## Adenda 26-10-2026 (5) — cierre de los pendientes de la auditoría

- **E20 (estático, cerrado con límite):** [e20_exl.py](../../analysis/s403_pendientes/e20_exl.py) → `e20_exl.json` (17 instrucciones decisivas, comprobadas contra los bytes por `tests/test_s403_e20_exl.py`). `[EXL]` sí puede rechazar una captura: `hsiz_arcout > 2240` (`0x8c0`), `arcout > arcin` y `hsiz_sig > 2240` registran el aviso y ponen a 0 la bandera de retorno de `0x436ca820` (y `0x436cafc0`, sin la comprobación de `hsiz_sig`). La bandera sube por `0x43ad5b02` y `0x43ad5998` hasta `0x436c25d0` (`cbz` → `movs r0,#7`), que sale sin ejecutar el resto; `0x43acc424` devuelve el 7 y `0x437f5a04` lo registra como `snrBusThroughPrereviewParamSet Error!` y aborta. Límite: no se evaluaron las dimensiones de cada modo de disparo, así que no se sabe si algún modo real pasa de 2240.
- **C8:** `build_pages_status.py` acepta un directorio de salida y la prueba escribe en uno temporal; la suite deja de ensuciar `site/`.
- **C7:** `tests/test_s404_herramientas_offline.py` (11 pruebas sintéticas) cubre las 11 herramientas fuera de línea.
- **R3a, R4, R5:** `libmprctrl.so`, los cuatro `.zip` y seis registros `*.log` salen del índice (copias locales conservadas) y se ignoran; los tres `raw305*.jsonl` se conservan con excepción en `.gitignore`. El historial de git aún contiene `libmprctrl.so` (R3): reescribirlo es decisión del usuario.
- **D9:** sigue descartado (cifras históricas).

- **Suite completa:** 3 595 aprobadas, 35 omitidas, 0 fallos, 1 168 subpruebas, 576 s (3 630 colectadas); el árbol de `site/` y `docs/progress/` queda intacto tras correrla (C8). Se lanza con `pytest tests`: `pytest` sin ruta choca con el nombre duplicado de `analysis/s300_state_xref_sweep/test_s300_state_xref_sweep.py`.
- 27-10-2026 (6): E20 llega a su límite estático (salida acotada a 2208x1242; los rectángulos de entrada se arman en ejecución); R2 cerrado con `.github/workflows/tests.yml` y `tests/conftest.py`; R3 preparado en clon aparte con `scripts/r3_prepare_history_rewrite.sh`, sin `push --force`.
