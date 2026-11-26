# FILM-PB-1 / sub-fuga-mutex — ¿Se fuga de verdad el mutex del `ifoFramework` en el `mp4Ifo_If`? (libmpr 3.21)

**Binario:** `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`)
**Evidencia:** [reports/evidence/film-pb-1-sub-fuga-mutex-20261126/](evidence/film-pb-1-sub-fuga-mutex-20261126/)
**Herramientas:** `python3 /tmp/elfhelper.py <so> dis <va> <len>` (capstone THUMB) para el desensamblado;
`.ARM.exidx` + destinos de `bl` + prólogos `push {..,lr}` para delimitar funciones (31 233 entradas de
`.text` `0x120228..0x7A3E84`); CFG por descenso recursivo propio (`scripts/ifocfg.py`) para el balanceo por caminos.
**Datos de partida (no re-investigados):** `0x5BAD00`=Adquirir (try-lock), `0x5BACB0`=Liberar,
`0x5BACF4`=set_owner, objeto `IfoSemaphore` creado en `0x5BACD0`.

---

## 0. Veredicto en corto

| Pregunta | Respuesta | Estado |
|---|---|---|
| ¿Hay acquire sin release en la clase `mp4Ifo_If`? | **No.** 106 métodos, 106 acquire, 106 release, **1 par por método** y **todos** los caminos de salida pasan por `0x5BACB0`. | VERIFICADO |
| ¿Censo global en libmpr? | 809 llamadas a `0x5BAD00` y **809** a `0x5BACB0`; 564 funciones; ninguna huérfana. | VERIFICADO |
| ¿Reentrada por llamada directa (misma clase) dentro de la sección crítica? | **0 casos** (ni dentro ni fuera de la sección crítica). | VERIFICADO |
| ¿Algún llamador de los 106 métodos llama también a `0x5BAD00`? | **0 de 245 sitios de llamada** (103 de los 106 métodos tienen llamadores directos). | VERIFICADO |
| ¿Puede el destructor `0x6E81BC` destruir con el semáforo tomado? | **Sí**: ignora el fallo del acquire y sigue (0x6E81E0 → 0x6E81EC). | VERIFICADO |
| ¿Puede `[mp4Ifo_If+4]` quedar apuntando a memoria liberada? | **Sí**: `delete(sem)` en `0x6E81FE` no limpia el campo; solo lo hace el ctor (`0x6E80CE`, `0x6E816A`). | VERIFICADO |
| ¿Deja algún camino de código el byte a 0 **con el objeto vivo**? | **Ninguno.** Un 0 persistente exige un hilo vivo dentro de la sección crítica **o** el objeto muerto/reciclado. | VERIFICADO el "ninguno"; INFERIDO la causa |

**Conclusión de una línea:** el mutex **no se fuga por desbalanceo**; el `0` persistente solo puede venir de
(a) un hilo que entró y no vuelve (sección crítica larga/bloqueada — el lock es *try-lock sin espera*) o
(b) del binomio `~mp4Ifo_If` + `MMgrMp4IfoAcsr::DestroySub`, que destruyen el `mp4Ifo_If` **aunque no hayan
podido tomar el lock**, liberan un lock que no poseen y borran el semáforo sin poner `[handle+4]=0`.

---

## 1. El objeto semáforo del `mp4Ifo_If`: dónde nace y quién escribe el puntero

### 1.1 Creación (única)

```
006e815a  movs  r0, #0x1c
006e815c  blx   _Znwj               ; new(0x1C) = objeto IfoSemaphore
006e8160  movs  r1, #5              ; módulo de log
006e8162  mov   r2, r6              ; subtipo 1..8 según tipo de ifo
006e8166  bl    0x5bacd0            ; ctor: m_free([+4]) = 1
006e816a  str   r5, [r4, #4]        ; handle[+4] = sem   <-- ÚNICO escritor del puntero con valor
```

y este bloque **solo se ejecuta si la apertura del impl tuvo éxito**:

```
006e8128  cbnz  r0, 0x6e816c        ; r0 = resultado de 0x6EC028/0x6EC07C; si != 0 salta a la salida
```

* Escritores de `[mp4Ifo_If+4]` en toda la TU (`0x6E807C-0x6EC200`): **solo dos**, `0x6E80CE` (`=0`, en el ctor)
  y `0x6E816A` (`=sem`). Barrido exhaustivo de `str/strb` con offset `#4`: evidencia
  `provenance-reentrancy.txt` §1. (El `str r5,[r4,#4]` de `0x6EC120` es otro objeto — un contenedor de
  18 B con 4 sub-objetos — no el handle.)
* El byte `[sem+4]` solo lo escriben `0x5BACE0` (ctor, `1`), `0x5BACC6` (release, `1`) y `0x5BADC2`
  (acquire, `0`). Confirmado en `disasm-key-paths.txt`.
* **Estado real “sin semáforo”**: si la apertura falla, el ctor retorna el handle con `[handle+4]==0`
  y el llamador (`0x67C67A-0x67C68C`) lo usa igualmente → `0x5BAD00` haría `ldrb [r4,#4]` con `r4=0`
  = *data abort* en `0x4`. Es decir: `[handle+4]==0` **no** produce `0xCA001001`, produce excepción.
  Por eso el síntoma observado (rechazo limpio) implica un objeto **vivo**.

