# Sector FBM `0x31` en la cámara: un comando por telnet, en seco y con vuelta atrás

**Fecha:** 26-11-2026 · **Script:** `scripts/film_pb1_sector31.py` · **Evidencia:** `reports/evidence/film-pb-1-sector31-runbook-20261126/`
**Estado de la cámara:** **no se ha ejecutado contra ella** (192.168.1.29/30/18 no responden). Todo lo medido aquí es el invitado del arnés (`NFLASH4=1` + telnet), nunca la cámara.

> **No reiniciar entre aplicar y grabar.** El `fn` de `0x9D23FC[13]` vive en `.data` y **no persiste**:
> `FBM EWBDFD 4 3 0` sólo lo deja en RAM de esa sesión. El **sector sí persiste** (está en `nflasha4`),
> así que la **lectura** queda arreglada para siempre, pero la **escritura** de un clip nuevo necesita el
> `fn` en el mismo arranque: medido en el invitado, con el sector persistido y `fn = 0` se vuelve a
> `ChangeSector = 0x10800010` / `WritePackEnd = 0x10800020` y **0 B escritos**; con `fn` en la misma
> sesión, `ChangeSector / WritePackBegin / Add / End = 0` y **4 770 B** (payload `0x5a` en `0x3A0206`).
> Por eso la secuencia es: aplicar → **sin apagar** → grabar el clip nuevo → reproducirlo. Si se reinicia
> antes de grabar se pierde el registro transitorio de `fn`. El paquete 3.97 también omite el alta
> de `fn` si `FBM::Init` ya encontró el sector. [Auditoría del 3.97](fbm-sector31-c-pkg397-20261126.md).

## Resumen (18 líneas)

1. El arreglo son **dos líneas** en el anillo del monitor EX-PC de `im.elf`: **`FBM EWBDFD 4 3 0`** y después **`FBM InitB 6 3`**. Criterio de OK: idx 10 de `base+0xA3699C` con `sector=0x31 handle≠0 valido=1 OM=6`.
2. **No se usa `FBM LTC 1`**: es un test de fábrica y sus escritores (`0x2B5724`/`0x2B5658`) escriben texto de prueba («MS »/«HDD » + «packData») en la página de datos base ([causa-fbm §6.2](film-pb-1-causa-fbm-20261126.md), [grabación-BD §17-18](grabacion-bd-fbm-20261126.md)).
3. `EWBDFD 4 3 0` escribe en `0x9D23FC[13]` el **dummy `0x2B5184`** (sólo log + `return 0`); crea igual (`idx10 = 0x31 h3 +8=1`, `BkRead = 0x10100003`, persiste tras reiniciar).
4. El escritor real de `(4,3)` es **`0x5CA354`**, registrado en **`0x5C9B06`** por `m2psIfo_Backup`, y **hoy nadie lo registra**. El dummy **no estorba**: el camino de grabación decide por `fileType` (`0x2B2F48`), no por `fn`, así que un clip nuevo queda registrado aunque `fn` sea el dummy.
5. Un solo comando: `python3 scripts/film_pb1_sector31.py --host <IP> --aplica --escribe` (§1).
6. Por defecto es **en seco**: sin `--escribe` no escribe nada (ni volcado, ni `ptcall`, ni el anillo). Si falla cualquier comprobación previa, aborta sin escribir.
7. Pasos: alcance → anillo → tabla → **volcado de rollback a la tarjeta** → subida de `ptcall` → línea 1 → línea 2 → relectura del idx 10 → veredicto OK/NO con los valores de antes y de después (§3).
8. El monitor confirma cada línea porque mueve `A` (índice de lectura): si no lo mueve en ~3 s, el script aborta.
9. Vuelta atrás: el fichero queda en la tarjeta con fecha, y `--restaurar FICHERO --escribe` lo devuelve con `dd` + `sync` + `md5` (§6). Ojo: escribir `nflasha4` a mano **salta el asignador del FBS**.
10. Comprobación a mano del resultado: un `ptcall peek` del idx 10 y del anillo (§4).
11. Verificado **en seco** contra el invitado del arnés (perfil `nf4`, telnet en `127.0.0.1:2323`): secuencia de lectura y depósito en el anillo, con veredicto OK (§7).
12. El plan de prueba posterior (clip nuevo de 5 s → reproducirlo → antiguos → recuperar BD) va en §5, con criterio de éxito y lectura del resultado por telnet.
13. Lo que el arreglo **no** hace: registrar clips viejos. El sector se crea vacío; los antiguos siguen sin IFO ([causa-fbm §6.3](film-pb-1-causa-fbm-20261126.md)).
14. Lo que **no** está verificado: el `poke` del anillo desde fuera del proceso en la cámara real, y `EWBDFD`+`InitB` en cámara real (sí en el arnés).
15. Antes de usarlo: cámara encendida, Tweak con `telnetd` (root, 23), misma red, MPR arrancado y tarjeta con ≥20 MiB libres (§2).

