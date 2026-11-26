# FILM-PB-1 · Sub-paquete con el `AV-CAM.BIN` de fábrica 3.21 (CFW 3.94, sin el PP del núcleo)

26-11-2026. Paquete construido **offline**: no se ha instalado nada, no se ha tocado la cámara ni
`firmware/`. Base = el paquete **instalado** `build/cfw_func393/pp/` (3.93). Lo único que cambia es el
núcleo BIONZ: el `AV-CAM.BIN` de dentro de `nflasha3` pasa a ser **byte a byte el de fábrica 3.21**.

| Dato | Valor |
|---|---|
| Versión del contenedor | **3.94** (mayor que 3.93; Darwin v3; sin `nflasha5` = `--sin-wbi`) |
| **`.dat`** | `build/cfw_avcam_limpio/firmware_packed-3.94.dat` (enlace duro) = `build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat` (**172 661 912 B**) |
| **sha256 del `.dat`** | **`2a6fd62ff4ed0e63af31a73a2dfb0b261700515147c421f8026b9463dd284c1c`** |
| `.fdat` | `…/firmware_packed.fdat`, sha256 `b2d0c36b74cbd16349964032e1e5d712f7b9ebffbc55e8adc6312a724d0376ac` |
| `firmware.tar` de dentro (104 miembros) | `build/cfw_avcam_limpio/pkg-3.94/firmware.tar`, 171 843 072 B, sha256 `92dfeb6adcf1ee247144ab7b7b5db2c231a193b98b1ff87fa3f7c928b3451e0d` |
| `AV-CAM.BIN` resultante | 11 427 236 B, sha256 **`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`** (= `build.AVCAM_SHA256`, el de fábrica) |
| `nflasha3` resultante | 11 488 768 B (antes 11 504 128), sha256 `dcd6994baa51ecd0e6e38c1a127992c83ccace482193eb7c7d4730c165b70b43` |
| Estado | **CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA** |

> Nota de nombres: la versión **3.94** ya la usan otros builds (`build/og113/pkg-3.94`, `build/cfw_func394/sin_iso/pkg-3.94`)
> con contenido distinto. Este paquete se identifica por el sha256 del `.dat`, no por el número.

## 1. Qué se ha construido

El paquete 3.93 instalado es «userland del CFW Film» + «núcleo parcheado» (PP del núcleo, S-Log3,
B/N monocromo, Hi-Light, Silent calibrado R87, LUT de películas, ISO 409600 y los 40 B del «BIONZ 3.38»).
Este 3.94 deja **el userland idéntico** (mismo `nflasha15-393.bin`) y **el núcleo de fábrica**: sustituye
`AV-CAM.BIN` por el del tar oficial 3.21 y recompone solo los bloques TPZL tocados y `part_image.sum`,
con los mismos módulos que usa `scripts/gui/build_base_pp.py` (`scripts/e25_27/{tarball,tpzl,fatimg,sums}`).

## 2. Comandos exactos (reproducibles)

```bash
# 1) tar con el av-cam de fábrica (hook `bionz` = identidad): TPZL + part_image.sum
python3 reports/evidence/film-pb-1-sub-paquete-avcam-limpio-20261126/construir.py \
  build/cfw_func393/pp/base-film.tar build/cfw_avcam_limpio/base-film-avcam321.tar
# 2) paquete 3.94 (mismo camino que la 3.93: Darwin v3 + sin WBI)
python3 scripts/gui/build_package_nflasha15.py \
  build/cfw_func393/pp/nflasha15-393.bin build/cfw_avcam_limpio/pkg-3.94 \
  --base-tar build/cfw_avcam_limpio/base-film-avcam321.tar --version 3.94 --darwin-v3 --sin-wbi
# 3) auditoría del contenedor (misma invocación que la 3.93)
python3 scripts/gui/audit_package_nflasha15.py \
  build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat \
  build/cfw_func393/pp/files --darwin-v3 --sin-wbi --bionz-g22
```

