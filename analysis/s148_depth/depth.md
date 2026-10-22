# S148 — el módulo `[DEPTH]` (16 trazas) del firmware A6000 fw3.21

> Hito de la línea de RE general por módulos de trazas. Todo lo que sigue está
> verificado desensamblando bytes de `analysis/rea-independent/input/av-cam.bin`
> (convención **vaddr = 0x43541000 + file_offset**, válida también para la A7S
> fw3.20 y la A6300 fw2.01).
> Regla de referencias a cadenas: **estricta** (canónica del repo,
> `analysis/s106_imaging_cap/scan_pic_refs_strict.py`), verificada **a mano**
> en los 17 sitios (ver §4).
> Datos estructurados: [`depth.json`](depth.json) · Nota breve: [`docs/capture/s148-depth.md`](../../docs/capture/s148-depth.md).

---

## 1. Resumen ejecutivo

`[DEPTH]` **no es un módulo nuevo**: es la **instrumentación** de un módulo de
servicio ya presente en los tres firmwares, la clase **`DepthGaugeMain`**, que
publica un valor numérico («depth») con un «status» y lo difunde por
notificaciones.

| dato | valor | verificación |
|---|---|---|
| trazas `[DEPTH]` | **16** (16 textos distintos) | búsqueda literal del token en el blob |
| rango | `0x43C249EC` – `0x43C24C73` | idem |
| niveles | 11 `INFO`, 2 `DEBUG`, 3 `WARN` | idem |
| sitios de emisión (PIC, regla estricta) | **17** | recomputados y verificados a mano |
| funciones emisoras | **11** | prólogo más cercano hacia atrás |
| cadenas sin referencia | **0** (las 16 referenciadas) | mapa global `pic_refs_strict_global.json` |
| clase | `DepthGaugeMain` (RTTI `0x43C24B85`) | `std::type_info` en `0x43FD7C84` |
| nombre de registro del módulo | `depth` (`0x43C24B46`) | `add r0,pc` en `0x4356249A` |
| comandos del módulo | **6** | tabla de 12 B en `0x43FD7C30` |
| GID del subsistema | `0x018B04DC` | 6 apariciones del literal en el blob |
| **diferencial A7S fw3.20** | **0/16** trazas y **0/16** núcleos de texto | búsqueda literal |
| **diferencial A6300 fw2.01** | **0/16** trazas y **0/16** núcleos de texto | búsqueda literal |

**Conclusión para la línea del obturador electrónico:** el módulo **no habla** de
obturador, sensor, exposición, enfoque, lectura del sensor ni distancia
(0 menciones de `shut`/`shutter`/`silent`/`sensor`/`exposure`/`readout`/`focus`/`af`
en las 16 trazas) → **S51 (A/B/C = NO) se mantiene intacto**. Véase §7.

---

## 2. Qué es `[DEPTH]`

### 2.1 Lo que sí está verificado en los bytes

1. **Es una etiqueta de logging de nivel 2 sobre un servicio con nombre.**
   La clase es `DepthGaugeMain` (nombre RTTI con longitud incluida,
   `14DepthGaugeMain`, `0x43C24B85`); su `std::type_info` es la entrada
   `{vptr 0x43FD04F8, nombre}` en `0x43FD7C84`, y su vtable está en `0x43FB8F50`
   (`offset-to-top = 0`, `type_info`, dos funciones virtuales: `0x435624B1` —el
   constructor— y `0x43A3ACD1`).

2. **El módulo se da de alta con el nombre `depth`** en un registro de módulos
   de 36 entradas (`0x435AB6F0`), pasando su **tabla de comandos**:

   ```
   0x4356248C  push {r4, lr}
   0x4356248E  bl   0x43562590          ; init
   0x43562492  bl   0x435625DC          ; alta como receptor del GID 0x018B04DC
   0x43562496  ldr  r0, [pc, #0x10]     ; pool 0x435624A8 = 0x006C26A8
   0x43562498  ldr  r1, [pc, #0x10]     ; pool 0x435624AC = 0x00A75790
   0x4356249A  add  r0, pc             ; -> 0x43C24B46  'depth'
   0x4356249C  add  r1, pc             ; -> 0x43FD7C30  (tabla de comandos)
   0x435624A2  b.w  0x435AB6F0          ; registro por nombre
   ```

