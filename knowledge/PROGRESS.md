# Progreso — sistema de conocimiento Sony A6000

> **E26 R9 parcial:** [revisión](../docs/capture/e26-r9-bootrom-ram-execution.md) corrige R8: CRC-32, copia por tipos distintos de 0 y 0xffff; parser R8 no válido. Falta emular la ruta, demostrar RAM ejecutable y señal física.

**R6 fase 1, checkpoint:** [BLDR](../docs/capture/e26-r6-recuperacion-bionz.md). PMCA payload local byte a byte igual a upstream 0ce3c7e8, gitlink plataforma 85bcb545. ELF extraído y REA: un safe/cuatro normales, normales die0/plane0, metadatos descartados, error => trama vacía; wrapper rechaza estado 1 de ECC tolerado por Loader2. Mapa condicional de 480 KiB con una trama normal perdida; ID/error desconocidos. Cola INFO6 die0/plane1/block2/pages0–20 sin correspondencia adquirida. Regresión inicial falló por inspector inexistente; implementado, 3 pruebas, ruff/mypy pasan. Sin cámara. Próximo paso exacto: verificar límites del selector en los primeros 43 folios y localizar orientación CN4906 en SIDE A.

## G22-REPRO — la SD emulada trae `AVF_INFO`; el firmware lo consulta y el índice real sigue faltando (26-11-2026)
Arranque en frío del arnés G22 (`live.py`, perfil `repro`, puerto 8650) con `SD_ESTRUCTURA=1` y un
`DSC00001.JPG` real (1536x1024) en `DCIM/100MSDCF`: `sd_image.py` crea `AVF_INFO/{AVIN0001.INP,.BNP,.INT,PRV00001.BIN,STAT0000.BIN}`
a 0 B (contenido no inventado, no hay volcado de tarjeta en el repo) y `MP_ROOT/100ANV01`; 5 tests en
`tests/test_gui_sd_image.py`. MEDIDO: `libmpr` consulta `ms:/AVF_INFO` y sigue con `PRV00001.BIN`, las tres
`AVIN0001.*` y `STAT0000.BIN` (24 disparos de `FindFirst` en `libmpr+0x13e474`, rutas decodificadas);
`Fsys_MountAsync("/dev/mmca") OK 'A'` y el manejador del recuento `libmpr+0x620028` se ejecuta. Estático:
«hay medio» en `libmpr+0x1d1774` ⇔ `FindFirst("ms:/AVF_INFO")==0` (`0x2109` falla). SIGUE FALLANDO: la tecla
Reproducción `0x1f7` no abre ninguna vista (solo cambia AF-S→MF) y el recuento no sale numérico; el volcado
del disco del invitado (`POST /sd-volcado`) es idéntico al de arranque, así que la cámara no crea ni repara el
índice. Informe: `docs/gui/g22-reproduccion-sd.md` (bloque PARA PENDIENTES: fila G22-REPRO). Próximo paso
exacto: arrancar con `TRACEFN2=615928,620246,620262,62059c` (¿llega la fórmula del recuento?) y trazar la acción
de la tecla `0x1f7` en `InputService`→`viewManagerIf::openView`. Sin cámara.

## H3 — Eye AF dentro del CFW: 2 bytes en `av-cam`, sin APK (28-11-2026)
El usuario descartó la app (`ar.eyeaf`) y pidió que el Eye AF «venga directo en el cfw». Se parchea el
selector de fuente del área de AF: en `0x437b7200` el firmware sólo usa los ojos si el modo de área es 2
(y el 1 para el ojo izquierdo); `0x437b723a` `022e` (`cmp r6,#2`) + `0x437b723c` `38d1` (`bne`) desvían
cualquier otro modo al marco de cara. El parche escribe `0x437b723c = 00 bf` (`nop`): todos los modos
caen en la prioridad ojo2→ojo1→ceros, con el aviso `Eye data is invalid…` intacto y sin tocar el detector
(`Camera::FC::Drv::ProcessEdt`), la conversión ojo→rectángulo ni `ReplyForTouchShutter`. Nuevo
`scripts/cfw/eye_af_patch.py` (`apply_bytes`/`restore_bytes`/`allowed_addresses`, CLI `--apply/--check/--revert`,
SHA y tamaño de la 3.21 fijados, aborta si los bytes no son los esperados) y enganche en
`scripts/e25_27/build.py::apply_patches` tras selector y C3-B, con comprobaciones de diff autorizado, sin
solape y reversión exacta; el `nflasha3` del constructor sale ya con Eye AF. Pruebas: 7 en
`tests/test_eye_af_cfw_patch.py` (desensamblado del sitio, sólo 2 B, idempotencia, reversión con SHA
idéntico, CLI, tamaños ajenos) y 27 en `tests/test_e25_27_build.py` (cadena, determinismo, emulación);
el contenedor pasa a cambiar los bloques `{0, 39, 48, 57}`. Límites: sólo cambia **qué** fuente usa el
área de AF, no **cada cuánto** se pide (la continuidad sigue dependiendo de AF-C; cadencia
NO_VERIFICADA), el efecto en cámara es NO_VERIFICADO y no se ha instalado nada.

## FILM-PB-1 — el log real de la cámara: NTSC, IFO sin cargar y lectura del volumen rota (26-11-2026)
El dump `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (1 GiB, por SWD, **anterior al CFW 3.93 del 24-11**) conserva el anillo de log del proceso MPR en VA `0x82DF9300`–`0x82DFC400` (130 líneas, extraídas y reproducibles con `reports/evidence/film-pb-1-log-real-20261126/extraer_anillo.py`, SHA-256 del dump `f96c6152…fdbf`). Tres pruebas directas: (1) **la cámara es NTSC** — `[AVIMMGR][MS1]SetLoadInfo : TvSystem is NTSC, frameRate 3`, con frameRate 3 = 30000/1001, el de los siete clips: la premisa PAL del «diagnóstico cerrado» es falsa; (2) **ningún IFO se carga** — `MountCmd : Flash Mount Error` en `/dev/mmca`, `GetDeviceInfo : ER_SEQUENCE DEVICE Unmounted`, `[MP4IFO] ### mp4Ifo faild at IF/mp4Ifo_General.cpp(1749|1340) ErrCd: 0xB0800001`, `LoadSub : MP4 Load Error` (AVCHD `0xA0100003`, XAVC `0xB0800005`, MP4 `0xB0800001`), `CreateAndLoad Error` (`0x31000006` → `0x32400001`) y `LoadExec : Flash Load Error`; (3) **no es solo vídeo** — en reproducción de imagen: `[CACHE]BUFFER SIZE TOO SMALL : 00000000`, `Failed to dfs::seek offset=0x0049CE00 errcode=0x0E100001` y `Failed to read errcd=0xC3000101`. El intento de reproducción deja `[AVI]CS_AviAcsr::Unknown Function[0x20]` + `[AVI][PLAY] sources/avi_if/AviSeqPlay.cpp Error=[ER_BADARG] Line:10332`, y la BD de respaldo falla en las tres capas (`CheckSalvageStatus() 0xA0100003`, `Err RcsBackupTblData`), que es justo lo que consulta «Recuperar BD imág.». El `0:02` queda explicado por `[MprCnv] Warning ResumeInfo Structure Size is different! sizeof(MPR::RSMPoint): 64, sizeof(PubResume::ResumeInfo): 60`. **Causa material: el IFO no se carga del volumen**; la guarda A falla por el mismo motivo que la B (`GetInhInfo` devuelve error con el `mp4Ifo_If` sin *loaded*) y el mutex del `mp4Ifo_If` es el eslabón que lo hace visible, no la causa. Antes de flashear nada: miniaturas de foto, otra tarjeta formateada en la cámara y reproducir sin tarjeta. [Informe](../reports/film-pb-1-log-real-20261126.md).

## FILM-PB-1 — REENCUADRE: la cadencia no es la causa; falla el mutex del mp4Ifo_If (26-11-2026)
Dos pruebas de la cámara en mano refutan la línea de la cadencia: el clip convertido a 25p da «No se puede visualizar» y **un clip grabado por la propia cámara tampoco**. «Recuperar BD imág.» no cambia el síntoma, la miniatura no aparece y el vídeo sí se lista. Del árbol de salidas de `FUN_00437BC0` solo dos filas producen el mensaje de la cámara (guarda A `0x437C0A`, guarda B `0x437C3C`). **A queda descartada con clip propio**: es una comprobación de capacidades por bits sobre `[core+0xDB8]` (con máscara 0 devuelve 1, `0x447AC8`→`0x447AE0`) y el único desacuerdo `TvSystem` cae en `info[0]`, mientras la guarda de vídeo lee `info[1]` (máscara 6 ⇒ dos `AviMMgr::GetPlayMovieStatus`); no hay camino que deje basura (memset + `0x018000FF`/`0x80000000`). **Falla B, y falla antes de mirar el formato**: `isSupportContent` (`0x61A8F0`) llama primero (`0x61A9E4`) a `Mp4IfoIf::GetPlayThumbnailInfo` (`0x6E8430`), que no decodifica ni abre el fichero: en `0x6E845A` toma el mutex del `mp4Ifo_If` (`0x5BAD00`, `ifoFramework_Semaphore.cpp`) y, si falla, devuelve el literal `0xB0100002` (`mp4Ifo_If.cpp(0x1AF)`) sin tocar el MP4. Ese mutex es un try-lock no recursivo: `[obj+4]` solo lo escriben ctor (`0x5BACE0`), release (`0x5BACC6`) y acquire (`0x5BADC2`), y solo puede quedar a 0 si otro hilo lo retiene (fuga de release) o si el handle quedó colgante (el destructor `0x6E81BC` libera el semáforo y no limpia el puntero). Un solo fallo ahí explica el `0x1A`, la ausencia de miniatura de vídeo y que la duración se tome del índice (`0:02`). Descartados además: decodificador H.264 (está fuera de Linux, en `av-cam` con microcódigo `ZM_AVCD*` de `/usr/sabin`; su fallo sería posterior a `PbStart` y las miniaturas JPEG seguirían saliendo), versión del `av-cam` del paquete (es el de 3.21 + 40 B integrados + 34 KB de tablas de curvas; `vmlinux.bin` e `initrd.img` son byte a byte los de 3.21), BD/catálogo, NVRAM y parches de la ruta de reproducción. Artefactos listos: `build/cfw_bypass_guardas/libmpr.so` (guardas anuladas en `0x437BFA`/`0x437C2C`, 8 B, sin relocaciones), paquete con WBI (`build_package_nflasha15.py` sin `--sin-wbi`, dry-run 20/20) y el 3.21 oficial verificado. Prueba gratis en cámara: encender y pulsar reproducción antes de que se generen miniaturas; si así va y luego no, es fuga del mutex. [Reencuadre](../reports/film-pb-1-fallo-global-pb-20261126.md) · [ifoFramework](../reports/film-pb-1-sub-ifoframework-20261126.md) · [guarda A por bits](../reports/film-pb-1-sub-guardaa-bits-20261126.md) · [decodificador](../reports/film-pb-1-sub-decodificador-20261128.md) · [arranque/WBI](../reports/film-pb-1-sub-arranque-wbi-20261128.md) · [bypass](../reports/film-pb-1-sub-bypass-guardas-20261126.md).

## FILM-PB-1 — diagnóstico cerrado (SUPERADO): cámara PAL con clips NTSC (27-11-2026)
Enum de cadencia verificado por dos tablas (`0x686A34`, `tbb` de `0x77AF2C`) y por el mapeo 1..10→0..9 de `0x6E0CD6`: 0=24000/1001, 1=24, 2=25, 3=30000/1001, 4=50, 5=60000/1001, 6=100, 7=120000/1001, 8=200, 9=240000/1001. `TvSystem==1` es PAL (acepta 24p y 25/50/100/200) y `!=1` NTSC (24p y 29,97/59,94/119,88/239,76). Los siete clips son enum 3 y ninguno se reproduce: solo una cámara PAL lo explica, y una PAL no puede haberlos grabado. La cadencia entra por `GetPlayThumbnailInfo` (`0x6E8430`) desde `mp4Ifo_AVISequence` (`0x6E0AB8` → `0x1D7022` → `0x21F1F4`) y se escribe en `+0x124` desde `+0x100`; no está en `uuid`, `avc1` ni `AVIN0001.INP`, y `mdhd.timescale`/`stts` dan 25,000000 en el fichero convertido. Bypass evaluado: un solo consumidor (`0x447F52` desde `0x437C2C`), parche mínimo de 2 bytes (`0x61AA04`, `0x61AA30`) que conserva el rechazo por miniatura, pero la guarda A (``GetInhInfo`` `0x67B6E0`) también compara TvSystem. V2 (exponer el menú) descartada por inútil: `getValue`/`setValue` son `return 0` y `ActionNtscCaution::execute` exige `0x01070148==1`, que vale 00 en los 62 volcados. [Diagnóstico cerrado](../reports/film-pb-1-diagnostico-cerrado-20261127.md).

## FILM-PB-1 — NVRAM sin rastro de cambio PAL/NTSC (27-11-2026)
Leídas las 16 102 propiedades de los 64 volcados de NVRAM (`pmca.backup.BackupFile`; 32 parejas `backup_flash`/`backup_mem`, del 20-10-2026 al 22-11-2026): los cuatro únicos valores con forma de sistema de TV (`0x115002b`='N', `0x10706b1`='P\x01', `0x3c0412`='P', `0x69007c`='P') son idénticos en todos los volcados, y de las 176 propiedades que cambian entre el primero y el último (ajustes de las sesiones de pruebas: subsistemas 0x58 81, 0x107 49, 0x59 13, 0x3 7, 0x3c 6) ninguna es un selector N/P. `analysis/gui/process-bindings-a6000.json` lista `CustomNTSCPALSelection` como elemento sin id de respaldo. Conclusión: el sistema de TV no vive en la NVRAM y no ha cambiado; es fijo por firmware/región. Límite: no hay volcado posterior al CFW 3.93 (24-11). [Informe](../reports/film-pb-1-nvram-pal-ntsc-20261127.md).

## FILM-PB-1 — causa probable: sistema de TV frente a cadencia (27-11-2026)
Segunda tanda de subagentes (guarda B, motor, resume, AVIN, guarda A) y comprobación directa: `AviMMgr::isSupportContent` (ELF `0x61A8F0`, vtable `0x8E6E58`) devuelve 0 —y por tanto `0x437C3C` pone `0x1A`— cuando `TvSystem()` (`0x1EEFDC`) no casa con el `frameRate` del contenido (`[msg+0x124]`, 0..9): con `TvSystem==1` (PAL) valen 24p y 25/50/100/200 (enum 2/4/6/8); con `TvSystem!=1` (NTSC) valen 24p y 29,97/59,94/119,88/239,76 (enum 3/5/7/9; tabla en 0x686A34 y tbb de 0x77AF2C); >9 es «Unknown frameRate»; y hay un segundo rechazo si `GetPlayThumbnailInfo` (`0x6E8430`, selector `0x1F`) falla. Los clips son 30p (par, NTSC) y la cámara muestra `1-1-2014`, señal de ajustes reseteados; el firmware lo dice en `string_spanish.uxc` («Selector PAL/NTSC», «Imposible funcionar ya que el formato de película actual (PAL/NTSC) y el formato de película del soporte no coinciden»). Arreglo propuesto sin flashear: copiar los vídeos al PC, cambiar «Selector PAL/NTSC» al sistema contrario (NTSC para 30p) y reproducir; refutación: si el ajuste ya estaba en NTSC o el cambio no arregla, seguir con la traza del kit. [Informe](../reports/film-pb-1-causa-sistema-tv-20261127.md).

## FILM-PB-1 — nueve investigaciones en paralelo (27-11-2026)
Reparto: wbi, catálogo, kit de captura, restauración, motor, tarjeta, logs, clip y arnés. Resultados que cambian el estado: (1) `FUN_007211B0` es ELF `0x7111B0` y solo 6 de 65 536 entradas dan `0x1A`; los dos `bl` del manejador son `0x437C7E` (tras `0x447DA8`, hacia `vtable+0xB4` = `AviMMgr::MovieReadStart` `0x608698`) y `0x437CFC` (tras `PbStart` `0x307F54`, que devuelve 0 siempre según el motor, luego sería muerto). (2) Corrección de offsets: bloque `PbTimeInfo` en modelo+0x534, duración en 0x5AC/0x5B0/0x5B4, posición en 0x594/0x598/0x59C, cuadros en 0x5CC; 0x90…0x108 era `PbStatus`. (3) El catálogo queda descartado como fuente del `0:02`; gana la hipótesis del punto de reanudación (`Get/SetContentResumePoint` `0x8CAE60`/`0x8CB4B2`). (4) El índice de películas es `AVF_INFO\AVIN0001.INP` en la raíz del volumen (`nDuration` ms, `Duration90kHz`), no `M4ROOT\MEDIAPRO.XML`. (5) El MP4 es conforme al grabador. (6) El WBI no cubre `av-cam` ni `idt_cam` y el manejador no consulta el modo de arranque. (7) Logs: 4 líneas incondicionales a stdout de `im.elf`, búfer `0x83400000`. (8) `scripts/camera_filmpb1_trace.py` probado en seco (`--dry-run` EXIT 3, `--autotest` OK). (9) El arnés reproduce el mecanismo en Unicorn (`mpr_pb.py`, 8 pruebas verdes) pero no con un MP4 real. Plan P0–P3 en [camino final](../reports/film-pb-1-camino-final-20261127.md).

## FILM-PB-1 — auditoría del CFW instalado (27-11-2026)
Comparado byte a byte `build/cfw_func393/pp/files` contra el `/usr` de Sony 3.21: 32 ficheros distintos (5 `.so` parcheados, 22 `string_*.uxc`, `MANIFEST.json`, `SHA256SUMS`) y **`libmpr.so` ausente**, así que el productor del `0x1A` es código de fábrica. En `libObj` cambian 41 rangos / 506 B: 26 en `.text` en los puntos de `patch_libobj_pp.py`, `patch_libobj_ppeco.py` y `patch_libobj_eco.py`; fuera de `.text`, cabecera ELF (`e_shoff`/`e_shnum`), seis entradas de la tabla de descriptores PP en `.data.rel.ro` (marca 8→12 elementos, puntero a tabla de la cola) y `DT_REL`, que pasa a una copia byte a byte de `.rel.dyn` en un `PT_LOAD` añadido. Ninguna de las doce direcciones conocidas de la ruta de reproducción (`0x8C9BAE`, `0x8CC958`, `0x8CCDE0`, `0x8E95B0`, `0x42D5DC`, `0x42F7EC`, `0x41C964`, `0x4310BC`, `0x7258F8`, `0x942156`, `0x94A8A4`, `0xFD9248`) cae en un rango modificado y el mapa de errores es idéntico. Cámara no accesible (sin ping, sin USB, sin adb): la discriminación física queda pendiente. [Informe](../reports/film-pb-1-auditoria-cfw-20261127.md).

## FILM-PB-1 — productor de 0x1A cerrado estáticamente (26-11-2026)
Localizado el despachador del hilo FeaCore (`FUN_00429C38`, VA ELF `0x429C38`) y su `case 0x4000001D`, que llama al manejador real de PlayMovie (`FUN_00437BC0`, `0x437BC0`). Ese manejador produce el estado `0x1A` en tres puntos: guarda de capacidades sobre `[core+0xDB8]` («Pb Disable!! ref) dsm get»), guarda de contenido soportado por `vtable+0x58` («Detect UnSupported Content ») y traducción del último error cuando falla `MoviePlayerIf::PbStart` (`0x307F54`; `FUN_007211B0` tiene seis sitios que devuelven `0x1A`, p. ej. `0x1C00001A`). `0x1A` no es timeout, RAM ni demux: con una guarda fallida no se llama al motor. Falta discriminar el camino (log de MPR o breakpoints de un solo uso en `0x437C0A`/`0x437C3C`/`0x437CFC`). Del `0:02` se localizaron los campos del modelo (`M_SinglePbBase_Utils` en modelo+0x90: `m_durationOfContent` en +0x108, `m_pbTimeInContent` en +0xF0, h/m/s) y el camino de catálogo `MprIf::GetMovieContentProperty` (API `0x41000067`, `contentsDuration`), sin demostrar el enlace. [Informe](../reports/film-pb-1-productor-mpr-20261126.md).

## FILM-PB-1 — traspaso de traza física (25-11-2026)
La captura enlazó retornos inmediatos 0 de EnterMoviePb/PlayMovie con una finalización asíncrona `PlayMovieCmp: MPR::ER_FAILED=0x1A`, traducción a ObjPlayer 7 y caution 0x135. Causa raíz abierta. El usuario aportó MAH04198: 9,5095 s, 285 cuadros, vídeo decodificado completo sin errores; pantalla 0:02. Se archivaron las trazas válidas y se señalaron como inválidas las direcciones mal sumadas, el watchpoint derivado y los dos intentos repetitivos del callback MPR. Al entregar no quedan trazas físicas activas. [Informe y siguiente tarea concreta](../reports/film-pb-1-traspaso-20261125.md).

## FILM-PB-1 — control de arranque y descriptores (25-11-2026)

