# S137 — `[CTRLCORE]`: el núcleo de control del códec (`*CtrlCore`)

**Línea de ingeniería inversa general** (no afecta al obturador electrónico: S51 sigue con
A/B/C = NO — ninguna de las 55 cadenas menciona obturador, disparo, cortinilla, lectura del
sensor ni tiempos de exposición).

Informe: [analysis/s137_ctrlcore/ctrlcore.md](../../analysis/s137_ctrlcore/ctrlcore.md) ·
Datos: `analysis/s137_ctrlcore/ctrlcore.json` · Test: `tests/test_s137_ctrlcore.py`.
## Hallazgo central
`[CTRLCORE]` **no es un módulo de primer nivel**: es una **sub-etiqueta de segundo nivel**
(como `[APL]` dentro de `[CAMERA_SA]`, S119). Siempre va detrás de un contenedor y designa
la clase **núcleo de control (`*CtrlCore`)** de ese contenedor:
| prefijo | cadenas | clase |
|---|---|---|
| `[CDIAG][CTRLCORE]` (incl. `[ERR]`) | **51** | `CdCtrlCore` |
| `[MCSENS][CTRLCORE]` | **1** | `McSensCtrlCore` |
| `[AMSENS][CTRLCORE]` | **3** | `AmSensCtrlCore` |

- **55 cadenas**, `0x43c3b82d`–`0x43cdb492`; **4 ficheros fuente**: `cdCtrlCore.cpp`
  `0x43c3b86c`, `mcSensCtrlCore.cpp` `0x43c73689`, `amSensCtrlCore.cpp` `0x43cdb45a`,
  `mcAvCtrlCore.cpp` `0x43c454e8` (éste último sin ninguna cadena `[CTRLCORE]`).
- **74 sitios PIC** (**regla estricta**: `ldr rX,[pc,#imm]` del mismo registro → literal
  `W` → `destino = W + (add + 4)`); **74/74 verificados de forma independiente** con
  `verify_sites.py`, **74/74 textos** coincidentes.
- **16 funciones emisoras** con prólogo Thumb `push {…,lr}`; **55/55 cadenas referenciadas**
  y **0 punteros absolutos de 4 B** (todo el acceso es PIC).
## Qué se ha reconstruido (verificado contra bytes)
1. **Capas**: los tres despachadores están en `cdCtrlIf.cpp` (`0x43c3b1a8`), no en el
   `*CtrlCore`; `CdCtrlCore` **ejecuta** y **compone respuestas**.

| despachador | vaddr | guarda `line` | contenido |
|---|---|---|---|
| `CdCtrlIf::ExecCmd` | `0x435a1424` | `0xc2` (`0x435a142a`) | 2→`SetMemArea` `0x435a2200`, 3→`RelMemArea` `0x435a20b0`, `0x11`→`RunCodec` `0x435a1f18` |
| `CdCtrlIf::ExecSensCmd` | `0x435a15e8` | `0x41` (`0x435a15f4`) | 1→`SetDiagMode`, 2/3/`0x11`→trama 12 B `0x435a157c`, `0x12`→`CmpData`, `0x21`/`0x22`→`SetData`, `0x41`→`ConfirmDoneCodec`, `0xd1`→`DbgDiagAvc` |
| `CdCtrlIf::ExecSensComp` | `0x435a17e8` | `0x12d` (`0x435a17f4`) | 11 ids con su nombre `SENS_*` + `SetComp*` |

2. **Firmas embebidas** (no inferencia por vecindad): la guarda pasa a `0x435ab880` el
   fichero, la **firma de la propia función** y el `line`; p. ej. `0x43c3b7a9`
   `CDIAGER CdCtrlCore::SetCompNormal(OsalResponsePacket*, __uint32_t)` con `line 0x2bd`,
   `0x43c3c19c` `SetCompDeleteData` con `line 0x34f`, `0x43c3c162` `SetData`.
3. **Trama de respuesta** `SetCompNormal` (`0x435a1b64`): tipo `8`, `+0x01`=1, `+0x04`=0,
   `+0x06`=u16 0, `+0x08`=u32 0, `+0x0c`=u32 1, `+0x10`=estado en `[obj+0x1480+0x18]`;
   variantes tipo `2` (`0x435a1bac`), tipo `8` (`0x435a1be0`), tipo `0x20` (`0x435a1c14`).
4. **Grafo**: `0x435a121c` es un switch por id de mensaje (`b.w 0x435a1424` en `0x435a1242`),
   invocado una vez por paquete en el bucle `0x435a136e`–`0x435a1388` (`bl` en `0x435a1382`).
5. **Singleton** `0x435a1b18`: bandera `0x43e4a768`, objeto `0x43e4a76c`, ctor `0x435a1a68`,
   registro `0x439b4244` (tabla `0x4401eee4` + `{0x6c4c, 0x65e8}`), 18 llamadores `bl`.
6. **McSens/AmSens**: `0x43629c4c` (guarda `line 0x13`, llamada desde `0x43620044`);
   `0x43920bcc` (`line 0x26`), `0x43920c2c` (size `0x5000`) y `0x43920c9c` (size `0x800`),
   con `adr` de `0x43a3a9b4(handle, 0x12, 0)`.
## Diferencial
- **A7S fw3.20: 55/55 cadenas idénticas** (0 exclusivas en ambos sentidos).
- **A6300 fw2.01: 90** = 55 comunes + **14 `[CDIAG][CTRLCORE] … 4K`** + **21
  `[CDEXT][CTRLCORE]`** (`StartVideoCodecDiag`, `LoopbackControl`, memorias
  `MEM AROOC/ARROC`). `CdExtCtrlCore` **no existe** en la A6000.
## Abierto / NO VERIFICADO
Nombre de `0x439b4244` · nombres de `0x435a1bac` y `0x435a1be0` (sólo guarda corta) ·
sitio exacto de la entrada indirecta a `ExecSensCmd`/`ExecSensComp` (sin `bl` ni puntero de
4 B) · significado funcional de los ids `0x32`/`0x33` (`0x43a48d16`/`0x43a48cf2`). Scripts:
`analysis/s137_ctrlcore/` (`scan_ctrlcore.py`, `verify_sites.py`).
