# Modos de lectura: evidencia y límites

Los manuales Level 3 indican IMX235AQR-13 (A7S) e IMX210AQL-13 (A6000), CXD90027GF, 12 pares sub-LVDS de recepción/transmisión y reloj 54 MHz: **VERIFICADO como transcripción de manual**, con origen de terceros no auditado. 432 Mb/s por canal no aparece: **DESCARTADO como afirmación sustentada por esos manuales**. IMX157 no corresponde a A7S: el manual citado dice IMX235, por lo que la proposición «A7S usa IMX157» queda **REFUTADA** por esa fuente.

En A6000, la tabla IMX210 conocida ofrece modos completos 6000×4000 y modos 1996×1124/2000×570/2000×800; el análisis previo los clasifica por tablas y temporización, pero no establece bits eléctricos de cada registro. No hay una tabla IMX235 equivalente recuperada aquí, por lo que no se comparan secuencias ni se infiere global-reset, rolling-reset o fin de integración.

**Conclusión:** los blobs examinados prueban infraestructura DFE y APIs de control, no una secuencia que pruebe exposición electrónica completa ni una dependencia de cortinas.
