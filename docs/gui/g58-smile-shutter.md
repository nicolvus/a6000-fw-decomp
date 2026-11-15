# G58 — Smile Shutter: ya existe de fábrica en la A6000 (15-11-2026)

**Resultado: ya existe de fábrica; objetivo descartado.** La hipótesis (el menú lo omite por la lista de nodos por modelo, como Extra fine en G39) es falsa: la lista de la A6000 sí lo incluye. Sin parche ni CFW.

## 1. Las tres piezas están en el fw 3.21
- (a) Detector en av-cam: `FaceDet::fdet_WriteFaceSmileResult`, `CPafStateSmile`, `###RES_FACE_SMILE### SmileCount`, `faceSmile` en los datos de cara.
- (b) Secuencia en `libObj`: `sendSmileScoreEvt`, `PARAMID_SMILE_SHUTTER_MODE`, `PARAMID_SMILE_DETECTION_SENSITIVITY`, `PARAMID_SMILE_THRESH_HIGH/LOW`, `PARAMID_SMILE_SCORE`, `ActionExeSmileShutterPause/UnPause`; `libScalarDaemon.so` trae `PARAMID_CAMSETTING_SMILE_SHUTTER_MODE`; `wrapperFaceDetectionSmileShutter.so` y `CmnFnWrapper` convierten menú↔enum.
- (c) Menú en `CautionConfig.so`: `CmnViewSettingNodeFaceDetect_SmileShutter` con nodos `FacDetOff`, `ON_PriorityOnResisteredFace`, `ON_NoPriority`, `SmileShutterOn` y sensibilidad `Big/Normal/Slight`; textos en `string_english.uxc` (0xe107 «Smile Shutter», 0xe6ce–0xe6d0). El manual de servicio de la A6000 (`sony-ilce-6000-level3-sm.txt`) también lista «SMILE SHUTTER».

## 2. La puerta por modelo (`_getSubNode`, `CautionConfig.so+0x106da8`)
Lee el tipo de modelo (`0x101c20`, id `0x1070316`) y hace `tbb` sobre `tipo-1` (0x1b casos). Listas: Type00/Type03/Default = 4 nodos (Off, Regist., Normal, **SmileShutterOn**); Type02 = 3 (sin Regist.); Type01 = 2 (Off, On: sin Smile). Tipos 2–15, 20, 22, 23 y >28 → Default. La A6000 es el tipo 29 (G48), que supera el límite `cmp 0x1b` y cae en **Default: Smile incluido**.

## 3. Prueba en el arnés (Sony 3.21 sin overlay, perfil propio `g58smile`, borrado)
- `img/g58-camara-pag5-sonrisa-detec-cara.png`: Cámara pág. 5, fila «Sonrisa/Detec. cara».
- `img/g58-sonrisa-detec-cara-lista.png`: la lista con cuatro iconos: Detección de cara Off, Registrada, On y **sonrisa On** (cuarto icono).
- Límite: el arnés no persiste elecciones (G27-A) y no ejecuta av-cam; no se vio escribir `nvram.json`.

## 4. Qué queda para la cámara
El disparo por sonrisa real (detector, umbral y secuencia) no se puede probar en el arnés. Pendiente de cámara: ajustar la opción y comprobar el disparo (SMILE-CAM).
