# E25-04 — Recuperabilidad de Darwin y decisión final sobre B1a (27-10-2026)

Sesión **100 % offline**: no se conectó ni reinició la cámara, no se emitió ningún comando USB, no se
escribió RAM/NVRAM/NAND, no se flasheó, no se generó ningún FDAT/DAT y no se modificó B1a. Base:
`2cf5159314db1fa11b4d06b8410cdf9a3c2a268c` (E25-02). Este informe **no repite** E24 ni E25: audita sus
conclusiones, verifica el plan de recuperación y cierra la decisión.

Binarios y paquetes leídos (sin reescribirlos):

| Papel | Ruta local | SHA-256 | Tamaño |
|---|---|---|---|
| Darwin oficial 3.21 | `firmware/extracted/fw321/.../0640_darwin/darwin_core.bin` | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` | 157 276 B |
| Tipo 0 instalado (T024, 3.22) | `analysis/darwin-patch/darwin_core_tipo0.bin` | `ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc` | 157 276 B |
| **Candidato B1a** | `analysis/e25/darwin_core_tipo0_sin_rearme.bin` | **`55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d`** | 157 276 B |
| FDAT recuperación 3.23 (`.dat`) | `analysis/darwin-patch/fdat/recuperacion-323/firmware_packed.dat` | `5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf` | 212 988 056 B |
| FDAT recuperación 3.23 (`.fdat`) | `analysis/darwin-patch/fdat/recuperacion-323/firmware_packed.fdat` | `cfb65c8aad8ac8a3ccb1c4c758d485feee1ebf2e83e503d9c62d59fb96b01ce4` | 212 155 392 B |
| FDAT instalado 3.22 tipo 0 (`.dat`) | `analysis/darwin-patch/fdat/firmware_packed.dat` | `c19a1463a14d2b8038289240aa68d62dfa0de7e07b0db5c513e99565db3305a6` | 212 988 056 B |
| FDAT instalado 3.22 tipo 0 (`.fdat`) | `analysis/darwin-patch/fdat/firmware_packed.fdat` | `ddc2d5db41cfd049be6b64d702f544ecb6b8e92f6150782097ddb95dccb33295` | 212 155 392 B |
| Firmware 3.21 (`.dmg`) | `firmware/original/Update_ILCE6000V321.dmg` | `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e` | 214 920 547 B |
| NVRAM referencia 3.21 | `analysis/camera-dumps/nvram-referencia-20261020-214913/backup_flash.bin` | `bdf4e8a6d9721f26b466ce86c726623d8c7806d57140c4943a9a829efa5eef32` | 852 647 B |
| NVRAM pre-T024 | `analysis/camera-dumps/20261026-232912-pre-T024-darwin-tipo0/backup_flash.bin` | `5419d449109e0c5424c8946b171a702dcdf0feba208c039e7301459738a8a241` | 852 647 B |
| `nflasha1` (updater) | `analysis/camera-dumps/nand-20261020/dev_nflasha1.bin` | `ea74eb046a6c3ae2cc2e2b5e5fb09a7ce9666e75890d21362a89e7f5c95301fb` | 6 291 456 B |

## 0. Resultado en una frase

**No hay ninguna recuperación independiente de la aplicación Darwin demostrada; el único acceso
independiente es físico y no verificado, así que B1a no es técnicamente autorizable todavía.** El plan
3.24/3.25 es coherente en lo formal, pero un paquete íntegro no es una recuperación: falta demostrar
que un Darwin defectuoso puede volver a arrancar. La acción mínima que cambiaría el veredicto exige
hardware (volcar/probar el arranque propio del MCU), no más análisis estático.

## 1. Veredictos A–H

| | Pregunta | Respuesta | Tipo de límite / alcance |
|---|---|---|---|
| **A** | ¿Hay recuperación independiente por USB demostrada? | **NO** | Evidencia insuficiente **con evidencia en contra**: el USB necesita BIONZ alimentado y el BIONZ recibe núcleo/RAM de `DD_ON1/2/3`, que sube `darwin_core` (E24-01). No es imposibilidad demostrada: falta el binario del arranque. |
| **B** | ¿Hay acceso al bootloader Darwin sin depender de su aplicación demostrado? | **NO** | Existe código de arranque propio en `0x0–0x41ff` (E24-02 A=SÍ), pero **acceder a él para reprogramar** no está demostrado. El único acceso documentado es físico (`MD0_DWN`, `XDWN_RESET`, UART, SWD) y no está verificado. |
| **C** | ¿Existe una recuperación por hardware técnicamente especificada y verificada? | **NO** | **Especificada a nivel de esquema, no verificada**: `CN4906` no montado, `R4927` sin confirmar, protocolo del *serial writer* y protección de flash desconocidos, sin herramienta ni prueba. |
| **D** | ¿R1 está completado y verificado? | **NO** | **Procedimiento listo, copia externa no hecha ni verificada**. El manifiesto local da 62/62 archivos presentes y `verify` pasa contra el origen; eso no es una copia externa. |
| **E** | ¿La integridad y versión de un futuro paquete de recuperación podrían verificarse offline? | **SÍ** | Integridad (SHA-256, CRC-32, reconstrucción byte a byte) y versión (cabecera/BCD) sí. **La aceptación por el guard con 3.22 instalada no se puede verificar offline** (M2). |
| **F** | ¿Existe una contradicción estática demostrada que impida a BIONZ aceptar L0? | **NO** | **No hay contradicción**: el estado 9 libera la ocupación, el 10 es terminal, los mensajes obligatorios salen de la máquina de captura (no de L0), y los temporizadores no tienen una incompatibilidad demostrada. Quedan eslabones sin resolver, no contradicciones. |
| **G** | ¿Es técnicamente autorizable instalar B1a con las evidencias actuales? | **NO** | **Evidencia insuficiente**: no hay recuperación de un Darwin defectuoso, la vía física no está verificada, R1 no está cerrado y el paquete 3.24/3.25 no existe. B1a es válido estáticamente, pero “válido” no es “instalable con recuperación”. |
| **H** | ¿Qué acción mínima permitiría cambiar G de NO a SÍ? | — | **Demostrar la recuperación en hardware**: obtener el arranque `0x0–0x41ff` y el estado de protección de flash, y recuperar un `darwin_core` corrompido en una unidad donante (o en la propia cámara con copia previa). Después, cerrar M1/M2/M9/M10/M12 y reempaquetar 3.24/3.25. Sin abrir una cámara no hay vía demostrada. |

Ninguno de los NO es una imposibilidad técnica demostrada. A, B, C y G son límites de evidencia; D es
procedimental; F es ausencia de contradicción, no prueba de aceptación.

## 2. Parte A — Recuperación independiente de Darwin

### 2.1 Cadena que debe funcionar para que exista recuperación por USB

```text
Batería / VBUS
  └─ Darwin MCU (IC5700, FM3 MB9AF004B)
       ├─ arranque propio 0x0000–0x41ff   ← NO disponible, sin binario
       └─ darwin_core (0x4200)            ← aplicación que se parchea
            ├─ DD_ON1/2/3 = 1  → CP5100/IC5200 → núcleo y LPDDR2 del BIONZ
            ├─ InitCom 0x4bca  → estado 4 → Upd 0x8da8 → 0x45bc
            └─ Upd → arranque 0x0 → protocolo 0x14/0x15 → reescribe flash
  └─ BIONZ (solo si DD_ON* está arriba)
       └─ BootROM «Musashi Loader1» 0xffff0000
            └─ Loader2/3 (NAND física, sin volcar)
                 └─ nflasha1: kernel + initrd del actualizador
                      └─ nflasha2 montable sin uincomp
                           └─ sauU / USB → actualizador
