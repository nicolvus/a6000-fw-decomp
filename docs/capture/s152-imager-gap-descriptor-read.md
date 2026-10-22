# S152 — una ruta de diagnóstico lee el byte del hueco G

S152 resuelve la pista S150: **dos entradas de descriptor** apuntan al mismo
byte del gap `0x43eb0850` y un consumidor de copia raw usa el campo `addr`.
Cuando se usa la entrada de tamaño 1, la ruta lee exactamente ese byte y copia
el valor a un buffer del llamador. Esto verifica un uso de lectura estático,
no una escritura ni su alcanzabilidad en una captura.

## Descriptores encontrados

Bytes originales de A6000 fw3.21, `av-cam.bin` SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`:

| Tabla | Base | Entradas incl. terminador | Índice | Registro | `{id,size,addr}` |
|---|---:|---:|---:|---:|---|
| A | `0x44008028` | 68 | 32 | `0x44008128` | `{0x0030,1,0x43eb0850}` |
| B | `0x4400b248` | 59 | 6 | `0x4400b278` | `{0x0030,1,0x43eb0850}` |

La estructura observada en bytes es `{u16 id, u16 size, u32 addr}` little-endian,
8 B por entrada. La celda que apareció en S150 (`0x4400812c`/`0x4400b27c`) es
el campo `addr` de cada entrada, no el comienzo del registro. El script
recalcula ambos índices, campos y terminadores.

REA Evidence de las entradas: tabla A
`ev_f8bd0f66f1e8d90f997d6ea0c37e47e3911c40c8dc9de66f9652bfca536f4289`, tabla B
`ev_01d929687b87aa4343c193261123044fac8ffad3ae264dda33a77826adfffa90`.
Dentro de `FUN_43858338`, las dos bases se materializan mediante referencias
PC-relative: `0x438583c4 → 0x44008028` y `0x43858504 → 0x4400b248`
(`ev_0ef38c5ad0d5093989b4713814af48c02df0b5d75a9d98b879db44444d517eb5`,
`ev_c42f20caa4477198bfa7003dcd55b507a1fe754cbd56a3b5054f7bdfb77858b6`).

## Consumidor y acceso efectivo observado

`FUN_43858338` selecciona un formatter a partir de su segundo argumento:
valor cero elige el copiador `FUN_43b09c7a`; valor no cero elige el volcado
hexadecimal `FUN_43857fc4` (Evidence selector `ev_34e0e04b1ff478bef5490226e075705d72132d109dfa68e7663c2056be5edbfb`).

El copiador raw carga `size` desde entrada+2 y `addr` desde entrada+4; lee
`addr+size-1-i` y escribe los bytes en el buffer de salida del llamador
(`ev_2d31ad1d2d49ace2985775034cfc294bb17251c7e6930056dfb4cb9c47716ffa`). Para
`{id=0x30,size=1,addr=0x43eb0850}`, el acceso fuente es **exactamente una
lectura de `0x43eb0850`**. No se observa escritura a ese origen. El formatter
hex usa los campos iniciales del descriptor pero no el campo addr
(`ev_6efbdb9318dab3f4c890adbbc9f1e066ffa8905d6ccb639967336a706653e212`).

Las dos llamadas se observan en el mismo caller `FUN_43859710`; están bajo
gates de bits del bloque `0x43f72d02`: bit 1 de `0x43f72d05` y bit 5 de
`0x43f72d08` (call sites `ev_f944e886a327ba29e26b3daefbb015d751b348023b937b6ee1eae21ed370ddc3`).
Ambos bytes están a cero en la imagen (`ev_bb32443f6fbf218e8e633251877e90f9a85a57324d21e818d58e4f45a8d72c0f`),
por lo que la alcanzabilidad en ejecución queda **PARTIAL**: no se conoce el
valor runtime de esos flags. No se afirma que la ruta se ejecute en una foto.

## Alcance y límites

- **VERIFICADO:** hay dos descriptores y el copiador raw leído usa su dirección
  como fuente; `size=1` produce una lectura del gap.
- **PARTIAL:** cuándo se satisfacen los gates durante una captura.
- **NO_VERIFICADO:** escritura del byte por otro flujo, significado físico del
  campo, relación del descriptor con modo fotográfico o control del sensor.
- **No cambia S51.** La lectura por un camino de diagnóstico/volcado no prueba
  que el firmware programe ese byte ni que afecte la exposición.

```sh
python3 analysis/s152_imager_descriptor_reads/verify_descriptor_reads.py
python3 -m unittest tests.test_s152_imager_descriptor_reads -v
```
