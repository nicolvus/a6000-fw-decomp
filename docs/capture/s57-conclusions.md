# S57 — Conclusiones (Claude, 20-10-2026)

**Pregunta final:** ¿qué registros, bits y señales controlan la duración y finalización de la integración electrónica del IMX210 y hay evidencia para una segunda cortina electrónica a resolución completa? **Duración:** candidatos identificados con mapeo exacto — `svd` (ID3, ID4[3:0], 12 bit), `shd` (ID5, ID6[5:0], 14 bit), `spl` (ID7, ID8[3:0], 12 bit) y el selector `ShutMode` en ID1 bits 2/4/6/7 (+0x100/0x101 en ShutMode 2); `svd` está ligado a un contador de pasos del host y a una fórmula `n·svr_num−1`. **Finalización: NO VERIFICADO.** Eslabón exacto que falta: la **semántica y unidades** de esos registros (y de la línea XPI) para saber si el sensor cierra la integración por temporización programada al inicio; el firmware **no escribe ningún registro al terminar la exposición**. **S51 se mantiene (A=NO, B=NO, C=NO).**

Informes: [A ID1](s57-imx210-register1-semantics.md) · [B SSB](s57-ssb-pulse-analysis.md) · [C temporización](s57-exposure-timing-origin.md) · [D IMX235](s57-imx235-silent-register-diff.md) · [E XPI](s57-xpi-shutter-reset.md) · [F P2S/VD](s57-p2s-vd-synchronization.md). Matriz `analysis/s57-evidence-matrix.json` (33 entradas, 10 hipótesis); pruebas `tests/test_s57_imx210_exposure.py` (34/34); scripts `analysis/s57/`. REA: sesión `GHIDRA_MAXMEM=6G`, 1 instancia, cerrada; `analysis/s57/rea-out/`.

## Qué se sabía desde S56 (no repetido)
Cadena SetExposure → sombra → Execute → P2S(DFE0), formato de trama `81|len|81|AH AL|datos`, lista de 119, ShutMode 0–4 → ID1 `40/C4/94/D4/C0` (solo el 2 carga 0x100/0x101), pulso SSB = bit 3 enviado dos veces, nombres `svd/shd/spl`, A7S con el mismo P2S y formato de registro distinto. S57 usa esos hechos y los reemplaza por semántica.

## Descubrimientos nuevos (VERIFICADO salvo indicación)
1. **ID1 es un registro de función combinada.** Escritores completos: carga de columna de SetMode (bits 0 y 2), SetExposure (bits 2,7,4,6 según ShutMode), `0x436d7c08` (bit 3) y `0x436d7cf0` (borra 2,7,4 en la ruta de ajuste). `B` (índice 2) es copia de `A`; el bit 2 final depende solo de ShutMode. Rejilla 13 modos × 5 ShutMode × SSB: 130 casos, idéntica con memoria `0x00`/`0xA5`.
2. **SSB acompaña a toda actualización de exposición** (SetExposure → SSB → Execute en captura, StartExposure, ExposureTimerStart(first), helper de CAMERA_MAIN_SYNC); no hay SSB en `Execute(0)` ni en `ExposureTimerEnd!`. A7S genera su pulso dentro de SetExposure cuando el parámetro `arg+2 > 0x1000`.
3. **Mapeo exacto de `svd/shd/spl`** (400/400 vectores) y espejo `0x144–0x149` condicionado a `[G+0x7f]≠0xFF`.
4. **`svd` está atado al secuenciador del host**: `cap+0x650`=svd; el contador `cap+0x4b9c` avanza hasta svd y solo el paso 0 programa registros; `0x4381106c` valida `svd = n·svr_num−1` (o `n/VdNum−1`). INFERENCIA: svd cuenta periodos de VD.
5. **El ShutMode real en captura** solo toma 0 (arranque/StartExposure) y 1 (`ExposureTimerStart`, o `tipo==9` en CAMERA_MAIN_SYNC); no se hallaron constantes 2, 3, 4.
6. **Banderas +0x277/0x278/0x279/0x27c** las fija el manejador de **AdjustCmd 0x91** (`0x43a12d9c`): ruta de ajuste/servicio, no fotografía normal.
7. **IMX235 Silent:** `0x4e/0x4f` son variantes mínimas de `0x4c/0x4d` (1–4 registros de diferencia; dir `0x000C` 0x10 vs 0x20) y distan 33–35 de 35 registros del modo foto `0x0b`; no hay comando extra de «terminar integración» en la matriz.
8. **XPI:** conexión reconstruida a CN0400 pin 6 → pin F6 del sensor (también en A7S); 0 cadenas `SHT_RST` en todo el firmware; controlador no localizado.
9. **P2S SyncMode:** valor escrito en `0xfc088800`; solo el modo 2 usa banderas OSAL y disparo `1,0,1`. `Execute` envía 119 (síncrono) → espera → 8 inmediatos.
10. El fin de exposición del host (`ExposureTimerEnd!`) envía mensajes a Darwin y **no** toca el sensor.

