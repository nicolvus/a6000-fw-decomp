# FILM-PB-1-WBI-SILENT — traspaso a Codex (26-11-2026)

**Para Codex: decide tú el rumbo.** Este documento solo recoge hechos, estado y opciones; no impone ninguna.

## 1. Objetivo
Reproducir vídeo (solo funciona en arranque caliente con WBI) junto con Silent Shooting en el CFW. Hilo anterior: `reports/film-pb-1-wbi-silent-20261128.md`.

## 2. Estado de la cámara (A6000, IP 192.168.1.30)
- CFW 4.05 `pkg405sony` instalado: 3.21 de fábrica + `nflasha15` con `/usr` del CFW Silent + `im.elf` parcheado (`0x9F44` → `movs r0,#1; bx lr`), sin `nflasha5` (`--sin-wbi`). Paquete: `build/wbi_silent/pkg405sony/package-4.05/firmware_packed.dat`.
- `/dev/nflasha5`: cabecera `WBI1` a cero (la borra `ud_wbi_drop` del instalador); los sectores de datos son idénticos al WBI original de Sony. Resultado: arranque frío, sin reproducción de vídeo.
- Instalación: `pmca-console firmware <ruta> --flash --confirm --reflash` (ruta posicional). Telnet root en el puerto 23; la APK `tools/wbi-maker` (sin commitear) abre su propio telnet y sirve `/`, `/live`, `/kmsg` en el 8765.

## 3. Hechos medidos
1. El apagado con el interruptor escribe `"mem"`, no `"warm"` (2 veces; uptime sin reinicio, `nflasha5` sigue a cero).
2. `echo warm > /sys/power/state` apaga la cámara, pero el siguiente arranque es frío y `nflasha5` no cambia (2 veces; con y sin apps muertas y `drop_caches`).
3. Log en RAM (`dd if=/dev/mem bs=65536 skip=33600 count=19`): Syncing → Freezing → free_some_memory → `count_sections_p1:3817, 47112` (otra vez `3515, 43998`) → `Suspending console(s)` → fin.
4. Parámetros: `warm.mode=2`, `errmode=0`, `cancel=255,255`, `mem_dst=0xC00000@0x9B000000`, `mem_work=0x600000@0x9C000000`, `tmo=50000`, MemTotal 204116 kB.

## 4. Análisis estático (commit d117e735; informe `reports/film-pb-1-warm-abort-20261126.md`, evidencia en `reports/evidence/film-pb-1-warm-abort-20261126/`)
Verificado por mí contra bytes y fuentes en esta sesión:
- **El interruptor nunca pide warm.** `im.elf` decide el modo en `0xA258-0xA280` (2 si `*(…)==0x27`, 1 si el flag vale 1 y `[r4+4]!=0`, si no 0). Con modo ≠ 1, `0x9FE8 bne 0xA030` va directo a `"mem"` sin pasar por `0x9F44`. El parche es inerte para el interruptor.
- **`echo warm` falla en silencio.** `sleep.S:99` (mach-cxd90014) llama a `cxd90014_create_warmbootimage` ya con la consola suspendida; con `errmode=0` el fallo se imprime y devuelve 0 (`warm.c:1195-1202`), y `sleep.S` apaga igual.
- **Un frío no escribe `WBI1`.** `resume.S:52` pone `ssboot_stat=SSBOOT_CREATE_MINSSBI`, y `warm.c:1154-1155` escribe `"prof"` en `fVersion`. `WBI1` solo sale sin `CONFIG_SNSC_SSBOOT`. Que el WBI de fábrica lo copie el actualizador desde `dev/nflasha5` lo afirma el informe; no lo verifiqué.
- Hipótesis vivas del aborto (sin cerrar): P1 `udif_driver_suspend` → `pm_suspend_error` → halt; P2 `open`/`write_sector` del dispositivo ya suspendido; P3 timeout (improbable).

## 5. Prueba pendiente en cámara (receta §7 del informe)
Control: `echo 1 > /sys/power/image_drop` (debe imprimir `dropped wbi`; prueba el mismo open+write fuera de la suspensión). Después `echo 1 > /sys/module/pm/parameters/suserr` (si no existe, `BUG()` y reinicio, sin tocar flash), `echo 300000 > /sys/module/warm/parameters/tmo`, `echo 1 > /sys/module/warm/parameters/errmode` y `echo warm > /sys/power/state`. Si no se apaga: P2 (el código sale en dmesg); si se apaga rápido: P1; si tarda ~5 min: P3. Nada de esto requiere flashear. Antes: pedir confirmación al usuario (hubo un apagado accidental por ejecutar la orden real).

## 6. Opciones (a criterio de Codex)
- **A.** Ejecutar la receta §5 para ver el motivo real del aborto.
- **B.** Restaurar el WBI original de Sony desde dentro de la cámara (por ejemplo `dd` del fichero `firmware/extracted/fw321/.../0700_part_image/dev/nflasha5` a `/dev/nflasha5`, con la cabecera `WBI1`). NO probado: habría que revisar la geometría, el riesgo y si el WBI de Sony arranca con `/usr` del CFW Silent (la verificación estática previa decía que sí; falta la prueba física). Toca flash: pedir autorización expresa.
- **C.** Aceptar `prof`: comprobar en estático si el cargador (Loader3) acepta un WBI con cabecera `prof`. NO verificado.
- **D.** Hacer que el interruptor llegue al modo 1 o 2 (condiciones de `0xA258-0xA280`) en lugar de parchear `0x9F44`.

## 7. Límites
- La APK `WbiMaker` fabrica un WBI que, según la capa 3, no sería `WBI1`. No distribuirla como solución hasta decidir.
- Sin commitear: `tools/wbi-maker/`, `build/wbi_silent/`.
- Reglas del proyecto: sin flasheo ni pruebas que apaguen la cámara sin autorización; PENDIENTES en el mismo commit; commits locales sin push.