3. **La tabla de comandos** (`0x43FD7C30`, 12 B por entrada:
   `{char* nombre, char* nombre, handler}`; terminador `{0,0,0}` en `0x43FD7C78`):

   | # | comando | handler (vaddr) | qué hace (verificado) |
   |---|---|---|---|
   | 1 | `update` | `0x43562454` | `cmp r0,#3` (3 tokens) → parsea **dos hexadecimales** con `strtoul` base 16 (`0x43A3AC8C`) y llama a `update` (`0x43541B00`) |
   | 2 | `getLiro` | `0x43562424` | lee el par `{status, valueDepth}` y lo traza |
   | 3 | `getMsg` | `0x4356230C` | reserva un mensaje OSAL, copia el par y lo traza |
   | 4 | `notifyOn` | `0x435623BC` | `cmp r0,#2` → parsea `respGID` en hex y **envía un mensaje con id 2** al GID registrado |
   | 5 | `notifyOff` | `0x43562354` | `cmp r0,#2` → ídem con **id 3** |
   | 6 | `enableDummyRecv` | `0x4356228C` | da de alta un **receptor «dummy»** (respuesta con `0x435622D4`) y traza el GID |

4. **El transporte** es el de los servicios del firmware: un **GID**
   (`0x018B04DC`, literal repetido 6 veces en la zona del módulo) y la
   tabla global de despacho de servicios `0x4401EEE4`. Los "thunks" de OSAL
   (`0x43561298`, `0x435612B4`, `0x4356127C`, `0x43561324`) son llamadas
   indirectas `blx` a través de un vtable de `0x4401EEE4 + 0x16DC`.

5. **Los ids de notificación** se leen en el despachador `0x435626D4`:
   `cmp r7,#2` → NOTIFY_ON, `cmp r7,#3` → NOTIFY_OFF, `cmp r7,#1` → GET,
   resto → `ERR Invalid Command`.

6. **El valor es acotado**: `cmp.w r3,#0xFA0` / `movhi.w r3,#0xFA0` en
   `0x43541B04` recorta `valueDepth` a **4000** antes de propagarlo.

7. **El consumidor real del valor** está fuera del módulo:
   `CS_ExifMakerNote.cpp` (`0x43CC56DC`) llama a `getMsg` en `0x438B900A` y
   escribe el resultado en el MakerNote:
   * tag Exif **0x5001** = racional `(valueDepth*10 : 1000)` → es decir
     `valueDepth/100` (`muls r7,r2,r7` con `r2=0x0A` en `0x438B90A2`,
     `movw r2,#0x3E8` en `0x438B90A4`, `str r7,[r3]` / `str r2,[r3,#4]` en
     `0x438B90A8`/`0x438B90AA`);
   * tag Exif **0x5002** = entero con el estado: `0` (valor válido), `1`,
     `0x80` (estado 2), `0x81` (estado `0xF0000000`) — `movs r6,#0x80` en
     `0x438B9088`, `movs r6,#0x81` en `0x438B9084`, escritura en `0x438B90B8`.
   Un segundo consumidor es el módulo `[ACCY]`, que llama a `update` en
   `0x43564DC0` con `{status=2, valueDepth=0}` y en `0x43564ED2` con el estado
   recibido.

### 2.2 Lo que **NO** está verificado

* **La sigla no se desarrolla.** `DEPTH` no aparece expandida en ningún byte
  del blob (ni como `Depth`, ni como `Distance`, ni como `FocusDepth`); el
  nombre de la clase es `DepthGaugeMain` y el del registro es `depth`. **No se
  inventa la expansión.**
* **No se sabe qué magnitud física mide `valueDepth`** (0..4000, con 2
  decimales al escribirlo en el Exif) ni qué significa exactamente `status`.
  No hay ninguna traza, símbolo ni nombre de fichero en el módulo que lo
  identifique.
* **No hay fichero fuente embebido.** Ni las 16 trazas ni la zona de código
  `0x4356228C`–`0x435627B0` contienen un nombre de fichero (a diferencia de
  otros módulos, p. ej. `[SFRA]` o `[SMP SELECTOR]`, que sí citan
  `file=%s`/`ExecQValue`/`ModuleOnePassBase.cpp`). El único fichero fuente
  **identificable** del entorno es `CS_ExifMakerNote.cpp` (`0x43CC56DC`),
  que es el *consumidor*, no el implementador del módulo.

---

## 3. Las 16 trazas

Todos los textos están en el bloque contiguo `0x43C249EC`–`0x43C24C73`.

