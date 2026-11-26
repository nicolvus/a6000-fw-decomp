# FILM-PB-1 — estabilidad y repetibilidad del arnés (26-11-2026)

Estado: **un comando para arrancar (perfil limpio, instrumentación por entorno), catálogo de los fallos de
arranque que sí se midieron, regla de la trampa en entrada de función con chequeo estático y vigilante, y
verificación en seco con veredicto**. Nada de cámara, firmware ni NVRAM de la cámara; no se ha tocado ningún
fichero de otro subagente ni perfil ajeno (`live/` está en `.gitignore`). Código nuevo:
[`estable.sh`](../scripts/gui/harness/estable.sh) y
[`chequea_trampas.py`](../scripts/gui/harness/chequea_trampas.py); evidencia ejecutable y registros en
[evidence/film-pb-1-sub-arnes-estable-20261126/](evidence/film-pb-1-sub-arnes-estable-20261126/).

## 1. Un comando

```sh
cd <repo>
HOME=$HOME sh scripts/gui/harness/estable.sh <perfil> [live|seco|verifica|arma|limpia]
```

| modo | qué hace | cuánto tarda | qué deja |
|---|---|---|---|
| `live` (omisión) | `live.py`: pantalla en el navegador, canal LIVE (teclas, `POST /linea`, `/guardar`) | 2–3 min en frío, ≈7 s restaurando | `$W/live/<perfil>/{estado.zst,consola.log,shim.log,nvram.json,avcam.jsonl,initrd.gz,huella.txt}` |
| `seco` | `run.py` + `im.sh`, sin UI ni canal LIVE: la cadena de vistas y la línea `alive=… threads=… modulos=…` | WAIT + arranque | `last.log` (consola del invitado), `stdout.txt` |
| `verifica` | `seco` **sin instrumentar**, `WAIT=100` s del invitado, tope de pared de 172 s y veredicto | ≤ 3 min | ídem + el veredicto por pantalla (§4) |
| `arma <puerto> <línea>` | manda una línea al invitado (`E TRACEFN2=…`) con vigilante de 12 s | 15 s | — |
| `limpia` | borra del perfil `initrd.gz`, `estado.zst(.tmp)`, `consola/shim/last.log` (~200 MB) | instantáneo | `nvram.json` y `av-cam.bin` intactos |

Instrumentación (sólo por entorno, entra en `SHIMENV` del invitado — §5.41 de
[g22-avcam-puente](../docs/gui/g22-avcam-puente.md)): `TRACELIB=libmpr.so`,
`TRACEFN2=5bad00,6e8430,…` (VA del ELF relativas a la base de esa biblioteca), `TRACEFN=…` (libObj),
`TRACEDEREF=d0:0:7`, `TRACEREP=1`, `TRACEMAX=n`, `TRACEPEEK=…`; `SHIMEXTRA` para el resto (`WAITLOG=1000`,
`FULLLOG=1`, `SKIPFN`, …). `PUERTO` (8600), `WAIT` (130 s; 100 s en `verifica`), `TOPE` (600 s; 172 s en
`verifica`), `ESTABLE_WORK` (DIR_TRABAJO),
`INTENTOS`, `CHEQUEA`, `FUERZA`, `ESTABLE_REUSA`, `LIBDIR`.

Tres comprobaciones antes de gastar los 3 minutos del arranque, porque las tres se pagaron caras en esta
sesión: **(a) tarjeta** — el invitado ve `$HOME/A6000-SD` (`sd_emu.SD_DEFECTO`), así que con otro `HOME`
la tarjeta sale vacía y la enumeración no prueba nada: el script imprime `tarjeta: N clip(s) M foto(s)`;
**(b) largo del perfil** — QEMU exige rutas de socket UNIX < 108 B (`$W/live/<perfil>/ui.sock`), el perfil
`arnes-indice` murió con *«Unix socket path … is too long»*: el script lo calcula y aborta, y de ahí la
regla de nombres cortos (≤ 12 caracteres es seguro con el `ESTABLE_WORK` de fábrica, que deja 70 B de
margen); **(c) disco** — un arranque en frío escribe `initrd.gz` (93–117 MB) + `estado.zst` (≈117 MB) y
`run.py` construye otro initrd en `/tmp` (tmpfs, ~150 MB): aborta si quedan < 1200 MB en `$W` o < 400 MB en `/tmp`.

