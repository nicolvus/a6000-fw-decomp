# Tabla de secuencias de captura 0x43edccf8 (línea D, resuelta por Claude)

Exports: `analysis/ghidra/liro-seqtable-builder.json` (constructor 0x437ebed8), `liro-seqselect.json` (selector 0x437eabfc), `liro-seqrows.json` (cuerpos de filas 0, 8, 9, 10).
Análisis adicional estático: `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt`, `c2_handlers_0x43808100.txt`, `c2_handlers2_0x43808400.txt` (22-10-2026).

## Hechos

**VERIFICADO:** La tabla `GOT[0x44022934]=0x43edccf8` está a cero en la imagen (BSS); se rellena en arranque por el constructor estático `0x437ebed8`. Para cada fila de 20 B llama `0x43afb46a(fila, puntero_a_función)` (envoltorio de un delegado/`std::function` de 5 palabras; `0x43afb46a` sólo llama `0x437de944` y devuelve la fila). Otros bloques del mismo constructor inicializan las demás tablas (GOT 0x44021258, 0x44025f60 [la de exposición], 0x44021ed4, 0x440267e4, 0x44022458, 0x440265c4, 0x4401f7dc...).

**VERIFICADO:** El constructor `0x437ebed8` itera sobre una tabla de punteros a función (base obtenida vía `ldr.w r4, [pc, #0xdd8]` + `add r4, pc`) e instala cada puntero en la tabla de secuencias en offsets 0x00, 0x14, 0x28, 0x3c, 0x50, 0x64, 0x78, 0x8c, 0xa0, 0xb4, 0xc8, 0xdc, 0xf0, 0x104, 0x118, 0x12c, 0x140 (stride 0x14 = 20 B, 17 filas).

**VERIFICADO:** La tabla de punteros a función parece estar en la vtable `0x43fcd3a0` (entradas Thumb: 0x43807488, 0x438073bc, 0x43b1f2de, 0x43b1f2a2, 0x43b01572, 0x438070cc, 0x43b015b8, NULL, NULL, 0x43fffd94[dato], 0x43b0173a, 0x43b016f8, 0x43807c30, 0x43b1f2ea, 0x43b1f2e4, 0x43b1f27c, 0x43807f4c[dispatcher C2], ...). No se han confirmado las correspondencias exactas fila→función porque el literal de la vtable no tiene referencias directas.

**VERIFICADO (selector, liro-seqselect.json):** Captura normal de una imagen (`+0x4b70==0`, `+0x54a5==0`, `+0x1d8==0`, `+0x1e0∉{7,0x17}`) → fila 8; con `+0x1d8≠0` → 0xb; `+0x1e0==7` → 0xa/0xd; fila 9 si `(+0x70)-8<6 && +0x1d8==0`; ráfaga en curso → filas 8/12; `+0x4b70==7` → 15; otros `+0x4b70` → 14.

**VERIFICADO:** Cada fila es una **máquina de estados** `uint32 f(Image*)` con `switch(FUN_43afdf16())` (estado actual); p. ej. fila 8 (0x43b1be36): caso 0 = petición de captura/reintentos (`Capture Req Retry`, `Capture Cancel`, contadores `+0x74f/+0x750`), caso 2 = prepara parámetros (`0x43795a60`, `0x436d6118/61a4`, `0x4383fd6c`), caso 3 = `0x437ef8cc` y continúa. El mismo contrato `Image*→estado` que usa `0x43b04730` desde CaptureManager (C).

**INFERENCIA:** La fila es el **punto de sustitución** más limpio: una fila Silent sería otra función con el mismo prototipo (`Image*`→estado) y su propia máquina de estados que (1) hace la petición/cancelación estándar (caso 0), (2) toma el YC retenido en lugar de configurar sensor/CAIF (casos 1..), (3) codifica y llama Stage_Notify, (4) hace la contabilidad de fin (S2Handler, contadores) que hace el final de la fila normal.

**NO VERIFICADO:** Qué casos de la fila 8 emiten CAIF/SetMode/SACC (el cuerpo es largo; faltan casos 1, 4+). Dónde están las etapas Stage_* para fila 8 (probablemente en los casos posteriores: `0x438c828c`, `0x437ed568`...).

