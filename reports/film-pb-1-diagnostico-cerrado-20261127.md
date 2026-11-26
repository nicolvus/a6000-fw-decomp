# FILM-PB-1 — Diagnóstico cerrado: cámara PAL, clips NTSC

> **SUPERADO el 26-11-2026.** Dos pruebas de la cámara en mano refutan la causa de este informe:
> un clip convertido a 25p da «No se puede visualizar» y **un clip grabado por la propia cámara
> tampoco se reproduce**. La cadencia no es la causa; el fallo está en el mutex del `mp4Ifo_If`
> (`0x5BAD00`), que bloquea `GetPlayThumbnailInfo` (`0x6E8430`) y con ello la guarda B
> (`0x437C3C`). Ver [reencuadre](film-pb-1-fallo-global-pb-20261126.md). Se conserva el resto
> del documento por el enum de cadencia, la auditoría de `GetInhInfo` y el estado del selector.

Fecha: 27-11-2026. Sustituye al estado «causa probable» del
[informe de sistema de TV](film-pb-1-causa-sistema-tv-20261127.md) §2: ahora la combinación
está cerrada por evidencia y el arreglo está preparado y probado en laboratorio.

Cámara **no accesible**: la verificación final (reproducir el clip convertido) sigue pendiente
de un minuto de cámara. Todo lo demás está medido.

## 1. La cadena, con el enum verificado

`MprIf::PlayMovie` → orden `0x4000001D` → manejador `FUN_00437BC0` (`0x437BC0`) → dos guardas
que comparan el sistema de TV con la cadencia del clip:

| Guarda | Punto | Qué llama |
|---|---|---|
| A | `0x437BFA` → `0x447A1E` | `GetPlayMovieStatus(6)` `0x60945C` → `GetInhInfo` `0x67B6E0` |
| B | `0x437C2C` → `0x447F26` → vtable `+0x58` | `AviMMgr::isSupportContent` `0x61A8F0` |

`isSupportContent` obtiene la cadencia por `GetPlayThumbnailInfo` (`0x6E8430`, struct de 0x13C B
como octavo argumento), que la escribe en `+0x124` a partir de `+0x100` (1..10) con el `tbb` de
`0x6E0CE0`. El enum está **verificado** por dos tablas del firmware (nombres en `0x686A34`,
numérica en el `tbb` de `0x77AF2C`):

| enum | cadencia | familia | | enum | cadencia | familia |
|---:|---|---|---|---:|---|---|
| 0 | 24000/1001 | 24p | | 5 | 60000/1001 | NTSC |
| 1 | 24 | 24p | | 6 | 100 | PAL |
| 2 | 25 | **PAL** | | 7 | 120000/1001 | NTSC |
| 3 | 30000/1001 | **NTSC** | | 8 | 200 | PAL |
| 4 | 50 | PAL | | 9 | 240000/1001 | NTSC |

Con `TvSystem==1` (**PAL**) se aceptan 24p y 25/50/100/200; con `TvSystem!=1` (**NTSC**) se
aceptan 24p y 29,97/59,94/119,88/239,76. Cualquier otro caso: `return 0` → `0x437C3C` → `0x1A`
→ `DefObjPlayer::ER_FAILED (7)` → caution `0x135` → «No se puede visualizar.».

## 2. Por qué se concluye que la cámara está en PAL

1. Los **siete** clips de la tarjeta son `30000/1001` = **enum 3**, y **ninguno** se reproduce.
2. Si la cámara estuviera en NTSC, el enum 3 estaría entre los aceptados y se reproducirían.
3. La única combinación que explica que falle el 100 % es cámara **PAL** con clips NTSC.
4. Corolario: una cámara PAL no ofrece 30p al grabar, así que esos siete ficheros no salieron de
   ella; vienen de otra fuente (otra cámara o una tarjeta ajena).

Y el cambio de sistema no es una salida: `DefRootView::ActionNtscCaution::execute` (`0x17A930`)
exige `Bkup_Read(0x01070148) == 1` antes de mandar el evento `0x89E`, y ese id vale **`00` en los
62 volcados** que lo contienen ([evidencia](evidence/film-pb-1-nvram-20261127/flag-ntsc-01070148.txt)).
El ítem de menú, además, es un stub (`getValue`/`setValue` en `0x24B448`/`0x24B450` son
`return 0`), así que exponerlo no serviría de nada.

## 3. El arreglo, preparado y probado en laboratorio

`scripts/mp4_set_framerate.py` reescribe **solo** el `mdhd.timescale` de la pista de vídeo
(timescale = delta de muestra × fps pedidos) y deja intactas las cajas que el lector de Sony
verifica. Sobre `MAH04198.MP4`:

