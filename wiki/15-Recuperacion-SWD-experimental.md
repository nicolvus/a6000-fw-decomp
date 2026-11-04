# 15. Recuperación por SWD (EXPERIMENTAL)

> **EXPERIMENTAL, pero ya probado una vez.** El 03-11-2026 se ejecutó en la cámara del autor: lectura ([R47](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md)) y recuperación completa **sin escribir la NAND a mano** ([R48](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md), [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)): la cámara arranca con el 3.26. Las fases 8 A/B de abajo (escribir `nflasha2`/`nflasha3`) **no se usaron ni se recomiendan**: Loader3 ignora las escrituras de bloque. La vía que funcionó está en «Resultado real». Sigue siendo soldar en una placa: puede dañarla, y un caso no es garantía.

Aplica solo a la A6000 bloqueada tras instalar el 3.25 (LED 3 lentos + 2 rápidos; error −302 de Loader3, **medido** en R47 §15). Causa y estado: [Estado actual](14-Estado-actual). Detalle técnico completo (en español): [R46](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r46-procedimiento-fisico-swd.md).

## Resultado real (R49)

1. Hilos soldados a los pads del lado BIONZ de R4911/R4912 (opción 5a) y sonda RP2040 con `debugprobe`; OpenOCD, DPIDR `0x3ba02477`, 3,09 V.
2. Con puntos de parada encadenados desde la entrada de Loader3, en la comprobación de `\updater\mode` se forzó `r0 = 0` (solo un registro, durante esa parada). Loader3 eligió BootMode 3 y arrancó el actualizador de fábrica de `nflasha1`.
3. `pmca-console firmware` instaló el 3.26: el primer intento se cortó al 45 % con `0x1063` (NG de Darwin, sin causa aclarada); el segundo se completó.
4. Verificación sin sonda: Mass Storage, `ILCE-6000`, firmware 3.26, sin LED de error.

Queda abierto: la causa del `0x1063` y retirar la sonda. Método completo y trampas (registros bancados, puntos de parada): [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md).

## Idea

Un depurador por SWD al BIONZ permitiría escribir en la NAND sin la clave del BootROM (que no conocemos). Después se vuelve al actualizador de fábrica y se instala firmware oficial por USB. Los motivos están en [R37](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r37-cierre-estatico-recuperacion.md), [R38](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r38-guard-y-entrada-updater.md) y [R40](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r40-jtag-swd-bionz.md).

## Qué sabemos y qué no

| Dato | Estado |
|---|---|
| SWCLK = bola W25 y SWDIO = bola W26 de IC6000 (BIONZ), hacia CN4906 pines 11/12 por R4911/R4912 | Esquema |
| R4911, R4912, R4915, R4916 y CN4906 **sin montar** (solo huellas) | Confirmado por el usuario (02-11-2026) |
| Ningún cargador toca el DAP CoreSight | Binario (R40) |
| Tensión real de SWCLK/SWDIO (se supone ≈ 3,15 V) | **No medido** |
| Si un eFuse bloquea la depuración | **No se sabe**; si lo hace, esta vía se descarta |
| Compatibilidad de OpenOCD/pyOCD con el CXD90014 | **No demostrada** |
| Escritura de NAND desde el BIONZ (capa lógica MuMin) | Solo análisis y emulación ([R39](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r39-estatico-profundo.md)) |

## Material

- Sonda SWD con tensión de referencia: J-Link EDU Mini, o Raspberry Pi Pico con `debugprobe` (esta trabaja a 3,3 V fijos; no usar si la línea mide 1,8 V).
- Multímetro con continuidad. No hace falta osciloscopio.
- Soldador de punta fina y estaño fino con flux; hilo esmaltado de 30 a 38 AWG; lupa o microscopio; malla desoldadora.
- Destornilladores de precisión, material antiestático, Kapton.
- Fuente regulada de 3,8–4,2 V limitada a 1 A, o batería NP-FW50 cargada.
- Opcional: resistencias de 0 Ω (0402/0603, solo para la variante 5b) y analizador lógico de 8 canales.

