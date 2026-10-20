# S52 — A7S 3.20: traza del control de cortinas en Silent (consolidado, 19-10-2026)

Fuente primaria: Agente A (Claude) [`work/claude/s52_curtain_control_trace.md`](../../work/claude/s52_curtain_control_trace.md),
[`s52_silent_flag_consumers.md`](../../work/claude/s52_silent_flag_consumers.md), validado por Agente B (Codex)
[`work/codex/s52_crosscheck.md`](../../work/codex/s52_crosscheck.md). Solo estático. Tests: `work/claude/tests/test_s52_curtain_facts.py` (14/14).

## Arquitectura

LIRO (`av-cam.bin`) no acciona las cortinas: habla con el MCU de obturador (ROM `darwin_core.bin` propia en A7S) por **CAIF**.
Emisor `0x4379b590(ev,…)`: ev1 → `0x436d8354` copia el paquete de **22 B** `captura+0x4ae8 → +0x40`; ev3 → `0x436d82e4` (tag `0x12`).
Receptor de respuestas `0x4379b6ac`. El tag `0x12` termina, en A6000, en un helper GPIO genérico (`0xf2910048+banco*0x100`);
sus homólogos A7S `0x43b585aa/0x43b585b6 → 0x4397d4c0` son idénticos en bytes (CONFIRMADO por Codex; «~150 llamadores» no reproducido).
Darwin A7S `0x216e8` acepta tipos de mecanismo 1/2/3 como A6000 `0x20c74` (A6300 añade 4) — CONFIRMADO por ambos.

## `captura+0x748` (P1)

**VERIFICADO:** es el mismo campo que A6000 `captura+0x740` (estructura desplazada +8 desde ≈`+0x73b`, secuencias de instrucciones
idénticas). Escritor A7S único hallado `0x43813ea2` (`=1` si tipo Silent `cap+0x78c==2`; bytes `8af7b6fe0228c4f88c0702d10123c4f8`, CONFIRMADO).
A6000: lectores de `+0x740` existentes, ningún escritor directo hallado (recuento exhaustivo no reproducido por Codex: PARCIAL).
Inicialización del campo: NO VERIFICADO.

## Prueba central: clase vs tipo Silent

En A7S Silent produce a la vez **clase 0** (`G+0x5c`, `G=0x43f06bc8`, política `0x438649bc`) y **tipo 2** (`cap+0x78c`, bandera `cap+0x748`).

| # | Depende de | Función | Silent / clase 0 | Normal / clase 1-3 | Validación B |
|---|---|---|---|---|---|
| C1 | clase | `0x438627d2` | **omite** `0x43aed4ba → 0x437c3114` (mensaje tipo 3/`0x22` a cola OSAL; receptor NO VERIFICADO) | lo envía (clase 1, o 3 con `*0x43faba61==1`) | CONFIRMADO |
| C2 | clase | `0x4386315c..74` byte +1 del paquete ev1 | 2/`0x42` (**igual que clase 3**) | clase 1 → 0/`0x40` | CONFIRMADO; A6000 `0x4384137c` daría 0 |
| C3 | clase | `0x43862158 → param+9 → SetExposure` | ShutMode 0 | ShutMode 1/3 | ver [propagación](s52-shutmode-propagation.md) |
| S1 | tipo | `0x4386329a..b4` | `pkt[+0x12] |= 0x20` | bit 5 = 0 | CONFIRMADO; A6000 no lo tiene |
| S2 | tipo | `0x43863258` | `pkt[+0xd]` bits 6-7 = 2 | 2 solo con modo `0x19` | CONFIRMADO |
| S3 | `+0x748` | etapa `0xc8` `0x438b1cba` | **no espera** respuesta CAIF 3 (`0x438be5f8`) | espera | PARCIAL (instr. vistas) |
| S4 | `+0x748` | etapa `0xc9` `0x43b1c92e` | espera CAIF 3 antes de CAIF 5 | solo CAIF 5 | PARCIAL |
| S5 | `+0x748` | ReadExecuteBase `0x438b726c` | **no espera** bandera `0x800000` (puesta por callback CAIF `0x43b1e3e4`) | espera | PARCIAL |
| S6 | `+0x748` | `0x438b7ec2` | evento `0x100` | `0x102` posible | PARCIAL |
| S7 | `+0x748` | `0x438b8054` / `0x438b7fce` | omite `post(2,1)` y ops del imager; temporizador `0xffffffff` + callback `0x43b1d5b1` | tiempo calculado + callback `0x43b1d649` | PARCIAL |

No cambia con Silent: la bandera de comunicación CA `cap+0x757`; ningún emisor CAIF (`0x438be16c…0x438be980`) está guardado por
`+0x748`/`+0x78c` (barrido `s52/guards.py`, cobertura del desensamblado lineal).

## Respuesta P2 (cómo evita la A7S la 2ª cortina)

1. **VERIFICADO:** LIRO **no suprime** comandos de cortina: envía igual el evento 1, pero con Silent **marcado en el paquete** (S1/S2) y
   byte de clase = 3 (C2).
2. **VERIFICADO:** LIRO deja de **esperar** las respuestas del mecanismo que sincronizan la toma normal (S3, S5) y reordena la espera
   CAIF 3 (S4); programa el sensor con drive_mode `0x4e/0x4f` y ShutMode 0.
3. **INFERENCIA fuerte:** la decisión de no mover las cortinas la toma el MCU de obturador al leer la marca del paquete.
4. **NO VERIFICADO:** consumidor del bit `0x20`/modo 2 en `darwin_core.bin` (parser CAIF de Darwin nunca localizado en ninguna ROM),
   tarea CA A7S (tag `0x12`), pin GPIO→Darwin, receptor del mensaje C1, efecto en las bobinas `1ST/2ND_CURTAIN_MG`.

Selección de modo (`0x4e/0x4f`) y control de cortinas son ramas **paralelas** derivadas del mismo `cap+0x78c`; no se halló punto en que
drive_mode influya en el paquete CAIF o en S3–S7 (Claude, fase C; PARCIAL: no se recorrieron todas las llamadas del constructor del paquete).

## Motor VD (A4, acotado)

Equivalentes A7S localizados por cadena: `VD_Pre` `0x437b65a0`, `VD_Seq` ref `0x437b524a`, `VD_Drive` ref `0x437b33f0`, `EC_VD_Post`
ref `0x437b37a4`, `int_LM_Send1st_Handler` ref `0x437b631e`. `VD_Pre` llama al conversor y guarda el tipo en `0x43eaaac0` (CONFIRMADO);
lectores: ninguno hallado (NO VERIFICABLE). Sin acceso de VD_Drive/Seq/Post a `+0x748/+0x78c` ni a las copias de clase (búsqueda no exhaustiva).
Detalle: [`work/claude/s52_vd_sequence_comparison.md`](../../work/claude/s52_vd_sequence_comparison.md).

## Mapa MMIO

[`work/claude/s52_mmio_curtain_map.csv`](../../work/claude/s52_mmio_curtain_map.csv). Única escritura física cercana: helper GPIO genérico
`0xf2910048` — no identificado como driver de cortina. Ninguna escritura MMIO difiere entre clase 0 y 1/3 dentro de la cobertura.
