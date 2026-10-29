# E26-RECOVERY — incidente 3.25 (investigación abierta)

## Hechos y alcance

El usuario informa que la A6000 funcional con 3.23 recibió 3.25, el actualizador mostró 100 % y Done, y después dejó de arrancar; describe tres destellos lentos y dos rápidos. Es un testimonio, no una captura UART ni una verificación de la NAND. La prioridad pasa a ser la recuperación original preservando calibraciones. Ninguna conexión o escritura en la cámara está autorizada. El diagnóstico y los mecanismos de recuperación siguen abiertos.

El usuario indica ahora que la cámara ya está desmontada, con una cara de SY-1028 expuesta, y prefiere no retirar la placa. No existen mediciones posteriores al bloqueo; no se autoriza intervención física en esta ejecución. La cara visible aún no está identificada con evidencia.

## Identidad y alineación: primera comprobación offline

El SHA-256 calculado del FDAT local `analysis/e25-27/artifacts/package-3.25/firmware_packed.fdat` es `87145e1b06c01564dbebbb40d98acb084aa8ff8d044e6bf93e8cf79cae1a8d9f`, coincidente con la referencia aportada. No prueba por sí solo qué archivo transfirió el actualizador. Del tar local `firmware.integrated.tar`, los miembros `0640_darwin/darwin_core.bin` y `0700_part_image/dev/nflasha3` dan respectivamente `9771c0508ee17e7984a619479c1f69cc4e8b71f0091fb5f9dfde66bbd19fb177` y `bb9ce25a073d1ccc990d8ee1fdd75322c703d5d2a4020ab5e7daeaf8d23d546c`. Son comprobaciones independientes del manifiesto, no lectura posterior de la cámara.

El manifiesto `analysis/e25-27/artifacts/manifest.json` enumera 369 offsets: los 369 originales son múltiplos de 512; de los nuevos, 10 son múltiplos de 512 y 359 tienen residuo 256. La comparación directa y el lector A6000 se examinan a continuación. El constructor usa `ALIGN = 256` (`scripts/e25_27/tpzl.py`). Esto es una anomalía prioritaria, no una incompatibilidad ni causalidad demostradas. Las pruebas offline de E25-27 no validaron el lector real.

### Fase A: lector Sony y comparación directa (29-10-2026)

**VERIFICADO EN BINARIO:** el `nand.ko` del initrd oficial 3.21, SHA-256 `2169b84deee1a424539255affbdff499c4094e0913eeefe49339f3d47cbe6faa`, contiene `muminlzp_register` en `0x12520` y `muminlzp_request` en `0x11d50` (direcciones REA/Ghidra de un ELF relocatable, no direcciones de carga en cámara). `register` lee la cabecera, valida `0x4c5a5054` (`TPZL` little-endian), usa los campos del offset y tamaño de TOC y copia la tabla a `piVar1[0x10]`. `request` selecciona una entrada de 8 bytes por índice: en `0x11e78–0x11e90` carga offset y tamaño y obtiene el residuo con dos desplazamientos equivalentes a `offset & 0x1ff`. Si no es cero, `0x11e98–0x11ec0` imprime **«Offset for lded_read should be 0»**, pero no rechaza inmediatamente la entrada. En `0x11efc` calcula el sector como base de partición más `offset >> 9`; `0x11ef0–0x11f3c` calcula `ceil((size + residuo)/512)` y llama a `mumin_map_tulist`. En `0x11f60` pasa a `mumin_devif_ldec_read` una estructura que incluye el residuo. Por tanto la referencia de Sony al cero está ligada al offset de la TOC y a la lectura LDEC, no es una constante aislada.

El importador de REA identificó el proveedor en `lld.ko` del initrd extraído de la cámara, SHA-256 `113c1b1f97ef2339b804c88d8924bc5ac7acc81f775fe4ccf27da73625e6840e`: `mumin_devif_ldec_read` `0x11048` copia los campos y los pone en cola; `0x10e0c` los entrega a `boss_hw_arm7_comm_set_firmware_api_param` con operación `0x2800`. **Límite:** no se ha trazado qué hace el firmware ARM7/hardware con ese residuo, ni demostrado que este módulo Linux se ejecute para leer el mismo `nflasha3` antes de que el propio initrd esté disponible. La advertencia no equivale a un rechazo demostrado. **Resultado: PROBABLE CON EVIDENCIA** de incumplimiento de la condición indicada por el controlador; incompatibilidad efectiva con el arranque y causa del bloqueo **INDETERMINADAS**.

La comparación directa de los dos binarios de partición, ejecutada por `scripts/e26_recovery/compare_tpzl.py`, confirma 369 entradas originales con residuo 0 y 359/369 entradas 3.25 con residuo 256. El mismo script reconstruye una tercera imagen **solo en memoria**, alineada a 512, sin FDAT ni escritura de firmware; descomprime los 369 bloques y comprueba que la tercera reproduce cada bloque descomprimido de 3.25. Los únicos bloques descomprimidos que difieren entre original y 3.25 son 0, 48 y 57. Las longitudes son 11 489 040, 11 572 480 y 11 573 248 bytes, respectivamente. El tamaño declarado del último bloque original excede el archivo en 240 bytes; el decodificador offline lo tolera y esto no demuestra cómo actúa la cámara.

