# S322 — trama A7S del formateador `0x43ad9666`

**Resultado:** para los registros de S315/S321, el formateador genera una trama por
registro con cinco bytes:

```text
81 | 03 | device | address8 | data8
```

El segundo byte vale `3` porque cuenta los tres bytes posteriores: dispositivo,
dirección y dato. Las tramas se concatenan en el búfer P2S y cada transmisión termina
en `00`. El modo 2 no modifica esta codificación; solo selecciona una lista y activa el
reintento documentado en S320.

## Cadena estática (REA primero)

REA decompiló las siete funciones consultadas (evidencia
`ev_4d11d6e5e67806c9404fb64236de7edaf8b8dcbed1afe35beed8c00119840a2f`):

- `0x43ad9666` consulta capacidad con `0x436f2554`, llama a `0x43ad9628` y transforma
  su retorno con `xor 1`; si no hay espacio devuelve `2`.
- `0x43ad9628` abre o continúa la trama, llama a `0x43ad9536` para cabecera/dirección y
  a `0x43ad95a6` para el dato.
- `0x43ad9536`, con `obj[0]==0`, escribe `0x81`, reserva el byte de longitud, escribe
  `obj[3]` como dispositivo y una dirección de 8 bits (`obj[1]<=8`).
- `0x43ad95a6`, con `obj[0]==0`, añade el dato de 8 bits (`obj[2]<=8`).
- `0x43ad9374` cierra la trama anterior y calcula `longitud = fin - longitud - 1`.

Contrato observado del wrapper: `0=éxito`, `1=rechazo del ensamblador`, `2=sin espacio`.
El valor `2` es el que activa el único reintento de S320.

## Confirmación con evidencia previa

Se reutilizó, sin reejecutarla, la emulación del código real conservada en
`analysis/s58/out/a7s_scenarios.json`: 12 escenarios, 1200 registros y 1200 tramas
decodificadas. Todas cumplen `81 03 device address data`, reproducen exactamente
`device_seq` y terminan cada transmisión con `00`. Ejemplo inicial:
`81 03 81 00 1c`.

Esto confirma y delimita S56/S58: el byte `0x81` inicial es la cabecera P2S; el tercer
byte es el dispositivo del registro (`0x81` o `0x83`), seguido por dirección y dato.
No hay agrupación de direcciones consecutivas en este camino A7S: hay una trama por
registro.

## Límites

- Análisis estático y reutilización de una captura de emulación ya versionada; no se
  ejecutó firmware, cámara ni flasheo.
- La semántica eléctrica del bloque P2S y el significado físico de los registros siguen
  **NO_VERIFICADOS**.
- El enlace entre «modo 2» y silent shutter sigue **NO_VERIFICADO**. S51 no cambia.

## Reproducción

```sh
.venv/bin/python analysis/s322_frame_format/build_frame_format.py
.venv/bin/python analysis/s322_frame_format/verify_frame_format.py
.venv/bin/python -m unittest tests.test_s322_frame_format
.venv/bin/ruff check analysis/s322_frame_format tests/test_s322_frame_format.py
.venv/bin/mypy --ignore-missing-imports analysis/s322_frame_format
```

El verificador realiza 1282 comprobaciones; la suite contiene 6 tests.
