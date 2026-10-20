# S56 — Conclusiones (Claude, 20-10-2026)

Pregunta final: ¿existe una ruta demostrable para finalizar electrónicamente la integración del IMX210 a resolución completa? **No demostrada; tampoco refutada.** Eslabón que falta: la **semántica de los registros del IMX210** (ID1 bits 2/3/4/6/7, IDs 3–8 `svd/shd/spl`, `0x100/0x101`) y de la línea `CIS0_SHT_RST→XPI` en lectura completa; no hay datasheet ni traza.
Informes: [A transporte](s56-imx210-register-transport.md) · [B CISIF/DFE](s56-cisif-dfe-controller.md) · [C integración](s56-imx210-electronic-shutter.md) · [D IMX235](s56-imx235-imx210-differential.md) · [E SENS_B](s56-sens-b-mmio-analysis.md) · [F sincronía](s56-exposure-synchronization.md). Matriz `analysis/s56-evidence-matrix.json`; tests `tests/test_s56_imx210_transport.py` (26/26 ejecutados).

## Hallazgos nuevos (VERIFICADOS por bytes + emulación Unicorn del código real)
1. `SetExposure` solo escribe registros sombra; el envío lo hace `Execute` (vtable+0x38) con tres listas (119 sync, 8 inmediatos, 4 sleep).
2. Los «IDs» (ID1/100/101…) **son direcciones de registro de 16 bits** (mapa `0..0x155`); backend = formateador P2S → trama `81|len|81|AH AL|datos`, RAM de datos del bloque P2S(DFE0) `0xfc088340…`, disparo 1,0,1 en `0xfc088808`. Transformación ID→dirección→byte probada (ida y vuelta, 119/119).
3. CISIF es el **receptor** (12 carriles + códigos de sincronía), no el bus de configuración.
4. `SetExposure` reparte `svd/shd/spl` en IDs 3–8 (+ espejo 0x144–0x149); `ShutMode` 0–4 fija ID1 = 40/C4/94/D4/C0, y solo el 2 carga 0x100/0x101.
5. Pulso **SSB**: ID1 bit3 enviado 2 veces (1 y 0) en el mismo lote; lo piden captura, prelight y StrtExps.
6. La cadena de registros no lee GPIO/P4C. A7S usa el mismo hardware P2S con formato de registro distinto (byte de dispositivo) y sin ShutMode 2.

## Heredado (no repetido)
S55: pares GPIO por BK4 (`0x436bcef4`), SENS_B sin lector GPIO; S51–S54: Darwin/CAIF, tipo 0 ≡ Silent en exposición, ExposureEnd solo mensaje.

## Rutas descartadas
CISIF como bus de configuración (H56-2); asumir IDs opacos; buscar `SENS_B` por cadenas (0 aciertos); atribuir `0xf2a1…`/`0xf2403…` a SENS_B (parecen reloj/ADC).

## Hipótesis (estado, confianza)
H56-1 VERIFICADA con matiz (alta) · H56-2 REFUTADA como formulada (alta) · H56-3 PARCIAL (alta) · H56-4 NO VERIFICADA · H56-5 NO VERIFICADA · H56-6 NO VERIFICADA · H56-7 INFERENCIA (media-baja) · H56-8 NO VERIFICADA · H56-9 NO VERIFICADA (no demostrable). Detalle en la matriz.

## Bloqueantes
Sin datasheet IMX210; el bloque P2S/DFE0 es hardware (no se ve cómo serializa); consumidor de SENS_B no hallado; origen de los valores de banco del tiempo de exposición (`0x43eb35d0`) no rastreado; REA no cubre las entradas Thumb (`0x436d6f6c`).

## Viabilidad y decisión S51
Aparece un camino técnico nuevo y concreto (registros 16/8 bit con formato conocido), pero no una capacidad demostrada. **S51 se mantiene: A=NO, B=NO, C=NO.** No se genera parche.

## Siguiente experimento (requiere autorización específica, pasivo)
Analizador lógico en `CIS0_SI/SCK/XCS`, `CIS0_VD`, `CIS0_SHT_RST` (XPI) y `CA_1ST_CURTAIN_START`: foto mecánica 1/1000, 1/4 s y EFCS; decodificar con `analysis/s56/p2s_emu.frames` y comparar ID1 (C4/CC/94…), 3–8 y pulsos XPI. Estático alternativo: rastrear quién rellena `0x43eb35d0+0xc4..0xd8` (tiempo→svd/shd/spl).
Límites: sin ejecutar firmware real; mypy no ejecutado (scripts sin tipos); emulación cubre formateador/SetExposure, no el hardware.
