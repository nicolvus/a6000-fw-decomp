# S170 — el módulo `[ILLUMI]` (34 trazas): el subsistema de iluminación (sensor de luz ambiente)

> Hito de **ingeniería inversa de firmware** (línea general; sin relación con la línea del
> obturador S101/S102). Sólo análisis de bytes: `analysis/rea-independent/input/av-cam.bin`
> (A6000 fw3.21, 11 427 236 B, sha256 `b60c845c…9e56bb9` — ver `illumi.json`), comparado con la
> **A7S fw3.20** y el **A6300 fw2.01**.
> Convención: **vaddr = 0x43541000 + file_offset**.
> Referencias a cadenas: **regla PIC estricta** (canónica del repo,
> `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> Restricciones del proyecto: **sin firmware ejecutado, sin cámara, sin flasheo, sin REA/Ghidra**.
>
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. **NO VERIFICADO** = pendiente.

---

## 1. Resumen / veredicto

**`[ILLUMI]` es la instrumentación de traza del subsistema de iluminación de la cámara
(sensor de luz ambiente) y de su cadena de medida —auto-ganancia, filtrado, corrección
y niveles— que acaba emitiendo un evento de «nivel de luz» a la cola de eventos de la
cámara.** (La lectura «sensor de luz ambiente» es **INFERENCIA** sostenida por el
comportamiento medido; la sigla no se desarrolla en ninguna cadena: §2.1 y §9.1.)

Lo esencial del hito (todas las cifras verificadas contra bytes, §7):

| magnitud | valor |
|---|---|
| cadenas con el token `[ILLUMI]` | **34** (34 textos distintos, 34 ocurrencias) |
| rango de las cadenas | `0x43c40570` – `0x43c40ddc` (dentro del bloque de strings del módulo `0x43c4052a`–`0x43c40e89`) |
| sitios de emisión (pares PIC, regla estricta) | **52** |
| funciones emisoras | **25** |
| cadenas muertas (sin referencia) | **0** |
| pares PIC verificados a mano | **52 / 52** (sin reuso de registro) |
| clases RTTI del subsistema | **4** (`IllumiDev`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400`) |
| cadenas `__PRETTY_FUNCTION__` del bloque | **20** |
| diferencial del token `[ILLUMI]` | A6000 fw3.21 **34** / A7S fw3.20 **0** / A6300 fw2.01 **0** |

**Conclusión principal (corrige la lectura superficial de S130):** el *subsistema* de
iluminación **existe en las tres fw** (mismas clases RTTI, mismo código de acceso al
dispositivo); lo **propio de la fw3.21 de la A6000 es la instrumentación** (las 34 trazas
`[ILLUMI]` + las 20 cadenas `__PRETTY_FUNCTION__`). Ver §6.

---

## 2. Qué es exactamente `[ILLUMI]`

### 2.1 Base textual (sin inventar siglas)

No se desarrolla ninguna sigla: **`Illumi` no se expande en ninguna cadena de la
imagen**. Los únicos anclajes textuales son:

* **Nombres de clase RTTI** (formato Itanium, longitud + nombre):
  `9IllumiDev` @`0x43c4084c`, `8IllumiAd` @`0x43c40893`, `9IllumiCam` @`0x43c40a20`,
  `13IllumiRPR0400` @`0x43c40baf`.
* **Cadenas `__PRETTY_FUNCTION__`** (20), que dan clase **y** método:
  `static void IllumiDiag::Handler(void*, void*)` @`0x43c4052a`,
  `void IllumiDiag::Init()` @`0x43c406a4`, `void IllumiDiag::Exit()` @`0x43c40558`,
  `static void IllumiGain::JudgeGainChange()` @`0x43c406bc`,
  `bool IllumiLevel::CalcIllumiLevel()` @`0x43c40828`,
  `virtual void IllumiAd::Start(void (*)())` @`0x43c409ae`,
  `virtual void IllumiAd::Stop()` @`0x43c40857`,
  `virtual void IllumiAd::Exit()` @`0x43c40875`,
  `virtual void IllumiCam::Start(void (*)())` @`0x43c409d7`,
  `virtual void IllumiCam::Stop()` @`0x43c40a01`,
  `virtual void IllumiCam::Exit()` @`0x43c40a2b`,
  `virtual void IllumiRPR0400::Init()` @`0x43c40e38`,
  `virtual void IllumiRPR0400::Start(void (*)())` @`0x43c40be2`,
  `virtual void IllumiRPR0400::Stop()` @`0x43c40b8c`,
  `virtual void IllumiRPR0400::Exit()` @`0x43c40bbf`,
  `static OSAL_ERR IllumiRPR0400::ReadDevice(__uint16_t, __uint8_t, __uint8_t*, __uint8_t)` @`0x43c40adb`,
  `static OSAL_ERR IllumiRPR0400::WriteDevice(__uint16_t, __uint8_t, __uint8_t*, __uint8_t)` @`0x43c40b33`,
  `static __uint16_t IllumiRPR0400::GetAD()` @`0x43c40e0f`,
  `static bool IllumiRPR0400::PollingDevice()` @`0x43c40e89`,
  `static void IllumiRPR0400::InitializeDevice()` @`0x43c40e5b`.
* **Las propias trazas**: `GetRawData`, `GetIllumiData`, `ADwork`, `ADcor`, `AD MAXOVER`,
  `C_AD`, `gain`, `gain_pre`, `Gain Change Complete!`, `<Send Event> key_code = 0x%x,Level:%d`.

`IllumiDiag`, `IllumiGain` e `IllumiLevel` **no tienen typeinfo** → clases no
polimórficas (igual que `JogMain`/`JogKey` de S165).

### 2.2 Qué hace (reconstrucción por los bytes)

El subsistema mide la **iluminancia ambiente** con un sensor dedicado y produce un
**nivel** (0..N) que se publica como evento de cámara:

