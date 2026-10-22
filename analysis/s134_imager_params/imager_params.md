# S134 — la aritmética de los parámetros del imager (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`)

> Hito de la **línea de ingeniería inversa general**, con relevance directa para la línea del
> **obturador electrónico**: es el punto donde la fw3.21 **calcula** el parámetro de obturación
> del modo de lectura, y donde S124 dejó abierta la pregunta de la «tabla de valores por
> `drive_mode`». Verificación contra los bytes de la A6000 fw3.21; convención
> **vaddr = 0x43541000 + file_offset**. Sin efecto en S51.

## 1. La pregunta que responde este hito

S124 verificó de dónde sale cada campo de la traza `[CAM_IMAGER]: SetExps : [PrevDrv][NowDrv]
[NextDrv][svd][shd][spl][shut]` y dejó abierto: *«la tabla de valores por `drive_mode`»*.
Este hito sigue la pista desde el otro extremo: la función de `[CAMERA_MAIN_SYNC]` que **valida**
esos parámetros, y muestra que **la relación entre `shut` y `svd` es aritmética, no tabulada**.

## 2. La función que valida: `0x4381106c`

| traza | sitio PIC | formato |
|---|---|---|
| `[CAMERA_MAIN_SYNC]: Imager param error shut:%d, svr_num:%d, VdNum:%d` `0x43cb11d2` | `0x4381110e` | error de parámetros |
| `[CAMERA_MAIN_SYNC]: Imager svd error. shut:%d, svd:%d -> %d` `0x43cb1217` | `0x43811162` | `svd` incorrecto → valor esperado |
| `[CAMERA_MAIN_SYNC]: shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d` `0x43cb1253` | `0x438111d4` | volcado del bloque completo |

## 3. De dónde salen los seis parámetros (volcado de `0x4381118e`–`0x438111d4`)

1. `bl 0x4378f9b4` → un **accesor de un singleton** (`ldr r0,[pc,#4]; add r0,pc; bx lr` → global en
   `0x43e99208`, inicializado a cero en el blob: se rellena en ejecución).
2. `ldr r3, [r0, #0x24]` + `ldm r3, {r0,r1,r2,r3}` → se copian **16 bytes** a la pila:
   `stm.w r6, {r0,r1,r2,r3}` con `r6 = sp+0x18`.

| destino | origen | parámetro |
|---|---|---|
| `sp+0x18` | `[estado+0x24]` (u32) | **`shd`** |
| `sp+0x1c` | `[estado+0x28]` (u16 bajo) | **`svd`** |
| `sp+0x1e` | `[estado+0x28]` (u16 alto) | **`spl`** |
| `sp+0x20` | `[estado+0x2c]` (u8) | **`sint`** |
| `sp+0x21` | flag calculado | **`gs`** |
| `[r4+0x1f8]` | contexto de sincronización (u32) | **`shut`** |

→ **`svd` y `spl` van empaquetados en la misma palabra de 32 bits** (`[estado+0x28]`), y `gs` es un
**flag binario**, no un contador: en `0x4381118e`:

```
ldr.w r3, [r4, #0x1fc]   ; svd del contexto
cmp  r3, #9
bne  0x4381119a
subs r3, #8              ; svd == 9 -> 1
b    0x4381119c
movs r3, #0              ; svd != 9 -> 0
strb.w r3, [sp, #0x21]   ; gs
```

Es decir, **`gs` = 1 cuando el `svd` del contexto vale 9** (un valor especial).

## 4. La fórmula: cómo se calcula el `svd` esperado

En `0x438110be`–`0x438110f8`:

```
ldr.w r0, [r4, #0x1f8]   ; shut
cmp  r0, #0
beq  <fin>               ; si shut == 0, no hay nada que validar
ldr.w sl, [r7, #8]       ; sl = *(estado+8)  (otra estructura)
ldr.w r6, [r4, #0x1fc]   ; svd del contexto
ldrh.w sb, [sl, #0xcc]   ; VdNum
cmp  r6, #9
ite ne
movne r6, r0             ; svd != 9 -> r6 = shut
moveq r6, #1             ; svd == 9 -> r6 = 1
cmp.w sb, #1
bhi  <division>
ldrb.w r0, [sl, #0x14e]  ; svr_num (u8)
muls r0, r6, r0          ; r0 = shut * svr_num
b    <fin>
<division>:
mov  r0, r6
mov  r1, sb
bl   0x4355faf0          ; division sin signo (udiv)
<fin>:
subs r0, #1              ; -1
uxth r0, r0
tst.w r0, #0x8000        ; signo -> desbordamiento
beq  <ok>                ; sin error
```

→ **`svd_esperado = (svd == 9 ? 1 : shut) * svr_num − 1`**, y **`svd_esperado =
(svd == 9 ? 1 : shut) / VdNum − 1`** cuando `VdNum > 1` (`bl 0x4355faf0` es una rutina de
**división sin signo**: `clz`/`rsb` + tabla de salto, típico `__aeabi_uidiv`).

Si el resultado se desborda (queda el bit 15 a 1), se emiten las dos trazas de error:
`Imager param error shut:%d, svr_num:%d, VdNum:%d` (con `shut` = el valor usado, `svr_num` =
u8 en `+0x14e`, `VdNum` = u16 en `+0xcc`) y `Imager svd error. shut:%d, svd:%d -> %d` (con el
`svd` actual y el valor esperado).

## 5. Conclusión para la pregunta de S124

**No hay una «tabla de valores por `drive_mode`» para `svd`**: la relación con `shut` es
**aritmética** (una multiplicación o una división por dos contadores del propio estado del
imager) y el único valor *magic* es el `svd == 9`, que actúa como centinela (usa `shut = 1`).
Esto **descarta** la hipótesis de una tabla de parámetros por modo de lectura y deja el peso del
`shut` en la **fórmula**, no en una tabla.

**Lo que esto NO dice**: no se ha localizado el bloque de modo que S124 vio leer en
`FUN_436d6f70` (`NowDrv`/`PrevDrv`/`NextDrv` en +0/+4/+6 y `shut` en +9); esa estructura sigue
sin localizar (S124 §7). Lo que se ha esbozado aquí es el otro lado: **cómo se usa `shut`** para
validar `svd` en el módulo de sincronización.

## 6. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| función `0x4381106c` (prólogo `push.w {r4-r8, sb, sl, lr}`) | bytes del binario |
| `svd`/`spl` empaquetados en `[estado+0x28]` | `ldm`/`stm` de 4 registros a `sp+0x18` y uso de `sp+0x1c` y `sp+0x1e` como u16 |
| `gs` = (svd == 9) | `cmp r3,#9` + `subs r3,#8` / `movs r3,#0` + `strb` |
| fórmula de `svd` | desensamblado de `0x438110be`–`0x438110f8` |
| `0x4355faf0` es división sin signo | desensamblado (`clz`, `rsb`, tabla de saltos) |
| formato de las trazas | referencias PIC(strict) `0x4381110e`→`0x43cb11d2`, `0x43811162`→`0x43cb1217`, `0x438111d4`→`0x43cb1253` |

## 7. NO VERIFICADO / abierto

- El bloque de modo de S124 (`[r1+0]`, `[r1+4]`, `[r1+6]`, `[r1+9]`): **sigue sin localizar**.
- Qué es exactamente `svr_num` (u8 en `+0x14e`) y `VdNum` (u16 en `+0xcc`), y quién los escribe.
- Por qué `svd == 9` es un caso especial (y si hay más centinelas).
- El significado de `sint` y `gs` más allá de lo medido (`gs` = flag `svd == 9`).
- Si la fw3.20 de la A7S usa la **misma** fórmula (no comprobado: la A7S tiene un contexto con
  otros offsets, S124 §4).
- Nada de esto **modifica** S51 (A/B/C = NO): `shut` sigue siendo el índice/contador de
  obturación (S124), no un selector de mecanismo.

## 8. Ficheros de este hito

| fichero | contenido |
|---|---|
| `imager_params.md` | este informe |
| `disasm_params.py` | script que extrae el desensamblado citado (para repetirlo) |
