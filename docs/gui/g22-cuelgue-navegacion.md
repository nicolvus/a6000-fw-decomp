# G22-CUELGUE — el cuelgue de la navegación: la UI deja de repintar («0 listas»)

**Estado (26-11-2026): REPRODUCIDO y ACOTADO a un hilo; causa última abierta.** La secuencia de teclas de
abajo deja al invitado sin fotogramas nuevos a las **38 pulsaciones** (≈ 2,5 min de navegación por el menú):
las teclas siguen llegando al hilo de entrada, el motor de presentación sigue girando y **la GPU deja de
recibir listas**. No hay SIGSEGV, ni aborto, ni cola descartada, ni cerrojo del cargador.

Se añadió lo necesario para medirlo sin mirar a ojo: `GET /estado` da `listas`/`listas_total` en números,
el conductor `secuencia_cuelgue.py` repite la secuencia y se para solo, `im.sh` admite `PMROUNDS` y
`PMFILTER` (volcados del grafo de espera que caben entre cuelgue y cuelgue) y con `TIDLOG=1` las líneas
reenviadas al anfitrión llevan el `tid` (antes había que adivinarlo). Pruebas: `tests/test_g22_hang.py`
(9, sin QEMU).

## 1. Reproducción (perfil propio, puerto propio)

Perfil `hangkeys`, puerto 8660, arranque **en frío** (primera pantalla a los 179 s), `SHIMEXTRA`:

```
FULLLOG=1 WAITLOG=3000 WAITINF=1 WLALL=1 PMWAIT=140 PMEVERY=25 PMROUNDS=10
```

Secuencia (una vuelta = 8 pulsaciones, se repite hasta el cuelgue): **MENU · derecha · abajo · derecha ·
izquierda · abajo · Intro · MENU**. `secuencia_cuelgue.py` pulsa y suelta (`v=1`, `v=0`), espera hasta 6 s
a que llegue un fotograma nuevo y cuenta la pulsación como «sin respuesta» si no llega ninguno.

| # | tecla | s | fotogramas | listas nuevas | listas total |
|---|---|---|---|---|---|
| 1 | menu | 10,6 | 3 | 2 | 2 |
| 2 | derecha | 14,3 | 4 | 20 | 22 |
| … | … | … | … | 28–39 por pulsación | … |
| 24 | menu | 69,4 | 26 | 32 | 678 |
| 25 | menu | 72,4 | 27 | 37 | 715 |
| 26 | derecha | 78,8 | 27 | **0** | 715 |
| 27 | abajo | 84,2 | 28 | **2** | 717 |
| 28–31 | derecha, izquierda, abajo, Intro | 90–110 | 28 | **0** | 717 |
| 32 | menu | 114,0 | 29 | 31 | 748 |
| 33 | menu | 118,6 | 30 | **2** | 750 |
| 34–38 | derecha, abajo, derecha, izquierda, abajo | 125–151 | 30 | **0** | 750 |

- `/estado` **antes**: `{"fotogramas": 1, "listas": 0, "listas_total": 0}` (primera pantalla).
- `/estado` **después**: `{"fotogramas": 30, "listas_total": 750, "último: 0 listas · dibujo 0 ms · copias 0 ms"}`.
- **Alfa opaco** del último fotograma: **0,0046** (medido sobre el PNG, canal alfa ≠ 0). Una OSD de disparo
  sana ronda **0,09**: es la métrica con la que se distingue «pantalla vacía» de «OSD pintada» sin mirar la
  imagen, y la que conviene usar como criterio de PASS en la autoprueba (`/estado` la da en `opacos`).
- Último fotograma bueno y último fotograma tras 5 pulsaciones sin respuesta: idénticos
  ([`img/g22-cuelgue-antes.png`](img/g22-cuelgue-antes.png)); el que se ve es el fondo con el icono de modo
  «P» y un icono de estado, **sin OSD ni menú**: la composición ya se había degradado antes del cuelgue.
- Registro completo: `analysis/gui/g22/harness/live/hangkeys/{shim.log,consola.log}` (ignorado por git) y
  `.../cuelgue/{pulsaciones.csv,resumen.json}`.

## 2. Qué hace el invitado mientras «no responde» (medido en `shim.log`)

