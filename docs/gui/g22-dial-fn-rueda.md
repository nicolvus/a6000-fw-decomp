# G22-DIAL-FN — dial de modos, Fn y rueda por la ruta real del firmware

**Estado: PARCIAL (medido).** El dial de modos **sí** llega al firmware por su camino real —el driver de entrada entrega la
posición y `InputService::callback_mode_dial` publica el evento `0x15070050` por `EventManager` (VERIFICADO con traza)—,
pero **ningún consumidor del arnés repinta el icono de modo a partir de ese evento**, así que el cambio visible se sigue
haciendo reabriendo la vista de disparo. Lo que **sí** se ha quitado del anfitrión es el *modo*: ahora lo da el firmware
(`CmnViewBigModelUtil::getRecViewFromDial`), la misma consulta que usa la cámara, en vez de una constante de `live.py`.
Fn y rueda funcionan y quedan medidos con captura.
**[G22-DIAL-POS] Las cuatro posiciones que faltaban están medidas** (§3.1): el firmware devuelve la posición tal cual, la
vista pinta indicador propio en película (8) y SCN (0xb) —se añaden a `POSICIONES_MODO`— y **no pinta nada** en MR (1) ni en
panorámica (0x10), que dan la misma captura byte a byte y quedan NO_VERIFICADO. Fn/rueda medidos control a control (§3.2).

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

### 3.1 Las cuatro posiciones que faltaban (G22-DIAL-POS, 26-11-2026)

Perfil `dialpos`, puerto 8661, arranque en frío (primera pantalla a los **142 s**; `KEYINIT key=0x7025 status=0x3 idx=0x27`,
pantalla `ca2b3e17…` con la «P»). Por cada posición, la misma orden: `K 7025 <pos> 27` (solo el evento del driver), captura,
`O view/ROOT 0` + `O view/STLREC` **sin argumento** (el modo lo da `OPENVIEWDIAL`) y dos capturas separadas 4 s (idénticas
las dos: la pantalla queda estable). El control es P (3): da la misma captura que el arranque.

| Posición | `OPENVIEWDIAL getRecViewFromDial()` | Captura (`docs/gui/img/`) | md5 / bytes | Qué pinta |
|---|---|---|---|---|
| `0x1` MR | **1** | `g22-dialpos-1-mr.png` | `cb0bd7f2…` / 12 061 B | **nada** en la esquina del modo; idéntica a `0x10` (0 px de diferencia) |
| `0x8` película | **8** | `g22-dialpos-8-pelicula.png` | `a157d367…` / 15 347 B | diseño de película (el resto de la OSD se recoloca); 2 201 px distintos de P |
| `0xb` SCN | **11** | `g22-dialpos-b-scn.png` | `d8c892c1…` / 17 964 B | icono de SCN en la esquina **y rótulo «SCN»** abajo; 3 189 px distintos de P |
| `0x10` panorámica | **16** | `g22-dialpos-10-panoramica.png` | `cb0bd7f2…` / 12 061 B | **nada**; idéntica a MR |
| `0x3` P (control) | **3** | `g22-dialpos-3-p.png` | `ca2b3e17…` / 12 861 B | letra «P» (igual que el arranque) |

- **El evento solo no cambia nada** en las cuatro (`dial-<pos>-1-evento.png` es la captura anterior en 4 de 4) y
  `TRACE 112040 n=1..5` confirma que `callback_mode_dial` corre en los cinco giros.
