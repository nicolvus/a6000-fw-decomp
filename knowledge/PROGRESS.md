# Progreso — sistema de conocimiento Sony A6000

> **E26 R9 parcial:** [revisión](../docs/capture/e26-r9-bootrom-ram-execution.md) corrige R8: CRC-32, copia por tipos distintos de 0 y 0xffff; parser R8 no válido. Falta emular la ruta, demostrar RAM ejecutable y señal física.

**R6 fase 1, checkpoint:** [BLDR](../docs/capture/e26-r6-recuperacion-bionz.md). PMCA payload local byte a byte igual a upstream 0ce3c7e8, gitlink plataforma 85bcb545. ELF extraído y REA: un safe/cuatro normales, normales die0/plane0, metadatos descartados, error => trama vacía; wrapper rechaza estado 1 de ECC tolerado por Loader2. Mapa condicional de 480 KiB con una trama normal perdida; ID/error desconocidos. Cola INFO6 die0/plane1/block2/pages0–20 sin correspondencia adquirida. Regresión inicial falló por inspector inexistente; implementado, 3 pruebas, ruff/mypy pasan. Sin cámara. Próximo paso exacto: verificar límites del selector en los primeros 43 folios y localizar orientación CN4906 en SIDE A.

## E26-RECOVERY — 29-10-2026: incidente abierto

**R8 completo offline:** [informe](../docs/capture/e26-r8-bootrom-uart-boss.md). Receptor serie BootROM reconstruido: `FUN_ffff1062` → `FUN_ffff0fa0` → `FUN_ffff0876` → `FUN_ffff0634`; MMIO `0xf2915010` bit 1; tipos 0/0xFFFF; checksum XOR+CRC8; parser offline `r8-uart-parser.py` (6/6 tests). Pines físicos UART no identificados (candidato GPIO(4,RDATA)=`0xf2910410`, CN4906 pin 9 vía R4003 XX sin continuidad verificada). No hay lectura de NAND vía protocolo. Escrituras NAND solo en Linux. INFO6 sin cambios desde R7. Seis preguntas de cierre: 1=SÍ, 2=NO DEMOSTRADO, 3=NO DEMOSTRADO, 4=NO DEMOSTRADO, 5=NO DEMOSTRADO, 6=NO. No existe ruta de recuperación sin Linux.

**R9 completo (29-10-2026):** [informe](../docs/capture/e26-r9-bootrom-ram-execution.md). Cadena BootROM→UART→RAM→salto a RAM demostrada estáticamente y en emulación Unicorn: tipo 0 hace `str(valor,[dirección])` sin validación de rango (`0xffff0bb8`, escritura RAM arbitraria); tipo 0xFFFF almacena dirección de salto de 32 bits en `0xc000500C` y `FUN_ffff0144` (`0xffff0144`: `ldr r1,[0xc0005000]; ldr r0,[r1,#0xc]; bx r0`) transfiere el control a eSRAM. eSRAM `0xc0000000–0xc0100000` (16 MiB) demostrada usable y ejecutable en tiempo de BootROM. Sin firmas ni Linux. CRC8 corregido: polinomio `0xEDB88320` (`0xffff0c04`), iterativo por byte, no placeholder `0x07`. Scripts: `analysis/e26-recovery/r9-uart-protocol.py` (parser + constructor) y `r9-unicorn-ramjump.py` (Unicorn; PC transfiere a eSRAM). Tests: `tests/test_e26_r9_*.py` (19/19 pasan). Pines físicos UART no identificados (NO DEMOSTRADO; requiere autorización física separada). Q1–Q10: Q1=SÍ, Q2=SÍ, Q3=SÍ, Q4=NO, Q5=SÍ, Q6=SÍ (emulado), Q7=SÍ, Q8=NO DEMOSTRADO, Q9=viable estática+emulada / no demostrada en hardware, Q10=identificación eléctrica del contacto UART. Sin escritura NAND, sin flasheo, sin payload en hardware físico.

**R7 completo offline (29-10-2026):** [informe](../docs/capture/e26-r7-recuperacion-estatica.md). Grafo de rutas de arranque verificado en binario: `FUN_c01f11ec` init completo (Sync,Power,UDIF,BOSS,DDR,DGU,BlkDev,FAT,Backup,Pwr2nd); modo 3=`FUN_c01f1378` carga vmlinux+initrd desde dev1 vía `FUN_c01f068a()` y salta al kernel vía `FUN_c01f04b6()`, sin entorno de recuperación independiente; modo 0xc (COLD)=`FUN_c01f09e4` carga desde dev3, fallo→`FUN_c01f3b74` bucle LED infinito sin retorno ni fallback; escrituras/borrados MuMin/LLD→ARM7 solo en entorno Linux; `boss_hw_nandc_recovery_check` 0x17b8c maneja errores NAND, no es UPDATER; no hay productor pre-Linux de `updater/mode`; INFO6 (21 páginas) sin fuente; residuo TPZL 256 sin rechazo demostrado por ARM7; escritura selectiva de `nflasha3` preservando metadatos no demostrada. Receptor serie BootROM sin red física identificada ni cadena de escritura NAND. Conclusión: no existe ruta de restauración utilizable antes de `nflasha3` con evidencia actual.

**R6 fases 2/3, checkpoint:** prefijo de 43 páginas sin cambios, REA/Capstone confirman las cinco rutinas del selector, sin reconstruir cola INFO6 ni certificar runtime. Nueva condición de log: Backup510015 debe valer1; histórico00, de modo que silencio UART no prueba falta de ejecución. Puerto0/1 y registros compatibles PL011; reloj y mux no certificados. 73 tests knowledge pasan excluyendo seis de servidor MCP (espera sin respuesta en entorno), 12 triage pasan; no cambios al servidor. Próximo paso exacto: usar dibujo SIDE A6-38 para orientación CN4906 y documentar niveles/SWD/NAND, sin conexiones.

**R6 fases 4–8, checkpoint:** manual SIDE A6-38 fija CN4906 con pin1 arriba/pin16 abajo y entorno fotografiable; se publicó mapa SVG documental. SWD BIONZ sigue opcional por R4911/R4912 XX, sin puerto, tensión, protección ni acceso NAND demostrado. BLDR/MuMin no autorizan NAND cruda; las vías restantes son Loader3 condicionado, servicio BIONZ demostrado o diagnóstico profesional que obtenga lectura repetible. Se redactó matriz conservadora: foto identificada → UART pasiva → clasificación de etapa; sin conexión, energía, escritura ni imagen firmware. Próximo paso exacto: esperar autorización física y fotografías; no hacer más inferencia de recuperación ni activar SWD.

**R5, checkpoint vigente:** [Loader3 y servicio](../docs/capture/e26-r5-loader3-servicio.md). REA + bytes amplían selector, inicialización y dependencia Backup; el recorte contiguo NO queda íntegramente validado (suma32 05c12355 frente a INFO eda2f689, tabla/runtime final incoherentes). Bandera mode sin contenido → 3; recepción alternativa SIO REIO condicionada, deshabilitada con Backup histórico 51001c=01. CN4906 A contiene UART0 BIONZ 4/5 y SWD opcional 11/12 por R4911/12 XX, además de Darwin. CompleteUpdate crea comp/borra mode; HasError y landing pads setError comprobados, éxito FIFO2=2; UI Done y ciclo uincomp pendientes. Inspector reforzado tras regresión fallida; 3 tests E26, ruff y mypy explícito sin errores. Sin fotografía local, conexión ni medición física; sin imagen instalable. Evidencia derivada en `analysis/e26-recovery/r5-rea.json`; respaldos originales privados intactos.

**Próximo paso exacto R5:** localizar la implementación de `bootloader_get_blocks`/`bootloader_read_block` en la revisión de OpenMemories-Platform usada por BLDR y reconstruir el mapa INFO 5→6; no repetir búsqueda de Loader3 ni interpretar su cola incoherente. En paralelo documental, falta manual de flash MB9AF004B y especificación física NAND. Cualquier captura propuesta espera foto, continuidad/nivel y autorización separada; el trabajo sigue offline. Pendientes E26-R5-* en el índice maestro.

Fase A: REA sobre `nand.ko` (`muminlzp_register` 0x12520, `muminlzp_request` 0x11d50) y `lld.ko` (0x11048/0x10e0c) identifica TOC, advertencia de offset y entrega ARM7; falta implementación ARM7 y nexo con lectura inicial. Tablas binarias comparadas y tres imágenes descomprimidas, tercera solo en memoria; 17 pruebas, ruff y mypy sin errores. Siguiente paso exacto: Fase B, analizar llamadores reales de `SenserUpdaterIF::setResult` en `libupdaterbody.so` y registrar argumentos y conversiones; no volver a atribuir el LED sin evidencia.

Fase B parcial: `libsenupdater.so` de initrd `nflasha1` y `mf` trazados con REA; `setResult` convierte nibbles hex y `mf` transmite por FIFO2 el valor de excepciones `0x3000c`; `BuildInPlugin::execute` acepta un resultado de shell 50 como valor 0x32. Pendiente identificar script real y conexión de excepciones, y trazar Done. Los binarios extraídos están solo en `/tmp/e26-updater/root`, no se publican.

Fase C iniciada: `config.xml`, `us_crc32sum.sh`, `us_darwin_firm.sh` y `endupdate.sh` delimitan comprobaciones, hilo Darwin y operaciones de cierre; sin orden demostrado respecto a Done. REA: `ThreadPlugin::Join` 0x23d88 ejecuta `pthread_join`; `XmlConfigHandler::Join` 0x23768 usa una llamada virtual. Próxima operación: resolver llamador del thunk 0x1db8c, destino virtual y mensaje de éxito al host; Fase B mantiene pendiente el script real del byte 0x32. El usuario informa una cara de la placa expuesta, sin acceso físico autorizado.

R3: `UpdaterBody::Execute` 0x1f4c8 → thunk 0x1db8c → `XmlConfigHandler::Join` → `ThreadPlugin::Join` 0x23d88 (objeto construido en 0x23964, vtable 0x30fa0 +0x10); después `HasError`, `EndUpdate`, `CompleteUpdate` 0x2516c y retorno. `CompleteUpdate` borra clases de banderas de modo y crea la de completo. Enlace al Done del PC pendiente. Próxima tarea: Loader2 0xc0030000 y localización de Loader3, sin repetir BootROM.

R3 Loader3: `bootloader.bin` INFO 0x18000, entradas 5→6 y candidato continuo 0x22800–0x427ff (SHA 8fd98a41…); Loader2 carga índice 5 en 0xc01f0000. REA del candidato: comprobación `\\updater\\mode` 0xc01f159a, selector 0xc01f1de6, modo 3 0xc01f1312, carga de kernel/initrd de dispositivo 1 0xc01f068a. Pendientes integridad/geométrica, modo físico y condiciones previas. Próximo paso: diagrama SIDE A/B de SY-1028 y accesibilidad de servicio.

R3 placa: manual PDF páginas 50/51 verifica CN4906 e IC6000 lado A e IC5700 y CL5701/CL701/CL703–707 lado B; esquema PDF 23 determina señales de islas. Sin foto de la cara visible ni identificación física de NAND, no se puede concluir acceso. Matriz de recuperación y siguiente diagnóstico documental en E26. Próxima operación: resolver indicador `mode`/`uincomp` y origen `Done`; validar geometría del candidato Loader3 sin escribir hardware.

El usuario informa instalación 3.25, Done y bloqueo. Comprobados hashes FDAT, Darwin y `nflasha3` locales y anomalía de alineación en el manifiesto; aún no se verifica causalidad ni lector real. Ver [informe](../docs/capture/e26-recovery.md). Siguiente paso exacto: inspeccionar con REA `uc_portctl.elf` y `SenserUpdaterIF::setResult`, y contrastar las tablas TPZL directamente con los binarios. Sin acceso físico.


## E25-24 — Selector EFCS / Electronic, auditoría parcial — 28-10-2026

Se actualizó la base a `1edcf13a` y se contrastó el informe de referencia con
E020 y E25-18–23. La opción binaria es candidata, sin implementación: B1a es
global y no hay conmutación demostrada que restaure el EFCS original. Se
registraron contradicciones sobre `r5`, C3 y el mecanismo, y los pendientes
E25-24/E25-25. Sin cámara ni pruebas físicas. Próximo paso: censar consumidores
y persistencia del selector con REA y bytes y buscar un canal por captura hacia
Darwin, antes de preparar código o solicitar pruebas físicas.

## E25-16 — Cálculo autónomo de `r5` en BIONZ — 28-10-2026

