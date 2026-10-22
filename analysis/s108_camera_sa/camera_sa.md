# S108 — Módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar (SA)

**Firmware:** A6000 fw3.21  
**Base virtual:** `vaddr = 0x43541000 + file_offset` (verificada)  
**Total de trazas:** 231 strings `[CAMERA_SA]` únicas en el rango `0x43cc5286 → 0x43cef0d8`

---

## 1. Qué es el acelerador escalar (SA) según el firmware

El módulo `[CAMERA_SA]` es el componente de firmware que supervisa y reporta los errores y el estado del **acelerador escalar (Scalar Accelerator, SA)** de la cámara. El SA es el motor de cálculo paralelo que ejecuta los algoritmos de procesado de imagen (BFNR, BOKS, DECOMP, DUALREC, NFLASH, SPICA, STAR, YKNR, LFNR, KKNR, BDEX, y otros).

Las 231 trazas del módulo `[CAMERA_SA]` son mensajes de error, estado y diagnóstico generados por el código de cámara cuando interactúa con el driver del SA (`Camera::SaFuncDrv`). Estas trazas cubren:

- **Gestión de memoria** (asignación, liberación, validación de direcciones HME).
- **Errores de parámetros** (alineación, dimensiones, rangos inválidos).
- **Manejo de handles** (apertura, cierre y free de recursos).
- **Paso de mensajes** entre el procesador principal y el SA (mailbox, RcvMsg, Ack, Comp).
- **Errores de algoritmos específicos** (DUALREC, YKNR, LFNR, KKNR, NFLASH, SPICA).
- **Validación de modo y configuración** (modo first_mode, modo de captura, parámetros YC).

El SA opera bajo la dirección del driver `Camera::SaFuncDrv`, que provee 19 familias de funciones (`sa_func_*`) catalogadas en S84. El módulo `[CAMERA_SA]` actúa como el observador de nivel superior que reporta errores desde la capa de cámara, mientras que `sa_func_*` son las llamadas al driver de bajo nivel.

---

## 2. Mapa de las 231 trazas por sub-bloque

