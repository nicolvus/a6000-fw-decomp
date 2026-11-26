# G22-CUELGUE — el cuelgue de la navegación: la UI deja de repintar («0 listas»)

**Estado (26-11-2026): REPRODUCIDO 4 de 4 tandas y ACOTADO al cierre del MENU; la espera concreta sigue
abierta. Descartada la inanición del anfitrión como causa (§3).** La secuencia de teclas de
abajo deja al invitado sin fotogramas nuevos entre la **pulsación 22 y la 38** (≈ 1,5–2,5 min de navegación
por el menú; 4 de 4 tandas): las teclas siguen llegando al hilo de entrada, el motor de presentación sigue girando y **la GPU deja de
recibir listas**. No hay SIGSEGV, ni aborto, ni cola descartada, ni cerrojo del cargador.

Se añadió lo necesario para medirlo sin mirar a ojo: `GET /estado` da `listas`/`listas_total` en números,
el conductor `secuencia_cuelgue.py` repite la secuencia y se para solo, `im.sh` admite `PMROUNDS` y
`PMFILTER` (volcados del grafo de espera que caben entre cuelgue y cuelgue) y con `TIDLOG=1` las líneas
reenviadas al anfitrión llevan el `tid` (antes había que adivinarlo). Pruebas: `tests/test_g22_hang.py`
(12, sin QEMU), incluidas las del veredicto PASS/CUELGUE/SIN-OSD.

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

1. **¿Qué variable separa los arranques que pintan de los que no?** En estas medidas **ninguna** (y la
   contención del anfitrión tampoco: ver §3, donde con 2 vCPU en vez de 8 se cuelga igual). El
   cuelgue salió con el `SHIMENV` de `live.py` sin `LIVE_QUITA` (perfil `hangkeys`, 38 pulsaciones) y en un
   arranque en frío sin teclas el invitado no se cuelga, se queda **ocioso** (sigue registrando
   `UpdateStatusMonitor` y el camino de entrada sigue vivo: en `hangbase`, sin teclas mías, llegó una
   tecla de otra sesión al mismo puerto y hubo copia a pantalla 10 s después). Las tres variables sospechosas no llegan a ejecutarse en esta traza:
   `RELOJEMU` no deja **ni una** línea `G22-FECHA` (ninguna vista pide `@M018`/`model/CLOCK`), `ZOOM` solo
   actúa sobre `IssueCommandAsync` con `0x7612/0x7614` (no hay ninguna) y `OPENVIEWDIAL` solo en la
   apertura en caliente `O view/STLREC`. El cuelgue es **intermitente y de carrera**, no de configuración.
2. **¿Termina solo?** No en la ventana medida: §5 restaura un estado guardado ya colgado y lo vigila
   8 minutos con teclas; sigue en `fotogramas: 1`, `0 listas`, alfa opaco 0,0046 y sordo a las flechas.
   En las tandas en vivo el invitado dejó de copiar a pantalla para siempre (70–90 s de margen tras la
   última pulsación) y su registro se apaga del todo ~48 s después de la última copia (§2).
3. **¿Qué hilo espera?** El que deja de escribir primero es el que despacha las vistas (destruye `07C` y
   no vuelve a tocar ninguna vista); el ciclo de presentación (`UpdateStatusMonitor` + vdf 1/3, que corre
   en hilos de `libObj`/`libosal_uipc`) sigue 48 s más y luego también para. La espera concreta no está
   capturada: no es `rcv_msg` (las colas contestan), ni `poll`/`sleep`, ni `pthread_cond_wait` (todas las
   de `Appframework` terminan); queda un cerrojo o una escritura bloqueante, que es lo que hay que
   capturar con `MUTEXWATCH` en el instante del cuelgue.

## 3. ¿Cuelgue del invitado o inanición del anfitrión? (A/B medido)

La duda planteada el 26-11-2026: cada `qemu-system-arm` es `-smp 8` en una máquina de 8 vCPU, así que dos
VMs ya compiten; con dos, el invitado tarda 240–380 s en pintar e incluso se queda en «0 listas» más de
500 s, y al matar la segunda VM un arranque de 108 s pintó de golpe. Si el cuelgue fuese solo eso, bajar
la presión del anfitrión lo quitaría. Medido con la misma rama y el mismo `.so` (el de `main`), perfil
nuevo en cada tanda y `SHIMEXTRA="FULLLOG=1 WAITLOG=3000"` — **sin `WLALL` ni `PMWAIT`**, para no cargar
al invitado con la propia instrumentación (la tanda anterior, `hangkeys`, los llevaba):

