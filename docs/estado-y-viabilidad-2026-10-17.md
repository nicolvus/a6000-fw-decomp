# Estado consolidado y viabilidad — 17-10-2026

Evaluación de los descubrimientos documentados hasta S21. Se contrastaron contexto, alcance, síntesis de alternativas, correcciones S19/S20 y los dos informes S21. Se volvieron a ejecutar los auditores estáticos `claude-button-to-shutter.py` y `codex-chain-audit.py`: ambos PASS. Esto valida sus comprobaciones sobre los binarios locales; no valida una captura en cámara ni todas las interpretaciones históricas.

## Conclusión y probabilidades

El proyecto sigue abierto: hay piezas reales y reutilizables, pero ninguna captura silenciosa completa validada. No está demostrada ni la capacidad ni la imposibilidad de fotografía totalmente electrónica a resolución completa. La categoría técnica sigue siendo evidencia insuficiente.

Las cifras siguientes son estimaciones de juicio técnico, no probabilidades medidas ni porcentajes de avance. Suponen acceso futuro autorizado a hardware y recuperación, tiempo de ingeniería y posibilidad de modificar el software necesario. Los escenarios comparten bloqueos; sus porcentajes no se suman.

| Resultado buscado | Estimación central | Intervalo orientativo | Fundamento |
|---|---:|---:|---|
| Prototipo silencioso que guarde una imagen procedente del flujo continuo, aceptando resolución/calidad limitadas | 50% | 30–65% | Existen fuente electrónica y componentes de codificación/escritura; faltan integración, contratos y ciclo de disparo |
| Foto silenciosa a resolución fotográfica completa, equivalente funcional al recorrido normal | 20% | 10–35% | No se acreditó fin electrónico de integración y lectura apropiada del IMX210 |
| RAW silencioso nuevo a resolución completa | 10% | 5–20% | La escritura ARW existe, pero no se demostró adquisición RAW electrónica compatible |
| Base documental reproducible de arquitectura y firmware, con alcance acotado | 85% | 75–95% | Ya existen extracción, inventario y trazas; quedan hardware, interfaces y recuperación |

Si «completar» significa obtener alguna fotografía silenciosa guardada e integrada, usaría **50% provisional**. Si significa sustituir completamente el obturador de fábrica conservando resolución y RAW, usaría **20% o menos según requisitos**. El proyecto general de ingeniería inversa puede tener éxito aunque ese subproyecto resulte físicamente inviable. No es defendible asignar una probabilidad a comprender absolutamente todo el hardware y firmware sin definir criterios de cierre.

## Flujos completos por tramo

«Completo» en esta tabla significa un tramo estático reconstruido con sus límites, no un producto terminado.

| Flujo | Evaluación | Lo que permite afirmar |
|---|---|---|
| Ajuste SilentShutter → secuencia de software → comando `0x40e3` → almacenamiento LIRO | ACEPTO | Existe control real de software; recibir/guardar On no demuestra exposición silenciosa |
| Entrada de eventos `input.ko` → cola `0x7a0020` → InfraInput | ACEPTO | Transporte de entrada identificado; asignación física de teclas y puente posterior incompletos |
| Selector de captura fija examinado → Stage_CaComm | ACEPTO | Las rutas fijas seleccionadas estudiadas solicitan intervención CA/Darwin; no apareció un bypass Silent seleccionable |
| Rutinas Darwin → escrituras de control P4D/P4E de cortinas | ACEPTO | Se identificó control eléctrico en código; no movimiento observado ni unión completa de la trama hasta cada fase |
| SFRA → JPEG comprimido → cliente de streaming Linux | ACEPTO | Hay fuente electrónica reutilizable como candidata; no se ha unido a almacenamiento fotográfico |
| RawPlay/DevLater → reprocesamiento de ARW existente | ACEPTO | Precedente de procesamiento reutilizable; no es adquisición RAW nueva |
| Ramas de escritura JPEG/RAW → llamadas de registro DCF | ACEPTO | Existen escritores y registros diferenciados; faltan selección concreta, completado y publicación extremo a extremo |

## Flujos incompletos

| Flujo | Qué tenemos | Qué falta |
|---|---|---|
| Botón físico → orden efectiva de cortinas | Entrada, mensajes, coordinación LIRO, tarea CA y rutinas Darwin | Tabla de teclas, puente InfraInput, estado activo, tags CA → opcode y trama → fases; señales e interrupciones físicas |
| EFCS/Silent → sensor | Configuración, selectores y controlador IMX210 documentados | Demostrar que Silent termina integración electrónicamente y produce una lectura fotográfica válida |
| Sensor → imagen disponible | Descriptores DMM y entrega nativa Stage_Notify | Productor final, evento de fin DMA, coherencia de caché y propiedad del buffer |
| Camera → Effect → Recorder → EncodeStill | Topología y contratos parciales, con precedente PbCap | YC real de Camera, geometría/color, activación y retención/liberación hasta fin de codificación |
| EncodeStill → Pool → escritura | Codificación encolada y piezas de conversión/Pool | Callback real, último acceso al YC, resultado Recorder→FEA y SetImageWrited |
| WriteStill → SD → biblioteca/reproducción | Secuencias de escritores y registros JPEG/RAW/DCF | Instancia real de escritor, resultado persistido, rollback y consumidor que hace visible la entrada |
| Arranque/actualización → recuperación | Inventario inicial documental | Procedimiento de recuperación demostrado y correspondencia con dispositivo/placa |

## Alternativas de implementación

Los nombres históricos cambian: en S17–S21, **A** designa la arquitectura LIRO de fábrica como referencia. Algunos diseños antiguos llamaban A a su modificación hipotética. Que la referencia tenga precedente operativo no prueba la adaptación silenciosa.

