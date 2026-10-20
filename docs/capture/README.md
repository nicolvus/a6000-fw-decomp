# Línea B: pipeline de captura

- [S44: consumidor de registros y comparación de modos](s44-register-consumer-mode-table.md):
  backend de comandos hasta MMIO y virtual+a8 resueltos; alias P/C y cierre
  físico de integración pendientes.

- [S41: mensajería, snapshots y valores IMX210](s41-message-origin-imx210.md):
  colas y productores internos; tablas de conversión contrastadas.
  Bit31 de OSAL, productor 3023 y enlace físico pendientes.

- [S38: DMM/OSAL y frontera del blob](s38-dmm-osal-static-frontier.md):
  pool compartido, receptor sin recuperar; slot importado cero y sin ELF.
  Próximo vigente: enum de formato S33 hasta APL/stride/tamaño.

- [S30: captura, origen YC y cierre de EncodeStill](s30-pipelines-capture-encode.md):
  receptor InfraAvbbc→StillEncoder→SDF y retorno hasta Execute/Pool.
  Descarta CaptureId como raster y el getter como completion DMA.
  Los tres requisitos funcionales siguen pendientes de adquisición y contrato YC.

- [S29: WriteStill de entrada a cierre](s29-writestill-end-to-end.md):
  orden, preparación, escritor DCF, retorno RecStill→FEA→Obj y cierre Pool.
  Respuesta `0x10000004`; SetImageWrited usa `0x1007`. Durabilidad física y
  visibilidad en reproducción no se infieren del callback.

- [S28: cierre OSAL y contrato de pines](s28-osal-pin-contract-closure.md):
  InfraImaging registra y sirve `0x50004`; VEF y ScalarInfra identificados;
  las propiedades de conexión no satisfacen el contrato de WriteStill.
  Corrige los límites e interpretaciones pendientes de S23–S27.

- [Fases Darwin y escrituras de control](darwin-state-machine.md): cuatro
  destinos por cámara, notificación ADC y retención del planificador verificadas.

- [Paquete Silent y transporte CAIF](silent-caif-transport.md): 22 bytes en
  A6000 frente a 31 en A6300; construcción y receptor físico aún por completar.
- [Firmware auxiliar Darwin](darwin-shutter-entrypoints.md): base ROM `4200`
  contrastada y entradas para estudiar la posición del obturador.
- [KikiLog descartado como control de cortinas](silent-kikilog.md): receptor
  y contador comprobados con REA/Ghidra.

- [Comparación Silent A6300 / A6000](a6300-silent-comparison.md): modos,
  secuencias y diferencias de controlador verificadas; investigación abierta.
- [Ajuste y respuestas Silent en A6300](a6300-silent-software.md): protocolo
  común, envío y respuesta de ajuste; no equivalen a un fotograma validado.

- [EFCS: configuración, bancos y selector de captura](efcs-capture-selector.md),
  E020: enlace condicional hasta el argumento recibido por SetExposure.
- [S19-12: decisiones previas a obturación mecánica](s19-mechanical-shutter-decision-points.md):
  guardas de admisión, selector LIRO y límite actual de la evidencia.
- [Exposición IMX210, EFCS y transporte P2S](imager-exposure-p2s.md), E019:
  coordinador → parámetros → controlador → escrituras periféricas; vínculo
  de Silent con el final electrónico todavía no demostrado.
- [Consumidores y correcciones de entradas](silent-imager-consumers.md), E018.

- [SilentShutter: configuración → receptor LIRO y estado actual](silent-shutter-status.md),
  E015–E017; base de la ruta de configuración y recepción.

Prioridad vigente del usuario: **obturación**. Resultado principal:
[EFCS y cortina trasera electrónica](shutter-investigation.md), con comparación
de métodos, rutas de mensajes, alternativas y evidencia aún necesaria.

- [Pipeline parcial](../capture-pipeline.md).
- [S17: contrato SDF/YC de la secuencia 0x6013](s17-codex-c-sdf-yc.md): PbCap crea un par raster/SDS dedicado; la compatibilidad del YC de Camera permanece sin demostrar.
- [S22: sensor nuevo → YC para StillRecorder](s22-sensor-to-yc.md): LIRO
  serializa StillInfo, pero el productor del raster YC y su sincronización
  continúan abiertos; SilentShutter no se declara funcional.
- [S23: frontera Dataflow de los pines YC](s23-yc-pin-dataflow-boundary.md):
  `PIN_YC#0` valida cuatro enteros y realiza un request/reply Dataflow
  síncrono; aún no identifica píxeles ni un descriptor DMM de captura.
- [S24: endpoint Dataflow de Camera.YC0](s24-camera-yc0-effect-endpoint.md):
  el parser fija `0x50004`, que se reconecta desde el dominio ObjEffect; el
  receptor de payload y un YC apto para Recorder siguen abiertos.
- [S25: límite del registro Dataflow](s25-dataflow-pin-registry-limit.md):
  `infraGetPin` resuelve `0x50004` por request/reply de infraestructura; el
  callback final no está en una tabla estática local de Camera.
- [S26: seis microprocesos estáticos de Camera.YC0](s26-five-static-microprocesses.md):
  constructor, admisión, serialización, transporte, consulta de registro y
  relay quedan cerrados dentro de sus fronteras; no acreditan un YC de captura.
- [S27: recableado de PostProcess](s27-effect-postprocess-rewire.md): la
  transición ObjEffect conecta `0x005a0048` con `0x50004` en dos perfiles; el
  registro y el productor YC continúan abiertos.
- [Traza SilentShutter E007–E009](../silent-shutter-trace.md).
- [Control de obturador](../shutter-control.md).
- [Sensor](../sensor-investigation.md).
- [Subproyecto de obturador electrónico](../../projects/electronic-shutter/README.md).

E012 resolvió secuencia→conversor; E013, despacho 0x1008; E015/E016 añaden
factory, identidad de cola y receptor LIRO. Siguiente frontera: consumo físico
del estado, selección por modelo y fin de integración/lectura.
