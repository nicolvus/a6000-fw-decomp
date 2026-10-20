# EFCS: configuración → selector de captura → IMX210 — E020

Análisis estático de A6000 3.21. Todas las direcciones y desplazamientos
precedidos de `0x` son hexadecimales. Fuente: av-cam.bin, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Complementa [la transferencia P2S](imager-exposure-p2s.md).

**Resultado:** se cerró un recorrido estático entre el campo EFCS común y el
selector que recibe SetExposure. Tiene condiciones de selección de backend,
instantánea y modo; no acredita que todas las ramas se ejecuten en una cámara
concreta. SilentShutter +0x238 continúa sin un consumidor de captura demostrado.
No hay todavía un parche funcional de obturación completamente electrónica.

## Recorrido comprobado

| Paso | Evidencia y efecto |
| --- | --- |
| Configuración común | 0x43844e80 lee `(*contexto)+0x210`; guarda una palabra en `param6+0x41c` en bytes. El pseudocódigo tipa param6 como puntero de 16 bits: `+0x20e` equivale a +0x41c bytes. |
| Banco calculado | 0x437b5b14 pasa como param6 el contenido de GOT 0x44023eb4: 0x43eb2680. El campo está en 0x43eb2a9c. |
| Instantánea | 0x437b5b14 pasa ese mismo banco como argumento 14 de 0x4384b268. Bajo la condición de 0x4384cb38, llama 0x437b03c8(param14), que copia **0x92c bytes** a GOT 0x44021ba8 → 0x43ea976c. El campo +0x41c está incluido. |
| Selección del banco | 0x4383fc48 retorna 0x43ea976c o el banco alternativo 0x43eee9d4 según 0x43b08d42 y paridad del identificador. La copia anterior demuestra la primera rama; no demuestra por sí sola el origen de la alternativa. |
| Clase de exposición | 0x43841070 pasa el banco seleccionado como tercer argumento de 0x43842158. Esta función lee +0x41c y calcula el estado global 0x43eefb7c. |
| Estado conservado | 0x4383f5e4 obtiene ese estado mediante 0x43842404 y lo guarda en 0x43eedecc. |
| Registro del fotograma | 0x43841070 obtiene un registro mediante 0x4383fb6c y escribe la clase en byte +0x6d. |
| Copia al parámetro de exposición | 0x4383fd6c copia los 16 bytes del registro +0x64..+0x73 al destino indicado por `*param3`. La clase queda en destino +9. |
| Objeto de captura | 0x437f8a50 establece `*param3 = captura+0x64c` y llama a 0x4383fd6c si `*(GOT[0x44020e90]+0x24)==1`. La clase queda en captura +0x655. Hay otra llamada en 0x43b1d914 con el mismo destino; conserva también el selector en captura +0x4cc. |
| Programación | 0x438c828c llama a 0x437f8a50 y después SetExposure 0x436d6320 con captura +0x64c, cuando captura +0x4b9c es cero. Para clases de dispositivo 2/3 de 0x43a12c64 sobrescribe antes el selector con cero: no omitir esta condición. |
| Aplicación | SetExposure → slot +0x28 → IMX210 0x436d6f6c → registro 0x4401ca2c → lista P2S 0x43fe995c, índice 1 → transporte descrito en E019. |

La comprobación corrige el límite de E019: los bloques 0x43eb2680 y
0x43ea976c eran distintos, pero ahora se identificó una copia explícita que
transporta el campo. No se los trata como un mismo objeto.

## Selección normal y anulaciones

En 0x43842158, si `bank[+0x4bc] & 0xe0 == 0`:

- Si el campo EFCS +0x41c no vale 1, la clase resulta 3.
- Si vale 1, la clase parte de 1. Según los campos de modo +2 y +0x38c y un
  umbral de exposición, puede volver a 3.
- Si hay indicadores en la máscara 0xe0, otras condiciones seleccionan 1 o 5.

La estructura de diagnóstico GOT 0x44022728 +0x7e puede forzar clases 0–7.
Existe además una anulación por los campos +0x36/+0x37 del primer argumento.
Estos controles son evidencia de un mecanismo de diagnóstico, no una interfaz
de SilentShutter validada. La clase 5 existe en el coordinador, mientras que el
método IMX210 normal acepta 0–4: la compatibilidad exige seguir el backend y
sus condiciones; no todas las clases del coordinador son modos de este sensor.

Para las clases 1 y 3, la máscara controlada por SetExposure en el byte del
registro cambia de 0xc4 a 0xd4, respectivamente. La clase 2 produce 0x94 en esa
máscara: respecto de 3 difiere en 0x40. **No se ha probado que ese bit sea una
cortina trasera electrónica ni que forzar 2 produzca una fotografía válida.**
La existencia del enum y una escritura P2S no resuelve temporización,
sincronización mecánica ni lectura completa.