---

## 1. El comando

```sh
python3 scripts/film_pb1_sector31.py --host 192.168.1.29 --aplica --escribe
```

Variantes (mismo script, mismos ficheros):

| qué | comando | escribe |
|---|---|---|
| ver el estado, sólo lectura | `python3 scripts/film_pb1_sector31.py --host 192.168.1.29 --verifica` | no |
| simular el arreglo (plan) | `... --aplica` | no |
| aplicar | `... --aplica --escribe` | sí (volcado + `/tmp/ptcall` + 2 líneas) |
| vuelta atrás | `... --restaurar /mnt/sdcard/nflasha4-AAAAMMDD-HHMMSS.bin --escribe` | sí (`dd` al dispositivo) |

Opciones: `--port` (23), `--ptcall` (`/tmp/ptcall`), `--origen-volcado` (`/dev/nflasha4`), `--destino` (busca la tarjeta), `--espera` (3 s), `--comprobar-persistencia` (añade `FBM WBI`).
Código de salida: `0` OK · `1` NO/abortado · `2` uso.

## 2. Precondiciones (si falta una, el script aborta sin escribir)

1. **Cámara encendida y en la misma red** que el PC, alcanzable por telnet. IPs usadas en el proyecto: `192.168.1.29`, `192.168.1.30`, `192.168.1.18` (hoy ninguna responde).
2. **Tweak OpenMemories con `telnetd`** (busybox `telnetd -l sh`, puerto 23, **root sin contraseña**). El script verifica `id -u == 0` (o `/proc/self/status` si el busybox no trae `id`).
3. **MPR arrancado**: `pidof im.elf` da un PID y `/proc/PID/maps` es legible con `libmpr.so` en un mapeo `r-xp`. La base **se lee en cada ejecución** (ASLR: cambia entre arranques).
4. **Tarjeta SD montada** con **≥20 MiB libres** en `/mnt/sdcard` (o `/android/mnt/sdcard`; `--destino` si tu cámara la monta en otro sitio). Es el destino del volcado de rollback.
5. **`/dev/nflasha4` presente** (la partición del FBS; 10 485 760 B).
6. **`ptcall` compilado en el PC**: `sh tools/camera-ptrace/build.sh` → `tools/camera-ptrace/ptcall` (ARM EABI estático). El script lo sube por telnet si no está en `/tmp`.
7. Nada grabando ni reproduciendo (el arreglo escribe en la BD del MPR y hace `InvalidateSync`/`Sync`).

## 3. Qué hace cada paso

