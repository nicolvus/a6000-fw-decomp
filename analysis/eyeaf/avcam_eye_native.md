# Eye AF nativo en la A6000 — demostración estática sobre `av-cam.bin` (BIONZ, fw3.21)

Autor: agente `avcam_eye_native` · fecha 26-11-2026 · **solo análisis estático** (sin cámara, sin
firmware ejecutado, sin RAM).

* Binario: `analysis/rea-independent/input/av-cam.bin`, cargado en **`0x43541000`** (base ya
  verificada en el proyecto: `vaddr = 0x43541000 + offset`; `.text` = `0x43541000`–`0x44026da4`).
* Herramientas propias (en `analysis/eyeaf/avcam_eye_native/`): `avdis.py` (desensamblador Thumb-2
  anotado con resolución del idiomático `ldr rX,[pc,#k]`+`add rX,pc`), `sweep.py`, `sweep_eyes.py`,
  `fieldscan.py`, `index_branches.py`, `refs_pic.py`, `blfind.py`, `find_pic_refs.py`.
* Cifras del barrido: **4.975.565 instrucciones** decodificadas con salto de huecos, índice de
  **420.003 ramas** y **37.406** destinos PIC resueltos (ficheros `branches.json` y `refs_pic.json`).
* Marcas: **VERIFICADO** = bytes/instrucciones citadas y leídas; **INFERENCIA** = lectura semántica
  del código sin prueba de ejecución; **NO_VERIFICADO** = límite declarado.

---

## 0. Respuesta corta

La A6000 **sí tiene detección de ojos nativa** —existe un driver de *eye detection* en la biblioteca
`Camera::FC` (`FC/Drv/fc_drv_edt.cpp`, `::ProcessEdt::StartEdt`, servicio `idt_edt_start`) y un
consumidor propio en el módulo `[CAMERA_MAIN_FC]` (`0x437b7200`)—, pero **el ojo solo se convierte
en área de AF dentro del manejador de respuesta de una petición de AF/táctil**
(`0x437b7ea0` = `ReplyForTouchShutter`). El **único camino conocido** hacia `0x437b7200` es ese
manejador de *respuesta*: se ejecuta cuando el subsistema de AF emite una petición (pulsación S1,
AF-C activo, toque). Ni `0x437b6ea4` ni `0x437b7200` ni `0x43aef890` ni `0x437b7ea0` tienen otra
arista de entrada en todo el binario (quien invoca `0x437b6670` no aparece en `av-cam.bin`:
NO_VERIFICADO). De ahí
que el Eye AF «solo actúe mientras se mantiene pulsado»: al soltar, cesan las peticiones, cesa
`0x437b7598`, y el estado de ojos caduca con un temporizador OSAL de un disparo
(`0x437b74a4` → `0x437b7778`, período = `u16[cfg+6] × 1000 ms`).

---

## 1. Cadena completa (VERIFICADO salvo donde se indica)

```
IDT (servicio de detección, otro binario/tarea)
   ▲ idt_edt_start (opcode 8)                      0x43a303f8  (llamada en 0x43a0a55e)
   │
Camera::FC  ::ProcessEdt::StartEdt(DataMonFace&, CallBackEvent&)
   0x43a0a47c            ← único llamador 0x43b7587e
   0x43b75836            (gate: [fcctx+0x1d3]!=0 y 0x43b780c4(...)!=0)
   ← único llamador 0x43a06700, dentro de la función 0x43a06428
     (fichero de aserción "./FC/Alg/fc_alg_select_key.h", sitio 0x43a0640c)
     = **selección de objetivo AF**

bloque de resultado FC  r1 (= 0x439fd844())
   +0x1c  nº de caras              (0x437b6ed0)
   +0x24/+0x26/+0x28/+0x2a  rect de la cara (0x437b6ee4-0x437b6ef4)
   +0x56/+0x58  ojo #1 (x,y)       (0x437b6fd8/0x437b6fdc)
   +0x5a/+0x5c  ojo #2 (x,y)       (0x437b6ffc/0x437b7004)
   +0x5f        válido ojo #1      (0x437b6fca)  ← «lc flag»
   +0x60        válido ojo #2      (0x437b6fee)  ← «lc flag»

[CAMERA_MAIN_FC] 0x437b6ea4   (this, fc_face_block, obj_block, ctx, &flag)
   ctx+0xde/0xdf = válidos;  ctx+0xe0/e2/e4/e6 = coordenadas;  ctx+0xe8 = nº ojos
   ctx+0x8.. 0xa8 = 8 registros de área de 0x14 B (x,y,w,h + clase + flags)

0x437b7598 (this, ctx, modo, ·)   ← único llamador 0x43aef9ca (cola de 0x43aef890)
   0x437b7200 (this+0x38, ctx, modo)  ← SOLO 2 sitios: 0x437b7682 y 0x437b76d4
        convierte los ojos en registros de área (ctx+8 + (i-1)*0x14)
   0x437b74a4 (ctx)  arma temporizador OSAL de un disparo, período (u16[cfg+6]×1000)

0x437b7ea0  ReplyForTouchShutter(this, reply)     ← thunk 0x43aef72e ← 0x437b668c
   reply+0xc ← memcpy(0xec) de 0x43eb3c18 (= ctx de 0x437b7598 +2)   0x437b7f86
   reply enviado por el método virtual de this+0xb0 (0x43ad6034)      0x437b7fba

0x437b7fe4  copia de estado de áreas: A (0x43eb3af6) → buffer del llamador
   llamada desde 0x4378f6a6, dentro de Imaging::VD_Drive ([CAMERA_MAIN_SYNC]) = **cada VD**
```

