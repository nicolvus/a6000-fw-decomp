# E21 — Lecturas sin cámara de los volcados del 20-10-2026

Solo lectura de `analysis/camera-dumps/` (ILCE-6000, fw 3.21). No se ejecutó nada en cámara. Etiquetas: `VERIFICADO` (leído en el volcado), `INFERENCIA`, `NO_VERIFICADO`.

## 1. ARM7 SRAM (`regiones-20261020/arm7sram_0x0_0x4000.bin`)

- `VERIFICADO`: 16 KiB, 13 183 B no nulos. Código **ARM de 32 bits** (0 instrucciones válidas en Thumb en los primeros 0x400 B), no Darwin.
- `VERIFICADO`: tabla de vectores en `0x0` (`ldr pc,[pc,#…]`); reset en `0x23c`: pone a 0 una palabra, inicializa la pila en los seis modos (`cpsr` 0xd2, 0xd1, 0xd7, 0xdb, 0xd3, 0xdf) y llama a `0x10c+…` (`bl`) antes de un bucle infinito.
- `VERIFICADO`: sin cadenas legibles (solo fragmentos de 5 B sin sentido); literales de periférico: `0x11000` (E/S ARM7, volcada en `arm7io`) y `0x20000` (registros NAND, volcados en `nandreg`).
- `INFERENCIA`: es el firmware de un coprocesador ARM7 cargado en SRAM local, con acceso a esos dos bloques. No se desensambló más allá del arranque.
- `NO_VERIFICADO`: su papel respecto al obturador. `arm7io` está casi a cero (16 filas con `1`) y `nandreg` casi a cero: sin información de captura.

## 2. Clave Backup `0x3000b` (BK4)

- `VERIFICADO`: las 18 copias (`20261020-*`, `nvram-referencia`, `post-*`, `silent-nvram/*`) tienen **el mismo valor**: 256 B, `attr 0x8`, 10 bytes no nulos, todos `0x01`, en los desplazamientos `0x30`–`0x37`, `0x41` y `0x51`.
- `VERIFICADO`: los bytes `+3` y `+6` (los gates de S305/P18) valen 0 en el BK4, igual que en la RAM viva (`0x83f72d00`, 32 B a cero). Coherente, pero **ni los desplazamientos `0x30…` ni el cambio Silent alteran la clave** (idéntica en `1-base`, `2-silent` y `3-revertido`).
- `NO_VERIFICADO`: el significado de los bytes `0x30`–`0x37`, `0x41`, `0x51`.

## 3. Matriz `0x43e80160` (RAM viva, `ram-servicio-20261020`)

- `VERIFICADO`: los primeros `0x270` B son una **tabla de 13 registros de 0x30 B** con campos fijos: `+0x14/+0x18` = pares ancho×alto (`0x1626`×`0x1000`, `0x12fc`×`0xcd6`, `0x165b`×`0x1035`, `0x160a`×`0xfe4`), `+0x1c` = `0x98` constante y un id en `+0x24`/`+0x2c` (`0x104f`, `0x513`, `0x506`, `0x289`…). Tras `0x270` siguen punteros `0x4099e9xx` y estructuras de otra clase.
- `INFERENCIA`: descriptores de tamaño de lectura (similares a los rectángulos de `[EXL]`); en la imagen estática estaba a cero (S328), así que los llena el código en ejecución.
- `NO_VERIFICADO`: quién la escribe; la ventana de 4 MiB de `silent-ram-*` no cubre `0x83e80160`.

## Efecto en los pendientes

E21 se cierra con límite. P16 queda reducida a «identificar el escritor» (ya se conoce la forma de los datos). P18: en reposo, gates a 0 en BK4 y RAM; faltan live view y disparo.
