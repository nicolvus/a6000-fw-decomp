# 15. Recuperación por SWD (EXPERIMENTAL): cómo recuperé una Sony A6000 bloqueada con una RP2040

**Resumen:** mi A6000 quedó bloqueada (LED de error, sin USB) tras instalar un firmware modificado mío. La recuperé conectando una RP2040 por SWD a dos pads de la placa y forzando un solo registro durante el arranque, lo que hizo que la cámara cargara el actualizador de fábrica de Sony. Después instalé el firmware oficial por USB.

**Antes de empezar:** esta página es muy técnica y específica. Si no entiendes todo, no te preocupes; hay muchas cosas que yo tampoco entiendo del todo. Espero que sirva para entender cómo funciona el sistema de actualización de esta cámara. No es una guía para seguir a ciegas: soldar en la placa puede dañarla, y esto funcionó en una sola cámara.

## Cómo está organizado el firmware

La A6000 guarda su firmware en una memoria NAND de unos 473 MiB, dividida en particiones que Linux ve como `/dev/nflasha1`, `nflasha2`, `nflasha3`, etc. Conozco estas particiones por un volcado completo que hice el 20 de octubre de 2026, con la cámara en el firmware 3.21.

Ese volcado salió del propio modo actualizador de Sony. Con la cámara en ese modo, un script mío leía cada `/dev/nflasha*` por USB, con el mismo protocolo que usa pmca (la herramienta libre para hablar con las cámaras Sony por USB). Fue solo lectura. En total son unos 916 MB. También volqué el BootROM (24 KB) y los cargadores de arranque (`bootloader.bin`, que contiene Loader2 y Loader3). La copia no sirvió para restaurar nada, pero sí para analizar todo offline.

Las tres particiones que importan:

- `nflasha1` es el actualizador de fábrica: una pequeña partición FAT12 con un kernel Linux, un initrd y los programas que instalan firmware por USB. Los paquetes 3.2x no incluyen imagen del actualizador, así que ninguna actualización la reescribe.
- `nflasha2` guarda ajustes y estado: la versión instalada (`\updater\dat4`) y las banderas del actualizador, incluido el fichero `\updater\mode`.
- `nflasha3` contiene el firmware principal (`av-cam.bin` y otros ficheros).

## El bloqueo

Unos días después instalé en mi A6000 un firmware modificado que había creado por ingeniería inversa: el 3.25. El actualizador llegó al 100 % y mostró `Done`. Al reiniciar, la cámara quedó muerta. No daba USB y no entraba en modo recuperación. La única señal de vida era el LED con tres parpadeos largos y dos cortos.

Con la cámara inaccesible, analicé de forma estática los bootloaders de Sony (Loader2 y Loader3) con REA, una herramienta de ingeniería inversa, con ayuda de Claude. El patrón de LED correspondía al código de error −302 de Loader3. Mi hipótesis era que la causa estaba en `nflasha3`, que yo había recomprimido con un formato que el descompresor por hardware no sabe leer (esto era una inferencia por análisis, no una medición; más abajo explico qué pude confirmar y qué no). Mi firmware había pasado todas las comprobaciones en el PC y aun así bloqueó la cámara.

Había una buena noticia: el actualizador de fábrica (`nflasha1`) no había sido tocado. El problema era que Loader3 nunca llegaba a arrancarlo.

Desde el volcado abrí `nflasha1`, extraje su initrd (un CRAMFS) y desensamblé sus programas. Su script `UdtrMain.sh` busca ficheros llamados `mode1`, `mode2`, `mode3` o `mode6`. Si no encuentra ninguno, arranca por defecto en modo usuario y espera firmware por USB. O sea, el actualizador no necesita ninguna bandera para funcionar. Solo necesitaba que Loader3 lo arrancase.

## Por qué SWD

Necesitaba una forma de entrar a la cámara, y las vías habituales estaban cerradas:

- Por USB era imposible, porque Loader3 nunca llega a exponerlo.
- Escribir la NAND desde fuera no era una opción: no había identificado el chip y en ese momento no tenía la clave del BootROM.
- El JTAG convencional estaba descartado: según el esquema, TDI, TCK y TMS van atados a 3,15 V.

Quedaba SWD, la versión de dos hilos de la interfaz de depuración. En el manual de servicio, SWCLK (Serial Wire Clock) sale de la bola W25 del procesador BIONZ (IC6000) y SWDIO (Serial Wire Data I/O) de la W26. Ambas señales van hacia el conector CN4906 a través de dos resistencias, R4911 y R4912. En mi cámara, esas resistencias y el conector no están montados: solo están las huellas. No había dónde enchufar nada, así que tuve que soldar directamente a los pads. Había además una incógnita: un eFuse podía tener la depuración deshabilitada, y no había forma de saberlo sin probar.

