# FILM-PB-1 · El log del MMgr en **todos** los estados guardados del arnés (26-11-2026)

Extracción y clasificación de la ruta de video en **215 `estado.zst`** de
`analysis/gui/g22/harness/live/*/` (721 subdirectorios, 51 G). Sin cámara, sin `git`, sin
instalar nada: solo `zstd -dc` + los scripts de `reports/evidence/`.

## 0. Respuesta corta

1. **215 estados, 215 ficheros de log (214 con contenido), 0 fallos de extracción.** `uilive`
   no conservaba `estado.zst` cuando le tocó el turno: su log sale vacío (§2).
2. **Ningún IFO se cargó en ningún perfil.** 165 perfiles llegan al IFO y los 165 reciben
   código de error (MP4 153, MP4+XAVC 9, MP4+XAVC+AVCHD 3); de los 214 con log, los otros 49
   no llegan ni a intentarlo.
3. **Ninguna reproducción.** `AviSeqPlay.cpp` aparece **siempre** con `Error=[…]` (166
   perfiles). Las 156 apariciones de `PlayMovie` y las 79 de `PbStart` son **constantes en los
   214 perfiles** (cadenas de ayuda y símbolos de los ELF), no líneas emitidas.
4. **No hay ninguna línea `Load OK` emitida.** Las que aparecen
   (`LoadAvi :  Load OK`, `FlashLoadMp4 : MP4 Load Completed`, `FlashLoadDcf : DCF Flash Load
   Success.`) son **literales de `.rodata`** idénticos en los 214 perfiles, no emisiones (§3).
5. **Lo único positivo emitido del corpus** (3 perfiles):
   `[AVI][MEDIA]    sources/avi_if/AviSeqMedia.cpp Error=[ER_OK] Line:2594`
   → es un paso de *media*, **no** un load ni una reproducción (§6).

## 1. Método (comandos exactos)

```bash
# 1) censo
ls analysis/gui/g22/harness/live/*/estado.zst | wc -l          # 215 (23:47–00:00), 721 dirs

# 2) extracción, por perfil (script ya existente en el repo)
zstd -dc analysis/gui/g22/harness/live/<perfil>/estado.zst \
  | python3 reports/evidence/film-pb-1-arnes-log-20261126/extraer_log_estado.py \
      reports/evidence/logs-arnes-todos/<perfil>.log.txt
# automatizado, 6 en paralelo (~25 min, I/O):
reports/evidence/claude-sub-logs-arnes-todos-20261126/extraer_todos.sh

# 3) segunda pasada ancha (marcadores sin tag) -> <perfil>.markers.txt
# 4) conteo en crudo de cada cadena clave -> <perfil>.agujas.tsv
python3 reports/evidence/claude-sub-logs-arnes-todos-20261126/analizar2.py    # index.tsv + firmas.md
python3 reports/evidence/claude-sub-logs-arnes-todos-20261126/tabla_perfil.py # perfil-error-ifo.md + mapa-codigos.md
```

Artefactos:

| qué | ruta |
|---|---|
| log por perfil (215 ficheros, 1 vacío) | `reports/evidence/logs-arnes-todos/<perfil>.log.txt` |
| marcador ancho por perfil | `reports/evidence/logs-arnes-todos/<perfil>.markers.txt` |
| conteos en crudo por perfil | `reports/evidence/logs-arnes-todos/<perfil>.agujas.tsv` |
| tabla perfil→error→IFO (215) | `reports/evidence/logs-arnes-todos/perfil-error-ifo.md` |
| código → sitio de impresión | `reports/evidence/logs-arnes-todos/mapa-codigos.md` |
| firmas agrupadas (14) | `reports/evidence/logs-arnes-todos/firmas.md` |
| índice máquina | `reports/evidence/logs-arnes-todos/index.tsv` |
| scripts y estado de ejecución | `reports/evidence/claude-sub-logs-arnes-todos-20261126/` |

## 2. Censo: el corpus está vivo (importante)

