# eye-af — Eye AF en tiempo real en la A6000 (26-11-2026)

Fecha: 26-11-2026. Estado: **implementado y verificado offline; sin probar en cámara**. Fuentes:
`orb-server` y `libInfraWebApi.so` de fw3.21 (extracción local), `SmartRemote.odex` de fw3.21 y la
medición en esta máquina del detector. Evidencia: [`analysis/eyeaf/`](../../analysis/eyeaf).

Etiquetas: **VERIFICADO** (bytes o ejecución citados) · **INFERENCIA** · **NO_VERIFICADO**.

La A6000 no trae Eye AF de fábrica (sí detección de caras), pero su **API remota de "touch AF"**
mueve el punto de enfoque a unas coordenadas y enfoca allí. Con un detector de ojos en el PC que
mande la posición del ojo por esa API, la cámara enfoca el ojo a la frecuencia que fije el bucle.

## 1. Arquitectura

```
cámara (app Smart Remote Control, orb-server)          PC (tools/eye-af)
  startLiveview ──► JPEG por HTTP chunked ────────────► EyeDetector (YuNet) ─► EyeTracker
  setTouchAFPosition(x, y) ◄── coordenadas 0..100 ◄──── banda muerta + máx. Hz
        └─► mueve el marco de AF y enfoca (AFResult)
```

Ninguna pieza toca firmware: (a) el productor de Live View que la cámara ya tiene, (b) la orden de
punto de AF que la cámara ya tiene, (c) la visión, que es lo único nuevo y vive en el PC.

## 2. Hechos verificados (fw3.21)

Detalle con direcciones en [`analysis/eyeaf/orb_touchaf.md`](../../analysis/eyeaf/orb_touchaf.md) y
[`orb_liveview.md`](../../analysis/eyeaf/orb_liveview.md).

| Hecho | Evidencia | Estado |
|---|---|---|
| `setTouchAFPosition` existe en `orb-server`: `params` = **[x, y]** posicionales, dos `double` | `parameterTypes()` `0x215958`; `call()` `0x21574c` exige longitud exactamente 2 | VERIFICADO |
| Las coordenadas son **porcentaje del encuadre 0..100** (no 0..1, no píxeles) | constantes `100.0` en `0x215308`; fuera de rango ⇒ `parameter err` y no se envía | VERIFICADO |
| La orden viaja como mensaje `msgid 0x192 / paramid 0x8d` de 1568 B a la cámara | `invoke()` `0x214ec8`, `setEvtParamId` `0x18773c`, `sendMsgToServer` `0x18767c` | VERIFICADO |
| La respuesta es `[0, {"AFResult": bool, "AFType": "Touch"}]`; el `AFResult` lo produce la cámara | `SetTouchAFPosition_invoke_cmd` `0x1a7820`; esquema `0x327d9c` | VERIFICADO |
| `cancelTouchAFPosition` (`0x195/0x90`) y `getTouchAFPosition` (`0x198/0x93`) existen; `get` devuelve `touchCoordinates` **siempre vacío** | `0x1b756c`: array creado sin ningún `push` | VERIFICADO |
| El método aparece en `getAvailableApiList` sólo si la cámara anuncia el **id 45**; `orb-server` no filtra por modo ni por objetivo | `GetAvailableApiList_invoke_cmd` `0x1b52b0`; tabla `0x2e4514` | VERIFICADO (mecanismo); condiciones de la cámara NO_VERIFICADO |
| Live View: HTTP **chunked, un JPEG por chunk**, `startLiveview` sin parámetros | `0x21fe2c`/`0x21feac`; 0 ocurrencias de multipart/MJPEG en `orb-server` | VERIFICADO |
| URL de Live View `http://192.168.122.1:8080/liveview/liveviewstream` en la app; `orb-server` arranca con `-p 10000` | literal en `SmartRemote.odex` off. `0x247b67`; `WebApiLauncher.sh` → `orb-server -f … -p 10000` | VERIFICADO (dos literales; cuál se usa en cada modo NO_VERIFICADO) |
| `getEvent` no publica caras: no hay `faceDetection` ni `faceInfos` | 0 ocurrencias en `orb-server` | VERIFICADO |
| Modos de enfoque aceptados por nombre: `MF, AF-S, A-Macro, AF-C, AF-A, AF-D, DMF, MF-R` | tabla `0x2e5244` | VERIFICADO |
| El `orb-server` de la A7S fw3.20 es **idéntico** byte a byte; el de la A6300 no añade ninguna API de ojos (`EyeAF`, `pupil`, `face`) | sha256 `2ef500ba…`; tabla de métodos del A6300 | VERIFICADO |

**Consecuencia:** el Eye AF nativo de la A6300 no se puede heredar por API (no está expuesta) y la
A6000 no tiene canal externo a `Camera::FC`; la vía interna es la orden `PARAMID_EYE_START_AF`
(`0x4054`, solo copia al espejo, ver [g83](../gui/g83-barrido-objetivos-restantes.md)). La vía realista
es dirigir el punto de AF desde fuera, que es lo que hace este carril.

## 3. Qué hace el bucle

Cada cuadro de Live View se detectan caras y ojos (YuNet, 5 landmarks) y se elige **un** ojo: el de
la cara más grande; en cuadros siguientes se mantiene la misma cara salvo que aparezca otra
claramente mayor. Después:

