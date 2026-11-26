# Evidencia — parche C: sector FBM `0x31` creado por la vía de consola, **persistente** (QEMU)

Todo QEMU sobre **copias** del volcado `/dev/nflasha4` (perfil `nf4`, `NFLASH4=1`): la cámara no se ha
tocado y no se ha usado `mcp_rea`. Informe: [`reports/fbm-sector31-c-persistente-20261126.md`](../../fbm-sector31-c-persistente-20261126.md).

## Resultado en una línea

El parche (`build/cfw_fbm_sector31_c/libmpr.so`, sha256 `831142ae…378e`) crea el sector en el primer
arranque escribiendo **1 300 B idénticos** a los de la vía de consola (`6d2ab43a…dca51`), y un **segundo
arranque con el `libmpr` de fábrica** registra `idx 10` solo (`CheckExistSector=0x45`,
`BkRead(0x04,3)=0x10100003`) **sin escribir un byte**.

## Ficheros

| fichero | qué es |
|---|---|
| `parche_fbm31_c.py` | constructor **y** auditoría: sha256 del original, bytes y semántica del `bl` del gancho, zona libre hasta `0x93B081`, PT_LOAD R+X con VA==offset, ausencia de relocaciones / `ldr|adr` pc-relativos / punteros u32 a la cueva, ensamblado con keystone (2 pasadas para las constantes PC-relativas), desensamblado instrucción a instrucción, diff exacto, cabecera/`PT_*`/secciones idénticas. `--fn-dummy` construye el **control negativo** |
| `auditoria-parche-c.txt` | salida del build final (`831142ae…`, 88 B previstos en 2 rangos, 81 cambian de valor) |
| `auditoria-control-fn-dummy.txt` | salida del control negativo (`f87cedd0…`, registra `fn=0x2B5185`) |
| `emula_cueva_c.py` · `emulacion-cueva-c.txt` | pre-vuelo Unicorn (Cortex-A15/Thumb-2), base `0xAE3E5000`: llamadas y argumentos exactos, guarda estricta (`handle=1`/`3` ⇒ sólo `FBM::Init()`), `fn` apuntando al stub `movs r0,#0; bx lr` |
| `dis_evidencia.py` · `dis-funciones-c.txt` | desensamblados citados: `0x2B1DEC`, `EWBDFD 0x2B5198`, dummy `0x2B5184`, `0x2B3000`, `0x2B2F48`, `0x2B2B18`, `0x2B3F7C`, `0x2B43F0`, `0x2B4030`, `TermSectorData`, `0x2A8750` |
| `resumen_imagen.py` · `imagen-diferencias.txt` | diff por páginas de 1 KiB, entradas de fileType de cada página de control, sha256 de la página de datos base y comparación con la página que dejó la consola |
| `comando.sh` | repetición completa (build, C1, C2, C3 y control) |
| `runC1/` | **primer arranque con el parche**, imagen D1 prístina: crea (`idx10 = 0x31 h2 1 om6`, `CheckExistSector 0x45`, `BkRead 0x10100003`), **1 300 B**, `nflash4.img` extraída (`6d2ab43a…`) |
| `runC2/` | **segundo arranque con el `libmpr` de fábrica** sobre la imagen de C1 (`gancho=a2 f7 9b f0`, `cueva=00…`): `idx10 = 0x31 h1 1 om6`, `CheckExistSector 0x45`, `BkRead 0x10100003`, **`NF4DIFF bytes_distintos=0`** |
| `runC3/` | parche C sobre la imagen ya escrita: misma tabla, **0 B** escritos (la guarda sale antes) |
| `runX-control-fn-dummy/` | control negativo: con `fn = 0x2B5185` (el dummy de `EWBDFD`) el arranque se cae en el dummy (`pc=addr=base+0x2B5186`, `lr=base+0x2B3FCB`), `EXIT=132`, sólo **394 B** (control sin datos) |
| `pagina-9D400.bin` · `pagina-BD400.bin` · `pagina-380000.bin` | las **tres páginas de 1 KiB** (3 KiB) que escribe C1; el resto de la imagen es el volcado `a5ab15ca…` sin tocar |
| `reconstruye_imagen.py` · `reconstruccion.txt` | reconstruye la imagen de 10 MiB en `/tmp` (volcado + 3 páginas) y comprueba que da `6d2ab43a…`; es la entrada de C2/C3 (los 10 MiB **no se versionan**) |
| `runC*/consola.log` | la prueba de cada pasada (líneas `FBMTAB`, `PROBE`, `NF4DIFF`, `alive=`) |

## Cómo se lanzan (resumen; `comando.sh` lo hace todo)

```sh
# build (final + control negativo)
python3 parche_fbm31_c.py
python3 parche_fbm31_c.py --fn-dummy --out ../../../build/cfw_fbm_sector31_c/control-fn-dummy/libmpr.so
# C1: crea. Imagen D1 prístina (por omisión del lanzador)
FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1 NF4IMG=1" \
  python3 ../film-pb-1-sub-fbm-create-20261126/fbm_run.py 200 runC1 ../../../build/cfw_fbm_sector31_c/libmpr.so
# C2: LA PRUEBA — segunda pasada SIN parche sobre la imagen de C1
FBMNFLASH4=runC1/nflash4.img FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1" \
  python3 ../film-pb-1-sub-fbm-create-20261126/fbm_run.py 200 runC2 ""
# C3: riesgo — parche cargado con el sector ya presente (debe escribir 0 B)
FBMNFLASH4=runC1/nflash4.img FBMFIN='--- IMEXIT' FBMEXTRA="FBMPROBE=1 NF4DUMP=1" \
  python3 ../film-pb-1-sub-fbm-create-20261126/fbm_run.py 200 runC3 ../../../build/cfw_fbm_sector31_c/libmpr.so
```

`fbm_run.py`, `sonyshim.so` (hilo `FBMTAB` + sonda `FBMPROBE`) e `im_fbm.sh` son los del sub-arnés
[`film-pb-1-sub-fbm-create-20261126`](../film-pb-1-sub-fbm-create-20261126/README.md), **sin
modificar**: sólo se les pasa la `libmpr` parcheada en el overlay y la imagen de `nflasha4`.
