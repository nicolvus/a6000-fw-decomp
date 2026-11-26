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

| TvSystem | Cadencias aceptadas | Cadencias rechazadas |
|---|---|---|
| `== 1` | bits 0,1 (24p/23,976p) y bits **pares** 2,4,6,8 | bits **impares** 3,5,7,9 y >9 |
| `!= 1` | bits 0,1 y bits **impares** 3,5,7,9 | bits **pares** 2,4,6,8 y >9 |

24p se acepta en **ambos** sistemas, que es justo lo que hace la cámara de verdad: señal de que
la lectura es correcta. La partición par/impar es la de NTSC (60 Hz) frente a PAL (50 Hz).

## 2. Por qué esto explica el síntoma completo

- Los clips de la tarjeta son **30000/1001 (30p, NTSC)**: 1440×1080, 285 cuadros, 9,5095 s. Si el
  ajuste de la cámara está hoy en **PAL**, `isSupportContent` devuelve 0 para **todos** ellos y la
  reproducción falla siempre con el mismo mensaje, sin tocar el fichero (que es conforme al
  grabador, [verificado](film-pb-1-sub-clip-20261127.md)).
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

## 3. Arreglo propuesto, con su riesgo

1. **Antes de nada, copiar al PC todos los vídeos y fotos de la tarjeta.** El aviso del propio
   menú dice que hay que formatear para *grabar* en una tarjeta usada en el otro sistema; copiar
   evita cualquier pérdida.
2. **Menú → «Selector PAL/NTSC»** (página de ajustes de la cámara) y poner el sistema **contrario
   al actual**: si está en PAL, pasar a **NTSC** (es el que corresponde a clips de 30p). La cámara
   reinicia.
3. Reproducir un clip. Si aparece la imagen, queda cerrado.
4. Si el ajuste ya estaba en NTSC, o el cambio no arregla nada, la hipótesis cae y el siguiente
   paso es la traza con `scripts/camera_filmpb1_trace.py` (guarda A frente a guarda B) y la
   lectura del índice `AVF_INFO\AVIN0001.INP` con `reports/evidence/film-pb-1-sub-avin-20261127/leer_avin.py`.

Riesgo: bajo. El cambio de sistema reinicia la cámara y no toca el firmware; el formateo **no** es
necesario para reproducir y aquí no se propone.

## 4. Cómo se refuta o se confirma

| Observación | Conclusión |
|---|---|
| El ajuste estaba en PAL y al pasar a NTSC los clips se reproducen | **Causa raíz cerrada**; el CFW queda exculpado y no hay que flashear nada |
| El ajuste ya estaba en NTSC | La guarda B no rechaza por TvSystem; seguir con la traza (A frente a B) |
| El ajuste estaba en PAL y tras el cambio sigue fallando | El rechazo es por `GetPlayThumbnailInfo` o por el motor; seguir con la traza |

## 5. Límites

- **NO_VERIFICADO** el valor actual del ajuste en la cámara y el mapeo exacto `frameRate`→cadencia
  (solo la partición par/impar está verificada por bytes y por el caso 24p).
- **NO_VERIFICADO** que `TvSystem()` (`0x1EEFDC`) devuelva el ajuste de menú y no otro estado; es
  la inferencia más fuerte pendiente y se confirma con el punto 2 del plan.
- La otra rama de rechazo (`GetPlayThumbnailInfo`, miniatura) se cubre con «Recuperar BD imág.».
