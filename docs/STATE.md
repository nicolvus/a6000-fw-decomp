# Estado vigente — Sony A6000 reverse engineering

## Reproducción de vídeo — la rotura es del arranque EN FRÍO del propio 3.21 (28-11-2026)

> **Cambio de conclusión, medido.** El par A/B de la bisecta no aísla un parche: A es el tar de fábrica
> 3.21 con **un solo miembro menos** (`0700_part_image/dev/nflasha5`) y los otros 71 son idénticos byte a
> byte; B es ese mismo tar íntegro. A no reproduce y B sí ⇒ **la causa no es ningún cambio del CFW, sino
> el camino de arranque en frío (Loader3 `BootMode 1`) del 3.21 de Sony**. En el campo ese camino casi no
> se recorre: `ud_wbi_drop.elf` invalida el WBI y el propio paquete oficial lo reescribe acto seguido.
> **Dónde falla (VERIFICADO contra bytes):** el core AV contesta al mensaje `0x2003` («movie decoder
> start») con estado ≠ 0; `libmpr` lo traduce en `0x2C0E88` a `0x1600F101` (`E_AVCON_MOVIE_CODEC_STOP`,
> nombre de la tabla `0x2D0B44`) y `MDecI/F` (`0x462E2C`) lo convierte en `0x16001001`
> = `ER_MOVIE_DECODE_FAILED` → `libObj` `ER_FAILED`. **Corrección:** el `00002003h` del anillo es el **id
> del mensaje**, no un código de error. **Qué cambia en frío:** Loader3 carga 6 ficheros RAMCFG en vez de
> 2 (`sa_dfdet.bin`, `kemco.txt`, `initrd.img`, `vmlinux.bin` de más) y **no se restaura la instantánea**
> (estado de MPR/`libmpr`/`libObj` + 12 regiones `wbimem=`); `im.elf` vuelve a pedir la carga de
> `av-cam.bin`. **Qué no cambia:** `av-cam.bin` tiene **0 de 2 200 páginas** dentro del WBI ⇒ la imagen
> del core AV es la misma en ambos modos; cmdline, módulos, montajes y `DmmConfig.bin`, iguales.
> **Causa última: NO DEMOSTRADA** (tres mecanismos vivos y un experimento de 4 bytes que los separa).
> [Informe](../reports/film-pb-1-busqueda-decodificador-frio-20261128.md) ·
> [evidencia](../reports/evidence/film-pb-1-busqueda-decodificador-frio-20261128/)

## Reproducción de vídeo — FILM-PB-1, estado de FBM (26-11-2026)

> **Arreglo identificado y verificado en el arnés (26-11-2026).** El sector que falta es **uno solo**:
> `0x31`, idx **10** de `0xA3699C`, compartido por `userID 0x04` y `0x21` (**OM 6 = M2PS**) con
> **mediaID 3 (MS1, la tarjeta)**. Tabla de pares `0x9D23FC` volcada del propio ELF
> (`reports/evidence/film-pb-1-causa-fbm-20261126/tabla_pares_om.txt`): los otros tres pares del media 3
> ya tienen handle (`0x10` OM 4 → `0x30`, `0x20` OM 7 → `0x62`, `0x23` OM 10 → `0xB2`), y `0x90/0x91/0x92`
> son de **media 7 (USB)**, no de la tarjeta. El cerrojo es `0x2B3000` (`0x2B301A cbz r2`): salta las 37
> filas de `0x9D23FC` con `fn == 0`, y las 37 lo están; el único escritor de `fn` es
> `BackupMgr::EntryWriteBaseDataFunction` (`0x2B1DEC`), expuesto en consola como `EWBDFD` y como test de
> fábrica **`LTC`**.
> **Vía de consola, sin flashear y persistente (1 300 B en `nflasha4`):** `FBM LTC 1` (o `FBM EWBDFD 4 3 0`)
> y después **`FBM InitB 6 3`** → idx 10 = `0x31 / h3 / +8=1 / om6` y `BkRead(0x04,3)` pasa de
> `0x10100001` a `0`; persiste tras reiniciar porque `FBM::Init` la reabre. El monitor se alimenta por un
> anillo en memoria (`X = u32 en libmpr+0xA4FD88`, cabecera `[X]`=lectura `[X+4]`=escritura, datos en
> `X+0x10`, 0x400 B, terminador CR), y desde la cámara se deposita con `tools/camera-ptrace/ptcall`
> (`sh tools/camera-ptrace/fbm_ring.sh "FBM InitB 6 3"`). La vía `EWBDFD`/`ChgSec`/`CRFB`/`WBI` por sí
> solas no crean nada. [Informe](film-pb-1-sub-consola-sector31-20261126.md) · [anillo](film-pb-1-sub-consola-fbm-anillo-20261127.md).
> **Vía CFW (alternativa, sin depender del telnet):** parche de 68 B en `libmpr.so` (gancho en `0x7126E6`
> → cueva en `0x93B000`: `FBM::Init` + `CreateSector32(0x31)` + alta manual de la entrada) medido en el
> arnés (`idx10 h2 válido1`, `BkRead` `0x10100003`, que el llamante tolera). Paquete **3.95**
> `build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat`
> (sha256 `61bfcb79…b442a`, auditoría `todo_ok` 22/22, solo cambia `/lib/libmpr.so` de 715 ficheros) y
> vuelta atrás **3.96** (`f5283bf9…6c47`). No persiste entre arranques con `libmpr` de fábrica y rota una
> página de control de 1 KiB por arranque. [Informe](film-pb-1-sub-fbm-sector31-20261126.md) ·
> [paquete](film-pb-1-sub-paquete-cfw395-fbm31-20261126.md).
> **Aviso:** crear el sector **no rellena** la base de datos; después hay que dejar que la cámara la
> reconstruya (grabar un clip nuevo o el menú de recuperación) y solo entonces probar la reproducción.
> **¿Basta el sector? Sí, con matiz (medido):** con idx 10 registrado, `BkRead(0x04,3)` = `0x10100003`
> (tolerado) → `RcsBackupTblData` = `0x00500003` → `0x3AFA94` lo toma como *Need Salvage*, deja
> `[msv+0x44]=1` y **devuelve 0** → `FlashLoadForMsv` (`0x698EC8`) devuelve **0**, sin el 1749. Antes daba
> `0x00100001` / `0xB0800001`. Queda una tabla **vacía marcada para salvage**: el firmware la reconstruye y
> un clip nuevo sí se registra; los viejos no.
> **Matiz medido el 26-11 sobre la ESCRITURA del clip (26-11):** el camino `m2psIfo_Backup` →
> `ChangeSector(4,3)` `0x2B41B4` / `WritePackBegin` `0x2B3D24` / `WritePackAdd` `0x2B3C64` /
> `WritePackEnd` `0x2B3B94` **no** funciona sólo con el sector: sobre la imagen con `0x31` persistido y
> `fn=0`, `ChangeSector` = `0x10800010` (`0x2B4232` ← `0x2B3000`/`0x2B301A`) y `WritePackEnd` =
> `0x10800020` = `FBS_UNCERTAIN_WRITE_POINT` (`0x11`; `GetSectorInfo` da `validDataSize=0xffffffff`) y
> **0 bytes** llegan a `nflasha4`. Con `fn` registrado en `0x9D23FC[13]` en el **mismo arranque**
> (`FBM EWBDFD 4 3 0`) + sector: `ChangeSector=0`, `WritePackBegin/Add/End=0` y **4 770 B** escritos.
> `0x9D23FC` es `.data` de `libmpr`: el `fn` **no persiste**, el sector sí. Por eso `EWBDFD`+`InitB` y la
> prueba de grabación tienen que ir en el **mismo** arranque. [Informe](clip-write-cs-wpb-20261126.md).
> **Auditoría independiente del 3.97:** `.dat` `69447a27…5cd9`, `libmpr` `831142ae…e378e`, relocaciones y
> cabeceras intactas, auditor `todo_ok` 22/22; la cueva está en `.rodata` pero se ejecuta por el primer
> `PT_LOAD` (`R E`) —medido en QEMU— y su alineación de pila no afecta a los tres destinos.
> **Camino de escritura (medido en el invitado):** con el sector `0x31` **y** el `fn` de `0x9D23FC[13]`,
> `ChangeSector(4,3)` = `0`, `WritePackBegin/Add/End` = `0` y un clip nuevo deja **4 770 B** en `nflasha4`;
> sin uno de los dos, `WritePackEnd` = `0x10800020` o `ChangeSector` = `0x10800010`/`0x10100006`. Es decir:
> el arreglo completo son las dos cosas, y eso es justo lo que hacen `EWBDFD 4 3 0` + `InitB 6 3` y el
> parche C.


> **La tabla de sectores del backup FBM está vacía y nada la recrea.** `0xA3699C` (30 entradas × 0x14,
> `+4` = handle de sector de `FlashLib`) solo tiene **4 entradas con handle** en el volcado de RAM del
> 20-10 (`0x30`, `0x62`, `0xA0`, `0xB2`); las de foto (`0x90/0x91/0x92`) y las de vídeo (idx 24…29) están
> a 0. `ReadFirstPackData` (`0x2B3948`) devuelve `0x10100001` en `0x2B3A28` cuando `[entrada+4]==0`; con
> eso `RcsBackupTblData` falla, `mp4Ifo` imprime `0xB0800001` por su fallback (`0x6F0D4C`), el IFO no queda
> cargado. La guarda A puede producir `0x1A` en `0x437C0A`; falta demostrar que produjo el de esa sesión.
> `FBM::Init` (`0x2B4820`) solo registra sectores que **ya existen**
> (`CheckExistSector == 0x45`) y **no crea ninguno**; el anillo de `nflasha4` nunca tuvo más de cinco
> `fileType` en ninguno de los tres volcados. **Correcciones a lo publicado el 26-11:**
> `FlashLib::Init` **sí** tiene llamante (`0x7126E2`, antes de `BackupMgr::Init`) y el log de arranque
> trae `[DFB] partition start sector = 100864`, así que el flash arranca bien; `ExecMprUtility(1)` no es
> la vía de arranque. **Arreglo:** `BackupMgr::InitBackupData(OM, mediaID)` (`0x2B43F0`) o su consola
> `InitB [OM] [MediaID]` (`0x2B5B5A`), y después reiniciar MPR (la tabla es un snapshot de
> `MprIf::Create`). **La consola sola no basta (medido 26-11-2026):** `0x2B3000` salta las filas de
> `0x9D23FC` con `fn==0` (las 37 están a 0) y el único escritor de `fn` es `BackupMgr::EntryWriteBaseDataFunction`
> (`0x2B1DEC`), que la consola expone como `EWBDFD`/`CWBDF` — y como el test de fábrica **`LTC 1`**.
> Secuencia que funciona en el arnés (`NFLASH4=1`): `FBM LTC 1` (o `FBM EWBDFD 4 3 0`) + `FBM InitB 6 3`
> ⇒ idx 10 de `0xA3699C` = `0x31`/handle válido/`+8=1`, `BkRead(0x04,3)` = `0` (`0x10100003` con el dummy)
> y **persiste** al reiniciar (1 300 B en `nflasha4`: páginas `0x9D400`, `0xBD400` y `0x380000`).
> No escribir `nflasha4` a mano sin rollback.
> **Parche C (26-11-2026, medido):** un `libmpr` que en cada arranque hace eso mismo — tras `FBM::Init`,
> si `0xA3699C[10].handle==0` llama a `0x2B1DEC` para `(4,3)` y `(0x21,3)` con un stub propio y a
> `InitBackupData(6,3)` — **crea y persiste**: la imagen que escribe es byte a byte la de la consola
> (`6d2ab43a…`) y un segundo arranque con el `libmpr` de fábrica ya registra idx 10 (`CheckExistSector=0x45`,
> `BkRead(0x04,3)=0x10100003`) **sin escribir un byte**; cuando el sector ya existe el parche tampoco escribe
> (0 B). Dato nuevo de código: `0x2B3F7C` **sí llama** al `fn` registrado (`blx r3`, `r0=arg`) ⇒ el dummy de
> fábrica `0x2B5185` aborta el arranque y hay que registrar un stub inocuo.
> [Informe causa](../reports/film-pb-1-causa-fbm-20261126.md) ·
> [informe consola/0x31](../reports/film-pb-1-sub-consola-sector31-20261126.md) ·
> [informe parche C](../reports/fbm-sector31-c-persistente-20261126.md).


## Reproducción de vídeo — revisión de la traza física (26-11-2026)

> La pasada con 6 puntos armados y 161 hilos observó la entrada al manejador `0x437BC0` y una
> traducción con `r0=0`, 124 ms antes y desde otro llamador. La captura carece de cierre y las
> seis relecturas devolvieron 0 B. Dos pasadas adicionales quedaron con cero puntos armados.
> El origen del `0x1A` de esa sesión sigue abierto. El error de AVI y el fallo del IFO proceden
> del log histórico del 20-10.
>
> Se obtuvo en RAM `idx 10 = 0x31 handle=6 valido=1 OM=6` (5/30 con handle) y `A=B=31`.
> Falló la reproducción de un clip nuevo y de uno antiguo. Falta comprobar el `fn` reubicado,
> el registro del clip nuevo y su persistencia. El paquete 3.97 conserva la guarda que omite
> el alta de `fn` si el sector ya existe.
> [Resultado auditado](../reports/film-pb-1-sector31-resultado-20261126.md).

