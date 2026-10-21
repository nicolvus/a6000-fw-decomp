# S71 — Subsistema de detección de caras y objetos (FC/FRC) de la A6000 fw3.21

**Alcance:** línea de ingeniería inversa **general** de la cámara: el subsistema `Camera::FC` del
`av-cam.bin` (detección de caras, seguimiento de objetos/personas, iconos de cara, retoque y
MakerNote de caras) y su puente con el **acelerador Scalar (SA)**. No es la línea SilentShutter, ni
la montura (S66), ni el AF (`analysis/s63_af/`, otro agente), ni el pipeline (S76), ni ZIT (S80).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** Este documento sustituye al borrador del subagente, que
> contenía errores verificados: (a) direcciones en espacio de ficheros (`0x8060839`) en vez de
> direcciones del binario (`0x43cf0db8`); (b) nombres de búfer inexistentes (`s_temp_icon_mem`,
> `s_param_mem` → los reales son `s_sa_temp_icon_mem` y `s_sa_param_mem`); (c) "SA (Secure Area)" →
> **SA es el acelerador Scalar** (proyecto: SFRA = *ScalarA-ScalarInfra*, `sa_dfdet.bin` = detección
> de caras en el Scalar); (d) semántica inventada para los drivers (BT, FAT, IRO, PMV, STK); (e) un
> **diferencial A7S falso** (los ficheros `FC/` son los mismos 99 en ambas cámaras).

Artefactos: `analysis/s71_frc/frc_subsystem.json`, `tests/test_s71_frc.py`.

---

## 1. Inventario del subsistema (VERIFICADO)

**99 ficheros** `FC/…` embebidos en el blob, **idénticos en A6000 fw3.21 y A7S fw3.20** (0
diferencias). Todos son `.cpp` salvo los de `FC/Alg`, `FC/Seq`, `FC/Drv`, `FC/Lib` y `FC/Misc`, que
también son `.cpp` salvo indicación. Reparto (dirección = inicio de la cadena):

