# E24-03 — Auditoría de respaldos y del FDAT de recuperación 3.23 (27-10-2026)

Sesión 100 % offline: no se conectó la cámara, no se entró al modo actualizador, no se emitió ningún comando USB ni se instaló nada. Solo
se leyeron archivos locales. Parte de [E24-01](e24-01-arranque-recuperacion.md) (`2f29630f`) y [E24-02](e24-02-protocolo-actualizacion-darwin.md)
(`1ecfc0d2`). Estado de la cámara **supuesto** (no re-verificado hoy): fw 3.22 con `darwin_core` tipo 0 ([T024](registro-pruebas-camara.md)); no consta
ningún flasheo posterior (T025–T039 solo escribieron RAM).

## Respuestas

| | Pregunta | Respuesta | Qué significa |
|---|---|---|---|
| **A** | ¿Material de recuperación completo e íntegro? | **NO** | **Íntegro: sí** (hashes y descifrados correctos, §1–§2). **Completo: no**: faltan el arranque de Darwin (`0x0–0x41ff`), Loader2/3, un volcado de la flash de Darwin, una vía de escritura de NAND, una NVRAM posterior a 3.22, un script de reinstalación 3.23 y toda copia fuera de este disco (§8) |
| **B** | ¿El FDAT 3.23 contiene el Darwin original y supera las validaciones offline disponibles? | **SÍ** | `darwin_core.bin` = oficial 3.21 (`5f2be06d…`, CRC-32 `9ff7148c`), no el tipo 0 (`ca41b46c…`); el `firmware.tar` completo es byte a byte el oficial; modelo, región, CRC y cifrado correctos; se reconstruye bit a bit (§2–§3) |
| **C** | ¿Se ha demostrado que puede reinstalarse con la aplicación Darwin defectuosa? | **NO** | Ausencia de evidencia. No consta la inversa 3.22→3.23 en hardware, ni ningún caso con Darwin defectuoso. Lo único ejercitado: 3.21→3.22 con Darwin sano (T024) |
| **D** | ¿Procedimiento de restauración por software independiente de `darwin_core`? | **NO** | Ausencia de evidencia, no imposibilidad: depende del arranque de Darwin, que no se ha visto (E24-02). Evidencia en contra: el actualizador necesita `DD_ON*` y `InitCom`/`Upd` de `darwin_core` (E24-01/02) |

Ninguno de los NO es una imposibilidad técnica demostrada.

## 1. Inventario y verificación de respaldos (tareas 1 y 2)

Verificado con `sha256sum -c` sobre cada `SHA256SUMS` de `analysis/camera-dumps/` (32 carpetas) y con `tests/test_e24_03_recovery.py`.

| Componente | Respaldo local | Hash / integridad | Estado |
|---|---|---|---|
| NVRAM (BK4, 852 647 B, región `CX77500_E38`) | 11 `backup_flash.bin` / 10 distintos; copia buena `nvram-referencia-20261020-214913` (fw 3.21, cámara funcionando); último previo a T024: `20261026-232912-pre-T024-darwin-tipo0` | `bdf4e8a6…` (referencia); todas las sumas correctas; en la referencia `backup_flash` y `backup_mem` difieren en 6 B (estado de ejecución, no comprobado en las demás) | VERIFICADO |
| BootROM (24 KiB, `0xffff0000`) | 8 copias | idénticas, `81a17e03…` | VERIFICADO (es ROM: se lee, no se restaura) |
| NAND completa lógica (`/dev/nflasha*`) | `nand-20261020/` (`dev_nflasha.bin` 473 MiB + 14 particiones, incluida `nflasha1`) y `full-20261020-nand/` | `dev_nflasha.bin` `472514b9…`, `dev_nflasha1.bin` `ea74eb04…`; todas correctas | VERIFICADO el contenido; **no restaurable por software** (el shell de pmca hace `PUSH` de archivos, no de dispositivos) |
| Firmware original 3.21 | `.dmg` (`844349ff…`), `.dat` extraído (`29aef21a…`), `firmware.fdat` | El `.dat` descifra a un FDAT de SHA-256 `603b42ec…` = `firmware.fdat` extraído | VERIFICADO |
| Firmware de otros modelos | A7S 3.20 y A6300 2.01 (`.exe`) | Solo referencia; no sirven para recuperar esta cámara | — |
| FDAT de recuperación | `analysis/darwin-patch/fdat/recuperacion-323/` | §2 | VERIFICADO |
| Arranque de Darwin / Loader2/3 / flash de Darwin | **ninguno** | — | AUSENTE (§8) |