[Insertar el recorte del esquema, con las dos resistencias sin montar resaltadas, y fotos de ambas caras de la placa SY-1028 con IC6000, R4911, R4912 y CN4906 señalados. Citar la fuente del recorte.]

## El montaje

Antes de conectar nada medí con el multímetro. Con la cámara apagada comprobé que no hubiera cortos entre los pads y masa ni con las alimentaciones. No comprobé la continuidad entre cada pad y el BIONZ; me fié del esquema del manual de servicio. Con la cámara encendida y sin sonda medí 3,09 V en ambos pads, compatible con una sonda de 3,3 V. Si hubiera medido 1,8 V no la habría conectado.

Soldé un cable AWG30 al pad inferior de R4911 (SWCLK, lado BIONZ), otro al pad inferior de R4912 (SWDIO, también lado BIONZ) y un tercero a masa. Los fijé con máscara de soldadura curable con UV y cinta Kapton.

[Insertar una foto macro de la soldadura, con una flecha en cada pad.]

Como sonda usé una RP2040 Zero con el firmware `debugprobe-zero` v2.3.0 (https://github.com/inindev/debugprobe-zero), que la convierte en un adaptador CMSIS-DAP. SWCLK va al GPIO 10, SWDIO al GPIO 11 y la masa a GND. En el PC usé OpenOCD, con ayuda de Claude.

[Insertar una foto o esquema de la sonda con su cableado.]

## Primer contacto

Con los hilos soldados, lo primero fue comprobar si el procesador respondía. Lancé OpenOCD con el driver `cmsis-dap` y el transporte SWD a 100 kHz, por precaución. El DPIDR fue `0x3ba02477`, un valor válido.

Eso resolvió una de las mayores dudas: la lectura por SWD no estaba bloqueada por ningún mecanismo de protección que impidiera acceder al DAP. La escritura no la probé en ese momento. Subí a 1 MHz y comprobé que 256 palabras de prueba coincidían con las leídas a 100 kHz; los volcados grandes los hice a esa velocidad.

Al explorar el DAP (el bloque de acceso a depuración del chip) encontré tres puertos de acceso. Por sus identificadores, deduje que uno es de memoria física, otro de depuración y el tercero JTAG. Por el de depuración llegué a una tabla ROM con cuatro núcleos Cortex-A5. Trabajé solo con el primero.

Con el puerto de memoria leí los vectores de arranque y volqué la RAM: un megabyte primero y luego otros dos. Hice cada volcado dos veces y salieron idénticos byte a byte. En la RAM encontré el Loader3 en ejecución, idéntico al original de Sony. También encontré el log interno del cargador y la tabla de ficheros que intentaba cargar.

Después paré la CPU y vi dónde estaba: en el bucle del LED, con los registros mostrando el código de error −302. Con puntos de parada encadenados desde la entrada de Loader3 (la técnica la explico enseguida) medí que el error ocurría al cargar `\sabin\idt_cam.bin`, que está en la partición 3. Eso coincide con mi diagnóstico teórico, que apuntaba a `nflasha3`. Lo que esta medición no puede demostrar es el motivo exacto: el formato de compresión sigue siendo una inferencia.

## Cómo parar un arranque que dura segundos

El arranque de la cámara pasa por tres etapas seguidas: BootROM, Loader2 y Loader3. Todo ocurre en pocos segundos (Loader3, en menos de uno), así que no da tiempo a conectar e inspeccionar. Hay que parar la CPU casi en cuanto arranca y dejar preparados los puntos de parada en los sitios que se quieren mirar.

Mi primer intento fue poner puntos de parada en Loader2 para que saltaran más adelante, en Loader3. No funcionó: no sobrevivían hasta esa etapa. Comprobé que un punto de parada en la rutina del LED, que se ejecuta en todo arranque fallido, nunca saltó. No sé por qué se pierden. Solo sé que se pierden.

Lo que funcionó fue ir por etapas. En cuanto el enlace SWD responde, paro la CPU y pongo un único punto de parada en la entrada de Loader3. Cuando salta, quito ese punto, pongo el siguiente de la cadena y continúo, hasta llegar al punto que quiero inspeccionar.

Hay un detalle importante en cada parada. Antes de reanudar, quito los puntos de parada actuales, avanzo una instrucción y entonces coloco los siguientes. Si no avanzo esa instrucción, la CPU sigue parada justo sobre el punto que acabo de colocar y, al reanudar, vuelve a saltar inmediatamente, una y otra vez.

La segunda trampa son los registros. El procesador tiene copias separadas de `sp` (puntero de pila) y `lr` (registro de enlace, o dirección de retorno) para cada modo de funcionamiento. Loader3 corre en modo Supervisor. En este núcleo, los nombres genéricos `sp` y `lr` de OpenOCD no se refieren a esas copias y devuelven 0 aunque la CPU esté perfectamente. Yo vi `lr = 0` y pensé que la ejecución había saltado a una dirección nula, lo que habría sido un fallo grave. Al pedir los registros del modo, `sp_svc` y `lr_svc`, la pila y el retorno estaban sanos. Si lees registros por SWD en este chip, usa siempre los del modo actual.

## La idea: no escribir nada, solo cambiar un registro

Con las paradas encadenadas funcionando, podía inspeccionar el arranque desde dentro. Mi primera idea fue usarlas para escribir en la NAND, por ejemplo creando el fichero `\updater\mode` en `nflasha2`. Miré cómo lo gestiona Loader3 y no era viable. Su capa de bloques acepta las peticiones de escritura y devuelve éxito sin transferir nada. Las funciones que de verdad escriben en la NAND están en RAM, pero Loader3 no las usa. Llamarlas yo mismo sin el contexto del controlador de la NAND podía dañar la capa de traducción de toda la NAND.

La salida vino de otro sitio. Leí el volcado de `bootloader.bin` (480 KiB), desensamblé Loader3 y busqué qué determina el modo de arranque. Hay varios modos. El normal (el 11), donde se había estrellado mi cámara, carga `nflasha3`. Solo el modo 3 arranca el actualizador de `nflasha1`, esquivando `nflasha3`, y Loader3 lo elige solo si encuentra el fichero `\updater\mode` en `nflasha2`.

La comprobación está en una función que bauticé `chk updater`. Monta `nflasha2`, llama a una rutina que busca `\updater\mode` y compara el resultado con cero:

```asm
c01f15c0:  cmp r0, #0
           bge → el fichero existe → devuelve 1 → modo 3
```

Si `r0` es mayor o igual que cero, el fichero existe y se elige el modo 3. En mi cámara bloqueada, `r0` contenía `0xfffffed2`, un número negativo que significa «no existe». (Es el mismo número que el código de error del LED; no he demostrado que tengan la misma causa.)

Puse un punto de parada justo en esa comparación y, en ese momento, forcé `r0 = 0`. Modifiqué solo el registro `r0` con la CPU parada inmediatamente antes de ejecutar esa comparación.

No escribí nada en memoria ni en la NAND. Loader3 creyó que el fichero existía y eligió el modo actualizador. Esa función se llama desde ocho sitios, pero el camino del arranque pasa por ella dos veces. En ambos puntos puse `r0 = 0` y lo releí para verificar el cambio. Desde la entrada de Loader3 hasta el arranque del actualizador pasaron 696 milisegundos.

## Instalación y verificación

El actualizador de fábrica arrancó y el PC detectó el dispositivo USB de Sony en modo actualizador. Empecé a instalar el firmware oficial 3.26 con `pmca-console`. La NAND la escribió el actualizador de Sony, no yo.

El primer intento se detuvo al 45 % con el error `0x1063`. Según documentación previa de mi proyecto, ese código suele indicar que Darwin (el microcontrolador de gestión de energía) no responde, pero en este caso no pude confirmar la causa. Apagué y encendí la cámara. El actualizador arrancó solo, sin repetir el truco por SWD: el fichero `\updater\mode` ya existía, creado por el actualizador de Sony al empezar la instalación (este mecanismo estaba previsto en mi análisis; no lo verifiqué leyendo la NAND). El segundo intento llegó al 100 %.

Para verificar la recuperación, quité la batería diez segundos y encendí la cámara con OpenOCD cerrado. Apareció como `ILCE-6000` en modo Mass Storage, con el firmware 3.26 y sin LED de error.

## Consejos prácticos

- Lanza OpenOCD con `nohup … & disown` para que no termine con el shell.
- No ejecutes dos instancias de OpenOCD contra la misma sonda.
- Evita `kill -9`: puede dejar sucio el estado de depuración y obligarte a reiniciar la cámara.
- Al meter la batería con el interruptor en OFF, la cámara arranca y se apaga sola en menos de un segundo. No es un fallo.

## Límites y riesgos

- Esto funcionó en una cámara, con un fallo concreto y una sonda concreta. No es una garantía.
- Soldar en pads 0402 es irreversible y puede levantar pistas. Una tensión incorrecta en SWCLK/SWDIO puede dañar el BIONZ.
- La causa del error `0x1063` sigue sin conocerse; pudo ser un fallo aislado o interferencia de la sonda.
- La sonda sigue soldada en mi placa; todavía no la he retirado.
- No he verificado que el script exacto, `analysis/e26-recovery/r48_updater_swd.cfg`, funcione tal cual en otra cámara.
- Detalle técnico completo: [R46](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r46-procedimiento-fisico-swd.md) (procedimiento planeado), [R47](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md) (primer contacto), [R48](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md) (plan) y [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md) (informe de cierre). Estado actual: [Estado actual](14-Estado-actual).
