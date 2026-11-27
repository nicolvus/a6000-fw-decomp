# Prompt para 10 agentes (DeepSeek Flash v4.1) — FILM-PB-1: WBI propio del CFW 4.05

Copia el **bloque común** + **uno** de los bloques A1…A10 en cada agente. Todos trabajan en paralelo,
solo en estático, y entregan un archivo cada uno.

---

## Bloque común (pegar en los 10)

Eres un ingeniero de ingeniería inversa de firmware ARM (Sony A6000, SoC CXD90014, Linux 2.6.35 + userspace
Sony, Thumb-2). Trabajas **solo en estático** sobre el repositorio
`/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter` (rutas relativas a él).

**Prohibido:** tocar la cámara, SWD, flashear, ejecutar binarios del firmware, `git commit`/`push`, editar
archivos fuera de tu entregable. Escribe en español.

**Objetivo global:** que la cámara genere en el apagado por interruptor una imagen de arranque en caliente
(WBI) válida para el CFW 4.05 y que esa imagen reanude sin fallos, de modo que la escalera SSBI
(MINSSBI `prof` → PROFILE → OPTSSBI → SSBOOT_PRE → SSBOOT `WBI1`) avance.

**Hechos ya medidos en cámara (26-11-2026). Tómalos como datos; si encuentras algo que los contradiga,
dilo con evidencia:**

1. El apagado por interruptor llega a `im.elf` con el mensaje `0x920143`. `im.elf@0xa124..0xa14a` guarda
   `msg[4]` (el **factor de apagado**) en `0x153e0`, `msg[8]` en `0x15248`, y el **tipo** en `0x153dc`:
   `8` si factor==`0x27`, `4` si `msg[8]`==`0x1b`, si no `1`. Medido: factor del interruptor = **`0x7`**
   (tipo 1). Después, `0xa262..0xa282` elige el modo (2 si `*(0x153e0)==0x27`), y `0x9fb4` escribe
   `"warm"` o `"mem"` en `/sys/power/state`.
2. **Ruta A, la que crea imagen pero reanuda mal.** Con factor 7 (preparación `mem`), SWD cambia `r0=3→4`
   en la llamada a `state_store` del kernel (`0x40091f7c`). El kernel crea la imagen y `nflasha5` pasa a
   cabecera `prof`. El loader **sí** la acepta (`Kernel Jump[MODE#12]`, `WARMBOOT`, `ssboot: basic: start
   profiling...`). A los ~1,5 s `im.elf` (pid 144) aborta:
   `raise ← abort ← libSyncAndroid.so res_load_backup@0x1dc8`, porque `mount_fs()` devuelve ≠0 tras
   `Android Loaded file bk1`. Con `exception.reboot=1`, `em_reboot(0)` → IRQ `rstreq` con
   `RSTREQ_STAT=0` → `kernel BUG at wdt.c:182` → reinicio en frío. Con `reboot=0` la cámara queda negra.
   Hipótesis (por verificar, A1/A3): `/android/data` (`/dev/nflasha17`, vfat) **sigue montado** dentro de la
   instantánea porque `SyncAndroid_sus` solo desmonta y guarda con tipo `8`.
3. **Ruta B, preparación `warm` nativa que se cuelga.** SWD pone factor `0x27` en `im.elf@0xa130`
   (`cmp r3,#0x27`). El registro de arranque del apagado termina en `3: 94 B Is 155_SyncAndroid_sus` (106,588 s)
   y **nunca** marca su `E`. No aparece la línea `155 B make /setting/init_bk.bak` de `make_init_bk.sh`. El
   kernel no crea imagen: `nflasha5` queda igual.
4. Ya existen en `/android/data/backup/`: `BK1.BAK` y `BK1.OLD` (1 310 732 B cada uno, sin `BK2`). En
   `/setting/` existe `init_bk.bak` (6,8 MB) y **no** existe `iniok` ni `first_ssboot` (no verificado su ausencia
   exhaustiva).

**Evidencia** (en `reports/evidence/film-pb-1-ssbi-20261126/`):
- `klog-reanudacion-abort-imelf.txt`: klog completo de la reanudación de la ruta A, con el volcado del
  monitor de excepciones (registros, pila, mapas de `im.elf`).
- `klog-reanudacion-wdt-bug.txt`: la misma reanudación con `reboot=1`, más el cmdline.
- `boottime-mode12-reset.txt`: el loader en `MODE#12`, la reanudación y el reinicio.
- `boottime-cuelgue-syncandroid-sus.txt`: el apagado de la ruta B colgado en `SyncAndroid_sus`. Está antes de la
  línea `L: BOOT`.
- `swd-*.cfg`, `swd-resumen.log`: las dos conversiones SWD y su resultado.

