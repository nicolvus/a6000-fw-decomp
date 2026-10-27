# Estado vigente — Sony A6000 reverse engineering

Estado técnico **consolidado**: conclusiones vigentes, rectificaciones y límites. No es historial ni lista de tareas:
cada afirmación enlaza al informe canónico donde está comprobada. Tareas y sus estados: [PENDIENTES](PENDIENTES.md) (única fuente).
Informes por tema: [INDEX](INDEX.md). Cronología: [PROGRESS](../knowledge/PROGRESS.md). Contexto mínimo para agentes:
[CURRENT](../knowledge/CURRENT.md). Rectificaciones completas generadas del grafo: [CORRECTIONS](CORRECTIONS.md); preguntas abiertas: [OPEN-QUESTIONS](OPEN-QUESTIONS.md).
La versión anterior de este archivo (instantáneas S44–S348 y bloques por fecha, íntegra) está en
[history/STATE-historial-2026-10-26.md](history/STATE-historial-2026-10-26.md).

## Estado vigente — 26-10-2026 (auditoría integral)

Proyecto abierto: hay piezas reales y reutilizables, pero **ninguna captura silenciosa completa validada**; no está demostrada ni la
capacidad ni la imposibilidad de fotografía totalmente electrónica a resolución completa.

- **S51: A=NO, B=NO, C=NO** ([decisión](capture/s51-decision.md)): sin ruta demostrada, sin base para un parche, sin prueba de imposibilidad.
- Estáticos cerrados con límite: E2–E5, E7, E8, E10 (a–c), E12, E14–E20, D1, D3, D4 y D6 ([evidencia](capture/s403-cierre-pendientes.md));
  E1 `NO_VERIFICADO` sin vías estáticas. Bloqueados por datos o hardware: E6, E9, E11, E13, D5; físicos F1–F6 (P1–P4, P6, P13–P16, P18–P21 ejecutadas el 26-10-2026 por USB (T001–T021, [registro](capture/registro-pruebas-camara.md)); P5/P11 caen con F4, P7/P17 descartadas; E22 cerrado con límite ([informe](capture/tipo2-analisis-estatico-2026-10-26.md)));
  respaldo R1–R3 (R3: historial con un binario de Sony). Sin firmware ejecutado ni cámara.
- Datos de auditoría y memoria temporal: [estado.json](../knowledge/audit/estado.json), [memoria.json](../knowledge/audit/memoria.json)
  (`scripts/audit/repo_audit.py`). Viabilidad por escenarios (17-10-2026): [estado-y-viabilidad](estado-y-viabilidad-2026-10-17.md).
- Los 133/372 del censo miden **documentación de etiquetas**, no código recuperado ni funcionamiento ([matriz de cobertura](capture/s51-static-coverage-and-tool-limits.md)).

## Conclusiones técnicas vigentes

Etiquetas: **V** = VERIFICADO (bytes/instrucciones), **I** = INFERENCIA, **N** = NO_VERIFICADO.

