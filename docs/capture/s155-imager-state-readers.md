# S155 — tres xrefs al objeto de gates son lectores/accesores

S155 clasifica tres xrefs más de la base `0x43f72d02` que quedaron pendientes
en S153/S154. **VERIFICADO dentro de estos tres procedimientos:** dos son
predicados sobre `+0`; el tercero carga el puntero desde el slot GOT y lee
campos `+4` y `+0x1c`. Ninguno escribe `+3/+6` ni esos campos pertenecen a los
bits de gate. Esto es una conclusión local, no ausencia global de escritores.

## Lectores de `+0`

- `0x43857f90` pertenece a `FUN_43857f88`. Resuelve el slot
  `0x4401f990 → 0x43f72d02`, hace `ldrb r0,[r3]` y retorna un booleano derivado
  de si el byte es igual a 1. Instrucción `0x43857f90`, bytes `18 78`.
- `0x43857fb0` pertenece a `FUN_43857fa8`. Usa el mismo slot, hace la misma
  lectura `ldrb r0,[r3]` y retorna el predicado inverso (`byte != 1`). Bytes
  `18 78`.

REA referencia tipada para ambos: `ev_9975507315e3e9ae8b0b12ed371553fbde517212c7deab61373a08b5fdd07e0c`
y `ev_8af01bde84b54dc562aa3f33aacbc80ffbc8e7e2ca7f89e26e51b8143ca3dd92`;
las edges al objeto son READ. Los dos helpers tienen llamadores en
`FUN_43859710`, pero la existencia estática de esas llamadas no demuestra
alcanzabilidad runtime.

## Accesor `0x43858134`

`0x43858134` en `FUN_4385812c` vuelve a cargar `0x43f72d02` desde `0x4401f990`,
pero la edge a la base representa el puntero cargado (`PARAM`, no acceso a la
memoria de la base). Después lee `r3+4` y `r3+0x1c`. Sus stores están dirigidos
a otras estructuras/slots, incluyendo `0x43eedb70` y `0x43f7c704`; no a los
gates `+3/+6`. Evidence de referencias tipadas:
`ev_8e30d1b8e05356a533217a31f3da3ec92df520c6aa1e9eb79cca3dbd31c18132`.

## Alcance

El barrido S153 había observado que los xrefs directos a `+3/+6` eran lecturas
en el dumper. S155 muestra que estos tres xrefs adicionales tampoco escriben
esos flags. **No** se extrapola a las otras referencias a base, a `memcpy` de
bloque, DMA o alias no resueltos. Los 32 bytes de objeto están a cero en la
imagen; eso no revela valor de ejecución. No se modifica S51.

```sh
python3 analysis/s155_imager_state_readers/verify_state_readers.py
python3 -m unittest tests.test_s155_imager_state_readers -v
```

El JSON conserva bytes Thumb para los tres procedimientos y valores GOT usados;
la salida se recalcula desde `av-cam.bin` por `file_offset = VA−0x43541000`.
