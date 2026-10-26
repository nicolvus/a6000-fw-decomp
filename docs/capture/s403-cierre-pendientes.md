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