| # | vaddr | texto | nivel | sitio PIC | función emisora |
|---|---|---|---|---|---|
| 1 | `0x43C249EC` | `[DEPTH][INFO]Regist Dummy Receiver 0x %08X` | INFO | `0x435622BA` | `0x4356228C` (`enableDummyRecv`) |
| 2 | `0x43C24A17` | `[DEPTH][INFO]Rsp: cid = %08X, status = %d, valueDepth = %d` | INFO | `0x435622EC` | `0x435622D4` (respuesta) |
| 3 | `0x43C24A52` | `[DEPTH][INFO]status = %d, valueDepth = %d` | INFO | `0x43562338` | `0x4356230C` (`getMsg`) |
| 4 | `0x43C24A7C` | `[DEPTH][INFO]usage: notifyOff respGID(as HEX)` | INFO | `0x43562366` | `0x43562354` (`notifyOff`) |
| 5 | `0x43C24AAA` | `[DEPTH][INFO]ret = %08X` | INFO | `0x4356239C` | `0x43562354` (`notifyOff`) |
| 6 | `0x43C24AC2` | `[DEPTH][INFO]usage: notifyOn respGID(as HEX)` | INFO | `0x435623CE` | `0x435623BC` (`notifyOn`) |
| 7 | `0x43C24AEF` | `[DEPTH][INFO]ret = 0x%08X` | INFO | `0x43562402` | `0x435623BC` (`notifyOn`) |
| 8 | `0x43C24B09` | `[DEPTH][INFO]usage: Update status(as HEX) valueDepth(as HEX)` | INFO | `0x43562464` | `0x43562454` (`update`) |
| 9 | `0x43C24B96` | `[DEPTH][INFO]GET %d %d` | INFO | `0x43562652` | `0x43562634` (notificación GET) |
| 10 | `0x43C24BAD` | `[DEPTH][INFO]NOTIFY to %08X %d %d` | INFO | `0x435626B8` | `0x43562660` (envío de notificación) |
| 11 | `0x43C24BCF` | `[DEPTH][INFO]UPDATE %d %d` | INFO | `0x43541B28` | `0x43541B00` (impl. de `update`) |
| 12 | `0x43C24BE9` | `[DEPTH][DEBUG]NOTTIFY_ON %08X` | DEBUG | `0x4356270C` | `0x435626D4` (despachador, cmd 2) |
| 13 | `0x43C24C07` | `[DEPTH][WARN]ERR NOTTIFY_ON %08X %08X` | WARN | `0x4356273E` | `0x435626D4` (cmd 2, error) |
| 14 | `0x43C24C2D` | `[DEPTH][DEBUG]NOTTIFY_OFF %08X` | DEBUG | `0x43562764` | `0x435626D4` (despachador, cmd 3) |
| 15 | `0x43C24C4C` | `[DEPTH][WARN]ERR NOTTIFY_OFF %08X %08X` | WARN | `0x43562786` | `0x435626D4` (cmd 3, error) |
| 16 | `0x43C24C73` | `[DEPTH][WARN]ERR Invalid Command %08X %08X` | WARN | `0x435627A6` | `0x435626D4` (cmd inválido) |

**Cadenas del bloque que NO llevan la etiqueta `[DEPTH]`** (identifican el
módulo pero no son trazas del módulo): `depth` `0x43C24B46`,
`update` `0x43C24B4C`, `getLiro` `0x43C24B53`, `getMsg` `0x43C24B5B`,
`notifyOn` `0x43C24B62`, `notifyOff` `0x43C24B6B`,
`enableDummyRecv` `0x43C24B75`, `14DepthGaugeMain` `0x43C24B85`.

---

## 4. Verificación a mano de los 17 sitios PIC

Todos ellos cumplen la regla estricta: `ldr rX,[pc,#imm]` (el más cercano por
detrás, misma ventana de 4 KB) → literal pool → `add rX,pc` →
`destino = W + (add + 4)`. Ninguno tiene un puntero absoluto de 4 B a la
cadena. Ejemplo (los 17 están en `analysis/s148_depth/verify_pic.py`):

```
add en 0x435622BA  reg=r3
   ldr emparejado 0x435622B8  bytes=054b
   literal pool  0x435622D0 = 0x006C272E
   destino = 0x006C272E + 0x435622BE = 0x43C249EC
   cadena: '[DEPTH][INFO]Regist Dummy Receiver 0x %08X'
```

