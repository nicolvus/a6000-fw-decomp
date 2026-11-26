# FILM-PB-1 (sub) — ¿Puede la retirada de `nflasha5` (WBI) romper la reproducción de vídeo?

Fecha: 27-11-2026. Estático; cámara no accesible (sin red, USB ni `adb`). Continúa [la auditoría del
CFW](film-pb-1-auditoria-cfw-20261127.md) (H1 = arranque en frío). **Direcciones:** los VA de `libmpr.so`/`libObj.so` son **ELF (base 0)**
(REA ve `libmpr` como *ELF + 0x10000*); los `0xC01Fxxxx` son **VA de ejecución de Loader3** leídos por SWD (el binario del loader no está
en el repo).

## 1. Qué es `nflasha5` y quién lo consume

`0300_partconf/partinf.conf:25` lo etiqueta literalmente: `# /dev/nflasha5 60MB(System Group Warm Boot Image /dev/nflasha5)`. Fila 5 de la
tabla BOS: `0x3B40000`, 60 MiB, **tipo 2** ([R14 §6](../docs/capture/e26-r14-ramcfg-bos-analysis.md)). Imagen 3.21: 42 293 120 B, SHA-256
`fe080cda…f3f04` ([firmware-analysis.md:13](../docs/firmware-analysis.md)).

**Firma y estructura (VERIFICADO con `xxd`).** `WBI1`, `numSections=1164`, `flag=9` (bit0 comprimido), `resumeVector=0x800523BC`,
`version=0x20060224`, `sectorSize=0x200`, `dataSize=41 993 728`, **`kernelStart=0`, `kernelSize=0`**, `oDataSize=172 998 656`. Esquema en
`references/fwtool/fwtool/sony/wbi.py:14-46` (`WbiHeader`/`WbiSectionHeader`: `addr`, `size`, `checksum`, `virt`) ⇒ **no es un sistema de
ficheros: es un volcado de RAM física por rangos** (`reports/wbi-sections.json`: 1164 secciones, 172 998 656 B, física
`0x80021000`–`0x96830000`, 1044 tramos disjuntos).

| Quién lo lee / invalida | Evidencia |
|---|---|
| Loader3: `chk ssboot` `0xC01F20F4`, lee `0xC01F2BC6`/`0xC01F2BE6`/`0xC01FBF0E`, elige **BootMode 11** en `0xC01F212A` | [G11 §11.1](../docs/gui/g11-auditoria-307-nflasha15.md) |
| RAMCFG modo `0x4000000` (caliente) carga **solo** `idt_cam.bin` y `av-cam.bin`; `0x1000000` (frío) los seis | [R14 §5](../docs/capture/e26-r14-ramcfg-bos-analysis.md) |
| `us_mkfs.sh:106` ejecuta `ud_wbi_drop.elf $FILE_PARTINF` (error `0x68`, línea 6) en **toda** actualización | `fw321/updater.img_unpacked/bin/us_mkfs.sh` |
| `ud_wbi_drop.elf` recorre `partinf.conf` y abre `/dev/nflasha%d` («%s wbi_drop», «wbi size is zero. skip») ⇒ **no depende del tar** | strings del ELF, off. `0xc60`–`0xd6d` |
| Luego el actualizador reescribe `0700_part_image/dev/nflasha5` del paquete ⇒ WBI válido otra vez | [G11 §11.3](../docs/gui/g11-auditoria-307-nflasha15.md) |
| El paquete 3.93 instalado **no trae** ese miembro | `build/cfw_func393-pp.audit.json:tar_quitados_vs_base` |

Medición apareada en cámara: 3.48 (con WBI) `BootMode: 11` (`analysis/camera-dumps/20261108-swd-348/loader-log-*.txt:75`); 3.52 (sin
`nflasha5`) `BootMode: 1` + `LD3:Run Config(load:1000000)` (`analysis/camera-dumps/20261108-swd-352/loader-log-0xc0060000.txt:74,145`).

**Contenido, comprobado sobre el mapa físico de las 1164 secciones.** En **`0x80038000`** (carga de `vmlinux.bin`) los bytes son
**idénticos** a `nflasha3_unpacked_unpacked/vmlinux.bin` (64/64 B) ⇒ la instantánea **lleva el kernel** (de ahí `kernelStart=0`). El TOC
TPZL de `nflasha15` (bytes `0x18…` de la partición) aparece **una sola vez**, en **`0x8D3B8000`** (`0912-8d3a4000.bin`), página alineada ⇒
lleva el **índice de `/usr`**. **`0x83541000` (`av-cam.bin`) y `0x83501000` (`idt_cam.bin`) NO están cubiertos** ⇒ el loader los recarga
en *ambos* modos (coincide con la máscara `0x4000000`).