- 721 subdirectorios en `live/`; **215 con `estado.zst`** en la instantánea (23:47–00:00).
- Hay un **arnés corriendo** durante este trabajo (`davf2`, puerto 8624, otro proceso), que
  aún **no** tiene `estado.zst`: no entra en este censo y entrará en la próxima pasada.
- **`uilive`**: tenía `estado.zst` (152 MB) a las 23:34 y ya no lo tenía al leerlo; su log
  queda vacío. Es el único perfil sin log. `zstd -t` no aplica: el fichero no existe.
- Ningún perfil falló la descompresión: 215 ficheros escritos, 214 con líneas y `uilive.log.txt`
  en 0 B.

## 3. Regla metodológica: qué es una línea emitida y qué es un literal

El volcado contiene a la vez **el texto de log emitido** (con `\r\n` y vecinos de log) y el
**`.rodata` de las librerías**. Confundirlos invierte la conclusión, así que se usaron dos
discriminadores independientes:

- **valor dinámico rellenado** (`0xB0800001`, `Line:2594`): un literal no puede llevar un
  código de ejecución;
- **variación entre perfiles**: un literal es constante; una emisión no.

Conteo real en el flujo descomprimido (`contar_agujas.py`, 214 perfiles):

| cadena | valor | veredicto |
|---|---|---|
| `FlashLoadMp4 : MP4 Load Completed` | 1 en **214/214** | literal `.rodata` |
| `FlashLoadDcf : DCF Flash Load Success.` | 1 en **214/214** | literal `.rodata` |
| `DiscLoadDcf : DCF Disc Load Success.` | 1 en **214/214** | literal `.rodata` |
| `Dcf Re-Load Success` | 1 en **214/214** | literal `.rodata` |
| `LoadAvi :  Load OK` (dos espacios) | 2 en **214/214** | literal `.rodata` (2 copias) |
| `MountCmd : Flash Mount Error` | 1 en 42, **2 en 170**, 3 en 2 | literal + **emisión** |
| `FlashLoadMp4 : CreateAndLoad Error` | 1 en 49, **2 en 163**, 3 en 2 | literal + **emisión** |
| `LoadSub : MP4 Load Error.` | 2 en 49, **3 en 163**, 4 en 2 | 2 literales + **emisión** |
| `ErrCd: 0xB0800001` | 0 en 49, **1 en 152**, 2 en 13 | solo **emisión** |
| `AviSeqPlay.cpp Error=` | 0 en 48, 3–7 en 166 | **emisión** |
| `PlayMovie` | 156 en **214/214** | literal/símbolo (ayuda `ex) MPR PLAY PlayMovie …`) |
| `PbStart` | 79 en **214/214** | símbolo de los ELF |

Vector de `LoadAvi :  Load OK` en RAM (los vecinos son sus propias ramas, no log):
`LoadAvi : Started | LoadAvi : Not Managed | LoadAvi : AVI Loaded... | Disk | LoadAvi :  Load OK | LoadAvi : Load NG`.
Igual para `FlashLoadMp4 : MP4 Load Completed`, pegado a `FlashLoadMp4 : CreateAndLoad Error`.
Es la **trampa** de esta tarea: un `grep "Load OK"` sobre el volcado «encuentra» el éxito en
todos los perfiles.

## 4. Cobertura de los marcadores pedidos (214 perfiles con log)

| marcador | perfiles | lectura |
|---|---|---|
| `AVIMMGR` | 184 | etiqueta presente; la cadena de carga real en 165 |
| `MP4IFO` | 165 | intento de IFO MP4 |
| `XAVCIFO` | 12 | intento de IFO XAVC |
| `MMGR_ACSR` | 165 | traductor de errores IFO |
| `AviSeqPlay` | 166 | **siempre** con `Error=[…]` |
| `SetLoadInfo` | 165 | parámetro de carga |
| `LoadSub` | 165 | capa de carga por tipo |
| `LoadExec` | 166 | ejecutor de la orden de carga |
| `CreateAndLoad` | 165 | composición + carga |
| `CheckMSId` | 170 | `MS IDs are not same!` |
| `CACHE` | 214 | solo el literal `[CACHE]ERROR(`; **no** aparece `BUFFER SIZE TOO SMALL` (era de la cámara real) |
| `StillCache` | — | solo literales (`(null)`), sin línea emitida útil |
| `Salvage` | 214 | **ruido**: nombres de símbolo/fichero de los ELF (`_ZN5MprIf7SalvageEmmm`), no ruta ejecutada |

