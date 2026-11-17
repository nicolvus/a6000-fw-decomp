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

## 5. TCUB-F1: origen de la inhibición (G75 T30, 16-11-2026, MEDIDO)
- **No es un factor de inhibición.** Con la traza de `libMWF+0x1e264` (`SubMakeInhFactorMsg`, `r5` = factores activos por palabra), la consulta `GetInhInfo(0x34b)` de «Check Tcub» da 0 factores.
- **Es un interruptor de configuración de fábrica.** `ObjEffect` (`0xbc4c36`) lee `AvbbcBackup::Read1Byte(0x3c03d9)` y solo acepta TC/UB si vale 1. **Vale 0 en todos los volcados reales de Backup** (28 fechas) y en el `bk.tbl` del arnés.
- Las 11 lecturas de `0x3c03d9` en `libObj` y la de `libmprctrl` son todas de TC/UB: inicio y fin de grabación con TCUB, conexión del pin TCUB al VEF, `InfDecoder`, `InfMovieEditor` y «PARAMID_TC_FRAMERATE». Es el interruptor de toda la función.
- **Arnés** (perfil `e2e45`, overlay `pkg-e2e-xavcs`):
  - Con el byte de fábrica, la propia UI manda en vídeo las seis órdenes TC/UB (`0x3016`, `0x3017`, `0x3018`, `0x3019`, `0x301b` y la `0x3015` de S&Q, vistas tras Fn en «REC»), y `ObjEffect` las rechaza todas.
  - Con `BKSET=3c03d9=1`, `Z 9:3900:301a` ya no se rechaza («Check Tcub» sin «is Inhbited»).
  - No se ve todavía qué hace después: la ruta pasa por el pin TCUB/VEF y el servicio VDF, que el shim contesta él mismo, y la grabación no avanza (E2E-15).
  - Incidente: con la grabación atascada en «REC», pulsar Fn tras inyectar provocó un SIGSEGV en `THREAD_INFRA0` (`libObj+0x6a8401`). Con Fn en «REC» atascado el arnés no es fiable.
- **Consecuencia para S&Q:** la orden Effect `0x3015` que manda la cueva de VFR-F2 también pasa por «Check Tcub», así que con el byte de fábrica Effect la rechaza. Las órdenes a `ObjCamera` (`0x75e4`) y al grabador (`0x1005`) no dependen de ese byte.
- **Vía para un CFW (sin código):** poner `0x3c03d9 = 1`, por ejemplo con un ajuste «Timecode» de la carpeta CFW cuyo id de Backup sea directamente `0x3c03d9`. NO_VERIFICADO:
  - que el descriptor «solo respaldo» escriba en ese espacio de ids (`0x3cxxxx`, `AvbbcBackup`);
  - que el resto del flujo TC/UB (pin TCUB, VEF, codificador, `libmpr`) funcione en el hardware de la A6000. Es código común, pero con el interruptor de fábrica a 0 la A6000 nunca lo ha ejecutado.

## 6. TCUB-F2: ajuste «Timecode» en la carpeta CFW (G75 T31, 16-11-2026, MEDIDO)
- **Ajuste:** `cfw_ajustes` añade «Timecode» (Off/On, pid `0xF4`), cuyo id de Backup es directamente el interruptor de Sony **`0x3c03d9`** (`ID_SONY`). Sin código nuevo: la UI escribe el índice de la opción (0/1), que es el valor que espera `ObjEffect`. El id tiene atributo `0x0` en el Backup real (escribible, como los ids CFW `0x1070208`/`0x1070210`; `0x1070087` tiene `0x68`), y en todos los volcados vale 0, que es el Off.
- **Arnés** (perfil `e2e47`, overlay `pkg-e2e-tc` = menú CFW + parche de XAVC S de G79, sin `BKSET`):
  - «Timecode: Off» aparece en la p. 2 de la carpeta CFW (`docs/gui/img/g75/t31-carpeta-cfw-timecode.png`).
  - Con Off, `Z 9:3900:301a` se rechaza («is Inhbited»).
  - On escribe `0x3c03d9` = 1 (`nvram.json`); el mismo preset de TC pasa «Check Tcub» sin rechazo (`t31-timecode-on.png`).
  - Volver a Off escribe 0 y el rechazo vuelve.
- **Pendiente (TCUB-F3):**
  - preset de TC, modo de avance y DF/NDF desde el menú: la UI de Sony ya manda sus órdenes; con el interruptor a 1 usan sus valores de fábrica, que no se han medido;
  - comprobar el TC en un clip grabado (depende de E2E-15);
  - el riesgo en cámara de §5 (la cadena TCUB nunca se ha ejecutado en la A6000).
