# 3.44a: arranque fallido, lectura SWD de solo lectura (08-11-2026)

Ver [G11 §8](../../../docs/gui/g11-auditoria-307-nflasha15.md).

* `loader2-log-0xc0060000.txt`: búfer de log de Loader2 en la eSRAM (extraído de un volcado de 1 MiB por la CPU, no versionado).
* `poll.log`: registros de la CPU en la parada (PC `0xc00310e0`, LR `0xc00332e9`, en Loader2).
* `r48.log`: recuperación por SWD (R48) hasta el actualizador.
* `postfail_l2.cfg`, `ap0_klog.cfg`, `poll.sh`: guiones usados (solo lectura salvo R48, que solo cambia `r0` de la CPU).
