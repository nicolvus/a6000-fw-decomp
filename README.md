# Sony A6000 Hardware & Firmware Reverse Engineering Project

Ingeniería inversa de hardware y firmware de la Sony A6000 (fw 3.21): arquitectura, arranque,
recuperación y pipeline de captura. El obturador electrónico es un
[subproyecto](projects/electronic-shutter/README.md). Sin firmware ejecutado, sin cámara, sin flasheo.

## Dónde mirar primero

- Estado operativo breve: [knowledge/CURRENT.md](knowledge/CURRENT.md) · restricciones: [docs/STATE.md](docs/STATE.md) · continuidad: [CONTEXT.md](CONTEXT.md).
- Historial completo de fases: [knowledge/PROGRESS.md](knowledge/PROGRESS.md).
- Catálogo de la línea de RE general (38 hitos): [docs/capture/linea-general-re.md](docs/capture/linea-general-re.md).
- Resultados y viabilidad: [docs/findings.md](docs/findings.md), [docs/feasibility-report.md](docs/feasibility-report.md).
- README histórico íntegro (S19–S100, antes de esta reorganización): [docs/history/README-historial-2026-10-21.md](docs/history/README-historial-2026-10-21.md).

## Fases recientes (más nuevas primero)

Cada enlace lleva a su informe; el resumen de hallazgos está en el [catálogo](docs/capture/linea-general-re.md) y en el [historial](docs/history/README-historial-2026-10-21.md).

