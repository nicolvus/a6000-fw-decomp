# S2, captura nativa y punto de bifurcación — investigación directa del principal (sesión 17)

Alcance: análisis estático exclusivo de LIRO (`av-cam.bin`, fw 3.21, SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`, 11 427 236 bytes). Base de carga asumida `0x43540000` (verificada leyendo bytes crudos: offset de archivo = vaddr − `0x43540000`, confirmado en `0x437eabfc`). No se afirma que SilentShutter funcione. No hay cámara conectada ni flasheo. Herramienta: Ghidra headless `-noanalysis -readOnly` sobre el proyecto compartido `silent-liro`, script `QuerySilentLiro.java`/`QuerySilentReferences.java`, proceso `av-cam.bin`. Continúa directamente la "Siguiente tarea sugerida" de `docs/capture/shutter-trigger-state-machine.md` (sesión 16): resolver el consumidor de la cola `0x40193` y las cinco palabras reales del descriptor instalado por `0x437eabfc`.

Clasificación: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.

## 1. Decompilado completo del selector `0x437eabfc` (nuevo, VERIFICADO)

Sesión 16 solo tenía "copia cinco palabras de una fila" de la tabla `GOT[0x44022934]=0x43edccf8`. Esta sesión decompila la función completa:

```c
undefined4 * FUN_437eabfc(undefined4 *param_1, undefined4 param_2)
{
  iVar1 = FUN_43ae75dc(param_2);
  iVar4 = DAT_44022934;                         // = 0x43edccf8
  if (*(int *)(iVar1 + 0x4b70) == 0) {
    if (*(char *)(iVar1 + 0x54a5) == '\0') {
      if ((*(int *)(iVar1 + 0x70) - 8U < 6) && (*(int *)(iVar1 + 0x1d8) == 0)) {
        puVar6 = (undefined4 *)(DAT_44022934 + 0xb4);           // fila índice 9
      } else {
        if (*(int *)(iVar1 + 0x1e0) == 7) {
          iVar7 = (*(int *)(iVar1 + 0x1d8) == 0) ? 10 : 0xd;     // fila 10 ó 13
        } else if (*(int *)(iVar1 + 0x1e0) == 0x17) {
          iVar7 = 8;                                             // fila 8
        } else if (*(int *)(iVar1 + 0x1d8) == 0) {
          iVar7 = 8;
        } else {
          iVar7 = 0xb;                                           // fila 11
        }
        FUN_43ae76ca(iVar1, 0, iVar7);
        puVar6 = (undefined4 *)(iVar7 * 0x14 + iVar4);
      }
      goto LAB_437eac8a;
    }
    iVar4 = (*(int *)(iVar1 + 0x54a8) == 0) ? 0xa0 : 0xf0;        // fila 8 ó 12
  } else if (*(int *)(iVar1 + 0x4b70) == 7) {
    iVar4 = 300;                                                  // fila 15 (0x12c)
  } else {
    iVar4 = 0x118;                                                // fila 14
  }
  puVar6 = (undefined4 *)(DAT_44022934 + iVar4);
LAB_437eac8a:
  // copia las 5 palabras (0x14 bytes) de *puVar6 a param_1[0..4]
  ...
  return param_1;
}
```

**VERIFICADO:** el selector es un árbol de decisión de 4 niveles sobre los campos de la petición de captura:
1. `+0x4b70` (¿cero?) separa "captura ordinaria" de dos ramas con `iVar4` fijo (`0x118` o `300`, filas 14/15) cuando es distinto de cero — candidatas a vídeo/ráfaga especial (no exploradas aquí).
2. Si `+0x4b70==0` y `+0x54a5` (flag byte, antes documentado como ráfaga/contexto) es distinto de cero, usa `+0x54a8` para elegir entre fila 8 (`0xa0`) y fila 12 (`0xf0`).
3. Si `+0x54a5==0`: comprueba `(+0x70 − 8) < 6` (es decir `+0x70 ∈ {8..13}`) junto con `+0x1d8==0` → **fila 9 (`0xb4`)**, un caso especial sin paso por `FUN_43ae76ca`.
4. En el resto, usa `+0x1e0` (7 ó 0x17) y `+0x1d8` para seleccionar filas 8, 10, 11 ó 13, y **sí** llama antes a `FUN_43ae76ca(iVar1,0,iVar7)` — una función de "preparar/confirmar" por índice que no se decompiló en esta sesión (bloqueo declarado).

**INFERENCIA:** los campos `+0x70` y `+0x1e0` son los mismos ya documentados en sesión 16 (`0x437e067c normaliza tipo de captura` y similares); el valor `7` repetido en `+0x1e0` y el valor `0x1d8==0` (ya visto en `0x437df338` como "número de imágenes"/"primera activación") sugieren que la fila 9 (`0xb4`, caso directo sin `FUN_43ae76ca`) corresponde a un tipo de captura de "una sola imagen, primera activación" — compatible pero NO idéntico al disparo S2 ordinario. No se identifica aquí ninguna fila como "modo electrónico" explícito.

**DESCARTADO:** que la selección dependa de algún flag Silent/EFCS — las ocho condiciones observadas son enteramente de tipo de captura (RAW/no-RAW, ráfaga, número de imágenes), no de modo de obturador.

## 2. La tabla `0x43edccf8` es BSS, cero en la imagen estática (nuevo, VERIFICADO — explica el bloqueo, no lo resuelve)

Leyendo directamente los bytes de archivo en las 8 filas candidatas (índices 8, 9, 10, 11, 12, 13, 14, 15; offsets `0xa0, 0xb4, 0xc8, 0xdc, 0xf0, 0x104, 0x118, 0x12c` desde `0x43edccf8`), **las 8 filas son exactamente cero (5 palabras × 4 bytes = 0 en las 8)** en el binario `av-cam.bin` tal como se distribuye.

**VERIFICADO:** esto confirma y precisa la nota de sesión 16 ("la tabla reside después del intervalo tratado como constante... su contenido inicializado... no se identifica como lista de etapas"): la tabla vive en una región BSS que el firmware rellena en tiempo de ejecución (probablemente desde una tabla de constantes de otro módulo, o calculada), **no** en la imagen estática analizable. Por tanto el contenido real de las cinco palabras por fila (candidato a "lista de etapas mecánicas" o similar) **no es recuperable por análisis estático de este binario** — es un bloqueo de método, no solo de tiempo.

## 3. Búsqueda del consumidor de la cola `0x40193` (parcial, nuevo intento — sigue NO VERIFICADO, pero se descarta un candidato)

Sesión 16 dejó pendiente: "localizar el receptor desde `0x43809ed8` hacia atrás... o seguir desde el destino `0x4380db04` (mensajes `0x104/0x141`)".

**VERIFICADO (Ghidra, referencias estáticas):**
- `0x43809ed8` (la función que construye el callback `CaptureStart` vía `GOT[0x44021ed0]=0x437df641` y lo entrega a `FUN_439018b0`) **no tiene ninguna referencia de llamada directa** registrada por Ghidra en modo `-noanalysis`. Tampoco aparece como literal de puntero (`0x43809ed8`/`0x43809ed9` con bit Thumb) en ningún punto de los 11 427 236 bytes del binario. Es decir: se invoca indirectamente, por una ruta que el análisis sin resolver de llamadas indirectas/vtablas no puede ver, o su dirección se calcula (no se copia como literal).
- `0x4380db04` (instala el mismo callback para mensajes `0x104/0x141`) **sí** tiene un llamador directo: `0x43792a0c`, en la instrucción `0x43793ec4`.

**Intento de identificar `0x43792a0c` como el consumidor de `0x40193`:** decompilé la función completa (28 973 caracteres, muy grande — maneja logging extenso con cadenas `"vfc...shut...zaf..."`, compatible con un manejador central de captura/obturador). Contiene dos referencias literales a `0x30001` (como argumento de `FUN_43a49628`/`FUN_435aa20c`, funciones de mensajería no decompiladas en esta sesión) pero **cero referencias literales a `0x40193`**.

**Consecuencia (VERIFICADO, por ausencia):** `0x30001` es, según sesión 16, el **origen** (remitente) que RelMgr usa al enviar `0x3011` a la cola `0x40193` — es decir, es el identificador de RelMgr, no la cola de CaptureManager. Que `0x43792a0c` opere sobre el mailbox `0x30001` es compatible con que esta función **envíe mensajes de vuelta a RelMgr** (respuestas/avisos), no con que sea el lector de la cola `0x40193`. **NO VERIFICADO** que `0x43792a0c` sea el consumidor de `0x3011`; de hecho la ausencia de `0x40193` en su cuerpo es evidencia (parcial, no decisiva por posible uso de constantes calculadas) en contra de esa hipótesis. **DESCARTADO** como candidato principal, sin descartar que sea un participante secundario (receptor de confirmaciones) en la misma máquina de estados.

**Bloqueo persistente, ahora mejor acotado:** el consumidor real de `0x40193` sigue sin localizarse. Las dos rutas abiertas por sesión 16 (`0x43809ed8` hacia atrás, `0x4380db04` hacia atrás) han sido ambas recorridas esta sesión sin éxito: la primera no tiene llamador estático visible (candidato a llamada indirecta/vtable); la segunda llega a una función de logging/mensajería genérica sin relación textual con `0x40193`.

## 3bis. Callers reales de `0x43809ed8` encontrados por desensamblado directo (nuevo, VERIFICADO — corrige el "sin referencias" de Ghidra)

La consulta de referencias de Ghidra en modo `-noanalysis` (§3) no encontró llamadores de `0x43809ed8`. Repetí la búsqueda con `llvm-objdump -d --triple=thumbv7-none-eabi` sobre todo `analysis/av-cam-analysis-view.elf` y **sí aparecen 7 instrucciones `bl 0x43809ed8` reales**, agrupadas en dos funciones:

- **`0x43807d80`** (4 sitios de llamada, en `0x43807e74/eb4/eee/f2a`): decompilada por completo. Es un manejador de transición de estado de una tecla/disparador: según el resultado de varias comprobaciones (`func_0x43b02142/219c/213a/228c`, `FUN_43b01676`), unas ramas llaman a `func_0x43809ed8(*(param_1+0xc), *(param_2+4))` antes de retornar, y las ramas finales construyen un valor `uVar4` igual a **`0x3013`** o **`0x3015`** que pasan a una etiqueta compartida `LAB_43b01ec4` (patrón de epílogo/tail-jump compartido entre funciones, visible por los `WARNING: Possible PIC construction`). **VERIFICADO:** la llamada real a `0x43809ed8` existe en este contexto de transición de tecla. **HIPÓTESIS (no confirmada):** que `0x3013`/`0x3015` aquí sean literalmente las mismas notificaciones a CamUser que documentó sesión 16 para `0x4379eb04`/`0x4379ea38` (coincidencia de constante, no de dirección ni de cuerpo de función — podría ser una coincidencia numérica de un espacio de IDs distinto).
- **`0x438089d4`** (3 sitios de llamada): decompilada por completo (13 632 caracteres). Es un **despachador de mensajes de un espacio de IDs completamente distinto**: maneja literales `0x300` a `0x331` (`0x300,0x301,...,0x331`, enumeración densa), y **no contiene ni `0x3011`, ni `0x30001`, ni `0x40193`** en ninguna parte de su cuerpo. **DESCARTADO:** que esta función sea el consumidor de la cola `0x40193`/mensaje `0x3011` — es una máquina de estados distinta (probablemente del lado CAIF/exposición, coherente con los rangos de ID que documenta `a6000-caif-event-dispatch.json`, no revisado aquí en detalle).

**Conclusión parcial (VERIFICADO + HIPÓTESIS):** `0x43809ed8` (instalación del callback `CaptureStart`) se invoca desde al menos dos sitios reales de código, ninguno de los cuales referencia literalmente `0x3011` o `0x40193`. Esto **no confirma ni descarta** el enlace `0x3011→CaptureStart`: demuestra que el callback se instala desde manejadores de transición de estado internos (teclas/disparador y despacho CAIF denso), consistente con que `0x3011` dispare una de esas transiciones indirectamente (p. ej. a través de una variable de estado compartida), pero sin una arista de llamada o literal que lo pruebe directamente. El bloqueo de sesión 16 ("consumidor de `0x40193` no localizado") **persiste**, ahora con dos candidatos adicionales explícitamente revisados y sin literal `0x3011`/`0x40193` en ninguno — reduce el espacio de búsqueda sin cerrarlo.

## 4. Cruce con PMCADemo (evento Java vs RelMgr nativo)

**NO VERIFICADO en esta sesión por el principal** (delegado a Claude B, que investiga la pila Android/JNI en paralelo): si `onShutterKeyDown()`/`onFocusKeyDown()` de `CameraActivity.java` (PMCADemo) llega a invocar, directa o indirectamente, el mismo `RelMgr::0x4379d838` nativo analizado aquí, o si pasa por una ruta Android/JNI completamente distinta (p. ej. `android.hardware.Camera` estándar) que nunca toca LIRO/RelMgr. Es la pregunta de cruce explícita del encargo de sesión 17; su respuesta depende del hallazgo de Claude B sobre la pila JNI, que se integrará en el veredicto final.

## 5. Respuesta a las preguntas del encargo

1. **¿Qué clase/función ejecuta la selección inicial?** `0x437eabfc`, ahora decompilada por completo — **VERIFICADO**.
2. **¿Qué pin/entrada utiliza?** No es un "pin" como en ObjEffect: es un conjunto de campos de la estructura de petición de captura (`+0x4b70, +0x54a5, +0x54a8, +0x70, +0x1d8, +0x1e0`), ya documentados individualmente en sesión 16 — **VERIFICADO** (estructura), sin nombres semánticos definitivos para cada campo.
3. **¿Cómo selecciona la fila?** Árbol de decisión de 4 niveles, documentado arriba — **VERIFICADO**, nuevo esta sesión.
4. **¿Existe una fila "electrónica"?** No se encontró ninguna marca de modo Silent/EFCS en la lógica de selección; el contenido real de las filas es BSS y no es recuperable estáticamente — **NO VERIFICADO** (ni se puede verificar sin volcado de memoria en caliente, fuera de alcance).
5. **¿Se identificó el consumidor de `0x3011`/cola `0x40193`?** No. Se descartó un candidato (`0x43792a0c`) con evidencia concreta (ausencia de literal `0x40193`, presencia de `0x30001` como mailbox de respuesta a RelMgr) — **NO VERIFICADO**, bloqueo persistente.

## NO VERIFICADO / siguiente bloqueo específico

- Consumidor real de la cola `0x40193` (requiere resolver la llamada indirecta a `0x43809ed8` — candidato: localizar la tabla de function-pointers o vtable que la contiene, posiblemente vía el mismo mecanismo de `TM::createLifeCycles`/callback que investiga Claude A en libObj, aunque aquí es LIRO, no libObj — mecanismos distintos, no asumir equivalencia).
- Contenido real de las 8 filas candidatas de `0x43edccf8` (imposible por análisis estático de este binario; requeriría volcado de memoria en caliente, que está fuera del alcance de este proyecto: "no hardware, no flasheo").
- Semántica exacta de `FUN_43ae76ca(iVar1,0,iVar7)`, llamada antes de seleccionar las filas 8/10/11/13 (podría escribir estado, no solo leer).
- Relación entre el evento Java `onShutterKeyDown` (PMCADemo/Android) y `RelMgr::0x4379d838` nativo — pendiente de integración con hallazgo de Claude B.

**Riesgo para el usuario:** ninguna de las rutas de esta sesión demuestra ni descarta una divergencia Silent segura en `0x437eabfc`; el candidato de integración de sesión 16 permanece como HIPÓTESIS sin refutar ni confirmar. No se tocó, flasheó ni ejecutó ningún binario.
