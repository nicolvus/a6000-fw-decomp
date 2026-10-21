# S113 — `[CAM_DMM]`: el gestor de memoria dinámico de la cámara

> Hito de la **línea de ingeniería inversa general** (no afecta a la decisión del obturador
> electrónico: S51 sigue con A/B/C = NO). Datos verificables contra los bytes del
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Scripts reproducibles en este directorio.

## 1. Qué es

`[CAM_DMM]` es el **gestor de memoria dinámico** (DMM) del firmware de la cámara: la capa que
reserva, comparte, abre y libera **unidades de memoria** (recursos con *handles* y *extents*)
que luego consumen el motor de imagen, el acelerador escalar, el codificador y el gestor de
captura.

- **54 trazas** con el prefijo `[CAM_DMM]:`, de `0x43cce6ae` a `0x43ccf1c3`.
- Todas son **mensajes de error**: el módulo no traza el camino feliz, solo los fallos.
- La implementación está en un **bloque de código contiguo**: 25 funciones entre
  `0x439011d8` y `0x43903d5c` (≈11 KB) → es una biblioteca autocontenida, no código disperso.

## 2. La API del DMM en el firmware: 11 operaciones

| operación | n trazas | qué hace (según sus mensajes) |
|---|---|---|
| `AllocNew` | 4 | reserva una unidad nueva |
| `AllocNewRdv` | 4 | reserva una unidad **en rendezvous** (`MemoryHandle::AllocRendezvous`) |
| `AllocShare` | 4 | reserva **compartiendo** una unidad ya existente |
| `Free` | 2 | libera la unidad |
| `FreeRdv` | 2 | libera la unidad en rendezvous |
| `Open` | 3 | abre un handle ya reservado |
| `Close` | 2 | cierra el handle |
| `MemoryHandle::` (`AllocNew`, `AllocRendezvous`, `AllocShare`, `Open`) | 5 | capa de *handles*: valida el tamaño del extent (`ERR_EXTENT_SIZE! size[%d] max[%d]`) y la unidad (`DMM_UNIT_INVALID!`) |
| `AsyncAllocNew` | 9 | reserva **asíncrona** (cola OSAL) |
| `AsyncAllocRule` | 7 | variante asíncrona por **reglas** |
| `LoadExtraMap` | 7 | carga asíncrona del **mapa extra** de unidades |

`Rdv` = **Rendezvous** (confirmado por el nombre completo `MemoryHandle::AllocRendezvous`
`0x43cceb4c`): el *handles* existe pero la unidad no se reserva hasta que ambas partes se
encuentran.

### 2.1 Cuatro clases de error del DMM

| clase | n | significado |
|---|---|---|
| `ERR_DMM_RET_CODE` | 10 | el servidor de memoria devolvió un código de error |
| `ERR_DMM_DIFFERENT_COMP` | 10 | **la unidad pertenece a otro componente**: el mensaje incluye `msg_id %08x, my_id %08x` → el `msg_id` recibido no coincide con el propio `my_id` |
| `ERR_DMM_HANDLE` | 4 | handle inválido o ya liberado |
| `ERR_DMM_OPEN` | 5 | la unidad no está abierta |

### 2.2 La capa asíncrona habla OSAL

Las tres operaciones asíncronas fallan con códigos **OSAL**, no DMM: `ERR_OSAL_MSGQ`
(cola de mensajes), `ERR_OSAL_HANDLE`, `ERR_OSAL_UIPC` (comunicación inter-proceso) y
`rcv Invalid Src!: 0x%08x` (origen inesperado de la respuesta). Esto coincide con lo que
S38Ya había observado: en `av-cam.bin` la frontera **DMM↔OSAL** es real, no una inferencia.

## 3. Mapa función → traza (25 funciones)

La atribución se hace con el esquema **PIC** (`destino = literal_del_pool + (add rX,pc + 4)`,
probando todos los `ldr` del registro) y los prólogos Thumb. Resultado: una función por
operación, más un bloque asíncrono:

| función | n trazas | operaciones que reporta |
|---|---|---|
| `0x439011d8` | 1 | `AllocNew` (handle) |
| `0x439012d0` | 3 | `AllocNew`, `AllocNewRdv` |
| `0x43901380` / `0x439013be` | 1 / 2 | `AllocNewRdv` |
| `0x43901480` | 3 | `AllocShare`, `Free`, `FreeRdv` |
| `0x43901ccc` | 2 | `AsyncAllocRule`, `LoadExtraMap` (OSAL) |
| `0x43902168` | 4 | `AllocNew`, `AllocNewRdv`, `AllocShare`, `LoadExtraMap` |
| `0x439023b8` / `0x43902418` | 3 / 4 | `AllocNewRdv`, `Close`, `FreeRdv`, `MemoryHandle` |
| `0x43902786` / `0x439027f0` | 1 / 4 | `Free`, `MemoryHandle` |
| `0x43902a34` | 5 | `AllocNew`, `LoadExtraMap` |
| `0x43902c2c` | 5 | `AllocNewRdv`, `AsyncAllocRule` |
| `0x43902df8` | 8 | `AllocShare`, `AsyncAllocRule`, `LoadExtraMap`, `Open` |
| `0x43902fbc` / `0x43903118` | 3 / 2 | `Free`, `Open` / `FreeRdv` |
| `0x43903280` | 6 | `AsyncAllocNew`, `MemoryHandle`, `Open` |
| `0x43903414` | 4 | `AsyncAllocRule`, `Close` |
| `0x43903558` / `0x439035e0` / `0x4390366c` / `0x43903720` | 2 / 1 / 5 / 3 | los cuatro `MemoryHandle::*` |
| **`0x439037c0`** | **24** | **`AsyncAllocNew`** (bloque asíncrono) |
| **`0x43903b80`** | **17** | **`AsyncAllocRule`** |
| **`0x43903d5c`** | **8** | **`LoadExtraMap`** |