```

La dependencia crítica es la primera: **sin `DD_ON*` no hay BIONZ, y sin BIONZ no hay BootROM ni USB**.
`darwin_core` sube esas líneas desde su tabla de encendido `0x28c6c` (E24-01, VERIFICADO por bytes). Que el
arranque propio del MCU las suba por su cuenta, o que exista una alimentación independiente, **no está
demostrado**.

### 2.2 Las vías documentadas, una por una

| Vía | Qué se sabe | Estado de acceso | ¿Recuperación probada? |
|---|---|---|---|
| **Arranque del MCU `0x0000–0x41ff`** | Existe y es distinto de `darwin_core`; el core salta a su vector con el buzón `[0x20000706]=4`; el FM3 arranca por el vector de `0x0` (E24-02) | Solo por hardware; no hay binario | **NO**. No se sabe si valida la aplicación, si reprograma una imagen rota, si queda en modo descarga o si sube `DD_ON*` |
| **Reset y entrada a bootloader** | `Upd` desactiva IRQ, escribe el buzón 4 y llama a `0x45bc` (`msr msp; ldr pc`), que salta al vector de `0x0` | Requiere que `darwin_core` ejecute `Upd`; sin aplicación no se alcanza | **NO** |
| **`InitCom` / `Upd` / actualizador oficial** | Cadena `COM 0xece4 → InitCom 0x4bca → cola 0 → Seton main → tabla 0x274a8[2]=5 → Upd 0x8da8 → 0x45bc` trazada con bytes (E24-05) | Requiere `darwin_core` vivo y en `Seton` | **NO** para un Darwin defectuoso; solo se ejercitó 3.21→3.22 con Darwin sano (T024) |
| **Boot/download mode del FM3** | Manual de periféricos: `MD1=0`, `MD0=1` durante el reset por `INITX` entra en *Serial Writer Mode*; el protocolo está en el *Flash Programming Manual*, **no disponible** | Físico; `MD1` a masa; `MD0_DWN` sale a isla de prueba, con `R4927` no montada según el esquema | **NO**. Ni siquiera está verificado el nivel eléctrico ni el canal UART |
| **`MD0_DWN`, `XDWN_RESET`** | Redes del esquema; islas `CL5701`, `CL701` | Físico, dentro de la cámara | **NO** |
| **Conector de servicio `CN4906`** | 16 contactos (`BOOT_MODE_1`, `UART_RXD/TXD_DWN`, `NSRST`, `TDO`, `RTCK`, `TCK/SWCLK`, `TMS/SWDIO`, `TDI`, `NTRST`, `DEBUG_MODE`), marcado **XX = no montado** | No hay conector externo; hay que abrir | **NO** |
| **UART `P21/SIN0`, `P22/SOT0`** | Salen como `DWN_UART_RXD/TXD`; convergen en `CN4906` | Físico | **NO**; protocolo y protección desconocidos |
| **SWD/JTAG `P00–P04`** | `TRST/TCK/TDI/TMS/TDO` salen como `*_DWN`; `SPSR` permite SWJ-DP tras reset por defecto; que Darwin lo desactive no se ha comprobado | Físico | **NO**; no hay volcado ni escritura, ni estado de protección |
| **Mecanismos accesibles desde BIONZ** | El BootROM tiene ramas para MS/USB y `is_valid_boot.sh`, pero **no se conoce su disparador**; no hay botón en el actualizador; la entrada conocida es pmca desde el sistema normal (`up.sh user` → reinicio) | Software, pero exige sistema principal y Darwin | **NO** si Darwin no alimenta o no arranca |

### 2.3 Respuestas a las seis preguntas

1. **¿Recuperación por USB si Darwin no arranca?** **NO demostrada.** La cadena USB exige BIONZ
   alimentado, BootROM, Loader2/3, `nflasha1` y actualizador. El único camino conocido de entrada
   (pmca → `up.sh user` → reinicio) presupone el sistema normal y la energía de Darwin. Las ramas
   USB/MS del BootROM no tienen disparador conocido.
2. **¿Recuperación independiente de la aplicación Darwin?** **NO demostrada.** Hay código de arranque
   independiente en el MCU, pero no se ha demostrado que ofrezca una interfaz de reprogramación
   utilizable con la aplicación rota. La única vía independiente documentada es física.
3. **¿Bootloader del MCU sin abrir la cámara?** **NO.** `CN4906` no está montado; las islas de prueba
   (`CL5701`, `CL701`, `CL703–CL707`) están dentro. No hay conector, botón ni combinación externa.
4. **¿Escritura por SWD o modo descarga demostrada?** **NO.** El puerto está cableado y el modo serie
   del FM3 está descrito en el manual, pero no se ha ejecutado ninguna escritura ni se conoce la
   protección de flash. `R4927` (posible enlace de `MD0_DWN`) no está confirmada en la placa.
5. **¿Protecciones de flash o requisitos de arranque desconocidos?** **SÍ, desconocidos**: seguridad/
   protección del FM3, estado de `SPSR`, validación de la imagen por el arranque (CRC/firma), comportamiento
   de `DD_ON*` en el salto, y posible necesidad de una aplicación válida para que el arranque acepte
   una descarga.
6. **¿Qué debe seguir operativo para instalar una recuperación por FDAT?** Energía (`DD_ON*`), `InitCom`,
   `Upd`, salto `0x45bc`, arranque del MCU (`0x14/0x15`), BootROM, Loader2/3, `nflasha1` con kernel/initrd,
   `nflasha2` montable sin `uincomp`, `sauu`/USB, guard de modelo/región/versión, batería/temperatura,
   `usb_extcmd`/`upm.ko` si se entra por pmca, y la NVRAM con el tipo de circuito de energía y el canal SIO/CS.

### 2.4 Acceso físicamente documentado frente a recuperación probada

| | Documentado | Probado |
|---|---|---|
| `MD0_DWN` / `XDWN_RESET` | Sí (esquema; islas de prueba) | **No** (ni siquiera continuidad en placa) |
| UART `DWN_UART_RXD/TXD` | Sí (esquema) | **No** (sin protocolo ni prueba) |
| SWD `TCK/SWCLK`, `TMS/SWDIO` | Sí (esquema; SWJ-DP por defecto) | **No** (sin volcado ni escritura) |
| `CN4906` | Sí (16 contactos, no montado) | **No** (no hay conector) |
| Arranque `0x0–0x41ff` | Sí (existencia y salto) | **No** (sin binario) |
| Actualizador USB | Sí (cadena completa con Darwin vivo) | Solo 3.21→3.22 con Darwin sano; **no** con Darwin roto |

**Límite concreto:** la información que falta reside en el arranque `0x0–0x41ff` y en el *Flash
Programming Manual* del FM3. Ninguno está en el repositorio. No se busca más por software: el siguiente
paso exige hardware.

## 3. Parte B — Verificación del plan de recuperación existente

### 3.1 Estado de partida (supuesto, no re-medido)

Cámara con **3.22 y `darwin_core` tipo 0** instalado en T024 (26-10-2026). No consta ningún flasheo
posterior: T025–T039 no escribieron flash; las pruebas de RAM se revirtieron y los incidentes se
recuperaron con apagado completo. La versión instalada y la batería **no se re-verificaron** en esta
sesión (M10); se toman de T024.

### 3.2 Aritmética de versiones

| Hecho | Evidencia | Estado |
|---|---|---|
| El guard acepta solo versiones **estrictamente mayores** que la instalada | Medido con 3.21: 3.20/3.21 `Invalid version`; 3.22/9.99 aceptadas (`custom-fw-recovery-and-install.md`) | VERIFICADO con 3.21; **INFERENCIA con 3.22** |
| El guard es CRC + modelo + región + versión; **no firma** | S62; `libupdaterufp` | VERIFICADO documental |
| Modelo/región del 3.23 = `0x41030035` / 0 | Cabecera FDAT | VERIFICADO |
| El 3.23 es byte a byte reproducible | `test_e24_03_recovery.py` (8/8; re-ejecutado hoy dentro de 239 pruebas) | VERIFICADO |
| B1a no está empaquetado; no existe un FDAT 3.24 | `analysis/e25/` solo contiene el `.bin` y el manifiesto | VERIFICADO |
| Si B1a se empaqueta como 3.24, la recuperación debe ser **≥ 3.25** | 3.23 < 3.24; el guard rechaza iguales o menores | INFERENCIA fuerte (regla medida con 3.21) |
| La versión se guarda en BCD; tope 3.99 | 3.23 → `0x23`; el formato no permite 3.100 | INFERENCIA del formato |
| **Nunca 9.99**: cierra la vía de recuperación | 9.99 > cualquier 3.x; ya no habría versión mayor en el formato | INFERENCIA fuerte (formato BCD + regla medida) |

Consecuencia: el par correcto es **prueba 3.24 / recuperación 3.25**. Usar el 3.23 como recuperación
después de instalar 3.24 lo convierte en un paquete rechazado. Cada intento consume un número; no se
debe gastar el 3.24 en una prueba sin recuperación 3.25 preparada. La alternativa de usar el 3.23 como
prueba obligaría a reempaquetar la recuperación como ≥3.24; el plan de E24-04 reserva el 3.23 ya
verificado como recuperación y por eso sube el par a 3.24/3.25.

### 3.3 Los cuatro niveles que no deben confundirse

| Nivel | Qué significa | Estado hoy |
|---|---|---|
| **1. Paquete estructuralmente correcto** | Cabecera, CRC, cifrado, modelo/región/versión, tar y `updater.img` íntegros; reconstruible | **SÍ para el 3.23**; **no aplica a B1a** (no hay 3.24) |
| **2. Paquete aceptado por el actualizador** | El guard y el updater lo aceptan con la versión instalada | **Probable, no demostrado** para 3.23 con 3.22 (M2); 3.24 no existe |
| **3. Darwin capaz de ejecutar el actualizador** | `InitCom`, `Upd`, salto y arranque del MCU operativos; enlace SIO/CS | **Sí con Darwin sano** (T024); **no demostrado con Darwin defectuoso** |
| **4. Recuperación real de un Darwin defectuoso** | Un core que no arranca vuelve a arrancar y la cámara queda operativa | **NO**; ningún caso, ni por software ni por hardware |

**Un paquete íntegro no constituye por sí solo una recuperación.** El 3.23 demuestra el nivel 1; no el
2, el 3 ni el 4.

### 3.4 Integridad de NVRAM y firmware original

- **NVRAM**: hay referencia de 3.21 (20-10-2026) y copia pre-T024 (26-10-2026), ambas íntegras. **No hay
  NVRAM de 3.22**. Restaurar una NVRAM de 3.21 sobre 3.22 no está probado (F12). La NVRAM restaura
  ajustes/calibración, **no** Darwin ni el firmware principal; su restauración demostrada (20-10-2026)
  no cubre este caso.
- **Firmware original**: `.dmg` 3.21, `.fdat`, `firmware.tar` (`97024649…`) y `updater.img` (`b6d51752…`)
  íntegros. El tar y el updater del 3.23 son los oficiales; el `darwin_core` del 3.23 es el original
  (`5f2be06d…`), no el tipo 0.
- **NAND**: volcado lógico completo (`dev_nflasha.bin` `472514b9…`, `nflasha1` `ea74eb04…`) y particiones;
  **no hay vía de escritura de dispositivos** en el shell de pmca. Un volcado no es un respaldo
  restaurable por software.
- **B1a**: el candidato y su manifiesto están presentes; el SHA-256 coincide con E25-02. No se ha
  modificado ni empaquetado.

### 3.5 Riesgos de interrupción y dependencias

| Riesgo | Mecanismo | Estado |
|---|---|---|
| **Versión** | Si se instala 3.24 y la recuperación es 3.23, el guard la rechaza | Resoluble offline: reempaquetar ≥3.25 antes de la prueba |
| **Escritura no atómica** | El FDAT reescribe 212 MB de particiones principales además de Darwin; `us_darwin_firm.sh` corre en un hilo aparte (`thread="yes"`) | NO_VERIFICADO el orden y el efecto de un fallo parcial (M16/F7) |
| **Corte de energía/cable** | Ventana de escritura de `nflasha3/5/7/15/16` y de Darwin | Sin escritura atómica demostrada; el riesgo es real (F10) |
| **Darwin no responde** | `ud_darwin_firmup` espera el estado 5; si falla, «NG» y LED `0x63`; las particiones principales ya pueden estar escritas | NO_VERIFICADO si el fallo aborta el resto (F7) |
| **Sistema principal dañado** | La entrada conocida al actualizador es pmca desde el sistema normal; si `nflasha3/5/7` no arranca, no hay entrada | VERIFICADO el camino; alternativas del BootROM sin disparador |
| **`uincomp`** | `/setting/updater/uincomp` presente → error 54 y salida sin USB | VERIFICADO el bloqueo; quién lo crea, NO_VERIFICADO |
| **NVRAM** | Restaurar 3.21 sobre 3.22 no está probado | NO_VERIFICADO |
| **Batería/temperatura** | `libupdaterufp` rechaza con «battery NG»; la lectura probablemente viene de Darwin | VERIFICADO el rechazo; origen INFERENCIA |

### 3.6 Qué falta para que el plan sea una recuperación

1. Medir el guard con 3.22 instalada (M2) — exige conectar, sin escribir.
2. Reempaquetar la recuperación como ≥3.25 y verificarla offline.
3. Tener una NVRAM de 3.22 (M9) y re-verificar versión/batería (M10).
4. Cerrar R1 con copia externa verificada (M12).
5. **Demostrar la recuperación de un Darwin defectuoso** (M15) — no es offline.

Los puntos 1–4 son condiciones necesarias, no suficientes. El 5 es el que decide G.

Un **ensayo de recuperación** 3.22→3.23 con el core original (futuro, con autorización expresa) demostraría
los niveles 2 y 3 con Darwin sano y que el updater reescribe el core; no demuestra el nivel 4 ni cambia G.
Además, su riesgo es del mismo tipo de escritura persistente que se quiere evitar, así que no sustituye
la recuperación independiente.

## 4. Parte C — Respaldo externo R1

### 4.1 Procedimiento reproducible (solo lectura)

Herramienta nueva: `scripts/recovery/r1_manifest.py` + inventario `scripts/recovery/r1_inventory.json`.
No toca la cámara; solo lee archivos y escribe el manifiesto que se le pide.

```bash
# 1) Inventario y manifiesto en el disco externo (o en /tmp mientras se prepara)
python scripts/recovery/r1_manifest.py manifest \
  --out /media/EXT/r1/manifest.json

