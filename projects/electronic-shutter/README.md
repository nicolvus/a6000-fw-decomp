# Subproyecto: obturador electrónico completo

Forma parte de Sony A6000 Hardware & Firmware Reverse Engineering Project.
Mantiene el objetivo original de determinar fotografía sin cierre mecánico.

Estado: categoría E, evidencia insuficiente. No hay parche ni prueba sobre
hardware. Se conservan todas las evidencias anteriores en sus rutas originales.

- [Viabilidad provisional](../../docs/feasibility-report.md).
- [SilentShutter hasta el receptor LIRO](../../docs/capture/silent-shutter-status.md).
- [EFCS y cortina trasera electrónica: investigación principal](../../docs/capture/shutter-investigation.md).
- [Hallazgos](../../docs/findings.md).
- [SilentShutter](../../docs/silent-shutter-trace.md).
- [S140: vector de registros IMX210 y bancos de filas (enumeración estática; valores runtime pendientes)](../../docs/capture/s140-imager-register-map.md).
- [S141: selección/copia de fila y origen runtime aún abierto](../../docs/capture/s141-imager-row-copy.md).
- [S142: reset directo y lectura de S+0xda (sin resolver el escritor del selector)](../../docs/capture/s142-imager-s-init.md).
- [S145: límite de cobertura REA junto al staging IMX210](../../docs/capture/s145-imager-code-gap.md).
- [Comparación entre modelos](../../docs/comparative-analysis.md).
- [Límites de hardware pendientes](../../docs/hardware-limitations.md).

Depende de la caracterización del sensor, temporización y lectura del pipeline.
Un resultado negativo o inconcluso no bloquea la investigación general.
