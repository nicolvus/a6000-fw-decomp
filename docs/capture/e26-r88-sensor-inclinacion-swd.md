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

## 3b. Corrección: el firmware pulsa el sensor cada 100 ms (MEDIDO, misma fecha)

* Puntos de observación (`wp`) en el núcleo 3 (`dbgbase 0x80116000`, el del RTOS; los núcleos 0–2 estaban en `0x40049e9c`):
  el firmware lee u0 ch6 en `0x4398ee1e` (lectura de canal del driver, `r1 = 6`) de forma repetida y, vistas desde la CPU,
  ch6 ≈ `0xa5` y ch7 ≈ `0x3c8`. Detener el núcleo en cada lectura **bloquea la cámara** (no dispara): no repetir sin límite.
* Por AHB-AP (sin detener nada) a ~5 kHz: ráfagas **cada 100,0 ms** (el periodo que arma `startOrientationRollNotify`), cada una
  con una caída tipo RC de pocos ms. Las lecturas de §3 caían entre pulsos: **corrige §3.1, §3.4 y la «contradicción» de §4**. El atributo
  `CSW` del AP no influye. No hace falta forzar el GPIO: el LED lo gobierna el firmware (el bit 20 sigue siendo INFERENCIA).
* **Giro controlado (65 s, 656 pulsos, 0 errores SWD;** usuario: horizontal → vertical disparador arriba → horizontal → vertical
  disparador abajo → boca abajo → horizontal, ~10 s cada una). Mediana del pico por tramo de 10 s:

| Tramo | 0–10 | 10–20 | 20–30 | 30–40 | 40–50 | 50–65 s |
|---|---|---|---|---|---|---|
| ch6 | 144 | 144 | 148 | 149 | 150 | 149 |
| ch7 | 158 | 158 | 161 | 162 | 163 | 163 |

  Ninguna posición produce un salto: la deriva total es de 6 cuentas en ch6 y 5 en ch7 (≈ 0,6 % de fondo de escala), monótona.
  En sesiones anteriores, también en horizontal, ch7 valía 968 (40 s) y 154 (1,1 s): el nivel de ch7 cambió **entre** sesiones, no
  con el giro. `pulsos-65s-rotando.log.gz`, `picos-65s-rotando.txt`, `pulseR.cfg`.

## 3c. Giro controlado tras reiniciar la cámara (MEDIDO; anula la lectura de §3b)

La cámara estaba colgada durante §3b (el usuario la reinició; causa probable: las paradas del núcleo 3 por los puntos de
observación). Las cifras de §3b se tomaron con el firmware colgado y **no valen para la orientación**. Repetición, 65 s,
666 pulsos, 0 errores SWD, misma secuencia pedida al usuario:

| Tramo | ch6 (`VH_SENSE_1`) | ch7 (`VH_SENSE_2`) | Estado |
|---|---|---|---|
| 0–10 s | 104 → 115 | 136 → 152 | bajo / bajo |
| 11–19 s | 145–167 | 967 | bajo / **alto** |
| 20–31 s | 964 | 967 | **alto / alto** |
| 32–64 s | 964 | 200–227 | **alto** / bajo |

* **Salida binaria por canal:** «alto» ≈ 964–967 (casi fondo de escala) y «bajo» ≈ 100–230. Los cambios son saltos de un pulso a
  otro (100 ms); dentro de un estado solo hay deriva lenta (≤ 30 cuentas), sin relación con el ángulo.
* **Cuatro combinaciones** de dos bits = cuatro orientaciones a 90°: el diseño típico de un detector óptico de 4 direcciones.
* La asignación estado → orientación no se pudo fijar: la secuencia observada no repite el estado inicial al volver a horizontal
  (posible histéresis del elemento móvil o tiempos distintos a los pedidos). `picos-65s-rotando-tras-reinicio.txt`.

## 4. Conclusión

* **Como nivel:** con lo medido **no es viable demostrarlo**. El sensor es óptico, de dos canales, pensado para estados discretos
  (horizontal / vertical a cada lado); como mucho daría roll grueso y nunca pitch. La A6300 usa (INFERENCIA) un sensor distinto para su nivel.
* **Medida directa (§3c):** cada canal es binario (≈ 964 o ≈ 100–230), con saltos de un pulso a otro. Dos bits dan cuatro orientaciones
  a 90°; no hay salida proporcional al ángulo. **Como nivel, descartado** (F9 cerrado). Para un nivel haría falta un acelerómetro
  añadido por hardware.
* Límite: no se fijó qué combinación corresponde a cada orientación.
