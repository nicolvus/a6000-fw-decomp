# E26-R25 — Mapa completo de Loader3 (`bootloader.bin`, 0xc01f0000–0xc0205800)

Cierra el mapa de la cadena de arranque (BootROM R20–R23, Loader2 R24) con Loader3: la etapa a la que Loader2 salta (`blx r5=0xc01f0000`, R24). Fuente: `analysis/camera-dumps/updater-20261020-175427/bootloader.bin`, prefijo INFO 5 (offset de archivo `0x22800`–`0x38000`, 43 páginas; INFO 6, 21 páginas adicionales, **no adquirida** — límite ya documentado en R5/R13). Herramienta: `analysis/e26-recovery/r25_loader3_map.py` (misma metodología que R24, reapuntada a `r13_loader3.py`). Datos: `analysis/e26-recovery/r25-loader3-functions.json` (674 funciones), `r25-boot-sequence.json`. Test: `tests/test_e26_r25_loader3_map.py`.

## 1. Resultado

**674 funciones descubiertas, las 674 con dirección, tamaño, llamadores/llamadas y rol asignado.** De ellas, **418 (62 %) con evidencia directa**: 30 por cadena de registro propia (`LD3:`/`LD3_E:`/`LD3_W:`/`BOS_E:`/`CFG_E:`/`FAT_E:`/`LBK_E:`/`INS_E:`), 354 por una constante MMIO/eSRAM decisiva, 19 utilidades muy reutilizadas sin cadena, y las rutinas clave verificadas a mano por bytes (vectores de excepción, entrada ARM, despachador, LED). Las **256 restantes** son auxiliares sin cadena ni MMIO, inventariadas pero no narradas una a una (mismo criterio que R24 §6).

## 2. Entrada: vectores de excepción y arranque ARM (BINARIO, verificado por bytes)

```
0xc01f0000 exc_vectors (ARM)  : b 0xc01f0028 (reset)                 ; verificado: 0xEA000008
                                 b 0xc01f0020 ×7 (el resto de vectores) ; verificado: 0xEA000005
0xc01f0020 exc_handler        : carga un código y llama DIRECTAMENTE a led_error_blink (blx 0xc01f3b74)
                                 — una excepción real (no solo un error de arranque) también parpadea el LED
0xc01f0028 entry_arm          : ldr r0,[pc,#0x30]; mov sp,r0 ; bl 0xc020e090; bl 0xc020e024 ; b 0xc01f0070
0xc01f0070 mode_switch (ARM)  : blx 0xc01f0078 (ctx_restore_jump: ldm con pc -> Thumb)
                                 blx thumb_entry (0xc01f01e0)
0xc01f01e0 thumb_entry        : bl 0xc020d50e ; bl boot_dispatch (0xc01f11ec)
```

**Hallazgo nuevo respecto a R13:** los vectores de excepción (`0xc01f0004`–`0xc01f001c`: undef, SWI, abort de prefetch/datos, reservado, IRQ, FIQ) no tienen manejadores separados — todos caen en el mismo `exc_handler` (`0xc01f0020`), que llama al LED **sin pasar por `boot_dispatch`**. Es la misma forma que el BootROM (R22: manejador de excepción único) y confirma que el patrón «toda excepción → parpadeo de LED, sin registro ni recuperación» se repite en las tres etapas (BootROM, Loader2 no se comprobó para esto, Loader3).

## 3. `boot_dispatch` (`0xc01f11ec`) — confirmación de R13, sin cambios

Ya documentado en R13 §3: despacha según el modo de arranque; cualquier retorno distinto de 0 de inicialización, selección de modo o las tres rutas de carga cae en `0xc01f1262 → led_error_blink`. R25 no reabre esa rama (cubierta y verificada en R13); añade que el **propio despachador** (`0xc01f01e0 → 0xc01f11ec`) y sus 30 funciones con cadena de registro (`LD3:`/`LD3_E:`) quedan localizadas en el mapa completo, incluidas rutas no citadas antes: `LD3:Set SELFREF`/`Set DPD` (energía de la DRAM), `LD3:<< KEY E:… >>` (clave de arranque — candidato a resolver `E26-R20-KEYTABLE` por el lado de Loader3; no explorado, ver Límites), `LD3:Load vmlinux/initrd`, `LD3:read MISCREG`.

## 4. Capas ya cubiertas por R13/R15/R16, ahora localizadas en el mapa

| Capa | Función | Fuente previa |
|---|---|---|
| LED de error | `led_error_blink` (`0xc01f3b74`) | R13 |
| Tabla de particiones BOS | `bos_load`/`bos_read` (`0xc01f2c98`/`0xc01f2b7c`) | R13 P1 |
| Carga de archivos RAMCFG | `cfg_load_file` (`0xc01f2f24`) | R13 P2 |
| FAT (ID, PBR, montaje, cluster, tipo, carga) | 6 funciones (`0xc01f3d8a`…`0xc01f4654`) | R13 P3–P7 |
| Decisión de omitir RAMCFG | `ramcfg_skip_decide` (`0xc01f2282`) | R15 §10 |
| Lector TPZL (residuo de 256 B) | `tpzl_block_read`/`tpzl_toc_lookup` (`0xc01fdd8e`/`0xc01fe006`) | R15/R16 |
| Temporizador (misma familia que BootROM/Loader2) | `wait_timer` (`0xc01f4f88`) | R13 §8 (ahora con dirección fija en el mapa) |
| `log`/consola | `0xc01f3670` | nuevo en R25 — misma forma que `log` de Loader2 (R24 §4), refuerza que las tres etapas comparten una biblioteca común |

## 5. Inventario completo (674/674)

| Categoría | Funciones | Base de identificación |
|---|---|---|
| Entrada/despacho/LED/capas confirmadas (§2–4) | 21 | lectura directa o informes previos, verificadas por bytes |
| `log_*` (cadena de registro propia) | 30 | cadena `LD3:`/`LD3_E:`/`LD3_W:`/`BOS_E:`/`CFG_E:`/`FAT_E:`/`LBK_E:`/`INS_E:` |
| `mmio_access` | 354 | constante de periférico o eSRAM decisiva |
| `util_compartida` | 19 | sin cadena/MMIO, reutilizada por ≥8 funciones |
| `auxiliar` | 256 | localizada (dirección, tamaño, grafo de llamadas), sin cadena ni MMIO propios |
| **Total** | **674** | — |

Tabla completa en `analysis/e26-recovery/r25-loader3-functions.json`.

## 6. Límites

- Nombres propios salvo cadenas literales del binario.
- INFO 6 (21 páginas) no está adquirida: el mapa cubre solo el prefijo INFO 5 ya documentado como límite en R5/R13.
- Las 256 funciones «auxiliares» están localizadas, no narradas una a una (mismo criterio que R24).
- La cadena `LD3:<< KEY E:0x%X L:0x%X D:0x%X >>` (`0xc01f0590`) es una vía no explorada para `E26-R20-KEYTABLE` (la tabla de clave del BootROM); queda fuera de alcance de este informe — candidato a un R26 si se solicita.
- No se decodificó el formato exacto de BOS/RAMCFG/FAT campo a campo (mismo límite que R24 §7 para Loader2).
