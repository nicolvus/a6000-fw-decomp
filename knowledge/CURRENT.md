# Estado actual — léeme primero

Resumen operativo breve. Para el historial completo de decisiones, ver `knowledge/PROGRESS.md`.
Para restricciones del proyecto (sin firmware ejecutado, sin flasheo, sin `git push`), ver `docs/STATE.md`.

## S56 — transporte de registros IMX210 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s56_imx210_transport.py` 26/26, emulación Unicorn del código real):** `SetExposure` solo escribe registros sombra; `Execute` (vtable+0x38) los envía por **P2S(DFE0)** (`0xfc088300`): los «IDs» (119 punteros `0x43fe995c`, mapa `0..0x155`, ID1 duplicado) son **direcciones de 16 bit**; trama `81|len|81|AH AL|datos`, 119 registros → 2 transmisiones, ida y vuelta exacta. `svd/shd/spl` = IDs 3–8 (+0x144–0x149); `ShutMode` 0–4 → ID1 = 40/C4/94/D4/C0 (solo el 2 carga 0x100/0x101). Pulso SSB = ID1 bit3 enviado 2 veces. CISIF = receptor (no bus de configuración). Cadena sin GPIO/P4C. A7S: mismo P2S, registros de 5 B con byte de dispositivo, sin ShutMode 2. SENS_B: sin consumidor (clústeres 0xf2a1/0xf2403 parecen reloj/ADC).
Fin electrónico de integración a resolución completa: **NO VERIFICADO**. **S51 se mantiene.** Próximo: traza pasiva CIS0+XPI+VD (decodificable) o rastrear origen de `0x43eb35d0`.
[Conclusiones](../docs/capture/s56-conclusions.md) · [Matriz](../analysis/s56-evidence-matrix.json). REA con `GHIDRA_MAXMEM=6G`, sesión cerrada.

## S55 — origen de los pares GPIO (base de backup BK4), A7S vs A6000 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s55_bionz_sync.py` 16/16):** los pares (canal, bit) de la tarea CA **no** vienen de código externo: slot de servicio `+0x2e0` = `Backup_read_4Byte` (liro.ko) y los valores están en
`0110_backup/*/CX77500_*.bin` (A6000; A7S `CX78500_*`), formato BK4 reconstruido de `backup.ko`. El escritor de `0x43e77298…0x43e772d4` es **`0x436bcef4`** (A7S `0x436dc054`; S54 no lo vio: store vía GOT).
Lectores = (3,17),(10,3),(0,12),(0,7),(5,14), salidas (7,15),(7,13): handshake SIO; banco 0 = `GPIO_S_n` (nfc.ko + esquema; (0,7)=CA_RELEASE_LOCK). Estructura **idéntica en A7S** (14 funciones 1:1, mismos IDs/valores;
único `set` extra de A7S = no-op). Ningún par con bit 9 fuera del banco 0 → `GPIO_9` sin lector GPIO (INFERENCIA); `SENS_B` sin rastro (NO VERIFICADO). `ExposureEndNotify`/`ExpStartComp` no leen GPIO.
IMX210 sin avance. H55-1 VERIFICADO, H55-2/4 descartadas en lo recuperado, H55-3/5/6/7 NO VERIFICADO. **S51 se mantiene.**
Próximo: traza pasiva P4C/VD/CIS0 autorizada; estático: bloque SENS_B (escritores `0xf2a1…`), IDs dinámicos de `0x43716dd0`.
[Conclusiones](../docs/capture/s55-conclusions.md) · [Matriz](../analysis/s55-evidence-matrix.json). REA: `analysis/rea-independent/bin/session_daemon.py` con `GHIDRA_MAXMEM=6G`, 1 sesión cerrada.

## S54 — P4C, tipo de mecanismo 0 y BIONZ (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s54_p4c.py` 21/21):** `CA_1ST_CURTAIN_START` (P4C) llega a BIONZ por **`SENS_B` (AA13) y `GPIO_9` (AD21)**, igual en A7S (el esquema A7S sí está en
`docs/references/`: corrige «pines A7S inferidos» de S53). Darwin solo escribe **P4C←0** (9 sitios por ROM, nunca ←1; `0x51f2` conserva b12), también en la rama sin mecanismo;
en A7S Silent la escritura P4C se conserva. **Tipo 0 de A6000 ≡ rama Silent A7S** en exposición/diferidos/ADC (diff llamada a llamada), pero **no** en reposición (A7S Silent actúa
con `no_silent=1`; tipo 0 nunca) ni en lo previo a Darwin. Tipo = `[0x20000050+ch]` validado por `[0x200002c0+ch]` (manejador 33 de `0x2a1a0`); escritor NO localizado.
BIONZ: primitivas GPIO `0x43b5e2bc/22e/29a` (base `0xf2910000`); lectores de la tarea CA usan variables de pin sin inicializar en la imagen → **consumidor de P4C NO localizado**.
IMX210 sin avance. H54-1 INFERENCIA, H54-2 PARCIAL, H54-3/4/7 NO VERIFICADO, H54-5 PARCIAL reforzada, H54-8 INFERENCIA fuerte. **S51 se mantiene.**
Próximo: `av-cam` A7S (barrido `gpio_get`) + inicializador de pines; traza pasiva de P4C/`GPIO_9` autorizada.
[Conclusiones](../docs/capture/s54-conclusions.md) · [Matriz](../analysis/s54-evidence-matrix.json). SHA ROM A6000/A7S y `av-cam.bin` OK.

