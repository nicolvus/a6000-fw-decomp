# E26-R8 — Sony A6000 BootROM / UART / BOSS / NAND Recovery Investigation

**Fecha:** 29-10-2026
**Repositorio:** `nicolvus/a6000-fw-decomp`, commit base `a8a182c9` en `origin/main`
**Alcance:** Exclusivamente offline. REA, desensamblado ARM/Thumb, binarios de firmware, análisis estático de protocolos.
**Binario BootROM:** `analysis/camera-dumps/updater-20261020-175427/bootrom.bin`, SHA-256 `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026`, 24 576 bytes, base `0xffff0000`, modo Thumb (salvo vectores de excepción en ARM al inicio).
**Script analizador:** `analysis/e26-recovery/r8-uart-parser.py` (parser offline, autotest incluido).

---

## 1. Resumen ejecutivo

R8 investiga tres vías de recuperación para una Sony A6000 con firmware/NAND dañado, idealmente sin arranque completo de Linux:

1. **Prioridad A — BootROM y UART:** reconstrucción del receptor serie de BootROM, identificación de pines físicos candidatos, desarrollo de parser offline de protocolo.
2. **Prioridad B — BOSS/MuMin y NAND:** evaluación de escritura selectiva en `nflasha3` preservando otras regiones.
3. **Prioridad C — INFO6:** estado de las 21 páginas sin fuente identificada.

**Resultado global:** no se ha encontrado ninguna ruta de recuperación demostrable sin arranque de Linux. El receptor serie de BootROM existe estáticamente pero sin red física identificada ni cadena de escritura NAND. Las escrituras NAND (BOSS/MuMin/LLD → ARM7) requieren entorno Linux inicializado. INFO6 sigue sin fuente.

Respuestas a las seis preguntas de cierre:

| # | Pregunta | Respuesta | Alcance |
|---|----------|-----------|---------|
| 1 | ¿Existe un receptor UART en BootROM con entrada y protocolo identificados? | **SÍ** | `FUN_ffff1062` → `FUN_ffff0fa0` → `FUN_ffff0876` → `FUN_ffff0634`; MMIO `0xf2915010` bit 1; tipos de paquete 0 / 0xFFFF; checksum XOR + tabla CRC8 |
| 2 | ¿Podemos identificar cómo acceder físicamente a ese UART en una Sony A6000? | **NO DEMOSTRADO** | Candidato: GPIO(4,RDATA) = `0xf2910410` vía R4003 XX en esquema CN4906 pin 9 (MULTI UART_RX/BOOT_IN); no hay continuidad verificada, ni niveles, ni población |
| 3 | ¿Existe una función de lectura de memoria o NAND accesible mediante ese protocolo? | **NO DEMOSTRADO** | El protocolo acepta tipo 0 (dato + dirección) y tipo 0xFFFF (salto a dirección); no se demuestra lectura de memoria o NAND desde el receptor serie |
| 4 | ¿Existe una cadena comprobable de escritura selectiva en `nflasha3`? | **NO DEMOSTRADO** | Primitivas de escritura existen (`mumin_devif_write_pages_in_pblk` 0x153dc → `boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800)`) pero solo en entorno Linux; no hay aislamiento de partición ni preservación de metadatos/ECC |
| 5 | ¿Puede ejecutarse alguna de estas rutas sin arrancar Linux? | **NO DEMOSTRADO** | El receptor serie de BootROM es pre-Linux pero sin cadena de escritura NAND demostrada; las escrituras NAND requieren Linux |
| 6 | ¿Se logró identificar el origen de las 21 páginas INFO6? | **NO** | Cerrado con límite documental en R7; sin fuente en BLDR, volcados RAM ni otros respaldos |

**Recomendación para R9:** intentar lectura pasiva UART en el candidato físico identificado (CN4906 pin 9 vía R4003, GPIO(4,RDATA) `0xf2910410`) únicamente con autorización física separada y mediciones no destructivas (osciloscopio/analizador lógico, sin conectar TX de 5V/3.3V sin confirmar voltaje). Si no hay señal, declarar Prioridad A cerrada con límite físico y enfocar R9 en evidencia documental adicional o aceptación de que no hay ruta de recuperación sin nflasha3.

---