| perfil | vCPU del invitado | qemu en el sistema | 1.ª pantalla | pulsaciones hasta «0 listas» | fotogramas | listas | alfa opaco final | veredicto |
|---|---|---|---|---|---|---|---|---|
| `hangkeys` | 8 | 2–3 | 179 s | 38 (150 s de navegación) | 30 | 750 | 0,0046 | CUELGUE |
| `smp8` | 8 | 2 | 141 s | 31 (98 s) | 29 | 756 | 0,0046 | CUELGUE |
| `smp2` | **2** (`QEMU_SMP=2`) | 2 | 90 s | 22 (83 s) | 21 | 484 | 0,0046 | CUELGUE |
| `quita1` | 8, **sin `OPENVIEWDIAL`, sin `RELOJEMU` y con `NOZOOM=1`** | 2 | 131 s | 22 (127 s) | 16 | 285 | 0,0046 | CUELGUE |

Carga del anfitrión durante `smp8` y `smp2` (muestra cada 10 s de `/proc/<pid>/stat` y `/proc/loadavg`):
2 `qemu-system-arm`, loadavg 5–9 sobre 8 vCPU, 1,3–2,4 núcleos por VM.

**No es inanición del anfitrión.** Quitarle 6 de sus 8 vCPU al invitado *acelera* el arranque (141 → 90 s,
que es justo lo que hace la contención: alargarlo) pero **no evita el cuelgue**; se cuelga igual y antes en
pulsaciones porque cada vuelta del menú se recorre más rápido. Y las tres tandas se paran **en el mismo
fotograma**, que es lo que delata un fallo del invitado y no una simple falta de tiempo de CPU:

| pulsación | tecla | listas nuevas | alfa opaco | qué es |
|---|---|---|---|---|
| … | (menú abierto) | 28–39 cada una | **1,0** | el menú llena la pantalla (opaco) |
| 25 (`smp8`) / 16 (`smp2`) | menu (cerrar) | 30 / 39 | 1,0 | último fotograma bueno |
| 26 / 17 | derecha | **2** | **0,0046** | el menú ya no está y **la OSD de disparo no vuelve** |
| 27 / 18 | abajo | **0** | 0,0046 | ni una lista más |
| 28-31 / 19-22 | derecha, izquierda, abajo, Intro | 0 | 0,0046 | teclas que ya no responden |

El fotograma que sigue a cerrar el MENU lleva **2 listas** (el fondo y los dos iconos de estado) y alfa
opaco 0,0046: la composición de la pantalla de disparo no se rehace. A partir de ahí no llega ninguna lista
y la UI deja de responder, con el invitado todavía ejecutando su ciclo de presentación (§2). Si fuese
inanición, el invitado acabaría pintando tarde o temprano (el conductor espera 10 s por pulsación y luego
20 s más antes de la captura final: 70 s de margen en `smp8`, 90 s en `smp2`); no pinta.

Y las tres variables del shim que se sospechaban **no lo quitan**: en `quita1` se arranca con
`LIVE_QUITA=OPENVIEWDIAL,RELOJEMU` y `SHIMEXTRA="FULLLOG=1 WAITLOG=3000 NOZOOM=1"` y el cuelgue sale igual, en
el mismo fotograma (pulsación 22: `menu` deja 28 listas, la siguiente deja **2** y alfa 0,0046). Coherente
con lo que ya decía §2.3: en esta traza `RELOJEMU` no llega a ejecutarse (ni una línea `G22-FECHA`), `ZOOM`
solo actúa sobre `IssueCommandAsync` `0x7612/0x7614` y `OPENVIEWDIAL` solo en la apertura en caliente
`O view/STLREC`.

Lo que **sí** explica la contención es el otro síntoma, el de los arranques **sin teclas** (tus `menu5`/
`auto2`: «0 listas» durante 255–500 s): ahí el invitado no ha llegado a componer la pantalla de disparo y
solo compite por CPU, así que un arranque lento parece colgado. Son dos cosas distintas y esta página
separa la una de la otra: **navegar el menú cuelga la UI de forma reproducible** (4 de 4 tandas, mismo
fotograma), y **la contención solo alarga el arranque**.

## 4. Cambios en el arnés (instrumentación, no silencian nada)

- `live.py`: `GET /estado` añade `listas` (listas de GPU del último fotograma) y `listas_total`; el JSON se
  construye en `estado_json(vm)` para poder probarlo sin QEMU. **No se toca** `PAGINA` ni el HTML/JS.
