# S384 — Búsqueda del ID de cola `0x40193` (C2 receptor) en ARM y Thumb

**INFORME VIGENTE 23-10-2026:** [trazado verificado del ID](queue-40193-flow-2026-10-23.md).

**Actualización 25-10-2026:** [servicio y transporte estáticos identificados](capture-static-followup-2026-10-25.md).
El receptor LIRO espera con `osal_rcv_msg_tmo`; no requiere callback Linux
específico. El servicio del descriptor es `sta_tsk(0x46,descriptor)`.
Los nueve words A6000 de `.text` sí tienen cargas LDR desde pool; su
desensamblado lineal no permite descartarlos. Se identifican receptor e
instalador de su puntero en av-cam. Las secciones históricas siguientes
conservan errores explícitamente invalidados; no usarlas como conclusión vigente.

## 1. Patrones buscados en libObj.so (A6000 fw3.21, A7S fw3.20, A6300 fw2.01)

**AUDITORÍA 23-10-2026 — tabla y encodings históricos invalidados.** Los patrones Thumb publicados no codifican las instrucciones indicadas. `0x40193` requiere mitad alta **4**, no `0x40`. Además, el test reutilizaba el offset `.data` A6000 en la A7S. Las tablas siguientes se conservan como registro del método fallido; sus ceros de MOVW/MOVT no son evidencia de ausencia.

Resultados reproducidos desde las secciones de cada ELF: cero palabras `93 01 04 00` en `.rodata`/`.data` de A6000 y A7S y cero cadenas ASCII `40193`. `.data` A7S está en offset `0xefb9e0`, tamaño `0x736a0`; A6000 en `0x102d320`, tamaño `0x73588`.

El encoding correcto `40 f2 93 13` es `movw r3,#0x193` y existe en ambos binarios (A6000, por ejemplo, `0x14ccde`). `c0 f2 04 00` es `movt r0,#4`. Un barrido por máscaras de halfwords de `.text` detecta **60/44** candidatos Thumb MOVW #0x193 en A6000/A7S; son candidatos estáticos, no 60/44 construcciones del ID completo. Falta análisis de flujo y modos ARM/Thumb para identificar su uso. La A6300 no se reverificó en esta auditoría.

**Conclusión vigente:** origen por literales, receptor, instalador, arranque
estático y transporte userland/ioctl/OSAL kernel identificados. Los negativos
de datos son acotados. No se observó activación real ni se demuestra captura física.

## Registro histórico (no usar como prueba)

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

## 2. ARM vs Thumb — encodings históricos INVALIDADOS

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

## 4. Conclusión histórica S384 — INVALIDADA

**El ID de cola `0x40193` no se localiza estáticamente** en libObj.so de ningún modelo. Mecanismos posibles (no verificables estáticamente):
1. ID pasado como argumento de función (registro, no literal)
2. ID construido por cálculo en runtime (no movw/movt directo)
3. ID leído de una tabla de configuración en .bss (rellenado en runtime)
4. Callback registrado dinámicamente vía `osal_reg_msg_queue_cb(queue_id, ...)` donde queue_id viene de un registro

**Requiere trazado dinámico (REA o pruebas físicas P1 autorizadas).**

**Documentado en knowledge/agents/NEEDS-HUMAN.md.**

---

**Evidencia:** barrido de bytes completo de los 3 binarios con Python/struct.
