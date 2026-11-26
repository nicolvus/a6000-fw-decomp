# FILM-PB-1 — sector 0x31 aplicado en la cámara: estado y traspaso (26-11-2026)

Cámara `192.168.1.30` (telnet root del Tweak + adb 5555), fw 3.93 `pp`. Todo lo de abajo está
medido en la cámara salvo donde diga «sin medir».

## 1. Estado final en una línea

El sector `0x31` **existe ya** en la cámara (`idx 10 = 0x31 handle=6 valido=1 OM=6`, 5/30 con
handle), pero **ni el clip nuevo ni el antiguo se reproducen** y «Recuperar BD imág.» sigue sin
dar error. Falta comprobar el `fn` de `0x9D23FC[13]` y capturar el log en el momento del intento.

## 2. Cadena falla → solución → resultado

| # | Falla medida | Solución aplicada | Resultado |
|---|---|---|---|
| 1 | La traza no armaba nada: `X i=0 leido=0x0` y `armados=0` en todos los puntos | `PTRACE_PEEKTEXT` en ARM **escribe el dato en el puntero `data`** (`generic_ptrace_peekdata`), no lo devuelve en `r0`; con `data=0` da `-EFAULT`. Se pasa `&w` | `armados=5/6` y golpes reales |
| 2 | Tras `PTRACE_ATTACH` el `PEEK` seguía fallando | Falta `wait4` para recoger el `SIGSTOP` antes de `PEEK/POKE` | attach estable en 161-166 hilos |
| 3 | `lectura corta en 0x... (0 B)` al releer memoria | El `hd` dentro del `chroot` pedía `/android/dev/fpb1` en vez de `/dev/fpb1` | lecturas OK |
| 4 | La subida del auxiliar (68 conexiones `echo -ne`) se atascaba al reproducir | `adb push` a `/data/local/tmp` + `cp` a `/tmp` | subida en 1 s |
| 5 | La lista de hilos se truncaba | `MAXT` 128 → 256 | La pasada con golpes registró 161 hilos al armar. Falta comprobar la cobertura durante la ventana |
| 6 | El veredicto decía «SIN GOLPES» habiendo golpes | La última lectura del registro (vacía) sobrescribía la acumulada | veredicto correcto |
| 7 | `ptcall` no imprime nada y **deja el proceso trazado** (`TracerPid` apuntando a un `ptcall` colgado); todo `ATTACH` posterior falla | Accesor nuevo `camrw` (attach + `wait4` + peek/poke/call + detach) | Se obtuvieron lecturas. La revisión detectó paradas y errores de escritura sin validar |
| 8 | El anillo no se podía leer con ptrace (`EFAULT`) | Vive en un mapeo `rw-s /dev/mem` (`0ac60000… 82df9000`): se lee por `dd if=/dev/mem` | lectura del anillo OK |
| 9 | **El monitor no consumía** (`A` seguía en 0) | Dos límites del busybox: **no hay `printf`** y **`dd` no acepta `seek` > 2³¹** (el anillo está en `0x82df9000`): las escrituras no se ejecutaban. Nuevo `ringput`, que hace `mmap(/dev/mem)` y deposita la línea | `A=17 B=17` tras `FBM EWBDFD 4 3 0`; `A=31 B=31` tras `FBM InitB 6 3` |
| 10 | Vía alternativa por ptrace (`camrw call`): se imprimieron `-22` y `-25` | La primera llamada omitía un argumento y el accesor no validaba el retorno | Los valores son inconcluyentes |

## 3. Traza física: entrada observada, origen del `0x1A` abierto

La transcripción con golpes registra 6 puntos armados y 161 hilos en `im.elf`:

| pto | VA | golpes |
|---|---|---|
| E `0x437BC0` (entrada del manejador) | | **1** (desde `bl` en `0x42A37A`) |
| A `0x437C0A`, B `0x437C3C` | | 0 |
| C1 `0x437C7E`, C2 `0x437CFC` | | 0 |
| T `0x7111B0` | | 1, **con `r0=0`** (un éxito), desde `0x438192` |

