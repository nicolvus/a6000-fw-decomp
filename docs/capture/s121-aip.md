# S121 — `[AIP]`: el Audio IP (37 trazas)

**Hito de la línea de ingeniería inversa general**. Sin efecto en S51 (A/B/C = NO): no hay
ningún mensaje de obturador. Informe: [analysis/s121_aip/aip.md](../../analysis/s121_aip/aip.md) · Datos: `aip.json` · Test: `tests/test_s121_aip.py`.

## Hallazgo central

`[AIP]` es el **Audio IP**: la capa de audio del firmware, con la jerarquía
`SaWrapper` → `SaDriverBase`/`SaDriverZoomNr`/`SaDriverLinearPhase` → `SaBackUpCtrl`/`SaSysvCtrl`
y un submódulo **LPS**. **37 trazas** en **16 funciones**, rango `0x43cdd844`–`0x43cdec50`
(offsets `0x79c844`–`0x79dc50`), **37 sitios PIC = 37 cadenas, 0 muertas**, en **6 sub-bloques**
RTTI: SaWrapper (8), SaDriverZoomNr (1), SetFader (1), SaBackUpCtrl (12), SaDriverBase (4), LPS (11).

`AIP = Audio IP` es **inferencia contextual**, no una expansión del firmware: el RTTI
`9AudioIpIf` (`0x43cdd82e`) y `9SaWrapper` (`0x43cdd839`) precede a la primera cadena; conviven `[AudioIp]`/`[AudioIP]`.

## Qué instrumenta

- **Callbacks** en tres capas (SA, LPS, driver): `Ack`/`Comp`/`Err`, con `errCode`+`errState`
  (SA) o `ErrCode`+`ErrStatus` (LPS). `0x43926d1c` despacha por `[r1,#1]==0x14` y `0x43926de8`
  por `[r1,#1]==0x13` (`uniqueId` leído en `0x43926e4c`).
- **Comandos**: `0x4392ac30` loguea `Cmd`/`Func` y `Zma`/`Ext`/`Mbx` (`[r4,#1]`, `[r4,#9]`,
  `[r4,#0xa/b/c]`) y llama a `0x43b5e7f6`; `0x4392acb4` loguea `Cmd`/`Func`/`Unq` y llama a
  `0x43b5e7ea`.
- **Backup**: tabla de **350 entradas de 12 B** `{id=0x10c0000+n, offset, size}` en
  **`0x43bd1964`**; `CreateBackUpLpsList` la recorre y `WriteShadow2BakcupArea` vuelca `0x10c` B
  (`mov.w r0,#0x10c` en `0x4392ab78`). `SetAudioNrType` publica el **bit 3** de `bkId=0x10e0000`.
- **LPS**: buzón y `sysv` con buffers `0x82`/`0x83`/`0x85` y longitudes `0x2c`/`0x28`/`0x14`;
  **`SetFader`** (`0x4355ae98`) convierte el float y divide por 100/20/otro según `[r0,#0x78]`.

## Relaciones

- **S81 (`[ADF]`) es el cliente**: `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`, tipos
  `AUDIO_IP_CONFIG_TYPE_*` (`0x43c264fa`–`0x43c2659e`) y comandos `Proc` `SetAip0/1`, `GetSa0/1`,
  `SetSa`, `SetFader`, `SetZoomNr`.
- **S108 (`[CAMERA_SA]`) NO es este módulo**: allí «SA» es el acelerador escalar
  (`Camera::SaFuncDrv`, `sa_func_*`); ninguna de las 37 trazas lo menciona. Coinciden en el rango
  de enlazado `0x43cdxxxx`, no en el código. **S107** no tiene relación directa.

## Método: 37, no 60

Regla estricta `add rX,pc` + `ldr` más cercano del mismo registro (hueco real 2–6 B). La *kill
analysis* v2 da **60 pares: 37 verdaderos y 23 falsos** (21 apuntan a otra cadena real; 2 a
dirección no-cadena: `0x43f1c4b4`, `0x43f1c5f4`). Falso positivo señero: `0x4355bcb2` →
`0x43ceb58b`, no `0x43cde863` (sitio real `0x4392ab04`). Escaneo propio: **95 599** `add rX,pc`,
**88 158** con `ldr`, **123** destinos en el bloque (37 `[AIP]` + 86 de otras familias).

## Diferencial

**A7S fw3.20: 37/37 textos idénticos** (0 exclusivos; orden distinto, el LPS va antes; offsets
`0x79305f`–`0x794165`) → el módulo no cambió, solo se movió.
**A6300 fw2.01: 63** = 37 + 26 (25 `[AIP][ZNR_EE]*` + `SetInstanceNumberExec Err %d`); ninguna
de la A6000 falta → añade la instrumentación del `SaDriverZoomNrEe`.

## Abierto / NO VERIFICADO

Desarrollo de `AIP`/`SA`/`LPS`/`ANR`/`ZNR`/`Zma`/`Ext`/`Mbx`; semántica de `errState`,
`ErrStatus`, `Cmd`, `Func`, `Unq`, `bkId`, `uniqueId`; formato exacto de la cola
`AudioIpCmdQueue`; contenido de las 350 entradas; si `SetFader` y `SetAudioNrType` usan el mismo
objeto; significado físico de los divisores 100/20.
