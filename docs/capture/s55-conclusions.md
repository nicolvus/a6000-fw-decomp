# S55 — Conclusiones (20-10-2026)

Pruebas: `python3 -m unittest tests.test_s55_bionz_sync` → 16/16 OK (≈65 s). Matriz: [`analysis/s55-evidence-matrix.json`](../../analysis/s55-evidence-matrix.json).
Informes: [GPIO diferencial](s55-bionz-gpio-comparison.md) · [inicialización](s55-gpio-initialization-trace.md) · [SENS_B](s55-sens-b-controller.md) · [eventos](s55-exposure-event-trace.md) · [IMX210](s55-imx210-electronic-integration.md).
SHA: `av-cam` A6000/A7S y BK4 verificados; binarios originales sin tocar; REA cerrada (sesión única).

## Resumen ejecutivo
La frontera de S54 («pares canal/bit inyectados por el entorno») queda resuelta: son el contenido de la **base de backup** `0110_backup/*/CX77500_*.bin` leída con `Backup_read_4Byte`
y volcada a las celdas `0x43e77298…` por el inicializador `0x436bcef4` (A7S `0x436dc054`). Con ello los cinco lectores de la tarea CA son (3,17), (10,3), (0,12), (0,7), (5,14), todos
líneas de handshake SIO (banco 0 = `GPIO_S`: (0,7)=CA_RELEASE_LOCK, (0,12)=DWN_CSREQ). A7S y A6000 usan **exactamente** la misma infraestructura de pines. Ningún lector corresponde a `GPIO_9`
(INFERENCIA) y no se encontró consumidor de `SENS_B`. Respuesta a la pregunta principal: **BIONZ no consume `CA_1ST_CURTAIN_START` en ninguna ruta GPIO recuperada**; si la consume, es por
`SENS_B` (bloque dedicado, sin rastro) o no la consume y es solo vigilancia.

## Descubrimientos nuevos (VERIFICADO salvo nota)
1. Servicio `+0x2e0` = `Backup_read_4Byte`; IDs `0xf9xxxx` = base de pines del producto (formato BK4 reconstruido de `backup.ko`).
2. Escritor de las variables de pin = `0x436bcef4`/`0x436dc054` (**corrige S54**: sí existe; el store es vía GOT).
3. Mapa parcial pin↔esquema: banco 0 = `GPIO_S_n` (nfc.ko + esquema; PARCIAL).
4. Diferencia GPIO A7S/A6000: un único `set` extra de A7S, no-op en el preset oficial. Misma estructura de 14 consumidores.
5. BIONZ conmuta salidas (7,15)/(7,13) en eventos de lectura de imagen; `ExposureEndNotify`/`ExpStartComp` no leen GPIO.

## Comparación con S54
S54: «consumidor de P4C NO localizado; pares sin inicializar». S55: pares y escritor localizados; consumidores de pines enumerados y descartados como P4C (con la salvedad del banco GPIO_n);
S54 H54-4 (recepción equivalente) pasa a **PARCIAL fuerte**: la infraestructura es idéntica; no se comparó SENS_B. IMX210 sin avance.

## Hipótesis
| H | Estado | Evidencia / límite | Próxima comprobación |
|---|---|---|---|
| H55-1 variables configuradas dinámicamente | **VERIFICADO** (matiz: desde la base BK4, no módulo de arranque) | `0x436bcef4`, test PinDatabase | valores por unidad `Backup.bak` |
| H55-2 un lector de la tarea CA es GPIO_9/P4C | **DESCARTADO en lo recuperado / INFERENCIA** | lectores = SIO handshake; ningún bit 9 fuera del banco 0 | banco de `GPIO_n` (TRM) |
| H55-3 SENS_B con controlador especializado | **NO VERIFICADO** | sin cadenas ni bloque | traza lógica + registros f2a1/f2400 |
| H55-4 A7S usa configuración/consumidor distinto | **DESCARTADO** (para tarea de pines y primitivas); NO VERIFICADO para SENS_B | 14 funciones 1:1, valores idénticos | SENS_B A7S vs A6000 |
| H55-5 P4C participa en sincronización del sensor | **NO VERIFICADO** | sin lector; VD/DFE solo reciben interrupciones propias | traza pasiva P4C vs VD |
| H55-6 ExpStartComp/ExposureEndNotify ≈ P4C | **NO VERIFICADO**, sin soporte | handlers sin GPIO | orden entre tareas OSAL |
| H55-7 IMX210 con fin electrónico fotográfico | **NO VERIFICADO** | sin evidencia nueva | datasheet/traza CIS |
| H55-8 Darwin tipo 0 insuficiente por sí solo | **INFERENCIA fuerte** (S52/S53/S54 + S55: la señal de pines es idéntica en ambas, no es lo que falta) | falta LIRO + sensor | — |

## Bloqueantes
1. Banco/numeración de los `GPIO_n` y registro de `SENS_B` (SoC TRM o medición). 2. Valores por unidad de la base (`Backup.bak`). 3. Semántica eléctrica del sensor (datasheet/traza CIS).
4. Escritor del byte de tipo de mecanismo en Darwin (S54).

## Viabilidad y S51
**S51 se mantiene (NO PARCHEAR NI FLASHEAR).** S55 reduce un bloqueante (origen de pines) y elimina una vía de hipótesis (consumidor GPIO exclusivo de A7S), pero no aporta evidencia a favor de un cierre electrónico en IMX210.

## Siguiente experimento prioritario
**Pasivo (autorización específica pendiente):** analizador lógico de ≥100 MHz en `GPIO_9`/P4C (CN4900), `MSS_SO_DWN`, VD y `CIS0_XCS/SCK` durante una foto mecánica y una EFCS: confirma polaridad/flanco de P4C y si coincide con VD o con comandos CIS.
**Estático:** localizar el bloque de `SENS_B` desde los escritores de `0xf2a10000–0xf2a30000`; resolver los IDs dinámicos de `0x43716dd0`.