## 2. Hallazgos nuevos respecto de R7

R7 estableció que no existe ruta de restauración antes de `nflasha3`. R8 añade:

1. **Reconstrucción completa del receptor serie de BootROM** con grafo de llamadas, registro MMIO exacto, formato de paquete, códigos de retorno, checksum y validación por autotest offline (`analysis/e26-recovery/r8-uart-parser.py`, 6/6 pruebas pasan).
2. **Tabla de registros MMIO y candidatos TX/RX** con direcciones exactas del disassembly, no inferidas de otros dispositivos.
3. **Protocolo BootROM formalmente especificado** (tipo 0 = dato, tipo 0xFFFF = salto, checksum XOR/CRC8, timeouts por contador de iteraciones 0x3b).
4. **Evaluación de lectura de memoria/NDN vía protocolo:** no demostrada. El protocolo almacena valores y direcciones, y salta a direcciones en RAM (`0xc0005000` → `0xc000500C`), pero no hay función de lectura demostrada.
5. **BOSS/MuMin escritura selectiva:** confirmado que no existe cadena comprobable sin Linux; `boss_hw_nandc_recovery_check` (0x17b8c) maneja errores de controlador NAND, no es selección de UPDATER.
6. **INFO6:** sin cambios respecto de R7; sigue sin fuente identificada.

No se repiten investigaciones cerradas de R7 (COLD bucle, UPDATER = carga kernel desde dev1, escrituras NAND solo en Linux, residuo TPZL sin rechazo demostrado).

---

## 3. Grafo BootROM → UART → comandos

```
                           Reset / encendido
                                       |
                                       v
                              0xffff0000 (vectores ARM)
                                       |
                                       v
                              FUN_ffff1062 (BootROM main entry)
                                       |
            +--------------------------+--------------------------+
            |                          |                          |
      bandera uVar2 != 0          bandera uVar2 == 0        (otras rutas)
      (DAT_ffff12c0+0x10 bit 0)   (arranque normal)             |
            |                          |                          |
            v                          v                          v
      FUN_ffff0fa0()           FUN_ffff028c()                 ...
   (receptor serie wrapper)   (carga kernel)                     |
            |                          |                          |
            v                          v                          v
      FUN_ffff0876()           FUN_ffff04b6() → salto al kernel
   (bucle recepción serie)     (COLD/UPDATER)                      |
            |                                                      |
      +-----+-----+----------+----------+                         v
      |     |     |          |          |              FUN_ffff03b74 (bucle LED)
  tipo 0  tipo    |  error   |  tipo    |                         |
  (0x0000) 0xFFFF |  codes   | 0xFFxx   |                         |
      |     |     |          |          |                         |
      v     v     v          v          v                         |
   almacena  almacena     log +        log +                      |
   valor +   dirección    ret code     ret code                   |
   dirección |   de salto   (timeout,   (general, checksum,       |
   (0xc0010218)|   (0xc000500C)         parity, stop)              |
      |     |                         |                            |
      +-----+-----+-------------------+                            |
            |                                                      |
            v                                                      |
   FUN_ffff0144()  ← carga 32 bits desde 0xc0005000, BX r0       |
   (salto indirecto a RAM)                                         |
            |                                                      |
            v                                                      |
   Código cargado por UART ejecuta en RAM                         |
   (sin demostración de lectura/escritura NAND)                   |
                                                                    |
   Ninguna rama → lectura de NAND → restauración selectiva        |
   Ninguna rama → fallback de arranque                            |
   Ninguna rama → retorno al selector de modo                     |
```

**Flujo detallado de recepción de un byte (FUN_ffff0634):**

```
FUN_ffff0634(byte_count_limit, ...):
  │
  ├─ espera start bit: lee 0xf2915010 bit 1, compara con valor previo
  │  ├─ si no cambia dentro de 0x3b iteraciones → retorna 0x3002 (timeout)
  │  └─ si cambia → procede a muestreo de bits
  │
  ├─ para cada uno de 8 bits:
  │  ├─ espera transición (FUN_ffff05da, temporizado por 0xf240310c)
  │  ├─ si falla temporización → retorna 0x3003 (paridad) / 0x3004 (stop)
  │  └─ acumula bit en resultado (XOR con checksum corrido)
  │
  ├─ bit de paridad / stop (9º bit):
  │  ├─ espera y valida (FUN_ffff05da)
  │  └─ si falla → retorna 0x3004
  │
  ├─ checksum: tabla CRC8 (FUN_ffff0c00) sobre acumulador XOR
  │  └─ si no coincide → retorna 0x100d (checksum error)
  │
  └─ retorna 0 (éxito, byte almacenado en estructura 0xc0010218)
```