Toda la cadena de ojos nace en el **servicio IDT** y muere en ese manejador: no hay ningún camino
que llame a `0x437b6ea4`/`0x437b7200` desde el bucle de live view (los 5 sitios de `0x437b6ea4` y
los 2 de `0x437b7200` están todos dentro de `0x43aef890`, y este solo se llama desde `0x437b7ea0`,
sitio `0x437b7f02`; **VERIFICADO** con `blfind.py` sobre toda la imagen).

---

## 2. Estructuras (VERIFICADO por los desplazamientos leídos/escritos)

### 2.1 Registro de área de AF del módulo — objeto B `0x43eb3c16`

| off | tipo | contenido | evidencia |
|---|---|---|---|
| `+0x08 + i*0x14` (i=1..8) | u16 | x del área | `0x437b73e8`, `0x437b745e` |
| `+0x0a` | u16 | y | `0x437b73e4`, `0x437b7456` |
| `+0x0c`/`+0x0e` | u16 | ancho / alto | `0x437b73e0`/`0x437b73e2` |
| `+0x10` | u32 | id del objeto/cara (copia de `[ctx+0x10]`) | `0x437b73ec` |
| `+0x14`,`+0x15` | u8 | clase / flag (de `face+0x64`, `face+0x4c`) | `0x437b6efe`, `0x437b6f06` |
| `+0x16`,`+0x1a` | u8 | flags (`face+0x61`, `face+0x68/69`) | `0x437b6f0c`, `0x437b6f40` |
| `+0x18` | u8 | estado (`face+0x48`/`+0x50` → 1/2/0) | `0x437b6f24` |
| `+0x19`,`+0x1b` | u8 | flags recalculados por `0x437b7598` | `0x437b7612`, `0x437b7634` |
| `+0xd6` | u8 | «hay detección nueva» (salida de `0x43aef820`) | `0x437b6ecc` |
| `+0xd7` | u8 | nº de áreas (máx. 8) | `0x437b6ede`, `0x437b73ba` |
| `+0xdb` | u8 | clase de tamaño de imagen (1/2/3) | `0x437b704e`, `0x437b7340` |
| `+0xde`/`+0xdf` | u8 | **validez ojo #1 / ojo #2** | `0x437b6eac`/`0x437b6eb2` (limpia), `0x437b6fce`/`0x437b6ff2` (copia) |
| `+0xe0`/`+0xe2` | u16 | ojo #1 x,y | `0x437b6fdc`, `0x437b6fea` |
| `+0xe4`/`+0xe6` | u16 | ojo #2 x,y | `0x437b6ffc`, `0x437b700e` |
| `+0xe8` | u8 | nº de ojos añadidos (2 = ambos) | `0x437b73be`, `0x437b75be` |

### 2.2 Objeto A `0x43eb3af6`

Mismo formato (lo copia `0x437b7fe4` leído con base `0x43eb3af8`), pero **no tiene ningún escritor
en `av-cam.bin`**: sus 6 referencias PIC son todas lecturas (`0x437b7e46`, `0x437b7fe8`,
`0x437b803e`, `0x437b80b0`, `0x437b818e`). **NO_VERIFICADO** quién lo llena; solo se sabe que se
copia cada VD hacia el consumidor de `0x4378f6a6`.

### 2.3 Respuesta táctil `0xf8` B y mensaje de notificación `0xfe` B

* `0x437b7ea0`: `reply[5..8]` = flags (face/obj/af), `reply[0xc..0xf8)` = copia de `0xec` B del
  objeto B (`memcpy` en `0x437b7f86`, fuente `0x43eb3c18`, tamaño `0xec` = constante en `0x437b7f7c`).
  Doble búfer: `0x43eb3720` y `0x43eb3818` (0xf8 B cada uno, `mla` en `0x437b6688`), con selector
  `0x43f9a563` (`0x437b6678`/`0x437b669a`).
* Notificación FC: `0x437b67b8` copia `0xec` B de **A o B** según el signo de `[mbox+1]`
  (`0x437b67d4`–`0x437b67fa`), con puntero en `[mbox+0x10]`.

