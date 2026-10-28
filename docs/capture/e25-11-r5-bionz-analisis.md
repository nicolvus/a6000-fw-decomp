# E25-11 — Dónde calcula BIONZ `r5` y qué cambiar para que la foto use ShutMode 0 (análisis offline, 27-10-2026)

Sesión **100 % offline** (Capstone sobre `av-cam.bin` fw 3.21, SHA-256 `b60c845c…56bb9`, base `0x43541000`, físico = virtual + `0x40000000`).
No se conectó la cámara ni se escribió nada. Bytes verificados en `tests/test_e25_11_av_cam_r5.py` (9 pruebas; se omiten sin firmware).
Etiquetas: VERIFICADO = bytes/instrucciones leídos; INFERENCIA = interpretación.

## 1. Cómo consume `r5` el sensor (VERIFICADO)

`SetExposure` del IMX210 (`0x436d6f6c`, vtable `0x43fcc090+0x28`) lee el bloque de parámetros `param` (en `r1`):

| Campo | Lectura | Uso |
|---|---|---|
| `param+0` (h) | `0x436d6fae ldrh r5,[r1]` | **r5**: byte bajo → `+2` de una estructura sombra; bits 8–13 → otra |
| `param+4` (h) / `+6` (h) | `0x436d6faa`, `0x436d6fb0` | r6 / r7 (tiempos adicionales, sin efecto en T037/T038 salvo atascos) |
| `param+9` (b) | `0x436d6fb6 ldrb.w sb,[r1,#9]` | **ShutMode**; `tbb` de 5 ramas (0–4) |

`r5` es independiente del ShutMode (prólogo común); el ShutMode cambia bits de ID1 y la espera de Darwin `0x107` (S56, T028–T031).

## 2. Dos productores de `param` (VERIFICADO por llamadas; semántica = INFERENCIA)

`bl 0x436d6320` (envoltorio de `SetExposure`) se llama solo en 4 sitios: `0x438c79fc`, `0x438c830c`, `0x438c8824`, `0x438cc894`.

1. **Vista en directo — `0x437b27b8`** (único llamador `0x438cc868`, justo antes de `0x438cc894`): construye un registro de 16 B
   (`[r6+0x168..0x177]`, copiado a `*(r8+8)`) cuyo primer halfword vale
   `r5 = máx( [r8] − 0x4382fa94(h[obj+0x4da]) / [r6+0x134], [r6+0x144] )` (`0x437b288a..0x437b28c6`: `rsb sb,r0,sb` y `cmp/strhs/strlo`).
   Interpretación: `[r8]` = longitud de cuadro en líneas (≈ 4219–4270, T046), el cociente = líneas de exposición y `[r6+0x144]` = mínimo de `r5`. Es la fórmula
   medida en T046/T047 (E = (4219 − `r5`)·15,2 µs). **Sin verificar:** unidades de `0x4382fa94` y de `[obj+0x4da]`; que `[r8]` sea exactamente 4219.
2. **Foto — función de captura `0x438c828c`** (llamada al envoltorio en `0x438c830c`): el `param` lo copia `0x4383fd6c` desde un registro estático de modo
   (`R+0x64..0x73`, 16 B, vía `0x4383fb6c(cap+0x1c0, cap+0x1b8)`) a `cap+0x64c` (`param+9` = `cap+0x655`). Ese registro lleva **`r5` constante = 1** (T032), de modo
   que sin cortina la exposición sale como el cuadro completo (64,9 ms; T046 «sin forzar») y la cortina mecánica fijaba el tiempo real. Por eso la foto no sigue la velocidad.

## 3. Ya existe una ruta ShutMode 0 + `r5` fijo en la foto (VERIFICADO)

En `0x438c82a8..0x438c82cc`:

```
0x438c82a8  bl  0x43a12c64        ; clasificador de modo
0x438c82ac  cmp r0,#2 ; beq 0x438c82b8
0x438c82b0  bl  0x43a12c64 ; cmp r0,#3 ; bne 0x438c82d0     ; (0x438c82b6)
0x438c82b8  movs r3,#0 ; movs r1,#2
0x438c82bc  strb.w r3,[r4,#0x655]   ; param+9  = ShutMode 0
0x438c82c0  strh.w r3,[r4,#0x650]   ; param+4  = 0
0x438c82c4  str.w  r1,[r4,#0x64c]   ; param+0  = 2  (r5 = 2)
0x438c82c8  strh.w r3,[r4,#0x652]   ; param+6  = 0
0x438c82cc  strb.w r3,[r4,#0x654]   ; param+8  = 0
```

