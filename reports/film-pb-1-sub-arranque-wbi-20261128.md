# FILM-PB-1 (sub) — Arranque caliente (WBI) frente a arranque en frío: qué cambia de verdad y cómo se deja listo el arreglo

Fecha: 28-11-2026. **Solo análisis estático**. No se abrió binario con `mcp_rea`, no se ejecutó nada del
actualizador, no se construyó ningún DAT y **no se tocó la cámara**. Continuación de
[wbi-20261127](film-pb-1-sub-wbi-20261127.md) y de la [auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md)
(H1 = arranque en frío), a raíz del hecho nuevo: **un clip grabado por la propia cámara tampoco se reproduce, ni
sale su miniatura, y «Recuperar BD imág.» no lo arregla** ⇒ se sospecha un fallo global.

Evidencia en `reports/evidence/film-pb-1-sub-arranque-wbi-20261128/` (ficheros `01…09`, `dry-run-wbi.py`,
`dry-run-wbi.out`). Los VA de `libmpr`/`libObj` de los informes hermanos no se repiten aquí.

---

## 0. Respuesta en corto

1. **Ningún script de arranque distingue caliente de frío.** `/sbin/init` (ELF con símbolos) consulta
   `/proc/udm/upm_bootmode` y **solo** ramifica para `"ADJUST"` y `"BIS"` ([§1.3](#13-check_bootmode--el-único-que-mira-el-modo)).
   La decisión caliente/frío está **fuera**: en Loader3 y en los parámetros `warm.*` de la línea de comandos ([§2](#2-la-línea-de-comandos-del-kernel-el-verdadero-conmutador)).
2. Lo que cambia funcionalmente es el **conjunto de arranque**: en frío se ejecuta todo `/sbin/init` (**8 puntos de montaje**:
   `/proc`, `/rootfs`, `/usr`, `/tmp`, `/system`, `/setting`, `/log`, `/lens`; **38 `insmod`**; `pivot_root`;
   `bootin.elf` → `im.elf`); en caliente no se ejecuta **nada** de eso, se reanuda la
   instantánea de RAM ([§3](#3-qué-se-crea-monta-o-cambia-solo-en-frío)).
3. **Hallazgo nuevo y decisivo:** en este modelo los *drops* de WBI del **kernel están desactivados por la línea de
   comandos** (`warm.ignore_drop=1`, `warm.boot_drop=0`). `wbi_drop()` es un no-op ([§2.3](#23-quién-invalida-realmente-el-wbi)).
   La **única** invalidación efectiva es `ud_wbi_drop.elf` del actualizador: 512 B a cero sobre `/dev/nflasha5`
   ([§1.2](#12-ud_wbi_dropelf--cómo-se-invalida-el-wbi)). Y quien lo **produce** es `im.elf`, que escribe `warm` en
   `/sys/power/state` ([§2.4](#24-quién-produce-el-wbi-imelf)).
4. La maquinaria está completa y **`sin_wbi=False` es el valor por defecto**: basta con **no** pasar `--sin-wbi`
   ([§5](#5-el-arreglo-comando-exacto)). `--dry-run` **no existe** en esa cadena de scripts; se ha hecho un
   *dry-run* propio equivalente, **20/20 comprobaciones OK** ([§5.3](#53-verificación--dry-run-no-existe)).
5. **Riesgo documentado de conservar el WBI:** el WBI de Sony lleva el TOC y la caché del **`/usr` de Sony**, así que
   en caliente los parches de `/usr` del CFW **no se cargan nunca** y además se arriesga una mezcla incoherente.
   Es el motivo por el que el proyecto lo quita ([§6](#6-riesgo-de-conservar-el-wbi-lo-que-documenta-el-proyecto)).

---

## 1. Los scripts de arranque: quién arranca qué

No hay arranque por scripts. Hay **tres** piezas y un binario:

| Pieza | Ruta real | Qué es / qué hace | Evidencia |
|---|---|---|---|
| `init` | `…/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/sbin/init` | ELF32 ARM **Thumb**, 26 269 B, **no stripped** (`.symtab`). Es todo el arranque de usuario. | `02-init-desensamblado.txt`, `04-init-main-completo.txt` |
| `init` (copia) | `…/dev/nflasha7_unpacked_unpacked/sbin/init` | **Idéntico** bit a bit (`6bfcaf00…fb4d6`) | `01-hashes.txt` |
| `us_mkfs.sh` | `firmware/extracted/fw321/updater.img_unpacked/bin/us_mkfs.sh` | Script del actualizador; llama a `ud_wbi_drop.elf` | `05-ud-wbi-drop.txt` |
| `us_mkfs.sh` (copia) | `…/nflasha15_unpacked_unpacked/bin/udtrbody.bin_unpacked/bin/us_mkfs.sh` | **Idéntico** (`d5376365…b901`) | `01-hashes.txt` |
| `ud_wbi_drop.elf` | `updater.img_unpacked/bin/ud_wbi_drop.elf` | El *drop* del WBI | `05-ud-wbi-drop.txt` |
| **`rc`** | — | **NO EXISTE.** No hay SysV rc, ni `inittab`, ni `rcS`. `TOPRC=/etc/toprc` (`init` `0x9702`) es solo la configuración de la herramienta `top` (`/etc/toprc` contiene `RCfile for "top with windows"`). | `grep -rn 'rc'` sobre nflasha7/nflasha3; `04-init-main-completo.txt` |

### 1.1 `init` — mapa de funciones (VA real = símbolo `& ~1`)

| VA | Símbolo | Qué hace |
|---|---|---|
| `0x8E8C` | `mount_partition` | `mount(dev,mnt,fstype,flags,data)` con descriptor de 0x14 B; si es **vfat** y `f_bsize*f_blocks ≤ 0x32000` (200 KiB) hace `umount` + `/sbin/dosfsck -Y` + remontar |
| `0x8D1C` | `insmod_drivers` | tablas `{path, opts}` de 8 B |
| `0x92AC` | `check_bootmode` | lee `/proc/udm/upm_bootmode` |
| `0x9088` | `check_mode_file` | parsea `/setting/mode/dmode` (`0 k g d e`) |
| `0x9018` | `check_forced_senser` | `/setting/sen/smode` empieza por `"UU"` y no es BIS ⇒ flag `0x144C4` ⇒ lanza `sen.elf` |
| `0x934C` | `parse_cmdline` | `/proc/cmdline`: busca `console=ttyAM0` ⇒ `/dev/ttycons` en vez de `/dev/console` |
| `0x9568` | `set_oreore_env` | vuelca variables a entorno |
| `0x9600` | `setup_low_memory_killer` | escribe **`-16`** en `/proc/1/oom_adj` (`0xa1be` = `"-16"`) |
| `0x8E34` | `run_bg_process` | `fork` + `execv(path,{path,NULL})` — sin shell |
| `0x96CC` | `main` | 1452 B; secuencia descrita abajo |

**Orden de `main` (VA, `04-init-main-flujo.txt`):**

```
0x96D8  mount_partition(idx0)                 /proc
0x96E4  open /proc/snsc_boot_time, profile_entry("<<init start>>")
        putenv HOME PATH TOPRC MALLOC_OPTIONS LT_ABORTREASON
0x9714  set_stack_size_to_2MB()               setrlimit(RLIMIT_STACK, 2 MiB)
0x9720  check_oreore1 = check_qemu + check_nfs + parse_cmdline      (0x93F4)
0x9728  insmod_drivers(lote1=0x131EC, 5)      devno dmac ldec lld nand
0x9740  mount_partition(0x13484 → 0x13498)    /rootfs  (dnflasha7 → nflasha7, ext2)
0x9756  chdir("/rootfs"); pivot_root; chroot("/rootfs"); move_partition; reopen fds
0x984A  /usr   dnflasha15 ext2 → nflasha15 ext2 → nflasha15 cramfs → nflasha15 vfat
0x9886  mount_partition(idx5)                 /tmp     = nflasha10  vfat  5 MB
0x988C  /system dnflasha3 vfat → nflasha3 vfat
0x98A4  mount_partition(idx2)                 /setting = nflasha2   vfat 13 MB
0x98B6  mount_partition(idx17)                /log     = nflasha11  vfat  6 MB (batch_sync)
0x98BC  mount_partition(idx15)                /lens    = nflasha18  vfat 20 MB
0x98C2  check_oreore2 = check_mode_file                             (0x9408)
0x98DA  write "set" en /proc/udm/drivers       (set_mindrv)
0x9910  insmod_drivers(lote2=0x13214, 33)
0x9918  check_oreore3 = check_bootmode + check_forced_senser        (0x9414)
0x991C  if (BIS) { umount; system("mkdosfs -s 32"); remount; system("/usr/bin/swap_prepare.sh") }
0x995C  if (dmode 'k') LD_PRELOAD=/usr/tool/libkmcsup.so.2.0.0
0x9A4C  if (dmode 'e') LD_PRELOAD=/usr/tool/libsonyefence.so
0x9A5C  elif (dmode 'd') LD_PRELOAD=/usr/tool/libduma.so + DUMA_* + max_map_count
0x9A8C  run_bg_process("/usr/bin/bootin.elf")    (o system() si dmode 'g')
0x9AA6  if (0x144C4) run_bg_process("/usr/bin/sen.elf")
0x9AB2  setup_low_memory_killer()
0x9AB6  if (!ADJUST) run_bg_process("/usr/bin/s_start_android.sh")
0x9AC2  run_bg_process("/usr/bin/net_cmdd.elf")
0x9AC8  profile_entry("<<init end>>")
```

Tablas completas: **montajes** 19 entradas en `0x1331C` y **módulos** 5 + 33 (`03-init-tablas-y-banderas.txt`).
De los 19 descriptores, `main` alcanza **14**; los 5 restantes (`nflasha9` → `/usr/upgrade`, `nflasha23/24/25` y `ms1` → `/log`) están en la tabla pero `main` no los monta.

### 1.2 `ud_wbi_drop.elf` — cómo se invalida el WBI

`us_mkfs.sh` **línea 106**: `ud_wbi_drop.elf $FILE_PARTINF || { echo "[ERROR] ud_wbi_drop.elf" ; getledval.elf 0x68 ; exit $? ; }`
(error LED `0x68` = `ERROR_WBI_DROP`).

El binario (SHA `678d6baf…d3992b`, idéntico en `updater.img` y en `nflasha15/bin/udtrbody.bin`):

* **no importa `ioctl`**: sólo `open`, `write`, `close`, `fopen/fgets/fseek`, `snprintf`, `strlen` (`05-ud-wbi-drop.txt`);
* recorre `partinf.conf`, y por cada partición con tamaño WBI ≠ 0 y no «demasiado pequeño»:
  `snprintf(«/dev/nflasha%d»)` → `open(fd, 0x1002)` → **`memset(buf,0,0x200)`** → **`write(fd,buf,0x200)`**
  (`0x8890`–`0x88A4`).

⇒ **El «drop» es escribir 512 ceros sobre las primera mitad del sector 0 de `/dev/nflasha5`**, que es justo la
cabecera `WBI1` (`magic` en `+0x00`). Después, si el paquete trae `0700_part_image/dev/nflasha5`, el actualizador la
reescribe y el WBI vuelve a ser válido. Si el paquete **no** lo trae, la partición queda con la cabecera a cero y
Loader3 no puede reanudar.

`uc_mkfs.elf -m full` (línea 93) **no** toca `nflasha5`: sólo formatea `nflasha1` y `nflasha2` con `mkdosfs`
(`05-ud-wbi-drop.txt`, anexo 5b). `mount.conf:17` lo declara (`/dev/nflasha5 /wbi wbi 62914560 0`) pero es
descriptivo.

### 1.3 `check_bootmode` — el único que mira el modo

```
0x92C4  open("/proc/udm/upm_bootmode", O_RDONLY)
0x92EE  read(fd, buf, 0x400)
0x92F6  if (!strncmp(buf,"ADJUST",6)) write 1 en 0x144CC      ; ADJUST
0x9306  else if (!strncmp(buf,<0xA06E>,3)) write 1 en 0x144C8 ; 0xA06E = "BIS"
0x9318  close
```

**Sólo dos cadenas: `"ADJUST"` y `"BIS"`** (`0xA067` y `0xA06E`). Consecuencias:

* `0x144CC` (ADJUST) ⇒ `main` **no** arranca Android (`0x9AB6`);
* `0x144C8` (BIS) ⇒ `main` **no** lanza `sen.elf` (`0x9056`) y hace `mkdosfs -s 32` + `swap_prepare.sh` (`0x991C`).

`upm.ko` conoce **nueve** modos (`LDR_BOOT_MODE_COLD, HOT, UPDATER, CIPA, ADJUST, USB_CHARGE, WARM, SS, BIS` +
`ldr_mode2str`, `07-consumidores-productor-bootmode.txt`), pero **`init` no consulta `COLD`, `HOT` ni `WARM`**.
`/proc/udm/upm_bootmode` lo sirve `upm_bootmode_read_proc` de `upm.ko`.

---

## 2. La línea de comandos del kernel: el verdadero conmutador

### 2.1 La cadena literal

`firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/setting/kemco.txt` (SHA `6cbd70f8…5391a79`), líneas 12-16 y
40-42 — idéntica a la de `Kernel command line:` en `analysis/camera-dumps/*/klog.txt` y a
`analysis/camera-dumps/senser-shell-20261020-180946/shell.txt:16`:

```
warm.mode=2
warm.tmo=50000
warm.resume_drop=0
warm.boot_drop=0          ← el drop de arranque queda DESACTIVADO
warm.ignore_drop=1        ← wbi_drop() pasa a ser un NO-OP
cmpr.path=/system/sabin/ssboot.bin cmpr.path2=/system/sabin/ssboot_any.bin
warm.mem_dst=0xC00000@0x9B000000
warm.mem_work=0x600000@0x9C000000
rootfstype=ext2 root=/dev/ram0 init=/sbin/init initrd=0x80628000,8M
```

### 2.2 Los parámetros en el kernel de Sony (que sí está en el repo)

`linux-kernel.tar.gz` → `linux/arch/arm/common/warm.c` (`06-kernel-ssboot.txt`):

```
140: static int resume_drop = 0;        module_param_named(resume_drop, ...)
142: static int wbi_boot_drop = 1;      module_param_named(boot_drop, ...)
144: static int wbi_ignore_drop = 0;    module_param_named(ignore_drop, ...)
414: int wbi_drop(void) { if (!wbi_ignore_drop) ret = _wbi_drop(); }   EXPORT_SYMBOL(wbi_drop);
1301: if (wbi_boot_drop && wb_prev_drop != wb_default_device) __wbi_drop(...)
1223: int cxd_rewrite_wbheader(fver, entry) { memcpy(wbheader.fVersion,fver,4); wbheader.resume_vector=...; }
```

### 2.3 Quién invalida realmente el WBI

`wbi_drop` es un `EXPORT_SYMBOL`. Los módulos que lo **importan** (`07-consumidores-productor-bootmode.txt`):

| Módulo | Importa | Efecto con la cmdline del A6000 |
|---|---|---|
| `upm.ko` | `wbi_drop`, `ssboot_is_rewriting`, `ssboot_is_profiling`, `ssboot_optimizer_stop_profiling` | **inerte** (`ignore_drop=1`) |
| `backup.ko` | `wbi_drop` | **inerte** (`ignore_drop=1`) |
| `nand.ko` | — | no participa |

⇒ **En la A6000 el kernel no invalida nunca el WBI.** El único actor efectivo es `ud_wbi_drop.elf` (§1.2), que
escribe directo al dispositivo y no pasa por `wbi_drop()`. Consecuencia práctica: **quitar el miembro del paquete es
lo único que deja el WBI inválido**, y una vez reescrito sólo se vuelve a invalidar con otra actualización.

### 2.4 Quién produce el WBI: `im.elf`

`/usr/bin/im.elf` (`0xf0f18142…0d803a`), lanzado por `bootin.elf` (cadena `im.elf s &`) y éste sólo por `/sbin/init`
⇒ **`im.elf` sólo se ejecuta en arranque en frío**:

* `0x9FE0`–`0xA03A`: `open("/sys/power/state")` y **`write("warm",4)`** si `0x9F44()!=0` (log `WARM(warm_count=%d)`),
  si no **`write("mem",3)`** (`SUS(warm_count=%d)`) — cadenas `0xC0B7/0xC0C8/0xC0CD/0xC0E1`;
* `0x9F44` compara un contador global; `0x9F68` lo lee e incrementa en el canal de Backup **`0x00940004`**;
* `fn=/system/av-cam.bin load=1 debug=1` (string 292): **`im.elf` es el que carga el firmware del sub-CPU**;
* también hace `dosfsck -Y` / `e2fsck -y` (cadenas `0xC044`, `0xC05D`);
* lee `/proc/udm/upm_bootmode` y compara con `"BIS"` (`0x93B0`–`0x9462`).

El que escribe la instantánea es el kernel: `cxd_create_warmbootimage(entry, adjust_vma)` (`warm.c:1221`) y
`cxd_rewrite_wbheader(fver, entry)` (versión de 4 B + `resume_vector`).

**Cabecera real de `dev/nflasha5`** (`xxd -l 64`): `WBI1`, `numSections=0x48C` (1164), `flag=9`,
`resumeVector=0x800523BC`, `version=0x20060224`, `sectorSize=0x200`, `dataSize=0x0280C600` (41 993 728),
`kernelStart=0`, `kernelSize=0`, `oDataSize=0x0A4FC000` (172 998 656). SHA-256 `fe080cda…f3f04`, 42 293 120 B.

---

## 3. Qué se crea, monta o cambia SOLO en frío

En caliente **no se ejecuta `/sbin/init`**: se reanuda la instantánea (`resumeVector` de la cabecera WBI). Mecanismo
VERIFICADO en `warm.c`; que Loader3 lo use así es **NO_VERIFICADO** (binario ausente) y se apoya en la medición de
G11 §11 (`BootMode 11` con WBI, `BootMode 1` sin él).

| # | Qué | Evidencia | ¿Puede afectar a vídeo/miniatura? |
|---|---|---|---|
| 1 | `/proc` montado antes de todo (`0x96D8`) | tabla idx0 | no |
| 2 | `setrlimit(RLIMIT_STACK, 2 MiB)` sobre `init` | `0x9714` → `0x9658` | no |
| 3 | **`insmod` de 38 módulos en 2 lotes** en un orden fijo | `0x9728`, `0x9910` | **SÍ — ver 3.1** |
| 4 | `/rootfs` (ext2 `nflasha7`) + **`pivot_root`/`chroot`** | `0x9740`–`0x9756` | indirecto (todo el userland) |
| 5 | `/usr` (cadena ext2 → cramfs → vfat sobre `nflasha15`) | `0x984A` | sí (libs y `sabin/`) |
| 6 | **`/tmp` = `nflasha10`, vfat 5 MB**, `dirsync+sync+noatime` | `0x9886`, `partinf.conf` | **SÍ — ver 3.2** |
| 7 | **`/system` = vfat sobre `dnflasha3`/`nflasha3`** | `0x988C` | **SÍ — ver 3.3** |
| 8 | `/setting` (`nflasha2` vfat 13 MB), `/log` (`nflasha11` 6 MB), `/lens` (`nflasha18` 20 MB) | `0x98A4`–`0x98BC` | DMM y NVRAM: ver 3.1 |
| 9 | `echo set > /proc/udm/drivers` | `0x98DA`, literal `0x9D1C`=`"set"` | no |
| 10 | `/proc/1/oom_adj = -16` | `0x9AB2` | no |
| 11 | `bootin.elf` (y con él **`im.elf`**, que carga **`/system/av-cam.bin`**) | `0x9A8C`, `09-…` | **SÍ — ver 3.3** |
| 12 | `/android` = **tmpfs** + `gzip -dc /usr/bin/ramdisk.img \| cpio` + `cgroup memory 113M` + `chroot` | `bin/s_start_android.sh` | no (Android aparte) |
| 13 | `dosfsck -Y` en `mount_partition` para vfat ≤ 200 KiB | `0x8F1E` | **inerte**: ninguna vfat del A6000 baja de 1 MB (`partinf.conf`) |
| 14 | *Sólo BIS*: `mkdosfs -s 32` + `swap_prepare.sh` (compswap 60 MB en `nflasha8`) | `0x9938`,`0x9956` | **no se ejecuta** en arranque normal (modo ≠ BIS) |
| 15 | `/usr/upgrade` (`nflasha9`, tamaño 0) | tabla idx9 | no se monta |

> Corrección al informe hermano: `swap_prepare.sh` **no** corre en todo arranque en frío, sino sólo cuando
> `upm_bootmode == "BIS"` (`0x991C: ldr r3,[0x144C8]; cbz r3,#0x995C`). Por tanto el *compswap* **no** es un
> diferenciador caliente/frío.

### 3.1 `dmm.ko` — el candidato nº 1

`insmod /usr/kmod/dmm.ko DmmConfig=/setting/DmmConfig.bin` (lote2 idx16). En frío el mapa de memoria del
gestor DMM **se reconstruye desde flash**; en caliente **se hereda** de la instantánea. Es el único módulo del
lote 2 con parámetros propios y el único que reparte memoria entre los bloques de medios. **NO_VERIFICADO** en
cuanto a su efecto sobre el decodificador: exige `/proc/meminfo` y `/proc/dmm*` de la cámara.

Los otros 37 módulos no llevan parámetros de interés (sólo `dmac.ko` con `pri_mode_ch_0_3=1 pri_mode_ch_4_7=1`,
`backup.ko` con `Backup_load=0` y `osal_ulogio.ko` con `ulogio_initfile=/setting/ulogio.bin`).

### 3.2 `/tmp` en flash, sólo en frío

`/tmp` es **una partición vfat de 5 MB en `nflasha10`**, no un tmpfs, y sólo existe como montaje tras `/sbin/init`.
En caliente `/tmp` es lo que quedó en RAM. Cualquier componente de medios que reserve buffers temporales en `/tmp`
(la ruta de `im.elf` usa `/tmp/qsi.elf.pid`, `/tmp/lt/…`) ve un `/tmp` distinto según el modo. **NO_VERIFICADO**
para `libmpr`.

### 3.3 La cadena de decodificación — lo más prometedor

Dos hechos firmes:

1. **`/system` es un montaje vfat sobre `nflasha3`** (`0x988C`, `0x989E`) y el **único** firmware del sub-CPU que
   se carga desde ahí es `/system/av-cam.bin` (`im.elf`, string 292), junto con `sabin/ssboot.bin` que la cmdline
   usa como `cmpr.path`. Con `av-cam.bin` caído **no hay ni grabación ni reproducción**; como la grabación
   funciona, este vector queda **descartado**.
2. **El decodificador y el codificador son imágenes distintas** y viven en `/usr/sabin`:
   `sa_avcd_compatible_zma.bin`, `sa_avcd_performance_zma.bin` (decode AVC),
   `sa_avce_performance_zma.bin`, `sa_avce_quality_zma.bin`, `sa_avce_performance_plus_zma.bin` (encode AVC),
   `sa_jpeg_dec_1core.bin`, `sa_jpeg_dec_1unit.bin`, `sa_jpeg_enc_*` (miniatura), `sa_dcv.bin`,
   `dcv_psf_table_movie.bin`. **Ningún CFW de esta cadena toca `/usr/sabin`** (`build_cfw_completo.build_files`
   sólo sustituye `lib/libObj.so`, `lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so` y
   `share/app/*.uxc` → `09-subcpu-y-alcance-parches.txt`). Es decir, las imágenes del decodificador son las de
   Sony y no las ha tocado ningún parche.

Encaja con el síntoma (grabar sí, reproducir y miniatura no) **siempre que** el fallo esté en *programar* el
decodificador con esas imágenes, no en las imágenes en sí. Y el momento de programarlas es el arranque. Pero la
misma secuencia la ejecuta el 3.21 oficial. **NO_VERIFICADO**: no hay ningún dato estático que separe «programar el
decodificador» en caliente de en frío, más allá de que en caliente el sub-CPU **ya viene programado** dentro de la
instantánea y en frío hay que reprogramarlo desde cero.

Discriminador barato la próxima vez que haya cámara: en un arranque en frío con el CFW, mirar en el `klog` si
`im.elf` completó la carga de `/system/av-cam.bin` y qué `sa_*.bin` de `/usr/sabin` se programaron; y comparar
`/proc/meminfo` y el mapa de `dmm.ko` entre un arranque caliente (3.21 oficial) y uno frío (CFW).

### 3.4 Lo que **no** cambia

* Mismos ficheros de `/usr` (la partición está en flash, no en la instantánea en cuanto a contenido lógico).
* Ningún script consulta `COLD`/`HOT` (§1.3), así que **no hay ninguna rama de código que se active sólo en frío**.
* `sen.elf` (que corre porque `us_mkfs.sh:124-129` escribe `"UU"` en `/setting/sen/smode` en **toda**
  actualización, tanto en `fmode=app` como en `full`) sólo contiene la cadena `LoadSenserMode`; no carga
  `av-cam.bin`.

---

## 4. Discriminación: qué vector del arranque puede explicar el síntoma doble

El síntoma es **grabar sí, reproducir no, miniatura no** (y «Recuperar BD imág.» no lo arregla). Ordenados por
cuánto explica cada uno, con lo que se sabe:

| Vector (sólo-frío) | ¿Explica grabación OK + reproducción KO? | ¿Explica que falte la miniatura? | Confianza |
|---|---|---|---|
| `dmm.ko` reconstruye el mapa de memoria desde `/setting/DmmConfig.bin` (§3.1) | sí: el decodificador puede quedarse sin memoria mientras el codificador sí la obtiene | indirecta (la miniatura la extrae el decodificador) | **MEDIA**; NO_VERIFICADO |
| `/tmp` pasa de RAM a vfat 5 MB en `nflasha10` (§3.2) | posible si `libmpr`/`im` reservan buffers en `/tmp` | no directa | **BAJA-MEDIA**; NO_VERIFICADO |
| Reprogramación del sub-CPU desde cero (§3.3) | sí en teoría; pero es lo mismo que hace el 3.21 oficial, que sí reproduce | sí: `sa_jpeg_dec_*` no depende del codificador | **BAJA** como causa aislada |
| `/system` sin montar ⇒ sin `av-cam.bin` (§3.3) | **no**: sin `av-cam` tampoco grabaría ⇒ **descartado** | — | descartado |
| `swap_prepare.sh` / compswap (§3 fila 14) | **no**: sólo corre en BIS | — | descartado |
| `dosfsck -Y` de `mount_partition` (§3 fila 13) | **no**: ninguna vfat del A6000 es ≤ 200 KiB | — | descartado |
| Ausencia de una rama de código sólo-frío (§1.3, §3.4) | — | — | **descartado**: no existe tal rama |

Ninguno de estos vectores está **medido** en cámara; la tabla ordena el trabajo, no concluye. El discriminador
barato sigue siendo el de E1 del informe de auditoría (log de `im`/`libmpr` y un breakpoint en `0x437C0A`/`0x437C3C`),
más ahora `/proc/meminfo` y el mapa de `dmm.ko` en caliente (3.21 oficial) frente a frío (CFW).

---

## 5. El arreglo: comando exacto

### 5.1 La maquinaria ya existe

`scripts/gui/build_package_nflasha15.py` (86 líneas) **ya sabe** conservar el WBI:

```python
def main(new15, out, base_tar, version, darwin_v3=False, sin_wbi=False):   # línea 33
    ...
    if sin_wbi:   # sin nflasha5 el WBI queda invalidado por ud_wbi_drop (us_mkfs.sh) y Loader3 arranca en frío
        lines = part_sum.splitlines(keepends=True)
        part_sum = "".join(ln for ln in lines if not ln.rstrip().endswith(",dev/nflasha5,"))
    repl = {NFLASHA15: blob, build.PART_SUM: part_sum.encode("ascii")} | ({NFLASHA5: None} if sin_wbi else {})
```

`sin_wbi=False` **es el valor por defecto**: sin el flag, `nflasha5` y su línea de `part_image.sum` **no se tocan**.
El 3.93 instalado se construyó **con** `--sin-wbi` (`build/cfw_func393/base/pkg-3.93/container.json`:
`"sin_wbi": true`, `tar_quitados_vs_base = ["0700_part_image/dev/nflasha5"]`), y `build_cfw_completo.py:97` lo
llama con `sin_wbi=True` **codificado en duro**.

Los cuatro tars base del repo **traen** `nflasha5`, y con el **mismo** SHA-256 de Sony, y con su línea de suma
(`08-maquinaria-y-riesgo.txt` §8.4):

| tar | nflasha5 | SHA-256 | línea de `part_image.sum` |
|---|---|---|---|
| `firmware/extracted/fw321/firmware.tar` | sí | `fe080cda…f3f04` | `0,9cb10112,02855780,…,dev/nflasha5,` |
| `analysis/e25-27/artifacts-338/firmware.integrated.tar` | sí | idem | idem |
| `analysis/gui/g22/base-380.tar` | sí | idem | idem |
| `build/cfw_func393/base/base-film.tar` | sí | idem | idem |

### 5.2 Comando

```bash
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter

.venv/bin/python3 scripts/gui/build_package_nflasha15.py \
  build/cfw_func393/base/nflasha15-393.bin \
  build/cfw_func393/base-wbi \
  --base-tar build/cfw_func393/base/base-film.tar \
  --version 3.94 \
  --darwin-v3
```

**Sin `--sin-wbi`** (esa es toda la diferencia con el 3.93). Produce
`build/cfw_func393/base-wbi/pkg-3.94/package-3.94/firmware_packed.dat` y su `container.json` con
`"sin_wbi": false`. La versión tiene que ser **mayor** que la instalada (`--version` por defecto es `3.39`; el
actualizador sólo acepta versiones mayores).

Si el `/usr` instalado no coincide con `nflasha15-393.bin`, se regenera antes con:

```bash
.venv/bin/python3 scripts/gui/build_nflasha15.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 \
  build/cfw_func393/base/files \
  build/cfw_func393/base-wbi/nflasha15-394.bin
```

y se pasa ese como primer argumento.

> **La otra mitad de la cadena (`build_base_pp.py`) sigue haciendo falta** si se quiere el `nflasha3` parcheado del
> 3.93: `build_package_nflasha15.py` sólo sustituye `/usr` + sumas + Darwin v3 sobre el tar base. El `base-film.tar`
> **ya lleva** ese `nflasha3` (11 489 280 B, SHA-256 `1de903f3…`, frente a los 11 489 040 B / `93d4a1f0…` del
> `nflasha3` de Sony; `build/cfw_func393/base/build-base.json`: 369 bloques TPZL, 107 bytes cambiados), así que el
> comando de arriba reproduce el paquete instalado cambiando únicamente el WBI.

### 5.3 Verificación (`--dry-run`: **no existe**)

`grep -rn -- '--dry-run' scripts/` no devuelve **nada** en la cadena de empaquetado (las apariciones están en
`camera_filmpb1_trace.py`, `filmpb1_convertir_clips.py` y `agent/bootstrap.sh`). `build_package_nflasha15.py` sólo
tiene `nflasha15`, `salida`, `--base-tar`, `--version`, `--darwin-v3` y `--sin-wbi` (`08-…` §8.2).

Se ha hecho un *dry-run* equivalente que ejecuta **todos** los pasos de `main()` salvo escribir
`firmware.tar` + `firmware_packed.dat` (`reports/evidence/…/dry-run-wbi.py`). Resultado
(`dry-run-wbi.out`): **20/20 comprobaciones OK**, entre ellas

* `base_tar` contiene `0700_part_image/dev/nflasha5` (42 293 120 B, SHA-256 `fe080cda…f3f04`), y es **idéntico** al
  `dev/nflasha5` desempaquetado del fw321;
* su línea de `part_image.sum` (`0,9cb10112,02855780,…`) **verifica** por CRC-32 y tamaño;
* con `sin_wbi=False` sólo se reescriben **2** miembros (`dev/nflasha15` y `part_image.sum`) y el tar conserva sus
  **105** miembros, con `nflasha5` intacto y su suma válida;
* con `sin_wbi=True` desaparecen el miembro y la línea (lo que se instaló);
* `--darwin-v3` es aplicable sobre esta base.

Reproducible con:

```bash
.venv/bin/python3 reports/evidence/film-pb-1-sub-arranque-wbi-20261128/dry-run-wbi.py
```

**No se ha construido ningún DAT.** Instalarlo es una acción sobre la cámara y no está autorizada en esta tarea.

---

## 6. Riesgo de conservar el WBI (lo que documenta el proyecto)

1. **El WBI reinyecta el `/usr` de Sony y deja el CFW inerte.** Es literalmente el criterio con el que se descartó
   esta vía: [auditoría del CFW, §4 fila E4](film-pb-1-auditoria-cfw-20261127.md) — *«El WBI reinyecta el `/usr`
   de Sony y el CFW queda inerte (motivo documentado por el que se quita)»* — y el párrafo siguiente:
   *«el WBI es una instantánea de RAM con el `/usr` de Sony»*.
   Base técnica: en caliente `/usr` se sirve con el **TOC archivado en `0x8D3B8000`** y las páginas de caché
   ([G11 §11.2](../docs/gui/g11-auditoria-307-nflasha15.md), 282 de 2377 páginas de 4 KiB muestreadas); en frío el
   ext2 se monta y se relee del flash. Por eso *«cambiar `/usr` exige invalidar el WBI»* (G11 §11, línea 231) y
   *«en caliente los parches de `/usr` no se cargan nunca»* ([sub-wbi §2.2](film-pb-1-sub-wbi-20261127.md)).
2. **Mezcla incoherente.** Si el índice archivado no coincide con el ext2 que hay en flash, el sistema ve metadatos
   viejos con datos nuevos. El informe hermano lo resume: *«cualquier byte que mueva el índice da la mezcla peor»*,
   con **riesgo BAJO-MEDIO** y el dato de que el `nflasha15` recompuesto dio 0/4 frente a 3/3 con el de Sony
   ([sub-wbi §4a](film-pb-1-sub-wbi-20261127.md)). Aquí el `nflasha15` **es distinto**: 84 611 584 B frente a
   84 042 977 B del de Sony (`dry-run-wbi.out`).
3. **El WBI lleva el kernel** (`0x80038000`, idéntico a `nflasha3/vmlinux.bin`): no hay restauración «parcial» de
   solo `/usr`. Quitar páginas del TOC deja estructuras del kernel apuntando a memoria no restaurada
   ([sub-wbi §4b](film-pb-1-sub-wbi-20261127.md), riesgo ALTO, NO_VERIFICADO si Loader3 tolera secciones ausentes).
4. **Coste de equivocarse.** Una instantánea incoherente puede colgar la reanudación; la salida es R48 + un paquete
   con el `/usr` de Sony y versión mayor.
5. **Dato nuevo de este informe** (§2.3): como `warm.ignore_drop=1` deja `wbi_drop()` inerte, **una vez reescrito
   el WBI ya no se puede invalidar desde el sistema**; sólo otra actualización con `ud_wbi_drop` lo hace. Para
   experimentar eso es cómodo (el modo es reproducible), pero también significa que no hay marcha atrás «en
   caliente» si la mezcla sale mal.

**Lectura conjunta:** el comando de §5.2 produce exactamente el paquete que el proyecto ya identificó como
«arreglo definitivo con la pega conocida» (E4). Su resultado esperado, tal cual está documentado, es **arranque en
caliente con el `/usr` de Sony**, no con el `/usr` del CFW. Para tener caliente **y** CFW haría falta que la cámara
**regenere** su propio WBI después de instalar (mecanismo existe: `im.elf` → `/sys/power/state=warm` →
`cxd_create_warmbootimage`), lo que **NO está verificado** y de hecho no se observa (la cámara arranca en frío).

---

## 7. Límites (NO_VERIFICADO)

* **Loader3** (binario ausente): `chk ssboot` `0xC01F20F4`, los literales `0xC01F2BC6`/`0xC01F2BE6`/`0xC01FBF0E` y
  `BootMode 11` vienen de volcados SWD de [G11 §11.1](../docs/gui/g11-auditoria-307-nflasha15.md), no de este
  análisis.
* Que en caliente **no** se ejecute `/sbin/init`: verificado el modelo suspend/resume en `warm.c` (`resume_vector`),
  **inferido** para Loader3.
* Efecto de `dmm.ko` y del reparto de RAM en el decodificador (§3.1): sin acceso a `/proc` no se puede medir.
* Cuándo y con qué condiciones escribe `im.elf` `warm` en `/sys/power/state` (la compuerta `0x9F44` depende de un
  contador del Backup `0x00940004` cuya semántica exacta no se ha reconstruido).
* `warm.mode=2`, `warm.tmo=50000`, `warm.mem_dst`, `warm.mem_work`, `cmpr.*`, `wbimem=…`: leídos de la cmdline y de
  `kemco.txt`; **no** se ha trazado su interpretación en el kernel.
* Los 19 descriptores de montaje de `0x1331C` incluyen `nflasha9/23/24/25` que `main` no usa: la tabla es más
  grande que el uso y no se ha identificado quién usa el resto.
* `uc_mkfs.elf` con `-m full`: se ha comprobado que sólo formatea `nflasha1`/`nflasha2`, pero **no** se ha
  desensamblado para ver si además escribe cabeceras de WBI.
* No se ha re-verificado la muestra «282 de 2377 páginas» de G11 §11.2.

---

## 8. Reproducibilidad

```bash
# Desensamblador usado (Thumb + .symtab + simbolización de literales PC-relativos):
#   /tmp/thumbdis.py  (Capstone 5 de .venv; los símbolos Thumb van impares: el VA real es value & ~1)
INIT=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/sbin/init
.venv/bin/python3 /tmp/thumbdis.py "$INIT" dis 0x92ac 0xa0          # check_bootmode
.venv/bin/python3 /tmp/thumbdis.py "$INIT" dis 0x96cc 0x5ac         # main
.venv/bin/python3 /tmp/thumbdis.py "$INIT" dis 0x8e8c 0x16c         # mount_partition
.venv/bin/python3 /tmp/thumbdis.py firmware/extracted/fw321/updater.img_unpacked/bin/ud_wbi_drop.elf dis 0x8864 0x50
.venv/bin/python3 /tmp/thumbdis.py firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/bin/im.elf dis 0x9fe0 0x7c

# Kernel de Sony (ssboot / warm boot)
mkdir -p /tmp/ssboot && tar xzf linux-kernel.tar.gz -C /tmp/ssboot \
  linux/kernel/power/ssboot linux/arch/arm/common/warm.c linux/include/linux/ssboot.h
sed -n '138,146p;414,441p;1301,1305p' /tmp/ssboot/linux/arch/arm/common/warm.c

# Línea de comandos real
grep -nE 'warm|wbi|cmpr' firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/setting/kemco.txt

# Dry-run del paquete con WBI
.venv/bin/python3 reports/evidence/film-pb-1-sub-arranque-wbi-20261128/dry-run-wbi.py
```

### Ficheros de evidencia

| Fichero | Contenido |
|---|---|
| `01-hashes.txt` | SHA-256 de todo lo analizado; `us_mkfs.sh` y `ud_wbi_drop.elf` idénticos en `updater.img` y en `nflasha15-udtrbody` |
| `02-init-desensamblado.txt` | `.symtab` de `init` + `check_bootmode`, `check_oreore1/2/3`, `parse_cmdline`, `check_forced_senser` |
| `03-init-tablas-y-banderas.txt` | 19 descriptores de montaje, 38 módulos con opciones, mapa de banderas `0x144B8…0x144EC` con xrefs |
| `04-init-main-completo.txt` / `04-init-main-flujo.txt` | `main` completo / resumen de llamadas y saltos |
| `05-ud-wbi-drop.txt` | `us_mkfs.sh` con líneas, imports de `ud_wbi_drop.elf`, `.text` entero, `mount.conf:17`, `uc_mkfs.elf` |
| `06-kernel-ssboot.txt` | `warm.c` (parámetros, `wbi_drop`, `cxd_rewrite_wbheader`), `kemco.txt`, inventario del driver `ssboot` |
| `07-consumidores-productor-bootmode.txt` | `im.elf` (bootmode, `/sys/power/state`, contador de Backup), imports de `upm.ko`/`backup.ko`/`nand.ko`, modos `LDR_BOOT_MODE_*` |
| `08-maquinaria-y-riesgo.txt` | inventario de scripts, opciones reales (sin `--dry-run`), los 4 tars base con su `nflasha5`, `container.json` del 3.93, citas del riesgo |
| `09-subcpu-y-alcance-parches.txt` | `im.elf` → `/system/av-cam.bin`; `bootin.elf` → `im.elf s &`; alcance real de los parches (`lib/` y `share/app/`); `/usr/sabin` intacto |
| `dry-run-wbi.py` / `dry-run-wbi.out` | el *dry-run* y su salida (20/20 OK) |