Sesión 100 % offline (bytes, REA y emulación Unicorn; sin cámara). Hallado el productor nativo de
`r5`: `0x4383fa40(record, settings)`. Lee el Tv de `record+0xf6`, el período de línea de
`record+0xc`, el VTS de `record+0x20`, el suelo de `record+0x1c` y el multiplicador de
`settings+0x4b8`; escribe `r5` en `record+0x64` y ShutMode 0 en `+0x6d`. Lo llaman el constructor
normal (`0x437b46d0`, compuerta `[cap+0x11b0]`) y el EFCS (`0x438417c0`). La foto medida no lo usa
(r5=1); `0x4383fd6c` copia `record+0x64..0x73` a `cap+0x64c` y `0x438c828c` llega a `SetExposure`
(`0x436d6320` → vtable +0x28 → `0x436d6f6c`). La emulación con VTS 4219 reproduce T047 (±1 línea:
4203/4154/3956/3122); con 4266 se desvía 47 líneas (0,71 ms). 1/15 y mayores saturan a 0 (negro), no
son compatibles; >1 cuadro, bulb y 30 s siguen sin mecanismo. No se hardcodea 4219: el diseño usa el
campo del registro; su valor real no se verificó (T052 fase A). C3 (tras `0x437f8a50`, antes de
`0x436d6320`, copia a scratch + `0x4383fa40`) es la vía lógica recomendada; no hay parche instalable.
29 pruebas nuevas; 59 con E25-14/E25-15. Informe:
[E25-16](../docs/capture/e25-16-r5-autonomo-fotografia.md).

## T052-A — VTS real y preparación de C3 — 28-10-2026

**No ejecutada físicamente:** la cámara no era accesible (PC en `192.168.0.0/24`, sin ruta a
`192.168.1.29`, sin `adb`/`pmca`; barrido sin shell). Sin escrituras. Se completó A0 y la emulación, y
se usó el volcado real del 20-10 (1 GiB, reposo, sin foto) para confirmar el mapa: GOT
`0x4401eee4`; registro A `0x43ea5b4c`, B `0x43eee770`, ajustes `0x43f79f94`, imager `0x43ea976c`,
gate B `0x43f6e5c2`, predicado `0x43deb360`. **VTS:** `record+0x20 ← cap+0x5e0 ← [descriptor+6]`
(`0x43846e12`; descriptor en `[param+0x3c]` de `0x43844e80`); 4219 no es constante y 4266 solo lo
produce la vista en directo (`0x4385de94`); el valor de foto sigue **N**. **Compuerta:** `0x437b3b08`
la deriva de `[imager+0x504]==3` o `[gate B+0x8c]==1` (2 fuerza 0); en reposo 2/0 → 0. **Correcciones:**
el 2.º argumento del productor es el imager (`+0x4b8`), no `settings`; el productor escribe también
`+0xd8/+0xda/+0xdc`; el predicado `0x43a12ca8` lee `[0x43deb360+0x10]` y en reposo devuelve 1 → suma
un cuadro (r5 8422/8175/7341, inválido). C3 **no autorizada**; T052-B0 de solo lectura primero.
22 pruebas nuevas; 81 con E25-14/15/16. Informe:
[T052-A](../docs/capture/t052-a-parametros-reales.md).

## E25-14 — Temporización IMX235/IMX210 — 28-10-2026

Sesión 100 % offline (solo bytes; sin cámara ni emulación de sensor). Reconstruida la cadena Silent del
IMX235: `cap+0x648` → `SetExposure` (`0x436f4168`; `param+0`=SHR/líneas, `param+9`=ShutMode) y
`cap+0x6b0` → método de velocidad (`0x436f4a94`, `vtable+0x30`) → bloque de comandos. La A6000 tiene el
mismo contrato (`0x436d6f6c`/`0x436d7e08`), la misma tabla de tiempos (30 filas idénticas) y **ya llama
al método `+0x30` en la foto** (`0x438c831e`); lo que no usa es ShutMode 0. El armado de exposición
larga del A7S (`0x436f43c0`, `obj+0x3dc=2`, `0x43b73044(0xe)`, tercer argumento `r3`) no tiene
equivalente en el método del IMX210. El límite de ~65 ms es también del firmware (clamp a un cuadro);
no se demostró ningún modo de sensor con cuadro más largo ni acumulación multicuadro. **A=SÍ, B=NO,
C=NO, D=NO, E=NO, F=PARCIAL, G=NO, H=NO, I=NO, J=NO, K=SÍ, L=NO, M=NO.** 13 pruebas en
`tests/test_e25_14_exposicion.py`. Informe:
[E25-14](../docs/capture/e25-14-imx235-imx210-exposicion-electronica.md).

## E25-06 — Auditoría independiente de los paquetes 3.23 (B1a) y 3.24 — 27-10-2026

Auditoría 100 % offline del commit `88ce09ef` (paquetes de DeepSeek). Parsers propios de `.dat`, FDAT y
tar; descifrador AES propio validado contra el `.dat` original de Sony; `uc_crc32sum` reproducido sobre
los 7 `*.sum`; B1a emulado con Unicorn frente al tipo 0 y al original (retorno 0 en 259 entradas, sin
`0x1b080`, L0 en los tres arrancadores, escritores P4D/P4E filtrados con control positivo, comprobación
de leva suprimida, operación 5 sin cambios). **145 comprobaciones, 0 fallos; 21 pruebas (15
negativas).** A–K = SÍ, L = NO (sin defecto binario), M = NO (las pruebas de E25-05 pasan sin paquetes:
2 passed / 9 skipped; el manifiesto no puede registrar FAIL; hay comprobaciones de constantes), N = SÍ,
O/P/Q/R = NO por evidencia insuficiente. 3.24 vs 3.23: rangos del `.dat` predichos desde el formato =
reales. Riesgos comprobados: R4, R5, R6, R7 (dos 3.23 con `config-323.yaml` idéntico) y R8 (el
inventario R1 no tiene los paquetes nuevos). Nuevo pendiente E25-07. Informe:
[E25-06](../docs/capture/e25-06-auditoria-independiente-paquetes.md).

## E25-05 — Paquetes offline 3.23 (B1a) y 3.24 (recuperación) — 27-10-2026

Sesión 100 % offline sobre `81fab68e`; no se conectó la cámara ni se flasheó nada. **Plan de versiones
corregido**: con 3.22 instalada, `3.22 < 3.23 < 3.24`; la prueba pasa a 3.23 (tipo 0 + B1a) y la
recuperación a 3.24 (Darwin oficial). El antiguo `recuperacion-323` queda superado (misma versión que la
prueba) y se conserva intacto. Paquetes en directorios separados: `experimental-323` (`.dat`
`4c21353d…`, `.fdat` `268621fb…`; tar oficial + B1a + `darwin.sum` `cf930ac9`) y `recuperacion-324`
(`.dat` `e1345aff…`, `.fdat` `24ee9b42…`; payload oficial extraído del 3.23 verificado). **69
comprobaciones, 0 fallos**: DEND, CRC de cabecera FDAT, sumas por bloque, hashes, modelo `0x41030035`,
región 0, versiones BCD `0x23`/`0x24`, `fwtool unpack`. B1a vs tipo 0 = **exactamente 2 bytes**
(`0x1fe6a: 28 46 → 0a e0`); tar experimental solo cambia los dos ficheros Darwin; el 3.24 vs 3.23 solo
difiere en cabecera (`[8,12)`, `[32,33)` en `.fdat`; dos bloques AES + CRC DEND en `.dat`). **Rollback
limitado**: el 3.24 solo funciona si la cámara conserva acceso al actualizador; no es recuperación
independiente del MCU y no está demostrado que recupere un Darwin defectuoso. B1a sigue sin ser
instalable (E25-04 G=NO). Script `scripts/e25_05/build_packages.py`, 11 pruebas, manifiestos en
`analysis/e25-05/`. Informe: [E25-05](../docs/capture/e25-05-preparacion-paquetes-323-324.md).

## E25-04 — Recuperabilidad de Darwin y decisión sobre B1a — 27-10-2026

Auditoría 100 % offline (base `9d85cae9`). **A=NO, B=NO, C=NO, D=NO, E=SÍ, F=NO, G=NO.** No hay
recuperación independiente de la aplicación Darwin demostrada: el USB depende de `DD_ON1/2/3` de
`darwin_core`, el acceso al bootloader sin la aplicación no está demostrado y el puerto físico
(`MD0_DWN`, `XDWN_RESET`, UART, SWD, `CN4906` no montado) está documentado pero no verificado. El plan
3.24/3.25 es formalmente correcto, pero el 3.23 no recupera un Darwin defectuoso y, si se instala 3.24,
la recuperación debe ser ≥3.25. R1: procedimiento `scripts/recovery/r1_manifest.py` + inventario;
manifiesto local 62/62, 0 requeridos ausentes, `verify` OK contra el origen; **la copia externa no está
hecha ni verificada**, así que R1 sigue abierto. F = NO: L0 no tiene contradicción estática con BIONZ
(estado 9 libera el bit 24, el 10 es terminal, los mensajes obligatorios salen de la máquina de captura,
el estado 31 no cambia); P29, `pkt[2..3]` y el lector BIONZ del fin siguen abiertos. Pruebas nuevas:
`tests/test_e25_04_recuperabilidad.py` (2) y `tests/test_r1_manifest.py` (6); 239 pruebas E24/E25 verdes.
No se generó FDAT, no se tocó B1a y no se abrió la cámara. Informe:
[E25-04](../docs/capture/e25-04-recuperabilidad-y-decision.md).

## E26-R10 — USB Charger `054c:0994` como ruta de recuperación (29-10-2026)

- **Objetivo:** investigar si el único dispositivo USB que enumera en la a6000 bloqueada (054c:0994, cámara apagada) permite una ruta de recuperación que evite la intervención física UART.
- **Componente identificado con evidencia de binario:** **Darwin** (FM3). `darwin_core.bin` contiene el descriptor USB completo con VID `0x054c`, PID `0x0994`, clase HID, EP1 IN interrupt de 8 bytes y cadenas "Sony"/"USB Charger". Validación offline contra `lsusb -v`: **todos los campos coinciden** (script `analysis/e26-recovery/r10-usb-descriptor-parse.py` + 4 tests `tests/test_e26_r10_usb_charger.py`, 4/4 pasan). `bootrom.bin` **no** contiene `0x0994`/`0x054c` (búsqueda negativa).
- **Tres modos USB confirmados:** normal `054c:07c4` (MSC/PTP, cámara encendida), updater `054c:03e2`, charging `054c:0994` (Darwin, cámara apagada). `CMD_SWITCH_MODE = 0x30` (PMCA) pertenece a las interfaces `07c4`/`03e2`, **no** a `0994`; no hay relación demostrada.
- **Hallazgos clave:** la interfaz HID declara **solo un informe Input de 1 byte** (sin Output ni Feature, sin canal host → dispositivo). No se localizó el manejador de solicitudes de control (SETEP) ni peticiones vendor-specific de Sony en `darwin_core.bin`. El módulo DWN de Darwin (`DWN_VER0.78` + tabla de salto de 20 punteros en `0x021950`) es **pista futura no demostrada** (no demostrado USB-accesible ni capaz de cambiar modo). No existe cadena demostrada desde USB Charger hasta escritura de RAM, salto a ejecución o activación de Updater Mode.
- **Decisión de cierre: Opción B** — abandonar provisionalmente la ruta USB Charger y concentrar la recuperación en BootROM UART de R9. Respuestas Q1–Q10: Q1=SÍ, Q2=SÍ(binario)/NO(físico), Q3=NO, Q4=NO, Q5=PARCIAL, Q6=NO, Q7=NO, Q8=NO DEMOSTRADO/NO, Q9=módulo DWN no demostrado, Q10=priorizar BootROM UART.
- **Entregables:** `docs/capture/e26-r10-usb-charger-recovery.md`, `analysis/e26-recovery/r10-usb-descriptor-parse.py`, `tests/test_e26_r10_usb_charger.py`. Sin cámara, sin escritura, sin flasheo, sin intervención física.

## E26-R11 — Acceso físico al BootROM UART (29-10-2026)

- **Hallazgo:** esquema pág. 38: `BOOT_SERIAL_IN` → `MULTI pin 9 UART_RX/BOOT_IN` (CN4001) vía R4003/R4002, ambas `XX`. CN4906 pin 4 = `DEBUG_UART0_RXD` (montaje no verificado). CN4906 pin 9 ≠ Multi Terminal pin 9.
- **Selector BootROM:** `0xf2915010` bit 1 es estado externo leído; condición de activación, niveles y baudios no determinados.
- **Auditoría R9:** eSRAM 1 MiB (`0xc0000000–0xc0100000`), `0xEDB88320` = CRC-32 reflejado, salto indirecto compatible con la carga de prueba; válida offline, sin hardware.
- **Decisión C.** Q1–Q8=NO, Q9=PARCIAL, Q10=SÍ, Q12=CN4906. Pendiente `E26-R12-UART-FISICO`.
- **Entregables:** `docs/capture/e26-r11-bootrom-uart-physical-access.md`, `analysis/e26-recovery/r11-pinout-reconstruction.py`, `tests/test_e26_r11_pinout.py`. Sin cámara, sin UART, sin intervención física.

## E26-R12 — Auditoría estática del arranque (30-10-2026)

- **Selector:** MODEREG `0xf2915010` bit0 (`ffff1094..109e`); 1 → serie, 0 → almacenamiento. Registro externo.
- **LED:** BootROM ≤ 2 lentos; Loader2 −302 → 0/3/2 (hipótesis para el patrón 3+2). Corrección R7 `0xfffffed1`→`0xfffffed2`.
- **Darwin:** `PwrCtrl` Fase1..4, watchdog virtual, SIO `mss` (hipótesis hacia BIONZ).
- **Entregables:** `docs/capture/e26-r12-bootrom-static-audit.md`, `analysis/e26-recovery/r12-loader2-led-codes.py`, `r12-selector-emulation.py`, `tests/test_e26_r12_led_codes.py`.