## 5. Tabla por familia: perfil → error de video → ¿IFO cargado?

Las 14 firmas de `firmas.md` se agrupan así (la lista completa de perfiles, por firma, está
allí; el detalle por perfil, en `perfil-error-ifo.md`):

| # | n | qué IFO se intenta | error de video | AviSeqPlay | IFO cargado |
|---|---|---|---|---|---|
| 1 | 104 | MP4 | `mp4Ifo_General.cpp(1749) 0xB0800001` + `SetLoadInfo(523) 0xB0510007` + `CreateAndLoad(246) 0x31000006` | `ER_INTERNAL:12476` + `ER_AVI_FORMAT:10234` | **no** |
| 2 | 37 | MP4 | igual que 1 **más** capa BD: `0x31000003` (`GetStillContentsRemainCmd`), `0x31000007` (`ReserveEntryNumbersCmd`) | igual que 1 | **no** |
| 3 | 36 | ninguno | solo `MMgrBackup.cpp(74) 0x00000007` (monitor/BD, sin orden de carga) | — | **no** |
| 4 | 9 | MP4 | igual que 1 **más** `0x31000007` (reserva de entradas) | igual que 1 | **no** |
| 5 | 7 | ninguno | solo `0x31000007` (`ReserveEntryNumbersCmd`) | — | **no** |
| 6 | 7 | MP4 + XAVC | `xavcIfo_DbIf(0311)` / `DbSequencer(0579/0587)` `0xB0510010` + `xavcIfo_General(2086) 0xB0800001` + `MMgrXavcIfoAcsr(2480) 0xB0800005`; MP4 como en 1 | igual que 1 | **no** |
| 7 | 5 (+`uilive`) | ninguno | sin códigos MMGR | — | **no** |
| 8 | 2 | MP4 + XAVC + AVCHD | lo de 6 **más** `SetLoadInfo(523) 0xB0400005`, `MMgrAvcHdIfoAcsr(2608) 0xA0100003`, `MMgrIfoComposer(419) 0x46400001`, `0x3100000F` | **+ `Media:ER_OK:2594`** | **no** |
| 9 | 2 | MP4 | igual que 1 (sin `0x00000007`) | igual que 1 | **no** |
| 10 | 1 | ninguno | AVI sin IFO: `AviSeqPlay ER_INTERNAL`, `0x32000002`/`0x32400001` | `ER_INTERNAL:12476` | **no** |
| 11 | 1 | MP4 + XAVC | como 6 + `0xB0800005` | igual que 1 | **no** |
| 12 | 1 | MP4 + XAVC | como 6 + `0xB0800005` | igual que 1 | **no** |
| 13 | 1 | MP4 + XAVC + AVCHD | como 8 con `0x46500001` y `0x31000012` (`sony`) | igual que 1 | **no** |
| 14 | 1 | MP4 | `SetLoadInfo(523) 0xB0400005` + `0xB0800001` (`t45p`) | **+ `Media:ER_OK:2594`** | **no** |

Cadenas literales de referencia:

