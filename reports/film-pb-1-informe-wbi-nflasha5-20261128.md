# FILM-PB-1 — Informe consolidado: WBI, `nflasha5`, `/setting` y recuperación por SWD (27-28-11-2026)

Etiquetas: **MEDIDO** (en la cámara o en un volcado de esta sesión), **VERIFICADO** (contra bytes/código), **INFERENCIA**, **NO PROBADO**.
Sesión de Claude Code. Commits locales (sin push): `cbf72b4e`, `460c082c`, `933b600f`, `ab5e2fed`, `427d9e61`, `b577b588` y el de este informe.

## 0. Resumen en diez líneas
1. Objetivo: **Silent Shooting con el menú del CFW y reproducción de vídeo a la vez**. El vídeo solo funciona si la cámara arranca en caliente (WBI en `nflasha5`); el menú Silent vive en `/usr`, que el WBI de Sony congela.
2. El `.dat` que no instalaba (4.05/4.06 «Silent vía av-cam») era válido; el fallo era `/setting` llena (0x1043). **Cerrado.**
3. La receta de Vibe (apagar con el interruptor para que la cámara regenere el WBI) **no funciona**: el interruptor entra en modo 0 y escribe `"mem"`.
4. El ritual de fábrica (tipo 8, factor `0x27`) sí se puede forzar por SWD o parcheando `im.elf` en RAM. Sus bloqueos: la app `tweak` retenía `/android/data` (EBUSY) y `make_init_bk.sh` llena `/setting`.
5. Con esos bloqueos resueltos, la cámara **sí escribe una imagen en `nflasha5`**, pero con firma `prof` y tomada **a mitad del apagado**.
6. Instalada con firma `WBI1` (paquete 4.07), la cámara la reanuda (`WARMBOOT`) y vuelve a apagarse: **negro**. **No sirve.**
7. Tras reanudar, la cámara **no reescribe** `nflasha5` (volcado posterior idéntico): la hipótesis «dos fases de SSBOOT» no se sostiene.
8. Mezclar con el WBI de Sony: viable solo para `im.elf` y `libObj.so` (mismo tamaño); inviable para `viewUnified2.so` (+2,27 MB), `CautionConfig.so` (+196 KB) y los `.uxc`.
9. Fabricar el `nflasha5` del CFW en el PC: no es posible, es una foto de RAM de un sistema en marcha.
10. Estado: cámara con el 4.07 (negro); recuperación con el 4.08 sin WBI **construida y verificada en el PC, sin comprobar en la cámara**.

## 1. Auditoría del `.dat` que no instalaba (27-11)
- Paquetes 4.05/4.06 («Silent vía av-cam»): contenedor, CRC, modelo, updater 3.21 y 65 sumas **verificados**; solo difieren del control 4.02 en `darwin_core`, `nflasha3`, `nflasha15` y sumas.
- Afirmaciones **refutadas** (`reports/film-pb-1-auditoria-silent-avcam-20261127.md`): «WBI de Sony intacto» (`ud_wbi_drop.elf` borra la cabecera en toda instalación, `us_mkfs.sh:106`); «`pkt[0x0E]` no afecta al disparo»; «sin cortinilla» (faltaban la compuerta de Darwin y R86: `ShutMode=0` + `r5`). El parche de 86 B solo desactiva el EFCS.
- Causa del `0x1043` (CAM-SETTING-1, **MEDIDO**): `/setting` (`nflasha2`, vfat de 13,6 MB, 830 clústeres) al 100 %, `init_bk.bak` = 6 815 744 B (fábrica 1 346 048) por `make_init_bk.sh` cortado. El actualizador en modo app no formatea ni pasa `dosfsck`. Arreglo: `rm /setting/init_bk.bak` desde la shell del actualizador → `Done`. Runbook: `docs/runbook-setting-llena.md`; shell: `scripts/cam/ushell.py`.
- Se **repitió** el 28-11: el ritual de apagado vuelve a crear `init_bk.bak` de 6 815 744 B (el `tar` de `/android/data` no cabe) y causa otro `0x1043` al 95-99 %.

## 2. Cómo decide `im.elf` el apagado (VERIFICADO + MEDIDO)
- El interruptor da factor `0x7` → tipo 1 / modo 0 → escribe `"mem"` en `/sys/power/state`. El parche `0x9F44` de Vibe (`movs r0,#1; bx lr`) es inerte para el interruptor.
- Factor `0x27` → tipo 8 / modo 2 → escribe `"warm"`; solo el tipo 8 hace `unlink bk2.bak`, `make_init_bk.sh` y `umount_ad`.
- Forzar `0x27`: (a) SWD, breakpoint hardware en `im.elf@0xA130` en los 4 núcleos (`reports/evidence/film-pb-1-ssbi-20261126/swd-imelf-offfactor-0x27.cfg`, convierte `r3`); (b) parche en RAM de 2 B en `0xA12A` (`ldr r3,[r4,#4]` → `movs r3,#0x27` = bytes `27 23`) vía `/proc/<pid>/mem` con `dd` sin `conv=notrunc`. Ambos hicieron que la cámara entrara en el ritual (`Sus(8)`, `im_type=8`).
- Quién retenía `/android/data` (EBUSY, **MEDIDO**): `nmemories.tweak` (mapea `.../tweak-1.apk` y `libtweak.so`), `libadbd.so` (hijo de init) y `system_server` (mapea el apk). Además `DisableWiFiOnSuspend` **relanzaba** `tweak` al empezar el apagado. `telnetd` es `busybox` independiente.
- Solución: sacar de `/android/data` las apps (`tweak`, RemoteShutter, WbiMaker; copias en la SD `/BAKA6/*.APK`) y los volcados (`NFA4A.BIN`, `NFA4RB.BIN`, `K.BIN`, `LOG.BIN`), y reiniciar.