| Comprobación | Resultado |
|---|---|
| bytes distintos | **2** (`0xDDE20C`, `0xDDE20D`), dentro de `moov > trak > mdia > mdhd` |
| tamaño | idéntico (14 545 696 B) |
| cajas `MSNV`, `uuid`, `PROF`, `USMT`, `MTDT` | todas presentes e idénticas |
| `ftyp` | `MSNV` minor `0x015A0070`, intacto |
| `r_frame_rate` | `25/1` (antes `30000/1001`) |
| decodificación | completa, sin errores |
| fps calculado | **25,000000** frente a 29,970030 |
| duración | 11,40 s (20 % más lento; los 285 cuadros se mantienen) |

Para los siete clips hay un comando único que convierte y **verifica cada fichero** (mismas cajas,
mismo tamaño, cadencia leída):

```bash
python3 scripts/filmpb1_convertir_clips.py /ruta/tarjeta/MP_ROOT/103ANV01 /ruta/salida --fps 25
```

Solo procesa ficheros que tengan las cinco cajas de Sony; si a uno le falta alguna, lo deja intacto y
lo marca `NO TOCADO` ([transcripción](evidence/film-pb-1-v1-remux-20261127/lote-conversion.txt)).

## 4. Primer ensayo en cámara: no concluyente (el fichero quedó incoherente)

Lo que se vio el 27-11 con el primer `prueba-MAH04198-25p.mp4`: la cámara **lo indexa** (aparece en la
lista y en el contador), **no genera miniatura** y **no reproduce**. Por la propia cadena del firmware eso
encaja con un fichero incoherente: el primer reescritor cambiaba `mdhd.timescale` pero dejaba
`mvhd.duration`, `tkhd.duration` y `elst.segment_duration` en los 9,5095 s originales, así que el mismo
fichero declaraba 9,51 s en tres sitios y 11,40 s en el `mdhd`. Cualquier lector que use `mvhd`/`elst`
sigue calculando 285 / 9,5095 = **29,97 fps** (y el que use el `mdhd` ve 25): el ensayo no probaba «un
clip de 25p válido».

Corregido: el reescritor escala ahora las cuatro fuentes. El fichero resultante es coherente:

| Campo | Antes | Ahora |
|---|---|---|
| `mdhd.timescale` / `duration` | 30000 / 285285 (9,5095 s) | 25025 / 285285 (11,400 s) |
| `tkhd.duration` (vídeo) | 855855 | 1026000 |
| `elst.segment_duration` (vídeo) | 855855 | 1026000 |
| `mvhd.duration` | 855855 | 1026000 (escala 90000) |
| audio (`mdhd`, `tkhd`, `elst`) | 9,4933 s | **sin tocar** |
| `ffprobe` | — | formato 11,400 s · vídeo 25/1 11,400 s · audio 9,4933 s |
| bytes distintos | 2 | **11** (solo campos de tiempo) |

Nuevo fichero: `prueba-MAH04198-25p-v2.mp4` (copia en `~/Documents/a6000/`).

## 5. Lo que falta, y es un minuto

Copiar **`prueba-MAH04198-25p-v2.mp4`** a la tarjeta como `MP_ROOT/103ANV01/MAH04201.MP4` y
reproducirlo (y borrar antes el `MAH04200.MP4` del primer intento):

| Resultado | Conclusión y siguiente paso |
|---|---|
| Se reproduce (y los de 30p no) | **Objetivo cumplido**: pasar el reescritor a los siete clips |
| No se reproduce | El rechazo no es la cadencia: toca la traza (`scripts/camera_filmpb1_trace.py`) para ver qué guarda salta y con qué valor |

**Detalle del ensayo que importa:** copiar el fichero con **nombre nuevo** (`MAH04200.MP4`) para que
la cámara cree una entrada de índice limpia. El fichero convertido conserva el tamaño (14 545 696 B)
pero su duración pasa a 11,40 s, y el índice `AVF_INFO\AVIN0001.INP` guarda `nDuration` y `nFileSize`:
si se sobrescribe el original, la entrada queda descuadrada. Si al insertar la tarjeta el clip nuevo
no aparece en la lista, ejecutar «Recuperar BD imág.» (reconstruye el índice, `CreateAVIndexFile`
`0x7A7E7C`) y volver a mirar.

## 6. Límites

- **NO_VERIFICADO en cámara**: que `TvSystem()` valga 1 hoy (se deduce de que falle el 100 % de
  los clips NTSC, no de una lectura directa) y que el clip convertido se reproduzca.
- La duración del clip convertido crece un 20 %: es el precio de cambiar la cadencia declarada
  sin recodificar. Si se prefiere duración y movimiento exactos, hay que reencodear a 25p y
  perder las cajas propietarias (el lector de Sony dejaría de reconocerlo).
- Los volcados de NVRAM son del 20-10 al 22-11; el CFW 3.93 se instaló el 24-11.