---

## 3. Pregunta 1 — ¿quién escribe los datos de ojo que valida el chequeo?

**Respuesta: el módulo `[CAMERA_MAIN_FC]` los copia, en `0x437b6ea4`, desde el bloque de resultado
de `Camera::FC`; el dato original se produce en la detección de ojos que `Camera::FC` pide al
servicio IDT (`ProcessEdt::StartEdt` → `idt_edt_start`).** La instrucción concreta que escribe
`+0x56..+0x60` dentro de ese bloque **no se ha localizado** (el bloque lo devuelve `0x439fd844` y su
relleno ocurre dentro de `Camera::FC`/IDT): **NO_VERIFICADO**.

* **Productor inmediato (VERIFICADO)**: `0x437b6ea4` limpia y rellena `ctx+0xde..0xe8`:

```
0x437b6ea4  push.w {r0,r1,r2,r4,r5,r6,r7,r8,sb,sl,fp,lr}
0x437b6eac  strb.w sb,[r3,#0xde]      ; sb = 0
0x437b6eb2  strb.w sb,[r3,#0xdf]
...
0x437b6fc2  ldrb.w r1,[r7,#0x5f]      ; válido ojo #1 (bloque FC)
0x437b6fce  strb.w r1,[r6,#0xde]      ; -> ctx+0xde
0x437b6fd8  ldrh.w r1,[r7,#0x56]      ; x ojo #1
0x437b6fdc  strh.w r1,[r6,#0xe0]
0x437b6fe0  ldrh.w r1,[r7,#0x58]      ; y ojo #1
0x437b6fea  strh.w r1,[r6,#0xe2]
0x437b6fee  ldrb.w r1,[r7,#0x60]      ; válido ojo #2
0x437b6ff2  strb.w r1,[r6,#0xdf]
0x437b6ffc  ldrh.w r1,[r7,#0x5a]      ; x ojo #2
0x437b7000  strh.w r1,[r6,#0xe4]
0x437b7004  ldrh.w r1,[r7,#0x5c]      ; y ojo #2
0x437b700e  strh.w r1,[r6,#0xe6]
```
  con la guarda `0x437b6f54 cmp.w sb,#0 / 0x437b6f58 bne 0x437b7012`: el par de ojos se copia
  **solo en la primera iteración** (cara principal).

* **Origen (VERIFICADO)**: `r7` = 2.º argumento de `0x437b6ea4` = valor devuelto por `0x439fd844`
  en `0x437b7eb8`, es decir, el bloque de detección de `Camera::FC` (misma biblioteca cuyos ficheros
  son `FC/Alg/fc_alg_exif_face_data.cpp` `0x43cf0737`, `FC/Alg/fc_alg_blink.cpp` `0x43cf071f`,
  `FC/Drv/fc_drv_edt.cpp` `0x43cf6fd9`).
* **Productor remoto (VERIFICADO)**: la detección de ojos se **pide** al servicio IDT desde
  `Camera::FC`:
  * cadenas: `::ProcessEdt::StartEdt(const Camera::FC::DataMonFace&, const Camera::FC::CallBackEvent&)`
    `0x43cf6f80`, `FC/Drv/fc_drv_edt.cpp` `0x43cf6fd9`, `idt_edtsa_stop() rtn: %d` `0x43cf6fef`,
    `idt_edt_get_result rtn=%d` `0x43cf7008`, **`EyeDetection`** `0x43cf7022`,
    `idt_edt_start rtn=%d` `0x43cf702f`.
  * código: `0x43a0a47c` arma la petición (rect del `DataMonFace` en `0x43a0a4e2`–`0x43a0a536`),
    llama `0x43a303f8` en `0x43a0a55e`, y registra `idt_edt_start rtn=%d` en `0x43a0a570`.
  * **NO_VERIFICADO**: el interior de `0x43a303f8` y del servicio IDT (otra tarea del paquete de
    firmware); el binario solo muestra la petición y el retorno.

* **Llamador periódico**: **ninguno en el bucle de live view** (VERIFICADO).
  * `0x437b6ea4` ← 5 sitios, todos en `0x43aef890` (`0x43aef8ca`, `0x43aef94e`, `0x43aef964`,
    `0x43aef9a2`, `0x43aef9b8`).
  * `0x43aef890` ← **un solo** sitio: `0x437b7f02`, dentro de `0x437b7ea0` (`ReplyForTouchShutter`).
  * `0x437b7ea0` ← `0x43aef72e` (thunk `b.w`) ← `0x437b668c` (función `0x437b6670`).
  * Lo único «periódico» es el **temporizador de caducidad** `0x437b74a4`/`0x437b7778`
    (§5) y la copia por VD de `0x437b7fe4` desde el objeto A (`0x4378f6a6`, dentro de
    `Imaging::VD_Drive` de `[CAMERA_MAIN_SYNC]`).