## S53 — parser CAIF de Darwin A7S vs A6000 (Claude, 19-10-2026)

**VERIFICADO (bytes, `tests/test_s53_darwin_caif.py` 10/10):** el paquete CAIF ev1 (22 B) llega a Darwin (FM3, base `0x4200`) por
MFS5 (P36–P38 = `MSS_*_DWN` ↔ IC6000 BIONZ X) como mensaje mss-async **ID `0x0c`** (código `03 01`, 22 B; identidad con op `0x10300`:
INFERENCIA fuerte). **Parser:** A7S `0x18396`, A6000 `0x17f8c`, idénticos salvo que A7S guarda `pkt[+0x12]&0x20` en `S+0xd0.b5`
(`0x18460`) → predicado `no_silent` `0x19a86`/`0x216c2` que **impide escribir P4D/P4E** (`1ST/2ND_CURTAIN_MG`; `0x2172c`, `0x21786`,
`0x217b2…`, diferidos `0x214dc/0x214fa`) y omite el seguimiento ADC. A6300 tiene la misma rama. **A6000 descarta el bit** y sus
escritores (`0x20cb2`, `0x20d00`, `0x20d26…`) no tienen argumento Silent. Modo 2 de `+0x0d`: sin consumidor (PARCIAL).
**Escenario B:** falta lógica de firmware en Darwin A6000 (además de LIRO e IMX210). **S51 se mantiene.** Pines A7S por inferencia.
[Conclusiones](../docs/capture/s53-conclusions.md) · [Matriz](../analysis/s53-evidence-matrix.json). SHA 3/3 ROM Darwin OK.

## S52 — clase 0, `+0x748` y cortinas (Claude+Codex, 19-10-2026)

**VERIFICADO:** la A7S **no suprime** el control de cortinas en LIRO. Envía igual el paquete CAIF ev1 al MCU de obturador, pero con
Silent **marcado** (`+0x12` bit `0x20`, `+0xd` modo 2; `0x4386329a/0x43863258`) y byte de clase = 3. Además deja de **esperar** las
respuestas del mecanismo: CAIF 3 y bandera `0x800000` (`0x438b1cba`, `0x438b726c`), según `captura+0x748`. Esa bandera es la misma que la
A6000 tiene en `+0x740`: tiene lectores pero ningún escritor (latente). La clase 0 llega a `param+9`: `0x43864c74→0x43f04c8c→R+0x69→cap+0x651→0x436f2938→vtable+0x28`.
Identidad de R resuelta por el coordinador (`analysis/s52_coordinator_check.py`). La clase sola no omite CAIF/MMIO (solo el mensaje `0x22`).
**INFERENCIA fuerte:** la decisión física la toma el MCU Darwin (parser CAIF no localizado). P5 NO VERIFICADO; **S51 se mantiene**.
Corrección: IMX235 `cfg2+4|=8` en todos los ShutMode (no solo 0). Próximo: parser CAIF en `darwin_core.bin` A7S vs A6000 (bit `0x20`).
[Conclusiones](../docs/capture/s52-parallel-conclusions.md) · [Matriz](../analysis/s52-evidence-matrix.json). SHA 8/8 + manifiestos OK.

## A7S Silent reconstruido (estático) — 19-10-2026

**VERIFICADO (bytes+LLVM+REA, test `work/claude/tests/test_a7s_silent_facts.py`):** en A7S 3.20, `0x40e3`→estado `+0x250`→conversor
`0x4379ec04` (tipo {0,2})→`captura+0x78c`→ (a) selector `0x43826d58`: tipo 2 ⇒ drive_mode `0x4e/0x4f` (IMX235, columnas propias,
45/69 campos distintos de `0x0b`); (b) política `0x438649bc`: tipo 2 ⇒ clase de obturación 0. A6000: receptor `+0x238` existe, pero su
selector `0x437f7f98` y su política `0x43842158` son el mismo código **sin** ramas Silent, y el IMX210 no tiene modos `0x4e/0x4f`.
H1 mayormente refutada; S51 (no parchear) se mantiene. Pendiente: clase 0 → cortinas. [Informe](../docs/capture/a7s-silent-reconstruction.md).

## Referencia comparativa — 19-10-2026

**Decisión del usuario:** A7S 3.20 sustituye a A6300 2.01 como referencia (A6300 queda histórica; supera la instrucción del 16-10).
Manuales Level 3: mismo CXD90027GF con 12 pares sub-LVDS; sensores IMX235 (A7S) / IMX210 (A6000). [Comparación](../docs/references/a7s-vs-a6000-service-manuals.md). Firmware A7S en `firmware/extracted/a7s-fw320`, sin analizar.

## Hito REA independiente (Línea B) — 19-10-2026

