# S114 — el motor de secciones de la captura: 17 ids ↔ 17 etapas

**Hito de la línea de ingeniería inversa general** (no afecta a S51: A/B/C = NO). Cierra la
pregunta que S106 dejó abierta.

Informe: [analysis/s114_sections/section_engine.md](../../analysis/s114_sections/section_engine.md) ·
Datos: `section_map.json` · Test: `tests/test_s114_sections.py`.

## Hallazgo central

**15 de las 17 secciones** del gestor de captura (tabla `{id u32, manejador u32}` en
`0x43ff8fb4`) quedan **nombradas**:

| id | manejador | etapa |
|---|---|---|
| `0x01` | `0x437eb144` | **Prelight** (nuevo: se identifica porque su manejador llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) |
| `0x02`–`0x10` | … | Exposure, Read, AfterRead, DevEntry, CorrectRaw, OpdBeforeNR, Develop, Marble, FeatureEffect, AfterEffect, Encode, AfterEnc, SortJpeg, DevExit (por su propio `*_Selector.cpp`) |
| `0x00` | `0x437eabfc` | **sin nombre** (selector puro de perfil: solo llama a `0x43ae75dc` y `0x43ae76ca`; elige un registro de 20 B según el modo de captura) |
| `0x06` | `0x437eaa5c` | **sin nombre** (misma forma que `0x01` pero sin llamar al selector de Prelight) |

Además: 5 de los 16 nombres de selector los registra **código fuera de la tabla**
(`SequenceFilter` en 5 funciones con 14 registros; `CapturePrelight` en 2; `CaptureDevelop` +
`CaptureMarble` en una compartida) → hay **selectores auxiliares** que no son secciones.

## Método

Referencia PIC de la cadena (`literal + (add rX,pc + 4)`) → inicio de función por prólogo
Thumb (`push {..,lr}` / `push.w {..,lr}`) → si el sitio cae dentro del manejador, ese es el
selector de la etapa; si no, se leen sus llamadas `bl` (capstone) y se busca si llama a la
función que registra el nombre.

## Abierto / NO VERIFICADO

- El significado de las secciones `0x00` y `0x06` (no tienen nombre en el firmware).
- La tabla de 20 B por sección (5 u32) y su uso.
- La relación entre secciones (`SectionQueueManager.cpp` `0x43caaf62`, `SectionEndFunc.cpp`).
- Si `SequenceFilter` es una sección más o un filtro externo.
- Nada de esto cambia S51.
