# Estado actual — léeme primero

Contexto operativo mínimo para agentes. Última revisión: **31-10-2026** (E26 R41: caminos estáticos restantes).
No es historial ni fuente de verdad de los pendientes: ver [Responsabilidades](#responsabilidades-documentales).
Versiones íntegras anteriores (nada se borró): [CURRENT-historial-2026-10-31](history/CURRENT-historial-2026-10-31.md)
(bloques E26 R5–R35 y E25 completos) y [CURRENT-historial-2026-10-26](history/CURRENT-historial-2026-10-26.md) (S59–S627).

## Estado global

| Aspecto | Estado | Fuente |
|---|---|---|
| **Cámara** | **No arranca** desde que se instaló el 3.25 integrado (actualizador al 100 % y Done; LED 3 lentos + 2 rápidos). Testimonio del usuario, sin captura UART ni lectura de NAND | [E26-RECOVERY](../docs/capture/e26-recovery.md) |
| **Prioridad** | Recuperar la cámara conservando calibraciones. Investigación **solo offline**; ningún acceso físico autorizado | [PENDIENTES § E26](../docs/PENDIENTES.md) |
| Objetivo de recuperación | Una sola partición, `nflasha3` (CRC releída por el actualizador = imagen 3.25); copia válida `dev_nflasha3.bin` (20-10-2026). Falta la vía de escritura | [R30](../docs/capture/e26-r30-updater-done-boundary.md) |
| Hito del obturador | **3.23 (Darwin tipo 0 + B1a, 2 bytes)** instalado en T040 (27-10-2026): el usuario confirmó que disparaba en silencio y sin error. Capturas de T042–T044 versionadas el 31-10-2026 | [E25](../docs/capture/e25-desactivacion-mecanica.md), [registro](../docs/capture/registro-pruebas-camara.md) |
| Firmware 3.25 | Selector EFCS/Electronic + C3-B + Darwin condicionado, construido y verificado **offline** (E25-24b…E25-29); es el que se instaló | [E25-27](../docs/capture/e25-27-construccion-firmware-integrado.md) |
| **Causa del fallo** | **Identificada offline (R36):** el `nflasha3` del 3.25 incumple el formato que lee Loader3 → ARM7 → LDEC (residuo 256 en 359/369 bloques que nunca llega al LDEC; bloques 0/48/57 de 1 registro de 64 KiB frente a 16 × 4096). El 3.23 solo cambiaba Darwin. Constructor corregido; falta confirmación UART | [R36](../docs/capture/e26-r36-causa-fallo-325.md) |
| Pregunta original (S51) | Exposición totalmente electrónica a resolución completa: A=NO, B=NO, C=NO en estático; superada en la práctica por el parche de Darwin (3.23), cuya exposición por filas tiene el límite medido de E25-10 | [S51](../docs/capture/s51-decision.md), [E25-10](../docs/capture/e25-10-exposicion-por-fila.md) |
| Cifras | 4 427 pruebas colectadas en local; CI (sin firmware): 918 pasan, 2 310 omitidas. Censo de etiquetas 133/372 (35,75 %, mide documentación). Sesiones S 291/627 y 74 informes de fase E. Planes físicos con prueba 12/24 (P1–P24). Registro T001–T053 (50 filas) | [estado.json](audit/estado.json), [tablero](https://nicolvus.github.io/a6000-fw-decomp/progress/) |

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
| R41 | Caminos estáticos restantes: `c01f379a` = consola serie de Loader3/Loader2 (`beast`, `ldump`), solo lectura y muda con `Backup[0x510015]=0` (corrige R13/R37 §4/R40 §6); espera `CFG:Wait ICE` por GPIO 14.17 antes del −302. Ninguna vía nueva sin acceso físico | [R41](../docs/capture/e26-r41-caminos-estaticos-restantes.md) |

**Conclusión operativa:** la vía serie del BootROM existe y se abre en cada arranque, pero exige la clave de `nflasha0`, que nunca se
volcó; todo lo restante es físico (`E26-FISICO-UPDATERMODE`, `E26-FISICO-BOOT`, `E26-R33-BLOQUE0`) y requiere autorización expresa. La
intervención mínima es crear `\updater\mode` en `nflasha2` (1 byte lógico, `updater_mode_entry.py`) e instalar el 3.26 por USB en menos
de 30 min con batería cargada (R37–R39); ese byte debe escribirse vía MuMin desde el BIONZ, no con lector externo (R39).

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

## Pendientes activos prioritarios (autoridad: PENDIENTES)

| ID | Estado | Qué falta |
|---|---|---|
| E26-R33-BLOQUE0 / E26-FISICO-BOOT | ABIERTO (físico) | Leer la clave de `nflasha0` (bloque 0, `0xc00`, 8 B) y continuidad Multi pin 9 ↔ `BOOT_SERIAL_IN`; exige lector NAND/JTAG y autorización |
| E26-FISICO-UPDATERMODE | ABIERTO (físico) | Crear `\updater\mode` (0 B) en `nflasha2` y, en la misma sesión, instalar `recuperacion-326` por USB |
| E26-R12-UART-FISICO / E26-R14-LED-MEDIDA | ABIERTO (físico) | UART0 solo útil para la vía serie del BootROM (logs apagados, R37); vídeo del LED para confirmar 0/3/2 |
| E26-R5-NAND / -BIONZ / -FM3 | ABIERTO | Geometría y ECC de `nflasha3`, acceso SWD de lectura, protocolo del FM3; especificar herramienta y preservación antes de escribir |
| E26-R30-HOSTRET0 | ABIERTO (baja) | Qué muestra el PC si `Execute` retorna 0 sin excepción |
| E1 | NO_VERIFICADO | Origen del local 4/2 a `ModelScalarPb`/`ModelPbCap` |
| E25-01 / E25-27 / E25-20 | ABIERTO / BLOQUEADO | Validación física del obturador (3.23 y 3.25) y C3-B en RAM; dependen de recuperar la cámara |
| E25-19f, E25-EFCS-1…4 | ABIERTO | Escritores de `cap+0x74f`, `+0x504`, `+0x740`, `+0x11b0`; funciones Thumb sin sembrar |
| R1 / R7 | PARCIAL / BLOQUEADO | Copia externa del respaldo; GitHub conserva commits antiguos en `refs/pull/*` y en un fork ajeno (R3/R6 cerrados: historial reescrito el 31-10-2026) |

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
[subproyecto](../projects/electronic-shutter/README.md) · archivos históricos en [docs/history/](../docs/history/) y [knowledge/history/](history/).
