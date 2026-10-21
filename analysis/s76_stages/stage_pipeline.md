# S76 — Etapas del procesado de captura (`Stage_*`) y funciones SA asociadas

**Alcance:** línea de ingeniería inversa **general** de la cámara: la **cadena de desarrollo de
imagen** de la A6000 (fw3.21) tal y como aparece en `av-cam.bin`: las *etapas* (`Stage_*`), sus
ficheros fuente internos y las funciones del **SA** (motor de imagen) que invoca cada una. No es la
línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD (`analysis/s73_adj/`), ni ZPD
(`analysis/s75_zpd/`).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

---

## 1. Las 73 etapas (VERIFICADO: cadenas `Stage_*` en `0x43c9ee6c`–`0x43cca4d9`)

El blob incluye el **nombre de la clase/etapa y su fichero fuente**, lo que documenta la arquitectura
del procesado:

| Familia | Etapas (dirección de la cadena) |
|---|---|
| Base y contenedores | `Stage_SACC` (0x43c9ee6c), `Stage_Common.cpp` (0x43cac363), `Stage_DevLater.cpp` (0x43cac51b), `Stage_DualRec.cpp` (0x43cac9f8), `Stage_Notify.cpp` (0x43caccd6), `Stage_WaitControl.cpp` (0x43cad6fd) |
| Panorama | `Stage_Panorama.cpp` (0x43cacf07), `Stage_PanoramaCcnrEncode` (0x43cad0f4) |
| Ramas de disparo | `Stage_InitializeSweepAndSpoolBranch` (0x43cad10d), `Stage_DummyPreReview` (0x43cad160), `Stage_MkOpenBranch` (0x43cad175), `Stage_MkOpenWait` (0x43cad188), `Stage_FaceDetectPreReviewBranch` (0x43cad199) |
| RAW / resize / trim | `Stage_Raw.cpp` (0x43cad1e2), `Stage_ResizeHV.cpp` (0x43cad6ea) + `Stage_RchRcv_Resize*` (0x43cad558–0x43cad784), `Stage_Rch_*`/`Stage_Rcv_Dist*` (0x43cc8417–0x43cc87b1) |
| Imagen (ajustes) | `Stage_Adjust.cpp` (0x43cc6cc6), `Stage_Apollo.cpp` (0x43cc6e0f), `Stage_AutoFraming.cpp` (0x43cc71a3), `Stage_BDRO.cpp` (0x43cc71fa), `Stage_BFNR` (0x43cc7531), `Stage_BOKS.cpp` (0x43cc7569) + `Stage_BoksPre`/`Stage_BoksPost_Boks` (0x43cc78fe/0x43cc790c) |
| Comunicación | `Stage_CaComm.cpp` (0x43cc7b9c), `Stage_CameraHAPI.cpp` (0x43cc7bad) |
| Deconvolución | `Stage_Decomp.cpp` (0x43cc7df8), `Stage_Decomp4SA_ForDualRec` (0x43cc7fae), `Stage_LoadDeconvPsfTbl` (0x43cc8209), `Stage_ExpandDeconvParam` (0x43cc8220) |
| Desarrollo | `Stage_Develop.cpp` (0x43cc82be) |
| Codificación | `Stage_SCNEnc` (0x43cc87cc), `Stage_THMEnc` (0x43cc87d9), `Stage_THMCopy` (0x43cc87fe), `Stage_SCNEncWithTHM` (0x43cc880c) |
| Detección de caras | `Stage_FaceDetect.cpp` (0x43cc8d9d) |
| Reducción de ruido | `Stage_KKNR.cpp` (0x43cc9329), `Stage_MARBLE.cpp` (0x43cc956d), `Stage_OPD.cpp` (0x43cc9785) + `Stage_DevOPDAfterCap` (0x43cc9793) |
| Orientación | `Stage_Orientation.cpp` (0x43cc97b4) |
| SPICA / STAR / soft focus | `Stage_ExpandSpicaParam` (0x43cc98f5), `Stage_SPICA` (0x43cc990c), `Stage_STAR` (0x43cc9dd6), `Stage_SoftFocus.cpp` (0x43cc9f22) |
| Fecha/hora | `Stage_SetDateImageParam` (0x43cc9fb3), `Stage_StillDate.cpp` (0x43cca086) |
| TBOX / YKNR | `Stage_TBOX.cpp` (0x43cca36a), `Stage_YKNR` (0x43cca4d9) |