---

## 4. Tabla de registros MMIO y candidatos TX/RX

### 4.1 Registros MMIO utilizados por el receptor serie (VERIFICADO en disassembly)

| Dirección | Nombre | Uso en BootROM | Fuente |
|-----------|--------|----------------|--------|
| `0xf2915010` | `MISC_MODEREG` (bit 1 = `BOOT_SERIAL_IN`) | Lectura del bit de entrada serie en `FUN_ffff0f82`, `FUN_ffff05da`, `FUN_ffff0634`, `FUN_ffff0876` | REA literals `0xffff0968` = `0xf2915000`, offset +0x10 |
| `0xf2910410` | `GPIO(4, RDATA)` | Lectura en `FUN_ffff0554` para decidir configuración de baud rate (camino A vs B) | REA literals `0xffff094c` = `0xf2910410` |
| `0xf2403000` | Timer base | Contador usado para temporización de bits en `FUN_ffff0f52` (offset +0x10c = `0xf240310c`) | REA literals `0xffff0964` = `0xf2403000` |
| `0xc0005000` | Jump vector storage | `FUN_ffff0144` carga desde aquí y hace `BX r0` | REA literals `0xffff014c` = `0xc0005000`, `0xffff0bf8` = `0xc0005000` |
| `0xc000500C` | Jump target storage | Tipo 0xFFFF almacena dirección de salto aquí | `FUN_ffff0b7c`: `str r1, [r2, #0xc]` donde r2=0xc0005000 |
| `0xc0010004` | UART config / mode pointer | `FUN_ffff0554` escribe tabla de configuración; `FUN_ffff0bd4` lee `*0xc0010004` | REA literals `0xffff0bfc` = `0xc0010004` |
| `0xc0010008` | Mode flag | `FUN_ffff0b82`: almacena 1 después de paquete tipo 0xFFxx | Inferred from disassembly |
| `0xc0010218` | Paquete recibido | Estructura de 6 campos donde `FUN_ffff0634` almacena bytes recibidos | REA literals `0xffff0950` = `0xc0010218` |

### 4.2 Configuración de UART (FUN_ffff0554, 0xffff0554)

La función lee `0xf2910410` (GPIO(4,RDATA)), hace `ubfx r0, r0, #0x15, #1` (bit 22) y toma dos caminos:

| Camino | Condición | Baud divisor lo | Baud divisor hi | Campo +8 | Campo +0xC | Campo +0x10 |
|--------|-----------|-----------------|-----------------|----------|------------|-------------|
| A | bit 22 de `0xf2910410` = 1 | 0x04A0 | 0x038D | 0x070A | 0x033E | 0x0001 |
| B | bit 22 de `0xf2910410` = 0 | 0x0E74 | 0x0B18 | 0x0F05 | 0x0A23 | 0x0014 |

**Interpretación:** los valores 0x04A0/0x038D y 0x0E74/0x0B18 parecen ser divisores de baud rate de dos configuraciones distintas (posiblemente 115200 vs otra velocidad, o dos pines UART distintos). No se ha verificado empíricamente qué velocidad corresponde a cada valor.

**Línea de kernel del shell.txt (cámara en funcionamiento):**
```
console=ttyAM0,115200n8
cfg.uart=5
```
Esto confirma que el puerto serie del kernel usa 115200 baud, 8 bits, sin paridad. No se ha demostrado que el BootROM use la misma velocidad.

### 4.3 Candidatos físicos TX/RX (NO DEMOSTRADO)

