# G17 — Picture Profile completo en la A6000 (opción C): fase 1 verificada y plan (08-11-2026)

**Decisión del usuario**: opción C de [G16](g16-picture-profile-nucleo.md) §5, que es el Picture Profile completo de la A6300 en
la A6000, «verificando cada paso». Este documento cierra la **fase 1** (la ruta de datos de punta a punta, sin cámara) y fija las fases
siguientes con su criterio de verificación. Scripts de trabajo: `analysis/gui/g17/`.

## 1. Fase 1 — ruta userland → núcleo (VERIFICADO con bytes)

| Eslabón | A6000 fw3.21 | A7S fw3.20 | Resultado |
|---|---|---|---|
| `SequenceSetPictureProfile` envía el comando LIRO **0x4066** con 0x36 B (`movw r0,#0x4066`; tras enviarlo registra en la traza `buf[0x1a]`, la gamma) | `libObj.so 0xa267f0` (sitio `0xa26834`) | `0x9e0984` | igual |
| Conversor `CamMsgConv`: caso 0x4066 del `tbh` (`sub r2,r4,#0x4000`) → GOT `0x103188c` → función | `0x9b3200` (832 instr.) | `0x92c5xx` | igual |
| El conversor rellena los bytes `0x0a`–`0x26` desde las claves `0x9675`–`0x9691` (29 campos) y los bytes 8/9 | sí | sí | **el 0x4066 es el mensaje PP completo**: 31 `PARAMID_PP_*` en el orden de la tabla 371–401 (bytes 8/9 = Color Mode tipo/nivel, `0x0a`–`0x0e` = WB shift, `0x0f`–`0x14` = Color Depth R…Y, `0x15` saturación, `0x16` fase, `0x17` black level, `0x18`/`0x19` black gamma, `0x1a` gamma, `0x1b`–`0x1f` knee, `0x20`–`0x26` detail) (orden por la tabla PARAMID: INFERENCIA fuerte) |
| Gamma (clave `0x9685`) → selector 0–11: `0x1b7`→0, `0x1b8`→1, `0x1b9`→2, `0x1ba`→3, `0x39c`→4, `0x39d`→5, `0x39e`–`0x3a1`→6–9, `0x480`→10, `0x481`→11 | `0x9b36ce` | `0x92c526` | **idéntico**: la `libObj` de la A6000 ya produce los selectores PP 3 y 6–11 |
| Las claves `0x9675`–`0x9691` se rellenan desde los PARAMID PP en la secuencia PP | `0xa22f2a`–`0xa232fa` | varios sitios | presente |
| Núcleo: desempaquetador del 0x4066 → `cfg` (`0x43edf684` / `0x43ea1d84`) | `0x43802a28` | `0x437a9404` | mismo formato (G16) |
| Curva: 4 parámetros u16 `+0x1012…+0x1018` copiados al bloque de registros YC (`+0x814…`) | `0x438549a6` | `0x437db806` | igual; `+0x1012` = 4 en todas las curvas de la A6000 y 7 en las de la A7S → al portar se usa 4 (INFERENCIA) |

**Conclusión de la fase 1**: para la **gamma**, la cadena UI → `libObj` → LIRO 0x4066 → núcleo existe entera en la A6000. Solo
faltan (a) la UI que pone el parámetro, (b) la tabla selector→gamma del núcleo y (c) las curvas.

## 2. Lo que la fase 1 no ha podido cerrar

1. **Espacio para las curvas** (~29 KB; 5 curvas ≈ 20 KB). El hueco de 40 020 B a cero en `0x43faf28c` mide 40 000 B
   más alineación y está pegado a la cadena de versión del front-end «REGULUS» (`0x43fb8ee8`). La A7S no lo tiene. Parece un
   **buffer estático de trabajo**, así que **no es espacio libre verificado**. El CFW conserva el tamaño de `av-cam.bin` (R15).
   Alternativas: (a) cargar las curvas en RAM en ejecución, como el parche de RAM de la app del 3.35 (R56), y apuntar ahí la
   tabla de curvas; (b) demostrar con REA que el buffer no se escribe; (c) ampliar `av-cam.bin` y verificar
   RAMCFG/Loader3 (R14) y que no pisa lo que viene detrás.
2. **Los demás parámetros PP en el núcleo** (black level, black gamma, knee, color depth, detail, color mode, saturación y
   fase). Llegan al núcleo en el 0x4066, pero no se ha demostrado qué código de la A6000 los aplica. Contar lecturas
   por desplazamiento no sirve (ruido). El emparejamiento de funciones (`funcdiff.py`) deja 8 556 funciones de la A7S sin
   pareja, y solo 9 tocan el número de gamma. La forma fiable es una **prueba en cámara**: enviar el 0x4066 con un campo cambiado y mirar la imagen.
3. Qué gamma es cada número (`0x1ba`/`0x480`/`0x481` frente a ITU709, ITU709(800%) y S-Log2). Se resuelve con la
   prueba de la fase 3 o leyendo en la vista de la A6300 cómo se traduce cada opción del menú.

## 3. Plan de la opción C (cada fase con su verificación)

| Fase | Contenido | Verificación sin cámara | Verificación en cámara (autorización expresa) |
|---|---|---|---|
| 1 | Ruta de datos | **hecha** (§1) | — |
| 2 | Espacio para las curvas (§2.1) y parche de datos del núcleo: tabla selector→gamma + 5 curvas de la A7S con `+0x1012 = 4` + punteros | qemu/emulación de la función de selección y bytes comparados; paquete con `nflasha3` TPZL validado (R36) | arranque, y elegir una gamma por el mensaje 0x4066 |
| 3 | Prueba de parámetros: enviar el 0x4066 con cada campo PP cambiado (telnet/`libObj`) | — | imagen por campo → lista de los que la A6000 aplica |
| 4 | Gammas `0x1c`/`0x1d`: ampliar `switch`/rangos y `cfg+0x4a8/0x4aa` | parche Thumb + emulación | ídem fase 2 |
| 5 | UI: 29 nodos de menú, ~30 ProcessIds (ampliar la tabla `0xe8`), 25 clases de vista, ayudante `CmnViewPictureProfileCommon`, vistas PICTUREPROFILE/SLOGDISPASSIST, iconos | carga con `qemu_sysroot.py`, auditoría del paquete `nflasha15` (G11) | navegar por el menú y que cada ajuste llegue al 0x4066 |
| 6 | Perfiles PP1–PP9: NVRAM por perfil y `PARAMID_PP_MODE` (ausente en la `libObj` de la A6000) | código de la vista que guarda por perfil | persistencia tras apagar |
| 7 | Solo con lo aplicable según la fase 3: Gamma Disp. Assist (LUT del visor), metadatos RDD18 (`job_EC_CalcCaptureGamma`) | — | — |

**Bloqueante inmediato**: fase 2, §2.1 (espacio). **Riesgo**: el `nflasha3` modificado ya bloqueó la cámara una vez (3.25, R36).
Se construye con el método corregido del 3.25c/3.38.