### 1.2 Censo de llamadas que usan ESTE semáforo

Criterio: sitios `bl 0x5BAD00` cuya procedencia de `arg0` es `ldr r0,[r4,#4]` con `r4 = this` (r0 de entrada
del método) dentro de la TU `mp4Ifo_If.cpp` (`0x6E807C..0x6EC200`, delimitada por las 88 funciones que citan
la cadena de fichero `0x91B6DF "mp4Ifo_If.cpp"`).

| Censo | Valor |
|---|---|
| Sitios acquire en la TU | **106** (evidencia `acquire-release-106.tsv`) |
| Sitios release en la TU | **106** |
| Métodos con más de un par | **0** (los “2 pares” del informe previo, p.ej. `0x6E8430`, son **dos funciones distintas**: `GetPlayThumbnailInfo` y `GetContentsInfo` en `0x6E84E0`, que `.ARM.exidx` no separa) |
| Rango de `cmd` (r1) | `0x01` (dtor) y `0x10..0xd9` (p.ej. `0x23` = `GetPlayThumbnailInfo`, `0x60` = `OpenPbFile`) |

Procedencia global en libmpr (809 sitios), por firma del objeto que se pasa a `0x5BAD00`:
`[rX+8]` 435 sitios (otra familia de wrappers), `[rX+4]` 288 (dos familias: `hdAvcIfo_If` `0x5AC738..0x5B0CD0`
— 186 sitios, atribución INFERIDA por el ctor `0x5AC6E8` del informe previo — y **`mp4Ifo_If`
`0x6E81BC..0x6EBF90`, 106 sitios**), `this` directo 23, resto ruido de análisis.
→ La familia del `+4` **no** es única, pero la TU sí: los 106 sitios son de `mp4Ifo_If`.

---

## 2. Balanceo por caminos (¿todos los `return` pasan por `0x5BACB0`?)

**Método.** Para cada uno de los 106 sitios: CFG por descenso recursivo desde la entrada de la función
(siguiendo `b`, `bcc`, `cbz/cbnz`, `it`; `pop {..,pc}`, `bx lr` y `b` fuera de rango = salida; sin modelar
`blx`); se arranca en la rama **“acquire OK”** (`cbz r0, ok` / `cbnz r0, fallo` / `cmp r0,#0`+`beq`) y se
calcula el conjunto alcanzable **bloqueando** los sitios de release. Si se alcanza una salida → fuga.

**Resultado: 106/106 OK.** Salida completa en `evidence/cfg-balance.txt`. No hay ni un `return` con el lock
tomado. Dos únicos “LEAK” que la herramienta marcó son **falsos positivos** y se comprobaron a mano:

| Sitio | Por qué es falso positivo | Desensamblado |
|---|---|---|
| `0x6EB3FC` (`DeleteDirectory`) | La instrucción siguiente al acquire es `mov r2,r0`; la heurística tomó el *fallthrough* (que es el camino de **fallo**) y lo interpretó como éxito. El camino real de éxito es `0x6EB414` y libera en `0x6EB42A`. | `disasm-key-paths.txt` |
| `0x6E9E7E`, `0x6E9F22`, `0x6E9FBE`, `0x6EAF22`, `0x6EB8CE` | Mismo patrón (`mov rX,r0` antes del `cbz`); el camino de éxito libera (`0x6E9EBA`, `0x6E9F5A`, `0x6E9FF4`, `0x6EAF5A`, `0x6EB918`). | idem |

**Forma canónica de los 106 métodos** (ejemplo verificado, `GetPlayThumbnailInfo`):

```
006e8454  ldr  r0, [r4, #4]        ; sem = this->handle[+4]
006e8456  movs r1, #0x23           ; cmd
006e8458  movs r2, #1              ; log
006e845a  bl   0x5bad00            ; acquire
006e845e  cbz  r0, 0x6e8470        ; 0 = tomado -> camino bueno
006e8460..6e8466  log(0xB0100002)  ; fallo: NO se libera (correcto: no se tomó)
006e846c  ldr  r5, =0xB0100002
006e846e  b    0x6e84ac            ; -> END
006e8470  ...  blx r5 (impl)       ; trabajo real
006e84a2  movs r1, #1
006e84a4  mov  r5, r0
006e84a6  ldr  r0, [r4, #4]        ; mismo sem, recargado del mismo this
006e84a8  bl   0x5bacb0            ; release
006e84ac  ... END ... pop {..,pc}
```

Riesgo residual del análisis, acotado: dentro de las **106** secciones críticas (`acquire+4` … `release`) el
único `bl` directo es **`0x6F0A54`** (logger de error de la rama de fallo, 107 apariciones) y **`0x6EC0C8`**
(teardown del impl, 1 aparición: el destructor). Todo el trabajo real de cada método se hace con **`blx`** a
un método virtual del impl (`ldr r3,[this]` → `ldr rN,[vtable+slot]` → `blx`), que el CFG no puede seguir.
No hay `tbb/tbh` (tablas de salto) en ninguna sección crítica. `~mp4Ifo_If` sí tiene `blx` a destructores
virtuales en medio de su sección crítica (`0x6E81D6`, `0x6E81EE`): una excepción ahí se saltaría el release.
La función tiene entrada `.ARM.exidx` con unwind en `0x9777A8` pero **no** tiene *landing pad* en el cuerpo
→ **NO_VERIFICADO** que el destructor del impl pueda lanzar (en la práctica un dtor es `noexcept`: sería
`terminate`, no un estado persistente).