## E26-R13 — Procedencia del error LED (30-10-2026)

- **Identidad:** `FUN_c01f3b74` = Loader3 (corrige R12); gemela Loader2 `c0030c7c` con `err−1000`.
- **−302:** 7 funciones, 9 cargas; 3 devuelven −306. Propagan al LED: BOS `c01f2c98` y CFG `c01f2f24`.
- **Tiempos:** `d`=2,0 s (timer DIV2, entrada 4 MHz según cabeceras Sony; sin medir). Ciclo de −302 = 8,0 s.
- **Entregables:** `docs/capture/e26-r13-led-error-provenance.md`, `analysis/e26-recovery/r13_loader3.py`, `r13-led-provenance.py`, `tests/test_e26_r13_led_provenance.py`. Pendientes `E26-R14-RAMCFG`, `E26-R14-LED-MEDIDA`.

## E26-R14 — RAMCFG, BOS y FAT de Loader3 (30-10-2026)

- **RAMCFG:** Backup BK4 `0xfa0080`, 64 entradas de `0x90` B (6 usadas); idéntico en 55 BK4 (volcados, `nflasha2`, paquetes 3.21/3.25).
- **Particiones:** 2 = FAT12 (`\Backup.bin`, `\kemco.txt`); 3 = TPZL→FAT12 (resto). BOS sector 0 = `8246`.
- **−302:** `c01f4690` convierte todo fallo de sector en −302; BOS: lectura −1, firma −302; Backup no en estado 1 → −303.
- **Entregables:** `docs/capture/e26-r14-ramcfg-bos-analysis.md`, `analysis/e26-recovery/r14_backup.py`, `r14-ramcfg-bos-fat.py`, `tests/test_e26_r14_ramcfg_bos.py`. Pendientes `E26-R15-*`.

## E26-R15 — TPZL de Loader3, firmware 3.25 propio y c01f2282 (30-10-2026)

- **Procedencia:** 3.25 = paquete propio (E25-27) sobre 3.21 oficial; 4 de 73 miembros del tar difieren; `updater.img` oficial; Loader/Backup/kernel intactos. Sin logs de instalación.
- **Lector TPZL:** registro `c01fe4ec`, petición `c01fdd8e`; residuo ≠ 0 solo avisa; sectores `(res+tam+0x1ff)>>9`. Las 3 imágenes pasan.
- **`c01f2282`:** omite solo si Backup `0xfa0033` ∈ {1,2}; vale `0x80021048` en 55 BK4 → nunca.
- **Entregables:** `docs/capture/e26-r15-tpzl-custom-fw325.md`, `analysis/e26-recovery/r15_tpzl_loader3.py`, `r15-mode-table.py`, `tests/test_e26_r15_tpzl.py`. Pendientes `E26-R16-*`.

## E26-R16 — Ruta LDEC/BOSS/ARM7 del TPZL 3.25 (30-10-2026)

- **Ruta:** Loader3 `c01fdd8e`→`c01fce8c`→MuMin→SRAM ARM7 `+0x3f40`→BossFirm `0x1338`→LDEC `0xf2903000`; sin descompresor software en Loader3. `0x2800` (NAND/firmware) excluido del grafo.
- **Diferencia nueva (decisión C):** 100 % del corpus Sony = 16 segmentos × 4096 B por bloque (`size>>12`=16 va al registro `+0x0c`); bloques 0/48/57 del 3.25 = 1 × 65 536 B. Sin rechazo demostrado.
- **Límites:** 129 sectores funcionan (Sony `nflasha15/16`); ARM7 trocea en lotes de 0x80; residuo copiado y no leído en lo analizado.
- **Conciliado:** 89 B BIONZ + 22 B Darwin = 111; `c01f7752` no carga archivos ni da −302; fallos `tests/knowledge` desde R7 (`a8a182c9`).
- **Entregables:** `docs/capture/e26-r16-ldec-hardware-audit.md`, `analysis/e26-recovery/r16_*.py`, `tests/test_e26_r16_ldec.py`. Pendientes `E26-R17-*`.

## E26-R17 — BossFirm ARM7 y semántica LDEC (30-10-2026)

- **ARM7:** todo ARM; despachador `0xec8` (`bx r1`) sobre 18 punteros `0x379c`; op 0 = `0x1338`. LDEC (`0xf2903000`) solo en `0x3f4` (config), `0x43c` (ISR, errores `0x28–0x2d`), `0x4d8` (arranque).
- **Hallazgos:** `+0xc` se escribe una vez desde `trabajo+0xc` y no se lee ni compara; `trabajo+8` sin lector en la op 0; tulist síncrono por tanda de 0x80 (`0x5f8` sondea `[0x378c]`).
- **Decisión C.** No ejecutado: corpus Sony externo (`E26-R17-TPZL-1SEG` abierto), trazado de otras ops (`E26-R18-ARM7-RESTO`).
- **Entregables:** `docs/capture/e26-r17-arm7-ldec-segment-analysis.md`, `analysis/e26-recovery/r17_arm7_full.py`, `tests/test_e26_r17_arm7.py`.

## E26-R19 — capa USB de Darwin y esquema de arranque (30-10-2026)

- **Pedido:** avanzar hacia una vía de arranque/actualización; USB Charger, Multi, CN4906 por código; luego resolver el callback USB de clase/vendor.
- **Hallazgos:** mapeo dirección = archivo + `0x4200` (primera pasada lo ignoró y dio rutinas desalineadas; corregido). EP0 `0xc90a`; callback `0xc59c`: GET_DESCRIPTOR HID, GET_REPORT, SET_IDLE; vendor parado; sin OUT; Darwin sin flash/MFS en código; DWN (`0x2f50–0x4ba8`) sin referencias. Esquema: `CM4002/CM4003` en paralelo a R4002/R4003 XX (patrón de montado) → Multi pin 9 ↔ `BOOT_SERIAL_IN` probable (corrige R11); `BOOT_MAIN`→CL1000 candidato a bit 0 de `MODEREG`; CN4906 no llega a `BOOT_SERIAL_IN`.
- **Decisión:** USB Charger cerrado (límite documentado); resto C. REA no reconoce el Thumb de `darwin_core.bin`; desensamblado con Capstone y emulación Unicorn.
- **Entregables:** `docs/capture/e26-r19-darwin-usb-static.md`, `analysis/e26-recovery/r19_darwin_usb.py`, `r19_darwin_usb_emu.py`, `tests/test_e26_r19_darwin_usb*.py`.

## E26-R20 — selector del BootROM (30-10-2026)

- **Pedido:** reconstruir `ffff1062–109e`.
- **Hallazgos:** el BootROM es `Musashi Loader1 Ver.01.00` (2011). Selector = `MODEREG` bit 0 (0 → Loader2; 1 → ruta de servicio). GPIO(4,RDATA) bit 21 = juego de temporización, bit 22 = salto directo a la recepción serie. Con bit0=1 y GPIO4.22=0: fallo de almacenamiento/cabecera o tabla de claves vacía → serie; clave presente → hay que enviarla (4 B + CRC-32 `0xEDB88320`), sin datos → payload alternativo. Bit 0 = `BOOT_MAIN` (CL1000) por exclusión y por el registro hermano CXD4132; por defecto 0 en uso normal.
- **Verificación:** REA (descompilación de `main`), Capstone y emulación Unicorn con auxiliares sustituidas (9 escenarios, 4 pruebas).
- **Pendientes:** `E26-R20-BOOTMAIN-NIVEL` (físico), `E26-R20-KEYTABLE`, `E26-R20-GPIO4`.
- **Entregables:** `docs/capture/e26-r20-bootrom-selector.md`, `analysis/e26-recovery/r20_bootrom_selector.py`, `tests/test_e26_r20_bootrom_selector.py`.

## E26-R20-KEYTABLE — mecanismo de la tabla de clave (30-10-2026)

- **Pedido:** resolver `E26-R20-KEYTABLE`.
- **Hallazgos:** `0xffff1352` (llamada desde `0x150/0x332`) es un lector real de sectores de `0x600` B desde un controlador de bloque en `0x20000` (FIFO `0x10000010`), con reintentos; solo pone a 0xFF un array de estado por sector (`memset` vía `0xffff1814`), no el buffer de datos. El sector que correspondería a `0xc0001200` vive en la partición `nflasha0` (área de boot/loader1), que según `analysis/camera-dumps/nand-20261020/README.md` **no tiene nodo de dispositivo Linux y nunca se volcó**; `bootloader.bin` (paquete `EXBL`) es una etapa posterior sin relación con esa zona.
- **Decisión:** C — mecanismo cerrado estáticamente; contenido («vacía»/«con clave») no determinable sin volcado físico/JTAG del área de boot.
- **Entregables:** `docs/capture/e26-r20-keytable.md`, `tests/test_e26_r20_keytable.py`.

## E26-R19/R20 — cierre estático de pendientes restantes (30-10-2026)

- **Pedido:** cerrar de forma estática `E26-R19-USB-EVT13`, `E26-R19-CM-MONTAJE`, `E26-R20-BOOTMAIN-NIVEL` y `E26-R20-GPIO4`.
- **Hallazgos:** `post(0x13)` = registro de traza; EP1 IN único; `CM4002/3` montados por convención; `BOOT_MAIN` sin pull externo; GPIO4 bit21 elige entre dos tablas de muestreo serie por software (250/84 ticks por bit), bit22 salta a serie.
- **Límites:** baudios absolutos, pines de GPIO(4) y nivel de `BOOT_MAIN` no determinables sin hoja de datos del IC6000 o medición.
- **Entregables:** `docs/capture/e26-r19-r20-cierre-estatico.md`, `tests/test_e26_r19_r20_cierre.py`.

## E26-R21 — receptor serie del BootROM (30-10-2026)

- **Pedido:** seguir con lo hallable sin mediciones físicas.
- **Hallazgos:** código Sony del SoC (`mach-cxd90014`) confirma `MODEREG` bit 1 = `BOOT_SERIAL_IN`; `0x634` es un receptor serie por software (8 datos + paridad impar + parada); tablas de 250/84 ticks por bit ≈ 16 000/47 600 baudios con reloj base 4 MHz.
- **Límite:** reloj del temporizador inferido de Linux; pin de GPIO(4) bit 21 desconocido.
- **Entregables:** `docs/capture/e26-r21-bootrom-rx-serie.md`, ampliación de `tests/test_e26_r19_r20_cierre.py`.

- **R21 ampliación:** descubierto el tren de sincronismo de 60 flancos previo a los bytes (corrige «sin sincronización» de R8/R9) y validado con `analysis/e26-recovery/r21_rx_emulation.py` (Unicorn, ROM real; ambos perfiles aceptan 8O1, rechazan periodo/paridad/flancos erróneos).

## E26-R22 — mapa completo del BootROM (30-10-2026)

- **Pedido:** identificar todo el BootROM de principio a fin.
- **Hallazgos:** 57 rutinas (0xffff0000–0xffff1a80) nombradas; capa de carga de bloques, claves, consola/traza, CRC, `printf`; reloj de 4 MHz verificado por las dos variantes del parpadeo de error.
- **Límite:** nombres propios; `0x2001–0x2005` y pasos de traza sin asociar a condiciones concretas.
- **Entregables:** `docs/capture/e26-r22-bootrom-mapa-completo.md`, `analysis/e26-recovery/r22_bootrom_map.py`, `tests/test_e26_r22_bootrom_map.py`.

## E26-R23 — flujo completo de main/serial_entry, cierre total del BootROM (30-10-2026)

- **Pedido:** no detenerse hasta obtener todo el BootROM.
- **Hallazgos:** pseudocódigo línea a línea de `main` y `serial_entry`; 109 pasos de traza y 25 códigos de error resueltos a su sitio emisor exacto; corrige R12 §3 (cabecera dañada desvía a `serial_entry`, no es éxito aparente).
- **Cierre:** el BootROM queda completo en estático; lo que falta es físico (`E26-FISICO-BOOT`).
- **Entregables:** `docs/capture/e26-r23-bootrom-flujo-completo.md`, `analysis/e26-recovery/r22-trace-steps.json`, `analysis/e26-recovery/r22-error-codes.json`, `tests/test_e26_r23_bootrom_flujo_completo.py`.

## E26-R24 — mapa completo de Loader2 (30-10-2026)

- **Pedido:** seguir con Loader2 (`bootloader.bin`), completo.
- **Hallazgos:** 247/247 funciones localizadas y con rol; secuencia de arranque `loader2_main` completa por cadenas `LDR:`/`BOS:`/`INS_E:`; entrada ARM→Thumb verificada por bytes; handoff a Loader3 (`0xc01f0000`); confirma −306→1/3/6 (R13) y el temporizador de 4 MHz (R22) de forma independiente.
- **Límite:** 153 funciones de soporte (RTOS interno) solo inventariadas por dirección/grafo, no narradas una a una.
- **Entregables:** `docs/capture/e26-r24-loader2-completo.md`, `analysis/e26-recovery/r24_loader2_map.py`, `r24-loader2-functions.json`, `r24-boot-sequence.json`, `tests/test_e26_r24_loader2_map.py`.

