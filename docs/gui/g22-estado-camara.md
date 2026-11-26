# G22-E — Batería, carga y USB en el arnés

Qué añade esta tarea al emulador: un **estado de cámara del anfitrión** (batería 0-100, carga, jack USB, HDMI) que se puede cambiar en
caliente y viaja al invitado con dos órdenes nuevas del protocolo LIVE del shim. No hay ninguna lectura del estado real de la cámara: no
existe vía verificada para leer el nivel de batería ni el jack desde software de la cámara, así que esto es **modelo del anfitrión +
inyección**, no emulación del origen.

Código: `scripts/gui/harness/estado_camara.py`, `camara_web.py`, la sección `camara` de `emu_config.py`, los comandos `U`/`B` de
`shim/sonyshim.c` y **dos líneas** de enganche en `live.py` (una en `do_GET`, otra en `do_POST`, junto a `sensor_web.maneja`).
La página del lienzo (`PAGINA`, su HTML/JS) no se toca; el control vive en su propia página, `GET /camara/`.

## 1. Protocolo

| Orden LIVE | Efecto en el invitado | Evidencia del origen |
|---|---|---|
| `U <0\|1>` | Estado del jack USB: mensaje `{clave 0x7000001, 0, estado, 0, índice 0x177}` a la cola `0x7a0020`, la **misma construcción** que `KEYINIT` (ahora en el ayudante `entrada_estado()`) | §5.18w de [g22-arnes-ui-qemu.md](g22-arnes-ui-qemu.md): `KEYINIT=7000001:1:177` = «jack USB (evento `0x15040010`)», índice físico medido, sin índices inventados |
| `B <0..100>` | Nivel de batería de la respuesta emulada de CamMgr (`CAMGREMU`, mensaje `0x3001`, palabra 3; antes fijo `0x0064`). Por omisión 100 % | Bloque `CAMGREMU` del shim (§5.18 del mismo informe); el layout de la respuesta sigue siendo **INFERENCIA** |

`B` se parsea en **decimal** (no hex, al revés que `K`/`U`): `100` tiene que valer cien. `U` usa el mismo `hexv` que el resto.

Puntos HTTP de `camara_web.py` (`maneja(h, metodo, ruta, cuerpo, vm)`):

| Punto | Cuerpo | Respuesta |
|---|---|---|
| `GET /camara/` | — | página con los controles (batería, USB, HDMI) |
| `GET /camara/estado` | — | `{"modelo": {bateria, usb, hdmi, cargando}, "invitado": {conectado, dir, shim}, "config": ruta}` |
| `POST /camara/bateria` | `{"pct": 0..100}` | modelo actualizado + `enviado: ["B 5"]` |
| `POST /camara/usb` | `{"on": true\|false}` | modelo actualizado + `enviado: ["U 1"]` |
| `POST /camara/hdmi` | `{"on": true\|false}` | solo modelo; `enviado: []` y una `nota` (ver §5) |

`invitado.shim` son las últimas líneas del shim sobre estos eventos, buscadas en `live/<perfil>/shim.log` (con `WAITLOG`/`WLALL`) y en la
consola del invitado. Es lo único que el anfitrión puede afirmar del invitado sin la cámara: que el mensaje llegó y que alguien lo leyó.

## 2. VERIFICADO (medido en esta rama)

- **El shim compila y no añade símbolos que falten en el invitado.** `shim/build.sh` con el sysroot de `analysis/gui/g22/harness/stage` y
  la libc 2.11.2 de la cámara: 0 errores. El conjunto de símbolos indefinidos (sin versión) del `.so` nuevo es **el mismo que el del shim
  de `main`, menos uno** (71 → 70): desaparece `__isoc23_strtol` (§4).