| grupo | ficheros |
|---|---|
| **Alg** | `fc_alg_frc.cpp` (`0x43cf052f`), `fc_alg_smoothing.cpp` (`0x43cf0412`), `fc_alg_remove_overlap.cpp` (`0x43cf042e`), `fc_alg_target_selecting.cpp` (`0x43cf044f`), `fc_alg_tracking.cpp` (`0x43cf0472`), `fc_alg_pre_fdt.cpp` (`0x43cf048d`), `fc_alg_attribute.cpp` (`0x43cf04fc`), `fc_alg_tracking_obj_color.cpp` (`0x43cf05b4`), `fc_alg_tracking_obj.cpp` (`0x43cf05d9`), `fc_alg_extract_color.cpp` (`0x43cf05f8`), `fc_alg_blink.cpp` (`0x43cf071f`), `fc_alg_exif_face_data.cpp` (`0x43cf0737`), `fc_alg_exif_makernote.cpp` (`0x43cf0758`), `fc_alg_normalize.cpp`, `fc_alg_object.cpp`, `fc_alg_pmv.cpp`, `fc_alg_select_key.cpp`, `fc_alg_tracking_face_object.cpp`, `fc_alg_track_init.cpp` |
| **Seq** | `fc_data_frc.cpp` (`0x43cf0518`), `fc_seq_attribute.cpp` (`0x43cf04ca`), `fc_seq_mon_object.cpp` (`0x43cf0563`), `fc_data_mon_object.cpp` (`0x43cf0580`), `fc_seq_mon_frame.cpp` (`0x43cf063d`), `fc_data_track_human_frame.cpp` (`0x43cf0659`), `fc_data_track_object_frame.cpp` (`0x43cf067e`), `fc_seq_vae.cpp` (`0x43cf06a4`), `fc_data_vae.cpp` (`0x43cf06ba`), `fc_seq_oneshot.cpp` (`0x43cf0705`), `fc_seq_touch.cpp` (`0x43cf082f`), `fc_seq_prc.cpp` (`0x43cf088a`), `fc_seq_re_init.cpp`, `fc_seq_rec_face.cpp`, `fc_seq_track_init.cpp`, `fc_seq_pmv.cpp` (`0x43cf697b`), `fc_seq_mon_face.cpp`, `fc_seq_base.cpp` |
| **Drv** | `fc_drv_fat.cpp` (`0x43cf04e6`), `fc_drv_iro.cpp` (`0x43cf059e`), `fc_drv_vae.cpp` (`0x43cf06d1`), `fc_drv_prc.cpp` (`0x43cf08a0`), `fc_drv_bt.cpp` (`0x43cf603a`), `fc_drv_edt.cpp` (`0x43cf6fd9`), `fc_drv_iro2g.cpp` (`0x43cf7044`), `fc_drv_frc.cpp`, `fc_drv_fdt.cpp`, `fc_drv_vat.cpp`, `fc_drv_detsa.cpp`, `fc_drv_pmv.cpp`, `fc_drv_stk.cpp` |
| **SaFuncDrv** | `recog_sa_drv.cpp` (`0x43cf0545`), `fc_sa_frc2_drv.cpp` (`0x43cf0a5c`), `fc_sa_frc2_mmu.cpp` (`0x43cf0bf1`) |
| **Feature** | `fc_feature_mon_face.cpp` (`0x43cf04a7`), `fc_feature_mon_object.cpp` (`0x43cf0618`), `fc_feature_vae.cpp` (`0x43cf06e7`), `fc_feature_capture.cpp` (`0x43cf0779`), `fc_feature_retouch.cpp` (`0x43cf079b`), `fc_feature_panorama.cpp` (`0x43cf07bd`), `fc_feature_develop.cpp` (`0x43cf07e0`), `fc_feature_panorama_face_meta.cpp` (`0x43cf0802`), `fc_feature_touch_for_scanaf.cpp` (`0x43cf085f`), `fc_feature_prc_retouch.cpp` (`0x43cf08b6`), `fc_feature_base_setting.cpp` (`0x43cf08dc`), `fc_feature_beauty_effect.cpp`, `fc_feature_rec_face.cpp`, `fc_feature_retouch_art.cpp`, `fc_feature_develop_art.cpp`, `fc_feature_pmv.cpp`, `fc_feature_re_init.cpp`, `fc_feature_touch.cpp`, `fc_feature_track_init.cpp`, `fc_feature_scalara_oneshot.cpp`, `fc_feature_mon_obj_for_face.cpp` |
| **Api** | `fc_api_camera_param.cpp`, `fc_api_cap.cpp`, `fc_api_idt.cpp`, `fc_api_monitoring.cpp`, `fc_api_startup.cpp`, `fc_api_tracking.cpp`, `fc_api_callback.cpp`, `fc_api_face_record.cpp`, `fc_api_retouch.cpp` |
| **Lib** | `fc_lib_dds.cpp`, `fc_lib_image.cpp`, `fc_lib_message.cpp`, `fc_lib_if_flash.cpp`, `fc_lib_print.cpp`, `fc_lib_record_log.cpp`, `fc_lib_resource.cpp` |
| **Misc** | `fc_detect_cb_handler.cpp` (`0x43cf0903`), `fc_prc_request_controller.cpp` (`0x43cf0924`), `fc_scalara_detect_cb_handler.cpp` (`0x43cf0a33`) |
| **raíz** | `fc_api.cpp`, `fc_top.cpp`, `fc_tsk_start.cpp`, `fc_seq_controller.cpp` |

## 2. Las clases (RTTI mangled) (VERIFICADO)

`N6Camera2FC5FCTopE`, `N6Camera2FC11FeatureBase<…>`, `N6Camera2FC12SequencePool<…>`,
`N6Camera2FC14FeatureMonFaceE`, `N6Camera2FC20FeatureMonObjForFaceE`,
`N6Camera2FC23FeaturePanoramaFaceMetaE`, `N6Camera2FC15FeaturePanoramaE`,
`N6Camera2FC21FeatureCancelPanoramaE`, `N6Camera2FC10FeaturePmvE`, `N6Camera2FC13FeatureReInitE`,
`N6Camera2FC21FeatureTouchForScanAFE`, `N6Camera2FC12FeatureTouchE`,
`N6Camera2FC16FeatureTrackInitE`, `N6Camera2FC17FeatureAttributeE`, `N6Camera2FC17SequenceAttributeE`,
`N6Camera2FC15SequenceMonFaceE`, `N6Camera2FC17SequenceMonObjectE`, `N6Camera2FC15SequenceOneshotE`,
`N6Camera2FC11SequencePmvE`, `N6Camera2FC11SequencePrcE`, `N6Camera2FC15SequenceRecFaceE`,
`N6Camera2FC14SequenceReInitE`, `N6Camera2FC13SequenceTouchE`, `N6Camera2FC17SequenceTrackInitE`,
`N6Camera2FC18FeatureBaseSettingE`, `N6Camera2FC19FeatureCaptureDummyE`,
`N6Camera2FC14FeatureCaptureE`, `N6Camera2FC17FeatureDevelopArtE`, `N6Camera2FC14FeatureDevelopE`,
`N6Camera2FC19FeatureBeautyEffectE`, `N6Camera2FC22FeaturePrcBeautyEffectE`,
`N6Camera2FC17FeaturePrcRetouchE`, `N6Camera2FC14FeatureRecFaceE`, `N6Camera2FC17FeaturePrcRecFaceE`,
`N6Camera2FC17FeatureRetouchArtE`, `N6Camera2FC20FeaturePrcRetouchArtE`,
`N6Camera2FC14FeatureRetouchE`, `N6Camera2FC21FeatureScalarAOneshotE`,
`N6Camera2FC24FeaturePrcScalarAOneshotE`.

