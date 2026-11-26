# FILM-PB-1 — De dónde sale el `frameRate` de la guarda y si el `mdhd` reescrito lo cambia

27-11-2026 · cámara **no accesible** · **estático + emulación Unicorn** sobre la libmpr real (fw 3.21,
`…/nflasha15_unpacked_unpacked/lib/libmpr.so`; SHA-256 y desensamblados en [evidencia](evidence/film-pb-1-sub-framerate-20261127/)). VA = VA del ELF (REA = VA+0x10000). **V** verificado (instrucciones/bytes/emulación) · **D** deducido · **NV** no verificado.

## 1. `[r7+0x124]` **no** es un argumento: es un campo del struct de `GetPlayThumbnailInfo` (V)

`0x61A8F0` recibe **3** palabras (`0x61A908 stm.w r8,{r1,r2,r3}`, `r8=r7+0x1F4`); la cadencia entra por un **8.º `out` construido en su propio frame**:

```
0x61A9BE  str   r3,[sp,#0x04]    ; out r7+0x1C0 (también 0x1AC/0x1B4/0x1B8/0x1BC)
0x61A9DE  adds  r3, r7, #0       ; r3 = r7+0 → struct grande
0x61A9E0  str   r3,[sp,#0x1C]    ; 8.º out ; 0x61A9E2 movs r3,#0x1F (selector)
0x61A9E4  bl    0x6E8430         ; mp4Ifo_If::GetPlayThumbnailInfo (mp4Ifo_If.cpp:0x1A9)
0x61A9EE  bl    0x1EEFDC         ; TvSystem()
0x61A9F2  ldr.w r3,[r7,#0x124]   ; ← campo del struct de 0x13C B, no argumento
```

El struct ocupa `r7+0x000..0x13C`; detrás empieza el buffer de «condición» de **0xC4 B** de `0x3F9C7C`/`0x61A764` (`r6=r7+0x13C` en `0x61A904`; `movs r1,#0xC4` en `0x61A948`). Los demás `out` (`0x174/0x194/0x1AC/0x1B4/0x1B8/0x1BC/0x1C0/0x1C4`) quedan fuera ⇒ el mensaje de 0x8C B de la orden `0x4000001D` **no** lleva la cadencia: se pide al contenido.

## 2. El enum 0..9 equivale a (V, dos tablas independientes)

`0x686A34` (volcado `0x6869A2`, rótulo `0x686988` «ProfileInfo->frameRate»): `FPS_23_976, FPS_24, FPS_25, FPS_29_97, FPS_50, FPS_59_94, FPS_100, FPS_119_88, FPS_200, FPS_239_76, FPS_UNKNOWN`; `0x77AF2C tbb [pc,r2]` empareja cada índice con `1001/1000` y `24/25/30/50/60/100/120/200/240` ([tablas-enum.txt](evidence/film-pb-1-sub-framerate-20261127/tablas-enum.txt)) ⇒ **0**=24000/1001 · **1**=24 · **2**=25 · **3**=30000/1001 · **4**=50 · **5**=60000/1001 · **6**=100 · **7**=120000/1001 · **8**=200 · **9**=240000/1001. La capa AVI nombra el mismo enum con el racional (V): `FRAME_RATE_24000_1001 … FRAME_RATE_240000_1001` (`0x7AFCC9`–`0x7AFDD5`, volcado `0x7AFCA5`) ⇒ la cadencia viaja como (num,den).

## 3. Cadena de producción (V; [desensamblado-cadena.txt](evidence/film-pb-1-sub-framerate-20261127/desensamblado-cadena.txt))

`0x61A8F0` → `0x6E8430` → virtual `+0x18` → `mp4Ifo_AVISequence::GetPlayThumbnailInfo 0x6E0AB8` → `0x1D7022` → `0x21F1F4` (`CS_FlashAcsr`, `r3=4`), que llena un struct de **0x110 B** en `r7+0x08`; su `+0x100` (**1..10**) se convierte y acaba en el struct de 0x13C:

```
0x6E0CD6 ldr.w r3,[r7,#0x100]   ; 1..10 ; 0x6E0CDC cmp #0xA / bhi error
0x6E0CE0 tbb   [pc,r3]          ; idx 1..10 → 0,1,2,3,4,5,6,7,8,9  (idx 11 → 0xFF)
0x6E0D1A str.w r3,[r4,#0x124]   ; ← lo que lee la guarda
```

Segundo productor del **mismo** struct: `0x77B020 str.w r2,[r4,#0x124]` en `0x77ABEC`, desde un perfil de
0x4D8 B que copia la cadencia de `[r5+0x94]` (`0x77AD06`–`0x77AD0A`) junto a `+0x84` (W/H), `+0x8C` (códec
audio), `+0x98` (entrelazado) y `+0xA0` (nº de cuadros).

## 4. Qué campo del MP4 acaba ahí

- **V (descartan cajas propietarias e índice):** `PROF` no lleva cadencia —`FPRF` son 12 B a cero y `VPRF`
  44 B = `'avc1'`, `0x014D0028`, `0x00020002`, `12000`, `16000`, `0x001DF853` ×2, `1440×1080`, `4`, `3`—;
  `stsd/avc1` solo da 1440×1080 (`05 A0 04 38`) y «AVC Coding»; el registro de 0x80 B de `AVF_INFO\AVIN0001.INP` ([informe](film-pb-1-sub-avin-20261127.md)) trae tamaño, W×H, duración, códec y perfil, **sin** cadencia; y `0x61A8F0` no hace E/S.
