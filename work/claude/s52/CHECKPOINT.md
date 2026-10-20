# S52 Agente A — checkpoint (cerrado 19-10-2026)

Estado: entregables completos; REA propia cerrada (`--shutdown`, solo queda el daemon de Codex). Test 14/14.

## Analizado (no repetir)
- `cap+0x748` A7S = `cap+0x740` A6000 (+8). Único escritor `0x43813ea2`. Lectores A7S y homólogos: tabla en `s52_silent_flag_consumers.md`.
- Nuevos por Silent: `0x438b1cba` (0xc8), `0x43b1c92e` (0xc9), `0x438b726c` (ReadExecuteBase), `0x438b7ec2`, `0x438b8054`.
- Paquete CAIF ev1 `0x43862e24`: `+0x12` bit5, `+0xd` modo 2, byte `+1` clase 0=3.
- Política `0x438649bc`, G=`0x43f06bc8`; clase→`0x43f04c8c`→consumidores `0x438627d2`, `0x43863146`, `0x4386347a`; copia `0x43862158`→`param+9`.
- CAIF: emisor `0x4379b590`, receptor `0x4379b6ac`, helpers `0x438be16c..0x438be980`; ev3=tag 0x12 `0x436d82e4`.
- GPIO `0x43b585aa/0x43b585b6`→`0x4397d4c0` (= A6000 `0x43b5e2a4/0x43b5e2b0`→`0x4398f9a4`).
- Darwin A7S selector `0x216e8` (1/2/3).
- VD: cadenas→funciones A7S; VD_Pre `0x437b65a0` guarda tipo en `0x43eaaac0`.

## Callejones sin salida
- Buscar `ldrb #0x12`+`tst #0x20` en las 3 ROM Darwin: nada (el parser usa otra forma o copia a estructura).
- Lectores de `0x43eaaac0`: REA vacío, barrido PIC vacío.
- REA no recupera `0x43b1c920`, `0x43b1d648`, `0x43b1e3e4` como procedimientos (sin llamadores); usar `pcrel_scan` para punteros Thumb (`+1`).
- `ctx.py` recarga el .dis completo: lento en bucles (usar awk por rango).

## Siguiente
1. Parser CAIF en `darwin_core.bin` A7S: localizar receptor serie (Cortex-M, base 0x4200) y buscar el uso de `+0x12`/`+0xd`.
2. Tarea CA A7S: homólogo de `0x436bc140/0x436b93b0` y banco/bit del tag 0x12.
3. Constructor de `captura` (inicialización de `+0x748`).

## Fase C (validación de Codex) — cerrada
- `s52_crosscheck_claude.md`, `tests/test_s52_xcheck.py` (7/7), arnés `s52/xcheck_emu.py` (entrada real de SetExposure).
- Corrección propia: `cfg2+4 |= 8` (IMX235) es común a ShutMode 0/1/3/4, no exclusivo de la clase 0.