Estado de la tarjeta emulada hoy en esta máquina: **0 clip(s) y 3 foto(s)** (`~/A6000-SD/DCIM/100MSDCF/
DSC00001..3.JPG`). Para probar la enumeración de un clip hay que poner uno en la tarjeta que ve el invitado:
`~/A6000-SD/PRIVATE/M4ROOT/CLIP/C0001.MP4` (XAVC S, `sd_emu.ruta_clip`) o `~/A6000-SD/MP_ROOT/100ANV01/
MAH0xxxx.MP4` (AVCHD). Sin ese fichero el arnés puede ser perfecto y no enumerará nada: es un bloqueo
independiente del arranque, y el `0 clip(s)` de cada arranque lo delata en una línea.

Ejemplos exactos:

```sh
# UI instrumentada con trampas de libmpr en entradas de función, perfil nuevo (arranque en frío)
TRACELIB=libmpr.so TRACEFN2=5bad00,6e8430,6e80a4 TRACEDEREF=d0:0:7 TRACEREP=1 PUERTO=8631 \
  sh scripts/gui/harness/estable.sh pb1-1 live

# arranque seco instrumentado, con el registro completo del invitado extraído a guest.log
TRACELIB=libmpr.so TRACEFN2=5bad00 WAIT=150 SHIMEXTRA='FULLLOG=1' \
  ESTABLE_WORK=/home/nicolas/a6000-estable/work sh scripts/gui/harness/estable.sh pb1-2 seco

# verificación en seco (OK/NO, ≤ 3 min)
sh scripts/gui/harness/estable.sh pb1-3 verifica

# trampa en caliente sobre una VM `live` ya arrancada, con vigilante
sh scripts/gui/harness/estable.sh pb1-1 arma 8631 "E TRACEFN2=5bad00"
```

`ESTABLE_WORK` por omisión es `analysis/gui/g22/harness` (allí ya viven `vmlinuz` y `base.cpio.gz`). Si falta,
`sh scripts/gui/harness/setup.sh $W` (2 min, descarga 34 MB y compila el shim). Un DIR_TRABAJO propio
(`/home/nicolas/a6000-estable/work` en esta sesión) es lo que aísla de otros subagentes: mismo binario, sin
compartir `live/`.

## 2. El arranque: tiempos medidos y los fallos que de verdad aparecen

| # | modo | instrumentación | WAIT | pared | carga (1 min) | resultado |
|---|---|---|---|---|---|---|
| 1 | seco | ninguna | 150 s | **181 s** | ≈20 | `alive=207 threads=119 lineas=35161 modulos=91`; `OPENVIEW view/ROOT -> 0`, `Root Draw` |
| 2 | seco | 5×TRACEFN2+FULLLOG | 150 s | **≈277 s** | 27 | `alive=206 threads=119 lineas=28063 modulos=91`; `TRACELIB libmpr.so base 0xaeb1d000`; **0 impactos** |
| 3 | seco | 5×TRACEFN2+FULLLOG | 150 s | ≥200 s | 27 | **cortado por un tope de pared de 200 s** mío: sin resumen (no fue fallo del arnés) |
| 4 | live | TRACELIB | — | 460 s | 36 | **sin primera pantalla**; el invitado iba a **0,42×** (192 s propios en 461 s de pared); **sin `IMEXIT`**; el supervisor de `live.py` ya había matado y reiniciado un arranque a los 260 s |
| 5 | verifica (versión previa, `WAIT` 130→135) | ninguna | 135 s | **174 s** | 32.7 | `NO-CONCLUYENTE` (75): no murió, no llegó a la pantalla en el tope |
| 6 | verifica (final, `WAIT=100`) | ninguna | 100 s | **159 s** | 21 | **OK**: `alive=205 threads=119 modulos=91`, resumen a los 155 s |

De (1) y (2): el arranque en frío tarda **≈30 s con la máquina medio libre** (181 s − 150 de `WAIT` − cierre) y **≈130 s con carga 27**; el invitado va a
0,4–0,5× cuando hay 3–4 VM en paralelo (8 vCPU TCG por VM, 12 núcleos). Consecuencia práctica: **cualquier
plazo fijo se queda corto y el fallo que se ve es de plazo, no de código**.