| Alternativa | Estado y prioridad |
|---|---|
| Adaptar el pipeline LIRO de fábrica | Primera candidata: conserva coordinación y etapas de metadatos/escritura. Necesita cambiar adquisición/selección antes de Stage_CaComm y demostrar finalización/cancelación sin cortinas |
| E: Camera → Effect → Recorder con frame continuo | Segunda candidata: componentes reales; datos, activación y vida útil del YC siguen abiertos |
| P: API CameraSequence | API real, pero no acredita que evite adquisición mecánica ni que entregue el buffer necesario |
| E2 y variantes híbridas | Alternativas de reserva; no tienen cierre superior al de E y no eliminan sus contratos pendientes |
| SFRA JPEG → MPR | Fuente candidata de menor calidad/resolución por caracterizar. Requiere miniatura, screennail, EXIF, handles y registro; JPEG no se puede pasar como si fuera YC |

El orden documental vigente es **A > E > P ≈ E2**. Es prioridad de investigación, no tasa de éxito ni prueba de compatibilidad.

## Descartes firmes y límites de esos descartes

| Afirmación o atajo | Veredicto y evidencia |
|---|---|
| «Con activar el menú/recibir ACK ya funciona Silent» | RECHAZO: solo se verificó configuración/recepción |
| «EFCS demuestra final electrónico» | RECHAZO: inicio electrónico no acredita sustitución de la segunda cortina |
| «Copiar el bit Silent de A6300 basta» | RECHAZO para ese mecanismo: el parser A6000 examinado no consume ese campo como A6300 |
| «Una secuencia sin CAIF directo evita las cortinas» | RECHAZO: la fila externa ya hizo la petición mecánica |
| «Cambiar tipo HW de Darwin equivale a implementar Silent» | RECHAZO: inhibir escrituras no demuestra fin de exposición, lectura ni coherencia del mecanismo |
| «RawPlay produce una captura RAW nueva» | RECHAZO: parte de un ARW ya guardado |
| «JPEG SFRA es entrada YC válida para EncodeStill» | RECHAZO: contratos y formatos distintos |
| «Guardar un JPG en DCIM garantiza reproducción» | RECHAZO como garantía: no demuestra registro ni catálogo DCF/MPR |
| «StsViewer es un cerrojo que impide E» | RECHAZO: la revisión de Connect/StatusViewer corrigió esa interpretación |
| «CapIdTblMgr es la entrada de CaptureStart» | RECHAZO: cliente de servicio de tablas; el análisis posterior identificó retroalimentación RelMgr |
| «StillConverter +0x4c es un pin hacia DCF» | RECHAZO: es EventReceiver local |
| «La A6000 es físicamente incapaz de Silent» | RECHAZO como conclusión: falta evidencia física específica; no se descartó el objetivo global |

Se descartan interpretaciones y atajos concretos. Ninguna alternativa principal queda demostrada físicamente imposible por estos resultados.

## Investigación que más cambia la viabilidad

1. **Separar los dos objetivos:** frame continuo guardado frente a fotografía completa. Elegir criterio de calidad, resolución y RAW para poder declarar éxito.
2. **Capacidad real del sensor:** demostrar fin electrónico, modo de lectura, resolución y profundidad. Es la incertidumbre dominante para fotografía completa; investigar más DCF no la resuelve.
3. **Unir orden LIRO con Darwin:** tags `0x12/0x13` de la tarea CA, opcode, descriptor/fase y primera escritura de cortina. Completar además señales/interrupciones del disparo.
4. **Cerrar la fuente de imagen:** productor del YC, raster frente a SDS, geometría, DMM/DMA, caché y liberación tras completion EncodeStill.
5. **Cerrar éxito y errores:** Recorder→FEA, Pool, escritor concreto, persistencia, rollback y primera visibilidad en reproducción. Ver una llamada a Write no basta.
6. **Recuperación y prueba física:** antes de considerar demostrado el prototipo, disponer de recuperación y verificar varias tomas, cancelación, vuelta al modo normal y ausencia de accionamiento mecánico.

Una demostración de fuente YC compatible más codificación completa aumentaría la estimación del prototipo; una lectura fotográfica electrónica acreditada cambiaría sustancialmente la estimación de resolución completa. Una limitación física documentada podría cerrar esa segunda vía conservando la alternativa de flujo continuo.

## Evidencia principal y límites de validación

- [S21: botón → cortina](capture/s21-claude-button-to-shutter-order.md), especialmente líneas 110–145: bypass, descartes y huecos.
- [S21: exposición → biblioteca](capture/s21-codex-exposure-to-library.md), especialmente líneas 310–334: siete fronteras pendientes y validación previa.
- [Correcciones y síntesis S20](capture/s20-claude-autonomous-verdict.md).
- [Alcance general](project-scope.md), [recuperación](boot-and-recovery.md) y [estado Silent](capture/silent-shutter-status.md).

Validación de esta revisión: ambos auditores S21 PASS sobre artefactos locales. No se ejecutó firmware ni se probó cámara; no se materializó una fotografía. No se modificó código; no se repitieron lint/mypy para este informe. Sus resultados previos S21 distinguen scripts propios sin avisos, mypy src PASS y nueve avisos ruff en tests ajenos. Sin commit: el directorio del proyecto no es un repositorio Git utilizable según el checkpoint; sin push.

**VEREDICTO: CAMBIOS** para declarar completa la captura silenciosa o el flujo exposición → biblioteca. La investigación aporta cierres parciales verificables, sin demostrar todavía el resultado final.