| Sub-bloque | Cadena(s) | Rango vaddr | Observación |
|---|---|---|---|
| **Módulo APL** | 27 | `0x43cc5286 → 0x43cee903` | Inicialización y cierre APL: errores de `[APL] HW Open/Save`, gestión de unidades (`unit_hndl:0x%x`), llamadas `Open Err`/`Close Error`. |
| **Gestión de Memoria** | 20 | `0x43cec140 → 0x43cecf5e` | `GetZimaNo Err`, `GetMemInfo Err1-5`, direcciones `HME_BaseTar_Addr`/`HME_BaseRef_Addr` inválidas, `HW GetCoreNum`, `HW SetMode`, `MmuMakeParam`, `HW TimeOut`/`Abort`, `Output Ref Img`. |
| **Errores GetAddr** | 35 | `0x43ceca80 → 0x43ceeffc` | Mensajes `GetAddr error` para handles de imagen (`hndl_for_pWork`, `hndl_for_pRawImg`, `hndl_for_pYcImg`, etc.), `hndl_for_kernel`, `hndl_for_fdt`, `hndl_for_src_addr`, `hndl_for_kk_work_addr`, `hndl_for_yk_work_addr`. |
| **Alineación de Parámetros** | 29 | `0x43cecead → 0x43ceee02` | Errores de alineamiento SA: `in_adr`, `out_adr`, `sizex`, `sizey`, `lineofs`, `work_adr`, `flash_add`, `amb_add`, `int_add`, `rc_line_ofs`, `PSF_table_adr`, `PSF_buffer_adr`, alineación de `image_input_psf_table`/`image_output_psf_buffer`. |
| **Parámetros Inválidos** | 2 | `0x43cec8aa → 0x43ceee41` | parámetros fuera de rango: `width`, `height`, `dx1`, `dx2`, `first_mode`, `RawHsize`, `YcHsize`, `cap_addr Error`, `LineOffset`… |
| **Otros (contenido mixto)** | 51 | `0x43cc5286`–`0x43cef0d8` | mensajes que combinan alineación + `GetAddr` o cierre de handles + parámetros: la heurística de clasificación no los encaja en una sola categoría |
| **Paso de Mensajes** | 18 | `0x43cec785 → 0x43ceee78` | Mailbox y comunicación: `AsyncOpen`, `RcvMsg error/ack/comp`, `bandwidth_arg func_code[0x%x]`, `ExecuteSetBandWidthMSG error`, `ExecuteOpenMSG error`, `SA Close Done`, `osal_rcv_msg`, `Wrong Message Received`. |
| **Parámetros Yc DUALREC** | 14 | `0x43cedae3 → 0x43cedf40` | Parámetros YC de DUALREC: `RawHsize`, `RawHofs`, `YcHsize %d %d`, `YcVsize`, `YcHofs`, `bgImage*`, `bgCanvas*`, `sspImage*`, `sspCanvas*`. |
| **Cierre de Handles (imágenes)** | 4 | `0x43cec546 → 0x43cec600` | `CloseHndl for `hndl_for_m_pOverImage`, `hndl_for_m_pMiddleImage`, `hndl_for_m_pUnderImage`, `hndl_for_m_pOutputImage`. |
| **Cierre de Handles (WorkMemArea)** | 3 | `0x43cec63f → 0x43cec6bf` | `CloseHndl for `hndl_for_m_pWorkMemArea0`, `hndl_for_m_pWorkMemArea1`, `hndl_for_m_pWorkMemArea2`. |
| **Cierre de Handles (genéricos)** | 13 | `0x43ced960 → 0x43ceef2f` | `CloseHndl for `pWork`, `pRawImg`, `pYcImg`, `pRegArea`, `pRawImg2`, `PSF_tbl`, `hndl_for_src_addr`, `hndl_for_kk_work_addr`, `hndl_for_yk_work_addr`, `hndl_for_input_raw`, `hndl_for_output_raw`, `pImgIn`, `pImgOut`. |
| **Referencias API SA** | 8 | `0x43cec6ff → 0x43ceef6c` | Mencionan `sa_func_BDEX_exit`, `sa_func_BFNR_release`, `sa_func_BOKS`, `sa_func_LFNR`, `sa_func_KKNR`, `sa_func_NFLASH`, `sa_func_YKNR`, `sa_func_DUALREC_BAYER`. |
| **Errores Especiales** | 4 | `0x43ced103 → 0x43ced58d` | `NOTREACHED`, `sp_cnt is over 4095!`, `Wrong Message Received (result_code = 0x%x)`, `ddl_saCalcStart error func_code[0x%x]`. |
| **Códigos de Error** | 3 | `0x43ced44e → 0x43ced498` | `SA_FUNCDRV_E_OSAL`, `SA_FUNCDRV_E_RSLTCODE`, `SA_FUNCDRV_E_ERRCODE`. |

**Total:** 27+20+35+29+2+18+14+4+3+13+8+4+3+51 = **231 strings** (suma verificada, igual que en `camera_sa.json`)

---

## 3. Relación con subsistemas y otros módulos del firmware

### 3.1 Relación con `Camera::CamCore` (S107)

El módulo `[CAMERA_SA]` es **independiente** de `CamCore`, aunque ambos coexisten en el mismo blob de `av-cam.bin`. Las diferencias clave:

| Característica | `[CAMERA_SA]` | `CamCore` (S107) |
|---|---|---|
| Cadenas `[module]:` | 231 con prefijo `[CAMERA_SA]:` | 37 con prefijo `[CAMCORE]:` |
| RTTI `N6Camera7CamCore8RdcImageE` | No presente | `0x43c906b6` presente |
| RTTI `N6Camera7CamCore13SplitRdcImageE` | No presente | `0x43cb0b94` presente |
| Subsistemas SGC, RDC, PFR, AIF | No applicable | presentes (hipótesis) |
| Funciones `sa_func_*` | reporta errores desde cámara | infraestructura de bajo nivel |

Las strings del módulo `[CAMERA_SA]` reportan errores que provienen del driver `Camera::SaFuncDrv`, no del motor de imagen `CamCore`. Sin embargo, ambos modules comparten el mismo acelerador SA.

### 3.2 Relación con `IMAGING_CAP` (S106)

El bloque `[IMAGING_CAP]` (697 trazas, S106) es el principal consumidor de los recursos del SA. La relación es:

- `IMAGING_CAP` invoca las funciones `sa_func_*` del motor de imagen durante la captura still (S84).
- El módulo `[CAMERA_SA]` reporta errores de esas mismas funciones cuando fallan.
- 92 cadenas en la A6000 contienen `sa_func_` (S84); los errores aparecen tanto en `IMAGING_CAP` como en `[CAMERA_SA]`.
- Ejemplos de superposición:
  - `sa_func_DUALREC_CLEARVID_acquire` → referenciado desde `IMAGING_CAP` (`0x43cac6cf`) y desde `[CAMERA_SA]`.
  - `sa_func_BFNR_acquire` → referenciado desde `IMAGING_CAP` (`0x43cc7390`) y su liberación desde `[CAMERA_SA]` (`0x43cec87c`).
  - `sa_func_NFLASH_*` → invocados desde `IMAGING_CAP` y sus errores reportados desde `[CAMERA_SA]`.

En resumen: `IMAGING_CAP` es el **usuario** del SA durante la captura, y `[CAMERA_SA]` es el **informante** que reporta el resultado de esas operaciones.

### 3.3 Relación con el DFE (Digital Front End)

- Strings del módulo `[CAMERA_SA]` sobre `CloseHndl` y parámetros de memoria pueden entrar en conflicto con el DFE cuando este usa los mismos buffers de imagen.
- La string `0x43cad834` (`[IMAGING_CAP]: DFE Acquire ERR:0x%02x`) y `0x43cad8d6` (`[IMAGING_CAP]: DFE::Release: IMAGER0, DFE_ERR:0x%02x`) en S106 son del bloque IMAGING_CAP, no de `[CAMERA_SA]`, pero ambos operan sobre los mismos recursos de imagen gerenciados por el SA.

### 3.4 Diferencial A6000 vs A7S fw3.20

| Característica | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| Módulo `[CAMERA_SA]` | 231 trazas con prefijo `[CAMERA_SA]:` | **0 trazas** con ese prefijo |
| Los mismos 231 mensajes **sin la etiqueta** | — | **231/231** presentes (comparación texto a texto) |
| Cadenas `sa_func_*` | 92 cadenas en el blob A6000 | 109 cadenas en A7S |
| Familia `NLAP` | Ausente (eliminada) | presente (13 cadenas) |
| Familia `MOTIONSHOT` | Ausente (eliminada); queda `MOTIONSHOTVIDEO` en SFRS | presente |
| Errores `sa_func_*` con prefijo `[CAMERA_SA]:` | presentes (8 referencias API) | sin prefijo (mensajes sin etiqueta) |

**Observación:** la fw3.21 de la A6000 añadió la etiqueta de módulo `[CAMERA_SA]:` a mensajes
que **ya existían** en la A7S fw3.20 sin etiqueta (los 231 textos coinciden uno a uno). La
distinción es de instrumentación, no funcional.

### 3.5 Diferencial A6300 fw2.01

El blob `av-cam.bin` del A6300 (fw2.01) tiene 13 382 836 B (frente a 11 427 236 de la A6000) y
**0** cadenas con el prefijo `[CAMERA_SA]:`; los **231/231** mensajes de la A6000 existen allí
**sin etiqueta**. Es el mismo patrón que la A7S: la etiqueta de módulo es una novedad de la
fw3.21 de la A6000.

> **Corrección de la revisión (agente principal):** el borrador de esta tabla afirmaba que
> `ExlHelper` (5 apariciones) y `MonPowersave` (1) aparecían "con etiqueta `[CAMERA_SA]:`" y
> que el A6300 tenía "un número mayor de trazas por categoría". **Ambas cosas son falsas**:
> `ExlHelper` y `MonPowersave` **no aparecen** en ninguna de las 231 trazas de `[CAMERA_SA]`
> (pertenecen a `[CAMCORE]`, S107) y el A6300 tiene **0** trazas con la etiqueta y los mismos
> 231 mensajes sin ella.

---

## 4. No verificado / abierto

- **Significado de siglas**: El firmware no expande las siglas SA (Scalar Accelerator). El driver `Camera::SaFuncDrv` usa las siglas internamente sin documentación formal.
- **Estructura completa de los parámetros `<X>_START_PARAM`**: Las trazas reportan errores de campos específicos pero no la definición estructural completa de cada parámetro.
- **Relación exacta entre las 8 referencias `sa_func_*` y sus funciones contenedoras**: Solo 8 de las 19 familias `sa_func_*` (S84) tienen trazas directas en `[CAMERA_SA]`; las otras 11 (CONTP, GOLFSHOT, TBOX, SFTFCS, BDEX exit, etc.) no aparecen o aparecen con nombres distintos.
- **Formato interno del mailbox SA**: Las trazas mencionan `bandwidth_arg func_code[0x%x]` y `ExecuteSetBandWidthMSG`/`ExecuteOpenMSG`, pero la estructura binaria del mensaje de mailbox no ha sido desglosada.
- **Por qué 51 strings caen en la categoría "Other"**: Algunas tienen contenido mixto (errores de alineación + GetAddr, o cierre de handles + parámetros inválidos) y no encajan en una sola categoría con la heurística actual.
- **Diferenciales completos A6300 fw2.01**: El análisis comparativo aún está en curso.

---

## 5. Revisión del agente principal

1. **Recuento de la tabla de sub-bloques**: el borrador ponía "Parámetros Inválidos: 17" y
   omitía la categoría "Otros", de modo que las 13 filas sumaban 195 y no 231. Corregido a
   los valores del JSON (**2** y **51**), que sí suman 231.
2. **Diferencial A7S**: el borrador daba por "no verificada" la presencia de `ExlHelper` y
   `MonPowersave` en `[CAMERA_SA]` — **no aparecen** en ninguna de las 231 trazas (son de
   `[CAMCORE]`, S107). Y los **231/231** mensajes de la A6000 existen en la A7S **sin la
   etiqueta**, lo que confirma que la diferencia es solo de instrumentación.
3. **Diferencial A6300 fw2.01**: el borrador afirmaba un "número mayor de trazas por
   categoría"; en realidad el A6300 tiene **0** trazas con la etiqueta `[CAMERA_SA]:` y los
   mismos **231/231** mensajes sin ella.
4. El informe **no** localiza las funciones que emiten cada traza (solo el rango de
   cadenas): la atribución función→traza del esquema PIC (ver S110) se deja como trabajo
   pendiente.

