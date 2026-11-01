# 8. Cómo funciona el parche

El obturador lo gobierna **Darwin**, un microcontrolador aparte (`darwin_core`), que mueve las cortinillas mecánicas y las rearma tras cada foto.
El 3.23 modifica únicamente `darwin_core.bin` del firmware oficial 3.21 (157 276 B, dirección de carga `0x4200`), en dos pasos apilados:

| Paso | Cambio en `darwin_core.bin` | Efecto |
|---|---|---|
| **Tipo 0** | `0x20c78..0x20c7f` → `b 0x20c8e; nop; nop; nop` (`09e000bf00bf00bf`) | La función de tipo de mecanismo `0x20c74` devuelve siempre 0 (rama que ya existe, «sin bobinas»): no se activan P4D/P4E |
| **B1a** | `0x1fe6a: 28 46 → 0a e0` (2 bytes) | La compuerta `0x1fe66` devuelve siempre 0; los arrancadores eligen la lista `[0,7,8,9,10]`, que no usa el motor del obturador en captura ni en rearme |

La captura y el rearme no llegan a las primitivas que accionan P40/P41; la exposición la determina el sensor (reinicio y lectura por filas).
Después se actualiza `darwin.sum` (CRC-32 y tamaño) y se reempaqueta el FDAT: se descifra con `CXD90014`, se recalculan los CRC de cabecera y de `DEND` y se escribe el `.dat`.

## Por qué solo se toca Darwin

Cambiar solo Darwin deja intactas las particiones comprimidas (`nflasha3`), la parte que bloqueó la cámara con el 3.25.
El 3.23 pasó por el mismo actualizador y el mismo Loader3 con el `nflasha3` de Sony.

## Más detalle

- [E25 desactivación mecánica](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-desactivacion-mecanica.md)
- [Auditoría independiente E25-06](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-06-auditoria-independiente-paquetes.md)
- [Preparación de los paquetes E25-05](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-05-preparacion-paquetes-323-324.md)
