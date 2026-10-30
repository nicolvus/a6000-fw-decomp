# E26-R20-KEYTABLE — mecanismo de la tabla de clave de arranque serie

**Fecha:** 2026-10-30 · **Origen:** pendiente abierto en [R20](e26-r20-bootrom-selector.md) §5.
**Método:** BINARIO (bytes de `bootrom.bin`, desensamblado Capstone/Thumb) + comparación con
los volcados de NAND disponibles.

## 1. Resumen

La rutina `0xffff1352` (llamada desde `0x150`, a su vez desde `0x332` — «load_header» en el
mapa de R20) **no sintetiza ni deja en blanco** la tabla de clave: es un lector real de
sectores de almacenamiento de 0x600 B cada uno, con reintentos (hasta 6 por sector) y
comprobación de estado por hardware. El contenido final de la tabla depende de lo que haya
físicamente en el medio de arranque — dato que **no tenemos**, porque la partición que lo
contendría (`nflasha0`, área de boot/loader1) nunca tuvo nodo de dispositivo Linux y por tanto
nunca se volcó.

**Decisión: C** — mecanismo cerrado de forma estática; el contenido (vacía/con clave) no es
determinable con los datos disponibles. No reabre R20; cierra `E26-R20-KEYTABLE` con este límite
documentado.

## 2. Lo que hace `0xffff1352`

1. `movs r2,#0xff` + `bl 0xffff1814` (`0xffff1368`/`0xffff1372`): **memset(r4, 0xFF, count·4)**.
   `0xffff1814` es una rutina genérica de relleno de palabra (replica un byte en las 4 posiciones
   y salta a un memset de propósito general en `0xffff1926`-`0xffff199x`, compartido con el resto
   del BootROM). `r4` es un **array de estado por sector** (uno por bloque a leer), no el buffer
   de datos: se relee/compara en el bucle (`ldr r1,[r4]` en `0xffff145a`, `adds r4,r4,#4` en
   `0xffff148e`). Dejarlo en 0xFF antes de leer es la convención habitual de «aún sin leer», no
   una limpieza del contenido real.
2. Bucle principal (`0xffff1388`-`0xffff149a`): por cada sector,
   - programa un controlador de bloque mapeado en `0x20000` (comando `0x41` en el registro
     `+0x410`, dirección/dato en `+0x2b0`, bits de estado en `+0xf0`/`+0x410`/`+0x650`),
   - copia `0x180` palabras (`0x600` B) desde una FIFO en `0x10000010` al buffer **real** del
     llamador, apuntado por `r6`,
   - reintenta hasta 5 veces (`cmp r3,#5` en `0xffff1472`) si el estado indica fallo,
   - `r6 += 0x600` (`0xffff1496`, bytes `f5 06 66 c0` = `add.w r6, r6, #0x600`) y pasa al
     siguiente sector.
3. No hay ninguna escritura de 0xFF, de un patrón fijo, ni de un valor calculado en el propio
   BootROM hacia el buffer `r6`: todo lo que termina ahí viene del controlador de hardware.

Esto descarta las dos hipótesis más simples («la tabla siempre queda en 0xFF por diseño» o «el
BootROM calcula la clave internamente»): el BootROM delega por completo en el contenido del
medio físico.

## 3. Por qué no se puede resolver con los datos disponibles

- `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` es la imagen de un **paquete de
  actualización** (`EXBL`, cabecera con tamaño de bloque `0x600` en el offset `0x8`), no un
  volcado del área de boot. Su offset `0x1200` (que coincidiría con `0xc0001200` si se cargara
  linealmente en `0xc0000000`) contiene cadenas de depuración del cargador `LD3`
  (`"LD3_W:invalid address:0x%x"`, etc.), no datos de clave — más prueba de que es una etapa
  posterior, no la zona que lee `0xffff1352`.
- `analysis/camera-dumps/nand-20261020/` es un volcado real de la NAND leído en modo
  actualizador (`/dev/nflasha*`, solo lectura). Según su propio `README.md`:
  > «Sin tamaño (nodos inexistentes): `nflasha0`, `8`, `9`, `12`–`14`, `19`–`22`, `24`–`31`.»

  **`nflasha0` no existe como nodo de dispositivo Linux.** Es la convención habitual en este
  tipo de particionado Sony para la zona de boot/loader1 protegida (no expuesta al sistema de
  archivos de aplicación), que es precisamente donde `0xffff1352` leería los sectores que
  alimentan la tabla de `0xc0001200`.
- El resto de particiones volcadas (`nflasha1`–`23`) son etapas posteriores (Updater, Main,
  warm boot, rootfs, `/usr`, Android system): ninguna es candidata razonable para la zona de
  arranque de muy bajo nivel que usa este selector.

## 4. Cierre

| Hallazgo | Veredicto |
|---|---|
| ¿La rutina sintetiza/limpia la tabla? | No — solo inicializa un array de estado de 0xFF, aparte del buffer de datos. |
| ¿Lee hardware real? | Sí — controlador de bloque en `0x20000`/FIFO en `0x10000010`, sectores de `0x600` B, reintentos. |
| ¿Tenemos el sector físico que correspondería a `0xc0001200`? | No — vive en `nflasha0`, sin nodo Linux, nunca volcado. |
| ¿Vacía o con clave? | **No determinable de forma estática con los datos actuales.** |

Para cerrar el contenido (no solo el mecanismo) haría falta un volcado de bajo nivel de la zona
de boot/loader1 (fuera del alcance de `/dev/nflasha*`), que no está disponible ni se puede
obtener sin acceso físico/JTAG — fuera de alcance mientras el usuario no autorice ese paso.

## 5. Pendientes relacionados

- `E26-R20-BOOTMAIN-NIVEL`: sigue abierto (físico).
- `E26-R20-GPIO4`: sigue abierto (estático, sin relación con este hallazgo).
