# E26-RECOVERY R7 — investigación estática en curso

29-10-2026. Continúa [R6](e26-r6-recuperacion-bionz.md), con la instrucción vigente de trabajar exclusivamente offline. Este es un **checkpoint parcial**, no el grafo completo solicitado ni un procedimiento de recuperación. No se ejecutó firmware ni se accedió a la cámara.

## B. Escritura y borrado en Linux: evidencia nueva

**VERIFICADO EN BINARIO:** REA examinó `nand.ko` del initrd, SHA-256 `2169b84deee1a424539255affbdff499c4094e0913eeefe49339f3d47cbe6faa`, y `lld.ko`, SHA-256 `113c1b1f97ef2339b804c88d8924bc5ac7acc81f775fe4ccf27da73625e6840e`. Las direcciones son del ELF relocatable importado por REA, no direcciones de ejecución. Se conservan pseudocódigo, instrucciones y llamadas en [nand](../../analysis/e26-recovery/r7-nand-rea.json), [MuMin](../../analysis/e26-recovery/r7-mumin-rea.json) y [LLD](../../analysis/e26-recovery/r7-lld-rea.json). Una llamada o nombre no demuestra accesibilidad desde una cámara bloqueada.

| Interfaz → implementación | Operación y evidencia | Alcance |
|---|---|---|
| `muminblk_request` `0x1020c` → `mumin_ext_write_scts` `0x26e80` → `__mumin_write_ltus` `0x139fc` → `mumin_ebm_write_ltus` `0x1a638` | Escritura lógica por sectores; la primera serializa con mutex y distingue lectura/escritura. La segunda comprueba estado y límites y para un LTU parcial lee, modifica y vuelve a escribir; la capa EBM maneja información de caché y bloques, con llamadas a borrado y selección de bloques. | Requiere el controlador Linux inicializado; no se probó restauración selectiva ni atomicidad. La gestión interna puede afectar metadatos además de los sectores de datos. |
| `muminblk_ioctl` `0x104b0` → `nand_ioc_pwrite_normal` `0x284bc` → `mumin_devif_write_pages_in_pblk` | Escritura de páginas físicas normales, selector `0x6e06`. Copia la solicitud de 36 bytes, valida dos dimensiones contra geometría, prepara datos y metadatos de 8 bytes por página y llama al LLD. Devuelve error si falla. | Existencia en módulo Linux, no interfaz externa disponible antes de Linux ni escritura segura de una partición. No se ha cerrado validación de punteros o estructura completa. |
| `muminblk_ioctl` → `nand_ioc_perase_normal` `0x28298` → `mumin_devif_erase_pblk` | Borrado físico, selector `0x6e04`; error del controlador se traduce a error ioctl. | Conocer los tres campos copiados no establece mapeo físico de `nflasha3` ni seguridad de borrado. |
| `muminblk_ioctl` → `nand_ioc_lerase` `0x28624` → `mumin_ext_erase_lblk` | Borrado lógico, selector `0x6e08`, copia y devuelve estructura de 8 bytes. | Depende de MuMin y su mapeo; no equivale a borrado exclusivo de una partición. |
| `mumin_vbm_write_vpages` `0x24490` → `mumin_pbm_write_vpages` `0x21ba8` → `0x1fa44` | Escritura de páginas virtuales: VBM marca bloque usado en una rama; PBM despacha por puntero y, ante `-0x20007`, registra información de bloques y la guarda. | La tabla del puntero y la secuencia completa EBM→VBM→PBM requieren reconstrucción adicional; no se presenta como cadena completa. |

**VERIFICADO EN BINARIO:** en `lld.ko`, `mumin_devif_write_pages_in_pblk` `0x153dc` comprueba inicialización y estado del firmware, adquiere mutex y llama `0x15144`. Esta última construye una solicitud con descriptor de bloque, contador, lista de fragmentos y metadatos, convierte punteros a direcciones físicas, sincroniza caché y llama `boss_hw_arm7_comm_set_firmware_api_param(9, 0x2800, …)`, espera y recoge resultado. `mumin_devif_erase_pblk` `0x10b64` → `0x10a60` prepara tres campos de bloque y usa la misma API con primer argumento `0x0c`, seguido de espera y traducción de resultado. Los argumentos son valores observados en esos puntos; **no** se atribuye semántica global al `0x2800` ni se ha inspeccionado el firmware receptor.

Estas primitivas confirman que el sistema funcional tiene escrituras y borrados internos. **NO DEMOSTRADO:** una entrada pre-Linux, un protocolo de servicio, escritura de `nflasha3` aislada, preservación de calibraciones o una vía para invocarlas con el sistema bloqueado. `boss_hw_nandc_recovery_check` `0x17b8c` ([REA](../../analysis/e26-recovery/r7-recovery-check-rea.json)) retorna inmediatamente salvo para `-0x20001` o `-0x2713`; en esas ramas actúa sobre registros de reloj/reset y SRAM ARM7 y espera un bit del controlador NAND. **VERIFICADO EN BINARIO** como manejo interno del controlador, no como selección de UPDATER ni recuperación de arranque. La interpretación exacta de esos registros y de la transmisión del código desde cada llamador permanece abierta.

## Estado de las preguntas restantes

- **A:** el destino exacto tras fallo COLD y el grafo completo de rutas siguen pendientes. No se presupone fallback ni apagado.
- **C:** el selector UPDATER y sus dependencias están documentados en R6; productores, condiciones suficientes y una entrada independiente siguen sin cerrar.
- **D:** el tratamiento ARM7 del residuo TPZL y su relación causal con el incidente permanecen **NO DEMOSTRADOS**; el análisis de escritura anterior no resuelve la lectura LDEC.
- **E:** R6 identifica 21 páginas INFO6 sin correspondencia adquirida; este checkpoint no ha completado un nuevo inventario exhaustivo de fuentes.
- **F y comparación:** no se ha demostrado un protocolo pre-kernel ni establecido compatibilidad de una implementación de otro modelo.

Siguiente paso offline: trazar la tabla de callbacks PBM y el código de retorno que recibe `boss_hw_nandc_recovery_check`, cotejar sus instrucciones y reconstruir los retornos del cargador COLD dentro del prefijo válido. Mantener pendientes las otras preguntas hasta examinarlas; no usar UART como requisito de avance de esta investigación.
