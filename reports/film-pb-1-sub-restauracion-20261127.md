# FILM-PB-1 — Restauración: qué discrimina «CFW» frente a «cámara/tarjeta» (27-11-2026)

Estado: **plan cerrado y verificado íntegramente offline**; no se ha ejecutado nada contra la cámara (sin red,
sin USB, sin `adb`, sin flasheo). Continúa [la auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md): descartado
el parche de código, quedan H1 (arranque en frío sin `nflasha5`/WBI) y H2 (contenido/catálogo). Evidencia y arnés
reproducible: [evidence/film-pb-1-sub-20261127](evidence/film-pb-1-sub-20261127/). Las VA citadas (`0x437BC0`,
`0x437C0A`…) son VA del ELF de los informes de origen; esta sesión no desensambla nada nuevo.

## 1. DAT oficial 3.21 — VERIFICADO

| Comprobación (comando) | Resultado |
|---|---|
| `stat -c %s …/FirmwareData_ILCE6000V321.dat` | **212 988 056 B** |
| `sha256sum` del mismo | `29aef21a…8892f`, igual al que exige `scripts/camera_reflash_fw321.sh:8` |
| Contenedor (`e25_06.parse_dat`) | `DATV 16/4 · PROV 28/4 · UDID 40/92 · FDAT 140/212987904 · DEND 212988052/4`; 0 B tras DEND; CRC de DEND OK |
| FDAT (`e25_06.decrypt_fdat`, 207 996 bloques) | 0 sumas/banderas/longitudes malas; descifra **byte a byte igual** a `fw321/firmware.fdat` (sha `603b42ec…`, 212 155 392 B) |
| Cabecera FDAT (`parse_fdat_header`) | `UDTRFIRM`, CRC `92a94bb3` OK, versión **3.21**, modelo `0x41030035`, región 0, tar en +143 872 / 212 011 520 B |
| `updater.img` (fs `U`, 143 360 B) | sha `b6d51752…` = `e25_06.UPDATER_SHA` = `build.UPDATER_SHA256` |
| Tar (`e25_06.parse_tar`) | sha `97024649…` = `fw321/firmware.tar` = `e25_06.OFFICIAL_TAR_SHA`; 105 miembros, 0 problemas, 2 bloques nulos |
| Sumas del tar (`verify_all_sums`) | 7 ficheros `.sum`, **80 líneas, 0 errores** |
| **`nflasha5` presente** | sí: 42 293 120 B, sha `fe080cda…4f04`; línea `0,9cb10112,02855780,…,dev/nflasha5` en `part_image.sum` |
| `nflasha3` (ruta LDEC) | 369 bloques, 11 489 040 B, `hardware_violations` = **[]** (residuo 0, 16×4096): no repite el defecto del 3.25 |
| pmca-console + venv | `~/.local/share/pmca-venv/bin/python` 3.14.10; `pmca-console.py --help` rc 0; `firmware -f DATFILE` existe; `readDat` envía **offset 140, 212 987 904 B**; sin driver nativo cae a `libusb` (pyusb 1.3.1 + `libusb-1.0.so.0`), no hace falta `-d` |
| Script | `bash -n` OK; `sha256sum -c` (línea 10) **antes** de `lsusb` (11) y de la confirmación `SI` (13); `lsusb` y `systemd-inhibit` disponibles |

## 2. `build/sony_puro_sin_wbi_404` — AUDITADO

Contenido: `config-404.yaml`, `container.json`, `firmware.tar` (169 717 760 B), `package-4.04/{firmware_packed.dat, .fdat, SHA256SUMS}`; no hay `MANIFEST.json`.