---

## 3. Reentrada

| Comprobación | Resultado | Evidencia |
|---|---|---|
| `bl` directo, desde dentro de la sección crítica, a otro método de la clase que también hace acquire | **0** | `provenance-reentrancy.txt` |
| `bl` a otro método de la clase en cualquier punto de los 106 métodos | **0** | idem |
| Llamadores de los 106 métodos (245 sitios, 103 métodos) que además llamen a `0x5BAD00` | **0** | `provenance-reentrancy.txt` |
| Rutas indirectas: `blx [impl_vtable+slot]` (el impl de `[handle+0]`, 0x230/0x208 B) | No recibe el puntero al handle (`0x6EC028`/`0x6EC07C`), así que no puede llamar a los métodos por ese camino | VERIFICADO el “no recibe el handle”; **NO_VERIFICADO** que no lo obtenga por la tabla del framework (`0x601F48`, id 7) o por un callback (`SetCallback` `0x6EBF90`, cmd `0x20`) |

**Consecuencia:** no hay reentrada *demostrable* en código. Pero el lock **no es recursivo ni espera**
(`0x5BAD22 bne 0x5BADBC` → toma; si el byte es 0 → rechazo inmediato en `0x5BAD24`), así que **cualquier**
solape (dos hilos, o un callback que re-entre) produce `0xCA001001` garantizado, sin reintento.
`GetPlayThumbnailInfo` (`0x6E8430`) tiene **4 sitios de llamada en 4 zonas distintas del binario**
(`0x4D37E0`, `0x61A9E4`, `0x67B598`, `0x67C0B2`) y el único serializador es este try-lock.

---

## 4. Destructor `0x6E81BC` y sus llamadores

### 4.1 El destructor, instrucción a instrucción

```
006e81bc  push {r4,r7,lr} ; sub sp,#0x14 ...
006e81d6  movs r1, #1
006e81d8  ldr  r0, [r4, #4]        ; sem
006e81da  mov  r2, r1
006e81dc  bl   0x5bad00            ; (A) ACQUIRE
006e81e0  cbz  r0, 0x6e81ec        ;      si OK -> teardown
006e81e2  ldr  r0, =mp4Ifo_If.cpp
006e81e4  movs r1, #0x97
006e81e6  ldr  r2, =0xB0100002
006e81e8  bl   0x6f0a54            ;      si FALLA: solo loguea...
006e81ec  mov  r0, r4              ;   ...y SIGUE (misma etiqueta que el camino bueno)
006e81ee  bl   0x6ec0c8            ; (B) teardown del impl: vtable[1] + [handle+0]=0
006e81f2  ldr  r0, [r4, #4]
006e81f4  movs r1, #1
006e81f6  bl   0x5bacb0            ; (C) RELEASE  <-- se ejecuta SIEMPRE
006e81fa  ldr  r0, [r4, #4]
006e81fc  cbz  r0, 0x6e8204
006e81fe  ldr  r3, [r0] ; ldr r3,[r3,#4] ; blx r3   ; (D) delete(sem)  [vtable[1] de 0x8BBCF8 = _ZdlPv]
006e8204  movs r0, #7 ; mov r1, r4 ; bl 0x601ea0   ; (E) baja del registro del framework (id 7)
006e820c..006e8226  END; return this
```

Defectos **verificados**:

| # | Defecto | Instrucción |
|---|---|---|
| 1 | **Destruye sin haber tomado el lock**: el fallo del acquire no corta el camino, cae en la misma etiqueta del teardown. Destruye el impl que otro hilo está usando. | `0x6E81E0 cbz r0,#0x6E81EC` + `0x6E81EC` |
| 2 | **Release sin propiedad**: libera (pone `[sem+4]=1` y borra PID/TID/CMD) aunque el acquire falló → *desbloquea el lock de otro hilo*. | `0x6E81F6 bl 0x5BACB0` |
| 3 | **Borra el semáforo con el lock tomado** (28 B liberados por el deleting dtor `0x5BAC50` → `_ZdlPv`). El base dtor `0x5BAC40` solo repone el vptr: no hay “reinicio” del byte. | `0x6E81FE..0x6E8202` |
| 4 | **No limpia `[handle+4]` tras el delete** → el handle queda con un puntero al bloque liberado. Solo `0x6E80CE`/`0x6E816A` escriben ese campo. | ausencia tras `0x6E8202` |

### 4.2 Llamadores (corrección del dato de partida)

`b.calls_to(0x6E81BC)` → **`0x67C784`** y **`0x6F1B28`**. (El `0x6F1BEC` que citaba el encargo es un llamador
del **constructor** `0x6E80A4`, no del destructor.)

