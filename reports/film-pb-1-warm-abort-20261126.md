# FILM-PB-1 — por qué `echo warm > /sys/power/state` no deja un WBI válido (26-11-2026)

Búsqueda estática coordinada (10 subagentes + auditoría adversarial). Cámara apagada y desconectada: **no** se
ha ejecutado nada en ella, no se ha flasheado, no se ha hecho push. Evidencia: `reports/evidence/film-pb-1-warm-abort-20261126/`
(A1, A2, B1, B2, C1, C2, D1, E1, X1).

---

## 0. Respuesta en una página

**El `echo warm` sí llega al kernel y sí entra en la ruta que fabrica la imagen; lo que falla es la fabricación,
y falla en silencio por diseño.** Tres defectos independientes, cada uno verificado contra bytes:

1. **El interruptor nunca pide `warm`.** `im.elf` decide el modo con **tres** vías, no con la compuerta
   `0x9F44`: `0xA262` → modo 2 si `*(0x153E0) == 0x27`; `0xA26E` → modo 1 si `Backup[0x510023] == 1` **y**
   `[msg+4] != 0`; `0xA280` → **modo 0**. Solo los modos 1 y 2 escriben `"warm"`; el **modo 0 escribe `"mem"`
   sin consultar la compuerta** (`0x9FE8 bne 0xA030`). El apagado por interruptor entra con **modo 0**
   (VERIFICADO: es el único modo que produce el `"mem"` medido) ⇒ **el parche de 4 B en `0x9F44` es inerte
   para el interruptor**.
2. **La fabricación del WBI ocurre al final del apagado, con los dispositivos ya suspendidos, y su fallo se
   traga.** `sleep.S:99 bl cxd90014_create_warmbootimage` se ejecuta **después** de `suspend_console()`
   (`suspend.c:339`), de `dpm_suspend_start` (342), de `dpm_suspend_noirq`, de apagar CPUs y de
   `syscore_suspend` (263-284). Si `do_make_image` falla y `warm.errmode = 0`, el código **devuelve 0**
   (`warm.c:1195-1202`) y `sleep.S` interpreta 0 como éxito y apaga (`beq goto_suspend`). Resultado
   indistinguible de un éxito: cámara apagada, cero sectores escritos.
3. **Aunque la fabricación funcionase, un arranque en frío NO escribe `"WBI1"`.** En frío
   `cxd90014_ssboot_stat = SSBOOT_CREATE_MINSSBI (=0)` (`resume.S:51-52`, valor de compilación que ningún
   camino frío reescribe) y `pm.c:379-382` toma esa rama ⇒ `do_make_image` sella `fVersion = "prof"`
   (`warm.c:1154-1156`) con `resume_vector = cpu_resume_profile`. **`WBI1` es el último peldaño de una
   escalera de 5 estados** (MINSSBI → PROFILE → OPTSSBI → SSBOOT_PRE → SSBOOT) que avanza un paso por ciclo de
   apagado/encendido (`pm.c:375-396`, `pm.c:268-278`, `warm.c:1151-1166`). El `nflasha5` de fábrica empieza
   por `WBI1` **porque lo escribió el actualizador**, no la cámara (D1: la copia va después del `ud_wbi_drop`).

**Por eso el log de RAM acaba en `Suspending console(s)`:** `klog` es una **consola** (`kernel/klog.c:201-215,
366`) y `suspend_console()` cortocircuita `console_unlock()`. Todo lo que se imprime después (incluido el
`checking opened files` de `.prepare` y cualquier `wb_printk` del compresor) queda en `__log_buf`, no en la
zona persistente `0x834E0000`. **No ver nada después de esa línea no prueba que no se ejecutara** (§4).

**Causa más probable del fallo de fabricación (INFERENCIA, con dos candidatas vivas y una tercera descartada
por tiempo):** (P1) `udif_driver_suspend()` falla en `.prepare` y `pm_suspend_error()` apaga sin más
(`pm.c:224-232`), o (P2) `do_make_image` falla en/antes de la primera escritura (`open` del `wb_device` o
`write_sector` de `nand.ko`, ya suspendidos). Ninguna de las dos deja rastro. **La prueba de §7 las separa.**

---

## 1. Quién escribe `"warm"`: la cadena completa (VERIFICADO contra bytes)

