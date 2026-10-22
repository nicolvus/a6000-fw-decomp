# S602 — módulo `[REMOTE]` (bajo `[ACCY]`) (32 trazas): exclusivo de A6000 fw3.21

**Estado: VERIFICADO** — 30 cadenas únicas con prefijo `[REMOTE]` (todas bajo `[ACCY][DEBUG/INFO/WARN/ERR][REMOTE]`) en la A6000 fw3.21; **0 en A7S fw3.20** y **0 en A6300 fw2.01** (búsqueda literal `strings -a` en los tres `av-cam.bin`).

---

## 1. Censo de trazas (30 únicas `[ACCY][...][REMOTE]`, direcciones virtuales base 0x43000000)

| # | VA | Texto (truncado) |
|---|---|---|
| 1 | 0x43c25b9f | NotifyUartCommand...UART CMD:%C%C%C%C%C%C [%02X %02X %02X %02X %02X %02X] |
| 2 | 0x43c25c01 | RecvCmd Unknown Category:%02X |
| 3 | 0x43c25c37 | EventKey Catwgory:%02X ,Data1:%02X, Data2:%02X |
| 4 | 0x43c25c7e | RetrySendCmd...retry_up:%d |
| 5 | 0x43c25cb1 | RetrySendCmd Buffer err |
| 6 | 0x43c25ce0 | SaveInfo...GF:%d SS:%d Freeze:%d Photo:%d Zoom:%d Tally:%d |
| 7 | 0x43c25d33 | Zoom State Change To %d Speed:%d |
| 8 | 0x43c25d6d | RestoreInfo...Savedata:%02X %02X |
| 9 | 0x43c25da6 | ExecUartCommand |
| 10 | 0x43c25dce | To Input KEY:%08X STATE:%08X INFO:%08X |
| 11 | 0x43c25e0d | SendCmd...CMD:%S retry:%d |
| 12 | 0x43c25e3f | SendCmd Buffer Busy Request CMD:%S |
| 13 | 0x43c25e79 | TallyControlCmd...retry:%d |
| 14 | 0x43c25eac | CallForTransaction...Wait Tally Light Response  NextState:%d |
| 15 | 0x43c25f01 | NotifyApiRequest...Command:%02X State:%02X CntlState:%d |
| 16 | 0x43c25f51 | NotifyApiRequest...Buffer Busy CntlState:%d |
| 17 | 0x43c25f95 | NotifyApiRequest...Tally Light State:%d  NextState:%d |
| 18 | 0x43c25fe3 | NotifyApiRequest...Not Support Command:%02X or State:%02X |
| 19 | 0x43c26035 | AccyCmdClr |
| 20 | 0x43c26058 | RemoteClose...Spinal:%02X  GF:%02X  SS:%02X  Freeze:%02X  Photo:%02X  Zoom:%02X |
| 21 | 0x43c260c0 | GUIDE FRAME OFF  KEY:%08X STATE:%08X  INFO:%08X |
| 22 | 0x43c26108 | START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X |
| 23 | 0x43c2614f | PHOTO FREEZE OFF  KEY:%08X STATE:%08X  INFO:%08X |
| 24 | 0x43c26198 | PHOTO REC OFF  KEY:%08X STATE:%08X  INFO:%08X |
| 25 | 0x43c261de | ZOOM OFF  KEY:%08X STATE:%08X  INFO:%08X |
| 26 | 0x43c2621f | NotifyDetached |
| 27 | 0x43c26246 | NotifyUartTimedOut...RetryCount:%d |
| 28 | 0x43c26281 | TimeoutNotify...Command Not Execution |
| 29 | 0x43c262be | EventTimeout Tally Light TIMEOUT |
| 30 | 0x43c262f8 | NotifyUartResponse...Set Tally Light:%02X |
| 31 | 0x43c2633a | Set Tally Light:%02X State:%d |
| 32 | 0x43c26371 | NotifyAttached |

**Cadenas `Remote` adicionales (sin prefijo `[ACCY][...][REMOTE]`):**
- 0x43bd6100: "Object is remote"
- 0x43bd6214: "Remote address changed"
- 0x43bd66b8: "Remote I/O error"
- 0x43c2536b: "[ACCY][DEBUG][FACTORY]:%d:Remote Attached"
- 0x43c26398: "18AccyUmDeviceRemote"
- 0x43ca53cf: "[IMAGING_REL]: remote capture cancel due to camuser's release lock"

---

## 2. Funciones emisoras (REA `xrefs` + `procedure_pseudo_code`)

Solo 6 de las 30 cadenas principales tienen xrefs directos; apuntan a funciones en **0x43566xxx** (área de logging OSAL):

