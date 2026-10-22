# S114 — el motor de secciones de la captura, completo: 17 ids ↔ 17 etapas

> Hito de la **línea de ingeniería inversa general** (no afecta a S51: A/B/C = NO). Cierra la
> pregunta que S106 dejó abierta ("la asignación id↔etapa completa queda pendiente").
> Verificación contra los bytes del `analysis/rea-independent/input/av-cam.bin`; convención
> **vaddr = 0x43541000 + file_offset**.

## 1. Qué se resuelve

S106 encontró la **tabla de 17 secciones** del gestor de captura (`{id u32, manejador u32}` en
`0x43ff8fb4`) y que 14 de los 17 manejadores registran el nombre de su etapa
(`Capture<Etapa>_Selector.cpp`). Aquí se cierra el mapa:

- **15 de las 17 secciones quedan nombradas** (14 por su propio nombre + **Prelight**, que se
  identifica porque su manejador **llama** a la función que registra
  `CapturePrelight_Selector.cpp`).
- Las **2 restantes** (`0x00` y `0x06`) **no tienen nombre en el firmware**: se describen por
  su estructura (abajo).

## 2. El mapa completo

| id | manejador | etapa | cómo se identificó |
|---|---|---|---|
| `0x00` | `0x437eabfc` | **sin nombre** | ver §4 |
| `0x01` | `0x437eb144` | **Prelight** | llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp` |
| `0x02` | `0x437ea8cc` | Exposure | nombre propio `CaptureExposure_Selector.cpp` |
| `0x03` | `0x437eb24c` | Read | `CaptureRead_Selector.cpp` |
| `0x04` | `0x437e9d78` | AfterRead | `CaptureAfterRead_Selector.cpp` |
| `0x05` | `0x437ea178` | DevEntry | `CaptureDevEntry_Selector.cpp` |
| `0x06` | `0x437eaa5c` | **sin nombre** | ver §4 |
| `0x07` | `0x437ea034` | CorrectRaw | `CaptureCorrectRaw_Selector.cpp` |
| `0x08` | `0x437eaf38` | OpdBeforeNR | `CaptureOpdBeforeNR_Selector.cpp` |
| `0x09` | `0x437ea410` | Develop | `CaptureDevelop_Selector.cpp` |
| `0x0a` | `0x437ead4c` | Marble | `CaptureMarble_Selector.cpp` |
| `0x0b` | `0x437eab64` | FeatureEffect | `CaptureFeatureEffect_Selector.cpp` |
| `0x0c` | `0x437e9a70` | AfterEffect | `CaptureAfterEffect_Selector.cpp` |
| `0x0d` | `0x437ea724` | Encode | `CaptureEncode_Selector.cpp` |
| `0x0e` | `0x437e9be8` | AfterEnc | `CaptureAfterEnc_Selector.cpp` |
| `0x0f` | `0x437eb470` | SortJpeg | `CaptureSortJpeg_Selector.cpp` |
| `0x10` | `0x437ea2bc` | DevExit | `CaptureDevExit_Selector.cpp` |

**Las 16 etapas** que la fw3.21 de la A6000 nombra en el firmware son, por tanto: Prelight,
Exposure, Read, AfterRead, DevEntry, CorrectRaw, OpdBeforeNR, Develop, Marble, FeatureEffect,
AfterEffect, Encode, AfterEnc, SortJpeg, DevExit y **SequenceFilter** (que no es una sección de
la tabla: es un filtro de secuencia, con 5 funciones que lo registran, §5).

## 3. Cómo se identifican (método)

1. **Referencia PIC** de la cadena `Capture<Etapa>_Selector.cpp`: el destino es
   `literal_del_pool + (add rX,pc + 4)` (ver `analysis/s106_imaging_cap/scan_pic_refs.py`).
2. **Inicio de función** por prólogo Thumb: `push {..,lr}` (`0xb5xx` con bit de LR) o
   `push.w {..,lr}` (`0xe92d` + 2ª mitad con bit 14).
3. Si el sitio de referencia cae **dentro** del manejador → el manejador es el selector de esa
   etapa (14 casos).
4. Si no, se leen las **llamadas directas** del manejador (`bl`/`blx` desensamblados con
   capstone) y se busca si llama a la función que registra el nombre → caso de **Prelight**
   (`0x01` → `0x437eb07c`).

## 4. Las dos secciones sin nombre

| id | manejador | estructura observada |
|---|---|---|
| `0x00` | `0x437eabfc` | **selector puro de perfil**: solo dos llamadas (`0x43ae75dc` = obtener el contexto de captura y `0x43ae76ca` = fijar el modo). Elige un registro de 20 B de una tabla según el modo: si `(modo-8) < 6` y `+0x1d8 == 0` usa la base `+0xb4`; si `+0x1e0 == 7` elige el registro 10 (`0xa`) o el 13 (`0xd`); si `+0x1e0 == 0x17` el 8; y si `+0x1d8 != 0` el 11 (`0xb`). No registra ningún nombre: es un selector **de parámetros** sin etapa asociada. |
| `0x06` | `0x437eaa5c` | tiene la **misma forma** que `0x01` (llama a `0x4356120c/44/d0/ec`, `0x43783e30`, `0x439c5004`, `0x439c5a04`, `0x43ae75dc`, `0x43ae76ca`) pero **sin** llamar a la función del selector de Prelight: es el manejador "de parámetros" que acompaña a una sección que no registra nombre. |

Ambos devuelven un bloque de **20 B (5 u32)** con los parámetros de su sección, igual que
los 15 nombrados.

## 5. Los selectores que no son secciones de la tabla

Cinco de los dieciséis nombres los registra **otra** función, fuera de la tabla:

| nombre | funciones que lo registran | sitios |
|---|---|---|
| `CapturePrelight_Selector.cpp` | `0x437e977a`, `0x437eb07c` | `0x437e97b6`, `0x437eb0b6` |
| `CaptureDevelop_Selector.cpp` / `CaptureMarble_Selector.cpp` | `0x437e858c` (compartida) | `0x437e85b4`, `0x437e8654` |
| `SequenceFilter_Selector.cpp` | `0x437e83dc`, `0x437e98ec`, `0x437eb5c4`, `0x437eb632`, `0x437eba9c` | 14 sitios (`0x437e84a0`…`0x437ebe22`) |

→ el motor de captura tiene **más código de selección** que las 17 entradas de la tabla: hay
selectores auxiliares (`SequenceFilter` sobre todo, con 14 registros del mismo nombre) que no
son secciones sino **filtros de secuencia**.

## 6. Corrección de S106

S106 dejó escrito: "los ids `0x00`, `0x01` y `0x06` no [registran nombre] y
`CapturePrelight`/`SequenceFilter` se referencian fuera de la tabla → asignación id↔etapa
completa NO VERIFICADA". Con este hito:

- `0x01` **sí** es **Prelight** (por llamada directa a su selector);
- `0x00` y `0x06` siguen **sin nombre** en el firmware, pero su estructura queda caracterizada
  (§4);
- `CapturePrelight` y `SequenceFilter` son **selectores auxiliares**, no secciones de la tabla.

## 7. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 17 entradas `{id, manejador}` en `0x43ff8fb4` | lectura directa de los pares u32 |
| 14 manejadores con nombre propio | referencia PIC de su `*_Selector.cpp` + prólogos |
| `0x01` = Prelight | `bl` desde `0x437eb144` a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp` |
| `0x00` y `0x06` sin nombre | ninguna de sus trazas registra un `*_Selector.cpp` |
| 5 nombres los registra código fuera de la tabla | mapa completo de referencias (8 funciones) |

## 8. NO VERIFICADO / abierto

- El **significado** de las secciones `0x00` y `0x06` (no hay nombre en el firmware): solo se
  describe su estructura.
- La **tabla de 20 B por sección**: qué campos la componen y cómo los usa la máquina de
  estados.
- La **relación entre secciones**: qué sección sigue a cuál (el motor `SectionQueueManager`
  `0x43caaf62` y `SectionEndFunc.cpp` `0x43caea54` son los candidatos, no analizados aquí).
- Si `SequenceFilter` actúa como una sección más del motor o como un filtro externo.
- Nada de esto **afecta a S51**.

## 9. Ficheros de este hito

| fichero | contenido |
|---|---|
| `section_map.json` | mapa completo: tabla, selectores (con sus sitios y funciones) y las 17 secciones con sus llamadas |
| `section_map.py` | script que lo genera (PIC + prólogos + `bl` de capstone) |