`0x43a12c64` clasifica una variable global (literal `0x43a12ca4`): `0xbb` → 2; `1` → 3; `0x31–0x37`, `0xbc`, `0xee–0xef`, `0xfd–0xff` → 1; resto → 0.
INFERENCIA: es el código de modo de disparo; con 2 ó 3 la foto se hace en ShutMode 0 con `r5` = 2 (cuadro completo ≈ 64 ms, sin parámetro de velocidad).
Cuál es el modo 2/3 en la A6000 (¿automáticos?) **no está verificado**; hay una ruta análoga en la A7S (S52, `0x438b775c`). Los otros llamadores ponen `param+0 = 0` con ShutMode 4
(`0x438c79e2`, bandera `[r6+5]`) o ShutMode 1 (`0x438c87f0`).

## 4. Qué cambiar (diseño, no probado)

Objetivo: en M/A/S/P, ShutMode 0 con `r5 = máx(r5_mín, VTS − T/15,2 µs)`.

| Opción | Cambio | Ventajas / límites |
|---|---|---|
| **C1** (lo ya probado en RAM, T028–T047) | `0x436d6fb6` → `4ff00009` (`mov.w sb,#0`) y `0x436d7000` → `r5` calculado | Fuerza ShutMode 0 para **toda** llamada (vista en directo ya usa 0; vídeo y otros modos sin probar). `r5` no puede ser constante: necesita T |
| **C2** (propuesta) | En `0x438c82b6` sustituir `bne 0x438c82d0` (2 B) por `nop` (`00bf`) para tomar siempre el bloque de §3, y cambiar `movs r1,#2` (`0x438c82ba`) por un cálculo de `r5` en una cueva de código | Solo afecta a la ruta de captura. Falta T: **[cap+0x4da] (código Tv, §6)**, no `[cap+0x56c]` (descartado en §6). T → líneas: `0x4382fac8([cap+0x4da])` da µs; líneas = µs·5/76 (`0x4355faf0` es la división ya existente); constantes (4219, 15,2 µs) medidas en esta cámara |
| C3 | Llamar al constructor de la vista en directo `0x437b27b8` desde la captura | Descartada por ahora: argumentos y efectos laterales sin verificar |

Pendiente antes de cualquier prueba: que `[cap+0x4da]` lleve en la **foto** el código Tv de la velocidad (§6); valor de `[r6+0x134]` y `[r6+0x144]`; que Darwin (`0x107`) no dependa de `r5`; efecto sobre ráfaga/vídeo/AF.

## 5. Vía permanente: no recomendada hoy

- `av-cam.bin` está dentro de `nflasha3` (TPZL: vmlinux + initrd + av-cam + sabin) en `firmware.tar`. Cambiarlo exige un re-empaquetador reproducible byte a byte (existe para Darwin, **no** para `nflasha3`), que el arranque no valide firma/hash (sin verificar) y reescribe ≈ 212 MB de particiones ([E24-04 M16](e24-04-dictamen-seguridad.md)).
- Un `av-cam` defectuoso deja sin arranque el sistema principal, y **la única entrada al actualizador es por software desde ese sistema** ([E24-03 F6](e24-03-auditoria-recuperacion-usb.md)): el FDAT 3.24 de recuperación solo sirve si la cámara sigue llegando al actualizador. El riesgo es «alto y simétrico» (E24-04) y no hay recuperación independiente (E25-04).
- **Alternativa sin flasheo (no implementada):** reaplicar los parches de RAM (§4 C1/C2, con verificación y reversión) desde la app RemoteShutter tras cada arranque, vía telnet/adb. No persiste tras apagar, pero es reversible y no toca flash/NVRAM.

## 6. Unidades verificadas (offline, 27-10-2026)

**Tv → tiempo — VERIFICADO por bytes y por emulación** (`scripts/e25_11_tv_emu.py`, Unicorn sobre `av-cam.bin`; prueba `test_tv_a_tiempo_emulado`):

- `0x4382fac8(x)` devuelve **µs** = `1e6 · 2^((4096 − x)/256)` (±1 µs); `0x4382fa94(x)` devuelve ese tiempo en **1/256 µs** y `0xFFFFFFFF` si `x ≤ 0xC00` (≥ 16 s). Entrada `x` = `0x1000 + 256·log2(1/t)`: `0x1000` = 1 s, un paso de 1/256 EV por unidad.
  Tablas internas: `0x43902924` = `2^(x/256)·65536` (exp2 con tabla de 256 entradas).
- Velocidades enteras (calculado con la función): 1/4000 → `x`=`0x1bf7` → 250 µs; 1/1000 → `0x19f7` → 1000 µs; 1/250 → `0x17f7` → 4002 µs; 1/60 → `0x15e8` → 16 674 µs.

