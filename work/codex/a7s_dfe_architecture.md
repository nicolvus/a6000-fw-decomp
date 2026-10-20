# DFE A7S 3.20 frente a A6000 3.21

## Resultado

**VERIFICADO:** A7S 3.20 no trae `dfe.bin` ni otro blob con los vectores de la DFE A6000; sí contiene en `av-cam.bin` la pila host DFE, receptor y controlador `IMX235`. Esto no permite decidir si el ejecutable de la DFE reside en ROM, en almacenamiento no incluido o si A7S emplea otra disposición: **NO VERIFICADO**.

| Hallazgo | Evidencia | Clasificación |
|---|---|---|
| A6000 tiene una imagen DFE separada | `.../dfe/dfe.bin`, SHA-256 `fc4e314db24a72d584bd8795bd8f1144b003c97c390cb143d09b840b38bf9fcd`, 65 536 B. Offset 0: ocho instrucciones `ldr pc,[pc,#0x18]`; literales offset `0x20`: `0x01005870,34,38,4c,50`. | VERIFICADO |
| Base práctica de la imagen A6000 | Cargar raw ARM little-endian en `0x01000000`: REA observa segmento `0x01000000..0x01010000`, entry `0x01000000`. Es una base de análisis coherente con los vectores, no prueba su dirección de ejecución física. | INFERENCIA |
| Inicialización DFE | Tras la tabla de vectores, offset `0x3c` inicia copia/borrado de memoria (`ldmia r0,{r10,r11}`, stores), antes de los cuerpos recuperados. Los destinos exactos requieren mapa SoC. | VERIFICADO (instrucciones), NO VERIFICADO (semántica) |
| Cargador A6000 | La cadena `/usr/dfe/dfe.bin` está en `av-cam.bin` A6000, offset `0x790b98` / dirección lógica `0x43cd1b98`. Su presencia prueba referencia de ruta, no qué proceso abre/carga el archivo: no se recuperó xref debido al límite temporal de REA. | VERIFICADO / NO VERIFICADO |
| A7S contiene host DFE | En A7S, `av-cam.bin` contiene `DFE DDR Initialize`, `DFE_INT(HDMAC0..3)`, tipos `Camera::DFECore::*`, `GCS2RxLink`, `MPHYRx4ch`, `SubLVDS` y `C_ImagerCtrl_IMX235`. | VERIFICADO |

## Comunicación

El manual Level 3 sitúa CXD90027GF entre el sensor y la cámara y enumera 12 pares SLRX y 12 SLTX, a 54 MHz, en ambos modelos. `GCS2RxLink`/`MPHYRx4ch`/`SubLVDS` son nombres de receptor y lanes en el host. Esto apoya una ruta de **datos** sub-LVDS hacia el CXD; no identifica el protocolo del bus de configuración de registros del sensor. Las tablas de pares `(ID u16, dato byte)` y `SetMode`/`SetExposure`/`SetRead` son configuración, no muestras sub-LVDS: **INFERENCIA**.

No hay evidencia estática de reset global, terminación electrónica de integración por filas ni lectura sin cortina. Por tanto, la hipótesis de exposición completamente electrónica en A7S queda **NO VERIFICADA**.

## Reproducción

```bash
sha256sum firmware/extracted/{a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin,fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/dfe/dfe.bin}
xxd -g4 -l128 firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/dfe/dfe.bin
strings -a -td firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin | rg 'IMX235|GCS2RxLink|MPHYRx4ch|SubLVDS|DFE_INT'
```

REA se intentó sobre A7S raw ARM base `0x43541000`; agotó el límite MCP de 330 s durante autoanálisis. Ese timeout no se usa como evidencia de ausencia.
