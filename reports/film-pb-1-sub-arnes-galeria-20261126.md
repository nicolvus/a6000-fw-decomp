# FILM-PB-1 / sub-arnés-galeria — intento de reproducir `0xB0100002` en el arnés QEMU (sin cámara)

Sesión: **26-11-2026** (nombre del informe; reloj del anfitrión durante la sesión: 25-11-2026 22:30–22:47, −03).
Cámara: **no usada** (ni red, ni USB, ni `adb`, ni flasheo). Todo ocurre en `qemu-system-arm`.
Espacio de direcciones: **VA del ELF** de `libmpr.so` 3.21 (`SHA-256 9a74a3bb…4c30`); en REA/Ghidra suman `+0x10000`.
Evidencia cruda: [`evidence/film-pb-1-sub-arnes-galeria-20261126/`](evidence/film-pb-1-sub-arnes-galeria-20261126/) ·
comando reproducible: [`comando.sh`](evidence/film-pb-1-sub-arnes-galeria-20261126/comando.sh) ·
cliente del arnés: [`galeria.py`](evidence/film-pb-1-sub-arnes-galeria-20261126/galeria.py).

---

## 0. Veredicto

| Pregunta | Respuesta | Cómo |
|---|---|---|
| ¿Arranca hoy el arnés en esta máquina? | **SÍ** | `run.py` en seco: `alive=206 threads=90 lineas=6723 modulos=80`; dos arranques en frío con `live.py` llegan a la pantalla de disparo (≈100–160 s) |
| ¿Se llega a la galería? | **SÍ a las vistas, NO a contenido** | `view/INDEX_PLAYBACK` (`Vn 03F_viewUnified3`) y `view/SINGLEPB` (`Vn 080_viewUnified2`) se abren y **se cierran solas en 10 ms**; la pantalla queda en blanco |
| ¿Se llega a intentar reproducir un MP4? | **NO** | la tecla Reproducción (`0x1f7`) llega al shim (`tecla 0x1f7`) y **no abre ninguna vista**; no hay ninguna entrada que reproducir |
| ¿Se ejecuta `0x6E8430` (GetPlayThumbnailInfo)? | **NO, ni una vez** | trampa armada al arranque en `libmpr`: `0` disparos en dos sesiones (≈8 min de UI con MP4 real en la tarjeta emulada) |
| ¿Se reproduce `0xB0100002`? | **NO — y no puede reproducirse así** | el mutex `0x5BAD00` está **LIBRE y sin dueño** en el arnés (≥16 adquisiciones medidas, todas con `m_free=1`, `pid=tid=cmd=0`): `0xB0100002` exige un dueño o un objeto muerto |
| ¿Se puede cerrar el diagnóstico desde aquí? | **NO** | el arnés no tiene la causa del fallo (nadie toma el mutex); reproducirlo exigiría **fabricar** el dueño, que no es una reproducción |

Lo que **sí** deja cerrado esta sesión: la instrumentación funciona sobre el `libmpr` real dentro del arnés, el objeto
`mp4Ifo_If` **existe** en el invitado, y el fallo **no** es un «no arranca» del arnés sino que la cadena de reproducción
**no se ejecuta** porque el índice de medios está vacío.

---

## 1. El arnés arranca hoy (VERIFICADO)

```sh
HARNESS_OUT=/tmp/fpb1 SHIMENV='WAIT=60 CVWAIT=0 POKE=fef348 FULLLOG=1' \
  python3 scripts/gui/harness/run.py analysis/gui/g22/harness scripts/gui/harness/im.sh 150
```

