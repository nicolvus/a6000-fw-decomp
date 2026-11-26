# FILM-PB-1 — Verificación de la NVRAM frente a PAL/NTSC

Fecha: 27-11-2026. Pregunta del usuario: ¿hay algún cambio en las NVRAM volcadas respecto
a PAL/NTSC?

**Respuesta: no. En los 64 volcados (32 parejas `backup_flash`/`backup_mem`, del 20-10-2026
al 22-11-2026) no hay un solo cambio en ningún valor con forma de sistema de TV ('N'/'P'), y
el elemento de menú NTSC/PAL de la A6000 no tiene identificador de respaldo en la NVRAM.**

## 1. Cómo se ha leído

La NVRAM es un `BackupFile` de 852 647 B con **16 102 propiedades** `(id, attr, datos)`; se
parsea con el módulo del propio proyecto (`references/pmca/pmca/backup.py`):

```python
from pmca.backup import BackupFile
props = {i: bytes(pr.data) for i, pr in BackupFile(open(f, 'rb')).listProperties()}
```

## 2. Candidatos con forma de sistema de TV

Barrido de las 16 102 propiedades: solo cuatro contienen un byte 'N' o 'P' en un campo propio.

| id | valor | ¿cambia en algún volcado? | ¿el id aparece como literal en las libs? |
|---|---|---|---|
| `0x115002b` | `4E` ('N') | **no, idéntico en los 64 volcados** | no |
| `0x10706b1` | `50 01` ('P' + flag) | **no, idéntico** | no |
| `0x3c0412` | `50` ('P') | **no, idéntico** | **sí**: `libmprctrl` 0x130B4 y 0x1312C (junto a `0x3c0411`), `libmpr` 0x96B530, `libObj` 0x94E020/0xED0328/0xF16830 |
| `0x69007c` | `50` ('P') | **no, idéntico** | no |

Vecinos, para descartar que sean campos de una estructura mayor:
`0x115002a=00`, `0x115002c=00`; `0x3c0411=00`, `0x3c0413=00`;
`0x10706b0=f000`, `0x10706b2=c001` (formato `{valor, 0x01}`, típico de ajuste de usuario del
subsistema `0x107`).

## 3. Comparación global primer volcado ↔ último volcado

`20261020-first` ↔ `20261122-lutsd385b`: mismas 16 102 propiedades (ninguna añadida ni
borrada) y **176 con valor distinto**, todas de las sesiones de pruebas:

| subsistema | propiedades cambiadas |
|---|---:|
| `0x58` | 81 |
| `0x107` | 49 |
| `0x59` | 13 |
| `0x3` | 7 |
| `0x3c` | 6 |
| resto | 20 |

De esas 176, **ninguna** es un selector de 1 byte con valor 'N'/'P'. Los cambios de ≤2 B son
valores de ajustes (p. ej. `0x51000f 0b→01`, `0x580000 01→00`, `0x3c032d e20b→c20f`).

## 4. El elemento de menú NTSC/PAL no tiene respaldo en NVRAM

`analysis/gui/process-bindings-a6000.json` (mapa elemento de menú ↔ id de respaldo de la
A6000) contiene la entrada `0x85: {"elemento": "CustomNTSCPALSelection", "modelos": [],
"respaldos": []}`: el elemento **existe** en las tablas de la interfaz pero **no está ligado a
este modelo ni a ningún id de NVRAM**. Concuerda con lo que el usuario ve (no aparece en el
menú) y con que el firmware traiga el módulo de interfaz (`viewNtscPalSEL_D.uxc`) sin exponerlo.

## 5. Qué significa para la causa

- **No hubo cambio de PAL a NTSC en la NVRAM**: si el sistema de TV se hubiera alterado por un
  reseteo, aquí no queda rastro; y el ajuste no tiene registro persistente propio.
- Por tanto el sistema de TV de esta cámara es **fijo por firmware/región**: si es PAL, los
  clips de 30p **nunca** se han podido reproducir en ella (ni grabar con ella), y el arreglo es
  cambiar la cadencia de los clips; si es NTSC, la guarda de cadencia no es la causa y hay que
  ir a la otra rama (miniatura) o al motor.

## 6. Límites

- **No hay ningún volcado posterior al CFW 3.93** (instalado el 24-11): el último es del
  22-11-2026. Nada de esto mide el estado actual de la cámara.
- No se ha identificado con certeza cuál de los cuatro ids es el sistema de TV: el único que
  usa el código (`0x3c0412`) vale 'P', y el más «de ajuste de usuario» (`0x10706b1`) también
  vale 'P'; `0x115002b` vale 'N'. Esa ambigüedad **no se puede resolver sin la cámara** (leyendo
  la propiedad con el ajuste cambiado) y es el dato que decide si la hipótesis de cadencia vive.
- El ensayo del clip de 25p (§6 del [informe de causa](film-pb-1-causa-sistema-tv-20261127.md))
  sigue siendo el discriminante práctico y no necesita NVRAM.