## 2. Qué se pierde con el arranque en frío

1. **El kernel que corre.** En caliente es el archivado en `0x80038000` (Sony 3.21), no el de `nflasha3`: los
   parches de núcleo del CFW son **inertes** en caliente y solo actúan en frío.
2. **Índice y caché de `/usr`.** En caliente `/usr` se sirve con el TOC de `0x8D3B8000` y las páginas
   archivadas (282 de 2377 de 4 KiB muestreadas, [G11 §11.2](../docs/gui/g11-auditoria-307-nflasha15.md)); en frío el
   ext2 se monta y **se relee del flash**. Por eso «cambiar `/usr` exige invalidar el WBI»: en caliente los
   parches de `/usr` **no se cargan nunca**.
3. **Estado de los procesos.** En caliente no corre `/sbin/init`; en frío sí (`init` → `insmod` →
   `pivot_root` → `bootin.elf`/`sen.elf`/Android, [e24-01](../docs/capture/e24-01-arranque-recuperacion.md)). No hay
   **ningún módulo ni proceso exclusivo del WBI**: mismos 37 módulos, solo `wlanMemoryAllocator` extra
   ([G111 §14](../docs/gui/g111-film-receta-gui-iconos.md)).
4. **Mapa de RAM/DMM heredado** (`DmmConfig=/usr/share/dmm/DmmConfig.bin` en 0082/0099,
   [G111 §14.1](../docs/gui/g111-film-receta-gui-iconos.md)); en frío lo reconstruye `dmm.ko`. Y **tiempo**: ~3 s
   ([camera-reset-logs.md:11](../docs/capture/camera-reset-logs.md)) más el «error de cámara» del primer encendido del
   3.52, sin explicar ([G11 §12](../docs/gui/g11-auditoria-307-nflasha15.md)). **No** se pierde el firmware ARM7 (§1).

## 3. ¿Deja la falta de WBI sin inicializar el camino de decodificación?

**No (confianza ALTA en lo estático).** Lo único que la capa de medios sabe del modo de arranque:

| Elemento (VA ELF) | Qué hace | ¿Alcanza a reproducción? |
|---|---|---|
| `MprIf::SnapShotBootInit` **`0x71CE64`** (36 B) → `0x712010` | copia 13 B del param y escribe solo `0x00AD28F8` (nombre ≤12), `[0x00AD2920]=param[1]`, `[0x009DF380]=param[2]`, `[0x00AD3538]=param[0xC]` | no |
| `MprIf::Create` **`0x712530`** | escribe **el mismo** `0x00AD28F8` (+0xD, +0x28, +0xC30/+0xC34/+0xC38) ⇒ **superconjunto** | no |
| Lectores de esos globales | `MprIfMcmd::DebugDispInfo` `0x72AAB4`/`0x72AE46`, `DebugSetSerialNumber` `0x729C5A`, `DebugSetGpsModuleExist` `0x729618` ⇒ **S/N y flag GPS** | no |
| `MPR::BootType` | 2.º word del mensaje `0x10000002` que arma `MMgrCtrl::Resume` **`0x66221C`** («Resume : bDrivePowerOff = %d») ⇒ gestor de medios | no |
| `libObj` `0x7E6956` / `0x7E6F6A` | únicos llamadores de `MprIf::Resume(bool,BootType)`: **1 (HOT)** y **3 (SNAP)** (este tras `SnapShotBootInit`, `0x7E6F54`) | API de servicio, no `PlayMovie` |
| `" Snapshotboot mode"` `0x8F74B1` / `" Hotboot mode"` `0x8F74C5` | manejador `0x651AA8`, ayuda `"Resume <bDrivePowerOff : true/false> <HOT\|SNAP>"` (`0x8F7446`/`0x8F747B`): comando manual | no |
| `FUN_00437BC0` **`0x437BC0`** | guardas A (`0x447A1E`, «dsm») y B (`0x447F26`), `MoviePlayerIf::PbStart` `0x307F54`: **no consulta el modo** | — |

`MprIf::SnapShotBootInit` tiene **un solo llamador** en `libObj` (`0x7E6F54`) y **ninguno** en `libmpr` (barrido de todos los `BL`/`BLX`
de `.text`). Y el frío es lo que hace **efectivos** los parches de `/usr`, no lo que los oculta (§2.2).

**Veredicto sobre H1.** La falta de WBI **no** puede explicar el `0x1A` por «inicialización ausente» del camino de decodificación. Queda
un vector no modelado: la RAM/DMM disponible, que en caliente se hereda y en frío se reconstruye. Confianza **MEDIA** en que el frío sea
irrelevante en conjunto: (a) ese vector no se ha medido nunca; (b) la única bisección en cámara (4.02 vs 4.03) **no lo separa**, ambas van
sin `nflasha5` ([G111 §14](../docs/gui/g111-film-receta-gui-iconos.md)). Discriminador barato: log de MPR o breakpoints en
`0x437C0A`/`0x437C3C`/`0x437CFC` y, si no, el 3.21 oficial (E3).

