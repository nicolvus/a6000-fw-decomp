# FILM-PB-1 · Sub-paquete 4.05: `pp` + `libmpr.so` con las dos guardas de `PlayMovie` anuladas

26-11-2026 (offline, sin cámara). **Construido y auditado; NO instalado.** Artefacto:
`build/cfw_bypass_guardas/pkg-4.05/package-4.05/firmware_packed.dat`, sha256 `670f7c8a…c2ea`, versión **4.05**.

## Resumen (rutas y comandos exactos)

- Fuentes: `build/cfw_bypass_guardas/files/` = copia de `build/cfw_func393/pp/files/` + `lib/libmpr.so`
  (**31** ficheros: 6 `.so` + 25 `string_*.uxc`; `MANIFEST.json` 31/31 en `originales`≡`parcheados`≡`md5`,
  `nuevos` vacío, 25 idiomas; `SHA256SUMS` 31 líneas). Las **30 entradas heredadas conservan su hash**:
  `SHA256SUMS` líneas 1–30 idénticas byte a byte al del pp y 30/30 casan con el original de Sony 3.21.
- `lib/libmpr.so`: original Sony 3.21 `9a74a3bb…4c30` (md5 `d65462a3…`) → parcheado `63dfaed5…1578`
  (md5 `b9fabe9e…`), 10 321 204 B, **8 bytes** distintos (`0x437BFA..FD` y `0x437C2C..2F` = `01 20 00 bf`
  = `movs r0,#1 ; nop`, con los `cbnz` de detrás `38 b9` / `f0 b9` intactos).
- `nflasha15-405.bin`: 86 168 576 B (límite 104 857 600), sha256 `dd5a52ab…724f`, 2373 bloques TPZL,
  **328 recompuestos**, 0 violaciones LDEC, bloque 0 igual que Sony, CRC-32 `aff4ea81`.
- `firmware.tar`: 171 857 920 B, sha256 `d0cb347e…7ecf`; base `build/cfw_func393/pp/base-film.tar`
  (cuyo `nflasha15` es byte a byte el de Sony 3.21) con `--darwin-v3 --sin-wbi`, igual que el pp.
- Auditoría independiente: **`todo_ok: true`, 29/29**. `/usr` difiere de Sony en **31** ficheros =
  los 30 del pp + `lib/libmpr.so`, y **vs el `/usr` del 3.93 solo difiere `lib/libmpr.so`**.
- Versión 4.05 > instalada 3.93 (`knowledge/CURRENT.md`) y > toda build existente (máx. 4.04).

```
python3 reports/evidence/claude-sub-paquete-guardas-20261126/preparar_files.py
python3 scripts/gui/build_nflasha15.py firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 build/cfw_bypass_guardas/files build/cfw_bypass_guardas/nflasha15-405.bin
python3 scripts/gui/build_package_nflasha15.py build/cfw_bypass_guardas/nflasha15-405.bin build/cfw_bypass_guardas/pkg-4.05 --base-tar build/cfw_func393/pp/base-film.tar --version 4.05 --darwin-v3 --sin-wbi
python3 scripts/gui/audit_package_nflasha15.py build/cfw_bypass_guardas/pkg-4.05/package-4.05/firmware_packed.dat build/cfw_bypass_guardas/files --darwin-v3 --bionz-g22 --sin-wbi
python3 reports/evidence/claude-sub-paquete-guardas-20261126/verificacion_final.py
python3 reports/evidence/claude-sub-paquete-guardas-20261126/diff_pp_vs_405.py
```

## 1. Las dos guardas dentro del paquete

`libmpr.so` va a `files/lib/libmpr.so`; la raíz del ext2 de `nflasha15` es `/usr`, así que en la cámara
queda **`/usr/lib/libmpr.so`** (misma ruta que el original; en el ext2 construido: modo `0555`, uid `57285`,
gid `1000`, tamaño 10 321 204 B, los tres atributos idénticos a los del fichero de Sony). El parche es el del informe
[film-pb-1-sub-bypass-guardas-20261126](film-pb-1-sub-bypass-guardas-20261126.md); aquí no se ha vuelto a
parchear nada, solo se ha empaquetado la copia ya verificada.

Lo que hace falta para que entre (y lo que se comprobó): `build_nflasha15.py` sustituye **solo** lo que
liste `MANIFEST.json["parcheados"]` (línea 73), así que la entrada nueva era condición necesaria; y
`audit_package_nflasha15.py` calcula la lista esperada como `parcheados` cuyo hash ≠ `originales` (línea 178),
de ahí que la entrada nueva necesitase también su `originales` (sha256 del fichero de Sony) y su `md5`.

## 2. Contabilidad: `MANIFEST.json` y `SHA256SUMS`

