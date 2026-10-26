# S58-A — Productores AE de svd / shd / spl del IMX210 (20-10-2026)

> **Aviso D4 (25-10-2026):** [S59 SOL-07](s59-sol.md) rectifica la atribución de clk del §5: el mismo offset `+0x4c0` no demuestra alias; el escritor de histogramas recibe el objeto `0x43eb121c` y la entrada AE P `0x43eaee84`.

**Resultado:** el productor numérico que S57 no localizó **existe y está recuperado**: no estaba en las etapas candidatas (`0x43844e80`, `0x4384b268`, `0x4385b234`, …; esas solo copian o consumen) sino en la rama de temporización `0x437b5e70`. Tres funciones calculan los valores y sus modelos Python coinciden con el código real (Unicorn): `0x4383d4d0` (tiempo → n, shd, reloj fino; 600/600), `0x4383c9dc` (filas por banco → shd/svd/spl; 300/300) y `0x4383b790` (A/B por banco; solo REA). Queda sin recuperar el **origen de las entradas** (Tv por banco y el bloque de temporización del modo). Pruebas: `tests/test_s58_timing_a7s.py::{AETimingA6000,Itstate}`; scripts `analysis/s58/`; matriz S58-01…11.

## 1. Estructuras (VERIFICADO, REA + Capstone + trazado de escrituras en Unicorn)
| Nombre | Dirección | Papel |
|---|---|---|
| `P` | `0x43eaee84` (GOT `+0xcb0`) | estado AE por fotograma; `P+0x4c4…0x4f3` = bloque de temporización de modo; `P+0x4f4` = VdNum; `P+0x22c` = N |
| `X` | `0x43ead7e0` (GOT `+0x76e4`) | instantánea de `P` (`0x4383d18c`); `X+0x60` = bloque M |
| `AEOUT3` | `X+0x290 = 0x43eada70` | salida de `0x4383d704`: `+0xfc+2i` Tv_i; `+0x348+4i` n_i; `+0x358+4i` shd_i; `+0x368+4i` reloj fino_i |
| `G` | `0x43eb05d8` (GOT `+0x1c3c`) | resumen que lee el constructor de filas (`0x4383bc6c` lo rellena desde `P`/`AEOUT3`); `G+0xb0/+0xc0/+0xd0` = shd_i / fino_i / n_i |
| `G224` | `G+0x224` | salida: filas de 16 B (`+0x2c+16i`), `A_i` (`+0x6e+6i`), `B_i` (`+0x86+2i`) |
| `S` | `0x43eb35d0` (GOT `+0x1db8`) | estado de envío: `S[0]` banco activo, filas `S+4+16b`, copia por modo `S+0x64…` (staging), fila elegida `S+0xc4…0xd8` |

El estudio de S57 trató `S` como origen; en realidad `S` solo **recibe** de `G224` (`0x43843a44`: `memcpy S+0x64+16i ← G224+0x2c+16i`, `S+0xa4+6i ← G224+0x6e+6i`, `S+0xbc+2i ← G224+0x86+2i`, y copia a `S+4…` según el modo).

## 2. Cadena completa (de la velocidad al argumento de SetExposure)
```
Tv_i (AEOUT3+0xfc+2i)                                   [origen: AE core, NO recuperado]
  └─ 0x4382fa94(Tv)   → T_i  (unidades; ver informe B)
      └─ 0x4383d4d0(T_i, M, clk, &n_i, &shd_i, &fino_i)  en 0x4383d704 (4 bancos)
          └─ AEOUT3+0x348/+0x358/+0x368 → 0x4383bc6c → G+0xd0/+0xb0/+0xc0
              └─ 0x4383bf2c: 0x4383c9dc(G,G224) → filas {shd,svd,spl,fino,…} ; 0x4383b790 → A_i,B_i
                  └─ 0x43843a44 (staging S+0x64) → 0x43b0893c (fila del banco S[0] → S+0xc4) → 0x43849fb8 → arg[0..0xf] de SetExposure
                      └─ SetExposure: shd=arg+0, svd=arg+4, spl=arg+6  → regs sombra (IMX210 ID3–ID8)  [S56/S57]
```
`0x437b617e` (que llama a `0x43843a44`/`0x43849fb8`) no tiene llamadores directos (callback). Existe una variante `0x437b5d30` (marcas 0x42–0x45, usa `0x4383ecf8`) no analizada.

## 3. Algoritmos (pseudocódigo fiel a ARM; aritmética de 32 bit sin signo salvo `sdiv`)
**`0x4383d4d0(T, M, clk, &n, &shd, &spl)`** — M = bloque de 0x34 B (`u32 M0=s0, M4=Lt, M8=fb, M20=F`, `u16 M10=vmax, M14=shmin, M2c=hmax`, `u8 M16=svr`):
```
tick = 0xde3 si clk==0 sino udiv(0xf424000, udiv(clk,1000))          # 256e6/(clk/1000)
F    = M20*svr;  n = sdiv(T, F);  rem = T - n*F                       # 0x43b0791e: F==0 → n=T
fine = udiv(hmax*tick,1000)
sb   = (hmax!=0) ? ((s0 > fb+fine) ? s0-fb-fine : 0) : max(s0-fb,0)
lines= (rem > sb) ? udiv(rem-sb, Lt) : 0                              # 0x43b084e8: Lt==0 → rem-sb
shd  = ((vmax-shmin) < lines) ? shmin : vmax-lines
if hmax: rem2=rem-Lt*lines; f2=(rem2>sb)? udiv(1000*(rem2-sb),tick):0; spl = (hmax<f2)?0:hmax-f2   else spl=0
```
Descomposición ideal relacionada con `0x4383d430`: `T ≈ n·F·svr + (vmax−shd)·Lt + (hmax−fino)·tick/1000 + sb`. **No es una inversa exacta universal**: divisiones enteras, saturaciones, casts y overflow pierden información. Los nombres periodo/línea/reloj son interpretaciones de las operaciones; su duración física requiere recuperar M y el significado de clk.

