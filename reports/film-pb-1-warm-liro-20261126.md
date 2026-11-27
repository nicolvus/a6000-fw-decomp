# FILM-PB-1 · Por qué `echo warm > /sys/power/state` reinicia la A6000

Investigación **offline** (sin cámara, sin SWD, sin repetir `warm`, sin flashear). 26-11-2026.
Evidencia: `reports/evidence/film-pb-1-warm-liro-20261126/S1…S10-*.txt` (2 923 líneas).
Coordinador: 10 subagentes en paralelo (`deepseek-v4-1-flash-1017`, thinking **max**; el perfil `high` no se pudo
usar: `subagent_type_not_found` hasta `/reload`).

---

## 1. Respuesta en una página

**Último punto confirmado:** `<4>[ 537.295341] [LIRO]: entry_suspend:43541068(1)`.
Esa línea la imprime `liro_suspend` (`liro.ko` `.text+0x388`) **11 instrucciones antes** del `blx r3`
(`+0x3B8`) que invoca el callback de AV-CAM `0x43541068`. No hay ninguna línea posterior del kernel viejo.

**Lo que ya está descartado con bytes o con traza persistente**

| Hipótesis | Estado | Prueba |
|---|---|---|
| El callback devuelve error y `udif_driver_suspend` aborta | **REFUTADA** | `liro_suspend` **descarta** el retorno: recarga `r0` en `+0x3BC` y sólo puede devolver 0, -8, -12, todos de **trabajo propio posterior** (`kthread_create`, `vmalloc`). Su llamador (`pm.c:247-252`) sí aborta, pero nunca recibe ese error. |
| El fallo es la fabricación del WBI (`do_make_image`, `warm.c`, timeout `warm.tmo=50000`) | **REFUTADA** | La marca persistente `PM: suspend enter` (`BOOT_TIME_ADD1`, `suspend.c:280`) **no existe** en `boottime-despues.txt`: el kernel no llegó a `sleep.S`. El corte es anterior, en `suspend_ops->prepare`. |
| El fallo es `dpm_suspend` / la congelación / un driver de dispositivo | **REFUTADA** | `dpm_suspend_start()` terminó bien: `PM: suspend of devices complete after 12.181 msecs` sólo se imprime si `error==0` (`main.c:968` + `dpm_show_time` `main.c:407`). |
| Corte de alimentación / batería / SD | **REFUTADA** | `R_REQ#1` en los dos intentos frente a `R_REQ#0` en los cuatro apagados por interruptor; DDR conserva el contenido (el anillo viejo y el nuevo conviven); 87 %, 4 000 mV, sin AC/USB. |
| `pm_suspend_error(0)` → halt silencioso | **REFUTADA como reinicio** | Esa ruta escribe `sus_error=1` (`VA 0x40021060`), ejecuta `cxd90014_cpu_suspend(1)`, se salta el WBI y queda en **WFI**: no reinicia. Además sólo se alcanza si `udif_driver_suspend()` devuelve ≠0, y liro no puede devolver ese error (fila 1). |
| Silent Shooting / EFCS / `nflasha15` / AV-CAM parcheado | **REFUTADA** | El `liro.ko` activo es el de Sony (md5 `1a67c943…`, extraído del TPZL de `nflasha15-405.bin`) y el `AV-CAM.BIN` es el de fábrica (`ef2e3003…`). Nada del CFW entra en esta fase. |

**Lo que queda vivo: dos mecanismos, un mismo observable**

1. **H1 · Cuelgue + watchdog.** `wdt.mode=1`, `wdt.timeout=500` son **500 ms** (`wdt.c:199`: `count = ticks_por_ms × timeout`);
   el IRQ `wdt_intr` (`wdt.c:174-182`) imprime `WDT:RSTREQ_STAT=0x%lx` y llama `pm_machine_reset(0)`.
   Si el callback se bloquea (los servicios de liro que invoca hacen `ter_tsk`/`del_tsk` → `schedule()` sin
   timeout), el WDT dispara el RSTREQ. **Mecanismo VERIFICADO; atribución INFERENCIA.**
2. **H3 · Excepción + `exception.reboot=1`.** Un data/prefetch abort dentro del callback dispara el
   *exception monitor* de Sony y termina en `machine_restart` → mismo RSTREQ. `exception.reboot` **no está en el
   OSS**: su semántica exacta (¿imprime antes de reiniciar?) es **NO VERIFICADO**.

