# G22-DIAL-FN — dial de modos, Fn y rueda por la ruta real del firmware

**Estado: PARCIAL (medido).** El dial de modos **sí** llega al firmware por su camino real —el driver de entrada entrega la
posición y `InputService::callback_mode_dial` publica el evento `0x15070050` por `EventManager` (VERIFICADO con traza)—,
pero **ningún consumidor del arnés repinta el icono de modo a partir de ese evento**, así que el cambio visible se sigue
haciendo reabriendo la vista de disparo. Lo que **sí** se ha quitado del anfitrión es el *modo*: ahora lo da el firmware
(`CmnViewBigModelUtil::getRecViewFromDial`), la misma consulta que usa la cámara, en vez de una constante de `live.py`.
Fn y rueda funcionan y quedan medidos con captura.

## 1. Cómo se midió

Perfil `dial`, puerto 8611, sesión del 26-11-2026, arranques en frío (sin av-cam: no hay `unicorn`+`av-cam.bin` en este
árbol). Órdenes (todas por HTTP, sin tocar la visualización):

```sh
SHIMEXTRA='WAITLOG=999999999 WLALL=1 TRACEFN=112040 TRACEREP=1 TRACEMAX=4' \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir dial --puerto 8611
curl -s -X POST localhost:8611/linea  -d 'K 7025 6 27'      # solo el evento real del dial (M)
curl -s -X POST localhost:8611/linea  -d 'P 10a8c3d 4'      # globales del dial en libObj (.bss)
curl -s -X POST localhost:8611/linea  -d 'F 1133e0 7025 0'  # InputService::setPhysicalKeyInh(0x7025,0) = liberar
curl -s -X POST localhost:8611/modo   -d '{"p":4}'          # P, A, S, M, Auto por el camino del arnés
curl -s -X POST localhost:8611/tecla  -d '{"k":"fn","v":1}' # Fn, MENU, DISP, rueda, dial superior
curl -s -N localhost:8611/eventos                           # capturas PNG (POST /refrescar antes de cada una)
```

Capturas: `docs/gui/img/g22-dial-*.png`. Log en vivo del shim: `analysis/gui/g22/harness/live/dial/shim.log` (`WLALL=1`; copia de la
sesión de Fn/rueda en `…/live/dial/shim-fn-rueda.log`, ambos en `analysis/`, ignorado por git). Las filas 9–12 se repitieron con el build
final y las filas 5–8 son la ronda de los cinco modos.

## 2. El camino real del dial (estático; REA no cubre estas Thumb, capstone sobre los binarios del arnés)

Binarios: `libObj.so` md5 `eb12512e6b74a940f1ae6de1c38477db`, `viewUnified2.so` md5 `1adc83954cfad8b17ff2e7199090f923`
(fw 3.21 de `analysis/gui/g22/harness/stage/cam/usr/lib`). Direcciones = VA = desplazamiento en el fichero.

1. **Mensaje del driver.** Cola `0x7a0020`, hilo `I-InputMain`, receptor `libObj+0x806f88`: copia 0x18 B a `[sp+0xdc]`
   — `+0xdc` = `w0` clave, `+0xe4` = `w2` valor, `+0xe8` = `w3`, `+0xec` = `w4` índice físico (`+0x807044: cmp.w r8,#0` /
   `+0x807048 bge` descarta los negativos), `+0xf0` = `w5` banderas (`+0x807072: tst.w sb,#1` compara 0x10 B con la tabla
   física y filtra repeticiones). El estado se guarda en la entrada de la lista (`+0x8071a2: str r3,[r5,#0x14]`, tras
   `+0x807164 bl 0x806eee`) y luego se avisa a los oyentes registrados. El shim mete exactamente ese formato
   (`sonyshim.c: live_keys`, `mbx_post_raw(0x7a0020, m)`).
