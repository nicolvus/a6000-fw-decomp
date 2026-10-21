# Firmware propio: cómo volver atrás y cómo instalar uno nuevo

Fecha: 2026-10-20. Cámara ILCE-6000 fw 3.21 (CXD90014). Solo estático y lecturas; no se ha flasheado nada en esta fase.

## Qué se verificó

| Hecho | Evidencia | Estado |
|---|---|---|
| El FDAT de CXD90014 está cifrado, no firmado: `DoubleAesCrypter` con claves públicas de `fwtool/sony/constants.py` | 4000 bloques del `.dat` oficial 3.21 descifrados (checksum de bloque válido) y re-cifrados: 4000/4000 idénticos byte a byte (`blkrt.py`, scratchpad) | VERIFICADO (primeros 4 MB; el archivo completo no se pudo recorrer: el reempaquetado en Python puro superó 50 min y se abortó) |
| El guard del updater es CRC + modelo + región + versión, no firma | `docs/capture/s62-pmca-injection.md` §2.5; FDAT mínimo de pmca (v9.99, modelo `0x41030035`, región 0) aceptado por esta cámara en sesiones previas | VERIFICADO documental + uso previo |
| Misma versión se rechaza (`Invalid version`) | Intento de reflash 3.21 sobre 3.21 en esta sesión, antes de escribir nada | VERIFICADO |
| Qué particiones escribe una actualización oficial: `nflasha3` (Main), `5` (warm boot), `7` (rootfs), `15` (/usr), `16` (Android system) + plantillas de NVRAM `0110_backup` + `partinf.conf`/`mount.conf` | `firmware.tar_unpacked/0701_part_image_sum`, `0300_partconf/partinf.conf`, `0100_config/mount.conf` | VERIFICADO (contenido del paquete) |
| NO incluye `nflasha1` (Updater, 6 MB), `2` (Setting), `4` (MPR Flash Backup), `6` (Jiritsu), `10/11` (Work/Log), `17/18/23` | mismos ficheros | VERIFICADO (el paquete); que el updater real no toque más allá del paquete: NO VERIFICADO |
| Los `.sum` son `tipo,crc32,tamaño,modo,...,ruta`; el CRC-32 de `nflasha7` coincide (`b969856d`, `0x32ba4f` B) | cálculo local con `zlib.crc32` | VERIFICADO |
| El paquete trae NVRAM de fábrica por región (`CX77500_E38.bin`, 852 647 B) | `0110_backup/.../DM_UUD3/` | VERIFICADO |

## Cómo volver atrás (de menos a más invasivo)

1. **Ajustes/NVRAM corruptos** (el caso del 2026-10-20): service mode + `scripts/senser_backup_restore.py FILE SHA256` con la copia buena `analysis/camera-dumps/nvram-referencia-20261020-214913/backup_flash.bin`. Probado en hardware: la cámara volvió a encender/apagar bien.
2. **Firmware propio defectuoso pero la cámara aún entra en modo actualizador**: reinstalar el `.dat` oficial 3.21 con `scripts/camera_reflash_fw321.sh` (pmca `firmware`). Obstáculo: el guard rechaza la misma versión. Para poder volver, el FDAT propio debe llevar una versión **distinta de la oficial** y el de recuperación una **aceptada por el guard** (p. ej. reempaquetar el oficial con versión 9.99 como hace pmca, o mayor que la instalada). Guard medido en esta cámara (fw 3.21, `scripts/fdat_guard_probe.py`, solo chequeo, sin escribir): 3.20 RECHAZADA, 3.21 RECHAZADA, 3.22 ACEPTADA, 9.99 ACEPTADA (`Invalid version` en las rechazadas) ⇒ solo acepta versiones **estrictamente mayores** que la instalada: no se puede volver al oficial 3.21 desde una versión propia ≥3.22 sin reempaquetar el oficial con una versión mayor (p. ej. 9.99). VERIFICADO.
3. **No arranca ni la app**: depende de que `nflasha1` (Updater) siga intacto, que no está en el paquete, y de poder entrar en modo actualizador (botón/USB). NO VERIFICADO en hardware. No existe en el repo un volcado completo de la NAND (`updater_full_dump.py` está escrito, nunca ejecutado: no hay `analysis/camera-dumps/full-*`).
4. **Sin modo actualizador**: no hay vía demostrada (JTAG/NAND externa no investigados; ver `docs/boot-and-recovery.md`).

