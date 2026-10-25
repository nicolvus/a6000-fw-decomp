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
