# FILM-PB-1 · sub-msv-698ec8 — ¿devuelve 0 el cargador del IFO (`0x698EC8`) con el sector FBM `0x31` registrado?

26-11-2026 · `libmpr.so` fw 3.21 (10 321 204 B, SHA-256 `9a74a3bb…4c30`) · VA = offset del ELF ·
Evidencia: [`reports/evidence/film-pb-1-sub-msv-698ec8-20261126/`](evidence/film-pb-1-sub-msv-698ec8-20261126/README.md).
QEMU sobre **copia** del volcado de `/dev/nflasha4` (`a5ab15ca…7247`), perfil `nf4`, `NFLASH4=1`. Cámara no usada,
`mcp_rea` no usado, nada de git.

## Resumen (≤18 líneas)

1. **La cadena del IFO MP4 no se ejecuta en el arnés**: 6 trampas UDF en `0x698EC8`, `0x3AFA94`, `0x35EA1C`, `0x698FB8`, `0x67CA6C` y `0x698F18` → **0 capturas en 240 s** (`run1`, `run2`); sin objeto real no hay medida directa.
2. La clase **sí** se instancia con su ctor real `0x3B04A4` (`[obj]=base+0x835980`, hijo `[obj+0x50]`=`new(0x4B78)`+ctor `0x3B1DE8`) y admite `[+0x4088]=4`, `[+0x408c]=3` (`run3`).
3. Pero llamar a `0x3AFA94` desde el hilo inyectado **no vuelve**: se queda en su macro de traza `0x34E468` → `0x5BB83C` → `osal_valloc_msg_wait` (`run3`, `run5`). Es límite del arnés, no del código medido.
4. La respuesta se cierra con la única entrada **medida** y con el código, instrucción a instrucción:
5. **Medido en esta sesión** (`run6`, `NFLASH4=1`): `EWBDFD 4 3 0` + `InitB 6 3` → `idx 10 = 0x31/h3/+8=1/om6` (1 300 B escritos) y `BkRead(0x04,3) = 0x10100003`; coincide con `fbm-sector31-c/runC1,runC2` y `fbm-initb-6-3-nflasha4/run3`.
6. `0x35E0FA/FC/100` **tolera** `0x10100003` → `0x35E118`: `vtbl[0xB8]`=`0x3B16B0` escribe `8` en `[r7+0xd5]`, y `[r7+0xd6]`=0 (`0x35E074`).
7. `8≠0` → `0x35E954`; `0≠0x11` → `r5=0x00500003` (`0x35E994`) → `0x35EA08` devuelve **`0x00500003`**.
8. `0x3AFA94`: cabecera `0x00`≠`0x10` → *Need Salvage*: `r6=0` (`0x3AFB18`), `[msv+0x44]=1` (`0x3AFB22`) → `0x3502CA(this,0)` → `0x350124(0)` → `0x350242` → **0**.
9. `0x698EC8`: `status=0` → `0x6F0D4C` → `0x6F0EA4` → **0**; `cbz r0` ⇒ sin `Unload` y **sin imprimir 1749**.
10. Objetos **sintéticos**: tampoco miden nada — `SIN1` (`[+0x4088]=4`, `[+0x408c]=3`, resto 0) se quedó **antes de tocar el objeto**, en la misma macro de traza; y por código moriría en `0x35E11A` (`blx [r4]+0xB8`) y `0x35E9C0/C6` (`0x35A464`/`0x358BB4` con `this`) → artefacto, no 2.º fallo.
11. Queda abierto: si `[msv+0x44]=1` dispara luego una reconstrucción del backup (no medido).

## 1. Qué se ha medido en el arnés (y qué no)

| # | medida | resultado | fichero |
|---|---|---|---|
| 1 | ¿la cámara ejecuta la cadena del IFO al arrancar en el arnés? | **no**: 0/6 trampas con captura en 240 s | `run1/consola.log`, `run2/consola.log` |
| 2 | ¿se puede instanciar la clase con su ctor real? | **sí**: `0x3B04A4` → `[obj]=base+0x835980`, hijo `[obj+0x50]`, `[+0x4088]=4`, `[+0x408c]=3` | `run3/consola.log` |
| 3 | ¿devuelve `0x3AFA94` desde un hilo inyectado? | **no vuelve** (traza OSAL); con las macros TRACE anuladas, tampoco | `run3/consola.log`, `run5/consola.log`, `run4/consola.log` |
| 4 | ¿el sector queda registrado con la receta de consola? | **sí**: `idx10 = 0x31 / h3 / +8=1 / om6` (1 300 B), `BkRead(0x04,3)=0x10100003` | `run6/consola.log` (+ `fbm-sector31-c-20261126/runC1,runC2`, `fbm-initb-6-3-nflasha4-20261126/run3`) |