```
  IllumiRPR0400 (chip de sensor)  ── bus OSAL 0x520250 ──┐
      ReadDevice(0x39, 0x46, buf, 4)  → AD crudo (u16)  │
                                                        ▼
  IllumiAd / IllumiCam  ── timer OSAL (periodo 0x4e20) ──►  Illumi::TareaPeriodica (0x435ad680)
                                                        │      1. lee AD del servicio LIRO ADC (0x720018, msg 0xfff0)
                                                        │      2. media móvil de 4 muestras (0x435ad574)
                                                        │      3. corrección C_AD (0x435ad4dc)
                                                        │      4. JudgeGainChange (0x435acb90) → auto-ganancia por GPIO
                                                        │      5. CalcIllumiLevel (0x435acf00) → índice de nivel
                                                        ▼
                        IllumiLevel::SendEvent (0x435acdd0)
                            mensaje de 16 B {u32 key_code, u32 0, u32 Level, u32 0}
                            → cola de eventos de cámara OSAL 0x7a0020
```

Evidencia puntual (todas con dirección):

* **El mensaje de evento** se construye en `0x435ace00`-`0x435ace0a`:
  `str r0,[r3,#4]` (msg[1]=0), `str r5,[r3,#8]` (msg[2]=Level), `str r0,[r3,#0xc]`
  (msg[3]=0), `str r6,[r3]` (msg[0]=key_code); tamaño `movs r2,#0x10` (16 B) en
  `0x435acdda`; envío con `osal_snd_msg` en `0x435ace1c` sobre el id **`0x7a0020`**
  (`ldr r0,[pc,#0x28]` @`0x435ace18`, pool `0x435ace44` = `0x7a0020`).
* **La cola `0x7a0020` es la cola de eventos/“key” de la cámara**: el módulo de
  accesorios `[ACCY]` envía al **mismo** id y con el **mismo** formato de 16 B
  `{KeyCode, 0, State, Info}` (`0x43565846`-`0x43565854`, traza
  `[ACCY][DEBUG][BASE]:%d:NotifyInput...KeyCode:%08X, State:%d, INFO:%d` @`0x43c25593`).
* **Los `key_code` que usa `[ILLUMI]` son `0x17000001` y `0x17000002`**
  (pool `0x435abe38` = `0x17000001`, pool `0x435abe34` = `0x17000002`), escritos en el
  objeto de nivel con `str r1,[r0,#0x24]` (`0x43a4a100`). Son las **únicas dos
  apariciones de esos valores en toda la imagen** → el consumidor final no es
  localizable por literal (ver §9, punto 3).

### 2.3 La cadena de medida del ADC (relación con S166 / `[ADC_DEBUG]`)

El `[ILLUMI]` **es cliente del servicio LIRO ADC**, tal como ya verificó S166 (§4.3):

* `0x435ad474` — **`Illumi::LeerAD_del_LIRO()`**:
  `ldr r0,[pc,#0x44]` @`0x435ad47c` → pool `0x435ad4c4` = **`0x720018`** (handle del
  servicio LIRO ADC, el mismo que S166 documentó); `movs r2,#8` (8 B);
  `osal_try_valloc_msg` @`0x435ad47e`; `movw r3,#0xfff0` @`0x435ad486` (**id de mensaje
  `0xfff0` = comando ADJ `get_d` del ADC**, ver S166); `str r3,[r5]` @`0x435ad48e`
  (msg[0]=0xfff0); `bl 0x43561228` @`0x435ad4a6` (**`osal_snd_sync_msg`**, el punto que
  S166 señaló); el valor de 16 bits se lee de `msg[6]` (`ldrh r5,[r5,#6]` @`0x435ad4aa`)
  y se guarda en el global `0x4401b9fc` (`strh r5,[r6]` @`0x435ad4b0`).
* El canal del ADC y el "código de corrección" son dos bytes globales tomados de la GOT:
  `strb r3,[r5,#4]` @`0x435ad49c` (canal) y `strb r3,[r5,#5]` @`0x435ad4a4`.
* Sobre el valor leído se aplican dos pasos: la **corrección** `C_AD` (§2.4) y el
  **filtrado** (§2.5). Los nombres `ADwork` y `ADcor` que aparecen en las trazas son
  los de las variables de trabajo del bloque; su equivalencia exacta con los globals
  (GOT+`0x61c8` → `0x43f6133a`, GOT+`0x64dc` → `0x43e4e608`, …) es NO VERIFICADO
  (§9.8).

### 2.4 Corrección (`C_AD`) y saturación (`AD MAXOVER`)

`0x435ad4dc` — **`Illumi::C_AD()`** (interpolación lineal de dos puntos de calibración):

```
0x435ad4ee  cmp r1, r2            ; compara los dos puntos de calibración
0x435ad4f0  beq 0x435ad554        ; iguales → devuelve 0xffff
0x435ad4fe  mul r5, r1, r3        ; x1*y2
0x435ad502  subs r3, r4, r3       ; x2-x1
0x435ad504  subs r1, r1, r2       ; x1-x2
0x435ad506  mls r5, r2, r4, r5    ; y2*x2 - x1*y2
0x435ad50a  mla r0, r3, r0, r5    ; + (x2-x1)*AD
0x435ad50e  bl 0x4355faf0         ; conversión a u16
0x435ad512  movw r3, #0xfffe
0x435ad516  cmp r0, r3
0x435ad518  bhi 0x435ad51e        ; > 0xfffe → saturación
0x435ad51e  mov.w r3, #0x116      ; línea 278
0x435ad530  add r3, pc            ; '[ILLUMI]AD MAXOVER. ADwork=0x%x, line=%d'  (imprime r0)
0x435ad536  mov.w r3, #0x11a      ; línea 282
0x435ad54a  add r3, pc            ; '[ILLUMI]C_AD. ADcor=0x%x, line=%d'  (imprime 0xffff)
```

Los cuatro puntos de calibración (`v0`..`v3`) se leen en `0x435ad600` (inicialización)
desde una tabla de configuración y se guardan en los globals GOT+`0x5da8`
(`0x43e4e614`), GOT+`0x6ff8` (`0x43e4e60c`), GOT+`0x6b24` (`0x43e4e61c`) y
GOT+`0x55f4` (`0x43e4e5e0`); se ponen a cero en `0x435ad658`.

### 2.5 Filtrado

