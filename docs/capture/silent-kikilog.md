# Silent y KikiLog: pista descartada como control de cortinas

Evidencia estática, 16-10-2026. Referencia ILCE-6300 2.01. Este resultado
resuelve una atribución de mensajes; no resuelve la viabilidad del IMX210.

## Productor y condición Silent

`43919c04` recibe una configuración cuyo `+7e4` corresponde a Silent en
captura `+804`. Llama a `43ba72ba` cuando ese valor es distinto de 2.
Existe otra llamada condicionada por clase 1, o clase 3 con `4415af79==1`,
y un indicador del primer argumento `+10`. La clase normal Silent es 0.
Los argumentos de tiempo se leen del banco seleccionado `+162/+166`.

LLVM confirma que `43ba72ba` emite códigos `0a..10` para intervalos
`1200..18ff` del primer argumento, si el segundo supera `1af7`.
Después emite `11` si el tercer argumento es cero y siempre emite `12`.
Cada emisión pasa por `4380fc78`, que reserva 20 bytes para cola `0110027c`
y escribe medias palabras `[3, código_bajo, código_alto, 22, 0]`.
**El campo `22` son flags del registro, no un comando mecánico identificado.**

## Receptor identificado con símbolos y reubicaciones

El firmware contiene `nflasha15_unpacked_unpacked/kmod/kikilog.ko`,
33 824 bytes, SHA-256
`a2ce89c05b3d4cc2b133f547e7a613419412ad163e0608c4a2634c02edac3fe0`.

En este ELF relocatable las siguientes direcciones son relativas a sección:

| Prueba | Ubicación |
|---|---|
| Descriptor de hilo, argumento cola `0110027c` | `.data+cc`, archivo `5718` |
| Instalación de `kikilog_main_thread` en descriptor `.data+c0` | `.text+c84..c98`, reubicaciones `cdc/ce0` |
| Recepción OSAL, copia de 20 bytes, liberación y `record_log` | `.text+b8..148` |
| Decodificación de categoría, identificador y flags | `record_log`, `.text+1c04` |
| Flags `22` conducen a contabilidad de eventos | `record_acm`, `.text+19e8` |

`record_acm` busca la clave categoría/identificador en `p_other_buf`,
actualiza marcas de tiempo y aumenta el contador. El campo alto de flags
es cero en este productor, por lo que utiliza el incremento unitario.
La identificación de esta ruta como registro acumulado tiene evidencia
del receptor; no depende del nombre de la función emisora.

REA/Ghidra decompiló correctamente las cuatro funciones del módulo.
Exportaciones: `analysis/ghidra/a6300-kikilog-rea.json` y
`a6300-kikilog-acm-rea.json`. Primera evidencia REA:
`ev_c12a3c652efc5e28a4e59f22cd1246039cda50914f647fa4300475d0b15ad464`.
REA mapea `.text` en `1002c`; no confundir sus direcciones con las relativas
a sección de la tabla. Las reubicaciones LLVM corroboran los nombres importados.

## Correcciones y límites

Ghidra había unido el consumidor `43919c04` a `438bc9f4` y el emisor
`4380fc78` a `43ba72ba`. `RepairA6300Sequence.java` elimina solamente esas
dos definiciones inferidas, con comprobación de hash y del solapamiento.
Se sembraron primero las entradas del callee y después las del caller,
con prólogos y retornos verificados por LLVM. No se alteraron bytes.
El export preferido es `a6300-silent-timed-command-corrected.json`;
los anteriores se conservan para auditar el error. La inferencia de tipos
del emisor todavía presenta argumentos espurios por el wrapper OSAL;
la reconstrucción numérica anterior se basa en instrucciones verificadas.
El consumidor conserva avisos PIC posteriores a las condiciones descritas.

**ACEPTO**: Silent omite este registro acumulado en la ruta normal descrita.
**RECHAZO**: interpretar esa omisión como desactivación de una cortina.
**VEREDICTO: CAMBIOS**. Continuar con las señales de exposición y lectura
del sensor y la coordinación mecánica, excluyendo esta falsa pista.
