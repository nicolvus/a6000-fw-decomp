# S140 — vector de registros IMX210 y bancos dinámicos

**Pregunta:** ¿qué contiene el vector de 119 punteros `0x43fe995c` y qué puede
decirse de las filas de 16 bytes en los bancos de parámetros de exposición?

## VERIFICADO — vector de registros

En `av-cam.bin` de A6000 fw3.21 (SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`), el
vector desde `0x43fe995c` contiene 119 punteros de 32 bits y el terminador cero
en `0x43fe9b38`. Cada destino empieza con `u16 ID` little-endian, byte de valor
en `+2` y byte adicional en `+3`. La lista completa y los bytes de cada registro
están en [`imager_regmap.json`](../../analysis/s140_imager_regmap/imager_regmap.json).
Por ejemplo, los índices 1 y 2 apuntan a `0x4401ca2c` y `0x4401c734`, ambos ID
1; el primero es el registro cuyo byte +2 se prepara por SetExposure, como ya
establecen S44/S57. El orden del vector no es orden numérico estricto de ID.

REA observó una lectura completa de 484 bytes desde el vector
(`ev_3e4a16b351da4229205a68b4225aedf7ff70d9edb3e89440d91314576341614b`).
La resolución de lista por `0x436d79b0` aparece en REA bajo Evidence
`ev_3cb33364f766ef7f926eb693085d696eeaff00514ee05e7183a4df52d1af3496`;
el consumidor y el transporte P2S están descritos en S44. Los bytes del archivo
se contrastaron por separado con el lector reproducible de este hito.

## PARCIAL — bancos de filas

El rango `0x43eb35d0..+0x147` (S) y `0x43eb07fc..+0xff` (G+`0x224`)
contienen ceros en la imagen distribuida. Por ello sus bytes estáticos no
permiten recuperar valores de una captura: son estado que se completa durante
la ejecución. El consumidor `0x43b0893c` selecciona una fila de 16 bytes con
índice `S[0]`, desde `S+4+16·índice`, y copia la fila al staging `S+0xc4`;
`0x43849fb8` transfiere campos de esa fila al bloque de exposición. La lectura
de REA de `0x43b0893c` (`ev_b376d03662f3edddb3c528e4fa223070270ef09dbc71e5ef8ccc7d012e05857b`)
concuerda con las instrucciones Thumb contrastadas contra los bytes.

S58 ya había establecido que la etapa AE alimenta los bancos y que S es estado
de envío, no una tabla constante de parámetros. Este hito enumera los bytes,
pero **no** resuelve qué modo fotográfico selecciona cada fila ni atribuye
significado físico a ningún campo. No modifica S51: obturación completamente
electrónica permanece sin demostrar.

## Reproducción y límites

```sh
python3 analysis/s140_imager_regmap/extract_regmap.py
pytest tests/test_s140_imager_regmap.py -q
```

El script recalcula offsets con `file_offset = address - 0x43541000`, extrae
el vector y ambos rangos y verifica la integridad SHA-256. La inspección REA fue
estática; no se ejecutó firmware ni se observó un banco en uso. El valor de un
registro no es interpretado como efecto eléctrico sin documentación o evidencia
adicional.
