# S57-C — Origen y mapeo de svd / shd / spl (20-10-2026)

**Resultado:** el mapeo valor→registro es **exacto y verificado**; svd está **atado a un contador de pasos del host y a una fórmula** (`n·svr_num−1`), lo que lo caracteriza como contador de periodos de VD (INFERENCIA); shd y spl son enteros de 14 y 12 bit sin fórmula recuperada. El **productor numérico** (pipeline AE) no se localizó: la frontera queda en el rastreo del banco `0x43eb35d0`. Ningún valor se escribe al *terminar* la exposición. Pruebas: `tests/test_s57_imx210_exposure.py::{TimingMapping}`; script `analysis/s57/c_timing.py`; matriz S57-15…22.

## 1. Argumento y registros (VERIFICADO, 400/400 vectores aleatorios con dos rellenos de memoria)
`SetExposure(O, arg)` (`0x436d6f6c`; log `0x436d723a` «`SetExps: [svd][shd][spl][shut]`») lee `svd=u16[arg+4]`, `shd=u16[arg+0]`, `spl=u16[arg+6]`, `ShutMode=u8[arg+9]`:

| Parámetro | Ancho | Registros (byte bajo / alto) | Bits altos preservados |
|---|---|---|---|
| svd | 12 | ID3 = svd[7:0]; ID4[3:0] = svd[11:8] | ID4[7:4] |
| shd | 14 | ID5 = shd[7:0]; ID6[5:0] = shd[13:8] | ID6[7:6] |
| spl | 12 | ID7 = spl[7:0]; ID8[3:0] = spl[11:8] | ID8[7:4] |

Los bits superiores de entrada (svd,spl [15:12]; shd [15:14]) se **descartan**. Espejo 0x144–0x149 de los mismos bytes **solo si** `[G(0x4f24)+0x7f]≠0xFF`. ShutMode 2 carga además `ID0x100←arg+8` (en el log de la captura se llama «sint») y `ID0x101←arg+0x14`; con ShutMode≠2 conservan su valor previo. `ShutMode` («gs» en el log de CAMERA_MAIN_SYNC) y ID1: ver [informe A](s57-imx210-register1-semantics.md).

## 2. Cadena de producción (hasta la frontera)
```
pipeline AE por frame  0x437b5b14 (etapas 0x20…0x36: 0x43844e80, 0x43859ae0/b34, 0x4384b268, 0x4385b234, 0x43b08648)
  → struct S = 0x43eb35d0 (0x148 B, BSS: cero en la imagen; memset en 0x437b56b0)
  → 0x43843a44 prepara 4 bancos de 16 B (S+4+16·banco) desde otra estructura (0x43eb05d8+0x224)
  → 0x43b0893c copia la fila del banco S[0] a S+0xC4..0xD0 ; 0x43849fb8 construye el bloque de exposición (16 B + copia)
  → bloque en [obj+0x24] (obj = 0x4378f9b4())  ──► 0x4381106c (StrtExps): copia 16 B, verifica svd, llama 0x43ae935a (SSB + SetExposure)
  → cap+0x640+0x0c (=cap+0x64c) ──► 0x438c828c / 0x438c86b0: SetExposure(arg=cap+0x64c), SetRead, SSB, Execute
```
(REA `procedure_pseudo_code` de `0x43b0893c`, `0x43849fb8`, `0x437b5b14`, `0x4381106c`: `analysis/s57/rea-out/`.) Las lecturas de S+0x48,+0x70,+0x7a… en `0x43838b02…` son serializadores de mensajes a Darwin (empaquetan valores big-endian de la misma estructura): **Darwin recibe los mismos parámetros**.

**Frontera (NO VERIFICADO):** no se localizó la instrucción que escribe las filas de banco (`S+0xC4…0xD8`): sólo 3 funciones usan el slot GOT de S (`0x437b5614` memset, `0x437b59b8`, `0x437b617e`); el resto del pipeline recibe punteros como argumento. Es el eslabón exacto para seguir (REA `trace_native_values` sobre `0x43844e80`/`0x4384b268`).

