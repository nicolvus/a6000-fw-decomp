# LUTs propios — evidencias (26-11-2026)

Material de apoyo de [G113](../../docs/gui/g113-lut-t1-curva-1d.md) y
[G114](../../docs/gui/g114-lut-propios-especificacion.md). No es fuente de
verdad: las conclusiones vigentes están en esos informes y en
[docs/PENDIENTES.md](../../docs/PENDIENTES.md) (filas `LUT-*`, `ZONA-1`).

| Fichero | Qué es |
|---|---|
| `auditoria-pipeline.md` | Auditoría read-only del pipeline de LUTs sobre HEAD `aa618415`: suite real, límites numéricos de cada pieza, verificación/refutación de las afirmaciones de G71/G90/G92/G93/G94, y los cinco riesgos para la cámara. Encontró que `ZONA_A`/`ZONA_B` son T1/BOKS (G107) → `LUT-C` reabierto. |
| `medidas-cube-usuario.md` | Calidad medida de 21 de los 75 `.cube` de `luts/` (6 de `peliculas` + 15 de `sosang/std`): ΔE2000 con y sin T, nodos recortados, clasificación y pack de 6 ranuras. |
| `medidas-cube-usuario.json` | Datos crudos de esas medidas (validación de los 75, métricas, umbrales y pack). |
| `especificacion-fabricantes.md` | Especificaciones oficiales de LUTs de usuario en Sony y otros fabricantes (rejilla, dominio, ruta, nombre, entrada log), con URL por dato. |

Reproducir: `scripts/lut/cube_spec.py` (validación) y `scripts/lut/lut_pkg.py`
(conversión). Las LUTs de `luts/` no se versionan (37 MB, material de terceros).