# 2) Lista de rutas para copiar (solo las presentes)
python scripts/recovery/r1_manifest.py paths /media/EXT/r1/manifest.json \
  > /media/EXT/r1/files.txt

# 3) Copia preservando rutas relativas (-R)
rsync -aR --files-from=/media/EXT/r1/files.txt . /media/EXT/r1/copia/

# 4) Verificación efectiva de la copia (no del origen)
python scripts/recovery/r1_manifest.py verify \
  /media/EXT/r1/manifest.json --root /media/EXT/r1/copia
```

Criterio de cierre: `verify` devuelve **OK**, con 0 ausentes de los que estaban en el manifiesto
(incluidos los opcionales presentes), 0 requeridos ausentes, 0 tamaños distintos y 0 hashes distintos.
Guardar el manifiesto **junto con la copia** y, si es posible, una segunda copia en otro soporte. R1
**no** se declara cerrado hasta que esa verificación se haya ejecutado sobre la copia externa real.

### 4.2 Qué incluye el inventario

| Grupo | Archivos | Tamaño | Obligatorio |
|---|---|---|---|
| NVRAM referencia 3.21 | 7 (backup_flash, backup_mem, bootrom, status, info, SHA256SUMS, README) | 1,7 MB | Sí |
| NVRAM pre-T024 | 6 | 1,7 MB | Sí |
| NAND lógica + particiones | 15 (`dev_nflasha*.bin`) | 960 MB | Sí |
| Metadatos NAND | 3 (`SHA256SUMS`, `README`, `shell.txt`) | 23 KB | Sí |
| Firmware original 3.21 | `.dmg` | 215 MB | Sí |
| Firmware extraído | `.fdat`, `firmware.tar`, `updater.img`, `config.yaml` | 424 MB | Sí |
| Darwin original + sum | 2 | 157 KB | Sí |
| FDAT recuperación 3.23 | `.dat`, `.fdat`, `config-323.yaml` | 425 MB | Sí |
| FDAT instalado 3.22 tipo 0 | `.dat`, `.fdat`, `firmware_tipo0.tar`, `config-322.yaml` | 637 MB | Sí |
| Darwin tipo 0 + sum + README | 3 | 158 KB | Sí |
| B1a + manifiesto | 2 | 162 KB | Sí |
| Controles B1a / auditoría | 4 | 184 KB | No |
| Registro T024 | 2 | 1,8 KB | No |
| Manuales de referencia | 4 | 19 MB | No |
| Otros modelos (A7S/A6300) | 2 | 494 MB | No |

Total del manifiesto generado: **62 archivos, 3 178 353 345 B** (50 requeridos, 2 665 465 292 B; 12
opcionales, 512 888 053 B). Todos presentes, 0 requeridos ausentes, 0 requeridos vacíos.

### 4.3 Estado R1

| | Estado |
|---|---|
| Inventario definido | **SÍ** |
| SHA-256 de los archivos presentes | **SÍ** (manifiesto local) |
| Detección de faltantes | **SÍ** (probada con directorios temporales) |
| Manifiesto para copia externa | **SÍ** (`/tmp/opencode/r1-manifest.json` en esta sesión; regenerable) |
| Verificación contra el origen | **SÍ**: `verify` OK, 62/62 |
| **Copia externa efectuada por el usuario** | **NO** |
| **Verificación de esa copia** | **NO** |
| **R1 cerrado** | **NO** |

El manifiesto incluye la fecha de generación, así que su SHA-256 cambia entre ejecuciones; lo que debe
coincidir son los SHA-256 de cada archivo, no el hash del manifiesto. El manifiesto no se sube al
repositorio: contiene rutas locales y no es necesario para reconstruir nada. Los binarios, volcados y
manuales tampoco se suben (`.gitignore`).

## 5. Parte D — Viabilidad de prueba física sin abrir la cámara

### 5.1 Escenario 1 — recuperación por software demostrada

**No es el estado actual.** Si existiera, significaría: entrar al actualizador con Darwin sin arrancar
(por el BootROM/loader o por una entrada USB independiente), aceptar un FDAT de recuperación y reescribir
un `darwin_core` defectuoso. Antes de considerar B1a faltarían:

1. Medir el guard con 3.22 instalada (M2) y con la recuperación ≥3.25.
2. Tener un FDAT 3.24 con B1a y un 3.25 de recuperación, ambos verificados offline.
3. NVRAM de 3.22 y re-verificación de versión/batería (M9/M10).
4. Prueba física M0 normal: corriente del motor, P40/P41, P4D/P4E, P4B/P4C, P29, CAIF; sin movimiento
   con B1a y captura `done`.
5. Prueba M0 en error: operación 5 (P40/P41=3), timeout 0x17, error de posición; decidir si el apagado
   es aceptable.
6. Cierre BIONZ/M1: estado 31 (P29/ADC-B), fin de L0, mensajes 0x0b/0x0d/0x15/0x0e/0x10/0x17.
7. Criterio de aceptación posterior: arranque en frío, apagado/encendido completo, `pmca info`, y
   recuperación probada antes de la prueba.

Este escenario **no existe**; se enumera para no confundir “B1a válido” con “B1a probado”.

### 5.2 Escenario 2 — recuperación por hardware posible, no verificada

Es el único camino realista para cambiar G. Condiciones técnicas:

| Elemento | Qué hace falta | ¿Abre la cámara? |
|---|---|---|
| Unidad donante | A6000/ILCE-6000 con el mismo MB9AF004B; preferible una unidad de piezas | Sí (o ya abierta) |
| SWD | Adaptador CMSIS-DAP/J-Link/Black Magic, 3.3 V, `SWCLK`/`SWDIO`/`GND`/reset; comprobar `SPSR` y protección | Sí |
| UART | USB-UART 3.3 V en `DWN_UART_RXD/TXD`; `MD0`/`INITX` para el *serial writer* | Sí |
| Alimentación | Fuente de banco o batería; medir `DD_ON1/2/3` y consumo | Sí |
| Flash | Volcar `0x0–0x41ff` y la flash completa; verificar protección de lectura/escritura | Sí |
| Prueba | Corromper deliberadamente el `darwin_core` de la donante y recuperarlo por el puerto de descarga; verificar arranque en frío y `DD_ON*` | Sí |
| Instrumentación | Analizador lógico en P29/P4B/P4C/P40/P41 y CAIF; sonda de corriente del motor | Sí |

Si la flash está protegida o el *serial writer* está deshabilitado, el escenario 2 se convierte en
**no disponible** y G sigue en NO. La prueba en la donante no garantiza al 100 % el mismo estado de
protección en la cámara del usuario, pero es la evidencia mínima para autorizar la operación.

### 5.3 Escenario 3 — sin recuperación independiente demostrada (actual)

Experimentos **de solo lectura** que reducirían incertidumbre sin modificar Darwin:

| Experimento | Qué mide | Requiere | ¿Reduce G? |
|---|---|---|---|
| `pmca info` | Versión instalada, modelo, batería | USB, sin escritura | M10; no G |
| `fdat_guard_probe.py` con 3.23 | Si el guard acepta 3.23 con 3.22 | USB, solo chequeo | M2; no G |
| `senser_backup_dump.py` | NVRAM de 3.22 | Service mode, lectura | M9; no G |
| Lectura T022 de `pkt` en DRAM de BIONZ | `pkt[1]`, `pkt[2..3]`, clase/flag | USB, solo lectura | E24-05e; no G |
| Analizador lógico pasivo en P29/P4B/P4C/CAIF | Niveles y tiempos reales | Abrir la cámara | E24-05h-2; no G |
| Volcado SWD de solo lectura de `0x0–0x41ff` | Contenido del arranque, validación, `DD_ON*` | Abrir la cámara; puede detener el núcleo | A/B/C parcialmente; **no G** |
| Volcado de la flash de Darwin | Core, protección, estado | Abrir la cámara | A/B/C parcialmente; **no G** |

**Riesgo que seguiría sin resolver:** aunque todos estos datos confirmen que el arranque tiene un modo
de descarga y que no valida la aplicación, **no se habría demostrado que un Darwin corrupto se recupera**.
La diferencia entre “el bootloader podría” y “el bootloader recupera” solo se cierra escribiendo y
recuperando. Aceptar el riesgo de instalar B1a sin esa prueba **no equivale a disponer de una
recuperación**: es una decisión del usuario, no un hecho técnico.

### 5.4 Matriz de decisión

| | Recuperación | Evidencia actual | Prueba adicional | Riesgo residual | ¿Autoriza B1a? |
|---|---|---|---|---|---|
| **1** | Software demostrada | **No existe** | Guard 3.22, FDAT 3.24/3.25, M0/M1, NVRAM 3.22 | Bajo si todo se cierra | **No hoy** (habría que crearla) |
| **2** | Hardware posible, no verificada | Esquema + manual FM3; sin protocolo ni protección | Donante + SWD/UART + corrupción/recuperación + instrumentación | Medio: depende de la protección y del arranque | **No** hasta verificarla |
| **3** | Sin recuperación independiente | La actual | Solo lectura (tabla 5.3) | **Alto**: un fallo de arranque puede dejar la cámara sin salida por software | **No**; solo aceptación expresa del riesgo |

## 6. Parte E — Contrato mínimo con BIONZ (solo contradicción con L0)

Alcance: únicamente si las evidencias de E24-05f/g/h y E25 contradicen el fin de L0. No se reabre la
auditoría general.

| Punto | Evidencia | ¿Contradicción con L0? |
|---|---|---|
| **Estado exterior 9 y liberación de ocupación** | L0 = `[0,7,8,9,10]` (bytes `0x29cd8`); el estado 9 (`0x200e6`) hace `mov.w r0,#0x1000000; bl 0xd18e`; `0xd18e` hace `bics` en `[0x20002bd0+8]` y `+4`; la admisión lee `+8` | **No**. L0 incluye el 9 y libera exactamente el bit 24 que bloquea la admisión. |
| **Estado exterior 10** | El descriptor `0x29cf0` tiene id terminal `0xa`; la tabla `0x29d0c` empareja 9→`0x200e6`, 10→`0x200fc`; el motor compara el id actual con el terminal en `0x1e16e` | **No**. El 10 es terminal y L0 lo alcanza. |
| **Mensajes obligatorios esperados por BIONZ** | BIONZ espera en orden `0x0b`, `0x0d/0x15`, `0x0e`, `0x10`, `0x17` (y `0x11/0x14` de ajustes) con `caif_recv` sin plazo; los emisores son la tarea de captura, la FSM de ajustes/modo y la máquina de 49 estados, no la lista exterior (E24-05d/f/g/h) | **No demostrada**. Los cinco primeros no leen la compuerta y salen en el mismo orden; `0x17` es autopetición de Darwin (E24-05g); faltan el productor BIONZ de los datos que cumplen las condiciones de `0x11/0x14` y la correspondencia modo/tipo, pero son eslabones sin resolver, no una contradicción. |
| **Temporizadores de L0** | Estado 0: `0x8ca0`; estado 7: `0x5dc0`; unidad no medida. La espera de 1000 unidades (`0x1ff2a`) pertenece a la API de carga `0x1984e`, no al camino de captura; en la rama de preparación que espera el fin de la máquina exterior (`0x17dba`), la tarea sondea `0x199d0` mientras devuelve 0, sin ese presupuesto | **No demostrada**. No hay un plazo estático que se oponga a L0; la unidad y los plazos de BIONZ no están medidos. Es un riesgo temporal, no una contradicción. |
| **Condiciones de entrada al estado 31** | El 31 está en las cinco listas de captura; su espera la selecciona `S+0x32` (`pkt[2..3]`): con 0, P29 bajo; con ≠0, FSM ADC-B. La compuerta `0x1fe66` no interviene en esa entrada (E24-05h) | **No**. La entrada al 31 no cambia con B1a; siguen sin resolver el conductor/polaridad de P29 y el productor de `pkt[2..3]`. |

