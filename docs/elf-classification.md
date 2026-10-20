# Atlas de ejecutables y bibliotecas — firmware 3.21

Resultado reproducible: `reports/elf-atlas.json`; herramienta: `src/atlas.py`.
Cada fila conserva ruta, SHA-256, región, cabeceras, SONAME, DT_NEEDED,
RPATH/RUNPATH, intérprete y símbolos importados/exportados. Nunca se ejecuta
el programa analizado. Los diagnósticos de readelf se conservan por contenido.

## Cobertura

| Medida | Resultado |
|---|---:|
| Rutas analizadas / candidatas | 679 / 679 |
| Contenidos únicos por SHA-256 | 641 |
| Cabeceras Machine=ARM | 679 |
| Ejecutables | 147 |
| Objetos dinámicos candidatos a biblioteca | 469 |
| Módulos con sección .modinfo | 63 |
| Errores de extracción de metadatos | 0 |
| Sin asociación funcional suficiente | 391 |

ET_DYN sin intérprete se conserva como candidato a biblioteca, no se considera
prueba absoluta de su rol de carga. Los módulos se identifican estructuralmente,
sin deducir hardware únicamente del nombre del archivo.

Regiones: nflasha15=320, nflasha16=199, nflasha3=15, nflasha7=125,
actualizador/otras=20. Los hashes duplicados no se eliminan: se conserva cada
ruta de procedencia y se comparte el resultado del análisis.

## Asociaciones iniciales

| Asociación | Rutas con evidencia de interfaz |
|---|---:|
| Android/IPC | 90 |
| Red | 72 |
| Kernel | 63 |
| Interfaz gráfica | 62 |
| Criptografía | 27 |
| Captura | 23 |
| Almacenamiento | 17 |
| Audio | 17 |
| Codecs/compresión | 12 |
| Servicio Senser | 2 |

Las categorías se solapan. Salvo la identificación de .modinfo, son
[INFERENCIA] a partir de dependencias y símbolos concretos, conservados en
`associations.evidence`. Indican uso o exposición de interfaces; no establecen
la responsabilidad completa de un binario. Una biblioteca criptográfica que
importe sockets puede tener asociación de red sin ser el controlador Wi-Fi.
Senser se distingue explícitamente de sensor CMOS.

## Reproducción y caché

```sh
python3 -m src.atlas
```

Primera pasada del esquema 2: 641 extracciones y 38 reutilizaciones entre
duplicados. Segunda pasada sin cambios: 679 aciertos de caché. Se verifican
todos los hashes antes de reutilizar datos. No se lanzó Ghidra para este atlas.
Cambiar el productor o el esquema invalida la caché; los cambios en reglas
heurísticas recalculan las asociaciones sobre los metadatos conservados.

Siguiente clasificación: priorizar los 391 desconocidos mediante importaciones,
tablas y relaciones con los puntos de entrada ya identificados, conservando
desconocido cuando la evidencia no alcance.