- **El valor que devuelve el firmware es la posición inyectada** (identidad, igual que §5.4): el modo no lo pone `live.py`.
- **Qué manda en el indicador: el argumento de `openView`, no `getExposureMode`.** Experimento cruzado, con las mismas
  órdenes (medido, capturas en `docs/gui/img/`):

  | dial (estado) | argumento de `O view/STLREC` | captura | resultado |
  |---|---|---|---|
  | `0x10` (panorámica) | `3` (P, explícito) | `g22-dialpos-arg-dial10-arg3.png` = `ca2b3e17…` | pantalla **P** con la letra «P» |
  | `3` (P) | `0x10` (panorámica, explícito) | `g22-dialpos-arg-dial3-arg10.png` = `cb0bd7f2…` | pantalla **sin indicador** |

  Es decir: la letra de la esquina sigue al número que recibe `openView`; `getExposureMode` (que lee el dial) no participa
  en esa decisión en el arnés. Refina §3 de este informe y §5.31: el número medido en el arranque (`OPENVIEWARG`) y el que
  da el firmware en caliente son el mismo, y es el que se pinta.

**Tabla estática del modo → icono** (`WrapperSettingUtil::getExposureMode`, `viewUnified2+0x18e454`; `movs r4,#icono`):

| estado del dial | rama | icono | consulta hija (parámetro del modelo) |
|---|---|---|---|
| `0x2` | `+0x18e46e cmp r4,#2` → `+0x18e7d2` | `0` | — |
| `0x1` MR | `+0x18e474` → ayuda `+0x18e324` | `7`/`8` → `0`; otro → `1`; consulta fallida → `1` | `0x01070a5e` |
| `0x3` P / `0x4` A / `0x5` S / `0x6` M | `+0x18e594/5a0/59a/5a6` | `0x15` / `0x17` / `0x16` / `0x18` | — |
| `0x8` película | `+0x18e5ae cmp r3,#8` → ayuda `+0x18e384` | `≤0` → `0x19`; `1` → `0x1a` | `0x0107010b` |
| `0x9` | `+0x18e5d0` → `+0x18e866` | `0x1a` | — |
| `0xb` SCN | `+0x18e4a2` → ayuda `+0x18e344` | sin escena → `3`; escena → `3,0x28–0x35,0x4–0xf` | `0x0107015e` |
| `0x10` panorámica | `+0x18e566` → ayuda `+0x18e364` (defecto `0x2b`) | `0x30` → `0x12`; `0x31` → `0x14`; si no → `0x10` | `0x0107099a` |
| `0x11` | `+0x18e49c` → `+0x18e7da` | `2` | — |

Las cuatro posiciones pendientes **tienen rama propia** (son códigos de modo reales), y sus iconos son `1`/`0` (MR),
`0x19`/`0x1a` (película), `3`/`0x28–0x35` (SCN) y `0x10`/`0x12`/`0x14` (panorámica): el despachador no las descarta. Lo que
difiere es lo que la **vista** pinta con esos números: en el invitado sólo se ven indicador para P/A/S/M y para SCN
(rótulo propio), y nada para MR y panorámica, que además dan exactamente la misma imagen.

**Decisión sobre `POSICIONES_MODO`** (`live.py`, ver §4): se añaden `("Película", 8)` y `("SCN", 0xb)` —la vista responde con
un diseño propio y, en SCN, con el rótulo «SCN» del firmware— al final de la tupla, para no mover los índices 0–4 que ya
usaban la página y `/modo`. **MR (1) y panorámica (0x10) quedan NO_VERIFICADO** y no se añaden: misma captura byte a byte
(`cb0bd7f2…`), sin indicador de modo, así que no se pueden distinguir entre sí ni comparar con la cámara.

### 3.2 Fn y rueda: qué mueve cada control (G22-DIAL-POS, 26-11-2026)

Con el menú Fn abierto (`Vn 030_viewUnified4.so`, `open(./viewFnMenu.uxc)`), capturas en `docs/gui/img/g22-dialpos-fn-*.png`:

| Acción | md5 / bytes | Qué hace |
|---|---|---|
| `Fn` | `77398585…` / 37 022 B (`g22-dialpos-fn-menu.png`) | abre el **menú rápido**: 12 ranuras (2 filas × 6), título de la ranura seleccionada y barra «⟳/▣ Cambiar ● Más MENU ↩». **Una sola página medida** (sin indicador de página) |
| `rueda_der` ×1 | `2b26671d…` / 48 047 B (`g22-dialpos-fn-rueda-entra.png`) | entra en **«Cambiar»**: se abre el carrusel de valor de la ranura |
| `rueda_der` ×2 | `eb3e8347…` / 49 266 B (`g22-dialpos-fn-rueda-valor.png`) | **mueve el valor** del carrusel (OFF → **70** → 75 → 80…) |
| `derecha` | `26b2535f…` / 33 380 B (`g22-dialpos-fn-derecha.png`) | cierra el carrusel y **cambia de ranura** (+2 por pulsación en lo medido: 2 → 4 → 6) |
| `abajo` | `43569653…` / 40 242 B (`g22-dialpos-fn-abajo.png`) | pasa a la **fila inferior** (ranura «Estilo creativo»); `arriba` vuelve |
| `dial_der` ×2 | `334c8019…` / 29 744 B (`g22-dialpos-fn-dialogo.png`) | abre el modal **«Función desactivada actualmente.»** sobre la ranura seleccionada (`Vn 011_viewUnified2.so`, CAUTION) |

El menú recuerda la ranura seleccionada entre aperturas y entre arranques: la segunda vez que se abrió en ese perfil salió
con «Modo de enfoque» (AF-S) marcado y la captura cambió de md5 (`41f1641d…`, 39 582 B) sin que cambiara el diseño.

- **El carrusel lo mueve la rueda** (`callback_dial_signed_speed`, `libObj+0x111c80`, ya medido en la fila 11). Las flechas
  cambian de ranura. El dial superior entra en «Cambiar» igual que la rueda (mismo modal sobre una ranura deshabilitada),
  pero **no se pudo medir que mueva el valor**: el modal es modal y bloquea el resto.
- El modal aparece en las ranuras que dependen de datos de la cámara («Modo de enfoque» AF-S, «Estilo creativo»): sin
  av-cam no hay valor que ofrecer. **Cerrarlo con el disparador deja la UI sorda a las teclas** (medido dos veces, dos
  arranques: después `Fn`/`MENU` no abren nada y el invitado sigue procesando mensajes), así que la captura necesita BIONZ.
- **`Fn` necesita pulsación y suelta (medido al abrir)**: el driver descarta el evento repetido (`TRAZA z … same event` en
  el registro) y, con `K 70a1 1 95` dos veces seguidas, la segunda no hace nada; con `K 70a1 0 95` (suelta) + `K 70a1 1 95`
  vuelve a abrir. La ventana manda **sólo la pulsación** (`pulsa`), así que un segundo Fn no cambia nada: **NO_VERIFICADO**
  que pulsación+suelta **cierre** el menú abierto (no se midió en ese estado; es el paso previo a tocar `pulsa`).
- **Registro real de la cámara**: `analysis/camera-dumps/mem-20261020-log/log.txt` (6 508 líneas, arranque del 20-10-2026)
  **no tiene ninguna pantalla de Fn**: sus únicas vistas son `Vn 080/011/088` y `Vn/Vd 08C/06F` (reproducción, aviso y
  USB), y no aparece el menú rápido ni sus páginas. §5.18z–z″ habla del menú principal, no del Fn. Por tanto **no
  hay evidencia de cámara con la que comparar el Fn**: lo de arriba es lo que hace el firmware de 3.21 en el invitado.

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

**G22-DIAL-POS — cambio mínimo de esta sesión.** Un solo hunk de datos en `live.py`, backend y sin tocar `PAGINA`/HTML/JS
(líneas 106–112, comentario + tupla; **no** hay ningún otro cambio de código):

- `POSICIONES_MODO` pasa a `(("Auto", 2), ("P", 3), ("A", 4), ("S", 5), ("M", 6), ("Película", 8), ("SCN", 0xB))`, con el
  comentario que dice qué se midió, qué queda NO_VERIFICADO (MR 1 y panorámica 0x10) y por qué.
