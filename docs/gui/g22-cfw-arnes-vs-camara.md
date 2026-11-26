# G22 — Por qué un CFW no arranca en la cámara y sí en el arnés (y qué puede auditar el arnés)

Etiquetas: **VERIFICADO** (bytes/instrucciones) · **MEDIDO** (ejecución o cámara) · **INFERENCIA** ·
**NO_VERIFICADO** · **NO DETERMINADO**. Solo análisis y documentación: no se ha tocado código, ni cámara, ni firmware.
Fuentes primarias: [`g11`](g11-auditoria-307-nflasha15.md) (auditoría del −307 y del `nflasha15` recompuesto),
[`g10`](g10-menu-silent-informe-de-continuacion.md), [`e24-01`](../capture/e24-01-arranque-recuperacion.md) (cadena de arranque),
[`e26-r13`](../capture/e26-r13-led-error-provenance.md) (códigos LED), [`e26-r36`](../capture/e26-r36-causa-fallo-325.md) (LDEC/TPZL),
[`g111`](g111-film-receta-gui-iconos.md) (cuelgues en cámara y qué se vio en el arnés),
[`g22`](g22-arnes-ui-qemu.md) (§2 arquitectura, §5.18z″ F5, §8 límites) y `scripts/gui/harness/`.

## 1. Respuesta en tres líneas

1. **La cámara no arranca el `/usr` del paquete: reanuda la instantánea de RAM de Sony.** El arranque normal no carga
   Linux de `nflasha3`: Loader3 lee la cabecera de `nflasha5` (`chk ssboot`, `0xc01f20f4`), ve la firma `WBI1` del paquete de
   Sony y elige **`BootMode 11`** (instantánea) ([g11:212-217](g11-auditoria-307-nflasha15.md)). Esa instantánea lleva **el TOC
   TPZL completo del `nflasha15` de Sony**, su superbloque ext2 y 282 páginas de caché ([g11:218-220](g11-auditoria-307-nflasha15.md)).
   Todo `nflasha15` recompuesto **mueve el TOC**, así que el kernel reanudado lee datos equivocados de `/usr`
   ([g11:223-229](g11-auditoria-307-nflasha15.md)). Recuento: **6/6 paquetes con `/usr` recompuesto fallaron y 4/4 con el de
   Sony arrancaron** ([g11:203-205](g11-auditoria-307-nflasha15.md)); quitar el WBI (3.52) lo confirma con `BootMode: 1`
   ([g11:246-250](g11-auditoria-307-nflasha15.md)).
2. **El arnés no pasa por ahí.** Monta `nflasha7` como `/`, el `/usr` (de Sony o del paquete) como `/cam/usr` y ejecuta
   `im.elf` directamente bajo un kernel Debian: **no ejecuta Loader2, ni Loader3, ni Darwin, ni lee `nflasha5`, ni usa el
   kernel de `nflasha3`** (citas y medición en §3).
3. Por tanto: «no arranca en cámara / sí en arnés» = el fallo está **antes del userland** (Darwin → BootROM → Loader2 →
   Loader3 → WBI/kernel), y «falla en ambos» = el fallo está **dentro del userland**, que el arnés sí ejecuta (3.78, §5).

## 2. Cadena de arranque real de la cámara

Orden de ejecución (fuentes en la columna derecha; `e24-01` es análisis estático del volcado NAND y del `bootrom.bin`):

| # | Etapa | Qué hace | Fuente |
|---|---|---|---|
| 0 | **Darwin** (MCU FM3 IC5700), siempre alimentado | Secuencia de encendido `DD_ON1/2/3` (`darwin_core.bin`, tabla `0x28c6c`) → alimenta núcleo y LPDDR2 del BIONZ; mide batería; recibe `XPOWER_SW`/`XPWR_ON`. Sin ella no hay BootROM ni actualizador | [e24-01:72](../capture/e24-01-arranque-recuperacion.md), [e24-01:18-30](../capture/e24-01-arranque-recuperacion.md) |
| 1 | **BootROM** «Musashi Loader1» `0xffff0000` | Lee GPIO `0xf2915010` b0 y `0xf2910410` b22 y salta a `0xc0030000` | [e24-01:73](../capture/e24-01-arranque-recuperacion.md), [e26-r13:34-36](../capture/e26-r13-led-error-provenance.md) |
| 2 | **Loader2** `0xc0030000` | `Init BOSS`/MuMin (`nflasha0`), copia Loader3 a `0xc01f0000` y salta (`blx r5`). Errores propios → LED con `n = 1000 + abs(err)` | [e26-r13:34-40](../capture/e26-r13-led-error-provenance.md), [g11:150-151](g11-auditoria-307-nflasha15.md) |
| 3 | **Loader3** `0xc01f0000` | Init (UDIF/MuMin/BlkDev) y **selección de modo**: `chk ssboot` (`0xc01f20f4`) → si `nflasha5` es `WBI1`/`WBI0`, `BootMode 11`; si no, modo por defecto | [g11:215-217](g11-auditoria-307-nflasha15.md), [e26-r13:34-40](../capture/e26-r13-led-error-provenance.md) |
| 4a | Arranque **UPDATER**→ `nflasha1` (FAT) | `boot/vmlinux.bin` (Linux 3.0.27) + `boot/initrd.img` (cramfs) en `loadaddr` 0x81528000/0x80628000 | [e24-01:77](../capture/e24-01-arranque-recuperacion.md) |
| 4b | Arranque **en caliente** → `nflasha5` | Instantánea `WBI1`: RAM restaurada; en modo 11 el RAMCFG solo carga `idt_cam.bin` y `av-cam.bin`, **no** `vmlinux.bin`/`initrd.img` | [e24-01:79](../capture/e24-01-arranque-recuperacion.md), [g11:217](g11-auditoria-307-nflasha15.md) |
| 4c | Arranque **en frío** → `nflasha3` (TPZL) | `vmlinux.bin`, `initrd.img`, `av-cam.bin`, `sabin`; decodificados por el **LDEC** hardware | [e24-01:78](../capture/e24-01-arranque-recuperacion.md), [e26-r36:30-44](../capture/e26-r36-causa-fallo-325.md) |
| 5 | Linux + `/sbin/init` | Carga módulos (`nand`, `osal_*`, `backup`, `dmm`, `upm`…), `pivot_root`, lanza `bootin.elf`/`sen.elf`; `/` = `nflasha7`, `/usr` = `nflasha15`, `/setting` en `nflasha2` | [e24-01:78](../capture/e24-01-arranque-recuperacion.md) |