- **Batería y jack llegan al invitado y un hilo los consume.** Sesión E2E con `SHIMEXTRA="CAMGREMU=1"`, perfil `estado`, puerto 8610.
  En `live/estado/shim.log` (con `WLALL=1` activado en caliente por `POST /linea`):

  ```
  593.66 255.24 JACK USB estado=1 (LIVE, driver de entrada 0x7a0020)
  593.74 255.34 rcv_msg qid=0x7a0020 <- respuesta
  614.89 276.49 JACK USB estado=0 (LIVE, driver de entrada 0x7a0020)
  636.20 297.78 BATERIA 5 % (LIVE, respuesta emulada de CamMgr)
  657.31 318.90 BATERIA 100 % (LIVE, respuesta emulada de CamMgr)
  ```

  El `rcv_msg qid=0x7a0020 <- respuesta` inmediato es el hilo lector del driver de entrada del invitado (`libObj+0x806f88`, §5.18w)
  sacando el mensaje del buzón: el mensaje se entrega, no se descarta.
- **La pantalla no cambia con ninguna de las dos órdenes.** Diffs de fotograma (640×480, umbral 12 sobre la suma RGB) en la sesión con el
  shim corregido, con el invitado vivo y el OSD ya poblado:

  | Comparación | Píxeles distintos |
  |---|---|
  | ruido (dos capturas seguidas sin tocar nada) | **0** |
  | antes → `U 1` | **0** |
  | antes → `U 0` | **0** |
  | antes → `B 5` | **0** |
  | antes → `B 100` | **0** |
  | `U 1` → `U 0` | **0** |
  | `B 5` → `B 100` | **0** |

  Capturas: [OSD poblado](img/g22-estado-camara-osd.png) (idéntica antes y después de conectar/desconectar USB y de cambiar la batería) y
  [OSD a medio poblar](img/g22-estado-camara-osd-vacio.png).
  En una sesión anterior, sin la corrección del §4, el `B` mató al invitado a mitad de la tanda; los tres PNG de esa tanda no valen como
  medida y no se usan aquí.
- **No hay indicador de batería que pueda cambiar.** En las capturas hay modo `P`, formato `3:2 24M FINE`, `1080`, `AF-S`, medición, `AWB
  A2 G1`, `DRO AUTO`, estilo, `ISO 25600`, `+0.5`, efecto y dos `OFF` (SteadyShot y otro), y el icono naranja con «ERROR» de soporte. Ese
  icono es el **mismo** que aparece en la captura de referencia [g22-osd-iconos-poblados.png](img/g22-osd-iconos-poblados.png) de §5.18
  (OSD-ICONOS-1), donde se describió como batería poblada por av-cam: aquí se ve que **no cambia con `B`**, así que no se puede afirmar
  que sea el nivel de batería. Queda como observación para revisar esa fila (no se edita aquí).
- **Nadie contesta al CamMgr en este perfil.** En la sesión medida, `live/estado/avcam.jsonl`: **0** peticiones del invitado a `0x30001`
  (`entra`) y **0** respuestas de av-cam por esa cola (`sale`); y el shim, con `CAMGREMU=1`, no registró ni una línea `CamMgr MSGID`. Es
  decir: en el estado por defecto del arnés el nivel de batería **no tiene consumidor**, ni por av-cam (AVQ) ni por el shim. `B` solo
  cambia la variable que usaría la respuesta emulada cuando alguien pregunte.
- **Persistencia.** Tras los `POST`, `~/.config/a6000-emu/config.json` queda con
  `"camara": {"bateria": 100, "usb": false, "hdmi": false}` y el resto de secciones intactas (se validó y reescribió con
  `emu_config.guarda_config`, atómico).
- **Arranque en frío cronometrado** (`live.py … --perfil-dir estado --puerto 8610`, av-cam conectado): primer fotograma a los **186 s**
  (run 1, shim anterior), **143 s** (run 2) y **173 s** (run 3, shim corregido). Las tres sesiones compartieron CPU con otros dos
  `qemu-system-arm` de otros agentes, así que los números no son un banco de medidas; sí confirman el orden de magnitud de 2–3 min.
  **No se midió la restauración desde `estado.zst`** (cada sesión cambió `SHIMENV`, y la huella invalida el estado guardado).