| Paso | Sitio | Bytes / VA |
|---|---|---|
| `upm.ko` emite el mensaje | `k_upm_off_factor_handler_inactive` (`0xFA18..0xFD7C`), caso `cmd == 0x92014E`, estado `0x22`, `dmm_pre_suspend`, `valloc(0x920169)` | `0xFC18-0xFC24` construye `{0x92014F, param1 = 0xE32C()}`; `0xFC2C osal_snd_sync_msg`; pool `0xFD60 = 0x0092014F` |
| `im.elf` reenvía | callback de cola `0x95B0` → lista `0x920143…0x92014F` → `0x94016A` | registrado para `0x920169` en `0x9C9E` |
| `im.elf` despacha | **único** consumidor de `0x92014F`: `0xA06C`, `cmp` en `0xA258` | literal `0xA360 = 0x0092014F` |
| `im.elf` decide modo | `0xA262` (`*(0x153E0)==0x27` → 2), `0xA26E` (`*(0x154D0)==1 && [msg+4]!=0` → 1), `0xA280` (→0) | `0xA328 = 0x153E0`, `0xA364 = 0x154D0`, `subs r0,#0 / it ne / movs r0,#1` |
| `im.elf` escribe | `0x9FB4`: `open("/sys/power/state",0x1001)` (`0x9FBC-0x9FC2`) → `memset` → compuerta → `write` | `0xA014 ldr r1,=0xC0C8 "warm"` (r2=4) · `0xA034 ldr r1,=0xC0F4 "mem"` (r2=3) · `blx 0x8F68` en `0xA03A` |

**Un solo escritor del nodo en toda la imagen**: `grep` exhaustivo sobre `/usr`, `/system`, `initrd`,
`bootin.elf` y los 53 `.ko` deja solo `im.elf` (más dos cadenas muertas: `init.rc:370` y
`libhardware_legacy.so`, sin xrefs). `upm.ko` **no** escribe el nodo.

**Corrección importante (C2/B1):** el contador persistente **no** decide el frío/caliente como se creía.
`0x9A84` **pone el contador a 0 en cada arranque** y el límite es `0x940005`; la compuerta `0x9F44` pasa en el
primer apagado de cada sesión salvo que el límite valga `0xFFFFFFFF`. El modo lo fijan `Backup[0x510023]`
(leído **una vez** al arrancar, `0x9C6E-0x9C76`, única aparición de `0x510023` en el binario) y el flag de
`upm.ko`.

---

## 2. Dónde se fabrica la imagen y por qué el fallo es mudo (VERIFICADO)

Orden real, tomado de fuente (`kernel/power/suspend.c` + `arch/arm/mach-cxd90014/{pm.c,sleep.S}`):

```
suspend_devices_and_enter
  ├─ ops->begin      = warm_boot_pm_begin   → wbi_setup, free_some_memory, count_sections_p1   [imprime]
  ├─ suspend_console()                                                                        [imprime: última línea visible]
  ├─ dpm_suspend_start()      ← NAND, DMA, MMC… ya suspendidos
  └─ suspend_enter
       ├─ ops->prepare = cxd90014_pm_prepare → udif_driver_suspend() ; warm_boot_pm_prepare()
       ├─ dpm_suspend_noirq · drain_all_pages · disable_nonboot_cpus · IRQs off · syscore_suspend
       └─ ops->enter   = cxd90014_pm_enter → cxd90014_cpu_suspend → sleep.S
                                                                  └─ bl cxd90014_create_warmbootimage
```

Y el enmascarado del error (`warm.c:1191-1206`):

```c
close_error:
    if (ret == -ECANCELED) { wb_printk("canceled to create wbi"); return 0; }   // timeout/cancel ⇒ 0
    if (!wbi_errmode)      { wb_printk("ret=%d"); return 0; }                   // errmode=0 ⇒ 0
    wb_printk("SUSPNED is aborted - error code (%d)!", ret); return ret;        // sólo con errmode≠0
```

Con `warm.errmode=0` (el valor medido en la cámara) **todo fallo devuelve 0** ⇒ `sleep.S` apaga igual. Los
mensajes van a `wb_printk` → `vprintk` → `__log_buf`, y como `klog` es una consola cortocircuitada, **no
llegan a la zona persistente**. Por eso el volcado de `0x83400000` termina en `Suspending console(s)`.