Catálogo de lo que rompe un arranque (firma exacta en el registro y mitigación):

| fallo | firma | causa medida / documentada | mitigación |
|---|---|---|---|
| SEGV intermitente de arranque | `IMEXIT im_s 139` + `pila (sig 11)` antes de la primera pantalla | §5.41: 35–50 % por intento en frío antes de los atajos; 6/6 después | `live.py` ya reintenta (`LIVE_REINTENTOS=6`); `seco`/`verifica` reintentan aquí (`INTENTOS=2`) |
| «tercer arranque falla» | sin pantalla, **sin** `IMEXIT`, a veces `arranque N/M fallido a los 260 s` | **medido (4)**: el invitado va a 0,42× con carga 36 y `LIVE_ARRANQUE_MAX=260 s` se cumple → el supervisor mata el frío y repite (cada reintento **rehace** `initrd.gz`); a la tercera se percibe como fallo del arnés | `LIVE_ARRANQUE_MAX` y `WAIT` proporcionales a la carga (lo hace `estable.sh`); veredicto `NO-CONCLUYENTE` en vez de `NO` si carga > 12 |
| estado de 2.ª generación | restaurar peta o `estado.zst.tmp` huérfano | guardar desde una VM restaurada (`guardar()` al salir) y, según otro subagente, `live.py` puede morir al salir en `puente.desde_invitado` (`ValueError`) | `POST /guardar` **antes** de `/salir` (guardado atómico mientras la VM está sana); si hay duda, `limpia` → frío |
| ruta de socket > 107 B | `qemu-system-arm: -chardev socket,…: UNIX socket path '…' is too long` | medido en el perfil `arnes-indice`: su `ui.sock` mide **110 B** | preflight del largo + nombres de perfil cortos |
| sin disco | `No space left on device` en `initrd.gz`, `estado.zst` o el build de `/tmp` | 721 perfiles = **51 GB**; cada frío ≈210 MB en `$W` + ≈150 MB en `/tmp` | preflight de `df` + `limpia` |
| SIGTERM ajeno | `qemu-system-arm: terminating on signal 15 from pid N (<unknown process>)` a los 6 s | **medido**: un `pkill -f` de otro proceso/shell con patrón genérico mata qemus y arneses ajenos (me pasó a mí y a otra sesión) | lanzar con `setsid` y matar **por PID o grupo propio**, nunca `pkill -f` genérico; el registro de qemu dice el PID culpable |
| tarjeta vacía | el invitado no ve medios y la reproducción «no hace nada» | `HOME` distinto ⇒ `~/A6000-SD` no existe (medido por otro subagente) | aviso y `tarjeta: N clip(s)` en cada arranque |

## 3. Trampas: por qué sólo en entrada de función

`TRACEFN/TRACEFN2` escriben **UDF `0xde00`** en la dirección y se rearman borrando el UDF cuando salta la señal
(`sonyshim.c`, `trace_fns`/`on_trace`). Con `TRACEREP=1` dejan además **otro UDF en «la instrucción
siguiente»** (`pc+2`/`pc+4`) y lo restauran al pisarlo: eso presupone que `pc+2` **es** una instrucción y que
el flujo pasa por ella, es decir `pc` es la primera instrucción de una función. Fuera de una entrada:

- `pc+2` cae a media instrucción de 32 bits ⇒ el UDF queda donde nadie lo espera y el `SIGILL` no casa con
  ninguna entrada de la tabla ⇒ `signal(SIGILL, SIG_DFL)` ⇒ **`IMEXIT … 139`**. Medido por el equipo: armar
  fuera de una entrada mata `im.elf` (139); con 0x60c9ee/0x60c9f4 el arranque se quedó en 2 fotogramas.
- En código caliente cada impacto cuesta 2 `SIGILL` + escritura del registro: una trampa en un bucle
  interno satura el invitado y **parece un cuelgue** aunque no muera.
- `mprotect(pc & ~4095, 8192, …)` protege **dos** páginas: si `pc` cae en la última página de un segmento, la
  segunda no está mapeada y el `mprotect` falla entero, y el `store` del UDF iría a página de sólo lectura
  (inferencia leída en `trace_fns`, no reproducida).

Chequeo estático obligatorio antes de armar (`chequea_trampas.py`, 2 s: una pasada por `.text` para los
destinos de `bl` y búsqueda de punteros literales):

