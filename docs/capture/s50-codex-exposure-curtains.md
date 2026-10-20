# S50 B — exposición y cortinas (Codex)

2026-10-19. Investigación estática de A6000 3.21. **Respuesta a la pregunta final: NO_VERIFICADO** que exista una foto nueva de resolución completa con inicio y fin electrónicos de exposición y sin cierre mecánico. Tampoco se ha demostrado una imposibilidad física del sensor. No hay parche ni captura funcional validada.

El resultado nuevo principal es una corrección de nomenclatura que afecta a la premisa: **los valores 1/2/3/6 de las filas de S49 son cantidades de callbacks, no clases de captura**. Se identificó además una omisión diagnóstica de peticiones CA con estados de cancelación/error, y se precisaron el envío inicial y la fila especial externa `+0x12c`.

## Alcance, fuentes y reproducibilidad

Todas las direcciones siguientes, salvo la tabla histórica Darwin expresamente indicada, corresponden a **`av-cam.bin`**, base de carga `0x43541000`, SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.

Se consultó primero el MCP de conocimiento (`get_current_state`, búsquedas exactas/conceptuales y `find_corrections`), después CURRENT, CONTEXT y las secciones pertinentes de S40–S49, E019/E020 y S19/S21. Las relaciones del grafo con estado CONFLICTO_PENDIENTE no se tomaron como correcciones técnicas probadas.

REA propio, cinco lotes, una sola sesión: [01–05 y sus JSONL](../../analysis/s50/codex/). Respaldo histórico `silent-liro.gpr`, siempre `-readOnly -noanalysis`, sin crear funciones ni instrucciones: exports [06](../../analysis/s50/codex/06-historical.json), [07](../../analysis/s50/codex/07-historical-followup.json), [08](../../analysis/s50/codex/08-caif.json) y [09](../../analysis/s50/codex/09-callback-count.json). Exportador: [S50Export.java](../../analysis/s50/codex/S50Export.java).

Verificación independiente de decodificación mediante LLVM sobre una sección ELF idéntica byte a byte al binario: [llvm-evidence.json](../../analysis/s50/codex/llvm-evidence.json). REA y el histórico comparten Ghidra; su acuerdo **no** es validación independiente de hardware. El [auditor](../../analysis/s50/codex/audit.py) contrasta bytes, punteros, tablas y archivos protegidos; resultado en [audit-result.json](../../analysis/s50/codex/audit-result.json).

## VERIFICADO — corrección de S49: cantidades 1/2/3/6

**CORRECCIÓN de [S49, líneas 23–28 y 65–71](s49-capture-config-producer.md):** interpretar `{clave, slot, tercer campo}` como `{clave, callback, clase de captura}` es incorrecto. El slot señala una **lista de punteros de función** y el tercer campo es su **cantidad**. No hay aquí cuatro modalidades físicas de exposición.

| Prueba en `av-cam.bin` | Instrucciones | Conclusión |
|---|---|---|
| `0x43af6870` busca una fila de 12 B | `43af6878..6886`: compara clave, avanza `r1` en `0xc`, limita por número de filas recibido en `r2` | VERIFICADO: el argumento `1/2/3/6` que puede pasar `437da100` a este helper también puede ser un **número de filas de búsqueda**; no debe confundirse con el tercer campo de una fila |
| Copia de la fila seleccionada | `43af68a4`: slot a objeto+`0x25c`; `43af68a8/aa`: carga fila+8 y guarda en objeto+`0x260` | VERIFICADO: lista y cantidad |
| Despachador `437da2d8` | `437da2ea`: cursor+258; `2f2`: cantidad+260; `2f6/2f8`: compara y sale si cursor≥cantidad; `2fc`: carga `lista[cursor]` con escala 4; `314`: `BLX r3` | VERIFICADO: el campo limita un índice de callbacks |
| Avance | `437da318..31e` incrementa cursor cuando el callback devuelve 0 | VERIFICADO: la secuencia puede continuar en otra invocación; no implica que todos los callbacks se ejecuten siempre |

Ejemplos verificados directamente contra bytes originales:

| Clave | Lista | Cantidad | Punteros Thumb almacenados |
|---|---|---:|---|
| `ce` | `43ff7414` | 1 | `437dad79` |
| `b8` | `43ff769c` | 2 | `43af8ccb`, `43af8ce5` |
| `b7` | `43ff7424` | 3 | `43af7733`, `43af7745`, `43af774d` |
| `ba` | `43ff73d4` | 6 | `43af7543`, `43af7555`, `437dae1d`, `43af7559`, `43af758f`, `43af7593` |

