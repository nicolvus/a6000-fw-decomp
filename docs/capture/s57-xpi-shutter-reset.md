# S57-E — CIS0_SHT_RST / XPI del IMX210 (20-10-2026)

**Resultado:** la conexión eléctrica se reconstruye a nivel de esquema (línea discreta directa a la flex del sensor, junto a reset y sincronías), pero **no se localiza ningún controlador, escritura, interrupción ni cadena en el firmware** que la maneje. Función de XPI: **NO VERIFICADO**. Evidencia: `docs/references/sony-ilce-6000-level3-sm.txt`, `…-7s-…`; barrido de bytes de todo `firmware/`; matriz S57-27/28; prueba `MatrixConsistency` (referencias) — el barrido de cadenas se documenta aquí.

## E.1 Conexión (INFERENCIA: texto extraído de PDF, sin netlist)
| Tramo | Evidencia (línea del texto del esquema A6000) |
|---|---|
| BIONZ → red `CIS0_SHT_RST` | l.488: «XPI \| CIS0_SHT_RST \| 47 \| 36»; l.3436 «T8 \| CIS_SHT_RST» y l.4445-4446 «CIS0_SHT_RST … C9 C20» (ball de IC6000; la asignación exacta de la ball queda ambigua en el texto) |
| Conector CN0400 (51P, flex del sensor) | l.2518-2540: pin 11 `XCLR`=`CIS0_IMG_RST`, 10 `SDO`=`CIS0_SI`, 9 `SCK`=`CIS0_SCK`, 8 `SDI`, 7 `XCE`=`CIS0_XCS`, **6 `XPI`=`CIS0_SHT_RST`**, 5 `VREF_ON`, 3 `XHS`=`CIS0_HD`, 2 `XVS`=`CIS0_VD`; `IC5400` es un regulador de 4,5 V (MM3416A45URE), no un adaptador de nivel |
| Sensor | l.1631/1694: pin `F6 XPI` (y `XCE` R12/R13, `XCLR` E8) |
El esquema A7S repite la misma red (l.485, 4412 de `sony-ilce-7s-level3-sm.txt`: `CIS0_SHT_RST … XPI`). Por tanto **la línea existe en ambas cámaras**, también en A7S con Silent: su presencia no distingue el Silent.
No demostrado: polaridad (el prefijo `X` de otras señales del sensor indica activo-bajo, pero `XPI` es un nombre propio del sensor), resistencias de reposo, función alternativa del pin ni tensión de reposo.

## E.2 Controlador en BIONZ (búsqueda)
* **0 cadenas** `SHT_RST`/`SHTRST`/`SHT_RESET`/`sht_rst` (sin distinguir mayúsculas) en todo `firmware/` (ripgrep binario sobre ambos modelos, módulos de kernel y Darwin).
* S55/S56: los pares GPIO leídos por la tarea CA (bancos `0xf2910000…`) no incluyen una salida con ese nombre; SENS_B sin escritores; la cadena SetExposure→Execute→P2S no escribe GPIO (solo `gpio_set(15,5)` en el constructor).
* Las bases MMIO `0xf2403000–0xf2406040` y `0xf2a1xxxx` parecen reloj/ADC (S56-E). Un bloque VD/DFE dedicado no se identificó. No se usó `trace_native_values` sobre literales `0xf24xxxxx` (siguiente paso estático, de coste alto).
**Frontera:** si el pin lo maneja un temporizador de sensor integrado en el SoC (como el generador de VD), su registro no tiene nombre en `av-cam.bin`; la ausencia de escritor visible **no prueba** que no exista control.

## E.3/E.4 Relación con ShutMode, EFCS y SSB
Sin controlador no se puede establecer cuándo se activa, si depende de ShutMode, drive_mode, EFCS o tiempo de exposición. Con la evidencia disponible, SSB (bit 3 de ID1, canal serie) y XPI (línea discreta) son **canales distintos** sin enlace demostrado: posibilidades abiertas (independientes, coordinados, mecanismos de reset diferentes o sin relación). No se elige hipótesis.

## E.5 Siguiente experimento (requiere autorización específica)
Analizador lógico en `CIS0_SHT_RST`/XPI (pin 6 de CN0400), `CIS0_VD`, `CIS0_SCK/SI/XCS` y `CA_1ST_CURTAIN_START` durante: foto mecánica 1/1000 s y 1/4 s, EFCS y vídeo; decodificar el serie con `analysis/s56/p2s_emu.frames` y buscar `CC→C4` en ID1 y flancos de XPI respecto de VD. Pasivo, no destructivo.