- `secuencia_cuelgue.py`: conductor de la secuencia (pulsación + espera de fotograma + CSV + PNG antes y
  después + `resumen.json`), con `cuelga(historial, ventana)` como regla de parada y un **`veredicto`** con
  las dos medidas que hacen falta para la autoprueba: `PASS` (aguantó y alfa opaco ≥ `--min-opacos`, 0,05
  por defecto), `CUELGUE` (dejó de pintar) o `SIN-OSD` (pintó con la pantalla vacía). Códigos de salida:
  0 PASS · 1 CUELGUE · 2 SIN-OSD. Con `QEMU_SMP=2` se repite la tanda con menos vCPU (experimento de §3).
- `im.sh`: `PMROUNDS` (nº de volcados `PMWAIT`, por defecto 3 como antes) y `PMFILTER` (regex sobre `comm`:
  im.elf tiene ~300 hilos y leer `stat`/`wchan`/`syscall` de todos con procesos de busybox tarda minutos,
  así que el volcado no cabía entre dos cuelgues).
- `sonyshim.c`: con `TIDLOG=1`, las líneas que `WLALL` reenvía al anfitrión llevan el `tid` delante
  (antes cada línea se sabía de qué hilo era solo por el registro del invitado).

## 5. Límites

- La causa última (qué cerrojo/condición deja de llegar) queda **abierta**; lo cerrado es el eslabón
  visible: la UI deja de despachar acciones de vista después de cerrar el menú y la GPU se queda sin listas.
- `WLALL=1` cambia los tiempos (el invitado va 2–3× más lento) y el cuelgue aparece igual: también sin
  `WLALL` ni `PMWAIT` (§3, perfiles `smp8` y `smp2`), así que la instrumentación no lo provoca.
- Un estado guardado durante el cuelgue se restaura colgado (útil para reproducir y para medir la espera,
  inservible para seguir navegando): hay que borrar `estado.zst` del perfil antes de cada tanda. Restaurar
  exige el **mismo `SHIMEXTRA`** con el que se guardó; si no, `live.py` invalida el estado y arranca en frío.
- El rango de puertos 8660–8690 lo comparten las ramas: en una tanda llegó a mi VM una tecla de otra
  sesión (0x1f7). Las medidas de esta página se apoyan en el registro del invitado, no en el contador de
  teclas propio, así que la contaminación no cambia las conclusiones; aun así, conviene comprobar el
  puerto con `ss -tln` antes de arrancar.

## 5. ¿Se recupera solo? (estado colgado restaurado y vigilado 10 minutos)

Se guarda el estado de `smp8` justo después del cuelgue (`live/smp8/estado.zst`, 118 MiB) y se restaura en
un perfil nuevo (`hangrep`, puerto 8660) copiando `estado.zst`, `huella.txt`, `initrd.gz` y `nvram.json`
del mismo perfil y arrancando con el **mismo `SHIMEXTRA`** (si cambia, `live.py` invalida el estado y
arranca en frío). Restaurar tarda ~20 s frente a los 141 s del arranque en frío.

| t desde la restauración | fotogramas | listas | listas total | alfa opaco |
|---|---|---|---|---|
| 35 s | 1 | 0 | 0 | 0,0046 |
| 300 s | 1 | 0 | 0 | 0,0046 |
| 597 s (fin de la ventana de 600 s) | 1 | 0 | 0 | 0,0046 |

- **No se recupera**: 10 minutos sin un solo fotograma nuevo ni una lista.
- El registro del shim de esa sesión (`live/hangrep/shim.log`) solo trae el latido de siempre, sin errores:
  `WAITLOG … StlDateEvtLoop uipc7 id=0x12c032f tmo=60000 … tras 60001 ms` cada 60 s hasta el final
  (t=428 s del invitado): **el bucle de eventos de la OSAL sigue vivo y solo expira su temporizador**. El
  hilo que no vuelve no está en `uipc7`; es el que despacha las vistas.
- **Sigue sordo a las teclas**: una pulsación de `derecha` a los 92 s no produce fotograma (9 s de espera),
  y abrir la vista de disparo en caliente (`POST /linea` con `O view/STLREC`, la vía del shim que llama a
  `viewManagerIf::openView`) tampoco: 12 s sin fotograma nuevo.
