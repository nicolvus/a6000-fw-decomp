# FILM-PB-1 — Causa probable localizada: el sistema de TV (PAL/NTSC) frente a la cadencia del clip

Fecha: 27-11-2026. Sale de la segunda tanda de subagentes
([guarda B](film-pb-1-sub-guardab-20261127.md), [guarda A](film-pb-1-sub-guardaa-20261127.md),
[resume](film-pb-1-sub-resume-20261127.md)) y de una comprobación directa de bytes.

Cámara no accesible: **esto es una hipótesis con arreglo de menú, no una medida en la cámara.**
La comprobación cuesta un minuto y no requiere flashear.

## 1. La condición exacta de rechazo

`AviMMgr::isSupportContent` = ELF **`0x61A8F0`** (vtable `0x8E6E58`) devuelve 0 ⇒ el manejador
`0x437BC0` imprime «Detect UnSupported Content » (`0x437C3C`) y pone `0x1A` ⇒
`DefObjPlayer::ER_FAILED (7)` ⇒ caution `0x135` ⇒ **«No se puede visualizar.»**

Desensamblado verificado (`libmpr.so` 3.21, VA del ELF):

```
0x61a9ee  bl   0x1eefdc          ; TvSystem()
0x61a9f2  ldr.w r3,[r7,#0x124]   ; frameRate del contenido (0..9)
0x61a9f6  cmp  r0,#1             ; ¿TvSystem == 1?
0x61a9f8  bne  0x61aa1e          ; rama espejo
          ; TvSystem == 1
0x61a9fa  cmp  r3,#9 ; bhi 0x61aa52   → «Unknown frameRate %d» ⇒ return 0
0x61aa00  tst  (1<<r3),#0x2a8    ; bits 3,5,7,9 → 0x61aa3a «Invalid TvSystem detect» ⇒ return 0
0x61aa06  tst  (1<<r3),#0x154    ; bits 2,4,6,8 → 0x61aa4a «Valid TvSystem detect»  ⇒ return 1
0x61aa0c  tst  (1<<r3),#0x3      ; bits 0,1     → «24p/23.976p frameRate»           ⇒ return 1
          ; TvSystem != 1 (rama 0x61aa1e)
0x61aa26  tst  (1<<r3),#0x2a8    ; bits 3,5,7,9 → «Valid TvSystem detect»   ⇒ return 1
0x61aa2c  tst  (1<<r3),#0x154    ; bits 2,4,6,8 → «Invalid TvSystem detect» ⇒ return 0
0x61aa32  tst  (1<<r3),#0x3      ; bits 0,1     → 24p                      ⇒ return 1
```

Además hay un segundo `return 0` si `GetPlayThumbnailInfo` (`0x6E8430`, selector `0x1F`) falla
(«isSupportContent : GetPlayThumbnailInfo »).

El enum `frameRate` está **verificado** por dos tablas del propio firmware (nombres en `0x686A34`,
numérica en el `tbb` de `0x77AF2C`) y por el mapeo `1..10 → 0..9` de `0x6E0CD6`:

| enum | cadencia | familia |
|---:|---|---|
| 0 | 24000/1001 | 24p |
| 1 | 24 | 24p |
| 2 | 25 | **PAL** |
| 3 | 30000/1001 | **NTSC** |
| 4 | 50 | **PAL** |
| 5 | 60000/1001 | **NTSC** |
| 6 | 100 | **PAL** |
| 7 | 120000/1001 | **NTSC** |
| 8 | 200 | **PAL** |
| 9 | 240000/1001 | **NTSC** |

| TvSystem | Acepta | Rechaza |
|---|---|---|
| `== 1` = **PAL** | 24p (0,1) y **25/50/100/200** (2,4,6,8) | **29,97/59,94/119,88/239,76** (3,5,7,9) |
| `!= 1` = **NTSC** | 24p (0,1) y **29,97/59,94/119,88/239,76** (3,5,7,9) | 25/50/100/200 (2,4,6,8) |

`frameRate > 9` **devuelve 1** (acepta), no 0: descartado como causa.

24p se acepta en **ambos** sistemas, que es justo lo que hace la cámara de verdad: señal de que
la lectura es correcta. La partición par/impar es la de NTSC (60 Hz) frente a PAL (50 Hz).