| t del invitado | Hecho |
|---|---|
| 269,16 | `Vn 00E` (BASE_MENU) + `Vo 0x20` → `Vn 07C` (SETTINGMENU) + `Vo 0x27`: el menú se abre |
| 269,6–270,7 | `open(./viewSettingMenu.uxc)`, `open(./LayoutMaster_Menu.uxc)` |
| 273,26 | **tecla MENU** (0x1ab) entregada a `0x7a0020` |
| 273,55–277,11 | `Vd 07C_viewUnified2.so` (cerrar el menú tarda 3,5 s) |
| **277,68** | **última copia a pantalla** (`copia a pantalla seq=…`) |
| 277,8 / 284,2 / 290,6 / 297,0 / 303,5 | teclas derecha/abajo/derecha/izquierda/abajo: **llegan a `I-InputRecv`** (`rcv_msg qid=0x7a0020 <- respuesta`) y el firmware deja trazas de que las procesa (`TRAZA … l # #`) |
| 277,1 → 325,8 | el ciclo de presentación **sigue** a ~100 Hz (`UpdateStatusMonitor … push/pop turn inc`, `vdf: petición 1/3 terminada → callback`) pero **no produce ni una lista nueva** |
| 325,8 | última línea del registro del invitado (`uipc sig_sem 0x830451`), después silencio total |

Es decir: **no es que la entrada se pierda** (las teclas llegan y se contestan), es que **no hay ni una
operación de vista después de `Vd 07C`**: no se vuelve a abrir 07C ni 00E, no se crea ninguna otra vista y
no se compone ningún fotograma. `Vd 00E` (BASE_MENU) tampoco llega nunca: el menú base queda abierto y
vacío, que es exactamente lo que se ve en la captura (fondo + dos iconos).

**Descartado en esta traza** (todo medido, no supuesto):

- Cola sin respuesta: ningún `snd_msg` a cola de kernel descartado después de t=270 (`descartado` solo
  aparece en el arranque: `0x7a0020`, `0x110027c`, `0x4015e`, `0x920021`, `0x5700f9`, `0x9c015b`, `0x5a0048`).
- `dlv`/`mbx` llenos y abortos: 0 casos; sin `SIGSEGV`/`ABORT`/`EXIT`.
- Esperas nuevas del hilo de la UI: `Appframework` no registra ninguna espera (`WAITLOG`) que no termine;
  sus `cond_wait` de 3,3–3,6 s son el latido normal del bucle de eventos.
- `0x59000e` (VDF), `0x80003b` (vdf del kernel), `0x7a0020` (entrada) y `0x8f0139/a` (trazas) responden
  durante todo el cuelgue.

Lo que **sí** queda localizado es el eslabón que falta: tras destruir `07C`, el hilo que despacha las
vistas no vuelve a ejecutar ninguna acción, y el hilo de presentación deja de recibir trabajo. La espera
concreta (cerrojo o condición) no se ha podido capturar todavía en el instante del cuelgue con
`MUTEXWATCH` — al activarlo, el arranque entra en un interbloqueo distinto y anterior (`im.elf` espera un
cerrojo de `sonyshim.so` que retiene `uipc_proxy_0` dentro de `issue_cmd`, `sonyshim.so+0x29954`), que es
una pista del mismo tipo de problema: **un callback entregado a un hilo proxy que no vuelve**.


### 2.1 Qué estaba haciendo la UI justo antes de pararse (t = 273,3–277,3)

El cierre del menú no es instantáneo: el hilo que despacha las vistas destruye `07C` y encadena la vuelta a
la pantalla de disparo. En esa ventana se ve, en orden:

```
273.55  Vd 07C_viewUnified2.so          (empieza la destrucción de la vista del menú)
273.56  Lc Layer / Lc Layout            (suelta capas y diseño del menú)
273.94  open(./master_camera.uxc)       (vuelve a cargar el diseño de la pantalla de disparo)
274.41  [CmnViewMgrSetSave] MAAJID      (guarda la posición del menú)
274.59  [ACT_IconFlashEmission] userWidgetUpdate   ×3
275.70  [ACT_ICONAFAREA] … GetModelInfo Fail / focusArea=0
276.44  [CmnViewNoHdmi] m_isHDMISupport =1
276.72  backup op=3 n=2 id=0 len=0 r=0 ausente  ×4   (lectura de Backup con id 0, inexistente)
276.80  [ViewStlRec] ActionEyeFocusOff / Eyefocus_On
277.10  Lc Layout  /  277.11  Vd 07C_viewUnified2.so     (destrucción terminada)
277.14… TRAZA … «b»                     (últimas líneas del firmware)
```

A partir de ahí el invitado solo escribe el ciclo de presentación (`UpdateStatusMonitor`, vdf) hasta
t=325,8. **No hay ni una operación de vista más**: ni `Vn`/`Vd`/`Vo`, ni `open(.*.uxc)`, ni una lista de
GPU. La vuelta a la pantalla de disparo se quedó a medias.

### 2.2 El interbloqueo que sí se pudo capturar con pila (al activar `MUTEXWATCH`)