**Cierre:** **F = NO**. No hay contradicción estática demostrada que impida a BIONZ aceptar L0. Eso
**no** significa que BIONZ lo acepte: los eslabones pendientes (P29, `pkt[1]`, `pkt[2..3]`, lector BIONZ
del fin) son evidencia insuficiente, no una prueba de aceptación.

## 7. Riesgos y estado de la decisión

| Riesgo | Consecuencia | Estado |
|---|---|---|
| Darwin roto sin recuperación | Cámara sin USB, sin menú; solo puerto físico | **No demostrado que se pueda recuperar**; evidencia en contra para A/G |
| Interrupción de escritura | Core o particiones incompletas | Sin atomicidad demostrada; M16/F10 |
| Guard rechaza la recuperación | 3.23 inútil tras 3.24 | Resoluble offline con ≥3.25 |
| NVRAM incorrecta | Ajustes/calibración mal; no restaura Darwin | NVRAM 3.22 no existe; F12 |
| BIONZ no acepta L0 | Captura bloqueada, no necesariamente brick | F = NO; falta medir |
| Watchdog | Reinicio durante L0; `DD_ON*` cae | E24-05b bloqueado; no medido |
| R1 sin copia externa | Pérdida del material si falla el disco | **PARCIAL / abierto** |
| Aceptar el riesgo | Decisión del usuario, no recuperación | No cambia A–G |