2. **`InputService::callback_mode_dial(int, _InfraInputEvent*)`** — `libObj+0x112040`, 0x15c B:
   - `+0x112066: ldrb r3,[r3]` + `+0x112068: cbz r3` = indicador «dial inhibido» (`0x10a8c3d`). Si está a 1, la rama
     inhibida **retiene** el evento: `+0x112074/+0x112078` copian 0x18 B a `0x10a8c14` y `+0x112088: strb r2,[r3]` pone el
     pendiente (`0x10a8ccc`); no publica nada.
   - Rama normal: `+0x112098: blx createEvent` (`InputService::createEvent(id=w0, 4)`, `libObj+0x1106b8` =
     `new Event(id, 4, 1)`: el tercer byte es `dest`); tres `Param<int>` (constructor `0xf0fb0`) con `w2`/`w3`/`w4`;
     `+0x1120e2/+0x1120f0/+0x1120fa: addParameter(0x1b|0x1c|0x20, …)`; `+0x112104: pushFilterEvent`.
3. **`InputService::pushFilterEvent`** — `libObj+0x1117f4`: encola en `this+0xc` y drena; `+0x11183c: bl 0x127bb6` →
   `[this+4]` → `b.w 0xdf270` = `EventManager::push(Event*, false)`; `+0x111852: 0x127bc4` señaliza al salir.
4. **Reparto.** `AppSystem::dispatch` — `libObj+0x7eed0c`: `+0x7eed3c getId`, `+0x7eed78 getDest`; `dest&1` →
   `+0x7eee2a: bl 0x7f4c30(app+8, ev)` (vista), `dest&2` → `+0x7eedf0: 0x7ed49c`, `dest&4` → `+0x7eedaa: 0x7f4528`. Los
   eventos de `InputService::createEvent` llevan `dest=1` (`+0x1106ca: movs r3,#1`), **la misma vía que Fn, DISP y MENU**.
5. **De dónde sale el modo.** `CmnViewBigModelUtil::getRecViewFromDial()` — `viewUnified2+0x19f004`: si el Backup
   `0x15040040` vale 1 o 2 (`+0x19f00e`/`+0x19f01a: bl 0x19ef64` + `cmp`) devuelve el guardado; si no, **consulta**
   `+0x19f088: blx 0xe949c` = `InputService::getInputEventStatus(ParamList*, &resp)` (`libObj+0x114104`), guarda la
   respuesta en `this+0x714` (`+0x19f0b8`), la pasa por la conversión identidad `0x2441f4` (`+0x19f0c8`) y la devuelve
   (`+0x19f0e6: ldr r0,[r4,#0x714]`). `InputService::getInputEventStatus` lee el estado con `ParamList::get`, lo contrasta
   con `0x113d60` y, si **cambió** (`+0x1141c2: cmp r0,r4`), avisa con `+0x1141e2: bl 0x7edcc6`.
6. **El estado del dial en crudo.** `InfraInput::GetEventStatus(int dev, int idx, _InfraInputEvent*)` — `libObj+0x805804`:
   devuelve `[entrada+0x14]` (`+0x8058ae: ldr r5,[r6,#0x14]`) o `0x80000000` si `[this+0x20]`; la entrada la busca
   `0x8057c0` recorriendo la lista. Es lo que rellena el mensaje del driver del punto 1 (y por eso `KEYINIT` del arnés
   cambia el modo al arrancar).
7. **Modo → icono.** `WrapperSettingUtil::getExposureMode(ViewBaseProduct*)` — `viewUnified2+0x18e454`: `+0x18e460: bl 0x18e2da`
   = `getInstance()` (`+0x18e2e4: blx 0xe6acc`) + `getRecViewFromDial()` (`+0x18e2e8: blx 0xe5a6c`); el byte obtenido se mapea:
   `<0` → `+0x18e7ce: movs r4,#0x36` (desconocido), `2` → `+0x18e7d2: movs r4,#0` (AUTO), **`3` → `+0x18e594: cmp r4,#3` /
   `+0x18e596: beq.w 0x18e852` / `+0x18e852: movs r4,#0x15` (P)**, `4` → `+0x18e85a: movs r4,#0x17` (A), `5` →
   `+0x18e856: movs r4,#0x16` (S), `6` → `+0x18e85e: movs r4,#0x18` (M).