| Tema | Conclusión vigente | Estado | Fuente |
|---|---|---|---|
| RecordStill / RecordImage | A6000 `0x90b248` = RecordImage (sus diagnósticos lo dicen); pareja A7S `0x84a568`. RecordStill A6000 `0x908afc` ↔ A7S `0x847e1c`; RecordImage llama a RecordStill en ambos. Equivalentes salvo líneas de log (199 pares) | V | [contrato](capture/recordstill-contract-audit-2026-10-23.md), [S402](capture/static-closure-2026-10-25.md) |
| Llamadores | BL `0x90de2e` y `0x91634e`; 25 punteros Thumb a `0x90d7e8` son `call_fn` de `StateMgr::_FuncEntry`; `StateMgr::CallFunc` los ejecuta con `blx r3` (`libmprctrl.so:0x1cef2`); `0x91631e` es tabla TBB | V | [S382](capture/s382-recordstill-callers.md) |
| Activación real de la captura | Qué dispara RecordImage en ejecución, equivalencia de todos los callees y ocho parejas locales de RecordStill (43 llamadas mapeadas: 20 importadas, 23 locales) | N | [seguimiento](capture/capture-static-followup-2026-10-25.md) |
| Cola `0x40193` | ID construido desde literales `.text` (LDR); 16 B hasta `osal_snd_msg`; receptor LIRO `0x4381d16c`, tabla `0x44000174` (35×12 B); instalador `0x4379e93c` → descriptor `0x43ea048c` (campo `+0x14` = `0x46`), fila 189 de 372 punteros Thumb, bucle `0x4356082c`; servicio `+0x3c` = `sta_tsk`; recepción bloqueante. Ejecución real de la cabecera LIRO no observada | V / N | [flujo](capture/queue-40193-flow-2026-10-23.md), [S384](capture/s384-queue-id-0x40193-search.md) |
| Mensaje `0x10000005` | Dos constructores (PlayData y secuencia `0x3026`); único `ObjMsg(0x3a49,0x3026)` = `0x659cb0` (acción 13 de `ModelScalarPb`); local `0x109` auto-publicado (`0x65a8a4`); quién publica `4`/`2` a Pb/PbCap: ningún código de `libObj` | V / N (E1) | [S402](capture/static-closure-2026-10-25.md), [E2](capture/s403-e2-productores.md) |
| Estado IMX210 (gates) | Objeto `0x43f72d02` (A7S `0x43f7bce6`): gates `+3/+6` idénticos y sin escritor; Backup `0x3000b` = 256 B, gates a 0; escritor `S[0]` y copia G→S resueltos (`0x44020c9c → 0x43eb35d0`); 7 de 14 lectores cuelgan de la captura | V / N valores | [S300](capture/s300-state-xref-sweep.md), [S301](capture/s301-a7s-state-xref-sweep.md), [S205](capture/s205-imager-s0-writer.md), [S403](capture/s403-cierre-pendientes.md) |
| Mecanismo por modo (carril B) | `modo → matriz 69/59 filas → T1/T2/T3 → pares (flag,bit) → máscara u16 → MMIO DFE/CISIF (0xfc02a00c)`; mismo código en A7S y A6000, la diferencia son datos (34 vs 13 modos; 7 vs 15 vectores de registro). Identidad de `0xf292b000..8` y significado de `w0` | V / N | [S341](capture/s341-synthesis-b2.md), [S332](capture/s332-a6000-tables.md), [S333](capture/s333-mode-vocabulary.md) |
| `0x43fef404` | Tabla de ids de `Camera::Lens::ODL` (69 entradas A7S/A6300, 47 A6000), `0x000d` = capacidad 13; callback = adaptador de `memcpy` (13 B, I alta). No es tabla de tiempos | V / I | [S342](capture/s342-fef404-consumers.md), [S347](capture/s347-odl-field.md), [S348](capture/s348-odl-callback.md) |
| Silent en A7S | UI → LIRO `0x40e3` (existe también en A7S) → `+0x250` → bit `0x20`; conmutación IMX210 modos 0–4 / IMX235 0,1,3,4; la A6000 no tiene el selector ni el bloque de tiempos de la A7S (código ausente) | V | [S401](capture/s401-a7s-silent-control-path.md), [S402](capture/static-closure-2026-10-25.md), [S309](capture/s309-chain-presence.md), [S312](capture/s312-cluster-consumers.md) |
| `…ForLiro` | 216/221/240 nombres; soportados 0/0/6 (A6000/A7S/A6300); los cinco de obturador rechazados; `SetShutterTypeForLiro` solo en A6300 | V | [S174](capture/s174-forliro-api.md), [S383](capture/s383-forliro-silentlibobj.md) |
| `[EXL]` | Puede rechazar una captura (`hsiz_arcout > 2240`, `arcout > arcin`); entradas por modo de disparo solo en ejecución | V / N | [S403](capture/s403-cierre-pendientes.md) (E20) |
| Cortinas | P4D=1ST_CURTAIN_MG, P4E=2ND_CURTAIN_MG, P4C=CA_1ST_CURTAIN_START, P4B=CA_RELEASE_LOCK_MSS (no son serie); el enlace banco/bit `0xf2910048` → P4E no consta en el firmware | V / N (E11) | [fm3-gpio](capture/fm3-gpio-shutter-mapping.md), [S50](capture/s50-parallel-conclusions.md) |
| EFCS → sensor | Recorrido estático cerrado hasta IMX210; `CURTAINMODE 0xce` no gobierna el sensor (T1); SilentShutter `+0x238` sin lector de captura en `av-cam`; fin electrónico de integración sin identificar | V / N | [efcs-capture-selector](capture/efcs-capture-selector.md), [S51](capture/s51-decision.md), [S58](capture/s58-conclusions.md) |
| PMCA | `updatershell` inyecta un fdat propio (guard CRC + modelo/región/versión **sin firma**); `bk w 0x003e0005` escribe la propiedad `modelName` (`ILCE-6000` de fábrica); el efecto «shell mode» de `ILCE-6001` es no verificado | V / N | [S62](capture/s62-pmca-injection.md) |
| Patrón de logging | La fw3.21 reescribe etiquetas de trazas, no funcionalidad (9+ ejemplos); la presencia de una cadena **no** prueba una funcionalidad | V / I | [S128](capture/s128-label-map.md), [S130](capture/s130-new-modules.md), [S174](capture/s174-forliro-api.md) |
| Arranque y recuperación (E24-01) | Darwin (IC5700) es también el **control de energía**: `darwin_core` sube `DD_ON1/2/3` (núcleo y LPDDR2 del BIONZ). **No está demostrado** que el actualizador USB arranque sin `darwin_core`. El script del actualizador ignora el resultado de `ud_darwin_init`. La entrada por pmca exige el sistema normal (batería vía `upm`) | V / I | [E24-01](capture/e24-01-arranque-recuperacion.md) |