| desplazamiento | veredicto | por qué |
|---|---|---|
| `0x5bad00` mutex | **ENTRADA** | 809 `bl` (0x2ba768…) + prólogo `push.w` |
| `0x6e8430` ctor `mp4Ifo_If` | **ENTRADA** | 4 `bl` (0x67b598…) + `push.w` |
| `0x6e80a4` ctor `mp4Ifo_If` | **ENTRADA** | 2 `bl` + `push.w` |
| `0x61a8f0`, `0x608698` | **ENTRADA** | puntero en `.text` (0x8e6eb0/0x8e6f0c) + prólogo |
| `0x6e8432`, `0x6e8434`, `0x6e80a8` | **NO / DUDOSA** | media instrucción: sin `bl`, sin puntero (`0x6e8434` es el `sub sp` del prólogo de 0x6e8430) |
| `0x60c9ee`, `0x60c9f4` | **NO / DUDOSA** | los que otro subagente midió que cuelgan el arranque: el chequeo los rechaza solo |

`estable.sh` ejecuta el chequeo cuando hay `TRACEFN2` (en el arranque y antes de `arma`) y **no arranca** si
alguno no es `ENTRADA` (`FUERZA=1` lo salta, con el riesgo asumido). `arma` además vigila: mide fotogramas,
manda la línea, espera 12 s y dice `VM VIVA` o `VM CAÍDA` (entonces hay que mirar `consola.log`/`shim.log`).
Regla operativa: **de una en una, sólo entradas de función y preferir funciones frías** (máx. 32 trampas,
`ntrc < 32`).

**Instrumentación y modo.** En `seco` (sin av-cam) `TRACELIB=libmpr.so` resuelve la base pero **las 5
funciones no se ejecutan nunca en el arranque** (0 impactos en (2)): la cadena MPR sólo corre con el puente
av-cam ⇒ la instrumentación de `libmpr` exige `live` (con `av-cam.bin`+`liro.ko`, que aquí están). Además `WLALL=1` frena el arranque (medido por otro subagente); para ver los `TRACE` en `live` basta `FULLLOG=1`
(se vuelca al final, sin coste durante el arranque) o `WAITLOG=1000` (todo `efp` a `shim.log`, con coste).

## 4. Verificación en seco (OK/NO, ≤ 3 min)

```sh
sh scripts/gui/harness/estable.sh <perfil-nuevo> verifica      # 0 = OK · 1 = NO · 75 = NO-CONCLUYENTE
```

Corre `run.py` + `im.sh` con la cadena de la pantalla de disparo (`OPENVIEW=view/ROOT,view/STLREC`,
`POSTROOTEV`, `SDIMG=1`, `NULLMWF=1`, `SYNCWAIT=37807c:300`), **sin ninguna instrumentación** (se descartan
`TRACEFN*` a propósito), y decide con lo que el propio `im.sh` imprime:

- **OK**: hay `alive=<pid>` y `threads ≥ 60` y `modulos ≥ 60`, sin `IMEXIT`/`Segmentation fault`/`Aborted`.
  Referencia medida: `threads=119 modulos=91` en (1) y (2); el umbral 60/60 deja margen y sigue distinguiendo
  un arranque que no llegó (en (3), sin resumen).
- **NO**: muerte detectada o `threads`/`modulos` por debajo; reintenta una vez (`INTENTOS=2`) porque el SEGV de
  arranque es intermitente.
- **NO-CONCLUYENTE** (75): no murió pero la carga del anfitrión es > 12; el invitado no cabe en 3 min y un NO
  sería mentira. La salida imprime `carga` en todos los casos.

Parámetros: `WAIT = 100 s` **del invitado** (la cadena abre `view/STLREC` a los ≈67 s: las `CALMA` del arranque
suman 40+4+4+8+6,5+4,1) y `TOPE = 172 s` de pared. `WAIT` no crece con la carga —lo que no cabe es el tiempo
de pared, no la espera—; si el invitado va lento el veredicto es `NO-CONCLUYENTE`, nunca un NO falso.