## Siguiente paso concreto (D-02/D-03)

Decompilar los casos restantes de 0x43b1be36 (y comparar con la fila 0 y 10) para etiquetar cada estado como: petición, configuración de sensor (0x438c828c / SetExposure), CAIF/Darwin, SACC, revelado/codificación (Stage_*Enc), Notify. Con eso sale la lista exacta de qué copiar y qué saltarse.

## Estados de la fila 8 (0x43b1be36, desensamblado parcial)

| Estado | Dir | Qué hace | Mecánico/sensor |
|--------|-----|----------|-----------------|
| 0 | 0x43b1be36 | Petición de captura: `Capture Req Retry exp_id`, reintentos (`+0x750<0x14`), `Capture Cancel`, espera `0x4372a73c(0x13)`; al final fija `FUN_436e9b08` (estado de modo por `+0x1e0`) | No (gestión de petición) |
| 1 | 0x437f22d4 | Inicio de captura: `0x43ae8220`, `0x43901a8c(4,..)`; espera `RawDevInit WAIT IMG PARAM` si `+0x4b70≠0`; `0x437f7ff0`, `0x43b00410`; **`0x436d6168`**, `0x43783764`, `0x436c2270`, `0x43ae9226(…0x9400…)` (relacionado con exposición/parámetros), `0x437f87ac` | **Probable**: configuración de sensor/exposición (0x436d61xx) — SetExposure/SetRead según C |
| 2 | 0x43b1d8a2 | Prepara parámetros: `0x43795a60`, `0x436d6118/0x436d61a4`, `0x4383fd6c`, `0x438d0420` | Configuración |
| 3 | 0x43afe942 | Notificación a Linux: mensaje tipo 4, id **0x1000**, secuencia `+0x4b64`, resultado `0xf000`, con 4 bytes de estado; `0x437feef8(msg,0x1c,0x20002)` | No (aviso «captura iniciada», difiere de Stage_Notify 0x1006) |
| 4 | 0x437f247c | `Stage_Raw.cpp`: `0x438bf1bc`, `0x43782f10`, `0x437dd400`, `0x437dd4dc`, `0x43afb276` (reserva/arranque de etapas RAW; error FATAL Stage_Raw.cpp:0x109) | **Sí**: arranque de adquisición |
| 5 | 0x43afe8a4 | `0x43afe8a4(+0x4b64, +0x4b54, idx)` por imagen (contabilidad de resultado por imagen) | Posterior |
| 6 | 0x437ed5bc | `NextSection`: `0x43afbf44`, `0x437e58c4`; mensaje `Stage_NextSection CapInit1st` (`Stage_Common.cpp`) | Avance de sección |

**Conclusión provisional (INFERENCIA):** La fila no contiene las etapas Stage_* directamente: cada estado invoca secciones (`0x437dd400` etc.). El cuerpo que emite 0x1006 (Stage_Notify 0x437efe78) está en una sección posterior. Una fila Silent debería reproducir 0/3/5/6 (petición, aviso 0x1000, contabilidad, avance) y sustituir 1/2/4 (sensor/exposición/RAW) por «tomar YC retenido y codificar».

**Hallazgo adicional:** Existe un aviso previo 0x1000 (inicio de captura, mismo destino 0x20002) que libObj debe esperar antes de 0x1006: una fila Silent debe seguir emitiéndolo (VERIFICADO el emisor; NO VERIFICADO el consumidor en libObj).

## Efecto en S51

Ninguno directo. La tabla de secuencias es el mecanismo de ejecución de captura, no el selector de mecanismo de obturación.

## Archivos relacionados

- `docs/capture/capture-stage-reuse.md` (este documento)
- `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt` (desensamblado del dispatcher C2)
- `analysis/rea-independent/out/c2_handlers_0x43808100.txt` (handlers del dispatcher)
- `analysis/rea-independent/out/c2_handlers2_0x43808400.txt` (handlers adicionales)
- `docs/capture/shutter-trigger-chain-0x3011.md` (cadena C2)