```
[AVIMMGR][MS1]MountCmd : Flash Mount Error
[MP4IFO] ### mp4Ifo faild at IF/mp4Ifo_General.cpp(1749) ErrCd: 0xB0800001
[AVIMMGR][MS1]LoadSub : MP4 Load Error.
[MMGR][MMGR_ACSR] ## ERROR(MMGR):0xB0800001 ## mmgrifoacsr/MMgrMp4IfoAcsr.cpp(2319) LoadSub()
[MMGR][MMGR_ACSR] ## ERROR(MMGR):0x31000006 ## mmgrifoacsr/MMgrMp4IfoAcsr.cpp(246) CreateAndLoad()
[AVIMMGR][MS1]FlashLoadMp4 : CreateAndLoad Error
[MMGR][AVI] ## ERROR(MMGR):0x31000006 ## avimmgr/AviMMgrCmd.cpp(13247) FlashLoadMp4()
[AVIMMGR][MS1]LoadSub : XAVC Load Error.
[MMGR][MMGR_ACSR] ## ERROR(MMGR):0xB0800005 ## mmgrifoacsr/MMgrXavcIfoAcsr.cpp(2480) LoadSub()
[AVIMMGR][MS1]LoadSub : AVCHD IFO Load() Error.
[MMGR][MMGR_ACSR] ## ERROR(HDAVCIFO):0xA0100003 ## mmgrifoacsr/MMgrAvcHdIfoAcsr.cpp(2608) LoadSub()
[AVI][PLAY]     sources/avi_if/AviSeqPlay.cpp Error=[ER_INTERNAL] Line:12476
[AVI][PLAY]     sources/avi_if/AviSeqPlay.cpp Error=[ER_AVI_FORMAT] Line:10234
```

Traducciones ya establecidas en el proyecto: `0x31000006`=`ER_CMD_CONFLICT`,
`0x31000007`=`ER_INTERNAL`, `0x31000003`=`ER_FAILED`, `0x31000012`=`ER_TIMEOUT`
(tabla `MMgrGlobal` en `0x8F6CA8`), `0x32400001`=`ER_FAILED` (mapper AVI), `0xB0510007` ⇐
`0x32200001` («la capa AVI dice que el formato no vale»), `0xB0800001` = genérico de mp4Ifo.
**Sin traducir** (no están en la tabla del proyecto): `0xB0510010`, `0xB0400005`,
`0xB0800005`, `0xA0100003` (este último ya aparece en la cámara real como fallo de la orden
HD-AVC), `0x46400001`, `0x46500001`, `0x3100000F`, `0x32000002`.

## 6. ¿Algún «Load OK» o alguna reproducción?

**No.** Ni un perfil. Lo único positivo emitido en 214 logs:

```
[AVI][MEDIA]    sources/avi_if/AviSeqMedia.cpp Error=[ER_OK] Line:2594
```

- Perfiles: **`arnes4`, `arnes6`, `t45p`** (3/214).
- Aparece en el flujo de log real: los vecinos son
  `…AviSeqCommon.cpp Error=[ER_MEDIUM] Line:18944` y `…AviSeqMedia.cpp Error=[ER_INTERNAL] Line:3109`,
  con `\r\n`.
- Los mismos 3 perfiles son los que **más lejos** llegan: `arnes4`/`arnes6` intentan los tres
  IFO (XAVC flash y disco, MP4, AVCHD) y `t45p` llega a `SetLoadInfo` especializado
  `0xB0400005`; aun así todos acaban en `CreateAndLoad 0x31000006`.
- **No es un `Load OK` ni una reproducción**: `AviSeqMedia` es la capa de medio, y el
  `ER_OK` no va seguido de `AviSeqPlay` sin error en ninguna de las tres.

Búsquedas negativas ejecutadas sobre los 214 logs (**0 resultados**): `Load OK` / `Load
Success` / `LoadSub : OK` / `CreateAndLoad OK` emitidos, `AviSeqPlay.cpp` sin `Error=`,
cualquier `## ERROR` con código `0x00000000`, y `BUFFER SIZE TOO SMALL`. (Las apariciones de
`PlayMovie` y `PbStart` existen pero son constantes en los 214 perfiles: literales y símbolos,
§3.)

## 7. Qué añade al estado vigente

- **Confirma y amplía** `docs/STATE.md` / `CURRENT.md` («ningún IFO se carga») de 1 perfil a
  **165 perfiles con intento** y 49 sin intento: no es un caso del `e2e17b`, es el
  comportamiento del arnés entero.
- **Nuevo en el arnés**: la capa XAVC sí se ejecuta en **12** perfiles
  (`xavcIfo_DbIf(0311)`, `DbSequencer(0579/0587)` con `0xB0510010`, `xavcIfo_General(2086)`
  con `0xB0800001`) y AVCHD en **3** (`0xA0100003`). Informes previos describían XAVC/AVCHD
  solo desde la cámara real.
