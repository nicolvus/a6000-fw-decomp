# Validación del cambio de alcance — 15-10-2026

## Resultado

Proyecto ampliado y dos líneas de investigación documentadas. Evidencias
E001–E009, firmware, snapshots y rutas originales conservados. El obturador
electrónico continúa como subproyecto con categoría E.

| Comprobación | Resultado |
|---|---|
| TDD atlas | Fallo inicial por módulo ausente; implementación posterior correcta |
| TDD símbolos versionados | Fallo con socket@GLIBC_2.4; corregido manteniendo evidencia original |
| TDD rol ELF y agregación | Fallo antes de implementar las funciones; pruebas posteriores correctas |
| Pruebas unitarias | 15 correctas |
| ruff check src tests | Sin avisos |
| mypy --ignore-missing-imports src | Sin avisos, 2 archivos fuente |
| Integridad de los ELF | SHA-256 de cada entrada comprobado antes de analizar/reutilizar |
| Cobertura del atlas | 679/679 rutas, 641 contenidos únicos, cero errores |
| Caché esquema 2, primera pasada | 641 extracciones, 38 aciertos entre duplicados |
| Caché esquema 2, segunda pasada | 679 aciertos; sin repetir extracción de metadatos |
| Ghidra | No se volvió a ejecutar para producir el atlas |
| Cámara | Sin acceso ni modificaciones |
| Git | Sin commit: no existe repositorio utilizable y .git está protegido |

## Interpretación de hallazgos

- ACEPTO: 679 ELF ARM y 3890 dependencias declaradas. Evidencia: cabeceras y
  DT_NEEDED por archivo en elf-atlas.json, con productor identificado.
- ACEPTO: 8 dependencias tienen candidatos de contenidos distintos; se conserva
  ambigüedad y no se selecciona una copia arbitraria.
- RECHAZO: una asociación de subsistema demuestra responsabilidad o acceso
  físico. Son heurísticas con tokens conservados; 391 archivos permanecen
  sin asociación suficiente.
- RECHAZO: este inventario físico identifica los chips de la placa. Documenta
  bloques funcionales, fuentes primarias y los identificadores que faltan.

VEREDICTO: APROBADO