`wb_printk_init()` es un **no-op** (necesita `CONFIG_EJ_WBI_DEBUG`; `kslog` no está compilado: 0 cadenas en
`vmlinux.bin`), y `wb_printk` sólo se calla si el dispositivo lleva `WBI_SILENT_MODE` — no es el caso: el
dispositivo por defecto es el de `nand.ko` (`wb_default_device: sector_size=0x40000, phys_sector_size=0x200`,
una vez por arranque; `xmodem` con `WBI_SILENT_MODE` no se registra).

---

## 3. Hipótesis ya muertas, con la prueba

| Hipótesis | Prueba de defunción |
|---|---|
| **Capacidad / `-ENOSPC`** | El kernel que corre tiene `CONFIG_SNSC_SSBOOT=y` (la cadena `"Freeing memory(use swap parititon): "` sólo existe dentro de ese `#ifdef` y **está** en `vmlinux.bin`), rama en la que la capacidad **sólo avisa** (`warm.c:1088-1095`). El `-ENOSPC` exige `image_mode == IMAGE_MODE_ADP`. Y la cuenta cabe: `o_data = 47 111×4096 = 192 966 656` ⇒ `calc_r = 512 + 80 384 + 192 966 656/5 = 38 674 227 B` (62,2 %) < `121 344 × 512 = 62 128 128 B` |
| **`warm.cancel=255,255`** | `WBI_PORT_UNDEF = 0xfffffff` y `param_ops_port` escribe **2 bytes**: `0xFF,0xFF` ya son los bytes bajos del centinela ⇒ el valor **no cambia** y `wbi_is_canceled()` devuelve 0 siempre. Además `1 << 255 = 0` en ARM |
| **Otro dispositivo (`xmodem`)** | Único registrante: `nand.ko` (`U wb_register_device`, `"WBI partition[%d]…"`); `wb_default_device:` aparece **1 vez por arranque**; `image_dev=*` es el marcador de lectura |
| **`wb_default_device == NULL` en `.enter`** | `nand.ko` sólo llama `wb_unregister_device` en init-cleanup y en `exit`; ningún camino de suspensión |
| **Compresor con `waddr` inválido** | `wbi_cmpr.waddr = 0x5D000000` es válido: lowmem `0x40000000-0x80000000` ⇒ físico `0x9D000000`, detrás de `mem_work` |
| **Cancelación por GPIO durante el envío** | misma prueba que `cancel` |
| **`im.elf` prepara algo (sync, drop_caches, mensajes, ioctls) antes del `write`** | Verificado que **no**: entre `0x92014F` y el `write` sólo hay `open`, lecturas, `Backup_read/write` del contador, `memset`, la compuerta y `snprintf`. Cero referencias a `nflasha5`/`wbi` y cero `fsync` (no están entre los 58 símbolos importados) |
| **Falta memoria / procesos abiertos** | `chk_opened=` ausente (compuerta inerte); `free_some_memory` no aborta; la 2.ª prueba con apps matadas y `drop_caches` dio **lo mismo** con 22 MB menos |

---

## 4. Hipótesis vivas (y qué las separa)

| # | Hipótesis | Predicción | Cómo se separa |
|---|---|---|---|
| **P1** | `udif_driver_suspend()` falla en `.prepare` ⇒ `pm_suspend_error(0)` ⇒ `wbi_drop()` + `sus_error=1` + **halt** (`pm.c:224-232`, `pm.c:228`) | Apagado inmediato, sin escritura | Con `errmode=1` **la cámara seguiría apagándose** (P1 no pasa por `do_make_image`) |
| **P2** | `do_make_image` falla en/antes de la primera escritura: `wb_default_device->open()` (`warm.c:1070`, con el bug `ret = (open()<0)`), `wbi_send_data` o el primer `wbi_wbuf_flush` (`wbi_cmpr.c:715-745`, bloque de 256 KiB en LBA 0) | Apagado inmediato, sin escritura (idéntico a P1 a simple vista) | Con `errmode=1` el suspend **se aborta** (`sleep.S:99-104`), la cámara **sigue encendida** y el código de error exacto aparece en `/log` |
| **P3** | Timeout del compresor: `-ECANCELED` a los `warm.tmo` ms | Apagado **tras ~50 s**, sin escritura | `-ECANCELED` **no** respeta `errmode` (`warm.c:1196`): con `errmode=1` seguiría apagándose, **pero** con `tmo=300000` tardaría 5 min. Si el apagado es rápido, P3 muere |

