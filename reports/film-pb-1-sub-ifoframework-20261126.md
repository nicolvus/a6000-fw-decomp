# FILM-PB-1 / sub-ifoframework — ¿Qué es `0x5BAD00`, quién pone el byte `[obj+4]` y por qué rechaza el semáforo del `mp4Ifo_If`?

**Binario:** `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(`fw 3.21`, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`)
**Evidencia:** [reports/evidence/film-pb-1-sub-ifoframework-20261126/](evidence/film-pb-1-sub-ifoframework-20261126/)
**Herramienta:** `python3 /tmp/elfhelper.py <so> dis <va> <len>` (capstone THUMB); `calls` = barrido de `bl`/`blx` en `.text`.

---

## 0. Resumen

1. `0x5BAD00` **no es un gate de inicialización**: es `Acquire()` de un mutex binario con dueño
   (`ifoFramework_Semaphore.cpp`, módulo de log `22IfoFramework_Semaphore`, vtable `0x8BBCF8`).
   **No bloquea, no reintenta y no tiene timeout**: es un *try-lock* que devuelve `0xCA001001` =
   **`ER_FAILED_ACQUIRE_SEMAPHORE`** (cadena `0x8BBC95`, impresa por el propio acquire) si `[obj+4] == 0`.
2. `0x5BACF4` **no es el unlock**: es el *setter de dueño* (`+8=pid`, `+0xC=tid`, `+0x10=cmd`) que el acquire
   llama **después** de poner `[obj+4]=0`. El unlock real es `0x5BACB0` (pone `[obj+4]=1` y limpia el dueño).
3. `[obj+4]` es **`1 = LIBRE`, `0 = OCUPADO`**. En toda la TU solo hay **tres** escritores: `0x5BACE0`
   (ctor → 1), `0x5BACC6` (release → 1) y `0x5BADC2` (acquire → 0). No existe ningún "reset" externo ni
   inicialización perezosa del flag.
4. El objeto del camino de reproducción lo crea `0x6E80A4` (constructor `mp4Ifo_If`, tag de log
   `"mp4Ifo_If"` `0x91B801`, líneas `0x4D`…`0x7E`) y **solo hay un**
   escritor del puntero: `0x6E816A` `str r5,[r4,#4]`. Se construye desde `MMgrMp4IfoAcsr` (`0x67C676`),
   **no** desde `MprIf::Create` ni desde un constructor estático.
5. Consecuencia: si `0x6E8430` devuelve `0xB0100002` (y con ello `status 0x1A` → «No se puede visualizar»
   **y** cero miniaturas) hay exactamente **dos** mundos posibles, y el propio diagnóstico del acquire
   los separa: **el semáforo está tomado por un hilo vivo** (`ACTIVE PID/TID ≠ 0`) o **el objeto está
   muerto/zero** (`ACTIVE PID = TID = CMD = 0`, vtable distinta de `0x8BBCF8`).

---

## 1. `0x5BAD00` y `0x5BACF4`, identificados

### 1.1 La unidad de compilación y la clase

| Dato | Dirección | Contenido |
|---|---|---|
| nombre de fichero `.cpp` | `0x8BBB14` | `"ifoFramework_Semaphore.cpp"` (literal usado en `0x5BADF4`) |
| nombre de tipo / tag de módulo | `0x8BBC7C` | `"22IfoFramework_Semaphore"` (descriptor `{len,ptr}` en `0x8BBC74`) |
| vtable | `0x8BBCF8` | slot0 `0x5BAC40` (dtor base: fija vptr), slot1 `0x5BAC50` (deleting dtor) |
| tag de log del módulo | `0x8BBC48` | `"IFOFRMWK"` |
| tabla de ficheros del logger | `0x9D9F90…0x9D9FC4` | índice por nombre, incluye `ifoFramework_Semaphore.cpp` |

`ifoFramework_*` es la capa de infraestructura común (**CMN**) que usan todos los *wrappers* `XXXIfo_If`
(`hdAvcIfo_If`, `m2psIfo_If`, `mp4Ifo_If`, …). El semáforo es **una instancia por wrapper**, no un
singleton global. *(Nombre de clase `IfoSemaphore`: **INFERIDO** del nombre del fichero y del tag; el
binario está sin RTTI y solo expone la vtable y el descriptor de tipo.)*