## 8. Decisión final y acción mínima

**No instalar B1a con las evidencias actuales.** B1a sigue siendo un candidato válido estáticamente
(2 bytes, L0 en los tres arrancadores, tipo 0 intacto, 12 consumidores cubiertos), pero **no es
instalable**: no hay recuperación demostrada de un Darwin defectuoso, la vía física no está verificada y
R1 no está cerrado. Un fallo de arranque dejaría la cámara sin salida por software.

**Acción mínima para cambiar G de NO a SÍ (H):**

1. **Donante**: conseguir una A6000 de piezas o una unidad ya abierta con el mismo MB9AF004B.
2. **Volcar** por SWD/UART el arranque `0x0–0x41ff` y la flash de Darwin; comprobar protección de
   lectura/escritura y el estado de `SPSR`.
3. **Corromper** deliberadamente el `darwin_core` de la donante y **recuperarlo** por el puerto de
   descarga; verificar arranque en frío, `DD_ON1/2/3` y que el BIONZ llega al actualizador.
4. **Documentar** el procedimiento y repetirlo, si el usuario lo autoriza, en la cámara real con copia
   previa. Sin este paso no hay G = SÍ; con él, la recuperación pasa a ser un hecho, no una hipótesis.
5. Después, y solo después: FDAT 3.24 con B1a, recuperación ≥3.25, guard medido con 3.22, NVRAM 3.22,
   R1 verificado y matriz M1–M17 cerrada.