**VERIFICADO:** REA 6.5.0+Ghidra 12.1.4 abre `av-cam.bin` (raw ARM, base 0x43541000)
con `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`: análisis completo en ~459–486 s (por defecto
330 s no basta), 42006 procedimientos, pico RSS 2,3 GB. Frente a 464 entradas históricas:
363 exactas, 9 absorbidas, 92 ausentes (las Thumb sembradas a mano, p. ej. 0x43789cc0).
234/234 listados idénticos a Línea A; LLVM decodifica en las 38708 direcciones.
`libmprctrl.so`: 8 funciones coinciden en bytes, nº de instrucciones y offsets (análisis ~22 s).
**PARCIAL:** el decompilador B no pliega literales a `_DAT_f3c3xxxx` (Línea A sí, 19/234).
Setters 0x436c6288/6294 escriben `0xf3120000+0x48/+0x4c`; semántica NO_VERIFICADO.
**Sin evidencia nueva** de exposición electrónica independiente de cortinas.
Límite: la sesión REA no persiste (rea#1048 abierta); Línea A sigue siendo la referencia de verificación (Thumb sembradas); la exploración nueva va primero por REA: ver `docs/STATE.md` § Política de ingeniería inversa.
Línea A, `silent-liro.*`, firmware y S1–S48 intactos (SHA idénticos).
[Informe](../docs/capture/rea-independent-milestone.md). Próximo exacto S48 sin cambios.

## S51 — decisión vigente (19-10-2026)

**A=NO, B=NO, C=NO.** No hay una ruta electrónica demostrada ni un parche justificable, y tampoco una imposibilidad demostrada.
T1 (VERIFICADO): el modo `0..7` (getter `0x43842404`→`0x43eedecc`) solo llega al registro `0x4383fb6c` (+0x6d/+0x6e/+0x70,
serializado por `0x438e2b98`) y a eventos; `ModeRsvParam` = `0x43795a60(cap+0x4d0 drive_mode, +0x4d4, +0x4d5)`, con el drive_mode
fijado en `0x437f7ff4` sin depender del modo. C_Imager: `SetMode 0x436d62e4`, `SetExposure 0x436d6320`, `SetRead 0x436d6398`.
T3 (Codex): no hay guarda configurable sobre el cierre de la 2ª cortina. T2: ID1/100/101 sin dirección/semántica de sensor.
**Decisión: detener el parche.** Retomar solo con el datasheet del IMX210 o con una traza pasiva autorizada de la interfaz serie
del sensor. [Decisión](../docs/capture/s51-decision.md) · [Codex](../docs/capture/s51-codex-t2-t3.md). SHA 1490/1490 OK.

## S50 — estado anterior (19-10-2026)

**VERIFICADO (investigación paralela Claude+Codex):** `0xb6 A_LINEAR_ELEC_SHUT` sin fila de callback ni caso `C+0x60` → inerte. `0x4382dd78`
construye B desde C (`C+0x94/95→B+0x36/37`); `0x43842158` usa `C+0x94/95` como override del modo `0..7` (`0x43eefb1c+0x60`) que solo se exporta
a registros de estado. **CORRECCIÓN S49:** `1/2/3/6` = cantidad de callbacks, no clases. Bypass CA `+74f` no es foto silenciosa.
**Pregunta final: NO_VERIFICADO** (ni demostrada ni imposibilidad). Falta consumidor físico del modo y significado eléctrico ID1/100/101.
[Conjunto](../docs/capture/s50-parallel-conclusions.md) · [Claude](../docs/capture/s50-claude-electronic-config.md) · [Codex](../docs/capture/s50-codex-exposure-curtains.md). SHA 1490/1490 OK.

## S49 — estado anterior (19-10-2026)

**VERIFICADO:** `0x301d7` = id OSAL de la cola de comandos de ajuste/servicio; clave `0xce` = `S_IMAGER_CURTAINMODE`
(payload `(habilitar, valor)`). Tabla de servicios de `av-cam` copiada por `liro.ko` (`tsk_entry`, `memcpy(hdr[0x14]+0x24)`):
slots `0x4354129c/a0/b4` = `osal_unreg_msg_queue_cb/osal_reg_sync_msg_queue_cb/osal_dynamic_id`. Productor: puente USB
`libsencore` (`TransactionStart 0x25fc8`) y `adjstctl`/`libtestcmd`; `libObj` solo claves 0/1/0x67. **NO_VERIFICADO:** emisor
en uso normal y significado del valor. Informe: [S49](../docs/capture/s49-capture-config-producer.md). Próximo S50:
consumidores de `C+0x94/+0x95`, `C+0x60`, `0xb6`.

## S48 — estado anterior (19-10-2026)

**VERIFICADO:** servicios `+0x1e8/+0x1ec/+0x200` de la tabla `0x435410b4` están a 0 en el blob y solo se leen
(wrappers `0x43561298/0x435612b4/0x43561324`): el proveedor y el emisor del paquete `0x301d7` están **fuera de
`av-cam.bin`**. Función de alta `0x43789fdc` (crea manejador `0x301d7`). **NO_VERIFICADO:** emisor/productor de
`+0x1c/+0x1e`. Informe: [S48](../docs/capture/s48-service-table-provider.md). Próximo: buscar el emisor en
userland (`libObj.so` etc., hits `d7 01 03 00`) o cerrar la línea como frontera externa.

## S47 — estado anterior (19-10-2026)

**VERIFICADO:** entrada `0x43789cc0`, registrada con ID `0x301d7`;
fila clave `0xce` en `0x43ff29b8` → handler `0x43789708`.
Copia solicitud `0x140`B a `0x43e95420`; payload en `0x43e9543c`
→ argumento4 de `0x437da100` → `0x43ed4620` → callback `0x437dad78`.
`0x43ed44dc` es otra solicitud sintética, no el buffer recibido.
Callback ANTES de copia C: despacho `0x43792f9c` domina copia `0x43794096`;
`0x43ae90ce` copia `0x1a4` desde `0x43e9d3b4` a `0x43e9b380`,
incluyendo `+0x94/+0x95`. S46 no queda refutada por orden.
**PARCIAL:** productor original de los dos u16 anterior a `0x43789cc0`;
valor2 y propagación B/G. Servicio de registro `+0x1ec`, slot `0x435412a0=0`.
**Próximo exacto S48:** contrato/proveedor de ese registro y productor del
paquete ID `0x301d7`, clave `0xce`, stores `+0x1c/+0x1e`.
No repetir orden ni solicitud sintética como única fuente. Punto opcional VD
aplazado; clases1–3 físicas y VD/cortinas sin cierre. Hito S46–S52 abierto.
SHA/manifiestos intactos; sin git.
[Informe S47](../docs/capture/s47-payload-producer-and-order.md).

## S46 — antecedente (18-10-2026)

**VERIFICADO:** owner `0x43e15f18` → `0x436c6f3c` → `0x436c7950`
→ setter `0x43acee66` inicializa `0x43e16d2c=0xf3120000`;
destino de S45 base+220=`0xf3120220`, escritura condicional.
C fuente `0x43e9d3b4` construido con offsets partidos `1e40+2c`.
Callback `0x437dad78`, fila `0x43ff8adc`, clave `0xce`, escribe
C+94/+95 desde payload4B: primer u16!=0 → (1,low8(segundo u16));
primer u16=0 → (0,0). Scratch `0x43f7bbf4`, distinto de snapshot `0x43ef2474`.
**PARCIAL:** propagación condicional de (1,2) por copia a C/B/G;
productor del payload y orden completo pendientes. P=padre+1454 sin alias C.
Integración/cortinas y semántica eléctrica `0xf3120220` NO_VERIFICADO.
**Próximo exacto S47:** argumento4 de `0x437da100` hasta payload
`0x43ed4620`; productor de los dos u16 de clave `0xce` y orden frente
a `0x43792f9c/0x4379409e`; después semántica del controlador VD.
[Informe S46](../docs/capture/s46-vd-base-and-context-identity.md).

## S45 — antecedente (18-10-2026)

**VERIFICADO:** contexto437b5b14=43eaadd8, copia0xb0 desde43e993a4;
VD_Pre reconstruye este último desde raíz copiada43e99514.
C=contexto[14]=43e9b380, copia1a4 desde43e9d3b4. AliasP/C pendiente.
GetterIMX210+3a0=43ad9202, virtual+74;43ad90b6→438c828c usa el retorno,
calcula captura+570→43795dec→436c74c8→43ad2bd6 escribe base+220.
**PARCIAL:** controlador43e16d28, base=*(43e16d2c) sin escritor recuperado;
MMIO físico de esa escritura e integración/cortinas NO_VERIFICADO.
**Próximo exacto:** escritores43e9d3b4+94/+95/copiaP→C y escritor43e16d2c
desde owner43e15f18. No repetir getter+74 ni consumidor/virtual+a8.
Termina serie explícitaS40–S45; hito abiertoS46+, sin agotamiento/Línea E.
SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S45](../docs/capture/s45-context-identity-and-physical-closure.md).