| # | orden que manda | para qué | criterio que exige el script |
|---|---|---|---|
| 1 | `id -u`, `pidof im.elf`, base con `awk '/libmpr\.so/ && /r-xp/'` (si no hay `awk`: `grep -aF libmpr.so … \| grep -aF r-xp \| cut -d' ' -f1 \| cut -d- -f1`) | identificar proceso y base | uid 0, PID y base de 8 hex |
| 2 | `ptcall PID 0 peek <base+0xA4FD88> 4` → `X`; `peek X 8` → `A`, `B` | estado del anillo del monitor | `X≠0`, `A,B < 0x400`, libres ≥ longitud de la línea |
| 3 | `ptcall PID 0 peek <base+0xA3699C> 0x258` | tabla de sectores (30 × 0x14) | — (foto del «antes») |
| 4 | `ls -l /dev/nflasha4` y `df -k <tarjeta>` | que hay de dónde volcar y dónde | existe y ≥20 MiB libres |
| 5 | `dd if=/dev/nflasha4 of=<tarjeta>/nflasha4-<fecha>.bin bs=1024` + `busybox md5sum` | **rollback** | 10 485 760 B y md5 de 32 hex |
| 6 | `echo -ne '\0NNN…' >> /tmp/ptcall`, `chmod 755`, `busybox md5sum` | subir la herramienta de peek/poke | md5 local = md5 en cámara |
| 7 | `ptcall poke <X+0x10+B> <bytes>` y `poke <X+4> <B+nuevo>` | depositar **`FBM EWBDFD 4 3 0`** + CR | `A` avanza = el monitor la consumió |
| 8 | ídem | depositar **`FBM InitB 6 3`** + CR | ídem |
| 9 | `ptcall peek <base+0xA3699C+0x14*10> 0x14` | releer idx 10 | `handle≠0` y `valido=1` → **OK** |

El depósito respeta el formato medido del anillo: se escriben **primero los bytes** (`X+0x10+B`, partiendo en dos si da la vuelta) y **después `B` con un solo store**, para que el monitor no vea media línea. Terminador **CR (0x0D)**; capacidad útil 0x3FF. Detalle: [anillo](film-pb-1-sub-consola-fbm-anillo-20261127.md).

## 4. Cómo comprobar el resultado a mano

En el propio telnet de la cámara (root); `ptcall` ya está en `/tmp/ptcall` tras `--aplica --escribe`:

```sh
PID=$(pidof im.elf | cut -d' ' -f1)
BASE=0x$(grep -aF libmpr.so /proc/$PID/maps | grep -aF r-xp | cut -d' ' -f1 | cut -d- -f1)
# 1) anillo: X, A, B
/tmp/ptcall $PID 0 peek $((BASE + 0xA4FD88)) 4        # -> X, p. ej. 0x9040b000
/tmp/ptcall $PID 0 peek 0x9040b000 8                  # -> A (4 B) y B (4 B), LE
# 2) idx 10 = sector 0x31: +0 sector, +4 handle, +8 valido, +0xC OM
/tmp/ptcall $PID 0 peek $((BASE + 0xA3699C + 0x14*10)) 0x14
```

- **Sector creado** ⇔ `+4` (handle) ≠ 0 **y** `+8` = 1. Medido en el arnés: `31 00 00 00 | 03 00 00 00 | 01 00 00 00 | 06 00 00 00`.
- **Antes del arreglo** el mismo peek da `31 00 00 00 | 00 00 00 00 | 00 00 00 00 | 00 00 00 00`.
- **Anillo vacío** ⇔ `A == B`; tras depositar, `B` sube y `A` le sigue en ≤1 s.
- La consola FBM **no contesta por el anillo**: `FBM View`, `GSS`, `InitB` escriben en el **log del MPR** (su salida no se puede leer con `peek` del anillo de entrada). `InitB` devuelve 1 siempre, así que **la única señal fiable es la tabla**.
- Si se quiere el log del MPR: `[0xA4FD88+4]` es la base del anillo de log (`0x82DF9000`, 0x8000 B); `ptcall peek` de esa zona y filtrar `[FBM]` da las líneas, pero **no está verificado en cámara** (en el arnés el área aparece vacía en el momento de la prueba).

## 5. Plan de prueba DESPUÉS de aplicar (en este orden)

Precondición: `--verifica` da el paso 1 con veredicto OK. Si el paso 2 falla, **no** se sigue.

### Paso 1 — el sector existe

```sh
python3 scripts/film_pb1_sector31.py --host 192.168.1.29 --verifica
```

- **Criterio de éxito:** `VEREDICTO: ... EXISTE` con `sector=0x31 handle≠0 valido=1 OM=6`, y `con handle != 0: 2/30` (idx 10 y el `0xa0` que ya estaba).
- A mano: el `peek` del idx 10 de §4.
- Si falla: repetir `--aplica` (en seco) y mirar el veredicto; no seguir al paso 2.

