# S59 — Validación cruzada Claude ↔ GPT-6.1 Sol

20-10-2026. Invocaciones reales de `codex exec` (v0.162.1, `-m gpt-6.1-sol`, `model_reasoning_effort="medium"`); entradas y registros en `analysis/s59/sol/` (`task.md`, `run1.log`, `last-message.txt`; `task2.md`, `run2.log`, `review-last-message.txt`). Ambas tareas empezaron con la regla de silencio.

## Ronda 1 — GPT investiga IMX210 (sandbox `workspace-write`)

Entregó `docs/capture/s59-sol.md`, `analysis/s59/sol/` y `tests/test_s59_sol.py` (11 tests; los reejecuté: **11/11 OK**). Claude re-verificó de forma independiente en bytes: SHA A6000 (`b60c845c…`), `0x43ae84c0..c6` (`add.w r0,r0,#0xdd0`), `0x437aab3c..52` (VdNum), `0x43b00da0`/`0x43b00dd4` (copia 80 B y guarda `+0x57c`). Coinciden con SOL-01/02/03/05/08. No re-ejecuté SOL-06/07/09/10/11 (confianza en su informe y tests ejecutados; no verificados por Claude por separado).

## Ronda 2 — GPT revisa A7S (sandbox `read-only`)

Veredicto de GPT: **CAMBIOS**. Tabla de resolución:

| Punto de GPT | Resolución |
|---|---|
| C59-1/2/3 reproducidos (12/12 parejas, 127/94/26 B, base `0xfc088300`) | CONFIRMADO |
| C59-8 único llamador (barrido de 11 455 416 B con BL/BLX/B.W/punteros) | CONFIRMADO, límite «llamada directa» añadido |
| C59-5: omitía `0xff = desactivado` en `[dbg+0xc]` (`0x436f5d9a`) | CORREGIDO en informe y test |
| C59-7: «solo difieren los emisores» era falso (17045/17035/17003 instrucciones; ramas por grupo de modo) | **CORREGIDO**: nuevo `blockdiff.py`/`blockdiff.json` + test; la diferencia son emisores + lectores de sustituciones de depuración |
| `modediff.py` atribuye funciones por «último push lr» (etiqueta `0x43ada062/07c`) | Marcado como orientativo; prueba = `blockdiff.py` |
| C59-9: campos `+0x50..0x55` incompletos (`0x4c/4d`→`+0x54..57`, `0x4e..51`→`+0x5c..5f`) | CORREGIDO |
| C59-10: 34 llamadas a `0x439b3918` en `0x4c/4d` (24 en el resto) y falta `0x438f7114` | CORREGIDO |
| `s59-claude.md` decía que el constructor no se emuló | CORREGIDO |
| «fin de integración no es evento de C_Imager» sobreafirmado | Rebajado a NO IDENTIFICADO |
| Sin contradicción con `s59-sol.md` | CONFIRMADO |

REA no se usó en la revisión (la política `never` de aprobación rechazó `binary_session`); GPT lo declaró y usó bytes/Capstone/Unicorn. El sandbox read-only no permitió ejecutar los generadores que escriben.

## Contradicciones corregidas

1. **S58-C** (base `0xf3c00300`, 5 tramas, longitudes 126/126/126/101/26): artefacto del objeto sintético (S59-C3). El contenido de registros se conserva.
2. **S58-D** («mensajes dependen quizá de estado no inicializado»): es lista blanca de modos (S59-C5).
3. **S58-A §5** (atribución de `clk` al objeto de histogramas): descartada por S59-G4.
4. Borrador de Claude «solo difieren los emisores»: corregido por GPT (S59-C7).

## Pruebas ejecutadas (quién)

Claude: `tests/test_s59_claude.py` (9), regresiones S56–S58 (83), scripts de `analysis/s59/claude/`. GPT: `tests/test_s59_sol.py` (11), probes de `analysis/s59/sol/`, y en la revisión 7 tests de Claude, 12 parejas, trazas por etapa, 4 variantes de depuración, barridos. Claude reejecutó los 11 tests de GPT.
