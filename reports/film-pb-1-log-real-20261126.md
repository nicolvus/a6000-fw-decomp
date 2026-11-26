# FILM-PB-1 — El log real de la cámara: la cámara es NTSC, el IFO no carga y la lectura del volumen falla

Fecha: 26-11-2026. **Evidencia directa del propio firmware**, no inferencia: el anillo de log
del proceso MPR quedó volcado en un dump de RAM del 20-10-2026 y contiene el arranque
completo, los fallos de carga de los tres IFO y un intento de reproducción.

Fuente: `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (1 GiB, volcado por
SWD del 20-10-2026 23:21). El anillo vive en **VA `0x82DF9300`–`0x82DFC400`** (offset
`0x2DF9300` en el dump) y son 130 líneas de texto. Evidencia extraída:
`reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt`
(reproducible con `extraer_anillo.py`, en la misma carpeta).

Es de **antes del CFW 3.93**, que se instaló el 24-11-2026: nada de lo que sigue puede
atribuirse al paquete `pp`.

## 1. La cámara es NTSC y los clips son 29,97 — la cadencia queda refutada por log

```
[AVIMMGR][MS1]SetLoadInfo : TvSystem is NTSC, frameRate 3
```

`frameRate 3` = `30000/1001` en el enum verificado (`0x686A34`), el mismo de los siete clips
de la tarjeta. **La comparación que hace la guarda de cadencia se ejecuta y coincide.** El
`TvSystem` de esta cámara es **NTSC**, no PAL: el «diagnóstico cerrado» del 27-11 partía de
una cámara PAL y esa premisa es falsa. `SetLoadInfo` se llama justo después de los tres
`FlashLoad*` fallidos, así que la guarda de formato se evalúa sobre un IFO que no se ha
cargado.

## 2. Ningún IFO se carga: los tres `LoadExec` fallan

La secuencia completa aparece **tres veces**, una por formato, y nunca hay un `LoadExec`
correcto:

```
[AVIMMGR][MS1]MountCmd : Flash Mount Error            ← /dev/mmca (SD)
[AVIMMGR][MS1]GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted
[AVIMMGR][MS1]LoadSub : AVCHD IFO Load() Error.       0xA0100003  MMgrAvcHdIfoAcsr.cpp(2608)
[AVIMMGR][MS1]LoadSub : XAVC Load Error.              0xB0800005  MMgrXavcIfoAcsr.cpp(2480)
[AVIMMGR][MS1]LoadSub : MP4 Load Error.               0xB0800001  MMgrMp4IfoAcsr.cpp(2319)
[MMGR][MMGR_ACSR] ## ERROR(MMGR):0x31000006 ## …CreateAndLoad()
[AVIMMGR][MS1]FlashLoad{Mp4,Xavc,AvcHd} : CreateAndLoad Error
[MMGR][AVI] ## ERROR(MMGR):0x31000006 ## avimmgr/AviMMgrCmd.cpp(13247|13584|13089)
[AVIMMGR][MS1]LoadExec : Flash Load Error
```

Y en la capa de más abajo, el fallo del parser MP4 con su nombre y su línea:

```
[MP4IFO] ### mp4Ifo faild at IF/mp4Ifo_General.cpp(1749) ErrCd: 0xB0800001
[MP4IFO] ### mp4Ifo faild at IF/mp4Ifo_General.cpp(1340) ErrCd: 0xB0800001
```

`0x31000006` es el código que el motor devuelve al manejador cuando el contenido no está
disponible, y `0xB0800001`/`0xA0100003` son «estado inválido» / «no existe» del IFO. Es
decir: **el `mp4Ifo_If` existe pero no está *loaded***, exactamente el estado que hace
fallar `MMgrMp4IfoAcsr::GetInhInfo` (guarda A) y `Mp4IfoIf::GetPlayThumbnailInfo`
(guarda B). Las dos guardas y la falta de miniatura salen del mismo sitio.

## 3. La base de datos de respaldo también falla

```
## HD-AVC COMMAND ERROR ##  CMD ID : 004E  ERROR : A0100003
[MMGR][MMGR_ACSR] ## ERROR(HDAVCIFO):0xA0100003 ## MMgrAvcHdIfoAcsr.cpp(791) CheckSalvageStatus()
[MSV][MS1]Err RcsBackupTblData
[DCF][MS1]Err RcsBackupTblData
```

`CheckSalvageStatus` es la comprobación de la recuperación de la BD, y la tabla de respaldo
(`RcsBackupTblData`) da error en las tres capas (`MSV`, `DCF`, `HDAVCIFO`). Esto explica por
qué **«Recuperar BD imág.» no arregla nada**: la reconstrucción se apoya en esas mismas
tablas.

## 4. El intento de reproducción, tal cual

```
[AVI]AviEdit::Unknown Function[0x000000BD] Error=[Module 0x1 Unknown Error[0x1017]] Line=[6490]
[AVI]CS_AviAcsr::Unknown Function[0x00000020] Error=[INT_ERCD_INVALID_PARAM] Line=[9860]
[AVI][PLAY]     sources/avi_if/AviSeqPlay.cpp Error=[ER_BADARG] Line:10332
```

`ER_BADARG` en `AviSeqPlay` es el **mismo** «Invalid State» que el arnés reprodujo al emular
`mp4Ifo_AVISequence` → `0x1D7022` → `0x21F1F4`
([emu-fps](film-pb-1-sub-emu-fps-20261127.md), `CS_AviMainState::CheckState` →
`0xB0800001`). El motor rechaza la reproducción porque su estado no es válido, y el estado no
es válido porque el IFO no se cargó.

## 5. No es solo vídeo: la lectura del volumen falla también en foto

En la misma sesión, al entrar en reproducción de imagen:

```
[Cache]BUFFER SIZE TOO SMALL : 00000000
[CACHE]ERROR(C1000002h)
[StillCache]ERROR:StillCacheRead::StartRead> Failed to dfs::seek offset=0x0049CE00 errcode=0x0E100001
[StillCache]ERROR:StillCacheFile::Read> Failed to read errcd=0xC3000101
[StillCache]ERROR:StillCache::Read> Failed to Read errcd=C3000101
[DCF][MS1]ReadScreenNailImage pAddr = [117AE000]  readSize = [000605EC]
```

`dfs::seek` y `dfs::read` son el sistema de ficheros. Que fallen en una miniatura de foto
significa que **el problema no es del decodificador de vídeo ni del player**: es la lectura
del volumen (o el tamaño de caché, que llega a 0).

## 6. El `0:02`, explicado por el propio firmware

```
[MprCnv] Warning ResumeInfo Structure Size is different!
sizeof(MPR::RSMPoint): 64, sizeof(PubResume::ResumeInfo): 60
```

El conversor de `libmpr` avisa de que convierte una estructura de 60 B a 64 B al leer el
punto de reanudación. Es el mecanismo que el informe del 27-11 señaló como fuente del `0:02`
(`Get/SetContentResumePoint`): la duración no viene del `moov` sino del estado de reanudación
que se lee de una estructura que no coincide en tamaño.

## 7. Conclusión

El fallo es **la carga del IFO / lectura del volumen**, no el vídeo:

1. `MountCmd : Flash Mount Error` y `DEVICE Unmounted` en el montaje.
2. `CreateAndLoad Error` en los tres formatos; `mp4Ifo` con `0xB0800001`.
3. La BD de respaldo (`RcsBackupTblData`) da error, que es lo que consulta «Recuperar BD imág.».
4. `dfs::seek`/`dfs::read` fallan también con una foto y la caché recibe tamaño 0.
5. Y todo esto ocurre **con el firmware de antes del CFW**.

`0:02`, la miniatura ausente y «No se puede visualizar» son consecuencias del mismo estado:
sin IFO cargado no hay duración real, ni miniatura, ni reproducción.

## 8. Tres pruebas gratis, sin flashear y sin abrir la cámara

| # | Prueba | Si sale bien | Si sale mal |
|---|---|---|---|
| 1 | Ver si las **miniaturas de las FOTOS** aparecen | descarta el almacenamiento y devuelve el foco al lector de vídeo | confirma que es el volumen: no hay que tocar el firmware |
| 2 | **Otra tarjeta formateada en la cámara**, grabar un clip y reproducirlo | la tarjeta/volumen es la causa y el arreglo es formatear la actual | la causa está en la cámara (lector/memoria interna) |
| 3 | **Quitar la tarjeta** y reproducir lo que haya en la memoria interna | confirma que el fallo viaja con el volumen | el fallo es del lector o del montaje, no del contenido |

Ninguna de las tres requiere autorización especial: no escriben nada en la cámara que no sea
una grabación normal.

## 9. Límites

- **NO_VERIFICADO**: que el volumen del 20-10 sea el mismo que el de ahora. El log es de una
  sesión de pruebas de ese día y puede reflejar la tarjeta ausente o mal montada.
- Falta un log de una pulsación de reproducción **de vídeo** con la tarjeta actual: el anillo
  del 20-10 solo conserva la de imagen (`EnterStillPb`/`PlayStillSingle`).
- `0x0E100001` y `0xC3000101` no se han resuelto a nombre en la tabla de errores.
- Los dumps posteriores (17-11, 22-11) no contienen el anillo de MPR, y en el repo no hay ningún
  dump de la zona `0x82DF…` posterior al 24-11 (ya con el CFW).