| Comprobación | Resultado |
|---|---|
| DAT vs `SHA256SUMS` | `9c7b4f46…0872` coincide (fichero y manifiesto), y con `container.json` |
| Contenedor | misma forma que Sony; **`UDID` idéntico byte a byte**; CRC de DEND OK; 0 B tras DEND |
| FDAT | 170 528 768 B = 166 532 × 1024; 0 bloques malos; descifra igual a `firmware_packed.fdat` (`e761574c…`, = `SHA256SUMS`) |
| Cabecera | versión **4.04** (> base 3.21), CRC `016d023c` OK, modelo/región iguales a Sony, tar +143 872 / 169 717 760 B |
| `updater.img` | sha `b6d51752…` = el oficial 3.21 |
| Tar | sha `1f73e141…` = `container.json` = `firmware.tar` del build; 104 miembros, 0 problemas |
| **Diferencia con 3.21** | **solo** se quita `0700_part_image/dev/nflasha5` y su línea de `part_image.sum`; de los 104 miembros comunes, **103 son idénticos byte a byte** (modo/uid/gid incluidos) y el único distinto es `part_image.sum`, por esa línea |
| Sumas | 79 líneas, 0 errores; `part_image.sum` conserva `0,df198ecd,050264e1,…,dev/nflasha15` |
| `nflasha15` | sha `e3530a89…71f4` = **la de Sony**; 2373 bloques, contiguo, máx. 129 sectores, residuo 0, 84 042 977 B ≤ 100 MiB |
| `audit_package_nflasha15.py` en lectura | **no aplicable a este build**: aborta con `FileNotFoundError: …/package-4.04/MANIFEST.json` ([stderr](evidence/film-pb-1-sub-20261127/audit-script-404.stderr.txt)) y su semántica exige `nflasha15`+`part_image.sum` modificados |
| Auditoría equivalente (mismo código) | su lista de comprobaciones reejecutada con las mismas funciones de `e25_06`/`e25_27`: [arnés](evidence/film-pb-1-sub-20261127/film-pb-1-sub-check.py), [JSON](evidence/film-pb-1-sub-20261127/verificacion-dat-321-y-404.json) |

Veredicto: **DAT coherente** (versión 4.04 > 3.21, sumas y CRC OK, contenedor/UDID/updater idénticos a Sony,
particiones con el layout de Sony) y su `/usr` es exactamente el de fábrica; lo único que cambia es la ausencia
del WBI. Es un control, **no** una restauración.

## 3. Procedimiento de decisión

**P0 — 20 min, riesgo 0, sin flashear.** (1) Anotar versión que reporta la cámara (Menú → Configuración → Versión)
y batería. (2) Reproducir MAH04198 de la tarjeta de siempre: miniatura, contador, aviso, caution `0x135`.
(3) «Recuperar BD imág.» y reintentar. (4) Copiar el clip a una tarjeta formateada en la propia cámara y
reproducirlo. Si reproduce con la tarjeta nueva y no con la vieja ⇒ **tarjeta/catálogo (H2)**, no hay que
flashear; si falla en ambas ⇒ pasar a P1.

**P1 — Condiciones y criterios de aborto** (cualquier flasheo).

| Criterio | Regla | Si no se cumple |
|---|---|---|
| Batería | ≥ 50 % y 3 barras; fuente de alimentación si hay | abortar: el updater devuelve «Low battery»/«AC adapter required» |
| Cable | directo al PC, sin hub, puerto trasero, cable de datos conocido | cambiar cable/puerto y repetir `lsusb` |
| PC | `systemd-inhibit --what=idle:sleep --mode=block` activo, portátil enchufado, sin updates ni ahorro | abortar |
| Hash | `sha256sum -c` del script (línea 10) = OK | abortar |
| Visibilidad | `lsusb` con VID `054c`, cámara en **MTP**, PlayMemories/Imaging Edge cerrados | abortar |
| Tarjeta | si `checkGuard` responde «Memory card inserted»/«Disk inserted», sacarla | reintentar |
| Versión | pmca imprime «Updating from version A to B» (`commands/usb.py:390-393`); si **B<A** es un descenso (3.21 sobre 3.93/4.02) | decisión consciente; `Invalid version` ⇒ rechazo sin escribir |
| Antes de «Writing firmware» (`usb.py:419`) | cualquier duda: Ctrl-C y desconectar | no se ha escrito nada |

**P2 — E3, 3.21 oficial (una sola escritura).**
`systemd-inhibit --what=idle:sleep --mode=block sh scripts/camera_reflash_fw321.sh` — nunca desconectar.
Secuencia esperada en el PC: `Initializing firmware update` → `Updating from version A to B` → `Switching to
updater mode` → `Please follow the instructions on the camera screen` → `Writing firmware` → `Done`; en la
cámara, pantalla de actualización con progreso y «Done». Si el proceso muere: **no** retirar el cable, esperar
el resultado en pantalla y, si sigue en modo actualizador, repetir el mismo comando (el actualizador de fábrica
de `nflasha1` acepta otra pasada; precedente: 3.26 cortado al 45 % y reintentado con éxito).