## Hipótesis (estado, confianza)
| H | Estado | Confianza | Resumen |
|---|---|---|---|
| H57-1 ID1 control de estado/mecanismo | **PARCIAL** | alta (estructura) / baja (eléctrica) | mezcla modo de lectura + ShutMode + strobe |
| H57-2 SSB = transición de configuración/sincronización | **INFERENCIA** | media | strobe de aplicación de exposición; no fin |
| H57-3 svd/shd/spl = temporización | **INFERENCIA** | media-alta | contador de VD + fórmula verificados para svd |
| H57-4 un registro 3–8 fija el fin | **NO VERIFICADO** | — | no se reescriben al final |
| H57-5 Silent IMX235 con configuración ausente en IMX210 | **PARCIAL** | media | modos de lectura dedicados; sin comando extra |
| H57-6 XPI en reset/temporización | **NO VERIFICADO** | — | línea existe; sin controlador |
| H57-7 SyncMode 2 sincroniza con vídeo/sensor | **PARCIAL** | media | handshake verificado; VD inferido |
| H57-8 mecanismos parciales reutilizables | **NO VERIFICADO** | — | piezas existen, ninguna demostrada como fin |
| H57-9 depende de hardware aún no identificado | **HIPÓTESIS** | baja | compatible |
| H57-10 ruta deducible de lo recuperado | **NO VERIFICADO** | — | no se deduce |
**Descartado / refutado en esta fase:** «SSB = finalización de exposición» (se emite al inicio, ausente en el fin) y «el host reescribe svd/shd/spl al terminar» (no ocurre en `0x438c86b0`); lectura «ShutMode 4 escrito en captura» no reproducida.

## Revisión de S51 (G)
* ¿Se conoce dirección de un registro de integración? Candidatos (ID3–8) sin unidades. ¿Efecto eléctrico? No. ¿Inicio? Sí en sentido de **programación** (paso 0 + SSB + Execute); no como instante eléctrico. ¿Finalización? **No hay operación identificada.** ¿Sincronización? SyncMode 2 + planificador `VD_Pre` (parcial). ¿Configuración de resolución completa compatible? El modo `0x0b` (24 MP, 4176 líneas, ≈66,8 ms/cuadro) existe; su uso sin obturador mecánico no está demostrado.
* Clasificación: **(1) capacidad demostrada:** escritura de registros por P2S con mapeo exacto (offline), strobe SSB, ShutMode. **(2) compatible, no probada:** que el sensor cierre la integración por temporización programada. **(3) ruta refutada:** SSB como fin; reescritura de 3–8 al final. **(4) imposibilidad física:** ninguna demostrada. **(5) insuficiente:** unidades de svd/shd/spl, ID1 eléctrico, XPI, Darwin.
* Por las reglas de S51 (registro de temporización o pulso no demuestran un obturador electrónico) **no se cambia la decisión**: «A: NO, B: NO, C: NO». Retomar con datasheet IMX210 o traza pasiva.

## Impacto en la viabilidad de Silent Shooting
Sin cambio: no hay parche justificable. Lo nuevo es un diagnóstico más preciso: el Silent A7S es **selección de modo de lectura + política de clase/CAIF** (S52/S53), y en A6000 faltan esos tres eslabones; el sensor IMX210 no tiene modos dedicados (13 modos). Si existiera un camino, pasaría por (a) un modo de lectura foto con temporización programada (hay piezas: svd/shd/spl, ShutMode) y (b) lógica en LIRO/Darwin sin cortinas, que no está en el firmware.

## Límites
Sin datasheet ni hardware; emulación Unicorn con stubs (documentados en `analysis/s57/emu57.py`), memoria rellena y no el sensor; A7S SetExposure/formateador no emulados; productor AE de las filas de banco no localizado; `AdjustCmd` categorías no resueltas; REA no reconoce `SetExposure`/`0x43a12d9c` (Thumb) y comparte motor con Ghidra — hechos críticos verificados con Capstone y bytes; mypy no instalado (scripts sin tipos; `ruff --select F,E9` limpio).

## Siguiente experimento de mayor valor
1. **Estático (sin autorización):** `trace_native_values` sobre `0x43844e80`/`0x4384b268`/`0x4385b234` para localizar quién escribe `S+0xC4…0xD8` (`0x43eb35d0`) a partir de la velocidad de obturación; con tres velocidades derivar svd/shd/spl y sus unidades frente al periodo de 4176 líneas (66,8 ms).
2. **Pasivo (requiere autorización específica):** analizador lógico en `CIS0_SCK/SI/XCS`, `CIS0_VD` y XPI (CN0400 pin 6) con foto mecánica 1/1000 s y 1/4 s y EFCS; decodificar con `analysis/s56/p2s_emu.frames`; buscar `CC→C4` de ID1, flancos de XPI y el instante del fin respecto de VD.