**`[cap+0x56c]` NO es el tiempo de exposición (INFERENCIA moderada):** es un `u32` que `0x438c7aee` pone a `10·k + valor` o `2·valor`, y `0x438c7df0` reescribe desde `fp`; se usa como `1000·[0x56c] / …` y como mitad baja de la carga del mensaje a Darwin `0x107` junto con `[0x570]` (`0x438c83ae..ba`). Es la espera/sincronización asociada al mensaje `0x107` (S56), no `T`. Se descarta como entrada de C2.

**`[cap+0x4da]` es el candidato correcto (VERIFICADO por bytes; significado = INFERENCIA):** halfword copiado de `[src+0x29c]` en una tira de seis halfwords `+0x4d4..+0x4de` (`0x43b0cbc6`, simétrico en `0x43b0c554`); la única lectura que lo usa es el constructor de la vista en directo (`0x437b2878`), que lo pasa a `0x4382fa94`. Falta comprobar que en la **foto** lleve el código de la velocidad elegida (dump en vivo, con autorización).

**Constantes del sensor (INFERENCIA fuerte):** `0x4385de94(a, m, c)` = `(0x271000 | 0x4e2000) / a · m` (u16), que se usa como longitud de cuadro (VTS). Con `a = 600`: 2 560 000/600 = **4267 líneas**, el cuadro completo medido (≈ 4270; T046: 64,9 ms). Y 15,2 µs/600 = 25,33 ns = 64,9 ms/2 560 000: **una misma unidad de 25,3 ns (≈ 39,5 MHz) explica tanto el tiempo de línea como el de cuadro**. No se pudo leer `[r6+0x134]` (la estructura está a cero en el volcado de servicio en reposo `ram-servicio-20261020`).
**No resuelto:** el constructor de la vista en directo divide `256·t_µs` entre `[r6+0x134]` (`0x437b2894`); con `[0x134]`=600 daría 2,34 µs por línea (6,49 veces menos que los 15,2 µs medidos). Hay una escala (¿unidad de `0x4382fa94`? ¿otra fuente de `[0x134]`?) sin explicar; para la foto C2 usaría las constantes **medidas** (T044/T046/T047), no esa división.

**Fórmula C2 propuesta (calculada, no medida salvo T047):** `r5 = máx(r5_mín, 4219 − round(µs/15,2))` con `µs = 0x4382fac8([cap+0x4da])`:

| Velocidad | µs | líneas | `r5` | medido (T047) |
|---|---|---|---|---|
| 1/4000 | 250 | 16 | 4203 | 0,24 ms (obj. 0,25) |
| 1/2000 | 500 | 33 | 4186 | — |
| 1/1000 | 1000 | 66 | 4153 | 0,99 ms (obj. 1,00) |
| 1/500 | 2001 | 132 | 4087 | — |
| 1/250 | 4002 | 263 | 3956 | 4,03 ms (obj. 4,00) |
| 1/125 | 8005 | 527 | 3692 | — |
| 1/60 | 16 674 | 1097 | 3122 | 16,75 ms (obj. 16,7) |
| 1/30 | 33 348 | 2194 | 2025 | — |
| 1/15 | 66 696 | 4388 | **−169 (imposible)** | — |

**Límite nuevo:** con ShutMode 0 la exposición máxima uniforme es el **cuadro completo (≈ 64,9 ms ≈ 1/15,4)**; desde 1/15 hacia velocidades más lentas `r5` queda fuera de rango y habría que dejar la ruta normal (ShutMode 3, donde el τ de T044 pesa poco) o un modo de varios cuadros. C2 debería caer a la ruta original cuando `líneas > 4218`.

## 7. Lectura en vivo de `[cap+0x4da]` (T048, 27-10-2026, solo lectura de RAM) — NO confirmado

Con autorización del usuario («lee [cap+0x4da] en vivo, solo lectura»; sin parches ni escrituras de RAM; `scripts/camera_ram_speed_scan.py`): cuatro disparos (1/60, 1/250, 1/500, 1/1000) con un volcado de 4 MiB (`0x83c00000..0x84000000`, que contiene los objetos conocidos `0x83e7f4a8`, `0x83ea5ca4`, `0x83edf684`) tras cada uno.
(Un primer intento no sirvió: los archivos de `/data/local/tmp` creados por `dd` son de solo lectura y el segundo volcado devolvía el primero; se repitió borrando antes.)