| Candidato | Fundamento | Limitación |
|-----------|------------|------------|
| **GPIO(4,RDATA) = `0xf2910410`** | Leído por `FUN_ffff0554` para seleccionar configuración de UART; regs-gpio.h define `GPIO_REG(4,RDATA)` = `(4<<8)+0x10` = `0x410` sobre `GPIO_BASE=0xf2910000` → `0xf2910410` | Es una dirección MMIO, no un pin físico. No hay mapeo pin→registro verificado para la A6000 |
| **CN4906 pin 9 (MULTI, UART_RX/BOOT_IN)** | Manual de servicio A6000, página 37: BOOT_SERIAL_IN pasa por R4003 (marcado XX, no poblado verificado) al nodo "MULTI pin 9 UART_RX/BOOT_IN". Alternativa CM4003 en paralelo. DEBUG_UART0_RXD llega por R4002 (también XX). | El dibujo no prueba que R4003/CM4003 estén poblados. No hay continuidad eléctrica verificada. No hay niveles de tensión. |
| **CN4906 pin 10 (AD_JACK_IN)** | Mismo diagrama, pin separado. | No asociado con BOOT_SERIAL_IN en el esquema. |

**Fundamento de cada candidato:**
- GPIO(4,RDATA): evidencia lógica (el BootROM lee este registro para configurar UART). No evidencia física.
- CN4906 pin 9: evidencia documental (manual de servicio). No evidencia eléctrica.

**Procedimiento de comprobación eléctrica no destructiva (plan, no ejecutado):**
1. Identificar la placa SY-1028 (SIDE A: CN4906, IC6000; SIDE B: IC5700, CL5701/CL701/CL703-707).
2. Localizar R4003 (0 Ω candidato para BOOT_SERIAL_IN) y R4002 (DEBUG_UART0_RXD).
3. Medir continuidad entre R4003 y el pad de CN4906 pin 9 con multímetro (placa sin alimentar).
4. Medir resistencia entre CN4906 pin 9 y masa (sin alimentar, para detectar cortocircuitos).
5. Con alimentación conectada pero cámara apagada, medir tensión DC en CN4906 pin 9 respecto a masa (esperar 0-3.3V, nunca 5V).
6. Con osciloscopio/analizador lógico, observar actividad en pin 9 durante encendido (buscar bits de start, baud rate aproximado).
7. Solo si hay señal clara, intentar lectura pasiva con adaptador USB-UART a 3.3V (nunca 5V).

**Restricción de seguridad:** no conectar interfaces serie de 5V o 3.3V directamente a contactos cuyo voltaje no se ha confirmado. Empezar por mediciones pasivas.

---

## 5. Reconstrucción del protocolo BootROM

### 5.1 Formato de frame (reconstruido desde disassembly)

```
Offset  Campo         Tamaño  Descripción
0       type_hi       1 byte  Byte alto del tipo de paquete
1       type_lo       1 byte  Byte bajo del tipo de paquete
2       data_hi       1 byte  Dato/valor alto (tipo 0) o salto_lo (tipo 0xFFFF)
3       data_lo       1 byte  Dato/valor bajo (tipo 0) o salto_hi (tipo 0xFFFF)
4       addr_hi       1 byte  Dirección alta (tipo 0) o reservado (tipo 0xFFFF)
5       addr_lo       1 byte  Dirección baja (tipo 0) o reservado (tipo 0xFFFF)
6       checksum      1 byte  XOR acumulado + tabla CRC8 (FUN_ffff0c00)
```

### 5.2 Tipos de paquete

| Tipo | Significado | Acción en BootROM | Retorno de `FUN_ffff0876` |
|------|-------------|-------------------|---------------------------|
| `0x0000` | Dato | Almacena valor (2B) + dirección (2B) en estructura `0xc0010218`, almacena 1 en `0xc0010004` | `0x0000` (éxito) |
| `0xFFFF` | Salto | Almacena dirección de salto en `0xc000500C`, flag en `0xc0010008` | `0x3001` (salto a RAM) |
| `0xFF01` | Error timeout | No start bit dentro de 0x3b iteraciones | `0x3002` |
| `0xFF02` | Error paridad | Bit de paridad incorrecto | `0x3003` |
| `0xFF03` | Error stop | Bit de stop incorrecto | `0x3004` |
| `0xFF04` | Error general | Error de protocolo genérico | `0x100C` |
| `0xFF05` | Error tamaño | Paquete > 0x1000 bytes | `0x2004` |
| `0xFF06` | Error modo | Estado de modo inválido | `0x2005` |