## S44 — antecedente (18-10-2026)

**VERIFICADO:** consumidor436d75f8 lee119 paresIDu16/byte+2 de43fe995c;
436d839c→436d79b0→75f8→backend+298→436d5ed0 carga MMIO,
436d5f60 pulsa B+8. Canales{1,2,0}; bancos43bc14e8.
Virtual+a8=436d65b8 compara nibble alto del registroID0 entre13 índices;
ignora flags y devuelve1 si cambia. No transporte dentro del comparador.
**PARCIAL:**4385cf2c produceP+95=2; P=raíz+2bc, alias con
C=*(contexto+50) no probado; snapshot43ef2474 candidato, no identidad.
**Próximo exacto:**origen del contexto de437b5b14 y campo+50 hastaP/C;
después lectoresIMX210+3a0 y semántica físicaID0/integración/VD/cortinas.
No repetir consumidor/virtual+a8; no agotamiento estático ni Línea E.
OSALbit31 y AF permanecen cerrados. SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S44](../docs/capture/s44-register-consumer-mode-table.md).

## S43 — antecedente (18-10-2026)

**VERIFICADO:** PIC4401eee4; slots resueltos a estructuras4401c6xx–4401caxx,
ID u16 + dato byte+2, b3, sin MMIO directo/vtables.43ad9a40/43ad99d4
guardan estado en objeto+fc (la variable ya no representa base PIC).
**RECHAZO** códigos de bloqueo AF: cadenas SetSequenceMode img/fratechg/clamp,
ImgMode/IMAGE_FRAME_RATE/SYNC_RAW_OUTPUT_SIZE; virtual+94 consulta tabla de
modos del backend. **ACEPTO**4380e020/43902718 como log/trace.
**PARCIAL:** transporte de staging, lector IMX210+3a0 y escritor C+94/+95.
**Próximo exacto:** consumidores de registros por slots PIC y virtual+a8 desde
436d92e0; virtual+10 436d8ff4 es getter de0x70B, sin transporte. Después
C=*(contexto+50) en4382dd78→B43eae270→G43ea6ad4→43842158.
No cierre físico, agotamiento global, Línea E ni reapertura OSAL bit31.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S43](../docs/capture/s43-exposure-mmio-and-lock-codes.md).

