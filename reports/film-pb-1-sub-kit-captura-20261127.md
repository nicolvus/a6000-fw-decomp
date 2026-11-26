# FILM-PB-1 · kit de captura: cuál de los tres productores de `MPR::ER_FAILED` (0x1A) dispara (27-11-2026)

Estado: **kit escrito y probado en seco**, **no ejecutado contra la cámara** (sin ping a `192.168.1.30`, sin USB,
sin adb). Entrega: `scripts/camera_filmpb1_trace.py` (un fichero, solo stdlib) y transcripciones reales en
[`evidence/film-pb-1-sub-kit-20261127/`](evidence/film-pb-1-sub-kit-20261127/).

## 1. Veredicto

Un comando arma tres puntos de parada de un solo golpe y dice **cuál** de los tres caminos hacia el `0x1A` se ejecutó,
en qué orden y con qué registros, tras comprobar mapas, base de la sesión y 16 B por punto contra el `libmpr.so` local
(SHA-256 `9a74a3bb…4c30`, el auditado). Sin cámara sale con `cámara no accesible` y código **3**, sin traza de excepción.
Falta solo el paso físico E1 de la auditoría del 27-11.

## 2. Método: lo ya probado en el proyecto (no se inventó otro)

| Pieza | Precedente | Uso |
|---|---|---|
| Transporte y mapas | `scripts/camera_telnet.py` (telnet root del Tweak) y `/proc/PID/maps` de `analysis/camera-dumps/20261117-traza-T1/im_elf_maps.txt` (PID 143 de `im.elf`) | órdenes y bases de la sesión |
| Lectura de memoria | `camera_darwin_buffers.py:19`, `camera_tipo2_sweep.py:21` — `dd` + `hd` de toybox por `chroot /android`, **el busybox no trae `od`/`hexdump`** | 16 B por punto |
| Subida y ptrace | `camera_push_file.py` (`echo -ne` octal, 96 B) + `tools/camera-ptrace/{sctrace.c,build.sh}` (clang `-nostdlib`, `svc 0`) | auxiliar `/tmp` |
| Breakpoint de un golpe | `scripts/swd_bp_unico.sh:1-10` (se desarma al saltar) | igual, en espacio de usuario |

Los *breakpoints* SWD del proyecto paran las CPU del BIONZ (`0x43…` de `av-cam`), no el espacio de `im.elf`, y no
hay `gdb`/`gdbserver` en la cámara (`camera-reset-logs.md:11`). El riesgo se asume con lo de §5: **ptrace sobre
`im.elf` puede coincidir con una petición de reset y `sctrace` nunca se probó con éxito** (`camera-reset-logs.md:14`).

## 3. Los tres puntos (VA del ELF de `libmpr.so`, base 0; en REA suman +0x10000)

| Pto | VA ELF | instrucción (capstone, 3.21) | 16 B / md5 | Qué mide |
|---|---:|---|---|---|
| **A** | `0x437C0A` | `movs r3, #0x1a` tras el log «Pb Disable!! ref) dsm get» | `1a 23 fb 63…` / `d2423e98…` | guarda de **capacidades** (`FUN_00457A1E`, bitmap `[core+0xDB8]`) |
| **B** | `0x437C3C` | `movs r3, #0x1a` tras «Detect UnSupported Content » | `1a 23 fb 63…` / `80f5cd83…` | guarda de **contenido** (`FUN_00457F26`, `vtable+0x58`) |
| **T** | `0x7111B0` | `and r3, r0, #0xff000000` / `cmp.w r3, #0x1c000000` | `00 f0 7f 43…` / `9e1207b1…` | **traducción** del error interno de `PbStart` a código MPR |
| C1/C2 (`--callsites`) | `0x437C7E` / `0x437CFC` | `bl #0x7111b0` | `d9 f2 97 fa…` / `d9 f2 58 fa…` | qué `bl` invocó la traducción |

