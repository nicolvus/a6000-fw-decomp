# Arranque y recuperación: inventario inicial

## Evidencia existente

- [VERIFICADO] Se extraen updater.img, componentes de kernel/initrd y árboles
  de las particiones; rutas y hashes en reports/inventory.json.
- [VERIFICADO] nflasha5 es WBI1; 1164 secciones descomprimidas coinciden en
  longitud con la cabecera. No constituyen una imagen de arranque reconstruida.
- [VERIFICADO] El atlas encuentra 63 módulos con .modinfo.
- [VERIFICADO] La búsqueda inicial de scripts en el initrd de nflasha3 localiza
  sbin/init, pero no produjo una secuencia textual de montajes. No se atribuye
  un orden de arranque por los nombres de archivos.
- [VERIFICADO documental] [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE)
  explica ejecución de código personalizado en modo actualizador. No equivale
  a una recuperación independiente de firmware dañado.

## Preguntas de la siguiente fase

| Área | Evidencia que falta |
|---|---|
| Reset y bootloader | Imagen autorizada, versión, decisiones y mapa de carga |
| Arranque normal | Entrada real, kernel, init, montajes y procesos iniciales |
| Warm boot | Secuencia de restauración y validación independiente de checksums |
| Actualización | Selección del modo y dependencias del software que sigue intacto |
| Recuperación | Procedimiento demostrado, equipo requerido y condiciones de fallo |
| Persistencia | Diferenciar firmware reemplazable, calibración y datos por unidad |

Próximas acciones estáticas: caracterizar sbin/init, inventariar parámetros de
kernel y cargadores, enlazar módulos con sus consumidores. No ejecutar utilidades
llamadas format, backup_write o similares sobre una cámara. Sus nombres en el
atlas son objetos de investigación y no pasos de recuperación recomendados.

No se ha probado recuperación de un equipo averiado. Ningún trabajo actual
autoriza escritura de bootloader, NAND, calibraciones o identificadores.
