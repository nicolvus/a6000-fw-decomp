# S73 (reconocimiento) — Protocolo de ajuste de fábrica `ADJ_CMD` (panel/EVF/OLED) y calibraciones

**Alcance:** línea de ingeniería inversa **general** de la cámara: el protocolo de **comandos de
ajuste** (`ADJ_CMD_*`) del `av-cam.bin` de A6000 (fw3.21), en concreto el bloque de **panel/EVF/OLED**
(`AVBB_PANELEVF`), el de **ADC** (`LIRO_DRIVERS_ADC`) y el bloque `ContrastPlus` del procesado de
captura. No es la línea SilentShutter, ni la montura de lente (S66), ni el AF, ni service mode.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s73_adj.py` (anclas verificadas).

---

## 1. La familia `ADJ_CMD_AVBB_PANELEVF_*` (VERIFICADO)

38 cadenas de nombre de comando, **todas** referenciadas por la misma función, el manejador de
ajuste de panel/EVF (`0x4363524c`), en `0x43c76c93`–`0x43c774d9`:

| Grupo | Comandos (nombre lógico) |
|---|---|
| Secuencia | `..._PANELEVF_ADJ_START`, `..._PANELEVF_ADJ_END` |
| Panel (PNL) | `PNL_TESTPATTERN`, `PNL_W_VCOM`, `PNL_W_VCOM_2ADRS`, `PNL_W_WB`, `PNL_W_WB_G`, `PNL_W_WB_R_2BYTE`, `PNL_W_WB_G_2BYTE`, `PNL_W_WB_B_2BYTE` |
| EVF/OLED | `EVF_W_WB`, `PANELEVF_EVF_OLED_W_WB_G`, `PANELEVF_EVF_OLED_CALDAC`, `PANELEVF_EVF_OLED_VO`, `PANELEVF_EVF_OLED_W_WB_RIGHT`, `PANELEVF_EVF_OLED_W_WB_G_RIGHT` |
| Termistor | `OLED_EVF_THERMISTOR_ADJ_INIT`, `_START`, `_CNFM`, `_INFO`, `_END` (+ variantes `_RIGHT`) |
| Pruebas | `TEST_START_PANELEVF`, `TEST_STOP_PANELEVF`, `TEST_SIO_SEND`, `TEST_BL`, `TEST_BRIGHT`, `TEST_SIO_DUMP`, `TEST_DIRECTION`, `TEST_SHIFT_PANELEVF` |
| Detección | `PNL_EXTPANEL_DETECT_START/_STOP`, `EVF_TYPE_DET_START`, `EVF_TYPE_DET_CONF` |

### 1.1 Estructura del manejador (VERIFICADO por instrucciones)

En `0x4363524c`:

- 4 búferes de 8 B en la pila (`memset` con `0xff` vía `0x439c5a04` en `sp+0x40/0x48/0x50/0x58`).
- `ldrh r2, [r6, #0x18]` → **ID de comando** (u16); se compara con `0x302`
  (`movw r3,#0x302` @ `0x4363527e`); si no coincide, se llama a `0x435ab880` con un literal
  (error) y se sale.
- `ldrb r3, [r6, #0x1a]` → **sub-comando** (u8) con rango **0..0x28** (29 valores)
  (`subs r3,#1; cmp r3,#0x28` @ `0x436352ac`).
- El estado se escribe en la estructura de entrada: `[r6+0]=8`, `[r6+1]=1`, `[r6+4]=8`,
  `[r6+8]=8`, `[r6+0xc]=8`.
- Las tablas de punteros se indexan por el ID (`ldr r3, [r3, r0, lsl #2]` @ `0x43635626`).

### 1.2 Calibración de WB del display (VERIFICADO)

`WB_SubB_R_Adrs=%02X ` (`0x43c76e31`), `WB_SubB_G_Adrs=%02X, ` (`0x43c76e87`),
`WB_SubB_B_Adrs=%02X, ` (`0x43c76ddb`): el ajuste de **balance de blancos del panel/EVF** opera
sobre **sub-bloques por canal R/G/B** identificados por una dirección de registro de 8 bits
(`%02X`). Es decir, el WB del display no es un único registro global sino tres sub-bloques.

### 1.3 Termistores OLED/EVF (VERIFICADO)

La secuencia `THERMISTOR_ADJ_INIT → _START → _CNFM → _INFO → _END` (y sus gemelas `_RIGHT`)
implementa la **compensación térmica de los displays**: se mide la temperatura de los termistores del
panel OLED y del EVF y se ajustan sus parámetros. `PANELEVF_EVF_OLED_CALDAC` sugiere además un DAC de
calibración asociado.

## 2. `ADJ_CMD_LIRO_DRIVERS_ADC_*` (VERIFICADO)

Cuatro nombres en `0x43ce4ff2`–`0x43ce507a`, todos referenciados por `0x4398e578`:
`LIRO_ADC_GET_DATA_ALL`, `LIRO_ADC_CHECK_DATA`, `LIRO_ADC_TEST_MODE`, `LIRO_ADC_SET_DATA`.
Es el juego de comandos de los **drivers ADC** del subsistema LIRO (lectura, verificación, modo de
prueba y escritura de datos).

## 3. `ContrastPlus` (VERIFICADO)

`ContrastPlus_Base` (`0x43cc7bc2`, referenciada por `0x438c2dc4`) y
`[IMAGING_CAP]: %s: ContrastPlus error` (`0x43cc7d5c`): una función de **procesado de imagen**
("ContrastPlus") dentro del camino de captura (`[IMAGING_CAP]`). Sony la usa en varios modelos para
el realce de contraste por píxel; aquí solo consta su existencia, su tabla base y su error.

## 4. Cómo se codifican los IDs (NO_VERIFICADO / siguiente paso)

Los 38 nombres **no** están en una tabla de punteros: cada rama del manejador carga su literal con
`ldr rX, [pc, #imm]; add rX, pc` y lo pasa a `0x435ab880` (traza). Por tanto, **el mapa ID↔nombre
está en el flujo de control**, no en los datos. Recuperarlo exige recorrer las comparaciones
previas a cada rama (el `cmp` con el ID) — trabajo mecánico pero extenso.

## 5. Abierto (NO_VERIFICADO)

- ID numérico de cada uno de los 38 comandos `AVBB_PANELEVF`.
- Semántica de `TEST_*` (¿test de fábrica? ¿SIO = puerto serie?).
- Registro de destino de los sub-bloques `WB_SubB_*` (¿I2C del controlador de display?).
- Qué es exactamente `ContrastPlus_Base` (tabla de coeficientes) y su efecto.
- Destino de los comandos ADC de LIRO (¿calibración del sensor?).
- Si la A7S (fw3.20) tiene el mismo bloque (no comprobado todavía).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s73_adj.py -q
```