- **La página `GET /camara/` se sirve** con sus controles (lo comprueba el test de los puntos HTTP). No se ha abierto en un navegador en esta
  sesión: lo probado es la respuesta del servidor, no el aspecto en pantalla.
- **Pruebas.** `pytest tests/test_gui_harness.py` → 39 pasan, 8 saltan (las lentas con `A6000_HARNESS_RUN=1` y las que exigen CFW), con
  `A6000_HARNESS_WORK=/home/nicolas/a6000-arnes/analysis/gui/g22/harness` para que el test de compilación del shim tenga sysroot;
  `tests/test_live_shimenv.py tests/test_shim_logic.py tests/test_live_reintento.py` → 37 pasan. `ruff` limpio en los módulos nuevos,
  `emu_config.py` y los tests; `live.py` conserva el `I001` (imports sin ordenar) de su bloque, que ya estaba en `main`. `mypy` sin
  errores nuevos en los dos módulos nuevos (`emu_config.py` arrastra los suyos, previos).

## 3. INFERENCIA

- **«USB conectado ⇒ cargando»**. La A6000 carga por USB con la cámara apagada y, encendida, se alimenta por el mismo conector; el
  firmware no expone en lo medido un bit de carga distinto del estado del jack. El modelo lo deduce (`Estado.cargando = usb`) y así se
  documenta en la página; **no** se ha comprobado contra la cámara.
- **Cambiar el jack en caliente sí cambia el estado de `InputService`**: es el mismo mensaje que en §5.18w hacía que
  `CheckerUSBAndClockReady` viera `jackStatus : 2`. Pero `execCheck` corre al **activar** la vista, así que un cambio posterior no
  reevalúa esa guarda. No se ha vuelto a medir `jackStatus` en esta sesión (haría falta `TRACEFN` en un arranque en frío).
- El layout de la respuesta de CamMgr `0x3001` (palabra 3 = batería) sigue siendo el del shim anterior, sin verificar contra av-cam.

## 4. Defecto encontrado y corregido (medido)

El primer `B` mató al invitado: `/usr/bin/im.elf: symbol lookup error: /usr/lib/sonyshim.so: undefined symbol: __isoc23_strtol` y
`IMEXIT im_s 127` en `live/estado/consola.log`. Causa: en este sysroot `strtol`/`atoi` se enlazan como `__isoc23_strtol` y la glibc 2.11.2
del invitado no lo tiene; la resolución es perezosa, así que el shim carga bien y **muere el proceso al primer uso**. Dos consecuencias:

- el parseo de `B` ya no usa `strtol` (bucle de dígitos, como `hexv`/`num`);
- `rt_on()` usaba `atoi(getenv("RTMAP"))`, que era la **misma mina** en `main` (el shim de `main` también exporta ese símbolo): con
  `RTMAP` definido el invitado moriría igual. Se cambia a `num()`, que ya existía para esto (`sin atoi: el sysroot nuevo enlaza
  __isoc23_strtol`, dice el comentario del propio fichero). Tras el cambio, el conjunto de símbolos indefinidos del `.so` es el de `main`
  **menos** `__isoc23_strtol`.

## 5. NO_VERIFICADO y lo que no se puede medir sin la cámara

- **Qué hace la cámara al conectar el jack USB** (icono de carga, diálogo «Modo USB», si carga encendida o solo apagada). Requiere la
  cámara física y el cable: no se simula a ciegas.
- **Que el icono de batería de la OSD responda a `B`**: en este estado del arnés **no hay ningún icono que cambie** y nadie pide el nivel
  (§2). Para cerrarlo hace falta (a) saber qué modelo/vista consume `0x3001` y (b) el layout real de av-cam; con eso se podría forzar la
  consulta y comparar. Hoy `B` queda como **modelo del anfitrión + shim**, sin efecto observable en el firmware.