### 5.3 Checksum

El algoritmo reconstruido (ver `r8-uart-parser.py`):

1. XOR-acumular todos los bytes de datos (6 bytes: type_hi, type_lo, data_hi, data_lo, addr_hi, addr_lo)
2. Aplicar tabla CRC8 (función `FUN_ffff0c00`, polinomio **no identificado** en el disassembly — placeholder en el parser)
3. XOR del resultado CRC con el acumulador desplazado (instrucciones `0xffff078c-0xffff0794`: `eor.w r0, r0, r1, lsr #8`)

**Limitación:** el polinomio exacto de la tabla CRC8 no se ha extraído de la ROM. El parser usa un placeholder (polinomio 0x07) que debe verificarse contra capturas reales antes de confiar en la validación de checksum.

### 5.4 Timeouts y sincronización

- **Timeout de start bit:** 0x3b (59) iteraciones del bucle principal sin detectar transición en `0xf2915010` bit 1 → error 0x3002
- **Temporización de bits:** uso del timer en `0xf240310c` (offset +0x10c sobre `0xf2403000`) con `FUN_ffff0f52` (poll hasta que el contador alcance el valor esperado) y `FUN_ffff0f72` (comparación)
- **No hay sincronización explícita de baud rate:** el receptor espera transiciones en la línea de datos; el remitente debe usar la misma velocidad que el BootROM espera (no determinada)

### 5.5 Capacidades demostradas vs. no demostradas

| Capacidad | ¿Demostrada en binario? | Evidencia |
|-----------|------------------------|-----------|
| Recibir bytes por serie | SÍ | `FUN_ffff0634`, `FUN_ffff0876` |
| Almacenar valor recibido en RAM | SÍ | `0xc0010218`, `0xc0010004` |
| Saltar a dirección en RAM (tipo 0xFFFF) | SÍ | `FUN_ffff0144`: `ldr r0, [0xc0005000]; BX r0` |
| Leer memoria mediante el protocolo | NO | No hay función de lectura en el receptor serie |
| Escribir NAND mediante el protocolo | NO | No hay cadena desde receptor serie a operaciones NAND |
| Ejecutar código arbitrario | PARCIAL | Salto a dirección en RAM almacenada vía tipo 0xFFFF, pero el código debe estar ya en RAM |

---

## 6. Grafo BOSS/MuMin → NAND

### 6.1 Cadena de llamadas de escritura (VERIFICADA en binario)

```
Escritura de páginas:
  muminblk_request (0x1020c) [nand.ko]
    → mumin_ext_write_scts (0x26e80)
      → __mumin_write_ltus (0x139fc)
        → mumin_ebm_write_ltus (0x1a638)
          → mumin_devif_write_pages_in_pblk (0x153dc) [lld.ko]
            → boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800, ...) [ARM7 dispatch]

Borrado:
  mumin_devif_erase_pblk (0x10b64) [lld.ko]
    → boss_hw_arm7_comm_set_firmware_api_param(0x0c, ...)

IOCTL de bloque dispositivo:
  muminblk_ioctl (0x104b0)
    → nand_ioc_pwrite_normal (0x284bc) → mumin_devif_write_pages_in_pblk
    → nand_ioc_perase_normal (0x28298) → mumin_devif_erase_pblk
    → nand_ioc_lerase (0x28624) → mumin_ext_erase_lblk
```

### 6.2 `mumin_devif_write_pages_in_pblk` (0x153dc) — verificación

```c
undefined1 *mumin_devif_write_pages_in_pblk(
    int param_1,   // puntero de dispositivo
    undefined4 param_2,  // ?
    int param_3,   // ?
    int param_4,   // ?
    int param_5    // ?
) {
  if ((param_1 == 0 || param_3 == 0) || (param_4 == 0 || param_5 == 0))
    return error 0xffffd8ef;
  
  iVar1 = boss_lld_udm_get_init_flag();
  if (iVar1 == 0)
    return error 0xffffd8e8;  // dispositivo no inicializado
  
  boss_lld_udm_mutex(1);  // tomar mutex — REQUIERE ENTORNO LINUX
  
  iVar1 = boss_hw_arm7_comm_get_firmware_status();
  if (iVar1 == 3) {
    boss_lld_udm_mutex(0);
    return error 0xffffd8ea;  // firmware en estado 3 (no acepta escritura)
  }
  
  puVar2 = FUN_00015144(param_1, param_2, param_3, param_4, param_5);
  boss_hw_nandc_recovery_check();  // comprobación de recuperación de controlador NAND
  boss_lld_udm_mutex(0);  // liberar mutex
  
  return puVar2;
}
```

