# S160 — `FUN_4383abec` escribe `state+0`, no los gates

S160 confirma un writer de la base `0x43f72d02` que la lista S153 señalaba.
**VERIFICADO:** `0x4383ac90` es `strb r3,[r2,#0]`; REA tipa la escritura en
`0x43f72d02+0`. El slot `0x4401f990` suministra esa base. En la ruta que llega
al store, `r3` vale cero tras decrementar el contador compartido hasta cero.
El destino no es `+3` ni `+6`.

## Procedencia y guard

El procedimiento `FUN_4383abec` (`ev_134be2dfce4598770fe1825386a5899cfad96fb794784e8673a5c3f42e37bd3b`)
obtiene la tabla GOT `0x4401eee4`, suma `0xaac` y lee el slot `0x4401f990`;
bytes `02 2d f7 43` → `0x43f72d02`. En `0x4383ac8c/8e` carga el mismo slot,
y en `0x4383ac90` almacena un byte a offset 0. La instrucción typed WRITE de
REA es `ev_3992433ca320c9303ec5bd74990f7e8e53f481516afd812000138c8654f83014`;
bytes `13 70`, offset de archivo `0x2f9c90`. El pseudocódigo del cuerpo
(`ev_d9486547d0d47dc8039f483cc2e75d37bee5fd8e82c1044c8d033137462f0946`)
reduce el contador `0x43f7c710`; si aún no llega a cero, no entra en el store.

Hay dos llamadores estáticos observados (`0x4383b350`, `0x4383b3b0`), cada uno
con condiciones diferentes sobre otros bytes/contadores (`ev_d26c82da23892ec4f409332c9f21087a17c6239b8c09a0c620d048fd5aae0213`,
`ev_2db8b63f3ac711416bf1412cf5b9f69e4bce744fb6e3edf0af500029e9d7aa32`). Esto
no demuestra que el contador expire durante una foto concreta.

## Alcance

**VERIFICADO localmente:** el writer observado es a `+0`; no modifica los
gates `+3/+6`. El slot contiene un puntero en la imagen, y su posible cambio en
runtime no se observó. El byte `+0` puede participar en otros predicados
(S155), pero no se asigna semántica física. Esta localización no resuelve
escritores de gates por copia de bloque, alias u otras funciones. S51 no cambia.

```sh
python3 analysis/s160_state_open_flag_writer/verify_open_flag_store.py
python3 -m unittest tests.test_s160_state_open_flag_writer -v
```

El JSON incluye bytes y disassembly independiente sobre `av-cam.bin` con
`file_offset=VA−0x43541000`.
