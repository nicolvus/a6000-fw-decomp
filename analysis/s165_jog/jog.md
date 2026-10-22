# S165 — el módulo `[JOG]`: el subsistema de rueda/joystick de la A6000 fw3.21

> Hito de **ingeniería inversa de firmware** (no confundir con S101/S102, línea del obturador).
> Sólo análisis de bytes: `analysis/rea-independent/input/av-cam.bin` (11 427 236 B,
> sha256 `b60c845c…9e56bb9`). Convención **vaddr = 0x43541000 + file_offset**.
> Método de referencias: **regla PIC estricta** (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`,
> canónica según `analysis/s106_imaging_cap/pic_xref_methodology.md`).

---

## 1. Resumen ejecutivo

`[JOG]` es el prefijo de traza del **subsistema de control de la rueda** de la A6000
(`Jog` = rueda/joystick). No es un módulo de captura: es la capa que

1. **sondea** la rueda (`JogFg`, `JogTpu`, `JogVGrip`) con un temporizador OSAL,
2. **traduce** el movimiento a un `key_code` de cámara + un delta en grados,
3. **emite** un evento de 12 bytes hacia la cola de eventos de la cámara.

Cifras (todas verificadas contra bytes, ver §7):

| magnitud | valor |
|---|---|
| cadenas `[JOG]` distintas | **14** |
| apariciones del token `[JOG]` en la imagen | **14** (1 por cadena, sin repeticiones) |
| sitios que referencian una cadena `[JOG]` (regla estricta) | **24** |
| funciones distintas que contienen esos 24 sitios | **12** |
| cadenas `[JOG]` muertas (sin referencia) | **0** |
| clases RTTI del subsistema | **4** (`JogDev`, `JogFg`, `JogTpu`, `JogVGrip`) + `JogKey`, `JogMain` (no polimórficas) |
| diferencias con A7S fw3.20 / A6300 fw2.01 | el token `[JOG]` **no aparece** en ninguna de las dos |

---

## 2. Qué es exactamente `[JOG]`

### 2.1 Base textual (no inventada)

El firmware **no** contiene el nombre de fichero fuente del módulo (ver §5). Lo que sí
contiene, y es la única base textual disponible:

* **Nombres de clase RTTI** (formato Itanium, longitud + nombre):
  `6JogDev` @`0x43c40f7d`, `5JogFg` @`0x43c4105c`, `6JogTpu` @`0x43c410b5`,
  `8JogVGrip` @`0x43c4113c`.
* **`__PRETTY_FUNCTION__`** (GCC), que da clase **y** método:
  `void JogMain::Exit()` @`0x43c40ec8`, `void JogMain::Init()` @`0x43c40edd`,
  `virtual void JogFg::Start(void (*)(), __uint32_t, __uint32_t)` @`0x43c4101e`,
  `virtual void JogTpu::Start(void (*)(), __uint32_t, __uint32_t)` @`0x43c41063`,
  `virtual void JogVGrip::Start(void (*)(), __uint32_t, __uint32_t)` @`0x43c410bd`,
  `void JogKey::SetDev(JogDev*, __uint8_t, __uint8_t, __uint8_t)` @`0x43c411df`,
  `bool JogKey::SendKeyEvent(__uint32_t, __uint32_t, __int32_t*)` @`0x43c41146`.
* **`VGrip` = "V Grip"** (empuñadura vertical) tiene base textual: la cadena
  `Vgrip_Snd` @`0x43c8fb2f` (nombre de cola de mensajes) y la etiqueta de interfaz
  `V Grip S1` @`0x43c8fbbe`, ambas apuntadas por punteros absolutos en la tabla de datos
  (`0x43fe8174` y `0x43fe8228`).

**NO se desarrollan las siglas `Fg` y `Tpu`**: no existe ninguna cadena en la imagen que
las expanda. Se dejan tal cual.

### 2.2 Jerarquía de clases (RTTI, verificado byte a byte)

| clase | typeinfo | base | vtable (address point) |
|---|---|---|---|
| `JogDev` | `0x43fdaaf4` | — (abstracta) | `0x43fbb640` |
| `JogFg` | `0x43fdaafc` | `JogDev` (`0x43fdaaf4`) | `0x43fbb660` |
| `JogTpu` | `0x43fdab08` | `JogDev` (`0x43fdaaf4`) | `0x43fbb680` |
| `JogVGrip` | `0x43fdab14` | `JogDev` (`0x43fdaaf4`) | `0x43fbb6a0` |

* Los typeinfo usan `__si_class_type_info` (vptr `0x43fd03d8`) con puntero a la clase base
  — herencia **pública y única**.
* `JogDev` es **abstracta**: sus 6 ranuras apuntan todas a `0x439b4145`, que es
  `__cxa_pure_virtual` (la cadena `'pure virtual method called\n'` está en `0x43bd4de4`).
* Ranuras de las clases derivadas (índice 0..5):

| ranura | `JogFg` | `JogTpu` | `JogVGrip` |
|---|---|---|---|
| 0 | `0x43a4a249` | `0x43a4a2c7` | `0x43a4a2ef` |
| 1 | `0x435aedd1` = `JogFg::Start` | `0x435af205` = `JogTpu::Start` | `0x435af621` = `JogVGrip::Start` |
| 2 | `0x435aed31` | `0x435af165` | `0x435af581` |
| 3 | `0x43a4a259` | `0x43a4a273` | `0x43a4a349` |
| 4 | `0x43a4a251` | `0x43a4a2b5` | `0x43a4a2f7` |
| 5 | `0x43a4a255` | `0x43a4a277` | `0x43a4a313` |

  Ranura 1 es `Start(void (*)(), u32, u32)` (verificado por la cadena `__PRETTY_FUNCTION__`
  referenciada dentro de esas funciones). Ranura 2 es la función que libera el temporizador
  (contiene la traza `[JOG]ERR. osal_free_timer…`).
  Ranuras 0/3/4/5 apuntan a una zona de código lejana (`0x43a4a2xx`–`0x43a4a3xx`) que
  **no contiene ninguna referencia a cadena**; es una zona de *stubs* compartidos (el
  mismo patrón aparece en `IllumiCam`, ranura 0 = `0x43a4a1c5`).

### 2.3 `JogMain` y `JogKey` (clases no polimórficas)

* `JogMain` — no tiene typeinfo (no es polimórfica). Es el **gestor/singleton**:
  `0x435aea24` es un *getter* perezoso (comprueba un flag global, construye el objeto con
  `0x43a4a228` y lo registra con `0x439b4244`) y devuelve su puntero. El módulo lo usa
  desde 22 sitios distintos.
* `JogKey` — no tiene typeinfo tampoco. Es el **traductor posición→evento**:
  guarda un `JogDev*`, un índice de `key_code`, y expone `SendKeyEvent()`.

---

## 3. Las 14 trazas (dirección exacta + referencias)

Todas están **contiguas** en `.rodata`: de `0x43c40eb4` a `0x43c411bd`.

| # | vaddr | file_offset | texto | sitios de referencia (regla estricta) | función(es) |
|---|---|---|---|---|---|
| 1 | `0x43c40eb4` | `0x6ffeb4` | `[JOG]JogMain::%s:%d` | `0x435ae5d4`, `0x435ae6ce` | `JogMain::Exit`, `JogMain::Init` |
| 2 | `0x43c40ef2` | `0x6ffef2` | `[JOG]ERR. osal_try_valloc_msg. err=0x%x, line=%d` | `0x435aeb42` | `JogMain::SendEvent` |
| 3 | `0x43c40f23` | `0x6fff23` | `[JOG]<Send Event> key_code = 0x%x, deg/sec = %d` | `0x435aeb74` | `JogMain::SendEvent` |
| 4 | `0x43c40f53` | `0x6fff53` | `[JOG]ERR. osal_snd_msg. err=0x%x, line=%d` | `0x435aebb4` | `JogMain::SendEvent` |
| 5 | `0x43c40f85` | `0x6fff85` | `[JOG]ERR. osal_free_timer. err=0x%x, line=%d` | `0x435aeda6`, `0x435af1da`, `0x435af5f6` | `JogFg::Exit`, `JogTpu::Exit`, `JogVGrip::Exit` |
| 6 | `0x43c40fb2` | `0x6fffb2` | `[JOG]JogFg::%s:%d` | `0x435aee00`, `0x435aef18` | `JogFg::Start` |
| 7 | `0x43c40fc4` | `0x6fffc4` | `[JOG]ERR. osal_alloc_timer. err=0x%x, line=%d` | `0x435aeeac`, `0x435af2e0`, `0x435af6fc` | `JogFg::Start`, `JogTpu::Start`, `JogVGrip::Start` |
| 8 | `0x43c40ff2` | `0x6ffff2` | `[JOG]ERR. osal_set_timer. err=0x%x, line=%d` | `0x435aeee6`, `0x435af31a`, `0x435af736` | `JogFg::Start`, `JogTpu::Start`, `JogVGrip::Start` |
| 9 | `0x43c410a2` | `0x7000a2` | `[JOG]JogTpu::%s:%d` | `0x435af234`, `0x435af34c` | `JogTpu::Start` |
| 10 | `0x43c410fe` | `0x7000fe` | `[JOG]JogVGrip::%s:%d` | `0x435af650`, `0x435af768` | `JogVGrip::Start` |
| 11 | `0x43c41113` | `0x700113` | `[JOG]UpdateDataFromVgrip SndErr, line=%d` | `0x435af890` | `JogVGrip::UpdateDataFromVgrip` |
| 12 | `0x43c41184` | `0x700184` | `[JOG]JogKey::%s:%d:0x%x,%d` | `0x435af990` | `JogKey::SetDev` |
| 13 | `0x43c4119f` | `0x70019f` | `[JOG]JogKey::%s:%d,pos:%d->%d` | `0x435afa0c` | `JogKey::SendKeyEvent` |
| 14 | `0x43c411bd` | `0x7001bd` | `[JOG]JogKey::%s:%d,Deg=0,Not Send` | `0x435afa66` | `JogKey::SendKeyEvent` |

Total: **24 sitios** (2+1+1+1+3+2+3+3+2+2+1+1+1+1 = 24). Las 14 cadenas están referenciadas
≥1 vez: **ninguna muerta**.

Además, dentro de la misma zona hay **10 referencias a cadenas `__PRETTY_FUNCTION__`**
(no `[JOG]`): `0x435ae5c2`, `0x435ae6ba`, `0x435aedf2`, `0x435aef0e`, `0x435af226`,
`0x435af342`, `0x435af642`, `0x435af75e`, `0x435af978`, `0x435afa0e`.

### 3.1 Mapa función → traza (12 funciones)

| inicio | fin | función | trazas `[JOG]` que contiene | nº |
|---|---|---|---|---|
| `0x435ae5bc` | `0x435ae616` | `JogMain::Exit` | `0x435ae5d4` | 1 |
| `0x435ae6b6` | `0x435ae846` | `JogMain::Init` | `0x435ae6ce` | 1 |
| `0x435aeb18` | `0x435aebd2` | `JogMain::SendEvent` | `0x435aeb42`, `0x435aeb74`, `0x435aebb4` | 3 |
| `0x435aed30` | `0x435aedc6` | `JogFg::Exit` | `0x435aeda6` | 1 |
| `0x435aedd0` | `0x435aef24` | `JogFg::Start` | `0x435aee00`, `0x435aeeac`, `0x435aeee6`, `0x435aef18` | 4 |
| `0x435af166` | `0x435af1fa` | `JogTpu::Exit` | `0x435af1da` | 1 |
| `0x435af204` | `0x435af358` | `JogTpu::Start` | `0x435af234`, `0x435af2e0`, `0x435af31a`, `0x435af34c` | 4 |
| `0x435af582` | `0x435af616` | `JogVGrip::Exit` | `0x435af5f6` | 1 |
| `0x435af620` | `0x435af774` | `JogVGrip::Start` | `0x435af650`, `0x435af6fc`, `0x435af736`, `0x435af768` | 4 |
| `0x435af848` | `0x435af8b2` | `JogVGrip::UpdateDataFromVgrip` | `0x435af890` | 1 |
| `0x435af968` | `0x435af9ae` | `JogKey::SetDev` | `0x435af990` | 1 |
| `0x435af9d0` | `0x435afa76` | `JogKey::SendKeyEvent` | `0x435afa0c`, `0x435afa66` | 2 |

(Nombres de `JogFg/JogTpu/JogVGrip::Start` y `::Exit` deducidos de la ranura de vtable que
ocupan y de la cadena `__PRETTY_FUNCTION__` que referencian; `JogMain::SendEvent`,
`JogVGrip::UpdateDataFromVgrip` y `JogKey::*` por su cadena `__PRETTY_FUNCTION__` o por el
texto de la traza.)

---

## 4. Funcionamiento reconstruido

### 4.1 `JogMain::Init` (`0x435ae6b6`) — montaje

```
0x435ae6ba  add r3, pc        -> 'void JogMain::Init()'
0x435ae6be  movs r3, #0x89    -> nº de línea del fuente = 137
0x435ae6ce  add r3, pc        -> '[JOG]JogMain::%s:%d'
0x435ae6d2  bl   0x435ae47c   -> LOG(id=0x106, nivel=0, ...)
0x435ae6d6  bl   0x435aea24   -> JogMain* (singleton)
0x435ae6e6  bl   0x435aea70   -> registra handler (key=1, ...)
0x435ae6ec  bl   0x435ae630
0x435ae70c  bl   0x43a4a3ba   -> ctor del JogKey (slot, índice, tipo)
0x435ae72c  bl   0x435af968   -> JogKey::SetDev(dev, u8, u8, u8)
0x435ae81c  blx  r7           -> dev->Start(callback, u32, flag)   [ranura 1 de la vtable]
```

* Construye **hasta 5** objetos `JogKey` en un array de 44 B (`0x43a4a3ba` → `this[0xc] = tipo`,
  `this[0x10] = 1`, `this[0x14] = 0`, `this[0x28] = 0`), y los enlaza con un `JogDev`
  mediante `JogKey::SetDev` (5 llamadas: `0x435ae72c`, `0x435ae76a`, `0x435ae7a2`,
  `0x435ae7d4`, `0x435ae7fc`).
* El `JogDev` concreto se elige con **dos tablas** (punteros a instancias) según el nibble
  alto del byte de configuración: `ite eq` en `0x435ae722`/`0x435ae760`/`0x435ae798`.
* Al final llama a `dev->Start(cb, u32, flag)` en **tres** dispositivos (`0x435ae81c`,
  `0x435ae82e`, `0x435ae840`): el **callback** es el que leen de la GOT.

### 4.2 `JogFg/JogTpu/JogVGrip::Start` — sondeo

* Registran un **temporizador OSAL** (`osal_alloc_timer` / `osal_set_timer`, trazas 7 y 8)
  y guardan el **callback** recibido en `Start`.
* En el error de `osal_alloc_timer`/`osal_set_timer` se registra con la traza
  `[JOG]ERR. osal_alloc_timer…` / `[JOG]ERR. osal_set_timer…`.
* En `::Exit` se libera el temporizador (`[JOG]ERR. osal_free_timer…`, traza 5).

### 4.3 `JogKey::SendKeyEvent` (`0x435af9d0`) — elTraductor

```
0x435af9de  ldr r1, [r4, #0x1c]
0x435af9e2  ldr r3, [r0]        ; vtable del JogDev
0x435af9e4  ldr r5, [r3, #0x14] ; ranura 5 (vfunc) -> devuelve la posición actual
0x435af9e8  blx  r5
0x435afa0c  add r3, pc         -> '[JOG]JogKey::%s:%d,pos:%d->%d'
0x435afa0e  add r6, pc         -> 'bool JogKey::SendKeyEvent(__uint32_t, __uint32_t, __int32_t*)'
0x435afa1a  bl   0x435af8bc    ; LOG
0x435afa1e  cbz r5, 0x435afa58 ; si delta == 0 ->
0x435afa66  add r3, pc         ; '[JOG]JogKey::%s:%d,Deg=0,Not Send'
0x435afa3a  bl   0x435aeb18    ; SendEvent(handle, key_code, 0)
0x435afa50  bl   0x435aeb18    ; SendEvent(handle, key_code, delta)
```

* Pide al `JogDev` (ranura 5) la **posición**; calcula el delta; si es 0 **no envía**
  ("Deg=0,Not Send") y devuelve 0.
* Si no es 0: envía **dos** eventos — primero con `deg = 0` (si la posición cambió) y
  después con `deg = delta`.

### 4.4 `JogMain::SendEvent` (`0x435aeb18`) — el emisor

```
0x435aeb22  ldr r0, [pc, #0xb0]   ; id de recurso OSAL = 0x011b02aa
0x435aeb26  movs r2, #0xc         ; tamaño del mensaje = 12
0x435aeb2a  bl   0x435612d0       ; osal_try_valloc_msg (dispatcher OSAL)
0x435aeb42  add r3, pc            ; '[JOG]ERR. osal_try_valloc_msg. err=0x%x, line=%d'  (línea 57)
0x435aeb64  str  r7, [r3]         ; msg[0] = key_code
0x435aeb66  str  r6, [r3, #4]     ; msg[1] = deg/sec
0x435aeb68  str  r0, [r3, #8]     ; msg[2] = err (0)
0x435aeb74  add r3, pc            ; '[JOG]<Send Event> key_code = 0x%x, deg/sec = %d'
0x435aeb8c  bl   0x435aea70       ; entrega el evento (registro de handler de 40 B, id=0x106)
0x435aeb94  bl   0x4356120c       ; libera el mensaje
0x435aebb4  add r3, pc            ; '[JOG]ERR. osal_snd_msg. err=0x%x, line=%d'  (línea 73)
```

El mensaje es de **12 bytes**: `{u32 key_code, u32 deg/sec, u32 err}`.

### 4.5 La tabla de `key_code` — `0x43fdab20`

```
0x435af9b8  ldr r3, [pc, #0xc]    ; GOT
0x435af9ba  ldr r2, [pc, #0x10]   ; índice en la GOT
0x435af9c0  ldr r2, [r0, #0xc]    ; índice del JogKey (byte en this+0xc)
0x435af9c2  ldr.w r0, [r3, r2, lsl #2]   ; key_code = tabla[indice]
```

La GOT base es `0x4401eee4`; `[GOT + 0x370c] = 0x43fdab20`. La tabla (6 × `u32`) es:

| índice | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| key_code | `0x11` (17) | `0x12` (18) | `0x16` (22) | `0x17` (23) | `0x14` (20) | `0x15` (21) |

Es **única en toda la imagen** (búsqueda del patrón de 6 `u32` → una sola coincidencia).
El índice lo fija el constructor (`0x43a4a3ba`: `str r2, [r0, #0xc]`), con valores
0,2,3,4,1 para los cinco dispositivos → key_codes `0x11`, `0x16`, `0x17`, `0x14`, `0x15`.
**La equivalencia semántica de esos códigos con funciones de cámara es NO VERIFICADO**
(no hay leyenda de key codes en el firmware ni en el repo).

### 4.6 `JogVGrip::UpdateDataFromVgrip` (`0x435af848`) — entrada desde la empuñadura

```
0x435af852  movs r2, #0xc     ; 12 bytes
0x435af856  bl   0x435612d0   ; osal_try_valloc_msg
0x435af890  add r3, pc        ; '[JOG]UpdateDataFromVgrip SndErr, line=%d'  (línea 239)
0x435af8a2  blx  0x439c5320   ; memcpy de 12 B a this+0xa
```

Recibe un bloque de **12 bytes** del grip vertical y lo reenvía. La cola de origen es la
del accessor **V Grip** (`Vgrip_Snd` @`0x43c8fb2f`, puntero absoluto en `0x43fe8174`).

### 4.7 A quién entrega y de dónde recibe (resumen)

```
   [JogFg/JogTpu/JogVGrip]  --(timer OSAL)-->  posición de rueda
                |
                v
        JogKey::SetDev / :SendKeyEvent        --calcula key_code + delta--
                |
                v
        JogMain::SendEvent  --(msg 12 B)-->  cola de eventos de cámara  (id 0x106)
```

* **Entrega**: `0x435aea70`, que registra un descriptor de **40 bytes** con
  `type = 2` e `id = 0x106 (262)`, más un `osal_snd_msg` (dispatcher `0x4356120c`).
  El `id 0x106` es el mismo que se usa como primer argumento de las llamadas de log
  (`mov.w r0, #0x106`), es decir, **el identificador de módulo/diagrama de traza**.
* **Recibe**: (a) la **posición** de la rueda a través de la ranura 5 de la vtable del
  `JogDev` (interfaz del dispositivo), y (b) los **12 bytes** del grip vertical a través
  de la cola `Vgrip_Snd` (`JogVGrip::UpdateDataFromVgrip`).
* La **cadena de eventos** de la cámara es la consumidora final; en el firmware no hay
  ninguna otra referencia a `[JOG]` (el bloque es autocontenido).

---

## 5. Ficheros fuente

**No hay ninguna cadena con nombre de fichero fuente asociada al módulo.**
Comprobado: la única aparición de la secuencia `jog` en toda la imagen A6000 (14
ocurrencias de `[JOG]` + 19 de nombres de clase/método) está en
`0x43c40eb4`–`0x43c411e4`; **ninguna** es un nombre de fichero (`*.cpp`, `*.h`).
El escaneo de referencias a cadena en todo el rango de código del módulo
(`0x435ae400`–`0x435afb00`) no devuelve **ningún** nombre de fichero: la única ruta
referenciada en esa zona es `cdcIf/CdcIfCtrl.cpp` @`0x43c41501`, que pertenece al
módulo siguiente (`TskAvif*`, a partir de `0x435afb38`).

Los únicos anclajes textuales son, por tanto:
* los **nombres de clase RTTI** (`6JogDev`, `5JogFg`, `6JogTpu`, `8JogVGrip`);
* las cadenas **`__PRETTY_FUNCTION__`** (`void JogMain::Exit()`, …);
* las **etiquetas de interfaz** `Vgrip_Snd` @`0x43c8fb2f` y `V Grip S1` @`0x43c8fbbe`,
  que sí dan el sentido de "empuñadura vertical" a `JogVGrip`.

---

## 6. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

Comparación sobre las tres imágenes `av-cam.bin` (rutas y sha256 en `jog.json`):

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[JOG]` | **14** apariciones | **0** | **0** |
| cadenas `[JOG]` distintas | 14 | 0 | 0 |
| `'Send Event'` / `'deg/sec'` | sí | **no** | **no** |
| `'JogKey'` (texto) | sí | **no** | **no** |
| clases RTTI `Jog*` | `JogDev`, `JogFg`, `JogTpu`, `JogVGrip` | `JogDev`, `JogFg`, `JogTpu`, **`JogVGrip`** | `JogDev`, **`JogCaif`**, `JogFg`, `JogTpu` (**sin** `JogVGrip`) |
| `Illumi*` | `IllumiDev`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400` | idéntico | idéntico |
| `McAssert` | sí | sí | sí |
| `Vgrip_Snd` / `V Grip S1` | sí | sí | sí |

**Lectura del diferencial**:

1. El **subsistema de rueda existe en las tres fw**: las clases `JogDev`/`JogFg`/`JogTpu`
   están presentes en A6000, A7S y A6300 (RTTI idéntico). Lo que es **propio de la A6000
   fw3.21 es la instrumentación de traza `[JOG]`** (y la clase `JogKey` con su
   `SendKeyEvent`). Es decir: la A6000Instrumentó este módulo con el prefijo `[JOG]`.
2. La **A7S** conserva `JogVGrip` (empuñadura vertical) igual que la A6000.
3. La **A6300** sustituye `JogVGrip` por **`JogCaif`** — misma posición en la tabla de
   typeinfo (`0x7ed44f` en la A6300, justo entre `6JogDev` y `5JogFg`), lo que sugiere
   que en la A6300 la rueda se toma por la interfaz **CAIF** en vez de por la empuñadura
   vertical. (Interpretación: NO VERIFICADA funcionalmente.)
4. El módulo hermano `[ILLUMI]` (`IllumiDev`/`IllumiAd`/`IllumiCam`/`IllumiRPR0400`,
   sensor de luz ambiente) está en las tres fw y, en la A6000, tiene una traza gemela:
   `[ILLUMI]<Send Event> key_code = 0x%x,Level:%d` @`0x43c40798` — mismo patrón de
   emisión de eventos por `key_code`.

---

## 7. Verificación y método

* **Regla de referencias**: estricta (`scan_pic_refs_strict.py`), verificada contra el
  mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json`.
* **Verificación a mano**: se desensamblaron y comprobaron **los 34 pares PIC** de la
  zona `0x435ae400`–`0x435afb00` (24 de cadenas `[JOG]` + 10 de `__PRETTY_FUNCTION__`),
  comprobando en cada caso: (a) el `ldr rX,[pc,#imm]` más cercano del mismo registro,
  (b) el valor literal en el pool, (c) `destino = literal + (add + 4)`, y (d) que el
  registro **no** se reescribe entre el `ldr` y el `add` (heurística de *kill analysis*,
  corregida: `movs/adds Rd,#imm` → `Rd = (h>>8)&7`). **Los 34 pares salen correctos
  ("ok")**, sin reutilización de registro. Script: `analysis/s165_jog/verify_pic.py`.
* **Ejemplo de verificación manual** (sitio `0x435aeb74`):
  `ldr r3,[pc,#0xa0]` @`0x435aeb6e` → pool `0x435aebdc` = `0x6923ab`;
  `add r3,pc` @`0x435aeb74` → `0x6923ab + 0x435aeb78 = 0x43c40f23` =
  `'[JOG]<Send Event> key_code = 0x%x, deg/sec = %d'`. ✓
* **RTTI**: los typeinfo y las vtables se leyeron byte a byte
  (`analysis/s165_jog/scan_jog_rtti.py`), incluidos los punteros a las clases base y la
  comprobación de que `0x439b4145` referencia `'pure virtual method called\n'`.
* Scripts del hito: `scan_jog_strings.py`, `scan_jog_funcs.py`, `scan_jog_table.py`,
  `scan_jog_bounds.py`, `scan_jog_callers.py`, `scan_jog_rtti.py`, `verify_pic.py`,
  `dasm.py`, `build_jog.py`.
* Tests: `tests/test_s165_jog.py` (comprueban bytes reales: si cambia una dirección,
  el test falla).

---

## 8. Interés para la línea del obturador

**El módulo `[JOG]` NO habla de obturación, de disparo, de lectura de sensor ni de tiempos
de exposición.** Ninguna de sus 14 trazas, ni ninguna de las 10 cadenas
`__PRETTY_FUNCTION__` de la zona, contiene `shutter`, `capture`, `exposure`, `sensor`,
`read` ni `frame`. Los únicos Temporizadores son los de **sondeo de la rueda**
(`osal_alloc_timer` / `osal_set_timer` / `osal_free_timer`).

Lo que sí es relevante para el usuario final (no para el obturador) es que
`[JOG]` es **la fuente de eventos de la rueda de control**: de ahí salen los `key_code`
`0x11`, `0x12`, `0x14`, `0x15`, `0x16`, `0x17` con deltas en grados. Si en el futuro se
quiere saber qué función de cámara ejecuta la rueda (p. ej. velocidad de obturación),
el punto de entrada es la **tabla de key codes `0x43fdab20`** y el emisor
`0x435aeb18`; el consumidor (la cola de eventos de cámara, id `0x106`) es el mismo
mecanismo que usan el `[ILLUMI]` y el `[TP_R]`.

---

## 9. NO VERIFICADO / abierto

1. **Nombre de fichero fuente** del módulo: no existe en la imagen (ver §5).
   NO VERIFICADO / no recuperable con las técnicas de este hito.
2. **Desarrollo de las siglas** `Fg` y `Tpu`: sin base textual. NO VERIFICADO.
   (`VGrip` sí tiene base textual: `Vgrip_Snd`, `V Grip S1`.)
3. **Significado de los `key_code`** `0x11`–`0x17`: no hay leyenda en el firmware ni en el
   repo. NO VERIFICADO.
4. **Qué cola OSAL concreta** recibe el mensaje de 12 B: los thunks de OSAL
   (`0x4356120c`, `0x435612d0`, `0x43561228`, `0x43561244`, `0x435612ec`, `0x43561298`)
   despachan por una tabla de API (offsets `0x1d4`…`0x1e8`); el identificador de recurso
   que se les pasa es la constante `0x011b02aa` (presente en 3 puntos de la imagen).
   NO VERIFICADO a qué cola corresponde.
5. **Identidad de las ranuras 0/3/4/5** de las vtables de `JogFg/JogTpu/JogVGrip`
   (código en `0x43a4a2xx`–`0x43a4a3xx`, sin ninguna referencia a cadena): NO VERIFICADO.
6. **El bloque `0x43a4a1xx`–`0x43a4a4xx`** parece ser una zona de *stubs*/objeto
   compartido usada por las familias `Illumi*` y `Jog*` (constructores de `JogKey` en
   `0x43a4a3ba`, máquina de estados de la rueda en `0x43a4a3fc`). Por qué el enlazador
   la coloca a 5 MB del código de `Jog`: NO VERIFICADO.
7. **Función de callback** pasada a `Start(cb, u32, u32)` en `0x435ae81c`/`0x435ae82e`/
   `0x435ae840`: se lee de la GOT (`[GOT+0x6884]`); su identidad NO VERIFICADA.
8. **`JogKey` en A7S/A6300**: no aparece el texto `JogKey` en ninguna de las dos; si la
   clase existe allí sin instrumentación, es NO VERIFICADO.
9. **Límite exacto de `JogMain::Exit`**: la función empieza en `0x435ae5bc` con 4 bytes de
   preámbulo (`ldr r3,[pc,#0x58]` @`0x435ae5bc`, `movs r2,#3` @`0x435ae5be`) antes del
   `push {r0,r1,r4,lr}` @`0x435ae5c0`. El inicio "limpio" en `0x435ae5c0` es NO VERIFICADO.

---

## 10. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 14 cadenas `[JOG]` en la A6000 fw3.21 entre `0x43c40eb4` y `0x43c411bd`
   (contiguas en `.rodata`); **0** en la A7S fw3.20 y el A6300 fw2.01 → comprobado con
   `bytes.count()`; `deg/sec` **1/0/0**.
2. **Estructura**: 14/14 referenciadas, **24 sitios** (regla estricta) en **12 funciones**; **0**
   cadenas muertas. Los **34 pares PIC** de la zona `0x435ae400`–`0x435afb00` (24 de `[JOG]` + 10
   de `__PRETTY_FUNCTION__`) se verificaron **a mano 34/34**, comprobando además que el registro
   no se reescribe entre el `ldr` y el `add` (kill analysis con la corrección
   `movs/adds Rd,#imm` → `Rd = (h>>8)&7`).
3. **Base textual y RTTI verificados**: las clases `JogDev`, `JogFg`, `JogTpu`, `JogVGrip` (RTTI
   leído byte a byte) están **en los tres firmware** (`JogDev` 2/1/1, `JogFg` 3/1/1,
   `JogTpu` 3/1/1) → el **subsistema de rueda ya existía**; lo propio de la fw3.21 es la
   **instrumentación** `[JOG]` y la clase `JogKey` (`JogKey` **5/0/0**).
4. **Diferencial con matiz propio (verificado)**: `JogVGrip` es **3/1/0** y `JogCaif` **0/0/1** →
   la A7S conserva la empuñadura vertical (`JogVGrip`) como la A6000, mientras que el **A6300 la
   sustituye por `JogCaif`** (la rueda se toma por la interfaz CAIF). El nombre de clase es
   común a las tres (`JogDev`/`JogFg`/`JogTpu`), luego es el **RTTI compartido** lo que prueba
   que el subsistema es común.
5. **Colateral útil**: el módulo hermano `[ILLUMI]` (sensor de luz ambiente, clases `IllumiDev`/
   `IllumiAd`/`IllumiCam`/`IllumiRPR0400` en las tres fw) emite en la A6000 una traza **gemela**
   `[ILLUMI]<Send Event> key_code = 0x%x,Level:%d` `0x43c40798` → mismo patrón de emisión de
   eventos por `key_code`, y `ILLUMI]` es **34/0/0**.
6. **Negativo acotado**: ninguna de las 14 trazas ni las 10 cadenas `__PRETTY_FUNCTION__` contiene
   `shutter`, `capture`, `exposure`, `sensor`, `read` ni `frame`; los únicos temporizadores son de
   **sondeo de la rueda** → **sin efecto en S51**. Punto de entrada futurejo: tabla de key codes
   `0x43fdab20` y emisor `0x435aeb18` (cola de eventos de cámara, id `0x106`).