---

## 4. Pregunta 2 — ¿qué es el «lc flag» y qué hace VÁLIDO el dato de ojo?

* **Comparación exacta (VERIFICADO)**: cuatro sitios, dos por ojo (ruta de 2 ojos y ruta de 1 ojo):

```
0x437b723e  ldrb.w r3,[r4,#0xdf]      ; modo 2 ojos
0x437b7242  cmp    r3,#1
0x437b7244  bne    0x437b7260          ; != 1  -> log
0x437b7260  ldr    r3,[pc,#0x228]      ; 0x004ef6d8
0x437b7268  add    r3,pc               ; 0x43ca6944 = "[CAMERA_MAIN_FC]: Eye data is invalid, but lc flag is true."
0x437b726c  bl     0x437b7158          ; logger del módulo

0x437b7274  ldrb.w r3,[r4,#0xde]
0x437b7278  cmp    r3,#1
0x437b727a  bne    0x437b729c          ; != 1  -> log (0x437b72a6)
```
  Equivalentes en el modo de un solo ojo: `0x437b72c0`/`0x437b72c6` (ojo 2) y
  `0x437b72fa`/`0x437b7300` (ojo 1), con sitios de log `0x437b72ee` y `0x437b7326`.

* **Qué es el flag**: `[ctx+0xde]`/`[ctx+0xdf]` = **byte de validez del ojo #1/#2**, copiado sin
  transformación de `face_block+0x5f`/`+0x60` (`0x437b6fca`→`0x437b6fce`, `0x437b6fee`→`0x437b6ff2`).
  El productor solo copia coordenadas cuando ese byte es distinto de 0 (`0x437b6fd6 cbz`), luego
  `1` = «hay ojo» y cualquier otro valor = «no hay dato». **VERIFICADO**.
* **Qué hace VÁLIDO el dato**: `[ctx+0xde] == 1` (ojo 1) y `[ctx+0xdf] == 1` (ojo 2). No se comprueba
  ningún rango de coordenadas: si el flag vale 1, las coordenadas `+0xe0..+0xe6` se usan tal cual.
  **VERIFICADO** (`0x437b7242`, `0x437b7278`, `0x437b72c4`, `0x437b72fe`).
* **Sobre el nombre `lc`**: el log se emite cuando el flag **no** vale 1 (`0x437b7244 bne`), luego «lc
  flag» no puede ser el propio `[ctx+0xdf]` —esa lectura es la del **dato**, y s138 la identificó
  como el flag leído, pero su valor 1 es la condición de *validez*, no la del aviso—. El único estado
  «LC» que gobierna esta rama es el objeto de `Camera::LC` en `[this+0x38]`:
  `[this+0x38]+0x56` (bit de «ojo seleccionable») y `+0x55` (1 ojo / 2 ojos), leídos en
  `0x437b765c`–`0x437b766c` y `0x437b76b0`–`0x437b76bc`. Clases RTTI del subsistema, **VERIFICADAS**
  en bytes: `N6Camera2LC15IAfAreaPriorityE` `0x43cb6032`,
  `N6Camera2LC19CAfAreaPriorityGpmaE` `0x43cb6050`, `N6Camera2LC12CCoordAfAreaE` `0x43ccb2cd`,
  `N6Camera2LC15CPAFCoordAfAreaE` `0x43ccb2e8`, `N6Camera2LC17CPafStateEyeStartE` `0x43ca7b3a`.
  **INFERENCIA**: «lc flag» = bit del subsistema `Camera::LC` que declara que el ojo existe/se
  selecciona; el mensaje avisa de la incoherencia «LC dice que hay ojo, el dato no es válido».

---

## 5. Pregunta 3 — ciclo de vida: qué enciende, qué apaga, qué mantiene

