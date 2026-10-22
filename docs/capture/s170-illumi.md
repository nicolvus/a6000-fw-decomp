# S170 — `[ILLUMI]`: el subsistema de iluminación (sensor de luz ambiente)

**34 trazas · 52 sitios (regla PIC estricta) · 25 funciones · 4 clases RTTI.**
Detalle y tabla función→traza: `analysis/s170_illumi/illumi.md` · datos: `analysis/s170_illumi/illumi.json`.

## Qué es

`[ILLUMI]` es la instrumentación del **subsistema de iluminación** (sensor de luz ambiente):
auto-ganancia del pre-amplificador (por GPIO), filtrado, corrección calibrada, cálculo de un
**nivel de luz** y publicación de ese nivel como **evento de cámara** con `key_code`.
`Illumi` **no se expande** en ninguna cadena; `RPR0400` tampoco (NO VERIFICADO).
Flujo: chip `IllumiRPR0400` (bus OSAL `0x520250`, reg `0x46`) → timer OSAL (`0x4e20`) →
`TareaPeriodica` (`0x435ad680`) → AD del servicio **LIRO ADC** (`0x720018`, msg `0xfff0` [S166])
→ media móvil de 4 muestras (`0x435ad574`) → `C_AD` (`0x435ad4dc`) → `JudgeGainChange`
(`0x435acb90`) → `CalcIllumiLevel` (`0x435acf00`) → `SendEvent` (`0x435acdd0`): 16 B
`{key_code, 0, Level, 0}` → cola de cámara `0x7a0020`.
## Las 34 trazas (vaddr; sitio y función en `illumi.md`)
```
0x43c40570 ADJ BLOCK ERROR    0x43c40588 GetRawData Success  0x43c405b9 GetIllumiData OK  0x43c405ed GetRawData Error   0x43c4061c ADJ COMMAND ERROR  0x43c40636 reg_sync_queue
0x43c4066c unreg_sync_queue   0x43c406e6 Parameter Err gain  0x43c4070d gain/gain_pre    0x43c40736 IllumiGain Gain/AD   0x43c40764 ERR try_valloc_msg   0x43c40798 <Send Event> key_code
0x43c407c6 ERR osal_snd_msg   0x43c407f3 IllumiLevel Level   0x43c4089d IllumiAd::%s:%d   0x43c408b5 ERR osal_set_timer  0x43c408e4 ERR osal_free_timer  0x43c40914 ERR osal_alloc_tmr
0x43c40945 AD MAXOVER ADwork  0x43c4096e C_AD. ADcor         0x43c40990 Gain Change OK    0x43c40a4a IllumiCam::%s:%d    0x43c40a63 ERR unreg_sync_cb   0x43c40aa0 ERR reg_sync_cb
0x43c40c10 IllumiRPR0400::    0x43c40c2d RPR0400 try_valloc  0x43c40c69 RPR0400 snd_sync   0x43c40ca3 RPR0400 free_msg   0x43c40cd9 RPR0400 hdr->err    0x43c40d05 RPR0400 ReadDevice
0x43c40d37 RPR0400 valloc_msg 0x43c40d6f RPR0400 snd_msg    0x43c40da4 RPR0400 Backup_rd  0x43c40ddc RPR0400 WriteDevice
```
Ninguna cadena muerta; 20 `__PRETTY_FUNCTION__` más (31 sitios) nombran las funciones.

## Clases (RTTI) y hallazgos con dirección
`IllumiDev` (abstracta, 5 ranuras → `__cxa_pure_virtual` @`0x439b4145`) → `IllumiAd` /
`IllumiCam` / `IllumiRPR0400` (herencia única). Typeinfo `0x43fdaa74`/`0x43fdaa7c`/
`0x43fdaa8c`/`0x43fdaa98`; vtables `0x43fbb5c0`/`0x43fbb5e0`/`0x43fbb600`/`0x43fbb620`.
- **Cola de eventos de cámara**: OSAL **`0x7a0020`**; 16 B `{u32 key_code, u32 0, u32 Level,
  u32 0}` (`0x435ace00`-`0x435ace0a`) — mismo formato que `[ACCY][BASE]:NotifyInput`
  (`0x43565846`-`0x43565854`). **`key_code`**: `0x17000001` (`0x435abe38`) y `0x17000002`
  (`0x435abe34`); únicas apariciones en la imagen → consumidor final NO VERIFICADO.
- **ADC LIRO (S166)**: `0x435ad474` llama al servicio `0x720018` con mensaje `0xfff0`
  (`get_d`); AD crudo → global `0x4401b9fc`. **Chip `RPR0400`**: bus `0x520250`; `GetAD` =
  `ReadDevice(0x39, 0x46, buf, 4)` (`0x435adffe`-`0x435ae006`); backup ids `0x133003c`/
  `0x133003d`. **Id de módulo de traza**: **`0x133`**; colas sync `0x13303ba`/`0x13303be`.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ILLUMI]` | **34** | 0 | 0 |
| apariciones de `Illumi` | **45** | 4 | 4 |
| clases RTTI `Illumi*` / `__PRETTY_FUNCTION__` | 4 / **20** | 4 / 0 | 4 / 0 |
| `ReadDevice(0x39,0x46)` | `0x435adffe` | `0x435afee0` | `0x435b0cd0` |

→ El **subsistema es común a las tres fw**; lo **propio de la A6000 fw3.21 es la instrumentación**.

## Obturador

**Negativo acotado**: 0 coincidencias de `shutter`/`curtain`/`expos`/`iso`/`apert`/`frame`/
`capture`/`sensor`/`compens` en las 34 trazas. El `gain` es la **ganancia del sensor de luz**
(GPIO), no ISO; el único evento publicado es el **nivel de luz**. **S51 A=NO/B=NO/C=NO.**

## Verificación
**52/52** pares PIC verificados a mano (literal del pool, `destino = literal + (add+4)`, sin
reutilización del registro). Scripts: `analysis/s170_illumi/` · Tests: `tests/test_s170_illumi.py`.