## S42 — antecedente (18-10-2026)

**VERIFICADO:** corrección de nomenclatura S41:436d6320 es wrapper,
436d634a llama virtual+28; vtable43fcc090+28=436d6f6d. Constructor436d72e8
y factoría436d6504 publican objeto43e7f4a8 en contenedor43e7f858.
Clase2: cargas BYTE en436d7136/7142 desde parámetro+08/+14,
buffers4401c6d2/4401c7ce, cálculo→objeto+3a0. Cortinas/VD NO_VERIFICADO.
**PARCIAL:**4382dd78 copia C=*(contexto+50), C+94/+95 a B43eae270+36/+37;
4384cb58→437b0480 copia c14B a G43ea6ad4;438412d0 pasa G al selector.
Escritor original de valor2 pendiente. No confundir stores43845b68/70:
son otro objeto. R43e9b548+5cc=43e9bb14=ImgState43e9baec+28;
lectores438553dc/4385558a pertenecen a43e18c60, no R.
Cadena de bloque0x44=68B hasta4378e334/43795a60 contrastada, pero sin
dependencia recuperada desde R+5cc. Descriptores3023: parser sin tipar.
**Próximo exacto:** escritores C+94/+95 hasta valor2; lectores IMX210+3a0
y buffers hasta transporte/cortinas; alias ImgState+28 hacia43eea2e4;
consumidor indirecto de getters3023. No reabrir OSAL bit31 sin evidencia nueva.
No agotamiento estático: Línea E no activada; A6300 existe, sin analizarlo.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S42](../docs/capture/s42-exposure-call-identity.md), `analysis/ghidra/s42-findings.json`.

## S41 — antecedente (18-10-2026)

**PARCIAL:** cola principal30001 y snapshots3030f. Productores internos
4000/4036:43816448/43818c1c/43817e20→4381a138→435aa20c→4356120c.
Conversores:43bc59e0={1,0,5},43bc5a50={1,2,0,3}; nombres de opciones
NO_VERIFICADO. Case1:43b01026 envía objeto+4/564B; case10 largo:
43b00f62 envía objeto+6c0/5e0B, incluyendo copia previa en+6c4.
Destino8003030f frente a receptor3030f: bit31 sin resolver, no cerrar bucle.
R+458 o R+48→0,2,1,4 en VD_Pre; sin enlace demostrado a integración.
**Próximo:** productores de argumento1+36/+37 de43842158 (valor2),
argumentos+8/+14 de clase2 en436d6f6c y sincronía de cortinas;
metadatos3023 y lectores de R+5cc hasta argumentos tipados del sensor.
Slots OSAL en435410b4 cero: frontera de implementación; se activó Línea C
para contrastar selector EFCS separado: banco+41c, diagnóstico+7e y
anulación+36/+37. Clase2 alcanza rama distinta; cierre físico NO_VERIFICADO.
Sin agotamiento A/B universal.
SHA/proyecto intactos.
[Informe S41](../docs/capture/s41-message-origin-imx210.md), `analysis/ghidra/s41-findings.json`.

## S40 — antecedente (18-10-2026)

**PARCIAL:** `context[0]+24/+48/+458` provienen de staging43edf684,
escrito por comandos API4000/4036/3023 (bytes solicitud+0a/+09/+0e),
con ceros condicionales438040e8 y437935ae.43804cdc copia560B a raíz;
43804c82/43804d12→43b00d06 copian snapshot objeto+8. Tabla despacho
43fff30c:220×12B; tabla selección43ca3c21={1,1,0,1}.
API demostrada, menú/FPS/píxel y exposición/read-enable/generación física
NO_VERIFICADO. No agotamiento estático.43804cc8 toma staging;
43806a80/43806d50 toman mensaje+4/+8. **Próximo:** productores originales
de esos mensajes case1/10 de438069f0, después enlace
tipado a selectores IMX210. Proyecto readOnly/noanalysis y firmware intactos.
[Informe S40](../docs/capture/s40-context-origin-imx210.md), `analysis/ghidra/s40-findings.json`.