Evidencia: `09-callback-count.json`, `llvm-evidence.json` claves `callback-dispatch`/`callback-count-copy`, `audit-result.json.callback_lists`. S46 ya describía +258/+25c/+260 como cursor/lista/cantidad; la contradicción concreta procede de la etiqueta posterior de S49, no de una nueva capacidad del sensor.

## VERIFICADO / PARCIAL — dominios de selección e identidades

| Dominio | Evidencia | Estado y límite |
|---|---|---|
| Servicio de ajuste | Cantidades anteriores | VERIFICADO: no son clases físicas |
| CaptureStart | Antecedente `437df640`, `(cfg[265]&0xf)>>2` | PARCIAL en S50: LLVM previo documenta ramas 0–3; REA y el histórico no tienen aquí una función recuperada. No se afirma una clase 6 ni una modalidad silenciosa a partir de ese campo |
| Exposición del coordinador | `43842158`: banco+41c (EFCS), +4bc, modos/umbrales y anulaciones; `438421f0` diagnóstico | VERIFICADO software: normalmente 1 o 3 con las condiciones de E020/S41. Las anulaciones permiten otros valores, sin garantizar compatibilidad física |
| Backend IMX210 SetExposure | Byte de parámetro+9; `436d70be` compara con 4; TBB en `436d70c6` | VERIFICADO: acepta 0–4; 6 queda fuera. Tabla de destinos: `70d0`, `70e0`, `7114`, `717a`, `71ae` |
| Secuencia externa | `437eabfc`, tabla `43edccf8`, filas de `0x14` B | VERIFICADO: selecciona etapas de captura; no son los códigos del sensor |
| Secuencia interna | `437ea8cc`, tabla `43eddd08` | VERIFICADO: otro selector; deja fila 0 en cancelación o `captura+4b70==7` |

**P y C no se equiparan.** C fuente `43e9d3b4` y copia `43e9b380` conservan la identidad demostrada en S45–S47. El objeto P de `4385ca3c`, el snapshot `43ef2474`, los bancos EFCS y el objeto Image/captura son estructuras distintas hasta demostrar una copia concreta. La copia de EFCS entre bancos de E020 no prueba P=C. El control diagnóstico **D=`43e95950`** identificado abajo tampoco es C.

## VERIFICADO — disparo, preparación y petición CA

La cadena heredada S21 sitúa el despacho local `43807f4c→43807d80→43809ed8` antes del callback CaptureStart. No se vuelve a declarar cerrado aquí el enlace físico completo botón→ese despacho. En S50 sí se recupera con REA `437df338`: crea el objeto, llama a `437eabfc`, instala el descriptor y lo entrega a `43b04730`. La alcanzabilidad real en cámara sigue sin medirse.

**PRECISIÓN de [S21](s21-claude-button-to-shutter-order.md), fila L10:** no describir eventos 1 y 3 como dos envíos iniciales incondicionales.

| Fase | Función / instrucciones | Resultado |
|---|---|---|
| Entrada externa normal | Filas `+a0..+118` conducen a `438c2538` (el análisis lo absorbe en `43b1be98`) | VERIFICADO como control de flujo; una etapa no equivale por sí sola a movimiento mecánico |
| Caso 0 de Stage_CaComm | `438c25b0→438d025c`; helper con guarda `captura+74f!=0` | VERIFICADO: reserva/inicializa interacción CA, evento 0 y espera respuesta de estado |
| Caso 2 | Prepara modo y parámetros; después `438d0420` | VERIFICADO: petición inicial; ver `08-caif.json` |
| Envío inicial | `438d0420/24/2a`: guarda +74f; `438d0434/3a`: evento 1 a `437db858` | VERIFICADO: evento 1 usa `436b8a50`, paquete de 22 B hacia `436ba234` |
| Cancelación después del envío | `438d0466..46e`: getter de estado==1; entonces `438d0474/7a`: evento 3 | VERIFICADO: evento 3 condicionado a cancelación, con espera/liberación posteriores |
| Reintento/cancelación del caso 0 | `438c2638→438d033c`; helper envía eventos 1 y 3 si +74f!=0 | VERIFICADO: esta ruta no debe confundirse con el envío inicial normal |