- **No está bloqueado**: los 8 hilos `CPU n/TCG` del `qemu` siguen gastando CPU del anfitrión (medido sobre
  `/proc/<pid>/task/*/stat`, 6 s):

  ```
  54% CPU 0/TCG   49% CPU 3/TCG   43% CPU 1/TCG   33% CPU 2/TCG
  21% CPU 5/TCG   14% CPU 7/TCG   14% CPU 4/TCG   11% CPU 6/TCG   (245% de 800%)
  ```

  y el monitor de QEMU (`socat - UNIX-CONNECT:live/hangrep/mon.sock`, orden `info registers -a` — **sin
  `quit`**, que apaga la VM) pilla a los vCPU así:

  ```
  #0 ae6e0444 usr32   #1 c0ec2b4c svc32   #2..#7 c031cce8 svc32   (kernel, `bx lr`)
  #0 b6e04146 usr32   #3 b6e696cc usr32   #1, #2, #4..#7 c031cce8 svc32
  ```

  Es decir: el invitado **gira** (1–2 vCPU en espacio de usuario, el resto en el kernel, todos gastando
  anfitrión) pero la composición no avanza. Un interbloqueo clásico dejaría el proceso a ~0 y a los vCPU
  dormidos en `wfi`.

## 6. Cómo repetir la medida (5 min, sin tocar la visualización)

```sh
# 1) arranque en frío con perfil nuevo y puerto propio (8660-8690); SHIMEXTRA mínimo, sin WLALL ni PMWAIT
SHIMEXTRA="FULLLOG=1 WAITLOG=3000" \
  /home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir smpX --puerto 8660 &

# 2) en cuanto /estado dé fotogramas>0, conduce la secuencia: sale con veredicto y código 0/1/2
/home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/secuencia_cuelgue.py 8660 \
  --espera 10 --pausa 0.3 --ventana 5 --vueltas 40 --max-pulsaciones 300 --minutos 6 \
  --salida analysis/gui/g22/harness/live/smpX/cuelgue

# 3) variantes: QEMU_SMP=2 (menos vCPU) delante del paso 1; para medir carga del anfitrión, muestrear
#    /proc/loadavg y las ticks de /proc/<pid>/stat de cada qemu-system-arm cada 10 s.
curl -s -X POST http://127.0.0.1:8660/salir   # 4) cerrar y comprobar que no queda ningún qemu
```

## PARA PENDIENTES.md