- **HDMI**: no hay orden en el shim para ese jack (el bucle CEC del invitado está silenciado, §5.18); `POST /camara/hdmi` solo guarda el
  modelo y lo dice en su respuesta. No se inventa una orden.

## 6. Reproducir

```sh
cd /home/nicolas/h-estado
/home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir estado --puerto 8610
# en otra terminal (≈ 2-3 min hasta el primer fotograma; el OSD tarda otro minuto en poblarse)
curl -s http://127.0.0.1:8610/camara/estado
curl -s -X POST -H 'Content-Type: application/json' -d '{"on":true}'   http://127.0.0.1:8610/camara/usb
curl -s -X POST -H 'Content-Type: application/json' -d '{"pct":5}'      http://127.0.0.1:8610/camara/bateria
# fotograma actual (PNG): POST /refrescar y leer el primer «data:» de GET /eventos; cerrar con POST /salir
```

Para ver las líneas del shim: `POST /linea` con `E WAITLOG=1000` y `E WLALL=1` (quedan en `live/<perfil>/shim.log`). Con `CAMGREMU=1` en
`SHIMEXTRA` el shim contesta al CamMgr en vez de dejar pasar `0x30001` a av-cam.

## 7. Límites de este cambio

- El estado vive en el **config del configurador** (`~/.config/a6000-emu/config.json`, o el `--config` de `live.py`): la primera sesión
  que use el control añade la sección `camara` a ese fichero (aditivo y con validación; no toca las demás).
- `B`/`U` son **modelo del anfitrión**: no hay realimentación desde la cámara. Si la cámara está apagada o no arranca, el modelo sigue
  diciendo lo que el usuario puso.
- El enganche en `live.py` son dos líneas de backend; la página del lienzo no se ha tocado (otro subagente trabaja ahí).

## 8. Quién pinta la batería y la carga (27-11-2026, estático + medido; G22-OSD-REFRESCO)

Ver [G22-OSD-REFRESCO](g22-osd-refresco.md). Lo que faltaba aquí —«no hay indicador de batería que pueda cambiar»— ya tiene cadena:

- El icono existe y es `ACT_IconBattery` (con `ACT_IconBattery_Rec` y `ACT_IconBatteryLevel_C`). Su actualización es
  `ACT_IconBattery::WidgetUpdateSync` (`viewUnified2+0x2758b8`) → `b.w 0x275530`, que consulta **`model/POWER` info 0** claves **`0x100`**
  (tipo de alimentación, el mismo que lee `CmnViewModelWrpPowerState::getPowerType`, `viewUnified2+0x243c50`), **`0x102`** y **`0x104`**, y
  **`@M084` info 1** clave **`0x101`**.
- `0x3001` sigue **sin consumidor** en el perfil medido (0 peticiones): `B` alimenta una respuesta que nadie pide. Para que el nivel se
  pinte sin av-cam hay que rellenar esas claves de `model/POWER` (siguiente paso en la ficha G22-OSD-REFRESCO).
- El jack USB **no** se consulta al llegar el mensaje: `InputService::getInputEventStatus` con la clave `0x15040010` lo leen los `execCheck`
  de `ViewRootPowerSw` (`CheckerUSBAndClockReady`, literales en `viewUnified2+0x17083c/0x1708cc/0x171a7c`), que corren **al activar** la
  vista. Por eso `U 0|1` con la vista abierta da 0 px, y por eso re-activarla (`O view/STLREC`) sí cambia lo que se ve.

## PARA PENDIENTES.md

