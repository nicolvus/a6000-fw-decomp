# REA operativo

Continuación E018/E019: docs/capture/silent-imager-consumers.md e
docs/capture/imager-exposure-p2s.md. REA reimportó los 61 registros avcam y
validó sus IDs; el registro de copia conservado no contiene dossier de valores.
Las nuevas consultas se realizaron sobre el proyecto Ghidra persistente,
sin atribuirles IDs ni cobertura REA inexistentes. 35 exports de funciones
Ghidra verificados contra el hash original; cinco consultas finales correctas.
Autoanálisis amplio limitado a300s, parcial, con advertencias. Proyecto final:
más de37000 funciones registradas. Usar QuerySilentLiro.java; ExportSilentLiro.java
es histórico y limpia metadatos, por lo que no debe ejecutarse sobre este proyecto.

Última investigación: docs/capture/silent-shutter-status.md. Exports
silent-deep-libObj (34), silent-deep-avcam (61), silent-liro-loader (5) y
silent-ui (3), con snapshots y sesiones cerradas. REA ya fue cargado tras el
reinicio del usuario; no se requiere otro reinicio para estos resultados.

av-cam es un blob LIRO, base lógica de análisis 0x43541000, sin +0x10000 de
las importaciones ELF. El análisis automático no descubrió todos sus handlers
Thumb; no interpretar consultas vacías como ausencia. Se creó además un
proyecto Ghidra persistente en ../ghidra/silent-liro.gpr, inicialmente con ocho candidatos
y export independiente verificado contra el SHA-256 original. Su script
recrea metadatos de ese proyecto dedicado; no es una modificación del firmware.

Paquete oficial 6.5.0 local en tools/rea, lockfile conservado. Entrada reproducible: ./scripts/rea. MCP inicializado, 207 herramientas y binary_session comprobados. Doctor Codex/Ghidra saludable y análisis real libcamera.so completo. Ver reports/rea-codex-doctor.json, rea-mcp-smoke.json y rea-libcamera-analysis.json. Reiniciar Codex para cargar registro persistente. La compilación de la copia fuente no fue necesaria.
