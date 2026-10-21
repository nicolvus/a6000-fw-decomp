# Barrido de registros 0xF0000000 (parcial, 2026-10-20)

`scripts/senser_sfr_scan.py` (RMEM por service mode, 4 KiB por página, tolerante a fallos). Incompleto: se detuvo tras 5 páginas fallidas (cada una reinició la cámara) y no se reanudó.

- `state.json`: 32 páginas leídas (`0xF0000000-0xF001FFFF`), 5 malas (`0xF0020000-0xF0024000`), tramo saltado `0xF0025000-0xF00FFFFF` (sin verificar).
- `leido_0xf0000000_0x20000.bin` (128 KiB): lo leído. `scan_0xf0000000.bin` (64 MiB, casi todo ceros) no se versiona.
- Dentro de `0xF0000000-0xF000FFFF` las 16 páginas son idénticas (un juego de registros <4 KiB repetido; 11 palabras no nulas) y en `0xF0010000-0xF001EFFF` otras 15 idénticas (6 palabras); `0xF001F000` es cero. Naturaleza (¿DMA?) NO VERIFICADA.
- Por telnet (`dd` de `/dev/mem`) estas direcciones dan `Bad address`: solo se pueden leer por service mode.