## E26-R25 — mapa completo de Loader3 (30-10-2026)

- **Pedido:** seguir con Loader3, completo si falta algo.
- **Hallazgos:** 674/674 funciones localizadas y con rol; vectores de excepción (toda excepción -> LED directo, sin boot_dispatch); `log`/consola con la misma forma que Loader2; capas BOS/CFG/FAT/TPZL de R13/R15/R16 ahora con dirección fija en el mapa; candidato `LD3:<< KEY E… >>` para E26-R20-KEYTABLE, no explorado.
- **Límite:** INFO 6 (21 páginas) no adquirida; 256 funciones de soporte solo inventariadas.
- **Entregables:** `docs/capture/e26-r25-loader3-completo.md`, `analysis/e26-recovery/r25_loader3_map.py`, `r25-loader3-functions.json`, `r25-boot-sequence.json`, `tests/test_e26_r25_loader3_map.py`.

## E26-R26 — updater\mode (gate verificado) y descarte de la clave PwrIC (30-10-2026)

- **Pedido:** continuar con los 4 pendientes estáticos restantes.
- **Hallazgos:** `boot_dispatch` indexa un valor 0-14 persistido en Backup; `\updater\mode` (dispositivo 2 = nflasha2) es condición necesaria verificada por bytes (su ausencia fuerza modo 3, cadena normal); la cadena `LD3:<<KEY E/L/D>>` es de autenticación de batería, no de arranque — descartada para E26-R20-KEYTABLE.
- **Cierre:** E26-R7-C-UPDATER-MODE CERRADO PARCIAL (mecanismo de lectura resuelto, sin productor pre-Linux); nueva fila E26-R20-KEYTABLE-PWRIC DESCARTADA.
- **Entregables:** `docs/capture/e26-r26-updater-mode-y-clave-pwric.md`, `tests/test_e26_r26_updater_mode.py`.

## E26-R27 — ARM7: ISR NAND y geometría (30-10-2026)

- **Hallazgos:** ISR `0xd24` traduce bits de estado del controlador NAND a códigos propios (0xc/0xd/0x20/0x21/0x23/0x24); `0x1a80-0x1ae4` implementan capacidad y traducción de direcciones con entrelazado multi-plano; las 17 operaciones restantes del despachador comparten la base SRAM `0x3f40` de op 0.
- **Límite:** sin clasificar el comando NAND de cada una de las 17 operaciones.
- **Cierre:** E26-R18-ARM7-RESTO CERRADO PARCIAL.
- **Entregables:** `docs/capture/e26-r27-arm7-isr-geometria.md`, `tests/test_e26_r27_arm7_isr_geometria.py`.

## E26-R28 — búsqueda externa de TPZL (30-10-2026, resultado negativo)

- **Pedido:** continuar con el último de los 4 pendientes estáticos (Prioridad E de R17, no ejecutada).
- **Hallazgos:** sin mención pública de «TPZL» en GitHub ni en la web; Sony-PMCA-RE y fwtool solo cubren el actualizador (FDAT), no el BootROM/Loader2/Loader3.
- **Cierre:** E26-R17-TPZL-1SEG CERRADO con resultado negativo documentado; no hay muestras externas con las que construir la tabla pedida.
- **Entregables:** `docs/capture/e26-r28-tpzl-busqueda-externa.md`.

## E26-R29 — pinout completo de CN4001/CN4906, dos correcciones a R11 (30-10-2026)

- **Pedido:** mapear todos los pines del PDF a su red correspondiente (alcance acordado: CN4001 y CN4906).
- **Hallazgos:** CN4001 es de 19 pines (1=VBUS, no D-; faltaba pin3=D+); CN4906 es de 18 pines, no 32 (los «31/32» eran de otro conector de la misma hoja); CN4906 combina BIONZ+Darwin: pines 11/12/15 unen SWCLK/SWDIO/VIO_FLD con TCK_DWN/TMS_DWN/XDWN_RESET; pin10=RTCK sin red externa.
- **Método nuevo:** `analysis/e26-recovery/r29_pinout_pixel_trace.py` sigue columnas de píxel sobre el render a 600 dpi para resolver cableado que cruza filas (el agrupador por fila existente no lo distingue).
- **Entregables:** `docs/capture/e26-r29-pinout-cn4001-cn4906-completo.md`, `tests/test_e26_r29_pinout_cn4906.py`, correcciones en `analysis/e26-recovery/r11-pinout-reconstruction.py` y `docs/capture/e26-r11-bootrom-uart-physical-access.md`.

## E26-R20-SERIE-PLAN — síntesis del plan de recuperación por serie (31-10-2026, sin evidencia nueva)

- **Pedido:** evaluar si "llevar `CL1000` a 1 y enviar el bloque de arranque por el pin 9" repara la cámara, recombinando R19/R20 sin abrir la carcasa.
- **Hallazgos:** el árbol de decisión de R20 confirma por bytes que `MODEREG` bit 0=1 (`CL1000`/`BOOT_MAIN`, mapeo por inferencia) es necesario pero no demostrado suficiente; el resultado encadena tres datos físicos ya cerrados por separado (`E26-R20-BOOTMAIN-NIVEL`, `E26-R20-GPIO4`, `E26-R20-KEYTABLE`), ninguno medido.
- **Límite:** solo estático; no resuelve ningún dato físico nuevo, solo documenta por qué no son cerrables sin acceso a la cámara.
- **Cierre:** `E26-R20-SERIE-PLAN` permanece ABIERTO (síntesis, sin nueva evidencia); coincide con el criterio de cierre de `E26-FISICO-BOOT`. Segundo commit reescribe el informe con vocabulario neutro de recuperación de hardware (sin cambiar hechos, direcciones ni conclusión).
- **Entregables:** `docs/capture/e26-r20-serie-plan.md`.

## E26-R31 — cierre estático de `MODEREG` bit 0 = `BOOT_MAIN` (31-10-2026)

- **Pedido:** cerrar estáticamente la inferencia de R20 §1.6 (bit 0 = `BOOT_MAIN`/`CL1000`).
- **Hallazgos:** inventario completo de lectores de `MODEREG`: BootROM (bit 0 selector, bit 1 serie), Loader3 `0xc01f4ef8` (solo lo registra en bruto), `mcmn_drv.ko` («MODEREAD»: bit 16 `MSX_INS_HIZ`, 24–27 CD/WP MMC); `vmlinux`/`av-cam`/Loader2 no lo leen (`av-cam` barrido también por `movw/movt`: 0 `movt #0xf291`, control positivo 216 `movt #0x43bd`). Bloque BOOT del IC6000 = `DDRCKSEL`/`BOOT_SERIAL_IN`/`BOOT_MAIN` (A6000 y A6300). `DDRCKSEL` sin consumidor software (y en bit 24 en CXD4132); `MODEREAD_BM1` = bit 1 en CXD4132 → BM0 = bit 0 = `BOOT_MAIN`.
- **Límite:** deductivo; ninguna fuente Sony nombra el bit 0. Polaridad/pull físico siguen en `E26-FISICO-BOOT`.
- **Cierre:** `E26-R19-BOOTMAIN` → CERRADO (R31, estático).
- **Entregables:** `docs/capture/e26-r31-bootmain-bit0-cierre.md`, `tests/test_e26_r31_bootmain_bit0.py`.

## E26-R32 — valor real de `MODEREG` en la cámara (31-10-2026)

- **Pedido:** confirmar con los datos existentes en qué estado está siempre `CL1000`.
- **Hallazgos:** Loader3 (`0xc01f4ef8`, `LD3:read MISCREG`, llamada incondicional en `0xc01f11e4`) escribe TYPEID, `[0xf2912b10]` y `MODEREG` en el backup (IDs `0x3e0003/9/a`, 2 bytes). En los 23 `backup*.bin`: `0x0500` (= `TYPEID_CXD90014`), `0x0010`, **`0x0003`**; la plantilla `0110_backup` trae `0x00ff/0/0`. → bit 0 = 1 y bit 1 = 1 en reposo. Bytes del BootROM: con bit 0 = 1 y clave presente, la ventana serie (`0x876`) sin sincronismo (`0x3001`) salta a `0x1226` (`load_payload` → salto): ese es el arranque normal.
- **Correcciones:** R20 §1.6 y R23 §1 («bit 0 = 0 en uso normal»). `E26-R20-BOOTMAIN-NIVEL` → CERRADO (dato de cámara); `E26-R20-KEYTABLE` → inferencia fuerte «con clave»; `E26-R20-SERIE-PLAN` → CERRADO (el paso «`CL1000` a 1» sobra; la vía serie exige la clave de `nflasha0`).
- **Límite:** el valor lo lee Loader3, no el BootROM; solo 16 bits; polaridad pin↔bit no probada.
- **Entregables:** `docs/capture/e26-r32-moderreg-valor-real.md`, `tests/test_e26_r32_moderreg_backup.py`.

## E26-R33 — veracidad de la clave de `nflasha0` (31-10-2026)

- **Pedido:** examinar si es cierto que la clave de arranque serie está en `nflasha0`.
- **Hallazgos (bytes del BootROM):** `load_header` lee 3 sectores de `0x600` B del bloque 0 a `0xc0000600`; la tabla `0xc0001200` es el tercero → `nflasha0`. `find_key` (`0x39c`) devuelve 0 si **alguna** de las `0x180` palabras ≠ `0xFFFFFFFF` y copia las dos primeras. Sin clave y sin serie: receptor `0x3002` → `0x3001` → `serial_entry` → LED `0x1001`. Formato válido emulado con `0xc52`: palabra 0 = clave, palabra 1 = `~crc32(clave)`.
- **Correcciones:** R32/`E26-R20-KEYTABLE` precisados («sector no borrado», no «clave válida»); R23 §1 con condiciones invertidas; R12 §3 vigente.
- **Límite:** valor y formato reales solo con lectura del bloque 0 (`E26-R33-BLOQUE0`, nuevo).
- **Entregables:** `docs/capture/e26-r33-veracidad-clave-nflasha0.md`, `tests/test_e26_r33_clave_nflasha0.py`.

## E26-R34 — `serial_entry` emulado con todas las combinaciones de banderas (31-10-2026)

- **Pedido:** emular `serial_entry` con todas las combinaciones de banderas (continuación de R33).
- **Hallazgos (bytes + emulación Unicorn, sustitución de llamadas):** `get_flag1()` se lee hasta 3 veces en puntos distintos: 1.ª lectura ==1 salta la recepción entera (va directo a la sección de salto); 2.ª lectura !=0 (cualquier valor) es error `0x1001` directo; tras aceptar un paquete (`rx_packet()==0`), una 3.ª lectura ==0 es también error `0x1001`, no un reintento. Confirmado por bytes: solo dos saltos llegan a la llamada de recepción (`0xfb8`, `0x1032`); ninguno sale del tramo de error ni del de aceptación. `get_flag0()!=0` es error (sentido opuesto al de la misma bandera en `main`, ya documentado en R23, confirmado aquí).
- **Corrección:** R23 §2 tenía un bucle de reintento inexistente y mezclaba dos tramos bajo una sola etiqueta `REGISTRO_MOTIVO`.
- **Límite:** `serial_receiver`/`rx_packet` sigue tratado como caja sustituible (su lógica interna es de R9/R21); no se emuló la forma de onda real.
- **Entregables:** `docs/capture/e26-r34-serial-entry-flags.md`, `analysis/e26-recovery/r33_serial_entry_flags.py`, `tests/test_e26_r34_serial_entry_flags.py`.

## E26-R35 — `serial_receiver` recibe varios paquetes por llamada (31-10-2026)

- **Pedido:** revisar si `rx_packet`/`serial_receiver` (`0x876`) puede recibir varios paquetes en una sola llamada (seguimiento de R34, donde quedó como caja sustituible sin examinar).
- **Hallazgos (desensamblado completo de la función, 279 instrucciones, dos tramos separados por un pool de literales en `0x944–0x99f`):** tras procesar un paquete, `fp==0` (primer paquete) fuerza siempre otra vuelta a `0x89c` (resincronizar), sea el tipo que sea. Solo con `fp==1` y el tipo del paquete actual igual al del primero (`sl`) se sale del bucle; el chequeo final es `[0xc0010004] OR [0xc0010008]` (= `get_flag0()`/`get_flag1()`, mismas variables que lee `serial_entry`, confirmado por ser la única otra copia del literal `0xc0010004` en todo el ROM). Un paquete tipo 0 pone a 1 `[0xc0010004]`; uno tipo `0xFFFF` guarda el destino de salto y pone a 1 `[0xc0010008]`. Confirmado que solo dos saltos (`0xb90`, `0xb96`) llegan al punto de resincronización.
- **Corrección (propia, dentro de esta sesión, no de un informe publicado):** la hipótesis inicial de que el chequeo final exigía específicamente un paquete de salto era incorrecta; es un OR que acepta cualquier paquete tipo 0 o tipo `0xFFFF` visto en la secuencia, no necesariamente el que cierra el bucle.
- **Límite:** `main` llama a la misma función para la «clave» de R32/R33; no se ha trazado si el valor que usa puede venir de varios paquetes encadenados. No se emuló una secuencia real de varios paquetes (solo control de flujo por bytes).
- **Entregables:** `docs/capture/e26-r35-serial-receiver-multi-paquete.md`, `tests/test_e26_r35_serial_receiver_multipaquete.py`.