**Prueba de que "cero sectores" acota el punto de fallo (X1):** la primera escritura posible es un bloque
completo de `0x40000` B (256 KiB) en LBA 0 con `fVersion="invl"` — cubriría los sectores 0..511. El sector 1
está **idéntico** al WBI de Sony ⇒ **no hubo ninguna escritura, ni parcial**. Cualquier fallo "a mitad"
(compresión, NAND tras el primer bloque, `-ENOSPC` tardío) queda descartado: el fallo es **en o antes** de
`warm.c:1132`.

---

## 5. La trampa del `"prof"`: un arranque en frío nunca escribe `"WBI1"` (VERIFICADO)

`cxd90014_ssboot_stat` nace `SSBOOT_CREATE_MINSSBI = 0` (`resume.S:51-52`) y **sólo** lo reescribe el prólogo
asm de la entrada de reanudación (`resume.S:53-70`). En frío nadie lo toca ⇒ `pm.c:379-382` ⇒
`cxd_create_warmbootimage(cpu_resume_profile, 0)` ⇒ al final `warm.c:1154: fVersion = WBI_PROF_VER = "prof"`.
Confirmación empírica independiente: el log medido imprime `Freeing memory(use swap parititon)`, cadena que
**sólo** se alcanza con `stat == SSBOOT_CREATE_MINSSBI` (`warm.c:728-729`).

Consecuencias:

* El criterio de cierre que figuraba en los informes previos («tras el apagado, `nflasha5` empieza por
  `WBI1`») es **erróneo para un arranque frío**: debe ser `"prof"` en el primer apagado, `"WBI1"` sólo tras la
  escalera completa. **Corregido en `docs/PENDIENTES.md`.**
* `Loader3` sólo tiene **medido** el caso `WBI1` (3.48 con `nflasha5` → `BootMode 11`; 3.52 sin él →
  `BootMode 1`). Si acepta `"prof"` es **NO VERIFICADO**; si no lo acepta, la escalera no arranca y la cámara
  se queda en frío para siempre aunque la fabricación funcione.
* El `nflasha5` que trae el paquete de Sony empieza por `WBI1` porque **lo escribió el actualizador**, copiando
  `dev/nflasha5` después del `ud_wbi_drop` (D1). La cámara no participa en su creación en ese camino.

---

## 6. Tabla por pregunta

