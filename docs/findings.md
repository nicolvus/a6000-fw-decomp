# Evidencias

E015 — [VERIFICADO] dato 0x291, inicialización, acción, factory 0x768e,
constructor Silent, mp_CamMgr y SET/ACT. Tabla indexada demuestra
0x450=Off y 0x451=On; modos 1/2→bytes0/1. Evidencias, funciones, hash y
límites en [SilentShutter](capture/silent-shutter-status.md).

E016 — [VERIFICADO] av-cam.bin LIROv4, receptor cola0x30001, paquete tipo5,
tabla220 y comando0x40e3→handler0x438032d4→bloque+0x238. No era parte del
atlas ELF. Extractor con siete tests, tabla completa y hash en
reports/silent-liro-dispatch.json. Consumo físico del estado [NO VERIFICADO].

E017 — [VERIFICADO] RTTI de controlador Camera::Imager::IMX210 y diagnósticos
de lectura/exposición dentro de av-cam.bin. [INFERENCIA] candidato al sensor;
chip/revisión físicos sin comprobar. Ocho funciones candidatas decompiladas
en proyecto Ghidra persistente; sin enlace probado a Silent ni registro CMOS.

E014 — [VERIFICADO] inicialización candidata de colas 0x30001/0x40193 en
libObj, transporte /dev/uipc en la copia nflasha15 de libosal_uipc y encolado
genérico en osal_uipc.ko. [HIPÓTESIS] identidad del owner de esa inicialización
con el de las secuencias de obturador; resolución de biblioteca en ejecución
no observada. Hashes, funciones, exports y límites en
[informe de obturación](capture/shutter-investigation.md). Receptor final pendiente.

E012 — [VERIFICADO] EFCS oficial A6000; acciones y secuencias candidatas
FrontEShutterMode/SilentShutter, despacho indirecto a conversores y envío OSAL
en libObj 3.21. Coordenadas, hash, tablas, alcance y reproducción en
[informe de obturación](capture/shutter-investigation.md) y
reports/efcs-silent-dispatch.json. [NO VERIFICADO] soporte físico de final
electrónico. Próximo experimento: resolver receptor y selección por modelo.

E013 — [VERIFICADO] factory ScalarDaemon caso0x1008 construye TakePicture;
captureStart emite modelo3/event7 hacia ModelManager. Callbacks de entrada y
AutoReview parcialmente localizados. Exports REA, hashes y funciones en
[pipeline](capture-pipeline.md). [NO VERIFICADO] unión completa botón→sensor→
RAW/JPEG→pantalla. captureStop no se interpreta como cierre mecánico.

E010 — [VERIFICADO] Atlas estructural completo: 679 ELF ARM, 641 hashes únicos,
3890 DT_NEEDED y 8 resoluciones ambiguas. Herramienta readelf, productor y
diagnósticos por archivo en reports/elf-atlas.json. [INFERENCIA] asociaciones
funcionales según símbolos/dependencias; 391 desconocidas. Limitación: carga
real, dlopen, IPC e interfaces físicas no resueltas. Siguiente paso: resolver
las ambigüedades de libosal_uipc y cargadores. Detalle: docs/elf-classification.md.

E011 — Inventario físico documental inicial, fuentes y límites por componente
en docs/hardware-inventory.md. No identifica encapsulados ni revisiones de placa.

E007–E009 y sus campos de archivo, hash, coordenadas, método, evidencia,
interpretación, límites y siguiente experimento: [traza SilentShutter](silent-shutter-trace.md).

Etiquetas: [VERIFICADO] resultado local o documento comprobado; [INFERENCIA] deducción; [HIPÓTESIS] pendiente; [NO VERIFICADO] sin comprobar; [DESCARTADO] refutado.


## E001

- ID: E001
- Fecha: 2026-10-15
- Hipótesis: El paquete corresponde a 3.21
- Herramienta: fwtool / lectura YAML
- Archivo: firmware/extracted/fw321/config.yaml
- SHA-256: 35d77d336dab52c654f0cb44e9cf0a2ebadfcfdf69931fca9d42e29b0d245ba3
- Dirección o referencia: fdat.version
- Método de análisis: fwtool / lectura YAML
- Evidencia: 3.21, model 0x41030035, CXD90014
- Interpretación: Versión declarada por cabecera
- Limitaciones: No se dispone de NAND
- Estado: VERIFICADO
- Próximo experimento: Analizar ELF