Particiones que intervienen: `nflasha0` (zona de arranque: Loader3 = bloque 2), `nflasha1` (FAT del actualizador),
`nflasha2` (`/setting` + banderas `mode*`), `nflasha3` (kernel/initrd/`av-cam`/`sabin` del arranque en frío), `nflasha5` (WBI),
`nflasha7` (rootfs), `nflasha15` (`/usr`, TPZL de ext2 de 100 MiB — `mount.conf`; tope 104 857 600 B en
`scripts/gui/build_nflasha15.py:17`). Los LED de error se decodifican con el patrón de
[e26-r13 §2](../capture/e26-r13-led-error-provenance.md): grupos LDR2/LNG/SHT = millares/centenas/unidades de `n = |código|`, y Loader2
suma 1000.

**Corolario clave (INFERENCIA fuerte, [g11:212-232](g11-auditoria-307-nflasha15.md)):** en el arranque normal Loader3 **solo lee la
cabecera y el TOC de `nflasha15`** (24 B + TOC; el retorno del bucle se ignora, [g11:22-27](g11-auditoria-307-nflasha15.md)), así que un
−307 nunca se debe al *contenido* de `/usr`; el daño de un `nflasha15` recompuesto ocurre en el kernel reanudado desde el WBI.

## 3. Cadena de arranque del arnés

| Pieza | Qué es | Fuente |
|---|---|---|
| Kernel + initramfs | Instalador *netboot* de Debian trixie armhf: `vmlinuz` 6.12 armmp + `initrd.gz`; **no** el kernel 3.0.27 de Sony | [setup.sh:14-15](../../scripts/gui/harness/setup.sh), [setup.sh:19-23](../../scripts/gui/harness/setup.sh) |
| `/` del invitado | `nflasha7_unpacked_unpacked` copiado a `stage/cam`; su `/usr` se borra y se pone `nflasha15_unpacked_unpacked` | [build_base.py:20-22](../../scripts/gui/harness/build_base.py) |
| Enlaces y permisos | soname reconstruidos, `ld-linux.so.3 → ld-2.11.2.so`, bit `x` restaurado (el extractor no lo conserva) | [build_base.py:25-39](../../scripts/gui/harness/build_base.py) |
| `init` | `busybox sh`: monta `proc/sys/dev`, bind-mount en `/cam`, `tmpfs` en `/cam/tmp`, ejecuta `/cam/harness.sh` y apaga | [build_base.py:41-49](../../scripts/gui/harness/build_base.py) |
| Overlay | cpio.gz concatenado: `/cam/harness.sh`, `/cam/harness.env` (`SHIMENV`), `overlay/` (shim + `bk.tbl`) y `OVERLAY2` (el `/usr` del CFW), que sustituye a los ficheros de Sony por ir después en el cpio | [run.py:36-61](../../scripts/gui/harness/run.py), [run.py:46-47](../../scripts/gui/harness/run.py) |
| QEMU | `qemu-system-arm -M virt -cpu cortex-a15 -smp 8 -m 1536`, `-kernel vmlinuz -initrd <concat> -nographic -no-reboot` | [run.py:64-68](../../scripts/gui/harness/run.py) |
| Arranque del userland | `LD_PRELOAD=/usr/lib/sonyshim.so chroot /cam /usr/bin/im.elf "${IMARGS:-s g r u l i a}"` | [im.sh:42](../../scripts/gui/harness/im.sh), [im.sh:48-54](../../scripts/gui/harness/im.sh) |
| Resultado | `alive= / threads= / lineas= / modulos=`, colas `dlopen(.*) -> 0x0`, `EXIT=`, pilas de `SIGSEGV` | [im.sh:71-83](../../scripts/gui/harness/im.sh) |
| NVRAM | tabla `{id,len,datos}` extraída del volcado real; el shim atiende el backup `0x3e014d` (lectura) y `live.py` parchea registros sobre la copia | [gen_bk.py:1-17](../../scripts/gui/harness/gen_bk.py), [run.py:21-33](../../scripts/gui/harness/run.py) |
| `/usr` de un CFW | `pkg_usr.py` lee la imagen TPZL **ya construida** (TPZL → ext2 → `debugfs rdump`) y deja solo los ficheros distintos del `/usr` de Sony | [pkg_usr.py:20-33](../../scripts/gui/harness/pkg_usr.py), [g22:456-461](g22-arnes-ui-qemu.md) |