- [S115: `[CAM_IMAGER]`, el driver del imager de la cámara](analysis/s115_cam_imager/imager_driver.md): 371 trazas (79 del ZIT ya de S80 → 292 del driver) en 94 funciones: el **transporte P2S** al sensor (canales **DFE0/DFE1**, datos **por páginas**, `P2SFormatter`, `CheckAddrOrder`), las interrupciones (`int_p2s_handler`, `int_timer_handler`), la **SIF** (sync code **en serie o en paralelo**), la API `ImagerCommon` de **un solo canal** hacia el **CISIF** y el serializador `SubLVDS`; sobre todo la **máquina de lectura/exposición por `drive_mode`**, con el campo **`shut`** en la traza de exposición (`0x43c93cc2`) y `SSBRK_ON`/`SIFSyncCode` al ejecutar → puntos de contacto directo con la línea del obturador (S56–S58). En la A7S fw3.20 el mismo driver está **sin etiqueta** y sin `SetExps`/`Execute0`. 9 tests.
- [S112: el módulo `[CAMERA_MAIN_SYNC]` (429 trazas) de sincronización de recursos](analysis/s112_camera_main_sync/camera_main_sync.md): el subsistema que coordina los recursos compartidos durante la captura — `SyncResMgr` (55 trazas: `Lock`/`Unlock`/`Free`/`Get` sobre `CAMDEV(0|1)`, RC y APL), volcado de registros `[CAM0]/[DDT]/[APL0]`, `DFS`/`DVS`, `Sync_Kick_IDT/RCH/RCV`, `HS_Sequence` y `int_HS timing`; **mapa función→traza completo** (430 funciones, 1 407 pares) y diferencial verificado: **418/429** mensajes existen también en la A7S fw3.20 sin la etiqueta (11 exclusivos: `Sync_Kick_*` con overflow, `SuperSlowMotion[Buffering]`, `EC::CapISO`…). 12 tests.
- [S114: el motor de secciones de la captura, completo (17 ids ↔ 17 etapas)](analysis/s114_sections/section_engine.md): cierra la pregunta abierta de S106 — **15 de las 17 secciones** de la tabla `0x43ff8fb4` quedan nombradas: `0x01` = **Prelight** (nuevo: su manejador `0x437eb144` llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) y las 14 restantes por su propio `*_Selector.cpp` (Exposure, Read, AfterRead, DevEntry, CorrectRaw, OpdBeforeNR, Develop, Marble, FeatureEffect, AfterEffect, Encode, AfterEnc, SortJpeg, DevExit); `0x00` y `0x06` **no tienen nombre** en el firmware (se describe su estructura) y 5 de los 16 selectores los registra código **fuera** de la tabla (`SequenceFilter` en 5 funciones) → hay selectores auxiliares. 9 tests.
- [S113: `[CAM_DMM]`, el gestor de memoria dinámico de la cámara](analysis/s113_cam_dmm/dmm_module.md): 54 trazas (todas de error) en `0x43cce6ae`–`0x43ccf1c3` y la implementación concentrada en **25 funciones contiguas** (`0x439011d8`–`0x43903d5c`); **11 operaciones** (`AllocNew`, `AllocNewRdv` = *rendezvous*, `AllocShare`, `Free`, `FreeRdv`, `Open`, `Close`, 4 `MemoryHandle::*` y las asíncronas `AsyncAllocNew`, `AsyncAllocRule`, `LoadExtraMap`) y **4 clases de error** (`ERR_DMM_RET_CODE`, `ERR_DMM_DIFFERENT_COMP` con `msg_id`/`my_id`, `ERR_DMM_HANDLE`, `ERR_DMM_OPEN`), más 4 de capa **OSAL** → la frontera DMM↔OSAL es real (S38); el userland `DmmAccess` de `libmprctrl.so` (S37) es **cliente** de este servidor, no una reimplementación. A7S fw3.20: 50/54 mensajes idénticos sin etiqueta. 11 tests.
- [S108: el módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar](analysis/s108_camera_sa/camera_sa.md): la capa de cámara que reporta los errores y el estado del SA (`Camera::SaFuncDrv`, S84) en 13 sub-bloques —APL (27), gestión de memoria (20), `GetAddr` (35), alineación de parámetros (29), paso de mensajes (18), parámetros DUALREC (14), cierre de handles (20), referencias `sa_func_*` (8) y códigos `SA_FUNCDRV_E_*` (3)—; la A7S fw3.20 y el A6300 fw2.01 tienen los **231/231 mensajes idénticos sin la etiqueta**: la fw3.21 solo añade el prefijo de módulo. 4 tests.
- [S110: `Camera::YC`, el motor de imagen de la A6000](analysis/s110_camera_main_yc/yc_engine.md): las **970 trazas** `[CAMERA_MAIN_YC]` (`0x43ca88f6`–`0x43ccd469`) describen el motor que calcula los parámetros del disparo: **API de 8 funciones** (`api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`, `api_YC_SetSaCamDsp`…, `api_YC_DEV_SetCoodinate` `0x437d9d1c`) y **12 jobs** (`job_YC_SetParam`, `job_YC_CalcParam`, `job_YC_ModeManager` `0x4389f29e`, `job_YC_Initialize` `0x438aa574`…), con **141 sub-módulos etiquetados** (`SHD` 219, `ITP` 90, `YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19); mapa **función→traza** de las 970 cadenas en **332 funciones** (960 referenciadas, 10 cadenas muertas) y **119 ficheros fuente** embebidos (`Sequence_*.cpp`, `yc_clp_common.cpp`, `init_cam_SetCamParam.cpp`…). **Diferencial A7S fw3.20**: los mismos mensajes existen sin la etiqueta → **969 de las 970** cadenas son comunes; la única nueva de la fw3.21 es `HD_SWEEP_HOLD =%x` (`0x43cbc27c`). 15 tests.
- [S107: `Camera::CamCore` y la pila de recursos `ResourceStack`](analysis/s107_camcore/camcore_resources.md): las 37 trazas `[CAMCORE]` de la fw3.21 de la A6000 (0 en la A7S fw3.20) describen la librería núcleo del controlador de cámara — SGC (`SgcTable`), RDC/PFR, AIF, `MemoryPool`/`ResourceBase`, `ExlHelper`, el *setter* de DMA, powersave y corrección de defectos (RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6`, `N6Camera7CamCore13SplitRdcImageE` `0x43cb0b94`); la pila `ResourceStack` (adquisición/liberación de recursos de CamCore, RC y DFE) se consume desde el gestor de captura (`[IMAGING_CAP]` `0x43ca10d1`–`0x43ca120f`). La fw3.21 **añade la etiqueta** `[CAMCORE]:`: los mismos mensajes (`ExlHelper`, `MonPowersave`, `ResourceStack)`) ya existían en la A7S sin etiqueta. 9 tests.
- [S106: `IMAGING_CAP`, el gestor de captura still de la A6000](analysis/s106_imaging_cap/imaging_cap_architecture.md): 697 trazas (`0x43c9b335`–`0x43ccab72`) y **83 nombres de fichero fuente embebidos** (`0x43ca8e14`–`0x43cb0cbe`) que reconstruyen el subsistema; **motor de secciones con 17 entradas** (`{id, manejador}` en `0x43ff8fb4`, 14 de ellas con su `Capture<Etapa>_Selector.cpp`), CapMgr con tabla de salto de 16 entradas, canal CAIF (`CAP_REQ`/`CAP_DATA`/`CAP_V_COM`), 8 modos `MODE_CAP*` del CamCore y la capa `ImageParam_Capture`/`RawMemManager`/DMM; esquema **PIC** de referencias a cadenas verificado (`694/697` referenciadas, 3 muertas); en la A7S fw3.20 el mismo subsistema **no lleva la etiqueta** `[IMAGING_CAP]`. 0 menciones del obturador → S51 sin efecto.
- [S105: panorámica/barrido (sweep), bracketing e intervalo](analysis/s105_panorama/panorama_bracket_interval.md): `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un campo de 2 bits del contexto `0x43e9b548` y, en el valor 2, pide la petición `0x301f` (`"!!! Can't send Panorama cmd"`); cadena `Stage_InitializeSweepAndSpoolBranch` → `PanoramaSweepStart` (`0x437e6b3c`) → `UpdateSweepCanvas` → `PanoramaSweepEnd` → `seq_panoramaClippingDecode` → `PanoramaStitch` (`0x438bcef8`); bracketing solo en el firmware como `lc_BracketAF.cpp` (`0x43ca79ba`); intervalo con `GetCaptureIntervalResource` (`0x437df338`), semáforo OSAL `CAPTURE_INTERVAL` y control por PTM (`[SDF] interval(PTM)` `0x43c7a1a5`, límite 900000 → `interval_ptm over 10[sec]`). 305 tests.
- [S104: prefijos de traza exclusivos de la A6000 sin decodificar](analysis/s104_prefixes/a6000_prefixes.md): seis prefijos que la A7S fw3.20 no tiene — `ADC_DEBUG` (ADC de 12 canales del LIRO), `AVR` y `AVOUT` (accesorios de `ACCY`), `ADR` (campo de dirección, no un módulo), `BKID` (*backup ID*) y `CAMCORE` (la librería `Camera::CamCore`); corrige S73 (cinco cadenas `ADJ ADC`, no cuatro).
- [S103: el subsistema SDF — la capa de *dataflow* de imagen still](analysis/s103_sdf/sdf_module.md): `[SDF]` (477 trazas) es el **ejecutor de trabajos de imagen still** al que el gestor de captura (`IMAGING_CAP`) envía **33 `MSG_ID_SDF_*`** (resize/rotate, encode/decode JPEG, CCNR, panorámica, THM, develop resize, face resize…); los 15 `[SDF_ERR]` son casi todos comprobaciones de **PTM** (el temporizador de imagen); en el userland, `OBJAVBBCBASECLASS::SdfCh`.
- [S102: menú principal (botón MENU), cadena de carga y apertura](docs/capture/s102-menu-principal.md): `libObj.so` → `viewUnified2.so` (registro de ~150 vistas, índices = `Vn` del log real) → `viewUnified3..8`; vistas BASE_MENU/GLOBAL_MENU/SETTINGMENUX/FNMENU; `DefRootView::ActionOpen*` es el árbitro de arranque, no la tecla MENU; evento de MENU sin demostrar. Anexos: [APK por función](analysis/apk-por-funcion/README.md), [decompilación de apps](analysis/decomp-apk/README.md).
- [S101: selector del tipo de mecanismo y consumidores de los campos de ajuste (A6000 vs A7S)](docs/capture/s101-conclusions.md): `+0x238`/`+0x280` solo se escriben; Darwin nunca fija el tipo (3 lectores, 0 escritores en A6000/A7S/A6300); selector A6000 `0x4379316a` sobre `[G+0x808]&7` (por defecto tipo 0) frente al de A7S por el byte `+0x7a`; plan de pruebas físicas pendientes. S51 se mantiene.
- [S100: el contrato de comandos del ADF (firmware) ↔ `AdfCh` (userland)](analysis/s100_adf_contract/adf_command_contract.md)
- [S98: `libBizFw.so` — el orquestador userland y el puente con el ADF](analysis/s98_bizfw/bizfw_bridge.md)
- [S99: la arquitectura del userland — las capas de `libObj.so`](analysis/s99_userland/userland_architecture.md)
- [S97: sincronización audio/vídeo del codificador](analysis/s97_encsync/encoder_sync.md)
- [S94: la API HAPI de la app remota](analysis/s94_hapi/hapi_api.md)
- [S96: modos de captura — `drive_mode`, `CapMode` y la tabla 69 → 14 ShdMode](analysis/s96_modes/capture_modes.md)
- [S92: la base de datos de medios — SceneInfo, MovieFile e índice](analysis/s92_mediadb/media_database.md)
- [S95: los ficheros que la cámara lee y escribe](analysis/s95_files/file_inventory.md)
- [S90: reproducción de vídeo — PlayArranger, VFC y VDISP](analysis/s90_playback/playback.md)
- [S93: el bus de mensajes OSAL del userland](analysis/s93_osal_bus/osal_message_bus.md)
- [S87: almacenamiento, sistema de archivos y tarjeta](analysis/s87_storage/storage_filesystem.md)
- [S91: submódulos del framework ADF (ADJ, SYSND, GS, FACE, AFNR, CH_SRC)](analysis/s91_adf/adf_submodules.md)
- [S82: AutoFraming y las etapas de control del pipeline](analysis/s82_autoframing/autoframing_stages.md)
- [S88: GOLFSHOT (disparo de golf por sonido) y MOTIONSHOT](analysis/s88_shotmodes/golfshot_motionshot.md)
- [S89: el módulo `IDT`/`IDT_OPD` — mapas del imager, FOPD e IDTSA](analysis/s89_idt/idt_opd_maps.md)
- [S77: Creative Style y balance de blancos](analysis/s77_pp/picture_profile_creative_style.md)
- [S86: el subsistema del visor — `VDF` (marco de display) y `VEF` (visor electrónico)](analysis/s86_vdf_vef/vdf_vef_viewfinder.md)
- [S85: `CLK_CTRL` (control de reloj) y `VPH_API` (API del vídeo del visor)](analysis/s85_clk_vph/clk_ctrl_vph_api.md)
- [S72: wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand")](analysis/s72_wlan/wlan_playmem.md)
- [S84: el API del motor de imagen (SA) — catálogo de `sa_func_*`](analysis/s84_sa_api/sa_api_catalogue.md)
- [S83: los módulos "menores" del firmware, decodificados](analysis/s83_modules/minor_modules.md)
- [S81: ADF — framework de arranque, MSGQ, MMGR y comandos DBGCMD](analysis/s81_adf/adf_framework.md)
- [S71: subsistema de detección de caras y objetos (FC/FRC)](analysis/s71_frc/frc_subsystem.md)
- [S80: ZIT — corrección de defectos del sensor (DDC) en el imager](analysis/s80_zit/zit_defect_correction.md)
- [S79: mapa de módulos del firmware por prefijos de log](analysis/s79_modules/module_map.md)
- [S78: parámetros `apc_*` del motor de imagen YC](analysis/s78_apc/yc_apc_params.md)
- [S76: pipeline de captura (etapas `Stage_*`) y motor de imagen](analysis/s76_stages/stage_pipeline.md)
- [S75: ZPD (zone plate detection) — calibración del sensor con datos de la lente](analysis/s75_zpd/zpd_subsystem.md)
- [S73/S74: protocolo de ajuste de fábrica `ADJ_CMD` (panel/EVF/OLED) y `ContrastPlus`](analysis/s73_adj/adjust_cmd_recon.md)
- [S70: reconocimiento del subsistema EIS/gyro](analysis/s70_is/is_gyro_recon.md)
- [S68: gestión de batería, energía y carga (NP-FW50)](docs/capture/s68-battery-power.md)
- [S69: subsistema de audio de la A6000 (línea general)](docs/capture/s69-audio-subsystem.md)
- [S66: montura de lente E-mount (línea general, sin relación con SilentShutter)](docs/capture/s66-lens-mount.md)
- [S64: prueba en cámara de SilentShutter](docs/capture/s64-silent-ram-nvram-test.md)
- [S62: PMCA — inyección de código, service shell y la propiedad `modelName`](docs/capture/s62-pmca-injection.md)
- [S61: origen de los parámetros IMX210 y flujo de mensajes](docs/capture/s61-conclusions.md)
- [S60: emisor de mensajes IMX210 y receptores A7S](docs/capture/s60-conclusions.md)
- [S59: validación cruzada Claude + GPT-6.1 Sol](docs/capture/s59-conclusions.md)
- [S58: productores AE y configuración efectiva A7S Silent](docs/capture/s58-conclusions.md)
- [S57: semántica de ID1/SSB/svd-shd-spl, Silent IMX235, XPI y sincronía P2S](docs/capture/s57-conclusions.md)
- [S56: transporte de registros del IMX210 (IDs = direcciones 16 bit, P2S/DFE0), CISIF = receptor](docs/capture/s56-conclusions.md)
- [S55: origen de los pares GPIO (base de backup BK4), A7S vs A6000](docs/capture/s55-conclusions.md)
- [S54: P4C, tipo de mecanismo 0 y sincronización BIONZ](docs/capture/s54-conclusions.md)
- [S53: parser CAIF de Darwin, A7S vs A6000](docs/capture/s53-conclusions.md)
- [S52: mecanismo Silent Shooting A7S y viabilidad en A6000](docs/capture/s52-parallel-conclusions.md)
- [S51: decisión SÍ/NO sobre exposición totalmente electrónica](docs/capture/s51-decision.md)
- [S50: conclusiones conjuntas Claude + Codex](docs/capture/s50-parallel-conclusions.md)
- [S49: productor de configuración de captura](docs/capture/s49-capture-config-producer.md)
- [S48: proveedor del servicio de registro `+0x1ec`](docs/capture/s48-service-table-provider.md)
- [S47: entrada del payload y orden de C](docs/capture/s47-payload-producer-and-order.md)
- [S46: base VD y escritor del contexto](docs/capture/s46-vd-base-and-context-identity.md)
- [S45: contexto y consumidor real del timing IMX210](docs/capture/s45-context-identity-and-physical-closure.md)
- [S44: consumidor de registros y tabla de modos](docs/capture/s44-register-consumer-mode-table.md)
- [S43: tabla PIC y códigos de modo IMX210](docs/capture/s43-exposure-mmio-and-lock-codes.md)
- [S42: identidad de la llamada de exposición](docs/capture/s42-exposure-call-identity.md)
- [S41: productores de mensajes y snapshots](docs/capture/s41-message-origin-imx210.md)
- [S40: origen del contexto de modo](docs/capture/s40-context-origin-imx210.md)
- [S39: enum de imagen y discriminador APL](docs/capture/s39-image-format-apl.md)
- [S38: frontera DMM/OSAL en av-cam](docs/capture/s38-dmm-osal-static-frontier.md)
- [S37: definidor DMM en libmprctrl](docs/capture/s37-libmprctrl-dmm-extents.md)
- [S36: memoria de libInfraScalarMpr](docs/capture/s36-libinfra-scalar-mpr-memory.md)
- [S35: objetos DFE y frontera estática APL/IRQ](docs/capture/s35-dfe-objects-static-frontier.md)
- [S34: APL/DMA frente a VD e interrupciones](docs/capture/s34-apl-dma-vd-interrupts.md)
- [S33: origen de los handles YC](docs/capture/s33-yc-rendezvous-producer.md)
- [S32: callbacks VD y SyncYCout](docs/capture/s32-vd-callbacks-sync-ycout.md)
- [S31: subsistema CAMERA_MAIN_SYNC/DFECore](docs/capture/s31-camera-main-sync-strings.md)
- [S30: receptor y retorno de EncodeStill](docs/capture/s30-pipelines-capture-encode.md)


## Agentes (Claude Code, Codex/ChatGPT, DeepSeek Harness)

Reglas en `AGENTS.md` y `CLAUDE.md`; skills en `.claude/skills/` y `.agents/skills/`
(copias idénticas, verificadas por `tests/test_agent_skills_sync.py`). Instalación de
REA/Ghidra, MCP y arranque de sesión: [docs/agent/README.md](docs/agent/README.md).
Para ChatGPT web: [docs/agent/chatgpt-pack.md](docs/agent/chatgpt-pack.md).
Entorno: `python scripts/agent/check_env.py`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Documentación: arquitectura, captura (`docs/capture/`), historial, referencias |
| `analysis/` | Un directorio por hito (`sNN_*`), con informe y datos |
| `tests/` | Un test por hito + utilidades |
| `scripts/` | Herramientas, conocimiento (`scripts/knowledge/`), agente |
| `knowledge/` | Estado (`CURRENT.md`), progreso e índices derivados |
| `src/` | Inventario, atlas, LIRO |
| `tools/`, `reports/`, `references/`, `research/`, `work/` | REA/Ghidra, informes, fuentes públicas, notas |
| `firmware/` | Firmware Sony original/extraído (en `.gitignore`, no se publica) |

## Subproyecto: obturador electrónico

- Pruebas físicas pendientes (no ejecutadas): [docs/capture/physical-test-plan.md](docs/capture/physical-test-plan.md).
- Decisión vigente: **no parchear** (S51, [decisión SÍ/NO](docs/capture/s51-decision.md)); categoría E, evidencia insuficiente; ni viabilidad ni imposibilidad demostradas.
- Conclusiones: [S50](docs/capture/s50-parallel-conclusions.md) · [S52 viabilidad A6000](docs/capture/s52-a7s-a6000-feasibility.md) · [EFCS](docs/capture/efcs-capture-selector.md) · [estado Silent](docs/capture/silent-shutter-status.md) · [traza](docs/silent-shutter-trace.md).
- Referencia comparativa: A7S 3.20 ([A6300 vs A6000](docs/capture/a6300-silent-comparison.md)).

## Documentos generales

[Alcance](docs/project-scope.md) · [Arquitectura](docs/architecture/README.md) · [Captura](docs/capture/README.md) · [Inventario físico](docs/hardware-inventory.md) · [Atlas ELF](docs/elf-classification.md) · [Dependencias](docs/subsystem-dependencies.md) · [Arranque y recuperación](docs/boot-and-recovery.md).

## Reproducción local sin instalar paquetes

Desde este directorio:

```sh
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.inventory firmware reports/firmware-inventory.json
python3 -m src.atlas
python3 -m src.liro firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin reports/silent-liro-dispatch.json --base 0x43541000 --table 0xabe30c --count 220
python3 -m unittest discover -s tests -v
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/ruff check src tests
/home/nicolas/Documents/GPREMIUM/ingreso-agentes/.venv/bin/mypy --ignore-missing-imports src
```

Extracción: `7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater` y `/home/nicolas/.local/share/pmca-venv/bin/python references/fwtool/fwtool.py unpack -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat -o firmware/extracted/fw321`.

La CLI real necesita `-f` y `-o`: el ejemplo posicional del proyecto base no corresponde a esta versión.
La extracción WBI por CLI falla al intentar interpretar recursivamente una sección como ext2. La alternativa ejecutada fue iterar `fwtool.sony.wbi.readWbi`, guardar `chunk.contents.read()` y registrar `physicalAddr`, `virtualAddr`, tamaño y SHA-256 en `reports/wbi-sections.json`. Véase el procedimiento completo en `docs/firmware-analysis.md`.

679 ELF ARM confirmados por readelf; 45 archivos con coincidencias de palabras
clave en la búsqueda inicial. El inventario total incluye contenedores,
derivados y duplicados: sus tamaños no deben sumarse como memoria del dispositivo.
El atlas reutiliza metadatos por hash y productor; se comprobaron 679 aciertos
en la segunda pasada. Los snapshots REA conservan evidencia, pero no sustituyen
un proyecto persistente de Ghidra ni garantizan evitar una nueva importación.

## Validación

Veintiséis pruebas correctas; ruff y mypy sin avisos en `src tests`. TDD aplicado
a inventario, atlas, símbolos versionados, roles ELF y agregación de
dependencias, referencias Thumb y extracción LIRO. Registro actual:
reports/shutter-validation.md; registro previo: reports/atlas-validation.md. Dos archivos
auxiliares del DMG no legibles se registran como errores; el payload y el
firmware están inventariados y los 679 ELF se analizaron sin errores.

Repositorio Git inicializado y publicado en `github.com/nicolvus/a6000-fw-decomp` (rama `main`); desde S54 cada fase se commitea y se sube. `firmware/` está en `.gitignore`: los artefactos de firmware no se publican. Inicialmente no se instalaron paquetes. Después, el usuario autorizó hacer funcionar REA: se instaló REA localmente y se extrajeron Ghidra/JDK portables. No se ejecutaron programas del firmware.

## REA operativo

REA 6.5.0 instalado en `tools/rea` con versión y dependencias fijadas en package-lock.json. Ghidra 12.1.4 y Temurin JDK 21 portables, sin modificar paquetes del sistema. Descargas y hashes verificados: `reports/rea-provider-downloads.json`. Registro MCP aplicado a `/home/nicolas/.codex/config.toml`, con respaldo `.rea.backup`; reiniciar Codex para cargarlo.

```sh
./scripts/rea doctor --client codex --provider ghidra --json
./scripts/rea analyze "$PWD/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha16_unpacked_unpacked/lib/libcamera.so" --provider ghidra --json
```

Comprobado: protocolo MCP initialize, 207 herramientas, binary_session, diagnóstico Ghidra/Codex y análisis ARM real. En este sandbox, la comprobación Java desde Node requiere ejecución autorizada fuera de la restricción EPERM; no confundir ese fallo con ausencia del JDK. Binwalk, Unblob y JADX siguen pendientes; no son necesarios para el ELF ya extraído.

## Empezar desde cero (clon nuevo + firmware 3.21 recién descargado)

**Para agentes de IA:** ejecutar `scripts/agent/bootstrap.sh` (idempotente, `--dry-run` disponible) y seguir el runbook [docs/agent/bootstrap-desde-cero.md](docs/agent/bootstrap-desde-cero.md) (verificación, orientación, REA, ciclo de fase y límites). Lo siguiente es el desglose manual de esos mismos pasos.

Los binarios (firmware, Ghidra, JDK, `node_modules`, `.venv`) no están en Git: se reconstruyen así.
Todo desde la raíz del repo; Linux x86_64.

```sh
# 1. Clonar y entrar
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter && cd sony-a6000-electronic-shutter