La transcripción termina sin marcador de cierre y las seis relecturas devuelven 0 B. Las otras
dos transcripciones locales tienen cero puntos armados. Los golpes confirman la entrada al
manejador y una traducción de éxito desde otro llamador. Los ceros de A/B/C1/C2 no permiten excluir
esas rutas. El error de AVI y los fallos del IFO proceden del log histórico del 20-10.
[Traza original](film-pb1-traza-camara-20261126.md).

## 4. Aplicación del sector (lo que sí se hizo)

```
ringput 0x82df9000 "FBM EWBDFD 4 3 0"   →  A=0  B=0  -> B=17   ; A=17 B=17
ringput 0x82df9000 "FBM InitB 6 3"      →  A=17 B=17 -> B=31   ; A=31 B=31

idx 10: sector=0x31 handle=6 valido=1 OM=6
con handle != 0: 5/30 -> idx 9(0x30 h4), idx 10(0x31 h6), idx 18(0x62 h1), 23(0xa0 h3), 25(0xb2 h2)
```

Evidencia: `reports/evidence/film-pb1-sector31-camara-20261126/1-verifica-tras-aplicar.out`.

## 5. Prueba en cámara (falla)

1. Clip **nuevo** de 5 s: **no reproduce**.
2. Clip **antiguo**: **no reproduce**.
3. «Recuperar BD imág.»: **sin error** (igual que antes de crear el sector).

Búfer de log del firmware (`/dev/mem` 0x83400000, 1 245 184 B): 2 559 tramos imprimibles y
**ninguna** línea de `mp4Ifo` / `AVI` / `RcsBackup`. Quedó sin verificar la cobertura temporal del
volcado y si se reinició el MPR.

## 6. Siguiente paso exacto

1. En una sesión física autorizada, adquirir una línea base con el firmware actual. Registrar PID,
   mapa, modo de grabación y estado del medio. Verificar por lectura la fila de sector y la fila
   `(4,3)`; el campo `fn` está en `base+0x9D2544`, y el dummy de consola es un puntero Thumb
   reubicado (`base+0x2B5185` para ese ELF). Un cero indica que la fila carece de escritor en
   ese instante. Registrar el arranque antes de atribuirlo a un comando anterior.
2. Grabar un clip normal y comprobar el archivo, el resultado de FBM y la reproducción del mismo
   clip. En el arnés, `0x10100001` indica sector ausente y `0x10100003` se observó con un sector
   vacío. Para comprobar el registro del clip se requiere una lectura satisfactoria con sus datos.
   Guardar el log antes y después, con marcas de tiempo y PID, y controlar que la ruta de adquisición
   siga disponible durante la reproducción.
3. Evaluar la persistencia en un arranque aparte. Verificar sector y datos del clip otra vez.
   El `fn` es volátil. El paquete 3.97 sale antes de registrar su función si el sector ya existe;
   3.95 contiene otra variante y 3.96 restaura la 3.94. Ninguno acredita una reparación física.
   [Parche C empaquetado](fbm-sector31-c-pkg397-20261126.md).

## 7. Rollback y riesgos

- `nflasha4` antes de tocar nada: 10 485 760 B, md5 `5ec6c2a779781e6531f09f64eb472345`
  (`/tmp/nflasha4-rollback-20261126.bin` en el PC y `/android/data/nflasha4-20261126-151107.bin`
  en la cámara). Vuelta atrás: `dd if=... of=/dev/nflasha4 bs=1024` + reinicio del MPR.
- El shell del Tweak **se cuelga al reproducir** y vuelve al salir del modo reproducción.
- `ringput` escribe en `/dev/mem`: si se le pasa una física equivocada, corrompe RAM. La física
  del anillo es el **offset** del mapeo `rw-s /dev/mem` que contiene `X` (hoy `0x82df9000`, pero
  se calcula con `fisica_de`, no se asume).

## 8. Relectura física del arranque posterior (26-11-2026, 16:33 CLST)

