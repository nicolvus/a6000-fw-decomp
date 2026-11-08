# G13 — Barrido de ajustes de menú A6000 fw3.21 frente a A6300 fw2.01 (estático, 08-11-2026)

**Método**: `scripts/gui/settings_sweep.py` → `analysis/gui/settings-sweep.json`. Lee las raíces `cmnViewSettingNodeRoot*` de
`CautionConfig.so`, sus listas de propiedades (`setting_nodes.py`), el texto inglés (`uxc_strings.py`) y qué raíces importa cada
`viewUnified*.so`. Sin cámara. Estados: VERIFICADO = leído en los ficheros; INFERENCIA = razonado; NO_VERIFICADO = pendiente.

## 1. Recuento (VERIFICADO)

| | Raíces | Activas | Dudosas | Ocultas |
|---|---|---|---|---|
| A6000 3.21 | 206 | 187 | 8 | 11 |
| A6300 2.01 | 287 | 249 | 27 | 11 |

- **Oculta**: ninguna `viewUnified*.so` la importa (la UI no puede llegar a ella). **Dudosa**: importada pero la raíz no tiene `0xb = 2`
  (incluye SilentShutter, que no se ve, y también FnFunction/CustomFunction, que sí se ven). **Activa**: el resto.
- Comprobaciones de la heurística (asserts del script): EFCS = activa; SilentShutter = dudosa; `AfIlluminator` = oculta mientras
  `StillAFIlluminator` (la que se ve) = activa. **Límite**: «importada» no prueba que una página visible para este modelo la contenga
  (las `viewUnified` son comunes a varios modelos); la verdad final es la cámara.
- Todas las raíces de la A6000 existen en la A6300 (0 exclusivas de la A6000); la A6300 tiene **81 raíces más**.
- **ProcessId (`0xe`) igual solo en 10 de 206 raíces comunes**: la numeración es propia de cada modelo. Un nodo de la A6300 **no se
  copia tal cual**: hay que darle el ProcessId de la A6000 si el ajuste ya existe, o un manejador nuevo si no.
- 30 raíces comunes tienen más opciones en la A6300 (p. ej. DriveMode 32→176, ISO 48→121, MovieRecordingSetting 22→76).

## 2. Ajustes no activos en la A6000 (19)

| Raíz | Texto | Estado | Activa en A6300 | Lectura |
|---|---|---|---|---|
| AfTrackingSpeed | AF Track Duration | oculta | sí | candidata: nodo y opciones ya en la A6000 |
| CustomAfAreaNumber | AF Area Points | oculta | sí | candidata (sin opciones en la A6000) |
| LocalAreaLimitation | AF Area Pts in Local | oculta | sí | candidata |
| WheelLock | Wheel Lock | oculta | sí | candidata |
| SilentShutter | (texto de SteadyShot) | dudosa | sí | el nodo del G10; en la A6300 es «Shutter Type» lo visible |
| AfIlluminator, CustomAfAreaDisplay, DualRecImageSize, ISOAutoMax, ISOAutoMin, MoviePushAutoFocus, CtrlDialWheelSetup | — | oculta | no | restos de otros modelos o duplicados de nodos activos (`CtrlDialWheelSetup` ≈ `ZoomFuncOnLensRing`) |
| CustomFunction, FnFunction, DispButton, CustomLensComp, SuperiorAutoSettings, SettingSendTo* | — | dudosa | no | contenedores visibles (falsos positivos de la heurística) |

## 3. Exclusivas de la A6300 y complejidad estimada para la A6000 (INFERENCIA)

Escala: **Baja** = solo UI (nodo/página/texto) y el comportamiento ya existe en la A6000. **Media** = nodo nuevo + el negocio de la
A6000 probablemente ya tiene la función (variante de algo existente). **Alta** = hace falta código nuevo en el modelo/`av-cam`
(AE, AF, códecs, metadatos). **Hardware** = depende de sensor/LSI/estabilizador/visor que la A6000 no tiene; no viable.

| Complejidad | Ajustes (raíz A6300 → texto) |
|---|---|
| **Baja** | Ocultas ya presentes: AfTrackingSpeed, WheelLock, LocalAreaLimitation, CustomAfAreaNumber (§2). DialLockTA (Dial Lock), SettingSetupNtsctoPal (la A6000 ya tiene `SettingSetupNtscPalSEL`), SelfTimerOnBracket, StillPanoramaShooting2DDirection, CustomFunctionShooting/Playback (reparto de Custom Key que ya existe), MarkerDisplay |
| **Media** | CustomStillShutterType (Shutter Type: Auto/Mecánico/Electrónico; en curso como «Silent Shooting», G10/G11), CustomReleaseWOCard (análogo a Release w/o Lens), AfAreaAutoClear, WideFocusAreaDisplay, FocusMagnifAF, ExtZebra (más niveles de cebra), MarkerSettings, FuncFinderClose, ZoomRingRotate/ZoomAssistRange/ZoomSettingSmart/ZoomSpeedNF (zoom motorizado ya soportado), VideoLightSet, BracketSetting, AutoPowerOffTemp, CustomLensRingSetup, opciones nuevas de DriveMode (horquillado de 9 imágenes, autodisparador continuo) |
| **Alta** | ISO_Auto_Min_Shutter_Speed (+_Menu) (algoritmo de AE), StillPrioritySetupAFC/AFS (prioridad AF/disparo), AFSystem/PhaseAF_FocusSet (adaptadores LA-EA3), CopyrightInformation y FileNameSetting (EXIF/nombres), RawFileType (RAW sin comprimir), PictureProfile y sus 13 subnodos (gamma/S-Log/Knee…), SLogDispAssist, TCUBSettings (timecode), HDMISettings, opciones de AF ampliadas (Lock-on AF por área, Expand Flexible Spot), ISO ampliado/Multi Frame NR |
| **Hardware** | 4kPhotoCapture, SetupHDMI4kOutput*, MovieFileFormat XAVC S 4K, MovieRecordingSetting_Super35mm, SetupAPSCSuper35, HFR*/MovieHfr*/FrameRateZako, SQ*/MovieSlowAndQuickExpoMode (100/120p), CustomFinderFrameRate (visor a 120 fps), SteadyShot* (estabilización en cuerpo), LPFilter, DualVideoRecording/AutoDualRec/TwoStream* (doble flujo) |
| Fuera de alcance | GpsTest (depuración), SetupVersionForFixedLens, Aperture/ShutterSpeed/AfASetup/LockOnAfwCenter (raíces sin lista, internas) |

Notas: la diferencia de etiquetas de opciones incluye renombrados (p. ej. «Continuous Shooting: Hi+» frente a «Hi»), no solo
opciones nuevas. Lo «Alto» y «Hardware» lo estimo por la función, no por código leído: ningún manejador de ProcessId de la A6000
se ha comprobado aún (G7).

## 4. Orden recomendado
1. Terminar la receta del nodo con el 3.54 (selector Silent Shooting): sin eso nada de §3 es aplicable.
2. Las 4 ocultas «Baja» de §2 (ya existen en la A6000): solo añadir la entrada a una página con `add_menu_entry.py` y ver si el
   negocio responde a su ProcessId. Es la prueba más barata de que la A6000 conserva el código de un ajuste no mostrado.
3. Después, las «Media» que reutilizan una función existente.
