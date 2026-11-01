# 13. Glosario

## Hardware y firmware

| Término | Significado |
|---|---|
| **A6000 / ILCE-6000** | La cámara. Modelo FDAT `0x41030035`, región 0 |
| **BIONZ (CXD90014)** | El procesador de imagen/SoC principal (ARM) que ejecuta Linux y la app de cámara |
| **Darwin** | Microcontrolador aparte que mueve las cortinillas mecánicas, rearma y controla la energía. Su firmware es `darwin_core.bin` |
| **Obturador mecánico / EFCS / electrónico** | EFCS = cortina delantera electrónica (la trasera sigue siendo mecánica). Electrónico = ninguna cortina mecánica; el sensor controla la exposición por filas |
| **IMX210 / IMX235** | Sensores de imagen. La lectura por filas dura ≈ 61 ms |
| **Bobinas P4D/P4E, motor P40/P41** | Salidas de Darwin que accionan los imanes de las cortinillas y el motor de rearme |
| **FDAT / `.dat`** | Formato de paquete de firmware que consume el actualizador; cifrado con `CXD90014` |
| **`nflasha0..3`** | Particiones de la NAND. `nflasha3` es la comprimida con `av-cam.bin` |
| **`av-cam.bin`** | Binario principal de la aplicación de cámara en BIONZ |
| **Loader2 / Loader3 / BootROM** | Cadena de arranque. Loader3 da el error −302 que se vio con el 3.25 (LED 3 lentos + 2 rápidos) |
| **TPZL / LDEC** | Formato de compresión de bloques de `nflasha3` y descompresor por hardware que lo lee |
| **NVRAM / backup** | Memoria con ajustes y calibración de cada cámara; se copia con el modo de servicio |
| **Modo de servicio / actualizador** | Modos USB de la cámara usados por `pmca` para volcar la NVRAM y flashear |

## Parches

| Término | Significado |
|---|---|
| **Tipo 0** | Parche de Darwin: la función `0x20c74` devuelve siempre 0, así que no se activan las bobinas P4D/P4E (firmware 3.22) |
| **B1a** | Parche de 2 bytes en `0x1fe6a`: Darwin no acciona el motor del obturador en captura ni en rearme (3.23 = tipo 0 + B1a) |
| **Capa 1 / Capa 2** | Capa 1 = firmware 3.23; capa 2 = parche en RAM (`ShutMode 0` + `r5`) para exposición uniforme |
| **`ShutMode`** | Registro de BIONZ (`0x836d6fb6`) que selecciona el modo de obturador; el parche lo fija a 0 |
| **`r5`** | Parámetro de exposición del sensor (`0x836d7000`); (4219 − `r5`) × 15,2 µs es la exposición |
| **Guardián** | Proceso `sh` en la cámara que revierte el parche de RAM si el PC no responde en 25 s |
| **3.25c** | 3.25 reconstruido con `nflasha3` en el formato exacto de Sony; experimental, nunca instalado |

## Etiquetas de los informes

| Etiqueta | Significado |
|---|---|
| **Sxx** | Sesión de análisis estático/offline |
| **Exx / E25-nn** | Fase de investigación con informe en `docs/capture/` (E25 = desactivación mecánica; E26 = incidente 3.25 y recuperación) |
| **Rnn / E26-Rnn** | Informes de recuperación de la cámara bloqueada (R36 = causa del fallo del 3.25; R45 = 3.25c) |
| **Tnnn** | Prueba física en cámara, anotada en `docs/capture/registro-pruebas-camara.md` (T040 = primer disparo silencioso con el 3.23) |
| **VERIFICADO / PARCIAL / NO_VERIFICADO** | Grado de evidencia de una conclusión |
| **REA / Ghidra** | Herramientas de ingeniería inversa: REA vía MCP y Ghidra histórico de solo lectura |