La A6000 respondió por Telnet y ADB. `im.elf` era PID 144, tiempo de inicio 148 ticks,
`libmpr.so` con base `0x06B22000` y MD5 `d65462a32da6b8249ec7add0a99d8fe0`, igual al ELF
de fábrica de referencia. El hash identifica esa biblioteca, y la versión completa del
firmware instalado queda sin verificar.

| Lectura | Resultado |
|---|---|
| Fila 10 de la tabla de sectores | `sector=0x31 handle=0 válido=0 OM=0` |
| Fila del escritor `(4,3)` | `sector=0x31 OM=6 fn=0 arg=0` |
| MD5 de `nflasha4` | `5cec73d04b3761d7327eab3d184b527a` |
| Archivos MP4 visibles antes de grabar | `MAH04202.MP4` y `MAH04203.MP4` |

El sector observado con handle en la sesión anterior no está abierto en este proceso. Esto
verifica el estado de RAM tras el arranque posterior. Falta comprobar si la entrada existe en
flash y este arranque falló al reabrirla, o si nunca quedó persistida.

El descriptor actual y su mapa `/dev/mem` coincidieron con la región histórica del anillo MPR.
Una lectura pasiva de 12 544 bytes contenía `Err RcsBackupTblData`, `mp4Ifo_General.cpp(1749)`
con `0xB0800001` y `AviSeqPlay.cpp Error=[ER_BADARG]` en la línea base, antes del nuevo intento.
Estas líneas establecen el control anterior a la grabación. El resultado del clip nuevo debe
identificarse por diferencias entre las capturas, conservando PID y tiempo de inicio.

### Después de grabar, antes de pulsar PLAY (16:37:59 CLST)

La tarjeta añadió `MAH04204.MP4` (9 168 986 B) y `MAH04204.THM` (5 813 B) en
`MP_ROOT/100ANV01`. El anillo añadió `RecStart`, `RecStop`, `EvtStreamWriteComplete` y
`EvtRecComplete`. Seguía el PID 144 con el mismo tiempo de inicio. El handle, la validez
del sector y `fn` seguían a cero. El MD5 de `nflasha4` cambió a
`6de6b36cd5aee15190edee51c592e7f7`. Ese cambio de la imagen global no acredita una
entrada FBM para el clip, y en este tramo no apareció un retorno de escritura de FBM.

### Después de reproducir el clip nuevo (16:39:20 CLST)

El usuario vio la miniatura de `MAH04204` y el mensaje «No se puede visualizar» al pulsar
reproducir. El `.THM` copiado por ADB es un JPEG de 160 × 120 identificado como Sony ILCE-6000.
El MP4 contiene 180 cuadros H.264 de 1440 × 1080 a 30000/1001, 6,006 s y audio AAC estéreo
de 48 kHz. FFmpeg completó la decodificación de audio y vídeo con `-xerror`.
En el archivo, `stts` suma 180 muestras de 1001 unidades y cuadra con `stsz` y la duración
`mdhd` de 180 180 unidades a escala 30 000.

El PID y el tiempo de inicio siguieron iguales. Entre las lecturas posterior a REC y posterior
a PLAY se añadieron dos secuencias con este orden:

1. `EnterMoviePb`
2. `ff4PlayIf.cpp` devuelve `0xB051000B` (primera aparición en línea 1084).
3. `E_AVCON_MOVIE_CODEC_STOP (00002003h)`, `Dec start complete error` y
   `ER_MOVIE_DECODE_FAILED (1600F101h)`.
4. `mp4FileLib_Play.cpp` devuelve `0xB0F2000A`. `PauseRelease` termina con
   `ER_OUTSIDE_RANGE` (`54003024`) y la respuesta es `PlayMovie err = MPR::ER_FAILED`.