**Punto clave:** `FeatureScalarAOneshot` y `fc_scalara_detect_cb_handler.cpp` conectan el subsistema
FC con **ScalarA** (el acelerador Scalar), coherente con el resto del proyecto (SFRA =
*ScalarA-ScalarInfra*, `sa_dfdet.bin` = detección de caras en el Scalar).

## 3. El puente con el acelerador Scalar (SA) (VERIFICADO)

Ficheros: `FC/SaFuncDrv/fc_sa_frc2_drv.cpp` (`0x43cf0a5c`), `FC/SaFuncDrv/fc_sa_frc2_mmu.cpp`
(`0x43cf0bf1`), `FC/SaFuncDrv/recog_sa_drv.cpp` (`0x43cf0545`).

- **Adquisición de recursos en los dos núcleos**:
  `AcquireRes 0x%x<-0x%x Core2 user[0]:[ 0x%08x, 0x%08x ]` (`0x43cf094a`),
  `… Core3 user[1]:…` (`0x43cf0981`),
  `release res error: RES_SA_FOR_FRC2 = 0 (0x%x)` (`0x43cf09b8`).
- **Búferes propios** (nombres reales): `s_sa_temp_icon_mem.Alloc` (`0x43cf0bd8`),
  `s_sa_temp_icon_mem.Free` (`0x43cf0b64`), `s_sa_param_mem.Alloc` (`0x43cf0bc3`),
  `s_sa_param_mem.Free` (`0x43cf0b7c`), `s_mmu_memhundle Free Error:%d` (`0x43cf0b90`).
- **MMU**: `MakeMmu - SA_MMU_NUM_MEM_ERR :%d` (`0x43cf0c11`), `MakeMmu - MMU_ID AllocError :0x%x`
  (`0x43cf0c32`), `MakeMmu - MakeExtentError[%d->%d] :0x%x` (`0x43cf0cf9`),
  `FC MMU param open error %d` (`0x43cf0aaf`).
- **Ciclo de cálculo**: `error_status (cancel): %d` (`0x43cf0a7c`), `SA result (cancel): NULL`
  (`0x43cf0a96`), `ddl_saCalcCancel: %d` (`0x43cf0afb`), `warn: int_fact=NOT_FINISH`
  (`0x43cf0ad4`), `int_fact: %d` (`0x43cf0aee`), `alloc size:%d, expected:%d` (`0x43cf0b39`),
  `SA result: NULL` (`0x43cf0b54`), `Cancel OK` (`0x43cf0aca`).
- **Iconos de cara**: `FRC: Init FaceIcon` (`0x43cf0d6c`), `FRC: Update FaceIcon :%d` (`0x43cf0d7f`),
  `FaceIconInfo::Free() handle:%d` (`0x43cf0d98`), `FaceIconInfo::Alloc() handle:%d` (`0x43cf0db8`).
- **Respaldo/restauración del estado de iconos**: `Backup() error(clear) %d` (`0x43cf0dd9`),
  `Backup():data` (`0x43cf0e0a`), `Restore():info` (`0x43cf0e3e`).
- **Temporizadores**: `timer not alloc (%d)` (`0x43cf0b10`), `UTimer not available` (`0x43cf0bae`).

## 4. El módulo `[FACE]` (70 trazas) (VERIFICADO)