Salida ([`arnes-runpy-en-seco.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes-runpy-en-seco.txt)):
`alive=206 threads=90 lineas=6723 modulos=80`, sin `ABORT` ni `EXIT` (`qemu-system-arm` 11.1.3, TCG). Nada que arreglar
en `setup.sh`: `analysis/gui/g22/harness/{vmlinuz,base.cpio.gz,overlay/cam/usr/lib/sonyshim.so}` ya están construidos
(shim de 21-11, 278 464 B).

Arranque interactivo usado para el resto (`live.py`, perfil `arnes2`, puerto 8612, SD emulada propia en `$HOME/A6000-SD`):
primera pantalla a ≈100 s, 39 fotogramas a 161 s, 1,5–3 fps. Perfil `arnes1` (mismo arranque, 8611) para el primer
intento. Ambos perfiles quedan en `analysis/gui/g22/harness/live/` (ignorado por git).

---

## 2. Instrumentación de `0x5BAD00` y `0x6E8430` (VERIFICADO)

No hizo falta tocar el shim: ya trae trampas UDF por biblioteca (`TRACELIB` + `TRACEFN2`, offsets relativos a la base
de la biblioteca, `TRACEDEREF` para volcar memoria en el punto, `TRACEREP` para repetir y contar, `TRACEMAX` para el
detalle). Se armaron **al arranque** (única forma fiable, ver §7):

```
TRACELIB=libmpr.so
TRACEFN2=5bad00,6e8430,6e80a4,61a8f0,608698
TRACEDEREF=d0:0:7        # 7 palabras desde r0 = {vptr, m_free|…, pid, tid, cmd, logModule, logSub}
TRACEREP=1 TRACEMAX=4
```

| Punto | Qué es | Disparos (arnés1, 8611) | Disparos (arnés2, 8612) |
|---|---|---:|---:|
| `0x5BAD00` | `ifoFramework_Semaphore::Acquire` | **≥8** (contador `n` hasta 8) | **≥16** (contador `n` hasta 16) |
| `0x6E80A4` | ctor de `mp4Ifo_If` (crea el wrapper + su semáforo) | **2** | **2** |
| `0x6E8430` | `Mp4IfoIf::GetPlayThumbnailInfo` | **0** | **0** |
| `0x61A8F0` | `AviMMgr::isSupportContent` (guarda B) | — (no armada) | **0** |
| `0x608698` | `AviMMgr::MovieReadStart` | — (no armada) | **0** |

Lecturas del mutex en el arranque ([`arnes2-trazas.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes2-trazas.txt)):

```
TRACE 5bad00 n=1 r0=42b1b060 r1=1  r2=1 lr=ad64d90f
  DEREF 0x42b1b060+0: adb66cf8 42b46501 00000000 00000000 00000000 00000001 00000002 …
  → vptr=vtable 0x8BBCF8 relocalizada, [obj+4]=0x01 (LIBRE), pid=0, tid=0, cmd=0, logModule=1, logSub=2
TRACE 5bad00 n=8 r0=42a4c5a0 r1=1 r2=1 lr=ad9931e1
  DEREF 0x42a4c5a0+0: adb66cf8 4c494501 00000000 00000000 00000000 00000005 00000002 …
  → el mismo layout pero logModule=5 → envoltorio de la familia mp4Ifo_If
```

El código de `0xB0100002` es el **genérico del `ifoFramework` para «no pude tomar el mutex»**: el literal aparece
**144 veces** en `libmpr.so` y lo devuelven (o registran) todas las `ifos`; en `0x6E8460–0x6E846C` está el camino de
`GetPlayThumbnailInfo` (`cbz r0` → sigue; si falló el acquire, `r5 = 0xB0100002` y retorna) y en `0x6E81E2–0x6E81E8`
el mismo literal en `~mp4Ifo_If` (línea `0x97` de `mp4Ifo_If.cpp`), que **ignora** el fallo y sigue.

Conclusión medida: **el mutex del `mp4Ifo_If` existe en el arnés, está LIBRE y no tiene dueño**, y el único uso que se
hace de `Acquire` en toda la sesión son las 16 tomas del arranque (comandos `1, 0x5e, 0x4b, 0x53, 0x55`); **no hay
ninguna toma posterior** (el contador llegó a 16 y no a 32 en los ~90 s siguientes de UI viva). Es decir: la condición
del fallo (`[obj+4]==0` con dueño, o handle colgante) **no se da** en el emulador.

---

## 3. Intento de galería y de reproducción (VERIFICADO, negativo)

