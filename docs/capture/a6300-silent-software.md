# Ajuste Silent y respuestas de software en A6300 2.01

Investigación estática en curso. Fuente `libObj.so`, SHA-256
`c70b635bcbd386b4b34b6a5c37ef941a1463253aebb43d83fada7fe4e9fe9073`.
Las direcciones de este documento son virtuales ELF; sumar `0x10000` para
el proyecto Ghidra `a6300-libObj.gpr`. No mezclar con direcciones LIRO.

## Ajuste y traducción

`66e27c`, `pvt_ActionSetSilentShutterMode`, obtiene el parámetro de modelo
`0x291` y llama a `66aedc`, `pvt_SetSilentShutterMode`.
El conversor `68efc8` acepta modelo 1/2 → valor `0x450`/`0x451`;
otros valores fallan. El setter forma categoría `0x3100`, mensaje `0x768e`
y parámetro `0x9983`. `68808c`, inicialización del mismo ajuste, aplica
la misma conversión; no son configuraciones físicas independientes.

`96034c` traduce `0x768e` o `0x75e6`, requiere `0x9983`, y forma un paquete
de nueve bytes: `05 00 e3 40 rr rr rr rr mm`, con `mm=0/1` para `450/451`.
Los cuatro bytes `rr` proceden del tercer argumento. El valor del segundo
byte lo establece a cero el llamador `adbf58`: limpia nueve bytes mediante
`memset@plt`, ELF `ef5c8`, confirmado por su reubicación dinámica.
El mismo protocolo está documentado para A6000. Su recepción LIRO A6300
es `437ef610`, que actualiza el estado común `+264`.

**RECHAZO**: usar el diagnóstico `SetSilentShutterModeForLiro NON SUPPORTED`
como prueba de incompatibilidad del sensor. En esta función A6300 también
existe y se alcanza al recibir un identificador de mensaje incorrecto.
Otros diagnósticos cubren parámetro ausente o valor de modelo no reconocido.

## Respuesta del ajuste

`680b14`, `pvt_subActionObjectSilentShutterModeCmpEvt`, obtiene parámetros
`9984` y `9985`, convierte sus valores y actualiza dos campos del objeto
en `param_1+560`. Después comunica categoría `3100`, mensaje `768f` con esos
dos valores. Todavía no se ha demostrado que esta respuesta incluya un
fotograma, lectura del sensor o confirmación mecánica.

## Método y límites

REA abrió el ELF y confirmó su identidad. La primera consulta de cadenas
agotó 300 segundos sin devolver evidencia; no se repitió el análisis global.
El proyecto nativo Ghidra se importó sin autoanálisis amplio y conserva las
consultas dirigidas. Exports `a6300-silent-library-entrypoints.json` y
`a6300-silent-library-conversion.json`.

La tabla `.ARM.exidx` tiene 57390 registros, ordenados, pero puede agrupar
funciones adyacentes. Ejemplo comprobado: `960294` traduce `40e4`, mientras
que el conversor Silent empieza en `96034c`, dentro del mismo intervalo.
Su prólogo, comparaciones de mensaje y referencia al diagnóstico se
comprobaron con LLVM. No usar el registro de unwind como prueba automática
de que toda instrucción del intervalo pertenece a una sola función.

El RTTI `CamUser::SequenceSetSilentShutterMode` está en `100c488`, con
vtable en `100c478`. Sus métodos `adbf10/adbf18` retornan cero y
`adbf20/adbf44` son destructores; **no se han etiquetado como ejecutor**.
El diagnóstico específico de envío tiene una referencia en `adbfc0`, dentro
de la función que empieza en `adbf58`, identificada después como ejecutor.

`adbf58` es el ejecutor de envío: limpia el paquete, llama al conversor
genérico `97cca4` con comando `40e3` y envía nueve bytes por `941860`.
Si falla el envío comunica error `f001` y retorna `ffff`.
Si el envío retorna éxito, actualiza estado, construye una respuesta con
parámetro `9502=f000` y comunica otra notificación `85f6`.
La respuesta se construye en esta misma función después del envío;
no aparece una espera de fin de exposición o de disponibilidad de imagen.
No debe confundirse con una confirmación de captura física.

`941860` llama a `osal_snd_msg@plt` (ELF `f3f68`) y traduce su estado con
`94180c`. El epílogo conserva R0 tras esa llamada (`9418c2..9418cc`), por lo
que se anotó el retorno como entero en el proyecto; las primeras consultas
lo inferían como void. El traductor convierte varios errores conocidos y
retorna 0 para estado 0; su rama de error no reconocido registra diagnóstico
y también retorna 0. Por tanto, ni siquiera todo retorno 0 constituye una
prueba inequívoca de entrega. Es una limitación del código observado.

`97cca4`, caso `40e3` (índice `e3` del switch), selecciona puntero Thumb
`96034d`; se ha unido el ejecutor al conversor Silent concreto.

Export: `a6300-silent-library-sequence-execute.json`. Los métodos virtuales
que retornan cero no son el ejecutor de envío; identificar el RTTI no basta
para asignar semántica a todos los slots de la vtable.

**ACEPTO**: ajuste 1/2 → protocolo 0/1 y comando `40e3`, comparable a A6000.
**RECHAZO**: respuesta de ajuste = prueba de fotografía silenciosa.
**VEREDICTO: CAMBIOS**. El ejecutor y la respuesta de ajuste están unidos;
faltan una prueba de captura física y la capacidad necesaria del IMX210.