**El arnés no ejecuta Loader2, Loader3 ni Darwin (VERIFICADO por código y por medición):**

* `im.sh` arranca `im.elf` en el `init` de Debian ([im.sh:42](../../scripts/gui/harness/im.sh)); no hay ninguna etapa de carga previa.
* `build_base.py` solo toma `nflasha7` y `nflasha15` del firmware ([build_base.py:20-22](../../scripts/gui/harness/build_base.py));
  `stage/cam/initrd/` queda **vacío** (`ls | wc -l` = 0): no se copian `vmlinux.bin` ni `initrd.img` de `nflasha3`.
* Medición: `grep -rli` sobre `scripts/gui/harness/*.py|*.sh|shim/` de los nombres `vmlinux.bin`, `initrd.img`,
  `darwin_core`, `bootloader.bin`, `nflasha5`, `wbi`/`WBI` → **0 ficheros**; sí aparecen `av-cam` (motor BIONZ, que se ejecuta
  aparte en la LIRO VM) y `nflasha4` (imagen opt-in, §5.43).
* El initramfs base no contiene dispositivos ni particiones de la cámara: `zcat base.cpio.gz | cpio -it | grep -E "^cam/(boot|nflasha)"`
  → vacío (solo `cam/setting` y `cam/system`, directorios del rootfs de `nflasha7`).

## 4. (a) Qué valida la cámara y el arnés no

| Comprobación | Cámara (dónde) | Arnés QEMU (`run.py`/`live.py`) | Auditor offline (`audit_package_nflasha15.py`) |
|---|---|---|---|
| Magia e CRC del `.dat`, descifrado FDAT por bloques | `pmca` (host) al enviar; el actualizador lo recibe | **sí**, al importar: `emu_config.descifra`/`cabecera_dat` ([emu_config.py:140-181](../../scripts/gui/harness/emu_config.py)) | **sí**: `contenedor.dend_ok`, `descifrado_igual_a_fdat`, `bloques_cifrado_sin_error`, `crc_cabecera_ok` ([audit_package_nflasha15.py:47-56](../../scripts/gui/audit_package_nflasha15.py)) |
| Modelo y región del paquete | `pmca` en el envío (`install-3.94.log`: «Firmware image matches this camera») y el actualizador por sus sumas ([e26-r36:29](../capture/e26-r36-causa-fallo-325.md)) | **modelo sí** (`0x41030035`); **región no se comprueba** ([emu_config.py:37](../../scripts/gui/harness/emu_config.py), [:169-181](../../scripts/gui/harness/emu_config.py)) | **sí**: `contenedor.modelo_region`, `contenedor.updater_oficial_3_21` |
| Versión estrictamente mayor | el actualizador rechaza (`Invalid version`, [g11:209](g11-auditoria-307-nflasha15.md)) | **no** | **sí**: `contenedor.version_mayor_que_base` |
| CRC/tamaño de cada partición (`part_image.sum`) | el actualizador relee y verifica antes de «Done» ([e26-r36:29](../capture/e26-r36-causa-fallo-325.md)) | **no** | **sí**: `tar.todas_las_sumas_verifican`, `tar.solo_cambian_los_miembros_previstos` |
| Loader2/Loader3 (`loader_sum`) e integridad del arranque | el actualizador solo reescribe los cargadores si el paquete trae `loader_sum` (el 3.21 no lo trae) ([e24-01:74](../capture/e24-01-arranque-recuperacion.md)) | **no** | **no** |
| TPZL como lo lee el **LDEC**: 512 B, ≤16 registros de 4 KiB por bloque, bloque 0 | sí, en cada lectura de Loader3/Linux ([e26-r36:30-44](../capture/e26-r36-causa-fallo-325.md)) | **no**: el TPZL se decodifica por software ([pkg_usr.py:23](../../scripts/gui/harness/pkg_usr.py)) | **sí**: `nflasha15.sin_violaciones_ldec`, `.alineado_512`, `.contiguo`, `.bloque_0_identico_a_sony_(R55)`, `.max_sectores_no_mayor_que_sony` |
| Coherencia **WBI (`nflasha5`) ↔ `nflasha15`** | sí: es la causa de los 6 fallos ([g11:212-232](g11-auditoria-307-nflasha15.md)) | **no**: el arnés ignora `nflasha5` (§3) | **parcial**: detecta si se quita `nflasha5` (`tar.solo_se_quitan_los_previstos`, `tar.sum_sin_linea_nflasha5`), pero **no** que un `nflasha15` recompuesto con `nflasha5` presente es inviable |
| Darwin: `darwin.sum` y que la secuencia de encendido no se rompa | sí, `us_darwin_firm.sh`/`darwin.sum`; y el encendido depende de `darwin_core` ([e24-01:18-30](../capture/e24-01-arranque-recuperacion.md)) | **no** | **parcial**: `darwin.darwin_v3_presente` y `darwin.darwin_solo_rango_r82` (solo si se usó Darwin v3) |
| ext2: contenido, hashes, modo/uid/gid, `e2fsck` | Linux monta `/usr` y ejecuta los ficheros | **no valida**: monta lo que le den ([pkg_usr.py:26-32](../../scripts/gui/harness/pkg_usr.py)) | **sí**: `ext2.solo_cambian_los_ficheros_del_paquete`, `ext2.hashes_…`, `ext2.modo_uid_gid_como_sony`, `ext2.fsck_…` |
| `.uxc`: orden de registros por id, ids dentro de las 5 958 ranuras | sí: el Lector de recursos de la cámara (`stella … ResourceManager.cpp(954)`, [g10:21](g10-menu-silent-informe-de-continuacion.md)) — y en general cualquier id de la tabla de recursos `0x…` que consulte | **no**: los `.uxc` se descomprimen por software y se aceptan los dos órdenes ([g111:330-339](g111-film-receta-gui-iconos.md)) | **no** |
| **Coherencia de versiones entre particiones** (`nflasha3` ↔ `nflasha7` ↔ `nflasha15`) | sí: el kernel y los `.ko` de `nflasha3`/`nflasha7` tienen que encajar (Linux 3.0.27, módulos propietarios) | **no**: el kernel es Debian y los módulos de Sony no se cargan; **solo** se ejecuta el `av-cam` del paquete, si se adjunta ([lanzador.py:69](../../scripts/gui/harness/lanzador.py), [emu_config.py:206-208](../../scripts/gui/harness/emu_config.py)) | **no** |
| ELF: relocaciones, `PT_LOAD`, `DT_REL` | el `dlopen` de la cámara | **sí, de facto**: si el ELF o una biblioteca está roto, `im.elf` muere en segundos (§7) | **no** |
| NVRAM: existencia y coherencia de los registros que lee el CFW | la propia NVRAM | **lectura** desde el volcado real (`bk.tbl`); escrituras descartadas o al perfil | **no** |
| Hardware: sensor, cortinas EFCS, ISP, GPU de DMP, decodificador de vídeo | sí | **no** (GPU/2D emulados por software, ISP propio en G23) | **no** |

