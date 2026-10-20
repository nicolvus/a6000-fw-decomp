# Traza estática de SilentShutter — 15-10-2026

Resultado más reciente: [ruta hasta receptor LIRO, Off/On y controlador
IMX210 candidato, E015–E017](capture/silent-shutter-status.md). La incertidumbre
de etiquetas Off/On y el receptor pendientes en este registro histórico se
resolvieron. No se demostró captura electrónica completa.

Continuación: [E012 compara EFCS y SilentShutter](capture/shutter-investigation.md).
Ya se resolvió el despacho desde la secuencia SilentShutter candidata al
conversor 0x99b004 y su envío OSAL. El receptor y el control físico siguen
pendientes. El siguiente experimento descrito al final pertenece a la pasada
histórica E009; para continuar, usar los pendientes de E012.

## E007: nodo de configuración construido

- Estado: [VERIFICADO] estructura y constructor; soporte de captura [NO VERIFICADO].
- Herramienta: REA 6.5.0 / Ghidra 12.1.4, perfil automático.
- Archivo: `nflasha15_unpacked_unpacked/lib/CautionConfig.so`.
- SHA-256: `1ad489b97362dca2943bdd35b3d2bbf8ea8400164873cd65eb7afb97d62f9f39`.
- Evidencia: símbolos ELF, referencias analizadas, pseudocódigo y lectura de datos.

| Objeto | Valor símbolo ELF | Dirección en Ghidra |
|---|---|---|
| cmnViewSettingNodeRootSilentShutter | 0x1c9b2c | 0x1d9b2c |
| cmnViewSettingNodesNumOfSilentShutterDefault | 0x19fbb0 | 0x1afbb0 |
| cmnViewSettingNodesSilentShutterDefault | 0x1a6cec | 0x1b6cec |
| cmnViewSettingNodeSilentShutterOn | 0x1afc28 | 0x1bfc28 |
| cmnViewSettingNodeSilentShutterOff | 0x1b89dc | 0x1c89dc |

La función analizada en `0x148eb4` construye el nodo raíz con
`CmnViewSettingNode::CmnViewSettingNode`, la lista de nodos por defecto,
su contador y las propiedades SilentShutterRoot. Registra además su destructor
mediante `__aeabi_atexit`. No se asignó un nombre original a esa función.

El contador contiene `02 00 00 00`. La lista contiene `28 fc 1b 00 dc 89 1c 00`:
dos punteros que corresponden a los objetos On y Off en el programa cargado.
Referencias al nodo raíz: `0x14a512`, `0x14a526`, `0x1a8700`.
La referencia de `0x14a512` es de tipo PARAM según Ghidra; no es una escritura
directa a hardware. El pseudocódigo es una reconstrucción del decompilador.

Interpretación: existen estructuras de configuración inicializadas, más allá
de nombres sueltos. No prueba visibilidad del menú, habilitación por modelo,
ejecución de la acción, control del sensor ni finalización electrónica.
Siguiente experimento: resolver propiedades, condiciones de inhibición y
receptor de la orden en libObj.so.

Se recuperó también el resultado del inicializador de propiedades desde el
snapshot, aunque su entrega directa no fue utilizable por tamaño. En la función
Ghidra `0x11b5f4`, el pseudocódigo construye propiedades Root con 3 entradas y
On/Off con 4 entradas cada una; después construye ambos nodos hoja.
Evidencia `ev_49c9a2120e87947a6152e996de325ef10edba9f0ad7d1ef2f95da4aba73c2b87`
en `analysis/rea/CautionConfig.snapshot.json` (1858371 caracteres de pseudocódigo).
Constructor raíz: evidencia
`ev_12763268e1124c36a71271a073fb9fafb52c290aaffb8953a11aa112aa579caf`.
No se han asignado significados a los identificadores numéricos de las propiedades.

## E008: libsencore no demuestra un controlador de sensor fotográfico

- Estado: [VERIFICADO] cadenas y funciones; interpretación funcional limitada.
- Archivo: `nflasha15_unpacked_unpacked/lib/libsencore.so`.
- SHA-256: `f1789e4e4b202dd4e6a5591e7b53cec1609cac32aa083d35974e6d0ed20b279d`.
- Evidencia conservada: `analysis/rea/libsencore-evidence.json`.

Ghidra define dos cadenas S_IMAGER_CURTAINMODE en `0x34050` y `0x47b6c`.
La consulta de xrefs a ambas devuelve cero referencias. Es un resultado del
análisis, no prueba de ausencia de consumidores o de acceso indirecto.

Hay funciones `SenserIfStart`, `SenserIfStop`, `senser_usb_mode_start` y
`SubsystemCommunicationCommand::lsi_send` (Ghidra `0x243b0`). La última
comprueba estado y delega a otra rutina; no se identificó una escritura a un
registro del sensor. El nombre Senser y la cadena IMAGER no bastan para
clasificar esta biblioteca como controlador del CMOS: hay interfaz de servicio.
Siguiente experimento: seguir referencias desde código de captura, evitando
confundir modo de servicio con sensor de imagen.

