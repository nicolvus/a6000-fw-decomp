# E26-R11 — Sony A6000: acceso externo al BootROM UART y activación del modo de carga en RAM

**Fecha:** 29-10-2026  
**Repositorio:** `sony-a6000-electronic-shutter`  
**Alcance:** Exclusivamente offline. Ingeniería inversa de binarios, análisis de esquemas del manual de servicio, validación con scripts. **No se conectó, encendió, depuró ni modificó la cámara.** No se transmitió UART ni se realizaron pruebas eléctricas sobre el hardware físico.

---

## 1. Resumen ejecutivo

R11 investiga si el receptor UART del BootROM de la Sony A6000 (identificado estáticamente en R8/R9) puede activarse y utilizarse desde un conector externo de la cámara, especialmente el Sony Multi Terminal, sin soldar ni modificar la placa.

**Hallazgo principal:** El esquema eléctrico del manual de servicio (página 38, SY-1028 BOARD) documenta la red `BOOT_SERIAL_IN` hacia el nodo `MULTI pin 9 UART_RX/BOOT_IN` a través de `R4003` y `R4002`, pero **ambas resistencias están marcadas `XX` (no montadas)** en el esquema. Por tanto, **no existe continuidad eléctrica demostrada ni población de componentes entre el contacto de recepción BootROM UART y el conector Multi Terminal externo**. La ruta interna CN4906 (huella de servicio en SIDE A) sí lleva `DEBUG_UART0_RXD` en su pin 4, pero su montaje y continuidad en esta unidad tampoco están verificados.

**Decisión de cierre: Opción C** — Falta una identificación concreta. La ruta externa por Multi Terminal está descartada con evidencia (R4003/R4002 no montadas, sin continuidad), y la ruta interna CN4906 no está suficientemente verificada (montaje y continuidad pendientes de medición física autorizada). Se ha identificado exactamente qué conexión requiere comprobación física: la población de R4003/R4002 y la continuidad CN4906 pin 4 → DEBUG_UART0_RXD.

Respuestas Q1–Q12:
| Q | Respuesta |
|---|-----------|
| Q1 | **NO** — no identificada inequívocamente en hardware; solo candidato documental (CN4001 pin 9 vía R4003/R4002 XX) |
| Q2 | **NO** — el esquema documenta la intención (R4003/R4002 hacia CN4001 pin 9) pero ambas resistencias están `XX` (no montadas); sin continuidad demostrada |
| Q3 | **NO** — sin población de R4003/R4002 no hay camino eléctrico desde el Multi Terminal al BOOT_SERIAL_IN |
| Q4 | **NO** — no se determinó la condición exacte de activación; `0xf2915010` bit 1 es un estado externo leído, no un bit interno concondición documentada |
| Q5 | **NO** — no se distinguió si es condición eléctrica, secuencia UART o ambas |
| Q6 | **NO** — no se identificaron niveles eléctricos ni temporizaciones |
| Q7 | **NO** — R4003 está `XX` (no montado); la ruta CN4906/R4003 no es utilizable según las evidencias disponibles |
| Q8 | **NO** — no se encontró procedimiento externo documentado en cámaras Sony compatibles que se aplique a la A6000 |
| Q9 | **PARCIAL** — la cadena de R9 (memoria, checksum, salto) es válida estática+emulada; no demostrada en hardware |
| Q10 | **SÍ** — se puede proponer un procedimiento pasivo concreto y no destructivo (ver §12) |
| Q11 | Falta: identificación eléctrica del contacto UART (continuidad R4003→CN4001 pin 9, tensión DC, señal en osciloscopio) y prueba de que BOOT_SERIAL_IN se activa externamente |
| Q12 | **Acceso interno CN4906** — la ruta externa Multi Terminal está descartada con evidencia; CN4906 es la alternativa mejor sustentada, aunque su montaje y continuidad también requieren verificación física |

---

## 2. Estado heredado de R9/R10

### 2.1 Cadena BootROM → UART → escritura RAM → salto a RAM (R9)