El script `analysis/s148_depth/build_depth.py` **recomprueba** los 17 pares
(`assert dest == addr`): si una dirección cambiara, el script aborta.

---

## 5. Mapa función → traza y resto de funciones del módulo

| función | rol | trazas que emite |
|---|---|---|
| `0x43541B00` | implementación de `update` (recorta a 0xFA0) | #11 |
| `0x4356228C` | handler `enableDummyRecv` | #1 |
| `0x435622D4` | callback de respuesta (`Rsp`) | #2 |
| `0x4356230C` | handler `getMsg` | #3 |
| `0x43562354` | handler `notifyOff` | #4, #5 |
| `0x435623BC` | handler `notifyOn` | #6, #7 |
| `0x43562424` | handler `getLiro` | #3 (mismo texto, 2.º sitio) |
| `0x43562454` | handler `update` | #8 |
| `0x43562634` | manejador de la notificación GET | #9 |
| `0x43562660` | envío de la notificación | #10 |
| `0x435626D4` | despachador de notificaciones (1/2/3) | #12, #13, #14, #15, #16 |

Funciones del módulo **sin traza propia** (participan en el flujo):

| función | rol |
|---|---|
| `0x4356248C` | alta del módulo: init + registro con el nombre `depth` y su tabla |
| `0x435624B0` | constructor de `DepthGaugeMain` (fija el vptr `0x43FB8F50`) |
| `0x43562578` | fija el vptr de una instancia |
| `0x43562590` | init: registra el callback de notificación `0x43A3ACE2` con `0x439B4244` |
| `0x435625DC` | init: da de alta el módulo como receptor del GID `0x018B04DC` |
| `0x43562618` | `getLiro` interno: pide el valor al GID `0x018B04DC` y lo lee |
| `0x43A3AC8C` | API: conversión de cadena hexadecimal (`strtoul` base 16) |
| `0x43A3AC98` | API: `getMsg` → `0x43562634` |
| `0x43A3ACAA` | API: `update` → `0x43541B00` |
| `0x43A3ACBC` | API: `getLiro` → `0x43562618` |
| `0x43A3ABFE` | arranque que da de alta el módulo `depth` (y el resto de inicializadores del fichero) |

**Nota sobre los puntos de entrada.** La detección por prólogo da `0x43541B02`,
`0x43562356`, `0x435623BE` y `0x43562456`, pero los puntos de entrada reales
son **`0x43541B00`**, `0x43562354`, `0x435623BC` y `0x43562454`:
en los tres últimos la instrucción `cmp r0,#N` precede al `push`, y en el
primero hay un `ldr r3,[r1,#4]` antes del `push`. Lo confirman la tabla de
comandos (los punteros a handler son `0x43562355`, `0x435623BD`, `0x43562455`,
todos con el bit de Thumb) y el `b.w 0x43541B00` de `0x43A3ACB8`.

**Estado interno.** El objeto es un **singleton** en `0x43E131E8`; sus campos
`{status, valueDepth}` están en `+4` y `+8` (copia de 8 B con `ldm`/`stm` en
`0x4356263C`/`0x4356263E`). Los flags de "iniciado una vez" están en
`0x43E37990` (GID del receptor), `0x43E3798C`, `0x43E37994` y `0x43E37998`.
**Ninguno de esos globales es referenciado desde fuera del módulo** (búsqueda
PIC sobre toda la imagen: 0 sitios fuera de `0x4356228C`–`0x435626D4`).

---

## 6. Fichero(s) fuente

* **NO VERIFICADO / no disponible**: el módulo **no incrusta ningún nombre de
  fichero fuente**. Se han revisado las 16 trazas, las 8 cadenas auxiliares
  (`depth`, `update`, `getLiro`, `getMsg`, `notifyOn`, `notifyOff`,
  `enableDummyRecv`, `14DepthGaugeMain`) y todo el rango de código
  `0x4356228C`–`0x435627B0`: no aparece ningún `*.cpp`/`*.h`, ni `file=%s`, ni
  `line=%d`.
* El **único fichero fuente identificable** en el entorno inmediato es
  **`CS_ExifMakerNote.cpp`** (`0x43CC56DC`), que es el *consumidor* del valor
  (líneas `0x33A` = 826 y `0x360` = 864 en los `FATAL! %s:%d`).