* **`0x67C784` = `MMgrMp4IfoAcsr::DestroySub(this, handle)`** (`0x67C748-0x67C7A8`):
  ```
  0067c76e  ldr r0,[r4,#8] ; movs r1,#0 ; bl 0x3b2070   ; (wrapper de mgr; semántica NO_VERIFICADA)
  0067c776  ldr r0,[r4,#0x3c] ; cbz ; bl 0x36486c        ; cierra el "medio"
  0067c782  mov r0, r8                                  ; r8 = handle
  0067c784  bl 0x6e81bc                                 ; ~mp4Ifo_If
  0067c788  mov r0, r8
  0067c78a  blx _ZdlPv                                  ; free(handle 8 B)
  ```
  El miembro del accessor (`[this+0x48]`, escrito en `0x67C71C`/`0x67CAD6`) **sí se limpia** en los 3
  caminos normales: `0x67C89C` (`Destroy`), `0x67CAE8`+`0x67CAEC` (`CreateAndLoad` con error),
  `0x67CD14` (`DestroyAndUnload`). → **el “miembro colgante” no es el fallo**; el colgante es `[handle+4]`
  **dentro del handle** durante la ventana entre `0x6E81FE` y `0x67C78A` (y, en el singleton, hasta `0x6F1B2E`).
* **`0x6F1B28`** = destructor del singleton `mp4Ifo_Instance` (`0x6F1B1C-0x6F1B38`):
  ```
  006f1b22  ldr r4,[r5]        ; r5 = &global 0xAD287C
  006f1b24  cbz r4, fin
  006f1b26  mov r0,r4
  006f1b28  bl 0x6e81bc        ; ~mp4Ifo_If
  006f1b2c  mov r0,r4
  006f1b2e  blx _ZdlPv
  006f1b32  movs r3,#0
  006f1b34  str r3,[r5]        ; global = 0  (esta sí limpia)
  ```
  Constructor del singleton: `0x6F1BEC bl 0x6E80A4` → `0x6F1BF0 str r4,[r5]`. Se crea una sola vez
  (guarda en `0x6F1BD4 cbnz`), con argumentos ficticios `0x12345678`/`0x98765432`.
* **Handle temporal**: `MMgrMp4IfoAcsr::CheckSalvageStatus` (`0x67C7B0`) crea un `mp4Ifo_If` **nuevo**
  (con **su propio** semáforo) en la pila si `[this+0x48]==0`, llama a `0x6EBAE4` y lo destruye
  (`0x67C810`…`0x67C828`). Es decir: en el camino de salvamento se crean/destruyen semáforos de 28 B
  con frecuencia → **la ventana de reutilización del bloque liberado es amplia** (refuerza el escenario 3 de §5).

**Respuesta a la pregunta 4:** sí, puede destruirse con el semáforo tomado (defecto 1), y sí, `[mp4Ifo_If+4]`
queda apuntando a memoria liberada (defecto 4). Lo que *no* queda colgando es el puntero del accessor, que se
limpia en los 3 caminos (`0x67C89C`, `0x67CAE8/EC`, `0x67CD14`).

---

## 5. ¿Qué camino deja el byte a 0 de forma *persistente*? (los 3 únicos compatibles)

Descartado el desbalanceo (§2), solo quedan estas tres formas, y **se distinguen en cámara con el volcado
del rechazo** (`0x5BAD8E..0x5BADB8` imprime ACTIVE PID/TID/CMD; ver §7):

| Esc. | Mecanismo | Firma esperada en el rechazo | Estado |
|---|---|---|---|
| **1. Hilo vivo atrapado dentro** | El lock es *try-lock*: el ganador entra y no vuelve (I/O de tarjeta en `OpenPbFile 0x6E9A78` cmd `0x60`, `Load 0x6E823C` cmd `0x10`, `Recovery 0x6EB958` cmd `0xd2`, `Salvage 0x6EBB68` cmd `0xd6`, `ExecRepair 0x6EBD00`, o `GetPlayThumbnailInfo 0x6E8430` cmd `0x23`). Mientras no salga, **todo** lo demás recibe `0xCA001001`. | `[obj]==0x8BBCF8`, `[obj+4]==0`, `PID/TID` ≠ 0, `CMD` = uno de los anteriores | VERIFICADO que no hay salida sin release; **INFERIDO** que el hilo puede quedarse (no se puede probar sin cámara) |
| **2. Solape de dos llamadores** (misma cosa que 1 pero con sección crítica corta) | Dos hilos llaman a la vez a cualquiera de los 106 métodos; el segundo **falla al instante** (no espera). `GetPlayThumbnailInfo` tiene 4 llamadores en 4 TUs. | `CMD` del ganador ≈ `0x23` si es otra miniatura | VERIFICADO el try-lock; **NO_VERIFICADO** el solape real |
| **3. Objeto colgante** | Tras `~mp4Ifo_If` (§4): `delete(sem)` deja `[handle+4]` apuntando a 28 B liberados; si otro hilo ya copió el handle, su `ldr r0,[handle+4]` da el bloque liberado (con `m_free=1` porque el release lo puso antes de liberar) → el acquire **toma** memoria muerta. Si el bloque se recicló como **otro `IfoSemaphore` actualmente tomado**, el rechazo es limpio y `0xCA001001`… y se repite mientras el bloque siga reciclándose igual. | `[obj]==0x8BBCF8` (vtable de otro semáforo vivo), `PID/TID` ≠ 0, `CMD` **ajeno** al llamador | VERIFICADO el puntero colgante y la ausencia de limpieza; **INFERIDO** el reciclado |

Nota: el escenario “objeto muerto/zero” del informe previo (`[obj]≠0x8BBCF8`, PID=TID=CMD=0) **no** puede
producirse por `~mp4Ifo_If` (el release deja `m_free=1` antes del `delete`, y el base dtor no toca el byte);
exigiría memoria reciclada por un tercero.

