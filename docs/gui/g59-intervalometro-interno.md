# G59 — Intervalómetro interno: `ModelStillIntervalRec` es un modelo de ajustes/estado, no un motor de disparo; sin parche (15-11-2026)

Estático sobre `libObj.so` 3.21 (`analysis/camera-extract/usr/lib/libObj.so`, Thumb, VA = offset en el primer LOAD, datos = VA − 0x8000) y `av-cam.bin`. Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`. Resultado: **parcial/documentado** (rama 3 del brief); no se escribió parche ni ajustes de menú porque no hay a qué enganchar la secuencia.

## 1. Qué es `ModelStillIntervalRec` (VERIFICADO en bytes)
- `ModelStillIntervalRecToInstance` (`0x66cb61`): `new(0xe0)` + ctor `0x66cb28`; vtable en `0x10140a0+8`, métodos propios solo en los slots 12 (`0x66cfb8`, inicialización), 13 (`0x66cd96`), 17 (`0x66d6b0`) y 18 (`0x66bb8e`); el resto hereda la base.
- La inicialización `0x66cfb8` crea **cuatro datos ligados al Backup/NVRAM**, ids **`0x1070ab3` (H), `0x1070ab4` (M), `0x1070ab6` (S), `0x1070ab5` (MS)** (cadenas `INTERVAL_H/M/S/MS` en `0xd49148…`), cada uno con su tupla de claves de modelo (`0x101/0x105/0x109/0x10d`, mín./máx. en `0x102/0x103…0x10e/0x10f` servidos por `0x66bb8e`) y dos campos más en `+0xa8/+0xac` con claves `0x111/0x112` (rango del número de tomas, según el reparto de `0x66bb8e`). Es decir: **el intervalo (h/min/s/ms) y el número de disparos son datos del modelo**, persistidos en Backup, que una UI podría editar.
- Sus acciones (cadenas `IntRecMd` `0x66bec0`, `iRStsChg`, `ActivCmp`, `DeactCmp`, `testStop`, `testCnt`) son **trazas/relés de estado**: guardan el modo (`+0xa8`) y empaquetan `H<<24 | M<<16 | MS/S` para la capa superior. Los manejadores compartidos con `ModelStillRec` (`pvt_ActionObjectRemainEvt` `0x66dab8`, `BracketCountEvt`, `PanoramaSweepEndEvt`) son de contabilidad (restantes), no de disparo.
- **No contiene ninguna petición de captura**: en `0x66b800–0x66dd00` no hay constantes `0x75xx` (`StillCaptureStart` = `0x7506`), solo claves de modelo (`0x1xx`, `0x400x`, `0x3a30`, `0x9001/3`).

## 2. Quién lo arranca y quién cuenta
- `CameraAgent` (`ObjCameraAgent`, `libObj` `0xaf5…–0xafb…`) solo **notifica a las apps**: `sendIntervalRecStartCmp` (`0xafb638`), `…StopCmp` (`0xafb584`), `…CountEvt` (`0xafb2cc`), `…ModeCmp`, `…StopEvt`; sin ruta que dispare.
- El despachador `0xaf86c0` (CP) trata `0x8078` → `0xaf84f8` (fin de arranque: StartCmp(0) + CountEvt(0)) y `0x8079` → parada. Los ids `0x8078/0x8079` los fabrica `appif.cpp` (`0xafd00c`, casos en `0xafd11e/0xafd13e`), la **interfaz de aplicaciones**: el arranque/parada nace en la API de apps (como `bracketAF` en g57 §6), no en un flujo propio de la UI. El contador (`0xaf6474`, `CountEvt` con contador incrementado y error «SYSCNT») es relé de eventos.
- `av-cam` 3.21: **sin cadena ni id `0x8077–0x8079`** (escaneo Thumb con movw/mov.w); `CAPTURE_INTERVAL`/`SetIntervalTimer` (`0x437df338`, s105) es el espaciado mínimo entre capturas de la capa de captura, no un temporizador de timelapse.
- Candidatos de motor no resueltos: el bucle disparo→espera→disparo vive, si existe, en el lado de las apps (la app Time-lapse repetía `StillCaptureStart`) o en una pieza no localizada entre `0x8078` y `ObjCamera`.

## 3. Menú
`string_english.uxc`: solo «Interval» (`0xe16d`) y los intervalos de reproducción/ahorro de energía; **no hay** «Shoot Interval», «Number of Shots» ni nodos de intervalo en `CautionConfig.so`/`viewUnified2.so`. No hay un tipo de modelo de lista ya existente al que cambiar la lista (patrón G39/G58 no aplicable).

## 4. Veredicto y diseño mínimo que falta
**El modelo no dispara solo**: es el almacén de ajustes (h/m/s/ms, número) y de estado que usa la API de apps. Hace falta un bucle propio, enganchado al fin de captura:
1. Ajustes CFW («Intervalo» Off/1/2/5/10/30/60 s; «N.º disparos» 10/30/60/100/300/999) con el circuito de [g56](g56-ajustes-propios-cfw.md) (ids libres `0x1070214…`).
2. Gancho de **fin de captura** (pieza común con `FOCUSSHIFT-HOOK` y `LIVECOMP-F1`): cuenta de tomas, temporizador (`osal_set_timer`, ya usado por `SetIntervalTimer`) y nuevo disparo. Candidato nuevo a verificar: `pvt_ActionObjectRemainEvt` (`libObj` `0x66dab8`, bytes `f0b50d4687b03949002602af79443246`; evento `MSGID_STILL_REMAIN_EVT`, ejecutado tras cada toma guardada) en el lado `libObj`, o el fin de `CaptureStart` en `av-cam`; ninguno está probado por Unicorn.

## 5. Límites
No se localizó el emisor de `0x8077…` ni el efecto real de arrancar el modelo; no se probó nada en el arnés (no hay ajuste ni consumidor). El intervalo en Backup `0x1070ab3…6` no se miró en NVRAM real.