El paquete serie de evento 1 y el tag interno de evento 3 son mecanismos diferentes. `436b89e0` construye tag `0x12`; `436bc140→436b93b0` lo consume y llama `43b5e2b0`. LLVM verifica `43b5e2b0`: comprueba banco≤17, pone `r2=0`, salta a `4398f9a4`; `4398f9bc..c8` escribe `1<<bit` en **`0xf2910048 + banco*0x100`**, y `4398f9ca..da` lee otro registro del banco y copia su valor a memoria. **VERIFICADO:** acción MMIO, no una segunda trama serie en ese helper. **NO_VERIFICADO:** identidad eléctrica de banco/bit y unión de esa señal con la primera escritura de bobina Darwin. El número `0x13a` pasado a `436b96b4` no se promueve a opcode de disparo Darwin.

## VERIFICADO / PARCIAL — omitir la petición no demuestra exposición electrónica

En `438c2538`:

1. `438c2540/42/4a/4c` resuelve base PIC `4401eee4`, slot `4402546c`, **D=`43e95950`**.
2. `438c254e..255e` comprueba D+7e no nulo y D+7f igual a `captura+1d8`.
3. `438c2560/62` pone `captura+74f=0`; `438c2566..256c` salta la petición normal.
4. La rama `438c26a4..2728` usa el mismo control: valores D+7e **1/2/3** llaman a `43ae7636` con **1/2/4** respectivamente y consumen el control.
5. `43ae7636` hace OR en `captura+4fd0`; `43ae7648` devuelve 1 con bit0, 2 con máscara1e y 0 sin esos bits. Las etapas siguientes consultan ese estado.

**VERIFICADO:** existe un bypass diagnóstico de interacción CA con propagación de estado no normal para esos valores. **RECHAZO:** presentarlo como una toma silenciosa exitosa. **NO_VERIFICADO:** otros valores, alcanzabilidad por controles normales y producción de imagen válida. No se descarta una futura ruta mediante este dato; se descarta la inferencia de éxito a partir de la sola omisión.

Inventario REA de la codificación STRB.W a +74f: `437df5e8`, `438acc9c`, `438c2562`. El primero borra el campo después de marcar estado no normal. En el segundo, LLVM prueba `438acc98 LDRB r1,[r4,#142]→438acc9c STRB r1,[r3,#74f]`. **PARCIAL:** identidad del origen y contexto de esa copia; Ghidra une ese bloque a una función extensa con partes ajenas. No se identifica su `r4` con P/C ni se toma un nombre de parámetro decompilado como prueba. El inventario no cubre todos los escritores por alias, copias o codificaciones distintas.

## VERIFICADO / INFERENCIA — fila externa +12c

Se resuelve el pendiente de colocación de S21:

- `437ebed8` obtiene tabla `43edccf8` mediante literal `437eccb8`, slot `44022934`.
- `437ebfb6..437ebfc0` pasa tabla+`0x12c` y función Thumb **`43b1c0e3`**, obtenida de literal `437eccf8` y slot `44021cc4`, a `43afb46a→437de944`; el constructor guarda el callback en descriptor+8 (`437de956`).
- LLVM `43b1c0e2..c116`: estado0→`43b1d9dc`, estado1→`437f22d4`, estado2→`437ed568`.
- `43b1d9ee` llama **`438d0d30`** (no tomar `+4` como entrada); `438d0d30/38/3a` comprueba +74f y `438d0d72/78` solicita evento12. La secuencia interna queda en fila0 cuando `captura+4b70==7`.

**VERIFICADO:** colocación, destinos y condiciones anteriores. **INFERENCIA:** es compatible con reproceso/RawDev, según la procedencia documentada en S20. **NO_VERIFICADO:** evento12 como mecanismo de fin electrónico o captura nueva de 24 MP. No se ha cerrado una exposición nueva de sensor en esta rama; no basta que falte la llamada habitual a Stage_CaComm.

## VERIFICADO / NO_VERIFICADO — inicio y fin electrónicos, VD y lectura