## Cómo instalar un firmware propio

1. Partir del `.dat` oficial: `fwtool.sony.dat.readDat` → `fdat.decryptFdat` → `fdat.readFdat` (modelo `0x41030035`, región 0, 2 file systems).
2. Modificar las particiones dentro de `firmware.tar` (`nflasha3/5/7/15/16`); recalcular CRC-32 y tamaño en los `.sum` (`0701_part_image_sum`, etc.) y la cadena de sumas del tar.
3. `fdat.writeFdat(FdatFile(..., version=X))` (recalcula el CRC de cabecera) → `fdat.encryptFdat(..., 'CXD90014')` → `dat.writeDat` (CRC de DEND).
4. Instalar con `pmca-console firmware -f NUEVO.dat` (batería >50 %, cable directo). La versión X debe pasar el guard (≠ instalada).

Límites y riesgos:
- Pasos 2–3 no se han ejecutado de extremo a extremo: no hay prueba de que la cámara acepte una `nflasha*` modificada (el updater podría validar más allá del `.sum`; NO VERIFICADO).
- Una imagen mala en `nflasha3/5/7` puede dejar sin arrancar el sistema principal; la recuperación (punto 3 arriba) depende de `nflasha1`.
- El reempaquetado completo en Python puro es muy lento (>50 min para 212 MB); conviene un script con archivos temporales y `numpy`/`Cryptodome` en bloque.

## Antes de cualquier flasheo (pendiente de hacer)

- `scripts/updater_full_dump.py` (solo lectura) para guardar la NAND y las particiones 1–7, 10, 11, 15–18, 23.
- (hecho) `scripts/fdat_guard_probe.py`: resultado arriba.
- (hecho) Volcado de NAND con `scripts/updater_nand_dump.py` → `analysis/camera-dumps/nand-20261020` (916 MB, solo hashes versionados): NAND entera (`nflasha`, 473 MiB) y 20 particiones. `nflasha3/5/7/15/16` empiezan con la imagen exacta del paquete oficial 3.21 (VERIFICADO con `cmp`). `nflasha1` (Updater) está en el volcado. El primer intento (`updater_full_dump.py`, nodos `nflasha0pN`) solo sacó RAM. Restaurar sigue sin camino de escritura de dispositivo en el shell de pmca (`PUSH` escribe archivos): NO VERIFICADO.
- Copia NVRAM fresca (`senser_backup_dump.py`).

## Volcado de RAM del sistema (2026-10-20)

`scripts/senser_ram_dump.py` leyó 1 GiB de RAM física del sistema en marcha por service mode (`analysis/camera-dumps/ram-servicio-20261020`, solo hash versionado). El volcado de RAM de `full-20261020-nand` es de modo actualizador, no del sistema.

## Resto de volcados (2026-10-20)

- RAM del sistema: `/proc/iomem` declara `System RAM` en `0x80000000-0xbfffffff` = 1 GiB, ya volcado completo (`ram-servicio-20261020`); no hay más RAM.
- Periféricos (`regiones-20261020`): `arm7sram`, `arm7io`, `nandreg`, USB (EHCI/OHCI/UDC), `uart0/2` y `0xf1000000+0x100` leídos; `nandc` (`0x10000000`) falla. El volcado de 16 MiB en `0xf0000000` no se repite: solo se leen regiones declaradas.
- `/proc/config.gz` no existe en el kernel de la cámara; `kallsyms` ya estaba volcado. Objetivo (`/lens`) listado, sin volcado de su firmware.

- Barrido de `0xF0000000` (parcial): `analysis/camera-dumps/sfr-scan-20261020`; 128 KiB legibles, falla desde `0xF0020000`; por telnet `/dev/mem` da `Bad address` (no sirve). OpenMemories Tweak reinstalado con pmca (`install -a com.github.ma1co.openmemories.tweak`).