Si el usuario decide no abrir ninguna cámara, **G sigue en NO** y la única alternativa es la aceptación
expresa del riesgo, que debe registrarse como excepción del usuario: **no es una autorización técnica ni
una recuperación**. La prioridad del proyecto —probar B1a sin perder la cámara— no se satisface con el
material actual.

## 9. Pruebas y reproducción

- **Regresión E24/E25**: 239 pruebas aprobadas en 76 s con `.venv`:
  `tests/test_e24_01_boot.py`, `02`, `03`, `04`, `05`, `05a`, `05d`, `05f`, `05g`, `05h`,
  `test_e25_desactivacion.py` y `test_e25_02_auditoria.py`.
- **Nuevas E25-04**: `tests/test_e25_04_recuperabilidad.py` (2 pruebas, 0,5 s): estado 9/10 de L0 y
  distinción entre la espera acotada de la API de carga y la espera de captura.
- **R1**: `tests/test_r1_manifest.py` (6 pruebas): manifiesto, verificación, faltantes, hashes,
  `paths` y rechazo de rutas que salen del árbol.
- **Manifiesto local**: `python scripts/recovery/r1_manifest.py manifest --out /tmp/opencode/r1-manifest.json`
  → 62/62 presentes, 0 requeridos ausentes; `verify` contra el origen → OK. **No es una copia externa.**