## 3. Relación demostrada: svd y el contador del host
* `cap+0x650` **es** svd (`arg=cap+0x64c`, `arg+4`). Los manejadores `0x43b1e7f2/0x43b1e854` (llamados desde 8 estados `0x43b1ae2a…0x43b1b22e`) hacen: si svd==0 → mensaje de fin (4,2) sin pasos; si no, `StartExposure`, `[cap+0x4b9c]++` y devuelven «continuar» mientras el contador ≠ svd. `StartExposure` (`0x438c828c`) **solo programa registros en el paso 0**; los demás pasos ejecutan `Execute(0)` (reinicio del P2S sin datos) (VERIFICADO).
* `0x4381106c` valida: `n = [obj+0x1f8]` (o 1 si `[obj+0x1fc]==9`); `svd_esperado = (VdNum≤1) ? n·svr_num : n/VdNum`, menos 1; si el bit 15 queda activo → «`Imager param error shut:%d, svr_num:%d, VdNum:%d`»; si difiere del svd del plan → «`Imager svd error`» y solo lo sustituye con el indicador de depuración `[G+0x1d] bit2`. `svr_num=u8[X8+0x14e]`, `VdNum=u16[X8+0xcc]`, `n=[X8+0x3c]`, tipo `=[X8+0x44]` (X8=`[obj+8]`, copiados en `0x4380ca5c`). `[G+0x1d] bit0` fuerza `shd=9, spl=0`.
**INFERENCIA media-alta:** svd cuenta periodos de VD (o de lectura vertical: «svr»/«VdNum» en los mensajes) y no una duración en unidades de tiempo. shd/spl: sin fórmula; quedan como enteros que acompañan.

## 4. Dependencias (C.2/C.4): lo que sí y no se puede decir
| Posible dependencia | Evidencia | Estado |
|---|---|---|
| Velocidad de obturación (shut) | `n=[X8+0x3c]` entra en la fórmula de svd | PARCIAL (el *origen* de n no se rastreó) |
| drive_mode / resolución | `VdNum`/`svr_num` salen del bloque de modo `X8`; SetExposure no ramifica por drive_mode (solo `0x0b` en la ruta de ajuste) | INFERENCIA |
| Tipo de captura | tipo==9 ⇒ n=1 y ShutMode=1 | VERIFICADO |
| Frecuencia/duración de línea | no hay constante de reloj en SetExposure | NO VERIFICADO |
| EFCS/foto-vídeo | sin rama en SetExposure; el flujo (`0x438c86b0`) escribe ShutMode 1 | NO VERIFICADO |
Los seis tiempos sugeridos (1/4000…1 s) **no se pueden derivar**: el productor AE no se recuperó. Las 400 emulaciones usan entradas sintéticas (etiquetadas) y prueban solo la transformación; **no** representan velocidades reales.

## 5. Pregunta crítica (C.5)
¿Alguno de estos parámetros es una operación de fin de integración? **No hay evidencia de ello**: los tres se escriben una vez al inicio (paso 0) y el firmware no reescribe ningún registro de 3–8 al terminar (`ExposureTimerEnd!` sin SetExposure). Son compatibles con temporización de integración/lectura programada **al inicio**, de modo que el sensor podría cerrar la integración por sí mismo (hipótesis H57-9). Para distinguir hacen falta: (a) el datasheet (significado y unidades de svd/shd/spl), o (b) una traza pasiva CIS0 + XPI + VD de dos exposiciones con distinto `svd`/`shd` que muestre si cambia el instante del fin (por ejemplo, en 1/1000 s frente a 1/4 s, y con/ sin primera cortina electrónica).

## 6. Límites
Productor AE no recuperado; `X8` (bloque de modo) no rastreado hasta su origen; `cap+0x4b9c` como «paso de VD» es inferencia (no se midió la cadencia de los estados `0x43b1ae2a…`). La emulación no modela el sensor.