## Qué existe

- Grafo de conocimiento en `.knowledge-cache/knowledge.sqlite` (regenerable, gitignorado):
  **1189 entidades Function, 1764 relaciones CALLS deduplicadas (2604 fuentes de evidencia
  preservadas en `relation_sources`), 39 relaciones CORRECTS/SUPERSEDES.**
- Fuentes del grafo: dossiers JSON legacy, ~430 exports Ghidra (pseudocódigo decompilado),
  5 evidencias REA. Catalogadas por forma estructural en `knowledge/catalog/JSON-CATALOG.md`
  (2146 JSON, 108 familias; dos familias explícitamente excluidas por falta de identidad
  verificable — ver PROGRESS.md Fase 12.4.A).
- CLI unificada: `scripts/knowledge/search.py` (`exact`/`text`/`tree`/`section`/`graph`/
  `trace`/`claim`/`ask`/`freshness`). Servidor MCP: `scripts/knowledge/mcp_server.py`
  (11 tools, límite global 20000 chars).
- Benchmarks: línea base pre-rediseño en `knowledge/benchmarks/baseline-2026-10-18-pre-12.6.md`
  (NO editar). Benchmark rediseñado con verdad de referencia estructurada en
  `knowledge/benchmarks/report-v2.md` (generar con `scripts/knowledge/benchmark_v2.py`).

## Última fase completada

**S39 (18-10-2026):** av-cam SHA/memoria verificados; silent-liro solo
readOnly/noanalysis, sin mutaciones. Tres llamadores de 43814d24 convergen
en config+0c→43ef71a4→4387a6c4→caché 43e77ccc por unidad, valores
0/1/2/4; cambio invalida/reinicializa APL, sin campo hardware/pitch enlazado.
No confundir índices P con remapeo separado input+38. 43ae8d56 fija
context[2]=root+5a4; campo43e9bb14 tiene cuatro escrituras en VD_Pre,
copia/cero/remapeo según estado. Nombres de píxel y opción/FPS no demostrados.
**PARCIAL**, sin declarar agotamiento estático universal. Próximo: fuentes
context[0]+24/+48/+458 y copias masivas hasta solicitud/tabla tipada.
Incógnita física prioritaria: productor/handle/VD y cierre de integración.
[Informe S39](../docs/capture/s39-image-format-apl.md),
`analysis/ghidra/s39-findings.json`. Se conservan S31–S38 debajo como historial.

**S38 (18-10-2026):** SHA av-cam verificado, silent-liro readOnly/noanalysis;
.gpr/.rep intactos. 85 literales 61003c, 16 sin xrefs: pool compartido,
sin servidor/alta recuperados. Blob ORIL/LIRO, no ELF; readelf -d/-r y nm
fallan. Tabla 435410b4, slot +2e4=0 en archivo.
**FRONTERA ESTATICA AGOTADA** para resolución ELF/valor externo del slot
en este blob; no ausencia universal de receptor. Extents→P/APL y productor
físico YC NO_VERIFICADO. **Próximo paso exacto:** enum de formato S33,
input+38←P+1b4←context[2]+28, conversor 43814d24 y campos APL/stride/tamaño.
[Informe S38](../docs/capture/s38-dmm-osal-static-frontier.md),
`analysis/ghidra/s38-findings.json`. S31–S37 se conservan debajo como historial.

**S37 (18-10-2026):** `libmprctrl.so`, SHA
`514e14116caa1d15d75bd56641dabfe815f620b6208008929c44d8d70386011d`,
define AllocDmmMemory/FreeDmmMemory; proyecto nuevo `libmprctrl.gpr`, copia
0444 y export readOnly. Getters originales son **DmmAccessPLA**: leen
dirección/tamaño en respuesta+0x10/+0x14, sin demostrar dominio físico/lógico
ni valor concreto. AllocDmmMemory devuelve cabecera de paquetes, otro layout.
Cliente OSAL **0x61003c**, payload 0x18: compatible parcialmente con campos
S33, pero no idéntico a envoltura 0x55/0x70 ni prueba del slot av-cam.
PLT libObj 0xdc180 importa exactamente DmmCloseAndFree definido aquí,
con DT_NEEDED directo. **Productor físico YC NO_VERIFICADO.** Próximo:
receptor 0x61003c y proveedor tabla av-cam+0x2e4 hasta escritor de extents,
misma clave/ID Rendezvous y APL. [Informe S37](../docs/capture/s37-libmprctrl-dmm-extents.md),
`analysis/ghidra/s37-findings.json`. S31–S36 se conservan debajo.

**S36 (18-10-2026):** analizada únicamente `libInfraScalarMpr.so`, SHA
`b56b4c6172a60b879ebf405bc64e19e7456d230ff6125a21bbd4469e35c0d2c9`, en
proyecto Ghidra separado, export final readOnly. `AllocDmmMemory(int,ushort*)`
y `FreeDmmMemory(int)` son **UND**, no cuerpos locales. `AllocSharedMemory`
devuelve ID SysV y dirección virtual de `shmat`, usada en copia de datos still;
no demuestra origen YC/DMA ni relación con Rendezvous. Próximo: localizar
definidor de `_ZN9DmmAccess14AllocDmmMemoryEiPt` y
`_ZN9DmmAccess13FreeDmmMemoryEi`; resolver por separado slot av-cam.
[Informe S36](../docs/capture/s36-libinfra-scalar-mpr-memory.md),
`analysis/ghidra/s36-findings.json`. S31–S35 se conservan.