## 4. Correspondencia con el DMM del userland (S37)

S37 decodificó en `libmprctrl.so` la clase `DmmAccess` (y `DmmAccessPLA` para los accesores).
Sus símbolos exportados se comparan uno a uno con la API del firmware:

| firmware `[CAM_DMM]` (fw3.21) | userland `DmmAccess` (libmprctrl.so) |
|---|---|
| `AllocNew` | `DmmAllocateNEWAndOpen_body`, `DmmAllocateAndOpen` |
| `AllocNewRdv` (rendezvous) | `DmmAllocateAndOpen`, `DmmReuseAndOpen` |
| `AllocShare` | `DmmShare`, `DmmShareAndOpen` |
| `Free` | `DmmFree`, `FreeDmmMemory`, `DmmCloseAndFree` |
| `FreeRdv` | `DmmCloseORFree_body` |
| `Open` / `Close` | `DmmOpen` / `DmmClose` |
| `MemoryHandle::*` | `GetUnitHandleFromDmmAlloc`, `GetExtAdrsFromDmmAlloc`, `GetExtAdrsFromDmmOpen`, `GetDmmExtList` |
| `ERR_DMM_RET_CODE` | `DmmAccess::GetDMMRetMsg(short)`, `CheckDMMRetCode(short, char*)` |
| errores OSAL de la capa asíncrona | `DmmAccess::CheckOSALRetCode(OSAL_ERR, char*)` |

→ **el userland es un cliente del DMM del firmware**, no una reimplementación: el servidor de
memoria vive en `av-cam.bin` y el userland lo usa por OSAL (esto cierra la cadena que S37
dejó abierta y encaja con la "frontera DMM/OSAL" de S38).

## 5. Diferencial con la A7S fw3.20

- La A7S fw3.20 tiene **0** trazas con el prefijo `[CAM_DMM]:`, pero **los mismos mensajes
  existen sin etiqueta**: comparando texto a texto (ignorando los especificadores de
  formato) **50 de las 54** cadenas tienen equivalente directo.
- Las **4** restantes son los mensajes de `AllocNew`: en la A7S el mismo error se registra con
  otra forma, `AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x` (`0x43cb4f99`), es
  decir, la fw3.21 **sustituyó** esa variante por cuatro mensajes detallados
  (`ERR_DMM_RET_CODE`, `ERR_DMM_DIFFERENT_COMP`, `ERR_DMM_HANDLE`, `ERR_DMM_OPEN`).
- Diferencia menor de formato: la A7S escribe `0x%x` y `%d` donde la A6000 escribe `%x` y
  `%d` (mismos datos, especificadores más poor).
  → **la API del DMM es la misma en A6000 fw3.21 y A7S fw3.20**; la fw3.21 solo añade la
  etiqueta de módulo y detaila el caso `AllocNew`.

## 6. Relación con los demás hitos

- **S106** (`IMAGING_CAP`): el gestor de captura pide unidades al DMM (`GetMem_*`,
  `ShareMem_StlRaw8`, `UseRaw_DualRec`) y su traza `SetDmmInfo) FATAL! overwrite: id 0x%x
  handle 0x%x, type 0x%x` (`0x43ca9bd1`) es del mismo servidor: el DMM mantiene la
  información de las unidades (`tDmmInfo`).
- **S107** (`CamCore`/`ResourceStack`): la pila de recursos de CamCore es un **cliente** del
  DMM (adquiere/libera unidades de RC, DFE y memoria de imagen).
- **S37/S38**: el otro extremo (userland) y la frontera OSAL.
- **S89** (`IDT`/`IDT_OPD`): los mapas que el imager recibe se sirven desde unidades de
  memoria del DMM.

## 7. Verificaciones hechas (trazabilidad)

| afirmación | cómo se comprueba |
|---|---|
| 54 trazas `0x43cce6ae`–`0x43ccf1c3` | `extract_dmm.py` cuenta el prefijo en los bytes |
| 11 operaciones y 4 clases de error | mismo script, agrupando por el texto tras el prefijo |
| 25 funciones en `0x439011d8`–`0x43903d5c` | `extract_dmm.py` (PIC + prólogos Thumb) |
| 50/54 comunes con la A7S | comparación normalizada contra el blob de la A7S |
| caso `AllocNew` sustituido en fw3.21 | `AllocNew(DMM_OPTION_NOUNIT_WARN)` en `0x43cb4f99` (A7S) |
| API del userland | `llvm-nm -D` sobre `libmprctrl.so` (30+ símbolos `DmmAccess`) |

## 8. NO VERIFICADO / abierto

- Los **códigos numéricos** de `ERR_DMM_*` y `ERR_OSAL_*`: el firmware solo imprime el
  *nombre*; los valores concretos no se han extraído.
- El **formato del mensaje OSAL** de la capa asíncrona (payload, id de origen, correlación):
  S38 lo dejó en `NO_VERIFICADO` para el lado userland; aquí solo se ve el canal y los
  nombres de error.
- La **tabla de reglas** que usa `AsyncAllocRule` (qué reglas y de dónde se cargan).
- La implementación de `LoadExtraMap` (qué "mapa extra" carga).
- Nada de esto **afecta a S51**.

## 9. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 54 cadenas con vaddr/offset/texto |
| `func_map.json` | mapa función → traza (25 funciones) |
| `summary.json` | operaciones, clases de error y diferencial con la A7S |
| `extract_dmm.py` | script de extracción (reproducible) |
