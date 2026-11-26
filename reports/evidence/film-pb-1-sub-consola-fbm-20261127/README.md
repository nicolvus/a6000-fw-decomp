# Evidencia — FILM-PB-1 / sub-consola-fbm (27-11-2026)

Dos encargos: (1) tabla de comandos de la consola FBM y creación del sector 0x90 en el arnés;
(2) el anillo de entrada del monitor EX-PC y cómo meterle órdenes por ptrace.
Informes: `reports/film-pb-1-sub-consola-fbm-20261127.md` y
`reports/film-pb-1-sub-consola-fbm-anillo-20261127.md`.

| fichero | qué es |
|---|---|
| `sonyshim-fbm.c` | shim del arnés + hilo `PBINJECT`: consola REAL de FBM (handler `0x2B50D8`), volcado de `base+0xA3699C`, ensayo del anillo (`fbm_ring_test`) y prueba de ptrace (`fbm_ptrace_selftest`: `ptcall --dry/peek/poke/call` y `fbm_ring.sh`). `PBSKIP=1` sólo ptrace, `PBSKIP=2` sólo volcado |
| `comando.sh` | compila el shim (mismos flags que `shim/build.sh`) y lanza el perfil nuevo `fbm` |
| `pb_run_fbm.py` | lanzador: `run.build_initrd` + `qemu_cmd`, `-serial file:consola.log`, overlay `live/fbm/overlay`; corta al `[FBMC] FIN`. 3.er argumento = `SHIMEXTRA` (p. ej. `"PBSKIP=1"`) |
| `im_pb.sh` | guion del invitado (copia del de `sub-arnés-orden`, filtro ampliado a `FBMC/FBMP/ptcall/poke ok/ATTACH`) |
| `run0/consola.log` | **contraste de argc**: sin el nombre del módulo `InitB` devuelve 0 (rama de ayuda) |
| `run2`, `run3/consola.log` | **consola FBM**: `lookup("FBM")→base+0x2B50D9`, `InitB …`→1, tabla 0/30 antes y después, `CreateSector32 → 0x7`, `GetErrorString(7)="FBS_INVALID_PROCESS"` |
| `run4`, `run5/consola.log` | descriptor del anillo (`0xA4FD88`), objeto `0xA51AC4`, `mincore` del área (X distinto en cada arranque) |
| `run6/consola.log` | **anillo escrito a mano desde dentro**: `FBM SetSMI 20 90 7 1 10` → `A 0→24` y `idx 20 (0x90) h7/s1`; `InitB 6 3` y `LTC 1` consumidos |
| `run7`, `run8/consola.log` | primeras pruebas de `ptcall` en el invitado (aún sin salida: `/tmp/ptcall` no existía en el chroot) |
| `run9/consola.log` | `ptcall` con TID inválido (el `svc` de `gettid` no compilaba) |
| `run10`…`run14/consola.log` | depuración de la ruta y del binario (`/cam/tmp` es tmpfs, falta `/bin/sh`) y del `PEEKDATA` (devolvía `-14`) |
| `run15/consola.log` | `peek` real OK tras pasar el puntero `data`; el `call` hacía caer al trazador (siginfo de 16 B) |
| `run17/consola.log` | **`peek` de la tabla** (`10 00 00 00 …`), cabecera ELF, global `0x11111111`, **`poke` → `0x12345678`** |
| `run20/consola.log` | **`call GetErrorString(7)`**: `sig=11 code=1 fault=0xdead0000 ret=0xaeb03322 centinela=1`, `text=FBS_INVALID_PROCESS` |
| `run23/consola.log` | **línea base** (8 s, sin tocar nada): `0/30` entradas con handle≠0 |
| `run26/consola.log` | `ptcall ring` con `BASE` explícito: `X=0x8fa84000`, `ok B: 0 -> 24`, `idx 21 h7/s1` |
| `run27/consola.log` | **`fbm_ring.sh` completo** (maps → X → A/B → bytes → B): `idx 21 (0x91) h7/s1` tras `FBM SetSMI 21 91 7 1 10` |
| `evidencia/tabla-comandos-fbm.txt` | tabla completa de los 29 comandos (nombre, handler, sintaxis, descripción) |
| `evidencia/dump_tabla.py` | genera ese volcado desde `libmpr.so` |
| `evidencia/initb-cadena-y-tablas.txt` | OM/mediaID → nombre (0x7E6654 / 0x7E6364), tabla estática `{userID,mediaID,sector,OM}` de 0x9D23FC y desensamblado de `InitB` / `InitBackupData` |

Herramientas (fuera de esta carpeta): `tools/camera-ptrace/ptcall.c` (ARM estático: `peek|poke|call|ring`),
`tools/camera-ptrace/fbm_ring.sh`, `tools/camera-ptrace/build.sh`.

Perfil del arnés usado (gitignored): `analysis/gui/g22/harness/live/fbm/` — su `overlay/cam/usr/bin/`
lleva `ptcall`, `fbm_ring.sh` y `sh` (copia de `busybox`), y `overlay/cam/usr/lib/sonyshim.so`.
Cámara no usada; sólo QEMU.
