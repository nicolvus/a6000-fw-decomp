# S384 — Búsqueda del ID de cola `0x40193` (C2 receptor) en ARM y Thumb

## 1. Patrones buscados en libObj.so (A6000 fw3.21, A7S fw3.20, A6300 fw2.01)

| Patrón | Encoding | A6000 | A7S | A6300 |
|---|---|---|---|---|
| Word LE 0x00040193 | `93 01 04 00` | 9 sitios* | 11 sitios* | 12 sitios* |
| Half LE 0x0193 | `93 01` | 2840 sitios | 2418 sitios | 2827 sitios |
| Thumb movw #0x0193 | `?? F2 93 F9` | 0 sitios | 0 sitios | 0 sitios |
| Thumb movt #0x0040 | `?? C2 40 F8` | 0 sitios | 0 sitios | 1 sitio |
| ARM movw #0x0193 | `93 01 00 E3` | 0 sitios | 0 sitios | 0 sitios |
| ARM movt #0x0040 | `40 00 40 E3` | 0 sitios | 0 sitios | 1 sitio |
| String ASCII "40193" | `34 30 31 39 33` | 0 sitios | 0 sitios | 0 sitios |

\* Los sitios de Word LE 0x00040193 en A6000 están todos en `.text` (código), verificados como **falsos positivos**: corresponden al encoding de instrucciones Thumb-2 `lsls r3, r2, #6` (el campo imm12 contiene 0x0193). No son el ID de cola usado como dato inmediato.

**Conclusión:** No se encontró `0x40193` como dato inmediato, literal, o string en ningún binario.

## 2. ARM vs Thumb — cobertura

**Thumb-2 MOVW/MOVT para 0x40193:**
- `movw Rd, #0x0193`: buscar `hw1 = 0xF240 | (s<<10) | imm10`, `hw2 = 0xF800 | imm11` con imm16 = 0x0193
  - s = bit 15 de 0x0193 = 0
  - imm10 = bits [14:12] de 0x0193 = 0x0
  - imm11 = bits [11:0] de 0x0193 = 0x193
  - hw1 = 0xF240 | 0x000 = 0xF240, hw2 = 0xF800 | 0x193 = 0xF993
  - Bytes LE: `40 F2 93 F9` (para Rd=r0; varía por Rd)
- `movt Rd, #0x0040`: imm16 = 0x0040, s = 0, imm10 = 0x1, imm11 = 0x040
  - hw1 = 0xC240 | 0x001 = 0xC241, hw2 = 0xF800 | 0x040 = 0xF840
  - Bytes LE: `41 C2 40 F8` (para Rd=r0; varía por Rd)

**ARM MOVW/MOVT para 0x40193:**
- `movw Rd, #0x0193`: encoding `E3000193` → bytes `93 01 00 E3`
- `movt Rd, #0x0040`: encoding `E3400040` → bytes `40 00 40 E3`

Se buscó con **cualquier registro destino** (no se fijó Rd). Resultado: 0 sitios en A6000 y A7S.

## 3. Construcciones alternativas (PIC, ldr literal)

También se verificó:
- `ldr rX,[pc,#imm]` + `add rX,pc` con literal 0x00040193 en el pool: 0 sitios en .rodata
- Construcciones `mov`+`lsl`/`orr` para formar 0x40193: no buscadas exhaustivamente (requiere análisis de flujo)

## 4. Conclusión S384

**El ID de cola `0x40193` no se localiza estáticamente** en libObj.so de ningún modelo. Mecanismos posibles (no verificables estáticamente):
1. ID pasado como argumento de función (registro, no literal)
2. ID construido por cálculo en runtime (no movw/movt directo)
3. ID leído de una tabla de configuración en .bss (rellenado en runtime)
4. Callback registrado dinámicamente vía `osal_reg_msg_queue_cb(queue_id, ...)` donde queue_id viene de un registro

**Requiere trazado dinámico (REA o pruebas físicas P1 autorizadas).**

**Documentado en knowledge/agents/NEEDS-HUMAN.md.**

---

**Evidencia:** barrido de bytes completo de los 3 binarios con Python/struct.
