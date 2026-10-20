# Arquitectura observada

Alcance ampliado: [proyecto general](project-scope.md),
[inventario físico](hardware-inventory.md), [atlas ELF](elf-classification.md)
y [dependencias](subsystem-dependencies.md). Los hallazgos siguientes se conservan.

[VERIFICADO] El atlas analiza 679 cabeceras ARM y 3890 DT_NEEDED; diferencia
referencias libc.so de libc.so.6. [INFERENCIA] representan entornos ABI distintos;
hay que resolver cargadores e IPC antes de intercambiar o comparar bibliotecas.
No se ha reconstruido aún el flujo completo entre ambas capas.

[VERIFICADO] Firmware FDAT 3.21, modelo numérico `0x41030035`, región 0; descifrador `CXD90014` en `config.yaml`. Esto no demuestra fabricante Qualcomm del procesador: esa atribución del repositorio base queda [NO VERIFICADO]. Descifrado y firma criptográfica son propiedades distintas.

[VERIFICADO] `nflasha16` contiene Android 2.3.7, SDK 10, `armeabi-v7a`, plataforma `diadem`, según `build.prop` (SHA-256 7b05c73ffccf864d1f30d51cfae6cce5951c75e72508f0af3b3fc9b6a848a872). Los ELF inventariados declaran ARM.

[VERIFICADO] `nflasha15` contiene bibliotecas y escenarios nativos; `nflasha16`, librerías Android y framework. Cuatro particiones empiezan con TPZL; nflasha5 empieza con WBI1. `fwtool/archive/lzpt.py` identifica TPZL como compresión LZPT; no demuestra por sí sola un sistema de archivos Android.

[INFERENCIA] La interfaz Android delega captura hacia ScalarDaemon y las capas nativas. Hay aristas verificadas dentro de funciones; la conexión completa entre mensajes, receptor y sensor sigue pendiente. No se ha reconstruido el flujo físico del botón ni el final RAW/JPEG.