## Coordenadas y límites del análisis

En estas importaciones Ghidra utiliza una base adicional de `0x10000` respecto
a los valores ELF. Los offsets del archivo, las VA relativas del ELF y las
direcciones de Ghidra deben registrarse por separado. No son direcciones
medidas en una cámara. Las primeras consultas a offsets de cadena no son
consultas a los objetos exportados del mismo nombre; se corrigieron usando
la tabla de símbolos y las direcciones del programa cargado.

La primera pasada de libObj.so con perfil predeterminado no terminó dentro
del plazo: cliente MCP 300 s, arranque del proveedor 330000 ms. Hubo advertencias
de relocaciones externas y decompilación. No se obtuvieron xrefs válidas de
esa pasada. El reintento usa una sesión independiente, plazo 900000 ms,
`ARM:LE:32:v7` (ELF declara ARMv7-A y Thumb-2) y desactiva
`Decompiler Switch Analysis,Stack`. Ese perfil reduce cobertura automática;
sus resultados no deben confundirse con el análisis predeterminado.

## E009: rama de conversión de mensajes SilentShutter

- Fecha: 15-10-2026.
- Estado: [VERIFICADO] referencia e instrucciones; [INFERENCIA] delimitación y
  papel de la rutina; soporte en hardware [NO VERIFICADO].
- Hipótesis examinada: el texto NON SUPPORTED demostraría ausencia de soporte
  del obturador silencioso. **RECHAZO de esa interpretación**: la rama comprueba
  identificadores de mensaje, no una capacidad del sensor.
- Archivo: `nflasha15_unpacked_unpacked/lib/libObj.so`.
- SHA-256: `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.
- Herramientas: REA/Ghidra con perfil reducido descrito arriba y desensamblado
  independiente LLVM en Thumb-2. No se ejecutó el código ARM.
- Evidencia REA: `ev_424ae6aa596340bac01170f2321104b2246f24e75e77eb711071b3a5c46261fb`
  en `analysis/rea/libObj-selective-evidence.json`.

REA encuentra una referencia a la cadena de error en Ghidra `0x9ab038`,
equivalente a VA ELF/offset `0x99b038` en este segmento. La relación se comprueba
con la carga del literal en `0x99b0e4` y su suma al PC `0x99b03c`, que produce
`0xe072e8`, inicio de la cadena SetSilentShutterModeForLiro NON SUPPORTED.

El prólogo Thumb en VA ELF `0x99b004` delimita una rutina candidata; su nombre
provisional es `candidate_silent_shutter_message_converter`. No se confunde con
el símbolo anterior que imprime LLVM por proximidad. Las tablas de unwind
agrupan aquí un intervalo más amplio y no fijan por sí solas esta entrada.

| Instrucciones observadas, VA ELF | Comportamiento |
|---|---|
| 0x99b012–0x99b02a | GetMessageId; acepta 0x768e o 0x75e6 |
| 0x99b02c–0x99b04e | Para otros identificadores, prepara el diagnóstico NON SUPPORTED |
| 0x99b0bc–0x99b0de | GetParam(0x9983); comprueba puntero no nulo |
| 0x99b050–0x99b070 | Acepta valores 0x450 y 0x451; escribe respectivamente 0 y 1 en buffer+8 |
| 0x99b0ac–0x99b0d2 | Escribe 5 en buffer+0, 0xe3 en +2, 0x40 en +3 y bytes del tercer argumento en +4..+7 |
| 0x99b072–0x99b0aa | Valores no aceptados o parámetro nulo conducen a error y retorno 4 |

No se atribuye a `0x40e3` la identidad de un comando de sensor: solo se han
observado dos bytes escritos en un buffer. Tampoco se identificó un envío USB,
una escritura de registro, temporización de exposición ni una condición por
modelo en este fragmento. La asociación 0x450=Off y 0x451=On es por ahora una
hipótesis: dos cadenas contiguas de una tabla no bastan para demostrar sus índices.

SHA-256 de bytes originales en `[0x99b004,0x99b0fc)`:
`b81d0dd02718e38bed8310ead5a0f75bee2299071036d7ebc76e66791953963c`.
Reproducción del desensamblado:

```sh
llvm-objdump -d --triple=thumbv7-linux-gnueabi --start-address=0x99b004 --stop-address=0x99b0e2 firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so
```

Próximo experimento: obtener la función y sus llamadores en una sesión REA
persistente, rastrear el consumidor del buffer y resolver el receptor de esa
operación. La existencia del conversor no prueba que un recorrido de captura de
A6000 llegue a él ni que el sensor implemente el comportamiento solicitado.

## Cierre de esta pasada

Sesiones cerradas y snapshots conservados. Integridad de los tres ELF comprobada
contra el inventario: sin cambios. Cinco pruebas unitarias correctas; ruff y mypy
sin avisos. No se modificó código propio ni se desarrollaron parches. Trabajo
sin commit por ausencia de repositorio Git utilizable y .git de solo lectura.