`0x435ad574` — **media móvil de 4 muestras** sobre el AD: guarda la muestra nueva en
`[r3+6]`, desplaza `[r3+2]→[r3]`, `[r3+4]→[r3+2]`, `[r3+6]→[r3+4]` y devuelve
`(ant4+ant3+ant2+nueva)>>2` (`lsrs r0,r0,#2` @`0x435ad5a2`).

### 2.6 Auto-ganancia (`IllumiGain`)

`0x435acb90` — **`IllumiGain::JudgeGainChange()`**: compara el AD con una **tabla de
umbrales por ganancia** (`ldrh r3,[r0,r5,lsl #2]` @`0x435acbc0`, base en GOT+`0xfd4`):

* si `umbral[ganancia] > AD` (demasiado oscuro) → sube el **contador** de ganancia
  (`0x435acbd2`-`0x435acbd6`); al alcanzar el máximo (`cmp r3,r1` @`0x435acbdc`)
  incrementa la ganancia (`adds r5,#1` @`0x435acbe0`) y llama a
  `SetGainMode(ganancia+1)` (`bl 0x435aca80` @`0x435acbe8`);
* si `umbral[ganancia] <= AD` → ruta simétrica a la baja (`0x435acc0e`), con
  `umbral[ganancia+1]` como segundo umbral (histéresis).

`0x435aca80` — **`IllumiGain::SetGainMode(u8)`** escribe el modo de ganancia
(`strb r4,[r3]` @`0x435acb42`, global GOT+`0x6688` → `0x43f90edb`) y lo registra junto
a `gain_pre`, leído de otro global (GOT+`0x7438` → `0x43f90ee2`, `ldrb r3,[r3]`
@`0x435acb4a`); la relación exacta entre ambos es NO VERIFICADO (§9.8). Además
**acciona dos GPIO** por modo (tabla de 4 identificadores
`0xf901a5`, `0xf901a6`, `0xf901a7`, `0xf901a8` en los pools `0x435acb6c`-`0x435acb78`;
se resuelven con el servicio de nombres en `0x43561508` → `GOT[0x16dc]->vtable[0x2e0]`, y
se escriben con `0x43b5e2a4` = GPIO a 1 / `0x43b5e2b0` = GPIO a 0). Los modos válidos son
`0`, `1`, `2` y `0xff` (`cmp r4,#1/2/0xff` @`0x435acb58`-`0x435acb64`); cualquier otro →
`'[ILLUMI]Parameter Err: gainMode = 0x%X'` @`0x43c406e6`.

### 2.7 Cálculo del nivel (`IllumiLevel`)

`0x435acf00` — **`IllumiLevel::CalcIllumiLevel()`**:

* llama a la ranura 4 de la vtable del dispositivo (`ldr r3,[r3,#0x10]` @`0x435acf16`,
  `blx r3` @`0x435acf18`) → **AD crudo**; si es 0 marca error (`strb r3,[r4,#4]` con
  `r3=2` @`0x435acfac`);
* compara el AD con la ventana del nivel actual (`this[4]` = índice de nivel):
  `ldrh r0,[r1,#6]` (umbral bajo) y `ldrh r1,[r1,#8]` (umbral alto) con
  `r1 = this + 4*índice` (`add.w r1,r4,r2,lsl #2` @`0x435acf24`);
* con histéresis y **contadores** (`this[0x28]`, `this[0x2c]`, máximo en `this[0x30]`)
  ajusta el índice de nivel: si el AD queda **por debajo** del umbral bajo
  (`lo > AD`, `0x435acf2c` no salta) el índice **baja** (`subs r2,#1` @`0x435acf3e`,
  traza con línea 199 = `0xc7`); si el AD queda **por encima** del umbral alto
  (`hi < AD`, `0x435acf68` no salta) el índice **sube** (`adds r2,#1` @`0x435acf7a`,
  traza con línea 208 = `0xd0`);
* traza `'[ILLUMI]IllumiLevel::%s:%d--Level:%d,Data:(0x%04x)%x'` (`0x43c407f3`) en
  ambos sentidos.

La tabla de umbrales y la tabla de bytes de "nivel" por índice se montan en
`0x43a4a144` (6 niveles, `cmp r4,#0x18` @`0x43a4a182`) a partir de bloques de
configuración leídos por `0x435ac3b4` (variante u16 en `0x435ac3f6`-`0x435ac436` y
variante u8 en `0x435ac46c`-`0x435ac4d4`).

### 2.8 El dispositivo `IllumiRPR0400`

Clase concreta de sensor, con acceso por un bus OSAL propio (**`0x520250`**):

* `IllumiRPR0400::ReadDevice(u16 addr, u8 len, u8* buf, u8* err)` @`0x435ade38`:
  `osal_try_valloc_msg(0x520250, …)` @`0x435ade5e`, mensaje propio con cabecera y
  payload, `osal_snd_sync_msg(0x520250, msg)` @`0x435adf00` y `osal_free_msg`
  @`0x435adf2a`.
* `IllumiRPR0400::GetAD()` @`0x435adffc`: **`ReadDevice(0x39, 0x46, &buf, 4)`**
  (`movs r0,#0x39` @`0x435adffe`, `movs r1,#0x46` @`0x435ae000`, `movs r3,#4`
  @`0x435ae004`) → **el registro `0x46` del dispositivo `0x39` contiene el valor del
  ADC de luz**; el resultado u16 se guarda en el global `0x4401b9fe`
  (`strh r2,[r3]` @`0x435ae03c`).
* `IllumiRPR0400::PollingDevice()` @`0x435ae058`: `ReadDevice(0x39, 0x41, &buf, 1)`
  (`movs r1,#0x41` @`0x435ae062`) → registro de estado.
* `IllumiRPR0400::InitializeDevice()` @`0x435ae228`: lee **backup ids** `0x133003d` y
  `0x133003c` (`ldr r0,[pc,#0x80]` @`0x435ae22e` → pool `0x435ae2b0` = `0x133003d`;
  `ldr r0,[pc,#0x58]` @`0x435ae258` → pool `0x435ae2b4` = `0x133003c`) con
  `Backup_read` (`0x435613b0`) y escribe el bloque con `WriteDevice`.