| ID | Estado | Qué es | Criterio de cierre | Origen |
|---|---|---|---|---|
| G22-ESTADO-CAMARA | EN CURSO (26-11-2026) | **Batería, carga y USB del arnés (G22-E)**: modelo del anfitrión (`estado_camara.py` + sección `camara` del config) y dos órdenes LIVE nuevas del shim — `U <0\|1>` (jack USB como el driver de entrada: `{0x7000001, 0, estado, 0, 0x177}` a `0x7a0020`, la vía de §5.18w) y `B <0..100>` (palabra 3 de la respuesta emulada de CamMgr, `CAMGREMU`). Puntos `GET /camara/estado`, `GET /camara/`, `POST /camara/{bateria,usb,hdmi}`; enganche de dos líneas en `live.py`. **Medido**: el mensaje del jack llega y un hilo lo lee (`rcv_msg qid=0x7a0020`), pero **la pantalla no cambia** (0 px en 7 comparaciones, incluido el ruido); `B` no tiene consumidor (0 peticiones a `0x30001` en el perfil `estado`, av-cam tampoco contesta) y no hay icono de batería que cambie; HDMI solo modelo | Cerrar cuando (1) se identifique el modelo/vista que consume `0x3001` y el layout real de av-cam, de modo que un cambio de nivel se vea en la OSD o se demuestre que la A6000 no lo pinta con esos datos; (2) se compruebe en la cámara física qué produce el jack USB (icono de carga y/o «Modo USB», y si carga con la cámara encendida) y se refleje o se deseche `cargando = usb`; (3) haya orden verificada (o decisión explícita de no tenerla) para el jack HDMI | [G22-E estado de cámara](gui/g22-estado-camara.md) · `scripts/gui/harness/{estado_camara,camara_web}.py` · `shim/sonyshim.c` · `tests/test_gui_harness.py` |

## 9. Que la OSD pinte el estado del anfitrión (28-11-2026): `model/POWER` desde el shim y repintado del invitado

Intento de cerrar el punto (1) y el (2) de esta fila: que el nivel de `B` llegue al icono de batería y que `U` cambie lo que se ve.
Lo implementado queda (es el mínimo que pedía la ficha y es correcto en su sitio); lo que **no** se consigue es el cambio visible, y
ahora se sabe **por qué** con medida, no por inferencia: **en la OSD del arnés nadie pregunta por `model/POWER` y el icono de batería
no se instancia**. Detalle abajo.

### 9.1 Qué se ha añadido (código)

1. `shim/sonyshim.c` — `power_params()`: responde `getModelInfo("model/POWER", …)` **cuando la llamada real falla** (si el modelo
   existe —av-cam/UPM— manda él) con el nivel del anfitrión, igual que `reloj_params` hace con `@M018` y `CAMGREMU` con CamMgr.
   Está enganchada en las tres puertas que el arnés ya usaba o podía usar: `viewManagerIf::getModelInfo` (la que la OSD usa de
   verdad: **37 222** llamadas en la sesión medida), `ViewBase::getModelInfo` y `LayoutableWidgetBase::getModelInfo` (nueva).
   `POWEREMU=0` lo apaga y `POWERPCT=nn` fuerza el nivel (diagnóstico).
2. `shim/sonyshim.c` — `repinta()` / `repinthot()`: tras `B` y tras `U`, **el invitado** vuelve a activar la vista de disparo con la
   misma ruta que REDIAL (`openView("view/STLREC")` sin argumento: el modo lo da el firmware). `REPINT=0` lo apaga —es el control de
   la medida: mismo cambio de estado sin reapertura— y `REPINTROOT=1` añade el `O view/ROOT` previo. `live.py`, el HTML y el JS **no
   se han tocado**: el anfitrión sigue mandando solo `B`/`U`.
3. `tests/test_g22_osd.py` — 4 casos nuevos sin QEMU (relleno de `model/POWER`, «no pisa al modelo real», repintado del invitado y
   los bytes de las claves que se rellenan). `sonyshim.so` reconstruido: **mismo conjunto de símbolos indefinidos** (70, ninguno nuevo).

### 9.2 Claves que lee el icono (bytes verificados, `viewUnified2.so` md5 `1adc8395…`)

`ACT_IconBattery::WidgetUpdateSync` (`+0x2758b8`) salta a `+0x275530`, que hace **dos** consultas y seis puertas:

