# E26-R88 — Sensor de orientación horizontal/vertical (SE7750): esquema, firmware y medida SWD (11-11-2026)

Pregunta del usuario: ¿qué detecta si la foto es vertical u horizontal y podría servir de nivel (como el de la A6300)?
Etiquetas: **MEDIDO** · **VERIFICADO** (bytes/esquema) · **INFERENCIA**. Firmware en cámara: CFW 3.77. Sonda SWD
`E6698030DF5B3936` (DPIDR `0x3ba02477`). Scripts y registros: `analysis/e26-r88/`.

## 1. Hardware (VERIFICADO en el esquema, `sony_ilce-6000…level3.pdf`)

* **No es un acelerómetro.** SE7750 (1-487-961-11) es un «SLANT SENSOR», rotulado «HORIZONTAL/VERTICAL POSITION DETECT»
  (SY-1028 18/23, flex FP-2045/CN-1027). Símbolo: LED + fototransistores → detector óptico de inclinación (INFERENCIA por el símbolo).
* Alimentación `VCC_ACCEL` (de D_3.15V; el nombre de la red no implica un acelerómetro). LED conmutado por Q7750 (RN1102MFV, R7750 180 Ω)
  desde **`ROTATE_SENS_ON`**. Salidas analógicas **`VH_SENSE_1` → `ADC0_IN6` (bola AA22, compartida con `SIR_RXD`) y `VH_SENSE_2` → `ADC0_IN7`**
  (R7751/R7752 22 k, C7750/C7751 0,1 µF). Sin I²C/SPI; Darwin no interviene.
* `ROTATE_SENS_ON` sale de la bola **F11 del BIONZ, red `MMC_DAT_4`** (pág. 26, `pdftotext -bbox`): pin MMC reutilizado como GPIO, igual que
  sus vecinos `POKB` (`MMC_CMD`), `MSS_LENS_UNREG_ON` (`MMC_CLK`), `DWN_IN_RELEASE` (`MMC_DAT_1`) y `SHOE_VDD_ON` (`MMC_DAT_0`).

## 2. Firmware (VERIFICADO en bytes salvo indicación)

* `libObj.so` (Linux): `InputService::startOrientationRollNotify` (0x10fe6d) / `stop…` (0x10fecd) solo arman/paran una notificación con
  periodos 100/500; no tocan el sensor. Comandos de servicio `MPR_CMD_GSENSOR_ADJUST_START/STOP/GET_VALUE/SET_DROP/CHECK` (genéricos de plataforma).
* `av-cam.bin`: `Stage_Orientation.cpp`, `Orientation judge failed: %x`, `orientation_result = 0x%x` (etapa de captura que decide la orientación
  → EXIF; INFERENCIA por nombres).
* Driver GPIO del RTOS (`0x4398f86c`–`0x4398fa5c`): funciones (banco, bit, valor) sobre `0xf2910000 + 0x100·banco` (PORTSEL +0x34/+0x38,
  DIR +0x04/+0x08, +0x20, +0x40) y **un segundo bloque `0xf2912000 + 0x100·banco`** (DIR +0x04/+0x08, **DATA_SET +0x14 / DATA_CLR +0x18**).
  Solo 2 `bl` directos a estas funciones: el resto se llama por punteros; no se localizó el llamador del sensor.
* Driver ADC (`0x4398ed04`–`0x4398ee5a`): unidad u en `0xf2406000 + 0x1000·u`; +0x04 bit0/bit4, +0x08 bits[1:0] (modo), +0x0c bit8,
  +0x10 bit0 (estado), datos u16 en `+0x14 + 4·canal`, +0x44/+0x48. Semántica exacta de los bits: no resuelta.

## 3. Medidas SWD (MEDIDO; solo lectura salvo §3.4)

1. **Reposo:** 12+12 canales a 5 Hz, 45 s girando la cámara: ningún canal varía > 8 cuentas. u0 ch6/ch7 (`0xf240602c`/`0xf2406030`) = 0.
2. **Reproducción:** u0 ch6/ch7 dan ráfagas de ≈200 ms cada ≈1,7 s durante unos 6 s: (35, 45) → (101, 131) → (109, 144), cociente ch7/ch6 ≈ 1,3;
   luego 0. No se reprodujo en otras 4 capturas (≈250 s, hasta ~1 kHz). Qué las disparó: desconocido. `adc4-rafagas.log.gz`.
3. **Mapa del banco 3** (`0xf2912300`, DIR `05111010`, DATA `02eeefef`): bits 25→16 = `MMC_CMD`…`MMC_DAT_0`; salidas b24 (`MSS_LENS_UNREG_ON`),
   b20, b16 (`SHOE_VDD_ON`); entradas b25 (`POKB`), b17 (`DWN_IN_RELEASE`) y b18–b23 salvo b20. **`ROTATE_SENS_ON` = banco 3 bit 20 (INFERENCIA
   fuerte:** encaja la dirección de los 10 pines con la ordenación inversa; no se vio al firmware escribirlo).
4. **Escrituras:** a `0xf2910314` (por AHB-AP y con la CPU 0 detenida, `mww phys`) no tienen efecto en la lectura. A **`0xf2912314` sí:**
   DATA `02eeefef` → `02feefef`; se restauró con `0xf2912318`. Con el bit 20 a 1 durante 45 + 45 + 30 s (girando la cámara) y disparando además
   `+0x04` = 1/0x10/0x11 en la unidad 0: **ch6/ch7 = 0–1 todo el tiempo**. La unidad 0 sí convierte (ch8 `3fe/3ff`, ch11 `18e/18f` fluctúan);
   su `+0x00` alterna `0x0fff`/`0x00c0` en lecturas consecutivas.
5. Estado final: bit 20 a 0, `+0x04` de u0 a 0, CPU reanudada. Nada más escrito.

## 4. Conclusión

* **Como nivel:** con lo medido **no es viable demostrarlo**. El sensor es óptico, de dos canales, pensado para estados discretos
  (horizontal / vertical a cada lado); como mucho daría roll grueso y nunca pitch. La A6300 usa (INFERENCIA) un sensor distinto para su nivel.
* **Contradicción abierta:** forzando el bit 20 la salida sigue a 0 aunque el ADC convierte. Hipótesis: (a) b20 no es `ROTATE_SENS_ON`,
  (b) hace falta otra condición (alimentación de `VCC_ACCEL`, modo del pin), (c) la conversión de ch6/7 necesita una secuencia del driver no
  reproducida. Pendiente **F9** en `PENDIENTES.md`.