## Antes de empezar

1. Haz el **respaldo externo R1** y verifícalo (sigue pendiente).
2. Instala OpenOCD o pyOCD y comprueba que la sonda se detecta **sin** conectarla a la cámara.
3. Decide con antelación qué se escribirá (fase 8).

## Fases

Cada fase tiene criterio de parada. Si no se cumple, detente y documenta.

1. **Abrir y fotografiar.** Batería fuera, espera 5 min. Abre según el manual de servicio, guarda tornillos por zona y fotografía ambas caras de la placa SY-1028. Localiza CN4906, R4911, R4912 e IC6000.
2. **Identificar.** Compara con el esquema. Confirma que R4915 y R4916 están vacías (así Darwin no compite con la sonda). Marca los pads de R4911/R4912 y la masa más cercana.
3. **Continuidad (cámara apagada).** Mide qué pad de cada resistencia va al BIONZ y cuál a CN4906; que la masa de la placa sea común; y que no haya cortos entre SWCLK/SWDIO y masa ni con alimentaciones. Un valor bajo o un corto detiene el procedimiento.
4. **Tensión (cámara alimentada, sin sonda).** Mide D_3.15V_MSS y los pads de SWCLK/SWDIO contra masa. Si miden entre 3,0 y 3,3 V, puedes seguir; si miden 1,8 V u otro valor, no conectes una sonda de 3,3 V.
5. **Conectar los hilos (cámara apagada).**
   - **5a (recomendada):** un hilo directo al pad de R4911 y otro al de R4912 del lado del BIONZ, más un hilo a masa. Fíjalos con Kapton.
   - **5b:** montar resistencias de 0 Ω (o 22 Ω, máximo 47 Ω) en R4911/R4912 y soldar a los pads 11/12 de CN4906. Es más difícil: paso fino.
   - Longitud ≤ 15 cm. Revisa la continuidad y que no haya cortos antes de seguir.
6. **Primer contacto con el DAP (solo lectura).** Conecta GND primero y luego SWCLK/SWDIO. Con la cámara alimentada, ejecuta un escaneo SWD a 100 kHz (`dap info`); baja a 10–50 kHz si no responde. Éxito: IDCODE válido. Abandono: sin respuesta tras revisar tensión, conexión y velocidad, o depuración deshabilitada por eFuse.
7. **Lectura.** Detén el núcleo y lee `0xc0001200` (tabla de clave), `[0xc006000c]` y el buffer de log `0xc006001c…`. Confirma el código de error real y volca la RAM útil con SHA-256.
8. **Decidir la escritura, con respaldo previo de lo legible de `nflasha2` y `nflasha3`:**
   - **A.** Crear `\updater\mode` en `nflasha2` (R37/R38): el actualizador de fábrica de `nflasha1` arranca y acepta firmware por USB.
   - **B.** Reescribir `nflasha3` con la imagen válida del 20-10 ([R30](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r30-updater-done-boundary.md)).
   - Ambas deben respetar ECC, geometría y bloques defectuosos. No se han ejecutado.
9. **Cerrar.** Retira la sonda y los hilos, remonta, comprueba el arranque e instala por USB el paquete oficial **3.26** (preparado en R37). El 3.25c ([R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md)) es también experimental y no se recomienda instalarlo.

## Condiciones de parada

- Corto, lectura anómala o tensión inesperada.
- Olor, calor o consumo superior a 1 A.
- El DAP indica depuración deshabilitada.
- Cualquier duda sobre qué se escribe o dónde: no escribir.

## Riesgos

- Soldar en pads 0402 es irreversible y puede levantar pistas; fija los hilos para que no tiren.
- Una tensión incorrecta en SWCLK/SWDIO puede dañar el BIONZ.
- Una escritura mal hecha en `nflasha2` puede perder calibraciones.
- Si el eFuse bloquea el DAP, esta vía no sirve y quedan la lectura externa de la NAND (sin NAND identificada), el servicio de Sony o el cambio de placa.