## 4. Vías para CFW + arranque en caliente

**(a) Conservar `nflasha5` con el `/usr` de Sony intacto — VIABLE, la única limpia.** Base: tar con `nflasha3` parcheado (av-cam/Darwin) y
`nflasha15` = **partición original de Sony byte a byte** (así el TOC de `0x8D3B8000` y la caché siguen valiendo);
`build_package_nflasha15.main(dev/nflasha15, …, base_tar=<tar con nflasha3 parcheado>, darwin_v3=True)` **sin** `--sin-wbi`
(`scripts/gui/build_package_nflasha15.py:33-44`; la base con núcleo parcheado la produce `build_base_pp`, `build_cfw_completo.py:95-97`).
Conserva: caliente (~3 s), `av-cam` (Film/Silent/EFCS) y Darwin v3. Pierde **todo el userland** (eco de `libObj` `0x686DE6`,
`viewUnified2`, `CautionConfig`, `.uxc`) ⇒ sin menús Silent/PP. Riesgo **BAJO-MEDIO**: mecanismo documentado (0/4 con `nflasha15`
recompuesto frente a 3/3 con el de Sony), pero cualquier byte que mueva el índice da la mezcla peor.

**(b) Invalidar solo la parte `/usr` de la instantánea — NO VIABLE.** (i) El loader restaura por dirección física: quitar la página del
TOC (`0x8D3B8000`) o páginas de caché deja estructuras del kernel archivado apuntando a memoria no restaurada; (ii) aunque se quitaran, en
caliente **ningún proceso relee `/usr`**: las `.so` de Sony ya están mapeadas en los procesos archivados y no se pueden re-ejecutar; (iii)
el WBI lleva el propio kernel (`0x80038000`), luego no hay restauración «parcial» conocida. Riesgo **ALTO**; NO_VERIFICADO si Loader3
tolera secciones ausentes.

**(c) Que la cámara regenere el WBI con el `/usr` del CFW — POSIBLE, NO DEMOSTRADO.** Hay utillaje de instantánea: `upm.ko` expone
`wbi_drop`, `upm_senser_wbi_drop`, `ssboot_is_rewriting`, `ssboot_is_profiling`, `ssboot_optimizer_stop_profiling`, `LDR_BOOT_MODE_WARM`;
`nflasha3` trae `/sabin/ssboot.bin` (11 280 B) y `ssboot_any.bin` (9 648 B); la línea de arranque usa `cmpr.path=/system/sabin/ssboot.bin`
([e24-01:79](../docs/capture/e24-01-arranque-recuperacion.md)); `libSyncAndroid.so` referencia `/setting/first_ssboot`. Si funciona, un frío con
el CFW generaría su propio WBI y el **siguiente** sería caliente con `/usr` parcheado. Estado: **NO_VERIFICADO** (nunca observado; [G11 §12](../docs/gui/g11-auditoria-307-nflasha15.md) lo dejó abierto y los «arranques algo más rápidos» no son prueba). Riesgo **ALTO**: una
instantánea incoherente puede colgar la reanudación; recuperación por R48 + paquete con `/usr` de Sony y versión mayor.

**(d) Statu quo**: CFW 3.93 en frío. Sin riesgo nuevo; cuesta ~3 s y el «error de cámara» del primer encendido.

## 5. Límites (NO_VERIFICADO)

Loader3 a nivel de byte (binario ausente; `0xC01F20F4`/`0xC01F212A` vienen de volcados SWD) · que `idt_cam`/`av-cam` queden fuera del WBI
*por diseño* (la ausencia de cobertura es un hecho medido; la causa se infiere de la máscara `0x4000000`) · la muestra «282 de 2377
páginas» es de G11 §11.2, no re-verificada aquí (sí el TOC en `0x8D3B8000`) · que exista ruta de **escritura** del WBI (solo nombres de
símbolos, sin llamadores) · DMM/RAM libre por modo (sin `/proc/meminfo`).

## 6. Reproducibilidad

`xxd -l 64 …/dev/nflasha5`; mapa físico y cobertura en `reports/wbi-sections.json`; desensamblado, símbolos y xrefs con `python3 /tmp/elfhelper.py <lib.so> dis|sym|str|xref|calls …` (Capstone 5 de `.venv`), más barrido
propio de `BL`/`BLX` y `ldr [pc]`; firmas de `/usr` con `strings -a`.