| Hallazgo | Evidencia concreta | Alcance |
|---|---|---|
| Selección EFCS frente a alternativa normal | `43842158`, campo banco+41c; ruta E020 hasta `captura+655`; `438c830c→436d6320` bajo `captura+4b9c==0` | VERIFICADO software; inicio electrónico físico atribuido a EFCS por contrato previo, no medido en S50. Dispositivos2/3 sobrescriben selector a0 en `438c82bc` |
| Clases IMX2101/3 | `436d70e0..7110` y `436d717a..71ac` | VERIFICADO: control bajo máscara d4 resulta c4/d4. No son valores constantes de todo el byte |
| Candidato IMX2102 | `436d7114..7132`, destino ID1/byte+2; `436d7136/7142`: LDRB a +08/+14; `713e/714a`: stores en descriptores ID100/101 | VERIFICADO: máscara94 y dos bytes adicionales. **NO_VERIFICADO:** reset, muestreo, almacenamiento de carga o segunda cortina electrónica como significado de esos bits |
| Temporización de clase2 | `436d7154..71e0`: tablas, división, producto y store u16 en IMX210+3a0 | VERIFICADO aritmético, conforme S42. Unidades y fin eléctrico NO_VERIFICADO |
| Lector del tiempo | Getter `43ad9202` y `43ad90b6→438c828c`; `43795dec→436c74c8→43ad2bd6` | VERIFICADO software con respaldo S45/S46; el destino `f3120220` pertenece a temporización VD. No prueba que ese flanco finalice integración |
| SetRead | `436d7e08`, parámetro u16, tabla por modo y cuatro llamadas a `43ad9262` | VERIFICADO: programación de lectura y condición `>0x1000`; no se asigna semántica de fin de integración solo por el nombre |
| Transporte | S44: descriptores ID/valor→empaquetado→MMIO | VERIFICADO heredado: registros llegan al transporte; no identifica por sí mismo el efecto físico de ID1/100/101 |
| Geometría completa | Datos originales: fila `43bc16dc`, u32+28=6000 y +60=4000; tablas por modo de `imx210-video-readout.md` | VERIFICADO como datos, modos0b/2f según antecedente. Existe geometría completa; no demuestra un ciclo silencioso |
| Periodo de lectura | Tabla `43bc1ae8`:864×4176; reloj54,054MHz usado en el antecedente | INFERENCIA: ≈66,8ms. No es una medición de barrido ni un límite físico demostrado para toda configuración |
| VD/YC/DMA | S32/S34/S39 distinguen callback, ventana temporal, referencia de buffer y final DMA | PARCIAL: no se cierra asociación de un cuadro nuevo completo con un fin electrónico de integración. FinDMA tampoco equivaldría automáticamente a fin de exposición |

**Relación con CURTAINMODE:** se conserva la cadena demostrada C+94/+95→bloques del coordinador y la posibilidad condicionada de seleccionar clase2 (S42–S47). El nombre de servicio y los valores de C no prueban el efecto eléctrico. El bypass mecánico hallado usa D+7e/+7f y `captura+74f`; **no se ha demostrado una dependencia CURTAINMODE→ese bypass**. No se reabrieron los callbacks/configuraciones reservados a Claude.

## Dependencias de hardware y contraste de hipótesis

El antecedente Darwin, base ROM corregida `0x4200`, mapea `20c90/20cb2` a P4D (`1ST_CURTAIN_MG`) y `20d00/20cd4` a P4E (`2ND_CURTAIN_MG`), con filtro `20c74→1b080(0)&7`: tipos1/2 para P4D,1/2/3 para P4E. **VERIFICADO heredado**, estático y por esquema: [mapa GPIO](fm3-gpio-shutter-mapping.md), [S21](s21-claude-button-to-shutter-order.md). No se volvió a abrir Darwin en S50. Esa dependencia de tipo de mecanismo no prueba que cambiarlo produzca píxeles válidos. El enlace temporal completo LIRO/MMIO→Darwin→bobina→sensor continúa PARCIAL.