---

## 6. Conclusión (una frase) y parche mínimo

> **El mutex no se fuga: los 106 métodos del `mp4Ifo_If` tienen un único acquire y un único release y todos
> los caminos pasan por `0x5BACB0`; el `0` persistente solo puede venir de un hilo que entró y no vuelve
> (try-lock sin espera, con I/O de tarjeta dentro) o del destructor `0x6E81BC`, que destruye, libera y borra
> el semáforo aunque no haya podido tomarlo y deja `[handle+4]` colgando.**

**Parche mínimo recomendado (2 bytes)** — que el destructor **no derribe nada si no pudo tomar el lock**:

```
VA 0x6E81E0 :  20 B1      cbz  r0, #0x6E81EC     (actual)
        -->    80 B9      cbnz r0, #0x6E8204     (propuesto: si acquire!=0 -> saltar a "baja del registro")
```

*(Codificación verificada con capstone: `80 B9` en `0x6E81E0` decodifica como `cbnz r0, #0x6e8204`.)*

Consecuencia: en el camino de fallo se salta (B) teardown del impl, (C) release sin propiedad y (D) `delete`
del semáforo tomado; se ejecuta (E) la baja en el framework y el `return this`. **Coste:** se fugan el impl
(0x230/0x208 B) y los 28 B del semáforo en ese caso raro, y el handle (8 B) lo libera igualmente
`DestroySub` (`0x67C78A`) → el llamador debe asumir que el objeto no está completamente destruido.
Efecto buscado: se elimina el *use-after-free* del semáforo y el desbloqueo del lock ajeno. **NO_VERIFICADO**
en emulación/cámara.

**Parche alternativo (2 bytes)** — si en cámara el ACTIVE CMD resulta ser *del mismo llamador* (solape real)
y se acepta el riesgo de reentrada, convertir el rechazo en **espera activa** (bloqueante) releyendo el byte:

```
VA 0x5BAD24 :  32 4A      ldr r2,[pc,#0xc8]   (inicio del bloque de rechazo)
        -->    F8 E7      b.n 0x5BAD18        (vuelve al ldrb/cmp/bne; reintenta hasta tomar)
```

**Riesgo:** si el 0 lo tiene *el mismo hilo* (reentrada, p.ej. vía callback `SetCallback` `0x6EBF90` o la tabla
del framework), este parche cuelga el hilo en un bucle infinito. **No aplicar sin el volcado de PID/TID.**

**Lo que NO arregla ningún parche de 2 bytes:** limpiar `[handle+4]` tras el `delete` (no hay hueco: habría
que reubicar `movs r0,#7 / mov r1,r4` de `0x6E8204`), ni la ausencia de timeout en las secciones críticas de I/O.

---

## 7. Cómo confirmarlo en cámara (breakpoint ya definido en el informe previo)

Punto de parada `0x5BAD24` (primer byte del rechazo). Leer:

| Memoria | Qué decide |
|---|---|
| `[r4]` | `0x8BBCF8` → objeto vivo. Otro valor → escenario 3 (colgante/reciclado) |
| `[r4+4]` | 0 (por eso estamos aquí) |
| `[r4+8]`,`[r4+0xC]`,`[r4+0x10]` | PID/TID/CMD del dueño. **CMD=`0x23`** → solape de miniaturas; **`0x60`/`0x10`/`0xd2`/`0xd6`** → I/O; **los tres a 0** → memoria muerta |
| `r8`,`r6`,`r5` | PID/TID/CMD del que pide; si coinciden con el dueño → **reentrada del mismo hilo** (escenario 2/3) |
| `[r4+0x14]`,`[r4+0x18]` | `5` / `1..8` si es el semáforo del `mp4Ifo_If` |

`NO_VERIFICADO`: nada de esto se ha ejecutado en la cámara; el trabajo es estático sobre `libmpr.so` 3.21.

---

## Apéndice A — Los 106 pares acquire/release de `mp4Ifo_If` (VA de cada uno)

`cmd` = valor de `r1` (el “CMD” que imprime el rechazo). Fuente: `evidence/acquire-release-106.tsv`.
Veredicto de balanceo: **OK en los 106** (`evidence/cfg-balance.txt`).

