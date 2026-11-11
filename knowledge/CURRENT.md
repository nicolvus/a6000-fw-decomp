# Estado actual — léeme primero

Contexto operativo mínimo para agentes. Última revisión: **07-11-2026** (E26 R65–R68: rama EFCS de Darwin y auditoría).
No es historial ni fuente de verdad de los pendientes: ver [Responsabilidades](#responsabilidades-documentales).
Versiones íntegras anteriores (nada se borró): [CURRENT-historial-2026-10-31](history/CURRENT-historial-2026-10-31.md)
(bloques E26 R5–R35 y E25 completos) y [CURRENT-historial-2026-10-26](history/CURRENT-historial-2026-10-26.md) (S59–S627).

## Estado global

| Aspecto | Estado | Fuente |
|---|---|---|
| **Cámara** | Arranca con el **CFW 3.73** (11-11-2026; 3.38 + tres estados de obturador + menú Picture Profile plano de 6 filas/página, parche PP del núcleo en la imagen `nflasha3`, **sin `nflasha5`**) ([PENDIENTES G30-C](../docs/PENDIENTES.md), [auditoría PP G32: 15 ajustes sin consumidor en el núcleo, Gamma Movie/Still sin efecto](../docs/gui/g32-auditoria-picture-profile-3-73.md), [G33: Black/Knee/Detail/Still aplicados en el núcleo, CFW 3.74 construido sin instalar](../docs/gui/g33-pp-black-knee-detail-still.md), [G29](../docs/gui/g29-informe-picture-profile-estado.md) §6). Antes: 3.53 ([G11 §11](../docs/gui/g11-auditoria-307-nflasha15.md)). Cambiar `/usr` exige quitar el WBI de Sony (`nflasha5`). En NVRAM sigue la tabla EFCS de prueba `c = 2000 µs` (R84; R85 mide +27…+34 % a 1/350, tabla calibrada lista sin escribir) y la variante BIONZ `0x30102+0x88 = 834` (R64 §6). Sonda SWD aún soldada | [G11](../docs/gui/g11-auditoria-307-nflasha15.md), [R84](../docs/capture/e26-r84-darwin-v3-en-camara.md) |
| **Prioridad** | Obturador electrónico funcionando desde el 3.30 (R54). Abierto: **EFCS activado pierde ≈1,27 ms y sale negro desde 1/1000, también con el firmware de Sony** (R57 §5/§8). R65: Darwin hace `S+0x48 = T − u16[G+0x42]` con EFCS activado; R66: G = NVRAM `0x1850000` (`G+0x42`=3407, sin cambios desde el 20-10); la pérdida viene del lado BIONZ/sensor o de la cortina (E26-R66-RESET); compensación descartada (R69). **`0x30102` no es Darwin** | [R66](../docs/capture/e26-r66-bloques-darwin-en-nvram-1850000.md), [PENDIENTES § E26](../docs/PENDIENTES.md) |
| Recuperación | Cerrada (R49); las vías alternativas se cerraron en el triaje del 07-11-2026 | [R49](../docs/capture/e26-r49-cierre-recuperacion-326.md) |
| Hito del obturador | Electrónico funcionando desde el **3.30** (envío en línea de `pkt[0x0e]` + compuerta de Darwin); 3.35 con la exposición calibrada por el parche de RAM de la app (R56 §7). El 3.23 (B1a) fue el primer hito (T040) | [R54](../docs/capture/e26-r54-paquete-330-envio-pkt0e.md), [R56](../docs/capture/e26-r56-paquete-333-envio-inline.md) |
| Firmware 3.25 (histórico) | Selector + C3-B + Darwin condicionado; su `nflasha3` bloqueó la cámara (R36) | [E25-27](../docs/capture/e25-27-construccion-firmware-integrado.md), [R36](../docs/capture/e26-r36-causa-fallo-325.md) |
| Causa del bloqueo del 3.25 | Formato TPZL de `nflasha3` (R36); corregido en el 3.25c | [R36](../docs/capture/e26-r36-causa-fallo-325.md) |
| Arnés de la UI (G22-B) | `im.elf` 3.21 corre bajo QEMU + `sonyshim.so` (reproducible: `scripts/gui/harness/setup.sh`); la UI arranca y carga vistas, recorre el ciclo completo de modelos `Tc`/`Ts`/`Mr` (`SALVAGE=0`, `ACKQ0=58003f` acuse ADF, `STARTGAP=f`; §5.18v, 11-11-2026), pero no abre la vista `0x3C` y la pantalla sigue a cero (GPU). Plan F1–F5 | [G22](../docs/gui/g22-arnes-ui-qemu.md) |
| Pregunta original (S51) | Exposición totalmente electrónica a resolución completa: A=NO, B=NO, C=NO en estático; superada en la práctica por el parche de Darwin (3.23), cuya exposición por filas tiene el límite medido de E25-10 | [S51](../docs/capture/s51-decision.md), [E25-10](../docs/capture/e25-10-exposicion-por-fila.md) |
| Cifras | 4 427 pruebas colectadas en local; CI (sin firmware): 918 pasan, 2 310 omitidas. Censo de etiquetas 372/372 (100 %, mide documentación). 295 sesiones S con informe (numeradas en paralelo hasta S630; no son 630 sesiones) y 84 informes de fase E. Planes físicos con prueba 12/24 (P1–P24). Registro T001–T056 (53 filas) | [estado.json](audit/estado.json), [tablero](https://nicolvus.github.io/a6000-fw-decomp/progress/) |
| Binarios publicados | Release GitHub `fw-3.23-3.24` (01-11-2026, a petición del usuario): `.dat` del 3.23 (instalado, T040) y del 3.24 (recuperación, solo offline). Release **`fw-3.25c-experimental`** (*pre-release*, R45): 3.25 corregido `d64ad6e3…` (**nunca instalado**) + 3.26 de vuelta atrás (un paquete 3.26 de recuperación sí se instaló en la cámara del autor, R49). No están en el árbol de git | [R8](../docs/PENDIENTES.md), [R45](../docs/capture/e26-r45-firmware-325c-experimental.md) |

## E26 — recuperación (todo offline)

| R | Resultado vigente | Informe |
|---|---|---|
| R1–R4 | Identidad del FDAT 3.25, comparación TPZL (fases A/B/C), Loader3 candidato, placa SY-1028 | [E26-RECOVERY](../docs/capture/e26-recovery.md) |
| R5–R7B | Loader3 de 128 KiB (recorte no íntegro), BLDR die0/plane0, INFO6 sin fuente; COLD fallido = bucle LED; escrituras NAND solo desde Linux | [R5](../docs/capture/e26-r5-loader3-servicio.md), [R6](../docs/capture/e26-r6-recuperacion-bionz.md), [R7](../docs/capture/e26-r7-recuperacion-estatica.md), [R7B](../docs/capture/e26-r7b-recuperacion-prelinux.md) |
| R8–R9 | Receptor serie del BootROM: tipo 0 = escritura RAM arbitraria, `0xFFFF` = salto (`0xc000500C`); CRC-32 reflejado `0xEDB88320`; eSRAM 1 MiB ejecutable (emulado) | [R8](../docs/capture/e26-r8-bootrom-uart-boss.md), [R9](../docs/capture/e26-r9-bootrom-ram-execution.md) |
| R10, R19 | USB Charger `054c:0994` = Darwin; HID solo Input, sin canal de escritura → descartado como vía | [R10](../docs/capture/e26-r10-usb-charger-recovery.md), [R19](../docs/capture/e26-r19-darwin-usb-static.md) |
| R11, R29 | Pinout CN4001 (19 pines) y CN4906 (18; BIONZ+Darwin combinados); `BOOT_SERIAL_IN` → Multi pin 9 vía `CM4002/CM4003` (montados por convención) | [R11](../docs/capture/e26-r11-bootrom-uart-physical-access.md), [R29](../docs/capture/e26-r29-pinout-cn4001-cn4906-completo.md), [R19/R20](../docs/capture/e26-r19-r20-cierre-estatico.md) |
| R12–R14 | LED 3+2 = −302 de **Loader3** (BOS o CFG); tiempos con reloj de 4 MHz; RAMCFG y FAT cumplidos por 3.21 y 3.25 | [R12](../docs/capture/e26-r12-bootrom-static-audit.md), [R13](../docs/capture/e26-r13-led-error-provenance.md), [R14](../docs/capture/e26-r14-ramcfg-bos-analysis.md) |
| R15–R17, R27–R28 | Loader3 acepta el residuo TPZL (solo avisa); el ARM7 escribe el residuo en el LDEC y nadie lo lee; semántica de silicio indecidible sin hardware (decisión C); sin muestras públicas de TPZL | [R15](../docs/capture/e26-r15-tpzl-custom-fw325.md), [R16](../docs/capture/e26-r16-ldec-hardware-audit.md), [R17](../docs/capture/e26-r17-arm7-ldec-segment-analysis.md), [R27](../docs/capture/e26-r27-arm7-isr-geometria.md), [R28](../docs/capture/e26-r28-tpzl-busqueda-externa.md) |
| R20–R23 | BootROM completo: selector `MODEREG` (`0xf2915010`) bit 0, GPIO4.21/22; receptor 8O1 ~16 000/~47 600 baudios; 57 rutinas, 109 pasos de traza, 25 códigos | [R20](../docs/capture/e26-r20-bootrom-selector.md), [R21](../docs/capture/e26-r21-bootrom-rx-serie.md), [R22](../docs/capture/e26-r22-bootrom-mapa-completo.md), [R23](../docs/capture/e26-r23-bootrom-flujo-completo.md) |
| R24–R26 | Loader2 247/247 y Loader3 674/674 funciones con rol; `\updater\mode` en `nflasha2` es condición necesaria de la cadena especial; `LD3:<<KEY>>` = clave de batería, descartada | [R24](../docs/capture/e26-r24-loader2-completo.md), [R25](../docs/capture/e26-r25-loader3-completo.md), [R26](../docs/capture/e26-r26-updater-mode-y-clave-pwric.md) |
| R30 | Fase A cerrada, B acotada (byte 0x32 no observado), C: con Done la cámara tiene exactamente el `nflasha3` del 3.25 | [R30](../docs/capture/e26-r30-updater-done-boundary.md) |
| R31–R33 | Bit 0 = `BOOT_MAIN`/`CL1000`; **valor real `MODEREG[15:0]=0x0003`** (23 volcados): el arranque normal pasa por la ventana serie con clave; la clave está en `nflasha0` (sector `0xc00` no borrado; validez y valor desconocidos) | [R31](../docs/capture/e26-r31-bootmain-bit0-cierre.md), [R32](../docs/capture/e26-r32-moderreg-valor-real.md), [R33](../docs/capture/e26-r33-veracidad-clave-nflasha0.md), [KEYTABLE](../docs/capture/e26-r20-keytable.md) |
| R34–R35 | `serial_entry` sin bucle de reintento (corrige R23 §2); `serial_receiver` recibe varios paquetes por llamada | [R34](../docs/capture/e26-r34-serial-entry-flags.md), [R35](../docs/capture/e26-r35-serial-receiver-multi-paquete.md) |
| R36 | Causa del −302: formato TPZL del 3.25 (residuo descartado por Loader3; registros ≠ 16 × 4096); 3.23 vs 3.25 = solo Darwin + `nflasha3`; corrige R16/R17 (residuo) y la recomendación «alinear a 512» | [R36](../docs/capture/e26-r36-causa-fallo-325.md) |
| R37 | Cierre estático: solo `\updater\mode` (en `nflasha2`) lleva al actualizador de `nflasha1`, que no lee `nflasha3` (corrige R26 §1.2); paquete **3.26** listo (3.24 ya no sirve); UART de Loader2/3 apagada por `Backup[0x510015]=0`; Darwin 3.25 sin comportamiento nuevo al encender | [R37](../docs/capture/e26-r37-cierre-estatico-recuperacion.md) |
| R38 | Guard de `sauu`: compara con `\updater\dat4` (`comp` = firmware válido); `CompleteUpdate` escribe la versión del FDAT → tras el 3.25 hace falta ≥ 3.26. Loader3 solo pide la entrada corta `MODE` (0 B); en el volcado basta 1 byte (entrada borrada, sector 132 de `nflasha2`); sin LFN persiste tras sesiones fallidas (corrige R37 §2) | [R38](../docs/capture/e26-r38-guard-y-entrada-updater.md) |
| R39 | Fallo del 3.25 reproducido en emulación (Loader3 + ARM7 reales, LDEC modelado: 361/369, Sony/corregida 0); `nflasha` lógico de MuMin → el byte de `MODE` no se escribe con lector externo, hace falta escribir desde el BIONZ; `MODE` persistente por FUENTE; guard USB sin batería; clave quizá legible en SRAM `0xc0001200` | [R39](../docs/capture/e26-r39-estatico-profundo.md) |
| R40 | JTAG/SWD del BIONZ: ningún cargador previo a Linux toca el DAP CoreSight (0xf2710000); `defconfig` `ice_*` de Sony arrancan bajo depurador; tras −302 la CPU no se apaga (bucle de LED sin `wfi`, ventana indefinida). No añade vía nueva sobre R5/R6/R29: falta población de R4911/R4912 y el eFuse de seguridad, no legibles estáticamente | [R40](../docs/capture/e26-r40-jtag-swd-bionz.md) |
| R41 | Caminos estáticos restantes: `c01f379a` = consola serie de Loader3/Loader2 (`beast`, `ldump`), solo lectura y muda con `Backup[0x510015]=0` (corrige R13/R37 §4/R40 §6); espera `CFG:Wait ICE` por GPIO 14.17 antes del −302 (bola no determinable). La consola usa la UART0 a 115 200 8N1 y su RX no llega al Multi (`R4002` XX). Ninguna vía nueva sin acceso físico | [R41](../docs/capture/e26-r41-caminos-estaticos-restantes.md) |
| R42 | Búsqueda en GitHub (sin hallazgos nuevos aplicables al CXD90014) y lectura directa del esquema (no el `.txt` OCR, que pierde la hoja): bolas de JTAG/eFuse/SWD, `FUSE_EN` atado a VDD, `NTRST` = neto `XRESET_CR` = entrada `XRESET` del propio chip; cobertura de GPIO verificada sobre el manual completo | [R42](../docs/capture/e26-r42-busqueda-externa-y-esquema-jtag.md) |
| R43 | Cierre estático de `CL1000`/`BOOT_MAIN` (bit0): el GPL de Sony no define su polaridad (solo nombra el bit1); trazado vectorial (`pdftotext -bbox`+`pdftocairo -svg`, sin OCR) de la hoja CLK BOOT muestra que `CL1000` no tiene salida hacia el conector Multi — sin atajo externo, sigue siendo físico interno. Efecto lateral: `BOOT_SERIAL_IN` (bit1) llega al pin **10** de CN4001, no al 9 (corrige R11/R19/R20/R29) | [R43](../docs/capture/e26-r43-cl1000-sin-acceso-externo.md) |
| R44 | La comprobación de clave es una sola palabra de 32 bits comparada en una instrucción (`ldrd`+`cmp`), sin canal lateral; `error_blink` es un bucle infinito (exige apagar/encender por intento) → **fuerza bruta descartada**. Mejor vía ya conocida (R20/R23): `GPIO4.22!=0` evita la clave por completo. Reabierto el pin físico de ese bit con el método de R43: sin cierre, candidato débil `GPIO_SB_5`/bola N8. Sesión REA de `av-cam.bin` (§6): la asignación banco/bit de las 26 funciones que leen GPIO depende de la base de datos de propiedades de Sony (IDs opacos) — bloqueado por el mismo límite que `E1` | [R44](../docs/capture/e26-r44-gpio4-bit22-busqueda-pin.md) |
| R45 | 3.25c: mismo BIONZ/Darwin que el 3.25, `nflasha3` con forma de Sony; constructor endurecido (`_splice`, máx. 126 sectores como Sony; el de R36 daba 129). 30/30 sobre el `.dat` final, emulación 0/369 fallos; publicado como *pre-release* experimental y teórica | [R45](../docs/capture/e26-r45-firmware-325c-experimental.md) |
| R46 | Procedimiento físico planeado para SWD al BIONZ (sin osciloscopio): materiales, fases F1–F9, criterios de parada. R4911/R4912/CN4906 confirmados sin montar | [R46](../docs/capture/e26-r46-procedimiento-fisico-swd.md) |
| R47 | Primer contacto SWD real: DPIDR/APs leídos, RAM volcada, `halt`+registros confirman −302 en registros; cadena de puntos de parada hasta el arranque 2 confirma físicamente que P2 (`CFG_E:Load file`) falla al cargar `\sabin\idt_cam.bin` de `nflasha3` (§15) | [R47](../docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md) |
| R48 | Plan de entrada al actualizador sin escribir NAND (forzar `r0=0` en `chk updater` por SWD); P0/P1 preparados; primer intento de instalación del 3.26 cortado al 45 % (`0x1063`, NG de Darwin) | [R48](../docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md) |
| R49 | **Cierre:** script corregido para el arranque único real; P1 ejecutado con éxito, reintento de instalación completo (`CMD_COMPLETE`). **Cámara recuperada, firmware 3.26 confirmado** | [R49](../docs/capture/e26-r49-cierre-recuperacion-326.md) |
| R50–R64 | Paquetes 3.27–3.38; obturador electrónico funcionando desde el 3.30 (envío en línea de `pkt[0x0e]`); EFCS activado negro desde 1/1000 incluso en el 3.37 de Sony; NVRAM, NAND y Darwin descartados como causa; marca EFCS `pkt[1]` 0x02/0x40 | [R54](../docs/capture/e26-r54-paquete-330-envio-pkt0e.md), [R57](../docs/capture/e26-r57-paquete-336-darwin-eq1.md), [R58](../docs/capture/e26-r58-auditoria-nvram-nand-calibracion.md), [R63](../docs/capture/e26-r63-swd-efcs-on-off.md), [R64](../docs/capture/e26-r64-darwin-marca-efcs.md) |
| R65 | `t` = 0 al arrancar; tiempos de Darwin en µs; con EFCS activado `S+0x48 = T − u16[G+0x42]` y cierre con `B+0x8a`/`B+0x86` según la rama (R68: las ramas no explican la pérdida) | [R65](../docs/capture/e26-r65-darwin-efcs-on-resta-g42.md) |
| R66 | B/G de Darwin = NVRAM `0x1850001`/`0x1850000` (no `0x30102`, corrige R58 §13 y R61–R65); idénticas en 28 volcados; temporización de Darwin continua → la pérdida no es de Darwin | [R66](../docs/capture/e26-r66-bloques-darwin-en-nvram-1850000.md) |
| R67 | Con EFCS, Darwin baja P4C (`CA_1ST_CURTAIN_START`, flanco hacia BIONZ `SENS_B`/`GPIO_9`) y `T − 3,4 ms` después suelta P4E (`2ND_CURTAIN_MG`); la pérdida está en el retardo flanco→reinicio (BIONZ/sensor) o en la cortina; prueba pasiva E26-R67-GPIO9 | [R67](../docs/capture/e26-r67-eventos-a-b-p4c-p4e.md) |
| R68 | Auditoría de R65–R67: corregidos la explicación del negro (R65 §3), `0x30102` en R65, la saturación de B86 y esta tabla global; cuatro afirmaciones rebajadas a INFERENCIA | [R68](../docs/capture/e26-r68-auditoria-r65-r67.md) |
| R69 | Revisión de R56–R64: notas de corrección en R58/R61/R62/R63/R64 (`0x30102` y `0x30100` no son bloques de Darwin; `t` = 0); B (P4E ← 1) suelta la segunda cortina y la separación A–B no depende de `ip`; B86 descartado | [R69](../docs/capture/e26-r69-revision-informes-efcs.md) |
| R70 | P4C sube en la preparación (`0x1811a`) y se rearma después (`0x28dc5`, acción 0x14): A siempre genera el flanco en Darwin. `ip` (`0x237cc`) no toca líneas de cortina; `0x182d8` usa `G+0x42` solo en plazos largos. Sin pendientes estáticos del problema EFCS |
| R71 | Medida SWD de los GPIO del BIONZ (42 disparos): fin de exposición (`b0.8↓`) sigue a B; lectura `b7.21` ≈ 66 ms; a 1/1000 el BIONZ hace lo mismo con EFCS activado y desactivado. P4C sin identificar; siguiente: analizador lógico |
| R72 | NVRAM `0x30087+0xa0..` → `record+0x156` solo con EFCS (90 líneas ≈ 1,37 ms; posible palanca sin código); `[0x20000050]` de Darwin viene del cargador. Pendientes E26-R72-30087 y -DARWIN-CFG |
| R73 | Corrige R72: `0x30087` va a StillInfo+0x2b4 (procesado en Linux), no al sensor. Ganchos de `sl` = variables de depuración del grupo 2. Sin fuente estática por unidad en el BIONZ |
| R74 | **Conclusión final:** causa física. El BIONZ no depende de T en el EFCS oficial y la pérdida sigue a `B − A` de Darwin. Pruebas físicas en E26-R74-FISICO; compensación opcional `0x1850001+0x86` = 1256 (E26-R74-COMP) |
| R75 | **Verificación de R74 y Darwin:** R74 §2–§3 verificados (14 lecturas de `0x30097+0x15`; clase 3 fija por tres vías). Darwin sin mecanismo que dependa de `B − A` (P4E 5 ms fijo). **Corrige R74 §4:** la pérdida es función de `B − t0` (retardo de B desde el armado), no del flanco A. Pendiente E26-R75-T0 |
| R77 | **Preparación y P4D:** P4C ← 1 (`0x17cee`) primero; con EFCS y tipo 1/2 el único P4D ← 1 de la captura va tras el armado (`0x190fc → 0x199b8 → 0x1ffce`) con retardo de configuración fijo, sin T; preparación→0x1f solo medible. Corrige R75 §2.3. [R77](../docs/capture/e26-r77-preparacion-p4d-orden-temporal.md) | `test_e26_r77_preparacion.py` |
| R78 | **Límites de R77 cerrados:** `0x1e4aa/c2/f6` = seguir/retener/ceder; 09/0a/13/14 gobiernan la máquina S `0x28dd4` (sin P4C–P4E ni T; P4B solo por error de vigilancia); `0x1fee2` solo por `0x1984e` (4 raíces). [R78](../docs/capture/e26-r78-cierre-limites-r77.md) | `test_e26_r78_limites_r77.py` |
| R79 | **Restos de R78 cerrados:** `0x295c4` = evento `0x16` (cola 2, paquete `0x31` del host, fuera de la captura); `0x25b70` = lista de arranque; 04–06 de S avanzan (stubs), `0x2f` espera bandera externa; sin T ni P4C–P4E; reejecución de S fuera de la imagen. [R79](../docs/capture/e26-r79-cierre-restos-r78.md) | `test_e26_r79_restos_r78.py` |
| R81 | Parche Darwin con tabla EFCS (R76) BLOQUEADO (levantado en R82): el cave `0x13d5a` está en la función viva `0x13d58` (`bl` en `0x1516c`) y no hay ≥ 40 B libres en la imagen; la vía NVRAM (a) sigue disponible | [R81](../docs/capture/e26-r81-auditoria-opus-parche-efcs.md) |
| R82 | **Parche EFCS v3 en sitio:** el prefijo `0x18d6e..0x18e0f` (162 B) se reescribe con la tabla `c(T)` integrada (`G+0x48`, 14 × `{s16 T−G42, u16 c}`), mismo tamaño y sin hueco; equivalente al original (1 M estados + 786 k combinaciones, modelo a mano, oráculo con cave anexado). Volcados NVRAM `B86 = 1256` / `G42 = 2157` listos sin escribir (E26-R82-NVRAM). Anexar (C): el actualizador admite hasta 246 023 B, el cargador solo se decide en cámara. Sin hueco ≥ 40 B (B). Pendiente en cámara: E26-R82-CAMARA | [R82](../docs/capture/e26-r82-parche-efcs-v3.md) | `test_e26_r82_parche_efcs_v3.py` |
| R83 | **Informe final EFCS negro:** no es firmware ni datos (alta); causa física más probable (media); parche v3 de Darwin listo sin instalar, útil de 1/1000 hacia abajo. Siguiente: pruebas físicas y prueba NVRAM con autorización |
| R85 | Fotos DSC03749–03779: pérdida EFCS real ≈ 1,0–1,16 ms → tabla calibrada `analysis/e26-r85/tabla-r85.json` (media ±2 %, degradado vertical sin corregir); **Silent sin calibrar en el CFW** (`av-cam` 3.73/3.75 sin ShutMode 0 + `r5`): +3,5…+5,5 EV a cualquier velocidad; solo el parche RAM por disparo lo nivela | [R85](../docs/capture/e26-r85-calibracion-fotos-3749-3779.md) |

**Conclusión operativa:** la recuperación física se completó por SWD (R46–R49): se forzó la entrada al actualizador de fábrica sin
escribir NAND ni memoria (solo un registro de CPU durante el arranque), y el actualizador oficial de Sony instaló el 3.26, que
restauró `nflasha3`. La cámara arranca en modo normal. Pendiente solo retirar la sonda y decidir si se retoma el obturador electrónico.

## Obturador — hallazgos que siguen vigentes (VERIFICADO salvo nota)

- **Darwin gobierna el obturador y la energía** (`DD_ON1/2/3`, E24-01); bootloader propio en `0x0–0x41ff` (E24-02). Ningún Darwin defectuoso
  tiene recuperación demostrada (E24-04, E25-04). Base ROM `0x4200`.
- **B1a**: `0x1fe6a: 28 46 → 0a e0` fuerza la compuerta `0x1fe66` a 0 → lista `[0,7,8,9,10]` sin motor en captura ni rearme (E24-05, E25-02).
- **Exposición sin cortina** (E25-10): fila `i` = T + ≈7 ms + 15,2 µs·i; con ShutMode 0 la integración es uniforme y vale (4219 − `r5`) × 15,2 µs (T046/T047).
- **Productor nativo** `0x4383fa40`: `r5`, ShutMode 0 y `svd` desde Tv/período/VTS; emulado ±1 línea frente a T047 (E25-15/16). VTS real de foto 4176 (T053).
- **Selector EFCS/Electronic + C3-B** (E25-24b/25/26): `cap+0x41c → pkt[0x0e] → S+0x3e`; enganche `0x438c82fe`, cueva `0x43541840`; verificado offline, nunca físicamente antes del 3.25.
- **Captura BIONZ↔Darwin** (E24-05a…h-4): ID `0x0c` arranca la máquina de 49 estados; fin = Darwin→BIONZ `0x0e`; P29/ADC-A/ADC-B sin bloqueo demostrado.
- **Silent A7S**: LIRO `0x40e3` → `+0x250` bit `0x20`; la A6000 no tiene ese selector (S401/S402). Ausencia estática ≠ incapacidad de hardware.
- **RecordStill/RecordImage** A6000 ≡ A7S salvo logs; cola `0x40193` trazada; origen del local 4/2 de `ModelScalarPb` sin resolver (E1, `NO_VERIFICADO`).

## Correcciones fundamentales (no reutilizar las versiones previas)

Trazabilidad completa: [CORRECTIONS](../docs/CORRECTIONS.md) y [STATE § Conclusiones corregidas](../docs/STATE.md).

- E26: R41 corrige R13/R37 §4/R40 §6 (consola serie en el bucle de error); R13 corrige R12 (el LED es de Loader3); R21 corrige los baudios de R8/R9/R11; R29 corrige el pinout de R11; R32 corrige «bit 0 = 0 en uso
  normal» (R20/R23); R33 corrige R23 §1; R34 corrige R23 §2; R11 corrige eSRAM 16 MiB → 1 MiB y R9 el CRC «0x07» de R8.
  R43 corrige R11/R19/R20/R29: `BOOT_SERIAL_IN` llega al pin 10 de CN4001, no al 9.
- S401 negaba el manejador LIRO `0x40e3` en la A7S: sí existe (S402). `0x90b248` es RecordImage, no RecordStill.
- Destinos BL `0x7484dc`/`0x755af8` (S382) y MOVW/MOVT de `0x40193` (S384) eran falsos. Sesgo `+0x58` de S303rev1/S304/S305 corregido.
- Carril B: S325 (posición→columna), S329 (bases T2/T3), S331 (`obj+0x2b4` = flag de log), `0x43fef404` = ids de `Camera::Lens::ODL`.
- Cadenas ≠ funcionalidad (S168, S172). S605–S627: siete gemelas erróneas y 13 textos truncados. SetImageWrited = `0x6108/0x1007`.
- E23 «`0x1fe66`→0 no desactiva el rearme» superado por E24-05. El «límite de ~65 ms» es de la ruta manual `r5`, no del firmware (E25-17).

## Decisiones técnicas vigentes

- **REA primero**, Ghidra histórico (`silent-liro.gpr`, readOnly) como respaldo; una consulta vacía de REA no prueba ausencia. Una sola
  sesión `session_daemon.py` + `q.py`; verificar lo decisivo contra bytes ([STATE § Política](../docs/STATE.md)).
- Ningún acceso físico, flasheo ni escritura en la cámara sin autorización expresa para ese caso concreto. Backup NVRAM y fila T0NN antes de cualquier prueba.
- Commit convencional por fase con PENDIENTES en el mismo commit; push a `origin/main` tras cada fase; nunca firmware, binarios de Sony ni datos personales.

## Pendientes activos prioritarios (autoridad: PENDIENTES; triaje del 07-11-2026 y R69: quedan 13)

| ID | Estado | Qué falta |
|---|---|---|
| E26-R74-FISICO | ABIERTO (R74: causa física; pruebas: sonda, flex CN4900, batería, obturador) | La pérdida (≈1,27 ms; negro desde 1/1000) no viene de Darwin. Procedimiento listo (R69 §4): leer por SWD si llega el pulso de P4C (`CA_1ST_CURTAIN_START`) al BIONZ; después, continuidad o analizador lógico | R75: referencia `B − t0`, ver E26-R75-T0.
| E25-11 | ABIERTO (consolidado) | Llevar al firmware la corrección ShutMode 0 + `r5` que hoy aplica la app; velocidades > 1/300 y < 1/15; validación en cámara |
| E26-R49-SONDA | ABIERTO (físico) | Retirar los hilos de R4911/R4912 (antes, ejecutar la lectura de E26-R66-RESET, que los usa) |
| R1 / R7 | PARCIAL / BLOQUEADO | Copia externa del respaldo; commits antiguos en `refs/pull/*` de GitHub (requiere al soporte de GitHub) |
| DOC-SITIO-EN | ABIERTO (decisión del usuario) | Sitio de Pages solo en español y con el hito 3.23; traducir/actualizar o dejarlo así |
| G2–G8 | ABIERTO | Carril de interfaz, independiente del obturador |

## Bloqueos y límites de evidencia

- Sin sembrar funciones Thumb a mano, REA no cubre `0x437…`/`0x438…`; usar Ghidra histórico para verificar bytes.
- Valores en ejecución (rectángulos `[EXL]`, Backup `0x3000b`, `params[+9]`, activación de RecordImage) no salen del binario.
- `nflasha0`, INFO6 (die0/plane1/block2) y el arranque de Darwin no están en ningún respaldo.
- Censo, número de pruebas y sesiones miden documentación y verificadores, no funcionamiento en cámara.

## Protocolo de sesión

**Al empezar:** `AGENTS.md`/`CLAUDE.md` → este archivo → pendientes relevantes en [PENDIENTES](../docs/PENDIENTES.md) → solo los informes
necesarios (`scripts/knowledge/search.py`, [INDEX](../docs/INDEX.md)).
**Durante:** `knowledge-navigation`; `contradiction-audit` antes de reutilizar un hallazgo; marcar `VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO`.
**Al terminar (en este orden):** informe en `docs/capture/` (+ prueba/evidencia) → fila de PENDIENTES → [STATE](../docs/STATE.md) si cambió una
conclusión → este archivo solo si cambió el contexto mínimo (≤ ~150 líneas; **sin bloques por sesión**: una fila en las tablas de arriba) →
una entrada en [PROGRESS](PROGRESS.md) → `python scripts/knowledge/build_subsystem_index.py` y `knowledge-maintenance` → commit y push.
El README solo cambia si cambia el estado global (tabla «Estado técnico actual» o «Último cierre»).

## Responsabilidades documentales

[README](../README.md) portada pública · **este archivo** contexto mínimo · [STATE](../docs/STATE.md) conclusiones y límites vigentes ·
[PENDIENTES](../docs/PENDIENTES.md) tareas (única fuente) · [PROGRESS](PROGRESS.md) historial cronológico ·
[INDEX](../docs/INDEX.md) informes por subsistema · `docs/capture/` informes · `analysis/` evidencia · `tests/` verificadores ·
[subproyecto](../projects/electronic-shutter/README.md) 