Ambas producen lo medido: `R_REQ#1`, sin `008E E liro`, sin `PM: suspend enter`, sin imagen escrita y sin texto
nuevo en el anillo. **La estática no puede separarlas**: los dos caminos acaban en el mismo registro
(`MISC_RSTREQ_SET`) y el anillo se pierde en el reinicio.

**Último punto que falta observar:** si el reset lo pidió el WDT (`WDT:RSTREQ_STAT`) o el manejador de excepción
(oops). Ese texto **sí se escribe** en el klog de 0x834E0000 (128 KiB), que **sobrevive** al reinicio
(`klog: keep logging buffer … magic wrong`), y se lee con `dd` tras el arranque. Es la §7.

---

## 2. Secuencia verificada (bytes)

```
suspend_enter (suspend.c:240)          [usuarios congelados, consola suspendida, IRQs ON, 4 CPU]
  └ dpm_suspend_start → "PM: suspend of devices complete after 12.181 msecs"   ← medido
      └ suspend_ops->prepare = cxd90014_pm_prepare (pm.c:247)
          └ udif_driver_suspend (driver.c:414) "UDIF: suspend start: unified drivers"  ← medido
              · marca 008E 'B' + nombre del driver (persistente en /proc/snsc_boot_time)
              └ ops->suspend = liro_suspend (liro.ko .text+0x348)
                  · +0x358..+0x378: r0 = (pm_get_state()==4)   → el "(1)" medido = estado DISK
                  · +0x388: printk "[LIRO]: entry_suspend:%p(%d)"                 ← ÚLTIMA LÍNEA
                  · +0x3B8: blx r3   (r3 = [entry+0x18] = 0x43541068)             ← aquí se corta
                  · +0x3BC: recarga r0  ⇒ el retorno del callback se DESCARTA
                  · después: "liro suspend (WBI)" + ft_backup + cp_backup + "liro suspend complete!"  ← NO aparecen
          · marca 008E 'E' del driver y "E unified drivers"                        ← NO aparecen
```

`0x43541068` es un envoltorio ARM de 4 instrucciones (`push {r4-r11,lr}` · `blx #0x435608C0` · `pop` · `bx lr`)
que entra en la rutina Thumb `0x435608C0` (base de carga `0x43541000`, offset `0x1F8C0`). Secuencia interna
(S3, S4):

| Orden | Llamada | Qué es |
|---|---|---|
| 1 | `0x435605A8(3,0xED)` | registrador de marcas en RAM propia de av-cam (12 B/registro) |
| 2 | `0x43560AA4` | **desmontaje RTOS**: 114 `ter_tsk`+`del_tsk`, 35 `del_sem`, 30 `del_flg`, 67 `del_mbf`, `del_cyc`, 88 `def_inh` |
| 3 | `0x43561594` | `malloc_reset` (servicio liro idx 181): vacía las listas del buddy |
| 4 | `0x435605A8(0xB,0x150)` | marca |
| 5 | `blx 0x439C5A04` | **memset**(`0x43D63000`, 0, **0x244D5A** = 2 379 098 B) |
| 6 | `blx 0x439C5320` | **memcpy**(`0x43FA8F00` ← `0x44026E00`, 0x75FE4 = 483 300 B) |
| 7 | `0x435605A8(0x1B,0x163)` | marca |
| 8 | `0x435609B0` | montaje espejo: 113 `CRE_TSK`, 35 `CRE_SEM`, 30 `CRE_FLG`, 67 `CRE_MBF`, 2 `CRE_MPL` |
| 9 | `0x435605A8(0x13,0xFC)` | marca final |

Los "destinos de trabajo" son stubs `[global]+0x14 → +slot` que resuelven en la **tabla de servicios que liro
copia** en `descriptor+0x24` (`*(0x43541014)=0x435410B4`): un stub `ldr r3,[r3,#S]` llama al servicio
`(S-0x24)/4`. El callback **no escribe MMIO** (0 literales ≥0x50000000 en 72 320 instrucciones) y sus dos copias
caen íntegras en `memrsv=0x13B1000@0x82D90000`, sin solape con `wbimem`, `warm.mem_*`, `cmpr.mem`, `tmonitor`
ni klog/alog (S5). El bloqueo, si lo hay, sólo puede venir de `schedule()` dentro de `ter_tsk`/`del_tsk` (S4).

