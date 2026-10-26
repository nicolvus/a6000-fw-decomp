# Subproyecto: obturador electrónico completo

Forma parte de Sony A6000 Hardware & Firmware Reverse Engineering Project.
Mantiene el objetivo original de determinar fotografía sin cierre mecánico.

Estado: categoría E, evidencia insuficiente. No hay parche ni prueba sobre
hardware. Se conservan todas las evidencias anteriores en sus rutas originales.

## Estado del obturador electrónico completo (26-10-2026)

Decisión [S51](../../docs/capture/s51-decision.md): **A=NO** (ruta no demostrada), **B=NO** (sin base para un parche), **C=NO** (sin prueba de
imposibilidad). No hay captura silenciosa completa validada. Lo demostrado y lo pendiente: [STATE](../../docs/STATE.md); tareas:
[PENDIENTES](../../docs/PENDIENTES.md); informes por tema (obturador, sensor, comparaciones): [INDEX](../../docs/INDEX.md);
pruebas físicas propuestas y diferidas: [P1–P8](../../docs/capture/physical-test-plan.md), [P13–P21](../../docs/capture/physical-test-plan-2.md).

- [Viabilidad provisional](../../docs/feasibility-report.md).
- [SilentShutter hasta el receptor LIRO](../../docs/capture/silent-shutter-status.md).
- [EFCS y cortina trasera electrónica: investigación principal](../../docs/capture/shutter-investigation.md).
- [Hallazgos](../../docs/findings.md).
- [SilentShutter](../../docs/silent-shutter-trace.md).
- [S140: vector de registros IMX210 y bancos de filas (enumeración estática; valores runtime pendientes)](../../docs/capture/s140-imager-register-map.md).
- [S141: selección/copia de fila y origen runtime aún abierto](../../docs/capture/s141-imager-row-copy.md).
- [S142: reset directo y lectura de S+0xda (sin resolver el escritor del selector)](../../docs/capture/s142-imager-s-init.md).
- [S145: límite de cobertura REA junto al staging IMX210](../../docs/capture/s145-imager-code-gap.md).
- [S146: REA no permite sembrar procedimientos fuera del análisis](../../docs/capture/s146-rea-seed-limit.md).
- [S147: recorrido parcial de las filas de 16 B del banco G](../../docs/capture/s147-imager-g-rows.md).
- [S149: auditoría de los helpers y offsets aún no escritos dentro de cada fila](../../docs/capture/s149-imager-row-helpers.md).
- [S150: referencias directas y literales de puntero a los huecos de fila](../../docs/capture/s150-imager-row-gaps.md).
- [S152: lectura diagnóstica del byte gap por descriptores](../../docs/capture/s152-imager-gap-descriptor-read.md).
- [S153: gates de flags del dumper y límite de alcanzabilidad](../../docs/capture/s153-imager-dump-gates.md).
- [S154: xref de GOT al objeto de flags, sin escritura](../../docs/capture/s154-imager-state-ref.md).
- [S155: más xrefs al objeto gate, clasificadas como lectores/accesores](../../docs/capture/s155-imager-state-readers.md).
- [S157: rutina de snapshot del estado, sin escritura de los gates](../../docs/capture/s157-imager-state-snapshot.md).
- [S158: spill de puntero y lectores de otros campos del estado](../../docs/capture/s158-imager-state-ref.md).
- [S159: otro spill de puntero y lecturas de campos del estado](../../docs/capture/s159-imager-state-spill.md).
- [S160: escritura de `state+0` al expirar un contador](../../docs/capture/s160-state-open-flag.md).
- [S161: otro xref de base es spill a stack](../../docs/capture/s161-imager-state-spill.md).
- [S162: lectores de un halfword del estado en helpers de eventos](../../docs/capture/s162-imager-state-event-readers.md).
- [S163: tercer lector de campos del estado en el pipeline de eventos](../../docs/capture/s163-imager-state-event-reader.md).
- [Comparación entre modelos](../../docs/comparative-analysis.md).
- [Límites de hardware pendientes](../../docs/hardware-limitations.md).

Depende de la caracterización del sensor, temporización y lectura del pipeline.
Un resultado negativo o inconcluso no bloquea la investigación general.