**S35 (18-10-2026), investigación de firmware:** los cuatro objetos DFE son
Ofmt/Ifmt; RTTI, vtables y métodos +8 de sus hijos resueltos. Leen y activan
bit 0 de SGC `0xfc0a1210/1310/1610/1710` (+0x1000 en unidad 1), sin lectura/ack
APL recuperado. Bit `0x00200000` sin causa física identificada; los usos en
enable del controlador son otro dominio. **FRONTERA ESTATICA AGOTADA para
esta vía**, no imposibilidad universal: falta routing/semántica hardware o traza
pasiva correlacionada APL/IRQ/VD/handle en cámara sin flashear. Ciclo físico
NO_VERIFICADO. Próximo: DMM importado `0x43561524`, `tabla+0x2e4`, productor
Rendezvous y lector YC real. [Informe S35](../docs/capture/s35-dfe-objects-static-frontier.md),
`analysis/ghidra/s35-findings.json`; S31–S34 se conservan debajo como historial.

**S34 (18-10-2026), investigación de firmware:** tres BL a `0x43814ea0`
contrastados con el blob; direcciones → MMIO → kick 0/1 síncronos en Image.
Ruta VD_Sequence demostrada; selector permite categoría HS para dos productores,
sin demostrar factibilidad conjunta de cada modo/rama. Sin llamada directa desde
Post/Drive. El evento Drive `0x80` puede preceder Sequence o venir de timer 4:
no demuestra fin DMA. Registrador DFE de cuatro callbacks y cuatro conversiones
de causa resueltos; falta mapear bancos APL a causa/estado/callback y handle/VD.
Kick en `…0500` es +0x100 respecto de bancos `…0400`. Cuadro propio/siguiente
y cierre inicio-exposición/DMA/fin-exposición **NO_VERIFICADO**.
[Informe S34](../docs/capture/s34-apl-dma-vd-interrupts.md),
`analysis/ghidra/s34-findings.json` / `s34-audit.json`; proyecto/binario intactos.

**S33 (18-10-2026), investigación de firmware:** AllocShare completo y sus
26 llamadas YC cerradas estáticamente (12 funciones, 13 parámetros locales
inicializados a cero). `input+0x10` referencia handles de trabajo, varias rutas
AllocRendezvous; helper `0x43814ea0` puede activar `+0xc8` y escribir
`input+0xd4=P+0xbc` en tres productores (también se propaga por copia).
Rama APL seguida hasta palabras de extents y registros MMIO en bancos
`0xf3850400/0xf3950400/0xf3a50400`; el flag secundario es estado de software.
La palabra `handle+4` es clave conservada de la solicitud, no dirección raster
demostrada. Despacho Image dentro de VD_Sequence y publicación alternativa
desde HS_Sequence (`0x43790b68`). Pendientes: proveedor importado DMM
(`tabla+0x2e4`), productor que satisface Rendezvous, pitch/formato y fin DMA físico.
[Informe S33](../docs/capture/s33-yc-rendezvous-producer.md),
`analysis/ghidra/s33-audit.json`. Proyecto y binario sin cambios; sin cámara.

**S32 (18-10-2026), investigación de firmware:** continuó S31 sin ampliar la
arquitectura de conocimiento. Resueltos `0x43ad6034` (despachador), su thunk
`0x43ad6052`, el adaptador `0x43b03a48`, registradores
`0x4379704c`/`0x43797090` y seis destinos de las listas VD. Nueva rama
`0x4379b44c→0x4390366c` prepara referencias DMM compartidas en el bloque YC;
no es únicamente temporización. CORRECCIÓN de S31: «YC out window overflow»
se imprime en `0x4379cb2e`, dentro de `0x4379bb90`; es comparación temporal,
no finalización DMA. Falta el handle fuente efectivo (`input+0x10/+0xd4`),
su mapeo a píxeles/pitch/formato y la tupla del consumidor remoto.
Evidencia estática, sin cámara: [informe S32](../docs/capture/s32-vd-callbacks-sync-ycout.md)
y `analysis/ghidra/s32-findings.json`. El pendiente S31 descrito abajo es histórico
y queda actualizado por S32; la captura física sigue NO_VERIFICADO.

**Fase 12.11** (2026-10-18): tras cerrar la arquitectura del sistema de conocimiento
(instrucción explícita del usuario de no ampliarla más), se retomó la investigación
principal del shutter completamente electrónico.

1. `SetRead` IMX210 (0x436d7e08) decompilada íntegra vía Codex: no lee
   Silent+0x238/+0x280 ni produce buffer YC/DMA (ver `docs/capture/silent-imager-consumers.md`).
