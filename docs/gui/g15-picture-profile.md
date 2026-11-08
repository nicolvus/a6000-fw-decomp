# G15 — Picture Profile de punta a punta: A6300 → A6000 (estático, 08-11-2026)

**Alcance**: todo el Picture Profile de la A6300 fw2.01 (menú, opciones, clases de la UI, vistas, persistencia, capa de
cámara de `libObj.so` y núcleo `av-cam.bin`), comparado con la A6000 fw3.21 y con la **A7S fw3.20** (misma generación
Bionz X que la A6000 y con Picture Profile/S-Log2). Amplía [G14](g14-auditoria-cadena-a6300.md) y **corrige
[S77](../../analysis/s77_pp/picture_profile_creative_style.md) §4** («no hay ninguna traza de Picture Profile en el firmware»:
sí la hay, en `libObj.so`).

> **Superado en parte por [G16](g16-picture-profile-nucleo.md) (08-11-2026)**: el núcleo de la A6000 sí aplica curvas PP por número de gamma; le faltan 7 curvas de vídeo (datos) y la tabla del selector, y código solo para 2 gammas. `job_EC_CalcCaptureGamma` es metadatos y `EC_Gamma.cpp` una aserción.

**Reproducción**: `scripts/gui/picture_profile_audit.py analysis/gui/picture-profile-audit.json` (con autocomprobaciones);
clases y medidas de la A6300 en `analysis/gui/g14/` (`f6300.json`, `measure.json`, `cls_params.json`).

## 1. Menú de la A6300 (29 ajustes, ProcessIds `0xff`–`0x12a` y `0x151`)

PP1…PP9 + Off. Cada PP guarda su propio juego de valores; las opciones marcadas «S-Log2» en el árbol son las variantes
bloqueadas cuando la gamma es S-Log.

| ProcessId | Ajuste | Opciones (valor interno) | Clase A6300 |
|---|---|---|---|
| `0xff` | Picture Profile | PP1–PP9 = 0–8, Off = 9 | `CustomPictureProfile` |
| `0x101` | Gamma | Movie 0, Still 1, Cine1–4 2–5, ITU709 6, ITU709(800%) 7, S-Log2 8, S-Log3 9 | `…Gamma` |
| `0x102` / `0x103` | Black Gamma: Range / Level | Wide 0, Middle 1, Narrow 2 / −7…+7 | `…BlackGammaRange` / `…Level` |
| `0x104` | Black Level | −15…+15 | `…BlackLevel` |
| `0x105` | Knee: Mode | Auto 0, Manual 1 | `…KneeMode` |
| `0x106` / `0x107` | Knee Auto: Max Point / Sensitivity | 5 pasos / High 0, Mid 1, Low 2 | `…KneeAutoMaxPoint` / `…Sensitivity` |
| `0x108` / `0x109` | Knee Manual: Point / Slope | 13 pasos / −5…+5 | `…KneeManualPoint` / `…Slope` |
| `0x113` / `0x114` | Color Mode / nivel | Movie 1, Still 2, Cinema 3, Pro 4, ITU709 Matrix 5, B&W 6, S-Gamut 7, S-Gamut3 8, S-Gamut3.Cine 9 / nivel | `…ColorModeType` / `…Level` |
| `0x10a` | Saturation | −32…+32 | `…ColorLevel` |
| `0x10b` | Color Phase | −7…+7 | `…ColorPhase` |
| `0x115`–`0x11a` | Color Depth R, G, B, C, M, Y | −7…+7 cada uno | `…ColorDepth` (una clase) |
| `0x10c` / `0x10d` | Detail: Level / Mode | −7…+7 / Auto 0, Manual 1 | `…DetailLevel` / `…Mode` |
| `0x10e`–`0x112` | Detail manual: V/H Balance, B/W Balance, Limit, Crispening, Hi-Light Detail | −2…+2, Type1–5, 0–7, 0–7, 0–4 | 5 clases `…Detail*` |
| `0x129` / `0x12a` | Copy (a PP1–PP9) / Reset | — | `…Copy` / `Normal` |
| `0x151` | Gamma Disp. Assist | Off, Auto, S-Log2→709(800%), S-Log3→709(800%) | `CustomSLogDispAssist` |
| `0x11f`–`0x122` | WB Shift (LB, CC, R, B, tipo de filtro) | nodo con `0xb = 0`: **oculto también en la A6300** | `…WbShift` |