## Auditoría integral repo/GitHub (31-10-2026)

Local = `origin/main` (`a4c42e69`) al empezar. **CI «Pruebas» en rojo desde el 30-10 (26 ejecuciones):** Pillow ausente en el flujo y R20/R29
leyendo `bootrom.bin` y el manual de servicio (no versionados); arreglado (C9). **Fugas:** número de serie de la cámara en 16 `info*.txt`
redactado (SHA256SUMS recalculados; queda en el historial, R6); la clave `localtest.me.pem` es el certificado público de PMCA; sin tokens.
Volcados nuevos: se versionan JPEG reducidos, montajes y JSON de T042–T044/E25-22/E25-23; RAW, parciales, audio y la corrida previa de T043
quedan ignorados. **Coherencia:** README y CURRENT decían «funcional» tras el bloqueo del 3.25; STATE afirmaba «no se ha flasheado ninguna
cámara»; PENDIENTES tenía filas EFCS con IDs E26–E30 dentro del registro de cambios (renumeradas E25-EFCS…) y E25-19f duplicado; 61 enlaces
rotos corregidos (0 restantes salvo el ejemplo `old.md`). Tablero: planes P1–P24 (antes P1–P21) y recuento de informes de fase E.
README, CURRENT (≤150 líneas, tabla E26) y cabecera de STATE reescritos.

## Mantenimiento posterior a la auditoría (31-10-2026)

- **D13:** registro T054 (E25-22), T055 (E25-23) y T056 (instalación del 3.25, testimonio); informe [E25-23](../docs/capture/e25-23-interrupcion-captura-larga.md) redactado desde la evidencia (5 s OK, 15→20 s, 30 s→`65535` y `shooting` >90 s; causa sin demostrar).
- **C10:** los 15 fallos/errores de `test_s402_static_closure.py` en la suite completa eran una colisión de módulos `fw` en `sys.modules`; los 2 de `test_subsystem_index` venían del informe nuevo sin indexar.
- **C11:** dependencias de CI fijadas en `knowledge/requirements-ci.txt`; `pyelftools` retirado; `F821` corregido; `repo_audit.py` ignora cifras de copias históricas.
- **R3/R6 (historial):** con orden del usuario («hazlas todas»), `git filter-repo` quitó `libmprctrl.so`, el número de serie y el correo personal de los 727 commits; `main` publicado con `--force-with-lease` y árbol idéntico. SHA citados remapeados. Respaldo previo: `~/a6000-respaldo-historial-20261031.git`. Queda R7 (refs de PR y fork ajeno en GitHub).

## E26-R36 — causa del fallo del 3.25 frente al 3.23 (31-10-2026)

- **Pedido:** verificar de inicio a fin, dos veces, por qué falló el 3.25 si el 3.23 (solo Darwin) se instaló bien.
- **Paquetes:** `.dat` instalados descifrados (auditor E25-06) = FDAT plano; frente al 3.21, el 3.23 cambia `darwin_core.bin`/`darwin.sum` y el 3.25 además `dev/nflasha3`/`part_image.sum`. El `nflasha3` del 3.25 instalado = `bb9ce25a…`.
- **Binario (Capstone, releído):** `c01fdd8e` arma la lista de sectores desde `off>>9` y el residuo solo va al aviso y a `trabajo+8`; `c01fccd2` copia 0x18 B; ARM7 `0x1338`/`0x3f4` leen `+0`, `+4`, `+0xc` (16 registros) y `+0x10` (destino), nunca `+8`. `ldec.ko` (Linux) programa el LDEC igual. El residuo no llega al silicio.
- **Datos:** 16 imágenes Sony, 19 489 bloques, 311 824 registros: siempre residuo 0 y 16 × 4096 B (dos parsers coinciden). Cota de Sony `cmpr.c`: 4112 B por registro de 4 KiB. El 3.25: 359 residuos, bloques 0/48/57 = 1 registro de 73 732 B. Montaje (bloque 0) y primera entrada RAMCFG (bloque 240) caen en bloques defectuosos → −302.
- **Arreglo:** `tpzl.py` alinea a 512, recompone con 16 registros almacenados y `rebuild` rechaza particiones con `hardware_violations`; regresión primero (fallaba), 49 pruebas pasan; construcción completa en temporal cumple el formato de Sony con el mismo contenido FAT. La variante «alinear a 512» del README no bastaba.
- **Límite:** sin confirmación física (UART). El Darwin y el BIONZ nuevos del 3.25 nunca se han ejecutado. Entregables: `docs/capture/e26-r36-causa-fallo-325.md`, `analysis/e26-recovery/r36_ldec_records.py`, `r36-ldec-records.json`.

## E26-R37 — cierre estático de la recuperación (31-10-2026)

- **Pedido:** avanzar letra por letra (a→d) hasta cerrar todo lo estático tras R36.
- **(a)** `c01f1de6` trazado: solo `\updater\mode` en `nflasha2` fija el modo 3 (`c01f1e14 cbz` → `movs r0,#3`; R26 lo había leído al revés). El modo 3 carga el actualizador de `nflasha1` (dispositivo 1, intacto: `\boot\{loadaddr.txt,vmlinux.bin,initrd.img}` de 2013), que con solo `mode` entra en MODE_USER y espera firmware por USB (`UdtrMain.sh`, `execute_ufp.sh`). Teclas (`chk ank` → modo 5, ajuste) y Backup llevan a modos que leen `nflasha3`. `c01f51f4` solo envía el modo.
- **(b)** `scripts/e26_recovery/build_326.py`: 3.26 = 3.24 oficial con versión 3.26 (CRC de cabecera, suma y cifrado del primer bloque, DEND). Verificado con el auditor E25-06 (descifrado completo = FDAT) y con `fwtool`; mismos rangos de diferencia que 3.23→3.24.
- **(c)** Loader2 (`c003126c`) y Loader3 (`c01f4edc`) solo encienden la UART si `Backup[0x510015]==1`; 12/12 BK4 = 0. Una UART pasiva no confirma R36; solo el vídeo del LED.
- **(d)** Darwin 3.25: `0x20003716` está en la zona que `__scatterload_zeroinit` (`0x4494`) pone a 0; los vectores 70–73/76 que pisa la cueva son IRQ 54–57/60 y no hay ningún acceso a `NVIC_ISER1`.
- **Entregables:** `docs/capture/e26-r37-cierre-estatico-recuperacion.md`, `tests/test_e26_r37_cierre_estatico.py` (5), `analysis/e26-recovery/manifest-recuperacion-326.json`; pendiente nuevo `E26-FISICO-UPDATERMODE`.

## E26-R38 — guard del actualizador y entrada mínima `\updater\mode` (31-10-2026)

- **Pedido:** «investiga más a fondo» tras R37; se cierra la suposición abierta (comparación de versión) y se baja la escritura física al byte.
- **`sauu` (initrd cramfs de `nflasha1`):** `isVersionOK` (`0xd3d0`) compara con `updater/dat4` (`getVersion` `0xf6e4`, u16 LE); igual solo si falta `comp` (`IsValid` `0xf0b8`) o con `-m`; `-s` acepta todo (constructor `0xd180`).
- **Cuerpo (`libupdaterbody.so` 3.21):** `StartUpdate` borra `comp`; `CompleteUpdate` hace `setVersion(mayor<<8|menor)` (`0x152a8`), borra `mode1…6`, crea `comp` y borra `mode`. `uincomp` solo con `updater_sum` (ausente en los tar 3.2x).
- **Datos:** `nflasha2` del 20-10: `dat4 = 21 03`, `comp` oculto, par LFN+SFN `mode` borrado en las entradas 4–5 de `\updater`. Loader3 (`c01f44c6`/`c01f3f34`) solo compara el nombre corto en el primer clúster y no lee datos.
- **Entregables:** `docs/capture/e26-r38-guard-y-entrada-updater.md`, `scripts/e26_recovery/updater_mode_entry.py` (réplica de Loader3 + parche mínimo; `fsck.vfat -n` limpio), `tests/test_e26_r38_guard_updater.py` (5).
- **Límite:** nada leído de la NAND actual; la persistencia de `MODE` sin LFN es inferencia sobre `vfat`/busybox.

## E26-R39 — investigación estática a fondo (31-10-2026)

- **Pedido:** «hazlas todas, mientras se pueda avanzar en modo estático» (seis líneas tras R38).
- **Emulación:** `analysis/e26-recovery/r39_tpzl_emu.py` ejecuta en Unicorn Loader3 `c01fe4ec`/`c01fdd8e` y ARM7 `0x3f4` (sustituye solo `c020xxxx` ausentes y E/S); LDEC modelado. 3.25: 361/369 fallos (bloque 0 primero, 359 avisos de residuo); Sony y corregida: 0. Residuo en trabajo+8, nunca en registros LDEC.
- **NAND:** particiones = ventanas lineales de `nflasha` (473 MiB lógicos); `nand.ko` = MuMin (LTU/VBM/PBM, bloques malos, ECC/extra) → sector 132 no traducible; `0xE5→0x4D` necesita 0→1.
- **Actualizador:** `/sbin/init` + `insmod.sh` solo montan `nflasha2`; Darwin 3.25 = Sony + 22 B. Kernel `3.0.27_nl-rt106` = árbol GPL: búsqueda `nls_strnicmp`, `shortname=mixed` lista `MODE`. Guard: modelo/región/versión, sin batería.
- **Clave:** sin paquetes con loader; ningún cargador toca `0xc0001200`; el actualizador ya lee SRAM de arranque → `E26-R39-CLAVE-SRAM`.
- **Entregables:** `docs/capture/e26-r39-estatico-profundo.md`, `tests/test_e26_r39_estatico_profundo.py` (9), `r39-tpzl-emu.json`.

## E26-R40 — JTAG/SWD del BIONZ (31-10-2026)

- **Pedido:** analizar JTAG/SWD como alternativa a lo físico tras R39 (escribir `nflasha2` sin lector externo).
- **DAP CoreSight** (FUENTE, GPL de Sony): `0xf2710000`, 4 CTI, `dap.c` solo lo usa para una IRQ de la PMU; literal de desbloqueo `0xC5ACCE55` único en el kernel.
- **Sin bloqueo de software** (BINARIO): barrido de literales en BootROM/Loader2/Loader3/ARM7 sobre `0xf2710000`–`0xf271ffff`: 0 en los cuatro.
- **Silicio pensado para ICE:** `defconfig` `cxd90014_ice_initrd`/`ice_nfs` arrancan con `initrd`/cmdline fijos, sin `nflasha1`.
- **Ventana sin apagado:** `c01f3bf6: b #0xc01f3bc8` (bytes `e7e7`), bucle de LED tras −302 sin `wfi` ni apagado.
- **Límite real:** población de R4911/R4912 y eFuse de seguridad (junto al bloque JTAG en el manual) no están en ningún binario accesible; mismo límite que la clave de `nflasha0` (R33).
- **Entregables:** `docs/capture/e26-r40-jtag-swd-bionz.md`, `tests/test_e26_r40_jtag_swd.py` (8). Anota R5-SIDEA/R5-BIONZ; no los cierra (siguen físicos).

## E26-R41 — caminos estáticos restantes (31-10-2026)

- **Pedido:** «verifica los caminos estáticos faltantes por descubrir».
- **Consola de Loader3** (BINARIO): `c01f379a` lee la UART, con `\r` compara `beast`/`ldump`; `ldump` (`c01f3708`) solo hace `ldrb/ldrh/ldr`; `beast` (`c01f376e`) sale si `[0xc0060014]=0`. El bucle de LED llama a `c01f5008` (PL011: `IBRD 0x1a`, `FBRD 3`, `LCRH 0x70`, `CR 0x701`). Loader2 trae la misma consola.
- **Muda** (DATOS): `0x510015=0` → nivel UART 0 y `beast` desactivado en los 12 BK4.
- **Wait ICE:** `c01f0cc2: bl c01f48cc`, antes de `c01f0cca`; GPIO de Backup `0xf90449/0xf9044a` = 14/17; espera `[0xc0045804]≠0`.
- **Entregables:** `docs/capture/e26-r41-caminos-estaticos-restantes.md`, `tests/test_e26_r41_consola_loader3.py` (4); pendiente nuevo `E26-R41-ICE-GPIO`. Corrige R13, R37 §4 y R40 §6.
- **§7 (límites completados, «completa esos»):** Loader2 `c0030014: blx c003110c(0)` y `c0030020: blx c00308b8(0,7)` → `[0xc006000c]=0` (UART0); GPL `regs-clk.h`/`uart.S`/`clock.c`: 48 MHz, `IBRD 0x1a`/`FBRD 3` = 115 200; ningún cargador activa `OCTRL(2)+IEN` (sí `uart_init` con `UART_IO_INIT`, solo en `ice_initrd`). GPIO: `gpiopin_to_irq` puerto 0 = `GPIO_S` → bolas `GPIO_n` = puerto 0; el 14.17 no se puede determinar (falta la tabla de pines) → `E26-R41-ICE-GPIO` cerrado con límite. Pruebas: 6.