## Conclusiones corregidas (no reusar versiones previas)

La conclusión vigente va primero; el antecedente conserva su informe y se señala allí.

| Tema | Conclusión vigente | Rectifica | Fuente |
|---|---|---|---|
| Darwin — base ROM | La base es `0x4200`, NO `0`; no reusar punteros de proyectos Ghidra antiguos | proyectos a6000/a6300-darwin | [darwin-shutter-entrypoints](capture/darwin-shutter-entrypoints.md) |
| SetImageWrited | `0x6108/0x1007`, **no** `0x1009` | sesión 12 | [pool-write-completion](capture/pool-write-completion.md), [S29](capture/s29-writestill-end-to-end.md) |
| Recuperación por USB | Depende también de que `darwin_core` encienda el sistema, no solo de `nflasha1` y `ud_darwin_firmup`; la entrada al actualizador por USB pasa por el sistema normal (`up.sh user`), no por botón | custom-fw-recovery (punto 3), darwin-via-actualizacion (riesgo 4) | [E24-01](capture/e24-01-arranque-recuperacion.md) |
| Bootloader de Darwin (E24-02) | Existe código de arranque propio del MCU en `0x0–0x41ff` (el core, en `0x4200`, salta a su vector con el buzón `[0x20000706]=4` al recibir `0x11` estado 4; sin binario). `ud_darwin_init` provoca ese salto en cada actualizador. `darwin_core` no programa flash: `0x14/0x15` los atiende el arranque. **No está demostrado** que el arranque reprograme una aplicación rota ni que encienda `DD_ON*` solo. El MCU tiene cableado un puerto de descarga (MD0/INITX/UART P21-P22/SWD, `CN4906` no montado); sin vía de software | V / I / N | [E24-02](capture/e24-02-protocolo-actualizacion-darwin.md) |
| Material de recuperación (E24-03) | Respaldos íntegros (NVRAM, NAND lógica, BootROM, firmware 3.21) pero incompletos: faltan el arranque de Darwin, Loader2/3, vía de escritura de NAND, NVRAM post-3.22 y copia externa. El FDAT 3.23 lleva el `darwin_core` oficial y el tar oficial, y se reconstruye bit a bit; el guard solo acepta versiones mayores que la instalada, por lo que `camera_reflash_fw321.sh` ya no sirve. Solo la NVRAM tiene una restauración demostrada en hardware; reinstalar con Darwin defectuoso y restaurar sin `darwin_core` NO están demostrados (ausencia de evidencia, no imposibilidad) | E24-03 | V / I / N | [E24-03](capture/e24-03-auditoria-recuperacion-usb.md) |
| Dictamen de seguridad (E24-04) | **No hay evidencia suficiente para autorizar un nuevo flasheo persistente de Darwin** (límite de evidencia, no imposibilidad): ningún Darwin defectuoso se ha recuperado nunca ni existe vía independiente de la aplicación; el FDAT 3.23 es íntegro y reproducible pero su aceptación y su uso como recuperación no están demostrados. Matriz M1–M14 auditada (+M15–M17): FAIL M1 frente a 3.24, M9, M12, M14. De los diez escenarios, solo «mecánica rota con Darwin vivo» tiene ruta plausible; D–H (sin `Upd`, sin enlace, bucle de watchdog, sin `DD_ON*`, core incompleto) no. Una modificación persistente de LIRO tampoco es más segura; solo lo volátil (RAM) tiene recuperación demostrada. El watchdog de Darwin se arma con un byte de configuración (0 lo desarma) | E24-03 M14 («aceptar el riesgo»); «parche de Darwin tipo 0 = bajo riesgo» | V / I / N | [E24-04](capture/e24-04-dictamen-seguridad.md) |
| Ruta `Upd` y rearme (E24-05) | La cadena `InitCom → Upd → 0x45bc` está **trazada con bytes** (solo existe en `Seton`; evento 2 de `next` = 5; una orden desconocida o el estado 7 mandan a `On`); clausura conservadora C1 = 480 / C2 = 571 funciones (sin binario del arranque: no es garantía de recuperación). **`0x1fe66`→0 sí cambia la lista de la máquina exterior a `[0,7,8,9,10]`** y evita `0x1fe50/0x1fe86/0x1feb6` desde las APIs de cargar y los 49 estados; excepción: operación 5 (`0x1fcb8→0x1feb6`, freno sin compuerta). Hay cinco sitios de error 6. `pkt[+1]` llega a `0x20003a01` (copia); su valor EFCS no está medido. Control volátil NO demostrado (falta el emisor BIONZ del bloque 0 y solo existe en `Seton`); watchdog: estructura conocida, reloj y valores no | E23: «`0x1fe66`→0 no desactiva el rearme»; E24-04 X8/§5 | V / I / N | [E24-05](capture/e24-05-upd-y-rearme.md) |
| Captura BIONZ→Darwin y fin (E24-05a) | El mensaje que arranca la máquina de 49 estados es el **ID `0x0c`** (22 B): `On` → `0xce84` → tarea `0x1811a` → `0x17f8c` (admite si `pkt[0]=0` y `S+0x43=0`) → `0x1961c`, que elige entre **cinco listas** según `S+0x44.b0`, `S+0x32` y `S+0x3c`. Los estados 4 (primera toma), 5 (ráfaga) y 0x1f (todas) arrancan los rearmes; el 4 depende del predicado `0x196a2` (clase `pkt[+1]` × tipo de mecanismo fijado por orden BIONZ 1–4). `[0,7,8,9,10]` cumple las esperas internas de Darwin (`S+0x12c`, id terminal; el estado 9 baja el bit 24 de la máscara de ocupación, que además **bloquea** la admisión del siguiente paquete), pero no se ha localizado el lector BIONZ del fin (C = NO, D = NO, F = NO, G = NO). Dentro de la captura solo dos sitios llegan a la operación 5 (rechazo cat 2/`0x51`, tiempo de fase cat 2/`0x30`); `0x1989c` no está en la captura. Valor EFCS de `pkt[+1]` sin medir | E24-05 «B = NO» (resuelto) y «unión de 49 estados» (hay 5 listas) | V / I / N | [E24-05a](capture/e24-05a-captura-fin-bionz-darwin.md) |
| Consumidor BIONZ del fin (E24-05d) | BIONZ recibe de Darwin **ocho** mensajes mss (IDs `0x0b,0x0d,0x0e,0x10,0x11,0x14,0x15,0x17`; clase 3, subclases 0,2,3,5,6,9,10,12) por la tabla CAIF `0x43fe87f0`: receptor → buzón `[0x43e77284]` → `caif_recv` (`0x437db9f0`), que **bloquea sin plazo** (`-1`) y exige la subclase esperada; cada fase de captura (`0x438c24bc…0x438cc…`) espera su mensaje en orden. **Corrige E24-05a:** la máscara de ocupación y el anillo de eventos **no** viajan a BIONZ: el «bloque de estado» `0x6c78` es una instantánea del registro de fallos (única llamada `0x45b2`, entrada de excepción) y los lectores de la máscara son solo `0x6ca0/0x6ca8/0x17eba`. Falta el emisor Darwin de cada ID y si `[0,7,8,9,10]` los emite (F = NO) | E24-05a §4.4 (máscara + anillo en `0x0d/0x10/0x11`) | V / I / N | [E24-05d](capture/e24-05d-consumidor-estado-darwin-bionz.md) |
| Emisores mss de Darwin (E24-05f) | Los ocho mensajes salen de: admisión `0x17f8c` → op `0x16c64` (`0x0b`); estado de captura 9 (monodisparo) u 11 (ráfaga) → ops `0x16ca4/0x16cd8/0x16d2e` (`0x0d`, `0x15`); estado 31 → FSM `0x296f0` estado 5 → op `0x16e92` (`0x0e`, `0x10`); FSM de ajustes `0x294f8`→`0x29f64` (`0x11`, `0x14`, solo con modo 0–8); `0x125f6` (`0x17`, orden de cambio de modo). Las cinco listas de captura contienen 9 u 11 y el 31; el código emisor de `0x0b,0x0d,0x15,0x0e,0x10` **no** alcanza `0x1fe66`, el tipo de bobina ni primitivas de motor: orden idéntico en `[0,7,8,9,10]` y en las listas con rearme. **Corrige E24-05d (B):** la clase de ocupación (`S+0x43` ← máscara) sí viaja en el byte 0 del `0x0b`. Falta el disparo de `0x11/0x14/0x17` y el consumo del byte 0 en BIONZ | E24-05d §3 (la máscara no sale) | V / I / N | [E24-05f](capture/e24-05f-emisores-mss-darwin.md) |
| Ajustes, modo y ocupación (E24-05g) | `0x18a` son flags de las filas 22/23 de `0x29514` (no un evento). `0x11/0x14` los dispara el gancho `0x1c04c` (bloque 10 bit 3 de la trama `0x31` → `{2,0x18}` → fila 24 → `0x1aa28`) o el arrancador por disparo `0x17c26`→`0x1a3ec`; solo con modo 0–8. **Corrige E24-05f:** el `0x17` no es una orden de BIONZ: lo pide Darwin (estado 27 de la lista de `0x0e/0x10`, tras el `0x10`; modo 0, único que lo emite); los modos 1/2 salen de las esperas del estado 31 sin `0x17`. Byte 0 del `0x0b` en BIONZ (`0x438c2538`): clase 0 acepta, 1 reintenta ≤19, 2 error. Sin rearme se conservan los cinco mensajes y el `0x17` sin tocar compuerta/bobinas; la espera del estado 31 depende de P29 y puede escribir P4E (`0x2041e`→`0x20d00`) con `0x1fe66=0` | E24-05f §3/§7 (`0x17` «orden BIONZ») | V / I / N | [E24-05g](capture/e24-05g-ajustes-modo-ocupacion.md) |
| Dependencias finales (E24-05h) | La espera del estado 31 tiene **dos variantes** (corrige E24-05g): `S+0x32=0` (`0x18fa0`) sale solo con P29 bajo (`MSS_S2_REQ_CA`, IC6000→Darwin), sin plazo; `S+0x32≠0` (`0x18d6e`, observada en T022: `pkt[2..3]=0x1600`) sale por la FSM ADC-B (`0x29dc8`) temporizada. Con `0x20c74=0` no hay escritura estática a P4D/P4E en estado 31, modos 0/1/2 ni FSM ADC; P4C sí (=1 en cada toma). FAIL (bit 7 de `ctx+0x10`) = reintento sin avance, sin mensaje a BIONZ ni op 5; el estado 26 sondea hasta que llega un mensaje de BIONZ. El `0x0c` lo construye `0x438d0064` por envío (tipo 1–4 en `pkt[0xc]`, de `obj[0x1e0]`). No hay bloqueo real demostrado ni ausencia demostrada (A=NO,B=NO,C=SÍ,D=NO,E=NO,F=SÍ,G=NO,H=NO,I=SÍ) | E24-05g §2.3 (espera solo por P29), §5 FAIL pendiente | V / I / N | [E24-05h](capture/e24-05h-dependencias-finales-captura.md) |
| Terminación de ADC-B y P29 (E24-05h-3) | ADC-B (`0x29dc8`, terminal 7) **se inicia y termina con `0x20c74=0`**: la compuerta `0x19b9e` (`S+0x444` b4=0 ∧ `S+0x170` b0=0) no lee el tipo; lista `[1,4,6,7]`, sin FAIL/salto/lecturas de pin; única espera = evento 0 del canal 0 de `0x40023000` (plazo `S+0x14c` ticks, ≈ µs inferido); el estado 31 espera `0x203ae` **sin plazo** (3 bucles). Con tipo 0 solo desaparecen P4D/P4E, `0x16fe2` y `0x20c4a`. P29: tabla `0x2675c`→INT05; 7 grupos de pines (P29 salida GPIO en 0/1/5/6, entrada en 2/4, función INT05 en 3; sin pull); grupo activo en captura: ver E24-05h-4 | no hay bloqueo real demostrado | [E24-05h-3](capture/e24-05h-3-adcb-p29.md) |
| GPIO cortinillas | P4D/P4E no son serie (descartado estáticamente) | hipótesis serie | [fm3-gpio](capture/fm3-gpio-shutter-mapping.md) |
| ADC-A, grupo de P29 e IRQ de ADC-B (E24-05h-4) | ADC-A `[2,4,6,16,17]` (la ejecuta el estado 4 de ADC-B) **retorna sin bloquear**: con tipo 0 sin ciclos, pines ni esperas; cada estado de ADC-A necesita eventos de su temporizador base canal 11 (2 eventos hasta terminal). **Los estados 3 y 32 de la captura fallan (reintento sin plazo) si ADC-A y ADC-B no están ambos en terminal**; igual con tipo 0 y ≠ 0. Grupo de P29 en `On` = **3 (INT05, entrada sin pull)**; ningún FSM de captura cambia de grupo. Evento 0 de ADC-B: armado `0x94f6/0xf99a` → IRQ 32 → vector `0xf8d3` (tabla base `0x42fc`) → `0x1d04d` | no hay bloqueo de software demostrado; ausencia no demostrable sin medir (VTOR, prioridad NVIC, ISR canal 11) | [E24-05h-4](capture/e24-05h-4-adca-p29-irq.md) |
| Manejador LIRO `0x40e3` | **Existe en la A7S** (fila `0x43ff79e4` → `0x437a9cb1`); S401 lo buscó en la VA de la A6000 | S401 | [S402](capture/static-closure-2026-10-25.md) |
| Etiqueta `RecordStill::Execute` | `0x90b248` es RecordImage; no demostrada la antigua etiqueta | etiqueta histórica | [contrato](capture/recordstill-contract-audit-2026-10-23.md) |
| Llamadores de RecordImage | Falsos `0x7484dc`/`0x755af8` retirados; válidos `0x90de2e`/`0x91634e` | S382 inicial | [S382](capture/s382-recordstill-callers.md), [auditoría](auditoria-2026-10-23.md) |
| ID `0x40193` | No aparece como palabra en `.rodata/.data` pero sí como literal en `.text`; el negativo MOVW/MOVT era inválido | S384 inicial | [S384](capture/s384-queue-id-0x40193-search.md) |
| Sesgo `+0x58` | La entrada de S305 era interior `+0x58`; corregidas S303rev1/S304/S305 | S303rev1, S304, S305 | [S303](capture/s303-ref-tree-43ff3200.md), [S305](capture/s305-fun43858390-literal-pool.md) |
| Mapa de columnas | `0x43c9c5b5` es posición→columna (34); `0x4e`→12, `0x4f`→13 | «columna 1», S302/S321 | [S325](capture/s325-position-map.md), [S324](capture/s324-columns-audit.md) |
| Tablas T1/T2/T3 | Bases 4 B más bajas (T2 `0x43bbf2e8`, T3 `0x43bbef30`); sin tabla de tiempos por modo; huella silent en T2 (`0x3ff` vs 0) | S317, S326 | [S329](capture/s329-mode-timing-tables.md), [S331](capture/s331-consumer-signature.md) |
| `obj+0x2b4` | Flag de log; la fila la elige la posición del modo | S327, S330 | [S331](capture/s331-consumer-signature.md) |
| Alcance de T | Cinco consumidores leen campos de la fila (no solo `+0x14/+0x18`) | S329 | [S336](capture/s336-table-consumers.md) |
| `0x43fef404` | No es `u16[69]` de tiempos: tabla de ids del ODL | S329 | [S337](capture/s337-fef404-table.md), [S342](capture/s342-fef404-consumers.md) |
| Rolling / ElecShutter A6300 | Cadena `rolling` muerta; los 128 B de `0x43dcfa9e` sin referencias | S164, S135 | [S168](capture/s168-a6300-rolling.md), [S172](capture/s172-elec-shutter-a6300.md) |
| Validación S605–S627 | Siete gemelas falsas, 13 textos truncados, cinco longitudes; S625 = `[CAM_UTIL_SENS]: ` (17 B) | las 263 pruebas originales | [auditoría](capture/S605-S627_tabla_hallazgos.md) |
| S207 | No demuestra ausencia de un fin de integración (JSON/generador `NO_VERIFICADO`) | lectura inicial | [S207](capture/s207-imx235-end-of-integration.md) |
| Triaje S400 | 141 clasificaciones automáticas reabiertas; 86 filas resueltas, 0 pendientes | triaje automático | [triaje](../analysis/s400_open_questions_triage/README.md) |