* `IllumiRPR0400::WriteDevice(...)` @`0x435ae0a8`: mismo bus, `osal_valloc_msg` +
  `osal_snd_msg`.

---

## 3. Las 34 trazas (dirección exacta + sitio de referencia)

`addr` = dirección de la cadena; `sitio` = dirección del `add rX,pc` (regla PIC estricta,
verificada a mano en §7).

| # | addr | texto | sitio(s) | función emisora |
|---|---|---|---|---|
| 1 | `0x43c40570` | `[ILLUMI]ADJ BLOCK ERROR` | `0x435abf90` | `IllumiDiag::Handler` |
| 2 | `0x43c40588` | `[ILLUMI]IllumiDiag::%s:%d,GetRawData Success=%ld` | `0x435ac038` | `IllumiDiag::Handler` |
| 3 | `0x43c405b9` | `[ILLUMI]IllumiDiag::%s:%d,GetIllumiData Success=%ld` | `0x435ac056` | `IllumiDiag::Handler` |
| 4 | `0x43c405ed` | `[ILLUMI]IllumiDiag::%s:%d,GetRawData Error=%ld` | `0x435ac08c` | `IllumiDiag::Handler` |
| 5 | `0x43c4061c` | `[ILLUMI]ADJ COMMAND ERROR` | `0x435ac0c2` | `IllumiDiag::Handler` |
| 6 | `0x43c40636` | `[ILLUMI]IllumiDiag::%s:%d,reg_sync_msg_queue Err=0x%x` | `0x435ac164` | `IllumiDiag::Init` |
| 7 | `0x43c4066c` | `[ILLUMI]IllumiDiag::%s:%d,unreg_sync_msg_queue Err=0x%x` | `0x435ac1a8` | `IllumiDiag::Exit` |
| 8 | `0x43c406e6` | `[ILLUMI]Parameter Err: gainMode = 0x%X` | `0x435acb32` | `IllumiGain::SetGainMode` |
| 9 | `0x43c4070d` | `[ILLUMI]gain = 0x%02X, gain_pre = 0x%02X` | `0x435acb50` | `IllumiGain::SetGainMode` |
| 10 | `0x43c40736` | `[ILLUMI]IllumiGain::%s:%d--Gain:%d, AD:0x%04X` | `0x435acc0a`, `0x435acc58` | `IllumiGain::JudgeGainChange` |
| 11 | `0x43c40764` | `[ILLUMI]ERR. osal_try_valloc_msg. err=0x%x, line=%d` | `0x435acdf6` | `IllumiLevel::SendEvent` |
| 12 | `0x43c40798` | `[ILLUMI]<Send Event> key_code = 0x%x,Level:%d` | `0x435ace10` | `IllumiLevel::SendEvent` |
| 13 | `0x43c407c6` | `[ILLUMI]ERR. osal_snd_msg. err=0x%x, line=%d` | `0x435ace3c` | `IllumiLevel::SendEvent` |
| 14 | `0x43c407f3` | `[ILLUMI]IllumiLevel::%s:%d--Level:%d,Data:(0x%04x)%x` | `0x435acf56`, `0x435acf94` | `IllumiLevel::CalcIllumiLevel` |
| 15 | `0x43c4089d` | `[ILLUMI]IllumiAd::%s:%d` | `0x435ad138`, `0x435ad19a`, `0x435ad238` | `IllumiAd::Stop/Start/Exit` |
| 16 | `0x43c408b5` | `[ILLUMI]ERR. osal_set_timer. err=0x%x, line=%d` | `0x435ad182`, `0x435adbc2` | `IllumiAd::Start`, `IllumiRPR0400::Start` |
| 17 | `0x43c408e4` | `[ILLUMI]ERR. osal_free_timer. err=0x%x, line=%d` | `0x435ad25a`, `0x435adcc8` | `IllumiAd::Exit`, `IllumiRPR0400::Exit` |
| 18 | `0x43c40914` | `[ILLUMI]ERR. osal_alloc_timer. err=0x%x, line=%d` | `0x435ad344`, `0x435ae422` | `IllumiAd` (ranura 0), `IllumiRPR0400::Init` |
| 19 | `0x43c40945` | `[ILLUMI]AD MAXOVER. ADwork=0x%x, line=%d` | `0x435ad530` | `Illumi::C_AD` |
| 20 | `0x43c4096e` | `[ILLUMI]C_AD. ADcor=0x%x, line=%d` | `0x435ad54a` | `Illumi::C_AD` |
| 21 | `0x43c40990` | `[ILLUMI]Gain Change Complete!` | `0x435ad6aa` | `Illumi::TareaPeriodica` |
| 22 | `0x43c40a4a` | `[ILLUMI]IllumiCam::%s:%d` | `0x435ad7ca`, `0x435ad814`, `0x435ad878` | `IllumiCam::Exit/Stop/Start` |
| 23 | `0x43c40a63` | `[ILLUMI]ERR. osal_unreg_sync_msg_queue_cb. err=0x%x, line=%d` | `0x435ad7fe` | `IllumiCam::Stop` |
| 24 | `0x43c40aa0` | `[ILLUMI]ERR. osal_reg_sync_msg_queue_cb. err=0x%x, line=%d` | `0x435ad862` | `IllumiCam::Start` |
| 25 | `0x43c40c10` | `[ILLUMI]IllumiRPR0400::%s:%d` | `0x435adb30`, `0x435adbda`, `0x435adcb4` | `IllumiRPR0400::Stop/Start/Exit` |
| 26 | `0x43c40c2d` | `[ILLUMI]IllumiRPR0400::%s. osal_try_valloc_msg. err=0x%x:%d` | `0x435ade7e` | `IllumiRPR0400::ReadDevice` |
| 27 | `0x43c40c69` | `[ILLUMI]IllumiRPR0400::%s. osal_snd_sync_msg. err=0x%x:%d` | `0x435adf18` | `IllumiRPR0400::ReadDevice` |
| 28 | `0x43c40ca3` | `[ILLUMI]IllumiRPR0400::%s. osal_free_msg. err=0x%x:%d` | `0x435adf48`, `0x435adfc2`, `0x435ae190`, `0x435ae1ec` | `ReadDevice`, `WriteDevice` |
| 29 | `0x43c40cd9` | `[ILLUMI]IllumiRPR0400::%s. hdr->err=0x%x:%d` | `0x435adf98`, `0x435ae1c2` | `ReadDevice`, `WriteDevice` |
| 30 | `0x43c40d05` | `[ILLUMI]IllumiRPR0400::%s:%d. ReadDevice err=0x%x` | `0x435ae024`, `0x435ae088` | `GetAD`, `PollingDevice` |
| 31 | `0x43c40d37` | `[ILLUMI]IllumiRPR0400::%s. osal_valloc_msg. err=0x%x:%d` | `0x435ae0f0` | `IllumiRPR0400::WriteDevice` |
| 32 | `0x43c40d6f` | `[ILLUMI]IllumiRPR0400::%s. osal_snd_msg. err=0x%x:%d` | `0x435ae160` | `IllumiRPR0400::WriteDevice` |
| 33 | `0x43c40da4` | `[ILLUMI]IllumiRPR0400::%s:%d. Backup_read ret_size=0x%x` | `0x435ae252`, `0x435ae27c`, `0x435ae360` | `InitializeDevice`, `Init` |
| 34 | `0x43c40ddc` | `[ILLUMI]IllumiRPR0400::%s:%d. WriteDevice err=0x%x` | `0x435ae2a6` | `IllumiRPR0400::InitializeDevice` |