| Elemento | Valor | Estado |
|----------|-------|--------|
| BootROM base | `0xffff0000` | VERIFICADO (binario, SHA `81a17e03…`) |
| Receptor serie | `FUN_ffff1062 → FUN_ffff0fa0 → FUN_ffff0876 → FUN_ffff0634` | VERIFICADO |
| MMIO entrada serie | `0xf2915010` bit 1 = BOOT_SERIAL_IN | VERIFICADO (literal) |
| MMIO GPIO baud | `0xf2910410` bit 22 (GPIO(4,RDATA)) | VERIFICADO (literal) |
| MMIO timer | `0xf240310c` | VERIFICADO (literal) |
| Vector de salto | `0xc0005000` → `0xc000500C` → `FUN_ffff0144` (`bx r0`) | VERIFICADO |
| Estructura paquete | `0xc0010218` | VERIFICADO |
| Config UART | `0xc0010004` / flag `0xc0010008` | VERIFICADO |
| eSRAM | `0xc0000000–0xc0100000` (16 MiB) | VERIFICADO (literales BootROM) |
| Polinomio CRC8 | `0xEDB88320` (cargado literalmente en `0xffff0c04`) | VERIFICADO |
| Escritura RAM (tipo 0) | `str valor,[dirección]`, sin validación de rango | VERIFICADO |
| Salto RAM (tipo 0xFFFF) | dirección 32 bits en `0xc000500C`, `bx r0` | VERIFICADO |
| Checksum iterativo | `acc = crc8_step((old_acc ^ byte) & 0xFF) ^ (old_acc >> 8)` | VERIFICADO |
| Init acumulador | `0xFFFFFFFF` en `0xffff0a20` | NEEDS-CONFIRMATION |

La cadena es **estática+emulada**, no demostrada en hardware físico.

### 2.2 USB Charger descartado (R10)

R10 identificó `054c:0994` como implementado por Darwin (FM3) con descriptor HID solo-Input de 1 byte. No hay canal host→dispositivo, no hay manejador de solicitudes de control identificado, no hay cadena a RAM ni a Updater Mode. **Decisión: abandonar provisionalmente USB Charger, priorizar BootROM UART.**

---

## 3. Reconstrucción de conexiones eléctricas

### 3.1 Fuente documental: manual de servicio Sony A6000 (ILCE-6000/6000L/6000Y, Level 3, Rev 1.1)

El manual de servicio `references/manuals/a6000_service_L3.pdf` (texto extraído en `a6000_service_L3.txt`) contiene el esquema eléctrico de la placa SY-1028. Las páginas relevantes son:

- **PDF 38 (impreso 6-38):** esquema del conector MULTI TERMINAL (CN4001) y huella de servicio CN4906.
- **PDF 50 (impreso 6-50):** distribución de componentes SIDE A (CN4906, IC6000).
- **PDF 51 (impreso 6-39):** distribución de componentes SIDE B (IC5700, CL5701/CL701/CL703-707).
- **PDF 23 (impreso 6-23):** diagrama de bloques del sistema.

### 3.2 Red BOOT_SERIAL_IN en el esquema (página 38)

El esquema documenta la siguiente red para la recepción serie del BootROM:

```
BIONZ IC6000 pin H21 ── BOOT_SERIAL_IN ──┬── R4003 (XX) ── DEBUG_UART0_RXD ──┬── CN4001 pin 9 (UART_RX/BOOT_IN, MULTI)
                                         │                                   │
                                         └── R4002 (XX) ─────────────────────┘
```

También existe un camino paralelo para `DEBUG_UART0_TXD`:

```
BIONZ ── DEBUG_UART0_TXD ── CM4008 ── CN4001 pin 8 (UART_TX/LANC_SIG, MULTI)
```

Y para `AD_JACK_IN`:

```
BOOT_SERIAL_IN ── CM4002 ── AD_JACK_IN ── CM4003 ── CN4001 pin 10
```

**Nota importante del esquema:** al pie del dibujo aparece `XX MARK: NO MOUNT` (marca XX: no montado). Tanto R4003 como R4002 llevan la marca XX.

### 3.3 Conector Multi Terminal CN4001 (página 37; **corregido en E26-R29**, ver `docs/capture/e26-r29-pinout-cn4001-cn4906-completo.md`)

| Pin | Señal | Origen en esquema | Montaje |
|-----|-------|-------------------|---------|
| 1 | USB_VBUS | F4001 (fusible 2A/36V) | — |
| 2 | USB_D- | USB_D-_UM | — |
| 3 | USB_D+ | USB_D+_UM | — |
| 4 | USB_ID | — | — |
| 5 | GND | — | — |
| 6 | D_3.1V/LANC_DC | — | R4008 (XX) |
| 7 | XRESET_REQ | — | — |
| 8 | UART_TX/LANC_SIG | DEBUG_UART0_TXD via CM4008 | — |
| 9 | UART_RX/BOOT_IN | DEBUG_UART0_RXD via R4002 (XX) / BOOT_SERIAL_IN via R4003 (XX) | **NO (R4002/R4003 XX)** |
| 10 | AD_JACK_IN | CM4002 / CM4003 | — |
| 11 | ROUT/XAELOCK | — | — |
| 12 | LOUT/XSHUT | XS_1 via R4004 (XX) | — |
| 13 | VIDEO | XS_2 via CM4004/CM4005 | — |
| 14 | AV_GND | — | — |
| 15 | XPWR_ON | — | — |
| 16-19 | REG_GND | masa/blindaje vía D4001 (XX) | — |

