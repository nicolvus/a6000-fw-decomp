# E26-R22 — Mapa completo del BootROM «Musashi Loader1 Ver.01.00» (30-10-2026)

Imagen: `analysis/camera-dumps/updater-20261020-175427/bootrom.bin` (24 576 B; contenido real `0xffff0000`–`0xffff1a80`, el resto es `0x00`). Mapa: `analysis/e26-recovery/r22_bootrom_map.py` (descenso recursivo Capstone) + lectura del código. Test: `tests/test_e26_r22_bootrom_map.py`. Etiquetas: **BINARIO** = desensamblado; nombres de función = propios (el ROM no tiene símbolos).

## 1. Resultado

Las **57 rutinas** del ROM están identificadas y ninguna función descubierta queda sin nombre. Lo que se sabía en R5/R8/R9/R12/R20/R21 queda integrado; lo **nuevo** de R22 es: la capa de carga de bloques completa (`0x150`–`0x514`), el controlador de bloque (`0x12d8`, `0x1532`), la biblioteca `printf`/`memset`/CRC, la consola y el anillo de traza, y las dos variantes del patrón de LED de error.

## 2. Hallazgos nuevos

1. **El reloj de los temporizadores del BootROM es 4 MHz (VERIFICADO en el propio ROM).** `error_blink` (temporizador) usa medio periodo largo `0x1e8480` = 2 000 000 ticks y pausa `0x7a1200` = 8 000 000; `error_blink_ms` (delay en ms) hace el mismo patrón con 500 ms y 2000 ms. 2 000 000 ticks = 500 ms ⇒ **4 ticks/µs**. Eleva a VERIFICADO la inferencia de R21 (16 000 y ~47 600 baudios) y fija el LED de error: **largo 0,5 s encendido/0,5 s apagado, corto 0,25/0,25, pausa 2 s** (código `0x1001`–`0x100e`: 0 largos; `0x2001`–`0x2005`: 1; `0x3001`–`0x3004`: 2).
2. **Consola y traza.** `console_puts`/`trace` escriben caracteres en `[0xc0005030]` (un registro de consola en eSRAM, uno por núcleo con paso `0x10`) y cada `(etapa,paso)` queda en un anillo `0xc0006000–0xc000b000`. Las etapas son: 2 = ruta serie, 3 = receptor serie, 4 = almacenamiento, 5 = bloques. Los pasos se listan en §5.
3. **Tabla de claves y cabecera.** `load_header` lee 3 bloques a `0xc0000600`; `find_key_entry` recorre `0xc0001200` (0x180 palabras) en busca de la primera ≠ `0xFFFFFFFF` y copia 8 B (cadena «KEY f:%x r:%x»); `load_key_target` y `load_payload` usan esos campos para leer la imagen. Resultado: sin clave en la tabla no hay segunda carga (cierra el alcance de `E26-R20-KEYTABLE`).
4. **Código muerto:** `crc32_update` (`0xc18`) no tiene llamadores; `crc32_byte` solo lo usa la ruta serie y `crc32` solo `main`.
5. **Arranque multinúcleo:** `reset` marca `[0xc0005000+0x1c+núcleo]=0xff`; el núcleo 0 sigue a `main`, los demás esperan (`wfe`) a que su marca sea 0 y saltan a `[0xc000500c+4·núcleo]`.

## 3. Rutinas

