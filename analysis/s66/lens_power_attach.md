# S66 (subtarea D) — Montura de lente: encendido, identificación y ciclo de vida

**Alcance:** ingeniería inversa **general** de la cámara (subsistema de montura E-mount del
`av-cam.bin` de A6000), **sin relación** con la línea SilentShutter/obturador electrónico.
Todo es análisis estático de bytes: no se ejecuta firmware, no se tocan cámaras.

**Estado de los hechos:** VERIFICADO = comprobado contra bytes/instrucciones del blob.
INFERENCIA = lectura razonada de esos bytes. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s66_lens_mount.py` (18 tests), `analysis/s66/func_strings.py`,
`analysis/s66/mount_strings_map.py`, `analysis/s66/out/func_436e5e3c.txt` (evidencia cruda).

---

## 1. Dónde vive el subsistema (VERIFICADO)

| Elemento | Dirección | Evidencia |
|---|---|---|
| Región de strings del subsistema | `0x43c95659`–`0x43c9a900` (646 cadenas en `0x43c95600`–`0x43c9ab00`) | barrido de strings del blob |
| Código del controlador | `0x436dfe6c`–`0x436e9ea4` (≈128 KB) | referencias a los logs anteriores |
| Ficheros fuente internos | `Mount_Controller.cpp`, `Mount_DividedInfo.cpp` | literales en los propios logs (`0x43c9671a`, `0x43c972fb`, `0x43c9756f`) |
| Tarea principal de montura | `0x436e5e3c`–`0x436e7bf0` (7604 B, 63 logs) | barrido lineal + `push {…,lr}` |
| API de usuario | `libInfraLensCommunicator.so` (`GetMountedLensInfo`, `GetSuopportedCommandIds`, `SndSyncMsg`, `ReadBackup`) | tabla de símbolos de la biblioteca |

El subsistema se autodenomina **"BL"** (*body↔lens*) y distingue dos direcciones:
`[B->L]` (cuerpo→lente) y `[L->B]` (lente→cuerpo).

---

## 2. Inventario de mensajes (VERIFICADO)

### 2.1 Cuerpo → lente (`[B->L]`)

| Mensaje | Dirección de la instrucción | Función que lo emite |
|---|---|---|
| `CS_POWER` | `0x436e4412` | bloque de power-off, `0x436e4360` |
| `ATTACH_INFO1` | `0x436e445c` | `0x436e4360` |
| `ATTACH_INFO3` | `0x436e449e` | `0x436e4360` |
| `ATTACH_INFO4` | `0x436e44da` | `0x436e4360` |
| `TEST_CMD:%d` | `0x436e4572` | `0x436e4360` |
| `CS_RESET` | `0x436e4708` | `0x436e4360` |
| `UPDATE_DATA` | `0x436e4800` | `0x436e4800` |
| `ALPHA_LENS_INFO:%d` | `0x436e50c4` | `0x436e509c` |
| `CS_CREDIT=%d` | `0x436e520e` | `0x436e51ac` |
| `UPDATE_ON` | `0x436e714a` | tarea principal |
| `STARTUP_INFO` | `0x436e5c6c` | `0x436e5c6c` |
| `ATTACH_INFO2` | `0x436e5cfc` | `0x436e5cfc` |

### 2.2 Lente → cuerpo (`[L->B]`)

| Mensaje | Dirección de la instrucción | Función que lo decodifica |
|---|---|---|
| `CS_POWER` | `0x436e4b82` | `0x436e4b66` |
| `SYSTEM_HZ` | `0x436e4bb2` | `0x436e4b96` |
| `CS_RESET` / `CS_RESET_ERROR` | `0x436e4be8` / `0x436e4c06` | `0x436e4bc4` |
| `CS_SLEEP` | `0x436e4c42` | `0x436e4c26` |
| `CS_CHECK_CMD` | `0x436e4c78` | `0x436e4c54` |
| `ATTACH_INFO1` (+`LENS UNKNOWN`, `LENS FIRMERR`) | `0x436e4cc6` | `0x436e4ca0` |
| `STARTUP_INFO` (+`SYNC START UP INFO ERR`) | `0x436e5034` | `0x436e4f98` |
| `CS_CREDIT` | `0x436e5088` | `0x436e505c` |
| `ATTACH_INFO2/3/4` | `0x436e67fe`/`0x436e6854`/`0x436e68ce` | tarea principal |
| `ALPHA_LENS_INFO:%d` | `0x436e7292` | tarea principal |
| `TEST_CMD:%d` | `0x436e7840` | tarea principal |
| `UART_HZ 750:%d 1500%d` (+`UART_HZ NG`) | `0x436e65bc` / `0x436e6638` | tarea principal |

### 2.3 Estructura interna (VERIFICADO por literales de depuración)

El blob incluye los **nombres de campo** de las estructuras del protocolo (`0x43c95745`–`0x43c96439`):
`BL ReceiveData`, `BL SendData`, `BL VsyncBufInfo`, `BL Info`, con campos
`CommState`, `ConnectLens`, `PowerMode`, `PowerMainSeq`, `LensPowerState`, `ReceiveLastIndex`,
`PreviousIndexInfo1/2`, `NowIndexInfo1/2`, `ErrCode`, `VsyncErrCount(+All)`, `ModuleCommand`,
`Mecha`, `LMCommandRes`, `Capture`, `POST`, `Timing`, `mastercounter`, `nextVDCycle`,
`nowVDCycle`, `vd_counter(VFC)`, `vd_counter(BL)`, `EditFlg(info1/2)`, `SendFlg(info1/2)`,
`EditCmpMCS/TC/EC/LC(0|1)`, `WriteSize(info1_0…)`, `PreviousSendCnt(info1/2)`, `GPL/GPMA DDS`.

Esto fija la **forma del protocolo**: dos buffers (recibidos/enviados) con dos "info" (Info1/Info2,
probablemente las dos mitades del paquete) y un bloque de estado (`BL Info`) con estado de
comunicación, estado de lente, modo/secuencia de power, contadores de error de VSYNC, índices de
paquete y contadores de VD (cuerpo y BL).

---

## 3. Identificación y tipo de lente (VERIFICADO)

Función `0x436e4eb4` (tras el bloque `[L->B]ATTACH_INFO1`):

```
ldrb r6, [r3, #0x22]     ; campo de modo de alimentación de la lente
and  r6, r6, #3          ; → 2 bits
cmp  r6, #1  → "LENS_POWER_4.8V"   (lente alimentada a 4.8 V)
cmp  r6, #2  → "LENS_POWER_UNREG"  (lente no registrada / tipo no estándar)
otro        → "LENS_TYPE_UNKNOWN"  → código de error 0xFF
éxito       → código 0x0A
```

- Dirección del log 4.8 V: `0x43c97cff`; el argumento del log incluye `0x1000` (=4096, mV) → **4.096 V**.
- Códigos: `0xFF` = tipo desconocido, `0x0A` = tipo válido (VERIFICADO en `0x436e4f5a`–`0x436e4f6e`).
- La lente puede además declarar **"ALPHA"** (`[B->L]ALPHA_LENS_INFO:%d`, `0x43c988cc`;
  `[B->L]ALPHALENS:%d,%d`, `0x43c96ea2`) → INFERENCIA: catálogo de lentes de terceros / montura
  "alpha" con información ampliada.

---

## 4. Bus cuerpo↔lente (VERIFICADO en parte)

| Hecho | Evidencia | Estado |
|---|---|---|
| Transporte **serie (UART)** | logs `UART_HZ 750:%d 1500%d` (`0x43c98540`), `UART_HS_COMPLETE` (`0x43c985b9`), `UART_HZ NG` (`0x43c98569`) | VERIFICADO (el log lo nombra) |
| Handshake de hardware por líneas **CS** y **DATA** | `[HS]CS_HIGH` (`0x43c97ac6`), `[HS]DATA_HIGH` (`0x43c97ae5`), `[HS]CS_LOW` (`0x43c97b06`), `[HS]COMPLETE` (`0x43c97b24`), `[HS]POWER SEQ TIME OUT` (`0x43c97b44`) | VERIFICADO |
| Las líneas CS/DATA se manejan con **primitivas GPIO** | `0x436e48fc`/`0x436e4d68` llaman a `0x43ada128` (set) y `0x43ada134` (get); el getter `0x43a1c768` salta a `0x43b5e2bc` = `gpio_get` documentado en S55 | VERIFICADO |
| Máquina de estados del handshake sobre `[r6+0x10]`: 0 → CS_HIGH, 1 → espera DATA, 3 → CS_LOW | `cmp r4,#1/#3/#0` en `0x436e4d74`–`0x436e4d7c` | VERIFICADO |
| Los **números de pin GPIO** de CS/DATA | los descriptores están en punteros **reubicados** fuera del blob (`0x9700b34`, `0x49215735`…) | NO_VERIFICADO |
| **Unidades** de "UART_HZ 750/1500" | el log no lo dice | NO_VERIFICADO (INFERENCIA: baudios muy bajos o tiempos de handshake) |
| Framing de la trama (cabecera/footer/checksum) | **VERIFICADO** (subtarea A, `analysis/s66/mount_functions.md` §3): cabecera `0xF0`, longitud `size+8` LE, tipo de comunicación (`&7`) en `+3`, ID de comando en `+5`, datos, **checksum u16 LE** (suma de bytes de `buf+1` durante `len-4`; excluye cabecera, checksum y footer) y footer `0x55`. Recepción: `HEADER_NG`(3) → `FOOTER_NG`(5) → `CHECKSUM_NG`(4) → `DATASIZE_NG`(2) → `COMMTYPE_NG_0`(6)/`_1`(7) → despacho por ID | VERIFICADO |

---

## 5. Ciclo de vida (tarea principal `0x436e5e3c`)

Secuencia de logs **en orden de código** (evidencia completa en
`analysis/s66/out/func_436e5e3c.txt`, 63 entradas):

```
MOUNT_CA_REQ_CLOSED → LOGIC_POWER → CA LOGIC POWER RES ERR → POFF(WAIT_LOGICPWR_OFF)
→ ERROR DETACH → DETACH RETRY → LENS_WEAR_START → UART_HZ 750/1500 → UART_HZ NG
→ UART_HS_COMPLETE (NO_WAIT) → [L->B]ATTACH_INFO2/3/4 → LENS_WEAR_END
→ WAKE_UP_START → WAKE_UP_END → POWEROFF_START → POWEROFF_HANDSHAKE_END
→ POWEROFF_HANDSHAKE_TIMEOUT_ERROR → cam_cmd change (0xC05:PB 0xC06:POFF) → POWEROFF_END
→ DETACH_1 → DETACH_COMP → DETACH_2 → DETACH_START → LOGIC_OFF(+COMP) → LOGIC_ON(+COMP)
→ [B->L]UPDATE_ON → LOGIC_OFF2(+COMP2) → [L->B]ALPHA_LENS_INFO → WAIT CHGFREQ1/2
→ WAIT NEXTVD → FREQ Now/Send → STANDBY → PB->WAKEUP->OFF → POWEROFF_* → [L->B]TEST_CMD
→ WAIT_LOGICPWR_OFF → POFF → FORCE LENS DETACH → LastLensError → POWER PARAM mode/main_seq/hs_seq
```

Lectura (INFERENCIA, apoyada en los logs):
1. **Ciclo de vida del lente**: detección (LENS_WEAR) → negotiation (UART_HZ, ATTACH_INFO) →
   operativo (WAKE_UP) → apagado (POWEROFF handshake) → **desmontaje** (DETACH_1/2/COMP) →
   **montaje** (LOGIC_ON/OFF = alimentación lógica de la montura) → standby (STANDBY,
   PB->WAKEUP->OFF).
2. **LOGIC_ON/LOGIC_OFF** controlan la alimentación lógica de la montura (no la del lente);
   `POWEROFF`/`PB` = power-off y power-back del conjunto.
3. **CS_CREDIT** implementa crédito de flujo: el cuerpo envía `CS_CREDIT=%d` y la lente responde
   `CS_CREDIT`; el log `LIF CREDIT RegistErro Lens doesn't know = %d` (`0x43c971b4`) marca el
   error cuando la lente no conoce el crédito.
4. **Cambio de frecuencia del bus**: `CHG FREQ` (`0x436e5b16`), `WAIT CHGFREQ1/2`, `FREQ Now:%d,
   Send:%d`, `WAIT NEXTVD` → el cambio de baudios se sincroniza con el VD (vertical drive).
5. **Lens wear**: `LENS_WEAR_START/END` envuelve la rutina de desgaste (polvo en la montura);
   hay además un guardado de datos de lente en `/mnt/Mount_ms_log_%03d.dat` (`0x43c97146`).

---

## 6. Comparación A6000 (fw3.21) vs A7S (fw3.20) (VERIFICADO por strings)

A7S tiene el **mismo subsistema** (`Mount_Controller.cpp`, `Mount_DividedInfo.cpp`, `BonoboDSP_*`,
`LensPowerState`, `LENS_TYPE_UNKNOWN`, `LENS FIRMERR`, `UART_HZ NG`, `PREPARE UPDATE`, `[L->B]`),
pero con un esquema de traza **reducido**:

| Rasgo | A6000 | A7S |
|---|---|---|
| Prefijos `[MOUNT_DEBUG]` / `[MOUNT_ERROR]` | sí | **no** (solo `[BL]…`) |
| Marcas `[B->L]` | sí | **no** |
| `LENS_WEAR_START/END` | sí | no |
| `DETACH_START/DETACH_COMP` | sí | no |
| `ALPHA_LENS_INFO` | sí | no |
| `LENS_POWER_4.8V` / `LENS_POWER_UNREG` | sí | no |
| `CS_CREDIT`, `LENS_SLEEP MODE` | sí | no |
| `UART_HZ 750:%d 1500%d` | sí | no |
| `PREPARE UPDATE`, `[L->B]`, `LensPowerState` | sí | sí |

INFERENCIA: la fw3.21 de A6000 **añade** el soporte de lente 4.8 V, la rutina de desgaste, el
ciclo explícito de detach/attach y la señalización completa; la A7S (fw3.20) conserva el núcleo
del protocolo pero sin esas extensiones. No es concluyente sin el historial de firmware.

---

## 7. Lo que queda abierto (NO_VERIFICADO)

1. **Pines físicos** de CS/DATA y de la alimentación de 4.8 V (descriptores en memoria reubicada,
   fuera del blob). Siguiente vía: datos de backup BK4 (como en S55) o esquema del manual de servicio.
2. **Unidades** de `UART_HZ 750/1500` y del timeout de 5000 (`movw r0,#0x1388` en `0x436e4db0`).
3. **Formato exacto de la trama** (cabecera/footer/checksum): **RESUELTO** por la subtarea A
   (ver §4). Persiste NO_VERIFICADO el **nombre** de cada ID de comando: la tabla de descriptores
   (`{u16 id, u16 size, u16 extra}`, terminador `0x100`, máx. `0x600` B) se registra **en tiempo de
   ejecución**, así que en la imagen estática solo hay código; sí se sabe que la lente declara qué
   comandos conoce mediante **dos bitmaps** indexados por `(ID-1)>>3` y bit `(ID-1)&7`
   (`0x436e00dc`).
4. **Semántica de "ALPHA"** (lente de terceros) y del campo `LensPowerState`.
5. **Código que carga `/lens/VX91xx_lensfile.bin`**: la entrada en `av-cam.bin` es
   `Camera::Lens::ODL::Load` (`0x43721b9c`), que pide los datos por mensaje asíncrono; el servicio
   que abre el fichero está **fuera** de `av-cam.bin` (ver subtarea F).

---

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s66_lens_mount.py -q     # 18 tests
.venv/bin/python analysis/s66/mount_strings_map.py A6000 --lo 0x43c95600 --hi 0x43c9ab00
.venv/bin/python analysis/s66/func_strings.py A6000 0x436e5e3c 0x436e7bf0 --calls
```

La sesión REA (Ghidra 12.1.4) sobre `av-cam.bin` se usó vía demonio
(`analysis/rea-independent/bin/q.py`) para decompilar `0x436e0d74`/`0x436e1328`/`0x436e239c`;
el resto se resolvió con Capstone sobre bytes.