`--sin-wbi` **sí**: la 3.93 se construyó con `sin_wbi=true` (`build/cfw_func393/pp/pkg-3.93/container.json`),
o sea que `dev/nflasha5` ya estaba fuera; mantener el criterio deja el paquete comparable (104 miembros)
y la única diferencia con lo instalado es el núcleo. `--darwin-v3` también igual que la 3.93.

## 3. Verificación (todo MEDIDO, no inferido)

Evidencia: `reports/evidence/film-pb-1-sub-paquete-avcam-limpio-20261126/`
(`construir.json`, `comparar_tars.json`, `comparar_avcam.json`, `auditar.json`, `verificar_dat.json`).

| Comprobación | Resultado |
|---|---|
| `AV-CAM.BIN` leído de vuelta del tar nuevo == av-cam de fábrica 3.21 | **sí**, 11 427 236 B, sha `b60c845c…6bb9` |
| `part_image.sum` válida (`sums.verify`) para `dev/nflasha3` | **sí** |
| Línea de suma | antes `0,46d66c73,00af8a00,…` → después `0,b5b1ca79,00af4e00,000001a4,00000000,000003e8,root,root,-1,-1,dev/nflasha3,` |
| Resto de miembros del tar (105 = 104 + `nflasha5`) intacto: nombre, orden, cabecera y SHA-256 | **sí**, 0 alterados |
| `nflasha15` intacta entre tar de entrada y de salida | **sí** (mismo sha256) |
| Descomprimido de `nflasha3`: todos los bytes distintos caen en los clústeres de `AV-CAM.BIN` | **sí** (34 013 B, 0 offsets fuera) |
| Bloque TPZL 0 igual al de Sony (R55) | **sí** |
| Disposición TPZL: 369 bloques, contiguo, alineado a 512 B, 0 violaciones LDEC, máx. 126 sectores | **sí** (`max_sectores` = el límite de Sony) |
| Contenedor: `dend`, descifrado == `.fdat`, CRC de cabecera, modelo/región, updater oficial 3.21 | **sí** (auditoría) |
| Extreme a extreme desde el `.dat` cifrado: `AV-CAM.BIN` extraído == fábrica | **sí**, sha `b60c845c…6bb9` (`verificar_dat.json`) |
| Extreme a extreme: `part_image.sum` del `.dat` válida y tar del `.dat` == tar en disco | **sí** |
| Reproducibilidad: segunda ejecución de `construir.py` sobre la misma base | mismo tar (`0f10c940…`) y mismas comprobaciones |

## 4. Auditoría `audit_package_nflasha15.py`: 27/29 (las dos rojas son de diseño)

Base de la auditoría: `.dat` del 3.38 (`analysis/e25-27/artifacts-338/package-3.38/`). Verdes: contenedor
(7/7), tar (4/4), `nflasha15` (8/8: partición, LDEC, alineado, contiguo, nº de bloques, `max_sectores`,
bloque 0, decodificador independiente), ext2 (4/4: ficheros = los del paquete, hashes, modo/uid/gid, fsck
solo contadores), Darwin v3 (2/2) y bloque 0 / nº de bloques de `nflasha3` (2/2).
Cambios vs base 3.38 detectados: `nflasha15`, `nflasha3`, `part_image.sum`, `darwin_core`, `darwin.sum`;
quitado: `dev/nflasha5` — exactamente lo previsto.

Rojas, **esperadas y no son un defecto**:

- `g22.bionz_es_3.38_mas_patch_tristate` — el auditor conoce solo las variantes **parcheadas** del núcleo
  (3.38+tristate, PP, objetivos, Film, Film+PP, mezclas G109, opengate). El av-cam de este paquete es el
  de fábrica, que no es ninguna de ellas.
- `g22.bionz_solo_cambia_el_parche` — consecuencia de la anterior.

