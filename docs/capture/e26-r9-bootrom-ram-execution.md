# E26-R9 — BootROM: revisión parcial de carga y ejecución en RAM

29-10-2026. Investigación **parcial, exclusivamente offline**. No se ha demostrado una cadena completa ni un procedimiento físico. Este informe corrige conclusiones de [R8](e26-r8-bootrom-uart-boss.md); no valida su parser.

## 1. Resumen ejecutivo

El receptor escribe directamente los bytes de los tipos distintos de `0` y `0xffff` en la dirección de 32 bits recibida **antes** de comprobar el CRC. El tipo `0` guarda un valor de control; el tipo `0xffff` guarda otro en `0xc000500c`. Una ruta posterior ejecuta `bx` usando ese último valor, pero su alcanzabilidad requiere condiciones adicionales. El checksum es CRC-32 reflejado, no CRC8. Se trata de evidencia estática, no de ejecución en la cámara ni de memoria libre y ejecutable demostrada.

## 2. Cambios respecto de R8

R8 atribuyó erróneamente la copia de datos al tipo 0, describió tramas de siete bytes y llamó CRC8 a una rutina de CRC-32. Su script `r8-uart-parser.py` implementa un formato hipotético y sus autotests solo comprueban consistencia interna: **no usarlo para generar ni validar tramas de cámara**. Los valores `0xff01` etc. no quedan demostrados como tipos de error de protocolo por la evidencia examinada. `0xffff0148` lee `0xc000500c`, no el contenido de `0xc0005000`.

## 3. Protocolo y fuente verificable

Fuente: `analysis/camera-dumps/20261020-174955/bootrom.bin`, 24576 bytes, SHA-256 `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026`, mapeado desde `0xffff0000`. REA/Ghidra, arquitectura ARM LE; las funciones aquí examinadas son Thumb. Las referencias son estáticas y el receptor de bits depende de temporizadores MMIO. Reproducir literal y algoritmo con `python3 analysis/e26-recovery/r9-crc32-check.py analysis/camera-dumps/20261020-174955/bootrom.bin`.

`FUN_ffff0876` llama `FUN_ffff0634` para recibir 4 bytes de longitud, 2 de tipo y 4 de valor/dirección, en memoria ARM little-endian; después, para tipos distintos de 0 y `0xffff`, recibe `longitud - 10` bytes en esa dirección. Luego recibe cuatro bytes de CRC y compara con el acumulador complementado. La longitud declarada se limita a `0x1000` (`0xffff0a42–0a52`); para los tipos de datos se exige longitud al menos 10 (`0xffff0ad2–0ae6`), por tanto hasta 4086 bytes de datos por bloque. La recepción incluye validaciones de temporización, paridad y stop; `FUN_ffff0634` escribe cada byte con `strb` tras validación del byte y antes de la validación final del CRC. El comportamiento completo de delimitación y los estados de sincronización no están reconstruidos. No existe aquí evidencia para declarar un constructor de tramas físicas listo.

## 4. Tipo 0

`0xffff0aa6–0aae` recibe cuatro bytes; tras comprobar CRC, `0xffff0bb4–0bbe` guarda el valor en el argumento de salida y pone a 1 la bandera en `0xc0010004`. **No copia el bloque de payload**: Q1 se descarta para esta atribución concreta. Puede intervenir en una validación posterior de clave, no es una dirección de destino de datos demostrada.

## 5. Tipo 0xffff y grafo de control

`0xffff0a80–0a94` recibe el valor de cuatro bytes. Tras CRC correcto, `0xffff0b78–0b82` lo escribe en `0xc000500c` y pone a 1 `0xc0010008`. El receptor no devuelve éxito por un único paquete: conserva el primer tipo y exige volver a observar ese tipo, con al menos una de las dos banderas puesta (`0xffff0b84–0ba2`). El estado inicial y las rutas de limpieza de banderas necesitan análisis adicional.

Grafo parcial verificado por REA:

```
FUN_ffff1062 -> FUN_ffff0554 -> FUN_ffff0fa0 (según condición)
                                  -> FUN_ffff0876 -> FUN_ffff0634 -> FUN_ffff0c00
                                  -> FUN_ffff0bda (bandera 0xffff)
                                  -> FUN_ffff0144: ldr r1,[literal]; ldr r0,[r1,#12]; bx r0
```

El literal `0xffff014c` contiene `0xc0005000`; por tanto `bx` consume efectivamente el valor en `0xc000500c`. Existe otra llamada directa al receptor desde `FUN_ffff1062`, con comprobación de bandera tipo 0 y comparación de clave, y ruta posterior de carga desde almacenamiento; no se puede confundir con el camino del wrapper. `bx` usa bit 0 para seleccionar Thumb/ARM; no prueba que el destino contenga código válido, que sea ejecutable, ni que corresponda a datos recibidos. El wrapper comprueba la bandera `0xffff` antes de saltar; tiene otra ruta previa dependiente de banderas. No se ha cerrado el grafo de inicialización y aceptación completo ni descartado otras verificaciones.

## 6. Mapa de memoria

| Región | Inicio | Final | Inicializada | Ejecutable | Evidencia |
|---|---|---|---|---|---|
| Datos de control BootROM | `0xc0005000` | desconocido | uso estático observado | no demostrado | literal `0xffff014c`; store en `0xffff0b7c` |
| Banderas receptor | `0xc0010004` | `0xc001000b` | uso estático observado | no demostrado | literal `0xffff0bfc`; stores `0xffff0b82/0bbe` |
| Destino elegido por emisor | desconocido | desconocido | no demostrado | no demostrado | puntero a `FUN_ffff0634` en `0xffff0ae8–0af0` |
| DDR/SRAM, pila, Loader3 y memoria compartida | desconocido | desconocido | no demostrado en esta ruta | no demostrado | faltan mapa físico e inicialización de esta ruta |