- Se añaden **al final** para no mover los índices 0–4 que ya usaban la página (`__MODO0__` sigue siendo 1 = P) ni `/modo`.
- Tests: `tests/test_g22_dial_pos.py` (nuevo, 6 casos) y las dos aserciones que fijaban los cinco estados
  (`tests/test_g22_dial.py`, `tests/test_live_shimenv.py`).

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
- **G22-DIAL-POS (§3.1)**: `getRecViewFromDial` devuelve **la posición inyectada** también en `0x1` (1), `0x8` (8), `0xb`
  (11) y `0x10` (16), y la vista tinta pantallas **distintas** para 8 (`a157d367…`, diseño de película) y `0xb`
  (`d8c892c1…`, icono y rótulo «SCN»), sin indicador de modo para `0x1` y `0x10`, que dan la **misma** captura
  (`cb0bd7f2…`, 0 px de diferencia). El evento solo no cambia la pantalla en ninguna de las cuatro.
- **El indicador de modo sigue al argumento de `openView`, no al dial** (§3.1): dial `0x10` con argumento `3` → pantalla P;
  dial `3` con argumento `0x10` → pantalla sin indicador. Mismo md5 que las capturas anteriores en cada caso.
- **Fn y rueda (§3.2)**: Fn abre `viewUnified4` (`Vn 030`, `viewFnMenu.uxc`), una página de 12 ranuras; la rueda entra en
  «Cambiar» y mueve el carrusel de valor (OFF → 70 → 75 → 80); las flechas cambian de ranura (derecha +2, abajo a la fila
  inferior); el dial superior entra en «Cambiar» y, sobre ranuras sin datos de cámara, saca el modal «Función desactivada
  actualmente.» (`Vn 011`). Fn necesita **pulsación y suelta** (`K 70a1 0 95`): el driver descarta el evento repetido.
- **Cerrar ese modal con el disparador deja la UI sorda a las teclas** (dos arranques: después `Fn` y `MENU` no hacen nada
  y el invitado sigue procesando mensajes).

**INFERENCIA**
- El consumidor que falta es el widget/ACT de la pantalla de disparo que debería leer `getExposureMode()` al recibir
  `0x15070050` (existe `ACT_ExposureMode::cast` en `viewUnified2+0x2b6e2c`, sin llamadores directos localizados).
- En la cámara, la lectura del dial que cambia de pantalla es la de `getRecViewFromDial` (consulta a `InputService`), no el
  `Event` de `callback_mode_dial`: el evento avisa y la consulta es la que decide; en el arnés la consulta sólo ocurre al
  abrir la vista.
- Que en la cámara el argumento de `openView` sea el mismo número que devuelve `getRecViewFromDial` (en el arnés se cumple
  por construcción; es lo que explica que P/A/S/M y SCN salgan como en la cámara).
- Los iconos `1` (MR), `0x19`/`0x1a` (película) y `0x10`/`0x12`/`0x14` (panorámica) existen en la tabla de
  `getExposureMode`, pero la vista de disparo no pinta indicador con ellos en el invitado: o faltan recursos, o el número
  que pasa la cámara para esas posiciones no es el que se inyectó.

**NO_VERIFICADO**
- Que la cámara real repinte el icono con el evento del dial (no hay registro de una cámara con `TRACEFN`).
- El dial superior: entra en «Cambiar» como la rueda, pero **no se pudo medir que mueva el carrusel** (el modal bloquea el
  resto en las ranuras disponibles sin av-cam).
- **MR (1) y panorámica (0x10)**: devuelven su posición pero la vista no pinta indicador y las dos pantallas son idénticas;
  falta medir con cámara (o con av-cam) qué número pasa la cámara en esos dos topes. Por eso **no** están en `POSICIONES_MODO`.