- **No hay ningún halfword con el código Tv `0x1000 + 256·log2(1/t)`** (1/60 → 5608, 1/250 → 6135, 1/500 → 6391, 1/1000 → 6647, tolerancia ±3) en las cuatro velocidades, ni ninguno con pasos de ±256/±527 (1/256 EV), ni monótono con el tiempo en 1/256 EV.
- **Candidato a objeto de captura:** el patrón del `param` de la foto (`r5` = 1, ShutMode 3 en `+0x64c`) aparece, entre otros, en `0x83e1a36c` ⇒ `cap` = `0x83e19d20` (INFERENCIA: hay otras seis coincidencias del patrón). Ahí `[+0x56c]` = 864 y `[+0x570]` = 4176 (valores constantes) y **`[+0x4d4..+0x4de]` = 0, 0, 1, 1, 3, 0**, es decir **`[cap+0x4da]` = 1**, sin cambio con la velocidad ni durante el disparo (600 lecturas de 388 B por disparo, a 1/250 y 1/1000: un único estado). Si ese es el objeto vivo, `[cap+0x4da]` **no lleva el Tv de la foto**; si no lo es, el objeto vivo no se localizó.
- **Lo que sí sigue a la velocidad en esa ventana:** (a) un índice en tercios de EV, 24 → 30 → 33 → 37 para 1/60 → 1/250 → 1/500 → 1/1000 (p. ej. `0x83e996cc`, `0x83e9b700`, `0x83ea9a90`, `0x83eaf1a8`, `0x83eb29a4`: espejos de ajustes); (b) un registro de exposición en `0x83e88ab8` (u16 = 4283, 1017, 521, 252) con una copia ×32 en `+4` (137 060, 32 557, 16 700, 8070): ≈ t/3,9 µs, o t en unidades de 125 ns (≈ 1–4 % por encima del tiempo nominal, ¿cuantizado en líneas de ≈ 4 µs, probablemente de la vista en directo?). Sin interpretar.

**Consecuencia para C2:** la entrada de tiempo `[cap+0x4da]` de §4/§6 queda **sin confirmar** (y probablemente sea propia de la vista en directo). Fuentes alternativas para el tiempo de la foto, sin verificar: el índice en tercios de EV (tabla de velocidades → µs) o el registro de `0x83e88ab8`; habría que buscar su origen estático (escritor) antes de diseñar C2. No se ha tocado nada en la cámara.

## 8. Búsqueda estática del origen del tiempo de la foto y propuesta C2 (27-10-2026, offline)

**Corrección a §6/§7 (VERIFICADO por bytes):** en el constructor de la vista en directo el objeto que se pasa como `r0` a `0x437b27b8` no es `cap` sino `cap+0x1198`
(`0x438cc856..5e`: `add.w r0,r4,#0x1180; adds r0,#0x18`; `r1 = cap+0x20`, `r2 = sp+0xec` entrada, `r3 = sp+0xbc` salida). Por tanto su `ldrh r0,[r4,#0x4da]`
(`0x437b2878`) es **`[cap+0x1198+0x4da] = [cap+0x1672]`**, no `[cap+0x4da]`. En el objeto candidato de T048 (`cap` = `0x83e19d20`) todos esos campos están a 0 en reposo (4 volcados),
de modo que ese objeto no es el vivo o no se rellena fuera de la vista en directo. La lectura de T048 sobre `[cap+0x4da]` (la función de captura `0x438c828c` usa otro `r4`) no refuta ni confirma el Tv de LV.

**Qué se buscó y qué se encontró (VERIFICADO salvo indicación):**

| Búsqueda | Resultado |
|---|---|
| Tabla de velocidades (código Tv de 1/3 EV, pasos de 85/86 en u16) en `av-cam.bin` | **No existe.** La conversión es la fórmula exp2 de §6; la velocidad llega ya como valor (índice o código) desde fuera de LIRO |
| Tablas geométricas (razón 2^(1/3)) u32/u16 | Solo tablas de **ISO**: `0x43bc48ec`/`0x43bc6050` (16, 20, 25 … 204 800, 41 entradas, versión ×65536 en `…ea`) y `0x43bc5fcc` (800 … 128 000); ninguna de velocidades |
| Cadenas con «shutter speed/exposure time» | Ninguna útil (`0x43c52495` «EDIT SHUTTER SPEED ERROR» es de la edición de vídeo) |
| `0x83e88ab8` (T048) | **Registro de estadísticas de AE/AF** en un vector de entradas de `0x210` B (`0x83e88ab8`, `…cc8`, `…ed8`): `[+0]` = 255/216, `[+4]` = valor con signo (5760, −2765, −1057, −22 221), `[+8]` = 4283/1017/521/252, `[+0xc]` = 32× eso, más contadores. El campo `[+8]` ≈ t/3,9 µs: la **exposición usada por la medición**, no un parámetro que lea `SetExposure`. Descartado como entrada de C2 |
| Fuente del `param` de la foto | `StrtExps` `0x4381106c` (`CaptureManager`): copia 16 B desde `*(0x4378f9b4()+0x24)` (objeto estático, `0x4378f9b4` devuelve `0x4378f9bc+0x70984e`) a `sp+0x18` y los modifica con `[cap+0x1f8]`, `[cap+0x1fc]`, `[obj+0xcc]` y `[obj+0x14e]` (`0x438110be..28`) antes de llamar a `SetExposure`. **Ahí** se decide `param+4` (r6); aún no se ha desarmado la rama que fija `param+0` (r5) ni la entrada de tiempo |