### 3.4 Huella de servicio CN4906 (página 38, SIDE A; **corregido en E26-R29**)

18 pines (no 32; los antiguos «31/32» pertenecían a otro conector de la misma hoja — el flex del disparador, `s21-claude-button-to-shutter-order.md`). Es un conector **combinado BIONZ + Darwin**: 11/12/15 unen la vía de servicio de BIONZ con el bus `_DWN` de Darwin (E26-R29 §3).

| Pin | Señal | Origen | Montaje |
|-----|-------|--------|---------|
| 1 | REG_GND | — | — |
| 2 | BOOT_MODE_1 | FIQ | R4910 (XX) |
| 3 | EVER_3.15V | — | — |
| 4 | UART_RXD_MSS | DEBUG_UART0_RXD | — |
| 5 | UART_TXD_MSS | DEBUG_UART0_TXD | — |
| 6 | UART_RXD_DWN | DWN_UART_RXD (Darwin) | — |
| 7 | UART_TXD_DWN | DWN_UART_TXD (Darwin) | — |
| 8 | NSRST | MD0_DWN (Darwin, MEDIA confianza) | — |
| 9 | TDO | TDO_DWN (Darwin) | — |
| 10 | RTCK | sin red externa | — |
| 11 | TCK(SWCLK) | SWCLK + TCK_DWN (unidos) | R4911 (XX) |
| 12 | TMS(SWDIO) | SWDIO + TMS_DWN (unidos) | R4912 (XX) |
| 13 | TDI | TDI_DWN (Darwin) | — |
| 14 | NTRST | TRST_DWN (Darwin) | — |
| 15 | DEBUG_MODE | VIO_FLD + XDWN_RESET (unidos) | R4913 (XX) |
| 16-18 | REG_GND | — | — |

CN4906 en sí aparece marcado como `XX` en la lista de repuestos (no suministrado, incluida en SY-1028 COMPLETE BOARD). Su montaje físico en esta unidad no está verificado.

### 3.5 BIONZ IC6000 (páginas 3264, 3806-3808)

| Pin | Señal | Notas |
|-----|-------|-------|
| H21 | BOOT_SERIAL_IN | Entrada serie BootROM |
| AB18 | UART0_RXD | → DEBUG_UART0_RXD |
| AB19 | UART0_TXD | → DEBUG_UART0_TXD |
| P7 | BOOT_MAIN | — |
| R31 | — | cerca de BOOT_SERIAL_IN |
| R6004 | 0.1u, XX | cerca de BOOT_SERIAL_IN (no montado) |

---

## 4. Mapa de pines y componentes

### 4.1 Tabla maestra de conexiones

| Referencia | Pin | Señal | Componente intermedio | Estado de montaje | Destino | Evidencia documental | Certidumbre |
|------------|-----|-------|----------------------|-------------------|---------|---------------------|-------------|
| BIONZ IC6000 | H21 | BOOT_SERIAL_IN | — | IC montado (no verificable sin abrir) | R4003, R6004 | Esquema pág. 38, líneas 3264 | ALTA (esquema) |
| R4003 | — | 0 Ω candidato BOOT_SERIAL_IN → DEBUG_UART0_RXD | XX (no montado) | NO montado | DEBUG_UART0_RXD | Esquema pág. 38, línea 6110 | ALTA (esquema dice XX) |
| R4002 | — | 0 Ω candidato DEBUG_UART0_RXD → CN4001 pin 9 | XX (no montado) | NO montado | CN4001 pin 9 | Esquema pág. 38, línea 6108 | ALTA (esquema dice XX) |
| DEBUG_UART0_RXD | — | Señal BIONZ UART0_RXD | R4003 (XX), R4002 (XX) | Ruta interrumpida | CN4001 pin 9, CN4906 pin 4 | Esquema pág. 38, líneas 6108-6110 | ALTA (esquema) |
| CN4001 | 9 | UART_RX/BOOT_IN (MULTI) | R4002 (XX), R4003 (XX) | Conector montado (presunción) | BootROM UART RX | Esquema pág. 38, línea 6109 | MEDIA (sin continuidad verificada) |
| CN4001 | 8 | UART_TX/LANC_SIG (MULTI) | CM4008 | — | BootROM UART TX | Esquema pág. 38, línea 6107 | MEDIA |
| CN4906 | 4 | UART_RXD_MSS | DEBUG_UART0_RXD | CN4906 XX (huella no suministrada) | BootROM UART RX | Esquema pág. 38, línea 6310 | BAJA (montaje no verificado) |
| CN4906 | 5 | UART_TXD_MSS | DEBUG_UART0_TXD | CN4906 XX | BootROM UART TX | Esquema pág. 38, línea 6314 | BAJA |
| CM4002 | — | AD_JACK_IN puente | — | — | CN4001 pin 10 | Esquema pág. 38, línea 6111 | MEDIA |
| CM4003 | — | AD_JACK_IN puente | — | — | CN4001 pin 10 | Esquema pág. 38, línea 6112 | MEDIA |
| R6004 | — | 0.1u cerca BOOT_SERIAL_IN | XX (no montado) | NO montado | — | Esquema pág. 38, línea 3270 | ALTA |

