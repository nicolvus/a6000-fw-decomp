# Evidencia — FILM-PB-1 / sub-consola-fbm (27-11-2026)

| fichero | qué es |
|---|---|
| `sonyshim-fbm.c` | shim del arnés + hilo `PBINJECT` que ejecuta la consola REAL de FBM (handler 0x2B50D8) y vuelca `base+0xA3699C` antes/después; mide `FlashLib::CreateSector32` y `GetErrorString` por símbolo |
| `comando.sh` | compila el shim (mismos flags que `shim/build.sh`) y lanza el perfil nuevo `fbm` |
| `pb_run_fbm.py` | lanzador: `run.build_initrd` + `qemu_cmd`, `-serial file:consola.log`, overlay propio `live/fbm/overlay`; corta al `[FBMC] FIN` |
| `im_pb.sh` | guion del invitado (copia del de `sub-arnés-orden`, filtro `FBMC`) |
| `run3/consola.log` | **pasada buena**: `lookup("FBM")→base+0x2B50D9`, `InitB …` → 1, tabla 0/30 antes y después, `CreateSector32 → 0x7`, `GetErrorString(7)="FBS_INVALID_PROCESS"` |
| `run2/consola.log` | igual, con el volcado recortado a idx 0…23 |
| `run0/consola.log` | **contraste**: `argc` sin el nombre del módulo → `InitB` devuelve 0 (rama de ayuda); sirve para fijar la convención de `argc` |
| `evidencia/tabla-comandos-fbm.txt` | tabla completa de los 29 comandos (nombre, handler, sintaxis, descripción) |
| `evidencia/dump_tabla.py` | genera ese volcado desde `libmpr.so` |
| `evidencia/initb-cadena-y-tablas.txt` | OM/mediaID → nombre (0x7E6654 / 0x7E6364), tabla estática `{userID,mediaID,sector,OM}` de 0x9D23FC y desensamblado de `InitB` / `InitBackupData` |

Perfil del arnés usado (gitignored): `analysis/gui/g22/harness/live/fbm/`. Cámara no usada; sólo QEMU.
