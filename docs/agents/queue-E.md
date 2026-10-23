# Cola carril E (Nemotron 3 Ultra Free) — módulos exclusivos de A6000 pendientes (S600+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

Tema: decodificación de módulos exclusivos de la A6000 fw3.21 (0 en A7S y A6300) no cubiertos por A/B/C, con comparación. Foco inicial: gestores de cámara y escalar.

- DONE S600 Decodificar `[CAM_FUNC_MGR]` (43 trazas): exclusiva A6000. Ficheros fuente, funciones, estructuras. → S177
- DONE S601 Decodificar `[CAM_SCALAR]` (34 trazas): exclusiva A6000. → S179
- DONE S602 Decodificar `[REMOTE]` (32 trazas): exclusiva A6000. → S180
- DONE S603 Decodificar `[CAMERA_DSP_APL]`. → S603 (18 trazas, driver APL/SAPL, logging rewrite)
- DONE S604 Decodificar `[LENS_YC]` y `[IMAGING_RAW]`. → S604 (21+20 trazas, Camera::Lens+ODL / RawMemMgr, logging rewrite)
- DONE S605 Decodificar `[JPEG]` (17 trazas): exclusiva A6000. → S605
- DONE S606 Decodificar `[NSX_VOT]` (7 trazas): exclusiva A6000. → S606
- DONE S607 Decodificar `[CAM_CMD]` (6 trazas): exclusiva A6000. → S607
- DONE S608 Decodificar `[MOUNT_INFO]` (6 trazas): exclusiva A6000. → S608
- DONE S609 Decodificar `[CAMERA_IS][DIST]` (5 trazas): exclusiva A6000. → S609
- DONE S610 Decodificar `[HOUSING]` (5 trazas): exclusiva A6000. → S610
- DONE S611 Decodificar `[IMAGING_RSRC]` (5 trazas): exclusiva A6000. → S611
- DONE S612 Decodificar `[MOUNT]` (5 trazas): exclusiva A6000. → S612
- DONE S613 Decodificar `[MOUNT_WARNING]` (5 trazas): exclusiva A6000. → S613
- DONE S614 Decodificar `[ZPD]` (5 trazas): exclusiva A6000. → S614
- DONE S615 Decodificar `[EIS]` (4 trazas): exclusiva A6000. → S615
- TODO S616 Decodificar `[LENS_PDR]` (4 trazas): exclusiva A6000.
- TODO S617 Decodificar `[CAMERA_DEVICE]` (3 trazas): exclusiva A6000.
- TODO S618 Decodificar `[DET_DIR]` (3 trazas): exclusiva A6000.
- TODO S619 Decodificar `[SENSER]` (3 trazas): exclusiva A6000.
- TODO S620 Decodificar `[STABILIZER]` (3 trazas): exclusiva A6000.
- TODO S621 Decodificar `[AVOUT]` (2 trazas): exclusiva A6000.
- TODO S622 Decodificar `[AVR]` (2 trazas): exclusiva A6000.
- TODO S623 Decodificar `[JIRO]` (2 trazas): exclusiva A6000.
- TODO S624 Decodificar `[UTILITY]` (2 trazas): exclusiva A6000.
- TODO S625 Decodificar `[ADR]` (1 traza): exclusiva A6000.
- TODO S626 Decodificar `[CAMERA_DETECT_FC]` (1 traza): exclusiva A6000.
- TODO S627 Decodificar `[EO_SW]` (1 traza): exclusiva A6000.
- TODO S628 Decodificar `[FILE_NUM]` (1 traza): exclusiva A6000.
- TODO S629 Decodificar `[FSYSMODE]` (1 traza): exclusiva A6000.
- TODO S630 Decodificar `[RING_DIAL]` (1 traza): exclusiva A6000.
- TODO S631 Al vaciar, regenerar la cola con los siguientes módulos pendientes del censo S178 (priorizar exclusivos A6000).