| Pregunta | Hallazgo | Estado | Fuente |
|---|---|---|---|
| **A** ¿Qué cancela antes de escribir? | Ninguna condición de `warm.c` se cumple con `count_sections_p1:3817, 47112`: es la **fase 1** (`.begin`), no un aborto. `3817 = 2502 + 64 + 2502/2` (margen `warm.c:915`), `47112 = 47 111 + 1` (`section_data_order` nunca se asigna); 2502 secciones son **fragmentación** (el tope por bloque es `maxnr_page_per_section = 917 504/4096 = 224`). La capacidad sólo avisa; `free_some_memory` no aborta; `cancel` es el centinela. Los abortos reales están en la fase 2 y **todos** devuelven 0 con `errmode=0` | VERIFICADO (fuente + aritmética + bytes del kernel) | A1, A2, X1 |
| **A'** ¿Dónde es la primera escritura? | `warm.c:1129` sólo copia la cabecera al WBUF en RAM; el primer acceso al dispositivo es `warm.c:1132 → wbi_wbuf_flush() → write_sector()`: bloque de 256 KiB en LBA 0. Antes hay 8 condiciones (`WBI_MODE`, dispositivo, cancel, plazo, `open`, `count_pages(p2)`, capacidad, WBUF) | VERIFICADO | A2, X1 |
| **B** ¿Qué hace `im.elf` entre `0x92014F` y el `write`? | Nada sustantivo: `open`, lecturas de tres globales, `Backup_read/write` del contador (`0x940004`, canal `0x94`), `memset`, compuerta, `snprintf` de traza. **Cero** `sync`/`drop_caches`/`/sys/power/image_*`/ioctls/mensajes a Darwin-MCU y **cero** referencias a `nflasha5` o `wbi` | VERIFICADO | B1 |
| **B'** ¿Qué necesita el kernel para dar la imagen por buena? | Nada de userspace. `do_make_image` no lee la cabecera previa, calcula `resume_vector` (`virt_to_phys`), pone `fVersion="invl"` al empezar y la reescribe al final (`"prof"`/`"WBI0"`/`"WBI1"` según estado). Con `CONFIG_SNSC_SSBOOT` el `cmpr.path` es sólo el microcódigo del compresor | VERIFICADO | B2 |
| **C** ¿Por qué el interruptor sigue yendo a `"mem"`? | El modo del `0x92014F` sale de `*(0x153E0)==0x27` (→2), `Backup[0x510023]==1 && [msg+4]!=0` (→1) o **modo 0**. El interruptor entra con **modo 0**, que escribe `"mem"` **sin pasar por `0x9F44`** ⇒ el parche de 4 B no interviene. Escritores del nodo en toda la imagen: **sólo `im.elf`** | VERIFICADO (bytes); el valor de `Backup[0x510023]` en la unidad, NO VERIFICADO | C1, C2, B1 |
| **D** ¿Cómo crea Sony su WBI? | **No lo crea la cámara en el update**: el actualizador borra la cabecera (`ud_wbi_drop`, 512 ceros, sin `lseek`) y **copia** `dev/nflasha5` pre-construido (42 293 120 B, `WBI1`). La fabricación en cámara es del kernel, en el apagado, y exige la escalera de 5 estados. No hay requisito de sistema «limpio» (`chk_opened` inerte, `boot_drop=0`, capacidad sólo avisa) | VERIFICADO (bytes del actualizador + fuente + cmdline); "la copia va después del drop", INFERENCIA | D1 |
| **E** ¿Cómo se ve el error? | `klog` es una **consola** ⇒ `suspend_console()` la corta y **nada** posterior llega a `0x834E0000`. `pmdebug` refleja printk por `printascii()` al UART de depuración (hardware, no sirve sin pin). `no_console_suspend` es `__setup` ⇒ **sólo cmdline** (flash). **Método válido:** `warm.errmode=1` (sysfs, `S_IWUSR`) ⇒ el fallo **aborta el suspend** ⇒ `resume_console()` vuelca el backlog y la cámara sigue encendida | VERIFICADO (fuente + bytes) | E1, A2 |
| **F** ¿Camino alternativo sin `im.elf`? | **No hay receta por telnet que haga falta**: los requisitos de usuario ya están cumplidos (`chk_opened` inerte, `sync` lo hace el kernel, `free_some_memory` ya corrió, la capacidad sólo avisa, `image_mode=3` no ayuda y `mem_dst` no se puede cambiar sin reflashear). Lo que **sí** se puede hacer desde telnet es (a) `sync; echo 3 > /proc/sys/vm/drop_caches`, (b) subir `warm.tmo`, (c) `errmode=1` + `logbuf_noclear=1` para **ver** el fallo. Para que el **interruptor** pida `warm` hay que parchear la decisión de modo (`0xA262-0xA280`, forzar `r5=2`): firmware, no comando. `echo disk` **no** es equivalente (sin `CONFIG_HIBERNATION` ⇒ `-EINVAL`); `echo mem` = SUS sin imagen | VERIFICADO (fuente + bytes) | F1, C1, C2, B1 |

---

## 7. Receta de la próxima prueba en cámara (no ejecutada)

Objetivo: **hacer visible el fallo** y separar P1 / P2 / P3 sin flashear y sin escribir en flash.

### 7.1 Antes (lecturas, 1 min)
```sh
cd /tmp
cat /proc/uptime                                    # referencia de tiempo
cat /sys/power/image_mode /sys/power/image_dev      # 2 / *nflasha5
cat /sys/module/warm/parameters/errmode /sys/module/warm/parameters/tmo
ls /sys/module/pm/parameters/ 2>/dev/null           # ¿existe 'suserr'? (lectura)
dd if=/dev/nflasha5 bs=512 count=2 2>/dev/null | md5sum   # huella del sector 0
```