### 1.2 Layout del objeto (28 B = `new(0x1C)` en `0x6E815A`)

```
+0x00  void** vptr        -> 0x8BBCF8
+0x04  u8     m_free      -> 1 = LIBRE, 0 = OCUPADO      <-- el byte de la pregunta
+0x08  u32    m_pid       \ 
+0x0C  u32    m_tid        > dueño actual (escrito por 0x5BACF4, limpiado por 0x5BACA2)
+0x10  u32    m_cmd       /
+0x14  u32    m_logModule (ctor arg1; mp4Ifo usa 5)
+0x18  u32    m_logSub    (ctor arg2; mp4Ifo usa 1..8 segun tipo de ifo)
```

### 1.3 `0x5BAD00` — `Acquire(obj, cmd, logOnSuccess)` *(desensamblado completo en la evidencia A–E)*

```
005bad00  push {r4..sl,lr} ; r4=obj  r5=cmd  sl=log
005bad0e  bl 0x5FD72C            ; r8 = getpid()   (veneer ARM 0x11F020)
005bad14  bl 0x5FD738            ; r6 = gettid()   (veneer ARM 0x11EAD8)
005bad18  ldrb.w sb,[r4,#4]      ; <-- EL BYTE
005bad1e  cmp  sb,#0
005bad22  bne  0x5BADBC          ; si !=0  => LIBRE => tomar
; ---- rechazo (byte == 0) ------------------------------------------------
005bad24  log(0x8BBB14, line=0x8F, err=0xCA001001)   ; "[Error] 0xCA001001"
005bad2e..5bad5a  rellena los 6 parametros del registro de traza
005bad5e  print("ER_FAILED_ACQUIRE_SEMAPHORE\r\n")   ; 0x8BBC95
005bad64  print(" ### REJECT PID = ")                 ; 0x8BBCB3
005bad6a  print_num(r8)                              ; pid del que pide
005bad70  print(" TID = ")  ; print_num(r6)          ; tid del que pide
005bad7c  print(" CMD = ")  ; print_num(r5)          ; cmd del que pide (0x23 en 0x6E845A)
005bad8e  print(" ### ACTIVE PID = ")                ; 0x8BBCD6
005bad94  print_num([r4,#8])                         ; pid del que lo tiene
005bad9a  print(" TID = ")  ; print_num([r4,#0xC])   ; tid del que lo tiene
005bada6  print(" CMD = ")  ; print_num([r4,#0x10])  ; cmd con el que se tomo
005badb8  r0 = 0xCA001001 ; return                   ; <-- rechazo, SIN esperar
; ---- toma (byte != 0) ---------------------------------------------------
005badbc  sb = 0
005badc2  strb.w sb,[r4,#4]                  ; m_free = 0   (UNICO escritor de 0)
005badcc  bl 0x5BACF4(obj, pid, tid, cmd)    ; graba dueño
005badd0  if (log) ...
005bade4  return 0
```

Rasgos que descartan las otras lecturas:

* **No hay bucle, ni `sleep`, ni `timeout`, ni contador de reintentos** entre `0x5BAD00` y `0x5BADE8`:
  se decide en la primera lectura del byte.
* **No compara `r8/r6` con `[obj+8]/[obj+0xC]`**: no hay reentrada recursiva. Si el mismo hilo entra dos
  veces, la segunda **falla** con `0xCA001001`.
* No hay ninguna escritura a `[obj+4]` aparte de las tres de §2.1: el flag **no** se "inicializa" aquí.

### 1.4 `0x5BACF4` — `SetOwner(obj, pid, tid, cmd)`: **no es el unlock**

```
005bacf4  str r1,[r0,#8]     ; m_pid  = pid
005bacfa  str r2,[r0,#0xC]   ; m_tid  = tid
005bacfc  str r3,[r0,#0x10]  ; m_cmd  = cmd
005bacfe  pop {r7,pc}
```

Cuatro instrucciones, **un solo llamante: `0x5BADCC`** (el camino de éxito del acquire). Es el
"grabador de dueño". **Corrige** lo que decía el informe anterior ([sub-BD-tarjeta](film-pb-1-sub-bd-tarjeta-20261128.md) §3:
«si es !=0 → pone `[r4+4]=0`, llama a `0x5BACF4` y devuelve 0» daba a entender que `0x5BACF4` era la
inicialización/liberación; es solo el registro de propiedad).