8. **Inhibición (mecanismo del firmware).** `InputService::setPhysicalKeyInh(int, bool)` — `libObj+0x1133e0`: `+0x1133f2:
   movw r3,#0x7025` / `cmp` → `+0x1133fc: bl 0x113280` (`setModeDialKeyInh`); `0x7026` → `0x113120`; el resto →
   `InfraInput::SetKeyInh` (`0x805b04`). `setModeDialKeyInh` (`libObj+0x113280`) con `inh=0` y evento pendiente lo
   **reproduce** por la vía real (`+0x11331c..+0x113344`: `createEvent` + `0x1b/0x1c/0x20` + `pushFilterEvent`).
9. **Rueda y dial superior.** `InputService::callback_dial_signed_speed` — `libObj+0x111c80`: `+0x111c8c: ldr r3,[r1,#8]`
   (paso) y `+0x111c90: cbz`/`beq` (paso 0 = no se emite nada); `+0x111cb0: adds r1,#0xa` (horario) / `+0x111cb4: adds r1,#0xb`
   (antihorario) → evento `w0+0xa`/`w0+0xb` (`0x15070040` → `0x1507004a/4b`); parámetros `0x1b` = |paso|, `0x1c` =
   `max(w3,0)` (`+0x111ce6: bic`), `0x20` = `w4`; `+0x111d34: b pushFilterEvent`. Misma vía que el dial de modo.
10. **Tabla clave → evento de la vista** (`viewUnified2+0x4a27d8`, entradas de 12 B `{clave, evento, 0x7ffffffe}`):
    `0x4a28d8` = `{0x00007025, 0x15070050}` (dial de modo), `0x4a281c/0x4a2824` = dial superior `0x10000014` →
    `0x15070030`, `0x4a2828/0x4a2834` = rueda `0x10000015` → `0x15070040`.
11. **Fn**: clave `0x70a1` → evento `0x15010120` (tabla de `libScalarDaemon`, T7 §1–2), misma cadena
    `InputService` → `Event(dest 1)` → vista.

## 3. Lo medido

Sesión final (shim con `OPENVIEWDIAL`), perfil `dial`, puerto 8611. Arranque en frío: **primera pantalla a los 146 s**
(`consola`/`shim.log`); con la máquina cargada (4 VMs de otros agentes) hubo que reintentar una vez.