**Condiciones previas para escritura:**
1. `param_1`..`param_5` todos non-NULL
2. `boss_lld_udm_get_init_flag()` != 0 (dispositivo inicializado — solo en Linux)
3. `boss_hw_arm7_comm_get_firmware_status()` != 3 (ARM7 no en estado de bloqueo)
4. Mutex tomado y liberado (primitiva de kernel Linux)
5. `FUN_00015144` ejecuta la operación de escritura real a través de ARM7

### 6.3 `boss_hw_nandc_recovery_check` (0x17b8c)

- Se activa solo cuando `param_1 == -0x20001` o `param_1 == -0x2713` (códigos de error específicos del controlador NAND)
- Obtiene direcciones base de ARM7 SRAM, clkrst3 y registros NAND
- Escribe `0x1f01` en `clkrst3 + 0xd8`, `0` en `ARM7_SRAM + 0x3f40`, espera (`__const_udelay(0x1a36e)`), escribe `0x1f00` en `clkrst3 + 0xd4`
- Lee registro NAND +0x410, hace `tst r3, #0x2000`
- Si bit 0x2000 no está set: bucle de espera con `FUN_c01f1b07c` (udelay) comparando con umbral en `0x17d18`
- **Interpretación:** manejo interno de recuperación del controlador NAND ante errores específicos. No es selección de UPDATER, no es recuperación de arranque, no es escritura selectiva de partición.

### 6.4 Evaluación de recuperación NAND (respuestas por requerimiento)

| # | Requisito | ¿Demostrado? | Cadena de llamadas | Evidencia |
|---|-----------|--------------|-------------------|-----------|
| 1 | Lectura de `nflasha3` | NO | — | No hay función de lectura desde BootROM o receptor serie |
| 2 | Escritura en `nflasha3` | PARCIAL (solo Linux) | `muminblk_request` → ... → `boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800)` | `r7-nand-rea.json`, `r7-lld-rea.json` |
| 3 | Borrado selectivo | PARCIAL (solo Linux) | `mumin_devif_erase_pblk` → `boss_hw_arm7_comm_set_firmware_api_param(0x0c, …)` | `r7-lld-rea.json` |
| 4 | Preservación de metadatos | NO | — | No hay aislamiento de partición, no hay gestión de OOB/ECC por partición |
| 5 | Comprobación de integridad | NO | — | `boss_hw_nandc_recovery_check` maneja errores del controlador, no verifica integridad de partición |
| 6 | Funcionamiento sin Linux | NO | — | Todas las operaciones requieren `muminblk` (mutex, kmem_cache, etc.) del kernel |

**Conclusión:** no existe cadena comprobable de escritura selectiva en `nflasha3` preservando metadatos, ECC, bloques defectuosos y calibraciones. Las operaciones de escritura/borrado existen pero requieren el entorno Linux inicializado y no aíslan particiones.

---

## 7. Estado de INFO6

| Atributo | Valor | Clasificación |
|----------|-------|---------------|
| Región | die0, plane1, block2, pages 0–20 | Documentado en R7 |
| Runtime esperado | 0xc0205800–0xc0210000 | Inferencia desde tabla INFO |
| Tamaño | 21 páginas | Documentado en R7 |
| Fuente identificada | NINGUNA | NO DEMOSTRADO |
| En BLDR `bootloader.bin` | Solo primeras 43 páginas (prefijo) | VERIFICADO (SHA-256 cotejado) |
| En volcados RAM (2×1 GiB) | No (anclas de 64 B no coincidieron) | VERIFICADO (búsqueda negativa) |
| En otras copias de Loader3 | No encontradas | NO ENCONTRADO |
| Firmware oficial A6000 | No disponible localmente | NO DISPONIBLE |

**Conclusión (sin cambios desde R7):** no hay fuente adecuada para recuperar las 21 páginas INFO6. Cerrado con límite documental. No se fabrica contenido faltante.