## 5. Clasificación de los CFW con fallo conocido

| CFW | Qué cambió | Fallo en cámara (etapa/código) | ¿Arranca en el arnés? | Por qué |
|---|---|---|---|---|
| **3.38** | `nflasha3` (BIONZ/`av-cam`) con EFCS desactivado; `/usr` de Sony | **arranca** ([g11:225](g11-auditoria-307-nflasha15.md)) | sí (clase de arranque del 3.21) | no mueve el TOC de `nflasha3` (2373/2373 entradas iguales) y `av-cam.bin` se recarga en cada arranque ([g11:225](g11-auditoria-307-nflasha15.md)) |
| **3.39** | menú Silent con ids de la A6300 (`0xf840/7/9`) + Darwin v3; `nflasha15` recompuesto (134 bloques) | Linux arranca y **pantalla negra**; `E/stella(148): assert src/ResourceManager.cpp(954)` ([g10:21](g10-menu-silent-informe-de-continuacion.md)) | sí (no se cargó esta imagen en el arnés: **NO_VERIFICADO**) | doble atribución: ids fuera de las 5 958 ranuras (VERIFICADO offline) y/o reanudación del WBI con el TOC viejo (corrige a la primera, [g11:227-228](g11-auditoria-307-nflasha15.md)) |
| **3.40** | menú corregido (`0xf3e8/0xf515/0xf56a`) + Darwin v3 | **no arranca**: LED 3 lentos + 7 rápidos = **Loader3 −307** ([g10:22](g10-menu-silent-informe-de-continuacion.md), [PENDIENTES:686](../PENDIENTES.md)) | sí (misma clase que el 3.79; **NO_VERIFICADO** con la imagen) | WBI de `nflasha5` + TOC desplazado (594) ([g11:223-229](g11-auditoria-307-nflasha15.md)); el arnés no lee ni el WBI ni el TOC |
| **3.42** | = 3.40 **sin** Darwin v3 | **no arranca** (mismo LED) ([g10:24](g10-menu-silent-informe-de-continuacion.md)) | sí (ídem) | ídem: Darwin no interviene en esta etapa |
| **3.43** | 3.38 + `/usr` de Sony + Darwin v3 | **arranca**, fw 3.43 ([g10:25](g10-menu-silent-informe-de-continuacion.md); MEDIDO [PENDIENTES:686](../PENDIENTES.md)) | sí | el TOC del WBI vuelve a ser el de su `/usr` |
| **3.44a** | 3.43 + `CautionConfig.so` y 25 `.uxc` (`viewUnified2.so` de Sony) | **no arranca**: LED 1/2/1 = **Loader2 −201** (INFERENCIA fuerte); SWD: se queda en `LDR:Load LDR3` ([g11:129-151](g11-auditoria-307-nflasha15.md)) | sí (**NO_VERIFICADO** con la imagen) | el fallo está **antes** de Loader3; el arnés arranca el userland sin cargadores |
| **3.48** (control) | los 26 ficheros reescritos con los **bytes de Sony** (cambian inodos/bloques) | **falla igual** que 3.40/3.44a ([g11:190-205](g11-auditoria-307-nflasha15.md)) | sí (equivale al `/usr` de Sony) | prueba decisiva de que el problema es **escribir un `nflasha15` recompuesto** (TOC nuevo) y no el contenido |
| **3.52** | `nflasha15` del 3.48 **sin** `nflasha5` | **arranca en frío**, `BootMode: 1` por SWD ([g11:246-250](g11-auditoria-307-nflasha15.md)) | sí | quitar el WBI es lo que el arnés ya hace por construcción |
| **3.53** | menú completo, sin `nflasha5` | **arranca**; la entrada aparece sin selector ([g11:261-264](g11-auditoria-307-nflasha15.md)) | sí | WBI invalidado; el defecto de selector se midió en `qemu-arm` ([g11:266-275](g11-auditoria-307-nflasha15.md)) |
| **3.25** (E26) | `nflasha3` recompuesto por `tpzl.py`: 359/369 bloques desalineados y 3 bloques con un solo registro de 64 KiB | **no arranca**: LED 3 lentos + 2 rápidos = **Loader3 −302** ([e26-r36:12-22](../capture/e26-r36-causa-fallo-325.md)) | sí: el TPZL se lee por software (el defecto es del **silicio**, no del formato lógico) | el LDEC recibe el residuo mal alineado y >16 registros por bloque ([e26-r36:30-44](../capture/e26-r36-causa-fallo-325.md)); reproducible solo con Loader3+ARM7 emulados (R39) |
| **3.78** | `libObj.so` + `viewUnified2.so` + `.uxc` (menú Picture Profile) | **cuelga** al abrir Picture Profile (G36 §7) | **no: se reproduce** — `SIGSEGV` en `libObj+0x5b6242` ([g22:460](g22-arnes-ui-qemu.md), [PENDIENTES:351](../PENDIENTES.md)) | el fallo está en el modelo de `libObj`, que el arnés ejecuta de verdad |
| **3.79** | corrección del 3.78 | no se instaló en cámara | **sí**: 6 filas + carpeta PP, F5 ([g22:459](g22-arnes-ui-qemu.md)) | — |
| **3.94 / 3.96 / 3.98** | `image_cmn_169.uxc` con iconos propios (fuera de orden y luego ordenados) y gancho `isInhOn` | Fn → bucle / cuelgue al entrar en AWB ([g111:66-90](g111-film-receta-gui-iconos.md), [:150-166](g111-film-receta-gui-iconos.md)) | **sí arranca y sin cuelgues**: «el arnés no emula el LDEC/GPU reales» ([g111:339](g111-film-receta-gui-iconos.md)) | el `.uxc` lo descomprime software (`tpzl._inflate_segment`) y el LDEC hardware nunca recibe esos flujos ([g111:82-84](g111-film-receta-gui-iconos.md)) |
| **3.99** | iconos propios ordenados + gancho `isInhOn` con comprobación de pila | **no arranca**, sin aislar ([g111:164-170](g111-film-receta-gui-iconos.md)) | **NO_VERIFICADO** | mezclaba dos cambios; si el fallo es de arranque (WBI/partición) el arnés no puede verlo |