| # | método | función | acquire | cmd | release |
|---|---|---|---|---|---|
| 1 | `~mp4Ifo_If` | `006e81bc` | **`006e81dc`** | `0x1` | `006e81f6` |
| 2 | `Load` | `006e823c` | **`006e825e`** | `0x10` | `006e8282` |
| 3 | `Unload` | `006e82b8` | **`006e82d8`** | `0x11` | `006e82fa` |
| 4 | `SetTvSystemOfDevice` | `006e8330` | **`006e8354`** | `0x21` | `006e837a` |
| 5 | `GetAVIndexFileID` | `006e83b0` | **`006e83d4`** | `0x22` | `006e83fa` |
| 6 | `GetPlayThumbnailInfo` | `006e8430` | **`006e845a`** | `0x23` | `006e84a8` |
| 7 | `GetContentsInfo` | `006e84e0` | **`006e850a`** | `0x24` | `006e8538` |
| 8 | `GetContentsProtect` | `006e8570` | **`006e8596`** | `0x25` | `006e85be` |
| 9 | `GetContentsProtect` | `006e85f4` | **`006e861a`** | `0x25` | `006e8642` |
| 10 | `GetThumbnailPathFromPath` | `006e86e8` | **`006e8712`** | `0x26` | `006e873c` |
| 11 | `ClrCancelFlag` | `006e87dc` | **`006e87fe`** | `0x28` | `006e8822` |
| 12 | `GetCurrentDirectoryId` | `006e8858` | **`006e887e`** | `0x29` | `006e88a6` |
| 13 | `GetDirectoryInfo` | `006e88dc` | **`006e8902`** | `0x2a` | `006e892a` |
| 14 | `GetDirectoryCount` | `006e8960` | **`006e8984`** | `0x2b` | `006e89aa` |
| 15 | `GetDirectoryTime` | `006e89e0` | **`006e8a0a`** | `0x2c` | `006e8a34` |
| 16 | `GetGroupCount` | `006e8a6c` | **`006e8a92`** | `0x2d` | `006e8aba` |
| 17 | `GetGroupInfo` | `006e8af0` | **`006e8b1a`** | `0x2e` | `006e8b44` |
| 18 | `GetContentCount` | `006e8b7c` | **`006e8ba6`** | `0x2f` | `006e8bd0` |
| 19 | `GetContentCount` | `006e8c08` | **`006e8c32`** | `0x2f` | `006e8c60` |
| 20 | `GetPlayContentsCount` | `006e8c98` | **`006e8cc2`** | `0x72` | `006e8cf0` |
| 21 | `GetPbTime` | `006e8d28` | **`006e8d4e`** | `0x30` | `006e8d76` |
| 22 | `GetFaceCount` | `006e8dac` | **`006e8dd2`** | `0x31` | `006e8dfa` |
| 23 | `GetGpsBasicInfo` | `006e8e30` | **`006e8e5a`** | `0x32` | `006e8e84` |
| 24 | `GetGpsComInfo` | `006e8ebc` | **`006e8ee6`** | `0x33` | `006e8f18` |
| 25 | `GetGpsInfoList` | `006e8f50` | **`006e8f7a`** | `0x34` | `006e8fac` |
| 26 | `GetMarkingCount` | `006e8fe4` | **`006e900a`** | `0x35` | `006e9032` |
| 27 | `GetMarkingComInfo` | `006e9068` | **`006e9092`** | `0x36` | `006e90bc` |
| 28 | `GetMarkingList` | `006e90f4` | **`006e911e`** | `0x37` | `006e9150` |
| 29 | `GetDubbingContentInfo` | `006e9188` | **`006e91b2`** | `0x38` | `006e91dc` |
| 30 | `GetLastTCUBInfo` | `006e9214` | **`006e923e`** | `0x39` | `006e9272` |
| 31 | `GetDemoContentInfo` | `006e92ac` | **`006e92d0`** | `0x3a` | `006e92f8` |
| 32 | `GetContentFileInfo` | `006e9330` | **`006e9356`** | `0x3b` | `006e9380` |
| 33 | `GetDubbingLoadTime` | `006e93b8` | **`006e93de`** | `0x3c` | `006e9408` |
| 34 | `CalcAlignmentFileSize` | `006e9440` | **`006e9466`** | `0x3d` | `006e9498` |
| 35 | `MakeFilePath` | `006e94d0` | **`006e94fa`** | `0x3e` | `006e9526` |
| 36 | `GetCancelFlag` | `006e9560` | **`006e9584`** | `0x3f` | `006e95ac` |
| 37 | `GetStreamFileName` | `006e9688` | **`006e96ae`** | `0x41` | `006e96d8` |
| 38 | `GetStreamFileSize` | `006e9710` | **`006e9736`** | `0x42` | `006e9760` |
| 39 | `GetContentExtentCount` | `006e9798` | **`006e97c2`** | `0x43` | `006e97fa` |
| 40 | `GetContentExtentInfo` | `006e9834` | **`006e985e`** | `0x44` | `006e98a2` |
| 41 | `SetPbAttribute` | `006e98dc` | **`006e9900`** | `0x62` | `006e9928` |
| 42 | `SetScenarioPBAttribute` | `006e9960` | **`006e998a`** | `0x63` | `006e99b6` |
| 43 | `SetRsmAttribute` | `006e99f0` | **`006e9a16`** | `0x62` | `006e9a40` |
| 44 | `OpenPbFile` | `006e9a78` | **`006e9a9a`** | `0x60` | `006e9ac0` |
| 45 | `GetPresentationInfo` | `006e9af8` | **`006e9b1c`** | `0x64` | `006e9b44` |
| 46 | `GetVideoSampleInfo` | `006e9b7c` | **`006e9ba6`** | `0x65` | `006e9bd6` |
| 47 | `GetSeqParamSetSize` | `006e9c10` | **`006e9c3a`** | `0x66` | `006e9c66` |
| 48 | `GetSeqParamSet` | `006e9ca0` | **`006e9cca`** | `0x67` | `006e9cf6` |
| 49 | `GetPicParamSetSize` | `006e9d30` | **`006e9d5a`** | `0x68` | `006e9d86` |
| 50 | `GetPicParamSet` | `006e9dc0` | **`006e9dea`** | `0x69` | `006e9e16` |
| 51 | `SetAudioSampleInfo` | `006e9e50` | **`006e9e7e`** | `0x73` | `006e9eba` |
| 52 | `GetAudioSampleInfo` | `006e9ef4` | **`006e9f22`** | `0x6a` | `006e9f5a` |
| 53 | `GetAudioSampleInfoAAC` | `006e9f94` | **`006e9fbe`** | `0x6a` | `006e9ff4` |
| 54 | `ClosePBFile` | `006ea02c` | **`006ea04e`** | `0x61` | `006ea074` |
| 55 | `GetResumePosition` | `006ea0ac` | **`006ea0d0`** | `0x6b` | `006ea0f8` |
| 56 | `ChgPBAttribute` | `006ea130` | **`006ea154`** | `0x6c` | `006ea17c` |
| 57 | `ResumeInfoToPlayPosition` | `006ea1b4` | **`006ea1da`** | `0x6d` | `006ea204` |
| 58 | `GetNextEntryId` | `006ea23c` | **`006ea266`** | `0x6e` | `006ea292` |
| 59 | `GetNextEffectInfo` | `006ea2cc` | **`006ea2f6`** | `0x6f` | `006ea322` |
| 60 | `CreateResumeInfo` | `006ea35c` | **`006ea382`** | `0x70` | `006ea3ac` |
| 61 | `GetResumeInfo` | `006ea3e4` | **`006ea40a`** | `0x71` | `006ea434` |
| 62 | `SetRecAttribute` | `006ea46c` | **`006ea490`** | `0x90` | `006ea4b8` |
| 63 | `CheckHRecEnable` | `006ea4f0` | **`006ea514`** | `0x91` | `006ea53c` |
| 64 | `GetChapterRecTime` | `006ea574` | **`006ea598`** | `0x92` | `006ea5c0` |
| 65 | `OpenRecFile` | `006ea5f8` | **`006ea61e`** | `0x93` | `006ea648` |
| 66 | `CloseRecFile` | `006ea6ec` | **`006ea710`** | `0x94` | `006ea738` |
| 67 | `ChangeRecFile` | `006ea772` | **`006ea79e`** | `0x9f` | `006ea7e4` |
| 68 | `AddAVCSeqParamSet` | `006ea820` | **`006ea846`** | `0x95` | `006ea870` |
| 69 | `AddAVCPicParamSet` | `006ea8a8` | **`006ea8ce`** | `0x96` | `006ea8f8` |
| 70 | `AddVideoSamples` | `006ea930` | **`006ea95a`** | `0x97` | `006ea986` |
| 71 | `AddAudioSamples` | `006ea9c0` | **`006ea9ea`** | `0x98` | `006eaa16` |
| 72 | `GetContentInformation` | `006eaa50` | **`006eaa74`** | `0x99` | `006eaa9c` |
| 73 | `EstimateResourceSize` | `006eab4c` | **`006eab76`** | `0x9a` | `006eaba2` |
| 74 | `GetRecDirAndFileName` | `006eabdc` | **`006eac06`** | `0xa0` | `006eac32` |
| 75 | `AddVideoSample` | `006eacd0` | **`006ead06`** | `0x9c` | `006ead4e` |
| 76 | `AddAudioSample` | `006ead88` | **`006eadb6`** | `0x9d` | `006eade4` |
| 77 | `DeleteStart` | `006eae78` | **`006eae9a`** | `0xc0` | `006eaec0` |
| 78 | `DeleteContent` | `006eaef8` | **`006eaf22`** | `0xc1` | `006eaf5a` |
| 79 | `DeleteContent` | `006eaf94` | **`006eafbe`** | `0xc1` | `006eaffa` |
| 80 | `DeleteEnd` | `006eb034` | **`006eb056`** | `0xc2` | `006eb07c` |
| 81 | `ProtectContent` | `006eb0b4` | **`006eb0e2`** | `0xc3` | `006eb114` |
| 82 | `CreateDirectory` | `006eb230` | **`006eb256`** | `0xc4` | `006eb280` |
| 83 | `ChangeDirectory` | `006eb2b8` | **`006eb2de`** | `0xc5` | `006eb308` |
| 84 | `IsDeleteDirectory` | `006eb340` | **`006eb36a`** | `0xc6` | `006eb39e` |
| 85 | `DeleteDirectory` | `006eb3d8` | **`006eb3fc`** | `0xc7` | `006eb42a` |
| 86 | `DeleteDirectory` | `006eb460` | **`006eb48a`** | `0xc7` | `006eb4ba` |
| 87 | `BeginMakeRssScenario` | `006eb4f4` | **`006eb51a`** | `0xc8` | `006eb544` |
| 88 | `SetRssScenarioConfig` | `006eb57c` | **`006eb5a0`** | `0xc9` | `006eb5c8` |
| 89 | `SetRssStartEffectInfo` | `006eb600` | **`006eb626`** | `0xca` | `006eb650` |
| 90 | `SetRssEndEffectInfo` | `006eb688` | **`006eb6ae`** | `0xcb` | `006eb6d8` |
| 91 | `EndMakeRssScenario` | `006eb710` | **`006eb732`** | `0xcc` | `006eb758` |
| 92 | `ClearRssScenario` | `006eb790` | **`006eb7b2`** | `0xcd` | `006eb7d8` |
| 93 | `IsNeedRecovery` | `006eb8a8` | **`006eb8ce`** | `0xd1` | `006eb918` |
| 94 | `Recovery` | `006eb958` | **`006eb97a`** | `0xd2` | `006eb9a0` |
| 95 | `IsNeedSalvage` | `006eb9d8` | **`006eb9fc`** | `0xd3` | `006eba24` |
| 96 | `GetSalvageInfo` | `006eba5c` | **`006eba82`** | `0xd4` | `006ebaac` |
| 97 | `CheckSalvageStatus` | `006ebae4` | **`006ebb08`** | `0xd5` | `006ebb30` |
| 98 | `Salvage` | `006ebb68` | **`006ebb8a`** | `0xd6` | `006ebbb0` |
| 99 | `BeginRepair` | `006ebbe8` | **`006ebc0e`** | `0xd7` | `006ebc38` |
| 100 | `GetRepairTime` | `006ebc70` | **`006ebc9a`** | `0xd8` | `006ebcc6` |
| 101 | `ExecRepair` | `006ebd00` | **`006ebd24`** | `0xd9` | `006ebd4c` |
| 102 | `EndRepair` | `006ebd84` | **`006ebda6`** | `0xda` | `006ebdcc` |
| 103 | `GetNeedRegisterCount` | `006ebe04` | **`006ebe28`** | `0xdb` | `006ebe50` |
| 104 | `GetNextRegisterContent` | `006ebe88` | **`006ebeac`** | `0xdc` | `006ebed4` |
| 105 | `RegisterContent` | `006ebf0c` | **`006ebf30`** | `0xd0` | `006ebf58` |
| 106 | `SetCallback` | `006ebf90` | **`006ebfba`** | `0x20` | `006ebfe6` |

