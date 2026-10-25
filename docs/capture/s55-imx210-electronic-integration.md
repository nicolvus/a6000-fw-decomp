# S55-E — IMX210: transporte e integración electrónica (20-10-2026)

**Alcance honesto:** S55 dedicó su esfuerzo a las fronteras GPIO/SENS_B y no obtuvo evidencia nueva sobre la terminación electrónica de integración. Este informe fija lo
heredado, lo nuevo y la frontera.

## Heredado (VERIFICADO en S34–S54, no repetido)
`SetExposure 0x436d6f6c` (wrapper `0x436d6320`), política `0x43842158`, selector `0x437f7f98`; ShutMode 0 implementado; lecturas completas `0x0b/0x2f`; cadena
`captura → +0x4d0 drive_mode → 0x43795a60 → registros de estado`; escritura MMIO condicional `0xf3120220` (VD) desde `0x43ad2bd6`; consumidor `0x436d75f8` (119 pares ID u16/byte)
→ backend → `0x436d5ed0` (carga MMIO) y `0x436d5f60` (pulso B+8). A7S: `SetExposure 0x436f4168`, modos Silent `0x4e/0x4f` (IMX235), clase 0.

## Nuevo en S55
1. **Pin de imager `(15,5)`** = IDs `0xf90343/344`: `gpio_set(15,5,·)` cierra el constructor de `ImagerCtrl` en A6000 (`0x436d670a`, tras fijar vtable/ptrs de 0x28000/0x2c00)
   y el de A7S (`0x436f3f90`). Mismo pin en IMX210 e IMX235: el imager usa un GPIO de control equivalente (función eléctrica NO VERIFICADO: reset/standby/alimentación).
2. **El `set` extra de A7S** (`0xf90381/382`, constructor `0x436f3c98`) está sin asignar en el preset ⇒ no-op. No hay GPIO adicional de A7S que explique Silent.
3. Hay un `cfg` sobre `(0xf9049a,0xf9049b)` en ambas (`0x43a0d65a` / `0x439f67d8`), sin asignar en A6000 y A7S ⇒ no-op.
4. Las líneas de configuración del sensor (`CIS0_XCS/CIS0_SCK/CIS0_IMG_RST`, esquema) son del bloque CISIF/serie de BIONZ; **no** pasan por la base de pines GPIO. Cadenas `ImagerCommon::SetCISIFRequest/GetCISIFSyncCodeRequest`
   (`0x43c9450d…`) sitúan ahí el acceso; su transporte registro a registro sigue sin reconstruirse.

## Pregunta crítica (E.3)
¿Evidencia de fin de exposición fotográfica electrónico en IMX210 sin cortina mecánica? **No hay ni a favor ni en contra** en S55. La rama ShutMode 0 no basta (S51). Distinciones respetadas:
fin de integración ≠ fin de DMA ≠ guardado ≠ notificación (`ExposureEndNotify` es solo un mensaje de 2 B, S55-D).

## Frontera (E.5)
1. Falta: datasheet del IMX210 o traza pasiva del bus CIS (serie) y de `CIS0_IMG_RST`. 2. Por qué: sin la semántica de los campos ID/byte no se distingue «reset de filas / fin de integración»
de una configuración. 3. Resultado: fijar si existe un registro de «fin de exposición» y su disparo (VD vs comando). 4. Cobertura histórica: S34–S54 + S55 (GPIO); no acredita agotar el análisis estático. 5. Propuesta física diferida: analizador lógico
sobre CIS0 + VD durante una foto mecánica y una EFCS. **No se declara imposible.**
H55-7: **NO VERIFICADO.**

Actualización 24-10-2026: quedan cuerpos y enlaces concretos en la
[cola auditada](repo-audit-2026-10-24.md). Las pruebas físicas siguen diferidas.