---

## 3. Por qué el camino "manual" es distinto del apagado normal

El apagado del usuario no es "im.elf escribe `warm`": es un intercambio de cuatro fases
`im→upm 0x920144` → `upm→LIRO 0x920143 "liro_sus"` → `upm→im 0x92014D` (im ejecuta `sus_all_u`) →
`upm→im 0x92014E` (`dmm_pre_suspend`) → `upm→im 0x92014F` → `write`. Escribir `warm` a mano **se salta las fases
2-4** (S6).

En los diez volcados de apagado normal, `udif_driver_suspend` marca `008E B liro` / `008E E liro` **sin una sola
línea de liro.ko**: `liro_suspend` sale por `+0x364` **antes** del print y del `blx`. Es decir, **Sony nunca
ejecuta ese callback en un apagado normal**; sólo lo ejecuta la ruta manual. Con `echo warm` sí se ejecutó, y murió.

Esto reencuadra el problema: no es "el WBI falla", es **"la ruta manual llama a un callback que el producto nunca
llama"**. Cualquier intento de crear el WBI a mano debe reproducir antes las fases 2-4 o evitar esa llamada.

---

## 4. Descartes y correcciones al marco anterior

| Afirmación previa | Estado ahora |
|---|---|
| «El fallo está en `do_make_image`/`warm.c`» (`film-pb-1-warm-abort-20261126.md`) | **superada**: el corte es en `suspend_ops->prepare`, antes de `sleep.S` |
| «`suserr=0`/`errmode=0` describen el intento» | **falso**: `pm_suspend_error` escribe el latch `pm.sus_error` (0x80021060) y `pm_setup` lo pone a 0 **en cada arranque**; `pm.suserr` es la **política** de fallo, no un registro. `warm.ignore_drop=1` anula además la única traza en flash (`wbi_drop`) |
| «El `(1)` de `entry_suspend` es una anomalía» | **falso**: es `pm_get_state()==PM_SUSPEND_DISK`; confirma que el kernel sí trató el `warm` como DISK |
| «El callback de av-cam salta a 0 porque la ranura está a cero» | **corregido**: esa ranura es BSS; liro copia ahí su tabla de 0x344 B; S3 lo leyó del fichero, S4 lo resolvió con las relocalizaciones |
| «El `0xB051000B` de `ff4PlayIf` es la causa» (informe anterior) | sigue **inocuo** (aparece también en B, que reproduce) |
| `/tmp/a6000-warm-sin-sd/` no existe | **falso**: existe (8 ficheros, 21:31-21:36); el "sin SD" está además en la captura SWD |
| `liro.ko` vive en `nflasha7` | **falso**: vive en `nflasha15` (`/usr/kmod/liro.ko`), md5 `1a67c943…` |

---

## 5. Reparto de los diez subagentes (hallazgo · estado · límite)

| # | Hallazgo principal | Estado | Límite |
|---|---|---|---|
| S1 | Descompone el bruto al byte: 42 788 B de anillo + 3 separadores Tcl; última línea fiable 537.295341; enlace perdido ≤0,12 s; siguiente contenido = kernel nuevo | VERIFICADO | el anillo no puede probar el no-retorno (lo pisa el kernel nuevo); `log_end=0xC5FD` incoherente, no usado |
| S2 | `liro_suspend` completo: alta UDIF, `(pm_get_state()==4)`, retorno descartado, únicos -8/-12 propios, `wait_for_completion` sin timeout **sólo en resume** | VERIFICADO | agregación interna de `udif_driver_suspend` no verificable (sin ELF) |
| S3 | Envoltorio ARM + orden exacto de las 9 llamadas, marcas `(3,0xED)…(0x13,0xFC)`, memset/memcpy sin acotar | VERIFICADO | no decide si alguna llamada bloquea |
| S4 | Identidad de los tres objetivos vía tabla de servicios de liro; cero MMIO; el bloqueo sólo puede venir de `schedule()` en `ter_tsk`/`del_tsk` | VERIFICADO / INFERENCIA | símbolos `osal_*` UND; WDT del SoC fuera del OSS |
| S5 | `0x439c5320`=memcpy, `0x439c5a04`=memset; rangos íntegros en `memrsv`, cero solape ⇒ **descarta** "la copia toca memoria del kernel" | VERIFICADO | mapeo `0x43xxxxxx` de liro no enumerado |
| S6 | Cadena de apagado normal de 4 fases, `dmm_pre_suspend` inocuo, im.elf no hace nada más, **liro sale antes del callback en el camino normal** | VERIFICADO | quién pone a cero `[Vcur_cpu+0x2C]` |
| S7 | Fase exacta (`prepare`), `pm_suspend_error` = halt WFI (no reset), política `pm.suserr` 0→`BUG()`+restart, `errmode=1` sólo afecta al WBI | VERIFICADO | `exception.reboot` NO VERIFICADO |
| S8 | Reset por **RSTREQ** del propio kernel; `wdt.timeout=500` = 500 ms; `R_REQ#1` en los dos intentos vs `R_REQ#0` en los cuatro por interruptor; DDR y klog se conservan | mecánica VERIFICADA, atribución INFERENCIA | no separa WDT de excepción |
| S9 | liro **ignora** el retorno; sin `E liro`/`E unified drivers` el op no retornó; diseño de captura con breakpoints | VERIFICADO | halt por SWD no probado físicamente en esta cámara |
| S10 | Auditoría: refuta "fabricación/timeout"; `PM: suspend enter` ausente; los tres intentos mueren en la misma fase (`.begin` 14,7/15,1/11,7 s) | VERIFICADO | "murió dentro del callback" vs "entre print y `blx`" no separable sin nueva captura |