### 4.2 Advertencia crítica: CN4906 pin 9 ≠ Multi Terminal pin 9

El esquema documenta:

- **CN4906 pin 9** = TDO (SWD/JTAG, vía R4911 XX)
- **CN4001 pin 9** = UART_RX/BOOT_IN (MULTI, vía R4003/R4002 XX)

**No son el mismo contacto.** Asumir que CN4906 pin 9 y Multi Terminal pin 9 son equivalentes es incorrecto. La página 38 del manual los muestra en secciones distintas del esquema con señales y resistencias de interposición diferentes.

---

## 5. Análisis del selector BootROM

### 5.1 Registro y bits implicados

El BootROM lee `0xf2915010` bit 1 (`MISC_MODEREG`, `BOOT_SERIAL_IN`) en cuatro funciones:

| Función | Uso del bit |
|---------|-------------|
| `FUN_ffff0f82` | Lectura del bit |
| `FUN_ffff05da` | Lectura del bit (muestreo start bit) |
| `FUN_ffff0634` | Lectura del bit (recepción de byte) |
| `FUN_ffff0876` | Lectura del bit (bucle de recepción serie) |

### 5.2 Naturaleza del bit 1 de `0xf2915010`

**No se identificó ninguna instrucción que escriba `0xf2915010` bit 1.** El BootROM solo **lee** este bit. Esto indica que `BOOT_SERIAL_IN` es un **estado externo** (nivel físico en un pin), no una bandera de configuración interna.

`FUN_ffff0554` lee `0xf2910410` (GPIO(4,RDATA)) bit 22 para seleccionar el divisor de baud rate (dos caminos: A o B), pero no se demostró que bit 22 de GPIO(4,RDATA) sea el mismo contacto físico que bit 1 de `0xf2915010`.

### 5.3 Flujo de activación (reconstruido estáticamente)

```
Reset / encendido
        |
        v
  0xffff0000 (vectores ARM)
        |
        v
  FUN_ffff1062 (BootROM main entry)
        |
    bandera uVar2 != 0  (DAT_ffff12c0+0x10 bit 0)
        |              |
        v              v
  FUN_ffff0fa0    FUN_ffff028c (carga kernel)
  (wrapper receptor)
        |
        v
  FUN_ffff0876 (bucle recepción serie)
        |
   lee 0xf2915010 bit 1 (BOOT_SERIAL_IN)
        |
   si nivel bajo (start bit detectado)
        |
        v
   recibe 8 bits + paridad + stop
        |
   valida checksum CRC8
        |
   tipo 0 → almacena valor+dirección en RAM
   tipo 0xFFFF → almacena salto en 0xc000500C, luego FUN_ffff0144 (bx r0)
```

**Preguntas sin respuesta:**
1. ¿Qué nivel lógico en BOOT_SERIAL_IN hace que el BootROM entre al receptor serie? (alto/bajo, pulso, sostenido)
2. ¿Se requiere una ventana temporal antes de liberar reset?
3. ¿Depende del estado de BIONZ o Darwin?
4. ¿Es BOOT_SERIAL_IN un dato recibido, una señal de activación o ambas?

---

## 6. Condiciones para activar UART

### 6.1 Lo que se sabe (estático)

- El receptor serie lee `0xf2915010` bit 1 para detectar el start bit.
- No hay escritura conocida a `0xf2915010` bit 1 (es entrada externa).
- `FUN_ffff0554` lee GPIO(4,RDATA) bit 22 para elegir divisor de baud.
- Timeout de start bit: 0x3b (59) iteraciones sin transición → error 0x3002.
- Temporización de bits mediante timer `0xf240310c`.
- No hay sincronización explícita de baud rate; el remitente debe coincidir con la velocidad esperada (no determinada).

### 6.2 Lo que NO se sabe

| Pregunta | Estado |
|----------|--------|
| Nivel lógico que activa el receptor | NO DETERMINADO |
| Voltaje del pin (3.3V? 1.8V? 5V?) | NO DETERMINADO |
| Velocidad de baud del BootROM | NO DETERMINADA (Linux usa 115200, pero el BootROM puede diferir) |
| Secuencia de activación antes del reset | NO DETERMINADA |
| Dependencia de BIONZ/Darwin | NO DETERMINADA |