## 2. La cadena por capas y qué tiene la A6000

| Capa | A6300 | A7S | **A6000** |
|---|---|---|---|
| Nodos de menú (`CautionConfig.so`) | 29 raíces + ~580 listas | — | **0** |
| ProcessIds y descriptores | 30 (`0xff`–`0x12a`, `0x151`) | — | **ninguno; tabla llena (`0xe8`)** |
| Clases de elemento (UI) | 25 clases, **≈9,8 KB** Thumb (248–756 B c/u) | — | **0** |
| Ayudante común `CmnViewPictureProfileCommon` (`viewUnified2.so 0x1e5cdd`: constructor 0x250 B + `getBackupIdForMR/ForDefault/CustomForModel`) | sí | — | **no** |
| Vista `view/PICTUREPROFILE` (`ViewPictureProfileToInstance`, `viewUnified4.so 0x11f3fd`) + `viewPictureProfile.uxc` (1 364 B) + icono `ACT_PictureProfile` | sí | — | **no** |
| Vista `view/SLOGDISPASSIST` (`viewUnified3.so`) | sí | — | **no** |
| `libObj.so` CamUser: `SequenceSetPictureProfile`, `MSGID_SET_PICTURE_PROFILE_CMD/CMP`, `MSGID_NOTIFY_PICTURE_PROFILE_EVT`, `ActionExePictureprofileCopy/Reset`, `INFO_DATA_PICTUREPROFILE_BKUP` | sí | sí | **sí** (VERIFICADO por cadenas/RTTI) |
| `PARAMID_PP_*` (tabla de nombres de `libObj.so`) | 44 | 44 | **31, mismos índices 371–401** (gamma, black gamma/level, knee, color mode/level, saturación, fase, 6 color depth, 7 detail, 5 WB shift) |
| Falta en `libObj.so` A6000 | — | — | `PARAMID_PP_MODE` (selector PP1–PP9), 12 `COLOR_CORRECT_*` (no están en el menú de la A6300), valores `PP_GAMMA_SLOG3`, `PP_COLOR_SGAMUT/SGAMUT3/SGAMUT3_CINE`, `PP_COLOR_BW` |
| `av-cam.bin`: `Camera::EC::job_EC_CalcCaptureGamma(uchar, PP_COLOR_MODE, PP_MODE)`, `PIN_YC_CAPTURE_GAMMA`, `Gamma/EC_Gamma.cpp`, «Unsupported Capture Gamma» | sí | sí | **no** (0 de cada uno) |
| `av-cam.bin`: validación `LiroSeq` `CheckSetPictureProfile` / `PP_*` | sí | no | no |
| `av-cam.bin`: escritura del registro de gamma (`GammaReg=`) | sí | sí | **sí** |

Lectura: el menú, la UI y la persistencia de la A6300 faltan enteros en la A6000. La **capa intermedia** (`libObj.so`) sí
trae Picture Profile, porque es código común de la familia. Su lista de parámetros es la de la A7S salvo el selector de
perfil (`PARAMID_PP_MODE`), S-Log3 y S-Gamut. Lo que decide es el **núcleo**. A la A6000 le falta el cálculo de gamma de
captura y los tipos `Camera::PP_*`, que la A7S, de la misma generación, sí tiene. El hardware de gamma existe (las tres
cámaras escriben `GammaReg`, que usan Creative Style y DRO).

Regla de [S174](../capture/s174-forliro-api.md): la presencia de cadenas en `libObj.so` no prueba que funcione. INFERENCIA
fuerte: si la UI de la A6000 enviara hoy `MSGID_SET_PICTURE_PROFILE_CMD`, el núcleo no calcularía ninguna curva PP.
NO_VERIFICADO: falta el manejador del mensaje en `av-cam.bin`.

## 3. Portabilidad por función