* El módulo vive en el mismo fichero/binario que el módulo `[ACCY]`
  (S136): la función de arranque `0x43A3ABFE` registra primero `depth` y luego
  llama a los inicializadores de `[ACCY]` (`0x4356288C`, `0x435628D8`,
  `0x43562D18`, `0x43563220`, `0x43562B48`), y las cadenas de `[ACCY]`
  (`0x43C24C9E`–`0x43C24E82`) son contiguas a las de `[DEPTH]` en `.rodata`.

---

## 7. Relación con los módulos ya documentados

| módulo | relación con `[DEPTH]` | evidencia |
|---|---|---|
| `[CAMERA_MAIN]` (S126) | **ninguna directa**. Existe `fc_depth` (`0x43C9C665`) y `cal_iterbound.cpp … in_infoLC->fcdepth = 0` (`0x43CCC013`, en `[CAMERA_MAIN_YC]`), pero ninguna función de `[DEPTH]` las referencia | 0 referencias cruzadas |
| `[CAMERA_MAIN_FC]` (S138) | ninguna | 0 |
| `[CAMERA_MAIN_LC]` (S127) | ninguna | 0 |
| `[CAMERA_MAIN_YC]` (S110) | ninguna | 0 |
| `[VDF]`/`[VEF]` (S86) | `VDF::VdfDisplayCmdSetPanelOut::VphSetPanelDepthCall` (`0x43C870E0`) y `[VPH_API]<panel_depth>` (`0x43CE3504`, S131) usan la palabra "depth" en otro sentido (panel); **no hay enlace de código** con `[DEPTH]` | 0 llamadas cruzadas |
| `[CAM_UTIL_SENS]` (S144) | ninguna | 0 |
| `[IDT_OPD]` (S120) | `MovieDepthRate illegal` (`0x43CF57F1`) es otro "depth" (tasa de profundidad de movie), sin enlace | 0 |
| `[ACCY]` (S136) | **sí**: comparten fichero/binario; `[ACCY]` llama a la API `update` del módulo en `0x43564DC0` y `0x43564ED2`; y `0x43A3ABFE` inicializa ambos | ver §5 |
| `[IMAGING]` / `CS_ExifMakerNote.cpp` (S125/S126) | **sí**: el Exif MakerNote consume el valor (`getMsg` en `0x438B900A`) y escribe los tags privados 0x5001/0x5002 | ver §2.1 |
| `[SMP SELECTOR]` | la cadena de `[DEPTH]` está inmediatamente detrás de las de `[SMP SELECTOR]` en `.rodata` (`0x43C248CA`–`0x43C249C9`); es contigüidad de `.rodata`, no dependencia | — |

**Nombres vecinos de `[ACCY]` (dato del módulo `[ACCY]`, no de `[DEPTH]`, pero
sitúa a los dos módulos en el mismo fichero)**: `EnableDummyRecv`,
`DisableDummyRecv`, `MsSleep`, `RxResponse`, `RxCommand`, `16AccyMiDeviceBase`
y `17AccyMiDeviceLight` existen en la A7S fw3.20 y en la A6300 fw2.01 y **no**
en la A6000 fw3.21 (el bloque `[ACCY]` de la A6000 usa otra nomenclatura;
`SendCommand`, `SetQue` y `GetQue` sí aparecen en los tres).

### Línea del obturador electrónico

* **0/16** trazas mencionan `shut`, `shutter`, `silent`, `electro`, `mech`,
  `sensor`, `exposure`, `readout`, `focus`, `af`, `dist`, `iso`, `aperture`,
  `iris`, `zpd`, `imager`, `drv`, `drive` (contadas sobre las 16 cadenas
  completas, en minúsculas).
* **Ningún `bl`/`blx` desde el módulo sale de él**: los 26 **destinos de
  llamada distintos** de sus funciones (63 instrucciones de llamada) son, todos,
  los *thunks* de OSAL/servicio `0x4356120C`–`0x43561324`, los dos ayudantes
  de log del propio módulo (`0x435621E0`, `0x435624C8`), sus propias funciones
  (`0x43562578`–`0x43562660`), el registro de clases `0x439B4244`, `strtoul`
  `0x439C0958`, `memset` `0x439C5004`/`0x439C5A04`, sus API
  `0x43A3AC8C`–`0x43A3ACCA` y los emisores de mensaje `0x43A3AF86`/`0x43A3AF9A`.
  **Cero llamadas** a `[CAM_IMAGER]`, `[CAMERA_MAIN_YC]`,
  `[CAMERA_MAIN_SYNC]`, `[IDT_OPD]`, `[CAMERA_MAIN]`, `[VPH_API]`/`[VDF]` o a
  cualquier módulo de captura.