| # | Acción | Evidencia (`live/dial/shim.log`) | Captura | Resultado |
|---|---|---|---|---|
| 1 | arranque en frío | `OPENVIEW view/ROOT -> 0`; `KEYINIT key=0x7025 status=0x3 idx=0x27`; `OPENVIEW view/STLREC -> 32727464`; `TRACE 113280 n=1 r0=0 r1=7025` (la vista libera la inhibición al abrirse) | `g22-dial-1-arranque-p.png` | pantalla de disparo con icono **P** (modo 3 del `OPENVIEWARG` medido) |
| 2 | `K 7025 6 27` — **solo** el evento del dial, sin reabrir | `TRACE 112040 n=1 r0=a r1=5effed34 … lr=ae74032b` | (idéntica byte a byte a la 1: md5 `ca2b3e17…`) | `callback_mode_dial` **corre** y el icono **no cambia** |
| 3 | `P 10a8c3d 4` antes y después del giro | `P libObj+0x10a8c3d: 00000000` en los dos casos | — | el dial **no estaba inhibido**; no hay evento retenido |
| 4 | `F 1133e0 7025 0` (liberar) | `TRACE 1133e0 n=1 r0=7025 r1=0`; `TRACE 113280 n=2 r0=0`; `F -> 0x1` | (idéntica a la 1) | la liberación es un **no-op**: no había nada retenido |
| 5 | `/modo {"p":4}` (M) | `TRACE 112040 n=1` y `OPENVIEWDIAL getRecViewFromDial() = 6` | `g22-dial-4-modo-m.png` | icono **M** |
| 6 | `/modo {"p":0}` (Auto) | `TRACE 112040 n=2`, `getRecViewFromDial() = 2` | `g22-dial-5-modo-auto.png` | sin letra (iAUTO+ no dibuja la letra en este diseño); pantalla distinta |
| 7 | `/modo {"p":1}` (P) | `TRACE 112040 n=3`, `= 3` | `g22-dial-6-modo-p.png` (md5 = el del arranque) | icono **P** |
| 8 | `/modo {"p":2}` (A) y `{"p":3}` (S) | `TRACE 112040 n=4`, `= 4`; `= 5` (`TRACEMAX=4`: la 5.ª traza no se imprime) | `g22-dial-7-modo-a.png`, `g22-dial-8-modo-s.png` | iconos **A** y **S** |
| 9 | `MENU` (y otra vez) | `Vn 07C_viewUnified2.so` (203,70 s); al repetir vuelve `ca2b3e17…` | `g22-dial-9-menu.png` (md5 `c0ba2f8c…`, 67 008 B) | menú completo: pestañas y «4»; la segunda pulsación lo cierra |
| 10 | `Fn` | `Vn 030_viewUnified4.so` (219,79 s) | `g22-dial-10-fn.png` (md5 `77398585…`, 37 022 B) | **menú rápido Fn**, mismo diseño que `g22-fn-menu-rapido.png` |
| 11 | `rueda_der` ×3 (con el menú Fn abierto) | `TRACE 111c80 n=1..3 r0=8 …` (73–76 s) | `g22-dial-11-rueda.png` (48 792 B) | entra en «Cambiar» y mueve el carrusel (OFF/75/**80**/85/90) |
| 12 | `dial_der` ×3 (dial superior) | `TRACE 111c80 n=4..6` (80–82 s): **sí** pasa por `callback_dial_signed_speed` | `g22-dial-12-dial-superior.png` (idéntica a la 11) | **sin cambio visible** en este estado |

Lectura de la tabla: el giro del dial de modo produce **dos** cosas en el invitado — el evento (fila 2, verificado, sin efecto
en pantalla) y la posición que el firmware guarda y devuelve al consultarlo (filas 5–8, que es lo que pinta el icono). Antes
de este cambio, ese número lo ponía `live.py`; ahora lo pone el firmware.

## 4. Cambio de código (mínimo)

1. `scripts/gui/harness/shim/sonyshim.c`
   - `modo_del_dial()`: llama a `CmnViewBigModelUtil::getInstance()` + `getRecViewFromDial()` (símbolo global y, si no está,
     por `/proc/self/maps` + `+0x19ba28` / `+0x19f004`). Es la consulta que hace la vista al abrirse en la cámara.
   - `modo_caliente(vista)`: con `OPENVIEWDIAL=1`, «`O view/STLREC`» **sin argumento** usa ese modo (rama de `openhot`).
   - El arranque (`openviewer`) sigue con `OPENVIEWARG`: a los `OPENVIEWAT=40 s` el dial aún no tiene estado (el `toActive`
     de `InputService` lo informa a ≈ 118 s).
2. `scripts/gui/harness/live.py` — **tres hunks, todos de backend** (`PAGINA`, HTML y JS intactos; `git diff a6c104ca --
   scripts/gui/harness/live.py`):
   - Hunk 1 (líneas 54–57, comentarios de `VISTA_REC`/`DIAL_INICIAL`): dice que el número es el del **arranque** y que en
     caliente lo da el firmware (`OPENVIEWDIAL`).
   - Hunk 2 (línea 62, `SHIMENV_BASE`): se añade un token, `OPENVIEWDIAL=1`; `OPENVIEWARG={VISTA_REC:x}` sigue igual.
   - Hunk 3 (`Vm.gira`/`Vm.reabre_vista`, líneas ~369–381): `gira()` manda la tecla del dial (`K 7025 …`) y lanza
     `reabre_vista()` **sin argumento**; `reabre_vista()` pierde el parámetro `estado` y envía `b"O view/STLREC\n"` en vez
     de `f"O view/STLREC {estado:x}\n"`. Docstring nuevo: qué hace el firmware y qué sigue siendo del arnés.