| Bloque | Original offset / tamaño | 3.25 offset / tamaño | Residuo 3.25 | Alineado offset / tamaño | Sectores 3.25 / alineado |
|---:|---:|---:|---:|---:|---:|
| 0 | 3072 / 26112 | 3072 / 73984 | 0 | 3072 / 74240 | 145 / 145 |
| 1 | 29184 / 58880 | 77056 / 58880 | 256 | 77312 / 58880 | 116 / 115 |
| 48 | 2527232 / 56320 | 2575104 / 73984 | 256 | 2575360 / 74240 | 145 / 145 |
| 49 | 2583552 / 59392 | 2649088 / 59392 | 0 | 2649600 / 59392 | 116 / 116 |
| 57 | 3011072 / 56320 | 3076608 / 73984 | 0 | 3077120 / 74240 | 145 / 145 |
| 58 | 3067392 / 51712 | 3150592 / 51712 | 256 | 3151360 / 51712 | 102 / 101 |
| 368 | 11486720 / 2560 | 11569920 / 2560 | 256 | 11570688 / 2560 | 6 / 5 |

Los sectores son el cálculo de la ruta `muminlzp_request`, no una simulación del hardware. Evidencia reproducible: [JSON](../../analysis/e26-recovery/tpzl-comparison.json), `tests/test_e26_tpzl.py`; entradas locales no publicadas: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3` y `analysis/e25-27/artifacts/nflasha3.integrated.bin`. 17 pruebas de E26/E25-27 pasaron. No se construyó imagen instalable.

### Fase B: procedencia del byte 0x32 (parcial, 29-10-2026)

**VERIFICADO EN BINARIO.** Del respaldo privado `analysis/camera-dumps/nand-20261020/dev_nflasha1.bin`, FAT12 → `boot/initrd.img` CRAMFS, se extrajeron temporalmente en `/tmp` los módulos del actualizador. `usr/lib/libsenupdater.so` tiene SHA-256 `3683de6c998876e67c6e16b5137d65dd7c8fd6ba207ade4726bb950d2d1e2e1d`; `usr/bin/mf` tiene SHA-256 `85590243764cbb5de11ae576c7c7a5b96e20da787c2c860b3532148321799aeb`. `libupdaterbody.so` local tiene SHA-256 `8d1dc242decea362c65c6dcaf320046df93f06e2fc97c547b7b250b2cc3057d6`. Las direcciones son las que REA/Ghidra asigna a cada ELF y no deben tratarse como direcciones de ejecución física.

```text
script integrado: system() sale con byte 0x32 (decimal 50)
  → libupdaterbody BuildInPlugin::execute 0x248e8
  → ApiException(tipo 0x3000c, valor 0x32)
  → mf LEDErrorConverter::Convert 0xbf84: tipo 0x3000c devuelve GetErrorValue()
  → mf StartWriting 0xa038 → sendErrorMessage 0x9fcc → fifo2, un byte
  → libsenupdater receiveReturnCode 0x11a84 → setResult 0x119f8
  → cadena hexadecimal ASCII "32" → us_error.sh → common.src:blink_error
  → uc_portctl.elf -b 32 -n 0
