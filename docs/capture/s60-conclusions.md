# S60 — conclusiones (Claude Sonnet 5.5 + GPT-6 Sol)

20-10-2026. Análisis estático y emulación offline. Sin firmware ejecutado en cámara, sin flasheo ni parche. A6000 SHA `b60c845c…bb9`; A7S 3.20 SHA `b857d338…5103e`. Informes: [Sol](s60-sol.md) · [Claude](s60-claude.md) · [validación cruzada](s60-cross-validation.md) · [matriz](../../analysis/s60-evidence-matrix.json).

## Resultados

1. **A6000 – emisor del payload (Sol, verificado por bytes).** `0x438069f0` es el despachador de una **tarea de mensajes** (`0x43806e38`, recv `0x3030f`, sin timeout). Los casos 4 y 10 son **respuestas** a peticiones 3 y 9 (`0x43b00fe6`/`0x43b00f62` → `0x43806400` → cola `0x8003030f`). Quien origina las peticiones 3/9 y el bit 31 del handle siguen sin resolver. Corrección mía: las entradas TBH son `…c28`/`…d06` (Sol: `…c24`/`…d02`).
2. **A6000 – origen de los 24 B `+0xdd0` (Claude, nuevo).** Equivalen a `obj+0xe20..0xe37` del registro de estado `obj+0xe04..0xe53`, escritos vía el accesor `0x43ae8504` por dos productores: A `0x437ab510` (6 pares idénticos de `obj+0x168/0x16a`) y B `0x43aecbfa` (5 pares de `obj8+0x48..0x5f` + sexto par por tabla `0x437a5a6c`). Son **6 pares (u16,u16)**; que sean M de temporización es **HIPÓTESIS**. `obj+0xe04` es un solo byte (`0x4376682c`). Tv/clk/N/svr/VdNum/modos 0x0B/0x2F: sin cambio (PARCIAL/NO VERIFICADO).
3. **A7S – mensajes `0x1000/0x1001` (Claude, verificado).** Son **registros de traza** de una API con 381 llamadores (`0x438f6864`): tipo 2/clase 3/carga 12 B a la cola `0x8f013a`, envío no bloqueante cuyo retorno se descarta. Su contenido es un **eco** de `SetExposure` (svd/shd/spl) y `SetRead` (ganancia). Silent no los emite; no sincronizan ni terminan la exposición. El **consumidor** de la cola no se localizó por referencia directa (PARCIAL).
4. **A7S – servicios.** `0x439b3918` = memcpy ARM; `0x438f7114` = printf de trazas; `0x43544270` = decodificador de estado→campos de sombra (tercer método de la cadena), efecto eléctrico no demostrado.

## Pruebas (resultados reales)

`tests/test_s60_claude.py` 12 OK · `test_s60_sol.py` 6 OK · regresión S56 26 OK, S57 34 OK, S58 23 OK, S59-Claude 9 OK, S59-Sol 11 OK (`analysis/s60/test-results.txt`).

## Límites

- **GPT:** la ejecución de investigación terminó por límite de uso (sin mensaje final; entregables previos presentes); la **auditoría cruzada de GPT no se obtuvo** (límite de uso hasta las 17:56). Los hallazgos de Claude C7/C8 y A7S no tienen contraste de GPT.
- El OSAL se sustituyó en el arnés (alloc/send); no demuestra el drenaje real de la cola.
- Inicio, duración, fin de integración, lectura, sincronía BIONZ–Darwin–DFE y movimiento mecánico: **NO VERIFICADO**.

## Decisión S51 (sin cambios)

**A = NO** (exposición completamente electrónica no demostrada) · **B = NO** (parche no justificado) · **C = NO** (imposibilidad física no demostrada).

## Siguiente investigación

1. Repetir la auditoría de GPT (`analysis/s60/sol-audit/task.md`) cuando se renueve el cupo.
2. Seguir los productores de `obj+0x168/0x16a` y `obj8+0x48..` (A6000) y el origen de la petición caso 3/9 (vtable de los emisores `0x43b00f26…`), con acotación de modos 0x0B/0x2F.
3. Localizar el drenaje de la cola de trazas A7S o descartarlo; física: traza pasiva autorizada.