## Apéndice B — Reproducibilidad

Todos los scripts están en `evidence/.../scripts/` y solo necesitan `capstone` (`.venv/bin/python3`):

| Script | Qué hace |
|---|---|
| `ifotool.py` | ELF + `.ARM.exidx` → mapa de funciones; `calls_to()` = barrido de `bl` en `.text` |
| `ifocfg.py` | CFG por descenso recursivo; `success_entries()` (rama “acquire OK”); `push_entries()` (arranques que `.ARM.exidx` no separa) |
| `slice.py` | Censo de los 809 sitios y firma de procedencia del objeto (`[rX+4]`, `[rX+8]`, …) |
| `final.py` | Auditoría de balanceo de los 106 sitios + nombre del método (literal de la traza `START`) |
| `reent.py` | Llamadas intra-clase desde dentro de la sección crítica + llamadores que también adquirieren |
| `table.py` | Genera `acquire-release-106.tsv` |

```bash
cd /tmp   # los scripts hacen sys.path.insert(0,'/tmp')
.venv/bin/python3 ifotool.py            # 31233 funciones en .text 0x120228 + 0x683c5c
.venv/bin/python3 slice.py              # 809 acquire / 809 release, firmas
.venv/bin/python3 final.py              # tabla + veredicto por sitio
.venv/bin/python3 reent.py              # reentrada
```