### 7.1 bis Controles previos (opcionales pero decisivos, 2 min)
```sh
ls -l /system/sabin/ssboot.bin /system/sabin/ssboot_any.bin   # microcódigo del compresor (F1)
cat /proc/ssboot/mode /proc/ssboot/state /proc/ssboot/swapfile 2>/dev/null
echo 1 > /sys/power/image_drop ; sleep 1 ; dmesg | tail -5
```
`image_drop` recorre **exactamente** el mismo `open`+`write_sector` del `wb_device` que usa la creación
(`warm.c:440-461` → `366-391`). Si imprime `dropped wbi`, el camino de escritura a `nflasha5` está **vivo
fuera de la suspensión**: eso descarta que el dispositivo esté roto y centra el fallo en el estado suspendido
(P2) o en que no se llegó (P1). Si **no** imprime nada, P2 sube a causa principal.

### 7.2 Preparar el diagnóstico (todo RAM, reversible)
```sh
echo 1 > /sys/module/pm/parameters/suserr   # SOLO si el fichero del 7.1 existe: evita el BUG() de
                                            # kernel/power/suspend.c:517-535 (FAIL_ACTION_EXCEPTION = 0)
echo 300000 > /sys/module/warm/parameters/tmo     # 5 min: hace inconfundible un timeout (P3)
echo 1 > /sys/module/warm/parameters/errmode      # el fallo deja de ser mudo y aborta el suspend
cat /sys/module/warm/parameters/errmode /sys/module/warm/parameters/tmo
sync
```
> Si `/sys/module/pm/parameters/suserr` **no** existe, seguir igualmente: un fallo de suspensión hará
> `BUG()` y la cámara se reiniciará (inofensivo, no escribe flash), pero se perderá el volcado. Ese
> reinicio, por sí mismo, ya demuestra que el suspend **sí** falló (P2).

### 7.3 Disparar y observar
```sh
echo warm > /sys/power/state
```
* **Resultado A — la cámara NO se apaga** (vuelve a responder en telnet, pantalla/led despiertan):
  **P2 confirmada**. Recoger la prueba:
  ```sh
  dmesg | tail -80                       # o: cat /proc/klog | tail -80
  dmesg | grep -iE 'wbi|warm|make_image|SUSPNED|canceled|ERROR:' | tail -40
  dd if=/dev/nflasha5 bs=512 count=2 2>/dev/null | md5sum     # ¿cambió el sector 0?
  ```
  Firmas esperadas: `ERROR:wbi_exec:…: -125` (timeout/ECANCELED) · `warm:…: ret=-5` / `ret=-19`
  (`open` del `wb_device`) · `warm:…: ret=-1` (primer `write_sector`) · `do_make_image: N sections,
  M pages` (llegó a enviar) · `rewrite header for compressed image!` (éxito).
* **Resultado B — se apaga igual, rápido (<1 min)**: **P2 descartada**; queda **P1**
  (`udif_driver_suspend` → `pm_suspend_error` → halt) como única explicación del apagado silencioso.
* **Resultado C — se apaga tras ~5 min**: **P3 confirmada** (timeout del compresor).
* Discriminante adicional si se apaga: en el arranque siguiente, `dmesg | grep -i rstreq` (el log imprime
  `WDT:RSTREQ_STAT`; ver `docs/capture/camera-reset-logs.md:8`). Un reset por watchdog distingue «se colgó»
  de «halt ordenado».

### 7.3 bis Control de la instrumentación (si se duda)
`echo 0x1000 > /sys/module/wbi_cmpr/parameters/wsize` fuerza un fallo de `wbi_setup` en `.begin` ⇒ con
`errmode=1` la cámara **debe** quedarse encendida con `ERROR` en el log. Si ese control **no** se comporta
así, la instrumentación no vale y hay que replantear (restaurar `wsize=0x100000` después).

> **Corrección de auditoría:** F1 afirma que `pm_action_on_suspend_fail = 0` equivale a RESUME. **No**: en
> `kernel/power/suspend.c:452-455`, `FAIL_ACTION_EXCEPTION = 0` y es el caso que ejecuta `BUG()`. Por eso el
> paso 7.2 empieza poniendo `suserr = 1` (RESUME) si el fichero existe. E1 y X1 coinciden en esta lectura.

### 7.4 Restaurar
```sh
echo 0 > /sys/module/warm/parameters/errmode
echo 50000 > /sys/module/warm/parameters/tmo
echo 0x100000 > /sys/module/wbi_cmpr/parameters/wsize   # si se usó el control de 7.3 bis
```