**Qué dicen los `install-*.log` (y qué no).** Todos registran la **actualización**, no el arranque: `install-3.94.log` acaba en
«Done.» tras «Firmware image matches this camera», y los intentos fallidos documentan el enlace con el actualizador
(`Operation timed out…` en `install-3.69-intento1-timeout.log`, `The camera sent an unexpected response…` en
`install-3.76-intento1-respuesta-inesperada.log`, `No devices found…` en `install-3.68-fallido-sin-camara.log`). Un «Done» solo
prueba que el actualizador aceptó el paquete — justo la etapa que el arnés **no** comprueba —, y no dice nada del arranque
posterior ([g11:209](g11-auditoria-307-nflasha15.md) es el mismo criterio: `Incorrect version`/`Done` no predicen el arranque).

## 6. (b) Qué es invisible para el arnés por diseño y qué rompe el arranque real

El arnés **solo ve** `/usr` (overlay de `nflasha15`), opcionalmente el `av-cam` del paquete (`--pkg ….nflasha3`) y una imagen
opcional de `nflasha4`. Todo lo demás del `.dat` es invisible:

| Cambio del CFW | ¿Lo ve el arnés? | ¿Rompe el arranque real? | Por qué |
|---|---|---|---|
| Contenido de `/usr` (bibliotecas, `.uxc`, recursos) | **sí** (overlay + ejecución) | depende: `dlopen`/modelo sí; recursos leídos por el Lector con invariantes no vistos en QEMU | [g22:456-461](g22-arnes-ui-qemu.md), [g111:116-124](g111-film-receta-gui-iconos.md) |
| **Recompresión de `nflasha15` (TOC desplazado)** | no (solo el contenido de ficheros) | **sí, si `nflasha5` sigue presente** | WBI de Sony con TOC/cachés viejas ([g11:223-232](g11-auditoria-307-nflasha15.md)) |
| Inclusión/exclusión de `nflasha5` (WBI) | no | **sí**: es la palanca que arregla el arranque | [g11:234-250](g11-auditoria-307-nflasha15.md) |
| Disposición TPZL de `nflasha15`/`nflasha3` (alineación 512 B, ≤16 registros/bloque) | no | **sí** (LDEC) | [e26-r36:30-44](../capture/e26-r36-causa-fallo-325.md) |
| `darwin_core.bin` (tabla EFCS) | no | solo si rompe la secuencia de encendido | [e24-01:18-30](../capture/e24-01-arranque-recuperacion.md) |
| Versión del paquete / `config.yaml` / `updater.img` | no | **sí** (rechazo del actualizador) | [g11:209](g11-auditoria-307-nflasha15.md), [install-3.94.log](../../analysis/gui/g22/install-3.94.log) |
| `part_image.sum` incoherente | no (el importador no lo comprueba) | **sí** (el actualizador relee CRCs) | [e26-r36:29](../capture/e26-r36-causa-fallo-325.md) |
| NVRAM (escrituras de la receta) | lectura sí, escritura no | puede cambiar el comportamiento, no el arranque | [g22:2.1 `0x3e014d`](g22-arnes-ui-qemu.md) |