## 2. Por qué esto explica el síntoma completo

- Los siete clips de la tarjeta son **30000/1001 = enum 3 (NTSC)**: 1440×1080, 285 cuadros, 9,5095 s.
  Si la cámara está en **PAL**, `isSupportContent` devuelve 0 para **todos** y la reproducción falla
  siempre con el mismo mensaje, sin tocar el fichero (que es conforme al grabador,
  [verificado](film-pb-1-sub-clip-20261127.md)).
- **Y la cámara está en PAL**: con el enum verificado, los siete clips son de la familia NTSC y
  **ninguno** se reproduce; una cámara en NTSC los aceptaría todos. Es la única combinación que
  explica que falle el 100 % de los clips. Corolario: una cámara PAL no puede haber grabado esos
  ficheros (no ofrece 30p), así que vienen de otra fuente.
- La cámara muestra **`1-1-2014`**: los ajustes se han reseteado. El **«Selector PAL/NTSC»** es
  justo uno de los que vuelven a su valor por defecto (PAL en Europa), y no tiene nada que ver
  con el CFW: la [auditoría](film-pb-1-auditoria-cfw-20261127.md) descartó cualquier parche en
  esta ruta.
- El `0:02` no es la causa ni la duración: es el **punto de reanudación** del clip
  ([resume](film-pb-1-sub-resume-20261127.md)), que el manejador solo copia y pasa a `PbStart`.
- El propio firmware lo dice con todas las letras en `string_spanish.uxc`:
  - «**Selector PAL/NTSC**» · «¿Cambiar a NTSC? Reinicia después de finalizar cambio. Es necesario
    formatear para grabar en soporte grabac. utilizado en PAL. Guarde la imagen de antemano.»
  - «**Imposible funcionar ya que el formato de película actual (PAL/NTSC) y el formato de
    película del soporte no coinciden.**»
  - «La grabación no está disponible en este formato de película porque está establecido en NTSC.
    ¿Formatear?»
- Las cadenas del módulo están en `libmpr.so`: «isSupportContent : Valid TvSystem detect»,
  «Invalid TvSystem detect», «Unknown frameRate %d», «24p/23.976p frameRate».

## 3. El ajuste NO está en el menú de esta cámara (verificado el 27-11)

El usuario confirma que la cámara no ofrece «Selector PAL/NTSC». Comprobado en el firmware 3.21:

- `share/app/viewNtscPalSEL_D.uxc` **existe** (700 B): el módulo de interfaz del ajuste está compilado.
- `share/app/global.xdb` lo declara (`viewNtscPalSEL_D.uxc`, y `CautionConfig.so` / `viewUnified2.so`
  contienen `NtscPalSEL`).
- Las cadenas de confirmación están en los 22 idiomas («Selector PAL/NTSC», «¿Cambiar a NTSC?»).

Es decir: **el firmware trae el ajuste, pero la configuración del modelo/región de esta cámara no lo
expone en el menú**, igual que otros ajustes ocultos ya inventariados en
[G13](../docs/gui/g13-barrido-ajustes-a6000-a6300.md). Por tanto el arreglo por menú **no está disponible** y
hay que elegir entre las vías de §4.

Dato que decide cuál: si la cámara graba hoy en **50p/25p/50i** está en PAL (`TvSystem != 1`) y los clips de
30p se rechazan; si graba en **60p/30p/60i** está en NTSC (`TvSystem == 1`) y esta hipótesis cae.

## 4. Vías de arreglo, con su riesgo

| Vía | Qué se hace | Riesgo | Cuándo elegirla |
|---|---|---|---|
| **V1 · Cambiar la cadencia declarada del clip** | **Hecho y probado**: `scripts/mp4_set_framerate.py` reescribe el `mdhd.timescale` de la pista de vídeo y deja **intactas** las cajas `uuid`, `MSNV`, `PROF`, `USMT` y `MTDT` (2 bytes distintos, mismo tamaño, decodifica sin errores, `r_frame_rate 25/1`). Con `ffmpeg -r 25 -c copy` **no** vale: deja `30000/1001` y borra las cajas ([evidencia](evidence/film-pb-1-v1-remux-20261127/ensayo-remux-25p.txt)) | Nulo para la cámara; el clip resultante se reproduce un 20 % más lento (11,4 s) | **Primer ensayo**: distingue PAL de NTSC en un solo clip |
| **V2 · Desbloquear el ajuste NTSC/PAL en el menú** | Parche de interfaz para exponer `viewNtscPalSEL_D` (mismo tipo de trabajo que G13/G14 con otros ajustes ocultos) | Medio: es un parche nuevo, sin probar en cámara | Si se prefiere arreglar la causa y seguir grabando en NTSC |
| **V3 · Traza y reparación de la otra rama** | `scripts/camera_filmpb1_trace.py` para ver si salta A, B o el motor; si es la miniatura, «Recuperar BD imág.» o renombrar `AVF_INFO` | Nulo | Si la cámara ya graba en NTSC (hipótesis caída) |