`MUTEXWATCH=5` en un arranque en frío (perfil `hangtid`, mismo shim) cambia el cuelgue por otro **anterior**
y ahí sí hay pila (`shim.log`):

```
MUTEXWATCH im.elf (tid 212) espera cerrojo 0xb6e89730 > 5 s; dueño tid 221 (uipc_proxy_0)
--- pila (sig 10 tid 221 uipc_proxy_0):
  libpthread-2.11.2.so+0xd146    (espera de futex)
  libpthread-2.11.2.so+0xad5f    (pthread_mutex_lock, ruta lenta)
  sonyshim.so+0x29954            (issue_cmd: MWF::ObjIf::IssueCommandAsync, 0x28800–0x2a1cc)
  sonyshim.so+0xa384             (bucle del hilo proxy)
  libpthread-2.11.2.so+0xbdc
```

Es decir: **un hilo proxy de la OSAL (`uipc_proxy_0`) ejecuta un callback de la UI y, dentro de él, se
queda con un cerrojo de `sonyshim.so` tomado**; el hilo principal de `im.elf` lo espera y el arranque no
termina. Es el mismo patrón que deja la UI sin despachar acciones: los callbacks de la UI se ejecutan en
hilos proxy y pueden re-entrar en la propia UI. Con `MUTEXWATCH` puesto el interbloqueo sale casi siempre
en el arranque (2 de 2), así que **no sirve tal cual para cazar el de la navegación**; hay que cazarlo con
`MUTEXWATCH` pero arrancando sin él y activándolo en caliente — imposible con el diseño actual, porque
`mw_secs()` se cachea en el primer cerrojo del arranque.

### 2.3 Respuestas a las tres preguntas

1. **¿Qué variable separa los arranques que pintan de los que no?** En estas medidas **ninguna**: el
   cuelgue salió con el `SHIMENV` de `live.py` sin `LIVE_QUITA` (perfil `hangkeys`, 38 pulsaciones) y en un
   arranque en frío sin teclas el invitado no se cuelga, se queda **ocioso** (sigue registrando
   `UpdateStatusMonitor` y el camino de entrada sigue vivo: en `hangbase`, sin teclas mías, llegó una
   tecla de otra sesión al mismo puerto y hubo copia a pantalla 10 s después). Las tres variables sospechosas no llegan a ejecutarse en esta traza:
   `RELOJEMU` no deja **ni una** línea `G22-FECHA` (ninguna vista pide `@M018`/`model/CLOCK`), `ZOOM` solo
   actúa sobre `IssueCommandAsync` con `0x7612/0x7614` (no hay ninguna) y `OPENVIEWDIAL` solo en la
   apertura en caliente `O view/STLREC`. El cuelgue es **intermitente y de carrera**, no de configuración.
2. **¿Termina solo?** En la tanda medida, la UI no volvió a pintar en los 53 s que duró la ventana de
   observación (y el registro del invitado se apaga del todo a los 48 s de la última copia). Un estado
   guardado en el cuelgue se restaura colgado. Con los datos de `menu5` (255 s seguidos con 0 listas) el
   orden de magnitud es minutos, no segundos; **no se ha medido una ventana de 10 min**.
3. **¿Qué hilo espera?** El que deja de escribir primero es el que despacha las vistas (destruye `07C` y
   no vuelve a tocar ninguna vista); el ciclo de presentación (`UpdateStatusMonitor` + vdf 1/3, que corre
   en hilos de `libObj`/`libosal_uipc`) sigue 48 s más y luego también para. La espera concreta no está
   capturada: no es `rcv_msg` (las colas contestan), ni `poll`/`sleep`, ni `pthread_cond_wait` (todas las
   de `Appframework` terminan); queda un cerrojo o una escritura bloqueante, que es lo que hay que
   capturar con `MUTEXWATCH` en el instante del cuelgue.

## 3. Cambios en el arnés (instrumentación, no silencian nada)

- `live.py`: `GET /estado` añade `listas` (listas de GPU del último fotograma) y `listas_total`; el JSON se
  construye en `estado_json(vm)` para poder probarlo sin QEMU. **No se toca** `PAGINA` ni el HTML/JS.
- `secuencia_cuelgue.py`: conductor de la secuencia (pulsación + espera de fotograma + CSV + PNG antes y
  después + `resumen.json`), con `cuelga(historial, ventana)` como regla de parada.
- `im.sh`: `PMROUNDS` (nº de volcados `PMWAIT`, por defecto 3 como antes) y `PMFILTER` (regex sobre `comm`:
  im.elf tiene ~300 hilos y leer `stat`/`wchan`/`syscall` de todos con procesos de busybox tarda minutos,
  así que el volcado no cabía entre dos cuelgues).