## 7. (c) Clases de fallo: qué se reproduce igual y qué no puede reproducirse nunca

**Se reproducen igual (MEDIDO):**

* **Cuelgue/crash del modelo o de la UI**: 3.78 → `SIGSEGV` en `libObj+0x5b6242` en el arnés y cuelgue en cámara
  ([g22:460](g22-arnes-ui-qemu.md)).
* **Estructura de menús y recursos visibles**: 3.79, 6 filas y carpeta PP ([g22:459](g22-arnes-ui-qemu.md)).
* **Inhibiciones y setters**: `WrapperWhiteBalance::isInhOn` devuelve 1 y el balance no se escribe; síntoma idéntico al de cámara
  ([g111:103-115](g111-film-receta-gui-iconos.md)).
* **Fallo de carga de una biblioteca de `/usr`**: prueba de hoy (§7.1).
* **Desbordamiento de la partición, `e2fsck`, hashes**: verificables offline (auditor).

**No pueden reproducirse nunca en el arnés (por diseño):**

* Códigos LED de **Loader2/Loader3** (−201, −302, −307) y todo lo que ocurre antes de Linux: el arnés no ejecuta esos
  binarios (§3). Para eso existe la emulación de Loader3 + ARM7 + LDEC de R39, no este arnés ([e26-r36:22](../capture/e26-r36-causa-fallo-325.md)).
* **Acoplamiento WBI (`nflasha5`) ↔ `nflasha15`**: el arnés no lee ni `nflasha5` ni el TOC ([g11:212-232](g11-auditoria-307-nflasha15.md)).
* **Darwin** (encendido, actualización del MCU, CAIF/MSS) y todo el bloque de potencia ([e24-01:72](../capture/e24-01-arranque-recuperacion.md)).
* **Aceptación del actualizador** (modelo, región, versión, `part_image.sum`) ([g11:209](g11-auditoria-307-nflasha15.md)).
* **Decodificación por hardware del LDEC** de los flujos LZ de `.uxc`/TPZL, y GPU/ISP/vídeo reales ([g111:82-84](g111-film-receta-gui-iconos.md)).
* **NVRAM física** (solo se emula la lectura) y cualquier efecto del hardware (sensor, cortinas del EFCS).

### 7.1 Prueba corta en el arnés (MEDIDO, 26-11-2026)

Objetivo: calibrar la sensibilidad del arnés ante un `/usr` corrupto *versus* un `/usr` correcto, con **una sola variable**
(`libosal_uipc.so`, 26 636 B, biblioteca que `im.elf` necesita: `readelf -d` → `NEEDED libosal_uipc.so`).

```sh
# overlay de control: la biblioteca de Sony, intacta
mkdir -p ov_control/cam/usr/lib && cp -p stage/cam/usr/lib/libosal_uipc.so ov_control/cam/usr/lib/
# overlay roto: la misma biblioteca truncada a 1024 B
mkdir -p ov_roto/cam/usr/lib && cp -p stage/cam/usr/lib/libosal_uipc.so ov_roto/cam/usr/lib/
truncate -s 1024 ov_roto/cam/usr/lib/libosal_uipc.so
# initrd con cada overlay (misma llamada que run.py:46-47) y un arranque de 20 s
qemu-system-arm -M virt -cpu cortex-a15 -smp 8 -accel tcg,thread=multi,tb-size=512 -m 1536 \
  -kernel vmlinuz -initrd <initrd_con_overlay> -append "console=ttyAMA0 quiet loglevel=3" -nographic -no-reboot
```

| Overlay | Resultado medido |
|---|---|
| control (`libosal_uipc.so` de Sony) | `alive=209 threads=83 lineas=4184 modulos=69` |
| roto (mismo fichero truncado a 1024 B) | `alive= threads=0 lineas=3 modulos=0`, `EXIT=135`, `ERROR: ld.so: object '/usr/lib/sonyshim.so' from LD_PRELOAD cannot be preloaded (cannot open shared object file): ignored.`, `Bus error` |