### 1.5 La pareja real: `0x5BACB0` (release) y `0x5BACA2` (clear owner)

```
005bacb0  if (r1) log_fin(...)        ; 0x5BA2D8
005bacb6  ...
005bacc2  movs r3,#1
005bacc6  strb r3,[r4,#4]            ; m_free = 1   (UNO de los dos escritores de 1)
005bacc8  bl 0x5BACA2                ; m_pid=m_tid=m_cmd=0
005baccc  return 0

005baca2  str r3,[r0,#8] ; str r3,[r0,#0xC] ; str r3,[r0,#0x10]   ; r3=0
```

Censo en libmpr: **809 llamantes de `0x5BAD00`, 809 de `0x5BACB0`, 9 de `0x5BACD0`** (ctor). El uso es
siempre el mismo par: `acquire` al entrar a un método de `XXXIfo_If`, `release` al salir.

---

## 2. El byte `[obj+4]`: qué significa y **todos** sus escritores

### 2.1 Los tres únicos escritores (barrido `strb rX,[rY,#4]` en `0x5BA000-0x5BB800`, TU completa)

| Dirección | Función | Valor | Contexto |
|---|---|---|---|
| `0x5BACE0` | ctor `0x5BACD0` | **1** | `movs r3,#1 ; strb r3,[r0,#4]` — nace **libre** |
| `0x5BACC6` | release `0x5BACB0` | **1** | tras `log_fin`; después `0x5BACA2` limpia el dueño |
| `0x5BADC2` | acquire `0x5BAD00` | **0** | `strb.w sb,[r4,#4]` con `sb=0`; después `0x5BACF4` graba el dueño |

No aparece ningún otro acceso de escritura al byte en la TU, ni en el resto de `libmpr` (los 809 pares
adquieren/liberan siempre a través de `0x5BAD00`/`0x5BACB0`). En particular **no hay reset de error,
ni "init()" del semáforo, ni un camino que lo deje a 0 sin pasar por el acquire**.

### 2.2 Quién construye el objeto del camino de reproducción

`[mp4IfoIf+4]` (el puntero al semáforo) se escribe **una sola vez**, en `0x6E816A`, dentro de
`0x6E80A4` (`mp4Ifo_If.cpp`, líneas `0x4D`…`0x7E`):

```
006e80cc  str r3,[r4]           ; handle[0]  = 0
006e80ce  str r3,[r4,#4]        ; handle[4]  = 0   (aún sin semáforo)
006e8106  bl 0x601F48           ; registra el ifo en la tabla del framework (id 7)
006e8114  bl 0x6EC07C  /  006e8124 bl 0x6EC028   ; apertura real del ifo (2 variantes)
006e8128  cbnz r0, 0x6E816C     ; <-- si la apertura FALLA, salta la creación del semáforo
006e815a  movs r0,#0x1c ; blx operator new            ; 28 B
006e8160  r1 = 5 ; r2 = <tipo 1..8>                   ; módulo/subtipo de log
006e8166  bl 0x5BACD0                                 ; ctor -> m_free = 1
006e816a  str r5,[r4,#4]                              ; handle[4] = sem
```

*Mapeo del tipo*: `[info+4]` `0→1, 1→2, 2→3, 3→4, 4→6, 5→8` (`0x6E812A-0x6E8158`).

Llamantes de `0x6E80A4` (2):

| Sitio | Contexto |
|---|---|
| `0x67C676` | `mmgrifoacsr/MMgrMp4IfoAcsr.cpp`, función que traza `"CreateIfoAcsrInstance : Device type is i…"` (`0x8DFE58`) y `"CreateSub"` (`0x90D5F1`). Crea el *accessor* MMgr y dentro el `mp4Ifo_If` (`new(8)` en `0x67C662`). |
| `0x6F1BEC` | inicialización de instancia única de `mp4Ifo_Instance` con argumentos ficticios `0x12345678`/`0x98765432`. |

Destructor `0x6E81BC` (`~mp4Ifo_If`), llamantes `0x67C784` (`MMgrMp4IfoAcsr`, destrucción) y `0x6F1B28`:

```
006e81d6  r1=1 ; ldr r0,[r4,#4] ; r2=1 ; bl 0x5BAD00   ; acquire
006e81e0  cbz r0, 0x6E81EC
006e81e2  log(0xB0100002)                              ; <-- solo REGISTRA el fallo
006e81ec  bl 0x6EC0C8                                  ; teardown real
006e81f2  ldr r0,[r4,#4] ; r1=1 ; bl 0x5BACB0           ; release  (¡aunque no lo tuviera!)
006e81fa  ldr r0,[r4,#4] ; cbz -> fin
006e81fe  ldr r3,[r0] ; ldr r3,[r3,#4] ; blx r3         ; delete(sem)   (slot 1 de 0x8BBCF8)
```

Dos defectos **verificados** en el destructor, relevantes para la hipótesis "objeto muerto":
**(a)** libera el semáforo **sin haberlo adquirido** si el acquire falló (`release` sin *ownership*);
**(b)** **no pone `[handle+4]=0`** después de `delete(sem)` → el handle queda apuntando a memoria liberada.

### 2.3 ¿Y el "arranque"? (constructor estático / `MprIf::Create` 0x712530 / MMgr / hilo del player)

* **No hay constructor estático** de este objeto: no aparece en `.init_array` ni en ningún `__attribute__((constructor))`
  de la TU; el ctor solo se invoca desde los 9 puntos de §2.4.
* El `ifoFramework` **no** se inicializa en `MprIf::Create` (`0x712530`): el *framework* se registra por módulo
  (`0x601F48`, id 7) y cada wrapper `XXXIfo_If` **crea su propio semáforo** cuando el MMgr crea el *accessor*
  correspondiente (`MMgrMp4IfoAcsr::CreateSub` → `0x6E80A4` → `0x6E8166`).
* Es decir: el semáforo del mp4 **nace y muere con el `mp4Ifo_If` que crea el MMgr**, no con el arranque de
  la cámara ni con el hilo del player. Si el MMgr recrea el *accessor* (cambio de medio, re-entrada a
  reproducción, recuperación de BD) el semáforo es **otro**, y el anterior se destruye.

### 2.4 Los 9 objetos (uno por wrapper) y sus constructores

`0x5AC6E8` (`hdAvcIfo_If::Create`), `0x5D0D90` (`m2psIfo_If`), `0x5ECE24`, `0x765F0E`, `0x78FB56`,
`0x79EAC6`, `0x2BA73A`, `0x3A838A` y **`0x6E8166` (mp4Ifo_If ← el de la miniatura/reproducción)**.

---

## 3. ¿LOCK con timeout, o gate de inicialización?

**Es un LOCK** (mutex binario con dueño), y además **sin timeout**: *try-lock* puro.

| Evidencia | Lectura |
|---|---|
| cadena `ER_FAILED_ACQUIRE_SEMAPHORE` (`0x8BBC95`) | el error es "no pude adquirir" |
| imprime `REJECT PID/TID/CMD` + `ACTIVE PID/TID/CMD` | contención con dueño identificado |
| ctor pone `1`; release pone `1`; acquire pone `0` | `1 = libre`, `0 = tomado` |
| `release` limpia dueño y devuelve 0 | es un mutex, no un contador |
| sin bucle / `sleep` / comparación de tiempo | **no hay espera ni timeout** |
| sin comparación pid/tid propio | **no es recursivo** |

**Condición exacta que deja el byte a 0.** Solo una de estas dos:

1. **Alguien lo adquirió y no lo liberó** (o lo liberará más tarde): `m_free=0` con
   `m_pid/m_tid/m_cmd ≠ 0`, y `[obj] == 0x8BBCF8`.
2. **La memoria está muerta**: el `new(0x1C)` nunca se ejecutó, o el bloque se liberó/zero tras
   `~mp4Ifo_If` (que **no** limpia `[handle+4]`, §2.2). Entonces `m_free=0` **y**
   `m_pid=m_tid=m_cmd=0` **y** `[obj] ≠ 0x8BBCF8`.

No hay una tercera vía: el byte **no** es un "initialized flag" que alguien pueda dejar a 0 por error de
secuencia — el único escritor de 0 es el propio acquire, que **acto seguido** graba el dueño.