**`0x4383c9dc(G, G224)`**, por banco i (N=G[0x30], svr=G[0x16], vd=G[0x38] con signo, modo=G[0x34]):
```
shdb = G.b0[i];  l40 = G[0x10];  l3c = G.d0[i]
si G[0x24]: t = G[0x18]*((N-1)-l3c); shdb += t; l40 += t; l3c = N       # y si G[0x2c]!=0 l40 = G[0x10]
si modo==0:
    f = (G[0x163]==1 o G[0x164]==1) ? ((FUN_436f059c()==1) ? 1 : G[0x190]) : 0
    svd  = ((N-f)*svr / vd  (vd==0: sin dividir)) - 1
    spl  = max(0, (svr*N/vd - 1) - l3c*svr)                              # 0x4383c7e0
    si svr==0: svd=3 sino { si (svd+1)%svr: svd=svr-1 ; svd = min(svd, svr*N/vd - 1) }
sino: svd=0; spl=0
fila.shd  = (shdb <= l40) ? max(shdb, G[0x14]) : l40       # 0x43b08960(l40, G[0x14], shdb)
fila.spl  = min(svd, spl)                                 # 0x43adb0d2
fila.+10  = min(G[0x2c], fino_i) ; +12 y +14: recortes con G[0x28], G[0x2a], G[0x2e]
```
El tercer argumento `vd` es `G[0x38]` = VdNum. Ambos caminos leen la tripleta `[X8+0x3c]`, `[X8+0x14e]`, `[X8+0xcc]`, pero **sus fórmulas no son idénticas para cualquier entrada**: el host `0x4381106c` usa `N·svr−1` cuando VdNum≤1 y `N/VdNum−1` cuando VdNum>1. El productor incluye `svr` antes de dividir y aplica otros recortes. Ejemplo sintético reproducido en Unicorn: N=6, svr=4, VdNum=3 → fila svd=7; fórmula del host=1. No se sabe si tal combinación es alcanzable. La coincidencia de fuentes no demuestra compatibilidad de todos los estados.

**`0x4383b790`** (REA): para cada banco, `A_i` y `B_i` con límites `B∈[0x801, 0x1800]` (las "funciones" `0x4383c7c4`/`0x4383c7a8` solo devuelven esas constantes y las guardan en `[X+0x56a]/[X+0x568]`) y reparto con `0x43b08684` (umbral 0x1000); salen a `G224+0x6e+6i` (A) y `+0x86+2i` (B) → `S+0xd4`/`S+0xda` → `arg+0x10…`. Sin emulación dedicada; semántica NO_VERIFICADO.

## 4. Qué cambia respecto a S57
* **svd**: ya no solo "validado contra n·svr−1": el productor lo calcula con esa misma fórmula (VERIFICADO).
* **spl** (arg+6) **no** es el reloj sub-línea: es la cuenta de pasos V restantes `svr·N/VdNum−1−n_i·svr` (acotada a svd). El reloj fino (`hmax−…`) viaja en `arg+0xa`. S57 lo trataba como "entero de 12 bit sin fórmula".
* **shd** (arg+0) es la posición de línea (`vmax−líneas`, suelo `M14` en `0x4383d4d0`), luego acotada por `G[0x10]` y con suelo `G[0x14]` en la fila.
* El pulso/ShutMode (S57) no interviene: los valores son función de T, del bloque de modo y de N/VdNum.

## 5. Fronteras (NO VERIFICADO)
1. **Tv_i** (`AEOUT3+0xfc+2i`): lo escribe el núcleo AE antes de `0x4383d704`; no se localizó (la ejecución en Unicorn de `0x437b5b14` con estado aleatorio no escribió en `P`/`AEOUT3` porque los punteros de objeto no eran reales; intento en `a3_trace.py`/`a5_trace.py`, resultados nulos documentados).
2. **Bloque M** (`X8+0x138…0x167`): `0x437aa65c` copia 12 u16 desde `0x43ae84c0() = 0x437876dc()+0xdd0` (X8+0x13c…0x153) y pone a cero o carga `X8+0x154…0x167` desde `param_2[0xa20…]`; esos datos son de tiempo de ejecución (BSS). El hallazgo `ab12=[864,4176,0]` de las tablas del ctor (`0x43bc1ae8`) **no** está demostrado como fuente de M.
3. **clk** (`X+0x5c` ← `P+0x4c0`): `0x438667e0` escribe dos u16 (interpolaciones `0xb0…0xe0` y `0x20…0x90`); no es una frecuencia demostrada; con `clk=0` rige `tick=0xde3`.
4. Variante `0x437b5d30` y servicio indirecto de `0x437b617e`.

## 6. Herramientas (S58)
REA (sesión única `GHIDRA_MAXMEM=6G`, `analysis/rea-independent/bin/session_daemon.py`, cerrada): `procedure_pseudo_code`, llamadores/GOT. **`trace_native_values`** sobre `0x4383bf2c` devuelve un grafo p-code de 1,1 MB (nodos INT_ADD/STORE/INDIRECT, la mayoría `is_dead`) sin nombres de campo; aportó confirmación de que los almacenes son por puntero argumento, pero **la localización de escritores se hizo con Capstone (`a3_stores.py`) y con trazado de escrituras en Unicorn (`wtrace.py`)**. Las salidas REA citadas están en `analysis/s58/rea-out/`.