| consulta | clave | instrucción (VA) | qué exige |
|---|---|---|---|
| `"@M084"` info **1** | `0x101` | `movw r1,#0x101` en `+0x275568` | si vale 1 o 2 **no pinta** (`+0x275580` → `+0x27575a`) |
| `"model/POWER"` info **0** | `0x100` | `mov.w r1,#0x100` en `+0x2755a0` | tiene que ser **2** (`cmp r0,#2; bne` en `+0x2755b4`) |
| | `0x102` | `mov.w r1,#0x102` en `+0x2755be` | booleano cierto (tipo 5) |
| | `0x104` | `mov.w r1,#0x104` en `+0x2755dc` | booleano cierto (tipo 5) |
| | `0x105` | `movw r1,#0x105` en `+0x2755fa` | entero ≠ 0; se reenvía como **filtro `0x107`** de la consulta siguiente |
| | `0x103` | `movw r1,#0x103` en `+0x27561a` | entero ≤ el valor cacheado del icono, que su constructor deja en **3** (`str.w r3,[r4,#0x960]` en `+0x275872`, con `+0x95c=1` y `+0x95d=1`) |
| `"model/POWER"` info **1** (con filtro `0x107`) | `0x108` | `mov.w r1,#0x108` en `+0x2756bc` | tiene que ser **1** |
| | `0x10b` | `movw r1,#0x10b` en `+0x2756d4` | tiene que ser **2** |
| | **`0x10c`** | `mov.w r1,#0x10c` en `+0x2756ec` | **el nivel 0..100**: elige entre cinco imágenes con umbrales **20 / 50 / 80** y `0` = apagado (`+0x275726…+0x27573c`) |

Lo que rellena `power_params()` es justo eso: info 0 → `0x100=2`, `0x102`/`0x104` ciertos, `0x103=3`, `0x105=1`; info 1 → `0x108=1`,
`0x10b=2`, `0x10c = B`. El nombre `model/POWER` sólo se construye en **dos** sitios de `viewUnified2` (barrido de todo `.text`
resolviendo los literales pc-relativos): `+0x2756ac` (este icono) y `+0x1ca4c4` (`CmnViewModelWrpPowerState`).

### 9.3 Lo medido (perfil `estado2`, puerto 8670, 640×480)

Sesión restaurada de `estado.zst` (restauración con la OSD ya poblada: primera pantalla a los **11 fotogramas / 15 s**). `WLALL=1` +
`WAITLOG=1000` desde el arranque, `SETLOG=1`, y trampas `TRACEFN2` armadas en caliente sobre `viewUnified2` (`TRACELIB`).

- **El repintado del invitado funciona.** Cada `B`/`U` deja en `live/estado2/shim.log` la orden (con el nivel) y la reapertura que
  pide el propio invitado:

  ```
  538.47 342.04 BATERIA 5 % (LIVE, respuesta emulada de CamMgr y model/POWER)
  538.48 342.05 REPINT BATERIA: el invitado vuelve a activar view/STLREC
  538.83 342.40 OPENVIEWDIAL getRecViewFromDial() = 3
  538.84 342.41 OPENHOT view/STLREC 0x3 -> 14438696
  ```

- **`model/POWER` no se pide nunca.** Con `SETLOG=1`, en la sesión hay **37 222** llamadas a `viewManagerIf::getModelInfo` y **0** con
  `model/POWER` (ni con `@M084`). Modelos pedidos: `model/CAMERA` 28 510, `model/STILL_REC` 6 388, `@M096` 1 583, `model/REMOTE` 415,
  `@M00A` 139, `model/INH_WRAPPER` 106, `@M006` 38, `@M09C` 22, `@M007` 20, `@M00B` 1. Es decir: el gancho del shim **sí** está en el
  camino que usa la OSD (por eso llegan esas 37 222), y la consulta de alimentación simplemente no ocurre.
