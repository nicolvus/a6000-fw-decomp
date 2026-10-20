# S50 — Investigador A (Claude): configuración electrónica (`0xce`, `0xb6`, `0xb7`, `0xed`, `C+0x60/0x94/0x95/…`)

Sesión 19-10-2026. Sin firmware ejecutado, sin cámara, sin flasheo, sin git. Binario: `av-cam.bin`
(SHA-256 `b60c845c…56bb9`, base `0x43541000`). Evidencias en `analysis/s50/claude/evidence/`
(SHA en `evidence.sha256`). Método: sesión REA propia (análisis en frío 468 s, RSS pico 2,9 GB) + **desensamblado
LLVM independiente** (`llvm-objdump --triple=thumbv7`) y un índice propio de referencias PC-relativas/GOT
(`xidx.py`, `calls.py`, `sh.py`). Ghidra histórico no hizo falta: LLVM decodifica las 38 708 direcciones.

**Límite de herramienta (VERIFICADO):** REA 6.5/Ghidra 12.1.4 responde «No procedure exists» para las funciones
Thumb impares clave (`0x437d9f9c`, `0x437da2d8`, `0x437dad78`, `0x43af7732`…) y `xrefs` de datos PC-relativos
devuelve vacío (`0x43ff7540`, `0x43ff23b0`). Una consulta vacía de REA no prueba ausencia; todo lo siguiente se
verificó sobre bytes con LLVM (decodificador distinto del de Ghidra).

## Resultado en una línea

Los parámetros `0xce`/`0xed`/`0xb7` **llegan a un bloque de configuración del imager (B) y a un descriptor de modo
(`0x43eefb1c`) que solo se exportan a registros de estado**; `0xb6 A_LINEAR_ELEC_SHUT` **no tiene ningún consumidor**
en este firmware. Ninguna ruta hallada finaliza la exposición electrónicamente.

## VERIFICADO

1. **`0xb6 A_LINEAR_ELEC_SHUT` es inerte.** (a) La tabla `clave→handler` (`0x43ff23b0`, filas de 8 B) lo envía al
   handler genérico `0x43789709`, igual que `0xce`, `0xb7`, `0xed`; (b) no existe en **todo** el binario ninguna fila
   `{0xb6, slot, clase<8}` de la tabla de callbacks (barrido de 4 B en alineación completa; `0xce`, `0xed`, `0xb5`,
   `0xb7` ×2 y `0xba` ×2 sí aparecen: `evidence/rows-shutter-keys.txt`); (c) el conmutador sobre `C+0x60` (id del comando activo)
   de `0x4382dd78` solo tiene casos `{0x8,0x9,0xc,0x10,0x3c…0x46,0x49,0x4d,0x55,0x80–0x83,0x91,0x93,0x99,0x9a,0xb5,0xb7,
   0xba,0xd0,0xe9,0xff}`: sin `0xb6`. El comando se acepta y no tiene efecto en `av-cam`.
2. **Dónde se consumen los campos de `C`.** `0x4382dd78` (`push.w {r0-r8,lr}`) es el **constructor del bloque B** desde `C`
   (`C=[ctx+0x50]`): conmuta sobre `C+0x60` y copia `C+0x94→B+0x36`, `C+0x95→B+0x37`, `C+0x9e/0xa0 (0xed)→B+0x38/0x3a`,
   `C+0xa1/0xa2→B+0x3b/0x3c` (`0x4382e34a–0x4382e3c6`). `evidence/copy-C94-95-9e-a0-to-B.txt`.
3. **`0xb7 A_NONLINEAR_ELEC_SHUT`:** el caso `0x4382e24e` pone `B+0x5c=1` y copia 16 B de parámetros del mensaje a
   `B+0xb20…` (tipo en `+0xb20`, subvalores `+0xb21–0xb23…`). Único lector fuera de la copia: `0x438d5eb4`
   (0xc94 B, paso de un pipeline `0x438d2290` que construye un registro de estado; sin literales MMIO salvo `0xf38bfa0f`
   dato, no puntero). Por tanto estos parámetros terminan en estructura de software, sin escritura MMIO demostrada.