**Binarios** (todas las copias de cada uno tienen el mismo md5 entre versiones salvo que se indique):
- `im.elf` 4.05: `build/wbi_silent/files/bin/im.elf` (md5 `00aa05ea…`; `.text` en VA `0x8000`, offset 0).
- `libSyncAndroid.so`: `build/cfw_fbm31_pkg397/work/xn397/lib/libSyncAndroid.so` (md5 `768c6299…`, con
  símbolos: `SyncAndroid_sus/_res/_act/_inact/_init`, `res_load_backup`, `mount_fs`, `sus_make_backup`,
  `ld_bk_file`, `mk_bk_file`, `select_bk_file`, `sasflag_*`, `ssbflag_*`). En cámara está en `0x09d72000`.
- Resto del userspace y los módulos: `build/cfw_fbm31_pkg397/work/xn397/{bin,lib,kmod}`. Ahí están `upm.ko`,
  `liro.ko`, `dmm.ko`, `make_init_bk.sh`, `load_init_bk.sh`, `chk_bkfile.elf`, `bk.elf` y `libosal_uipc.so`. Hay dos
  variantes de `libosal_uipc.so`: dilo si te afecta.
- Kernel OSS de Sony: `analysis/session18/codex-g/oss-linux/linux/` (`kernel/exception.c`,
  `arch/arm/common/warm.c`, `arch/arm/mach-cxd90014/{pm.c,resume.S,wdt.c,core.c}`, `kernel/power/*`).
- Informes previos: `reports/film-pb-1-warm-abort-20261126.md`, `reports/film-pb-1-warm-liro-20261126.md`,
  `reports/film-pb-1-wbi-silent-20261128.md`. Pueden tener conclusiones superadas por los hechos de arriba.

**Herramientas:** `llvm-objdump -d --triple=thumbv7-linux-gnueabi <bin>` (las funciones Thumb tienen la
dirección impar en las tablas), `readelf`, `strings -t x`, `python3`. Si tienes el MCP `rea`, úsalo y
verifica lo decisivo contra los bytes.

**Reglas de evidencia:** cada afirmación lleva una de estas etiquetas: **VERIFICADO** (bytes o
instrucciones citados con dirección), **INFERENCIA** (razonamiento explícito) o **NO VERIFICADO**. Una búsqueda
vacía no prueba ausencia. Cita las direcciones como `binario@0xVA`.

**Entregable:** un único archivo `reports/evidence/film-pb-1-ssbi-20261126/A<n>.md`:
1. Respuesta en ≤10 líneas.
2. Hallazgos con su evidencia.
3. Lo que propones medir en cámara para confirmarlo: un punto de interrupción de un solo disparo, con
   dirección, condición y qué leer.
4. Dudas abiertas.

Máximo unas 400 líneas.

---

## A1 — Qué hace `SyncAndroid_sus` con tipo 8 y dónde puede bloquearse

Descompila por completo `SyncAndroid_sus@0x22f0` y todo lo que alcanza con `r0=8`: `0x2138`, `0x1f34`, la
espera `osal_wait_thread_exit` y su argumento (qué hilo, quién lo crea), `unlink`, la condición del
`system("/usr/bin/make_init_bk.sh …")` y `0x1fb8`. Enumera **cada llamada que puede bloquear**: espera de hilo,
`system`, `umount`, `fsync`, `tar`/`dd`, mensajes `osal_snd_sync_msg`, binder. Para cada una indica si se
ejecuta con tipo 1 y con tipo 8. Conclusión pedida: el primer punto donde la ruta B puede quedarse sin
volver, y por qué la línea `make` del registro de arranque no aparece.

## A2 — El hilo que espera `SyncAndroid_sus`

Identifica la variable global que se pasa a `osal_wait_thread_exit` en `SyncAndroid_sus` y todos sus
escritores: `SyncAndroid_act`, `_inact`, `_init` y `_res`. Explica qué hace ese hilo y en qué condición termina
(¿espera a Android, binder, `/android/data`, un mensaje?). Explica por qué terminaría con tipo 1 y no con tipo
8, o por qué con tipo 1 ni siquiera se espera. Cruza con el klog: `binder: 419:434 transaction failed 29189` se
repite cada ~50 s.

## A3 — La reanudación: `SyncAndroid_res`, `res_load_backup` y `mount_fs`

Descompila `SyncAndroid_res@0x288c`, `res_load_backup@0x1d4c`, `mount_fs@0x19f8`, `ld_bk_file` y los
`sasflag_*`/`ssbflag_*` que intervienen. Responde:
- ¿Qué monta `mount_fs`, con qué argumentos, y qué códigos de error devuelve?
- ¿Falla si `/android/data` ya está montado?
- ¿Qué rama toma `SyncAndroid_res` según `sasflag_is_first_ssb` y `/setting/first_ssboot`?
- ¿Qué estado deja `SyncAndroid_sus(8)` para que la reanudación funcione, y cuál deja `SyncAndroid_sus(1)`?

Conclusión pedida: confirma o refuta que el `abort` de la ruta A se debe a que `/android/data` quedó montado.

## A4 — `im.elf`: factor de apagado, tipo y despacho de suspensión