Comandos:

```bash
source .venv/bin/activate
python -m pytest -q tests/test_e25_04_recuperabilidad.py tests/test_r1_manifest.py

python scripts/recovery/r1_manifest.py manifest --out /tmp/opencode/r1-manifest.json
python scripts/recovery/r1_manifest.py verify /tmp/opencode/r1-manifest.json --root .
```

## 10. Límites

- Todo el análisis es estático o documental; no se ejecutó firmware ni se midió la cámara. “No
  demostrado” no es “imposible”: el arranque `0x0–0x41ff` y el *Flash Programming Manual* del FM3 no
  están disponibles.
- La versión instalada (3.22) y la batería son un supuesto de T024, no una medida de hoy (M10).
- La protección de flash, el estado de `SPSR`, la continuidad de `R4927` y el protocolo del *serial
  writer* no se han verificado en placa.
- El guard con 3.22 es inferencia; la regla está medida con 3.21.
- El manifiesto R1 prueba que los archivos locales están presentes e íntegros, no que exista una copia
  externa. R1 sigue abierto.
- La aceptación del riesgo por el usuario no cambia A–G ni sustituye la recuperación demostrada.

**Cierre:** A=NO, B=NO, C=NO, D=NO, E=SÍ, F=NO, G=NO. La única vía que puede cambiar G exige hardware;
no queda una investigación estática que lo resuelva.