2. Corregida línea obsoleta en `CONTEXT.md`: el alta/callback de `0x50004` ya estaba
   cerrado desde S28, no pendiente.
3. Descartado, por ausencia total de cadenas `IMX210`/`exposure`/`SilentShutter`/`EFCS`
   en los 90+ `.ko` del firmware A6000, que el control del sensor viva en un módulo de
   kernel separado — refuerza que todo vive en `av-cam.bin`/librerías de servicio.
4. **Hallazgo S31** (`docs/capture/s31-camera-main-sync-strings.md`): subsistema
   `CAMERA_MAIN_SYNC`/`DFECore` en `av-cam.bin` — motor de temporización VD del sensor
   que ninguna sesión S16–S30 había explorado (todas se centraron en la capa de
   servicio libObj.so/libBizFw.so). Decompiladas 8 funciones clave vía Codex:
   `VD_Pre` (0x43792a0c) →evento 0x40→ `VD_Sequence` (0x4379155c) →evento 0x100→
   `VD_Post` (0x4379210c) →cola→ `VD_Drive` (0x4378f410); variante `EC_VD_Post`
   (0x4378f848) guarda el número de VD procesado en 0x43e992dc, comprobado por
   `int_LM_Send1st_Handler` (0x43792750); `camIntHandler0/1` (0x436cf954/0x436cf780)
   despachan causas de interrupción reales. **VERIFICADO: acceso MMIO real** a
   registros físicos 0xf3c30110–0xf3c3015c vía 0x436ccd9c→0x43ad6006. **PARCIAL:**
   `VD_Sequence→0x43796954→0x4379bb90` (SyncYCout.cpp) es el candidato más cercano
   al productor YC, pero no entrega dirección de píxeles/plano/pitch/fin DMA.
   **Pendiente exacto:** resolver los destinos de las llamadas indirectas vía
   `0x43ad6034` desde las listas de trabajo de `VD_Drive`/`VD_Post`.

**Fase 12.6** (2026-10-18): validación del grafo ampliado + rediseño del benchmark.
Encontrado y corregido un bug real: 840 relaciones CALLS duplicadas (misma función
reanalizada en varias sesiones JSON generaba una relación por archivo en vez de una sola
con procedencia múltiple) — ver `relation_sources` y `_upsert_call_relation` en
`build_graph.py`. Añadida distinción llamada directa vs. vía thunk de Ghidra.

## Bloqueadores reales / pendiente

- **Prueba de integración E2E completada** (2026-10-18, Fase 12.10): relación CALLS real
  con evidencia exacta confirmada (`AsyncProcessor::execute()`→`captureStart()`, callsite
  `0x108144`) y una relación inexistente correctamente NO inventada. Checkpoint de prueba
  escrito por Claude Code recuperado por una sesión nueva de Codex (`get_current_state`,
  sin leer `CONTEXT.md`/`PROGRESS.md`), que además localizó la evidencia original y
  distinguió un hallazgo VERIFICADO de una pregunta NO_VERIFICADO real. Prueba inversa
  (checkpoint de Codex recuperado por Claude Code) también confirmada. Contexto medido:
  recuperación de Claude Code ≈4024 caracteres / ~1006 tokens estimados; sesiones Codex
  completas reportaron 29 247 y 16 805 tokens reales (cifra de sesión, no de una sola
  llamada — no comparable 1:1 con la estimación de Claude Code). Checkpoints de prueba
  eliminados tras verificar. Detalle completo en `PROGRESS.md` Fase 12.10.
- **Codex ya tiene registrado el servidor MCP** (resuelto 2026-10-18, con autorización
  explícita del usuario): `~/.codex/config.toml` ahora define
  `[mcp_servers.sony-a6000-knowledge]` (python3 del `.venv` del proyecto +
  `scripts/knowledge/mcp_server.py`). Respaldo previo en
  `~/.codex/config.toml.bak-20261018T114752`. Detalle completo en `PROGRESS.md` Fase 12.9.
- **El servidor MCP `sony-a6000-knowledge` para Claude Code aparece "Pending approval"**
  en `claude mcp list` dentro de esta sesión no interactiva: requiere que el usuario lo
  apruebe desde una sesión `claude` interactiva. Mientras tanto, la verificación anterior
  usó la función Python real del servidor (misma lógica, mismo archivo) como sustituto.
- **Validación desde sesión interactiva nueva** (no `exec`, ni en Codex ni en Claude Code):
  lo verificado arriba usa `codex exec` (no interactivo) y la función Python directa; el
  descubrimiento en el modo interactivo normal de cada cliente sigue sin confirmación
  externa del usuario.
- Mapeo de lenguaje natural a nodo de `trace` (p. ej. "¿qué llama a 0x50004?") sigue siendo
  manual: hay que ubicar el nodo primero con `search.py exact`.

**Siguiente objetivo (indicado por el usuario):** no ampliar más esta arquitectura salvo
defecto importante; volver a la investigación principal — captura completamente
electrónica en Sony A6000 — reutilizando las evidencias existentes.

## Siguiente acción sugerida

Ver "Próximo paso exacto" al final de `knowledge/PROGRESS.md`.
