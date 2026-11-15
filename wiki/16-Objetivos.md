# 16. Objetivos

Funciones que se quieren en la A6000, heredadas de otros modelos Sony y de otras marcas, con su modelo de origen. Se marca ✅ cuando está hecha y verificada en la cámara. Las funciones parecidas se agrupan con «/».

≈ = modelo de Sony según mi memoria, sin verificar (la búsqueda web solo confirmó Silent Shooting → α7S, FTP → α9 y AF Track Sens → α99 II); puede no ser el primero.

## En investigación y ejecución

- ⬜ Silent Shooting ([estado](14-Estado-actual)) — _Origen: Sony α7S_
- ⬜ Picture Profiles PP1–PP10 — _Origen: ≈Sony α7R III_

## Pendientes

### Foto

- 🔧 Obturación máxima 1/8000 — _Origen: ≈Sony α7_. Reabierto (15-11-2026): el «piso» de 0,58 ms del Silent es el tope `r5 ≤ 4218` de nuestra cueva, no del firmware ni demostrado del sensor (T046 midió 0,3 ms); parche probado en el arnés, sin CFW: tope 4251 ⇒ 1/8000 → `r5` 4245 (≈ 120 µs en la ley R87), pendiente medir en cámara que el sensor acepte `r5` > 4218 (G38-C). Dial: la UI y `libObj` no limitan (G40 §6); el tope 1/4000 viene de `av-cam` y no se ha localizado (G38-E/G; [G40 §7](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g40-g38d-tope-de-velocidad-en-la-ui.md): cadena hasta el objeto AE, MIN probable en `+0x2a0/+0x2e4`; §8: el objeto AE es un global alimentado por mensajes `0x4089/0x4065/0x4053`, así que el MIN no es constante de `av-cam`: falta localizar el emisor). Mecánico/EFCS: Darwin no limita T (sin tabla); rendija ≈ 0,57 mm y ±33 µs exigidos frente a ±190 µs medidos en esta unidad; lista del dial: la UI no tiene tope (solo pide pasos ±1 al modelo), el MIN 1/4000 sale de `av-cam`/`ModelCamera` y sigue sin localizar (G38-D parcial, G38-E/F; [G40](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g40-g38d-tope-de-velocidad-en-la-ui.md)) ([G38](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g38-obturacion-1-8000.md)).
- 🔧 Calidad JPEG Extra Fine — _Origen: Sony α6300_. El menú Calidad de la A6000 (fw 3.21) NO la muestra: `_getSubNode` elige la lista `Type01` (4 nodos) en vez de `Default` (5, con Extra fine). Parche de 8 B en `CautionConfig.so` ([G39](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g39-extra-fine-menu.md)): probado en el arnés (aparece «Extrafina»), sin CFW construido ni instalado; falta confirmar en cámara.
- 🔧 ISO expandido hasta 409600 — _Origen: Sony α7S_. Parcial. Hasta 51200: parches del firmware probados en Unicorn, sin CFW; verificación en cámara pendiente ([G48](../docs/gui/g48-iso-51200-cadena-firmware.md); 102400 sin hacer). (G47: `wrapperIso` no se carga en el arnés; el tope `0x26` también está en `cmn_view_processDataMgr` `getValue`; sin captura 51200, ver [G47](../docs/gui/g47-iso-wrapperiso-no-se-carga.md); G46: `ISOSensitivity::_getSubNode` no construye el menú ISO del arnés, el parche de lista G43 no puede actuar; ver [G46](../docs/gui/g46-iso-getsubnode-no-construye-menu.md); G44/G45: inyección de ISO en el arnés no mueve el MAX y el parche de lista no cambia el menú; 51200 aún no visible, H1/H2 sin resolver, ver g44 §4-5; G41/G42, ISO-A; G42: parche del MAX en `libObj` hecho y probado en Unicorn, sin CFW; faltan `wrapperIso` (enum/setIso) y nodos de menú 64000/80000/102400 en `CautionConfig`, la lista estática llega a 51200): código ISO = índice de la tabla de `av-cam` (hasta `0x2c` = 204800, A7S hasta 819200); `wrapperIso` solo admite hasta `0x26` (51200); ids `0x96ff`/`0x98a1`; `libObj` ya porta códigos hasta `0x29` (102400); emisor en `av-cam` sin cerrar (G41 §8: av-cam tipo 4 id `0x1002` → `libObj 0x9aa134` → MSGID `0x8587`; trazas sin mensaje de ISO), `getIso` sin hueco; sin parche ni captura. [G41](../docs/gui/g41-iso-expandido-409600.md) G43: parche de lista (`iso_list_patch.py`, Type12→Default, hasta 51200) hecho, sin CFW; en el arnés 32000+ siguen ocultos por el MAX que no se emite ([G43](../docs/gui/g43-iso-lista-51200.md)).
- ⬜ Pre Capture photo / Pro Capture / Pre-Burst 4K/6K — _Origen: Olympus E-M1 II; Panasonic GH5, G9_. Pro Capture a resolución completa: viable por fases, sin implementar (falta ubicar el predicado S1/S2 y la cola de ráfaga; anillo de N×24 MB). La parte 4K/6K está descartada (g50). Ver [g51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g51-pro-capture.md).
- ⬜ Multiple Exposure — _Origen: Canon EOS 7D Mark II; Nikon D850; Olympus E-M1 II_. Parcial (estático): el motor Apollo/HME de MFNR/Twilight es solo estimación de movimiento, sin operación suma/máx/mín ni alineación desactivable; hace falta acumulador propio. Pendiente `MULTIEXP-ACC` ([g53](../docs/gui/g53-multiple-exposure-motor-fusion.md)).
- ⬜ Live Composite — _Origen: Olympus E-M1 II_. Parcial (estático): = `MULTIEXP-ACC` en modo máximo; la repetición automática y la revisión existen de fábrica (modelo `STILL_INTERVAL_REC`, parámetros del autodisparador continuo, `Stage_RchRcv_Resize_AutoReview`) pero falta localizar sus tablas y búferes. Pendientes `LIVECOMP-F1..F3` ([g54](../docs/gui/g54-live-composite-live-bulb.md)).
- ⬜ Live Bulb / Live Time — _Origen: Olympus E-M1 II_. Descartado en su forma original (con obturador mecánico la lectura es al final; sin lectura no destructiva documentada en el IMX210); derivado a Live Composite en modo suma ([g54](../docs/gui/g54-live-composite-live-bulb.md)).
- ⬜ Bulb Timer — _Origen: Canon EOS 7D Mark II_. Parcial: BULB ya cronometra por tramos y `T = 0` es «sin límite»; un gancho de 4 bytes (`0x438c74f6`) sustituye T por el ajuste de menú «Bulb Timer» (id de Backup `0x1070210`; 0 = fábrica), probado en Unicorn (5 s ⇒ 152 tramos); la entrada de menú (ahora en la carpeta «CFW», 7 opciones, junto a un ajuste de prueba; g56 §7) (Off…15 min) se ve en el arnés y su escritura al Backup funciona (CFWAJ-F1, CFWAJ-N); S2 sigue iniciando y no se sabe si el BULB queda bloqueado con un pulso (BULBTIMER-F2) ([g55](../docs/gui/g55-bulb-timer.md), [g56](../docs/gui/g56-ajustes-propios-cfw.md)).
- ⬜ Focus Shift Shooting / Focus Stacking — _Origen: Nikon D850; Panasonic GH5, G9; Olympus E-M1 II, E-M1X_. Parcial: localizado el comando de paso de enfoque (lente `0x1D`, s16 con signo; primitiva `0x43adb5e6`, la del bracketing de AF de fábrica `lc_BracketAF`); ajustes «Focus Bracket» (Off/3…30) y «Focus Br. paso» en la carpeta «CFW» (arnés: id `0x1070212`=02, `0x1070213`=02); cueva probada en Unicorn (N = 5 ⇒ 4 movimientos). Falta el gancho de fin de captura y medir sentido/escala del paso. `SequenceBracketAF` de fábrica solo mueve el enfoque un paso (no dispara): no sustituye a la cueva (g57 §6; paso API = s8, rango ±127). CFW sin construir. Ver [g57](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g57-focus-bracket.md).
- ✔ Smile Shutter — _Origen: Sony α5100_. Ya existe de fábrica en la A6000: «Sonrisa/Detec. cara» ofrece Smile Shutter (tipo de modelo 29 → lista `Default`); detector en av-cam, secuencia en `libObj`; visto en el arnés, sin parche ([g58](../docs/gui/g58-smile-shutter.md)). Pendiente solo el disparo en cámara (SMILE-CAM).
- ⬜ Intervalómetro interno — _Origen: ≈Sony α9_. Parcial (estático): `ModelStillIntervalRec` es solo almacén de ajustes/estado de la API de apps, no dispara; falta el gancho de fin de captura (`INTERVAL-F1/F2`, [g59](../docs/gui/g59-intervalometro-interno.md)).
- ⬜ Interval AE Tracking Sensitivity / Exposure Smoothing — _Origen: ≈Sony α7R III; Nikon D850_
- ⬜ Anti-Flicker Shooting / Flicker Reduction / Flicker Scan — _Origen: Canon EOS 7D Mark II; Nikon D500, D850; Fujifilm X-T3; Olympus E-M1 II, E-M1X_
- ⬜ Keystone Compensation — _Origen: Olympus E-M1 II, E-M1X_
- ⬜ Live ND — _Origen: Olympus E-M1X_
- ⬜ Rating de fotografías en cámara — _Origen: ≈Sony α9_