Los diez coinciden en el mismo punto de corte; ninguno encontró una ruta alternativa que reinicie antes.

---

## 6. Estado del conocimiento

- **VERIFICADO:** fase (`prepare`), no-retorno de `liro_suspend`, descarte del retorno del callback, ausencia de
  `PM: suspend enter`, mecanismos de reset disponibles (`wdt.timeout=500` ms y `exception.reboot=1`), procedencia
  de fábrica de `liro.ko`/`AV-CAM.BIN`, rangos de memoria de las copias.
- **INFERENCIA:** que el reset lo pidió el WDT (o el exception monitor); que el callback llegó a ejecutarse
  (el print está 11 instrucciones antes del `blx`, sin llamadas en medio).
- **NO VERIFICADO:** semántica de `exception.reboot=1` (fuera del OSS); qué servicio concreto podría bloquearse;
  si el halt por SWD funciona en esta cámara.

---

## 7. La prueba prioritaria (una sola, de sólo lectura tras el intento)

**Objetivo:** separar H1 (watchdog) de H3 (excepción) leyendo el texto que **cada mecanismo escribe antes de
reiniciar** en el klog que sobrevive.

1. Encender la cámara con el paquete actual; **no** cambiar nada de flash.
2. `telnet` root y anotar: `cat /proc/uptime`, `cat /proc/snsc_boot_time | tail -5`.
3. `echo warm > /sys/power/state` (una sola vez).
4. Tras el reinicio, **antes de tocar nada que escriba en `/log`**:
   `dd if=/dev/mem bs=65536 skip=33600 count=19 of=/tmp/klog-warm.bin` y `sha256sum /tmp/klog-warm.bin`
   (0x83400000, 19×64 KiB; el klog arranca en 0x834E0000). Alternativa si `dd` falla:
   `cat /log/klog.bin | head -c 131072`.
5. `strings /tmp/klog-warm.bin | grep -aE "WDT:RSTREQ_STAT|Unable to handle|BUG:|liro suspend|E liro|PM: suspend enter"`.

**Predicciones**

| Resultado | Conclusión | Siguiente paso |
|---|---|---|
| `WDT:RSTREQ_STAT=0x…` | **H1**: el callback se colgó y el WDT reinició | atacar el bloqueo: identificar qué `ter_tsk`/`del_tsk` no retorna |
| `Unable to handle…` / `BUG:` con PC en `0x43xxxxxx` | **H3**: excepción en el callback | localizar la instrucción con el PC del oops |
| `liro suspend (WBI)` o `E liro` | el callback **sí** retornó y el fallo es posterior | volver a `do_make_image` (marco antiguo) |
| Nada de lo anterior | el klog no captura la fase | pasar al plan B (breakpoint SWD en `0x43541068`) |

