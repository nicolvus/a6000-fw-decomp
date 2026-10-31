# E26-R20-SERIE-PLAN — Síntesis: ¿levantar `CL1000` y enviar el bloque de arranque por el pin 9 repara la cámara?

**Fecha:** 2026-10-31 · **Origen:** evaluación del procedimiento de recuperación de fábrica
documentado en el propio BootROM, a partir de
[R20 — selector del BootROM](e26-r20-bootrom-selector.md) y del
[cierre estático R19/R20](e26-r19-r20-cierre-estatico.md). **Sin evidencia nueva**: solo
recombina hallazgos ya cerrados. **Solo estático.** Sin cámara, USB, UART ni NAND.

**Contexto:** la cámara, propiedad del usuario, no completa el arranque normal. Se evalúa si el
modo de mantenimiento que el propio BootROM del fabricante implementa permite restaurarla sin
desmontar la carcasa. Este documento es análisis de código y esquema; no ejecuta nada sobre
hardware real (restricción de proyecto: sin firmware ejecutado, sin cámara, salvo autorización
expresa).

## 1. El procedimiento evaluado

1. Llevar la isleta de prueba `CL1000` (sobre `BOOT_MAIN`, P7 del IC6000) a nivel alto — el
   selector de modo que el propio fabricante define en el BootROM.
2. Transmitir por el pin 9 del conector Multi (`UART_RX`/`BOOT_IN`) el bloque de arranque que el
   BootROM espera recibir en ese modo.
3. Comprobar si el BootROM lo acepta y le transfiere la ejecución, restaurando el arranque normal.

## 2. Qué confirma el árbol de decisión de R20 (§2 de ese informe)

`CL1000`=1 solo mueve el selector hacia el modo de mantenimiento; **no basta por sí solo**.
Siguiendo el diagrama de R20 con `MODEREG` bit 0 = 1:

- Si GPIO4.22 = 1 → el BootROM queda a la espera de datos por el puerto serie (`0xfa0`) sin más
  condición.
- Si GPIO4.22 = 0 → hace falta que `0x28c` (inicialización de almacenamiento) y `0x332` (carga de
  cabecera) tengan éxito; si la cabecera trae un código de verificación en `0xc0001200`, la espera
  por puerto serie solo se habilita si los datos enviados incluyen ese mismo código (paquete
  `KEY f:%x r:%x`). Código distinto o CRC incorrecto → LED de error `0x2002/0x2003`, no se habilita
  la espera.
- Si la tabla de verificación está vacía (sin código) → espera por puerto serie sin más trámite.

**Conclusión de R20:** llevar `MODEREG` bit 0 a 1 (inferido = `CL1000`/`BOOT_MAIN`) es
**necesario** para entrar en el modo de mantenimiento, pero **no se ha demostrado suficiente**: el
resultado depende de GPIO4.22 y, si éste es 0, del contenido real de la tabla de verificación.

## 3. Los tres datos físicos que decide el resultado (ya cerrados por separado)

| Dato pendiente | Estado | Qué decide | Si se resuelve a favor | Si se resuelve en contra |
|---|---|---|---|---|
| [`E26-R20-BOOTMAIN-NIVEL`](e26-r19-r20-cierre-estatico.md#3-e26-r20-bootmain-nivel--cerrado-límite) | CERRADO (límite) | Si `CL1000` ya está a 1 por defecto, o si llevarlo a ese nivel realmente mueve `MODEREG` bit 0 (la relación bit0↔`BOOT_MAIN` es inferencia, sin confirmar por hoja de datos) | El paso 1 es innecesario o ya funciona | El paso 1 puede no mover el bit, o no es seguro intentarlo sin conocer el pull interno del IC6000 |
| [`E26-R20-GPIO4`](e26-r19-r20-cierre-estatico.md#4-e26-r20-gpio4--cerrado-roles-resueltos-pines-no-identificables) | CERRADO (límite) | Si GPIO4.22 ya vale 1 (espera directa, sin código) o 0 (pasa por almacenamiento + código) | Con GPIO4.22=1 el procedimiento no necesita resolver el código | Con GPIO4.22=0 el procedimiento depende del dato siguiente |
| [`E26-R20-KEYTABLE`](e26-r20-keytable.md) | CERRADO (límite) | Si la tabla en `nflasha0` está vacía (sin código) o tiene un código real | Tabla vacía → espera por puerto serie sin trámite adicional | Tabla con código → los datos enviados sin el código correcto dan LED `0x2002/0x2003`, el procedimiento no se completa |

Los tres informes citados cierran **el mecanismo** (cómo decide el BootROM) pero no el **valor
físico** de cada condición: ese valor solo se obtiene con acceso a la cámara, no con las fuentes
disponibles en el repositorio (ROM, esquema, NAND volcada sin `nflasha0`).

## 4. Veredicto

**El procedimiento no se puede validar ni descartar de forma estática.** Es la vía de recuperación
más plausible que el análisis hasta R20 deja (ver cierre estático R19/R20 §5), pero su éxito
depende de tres datos físicos no medidos, fuera del alcance de las fuentes disponibles.

**No se puede cerrar `E26-R20-SERIE-PLAN` con una conclusión definitiva "repara"/"no repara" sin
alguna de:**

1. Medición pasiva (sin forzar nada) del nivel/pull de `CL1000` — resuelve `E26-R20-BOOTMAIN-NIVEL`.
2. Identificación del pin físico de GPIO4.22 (requiere hoja de datos del IC6000, no disponible) —
   resolvería `E26-R20-GPIO4`.
3. Acceso autorizado a `nflasha0` para leer la tabla de verificación — resuelve
   `E26-R20-KEYTABLE`.

Todas requieren abrir la cámara o acceso físico, fuera de alcance sin autorización expresa del
usuario para ese paso concreto (ver `E26-FISICO-BOOT`, que ya agrupa estas mismas tres medidas).

## 5. Estado del pendiente

`E26-R20-SERIE-PLAN` permanece **ABIERTO**: esta síntesis documenta por qué no puede cerrarse con
las fuentes estáticas disponibles, no resuelve la pregunta. Se cierra cuando se resuelva
cualquiera de los tres datos físicos de §4, lo cual coincide con el criterio de cierre de
`E26-FISICO-BOOT`.