- **El icono no se instancia.** Trampas armadas tres veces (`TRACEFN2`): `0x2758b8` (`WidgetUpdateSync`), `0x275530` (la actualización),
  `0x275804` (su construcción: `str +0x960=3`), `0x275524` (`SetInfoOffVal`), `0x2c90c0` (`ACT_IconBattery::cast`) y `0x2c91d4`
  (`Check_ACT_IconBattery`): **ninguna se disparó** en toda la sesión (ni al reabrir `view/ROOT`+`view/STLREC` ni al abrir el menú
  `@V00E`). La única traza que saltó fue `1b4b10` con `@M00B` info `0x61` clave `0x2b5` desde `viewUnified2+0x27ab7a` (otro consumidor).
  La clase existe en el paquete (descriptor en `viewUnified2+0xbacc`), pero **no hay instancia en la OSD de este arnés**: sin instancia
  no hay quien lea `model/POWER`, y por eso ningún valor del anfitrión puede pintarse todavía.
- **El jack USB tampoco cambia el contenido.** `U 0`/`U 1` con reapertura (y con `REPINTROOT=1`) no mueven un píxel fuera de la banda
  animada de abajo: `CheckerUSBAndClockReady` es un `execCheck` que **decide**, no dibuja (§2 de `g22-osd-refresco.md`).

Fotogramas estables (dos capturas seguidas idénticas; el OSD se desvanece al repintar y comparar durante la transición da diferencias
de **alfa** en todo el fotograma, no de contenido). Fracción de píxeles **opacos**: OSD **0,080–0,092** (la variación es el elemento
animado y el desvanecido, no el estado). Diferencias **de contenido (solo RGB)**:

| comparación | todo el fotograma | fuera de la banda animada (`y < 340`) |
|---|---|---|
| `B 100` → `B 5` | 2 374 px, caja (357,344)-(625,471) | **0 px** |
| `B 5` → `B 30` | 3 911 px, caja (357,367)-(639,471) | **0 px** |
| `B 30` → `B 100` | 0 px | **0 px** |
| `B 100` → `B 5` (2.ª vez) | 3 911 px, misma caja | **0 px** |
| `POWEREMU=1` → `POWEREMU=0` con `B 5` | 3 911 px, misma caja | **0 px** |
| `U 0` → `U 1` | 0 px | **0 px** |
| `U 1` → `U 0` | 890 px, caja (498,438)-(575,471) | **0 px** |
| **control**: reabrir la misma vista con el mismo estado | **859 px**, caja (321,344)-(609,471) | **0 px** |

El control (misma vista reabierta, mismo estado) da **más** píxeles que `U 0`→`U 1`: todo lo que cambia en la columna «todo el
fotograma» es la banda `y ≥ 344` que **parpadea sola** (medidor/indicadores), no el estado de la cámara. Fuera de esa banda el
fotograma es idéntico en las 8 comparaciones. Capturas: [batería 100](img/g22-estado-camara-bateria100.png) ·
[batería 5](img/g22-estado-camara-bateria5.png) · [USB 1](img/g22-estado-camara-usb1.png) · [USB 0](img/g22-estado-camara-usb0.png)
(las cuatro con OSD poblado; las dos de batería son indistinguibles fuera de la banda animada).

### 9.4 Qué falta, exactamente

1. **Que exista el icono**: la OSD de este arnés no crea la instancia de `ACT_IconBattery` (traza negativa de §9.3). Hasta que el
   layout la cree, `B` no tiene dónde pintarse. Caminos concretos: (a) averiguar de qué recurso de layout sale el icono y qué condición
   lo excluye (candidato: el layout se construye con la lista de widgets que da el modelo de cámara/`model/CAMERA` y la batería falta
   ahí); (b) `M model/POWER` + `S <id>` en caliente **antes** de abrir la vista, para que el layout lo vea; (c) llamar nosotros a
   `+0x2758b8` sobre una instancia existente (hoy no hay ninguna: hace falta el puntero del widget).
2. **Reabrir no basta para el jack**: hay que emular la transición de `ModelUsb*`/`CmnViewNoHdmi` (vista `…USB_CONNECTING`,
   `CmnViewNoHdmi::enterConcurrentHdmiUsbMode`, `+0x1a9060`) o documentar que la A6000 sólo consulta el jack al activar la vista.
