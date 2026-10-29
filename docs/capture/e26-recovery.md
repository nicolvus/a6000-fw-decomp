# E26-RECOVERY — incidente 3.25 (investigación abierta)

## Hechos y alcance

El usuario informa que la A6000 funcional con 3.23 recibió 3.25, el actualizador mostró 100 % y Done, y después dejó de arrancar; describe tres destellos lentos y dos rápidos. Es un testimonio, no una captura UART ni una verificación de la NAND. La prioridad pasa a ser la recuperación original preservando calibraciones. Ninguna conexión o escritura en la cámara está autorizada. El diagnóstico y los mecanismos de recuperación siguen abiertos.

## Identidad y alineación: primera comprobación offline

El SHA-256 calculado del FDAT local `analysis/e25-27/artifacts/package-3.25/firmware_packed.fdat` es `87145e1b06c01564dbebbb40d98acb084aa8ff8d044e6bf93e8cf79cae1a8d9f`, coincidente con la referencia aportada. No prueba por sí solo qué archivo transfirió el actualizador. Del tar local `firmware.integrated.tar`, los miembros `0640_darwin/darwin_core.bin` y `0700_part_image/dev/nflasha3` dan respectivamente `9771c0508ee17e7984a619479c1f69cc4e8b71f0091fb5f9dfde66bbd19fb177` y `bb9ce25a073d1ccc990d8ee1fdd75322c703d5d2a4020ab5e7daeaf8d23d546c`. Son comprobaciones independientes del manifiesto, no lectura posterior de la cámara.

El manifiesto `analysis/e25-27/artifacts/manifest.json` enumera 369 offsets: los 369 originales son múltiplos de 512; de los nuevos, 10 son múltiplos de 512 y 359 tienen residuo 256. **VERIFICADO EN MANIFIESTO**: falta contrastar directamente las tablas binarias y el lector A6000. El constructor usa `ALIGN = 256` (`scripts/e25_27/tpzl.py`). Esto es una anomalía prioritaria, no una incompatibilidad ni causalidad demostradas. Las pruebas offline de E25-27 no validaron el lector real.

## Casos externos y límites

En [Sony-PMCA-RE #488](https://github.com/ma1co/Sony-PMCA-RE/issues/488), la A6000 original presenta un patrón compatible con 73 y un registro UART con errores Mumin/ECC y montaje. El autor sospecha flash defectuosa; no constituye diagnóstico de esta cámara. Un comentario posterior describe una **ILCE-7RM2 distinta**, 3 largos + 2 cortos tras un paquete modificado y registros `LDEC` con un offset de 32; atribuye el fallo a bloques no alineados. Es un testimonio de otro modelo, no prueba del origen del LED ni del mecanismo de la A6000. La afirmación del comentario de que códigos menores de 41 nunca provienen del actualizador requiere auditoría del binario: no debe usarse para atribuir el origen de 32. No se ha identificado allí una restauración ejecutada para este incidente.

## Interfaces y siguiente evidencia

El [manual Infineon del programador universal FM3/FM4/FM0+](https://www.infineon.com/assets/row/public/documents/30/42/infineon-fm3-fm4-fm0-family-universal-programmer-user-manual-applicationnotes-en.pdf?fileId=8ac78c8c7cdc391c017d0d60c5ec70de) documenta programación familiar por SWD y UART, pero usa ejemplos de otros componentes: compatibilidad con MB9AF004B, protección y conexión en placa siguen sin verificar. El SWD del Darwin no demuestra acceso al NAND del BIONZ. E24-02 identifica señales Darwin en CN4906; no confundirlas con el Multi Terminal externo.

Para una eventual captura **pasiva**, un [análisis de un conector de A6000](https://peterwedege.blogspot.com/2016/01/analyzing-sonys-new-multiport-protocol.html) identifica M08 como UART TX y M02 como tierra según su propia numeración, que advierte invertida frente a otra fuente. El caso #488 informa TX contacto 8, tierra contacto 2 y 115200 8N1 en otro cuerpo. No se ha cotejado la numeración física y el nivel eléctrico de diagnóstico con el esquema A6000: **no hay aún guía de conexión suficientemente verificada**. Una captura futura sin transmitir requerirá breakout inequívoco, identificación de tierra y TX con esquema, receptor de alta impedancia y nivel compatible; ausencia de texto no demostraría ausencia de arranque. Esta investigación no conecta ningún equipo.

## Pendientes prioritarios

1. Reconstruir el productor y representación de `0x32` con REA y bytes, distinguiendo origen, transporte y presentación.
2. Comprobar la tabla TPZL en binarios y las precondiciones del lector real; construir solo comparación local no instalable.
3. Trazar Done, verificación de escritura, Darwin, estados persistentes y selección de `nflasha1`.
4. Verificar y analizar Loader2 del respaldo; localizar Loader3 y auditar qué copias físicas faltan.
5. Validar pinout/voltaje para captura pasiva, y estudiar SWD, serial writer y NAND preservando datos de calibración.
