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
- **Pruebas.** `pytest tests/test_gui_harness.py` → 39 pasan, 8 saltan (las lentas con `A6000_HARNESS_RUN=1` y las que exigen CFW), con
  `A6000_HARNESS_WORK=/home/nicolas/a6000-arnes/analysis/gui/g22/harness` para que el test de compilación del shim tenga sysroot;
  `tests/test_live_shimenv.py tests/test_shim_logic.py tests/test_live_reintento.py` → 37 pasan. `ruff` limpio en lo tocado; `mypy` sin
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

## PARA PENDIENTES.md

| ID | Estado | Qué es | Criterio de cierre | Origen |
|---|---|---|---|---|
| G22-ESTADO-CAMARA | EN CURSO (26-11-2026) | **Batería, carga y USB del arnés (G22-E)**: modelo del anfitrión (`estado_camara.py` + sección `camara` del config) y dos órdenes LIVE nuevas del shim — `U <0\|1>` (jack USB como el driver de entrada: `{0x7000001, 0, estado, 0, 0x177}` a `0x7a0020`, la vía de §5.18w) y `B <0..100>` (palabra 3 de la respuesta emulada de CamMgr, `CAMGREMU`). Puntos `GET /camara/estado`, `GET /camara/`, `POST /camara/{bateria,usb,hdmi}`; enganche de dos líneas en `live.py`. **Medido**: el mensaje del jack llega y un hilo lo lee (`rcv_msg qid=0x7a0020`), pero **la pantalla no cambia** (0 px en 7 comparaciones, incluido el ruido); `B` no tiene consumidor (0 peticiones a `0x30001` en el perfil `estado`, av-cam tampoco contesta) y no hay icono de batería que cambie; HDMI solo modelo | Cerrar cuando (1) se identifique el modelo/vista que consume `0x3001` y el layout real de av-cam, de modo que un cambio de nivel se vea en la OSD o se demuestre que la A6000 no lo pinta con esos datos; (2) se compruebe en la cámara física qué produce el jack USB (icono de carga y/o «Modo USB», y si carga con la cámara encendida) y se refleje o se deseche `cargando = usb`; (3) haya orden verificada (o decisión explícita de no tenerla) para el jack HDMI | [G22-E estado de cámara](gui/g22-estado-camara.md) · `scripts/gui/harness/{estado_camara,camara_web}.py` · `shim/sonyshim.c` · `tests/test_gui_harness.py` |