| G22-CUELGUE | ABIERTO (26-11-2026) | **La UI deja de repintar al navegar el menú («0 listas»), reproducido 4 de 4 tandas en el mismo fotograma.** Secuencia: MENU · derecha · abajo · derecha · izquierda · abajo · Intro · MENU en bucle, 8 pulsaciones por vuelta ([`secuencia_cuelgue.py`](../../scripts/gui/harness/secuencia_cuelgue.py), `resumen.json` da `veredicto` PASS/CUELGUE/SIN-OSD con el alfa opaco). MEDIDO: perfil `hangkeys` 8 vCPU, `WLALL`+`PMWAIT` → cuelga a la pulsación **38**; perfil `smp8` 8 vCPU, instrumentación mínima (`SHIMEXTRA="FULLLOG=1 WAITLOG=3000"`) → **31**; perfil `smp2` **2 vCPU** (`QEMU_SMP=2`) → **22**; perfil `quita1` sin `OPENVIEWDIAL` ni `RELOJEMU` y con `NOZOOM=1` → **22**. En las cuatro, el último fotograma bueno es el de **cerrar el MENU** (30–39 listas, alfa opaco 1,0) y el siguiente trae **2 listas y alfa opaco 0,0046** (fondo + iconos): la pantalla de disparo **no se recompone** y después no llega ninguna lista más (las teclas siguen entrando a `I-InputRecv` y el ciclo de presentación sigue 48 s). **Descartada la inanición del anfitrión** (§3): bajar de 8 a 2 vCPU acelera el arranque (141 → 90 s) pero no evita el cuelgue; y `LIVE_QUITA=OPENVIEWDIAL,RELOJEMU` + `NOZOOM=1` tampoco (perfil `quita1`: cuelga a la pulsación 22, mismo fotograma). **No se recupera solo** (§5): estado guardado en el cuelgue, restaurado y vigilado 10 min → 1 fotograma, 0 listas, alfa 0,0046, sordo a las flechas y a abrir la vista en caliente, con los 8 hilos `CPU n/TCG` del `qemu` gastando 245 % (gira, no está bloqueado) y `StlDateEvtLoop uipc7` latiendo cada 60 s. Descartado además: cola de kernel descartada después de t=270, `dlv`/`mbx` llenos, SIGSEGV/abort, cerrojo del cargador y las colas `0x59000e`/`0x80003b`/`0x7a0020`/`0x8f0139` (responden todo el rato); `RELOJEMU` no deja ni una línea `G22-FECHA`, `ZOOM` solo actúa en `IssueCommandAsync` `0x7612/0x7614` y `OPENVIEWDIAL` solo en la apertura en caliente. Cierre: capturar con pila el hilo que deja de despachar vistas al destruir `07C` y que la secuencia aguante **300 pulsaciones o 5 min** con `veredicto: PASS` (alfa opaco ≥ 0,05). | [g22-cuelgue-navegacion](gui/g22-cuelgue-navegacion.md) |
| G22-CUELGUE-CONTENCION | MEDIDO (26-11-2026) | **La contención del anfitrión alarga el arranque, no es la causa del cuelgue.** Con 2 `qemu-system-arm` (`-smp 8` en 8 vCPU) el invitado tarda 141–380 s en la primera pantalla y puede quedarse en «0 listas» sin que se haya tocado una tecla (tus `menu5`/`auto2`: 255–500 s); **no** lo explica el cuelgue de la navegación, que se reproduce igual con 2 vCPU. Regla práctica: un `qemu` a la vez para medir tiempos de arranque, y `QEMU_SMP` menor solo si se van a solapar VMs (sirve para que arranque antes, no para evitar G22-CUELGUE). | [g22-cuelgue-navegacion §3](gui/g22-cuelgue-navegacion.md) |
| G22-CUELGUE-PROXY | ABIERTO (26-11-2026) | **Interbloqueo de la OSAL emulada con pila capturada**: con `MUTEXWATCH=5` el arranque en frío se queda en «esperando la primera pantalla» y el registro da `MUTEXWATCH im.elf (tid 212) espera cerrojo 0xb6e89730 > 5 s; dueño tid 221 (uipc_proxy_0)` con la pila del dueño: `libpthread+0xad5f` → `sonyshim.so+0x29954` (`issue_cmd`, `MWF::ObjIf::IssueCommandAsync`) → `sonyshim.so+0xa384` (bucle del proxy). Un **hilo proxy de la OSAL ejecuta un callback de la UI y se queda con un cerrojo del shim tomado**, mientras el hilo principal lo espera. Cierre: que los callbacks de la UI no puedan re-entrar en `issue_cmd` (o que el cerrojo no se tenga al llamar al callback) y que `MUTEXWATCH` deje de romper el arranque, para poder usarlo en caliente en G22-CUELGUE. | [g22-cuelgue-navegacion §2.2](gui/g22-cuelgue-navegacion.md) |

## 7. Sesión 27-11-2026: el cuelgue de arranque ahora se cura solo; 60 pulsaciones sin cuelgue de navegación

Dos medidas nuevas, con la receta que funciona hoy (`SD_MEDIA=1 SD_MEDIA_CAB=0`,
`SHIMEXTRA='INSHORT=1'`, **sin** `WLALL` ni trampas), perfil `nav1`, puerto 8686:

1. **El cuelgue de arranque es real y sigue ahí, pero ya no deja la sesión inservible.** El intento 1 se
   quedó en el fotograma de «2 listas» (0,0046 opacos) y el vigilante lo cortó a los 220 s
   (`LIVE_ARRANQUE_MAX`), **borró el `estado.zst` que el invitado había guardado a mitad de arranque** y
   arrancó en frío otra vez; el intento 2 llegó a la OSD (33 listas, 0,0877, 89 fotogramas). Antes de este
   cambio el reintento restauraba el estado colgado y repetía el cuelgue.
2. **La secuencia de navegación que colgaba no colgó.** `secuencia_cuelgue.py 8686 --max-pulsaciones 60`:
   **60 pulsaciones, 105,6 s, `cuelgue_en: null`, veredicto PASS**, latencia p50 1,03 s y máxima 3,55 s,
   fotogramas 94 → 189 y opacos 0,0908 → 1,0 (menú abierto al final). Evidencia en
   `reports/evidence/g22-cuelgue-nav60-20261127/`.

Lo que esto **no** dice: que el cuelgue esté resuelto. Sigue apareciendo en arranques en frío (1 de 3 en
esta sesión) y la causa última continúa abierta (§5). Lo que cambia es que el arnés se recupera solo y que
navegar 60 pulsaciones sin instrumentación no lo dispara.