| elemento | sitio | efecto | marca |
|---|---|---|---|
| **Enciende (petición de ojo a IDT)** | `0x43b75848` `ldrb.w r3,[r4,#0x1d3]` + `0x43b75850 cbz` | si `fcctx+0x1d3 == 0` no se pide detección de ojos | VERIFICADO |
| | `0x439fe636` `strb.w r7,[r3,#0x1d2]` / `0x439fe642` `strb.w r7,[r3,#0x1d3]` | el handler de parámetros de FC pone a 1 los dos flags de detección (junto con `+0x1c8..+0x1d6`) | VERIFICADO (escritura); semántica NO_VERIFICADO |
| | `0x43b75860` `bl 0x43b780c4` | segunda condición (devuelve 0 → no se pide) | VERIFICADO (llamada); semántica NO_VERIFICADO |
| | `0x43b7587e` `blx 0x43a0a47c` | `ProcessEdt::StartEdt` → `idt_edt_start` | VERIFICADO |
| | `0x43b75876` `strb.w r3,[r4,#0x65]` (`r4 = fcctx+0x2780`) | marca «EDT pedido» | VERIFICADO |
| **Enciende (uso del ojo como área)** | `0x437b7200` invocado | convierte ojos en áreas | VERIFICADO |
| **Apaga (caducidad)** | `0x437b7778`: `0x437b7784 strb r1,[r3]` con `r1=0` → `[0x43f9a575]=0`; `0x437b778c strb r2,[r3]` `r2=1` → `[0x43f9a563]=1`; libera el timer (`0x437b77e8 str r4,[r5]`, `[r5]=0`) | al expirar se borra el flag «timer en marcha» y se libera el handle | VERIFICADO |
| **Mantiene** | `0x437b74a4`: `0x437b7558 ldrh r3,[r3,#6]` + `0x437b755a muls r2,r3,r2` (`r2=0x3e8`) + `0x437b7562 bl 0x437b6d50` | arma timer OSAL de un disparo, período `u16[cfg+6]×1000` (config `Camera::FC`, mismo objeto `[GOT+0x463c]` que en `0x437b7212`) | VERIFICADO |
| | `0x437b7598` `0x437b7686 ldrb r3,[r7]` / `0x437b7688 cbnz` con `r7=0x43f9a577` (`0x437b7680`) | pestillo de «ya armado una vez»: si vale 1 no se rearma por esa rama; se pone a 1 en `0x437b7692` | VERIFICADO |
| | `0x437b7598` `0x437b76da` / `0x437b76dc` con `r7=0x43f9a575` (`0x437b76d2`) | segundo pestillo, **el que borra `0x437b7778`**: caducado → se puede volver a armar | VERIFICADO |
| | `0x437b7598` `0x437b75ba strb.w r1,[r4,#0xd7]`, `0x437b75be strb.w r3,[r4,#0xe8]` | antes de recalcular, **descuenta** del total las áreas de ojo previas | VERIFICADO |

**¿Atado a la secuencia de AF (pulsación) o al modo continuo?** — **A la secuencia de AF** (con el
límite de que la entrada de `0x437b6670` no está en este binario):
`0x437b7200` solo se ejecuta desde `0x437b7598`, y `0x437b7598` solo desde `0x43aef890`, y `0x43aef890`
solo desde `0x437b7ea0` (`ReplyForTouchShutter`), que es la **respuesta a una petición de AF/táctil**.
No existe ninguna otra arista de entrada (barrido completo de ramas + búsqueda de punteros absolutos
+ PIC: `blfind.py`, `find_pic_refs.py`, `refs_pic.json`). En AF-C la petición se repite mientras el
AF está activo; al cesar las peticiones no se recalcula nada y el estado caduca por el timer.
**INFERENCIA fuerte**: el «solo mientras se pulsa» del usuario es exactamente esto — el ojo se
consume como *respuesta* a una petición, no como *monitor* continuo.

---

## 6. Pregunta 4 — ¿cómo llega la coordenada del ojo al área de AF?

* **Escritor del área de AF (VERIFICADO)**: hay **tres** productores del arreglo de áreas del objeto
  B (`0x43eb3c16`, 8 × `0x14` B en `+0x08`, contador `+0xd7`):
  1. `0x437b6ea4` — caras y objetos (rect en `+0x24..+0x2a` del bloque FC → `ctx+8..0xe`, `0x437b6ee4`–`0x437b6ef4`).
  2. `0x43aef77a` — un registro «LC/PAF» externo (`0x43eb3bf4`) → `ctx+8..` (`0x43aef78e`–`0x43aef7ac`),
     incluidos `+0xde..+0xe6` desde `src+0x16/+0x17/+0x18..+0x1e` (`0x43aef7be`–`0x43aef7de`).
  3. `0x437b7200` — **los ojos** → registros adicionales (`0x437b73e0`–`0x437b743a` para modo 2 ojos;
     `0x437b7456`–`0x437b747c` para 1 ojo).
* **Cómo entra el ojo en el registro** (modo 2 ojos, `r6==2`, `0x437b723a`): `x = [ctx+0xe4] − w/2`,
  `y = [ctx+0xe6] − w/2` (`0x437b7246`–`0x437b725e`), `w = h = r5` donde `r5` se deriva del tamaño de
  cara (`0x437b7214`–`0x437b7238`, tabla `[GOT+0x463c]+5/8/9/0xa/0xb`), y se recorta a
  `0x280×0x1e0` (640×480) en `0x437b7366`–`0x437b73a4`. El registro final se escribe en
  `ctx + 8 + (n−1)*0x14` con `n = [ctx+0xd7]` (`0x437b73cc`–`0x437b7400`). **VERIFICADO**.