**P3 — Al terminar.** Cámara: **Versión = 3.21** y sin menús del CFW (Silent/PP desaparecen). PC:
`pmca-console.py info` en MTP debe listar `Firmware version: 3.21` (`commands/usb.py:250-256`). Si no es 3.21, el flasheo no
completó: reintentar antes de juzgar nada.

**P4 — Prueba de reproducción** (misma tarjeta, mismo clip, dos arranques). (1) Tarjeta de siempre con
MAH04198 (9,5095 s / 285 cuadros). (2) Play y registrar: ¿reproduce con audio?, contador (`0:09` o `0:02`),
miniatura, «No se puede visualizar.», caution `0x135`. (3) Apagar/encender y repetir.

| Resultado | Conclusión |
|---|---|
| Reproduce en 3.21 (los dos arranques) | **el CFW era la causa**; con el código descartado, el factor es el arranque en frío sin `nflasha5`/WBI. FILM-PB-1 se cierra como causa de entorno; el arreglo real (paquete que conserve `nflasha5`) exige build y auditoría nuevos, fuera de este plan |
| Sigue fallando en 3.21 | **cámara/tarjeta**: contenido/catálogo (H2) o cadena DMM/decoder (G111 §14.2); siguiente paso, tarjeta nueva + «Recuperar BD imág.» y captura de `dmm_units`/`dmm_log` |
| Reproduce solo en el segundo arranque | el primer arranque tras el flasheo no es comparable: quedarse con el estado estacionario del punto 3 |
| 3.21 reproduce y 4.04 no | queda probado que el discriminante es el **modo de arranque**, no el contenido de `/usr` |

## 4. Riesgo de cada vía y recomendación

- **Vía A — 3.21 oficial.** Riesgo de construcción ≈ 0 (DAT de Sony verificado: mismo `updater.img`, `nflasha3`
  compatible con LDEC, 80 sumas OK). Riesgos reales: (i) **rechazo por versión** al bajar de 3.93/4.02 a 3.21,
  que ocurre en `checkGuard` (`usb.py:390`) **antes** de escribir y no deja daño; (ii) **corte** de corriente/USB durante
  «Writing firmware», único escenario con daño y recuperable reintentando (precedente 3.26); (iii) se **pierde el
  CFW** instalado, reversible porque los `.dat` de `build/` siguen auditados y se reinstalan por la misma vía.
  No toca la tarjeta ni los datos.
- **Vía B — `build/sony_puro_sin_wbi_404`.** Contenido idéntico a Sony salvo `nflasha5`, pero el contenedor es de
  **construcción propia** (riesgo añadido: nuestra cadena, no la de Sony) y, sobre todo, **no restaura el WBI**:
  si H1 es cierta, seguirá fallando. Sirve para separar «arranque» de «`/usr`», no como arreglo, y exige un
  segundo flasheo.
- **Recomendación: P0 primero** (Recuperar BD imág. + tarjeta recién formateada: 20 min, riesgo 0, puede cerrar
  H2 sin flashear) y **después la Vía A**: una sola escritura devuelve el estado de fábrica completo, incluido
  `nflasha5`, y su resultado decide FILM-PB-1 en un paso. La Vía B solo si 3.21 se rechaza por versión o si,
  reproduciendo 3.21, se quiere aislar el modo de arranque.

## 5. NO_VERIFICADO

- **Versión actual de la cámara**: los informes discrepan (`cfw_func393/pp` = 3.93 en la auditoría del 27-11
  frente a «4.02 instalada» de G111 §14). Se resuelve en P0.1; con 4.02 o 3.93, 3.21 es un descenso.
- **Que el updater acepte un descenso**: sin precedente local; el guard compara con `\updater\dat4`
  (`docs/STATE.md:61`, R38) y pmca solo documenta `STAT_INVALID_VERSION` (`usb/sony.py:553`).
- **Que la cámara exija sacar la tarjeta**: `STAT_DISK_INSERTED`/`STAT_MS_INSERTED` existen en
  `references/pmca/pmca/usb/sony.py:541-554`, pero no consta cuándo los devuelve.
- **Que la restauración cure el síntoma**: es justo lo que E3 pone a prueba; nada offline lo demuestra.
- No se ha ejecutado firmware, ni scripts de flasheo, ni escrito fuera de `reports/`.
