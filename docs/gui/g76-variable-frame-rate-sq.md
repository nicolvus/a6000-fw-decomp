# G76 — Variable Frame Rate (GH5) = S&Q / «O/U Crank» de Sony: viable, sin menú

Fecha 16-11-2026 (G75 Tarea 21). Estático sobre av-cam 3.21, `libObj.so`, `libmpr.so` y `CautionConfig.so` 3.21. No hay parche ni CFW, y la prueba en el arnés queda bloqueada por la grabación (E2E-14). Reproducible con `tests/test_g76_sq_vfr.py`.

## 1. Qué es
El VFR de Panasonic graba a una frecuencia de captura distinta de la de reproducción: cámara lenta (captura alta) o rápida (captura baja). En Sony se llama **S&Q Motion** y en el firmware **O/U Crank** (*over/undercrank*). La A6000 tiene todo el camino por debajo de la UI.

## 2. Piezas de fábrica (VERIFICADO por bytes)
| Capa | Pieza | Evidencia |
|---|---|---|
| av-cam | Tabla de 57 combinaciones `{u32 fR, u8 sR, u8 válido}` en `0x43b93bf4`. La copia y consulta `0x435d709c`, que registra «[O/U Crank] Table[%d] fR sR» o «OuCrank Config Err». NTSC: fR 4/2/6 con captura 60, 30, 20, 16, 12, 10, 8, 6, 4, 2 y 1 fps. PAL: fR 5/3 con 50, 24, 16, 12, 10, 8, 6, 4, 2 y 1. fR 7–10 solo a 1 fps | `test_tabla_o_u_crank_de_av_cam` |
| av-cam | Codificador `McAvcEncVideoOuCrank*` (estados, índice, datos de usuario) y audio `McAvcEncAudioSeqCtrlStateOuCrank*` | cadenas RTTI |
| libObj | `CamMsgConv::SetOUCrankModeForLiro` (`0x99f18c`): MSGID `0x75e4`/`0x75e6`, `PARAMID_O_U_CRANK_MODE` `0x9724` y `PARAMID_O_U_CRANK_FRAME_RATE` `0x971b`. Los valores 0x207–0x20d y 0x3e2 pasan a los códigos 0–7 en el byte 9 de la orden LIRO. También están `SequenceAppSetOUcrankCmd` (`0x157268`…, parámetro `0x1013`), `InhFeatureCheck` de O/U crank y el arranque «Super S&Q Movie EncStart» (`0x49da8e`) | `test_libobj_convierte_s_q_para_av_cam` |
| libmpr | `SetRecOUCrankInfo`, `bOUCrankRec`, `GetOUCrankRecLimitTime` (NTSC/PAL): el fichero de vídeo sabe registrar la toma S&Q | cadenas |
| UI | **No hay** nodos de menú S&Q en `CautionConfig.so` | `test_sin_menu_s_q_en_la_a6000` |

## 3. Veredicto
- **Viable como S&Q de 1 a 60 fps** (50 en PAL), grabado a 24/25/30/50/60p. Eso da cámara rápida hasta 30× y lenta solo hasta 2,5× (60 → 24p). Para cámara lenta a 120 fps haría falta combinarlo con el modo de sensor 0x12 de G70; ninguna fila de la tabla pasa de 60, así que sería otra tabla: NO_VERIFICADO.
- La pieza que falta es la petición: un ajuste propio en la carpeta «CFW» (frecuencia de captura) y una cueva en `libObj` que envíe `0x75e4` con `0x9724`/`0x971b`, como D Range Priority envía `0x755a`/`0x759e` (g68).
- NO_VERIFICADO: la equivalencia exacta entre los códigos fR/sR de av-cam y los valores `0x20x` de `libObj`; si `InhFeatureCheck` inhibe O/U crank en el tipo de modelo 29; y si hace falta XAVC S (y por tanto SDXC, E2E-14).

## 4. Siguiente paso (VFR-F1…F3)
1. VFR-F1: en el arnés, enviar `0x75e4` con sus PARAMID desde `libObj` (ampliar el comando `X` del shim para que acepte parámetros) y ver en `avcam.jsonl` la orden LIRO que sale y si av-cam la acepta (`0x435d709c` sin «Config Err»).
2. VFR-F2: ajuste «S&Q» en la carpeta «CFW» y cueva en `libObj` (patrón g56/g68), probados en Unicorn y en el arnés.
3. VFR-F3: grabar en el arnés y comprobar el fichero (depende de E2E-14).

## 5. Prueba en el arnés y combinación con HD 120 (G75 T22, 16-11-2026)
- **Nombres** (tabla de `libObj` `0xfdb5ec`): `MSGID_SET_O_U_CRANK_MODE_CMD` `0x75e4` (CMP `0x75e5`), `PARAMID_O_U_CRANK_MODE` `0x971a`, `PARAMID_O_U_CRANK_FRAME_RATE` `0x971b`, `VALUEID_O_U_CRANK_OFF/ON` `0x205/0x206`, `…FR_60_50` `0x207`, `FR_30_25` `0x208`, `FR_15_12` `0x209`, `FR_8_6` `0x20a`, `FR_4_3` `0x20b`, `FR_2` `0x20c`, `FR_1` `0x20d` y **`FR_120_100` `0x3e2`**. Corrige §2: `0x9724` es otro parámetro, el de la orden `0x4087`.
- **En vivo (MEDIDO, perfil `e2e42`):** el comando nuevo del shim `Z 75e4 971a=206,971b=…` arma el mensaje con las funciones de `libObj` de las cuevas. Desde un hilo propio del shim, `ObjCamera` no lo despachaba; enviado dentro de la siguiente orden de la UI, en su hilo, pasa el control de soporte (`0xa38c84` con `0x75e4`) y `ExcMgr`. Llega a av-cam como **`05 00 8f 40 … 01 03`** (ON, 8/6 fps) y **`… 01 07`** (ON, **120/100 fps**). av-cam (`0x43802cfc`) guarda modo y código en `0x43edf684+0x208/+0x209` sin respuesta. Lo fija el test de la VM `test_av_cam_guarda_el_s_q_de_la_orden_0x408f`.
- **Enlace con HD 120 (VERIFICADO por bytes; el significado del campo es INFERENCIA):** `SeqSetOUCrankMode` (`0xa1aa90`), la secuencia de `ObjCamera` que se ejecuta con la cámara en marcha, manda `0x408f` y una orden EE `0x4000` de 0x17 B. Con `FR_120_100` pone su byte `0xd` = **4**, que es el valor de la clase de formato de «120p» con la que el selector de av-cam elige el modo de sensor 0x12 a 120 Hz (G70). Es decir, el firmware ya prevé S&Q a 120/100 fps sobre el modo HFR (`test_s_q_a_120_pide_el_formato_hfr`). En el arnés la inyección siguió el camino del conversor (`0x408f` solo), no esta secuencia.
- **Lo que falta para grabar S&Q a 120:** la tabla O/U Crank de av-cam (§2) no tiene ninguna fila con captura 120 ni 100. Con el código 7 la búsqueda `0x435d709c` daría «OuCrank Config Err» (INFERENCIA: depende de cómo av-cam traduce el código 7 a sR al iniciar la grabación, sin localizar). Habría que ampliar la tabla (cueva con más filas: fR 24/30/60p con sR 120 y fR 25/50p con sR 100) y comprobarlo grabando, lo que depende de E2E-14.