## E26-R42 — búsqueda externa en GitHub y esquema JTAG/eFuse (31-10-2026)

- **Pedido:** buscar en GitHub información nueva sobre ingeniería inversa/decompilación de la A6000 y verificar qué más da el código fuente (GPL) y el pinout en PDF.
- **Repos externos** (clonados en lectura fuera del repo): tres cubren la A6000 directamente (RafalB82, CliffVale, dhihacker) sin nada nuevo sobre arranque/recuperación; `cokeenet/zve10-qemu` (ZV-E10, CXD90045) y `Erlla/sony-a7m4-custom-firmware` (A7 IV) tienen vías de recuperación probadas en hardware real, pero no transferibles (SoC y arquitectura de arranque distintos: `fastboot`/eMMC vs NAND+Loader2/Loader3 del CXD90014).
- **Esquema (DATOS):** `pdftotext -layout` (el `.txt` versionado) pierde por completo la hoja JTAG/eFuse (pág. 26) y el neto `XRESET_CR` (pág. 24); `pdftotext` sin `-layout` + render de página (`pdftoppm`) sí los recupera. Bolas: TDI=G25/TCK=H25/TMS=F26 (atadas a VDD1), TDO=F25/RTCK=G26, NTRST=H26 (neto `XRESET_CR`); `FUSE_EN`=T12 atado a VDD2, `FUSE_CLK`=R12 sin red; SWCLK=W25/SWDIO=W26 sin atar. `XRESET_CR` = también la entrada `XRESET` del propio IC6000 (bola K6, hoja 1/7, vía `R6000` XX).
- **GPIO:** cobertura exhaustiva (54 páginas): solo existen `GPIO_0..16`/`GPIO_S_0..16` (puerto 0) y `GPIO_SB_0..6` (puerto 1); ningún nombre para el puerto 14. Confirma el límite de `E26-R41-ICE-GPIO`.
- **Entregables:** `docs/capture/e26-r42-busqueda-externa-y-esquema-jtag.md`, `tests/test_e26_r42_esquema_jtag_efuse.py` (3); pendiente nuevo `E26-R42-EXTERNO` (cerrado). No cambia ninguna vía de recuperación.

## E26-R43 — cierre estático de CL1000/BOOT_MAIN (bit0): sin acceso externo (31-10-2026)

Petición del usuario: verificar si la clave de `nflasha0` es realmente imprescindible o hay alternativa, y cerrar de
forma estática si forzar `CL1000` a masa es viable, revisando también el código GPL de Sony.

- **GPL (FUENTE SONY):** `regs-misc.h` de `mach-cxd90014` y `mach-cxd4132` solo nombra el bit 1 (`BOOT_SERIAL_IN`/`BM1`);
  el bit 0 (`BOOT_MAIN`) no tiene definición ni polaridad en ningún archivo del árbol GPL. No hay alternativa en
  software: sigue siendo un strap de hardware puro.
- **Esquema (ESQUEMA, vectorial — `pdftotext -bbox` + `pdftocairo -svg`, sin rasterizar ni OCR):** trazado exhaustivo de
  la hoja CLK BOOT (página 24): `CL1000`/`BOOT_MAIN` (P7) termina en el punto de prueba sin ningún salto hacia la
  columna de exportación global — **no hay atajo por el conector Multi externo (CN4001)**. Sigue siendo intervención
  física interna; polaridad no determinable sin hardware (igual que R31 §3/R32 §5, sin cambios).
- **Efecto lateral (corrección):** al trazar la misma hoja se confirmó que `BOOT_SERIAL_IN` (H21, bit1) sí exporta, y
  llega al **pin 10** de CN4001 (etiqueta de conector `AD_JACK_IN`), no al pin 9 como daban por hecho R11/R19/R20/R29
  (agrupaban por fila de texto, que en esta hoja no coincide en altura con el trazo real — mismo problema que motivó
  el pixel-trace propio de R29 para CN4906, nunca aplicado a CN4001 hasta ahora). El pin 9 solo lleva
  `DEBUG_UART0_RXD`, señal de consola independiente.
- **Entregables:** `docs/capture/e26-r43-cl1000-sin-acceso-externo.md`, `analysis/e26-recovery/r43_cl1000_cn4001_trace.py`,
  `tests/test_e26_r43_cl1000_cn4001.py` (3, en verde). Pendientes: `E26-R43-CL1000-ACCESO` (cerrado), nuevo
  `E26-R43-PIN10-CONTINUIDAD` (físico). No cambia el objetivo de recuperación ni abre vía nueva: confirma que lo que
  falta sigue siendo físico.

## E26-R44 — ¿otra forma de obtener la clave de nflasha0, o forzarla? (31-10-2026)

Petición del usuario, continuando R43: ¿hay alternativa a la clave, o se puede forzar?

- **Desensamblado directo** (Capstone, no pseudocódigo) de la comprobación de clave en `main`: una sola palabra de 32
  bits (la segunda palabra guardada es solo `~crc32`, sin secreto adicional), comparada en una única instrucción
  (`ldrd`+`cmp`) — sin bucle byte a byte, sin canal lateral de tiempos explotable. `error_blink` (`0xffff0d62`) es un
  **bucle infinito que nunca retorna**: cada intento fallido exige apagar y encender la cámara. **Fuerza bruta
  descartada**: 2³² intentos por este interfaz, inviable incluso automatizada (años, no horas).
- **Ninguna alternativa software** para leer/derivar la clave: Loader2 (247/247) y Loader3 (674/674), ya mapeados al
  100 %, no tocan `nflasha0`.
- **Mejor vía que la clave, ya documentada pero no resaltada así antes** (R20/R23, `E26-R20-GPIO4`): si `GPIO4.22`
  lee `!=0` al arrancar, `main` salta a `serial_entry()` sin pasar nunca por la comprobación — no exige conocer ningún
  secreto. El usuario pidió reabrir la búsqueda del pin físico con el método vectorial de R43: único bloque "GPIO SYS"
  en las 54 páginas del esquema, sin dato que confirme que sea el canal 4 del mapa de registros (el GPL de Sony da el
  cálculo de dirección pero no el mapeo canal→bola). Candidato débil por descarte: `GPIO_SB_5` (bola N8) es la única
  del grupo sin red de cámara nombrada. **No cierra.**
- **Entregables:** `docs/capture/e26-r44-gpio4-bit22-busqueda-pin.md`, `tests/test_e26_r44_gpio4_clave.py` (4, verde).
  PENDIENTES: cierra `E26-R44-CLAVE-FUERZA-BRUTA` y `E26-R44-GPIO4-BIT22-BYPASS` (bypass ya conocido, impacto
  precisado); abre `E26-R44-GPIO4-PIN` (sin cierre) y `E26-R44-AVCAM-GPIO4` (binario, rastrear llamadores con banco 4
  de la lectura genérica de GPIO en `av-cam.bin`, no iniciado — requiere sesión REA ~8 min).

## E26-R44 §6 — sesión REA de av-cam.bin: pin de GPIO4.22, bloqueado por el límite de E1 (01-11-2026)

Petición del usuario: iniciar la sesión REA de `av-cam.bin` para `E26-R44-AVCAM-GPIO4`.

- Primitiva de lectura de GPIO por banco (`FUN_4398f990`, `base=0xf2910010+banco*0x100`): **un solo llamador** en todo
  el binario, `FUN_43b5e2bc`, que acota el banco a 0–17 (banco 4 permitido, da exactamente `0xf2910410`) y tiene
  **26 llamadores**. Ninguno pasa banco/bit como constante: todos resuelven contra la base de datos de propiedades de
  Sony mediante IDs opacos (`0x00f902a9`, fuera del rango de direcciones del binario) — **el mismo mecanismo sin
  resolver de `E1`/`ModelScalarPb`**.
- 3/26 llamadores identificados por nombre vía tabla de registro de propiedades (`eosw_port`/`[EO_SW]`,
  `rvport`/`[PanelReverse]`, `esport`/`[EyeSens]`): los tres son funciones normales de cámara, ninguno de arranque.
- **No se identificó el pin de `GPIO4.22`.** Bloqueado por el mismo límite que `E1`: los valores reales de banco/bit
  no están en `av-cam.bin` como datos estáticos — dependen de una base de datos de propiedades no localizada.
- Sesión REA cerrada limpiamente; `exp2-session-log.jsonl` restaurado con `git checkout`.
- **Entregables:** `docs/capture/e26-r44-gpio4-bit22-busqueda-pin.md` §6. PENDIENTES: `E26-R44-AVCAM-GPIO4` pasa de
  ABIERTO a **BLOQUEADO** (mismo origen que `E1`); cruzado en la fila de `E1`.

## R8 — publicación de los binarios 3.23/3.24 como GitHub Release (01-11-2026)

Petición expresa del usuario: subir los dos firmware custom ya construidos en E25-05 (el que apaga las bobinas y el
obturador mecánico completo, y el de recuperación) como release de GitHub, con sección de copyright en el README.

