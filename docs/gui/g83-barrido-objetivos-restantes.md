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

## Zebra: prueba en el arnés (17-11-2026, perfil `e2e50`, puerto 8770, VM cerrada con `/salir`)
Código: `scripts/gui/zebra_levels_patch.py` (1 byte por índice; test `tests/test_zebra_levels_patch.py`), overlay local `analysis/gui/g22/harness/pkg-e2e-zebra/cam/usr/lib/libObj.so` (solo ese fichero; índice 0 → centro 10 % en vez de 70 %). Para ver la petición se amplió el registro VDF del shim (`sonyshim.c`: vuelca 32 B del cuerpo; el `sonyshim.so` del arnés se recompiló, así que los perfiles existentes arrancan en frío una vez) y se arrancó con `SHIMEXTRA="WAITLOG=3000 WLALL=1"`.
- **MEDIDO:** menú Ajustes personalizados pág. 1 → «Cebra» (lista Desactivar, 70, 75, 80, 85, 90, …). Con el índice 0 guardado, la orden VDF `0x203` (cat 2, `SetZebra`) sale con cuerpo `01 01 20 0f 05` = onoff 1, U = `0x0f` (15 %), L = `0x05` (5 %), es decir centro 10 ± 5: **el byte parcheado llega tal cual al servicio VDF**; con la tabla de fábrica el mismo camino da 75/65.
- **NO_VERIFICADO:** (a) el cambio de nivel en caliente no produjo una 2.ª orden `0x203` durante el registro (3 cambios a 95/…); solo se vio la del arranque (restauración del ajuste), probable aplicación diferida al volver al visor; (b) que el VDF/hardware acepte U < 65 % y pinte la cebra (el arnés no emula el dibujado de cebra); (c) no se construyó CFW.
- **Conclusión:** cambiar los niveles del Zebra es un parche de 1 byte por opción, probado hasta la petición al VDF. «0–109 %» libre exige además un ajuste de menú propio (cueva que calcule el centro) y probar en cámara el límite inferior del VDF.

## AF Adjust, AF Range, Auto Framing: ¿llega la orden a av-cam? (17-11-2026, estático)
Método: `elf_string_xrefs.py` sobre `libObj.so` para localizar cada `Seq…) SEND MSG ERROR` y leer el `movw r0,#id` de su función; tabla de órdenes de av-cam (`0x43fff564`, entradas de 12 B `{id, manejador, flag}`, 170 entradas) y desensamblado Capstone de cada manejador.

| Función | Orden de libObj → av-cam | Manejador en av-cam 3.21 | Qué hace |
|---|---|---|---|
| AF Adjust (`SeqSetAfAdjust`) | `0x4083` | `0x43802c78` | guarda 3 bytes del cuerpo en el espejo de ajustes (campos `+0x33c`, `+0x340`, `+0x341` de `0x43edf684`), responde OK |
| AF Range, modo (`SeqSetAfRangeLimitMode`) | `0x40d9` | `0x43803224` | 1 byte → `+0x39c` |
| AF Range, límite de enfoque (`SeqSyncAfRangeLimitDrive`) | `0x40da` | `0x43803238` | 2 bytes → `+0x3a0/+0x3a1` y contador `+0x3a2` |
| Auto Framing (`SeqSetAutoFramingMode`) | `0x40b5` | `0x43802f64` | 1 byte → `+0x4fc` |

- **VERIFICADO (estático):** las cuatro órdenes tienen manejador en la tabla y solo copian el cuerpo al espejo de ajustes (el mismo mecanismo que Calidad JPEG `0x4036`, G75 T19). av-cam trae además `Stage_AutoFraming` (etapa de la tubería de imagen), así que el Auto Framing es más que un residuo.
- **NO_VERIFICADO:** quién **lee** esos campos. Un barrido PC-relativo (`ldr`+`add pc` a `0x43edf684` + desplazamiento) solo halla las escrituras de los manejadores y de la copia del arranque (`0x43804968`, `0x438049f0/4`, `0x43804b54`); ninguna lectura directa. Pueden leerse con otro registro base o copiando la estructura entera, así que **no se demuestra que el AF o la etapa de encuadre los use**.
- **Cómo se probaría:** en el arnés ya se ve la orden llegar a av-cam (como Extra Fine), pero la A6000 no tiene nodo de menú que la dispare; haría falta añadir el nodo (menú CFW, patrón de G76/G81) y, para el consumo real, el AF/captura de av-cam, bloqueados por E2E-10/E2E-15.
- **Anamorphic Desqueeze:** solo `PARAMID_SQUEEZE_ASPECT_*` en `ObjEffect` (`NOT FOUND: …` si el parámetro no existe); av-cam 3.21 no tiene cadenas ni manejador evidente → sin base hasta localizar el consumidor.

Pendiente actualizado: AF Adjust / AF Range / Auto Framing pasan a «orden aceptada por av-cam, consumidor sin localizar»; el siguiente paso útil es localizar los lectores de `0x43edf9c0` (AF Adjust) con REA/Unicorn cuando E2E-10 permita ejecutar el AF.
