# S19-07 — tabla LIRO: entradas restantes

## Alcance y corrección de inventario

**VERIFICADO** — `docs/capture/s18-main-init-437ebed8.md` deja como ya
analizadas las filas seleccionables `0xa0`, `0xc8`, `0xdc` y `0x104`, más
`0xb4` por rama directa. Por tanto, el pendiente real eran las diez filas no
seleccionables: `0x00, 0x14, 0x28, 0x3c, 0x50, 0x64, 0x78, 0x8c, 0xf0, 0x118`.

**VERIFICADO (corrección de nomenclatura)** — en
`analysis/av-cam-analysis-view.elf`, las direcciones Thumb de la tabla, sin el
bit 0, son entradas de funciones completas: comienzan por `push {r4,lr}`, llaman
`FUN_43afdf16()` y despachan con `tbb`. No son stubs de cuatro bytes en esta
vista ELF. La afirmación histórica de trampolines no se usa para atribuir
semántica a estos flujos.

Método: `llvm-objdump -d --triple=thumbv7-none-eabi` y decompilación Ghidra
solo-lectura del proyecto `silent-liro` con las direcciones pares. Firmware:
`av-cam.bin`, base `0x43541000`.

## Inventario reconstruido

| Fila | Entrada Thumb / función | Estado y condiciones | Adquisición, codificación y finalización | Error / relación convencional |
|---|---|---|---|---|
| `0x00` | `0x43b1bc0d` / `FUN_43b1bc0c` | **VERIFICADO:** `FUN_43afdf16()==0`; si no, retorna `5`. | **NO_VERIFICADO:** sólo delega a `FUN_437ed568(param)`. | Gate mínimo de la misma familia; no prueba adquisición ni codificación. |
| `0x14` | `0x43b1bc25` / `FUN_43b1bc24` | **VERIFICADO:** selector 0..6; consulta contexto `FUN_43ae75dc/7648`, usa `+0x754`, `+0x1d8`, `+0x1e0`. | **INFERENCIA:** orquestador convencional: prepara/reintenta y llega al bloque común que actualiza `+0x23..+0x27` tras `FUN_43ae9226(...,0x9400,...)`. No hay llamada etiquetada como encoder recuperada. | **VERIFICADO:** rutas de retry, cancelación y retornos `0/1/2/3/5`; no equivale a JPEG finalizado. |
| `0x28` | `0x43b1bc71` / `FUN_43b1bc70` | **VERIFICADO:** selector 0..6 y mismo contexto; variante con literales `0xf6/0x1017`. | Igual bloque común de preparación/metadatos. **NO_VERIFICADO:** adquisición física y codificación real. | Misma familia convencional; sin marca Silent/EFCS. |
| `0x3c` | `0x43b1bcc7` / `FUN_43b1bcc6` | **VERIFICADO:** selector 0..4; añade `FUN_437de2fc`, `FUN_43ae9130`, `FUN_439018b0` y `FUN_43549020` antes del bloque común. | **INFERENCIA:** variante de pre-etapa de captura; el destino exacto de esas cuatro llamadas no queda nombrado. | Retornos `0/1/2/3/5`; no se atribuye cancelación de buffer ni finalización de imagen. |
| `0x50` | `0x43b1bd13` / `FUN_43b1bd12` | **VERIFICADO:** selector 0..4; casos delegan `FUN_43afe9f4` o `FUN_437ed568`; usa `+0x754`. | Comparte preparación y actualización de metadatos. **NO_VERIFICADO:** lector de sensor, buffer o encoder. | Variante convencional, no Silent. |
| `0x64` | `0x43b1bd5f` / `FUN_43b1bd5e` | **VERIFICADO:** selector 0..5, `FUN_43afe9f4`, `FUN_437ed568`; literales `0xf6/0x1024`. | Bloque común; sin identificador de codificador. | Retry/cancel/error comunes; no prueba liberación. |
| `0x78` | `0x43b1bdb5` / `FUN_43b1bdb4` | **VERIFICADO:** selector 0..4 y pre-etapa `43ae9130/439018b0/43549020`; luego ruta común. | **INFERENCIA:** preparación convencional alternativa. | Sin enlace recuperado a Silent ni a adquisición electrónica. |
| `0x8c` | `0x43b1be01` / entrada sin nombre propio Ghidra | **VERIFICADO:** selector y campos de petición comunes, incluyendo `+0x754/+0x4b70/+0x4d8/+0x4a7c`. | Misma cola común de metadatos `0x9400`; adquisición/codificación **NO_VERIFICADO**. | Convencional por similitud estructural, no por una etiqueta explícita. |
| `0xf0` | `0x43b1bfc9` / `FUN_43b1bfc8` | **VERIFICADO:** selector 0..7; maneja retries/cancelación y delega `FUN_43afe9f4` y `FUN_437ed568`. | **INFERENCIA:** variante rica del mismo coordinador convencional; no se recuperó una operación de encode final. | Retorno `0` no se interpreta como éxito JPEG. |
| `0x118` | `0x43b1c097` / `FUN_43b1c096` | **VERIFICADO:** selector 0..6 con retries/cancelación y bloque común. | **NO_VERIFICADO:** adquisición, codificación, publicación/fin y ownership de buffers. | Misma familia convencional; no contiene condición Silent/EFCS identificada. |

## Hallazgos transversales

- **VERIFICADO:** las diez pendientes son máquinas de estados locales (selector
  `FUN_43afdf16` y `tbb`), no saltos vacíos; sus estados observables devuelven
  `0, 1, 2, 3` o `5` según ruta.
- **VERIFICADO:** las variantes comparten el contexto y la cola de trabajo con
  las cinco filas antes analizadas, incluidos los campos `+0x754`, `+0x4b70`,
  `+0x4d8` y `+0x4a7c`, y el registro de metadatos `0x9400`.
- **INFERENCIA:** es una familia de secuencias de captura convencional con
  variaciones de precondición/retry, no una tabla de modos Silent.
- **DESCARTADO:** tratar el retorno `0`, las escrituras de metadatos o la mera
  presencia de la tabla como prueba de captura terminada, JPEG codificado,
  liberación de buffers o SilentShutter funcional.
- **NO_VERIFICADO:** semántica de cada estado, proveedor de píxeles, codificador
  JPEG, finalizador/publicador y ruta de error/ownership extremo a extremo.

## Trazabilidad

- Direcciones: tabla inicializada por `0x437ebed8`; callbacks GOT estáticos
  documentados en `s18-main-init-437ebed8.md`.
- Archivo/método: `analysis/av-cam-analysis-view.elf`; LLVM Thumb y exportación
  Ghidra en `analysis/session19/codex-runs/run-007/liro-all-entries.json`.
- Evidencia estructurada: `analysis/session19/evidence/liro-remaining-sequences.json`.

SilentShutter sigue sin declararse funcional.