Estados: `[FACE]: [INIT]`, `[BASE]`, `[MON]`, `[IMME]` (inmediato), `[ATTR]` (atributos),
`[STOP]`, `[STOP MON]`, `[STOP IMME]`, `[STOP ALL]`, `[INT ATTR]`, `[FDT INT]`, `[DATA]`.
Errores característicos: `SA Return Error : %08x`, `Face Num Error`, `Face Region Error`,
`FDT Int Error: factor=%d, sa_stat=%d`, `[FDT INT] PART CB is Null`, `Monitoring Search Failed. : L218 %08x`,
`Immediate Search Failed. : L107`.

## 5. El módulo `[TRK]` (216 trazas): los cinco Detectores (VERIFICADO)

Cada detector tiene su propio prefijo y su **núcleo SA**:

| detector | trazas | núcleo | evidencia de su función |
|---|---|---|---|
| **DETSA** | `[TRK]: [DETSA] …` | Core2 | `CORE2 RESOURCE CONTENTION`, `PARAM ERR !! face_num : %d`, `PARAM ERR !! image_address` |
| **EDTSA** | `[TRK]: [EDTSA] …` | Core3 | `CORE3 RESOURCE CONTENTION`, `Face size is too small`, `VGA/QVGA/160, <w,h>`, `face : [%d,%d,%d,%d]`, `angle : %d`, `node : %d`, `hue_range`, `saturation_range`, `value_range` |
| **IRO2G** | `[TRK]: [IRO2G] …` | Core2 | `ALIGNMENT ERR`, `HUE ERR`, `HEIGHT ERR`, `ValidWidth ERR`; driver `idt_iro2G_stop` |
| **PMV** | `[TRK]: [PMV] …` | Core3 | `Param GM conf_th1/conf_th2`, `Affine_err_thresh`, `Vector_thresh`, `Motion_frame_num`, `Cont_block_thresh` → **tracking geométrico por vectores de movimiento**; `idt_pmv_start`, `PMV GetResult() rtn` |
| **STK** | `[TRK]: [STK] …` | Core2 | `Saliency CB`, `TouchSimilarity CB`, `ColorSimilarity CB`, `idt_stk_start_auto_saliency`, `idt_stk_start_touch_similarity`; parámetros `p_saliency`, `p_similarity`, `p_hsv_xyz`, `p_saturation_table`, `p_yuv422`, `box af_island_*` → **saliencia y similitud (toque/color)** |
| **BT** | `[TRK]: [BT] …` | — | `fg_area`, `bg_area`, `detect_area`, `lost_fg_area`, `min/max_obj_size`, `bayes_map_level`, `gaussian_map_level`, `adaptive_thres`, `big_obj_size_thres`, `af_rect_thres`, `disp_rect_thres`, `color_mask_thres` → **detección de objetos con área de primer plano/fondo y mapas bayesianos** |

**Corrección:** el borrador atribuía a BT "brillo/toque", a IRO "infrarrojo" y a STK "skin tone
tracking"; la evidencia real es la de la tabla anterior.

## 6. Los drivers y su semántica (VERIFICADO por los nombres de función)

| driver | evidencia | lectura |
|---|---|---|
| `fc_drv_edt.cpp` | `idt_edt_start`, `idt_edt_get_result`, cadena literal `EyeDetection` | **detección de ojos** |
| `fc_drv_fat.cpp` | `ProcessFat::startAttributeDetection`, `ProcessFat::getAttributeResult`, `cancel_attribute_search`, `start_monitoring_search`, `start_immediate_search` | **atracción de atributos de cara** (búsqueda de caras para atributos) |
| `fc_drv_frc.cpp` | `index error : %d (face_num=%d)` | **FRC** (reconocimiento) |
| `fc_drv_fdt.cpp`, `fc_drv_vat.cpp`, `fc_drv_detsa.cpp` | `IDT`/`VATR` (`VATR Mem OK`, `VATR Error det/gle`) | detección de caras en el pipeline IDT (S16–S30) |
| `fc_drv_prc.cpp` | `PRC Acquire Error`, `PRC Start Error`, y las features `PrcRetouch`, `PrcBeautyEffect`, `PrcRecFace`, `PrcScalarAOneshot` | **PRC = el grupo de funciones de retoque/procesado de cara** (INFERENCIA) |
| `fc_drv_vae.cpp` / `fc_seq_vae.cpp` | `[TRK]: Vae_Work Alloc_Error`, `Vat Work Alloc Error`, `VOT RefMap Get ERR` | VAE/VAT/VOT: motor de análisis de imagen por voting (NO_VERIFICADO el significado de las siglas) |