**Interpretación (la imprime el script):** **A** ⇒ `0x1A` de capacidades/«dsm» ⇒ hipótesis **H1** (arranque; el CFW
quita `nflasha5`/WBI). **B** ⇒ contenido no soportado ⇒ **H2** (contenido/BD; control «Recuperar BD imág.»). **T** ⇒
viene del **motor**; el `lr` del golpe dice desde dónde: `lr-4 = 0x437CFC` ⇒ fallo de `PbStart`; `lr-4 = 0x437C7E` ⇒
falló la **precondición** `FUN_00457DA8` (también acaba en `0x1A` y no es el motor: para eso está `--callsites`).
Sin golpes ⇒ no se reprodujo el vídeo o el core no estaba en estado 5 (habría dado `0x0A`) ⇒ subir `--secs`.

## 4. Procedimiento exacto

Requisitos: cámara encendida con el Tweak (telnet root en el 23) y `/proc/PID/mem` legible como root (lo fue el 17-11-2026);
`clang` + `lld` en el PC; el `libmpr.so` de fábrica 3.21 en `firmware/extracted/fw321/…/lib/` (el script aborta si su SHA-256
no es el auditado). Sin `.venv` y sin `adb`.

```bash
python3 scripts/camera_filmpb1_trace.py --verify    # 1. mapas + bases + 16 B por punto (no escribe)
python3 scripts/camera_filmpb1_trace.py --dry-run   # 2. todo menos escribir en la cámara
python3 scripts/camera_filmpb1_trace.py             # 3. traza real (30 s armada)
python3 scripts/camera_filmpb1_trace.py --secs 60 --callsites --log /tmp/fpb1.txt
```

Modo real: (1) local: SHA-256 de `libmpr`/`libObj` y 16 B esperados; (2) compila el auxiliar ARM estático (6 244 B,
sha256 `9fdfed46…8afd`) y lo sube a `/tmp/filmpb1bp`; (3) busca el PID de `im.elf` (`pidof` de toybox; si falla,
`ls -l /proc/*/exe`), lee `/proc/PID/maps` y calcula `base + VA` **de esta sesión** (no usa las bases de traspaso
0x06B95000/0x05AB2000; el 17-11-2026 fueron libmpr `0x06C7E000`, libObj `0x05B9B000`); (4) comprueba los 16 B de cada
punto **antes** de escribir; (5) `PTRACE_ATTACH` a todos los hilos (todos o ninguno) y `UDF 0xde00` solo donde el
halfword coincide; (6) espera 30 s mientras se reproduce el vídeo, imprime cada golpe (`H ms= i= tid= pc= r0..r3 lr=`)
y desarma el punto al saltar; (7) restaura lo que quede, `PTRACE_DETACH`, relee los 16 B, reescribe si algo no cuadra,
borra auxiliar y registro, y da el veredicto. Salidas: `0` correcto · `2` error local · `3` cámara no accesible ·
`4` mapas/hash no cuadran · `5` sin golpes.

## 5. Qué escribe en la cámara y cómo se deshace

Solo tres cosas: un fichero de 6 244 B en `/tmp` (tmpfs), los **2 B `00 de`** en la primera mitad-palabra de cada punto y
`/tmp/filmpb1.log`. Nada de NAND, `/usr` ni `/dev/mem`. Garantías: no se escribe si el halfword leído ≠ esperado; un punto
se restaura **antes** de reanudar el hilo (nunca queda un `UDF` que ejecutar); si el auxiliar muere por SIGKILL o se corta
el telnet, la comprobación posterior reescribe los 16 B por `/proc/PID/mem` e informa `intacto`/`ALTERADO`. Los hilos
creados **después** de armar no quedan trazados: la ventana es corta y los puntos solo los toca FeaCore.

## 6. Transcripción real sin cámara (`--dry-run` y `--verify`)

Completas en [`dry-run-sin-camara.txt`](evidence/film-pb-1-sub-kit-20261127/dry-run-sin-camara.txt) y
[`verify-sin-camara.txt`](evidence/film-pb-1-sub-kit-20261127/verify-sin-camara.txt). Extracto literal:

```
$ python3 scripts/camera_filmpb1_trace.py --dry-run
1) comprobación local de los .so auditados
libmpr   …/nflasha15_unpacked_unpacked/lib/libmpr.so
         10321204 B  sha256 9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30
         sha256 = el auditado (3.21 de fábrica)  OK
  pto  VA ELF     instrucción               md5(16 B)  bytes
  A    0x00437C0A movs r3, #0x1a            d2423e98…  1a 23 fb 63 7e e0 07 f1 68 06 96 e8 0f 00 8d e8
  B    0x00437C3C movs r3, #0x1a            80f5cd83…  1a 23 fb 63 95 f8 24 30 00 2b 62 d0 96 e8 0f 00
  T    0x007111B0 and r3, r0, #0xff000000   9e1207b1…  00 f0 7f 43 b3 f1 e0 5f 80 b5 00 af 40 f0 f2 80
2) binario auxiliar (se compila aquí; solo se sube en la traza real)
  /tmp/filmpb1bp: 6244 B, ELF32 ARM estático, sha256 9fdfed46d9002b57…
3) cámara
   cámara no accesible: 192.168.1.30:23 (TimeoutError)
EXIT=3
```

`--verify` recorre lo mismo sin el auxiliar y termina igual (`cámara no accesible`, **EXIT=3**); `--simular` (§7) llega al final.

## 7. Ensayo del camino completo sin cámara

`--simular MAPS` sustituye la cámara por un volcado real de `/proc/PID/maps` (`--simular-hit` simula además el golpe). Con
el volcado T1 del 17-11-2026 calcula **libmpr `0x06c7e000`** → `0x070B5C0A`/`0x070B5C3C`/`0x0738F1B0`, **libObj `0x05b9b000`**
→ `0x064845B0`, los cuatro hashes coinciden con los `.so` locales, los tres golpes dan su veredicto y `none` da `SIN GOLPES`
(EXIT=5); `--autotest` valida las reglas de lectura. En [`ensayo-simulado.txt`](evidence/film-pb-1-sub-kit-20261127/ensayo-simulado.txt),
[`autotest.txt`](evidence/film-pb-1-sub-kit-20261127/autotest.txt) y, para las salidas de error del auxiliar con `qemu-arm`,
[`auxiliar-qemu.txt`](evidence/film-pb-1-sub-kit-20261127/auxiliar-qemu.txt).

## 8. Corrección: la traducción está en `0x7111B0`, no en `0x7211B0`

Los informes del 26-11 y 27-11 la llaman `FUN_007211B0` (`0x7211B0`), pero contra bytes: `0x437C7E` y `0x437CFC` decodifican
`bl #0x7111b0`; `0x7111B0` empieza por `and r3, r0, #0xff000000` + `cmp.w r3, #0x1c000000` (traducción de códigos
`0x1C0000xx`), y el sitio `0x1C00001A → 0x1A` que ese informe cita como `0x711232` cae **dentro** de ella: un dígito
desplazado. El kit usa `0x7111B0`; el hash no lo habría detectado (se compara contra el mismo `.so`).

## 9. NO VERIFICADO

- **Nada del camino físico**: ni `pidof`, ni `/proc/PID/mem` en esta sesión, ni el `PTRACE_ATTACH/POKETEXT` real
  (qemu-arm devuelve `ENOSYS` en `ptrace`: solo se probaron las salidas de error del auxiliar).
- Que `im.elf` tolere el attach de todos sus hilos sin reinicio ni bloqueo de UI (`camera-reset-logs.md:14`); orden
  recomendado: `--verify` → `--dry-run` → traza con `--secs 20` y el vídeo ya en pantalla.
- Que el busybox acepte `echo -ne` de 96 B y `/bin/busybox md5sum` (si no hay `md5sum`, lo dice y valida por tamaño).
- Cuál de los tres productores dispara de verdad: es exactamente lo que mide el kit.