3. `tests/test_live_shimenv.py`: `test_giro_del_dial_…` pasa a exigir `b"O view/STLREC\n"` (sin número).
4. `tests/test_g22_dial.py` (nuevo): mapa tecla→mensaje, secuencia del giro, `SHIMENV`, que el shim pide el modo al firmware
   en caliente y no en el arranque, y (si hay firmware extraído) los bytes del mapa de `getExposureMode`.

**El atajo que queda** (declarado en el código): la **reapertura** `view/ROOT` → `view/STLREC` la sigue decidiendo el arnés.
No se puede retirar porque, medido, el evento del dial no repinta el icono: `callback_mode_dial` corre, el evento se publica
con `dest=1` (la vía de Fn/DISP/MENU, que sí funcionan) y aun así la pantalla no cambia. Falta el consumidor que en la cámara
repinta el icono de modo a partir de `0x15070050`; no está en `libObj` (la constante no aparece en ese binario) y en
`viewUnified2/4/5/6/8` sólo se localizan usos como tabla clave→evento y como clave de consulta del modelo, ninguno con
manejador asociado.

## 5. VERIFICADO / INFERENCIA / NO_VERIFICADO

**VERIFICADO (medido en el invitado)**
- El mensaje del shim (`K clave valor índice` → cola `0x7a0020`) es el del driver y `callback_mode_dial` (`libObj+0x112040`)
  se ejecuta con el giro del dial de modo.
- El dial **no** está inhibido en el arnés (`0x10a8c3d = 0` antes y después del giro) y la liberación
  (`setPhysicalKeyInh(0x7025,0)`) devuelve 1 sin efecto visible: no había evento retenido.
- El giro **no** cambia el icono de modo por sí mismo (capturas idénticas byte a byte).
- `MENU`, `Fn` (menú rápido `viewUnified4`), `rueda` (carrusel de valor) funcionan con captura;
  `callback_dial_signed_speed` (`libObj+0x111c80`) corre con la rueda.
- El modo con el que se abre la vista es el número que recibe `openView` y `getExposureMode`
  (`viewUnified2+0x18e454`) lo traduce 3 → P (`0x15`), 2 → AUTO (`0`), 4 → A (`0x17`), 5 → S (`0x16`), 6 → M (`0x18`).

**INFERENCIA**
- El consumidor que falta es el widget/ACT de la pantalla de disparo que debería leer `getExposureMode()` al recibir
  `0x15070050` (existe `ACT_ExposureMode::cast` en `viewUnified2+0x2b6e2c`, sin llamadores directos localizados).
- En la cámara, la lectura del dial que cambia de pantalla es la de `getRecViewFromDial` (consulta a `InputService`), no el
  `Event` de `callback_mode_dial`: el evento avisa y la consulta es la que decide; en el arnés la consulta sólo ocurre al
  abrir la vista.

**NO_VERIFICADO**
- Que la cámara real repinte el icono con el evento del dial (no hay registro de una cámara con `TRACEFN`).
- El dial superior: no se vio efecto en la pantalla de disparo ni en el carrusel abierto (sí comparte manejador con la rueda).
- Posiciones del dial distintas de 2/3/4/5/6 (MR, película, barrido, SCN, panorámica) y su icono.
- `getExposureMode` llamado *en vivo* desde el invitado: se mide a través de `getRecViewFromDial` (que es su fuente), no
  llamando a `WrapperSettingUtil::getExposureMode` (no hay comando del shim para invocar símbolos de `viewUnified2`).
- Cambio de **página** del menú (`1 2 3 4 5 6`) con la rueda o el dial superior: en esta sesión sólo se midió el carrusel de
  valor del menú Fn (la rueda lo mueve; el dial superior no cambió nada).
- Con av-cam (este árbol no tiene `av-cam.bin`): los valores de exposición y el resto de la OSD no se pintan, así que la
  pantalla medida está menos poblada que `g22-osd-iconos-poblados.png`.

## 6. Tests y calidad

- `pytest -q tests/test_g22_dial.py tests/test_live_shimenv.py` → **18 pasan, 3 saltan**; `tests/test_gui_harness.py` →
  **33 pasan, 9 saltan** (incluido `test_botones_y_diales_de_la_a6000_con_indices_del_driver`).
