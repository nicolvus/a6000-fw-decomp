# S19-12 — Puntos de decisión antes de la captura mecánica

Alcance: Sony A6000 FW 3.21, análisis estático y local de
`av-cam.bin` mediante `llvm-objdump -d --triple=thumbv7-none-eabi` sobre
`analysis/av-cam-analysis-view.elf` (base LIRO `0x43541000`). Las direcciones
son VA LIRO. No se modificó ningún binario ni proyecto Ghidra, ni se usó una
cámara.

## Veredicto

**S19-12: PARCIAL.** Se identificaron guardas reales que impiden llegar a la
instalación/ejecución de la captura convencional y el selector que decide qué
descriptor LIRO se ejecuta. La condición más próxima a una decisión de
movimiento sigue siendo la **fila/descriptor de 20 bytes** escogido por
`0x437eabfc`; su contenido y la correlación de cada fila con CAIF/Darwin no se
pueden recuperar de la imagen estática. Por tanto, para evitar una captura
mecánica haría falta, como mínimo, que el evento no supere las guardas de
admisión **o** que el selector no ejecute un descriptor que alcance CAIF/Darwin;
no se verificó una alternativa electrónica completa ya activa.

EFCS es un selector de parámetros de exposición existente. No se equipara a
obturación totalmente electrónica: la ruta EFCS conserva programación de
exposición/lectura y no hay una prueba de que suprima ambas cortinas.

## Cadena y puntos de decisión

| Estado | Dirección / condición concreta | Resultado observado | Archivo / método |
|---|---|---|---|
| VERIFICADO | `0x4379e6a8` | RelMgr consulta el objeto de bloqueos por las ranuras `+0x18/+0x1c` para factores `1, 0xf, 0x11, 0x15`. Si la petición no es admitida, emite tipo 5 / `0x4045`; si lo es, `0x4379eba0` construye tipo 2 / `0x3011` hacia `0x40193`. Es una puerta previa a captura, no una prueba de la cortina. | `av-cam.bin`; LLVM y evidencia C previa en `shutter-trigger-state-machine.md`. |
| VERIFICADO | `0x43807f4c`, caso local `msg[0] == 0x100` | El dispatcher sólo deriva ese código a `0x43807d80`. El adaptador entre `0x3011/0x40193` y este dominio local sigue NO_VERIFICADO, así que no se puede afirmar que todo S2 atraviese esta puerta. | `av-cam.bin`; LLVM. |
| VERIFICADO | `0x43807d90..0x43807f40` | La llegada a `0x43809ed8` está condicionada por varios estados retornados por helpers del objeto de captura: rutas con retorno nulo/no nulo en `0x43b015ce`, `0x43b0228c`, `0x43b02142`, `0x43b0219c`, `0x43b0213a` y por `msg[+0xc] == 4` en `0x43807e4e..0x43807e52`. Fallar esas guardas toma limpieza, notificación o retorno, no el instalador. Los nombres semánticos de esos helpers/campos son NO_VERIFICADOS. | `av-cam.bin`; LLVM. |
| VERIFICADO | `0x43807e6c..0x43807e74`, `0x43807e8a..0x43807eb4`, `0x43807ee2..0x43807eee`, `0x43807f24..0x43807f2a` | Cuatro caminos alcanzan `CaptureStart` sólo con las combinaciones de estado respectivas: retorno de `0x43b0228c` nulo/no nulo, estado de `r4+0x1c` igual a 4 o 2 y, en una ruta, el puntero global `+0x30` no nulo. Las otras ramas salen por cancelación/limpieza o delegan a otro handler. | `av-cam.bin`; LLVM. |
| VERIFICADO | `0x43809ed8..0x43809f18` | El instalador no bifurca por modo de obturador: construye callback a `0x437df640` y llama `0x43b0172c(objeto,0)`. Por ello, un flag de Silent/EFCS no puede atribuirse a este punto por inspección directa. | `av-cam.bin`; LLVM. |
| VERIFICADO | `0x437df640`, `((cfg[+0x265] & 0x0f) >> 2)` | Valores 1, 2 y 3 se bifurcan a recorridos específicos; el resto llega a la llamada ordinaria `0x437df338` en `0x437df876..0x437df87a`. Para valor 2, `global+0x14 == 1` también llega a esa llamada (`0x437df79c..0x437df7a0`); de lo contrario toma el recorrido `0x301f`. Ésta es una selección de clase de captura, no una clasificación mecánica demostrada. | `av-cam.bin`; LLVM. |
| VERIFICADO | `0x437df338`, especialmente `0x437df49a..0x437df5d6` | Tras recursos y `ImageParamCapture`, crea `Image`, llama `0x437eabfc` y copia cinco palabras del descriptor seleccionado antes de `0x43b04730(Image)`, despacho indirecto de la etapa. Es el último selector comprobado antes de ejecutar la máquina de estados de captura. | `av-cam.bin`; LLVM. |
| NO_VERIFICADO | `0x437eabfc`, tabla `0x43edccf8` | Selecciona una fila con los campos de captura `+0x4b70,+0x54a5,+0x54a8,+0x70,+0x1d8,+0x1e0`. La tabla/filas no son recuperables desde la imagen estática y no existe correspondencia demostrada fila → primer comando CAIF/Darwin. Éste es el punto real que habría que resolver para decidir que el descriptor omitirá la secuencia mecánica sin romper el contrato `Image`. | `av-cam.bin`; desensamblado previo y LLVM. |
| VERIFICADO | `0x43842158`, campo de banco `+0x41c` | EFCS influye en clase de exposición: con `bank[+0x4bc] & 0xe0 == 0`, EFCS distinto de 1 produce clase 3; EFCS igual a 1 empieza en 1 y otros campos/umbral pueden devolver 3. La máscara/diagnóstico también permite otras clases. | `av-cam.bin`; recorrido estático conservado en `efcs-capture-selector.md`. |
| DESCARTADO | clase EFCS 1/2/3/5, `0x43842158` o `0x436d6f6c` | Ninguna de esas clases prueba que se omita una cortina. `SetExposure` sigue configurando el IMX210; clase 2 además modifica temporización/registros adicionales. EFCS no es obturación totalmente electrónica. | `av-cam.bin`; análisis previo contrastado. |
| VERIFICADO | `0x437db858(evento=1)` → `0x436b8a50` → `0x436ba234(0x10300,0x16,...)` | Hay una frontera concreta hacia CAIF: evento 1 empaqueta 22 bytes. En Darwin, helpers de cortina finalmente controlan P4D/P4E, pero no se vinculó cada descriptor LIRO a ese evento ni se probó que sea el primer compromiso mecánico para toda variante. | `av-cam.bin` y Darwin; LLVM / evidencia previa. |