- **Nuevo**: `SetLoadInfo` puede fallar con `0xB0400005` (3 perfiles) en vez de `0xB0510007`;
  es el código específico de `1749` que el informe `sub-mp4ifo-load` anticipaba.
- **Corrección de método**: `LoadAvi :  Load OK`, `FlashLoadMp4 : MP4 Load Completed` y
  `FlashLoadDcf : DCF Flash Load Success.` **no** son evidencia de carga; son `.rodata`.
  Cualquier informe futuro que los cite como éxito está equivocado.
- **`Salvage`** no aparece como ruta ejecutada: lo que hay son tablas de símbolos de los ELF.

## 8. Límites

- Instantánea, no serie temporal: cada `estado.zst` es un volcado; el orden dentro del fichero
  es orden de memoria, **no** cronológico.
- `uilive` sin log (§2); `davf2` en curso, fuera del censo.
- 2 perfiles muestran `MountCmd : Flash Mount Error` **dos veces emitido** (`e2e51`, `e2e152`;
  conteo 3 = 1 literal + 2 emisiones): hay reintento de montaje, no medido aquí.
- No se ha tocado la cámara ni el arnés, ni se ha modificado ningún `estado.zst`.

## Anexo · tabla por perfil (215)

Generada desde `index.tsv`. La versión con **código→sitio de impresión** (`mp4Ifo_General.cpp:1749`,
etc.), capas y códigos MMGR está en `reports/evidence/logs-arnes-todos/perfil-error-ifo.md`;
códigos por sitio, en `mapa-codigos.md`. Cero filas con IFO cargado.

