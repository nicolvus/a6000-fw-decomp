# FILM-PB-1 (sub) — Camino de decodificación de vídeo y su dependencia de entorno

> **Contraste físico del caso `MAH04204`.** La reproducción alcanzó un fallo de fin
> de arranque del decodificador. DMM estaba activo y los ficheros de microcódigo
> coincidían con Sony. Esto acota la discusión estática de §5 a sus escenarios
> originales. [Medición y traducción del error](film-pb-1-sector31-resultado-20261126.md#10-respuesta-de-inicio-del-decodificador-y-estado-del-bloque-av).

Fecha: 28-11-2026. **Solo análisis estático** del firmware 3.21 de fábrica y del paquete CFW
instalado. Cámara no accesible en esta sesión (sin red, sin USB, sin `adb`).
Evidencia en [`reports/evidence/film-pb-1-sub-decodificador-20261128/`](evidence/film-pb-1-sub-decodificador-20261128/).

**Direcciones:** los VA de `libmpr.so` / `libObj.so` son **ELF (base 0)**, los mismos que usan
[la auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md) y [el productor del `0x1A`](film-pb-1-productor-mpr-20261126.md).
Los VA `0xC01Fxxxx` de este repo son de Loader3 y aquí no se usan.

Continúa [el productor del `0x1A`](film-pb-1-productor-mpr-20261126.md),
[la auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md) y
[la sub‑investigación del WBI](film-pb-1-sub-wbi-20261127.md).
Origen de la pregunta: [traspaso](film-pb-1-traspaso-20261125.md) + hecho nuevo (un clip grabado por
la propia cámara tampoco se reproduce, su miniatura tampoco aparece y **sí graba**).

---

## 0. Veredicto en una página

| # | Pregunta | Respuesta | Confianza |
|---|---|---|---|
| 1 | ¿Quién abre `/dev/ldec`, `/dev/*dec*`, `/dev/dsp*`, dma? | `/dev/ldec` **solo** `libObj.so`; `/dev/dmac` **solo** `libmpr.so`; `/dev/uipc` solo `libosal_uipc.so`. **No existe** ningún `/dev/dsp*`, `/dev/vdec`, `/dev/avdec` ni `/dev/dma` creado por el kernel de la cámara | ALTA |
| 2 | ¿Dónde está el decodificador H.264? | **Fuera de Linux.** En el *core* AV (`/system/av-cam.bin`, RTTI `McAvcDec*` + `AvcDecVideoCtrl` + `McAvcDecClkCtrl`) con microcódigo DSP de `/usr/sabin` (`ZM_AVCDP` / `ZM_AVCDC`). En Linux no hay decodificador: solo un cliente de mando (`libObj` `InfraMovieDecoder*` → `libmpr` `MovieDecoderIf`/`BBControl`) | ALTA |
| 3 | ¿Miniatura de clip y reproducción comparten decodificador? | **Sí, en el camino "movie decoder"** (`SetNextThumbnailParamForMovieDecoder` → `SetBBThumbnailRegionParam`/`SetBBThumbnailBufferParam` → `RunParam:[ONLY_I]` sobre `mp_movieDecoder`). Hay además un camino JPEG (`PlayJpegThum` + `*ThumbnailReaderFilter` + `StillDecodr`) para miniaturas almacenadas. **Los dos viven en el mismo core AV** | MEDIA-ALTA |
| 4 | ¿Necesita módulo de kernel, firmware de DSP o estado de arranque? | **Sí, tres cosas**: (a) 37 kmods en orden fijo desde `sbin/init` (el stack NAND `devno,dmac,ldec,lld,nand` y `dmm.ko DmmConfig=/setting/DmmConfig.bin`); (b) `/system/av-cam.bin` cargado por `im.elf` en `0x83541000`; (c) microcódigo/tablas de `/usr/sabin` que pide `av-cam.bin`, más `/setting/{sen/smode,mode/dmode}` | ALTA |
| 5 | ¿Es el decodificador la causa del `0x1A`? | **No.** Las dos guardas que producen `0x1A` (`0x437C0A` y `0x437C3C`) son **puramente de metadatos/TvSystem** y se ejecutan **antes** de `MoviePlayerIf::PbStart` (`0x307F54`, línea 108 del mismo manejador). Un decodificador caído daría error **después**, con otra traza | ALTA |

**Consecuencia práctica:** el síntoma «no miniatura + no reproduce + sí graba» **se explica sin
tocar el decodificador**, pero solo si el que falla es el **lector de metadatos del MP4**
(`MP4 ifo`), que es justo lo que consultan las dos guardas y también el `ThumbnailReaderFilter`.
Una avería del decodificador, por sí sola, **no** puede producir el `0x1A` observado.

---

## 1. Inventario de dispositivos: quién abre qué

### 1.1 La lista completa de nodos la da `devno.ko`

`kmod/devno.ko` (rootfs 3.21, `nflasha7`) contiene el objeto `udif_devnodes` (900 B) con la
tabla de nombres que el kernel publica. Volcado completo en
[`01-devnodes-devno-ko.txt`](evidence/film-pb-1-sub-decodificador-20261128/01-devnodes-devno-ko.txt):

```
sio  ldec  dmac  uipc  backup  mmca-char  mmcb-char  mmcc-char  mmca … mmccd
ms-char  mcmn  sata…  stream  stream2  usb/*  jet/*  hdmi  hdmi_external_tx  cec
dmpgles2  boss-t1  boss-t2  boss-t3  hdmi_input
```

(`strings -a -n 3 kmod/devno.ko`, sha256 `b1b66b93…8599e`.)

**No aparece ningún nodo de decodificador de vídeo**: ni `vdec`, ni `avdec`, ni `dsp`, ni `codec`,
ni `mpeg`. La única aparición de `/dev/vdec` en todo el firmware está en una regla genérica de
Android (`bin/ramdisk.img_unpacked_unpacked/ueventd.rc`: `/dev/vdec 0660 system audio`), que
ningún driver del CXD crea → véase
[`02-dev-strings-por-fichero.txt`](evidence/film-pb-1-sub-decodificador-20261128/02-dev-strings-por-fichero.txt).

### 1.2 Barrido de consumidores en el `/usr` de fábrica

Comando: `for f in $(find . -maxdepth 2 -type f \( -name '*.so*' -o -name '*.elf' \)); do strings -a -n 5 "$f" | grep -E '^/dev/[a-z]'; done | sort | uniq -c`.
Resultado íntegro en [`02-dev-strings-por-fichero.txt`](evidence/film-pb-1-sub-decodificador-20261128/02-dev-strings-por-fichero.txt).

| Nodo | Ficheros que lo mencionan | Quién lo crea |
|---|---|---|
| `/dev/ldec` | **solo** `lib/libObj.so` | `kmod/ldec.ko` (rootfs, `/kmod/ldec.ko`) |
| `/dev/dmac` | **solo** `lib/libmpr.so` | `kmod/dmac.ko` (`pri_mode_ch_0_3=1 pri_mode_ch_4_7=1`) |
| `/dev/uipc` | `lib/libosal_uipc.so` (+ `init` del ramdisk Android) | `kmod/osal_uipc.ko` |
| `/dev/stream`, `/dev/stream2` | `libObj.so`, `libmpr.so`, `libInfraMtpServer.so`, `libInfraMediaCommon.so` | `kmod/stream.ko`, `kmod/stream2.ko` |
| `/dev/dmpgles2`, `/dev/fb0`, `/dev/gpio`, `/dev/cec`, `/dev/compass` | `libObj.so` | GPU / panel / GPIO |
| `/dev/dvdc`, `/dev/ipcm`, `/dev/msm`, `/dev/threadplot` | `libmpr.so` | **ningún kmod de 3.21 los declara** (cadenas heredadas; NO_VERIFICADO si se abren) |

### 1.3 `/dev/ldec` **no** es el decodificador de vídeo — cuatro pruebas

1. **Nombre de compilación** (cadena del propio `.ko`):
   `/home/jp10239/git-work/build/141H/141H.DSLR.DM_UUD3.reco.LATEST.diadem.set/Etools-NAND-BOSS-lld_131H/driver/boss/src/ldec/../boss_core/hw/boss_hw_ldec.c`
   → el LDEC pertenece al **BOSS Low Level Driver de NAND** (`Etools-NAND-BOSS-lld_131H`).
2. **Simbología** (`readelf -sW kmod/ldec.ko`): `boss_hw_ldec_{set,process,wait,stop,lock,get_state,resource_init,enable_irq,disable_irq}` y `boss_lld_get_base_addr_ldec`. Ningún símbolo de códec.
3. **El consumidor es `lld.ko`**: `mumin_devif_ldec_read`, `boss_lld_ldec_read_process`, `boss_lld_ldec_read_int_state`, junto a `boss_hw_arm7_comm_*` y `mumin_devif_firm_reset`
   ([`04-lld-ko-ldec.txt`](evidence/film-pb-1-sub-decodificador-20261128/04-lld-ko-ldec.txt)).
   Es exactamente el camino «lectura de NAND → descompresión por LDEC» ya caracterizado en
   [R16/R17 y R36](../docs/capture/e26-r36-causa-fallo-325.md) para la carga del firmware.
4. **Sin sintaxis de vídeo**: ni `nal`, `slice`, `cavlc`, `cabac`, `sps`, `pps`, `avcc` en `ldec.ko`
   ([`03-ldec-ko.txt`](evidence/film-pb-1-sub-decodificador-20261128/03-ldec-ko.txt)). El driver es
   un *poker* de registros + DMA (`dst_phys`, `dstlen`), no un decodificador de flujo.

**La cadena de `libObj.so` sí existe, pero en otro sitio.** El literal `/dev/ldec` está en el
clúster `grm::bmp` de gráficos, junto a `Skip bit blit.`, `FPS: %.2f`, `Invalid input buffer address`,
`Failed BMP_GetPhysicalAddress()` y `BMP_Error grm::bmp::BMP_GetPhysicalAddress(void*, off_t*)`
([`13-dev-ldec-dmac-detalle.txt`](evidence/film-pb-1-sub-decodificador-20261128/13-dev-ldec-dmac-detalle.txt)).
Además **no hay ni una referencia literal** al VA de esas cadenas (`0xd2e5dc`, `0xd2e5e6`, `0xd2e6a6`:
0 apariciones como `u32`), porque se indexan por la **tabla de log** `{ptr,id}` de `0xfcbe10`
(entrada `0xd2e5a2 / 0x40803`). Conclusión: es código de *blit* de bitmaps que en este modelo puede
no ejecutarse nunca. **NO_VERIFICADO** si es alcanzable; en cualquier caso **no puede ser el
decodificador H.264**, porque el control del decodificador de vídeo (`AvcDecVideoCtrl`) está dentro
de `av-cam.bin`, al otro lado del core AV, no en el espacio de usuario de Linux.

### 1.4 `/dev/dmac` tampoco

`libmpr.so`: `/dev/dmac`, `/dev/dmac open failed`, `ioctl DMAC_MEM_TRANSFER faild`, `DMA Close Error`,
`DMA Close Error`, en el clúster de comandos de monitor `MDV`/`RECMDV`.
`kmod/dmac.ko` se carga con `pri_mode_ch_0_3=1 pri_mode_ch_4_7=1` y sus símbolos son
`boss_hw_dmac_*` (`start_transfer`, `get_transfer_result`, `proc_setbuf_reg_unit`): un **motor de
DMA de memoria** genérico, no un códec.

---

## 2. Dónde está realmente el decodificador H.264

### 2.1 Topología (verificada por cadenas, no por documentos previos)

```
 sbin/init  (nflasha7, /usr = nflasha15)                       CPU «AV-CAM»            DSP (sabin)
 ─────────────────────────────────────────────                 ─────────────           ────────────
 insmod devno dmac ldec lld nand … dmm stream stream2 uipc
        │
        ▼  exec
 /usr/bin/bootin.elf ──► /usr/bin/im.elf s|g|r|u|l|i
                              │  dlopen("/usr/lib/libObj.so")         ┌────────────┐
                              │      └─ NEEDED libmpr.so, libmprctrl  │ av-cam.bin │
                              │  "fn=/system/av-cam.bin load=1 debug=1"│ 0x83541000 │
                              └────────────── carga ─────────────────►│ (física)   │
                                                                      │ McAvcDec*  │
   libObj: InfraMovieDecoder*  ── uipc/DMM/STM ── BBControl ─────────►│ AvcDecVideo│──► ZM_AVCDP
   libmpr: MovieDecoderIf/BBControl  (CMD_ENTER/RUN/NEXT_FRAME/…)     │ Ctrl       │    ZM_AVCDC
                                                                      └────────────┘
```

Evidencia de cada flecha:

| Flecha | Evidencia |
|---|---|
| `init` → kmods | cadenas de `sbin/init`: `/kmod/devno.ko`, `/kmod/dmac.ko` + `pri_mode_ch_0_3=1 pri_mode_ch_4_7=1`, `/kmod/ldec.ko`, `/kmod/lld.ko`, `/kmod/nand.ko`, …, `/usr/kmod/dmm.ko` + `DmmConfig=/setting/DmmConfig.bin`, `/usr/kmod/stream.ko`, `/usr/kmod/stream2.ko`, `/usr/kmod/osal_uipc.ko` ([`05-init-arranque.txt`](evidence/film-pb-1-sub-decodificador-20261128/05-init-arranque.txt)) |
| `init` → `bootin.elf` | `sbin/init`: `/usr/bin/bootin.elf` |
| `bootin.elf` → `im.elf` | `bin/bootin.elf`: `im.elf s &`, `im.elf g &`, `im.elf r &`, `im.elf u &`, `im.elf l &`, `im.elf i &`, `gdb --args im.elf`, `im.elf target=<im_target>` |
| `im.elf` → `libObj`/`libmpr` | `bin/im.elf`: `dlopen`, `/usr/lib/libObj.so`; `readelf -dW im.elf` **no** lleva `libObj` en `NEEDED` ⇒ lo carga en caliente; `libObj` sí lleva `libmpr.so` + `libmprctrl.so` en `NEEDED` ([`08-im-elf-proceso.txt`](evidence/film-pb-1-sub-decodificador-20261128/08-im-elf-proceso.txt)) |
| `im.elf` → `av-cam.bin` | `bin/im.elf`: `fn=/system/av-cam.bin load=1 debug=1` (única aparición de `av-cam` en todo el `/usr`); la tabla de montajes de `init` (registros de 20 B en `0x3344`) monta `/dev/nflasha3` en `/system` y `/dev/nflasha15` en `/usr` ([`14-init-tabla-montajes.txt`](evidence/film-pb-1-sub-decodificador-20261128/14-init-tabla-montajes.txt)), y `av-cam.bin` (11 427 236 B) vive en `nflasha3` |
| Linux → core AV | `lib/libStm.so` (`STM::DmmHandler`: `dmmOpen/dmmAlloc/dmmFree/mmapExtent/osalSndRcv`) + `libosal_uipc.so` (`/dev/uipc`, colas `snd to invalid qid`) + `MB` de `libObj` (`OBJAVBBCBASECLASS::StmCh`, `DmmCh`, `AdfCh`, `DmmAccessPLA`) |
| core AV → DSP | `av-cam.bin`: `Camera::SaFuncDrv::sa_func_*` (driver de funciones del DSP), `[ADF]…UNIT_TYPE_…`, `DMM_RET_ERR_UNIT_TYPE`, y las rutas `/usr/sabin/*` |

### 2.2 El decodificador de vídeo en `av-cam.bin`

Nombres RTTI/typeinfo presentes (cadena literal en el binario, ver
[`06-avcam-decodificador.txt`](evidence/film-pb-1-sub-decodificador-20261128/06-avcam-decodificador.txt)):

```
McAvcDecParam  McAvcDecState  McAvcDecMcmd  McAvcDecModeMgr  McAvcDecClkCtrl  McAvcDecPinCtrl
McAvcDecSeqCtrl  McAvcDecSTCCtrl  McAvcDecPtsNode  McAvcDecVDecIf  McAvcDecVDisplayIf
McAvcDec24PVDisplay  McAvcDecRelFrameIterator  McAvcDecEsIndexQueCtrl  McAvcDecPtsIndexQueCtrl
AvcDecVideoCtrl  AvcDecVideoCtrlIf  AvcDecVideoParam  AvcDecVideoState  AvcDecVideoDebugInfo
CdcCtrlDec{IfCall,Param,Seq,SeqNori,SeqStop,SeqClose,DecSeq,Mcmd,Timer,CIIf,CMIf,SEIf}
McAvcDecState{Inactive,DecReady,NormalDec,FastDec,Pause,FastPause,SlowDisp,DecErr}
CodecErrAdapter  InCodecErrAdapter  ModuleDecodeBase  ModuleDecodeJpeg  ApiDecodeJpeg
WrapJpegDecode  ProcPinDecoderBase  DefAvcDecVideoParam
```

Dos cosas que importan para la pregunta 4:

* `McAvcDecClkCtrl` y `McAvcDecPinCtrl` ⇒ el bloque decodificador **se enciende por reloj y se
  enruta por pin** desde el core AV; no hay registro de Linux que lo toque.
* `AvcDecVideoCtrl` ⇒ el decodificador H.264 es un **bloque hardware con registros propios**,
  gobernado por `McAvcDecSeqCtrl`; el DSP sólo aporta microcódigo (`ZM_AVCDP`/`ZM_AVCDC`).

### 2.3 Qué librería lo encapsula y qué proceso lo pide

| Capa | Artefacto | Nombres |
|---|---|---|
| Modelo/vista | `/usr/lib/libObj.so` | `InfraMovieDecoder`, `InfraMovieDecoderSeq{DecOpen,DecStart,DecNextFrm,NextThm,DecStop,DecClose,DecChgSpeed,SetOutputMoviePb,DecWfiInternalEvt}` + logs `[InfDecoder]…` |
| Servicio de medios | `/usr/lib/libmpr.so` | `MovieDecoderIf` (`mp_movieDecoder`), `BBControl` (`GetPlayRegionInfo`, `SetBBPlayMovieParam`, `SetBBThumbnailRegionParam`, `SetBBThumbnailBufferParam`, `DrawPixels`), `MDEC : [InitTable],[CMD_ENTER],[CMD_RUN],[CMD_CHANGE_SPEED],[CMD_NEXT_FRAME],[CMD_NEXT_THUMBNAIL],[CMD_STOP],[CMD_EXIT]`, callbacks `CB_MovieDecoder{Run,Stop,NextFrame,NextThumbnail,ChangeSpeed}`, eventos `"Decode Ready"`, `"Decoder Displayed"`, `"Stream End"`, `"Decoder Error"` |
| Proceso | **`/usr/bin/im.elf`** | `dlopen("/usr/lib/libObj.so")`; **ningún** ejecutable de `/usr/bin` enlaza `libmpr`/`libObj` en `NEEDED` (barrido de `readelf -dW` sobre `bin/*.elf` y `lib/*.so`); los únicos artefactos con `NEEDED libmpr.so` son 5 plugins `scenario/MPR_SCN_*.so` (cargados por `scenario.elf`); en `/system` (Android) tampoco aparece `libmpr` |

Detalle en [`12-camino-linux-decoder.txt`](evidence/film-pb-1-sub-decodificador-20261128/12-camino-linux-decoder.txt).

### 2.4 El microcódigo del DSP: `/usr/sabin`

`av-cam.bin` pide rutas absolutas de `/usr/sabin/` (29 cadenas). Las cabeceras de los módulos son
auto-descriptivas: `aa 0a 13 91` + versión + **nombre interno de 8 caracteres en el offset 0x10**
([`07-sabin-microcodigo.txt`](evidence/film-pb-1-sub-decodificador-20261128/07-sabin-microcodigo.txt)):

| Fichero | Nombre interno | Versión | Qué es |
|---|---|---|---|
| `sa_avcd_performance_zma.bin` | `ZM_AVCDP` | `0x01c8` | **decodificador H.264, perfil «performance», core ZMA** |
| `sa_avcd_compatible_zma.bin` | `ZM_AVCDC` | `0x01c9` | **decodificador H.264, «compatible»** |
| `sa_avce_{performance,performance_plus,quality}_zma.bin` | `ZM_AVCEP/PP/Q` | — | codificador H.264 (grabación) |
| `sa_jpeg_dec_1core.bin` / `_1unit.bin` | `SAJPGD_C` / `SAJPGD_U` | `0x02`/`0x01` | decodificador JPEG |
| `sa_jpeg_enc_1core.bin` / `_1unit.bin` | `SAJPGE_C` / `SAJPGE_U` | `0x02` | codificador JPEG |
| `sa_aaclcdec.bin`, `sa_ac3dec.bin`, `sa_bd_lpcmdec.bin` | `ZM_AACD`, `ZM_AC3D`, `ZM_LPCMD` | — | audio |
| `sa_zima_startup_zma{0,1}.bin`, `…minna{,1}` | `SA_Z_ST0/1`, `SA_Z_MNS/MN1` | `0x00` | *startup* de los cores DSP |
| `sa_dcv.bin` | `SA_DCV__` | `0x13` | core DCV (imagen) |
| `dcv_psf_table_{movie,still}.bin` | `IMX210…`, `SAL50 CenGch_3` | — | tablas de calibración **por sensor** (no del códec) |
| `sa_star.bin`, `star_kernel_param.bin`, `spica_musashi_*_tap_step{1,2}.bin` | `SA_STAR_`, … | — | pipeline de imagen / coeficientes |

Observación importante para la hipótesis «decodificador caído»: **codificador y decodificador H.264
son microcódigo del mismo core ZMA** (`ZM_AVCEP*` vs `ZM_AVCDP/C`). El hardware DSP está vivo si la
cámara graba. Lo que puede fallar de forma aislada es la **carga de un microcódigo concreto** o el
bloque hardware `AvcDecVideoCtrl`, no el DSP entero.

---

## 3. ¿Miniatura del clip y reproducción comparten el decodificador?

### 3.1 Hay dos caminos de miniatura, y solo uno usa el decodificador de vídeo

Cadenas de `libmpr.so` (catálogo completo en
[`11-miniatura-vs-reproduccion.txt`](evidence/film-pb-1-sub-decodificador-20261128/11-miniatura-vs-reproduccion.txt)):

```
Camino A — miniatura LEÍDA del contenedor y decodificada como imagen fija
  PlayJpegThum()                                   ← "Callback::IndexPlayer <---- PlayJpegThum errCode["
    ThumbnailReaderFilter  (Mp4 / Xavc / M2ps / Dcf / DvAvi / Wav)
    "ThumbnailReaderFilter->DisconnectDecordStillInfoOutputPlug()"
    "delete [StillDecodr]"   "create [STILL-DECODER] mp_movieDecoder: 0x…"

Camino B — miniatura EXTRAÍDA DEL FLUJO DE VÍDEO por el decodificador de película
  SetNextThumbnailParamForMovieDecoder()
    "Issue Cmd: BBControl::GetPlayRegionInfo"
    "Issue Cmd: mp_movieDecoder->SetBBThumbnailRegionParam"
    "Issue Cmd: mp_movieDecoder->SetBBThumbnailBufferParam"
  setRunParamForMovieDecoder()   "RunParam : [ONLY_I]"   "Direction[FORWARD]"
  "CB_MovieDecoderNextThumbnail"   "check OK ( NEXT THUMBNAIL from Movie Decoder )"
```

* **Camino B comparte decodificador con la reproducción, al 100 %**: misma instancia
  (`mp_movieDecoder`), misma cola de comandos `BBControl`, misma máquina de estados `McAvcDec*`;
  solo cambia el modo de ejecución (`ONLY_I`, buffer y región de destino).
* **Camino A no comparte decodificador de vídeo**: usa el decodificador *still* (JPEG,
  `SAJPGD_*`) o ni siquiera eso, si el contenedor ya trae la miniatura en un track aparte.
* **Lo que sí comparten los dos caminos** es el **lector del contenedor** (`mp4Ifo_If.cpp`,
  `Mp4ThumbnailReaderFilter`, `MMgrMp4IfoAcsr`) y el **transporte al core AV** (`STM`/`DMM`/`uipc`).

**NO_VERIFICADO**: cuál de los dos caminos usa la rejilla de reproducción del A6000 para un MP4
propio. La vecindad de cadenas sugiere que el camino B se usa cuando el contenido es una película y
A cuando hay miniatura almacenada; sin cámara no se puede medir.

### 3.2 `GetPlayThumbnailInfo` (0x6E8430) no decodifica nada

`libmpr 0x6E8430` (fichero `mp4Ifo_If.cpp`, línea `0x1a9`, nombre literal embebido):

```
006e8430 push.w {r4,r5,r6,r7,r8,sb,lr} ; sub sp,#0x3c
006e8438 mov r4,r0 ; … mov r6,r1 ; mov r8,r2 ; mov sb,r3
006e8442 bl   0x696394            ; entrada de traza ("START")
006e8454 ldr  r0,[r4,#4] ; movs r1,#0x23 ; movs r2,#1
006e845a bl   0x5bad00            ; toma de mutex; si falla -> b0100002 en 0x6E8468
006e8470 ldr  r3,[r4]  ; ldr r1,[r7,#0x30] ; ldr r2,[r3]
006e849c ldr  r5,[r2,#0x18]       ; vtable del objeto «ifo Acsr» + 0x18
006e84a0 blx  r5                  ; llamada virtual: lector del MP4
006e84a6 bl   0x5bacb0            ; suelta mutex
```

Es un **envoltorio**: mutex + una llamada virtual al lector de MP4. No hay ni un `BL` a
`STM`, `DMM`, `BBControl` ni a `MovieDecoderIf`. Volcado completo en
[`10-guardab-issupportcontent.txt`](evidence/film-pb-1-sub-decodificador-20261128/10-guardab-issupportcontent.txt).

---

## 4. Dependencias de entorno (lo que se prepara al arrancar)

### 4.1 Módulos de kernel: orden fijo desde `sbin/init`

`strings -a -n 6 sbin/init` (sha256 `6bfcaf00…6fb4d6`) da la secuencia completa, con parámetros
([`05-init-arranque.txt`](evidence/film-pb-1-sub-decodificador-20261128/05-init-arranque.txt)):

```
/kmod/devno.ko
/kmod/dmac.ko          pri_mode_ch_0_3=1 pri_mode_ch_4_7=1
/kmod/ldec.ko
/kmod/lld.ko
/kmod/nand.ko
/usr/kmod/osal_utm.ko  /usr/kmod/osal_uipc.ko  /usr/kmod/utimer.ko  /usr/kmod/backup.ko Backup_load=0
/usr/kmod/osal_ulogio.ko  ulogio_initfile=/setting/ulogio.bin
/usr/kmod/input.ko  /usr/kmod/udate.ko  /usr/kmod/indctr.ko  /usr/kmod/i2c.ko  /usr/kmod/sircs.ko
/usr/kmod/stream.ko  /usr/kmod/stream2.ko
/usr/kmod/usb_portMonitor.ko  … /usr/kmod/kikilog.ko
/usr/kmod/dmm.ko       ← DmmConfig=/setting/DmmConfig.bin
/usr/kmod/upm.ko  /usr/kmod/nfc.ko  /usr/kmod/grm_ma.ko  /usr/kmod/grm_gles.ko
/usr/kmod/hdmi.ko  /usr/kmod/cec.ko  /usr/kmod/accel.ko  …
```

`init` también lee, antes de montar: `/proc/cmdline`, `/proc/udm/upm_bootmode`,
`/setting/sen/smode`, `/setting/mode/dmode`, `/setting/env.txt`, y publica
`LD_PRELOAD=/usr/tool/libkmcsup.so.2.0.0`, `echo 1000000 > /proc/sys/vm/max_map_count`.

Tabla de montajes de `init` (20 B por registro, `0x3344`), decodificada en
[`14-init-tabla-montajes.txt`](evidence/film-pb-1-sub-decodificador-20261128/14-init-tabla-montajes.txt):

```
/dev/nflasha2  → /setting       vfat
/dev/dnflasha3 → /system        vfat   (primer intento)
/dev/nflasha3  → /system        vfat
/dev/nflasha10 → /tmp           vfat
/dev/nflasha15 → /usr           cramfs  → luego /dev/dnflasha15 ext2 → luego /dev/nflasha15 vfat
/dev/nflasha9  → /usr/upgrade   vfat
/dev/nflasha7  → /rootfs        ext2
```

⇒ **`/setting` es una partición aparte (`nflasha2`, vfat)**: `DmmConfig.bin`, `DmmConfigExtra.bin`,
`sen/smode`, `mode/dmode` son **datos de fábrica/campo**, no viajan en el paquete de actualización.

### 4.2 `dmm.ko`: memoria compartida con configuración **de arranque**

```
author=Sony Corporation   license=Proprietary
parmtype=DmmConfig:charp        ← init pasa  DmmConfig=/setting/DmmConfig.bin
parmtype=DmmConfigExtra:string  ← el módulo lee  /setting/DmmConfigExtra.bin
```

`DMM` no es un códec: es el **gestor de extents/unidades de memoria** compartida entre Linux y el
core AV. `libObj` lo consume por `OBJAVBBCBASECLASS::DmmCh` (`dmm_comp_open_unit`,
`dmm_comp_alc_unit`, `dmm_comp_free_unit`, `dmm_comp_get_unit_info`) y `DmmAccessPLA`
(`GetExtAdrsFromDmmOpen`, `GetExtSizeFromDmmAlloc`). Los `UNIT_TYPE` los comparten `av-cam.bin`
(`UNIT_TYPE_ZMA_ZOOMNR_DEBUG`, `MEM_UNIT_TYPE_CAM_RAW_DM_AFWORK`, `DMM_RET_ERR_UNIT_TYPE`) y
`analysis/dmm-unit-types.json`.

**Dependencia de entorno real**: si `/setting/DmmConfig.bin` o `/setting/DmmConfigExtra.bin` faltan
o no cuadran, `dmm.ko` no puede construir el mapa y **no hay memoria para buffers de vídeo** (ni
grabación ni reproducción). Como la cámara graba, se puede afirmar que **este vector no está roto**
en el estado actual.

### 4.3 El core AV y su imagen

* Imagen: `/system/av-cam.bin` (partición `nflasha3`, 11 427 236 B, cabecera `b 0x28` + `ORIL`),
  cargada por `im.elf` con `load=1 debug=1`.
* Base de ejecución `0x43541000` ([CORRECTIONS.md:765](../docs/CORRECTIONS.md)) y física
  `0x83541000`, **fuera** de la instantánea de arranque caliente
  ([WBI §1](film-pb-1-sub-wbi-20261127.md)) ⇒ se recarga en ambos modos.
* `RAMCFG` modo `0x4000000` (caliente) carga `idt_cam.bin` + `av-cam.bin`; `0x1000000` (frío) los seis
  (R14 §5, citado en [WBI §1](film-pb-1-sub-wbi-20261127.md)).
* Segunda imagen del ecosistema: `/system/sabin/{idt_cam.bin,sa_dfdet.bin,ssboot.bin,ssboot_any.bin}`
  (partición `nflasha3`) — sensor/`ssboot`, no el decodificador.

### 4.4 Microcódigo/tablas de `/usr/sabin`

Lo pide `av-cam.bin` (rutas absolutas) **desde el core AV**, así que el core AV necesita un servicio
de ficheros sobre el `/usr` de Linux. Consecuencia de auditoría: **el CFW no toca `/usr/sabin`**
(`build/cfw_func393/pp/files` solo tiene `lib/` y `share/`; `build/cfw_func393/pp/build-nflasha15.json`
lista exactamente 5 `.so` + 22 `string_*.uxc` + manifiestos, y la base es la partición **Sony 3.21**
byte a byte). ⇒ «falta el microcódigo» **no** es el mecanismo del fallo, salvo corrupción de flash.

---

## 5. Qué se vería si el decodificador estuviera caído — y por qué no es lo que se ve

### 5.1 Tabla síntoma → mecanismo

| Síntoma | Decodificador H.264 caído | Lector de MP4 / metadatos roto | Core AV o DSP caído |
|---|---|---|---|
| Grabar | **sí** (otro microcódigo, `ZM_AVCEP`, y otro bloque) | sí | **no** |
| Reproducir un clip | error **después** de `PbStart` (`0x307F54`): `"Decoder Error"`, `CodecErrAdapter`, o timeout de `"Decode Ready"`; pantalla negra sin avanzar | error **antes** de `PbStart`, en las guardas `0x437BFA`/`0x437C2C` → `0x1A` y aviso «No se puede visualizar.» | nada funciona |
| Miniatura de clip | negra/ausente solo en el camino B (movie decoder); las miniaturas JPEG (camino A) salen | **ausente** (el lector no encuentra o no sabe leer la miniatura) | ausente también en fotos |
| Miniatura de foto | sale | sale | ausente |
| Duración en la rejilla | correcta (metadatos intactos) | **mal** (p. ej. `0:02` para un clip de 9,5095 s) | correcta |
| Live view / menús | correctos | correctos | rotos |

### 5.2 El `0x1A` está aguas arriba del decodificador: prueba de código

En el manejador `0x437BC0` (opcode `0x4000001D` = `PlayMovie`) hay **exactamente dos** sitios que
producen `0x1A`, y los dos son guardas de metadatos:

```
00437bee ldr.w r0,[r4,#0x1ec] ; ldr.w r1,[r4,#0xdc0] ; ldr.w r2,[r4,#0xdb8]
00437bfa bl    0x447A1E            ; guarda A (estado/GetInhInfo: TvSystem del clip vs cámara)
00437bfe cbnz  r0,#0x437C10
00437c04 ldr   r1,=0085a51c " Pb Disable!! ref) dsm get"
00437c0a movs  r3,#0x1A            ; ← primer productor
…
00437c2c bl    0x447F26            ; guarda B = AviMMgr::isSupportContent (0x61A8F0)
00437c30 cbnz  r0,#0x437C70
00437c36 ldr   r1,=0085a7d8 " Detect UnSupported Content "
00437c3c movs  r3,#0x1A            ; ← segundo productor
…
00437cf6 bl    0x307F54            ; MoviePlayerIf::PbStart  ← aquí se arranca el decodificador
```

(líneas 22-28, 38-44 y 108 del desensamblado de `0x437BC0`+`0x340`; el volcado está en
[`10-guardab-issupportcontent.txt`](evidence/film-pb-1-sub-decodificador-20261128/10-guardab-issupportcontent.txt)).
**`PbStart` es posterior a las dos guardas**: si el decodificador estuviera caído, el flujo habría
pasado ya por las guardas y el código de error no sería `0x1A` sino el que devuelva la reproducción.

### 5.3 `AviMMgr::isSupportContent` (0x61A8F0): qué consulta y cuándo devuelve 0

Llamadas de la función (todas resueltas sobre el `.text` real):

| VA | Papel | ¿Toca el decodificador? |
|---|---|---|
| `0x3F9C7C` | «GetCondition» (nombre **deducido** del log `"Can't get condition"`); `0` = éxito | no |
| `0x61A764` | lee la propiedad **`0xC4`** (4 B) = flags del contenido; bit 2 (`0x4`) decide si hay que seguir comprobando | no |
| `0x677FB0` | segunda consulta (`this+0x770`); exige que `out[0x1c8]==4` para continuar | no |
| `0x6E8430` | `GetPlayThumbnailInfo` (§3.2) | no |
| `0x1EEFDC` | `GetTvSystem` (`1`=PAL, `!=1`=NTSC) | no |
| `0x65062C` | log con cadena | no |

**Solo dos caminos devuelven 0** (inservible ⇒ `0x1A`):

1. `0x61AA46` — desajuste **cadencia ↔ TvSystem**:
   PAL (`TvSystem==1`) y `(1<<fps) & 0x2A8` → `"Invalid TvSystem detect"`;
   NTSC (`TvSystem!=1`) y `(1<<fps) & 0x154` → `"Invalid TvSystem detect"`.
   `0x2A8` = bits 3/5/7/9 = 29.97/59.94/119.88/239.76; `0x154` = bits 2/4/6/8 = 25/50/100/200;
   `0x003` = 23.976/24 (válidas en ambos).
2. `0x61AA68` — **fallo de `GetPlayThumbnailInfo`** (`0x6E8430 != 0`).

Ni una sola instrucción de esta función toca `STM`, `DMM`, `BBControl`, `MovieDecoderIf` ni los
nodos del §1. **La guarda que produce el `0x1A` no puede detectar un decodificador caído.**

### 5.4 Hipótesis que sobreviven al análisis

* **H-A (preferente): el lector del MP4 falla.** Explica a la vez el `0x1A` de la guarda B
  (`GetPlayThumbnailInfo`), la miniatura ausente (mismo lector / `Mp4ThumbnailReaderFilter`) y el
  `0:02` frente a 9,5095 s ya medido ([auditoría §3](film-pb-1-auditoria-cfw-20261127.md)). No
  requiere que el decodificador esté mal y encaja con «graba bien».
* **H-B: desajuste TvSystem/cadencia.** Explica el `0x1A` de la guarda A con clips 30000/1001
  (enum 3) si `TvSystem==1` (PAL). Discriminador: la miniatura y la duración seguirían bien.
  *Nota*: un clip **grabado por la propia cámara** también cae, lo que hace muy improbable un
  desajuste «de contenido ajeno», pero **no** descarta que el global `TvSystem` esté corrupto.
* **H-C: decodificador sin inicializar.** No explica el `0x1A` (§5.2), ni el `0:02`; solo explicaría
  la miniatura si el camino usado fuese el B. **Sólo tomaría cuerpo si la traza real viniera de
  `PbStart`** con `"Decoder Error"` o `"Decode Ready"` agotado.

### 5.5 Síntomas exactos de un decodificador caído (para reconocerlo si aparece)

1. **Nada se rompe antes de pulsar reproducir**: rejilla, live view, grabación y miniaturas JPEG
   normales.
2. Al entrar en reproducción, el mensaje llega **con retardo** (timeout de `Decode Ready`/
   `Decoder Error`) o la pantalla queda en negro sin contador; el código de error del aviso **no**
   es `0x1A` sino el que devuelva `MoviePlayerIf::PbStart`/`ObjPlayerCore::PlayMovieCmp`.
3. Los logs `[InfDecoder]…` y `EVENT : "Decoder Error" from MovieDecoder` aparecen **después** de
   `"RunParam : [ONLY_I]"`/`CMD_RUN`, no antes.
4. Las miniaturas **de foto** siguen saliendo (JPEG ≠ AVC) y las de clip solo fallarían si la rejilla
   usa el camino B.
5. Grabar sigue funcionando, también en 1080/50p o 1080/60p (el codificador es otro microcódigo).

---

## 6. Cómo verificarlo

### 6.1 Sin cámara (tarjeta SD + PC) — lo más barato

| Prueba | Comando / método | Qué decide |
|---|---|---|
| Duración real y fps del clip | `ffprobe -v error -show_entries format=duration:stream=r_frame_rate,codec_name -of default=nw=1 clip.MP4` | si el `moov` dice ≈9,51 s y 30000/1001 mientras la cámara dijo `0:02` ⇒ **H-A** (lector), no decodificador |
| ¿Miniatura almacenada? | `ffprobe -show_streams` (buscar 2.º vídeo/`mjpeg`) y `mp4dump`/`AtomicParsley clip.MP4 --test` para ver `udta`/`thmb`/track extra | si el fichero **sí** trae miniatura y la cámara no la pinta ⇒ camino A/JPEG o lector |
| Índice de la tarjeta | listar `PRIVATE/AVF_INFO/` (o `AVF_INFO/`) y comparar con un clip antiguo | si el clip no está indexado o el índice está a 0 ⇒ **H-A** |
| Microcódigo intacto | `sha256sum` de `/usr/sabin/sa_avcd_*.bin` del firmware 3.21 vs el del CFW instalado | descarta corrupción de flash (aquí ya coincide: ver [`07`](evidence/film-pb-1-sub-decodificador-20261128/07-sabin-microcodigo.txt)) |
| Clip de fábrica | reproducir el MP4 de ejemplo (`scenario/MPR_SCN_INSTALL_MAP_DEMOMOVIE.so` existe en `/usr/scenario`) | si el demo **también** falla ⇒ entorno/estado, no el clip |

### 6.2 Con la cámara (USB/MTP o WiFi), si aparece

1. **Discriminador nº 1 — miniaturas de foto**: entrar en la rejilla. Si las fotos muestran
   miniatura y los clips no ⇒ el core AV y el JPEG están vivos ⇒ apunta a lector de MP4 (H-A) o al
   camino B, **no** al transporte ni al DSP.
2. **Discriminador nº 2 — antigüedad del clip**: reproducir un clip grabado **antes** del CFW. Si
   también falla ⇒ es estado global, no el contenido nuevo (refuerza H-A/H-B y descarta «fichero
   corrupto al grabar»).
3. **Discriminador nº 3 — cadencia**: grabar 1080/50p con `TvSystem=PAL` (o 60p/24p) y reproducirlo.
   Si ese sí se reproduce ⇒ **H-B** (máscaras `0x2A8`/`0x154` de §5.3).
4. **Descarga del clip por MTP/WiFi + §6.1** ⇒ decide H-A sin desmontar nada.
5. **Traza**: si en algún momento hay consola/UART, las cadenas a buscar son
   `"isSupportContent : GetPlayThumbnailInfo"`, `"Detect UnSupported Content"`,
   `" Pb Disable!! ref) dsm get"`, `"Invalid TvSystem detect"`, `"RunParam : [ONLY_I]"`,
   `"EVENT : \"Decoder Error\" from MovieDecoder"`, `"[InfDecoder]…"`. La primera que salga dice
   exactamente qué rama se tomó (guarda A vs guarda B vs decodificador).

### 6.3 Lo que no se puede verificar sin cámara

El **modo** de ejecución real del decodificador (carga de `ZM_AVCDP` vs `ZM_AVCDC`, estado
`McAvcDecState*`), el valor de `TvSystem` en RAM y el contenido del `moov`. Ninguno de los emuladores
del repo modela el core AV: el [arnés de `libObj`](film-pb-1-sub-arnes-20261127.md) despacha
mensajes de MPR, no decodifica.

---

## 7. Límites (NO_VERIFICADO)

* **Cuál de los dos caminos de miniatura usa la rejilla** del A6000 para un MP4 propio (§3.1).
* **Si el camino `grm::bmp` + `/dev/ldec` de `libObj` es alcanzable**; las cadenas no tienen
  referencia literal y en este modelo no hay uso evidente (§1.3).
* **Qué proceso del lado Android** consume el resultado de la reproducción (no se ha encontrado
  enlace `libmpr` en `/system`; `im.elf` es el único consumidor probado de `libObj`).
* **`0x447A1E` y `0x447F26`**: se aceptan los nombres y la semántica de
  [los informes previos](film-pb-1-sub-guardaa-20261127.md) / [guardab](film-pb-1-sub-guardab-20261127.md);
  aquí solo se ha verificado **que son las dos únicas fuentes del `0x1A`** y que `0x61A8F0` es de
  metadatos.
* **`0x5BAD00` / `0x5BACB0`** (mutex de `GetPlayThumbnailInfo`) se han interpretado por su forma
  (toma/suelta con código de error `b0100002`); no se ha resuelto el símbolo.
* Que `/setting/DmmConfig.bin` exista en la cámara: se infiere de que graba; no se ha leído.

---

## 8. Reproducibilidad

```bash
cd firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev
# nodos de dispositivo
strings -a -n 3 nflasha7_unpacked_unpacked/kmod/devno.ko
# microcódigo DSP
ls -la nflasha15_unpacked_unpacked/sabin
for f in nflasha15_unpacked_unpacked/sabin/sa_*.bin; do
  printf '%-40s ' "$(basename $f)"; dd if=$f bs=1 skip=16 count=16 2>/dev/null | tr -d '\0'; echo; done
# arranque
strings -a -n 6 nflasha7_unpacked_unpacked/sbin/init | grep -E 'kmod|setting|/proc/udm'
# decodificador
strings -a -n 6 nflasha3_unpacked_unpacked/av-cam.bin | grep -E 'McAvcDec|AvcDecVideo|/usr/sabin/'
strings -a -n 5 nflasha15_unpacked_unpacked/bin/im.elf | grep -E 'libObj|av-cam|dlopen'
# guardas y GetPlayThumbnailInfo (Capstone 5 de .venv)
python3 /tmp/elfhelper.py nflasha15_unpacked_unpacked/lib/libmpr.so dis 0x437BC0 0x340
python3 /tmp/elfhelper.py nflasha15_unpacked_unpacked/lib/libmpr.so dis 0x61A8F0 0x190
python3 /tmp/elfhelper.py nflasha15_unpacked_unpacked/lib/libmpr.so dis 0x6E8430 0xA0
# símbolos de módulos (son .symtab, no .dynsym: usar readelf)
readelf -sW nflasha7_unpacked_unpacked/kmod/ldec.ko
readelf -sW nflasha7_unpacked_unpacked/kmod/lld.ko | grep -i ldec
```

## 9. Evidencia

| Fichero | Contenido |
|---|---|
| [`01-devnodes-devno-ko.txt`](evidence/film-pb-1-sub-decodificador-20261128/01-devnodes-devno-ko.txt) | tabla `udif_devnodes` completa (qué nodos existen y cuáles no) |
| [`02-dev-strings-por-fichero.txt`](evidence/film-pb-1-sub-decodificador-20261128/02-dev-strings-por-fichero.txt) | barrido `/dev/*` por binario y consumidor de cada nodo |
| [`03-ldec-ko.txt`](evidence/film-pb-1-sub-decodificador-20261128/03-ldec-ko.txt) | símbolos y ruta de compilación de `ldec.ko` |
| [`04-lld-ko-ldec.txt`](evidence/film-pb-1-sub-decodificador-20261128/04-lld-ko-ldec.txt) | `lld.ko`: quién consume el LDEC (NAND + ARM7) |
| [`05-init-arranque.txt`](evidence/film-pb-1-sub-decodificador-20261128/05-init-arranque.txt) | secuencia de `insmod`, montajes y ficheros de `/setting` |
| [`06-avcam-decodificador.txt`](evidence/film-pb-1-sub-decodificador-20261128/06-avcam-decodificador.txt) | `av-cam.bin`: clases del decodificador, estados y `sa_func_*` |
| [`07-sabin-microcodigo.txt`](evidence/film-pb-1-sub-decodificador-20261128/07-sabin-microcodigo.txt) | `/usr/sabin` completo con nombres internos y versiones |
| [`08-im-elf-proceso.txt`](evidence/film-pb-1-sub-decodificador-20261128/08-im-elf-proceso.txt) | `im.elf`/`bootin.elf`: `dlopen` de `libObj` y carga de `av-cam.bin` |
| [`09-dmm-config.txt`](evidence/film-pb-1-sub-decodificador-20261128/09-dmm-config.txt) | `dmm.ko`: params y ficheros `/setting/DmmConfig*` |
| [`10-guardab-issupportcontent.txt`](evidence/film-pb-1-sub-decodificador-20261128/10-guardab-issupportcontent.txt) | desensamblado de `0x61A8F0` + mapa de llamadas y máscaras |
| [`11-miniatura-vs-reproduccion.txt`](evidence/film-pb-1-sub-decodificador-20261128/11-miniatura-vs-reproduccion.txt) | cadenas de los dos caminos de miniatura y del canal `BBControl` |
| [`12-camino-linux-decoder.txt`](evidence/film-pb-1-sub-decodificador-20261128/12-camino-linux-decoder.txt) | `InfraMovieDecoder*`, `MovieDecoderIf`, `MDEC`, eventos |
| [`13-dev-ldec-dmac-detalle.txt`](evidence/film-pb-1-sub-decodificador-20261128/13-dev-ldec-dmac-detalle.txt) | vecindad de `/dev/ldec` (`grm::bmp`) y ausencia de referencias literales |
| [`14-init-tabla-montajes.txt`](evidence/film-pb-1-sub-decodificador-20261128/14-init-tabla-montajes.txt) | tabla de montajes de `init` (`nflasha2`=/setting, `nflasha3`=/system, `nflasha15`=/usr) |