* **⇒ Sin efecto en S51: A = NO, B = NO, C = NO.**

---

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 8.1 Lo que NO cambia (el módulo es preexistente)

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| clase `14DepthGaugeMain` | 1 | 1 | 1 |
| nombre de registro `depth` | sí | sí | sí |
| tabla de comandos | `0x43FD7C30` | `0x43FD9914` | `0x4419920C` |
| comandos (mismo nombre y orden) | `update, getLiro, getMsg, notifyOn, notifyOff, enableDummyRecv` | idéntico | idéntico |
| formato de entrada (12 B) | `{nombre, nombre, handler}` | idéntico | idéntico |
| terminador `{0,0,0}` tras 6 entradas | `0x43FD7C78` | `0x43FD995C` | `0x44199254` |
| literal del GID `0x018B04DC` | 6 apariciones | 6 apariciones | 6 apariciones |

Handlers de la tabla de comandos:

| comando | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `update` | `0x43562454` | `0x43A20010` | `0x43AC9378` |
| `getLiro` | `0x43562424` | `0x43A1FFEA` | `0x43AC9352` |
| `getMsg` | `0x4356230C` | `0x435600B8` | `0x4355A7CC` |
| `notifyOn` | `0x435623BC` | `0x43560120` | `0x4355A834` |
| `notifyOff` | `0x43562354` | `0x435600E4` | `0x4355A7F8` |
| `enableDummyRecv` | `0x4356228C` | `0x43560074` | `0x4355A788` |

### 8.2 Lo que SÍ es nuevo en la fw3.21 de la A6000: el *logging*

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| apariciones del token `[DEPTH]` | **16** | **0** | **0** |
| textos interiores coincidentes | 16/16 | **0/16** | **0/16** |
| presencia de la cadena `valueDepth` | 3 | **0** | **0** |
| presencia de `Regist Dummy Receiver` | 1 | **0** | **0** |
| presencia de `usage: notifyOn/notifyOff/Update` | 3 | **0** | **0** |
| presencia de `NOTTIFY_ON` / `NOTTIFY_OFF` | 2 / 2 | **0 / 0** | **0 / 0** |
| presencia de `ERR Invalid Command` | 1 | **0** | **0** |

⇒ **El módulo `DepthGaugeMain` existe en los tres firmwares con la misma
estructura, los mismos 6 comandos y el mismo GID; lo que la fw3.21 de la A6000
añade es exclusivamente la instrumentación (`[DEPTH][INFO|DEBUG|WARN]`)**, sin
cambios funcionales observables en el código del módulo. Es el mismo patrón que
S130 lo detectó como «nuevo» y S132/S136 lo detallaron: *se reescribe el
logging, no el firmware*.

**Salvedad (heredada de S130 §4):** la comparación mezcla **versión y modelo**
(no hay una fw anterior de la A6000 en el repositorio), así que no se puede
separar «nuevo en la fw3.21» de «propio de este modelo». Lo que sí es
verificable es: **las 16 trazas y su contenido textual no existen en la A7S
fw3.20 ni en la A6300 fw2.01**.

---

## 9. NO VERIFICADO / abierto

1. **Qué magnitud física es `valueDepth`** (0..4000, con 2 decimales en el
   Exif) y qué significan los valores de `status` (`0`, `1`, `2`,
   `0xF0000000`) y sus equivalentes MakerNote (`0`, `1`, `0x80`, `0x81`).
2. **El fichero fuente que implementa el módulo**: no hay nombre de fichero
   embebido. Candidatos no verificados: el fichero que también contiene
   `[ACCY]` (mismo arranque `0x43A3ABFE`) y `CS_ExifMakerNote.cpp`
   (consumidor, no implementador).
3. **El significado de la sigla `DEPTH`**: no aparece expandida en ningún byte.
   El único nombre propio verificado es la clase `DepthGaugeMain` y el nombre
   de registro `depth`.
4. **El receptor final del GID `0x018B04DC`** fuera de `av-cam.bin`
   (`0x4401EEE4` es la tabla de servicios global; los "thunks" son
   `blx` indirectos, por lo que el destino real no se ve en estos bytes).