Lectura: **un `/usr` roto se detecta en menos de 20 s** (SIGBUS al mapear la biblioteca truncada; el `ld.so` de la cámara
aborta el preload). Es decir, el arnés **no es insensible por falta de sensibilidad, sino porque las etapas que fallaron en la
cámara (Darwin, Loader2/3, WBI) no se ejecutan aquí**. Límite honesto de esta medición: el arranque se hizo con otros dos
QEMU de otro agente en el host (`pgrep -c qemu-system-arm` = 2), así que los tiempos no son comparables; el fallo no depende de
ellos (el `SIGBUS` viene de leer páginas más allá del fin de fichero).

## 8. Qué puede auditar el arnés y qué no (criterio para `audita_cfw.py`)

Ordenado por etapa del paquete. «Arnés» = lo que se puede comprobar **hoy** con lo que hay en `scripts/gui/` (auditor
offline + importador + una ejecución en QEMU). Cada fila indica qué errores de un CFW se detectan aquí y cuáles solo se verían
en la cámara.

| Etapa | Errores **detectables** en el arnés | Cómo (implementación de referencia) | Errores que **solo** se verían en cámara |
|---|---|---|---|
| **Contenedor `.dat`** | magia/cabecera ilegible, CRC de cabecera, DEND, bloques FDAT corruptos o cifrados con otra clave, **modelo** distinto de `0x41030035`, `updater.img` no oficial, versión no mayor que la base | `emu_config.descifra`/`cabecera_dat` ([emu_config.py:140-181](../../scripts/gui/harness/emu_config.py)); `audit_package_nflasha15.open_dat` ([audit_package_nflasha15.py:40-56](../../scripts/gui/audit_package_nflasha15.py)) | **región** no comprobada en el arnés; rechazo real del actualizador (códigos `0x1063`, `Invalid version`) y del `p1chksum` de `nflasha1` ([g11:209](g11-auditoria-307-nflasha15.md)) |
| **Tar / particiones** | miembros que cambian sin estar previstos, miembros quitados, `part_image.sum` que no verifica, tamaño > partición (100 MiB), `nflasha15` no TPZL, `nflasha5` presente **con** un `nflasha15` recompuesto (regla nueva, ver abajo) | `audit_package_nflasha15.run` ([audit_package_nflasha15.py:218-240](../../scripts/gui/audit_package_nflasha15.py)) | rechazo del actualizador por sumas/CRC al releer las particiones; que el LDEC acepte la imagen (`nflasha3` sobre todo) ([e26-r36:29-44](../capture/e26-r36-causa-fallo-325.md)) |
| **`/usr` (ext2 dentro de `nflasha15`)** | ficheros distintos de los declarados, hashes, modo/uid/gid (el defecto 3.39–3.42), `e2fsck` con algo más que contadores, ficheros nuevos con modo/owner raros | `audit_package_nflasha15.run` ([audit_package_nflasha15.py:179-208](../../scripts/gui/audit_package_nflasha15.py)); `build_nflasha15.replace_files` comprueba modo tras escribir ([build_nflasha15.py:39-56](../../scripts/gui/build_nflasha15.py)) | nada propio de la cámara salvo el acoplamiento con el WBI (§6) |
| **Estructura TPZL (lo que lee el hardware)** | bloques mal alineados, >16 registros por bloque, TOC/h cabecera incoherentes, bloque 0 distinto del de Sony, `max_sectores` mayor que Sony | `tpzl.hardware_violations` vía `layout()` ([audit_package_nflasha15.py:77-91](../../scripts/gui/audit_package_nflasha15.py)) | el comportamiento del silicio está modelado, no medido: la emulación de R39 reproduce 361/369 fallos, pero no es prueba física ([e26-r36:22](../capture/e26-r36-causa-fallo-325.md)) |
| **ELF / recursos** | ELF truncado, `dlopen` que falla, `SIGSEGV` con pila, cuelgue del modelo; invariantes de `.uxc` si se implementan como test (hoy **no** hay comprobador de orden/ids) | ejecución en QEMU ([im.sh:71-83](../../scripts/gui/harness/im.sh); medición §7.1); `tests/test_gui_harness.py` | `ResourceManager` de la cámara (ids fuera de las 5 958 ranuras, `.uxc` fuera de orden) y el LDEC de los flujos LZ ([g10:21](g10-menu-silent-informe-de-continuacion.md), [g111:82-84](g111-film-receta-gui-iconos.md)) |
| **Arranque del userland en QEMU** | que `im.elf` llegue a un punto de referencia (`alive/threads/modulos`), que no aparezca un `SIGSEGV` nuevo frente a la línea base, que la vista/menú esperado se abra | `live.py` (perfiles), `run.py`+`im.sh`, `OPENVIEW`/`INJECT` ([g22:456-461](g22-arnes-ui-qemu.md)) | todo lo dependiente de hardware y de tiempos reales |
| **Loader2 / Loader3** | **nada** | — (fuera del arnés; ver R39) | −201 (Loader2), −302/−306/−307 (Loader3), `BootMode`, lectura NAND de `nflasha0` ([e26-r13 §2](../capture/e26-r13-led-error-provenance.md)) |
| **Darwin** | **nada** salvo el rango de parches del Darwin v3 (auditor) | `audit_package_nflasha15.run` → `darwin.*` | secuencia `DD_ON1/2/3`, actualización del MCU y todo el encendido ([e24-01:72](../capture/e24-01-arranque-recuperacion.md)) |
| **NVRAM** | coherencia de los registros que el CFW **lee** (con el volcado real: `bk.tbl`; en `live.py`, `nvram.json` del perfil) | [gen_bk.py:1-17](../../scripts/gui/harness/gen_bk.py), [run.py:21-33](../../scripts/gui/harness/run.py) | cualquier efecto de escritura real y el estado de la NVRAM de la cámara |
| **Hardware** | **nada** (GPU/2D por software, ISP propio en G23) | — | sensor, cortinas, ISP/GPU de DMP, decodificador de vídeo (`av-cam` real) ([g22:603-608](g22-arnes-ui-qemu.md)) |