**Estado:** el tiempo de exposición de la foto **no tiene una fuente estática confirmada** dentro de `av-cam`. Cualquier C2 en BIONZ (entrada = `[cap+0x4da]`, `[cap+0x1672]` o `0x83e88ab8`) sigue sin base verificada y no se debe proponer como parche.

### C2 viable: «modo silencioso» desde la app (RAM), sin tocar BIONZ ni Darwin (propuesta, no implementada)

La entrada de tiempo **ya la tiene la app**: `CameraEx.getShutterSpeed()` (RemoteShutter lo usa). Como los parches de T046/T047 son de RAM y `/dev/mem` es `crw-rw-rw-` (visto en T048, accesible al usuario de adb), la app podría hacerlo sola:

1. Antes de cada disparo: `T` → µs (par `n/d` de `getShutterSpeed`), líneas = µs/15,2, `r5 = 4219 − líneas` (§6; solo si 2 ≤ `r5`, es decir T ≤ ≈ 64 ms; si no, disparo normal).
2. Comprobar los bytes originales de `0x836d6fb6` (`91f80990`) y `0x836d7000` (`28125ffa85fe`); escribir `4ff00009` y `r5` (`hi 20 4ff0 lo 0e`); verificar lectura.
3. Disparar con RAW+JPEG; **siempre revertir y verificar** (`finally`), con aborto a los 45 s como `camera_r5_raw.py`.
4. Medidas ya hechas lo respaldan: T046/T047 (uniforme por filas, ±1 % con la calibración de T046). Sin persistencia: tras apagar vuelve al comportamiento normal.

Riesgos: ShutMode 0 vale para **todas** las llamadas mientras esté parcheado (la vista en directo ya lo usa, T031); no probado con ráfaga, AF ni vídeo; el incidente de T037/T038 fue con `r6`/`r7`, no con `r5`; la app debe poder revertir aunque se cierre (vigilante).

## 9. Prueba del modo silencioso en la app (T049, 28-10-2026): funciona, pero el mecanismo de escritura no es seguro

- **Funciona:** 6 disparos silenciosos (1/4000, 1/1000, 1/250 ×2) con `r5` calculado por la app (4203, 4153, 3956), parche y reversión verificados cada vez; exposición uniforme por filas y dentro de ≈ ±16 % del objetivo con la calibración de la misma tanda (1/1000 +6 %, 1/250 +11 %, 1/4000 −16 % con señal muy baja).
- **Dos fallos de implementación (no de la idea):** (1) `RandomAccessFile` no direcciona `/dev/mem` por encima de 2 GiB (`Value too large`); (2) `Runtime.exec("dd")` desde un proceso de 100 MB en una cámara con ≈ 8 MB libres es frágil: en el 7.º disparo el `fork` quedó colgado (hijo `ar.shutter` parado) **entre las dos escrituras**, dejando **ShutMode 0 forzado** en RAM y `r5` original. El vigilante y los `catch` usan el mismo camino y no podían revertir; se revirtió por telnet y se mató la app.
- **Consecuencia:** una app no debe aplicar el parche por `Runtime.exec`. Alternativas: (a) que lo aplique el PC por telnet (probado en T046/T047, sin colgar), (b) la app habla con el `telnetd` de `127.0.0.1:23` (sin `fork` propio), (c) aplicar ambas escrituras en **un solo `dd`/comando** y proceso auxiliar preabierto. Sin eso, el modo silencioso en la app **no se considera seguro** y queda desactivado por defecto (`silentOn` = false; solo `/silent?v=1`).
- Sin la 2.ª parte de la tanda (1/60, 1/30, 1/15, ráfaga) no hay medida de esos casos con la app; sí con parches por telnet (T047: 1/60 → 16,75 ms).
