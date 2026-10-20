# Tabla de secuencias de captura 0x43edccf8 (línea D, resuelta por Claude)
Exports: `analysis/ghidra/liro-seqtable-builder.json` (constructor 0x437ebed8), `liro-seqselect.json` (selector 0x437eabfc), `liro-seqrows.json` (cuerpos de filas 0, 8, 9, 10).

## Hechos
- VERIFICADO: la tabla `GOT[0x44022934]=0x43edccf8` está a cero en la imagen; la rellena en arranque `0x437ebed8` (constructor estático): para cada fila de 20 B llama `0x43afb46a(fila, puntero_a_función)` (envoltorio de un delegado/`std::function` de 5 palabras; `0x43afb46a` sólo llama `0x437de944` y devuelve la fila). Otros bloques del mismo constructor inicializan las demás tablas (GOT 0x44021258, 0x44025f60 [la de exposición], 0x44021ed4, 0x440267e4, 0x44022458, 0x440265c4, 0x4401f7dc...).
- VERIFICADO: destinos (función Thumb, restar 1 del puntero) de las filas de esta tabla: fila0 0x43b1bc0c; f1 0x43b1bc24; f2 0x43b1bc70; f3 0x43b1bcc6; f4 0x43b1bd12; f5 0x43b1bd5e; f6 0x43b1bdb4; f7 0x43b1be00; **f8 0x43b1be36**; f9 0x43b1be98; f10 0x43b1bf04; f11 0x43b1bf66; f12 0x43b1bfc8; f13 0x43b1c034; f14 0x43b1c096; f15 0x43b1c0e2; f16 0x43b1c118.
- VERIFICADO (selector, `liro-seqselect.json`): captura normal de una imagen (`+0x4b70==0`, `+0x54a5==0`, `+0x1d8==0`, `+0x1e0∉{7,0x17}`) → fila 8; con `+0x1d8≠0` → 0xb; `+0x1e0==7` → 0xa/0xd; fila 9 si `(+0x70)-8<6 && +0x1d8==0`; ráfaga en curso → filas 8/12; `+0x4b70==7` → 15; otros `+0x4b70` → 14.
- VERIFICADO: cada fila es una **máquina de estados** `uint32 f(Image*)` con `switch(FUN_43afdf16())` (estado actual); p. ej. fila 8 (0x43b1be36): caso 0 = petición de captura/reintentos (`Capture Req Retry`, `Capture Cancel`, contadores `+0x74f/+0x750`), caso 2 = prepara parámetros (`0x43795a60`, `0x436d6118/61a4`, `0x4383fd6c`), caso 3 = `0x437ef8cc` y continúa. El mismo contrato `Image*→estado` que usa `0x43b04730` desde CaptureManager (C).
- INFERENCIA: la fila es el **punto de sustitución** más limpio: una fila Silent sería otra función con el mismo prototipo (`Image*`→estado) y su propia máquina de estados que (1) hace la petición/cancelación estándar (caso 0), (2) toma el YC retenido en lugar de configurar sensor/CAIF (casos 1..), (3) codifica y llama Stage_Notify, (4) hace la contabilidad de fin (S2Handler, contadores) que hace el final de la fila normal.
- NO VERIFICADO: qué casos de la fila 8 emiten CAIF/SetMode/SACC (el cuerpo es largo; faltan casos 1, 4+). Dónde están las etapas Stage_* para fila 8 (probablemente en los casos posteriores: `0x438c828c`, `0x437ed568`...).

## Siguiente paso concreto (D-02/D-03)
Decompilar los casos restantes de 0x43b1be36 (y comparar con la fila 0 y 10) para etiquetar cada estado como: petición, configuración de sensor (0x438c828c / SetExposure), CAIF/Darwin, SACC, revelado/codificación (Stage_*Enc), Notify. Con eso sale la lista exacta de qué copiar y qué saltarse.

## Estados de la fila 8 (0x43b1be36, 399 líneas de decompilado; `liro-seqrows.json`) — VERIFICADO por lectura, etiquetas semánticas INFERENCIA
| Estado | Qué hace | Mecánico/sensor |
|---|---|---|
| 0 | Petición de captura: `Capture Req Retry exp_id`, reintentos (`+0x750<0x14`), `Capture Cancel`, espera `0x4372a73c(0x13)`; al final fija `FUN_436e9b08` (estado de modo por `+0x1e0`) | No (gestión de petición) |
| 1 | Inicio de captura: `0x43ae8220`, `0x43901a8c(4,..)`; espera `RawDevInit WAIT IMG PARAM` si `+0x4b70≠0`; `0x437f7ff0`, `0x43b00410`; **`0x436d6168`**, `0x43783764`, `0x436c2270`, `0x43ae9226(…0x9400…)` (relacionado con exposición/parámetros), `0x437f87ac` | **Probable**: configuración de sensor/exposición (0x436d61xx) — SetExposure/SetRead según C |
| 2 | Prepara parámetros: `0x43795a60`, `0x436d6118/0x436d61a4`, `0x4383fd6c`, `0x438d0420` | Configuración |
| 3 | Notificación a Linux: mensaje tipo 4, id **0x1000**, secuencia `+0x4b64`, resultado `0xf000`, con 4 bytes de estado; `0x437feef8(msg,0x1c,0x20002)` | No (aviso «captura iniciada», difiere de Stage_Notify 0x1006) |
| 4 | `Stage_Raw.cpp`: `0x438bf1bc`, `0x43782f10`, `0x437dd400`, `0x437dd4dc`, `0x43afb276` (reserva/arranque de etapas RAW; error FATAL Stage_Raw.cpp:0x109) | **Sí**: arranque de adquisición |
| 5 | `0x43afe8a4(+0x4b64, +0x4b54, idx)` por imagen (contabilidad de resultado por imagen) | Posterior |
| 6 | `NextSection`: `0x43afbf44`, `0x437e58c4`; mensaje `Stage_NextSection CapInit1st` (`Stage_Common.cpp`) | Avance de sección |
- Conclusión provisional (INFERENCIA): la fila no contiene las etapas Stage_* directamente: cada estado invoca secciones (`0x437dd400` etc.). El cuerpo que emite 0x1006 (Stage_Notify 0x437efe78) está en una sección posterior. Una fila Silent debería reproducir 0/3/5/6 (petición, aviso 0x1000, contabilidad, avance) y sustituir 1/2/4 (sensor/exposición/RAW) por «tomar YC retenido y codificar».
- Hallazgo adicional: existe un aviso previo 0x1000 (inicio de captura, mismo destino 0x20002) que libObj debe esperar antes de 0x1006: una fila Silent debe seguir emitiéndolo (VERIFICADO el emisor; NO VERIFICADO el consumidor en libObj).