- `sonyshim.c`: con `TIDLOG=1`, las líneas que `WLALL` reenvía al anfitrión llevan el `tid` delante
  (antes cada línea se sabía de qué hilo era solo por el registro del invitado).

## 4. Limites

- La causa última (qué cerrojo/condición deja de llegar) queda **abierta**; lo cerrado es el eslabón
  visible: la UI deja de despachar acciones de vista después de cerrar el menú y la GPU se queda sin listas.
- `WLALL=1` cambia los tiempos (el invitado va 2–3× más lento) y el cuelgue aparece igual; no se ha
  medido la secuencia sin `WLALL`.
- Un estado guardado durante el cuelgue se restaura colgado (útil para reproducir, inservible para seguir
  navegando): hay que borrar `estado.zst` del perfil antes de cada tanda.
- El rango de puertos 8660–8690 lo comparten las ramas: en una tanda llegó a mi VM una tecla de otra
  sesión (0x1f7). Las medidas de esta página se apoyan en el registro del invitado, no en el contador de
  teclas propio, así que la contaminación no cambia las conclusiones; aun así, conviene comprobar el
  puerto con `ss -tln` antes de arrancar.

## PARA PENDIENTES.md

| G22-CUELGUE | ABIERTO (26-11-2026) | **La UI deja de repintar al navegar el menú («0 listas»), reproducido con una secuencia fija.** Secuencia: MENU · derecha · abajo · derecha · izquierda · abajo · Intro · MENU en bucle, 8 pulsaciones por vuelta ([`secuencia_cuelgue.py`](../../scripts/gui/harness/secuencia_cuelgue.py)). MEDIDO (perfil `hangkeys`, puerto 8660, arranque en frío, `SHIMEXTRA="FULLLOG=1 WAITLOG=3000 WAITINF=1 WLALL=1 PMWAIT=140 PMEVERY=25"`): **cuelga a la pulsación 38** (2,5 min); hasta la 25 cada pulsación produce 1 fotograma con 16–39 listas de GPU; después, 5 pulsaciones seguidas sin fotograma. Las teclas **sí llegan** (`I-InputRecv`, `rcv_msg qid=0x7a0020`, t=284…303) y el firmware las procesa, pero tras `Vd 07C_viewUnified2.so` (cierre del menú, 3,5 s, t=273,6–277,1) **no hay ninguna operación de vista más** (ni `Vn/Vd/Vo`, ni `open(*.uxc)`, ni listas): 750 listas acumuladas y último fotograma con 2 listas y **alfa opaco 0,0046** (OSD sana ≈0,09). El ciclo de presentación (`UpdateStatusMonitor` + vdf 1/3) sigue 48 s y luego también para. Descartado: cola de kernel descartada después de t=270, `dlv`/`mbx` llenos, SIGSEGV/abort, cerrojo del cargador, y las colas `0x59000e`/`0x80003b`/`0x7a0020`/`0x8f0139` (responden todo el rato). Las variables recientes del shim no intervienen en esta traza: `RELOJEMU` no deja ni una línea `G22-FECHA`, `ZOOM` solo actúa en `IssueCommandAsync` `0x7612/0x7614` y `OPENVIEWDIAL` solo en la apertura en caliente. Cierre: capturar la espera concreta en el instante del cuelgue y que la secuencia aguante **300 pulsaciones o 5 min** con alfa opaco > 0,05 y sin `0 listas`. | [g22-cuelgue-navegacion](gui/g22-cuelgue-navegacion.md) |

| G22-CUELGUE-PROXY | ABIERTO (26-11-2026) | **Interbloqueo de la OSAL emulada con pila capturada**: con `MUTEXWATCH=5` el arranque en frío se queda en «esperando la primera pantalla» y el registro da `MUTEXWATCH im.elf (tid 212) espera cerrojo 0xb6e89730 > 5 s; dueño tid 221 (uipc_proxy_0)` con la pila del dueño: `libpthread+0xad5f` → `sonyshim.so+0x29954` (`issue_cmd`, `MWF::ObjIf::IssueCommandAsync`) → `sonyshim.so+0xa384` (bucle del proxy). Un **hilo proxy de la OSAL ejecuta un callback de la UI y se queda con un cerrojo del shim tomado**, mientras el hilo principal lo espera. Cierre: que los callbacks de la UI no puedan re-entrar en `issue_cmd` (o que el cerrojo no se tenga al llamar al callback) y que `MUTEXWATCH` deje de romper el arranque, para poder usarlo en caliente en G22-CUELGUE. | [g22-cuelgue-navegacion §2.2](gui/g22-cuelgue-navegacion.md) |