### 3.1 Tecla Reproducción (clave `0x1f7`, índice `0x1f`)

`POST /tecla {"k":"reproduccion"}` → `shim.log`: `tecla 0x1f7`. Efecto: **ninguno sobre la vista**. En la sesión 1 la
pantalla pasa de dibujo parcial a OSD completo ([`01-menu.png`](evidence/film-pb-1-sub-arnes-galeria-20261126/01-menu.png)
→ [`02-tras-reproduccion.png`](evidence/film-pb-1-sub-arnes-galeria-20261126/02-tras-reproduccion.png), diferencia en
toda la pantalla = iconos que faltaban por pintar); en la sesión 2 la única diferencia es un icono de 12×19 px en
(603,223) ([`04-arnes2-stlrec.png`](evidence/film-pb-1-sub-arnes-galeria-20261126/04-arnes2-stlrec.png) →
[`05-arnes2-tras-play.png`](evidence/film-pb-1-sub-arnes-galeria-20261126/05-arnes2-tras-play.png)). En ninguna de las
dos aparece una línea `Vn 0xx_…` de apertura de vista después de la tecla.

### 3.2 Forzar las vistas de reproducción (`O vista [modo]` del shim → `viewManagerIf::openView`)

| Vista | Traza del firmware | Duración | Pantalla |
|---|---|---|---|
| `view/INDEX_PLAYBACK` | `Vn 03F_viewUnified3.so` B 160.05 → **E 160.06** | **10 ms** | blanca |
| `view/SINGLEPB` | `Vn 080_viewUnified2.so` B 165.95 → **E 165.96** | **10 ms** | blanca |
| `view/STLREC` (control) | `Vn 088_viewUnified2.so` B 97.29 → E 97.30 y pantalla de disparo | — | OSD completa |

`B`/`E` = el bucle de la vista entra y **sale de inmediato**: no hay contenido que mostrar. Las tres capturas del
estado blanco ([`03`](evidence/film-pb-1-sub-arnes-galeria-20261126/03-openview-singlepb.png),
[`06`](evidence/film-pb-1-sub-arnes-galeria-20261126/06-arnes2-index-playback.png),
[`07`](evidence/film-pb-1-sub-arnes-galeria-20261126/07-arnes2-singlepb.png)) son **idénticas** (sha256 `460199dbac0a…`).
No hay miniaturas, no hay lista, y por tanto **no hay petición de miniatura ni de reproducción**: `0x6E8430` sigue a 0.

### 3.3 El dato sí está en la tarjeta emulada