La comprobación que el auditor intentaba hacer queda cubierta **más fuerte** fuera de él: igualdad byte a
byte con el binario de fábrica `firmware/extracted/fw321/…/av-cam.bin` (= `build.AVCAM_SHA256`), verificada
en el tar y otra vez a través del `.dat` cifrado. Enseñar esa variante al auditor queda como pendiente
(no se ha modificado una herramienta de certificación compartida dentro de una tarea de build).

## 5. Qué cambia respecto al paquete instalado (3.93)

Comparación de los dos `firmware.tar` (`comparar_tars.json`) y del `.dat` (`verificar_dat.json`):

| Miembro | 3.93 instalado | 3.94 limpio |
|---|---|---|
| `0700_part_image/dev/nflasha3` | 11 504 128 B, sha `cdbaf960…54b4` | 11 488 768 B, sha `dcd6994b…b0b43` |
| `0701_part_image_sum/part_image.sum` | sha `697ae954…e2e` | sha `2463fd0b…ef2e` (solo la línea de `nflasha3`) |
| Otros 102 miembros (`nflasha15` = /usr, `darwin_core`, `darwin.sum`, `nflasha7`, `nflasha16`, `appli.sum`…) | — | **idénticos** |
| `0700_part_image/dev/nflasha5` (WBI) | ya quitado | igual (quitado) |

Dentro de `nflasha3`, el único fichero que cambia es `AV-CAM.BIN` (`vmlinux.bin` 3 478 912 B e
`initrd.img` 4 079 616 B, sin tocar; ningún byte fuera de sus clústeres). **34 013 B** distintos, en 33
zonas (`comparar_avcam.json`), que se reparten así:

| Capa | Bytes | Dónde |
|---|---:|---|
| A — parches del «BIONZ 3.38» del proyecto (fábrica 3.21 → av-cam del 3.38) | 40 | 4 tramos en 2 zonas: `0x00300472..0x00300488` y `0x0038F1A2..0x0038F1C2` (`patch_tristate`/EFCS) |
| B — lo que añadía el 3.93 encima (PP del núcleo, Silent r5, S-Log3, B/N, Hi-Light, películas, ISO) | 33 992 | 25 zonas de código de ≤112 B (`0x26172C`..`0x7746FE`), 7 de tablas/datos en `0xA6E290`..`0xA76E6A` (la mayor, 33 084 B: `0xA6E300..0xA7643C`) y 1 de 60 B en `0xAC04A8..0xAC04E4` |
| A ∩ B (el PP del núcleo reescribe 19 B de A) | 19 | dentro de las dos zonas de A |
| **Total instalado vs fábrica** | **34 013** | 659 tramos contiguos → 33 zonas con hueco de 16 B, de `0x26172C` a `0xAC04E4` |

**Consecuencia práctica:** el 3.94 es **userland del 3.93 con núcleo de Sony**. Los menús y ajustes
(PP, Film, Silent, ISO) siguen en `/usr` porque `nflasha15` no se toca, pero **su lado núcleo desaparece**:
ni LUT/curva de películas, ni tablas PP, ni S-Log3/B-N, ni Silent calibrado R87, ni el estado triple de
EFCS. Sirve para aislar si el fallo de reproducción (`0x1A`) depende del núcleo parcheado — no para uso
normal. `vmlinux`, `initrd` y el resto del firmware siguen siendo los de 3.21, así que no hay desajuste de
versión.

## 6. Límites

- **No instalado** y sin probar en cámara; el `.dat` no se ha validado con el actualizador real.
- El av-cam de fábrica pierde los parches del CFW (ver §5): con él, Silent/EFCS/PP/Film no deben
  comportarse como en el 3.93.
- La auditoría es 27/29 por las dos comprobaciones de identidad del núcleo explicadas en §4.
- `build/cfw_avcam_limpio/` ocupa ~695 MB (tar base nuevo + tar empaquetado + `.dat` + `.fdat`; el `.dat`/`.fdat` de arriba son enlaces duros al paquete, no copias).