- `ruff check` sobre lo tocado: sin avisos nuevos (quedan el `I001` previo de `live.py` y el `RUF100` previo de
  `tests/test_live_shimenv.py`, los dos ya estaban).
- El shim compila (`shim/build.sh`) con los mismos 5 avisos de antes.

## 9. Seguimiento (27-11-2026): el repintado lo pide el invitado (G22-OSD-REFRESCO)

[G22-OSD-REFRESCO](g22-osd-refresco.md) cierra el «falta el consumidor» con estático: en `viewUnified2` **no hay** manejador del evento
`0x15070050` —los 12 sitios son consultas de `ParamList`/el estado del dial, y `ACT_ExposureMode::cast` (`+0x2b6e2c`) es un downcast por el
discriminador de la vtable (`+0x190`), no una acción de evento—; el icono se pinta al **activar** la vista y su dato es
`CmnViewModelWrpCameraExposureMode::getExposureModeActVal` (`+0x1c0eb4`: `getModelInfo("@M00B", 0xf, …)` → clave `0x12c`). Por eso el atajo
de la reapertura se sustituye por lo mismo **hecho por el invitado**: el shim (`REDIAL`, por defecto activo) vuelve a activar `view/STLREC`
sin modo al ver la tecla `0x7025`, y `Vm.gira()` ya solo manda la tecla. Medición y límites, en el informe nuevo.

## 7. PARA PENDIENTES.md

```
| G22-DIAL-FN | dial de modos, Fn y rueda por la ruta real | 26-11-2026 | PARCIAL: el dial llega a `InputService::callback_mode_dial` (`libObj+0x112040`, traza `TRACE 112040 n=1`) y publica `Event(0x15070050, dest=1)` por `EventManager`→`AppSystem::dispatch` (`libObj+0x7ef960`/`0x7eed0c`), pero **nada repinta el icono de modo** con ese evento (captura idéntica byte a byte); la tecla no está inhibida (`0x10a8c3d=0`) y liberarla (`setPhysicalKeyInh(0x7025,0)`) no cambia nada. El **modo ya no lo pone el anfitrión**: en caliente lo da el firmware con `CmnViewBigModelUtil::getRecViewFromDial` (`viewUnified2+0x19f004` → `InputService::getInputEventStatus`, `libObj+0x114104`), nueva variable `OPENVIEWDIAL=1` del shim; `Vm.gira()` manda la tecla y reabre `view/ROOT`→`view/STLREC` **sin** modo. El atajo que queda es sólo la reapertura (documentado en el código). Fn abre el menú rápido (`viewUnified4`) y la rueda mueve el carrusel de valor (`callback_dial_signed_speed`, `libObj+0x111c80`), con capturas; el dial superior no muestra efecto. Evidencia: `docs/gui/g22-dial-fn-rueda.md`, `docs/gui/img/g22-dial-*.png`. | Falta el consumidor del evento `0x15070050` que repinta el icono (candidato: `ACT_ExposureMode`, `viewUnified2+0x2b6e2c`, sin llamadores localizados); con él, retirar la reapertura. Medir con av-cam y con las posiciones MR/película/barrido/SCN. |
```

## 8. Cambios de esta sesión (para el registro)

- `scripts/gui/harness/shim/sonyshim.c`: `lib_base()`, `modo_del_dial()`, `modo_caliente()` y `openhot` sin argumento.
- `scripts/gui/harness/live.py`: `gira()`/`reabre_vista()` sin modo + `OPENVIEWDIAL=1` + comentarios.
- `tests/test_g22_dial.py` (nuevo, 8 casos) y `tests/test_live_shimenv.py` (un caso actualizado).
- Capturas nuevas en `docs/gui/img/` (`g22-dial-*.png`).
- No se tocaron `PAGINA` ni el HTML/JS de `live.py`, ni `isp_web.py`, `sensor_web.py`, `sd_emu.py`, `sd_image.py`, `captura.py`.
