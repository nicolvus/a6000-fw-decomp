# FILM-PB-1 — intento de WBI propio con el `/usr` del CFW (27-11-2026)

**Resultado: NO funciona.** La cámara queda en negro con el paquete 4.07. Todo lo de abajo está MEDIDO salvo lo marcado.

## Qué se hizo
1. `/android/data` sin los volcados (copiados a la SD, `/BAKA6/`) y sin las apps `tweak`, RemoteShutter y WbiMaker (copias `TWEAK.APK`, `SHUTTER.APK`, `WBIMAKER.APK`). La app `tweak` (mapeaba `/android/data/app/...apk`, `libtweak.so`, `libadbd.so`) era lo que retenía `/android/data` (EBUSY) en el ritual de apagado.
2. SWD (`reports/evidence/film-pb-1-ssbi-20261126/swd-imelf-offfactor-0x27.cfg`): `HIT` en `im.elf@0xA130`, factor `0x7 → 0x27` (tipo 8, modo 2). `umount /android/data` ya no falla.
3. La cámara escribió `nflasha5` con firma **`prof`**, 1397 secciones, `dataSize` 41 256 960 B, `oDataSize` 171 311 104 B (descomprime entera, sin errores). Volcado: `analysis/camera-dumps/20261127-wbi-nflasha5/` (sha256 en `SHA256SUMS`).
4. Paquete 4.07 (`scripts/gui/build_package_wbi_propio.py`): base Sony 3.21 + `/usr`, `nflasha3` y Darwin del `pkg405` + ese `nflasha5` con la firma cambiada a `WBI1`. Instalado `Done`, `EXIT 0`.

## Por qué no arranca (SWD, solo lectura)
Log del kernel del arranque siguiente (`0x834e0000`): `WARMBOOT`, `PM: early resume`, `[LIRO]: liro resume (WBI)`, `ssboot: basic: start profiling...`, y luego `mmc_hwip_system_off` repetido. El log restaurado (`0x83430000`) es el del apagado: `osd_pin send failed`, `bk2.bak fstat error`. **La imagen es una foto de la cámara a mitad del apagado**: al reanudarla, sigue apagándose.

## Mezclar con el WBI de Sony no es viable
`/usr` Sony → CFW: `im.elf` y `libObj.so` mantienen tamaño (1 página distinta cada uno); `viewUnified2.so` +2 273 444 B, `CautionConfig.so` +195 948 B, 26 `.uxc` +116…152 B. La instantánea de Sony trae esos procesos cargados y el ext2 en RAM con el diseño de Sony.

## Lecciones operativas
- El `pmca-console` del sistema falla en el actualizador forzado por R48 (`Writing updater payload → updater response error`). Vale el `pmca` del repo (`references/pmca/pmca-console.py firmware -f`), y solo para versiones mayores que la de la cámara.
- Con la batería puesta el SoC sigue vivo: para que R48 detecte el apagado hay que sacar la batería.
- `make_init_bk.sh` del ritual de apagado vuelve a llenar `/setting` (`init_bk.bak` 6 815 744 B → `0x1043`): borrar con `scripts/cam/ushell.py` (ver `docs/runbook-setting-llena.md`).
- No usar SWD con volcados largos con Linux en marcha (`DSCR` timeouts reiniciaron la cámara dos veces); lecturas por el AP de memoria (AP0, `mem_ap`) sí van a ~95 KB/s sin parar la CPU.

## Abierto
Hipótesis de dos fases de SSBOOT (`prof` y luego `WBI1`) sin comprobar: volcar `nflasha5` tras reanudar y apagar otra vez. Cámara pendiente de recuperar con un paquete sin `nflasha5` (4.08, `pkg405`).
