# E26-R20-SERIE-PLAN — Síntesis: ¿"subir `CL1000` a 1 y enviar payload por pin 9" recupera la cámara?

**Fecha:** 2026-10-31 · **Origen:** evaluación del plan de recuperación propuesto, a partir de
[R20 — selector del BootROM](e26-r20-bootrom-selector.md) y del
[cierre estático R19/R20](e26-r19-r20-cierre-estatico.md). **Sin evidencia nueva**: solo
recombina hallazgos ya cerrados. **Solo estático.** Sin cámara, USB, UART ni NAND.

## 1. El plan evaluado

1. Forzar `CL1000` (isleta de prueba sobre `BOOT_MAIN`, P7 del IC6000) a nivel alto.
2. Enviar un payload de arranque por el pin 9 del conector Multi (`UART_RX`/`BOOT_IN`).
3. Esperar que el BootROM lo acepte y salte a él, evitando así el firmware bloqueado.

## 2. Qué confirma el árbol de decisión de R20 (§2 de ese informe)

`CL1000`=1 solo mueve el selector hacia la rama de servicio; **no basta por sí solo**. Siguiendo
el diagrama de R20 con `MODEREG` bit 0 = 1:

- Si GPIO4.22 = 1 → recepción serie directa (`0xfa0`). El plan funcionaría sin más condición.
- Si GPIO4.22 = 0 → hace falta que `0x28c` (init. almacenamiento) y `0x332` (carga de cabecera)
  tengan éxito; si la cabecera trae una clave en `0xc0001200`, la recepción serie solo se habilita
  si el payload enviado por el host incluye la misma clave (paquete `KEY f:%x r:%x`). Clave
  distinta o CRC mala → LED de error `0x2002/0x2003`, no recepción.
- Si no hay clave en la tabla (vacía) → recepción serie sin más trámite.

**Conclusión de R20:** subir `MODEREG` bit 0 (inferido = `CL1000`/`BOOT_MAIN`) es **necesario**
para entrar en la ruta de servicio, pero **no se ha demostrado suficiente**: el resultado final
depende de GPIO4.22 y, si éste es 0, del contenido real de la tabla de clave.

## 3. Los tres límites que decide el resultado (ya cerrados por separado)

| Límite | Estado | Qué decide | Si se resuelve a favor | Si se resuelve en contra |
|---|---|---|---|---|
| [`E26-R20-BOOTMAIN-NIVEL`](e26-r19-r20-cierre-estatico.md#3-e26-r20-bootmain-nivel--cerrado-límite) | CERRADO (límite) | Si `CL1000` ya está a 1 por defecto, o si forzarlo realmente mueve `MODEREG` bit 0 (la relación bit0↔`BOOT_MAIN` es inferencia, no confirmada por hoja de datos) | El paso 1 del plan es innecesario o ya funciona | El paso 1 puede no mover el bit, o forzarlo puede no ser seguro sin saber el pull interno del IC6000 |
| [`E26-R20-GPIO4`](e26-r19-r20-cierre-estatico.md#4-e26-r20-gpio4--cerrado-roles-resueltos-pines-no-identificables) | CERRADO (límite) | Si GPIO4.22 ya vale 1 (entrada directa, sin clave) o 0 (pasa por almacenamiento+clave) | Con GPIO4.22=1 el plan no necesita resolver la clave | Con GPIO4.22=0 el plan depende del límite siguiente |
| [`E26-R20-KEYTABLE`](e26-r20-keytable.md) | CERRADO (límite) | Si la tabla en `nflasha0` está vacía (sin clave) o tiene una clave real | Tabla vacía → recepción serie sin trámite adicional | Tabla con clave → el payload sin la clave correcta da LED `0x2002/0x2003`, el plan falla |

Los tres informes citados cierran **el mecanismo** (cómo decide el BootROM) pero no el **valor
físico** de cada condición: ese valor solo se obtiene con acceso a la cámara, no con las fuentes
disponibles en el repositorio (ROM, esquema, NAND volcada sin `nflasha0`).

## 4. Veredicto

**El plan no se puede validar ni descartar de forma estática.** Es la vía de recuperación más
plausible que el análisis hasta R20 deja (ver cierre estático R19/R20 §5), pero su éxito depende
de tres valores no medidos que están fuera del alcance de los datos actuales. No hay combinación
de lectura adicional de binario, esquema o NAND volcada que resuelva esto: los tres límites son
físicos.

**No se puede cerrar E26-R20-SERIE-PLAN con una decisión definitiva "funciona" / "no funciona"
sin alguna de:**

1. Medición pasiva (sin forzar) del nivel/pull de `CL1000` — resuelve `E26-R20-BOOTMAIN-NIVEL`.
2. Identificación del pin físico de GPIO4.22 (requiere hoja de datos del IC6000, no disponible) —
   resolvería `E26-R20-GPIO4`.
3. Acceso autorizado a `nflasha0` (lector NAND/JTOP o JTAG) para leer la tabla de clave —
   resuelve `E26-R20-KEYTABLE`.

Todas requieren abrir la cámara o acceso físico/JTAG, fuera de alcance sin autorización expresa
del usuario para ese paso concreto (ver `E26-FISICO-BOOT`, que ya agrupa estas mismas tres
medidas).

## 5. Estado del pendiente

`E26-R20-SERIE-PLAN` permanece **ABIERTO**: esta síntesis documenta por qué no puede cerrarse con
las fuentes estáticas disponibles, no resuelve la pregunta. Se cierra cuando se resuelva
cualquiera de los tres límites físicos listados en §4, lo cual coincide con el criterio de cierre
de `E26-FISICO-BOOT`.