---

## 8. Evidencias reproducibles

### 8.1 Hashes de artefactos

| Artefacto | Ruta | SHA-256 |
|-----------|------|---------|
| BootROM | `analysis/camera-dumps/updater-20261020-175427/bootrom.bin` | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| Bootloader | `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` | `eb420385120f2cd7c9b071f67ce5808721b7de44fb78e2884a856e3c438a327f` |
| Backup | `analysis/camera-dumps/updater-20261020-175427/backup.bin` | `48b6dc423127d38bd7b8043197f1bdfdc9c80f9575ec24ae8a409c992ecfbb9a` |
| Parser UART | `analysis/e26-recovery/r8-uart-parser.py` | (ver commit) |
| R7 REA cold | `analysis/e26-recovery/r7b-cold-rea.json` | (existente) |
| R7 REA bootrom | `analysis/e26-recovery/r7b-bootrom-rea.json` | (existente) |
| R7 REA ROM protocol | `analysis/e26-recovery/r7b-rom-protocol-rea.json` | (existente) |
| R7 REA nand | `analysis/e26-recovery/r7-nand-rea.json` | (existente) |
| R7 REA lld | `analysis/e26-recovery/r7-lld-rea.json` | (existente) |
| R7 REA mumin | `analysis/e26-recovery/r7-mumin-rea.json` | (existente) |
| R7 REA recovery check | `analysis/e26-recovery/r7-recovery-check-rea.json` | (existente) |

### 8.2 Scripts y procedimientos de reproducción

1. **Parser UART offline:** `python3 analysis/e26-recovery/r8-uart-parser.py --selftest` → 6/6 pruebas pasan
2. **Parser UART con datos sintéticos:** `python3 analysis/e26-recovery/r8-uart-parser.py "000012345678XX"` (donde XX = checksum válido)
3. **REA sobre bootrom.bin:** usar `analysis/rea-independent/bin/session_daemon.py` + `bin/q.py` (sesión única, ~8 min en frío, consultar por lotes)

### 8.3 Distinción VERIFICADO / NO DEMOSTRADO

- **VERIFICADO:** demostrado por bytes e instrucciones del bootrom.bin desensamblado (receptor serie, formato de paquete, salto a RAM, MMIO direcciones)
- **NO DEMOSTRADO:** acceso físico al UART, lectura de NAND vía protocolo, escritura selectiva de nflasha3, origen de INFO6
- **DESCARTADO:** UPDATER como entorno de recuperación independiente (es igual que COLD: carga kernel y salta); BOSS/MuMin sin Linux (requiere mutex y kmem_cache del kernel)

---

## 9. Plan de diagnóstico físico no destructivo

### 9.1 Precondiciones (no cumplidas actualmente)

- [ ] Autorización física separada del usuario
- [ ] Cámara accesible (placa SY-1028 visible)
- [ ] Multímetro, osciloscopio o analizador lógico
- [ ] Adaptador USB-UART a 3.3V (solo si las medidas pasivas confirman señal)

### 9.2 Pasos (orden obligatorio, sin saltar)

1. **Identificación:** confirmar placa SY-1028, cara visible (SIDE A o B), ubicación de CN4906
2. **Continuidad (sin alimentar):** medir entre R4003 y CN4906 pin 9; entre R4002 y mismo nodo
3. **Resistencia a masa (sin alimentar):** CN4906 pin 9 vs GND (detectar cortocircuitos)
4. **Tensión DC (con alimentación, cámara APAGADA):** pin 9 vs GND (esperar 0-3.3V; si hay 5V, abortar)
5. **Observación de señal (osciloscopio/analizador lógico):** durante encendido, buscar transiciones en pin 9
6. **Lectura pasiva (solo si pasos 1-5 confirman señal):** adaptador USB-UART a 3.3V, conexión solo RX (cámara TX → adaptador RX), nunca TX del adaptador a la cámara
7. **Documentación:** registrar todas las medidas con fecha, instrumento, rango y resultado

### 9.3 Qué NO hacer (restricciones de seguridad)