El uso de direcciones por el código no demuestra capacidad, ausencia de solapamiento ni funcionamiento real. No se ha localizado una región libre y ejecutable que pueda recomendarse.

## 7. Estado de CPU y salto

La instrucción `bx r0` está verificada; no se conocen suficientemente CPSR, interrupciones, MMU, cachés, pila, registros y semántica ante fallo. La llamada a `FUN_ffff0144` deja una dirección de retorno en LR, pero no se ha demostrado un contrato para retornar desde código arbitrario; el wrapper llama al manejador de error si retorna. No asumir coherencia de caché ni recuperación tras salto inválido.

## 8. CRC

`FUN_ffff0c00` en `0xffff0c00–0c16` efectúa ocho pasos por bit, desplazando a la derecha y aplicando el literal de `0xffff0c94`, `0xedb88320`. El acumulador se inicia en `0xffffffff` y se complementa al final. `FUN_ffff0634` lo actualiza para longitud, tipo, valor y datos, no para los cuatro bytes de CRC. Es CRC-32 reflejado (polinomio normal `0x04c11db7`, refin/refout verdaderos, xorout `0xffffffff`), no CRC8 ni simple XOR de bytes. El verificador compara cuatro vectores sintéticos contra `zlib.crc32`, incluido `123456789 = 0xcbf43926`; esto confirma el cálculo matemático modelado y el literal del binario, no sustituye una captura ni una emulación de la función original.

## 9. Pruebas y emulación

El verificador local de CRC contrasta SHA-256, literal y cuatro vectores. No se ha emulado el receptor ni el salto y no se ha construido un payload: faltan mapa de RAM, estado de CPU y modelo de entrada MMIO. Por ello no se afirma que una secuencia sintética sea aceptada por la ROM.

## 10. Activación física

`FUN_ffff1062` lee `0xf2910410` bit 22 antes de llamar a `FUN_ffff0fa0`; `0xf2915010` bit 1 se muestrea para recibir datos en `FUN_ffff0634`. Eso no demuestra que ambas señales sean equivalentes ni identifica un contacto físico. El [manual público A6000](https://device.report/manuals/sony-a6000-service-manual-repair-guide-specs) menciona `BOOT_SERIAL_IN`; no verifica continuidad, población ni niveles de CN4906. La relación con pin 9 y R4003 sigue siendo candidata documental. Cualquier medición queda fuera de R9 y necesita autorización separada; ausencia de señal no descarta el receptor.

## 11. BOSS y Darwin

No se ha demostrado disponibilidad de primitivas BOSS/NAND ni de servicios compartidos en el momento de recepción. Acceder a direcciones MMIO y tener un servicio inicializado son hechos distintos. La revisión R9 no ha reconstruido inicialización de Darwin, ARM7 ni DDR, ni permite concluir independencia de la alimentación y arranque de Darwin.

## 12. Preguntas Q1–Q10

Todas las respuestas se refieren al `bootrom.bin` y direcciones de §3–5.

1. **NO — DESCARTADO:** el tipo 0 no hace la copia; los tipos no especiales sí llaman al receptor con un destino recibido (`0xffff0ae8–0af0`), condicionado a que el bus lo acepte.
2. **NO DEMOSTRADO:** el tipo `0xffff` fija el valor consumido por `bx` (`0xffff0b7c`, `0xffff0146–0148`), pero no se ha demostrado una secuencia completa ni relación obligatoria con el bloque escrito.
3. **NO DEMOSTRADO:** se observan accesos de trabajo a `0xc000500c` y `0xc0010004`, sin demostrar región libre, ejecutable y disponible.
4. **NO DEMOSTRADO:** el CRC y las banderas son comprobaciones observadas; una ruta de `FUN_ffff1062` compara una clave. Falta cerrar todas las rutas antes de descartar firma u otras condiciones.
5. **NO DEMOSTRADO:** CRC validado matemáticamente; formato completo y sincronización aún no validados contra ejecución de la ROM.
6. **NO DEMOSTRADO:** no se ha ejecutado una emulación representativa.
7. **SÍ — VERIFICADO ESTÁTICAMENTE:** el código del receptor está en BootROM y no llama a Linux en las funciones examinadas; esto no demuestra que el resto del sistema o Darwin sean prescindibles.
8. **NO DEMOSTRADO:** condición lógica GPIO observada, sin asociación eléctrica verificable ni secuencia física confirmada.
9. **NO DEMOSTRADO:** viabilidad estática parcial (escritura y salto indirecto separados); viabilidad emulada y física no demostradas.
10. Faltan secuencia aceptada en emulación de ROM, región libre ejecutable, estado CPU y coherencia de cachés, identificación y niveles de entrada física y procedimiento pasivo revisado. Cualquier prueba física requiere autorización específica.

## 13. Experimento mínimo siguiente

Offline: ejecutar `FUN_ffff0634`/`FUN_ffff0876` en un emulador ARM con lecturas de temporizador y bit serie controladas, observar escritura y CRC frente a vectores construidos de forma independiente; registrar los estados iniciales supuestos. Después trazar la inicialización de banderas y `FUN_ffff0fa0`, y localizar RAM y cachés. Una medición pasiva futura requiere primero identificación visual y documental, instrumentos apropiados y autorización separada; no proponer tensión de entrada aún.

## 14. Recomendación R10

Cerrar primero el camino `0xffff0ae8` → buffer → bandera `0xffff` → `0xffff0148`, con emulación de ROM y límites de memoria. Las investigaciones secundarias INFO6, ARM7 y `updater/mode` no se ampliaron en esta revisión. El cierre es **parcial**, no un resultado de explotación ni una validación en hardware.
