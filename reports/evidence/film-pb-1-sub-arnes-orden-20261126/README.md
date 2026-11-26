# Evidencia — sub-arnés-orden (FILM-PB-1)

Ejecución de `0x437BC0` (FeaCore::PlayMovie) en el arnés QEMU con el FeaCore real, sin pasar por la UI.

| Fichero | Qué es |
|---|---|
| `sonyshim-orden.c` | copia del `sonyshim.c` del arnés + hilo `PBINJECT` (resuelve `MprIfMcmd::mp_mprIf`/`mp_feaCore` por `dlsym`, llama a `FeaIf::PlayMovie` real y, si hace falta, a `0x437BC0`; escribe la traza en `/dev/console`) |
| `pb_run.py` | arranque: initrd como `run.py`/`live.py` (overlay del arnés + `pbo` + cabeza FAT32 de `~/A6000-SD`) y QEMU con `-serial file:consola.log`; corta al ver `PBINJ FIN` |
| `im_pb.sh` | copia de `im.sh` con un volcado final de las líneas `PBINJ`/`TRACE` (no se usa en las pasadas buenas: la consola ya las lleva) |
| `comando.sh` | compilación exacta del shim y ejecución |
| `runC/consola.log` | 1.ª pasada: localización de objetos; revela que `MprIfMcmd::mp_owner` **no** es el MprIf |
| `runD/consola.log` | vía (a) con estado real 2 → `0x0A`; después vía (b) con estado 5 → guarda A → `0x1A` |
| `runE/consola.log` | repetición de runD (el `PBFORCE` no llegó al invitado en esa pasada) |
| `runF/consola.log` | **pasada buena**: `PBFORCE` → estado 5 antes de `FeaIf::PlayMovie` real → despachador → guarda A → `0x1A` |

Resultado: `[core+0x1F0]=2` (estado real) ⇒ `0x0A`; con estado 5, `[core+0xDC0]=0` (media) ⇒ guarda A
(`0x437C0A`) ⇒ `0x1A`; la guarda B no se ejecuta. Detalle en `../../film-pb-1-sub-arnes-orden-20261126.md`.