El fallo de este clip llega a la ruta de reproducción y de inicio del decodificador. El primer
error nuevo registrado es `0xB051000B`. En el ELF verificado, la línea 1084 pertenece a
`Ff4PlayIf::GetSamplenoByMediatime32Offset` (`0x6DE608`), que busca la muestra correspondiente
a un tiempo multimedia. `0x6F0B08` traduce el retorno interno `0x200` a `0xB051000B`.
El llamado `0x69F83E` puede devolver `0x200` cuando el tiempo calculado alcanza o supera
el límite leído en `[r1+0x40]` (`0x69F904–0x69F90E`), y también propaga errores de otras
llamadas. No se midieron los operandos ni qué rama tomó este intento. El criterio siguiente
es reproducir esa consulta con el mismo MP4 y contrastar el tiempo solicitado con el límite que
usa el firmware.

La relación causal entre ese error, el sector FBM cerrado y el fallo de decodificación sigue
abierta. La fila 10 y `fn` continuaron a cero durante toda la prueba. El MD5 de `nflasha4` no
volvió a cambiar al reproducir.

[Transcripción de las tres capturas](evidence/film-pb1-sector31-camara-20261126/2-graba-reproduce.txt).
Se usaron los controles normales de la cámara y lecturas por Telnet y ADB.

## 9. Contraste del tiempo solicitado y los límites del MP4

El `0xB051000B` de la primera línea 1084 no identifica la pista. El ELF llama a ese
buscador desde dos rutas de audio, una de metadatos y una de vídeo. Una ruta de audio
trata ese código expresamente y sigue. Además, el retorno interno `0x200` también
puede llegar si no se encuentra la entrada de tiempos de la pista. El código por sí
solo deja abiertas esas posibilidades y el caso en que el tiempo alcanza el límite.

El error de vídeo posterior sí queda localizado. Las líneas **3058** de
`mp4FileLib_Play.cpp` y **362** de `mp4FileLib_Play_VideoTrack.cpp` corresponden,
respectivamente, a la salida de `SetPlayStartAndEnd` al llamar a `SetPlayStart`
y a la salida de `GetSyncSampleNoByTime` dentro de este último. El primer método
calcula `startOffsetVT` convirtiendo una posición de la escala 90 000 a la escala
de vídeo y aplicando una corrección con signo. La rutina de vídeo devuelve
`0xB0F2000A` cuando la búsqueda de muestra o de cuadro de sincronía devuelve
`0xB051000B`.

El mensaje de la línea **166** de `mp4FileLib_Play.cpp` sitúa esa llamada dentro de
`ChgPBAttribute`. Este método copia `ResumeInfo` antes de calcular el inicio. La
posición que convierte `SetPlayStartAndEnd` es su campo `vSyncSampleTimeOffset` y la
corrección llega del bloque de atributos. Esto vincula el error posterior con el
cambio de atributos del reproductor. El log no conserva el valor de reanudación ni
indica por qué el arranque inicial del decodificador falló.

| Valor de control en `MAH04204.MP4` | Unidades de vídeo a 30 000/s |
|---|---:|
| Primer DTS y último DTS | 0 y 179 179 |
| Primer CTS y último CTS | 1 001 y 180 180 |
| Inicio de la edición y duración total | 1 001 y 180 180 |

La edición resta 1 001 unidades al presentar la pista. Por ello el último CTS sin
ajustar coincide numéricamente con la duración `mdhd`, mientras que el último
instante de presentación ajustado es 179 179. Son referencias del archivo. La
captura física no imprime `startOffsetVT` ni el límite interno de la tabla cargada;
la igualdad en el archivo no demuestra una comparación de fin de pista en cámara.

La comprobación que discrimina el fallo debe adquirir en la misma consulta
`vSyncSampleTimeOffset`, `startOffsetVT`, el identificador de pista, el puntero
devuelto por la búsqueda de la tabla y el límite, si la tabla existe. Si el puntero
es nulo, la prioridad es la
carga de la tabla. Si existe, se puede reconstruir la comparación con el tiempo
solicitado. [Evidencia del contraste](evidence/film-pb1-sector31-camara-20261126/3-tiempo-de-muestra.txt).

## 10. Respuesta de inicio del decodificador y estado del bloque AV