### Imagen y color

- ⬜ S-Log2 — _Origen: ≈Sony α7S_
- ⬜ S-Log3 — _Origen: ≈Sony α7S II_
- ⬜ HLG 1-3 — _Origen: ≈Sony α7R III_
- ⬜ D Range Priority — _Origen: Fujifilm X-T3_
- ⬜ Color Chrome Effect — _Origen: Fujifilm X-T3_
- ⬜ Importación de LUTs — _Origen: Sony ZV-E1_
- ⬜ Film simulation directo — _Origen: Fujifilm X-T5_

### Video

- ⬜ Full HD / HD 120 fps — _Origen: ≈Sony α6300_
- ⬜ Variable Frame Rate — _Origen: Panasonic GH5_
- ⬜ 4K interno — _Origen: ≈Sony α7R II_
- ⬜ Dual Video Recording — _Origen: ≈Sony α7R III_
- ⬜ Salida HDMI 4K — _Origen: Sony α7S_
- ⬜ Timecode / User Bit — _Origen: ≈Sony α7S II_
- ⬜ Loop Recording — _Origen: Panasonic GH5_
- ⬜ Movie Silent Control / Silent Multi Controller — _Origen: Fujifilm X-T3; Sony α99 II_
- ⬜ Anamorphic Desqueeze — _Origen: Panasonic GH5_
- ⬜ Synchro Scan — _Origen: Panasonic GH5_
- ⬜ Auto Object Framing — _Origen: ≈Sony ZV-E1_
- ⬜ Voice Memo — _Origen: ≈Sony α9_

