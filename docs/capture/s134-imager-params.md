# S134 — la aritmética de los parámetros del imager (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`)

**Hito de la línea de ingeniería inversa general**, con relevance directa para la línea del
obturador electrónico. Responde a la pregunta que dejó abierta S124.

Informe: [analysis/s134_imager_params/imager_params.md](../../analysis/s134_imager_params/imager_params.md) ·
Datos: `disasm.json` · Test: `tests/test_s134_imager_params.py`.

## Hallazgo central

La relación entre `shut` y `svd` en el módulo de sincronización es **aritmética, no tabulada**:

```
svd_esperado = (svd == 9 ? 1 : shut) * svr_num - 1        (svr_num = u8 en [estado+0x14e])
svd_esperado = (svd == 9 ? 1 : shut) / VdNum - 1           (VdNum  = u16 en [estado+0xcc], si VdNum > 1)
```

Si el resultado desborda (bit 15 tras `uxth`) se emiten `Imager param error shut:%d, svr_num:%d,
VdNum:%d` `0x43cb11d2` e `Imager svd error. shut:%d, svd:%d -> %d` `0x43cb1217`. El único valor
*magic* es `svd == 9`, que actúa de centinela (usa `shut = 1`).

**Esto descarta la hipótesis de una «tabla de valores por `drive_mode`»** para `svd`: el peso del
`shut` está en la fórmula, no en una tabla.

## De dónde sale el bloque de seis parámetros (función `0x4381106c`)

| parámetro | origen |
|---|---|
| `shd` | `[estado+0x24]` (u32) |
| `svd` | u16 bajo de `[estado+0x28]` |
| `spl` | u16 alto de `[estado+0x28]` (¡empaquetados en la misma palabra!) |
| `sint` | u8 de `[estado+0x2c]` |
| `gs` | **flag binario**: 1 si el `svd` del contexto vale 9, si no 0 |
| `shut` | `[ctx_sync+0x1f8]` |

El estado del imager se obtiene con un **accesor de singleton** (`0x4378f9b4` → global
`0x43e99208`, cero en el blob: se rellena en ejecución), y la división es una rutina **sin signo**
(`0x4355faf0`, tipo `__aeabi_uidiv`: `clz`/`rsb` + tabla de saltos).

## Para la línea del obturador

`shut` sigue siendo el **índice/contador de obturación** del modo de lectura (S124), **no** un
selector de mecanismo: la fw3.21 no introduce ningún parámetro de obturador electrónico.
**Sin efecto en S51 (A/B/C = NO).**

## Abierto / NO VERIFICADO

- El bloque de modo de S124 (`[r1+0]`, `[r1+4]`, `[r1+6]`, `[r1+9]`) **sigue sin localizar**.
- Qué son exactamente `svr_num` y `VdNum` y quién los escribe; por qué `svd == 9` es especial.
- Si la A7S fw3.20 usa la misma fórmula (su contexto tiene otros offsets, S124 §4).