## Política de ingeniería inversa: REA primero (vigente desde 2026-10-19)

Canónica para Codex y Claude Code; `AGENTS.md`/`CLAUDE.md` solo la resumen. No sustituye las restricciones activas.

1. **REA primero** para explorar lo nuevo: descubrir funciones, xrefs, llamadas directas/indirectas, grafos
   (`get_call_graph`), dependencias de valores (`trace_native_values`), decompilar (`batch_decompile`,
   `analyze_function`), constantes/estructuras (`search_bytes`, `xrefs`, `resolve_containing_procedure`),
   comparar funciones y recuperar evidencia previa. Hay que *usarlo*, no solo comprobar que está instalado.
2. **Ghidra histórico (`analysis/ghidra/silent-liro.gpr`, readOnly/noanalysis) después**, cuando: REA no
   reconoce una función conocida (p. ej. entradas Thumb sembradas a mano: 0x43789cc0, 0x43789708, 0x437da100,
   0x43792f9c, 0x43794096, 0x43ae90ce; REA cubre 363/464 entradas históricas), su análisis es incompleto o
   ambiguo, hay que verificar bytes/instrucciones ya recuperados, o seguir una investigación conocida es
   más barato que repetir búsquedas fallidas. Una consulta vacía de REA **no** prueba ausencia.