| VA | Función (Ghidra) | Cadena(s) | Rol |
|---|---|---|---|
| 0x43566528 | `FUN_43566528` | #6 SaveInfo | Codifica estado GF/SS/Freeze/Photo/Zoom/Tally en buffer |
| 0x43566984 | `FUN_43566984` | #11 SendCmd, #12 Buffer Busy, #13 TallyControlCmd, #14 CallForTransaction | Construye comando UART (header `0x25 0x37 0x36` = `%76`), state byte, terminador `0x30 0x2a` = `0*`; llama `FUN_43a3b2a0` (envío UART) |
| 0x43566b84 | `FUN_43566b84` | #19 AccyCmdClr | Limpia estado en `param_1+0x14`, `+0x18`, `+0x1c` |
| 0x4356623c | `FUN_4356623c` | Logger común (nivel 0x5d) | Usado por todas las funciones anteriores |

**Nota:** Las 24 cadenas restantes (#1–5, #7–10, #15–18, #20–32) no tienen xrefs directos visibles; pueden usar tabla de punteros o referencias computadas.

---

## 3. Protocolo UART / REMOTE inferido

### 3.1 Formato de comando UART
```
Header:     0x25 0x37 0x36   ("%76" ASCII)
State byte: 0x31/0x32/0x33/0x30  (desde param_1+0x41: 1/2/3/default)
Terminator: 0x30 0x2a         ("0*" ASCII)
```

### 3.2 Comandos identificados
| Comando | Descripción |
|---|---|
| `NotifyUartCommand` | UART CMD de 6 bytes recibido del remote |
| `SendCmd` | Envío genérico con reintentos |
| `TallyControlCmd` | Control de Tally Light (led tally) con reintentos |
| `CallForTransaction` | Espera respuesta de Tally Light (NextState) |
| `NotifyApiRequest` | Petición API: Command/State/CntlState |
| `AccyCmdClr` | Limpia comando accesorio |
| `RemoteClose` | Volcado de estado al cerrar: Spinal/GF/SS/Freeze/Photo/Zoom |
| `ExecUartCommand` | Ejecuta comando UART |

### 3.3 Eventos de notificación
| Evento | Descripción |
|---|---|
| `NotifyAttached` | Remote conectado |
| `NotifyDetached` | Remote desconectado |
| `NotifyUartResponse` | Respuesta Set Tally Light |
| `NotifyUartTimedOut` | Timeout UART con contador de reintentos |
| `EventTimeout` | Tally Light TIMEOUT |

### 3.4 Campos de estado (SaveInfo / RemoteClose)
| Sigla | Significado |
|---|---|
| **GF** | Guide Frame |
| **SS** | Start Stop |
| **Freeze** | Photo Freeze |
| **Photo** | Photo Rec |
| **Zoom** | Zoom |
| **Tally** | Tally Light |

---

## 4. Diferencial A7S fw3.20 / A6300 fw2.01

| Firmware | Cadenas `[ACCY][...][REMOTE]` | Conclusión |
|---|---|---|
| A6000 fw3.21 | 30 únicas / 32 totales | **Módulo presente** |
| A7S fw3.20 | 0 | **Ausente** |
| A6300 fw2.01 | 0 | **Ausente** |

**Verificación:** `strings -a` literal en los tres `av-cam.bin` (SHA256 distintos). REA `search_strings` en A6000 confirma 30 cadenas únicas `[REMOTE]` bajo `[ACCY]`.

---

## 5. Evidencia y reproducibilidad

- **JSON + test:** `analysis/s602_remote/`
  - `remote.json` — catálogo completo
  - `test_remote_exclusivity.py` — test automatizado (3 asserts)
- **Herramientas:** REA (MCP `search_strings`, `xrefs`, `procedure_pseudo_code`) + `strings -a` / `grep` como control positivo.
- **Binario:** `av-cam.bin` A6000 fw3.21 (SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).

---

## 6. Límites / NO_VERIFICADO

- Solo 6/30 cadenas tienen xrefs directos; las demás pueden usar tabla de punteros o referencias computadas no resueltas por REA.
- Funciones en 0x43c25xxx (donde residen las cadenas) no decompiladas; emisoras identificadas en 0x43566xxx (logger OSAL).
- Nombres de archivo fuente no recuperados.
- Protocolo UART/Tally/ACCY inferido de formato de trazas; no confirmado en símbolos.
- La ausencia en A7S/A6300 es **estática**; no prueba incapacidad de hardware.
- No se probó alcance en runtime (sin firmware ejecutado).

---

## 7. Conclusión para la línea del obturador electrónico

**Sin efecto directo en S51 (A/B/C = NO).** El módulo gestiona **control de accesorio remoto (ACCY) vía UART**, incluyendo Tally Light (led de grabación), Zoom, Photo, Freeze, Guide Frame, Start/Stop. Es un subsistema de **control externo/accesorio** exclusivo de la A6000 fw3.21. No menciona `shutter`, `silent`, `electronic`, `EFCS`, `curtain`, `mechanical`, `flicker`.

---

**Próximo:** S603 — decodificar `[CAMERA_DSP_APL]`.