La imagen FAT32 que recibe el invitado (construida exactamente como lo hace `live.py`, sobre `$HOME/A6000-SD` con
`SD_ESTRUCTURA=1`) contiene el clip real y el índice
([`tarjeta-emulada-mdir.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/tarjeta-emulada-mdir.txt)):

```
::/MP_ROOT/100ANV01    MAH04198 MP4   14 545 696 B
::/AVF_INFO            AVIN0001 INP        1 408 B   (sintético, ver §6)
::/DCIM/100MSDCF       (vacía)
```

⇒ El fallo **no** es que falte el fichero: falta que la base de contenidos lo **enumere**. Hoy `INDEX_PLAYBACK` se
cierra en 10 ms con el MP4 presente.

> `TRACEMAX=4` imprime los 4 primeros disparos y luego solo las potencias de 2: **8** y **16** son cotas inferiores
> (no se alcanzó 16 en la sesión 1 ni 32 en la 2).

---

## 4. Por qué no es viable reproducirlo aquí (y qué falta exactamente)

### 4.1 El eslabón que no existe: el índice de medios

| Pieza | Estado medido en esta sesión | Qué falta |
|---|---|---|
| Procesos / módulos | `im.elf` vivo, 90 hilos, **80 módulos** (incluye `libmpr`, `viewUnified2/3/6`, `libInfraFsys`) | nada |
| `/dev` (tarjeta) | imagen FAT32 entregada por el shim (`/dev/mmca`), con el MP4 dentro (§3.3) | nada (el montaje ya estaba documentado en §5.12) |
| **Datos: índice AV** | `AVF_INFO/AVIN0001.INP` **sintético** de 1 408 B (formato deducido, no verificado) | un `AVF_INFO` **real** (`.INP` + `.BNP`/`.INT`, `PRV00001.BIN`) o un volcado de una SD de la A6000, o que el «Formatear» del MPR termine (hoy no termina, §5.40/§5.46) |
| Vista de reproducción | `INDEX_PLAYBACK`/`SINGLEPB` abren y cierran en 10 ms | entradas en el índice para que la vista se quede y pida miniaturas |
| Petición de reproducción | no se emite (tecla `0x1f7` sin efecto) | elegir un clip (`Intro`) y que la vista llame a `MprIf::PlayMovie` → `FeaIf::PlayMovie` → manejador `0x437BC0` |
| **Dueño del mutex** | **no existe**: ≥16 adquisiciones, todas con `m_free=1`, `pid=tid=cmd=0` | la condición real de la cámara (un hilo que lo tomó y no lo soltó, o el wrapper muerto). **No tiene causa en el emulador** |

### 4.2 Consecuencia importante para el diagnóstico

Aunque se cerrara el índice y se llegara a `0x6E8430`, el arnés **no devolvería `0xB0100002`**: devolvería éxito, porque
`0x5BAD00` encuentra el byte `[obj+4]=1`. Es decir, el arnés reproduce el **camino** (y con él puede descartar las otras
dos guardas), pero **no el fallo**: el fallo es un **estado** (mutex tomado / objeto muerto) que en el emulador nunca se
produce. Fabricar el dueño (un hilo que adquiriera y no soltara) no sería reproducción, sería inyección.

### 4.3 Enlace con el informe hermano de la fuga (sesión paralela, no re-verificado aquí)

`reports/film-pb-1-sub-fuga-mutex-20261126.md` (sesión paralela del mismo día, **sin commit**) concluye que ningún camino
de `mp4Ifo_If` deja el byte a 0 con el objeto vivo, y que un 0 persistente exige **(a)** un hilo vivo dentro de la
sección crítica o **(b)** `~mp4Ifo_If` + `MMgrMp4IfoAcsr::DestroySub` destruyendo el wrapper **sin haber tomado el lock**
(dejan `[handle+4]` apuntando a memoria liberada). Mis medidas encajan: en el arnés el wrapper **se construye** (2
llamadas a `0x6E80A4`) y el mutex se ve **libre y sin dueño**; la vía (b) es la única que *podría* aparecer sin un hilo
culpable, y no la he medido. **NO_VERIFICADO** aquí: ni el contenido de ese informe ni si el arnés llega a destruir el
wrapper (`0x6E81BC`) y a borrar el semáforo (`0x6E81FE`).

### 4.4 Qué haría falta para intentarlo de verdad

1. Un **volcado de la SD real** de la A6000: `AVF_INFO\AVIN0001.INP`, `AVIN0001.BNP`, `PRIVATE\M4ROOT\...` (no hay
   ninguno en el repo: ver [sub-BD-tarjeta §1](film-pb-1-sub-bd-tarjeta-20261128.md)).
2. Copiarlo a `$HOME/A6000-SD` y repetir `comando.sh` **sin cambios** (las trampas ya están en las cinco direcciones).
3. **Criterio de éxito**: `grep -c "TRACE 6e8430" …/shim.log ≥ 1` y, en el `DEREF` de `0x5BAD00`, `[obj+4] = 0` o
   `pid/tid ≠ 0`. Solo entonces el `0xB0100002` sería reproducible sin cámara.
4. **Criterio de fracaso del intento** (lo que hay hoy): `0` disparos en `0x6E8430`, `0` en `0x61A8F0` y `0` en
   `0x608698` ⇒ la cadena de reproducción nunca empieza.
5. **Medida siguiente, barata** (mismo comando, sin tocar código): añadir `6e81bc,6e81fe` a `TRACEFN2` para ver si el
   arnés **destruye** el `mp4Ifo_If` y borra el semáforo; si lo hiciera, quedaría la única vía por la que el
   `0xB0100002` podría aparecer en el emulador sin un hilo dentro de la sección crítica (informe hermano arriba).

---

## 5. Comando exacto para intentarlo (copiable)

Resumen (el fichero completo es [`comando.sh`](evidence/film-pb-1-sub-arnes-galeria-20261126/comando.sh)):

```sh
# 0) tarjeta emulada propia (nada dentro del repo)
H=/tmp/fpb1/home
mkdir -p $H/A6000-SD/DCIM/100MSDCF $H/A6000-SD/MP_ROOT/100ANV01 $H/A6000-SD/AVF_INFO
cp /home/nicolas/Documents/a6000/MAH04198.MP4 $H/A6000-SD/MP_ROOT/100ANV01/
cp reports/evidence/film-pb-1-sub-avin-20261127/AVIN0001_sintetico.INP $H/A6000-SD/AVF_INFO/AVIN0001.INP

# 1) arnés con SD «completa» y trampas en libmpr (terminal 1; ≈100–160 s hasta la primera pantalla)
HOME=$H SD_ESTRUCTURA=1 LIVE_REINTENTOS=1 \
SHIMEXTRA='WAITLOG=1000 LOGMARK=OPENHOT,viewUnified TRACELIB=libmpr.so TRACEFN2=5bad00,6e8430,6e80a4,61a8f0,608698 TRACEDEREF=d0:0:7 TRACEREP=1 TRACEMAX=4' \
.venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir arnes2 --puerto 8612

# 2) llevar la UI a la galería e intentar reproducir (terminal 2)
G=reports/evidence/film-pb-1-sub-arnes-galeria-20261126/galeria.py
.venv/bin/python3 $G --puerto=8612 tecla reproduccion
.venv/bin/python3 $G --puerto=8612 linea "O view/INDEX_PLAYBACK 0"
.venv/bin/python3 $G --puerto=8612 captura /tmp/fpb1/galeria.png

# 3) leer el resultado
grep -ao "TRACE [0-9a-f]*" analysis/gui/g22/harness/live/arnes2/shim.log | sort | uniq -c
grep -a "LOGMARK" analysis/gui/g22/harness/live/arnes2/shim.log | tail -20      # Vn B→E = la vista se cierra
```

---

## 6. Límites y NO_VERIFICADO

- **NO_VERIFICADO** que el `AVIN0001.INP` sintético tenga el formato que el MPR espera: es una deducción de
  [sub-avin](film-pb-1-sub-avin-20261127.md); en esta sesión **no** produjo ninguna entrada visible.
- **NO_VERIFICADO** que la SD esté montada a nivel de `libInfraFsys` en esta sesión concreta: se comprueba que la imagen
  **contiene** el clip (§3.3), no que el lector FAT del MPR la acepte. Para eso hace falta trazar `+0x13e474`
  (`Fsys_FindFirst`) y el estado de medio `+0x23f7ae`, que aquí **no** dieron disparos (§7).
- **NO_VERIFICADO** el dueño que tendría el mutex en la cámara: el arnés solo demuestra que en él está libre.
- **Caveat de método (§7)**: las trampas armadas **en caliente** (`E TRACEFN2=…`) escriben el UDF (se comprobó porque
  mataron `im.elf`), pero **no dieron ningún disparo** en 10–12 s para `0x13e474`, `0x1d1774`, `0x620028` ni `0x615928`.
  Por eso **todas** las conclusiones de §2–§3 se apoyan solo en trampas armadas **al arranque**.
- **NO_VERIFICADO** el efecto de `OPENVIEW` sobre `STLREC`: devolvió `-2140294400` (sesión 1) y `22082776` (sesión 2) y en
  ambos casos la pantalla de disparo se dibuja; el código de retorno no se interpreta aquí.
- No se ha modificado `docs/`, `knowledge/`, `build/`, `tests/` ni el código del arnés; el shim usado es el de 21-11.

---

### 6-bis. Tercer arranque: colgado (no usado como evidencia)

Un tercer perfil (`arnes3`, 8613) con las mismas cinco trampas más `0x6E81BC` (`~mp4Ifo_If`) y `0x6E81FE` (borrado del
semáforo) **se colgó en el arranque**: 2 fotogramas, registro del invitado congelado en 209 s y `CALMA 5,8 s de 20`,
**sin un solo `TRACE`** (ni siquiera los del arranque que sí salen siempre). Es el fallo intermitente de arranque en frío
ya documentado (§5.41 de [g22-avcam-puente](../docs/gui/g22-avcam-puente.md)); no se usó como evidencia y **la pregunta
de si el arnés destruye el wrapper sigue abierta**. Los dos arranques usados (§2–§3) sí llegaron a la UI.

## 7. Nota de método: el armado en caliente mata a `im.elf` si el punto no es una entrada de función

Al probar el armado en caliente se puso una trampa en `0x5fd71b` (es el `ra` de un `bl` a `nanosleep`, **no** una
entrada de función, según las líneas `WAITLOG … ra=libmpr.so+0x5fd71b`). Cuatro segundos después
([`arnes1-crash-armado-caliente.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes1-crash-armado-caliente.txt)):