Total: **52 sitios** (1+1+1+1+1+1+1+1+1+2+1+1+1+2+3+2+2+2+1+1+1+3+1+1+3+1+1+4+2+2+1+1+3+1 = 52).
**Ninguna cadena muerta** (34/34 referenciadas ≥1 vez).

---

## 4. Mapa función → traza (25 funciones)

| inicio | fin (aprox.) | función | trazas `[ILLUMI]` | nº |
|---|---|---|---|---|
| `0x435abf7a` | `0x435ac138` | `IllumiDiag::Handler(void*, void*)` | 5 | 5 |
| `0x435ac138` | `0x435ac184` | `IllumiDiag::Init()` | `0x435ac164` | 1 |
| `0x435ac184` | `0x435ac230` | `IllumiDiag::Exit()` | `0x435ac1a8` | 1 |
| `0x435aca80` | `0x435acb90` | `IllumiGain::SetGainMode(u8)` | `0x435acb32`, `0x435acb50` | 2 |
| `0x435acb90` | `0x435acdd0` | `IllumiGain::JudgeGainChange()` | `0x435acc0a`, `0x435acc58` | 2 |
| `0x435acdd0` | `0x435acf00` | `IllumiLevel::SendEvent(handle, level, key_code)` | `0x435acdf6`, `0x435ace10`, `0x435ace3c` | 3 |
| `0x435acf00` | `0x435ad0fc` | `IllumiLevel::CalcIllumiLevel()` | `0x435acf56`, `0x435acf94` | 2 |
| `0x435ad0fc` | `0x435ad150` | `IllumiAd::Stop()` | `0x435ad138` | 1 |
| `0x435ad150` | `0x435ad1b8` | `IllumiAd::Start(void (*)())` | `0x435ad182`, `0x435ad19a` | 2 |
| `0x435ad1b8` | `0x435ad270` | `IllumiAd::Exit()` | `0x435ad238`, `0x435ad25a` | 2 |
| `0x435ad270` | `0x435ad4dc` | `IllumiAd` (ranura 0 de la vtable) | `0x435ad344` | 1 |
| `0x435ad4dc` | `0x435ad574` | `Illumi::C_AD()` | `0x435ad530`, `0x435ad54a` | 2 |
| `0x435ad680` | `0x435ad7ac` | `Illumi::TareaPeriodica()` (callback del temporizador) | `0x435ad6aa` | 1 |
| `0x435ad7ac` | `0x435ad7dc` | `IllumiCam::Exit()` | `0x435ad7ca` | 1 |
| `0x435ad7dc` | `0x435ad82c` | `IllumiCam::Stop()` | `0x435ad7fe`, `0x435ad814` | 2 |
| `0x435ad82c` | `0x435adaf4` | `IllumiCam::Start(void (*)())` | `0x435ad862`, `0x435ad878` | 2 |
| `0x435adaf4` | `0x435adb90` | `IllumiRPR0400::Stop()` | `0x435adb30` | 1 |
| `0x435adb90` | `0x435adc38` | `IllumiRPR0400::Start(void (*)())` | `0x435adbc2`, `0x435adbda` | 2 |
| `0x435adc38` | `0x435ade38` | `IllumiRPR0400::Exit()` | `0x435adcb4`, `0x435adcc8` | 2 |
| `0x435ade38` | `0x435adffc` | `IllumiRPR0400::ReadDevice(u16,u8,u8*,u8*)` | `0x435ade7e`, `0x435adf18`, `0x435adf48`, `0x435adf98`, `0x435adfc2` | 5 |
| `0x435adffc` | `0x435ae058` | `IllumiRPR0400::GetAD()` | `0x435ae024` | 1 |
| `0x435ae058` | `0x435ae0a8` | `IllumiRPR0400::PollingDevice()` | `0x435ae088` | 1 |
| `0x435ae0a8` | `0x435ae228` | `IllumiRPR0400::WriteDevice(u16,u8,u8*,u8*)` | `0x435ae0f0`, `0x435ae160`, `0x435ae190`, `0x435ae1c2`, `0x435ae1ec` | 5 |
| `0x435ae228` | `0x435ae328` | `IllumiRPR0400::InitializeDevice()` | `0x435ae252`, `0x435ae27c`, `0x435ae2a6` | 3 |
| `0x435ae328` | `0x435ae500` | `IllumiRPR0400::Init()` | `0x435ae360`, `0x435ae422` | 2 |

Suma = **52** sitios en **25** funciones.