Escala de G14 (**Media** = datos + ampliar la tabla de ProcessIds; **Alta** = portar código de la UI; **Muy alta** = además,
código en `av-cam.bin`).

| Función | Qué hace | Qué falta en la A6000 | Complejidad |
|---|---|---|---|
| Selector PP1–PP9/Off | elige el juego de valores | menú, clase, vista PICTUREPROFILE, ayudante, NVRAM por perfil y **`PARAMID_PP_MODE`** en `libObj.so` | Alta (UI) + Muy alta (núcleo) |
| Gamma Movie/Still/Cine1–4/ITU709/ITU709(800%) | curva de tono | UI + `job_EC_CalcCaptureGamma` en el núcleo | Muy alta |
| Gamma S-Log2 | curva logarítmica (ISO mínimo 800 en la A6300) | lo anterior + mínimos ISO de S-Log (`PP_MIN_ISO_*`, solo en la A6300) | Muy alta |
| Gamma S-Log3 | ídem | además el valor `PP_GAMMA_SLOG3` en `libObj.so` | Muy alta |
| Black Gamma, Black Level, Knee (Auto/Manual) | tono de sombras y luces | UI; núcleo NO_VERIFICADO (sin marcador propio) | Alta (UI) + ¿núcleo? |
| Color Mode (Movie…ITU709 Matrix) | matriz de color | UI; tipo `Camera::PP_COLOR_MODE` ausente | Muy alta |
| S-Gamut / S-Gamut3 / S-Gamut3.Cine, B&W | espacios de color | además los valores en `libObj.so` | Muy alta |
| Saturation, Color Phase, Color Depth R/G/B/C/M/Y | color | UI; núcleo NO_VERIFICADO | Alta (UI) + ¿núcleo? |
| Detail (Level, Mode, V/H, B/W, Limit, Crispening, Hi-Light) | nitidez de vídeo | UI; núcleo NO_VERIFICADO | Alta (UI) + ¿núcleo? |
| Copy / Reset | copiar o restablecer un perfil | UI; acciones ya en `libObj.so` | Media, si hay perfiles |
| Gamma Disp. Assist | ver S-Log como 709 en pantalla | vista SLOGDISPASSIST + LUT del visor | Muy alta, depende de S-Log |
| WB Shift del PP | — | oculto también en la A6300 | No aplica |

**Conclusión**: portar el Picture Profile completo es **Muy alta**. La parte de UI se conoce bien (≈9,8 KB de clases, un
ayudante, dos vistas, unos 30 ProcessIds nuevos y su NVRAM). Lo que bloquea es el núcleo `av-cam.bin`, que no calcula curvas PP;
habría que portar el código de gamma de captura desde la A7S (misma generación) o parchear la tabla de gamma que escribe
`GammaReg`. No hay atajo de solo datos ni de solo userland.

Alternativas más baratas (INFERENCIA, por verificar):
1. **«PP ligero» sobre Creative Style**: la A6000 ya aplica contraste, saturación y nitidez (±3) por estilo. Un menú con
   otros nombres o rangos sería solo UI, pero no da curvas Cine/S-Log.
2. **Curva plana propia**: sustituir una de las tablas de gamma que el núcleo ya escribe (`GammaReg`) por una curva
   tipo Cine/log. Es un parche de `av-cam.bin`, necesita prueba en cámara y no daría metadatos ni la ayuda de visualización.

## 4. Límites

- La capa del núcleo se juzga por marcadores (cadenas, tipos, `job_`/`PIN_`), no por el manejador del mensaje
  (regla de S174). No se ha abierto `av-cam.bin` con REA (unos 8 min en frío).
- No se sabe si la A6000 tiene ids NVRAM para PP: el nombre `INFO_DATA_PICTUREPROFILE_BKUP` existe, los ids no se han buscado.
- Black gamma, knee, black level, color y detail no tienen un marcador propio en el núcleo de ninguna de las tres cámaras.
  Que falten en la A6000 es NO_VERIFICADO.
- Las opciones del JSON salen por prefijo de nombre de nodo y traen ruido (cabeceras «S-Log2», `${v1:02}`). La tabla del §1 está
  revisada a mano sobre el volcado de nodos.