```

`BuildInPlugin::execute` extrae `(system_status & 0xff00) >> 8` en `0x249d0–0x249d4`; un resultado no cero distinto de `0x8f` se copia como valor de `ApiException(0x3000c, valor)` en `0x24a12–0x24a32`. El convertidor devuelve ese valor para `0x3000c`; `sendErrorMessage` escribe exactamente un byte. El llamador `receiveReturnCode` lo lee de `/tmp_updater/fifo2` y lo pasa sin reinterpretarlo a `setResult`. Para valores mayores que 2, `setResult` convierte cada nibble a un dígito hexadecimal mayúsculo (`0x11a06–0x11a2c`), invoca el script y también actualiza `Status::SetResultCode`. Así, **byte 0x32 = decimal 50 → texto «32»**; el byte decimal 32 sería `0x20` y produciría texto «20». Esto demuestra una vía posible de propagación del valor desde el actualizador, no que se haya ejecutado en este incidente ni que un script concreto haya salido con 50.

Otros llamadores directos encontrados vía el thunk `0x11688` en `libsenupdater.so`: `receiveReturnCode` genera `0x44` cuando falla la lectura de un byte; `complete` genera `0x55` al agotarse 300000 ms; `write` genera `0x44`, `0x55` o `0x83` en sus errores locales; el constructor genera `0x44` si no abre un FIFO y `0x55` si falla la sincronización inicial. **Ninguna de estas constantes locales es 0x32**; la lectura del FIFO acepta un byte arbitrario. `libupdaterbody` `Plugin::Execute` (`0x2443c`) y `XmlConfigHandler::executeGuard` (`0x23584`) también crean excepciones `0x3000c` con valores retornados por módulos, pero en una rama específica valores menores de `0x41` se sustituyen por `0x59`: hay que determinar la ruta y configuración concreta antes de atribuirles `0x32`. La lista es de llamadores estáticos identificados, no una prueba exhaustiva de todas las entradas indirectas ni de persistencia.

**Pendiente:** identificar el script integrado y sus condiciones reales de salida, reconstruir cómo el estado de excepción llega al `mf` en esta configuración, auditar otros productores y comprobar si el LED posterior a reinicio usa esta ruta o alguna independiente. No hay evidencia de que el byte 0x32 del FIFO se haya observado físicamente ni de que describa NAND, Darwin o alimentación. La ausencia de una coincidencia textual con `exit 50` no descarta valores calculados.

### Fase C: cierre de actualización (parcial)

**VERIFICADO EN SCRIPTS:** `firmware/extracted/fw321/updater.img_unpacked/config/config.xml:17–18` asocia la suma de imágenes de partición con `us_crc32sum.sh`; este último usa `uc_crc32sum.elf -s -c` sobre `/` en modo imagen (`bin/us_crc32sum.sh:43–48`). No se ha verificado todavía la implementación de esa herramienta ni si lee de nuevo NAND o solo los datos extraídos. El XML asocia `darwin.sum` con comprobación CRC y después `us_darwin_firm.sh` marcado `thread="yes"` (`config.xml:35–37`). El script homónimo en el initrd del respaldo llama a `ud_darwin_firmup.elf`, comprueba su código de salida y devuelve cero si la herramienta declara éxito; eso no es evidencia de lectura posterior independiente ni de éxito en esta cámara.

`endupdate.sh:25–76` monta `nflasha2`, restaura ciertos datos, ejecuta `ud_backup_write.elf` y `ud_keep_backup.elf`, y desmonta `/setting`; después `:83` llama a `ud_lerase.elf /dev/nflasha 4`, con otras ramas según el modo, y `:97` vuelve a montar `/setting`. La condición de `$? -lt 0` tras `ud_backup_write.elf` está presente literalmente, pero no se ha establecido aquí qué implican todos sus retornos. Estas son operaciones documentadas de scripts, no un orden demostrado respecto de la interfaz del PC.

**INDETERMINADO:** aún no se ha reconstruido cuándo el programa del PC muestra `Done`, el orden real entre procesos con `thread="yes"`, la escritura y verificación de `nflasha3`, la limpieza de `uincomp` o `mode`, ni el resultado persistente de Darwin. `Done` por sí solo no demuestra que el sistema normal pueda arrancar. Siguiente dependencia exacta: estudiar `ThreadPlugin::Join`, `XmlConfigHandler::Join`, la activación de `endupdate.sh` y el mensaje de éxito hacia el host antes de fijar una línea temporal.

Seguimiento REA: `libupdaterbody.so` `ThreadPlugin::Join` `0x23d88` recorre una lista y llama `pthread_join` por cada hilo; si falla el join, según el parámetro registra o lanza excepción. `XmlConfigHandler::Join` `0x23768` invoca un método virtual en el objeto de `this+0x14`. Esto confirma una primitiva para esperar hilos, pero sin resolver el enlace del objeto y sus llamadores no prueba que la espera anteceda a `Done`. Siguiente: resolver el llamador del thunk `0x1db8c`, el método virtual concreto y el emisor de éxito al host.

**R3 — secuencia interna verificada en binario:** `UpdaterBody::Execute` `0x1f4c8` llama al thunk `0x1db8c` en `0x1f92c`, que entra en `XmlConfigHandler::Join` `0x23768`. `XmlConfigHandler::Initialize` `0x23964` construye un `ThreadPlugin` y lo guarda en `this+0x14`; su tabla virtual en `0x30fa0` contiene `0x23d88` en la ranura `+0x10`, llamada por `Join`. Por tanto la ruta normal espera los hilos registrados antes de `HasError`, `BuildInPlugin::EndUpdate` y `FlagFirmwareInformationHandler::CompleteUpdate` `0x2516c`, y después devuelve éxito desde `UpdaterBody::Execute`. Si `pthread_join` falla y se usa el parámetro falso observado en `0x1f92a`, `ThreadPlugin::Join` registra el error y continúa: no se debe convertir esa espera en garantía incondicional. `HasError` es otra llamada virtual, no se ha cerrado su manejo de excepciones de hilos.

En la rama de `CompleteUpdate` cuyo predicado virtual lo permite, el código monta `nflasha2`, revisa metadatos de versión y elimina si existen `mode1`, `mode2`, `mode3`, `mode5` y `mode6`; luego crea `CompleteFlagFile`, elimina `ModeFlagFile` y desmonta. Los nombres concretos de archivos asociados a esas clases y la semántica de `uincomp` necesitan verificación. Esta cronología termina en el retorno de la biblioteca: **la relación con el `Done` gráfico del PC sigue indeterminada**. Tampoco prueba arranque de Darwin ni descompresión de TPZL. Próximo punto de investigación: emisor de éxito desde el adaptador host y `ThreadPlugin::HasError`/captura de errores; no volver a rastrear el thunk resuelto.

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