* **Salida al consumidor (VERIFICADO)**: `0x437b7ea0` copia `0xec` B del objeto B (desde `0x43eb3c18`)
  en `reply+0xc` (`0x437b7f7c`–`0x437b7f86`) y entrega la respuesta por el método virtual de
  `this+0xb0` (`0x437b7fba b.w 0x437b6b70`; despacho en `0x43ad6034`). Es decir, **la coordenada del
  ojo sí viaja en el estado de áreas de AF que se devuelve al peticionario**, junto con las caras.
* **Copia por frame (VERIFICADO)**: `0x437b7fe4` = «copia del estado de áreas» lee el objeto A
  (`0x43eb3af6`), recorta a `0x280/0x1e0` (`0x437b8030`, `0x437b8084`–`0x437b80a2`) y lo escribe en
  el buffer que le pasa `0x4378f6a6` (dentro de `Imaging::VD_Drive`, `[CAMERA_MAIN_SYNC]`), esto es,
  **una vez por VD**. Ese buffer es el que consume el resto del *pipeline* de AF/pintado.
* **Otros consumidores de ojos en `Camera::FC`** (por nombre de fichero, **INFERENCIA**): 
  `FC/Alg/fc_alg_exif_face_data.cpp` `0x43cf0737` (ojos → metadatos EXIF de cara) y
  `FC/Alg/fc_alg_blink.cpp` `0x43cf071f` (parpadeo). No intervienen en el área de AF; el detalle de
  su uso de `+0x56..+0x60` queda **NO_VERIFICADO**.
* **NO_VERIFICADO**: que el motor de AF interno use el objeto B directamente; lo demostrado es
  (a) B se rellena con el ojo y (b) B viaja en la respuesta `0xf8` y en el mensaje de notificación
  `0xfe` (`0x437b67b8`, copia `0xec` B desde A **o** B). El consumo final ocurre fuera de este
  módulo (`0x4379ce0c` y el buzón `[GOT+0x7368]`).

---

## 7. Pregunta 5 — ¿existe un modo/orden que active el seguimiento de ojo persistente?

* **Setters de `[ctx+0xde]`/`[ctx+0xdf]` (barrido completo, 4.975.565 instrucciones)**: solo **dos**
  funciones escriben ambos bytes como pareja en esta zona de código:
  `0x437b6ea4` (limpia en `0x437b6eac`/`0x437b6eb2`, copia en `0x437b6fce`/`0x437b6ff2`) y
  `0x43aef77a` (copia de `src+0x16/+0x17` en `0x43aef7be`/`0x43aef7d2`). Ambas están **exclusivamente**
  dentro de la ruta de respuesta de AF (§1). **VERIFICADO**.
* **Setters de `face_on`/`obj_on` (`[settings+0x49c]`/`[+0x49e]`)**: el módulo solo los **lee**
  (`0x437b7868`, `0x437b786e`, `0x437b7f60`, `0x437b7cf6`). Ningún `strb` en la zona del módulo;
  los 36/17 escritores del barrido están fuera (`0x4354xxxx`, `0x4363xxxx`, …) — **NO_VERIFICADO**
  cuál de ellos es el ajuste de menú, pero **no** es este módulo.
* **Handlers de mensajes del módulo**: `0x437b7810` registra **solo dos** ids,
  `0x0003012e` (`0x437b7818`) y `0x0003012d` (`0x437b7820`), con `0x435613b0` (wrapper OSAL
  `[GOT+0x16dc]→[+0x14]+0x298`). **No hay ningún id `0x4xxx` ni ninguna cadena `eye`/`EyeAF` en el
  módulo**: barrido de inmediatos `0x30000..0x4ffff` en `0x437b6000`–`0x437b8500` → 0 coincidencias.
  **VERIFICADO**.
* **Sí existe el conmutador de ojo** (pero no es «persistente»): `[LCobj+0x56]` habilita el uso de
  ojos y `[LCobj+0x55]` elige 1 o 2 ojos (`0x437b765c`–`0x437b766c`, `0x437b76b0`–`0x437b76bc`);
  `mode` 0/1/2 se pasa como `r2` a `0x437b7598` desde `0x43aef890`
  (`0x43aef96c`→0, `0x43aef97c`→1, `0x43aef9aa`→2). **INFERENCIA**: son banderas de estado del AF,
  no un ajuste de «Eye AF continuo».
* **Conclusión**: **no existe** en `av-cam.bin` (fw3.21) ningún modo, orden ni mensaje que active la
  conversión ojo→área de forma persistente. Lo persistente solo puede venir de **repetir la
  petición** (que es lo que hace el AF continuo mientras hay pulsación).

---

## 8. Tabla de funciones (dirección, tamaño, qué hace, evidencia)

