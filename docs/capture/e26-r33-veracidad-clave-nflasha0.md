# E26-R33 — Veracidad de «la clave de arranque serie está en `nflasha0`» (31-10-2026)

Revisa contra los bytes de `bootrom.bin` la afirmación de [R32](e26-r32-moderreg-valor-real.md) y `E26-R20-KEYTABLE`: «hay clave (inferencia fuerte), está en `nflasha0` y su valor no se conoce». Sin hardware. Test: `tests/test_e26_r33_clave_nflasha0.py`.

Etiquetas: **BINARIO** · **EMULACIÓN** (Unicorn sobre la ROM real) · **DEDUCCIÓN**.

## 1. Veredicto

| Afirmación | Veredicto |
|---|---|
| La tabla viene de `nflasha0` | **VERDADERO (BINARIO + `partinf.conf`).** `load_header` (`0x332`) lee 3 sectores de `0x600` B del **bloque 0** a `0xc0000600`; la tabla (`0xc0001200`) es el tercer sector. `nflasha0` = NAND `0x0–0x3ffff`. |
| «Hay clave» | **Matizar.** Lo demostrado es más débil: la región de la tabla **no está borrada** (al menos una palabra ≠ `0xFFFFFFFF`). Que sea una clave válida **no** se deduce. |
| El valor no se conoce | **VERDADERO.** Ningún volcado contiene el bloque 0. |

## 2. Qué comprueba realmente `find_key` (`0x39c`, BINARIO)

- Recorre `0x180` palabras (`0x600` B) desde `0xc0001200`. Si **alguna** es distinta de `0xFFFFFFFF`, copia **las dos primeras** (`[0xc0001200]`, `[0xc0001204]`, no la palabra hallada) a la pila y devuelve 0. Si todas están borradas, devuelve 1.
- Por tanto, «`find_key` = 0» solo significa «sector no borrado». Cualquier contenido sirve, incluidos ceros o datos ajenos a una clave.

## 3. Por qué el arranque normal exige ese sector no borrado (BINARIO)

Con `MODEREG` bit 0 = 1 (R32) y GPIO4.22 = 0:

1. `storage_init` y `load_header` devuelven 0 → `main` sigue (`cbz` en `0x110e` y `0x1120`).
2. `find_key` = 1 (sector borrado) → `serial_entry` (`0x1150`).
3. En `serial_entry`, sin datos serie, el receptor (`0x876`) no ve flanco → `0x3002`, que devuelve como `0x3001` (`0x910`/`0x93e`). `serial_entry` lo convierte en LED `0x1001` (`0x1008–0x101e`). Las otras salidas dependen de las banderas `[0xc0010000]`/`[0xc0010004]`, que solo escribe el receptor: o LED `0x1001`, o salto a RAM sin haber cargado nada desde la NAND.
4. `find_key` = 0 → ventana serie → `0x3001` → `load_payload` (`0x1226`) desde NAND → salto. Es el único camino de arranque desde la NAND con bit 0 = 1.

Como la cámara arranca, el sector `0xc00` del bloque 0 no está borrado. **Deducción sólida**, condicionada a que el bit 0 que lee el BootROM sea el mismo que guarda Loader3 (`0x0003`) y a que GPIO4.22 = 0.

## 4. Formato de una entrada válida (BINARIO + EMULACIÓN)

`0xc52` es CRC-32 reflejado (`0xEDB88320`, inicio `0xFFFFFFFF`, devuelve el complemento). `main` acepta la entrada si devuelve `0xFFFFFFFF` sobre los 8 bytes. Emulado: se cumple con **palabra 0 = clave**, **palabra 1 = `~crc32(clave)`** (el CRC-32 estándar sin complementar no pasa; `FF…FF` tampoco). Precisa la frase de R20 «4 B + CRC-32».

Si el sector no está borrado pero sus dos primeras palabras no cumplen ese formato, todo paquete serie bien recibido acaba en LED `0x2003`: **la vía serie quedaría cerrada sea cual sea la clave**. Con los datos actuales no se distingue entre «clave válida» y «contenido sin formato de clave».

## 5. Correcciones a otros informes

- **[R23](e26-r23-bootrom-flujo-completo.md) §1 invierte dos condiciones.** `storage_init` y `load_header` con resultado 0 **continúan**; un resultado ≠ 0 lleva a `serial_entry`. R23 escribió «si r == 0 → `serial_entry`». También coloca `find_key_entry` tras la recepción; en los bytes va antes (`0x1130`), y lo que sigue a `0x1226` es `load_payload`/`0x44e`/`0x486`.
- **R12 §3 sigue vigente** (R23 lo había corregido mal). `load_header` devuelve 0 (éxito) ante cualquier error de lectura distinto de `0x3005`/`0x3006` (`0x362–0x376`). Una cabecera dañada sigue por la ruta normal; en ese caso el contenido de `0xc0001200` no es fiable.
- [R21](e26-r21-bootrom-rx-serie.md): «`0x3002` → error fatal» ocurre solo dentro de `serial_entry`. En `main`, el receptor lo devuelve como `0x3001` y el arranque continúa.

## 6. Límites

- Polaridad y momento de muestreo del bit 0: los mismos que en R32.
- No se emuló `serial_entry` completo con todas las combinaciones de banderas; la lectura es estática.
- Reinicio en caliente con SRAM conservada (banderas y `0xc0005000` de un arranque anterior): no analizado.
- Leer el bloque 0 (lector NAND/JTAG, `E26-FISICO-BOOT` punto 2) resolvería todo de una vez: sector borrado o no, formato y valor de la clave.
