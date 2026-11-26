# FILM-PB-1 — Diagnóstico cerrado: cámara PAL, clips NTSC

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

## 4. Lo que falta, y es un minuto

Copiar `prueba-MAH04198-25p.mp4` (generado en `~/Documents/a6000/`) a la tarjeta como
`MP_ROOT/103ANV01/MAH04200.MP4` y reproducirlo:

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

## 5. Límites

- **NO_VERIFICADO en cámara**: que `TvSystem()` valga 1 hoy (se deduce de que falle el 100 % de
  los clips NTSC, no de una lectura directa) y que el clip convertido se reproduzca.
- La duración del clip convertido crece un 20 %: es el precio de cambiar la cadencia declarada
  sin recodificar. Si se prefiere duración y movimiento exactos, hay que reencodear a 25p y
  perder las cajas propietarias (el lector de Sony dejaría de reconocerlo).
- Los volcados de NVRAM son del 20-10 al 22-11; el CFW 3.93 se instaló el 24-11.