- **D:** el único racional por clip del contenedor es `mdhd.timescale / stts.delta`, justo la forma del nombre
  del enum (`FRAME_RATE_30000_1001`); `mvhd`/`elst` van en escala de película (90000) y no dan cadencia sin el nº de muestras.
- **NV:** el último salto, `0x21F1F4` (`0x1327AE`/`0x1EF4FC`) → lectura del `moov` (§8). Por eso **no** se firma
  que salga de `mdhd`; sí que **no** sale de ninguna caja `uuid` ni del índice.

## 5. Emulación (libmpr real; `emu_framerate.py` y [emu-transcripcion.txt](evidence/film-pb-1-sub-framerate-20261127/emu-transcripcion.txt))

Dos fragmentos del `.text` cargado tal cual; solo se saltan las llamadas de log (`0x65062C`).

```
== A) guarda 0x61A9F2-0x61AA6E   (r0=TvSystem, [r7+0x124]=frameRate)
   TvSys | fr: 0 1 2 3 4 5 6 7 8 9 | >9        V = devuelve 1, X = devuelve 0
     0   |     V V X V X V X V X V | V   «Unknown frameRate %d»
     1   |     V V V X V X V X V X | V
     2   |     V V X V X V X V X V | V
== B) conversión 0x6E0CD6-0x6E0D1E :  entrada 1..10 → 0..9 ; entrada 11 → 0xFF
```

Corrige dos puntos de [causa-sistema-tv](film-pb-1-causa-sistema-tv-20261127.md): con `TvSystem==1` pasan 24p y los pares 2,4,6,8 = 25/50/100/200 ⇒ `TvSystem==1` es **PAL** (D); y `frameRate>9` **devuelve 1** (`0x61AA52`→`0x61AA18`→`0x61AA1C`→`0x61AA6C movs r0,#1`), no 0. Con la cadencia real del clip (**3**) la guarda acepta en NTSC y rechaza en PAL.

## 6. Los dos ficheros, medidos ([diff-y-candidatos.txt](evidence/film-pb-1-sub-framerate-20261127/diff-y-candidatos.txt))

14 545 696 B cada uno; difieren en **2 bytes**: `0xDDE20C` y `0xDDE20D` = los dos bajos del `mdhd.timescale`
de vídeo (`0xDDE20A`): `0x00007530` (30000) → `0x000061C1` (25025).

| expresión | orig198 | conv198-25p |
|---|---|---|
| `mdhd.timescale / stts.delta` | 30000/1001 = **29,970030** | 25025/1001 = **25,000000** |
| `muestras / (mdhd.duration / mdhd.timescale)` | 285 / 9,5095 s = 29,970030 | 285 / 11,4 s = **25,000000** |
| `muestras / (mvhd.duration / mvhd.timescale)` | 29,970030 | 29,970030 (igual) |
| `elst.segment_duration / mvhd.timescale` | 9,5095 s | 9,5095 s (igual) |

## 7. Recomendación sobre `scripts/mp4_set_framerate.py`

**Sirve tal cual** para el ensayo: cubre las dos fórmulas que dependen de `mdhd`, las únicas compatibles con lo verificado en §4. No cubre una hipotética fórmula basada en `mvhd`/`elst`, que exigiría reescribir `mvhd.timescale`, `mvhd.duration` y los dos `elst.segment_duration` (4 dwords, con redondeo y arrastre del `elst` de audio): **no** lo recomiendo, Sony deja 90000 fijo en `mvhd` y nada indica que se use para la cadencia. No hay que tocar `stts` (sus deltas fijan el *timing*; cambiarlos rompería la duración). Conviene que el script avise de que el clip pasa a 285 cuadros / 11,4 s.

Si se demostrara que **no** sale del `timescale`, no queda ningún campo de cadencia en el fichero (V §4): el único arreglo alternativo sin recodificar sería llevar la escala de película a 25p —`mvhd.timescale`+`mvhd.duration` (8 B) y los dos `elst.segment_duration` (8 B), 16 B en total, cajas `uuid` intactas— y dejaría el `elst` de audio con redondeo; hoy es una vía **no recomendada** y **NV**.

## 8. Límites

- **NV** `CS_FlashAcsr 0x21F1F4` → `0x1327AE`/`0x1EF4FC` → parseo del `moov`: 4 indirecciones con E/S de tarjeta
  y sin símbolos, no cerrado aquí; es el motivo de que §4 se quede en **D**.
- **NV** la semántica de `TvSystem()` (`0x1EEFDC`) más allá de la paridad (igual que el informe previo).
- **NV** la emulación *con fichero*: haría falta un arnés con hooks de `open/read/lseek/close` sobre el objeto
  `dfs_If` de `0x1D7022`, asignador (`malloc/free/memcpy/memset`) y el stub de log `0x65062C`. Descrito, no ejecutado: sin esos hooks la emulación se sale del mapa de memoria y no habría resultado medible.