## 5. Cómo se refuta o se confirma

| Observación | Conclusión |
|---|---|
| Un clip grabado ahora por la cámara **se reproduce** y los viejos no | La cámara está bien y los viejos son de otra cadencia ⇒ V1 |
| La cámara graba en 60p/30p (está en NTSC) | La guarda B no rechaza por TvSystem; seguir con V3 |
| La cámara graba en 50p/25p y tras convertir un clip a 25p sigue fallando | El rechazo es por `GetPlayThumbnailInfo` o por el motor; seguir con V3 |

## 6. Ensayo listo: un clip de 25p en la tarjeta

Preparado `prueba-MAH04198-25p.mp4` (junto al original, en `~/Documents/a6000/`): es el
mismo clip con la cadencia declarada a 25 y todas sus cajas de Sony. Se copia a la tarjeta como
`MP_ROOT/103ANV01/MAH04200.MP4` (nombre nuevo, sin tocar los originales) y se reproduce:

| Resultado | Conclusión |
|---|---|
| El clip de 25p **se reproduce** y los de 30p no | La cámara está en PAL y la causa es la cadencia: **cerrado**. Basta pasar el reescritor a los siete clips (20 % más lentos) |
| **Ninguno** se reproduce (tampoco el de 25p) | La cadencia no es la causa: toca la traza (A frente a B) y la otra rama de la guarda |
| Los dos se reproducen | Imposible con el síntoma actual: revisar que el fichero copiado es el de 25p |

Cadena del dato (verificada por el [subagente de cadencia](film-pb-1-sub-framerate-20261127.md)):
`isSupportContent` llama a `GetPlayThumbnailInfo` (`0x6E8430`) pasándole un struct de 0x13C B como octavo
argumento; el valor sale de `mp4Ifo_AVISequence` (`0x6E0AB8` → `0x1D7022` → `0x21F1F4`) y se escribe en
`+0x124` desde `+0x100` (1..10) con el `tbb` de `0x6E0CE0` (`0x6E0D1A`). **No está en las cajas `uuid`,
ni en `avc1`, ni en `AVIN0001.INP`**; la fuente que queda es `mdhd.timescale`/`stts`, que es lo que cambia
el reescritor. Sobre los dos ficheros, `muestras/(mdhd.duration/timescale)` da **25,000000** en el convertido
y 29,970030 en el original.

Comprobado sobre el fichero de prueba: los **dos únicos bytes distintos** (offsets `0xDDE20C` y `0xDDE20D`)
caen dentro de `moov > trak > mdia > mdhd`; el `ftyp` sigue en `MSNV` con minor `0x015A0070`, la caja `uuid`
del offset `0x20` conserva su *usertype* y las cabeceras de las 48 cajas son idénticas
(`cmp -l` = 2 bytes). Para los siete clips:

```bash
for f in MAH0411*.MP4 MAH0416*.MP4 MAH0419*.MP4; do
  python3 scripts/mp4_set_framerate.py "$f" "conv-$f" --fps 25
done
```

## 7. Límites

- **NO_VERIFICADO** el valor actual del ajuste en la cámara y el mapeo exacto `frameRate`→cadencia
  (solo la partición par/impar está verificada por bytes y por el caso 24p).
- **NO_VERIFICADO** que `TvSystem()` (`0x1EEFDC`) devuelva el ajuste de menú y no otro estado; es
  la inferencia más fuerte pendiente y se confirma con el punto 2 del plan.
- La otra rama de rechazo (`GetPlayThumbnailInfo`, miniatura) se cubre con «Recuperar BD imág.».