> **Prueba física con clip nuevo (26-11-2026, 16:33–16:39 CLST).** El PID 144 conservó
> el mismo tiempo de inicio. El sector `0x31` tuvo `handle=0` y `fn=0` antes y después
> de REC y PLAY. `MAH04204.MP4` se grabó, tiene miniatura y decodifica íntegro en FFmpeg.
> En la cámara muestra «No se puede visualizar». El anillo añade `EnterMoviePb`,
> `ff4PlayIf.cpp → 0xB051000B`, `ER_MOVIE_DECODE_FAILED (1600F101h)`, `PauseRelease
> NG: ER_OUTSIDE_RANGE` y `PlayMovie err = MPR::ER_FAILED`. El primer código es el retorno
> interno `0x200` de una consulta usada por audio, vídeo y metadatos. Puede venir del límite
> de tiempo o de una entrada de tiempos ausente. El error posterior de vídeo se localizó en
> `ChgPBAttribute` → `SetPlayStart` → `GetSyncSampleNoByTime`. La captura carece de `startOffsetVT` y del límite
> cargado. [Contraste con el MP4](../reports/film-pb-1-sector31-resultado-20261126.md#9-contraste-del-tiempo-solicitado-y-los-límites-del-mp4).
> [Resultado y evidencia](../reports/film-pb-1-sector31-resultado-20261126.md#8-relectura-física-del-arranque-posterior-26-11-2026-1633-clst).

> **Mismo arranque, contraste del entorno.** DMM activo, con unidades publicadas, y
> microcódigo H.264 de disco igual al de fábrica. El núcleo AV medido tiene 233
> bytes de cambios de captura de fotos. El 3.94 limpio lleva otro `libObj.so`, así que
> cambiaría también el código Linux del reproductor. `0x1600F101` traduce al menos dos
> estados originales del fin de arranque: `0xF1000001` y `0xFB050001`.
> [Huellas y condición de control](../reports/film-pb-1-sector31-resultado-20261126.md#10-respuesta-de-inicio-del-decodificador-y-estado-del-bloque-av).

> **Base verificada para el control AV.** La huella de `nflasha15` medida en la A6000
> coincide con 4.02 sin ISO. El `/system` lógico coincide con la variante de captura
> compartida con 3.93 base. En memoria se comprobó que el control con AV de fábrica
> conserva `/usr` y el resto del contenido, con 233 bytes distintos dentro de
> `AV-CAM.BIN`. Queda pendiente la comparación física.
> [Control aislado](../reports/film-pb-1-sector31-resultado-20261126.md#11-base-de-la-cámara-y-control-que-conserva-usr).

## Reproducción de vídeo — FILM-PB-1 (26-11-2026)

> **Descartado el 26-11-2026: el «modo con movie = 0».** `Type2Mode` (`0x5F699C`) decide solo con
> `(type, subType)` y `m_systemType` (constante 1, escrita solo en `0x5F755C`); no intervienen HDMI, tarjeta,
> batería ni ajustes. Los cinco modos con movie = 0 son trabajos de foto (`Still Rec`→0x03, `Still Pb`→0x06,
> `Still Dubbing`→0x12, `Still Pb RAW`→0x20; 0x13 no se alcanza) y la entrada en reproducción de vídeo
> (`0x437A40`–`0x437AC4`) pide `Movie Pb` y cambia a **0x0E con 20 MiB**. Medida en cámara pendiente: leer
> `0x9DECAC`, `0xA4F478` y `0xA4F4A8` al pulsar play. [Informe](../reports/film-pb-1-sub-modo-camara-20261126.md).

> **Reencuadre del 26-11-2026: la cadencia NO es la causa.** Dos pruebas del usuario con la cámara en mano lo
> cierran: un clip convertido a 25p (`scripts/filmpb1_convertir_clips.py`) da «No se puede visualizar.», y **un clip
> grabado por la propia cámara también**. Un clip propio cumple por construcción todo lo que exige la guarda de
> sistema de TV. Además «Recuperar BD imág.» no cambia el síntoma, la miniatura no aparece y el vídeo sí se lista.
> [Informe de reencuadre](../reports/film-pb-1-fallo-global-pb-20261126.md).
>
> **Árbol de salidas del manejador, verificado instrucción a instrucción** (`FUN_00437BC0`): `[core+0x1F0]!=5`
> → `0x0A`; `[core+0x1F0]==5` y `arg5==0` → `5`; **guarda A** `0x447A1E`=0 → `0x1A` («Pb Disable!! ref) dsm get»);
> **guarda B** `0x447F26`=0 → `0x1A` («Detect UnSupported Content»); `0x447DA8`≠0 y `PbStart`≠0 → código de
> `0x7111B0`. Solo las filas A y B producen el mensaje de la cámara.
>
> **Guarda A descartada con clip propio.** `0x447A1E` es una comprobación de *capacidades por bits* sobre la máscara
> `[core+0xDB8]`; con máscara 0 devuelve 1 (`0x447AC8`→`0x447AE0`). `GetInhInfo` (`0x67B6E0`) rellena 15 palabras y el
> único bit de desacuerdo `TvSystem` cae en `info[0]`, que la guarda de vídeo no lee (lee `info[1]`, máscara 6 ⇒ dos
> `AviMMgr::GetPlayMovieStatus`). No hay ruta que deje basura: `memset` + `0x018000FF`/`0x80000000` en los fallos, y
> `0x80000000` no activa ningún bit consultado. [Guarda A por bits](../reports/film-pb-1-sub-guardaa-bits-20261126.md).
>
> **Guarda B: el fallo está en el lector de metadatos del MP4, no en el contenido.** `isSupportContent` (`0x61A8F0`)
> llama **primero** a `Mp4IfoIf::GetPlayThumbnailInfo` (`0x6E8430`, `0x61A9E4`) y solo después compara `TvSystem`
> (`0x61A9EE`). Y `0x6E8430` **no decodifica ni abre el fichero**: en `0x6E845A` toma el mutex del `mp4Ifo_If`
> (`0x5BAD00`, `ifoFramework_Semaphore.cpp`); si falla, `0x6E846C` devuelve el literal **`0xB0100002`** sin tocar el
> MP4. Ese mutex es un **try-lock no recursivo** cuyo byte `[obj+4]` solo escriben 3 sitios (ctor/release/acquire);
> solo puede estar a 0 si **otro hilo lo retiene** o si el handle quedó **colgante** (el destructor `0x6E81BC`
> libera el semáforo y no limpia el puntero). Un único fallo ahí produce a la vez el `0x1A` de la guarda B, la
> ausencia de miniatura de vídeo y que la duración se tome del índice (`0:02`) en vez del `moov` (9,5095 s).
> [ifoFramework](../reports/film-pb-1-sub-ifoframework-20261126.md).
>
> **Prueba directa del propio firmware (26-11-2026).** El dump `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`
> (1 GiB, **anterior al CFW**) conserva el anillo de log del proceso MPR en VA `0x82DF9300`–`0x82DFC400`, 130 líneas.
> Dice tres cosas que zanjan la discusión: (1) `SetLoadInfo : TvSystem is NTSC, frameRate 3` ⇒ **la cámara es NTSC** y
> los clips son 29,97, así que el «diagnóstico cerrado» PAL era falso; (2) **ningún IFO se carga** —
> `MountCmd : Flash Mount Error`, `mp4Ifo faild … 0xB0800001`, `LoadSub : MP4 Load Error`, `CreateAndLoad Error`
> (`0x31000006`) y `LoadExec : Flash Load Error` en los tres formatos (AVCHD, XAVC, MP4); (3) falla también en foto:
> `[CACHE]BUFFER SIZE TOO SMALL : 00000000`, `Failed to dfs::seek offset=0x0049CE00 errcode=0x0E100001` y
> `Failed to read errcd=0xC3000101`. El intento de reproducción deja `[AVI][PLAY] AviSeqPlay.cpp Error=[ER_BADARG]`
> tras `CS_AviAcsr::Unknown Function[0x20]`. Y el `0:02` queda explicado por
> `[MprCnv] Warning ResumeInfo Structure Size is different! 64 vs 60`. **Causa material: el IFO no se carga del
> volumen.** La guarda A no se cae «por bits» sino por el mismo motivo que la B (`GetInhInfo` devuelve error con el
> `mp4Ifo_If` sin *loaded*), y el mutex del `mp4Ifo_If` es el eslabón que lo hace visible, no la causa.
> **Auditoría del mutex (26-11): no se fuga, pero su destructor tiene un bug real.** Censo completo: 106 acquire y 106
> release en la TU `mp4Ifo_If`, un par por método y **todos** los caminos de salida liberan (CFG por descenso recursivo,
> 106/106); reentrada por `bl` directo: 0 casos. En cambio el destructor `0x6E81BC` destruye aunque el acquire haya fallado
> (`0x6E81E0` cae en `0x6E81EC`), **libera un lock que no posee** (`0x6E81F6`), borra el semáforo tomado (`0x6E81FE`) y **no
> limpia `[handle+4]`**, dejando puntero colgante hasta el `_ZdlPv` del handle (`0x67C78A`, `0x6F1B2E`). Llamadores del
> destructor: `0x67C784` (`DestroySub`) y `0x6F1B28`. Parche mínimo si se confirma: `0x6E81E0: 20 B1 → 80 B9`
> (`cbnz r0,#0x6E8204`). Es decir: un fallo de montaje que haga destruir el acsr deja el `mp4Ifo_If` inservible para el
> resto de la sesión, y por eso el fallo se ve también con un clip recién grabado.
> [Auditoría del mutex](../reports/film-pb-1-sub-fuga-mutex-20261126.md).
> Pruebas sin riesgo antes de flashear nada: miniaturas de **foto**, **otra tarjeta formateada en la cámara**, **formatear la
> tarjeta actual** en la cámara (reconstruye `AVF_INFO`, que es lo que «Recuperar BD imág.» no hace) y encender **sin tarjeta**
> para ver si el aviso es correcto. La A6000 no tiene memoria interna: reproducir «sin tarjeta» no aplica.
> [Informe del log](../reports/film-pb-1-log-real-20261126.md).
>
> **Lo que no es la causa, verificado:** la cadencia (clip propio); el `TvSystem` (sin bits con clip propio); la
> BD/catálogo (la guarda es *fail-open* si falta el registro y recuperar la BD no cambia nada); el decodificador
> H.264 (está **fuera de Linux**, en `av-cam` con microcódigo `ZM_AVCD*` de `/usr/sabin`; su fallo sería posterior a
> `PbStart` y las miniaturas JPEG seguirían saliendo); el `av-cam` del paquete (**no es un binario 3.38**: es el de
> 3.21 + **233 B** de parches integrados (tres estados y Silent r5) + **33 780 B** de PP/S-Log3/B&N
> —32 437 B de curvas, 1 164 B de cuevas, 72 B de ganchos y 107 B de tablas—; `vmlinux.bin` e `initrd.img` son byte
> a byte los de 3.21 y ninguno de sus 25 parches de código cae en códec, muxer, decodificador ni IFO
> ([informe](../reports/film-pb-1-sub-avcam-parches-20261126.md)));
> la NVRAM (64 volcados, sistema de TV fijo); y los parches de código en la ruta de reproducción (auditoría del
> paquete 3.93 `pp`).
>
> **Artefactos listos para probar (nada instalado):** (1) `libmpr.so` con las dos guardas anuladas
> (`0x437BFA`/`0x437C2C` → `movs r0,#1 ; nop`), verificado byte a byte y sin relocaciones en los parches, en
> `build/cfw_bypass_guardas/libmpr.so` — [informe](../reports/film-pb-1-sub-bypass-guardas-20261126.md);
> (2) paquete **con WBI** (arranque caliente, un flag: `build_package_nflasha15.py` sin `--sin-wbi`) — comando y
> dry-run 20/20 en [arranque/WBI](../reports/film-pb-1-sub-arranque-wbi-20261128.md); (3) restauración del 3.21
> oficial verificado (`scripts/camera_reflash_fw321.sh`, SHA-256
> `29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f`); (4) paquete **3.94 con el `av-cam` de
> fábrica 3.21** (núcleo de Sony + el `/usr` del 3.93; `.dat` sha256
> `2a6fd62ff4ed0e63af31a73a2dfb0b261700515147c421f8026b9463dd284c1c`) — [informe](../reports/film-pb-1-sub-paquete-avcam-limpio-20261126.md).
>
> **Prueba de campo decisiva (gratis, 30 s):** encender y pulsar reproducción **lo antes posible**, sin dar tiempo a
> que la galería genere miniaturas. Si así reproduce y luego deja de hacerlo, el mutex se filtra al generar
> miniaturas (dueño vivo); si falla igual, el handle está colgado o el `mp4Ifo_If` no se creó nunca.
> Breakpoint de un solo uso en `0x5BAD24` con `r4`=semáforo: leer `[r4]` (vtable esperada `base+0x8BBCF8`),
> `[r4+4]`, y el dueño `[r4+8]/[r4+0xC]/[r4+0x10]`. Kit: `scripts/camera_filmpb1_trace.py`.

Mecanismo de la finalización fallida **cerrado estáticamente**; causa raíz física, abierta. La traza enlaza
`PlayMovieCmp` (`MPR::ER_FAILED=0x1A`) → `DefObjPlayer::ER_FAILED=7` → bloqueo → caution `0x135` → «No se puede
visualizar». Cadena completa: `MprIf::PlayMovie` (`0x7229E0`, solo log) → `FeaIf::PlayMovie` (`0x44EE9C`, encola la
orden `0x4000001D` con 0x8C bytes) → despachador FeaCore `FUN_00429C38` (`0x429C38`) → manejador **`FUN_00437BC0`**
(`0x437BC0`) → `MoviePlayerIf::PbStart` (`0x307F54`) o finalización `vtable+0x1C(0x4000001D, status)`.
El 0x1A tiene **tres productores** en ese manejador: guarda de capacidades («Pb Disable!! ref) dsm get», `0x437C0A`),
guarda de contenido no soportado («Detect UnSupported Content », `0x437C3C`) y fallo del motor traducido por
`FUN_007211B0` (seis sitios devuelven 0x1A; p. ej. `0x1C00001A`). **No es timeout, RAM ni demux**: si falla una guarda
no se llama al motor. Estado del core obligado: `[core+0x1F0]==5` (si no, el código habría sido `0x0A`).
Falta discriminar el camino (log de MPR o breakpoints de un solo uso en `0x437C0A`/`0x437C3C`/`0x437CFC`).
`0:02` (**corregido el 27-11**): el bloque `PbTimeInfo` está en modelo+**0x534**; `m_durationOfContent` en
modelo+0x5AC/0x5B0/0x5B4, `m_pbTimeInContent` en modelo+0x594/0x598/0x59C y `m_framesOfContent` en 0x5CC (lo de
0x90…0x108 era `PbStatus`, estado y no tiempos). El catálogo queda **descartado** como fuente
(`GetMovieContentProperty` solo lo usa el volcado `0x7258F8` y `libObj` no importa `GetContentDuration`); la
hipótesis viva es que el `0:02` sea el **punto de reanudación** (`Get/SetContentResumePoint` `0x8CAE60`/`0x8CB4B2`).
El MP4 no contiene ningún campo de ~2 s (ffprobe y parser propio). No hay prueba de causa DMM; los mapas externos
históricos contienen los cinco tipos AVC (conservar [G111 §14.5](gui/g111-film-receta-gui-iconos.md#145-mapa-externo-recuperado-y-selector-de-tipo-avc)).
[Informe de cierre estático](../reports/film-pb-1-productor-mpr-20261126.md) · [traspaso físico](../reports/film-pb-1-traspaso-20261125.md).

**Auditoría del CFW instalado (27-11-2026): la causa no es un parche de código.** El paquete 3.93 `pp` no incluye
`libmpr.so` (el productor del `0x1A` es de fábrica) y sus 32 ficheros distintos de Sony 3.21 son 5 bibliotecas con
parches de Picture Profile/Silent y 22 tablas de textos. En `libObj` cambian 506 B en 41 rangos: 26 en `.text` en los
puntos de `patch_libobj_pp*.py`/`patch_libobj_eco.py`, y fuera de `.text` solo la cabecera ELF, seis entradas de la
tabla de descriptores PP en `.data.rel.ro` y `DT_REL`. **Ninguna** de las doce direcciones conocidas de la ruta de
reproducción cae en un rango modificado y el mapa de errores `0xFD9248` (97 × 16 B, con `0x1A → 7`) es idéntico.
Quedan dos hipótesis: estado de arranque (el paquete quita `nflasha5`/WBI ⇒ arranque en frío) y contenido/catálogo
(el firmware documenta que la base de datos de imágenes gobierna la reproducción de películas). Discriminación:
breakpoints en `0x437C0A`/`0x437C3C`/`0x437CFC`, «Recuperar BD imág.» y, si no, restaurar el 3.21 oficial.
[Informe de auditoría](../reports/film-pb-1-auditoria-cfw-20261127.md).

**Nueve investigaciones en paralelo (27-11-2026): el diagnóstico queda en tres hipótesis medidas.** Quedan dos
guardas reales (A: `GetPlayMovieStatus` `0x60945C`/`dsm`; B: `isSupportContent` `0x61A8F0` → `vtable+0x58` sobre el
objeto de medios) y el motor (`AviMMgr::MovieReadStart` `0x608698`); el traductor es ELF `0x7111B0`, no `0x7211B0`,
y solo 6 de 65 536 entradas dan `0x1A`. `PbStart` (`0x307F54`) devuelve 0 siempre según el análisis del motor, así
que la rama `0x437CFC` sería muerta y el `bl` vivo es `0x437C7E`. El índice de películas está en la **raíz del
volumen**: `AVF_INFO\AVIN0001.INP` (+ `.BNP`, `.INT`), con `nDuration` en ms y `Duration90kHz`; `M4ROOT\MEDIAPRO.XML`
es la BD XAVC. El MP4 es **conforme** al grabador (MSNV minor `0x015A0070`, uuid PROF/USMT/MTDT, `moov` al final,
1440×1080 anamórfico): reempaquetar no ayuda. El arranque en frío pierde fuerza (el WBI no cubre `av-cam` y el
manejador no consulta el modo). Los logs son 4 líneas incondicionales a stdout de `im.elf` (búfer `0x83400000`), con
regla de decisión por línea. Kit de medida listo y probado en seco: `scripts/camera_filmpb1_trace.py`.
[Camino final y plan P0–P3](../reports/film-pb-1-camino-final-20261127.md).

**Montaje y carga del IFO, cerrado estáticamente (26-11-2026).** Los cinco literales del anillo salen de `libmpr.so` y
tienen emisor único: `MountCmd : Flash Mount Error` (`0x8EA305`) lo imprime `AviMMgrCmd::MountCmd` (`0x626DB8`, gemela
con *driveLetter* en `0x627020`) en `0x626F18`, solo desde el bloque de error común `0x626F08`, al que se llega por
`FlashMount()`≠0 (y ≠`0x31001001`) o por «media fuera + salvage» con `0x31000002`; `GetDeviceInfo : ER_SEQUENCE  DEVICE
Unmounted` (`0x8E9EAA`) sale de `0x625C7A` cuando `[this+8]->vtbl[0x140]()` devuelve 0 (registra `0x31000007`);
`FlashLoadMp4 : CreateAndLoad Error` (`0x8EA6B8`) sale de `0x627C86` cuando `MMgrMp4IfoAcsr::CreateAndLoad` (`0x67CA6C`)
devuelve ≠0 (línea 13247, `0x31000006`); `Err RcsBackupTblData` (`0x823999`) sale de `0x3AFB2C` cuando
`RcsBackupTblData()` devuelve un código con cabecera `0x10` y **no** marca salvage; `CheckSalvageStatus` (`0x90A075`) es
el nombre que `MMgrAvcHdIfoAcsr::CheckSalvageStatus` (`0x671DAC`) registra en la línea 791 con el código de
`hdAvcIfo_If::CheckSalvageStatus` (`0x5AD53C`). **Los códigos están resueltos por tablas del propio binario:**
`0x31000001 ER_OK`, `0x31000002 ER_INVALID_PARAM`, `0x31000003 ER_FAILED`, `0x31000006` = **`MMgrGlobal::ER_CMD_CONFLICT`**
(rama **por defecto** del traductor `0x64E300` en `0x64ECEC`: «error de subsistema no clasificado»), `0x31000007` =
**`ER_INTERNAL`** (precondición interna), `0x31000008 ER_SEQUENCE`, `0x31001001 ER_DIFFERENT_DEVICE_TYPE`,
`0x3100200C ER_NOT_MOUNTED` (tabla `{nombre,código}` en `0x8F6CA8`); `0x32400001` = `ER_FAILED` de AVI (mapper
`0x1DA818`); `0xB0800001` = fallo **genérico** de `mp4Ifo` (traductor `0x6F0D4C`: `0x6F0E40` para `0xXX100000` y default
`0x6F0EBC`); `0xA0100003` = comando HD-AVC `0x4E` fallido en la capa de comando (`0x520BFC`, fuera de la lista de
códigos «esperados» de `0x5215AC`, de ahí el banner). **Orden obligado:** estado de dispositivo → `FlashMount`/DFS
(`0x3BB220`; éxito ⇒ `[this+0x140]=4` vía `0x64C5DC` en `0x626960`) → `CheckSalvageStatus` (estado AVI ∈ {2,3,4,6}) →
gate `0x64C298` con `state==4` → `CreateAndLoad` → `CreateSub` → `LoadSub` → `Load` → `mp4Ifo_General::Load` (FLASH) →
`FlashLoadForMsv` → `RcsBackupTblData`. **Corrección 26-11-2026 (bytes):** `RcsBackupTblData` (`0x35EA1C` → `0x35E04C`)
**no abre ningún fichero**: hace un `BkRead` de un pack de sectores por `(userId, backupId)` (`0x2B39B8` → `0x2B2F48`
→ `0x2B3948`) y devuelve `0x10xxxxxx` cuando esa entrada no tiene reader (`0x2B39EE` → `0x2B3A28`); **no** prueba
«volumen ilegible» ni ausencia de `AVF_INFO`. **Consecuencia:** `0xB0800001` y `0x31000006` son códigos por defecto y no
identifican causa; el desajuste lógico del journal es `" Need Salvage"` (`0x00500003`), y el `INP` ausente se ve por la
reconstrucción del índice, no por `Err RcsBackupTblData`; un IFO corrupto pero legible daría un código específico
(`0xB0400005`, `0xB0510001`, `0xB0F30001`…). Los ficheros del índice son `AVF_INFO\AVIN0001.INP` (primario), `.BNP`
(respaldo) y `.INT` (tabla interna); `PRV00001.BIN` es propiedades. [sub-rcsbackup](../reports/film-pb-1-sub-rcsbackup-20261126.md). **No verificado:** identidad de las virtuales `vtbl[0x140]`/`[0x60]`/`[0x168]`, cuál de las dos vías de
`MountCmd` disparó la línea del anillo (el anillo no es transcripción completa: falta `MountCmd : `) y semántica nominal
de la cabecera `0x10`. [Informe de montaje/IFO](../reports/film-pb-1-sub-mount-ifo-20261126.md).

## Estado global (actualizado 03-11-2026)

- **Cámara recuperada (03-11-2026):** con autorización física expresa, se accedió por SWD al BIONZ (R46/R47), se confirmó en la propia
  cámara la causa de R36 (P2 `CFG_E:Load file` devuelve −302 al cargar `\sabin\idt_cam.bin` de `nflasha3`, [R47 §15](capture/e26-r47-primer-contacto-swd-lectura-ram.md)),
  y se forzó por SWD (solo un registro de CPU durante el arranque, sin escribir NAND ni memoria) que Loader3 entrara al actualizador
  de fábrica intacto de `nflasha1` ([R48](capture/e26-r48-plan-recuperacion-actualizador-swd.md)). El actualizador oficial de Sony instaló
  el 3.26 (tras un primer intento cortado al 45 % por un NG de Darwin, `0x1063`/LED `0x63`, reintentado con éxito) y restauró `nflasha3`.
  **La cámara arranca en modo normal y reporta firmware 3.26.** Cierre completo en [R49](capture/e26-r49-cierre-recuperacion-326.md).
  Las entradas siguientes describen el estado previo al bloqueo, mantenidas como historial de diagnóstico.
- **Cámara bloqueada tras instalar el 3.25 integrado** (Done en el actualizador; LED 3 lentos + 2 rápidos = −302 de Loader3 por inferencia,
  [R13](capture/e26-r13-led-error-provenance.md)). Testimonio del usuario; sin captura UART ni lectura de NAND. Prioridad: recuperación offline
  ([E26-RECOVERY](capture/e26-recovery.md)); ningún acceso físico autorizado.
- **Objetivo de recuperación:** solo `nflasha3`; con Done su CRC releída coincide con la imagen 3.25 y existe copia válida del 20-10-2026
  ([R30](capture/e26-r30-updater-done-boundary.md)). Falta la vía de escritura.
- **Vía serie del BootROM:** se abre en cada arranque (`MODEREG[15:0]=0x0003`, [R32](capture/e26-r32-moderreg-valor-real.md)), pero exige la
  clave guardada en `nflasha0`, nunca volcada ([R33](capture/e26-r33-veracidad-clave-nflasha0.md)). Protocolo completo y emulado:
  [R9](capture/e26-r9-bootrom-ram-execution.md), [R21](capture/e26-r21-bootrom-rx-serie.md)–[R23](capture/e26-r23-bootrom-flujo-completo.md),
  [R34](capture/e26-r34-serial-entry-flags.md), [R35](capture/e26-r35-serial-receiver-multi-paquete.md).
- **Causa del bloqueo: identificada offline** ([R36](capture/e26-r36-causa-fallo-325.md)). El 3.23 y el 3.25 difieren solo en Darwin y
  en `nflasha3`/`part_image.sum`, y Loader3 solo lee `nflasha3`. El `nflasha3` del 3.25 incumple el formato que exige la ruta
  Loader3 → ARM7 → LDEC: tiene residuo 256 en 359/369 bloques (Loader3 lee sectores desde `off>>9` y el residuo no llega al LDEC) y los
  bloques 0, 48 y 57 son un único registro de 64 KiB, cuando el LDEC se programa con 16 de 4096 B (73 732 B, por encima de la cota de
  Sony de 65 800 B). Las 16 imágenes de Sony del repo (19 489 bloques) siempre tienen residuo 0 y 16 × 4096 B. La primera lectura de
  la partición (bloque 0) y la primera entrada del RAMCFG (bloque 240) caen en bloques defectuosos y dan −302. Corrige la decisión C de
  [R16](capture/e26-r16-ldec-hardware-audit.md)/[R17](capture/e26-r17-arm7-ldec-segment-analysis.md) en cuanto al residuo. La UART no puede confirmarlo
  (consola apagada por `Backup[0x510015]=0`, [R37](capture/e26-r37-cierre-estatico-recuperacion.md)).
- **Recuperación (R37):** solo el modo 3 de Loader3 evita `nflasha3`, y solo lo fija `\updater\mode` en `nflasha2` (corrige R26 §1.2). Con ese
  archivo, Loader3 arranca el actualizador de fábrica de `nflasha1` y acepta firmware por USB; el paquete 3.26 (contenido oficial) está preparado.
  Crear el archivo exige escribir la NAND: sigue siendo físico. **R38:** el guard de `sauu` compara con `\updater\dat4`, que `CompleteUpdate`
  pone a la versión del FDAT → con el 3.25 instalado acepta el 3.26. En el volcado del 20-10 basta recuperar una entrada `MODE` borrada
  (1 byte, sector 132 de `nflasha2`; [R38](capture/e26-r38-guard-y-entrada-updater.md)). **R39:** el fallo se reproduce en emulación
  (código real de Loader3/ARM7, LDEC modelado); `nflasha` es lógico de MuMin, así que ese byte se escribe desde el BIONZ, no con lector externo
  ([R39](capture/e26-r39-estatico-profundo.md)).
- **Hito previo:** con el 3.23 (Darwin tipo 0 + B1a) la cámara disparó en silencio y sin error según el usuario (T040, 27-10-2026).
- Resumen por informe E26 (R1–R35): tabla en [CURRENT § E26](../knowledge/CURRENT.md); versión anterior de este encabezado, con un bloque por
  informe, en [STATE-historial-2026-10-31](history/STATE-historial-2026-10-31.md).

Estado técnico **consolidado**: conclusiones vigentes, rectificaciones y límites. No es historial ni lista de tareas:
cada afirmación enlaza al informe canónico donde está comprobada. Tareas y sus estados: [PENDIENTES](PENDIENTES.md) (única fuente).
Informes por tema: [INDEX](INDEX.md). Cronología: [PROGRESS](../knowledge/PROGRESS.md). Contexto mínimo para agentes:
[CURRENT](../knowledge/CURRENT.md). Rectificaciones completas generadas del grafo: [CORRECTIONS](CORRECTIONS.md); preguntas abiertas: [OPEN-QUESTIONS](OPEN-QUESTIONS.md).
La versión anterior de este archivo (instantáneas S44–S348 y bloques por fecha, íntegra) está en
[history/STATE-historial-2026-10-26.md](history/STATE-historial-2026-10-26.md).

## Estado estático y decisiones (auditoría del 26-10-2026; anotado el 31-10-2026)

Estas decisiones describen la evidencia estática. Después se instalaron el 3.22 (T024), el 3.23 (T040, captura silenciosa confirmada
por el usuario, sin medida física archivada hasta el 31-10) y el 3.25 (bloqueo): «no es instalable» se refiere a la falta de recuperación
demostrada, no a que no se instalara. Sigue sin demostrarse estáticamente la capacidad o la imposibilidad de fotografía totalmente
electrónica a resolución completa.

- **S51: A=NO, B=NO, C=NO** ([decisión](capture/s51-decision.md)): sin ruta demostrada, sin base para un parche, sin prueba de imposibilidad.
- **E25-04: A=NO, B=NO, C=NO, D=NO, E=SÍ, F=NO, G=NO** ([informe](capture/e25-04-recuperabilidad-y-decision.md)): no hay recuperación
  independiente de Darwin demostrada (ni USB, ni bootloader sin la aplicación, ni hardware verificado); B1a **no es instalable**.
  R1 tiene procedimiento y manifiesto (62/62 archivos, `verify` OK contra el origen), pero **la copia externa no está hecha ni verificada**.
  **E25-05**: paquetes 3.23 (tipo 0 + B1a) y 3.24 (recuperación) preparados y verificados offline en directorios separados
  ([informe](capture/e25-05-preparacion-paquetes-323-324.md)); el rollback 3.24 solo sirve con acceso al actualizador.
  **E25-06** ([auditoría independiente](capture/e25-06-auditoria-independiente-paquetes.md)): ambos paquetes binariamente correctos
  (145 comprobaciones, 0 fallos; N=SÍ), pero la instalación no se puede declarar segura (O/P/Q/R=NO). Antes de instalar, comprobar el SHA-256 (E25-07).
- Estáticos cerrados con límite: E2–E5, E7, E8, E10 (a–c), E12, E14–E20, D1, D3, D4 y D6 ([evidencia](capture/s403-cierre-pendientes.md));
  E1 `NO_VERIFICADO` sin vías estáticas. Bloqueados por datos o hardware: E6, E9, E11, E13, D5; físicos F1–F6 (P1–P4, P6, P13–P16, P18–P21 ejecutadas el 26-10-2026 por USB (T001–T021, [registro](capture/registro-pruebas-camara.md)); P5/P11 caen con F4, P7/P17 descartadas; E22 cerrado con límite ([informe](capture/tipo2-analisis-estatico-2026-10-26.md)));
  respaldo R1 parcial (procedimiento y manifiesto; falta copia externa verificada), R2 cerrado, R3 y R6 cerrados (historial reescrito el 31-10-2026); R7 bloqueado (copias antiguas en `refs/pull/*` y en un fork ajeno).
- Datos de auditoría y memoria temporal: [estado.json](../knowledge/audit/estado.json), [memoria.json](../knowledge/audit/memoria.json)
  (`scripts/audit/repo_audit.py`). Viabilidad por escenarios (17-10-2026): [estado-y-viabilidad](estado-y-viabilidad-2026-10-17.md).
- Los 133/372 del censo miden **documentación de etiquetas**, no código recuperado ni funcionamiento ([matriz de cobertura](capture/s51-static-coverage-and-tool-limits.md)).

## Conclusiones técnicas vigentes

Etiquetas: **V** = VERIFICADO (bytes/instrucciones), **I** = INFERENCIA, **N** = NO_VERIFICADO.

**Selector EFCS / Electronic (E25-24):** **implementado offline** ([E25-24b](capture/e25-24b-implementacion-selector.md)).
El ajuste EFCS (`0x2b4`/`0x2b5` → `+0x210` 0/1) selecciona la modalidad; BIONZ copia
`cap+0x41c` a `pkt[0x0e]` y Darwin sustituye B1a/tipo 0 por una compuerta por captura
(`0x20c78`/`0x1fe6c` → cave `0x4318`): con 0 ejecuta `0x1b080` original (segunda cortina),
con ≠0 devuelve 0 (sin P4D/P4E ni motor). Parches con bytes, manifiesto, reversión y emulación
Unicorn. **E25-25** reubicó la cueva BIONZ (`0x43541a80` → `0x43541800`): la zona antigua es
un objeto de 512 B con entrada GOT (`0x44020f00 → 0x43541900`, también en A7S), no relleno.
**E25-26** integra C3-B (enganche `0x438c82fe`, cueva `0x43541840`): en Electronic normaliza
`shd −= VTS`, `svd = 0`, `ShutMode = 0`; EFCS queda idéntico al original en emulación. La
validación física es E25-27. El informe de integración EFCS tenía contradicciones de
`r5`/enganche/mecanismo: resueltas en E25-24b §6bis. **E25-29** construye el firmware
integrado 3.25 sobre los originales 3.21 (selector + C3-B + Darwin) y lo verifica
offline: contenedor FDAT/DAT, extracción inversa y emulación integrada; no se ha
instalado ni ejercitado el guard/arranque ([E25-27](capture/e25-27-construccion-firmware-integrado.md)).

| Tema | Conclusión vigente | Estado | Fuente |
|---|---|---|---|
| RecordStill / RecordImage | A6000 `0x90b248` = RecordImage (sus diagnósticos lo dicen); pareja A7S `0x84a568`. RecordStill A6000 `0x908afc` ↔ A7S `0x847e1c`; RecordImage llama a RecordStill en ambos. Equivalentes salvo líneas de log (199 pares) | V | [contrato](capture/recordstill-contract-audit-2026-10-23.md), [S402](capture/static-closure-2026-10-25.md) |
| Llamadores | BL `0x90de2e` y `0x91634e`; 25 punteros Thumb a `0x90d7e8` son `call_fn` de `StateMgr::_FuncEntry`; `StateMgr::CallFunc` los ejecuta con `blx r3` (`libmprctrl.so:0x1cef2`); `0x91631e` es tabla TBB | V | [S382](capture/s382-recordstill-callers.md) |
| Activación real de la captura | Qué dispara RecordImage en ejecución, equivalencia de todos los callees y ocho parejas locales de RecordStill (43 llamadas mapeadas: 20 importadas, 23 locales) | N | [seguimiento](capture/capture-static-followup-2026-10-25.md) |
| Cola `0x40193` | ID construido desde literales `.text` (LDR); 16 B hasta `osal_snd_msg`; receptor LIRO `0x4381d16c`, tabla `0x44000174` (35×12 B); instalador `0x4379e93c` → descriptor `0x43ea048c` (campo `+0x14` = `0x46`), fila 189 de 372 punteros Thumb, bucle `0x4356082c`; servicio `+0x3c` = `sta_tsk`; recepción bloqueante. Ejecución real de la cabecera LIRO no observada | V / N | [flujo](capture/queue-40193-flow-2026-10-23.md), [S384](capture/s384-queue-id-0x40193-search.md) |
| Mensaje `0x10000005` | Dos constructores (PlayData y secuencia `0x3026`); único `ObjMsg(0x3a49,0x3026)` = `0x659cb0` (acción 13 de `ModelScalarPb`); local `0x109` auto-publicado (`0x65a8a4`); quién publica `4`/`2` a Pb/PbCap: ningún código de `libObj` | V / N (E1) | [S402](capture/static-closure-2026-10-25.md), [E2](capture/s403-e2-productores.md) |
| Estado IMX210 (gates) | Objeto `0x43f72d02` (A7S `0x43f7bce6`): gates `+3/+6` idénticos y sin escritor; Backup `0x3000b` = 256 B, gates a 0; escritor `S[0]` y copia G→S resueltos (`0x44020c9c → 0x43eb35d0`); 7 de 14 lectores cuelgan de la captura | V / N valores | [S300](capture/s300-state-xref-sweep.md), [S301](capture/s301-a7s-state-xref-sweep.md), [S205](capture/s205-imager-s0-writer.md), [S403](capture/s403-cierre-pendientes.md) |
| Mecanismo por modo (carril B) | `modo → matriz 69/59 filas → T1/T2/T3 → pares (flag,bit) → máscara u16 → MMIO DFE/CISIF (0xfc02a00c)`; mismo código en A7S y A6000, la diferencia son datos (34 vs 13 modos; 7 vs 15 vectores de registro). Identidad de `0xf292b000..8` y significado de `w0` | V / N | [S341](capture/s341-synthesis-b2.md), [S332](capture/s332-a6000-tables.md), [S333](capture/s333-mode-vocabulary.md) |
| `0x43fef404` | Tabla de ids de `Camera::Lens::ODL` (69 entradas A7S/A6300, 47 A6000), `0x000d` = capacidad 13; callback = adaptador de `memcpy` (13 B, I alta). No es tabla de tiempos | V / I | [S342](capture/s342-fef404-consumers.md), [S347](capture/s347-odl-field.md), [S348](capture/s348-odl-callback.md) |
| Silent en A7S | UI → LIRO `0x40e3` (existe también en A7S) → `+0x250` → bit `0x20`; conmutación IMX210 modos 0–4 / IMX235 0,1,3,4; la A6000 no tiene el selector ni el bloque de tiempos de la A7S (código ausente) | V | [S401](capture/s401-a7s-silent-control-path.md), [S402](capture/static-closure-2026-10-25.md), [S309](capture/s309-chain-presence.md), [S312](capture/s312-cluster-consumers.md) |
| Exposición electrónica (E25-14) | Cadena Silent del IMX235 reconstruida: `cap+0x648` → `SetExposure` (`0x436f4168`, `param+0`=SHR/líneas, `param+9`=ShutMode) y `cap+0x6b0` → método de velocidad (`0x436f4a94`, `vtable+0x30`) → bloque de comandos. La A6000 tiene el mismo contrato (`0x436d6f6c`/`0x436d7e08`) y la misma tabla (30 filas idénticas), y **ya llama al método `+0x30` en la foto** (`0x438c831e`); lo que no usa es ShutMode 0. El armado de exposición larga del A7S (`0x436f43c0`, `obj+0x3dc=2`, `0x43b73044(0xe)`, tercer argumento `r3`) **no tiene equivalente en el método del IMX210**. El límite de ~65 ms es también del firmware (clamp a un cuadro); >1 cuadro no demostrado | V / I / N | [E25-14](capture/e25-14-imx235-imx210-exposicion-electronica.md), `tests/test_e25_14_exposicion.py` |
| Exposición (E25-15) | `SetExposure` (`0x436d6f6c`) escribe `blk+0x50..0x57` (r5 en `+0x52`, ShutMode en `+0x57`); el método `+0x30` (`0x436d7e08`, "SetRead") escribe `blk+0x66..0x6c` y 4 pares de cfg, no recibe r5/ShutMode y no puede sobrescribir la integración. La emulación A/B/C reproduce el mismo bloque `+0x30` y solo cambia r5/ShutMode; la medición T046 (misma r5, 1/250 vs 1/30, misma exposición) confirma que **ShutMode 0 + r5=1 sigue en cuadro completo** y que r5 es imprescindible. El bloque `+0x30` es un **código de posición 0..4095** (conversión `0x436d8a90`, compartida con `+0x34`/SetReadZ), no el Tv: **corrige E25-14 A**. >65 ms/bulb/30 s sin mecanismo demostrado | V/I/N | [E25-15](capture/e25-15-shutmode0-temporizacion-nativa.md), `tests/test_e25_15_shutmode.py` |
| Exposición (E25-16) | **Productor nativo de `r5`:** `0x4383fa40(record, imager)` lee Tv de `record+0xf6`, período de línea de `record+0xc`, VTS de `record+0x20`, suelo de `record+0x1c` y multiplicador de `imager+0x4b8`; escribe `r5` en `+0x64` y ShutMode 0 en `+0x6d`. Lo llaman el constructor normal (`0x437b46d0`, compuerta `cap+0x11b0`) y el EFCS (`0x438417c0`); la foto medida no lo usa (r5=1). `0x4383fd6c` copia `record+0x64..0x73` a `cap+0x64c` y `0x438c828c` llama a `0x437f8a50` y a `0x436d6320` (vtable +0x28). Emulación con VTS 4219: T047 ±1 línea; con 4266: 47 líneas (0,71 ms) de desviación. 1/15 y mayores saturan a 0 (negro); >1 cuadro/bulb/30 s sin mecanismo. No se hardcodea 4219: se usa el campo `record+0x20`; su valor real no se verificó | V/I/N | [E25-16](capture/e25-16-r5-autonomo-fotografia.md), `tests/test_e25_16_r5_autonomo.py` |
| Exposición (T052-B0) | **No ejecutada físicamente** (cámara inaccesible). **VTS:** `record+0x20 ← cap+0x5e0 ← [descriptor+6]`; `ctx=0x43eaadd8`, descriptor `0x43ea13dc`, `+6=0` en reposo; el escritor/selector de foto no se localizó y el VTS de foto sigue **N**. **Predicado:** `0x43deb360` es el bloque 5 (`0xbc0005`) de 10 bloques de 0x100 B copiados de Backup/NVRAM (`0x74218`, SHA `2a42df46…e370`, `+0x10=0` en 12 backups 3.21–3.22 (pre-B1a; B1a no toca BIONZ) y en RAM); no se encontró escritor directo de `+0x10` en `av-cam`; el cuadro extra está activo y el `r5` nativo es inválido (8422/8175/7341). `record+0x68` se copia a `param+4` = `svd` (ID3/ID4; corregido por E25-17: no es una «ventana»). **C3-A no autorizable; C3-B preferible:** `r5 = 4219 − record+0xf0` es independiente de VTS/predicado y reproduce T047 (4203/3956/3122). Recolector listo; falta B0 físico | V/I/N | [T052-B0](capture/t052-b0-vts-predicado-fotografia.md), [T052-A](capture/t052-a-parametros-reales.md), `tests/test_t052_b0.py` |
| Integración Silent de todo el rango (E25-18) | **Decisión C (offline, sin cámara):** una fórmula (productor `0x4383fa40` normalizado frente al predicado: `shd−VTS`, `svd−1`) con dos rutas: rápida 1/8000–1/30 (= C3-B, enganche `0x438c82fe` confirmado) y larga 1/15–30 s (cálculo reproducido; requiere VTS dinámico, `svd` multicuadro y un 2.º punto sobre `record`, no demostrados). Sumidero físico del VTS: no encontrado. BULB: `0x8000` = callbacks de temporizador. [E25-18](capture/e25-18-integracion-silent-todas-velocidades.md) |
| Fin de exposición y cronómetro (E25-19c) | **Mensaje de fin = Darwin→BIONZ `0x0e` (3,3)**; Darwin recibe Tv en `pkt[2..3]` del `0x0c` (3243=10,07 s leído) y cronometra con cortina; `cap+0x728` = cronómetro de 32 µs (2/4/8 s pedidos → ≈1,59/4,00/10,07 s reales); `cap+0x744` no son segundos; rama de host `74f=0` sin observar; fin electrónico/`SetExposure` no demostrados | V/F/I | [E25-19c](capture/e25-19c-fin-exposicion-mensaje-temporizador.md), `analysis/e25-19c/` |
| Origen de `cap+0x74f` y rama de host (E25-19d) | **Tres escritores directos**: copia del plan (`0x438acc9c`), `0` por arranque rechazado (`0x437df5e8`) y `0` por cancelación (`0x438c2562`). Con `74f=0` BIONZ omite 21 esperas CAIF y sub 9 espera el flag `0x13:0x100000` de un temporizador de 32 µs (1/8000–30 s emulado, sin overflow; mismo Tv que el `0x0c`). Es ruta de error/cancelación, sin efecto en el sensor y sin liberar a Darwin: **decisión B**. Procedencia del 1 sin resolver (E25-19e) | V/E/I | [E25-19d](capture/e25-19d-origen-74f-rama-host.md), `analysis/e25-19d/` |
| Selector 3/4 y origen del `74f=1` (E25-19e) | El `r6`=3/4 de `0x438c83ce` llega a `0x436c74c8`, método del controlador VD/imager (`0xf3120000`): 3 y 4 difieren en `+0x208` bit0, `+0x258` y una llamada virtual; no es un comando al IMX210 y su efecto en la integración no está demostrado. `W1` no puede copiar un 1 (`plan+0x142` par); 19d omitió stores `strh@74e` en `EndExps`/secuenciadores; `74f` puede ser el byte alto de un halfword de geometría. Lectura física: `74f=1` constante, `74d` 1→0 al terminar. `G+0x60/+0x7e/+0x7f` sin escritor. Decisión B; origen del 1 sin cerrar (E25-19f) | [E25-19e](capture/e25-19e-origen-74f-selector-sensor.md) |
| Verificación física de exposición larga (E25-19, T053) | **Decisión C (físico, solo lectura):** fotos normales 1/30–30 s con `shd=1, svd=0, r5=1, ShutMode=3, lineas=0, d8/da/dc=0`; VTS real **4176**, período **4096** Q8, predicado byte 0; 20 s y 30 s completas y estables; `cap` sin cadena demostrada (no leído), mecanismo de la exposición larga sin identificar; BULB no probado | O/I/N | [E25-19](capture/e25-19-verificacion-fisica-exposicion-larga.md), `analysis/e25-19/` |
| Exposición larga y BULB (E25-17) | **Decisión C (estática, sin cámara):** el productor `0x4383fa40` codifica exposiciones de 1/15 s a 30 s como `shd=1`, `svd=cuadros−1` (ID3/ID4) y VTS ampliado del cuadro con resto (`record+0xd8` → `record+0x60` por cuadro); emulación: 1 s → `svd 14`, 30 s → `svd 472`. El contador de pasos del host no es el mecanismo (`StartExposure` anula `cap+0x650` si `cap+0x740==0`). BULB/largas con obturador mecánico: tramos de un cuadro cronometrados por el host (`0x438c74b0`, `bulbFrameCount=cap+0x72c`, objetivo 0 = sin límite; flag `0x8000` = parada externa). LongObMode = parámetro OB/DFE (mensaje `0xf013`); SetReadZ = `SetRead_ZAF`. No hay medición física de `svd`, del sumidero del VTS ni del fin de integración; C3-B se engancha en `0x438c82fe` | V/I/N | [E25-17](capture/e25-17-bulb-exposicion-electronica-larga.md), `tests/test_e25_17_long_exposure.py` |
| `…ForLiro` | 216/221/240 nombres; soportados 0/0/6 (A6000/A7S/A6300); los cinco de obturador rechazados; `SetShutterTypeForLiro` solo en A6300 | V | [S174](capture/s174-forliro-api.md), [S383](capture/s383-forliro-silentlibobj.md) |
| `[EXL]` | Puede rechazar una captura (`hsiz_arcout > 2240`, `arcout > arcin`); entradas por modo de disparo solo en ejecución | V / N | [S403](capture/s403-cierre-pendientes.md) (E20) |
| Cortinas | P4D=1ST_CURTAIN_MG, P4E=2ND_CURTAIN_MG, P4C=CA_1ST_CURTAIN_START, P4B=CA_RELEASE_LOCK_MSS (no son serie); el enlace banco/bit `0xf2910048` → P4E no consta en el firmware | V / N (E11) | [fm3-gpio](capture/fm3-gpio-shutter-mapping.md), [S50](capture/s50-parallel-conclusions.md) |
| EFCS → sensor | Recorrido estático cerrado hasta IMX210; `CURTAINMODE 0xce` no gobierna el sensor (T1); SilentShutter `+0x238` sin lector de captura en `av-cam`; fin electrónico de integración sin identificar | V / N | [efcs-capture-selector](capture/efcs-capture-selector.md), [S51](capture/s51-decision.md), [S58](capture/s58-conclusions.md) |
| PMCA | `updatershell` inyecta un fdat propio (guard CRC + modelo/región/versión **sin firma**); `bk w 0x003e0005` escribe la propiedad `modelName` (`ILCE-6000` de fábrica); el efecto «shell mode» de `ILCE-6001` es no verificado | V / N | [S62](capture/s62-pmca-injection.md) |
| Patrón de logging | La fw3.21 reescribe etiquetas de trazas, no funcionalidad (9+ ejemplos); la presencia de una cadena **no** prueba una funcionalidad | V / I | [S128](capture/s128-label-map.md), [S130](capture/s130-new-modules.md), [S174](capture/s174-forliro-api.md) |
| Arranque y recuperación (E24-01) | Darwin (IC5700) es también el **control de energía**: `darwin_core` sube `DD_ON1/2/3` (núcleo y LPDDR2 del BIONZ). **No está demostrado** que el actualizador USB arranque sin `darwin_core`. El script del actualizador ignora el resultado de `ud_darwin_init`. La entrada por pmca exige el sistema normal (batería vía `upm`) | V / I | [E24-01](capture/e24-01-arranque-recuperacion.md) |
| Recuperabilidad y B1a (E25-04) | **No hay recuperación independiente de Darwin demostrada**: ni USB (depende de `DD_ON*`), ni acceso al bootloader sin la aplicación, ni hardware verificado; solo el puerto físico (`MD0_DWN`, `XDWN_RESET`, UART, SWD, `CN4906` no montado) está documentado. El plan de versiones se revisa en E25-05: prueba 3.23 / recuperación 3.24, ambas preparadas y verificadas offline; el 3.24 solo sirve si la cámara conserva acceso al actualizador y no recupera un MCU que no arranca. R1: procedimiento y manifiesto listos (62/62, `verify` OK contra el origen), copia externa sin verificar. L0 no tiene contradicción estática con BIONZ (estado 9 libera el bit 24, el 10 es terminal, mensajes de la máquina de captura, estado 31 sin cambio); P29, `pkt[2..3]` y el lector BIONZ del fin siguen abiertos. **B1a no es instalable** | V / I / N | [E25-04](capture/e25-04-recuperabilidad-y-decision.md) |
| Paquetes 3.23/3.24 (E25-05) | **3.23 (B1a) instalado en T040 (27-10-2026, cámara en 3.23; funcionamiento confirmado por el usuario: dispara en silencio y sin error, sin capturas archivadas); 3.24 preparado**: 3.23 = tar oficial + B1a (`55a366a5…`) + `darwin.sum` (`cf930ac9`); 3.24 = payload oficial extraído del 3.23 verificado, versión BCD `0x24`. Modelo `0x41030035`, región 0; 69 comprobaciones sin fallos (DEND, CRC de cabecera, sumas por bloque, hashes, `unpack`). B1a vs tipo 0 = exactamente 2 bytes (`0x1fe6a: 28 46 → 0a e0`); tar experimental solo cambia los dos ficheros Darwin; 3.24 vs 3.23 solo difiere en cabecera y CRC DEND. El antiguo `recuperacion-323` queda obsoleto | V | [E25-05](capture/e25-05-preparacion-paquetes-323-324.md) |
| Exposición por modo en el CFW 3.73 (E26-R85) | Mecánico = referencia. EFCS on con la tabla de prueba `c = 2000 µs`: +27…+34 % a 1/350, ×3,9 a 1/3000 (pérdida real 1,0–1,16 ms; tabla calibrada R85 sin escribir; degradado vertical no corregible con `c`). **Silent sin calibrar:** el `av-cam` del CFW no lleva ShutMode 0 + `r5` (R56 §7), integra 31–54 ms a cualquier velocidad (+3,5…+5,5 EV); solo el parche RAM por disparo lo nivela. El CFW 3.76 (R86, sin instalar) lleva la calibración en la imagen | M / V | [R85](capture/e26-r85-calibracion-fotos-3749-3779.md), [R86](capture/e26-r86-cfw-376-tres-modos-nivelados.md) |

## Conclusiones corregidas (no reusar versiones previas)

La conclusión vigente va primero; el antecedente conserva su informe y se señala allí.

| Tema | Conclusión vigente | Rectifica | Fuente |
|---|---|---|---|
| Cadena «evento de ENTRADA → acción de vista» (G22-ACCION4, 26-11-2026) | El traductor existe pero vive en `libScalarDaemon.so`: `convertViewEventToAB` (`+0x13a704`) enmascara `code & ~0xf` y mapea `0x150100f0..f2` a **acción 4**. La copia de la tabla en `viewUnified2+0x3a03d4` es idéntica byte a byte y su lector (`viewUnified2+0x1906a8`) es **código muerto**, igual que `ScalarView::TriggerTableEvent` (`libObj+0x1170e8`, único llamante del traductor) y `ViewBase::transformByTriggerTable` (`+0x1208ec`); `[View+0x20]` es una **función**, no una tabla. En 3.21 **nadie ejecuta la cadena** (0 disparos medidos en el invitado con la tecla pulsada); el interruptor `PLAYVIEW=1` del arnés la ejecuta con las funciones del firmware y obtiene `accion=4`, pero la vista de reproducción no se instancia en un invitado sin OSD (G22-ACCION4-FALLA) | §7.3/§7.4/§8 del informe («la traducción se pierde en la vista») | [g22-reproduccion-dispatch §10](gui/g22-reproduccion-dispatch.md) |
| BK4 `0x30100` y `0x30102` (E26-R69) | Ninguna de las dos es un bloque de Darwin: `0x30100` es una tabla del BIONZ (da `pkt[0xa..b]`) y la relectura de Darwin va a `0x1850004/05`; `0x30102+0x88` no gobierna la segunda cortina. `t` = 0 al arrancar; la segunda cortina se suelta con el pulso de P4E en B | R58 §3/§13, R61, R62 §3–4, R63 §6, R64 §2/§5 | [R69](capture/e26-r69-revision-informes-efcs.md) |
| Pulso de P4C (E26-R70) | P4C ← 1 en la preparación (`0x1811a` → `0x17cee`) antes de armar A, y rearme posterior (`0x28dc5`, acción 0x14): A siempre produce el flanco de bajada en Darwin | R67 §1 (INFERENCIA «sube al preparar») | [R70](capture/e26-r70-cierre-pendientes-r65-r69.md) |
| Causa del negro con EFCS a ≥ 1/1000 (E26-R74) | No es firmware ni datos: el plan del sensor en el EFCS oficial no depende de T (`0x30097+0x15 = 0` → `sl = record+0x1c`; clase 3) y Darwin da `B − A` continuo con datos sin cambios. La pérdida (≈ 1,25 ms) sigue a lo cerca que cae B de A: causa física (obturador o su circuito) | R62 §2 (umbral `0x4383fa40`), R58 §12, R73 §4 | [R74](capture/e26-r74-conclusion-final-efcs-negro.md) |
| Bloques de ajuste de Darwin (E26-R66) | B (`0x20000300`) = propiedad NVRAM `0x1850001` y G (`0x20000480`) = `0x1850000`, enviados por la tabla BIONZ `0x43fe8c38`; **BK4 `0x30102` no llega a Darwin**. G/B no han cambiado desde el 20-10. Con EFCS activado Darwin hace `S+0x48 = T − G+0x42 (3407 µs)` | R58 §13, R61, R62 §3–4, R63 §6, R64 §5–6, R65 §4–5 | [R66](capture/e26-r66-bloques-darwin-en-nvram-1850000.md) |
| Darwin — base ROM | La base es `0x4200`, NO `0`; no reusar punteros de proyectos Ghidra antiguos | proyectos a6000/a6300-darwin | [darwin-shutter-entrypoints](capture/darwin-shutter-entrypoints.md) |
| SetImageWrited | `0x6108/0x1007`, **no** `0x1009` | sesión 12 | [pool-write-completion](capture/pool-write-completion.md), [S29](capture/s29-writestill-end-to-end.md) |
| Recuperación por USB | Depende también de que `darwin_core` encienda el sistema, no solo de `nflasha1` y `ud_darwin_firmup`; la entrada al actualizador por USB pasa por el sistema normal (`up.sh user`), no por botón | custom-fw-recovery (punto 3), darwin-via-actualizacion (riesgo 4) | [E24-01](capture/e24-01-arranque-recuperacion.md) |
| Bootloader de Darwin (E24-02) | Existe código de arranque propio del MCU en `0x0–0x41ff` (el core, en `0x4200`, salta a su vector con el buzón `[0x20000706]=4` al recibir `0x11` estado 4; sin binario). `ud_darwin_init` provoca ese salto en cada actualizador. `darwin_core` no programa flash: `0x14/0x15` los atiende el arranque. **No está demostrado** que el arranque reprograme una aplicación rota ni que encienda `DD_ON*` solo. El MCU tiene cableado un puerto de descarga (MD0/INITX/UART P21-P22/SWD, `CN4906` no montado); sin vía de software | V / I / N | [E24-02](capture/e24-02-protocolo-actualizacion-darwin.md) |
| Material de recuperación (E24-03) | Respaldos íntegros (NVRAM, NAND lógica, BootROM, firmware 3.21) pero incompletos: faltan el arranque de Darwin, Loader2/3, vía de escritura de NAND, NVRAM post-3.22 y copia externa. El FDAT 3.23 lleva el `darwin_core` oficial y el tar oficial, y se reconstruye bit a bit; el guard solo acepta versiones mayores que la instalada, por lo que `camera_reflash_fw321.sh` ya no sirve. Solo la NVRAM tiene una restauración demostrada en hardware; reinstalar con Darwin defectuoso y restaurar sin `darwin_core` NO están demostrados (ausencia de evidencia, no imposibilidad) | E24-03 | V / I / N | [E24-03](capture/e24-03-auditoria-recuperacion-usb.md) |
| Dictamen de seguridad (E24-04) | **No hay evidencia suficiente para autorizar un nuevo flasheo persistente de Darwin** (límite de evidencia, no imposibilidad): ningún Darwin defectuoso se ha recuperado nunca ni existe vía independiente de la aplicación; el FDAT 3.23 es íntegro y reproducible pero su aceptación y su uso como recuperación no están demostrados. Matriz M1–M14 auditada (+M15–M17): FAIL M1 frente a 3.24, M9, M12, M14. De los diez escenarios, solo «mecánica rota con Darwin vivo» tiene ruta plausible; D–H (sin `Upd`, sin enlace, bucle de watchdog, sin `DD_ON*`, core incompleto) no. Una modificación persistente de LIRO tampoco es más segura; solo lo volátil (RAM) tiene recuperación demostrada. El watchdog de Darwin se arma con un byte de configuración (0 lo desarma) | E24-03 M14 («aceptar el riesgo»); «parche de Darwin tipo 0 = bajo riesgo» | V / I / N | [E24-04](capture/e24-04-dictamen-seguridad.md) |
| Ruta `Upd` y rearme (E24-05) | La cadena `InitCom → Upd → 0x45bc` está **trazada con bytes** (solo existe en `Seton`; evento 2 de `next` = 5; una orden desconocida o el estado 7 mandan a `On`); clausura conservadora C1 = 480 / C2 = 571 funciones (sin binario del arranque: no es garantía de recuperación). **`0x1fe66`→0 sí cambia la lista de la máquina exterior a `[0,7,8,9,10]`** y evita `0x1fe50/0x1fe86/0x1feb6` desde las APIs de cargar y los 49 estados; excepción: operación 5 (`0x1fcb8→0x1feb6`, freno sin compuerta). Hay cinco sitios de error 6. `pkt[+1]` llega a `0x20003a01` (copia); su valor EFCS no está medido. Control volátil NO demostrado (falta el emisor BIONZ del bloque 0 y solo existe en `Seton`); watchdog: estructura conocida, reloj y valores no | E23: «`0x1fe66`→0 no desactiva el rearme»; E24-04 X8/§5 | V / I / N | [E24-05](capture/e24-05-upd-y-rearme.md) |
| Captura BIONZ→Darwin y fin (E24-05a) | El mensaje que arranca la máquina de 49 estados es el **ID `0x0c`** (22 B): `On` → `0xce84` → tarea `0x1811a` → `0x17f8c` (admite si `pkt[0]=0` y `S+0x43=0`) → `0x1961c`, que elige entre **cinco listas** según `S+0x44.b0`, `S+0x32` y `S+0x3c`. Los estados 4 (primera toma), 5 (ráfaga) y 0x1f (todas) arrancan los rearmes; el 4 depende del predicado `0x196a2` (clase `pkt[+1]` × tipo de mecanismo fijado por orden BIONZ 1–4). `[0,7,8,9,10]` cumple las esperas internas de Darwin (`S+0x12c`, id terminal; el estado 9 baja el bit 24 de la máscara de ocupación, que además **bloquea** la admisión del siguiente paquete), pero no se ha localizado el lector BIONZ del fin (C = NO, D = NO, F = NO, G = NO). Dentro de la captura solo dos sitios llegan a la operación 5 (rechazo cat 2/`0x51`, tiempo de fase cat 2/`0x30`); `0x1989c` no está en la captura. Valor EFCS de `pkt[+1]` sin medir | E24-05 «B = NO» (resuelto) y «unión de 49 estados» (hay 5 listas) | V / I / N | [E24-05a](capture/e24-05a-captura-fin-bionz-darwin.md) |
| Consumidor BIONZ del fin (E24-05d) | BIONZ recibe de Darwin **ocho** mensajes mss (IDs `0x0b,0x0d,0x0e,0x10,0x11,0x14,0x15,0x17`; clase 3, subclases 0,2,3,5,6,9,10,12) por la tabla CAIF `0x43fe87f0`: receptor → buzón `[0x43e77284]` → `caif_recv` (`0x437db9f0`), que **bloquea sin plazo** (`-1`) y exige la subclase esperada; cada fase de captura (`0x438c24bc…0x438cc…`) espera su mensaje en orden. **Corrige E24-05a:** la máscara de ocupación y el anillo de eventos **no** viajan a BIONZ: el «bloque de estado» `0x6c78` es una instantánea del registro de fallos (única llamada `0x45b2`, entrada de excepción) y los lectores de la máscara son solo `0x6ca0/0x6ca8/0x17eba`. Falta el emisor Darwin de cada ID y si `[0,7,8,9,10]` los emite (F = NO) | E24-05a §4.4 (máscara + anillo en `0x0d/0x10/0x11`) | V / I / N | [E24-05d](capture/e24-05d-consumidor-estado-darwin-bionz.md) |
| Emisores mss de Darwin (E24-05f) | Los ocho mensajes salen de: admisión `0x17f8c` → op `0x16c64` (`0x0b`); estado de captura 9 (monodisparo) u 11 (ráfaga) → ops `0x16ca4/0x16cd8/0x16d2e` (`0x0d`, `0x15`); estado 31 → FSM `0x296f0` estado 5 → op `0x16e92` (`0x0e`, `0x10`); FSM de ajustes `0x294f8`→`0x29f64` (`0x11`, `0x14`, solo con modo 0–8); `0x125f6` (`0x17`, orden de cambio de modo). Las cinco listas de captura contienen 9 u 11 y el 31; el código emisor de `0x0b,0x0d,0x15,0x0e,0x10` **no** alcanza `0x1fe66`, el tipo de bobina ni primitivas de motor: orden idéntico en `[0,7,8,9,10]` y en las listas con rearme. **Corrige E24-05d (B):** la clase de ocupación (`S+0x43` ← máscara) sí viaja en el byte 0 del `0x0b`. Falta el disparo de `0x11/0x14/0x17` y el consumo del byte 0 en BIONZ | E24-05d §3 (la máscara no sale) | V / I / N | [E24-05f](capture/e24-05f-emisores-mss-darwin.md) |
| Ajustes, modo y ocupación (E24-05g) | `0x18a` son flags de las filas 22/23 de `0x29514` (no un evento). `0x11/0x14` los dispara el gancho `0x1c04c` (bloque 10 bit 3 de la trama `0x31` → `{2,0x18}` → fila 24 → `0x1aa28`) o el arrancador por disparo `0x17c26`→`0x1a3ec`; solo con modo 0–8. **Corrige E24-05f:** el `0x17` no es una orden de BIONZ: lo pide Darwin (estado 27 de la lista de `0x0e/0x10`, tras el `0x10`; modo 0, único que lo emite); los modos 1/2 salen de las esperas del estado 31 sin `0x17`. Byte 0 del `0x0b` en BIONZ (`0x438c2538`): clase 0 acepta, 1 reintenta ≤19, 2 error. Sin rearme se conservan los cinco mensajes y el `0x17` sin tocar compuerta/bobinas; la espera del estado 31 depende de P29 y puede escribir P4E (`0x2041e`→`0x20d00`) con `0x1fe66=0` | E24-05f §3/§7 (`0x17` «orden BIONZ») | V / I / N | [E24-05g](capture/e24-05g-ajustes-modo-ocupacion.md) |
| Dependencias finales (E24-05h) | La espera del estado 31 tiene **dos variantes** (corrige E24-05g): `S+0x32=0` (`0x18fa0`) sale solo con P29 bajo (`MSS_S2_REQ_CA`, IC6000→Darwin), sin plazo; `S+0x32≠0` (`0x18d6e`, observada en T022: `pkt[2..3]=0x1600`) sale por la FSM ADC-B (`0x29dc8`) temporizada. Con `0x20c74=0` no hay escritura estática a P4D/P4E en estado 31, modos 0/1/2 ni FSM ADC; P4C sí (=1 en cada toma). FAIL (bit 7 de `ctx+0x10`) = reintento sin avance, sin mensaje a BIONZ ni op 5; el estado 26 sondea hasta que llega un mensaje de BIONZ. El `0x0c` lo construye `0x438d0064` por envío (tipo 1–4 en `pkt[0xc]`, de `obj[0x1e0]`). No hay bloqueo real demostrado ni ausencia demostrada (A=NO,B=NO,C=SÍ,D=NO,E=NO,F=SÍ,G=NO,H=NO,I=SÍ) | E24-05g §2.3 (espera solo por P29), §5 FAIL pendiente | V / I / N | [E24-05h](capture/e24-05h-dependencias-finales-captura.md) |
| Terminación de ADC-B y P29 (E24-05h-3) | ADC-B (`0x29dc8`, terminal 7) **se inicia y termina con `0x20c74=0`**: la compuerta `0x19b9e` (`S+0x444` b4=0 ∧ `S+0x170` b0=0) no lee el tipo; lista `[1,4,6,7]`, sin FAIL/salto/lecturas de pin; única espera = evento 0 del canal 0 de `0x40023000` (plazo `S+0x14c` ticks, ≈ µs inferido); el estado 31 espera `0x203ae` **sin plazo** (3 bucles). Con tipo 0 solo desaparecen P4D/P4E, `0x16fe2` y `0x20c4a`. P29: tabla `0x2675c`→INT05; 7 grupos de pines (P29 salida GPIO en 0/1/5/6, entrada en 2/4, función INT05 en 3; sin pull); grupo activo en captura: ver E24-05h-4 | no hay bloqueo real demostrado | [E24-05h-3](capture/e24-05h-3-adcb-p29.md) |
| GPIO cortinillas | P4D/P4E no son serie (descartado estáticamente) | hipótesis serie | [fm3-gpio](capture/fm3-gpio-shutter-mapping.md) |
| ADC-A, grupo de P29 e IRQ de ADC-B (E24-05h-4) | ADC-A `[2,4,6,16,17]` (la ejecuta el estado 4 de ADC-B) **retorna sin bloquear**: con tipo 0 sin ciclos, pines ni esperas; cada estado de ADC-A necesita eventos de su temporizador base canal 11 (2 eventos hasta terminal). **Los estados 3 y 32 de la captura fallan (reintento sin plazo) si ADC-A y ADC-B no están ambos en terminal**; igual con tipo 0 y ≠ 0. Grupo de P29 en `On` = **3 (INT05, entrada sin pull)**; ningún FSM de captura cambia de grupo. Evento 0 de ADC-B: armado `0x94f6/0xf99a` → IRQ 32 → vector `0xf8d3` (tabla base `0x42fc`) → `0x1d04d` | no hay bloqueo de software demostrado; ausencia no demostrable sin medir (VTOR, prioridad NVIC, ISR canal 11) | [E24-05h-4](capture/e24-05h-4-adca-p29-irq.md) |
| Espacios legibles y protocolo EFCS (E24-05e / E24-05h-5) | T022/T023 leen **DRAM de BIONZ** (`0x83f91e20..0x83f91f30`), no la SRAM de Darwin: los valores de E24-05h-4 §6 (ADC, FSM de captura, temporizadores, P29) no tienen vía de lectura demostrada. `pkt[1]` y `pkt[2..3]` del `0x0c` los escribe `0x43841070` en `carga+0x40` (`pkt[2..3] = [sl+0x162]`, 0 si `<0xb00` con la condición del filtro `0x4382fe08`); `S+0x32` es un derivado. Protocolo preparado (6 disparos ABBAAB, criterios C1–C5), no ejecutado | una foto normal no prueba el funcionamiento sin rearme; escritor de `[sl+0x162]` no único; no autoriza E24-06 | [E24-05e/h-5](capture/e24-05e-05h5-protocolo-lectura.md) |
| Desactivación del rearme (E25 / E25-02) | Candidato **offline** sobre el tipo 0: `0x1fe6a: 28 46 → 0a e0` (2 bytes) fuerza `0x1fe66=0`; los tres arrancadores eligen L0 `[0,7,8,9,10]`, `0x1f5a6` retorna y no se alcanzan `0x1fe50/0x1fe86/0x1feb6` en captura/rearme. Tipo 0 intacto; P4D/P4E filtrados; **P4B/P4C siguen**. **E25-02 cierra la vía volátil: A=NO** (sin emisor BIONZ de `InitCom 0x16`; actualizador solo `0x11/0x14/0x15`; Micon `NoAction`; además `0x16` copia 129 B con `length=0x81`, no 1 B). Auditoría independiente de B1a: salto 0x1fe6a→0x1fe82, pila/registros/retorno conservados, sin `0x1b080`, L0 en tres arrancadores, tipo 0 intacto, 12 consumidores. Correcciones: la “cancelación” de E25 era `InitCom`, no captura; op5 (`0x1fcb8→0x1feb6`, P40/P41=3, XOR=0) es **apagado**, no freno demostrado. Candidato no instalable; E24-04 sigue abierto. 54 + 42 pruebas nuevas + 255 E24/GPIO/Darwin (0 fallos con `.venv` activado) | V / I / N | [E25](capture/e25-desactivacion-mecanica.md), [E25-02](capture/e25-02-validacion-candidato-y-via-volatil.md), `tests/test_e25_02_auditoria.py` |
| Manejador LIRO `0x40e3` | **Existe en la A7S** (fila `0x43ff79e4` → `0x437a9cb1`); S401 lo buscó en la VA de la A6000 | S401 | [S402](capture/static-closure-2026-10-25.md) |
| Etiqueta `RecordStill::Execute` | `0x90b248` es RecordImage; no demostrada la antigua etiqueta | etiqueta histórica | [contrato](capture/recordstill-contract-audit-2026-10-23.md) |
| Llamadores de RecordImage | Falsos `0x7484dc`/`0x755af8` retirados; válidos `0x90de2e`/`0x91634e` | S382 inicial | [S382](capture/s382-recordstill-callers.md), [auditoría](auditoria-2026-10-23.md) |
| ID `0x40193` | No aparece como palabra en `.rodata/.data` pero sí como literal en `.text`; el negativo MOVW/MOVT era inválido | S384 inicial | [S384](capture/s384-queue-id-0x40193-search.md) |
| Sesgo `+0x58` | La entrada de S305 era interior `+0x58`; corregidas S303rev1/S304/S305 | S303rev1, S304, S305 | [S303](capture/s303-ref-tree-43ff3200.md), [S305](capture/s305-fun43858390-literal-pool.md) |
| Mapa de columnas | `0x43c9c5b5` es posición→columna (34); `0x4e`→12, `0x4f`→13 | «columna 1», S302/S321 | [S325](capture/s325-position-map.md), [S324](capture/s324-columns-audit.md) |
| Tablas T1/T2/T3 | Bases 4 B más bajas (T2 `0x43bbf2e8`, T3 `0x43bbef30`); sin tabla de tiempos por modo; huella silent en T2 (`0x3ff` vs 0) | S317, S326 | [S329](capture/s329-mode-timing-tables.md), [S331](capture/s331-consumer-signature.md) |
| `obj+0x2b4` | Flag de log; la fila la elige la posición del modo | S327, S330 | [S331](capture/s331-consumer-signature.md) |
| Alcance de T | Cinco consumidores leen campos de la fila (no solo `+0x14/+0x18`) | S329 | [S336](capture/s336-table-consumers.md) |
| `0x43fef404` | No es `u16[69]` de tiempos: tabla de ids del ODL | S329 | [S337](capture/s337-fef404-table.md), [S342](capture/s342-fef404-consumers.md) |
| Rolling / ElecShutter A6300 | Cadena `rolling` muerta; los 128 B de `0x43dcfa9e` sin referencias | S164, S135 | [S168](capture/s168-a6300-rolling.md), [S172](capture/s172-elec-shutter-a6300.md) |
| Validación S605–S627 | Siete gemelas falsas, 13 textos truncados, cinco longitudes; S625 = `[CAM_UTIL_SENS]: ` (17 B) | las 263 pruebas originales | [auditoría](capture/S605-S627_tabla_hallazgos.md) |
| S207 | No demuestra ausencia de un fin de integración (JSON/generador `NO_VERIFICADO`) | lectura inicial | [S207](capture/s207-imx235-end-of-integration.md) |
| Triaje S400 | 141 clasificaciones automáticas reabiertas; 86 filas resueltas, 0 pendientes | triaje automático | [triaje](../analysis/s400_open_questions_triage/README.md) |
| EFCS mapa completo (REA) | 9 funciones reconstruidas (0x43844e80, 0x43842158, 0x43841070, 0x4383fa40, 0x4383fd6c, 0x437f8a50, 0x438c828c, 0x436d6320/0x436d6f6c, 0x437ea8cc), grafo de llamadas, campos de `cap`/`record`, tabla de clases 0–7. Direcciones 0x436d6f6c/0x437ea8cc/0x43844e80 son código Thumb válido pero no auto-detectadas por Ghidra (E25-EFCS-4). | VERIFICADO | [REA `analysis/efcs-reia/`](../analysis/efcs-reia/), [informe](capture/efcs-darwin-silent-integracion.md) |
| Productor nativo r5 | `0x4383fa40(record, settings)` calcula r5 = frame − líneas, ShutMode = 0, svd = frames−1 desde Tv (`record+0xf6`), período (`record+0xc`), VTS (`record+0x20`). Llamado por constructor normal (0x437b43b4, compuerta `cap+0x11b0`) y EFCS (0x43841070). Emulado vs T047: ±1 línea. | VERIFICADO | [REA](../analysis/efcs-reia/evidence/0x4383fa40_pseudo.txt), [E25-16](capture/e25-16-r5-autonomo-fotografia.md) |
| EFCS → Darwin | BIONZ envía ID `0x0c` (CaptureStart) y mensaje `0x107` (vía `0x43901a8c`) con timing; Darwin responde `0x0e` (ExposureReady). Con tipo 0/B1a, Darwin no mueve P4D/P4E. No hay diferencia en el lado Darwin con o sin EFCS. | VERIFICADO (BIONZ) / INFERENCIA (Darwin) | [REA `0x43901a8c`](../analysis/efcs-reia/evidence/0x43901a8c_pseudo.txt), [E24-05](capture/e24-05-upd-y-rearme.md) |
| C3-B integrado (E25-26) | **Implementado offline y verificado en emulación:** enganche `0x438c82fe`, cueva `0x43541840`, solo paso 0, `cap+0x41c==1`, `svd ≤ 1`, VTS≠0 y `shd>VTS`; consume el plan nativo de `cap+0x64c` (no reejecuta `0x4383fa40`), escribe `shd−=VTS`, `svd=0`, `ShutMode=0`. EFCS idéntico al original; Electronic 1/8000–1/30 (`shd` 4211…2025); largas inhibidas. Riesgo residual `cap+0x73b` (E25-28). | V/E (offline) / N (físico) | [E25-26](capture/e25-26-c3b-exposicion-electronica.md), `tests/test_e25_26_c3b.py` |
| Carga y cuevas (E25-25) | La cueva antigua de E25-24 no era segura; nueva zona `0x4354141c–0x435418d8` (cero en A6000/A7S, sin punteros, después del `memcpy` API del cargador). Canal `cap+0x41c → pkt[0x0e] → S+0x3e`, congelado por captura; 0 lectores estáticos de `S+0x3e`. `liro.ko` lee el archivo completo; CRC-32 externo, sin firma demostrada; recuperación de Darwin sigue sin demostrar. | V/I/B | [E25-25](capture/e25-25-validacion-carga-caves.md) |
| Firmware integrado (E25-29) | **Construido offline** sobre los originales 3.21: selector + C3-B + compuertas Darwin, `nflasha3` recompuesta (3 bloques TPZL), `part_image.sum`/`darwin.sum` y tar de 105 miembros; FDAT/DAT 3.25 con `fwtool`. **Verificado offline:** 208 078 bloques descifrados sin errores, DEND/CRC, extracción inversa exacta, reversión SHA-256 y emulación integrada (`all_ok`). El guard y el arranque **no** se han ejercitado; no es instalable. | V/E (offline) / N (físico) | [E25-27](capture/e25-27-construccion-firmware-integrado.md), `analysis/e25-27/evidence.json` |
| Formato TPZL que exige el arranque (E26-R36) | Loader3 lee cada bloque por sectores enteros desde `off>>9` y el residuo no llega al LDEC; el LDEC se programa con `bloque>>12` registros. Toda partición recompuesta debe tener residuo 0 y bloques de 16 registros de 4096 B (como los 19 489 bloques de Sony). El `nflasha3` del 3.25 no lo cumplía y es la causa identificada del −302; `tpzl.py` ahora produce ese formato y `hardware_violations` lo comprueba. Ni la verificación por software (`fwtool`, `decode_block`) ni «alinear a 512» bastaban | E25-27 §3 (256 B, literal único); R16/R17 decisión C sobre el residuo; README rec. 2 | V (binario + datos) / N (físico) | [R36](capture/e26-r36-causa-fallo-325.md), `analysis/e26-recovery/r36-ldec-records.json` |
| Bucle de error de Loader3 (E26-R41) | `c01f379a` es una consola serie (`beast`, `ldump`) de solo lectura; el bucle reinicializa la UART (`c01f5008`), pero con `Backup[0x510015]=0` no imprime nada. Existe una espera de ICE por GPIO (banco 14, bit 17) antes del −302 | R13 («sondeo UART», hipótesis), R37 §4 («`c01f5008` no se llama»), R40 §6 | [R41](capture/e26-r41-caminos-estaticos-restantes.md) |
| Bolas JTAG/eFuse/SWD y neto XRESET_CR (E26-R42) | Leídas directamente del esquema (el `.txt` OCR pierde esta hoja): `FUSE_EN`(T12) y TDI/TCK/TMS atados a VDD; `FUSE_CLK`(R12) sin red; `NTRST`(H26) = mismo neto que la entrada `XRESET` del chip (bola K6, vía R6000 XX) | — (precisión nueva, no corrige nada) | [R42](capture/e26-r42-busqueda-externa-y-esquema-jtag.md) |
| Darwin condicionado (E25-24b) | **Sí se modifica Darwin**, pero solo dos `bl` y un cave: B1a/tipo 0 se sustituyen por una compuerta que lee `pkt[0x0e]`. EFCS conserva `0x20c74`/`0x1fe66` originales; Electronic devuelve 0. No se tocan `InitCom`, `Upd`, reset, watchdog ni GPIO. Verificado por bytes y Unicorn; no físicamente. | V (offline) / N (físico) | [E25-24b](capture/e25-24b-implementacion-selector.md), `tests/test_e25_24_selector.py` |

## Política de ingeniería inversa: REA primero (vigente desde 2026-10-19)

Canónica para Codex y Claude Code; `AGENTS.md`/`CLAUDE.md` solo la resumen. No sustituye las restricciones activas.

1. **REA primero** para explorar lo nuevo: descubrir funciones, xrefs, llamadas directas/indirectas, grafos
   (`get_call_graph`), dependencias de valores (`trace_native_values`), decompilar (`batch_decompile`,
   `analyze_function`), constantes/estructuras (`search_bytes`, `xrefs`, `resolve_containing_procedure`),
   comparar funciones y recuperar evidencia previa. Hay que *usarlo*, no solo comprobar que está instalado.
2. **Ghidra histórico (`analysis/ghidra/silent-liro.gpr`, readOnly/noanalysis) después**, cuando: REA no
   reconoce una función conocida (p. ej. entradas Thumb sembradas a mano: 0x43789cc0, 0x43789708, 0x437da100,
   0x43792f9c, 0x43794096, 0x43ae90ce; REA cubre 363/464 entradas históricas), su análisis es incompleto o
   ambiguo, hay que verificar bytes/instrucciones ya recuperados, o seguir una investigación conocida es
   más barato que repetir búsquedas fallidas. Una consulta vacía de REA **no** prueba ausencia.
3. **Coste:** `av-cam.bin` cuesta ~8 min en frío y la sesión REA no persiste (rea#1048). Primero buscar
   evidencia ya exportada (`knowledge/`, `analysis/rea-independent/out/`). Si hay que abrirlo: comprobar
   si ya hay demonio (`analysis/rea-independent/run/rea.sock` + `.ready`, proceso `session_daemon.py`);
   si no, abrirlo **una vez** con `bin/session_daemon.py` y consultar por lotes con `bin/q.py`
   (el demonio fija `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=2G`, límite 2,6 GB y 1 h de
   inactividad); cerrar con `q.py SOCK --shutdown` al terminar el hito y comprobar que no quedan
   procesos. Bibliotecas ELF pequeñas (`libmprctrl.so`): MCP `rea` directo (~25 s). Evitar `list_procedures`
   masivo sin paginar. Detalle y parámetros: [rea-independent-milestone.md](capture/rea-independent-milestone.md).
4. **Rigor:** REA y Ghidra comparten motor: su acuerdo prueba configuración coherente, no independencia
   (el decodificador independiente es LLVM `llvm-objdump` + búsqueda de bytes propia). Verificar los
   hallazgos decisivos contra instrucciones y bytes reales; separar hecho, inferencia y NO_VERIFICADO.
5. **Intactos siempre:** firmware original, `silent-liro.*`, `analysis/ghidra`, informes S1–S48; comprobar con
   SHA-256 (`analysis/rea-independent/manifests/*.final.sha256`). REA trabaja en proyecto temporal
   `-readOnly -deleteProject`. Sin ejecutar firmware, sin flasheo (salvo autorización expresa del usuario
   para un caso concreto), sin pruebas físicas.
6. **Foco:** obturador completamente electrónico, en hitos grandes y autónomos; no ampliar infraestructura.
7. **MCP:** `rea` en Codex (`~/.codex/config.toml`, `[mcp_servers.rea]`) y en Claude Code (`.mcp.json` del directorio padre `../`, único punto de configuración MCP/permisos; sesiones siempre desde el padre;
   usa `scripts/rea`, requiere aprobación del usuario al abrir `claude`), junto a `sony-a6000-knowledge`.

## Restricciones activas

- Flasheos realizados con autorización expresa: 3.22 (T024, 26-10-2026), 3.23 (T040, 27-10-2026), 3.25 (incidente E26) y **3.26
  (recuperación, 03-11-2026, por el actualizador oficial de Sony; R46–R49)**. Acceso físico por SWD autorizado para la recuperación
  (R46–R48), incluida la escritura transitoria de un registro de CPU durante el arranque (R48 P1) y la instalación del 3.26 (P3).
  Cualquier acceso físico o escritura posterior sigue necesitando autorización expresa para ese caso concreto.
- **Git**: el usuario ha instruido explícitamente (21-10-2026) **subir cada hito terminado a
  `origin/main`**; sigue vigente la prohibición de subir firmware y de tocar la cámara. La prohibición
  de flashear solo se levanta con autorización expresa del usuario para un caso concreto (26-10-2026).
  Los hitos se commitean **por ruta** (nunca `git add -A`) y el repositorio se compacta con
  `git gc` (`gc.auto=512`).
- Ningún resultado estático se ha convertido en demostración física sin evidencia adicional explícita.
- EFCS/SilentShutter: hay opciones de software y transporte identificados; **no** hay control físico demostrado ni finalización electrónica de exposición confirmada.
- Todos estos hallazgos son **sobre el firmware**: la ausencia estática de un módulo, cadena o parámetro **no** demuestra incapacidad del hardware.

## Próximos pasos

Se mantienen en [PENDIENTES](PENDIENTES.md) (estáticos A, documentales B, entorno C, físicos D, respaldo E). Resumen operativo en
[CURRENT § Pendientes activos prioritarios](../knowledge/CURRENT.md#pendientes-activos-prioritarios-autoridad-pendientes). Plan de pruebas físicas (diferido): [P1–P8](capture/physical-test-plan.md),
[P9–P12](capture/s402-physical-test-mapping.md), [P13–P21](capture/physical-test-plan-2.md), [P22–P24](capture/physical-test-review-2026-10-26.md).

## Cómo consultar el sistema de conocimiento

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py exact "0x..."        # dirección/símbolo
python3 scripts/knowledge/search.py text "concepto"       # búsqueda BM25
python3 scripts/knowledge/search.py tree --subsystem docs/capture
python3 scripts/knowledge/search.py claim docs/capture/<doc>.md   # qué lo corrige
```

Estado de implementación del propio sistema de conocimiento: [knowledge/PROGRESS.md](../knowledge/PROGRESS.md).
Auditoría de la lista de pendientes: [sincronización del 24-10-2026](capture/pending-sync-audit-2026-10-24.md).

## Dónde quedó el historial que antes vivía aquí

Todo en [history/STATE-historial-2026-10-26.md](history/STATE-historial-2026-10-26.md) (íntegro): avances S44–S47 (cadena de registros IMX210,
payload `0x43ed4620`, callback `0x437dad78`), S58 (productores numéricos y emulación IMX235), S140–S163 (mapa de registros IMX210, filas G, gates),
S138–S174 (línea de RE general y controles positivos A6300), S300–S348 (carril B) y los bloques por fecha del 23 al 25-10-2026. Sus informes
originales siguen en [docs/capture/](capture/); acceso por tema en [INDEX](INDEX.md).


## E25-22 — observación física parcial de sombras (28-10-2026)

Dos fotos normales y RAW de una nueva escena: durante la toma larga `cap` mostró shd=1/svd=0 y los bytes de sombras ID3–ID6 fueron compatibles (`00 00 01 00`), en lecturas no simultáneas. No se midió el plan nativo de cada foto ni la transferencia eléctrica; no se demostró inicio o fin de integración electrónica. Detalles, datos y límites: [E25-22](capture/e25-22-protocolo-transporte-fisico.md).

- **Publicación (01-11-2026):** el autor no tiene licencia de Sony sobre el firmware; los `.dat` del release se rigen por el «Copyright y uso» del README y el código propio por MIT. La réplica de principio a fin está en `wiki/`. Sin cambio técnico.

## Cambio de conclusión esta sesión (18-11-2026)

- **E2E-10 CERRADO:** av-cam contesta `0x3003` (seq 15) en la LIRO VM. La VM llega sola al estado 2 del secuenciador (`[0x43ede338]=2`, guion 0→2, posición 42) sin forzar el paso ni cargar volcado real; `tests/test_avcam_ee_start.py` en verde (`test_av_cam_contesta_0x3003_ultimo_paso_de_ee_start`, `test_secuenciador_elige_la_transicion_0_a_2…`). El bloqueo del secuenciador que retenía E2E-12c/E2E-15 queda eliminado.
- **E2E-12c CERRADO:** mismo resultado, sin forzar nada (T51, MEDIDO).
- **E2E-15 desbloqueada (PARCIAL):** la UI prepara la grabación (av-cam acepta `0x4000` EE vídeo, `0xf000`) y llega a «REC». **`0x3000` responde en el arnés** cuando el secuenciador `[0x43ede338]=8` (verificado en LIRO VM: `{1, 0x3000, seq=0x80000100, 00f000000000000000748043}`). El estado 8 se alcanzó por forzado directo de registro (diagnóstico) porque el guion de `0x3000` (lista `0x43bf37b4`, 43 palabras) se atasca en pos=11/43: las palabras 0-35 escriben `slot=0` (estado del secuenciador) con valores sucesivos (1, 8, 1, 0x4d, ...), y la palabra 11 exige estado 16, que requiere el pipeline de vídeo no emulado en la LIRO VM. **`0x3024` no responde por diseño:** su manejador en `tsk0x61` (`0x43807958`) llama a `0x43b023cc` y va al epílogo `0x43807a30` con `r6=0` (no genera respuesta); `tsk0x45` traduce `0x3024 → tipo 0x8102`; `0x3024` no está en el grupo 0 de la tabla de 271 descritores (está en grupos `0x52/0x53/0x54/0x5d`). Clip generado en `PRIVATE/M4ROOT/CLIP/C0001.MP4` vía `sd_emu.py` (50 KB, estructura MP4/XAVC S `ftyp`+`mdat`, no es stream real del encoder). Desbloquea VFR-F3, DVR-F3, TCUB-F3, G70-HD120 y Loop Recording. Criterio de cierre: `0x3024` respondido de forma legítima y clip real de vídeo en `PRIVATE/M4ROOT/CLIP`.

## LUTs propios — decisión y especificación (26-11-2026)

Petición: continuar la integración, decidir la mejor vía, si el 5×9×9 se puede mejorar y qué debe cumplir un LUT para subirlo a la cámara.
Informe: [G114](gui/g114-lut-propios-especificacion.md); validador `scripts/lut/cube_spec.py`; medidas de los 75 `.cube` del usuario en
`lut-eval/informe.md` (fuera del repo).

- **Mejor vía:** paquete `.LUT` precalculado en el PC (tabla 5×9×9 ajustada en ΔE + curva T opcional) → SD → hilo `lutsd` → blob de
  Backup `0x150005` → ganchos de `av-cam`. Cero coste por fotograma y afecta a foto, vídeo y vista en vivo. El `.cube` en la SD queda
  como respaldo (la cámara remuestrea por nodo y peor); `lutjpg` (`.cube` completo, 2…129³) es la vía exacta solo para foto.
- **Rejilla:** no se puede ampliar. El generador recorre 9×9×5 fijos, la copia es de `0x654` B y ningún registro codifica la rejilla;
  el mismo bloque está en A7S/A6300. Matiz de auditoría: con el modelo de bancos, 8³ cabría exacto, pero no lo dirige ningún registro.
- **Mejoras reales del 5×9×9:** curva 1D T tras la gamma (0,79→0,19 ΔE en película sintética; elegir T sí/no por LUT), ajuste en ΔE2000
  (ya por defecto), modelo de interpolación real (LUT-INT-1, cámara) y paquete precalculado. M no aporta; Color Depth/LutMode no dan geometría.
- **Especificación `.cube`:** 3D, 33³ recomendado (2…129 aceptado; `.cube` en cámara ≤64³), dominio 0…1, valores dentro, sin 1D ni
  `LUT_3D_INPUT_RANGE`, entrada Rec.709/sRGB de pantalla (no V-Log), líneas ≤95 caracteres. En la SD: `LUT/LUT1.LUT`…`LUT6.LUT` (1080 B,
  v1) o `LUT1.cube`…`LUT6.cube`.
- **Medido:** de 75 `.cube`, solo las 6 de `luts/peliculas` son aptas para el hardware (0,22–0,67 ΔE medio; 0–28 nodos recortados). Las
  69 de `sosang/` son de una Panasonic S1II (TITLE `S1II Standard - NNNNVLOG`): salen planas y recortan 31–384/405 nodos; las 29 `vlog`
  esperan V-Log y no aplican. Pack: portra400, pro400h, gold200, ektachrome_e100, kodachrome64, velvia50.
- **Bloqueo grave (ZONA-1), resuelto offline en G116:** la cueva/tablas históricas estaban dentro de la tabla T1 de estabilización y de las
  BOKS del YC de captura (G107); el CFW 3.86 instalado las lleva ahí. `LUT-C` se cierra en estático: cueva, máquina de estados y curva viven
  ahora en la cola libre del hueco G18 (`ZONA_L18` `0x43FB8800…0x43FB8EE0`, `ZONA_T18` desde `0x43FB8360`) y **las tablas ya no van en el
  `.dat`**: salen del blob de la SD (`.cube` o `.LUT`). `scripts/lut/zonas.py` verifica que esas zonas no tienen referencias (y encuentra las
  de T1/BOKS como control positivo). Sin tarjeta el ajuste queda en fábrica. LUT-SD-2/LUT-T-2 quedan como pruebas de cámara con un build
  nuevo: **no usar LUT con el CFW 3.86 instalado**. Nada del pipeline se ha probado en cámara: todos los ΔE son del modelo del PC.

## App web y cierre estático de la LUT (G116, 26-11-2026)

Informe: [G116](gui/g116-lut-solo-sd-y-app-web.md).

- **App**: `site/lut/` (GitHub Pages). Importa `.cube` 2³…64³, replica el muestreo del firmware (`lutsd.c`), descarga `LUT1.LUT`…`LUT6.LUT`
  (paquete v1 `A6LT` + CRC32) y previsualiza la foto del usuario con la cadena del proyecto. El `.LUT` que genera es **byte a byte** el del
  ARM (comprobado con Node frente a `lut_sd_userland.referencia` en 2³, 5³ y 33³).
- **Qué no es**: demosaico, NR y gamma propia del JPEG no se modelan; la previsualización es el modelo del PC, no una medida en cámara.
- **Cierre**: `LUT-C` cerrado en estático; `LUT-T-1` ya no está bloqueado (curva por ranura desde el blob); `LUT-INT-2` cerrado con el modelo
  conservador «ambos»; siguen abiertos `LUT-A` (M), `LUT-OPT-1` (necesita fotos), `LUT-DE-1` (métrica de ΔE, no cambia bytes), `LUT-2C-1`
  (segunda curva de 512 puntos) y las pruebas de cámara `LUT-SD-2`/`LUT-T-2`.
