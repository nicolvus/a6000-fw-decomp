# G81 — Timecode / User Bit: presente de fábrica sin menú; `ObjEffect` lo inhibe (PARCIAL)

Fecha 16-11-2026 (G75 Tarea 29). Estático sobre `libObj`/`libmpr`/av-cam 3.21, más una prueba en el arnés (perfil `e2e46`, Sony 3.21 sin overlay, cerrado con `/salir`). Prueba: `tests/test_g81_tcub.py`.

## 1. Piezas de fábrica (VERIFICADO por bytes)
| Capa | Pieza |
|---|---|
| UI (`libObj` `0x6005dc…0x600b04`, en la zona del modelo de vídeo, junto a S&Q y proxy) | Seis emisores `ObjMsg(0x3900, …)` a Effect (objeto 9): `0x3016` {`0x1047`}, `0x3017` {`0x1048`}, `0x3018` {`0x1049`}, `0x3019` {`0x1013`}, **`0x301a` {`0x104a…0x104d`}** y **`0x301b` {`0x104e…0x1051`}**. Por los comandos de `ObjEffect` (`CMD_ID_TCUB_TC_FORMAT/TC_MAKE/TC_PRESET/TC_RUN/UB_TIME_REC`), 0x301a/0x301b son el preset de TC y de UB (4 campos: hh/mm/ss/ff), INFERENCIA. |
| `ObjEffect` (`0xbc4bc8`, «Check Tcub») | Antes de aceptar la orden consulta `MWF::InhInfo::GetInhInfo(FeatureId 0x34b)`, y también `0x36c` para `0x3018`. Si está inhibida, la rechaza («tcub(msgId) is Inhbited»). |
| av-cam | Motor TC/UB del codificador (`McTcubIf`, `McTcubMcmd`, `NotifyEncodeTcubInfo` por fotograma, `[ENCOUCSTAT]YC TCUB DATA`), VDF `SetTimeCode` / `UpdateTimeCodePin` y decodificación TCUB |
| `libmpr` | Escritura y lectura de TC/UB (`b_timeCodeEnable`, `GetLastTimeCode`, `LastTCUBInfo`, «There is no Last User Bit») |
| Menú | Ningún nodo TC/UB en `CautionConfig.so` |

## 2. Prueba en el arnés (MEDIDO)
Con el comando `Z 9:3900:301a 104a=1,104b=2,104c=3,104d=4`, que es el comando `Z` del shim ampliado para elegir objeto y clase, el mensaje llega a `ObjEffect`: registra «IssueCommandAsync cateId 0x3900, msgId 0x301a» y «Check Tcub». Lo rechaza: **«tcub(msgId:0x301a) is Inhbited»**. La cámara estaba en modo foto (P), sin grabar.

## 3. Veredicto
**PARCIAL.** El TC/UB de Sony (preset, modo de avance, formato DF/NDF, UB) está en el firmware, de la UI al fichero, pero el factor de inhibición `0x34b` lo bloquea. No se sabe si ese factor es una prohibición por modelo (lo que lo haría inservible sin parchear `InhInfo`) o por estado (fuera de vídeo). Falta además el menú.

## 4. Pendientes (TCUB-F1…F3)
1. TCUB-F1: averiguar quién pone el factor `0x34b` (tabla de `InhInfo`/`ModelInhWrapper`) y si cambia en vídeo y en «REC» (el arnés ya entra en «REC» con G79). Repetir `Z 9:3900:301a` en esos estados.
2. TCUB-F2: si es por estado, ajustes CFW (TC preset y modo de avance) y una cueva que los envíe al entrar en vídeo; si es por modelo, un parche mínimo del factor, probado en Unicorn y en el arnés.
3. TCUB-F3: comprobar el TC en el XML y el MP4 de un clip grabado (depende de E2E-15).