3. Nada de esto invalida lo implementado: `power_params()` está en el gancho que la OSD usa de verdad (37 222 llamadas) y el
   repintado del invitado está medido (`OPENHOT view/STLREC`); lo que falta es **consumidor**, no camino.

### 9.5 Bloque PARA PENDIENTES.md (28-11-2026; sustituye las dos filas de §8)

| ID | Estado | Qué es | Criterio de cierre | Origen |
|---|---|---|---|---|
| G22-ESTADO-CAMARA | EN CURSO (28-11-2026) | **Estado de cámara en la OSD.** Modelo del anfitrión (`estado_camara.py`, sección `camara`) + órdenes LIVE `B <0..100>` y `U <0|1>`. Añadido 28-11: `power_params()` en el shim responde `getModelInfo("model/POWER", 0/1)` con el nivel de `B` cuando la llamada real falla (claves medidas en `viewUnified2+0x275530`: info 0 → `0x100=2`, `0x102`/`0x104` ciertos, `0x103=3`, `0x105=1`; info 1 → `0x108=1`, `0x10b=2`, **`0x10c` = nivel**, umbrales 20/50/80) y `repinta()` hace que **el invitado** reabra `view/STLREC` tras cada `B`/`U` (misma ruta que REDIAL; `REPINT=0` lo apaga). **Medido** (perfil `estado2`, sesión restaurada): el repintado del invitado corre (`OPENHOT view/STLREC`, `OPENVIEWDIAL = 3`), pero **`model/POWER` no se pide nunca** (37 222 llamadas a `viewManagerIf::getModelInfo` con `SETLOG=1`, 0 con ese modelo) y **el icono no se instancia** (trampas `TRACEFN2` en `+0x2758b8`, `+0x275530`, `+0x275804`, `+0x275524`, `+0x2c90c0`, `+0x2c91d4`: 0 disparos). Diff de contenido **0 px fuera de la banda animada** (`y<340`) en 8 comparaciones, incluido el control de reabrir con el mismo estado (859 px en la banda, más que `U 0`→`U 1`); opacos 0,080–0,092 | Cerrar cuando (1) exista instancia de `ACT_IconBattery` en la OSD del arnés y un `B 5` vs `B 100` cambie píxeles **fuera** de la banda animada (con captura y tabla); (2) el jack USB produzca la transición de `ModelUsb*`/`CmnViewNoHdmi` (`…USB_CONNECTING`) o se documente que la A6000 sólo lo consulta al activar la vista; (3) el modelo de `cargando` se compruebe en la cámara física | §9 de este informe · `scripts/gui/harness/shim/sonyshim.c` · `tests/test_g22_osd.py` |
| G22-OSD-REFRESCO | EN CURSO (28-11-2026) | **Repintado de la OSD al cambiar modo/batería/USB.** Lo del modo sigue cerrado en su efecto (REDIAL del invitado). Añadido 28-11: `B`/`U` ya disparan la misma reapertura del invitado (`REPINT`, por defecto activo; `REPINTROOT=1` añade `view/ROOT`), sin tocar `live.py` ni la página. **Medido**: la reapertura ocurre y **no cambia el contenido** (`y<340`: 0 px en todas las parejas batería/USB; el control de reabrir sin cambiar estado da 859 px sólo en la banda que parpadea). Conclusión: el repintado no era el eslabón que faltaba; falta el **consumidor** del estado (`ACT_IconBattery` no instanciado, `CheckerUSBAndClockReady` sólo decide) | Cerrar cuando (1) un cambio de batería o de jack cambie píxeles reales con la OSD poblada (no basta reabrir); (2) quede documentado qué vista/widget consume el estado en la cámara real | [informe](gui/g22-osd-refresco.md) · [§9](gui/g22-estado-camara.md) · `shim/sonyshim.c` |