---

## 7. Compatibilidad del Multi Terminal

### 7.1 Evaluación de la ruta externa

| Criterio | Resultado | Evidencia |
|----------|-----------|-----------|
| Contacto físico del receptor en el conector | Multi Terminal pin 9 (UART_RX/BOOT_IN) | Esquema pág. 38 |
| Continuidad eléctrica demostrada | **NO** | R4003 (XX) y R4002 (XX) no montadas |
| Resistencia de ruta montada | **NO** | Ambas resistencias marcadas XX |
| Posibilidad de uso sin abrir la cámara | **NO** | Sin camino eléctrico poblado desde el conector hasta BOOT_SERIAL_IN |
| Señal TX disponible | Multi Terminal pin 8 (UART_TX/LANC_SIG) vía CM4008 | Esquema, sin continuidad verificada |
| Nivel eléctrico del pin | NO DETERMINADO | — |

### 7.2 Conclusión sobre el Multi Terminal

**No es posible utilizar el conector Multi Terminal externo para acceder al receptor BootROM UART sin modificar la placa**, porque R4003 y R4002 (las resistencias de 0 Ω que conectarían BOOT_SERIAL_IN al pin 9 del conector) están marcadas como no montadas (XX) en el esquema. Sin ellas, no hay continuidad eléctrica.

---

## 8. Comparación con conexiones internas

| Criterio | Opción A: Multi Terminal externo | Opción B: CN4906 interna |
|----------|----------------------------------|--------------------------|
| Acceso físico | Sin abrir la cámara | Requiere abrir/placa visible |
| Continuidad demostrada | NO (R4003/R4002 XX) | NO (montaje CN4906 no verificado) |
| Capacidad de recepción (RX) | Pin 9, pero ruta rota | Pin 4 (UART_RXD_MSS), ruta directa desde DEBUG_UART0_RXD |
| Capacidad de transmisión (TX) | Pin 8 vía CM4008 | Pin 5 (UART_TXD_MSS) |
| Activación de BootROM | NO (sin ruta eléctrica) | Posible si se confirma señal |
| Riesgo eléctrico | Bajo (no se puede conectar) | Medio (requiere acceso físico) |
| Soldadura necesaria | Sí (para romper la ruta rota) | No (si hay puntos de prueba) |
| Evidencia disponible | Esquema con XX | Esquema, sin montaje verificado |

**Si ninguna opción está demostrada**, la evidencia concreta que permitiría decidir es:
1. Medición de continuidad entre R4003 y CN4001 pin 9 (confirmar si realmente está sin soldar)
2. Medición de continuidad entre DEBUG_UART0_RXD y CN4906 pin 4
3. Verificación visual de si CN4906 está montado en la placa
4. Medición de tensión DC en CN4906 pin 4 con cámara apagada

---

## 9. Casos publicados de otras cámaras Sony

### 9.1 Búsqueda realizada

Se buscó documentación pública sobre:
- Sony BootROM UART recovery
- Sony A6000 boot serial / UART boot mode
- Sony Multi Terminal UART boot
- BOOT_SERIAL_IN Sony
- Sony BIONZ serial boot
- Sony camera UART bootloader
- CN4906 Sony A6000
- Sony BIONZ recovery mode

### 9.2 Casos encontrados

| Caso | Modelo | Método | Evidencia | Resultado | Aplicable a A6000 |
|------|--------|--------|-----------|-----------|-------------------|
| Sony-PMCA-RE issue #488 | A6000 original | Patrón 73, registros UART con errores Mumin/ECC | Testimonio en GitHub | No constituyó diagnóstico | No (otra cámara, sin restauración) |
| Comentario en #488 | ILCE-7RM2 | 3 largos + 2 cortos tras paquete modificado, registros LDEC offset 32 | Testimonio | Atribuido a bloques no alineados | No (modelo distinto) |
| Peter Wedege blog (2016) | A6000 Multi Terminal | M08=UART TX, M02=GND (numeración propia, advertida como invertida) | Análisis de protocolo | Sin verificación con esquema A6000 | No (sin cotejo de niveles/numeración) |

**Conclusión:** No se encontró ningún procedimiento externo documentado y verificable para activar BootROM UART desde un conector externo en cámaras Sony compatibles con la A6000. Los casos encontrados son testimonios de otros modelos o análisis sin verificación eléctrica.

---

## 10. Auditoría de supuestos de R9

### 10.1 Tamaño de eSRAM (inconsistencia A)