**El orden en que aparecen las cadenas en el blob sigue el orden del código** (Apollo → BDRO → BFNR
→ BOKS → Decomp → Develop → FaceDetect → KKNR → MARBLE → OPD → Orientation → SPICA → STAR →
SoftFocus → StillDate → TBOX → YKNR), que es el **orden del pipeline de captura** (INFERENCIA).

## 2. Las funciones del motor de imagen (SA) que usa (VERIFICADO)

26 nombres `sa_func_*` distintos en el blob. Las etapas y sus SA comparten nombre, lo que fija la
correspondencia:

| Etapa | SA |
|---|---|
| `Stage_BOKS` | `sa_func_BOKS_{init,init_CONTROL,GetAddr,start,release,exit}` |
| `Stage_Decomp` | `sa_func_DECOMP_{acquire,start,release}` |
| `Stage_SPICA` | `sa_func_SPICA_{acquire,start,release,exit}` |
| `Stage_STAR` | `sa_func_STAR_{acquire,start,release,exit}` |
| `Stage_YKNR` | `sa_func_YKNR_{acquire,start,release,exit}` |
| `Stage_MARBLE` (LFNR) | `sa_func_LFNR_{init,acquire,start,release,exit}` |
| DualRec | `sa_func_DUALREC_BAYER_{acquire,release,exit}`, `sa_func_DUALREC_CLEARVID_{acquire,release,exit}` |
| BDEX | `sa_func_BDEX_{release,exit}` |

Otras etapas que también piden SA (visible en sus logs): `PreDCV` (`sa_func_PreDCV_*`),
`CONTP` (`sa_func_CONTP_*`), `sftfcs` (`sa_func_SFTFCS_*`), `CasNr`/`CasDcvNrDevRch` (`sa_func_NR_*`),
`ZIT` (`sa_func_ZIT_*` con `ZIT_SaOpen/Start/Close`).

## 3. Enlace con el resto del proyecto (VERIFICADO)

- El **SA** es el motor de imagen (funciones `sa_func_*`): ya documentado en S16–S18 y S30.
- `Stage_Apollo` (0x43cc6e0f) es la etapa que invoca `sa_func_APOLLO_*` (`[IMAGING_CAP]: ApolloNrBase
  err:0x%x`, `0x43cca3f4`).
- `Stage_Adjust` (0x43cc6cc6) es la etapa de **ajuste de imagen** (contraste/ganancia) y contiene
  `ContrastPlus_Base` (`0x43cc7bc2`) → la función `ContrastPlus` que aparece en S73.
- `Stage_SPICA` carga ficheros de parámetros desde `/usr/sabin/spica_*_tap_step*.bin`
  (`0x43cb2f9x`): es decir, el procesado **SPICA** toma sus parámetros de ficheros externos.

## 4. Abierto (NO_VERIFICADO)

- Grafo real de dependencias entre etapas (el orden por cadena es INFERENCIA, no el grafo).
- Qué función SA corresponde a cada etapa cuando el nombre no coincide (`PreDCV`, `CasNr`, `ZIT`…).
- Los ficheros `/usr/sabin/spica_*_tap_step*.bin` y `star_kernel_param.bin`: contenido y quién los
  genera (¿son de fábrica o de servicio?).
- Relación entre `Stage_FaceDetect` (S71, otro agente) y el bloque `[FACE]`/`[TRK]`.
- Cuál es la "salida" del pipeline (EncodeJpeg / `Stage_SCNEnc` vs `Stage_THMEnc`).

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s76_stages.py -q
```