- Si película (8) debe mostrar además el icono de modo en la esquina: aquí cambia el diseño pero la esquina queda vacía.
- `getExposureMode` llamado *en vivo* desde el invitado: se mide a través de `getRecViewFromDial` (que es su fuente), no
  llamando a `WrapperSettingUtil::getExposureMode` (no hay comando del shim para invocar símbolos de `viewUnified2`).
- Cambio de **página** del menú (`1 2 3 4 5 6`) con la rueda o el dial superior: en esta sesión sólo se midió el carrusel de
  valor del menú Fn (la rueda lo mueve; el dial superior no cambió nada), y el intento con el menú principal quedó sin
  medir porque la UI estaba sorda tras cerrar el modal (§3.2).
- Con av-cam (este árbol no tiene `av-cam.bin`): los valores de exposición y el resto de la OSD no se pintan, así que la
  pantalla medida está menos poblada que `g22-osd-iconos-poblados.png`.

## 6. Tests y calidad

- `pytest -q tests/test_g22_dial.py tests/test_live_shimenv.py` → **18 pasan, 3 saltan**; `tests/test_gui_harness.py` →
  **33 pasan, 9 saltan** (incluido `test_botones_y_diales_de_la_a6000_con_indices_del_driver`).
- **G22-DIAL-POS**: `pytest -q tests/test_g22_dial_pos.py tests/test_g22_dial.py tests/test_live_shimenv.py` → **25 pasan,
  2 saltan** (los saltos son los de siempre: firmware 3.21 extraído no disponible); con `tests/test_gui_harness.py` →
  **68 pasan, 13 saltan**. `tests/test_g22_dial_pos.py` es nuevo, 6 casos sin QEMU: posición que devuelve el firmware,
  coherencia de `POSICIONES_MODO` (con el criterio de capturas), índice de la página intacto, mapa de teclas de Fn/rueda/dial
  y bytes del despachador modo → icono (se mide contra el `viewUnified2.so` del arnés, no contra el firmware extraído).
- `ruff check` sobre lo tocado: sin avisos nuevos (quedan el `I001` previo de `live.py` y el `RUF100` previo de
  `tests/test_live_shimenv.py`, los dos ya estaban).
- El shim compila (`shim/build.sh`) con los mismos 5 avisos de antes. **No se tocó el shim en esta sesión.**

## 7. PARA PENDIENTES.md