El intervalo `0xc0000000–0xc0100000` representa **1 MiB** (0x1000000 bytes), no 16 MiB. R9 citaba "16 MiB" basándose en headers CXD90014 (`CXD90014_ESRAM_BASE=0xc0000000`, `SZ_16M`), pero los headers de CXD90014 no están confirmados como aplicables a la A6000. El BootROM usa direcciones en `0xc0005xxx` y `0xc0010xxx`, lo que confirma que al menos los primeros ~64 KiB de esa región son RAM usable y ejecutable en tiempo de arranque.

**Corrección:** La región `0xc0000000–0xc0100000` es de 1 MiB. El salto a `0xc000500C` está dentro de esta región y es alcanzable con la dirección de 32 bits del paquete tipo 0xFFFF.

### 10.2 Checksum (inconsistencia B)

R8 usó polinomio placeholder `0x07`. R9 corrigió a `0xEDB88320` (cargado literalmente en `0xffff0c04`). Sin embargo:
- El valor init del acumulador (`0xFFFFFFFF` observado en `0xffff0a20`) **NEEDS-CONFIRMATION**.
- La regla de comparación final (¿acumulador == 0? ¿== byte recibido?) **NEEDS-CONFIRMATION**.
- No se verificó contra una captura real.

### 10.3 Salto indirecto (inconsistencia C)

R9 interpreta los 4 bytes `data_hi,data_lo,addr_hi,addr_lo` del paquete tipo 0xFFFF como una dirección de salto de 32 bits. El disassembly muestra `ldr r1,[sp,#0xc]` (carga de 32 bits) como dirección de salto. Esto hace alcanzable eSRAM (`0xc0005000`). **NECESITA CONFIRMACIÓN** del mapeo byte-a-byte exacto.

### 10.4 Región de carga sin sobrescribir la estructura de salto

El paquete tipo 0 puede escribir en cualquier dirección sin validación de rango. Si el emisor escribe en `0xc0005000` o `0xc000500C`, sobrescribiría el vector de salto o el target, impidiendo el salto posterior. **El emisor debe evitar escribir en `0xc0005000–0xc000500F`.**

---

## 11. Validaciones offline

### 11.1 Tests existentes (R9)

| Test | Resultado |
|------|-----------|
| `tests/test_e26_r9_uart_protocol.py` (13 tests) | 13/13 PASS |
| `tests/test_e26_r9_unicorn_ramjump.py` (6 tests) | 6/6 PASS |
| Total | 19/19 PASS |

### 11.2 Nueva validación: reconstrucción de pinout

Se creó `analysis/e26-recovery/r11-pinout-reconstruction.py` con tests en `tests/test_e26_r11_pinout.py` que validan:
- La extracción de conexiones desde el texto del esquema del manual de servicio
- Que R4003 y R4002 están marcadas XX (no montadas)
- Que CN4001 pin 9 = UART_RX/BOOT_IN y CN4906 pin 9 = TDO (no son el mismo contacto)
- Que CN4906 pin 4 = UART_RXD_MSS = DEBUG_UART0_RXD
- La reconstrucción de la red BOOT_SERIAL_IN

### 11.3 Validaciones pendientes (requieren captura real)

| Validación | Estado | Por qué |
|------------|--------|---------|
| Valor init del checksum | NEEDS-CONFIRMATION | No verificable sin captura |
| Regla de comparación final del checksum | NEEDS-CONFIRMATION | No verificable sin captura |
| Mapeo byte-a-byte del salto 32 bits | NEEDS-CONFIRMATION | No verificable sin captura |
| Velocidad de baud del BootROM | NO DETERMINADO | Requiere captura de señal |
| Nivel lógico del pin UART | NO DETERMINADO | Requiere medición física |
| Población de R4003/R4002 | NO VERIFICADO | Requiere inspección visual |

---

## 12. Procedimiento pasivo propuesto (no ejecutado)

### 12.1 Precondiciones (no cumplidas)

- [ ] Autorización física separada del usuario
- [ ] Cámara accesible (placa SY-1028 visible, cara identificada)
- [ ] Multímetro, osciloscopio o analizador lógico
- [ ] Adaptador USB-UART a 3.3V (solo si las medidas pasivas confirman señal)

### 12.2 Pasos (orden obligatorio)