```
im.elf: monio(input): potentially unexpected fatal signal 11
PC is at 0x18a   LR is at 0xb6e3fb88      →  IMEXIT im_s 139
```

`TRACEREP` deja un `UDF` temporal en la instrucción siguiente y la restaura en el segundo disparo; si el flujo **salta**
(como en un `ra`), la instrucción siguiente no se ejecuta y el `UDF` queda armado donde no toca. Conclusión práctica:
**armar solo entradas de función y preferiblemente al arranque** (`SHIMEXTRA`), nunca mid-sentence ni en caliente.
El estado de la VM estaba guardado (`POST /guardar`, 146 MiB en `live/arnes1/estado.zst`), así que la pérdida fue de
minutos, no del arnés.

---

## 8. Evidencia

| Fichero | Contenido |
|---|---|
| [`arnes-runpy-en-seco.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes-runpy-en-seco.txt) | arranque en seco: `alive=206 threads=90 lineas=6723 modulos=80` |
| [`arnes1-trazas.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes1-trazas.txt) | sesión 1: `0x5BAD00` ≥8 (con `DEREF`), `0x6E80A4` ×2, `0x6E8430` ×0, tecla `0x1f7`, `Vn 03F` B→E |
| [`arnes2-trazas.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes2-trazas.txt) | sesión 2 (5 puntos armados al arranque): `0x5BAD00` ≥16, `0x6E80A4` ×2, `0x6E8430`/`0x61A8F0`/`0x608698` ×0 |
| [`arnes1-crash-armado-caliente.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/arnes1-crash-armado-caliente.txt) | SIGSEGV de `im.elf` al armar `0x5fd71b` en caliente (`IMEXIT im_s 139`) |
| [`tarjeta-emulada-mdir.txt`](evidence/film-pb-1-sub-arnes-galeria-20261126/tarjeta-emulada-mdir.txt) | la imagen FAT32 que recibe el invitado: `MAH04198.MP4` 14 545 696 B + `AVIN0001.INP` 1 408 B |
| `01-menu.png` … `07-arnes2-singlepb.png` | pantallas: STLREC antes/después de la tecla Reproducción y los tres estados blancos (idénticos) de `SINGLEPB`/`INDEX_PLAYBACK` |
| [`galeria.py`](evidence/film-pb-1-sub-arnes-galeria-20261126/galeria.py) | cliente mínimo del arnés (`estado`, `tecla`, `linea`, `captura` por SSE) |
| [`comando.sh`](evidence/film-pb-1-sub-arnes-galeria-20261126/comando.sh) | comando exacto, de cero a resultado |

Perfiles de VM usados: `analysis/gui/g22/harness/live/arnes1/` (8611), `.../arnes2/` (8612) y `.../arnes3/` (8613, el
arranque colgado de §6-bis), ignorados por git; el `shim.log` completo de cada uno queda allí.