## 7. El algoritmo FRC (VERIFICADO)

- `FRC algo: recognized ID=%d`, `FRC algo: swap ID=%d<-%d`, `FRC algo: [record_rank:%d] swap ID=%d<-%d`
  → el algoritmo **reordena los identificadores de cara** según el *ranking* de reconocimiento.
- `FRC error. CREATE_ICON & PRIORITY_RECOGNIZED`, `FRC error. RECOGNIZE & PRIORITY_SELECTED`,
  `FRC algo: skip` → la **prioridad** de reconocimiento gobierna la creación de iconos.
- `Alg::CalcGeneration`, `Alg::ImportAttributeResult`, `Alg::Smoothing`, `Alg::TargetSelecting`,
  `Alg::CalcVelocity` → la capa de algoritmos (suavizado, selección de objetivo, velocidad).
- `Alg::CheckFaceSelectKey` (`fc_alg_select_key.cpp`): selección de cara con cursor
  (`Cursor face err`, `set cursor face`, `update cursor face`).
- **Parpadeo**: `fc_alg_blink.cpp` + `score:%04x -> blink, unblink = %d, %d` → detección de parpadeo.
- **Pre-FDT** (escena para el AF): `PreFdt On: African`, `Scene`, `Bunri` (separación de colores),
  `Hist1`, `Hist2`, `Light_backlight_Hist`, `Light_backlight_Bunri` (en `fc_alg_pmv.cpp`).
- **Cara ↔ objeto**: `fc_alg_tracking_face_object.cpp` con `Face -> ObjTracking`, `ObjTracking->FaceTracking`,
  `Lost -> ObjTracking`, `Face Stabilized (ObjTracking on)`, `TrackingFace Detected:%d` → el
  seguimiento **alterna entre objeto y cara** según la estabilidad.

## 8. Panorámica, retoque y MakerNote (VERIFICADO)

- Panorámica: `fc_feature_panorama.cpp`, `fc_feature_panorama_face_meta.cpp`,
  `void Camera::FC::FCTop::ExecApiStartPanoramaDetection(const void*)`,
  `void Camera::FC::Api::CancelPanoramaSearch()`, `SetPanoramaFaceMeta send message error`.
- Retoque: `fc_api_retouch.cpp` (`BeautyEffect Memory Alloc Error`, `Face Meta Handle Open error`),
  `fc_feature_retouch.cpp`, `fc_feature_retouch_art.cpp`, `fc_feature_beauty_effect.cpp`.
- EXIF/MakerNote: `fc_alg_exif_face_data.cpp`, `fc_alg_exif_makernote.cpp`,
  `Exif Add %x`, `mp_meta_area NULL`, `mp_makernote_area NULL`,
  `FC MakerNote address: 0x%x, size: %d`.
- Registro de caras: `fc_api_face_record.cpp` (`Icon Handle Open error`, `guide frame: (%d,%d)-(%d,%d)`),
  `fc_seq_rec_face.cpp`.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20 (VERIFICADO, corregido)

- Los **99 ficheros `FC/…` son los mismos** en ambas cámaras (0 diferencias).
- Las cadenas `FRC: Init FaceIcon`, `FRC: Update FaceIcon`, `FaceIconInfo::Alloc/Free`,
  `MakeMmu`, `MakeExtent`, `alloc size:%d, expected:%d`, `SA result: NULL` y
  `error_status (cancel)` existen en ambas (con direcciones distintas: `0x43cf0d6c` en A6000,
  `0x43ce5ecd` en A7S).
- **Corrección:** el borrador afirmaba que la A6000 añadía `fc_drv_iro2g.c` y
  `fc_feature_panorama_face_meta.cpp`; ambos existen también en la A7S (`0x43ce9972` y
  `0x43ce5963`).

## 10. Abierto (NO_VERIFICADO)

- Significado de las siglas FDT, VAT, PRC, VAE, VOT, PMV (más allá de la evidencia de sus parámetros).
- Estructura binaria de los mensajes hacia el Scalar y el reparto entre Core2/Core3.
- Algoritmos concretos ejecutados por el SA para FRC (fuera del blob analizado).
- Relación con `analysis/s63_af/` (AF de otro agente) más allá de los ficheros compartidos
  (`fc_feature_touch_for_scanaf.cpp`, `fc_alg_pre_fdt.cpp`).
- Detalles del MakerNote de caras (versión, tags).

## 11. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s71_frc.py -q
```