## Condiciones necesarias derivadas

1. **Antes de CaptureStart:** la petición debe ser rechazada por RelMgr o por
   las guardas del dispatcher local, si y sólo si el dominio de evento concreto
   atraviesa dichas rutas. El puente `0x3011 → 0x100` permanece NO_VERIFICADO.
2. **Tras CaptureStart:** la clase de `cfg+0x265` debe evitar la rama ordinaria
   o conducir a una implementación que no ejecute un descriptor convencional.
   No hay evidencia de que las ramas 1/2/3 sean electrónicas.
3. **En la ejecución LIRO:** la fila resultante de `0x437eabfc` debe no emitir
   la transacción CAIF/Darwin de cortinas, conservando simultáneamente los
   contratos de exposición, lectura, finalización y limpieza. La condición de
   esa fila y su alternativa no se conocen todavía.

Esto es una lista de requisitos diagnósticos, no una receta de parche ni una
confirmación de que exista ruta sin cortinas.

## Límites

- **NO_VERIFICADO:** el receptor de `0x40193`, la relación exacta S2→`0x100`,
  la semántica de los helpers del dispatcher y cualquier flag explícito de
  “mecánico/no mecánico”.
- **NO_VERIFICADO:** que una fila concreta del selector alcance, evite o
  complete CAIF/Darwin; tampoco se conoce el balance de cancelación, esperas y
  recursos al omitirla.
- **HIPÓTESIS:** una divergencia segura, si existiera, debe estar en
  `0x437eabfc` o antes de ejecutar su descriptor, porque es el selector más
  cercano recuperado. No se debe modificar basándose sólo en esta hipótesis.
- SilentShutter no se declara funcional.

## Siguiente tarea propuesta

**S19-13 (d): cancelaciones y estados posteriores a S2.** Es la prioridad más
útil aún no resuelta: debe identificar qué mensajes/estados cancelan o liberan
una solicitud entre la admisión y las filas LIRO, y qué invariantes habría que
conservar si una rama evitara iniciar la secuencia convencional.