En `im.elf` 4.05, documenta lo siguiente:
- El manejador de `0x920143` (`0xa124`) y el significado de los factores `0x7`, `0x1b` y `0x27`.
- Todos los lectores de `0x153dc` (tipo), `0x153e0` y `0x15248`.
- Cómo se pasa el tipo a las funciones `Is xxx_sus` de `sus_all_i`: la tabla de manejadores y el orden.
- La secuencia completa `0x920143 → 0x920144 → 0x92014D → 0x92014E → 0x92014F → write`, con qué hace `im.elf`
  en cada fase según el tipo.

Indica si cambiar solo `msg[4]` en `0xa130` es equivalente a lo que haría Sony con factor `0x27`, o si
faltan otros campos u otros procesos que ya decidieron con `0x7`.

## A5 — Quién decide el factor `0x27`

Localiza el emisor de `0x920143` (probablemente `upm.ko` o un daemon de usuario) y de dónde saca `msg[4]`.
Explica en qué condiciones emite `0x27` (¿tecla, temporizador, existencia de un WBI válido, `ssbflag_is_available`,
modo de servicio?) y por qué el interruptor da `0x7`. Busca la tabla de factores de apagado. Conclusión pedida:
¿hay una vía de producto para que el interruptor genere `0x27`? Si la hay, ¿qué precondición le falta a
nuestra cámara?

## A6 — El resto de manejadores `Is *_sus` con tipo 8

En el registro `boottime-cuelgue-syncandroid-sus.txt`, lista los manejadores `Is` que corrieron antes de
SyncAndroid y los que vendrían después (sácalos de la tabla de `im.elf` o de los `.so`). Para cada uno indica si
su comportamiento depende del tipo (`cmp rX,#8` o similar) y si puede bloquear. Conclusión pedida: si se
desbloquea SyncAndroid, ¿qué otros manejadores son candidatos a bloquear o romper la ruta B?

## A7 — Requisitos del kernel en la escalera SSBI

Con el OSS (`warm.c`, `pm.c`, `resume.S`, `kernel/power/*` y lo que haya de `ssboot`), documenta:
- Qué exige cada peldaño al userspace.
- Qué hace `free_some_memory` con `MINSSBI` (swap `null` en cámara).
- Qué cambia entre `cpu_resume_profile`, `_optimize`, `_ssboot_pre` y `_ssboot`.
- Cuándo se escribe `/log/ssbi_prof.bin` (`basic.prof_path`) y quién lo consume.

Relaciona `ssbflag_mk_tta_flag`, `/android/data/backup/ssboot.tta` y `/setting/first_ssboot` de
libSyncAndroid con los estados del kernel. Conclusión pedida: el orden exacto de ciclos y qué debe hacer el
usuario o el sistema en cada uno.

## A8 — Cómo fabrica Sony su WBI y qué estado de usuario contiene

El informe anterior concluye que el actualizador **copia** `nflasha5` (WBI1) prefabricado. Determina con qué
estado de usuario se fabricó esa imagen, a partir de las páginas o archivos que restaura y de las marcas
`*.tta`:
- ¿`/android/data` montado o desmontado?
- ¿Existía `BK1`/`BK2`?
- ¿Qué tipo de apagado se usó?

Usa el WBI de Sony del paquete (`build/wbi_silent/pkg405sony/`, `reports/film-pb-1-wbi-silent-20261128.md`) y
los scripts `make_init_bk.sh` y `load_init_bk.sh`. Conclusión pedida: qué receta de fábrica debemos imitar.

## A9 — Diseños híbridos implementables con SWD (un solo disparo)

Con lo que se sabe, propone y evalúa **como máximo 3** recetas para obtener una imagen que reanude.
Ejemplos: ruta A más forzar en `SyncAndroid_sus` solo la rama de desmontaje `0x1fb8`; ruta B saltando la espera
bloqueante; hacer tolerante el `mount_fs` de la reanudación. Para cada receta da:
- La dirección exacta.
- Las huellas de registro que prueban que se está en el proceso correcto (VA de usuario compartida entre
  procesos).
- El cambio mínimo de registro o de flujo.
- Qué estado deja en flash, el riesgo para la cámara y cómo se verifica.

Prohibido proponer parches que escriban en flash fuera de `nflasha5` ni cambios permanentes.

## A10 — Auditor adversarial de los hechos base

Verifica contra bytes, sin fiarte del texto, cada afirmación del bloque común:
- El desensamblado de `im.elf@0xa124..0xa14a` y `0xa262..0xa282`.
- `res_load_backup@0x1dc0..0x1dc8` (`mount_fs` ≠0 → `abort`).
- `SyncAndroid_sus`: solo tipo 8 llega a `0x1fb8`.
- La lectura del volcado de excepción: que `r7=0x10c` sea `tgkill` y el símbolo `raise`, y que la pila
  contenga retornos en libSyncAndroid `0x1dcd`/`0x1ed9`/`0x29d1`.
- Que `wdt_intr` con `STAT=0` venga de `em_reboot(0)` y no de un watchdog.

Señala cualquier error o salto lógico con evidencia. Revisa también si los informes previos citados contradicen
algo y quién tiene razón.
