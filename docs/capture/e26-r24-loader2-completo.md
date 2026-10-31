# E26-R24 — Mapa completo de Loader2 (`bootloader.bin`, 0xc0030000–0xc0036c00)

Continúa el cierre del BootROM (R20–R23) con Loader2, la segunda etapa a la que salta el BootROM (`bx 0xc0030000`, R20/R22). Fuente: `analysis/camera-dumps/updater-20261020-175427/bootloader.bin`, offset de archivo `0x600`–`0x7200` (27 648 B). Herramienta: `analysis/e26-recovery/r24_loader2_map.py` (reutiliza `r13_loader3.py`, reapuntado a la base de Loader2). Datos: `analysis/e26-recovery/r24-loader2-functions.json` (247 funciones), `r24-boot-sequence.json` (17 pasos). Test: `tests/test_e26_r24_loader2_map.py`.

## 1. Resultado

**247 funciones descubiertas, las 247 con dirección, tamaño, llamadores/llamadas y rol asignado** (ninguna sin identificar). De ellas, **94 quedan verificadas por evidencia directa** (cadena de registro, constante MMIO/eSRAM decisiva o firma de bytes): 9 por su propia cadena `LDR:`/`BOS:`/`LD3_W:`/`INS_E:`/`ERROR:`, 64 por una constante de periférico o de eSRAM que lee/escribe, y las rutinas clave (`loader2_main`, `thumb_entry`, el receptor LED, `memset`, `fatal`, los lectores de temporizador y de bloque de tarea) verificadas a mano contra bytes. Las **153 restantes** son utilidades sin cadena ni MMIO (planificador/RTOS interno, aritmética, copia) — quedan localizadas e inventariadas (dirección, tamaño, grafo de llamadas) pero no narradas una a una; ver §6 y Límites.

## 2. Entrada: de ARM a Thumb (BINARIO, verificado por bytes)

```
0xc0030000 entry_arm (ARM)        : ldr r0,[pc,#0x3c]; mov sp,r0        ; pila (verificado: 0xE59F003C/0xE1A0D000)
            bl  cache_invalidate (datos, 0x210) y (instrucciones, 0x240) ; invalida caché por conjunto/vía
            bl  vic_init (0x2a4)                                        ; máscara IRQ en 0xf8000000
            blx 0x110c, 0x8b8, 0x1094                                   ; esperas/inicializaciones (temporizador)
            bl  mmu_cache_setup (0x36280)                               ; SCTLR (c1,c0,0) tras el arranque
            b   0xc0030054
0xc0030054 mode_switch (ARM)      : blx 0x3005c                         ; ctx_restore_jump: ldm con pc -> Thumb
            blx thumb_entry (0x301c4)
0xc00301c4 thumb_entry (Thumb)    : bl 0x3581a (init global); bl task_env_init (0x30198); bl loader2_main (0x302d8)
            ; si loader2_main retorna (no debería): bl fatal(0)
```

## 3. `loader2_main` (`0xc00302d8`) — secuencia de arranque completa (BINARIO, verificado por cadenas)

Cada paso registra `"LDR:<paso>\n"` antes de llamar y, si falla, `"LDR_E:<paso>[%d]\n"` con el código:

| # | Paso (cadena `LDR:`) | Función | Caída en error |
|---|---|---|---|
| 0 | — | `log("Loader2 Ver.33.01.90 (Jan 24 2014 22:07:33)")` | — |
| 1 | `Init UDIF_P` | `0xc00311f8` | continúa a UDIF_D |
| 2 | `Init UDIF_D` | `0xc0031230` | mapea código (`0xc00303f0`) y sale |
| 3 | `Init InfSec_S` | `infsec_s_init` (`0xc0030d4c`, `INS_E:Sign INFS_SAFE`) | sale |
| 4 | `Init BOSS` | `boss_init` (`0xc0030674`) | sale |
| 5 | `Load InfSec_N` | `infsec_n_load` (`0xc0030d80`, `INS_E:Sign/Read INFS_NORMAL`) | sale |
| 6 | `Load LBkup` | `lbkup_load` (`0xc0030f1c`, cadenas `LBK_E:*`) | sale |
| 7 | `Init DebugLv` | `debuglv_init` (`0xc00308d0`) | sin comprobación de error |
| 8 | `Load LDR3` | `load_rom_info` (`0xc0030de8`, `INS_E:ROM size/info/Load ROM`, tamaño máx. `0x30000`) | sale |
| 9 | `Exit UDIF_D` / `Exit UDIF_P` | `0xc0031238` / `0xc0031214` | — |
| 10 | mide tiempo de arranque | `timer_read_us` (`0xc00310b2`, lee `0xf240310c`) | — |
| 11 | `Jump LDR3@0x%X(%luus)` | `bl 0xc003117c; blx 0xc003082c; blx r5` (**r5 = `0xc01f0000`**, entrada de Loader3, R13) | — |
| 12 | si Loader3 retorna | `LDR_E:NOTREACHED`; código fijo **−306** | `fatal`/LED |