**Tres reglas que el CLI debería imponer como puerta (derivadas de la evidencia de este informe):**

1. **`nflasha5` presente ⇒ `nflasha15` byte a byte el de Sony.** Es la única regla que explica 6/6 fallos frente a 4/4 aciertos
   ([g11:203-205](g11-auditoria-307-nflasha15.md), [:212-232](g11-auditoria-307-nflasha15.md)). Si el paquete cambia `/usr`, debe
   llevar `--sin-wbi` ([build_package_nflasha15.py:40-44](../../scripts/gui/build_package_nflasha15.py)) y decirlo el informe.
2. **Toda partición que lea el LDEC cumple las reglas de hardware** (`hardware_violations` = 0, alineación 512 B, bloque 0 = Sony):
   es la clase que tumbó el 3.25 en cámara y que el arranque en QEMU **no** ve ([e26-r36:12-22](../capture/e26-r36-causa-fallo-325.md)).
3. **Diferencia de comportamiento en QEMU frente a la línea base de Sony**: mismo número de `modulos`, sin `SIGSEGV`/`EXIT≠0`
   nuevos y la vista esperada abierta; un fallo de tipo 3.78 se detecta así ([g22:460](g22-arnes-ui-qemu.md)).

## 9. Límites y NO_VERIFICADO

* **NO_VERIFICADO:** que las imágenes 3.39, 3.40, 3.42 y 3.44a arranquen en el arnés; sus `.bin`/`.dat` no están versionados en
  este árbol, así que la columna «arranca en arnés» de esas filas se apoya en la clase de arranque (F5: overlay de `/usr` del
  paquete) y no en una ejecución de esa imagen ([g22:456-461](g22-arnes-ui-qemu.md)).
* **NO DETERMINADO:** el eslabón exacto por el que el 3.44a no termina de leer Loader3 (el −201 de `Init BOSS`) y por qué el
  `nflasha15` recompuesto lo provoca *antes* de Loader3 ([g11:157-167](g11-auditoria-307-nflasha15.md)).
* La prueba de §7.1 se hizo con dos QEMU ajenos en el host (regla de 2 procesos); el fallo es determinista por construcción
  (páginas más allá del EOF), pero los tiempos no son comparables.
* El arnés no prueba nada sobre el silicio: su emulación de GPU/ISP es propia y su LDEC no existe
  ([g111:339](g111-film-receta-gui-iconos.md), [g22:603-608](g22-arnes-ui-qemu.md)).

## PARA PENDIENTES.md

```markdown
| G22-CFW-ARRANQUE | PARCIAL (26-11-2026) ([G22-CFW](gui/g22-cfw-arnes-vs-camara.md)) | **Por qué un CFW no arranca en la cámara y sí en el arnés**: el arranque normal reanuda el WBI de `nflasha5` (`BootMode 11`) con el TOC y las cachés del `/usr` de Sony, así que todo `nflasha15` recompuesto lee datos equivocados (6/6 fallos con `/usr` recompuesto, 4/4 con el de Sony; 3.52 sin WBI arranca en frío, `BootMode 1`). El arnés no ejecuta Loader2/Loader3/Darwin ni lee `nflasha5`: monta `nflasha7`+`nflasha15` (o el overlay del paquete) y lanza `im.elf` bajo una `init` de Debian. Clasificadas las clases de fallo: se reproducen los del userland/modelo (3.78, `SIGSEGV` en `libObj+0x5b6242`; un `/usr` truncado se detecta en <20 s, `EXIT=135`) y no pueden reproducirse los de Loader2/3 (−201/−302/−307), el acoplamiento WBI↔`nflasha15`, Darwin, la aceptación del actualizador ni el LDEC hardware (3.25). Criterio por etapa para `audita_cfw.py` y tres puertas propuestas: WBI coherente, reglas de hardware del TPZL y diferencia de comportamiento en QEMU frente a Sony | Cierre: `scripts/gui/harness/audita_cfw.py` implementa las tres puertas y las pasa sobre un paquete con `/usr` recompuesto + `nflasha5` (debe rechazarlo) y sobre el 3.95 instalado (debe aceptarlo) | `scripts/gui/harness/`, [G22-CFW](gui/g22-cfw-arnes-vs-camara.md) |
```