> Nota sobre el `NULL`: si `0x6E80A4` falla antes de crear el semáforo, deja `[handle+4]=0`; entonces
> `0x6E8454` (`ldr r0,[r4,#4]`) pasa `r0=0` a `0x5BAD00`, que haría `ldrb [4]`. Eso **no** produce
> `0xCA001001` limpio: produce una excepción de datos. Por eso el caso observado no es "handle NULL".

---

## 4. Los dos códigos de error

### 4.1 `0xCA001001` = `ER_FAILED_ACQUIRE_SEMAPHORE` — **sí tiene nombre**

* El propio acquire lo imprime: `0x5BAD5E` carga `0x8BBC95` = `"ER_FAILED_ACQUIRE_SEMAPHORE\r\n"`.
* Es también el `err` que pasa al logger del ifoFramework: `0x5BAD24` → `log(0x8BBB14, línea 0x8F, 0xCA001001)`
  → `0x5BA1CC` (registro estructurado DMSG). El formateador de texto de ese registro está en la misma TU,
  `0x5BA678`…`0x5BA6A8`: `"[Error] 0x"` (`0x8BBC51`) + `%08X` + fichero + `"("` (`0x8DD35E`) + línea + `")"`.
* Censo: 77 literales `0xCA001001` en `libmpr`, **ninguno** dentro de la TU `mp4Ifo_*`: la capa mp4 **no**
  propaga el código tal cual, lo traduce.

### 4.2 `0xB0100002` — **no tiene nombre ni tabla en el firmware**

* `grep -a 'B010'` sobre todo `nflasha15_unpacked` (incluidas las 100+ `.so`): **0 resultados**. Solo existe
  como literal de código: 144 veces en `libmpr` (213 sitios que lo cargan dentro de `0x6E8000-0x6ED000`) y
  `0xB0100001` una vez en `libObj`. No hay tabla `{código, nombre}` ni mensaje traducido.
* Familia en `libmpr`: `0xB0100001` ×56, `…02` ×144, `…03` ×4, `…04` ×4, `…05` ×2, `…06` ×80, `…07` ×1,
  `…08` ×1, `…09` ×4. Es el espacio de errores de la capa **IF/mp4** (`mp4Ifo_*`, `mp4FileLib_*`), no del
  ifoFramework.
* Traducción real en el log (`0x6F0A54`, logger de la TU): `" ### mp4Ifo faild at "` + fichero + `"("` +
  línea + `") ErrCd: 0x"` + `%08X` (`0x91C945`, `0x8DD35E`, `0x8BBA44`), es decir:
  **`### mp4Ifo faild at mp4Ifo_If.cpp(0x1AF) ErrCd: 0xB0100002`**.
* Semántica: en `mp4Ifo_If.cpp` es el **retorno único de "operación fallida"**, y **en `0x6E8430` hay un
  solo camino que lo produce**: el acquire fallido de `0x6E845A`. (En el resto de la TU acompaña tanto a
  fallos de semáforo como a errores internos; por eso el valor no distingue causa *por sí mismo* — pero en
  esta función sí, porque es el único `return` distinto de 0.)

### 4.3 Cadena de consecuencias (ya verificada en los informes previos)

`0x6E8430 → 0xB0100002` ⇒ `0x61A9EA bne 0x61AA5C` ⇒ log `"isSupportContent : GetPlayThumbnailInfo"` ⇒
`0x61AA68 mov r0,r6` (=0) ⇒ `isSupportContent = 0` ⇒ `0x437C3C` «Detect UnSupported Content» ⇒ `status 0x1A`
⇒ DefObjPlayer 7 ⇒ caution `0x135` ⇒ **«No se puede visualizar.»** y **ninguna miniatura**.
Nada de esto depende del clip, del código de fecha, de la BD de imágenes ni de `TvSystem`.

---

## 5. Conclusión y verificación en cámara

### 5.1 La frase