## 3. La imagen que escribió la cámara (MEDIDO)
Volcado: `analysis/camera-dumps/20261127-wbi-nflasha5/` (62 914 560 B, sha256 en `SHA256SUMS`).

| Campo | WBI de Sony (fw 3.21) | Imagen de la cámara |
|---|---|---|
| Firma | `WBI1` | **`prof`** |
| Secciones | 1164 | 1397 |
| `dataSize` | 41 993 728 | 41 256 960 |
| `oDataSize` | 172 998 656 | 171 311 104 |
| `resumeVector` | `0x800523BC` | `0x800523A4` |
| Miembro del `.dat` | 42 293 120 B | 41 563 808 B (`262144 + dataSize + secciones×32`) |

- Descomprime entera sin errores (171 311 104 B = `oDataSize`).
- Solo 15 de 4254 páginas de `libObj.so` del CFW están dentro (en el WBI de Sony hay 998): es un perfil mínimo, no una caché completa de `/usr`.
- La firma `prof` coincide con el análisis estático (`warm.c:1154`: con `CONFIG_SNSC_SSBOOT` se escribe `prof`).

## 4. Por qué no arranca (SWD, solo lectura, 28-11)
Log del kernel de RAM (AP de memoria, sin parar la CPU), arranque con el paquete 4.07 (`WBI1`):
- `0x834e0000`: `WARMBOOT`, `PM: early resume`, `[LIRO]: liro resume (WBI)`, `ssboot: basic: start profiling...`, y después `mmc_hwip_system_off` repetido (apagado de la SD).
- `0x83430000` (log restaurado): `osd_pin send failed` repetido y `bk2.bak fstat error`, o sea el ritual de apagado.
- **Conclusión:** Loader3 acepta la imagen y el kernel la reanuda, pero era una foto de la cámara **apagándose**; al reanudarla sigue apagándose. Pantalla negra.
- Volcado posterior de `nflasha5` (`analysis/camera-dumps/20261128-wbi-nflasha5-post/`): **idéntico** al instalado salvo la firma → la cámara no reescribe la cabecera tras reanudar.

## 5. Viabilidad de «mezclar con el WBI de Sony» (MEDIDO, tamaños)
| Fichero | Sony → CFW | Páginas distintas | ¿Sustituible en la foto de Sony? |
|---|---|---|---|
| `im.elf` | igual | 1/6 | sí |
| `libObj.so` | igual | 1/4257 | sí |
| `viewUnified2.so` | +2 273 444 B | 11/1210 + 555 añadidas | no |
| `CautionConfig.so` | +195 948 B | 6/417 + añadidas | no |
| 26 `.uxc` | +116…152 B | 9–12 | no (el ext2 mueve bloques) |
La foto de Sony trae los procesos cargados y el ext2 en RAM con el diseño de Sony; el menú nuevo (código añadido) no se mapearía. Crear el `nflasha5` del CFW en el PC: imposible (foto de RAM de un sistema en ejecución). Mover Silent a un ajuste de fábrica (EFCS `+0x210`) queda descartado por el usuario (impide añadir PP/Film Sim).

## 6. Lecciones operativas
- **pmca:** el `pmca-console` del sistema falla en el actualizador forzado por R48 (`Writing updater payload → updater response error`); funciona el `pmca` antiguo del repo: `references/pmca/pmca-console.py firmware -f <dat>`, solo para versión mayor que la de la cámara.
- **R48 automático:** `scripts/cam/r48_auto.sh` (repite `analysis/e26-recovery/r48_updater_swd.cfg` hasta ver `054c:03e2`) y `scripts/cam/r48_recuperar_ejemplo.sh` (R48 → limpieza `/setting` → instalación). El SoC sigue vivo con la batería puesta: para que R48 vea el apagado hay que **sacar la batería**.
- **Cuelgues:** una segunda shell de `ushell` tras otra sesión se queda en `Initializing firmware update`; hace falta ciclo de batería. Dos `pmca` a la vez fallan con `interface is busy`. `0x1043` deja el actualizador desincronizado.
- **SWD:** los volcados largos con Linux en marcha (CPU parada) dan `DSCR` timeouts y **reiniciaron la cámara dos veces**. La lectura por el AP de memoria (`mem_ap`, AP0) a ~95 KB/s no para la CPU y es segura. Dejar un `openocd` a medias (p. ej. `pkill` del padre) puede dejar la CPU parada.
- **Nunca** `pkill -f` con un patrón que aparezca en la propia línea de comandos (mató mi shell).

## 7. Estado y pendientes
- Cámara: firmware **4.07** con la imagen `prof→WBI1`; negra. Recuperación **4.08 sin `nflasha5`** (`build/wbi_propio/revivir/package-4.08`, sha256 `7c6e24d5…`), **construida y verificada** en el PC, **sin instalar**: el último intento no obtuvo el USB del actualizador.
- NO PROBADO: que el 4.08 arranque en frío (el `pkg405` equivalente sí arrancó el 27-11).
- Abierto: conseguir una instantánea con el CFW **en reposo**: `echo warm` completo desde dentro (hipótesis P1/P2/P3 de `film-pb-1-warm-abort-20261126.md`); o decidir vivir sin vídeo en el CFW con Silent.
- Archivos de esta sesión: `scripts/gui/build_package_wbi_propio.py`, `scripts/cam/{ushell,ushell_pull_part,r48_auto,r48_recuperar_ejemplo}`, `docs/runbook-setting-llena.md`, `reports/film-pb-1-wbi-propio-20261127.md`, volcados en `analysis/camera-dumps/2026112{7,8}-*`.