Anomalía menor (sin consecuencia): en `silent-nvram-20261020`, `silent-ram-20261020`, `silent-ram-control-20261020` y `silent-ram-cycles-20261020`
el `SHA256SUMS` se lista a sí mismo, así que `sha256sum -c` falla siempre en esa línea; el resto de líneas coincide. No indica corrupción.

Todo vive en un solo disco y fuera de git (`.gitignore`: `*.bin`, `firmware/`, `analysis/darwin-patch/fdat/`); solo se versionan README y `SHA256SUMS`.
Es el pendiente [R1](../PENDIENTES.md): un fallo del disco pierde NVRAM, NAND y FDAT. Los FDAT son regenerables (§3) solo si `firmware/` sigue ahí.

## 2. FDAT 3.23: integridad e identidad (tareas 2–4)

`analysis/darwin-patch/fdat/recuperacion-323/firmware_packed.dat` (212 988 056 B, `5f108901…`) y `firmware_packed.fdat` (212 155 392 B, `cfb65c8a…`).

| Comprobación | Resultado | Estado |
|---|---|---|
| Contenedor `.dat`: magia y CRC de `DEND` (`dat.readDat`); cifrado `CXD90014`; descriptor USB del actualizador `054c:03e2`; no es objetivo | Correcto | VERIFICADO |
| Descifrado bloque a bloque: suma de 16 bits y bandera de último bloque | Sin excepciones | VERIFICADO |
| Cabecera FDAT: magia `UDTRFIRM`, versión `0100`, CRC-32 de cabecera, modo `U`, LUW `N` | Correcto | VERIFICADO |
| Modelo / región / versión | `0x41030035` (ILCE-6000) / `0` / **3.23** (mayor 3, menor `0x23`); idéntico a oficial salvo la versión; igual modelo y región que el 3.22 que la cámara aceptó en T024 | VERIFICADO |
| `firmware.tar` interno (105 miembros) | SHA-256 `97024649…` = tar oficial 3.21 (212 011 520 B) | VERIFICADO |
| Partición de sistema de archivos del FDAT (`updater.img`, 143 360 B) | `b6d51752…` = oficial | VERIFICADO |
| `0640_darwin/darwin_core.bin` | 157 276 B, SHA-256 `5f2be06d…`, CRC-32 `9ff7148c`: **original**. El tipo 0 es `ca41b46c…` (CRC `0e2620b4`) | VERIFICADO |
| `0641_darwin_sum/darwin.sum` | `0,9ff7148c,0002665c,…,darwin_core.bin`: CRC-32 y tamaño coinciden con el core | VERIFICADO |
| `darwin_boo.bin`, loaders (`*_loader`) | No hay ninguno en el tar (solo `first_ssboot`, sin relación) | VERIFICADO |
| FDAT 3.22 (instalado) frente a 3.23 | Difieren solo en `darwin_core.bin` y `darwin.sum` (15 B + 8 B de CRC); ambos llevan la cadena `VER0.78` | VERIFICADO |

Límite: el descifrado y los CRC los comprueba el mismo `fwtool` que empaquetó el FDAT. La validación independiente es el updater de la cámara, que solo se ejerció con el 3.22 (misma tubería y estructura).

## 3. Reproducibilidad (tareas 2 y 3)

`fwtool pack` con `config-323.yaml` (el `config.yaml` oficial con `version: '3.23'`, única diferencia), `updater.img` y `firmware.tar` oficiales **reproduce
el `.dat` y el `.fdat` byte a byte** (prueba `test_recovery_323_rebuilds_byte_for_byte`). La entrada necesaria son `firmware/extracted/fw321/{firmware.tar,updater.img}`,
extraíbles del `.dat` oficial (`29aef21a…`) con `fwtool unpack`.

## 4. Requisitos del actualizador y fallos que impedirían instalar el 3.23 aun con BIONZ encendido (tareas 4, 5 y 7)

Camino de software: `pmca-console firmware -f firmware_packed.dat` → `init` + `checkGuard` (CMD `0x10`, comprueba el FDAT entero) → `switchMode` (reinicio y gestos en la
pantalla de la cámara) → de nuevo `init`/`checkGuard` en modo actualizador → `writeFirmware` → `complete`. `us_darwin_firm.sh` (hilo) reescribe Darwin al final.