Además, dentro de la misma zona de código hay **31 sitios que referencian 20 cadenas
`__PRETTY_FUNCTION__`** distintas (no `[ILLUMI]`), que son las que dan nombre a las
funciones: `0x435ac018`, `0x435ac07c`, `0x435ac156`, `0x435ac19a`, `0x435acbf4`,
`0x435acc42`, `0x435acf4e`, `0x435acf8a`, `0x435ad12e`, `0x435ad190`, `0x435ad22e`,
`0x435ad7c0`, `0x435ad80a`, `0x435ad86e`, `0x435adb26`, `0x435adbd0`, `0x435adcaa`,
`0x435ade70`, `0x435adf1e`, `0x435adf8c`, `0x435adfb4`, `0x435ae014`, `0x435ae078`,
`0x435ae0e2`, `0x435ae166`, `0x435ae1b6`, `0x435ae1de`, `0x435ae244`, `0x435ae26e`,
`0x435ae298`, `0x435ae352`.

---

## 5. Clases (RTTI) y jerarquía — verificado byte a byte

| clase | typeinfo | vptr | base | vtable (address point) | ranuras |
|---|---|---|---|---|---|
| `IllumiDev` | `0x43fdaa74` | `0x43fd04f8` (`__class_type_info`) | — | `0x43fbb5c0` | 5 × `0x439b4145` (`__cxa_pure_virtual`) → **abstracta** |
| `IllumiAd` | `0x43fdaa7c` | `0x43fd03d8` (`__si_class_type_info`) | `IllumiDev` | `0x43fbb5e0` | `0x435ad271`, `0x435ad151`, `0x435ad0fd`, `0x435ad1b9`, `0x435ad5e9` |
| `IllumiCam` | `0x43fdaa8c` | `0x43fd03d8` | `IllumiDev` | `0x43fbb600` | `0x43a4a1c5`, `0x435ad82d`, `0x435ad7dd`, `0x435ad7ad`, `0x435ad9f9` |
| `IllumiRPR0400` | `0x43fdaa98` | `0x43fd03d8` | `IllumiDev` | `0x43fbb620` | `0x435ae329`, `0x435adb91`, `0x435adaf5`, `0x435adc39`, `0x435ade21` |

* Las 5 ranuras virtuales coinciden en número y orden en las tres fw (ver §6) → la
  interfaz es estable. Sus nombres (deducidos de las cadenas `__PRETTY_FUNCTION__` de la
  A6000) son: ranura 0 = *Init*, 1 = *Start*, 2 = *Stop*, 3 = *Exit*, 4 = *GetAD*.
* Herencia **pública y única** (`__si_class_type_info`).
* `IllumiDev` es abstracta (todas sus ranuras son `__cxa_pure_virtual` @`0x439b4145`).

Adyacente a los typeinfo hay una **tabla de 19 identificadores OSAL `0x10600xx`**
(`0x43fdaaa4`–`0x43fdaaec`): `0x1060000, 0x1060003..0x1060005, 0x1060007..0x106000e,
0x106000f..0x1060015` (faltan `0x1060001`, `0x1060002`, `0x1060006`). **Presente
idéntica en las tres fw** (A7S `0x43fdbaf0`, A6300 `0x4419b508`), por lo que **no es
peculiar de `[ILLUMI]`**. Su uso concreto: NO VERIFICADO (el único puntero a la tabla
está en la tabla de punteros `0x440239f4`).

---

## 6. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ILLUMI]` (ocurrencias) | **34** | **0** | **0** |
| cadenas distintas con `[ILLUMI]` | 34 | 0 | 0 |
| apariciones de la subcadena `Illumi` | **45** | **4** | **4** |
| cadenas distintas que contienen `Illumi` | **43** | **4** | **4** |
| clases RTTI `Illumi*` | Dev, Ad, Cam, RPR0400 | Dev, Ad, Cam, RPR0400 | Dev, Ad, Cam, RPR0400 |
| `__PRETTY_FUNCTION__` de `Illumi*` | **20** | **0** | **0** |
| tipoinfo / vtable de las 4 clases | sí | sí | sí |
| id OSAL del bus del dispositivo `0x520250` | 8 usos | 8 usos | 10 usos |
| id OSAL del ADC LIRO `0x720018` | 13 usos | 13 usos | 14 usos |
| id OSAL de la cola de eventos `0x7a0020` | 10 usos | 12 usos | 13 usos |
| backup ids `0x133003c` / `0x133003d` | 1 / 1 | 1 / 1 | 1 / 1 |
| código `ReadDevice(0x39,0x46,…)` (GetAD) | `0x435adffe` | `0x435afee0` | `0x435b0cd0` |
| código `ReadDevice(0x39,0x41,…)` (PollingDevice) | `0x435ae060` | `0x435affd0` | `0x435b0dc0` |

**Lectura del diferencial (corrige la inferencia de S130/S165):**

1. **El subsistema de iluminación es COMÚN a las tres fw.** Las cuatro clases existen
   con la misma jerarquía, el mismo número de ranuras virtuales y el mismo código de
   acceso al chip (`ReadDevice` con dirección `0x39` y registros `0x46`/`0x41`), y los
   mismos identificadores OSAL (`0x520250`, `0x720018`, `0x7a0020`) y backup ids.
