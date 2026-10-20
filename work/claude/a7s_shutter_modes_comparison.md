# Modos de obturación A7S 3.20 vs A6000 3.21 — qué comparten y qué falta

Fuentes y método: ver `a7s_silent_execution_trace.md`. Todas las filas comprobadas por `tests/test_a7s_silent_facts.py`.

## Punto por punto (Silent)

| Eslabón | A7S 3.20 | A6000 3.21 | Clasificación |
|---|---|---|---|
| UI/menú Silent | `CmnViewProcessDataElementCustomSilentShutter`, `ACT_SilentShutter`, `isSilentShootingIconAvailable` | Sin cadenas `Silent` en `cmn_view_processDataMgr.so` A6000 ni `ACT_SilentShutter` en `CmnShootingInfoLayoutMgr.so` A6000; nodos `CautionConfig` presentes en ambos | VERIFICADO (cadenas) |
| libObj → LIRO `0x40e3` | Presente | Presente (`docs/silent-shutter-trace.md`) | VERIFICADO (A6000), INFERENCIA (A7S) |
| Receptor `0x40e3` | `0x437a9cb0` → estado `+0x250` | `0x438032d4` → estado `+0x238` | VERIFICADO |
| Conversor ajuste→tipo 0/2 | `0x4379ec04` | **Sin equivalente localizado**; ya se documentó `+0x238` sin consumidor de captura (`efcs-capture-selector.md`) | VERIFICADO A7S / NO VERIFICADO ausencia global A6000 |
| Tipo en captura | `cap+0x78c` (y `cap+0x748=1`) | — | VERIFICADO A7S |
| Selector de drive_mode | `0x43826d58(modo,sub,tipo)` → `0x4e/0x4f` | `0x437f7f98(modo,sub)`: misma lógica **sin la rama Silent** | VERIFICADO |
| Política de clase | `0x438649bc`: `tipo==2` → clase **0** | `0x43842158`: sin esa rama; clases 1/3/5 | VERIFICADO |
| Modos sensor | IMX235: 34 modos, incluye `4e 4f 50 51` (columnas 12/13 propias) | IMX210: 13 modos `{01,03,05,07,0a,0b,0f,10,12,18,19,1a,2f}`; `0x4e/0x4f` → error 2 en SetMode | VERIFICADO |
| SetExposure ShutMode | 0,1,3,4 (2 no soportado) | 0..4 todos con rama propia | VERIFICADO instrucciones; bits distintos por sensor |

## Clases de obturación (selector `param+9` de SetExposure)

| Clase | Origen en la política | IMX235 (`0x436f4168`) campo `0x440220a8` / `0x44021fee` | IMX210 (`0x436d6f6c`) campo byte `+2` |
|---|---|---|---|
| 0 | A7S: Silent tipo 2. A6000: no producida por la rama normal de la política (overrides posteriores no evaluados aquí) | b2=0 b4=0 b6=0; `|=8` | b2=0 b4=0 b6=1 b7=0 |
| 1 | `banco+0x4c4&0x80` o EFCS=1 | b2=1 b4=0 b6=0 | b2=1 b4=0 b6=1 b7=1 |
| 2 | override | **no soportado** | b2=1 b4=1 b6=0 b7=1 + 2 campos desde `param+8/+0x14` |
| 3 | EFCS≠1 (mecánico normal) | b2=1 b4=1 b6=0 | b2=1 b4=1 b6=1 b7=1 |
| 4 | — | b2=0 b4=0 b6=1 | b2=0 b4=0 b6=1 b7=1 |
| 5 | `banco+0x4c4&0x20` + umbral | (>4 → no soportado) | (>4 → no soportado) |

Los bits no se interpretan eléctricamente (sin datasheet). Que la clase 0 exista en el IMX210 **no** prueba que haga
lo mismo que en el IMX235: los patrones de bits difieren.

## Comparación con otros modos (estado)

- Mecánico / EFCS: clase 3 / 1 en ambos (A6000 ver `efcs-capture-selector.md`). VERIFICADO A6000; A7S por política.
- Silent: solo A7S, clase 0 + drive_mode `0x4e/0x4f`.
- Live View / vídeo: selector distinto (A6000 `0x4380e43c`); en A7S no trazado. NO VERIFICADO.
