# Evidencia — paquete CFW **3.97** con el `libmpr.so` del parche C (FBM sector `0x31`) y rollback **3.98**

26-11-2026. Todo **offline**: no se ha instalado nada, no se ha tocado la cámara ni `firmware/`, no se ha usado `mcp_rea`.
Binario entregado: `build/cfw_fbm_sector31_c/libmpr.so` (sha256 `831142ae…e378e`), copiado a
`build/cfw_fbm31_pkg397/libmpr.so` y comprobado igual (`sha256.txt`).

| Fichero | Qué es |
|---|---|
| `sha256.txt` | sha256 de todo lo que interviene y de lo entregado (base, binario, `.dat`/`.fdat`/tar de 3.97 y 3.98, rollback 3.96) |
| `auditoria-397.json` / `.err` | salida íntegra de `audit_package_nflasha15.py` para la 3.97 con `--base-dat` = `.dat` de la 3.94 → **`todo_ok: true`, 22/22** |
| `auditoria-398-rollback.json` / `.err` | auditoría del rollback 3.98 con `--base-dat` = `.dat` de la 3.97 → **`todo_ok: true`, 22/22** |
| `libmpr-diff.json` | diff byte a byte fábrica `9a74a3bb…` → parche C `831142ae…`: 81 B distintos en 2 zonas (`0x7126E6..E9` y `0x93B000..B051`) |
| `desasm-cueva-397.txt` | desensamblado (capstone) de la cueva **del binario empaquetado**: guarda `[r4+4]`, alta del stub en `(4,3)` y `(0x21,3)`, `InitBackupData(6,3)` |
| `nflasha15-397.json` | hashes y diffs de la imagen nueva: 86 169 600 B, crc32 `3f18fd9f`, 2 373 bloques, bloque 0 = Sony, difiere de la 3.94 solo en `lib/libmpr.so` |
| `container-397.json`, `container-398-rollback.json` | resumen de los dos empaquetados (base tar, línea de `part_image.sum`, sha del `.dat`) |
| `build-nflasha15-397.txt` | informe de `build_nflasha15.py` (329 bloques recompuestos, 31 ficheros, bloque 0 de Sony) |
| `build-package-397.txt`, `build-package-398-rollback.txt` | salidas de `build_package_nflasha15.py` |
| `diff-396-398.txt` | el rollback 3.96 y el 3.98 son el mismo contenido: 36 B de diferencia en la cabecera (versión + suma) |
| `versiones.txt` | versión/modelo/región y CRC de cabecera de los `.fdat` 3.94–3.98 (3.97 > 3.96, así que la 3.97 es instalable sobre el rollback 3.96) |
| `comandos.sh` | reproducción completa, de cero |
| `MANIFEST-397.json`, `MANIFEST-398-rollback.json` | manifiestos usados por `build_nflasha15.py`/auditor como «verdad» de hashes (31 ficheros / 30 sin `libmpr`) |
| `extrae.py`, `prepara_pkg.py`, `diff_libmpr.py`, `verifica_n15.py`, `desasm_cueva.py`, `diff_396_398.py` | scripts usados (rutas relativas a la raíz del repo) |

Hechos medidos que sostienen el paquete:

1. `/lib/libmpr.so` de la base 3.94 = `/lib/libmpr.so` de fábrica 3.21 = `9a74a3bb…4c30`
   (`work/xs`, `work/xn`): la sustitución es sobre el binario original.
2. El binario empaquetado es el del parche C, y su cueva se desensambla al diseño documentado.
3. `/usr` de la 3.97 = `/usr` de la 3.94 salvo `lib/libmpr.so`; frente a fábrica, los mismos 31 ficheros de siempre.
4. `firmware.tar` del rollback 3.98 es **byte a byte el de la base 3.94** (`92dfeb6a…`), igual que el del 3.96.