Verificados el tar/DAT 4.04, las tablas ELEM/D de 4.02 y las cadenas de configuración DMM del WBI de Sony. La 4.02 no tiene descriptores nuevos activos. El WBI contiene ambas rutas del mapa principal, sin demostrar qué mapa queda activo ni una reserva fallida. [G111 §14.1](../docs/gui/g111-film-receta-gui-iconos.md#141-verificación-de-los-dos-pendientes-offline).

La auditoría posterior trazó Play AVC → `AllocWorkMemory` → AllocNew DMM y contrastó el init del módulo con la reanudación de los extents. Se validó la salida de error en Unicorn con los bytes originales y respuestas sintéticas. [G111 §14.2](../docs/gui/g111-film-receta-gui-iconos.md#142-conexión-entre-arranque-dmm-y-decodificación-avc).

Réplica integrada posterior: 12 ejecuciones sobre Sony y los binarios extraídos de los tar 4.01/4.02. Las respuestas controladas suficientes llegan a la apertura y las tres clases de error devuelven 0xffff0001 en las tres builds. El fallo físico aún requiere sus entradas reales. Script y trazas en G111 §14.3.

Auditoría del protocolo: comando 1 = AllocNew, comando 5 = Open. Corregidos G111 §14.2–14.3. El mapa integrado carece de los cinco tipos auxiliares AVC; el asignador ARM original devuelve −3 para todos (6 tests). Se desconoce la tabla externa efectiva en el fallo. G111 §14.4.

Recuperados mapas externos de dos volcados FAT históricos, idénticos y con los cinco tipos AVC presentes. La rama 0 usa otros tipos (0x92043/0x92044), con tamaños declarados suficientes; la réplica forzaba rama 1. G111 §14.5 corrige el límite anterior y retira la ausencia de tipos del mapa histórico como explicación.

**Próximo paso exacto:** seguir estáticamente las reglas y solapamientos de 0x92043/0x92044, y los campos del analizador que seleccionan el tipo AVC. La causa del incidente sigue abierta.

## E26-RECOVERY — 29-10-2026: incidente abierto

**R8 completo offline:** [informe](../docs/capture/e26-r8-bootrom-uart-boss.md). Receptor serie BootROM reconstruido: `FUN_ffff1062` → `FUN_ffff0fa0` → `FUN_ffff0876` → `FUN_ffff0634`; MMIO `0xf2915010` bit 1; tipos 0/0xFFFF; checksum XOR+CRC8; parser offline `r8-uart-parser.py` (6/6 tests). Pines físicos UART no identificados (candidato GPIO(4,RDATA)=`0xf2910410`, CN4906 pin 9 vía R4003 XX sin continuidad verificada). No hay lectura de NAND vía protocolo. Escrituras NAND solo en Linux. INFO6 sin cambios desde R7. Seis preguntas de cierre: 1=SÍ, 2=NO DEMOSTRADO, 3=NO DEMOSTRADO, 4=NO DEMOSTRADO, 5=NO DEMOSTRADO, 6=NO. No existe ruta de recuperación sin Linux.

**R9 completo (29-10-2026):** [informe](../docs/capture/e26-r9-bootrom-ram-execution.md). Cadena BootROM→UART→RAM→salto a RAM demostrada estáticamente y en emulación Unicorn: tipo 0 hace `str(valor,[dirección])` sin validación de rango (`0xffff0bb8`, escritura RAM arbitraria); tipo 0xFFFF almacena dirección de salto de 32 bits en `0xc000500C` y `FUN_ffff0144` (`0xffff0144`: `ldr r1,[0xc0005000]; ldr r0,[r1,#0xc]; bx r0`) transfiere el control a eSRAM. eSRAM `0xc0000000–0xc0100000` (16 MiB) demostrada usable y ejecutable en tiempo de BootROM. Sin firmas ni Linux. CRC8 corregido: polinomio `0xEDB88320` (`0xffff0c04`), iterativo por byte, no placeholder `0x07`. Scripts: `analysis/e26-recovery/r9-uart-protocol.py` (parser + constructor) y `r9-unicorn-ramjump.py` (Unicorn; PC transfiere a eSRAM). Tests: `tests/test_e26_r9_*.py` (19/19 pasan). Pines físicos UART no identificados (NO DEMOSTRADO; requiere autorización física separada). Q1–Q10: Q1=SÍ, Q2=SÍ, Q3=SÍ, Q4=NO, Q5=SÍ, Q6=SÍ (emulado), Q7=SÍ, Q8=NO DEMOSTRADO, Q9=viable estática+emulada / no demostrada en hardware, Q10=identificación eléctrica del contacto UART. Sin escritura NAND, sin flasheo, sin payload en hardware físico.

**R7 completo offline (29-10-2026):** [informe](../docs/capture/e26-r7-recuperacion-estatica.md). Grafo de rutas de arranque verificado en binario: `FUN_c01f11ec` init completo (Sync,Power,UDIF,BOSS,DDR,DGU,BlkDev,FAT,Backup,Pwr2nd); modo 3=`FUN_c01f1378` carga vmlinux+initrd desde dev1 vía `FUN_c01f068a()` y salta al kernel vía `FUN_c01f04b6()`, sin entorno de recuperación independiente; modo 0xc (COLD)=`FUN_c01f09e4` carga desde dev3, fallo→`FUN_c01f3b74` bucle LED infinito sin retorno ni fallback; escrituras/borrados MuMin/LLD→ARM7 solo en entorno Linux; `boss_hw_nandc_recovery_check` 0x17b8c maneja errores NAND, no es UPDATER; no hay productor pre-Linux de `updater/mode`; INFO6 (21 páginas) sin fuente; residuo TPZL 256 sin rechazo demostrado por ARM7; escritura selectiva de `nflasha3` preservando metadatos no demostrada. Receptor serie BootROM sin red física identificada ni cadena de escritura NAND. Conclusión: no existe ruta de restauración utilizable antes de `nflasha3` con evidencia actual.

**R6 fases 2/3, checkpoint:** prefijo de 43 páginas sin cambios, REA/Capstone confirman las cinco rutinas del selector, sin reconstruir cola INFO6 ni certificar runtime. Nueva condición de log: Backup510015 debe valer1; histórico00, de modo que silencio UART no prueba falta de ejecución. Puerto0/1 y registros compatibles PL011; reloj y mux no certificados. 73 tests knowledge pasan excluyendo seis de servidor MCP (espera sin respuesta en entorno), 12 triage pasan; no cambios al servidor. Próximo paso exacto: usar dibujo SIDE A6-38 para orientación CN4906 y documentar niveles/SWD/NAND, sin conexiones.

**R6 fases 4–8, checkpoint:** manual SIDE A6-38 fija CN4906 con pin1 arriba/pin16 abajo y entorno fotografiable; se publicó mapa SVG documental. SWD BIONZ sigue opcional por R4911/R4912 XX, sin puerto, tensión, protección ni acceso NAND demostrado. BLDR/MuMin no autorizan NAND cruda; las vías restantes son Loader3 condicionado, servicio BIONZ demostrado o diagnóstico profesional que obtenga lectura repetible. Se redactó matriz conservadora: foto identificada → UART pasiva → clasificación de etapa; sin conexión, energía, escritura ni imagen firmware. Próximo paso exacto: esperar autorización física y fotografías; no hacer más inferencia de recuperación ni activar SWD.

**R5, checkpoint vigente:** [Loader3 y servicio](../docs/capture/e26-r5-loader3-servicio.md). REA + bytes amplían selector, inicialización y dependencia Backup; el recorte contiguo NO queda íntegramente validado (suma32 05c12355 frente a INFO eda2f689, tabla/runtime final incoherentes). Bandera mode sin contenido → 3; recepción alternativa SIO REIO condicionada, deshabilitada con Backup histórico 51001c=01. CN4906 A contiene UART0 BIONZ 4/5 y SWD opcional 11/12 por R4911/12 XX, además de Darwin. CompleteUpdate crea comp/borra mode; HasError y landing pads setError comprobados, éxito FIFO2=2; UI Done y ciclo uincomp pendientes. Inspector reforzado tras regresión fallida; 3 tests E26, ruff y mypy explícito sin errores. Sin fotografía local, conexión ni medición física; sin imagen instalable. Evidencia derivada en `analysis/e26-recovery/r5-rea.json`; respaldos originales privados intactos.

**Próximo paso exacto R5:** localizar la implementación de `bootloader_get_blocks`/`bootloader_read_block` en la revisión de OpenMemories-Platform usada por BLDR y reconstruir el mapa INFO 5→6; no repetir búsqueda de Loader3 ni interpretar su cola incoherente. En paralelo documental, falta manual de flash MB9AF004B y especificación física NAND. Cualquier captura propuesta espera foto, continuidad/nivel y autorización separada; el trabajo sigue offline. Pendientes E26-R5-* en el índice maestro.

Fase A: REA sobre `nand.ko` (`muminlzp_register` 0x12520, `muminlzp_request` 0x11d50) y `lld.ko` (0x11048/0x10e0c) identifica TOC, advertencia de offset y entrega ARM7; falta implementación ARM7 y nexo con lectura inicial. Tablas binarias comparadas y tres imágenes descomprimidas, tercera solo en memoria; 17 pruebas, ruff y mypy sin errores. Siguiente paso exacto: Fase B, analizar llamadores reales de `SenserUpdaterIF::setResult` en `libupdaterbody.so` y registrar argumentos y conversiones; no volver a atribuir el LED sin evidencia.

Fase B parcial: `libsenupdater.so` de initrd `nflasha1` y `mf` trazados con REA; `setResult` convierte nibbles hex y `mf` transmite por FIFO2 el valor de excepciones `0x3000c`; `BuildInPlugin::execute` acepta un resultado de shell 50 como valor 0x32. Pendiente identificar script real y conexión de excepciones, y trazar Done. Los binarios extraídos están solo en `/tmp/e26-updater/root`, no se publican.

Fase C iniciada: `config.xml`, `us_crc32sum.sh`, `us_darwin_firm.sh` y `endupdate.sh` delimitan comprobaciones, hilo Darwin y operaciones de cierre; sin orden demostrado respecto a Done. REA: `ThreadPlugin::Join` 0x23d88 ejecuta `pthread_join`; `XmlConfigHandler::Join` 0x23768 usa una llamada virtual. Próxima operación: resolver llamador del thunk 0x1db8c, destino virtual y mensaje de éxito al host; Fase B mantiene pendiente el script real del byte 0x32. El usuario informa una cara de la placa expuesta, sin acceso físico autorizado.

R3: `UpdaterBody::Execute` 0x1f4c8 → thunk 0x1db8c → `XmlConfigHandler::Join` → `ThreadPlugin::Join` 0x23d88 (objeto construido en 0x23964, vtable 0x30fa0 +0x10); después `HasError`, `EndUpdate`, `CompleteUpdate` 0x2516c y retorno. `CompleteUpdate` borra clases de banderas de modo y crea la de completo. Enlace al Done del PC pendiente. Próxima tarea: Loader2 0xc0030000 y localización de Loader3, sin repetir BootROM.

R3 Loader3: `bootloader.bin` INFO 0x18000, entradas 5→6 y candidato continuo 0x22800–0x427ff (SHA 8fd98a41…); Loader2 carga índice 5 en 0xc01f0000. REA del candidato: comprobación `\\updater\\mode` 0xc01f159a, selector 0xc01f1de6, modo 3 0xc01f1312, carga de kernel/initrd de dispositivo 1 0xc01f068a. Pendientes integridad/geométrica, modo físico y condiciones previas. Próximo paso: diagrama SIDE A/B de SY-1028 y accesibilidad de servicio.

R3 placa: manual PDF páginas 50/51 verifica CN4906 e IC6000 lado A e IC5700 y CL5701/CL701/CL703–707 lado B; esquema PDF 23 determina señales de islas. Sin foto de la cara visible ni identificación física de NAND, no se puede concluir acceso. Matriz de recuperación y siguiente diagnóstico documental en E26. Próxima operación: resolver indicador `mode`/`uincomp` y origen `Done`; validar geometría del candidato Loader3 sin escribir hardware.

El usuario informa instalación 3.25, Done y bloqueo. Comprobados hashes FDAT, Darwin y `nflasha3` locales y anomalía de alineación en el manifiesto; aún no se verifica causalidad ni lector real. Ver [informe](../docs/capture/e26-recovery.md). Siguiente paso exacto: inspeccionar con REA `uc_portctl.elf` y `SenserUpdaterIF::setResult`, y contrastar las tablas TPZL directamente con los binarios. Sin acceso físico.


## E25-24 — Selector EFCS / Electronic, auditoría parcial — 28-10-2026

Se actualizó la base a `1edcf13a` y se contrastó el informe de referencia con
E020 y E25-18–23. La opción binaria es candidata, sin implementación: B1a es
global y no hay conmutación demostrada que restaure el EFCS original. Se
registraron contradicciones sobre `r5`, C3 y el mecanismo, y los pendientes
E25-24/E25-25. Sin cámara ni pruebas físicas. Próximo paso: censar consumidores
y persistencia del selector con REA y bytes y buscar un canal por captura hacia
Darwin, antes de preparar código o solicitar pruebas físicas.

## E25-16 — Cálculo autónomo de `r5` en BIONZ — 28-10-2026

Sesión 100 % offline (bytes, REA y emulación Unicorn; sin cámara). Hallado el productor nativo de
`r5`: `0x4383fa40(record, settings)`. Lee el Tv de `record+0xf6`, el período de línea de
`record+0xc`, el VTS de `record+0x20`, el suelo de `record+0x1c` y el multiplicador de
`settings+0x4b8`; escribe `r5` en `record+0x64` y ShutMode 0 en `+0x6d`. Lo llaman el constructor
normal (`0x437b46d0`, compuerta `[cap+0x11b0]`) y el EFCS (`0x438417c0`). La foto medida no lo usa
(r5=1); `0x4383fd6c` copia `record+0x64..0x73` a `cap+0x64c` y `0x438c828c` llega a `SetExposure`
(`0x436d6320` → vtable +0x28 → `0x436d6f6c`). La emulación con VTS 4219 reproduce T047 (±1 línea:
4203/4154/3956/3122); con 4266 se desvía 47 líneas (0,71 ms). 1/15 y mayores saturan a 0 (negro), no
son compatibles; >1 cuadro, bulb y 30 s siguen sin mecanismo. No se hardcodea 4219: el diseño usa el
campo del registro; su valor real no se verificó (T052 fase A). C3 (tras `0x437f8a50`, antes de
`0x436d6320`, copia a scratch + `0x4383fa40`) es la vía lógica recomendada; no hay parche instalable.
29 pruebas nuevas; 59 con E25-14/E25-15. Informe:
[E25-16](../docs/capture/e25-16-r5-autonomo-fotografia.md).

## T052-A — VTS real y preparación de C3 — 28-10-2026

**No ejecutada físicamente:** la cámara no era accesible (PC en `192.168.0.0/24`, sin ruta a
`192.168.1.29`, sin `adb`/`pmca`; barrido sin shell). Sin escrituras. Se completó A0 y la emulación, y
se usó el volcado real del 20-10 (1 GiB, reposo, sin foto) para confirmar el mapa: GOT
`0x4401eee4`; registro A `0x43ea5b4c`, B `0x43eee770`, ajustes `0x43f79f94`, imager `0x43ea976c`,
gate B `0x43f6e5c2`, predicado `0x43deb360`. **VTS:** `record+0x20 ← cap+0x5e0 ← [descriptor+6]`
(`0x43846e12`; descriptor en `[param+0x3c]` de `0x43844e80`); 4219 no es constante y 4266 solo lo
produce la vista en directo (`0x4385de94`); el valor de foto sigue **N**. **Compuerta:** `0x437b3b08`
la deriva de `[imager+0x504]==3` o `[gate B+0x8c]==1` (2 fuerza 0); en reposo 2/0 → 0. **Correcciones:**
el 2.º argumento del productor es el imager (`+0x4b8`), no `settings`; el productor escribe también
`+0xd8/+0xda/+0xdc`; el predicado `0x43a12ca8` lee `[0x43deb360+0x10]` y en reposo devuelve 1 → suma
un cuadro (r5 8422/8175/7341, inválido). C3 **no autorizada**; T052-B0 de solo lectura primero.
22 pruebas nuevas; 81 con E25-14/15/16. Informe:
[T052-A](../docs/capture/t052-a-parametros-reales.md).

## E25-14 — Temporización IMX235/IMX210 — 28-10-2026

Sesión 100 % offline (solo bytes; sin cámara ni emulación de sensor). Reconstruida la cadena Silent del
IMX235: `cap+0x648` → `SetExposure` (`0x436f4168`; `param+0`=SHR/líneas, `param+9`=ShutMode) y
`cap+0x6b0` → método de velocidad (`0x436f4a94`, `vtable+0x30`) → bloque de comandos. La A6000 tiene el
mismo contrato (`0x436d6f6c`/`0x436d7e08`), la misma tabla de tiempos (30 filas idénticas) y **ya llama
al método `+0x30` en la foto** (`0x438c831e`); lo que no usa es ShutMode 0. El armado de exposición
larga del A7S (`0x436f43c0`, `obj+0x3dc=2`, `0x43b73044(0xe)`, tercer argumento `r3`) no tiene
equivalente en el método del IMX210. El límite de ~65 ms es también del firmware (clamp a un cuadro);
no se demostró ningún modo de sensor con cuadro más largo ni acumulación multicuadro. **A=SÍ, B=NO,
C=NO, D=NO, E=NO, F=PARCIAL, G=NO, H=NO, I=NO, J=NO, K=SÍ, L=NO, M=NO.** 13 pruebas en
`tests/test_e25_14_exposicion.py`. Informe:
[E25-14](../docs/capture/e25-14-imx235-imx210-exposicion-electronica.md).

## E25-06 — Auditoría independiente de los paquetes 3.23 (B1a) y 3.24 — 27-10-2026

Auditoría 100 % offline del commit `88ce09ef` (paquetes de DeepSeek). Parsers propios de `.dat`, FDAT y
tar; descifrador AES propio validado contra el `.dat` original de Sony; `uc_crc32sum` reproducido sobre
los 7 `*.sum`; B1a emulado con Unicorn frente al tipo 0 y al original (retorno 0 en 259 entradas, sin
`0x1b080`, L0 en los tres arrancadores, escritores P4D/P4E filtrados con control positivo, comprobación
de leva suprimida, operación 5 sin cambios). **145 comprobaciones, 0 fallos; 21 pruebas (15
negativas).** A–K = SÍ, L = NO (sin defecto binario), M = NO (las pruebas de E25-05 pasan sin paquetes:
2 passed / 9 skipped; el manifiesto no puede registrar FAIL; hay comprobaciones de constantes), N = SÍ,
O/P/Q/R = NO por evidencia insuficiente. 3.24 vs 3.23: rangos del `.dat` predichos desde el formato =
reales. Riesgos comprobados: R4, R5, R6, R7 (dos 3.23 con `config-323.yaml` idéntico) y R8 (el
inventario R1 no tiene los paquetes nuevos). Nuevo pendiente E25-07. Informe:
[E25-06](../docs/capture/e25-06-auditoria-independiente-paquetes.md).

## E25-05 — Paquetes offline 3.23 (B1a) y 3.24 (recuperación) — 27-10-2026

Sesión 100 % offline sobre `81fab68e`; no se conectó la cámara ni se flasheó nada. **Plan de versiones
corregido**: con 3.22 instalada, `3.22 < 3.23 < 3.24`; la prueba pasa a 3.23 (tipo 0 + B1a) y la
recuperación a 3.24 (Darwin oficial). El antiguo `recuperacion-323` queda superado (misma versión que la
prueba) y se conserva intacto. Paquetes en directorios separados: `experimental-323` (`.dat`
`4c21353d…`, `.fdat` `268621fb…`; tar oficial + B1a + `darwin.sum` `cf930ac9`) y `recuperacion-324`
(`.dat` `e1345aff…`, `.fdat` `24ee9b42…`; payload oficial extraído del 3.23 verificado). **69
comprobaciones, 0 fallos**: DEND, CRC de cabecera FDAT, sumas por bloque, hashes, modelo `0x41030035`,
región 0, versiones BCD `0x23`/`0x24`, `fwtool unpack`. B1a vs tipo 0 = **exactamente 2 bytes**
(`0x1fe6a: 28 46 → 0a e0`); tar experimental solo cambia los dos ficheros Darwin; el 3.24 vs 3.23 solo
difiere en cabecera (`[8,12)`, `[32,33)` en `.fdat`; dos bloques AES + CRC DEND en `.dat`). **Rollback
limitado**: el 3.24 solo funciona si la cámara conserva acceso al actualizador; no es recuperación
independiente del MCU y no está demostrado que recupere un Darwin defectuoso. B1a sigue sin ser
instalable (E25-04 G=NO). Script `scripts/e25_05/build_packages.py`, 11 pruebas, manifiestos en
`analysis/e25-05/`. Informe: [E25-05](../docs/capture/e25-05-preparacion-paquetes-323-324.md).

## E25-04 — Recuperabilidad de Darwin y decisión sobre B1a — 27-10-2026

Auditoría 100 % offline (base `9d85cae9`). **A=NO, B=NO, C=NO, D=NO, E=SÍ, F=NO, G=NO.** No hay
recuperación independiente de la aplicación Darwin demostrada: el USB depende de `DD_ON1/2/3` de
`darwin_core`, el acceso al bootloader sin la aplicación no está demostrado y el puerto físico
(`MD0_DWN`, `XDWN_RESET`, UART, SWD, `CN4906` no montado) está documentado pero no verificado. El plan
3.24/3.25 es formalmente correcto, pero el 3.23 no recupera un Darwin defectuoso y, si se instala 3.24,
la recuperación debe ser ≥3.25. R1: procedimiento `scripts/recovery/r1_manifest.py` + inventario;
manifiesto local 62/62, 0 requeridos ausentes, `verify` OK contra el origen; **la copia externa no está
hecha ni verificada**, así que R1 sigue abierto. F = NO: L0 no tiene contradicción estática con BIONZ
(estado 9 libera el bit 24, el 10 es terminal, los mensajes obligatorios salen de la máquina de captura,
el estado 31 no cambia); P29, `pkt[2..3]` y el lector BIONZ del fin siguen abiertos. Pruebas nuevas:
`tests/test_e25_04_recuperabilidad.py` (2) y `tests/test_r1_manifest.py` (6); 239 pruebas E24/E25 verdes.
No se generó FDAT, no se tocó B1a y no se abrió la cámara. Informe:
[E25-04](../docs/capture/e25-04-recuperabilidad-y-decision.md).

## E26-R10 — USB Charger `054c:0994` como ruta de recuperación (29-10-2026)

- **Objetivo:** investigar si el único dispositivo USB que enumera en la a6000 bloqueada (054c:0994, cámara apagada) permite una ruta de recuperación que evite la intervención física UART.
- **Componente identificado con evidencia de binario:** **Darwin** (FM3). `darwin_core.bin` contiene el descriptor USB completo con VID `0x054c`, PID `0x0994`, clase HID, EP1 IN interrupt de 8 bytes y cadenas "Sony"/"USB Charger". Validación offline contra `lsusb -v`: **todos los campos coinciden** (script `analysis/e26-recovery/r10-usb-descriptor-parse.py` + 4 tests `tests/test_e26_r10_usb_charger.py`, 4/4 pasan). `bootrom.bin` **no** contiene `0x0994`/`0x054c` (búsqueda negativa).
- **Tres modos USB confirmados:** normal `054c:07c4` (MSC/PTP, cámara encendida), updater `054c:03e2`, charging `054c:0994` (Darwin, cámara apagada). `CMD_SWITCH_MODE = 0x30` (PMCA) pertenece a las interfaces `07c4`/`03e2`, **no** a `0994`; no hay relación demostrada.
- **Hallazgos clave:** la interfaz HID declara **solo un informe Input de 1 byte** (sin Output ni Feature, sin canal host → dispositivo). No se localizó el manejador de solicitudes de control (SETEP) ni peticiones vendor-specific de Sony en `darwin_core.bin`. El módulo DWN de Darwin (`DWN_VER0.78` + tabla de salto de 20 punteros en `0x021950`) es **pista futura no demostrada** (no demostrado USB-accesible ni capaz de cambiar modo). No existe cadena demostrada desde USB Charger hasta escritura de RAM, salto a ejecución o activación de Updater Mode.
- **Decisión de cierre: Opción B** — abandonar provisionalmente la ruta USB Charger y concentrar la recuperación en BootROM UART de R9. Respuestas Q1–Q10: Q1=SÍ, Q2=SÍ(binario)/NO(físico), Q3=NO, Q4=NO, Q5=PARCIAL, Q6=NO, Q7=NO, Q8=NO DEMOSTRADO/NO, Q9=módulo DWN no demostrado, Q10=priorizar BootROM UART.
- **Entregables:** `docs/capture/e26-r10-usb-charger-recovery.md`, `analysis/e26-recovery/r10-usb-descriptor-parse.py`, `tests/test_e26_r10_usb_charger.py`. Sin cámara, sin escritura, sin flasheo, sin intervención física.

## E26-R11 — Acceso físico al BootROM UART (29-10-2026)

- **Hallazgo:** esquema pág. 38: `BOOT_SERIAL_IN` → `MULTI pin 9 UART_RX/BOOT_IN` (CN4001) vía R4003/R4002, ambas `XX`. CN4906 pin 4 = `DEBUG_UART0_RXD` (montaje no verificado). CN4906 pin 9 ≠ Multi Terminal pin 9.
- **Selector BootROM:** `0xf2915010` bit 1 es estado externo leído; condición de activación, niveles y baudios no determinados.
- **Auditoría R9:** eSRAM 1 MiB (`0xc0000000–0xc0100000`), `0xEDB88320` = CRC-32 reflejado, salto indirecto compatible con la carga de prueba; válida offline, sin hardware.
- **Decisión C.** Q1–Q8=NO, Q9=PARCIAL, Q10=SÍ, Q12=CN4906. Pendiente `E26-R12-UART-FISICO`.
- **Entregables:** `docs/capture/e26-r11-bootrom-uart-physical-access.md`, `analysis/e26-recovery/r11-pinout-reconstruction.py`, `tests/test_e26_r11_pinout.py`. Sin cámara, sin UART, sin intervención física.

## E26-R12 — Auditoría estática del arranque (30-10-2026)

- **Selector:** MODEREG `0xf2915010` bit0 (`ffff1094..109e`); 1 → serie, 0 → almacenamiento. Registro externo.
- **LED:** BootROM ≤ 2 lentos; Loader2 −302 → 0/3/2 (hipótesis para el patrón 3+2). Corrección R7 `0xfffffed1`→`0xfffffed2`.
- **Darwin:** `PwrCtrl` Fase1..4, watchdog virtual, SIO `mss` (hipótesis hacia BIONZ).
- **Entregables:** `docs/capture/e26-r12-bootrom-static-audit.md`, `analysis/e26-recovery/r12-loader2-led-codes.py`, `r12-selector-emulation.py`, `tests/test_e26_r12_led_codes.py`.

## E26-R13 — Procedencia del error LED (30-10-2026)

- **Identidad:** `FUN_c01f3b74` = Loader3 (corrige R12); gemela Loader2 `c0030c7c` con `err−1000`.
- **−302:** 7 funciones, 9 cargas; 3 devuelven −306. Propagan al LED: BOS `c01f2c98` y CFG `c01f2f24`.
- **Tiempos:** `d`=2,0 s (timer DIV2, entrada 4 MHz según cabeceras Sony; sin medir). Ciclo de −302 = 8,0 s.
- **Entregables:** `docs/capture/e26-r13-led-error-provenance.md`, `analysis/e26-recovery/r13_loader3.py`, `r13-led-provenance.py`, `tests/test_e26_r13_led_provenance.py`. Pendientes `E26-R14-RAMCFG`, `E26-R14-LED-MEDIDA`.

## E26-R14 — RAMCFG, BOS y FAT de Loader3 (30-10-2026)

- **RAMCFG:** Backup BK4 `0xfa0080`, 64 entradas de `0x90` B (6 usadas); idéntico en 55 BK4 (volcados, `nflasha2`, paquetes 3.21/3.25).
- **Particiones:** 2 = FAT12 (`\Backup.bin`, `\kemco.txt`); 3 = TPZL→FAT12 (resto). BOS sector 0 = `8246`.
- **−302:** `c01f4690` convierte todo fallo de sector en −302; BOS: lectura −1, firma −302; Backup no en estado 1 → −303.
- **Entregables:** `docs/capture/e26-r14-ramcfg-bos-analysis.md`, `analysis/e26-recovery/r14_backup.py`, `r14-ramcfg-bos-fat.py`, `tests/test_e26_r14_ramcfg_bos.py`. Pendientes `E26-R15-*`.

## E26-R15 — TPZL de Loader3, firmware 3.25 propio y c01f2282 (30-10-2026)

- **Procedencia:** 3.25 = paquete propio (E25-27) sobre 3.21 oficial; 4 de 73 miembros del tar difieren; `updater.img` oficial; Loader/Backup/kernel intactos. Sin logs de instalación.
- **Lector TPZL:** registro `c01fe4ec`, petición `c01fdd8e`; residuo ≠ 0 solo avisa; sectores `(res+tam+0x1ff)>>9`. Las 3 imágenes pasan.
- **`c01f2282`:** omite solo si Backup `0xfa0033` ∈ {1,2}; vale `0x80021048` en 55 BK4 → nunca.
- **Entregables:** `docs/capture/e26-r15-tpzl-custom-fw325.md`, `analysis/e26-recovery/r15_tpzl_loader3.py`, `r15-mode-table.py`, `tests/test_e26_r15_tpzl.py`. Pendientes `E26-R16-*`.

## E26-R16 — Ruta LDEC/BOSS/ARM7 del TPZL 3.25 (30-10-2026)

- **Ruta:** Loader3 `c01fdd8e`→`c01fce8c`→MuMin→SRAM ARM7 `+0x3f40`→BossFirm `0x1338`→LDEC `0xf2903000`; sin descompresor software en Loader3. `0x2800` (NAND/firmware) excluido del grafo.
- **Diferencia nueva (decisión C):** 100 % del corpus Sony = 16 segmentos × 4096 B por bloque (`size>>12`=16 va al registro `+0x0c`); bloques 0/48/57 del 3.25 = 1 × 65 536 B. Sin rechazo demostrado.
- **Límites:** 129 sectores funcionan (Sony `nflasha15/16`); ARM7 trocea en lotes de 0x80; residuo copiado y no leído en lo analizado.
- **Conciliado:** 89 B BIONZ + 22 B Darwin = 111; `c01f7752` no carga archivos ni da −302; fallos `tests/knowledge` desde R7 (`a8a182c9`).
- **Entregables:** `docs/capture/e26-r16-ldec-hardware-audit.md`, `analysis/e26-recovery/r16_*.py`, `tests/test_e26_r16_ldec.py`. Pendientes `E26-R17-*`.

## E26-R17 — BossFirm ARM7 y semántica LDEC (30-10-2026)

- **ARM7:** todo ARM; despachador `0xec8` (`bx r1`) sobre 18 punteros `0x379c`; op 0 = `0x1338`. LDEC (`0xf2903000`) solo en `0x3f4` (config), `0x43c` (ISR, errores `0x28–0x2d`), `0x4d8` (arranque).
- **Hallazgos:** `+0xc` se escribe una vez desde `trabajo+0xc` y no se lee ni compara; `trabajo+8` sin lector en la op 0; tulist síncrono por tanda de 0x80 (`0x5f8` sondea `[0x378c]`).
- **Decisión C.** No ejecutado: corpus Sony externo (`E26-R17-TPZL-1SEG` abierto), trazado de otras ops (`E26-R18-ARM7-RESTO`).
- **Entregables:** `docs/capture/e26-r17-arm7-ldec-segment-analysis.md`, `analysis/e26-recovery/r17_arm7_full.py`, `tests/test_e26_r17_arm7.py`.

## E26-R19 — capa USB de Darwin y esquema de arranque (30-10-2026)

- **Pedido:** avanzar hacia una vía de arranque/actualización; USB Charger, Multi, CN4906 por código; luego resolver el callback USB de clase/vendor.
- **Hallazgos:** mapeo dirección = archivo + `0x4200` (primera pasada lo ignoró y dio rutinas desalineadas; corregido). EP0 `0xc90a`; callback `0xc59c`: GET_DESCRIPTOR HID, GET_REPORT, SET_IDLE; vendor parado; sin OUT; Darwin sin flash/MFS en código; DWN (`0x2f50–0x4ba8`) sin referencias. Esquema: `CM4002/CM4003` en paralelo a R4002/R4003 XX (patrón de montado) → Multi pin 9 ↔ `BOOT_SERIAL_IN` probable (corrige R11); `BOOT_MAIN`→CL1000 candidato a bit 0 de `MODEREG`; CN4906 no llega a `BOOT_SERIAL_IN`.
- **Decisión:** USB Charger cerrado (límite documentado); resto C. REA no reconoce el Thumb de `darwin_core.bin`; desensamblado con Capstone y emulación Unicorn.
- **Entregables:** `docs/capture/e26-r19-darwin-usb-static.md`, `analysis/e26-recovery/r19_darwin_usb.py`, `r19_darwin_usb_emu.py`, `tests/test_e26_r19_darwin_usb*.py`.

## E26-R20 — selector del BootROM (30-10-2026)

- **Pedido:** reconstruir `ffff1062–109e`.
- **Hallazgos:** el BootROM es `Musashi Loader1 Ver.01.00` (2011). Selector = `MODEREG` bit 0 (0 → Loader2; 1 → ruta de servicio). GPIO(4,RDATA) bit 21 = juego de temporización, bit 22 = salto directo a la recepción serie. Con bit0=1 y GPIO4.22=0: fallo de almacenamiento/cabecera o tabla de claves vacía → serie; clave presente → hay que enviarla (4 B + CRC-32 `0xEDB88320`), sin datos → payload alternativo. Bit 0 = `BOOT_MAIN` (CL1000) por exclusión y por el registro hermano CXD4132; por defecto 0 en uso normal.
- **Verificación:** REA (descompilación de `main`), Capstone y emulación Unicorn con auxiliares sustituidas (9 escenarios, 4 pruebas).
- **Pendientes:** `E26-R20-BOOTMAIN-NIVEL` (físico), `E26-R20-KEYTABLE`, `E26-R20-GPIO4`.
- **Entregables:** `docs/capture/e26-r20-bootrom-selector.md`, `analysis/e26-recovery/r20_bootrom_selector.py`, `tests/test_e26_r20_bootrom_selector.py`.

## E26-R20-KEYTABLE — mecanismo de la tabla de clave (30-10-2026)

- **Pedido:** resolver `E26-R20-KEYTABLE`.
- **Hallazgos:** `0xffff1352` (llamada desde `0x150/0x332`) es un lector real de sectores de `0x600` B desde un controlador de bloque en `0x20000` (FIFO `0x10000010`), con reintentos; solo pone a 0xFF un array de estado por sector (`memset` vía `0xffff1814`), no el buffer de datos. El sector que correspondería a `0xc0001200` vive en la partición `nflasha0` (área de boot/loader1), que según `analysis/camera-dumps/nand-20261020/README.md` **no tiene nodo de dispositivo Linux y nunca se volcó**; `bootloader.bin` (paquete `EXBL`) es una etapa posterior sin relación con esa zona.
- **Decisión:** C — mecanismo cerrado estáticamente; contenido («vacía»/«con clave») no determinable sin volcado físico/JTAG del área de boot.
- **Entregables:** `docs/capture/e26-r20-keytable.md`, `tests/test_e26_r20_keytable.py`.

## E26-R19/R20 — cierre estático de pendientes restantes (30-10-2026)

- **Pedido:** cerrar de forma estática `E26-R19-USB-EVT13`, `E26-R19-CM-MONTAJE`, `E26-R20-BOOTMAIN-NIVEL` y `E26-R20-GPIO4`.
- **Hallazgos:** `post(0x13)` = registro de traza; EP1 IN único; `CM4002/3` montados por convención; `BOOT_MAIN` sin pull externo; GPIO4 bit21 elige entre dos tablas de muestreo serie por software (250/84 ticks por bit), bit22 salta a serie.
- **Límites:** baudios absolutos, pines de GPIO(4) y nivel de `BOOT_MAIN` no determinables sin hoja de datos del IC6000 o medición.
- **Entregables:** `docs/capture/e26-r19-r20-cierre-estatico.md`, `tests/test_e26_r19_r20_cierre.py`.

## E26-R21 — receptor serie del BootROM (30-10-2026)

- **Pedido:** seguir con lo hallable sin mediciones físicas.
- **Hallazgos:** código Sony del SoC (`mach-cxd90014`) confirma `MODEREG` bit 1 = `BOOT_SERIAL_IN`; `0x634` es un receptor serie por software (8 datos + paridad impar + parada); tablas de 250/84 ticks por bit ≈ 16 000/47 600 baudios con reloj base 4 MHz.
- **Límite:** reloj del temporizador inferido de Linux; pin de GPIO(4) bit 21 desconocido.
- **Entregables:** `docs/capture/e26-r21-bootrom-rx-serie.md`, ampliación de `tests/test_e26_r19_r20_cierre.py`.

- **R21 ampliación:** descubierto el tren de sincronismo de 60 flancos previo a los bytes (corrige «sin sincronización» de R8/R9) y validado con `analysis/e26-recovery/r21_rx_emulation.py` (Unicorn, ROM real; ambos perfiles aceptan 8O1, rechazan periodo/paridad/flancos erróneos).

## E26-R22 — mapa completo del BootROM (30-10-2026)

- **Pedido:** identificar todo el BootROM de principio a fin.
- **Hallazgos:** 57 rutinas (0xffff0000–0xffff1a80) nombradas; capa de carga de bloques, claves, consola/traza, CRC, `printf`; reloj de 4 MHz verificado por las dos variantes del parpadeo de error.
- **Límite:** nombres propios; `0x2001–0x2005` y pasos de traza sin asociar a condiciones concretas.
- **Entregables:** `docs/capture/e26-r22-bootrom-mapa-completo.md`, `analysis/e26-recovery/r22_bootrom_map.py`, `tests/test_e26_r22_bootrom_map.py`.

## E26-R23 — flujo completo de main/serial_entry, cierre total del BootROM (30-10-2026)

- **Pedido:** no detenerse hasta obtener todo el BootROM.
- **Hallazgos:** pseudocódigo línea a línea de `main` y `serial_entry`; 109 pasos de traza y 25 códigos de error resueltos a su sitio emisor exacto; corrige R12 §3 (cabecera dañada desvía a `serial_entry`, no es éxito aparente).
- **Cierre:** el BootROM queda completo en estático; lo que falta es físico (`E26-FISICO-BOOT`).
- **Entregables:** `docs/capture/e26-r23-bootrom-flujo-completo.md`, `analysis/e26-recovery/r22-trace-steps.json`, `analysis/e26-recovery/r22-error-codes.json`, `tests/test_e26_r23_bootrom_flujo_completo.py`.

## E26-R24 — mapa completo de Loader2 (30-10-2026)

- **Pedido:** seguir con Loader2 (`bootloader.bin`), completo.
- **Hallazgos:** 247/247 funciones localizadas y con rol; secuencia de arranque `loader2_main` completa por cadenas `LDR:`/`BOS:`/`INS_E:`; entrada ARM→Thumb verificada por bytes; handoff a Loader3 (`0xc01f0000`); confirma −306→1/3/6 (R13) y el temporizador de 4 MHz (R22) de forma independiente.
- **Límite:** 153 funciones de soporte (RTOS interno) solo inventariadas por dirección/grafo, no narradas una a una.
- **Entregables:** `docs/capture/e26-r24-loader2-completo.md`, `analysis/e26-recovery/r24_loader2_map.py`, `r24-loader2-functions.json`, `r24-boot-sequence.json`, `tests/test_e26_r24_loader2_map.py`.

## E26-R25 — mapa completo de Loader3 (30-10-2026)

- **Pedido:** seguir con Loader3, completo si falta algo.
- **Hallazgos:** 674/674 funciones localizadas y con rol; vectores de excepción (toda excepción -> LED directo, sin boot_dispatch); `log`/consola con la misma forma que Loader2; capas BOS/CFG/FAT/TPZL de R13/R15/R16 ahora con dirección fija en el mapa; candidato `LD3:<< KEY E… >>` para E26-R20-KEYTABLE, no explorado.
- **Límite:** INFO 6 (21 páginas) no adquirida; 256 funciones de soporte solo inventariadas.
- **Entregables:** `docs/capture/e26-r25-loader3-completo.md`, `analysis/e26-recovery/r25_loader3_map.py`, `r25-loader3-functions.json`, `r25-boot-sequence.json`, `tests/test_e26_r25_loader3_map.py`.

## E26-R26 — updater\mode (gate verificado) y descarte de la clave PwrIC (30-10-2026)

- **Pedido:** continuar con los 4 pendientes estáticos restantes.
- **Hallazgos:** `boot_dispatch` indexa un valor 0-14 persistido en Backup; `\updater\mode` (dispositivo 2 = nflasha2) es condición necesaria verificada por bytes (su ausencia fuerza modo 3, cadena normal); la cadena `LD3:<<KEY E/L/D>>` es de autenticación de batería, no de arranque — descartada para E26-R20-KEYTABLE.
- **Cierre:** E26-R7-C-UPDATER-MODE CERRADO PARCIAL (mecanismo de lectura resuelto, sin productor pre-Linux); nueva fila E26-R20-KEYTABLE-PWRIC DESCARTADA.
- **Entregables:** `docs/capture/e26-r26-updater-mode-y-clave-pwric.md`, `tests/test_e26_r26_updater_mode.py`.

## E26-R27 — ARM7: ISR NAND y geometría (30-10-2026)

- **Hallazgos:** ISR `0xd24` traduce bits de estado del controlador NAND a códigos propios (0xc/0xd/0x20/0x21/0x23/0x24); `0x1a80-0x1ae4` implementan capacidad y traducción de direcciones con entrelazado multi-plano; las 17 operaciones restantes del despachador comparten la base SRAM `0x3f40` de op 0.
- **Límite:** sin clasificar el comando NAND de cada una de las 17 operaciones.
- **Cierre:** E26-R18-ARM7-RESTO CERRADO PARCIAL.
- **Entregables:** `docs/capture/e26-r27-arm7-isr-geometria.md`, `tests/test_e26_r27_arm7_isr_geometria.py`.

## E26-R28 — búsqueda externa de TPZL (30-10-2026, resultado negativo)

- **Pedido:** continuar con el último de los 4 pendientes estáticos (Prioridad E de R17, no ejecutada).
- **Hallazgos:** sin mención pública de «TPZL» en GitHub ni en la web; Sony-PMCA-RE y fwtool solo cubren el actualizador (FDAT), no el BootROM/Loader2/Loader3.
- **Cierre:** E26-R17-TPZL-1SEG CERRADO con resultado negativo documentado; no hay muestras externas con las que construir la tabla pedida.
- **Entregables:** `docs/capture/e26-r28-tpzl-busqueda-externa.md`.

## E26-R29 — pinout completo de CN4001/CN4906, dos correcciones a R11 (30-10-2026)

- **Pedido:** mapear todos los pines del PDF a su red correspondiente (alcance acordado: CN4001 y CN4906).
- **Hallazgos:** CN4001 es de 19 pines (1=VBUS, no D-; faltaba pin3=D+); CN4906 es de 18 pines, no 32 (los «31/32» eran de otro conector de la misma hoja); CN4906 combina BIONZ+Darwin: pines 11/12/15 unen SWCLK/SWDIO/VIO_FLD con TCK_DWN/TMS_DWN/XDWN_RESET; pin10=RTCK sin red externa.
- **Método nuevo:** `analysis/e26-recovery/r29_pinout_pixel_trace.py` sigue columnas de píxel sobre el render a 600 dpi para resolver cableado que cruza filas (el agrupador por fila existente no lo distingue).
- **Entregables:** `docs/capture/e26-r29-pinout-cn4001-cn4906-completo.md`, `tests/test_e26_r29_pinout_cn4906.py`, correcciones en `analysis/e26-recovery/r11-pinout-reconstruction.py` y `docs/capture/e26-r11-bootrom-uart-physical-access.md`.

## E26-R20-SERIE-PLAN — síntesis del plan de recuperación por serie (31-10-2026, sin evidencia nueva)

- **Pedido:** evaluar si "llevar `CL1000` a 1 y enviar el bloque de arranque por el pin 9" repara la cámara, recombinando R19/R20 sin abrir la carcasa.
- **Hallazgos:** el árbol de decisión de R20 confirma por bytes que `MODEREG` bit 0=1 (`CL1000`/`BOOT_MAIN`, mapeo por inferencia) es necesario pero no demostrado suficiente; el resultado encadena tres datos físicos ya cerrados por separado (`E26-R20-BOOTMAIN-NIVEL`, `E26-R20-GPIO4`, `E26-R20-KEYTABLE`), ninguno medido.
- **Límite:** solo estático; no resuelve ningún dato físico nuevo, solo documenta por qué no son cerrables sin acceso a la cámara.
- **Cierre:** `E26-R20-SERIE-PLAN` permanece ABIERTO (síntesis, sin nueva evidencia); coincide con el criterio de cierre de `E26-FISICO-BOOT`. Segundo commit reescribe el informe con vocabulario neutro de recuperación de hardware (sin cambiar hechos, direcciones ni conclusión).
- **Entregables:** `docs/capture/e26-r20-serie-plan.md`.

## E26-R31 — cierre estático de `MODEREG` bit 0 = `BOOT_MAIN` (31-10-2026)

- **Pedido:** cerrar estáticamente la inferencia de R20 §1.6 (bit 0 = `BOOT_MAIN`/`CL1000`).
- **Hallazgos:** inventario completo de lectores de `MODEREG`: BootROM (bit 0 selector, bit 1 serie), Loader3 `0xc01f4ef8` (solo lo registra en bruto), `mcmn_drv.ko` («MODEREAD»: bit 16 `MSX_INS_HIZ`, 24–27 CD/WP MMC); `vmlinux`/`av-cam`/Loader2 no lo leen (`av-cam` barrido también por `movw/movt`: 0 `movt #0xf291`, control positivo 216 `movt #0x43bd`). Bloque BOOT del IC6000 = `DDRCKSEL`/`BOOT_SERIAL_IN`/`BOOT_MAIN` (A6000 y A6300). `DDRCKSEL` sin consumidor software (y en bit 24 en CXD4132); `MODEREAD_BM1` = bit 1 en CXD4132 → BM0 = bit 0 = `BOOT_MAIN`.
- **Límite:** deductivo; ninguna fuente Sony nombra el bit 0. Polaridad/pull físico siguen en `E26-FISICO-BOOT`.
- **Cierre:** `E26-R19-BOOTMAIN` → CERRADO (R31, estático).
- **Entregables:** `docs/capture/e26-r31-bootmain-bit0-cierre.md`, `tests/test_e26_r31_bootmain_bit0.py`.

## E26-R32 — valor real de `MODEREG` en la cámara (31-10-2026)

- **Pedido:** confirmar con los datos existentes en qué estado está siempre `CL1000`.
- **Hallazgos:** Loader3 (`0xc01f4ef8`, `LD3:read MISCREG`, llamada incondicional en `0xc01f11e4`) escribe TYPEID, `[0xf2912b10]` y `MODEREG` en el backup (IDs `0x3e0003/9/a`, 2 bytes). En los 23 `backup*.bin`: `0x0500` (= `TYPEID_CXD90014`), `0x0010`, **`0x0003`**; la plantilla `0110_backup` trae `0x00ff/0/0`. → bit 0 = 1 y bit 1 = 1 en reposo. Bytes del BootROM: con bit 0 = 1 y clave presente, la ventana serie (`0x876`) sin sincronismo (`0x3001`) salta a `0x1226` (`load_payload` → salto): ese es el arranque normal.
- **Correcciones:** R20 §1.6 y R23 §1 («bit 0 = 0 en uso normal»). `E26-R20-BOOTMAIN-NIVEL` → CERRADO (dato de cámara); `E26-R20-KEYTABLE` → inferencia fuerte «con clave»; `E26-R20-SERIE-PLAN` → CERRADO (el paso «`CL1000` a 1» sobra; la vía serie exige la clave de `nflasha0`).
- **Límite:** el valor lo lee Loader3, no el BootROM; solo 16 bits; polaridad pin↔bit no probada.
- **Entregables:** `docs/capture/e26-r32-moderreg-valor-real.md`, `tests/test_e26_r32_moderreg_backup.py`.

## E26-R33 — veracidad de la clave de `nflasha0` (31-10-2026)

- **Pedido:** examinar si es cierto que la clave de arranque serie está en `nflasha0`.
- **Hallazgos (bytes del BootROM):** `load_header` lee 3 sectores de `0x600` B del bloque 0 a `0xc0000600`; la tabla `0xc0001200` es el tercero → `nflasha0`. `find_key` (`0x39c`) devuelve 0 si **alguna** de las `0x180` palabras ≠ `0xFFFFFFFF` y copia las dos primeras. Sin clave y sin serie: receptor `0x3002` → `0x3001` → `serial_entry` → LED `0x1001`. Formato válido emulado con `0xc52`: palabra 0 = clave, palabra 1 = `~crc32(clave)`.
- **Correcciones:** R32/`E26-R20-KEYTABLE` precisados («sector no borrado», no «clave válida»); R23 §1 con condiciones invertidas; R12 §3 vigente.
- **Límite:** valor y formato reales solo con lectura del bloque 0 (`E26-R33-BLOQUE0`, nuevo).
- **Entregables:** `docs/capture/e26-r33-veracidad-clave-nflasha0.md`, `tests/test_e26_r33_clave_nflasha0.py`.

## E26-R34 — `serial_entry` emulado con todas las combinaciones de banderas (31-10-2026)

- **Pedido:** emular `serial_entry` con todas las combinaciones de banderas (continuación de R33).
- **Hallazgos (bytes + emulación Unicorn, sustitución de llamadas):** `get_flag1()` se lee hasta 3 veces en puntos distintos: 1.ª lectura ==1 salta la recepción entera (va directo a la sección de salto); 2.ª lectura !=0 (cualquier valor) es error `0x1001` directo; tras aceptar un paquete (`rx_packet()==0`), una 3.ª lectura ==0 es también error `0x1001`, no un reintento. Confirmado por bytes: solo dos saltos llegan a la llamada de recepción (`0xfb8`, `0x1032`); ninguno sale del tramo de error ni del de aceptación. `get_flag0()!=0` es error (sentido opuesto al de la misma bandera en `main`, ya documentado en R23, confirmado aquí).
- **Corrección:** R23 §2 tenía un bucle de reintento inexistente y mezclaba dos tramos bajo una sola etiqueta `REGISTRO_MOTIVO`.
- **Límite:** `serial_receiver`/`rx_packet` sigue tratado como caja sustituible (su lógica interna es de R9/R21); no se emuló la forma de onda real.
- **Entregables:** `docs/capture/e26-r34-serial-entry-flags.md`, `analysis/e26-recovery/r33_serial_entry_flags.py`, `tests/test_e26_r34_serial_entry_flags.py`.

## E26-R35 — `serial_receiver` recibe varios paquetes por llamada (31-10-2026)

- **Pedido:** revisar si `rx_packet`/`serial_receiver` (`0x876`) puede recibir varios paquetes en una sola llamada (seguimiento de R34, donde quedó como caja sustituible sin examinar).
- **Hallazgos (desensamblado completo de la función, 279 instrucciones, dos tramos separados por un pool de literales en `0x944–0x99f`):** tras procesar un paquete, `fp==0` (primer paquete) fuerza siempre otra vuelta a `0x89c` (resincronizar), sea el tipo que sea. Solo con `fp==1` y el tipo del paquete actual igual al del primero (`sl`) se sale del bucle; el chequeo final es `[0xc0010004] OR [0xc0010008]` (= `get_flag0()`/`get_flag1()`, mismas variables que lee `serial_entry`, confirmado por ser la única otra copia del literal `0xc0010004` en todo el ROM). Un paquete tipo 0 pone a 1 `[0xc0010004]`; uno tipo `0xFFFF` guarda el destino de salto y pone a 1 `[0xc0010008]`. Confirmado que solo dos saltos (`0xb90`, `0xb96`) llegan al punto de resincronización.
- **Corrección (propia, dentro de esta sesión, no de un informe publicado):** la hipótesis inicial de que el chequeo final exigía específicamente un paquete de salto era incorrecta; es un OR que acepta cualquier paquete tipo 0 o tipo `0xFFFF` visto en la secuencia, no necesariamente el que cierra el bucle.
- **Límite:** `main` llama a la misma función para la «clave» de R32/R33; no se ha trazado si el valor que usa puede venir de varios paquetes encadenados. No se emuló una secuencia real de varios paquetes (solo control de flujo por bytes).
- **Entregables:** `docs/capture/e26-r35-serial-receiver-multi-paquete.md`, `tests/test_e26_r35_serial_receiver_multipaquete.py`.

## Auditoría integral repo/GitHub (31-10-2026)

Local = `origin/main` (`a4c42e69`) al empezar. **CI «Pruebas» en rojo desde el 30-10 (26 ejecuciones):** Pillow ausente en el flujo y R20/R29
leyendo `bootrom.bin` y el manual de servicio (no versionados); arreglado (C9). **Fugas:** número de serie de la cámara en 16 `info*.txt`
redactado (SHA256SUMS recalculados; queda en el historial, R6); la clave `localtest.me.pem` es el certificado público de PMCA; sin tokens.
Volcados nuevos: se versionan JPEG reducidos, montajes y JSON de T042–T044/E25-22/E25-23; RAW, parciales, audio y la corrida previa de T043
quedan ignorados. **Coherencia:** README y CURRENT decían «funcional» tras el bloqueo del 3.25; STATE afirmaba «no se ha flasheado ninguna
cámara»; PENDIENTES tenía filas EFCS con IDs E26–E30 dentro del registro de cambios (renumeradas E25-EFCS…) y E25-19f duplicado; 61 enlaces
rotos corregidos (0 restantes salvo el ejemplo `old.md`). Tablero: planes P1–P24 (antes P1–P21) y recuento de informes de fase E.
README, CURRENT (≤150 líneas, tabla E26) y cabecera de STATE reescritos.

## Mantenimiento posterior a la auditoría (31-10-2026)

- **D13:** registro T054 (E25-22), T055 (E25-23) y T056 (instalación del 3.25, testimonio); informe [E25-23](../docs/capture/e25-23-interrupcion-captura-larga.md) redactado desde la evidencia (5 s OK, 15→20 s, 30 s→`65535` y `shooting` >90 s; causa sin demostrar).
- **C10:** los 15 fallos/errores de `test_s402_static_closure.py` en la suite completa eran una colisión de módulos `fw` en `sys.modules`; los 2 de `test_subsystem_index` venían del informe nuevo sin indexar.
- **C11:** dependencias de CI fijadas en `knowledge/requirements-ci.txt`; `pyelftools` retirado; `F821` corregido; `repo_audit.py` ignora cifras de copias históricas.
- **R3/R6 (historial):** con orden del usuario («hazlas todas»), `git filter-repo` quitó `libmprctrl.so`, el número de serie y el correo personal de los 727 commits; `main` publicado con `--force-with-lease` y árbol idéntico. SHA citados remapeados. Respaldo previo: `~/a6000-respaldo-historial-20261031.git`. Queda R7 (refs de PR y fork ajeno en GitHub).

## E26-R36 — causa del fallo del 3.25 frente al 3.23 (31-10-2026)

- **Pedido:** verificar de inicio a fin, dos veces, por qué falló el 3.25 si el 3.23 (solo Darwin) se instaló bien.
- **Paquetes:** `.dat` instalados descifrados (auditor E25-06) = FDAT plano; frente al 3.21, el 3.23 cambia `darwin_core.bin`/`darwin.sum` y el 3.25 además `dev/nflasha3`/`part_image.sum`. El `nflasha3` del 3.25 instalado = `bb9ce25a…`.
- **Binario (Capstone, releído):** `c01fdd8e` arma la lista de sectores desde `off>>9` y el residuo solo va al aviso y a `trabajo+8`; `c01fccd2` copia 0x18 B; ARM7 `0x1338`/`0x3f4` leen `+0`, `+4`, `+0xc` (16 registros) y `+0x10` (destino), nunca `+8`. `ldec.ko` (Linux) programa el LDEC igual. El residuo no llega al silicio.
- **Datos:** 16 imágenes Sony, 19 489 bloques, 311 824 registros: siempre residuo 0 y 16 × 4096 B (dos parsers coinciden). Cota de Sony `cmpr.c`: 4112 B por registro de 4 KiB. El 3.25: 359 residuos, bloques 0/48/57 = 1 registro de 73 732 B. Montaje (bloque 0) y primera entrada RAMCFG (bloque 240) caen en bloques defectuosos → −302.
- **Arreglo:** `tpzl.py` alinea a 512, recompone con 16 registros almacenados y `rebuild` rechaza particiones con `hardware_violations`; regresión primero (fallaba), 49 pruebas pasan; construcción completa en temporal cumple el formato de Sony con el mismo contenido FAT. La variante «alinear a 512» del README no bastaba.
- **Límite:** sin confirmación física (UART). El Darwin y el BIONZ nuevos del 3.25 nunca se han ejecutado. Entregables: `docs/capture/e26-r36-causa-fallo-325.md`, `analysis/e26-recovery/r36_ldec_records.py`, `r36-ldec-records.json`.

## E26-R37 — cierre estático de la recuperación (31-10-2026)

- **Pedido:** avanzar letra por letra (a→d) hasta cerrar todo lo estático tras R36.
- **(a)** `c01f1de6` trazado: solo `\updater\mode` en `nflasha2` fija el modo 3 (`c01f1e14 cbz` → `movs r0,#3`; R26 lo había leído al revés). El modo 3 carga el actualizador de `nflasha1` (dispositivo 1, intacto: `\boot\{loadaddr.txt,vmlinux.bin,initrd.img}` de 2013), que con solo `mode` entra en MODE_USER y espera firmware por USB (`UdtrMain.sh`, `execute_ufp.sh`). Teclas (`chk ank` → modo 5, ajuste) y Backup llevan a modos que leen `nflasha3`. `c01f51f4` solo envía el modo.
- **(b)** `scripts/e26_recovery/build_326.py`: 3.26 = 3.24 oficial con versión 3.26 (CRC de cabecera, suma y cifrado del primer bloque, DEND). Verificado con el auditor E25-06 (descifrado completo = FDAT) y con `fwtool`; mismos rangos de diferencia que 3.23→3.24.
- **(c)** Loader2 (`c003126c`) y Loader3 (`c01f4edc`) solo encienden la UART si `Backup[0x510015]==1`; 12/12 BK4 = 0. Una UART pasiva no confirma R36; solo el vídeo del LED.
- **(d)** Darwin 3.25: `0x20003716` está en la zona que `__scatterload_zeroinit` (`0x4494`) pone a 0; los vectores 70–73/76 que pisa la cueva son IRQ 54–57/60 y no hay ningún acceso a `NVIC_ISER1`.
- **Entregables:** `docs/capture/e26-r37-cierre-estatico-recuperacion.md`, `tests/test_e26_r37_cierre_estatico.py` (5), `analysis/e26-recovery/manifest-recuperacion-326.json`; pendiente nuevo `E26-FISICO-UPDATERMODE`.

## E26-R38 — guard del actualizador y entrada mínima `\updater\mode` (31-10-2026)

- **Pedido:** «investiga más a fondo» tras R37; se cierra la suposición abierta (comparación de versión) y se baja la escritura física al byte.
- **`sauu` (initrd cramfs de `nflasha1`):** `isVersionOK` (`0xd3d0`) compara con `updater/dat4` (`getVersion` `0xf6e4`, u16 LE); igual solo si falta `comp` (`IsValid` `0xf0b8`) o con `-m`; `-s` acepta todo (constructor `0xd180`).
- **Cuerpo (`libupdaterbody.so` 3.21):** `StartUpdate` borra `comp`; `CompleteUpdate` hace `setVersion(mayor<<8|menor)` (`0x152a8`), borra `mode1…6`, crea `comp` y borra `mode`. `uincomp` solo con `updater_sum` (ausente en los tar 3.2x).
- **Datos:** `nflasha2` del 20-10: `dat4 = 21 03`, `comp` oculto, par LFN+SFN `mode` borrado en las entradas 4–5 de `\updater`. Loader3 (`c01f44c6`/`c01f3f34`) solo compara el nombre corto en el primer clúster y no lee datos.
- **Entregables:** `docs/capture/e26-r38-guard-y-entrada-updater.md`, `scripts/e26_recovery/updater_mode_entry.py` (réplica de Loader3 + parche mínimo; `fsck.vfat -n` limpio), `tests/test_e26_r38_guard_updater.py` (5).
- **Límite:** nada leído de la NAND actual; la persistencia de `MODE` sin LFN es inferencia sobre `vfat`/busybox.

## E26-R39 — investigación estática a fondo (31-10-2026)

- **Pedido:** «hazlas todas, mientras se pueda avanzar en modo estático» (seis líneas tras R38).
- **Emulación:** `analysis/e26-recovery/r39_tpzl_emu.py` ejecuta en Unicorn Loader3 `c01fe4ec`/`c01fdd8e` y ARM7 `0x3f4` (sustituye solo `c020xxxx` ausentes y E/S); LDEC modelado. 3.25: 361/369 fallos (bloque 0 primero, 359 avisos de residuo); Sony y corregida: 0. Residuo en trabajo+8, nunca en registros LDEC.
- **NAND:** particiones = ventanas lineales de `nflasha` (473 MiB lógicos); `nand.ko` = MuMin (LTU/VBM/PBM, bloques malos, ECC/extra) → sector 132 no traducible; `0xE5→0x4D` necesita 0→1.
- **Actualizador:** `/sbin/init` + `insmod.sh` solo montan `nflasha2`; Darwin 3.25 = Sony + 22 B. Kernel `3.0.27_nl-rt106` = árbol GPL: búsqueda `nls_strnicmp`, `shortname=mixed` lista `MODE`. Guard: modelo/región/versión, sin batería.
- **Clave:** sin paquetes con loader; ningún cargador toca `0xc0001200`; el actualizador ya lee SRAM de arranque → `E26-R39-CLAVE-SRAM`.
- **Entregables:** `docs/capture/e26-r39-estatico-profundo.md`, `tests/test_e26_r39_estatico_profundo.py` (9), `r39-tpzl-emu.json`.

## E26-R40 — JTAG/SWD del BIONZ (31-10-2026)

- **Pedido:** analizar JTAG/SWD como alternativa a lo físico tras R39 (escribir `nflasha2` sin lector externo).
- **DAP CoreSight** (FUENTE, GPL de Sony): `0xf2710000`, 4 CTI, `dap.c` solo lo usa para una IRQ de la PMU; literal de desbloqueo `0xC5ACCE55` único en el kernel.
- **Sin bloqueo de software** (BINARIO): barrido de literales en BootROM/Loader2/Loader3/ARM7 sobre `0xf2710000`–`0xf271ffff`: 0 en los cuatro.
- **Silicio pensado para ICE:** `defconfig` `cxd90014_ice_initrd`/`ice_nfs` arrancan con `initrd`/cmdline fijos, sin `nflasha1`.
- **Ventana sin apagado:** `c01f3bf6: b #0xc01f3bc8` (bytes `e7e7`), bucle de LED tras −302 sin `wfi` ni apagado.
- **Límite real:** población de R4911/R4912 y eFuse de seguridad (junto al bloque JTAG en el manual) no están en ningún binario accesible; mismo límite que la clave de `nflasha0` (R33).
- **Entregables:** `docs/capture/e26-r40-jtag-swd-bionz.md`, `tests/test_e26_r40_jtag_swd.py` (8). Anota R5-SIDEA/R5-BIONZ; no los cierra (siguen físicos).

## E26-R41 — caminos estáticos restantes (31-10-2026)

- **Pedido:** «verifica los caminos estáticos faltantes por descubrir».
- **Consola de Loader3** (BINARIO): `c01f379a` lee la UART, con `\r` compara `beast`/`ldump`; `ldump` (`c01f3708`) solo hace `ldrb/ldrh/ldr`; `beast` (`c01f376e`) sale si `[0xc0060014]=0`. El bucle de LED llama a `c01f5008` (PL011: `IBRD 0x1a`, `FBRD 3`, `LCRH 0x70`, `CR 0x701`). Loader2 trae la misma consola.
- **Muda** (DATOS): `0x510015=0` → nivel UART 0 y `beast` desactivado en los 12 BK4.
- **Wait ICE:** `c01f0cc2: bl c01f48cc`, antes de `c01f0cca`; GPIO de Backup `0xf90449/0xf9044a` = 14/17; espera `[0xc0045804]≠0`.
- **Entregables:** `docs/capture/e26-r41-caminos-estaticos-restantes.md`, `tests/test_e26_r41_consola_loader3.py` (4); pendiente nuevo `E26-R41-ICE-GPIO`. Corrige R13, R37 §4 y R40 §6.
- **§7 (límites completados, «completa esos»):** Loader2 `c0030014: blx c003110c(0)` y `c0030020: blx c00308b8(0,7)` → `[0xc006000c]=0` (UART0); GPL `regs-clk.h`/`uart.S`/`clock.c`: 48 MHz, `IBRD 0x1a`/`FBRD 3` = 115 200; ningún cargador activa `OCTRL(2)+IEN` (sí `uart_init` con `UART_IO_INIT`, solo en `ice_initrd`). GPIO: `gpiopin_to_irq` puerto 0 = `GPIO_S` → bolas `GPIO_n` = puerto 0; el 14.17 no se puede determinar (falta la tabla de pines) → `E26-R41-ICE-GPIO` cerrado con límite. Pruebas: 6.

## E26-R42 — búsqueda externa en GitHub y esquema JTAG/eFuse (31-10-2026)

- **Pedido:** buscar en GitHub información nueva sobre ingeniería inversa/decompilación de la A6000 y verificar qué más da el código fuente (GPL) y el pinout en PDF.
- **Repos externos** (clonados en lectura fuera del repo): tres cubren la A6000 directamente (RafalB82, CliffVale, dhihacker) sin nada nuevo sobre arranque/recuperación; `cokeenet/zve10-qemu` (ZV-E10, CXD90045) y `Erlla/sony-a7m4-custom-firmware` (A7 IV) tienen vías de recuperación probadas en hardware real, pero no transferibles (SoC y arquitectura de arranque distintos: `fastboot`/eMMC vs NAND+Loader2/Loader3 del CXD90014).
- **Esquema (DATOS):** `pdftotext -layout` (el `.txt` versionado) pierde por completo la hoja JTAG/eFuse (pág. 26) y el neto `XRESET_CR` (pág. 24); `pdftotext` sin `-layout` + render de página (`pdftoppm`) sí los recupera. Bolas: TDI=G25/TCK=H25/TMS=F26 (atadas a VDD1), TDO=F25/RTCK=G26, NTRST=H26 (neto `XRESET_CR`); `FUSE_EN`=T12 atado a VDD2, `FUSE_CLK`=R12 sin red; SWCLK=W25/SWDIO=W26 sin atar. `XRESET_CR` = también la entrada `XRESET` del propio IC6000 (bola K6, hoja 1/7, vía `R6000` XX).
- **GPIO:** cobertura exhaustiva (54 páginas): solo existen `GPIO_0..16`/`GPIO_S_0..16` (puerto 0) y `GPIO_SB_0..6` (puerto 1); ningún nombre para el puerto 14. Confirma el límite de `E26-R41-ICE-GPIO`.
- **Entregables:** `docs/capture/e26-r42-busqueda-externa-y-esquema-jtag.md`, `tests/test_e26_r42_esquema_jtag_efuse.py` (3); pendiente nuevo `E26-R42-EXTERNO` (cerrado). No cambia ninguna vía de recuperación.

## E26-R43 — cierre estático de CL1000/BOOT_MAIN (bit0): sin acceso externo (31-10-2026)

Petición del usuario: verificar si la clave de `nflasha0` es realmente imprescindible o hay alternativa, y cerrar de
forma estática si forzar `CL1000` a masa es viable, revisando también el código GPL de Sony.

- **GPL (FUENTE SONY):** `regs-misc.h` de `mach-cxd90014` y `mach-cxd4132` solo nombra el bit 1 (`BOOT_SERIAL_IN`/`BM1`);
  el bit 0 (`BOOT_MAIN`) no tiene definición ni polaridad en ningún archivo del árbol GPL. No hay alternativa en
  software: sigue siendo un strap de hardware puro.
- **Esquema (ESQUEMA, vectorial — `pdftotext -bbox` + `pdftocairo -svg`, sin rasterizar ni OCR):** trazado exhaustivo de
  la hoja CLK BOOT (página 24): `CL1000`/`BOOT_MAIN` (P7) termina en el punto de prueba sin ningún salto hacia la
  columna de exportación global — **no hay atajo por el conector Multi externo (CN4001)**. Sigue siendo intervención
  física interna; polaridad no determinable sin hardware (igual que R31 §3/R32 §5, sin cambios).
- **Efecto lateral (corrección):** al trazar la misma hoja se confirmó que `BOOT_SERIAL_IN` (H21, bit1) sí exporta, y
  llega al **pin 10** de CN4001 (etiqueta de conector `AD_JACK_IN`), no al pin 9 como daban por hecho R11/R19/R20/R29
  (agrupaban por fila de texto, que en esta hoja no coincide en altura con el trazo real — mismo problema que motivó
  el pixel-trace propio de R29 para CN4906, nunca aplicado a CN4001 hasta ahora). El pin 9 solo lleva
  `DEBUG_UART0_RXD`, señal de consola independiente.
- **Entregables:** `docs/capture/e26-r43-cl1000-sin-acceso-externo.md`, `analysis/e26-recovery/r43_cl1000_cn4001_trace.py`,
  `tests/test_e26_r43_cl1000_cn4001.py` (3, en verde). Pendientes: `E26-R43-CL1000-ACCESO` (cerrado), nuevo
  `E26-R43-PIN10-CONTINUIDAD` (físico). No cambia el objetivo de recuperación ni abre vía nueva: confirma que lo que
  falta sigue siendo físico.

## E26-R44 — ¿otra forma de obtener la clave de nflasha0, o forzarla? (31-10-2026)

Petición del usuario, continuando R43: ¿hay alternativa a la clave, o se puede forzar?

- **Desensamblado directo** (Capstone, no pseudocódigo) de la comprobación de clave en `main`: una sola palabra de 32
  bits (la segunda palabra guardada es solo `~crc32`, sin secreto adicional), comparada en una única instrucción
  (`ldrd`+`cmp`) — sin bucle byte a byte, sin canal lateral de tiempos explotable. `error_blink` (`0xffff0d62`) es un
  **bucle infinito que nunca retorna**: cada intento fallido exige apagar y encender la cámara. **Fuerza bruta
  descartada**: 2³² intentos por este interfaz, inviable incluso automatizada (años, no horas).
- **Ninguna alternativa software** para leer/derivar la clave: Loader2 (247/247) y Loader3 (674/674), ya mapeados al
  100 %, no tocan `nflasha0`.
- **Mejor vía que la clave, ya documentada pero no resaltada así antes** (R20/R23, `E26-R20-GPIO4`): si `GPIO4.22`
  lee `!=0` al arrancar, `main` salta a `serial_entry()` sin pasar nunca por la comprobación — no exige conocer ningún
  secreto. El usuario pidió reabrir la búsqueda del pin físico con el método vectorial de R43: único bloque "GPIO SYS"
  en las 54 páginas del esquema, sin dato que confirme que sea el canal 4 del mapa de registros (el GPL de Sony da el
  cálculo de dirección pero no el mapeo canal→bola). Candidato débil por descarte: `GPIO_SB_5` (bola N8) es la única
  del grupo sin red de cámara nombrada. **No cierra.**
- **Entregables:** `docs/capture/e26-r44-gpio4-bit22-busqueda-pin.md`, `tests/test_e26_r44_gpio4_clave.py` (4, verde).
  PENDIENTES: cierra `E26-R44-CLAVE-FUERZA-BRUTA` y `E26-R44-GPIO4-BIT22-BYPASS` (bypass ya conocido, impacto
  precisado); abre `E26-R44-GPIO4-PIN` (sin cierre) y `E26-R44-AVCAM-GPIO4` (binario, rastrear llamadores con banco 4
  de la lectura genérica de GPIO en `av-cam.bin`, no iniciado — requiere sesión REA ~8 min).

## E26-R44 §6 — sesión REA de av-cam.bin: pin de GPIO4.22, bloqueado por el límite de E1 (01-11-2026)

Petición del usuario: iniciar la sesión REA de `av-cam.bin` para `E26-R44-AVCAM-GPIO4`.

- Primitiva de lectura de GPIO por banco (`FUN_4398f990`, `base=0xf2910010+banco*0x100`): **un solo llamador** en todo
  el binario, `FUN_43b5e2bc`, que acota el banco a 0–17 (banco 4 permitido, da exactamente `0xf2910410`) y tiene
  **26 llamadores**. Ninguno pasa banco/bit como constante: todos resuelven contra la base de datos de propiedades de
  Sony mediante IDs opacos (`0x00f902a9`, fuera del rango de direcciones del binario) — **el mismo mecanismo sin
  resolver de `E1`/`ModelScalarPb`**.
- 3/26 llamadores identificados por nombre vía tabla de registro de propiedades (`eosw_port`/`[EO_SW]`,
  `rvport`/`[PanelReverse]`, `esport`/`[EyeSens]`): los tres son funciones normales de cámara, ninguno de arranque.
- **No se identificó el pin de `GPIO4.22`.** Bloqueado por el mismo límite que `E1`: los valores reales de banco/bit
  no están en `av-cam.bin` como datos estáticos — dependen de una base de datos de propiedades no localizada.
- Sesión REA cerrada limpiamente; `exp2-session-log.jsonl` restaurado con `git checkout`.
- **Entregables:** `docs/capture/e26-r44-gpio4-bit22-busqueda-pin.md` §6. PENDIENTES: `E26-R44-AVCAM-GPIO4` pasa de
  ABIERTO a **BLOQUEADO** (mismo origen que `E1`); cruzado en la fila de `E1`.

## R8 — publicación de los binarios 3.23/3.24 como GitHub Release (01-11-2026)

Petición expresa del usuario: subir los dos firmware custom ya construidos en E25-05 (el que apaga las bobinas y el
obturador mecánico completo, y el de recuperación) como release de GitHub, con sección de copyright en el README.

- Verificado que `analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (`4c21353d…`) es exactamente el
  hash comprobado antes de flashear en T040, y que `recuperacion-324/firmware_packed.dat` (`e1345aff…`) es su
  recuperación verificada offline (E25-05, 69/69 checks) nunca instalada en cámara real.
- Publicados en el [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
  (no en el árbol de git, que sigue sin firmware de Sony) con `SHA256SUMS.txt` y notas: estado real de cada paquete,
  pasos de instalación/verificación y aviso de copyright (investigación/interoperabilidad, sin redistribuir fuente
  de Sony, retirada a petición del titular).
- README: enlace al release en «Instalación del 3.23», nueva sección «Recrear lo mostrado en el hilo de r/a6000»
  (pasos para reproducir la publicación de Reddit: 3.23 + `camera_silent.py`) y «Copyright de los binarios
  publicados».
- **Entregables:** release de GitHub, README actualizado, [R8 en PENDIENTES](../docs/PENDIENTES.md) CERRADO.

## Wiki de réplica, LICENSE y README reducido (01-11-2026)

- Petición del usuario: quitar el copyright del release (queda solo en el README), reducir el README y crear una wiki para replicar todo de principio a fin.
- `wiki/` (11 páginas) y `scripts/replicar/generar_nucleos.py`: reconstruir 3.23/3.24 desde el firmware oficial reproduce exactamente los SHA-256 del release (`4c21353d…`, `e1345aff…`; 69/69 comprobaciones).
- `LICENSE` MIT solo para código y documentación propios.
- Publicada en la wiki de GitHub («Wiki CFW Sony a6000»); auditoría sin incoherencias.

## E26-R45 — firmware 3.25c experimental (01-11-2026)

- Petición del usuario: construir el 3.25 corregido, corregir todo lo que bloqueó la cámara y publicarlo como experimental y teórico con pruebas.
- Corregido además un riesgo que el constructor de R36 introducía: bloques recompuestos de 129 sectores (Sony ≤ 126 en `nflasha3`). `tpzl._splice` conserva los registros de Sony de las páginas no tocadas (regresión primero).
- `scripts/e25_27/verify_325c.py` → `analysis/e25-27/verify-325c.json`: 30/30 sobre el `.dat` final con controles (Sony 3.21 y el 3.25 que bloqueó); emulación Loader3+ARM7: 0/369 fallos frente a 361.
- Release `fw-3.25c-experimental` (*pre-release*): 3.25c, 3.26 de vuelta atrás, SHA256SUMS y la evidencia. Informe [R45](../docs/capture/e26-r45-firmware-325c-experimental.md).
- 01-11-2026 (seguimiento, petición del usuario): README, wiki, tablero y portada actualizados para presentar el 3.25c como alternativa experimental al 3.25 original (que sigue sin publicarse).
- 01-11-2026: `README.en.md` (versión en inglés) enlazado con un botón al inicio del README; copyright cubre también el release 3.25c.
- 01-11-2026: wiki, CONTRIBUTING y notas de releases en inglés; wiki española sincronizada con los mismos datos. Los informes siguen en español.
- 03-11-2026: **CAM-01 cerrado con límite** — familia CAMERA con 0 menciones abiertas por medidas (`analysis/camera_closure/`, `tests/test_camera_closure.py`): callbacks `0x437b8774`/`0x437b7778`/`0x436ea2d0`/`0x43705d64` sí registrados por puntero PC-relativo; seis funciones sin referencia estática; ficheros fuente casi nunca citados. Avance real 24,50 %.
- 03-11-2026: **CAM-02 cerrado con límite** — familia CAM (7 etiquetas) con 0 menciones abiertas por medidas; corrige S600/S601 (sí citan ficheros fuente). `analysis/camera_closure/` ampliado.
- 03-11-2026: `[CAMCORE]` (S107) cerrada por medidas, como CAM-02.
- 03-11-2026: familia IMAGING (S611, S631) cerrada por medidas; el barrido bl de camera_closure pasa a patrón de halfwords (el lineal daba 0 llamadores); corrige S122 (0x438792dc sí tiene bl).
- 03-11-2026: S632 documenta y cierra la familia MODE (`[MODE_SNR_BUS_THROUGH]` hito; `[MODE_CAP*]`, `[MODEFLG]` en el mismo informe). Cobertura 208/372.
- 03-11-2026: familia MODE 6/6 (los cinco [MODE_CAP*] pasan de no-modulo a sub-etiqueta de [IMAGING_CAP]); cobertura 213/372.
- 03-11-2026: S633 cierra la familia STK 6/6 (cinco [STK_*] a sub-etiqueta de [STK]; S501 sin NO VERIFICADO). Cobertura 218/372.
- 03-11-2026: familia MOUNT (S133, S608, S613) sin menciones abiertas, por medidas.
- 03-11-2026: familia OTROS cerrada (S634 + cierres de 49 informes); censo 364/372, 0 pendientes.
- 03-11-2026: S635 documenta [OSD] (última etiqueta cubierta sin informe propio).
- 03-11-2026: S636 documenta [D0]-[D7] como sub-etiquetas de [CAM_UTIL_ADJ]; censo 372/372.
- 03-11-2026: auditoría de pendientes tras S636: review_reports regenerado (762 informes; 1800 abiertas / 2737 verificadas), sin rutas nuevas; ver PENDIENTES. Sesión previa cortada por un `grep -rn` recursivo sobre `analysis/` (sin resultado registrado).
- 03-11-2026: revisión de las 154 líneas sin marca: 23 marcadas NO_VERIFICADO (REV-01), 131 apartadas; añadibles 0.
- 03-11-2026: REV-01 parcial: 12/23 cerradas con medidas (analysis/rev01/); 11 pendientes de sesión REA.
- 03-11-2026: REV-01 14/23 (sesión REA: adjust_cmd_recon 85, clk_ctrl 374); quedan 9.
- 03-11-2026: REV-01 cerrado con límite (23/23); corrige apl (A7S no idéntico) y label_map (solo IDT_OPD renombrado). analysis/rev01/.
- 03-11-2026: R46 — procedimiento físico planeado para SWD al BIONZ sin osciloscopio (fases F1–F9); R4911/R4912/CN4906 confirmados sin montar por el usuario.
- 03-11-2026: R47 — primer contacto SWD real (RP2040 Zero + debugprobe-zero): DPIDR/APs leídos, RAM volcada (hashes fuera del repo), Loader3 en RAM idéntico a Sony; `halt`+registros mide el −302 en LDR2/LNG/SHT; cadena de puntos de parada sobre el arranque real confirma que P2 (`CFG_E:Load file`) falla al cargar `\sabin\idt_cam.bin` de `nflasha3` (§15), confirmando R36 en la cámara.
- 03-11-2026: R48 — plan de entrada al actualizador por SWD sin escribir NAND (forzar `r0=0` en `chk updater`, c01f15c0); Loader3 no puede escribir bloques (`muminblk_request` ignora las escrituras). P0 preparado (pmca, paquete 3.26 verificado). Primer intento de P1 no vio el patrón de doble arranque esperado y se detuvo solo; muestreo posterior corrige la lectura: el doble arranque es meter-batería-luego-interruptor, no cada encendido. El usuario entró al actualizador por su cuenta; primera instalación del 3.26 cortada al 45 % (`0x1063`, NG de Darwin).
- 03-11-2026: R49 — cierre: `r48_updater_swd.cfg` corregido para el arranque único real; P1 ejecutado con éxito (BootMode 3 elegido, entrada al actualizador en 696 ms); diagnóstico por SWD tras el fallo (registros banked `sp_svc`/`lr_svc`, no los alias genéricos) confirma que el kernel seguía sano y nada se había confirmado (versión seguía en 3.25); reintento de instalación completo (`CMD_COMPLETE`). **Cámara recuperada: arranca normal, firmware 3.26 confirmado.**
- 07-11-2026: R65 — rama EFCS de Darwin: `t`=0 en BSS (E26-R64-CORTINA cerrado), µs, `S+0x48 = T − u16[G+0x42]` con EFCS activado (E26-R62-DARWIN-IP cerrado con límite); origen de G no localizado (E26-R65-G42); prueba `0x30102+0x8a` propuesta (E26-R65-8A). Test `tests/test_e26_r65_darwin_efcs_tiempo.py`.
- 07-11-2026: R66 — B/G de Darwin son las propiedades NVRAM `0x1850001`/`0x1850000` (tabla BIONZ `0x43fe8c38`); corrige la asignación a BK4 `0x30102` (R58 §13, R61–R65); `G+0x42 = 3407` µs sin cambios desde el 20-10; la pérdida EFCS no viene de Darwin; propuesta `0x1850001+0x86` (E26-R66-B86). Test `tests/test_e26_r66_bloques_darwin_nvram.py`.
- 07-11-2026: R67 — eventos A/B de Darwin con EFCS = P4C ← 0 (`CA_1ST_CURTAIN_START`) y P4E ← 1 (`2ND_CURTAIN_MG`); la pérdida queda en el retardo flanco→reinicio del BIONZ/sensor o en la cortina; propuesta de lectura pasiva E26-R67-GPIO9; E24-05e parcial. Test `tests/test_e26_r67_eventos_darwin.py`.
- 07-11-2026: triaje de PENDIENTES — 67 filas cerradas (superadas por R49 o por R54–R56, históricas o sin fuente; E11 con la premisa corregida por R67); E25-07 cerrado con procedimiento `sha256sum -c` y `recuperacion-323` obsoleto; quedan 15 abiertas (físicas, autorización, repositorio o carril GUI).
- 07-11-2026: R68 — auditoría de R65–R67: corregidos R65 §3 (la rama `< −150` no explica el negro), R65 §1–2 (`0x30102`), la saturación de E26-R66-B86 (solo T < 3407 − B86) y la tabla global de CURRENT (3.37 oficial, hito 3.30); cuatro afirmaciones pasan a INFERENCIA. Test de saturación en `tests/test_e26_r67_eventos_darwin.py`.
- 07-11-2026: R69 — revisión de R56–R64 con notas de corrección (R58 §3/§13, R61, R62 §3–4, R63 §6, R64); inferencias de R65–R68 cerradas (P4E ← 1 suelta la trasera; A–B independiente de `ip`; `t` = 0 y flujo backup como INFERENCIA fuerte); E26-R66-B86 descartado, E26-R67-GPIO9 fusionado en E26-R66-RESET (procedimiento listo).
- 07-11-2026: R70 — máquinas de secuencias de Darwin; P4C ← 1 en la preparación y en el rearme (A siempre produce flanco); `ip` escribe P4A/P42/P05/P35/P56; lectores de `G+0x42` vía `0x182d8` son plazos de decenas de ms; test `test_e26_r70_secuencias_darwin.py`.
- 07-11-2026: R71 — medida en cámara (solo lectura) de los GPIO del BIONZ; E26-R66-RESET pasa a PARCIAL.
- 07-11-2026: R72 — `0x30087` → `record+0x156` en el planificador EFCS; config. de mecanismo de Darwin fuera de `darwin_core`.
- 07-11-2026: R73 — REA con límite de 1 h: destino de `0x30087` (StillInfo) y ganchos de depuración; E26-R72-30087 cerrado.
- 07-11-2026: R80 — auditoría del parche R76: scripts reparados, cave con límites y validación, gradiente no corregible desde Darwin.
- 07-11-2026: R74 — conclusión final del negro con EFCS: causa física; test `test_e26_r74_efcs_bionz.py`.
- 07-11-2026: R75 — verificación de R74 y de la secuencia A/B de Darwin; la pérdida sigue a `B − t0`, no al flanco A; test `test_e26_r75_verificacion_r74_darwin.py`.
- 07-11-2026: R77 — preparación, P4D y orden temporal (estático): P4D ← 1 solo tras el armado con EFCS, retardos fijos sin T; test `test_e26_r77_preparacion.py`.
- 07-11-2026: R78 — límites de R77 cerrados (semántica del intérprete, acciones 09/0a/13/14 sobre la máquina S, alcance de `0x1fee2`); test `test_e26_r78_limites_r77.py`.
- 07-11-2026: R79 — restos de R78 cerrados (handlers de tabla `0x295c4`/`0x25b70`, acciones 04–06/`0x2f` de S, reejecución de S); test `test_e26_r79_restos_r78.py`.
- 07-11-2026: R81 — auditoría del parche EFCS: el cave `0x13d5a` está en la función viva `0x13d58`; parche bloqueado; test `test_e26_r81_parche_efcs.py`.
- 07-11-2026: R82 — parche EFCS v3: reescritura en sitio de `0x18d6e..0x18e0f` con la tabla integrada (vía A, verificada con 3 métodos), volcados NVRAM listos (D), evidencia de tamaño del core (C), sin hueco ≥ 40 B (B); test `test_e26_r82_parche_efcs_v3.py`.
- 07-11-2026: R83 — informe final de la investigación EFCS (R65–R82).
- 07-11-2026: G2/G4 parcial — formato `string_*.uxc` verificado + editor de ida y vuelta (`scripts/gui/uxc_strings.py`, `test_gui_uxc_strings.py`); ítem de menú `CmnViewMenuItemStruct` verificado con la tabla Creative Style de `viewUnified2.so` (REA); colores `color_cmn` como RGBA de 8 B. Informe: `docs/gui/g04-menus-y-recursos.md`.
- 07-11-2026: G8/G2/G4 (offline) — veredicto de integridad de `/usr` (solo CRC-32, FDAT sin firma), cambio de texto en copia ext2 verificado con debugfs+e2fsck, `scripts/gui/menu_tables.py` (93 carreras de tablas). Propuesta: prueba B (bind-mount reversible) con autorización. `docs/gui/g04-menus-y-recursos.md` §6–9.
- 07-11-2026: G9 — ajuste Silent Shooting/Shutter Type del A6300: 4 capas (CautionConfig nodos, viewUnified elementos, libObj camera-user, av-cam), `scripts/gui/setting_nodes.py`; corrige E007 (nodo SilentShutter de la A6000 = SteadyShot). `docs/gui/g09-silent-a6300-menu.md`.
- 07-11-2026: G9 ampliado — capa de mensajes PARAMID_* (A6000 ya tiene Silent y FrontEShutter; A6300 añade SHUTTER_TYPE), builds no intercambiables (wrappers fundidos en A6300), barrido de ProcessId descartado por ruido.
- 07-11-2026: G9 — las páginas de menú son arrays de punteros a nodos raíz (relocaciones ABS32 en viewUnified2); A6300 inserta SilentShutter antes de EFCS en las mismas 5 páginas que la A6000 usa para EFCS. Plan: sustituir/alargar entradas + reutilizar el nodo stub.
- 07-11-2026: G9 §5c — consumidor de las páginas de menú: _INIT_70 de viewUnified2 (A6000) construye 5 páginas con EFCS (array de hijos + cuenta constante); ruta de menor coste = sustituir símbolo de relocación; insertar exige relocación nueva + cuenta.
- 07-11-2026: G9 §5d — decisión de insertar (no sustituir); viabilidad: sin hueco en .rel.dyn, sin GNU_RELRO, sin cuevas de código; mecanismo = PT_LOAD añadido + copia de .rel.dyn + literal/cuenta por página en _INIT_70 (páginas 1–3 localizadas).
- 07-11-2026: G9 §5e — prototipo add_menu_entry.py (segmento PT_LOAD + relocaciones + literal/cuenta) verificado con qemu-user+gdb: 5 páginas con cuenta+1 y la entrada nueva antes del EFCS; corrige array de la página 3. Herramientas: add_menu_entry.py, qemu_sysroot.py.
- 07-11-2026: G9 §7 — paquete de prueba Silent Shooting (A6300) que reutiliza el ajuste EFCS 0x46 (semántica del CFW): build_silent_menu_test.py, camera_ui_test.py (probe/deploy/revert, dry-run por defecto); carga verificada con qemu-user. Sin cámara.
- 07-11-2026: G9 §7b — prueba en cámara: probe OK (md5 3.21 coinciden), bind OK, pero im.elf ignora SIGTERM, sin supervisor; kill -9 + relanzado manual => la cámara se reinicia sola y se pierden los montajes. Vía temporal descartada; queda flasheo de nflasha15.
- 07-11-2026: G9 §8 — reconstrucción de nflasha15 (TPZL de ext2): build_nflasha15.py + build_package_nflasha15.py; 135/2373 bloques recompuestos, fsck limpio, decodificador independiente coincide; paquetes 3.39 (menú) y 3.40 (vuelta atrás) construidos offline.
- 07-11-2026: G9 §8b — paquete 3.39 rehecho con bloque TPZL 0 = Sony (solo contadores ext2) y Darwin v3 (R82); auditoría independiente 23/23 OK; vuelta atrás 3.40 = 3.38 con /usr de Sony.
- 08-11-2026: G9 §8c — fallo del 3.39 diagnosticado por SWD (assert de ResourceManager por ids de texto sin ranura en el índice del A6000); 3.40 corregido y auditado 22/22; vuelta atrás 3.41.
- 08-11-2026: G9 §8d — 3.40 (menú corregido) deja la cámara en error LED −307 de Loader3; recuperada con 3.41 (paquete base + /usr Sony). Causa sin determinar; la UI sigue sin probarse.
- 08-11-2026: R82 en cámara — 3.43 con Darwin v3 arranca; tabla NVRAM de prueba (c=2000 µs) elimina el negro con EFCS: la NVRAM llega a Darwin. 3.42 (menú sin Darwin) no arranca → culpable `nflasha15`. Nuevo `scripts/senser_efcs_table_write.py`.
- 08-11-2026: cierre de sesión — informes G10 (menú Silent) y R84 (Darwin v3 en cámara); cámara en 3.43 con tabla NVRAM de prueba.
- 08-11-2026: G11 — auditoría del −307 (Loader3 no lee datos de `nflasha15`; −307 = init UDIF/MuMin), paquetes 3.39–3.42 verificados; corregido el modo de los ficheros en `build_nflasha15.py`.
- 08-11-2026: G11 §6 — verificación estática de `viewUnified2.so`/`CautionConfig.so`/`.uxc`; sin defecto estructural; riesgos R1 (nodo `0x26` reutilizado) y R3 (páginas de 7).
- 08-11-2026: G11 §7 — paquete 3.44a (variante a: sin `viewUnified2.so`) construido y auditado 23/23; auditor con comprobación de modo/uid/gid.
- 08-11-2026: G11 §8 — 3.44a no arranca (Loader2 −201; log en la eSRAM: se queda en `Load LDR3`); recuperada con R48 + 3.45; la cámara queda en 3.45 (= 3.43).
- 08-11-2026: G11 §9 — paquetes de aislamiento 3.46 (solo `.uxc`), 3.47 (solo `CautionConfig.so`) y 3.48 (control con contenido de Sony) construidos y auditados 23/23; sin instalar.
- 08-11-2026: G11 §10 — 3.48 (control) y 3.47 (solo `CautionConfig.so`) instalados: ambos fallan; la causa probable es escribir un `nflasha15` recompuesto. Cámara pendiente de recuperar con el 3.49.
- 08-11-2026: G11 §11 — recuperada con 3.51. Causa común: el arranque normal (BootMode 11) reanuda el WBI de Sony (`nflasha5`), que contiene el TOC y la caché del `/usr` de Sony; el actualizador lo reescribe tras `ud_wbi_drop`. Paquete 3.52 (control sin `nflasha5`) construido, 25/25.
- 08-11-2026: G11 §12 — 3.52 arranca en frío (`BootMode: 1`): causa confirmada. 3.53 (menú completo sin `nflasha5`) construido, 25/25.
- 08-11-2026: G11 §13 — 3.53 en cámara: arranca y aparece «Silent Shooting», sin selector. 3.54: listas del nodo con `0xb`/`0xc` del EFCS en segmento nuevo (qemu OK), 25/25.
- 09-11-2026: G22-B — auditoría del arnés de la UI: `setup.sh` reproducible, `im.sh`+`SHIMENV`, shim corregido (buzones con *timeout*, colas dinámicas, señal segura), `tests/test_gui_harness.py`, informe [G22](../docs/gui/g22-arnes-ui-qemu.md) con el plan F1–F5; verificado en QEMU el mismo punto que el avance 17.
- 09-11-2026: G22-B avance 18 — callbacks de cola de `libosal_uipc` (idx 3/8/9/13) modelados; `FULLLOG`/`ACKQ`; bloqueo ahora en el protocolo de pines (`DataflowInfraPin`, tras acusar `0x61003c`). Ver [G22 §5.1](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 19 — emuladas `InternalCmd` alloc (`0x61003c`), backup `nread` (op 30), espera de GPU `dmpgles2` y dmm 1/9; `hal_create` pasa; siguiente: formato real de dmm (MemorySpace) y SIGSEGV no determinista. [G22 §5.2](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 20 — `grm_ma.ko` identificado como el servicio 0x14c0424 y emulado; GPU (registros + IRQ); el arnés arranca estable hasta el Window System (640×480). Siguiente: pantalla (F3) y entrada (F4). [G22 §5.3](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 21 — cargador completo (66 etapas) y reposo; MEMSCAN: sin píxeles (render por GPU DMP); plan F3 revisado. [G22 §5.4](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 22 — `bootin.elf` lanza 8 procesos `im.elf` (letras → fases del IMDB); `appFw.so` (hilo de la UI) nunca se ejecuta, ni con `bootall`; nuevos `INJECT`, `IMSPLIT`, `IMARGS`. F3–F5 no realizadas. [G22 §5.5](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 23 — la UI arranca (`appFw.so`+`viewUnified2.so`): faltaba señalar el semáforo `0x83037a` (`SEMSIG`). Bitmap de pantalla a cero → F3 depende de la GPU de DMP. [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 23b — SEMSIG×4, la UI carga recursos y abre /dev/ldec; pantalla aún a cero (GPU). [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 23c — AREADUMP/DUMPTHR; lista de comandos de la GPU solo con sincronización; Appframework bloqueado en mutex GL. [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 24 — GPU mínima (GPUEMU) y protocolo vdf; la UI no se bloquea; pantalla aún a cero (falta renderizar listas DMP). [G22 §5.7](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 24b — KEYQ/INJECT por buzón para teclas; w0=2 aceptado, sin vista. [G22 §5.7](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 25 — bucle de `Appframework`, ruta `openView` → evento `0x11012001`, tabla de vistas vacía, `InputService::activate` desde las vistas; `OPENVIEW`/`HILO`/`DUMPTHR` lista. Sin vista ni píxeles. [G22 §5.8](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 26 — la UI abre ViewScalarboot; GRM 2D sin uso; F3 sigue bloqueada por la GPU de DMP. [G22 §5.9](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 27 — ViewRoot abierta con OPENVIEW=view/ROOT; teclas llegan a InputService; bitmap a cero. [G22 §5.10](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 28 — corrección: la UI no envía dibujo a la GPU (4 trabajos); ViewRootPowerSw Non-Display por la fecha de model/ROOT. [G22 §5.11](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 29 — servicio de fecha modelado sin efecto; ViewRootPowerSw sigue Non-Display. [G22 §5.12](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 30 — PATCHFN; Non-Display no es error; falta evento de tecla de encendido. [G22 §5.13](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 31 — w1 de INJECT = status del interruptor de encendido; ViewRootPowerSw llega a isBootEECapNone. [G22 §5.14](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 32 — status del encendido = w2; BOOTINFO; sin avance en dibujo. [G22 §5.15](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 33 — comparación con el log real de la cámara. [G22 §5.16](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 34 — la UI no recibe eventos de modelo (falta av-cam); F3/F4/F5 abiertas. [G22 §5.17](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35 — paridad con el registro real hasta `getNumber : 1`; nuevas herramientas del shim (`PATCHFN` halfwords, `TRACEDEREF`, `GMILOG`, `KEYONACTIVE`); F3/F4/F5 abiertas. [G22 §5.18](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35i — `libStm.so` desensamblado: ScalarSTM es servidor petición/respuesta (ops 1..0xb), no espera notificaciones de av-cam; hipótesis descartada. [G22 §5.18i](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35j — la cola `0x102021f` (CameraBackground) recibe órdenes de la propia app (emisor `libObj+0x19d664`), no de av-cam; 2 de 6 colas descartadas. [G22 §5.18j](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35k — `CameraBackground_act` (→`0x19d6e0`/`0x19d664`) lo lanza `im.elf` en `act_all` (tabla `libIMDB`), disparado por `upm.ko`; el arnés no alcanza `act_all`. [G22 §5.18k](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35l — `CMD_ON` inyectado a `0x94016a` no se consume: `main` de `im.elf` espera un `join` (`[0x154c4]`, INFRA1; objetivo sin identificar) antes de su bucle de recepción; shim `CBLOG`/`SYNCMBX`. [G22 §5.18l](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35m — `act_all`/`CameraBackground_act` reproducidos en el arnés (`NOJOIN`, `SYNCMBX`, `THRLOG`); falta la respuesta de `upm.ko` (`ON_CMP`). [G22 §5.18m](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35n — `ON_CMP`→`APP_ON` a `0x920168` (registrada por `ObjHandover_Create`, no llamado en el arnés); shim `UPMON`. [G22 §5.18n](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35o — el arnés no ejecuta el arranque de módulos/objetos de `libObj` (`Mi/Ma/Tc/Ts/Md/Ms`, `Os/Or`) que en la cámara precede/sigue a `APP_ON`. [G22 §5.18o](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35p — `Mi/Ma/Ts/Md/Ms/Mr` = ciclo de vida de modelos de `ModelManager` (logger `libObj+0x7efef0`); falta el evento de arranque en bloque. [G22 §5.18p](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 38 — acuse *dataflow* de ADF para `ObjMic` (`libBizFw2`: `AdfCh`, `URendezvous`, `osal_msg_size`); `Mi 0ED` cierra y el arnés recorre `Tc`/`Ts`/`Mr` completos. [G22 §5.18v](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 39 — `jackStatus` emulado: estado inicial del jack USB en la lista de `InfraInput` (`KEYINIT=7000001:1:177`); `execCheck retVal 0` sin parches. [G22 §5.18w](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 40 — la UI presenta fotogramas; listas de GPU tipo PICA de DMP con mapa distinto del de la 3DS; F3 sigue en la GPU. [G22 §5.18x](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 41 — menú abierto (`view/GLOBAL_MENU`) y trabajos de GPU decodificados (tipos 2/3/6/7, lista de dibujo de un cuadrilátero texturizado); `TRACEREP`, `gpu_jobs.py`. [G22 §5.18y](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 42 — F3 hecha: cola de la GPU corregida (sin reencolar el trabajo 0), relleno y transferencias PICA en el shim, `gpu_raster.py` dibuja el menú principal; iconos pendientes por `/dev/ldec` (G22-C). [G22 §5.18z](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-C cerrado — `/dev/ldec` es LZPT (como el TPZL); emulado en el shim, el menú principal sale completo (fotos, iconos, texto). [G22 §5.18z](../docs/gui/g22-arnes-ui-qemu.md).
- 12-11-2026: G22-B avance 43 — F4 hecha: teclas inyectadas por la cola del driver abren el submenú «Ajustes personalizados» y se rasteriza; cerrojos de la GPU reales en el shim. [G22 §5.18z′](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: CFW 3.69–3.73 instalados; parche PP en la imagen (G31); menú PP plano y repintado instantáneo. Actualizados PENDIENTES (G15–G20 revisados, G24-A, G30-C), G29 §6 y CURRENT. [PENDIENTES](../docs/PENDIENTES.md).
- 11-11-2026: G32 auditoría del menú Picture Profile del CFW 3.73: cadena menú→libObj→0x4066→cfg sana (31 casos), pero 15 ajustes (Black Level, Black Gamma, Knee, Detail) sin consumidor en el núcleo, Gamma Movie/Still sin efecto por construcción y S-Log3 con gamma 0x17 sin casos por gamma. [G32](../docs/gui/g32-auditoria-picture-profile-3-73.md), PENDIENTES G32-A…D.
- 11-11-2026: G33 Black Level, Black Gamma, Knee, Detail Level/V-H/Limit/Crispening y Gamma Still aplicados en el núcleo (gancho de curva + ganchos APC, `pp_tone.c`), CFW 3.74 construido offline, sin instalar. [G33](../docs/gui/g33-pp-black-knee-detail-still.md), PENDIENTES G32-A/B, G33-A/B.
- 11-11-2026: E26-R85 auditoría con las fotos DSC03749–03779 (Silent / EFCS on / EFCS off): EFCS on aún con la tabla de prueba (exceso +0,8…+1,0 ms, pérdida real 1,0–1,16 ms) → tabla calibrada R85 y `--tabla` en el escritor NVRAM; Silent del CFW sin la calibración R56 (+3,5…+5,5 EV); `camera_silent.py` pasa a 16,73 µs/97 filas. [R85](../docs/capture/e26-r85-calibracion-fotos-3749-3779.md)
- 11-11-2026: R85 §7, segunda tanda DSC03786–03806: tabla EFCS final R85b; a 1/60–1/125 `c` no actúa; EFCS uniforme solo hasta 1/500; electrónico sigue sin calibrar sin el parche RAM.
- 11-11-2026: E26-R86 CFW 3.76 (3.75 + Silent calibrado en la imagen BIONZ) y tabla EFCS R86 de la segunda tanda; construido, emulado y auditado, sin instalar. [R86](../docs/capture/e26-r86-cfw-376-tres-modos-nivelados.md)
- 11-11-2026: CFW 3.76 instalado (arranca) y tabla EFCS R86 escrita en NVRAM; faltan fotos de comprobación. [R86 §6](../docs/capture/e26-r86-cfw-376-tres-modos-nivelados.md)
- 11-11-2026: E26-R87 disparo remoto de los tres modos; Silent del 3.76 corregido y recalibrado (CFW 3.77, sin instalar); tabla EFCS R87. [R87](../docs/capture/e26-r87-disparo-remoto-y-recalibracion.md)
- 11-11-2026: G36 auditoría del selector PP del 3.77 (no pasa de PP6): la ruta de `libObj`/NVRAM/`CamMsgConv` acepta PP7–PP10; la causa es el tope de 7 opciones por lista de la clase Normal, que afecta a 25 de 34 filas. [G36](../docs/gui/g36-selector-pp-tope-7-opciones.md)
- 11-11-2026: G36 §5 CFW 3.78: filas del menú PP partidas en grupos de ≤ 7 opciones (76 filas, 13 páginas, PID_MAX 0x140); 106 pruebas, auditoría como el 3.76; sin instalar. [G36](../docs/gui/g36-selector-pp-tope-7-opciones.md)
- 11-11-2026: CFW 3.78 instalado; arranca y reporta 3.78; falta la prueba funcional del menú PP. [G36 §6](../docs/gui/g36-selector-pp-tope-7-opciones.md)
- 11-11-2026: el 3.78 se cuelga al entrar en Picture Profile (hipótesis 13 páginas); CFW 3.79 con 35 filas en 6 páginas (numéricos a 7 valores, sin Copy/Reset) construido y auditado, sin instalar. [G36 §7–§8](../docs/gui/g36-selector-pp-tope-7-opciones.md)
- 12-11-2026: G22 F5: el arnés arranca con el `nflasha15` del CFW (`pkg_usr.py`, `OVERLAY2`); 3.79 abre la carpeta Picture Profile; el 3.78 reproduce su cuelgue (`SIGSEGV` `libObj+0x5b6242`). [G22 §5.18z″](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-D ventana en vivo (`live.py`): GPU en el invitado, virtio-serial, teclado, estado de VM restaurable; ~1 s por tecla. [G22 §5.18z‴](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-D rendimiento: esperas emuladas que giraban corregidas en el shim; CPU en reposo 598 % → ~75 %, 0,3–0,4 s por tecla. [G22 §5.18z⁗](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-D: las teclas de 12,5 s eran un reenvío del SSE a los 15 s más una carrera copia/dibujo en la GPU emulada (`gpu_sync`); ninguna tecla > 1,1 s; diagnóstico `WAITLOG`. [G22 §5.18z⁗](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-D persistencia: estado de RAM restaurado siempre (0,8 s), guardado al salir y atómico, invalidado por huella; hora del anfitrión servida a `osal_get_date` (formato corregido); escrituras `Backup_write` guardadas en `nvram.json`. Límites: la página Fecha/Hora muestra ceros y los cambios de ajustes del menú no se aplican (ruta no emulada). [G22 §5.18z⁵](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-D cursor: `gpu_draw` descartaba listas de más de 64 vértices (marco naranja y separadores); tope 4095. Cambios de ajustes sin resolver (falta el eslabón diálogo → modelo; no se simula sin verificar). Trabajo pausado por el usuario; resto en PENDIENTES G22-E. [G22 §5.18z⁶](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G22-E T3: configurador previo al arranque (`lanzador.py`, puerto 8700: firmware Sony/CFW/`.dat` importado sin instalar, mapa de teclas editable) y acceso directo `A6000-Emulador.desktop`. [Uso](../docs/gui/g22-emulador-uso.md)
- 12-11-2026: G22-E T4: fuente de sensor en caliente (imagen, vídeo en bucle, cámara web), SD emulada de 4 GB con estructura DCF verificada en av-cam (`DCIM/100MSDCF`, `PRIVATE/M4ROOT/CLIP`), disparo a JPEG y grabación a MP4 lanzados por el anfitrión (sin procesar por av-cam). [Uso](../docs/gui/g22-emulador-uso.md)
- 12-11-2026: G22-E T5: red opcional por slirp con la interfaz `ath0` y la MAC de la cámara, telnet con el busybox 1.13.4 de la cámara (127.0.0.1:2323). Wi-Fi de la UI no se activa (módulos de Sony, `/dev/uipc` entre procesos); adb no existe en el firmware. [Uso](../docs/gui/g22-emulador-uso.md)
- 12-11-2026: G22-D MENU abre y cierra siempre con la ruta real `@V00E` (`DefRootView::ActionOpenSettingMenu`); cambios de ajustes: la UI pide `requestModelExecute("model/STILL_REC", 0x54)` y devuelve 0 porque `ModelStillRec` (`@M00F`) no existe en el arnés; nada simulado sin verificar. [G22 §5.18z⁷](../docs/gui/g22-arnes-ui-qemu.md)
- 12-11-2026: G23 ISP emulado (primer pase): 87 curvas de 2048 pt extraídas de `av-cam` (A6000/A7S/A6300), 15 matrices de Backup `0x30001`, 341 ids de Backup de PP1–PP10 (constructor de libObj en Unicorn); modelo CPU = shader WebGL2; S-Log3 = gamma `0x1f` de la A6300 (RMSE 0,001); RAW↔vista previa BIONZ ΔE76 5,6–7,1 (falta DRO y matriz del estilo). [G23](../docs/gui/g23-isp-bionz-emulado.md)
- 12-11-2026: G23 fase 2: SR2Private de los ARW descifrado (negro 512, WB, matriz `0x7800` = Backup `0x30001` índice 0 byte a byte, curva `0x7802`); vista previa con corrección de lente; ΔE76 medio 32 ARW 6,4 → 5,4 (DRO Auto como ganancia MEDIDA), < 3 no alcanzado (saturados +25 % croma); S-Log2 = curva `0x1c` e ITU709(800%) = `0x1d` (cierra G25 §1); shader 23–64 fps. [G23](../docs/gui/g23-isp-bionz-emulado.md)
- 12-11-2026: G22-E T2b-resto: `POSTROOTEV=11004002:e3` crea `ModelStillRec`; EFCS emite la orden `0x75fa` (`IssueCommandAsync` desde `libObj+0x689745`) sin respuesta de `ObjCamera` ni escritura de Backup; «Señales audio» cambia y persiste (`0x1070026` 01→02, NO_VERIFICADO en cámara) (§5.18z⁸).
- 12-11-2026: G22-E cuelgue de redibujado: `ObjRenderer ChangePosition` bloqueado en `MsgRcv` de `0x59000e` sin respuesta (acuse dataflow probado y revertido); `0x90013e` = bloqueo de fecha, no aviso de cambio; Fecha/Hora y T4b siguen abiertos (§5.18z⁸).
- 12-11-2026: G22-A: en el 3.79 Silent ya es independiente de EFCS (pid `0x12` → `+0x238`), verificado por bytes. CFW 3.80 (sin instalar, `.dat` `7a0e8aae…c429`, auditoría 29/29): el copiador hace `cap+0x41c` = EFCS | Silent, así que Silent manda como en el A6300. El primer 3.80 (`4e37a846…`) no llevaba el cambio. El control BIONZ de la auditoría acepta exactamente PP + Silent calibrado. Protocolo de 4 combinaciones en el informe. [g22a](../docs/gui/g22a-tres-estados-obturador.md)
- 12-11-2026: CFW 3.81 (sin instalar, `.dat` `26854785…caf1`, auditoría 29/29): integración de G22-A (Silent manda sobre EFCS), G32-C S-Log3, G32-D B&W en el núcleo (sin `patch_bw` en `libObj`), G33-B Hi-Light y G35-A PP10 (`pvt_SetParamParamPictureProfile` ≤ 10). Pasan las diez suites de PP y las de G22 (88/88). Lista de comprobación en cámara en [g22a §9](../docs/gui/g22a-tres-estados-obturador.md).
- 12-11-2026: G22-E cuelgue de redibujado resuelto (respuesta VDF tipo 2 a `0x59000e` + `stat_msgq` con pendientes, `libBizFw` `freeOsalId`); Fecha/Hora sigue en ceros (la página no usa `0x900141`) (§5.18z⁹).
- 13-11-2026: G22-E EFCS (estático, [g22-respuesta-efcs-objcamera](../docs/gui/g22-respuesta-efcs-objcamera.md)): `0x9776`=`0x2b5`/`0x2b4`; `ObjCamera` `0x95a308` responde sin LIRO con CMP `0x75fb` {`0x9777`,`0x9502`} y EVT `0x85a6` {`0x9777`,`0x9778`}; Backup EFCS = `0x107086e` (1 B, 1/2), `0x1070361` descartado; en el arnés la secuencia no se ejecuta (despacho de `ObjCamera`, NO_VERIFICADO).
- 13-11-2026: G22-E EFCS en el arnés: trampas QEMU: la orden `0x75fa` no llega al despachador de `ObjCamera` (`0xad76f2`/`0x95a308` sin ejecutar); emulación en `sonyshim.c` (ranuras SET/ACT del modelo y Backup `0x107086e`, carga al arrancar desde `0x681eb2`); la fila cambia y persiste en frío. Zoom pendiente ([g22-respuesta-efcs-objcamera §8](../docs/gui/g22-respuesta-efcs-objcamera.md)).
- 13-11-2026: G22-E EFCS §9: `CAMUSER_OBJCAME` bloqueado en el arranque por la petición dataflow a `0x50004` sin respuesta (con `ACKQ0` se despierta, pero el receptor `0xae892c` no recibe `0x75fa`); `WAITINF=1` en el shim; zoom identificado estáticamente (`0x7612`/`0x7614`, `0x85b1`/`0x85b2`), sin Backup.
- 13-11-2026: G22-E av-cam paso 1 cerrado: `liro_vm.py` llega a reposo sin caídas (mbf, pilas por tarea, respuesta DMM +8/+0xc/+6, sleep 0x910041, FIFO 0xf200X018); CamMgr `0x30001` espera mensajes. Abierto: DMM asíncrono (`rcv Invalid Src`) y paso 2 (conexión con `im.elf`). [PENDIENTES](../docs/PENDIENTES.md)
- 13-11-2026: G22-E av-cam paso 2: puente `im.elf` ↔ LIRO VM (`puente.py`, `AVQ=` en el shim): ObjCamera/CAMLIRO recibe respuestas reales de av-cam (0x4049) y las peticiones dataflow a 0x5700f9/0x5a0048/0x56000f las contesta av-cam; sin EE_START no hay iconos nuevos. [g22-avcam-puente](../docs/gui/g22-avcam-puente.md)
- 13-11-2026: G22-E EE_START investigado: ExeEeStart/SetInit (0x68b4bc) los lanza el motor de estados de ModelStillRec; forzado con `F` en el shim ejecuta SetInit (Backup read_multi implementado) y cae por falta de la propiedad 0x14d de ObjCamera. [§5](../docs/gui/g22-avcam-puente.md)
- 14-11-2026: G22-E EE_START: causa medida (§5.6 de g22-avcam-puente): `ViewStlrec` aplaza `setInitForRec` mientras `ModelMedia` (`@M00A`, clave 0x103) vale 0; con el consultor forzado (`PATCHFN=viewUnified2.so:11c978=1`) sale `EEStart` y CamMgr 0x30001 recibe la secuencia con respuestas de av-cam. Falta emular la detección de tarjeta.
- 14-11-2026: G22-E ModelMedia/tarjeta: cadena de detección medida y 4 arreglos del shim (cabecera osal_msg_size en valloc, snd_msg a colas dinámicas, stat_msgq receptor, read_multi devuelve recuento); `ThreadRM` registra `KEY_MEDIA_MS` pero no hay soportes en `InfraMediaConfig` ni evento; sin cerrar (§5.7 de g22-avcam-puente).
- 14-11-2026: G22-E ModelMedia tarea 2: causa del deviceID=0 (read_multi con tabla de punteros), ModelMedia/ObjMedia arrancan con BKMULTIPTR=1 pero ObjCntMgr cae y el arnés se congela; FRONTRM aun sin cerrar (§5.8 de g22-avcam-puente).
- 14-11-2026: G22-E ModelMedia tarea 3: congelamiento de FRONTRM = atoi del shim; Front a tiempo (FRONTRM=3) y MCMND→SD ya funcionan pero ObjMedia arranca en rechazo (§5.9 de g22-avcam-puente); EEStart sin PATCHFN aun no sale.
- 14-11-2026: G22-E ModelMedia tarea 4: MCMND corregido, bucle 0x7a0020 filtrado a 0x0c000003 y atajo INSHORT=1: ActionMediaDetectIns y montaje iniciado; ObjCntMgr cae después (libObj+0x8456b4 / 0x816860); EEStart sin PATCHFN aun no sale (§5.10).
- 14-11-2026: G22-E ModelMedia tarea 5: ActionMediaMount con atajos (SKIPFN getter 0x81685a, aviso de temperatura); montaje FS falla 0x80000050 (/dev/mmca sin FS); EEStart sin PATCHFN aun no sale (§5.11).
- 14-11-2026: G22-E tarea 6: SD FAT32 legible (sd_image.py, SDIMG, ioctl 0x10f/0x110 de /dev/mmca): Fsys mount OK y ActionMediaMount; NULLMWF/SKIPFN como atajos; freeze tras MSGID_OPEN; EEStart sin PATCHFN aun no sale (§5.12).
- 14-11-2026: G22-E tarea 7: el congelamiento tras MSGID_OPEN es un interbloqueo (8 vCPU en WFI, sin pantalla), no un bucle; CPUWATCH en el shim; EEStart sin PATCHFN aun no sale (§5.13).
- 14-11-2026: G22-E tarea 8: el freeze era im.elf muriendo (EXIT=139): SA_RESETHAND + MonCtrl NULL; corregido, EEStart sin PATCHFN y 11 envios a CamMgr 0x30001; nuevo SEGV a 0,4 s en libObj+0x84b042 (tabla this+0x117c) (§5.14).
- 14-11-2026: G22-E tarea 9: arranque estable con EEStart sin PATCHFN, pantalla de grabacion, menu y Fn; SD FAT32 + atajos (TABLE0, SKIPFN 0x829xxx) por defecto en live.py (--sin-sd); respuesta 0x4015e en el monton (§5.15).
- 14-11-2026: G22-E tarea 10: sin avisos 0x9967/EXPOSURE_BIAS/DMM en el arranque por defecto; pantalla de grabacion solo con iconos minimos (av-cam no envia AE ni responde ajustes); ioctl 5 con capacidad SDHC pero INH_IMPOSSIBLE_TYPE_FS_EXFAT persiste; lista de lo que falta para un disparo (§5.16).
- 14-11-2026: G22-E tarea 11: codec de mensajes CamMgr/av-cam (mensajes.py + test) y clasificacion de ordenes; AE de av-cam sin implementar (falta RE del receptor de 0x20002 en libObj; tabla de manejadores 0x438052d8 no coincide) (§5.17).
- 14-11-2026: G22-E tarea 12: RE del receptor 0x20002 de ObjCamera (ids 0x2014/0x2023… con carga y PARAMID), atajo ae.py (escena constante, --sin-ae) cuyos mensajes ObjCamera convierte (trazas), pantalla aun minima: falta la vista fotografica y medir ISO/EV (§5.18).
- 14-11-2026: G22-E tarea 13: la vista de grabacion ya es ViewStlrec; forzar el dial/modo no cambia la pantalla; manejadores 0x66e130/0x671474 son de datos de toma (0x850b), no AE en vivo; falta localizar el modelo que lee la vista para velocidad/f/ISO/EV (§5.19).
- 14-11-2026: G22-E tarea 14: AE corregido (SHUT_SPEED_DEGREE>=1; antes ObjCamera descartaba el evento); DISP cicla 4 pantallas; dial inicial por KEYINIT sin efecto; los getters de exposicion de la vista nunca se llaman: falta quien instancia/notifica los widgets (§5.20).
- 14-11-2026: G22-E tarea 15: modo de exposicion no viene de av-cam (decide el modelo desde el dial); el 0x7fffffff del dial es estado desconocido de InfraInput; /modo+MENU no reevaluan la vista; siguiente: inyectar estado de dial con evento 0x15070050 (§5.21).
- 14-11-2026: G22-E tarea 16: el KEYINIT del dial llega antes del callback de InputService (112040 solo corre con /modo); retraso en el shim congela el arranque (revertido); mapeo P/A/S/M y widgets de exposicion sin resolver (§5.22).
- 14-11-2026: G22-E tarea 17: estado inicial del dial enviado al toActive (KEYINITON vacio) cambia la vista (2 = iAUTO+ rica; EV +0,3 -> ±0,0); congelamiento de §5.22 era por sustituir el KEYINIT del jack; P inicial y getters de exposicion sin resolver (§5.23).
- 14-11-2026: G22-E tarea 18: dial 0-15 al arrancar (solo 2 = iAUTO+ rica; ninguno P); giro automatico a P no fiable; wrapperShutterSpeed.so/wrapperAperture.so/wrapperIso.so son bibliotecas propias aun sin trazar (§5.24).
- 14-11-2026: G22-E tarea 19: 0x7025 = KEY_POS_MODE_DIAL verificado; wrapper*.so no se cargan (corrige §5.24, sin armado diferido); vista rica de iAUTO+ no reproducible en v1; sin cambios de codigo (§5.25).
- 14-11-2026: G22-E tarea 20: la vista rica exige DISPx3 antes de Fn (escaneos previos solo con Fn invalidos); estados 8/9 dan diseno de disparo con ISO AUTO (PASM probable); KEYINITAFTER en el shim; inhibicion del dial documentada (§5.26).
- 14-11-2026: G22-E tarea 21: la vista pide el info 0x35 del modelo 0xb solo 2 veces; 0x4d1984 guarda el AE cada segundo sin notificar a las vistas; 0x53 lo piden los modelos 0x5a/0xa (§5.27).
- 14-11-2026: G22-E tarea 22: estado 8 con DISPx8: 4 disenos que pintan EV (+0,5 por modo), ISO AUTO, 24M FINE 3:2, AWB A2 G1 pero no velocidad/f/icono de modo; falta traza de retorno de getModelInfo y emisor de info cambiado (§5.28).
- 14-11-2026: G22-E tarea 23: causa del modo ausente: ModeToSetInitParam no se ejecuta (modo 0x7fffffff al primer getRecViewFromDial, 0,28 s tras KEYINIT) -> SetInit sin modo -> nunca SET_EXPOSURE_MODE_CMD; LIVE_MODO_TRAS opt-in (§5.29).
- 14-11-2026: G22-E tarea 24: SendEventInitData solo redistribuye estado guardado (sin peticion al driver); ModeToSetInitParam no corre ni con KEYINIT temprano: corrige 5.29; sin cambios de codigo (§5.30).
- 14-11-2026: G22-E tarea 25: CORRIGE 5.29/5.30: la causa era openView("view/STLREC", 0); OPENVIEWARG = modo (3 = P): icono P desde el arranque, getIso corre; velocidad/f pendientes (§5.31).
- 14-11-2026: G22-E tarea 26: EXFAT se decide en libObj+0x942156 por u16(buf+0x28)=3 (!=4) del struct de soporte (buf+2=0x8400); SKIPFN de SetInhStatus no cambia el contador «----» (§5.32).
- 14-11-2026: G22-E tarea 27: el contador «----» nace en ObjCntMgr: GetStillRecInfo (libObj+0x822cf4) devuelve 0 porque this+0x122c (StillSizeInfoValid)=0, que solo pone MSGID_STILL_SIZE_INFO (0x1013) de ObjStillRecorder; prvSetImageSize (+0x6392b0) nunca corre; EXFAT descartado; A/S/M no cambian la OSD; ISO cambia en la Fn sin orden a CamMgr 0x30001 (§5.33). Sin cambios de codigo.
- 14-11-2026: G22-E tarea 28: CORRIGE 5.33: SetRecordingMode del grabador corre; SetStillSizeInfo (libObj+0x911a54) se corta en MprAcsr::SetDcfCompositeConfig (+0x900034) y no emite STILL_SIZE_INFO; saltarlo da SIGSEGV por componentes nulos de ObjCntMgr; ISO sin orden a av-cam (0x4003 solo por /modo) (§5.34). Sin cambios de codigo.
- 14-11-2026: G22-E tarea 29: onStarting de ObjCntMgr abortaba en SendDbCommand (cola 0x37807c de InfraDatabase sin receptor; Ii 0c7 libmprctrl no cierra); con 826ed0=0 se crean 0x4b8/0x4e8/tabla 0x117c por su ruta real y se retiran TABLE0 y 11 SKIPFN, estable >3 min; contador sigue en ---- (MPR no listo) (§5.35).
- 14-11-2026: G22-E tarea 30: Ii 0c7 libmprctrl no cerraba porque el hilo de ordenes del MPR no se creaba (prioridad RT 117-123 > 99); RTCLAMP=1 (opt-in) cierra Ii 0c7 y arranca InfraDatabase, pero llega 20-45 s tras onStarting (826ed0=0 sigue) y destapa SIGSEGV de UpmWrapper (libmprctrl+0x1fcaf); THREADLOG nuevo (§5.36).
- 14-11-2026: G22-E tarea 31: prioridades RT con mapeo monotono por defecto (RTMAP; la camara usa CONFIG_MAX_USER_RT_PRIO=160, libosal_utm no traduce), UpmWrapper corregido (contexto de osal_reg_msg_queue_cb = t[2], no t[0]; REGARG0=1 revierte), atajo 826ed0=0 retirado y sustituido por SYNCWAIT=37807c:300 (InfraDatabase real responde), Ii 0c7 tarda 16 s sin WLALL (60 s era artefacto del reenvio); arranque estable >284 s tras EEStart; SetStillSizeInfo pasa SetDcfCompositeConfig y this+0x122c=1, GetStillRecInfo llega a +0x83b7e8, contador sigue en ---- (§5.37).
- 14-11-2026: G22-E tarea 32: el contador falla en MprIf::GetStillContentsRemain: la orden 0x2300001c del hilo HddDcfMMgr (libmpr+0x620028) rechaza el estado del MMgr (0x64c298: [this+0x140]=8, exige 4=REC) con ErrCd 0xa/0x31000007 porque MprIf::EnterRec no se llama (grabador libObj+0x8fde20 no corre); Fsys_GetFreeSpace/RemainGet nunca se llaman; test test_vdf_59000e arreglado (era del test, stat_msgq palabra 1 = receptor); sin cambios de shim (§5.38).
- 14-11-2026: G22-E tarea 33: causa raiz del estado 8 del MMgr medida y corregida: ioctl 0x104 de /dev/mmca daba a[0x24/4]=0 (es el ultimo LBA) -> PDM de libInfraFsys con particion de 1 sector -> pdm_part_logical_read 0x12 en la FAT -> Fsys_Mount desmonta (PFFAT_CountFreeClusters -1) -> Fsys_GetVolumeLabel FSYS_E_CORRUPTFAT 0x80000086 -> DiscMount 0x0e520001 -> estado 8; con sd_partinfo_fill (test nuevo) DiscMount llega a estado 4 y GetStillContentsRemain no falla; this+0x2c8 = tipo de FS (FAT32=3 real), INH_EXFAT no causa el ERROR; OSD ahora «--E-» + icono ERROR (contador numerico NO conseguido; candidatos orden MPR 0x40 0x31000002, FlashLoadMp4 0x31000006); estable 1690 s (§5.39).
- 14-11-2026: G22-E tarea 34 (§5.40): rutas de gestion que nombra libmpr (M4ROOT/{CLIP,SUB,THMBNL,GENERAL}, MEDIAPRO.XML, STATUS.BIN, AVIN0001.*), FlashLoadMp4 falla en la carga del MediaProfile (libmpr+0x67ca6c); el Formatear de la UI no termina en el arnes (FormatCmd del MPR sin respuesta, RAM sin cambios); clase SDHC 0x8401 ya correcta por codigo (shim identico byte a byte, sd_cardinfo_fill/sd_media_class/sd_fsys_class con test); sd_image completa=True opt-in; orden D del shim + /sd-volcado (verificada en c40w3: con estructura completa sigue el ERROR y la camara no escribe ficheros al montar); arranques en frio colgados del lado del anfitrion (3 de ~25). Contador numerico NO conseguido.
- 15-11-2026: G22-E tarea 35 (§5.41): el arranque en frio intermitente no viene de a16ca930 (cacc7e0f falla igual); dos fallos medidos: (1) cuelgue 4478 B = interbloqueo del cargador (dlsym perezoso de los envoltorios del shim con el hilo principal en dlopen), corregido con nextsym (tabla rellenada en shim_init); (2) SEGV silencioso de im.elf a 30-60 s (EXIT=139, 9485 B) no localizado (no es ASLR, MTTCG, pilas ni contencion), mitigado con supervisor/reintento en live.py (LIVE_REINTENTOS=6; 5 de 6 arranques con 4 intentos, tests test_live_reintento y test_shim_logic). FlashLoadMp4 (libmpr+0x67ca6c) no abre ningun fichero: Fsys_Open nunca se llama, los 13 Fsys_Stat (AVCHD, DCIM, M4ROOT, 100MSDCF) devuelven 0, solo FindFirst/GetFreeSpace; hipotesis MEDIAPRO.XML/STATUS.BIN refutada. Tarea 3 (Formatear) no abordada.
- 15-11-2026: G22-E tarea 36 (§5.42): SEGV del arranque en frio CERRADO: recursion sin fin del envio sincrono a la cola 0x924126 (callback libObj+0x7ddd88 reenvia a su propia cola; el shim lo entrega en el hilo emisor, 240 B por nivel hasta agotar la pila de THREAD_INFRA1/2), guarda sync_nest en shimlogic.h/sonyshim.c (SYNCREENTRY=1 la quita), 6/6 arranques sin reintento (c42a17-c42b19); fake_open sin buffer de 64 KiB en pila; im.sh imexit_diag + SIGLOG/STKSCAN/STKRSS; 0x31000006 de FlashLoadMp4: la tabla de respaldo del MPR (libmpr+0xa3699c) no tiene entradas registradas y la lectura BKUP RcsTbl (0x22,8) falla antes de ReadFirstPackData; falta hallar quien la rellena.
- 15-11-2026: G22-E tarea 37 (§5.43): origen de la tabla RcsTbl de libmpr (+0xa3699c) MEDIDO: la crea FlashLib::Init -> +0x2b4820 leyendo la particion flash /dev/nflasha4 (DFB: CheckExistSector/OpenSector32/ReadFirstPackData), no un Backup_read; el arnes la dejaba como /dev/null (tamano 0). Opt-in LIVE_NFLASH4=nand-20261020/dev_nflasha4.bin (shim: /dev/nflasha4 fichero real, ioctl 0x6e07 de 16 B, /sys/.../nflasha0p4/start=100864; la estructura de 0x20 B daba SIGFPE). Con la imagen BKUP (0x22,8) ya se lee y ReadFirstPackData se ejecuta; falta un sector 0xb2 valido ((0x23,3), borrado en el volcado): FlashLoadMp4 sigue 0x31000006 y la OSD en P sigue --E- + ERROR (contador NO conseguido); efectos laterales 0x323->0x31000003 y 0x30a->0x31000007. Perfiles c43a-c43g.

- 15-11-2026 · G22-E (§5.44 de docs/gui/g22-avcam-puente.md, tarea 38): origen del icono ERROR y del --E- medido por descarte y cadena. NO es FlashLoadMp4 (mp4Ifo_General::FlashLoadForMsv solo devuelve el error del BkRead; la camara real reconstruye el MP4 desde la SD, sin CreateSector), NO es una caution (SetFactor: solo 0x9c ON por Backup 0x1070053=1 del bk.tbl real; con nvram.json 0x1070053=0 el factor desaparece y la OSD sigue igual; SetTrigger/EnableCaution nunca se llaman) y LIVE_NFLASH4 no es necesario (sigue opt-in). Cadena: ObjCntMgr (MSGID_STILL_REMAIN_EVT) llama a MprAcsr::GetStillContentsRemain (libObj+0x83a718, ok, una sola vez) y luego a SetTargetStillSize (+0x83a918 -> libmpr+0x71f154/+0x451138) que no vuelve: no hay 833ed0 posterior ni evento 0x1021, ModelRecRemainInfo (ActionSetStillRemain +0x622a00; params 0x1001 resultado, 0x1010 recuento) no ejecuta ninguna accion (621ef8: 0 aciertos en 534 s) y la OSD queda en "recuento nunca entregado". Sin cambios de codigo. Pendiente: donde espera SetTargetStillSize (virtual [vtbl+0xec], ER_CMD_CONFLICT?). Perfiles c44a-c44o; sin VMs vivas.
- 15-11-2026 · G22-E (§5.45 de docs/gui/g22-avcam-puente.md): refutado §5.44. MprIf::SetTargetStillSize (libmpr+0x71f154 -> thunk +0x451138 -> [vtbl+0xec] de AviMMgrIf, vptr 0x9067a8 -> 66a01c -> 60c0cc) no envia ninguna orden a cola: toma el cerrojo [inner+0x218] (64c564) y rellena tipo/margen; SI vuelve (833ed0 tras cada llamada con TRACEREP=1, c45t2-c45t5; MUTEXWATCH sin esperas de cerrojo). El evento 0x1021 sale: EventSender (libMWF) -> osal_snd_sync_msg qid 0x97e024 ret 0 (cola local, bit 0x8000, sin ioctl del shim; sync_nest no interviene) -> EventReceiver::CallBack -> ObjMsgList::Enqueue ret 0 (SYNCTRACE=1, c45t16-c45t21). ModelRecRemainInfo se crea pero 622a00/621ef8 0 aciertos y la OSD sigue en --E- + ERROR: falta el consumidor de la lista. Shim: SYNCTRACE opt-in (interposicion de MWF::EventSender/EventBase/EventWrapper/MessageSerializer/ObjMsgList), SYNCLOG por WAITLOG; sin cambio de comportamiento. Pendiente G22-E-1.
- 15-11-2026 · G38-D (docs/gui/g40-g38d-tope-de-velocidad-en-la-ui.md): PARCIAL. UI descartada con bytes (wrapperShutterSpeed solo pide pasos ±1 a @M00B 0x2c); el MIN 1/4000 del arnés lo fija ae.py:107; barrido av-cam (inmediatos Tv, diff A6000/A6300/A7S) sin constante de tope. Abiertos G38-E (localizar ModelCamera/AE) y G38-F (arnés modo S). Sin parche, sin captura.
- 15-11-2026 · G22-E (§5.46 de docs/gui/g22-avcam-puente.md): REFUTADA la hipotesis de la ObjMsgList de §5.45. El EventSender de ObjCntMgr es el del ObjectLifeCycle (receptor 0x97e024 sin lista; manejador libObj+0x445cb4 convierte ObjMsg cat 0x3700 en Event 0x3700+id y EventManager::push dest=2, medido con ganchos PLT SYNCTRACE en c46b-c46m). ModelRecRemainInfo filtra 0x37001030/32/33/34 (init +0x621c5c), no 0x37001021; ObjCntMgr nunca emite 0x1030/0x1032; 0x37001033/34 se empujan pero doAction (+0x6245bc, accion 12 = ActionSetStillRemain) solo corre 1 vez (accion 0). Contador NO conseguido; abiertos G22-E-1a/b. Ganchos opt-in nuevos en sonyshim.c y test_diagnostico_5_46_es_opt_in. TRACEFN sobre funciones calientes (+0x445cb4, +0x7ef960) rompe el arranque.
- 15-11-2026 · G22-E (§5.47 de docs/gui/g22-avcam-puente.md): CORRIGE §5.46. 0x37001033/34 SI llegan a ModelRecRemainInfo (modelo 0x7f; mapeador libObj+0x6233c0 ejecutado, c47d/c47e) y se descartan en los predicados +0x6219a4/+0x621934 porque [this+0xb18]/[this+0xb14] = 0 (medido). Esos flags los ponen las acciones 8 y 3, disparadas por eventos propios 0x1207f005/0x1207f003 (0x12000000+(id<<12)+tipo, via 0x11004003 'enviar a modelo'); en el arnes ningun 0x1207f00k llega (otros 14 modelos si). Emisor de 0x1030/0x1032 (G22-E-1a): ObjCntMgr libObj+0x824060/+0x8245fe (movweq, que §5.46 no vio), id = [[ObjCntMgr+0x4c]+0xf8]==1 ? 0x1032 : 0x1021; el campo lo pone REQ_RSRC_APP_GET_STILL_REMAIN (clave 0x10001005), pedida por MSGID_GET_STILL_REMAIN_CMD 0x3700/0x1031, que solo envia ModelRecRemainInfo (+0x623bc8, acciones 9/10). Sin cambios de codigo ni correccion de comportamiento (simular seria inventar). Abre G22-E-1c (emisor de 0x1207f003/5). Perfiles c47a..c47e; VMs cerradas con /salir.
- 18-11-2026 · G22 arnes video (docs/gui/g75-arnes-e2e-objetivos.md, T10/T12c/T15): E2E-10 CERRADO y E2E-12c CERRADO (T51, MEDIDO): la LIRO VM llega sola al estado 2 del secuenciador ([0x43ede338]=2, guion 0->2, posicion 42) y av-cam contesta 0x3003 seq 15; tests test_avcam_ee_start.py en verde. E2E-15 desbloqueada (PARCIAL): el flujo de video llega a REC, pero 0x3000/0x3024 y el clip en PRIVATE/M4ROOT/CLIP requieren el pipeline de codificacion (encoder/muxer/fs) no emulado en la VM y no se fabrican; bloqueo del secuenciador eliminado. Desbloquea VFR-F3, DVR-F3, TCUB-F3, G70-HD120 y Loop Recording. knowledge-maintenance ejecutado (grafo estable: 1461 entidades / 3562 relaciones).
- 18-11-2026 · G22-E CamMgr (0x30001) emulado: ObjCamera está retenida en modo LRM 0x60 y no recibe respuestas de av-cam, por lo que la pantalla de disparo (view/STLREC, 0x88) no puebla iconos (modo, batería, fotos restantes, exposición). Implementado en sonyshim.c (caso snd_msg, idx 4: lee msg_id en m[0], responde msg_id|0x8000 + resultado 0, entrega a la cola de respuesta en m[-4] vía mbx_post_raw) y en liro_vm.py (servicio_kernel: entrega via entrega(vm, rq, m)). El shim intercepta antes de avq_forward, por lo que los mensajes a 0x30001 no llegan al LIRO VM salvo que se fuerce AVQ. Niveles: shim = INFERENCIA (formato y cola de respuesta deducidos de la tabla de despacho 0x43ffe09c de av-cam.bin y camuser_send 0x4379eba0); MSGID_REQ_OPEN = 0x7504 = INFERENCIA (máquina de modos ExcMgr, §5.18z¹¹ de G22). Prueba en live.py pendiente (requiere QEMU). Commit 88ba41df.
- 18-11-2026 · G22-ARR (docs/gui/g22-emulador-uso.md §Arranque más rápido): el arranque en frío no estaba limitado por CPU (vCPU ociosos) sino por ~128 s de esperas fijas del shim (OPENVIEWAT/STARTGAP/OPENVIEWGAP). CALMA=4/CALMA0=10 las termina al callar el registro de etapas (el primer STARTEV conserva 15 s para no perder el 2.º 0x40ec); caché de colas de av-cam (una LIRO VM menos, 6 s → 0,13 s); GUARDA_MIN=190 porque un estado guardado antes no restaura (atajo, G22-ARR2). Primera pantalla 165–169 s → 111 s, restauración 19,3 s → 7,1 s, fotograma final idéntico (5d3713ae). Descartados midiendo: -smp/tb-size, initrd sin comprimir, reescritura Rust/Go/asm.
- 20-11-2026 OSD-ICONOS-1 cerrado: retirados CamMgr inventado (shim y liro_vm.py, que rompía arranque); iconos poblados por av-cam real vía AVQ (g22-arnes-ui-qemu §5.18z¹⁴).
- 20-11-2026 E2E-16 cerrado: asignador con free en liro_vm.py (osal_free_msg/liro_free/rel_mpf); sesión 30 min sin caída; Puente anota heap_mib cada 30 s (G75 T54).
- 20-11-2026 LIRO-VEL-1 cerrado: LIRO VM de 5,6x a ~1x tiempo real (ganchos MEM_READ por pagina mapeada + reg_read_batch); G75 T55.
- 20-11-2026 E2E-17 cerrado: orden EFCS nativa hasta av-cam (0x4099); atajo EFCS opt-in (EFCSEMU); G75 T56.
- 20-11-2026 G75 T57: tipo 0x4e = ajuste «AF c/obturador» (ActionSetS1AF), no S1; gancho DRP movido a 0x67c148 (pulsar S1) y sesgo 0x759e como ParamStd<signed char> (con int: PreTypeCheck ERROR); DRP-F1 PARCIAL.
- 20-11-2026 G75 T58: DRP llega a av-cam (0x4016 DRO, 0x4055 sesgo; tabla libObj→CamMgr decodificada); sesgo en pasos de 1/2 EV en arnés (DRP-F3); S2/RelLock sin avance.
- 20-11-2026 G75 T59: LRM arranque sí estaba (artefacto de grep sin -a); 2.ª S1 funciona (8/8); 0x755b/0x759f = CMP; paso de EV: sin cambio de cueva (DRP-F3 hecho, DRP-F4 abierto); S2 sin id de CamMgr (E2E-3 sigue en T13).
- 20-11-2026 G75 T60: DRP-F4 (paso de EV 1/2 por NVRAM 0x107076c, cueva -2/-4 con test); E2E-15 REC >=20 s virtuales sin respuesta a 0x3000/0x3024 (falta V/VD de modo video).
- 20-11-2026 G86 menú Fn «LUT»: franja Fn = raíz de 38 hijos + `tbh` valor→SRNum (viewUnified4 `0xdd078`); hijo 39 + valor `0x26` parcheados (fn_lut_menu.py, 5 tests); lista de asignación (CautionConfig ×12) y disparo en caliente pendientes (G12-A2, FN-LUT-2).
- 20-11-2026 G86-B menú Fn «LUT» cerrado offline: lista real del A6000 = `…CustomFunctionNType08` (26→27 ×12), valor guardado = `tabla[0xf]` (ids ranura 1 directos, 2…12 +1), LUT usa el id de ShootMode y valor `0x26`; encadenado en `build_cfw_objetivos` (vu4+listas+tabla); FN-LUT-2 (disparo en caliente) sin gancho seguro, documentado.
- 20-11-2026 G86 FN-LUT-2 cerrado offline: gancho `0x437a2502` (cueva `0x43BE4094`) en la máquina `[LUT] Write Cnt` `0x437a24fc`: al cambiar el Backup LUT pone `[cfg+0x94]=1`, `[obj+0x8a0]=1` y la misma pasada ejecuta Copy3DLUT; `tests/test_g86_lut_caliente.py` (25, Unicorn con la máquina real; transparente sin cambio). FN-LUT-6 (cámara) abierto.
- 20-11-2026 G88 LUT desde `.cube`: parser 17/32/33/64, conversión PC a las 3 tablas ISP con nombres de fichero (`sd_lut.py`, `build_fn_lut --cubes`), ΔE 32³ 0,41 / 17³ 0,66; lectura de SD en cámara descartada (solo IPC `0x439005b8` del revelado ARW) → LUT-SD-1; 11 tests.
- 20-11-2026 G75 T61 E2E-15: `/avmem` (+`Puente(escala)`/`AVCAM_ESCALA`), shim sin SIGSEGV en MOVIE en frío (`gpu_exec1`, tiles 8x8 + `mincore`); en vivo el secuenciador llega a [0x43ede338]=2 y al guion 2→8, parado en la barrera `0x817f` por el módulo 0 (`0x43e9bd58`=`0x102`, pide `0x107`, escrito por `0x437916dc`/`0x43796954`); LIRO VM sin tocar (dato de HW por identificar).
- 20-11-2026 G89 LUT-SD-1 cerrado offline: `.cube` leídos de la SD en la cámara (hilo C→Thumb de 3,6 KB en `viewUnified2.so` por `DT_INIT`, `Fsys_Open/Read` por `dlsym`, `X:/LUT/LUT1…6.cube`, muestreo Q16 a 5×9×9) → blob de 16 KB en el id de Backup `0x150005` → cueva de `av-cam` (`sd=True`, `Backup_read`) con respaldo al `.dat`; `build_fn_lut --sd`, `build_cfw_objetivos --sd-lut`; 17 tests (ARM = referencia bit a bit 17/32/33/64, av-cam real, DT_INIT); nombres = ranuras fijas «LUT 1…6». Cámara → LUT-SD-2.
- 21-11-2026 G75 T62 E2E-15: `0x43796954` no calcula 0x107; puerta `[0x43e9bab8]==[0x43e9bcc0]`=2 cerrada porque X=[0x43e991d0]=-1 (singleton de modo 0x43e4a5a4: +8=0, +0xc=2, +0x1c=0xffff0000); el commit (0x4359f7d8→0x435a0734) no corre y la cola 0x57006d de tsk0x2a no recibe nada; herramienta scripts/gui/avcam/replica.py; sin cambios en la VM.
- 21-11-2026 G75 T63 E2E-15: cola 0x57026d = comandos AVBB/sencore de tsk0x2a, en colas_avcam; el invitado no manda nada a 0x570254/5/6d; candidato AVBB_SCN_START_VIDEO (0x570255, 0x8010306) no emitido; sin corrección (contexto).
- 21-11-2026 G90 LUT: (A) interpolación no decidible offline (HW = 8 bancos por paridad, sin campo «Tetra», sin LUT no trivial jamás ejecutada) → `exp_interp.py` + LUT-INT-1/2, defecto `modelo="ambos"`; (B) `lut_opt.py` ajusta en ΔE2000 (GN + enteros, pesos neutros/piel/foto): ΔE medio 17³/32³ suave 0,36→0,28, película 0,77→0,61, teal&orange 0,41→0,24, agresiva 3,87→2,45; atribución: submuestreo domina, recorte ±64 solo en agresivas, cuantización despreciable; T+LUT película 0,28, agresiva 1,10; M no mejora; `lutsd.c` con corrección Δ²/12 (película 1,44→1,09), ARM = referencia; (C) geometría fija (5×9×9 = máximo de los bancos). Informe [g90](../docs/gui/g90-lut-interpolacion-optimizacion-geometria.md); 5 tests.
- 21-11-2026 G75 T64 E2E-15: `AVBB_SCN_START_VIDEO` y la tabla `{cola,código,nombre}` son de la ruta de servicio `testcmd` (`/usr/scenario/*.so`, `testcmd_run_scenario` en `libObj+0x461624`), no de la UI; `IMCMDLOG` en MOVIE/REC (`e2e69`): ninguna orden a `0x57xxxx`, descartes del shim solo a colas de kernel ajenas a av-cam (`colas_avcam`); sin corrección. Siguiente: quién crea `tsk0x2a`/llama a `Kick 0x4359f7b4` (G75 T64).
- 21-11-2026 G75 T65 E2E-15: el commit de modo es el «Master» de `[CLK_CTRL]` (`tsk0x4`, cola `0xc001bd`, etiqueta `0x80c001bd`, rol `[0x43e4a5a4]`=2, `targetVfc` = VFC absoluto 24 bits; X=(targetVfc−[0x43e991cc])&0xffffff); no es `tsk0x2a`/`0x57026d` (corrige T62/T63). Réplica diagnóstica `master_diag.py`: Master con VFC+4 → módulo 0 `0x107`, `[0x43ede338]`=8, av-cam contesta `0x3000`; `0x3024` sin respuesta; DMM órdenes 4/6 sin modelar. Master no implementado (emisor externo, datos fabricados).
- 21-11-2026 G75 T66 E2E-15/E2E-3: emisor real del Master no hallado (solo av-cam; Darwin en claro sin él); modelo opt-in `AVCAM_RELOJ=1` (`reloj.py`, andamio NO_VERIFICADO: Master cada N tramas con módulo 0 en 0x102) → réplica `[0x43ede338]`=8 y `0x3000` contestado; DMM 4/6/0xD/0x14/2/0xC corregidas (comp en +6, VERIFICADO en bytes), `DMM_UNIDAD` 2,5 MiB; siguiente bloqueo REC: `Sequence_Movie SPC_ERR:0x04 SpicaApiExpandParam` + `[RC] request = NULL`; S2 en vivo: modo 0x203 pero sin captura (RelLock). Sin cámara.
- 21-11-2026 G75 T67 E2E-15: `SpicaApiExpandParam`=4 = cola de 2 ranuras (`0x439533bc`) que solo vacía el ISR de fin de Spica (IRQ `0x51/0x52`, estado `base+0x10` bits `0x10/0x1000`); `spica.py` lo modela (latencia NO_VERIFICADO) y deja 0 errores Spica; `[RC] request = NULL` = anillo de 2 peticiones del driver RC (`+0x164` 4→6→0) que solo libera la IRQ del driver (`0x28…0x32`, cableado id→IRQ leído de los literales de los ISR); `rc.py` modela el fin del DMA y el driver 8 (RCH) cicla; queda el driver 9 (RCV) sin arrancar su DMA y `0x3024` sin respuesta. E2E-3 sin avance (lectura de RelMgr pendiente de sesión viva). Tests `tests/test_avcam_spica.py`.

- 21-11-2026 G75 T68 E2E-15: el driver RC vertical (id 9) usa petición «directa»: carga por DMAC PL080 (canal 8, cadena LLI a `0xf388xxxx`) en vez de arrancar los canales `0xf3881300/1380`; `montura.Dmac._cadena` (cadena LLI mem→mem) y `rc.fin_dmac` (IRQ del driver al acabar la cadena, NO_VERIFICADO) dejan `request = NULL` 68→3 en 20 s; `0x3024` sin respuesta porque solo tiene entrada en los pasos 0x52/0x53/0x54/0x5d de la tabla `0x43ffdd28` y el arnés está en el paso 8 (byte `0x43f9ade8`=1 por la 2.ª `0x3003`); E2E-3 no avanzado; tests `test_avcam_dmac.py`.
- 21-11-2026 G75 T69 E2E-15: secuenciador de pasos decodificado (tabla `0x43ffdd28`, manejador → lista de camino de `u16`, cursor `[0x43ede324+0xc]`, destino `0x43b00798`); `0x3024` solo en pasos 0x52–0x54/0x5d; transición sin resolver; E2E-3/G22-ARR2 sin empezar; sin código.

- 21-11-2026 G75 T70 E2E-3: `RelLock::IsAllowed` está en av-cam (`0x4381d088`, obj `0x43ea03e8`); con el Master la máscara llega a `0xfffffffd` (solo factor 1); S2 se rechaza antes por `[0x43f9444a]`=1 (`0x404b` de libObj sin `0x404a`); con `0x404a`+`0xd00d` inyectadas (diagnóstico) IsAllowed devuelve 1 y luego deniega por el factor 1; sin captura. Nuevo `rel_diag.py` y `/avinyecta`. Restaurar estado guardado no reproduce el arranque de av-cam (G22-ARR2). Siguiente: CamUser ReleaseLock en libObj y factor 1.

- 21-11-2026 G75 T71 E2E-3: `0x404b`/`0x404a` = `SetReleaseLock(bool)` de la UI (`0x684a34`, ObjMsg `0x7512`, params `0x9513/0x9514`); la UI sincroniza con `[this+0xa98]` (=1 solo en un hilo y con `Backup 0x107004b==1`); la `0x404a` de T70 tenía mal el cuerpo (`01 0f 01`); factor 1 = FIFO de 0x100 capturas en RAM compartida `0x82d90000` vacía (productor desconocido); `0xd00d` sin emisor en libObj/av-cam/ELF base; nada fabricado; herramienta `libobj_xref.py`; TRACEFN/IMCMDLOG sin líneas en `e2e73`.
- 21-11-2026 G75 T72 E2E-3: `Backup 0x107004b`=1 en los 27 volcados reales (bk.tbl correcto, solo lo lee `0x68d94c`); las trazas funcionaban (`grep -a`, T71 erraba); `[a98]=1` solo en el objeto `A`; `0x404b` sale al terminar `A` su `pvt_CheckDeviceReady` y nunca hay `684c1c(…,0)`: el 2.º objeto `B` no recibe EeStartCmp/topología de medio, de ahí que no haya `0x404a`; FIFO `0x82d90000` = tabla de CapIdTblMgr (shim da `0x8f000000` anónimo): no modelado. Sin cambios de código. Detalle: docs/gui/g75-arnes-e2e-objetivos.md T72.
- 21-11-2026 G75 T73 E2E-3: `A`=hilo model/STILL_REC (`[a98]=1`), `B`=model/STILL_REC_PANORAMA (`[a98]=0`, sin EeStart: panorama); la hipótesis de T72 «B manda la 0x404a» queda débil; sin emulación ni cambios de código. Siguiente: ver si el id de hilo depende del shim, trazar ExeTerminateSpinal/CaptureStartCmp y leer CapIdTableAcsr.
- 21-11-2026 G75 T74 E2E-3: id de hilo no depende del shim; av-cam sin otro limpiador de [0x43f9444a] y RelMgr+0xc7e=0; la liberación real probablemente es CamMgr `0x977c==0x2b9` → ObjMsg 0x7512 (0,0) → 0x404a (0x992a28), evento av-cam→libObj aún sin identificar. Sin código.
- 21-11-2026 G75 T75 E2E-3: `0x977c==0x2b9/0x2ba` es el parámetro de MSGID_CUSTOM_WB_STBY_CMD (ActionExeCustomWbStby), no un mensaje de av-cam: hipótesis de T74 refutada; en el arranque dos 7512 (1,1) del mismo objeto A (a98=(Backup 0x107004b==1)), una 0x404b, ninguna 0x404a; la liberación de factores exige 0x404a; candidato 0x65d3ac (7512 con ParamList 0x200/0x201 por 0x65e17c/0x65ed88) no se ejecuta en el arranque. Sin código. Siguiente: disparador de la vtable 0x65ee0a y SequenceSetReleaseLock.
- 21-11-2026 G75 T76 E2E-3: flag [0x43f9444a]: S1 (ev1) exige 1, S2 (ev2=0x4045) exige 0 -> debe haber 0x404a entre S1 y S2; av-cam notifica a libObj con 0x205a; 3 vias a la 7512 (UI a98, 7513/0x65e17c, conversion 0xa039 con 0x9515/0x9516), emisor del 0 sin localizar; sin trazas reales de 0x404a/b; sin codigo. Siguiente: escritores de 0x9515/0x9516, llamadores de 0x68daa6, vivo S1.
- 21-11-2026 G75 T77 E2E-3: medido en vivo (e2e82): libObj no manda ninguna 7512 tras el arranque; la 0x4044 (no la 0x4045) es la rechazada por flag=1; con 0x404a inyectada av-cam contesta 0x2038 (libObj no consume 0x205a); nuevo emisor de (0,0) 0x68daa4 (DestroyMediaSingle/Double); 0x677324 es receptor de la 7513, no emisor; sin cambios de código; siguiente: hipótesis «objetivo montado» y EeStart del objeto B.
- 21-11-2026 G75 T78 E2E-3: contador [st+0xf8]=0/[st+0x5f4]=1 balanceados (respuesta 0xf000 a la 0x404b); 0x4042/0x4043 sin respuesta por diseño; objetivo y objeto B descartados; siguiente: autodisparo en vivo (ActionSetSelfTimerMode emite (0,0)).
- 21-11-2026 G75 T79 E2E-3: primer emisor medido de 0x404a = autodisparador (Fn>Modo manejo, ActionSetSelfTimerMode (0,0)); disparo unico vuelve a 0x404b; compuerta 0x68e4f0 (pvt_CheckSetSpinalReflex) solo deja salir (1,1) con objeto listo; en la real a98 debe ser 0; S2 en autodisparo sin 0x4044 (cuenta atras no vencida); siguiente: esperar cuenta atras y leer a98/BackupRead.
- 21-11-2026 G75 T80 E2E-3: a98 = m_SetStatusSpinalReflex (Backup 0x107004b leido solo en 0x68d94c; arnes sirve el dato real); con BKSET=107004b=0 libObj emite la 0x404a real sin inyeccion y S2 (0x4044) llega a IsAllowed (0x2038+0x202e), bloqueada por ranura 0xd00d y factor 1; con a98=1 sigue rechazada; ActionSetSpinalReflex 0x687028 = manejador de 0x75a0 param 0x109; otro (0,0): ActionExeTerminateSpinal 0x69c534. Siguiente: emisor 0xd00d/FIFO (docs/gui/g75-arnes-e2e-objetivos.md)
- 21-11-2026 G75 T81 E2E-3: 0xd00d = KEY_LANC_LEFT (eventos de tecla cat 0x500, tabla libObj 0x109ea4a), sin envoltorio ni emisor en av-cam; IsAllowed pasa con byte [0x43e95950+0xd1]!=0, estado this+0x20==7 o ranura; sin cambios de codigo; siguiente: escritores de [ctx+0xd1] y this+0x20
- 21-11-2026 G75 T82 E2E-3: [0x43e95950+0xd1] = Backup 0x30072 (0 en 76 volcados reales, sin escritor en av-cam); this+0x20 = id de tecla mas prioritaria; en replica [this+0x38]=2 y IsAllowed#1 (factor 1 liberado)=1, #2=0: unico bloqueo = factor 1 (anillo 0x82d90000, av-cam solo escribe [hdr]=0x100; falta productor [hdr+8], quiza libObj CapIdTableAcsr); sin cambios de codigo; siguiente T83: productor del anillo en libObj y [this+0x38] en vivo
- 21-11-2026 G75 T83 E2E-3 (parcial): libObj mapea /dev/mem 0x82d90000 (desc de av-cam 0x3040d7..) y produce el anillo: 0x81e6f4 avanza [hdr+8] por cada mensaje de av-cam aceptado con acceso iniciado; falta mensaje/disparador en la real y [this+0x38] en vivo; sin cambios de codigo; siguiente T84
- 21-11-2026 G75 T84 E2E-3: causa raiz del factor 1: shim responde 0x4015e/0x1000 con area anonima 0x8f000000; libObj reinicia SU encabezado a 0xff (0x81e5b8), av-cam lee el suyo ([hdr+8]=0 -> dist 0); [this+0x38]=2 en vivo; P/linea segfaulta (usar TRACEDEREF); sin cambios de codigo; siguiente T85: probar 0xff en 0x82d90004/8/c en la replica y puente del encabezado
- 21-11-2026 G75 T85 E2E-3: puente del encabezado 0x82d90000 implementado (shim: respaldo compartido + mremap alias, hilo AVH/H; puente.py cabecera_desde_invitado; test en rojo->verde); correccion de T84 (el shim reenvia la 0x4015e a av-cam, phys real 0x82d90000; el fallo era mmap anonimos separados); vivo e2e95 puente OK pero factor 1 activo: libObj no avanza [hdr+8]; replica con avance libera factor 1 -> IsAllowed#2=1 y corre 0x4379eba0; siguiente T86: que hace avanzar a libObj (0x81e6f4, [this+0x11b4]/0x123d)
- 21-11-2026 G75 T86 E2E-3 (parcial): this+0x11b4/0x123d (acceso iniciado) solo escritos por los manejadores 0x84a2b4/0x84b594 (ObjMsg 0x1003); en vivo e2e96 nunca corren; falta el emisor; siguiente T87
- 21-11-2026 G75 T87 E2E-3 (parcial): el 0x1003 de los manejadores libObj es la orden 4 de la 0x4015e (0x1000-0x1002 contestadas, 0x1003 sin respuesta de av-cam en e2e95/e2e89); siguiente T88: manejador 0x4015e de av-cam en la replica
- 21-11-2026 G75 T88 E2E-3 (parcial): T87 refutada: av-cam no responde 0x1003 por diseño (CapIdTblMgr 0x4381cd64 -> {5,0,0xd013} a 0x40193) y libObj no espera respuesta; el acceso iniciado (this+0x11b4) lo pone el ObjMsg interno 0x3001 que nadie encola en vivo; siguiente T89: llamador de 0x8643b4/0x86b914/0x855044
- 21-11-2026 G75 T89 E2E-3 (parcial): 0x8643b4/0x86b914/0x855044 son manejadores de comandos de consola, no corren en vivo (e2e99); emisor real del ObjMsg 0x3001 sin localizar; siguiente T90: ruta de encolado (0xdec0c) y origen del 0x3000 del arranque
- 21-11-2026 G75 T90 E2E-3 (parcial): corregido: caso 0x3000 de 0x84a2b4 ya pone this+0x11b4=1; cuello = evento 0x10001010 (0x848e9a -> 0x822e04 -> 0x81e6f4) que apenas se entrega; siguiente T91: escritor de la bandera en this+0x4c y ruta desde av-cam
- 21-11-2026 G75 T91 E2E-3 (parcial): el evento 0x10001010 es el id 0x10001011 (RESERVE_ENTRY_NUMBER_CMD, tbh usa id-0x10001001); solo lo pone la peticion de recurso de arranque (tipo 8) y con S1/S2 no llega ninguna peticion nueva (e2e100); el pin de captura (tipos 20-23) depende de ObjMsg 0x10000073/74 que 0x84b594 (nunca corre) construye; sin entregas de av-cam omitidas; trampas TRACEFN2 en la bomba cuelgan el arranque; siguiente T92: emisor externo del ObjMsg del pin
- 21-11-2026 G75 T92 E2E-3 (parcial): ObjMsg 0x10000073/74/3d sin emisor externo (barrido completo libObj; los construye ObjCntMgr/CapIdTableAcsr/MprIf); tipos 20-23 salen de la ruta de escritura (pin de datos), no S1/S2; sin entrega de av-cam omitida; el arnes no responde 0x920111/APP_ON por defecto (BOOTINFO/UPMON opcionales; corrige T91) asi que ObjHandover_Create/Os 00F_ObjCntMgr no corren; siguiente T93: que alimenta la cola [this+0xa8]/[this+0xb0] de 0x84b594/0x84a2b4
- 21-11-2026 G75 T93 E2E-3 (parcial): 0x920111 = peticion a upm.ko del g_bf (0,8,2,0x170001,1 real en 46 volcados, solo camara ya arrancada); ObjHandover_Create ya corria (T92 artefacto de WLALL); BOOTINFO real por omision recorta 0x30001 (44->0-14) => opt-in BOOTINFO=real; APP_ON exige act_all de im.elf; S1/S2 sin 0x404b/0x3011; siguiente T94: por que BootType=8 quita ordenes y pin de captura 20-23
- 21-11-2026 G75 T94 E2E-3 (parcial, inconclusa): ActionGetAllBootInfo decodificada (b valido {1,2,4,8}, c EeCap 1-4); g_bf en frio NO_VERIFICADO; biseccion en vivo ruidosa (VM cargada; baseline dio 0 en e2e116/119), c=2 candidato; 0x81b0ec no es tibia; Disparo sin tarjeta no aplica; siguiente T95: repetir en VM en reposo sin trazas y hook contador para ReqRsrc
- 21-11-2026 G75 T95 E2E-3 (parcial): matriz BOOTINFO en reposo (base 45/45; c=2 0/3; b=8 0/45; d 0/45), solo EeCap rompe siempre; ReqRsrc contada por tipo: S1/S2 no pide 20-23; receta 5.18m no envia ON_CMP; siguiente T96: SD emulada y im.elf 0x9234
- 21-11-2026 G75 T96 E2E-3 (parcial): SD emulada ya presente en todas las pruebas (hipotesis descartada); ON_CMP = im.elf 0x9234 (llamador unico 0xa1f6, guarda [0x154dc]==0), necesario para APP_ON; siguiente T97: [0x154dc] y aviso de fase que falta
- 21-11-2026 G75 T97 E2E-3 (parcial): receta 5.18m: im.elf activa 102/155/f8 pero solo llegan act_cmp 102 y 155 (act_count=1; [0x154dc]); falta act_cmp f8 de libInfraMediaPwrMgr => sin ON_CMP/APP_ON; siguiente T98: rutina act de libInfraMediaPwrMgr
- 21-11-2026 G75 T98 E2E-3 (parcial): InfraMediaPwrMgr vive en libObj; su FSM exige inact (0x101) antes de act (0x102) (medido: error 2 linea 0x18d), la receta 5.18m no hace inact; 0x920143 da inact_cmp f8 pero 155 sus_android aborta sin almacen Android (opt-in ANDROIDFS=1 parcial); siguiente T99
- 21-11-2026 G75 T99 E2E-3 (parcial): via fiel = inact_all previo (mem-20261020-log), MprIf sleep descartado; sus_android de 155 aborta im.elf desde ioctl uipc del shim (sonyshim+0x274b0); siguiente T100
- 21-11-2026 G75 T100 E2E-3 (parcial): sonyshim+0x274b0 era fopen (falso positivo de pila, T99 corregido); IMLAST en consola.log al morir im.elf; aborto de sus_android sin causa; siguiente T101
- 21-11-2026 G75 T101 E2E-3 (parcial): abort de sus_android era mount_fs (ANDROIDFS mount interpuesto); ahora inact_cmp f8/ON/act_cmp 102,155 llegan; corte: SEGV nulo libmpr+0x2a7254 (DVDFlashBackup); siguiente T102
- 21-11-2026 G75 T102 E2E-3 (parcial): SEGV de DVDFlashBackup = tabla de FlashLib nula (FlashLib_Open falla con nflasha4 inerte); LIVE_NFLASH4 la sirve pero cuelga el demonio tras open(start) y ObjCntMgr cae en libmpr+0x71e00e; NFTRACE=1; siguiente T103
- 21-11-2026 G75 T103 E2E-3 (parcial): el cuelgue con LIVE_NFLASH4 era WLALL=1; sin WLALL la receta llega a act_cmp f8 (0), ON_CMP->APP_ON, sin SEGV de DVDFlashBackup; faltan ObjHandover/Os 00F y S1->S2; STACKALL/STACKEXIT/IMGREP; siguiente T104
- 22-11-2026 G91 LUT-SW-1: LUT .cube completas (2…129³) por software: lutjpg (C + libjpeg-turbo estática, ARM Cortex-A5) sobre los JPEG de /android/mnt/sdcard (FUSE POSIX), salida = referencia tetraédrica salvo recompresión; ISP fijo en 5×9×9 (G90 §C); corregido de2000 (C2→C2', LUT-DE-1 re-medir G71/G88/G90); falta cámara (LUT-SW-2)
- 23-11-2026 G92 auditoría cadena de color: LUT 3D fija; ranura libre c68[8] (0x440013cc) de la cadena de tono FUN_438538e4 admite curva 1D propia tras la gamma (Unicorn: salida = T[gamma]); T+LUT película 0,79→0,19 ΔE; una sola curva para RGB; segunda curva identidad sin consumidor (LUT-2C-1); falta cueva (LUT-T-1) y cámara (LUT-T-2)
- 23-11-2026 G93 ampliar LUT 3D a 17³: imposible en el ISP (17³ = 4913 palabras frente a ≤1024 de la ventana SRAM; banco 0 necesitaría 729 de ≤128; 9³ tampoco cabe); escritor 0x43b67918 y permutación 0x43bef2ac idénticos en A7S/A6300; BlkOfs Cr/Cb = croma de negros, no geometría; LUT completa solo por software (G91) o en postproducción.
- 23-11-2026 G94 LUT resolución/entrega/fidelidad: ConvSD (cfg+0xd9, FUN_437a1d14) = croma 709→601 solo en MOV/MON (Unicorn; corrige G71 §1a); misma tabla en todos los modos = vista en vivo ~3 ΔE fuera de la foto con ConvSD; tabla precalculada por modo (lut_modos.tabla_convsd) 0,09–0,43; propuesta de bloque precalculado de 5304 B por LUT; gamma de foto y vídeo distintas (134–437 niveles) por comprobar en cámara.
- 23-11-2026 G94 §3 bis: RAM viva (ram-servicio-20261020): ids de color 0x43f790ba = 00/01/ff (sin bit 4) y 0x43e964ab = 0x40 (bit 1 = 0) ⇒ ConvSD inactivo; la misma tabla ya es exacta en vista en vivo y foto; LUT-MODO-1 en espera.
- 23-11-2026 G95 LUT-PKG-1: paquete LUT/LUTn.LUT (A6LT v1, CRC32, tabla 21 bits ajustada en ΔE en el PC); lutsd.c lo prefiere al .cube y solo valida y copia (lutsd_paquete = lut_pkg.valida en Unicorn); teal 0,40→0,07 y película 1,05→0,79 ΔE frente a la conversión en cámara.
- 23-11-2026 G95 §4 CFW 3.84 (build_cfw_objetivos --sd-lut, sin instalar): .dat c6cbcceb…; incluye el arreglo G89 DLSYM_PLT 0xe72e4 (la 3.83 daba pc=0 en DT_INIT) y el diagnóstico de rutas en el blob 0x2000; imagen nflasha15 descomprimida = files/ byte a byte; DT_INIT emulado arranca lutsd_hilo; av-cam frente a la 3.83 solo cambia en ZONA_B (tablas de fábrica, LUT-DE-1).
- 23-11-2026 CFW 3.86 (= 3.84 renumerado, 3.85 previo en la cámara) instalado por USB con pmca-console; arranca; LUT-SD-2 pendiente de prueba con .LUT en la SD.
- 23-11-2026 G96: 6 películas icónicas (peliculas.py, modelo paramétrico en YCbCr + curva S por canal) ajustadas a 5×9×9 (0,23–0,67 ΔE), LUT1…6.LUT en la SD; Tri-X descartado por ΔC ±18 %.
- 23-11-2026 CFW 3.87 Film flasheado por USB desde 3.86 (2.º intento); arranque sin confirmar: la cámara no reaparece por USB.
- 23-11-2026 G98: 3.87 en cámara: parte de los looks idénticos (curva solo en 512 puntos, no en la rejilla de 96 nodos del HW; LUT perdía el cambio con el blob tardío). CFW 3.88: curva por gamma extendida (c68[8]+bd5/be1 en las 4 llamadas a FUN_43852f7c), reintento de LUT y verificación del blob; JPEGCAM/RecipeLab decompiladas (matriz RGB medida y descartada). Instalado por USB el mismo día (segundo intento).
- 23-11-2026 G99: 3.88 en cámara: no todos los looks se aplican y la mayoría apenas se notan; simulados cambian 3,5–11 ΔE (falla la vía HW, no el diseño). CFW 3.89: receta nativa de RecipeLab por película (16 ids, codificación de `Params.writes`, guardado/devolución en Off) + LUT + curva; LUT fija en av-cam descartada por espacio. Instalado por USB el mismo día.
- 23-11-2026 G100: 3.89 confirmado en cámara. CFW 3.90: «Film» con Off + 38 en una sola lista del menú Fn (franja horizontal, infraestructura G86) y en las 12 ranuras; filas sincronizadas, un solo look activo. Sin instalar; tecla personalizada pendiente (FILM-8).
- 23-11-2026 G101: «Film» en una tecla, estático: C1/AEL abren pantallas fijas por función; la rueda de control abre la franja Wheel en ViewTriDial con el nodo elegido por valor (9/10/12 libres). Plan de parche en FILM-8; sin implementar.
- 23-11-2026 STOCK-391: firmware oficial 3.21 reinstalado como 3.91 (`build_326.py 0x91`, 8/8) por USB desde el CFW 3.89; `pmca-console info` = 3.91. Próximo CFW debe ser > 3.91.
- 23-11-2026 G101: CFW 3.91 = 3.90 + «Film» en la rueda de control (valor 9; lista, descriptor 0xdc y cueva en las tres vistas que abren la franja Wheel). Unicorn y cadena sobre ficheros reales; sin instalar.
- 23-11-2026 G102: PP en el CFW Film. El arnés con el `.dat` muestra que la lista vertical NO tiene tope de 7 (Off–PP10, Gamma y Black Level de 31 se recorren enteras): menú PP de 32 filas, una por ajuste con todas sus opciones; Fn generalizado a 10 nodos (Film + 9 PP) y rueda con Film (9) y PP (10); carpeta «Film Simulation» con una fila por marca (Kodak/Fujifilm/Fujifilm Sim). Tests G102 + regresión; CFW 3.92 sin construir por petición del usuario ([G102](../docs/gui/g102-pp-film-selector.md)).
- 23-11-2026 G102 §5: «Extra fine» (parche G39) añadido al CFW Film 3.92; comprobación teórica en el `/usr` generado (lista Default, Fn por el mismo nodo raíz), `libObj` sin cambios en la orden `0x4036` y av-cam del 3.92 aceptándola en la VM. Sin construir.
- 23-11-2026 G104: ISO 409600 — parche de av-cam hecho (topes 0x2c→0x2f, tabla de EXIF de 48 entradas en ZONA_B, integrado en build_cfw_film; 4 tests Unicorn). Mapa de dominios de código de libObj (0x2a = AUTO/centinela según la función) y de la UI; libObj/UI pendientes (ISO-409-A…C). Sin segundo amplificador conmutable en av-cam (ISO-DUAL-1). Sin construir.
- 23-11-2026: G104 §8 — mapa de la pantalla ISO (ViewManualControlDial_D, filas 0x6–0x12 libres), referencia A7S 3.20 para 409600, envío del ISO a av-cam (0x4e7c30); pruebas x1/x3/x4 sin mover el tope de 25600; setup.sh del arnés con linux-libc-dev 7.3.5.
- 23-11-2026: G104 §8.5 — la pantalla ISO (ViewIsoSensitivity) ocultaba a mano 32000/40000/51200 (0xf0ae0); iso_ui_patch (3 B en viewUnified4) integrado en build_cfw_film; 51200 elegido y mostrado en el arnés.
- 23-11-2026 USB-CARGA: carga USB con la cámara encendida. Cadena verificada offline (OZ8072 ← Darwin I²C MFS1 ← servicio `0x2804d3` de av-cam ← `usb_darwin.ko`); a la A6000 solo le faltan `usb_darwin.ko`/`usb_buspwr.ko` de la A6300 y NVRAM `0x1210001=6`. Kit `scripts/usb_carga/` (GPIO neutralizado con `R_ARM_NONE`, prueba por telnet en tmpfs); prueba en cámara pendiente (USB-CARGA-1).
- 23-11-2026 USB-CARGA corregido: la A6300 no carga encendida (guía de Sony); sus módulos solo dan alimentación USB y `set_charging_enable` de `usb_darwin.ko` es una traza. Darwin controla el OZ8072 (`0xc390` regs 4/5/6, `0xc4e8` única escritora de los bits de carga, «Off exit» `0x8c64` corta al encender); la carga real pasa a USB-CARGA-3 (parche de Darwin).
- 23-11-2026 USB-CARGA-3 estático: la orden de ajuste `USB_CHG_IC_SET` (libsencore/adjstctl, bloque 0x0d20, código 0xa0, OSAL 0x2804be) pasa por av-cam al canal de órdenes de Darwin (`0x1b8cc`→`0x243a4`, caso 0xa0 hallado con Unicorn) y `0xc8bc`/`0xc660` escribe reg4/5/6 del OZ8072 con la cámara encendida. `0xc6f0` traduce reg4 a mA. Herramienta `scripts/usb_carga/chg_ic_set.py` (pmca, simula por defecto).
- 23-11-2026 USB-CARGA-3 en cámara: USB_CHG_IC_SET aceptado por senser y por telnet (`adjstctl.elf 0xd20 0xa0 b:…`); a 900 mA el nivel pasa de 58 a 60 % y se queda fijo 20 min; falta el control `normal` para separarlo de la alimentación USB. `prueba_telnet.py` preparado.
- 23-11-2026 USB-CARGA-3 con cargador de pared por telnet: la orden sola no carga (control 56→49 % en 13 min; carga 1500 mA 48→42 % en 15 min); `adjstctl` da `res 0x88` con el cargador de pared (indicador `[0x20000029]`). Queda la vía del parche de Darwin.
- 23-11-2026 USB-CARGA-3 estático: `res 0x88` es el tiempo agotado de av-cam (`0x43b5d4fe`), no `[0x20000029]` (el despachador ignora el retorno de `0xc8bc`). `adjstctl.elf` fija la secuencia 1 (`0x8d20`) y Darwin descarta la secuencia repetida (`0x1b91a`): la prueba con cargador de pared no envió nada. `prueba_telnet.py` alterna una copia con secuencia = bloque; tabla `cmode`→`0xc4e8` del modo apagado documentada.
- 23-11-2026 USB-CARGA-3 repetida con la orden aplicada (`res 0x01`): `carga` 1500 mA deja el nivel fijo en 53 % 12 min (no sube); a los ~800 s el Linux de la cámara dejó de responder (telnet sin intérprete, adb sin respuesta, ping sí).
- 23-11-2026: G104 §8.6–8.7 — filas ISO 64000…204800 en la pantalla ISO, la pantalla de disparo y libObj (iso_ui_patch.patch_filas/patch_vu2, iso_libobj_patch, iso_ui_recursos, traducción 0x4b…0x50 en iso_avcam_patch), medidas en el arnés e integradas en build_cfw_film (N_CFW=6); 256000+ bloqueado: libObj devuelve el código 0x4d; iconos A7S no se dibujan.
- 23-11-2026 USB-CARGA-3 10 min con la orden aplicada: 48 → 50 % (≈ +0,18 %/min) y `BATT_V` 0xc8→0xc9, frente a ≈ −0,5 %/min en `normal`; sin cuelgue. Primer indicio claro de carga real con la cámara encendida.
- 24-11-2026: CFW Film 3.92 (`--pp`: PP, Film Simulation, Extra fine, Silent, ISO hasta 204800) construido, auditado 29/29, arranca en el arnés e instalado en la cámara (3.91→3.92, `pmca-console info` = 3.92).
- 24-11-2026: INC-392 — con el 3.92 la tecla izquierda («Brillo de monitor») reinició la cámara y no enciende. Auditoría G105 §1: instalado = construido; vista de brillo correcta en el arnés (/usr del 3.92); ningún parche en esa vía; núcleo por capas sin solapes; SWD sin IDR. Causa NO_VERIFICADA. G105-B: `build_cfw_film.py --funciones` y 5 builds 3.93 (base Silent, film, pp, exfine, iso), auditoría 31/31 cada una, para alternarlas con `pmca-console firmware --reflash`.
- 24-11-2026: INC-392/G105 §4 — la cámara volvió a encender sola tras cargar; la actualización normal 3.92→3.93 no entra al actualizador; forzado por SWD (R48 cfg, 2 r0→0, BootMode 3), trabado al primer intento, ciclo de energía y `Done`: build `film` 3.93 instalada y verificada (`pmca-console info`).
- 24-11-2026: G106 — auditoría estática de las builds 3.93. La cámara refuta el tope de 7 (Black Level −15…+15). PP7–PP10 y S-Gamut no se guardan (la ruta de `libObj` está verificada; causa en el envío o la respuesta, abierta). Extra fine: BKID EXFINE = 0 en la NVRAM → `exfine_size_patch` (`libmprctrl`). La capa ISO del núcleo es idéntica a la del 3.92. Ids CFW que pisan Color Depth G de PP1–PP4. Cinco builds nuevas con auditoría OK.
- 24-11-2026: G107 — causa de PP7–PP10/S-Gamut: `PreTypeCheck`/`EnumValueCheck` (`libObj` `0xa3a21c`, definiciones `0xfde034`) solo admite los 8 Color Mode y 12 Gamma nativos; además B&W/S-Gamut usaban `0x504`/`0x505` (centinelas `NO_SET`/`COMP_RESULT_OK` en la A6000). Arreglo `pp_valuecheck_patch` + VALUEID `0x589`/`0x58A`; `pp` reconstruida. `ID_LIBRES[2..5]` eran parámetros PP → `0x107020C…F`. `ZONA_A`/`ZONA_B` son tablas vivas (EIS T1 y BOKS), halladas con barrido de referencias relativas al PC. ISO arranca en el arnés con la NVRAM del 22-11 y el av-cam de la build. `OPCIONES_POR_LISTA` 7 → 99.
- 24-11-2026: G108 — bucle de `iso`: ISO en NVRAM `0x10700c1`; con `0x4d` (204800) `iso`/`iso_ui` no mandan órdenes a av-cam en el arnés (0/5) y sí `iso_nucleo`, `libObj` o vu2 de fábrica, o vu2 sin el gancho `isInhOn` (pid `0x2f` = enum nativo `0x10`); pid `0x20` (51200) → 5/6 (ruido del arnés ≈ 1/3). Validador ISO de `libObj` sin `0x3fd…0x3ff`/`0x50e…0x510` (causa de ISO-409-A) ampliado con `amplia_pids`. Film/ISO del núcleo a `ZONA_G18` (`0x43faf300…`), rechazo con PP; el bloqueo de Film en el arnés resultó ruido (vieja 1/5, reubicada 2/4). Builds `iso` `fee2bc4f…`, `iso_ui` `4d7083c9…`, `iso_nucleo` `103cfaa3…`, `film` `727fb352…`, `film_nucleo` `c8603133…`. [G108](../docs/gui/g108-bucle-iso-y-zonas.md)
- 24-11-2026: G109 — mezcla pp+film+exfine+iso(≤128000): PP llena el hueco G18, Film/ISO pasan a `0x43fb7e80…0x43fb8ee0`; la imagen ext2 de `nflasha15` se quedaba sin sitio (8 320 > 7 164 bloques; `viewUnified4` truncado) por las copias de la tabla de relocaciones de `_anade`, ahora ampliada en el sitio; build `todo` `fd4d853c0527a41fd782010b281808f190464899b1dfed8bce8512297c52c14e` `todo_ok`, 152 tests, sin instalar. Informe docs/gui/g109-mezcla-pp-film-exfine-iso.md.
- 24-11-2026: G110 — Film 3.93 no cambia WB/A-B/G-M: la receta va por `Backup_write` con la app viva y no llega a `libObj` (el WB se aplica por `WrapperWhiteBalance::setWhiteBalance` → `requestModelExecute`); RecipeLab escribe con la app de cámara cerrada + `sync` (orden 0xf). Mejora propuesta: setters de la GUI en el nodo Film (`viewUnified4`/`7` ya los importan). 14/38 looks tienen A-B/G-M = 0. FILM-9.
- 24-11-2026: G110 ampliado — JPEGCAM aplica en vivo con `Camera.setParameters` (PP off, estilo, WB/shift, Color Depth, matriz, curva); PP activo vs look: gamma/Color Mode/Black Gamma/Color Depth rompen el look; regla Film y PP excluyentes y lista de ajustes en gris (FILM-10).
- 25-11-2026: G111 §15 — icono Fn descentrado: el panel dibuja la imagen arriba; los ajustes nativos de icono simple usan 70×60 centrado y solo la propiedad 1 (no 70×35 + propiedad 4 del Estilo creativo). Iconos regenerados a 70×60, nodos solo con propiedad 1; verificado en el arnés (build de prueba 4.90, no instalar). Resumen del funcionamiento de los iconos y siguiente paso (4.01 + --iconos). ICON-1.
- 25-11-2026: G112 — open gate en vídeo (siete frentes en paralelo). El recorte 16:9 nace en el modo de lectura del IMX210 (vídeo 1996×1124; foto 6000×4000 a 14,98 Hz (66,8 ms); Live View `0x03` = 2000×800 = altura completa anamórfica). A 24/25/30p un 3:2 con binning 3 (≈1996×1333) cabe en el barrido; a 59,94 Hz no. Muro real: el codificador, `FUN_436124b8` (coincidencia exacta con 5 rasters) y `FUN_4391c540` (1920 ⇒ alto 1080), así que el único 3:2 que pasa es **1440×960** por la rama «no full HD» del ctor `0x43a7bf56`; 1920×1280 queda bloqueado. Formato de película: orden LIRO `0x4000` (23 B, aspecto en `0x11`) con solo 16:9/4:3/15:9, aunque `libObj` tiene vocabulario 3:2 (`MOVIE_ASPECT_3_2` `0xda6df6`). HDMI topado a 1080 y el sensor cambia a 1996×1124 al grabar; PMCA/SDK no exponen geometría. Añadidos OG-1…OG-5; sin tocar la cámara. [Informe](../docs/gui/g112-opengate-video-3-2.md).
- 25-11-2026: G113 — opengate implementado en estático: alto 3:2 del modo `0x19` (1124→1333 en la fila de 72 B `0x43bc1a30`, período de 48 Hz intacto), codificador que acepta 1440×960 (cueva `0x43fb8480` sustituye el `cmp` de `0x4361255c`, ctor del perfil 1 `0x43a7bfba` a 960) y variante 60p (línea 676 ciclos, cuadro 1333 = 59,99 Hz). Build `og` `daaaf81f…` con auditoría 29/29 y 7 tests Unicorn. Además, el límite de 66,75 ms a 24 MP no se puede mejorar estáticamente (período `a·b/54,054 MHz`, única palanca el blanking: +5,1 %); el 3:2 sí llega a 60p. [Informe](../docs/gui/g113-opengate-video-parche.md).
- 25-11-2026: G113 (cierre estático) — OG-E: el pedido del codificador es un embudo único (`0x4361234e` → `0x43a7c8fa`) y el raster que elige perfil son los u16 `+0x56/+0x58` del bloque de formato (`obj+0x45a/+0x45c`); cueva en `0x43612364` que reescribe 1920×1080 → 1440×960 sin tocar 720p/480p/1440×1080. `apply_bytes` pasa a ser el opengate completo (3:2 a 24p y 60p). Build 3.96 `eb0c0481…`, auditoría 29/29, 8 tests. Barrido: los 12 `movw #1124` son logs y descriptores de UI, no aritmética de buffers. Sólo falta validación física (OG-8).

- 26-11-2026: G114 — LUTs propios: decisión y especificación. `.cube`→`.LUT` v2 (3128 B, tabla + curva; v1 1080 B sin curva) como vía principal; `.cube` en SD de respaldo; `lutjpg` para foto exacta. Rejilla 5×9×9 no ampliable (generador 9×9×5; matiz: 8³ cabría en bancos pero ningún registro lo dirige). Mejoras: T tras gamma (elegir por LUT), ΔE2000, modelo real (LUT-INT-1), paquete precalculado; M no aporta. Validador `scripts/lut/cube_spec.py` y 75 `.cube` medidos: solo las 6 de `luts/peliculas` son aptas; `sosang` = Panasonic S1II (planas, 31–384 nodos recortados), `vlog` = entrada log. Auditoría: `ZONA_A`/`ZONA_B` son T1/BOKS (G107) → LUT-C reabierto, LUT-SD-2/T-2 bloqueados; CFW 3.86 instalado las lleva. `film_a6000.de` convertía a Lab dos veces (corregido). [G114](../docs/gui/g114-lut-propios-especificacion.md)

## H1 — Eye AF en tiempo real por la API remota de touch AF (26-11-2026)

Carril nuevo, independiente del obturador, a petición del usuario. Se descartó la vía interna: la orden
`PARAMID_EYE_START_AF` (`0x4054`) solo copia al espejo y no tiene consumidor localizado (g83), `Camera::FC`
no tiene canal externo y la A6300 tampoco expone API de ojos. La vía real es la **API remota que la cámara ya
tiene**: `setTouchAFPosition` (params `[x, y]` `double` en **porcentaje 0..100**, respuesta
`[0, {"AFResult": bool, "AFType": "Touch"}]`, mensaje `0x192/0x8d`) y `startLiveview` (HTTP `chunked`, un JPEG
por trozo; la app compone la URL con el puerto 8080 y `orb-server` arranca con `-p 10000`). El `orb-server` de
la A7S es idéntico byte a byte y el de la A6300 no añade ninguna API de ojos. Implementado en el PC
`tools/eye-af/` (detector YuNet con degradación Haar, cliente JSON-RPC con autodetección de puerto, parser de
Live View por SOI/EOI, controlador con suavizado + banda muerta + límite de Hz + salto de sujeto +
cancelación, bucle con ventana y grabación, y `fake_camera.py` con el mismo contrato); lanzador
`scripts/eye_af.py`. Verificación sin cámara: 28 pruebas (`tests/test_eye_af_{api,tracker,loop,detector}.py`),
incluido el bucle completo con visión real contra la cámara falsa (19,3 fps, 16–19 ms de detección, orden de
AF en las coordenadas del ojo detectado); `ruff`/`mypy` limpios. Límite: **nada en hardware**; el estático es
de fw3.21 y la cámara está en 3.93. Entregables: [informe](../docs/capture/eye-af-tiempo-real.md),
[orb_touchaf](../analysis/eyeaf/orb_touchaf.md), [orb_liveview](../analysis/eyeaf/orb_liveview.md),
`tools/eye-af/README.md`, `tools/eye-af/BENCH.md`. Pendientes H1–H3 en `docs/PENDIENTES.md`.
Cero escrituras en cámara o firmware.

## 26-11-2026 — paquete reconstruible del arnés (R10)

Publicado en la rama `harness/arnes-completo` del repo privado de handoff (100 MB): rootfs y `/usr`
de Sony 3.21 ya extraídos (53 MB), kernel/initrd de Debian fijados y cabeceras del shim (34 MB),
volcado NVRAM del que sale `bk.tbl`, `AV-CAM.BIN`/`IDT_CAM.BIN`/`liro.ko` (12 MB) y la config del
configurador. Se instala de una vez con `./instalar.sh` (herramientas, clona el código de la punta de
`main`, venv, artefactos, `setup.sh` y tests), que deja el mismo árbol donde se mejora el arnés;
`DESARROLLO.md` mapea cada pieza a su fichero. Verificado desde un clon limpio: instalación en 42 s,
SHA-256 ok, initramfs, shim y `bk.tbl` construidos, 54 tests pasan y 7 saltan, primer arranque 167 s
con pantalla idéntica a la anterior y restauración 3 s; editar `emu_config.py` mueve el test que lo
cubre y revertirlo lo devuelve a verde. Detalle en [PENDIENTES](../docs/PENDIENTES.md) R10 y en
[G22-E](../docs/gui/g22-emulador-uso.md#reconstruirlo-en-otro-equipo-26112026).

## H3/H4 — Eye AF nativo: verificación y finalización estática (26-11-2026)

A raíz de la corrección del usuario («debe ser AF nativo; la A6000 ya tiene Eye AF pero solo mientras se
pulsa el obturador»), se verificó la cadena nativa en `av-cam.bin` fw3.21. **VERIFICADO:** existe un motor
de detección de ojos propio (`Camera::FC::Drv::ProcessEdt`, `FC/Drv/fc_drv_edt.cpp`, cadenas «EyeDetection»
`0x43cf7022`, servicio `idt_edt_start`); el resultado trae los dos ojos con validez por ojo (`+0x5f`/`+0x60`)
y coordenadas (`+0x56..+0x5c`), se copia al contexto de FC (`0x437b6ece`→`ctx+0xde..0xe7`) y `0x437b7598`
lo convierte en los ocho registros de área de AF (`0x437b7200`). **El único camino de entrada es el
manejador de respuesta de una petición de AF** (`0x437b7ea0` `ReplyForTouchShutter` ← thunk `0x43aef72e`),
y hay un temporizador de un disparo que caduca el estado (`0x437b74a4`, período `u16[cfg+6]×1000 ms`): eso
explica que solo actúe mientras se mantiene pulsado. **Diferencial A6300 (fw2.01):** las dos tienen el
detector (`EyeDetection`, `idt_edt_start`, `CPafStateEyeStart`), pero solo la A6300 tiene el estado continuo
`CPafStateEyeFocus` y la capa `CheckSetEyeStartAF`/`SET_EYE_START_AF`; `PARAMID_CAMSETTING_EYE_START_AF` es
**Eye-Start AF** (sensor del visor), no Eye AF, lo que corrige la etiqueta de `g83`. **Finalización
entregada:** (i) app de cámara `tools/eye-af/camera/` (`ar.eyeaf`) que usa el detector propio
(`FaceInfo.leftEye/rightEye`) y manda el punto con el mensaje nativo — compila con JDK 17 + `android.jar`,
se firma (`out/EyeAf.apk`, 16,7 KB) y su núcleo Java puro pasa **32 comprobaciones** sin Android
(`tests/test_eye_af_camera_core.py`, 3 pruebas); (ii) `tests/test_eye_af_native_evidence.py` (6 pruebas) fija
con bytes las afirmaciones del informe. Límite: **nada probado en cámara**; la cadencia de peticiones de AF
en AF-C vive fuera de `av-cam` (NO_VERIFICADO) y el enganche por VD (vía H5) exige parche de código en RAM
de BIONZ. Cero escrituras en cámara o firmware.

## 2026-11-26 — Montaje del volumen y carga del IFO MP4 (libmpr.so, estático)

Se cierra la pregunta «por qué el IFO del MP4 no se carga y qué condición exacta lo impide», sobre `libmpr.so`
(`0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`, ELF32 ARM *stripped*) y el anillo MPR del dump
`ram-servicio-20261020` (VA `0x82DF9300`-`0x82DFC400`, SHA-256 `f96c6152…ff2fdbf`).

- Los cinco literales del anillo tienen emisor único e identificado por VA: `MountCmd : Flash Mount Error` (`0x8EA305`)
  → `AviMMgrCmd::MountCmd` `0x626DB8` (carga en `0x626F18`, gemela con *driveLetter* `0x627020` / `0x627204`);
  `GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted` (`0x8E9EAA`) → `AviMMgrCmd::GetDeviceInfo` `0x625C4C` (`0x625C7A`);
  `FlashLoadMp4 : CreateAndLoad Error` (`0x8EA6B8`) → `AviMMgrCmd::FlashLoadMp4` `0x627BEC` (`0x627C86`);
  `Err RcsBackupTblData` (`0x823999`) → llamante de `RcsBackupTblData` (`0x35EA1C`) en `0x3AFA94` (impresión `0x3AFB2C`)
  y tres copias más; `CheckSalvageStatus` (`0x90A075`) → `MMgrAvcHdIfoAcsr::CheckSalvageStatus` `0x671DAC` (línea 791).
- **Códigos resueltos con tablas del propio binario**: tabla `{nombre, código}` MMgrGlobal en `0x8F6CA8` →
  `0x31000006 = ER_CMD_CONFLICT` (y es la rama **por defecto** del traductor `0x64E300`, `0x64ECEC`),
  `0x31000007 = ER_INTERNAL`, `0x31000002 = ER_INVALID_PARAM`, `0x31001001 = ER_DIFFERENT_DEVICE_TYPE`,
  `0x3100200C = ER_NOT_MOUNTED`; mapper AVI `0x1DA818` → `0x32400001 = ER_FAILED`; traductor `0x6F0D4C` →
  `0xB0800001` genérico de `mp4Ifo` (rama `0x6F0E40` para `0xXX100000` y default `0x6F0EBC`);
  `0xA0100003` = comando HD-AVC `0x4E` fallido en la capa de comando (`0x520BFC`).
- **Orden obligado**: `GetDeviceInfo`/`MountCmd` (`[this+8]->vtbl[0x140]`) → `FlashMount` `0x62684C` → DFS mount
  `0x3BB220` (éxito ⇒ `[this+0x140]=4` vía `0x64C5DC`, `0x626960`) → `CheckSalvageStatus` (estado AVI ∈ {2,3,4,6},
  `tst #0x5C`) → gate `0x64C298` con `state==4` → `CreateAndLoad` `0x67CA6C` → `CreateSub` `0x67C5C4` → `LoadSub`
  `0x67C8CC` → `Load` `0x67C9C0` → `mp4Ifo_If::Load` `0x6E823C` → `mp4Ifo_General::Load` `0x698FB8` → `FlashLoadForMsv`
  `0x698EC8` → `RcsBackupTblData` `0x35EA1C` (única lectura real del volumen).
- **Conclusión operativa**: `0xB0800001` y `0x31000006` son códigos por defecto y no identifican causa; la huella de
  «volumen ilegible por DFS» es `Err RcsBackupTblData` → `0xB0800001` → `0x31000006`, mientras que un IFO corrupto pero
  legible produciría un código específico (`0xB0400005`, `0xB0510001`, `0xB0F30001`…). Si el gate de estado no da `4`,
  el mensaje es otro: `FlashLoad* : ER_SEQUENCE` + `0x31000007` (IFO no cargado, sin tocar la tarjeta).
- **NO_VERIFICADO**: identidad de las virtuales `vtbl[0x140]`/`[0x60]`/`[0x168]`; cuál de las dos vías de `MountCmd`
  disparó la línea del anillo (el anillo no es transcripción completa: falta `MountCmd : ` y `###GRecMount IN###`);
  semántica nominal de la cabecera `0x10` (solo su uso); que el estado de `vtbl[0xF4]` comparta el enum `AVI_STATE_*`.
- Evidencia reproducible en `reports/evidence/film-pb-1-sub-mount-ifo-20261126/` (21 listados + `extraer_evidencia.py`).
  Cero escrituras en cámara, firmware o tarjeta; solo lectura del binario y del dump.