4. **`C+0x94/0x95` → modo.** B+0x36/0x37 → G (copia 14 B de S42) → `0x43842158` (llamada desde `0x438412d0`).
   `0x43842158` calcula una variable de modo global `X+0x60` (X=`0x43eefb1c`) en tres fases:
   (i) condiciones del cuadro (`ctx+0x4bc` bits `0x60/0x80/0x20`, `ctx+0x41c`, `ctx+0x38c`, `u16 +0x162` frente a límites) →
   valores 1/3/5; (ii) si el byte de estado del sensor `[0x43f76342+0x7e]` ≠ 0, modo = byte−1 (1..8 → 0..7, otro → 1);
   (iii) **si `G+0x36==1` (= `C+0x94` enable) el valor `G+0x37` (= `C+0x95`) sobrescribe el modo** con
   `{0→1, 1→3, 2→2, 3→0, 4→4, 5→5, 6→6, 7→7, >7→1}` y pone `X+0x64=X+0x65=0`.
   `evidence/mode-override-43842158.txt`. **El nombre `CURTAINMODE` no equivale a «cortina»**: es un alfabeto de modo 0–7
   compartido con el byte de estado del sensor; su semántica física no está demostrada.
5. **Consumidores de X.** Solo 5 funciones tocan X (índice PC-relativo exhaustivo; GOT sin hits): `0x43841bf8`,
   `0x43841d8e`, `0x43842158` (escritor), `0x438423c4/0x43842440` (lectores). `0x43842440` exporta al registro de estado
   `obj+0xf9 = modo+1 (0xff si fuera de 0..7)`, `obj+0xfa/0xfb = X+0x64/0x65`; getters
   `0x43842404/10/20/30` los leen `0x4383f5e4`, que los copia a globales (`0x43eedecc`, `0x43f7ca56`, `0x43f9b503/01`)
   usados solo por `0x43840150/0x4384031c/0x43841070`. **No se halló escritura MMIO derivada del modo.**
6. **Las copias `+0x94/0x95` en `0x438d6e90`, `0x438403e4`… son volcados byte a byte a registros de estado**
   (`+0x153/+0x154`, `+0x135/+0x136`): consumidores de reporte, no de control.
7. **Tabla `0x43bc4b58`** (36 filas `{u16 clave, u32 estado}` consultada por `0x437d9ea8`, usada en `0x437d9f9c`): rechazo
   con códigos `0xa001–0xa013` para claves como `0xb5(0xa010)`, `0xb7(0xa010)`, `0xba(0xa011)`, `0x99`, `0x9a`; `0xb6/0xce/0xed`
   **no** figuran (no rechazados por esa tabla). Semántica de los códigos NO_VERIFICADO.

## PARCIAL / INFERENCIA

- **PARCIAL:** el imager expone `SetMode/SetExposure/SetRead/GetShutGainParam` (`C_Imager`, cadenas); el nexo B/G → `ModeRsvParam`
  → `SetMode` no se cerró (frontera con la línea de Codex).
- **INFERENCIA:** `CURTAINMODE` actúa como override de diagnóstico/servicio del alfabeto de modo (llega por el puente USB de servicio, S49).
  El mapa `{0→1,1→3,2→2,3→0}` es distinto de la identidad, lo que sugiere que el valor externo no es el código interno.
- **PARCIAL:** quién escribe `[0x43f76342+0x7e]` (byte de estado del sensor) no está resuelto (no lo escriben las 12 funciones que usan el
  GOT `0x43f76342`).

## NO_VERIFICADO

Que algún modo 0–7 corresponda a mecánico/EFCS/electrónico; efecto físico de `X+0x60`; emisor de `0xce` en uso normal;
cualquier ruta de fin electrónico de exposición en este bloque.

## Hipótesis descartadas (con evidencia)

- «`0xb6` tiene un handler pendiente que habilita el modo electrónico lineal»: **descartada** (sin fila, sin caso `C+0x60`).
- «`CURTAINMODE` selecciona directamente mecánico/EFCS/electrónico»: **no apoyada**; es override de un código de modo que se exporta a estado.
- «Los consumidores de `C+0x94/0x95` escriben MMIO»: no hallado (copias a registros de estado + selector de modo).

## Siguiente paso exacto

1. Resolver quién consume `obj+0xf9` (o su equivalente) *fuera* de volcados: pipeline `0x438d2290` y `0x4385a630`.
2. Escritor de `[0x43f76342+0x7e]` y paso B/G → `ModeRsvParam`/`SetMode` de `C_Imager` (enlazar con el informe de Codex).
3. Si ningún consumidor de modo toca MMIO: la cadena `0xce/0xed/0xb7` queda confirmada como parámetros de reporte/ajuste, no de disparo.

## Recursos y honestidad

Tiempo: ~35 min de trabajo (8 min de análisis en frío REA). RSS REA 1,3–2,9 GB (`GHIDRA_MAXMEM=4G`); RAM disponible mín 2,9 GB; swap
~7,2 GB (ya usado antes de S50). Sin paginación intensa. Límite: REA no cubre Thumb impar, por lo que la exploración fue por LLVM;
el índice PC-relativo/GOT es heurístico (ventana de 14 instrucciones, sin flujo): un acceso por otra forma de direccionamiento podría faltar.
