# Evidencia — ¿devuelve 0 el cargador del IFO (`0x698EC8`) con el sector FBM `0x31` registrado?

Todo es QEMU (`scripts/gui/harness`), perfil `nf4`, `NFLASH4=1` sobre una **copia** del volcado
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` (sha256 `a5ab15ca…7247`). Cámara no tocada, `mcp_rea` no usado.
Informe: [`reports/film-pb-1-sub-msv-698ec8-20261126.md`](../../film-pb-1-sub-msv-698ec8-20261126.md).

## Resultado en una línea

Medido (`run6`): el sector `0x31` queda registrado (`idx10 = 0x31/h3/+8=1/om6`, 1 300 B) y `BkRead(0x04,3)=0x10100003`.
La cadena del IFO **no se ejecuta en el arnés** (0 capturas en las 6 funciones) y la llamada inyectada a `0x3AFA94`
**se bloquea en la traza OSAL**; con esa entrada medida, el código da: `0x35E04C→0x00500003` → `0x3AFA94` lo convierte
en *Need Salvage* y devuelve **0** → `0x698EC8` devuelve **0**.

## Ficheros

| fichero | qué es |
|---|---|
| `msvprobe.c` | 2.º `.so` precargado (junto a `sonyshim.so`): 6 trampas UDF en entradas de la cadena del IFO (`0x698EC8`, `0x3AFA94`, `0x35EA1C`, `0x698FB8`, `0x67CA6C`, `0x698F18`) con captura de `r0` y rearme; construye la clase con su ctor real `0x3B04A4`; llama por dirección a `0x3AFA94`/`0x698EC8` con captura de `SIGSEGV/SIGBUS` (siglongjmp) y **tope de 30 s** por llamada; objetos sintéticos; stubs temporales de macros de traza |
| `pb_run_msv.py` | lanzador: `run.build_initrd(..., nflash4=IMG)` + `qemu_cmd`, `-serial file:consola.log`, precarga `msvprobe.so` reescribiendo en memoria la línea `LD_PRELOAD=` de `im.sh`; corta en `[FBMC] FIN` |
| `comando.sh` | compilación y pasadas (reproducible) |
| `dis/libmpr-sha256.txt` | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` (fw 3.21) |
| `dis/01-698ec8-y-3afa94.txt` | `FlashLoadForMsv` `0x698EC8` y `MsvMcmd::RcsBackupTblData` `0x3AFA94` completos |
| `dis/02-35e04c-rama-10100003.txt` | `0x35EA1C` + `0x35E04C`: prólogo que pone a cero `0xd5/0xd6/0xd7` (`0x35E070-78`), `BkRead` `0x35E0F4`, rama de `0x10100003` (`0x35E118-66`), bloque `0x35E954` (`r5=0x00500003`) y epílogo que devuelve `r5` (`0x35EA08`) |
| `dis/03-clase-ctor-y-vtable.txt` | ctor `0x3B04A4` (vtable `0x835980`, `[this+0x50] = new(0x4B78)` + ctor `0x3B1DE8`), ctor del hijo `0x3B1DE8` (vtable `0x835FB8`) y ranura `+0xB8` = `0x3B16B1` (escribe `8` en `*pb`) |
| `dis/04-conversion-y-traductor.txt` | `0x3502CA → 0x3502B8 → 0x350124(código,[this+0x24])`; código 0 → `0x350242` devuelve 0; traductor `0x6F0D4C` con `status==0` → `0x6F0EA4` → 0 |
| `dis/05-2b39b8.txt` | `ReadFirstPackData` `0x2B39B8` (handle 0 → `0x10100001` en `0x2B3A28`) |
| `run1/`, `run2/` | 6 trampas armadas, **0 capturas** en 240 s: la cadena del IFO no se ejecuta (ni `0x698FB8`, ni `0x67CA6C`, ni `0x35EA1C`) |
| `run3/` | el ctor real `0x3B04A4` funciona en memoria del invitado (`[obj]=base+0x835980`, hijo en `[obj+0x50]`, `[+0x4088]=4`, `[+0x408c]=3`); la llamada `A1 0x3AFA94(msv)` **no vuelve** |
| `run4/` | control: anulando además los sumideros de log (`0x353708`, `0x35376C`, `0x3536DC`, …) la pasada **no llega a imprimir ni el inicio de la llamada** (7 stubs dejan el proceso sin avanzar): se descarta esa vía |
| `run5/` | sólo las dos macros TRACE (`0x34E468`, `0x34E490`) a `bx lr`: la llamada sigue sin volver (el hilo inyectado se queda dentro de la traza OSAL) |
| `run6/` | **la receta que sí funciona, medida en esta sesión**: `MSVONLY=1` (sin llamadas inyectadas) → `EWBDFD 4 3 0` (`0x9D23FC[13].fn = base+0x2B5184`), `0x2B3000(6,3)=0`; `InitB 6 3` → `idx10 = 0x31 / h3 / +8=1 / om6`, **1 300 B** en `nflasha4`; `BkRead(0x04,3)=0x10100003`; después, `SIN1` (objeto sintético) se queda en la macro de traza **sin llegar a usarlo** |

## Qué significa «no vuelve» (medido, no supuesto)

`0x3AFA94` empieza por la macro de traza `0x34E468(0x4f, 0x2000, 0, 0)` (`0x3AFAB2`) → `0x5BB83C` →
`osal_valloc_msg_wait` (`0x5BB884`), que espera un mensaje libre del *pool* OSAL. Llamado desde un hilo que no es
de OSAL, no vuelve. No es un fallo del código que se quiere medir: es el arnés.

## Imágenes / hashes

- copia de trabajo: `/tmp/nflasha4-origen.bin` = volcado `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247` (10 485 760 B)
- imagen con el sector (medida en sesiones anteriores, misma receta `EWBDFD 4 3 0` + `InitB 6 3`): `6d2ab43a…dca51` (1 300 B distintos)