| Dirección | Nombre | Función | Llamada desde |
|---|---|---|---|
| `0xffff0104` | `fmt_ext_dispatch` | Thumb: extensión de printf; 'd'→0x1608, 'x'→0x167c, otro→0 | `16d8` |
| `0xffff0114` | `delay_ms_arm` | ARM: espera en ms (lazo de 0xdac0 iteraciones por ms) | — |
| `0xffff013c` | `jump_main_image` | bx 0xc0030000 (Loader2 cargado) | `1062` |
| `0xffff0144` | `jump_serial_image` | bx [0xc000500c+0xc] (destino fijado por la ruta serie) | `0fa0`, `1062` |
| `0xffff0150` | `block_read` | lee N bloques vía 0x1352, vuelca estado al anillo de lectura, mapea códigos 0x3005/0x3006 | `02c6`, `0332`, `03de`, `0486` |
| `0xffff0244` | `nand_ctrl_timing` | escribe tiempos del controlador de bloque (0x20100..0x20190) | `1062` |
| `0xffff028c` | `storage_init` | 0x12d8 + marca [0xc0005024]=1 y puntero de anillo (0xc0010000) | `1062` |
| `0xffff02c6` | `load_boot_main` | block_read(0,3,0xd,6)→0xc0030000; error 0x1004/0x1005 | `1062` |
| `0xffff0332` | `load_header` | block_read(0,0,3,6)→0xc0000600; error 0x1006/0x1007 | `1062` |
| `0xffff039c` | `find_key_entry` | busca la 1.ª palabra ≠0xFFFFFFFF en la tabla 0xc0001200 (0x180 palabras) y copia 8 B | `1062` |
| `0xffff03de` | `load_key_target` | block_read con campos de la tabla de clave → 0xc0000000; error 0x1008/0x1009 | `1062` |
| `0xffff044e` | `check_loaded` | comprueba que 0xc0000000 (0x180 palabras) no es todo 0xFFFFFFFF | `1062` |
| `0xffff0486` | `load_payload` | copia 4 parámetros de la cabecera a 0xc0005000 y block_read; error 0x100a/0x100b | `1062` |
| `0xffff0514` | `ring_push` | añade una palabra al anillo 0xc000b000..0xc0010000 (puntero en 0xc0010000) | `0150` |
| `0xffff0554` | `serial_profile_select` | GPIO(4) bit21 → perfil en 0xc0010218 (R21) | `1062` |
| `0xffff05da` | `sample_confirm` | espera `filtro` ticks y reexamina MODEREG bit1 (error 0x3004 si cambia) | `0634`, `0876` |
| `0xffff0634` | `serial_recv_bytes` | recibe N bytes 8O1 (paridad impar) por MODEREG bit1; acumula CRC; errores 0x100c/0x100d | `0876` |
| `0xffff0876` | `serial_receiver` | sincronismo 60 flancos + cabecera/longitud/carga (R8/R21) | `0fa0`, `1062` |
| `0xffff0bd4` | `get_flag0` | devuelve [0xc0010004] | `0fa0`, `1062` |
| `0xffff0bda` | `get_flag1` | devuelve [0xc0010004+4] | `0fa0` |
| `0xffff0c00` | `crc32_byte` | CRC-32 reflejado 0xEDB88320, un byte | `0634` |
| `0xffff0c18` | `crc32_update` | CRC-32 (buf,len,acc) — sin llamadores (código muerto) | — |
| `0xffff0c52` | `crc32` | CRC-32 completo con inversión final | `1062` |
| `0xffff0c98` | `console_puts` | cadena → registro de consola [0xc0005030] + LF | `0634`, `0876`, `0d62`, `1062` |
| `0xffff0cb6` | `trace` | (etapa,paso): anillo 0xc0006000..0xc000b000 y línea «%02d:%02d» a la consola | `0150`, `0244`, `028c`, `02c6`, `0332`, `039c`, `03de`, `044e`, `0486`, `0554`, `05da`, `0634`, `0876`, `0fa0`, `1062` |
| `0xffff0d14` | `ctx_reset` | pone a cero 0xc0005030/40/50/60, 0xc0010238 y reinicia el anillo de traza | `1062` |
| `0xffff0d4c` | `led_gpio_init` | habilita las GPIO del LED (0xf2910000/0xf2912000) | `1062` |
| `0xffff0d62` | `error_blink` | código → (c>>12)−1 largos + (c&0xfff) cortos, medio periodo 0x1e8480 ticks; no retorna | `0fa0`, `1062` |
| `0xffff0e0a` | `error_blink_ms` | mismo patrón con delay_ms (500/250 ms, pausa 2000 ms); usado si falla el temporizador | `0efc` |
| `0xffff0ed0` | `timer1_restart` | reinicia temporizador 1 (0xf2403100) | `0634`, `0876` |
| `0xffff0ee8` | `timer0_restart` | reinicia temporizador 0 (0xf2403000) | `0876`, `0d62` |
| `0xffff0efc` | `timer_init` | programa ambos temporizadores (0x1030) y comprueba que cuentan (0xe10 vueltas, si no 0x100e) | `1062` |
| `0xffff0f36` | `wait_t0` | espera a que temporizador 0 alcance r0 | `0d62` |
| `0xffff0f52` | `wait_t1` | espera a que temporizador 1 alcance r0 (0 = ok) | `05da`, `0634` |
| `0xffff0f72` | `t0_expired` | -1 si temporizador 0 > r0 | `0634`, `0876` |
| `0xffff0f82` | `t1_expired` | -1 si temporizador 1 > r0 | `0634`, `0876` |
| `0xffff0fa0` | `serial_entry` | ruta serie: espera clave/bandera, llama serial_receiver y salta a la imagen | `1062` |
| `0xffff1062` | `main` | selector MODEREG bit0: 0 = Loader2 por almacenamiento; 1 = ruta de servicio | — |
| `0xffff12d8` | `storage_ctrl_init` | reinicia/configura el controlador de bloque 0x20000 | `028c` |
| `0xffff1352` | `read_sectors` | lector de sectores 0x600 B (FIFO 0x10000010), reintentos (R20) | `0150` |
| `0xffff1532` | `ctrl_reset` | pone/quita el reset del controlador (0x200f0 bit4) | `12d8` |
| `0xffff1584` | `snprintf` | snprintf(buf,n,fmt,…) | `0634`, `0876`, `0cb6`, `0d62`, `1062` |
| `0xffff15b8` | `pad_left` | relleno previo del campo (espacios/ceros) | — |
| `0xffff15e4` | `pad_right` | relleno posterior del campo | — |
| `0xffff1608` | `fmt_decimal` | conversión %d/%u | — |
| `0xffff167c` | `fmt_hex` | conversión %x/%X/%p | — |
| `0xffff16d8` | `vformat` | intérprete de formato (flags, anchura, conversiones) | `18e2` |
| `0xffff1814` | `memset_word` | memset con replicación del byte | `1352` |
| `0xffff1824` | `emit_field` | emite un campo numérico con relleno | — |
| `0xffff18d8` | `fmt_getc` | siguiente carácter del formato | — |
| `0xffff18e2` | `vsnprintf` | inicializa el contexto y llama a vformat | `1584` |
| `0xffff1908` | `putc_unbounded` | escribe un carácter y avanza | `1584` |
| `0xffff1912` | `putc_bounded` | escribe un carácter si cabe | — |
| `0xffff1922` | `memclr` | memset(…,0) | — |
| `0xffff1926` | `memset` | memset general (alineación + 0x1998 en bloques) | — |
| `0xffff1968` | `divmod10` | ARM: r0=n → cociente en r0, resto en r1 | — |
| `0xffff19e2` | `isdigit` | 1 si '0'..'9' | `16d8` |