La clase 2 tiene además efectos que impiden reducirla a cambiar un bit:
0x436d6f6c escribe dos registros adicionales mediante GOT 0x4401f790 y
0x44025b0c usando los argumentos +8 y +0x14, y calcula otra temporización.

## Aplicación a la temporización DFE

0x437f8a50 llama también a 0x43ae9462 con el parámetro de exposición. Este
construye un indicador `selector==3`. El helper inicial 0x43b04658 realiza
la programación por el backend Mobius y retorna siempre 1 en el código
analizado; por ello, la rama heredada posterior condicionada a retorno cero
no es la ruta demostrada para esta llamada.

El recorrido efectivo del indicador es:

`0x43b04658 → 0x436d055c → 0x43ad78c2 → 0x43ad766e`.

El indicador ocupa el cuarto campo de 16 bits del argumento temporal;
0x43ad766e lo guarda como palabra en **base+0x0a1b80**. La base se obtiene
del objeto GOT 0x44025254 → 0x43e7efe0, campo +4. Su inicializador
0x436d06d8 llama `0x436d2004(objeto,0)`; el constructor y el setter
0x43ad6f32 establecen **0xfc000000**. Destino lógico resultante:
**0xfc0a1b80**, valor 1 para selector 3 y 0 para los demás.

Otro objeto construido con argumento 1 usa base 0xfc001000. No confundirlo
con el objeto seleccionado por los wrappers anteriores. La tabla temporal
de 41 valores se programa por `0x436d0578 → 0x43ad7944 → 0x43ad76a6`.

Esta derivación identifica escrituras del código a registros lógicos de control;
no mide señales ni identifica eléctricamente una bobina o cortina. No se llama
al campo de 0xfc0a1b80 «cortina trasera»: no se dispone de esa semántica.
Exportaciones `efcs-dfe-*.json` y `efcs-capture-packet-commit.json` conservan
los pasos, los constructores y el setter de base.

## Selector de secuencias recuperado

Las referencias PIC al texto `CaptureExposure_Selector.cpp` localizan una
función que el análisis anterior no había registrado: **0x437ea8cc**. Su prólogo
Thumb está en esa dirección, después del retorno y pool de la función previa.
Se creó únicamente esta entrada, sin reiniciar el proyecto.

Selecciona filas de 20 bytes a través de GOT 0x44025f60 usando campos de captura
+0x73a, +0x4b84, +0x4b80, +0x4ee4 y +0x4ee8. El campo +0x73a procede de
0x437f87ac → 0x43aef26a; no es una lectura del campo SilentShutter. Su nombre
de archivo no basta para identificar sus filas con métodos de cortina.

La traducción de configuración 0x438b83a0 se volvió a decompilar con constantes
PIC: el switch antes irrecuperable quedó resuelto. Usa el bloque de diagnóstico
GOT 0x4402546c +0x75 y no agrega una lectura de común +0x238.

## Bancos de exposición de la ruta sincronizada

Se localizaron sus productores: 0x437b5e70 → 0x4383bc6c/0x4383bf2c;
0x4383bf2c → 0x4383c9dc/0x4383b790/0x4383bfd4. 0x4383c9dc prepara cuatro
filas separadas por 0x10 bytes a partir de salida +0x2c. Se conservan las
exportaciones para evitar repetir el análisis. No se encontró en esas funciones
una asignación que vincule SilentShutter con el selector de esas filas.

0x436ef534, 0x436ef570 y 0x436ef600 guardan parámetros en memoria a partir de
0x43e849c0; no son por sí mismas escrituras a registros del sensor. El comando
MechaCommon construido en 0x437cf928 tampoco tiene aún un receptor de cortinas
identificado. No se utiliza como prueba de accionamiento físico.

## Evidencia y siguiente comprobación

Exportaciones conservadas en [analysis/ghidra](../../analysis/ghidra/README.md):
`efcs-frame-bank-copy.json`, `efcs-frame-snapshot-producer.json`,
`efcs-exposure-class-consumer.json`, `efcs-exposure-frame-record.json`,
`efcs-capture-param-driver-link.json`, `efcs-capture-selector-live-call.json`,
`silent-capture-config-folded.json`, `capture-exposure-selector-recovered.json`
y las consultas de referencias con los mismos prefijos. La cobertura continúa
siendo parcial; el número de funciones registradas no constituye una prueba
de ausencia de otras rutas.

Pendiente para SilentShutter: interpretar la clase 2 y la coordinación de
cortinas, identificar el consumidor de común +0x238 o demostrar el alcance de
su ausencia, y verificar el fin de integración y la lectura completa. No se
generó un parche basado únicamente en asignar ese enum.