**Medido en esta sesión** (máquina con 2–4 VM de otros subagentes): (6) **OK en 159 s con carga 21**; (1), el
mismo camino con `WAIT=150`, `threads=119 modulos=91` en **181 s** con carga ≈20; (5), con el diseño anterior
(`WAIT` 135) y carga 32,7, **NO-CONCLUYENTE en 174 s**. Para una pasada larga: `TOPE=600 sh … verifica`
(entonces ya no promete 3 min); para gastar menos núcleos, `QEMU_SMP=4`.

## 5. Perfiles: qué sirve para qué

`$W/live/<perfil>` (721 perfiles, **51 GB**, todo `gitignore`d). Un perfil es estado, no código: se reutiliza
sólo si tiene sentido su `estado.zst`/`nvram.json`.

| familia | ejemplos | para qué sirve | qué guarda |
|---|---|---|---|
| por omisión | `sony` | UI de referencia, ya con `estado.zst` de la pantalla de disparo | `estado.zst`+`initrd.gz`+`nvram.json` |
| casos documentados | `disparo`, `prueba`, `osd1`, `fecha`, `fecha0` | reproducir un hallazgo concreto (pantalla de disparo, menú, OSD, fecha/hora) | `estado.zst`, `nvram.json` del caso |
| E2E / objetivos | `e2e01…e2e184` | mediciones con av-cam y CFW (`--pkg`), capturas de `docs/gui/g75` | `avcam.jsonl`, `estado.zst` |
| arnés/arranque | `arnes1…arnes9`, `calma*`, `base*` | pruebas del propio arranque, esperas, reintentos | `estado.zst`, `shim.log` |
| scratch de sesión | `cNN…`, `tNN`, `medNN`, `gNN` | pruebas de un rato; **no** reutilizar | lo que salga |
| de esta sesión | `est1`, `ver1`, `arm-t1`, `arm-t2`, `pb1-ver`, `pb1-ver2` | las corridas de §2; **borrados** con `limpia` al terminar (quedan 0–2 MB) | el perfil, `last.log` |

Orden de uso que evita sorpresas: **perfil nuevo por tanda** (`estable.sh` lo exige), `live` para
instrumentar y para la UI, `seco`/`verifica` para medir el arranque sin UI, y `limpia` al terminar una tanda
(51 GB ya son un problema de disco, no de espacio «libre»).

## 6. Límites

- No he podido medir el ciclo de restauración (`live` frío → `estado.zst` → 3.er arranque restaurando)
  porque con carga 36 el frío no llegó a la primera pantalla en 460 s (4). Queda **NO_VERIFICADO** aquí; la
  recomendación de §2 (guardar antes de salir y no encadenar restauraciones) sale de la lectura de
  `live.py` (`GUARDA_MIN=190 s`, `huella.txt`, guardado atómico) y de lo medido por otro subagente
  (`ValueError` en `puente.desde_invitado` al salir).
- Los 5 desplazamientos de §3 siguen armándose igual: el chequeo dice «es entrada de función», no «es útil».
- No he reproducido yo el `IMEXIT 139` de §3: con el equipo a carga 30+ una sesión `live` no llegaba ni a la
  primera pantalla (4), así que la evidencia del fallo es la del equipo y la del subagente que midió el
  cuelgue, más el chequeo estático, que rechaza solo esos mismos desplazamientos.
- `estable.sh` no recompila el shim (`shim/build.sh` sigue siendo manual) y no toca `im.sh`, `run.py` ni
  `live.py`: son ficheros **nuevos** (`estable.sh`, `chequea_trampas.py`), así que ningún perfil ni script de
  otro subagente cambia de comportamiento.
- Evidencia en `reports/evidence/film-pb-1-sub-arnes-estable-20261126/`: `1-seco-sin-instrumentar.txt`,
  `2-seco-instrumentado.txt` (resuelve `TRACELIB`, 0 impactos en seco), `3-chequeo-trampas.txt` (los 10
  desplazamientos), `4-live-sin-pantalla.txt`, `5-verifica-no-concluyente.txt`, `6-verifica-ok.txt` +
  `6-verifica-ok-last.log` (la corrida OK) y `ciclo_live.py` (ciclo en vivo con marcas de tiempo).
- Alcance de la entrega: sólo `reports/` y `reports/evidence/<subagente>/`. No se han tocado
  `docs/PENDIENTES.md`, `docs/STATE.md`, `knowledge/` ni `CONTEXT.md` (lo hará quien integre el informe en la
  sesión principal).