1. **Identificación visual:** Confirmar placa SY-1028, cara visible (SIDE A: CN4906, IC6000; SIDE B: IC5700, CL5701/CL701/CL703-707). Identificar la cara actualmente visible (no se asume orientación).
2. **Localización de componentes:** Localizar R4003, R4002, CM4008, CN4001, CN4906 en la placa.
3. **Continuidad (sin alimentar):** Medir entre R4003 y CN4001 pin 9; entre R4002 y CN4001 pin 9; entre DEBUG_UART0_RXD y CN4906 pin 4.
4. **Resistencia a masa (sin alimentar):** CN4001 pin 9 vs GND; CN4906 pin 4 vs GND (detectar cortocircuitos).
5. **Tensión DC (con alimentación, cámara APAGADA):** Pin 9 vs GND (esperar 0-3.3V; si hay 5V, abortar). CN4906 pin 4 vs GND.
6. **Observación de señal (osciloscopio/analizador lógico):** Durante el encendido, buscar transiciones en CN4001 pin 9 y CN4906 pin 4.
7. **Lectura pasiva (solo si pasos 1-6 confirman señal):** Adaptador USB-UART a 3.3V, conexión solo RX (cámara TX → adaptador RX), nunca TX del adaptador a la cámara. Velocidad inicial 115200 8N1 (hipótesis desde Linux, no confirmada para BootROM).
8. **Registro reproducible:** Documentar todas las medidas con fecha, instrumento, rango y resultado.

### 12.3 Qué NO hacer (restricciones de seguridad)

- No conectar 5V directamente a ningún pin
- No conectar TX de adaptador serie a ningún pin sin confirmar voltaje y dirección
- No escribir NAND, no modificar firmware, no flashear
- No abrir la cámara sin autorización expresa
- No puentear resistencias no montadas (R4003, R4002, R4004, R4910-R4913)
- No alterar señales de reset ni de selección de arranque (BOOT_MODE_1, NSRST, DEBUG_MODE)
- No asumir 3.3V ni 115200 baudios sin verificación

### 12.4 Condición especial

La cámara no ha permanecido inmóvil durante la investigación. No basarse en supuestos sobre posición física, orientación o cara visible de la placa. Cualquier intervención deberá partir de una nueva identificación visual y eléctrica.

---

## 13. Riesgos y limitaciones

1. **Ausencia de continuidad eléctrica:** R4003 y R4002 están XX (no montadas). Sin ellas, el Multi Terminal pin 9 no está conectado a BOOT_SERIAL_IN.
2. **Montaje de CN4906 no verificado:** CN4906 aparece como XX en la lista de repuestos. Su presencia física en esta unidad no está confirmada.
3. **Nivel eléctrico desconocido:** No se asume 3.3V. Medir antes de conectar cualquier adaptador.
4. **Velocidad de baud desconocida:** 115200 es la velocidad de Linux, no confirmada para el BootROM.
5. **Activación del modo serie desconocida:** No se sabe qué nivel o secuencia activa el receptor BootROM.
6. **Cámara no inmóvil:** La cara visible de la placa y la posición física pueden haber cambiado entre sesiones.
7. **Sin pruebas físicas autorizadas:** Toda validación eléctrica requiere autorización separada.

---

## 14. Matriz de evidencias