2. **Lo propio de la fw3.21 de la A6000 es la instrumentación**: las 34 trazas
   `[ILLUMI]` y las 20 cadenas `__PRETTY_FUNCTION__` (`IllumiDiag`, `IllumiGain`,
   `IllumiLevel`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400`). Ni la A7S ni la A6300
   tienen ni una sola.
   → Por tanto, `[ILLUMI]` **no es** un módulo exclusivo de la fw3.21 en el sentido de
   S130: es la **traza** de un módulo preexistente.
3. El identificador de módulo de traza del `[ILLUMI]` es **`0x133`** (307): es el primer
   argumento de todas las llamadas de log (`movw r0,#0x133`, p. ej. `0x435acdf2`) y
   el prefijo de sus identificadores OSAL/backup (`0x133003c`, `0x133003d`,
   `0x13303ba` cola sync de `IllumiDiag`, `0x13303be` cola sync de `IllumiCam`).
4. `IllumiDiag` es el **handler ADJ** (comandos de fábrica) del módulo: registra una
   cola de mensajes síncronos (`IllumiDiag::Init` @`0x435ac138`, id `0x13303ba`) y
   atiende el sub-comando leído en `[arg0+0x1a]` (`ldrb r5,[r0,#0x1a]` @`0x435abf94`):
   `1` → lectura de datos crudos y de nivel (sin traza de éxito, `0x435abfb8`);
   `2` → **fijar el modo de ganancia** (`SetGainMode`, `0x435ac0ac`); `3` → lectura de
   datos con traza *verbose* `GetRawData`/`GetIllumiData` (`0x435abfee`);
   cualquier otro → `'[ILLUMI]ADJ COMMAND ERROR'` (`0x435ac0c2`); y si el bloque ADJ no
   casa → `'[ILLUMI]ADJ BLOCK ERROR'` (`0x435abf90`, `cmp r2,r3` @`0x435abf7e`).

---

## 7. Verificación y método

* **Regla de referencias**: estricta (canónica del repo,
  `analysis/s106_imaging_cap/scan_pic_refs_strict.py`). El escaneo local propio
  (`scan_illumi_refs.py`, misma regla) coincide **exactamente** con el mapa global
  `analysis/s106_imaging_cap/pic_refs_strict_global.json`: **52 = 52 sitios**, ninguna
  diferencia. (No se publica aquí el mapa global.)
* **Verificación a mano de los pares PIC**: se desensamblaron los **52** pares
  (`analysis/s170_illumi/verify_pic.py`), comprobando en cada uno: (a) el
  `ldr rX,[pc,#imm]` más cercano del mismo registro, (b) el literal del pool,
  (c) `destino = literal + (add + 4)`, y (d) que el registro **no** se reescribe entre
  el `ldr` y el `add` (kill analysis heurística). **52/52 correctos, 0 reutilizaciones
  de registro.** Ejemplo (sitio `0x435ace10`): `ldr r3,[pc,#0x3c]` @`0x435ace0c` → pool
  `0x435ace4c` = `0x693984`; `add r3,pc` @`0x435ace10` → `0x693984 + 0x435ace14 =
  0x43c40798` = `'[ILLUMI]<Send Event> key_code = 0x%x,Level:%d'` ✓.
* **RTTI**: typeinfo, puntero a clase base y ranuras de vtable leídos byte a byte
  (`scan_illumi_rtti.py`, `scan_illumi_vtables.py`), incluida la comprobación de que
  `0x439b4145` es `__cxa_pure_virtual`.
* **Scripts del hito** (`analysis/s170_illumi/`): `scan_illumi_strings.py`,
  `scan_illumi_refs.py`, `scan_illumi_region.py`, `scan_illumi_names.py`,
  `scan_illumi_rtti.py`, `scan_illumi_vtables.py`, `scan_illumi_funcmap.py`,
  `scan_illumi_diff.py`, `scan_illumi_rtti_diff.py`, `verify_pic.py`, `dasm.py`,
  `find_calls.py`, `find_lit.py`, `build_illumi.py`.
* **Tests**: `tests/test_s170_illumi.py` (comprueban bytes reales: si cambia una
  dirección, el test falla).

---

## 8. Interés para la línea del obturador

**Negativo acotado: el módulo `[ILLUMI]` NO habla de obturación, de disparo, de lectura
del sensor de imagen ni de tiempos de exposición.**

Comprobación literal sobre las 34 trazas y sobre las 20 cadenas `__PRETTY_FUNCTION__`
del bloque `0x43c4052a`–`0x43c40e89`:

| término | coincidencias en las 34 trazas | en las 20 `__PRETTY_FUNCTION__` |
|---|---|---|
| `shutter` | 0 | 0 |
| `curtain` | 0 | 0 |
| `expos` | 0 | 0 |
| `iso` | 0 | 0 |
| `apert` | 0 | 0 |
| `frame` | 0 | 0 |
| `capture` | 0 | 0 |
| `photo` | 0 | 0 |
| `sensor` | 0 | 0 |
| `compens` | 0 | 0 |
| `read` | 2 (`ReadDevice`, `Backup_read` — **registros del chip de luz**, no del sensor de imagen) | 1 (`IllumiRPR0400::ReadDevice`) |
| `sync` | 5 (colas de mensajes OSAL síncronas) | 0 |

Matices que **sí** conviene registrar:

* El módulo **lee un sensor**, pero es el **sensor de luz ambiente** (chip `RPR0400`,
  registro `0x46`), no el sensor de imagen: no hay lectura de frames, ni de registros
  IMX210/IMX235, ni de tiempos de integración.
* El término **`gain`** del módulo es la **ganancia del amplificador del sensor de
  luz** (se selecciona con dos GPIO en `SetGainMode`, `0x435aca80`), **no** la ganancia
  ISO ni la compensación de exposición de la cámara.
* El único “nivel” que se publica (`Level`) es el **nivel de iluminancia** (índice
  0..N con umbrales e histéresis), publicado como evento de cámara
  `{key_code 0x17000001/0x17000002, 0, Level, 0}` en la cola `0x7a0020`.
* El **consumidor** de ese evento (quién lee `key_code 0x17000001`/`0x17000002` y qué
  hace con el nivel) **no está localizado**: no hay ninguna otra aparición de esos
  valores en la imagen, así que el despacho ocurre por tabla registrada en runtime.
  NO VERIFICADO.

⇒ **Para la línea del obturador: S51 A=NO / B=NO / C=NO se mantiene**; este módulo no
aporta ninguna ruta electrónica al obturador.

---

## 9. NO VERIFICADO / abierto

1. **Significado de las siglas**: `Illumi` **no se expande** en ninguna cadena de la
   imagen; `RPR0400` **tampoco** (no hay cadena que lo desarrolle). NO VERIFICADO.
   (La lectura “iluminación / sensor de luz ambiente” es **INFERENCIA** sostenida por
   el comportamiento medido: sensor con ADC propio, ganancia con GPIO, salida de
   “nivel de luz” a la cola de eventos de la cámara.)
2. **Nombres de fichero fuente**: **no existe ninguna cadena con nombre de fichero**
   (`*.cpp`, `*.h`) en la zona de código del módulo (`0x435ab000`–`0x435af000`) ni
   ninguna con `Illumi` en todo el binario. NO VERIFICADO / no recuperable con estas
   técnicas.
3. **Consumidor del evento de nivel**: el `key_code` `0x17000001` / `0x17000002` no
   aparece en ningún otro punto de la imagen → el despacho final (tabla runtime) no
   está localizado. NO VERIFICADO. Tampoco se ha identificado **qué hace la cámara**
   con el nivel de luz (auto-exposición, brillo de pantalla, balance de blancos):
   NO VERIFICADO.
4. **Naturaleza exacta de `key_code`**: en `[ILLUMI]` es un `u32` `0x17000001/2`; en
   `[JOG]` (S165) son `u32` pequeños `0x11`–`0x17` leídos de una tabla (`0x43fdab20`).
   La diferencia de espacio de nombres (0x17xxxxxx vs 0x00–0xff) **NO VERIFICADA**;
   sí es **VERIFICADO** que ambos módulos emiten un mensaje de evento con `key_code`
   como primer `u32` a una cola de cámara (0x7a0020 para ILLUMI, 0x011b02aa + registro
   de descriptor id 0x106 para JOG).
5. **Identidad de los 4 GPIO de ganancia** (`0xf901a5`–`0xf901a8`): se resuelven por un
   servicio de nombres (`GOT[0x16dc]->vtable[0x2e0]`), pero **no se ha recuperado su
   nombre textual**. NO VERIFICADO.
6. **Unidad del periodo del temporizador**: la constante `0x4e20` (20000) que se pasa a
   `osal_set_timer` (`0x435ad160`) es el periodo de muestreo; **su unidad (ms, ticks)
   no está confirmada**. NO VERIFICADO.
7. **Origen de los datos de configuración** (umbrales por nivel, tabla de bytes de
   nivel, puntos de calibración de `C_AD`): se leen de tablas indexadas por la GOT
   (`0x435ac3b4`, `0x435ad600`); **de qué parámetro de configuración se trata no está
   identificado**. NO VERIFICADO.
8. **Sentido de `ADwork` vs `ADcor`**: por el código, `'[ILLUMI]AD MAXOVER. ADwork=0x%x'`
   imprime (`0x435ad528`) el valor **interpolado** que acaba de calcular `C_AD` (`r0`),
   cuando supera `0xfffe`; y `'[ILLUMI]C_AD. ADcor=0x%x'` imprime (`0x435ad54c`) el
   centinela `0xffff` que la función devuelve en esa saturación. La nomenclatura exacta
   de ambos nombres es NO VERIFICADA. Lo mismo para `gain` / `gain_pre` (§2.6), que
   viven en dos globals distintos.
9. **Tabla de 19 ids OSAL `0x10600xx`** (`0x43fdaaa4`): presente en las tres fw, junto
   a los typeinfo de `Illumi*`; **su uso NO VERIFICADO**.
10. **Qué canal del ADC LIRO usa el `[ILLUMI]`**: el byte de canal se lee de un global
    (GOT+`0xba8`), no de un literal → su valor NO VERIFICADO.

---

## 10. Revisión del agente principal

*(vacía — pendiente de revisión)*

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (30 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 34 cadenas `[ILLUMI]` en la A6000 fw3.21 entre `0x43c40570` y `0x43c40ddc`
   (bloque contiguo); **0** en la A7S fw3.20 y el A6300 fw2.01 → comprobado con `bytes.count()`.
2. **Estructura**: **52 sitios** (regla estricta) en **25 funciones** emisoras, **0 cadenas muertas**,
   con los **52 pares PIC verificados a mano (52/52)** y sin reuso de registro.
3. **El subsistema es COMÚN a las tres fw (corrige la inferencia de S130/S165)**: las cuatro clases
   RTTI `IllumiDev`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400` existen en los tres con la misma
   jerarquía, y el acceso al chip es el mismo (`ReadDevice` con dirección `0x39` y registros `0x46`
   (GetAD) / `0x41` (PollingDevice): `0x435adffe` y `0x435ae060` en la A6000, `0x435afee0`/`0x435affd0`
   en la A7S, `0x435b0cd0`/`0x435b0dc0` en el A6300) con los mismos ids OSAL (`0x520250` bus del
   dispositivo, `0x720018` ADC LIRO, `0x7a0020` cola de eventos) y los mismos *backup ids*
   (`0x133003c`/`0x133003d`). Lo **propio de la fw3.21 de la A6000 es la instrumentación**: las 34
   trazas `[ILLUMI]` y las **20** cadenas `__PRETTY_FUNCTION__` (`IllumiDiag`, `IllumiGain`,
   `IllumiLevel`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400`), **0** en la A7S y el A6300.
4. **Coherencia**: el **id de módulo de traza es `0x133`** (307) — primer argumento de todas las
   llamadas de log (`movw r0,#0x133`, p. ej. `0x435acdf2`) — y es el prefijo de sus ids
   OSAL/backup (`0x133003c`, `0x133003d`, `0x13303ba` cola sync de `IllumiDiag`, `0x13303be` de
   `IllumiCam`). Es el mismo patrón que el id `0xb5` de la familia `CAM_UTIL` (S173) y el `0x93` de
   `[TP_R]` (S156).
5. **Negativo acotado**: 0 de `shutter`/`curtain`/`expos`/`iso`/`apert`/`frame`/`capture`/`photo`/
   `sensor`/`compens` en las 34 trazas; los 2 `read` son `ReadDevice`/`Backup_read` (**registros del
   chip de luz**, no del sensor de imagen) y los 5 `sync` son colas OSAL síncronas. El «gain» es la
   **ganancia del amplificador del sensor de luz** (seleccionada con dos GPIO en `SetGainMode`
   `0x435aca80`), no la ganancia de imagen → **sin efecto en S51** (A/B/C = NO).
6. **Riesgo de lectura evitado**: el módulo **lee un sensor**, pero es el **sensor de luz ambiente**
   (chip `RPR0400`), no el sensor de imagen: no hay lectura de frames, ni de registros
   IMX210/IMX235, ni de tiempos de integración.