## 4. Regiones no funcionales

| Rango | Contenido |
|---|---|
| `0xffff0000`–`0xffff0020` | tabla de vectores ARM (reset → 0x58; resto → 0x20) |
| `0xffff0020`–`0xffff0058` | manejador de excepción/estacionamiento: log (5,núcleo) y error 0x1002 |
| `0xffff0058`–`0xffff00e8` | reset ARM: id de núcleo, pila (0xc002f400+0x400·núcleo), marca; núcleo 0 → main, resto espera [0xc0005000+0x1c+n] y salta a [0xc000500c+4n] |
| `0xffff00e8`–`0xffff0114` | pool de literales del arranque (+ 0x104 fmt_ext_dispatch) |
| `0xffff0e7c`–`0xffff0ec8` | cadenas «ERROR: Blinking LED…» / «ERROR: Loader boot failed...» |
| `0xffff1288`–`0xffff12b8` | cadena de versión «Musashi Loader1 Ver.01.00 Dec  2 2011 10:45:17» |
| `0xffff12c8`–`0xffff12d8` | cadena «KEY f:%x r:%x» |
| `0xffff19f0`–`0xffff1a48` | tablas de muestreo serie (perfil bit21=0 en 0x19f0, bit21=1 en 0x1a1c) |
| `0xffff1a48`–`0xffff1a80` | dígitos hexadecimales (mayúsculas y minúsculas) para fmt_hex |

Otras cadenas: `parity %x` (`0x96c`), `timer %x-%x -> %x %x` y `timeout %x` (`0x97c`/`0x994`, errores del receptor serie), `CRC %x %x %x %x` (`0xbe8`), `%02d:%02d` (`0xd3c`).

## 5. Mapa de datos (eSRAM) y códigos

| Dirección | Uso |
|---|---|
| `0xc0000000` | destino de la imagen/clave (comprobada por `check_loaded`); cabecera en `0xc0000600`; tabla de claves en `0xc0001200` |
| `0xc0005000` | bloque de control: `+0..+0xc` parámetros de la cabecera, `+0x1c+n` marca de núcleo, `+0x24` almacenamiento listo, `+0x30` consola (paso `0x10` por núcleo), `+0x0c+4n` buzón de salto |
| `0xc0006000–0xc000b000` | anillo de traza `(etapa,paso)` (puntero `0xc001000c`) |
| `0xc000b000–0xc0010000` | anillo de lecturas de bloque (puntero `0xc0010000`) |
| `0xc0010004`/`+4` | banderas (`get_flag0/1`); `0xc0010010+4` = copia de `MODEREG` bit 0 |
| `0xc0010018` | estado por sector de `read_sectors` |
| `0xc0010218` | perfil serie (R21); `0xc0010238` búfer de formato (0x40 B) |
| `0xc002f400` | base de pilas (`0x400` por núcleo); `0xc0030000` imagen Loader2 |

**Códigos de error del ROM:** `0x1001` espera de clave/ruta serie; `0x1002` excepción; `0x1003` fallo de `storage_init`; `0x1004`/`0x1005` imagen principal; `0x1006`/`0x1007` cabecera; `0x1008`/`0x1009` imagen por clave; `0x100a`/`0x100b` carga de carga útil; `0x100c`/`0x100d` receptor serie (periodo/paridad); `0x100e` temporizador; `0x2001`–`0x2005` receptor (cabecera/longitud); `0x3001`–`0x3004` sincronismo/muestreo serie (`0x3002` sin flanco, `0x3003` flanco corto, `0x3004` muestra inestable); `0x3005`/`0x3006` bloque dañado/ECC (`block_read`, tratados como éxito por `load_boot_main`, R12).

## 6. Límites

Nombres y descripciones de las rutinas son propios; el cuerpo de `serial_receiver` y `read_sectors` se verificó en R8/R20/R21, el resto por lectura directa (sin emulación individual). Códigos `0x2001`–`0x2005` y los pasos de traza no se asociaron a cada condición. No hay hardware: no se confirma el comportamiento del controlador de bloque (`0x20000`) ni el contenido de `nflasha0`.