3. **Coste:** `av-cam.bin` cuesta ~8 min en frío y la sesión REA no persiste (rea#1048). Primero buscar
   evidencia ya exportada (`knowledge/`, `analysis/rea-independent/out/`). Si hay que abrirlo: comprobar
   si ya hay demonio (`analysis/rea-independent/run/rea.sock` + `.ready`, proceso `session_daemon.py`);
   si no, abrirlo **una vez** con `bin/session_daemon.py` y consultar por lotes con `bin/q.py`
   (el demonio fija `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`, `GHIDRA_MAXMEM=2G`, límite 2,6 GB y 1 h de
   inactividad); cerrar con `q.py SOCK --shutdown` al terminar el hito y comprobar que no quedan
   procesos. Bibliotecas ELF pequeñas (`libmprctrl.so`): MCP `rea` directo (~25 s). Evitar `list_procedures`
   masivo sin paginar. Detalle y parámetros: [rea-independent-milestone.md](capture/rea-independent-milestone.md).
4. **Rigor:** REA y Ghidra comparten motor: su acuerdo prueba configuración coherente, no independencia
   (el decodificador independiente es LLVM `llvm-objdump` + búsqueda de bytes propia). Verificar los
   hallazgos decisivos contra instrucciones y bytes reales; separar hecho, inferencia y NO_VERIFICADO.
5. **Intactos siempre:** firmware original, `silent-liro.*`, `analysis/ghidra`, informes S1–S48; comprobar con
   SHA-256 (`analysis/rea-independent/manifests/*.final.sha256`). REA trabaja en proyecto temporal
   `-readOnly -deleteProject`. Sin ejecutar firmware, sin flasheo (salvo autorización expresa del usuario
   para un caso concreto), sin pruebas físicas.
6. **Foco:** obturador completamente electrónico, en hitos grandes y autónomos; no ampliar infraestructura.
7. **MCP:** `rea` en Codex (`~/.codex/config.toml`, `[mcp_servers.rea]`) y en Claude Code (`.mcp.json` del directorio padre `../`, único punto de configuración MCP/permisos; sesiones siempre desde el padre;
   usa `scripts/rea`, requiere aprobación del usuario al abrir `claude`), junto a `sony-a6000-knowledge`.

## Restricciones activas

- No se ha ejecutado firmware en hardware real; no se ha flasheado ninguna cámara.
- **Git**: el usuario ha instruido explícitamente (21-10-2026) **subir cada hito terminado a
  `origin/main`**; sigue vigente la prohibición de subir firmware y de tocar la cámara. La prohibición
  de flashear solo se levanta con autorización expresa del usuario para un caso concreto (26-10-2026).
  Los hitos se commitean **por ruta** (nunca `git add -A`) y el repositorio se compacta con
  `git gc` (`gc.auto=512`).
- Ningún resultado estático se ha convertido en demostración física sin evidencia adicional explícita.
- EFCS/SilentShutter: hay opciones de software y transporte identificados; **no** hay control físico demostrado ni finalización electrónica de exposición confirmada.
- Todos estos hallazgos son **sobre el firmware**: la ausencia estática de un módulo, cadena o parámetro **no** demuestra incapacidad del hardware.

## Próximos pasos

Se mantienen en [PENDIENTES](PENDIENTES.md) (estáticos A, documentales B, entorno C, físicos D, respaldo E). Resumen operativo en
[CURRENT § Próximos pasos](../knowledge/CURRENT.md). Plan de pruebas físicas (diferido): [P1–P8](capture/physical-test-plan.md),
[P9–P12](capture/s402-physical-test-mapping.md), [P13–P21](capture/physical-test-plan-2.md).

## Cómo consultar el sistema de conocimiento

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py exact "0x..."        # dirección/símbolo
python3 scripts/knowledge/search.py text "concepto"       # búsqueda BM25
python3 scripts/knowledge/search.py tree --subsystem docs/capture
python3 scripts/knowledge/search.py claim docs/capture/<doc>.md   # qué lo corrige
```

Estado de implementación del propio sistema de conocimiento: [knowledge/PROGRESS.md](../knowledge/PROGRESS.md).
Auditoría de la lista de pendientes: [sincronización del 24-10-2026](capture/pending-sync-audit-2026-10-24.md).

## Dónde quedó el historial que antes vivía aquí

Todo en [history/STATE-historial-2026-10-26.md](history/STATE-historial-2026-10-26.md) (íntegro): avances S44–S47 (cadena de registros IMX210,
payload `0x43ed4620`, callback `0x437dad78`), S58 (productores numéricos y emulación IMX235), S140–S163 (mapa de registros IMX210, filas G, gates),
S138–S174 (línea de RE general y controles positivos A6300), S300–S348 (carril B) y los bloques por fecha del 23 al 25-10-2026. Sus informes
originales siguen en [docs/capture/](capture/); acceso por tema en [INDEX](INDEX.md).