5. **Por qué `[ACCY]` publica `update` con `status=2`** al desenchufar la
   carcasa (agua) (`0x43564DC0`): no hay ninguna traza que lo explique.
6. **Quién llama a `notifyOn`/`notifyOff`**: no hay ninguna referencia a esos
   nombres fuera de la propia tabla de comandos (se invocan por línea de
   comandos).
7. **Si el valor llega a la pantalla**: no hay ninguna llamada desde `[DEPTH]`
   a `[VPH_API]`/`[VDF]`; la ruta hacia el visor está cerrada.

---

## 10. Reproducir

```bash
# cadenas + referencias PIC + diferencial  ->  depth.json
.venv/bin/python analysis/s148_depth/build_depth.py

# verificación a mano de un par PIC concreto
.venv/bin/python analysis/s148_depth/verify_pic.py 0x435622ba 0x435627a6 0x43541b28

# desensamblado con anotación de pools y destinos
.venv/bin/python analysis/s148_depth/dasm.py 0x4356228c 0x43562400

# todos los pares PIC resueltos de un rango
.venv/bin/python analysis/s148_depth/resolve_range.py 0x43562000 0x43562c00

# llamadores (bl/blx/b/b.w) de una función
.venv/bin/python analysis/s148_depth/callers.py 0x4356248c 0x435622d4
```

---

## 11. Revisión del agente principal

_(vacío — pendiente de revisión)_

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (25 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 16 apariciones de `[DEPTH]` en la A6000 fw3.21 entre `0x43c249ec` y
   `0x43c24c73` (11 `INFO`, 2 `DEBUG`, 3 `WARN`); **0** en la A7S fw3.20 y el A6300 fw2.01 →
   confirmado con `bytes.count()`.
2. **17 sitios** (regla estricta, **verificados a mano** los 17: `ldr`→pool→`add`→destino) en
   **11 funciones** (`0x43541b00` `update`, `0x4356228c` `enableDummyRecv`, `0x435622d4` Rsp,
   `0x4356230c` `getMsg`, `0x43562354` `notifyOff`, `0x435623bc` `notifyOn`, `0x43562424`
   `getLiro`, `0x43562454` `update`, `0x43562634` GET, `0x43562660` NOTIFY, `0x435626d4`
   despachador); 0 cadenas sin referencia y ningún puntero absoluto de 4 B.
3. **No es un módulo nuevo**: la clase `DepthGaugeMain` (RTTI `14DepthGaugeMain` `0x43c24b85`,
   `type_info` `0x43fd7c84`, vtable `0x43fb8f50`) está **en los tres firmware** (1/1/1), registrada
   con el nombre **`depth`** (`0x43c24b46`) en `0x435ab6f0`, con **tabla de 6 comandos** de 12 B en
   `0x43fd7c30` (`update`, `getLiro`, `getMsg`, `notifyOn`, `notifyOff`, `enableDummyRecv`), GID
   `0x018b04dc` e ids 1=GET / 2=NOTIFY_ON / 3=NOTIFY_OFF (`0x435626d4`); `valueDepth` acotado a
   **0xFA0 = 4000** (`0x43541b04`) → lo nuevo en la fw3.21 es **solo el logging** (patrón S130 /
   S132 / S136).
4. **Consumidor real identificado** (aportación útil): `CS_ExifMakerNote.cpp` (`0x43cc56dc`) →
   `getMsg` en `0x438b900a` → tag Exif **0x5001** = racional `(valueDepth*10 : 1000)` (`0x438b90a8`)
   y **0x5002** = estado (`0`/`1`/`0x80`/`0x81`, `0x438b90b8`); segundo consumidor: `[ACCY]` →
   `update` en `0x43564dc0`/`0x43564ed2`. Es decir, la "profundidad" sale a la **EXIF** de la foto.
5. **Negativo acotado**: 0/16 menciones de obturador/sensor/exposición/enfoque/lectura/distancia
   (`shut`, `shutter`, `silent`, `electro`, `mech`, `sensor`, `exposure`, `readout`, `focus`, `af`,
   `dist`, `iso`, `aperture`, `iris`, `zpd`, `imager`, `drv`, `drive` = 0 cada uno) y los **26
   destinos de llamada** del módulo no salen de él (cero llamadas a `[CAM_IMAGER]`,
   `[CAMERA_MAIN*]`, `[IDT_OPD]`, `[VPH_API]`/`[VDF]`) → **S51 A/B/C = NO intacto**.