| # | Fallo posible | Mecanismo | Estado |
|---|---|---|---|
| F1 | **Versión rechazada.** El guard solo acepta versiones **estrictamente mayores** que la instalada (medido con fw 3.21: 3.20 y 3.21 `Invalid version`; 3.22 y 9.99 aceptadas, [custom-fw-recovery](custom-fw-recovery-and-install.md)). Con 3.22 instalada, 3.23 debería pasar; **no se midió con 3.22** (exige conectar) | Cualquier FDAT posterior (p. ej. el 3.24 que propone [darwin-via-actualizacion](darwin-via-actualizacion-2026-10-26.md)) invalida el 3.23 y obliga a reempaquetar la recuperación como ≥3.25. Instalar 9.99 cerraría la vía | VERIFICADO la regla con 3.21; INFERENCIA para 3.22 |
| F2 | **El script documentado ya no sirve.** `scripts/camera_reflash_fw321.sh` instala el `.dat` oficial 3.21: dependería de una versión rechazada (3.21 < 3.22). `physical-test-plan.md` §«Recuperación probada» dice «no hay vuelta atrás por firmware»: superado por el 3.23 | La recuperación válida es el FDAT 3.23, que no tiene script con comprobación de hash | VERIFICADO (código y dato de guard) |
| F3 | **Modelo/región** distintos | Modelo `0x41030035`, región 0, igual que el 3.22 aceptado en T024 | VERIFICADO |
| F4 | **CRC** (cabecera, bloques, `DEND`, `darwin.sum`) | Todos correctos offline (§2) | VERIFICADO |
| F5 | **Batería y temperatura.** `libupdaterufp` rechaza con «battery NG» (script: batería > 50 %); la lectura probablemente viene de Darwin | Hay que cargar y comprobar antes; el umbral exacto no se extrajo | VERIFICADO la existencia; INFERENCIA el origen |
| F6 | **Entrar al actualizador.** Solo hay entrada por software desde el sistema principal (pmca → `up.sh user` → reinicio, E24-01). Un sistema principal que no arranca (`nflasha3/5/7` dañadas, `upm.ko`, `usb_extcmd`) cierra esta vía | El actualizador (`nflasha1`) está íntegro en el volcado; otras entradas del BootROM/loader sin disparador conocido | VERIFICADO el camino; NO_VERIFICADO las alternativas |
| F7 | **Estado 4 de Darwin.** `ud_darwin_init` envía `0x11` con estado 4 en cada arranque del actualizador; `ud_darwin_firmup` necesita `InitCom`/`Upd` de `darwin_core` y el arranque de Darwin (`0x14/0x15`). Si Darwin no responde: «NG», LED `0x63` | Si ese NG aborta también las particiones principales no consta: es un `proc` con `thread="yes"` en `config.xml` y la gestión del fallo está en `libupdaterbody.so` | NO_VERIFICADO |
| F8 | **El core podría no reescribirse.** `ud_darwin_firmup` omite el core solo si boo y core coinciden con la versión del dispositivo. Sin `darwin_boo.bin` la versión del boo vale 0 y el core se **reescribe siempre** (bytes `0x8f8e`, `0x9080–0x9092`, test). El tipo 0 y el original llevan la misma cadena `VER0.78` y T024 sí cambió el comportamiento | El 3.23 no trae `darwin_boo.bin` | VERIFICADO (código + efecto de T024) |
| F9 | **`/setting/updater/uincomp`** presente → error 54 y salida sin USB | Quién lo crea es NO_VERIFICADO | VERIFICADO el bloqueo |
| F10 | **Interrupción** (corte, cable) en la ventana de escritura de Darwin o de `nflasha3/5/7` | Sin escritura atómica demostrada | INFERENCIA |
| F11 | **Host:** `pmca-console` carga en `~/.local/share/pmca-venv`; el `.dat` 3.23 solo existe en local | Regenerable (§3) | VERIFICADO el arranque de la herramienta; la comunicación USB no se ejerce |
| F12 | La NVRAM de 3.21 sobre una cámara 3.22: nada la comprueba (`senser_backup_restore.py` valida tamaño y región) | Ninguna NVRAM posterior a 3.22 | NO_VERIFICADO |

## 5. Tres recuperaciones distintas (tarea 6)