En el ELF de `libmpr.so` verificado en cámara, el manejador de fin de arranque lee el
estado original en el desplazamiento `+8` del mensaje (`0x2C1916`). Con cero emite
`Dec start complete`; con un valor distinto de cero toma la rama `0x2C1974`, traduce
el estado y emite `Dec start complete error!!`. La traducción en `0x2C0E88` lleva
tanto `0xF1000001` como `0xFB050001` a `0x1600F101` y sobrescribe la palabra original.
El log físico conserva el resultado traducido y otro mensaje de `CodecDrv` con
`0x2003` (`E_AVCON_MOVIE_CODEC_STOP`). La palabra original y quién puso el códec
en ese estado siguen sin medir.

En el mismo arranque (`im.elf` PID 144, tiempo de inicio 148), la lectura de DMM dio
`dmm is active.`, tablas de unidades pobladas y el fichero `/setting/DmmConfig.bin`
de 97 544 bytes. Los dos ficheros de microcódigo H.264 y los dos de arranque ZMA
coinciden con Sony 3.21 por MD5. Se comprobó su contenido en disco; la carga y el
estado del decodificador al pulsar PLAY quedan pendientes.

El `/system/av-cam.bin` leído por hash coincide con el núcleo incluido en cuatro
paquetes locales, entre ellos 3.93 **base**. Frente a Sony 3.21 cambian 233 bytes en
los ocho sitios documentados de la ruta de captura de fotos (Silent/EFCS y envío a
Darwin). El paquete 3.93 **PP** contiene otro núcleo, con 34 013 bytes distintos
del de fábrica. El 3.94 limpio empareja el núcleo Sony con las bibliotecas de la
variante PP, cuyo `libObj.so` difiere del medido en cámara. Por ello el 3.94 limpio
cambiaría más de una variable si se comparase con la sesión actual.

Entre los paquetes locales inspeccionados, 3.93 base y 4.02 sin ISO coinciden con el
núcleo y las tres bibliotecas medidas. Ningún paquete inspeccionado con el
núcleo AV de Sony coincidió en esas tres bibliotecas. Las huellas coincidientes
en dos versiones dejan abierto el número de versión instalado.

El control que aislaría el núcleo AV debe conservar las bibliotecas medidas y la
misma tarjeta, y cambiar solo `av-cam.bin`. En paralelo, una captura del mensaje de
fin de arranque antes de que se traduzca `+8` separaría los orígenes que hoy
comparten `0x1600F101`. [Huellas y rama de arranque](evidence/film-pb1-sector31-camara-20261126/4-arranque-decodificador.txt).

## 11. Base de la cámara y control que conserva `/usr`

En el mismo arranque, la huella de los 84 611 584 bytes de `nflasha15`
comprimida coincide con la del paquete **4.02 sin ISO**. La huella de los
24 182 784 bytes lógicos de `/system` coincide con la de ese paquete, compartida
con 3.93 base. La partición `/usr` distingue ambos candidatos.

Validé en memoria el control sobre la base **4.02 sin ISO**. Reemplazar solo
`AV-CAM.BIN` por el de fábrica cambia **233 bytes en cinco clústeres**, todos
del mismo archivo. La imagen lógica resultante coincide con `nflasha3` de
Sony 3.21. `vmlinux.bin`, `initrd.img` y los metadatos FAT resultan idénticos
a los de la base. En el manifiesto del tar solo cambian `nflasha3` y su
registro de tamaño y CRC en `part_image.sum`; los otros **70 archivos** conservan
su SHA-256, incluida la partición `nflasha15` medida en cámara.

Para comparar A y B hay que repetir la reproducción del clip conservado
`MAH04204.MP4` y comprobar después de cada arranque las huellas de `/usr` y
`/system`, el estado de FBM y el anillo del mismo intento de PLAY. Así también
queda registrado si el reinicio altera por sí solo el síntoma. La validación
actual es offline y las operaciones físicas fueron lecturas. Quedan pendientes
el paquete instalable y la prueba A/B.
[Huellas y contraste](evidence/film-pb1-sector31-camara-20261126/5-control-av-aislado.txt).