### Monitorización

- ⬜ Zebra 0–109 % — _Origen: ≈Sony α6400_
- ⬜ Waveform Monitor — _Origen: Panasonic GH5_
- ⬜ Vectorscope — _Origen: Panasonic GH5_
- ⬜ Gamma Display Assist — _Origen: ≈Sony α7R III_
- ⬜ Sports Finder Mode — _Origen: Fujifilm X-T3_

### Enfoque

- ⬜ Eye AF en tiempo real — _Origen: ≈Sony α9_
- ⬜ Seguimiento AF en tiempo real (3D Tracking / EOS iTR AF) — _Origen: ≈Sony α6400; Nikon D500, D850; Canon EOS 7D Mark II_
- ⬜ Ajustes de sensibilidad del seguimiento AF (AF-C Custom Settings / AF-C Cases) — _Origen: Sony α99 II; Fujifilm X-T3; Panasonic GH5; Olympus E-M1 II; Canon EOS 7D Mark II_
- ⬜ AF Acceleration/Deceleration Tracking — _Origen: Canon EOS 7D Mark II_
- ⬜ AF Range Control — _Origen: ≈Sony α99 II_
- ⬜ AF Micro Adjustment — _Origen: ≈Sony α99_
- ⬜ Pre-AF — _Origen: Fujifilm X-T3_
- ⬜ AF Point Auto Switching / Zone Area Switching — _Origen: Canon EOS 7D Mark II; Fujifilm X-T3_
- ⬜ Starry Sky AF — _Origen: Olympus E-M1 II_
- ⬜ Intelligent Subject Detection AF — _Origen: Olympus E-M1X_

### Sistema y conectividad

- ⬜ Carga USB con la cámara encendida — _Origen: ≈Sony α7 II_
- ⬜ FTP Background Transfer — _Origen: Sony α9_

## Descartadas

- ❌ Post Focus — _Origen: Panasonic GH5, G9_. Depende de 4K/6K Photo (descartado en g50: sin modo de lectura ≥3840 ni codificador suficiente) y la A6000 no tiene pantalla táctil (sin panel en el manual de servicio; las cadenas «Touch» del firmware son de detección de caras). Variantes: barrido en vídeo FHD → `G50-FHDPHOTO`; barrido en ráfaga a resolución completa → Focus Shift Shooting. Ver [g52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g52-post-focus.md).
- ❌ 4K/6K Photo (incl. 4K Photo Burst S/S) — _Origen: Panasonic GH5, G9_. El IMX210 de la A6000 solo lee 6000×4000 a 15 fps o 1996×1124 a 60 Hz (sin modo ≥3840 columnas), el codificador llega a 1080p60 (≈135 Mpx/s frente a 249 de 4K30) y el firmware no tiene la vista Photo Capture de la A6300. Ver [g50](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g50-4k-6k-photo.md).
- ❌ Pixel Shift Multi Shooting / High Res Shot / Handheld High Res Shot — _Origen: ≈Sony α7R III; Olympus E-M1 II, E-M1X; Panasonic G9_. La A6000 no tiene IBIS (estabilizador solo en el objetivo, OSS; sin cadenas ni piezas de actuador de cuerpo) y la alta resolución computacional exigiría salida >6000×4000, ≈384–480 MB de búferes y codificador nuevos (el MFNR del DSP fusiona a resolución de sensor). Ver [G49](../docs/gui/g49-pixel-shift-alta-resolucion.md).
- ❌ Nivel digital (horizonte virtual) — _Origen: ≈Sony α6300_. La A6000 no tiene acelerómetro: su sensor de orientación (SE7750) es óptico y cada uno de sus dos canales solo da alto o bajo, así que distingue cuatro posiciones a 90° y nada intermedio. Medido por SWD girando la cámara ([R88](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r88-sensor-inclinacion-swd.md)).