**Plan B (instrumentación, si la prueba 1 no concluye):** con SWD, `bp 0x43541068` antes de disparar `warm`;
si el breakpoint para, el callback se alcanza; seguir con `step` y, al perder el enlace, `halt` y leer
`PC`/`CPSR` y `MISC_RSTREQ_STAT`. Predicción: PC en el bucle del WDT o en `pm_machine_reset` ⇒ H1; PC en
`__dabt_svc`/`__pabt_svc` o en el *exception monitor* ⇒ H3.

**Si la prueba 1 confirma H1, la prueba que cierra la causa** es una variante con `wdt.timeout=60000` en el cmdline
(hoy `wdt.timeout` es `S_IRUSR`: **no** se puede cambiar en caliente, `wdt.c:44`): con el WDT a 60 s, un cuelgue se
manifiesta como cámara **colgada** en lugar de reiniciada, y H3 seguiría reiniciando en <1 s.

---

## 8. Hallazgo colateral que bloquea el objetivo «que la cámara regenere el WBI sola»

El parche actual de `im.elf` (`0x9F44: movs r0,#1; bx lr`) **no puede** forzar el apagado cálido. Verificado en
bytes sobre `build/wbi_silent/pkg/im.elf` (VA con `.text` en `0x8000`):

```
0xa258 ldr r2,[pc,#0x104] / cmp r3,r2 / bne 0xa2a2      ; despacho por id de orden
0xa262 ldr r3,[pc,#0xc4] / ldr r3,[r3] / cmp r3,#0x27   ; global A (off-factor que fija el mensaje 0x920143)
0xa268 bne 0xa26e
0xa26a movs r0,#2                                       ; modo 2
0xa26e ldr r3,[pc,#0xf4] / ldr r3,[r3] / cmp r3,#1      ; global B
0xa272 bne 0xa280
0xa276 ldr r0,[r4,#4] / subs r0,#0 / it ne / movne r0,#1
0xa280 movs r0,#0
0xa282 bl 0x9fb4                                        ; escribe el modo
```

y `0x9FB4` sólo consulta la compuerta `0x9F44` **dentro** de la rama `cmp r5,#1` (`0x9FE6`):

- modo **2** → escribe el literal `0xA060` = `"warm"`, longitud 4 (`0xA012`);
- modo **1** + compuerta cierta → también `"warm"`;
- cualquier otro (modo **0**) → `0xA030`/`0xA034` = literal `0xA068` = `"mem"`, longitud 3.

Como el interruptor sigue produciendo `"mem"`, el modo calculado en la cámara es **0**: el parche de `0x9F44`
nunca se evalúa. Para forzar el apagado cálido hay que mover el parche a la selección:

- `0xA280: 00 20` (`movs r0,#0`) → `01 20` (`movs r0,#1`): modo 1, que con la compuerta ya parcheada escribe `"warm"`; **o bien**
- `0xA268: 01 d1` (`bne`) → `00 e0`/`00 bf`: modo 2 directo.

Es un cambio de 2 bytes, no probado en cámara. Riesgo: el modo 1 ejecuta los ayudantes `0x9F68`/`0xAB10` que el
modo 2 se salta; el modo 2 se salta la compuerta y la preparación. **Ninguno se ha probado**; ambos exigen
reconstruir el paquete y flashear `nflasha15` (fuera de esta tarea).

---

## 9. Evidencia

`reports/evidence/film-pb-1-warm-liro-20261126/`: `S1-forense-swd.txt` (302 l.), `S2-liro-ko.txt`,
`S3-avcam-entrada.txt` (260), `S4-avcam-dependencias.txt` (230), `S5-memoria-copias.txt` (296),
`S6-apagado-vs-warm.txt` (260), `S7-kernel-suspension.txt` (283), `S8-origen-reset.txt` (264),
`S9-instrumentacion.txt` (262), `S10-auditoria.txt` (416).

Crudos: `/tmp/a6000-warm-captura-swd/{kernel-swd.bin (43 007 B, sha256 2bacd652…), swd.log, resultado.txt,
boottime-antes/despues.txt, antes/despues.json}`, `/tmp/a6000-warm-sin-sd/`, `/tmp/a6000-warm-controlador-sd.txt`.

Fuentes del kernel: `analysis/session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014/{pm.c,wdt.c}`,
`.../arch/arm/common/{warm.c,wbi_cmpr.c}`, `.../kernel/power/suspend.c`, `.../drivers/base/power/main.c`,
`.../drivers/udif/driver.c`, `.../arch/arm/mach-cxd90014/sleep.S`.
