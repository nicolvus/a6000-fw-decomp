# Evidencia — camino de ESCRITURA de un clip nuevo con el sector FBM `0x31` creado (QEMU)

Todo es QEMU sobre **copias** del volcado `/dev/nflasha4` (perfil `nf4`, `NFLASH4=1`): la cámara no se
ha tocado y no se ha usado `mcp_rea`. Informe: [`reports/clip-write-cs-wpb-20261126.md`](../../clip-write-cs-wpb-20261126.md).

## Resultado en una línea

Con el sector `0x31` creado y persistente, `ChangeSector(4,3)` pasa de `0x10100006` a **`0x10800010`**
(segundo fallo real, `fn==0` en la tabla estática `0x9D23FC`) y `WritePackBegin(4,3,0,0x800,&pack,0,0)`
pasa de `0x10100001` a **`0`**; pero `WritePackEnd` devuelve **`0x10800020`** (`FBS_UNCERTAIN_WRITE_POINT`)
y **no se escribe ni un byte** en `nflasha4` (0 B en los seis diffs).

## Ficheros

| fichero | qué es |
|---|---|
| `nf4clip.c` | sonda (2º `.so` precargado junto a `sonyshim.so`): espera a que `FBM::Init` llene `0xA3699C`, vuelca la tabla, llama **por dirección** a `ChangeSector 0x2B41B4`, `WritePackBegin 0x2B3D24`, `WritePackAdd 0x2B3C64`, `WritePackEnd 0x2B3B94`, descompone sus entradas (`0x2B2B18`, `0x2B2F48`, `0x2B3094`, `0x2B2BCC`, `0x2B1DCC`, `0x2B3000`, `0x2B4030`) y mide el diff byte a byte de `/nflasha4.img` contra `/usr/share/nflasha4.img` tras cada paso (más volcado hex de la página cambiada y búsqueda del relleno `0x5a`). Modos `NF4MODE`: `pre`, `post`, `both`, `fn`, `fnpost` |
| `pb_run_clip.py` | lanzador: `run.build_initrd(..., nflash4=IMAGEN)` + `qemu_cmd`, `-serial file:consola.log`; reescribe en memoria la línea `LD_PRELOAD=` de `im.sh` para precargar los dos `.so`, reenvía al invitado todas las variables `NF4*` y corta la VM al `[FBMC] FIN` |
| `comando.sh` | repetición completa: reconstruye `/tmp/nf4-post.img`, compila la sonda y lanza `runPre` (antes) + `runPost` (sector creado) + `runBoth` (InitB en el mismo proceso) |
| `dis_escritura.py` · `dis-escritura.txt` | desensamblado (capstone) de las 16 rutinas citadas (firmas, guardas, llamantes reales `0x5C9F7E`/`0x5CA164`, traductor de errores `0x2B242C`), la tabla estática `0x9D23FC` de 38 filas tal cual está en el fichero y la tabla de cadenas FBS de `0x7E9488` |
| `runPre/consola.log` | **antes**: tabla 1/30, `idx10 h0`; `ChangeSector(4,3)=0x10100006`; `WritePackBegin=0x10100001` (`bufferIndex=0xffff`); 0 B escritos; control `ChangeSector(0x22,8)=0x10800010` (sector `0xA0` con handle) |
| `runPost/consola.log` | **después**: imagen `6d2ab43a…` (la del parche C), arranque `idx10 h1/estado1/om6` **sin escribir nada**; `ChangeSector(4,3)=0x10800010`; `WritePackBegin=0` (`sector=0x31 handle=0x1 totalDL=0x800`); `WritePackAdd=0` (`curDL=0x800`); `WritePackEnd=0x10800020`; 0 B en todos los diffs; `GetSectorInfo(1)` y `FlashLib::WriteSector(1,0x10)` crudo `0x11` |
| `runPost2/consola.log` | repetición de `runPost` con la descomposición ampliada (`0x2B2BCC(4)=0 om=0x6`, `0x2B1DCC(6)=0`): los dos atajos de `ChangeSector` pasan, el fallo está en `0x2B4030` |
| `runBoth/consola.log` | control: `FBM InitB 6 3` sin `fn` → `- > 1` pero **0 B** y `idx10 h0` (no crea nada; confirma que el `1 300 B` del estado previo lo aporta `EWBDFD`, que registra `fn`) |
| `runFn/consola.log` | **prueba causal**: con `0x9D23FC[13].fn = stub propio` (antes `fn=0`, medido) y **sin** sector, `ChangeSector(4,3)=0x10100006` (no lo crea) y `BackupMgr::WriteBaseData(6,3)=0` escribe **1 300 B** (páginas `0x9D400`, `0xBD400`, `0x380000`); `GetSectorInfo(3)` ya da `validDataSize=0x200/currentSeekPoint=0x200` y `WriteSector(3,0x10)=0` con 16 B escritos (diff +512 B) |
| `runFnPost/consola.log` | **las dos cosas**: sector `0x31` + `fn` → `ChangeSector(4,3)=0` (1 816 B; 2 210 B tras `WritePackBegin`), `WritePackAdd=0` (`curDL=0x800`), `WritePackEnd=0` con **4 770 B** de diff y el relleno `0x5a` del payload en `0x3A0206`; `GetSectorInfo(1)` ya da `validDataSize=0x200`/`currentSeekPoint=0x200` |

Imágenes usadas (sha256):
- prístina = `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` → `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247` (10 485 760 B)
- «sector 0x31 creado» → `6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51`, reconstruida en `/tmp`
  con [`../fbm-sector31-c-20261126/reconstruye_imagen.py`](../fbm-sector31-c-20261126/reconstruye_imagen.py)
  (volcado + las tres páginas de 1 KiB de `fbm-sector31-c`; los 10 MiB no se versionan)
- sonda: `analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf4clip.so` → `4470d92da4a87df7a13f4504f6d3ec1716543f555a206479c49883d35956d361`

## Cómo se lanza

```sh
sh reports/evidence/clip-write-cs-wpb-20261126/comando.sh          # build + pre + post + both
# pasadas extra (prueba causal, ~1 min cada una)
NF4MODE=fn     NF4INJECT=30 python3 reports/evidence/clip-write-cs-wpb-20261126/pb_run_clip.py 240 \
  reports/evidence/clip-write-cs-wpb-20261126/runFn     analysis/camera-dumps/nand-20261020/dev_nflasha4.bin 30
NF4MODE=fnpost NF4INJECT=30 python3 reports/evidence/clip-write-cs-wpb-20261126/pb_run_clip.py 240 \
  reports/evidence/clip-write-cs-wpb-20261126/runFnPost /tmp/nf4-post.img 30
python3 reports/evidence/clip-write-cs-wpb-20261126/dis_escritura.py > …/dis-escritura.txt
```

Perfil del arnés: `analysis/gui/g22/harness/live/nf4/` (ignorado por git, como los demás `live/*`).
El `sonyshim.so` es el del arnés (`analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so`), sin recompilar.
Cada pasada tarda ~50 s de VM (corta al `[FBMC] FIN`); las cinco comparten el mismo `.so` y el mismo lanzador.
