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

## 5. Black Gamma ampliado (CFW 3.75, construido, sin instalar)

`pp_tone.c`: amplitud por nivel = `RANGO/32` códigos (antes 5 fijos). Tope por monotonía: la campana `4t(1−t)` tiene pendiente máxima `4·A/RANGO`; con más de `RANGO/28` por nivel la curva dejaría de ser monótona y el recorte monótono crearía una meseta. Emulado (Unicorn) sobre el `AV-CAM.BIN` del paquete 3.75 (escala de la curva 0…1023): Wide ±7 → +66/−67 códigos (6,5 %), Middle ±7 → +44/−45, Narrow ±7 → +22/−23; monótona en todos los casos, sin cambios fuera del rango, neutro devuelve el puntero original. `tests/test_g33_pp_tone.py` (15 pruebas con test_g31) en verde. `.dat` 3.75 sha256 `bae03dd3ea47ff99ac92574d8a5b9034bbfd3b4cc802e77682d5d2847532f4bf` (sustituye al anterior), **no instalado** (instalar exige autorización expresa) y sin auditoría independiente.

## 6. Revisión de rangos poco amplios (3.75, emulado sobre el `AV-CAM.BIN` del paquete)

Escala de la curva 0…1023. Efecto máximo medido antes → después:

| Ajuste | Antes | Después | Cambio |
|---|---|---|---|
| Black Gamma Wide / Middle / Narrow (±7) | 66 / 44 / 22 (6,5 / 4,3 / 2,2 %) | 87 / 55 / 28 (8,5 / 5,4 / 2,7 %) | rangos 39 / 25 / 12,5 % (antes 30 / 20 / 10 %), amplitud RANGO/32 por nivel |
| Black Level ±15 | 59 / 57 (5,8 %) | 89 / 83 (8,7 %) | 6 códigos por paso (antes 4) |
| Knee automático (Max Point 0, High / Mid / Low) | blanco 1000 / 1010 / 1018 (−2,2…−0,5 %) | 958 / 971 / 984 (−6,4…−3,8 %) | pendiente 0,375 / 0,5 / 0,625 (antes 0,78 / 0,88 / 0,96) |
| V/H Balance ±2 (base 8/8) | (5,10) / (10,5) | (4,11) / (11,4) | ±60/256 por paso (antes ±38) |
| Crispening 7 (coring base 10/20/30) | 20/41/62 (×2,1) | 37/74/112 (×3,7) | +100/256 por paso (antes +40) |

Sin cambio por ser ya amplios: Knee manual (blanco 805…985 con Point 0, nada con Point 12 = 100 %), Detail Level (×0,18…×1,82), Limit. Detail sigue solo con Detail Mode Manual. Tests: 15 de 15. **No instalado.**