`run2` incluso esperó 240 s con las 6 trampas armadas: ni `mp4Ifo_General::Load` (`0x698FB8`), ni `CreateAndLoad`
(`0x67CA6C`), ni el worker común de la tabla de respaldo (`0x35EA1C`) se ejecutan. Es la misma conclusión de
`film-pb-1-sub-arnes-datos-avf-20261126.md` §8-10: en el arnés no arranca el gestor de vídeo, así que **no existe**
el objeto `MsvMcmd` de la cámara y no se puede llamar «de verdad» a `0x698EC8`.

## 2. Por qué no vale un objeto sintético (lo que el código toca de la clase)

`0x698EC8` sólo usa `[this+0]` → `0x6964E2` → `[+8]` (el `MsvMcmd`) y, si falla, `Unload` `0x697D70`. El peso está dentro:

| VA | qué exige del objeto |
|---|---|
| `0x3AFA94` `+0x50` | puntero al objeto «`+0x4000`» (creado con `new(0x4B78)` en el ctor) |
| `0x35EA1C` `+0x4084` | logger; `+0x4088`/`+0x408c` = userID/mediaID (`0x35E0EC/0x35E0F0`) |
| `0x35E118` | **llamada virtual** `[obj]→[+0xB8]` con `this` (`0x3B16B0`: escribe `8` en `*pb`) |
| `0x35E9C0/0x35E9C6` | llamadas a métodos del objeto `0x35A464` y `0x358BB4` con `this` |
| `0x35E9CE` | `0x2B4584(&buf)` (liberar el pack) |

Con un bloque a cero la primera parada sería `0x353B96` (lectura de `[this+0x4084]` con `this=0`) y, si `[+0x50]` se
apunta a sí mismo, `0x35E11A` (vtable nula): es **artefacto**, no un segundo problema. Medido en `run6`: el objeto
sintético `SIN1` **ni se llega a usar** — la llamada se queda antes, en la macro de traza `0x3AFAB2`. Por eso se usó la
clase real (punto 2 del cuadro) y, aun así, la traza OSAL es lo único que impide cerrar la medida dentro del arnés.

## 3. La cadena completa, con la entrada medida

Antes de crear el sector (`BkRead=0x10100001`, medido en `fbm-initb…/run7` y `runC*/runE`): `0x35E0F4` → error directo
(`0x35E114`), `0x35EA1C` = `0x10100001`, `0x3AFA94` = `0x00100001` (cabecera `0x10` → «Err RcsBackupTblData»), y
`0x698EC8` = **`0xB0800001`** (el traductor `0x6F0D4C` no reconoce `0x00100001` y cae en su valor por defecto) — es el
1749 del anillo de la cámara. Después de crear el sector:

```
BkRead(0x04,3) = 0x10100003                      [MEDIDO: run6 + C1/C2]  único eslabón medido de la cadena
  0x35E0FA cbz / 0x35E0FC cmp / 0x35E100 beq      tolera 0x10100003 -> 0x35E118
  0x35E118 blx [obj+0xB8] = 0x3B16B0              *(&0xd5) = 8   (r0 se sobrescribe en 0x35E12C)
  0x35E152 cmp r0(=0x10100003)                    igual -> 0x35E158
  0x35E160 cmp 8,[0xd6]=0                         distinto -> 0x35E954
  0x35E954 cmp [0xd6],0x11                        distinto -> 0x35E958
  0x35E994 r5 = 0x00500003                        -> 0x35EA08 devuelve 0x00500003   (RcsBackupTblData)
  0x3AFAFE and r0,#0xff000000 = 0                 != 0x10000000 -> 0x3AFB0C « Need Salvage»
  0x3AFB18 r6 = 0 ; 0x3AFB22 [msv+0x44] = 1
  0x3AFBBC r0 = 0x3502CA(this,0) -> 0x3502B8 -> 0x350124(0) -> 0x350242   => devuelve 0   (0x3AFA94)
  0x698EEA 0x6F0D4C(status=0) -> 0x6F0EA4 -> 0                                     => devuelve 0   (0x698EC8)
```

## 4. Conclusión en una línea

**«El arreglo del sector es suficiente para que el cargador del IFO devuelva 0»** — con la salvedad, medida en el
código, de que el 0 llega porque `0x3AFA94` convierte el `0x00500003` (tabla `RcsTbl` vacía) en *Need Salvage* y lo
devuelve como 0, dejando `[msv+0x44] = 1`.

## 5. Lo que no está medido (y qué haría falta)

- La llamada real a `0x3AFA94`/`0x698EC8` dentro del arnés: bloqueada por `osal_valloc_msg_wait` desde un hilo ajeno a
  OSAL (`0x34E468` → `0x5BB83C`). Alternativa: arrancar el gestor de vídeo (`MprCtrl::Init` → cola de `AviMMgrCmd`) o
  enganchar la llamada en el hilo de la cámara en vez de invocarla desde fuera.
- Si `[msv+0x44] = 1` provoca una reconstrucción del backup en la cámara real (escritura en `nflasha4`).