# 2. Firmware oficial 3.21 (Mac updater) y verificación
mkdir -p firmware/original && cd firmware/original
curl -L -o Update_ILCE6000V321.dmg "https://support.d-imaging.sony.co.jp/download/NEX/AcicwqgUEQ/Update_ILCE6000V321.dmg?fm=am"
sha256sum Update_ILCE6000V321.dmg   # esperado: 844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
cd ../..

# 3. Entorno Python (herramientas, tests, grafo de conocimiento)
python3 -m venv .venv && . .venv/bin/activate && pip install pytest ruff mypy pyyaml capstone unicorn

# 4. Desempaquetar con fwtool (vendorizado en references/fwtool; necesita sus dependencias Python, ver su README)
7z x firmware/original/Update_ILCE6000V321.dmg -ofirmware/extracted/updater
python references/fwtool/fwtool.py unpack \
  -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat \
  -o firmware/extracted/fw321
# Si falla la extracción WBI anidada: procedimiento alterno en docs/firmware-analysis.md
# Comprobación: firmware/extracted/fw321/firmware.fdat debe tener SHA-256
#   603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90 (firmware/hashes/sha256.json)

# 5. Inventario y atlas ELF (679 ELF ARM esperados)
python3 -m src.inventory firmware/extracted/fw321 reports/inventory.json
python3 -m src.atlas