| Hipótesis | Veredicto y evidencia |
|---|---|
| “Clase6 de S49 ofrece otra obturación” | **RECHAZO — VERIFICADO:** es cantidad de callbacks, no modo |
| “Clase2 IMX210 termina electrónicamente” | **NO_VERIFICADO:** programación distinta probada, significado eléctrico ausente |
| “Una subetapa sin CAIF evita las cortinas” | **RECHAZO — VERIFICADO para el argumento:** debe inspeccionarse la fila externa y sus guardas; la ausencia local no elimina sus peticiones |
| “El bypass de +74f ya es una foto silenciosa” | **RECHAZO — VERIFICADO para valores diagnósticos1/2/3:** se omiten peticiones pero se marcan estados no normales |
| “La fila+12c es una foto nueva sin cierre” | **NO_VERIFICADO:** colocación ya resuelta, mecanismo de exposición nueva sin resolver |
| “Vídeo/LiveView prueba 24MP electrónicos” | **RECHAZO:** otros modos/geometrías no demuestran la combinación requerida de modo completo, exposición y lectura |
| “No tener global shutter impide cualquier obturación electrónica” | **RECHAZO:** la pregunta admite inicio/fin electrónicos por filas; la simultaneidad global es otra propiedad |
| “La arquitectura IMX210 lo imposibilita” | **NO_VERIFICADO:** no hay evidencia concreta del mapa eléctrico de registros o arquitectura de píxel que excluya toda ruta de exposición/lectura completa por filas |

Para contestar afirmativamente falta una combinación alcanzable que una: modo completo, programación de inicio y fin por filas con efecto eléctrico identificado, ausencia de cierre mecánico durante ese intervalo, lectura completa nueva y rearme coherente. La falta de esa unión no demuestra imposibilidad.

## Validación, tiempo, memoria y límites

- Auditoría estática **PASS**: 1490 archivos protegidos sin diferencias; 11 lecturas REA idénticas al binario; 31 consultas históricas con raw64 contrastados; 22 rangos LLVM. Los rangos pueden incluir pools/tablas: no se interpretan como instrucciones ejecutadas; en particular se excluye la tabla TBB `436d70ca..70cf` del razonamiento de flujo.
- REA:42 peticiones de decompilación,33 respuestas OK y9 errores; no son42 funciones distintas. Entradas ausentes y funciones absorbidas limitan xrefs, llamadas y prototipos. Una búsqueda vacía de cadenas/procedimientos no se ha convertido en evidencia de ausencia.
- Sesión propia: espera de flock **340,9s**, análisis en frío **489,9s**. `run/metrics.csv`:104 muestras entre **19:01:36 y19:18:46 UTC**, pico del árbol REA **2333MB RSS**, MemAvailable mínimo **2954MB**. `GHIDRA_MAXMEM=4G`, watchdog8000MB, sin aumentarlo ni modificar swap/kernel. El respaldo histórico usó3G después del shutdown; no está incluido en las métricas del demonio.
- Tiempo de trabajo: aproximadamente **27 minutos** incluyendo lectura, espera, análisis y verificación; intervalo instrumentado REA17min10s. Las horas exactas y pausas del demonio están en `run/session-log.jsonl`/`metrics.csv`.
- Fallos conservados: el primer nohup no persistió y se sustituyó por proceso mantenido por exec; primer ensayo LLVM con direcciones absolutas filtró vacío porque esa vista ELF tiene VMA0; se corrigió usando offsets para el filtro. Se descartaron consultas de geometría a filas equivocadas y se comprobó la fila CamCore correcta `43bc16dc`. Entradas sin función se leyeron por bytes; no se sembraron. REA/histórico comparten algunas fusiones problemáticas de funciones; se limitan las afirmaciones a instrucciones verificables. La herramienta rechazó `rm -f` al limpiar el socket ya cerrado; se retiraron únicamente esos dos artefactos propios mediante `Path.unlink`, comprobando antes su tipo/contenido.
- Ruff en `src tests` conserva **9 avisos preexistentes** de tests ajenos; ninguno nuevo en el auditor. Mypy `src` y auditor: **PASS,6 archivos**. No se modificaron esos tests ni se instalaron paquetes.
- Restricciones respetadas: sin firmware ejecutado, Frida, cámara, flasheo, commits ni push; sin cambios a firmware, histórico, S1–S49, CURRENT, PROGRESS o grafo. Los hallazgos críticos se añadieron al inbox compartido de Claude. No se ejecutó mantenimiento global del índice porque escribiría fuera del ámbito autorizado.

**ACEPTO:** cantidades de callbacks, guardas/estados, resolución de fila+12c y programación de exposición descritas. **RECHAZO:** su conversión en prueba de fin electrónico o en imposibilidad física. **VEREDICTO: CAMBIOS** para dar por cerrada la viabilidad de foto completamente electrónica a resolución completa.
