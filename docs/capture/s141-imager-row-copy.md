# S141 — selección de fila y límite del origen dinámico

S141 sigue la pregunta abierta de S140: de dónde sale el selector `S[0]` y
cuándo se rellenan las filas. **Resultado PARCIAL:** se vuelve a comprobar la
lectura/selección/copia estática de fila, pero el escritor de `S[0]`, sus gates
y el paso desde `0x43843a44` siguen sin demostrarse. No cambia S51.

## VERIFICADO — operaciones que sí se observan

REA Evidence `ev_b376d03662f3edddb3c528e4fa223070270ef09dbc71e5ef8ccc7d012e05857b`
para `0x43b0893c` muestra: `ldrb` de byte `[r0]` en `0x43b08942`; cálculo
`r0 + (S[0] << 4) + 4` en `0x43b08944..48`; `ldmia` de cuatro palabras desde
esa dirección y `stm` a `S+0xc4` en `0x43b0894a..4c`. Así se verifica la copia
de 16 bytes, no el valor que runtime toma `S[0]`. REA observa como caller
`0x43b08750` (Evidence `ev_b1bd068317fa32b2167455cc5189065e7d50b48f6e99b20ffde5dd250cfd3513`).

En el constructor de exposición `0x43849fb8`, REA Evidence
`ev_158664de14075207b8688292074cd88ef3ba64d4e12caeac876ffc695254c9f9`
muestra la carga de cuatro palabras desde `S+0xc4` y su escritura al destino
recibido (`0x43849fbe..0x43849fd4`), seguida por campos derivados de `S+0xd4`.
REA anotó cero callers directos reconocidos para esta entrada; por tanto la
relación de callers no cierra la cadena superior.

## NO VERIFICADO — producción runtime

El subagente intentó resolver `0x43843a44` como procedimiento REA, pero el
proveedor no lo reconoció en la sesión disponible. Esto es una limitación de
cobertura, **no** prueba que la función, los stores o el productor no existan.
No quedó demostrado quién escribe `S[0]`, cuáles condiciones preparan las filas,
ni cómo `G+0x224` alimenta el staging. Los bancos revisados están a cero en la
imagen original y no codifican una captura real.

El código Thumb de ambos puntos sí se contrastó en el binario original, con
`offset = VA - 0x43541000`; los bytes y el desensamblado reproducibles están en
[`row_trace.json`](../../analysis/s141_imager_row_trace/row_trace.json).

```sh
python3 analysis/s141_imager_row_trace/verify_instructions.py
python3 -m unittest tests.test_s141_imager_row_trace -v
```

Siguiente pregunta concreta: encontrar una coordenada Thumb REA admisible para
la rutina referida como `0x43843a44` y seguir, en evidencia positiva, el store
a `S[0]` y el movimiento `G+0x224 → S`. No interpretar los campos como
registros físicos ni ejecutar el firmware.