### Paso 2 — grabar un clip NUEVO corto (5 s)

**Por qué:** la escritura en la BD (`mp4` `0x37FC06`/`0x37FD4C` → `InitBackupData`) llevaba fallando por la guarda `fn==0`, así que **los clips que ya hay no tienen registro**. Si al grabar no da error, el registro del clip nuevo debería crearse (el camino de grabación decide por `fileType`, no por `fn`).

- Grabar **5 s** de vídeo (M y AVCHD/MP4, la tarjeta de siempre) y **parar** con el botón de grabación.
- **Criterio de éxito:** la cámara **no muestra error** al cerrar el clip, y el fichero está en la tarjeta:
  ```sh
  ls -l /mnt/sdcard/PRIVATE/M4ROOT/CLIP | tail -3      # MP4/AVCHD
  ls -l /mnt/sdcard/PRIVATE/AVCHD/BDMV/STREAM | tail -3
  ```
  Tamaño > 0 y fecha de hoy. Y `--verifica` sigue dando el paso 1 en OK (el sector no se ha perdido).
- **Si el paso 2 falla** (error en pantalla, clip de 0 B o no aparece): **no** tocar el paso 3. Recoger evidencia y volver atrás:
  ```sh
  python3 scripts/film_pb1_sector31.py --host 192.168.1.29 --restaurar <volcado> --escribe
  ```
  y reiniciar el MPR. El fallo del paso 2 con el paso 1 en OK apunta a `CreateSector32`/`WritePack` en la cámara (no al registro `fn`), así que lo siguiente es leer el log de FBM del MPR (`[FBM] BackupMgr::InitBackupData…`, `FlashLib`), no insistir con más líneas de consola.

### Paso 3 — reproducir ESE clip nuevo

- Reproducción → el clip recién grabado.
- **Criterio de éxito:** reproduce y **no** sale «No se puede visualizar.» (`0x1A` en `0x437C0A`). Si reproduce, el arreglo hace lo que se esperaba: la BD registra clips nuevos.
- Cómo leerlo por telnet, además de la pantalla: `--verifica` sigue en OK y el clip está en la tarjeta (mismas rutas del paso 2).

### Paso 4 — clips antiguos y, si no van, menú de recuperación

- Probar 2–3 clips grabados **antes** del arreglo.
- **Criterio de éxito esperado: que sigan fallando.** El sector se creó vacío y nadie rellena los registros viejos ([causa-fbm §6.3](film-pb-1-causa-fbm-20261126.md)). Que un clip viejo reproduzca sería una sorpresa que hay que anotar (¿ya tenía IFO?).
- Si no van, **Ajustes → «Recuperar BD imág.»**: reescribe `AVF_INFO/AVIN0001.INP` (`BeginRepair`) pero **no** crea sectores ni registra clips, así que no inventa registros; sirve para dejar el índice coherente. Criterio: el menú termina sin error y los clips antiguos siguen igual (o mejoran los que tenían IFO).
- Veredicto global del plan: **arreglo confirmado** = paso 1 OK + paso 2 sin error con clip nuevo + paso 3 reproduce. Los pasos 4 son diagnóstico de lo viejo, no criterio del arreglo.

## 6. Vuelta atrás

1. **Volcado** (automático en `--aplica --escribe`): `<tarjeta>/nflasha4-<AAAAMMDD-HHMMSS>.bin`, 10 485 760 B, con su `md5` impreso. **Conservarlo**: es la única copia del estado previo.
2. **Restaurar**:
   ```sh
   python3 scripts/film_pb1_sector31.py --host 192.168.1.29 --restaurar /mnt/sdcard/nflasha4-<fecha>.bin --escribe
   ```
   Hace `dd if=<fichero> of=/dev/nflasha4 bs=1024`, `sync` y compara `md5` del fichero y del dispositivo. Después hay que **reiniciar el MPR** para que `FlashLib` relea la partición.