| dirección | tamaño | qué hace | evidencia |
|---|---:|---|---|
| `0x437b6ea4` | `0x27c` | Productor de áreas: limpia `ctx+0xde/0xdf`, copia caras/objetos y **el par de ojos** (`+0x5f/+0x60`, `+0x56..+0x5c`) | `0x437b6eac`, `0x437b6ede`, `0x437b6ee4`, `0x437b6fca`–`0x437b700e` |
| `0x43aef77a` | `0x80` | Copia un registro externo (`0x43eb3bf4`) al mismo `ctx` (incluye ojos `src+0x16..+0x1e`) | `0x43aef782`–`0x43aef7f6` |
| `0x437b7158` | `0xa0` | Logger privado del módulo (`r0=3,r1=5,r2=1`) | 12 sitios `bl 0x437b7158` |
| `0x437b7200` | `0x282` | **Ojos → registros de área**; 4 sitios del log «Eye data is invalid, but lc flag is true.» | `0x437b723e`–`0x437b7326`, `0x43ca6944` |
| `0x437b74a4` | `0xd8` | Arma timer OSAL de un disparo: período `u16[cfg+6]×1000`; errores `osal_alloc_timer`/`osal_set_timer` | `0x437b7558`, `0x437b755a`, `0x437b7562`, logs `0x437b7548`/`0x437b7570` |
| `0x437b7598` | `0x1b6` | Actualizador de áreas desde caras/ojos; decide modo 1/2 ojos; rearma el timer; descuenta ojos previos | `0x437b75ba`, `0x437b765c`–`0x437b76e4`, `0x43aef9ca` |
| `0x437b7778` | `0x86` | Caducidad del estado: `[0x43f9a575]=0`, `[0x43f9a563]=1`, libera timer | `0x437b7784`, `0x437b778c`, `0x437b77e8`, log `0x437b77f6` |
| `0x437b7810` | `0x22` | Init: registra ids `0x3012e` y `0x3012d`; enmascara `[0x43f9a573]&1` | `0x437b7818`, `0x437b7820`, `0x437b782a` |
| `0x437b7844` | `0x422` | Construye el bloque de parámetros del `reply` (face_on/obj_on, modo, `APP MODE ERROR: face_on, obj_on`) | `0x437b7868`, `0x437b787c`, `0x43ca6a0a` |
| `0x437b7c8c` | `0xc4` | Flags del `reply` (face/obj/af, contador `0x43eb3bec`) | `0x437b7c94`–`0x437b7d4a` |
| `0x437b7d6c` | `0xa6` | Rellena estado de `reply` desde `0x439fd740`/FC | `0x437b7d70`, `0x437b7df6` (`BatteryInfo`) |
| `0x437b7e38` | `0x06` | Getter: devuelve `0x43eb3c16` (objeto B) | `0x437b7e3a` |
| `0x437b7e44` | `0x06` | Getter: devuelve `0x43eb3af6` (objeto A) | `0x437b7e46` |
| `0x437b7e50` | `0x12` | Getter: `[0x43f9a572]<<8 | [0x43f9a576]` | `0x437b7e52`–`0x437b7e5c` |
| `0x437b7e6c` | `0x08` | Getter: `[0x43f9a56e]` | `0x437b7e6e` |
| `0x437b7e78` | `0x08` | Getter: `[[0x43eb3be6]]` (objeto de detección) | `0x437b7e7a` |
| `0x437b7e84` | `0x08` | Getter: `[[0x43eb3af2]]` | `0x437b7e86` |
| `0x437b7e90` | `0x0a` | `[0x4401e959]=1` | `0x437b7e94` |
| `0x437b7ea0` | `0x126` | **`ReplyForTouchShutter`**: construye `reply` (0xf8), copia `0xec` del objeto B, dispara el envío | `0x437b7eb2`, `0x437b7f02`, `0x437b7f86`, `0x437b7fba` |
| `0x437b7fe4` | `0xec`+ | Copia de estado de áreas A → buffer del llamador, recorte 640×480 | `0x437b7fe8`, `0x437b803e`, `0x437b8084` |
| `0x437b81f0` | `0x30` | `SetRequestReplyForTouchShutter` (registra callback, flag de turno `0x43f9a564`) | `0x437b8200`, `0x437b820e` |
| `0x437b6670` | `0x62` | Entrada del camino táctil: elige búfer `0x43eb3720`/`0x43eb3818`, llama `ReplyForTouchShutter`, entrega por vtable `+0xb0` | `0x437b6688`, `0x437b668c`, `0x437b669a`, `0x437b6668` |
| `0x437b6b40` | `0x2c` | Despachador por índice 0..7 de los 8 handlers FC de la tabla `0x43ff460c` | `0x437b6b4c`, `0x437b6b4e`–`0x437b6b5a` |
| `0x437b67b8` | `0x4a` | Notificación: copia `0xec` B del objeto A **o** B al buzón y lo marca para envío | `0x437b67d0`, `0x437b67fa` |
| `0x43aef890` | `0x13c` | **Despachador de AF**: elige modo 0/1/2, llama `0x437b6ea4` y termina en `0x437b7598` | `0x43aef8ca`, `0x43aef96c`, `0x43aef9aa`, `0x43aef9ca` |
| `0x43a0a47c` | `0x100`+ | `ProcessEdt::StartEdt` → `idt_edt_start` (petición de **EyeDetection** al IDT) | `0x43a0a48c`, `0x43a0a498`, `0x43a0a55e`, `0x43a0a570` |
| `0x43b75836` | `0x66` | Envoltorio FC: gate `[fcctx+0x1d3]`, `0x43b780c4`, marca `+0x2780+0x65`, llama EDT | `0x43b75848`, `0x43b75860`, `0x43b75876`, `0x43b7587e` |
| `0x43a06428` | `>0x300` | Algoritmo de selección de objetivo AF (`fc_alg_select_key`), invoca EDT por `0x43a06700` | `0x43a0640c` (`./FC/Alg/fc_alg_select_key.h`), `0x43a06700` |
| `0x43a303f8` | — | Servicio IDT: `idt_edt_start` (NO_VERIFICADO su interior) | única llamada `0x43a0a55e` |