### 7.5 Lectura de apoyo (opcional, tras un arranque en frío)
```sh
dd if=/dev/mem bs=4096 skip=$((0x80021000/4096)) count=1 2>/dev/null | od -A x -tx4
```
`0x54` = `pm.resume`, `0x60` = `pm.sus_error`. **Ojo:** `cxd90014_pm_setup()` **pone `sus_error=0` en cada
arranque** (`pm.c:137-143`), así que un 0 no descarta nada; sólo sirve si se lee sin reiniciar.

---

## 8. Correcciones a los informes previos

1. **«Ninguna inferencia abierta» (informe `film-pb-1-wbi-silent-20261128.md` §9) queda REFUTADA.** Con
   `warm.errmode=0` un fallo devuelve 0: «no hay mensaje de error» **no** significa «no hay fallo». §9-I2
   («do_make_image no lee la cabecera ⇒ nada aborta») confundía *no leer la cabecera* con *no poder fallar*.
2. **El criterio de cierre «`nflasha5` empieza por `WBI1` tras el primer apagado» es erróneo**: en frío sale
   **`prof`** (§5). Y `WBI1` exige la escalera de 5 estados.
3. **El parche `0x9F44` no sirve para el interruptor**: el modo 0 no consulta la compuerta (§1). El parche
   sólo tendría efecto si `Backup[0x510023]==1` y `upm.ko` mandara `[msg+4]!=0`.
4. **El contador `0x940004` no es el freno**: `0x9A84` lo pone a 0 en cada arranque y el límite es
   `0x940005`. Lo que decide es `Backup[0x510023]`.
5. **El log persistente no ve nada después de `Suspending console(s)`** porque `klog` es una consola, no por
   «el código no llegó». El volcado aportado **no puede** contener el `checking opened files` de `.prepare`.
6. **`0x9FB4` es la función que escribe** (`power_write()`, prólogo `push {r4,r5,r7,lr}`); el **manejador**
   del mensaje es `0xA06C`, y el modo se calcula en `0xA258-0xA280`. Los informes previos llamaban «compuerta»
   al conjunto; son dos cosas distintas y sólo una está parcheada.

---

## 9. Límites

* `nand.ko` es binario y **no** está en el árbol OSS: no se ha desensamblado `open`/`write_sector` ni su
  `suspend_prepare`; por eso P1/P2 siguen vivas y no se puede afirmar cuál se cumplió.
* `Loader3` no está disponible: que acepte `"prof"` (y arranque la escalera) es **NO VERIFICADO**.
* El valor real de `Backup[0x510023]` y del flag de `upm.ko` en la unidad es **NO VERIFICADO** (NVRAM/RAM).
* No se ha ejecutado nada en la cámara: todo lo de §7 es una petición.

---

## 10. Evidencia

`reports/evidence/film-pb-1-warm-abort-20261126/`

| Fichero | Contenido |
|---|---|
| `A1-abortos-warm.txt` | Lista exhaustiva de abortos de `warm.c`, aritmética de 3817/47112, capacidad, `cancel` |
| `A2-cmpr-y-orden.txt` | Primera escritura, motor `wbi_cmpr`, timeout, silencio de `klog`, `waddr` válido |
| `B1-imelf-antes-del-write.txt` | Cadena `upm.ko → im.elf → write`, efectos previos, ausencias, bytes del parche |
| `B2-validacion-kernel.txt` | `get_ssboot_stat`, escalera `prof`/`WBI0`/`WBI1`, `resume_vector` de fábrica, ramas ssboot |
| `C1-escritores-de-state.txt` | Inventario de escritores del nodo en toda la imagen; cadenas muertas |
| `C2-ramas-r5.txt` | Desensamblado de `power_write`, origen de `r5`, unicidad de llamadas y literales |
| `D1-fabrica-y-prerrequisitos.txt` | `ud_wbi_drop` (512 ceros, sin `lseek`), copia de `dev/nflasha5`, Loader3 3.48/3.52 |
| `E1-observabilidad.txt` | `pmdebug`, `console_suspend`, `klog` como consola, método `errmode`, tabla de firmas |
| `F1-receta-sin-imelf.txt` | Qué se puede y qué no desde telnet, controles (`image_drop`, `wsize`), `disk` no equivale |
| `X1-auditoria-adversaria.txt` | Auditoría: hipótesis muertas, acotación del punto de fallo, corrección del magic |
