# S55-A — Comparación GPIO BIONZ: A7S 3.20 vs A6000 3.21 (20-10-2026)

Scripts: `analysis/s55/gpio_calls_diff.py` (+ `.json`), `fwdis.py`. Tests: `tests/test_s55_bionz_sync.py`. Método: capstone sobre bytes de `av-cam.bin`
(A6000 SHA `b60c845c…56bb9`, A7S SHA `b857d338…5103e`, ambos base `0x43541000`), pseudocódigo REA solo en A6000 (sesión única, cerrada).

## 1. Equivalentes A7S (VERIFICADO)

| Primitiva | A6000 | A7S | Cómo se halló |
|---|---|---|---|
| `gpio_get(ch,bit)` | `0x43b5e2bc` | `0x43b585c2` | secuencia de 10 B idéntica (`cmp r0,#0x11; push {r4-r6,lr}; mov; mov; bhi`) |
| `gpio_cfg(ch,bit,cfg*)` | `0x43b5e22e` | `0x43b58534` | idem (12 B) |
| `gpio_set(ch,bit,val)` | `0x43b5e29a` | `0x43b585a0` | mismo cuerpo `cmp r0,#0x11; bhi; b.w` |
Base `0xf2910000`, banco = `ch<<8` (32 bits por banco; RDATA `+0x10`, WDATA `+0x40`, DIR `+0`), `ch≤0x11`. Sin desplazamiento fijo entre firmwares.

## 2. Consumidores (VERIFICADO el recuento; argumentos por propagación lineal)

| | get | cfg | set | total |
|---|---|---|---|---|
| A6000 | 50 | 43 | 4 | 97 (= S54) |
| A7S | 50 | 43 | 5 | 98 |

Los 97 sitios de A6000 tienen contrapartida estructural en A7S (mismas funciones contenedoras, mismos IDs de pin). **Única diferencia:** A7S tiene un `set` extra en el
constructor del imager (`0x436f3e40`, función `0x436f3c98`) con IDs `0xf90381/0xf90382`, que en el preset de A7S valen `0xffffffff` → `ch>0x11` ⇒ no-op. El `set` común
`(15,5)` (IDs `0xf90343/344`) cierra los constructores de imager de ambos (`0x436d670a` A6000, `0x436f3f90` A7S).

**Hallazgo central (corrige la lectura de S54):** casi todos los argumentos no son «variables sin inicializar» ni inmediatos, sino `Backup_read_4Byte(id)` con IDs `0xf9xxxx`
(290 llamadas en A6000, 297 en A7S). Ver [inicialización](s55-gpio-initialization-trace.md).

## 3. Respuesta a la pregunta clave

¿Existe en A7S un consumidor dedicado de P4C ausente en A6000? **No en lo recuperado:** las 14 funciones que usan las variables de pin de la tarea CA son idénticas 1:1 en ambos
modelos, con los mismos IDs y los mismos valores (`pin_init.json`, `var_users.json`). Lo que cambia entre modelos es el preset (A7S define 158 entradas `0xf9` frente a 142; 88 difieren,
entre ellas pines de periféricos de A7S) y el sensor, no la tarea de pines.

Límites: intérprete lineal por función (sin ramas); 29 llamadas de `0x43716dd0` y 7 de `0x43707270` tienen IDs dinámicos sin resolver; una consulta negativa no es ausencia global.
