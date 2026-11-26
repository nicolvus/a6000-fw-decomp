# Evidencia — camino de ESCRITURA de un clip nuevo con el sector FBM `0x31` creado (QEMU)

Todo es QEMU sobre **copias** del volcado `/dev/nflasha4` (perfil `nf4`, `NFLASH4=1`): la cámara no se
ha tocado y no se ha usado `mcp_rea`. Informe: [`reports/clip-write-cs-wpb-20261126.md`](../../clip-write-cs-wpb-20261126.md).

## Resultado en una línea

Con el sector `0x31` creado y persistente, `ChangeSector(4,3)` pasa de `0x10100006` a **`0x10800010`**
(segundo fallo real: `fn==0` en la tabla estática `0x9D23FC`) y `WritePackBegin(4,3,0,0x800,&pack,0,0)`
pasa de `0x10100001` a **`0`**; pero `WritePackEnd` devuelve **`0x10800020`**
(`FBS_UNCERTAIN_WRITE_POINT`) y **no se escribe ni un byte** en `nflasha4` (0 B en todos los diffs, el
relleno `0x5a` del payload no aparece). Con el `fn` registrado además del sector, todo devuelve `0` y
se escriben **4 770 B**.

## Las cinco pasadas (todas con el mismo `.so` y el mismo lanzador)

| pasada | imagen de entrada | modo | qué añade |
|---|---|---|---|
| `runPre/` | prístina `a5ab15ca…` | `pre` | «antes»: `ChangeSector(4,3)=0x10100006`, `WritePackBegin=0x10100001`, 0 B; control `ChangeSector(0x22,8)=0x10800010` (sector `0xA0`, que sí tiene handle) |
| `runPost/` | `6d2ab43a…` (sector `0x31`) | `post` | «después»: arranque `idx10 h1 esto1 om6` **sin escribir nada**; `ChangeSector=0x10800010`, `WritePackBegin=0`, `WritePackAdd=0`, `WritePackEnd=0x10800020`, **0 B**; `GetSectorInfo(1)` con `validDataSize=0xffffffff`; `FlashLib::WriteSector(1,0x10)=0x11` crudo |
| `runBoth/` | prístina | `both` | `FBM InitB 6 3` **sin `fn`** → `-> 1` pero `idx10 h0` y **0 B** (no crea nada) |
| `runFn/` | prístina | `fn` | **causal A**: con `0x9D23FC[13].fn = stub` (antes `fn=0`, medido) y **sin** sector: `ChangeSector=0x10100006` (no lo crea) y `WriteBaseData(6,3)=0` escribe **1 300 B** (páginas `0x9D400`, `0xBD400`, `0x380000`); `GetSectorInfo(3)` ya da `validDataSize=0x200/currentSeekPoint=0x200` y `WriteSector(3,0x10)=0` con 16 B (diff 1 812 B) |
| `runFnPost/` | `6d2ab43a…` | `fnpost` | **causal B**: sector + `fn` → `ChangeSector(4,3)=0` (1 816 B), `WritePackBegin=0` (2 210 B), `WritePackAdd=0` (`curDL=0x800`), `WritePackEnd=0` con **4 770 B** de diff y el relleno `0x5a` del payload en **`0x3A0206`** |

## Ficheros

| fichero | qué es |
|---|---|
| `nf4clip.c` | sonda (2º `.so` precargado junto a `sonyshim.so`). `NF4INJECT=<s>`: espera a que `FBM::Init` llene `0xA3699C`, vuelca la tabla de sectores (30×0x14) y la estática `0x9D23FC` (38×0x18), y llama **por dirección** a `ChangeSector 0x2B41B4`, `WritePackBegin 0x2B3D24`, `WritePackAdd 0x2B3C64`, `WritePackEnd 0x2B3B94`, a los pasos intermedios (`0x2B2B18`, `0x2B2F48`, `0x2B3094`, `0x2B2BCC`, `0x2B1DCC`, `0x2B3000`, `0x2B4030`) y a los símbolos exportados `FlashLib::GetSectorInfo` / `WriteSector`. Tras **cada** paso mide el diff byte a byte de `/nflasha4.img` contra `/usr/share/nflasha4.img`, vuelca la primera y la última página cambiadas y busca el relleno `0x5a`. Modos: `pre`, `post`, `both`, `fn`, `fnpost` |
| `pb_run_clip.py` | lanzador: `run.build_initrd(..., nflash4=IMAGEN)` + `qemu_cmd`, `-serial file:consola.log`; reescribe en memoria la línea `LD_PRELOAD=` de `im.sh` para precargar los dos `.so`, reenvía al invitado todas las variables `NF4*` y corta la VM al `[FBMC] FIN` |
| `comando.sh` | repetición completa: reconstruye `/tmp/nf4-post.img`, compila la sonda (imprime su sha256) y lanza las cinco pasadas |
| `dis_escritura.py` · `dis-escritura.txt` | desensamblado (capstone) de las 16 rutinas citadas —firmas, guardas, llamantes reales `0x5C9F7E`/`0x5CA164`, traductor de errores `0x2B242C`, `0x2B25D0`— con literales pc-relativos resueltos y cadenas; la tabla estática `0x9D23FC` tal cual está en el fichero (38 filas, `fn=0`) y la tabla de cadenas FBS de `0x7E9488` (`0x11 = FBS_UNCERTAIN_WRITE_POINT`) |
| `run*/consola.log` | la prueba de cada pasada (líneas `[NF4]`, `[FBMC] FIN`) |

Imágenes y sonda (sha256):
- prístina = `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` → `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247` (10 485 760 B)
- «sector `0x31` creado» → `6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51`, reconstruida en `/tmp`
  con [`../fbm-sector31-c-20261126/reconstruye_imagen.py`](../fbm-sector31-c-20261126/reconstruye_imagen.py)
  (volcado + las tres páginas de 1 KiB de `fbm-sector31-c`; los 10 MiB no se versionan)
- sonda: `analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf4clip.so` → `3cce22fc8aa8f556333bcf1555b5ac16461f441575c2b58b1adb3f6f3d40edaa`

## Cómo se lanza

```sh
sh reports/evidence/clip-write-cs-wpb-20261126/comando.sh        # build + las cinco pasadas (~1 min cada una)
python3 reports/evidence/clip-write-cs-wpb-20261126/dis_escritura.py > …/dis-escritura.txt
```

Perfil del arnés: `analysis/gui/g22/harness/live/nf4/` (ignorado por git, como los demás `live/*`).
El `sonyshim.so` es el del arnés (`analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so`), sin recompilar.