```
| G22-DIAL-FN | PARCIAL (26-11-2026) | **Dial, Fn y rueda por la ruta real**: el dial llega a `InputService::callback_mode_dial` (`libObj+0x112040`, `TRACE 112040`) y publica `Event(0x15070050)` por `EventManager`→`AppSystem::dispatch`, pero nada repinta el icono con ese evento; el **modo ya lo da el firmware** con `getRecViewFromDial` (`viewUnified2+0x19f004`) mediante `OPENVIEWDIAL=1`, y `Vm.gira()` manda la tecla y reabre `view/ROOT`→`view/STLREC` sin modo (el atajo que queda es la reapertura). Fn abre el menú rápido (`viewUnified4`), la rueda mueve el carrusel (`libObj+0x111c80`); el dial superior entra en «Cambiar» pero no se midió que mueva el valor. Cierre: localizar el consumidor de `0x15070050` que repinta el icono (candidato `ACT_ExposureMode`, `viewUnified2+0x2b6e2c`) y retirar la reapertura. | [informe](gui/g22-dial-fn-rueda.md) · `tests/test_g22_dial.py` |
| G22-DIAL-POS | PARCIAL (26-11-2026) | **Posiciones pendientes del dial y menú Fn/rueda, medidos**: MR (1), película (8), SCN (0xb) y panorámica (0x10) devuelven **su posición tal cual** de `getRecViewFromDial` (`OPENVIEWDIAL getRecViewFromDial() = 1/8/11/16`) y la vista se abre con ese número. La pantalla es distinta por posición: película `a157d367…` (diseño de película) y SCN `d8c892c1…` (icono y rótulo «SCN», `Vn 088`); **MR y panorámica dan la MISMA captura byte a byte** (`cb0bd7f2…`, 0 px) y sin indicador de modo, así que quedan NO_VERIFICADO y **no** se añaden. `POSICIONES_MODO` pasa a Auto 2, P 3, A 4, S 5, M 6, **Película 8, SCN 0xb** (al final: índices 0–4 y `__MODO0__` intactos). Experimento cruzado: **el indicador sigue al argumento de `openView`, no al dial** (dial 0x10 + arg 3 → pantalla P; dial 3 + arg 0x10 → sin indicador). Tabla estática `getExposureMode` (`viewUnified2+0x18e454`): los cuatro modos tienen rama propia (iconos 1/0 MR, 0x19/0x1a película, 3 SCN sin escena, 0x10/0x12/0x14 panorámica). **Fn**: `viewUnified4`, 12 ranuras, una página; rueda = «Cambiar» + carrusel de valor (OFF→70→75→80); flechas = ranura (derecha +2, abajo a la fila inferior); dial = también «Cambiar», y en ranuras sin datos de cámara saca el modal «Función desactivada actualmente.» (`Vn 011`). Fn necesita **pulsación y suelta** (`K 70a1 0 95`): el driver descarta el evento repetido (`same event`); cerrar el modal con el disparador **deja la UI sorda a las teclas**. Evidencia: `docs/gui/g22-dial-fn-rueda.md` §3.1–§3.2, `docs/gui/img/g22-dialpos-*.png`, `tests/test_g22_dial_pos.py`. | Medir el dial superior **con el carrusel ya abierto** en una ranura con valores (p. ej. Cebra), en un arranque limpio y sin pasar por el modal; medir el **cambio de página** del menú principal con rueda y dial (aquí quedó sin medir por la UI sorda); confirmar si pulsación+suelta **cierra** el menú Fn (y entonces mandar la suelta en `pulsa`, que hoy manda sólo la pulsación); con cámara o av-cam, qué número pasa la cámara en MR y panorámica (los dos topes que no se distinguen aquí) y si película pinta icono de esquina. |
```

## 8. Cambios de esta sesión (para el registro)

**Sesión G22-DIAL-FN (26-11-2026):**
- `scripts/gui/harness/shim/sonyshim.c`: `lib_base()`, `modo_del_dial()`, `modo_caliente()` y `openhot` sin argumento.
- `scripts/gui/harness/live.py`: `gira()`/`reabre_vista()` sin modo + `OPENVIEWDIAL=1` + comentarios.
- `tests/test_g22_dial.py` (nuevo, 8 casos) y `tests/test_live_shimenv.py` (un caso actualizado).
- Capturas nuevas en `docs/gui/img/` (`g22-dial-*.png`).

**Sesión G22-DIAL-POS (26-11-2026, este cambio):**
- `scripts/gui/harness/live.py`: **un solo hunk de datos** (`POSICIONES_MODO` + su comentario, líneas 106–112). Nada más.
- `tests/test_g22_dial_pos.py` (nuevo, 6 casos sin QEMU); `tests/test_g22_dial.py` y `tests/test_live_shimenv.py` ajustan
  las dos aserciones que fijaban los cinco estados y el mapa estático (8 → `0x19`, 0xb → `3`).
- Capturas nuevas en `docs/gui/img/`: `g22-dialpos-{1-mr,8-pelicula,b-scn,10-panoramica,3-p}.png` (dial por posición),
  `g22-dialpos-arg-{dial10-arg3,dial3-arg10}.png` (experimento cruzado) y `g22-dialpos-fn-{menu,rueda-entra,rueda-valor,
  derecha,abajo,dialogo}.png` (menú Fn y sus controles).
- No se tocaron `PAGINA`, el HTML/JS de `live.py`, `isp_web.py`, `sensor_web.py`, `sd_emu.py`, `sd_image.py` ni `captura.py`.
  No se regeneraron artefactos (ni shim ni `setup.sh`): los del worktree son los de `main`.