| | NVRAM | Firmware principal | Aplicación Darwin |
|---|---|---|---|
| Qué cubre | Ajustes y calibración guardados (BK4) | `nflasha3/5/7/15/16` (+ `nflasha1` solo si el paquete trae loader: el 3.21 no) | `darwin_core.bin` en la flash del MCU, no el arranque `0x0–0x41ff` |
| Herramienta | Service mode (`senser_backup_restore.py`, `setBackupPresetData` + `saveBackup`) | `pmca-console firmware` con FDAT mayor que el instalado | Mismo FDAT: `ud_darwin_firmup` (0x14/0x15) |
| Necesita | BIONZ y Android arrancados con el shell de servicio | Sistema principal vivo para entrar; guard; batería | `darwin_core` con `DD_ON*`, `InitCom` y `Upd` operativos; arranque de Darwin |
| ¿Depende de `darwin_core`? | Sí, para que el cuerpo encienda; no del mecanismo | Sí (energía y estado 4); no de bobinas/cortinas | Sí, es el objeto restaurado: un core inservible puede cerrar la vía (E24-02 §4) |
| ¿Incluida en el FDAT 3.23? | No | Sí (tar oficial) | Sí (core original) |
| ¿Demostrada en hardware? | **Sí** (§6) | No (solo avance 3.21→3.22) | No (solo original→tipo 0) |

El FDAT 3.23 junta las dos últimas: reinstala el core original **solo si** el actualizador alcanza a Darwin. No hay un camino de software que restaure el firmware principal sin pasar por el actualizador, ni uno que restaure Darwin sin su arranque.

## 6. Restauraciones demostradas en hardware (tarea 9)

| Componente | ¿Restauración efectiva demostrada? | Evidencia y límite |
|---|---|---|
| NVRAM | **Sí, un caso** | 20-10-2026: tras ajustes reiniciados a fábrica se escribió la copia A; la cámara enciende y apaga bien según el usuario. [S65](s65-nvram-incident-diff.md): 215 de 237 propiedades vuelven; 7 no se restauran (R=F); causa no aislada. Una segunda restauración (`liveview-silent-capture-via-cameraex.md`) sin re-volcado ni verificación del efecto |
| Firmware principal | **No** | Solo avance con partición idéntica (T024, 3.21→3.22). Ninguna restauración de un firmware dañado |
| Aplicación Darwin | **No** | Solo original → tipo 0 con aplicación sana. La inversa (3.22→3.23) preparada y nunca ejecutada |
| Arranque de Darwin | **No** | Sin binario, sin acceso |
| NAND / `nflasha1` / loaders | **No** | Volcado de solo lectura; sin vía de escritura de dispositivos |
| BootROM | No aplica | ROM |
| Estado volátil (T029, T037) | Sí, **sin flasheo** | Cámara colgada recuperada con apagado completo: demuestra recuperación de RAM, no de flash |

## 7. Qué cambia en la documentación previa (tarea 7)

- `scripts/camera_reflash_fw321.sh` y [custom-fw-recovery](custom-fw-recovery-and-install.md) §«Cómo volver atrás» 2: el 3.21 oficial es válido solo si la versión instalada es menor; con 3.22 instalada rige el FDAT 3.23.
- `physical-test-plan.md` línea 12 («no hay vuelta atrás por firmware») queda superada: hay FDAT de recuperación (no probado en hardware).
- [E24-02](e24-02-protocolo-actualizacion-darwin.md) §5, fila 1: «Necesita FDAT versión mayor que la instalada (recuperación 3.23 preparada)»: confirmado offline; sigue sin medirse el guard con 3.22.

## 8. Material y herramientas que faltan (tarea 8)

| Falta | Efecto | Cómo obtenerlo |
|---|---|---|
| `darwin_boo.bin` (`0x0–0x41ff`) y volcado de la flash de Darwin | No se sabe si el arranque recupera una aplicación rota ni si valida la imagen | Solo hardware (SWD/serie, sin autorizar). **Límite del dictamen** |
| Loader2/3 y región física previa a `nflasha1` | Quién lee `/setting/updater/mode*` y qué hace el BootROM sin NAND válida | Solo hardware |
| Vía de escritura de NAND (`/dev/nflasha*`) | El volcado no restaura | No existe en el shell de pmca |
| NVRAM posterior a 3.22 | Restaurar una NVRAM de 3.21 sobre 3.22 no está probado | Un backup antes de la siguiente prueba (usuario) |
| Medida del guard con 3.22 instalada | F1 sigue siendo inferencia | `fdat_guard_probe.py` (solo chequeo; exige conectar: E24-04 con permiso) |
| Script de reinstalación 3.23 con comprobación de hash | Hoy se llamaría a mano | Crear junto a E24-04 |
| Copia externa de NVRAM, NAND, `firmware/` y FDAT (R1) | Un fallo de disco lo pierde todo | Decisión del usuario |
| Flash Programming Manual del FM3, herramienta SWD/UART | Vía de hardware no evaluable | Fuera de alcance |

