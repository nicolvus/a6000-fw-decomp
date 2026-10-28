# T052-A — Parámetros reales de exposición y preparación segura de C3

**Fecha:** 28-10-2026 · **Cámara:** ILCE-6000, fw **3.23** (Darwin B1a) · **BIONZ:** `av-cam.bin` 3.21,
SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`
**Alcance:** análisis estático, emulación *offline* y lectura de un volcado de RAM real ya capturado.
**No se conectó la cámara, no se escribió RAM/NVRAM/NAND, no se ejecutó firmware en hardware y no se
ejecutó C3.**

Etiquetas: **V** = verificado por bytes/instrucciones o por un volcado real; **I** = inferencia con
evidencia; **N** = no verificado.

---

## 0. Respuesta corta

1. **T052-A no se ejecutó físicamente.** La cámara no estaba accesible: el PC está en
   `192.168.0.13/24`, no hay ruta a `192.168.1.29` (la IP de T048–T050), no hay `adb` ni `pmca` en el
   equipo y el barrido de `192.168.0.0/24` no encontró un shell de cámara. No se simuló ninguna lectura
   de hardware.
2. **Se avanzó la parte estática y se usó el volcado real del 20-10-2026** (1 GiB de RAM, cámara en
   marcha, reposo, fw 3.21) para confirmar el mapa, los punteros GOT y los objetos. Ese volcado **no
   contiene una foto**: los dos registros de captura están a cero porque el constructor los limpia y
   no se disparó desde el arranque.
3. **La incertidumbre del VTS no se cerró.** Se identificó de dónde sale el campo:
   `record+0x20 ← cap+0x5e0 ← [descriptor+6]`, con el descriptor en `[param+0x3c]` del constructor
   `0x43844e80`. El valor real de ese descriptor durante una foto **no se leyó**. 4219 y 4266 siguen
   siendo hipótesis; la clasificación es **«valores distintos cuya causa todavía impide autorizar C3»**.
4. **Apareció un bloqueo nuevo, no documentado en E25-16:** el productor nativo llama al predicado
   `0x43a12ca8`, que lee `[0x43deb360+0x10]`. En el volcado real ese byte vale 0 → el predicado
   devuelve 1 y la función **suma un cuadro completo** a `r5` (8422/8175/7341 para 1/4000, 1/250 y
   1/60), lo que invalida la exposición. El arnés de E25-16 sustituye ese predicado por 0. Es una
   suposición no verificada y, con el único estado real disponible, **falsa**.
5. **También se corrigió la lista de escrituras de E25-16:** `0x4383fa40` escribe además
   `record+0xd8`, `+0xda` y `+0xdc`. La copia a *scratch* sigue siendo obligatoria; ejecutarla sobre el
   registro global (C1/C2) corrompería más campos de los que se creía.
6. **Decisión:** C3 **no se autoriza todavía**. No es una contradicción de la fórmula: es falta de
   lectura física. El diseño lógico se mantiene, pero T052-B debe empezar por una fase **B0 de solo
   lectura** que mida, tras una foto normal, `record+0x20`, `record+0xc`, `record+0x1c`, el factor, la
   compuerta y el predicado. Solo si esos valores son coherentes se puede pasar a la prueba C3 en RAM.

---

## 1. Versión y estado de la cámara

| Elemento | Valor | Base |
|---|---|---|
| Cuerpo | ILCE-6000 (A6000) | usuario |
| Firmware | 3.23, Darwin B1a instalado en T040 | T040 |
| BIONZ analizado | `av-cam.bin` 3.21, SHA-256 `b60c845c…e56bb9` | binario del repo |
| Base de carga | `0x43541000`; virtual `0x43xxxxxx` = físico `0x83xxxxxx` | bytes + volcado |
| Estado físico | **no accesible** en esta sesión | ping/telnet/scan; sin `adb`/`pmca` |
| HEAD al inicio | `4997ecc6` (sin commits posteriores; los archivos sin seguimiento de T042–T044 no se tocaron) | `git log`/`git status` |

La instalación de T040 cambió Darwin (tipo 0 + B1a); el paquete 3.23 conserva el `av-cam.bin` de 3.21
según E25-05/T040 (no se comparó byte a byte en esta sesión). El análisis estático y el volcado del
20-10 usan ese binario 3.21; la cámara actual ejecuta 3.23 con ese BIONZ.

**Comprobación de acceso (28-10-2026):**

- `ping 192.168.1.29` → 100 % de pérdida; `192.168.1.0/24` no está en la tabla de rutas.
- El PC está en `192.168.0.13/24`; el barrido de `192.168.0.0/24` solo abrió el puerto 23 del router
  (`192.168.0.1`) y de `192.168.0.252`, que no respondió como shell de cámara.
- No hay `adb`, ni `pmca`, ni `pmca-console` instalados; no hay dispositivo Sony visible por USB.

Por eso **A1 no se ejecutó** y todas las lecturas de esta sesión son (a) del binario, (b) de emulación
o (c) del volcado real del 20-10. No se presenta ninguna como lectura de una foto.

---

## 2. Procedimiento de lectura exacto (A0)

### 2.1 Validación del firmware y del mapa

1. SHA-256 del `av-cam.bin` = `b60c845c…e56bb9` (el mismo que usan E25-14/15/16).
2. Bytes de los sitios de T046/T050 en el binario: `0x436d6fb6 = 91f80990` y
   `0x436d7000 = 28125ffa85fe`. En el volcado real, en físico `0x836d6fb6` y `0x836d7000`, aparecen
   exactamente esos bytes: **el mapa virtual→físico es `+0x40000000`** (V).
3. La GOT de `av-cam` está en `0x4401eee4`. Los punteros que usa el código son **virtuales**
   (`0x43xxxxxx`); `/dev/mem` y el volcado usan **físico** (`0x83xxxxxx`). No son intercambiables.
4. Los objetos leídos están en DRAM (`0x83xxxxxx`), no en MMIO (`0xf0xxxxxx`/`0xf2xxxxxx`). El volcado
   del 20-10 se hizo con RMEM sobre DRAM y no toca MMIO.

### 2.2 Tabla de objetos

| Objeto | Origen estático | Dirección runtime (virtual / física) | Selección | Evidencia |
|---|---|---|---|---|
| Registro de foto A | GOT `0x44022648`; `0x4383fb6c` rama A | `0x43ea5b4c` / `0x83ea5b4c` | `[cap+0x1b8] & 1 == 0` (y selector `0x43b08d42` = 0) | **V**: GOT leída en el volcado; bytes del constructor |
| Registro de foto B | GOT `0x44025dfc`; `0x4383fb6c` rama B | `0x43eee770` / `0x83eee770` | `[cap+0x1b8] & 1 == 1` | **V**: GOT leída en el volcado |
| Ajustes | GOT `0x440207e8`; `0x4383fbc4` | `0x43f79f94` / `0x83f79f94` | mismo selector `[cap+0x1b8]` | **V**: GOT; `+0x162` = `0x15e8` (1/60) en el volcado |
| Objeto imager/config (2.º argumento de `0x4383fa40`) | GOT `0x44021ba8`; `0x437b4438` (`r7`) | `0x43ea976c` / `0x83ea976c` | GOT `+0x2cc4` | **V**: GOT; `+0x4b8` = 1 en el volcado |
| Entrada B de la compuerta | GOT `0x44024e58`; `0x437b3b64` | `0x43f6e5c2` / `0x83f6e5c2` | GOT `+0x5f74` | **V**: GOT; `+0x8c` = 0 |
| Predicado de cuadro extra | GOT `0x440253cc`; `0x43a12ca8` | `0x43deb360` / `0x83deb360` | GOT `+0x64e8` | **V**: GOT; `+0x10` = 0 |
| Contexto de captura `cap` | llamador `0x43b1e7f2` → `0x43ae75dc` (`ldr r0,[r0]`) | **no identificado** | puntero de contexto de ejecución | **N**: no se localizó en el volcado de reposo; su lectura (`cap+0x11b0`, `cap+0x5c8`, `cap+0x64c`) queda bloqueada |

### 2.3 Cómo se selecciona el registro y los ajustes

`0x4383fb6c` (y su gemelo `0x4383fbc4`) hace:

```
4383fb74  bl 0x43b08d42          ; selector global (0 = banco A)
4383fb78  cbz r0, 0x4383fb80
4383fb7a  tst r5,#1              ; r5 = [cap+0x1b8]
4383fb7e  bne 0x4383fb86         ; bit 0 = 1 -> banco B
4383fb80  ldr r3,[pc,#0xc]; ldr r0,[r4,r3]   ; GOT +0x3764 (registro A)
4383fb86  ldr r3,[pc,#0xc]; ldr r0,[r4,r3]   ; GOT +0x6f18 (registro B)
```

**V** por bytes. El banco activo depende de `[cap+0x1b8] & 1` y del selector `0x43b08d42`. Como `cap`
no se localizó en el volcado de reposo, **T052-B debe leer los dos registros** y decidir por el
contenido (el que tenga `Tv`/`r5` distintos de cero y coherente con la velocidad es el activo); no se
debe asumir el banco A.

### 2.4 Cómo se obtiene el objeto `settings` sin asumir la estructura

El constructor normal `0x437b43b4` recibe:

- `r0` = `cap+0x1198` (sub-objeto de captura; **no** es un bloque de ajustes, corrección de E25-16);
- `r1` = `cap+0x20` (el objeto de captura, base `cap` desplazada);
- `r2` = descriptor `{u16, u16, ptr}`;
- `r3` = bloque temporal.

Dentro:

```
437b43c6  ldr.w r6,[pc,#0x930]   ; base GOT 0x4401eee4
437b4410  ldr.w r3,[pc,#0x8e8]   ; offset 0x3764
437b441a  ldr   r5,[r6,r3]       ; registro A/B
437b4438  ldr.w r2,[pc,#0x8c8]   ; offset 0x2cc4
437b443e  ldr   r7,[r6,r2]       ; objeto imager/config (2.º argumento)
437b4504  ldr.w r3,[pc,#0x800]   ; offset 0x1904
437b450c  ldr.w fp,[r6,r3]       ; objeto de ajustes (0x43f79f94)
```

**V** por bytes. El Tv de la foto se lee de `[fp+0x162]` y se copia a `record+0xf6`; el factor
`+0x4b8` se lee del **objeto imager** (`r7`), no de `settings`. E25-16 llamó «settings+0x4b8» a ese
campo; la lectura real confirma el valor (1) pero **corrige el nombre**: es
`imager/config+0x4b8`.

---

## 3. Validación de punteros y direcciones

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA del firmware | `b60c845c…e56bb9` | binario |
| Código en físico `0x836d6fb6` | `91f80990` (original) | volcado 20-10 |
| Código en físico `0x836d7000` | `28125ffa85fe` (original) | volcado 20-10 |
| GOT `0x44022648` | `0x43ea5b4c` | volcado |
| GOT `0x44025dfc` | `0x43eee770` | volcado |
| GOT `0x440207e8` | `0x43f79f94` | volcado |
| GOT `0x44021ba8` | `0x43ea976c` | volcado |
| GOT `0x44024e58` | `0x43f6e5c2` | volcado |
| GOT `0x440253cc` | `0x43deb360` | volcado |
| `record A/B` mapeados y legibles | sí, 0x158 B cada uno; **todo 0** en reposo | volcado |
| `settings` mapeado | sí; `+0x162` = `0x15e8` (1/60) | volcado |
| `imager` mapeado | sí; `+0x4b8` = 1; `+0x504` = 2 | volcado |
| `cap` localizado | **no** | ver §2.2 |

No se usó ninguna dirección obtenida por búsqueda de patrones como si fuera un puntero confirmado. La
coincidencia de T048 en `0x83e19d20` **no** se reutiliza: en este volcado sus campos `+0x5c8`,
`+0x64c` y `+0x1198` están a cero y no se puede demostrar que sea el objeto vivo.

---

## 4. Tabla de valores observados

Volcado `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (1 GiB, cámara en marcha,
reposo, fw 3.21). **No es una foto.**

| Campo | Referencia E25-16 | Valor leído | Contexto | Evidencia |
|---|---|---|---|---|
| `record A+0xf6` (Tv) | `record+0xf6` | 0 | reposo; registro limpiado | **V** |
| `record A+0xc` (período) | `record+0xc` | 0 | ídem | **V** |
| `record A+0x20` (VTS) | `record+0x20` | 0 | ídem | **V** |
| `record A+0x1c` (suelo) | `record+0x1c` | 0 | ídem | **V** |
| `record A+0x64` (r5) | `record+0x64` | 0 | ídem | **V** |
| `record A+0x68` (frames) | `record+0x68` | 0 | ídem | **V** |
| `record A+0x6d` (ShutMode) | `record+0x6d` | 0 | ídem | **V** |
| `record B` (mismos campos) | — | 0 | ídem | **V** |
| `settings+0x162` (Tv) | `settings+0x162` | `0x15e8` = 1/60 | reposo, ajuste por defecto | **V** real |
| `imager+0x4b8` (factor) | `settings+0x4b8` | **1** | reposo | **V** real |
| `imager+0x504` (modo) | no documentado | **2** | reposo | **V** real |
| `gate B+0x8c` | no documentado | **0** | reposo | **V** real |
| `predicado+0x10` | no documentado | **0** | reposo | **V** real |
| `cap+0x11b0` (compuerta) | `cap+0x11b0` | **no leído** | `cap` no localizado | **N** |
| `cap+0x5c8` (bloque 48 B) | `cap+0x5c8` | **no leído** | `cap` no localizado | **N** |
| `cap+0x64c` (param SetExposure) | `cap+0x64c` | **no leído** | `cap` no localizado | **N** |

**Lo que falta y bloquea la decisión:** `record+0xc`, `record+0x1c`, `record+0x20`, `record+0x64`,
`record+0x68` y `record+0x6d` **durante o inmediatamente después de una foto**. Esos seis campos son
la entrada real del productor nativo y no se pueden sustituir por 4219/3891/0 sin convertirlos en una
suposición.

---

## 5. Instante y contexto de cada lectura

| Lectura | Instante | Contexto | Validez |
|---|---|---|---|
| GOT y objetos | 20-10-2026, servicio, cámara en marcha | reposo, sin foto desde el arranque | **V** para el mapa; **no** para la foto |
| `settings+0x162` | ídem | ajuste de reposo 1/60 | **V** real, pero no es la Tv de una foto |
| `record A/B` | ídem | memset del constructor; sin foto | **V** de que están a cero; **I** de que se deba a que no hubo foto |
| Emulación | 28-10-2026, PC | registro sintético con 3891/4219/4266, suelo 1, factor 1 | **V** de la función; **no** del sensor |
| Lecturas por telnet | **no realizadas** | cámara inaccesible | — |

No se afirma que un muestreo coincida con una instrucción de BIONZ. La ventana de la foto
(`0x437f8a50` → `0x436d6320`) es demasiado estrecha para un `dd` de telnet; la lectura viable es
**después** del disparo, sobre el registro que persiste hasta el siguiente `memset`.

---

## 6. Resultado de la comparación VTS 4219/4266

### 6.1 La cadena real del campo

```
settings+0x162 (Tv)
  └─ 0x437b4670 → record+0xf6

cap+0x5c8 (bloque de 48 B)
  └─ 0x437f892c/0x437f89bc: descriptor [r8+4] = cap+0x5c8
  └─ 0x437b43b4: memcpy 48 B a record+8
       record+0xc  = cap+0x5cc  (u32, período de línea)
       record+0x1c = cap+0x5dc  (u16, suelo)
       record+0x20 = cap+0x5e0  (u16, VTS)

cap+0x5e0 ← [descriptor+6]
  └─ 0x43846e00..12: r3 = [r5+0x3c]; ldrh r3,[r3,#6]; strh r3,[r4,#0x5e0]
  └─ 0x43844e80 (constructor grande) ← 0x437b5b14 ← 0x437b4e10
```

**V** por bytes. El valor no es una constante del binario: 4219 no aparece como `movw` ni como dato
del camino de foto; 4266 lo calcula `0x4385de94`, pero **solo lo llama la vista en directo**
(`0x437b285e`). La foto no llama a `0x4385de94`: usa el descriptor de modo.

### 6.2 Clasificación

| Hipótesis | Estado | Motivo |
|---|---|---|
| **A: `record+0x20 = 4219`** | **NO demostrada** | el registro está a cero en el único volcado real; no hay lectura de foto |
| **B: `record+0x20 = 4266`** | **NO demostrada** | 4266 es la salida de `0x4385de94`, que la foto no usa; no hay lectura del descriptor |
| **C: depende del modo/banco** | **NO demostrada** | el descriptor `[param+0x3c]+6` es data-driven; su productor no se identificó |

**Clasificación de cierre:** *valores distintos cuya causa todavía impide autorizar C3*. No se elige
4219 por proximidad a T047 ni 4266 por la función de la vista en directo.

### 6.3 Por qué importa

La ley medida T046/T047 es `E = (4219 − r5)·15,2 µs`. Si el productor nativo usa 4266 y escribe
`r5 = 4266 − líneas`, la exposición física queda `(4219 − r5)·15,2 = (líneas − 47)·15,2`, es decir
**47 líneas (0,71 ms) más corta**. A 1/250 eso es −17,9 %; a 1/60, −4,3 %; a 1/4000, no representable
(negro). Por eso el campo es crítico y no se puede sustituir a ciegas.

---

## 7. Resultado de la emulación con datos reales

Se ejecutó la función **del firmware** `0x4383fa40` en Unicorn con:

- `record+0xc = 3891` (período Q8; **hipótesis** de 15,2 µs/línea, no leído en foto);
- `record+0x1c = 1` (suelo; en el volcado el registro está a cero, pero el campo `cap+0x5dc` que lo
  alimenta es un byte 0/1 y el registro de foto normal vale 1 en T032/T046);
- `record+0x20 = 4219` o `4266`;
- `record+0xf6` = código Tv de 1/4000 (`0x1bf7`), 1/250 (`0x17f7`) y 1/60 (`0x15e8`);
- `imager+0x4b8 = 1` (leído en el volcado);
- predicado `0x43a12ca8` = 0 (sin cuadro extra) o 1 (cuadro extra).

### 7.1 Tabla obligatoria

| Velocidad | Tv real | Período | VTS real | r5 nativo | Tiempo previsto (ley 4219) | Diferencia |
|---|---:|---:|---:|---:|---:|---:|
| 1/4000 | `0x1bf7` | 3891 (H) | 4219 (H) | 4203 | 0,243 ms | −2,7 % vs 0,25 ms |
| 1/4000 | `0x1bf7` | 3891 (H) | 4266 (H) | 4250 | **no representable** | negro (r5 > 4219) |
| 1/250 | `0x17f7` | 3891 (H) | 4219 (H) | 3956 | 3,998 ms | −0,1 % vs 4,0 ms |
| 1/250 | `0x17f7` | 3891 (H) | 4266 (H) | 4003 | 3,283 ms | **−17,9 %** |
| 1/60 | `0x15e8` | 3891 (H) | 4219 (H) | 3122 | 16,674 ms | 0,0 % |
| 1/60 | `0x15e8` | 3891 (H) | 4266 (H) | 3169 | 15,960 ms | −4,3 % |

(H) = hipótesis de trabajo, no lectura física. La Tv de 1/60 (`0x15e8`) sí se leyó en el objeto de
ajustes del volcado; las de 1/4000 y 1/250 son los códigos estándar de E25-11.

### 7.2 El predicado de cuadro extra

En el volcado real `[0x83deb360+0x10] = 0`. La función `0x43a12ca8` devuelve 1 para 0 o 1 y 0 para
≥ 2. Con el valor observado (0), el productor nativo ejecuta `r8 += r6` y escribe:

| Velocidad | VTS | r5 con cuadro extra | frames | ¿Representable? |
|---|---:|---:|---:|---|
| 1/4000 | 4219 | 8422 | 1 | **no** |
| 1/250 | 4219 | 8175 | 1 | **no** |
| 1/60 | 4219 | 7341 | 1 | **no** |

El arnés de E25-16 fija el predicado a 0; es una **suposición no verificada**. Si el predicado real
durante la foto también es 1, C3 no puede usar el productor nativo tal cual: `r5 > VTS` y la
exposición sería negra o indefinida. Este es un bloqueo **nuevo** de T052-A.

### 7.3 Escrituras adicionales

Además de `+0x64` (r5), `+0x68` (frames), `+0x6a`, `+0x6c`, `+0x6d` (ShutMode) y `+0xf0` (líneas),
la función escribe `+0xd8`, `+0xda` y `+0xdc` con `factor · (resto + frame)`. E25-16 no las incluía.
La emulación confirma que **no escribe fuera del registro** (solo pila y registro), pero refuerza que
C3 debe trabajar sobre una copia y no sobre el registro global.

---

## 8. Comparación de r5 contra T047

| Velocidad | r5 nativo (4219) | r5 T047 | Δ | Tiempo nativo | T047 | Δ tiempo |
|---|---:|---:|---:|---:|---:|---:|
| 1/4000 | 4203 | 4203 | 0 | 0,243 ms | 0,24 ms | +1,3 % |
| 1/250 | 3956 | 3956 | 0 | 3,998 ms | 4,03 ms | −0,8 % |
| 1/60 | 3122 | 3122 | 0 | 16,674 ms | 16,75 ms | −0,5 % |

La función nativa con VTS 4219 reproduce T047 dentro de ±1 línea. La emulación **no** prueba el
sensor: el tiempo es la ley medida, no una nueva medición.

**1/8000 (no solicitada en la fase física, pero necesaria para el objetivo ±5 %):** 125 µs = 8,22
líneas. Con truncamiento (`__aeabi_uidiv`) son 8 líneas = 121,6 µs (**−2,7 %**); con techo serían 9
líneas = 136,8 µs (+9,4 %). El firmware trunca, así que el sesgo esperado es −2,7 %, dentro de ±5 %
**solo en cuantización**; la calibración absoluta (±20–25 % de T050) sigue dominando y no se corrige
con la fórmula.

---

## 9. Análisis de la compuerta `cap+0x11b0`

### 9.1 Quién la escribe

El escritor es `0x437b3b08` (sub-objeto `cap+0x1198`, campo `+0x18`):

```
437b3b54  ldr.w r2,[r3,#0x504]     ; objeto imager/config (0x43ea976c)
437b3b58  cmp   r2,#3
437b3b5a  bne   0x437b3b60
437b3b5c  movs  r3,#1
437b3b5e  b     0x437b3b62
437b3b60  movs  r3,#0
437b3b62  strb  r3,[r4,#0x18]      ; gate = ([imager+0x504] == 3)
437b3b64  ldr   r3,[pc,#0x16c]
437b3b66  ldr.w r3,[r8,r3]
437b3b6a  ldrb.w r3,[r3,#0x8c]     ; objeto 0x43f6e5c2
437b3b6e  cmp   r3,#1
437b3b70  beq   0x437b3b78         ; 1 -> gate = 1
437b3b72  cmp   r3,#2
437b3b74  bne   0x437b3b7a         ; otro -> conserva el primer valor
437b3b76  subs  r3,#2              ; 2 -> gate = 0
437b3b78  strb  r3,[r4,#0x18]
```

**V** por bytes. La compuerta es una función de dos modos, no un flag de usuario:

```
gate = ([0x43ea976c+0x504] == 3) || ([0x43f6e5c2+0x8c] == 1)
       y [0x43f6e5c2+0x8c] == 2 la fuerza a 0
```

### 9.2 Valores observados

| Entrada | Valor en el volcado | Efecto |
|---|---:|---|
| `imager+0x504` | **2** | primer término 0 |
| `gate B+0x8c` | **0** | no abre ni fuerza; gate = 0 |
| `cap+0x11b0` | **0** (deducido) | coincide con T046/T047 (compuerta cerrada, r5=1) |

La deducción es **V** para las entradas y **I** para el valor de la compuerta (no se leyó `cap`). El
resultado es coherente con la foto medida: en T046/T047 la compuerta estaba cerrada.

### 9.3 Semántica

`imager+0x504` es un **byte de propiedad** escrito por un setter dedicado (`0x43802950`, que copia
`[r0+8]` a `[global+0x504]`). La tabla de propiedades `0x43fff7a8` le asocia el id `0x4070`; la tabla
de despacho LIRO de `av-cam` asocia `0x406f` al mismo handler (`0x43802949`). El **nombre funcional**
de esa propiedad (¿tipo de obturador?, ¿modo de captura?) **no está demostrado**. Lo único que se puede
afirmar es que la compuerta se abre cuando esa propiedad vale 3.

**No se recomienda C1** (activar la compuerta) con la evidencia actual: sería reutilizar un modo cuyo
significado no está cerrado y afectaría a todo el constructor normal, no solo a la foto silenciosa.

---

## 10. Auditoría offline de C3

### 10.1 Contrato lógico

Punto de inserción: `0x438c82a0`, justo después de `bl 0x437f8a50` y antes de `0x438c830c`
(`bl 0x436d6320`). Es la secuencia de foto `0x438c828c`, llamada solo desde `0x43b1e82a` y
`0x43b1e85c`; la vista en directo usa otro camino (`0x438cc868`). **V**.

Pasos:

1. Guardar `r0-r3`, `r12`, `lr` y la pila necesaria.
2. `rec = 0x4383fb6c([cap+0x1c0], [cap+0x1b8])`; `set = 0x4383fbc4(...)`.
3. Copiar **0x158 B** del registro a un *scratch* verificado (no global).
4. Ejecutar `0x4383fa40(scratch, set)`.
5. Leer `r5 = [scratch+0x64]`, `frames = [scratch+0x68]`, `sm = [scratch+0x6d]`,
   `lines = [scratch+0xf0]`.
6. Comprobar: `2 ≤ r5 < [scratch+0x20]`, `r5 ≤ 4219` (ley física), `record+0xc != 0`,
   `record+0x20` en rango, `record+0xf6` coherente con `settings+0x162`, predicado sin cuadro extra
   (o `frames == 0` y `r5 < VTS`).
7. Si pasa, copiar 12 B de `scratch+0x64` a `cap+0x64c` (r5, frames, +6, +8, ShutMode). Si no,
   **no escribir nada** y volver a `0x438c82a4`.

### 10.2 Tamaño y campos

| Concepto | Valor | Base |
|---|---|---|
| Tamaño de la copia | **0x158 B** | el constructor hace `memset(record,0,0x158)` y la función escribe hasta `+0xdc` |
| Campos leídos | `+0xc` (u32), `+0x1c` (u16), `+0x20` (u16), `+0xf6` (u16) | **V** |
| Campos escritos | `+0x64` (u32), `+0x68` (u16), `+0x6a` (u16), `+0x6c` (u8), `+0x6d` (u8), `+0xf0` (u32), `+0xd8` (u16), `+0xda` (u16), `+0xdc` (u16) | **V** |
| Llamadas auxiliares | `0x4355faf0` (uidiv), `0x4382fac8`/`0x4382fa94` (Tv→µs), `0x43a12ca8` (predicado), `0x4355fd4c` (resto) | **V** |
| Efectos externos | ninguno observado en emulación (solo pila y registro) | **V** emulación |
| Predicado | lee `[0x43deb360+0x10]`; puede sumar un cuadro | **V** lectura; valor de foto **N** |

### 10.3 Aislamiento

La copia a *scratch* evita las escrituras al registro global, incluidas `+0xd8..+0xdc`, que E25-16 no
había listado. La emulación no muestra escrituras fuera del registro ni de la pila. **Pero** el
predicado lee un global y su valor cambia el resultado; el aislamiento del registro no basta si el
predicado Devuelve 1. C3 debe tratar ese caso como fallo y no escribir `cap+0x64c`.

### 10.4 Qué debe permanecer intacto

- `cap+0x64c+4/+6/+8` (frames, cero, auxiliar): se copian del *scratch* solo si la función los cambió;
  el original de `0x437f8a50` ya los contiene.
- El resto de `cap+0x64c..0x65b` (los 16 B que copia `0x4383fd6c`) no se toca más allá de los 12 B
  modificados.
- El registro global, `settings`, `imager` y la cola de la captura no se modifican.
- `cap+0x6bc` (bloque de `+0x30`) no se toca.

---

## 11. Riesgos

| Riesgo | Gravedad | Mitigación |
|---|---|---|
| VTS 4266 en la foto | alta: −17,9 % a 1/250, negro a 1/4000 | leer `record+0x20` en B0; no ejecutar C3 si no es 4219/coherente |
| Predicado de cuadro extra = 1 | alta: r5 > VTS, exposición inválida | leer `[0x43deb360+0x10]` en B0; abortar si < 2 |
| Banco de registro equivocado | alta: r5 de otro contexto | leer los dos registros; identificar por Tv/r5 no nulos |
| `cap` no localizado | media: no se puede leer `cap+0x11b0`/`cap+0x64c` | usar el registro como proxy; localizar `cap` en B0 o bloquear C1 |
| *Scratch* no verificado | media: corrupción de datos | reservar una región BSS verificada, volcarla antes/después |
| Ventana de interrupción | media: la copia puede intercalarse | sección crítica breve; guardián y reversión |
| Calibración absoluta ±25 % | media: no se cierra con C3 | luz controlada y referencias por tanda |
| >1 cuadro / bulb / 30 s | alta: fuera de la ruta | no probar; límite de un cuadro |

---

## 12. Veredictos A–T

| # | Pregunta | Veredicto | Tipo |
|---|---|---|---|
| A | ¿Se confirmó el mapa de direcciones runtime? | **SÍ para record/settings/imager/gate/predicado; NO para `cap`** | estático + volcado real |
| B | ¿Se identificó el registro de fotografía correcto? | **SÍ**: A/B por GOT y `0x4383fb6c`; el banco activo se decide en ejecución | estático; foto **N** |
| C | ¿Se identificó el objeto settings correcto? | **SÍ**: `0x43f79f94`; Tv en `+0x162` | estático + volcado |
| D | ¿Se leyó físicamente el Tv real de la cámara? | **NO** en una foto; sí `0x15e8` (1/60) en reposo | volcado de reposo |
| E | ¿Se leyó el período de línea real? | **NO** | falta lectura de foto |
| F | ¿Se leyó el VTS real? | **NO** | falta lectura de foto |
| G | ¿El VTS coincide con 4219? | **NO demostrado** | falta lectura |
| H | ¿La diferencia frente a 4266 tiene explicación demostrada? | **NO** | falta lectura del descriptor |
| I | ¿Se confirmó el factor `settings+0x4b8`? | **SÍ, como `imager+0x4b8` = 1** (nombre corregido) | volcado real |
| J | ¿Se confirmó el valor de `cap+0x11b0`? | **NO** (sí sus entradas: 2 y 0 → gate 0) | estático + volcado |
| K | ¿Se identificó la semántica de esa compuerta? | **PARCIAL**: mecanismo sí; significado del modo 3, no | estático |
| L | ¿Se estableció la vigencia temporal para una captura concreta? | **NO** | falta lectura de foto |
| M | ¿La emulación nativa produce r5 coherente con los parámetros leídos? | **SÍ con 4219 y predicado 0; NO con el predicado observado (1)** | emulación |
| N | ¿C3 puede usar el productor sin alterar el registro global? | **SÍ con copia a scratch**, sujeto a VTS/predicado | estático + emulación |
| O | ¿Se identificaron los efectos secundarios relevantes? | **SÍ**: `+0xd8..+0xdc` incluidos; predicado global | emulación + bytes |
| P | ¿Existe evidencia suficiente para diseñar T052-B? | **SÍ**: B0 de solo lectura + B1 condicionada | estático |
| Q | ¿Existe evidencia para ejecutar T052-B sin nuevas investigaciones estáticas? | **NO**: falta el *scratch* verificado y los bytes de la cueva; B0 debe ir primero | falta de evidencia |
| R | ¿Se realizó alguna escritura de memoria en la cámara? | **NO** | — |
| S | ¿Se modificó firmware persistente? | **NO** | — |
| T | ¿Se consiguió una exposición autónoma físicamente validada? | **NO** | — |

Los **NO** de D–H, J, L y Q son lecturas que no se pudieron obtener, no contradicciones de la fórmula.
El **NO** de M con el predicado 1 sí es una contradicción con la suposición del arnés: el único estado
real medido activa el cuadro extra.

---

## 13. Decisión sobre T052-B

**No se ejecutó T052-B.** El diseño queda preparado en dos fases, y la segunda no se autoriza hasta
que la primera pase.

### T052-B0 — solo lectura (obligatoria, sin parches)

1. Verificar fw 3.23 y los bytes originales de T050 (`91f80990`, `28125ffa85fe`).
2. Modo M, ISO fijo, RAW+JPEG, trípode, escena fija, sin parche RAM.
3. Para 1/4000, 1/250 y 1/60: fijar la velocidad, esperar a que se estabilice, disparar una foto
   normal y leer **inmediatamente** los dos registros:
   - `0x83ea5b4c` y `0x83eee770`, campos `+0xf6`, `+0xc`, `+0x1c`, `+0x20`, `+0x64`, `+0x68`,
     `+0x6d`, `+0xf0`, `+0xd8..+0xdc`;
   - `settings 0x83f79f94 + 0x162`;
   - `imager 0x83ea976c + 0x4b8`, `+0x504`;
   - `gate B 0x83f6e5c2 + 0x8c`;
   - `predicado 0x83deb360 + 0x10`.
4. Repetir la lectura inmediata del mismo objeto: los valores deben coincidir o documentar la
   transición.
5. Guardar los bytes en el PC; borrar el temporal de la cámara.

**Criterios de parada:** `record+0x20` distinto de 4219/4266; período distinto de 3891; predicado
`< 2`; `record+0xf6` distinto de `settings+0x162`; cualquier lectura incoherente entre los dos bancos.

### T052-B1 — C3 en RAM (solo si B0 pasa)

- Aplicar la cueva C3 **solo en RAM**, con guardián y reversión independiente.
- Verificar los bytes originales antes y después; apagar/enciendo revierte.
- Velocidades iniciales: 1/4000, 1/250, 1/60. Después, si procede: 1/8000, 1/1000, 1/30.
- **No** 1/15, bulb ni 30 s.
- Capturas RAW comparables; medir exposición por filas y absoluta con luz estable.
- Criterios: `r5` nativo = esperado ±1 línea; exposición ±5 % del objetivo; uniformidad por filas
  ±5 %; Live/Video/AF sin cambios; reversión verificada.
- Abortar si `r5 < 2`, `r5 ≥ VTS`, `r5 > 4219`, predicado de cuadro extra, o cualquier lectura
  incoherente.

**Si B0 da 4266:** no ejecutar C3. Hay que corregir la interpretación (47 líneas) o rediseñar C3 para
usar la salida `lines` (`record+0xf0`) con la ley física de 4219; eso exige una nueva decisión estática.
**Si B0 da predicado 1:** no ejecutar C3; investigar el cuadro extra antes.

---

## 14. Entregables, pruebas y límites

- **Informe:** este documento.
- **Evidencia:** `analysis/t052-a/lecturas.json` (GOT, objetos, valores del volcado y emulación).
- **Lector:** `scripts/t052_a_readonly.py` (solo lectura; `--protocol` imprime el protocolo B0).
- **Pruebas:** `tests/test_t052_a_parametros.py` — **22 pruebas**.
- **Regresión:** `tests/test_e25_14_exposicion.py`, `tests/test_e25_15_shutmode.py`,
  `tests/test_e25_16_r5_autonomo.py` + T052-A = **81 pruebas verdes**.
- **Límites:** no hay lectura de foto; el VTS y el período son hipótesis; el predicado de foto es
  desconocido; `cap` no se localizó; la emulación no prueba el sensor; la calibración absoluta ±25 %
  sigue abierta.

**Comando:**

```bash
python3 -m pytest tests/test_e25_14_exposicion.py tests/test_e25_15_shutmode.py \
  tests/test_e25_16_r5_autonomo.py tests/test_t052_a_parametros.py -q
python3 scripts/t052_a_readonly.py            # regenera analysis/t052-a/lecturas.json
python3 scripts/t052_a_readonly.py --protocol # protocolo T052-B0
```