# 6. REA + Ghidra + JDK locales (versiones y hashes en reports/rea-provider-downloads.json)
(cd tools/rea && npm ci)                      # rea-agents 6.5.0 (Node 22/24)
mkdir -p tools/providers   # descomprimir aquí ghidra_12.1.4_PUBLIC y jdk-21.0.12.1+1 (URLs en el JSON)
./scripts/rea doctor --client codex --provider ghidra --json

# 7. Binario principal para REA: av-cam.bin (base 0x43541000, ARM)
mkdir -p analysis/rea-independent/input
cp firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin analysis/rea-independent/input/

# 8. Comprobar todo y arrancar el grafo de conocimiento
python scripts/agent/check_env.py --sha
python3 scripts/knowledge/index_docs.py && python3 scripts/knowledge/build_graph.py
python -m pytest tests -q
```

Después de instalar:

1. Leer [knowledge/CURRENT.md](knowledge/CURRENT.md) y [docs/STATE.md](docs/STATE.md) (restricciones y política de RE).
2. Registrar los MCP `rea` y `sony-a6000-knowledge` ([docs/agent/README.md](docs/agent/README.md#mcp-claude-code-y-codex)); ajustar las rutas absolutas de `.mcp.json` a tu clon.
3. Abrir **una sola** sesión REA (`av-cam.bin` tarda ~8 min en frío): `python analysis/rea-independent/bin/session_daemon.py <sock> "$(cat analysis/rea-independent/exp2-open-args.json)"` (ajustar `path` al clon) y consultar por lotes con `bin/q.py <sock> guion.json`; cerrarla al acabar el hito.
4. Antes de reutilizar un hallazgo: skill `contradiction-audit`; antes de buscar a mano: `knowledge-navigation`; tras editar `.md`: `knowledge-maintenance`.
5. Reglas que no cambian: sin ejecutar firmware, sin flasheo, REA primero y verificar lo decisivo contra bytes. Foco actual: obturador electrónico (decisión vigente S51: no parchear).
6. Para saber qué falta, ver [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) y los «Próximo» del final de [knowledge/PROGRESS.md](knowledge/PROGRESS.md).
