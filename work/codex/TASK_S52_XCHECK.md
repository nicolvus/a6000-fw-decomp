# S52 — Validación cruzada (Codex valida a Claude)

Reglas: no aceptes la afirmación de Claude como prueba; repite cada comprobación crítica con instrucciones LLVM y bytes originales
(`work/claude/input/*.bin`, `*-view.elf`), revisa límites de funciones Thumb, saltos indirectos y llamadores reales. Puedes leer
`work/claude/s52_*.md`, `work/claude/s52_evidence.json`, `work/claude/s52/CHECKPOINT.md`. Escribe SOLO en `work/codex/`.
Salida: `work/codex/s52_crosscheck.md` con una fila por afirmación: CONFIRMADO / REFUTADO / PARCIAL / NO VERIFICABLE + evidencia
(direcciones, bytes, instrucciones) y, si discrepa de tu ronda 2, cuál es correcta y por qué. Añade al final de
`work/codex/s52/test_s52_shutmode_facts.py` las comprobaciones de lo que CONFIRMES (no rompas las existentes).

## Afirmaciones de Claude a validar (A7S salvo indicación)
1. Cadena clase → `param+9` (cierra tu B1 si se confirma): política escribe `G+0x5c` (G=`0x43f06bc8`); getter `0x43864c74` lee `G+0x5c`;
   su único llamador `0x43861bfc` copia a `0x43f04c8c`; `0x4386347a/7c` escribe el byte de `0x43f04c8c` en `r8+0x69` de un registro de
   fotograma; `0x43862158` (llamado desde `0x43b1c8e2` con `[sp]=cap+0x648`) obtiene un registro vía `0x43861f58(cap+0x1b8,cap+0x1c0)` y copia
   `+0x60..+0x6b` a `*[sp]` ⇒ `param+9 = registro+0x69 = cap+0x651`; SetExposure se invoca con `0x436f2938(img, cap+0x648)` en `0x438b77ac`
   y `0x436f2938` despacha a `vtable+0x28`. Puntos críticos: ¿es el mismo registro el que escribe `0x43863478` (r8) y el que devuelve
   `0x43861f58`? ¿hay escrituras intermedias a `cap+0x651`? `0x438b775c` fuerza `cap+0x651=0` si `0x439fb708()∈{2,3}`: confirma condición.
2. `captura+0x748` A7S ≙ `+0x740` A6000 (desplazamiento +8 desde ≈`+0x73b`); escritor único `0x43813ea2`; lectores y efectos: `0x438b1cba`
   (etapa 0xc8 omite espera CAIF 3), `0x43b1c92e` (0xc9), `0x438b726c` (ReadExecuteBase omite espera `0x800000`), `0x438b7ec2` (evento
   0x100/0x102), `0x438b8054`. A6000: 13 lectores de `+0x740` y ningún escritor directo.
3. Paquete CAIF evento 1: Silent marca bit `0x20` en `+0x12` (`0x4386329a`) y modo 2 en bits 6-7 de `+0xd` (`0x43863258`); byte +1:
   clase 0 y 3 → 2/0x42, clase 1 → 0/0x40 (`0x4386315c`); A6000 `0x4384137c` daría 0 con clase 0.
4. `0x438627d2`: clase 0 omite el envío tipo 3/`0x22` (`0x43aed4ba` → `0x437c3114`).
5. `0xf2910048`: helper GPIO genérico (~150 llamadores), no driver de cortina.
6. Darwin A7S acepta tipos de mecanismo 1/2/3 (no 4 como A6300).
7. VD_Pre A7S `0x437b65a0` guarda el tipo Silent en `0x43eaaac0` sin lectores hallados.
