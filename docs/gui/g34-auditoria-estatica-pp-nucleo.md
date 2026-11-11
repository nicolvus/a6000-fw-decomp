# G34 — Auditoría estática del Picture Profile en el núcleo (11-11-2026)

Continúa [G32](g32-auditoria-picture-profile-3-73.md) y [G33](g33-pp-black-knee-detail-still.md). **Solo estática** sobre `av-cam.bin` (A6000 fw3.21; el paquete 3.74 solo añade la cueva de G33): capstone + barridos de patrón (`scripts/gui/pp_static_audit.py`). Motivo: el usuario informa (3.74 instalado) de que **Black Gamma Range/Level y los ajustes siguientes de PP no hacen nada visible, salvo Saturación**. Cámara no alcanzable por red: nada medido en vivo (`scripts/gui/pp_probe.py` queda listo).

## 1. Conexiones verificadas (bytes)

| Eslabón | Resultado |
|---|---|
| Escritura del `cfg` | solo dos funciones lo escriben en `0x138…0x173`: el desempaquetador del `0x4066` (`0x43802a28`, función `0x43801fc8`) y la de valores por defecto (`0x43804610`). Cada byte PP tiene su campo (0x150 Black Level, 0x151/0x152 BG, 0x153 gamma, 0x154–0x158 Knee, 0x159–0x15f Detail) |
| Lectura del `cfg` por el camino real (`**(g+4)` → `cfg`) | **un único lector**: el proveedor de parámetros de 8 bytes `0x438280d0` (selector `grupo|índice` en `r0`). Lee **solo `0x138–0x153`**: tipo/nivel de Color Mode (`0x138/0x13c`), WB Shift (`0x13d–0x140`), filtro (`0x144`), Color Depth (`0x148–0x14d`), Saturación (`0x14e`), Fase (`0x14f`) y gamma (`0x153`), todos en el grupo `0x30` |
| Black Level (`0x150`), BG Range/Level (`0x151/2`), Knee (`0x154–0x158`), Detail (`0x159–0x15f`) | **ningún lector en ese proveedor**. Los lee solo la rutina `0x437b1048` (relleno de un bloque grande de «información de toma», que busca la etiqueta `0xb024`): copia `0x150–0x153` y `0x156…` a `bloque+0xa72…0xa92` y **omite `0x154/0x155`** (Knee Mode y Max Point, `0x437b1d22`). Del bloque solo leen `+0xa72…0xa92` unos getters de 8 bytes (`0x438e56a0`, `0x438e56da`, `0x438e56f6`, `0x438e429a…0x438e4354`) de una tabla de 285 punteros (`0x4400eac8…`) sin llamador directo localizado |
| Mismo patrón en la A7S | sin lector propio de esos campos (G32); no hay nada que portar |

## 2. Veredicto por ajuste (3.74)

| Ajuste | Camino | Estado estático | Por qué podría no verse |
|---|---|---|---|
| Saturación | cfg `0x14e` → proveedor `0x438280d0` grupo `0x30` | conectado (el usuario lo ve) | — |
| Color Mode tipo/nivel, Fase, Color Depth ×6, WB Shift ×4 + filtro | mismo proveedor y grupo que Saturación | **conectados por la misma vía**; no hay razón estática para que Saturación sí y estos no | efecto sutil (Fase ±7, Depth ±7, WB ±9) o el grupo/índice no se consulta en el modo usado: **sin medir** |
| Gamma / selector (`0x153`) | proveedor + tabla `TAB[gamma*2+modo]` | conectado | Movie = la de siempre; S-Log3 sin causa demostrada (G32-C) |
| Black Level | gancho G33 (snapshot `pp` → `pp_curve`) | aplicado sobre la LUT de 96 puntos | ±15 → ±60 códigos de ~1727 (~3,5 %) |
| **Black Gamma Range/Level** | gancho G33 | aplicado, **pero amplitud `5·nivel` = 35 códigos (≈2 %) a +7 y solo en el 10–30 % inferior** | **demasiado débil para verse**: hallazgo de calibración propio (mis constantes) |
| Knee | gancho G33 | solo actúa por encima del punto (75–105 %) y desactivado con Max Point 4 / Point ≥ 12; no en S-Log | invisible sin altas luces o con valores por defecto |
| Detail Level/V-H/Limit/Crispening | ganchos G33 en `pp_gain`/`pp_coring` | solo con Detail Mode **Manual**; Auto no cambia nada | depende de modo y de contenido (bordes) |
| B/W Balance, Hi-Light Detail | — | sin implementar (G33-B) | — |

## 3. Qué NO se ha podido establecer

- Qué recibe el bloque `+0xa72…0xa92` ni quién llama a su tabla de getters: sin llamador directo ni puntero a la tabla (acceso por la GOT); no demostrado que llegue a hardware. Por eso G33 actúa sobre la LUT y las salidas APC en vez de tocar ese camino.
- Que los tres constructores de LUT (`0x43854718`, `0x43854a28` y sus llamadas `0x438698ae`/`0x4386971a`) y las funciones APC (`0x438b3ea8`) se ejecuten en visión en vivo/vídeo/foto con PP activo: **sin medir** (sondear `pp_probe.py`: caché `pp_curve` ≠ 0 prueba que se ejecutaron).
- Que `Color Depth/Fase/WB` produzcan un cambio visible: el único dato es que comparten vía con Saturación.
- Limitación del barrido: seguimiento lineal de registros por función; un lector que reciba el `cfg` por argumento o por otra cadena no aparece.

## 4. Acciones propuestas (no hechas)

1. Subir la amplitud de Black Gamma (p. ej. `14·nivel`, ≈6 % a +7) y reconstruir (3.75): único cambio de constantes con respaldo claro en el análisis.
2. Medir con `pp_probe.py` en cámara: cfg `0x138…0x15f` tras cambiar cada ajuste, snapshot `pp`, caché y `W`.
3. Si la caché no se rellena en ningún modo: mover el gancho de curva a otro constructor (revisar `0x43854d14` y los otros llamadores de la tabla).