**Evidencia**

| Fichero | Contenido |
|---|---|
| `acquire-release-106.tsv` | Los 106 pares: método, rango de función, VA acquire, `cmd`, VA release, línea del `START` |
| `cfg-balance.txt` | Veredicto de balanceo por sitio (106) + los dos falsos positivos con su traza |
| `disasm-key-paths.txt` | Desensamblado de `IfoSemaphore` (ctor/acquire/release/dtors), `mp4Ifo_If` (create, dtor, `GetPlayThumbnailInfo`, `GetContentsInfo`, `DeleteDirectory`), `open`/`teardown` del impl, `MMgrMp4IfoAcsr` (CreateSub/Create/DestroySub/Destroy/CheckSalvageStatus/CreateAndLoad/DestroyAndUnload) y el singleton `mp4Ifo_Instance` |
| `provenance-reentrancy.txt` | Escritores de `[handle+4]`, censo de procedencia, reentrada, llamadores |
| `scripts/` | Los scripts usados (9) |

---

## Apéndice C — Limitaciones declaradas

1. El binario está **sin símbolos** (solo `.dynsym`): los nombres de método salen del literal de la traza
   `START` de cada función (`0x695C74(file,line,name)`), no de una tabla de símbolos.
2. El análisis de balanceo **no modela** llamadas indirectas (`blx`), excepciones C++ ni `longjmp`. Medido:
   en las 106 secciones críticas el único `bl` directo es el logger `0x6F0A54` (rama de fallo) y, en el
   destructor, `0x6EC0C8`; no hay `tbb/tbh`. El trabajo real es un `blx` virtual que no se sigue.
3. `~mp4Ifo_If` sí tiene un `blx` a un destructor virtual **dentro** de la sección crítica (`0x6E81D6` y
   `0x6E81EE`); si ese destructor lanzase, el release de `0x6E81F6` no se ejecutaría. **NO_VERIFICADO** que
   pueda lanzar (no hay *landing pad* en el cuerpo; el `~mp4Ifo_If` es `noexcept` en la práctica → `terminate`).
4. No se ha verificado si los 4 llamadores de `GetPlayThumbnailInfo` comparten un lock externo
   (`0x4D37E0`, `0x61A9E4`, `0x67B598`, `0x67C0B2`).
5. Nada de esto se ha probado en la cámara ni en emulación (QEMU): es análisis estático del `.so` 3.21.
