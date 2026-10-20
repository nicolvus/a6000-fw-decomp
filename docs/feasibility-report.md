# Viabilidad provisional — 15-10-2026

Informe del [subproyecto de obturador electrónico](../projects/electronic-shutter/README.md)
dentro del proyecto general de hardware y firmware. La investigación de
arquitectura, arranque e interfaces continúa aunque esta viabilidad siga abierta.

**Categoría E: evidencia insuficiente.** Ni viabilidad ni imposibilidad demostradas. No se desarrolló parche.

E015–E017 amplían significativamente la ruta de software: factory, CamMgr,
Off/On y receptor LIRO 0x40e3 identificados. El handler guarda estado y existe
una copia de parámetros a un objeto de trabajo; falta el consumo físico.
El blob incorpora un controlador llamado IMX210, candidato aún sin
identificación de chip/revisión. [Informe completo de SilentShutter](capture/silent-shutter-status.md).

Actualización E012/E013: [EFCS y fin electrónico](capture/shutter-investigation.md).
Se resolvieron las secuencias candidatas, despacho a conversores y envío OSAL
para EFCS/SilentShutter, y el caso 0x1008 del factory de captura. El consumidor
OSAL y la lectura física siguen pendientes. Un éxito de software tras envío
no demuestra una exposición completamente electrónica. Los pendientes
históricos de xrefs siguientes quedan acotados por esta actualización.

Avance E007: se verifica construcción del nodo de configuración SilentShutter
con dos opciones On/Off. No cambia la categoría: falta seguir la acción hasta
un procedimiento válido de finalización y lectura de la exposición.

E009 localiza una rama que convierte valores 0x450/0x451 a un byte 0/1. El
diagnóstico NON SUPPORTED corresponde a identificadores de mensaje no aceptados;
no es evidencia de una barrera de hardware. Falta demostrar alcance desde la
captura, envío y recepción efectivos y comportamiento físico del sensor.

| Pregunta | Respuesta sustentada |
|---|---|
| 1. ¿Quién inicia electrónicamente la exposición? | EFCS documentado; controlador físico no identificado. takePicture solo verifica una orden de software. |
| 2. ¿Quién sincroniza el cierre mecánico? | No identificado. |
| 3. ¿Comandos del sensor identificados? | No; identificadores de mensajes y cadenas de alto nivel no equivalen a registros. |
| 4. ¿Segunda cortinilla electrónica? | Sin evidencia funcional; SilentShutter es una pista de firmware. |
| 5. ¿Foto sin accionamiento mecánico? | No demostrado. |
| 6. ¿Resolución viable? | Desconocida para el modo propuesto. |
| 7. ¿RAW viable? | No demostrado. |
| 8. ¿Limitaciones? | Sin medir; falta caracterizar bits, lectura, exposición, rolling shutter, flash y ruido. |
| 9. ¿Cambios necesarios? | Indeterminados; falta resolver selección por modelo y secuencia física. |
| 10. ¿Qué evidencia falta? | Inhibiciones/modelo, consumidor físico del campo LIRO+0x238, enlace al controlador IMX210, fin de integración y lectura completa, recuperación antes de hardware. |

Nivel 1: firmware oficial extraído e inventariado, con incidencias y secciones WBI documentadas; no incluye NAND real. Nivel 2 parcial: Android y entradas de captura identificados, subsistema completo pendiente. Niveles 3–7 pendientes. No se declara arquitectura ni control físico reconstruidos.

La siguiente tarea decisiva es seguir el campo de estado Silent del receptor
LIRO y su copia de trabajo hasta exposición/lectura IMX210, resolver inhibiciones
y S_IMAGER_CURTAINMODE. Productor, cola y receptor ya se documentaron en E015/E016.