## 9. Matriz de condiciones que debe comprobar E24-04 antes de aprobar un flasheo (tarea 10)

Todas deben cumplirse; las marcadas **[conectar]** exigen la cámara y quedan fuera de esta sesión.

| # | Condición | Cómo comprobarla | Hoy |
|---|---|---|---|
| M1 | Versión del FDAT de recuperación **estrictamente mayor** que la del FDAT de prueba y que la instalada | Comparar versiones y reempaquetar con `fwtool pack` (§3); nunca 9.99 | 3.23 > 3.22; **falla** si la prueba es 3.24 |
| M2 | Guard medido con la versión instalada **[conectar]** | `scripts/fdat_guard_probe.py` (solo chequeo) con 3.23 | NO medido |
| M3 | FDAT de recuperación íntegro y reproducible | `pytest tests/test_e24_03_recovery.py` | Pasa |
| M4 | Core de recuperación = original y `darwin.sum` coincide | Misma prueba | Pasa |
| M5 | FDAT de prueba difiere del oficial solo en lo previsto | Comparar miembros del tar (como `test_type0_fdat_differs_only_in_darwin`) | Por hacer por parche |
| M6 | El parche no toca `0x45c8/0x43fc`, `0x4638`, `0x51c0`, tabla `0x28c6c` y manejadores, `0xece4`, `InitCom 0x4bca`, `Upd 0x8da8`, `0x45bc`, watchdog `0xa500/0xa524`, CRC `0xa1dc` | Diff byte a byte del core contra el original | Por hacer por parche |
| M7 | El parche conserva `VERM.mm` en el core | `b"VER0.78"` presente | Pasa para el tipo 0 |
| M8 | El paquete sigue sin `darwin_boo.bin` | Prueba de M4 | Pasa |
| M9 | NVRAM íntegra y reciente, con firmware instalado conocido **[conectar]** | `senser_backup_dump.py` + `sha256sum -c` | La última es de 3.21 |
| M10 | Estado de la cámara re-verificado **[conectar]** | `pmca info`: modelo, versión, batería | Supuesto 3.22 |
| M11 | Batería > 50 %, cable directo, PC sin suspensión | Operador | — |
| M12 | Un disco extra con copia de NVRAM, NAND, FDAT y `firmware/` (R1) | Decisión del usuario | NO hecho |
| M13 | Autorización expresa del usuario para ese flasheo concreto | Chat | — |
| M14 | La recuperación solo se declara válida si el usuario acepta el riesgo residual: C y D = NO (§Respuestas) | Registro en el informe de E24-04 | — |

## Límites

El arranque de Darwin (`0x0000–0x41ff`) no está disponible: de él dependen C y D, y se cierran como límite, sin buscarlo. Cada afirmación sobre la cámara se apoya en archivos locales; la
versión instalada, la batería y el guard con 3.22 no se re-verificaron. El descifrado y los CRC del FDAT los comprueba el mismo `fwtool` que lo generó. Pruebas: `python -m pytest -q tests/test_e24_03_recovery.py` (8 pruebas, ~20 s; se omiten si faltan binarios; requiere `pycryptodomex`, `capstone`, `mtools` y `7z`).

| Archivo | SHA-256 |
|---|---|
| `recuperacion-323/firmware_packed.dat` | `5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf` |
| `recuperacion-323/firmware_packed.fdat` | `cfb65c8aad8ac8a3ccb1c4c758d485feee1ebf2e83e503d9c62d59fb96b01ce4` |
| `fw321/firmware.tar` (= tar interno del 3.23) | `970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8` |
| `fw321/updater.img` | `b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c` |
| `darwin_core.bin` oficial 3.21 (= el del 3.23) | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` |
| `darwin_core_tipo0.bin` (3.22 instalado) | `ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc` |
| `fw321/firmware.fdat` = FDAT del `.dat` oficial | `603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90` |
| `Update_ILCE6000V321.dmg` | `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e` |
| `FirmwareData_ILCE6000V321.dat` | `29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f` |
| `nvram-referencia-…/backup_flash.bin` | `bdf4e8a6d9721f26b466ce86c726623d8c7806d57140c4943a9a829efa5eef32` |
| `bootrom.bin` | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `nand-20261020/dev_nflasha.bin` / `dev_nflasha1.bin` | `472514b9468b3d5cdbd2a8a78c2804a6e7bc2f7371525677e2572afaffacdfbf` / `ea74eb046a6c3ae2cc2e2b5e5fb09a7ce9666e75890d21362a89e7f5c95301fb` |