> **Para que `0x6E8430` devuelva `0xB0100002` tiene que estar tomado —o muerto— el mutex
> `IfoSemaphore` del `mp4Ifo_If` que el MMgr creó en `0x6E80A4`/`0x6E8166`: `[handle+4]` apunta a un objeto
> cuyo byte `+4` vale 0, así que `0x5BAD00` responde `0xCA001001` sin abrir siquiera el MP4; el mundo
> "tomado por un hilo vivo" y el mundo "objeto liberado/zero" se distinguen mirando si
> `[obj+8]/[obj+0xC]/[obj+0x10]` son cero y si `[obj]` sigue siendo la vtable `0x8BBCF8`.**

### 5.2 Cómo se verifica en cámara (breakpoint + qué mirar)

**Punto de parada primario: `0x5BAD24`** (primer byte del camino de rechazo; alternativamente `0x5BAD1E`,
el `cmp sb,#0`).

| Registro/memoria | Qué es | Valor esperado si el diagnóstico es correcto |
|---|---|---|
| `r4` | `obj` = el `IfoSemaphore` | puntero válido, alineado a 4 |
| `[r4+0]` | vtable | **`base(libmpr) + 0x8BBCF8`** ⇒ objeto vivo; otra cosa ⇒ memoria reutilizada |
| `[r4+4]` | `m_free` | **0** (por eso estamos aquí) |
| `[r4+8]` | `m_pid` del dueño | `≠0` ⇒ hay dueño real · `0` ⇒ objeto muerto/zero |
| `[r4+0xC]` | `m_tid` del dueño | comparar con `r6` (tid del que pide) |
| `[r4+0x10]` | `m_cmd` del dueño | p.ej. `1` (dtor) o `0x23` (miniatura) |
| `[r4+0x14]` / `[r4+0x18]` | módulo/subtipo de log | `5` / `1..8` si es el `mp4Ifo_If` |
| `r8` / `r6` | **PID/TID del que pide** | si `[r4+8]==r8` y `[r4+0xC]==r6` ⇒ **reentrada del mismo hilo** (no recursivo) |
| `r5` | `cmd` del que pide | `0x23` en `0x6E845A`, `1` en el dtor |

**Árbol de decisión con esos cinco números:**

```
[obj] != base+0x8BBCF8 , o ([obj+8],[obj+0xC],[obj+0x10]) == (0,0,0)
        -> HIPÓTESIS B: objeto muerto (nunca construido o liberado y zero)
           · el dtor 0x6E81BC libera el semáforo y NO limpia [handle+4]  (0x6E81FA..0x6E8202)
           · buscar quién llamó a 0x67C784 (DestroySub) y si el handle quedó colgando
[obj+8] != 0 y [obj+0xC] != r6   -> HIPÓTESIS A: otro hilo lo tiene y no lo suelta (fuga/deadlock)
           · el TID del print dice exactamente qué hilo; localizarlo
[obj+8] != 0 y [obj+0xC] == r6   -> HIPÓTESIS C: el MISMO hilo reentró; un camino se fue sin
           · release (0x5BACB0). El recurso no es recursivo (0x5BAD00 no compara dueño).
```

**Puntos de parada auxiliares (para no quedarse en el síntoma):**

* `0x5BADC2` (`strb sb,[r4,#4]`) → **toda adquisición**; `r1`=cmd, `r8`/`r6` = pid/tid. Un `bt`/log aquí
  da la secuencia completa y delata al último que tomó el semáforo sin soltarlo.
* `0x5BACC6` (`strb r3,[r4,#4]`) → **toda liberación**; si aparece una liberación sin adquisición previa
  (o al revés), el par está descuadrado: es la firma del destructor `0x6E81BC`.
* `0x6E8166` (ctor) y `0x6E816A` (`[handle+4] = sem`) → confirma **qué instancia** está en uso y descarta
  que el handle sea de una generación anterior.
* `0x67C784` (`~mp4Ifo_If` desde el MMgr) → si se dispara **antes** de la reproducción, el handle del
  `AviMMgr` (`[avimMgr+0x734]`, cargado en `0x61A9BA`) puede ser colgante: comprobar si alguien lo pone a 0.

**En el log de la cámara** (misma salida que los `printf` de `IFOFRMWK`) tiene que aparecer, en este orden:

```
[Error] 0xCA001001  ... ifoFramework_Semaphore.cpp(0x8F)
ER_FAILED_ACQUIRE_SEMAPHORE
 ### REJECT PID = <pid del player> TID = <tid del player> CMD = 0x23
 ### ACTIVE PID = <pid dueño>     TID = <tid dueño>     CMD = <cmd con el que se tomó>
### mp4Ifo faild at mp4Ifo_If.cpp(0x1AF) ErrCd: 0xB0100002
isSupportContent : GetPlayThumbnailInfo ...
```