---

## 9. Pieza mínima para que el ojo sea continuo

Ordenado por coste/riesgo y con la evidencia que lo sostiene:

1. **Repetir la petición en vez de reescribir el detector** (INFERENCIA, es lo único que el binario
   permite sin tocar código): el ojo solo se convierte en área cuando corre `0x437b7598`; si el
   consumidor (libObj/`SequenceSetAfAreaPoint`) emite la petición de AF/táctil de forma periódica
   con el `mode` adecuado, `0x437b7200` se reevalúa y el área de ojo se refresca. Ya está
   implementado en el carril H del proyecto (`setTouchAFPosition` desde PC) — este análisis explica
   **por qué** ese camino es el único viable sin parchear.
2. **Si se quisiera dentro de la cámara** (parche, no autorizado aquí): llamar a `0x437b7598` con
   `(this=0x43eb392c, ctx=0x43eb3c16, modo=2, ·)` desde el tick de VD o desde el bucle de live view.
   Requisitos que el código impone: `[ctx+0xd6] != 0` o la rama de `0x437b769a`, `ctx+0x1b != 0`,
   `[0x43eb392c+0x38]+0x54 & 0x00ffff00 != 0`, y que `0x437b6ea4` se haya ejecutado antes para dejar
   `ctx+0xde/0xdf` válidos (§1). Sin eso, `0x437b7200` solo registra «Eye data is invalid…».
3. **Bandera de habilitación de la detección**: el gate está en `Camera::FC` (`[fcctx+0x1d3]` y
   `0x43b780c4`), no en `[CAMERA_MAIN_FC]`; forzarlo sin el servicio IDT no produce ojos.
4. **Lo que no hace falta**: no hay que tocar `face_on`/`obj_on` (`+0x49c`/`+0x49e`) ni los ids
   `0x3012d/0x3012e`; el módulo no tiene ningún mensaje de ojos.

---

## 10. Método y límites (NO_VERIFICADO)

**REA (MCP)**: se abrió una sesión dedicada (`session_daemon.py` + `q.py`) sobre `av-cam.bin` con
`format=raw-binary, architecture=arm, entry_point=0x43541000`; el arranque en frío del binario de
11,4 MB no llegó a completarse dentro del presupuesto de esta sesión, por lo que **todo el material
de este informe procede de desensamblado propio byte a byte** (capstone, Thumb-2) con los índices
`branches.json` (420.003 ramas), `refs_pic.json` (37.406 referencias PIC), `field_access.json`,
`eye_fields.json` y `fieldscan_1d2_1d3.json`. Cada arista citada se comprobó con búsqueda
independiente del sincronismo del barrido (`blfind.py`, decodificación de BL/BLX/B.W en todas las
ventanas alineadas a 2) y con búsqueda de punteros absolutos de 32 bits.


* Quién invoca `0x437b6670`: **no aparece** ni como rama directa (`blfind.py`, `b.w`/`blx`
  incluidos), ni como puntero absoluto (barrido de todas las palabras de 32 bits), ni como delta PIC
  (`find_pic_refs.py`, `refs_pic.json`). La entrada del camino táctil queda **NO_VERIFICADA**;
  todo lo demás de la cadena sí está verificado porque cada arista se localizó por bytes.
* Quién llena el objeto A (`0x43eb3af6`): solo lecturas. **NO_VERIFICADO**.
* Interior del servicio IDT (`0x43a303f8`) y de `0x43b780c4`. **NO_VERIFICADO**.
* Semántica exacta del nombre «lc»: **INFERENCIA** (§4).
* No se ha usado la cámara ni se ha ejecutado firmware; todas las direcciones son de
  `av-cam.bin` fw3.21 con base `0x43541000`.