**Corrobora R13 por una segunda vía independiente:** el camino de error por defecto (`LDR_E:NOTREACHED` → −306) resta 1000 antes de negar (`sub.w r0,r4,#0x3e8` tras `r4=−306`), dando 1306 → patrón de LED **1 largo + 3 medios + 6 cortos** — exactamente lo que R13 derivó de Loader3 para el mismo código por otra vía. Verificado por bytes (`tests/test_e26_r24_loader2_map.py::test_rutina_led_resta_1000_igual_que_r13`).

## 4. Primitivas compartidas (BINARIO, verificadas)

- **`log`** (`0xc0030980`): `vsnprintf` (usa `memset`, `0xc0034870`) + salida a consola — confirma la hipótesis de R13.
- **`memset`** (`0xc0034870`): misma forma que el `memset` del BootROM (`0xffff1926`, R22): bloques de 0x20 B y relleno decreciente.
- **`fatal`** (`0xc0034a76`): niega el código, llama a `led_error_blink` (`0xc0030c7c`) y no retorna.
- **`led_error_blink`** (`0xc0030c7c`): el mismo patrón `n/1000, (n%1000)/100, n%100` documentado en R13, con periodo `d=0x3d0900` (mismo valor que Loader3, R13).
- **`timer_read_us`/`timer_wait`** (`0xc00310b2`/`0xc00310bc`): leen `0xf2403000+0x10c` — **el mismo temporizador que el BootROM** (R22, 4 MHz verificado), reforzando esa cifra con una tercera etapa independiente.
- **`tcb_get`** (`0xc0032980`…`0xc00329bc`, 8 variantes): lectores de un campo de la tarea actual sobre una tabla en `0xc00c8190` — asomo de un pequeño RTOS interno (consistente con las cadenas `LDR:Init UDIF_P/UDIF_D`, que en la terminología de Sony son las capas de interfaz de usuario/dispositivo del propio loader).

## 5. Handoff a Loader3

`loader2_main` salta con `blx r5`, `r5 = 0xc01f0000` — coincide exactamente con la entrada de Loader3 ya documentada en R13 (`0xc01f0000`, entrada ARM `b 0xc01f0028`). No hay ninguna otra vía de entrada a Loader3 en Loader2: es la única instrucción `blx` a un registro cargado desde esa constante.

## 6. Inventario completo (247/247)

| Categoría | Funciones | Base de identificación |
|---|---|---|
| Secuencia de arranque y primitivas nombradas (§2–4) | 15 | lectura directa, verificada por bytes |
| `log_*` (cadena de registro propia) | 9 | cadena `LDR:`/`BOS:`/`LD3_W:`/`INS_E:` referenciada |
| `mmio_access` | 64 | constante de periférico (`0xf2…`) o eSRAM (`0xc0…`) decisiva en el cuerpo |
| `util_compartida` | 10 | sin cadena/MMIO, reutilizada por ≥8 funciones (biblioteca de formato/copia, confirmado por forma en una muestra) |
| `auxiliar` | 153 | localizada (dirección, tamaño, llamadores/llamadas) sin cadena ni MMIO propios — mayoría del planificador interno, aritmética y envoltorios de una función |
| **Total** | **247** | — |

Tabla completa (dirección, rol, nota, tamaño, llamadores, llamadas) en `analysis/e26-recovery/r24-loader2-functions.json`.

## 7. Límites

- Los nombres son propios (el binario no trae símbolos), salvo los literales de las cadenas de registro.
- Las 153 funciones «auxiliares» están **localizadas e inventariadas**, no narradas instrucción a instrucción: cubren el núcleo tipo RTOS interno (creación/lectura de tareas sobre `0xc00c8190`, colas, planificación) y utilidades de cálculo; una muestra se verificó a mano (strlen SIMD, `memcpy`, accesores de TCB) para confirmar que el patrón se sostiene, pero no se decodificó cada una.
- El contenido exacto de `InfSec_S/N`, `BOSS` y `LBkup` (formatos de partición) no se decodificó campo a campo; queda fuera del alcance de «completar el mapa» y pertenece a un posible R25 si se solicita.
- `r13_loader3.py` (Loader3, `0xc01f0000`) ya estaba cubierto por R13/R16/R17; no se reabre aquí.