**Si esas cinco líneas no aparecen** al intentar reproducir, entonces `0x6E8430` **no** es el punto de fallo
en esa unidad y hay que volver a `0x437C2C` con el breakpoint puesto: es el discriminante más barato y no
necesita instrumentar nada.

---

## 6. Correcciones a informes previos

| Informe | Lo que decía | Lo verificado aquí |
|---|---|---|
| [sub-BD-tarjeta](film-pb-1-sub-bd-tarjeta-20261128.md) §3 | `0x5BACF4` era la continuación del acquire (¿init/liberación?) | `0x5BACF4` = **set_owner** (`+8/+0xC/+0x10`); el unlock es `0x5BACB0` |
| idem | `[this+4]` = "byte de inicialización" | `[this+4]` = **estado del mutex** (`1` libre / `0` tomado); los únicos `1` los ponen ctor y release |
| idem | `r1=0x23` = "recurso 0x23" | `0x23` = **cmd/caller-id** que se imprime en el diagnóstico (` CMD = `), no un índice de recurso |
| [sub-BD-tarjeta](film-pb-1-sub-bd-tarjeta-20261128.md) §3 | «hay un punto de fallo único, anterior a cualquier lectura del MP4» | **Se confirma**, y ahora se sabe que es un mutex con dueño, no un gate de init |

## 7. No verificado / siguiente paso

* **NO VERIFICADO**: qué escritor concreto deja el byte a 0 en la unidad del usuario. Está determinado
  *estáticamente* que solo puede ser (A) dueño vivo, (B) memoria muerta, (C) reentrada del mismo hilo, y
  el breakpoint de §5.2 lo resuelve en una pasada.
* **NO VERIFICADO**: que el TID del diagnóstico corresponda a un hilo identificable del player (los
  veneers `0x5FD72C`/`0x5FD738` → `0x11F020`/`0x11EAD8` son *thunks* ARM cuyo símbolo no está en `.symtab`;
  la identificación `getpid`/`gettid` es **INFERIDA** de que el propio código los imprime como `PID`/`TID`).
* **NO VERIFICADO**: si `[avimMgr+0x734]` se limpia al destruir el accessor (`0x67C784`). Si no se limpia,
  la hipótesis B pasa a ser la principal y el arreglo es de ciclo de vida, no de contención.

---

### Evidencia

| Fichero | Contenido |
|---|---|
| [libmpr-semaphore-tu.txt](evidence/film-pb-1-sub-ifoframework-20261126/libmpr-semaphore-tu.txt) | ctor `0x5BACD0`, `clear_owner` `0x5BACA2`, release `0x5BACB0`, `set_owner` `0x5BACF4`, acquire `0x5BAD00` completos + literales, cadenas y vtable |
| [libmpr-escritores-flag-y-llamadas.txt](evidence/film-pb-1-sub-ifoframework-20261126/libmpr-escritores-flag-y-llamadas.txt) | barrido de los 3 `strb [x,#4]`, censo 809/809/9, censo por TU, los 9 puntos de construcción |
| [libmpr-mp4ifoif-getplaythumbnail.txt](evidence/film-pb-1-sub-ifoframework-20261126/libmpr-mp4ifoif-getplaythumbnail.txt) | `0x6E8430` completo y el único camino que devuelve `0xB0100002` |
| [libmpr-mp4ifoif-ciclo-vida.txt](evidence/film-pb-1-sub-ifoframework-20261126/libmpr-mp4ifoif-ciclo-vida.txt) | `0x6E80A4` (creación, `new(0x1C)`, ctor), `0x6E81BC` (destrucción, release sin ownership, `delete(sem)` sin limpiar `[+4]`), llamantes |
| [libmpr-errorcodes.txt](evidence/film-pb-1-sub-ifoframework-20261126/libmpr-errorcodes.txt) | nombre de `0xCA001001`, ausencia de nombre para `0xB0100002`, familia `0xB01000xx`, logger `0x6F0A54`, cadena hasta `isSupportContent` |