3. **Ojo, riesgo real:** escribir `nflasha4` a mano **se salta el asignador del FBS y su libro de bloques**; si la geometría o los bloques malos relocalizados difieren, se escribe encima de otro sitio y una escritura parcial deja la BD peor que ahora. Con la cámara encendida y el MPR vivo, el volcado es coherente; aun así, restaurar es el último recurso.
4. **Alternativa sin escribir el flash**: `FBM WBI` (depositable con el mismo mecanismo) reconstruye `0xA3699C` desde el flash: si tras `WBI` el idx 10 sigue con handle, el arreglo está **persistido**; si vuelve a 0, no se escribió nada. El script lo hace con `--comprobar-persistencia`.

## 7. Verificación EN SECO contra el invitado del arnés

Perfil `analysis/gui/g22/harness/live/nf4` (`NFLASH4=1`: `/dev/nflasha4` = copia real del volcado del 20-10) **sin** precargar `nf4inject.so` (la inyección de consola ya no hace falta y ejecutaría `InitB` por su cuenta, contaminando el «antes»), y **telnet del invitado** (`busybox telnetd`, `hostfwd 127.0.0.1:2323 → 23`).

| paso | resultado (código de salida) | fichero |
|---|---|---|
| `--aplica` (en seco) | comprueba alcance, anillo, tabla, origen y destino; imprime el plan y **no escribe** (**rc=1**) | `1-aplica-seco.out` |
| `--aplica --escribe` | volcado de 10 MiB (`md5 b4142827…`) + `ptcall` subido (10 092 B, `md5 6e20b3a6…`, cuadra) + `FBM EWBDFD 4 3 0` (A 0→17) + `FBM InitB 6 3` (A 17→31) + relectura: idx 10 pasa de `0x31 h0 v0` a **`0x31 h3 v1 om6`** → **VEREDICTO OK** (**rc=0**) | `2-aplica-escribe.out` |
| `--verifica` | sólo lectura, con el sector ya creado: anillo `A=B=31`, tabla `2/30`, veredicto **EXISTE** (**rc=0**) | `3-verifica.out` |
| consola del invitado | `NET telnetd: puerto 23 (root, sin contraseña)` — el telnet es el del firmware | `consola.log` |

Reproducir: `VM_MEM=1024 QEMU_SMP=4 python3 reports/evidence/film-pb-1-sector31-runbook-20261126/verifica_arnes.py 420` (y `arranca_vm.py` para dejar la VM viva y probar a mano por `127.0.0.1:2323`).

Lo que demuestra: (a) la **secuencia de lectura** funciona entera — PID por `/proc`, base de `libmpr.so` por `maps`, `peek` del descriptor `+0xA4FD88`, del anillo y de las 30 entradas de la tabla; (b) el **depósito en el anillo llega al monitor**: cada línea movió `A` (0→17→31) y el efecto quedó en la tabla; (c) el **veredicto** distingue antes (NO existe) de después (EXISTE) con los mismos valores que el arnés mide por dentro.

Diferencias del invitado (su busybox de `.net/bin` tiene 92 applets): no hay `awk`, `df`, `id`, `tr` ni `head`; por eso la prueba pasó `--origen-volcado /nflasha4.img` (el nodo `/dev/nflasha4` lo intercepta el shim dentro de `im.elf`) y `--destino /tmp` (con aviso de que no puede leer el espacio libre). En la cámara real el busybox del Tweak sí trae `awk`/`df`/`id` y los caminos son `/dev/nflasha4` y `/mnt/sdcard`.

## 8. Límites (NO VERIFICADO)

1. **La cámara no se ha tocado**: no está en red; todo lo ejecutado es QEMU.
2. `ptcall poke` **desde fuera del proceso** está verificado en el invitado (QEMU ARMv7), no en la cámara real.
3. `FBM EWBDFD 4 3 0` + `FBM InitB 6 3` está medido en el arnés con `NFLASH4=1`; **en la cámara no**.
4. La ruta de la tarjeta (`/mnt/sdcard`) se deduce de los scripts existentes; si en tu cámara es otra, `--destino` lo resuelve.
5. El plan de §5 solo se puede completar con la cámara delante: el paso 3 (reproducir el clip nuevo) es la prueba real del arreglo.