- [ ] No conectar 5V directamente a ningún pin de la cámara
- [ ] No conectar TX de un adaptador serie a ningún pin de la cámara sin confirmar que es entrada y el voltaje es compatible
- [ ] No escribir NAND, no modificar firmware, no flashear
- [ ] No abrir la cámara sin autorización expresa
- [ ] No realizar mediciones que requieran alimentar circuitos no diseñados para ello

---

## 10. Conclusión de viabilidad de recuperación

**No existe una ruta de recuperación técnicamente demostrable sin arranque de Linux** basada en la evidencia estática actual.

| Vía | Estado | Por qué no es viable |
|-----|--------|---------------------|
| BootROM UART (tipo 0 / 0xFFFF) | Parcial (solo lógica) | Sin red física identificada; sin función de lectura NAND; sin cadena de escritura NAND |
| Escritura selectiva nflasha3 | NO DEMOSTRADO | Solo en entorno Linux; sin aislamiento de partición; sin preservación de metadatos/ECC |
| UPDATER (modo 3) | CERRADO (R7) | Carga kernel desde nflasha1 y salta; no es entorno independiente |
| COLD (modo 0xc) | CERRADO (R7) | Fallo → bucle LED infinito sin retorno |
| INFO6 recuperación | CERRADO CON LÍMITE (R7) | Sin fuente identificada para 21 páginas |

**La única vía teóricamente identificada** (ya en R7) es el selector `updater/mode` en Loader3, pero requiere:
1. BOSS inicializado (`FUN_c01f0cca` completo)
2. Dispositivo 2 con FAT montado (para leer `updater/mode`)
3. Dispositivo 1 con FAT montado (para leer `vmlinux.bin`+`initrd.img`)
4. `FUN_c01f068a()` con éxito (carga de archivos desde FAT)
5. Productor externo que cree `updater/mode` antes del arranque (no identificado)

Si se agotan las rutas estáticas razonables, las dependencias físicas irreducibles son: firmware ARM7 actual, red física del receptor serie BootROM, y una fuente para INFO6. Ninguna está disponible en el estado actual.

---

## 11. Próximos experimentos priorizados

| Prioridad | Experimento | Incertidumbre que resuelve | Costo | Dependencias |
|-----------|-------------|---------------------------|-------|--------------|
| 1 | Lectura pasiva UART en CN4906 pin 9 (osciloscopio/analizador lógico) | ¿Existe señal serie en el candidato físico? | Medio (requiere acceso físico) | Autorización física, instrumentos |
| 2 | Extraer tabla CRC8 real de bootrom.bin (offset de FUN_ffff0c00) | Validar checksum del parser UART | Bajo (offline) | REA session |
| 3 | Buscar `updater/mode` productor en binarios del initrd | ¿Cómo se activa UPDATER externamente? | Medio (offline) | Archivos de initrd disponibles |
| 4 | Buscar firmware ARM7 actual en respaldos | ¿Existe código ARM7 para operaciones NAND pre-Linux? | Medio (offline) | Respaldos disponibles |
| 5 | Buscar fuente de INFO6 en otros respaldos de firmware Sony | ¿Existen las 21 páginas faltantes? | Bajo (offline, web search) | Acceso web para buscar firmware oficial |

**Criterio de cierre para R8:** se han contestado las 6 preguntas con evidencia documentada. Si el experimento 1 (lectura pasiva UART) no está autorizado o no produce señal, Prioridad A se declara cerrada con límite físico.

---

## Metodología

Cada hallazgo incluye: binario de origen y hash, dirección exacta, instrucciones del disassembly, función llamadora y llamada, script de reproducción, interpretación técnica y limitaciones. Se distingue VERIFICADO / DESCARTADO / NO DEMOSTRADO. No se transforma hipótesis en conclusión. No se usa ausencia de referencias en búsqueda limitada para declarar imposibilidad global.

---

**Evidencia:** `analysis/e26-recovery/r7b-cold-rea.json`, `r5-rea.json`, `r7-nand-rea.json`, `r7-mumin-rea.json`, `r7-lld-rea.json`, `r7-recovery-check-rea.json`, `r7b-updater-rea.json`, `r7b-bootrom-rea.json`, `r7b-rom-protocol-rea.json`, `r7b-info6-inventory.json`, `r7b-info6-ram-search.json`, `r8-uart-parser.py`.
