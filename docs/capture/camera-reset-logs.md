# Por qué se reinicia la cámara: logs (2026-10-21)

Fuente: búfer de log del kernel en RAM (`0x83400000`, 19×64 KiB, leído por telnet con `dd` sobre `/dev/mem`). **Sobrevive a los reinicios** (/log, /setting y `last_kmsg` no guardan nada), así que contiene varios arranques seguidos.

| Evento | Uptime | Evidencia | Interpretación |
|---|---|---|---|
| Oops de kernel | 54,8 s | `fops_se_ioctl_receive(1042/1056) err` justo antes; `NULL pointer dereference`, `PC is at free_block+0x4c/0x160`, `LR drain_array+0xf4`, proceso `kworker/3:0`; luego `WDT:RSTREQ_SPAT` y `kernel BUG at arch/arm/mach-cxd90014/wdt.c:082` | Corrupción del slab del kernel justo tras cerrar una sesión de service mode (`usbter`/senser). Con `panic_on_oops=1` el oops acaba en reinicio vía WDT. Compatible con los reinicios al leer páginas de `0xF0020000+` por RMEM; causa exacta NO VERIFICADA |
| `WDT:RSTREQ_STAT=0x0` + `kernel BUG at …/wdt.c:182` | 466,1 s | sin oops previo | El driver WDT de Sony hace `BUG()` al recibir la petición de reset (IRQ 254 `rstreq`). Quién la pide: NO VERIFICADO (watchdog hardware o ARM7). Coincide en el tiempo con la prueba de `sctrace` sobre `bootin.elf` (pid 134), no demostrado |
| Igual | 40,1 s | sin oops previo | Segundo reinicio tras volver a activar Tweak; no hay acción mía registrada entonces |

Tras cada uno aparece `WARMBOOT` (arranque desde la imagen de `nflasha5`, ~3 s). Otros datos: `panic_on_oops=1`, `panic=0`, `watchdog_thresh=30`, ningún proceso tiene abierto un `/dev/watchdog`; no hay `strace`/`gdb` en la cámara.

## Consecuencias
- Trazar con `ptrace` hilos del sistema (`bootin.elf`, `im.elf`) puede disparar la petición de reset; no se repite sin una prueba aislada. `tools/camera-ptrace/sctrace` (ARM sin libc, `alarm` de seguridad) está compilado pero NO PROBADO con éxito.
- Los volcados por service mode que fallan pueden dejar el slab corrupto y reiniciar la cámara.
- Para diagnosticar un reinicio: tras arrancar, leer el búfer (`dd if=/dev/mem bs=65536 skip=$((0x83400000/65536)) count=19`) y buscar `WDT:`, `Oops`, `WARMBOOT`.
