# G83 — Barrido estático de los objetivos restantes (17-11-2026)

Método: `strings` y referencias PC-relativas (`scripts/elf_string_xrefs.py`) sobre `analysis/camera-extract/usr/lib/*.so` de fw 3.21. **Solo estático: nada probado en el arnés, nada implementado.** «Latente» = el código existe en `libObj.so` pero no hay menú o no se ha demostrado que av-cam lo soporte.

| Objetivo | Hallazgo (VERIFICADO salvo nota) | Estado |
|---|---|---|
| Zebra 0–109 % | El renderer ya manda `SetZebra(sel,onoff,gray,U,L)` al VDF. `libObj` `0x2b9944…`: el índice de menú 0–7 pasa por una tabla (`tbb` en `0x2b994c`) a un centro 70, 75, 80, 85, 90, 95, 100, 104 %; **L = centro−5, U = centro+5**, así que el tope de fábrica ya es 109 % (104+5). Bajar de 70 % = cambiar el `movs r3,#imm` de cada entrada (1 byte), pero solo sustituye opciones existentes; un rango libre exige un ajuste CFW propio que calcule el centro (cueva). NO_VERIFICADO: que el VDF acepte U/L < 65 y cómo se dibuja en el arnés | Viable, sin hacer; probar primero en arnés (¿pinta la cebra?) |
| AF Micro Adjustment | Latente: `PARAMID_AF_ADJUST_MODE/USER`, `ActionSetAfAdjust`, `MSGID_SET_AF_ADJUST_CMD` en `libObj` (de la plataforma compartida con α99/α7). Sin menú en la A6000. NO_VERIFICADO: soporte en av-cam/lente | Candidato: añadir nodo de menú que escriba el parámetro |
| AF Range Control | Latente: `PARAMID_AF_RANGE_LIMIT_MODE/DRIVE_NEAR/FAR`, `ActionExeAfRangeLimitDrive`; el CautionConfig trae botones «AfRange» pero son de otros modelos | Idem |
| Auto Object Framing | Latente: `PARAMID_AUTO_FRAMING_MODE/_W/_H`, `SeqSetAutoFramingMode` (cadenas de ZV-E1/α7 IV en la plataforma común) | Probable que av-cam 3.21 no lo tenga; verificar |
| Anamorphic Desqueeze | Latente en ObjEffect: `PARAMID_SQUEEZE_ASPECT_RATIO_X/Y_LIST` (lista de factores de desanamorfizado) | Candidato: comprobar si el renderer lo aplica al visor/reproducción |
| Eye AF en tiempo real | Solo `PARAMID_EYE_START_AF` (Eye-AF por botón, inicio manual); sin seguimiento continuo | Parcial de fábrica; el «tiempo real» necesita detector en av-cam (no localizado) |
| Seguimiento / sensibilidad AF | `SetMovieAfSensibility` / `SetStillAfSensibility` existen (sensibilidad en vídeo/foto); sin menú de «casos» | Candidato: exponer sensibilidad |
| Movie Silent Control, Synchro Scan, Voice Memo, Waveform, Vectorscope, Gamma Display Assist, Sports Finder, Carga USB encendida, FTP | **Ninguna cadena** en `usr/lib` ni `usr/bin` | Sin base en el firmware; irían por código nuevo (Waveform/Vectorscope: sin acceso a los píxeles del visor) |

## Siguiente paso recomendado
1. Zebra: probar en el arnés que cambiar la tabla mueve U/L (y que se ve en pantalla).
2. AF Adjust / AF Range / Anamorphic: ver si el valor llega a `ObjCamera`/av-cam en el arnés al escribir el parámetro (como en G75 con Extra Fine).
3. Todo lo demás: descartar o dejar con «sin base» hasta que haya motivo.
