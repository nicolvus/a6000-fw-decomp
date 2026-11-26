# FILM-PB-1 / sub-BD-tarjeta — ¿puede la base de datos de imágenes explicar «sin miniatura + no reproduce» en todos los clips?

28-11-2026. Auditoría de la **BD de imágenes y de los metadatos de los clips** que hay en el repo, para decidir si el
fallo es de **contenido**. Sin cámara: todo lo que sigue es (a) inventario de lo que existe en el repo y (b) estático
sobre `libmpr.so` de fw 3.21. **Direcciones = VA del ELF** (`.../fw321/.../nflasha15_unpacked_unpacked/lib/libmpr.so`,
SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`); en `libmpr` REA/Ghidra = VA + `0x10000`.
Evidencia cruda: [`evidence/film-pb-1-sub-bd-tarjeta-20261128/`](evidence/film-pb-1-sub-bd-tarjeta-20261128/).

**Respuesta corta:** no. Una BD corrupta **no** puede producir ese par de síntomas en todos los clips, y en particular
**no** puede impedir la reproducción de un clip recién grabado. Lo único que en el código verificado produce *a la vez*
«sin miniatura» y «No se puede visualizar.» es el fallo de `mp4Ifo_If::GetPlayThumbnailInfo` (`0x6E8430`), que **no
depende del contenido del índice** sino del servicio `ifoFramework` y del filtro de decodificación de miniatura. Y la
razón por la que «Recuperar BD imág.» no lo arregla es que ese menú reconstruye el índice (`AVF_INFO\AVIN0001.INP`)
escaneando los MP4, pero **no** repara ni el semáforo de `ifoFramework` ni el decodificador.

---

## 1. Inventario: qué evidencias de tarjeta hay realmente en el repo

Búsqueda exhaustiva (comandos y salida completos en [inventario-repo.txt](evidence/film-pb-1-sub-bd-tarjeta-20261128/inventario-repo.txt)):

| Buscado | Resultado |
|---|---|
| `*AVF_INFO*`, `*MEDIAPRO*`, `*.THM`, `*.INP`, `*.MODD`, `*.AVIN` | **nada real**; solo `evidence/film-pb-1-sub-avin-20261127/AVIN0001_sintetico.INP` (sintético de 1 408 B) y los `MediaProvider.apk/.odex` de Android |
| directorios `DCIM`, `PRIVATE`, `MP_ROOT`, `AVCHD` | **ninguno** |
| ficheros `*.MP4` | **ninguno**; `MAH04198.MP4` está **fuera** del repo (`/home/nicolas/Documents/a6000/`) |
| `grep -rIl` de `AVIN0001\|PRV00001\|MEDIAPRO\|CUEUP.XML\|STATUS.BIN\|THMBNL\|100ANV01\|103ANV01` | 24 ficheros, **todos** informes/`docs/`/código; **cero** volcados |

Lo que **sí** existe como evidencia de tarjeta, y es de segunda mano pero útil:

1. **Lectura en vivo de la tarjeta el 25-11** ([traspaso §2](film-pb-1-traspaso-20261125.md):48-70), vía
   `/android/mnt/sdcard` (Telnet) y `/mnt/sdcard` (ADB):
   - `PRIVATE/M4ROOT/CLIP` → **vacío**; `PRIVATE/AVCHD/BDMV/STREAM` → **vacío**.
   - Siete MP4 en `MP_ROOT`: `100ANV01` = MAH04114/04115/04165/04167; `103ANV01` = MAH04191/04198/04199.
2. **ffprobe de los siete** ([clip-metadata-summary.json](evidence/film-pb-1-20261125/clip-metadata-summary.json),
   copia con hash en [fuente-clip-metadata-summary.json](evidence/film-pb-1-sub-bd-tarjeta-20261128/fuente-clip-metadata-summary.json)).
3. **ffprobe + árbol de atoms completo de MAH04198**
   ([provided-04198-ffprobe.json](evidence/film-pb-1-20261125/provided-04198-ffprobe.json),
   [mp4-tiempos-vibe.md](evidence/film-pb-1-20261125/mp4-tiempos-vibe.md)).

**NO_VERIFICADO y decisivo:** no hay copia de `AVF_INFO\`, ni de `MEDIAPRO.XML`, ni un `ls -laR` de la raíz de la
tarjeta. Por tanto **no se puede afirmar ni negar que la BD estuviera corrupta**: no hay un solo byte de ella. Lo que sí
se puede decidir —y es el objeto de este informe— es si una BD corrupta *podría* producir el cuadro observado.

---

## 2. `MEDIAPRO.XML`: no existe y **no aplica** a estos clips

No hay `MEDIAPRO.XML` en el repo. Y en el firmware se verifica que es un fichero **solo XAVC**:

- Las cadenas de ruta `\PRIVATE\M4ROOT\MEDIAPRO.XML` (`0x947CF2`), `MEDIAPRO.BAK` (`0x947D0F`), `CLIP` (`0x947C8A`),
  `THMBNL` (`0x947CC3`) y `SUB` (`0x947CDA`) tienen **un único** xref cada una, y todas caen en el **pool de literales
  `0x779FBC-0x779FD8`** del volcado de `xavcIfo_DbDirMngr` (que imprime ` DeviceType MS` y ` m_rootDirPath = ` en
  `0x779FA4-0x779FB4`). Ningún módulo MP4/AVI las toca
  ([libmpr-cadenas-miniatura-y-bd.txt](evidence/film-pb-1-sub-bd-tarjeta-20261128/libmpr-cadenas-miniatura-y-bd.txt) §E).
- `PRIVATE/M4ROOT/CLIP` estaba **vacío** en la lectura en vivo: aunque el A6000 usara `MEDIAPRO.XML`, no habría ni un
  registro de clip que aportar.

⇒ El contenido de `MEDIAPRO.XML` **no puede** ser la causa. Coincide con
[sub-tarjeta](film-pb-1-sub-tarjeta-20261127.md) §1 y **corrige** el peso que le daba
[sub-catálogo](film-pb-1-sub-catalogo-20261127.md) §4 («la BD de imágenes gobierna la reproducción»): gobierna la
*enumeración*, y solo para XAVC lo hace por XML.

## 2-bis. Coherencia de los metadatos de los siete clips con el MP4 real

Recalculado desde los ffprobe ([tabla completa](evidence/film-pb-1-sub-bd-tarjeta-20261128/metadatos-7-clips-coherencia.txt)):

| clip | dur. declarada | frames | `nf*1001/30000` | Δ | fps | resolución |
|---|---:|---:|---:|---:|---|---|
| MAH04114 | 72,5725 | 2175 | 72,5725 | 0,000000 | 30000/1001 | 1440×1080 |
| MAH04115 | 34,5345 | 1035 | 34,5345 | 0,000000 | 30000/1001 | 1440×1080 |
| MAH04165 | 24,5245 | 735 | 24,5245 | 0,000000 | 30000/1001 | 1440×1080 |
| MAH04167 | 31,5315 | 945 | 31,5315 | 0,000000 | 30000/1001 | 1440×1080 |
| MAH04191 | 52,5525 | 1575 | 52,5525 | 0,000000 | 30000/1001 | 1440×1080 |
| **MAH04198** | **9,5095** | **285** | **9,5095** | 0,000000 | 30000/1001 | 1440×1080 |
| MAH04199 | 5,0050 | 150 | 5,0050 | 0,000000 | 30000/1001 | 1440×1080 |

Los siete son idénticos en formato (H.264 Main@L4.0 + AAC-LC 48 kHz estéreo, 1440×1080 SAR 4:3 → DAR 16:9,
progresivo, `MSNV`) y su duración declarada coincide **al microsegundo** con `cuadros × 1001/30000`. El audio también
cuadra (`nf*1024/48000`). Ningún contenedor guarda una duración parecida a 2 s (el «0:02» del OSD no sale de ningún
campo del MP4: ya descartado en [mp4-tiempos](evidence/film-pb-1-20261125/mp4-tiempos-vibe.md) §4).

**Hallazgo nuevo y útil:** el OSD de la cámara para MAH04198 era `1-1-2014 · 11/87 · 30p · 1080 · MP4 · 0:02`
([traspaso:35](film-pb-1-traspaso-20261125.md):35). Cuatro de esos seis datos **coinciden exactamente con el fichero**:
`creation_time = 2014-01-01T05:02:01Z` → «1-1-2014»; `r_frame_rate = 30000/1001` → «30p»; altura 1080 → «1080»;
`major_brand = MSNV` → «MP4». Es decir: la cámara está leyendo y publicando metadatos **del MP4**, y lo hace bien.
Solo fallan la duración («0:02») y el recuento («11/87», que no tiene contrapartida en el fichero y por tanto es un
contador del índice).

---

## 3. Qué necesita la cámara para (a) la miniatura y (b) reproducir

### (a) Miniatura de un clip MP4 — **no hay `.THM` para MP4**

- `.THM` **no se usa** en la ruta MP4. La cadena `.THM` (`0x7EF829`) y las de traza ` .THM: ` (`0x9428DA`) /
  ` .THM path: ` (`0x9436B4`) solo se referencian desde el **gestor XAVC** (`0x763C98`, `0x7645DC`, `0x767EA8`,
  `0x7685D8`, todos en la región `xavcIfo` `0x76xxxx`). Ver §D de
  [libmpr-cadenas-miniatura-y-bd.txt](evidence/film-pb-1-sub-bd-tarjeta-20261128/libmpr-cadenas-miniatura-y-bd.txt).
  Coherente con la lectura en vivo: ni `PRIVATE/AVCHD/BDMV/STREAM` ni `PRIVATE/AVCHD/BDMV/THUMBNAIL` tienen contenido.
- La miniatura de película la produce un **filtro lector + decodificador**, por tipo de medio:
  `Mp4ThumbnailReaderFilter` (`0x87742C`, `new` en `0x80623E`, `delete` en `0x805303`), con
  `SetCmdReadyThumbnailReaderFilter() mp_mp4ThumbnailReaderFilter->SetReadTarget` (`0x805F1F`) y
  `ThumbnailReaderFilter->ConnectDecordStillInfoOutputPlug()` (`0x8058C9`). Clase base
  `BaseThumbnailReaderFilter` (`0x8769D0`).
- La BD **solo aporta una copia cacheada**, y el firmware distingue explícitamente de dónde vino la miniatura:
  `THUMBNAIL_TYPE_AVINDEX` (`0x7C070B`), `THUMBNAIL_TYPE_ORIG_CONTENT` (`0x7C0740`),
  `THUMBNAIL_TYPE_INCONSISTENT` (`0x7C077A`), `THUMBNAIL_TYPE_NOTHING` (`0x7C07B4`), en la tabla de punteros
  `0x21FACC-0x21FAD8`, indexada con `cmp r3,#3` + `tbb [pc,r3]` (`0x21FAAA-0x21FAAE`); y el despachador lo registra:
  `GetPlayThumbnailInfo Type : NORMAL / ORIG_CONTENT / INCONSISTENT / NOTHING` (`0x876F59`, `0x876F7C`, `0x876FA5`,
  `0x876FCE`).
- El índice AV guarda además el **sello de tiempo del fichero de imagen de la miniatura**:
  `thumbPictFileModTime: [%4d] %04d.%02d.%02d %02d:%02d:%02d` (`0x7CB98E`, `0x7CC82E`), `thumPictFileName` (`0x7A9C74`),
  `Thumbnail Slot Num` (`0x7AB174`), `Thumbnail Size` (`0x7AB2D3`), `avi_sdk_ReadThumbPictFile Start/End`
  (`0x7AA295`/`0x7AA2B5`), y se vuelca con `FLUSH_FILE_THUMB` (`0x7B1723`, enumerado en `0x7ADFC4`).

**Conclusión (a):** para ver la miniatura de un MP4 la cámara necesita **una entrada en el índice AV** (para resolver
`EntryId` → contenido) **más** la miniatura: o la copia cacheada del índice, o —si no la hay— **decodificarla del MP4**
(`ORIG_CONTENT`). **Nunca un `.THM`.** Si el índice no tiene la copia, el camino de decodificación sigue existiendo; si
la decodificación está caída, no hay miniatura para ningún clip.

### (b) Reproducción — la guarda B puede rechazar por **dos** motivos, y la miniatura es el primero

`AviMMgr::isSupportContent` = slot `+0x58` de la vtable `0x8E6E58` = **`0x61A8F0`**. Desensamblado propio
([libmpr-desasm-miniatura-y-guardab.txt](evidence/film-pb-1-sub-bd-tarjeta-20261128/libmpr-desasm-miniatura-y-guardab.txt)):

```
0061a92c: bl 0x3F9C7C        ; GetContentCondition(owner,cc0,cc1,EntryId,&out)
0061a930: cbnz r0, 0x61A938  ; sin condicion  -> "Can't get condition" -> 0x61AA18 -> 0x61AA6C  RET 1  (SOPORTADO)
0061a932: ldrb r3,[r7,#0x1CF]; cbz -> idem
0061a950: bl 0x61A764        ; err -> RET 1
0061a962: ldr r3,[r7,#0x13C] ; tst r3,#4 ; beq 0x61AA6C  RET 1
0061a980: bl 0x677FB0        ; ConvEntryIdPreToPost
0061a984: mov r6,r0 ; cmp r0,#0 ; bne 0x61AA6C  RET 1
0061a98a: ldr r3,[r7,#0x1C8]; cmp r3,#4 ; bne 0x61AA6C  RET 1
0061a9e2: movs r3,#0x1F
0061a9e4: bl 0x6E8430        ; <<< GetPlayThumbnailInfo(..., sel=0x1F, &info)
0061a9ea: cmp r0,#0 ; bne 0x61AA5C
0061aa5c: ... log "isSupportContent : GetPlayThumbnailInfo " (0x8E53DC)
0061aa68: mov r0,r6          ; r6 == 0 aqui (0x61A984 lo dejo a 0 y 0x61A988 lo garantiza)  => RET 0  (NO SOPORTADO)
0061a9ee: bl 0x1EEFDC        ; TvSystem = *(u32*)0x28F850
0061a9f2: ldr.w r3,[r7,#0x124]  ; f = codigo frameRate del contenido
0061a9f6: cmp r0,#1 ; bne 0x61AA1E
0061aa00: tst.w r0,#0x2A8 ; bne 0x61AA3A -> 0x61AA46  RET 0   ; TvSystem==1 y f in {3,5,7,9}
0061aa06: tst.w r0,#0x154 ; bne 0x61AA4A             RET 1   ; TvSystem==1 y f in {2,4,6,8}
0061aa0c: tst.w r0,#3     ; bne 0x61AA12             RET 1   ; f in {0,1} = 24p/23.976p
0061aa6c: movs r0,#1                                    RET 1 ; todo lo demas
```

Dos hechos, ambos **VERIFICADOS en bytes**, que cambian el diagnóstico vigente:

1. **La miniatura se comprueba ANTES que la cadencia** (`0x61A9E4` precede a `0x61A9EE`). Si
   `GetPlayThumbnailInfo` falla, la guarda devuelve 0 **sin llegar a mirar `TvSystem`**. Es decir: la hipótesis
   «`TvSystem` PAL frente a clips 29,97» ([causa TV](film-pb-1-causa-sistema-tv-20261127.md),
   [diagnóstico cerrado](film-pb-1-diagnostico-cerrado-20261127.md)) **no predice la falta de miniatura**: con la
   cadencia como única causa las miniaturas se verían. El síntoma nuevo **enmascara** ese camino.
2. **Un índice ausente o ilegible NO bloquea: deja pasar (fail-open).** Las salidas de «Can't get condition»
   (`0x61A938`), del `ValidFlag` a cero (`0x61A932`), del bit de inhibición (`0x61A962`) y de
   `ConvEntryIdPreToPost` (`0x61A988`) van todas a **`0x61AA6C` = `movs r0,#1`**. Es decir: **si el registro del clip
   no está en la BD, la cámara intenta reproducirlo**. Corrupción que borra registros ⇒ no es causa de «No se puede
   visualizar».

**Los únicos dos `return 0` de la guarda son `0x61AA46` (cadencia) y `0x61AA68` (miniatura).**

### De dónde sale el fallo de miniatura: `0x6E8430`

```
006e8446-0x6e8450: log START (mp4Ifo_If.cpp:0x1a9, "GetPlayThumbnailInfo")
006e8454: ldr r0,[r4,#4] ; movs r1,#0x23 ; movs r2,#1
006e845a: bl 0x5BAD00        ; semaforo de ifoFramework, recurso 0x23
006e845e: cbz r0, 0x6E8470   ; si 0, sigue al mp4Ifo real
006e8460-0x6e8468: log(mp4Ifo_If.cpp, 0x1af, 0xB0100002)
006e846c: ldr r5,[pc] = 0xB0100002 ; 006e846e: b fin   =>  **devuelve 0xB0100002 SIN abrir el MP4**
006e8470: ... 006e849c: ldr r5,[r2,#0x18] ; 006e84a0: blx r5   (vtable de mp4Ifo + 0x18)
```

y `0x5BAD00` es `ifoFramework_Semaphore.cpp` (`0x8BBB14`), que registra `0xCA001001` (literal en `0x5BADF0`) y
aborta si el byte de inicialización `[this+4]` vale 0 (`0x5BAD18-0x5BAD26`). **Consecuencia:** hay un punto de fallo único, anterior a cualquier lectura del MP4, que produce
exactamente el par de síntomas:

> `GetPlayThumbnailInfo` → `0xB0100002` → `isSupportContent` = 0 → `0x437C3C` «Detect UnSupported Content» → `0x1A`
> → DefObjPlayer 7 → caution `0x135` → «No se puede visualizar.» **y** ninguna miniatura (ni cacheada ni decodificada).

Ese punto **no depende del contenido del clip**, no depende de la cadencia y es **global por arranque** (el semáforo y
el filtro son del proceso, no del fichero). Es el único sitio verificado que explica el cuadro completo.

---

## 4. ¿Está en las evidencias el clip grabado por la propia cámara?

Sí, pero **sin poder etiquetarlo como tal**. Lo que hay:

- **MAH04198.MP4** es el clip que el usuario identificó en pantalla. Está en `MP_ROOT/103ANV01`
  ([traspaso:52-60](film-pb-1-traspaso-20261125.md):52-60), 14 545 696 B, SHA-256
  `148c204c…7bda6` (calculado **fuera** del repo; el del fichero de la tarjeta **no** se hasheó).
- **Metadatos: íntegros.** Árbol de 44 atoms completo, `moov` al final tras `mdat`, `mvhd`/`tkhd`/`mdhd`/`elst`/`stts`/
  `ctts`/`stss` coherentes entre sí (285 muestras × 1001 ticks = 285 285 = 9,5095 s), `stco`/`stsz` con 19 chunks y
  285 tamaños, 10 keyframes. `ffmpeg -f null` decodifica **entero sin errores** (rc 0, log vacío —
  `provided-04198-decode.txt` son 0 B). Es decir: **el contenido no está dañado**.
- **Estado en la cámara:** aparece (se ve fecha, `30p`, `1080`, `MP4`), con la duración equivocada (`0:02`) y
  **sin miniatura**; al reproducir, «No se puede visualizar.».

**NO_VERIFICADO:** cuál de los siete es el «recién grabado». Los números van de 04114 a 04199 y no hay `mtime` de la
tarjeta ni fecha por clip (solo se midió `creation_time` de MAH04198). Si el clip de la prueba es MAH04199 (el que se
descargó completo al principio) o MAH04198, es indistinguible con lo que hay.

Lo relevante para el veredicto **no depende de identificarlo**: los siete son metadatos idénticos (§2-bis), así que
cualquiera de ellos vale como muestra «grabada por esta cámara con este firmware» y **los siete fallan**.

---

## 5. Veredicto

### 5.1 ¿Puede una BD corrupta producir «sin miniatura + no reproduce» en TODOS los clips, incluido el recién grabado?

**No.** Cuatro razones, en orden de fuerza:

1. **Un registro ausente o inválido deja pasar la reproducción** (§3: `0x61AA6C RET 1` por cuatro caminos distintos).
   Para bloquear, el registro tiene que **existir y resolver**, y aun así `GetPlayThumbnailInfo` tiene que fallar.
   Es una conjunción muy estrecha, no lo que produce una BD «corrupta».
2. **Un clip recién grabado escribe su propio registro.** El índice lo mantiene el módulo de grabación
   (`sources/avi_if/AviSeqRec.cpp`, presente en el binario) y `AVF_INFO\AVIN0001.INP` es el primario con `.BNP` de
   respaldo y `.INT` interno (`0x7A912C`/`0x7A9139`/`0x7A9160`, descriptor `0x9D1270`, volcado en
   [sub-AVIN](film-pb-1-sub-avin-20261127.md) §1). Que falle *también* el recién grabado exige que el fallo sea
   posterior al registro, o común a todos.
3. **La miniatura tiene camino de respaldo sin BD:** `THUMBNAIL_TYPE_ORIG_CONTENT` (`0x7C0740`) y
   `Mp4ThumbnailReaderFilter`. Una copia cacheada ausente da miniatura distinta o genérica, **no** ausencia total en
   los siete.
4. **Los datos que la cámara sí publica salen del MP4 y son correctos** (§2-bis): fecha, `30p`, `1080`, `MP4` coinciden
   con `mvhd`/SPS. Una BD que gobierna la reproducción pero produce un catálogo correcto y un `EntryId` que falla en la
   miniatura no es «corrupción»: es un subsistema de miniatura caído.

**Y hay una prueba de una línea que lo cierra:** los ficheros `.THM`/`MEDIAPRO.XML` **no participan** en esta ruta
(§2 y §3a), y `PRIVATE/M4ROOT/CLIP` y `PRIVATE/AVCHD/BDMV/STREAM` estaban **vacíos**. No hay ninguna fuente de
contenido alternativa que pueda estar corrupta.

### 5.2 ¿Por qué «Recuperar BD imág.» no lo arreglaría?

Porque reconstruye el **índice**, no el **servicio**:

- El menú está en `string_spanish.uxc` (id `0xE3D0`, ayuda `0xE43A`: «Recupera el archivo de base de datos de
  imágenes para películas y habilita la grabación y la reproducción.») y su cadena de firmware es
  `BeginRepair <AVINDEX/AVCHD_NEW/…>` (`0x9002BA`) → `CreateAVIndexFile` (`0x7A7E7C`) /
  `RunInconsistencyAvcMp4Register` (`0x7ADB04`). Es decir: **recorre `MP_ROOT\*` y reescribe `AVF_INFO\AVIN0001.INP`**
  (INFERIDO en cuanto al detalle, ver [sub-tarjeta](film-pb-1-sub-tarjeta-20261127.md) §4 R1).
- El fallo que explica los dos síntomas está **antes**, en `0x6E845A`/`0x6E846C` (`ifoFramework`, `0xB0100002`) o en
  el `Mp4ThumbnailReaderFilter`/decodificador. El índice regenerado tendría un hueco de miniatura que **tampoco** se
  podría rellenar, y `isSupportContent` seguiría devolviendo 0 en `0x61AA68`.
- La recuperación además solo actúa sobre lo que el escaneo encuentra: si el índice ya está bien (y §2-bis sugiere que
  el registro está, porque publica datos correctos), no hay nada que recuperar y el resultado es «no cambia nada», que
  es exactamente lo observado.

---

## 6. Qué falta: ficheros exactos que hay que copiar de la tarjeta

Para cerrar la auditoría de contenido (y descartar o confirmar la BD con bytes) hace falta, en este orden:

1. **`AVF_INFO\` completo**, copiado con `cp -a` (preservando tamaño y `mtime`): `AVIN0001.INP`, `AVIN0001.BNP`,
   `AVIN0001.INT`, `PRV00001.BIN`, `OTDISCBN.IND`, `MODELCFG.IND` — o el listado `ls -la` de la carpeta si no se
   puede copiar. Con el lector ya escrito (`evidence/film-pb-1-sub-avin-20261127/leer_avin.py`) se leería
   `nDuration` (`+0x30`), `Duration90kHz` (`+0x34`) y el byte de validez (`+0x24`) de cada clip sin tocar la cámara.
   **Esto resuelve el «0:02» y el «11/87» de una vez.**
2. **`ls -laR` de la raíz de la tarjeta** (`DCIM`, `MP_ROOT`, `PRIVATE`, `AVF_INFO`) con fechas y tamaños. Es lo único
   que permite saber cuántos contenidos hay (los 87 del contador) y si **las fotos JPG muestran miniatura**.
3. **`PRIVATE\M4ROOT\`** entero (aunque `CLIP` esté vacío): si existiera `MEDIAPRO.XML`/`.BAK`, `CUEUP.XML`,
   `STATUS.BIN`, `DISCMETA.XML`. Hoy es **NO_VERIFICADO** que no existan: la lectura en vivo solo dice que `CLIP` y
   `AVCHD/BDMV/STREAM` estaban vacíos.
4. **Los siete MP4** (o al menos sus `moov` completos) con `sha256sum`, para tener hash de tarjeta y no solo del
   fichero suelto de `~/Documents/a6000/`.
5. **Nombre, tamaño y `sha256` del clip recién grabado** en el momento de la prueba, y **una foto de la pantalla de
   índice de reproducción** (para ver si hay icono de miniatura, marcador de miniatura ausente o nada).

**Pruebas de una línea que separan las hipótesis sin copiar nada** (y que no requieren desmontar el CFW):

| Prueba | Si el resultado es… | Conclusión |
|---|---|---|
| ¿Las **fotos JPG** de la tarjeta muestran miniatura en el índice? | **Sí** | El índice y el `DcfThumbnailReaderFilter` funcionan ⇒ el fallo es de `Mp4ThumbnailReaderFilter`/decodificador ⇒ **BD descartada**. |
| | **No** (tampoco las fotos) | Fallo global de miniaturas/decodificador ⇒ **BD descartada** también. |
| Copiar **un solo** MP4 a una tarjeta **formateada por la cámara** | **Sigue fallando** | El índice es irrelevante ⇒ **BD descartada**. |
| | **Funciona** | BD o estructura de tarjeta implicadas ⇒ volver a §6.1. |
| Tras «Recuperar BD imág.», ¿cambia el tamaño/`mtime` de `AVIN0001.INP`? | **No cambia** | El menú no llegó a actuar (caution `0xE40F`/`0xE414`) ⇒ el experimento no prueba nada sobre la BD. |

Y si al restaurar las miniaturas sigue fallando, **entonces sí** entra la cadencia: `0x61AA46` con los siete clips en
enum 3 (29,97) y `TvSystem == 1`; el ensayo ya preparado (`scripts/mp4_set_framerate.py`, clip a 25p en
`~/Documents/a6000/prueba-MAH04198-25p.mp4` → `MP_ROOT/103ANV01/MAH04200.MP4`) es el discriminante.

---

## 7. Límites y correcciones

- **Corrige** [sub-catálogo](film-pb-1-sub-catalogo-20261127.md) §4: `AVF_INFO` sí es una ruta sondeada, no solo una
  etiqueta de volcado. La cadena `AVF_INFO` (`0x7A637F`) tiene **9 xrefs** (`0x12C6A4`, `0x139494`, **`0x13C0F0`**,
  `0x14494C`, `0x1449D4`, `0x144AB4`, `0x14B980`, `0x14BBE0`, `0x14BCDC`) y junto a ella se llama al import
  `MprFileIf::FindFirst` (`blx 0x11EA84` en **`0x13E496`**). El `0x2109` medido en el arnés
  ([g22 §5.51](../docs/gui/g22-avcam-puente.md):561) es consistente. Queda como **NO_VERIFICADO en cámara real**.
- **Corrige** el peso de la hipótesis de cadencia: `isSupportContent` mira la miniatura **antes** que `TvSystem`
  (§3b), así que la falta de miniatura **enmascara** el rechazo por cadencia. Ambas siguen siendo ciertas por
  separado; lo que no se sostiene es que la cadencia explique el síntoma nuevo.
- **NO_VERIFICADO:** la unidad y el contenido real de `dur` de `MEDIAPRO.XML`; el nombre del fichero de miniatura del
  índice (`thumPictFileName` no aparece como literal de ruta en `libmpr`, `libObj` ni `libmprctrl` — los tres
  registrados en `libmpr` únicamente); si el índice cachea miniaturas de MP4 en la práctica; qué clase implementa
  `[this]` en `0x6E8470` (se sabe que es `mp4Ifo` por la vtable `+0x18`, no el typeinfo); si la rejilla de índice usa
  el mismo `0x6E8430` que la guarda (si usara otro camino, el acoplamiento sería **INFERIDO**, no verificado).
- Nada de esto se ha medido en la cámara: la cámara no es accesible. No se ha escrito fuera de `reports/`. No se ha
  tocado `docs/`, `knowledge/`, `build/`, `scripts/` ni los informes previos; no se ha ejecutado el reindexador.