- Verificado que `analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (`4c21353d…`) es exactamente el
  hash comprobado antes de flashear en T040, y que `recuperacion-324/firmware_packed.dat` (`e1345aff…`) es su
  recuperación verificada offline (E25-05, 69/69 checks) nunca instalada en cámara real.
- Publicados en el [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
  (no en el árbol de git, que sigue sin firmware de Sony) con `SHA256SUMS.txt` y notas: estado real de cada paquete,
  pasos de instalación/verificación y aviso de copyright (investigación/interoperabilidad, sin redistribuir fuente
  de Sony, retirada a petición del titular).
- README: enlace al release en «Instalación del 3.23», nueva sección «Recrear lo mostrado en el hilo de r/a6000»
  (pasos para reproducir la publicación de Reddit: 3.23 + `camera_silent.py`) y «Copyright de los binarios
  publicados».
- **Entregables:** release de GitHub, README actualizado, [R8 en PENDIENTES](../docs/PENDIENTES.md) CERRADO.

## Wiki de réplica, LICENSE y README reducido (01-11-2026)

- Petición del usuario: quitar el copyright del release (queda solo en el README), reducir el README y crear una wiki para replicar todo de principio a fin.
- `wiki/` (11 páginas) y `scripts/replicar/generar_nucleos.py`: reconstruir 3.23/3.24 desde el firmware oficial reproduce exactamente los SHA-256 del release (`4c21353d…`, `e1345aff…`; 69/69 comprobaciones).
- `LICENSE` MIT solo para código y documentación propios.
- Publicada en la wiki de GitHub («Wiki CFW Sony a6000»); auditoría sin incoherencias.

## E26-R45 — firmware 3.25c experimental (01-11-2026)

- Petición del usuario: construir el 3.25 corregido, corregir todo lo que bloqueó la cámara y publicarlo como experimental y teórico con pruebas.
- Corregido además un riesgo que el constructor de R36 introducía: bloques recompuestos de 129 sectores (Sony ≤ 126 en `nflasha3`). `tpzl._splice` conserva los registros de Sony de las páginas no tocadas (regresión primero).
- `scripts/e25_27/verify_325c.py` → `analysis/e25-27/verify-325c.json`: 30/30 sobre el `.dat` final con controles (Sony 3.21 y el 3.25 que bloqueó); emulación Loader3+ARM7: 0/369 fallos frente a 361.
- Release `fw-3.25c-experimental` (*pre-release*): 3.25c, 3.26 de vuelta atrás, SHA256SUMS y la evidencia. Informe [R45](../docs/capture/e26-r45-firmware-325c-experimental.md).
- 01-11-2026 (seguimiento, petición del usuario): README, wiki, tablero y portada actualizados para presentar el 3.25c como alternativa experimental al 3.25 original (que sigue sin publicarse).
- 01-11-2026: `README.en.md` (versión en inglés) enlazado con un botón al inicio del README; copyright cubre también el release 3.25c.
- 01-11-2026: wiki, CONTRIBUTING y notas de releases en inglés; wiki española sincronizada con los mismos datos. Los informes siguen en español.
- 03-11-2026: **CAM-01 cerrado con límite** — familia CAMERA con 0 menciones abiertas por medidas (`analysis/camera_closure/`, `tests/test_camera_closure.py`): callbacks `0x437b8774`/`0x437b7778`/`0x436ea2d0`/`0x43705d64` sí registrados por puntero PC-relativo; seis funciones sin referencia estática; ficheros fuente casi nunca citados. Avance real 24,50 %.
- 03-11-2026: **CAM-02 cerrado con límite** — familia CAM (7 etiquetas) con 0 menciones abiertas por medidas; corrige S600/S601 (sí citan ficheros fuente). `analysis/camera_closure/` ampliado.
- 03-11-2026: `[CAMCORE]` (S107) cerrada por medidas, como CAM-02.
- 03-11-2026: familia IMAGING (S611, S631) cerrada por medidas; el barrido bl de camera_closure pasa a patrón de halfwords (el lineal daba 0 llamadores); corrige S122 (0x438792dc sí tiene bl).
- 03-11-2026: S632 documenta y cierra la familia MODE (`[MODE_SNR_BUS_THROUGH]` hito; `[MODE_CAP*]`, `[MODEFLG]` en el mismo informe). Cobertura 208/372.
- 03-11-2026: familia MODE 6/6 (los cinco [MODE_CAP*] pasan de no-modulo a sub-etiqueta de [IMAGING_CAP]); cobertura 213/372.
- 03-11-2026: S633 cierra la familia STK 6/6 (cinco [STK_*] a sub-etiqueta de [STK]; S501 sin NO VERIFICADO). Cobertura 218/372.
- 03-11-2026: familia MOUNT (S133, S608, S613) sin menciones abiertas, por medidas.
- 03-11-2026: familia OTROS cerrada (S634 + cierres de 49 informes); censo 364/372, 0 pendientes.
- 03-11-2026: S635 documenta [OSD] (última etiqueta cubierta sin informe propio).
- 03-11-2026: S636 documenta [D0]-[D7] como sub-etiquetas de [CAM_UTIL_ADJ]; censo 372/372.
- 03-11-2026: auditoría de pendientes tras S636: review_reports regenerado (762 informes; 1800 abiertas / 2737 verificadas), sin rutas nuevas; ver PENDIENTES. Sesión previa cortada por un `grep -rn` recursivo sobre `analysis/` (sin resultado registrado).
- 03-11-2026: revisión de las 154 líneas sin marca: 23 marcadas NO_VERIFICADO (REV-01), 131 apartadas; añadibles 0.
- 03-11-2026: REV-01 parcial: 12/23 cerradas con medidas (analysis/rev01/); 11 pendientes de sesión REA.
- 03-11-2026: REV-01 14/23 (sesión REA: adjust_cmd_recon 85, clk_ctrl 374); quedan 9.
- 03-11-2026: REV-01 cerrado con límite (23/23); corrige apl (A7S no idéntico) y label_map (solo IDT_OPD renombrado). analysis/rev01/.
- 03-11-2026: R46 — procedimiento físico planeado para SWD al BIONZ sin osciloscopio (fases F1–F9); R4911/R4912/CN4906 confirmados sin montar por el usuario.
- 03-11-2026: R47 — primer contacto SWD real (RP2040 Zero + debugprobe-zero): DPIDR/APs leídos, RAM volcada (hashes fuera del repo), Loader3 en RAM idéntico a Sony; `halt`+registros mide el −302 en LDR2/LNG/SHT; cadena de puntos de parada sobre el arranque real confirma que P2 (`CFG_E:Load file`) falla al cargar `\sabin\idt_cam.bin` de `nflasha3` (§15), confirmando R36 en la cámara.
- 03-11-2026: R48 — plan de entrada al actualizador por SWD sin escribir NAND (forzar `r0=0` en `chk updater`, c01f15c0); Loader3 no puede escribir bloques (`muminblk_request` ignora las escrituras). P0 preparado (pmca, paquete 3.26 verificado). Primer intento de P1 no vio el patrón de doble arranque esperado y se detuvo solo; muestreo posterior corrige la lectura: el doble arranque es meter-batería-luego-interruptor, no cada encendido. El usuario entró al actualizador por su cuenta; primera instalación del 3.26 cortada al 45 % (`0x1063`, NG de Darwin).
- 03-11-2026: R49 — cierre: `r48_updater_swd.cfg` corregido para el arranque único real; P1 ejecutado con éxito (BootMode 3 elegido, entrada al actualizador en 696 ms); diagnóstico por SWD tras el fallo (registros banked `sp_svc`/`lr_svc`, no los alias genéricos) confirma que el kernel seguía sano y nada se había confirmado (versión seguía en 3.25); reintento de instalación completo (`CMD_COMPLETE`). **Cámara recuperada: arranca normal, firmware 3.26 confirmado.**
- 07-11-2026: R65 — rama EFCS de Darwin: `t`=0 en BSS (E26-R64-CORTINA cerrado), µs, `S+0x48 = T − u16[G+0x42]` con EFCS activado (E26-R62-DARWIN-IP cerrado con límite); origen de G no localizado (E26-R65-G42); prueba `0x30102+0x8a` propuesta (E26-R65-8A). Test `tests/test_e26_r65_darwin_efcs_tiempo.py`.
- 07-11-2026: R66 — B/G de Darwin son las propiedades NVRAM `0x1850001`/`0x1850000` (tabla BIONZ `0x43fe8c38`); corrige la asignación a BK4 `0x30102` (R58 §13, R61–R65); `G+0x42 = 3407` µs sin cambios desde el 20-10; la pérdida EFCS no viene de Darwin; propuesta `0x1850001+0x86` (E26-R66-B86). Test `tests/test_e26_r66_bloques_darwin_nvram.py`.
- 07-11-2026: R67 — eventos A/B de Darwin con EFCS = P4C ← 0 (`CA_1ST_CURTAIN_START`) y P4E ← 1 (`2ND_CURTAIN_MG`); la pérdida queda en el retardo flanco→reinicio del BIONZ/sensor o en la cortina; propuesta de lectura pasiva E26-R67-GPIO9; E24-05e parcial. Test `tests/test_e26_r67_eventos_darwin.py`.
- 07-11-2026: triaje de PENDIENTES — 67 filas cerradas (superadas por R49 o por R54–R56, históricas o sin fuente; E11 con la premisa corregida por R67); E25-07 cerrado con procedimiento `sha256sum -c` y `recuperacion-323` obsoleto; quedan 15 abiertas (físicas, autorización, repositorio o carril GUI).
- 07-11-2026: R68 — auditoría de R65–R67: corregidos R65 §3 (la rama `< −150` no explica el negro), R65 §1–2 (`0x30102`), la saturación de E26-R66-B86 (solo T < 3407 − B86) y la tabla global de CURRENT (3.37 oficial, hito 3.30); cuatro afirmaciones pasan a INFERENCIA. Test de saturación en `tests/test_e26_r67_eventos_darwin.py`.
- 07-11-2026: R69 — revisión de R56–R64 con notas de corrección (R58 §3/§13, R61, R62 §3–4, R63 §6, R64); inferencias de R65–R68 cerradas (P4E ← 1 suelta la trasera; A–B independiente de `ip`; `t` = 0 y flujo backup como INFERENCIA fuerte); E26-R66-B86 descartado, E26-R67-GPIO9 fusionado en E26-R66-RESET (procedimiento listo).
- 07-11-2026: R70 — máquinas de secuencias de Darwin; P4C ← 1 en la preparación y en el rearme (A siempre produce flanco); `ip` escribe P4A/P42/P05/P35/P56; lectores de `G+0x42` vía `0x182d8` son plazos de decenas de ms; test `test_e26_r70_secuencias_darwin.py`.
- 07-11-2026: R71 — medida en cámara (solo lectura) de los GPIO del BIONZ; E26-R66-RESET pasa a PARCIAL.
- 07-11-2026: R72 — `0x30087` → `record+0x156` en el planificador EFCS; config. de mecanismo de Darwin fuera de `darwin_core`.
- 07-11-2026: R73 — REA con límite de 1 h: destino de `0x30087` (StillInfo) y ganchos de depuración; E26-R72-30087 cerrado.
- 07-11-2026: R80 — auditoría del parche R76: scripts reparados, cave con límites y validación, gradiente no corregible desde Darwin.
- 07-11-2026: R74 — conclusión final del negro con EFCS: causa física; test `test_e26_r74_efcs_bionz.py`.
- 07-11-2026: R75 — verificación de R74 y de la secuencia A/B de Darwin; la pérdida sigue a `B − t0`, no al flanco A; test `test_e26_r75_verificacion_r74_darwin.py`.
- 07-11-2026: R77 — preparación, P4D y orden temporal (estático): P4D ← 1 solo tras el armado con EFCS, retardos fijos sin T; test `test_e26_r77_preparacion.py`.
- 07-11-2026: R78 — límites de R77 cerrados (semántica del intérprete, acciones 09/0a/13/14 sobre la máquina S, alcance de `0x1fee2`); test `test_e26_r78_limites_r77.py`.
- 07-11-2026: R79 — restos de R78 cerrados (handlers de tabla `0x295c4`/`0x25b70`, acciones 04–06/`0x2f` de S, reejecución de S); test `test_e26_r79_restos_r78.py`.
- 07-11-2026: R81 — auditoría del parche EFCS: el cave `0x13d5a` está en la función viva `0x13d58`; parche bloqueado; test `test_e26_r81_parche_efcs.py`.
- 07-11-2026: R82 — parche EFCS v3: reescritura en sitio de `0x18d6e..0x18e0f` con la tabla integrada (vía A, verificada con 3 métodos), volcados NVRAM listos (D), evidencia de tamaño del core (C), sin hueco ≥ 40 B (B); test `test_e26_r82_parche_efcs_v3.py`.
- 07-11-2026: R83 — informe final de la investigación EFCS (R65–R82).
- 07-11-2026: G2/G4 parcial — formato `string_*.uxc` verificado + editor de ida y vuelta (`scripts/gui/uxc_strings.py`, `test_gui_uxc_strings.py`); ítem de menú `CmnViewMenuItemStruct` verificado con la tabla Creative Style de `viewUnified2.so` (REA); colores `color_cmn` como RGBA de 8 B. Informe: `docs/gui/g04-menus-y-recursos.md`.
- 07-11-2026: G8/G2/G4 (offline) — veredicto de integridad de `/usr` (solo CRC-32, FDAT sin firma), cambio de texto en copia ext2 verificado con debugfs+e2fsck, `scripts/gui/menu_tables.py` (93 carreras de tablas). Propuesta: prueba B (bind-mount reversible) con autorización. `docs/gui/g04-menus-y-recursos.md` §6–9.
- 07-11-2026: G9 — ajuste Silent Shooting/Shutter Type del A6300: 4 capas (CautionConfig nodos, viewUnified elementos, libObj camera-user, av-cam), `scripts/gui/setting_nodes.py`; corrige E007 (nodo SilentShutter de la A6000 = SteadyShot). `docs/gui/g09-silent-a6300-menu.md`.
- 07-11-2026: G9 ampliado — capa de mensajes PARAMID_* (A6000 ya tiene Silent y FrontEShutter; A6300 añade SHUTTER_TYPE), builds no intercambiables (wrappers fundidos en A6300), barrido de ProcessId descartado por ruido.
- 07-11-2026: G9 — las páginas de menú son arrays de punteros a nodos raíz (relocaciones ABS32 en viewUnified2); A6300 inserta SilentShutter antes de EFCS en las mismas 5 páginas que la A6000 usa para EFCS. Plan: sustituir/alargar entradas + reutilizar el nodo stub.
- 07-11-2026: G9 §5c — consumidor de las páginas de menú: _INIT_70 de viewUnified2 (A6000) construye 5 páginas con EFCS (array de hijos + cuenta constante); ruta de menor coste = sustituir símbolo de relocación; insertar exige relocación nueva + cuenta.
- 07-11-2026: G9 §5d — decisión de insertar (no sustituir); viabilidad: sin hueco en .rel.dyn, sin GNU_RELRO, sin cuevas de código; mecanismo = PT_LOAD añadido + copia de .rel.dyn + literal/cuenta por página en _INIT_70 (páginas 1–3 localizadas).
- 07-11-2026: G9 §5e — prototipo add_menu_entry.py (segmento PT_LOAD + relocaciones + literal/cuenta) verificado con qemu-user+gdb: 5 páginas con cuenta+1 y la entrada nueva antes del EFCS; corrige array de la página 3. Herramientas: add_menu_entry.py, qemu_sysroot.py.
- 07-11-2026: G9 §7 — paquete de prueba Silent Shooting (A6300) que reutiliza el ajuste EFCS 0x46 (semántica del CFW): build_silent_menu_test.py, camera_ui_test.py (probe/deploy/revert, dry-run por defecto); carga verificada con qemu-user. Sin cámara.
- 07-11-2026: G9 §7b — prueba en cámara: probe OK (md5 3.21 coinciden), bind OK, pero im.elf ignora SIGTERM, sin supervisor; kill -9 + relanzado manual => la cámara se reinicia sola y se pierden los montajes. Vía temporal descartada; queda flasheo de nflasha15.
- 07-11-2026: G9 §8 — reconstrucción de nflasha15 (TPZL de ext2): build_nflasha15.py + build_package_nflasha15.py; 135/2373 bloques recompuestos, fsck limpio, decodificador independiente coincide; paquetes 3.39 (menú) y 3.40 (vuelta atrás) construidos offline.
- 07-11-2026: G9 §8b — paquete 3.39 rehecho con bloque TPZL 0 = Sony (solo contadores ext2) y Darwin v3 (R82); auditoría independiente 23/23 OK; vuelta atrás 3.40 = 3.38 con /usr de Sony.
- 08-11-2026: G9 §8c — fallo del 3.39 diagnosticado por SWD (assert de ResourceManager por ids de texto sin ranura en el índice del A6000); 3.40 corregido y auditado 22/22; vuelta atrás 3.41.
- 08-11-2026: G9 §8d — 3.40 (menú corregido) deja la cámara en error LED −307 de Loader3; recuperada con 3.41 (paquete base + /usr Sony). Causa sin determinar; la UI sigue sin probarse.
- 08-11-2026: R82 en cámara — 3.43 con Darwin v3 arranca; tabla NVRAM de prueba (c=2000 µs) elimina el negro con EFCS: la NVRAM llega a Darwin. 3.42 (menú sin Darwin) no arranca → culpable `nflasha15`. Nuevo `scripts/senser_efcs_table_write.py`.
- 08-11-2026: cierre de sesión — informes G10 (menú Silent) y R84 (Darwin v3 en cámara); cámara en 3.43 con tabla NVRAM de prueba.
- 08-11-2026: G11 — auditoría del −307 (Loader3 no lee datos de `nflasha15`; −307 = init UDIF/MuMin), paquetes 3.39–3.42 verificados; corregido el modo de los ficheros en `build_nflasha15.py`.
- 08-11-2026: G11 §6 — verificación estática de `viewUnified2.so`/`CautionConfig.so`/`.uxc`; sin defecto estructural; riesgos R1 (nodo `0x26` reutilizado) y R3 (páginas de 7).
- 08-11-2026: G11 §7 — paquete 3.44a (variante a: sin `viewUnified2.so`) construido y auditado 23/23; auditor con comprobación de modo/uid/gid.
- 08-11-2026: G11 §8 — 3.44a no arranca (Loader2 −201; log en la eSRAM: se queda en `Load LDR3`); recuperada con R48 + 3.45; la cámara queda en 3.45 (= 3.43).
- 08-11-2026: G11 §9 — paquetes de aislamiento 3.46 (solo `.uxc`), 3.47 (solo `CautionConfig.so`) y 3.48 (control con contenido de Sony) construidos y auditados 23/23; sin instalar.
- 08-11-2026: G11 §10 — 3.48 (control) y 3.47 (solo `CautionConfig.so`) instalados: ambos fallan; la causa probable es escribir un `nflasha15` recompuesto. Cámara pendiente de recuperar con el 3.49.
- 08-11-2026: G11 §11 — recuperada con 3.51. Causa común: el arranque normal (BootMode 11) reanuda el WBI de Sony (`nflasha5`), que contiene el TOC y la caché del `/usr` de Sony; el actualizador lo reescribe tras `ud_wbi_drop`. Paquete 3.52 (control sin `nflasha5`) construido, 25/25.
- 08-11-2026: G11 §12 — 3.52 arranca en frío (`BootMode: 1`): causa confirmada. 3.53 (menú completo sin `nflasha5`) construido, 25/25.
- 08-11-2026: G11 §13 — 3.53 en cámara: arranca y aparece «Silent Shooting», sin selector. 3.54: listas del nodo con `0xb`/`0xc` del EFCS en segmento nuevo (qemu OK), 25/25.
- 09-11-2026: G22-B — auditoría del arnés de la UI: `setup.sh` reproducible, `im.sh`+`SHIMENV`, shim corregido (buzones con *timeout*, colas dinámicas, señal segura), `tests/test_gui_harness.py`, informe [G22](../docs/gui/g22-arnes-ui-qemu.md) con el plan F1–F5; verificado en QEMU el mismo punto que el avance 17.
- 09-11-2026: G22-B avance 18 — callbacks de cola de `libosal_uipc` (idx 3/8/9/13) modelados; `FULLLOG`/`ACKQ`; bloqueo ahora en el protocolo de pines (`DataflowInfraPin`, tras acusar `0x61003c`). Ver [G22 §5.1](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 19 — emuladas `InternalCmd` alloc (`0x61003c`), backup `nread` (op 30), espera de GPU `dmpgles2` y dmm 1/9; `hal_create` pasa; siguiente: formato real de dmm (MemorySpace) y SIGSEGV no determinista. [G22 §5.2](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 20 — `grm_ma.ko` identificado como el servicio 0x14c0424 y emulado; GPU (registros + IRQ); el arnés arranca estable hasta el Window System (640×480). Siguiente: pantalla (F3) y entrada (F4). [G22 §5.3](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 21 — cargador completo (66 etapas) y reposo; MEMSCAN: sin píxeles (render por GPU DMP); plan F3 revisado. [G22 §5.4](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 22 — `bootin.elf` lanza 8 procesos `im.elf` (letras → fases del IMDB); `appFw.so` (hilo de la UI) nunca se ejecuta, ni con `bootall`; nuevos `INJECT`, `IMSPLIT`, `IMARGS`. F3–F5 no realizadas. [G22 §5.5](../docs/gui/g22-arnes-ui-qemu.md).
- 09-11-2026: G22-B avance 23 — la UI arranca (`appFw.so`+`viewUnified2.so`): faltaba señalar el semáforo `0x83037a` (`SEMSIG`). Bitmap de pantalla a cero → F3 depende de la GPU de DMP. [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 23b — SEMSIG×4, la UI carga recursos y abre /dev/ldec; pantalla aún a cero (GPU). [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 23c — AREADUMP/DUMPTHR; lista de comandos de la GPU solo con sincronización; Appframework bloqueado en mutex GL. [G22 §5.6](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 24 — GPU mínima (GPUEMU) y protocolo vdf; la UI no se bloquea; pantalla aún a cero (falta renderizar listas DMP). [G22 §5.7](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 24b — KEYQ/INJECT por buzón para teclas; w0=2 aceptado, sin vista. [G22 §5.7](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 25 — bucle de `Appframework`, ruta `openView` → evento `0x11012001`, tabla de vistas vacía, `InputService::activate` desde las vistas; `OPENVIEW`/`HILO`/`DUMPTHR` lista. Sin vista ni píxeles. [G22 §5.8](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 26 — la UI abre ViewScalarboot; GRM 2D sin uso; F3 sigue bloqueada por la GPU de DMP. [G22 §5.9](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 27 — ViewRoot abierta con OPENVIEW=view/ROOT; teclas llegan a InputService; bitmap a cero. [G22 §5.10](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 28 — corrección: la UI no envía dibujo a la GPU (4 trabajos); ViewRootPowerSw Non-Display por la fecha de model/ROOT. [G22 §5.11](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 29 — servicio de fecha modelado sin efecto; ViewRootPowerSw sigue Non-Display. [G22 §5.12](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 30 — PATCHFN; Non-Display no es error; falta evento de tecla de encendido. [G22 §5.13](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 31 — w1 de INJECT = status del interruptor de encendido; ViewRootPowerSw llega a isBootEECapNone. [G22 §5.14](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 32 — status del encendido = w2; BOOTINFO; sin avance en dibujo. [G22 §5.15](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 33 — comparación con el log real de la cámara. [G22 §5.16](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 34 — la UI no recibe eventos de modelo (falta av-cam); F3/F4/F5 abiertas. [G22 §5.17](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35 — paridad con el registro real hasta `getNumber : 1`; nuevas herramientas del shim (`PATCHFN` halfwords, `TRACEDEREF`, `GMILOG`, `KEYONACTIVE`); F3/F4/F5 abiertas. [G22 §5.18](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35i — `libStm.so` desensamblado: ScalarSTM es servidor petición/respuesta (ops 1..0xb), no espera notificaciones de av-cam; hipótesis descartada. [G22 §5.18i](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35j — la cola `0x102021f` (CameraBackground) recibe órdenes de la propia app (emisor `libObj+0x19d664`), no de av-cam; 2 de 6 colas descartadas. [G22 §5.18j](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35k — `CameraBackground_act` (→`0x19d6e0`/`0x19d664`) lo lanza `im.elf` en `act_all` (tabla `libIMDB`), disparado por `upm.ko`; el arnés no alcanza `act_all`. [G22 §5.18k](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35l — `CMD_ON` inyectado a `0x94016a` no se consume: `main` de `im.elf` espera un `join` (`[0x154c4]`, INFRA1; objetivo sin identificar) antes de su bucle de recepción; shim `CBLOG`/`SYNCMBX`. [G22 §5.18l](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35m — `act_all`/`CameraBackground_act` reproducidos en el arnés (`NOJOIN`, `SYNCMBX`, `THRLOG`); falta la respuesta de `upm.ko` (`ON_CMP`). [G22 §5.18m](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35n — `ON_CMP`→`APP_ON` a `0x920168` (registrada por `ObjHandover_Create`, no llamado en el arnés); shim `UPMON`. [G22 §5.18n](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35o — el arnés no ejecuta el arranque de módulos/objetos de `libObj` (`Mi/Ma/Tc/Ts/Md/Ms`, `Os/Or`) que en la cámara precede/sigue a `APP_ON`. [G22 §5.18o](../docs/gui/g22-arnes-ui-qemu.md).
- 10-11-2026: G22-B avance 35p — `Mi/Ma/Ts/Md/Ms/Mr` = ciclo de vida de modelos de `ModelManager` (logger `libObj+0x7efef0`); falta el evento de arranque en bloque. [G22 §5.18p](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 38 — acuse *dataflow* de ADF para `ObjMic` (`libBizFw2`: `AdfCh`, `URendezvous`, `osal_msg_size`); `Mi 0ED` cierra y el arnés recorre `Tc`/`Ts`/`Mr` completos. [G22 §5.18v](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 39 — `jackStatus` emulado: estado inicial del jack USB en la lista de `InfraInput` (`KEYINIT=7000001:1:177`); `execCheck retVal 0` sin parches. [G22 §5.18w](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 40 — la UI presenta fotogramas; listas de GPU tipo PICA de DMP con mapa distinto del de la 3DS; F3 sigue en la GPU. [G22 §5.18x](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: G22-B avance 41 — menú abierto (`view/GLOBAL_MENU`) y trabajos de GPU decodificados (tipos 2/3/6/7, lista de dibujo de un cuadrilátero texturizado); `TRACEREP`, `gpu_jobs.py`. [G22 §5.18y](../docs/gui/g22-arnes-ui-qemu.md).
- 11-11-2026: CFW 3.69–3.73 instalados; parche PP en la imagen (G31); menú PP plano y repintado instantáneo. Actualizados PENDIENTES (G15–G20 revisados, G24-A, G30-C), G29 §6 y CURRENT. [PENDIENTES](../docs/PENDIENTES.md).
- 11-11-2026: G32 auditoría del menú Picture Profile del CFW 3.73: cadena menú→libObj→0x4066→cfg sana (31 casos), pero 15 ajustes (Black Level, Black Gamma, Knee, Detail) sin consumidor en el núcleo, Gamma Movie/Still sin efecto por construcción y S-Log3 con gamma 0x17 sin casos por gamma. [G32](../docs/gui/g32-auditoria-picture-profile-3-73.md), PENDIENTES G32-A…D.
- 11-11-2026: G33 Black Level, Black Gamma, Knee, Detail Level/V-H/Limit/Crispening y Gamma Still aplicados en el núcleo (gancho de curva + ganchos APC, `pp_tone.c`), CFW 3.74 construido offline, sin instalar. [G33](../docs/gui/g33-pp-black-knee-detail-still.md), PENDIENTES G32-A/B, G33-A/B.
- 11-11-2026: E26-R85 auditoría con las fotos DSC03749–03779 (Silent / EFCS on / EFCS off): EFCS on aún con la tabla de prueba (exceso +0,8…+1,0 ms, pérdida real 1,0–1,16 ms) → tabla calibrada R85 y `--tabla` en el escritor NVRAM; Silent del CFW sin la calibración R56 (+3,5…+5,5 EV); `camera_silent.py` pasa a 16,73 µs/97 filas. [R85](../docs/capture/e26-r85-calibracion-fotos-3749-3779.md)
- 11-11-2026: R85 §7, segunda tanda DSC03786–03806: tabla EFCS final R85b; a 1/60–1/125 `c` no actúa; EFCS uniforme solo hasta 1/500; electrónico sigue sin calibrar sin el parche RAM.
- 11-11-2026: E26-R86 CFW 3.76 (3.75 + Silent calibrado en la imagen BIONZ) y tabla EFCS R86 de la segunda tanda; construido, emulado y auditado, sin instalar. [R86](../docs/capture/e26-r86-cfw-376-tres-modos-nivelados.md)
- 11-11-2026: CFW 3.76 instalado (arranca) y tabla EFCS R86 escrita en NVRAM; faltan fotos de comprobación. [R86 §6](../docs/capture/e26-r86-cfw-376-tres-modos-nivelados.md)
- 11-11-2026: E26-R87 disparo remoto de los tres modos; Silent del 3.76 corregido y recalibrado (CFW 3.77, sin instalar); tabla EFCS R87. [R87](../docs/capture/e26-r87-disparo-remoto-y-recalibracion.md)
- 11-11-2026: G36 auditoría del selector PP del 3.77 (no pasa de PP6): la ruta de `libObj`/NVRAM/`CamMsgConv` acepta PP7–PP10; la causa es el tope de 7 opciones por lista de la clase Normal, que afecta a 25 de 34 filas. [G36](../docs/gui/g36-selector-pp-tope-7-opciones.md)