| ID | Evidencia | Tipo | Estado | Ruta |
|----|-----------|------|--------|------|
| E1 | Esquema página 38: BOOT_SERIAL_IN → R4003 (XX) → DEBUG_UART0_RXD → CN4001 pin 9 | Documental | VERIFICADO (texto extraído) | `references/manuals/a6000_service_L3.txt:6107-6110` |
| E2 | Esquema página 38: R4002 y R4003 marcadas XX (no montadas) | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:6108,6110` |
| E3 | Esquema página 38: CN4001 pin 9 = UART_RX/BOOT_IN | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:6109` |
| E4 | Esquema página 38: CN4906 pin 9 = TDO (no UART_RX/BOOT_IN) | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:6324` |
| E5 | Esquema página 38: CN4906 pin 4 = UART_RXD_MSS = DEBUG_UART0_RXD | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:6310` |
| E6 | Esquema página 38: CN4906 marcado XX (huella no suministrada) | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:6296` |
| E7 | Esquema página 38: BIONZ IC6000 pin H21 = BOOT_SERIAL_IN | Documental | VERIFICADO | `references/manuals/a6000_service_L3.txt:3264` |
| E8 | BootROM lee `0xf2915010` bit 1 (BOOT_SERIAL_IN) | Binario (REA) | VERIFICADO | `analysis/e26-recovery/r7b-bootrom-rea.json` |
| E9 | BootROM no escribe `0xf2915010` bit 1 (solo lectura) | Binario (REA) | VERIFICADO | `analysis/e26-recovery/r7b-bootrom-rea.json` |
| E10 | `FUN_ffff0554` lee GPIO(4,RDATA) `0xf2910410` bit 22 para baud | Binario (REA) | VERIFICADO | `analysis/e26-recovery/r8-uart-parser.py` |
| E11 | R9 scripts: parser + Unicorn emulación (19/19 tests) | Script | VERIFICADO | `analysis/e26-recovery/r9-uart-protocol.py`, `r9-unicorn-ramjump.py` |
| E12 | R10: USB Charger 054c:0994 = Darwin, sin recuperación | Binario + físico | VERIFICADO | `docs/capture/e26-r10-usb-charger-recovery.md` |

---

## 15. Respuestas finales (Q1–Q12)

| # | Pregunta | Respuesta | Fundamento / prueba que falta |
|---|----------|-----------|-------------------------------|
| Q1 | ¿Se identificó inequívocamente el contacto físico de recepción BootROM UART? | **NO** | Solo candidato documental: CN4001 pin 9 vía R4003/R4002 XX. Falta identificación física en hardware. |
| Q2 | ¿Existe una conexión eléctrica documentada entre ese contacto y Sony Multi Terminal? | **NO** | El esquema documenta la intención (R4003/R4002 hacia CN4001 pin 9) pero ambas resistencias están XX (no montadas). Sin continuidad demostrada. |
| Q3 | ¿Es posible utilizar el contacto externo sin modificar la placa? | **NO** | Sin población de R4003/R4002 no hay camino eléctrico desde el Multi Terminal al BOOT_SERIAL_IN. |
| Q4 | ¿Se determinó cómo se activa la rama serie del BootROM? | **NO** | `0xf2915010` bit 1 es un estado externo leído; no se identificó condición de activación. |
| Q5 | ¿El receptor serie se activa mediante condición eléctrica, secuencia UART o ambas? | **NO** | No se distinguió. Falta captura de señal o documentación del comportamiento de arranque. |
| Q6 | ¿Se identificaron los niveles eléctricos y temporizaciones necesarios? | **NO** | Voltaje del pin y velocidad de baud del BootROM no determinados. |
| Q7 | ¿La ruta CN4906/R4003 es utilizable según las evidencias disponibles? | **NO** | R4003 está XX (no montado). CN4906 montaje no verificado. |
| Q8 | ¿Se encontró algún procedimiento externo documentado en cámaras Sony compatibles? | **NO** | Casos encontrados son testimonios de otros modelos sin verificación eléctrica. |
| Q9 | ¿La cadena de R9 sigue siendo válida después de auditar memoria, checksum y salto? | **PARCIAL** | Válida estática+emulada (19/19 tests). No demostrada en hardware. Corrección: eSRAM es 1 MiB, no 16 MiB. |
| Q10 | ¿Es posible proponer una prueba pasiva concreta y no destructiva? | **SÍ** | Ver §12. |
| Q11 | ¿Qué falta exactamente para intentar recibir datos reales del BootROM? | — | Identificación eléctrica del contacto UART (continuidad R4003→CN4001 pin 9, tensión DC, señal en osciloscopio) y prueba de activación de BOOT_SERIAL_IN. |
| Q12 | ¿La prioridad de R12 debe ser Multi Terminal externo o acceso interno CN4906? | **CN4906 interna** | La ruta externa está descartada con evidencia. CN4906 es la alternativa mejor sustentada, aunque su montaje y continuidad requieren verificación física. |

---

## 16. Recomendación para R12

**Decisión: Opción C** → Priorizar **acceso interno CN4906** (Opción B de la comparación §8).

**Justificación:**
1. La ruta externa Multi Terminal está **descartada con evidencia**: R4003 y R4002 están XX (no montadas), sin continuidad desde CN4001 pin 9 hasta BOOT_SERIAL_IN.
2. CN4906 pin 4 lleva `UART_RXD_MSS = DEBUG_UART0_RXD` directamente desde BIONZ, sin resistencia intermedia marcada XX en esa ruta específica.
3. Si CN4906 está montado en la placa (pendiente de verificación visual), ofrece la ruta más directa al receptor BootROM UART.

**Próximos pasos para R12 (sujeto a autorización física separada):**
1. Identificar visualmente la cara visible de la placa SY-1028 (no asumir orientación).
2. Verificar si CN4906 está montado.
3. Medir continuidad DEBUG_UART0_RXD → CN4906 pin 4 (sin alimentar).
4. Medir tensión DC en CN4906 pin 4 (cámara apagada).
5. Observar señal con osciloscopio durante el encendido.
6. Si hay señal, lectura pasiva solo RX a 3.3V.
7. No conectar TX del adaptador durante captura pasiva.

**No elegir Opción D** (descartar BootROM UART) basado solo en ausencia de resultados: la identificación eléctrica simplemente no se ha realizado aún.

---

## Scripts y pruebas

- `analysis/e26-recovery/r11-pinout-reconstruction.py` — reconstrucción y validación del pinout desde el esquema del manual de servicio.
- `tests/test_e26_r11_pinout.py` — tests automáticos para el script de reconstrucción (no tocan la cámara).