| Comprobación | Resultado |
|---|---|
| Estilo del pp reproducido (`json.dumps(indent=1, sort_keys=True)` == fichero del pp) | idéntico antes de tocar nada |
| 30 ficheros heredados: sha256 del fichero copiado == `parcheados` | 30/30 |
| 30 ficheros heredados: sha256 del original de Sony 3.21 == `originales` | 30/30 |
| 30 `md5.original` / `md5.parcheado` contra Sony y contra el fichero | 30/30 |
| `SHA256SUMS`: líneas 1–30 == las del pp; línea nueva | `63dfaed5…1578  lib/libmpr.so` |
| `idiomas` / `nuevos` | 25 idiomas sin cambios; `nuevos` = `{}` |

Entrada añadida (clave `lib/libmpr.so`): `originales` = `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`,
`parcheados` = `63dfaed5a6ebf8e6d9a94a8bf29a5effdb98350cc680d41abf913617a92e1578`,
`md5` = `{original: d65462a32da6b8249ec7add0a99d8fe0, parcheado: b9fabe9ed1adf7bc41cb46af29ca94c2}`.
El original es el mismo objeto que lleva el ext2 de `base-film.tar` (`9a74a3bb…`), no una copia de otra versión.

## 3. nflasha15 y DAT

| | pp 3.93 (referencia) | **4.05 (este)** |
|---|---|---|
| ficheros en `files/` | 30 | **31** |
| `nflasha15` | 86 169 088 B, 326 bloques recompuestos, crc32 `7d055639` | **86 168 576 B, 328 bloques, crc32 `aff4ea81`** |
| `firmware.tar` | 171 858 432 B | **171 857 920 B** (`d0cb347e…`) |
| `package/firmware_packed.dat` | — | **172 677 272 B** (`670f7c8a…`) |
| versión de cabecera FDAT | 3.93 | **4.05** (modelo `0x41030035`, región 0) |

Línea de `part_image.sum` para la partición: `0,aff4ea81,0522d400,000001a4,00000000,000003e8,root,root,-1,-1,dev/nflasha15,`.
`firmware_packed.fdat` = `f98eb9fe…bcab`; `pkg-4.05/package-4.05/SHA256SUMS` reescrito por `package_checksums`.
`build/…/pkg-4.05/container.json` deja `tar_sha256`, `dat_sha256` y `estado: CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA`.

## 4. Auditoría (`scripts/gui/audit_package_nflasha15.py`, JSON íntegro en la evidencia)

`todo_ok: true` con **29/29** comprobaciones y 0 fallos, sin ninguna excepción: contenedor (DEND, descifrado
== `.fdat`, CRC de cabecera, modelo/región, updater oficial 3.21, versión mayor que la base 3.38), tar
(solo cambian los miembros previstos: `nflasha15`, `part_image.sum`, `darwin_core`, `darwin.sum`, `nflasha3`;
solo se quita `nflasha5`; 65/65 sumas verifican), TPZL (cabe, 512, contiguo, 2373 bloques, `max_sectores` 129
≤ Sony, bloque 0 intacto, decodificador independiente de `fwtool.lz77` de acuerdo), ext2 (solo los ficheros
del paquete, hashes, modo/uid/gid como Sony, fsck solo contadores de libres), Darwin v3 en su rango y
`nflasha3` = BIONZ del `pp` de 3.38 + parches documentados.

Ficheros distintos del `/usr` de Sony (31) = **30 del pp + `lib/libmpr.so`**, sin nada más; y el `diff -r`
del `/usr` del 4.05 contra el del **3.93 instalado** devuelve una sola línea: `lib/libmpr.so differ`
(mismo tamaño de ext2, mismo censo de ficheros). El volcado del ext2 del tar del paquete da para
`/lib/libmpr.so` el sha256 parcheado, 10 321 204 B y exactamente los 8 bytes del parche sobre el original.

## 5. Límites

- **No probado en cámara ni en emulación.** La verificación es estática (bytes, ELF, ext2, contenedor, sumas).
- El parche anula las dos llamadas de `FUN_00437BC0`; si el bloqueo real está aguas abajo (`0x447DA8` →
  `MovieReadStart 0x608698`, decodificador o visor) el síntoma cambiará de código sin haber reproducción.
  Ver riesgos en [film-pb-1-sub-bypass-guardas-20261126](film-pb-1-sub-bypass-guardas-20261126.md) §5.
- La instalada documentada es 3.93; algún informe deja abierto 4.02/4.04. 4.05 pasa el guard en cualquiera
  de los tres casos, pero **decidir la instalación es del usuario** (no se ha instalado nada).

## 6. Evidencia

`reports/evidence/claude-sub-paquete-guardas-20261126/`: `preparar_files.py` (+`.log`), `build_nflasha15.log`,
`build_package.log`, `audit.json`, `audit.err`, `verificacion_final.py` (+`.log`), `diff_pp_vs_405.py` (+`.log`),
`SHA256SUMS` (10 artefactos). Artefactos en `build/cfw_bypass_guardas/`: `files/`, `nflasha15-405.bin`
(+`.json`), `pkg-4.05/` (`firmware.tar`, `container.json`, `config-405.yaml`, `package-4.05/`).
