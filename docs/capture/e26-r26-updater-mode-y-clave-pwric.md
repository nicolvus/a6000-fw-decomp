# E26-R26 — Mecanismo de `updater\mode` y descarte de la clave `LD3:<<KEY…>>` (30-10-2026)

Cierra dos pendientes estáticos usando el mapa completo de Loader3 (R25) como base. Fuente: `analysis/camera-dumps/updater-20261020-175427/bootloader.bin`. Test: `tests/test_e26_r26_updater_mode.py`.

## 1. `E26-R7-C-UPDATER-MODE` — CERRADO PARCIAL (mecanismo de lectura identificado; productor pre-Linux sigue sin aparecer)

### 1.1 `boot_dispatch` indexa por un valor 0–14 en RAM (BINARIO, verificado por bytes)

`boot_dispatch` (`0xc01f11ec`) llama a `c01f2156` (`return *(int*)0xc00e0004`) y salta por tabla (`tbb`, instrucción `0xe8df 0xf000` en `0xc01f1220`; tabla de 15 bytes en `0xc01f1224`: `24 08 08 08 08 08 08 13 13 13 08 08 08 13 13`):

| Valor | Destino | Rama |
|---|---|---|
| 0 | `0xc01f126c` | inválido → log + LED |
| 1,2,3,4,5,6,10,11,12 | `0xc01f1234` | cadena normal: `c01f1312` (Normal load) → `c01f04b6` → `c01f03e2` |
| 7,8,9,13,14 | `0xc01f124a` | **salto directo a `c01f03e2`** (coincide con la nota de R16 §«rama modos 7–9, 13, 14») |

### 1.2 El archivo `\updater\mode` sí se comprueba y su ausencia fuerza la cadena normal (BINARIO, verificado por bytes)

La cadena está en `0xc01f19a4` (`\updater\mode`, referenciada por `adr r0,#0x3e8` en `0xc01f15ba`). La función `c01f159a` («`BOM:chk updater`») monta el dispositivo **2** (`fat_mount`, `c01f3eb6`) y busca ese archivo con `c01f44c6`; devuelve 1 si existe.

`c01f1de6` (la función de ~880 B que determina el modo, ya citada en R13) llama a `c01f159a` **dos veces**:

1. `0xc01f1df0: bl c01f50f4; cmp r0,#2` (verificado `0xf003 0xf980`) — bajo una condición concreta (resultado de `c01f50f4` = 2), llama a `c01f159a` (`0xc01f1df8`, verificado `0xf7ff 0xfbcf`); si el archivo **no existe** (`cmp r0,#0` en `0xc01f1dfc`, verificado `0x2800`; `beq 0xc01f1eec`, verificado `0xd075`), sale por una vía de salida temprana.
2. Tras leer un candidato de modo de Backup (`c01f498c`), vuelve a llamar a `c01f159a` (`0xc01f1e10`, verificado `0xf7ff 0xfbc3`): si el archivo **no existe** (`cbz r0,#0xc01f1e1a` en `0xc01f1e14`, verificado `0xb108`), **fuerza `r0=3`** (verificado `0x2003` en `0xc01f1e16`) y salta a `0xc01f212c` — **el modo 3 cae en la cadena normal (§1.1), no en la especial**.

**Conclusión verificada:** la presencia de `\updater\mode` en el dispositivo 2 (FAT) es una condición necesaria que `c01f1de6` exige al menos en dos puntos antes de poder entrar en la cadena especial (7–9/13/14); su ausencia fuerza la cadena normal. `c01f1544` (llamado después, dentro de la misma función) persiste el valor final en Backup y refresca `[0xc00e0004]` — es quien **escribe**, no quien decide.

### 1.3 Lo que queda sin trazar

El resto de `c01f1de6` (ramas `c01f1d6a`, `c01f1c70`, varias lecturas de Backup con `c01f498c`) decide el valor exacto final (cuál de 7/8/9/13/14, o cuál de 1–6/10–12) y no se trazó por completo: función grande, con más de 20 saltos condicionales. **Ningún productor pre-Linux del archivo `\updater\mode` en el dispositivo 2** aparece en el prefijo de Loader3 (coincide con la conclusión original de R7). Dispositivo 2 = `nflasha2` por el patrón ya establecido en R7 (dispositivo N ↔ `nflashaN`); no reverificado aquí contra la tabla de particiones BOS.

### 1.4 Efecto práctico

No cambia la conclusión de R7: aunque ahora se sabe exactamente qué archivo (`\updater\mode`) y qué dispositivo (2, `nflasha2`) activan la cadena especial, escribirlo exige el mismo acceso físico a NAND que `E26-FISICO-BOOT`. UPDATER sigue sin ser un entorno de recuperación independiente (carga el mismo kernel que COLD, solo que desde `nflasha1`).

## 2. `LD3:<<KEY E:… L:… D:… >>` — DESCARTADA como vía de `E26-R20-KEYTABLE`

La cadena en `0xc01f0590` (hallada al mapear R25) **no es la tabla de clave de arranque serie del BootROM** (`0xc0001200`). Es la lectura de la clave de autenticación de la **batería** (PwrIC):

1. Solo se llama con `r0` = tipo de PwrIC (verificado `cmp r0,#3`, bytes `0x2803` en `0xc01f0594`), gateada por `c01f5ba6`, que lee `[0xc00e0060+0x34]` (tipo de PwrIC) y exige valor `7`.
2. Construye tres campos `E`(4B)/`L`(4B)/`D`(1B), los pone a `0xFF` si falla la lectura, y los registra con `LD3:<<KEY E:0x%X L:0x%X D:0x%X>>`.
3. La función hermana `c01f54f0` despacha por el mismo campo `[0xc00e0060+0x34]` con las cadenas `"PWR:inv PwrIC"` y rutinas de energía/batería — vocabulario ajeno al almacenamiento o al arranque serie.

**Conclusión:** descartada. `E26-R20-KEYTABLE` permanece cerrado con el límite ya documentado (contenido de `nflasha0` no determinable sin acceso físico).

## 3. Límites

- `E26-R7-C-UPDATER-MODE` queda **CERRADO PARCIAL**: se identificó el mecanismo de lectura (archivo + gate), no el cálculo completo del valor final ni ningún productor pre-Linux.
- Dispositivo 2 = `nflasha2` es una inferencia por patrón, no reverificada contra la tabla BOS en esta pasada.
- El valor real del elemento Backup persistido en esta cámara no se leyó de las copias de NVRAM del repo (posible trabajo futuro con `r14_backup.py`, que mirror aún no cubre este accesor «de elemento plano» usado por `c01f4aa0`/`c01f498c`, distinto del esquema grupo/ítem BK4 que sí mirror).