- **Suavizado** EMA (`--smooth`, 0.4) para no traducir el ruido del detector en micro-órdenes.
- **Salto limpio** si el objetivo se mueve más de `--jump` (0.35): un barrido del punto de AF por
  todo el encuadre no tiene sentido, es un sujeto nuevo.
- **Banda muerta** `--min-move` (1 % del ancho): no se manda orden nueva si el ojo no se movió.
  El marco de AF es discreto y cada orden puede relanzar un ciclo de enfoque.
- **Límite de frecuencia** `--max-hz` (3 por defecto): techo duro de órdenes por segundo.
- **Pérdida** `--lost-after` (1.5 s): al desaparecer el ojo, `cancelTouchAFPosition` una sola vez.

## 4. Implementación

| Archivo | Papel |
|---|---|
| `tools/eye-af/eyeaf/detector.py` | YuNet (`cv2.FaceDetectorYN`) → ojos normalizados 0..1; degradación a cascadas Haar |
| `tools/eye-af/eyeaf/api.py` | cliente JSON-RPC de `/sony/camera`, autodetección de puerto, `parse_af_result` |
| `tools/eye-af/eyeaf/liveview.py` | flujo de Live View → JPEG → BGR por SOI/EOI (independiente del boundary) |
| `tools/eye-af/eyeaf/tracker.py` | elección de ojo, suavizado, banda muerta, límites, cancelación |
| `tools/eye-af/eyeaf/loop.py` | bucle, estadísticas, grabación, ventana (ESC sale, ESPACIO dispara) |
| `tools/eye-af/fake_camera.py` | cámara falsa con el mismo contrato, para probar sin hardware |
| `scripts/eye_af.py` | lanzador (convención `scripts/`) |
| `tools/eye-af/README.md`, `BENCH.md` | uso y latencia medida (16,4 ms de media a 640x480) |

## 5. Verificación hecha (sin cámara)

- **28 pruebas** offline: `tests/test_eye_af_{api,tracker,loop,detector}.py` — contrato de la API
  contra la cámara falsa (incluido el error JSON de la cámara), parser de Live View con basura y
  JPEG partidos, controlador (banda muerta, Hz, suavizado, salto de sujeto, cancelación), detector
  (ojos en 0..1, dos ojos con lados opuestos, imagen negra sin detecciones) y **bucle completo**:
  la cámara falsa sirve el retrato de prueba y recibe `setTouchAFPosition` con las coordenadas del
  ojo detectado, en los cuatro espacios de coordenadas (incluido el 0..100 real de la A6000).
- **Ejecución real del comando de usuario** contra la cámara falsa: 19,3 fps de media, 98 cuadros
  en 5 s, 16–19 ms de detección por cuadro, una sola orden de AF con el sujeto quieto (la banda
  muerta hizo su trabajo).
- `ruff` y `mypy` limpios en los ficheros nuevos.

## Límites

- **NO_VERIFICADO en hardware**: no se ha llamado a la cámara. Falta comprobar que anuncia
  `setTouchAFPosition` (id 45) en `getAvailableApiList`, en qué modo, y si cada orden hace AF
  puntual, AF continuo o sólo reposiciona el marco.
- **La cámara está en 3.26 y el análisis es de fw3.21.** No se ha verificado que `orb-server` de
  3.26 conserve la misma firma; la familia se comporta igual (A7S idéntico) pero eso no es prueba.
- NO_VERIFICADO: tamaño y tasa reales del Live View, puerto efectivo (8080/10000), latencia de ida
  y vuelta por Wi-Fi y comportamiento con el sujeto en movimiento.
- El detector depende de la luz y del ángulo: falla de perfil extremo, muy cerca o con el ojo
  tapado; la ruta Haar de respaldo es mucho peor (documentado en el código).
- La foto (`actTakePicture`) relanza su propio enfoque: no se puede disparar AF y foto con la misma
  orden. El bucle no dispara solo; ESPACIO en la ventana de previsualización.
- No se ha medido la distorsión ni la precisión del punto sobre el sensor: el Live View es ≈2 MP y
  el marco de AF tiene su propia granularidad.

## 6. Uso

```shell
# en la cámara: abrir la app "Smart Remote Control" y conectarla a la misma red
.venv/bin/python scripts/eye_af.py --host <IP> --check                  # ¿está la API?
.venv/bin/python scripts/eye_af.py --host <IP> --preview --focus-mode AF-C
```

Sin cámara, para ver la visión y el bucle:

```shell
.venv/bin/python tools/eye-af/fake_camera.py --image tools/eye-af/tests/data/obama-2012-retrato-dominio-publico.jpg --port 8080 &
.venv/bin/python scripts/eye_af.py --host 127.0.0.1 --dry-run --preview
```

## 7. Criterio de cierre (pendiente físico)

Con un rostro en el encuadre, el marco de AF sigue al ojo (no a la cara) a ≥2 Hz con
`--focus-mode AF-C`, `AFResult` verdadero en la mayoría de las órdenes, y una foto con ESPACIO sale
enfocada en el ojo. Registrarlo con capturas y latencias. Riesgo bajo: todo es API pública de la
cámara, sin escrituras en RAM, NVRAM ni firmware.