| perfil | IFO | error de video | AviSeqPlay | IFO cargado |
|---|---|---|---|---|
| `arnes1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `arnes2` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `arnes3` | no | — (no llega al IFO) | — | **no** |
| `arnes4` | sí | `0xB0400005`, `0xB0510010`, `0xB0800001` | C:ER_MEDIUM<br>M:ER_FAILED<br>M:ER_INTERNAL<br>M:ER_OK<br>P:ER_INTERNAL<br>P:ER_MEDIUM | **no** |
| `arnes5` | no | — (no llega al IFO) | — | **no** |
| `arnes6` | sí | `0xB0400005`, `0xB0510010`, `0xB0800001` | C:ER_MEDIUM<br>M:ER_FAILED<br>M:ER_INTERNAL<br>M:ER_OK<br>P:ER_INTERNAL<br>P:ER_MEDIUM | **no** |
| `arnes7` | no | — (no llega al IFO) | — | **no** |
| `arnes9` | no | — (no llega al IFO) | — | **no** |
| `b392f` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `base5` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `base6` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `calma1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `calma3` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `calma4` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `calma5` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `calma6` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e01` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e02` | no | — (no llega al IFO) | — | **no** |
| `e2e03` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e04` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e05` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e06` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e07` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e09` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e10` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e100` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e101` | no | — (no llega al IFO) | — | **no** |
| `e2e102` | no | — (no llega al IFO) | — | **no** |
| `e2e103` | no | — (no llega al IFO) | — | **no** |
| `e2e104` | no | — (no llega al IFO) | — | **no** |
| `e2e105` | no | — (no llega al IFO) | — | **no** |
| `e2e106` | no | — (no llega al IFO) | — | **no** |
| `e2e107` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e108` | no | — (no llega al IFO) | — | **no** |
| `e2e109` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e11` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e110` | no | — (no llega al IFO) | — | **no** |
| `e2e111` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e112` | no | — (no llega al IFO) | — | **no** |
| `e2e113` | no | — (no llega al IFO) | — | **no** |
| `e2e114` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e115` | no | — (no llega al IFO) | — | **no** |
| `e2e116` | no | — (no llega al IFO) | — | **no** |
| `e2e117` | no | — (no llega al IFO) | — | **no** |
| `e2e119` | no | — (no llega al IFO) | — | **no** |
| `e2e12` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e121` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e122` | no | — (no llega al IFO) | — | **no** |
| `e2e123` | no | — (no llega al IFO) | — | **no** |
| `e2e124` | no | — (no llega al IFO) | — | **no** |
| `e2e125` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e126` | no | — (no llega al IFO) | — | **no** |
| `e2e127` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e128` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e13` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e130` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e131` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e14` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e140` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e141` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e15` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e150` | no | — (no llega al IFO) | — | **no** |
| `e2e152` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e153` | no | — (no llega al IFO) | — | **no** |
| `e2e154` | no | — (no llega al IFO) | — | **no** |
| `e2e16` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e166` | no | — (no llega al IFO) | — | **no** |
| `e2e167` | no | — (no llega al IFO) | — | **no** |
| `e2e168` | no | — (no llega al IFO) | — | **no** |
| `e2e169` | no | — (no llega al IFO) | — | **no** |
| `e2e17` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e170` | no | — (no llega al IFO) | — | **no** |
| `e2e172` | no | — (no llega al IFO) | — | **no** |
| `e2e173` | no | — (no llega al IFO) | — | **no** |
| `e2e174` | no | — (no llega al IFO) | — | **no** |
| `e2e177` | no | — (no llega al IFO) | — | **no** |
| `e2e178` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e179` | no | — (no llega al IFO) | — | **no** |
| `e2e17b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e17c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e17d` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e18` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e180` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e181` | no | — (no llega al IFO) | — | **no** |
| `e2e183` | no | — (no llega al IFO) | — | **no** |
| `e2e19` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e20` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e21` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e22` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e30` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e31` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e32` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e33` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e382` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e40` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e41` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e42` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e43` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e44` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e45` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e46` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e47` | no | — (no llega al IFO) | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_INTERNAL | **no** |
| `e2e49` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e50` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e51` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e52` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e52b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e57` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e58` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e60` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e61` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e62` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e63` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e64` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e65` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e66` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e67` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e68` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e69` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e70` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e71` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e72` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e73` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e74` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e75` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e76` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e77` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e78` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e79` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e80` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e81` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e82` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e83` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e84` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e85` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e86` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e87` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e88` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e89` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e90` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e92` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e93` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e94` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e95` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e96` | no | — (no llega al IFO) | — | **no** |
| `e2e97` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e98` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `e2e99` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `fin` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `fin0` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g102` | no | — (no llega al IFO) | — | **no** |
| `g102j` | no | — (no llega al IFO) | — | **no** |
| `g110a` | no | — (no llega al IFO) | — | **no** |
| `g111a` | no | — (no llega al IFO) | — | **no** |
| `g111b` | no | — (no llega al IFO) | — | **no** |
| `g111c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g111d` | no | — (no llega al IFO) | — | **no** |
| `g111e` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g2` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g56b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `g97` | no | — (no llega al IFO) | — | **no** |
| `hd120F` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `iso1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `iso393a` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `iso393f` | no | — (no llega al IFO) | — | **no** |
| `m1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `osd1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `pp7t` | no | — (no llega al IFO) | — | **no** |
| `prof` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `q1` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `r0` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `sony` | sí | `0xB0510007`, `0xB0510010`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t42a` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t42b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t42c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t42e` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t42f` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43a` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43d` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43f` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t43g` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44a` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44d` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44e` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44f` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44i` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44j` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44k` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44l` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44m` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44o` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44p` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44q` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t44s` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45a` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45b` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45c` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45d` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45e` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45g` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45i` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45j` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45k` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45l` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45m` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45n` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45o` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `t45p` | sí | `0xB0400005`, `0xB0800001` | C:ER_MEDIUM<br>M:ER_FAILED<br>M:ER_INTERNAL<br>M:ER_OK<br>P:ER_INTERNAL<br>P:ER_MEDIUM | **no** |
| `t45r` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
| `uilive` | — | sin `estado.zst` | — | **no** |
| `wl` | sí | `0xB0510007`, `0xB0800001` | C:ER_AVI_FORMAT<br>M:ER_FAILED<br>M:ER_INTERNAL<br>P:ER_AVI_FORMAT<br>P:ER_INTERNAL | **no** |