## E002

- ID: E002
- Fecha: 2026-10-15
- Hipótesis: nflasha5 es TPZL
- Herramienta: xxd / parser WBI
- Archivo: firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5
- SHA-256: fe080cda9f330537f36d7e9e283ecd69e4e8096d974dbdd16d598a8cbdcf3f04
- Dirección o referencia: offset archivo 0
- Método de análisis: xxd / parser WBI
- Evidencia: WBI1
- Interpretación: Clasificación TPZL para esta partición refutada
- Limitaciones: No generalizar a otras versiones
- Estado: DESCARTADO
- Próximo experimento: Mapear las secciones WBI

## E003

- ID: E003
- Fecha: 2026-10-15
- Hipótesis: Existe código asociado a modo silencioso
- Herramienta: strings -a -t x
- Archivo: firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so
- SHA-256: 8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a
- Dirección o referencia: offset archivo 0xd5178c; 0xe52aac
- Método de análisis: strings -a -t x
- Evidencia: pvt_SetSilentShutterMode / MSGID_SET_SILENT_SHUTTER_MODE_CMD
- Interpretación: Pistas para xrefs
- Limitaciones: No prueba de función alcanzable o soporte hardware
- Estado: VERIFICADO
- Próximo experimento: Resolver xrefs y condiciones de modelo en Ghidra

## E004

- ID: E004
- Fecha: 2026-10-15
- Hipótesis: La interfaz de captura envía una orden
- Herramienta: readelf / llvm-objdump ARM
- Archivo: firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha16_unpacked_unpacked/lib/libcamera.so
- SHA-256: 7bb156b3c68b802fcdeceb83037d770504c128d0b73a6708122d58589f80c013
- Dirección o referencia: VA ELF 0x170c0; instrucción 0x170e4
- Método de análisis: readelf / llvm-objdump ARM
- Evidencia: takePicture carga r1=0x1008 y salta a SDComMsg_Basic
- Interpretación: Orden de alto nivel
- Limitaciones: Receptor y control físico sin resolver
- Estado: VERIFICADO
- Próximo experimento: Resolver dispatcher 0x1008

## E005

- ID: E005
- Fecha: 2026-10-15
- Hipótesis: El procesador de captura llama captureStart
- Herramienta: readelf / llvm-objdump Thumb
- Archivo: firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libScalarDaemon.so
- SHA-256: ca28cbf4c5c6402160ad80f6ad9f5e99052f42c3fabc382c557fcded18addc29
- Dirección o referencia: símbolo Thumb 0x1080b5; código 0x1080b4; llamada 0x108144
- Método de análisis: readelf / llvm-objdump Thumb
- Evidencia: BLX al PLT con símbolo SystemEventIssuerCamera::captureStart
- Interpretación: Arista local sustentada
- Limitaciones: No establece ruta desde botón ni sensor
- Estado: VERIFICADO
- Próximo experimento: Resolver eventos y destinatario de captureStart

## E006

- ID: E006
- Fecha: 2026-10-15
- Hipótesis: REA está operativo
- Herramienta: node scripts/rea.mjs doctor --json
- Archivo: reports/rea-doctor.log
- SHA-256: c1ab1934f21615b27b6c4a98f0770851a203b8396a51fa82f4be803688543c96
- Dirección o referencia: doctor
- Método de análisis: node scripts/rea.mjs doctor --json
- Evidencia: compiled runtime is missing
- Interpretación: REA no disponible funcionalmente
- Limitaciones: No se instalaron paquetes
- Estado: DESCARTADO
- Próximo experimento: Disponer de runtime precompilado y proveedor compatible

El reporte del repositorio base no sustituye una reproducción local. Sus offsets NAND no se han utilizado como VA. Su script verify_partitions.py solo busca la primera coincidencia de 16 bytes; un encabezado repetido puede causar un falso fallo. carve_fat16.py tiene incidencias LFN/FAT y discrepancia --dump/--outdir; no se usó sobre datos personales. map_regions.py usa heurísticas, no identifica funciones.
