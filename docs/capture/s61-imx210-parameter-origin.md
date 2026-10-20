# S61 — origen de los seis pares u16 del bloque `obj+0xE20` (IMX210, A6000)

20-10-2026. A6000 `av-cam.bin` SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`. Método: Capstone sobre bytes, REA (una sesión, cerrada) y Unicorn con el código original. Pruebas: `tests/test_s61_imx210.py` (22 OK). Scripts: `analysis/s61/`.

## Cadena reconstruida

```
obj+0x2BE..0x2CE (u16, origen NO LOCALIZADO)
  └─ P0 0x43861ed0 ──► obj+0x310..0x334 (ventanas lo/hi, márgenes ±0x400, constante 0x3400)
       └─ obj8 = copia de obj+0x2CC (0x244 B; memcpy en 0x43aece72..0x43aece90, p[2] = obj8)
            └─ B 0x43aecbec (si [[p]+0x3a]==1): 5 pares ◄ obj8+0x48,4a | 4c,4e | 50,52 | 54,56 | 5c,5e
                 + 6.º par = 0x437a5a6c(tabla T[idx]) ◄ BK4 0x300AB (o override p[3]+0x15d8/da)
                      └─ accesor 0x43ae8504 (= 0x437876dc()+0xE20) → bloque de 24 B
G (0x43e964a4, GOT+0x21a0) +0x168/+0x16A (escritor NO LOCALIZADO)
  └─ A 0x437ab474 (tramo 0x437ab502): si bit6 de G[0xD]==0 → 6 copias de (G[0x168],G[0x16A]) → mismo bloque
bloque obj+0xE20 ─(estado obj+0xE04..0xE53)─► 0x43b00da0/0x43b00dd4 (publica en VD_Pre) ─► obj+0xDD0 ─► consumidor IMX210 (S58/S59)
```

## Hallazgos

| ID | Estado | Afirmación | Evidencia |
|---|---|---|---|
| P61-1 | VERIFICADO | **A** solo escribe si `(G[0xD]>>6)&1==0`: `0x437ab502..0x437ab50e` (`movs r1,#6; ldrb r0,[r5,#0xd]; bl 0x43aeb0cc; cbnz`), `0x43aeb0cc` = `(r0>>r1)&1` (bytes `asrs; and #1; bx lr`). A escribe 12 `strh`: pares idénticos `(G[0x168],G[0x16A])` ×6. | Capstone + emulación del tramo real (`analysis/s61/e4_producer_a.py`: `G[0xD]` ∈ {0x00,0xBF} publica; {0x40,0xFF} no). |
| P61-2 | VERIFICADO / **corrige S60** | `obj+0x168/0x16A` de S60 **no** son campos del objeto de 0xF20 B: A los lee del **global G = `0x43e964a4`** (slot GOT `+0x21a0`; `ldr r5,[r4,r3]` en `0x437ab506`). `0x437aaff8` (preajuste de 0x1F4 B) lee los mismos campos. | bytes `0x437ab502..0x437ab51a`, `0x437aaff8..0x437ab006`; GOT `0x4401eee4+0x21a0`. |
| P61-3 | NO VERIFICADO | Escritor de `G+0x168/+0x16A` no localizado: 232 funciones cargan G; taint de registros no halla un store a esos offsets; no hay referencias pc-relativas directas a G; no hay memcpy hacia G detectado. Los únicos stores `+0x168/+0x16A` en la subred de constructores son sobre el *stage* `[p]` (`0x437aa4e4/e8` desde `src+0x164e/+0x1650`; `0x437aae54/58` = 0). Que G coincida con el stage es **no demostrado**. | `analysis/s61/{cfg_refs,g_writers}.py`, `g_writers.json`. |
| P61-4 | VERIFICADO | **B** solo escribe si `[[p]+0x3a]==1` (`0x43aecbf0..0x43aecbf8`). `stage+0x3a`: `0x437a9d30` lo pone a 0 (`0x437aa03c`); `0x437aa65c` lo copia de `src+0xb4` (`0x437aa956`); `0x437a9a7c` lo borra a 0 cuando `G[0xD]` bit6==1 (`0x437a9b8a..0x437a9ba0`). Sin escritor a 1 localizado en ningún constructor. | bytes; emulación `stage3a=0` → bloque de ceros. |
| P61-5 | PARCIAL | B copia 5 pares de `obj8+0x48..0x5f` (10 `ldrh.w` verificados) y calcula el 6.º con `0x437a5a6c`. En la familia `0x4379fc9e`/`0x43aece72`, `obj8 = obj+0x2CC` (copia de 0x244 B). En la familia `0x4379ed34` p[2] = `r6+0x248` (base distinta, sin resolver). | bytes `0x43aecc00..0x43aecc50`, `0x43aece6e..0x43aece94`, `0x4379fc20`. |
| P61-6 | VERIFICADO | **P0 `0x43861ed0`** (llamado desde `0x43862bc4`, `0x43863668`) escribe `obj+0x314,316,318,31a,31c,31e,320,322,328,32a` (más 0x310,0x312,0x324,0x326,0x32c..0x334) a partir de `obj+0x2be,2c0,2c2,2c4,2c6,2c8,2ca,2cc,2ce,2d0`: ventanas `x`, `x+0x400`, `x−0x400`, constante `0x3400`, interpolación con división (`0x4355fd68`) y reordenación `lo<hi`. | bytes + Unicorn (`analysis/s61/e3_chain.py`, sin stubs; entradas SINTÉTICAS). |
| P61-7 | INFERENCIA (debilita H60 de «tiempos») | Los pares se comportan como **límites inferior/superior de 16 bit con margen ±0x400 y reordenación**, no como tiempos: ningún consumidor demostrado los trata como duración. Unidad desconocida (0x400 sugiere Q10, **no probado**). La hipótesis «M = temporización» queda **DEBILITADA, no descartada**. | código de P0; ausencia de consumidor temporal. |
| P61-8 | VERIFICADO (bytes) / INFERENCIA (origen) | 6.º par: `T = *(0x43ea5070)`; el puntero lo fijan `0x437ad3a4` (`T←GOT[0x3d8]=0x43e95cd0`) y `0x437ad3c0` (`T←obj[0x9c]? GOT[0x381c]=0x43e95e10 : 0x43e95cd0`). Índice `idx = (stage[0x17]==0x1a)·9 + (modo−0x0d)·3 + sel`, `sel = 1` si `stage[1]≠0`, si no `2` si `obj8[2]==0` y `0` en otro caso; par = `T[0x36+4·idx], T[0x38+4·idx]`; override por `p[3]+0x15d8/0x15da` si `stage[1]≠0` y (`obj8[0xa]==2` o `p[3][0x15e9]==1`). Los tres bloques de 18 B + 18 pares de `T` coinciden con la entrada **BK4 `0x300AB`** (232 B) y el servicio `+0x27c` (envoltorio `0x435613cc`, llamado como `svc(0,0x300ab,T)`) corresponde por desplazamiento (+0x24 respecto a la relocalización de `liro.ko`) a `Backup_read_setting_attr`: **INFERENCIA**, no verificada la semántica del servicio. | `0x437a5a6c`, REA pseudocódigo, `0x4378ba70..0x4378ba86`, `liro.ko` relocs, `analysis/s55/bk4.py`. |
| P61-9 | VERIFICADO (valores por defecto del paquete) | La entrada BK4 `0x300AB` es **idéntica** en los 5 `CX77500_*.bin`: cabeceras `01×18, 37×18, 00×18` y **18 pares `(0x2EA0, 0x6028)`** = `(11936, 24616)`, resto cero. El 6.º par por defecto es por tanto `(0x2EA0,0x6028)`; valores por unidad (ajuste) pueden diferir. | `ChainEmulation.test_pairs_and_classification`, `SixthPair`. |

## Selección A / B

Verificado: A y B no son alternativas explícitas; escriben el **mismo** bloque desde rutas distintas.

* A: `G[0xD]` bit6==0 (rama de `0x437ab474`, invocada en `0x437ad552` desde un manejador de tabla `0x437ad528`, sin llamadores directos).
* B: `[[p]+0x3a]==1`, tres llamadores: `0x437ac16e` (si `G[0xF]` bit5==1), `0x43aecfea`, `0x43aed068` (secuencias idénticas de refresco de etapa).
* Orden en `0x43aeb2ec`: `0x437ad618 → 0x437ab44c → 0x43aece98` (a y b en secuencias distintas; el orden relativo A→B en una misma captura **no se demuestra**).
* Dependencia de modo: B usa `obj8[3]` acotado a 0x0D..0x0F para elegir el 6.º par; `0x437aa65c` (rama `src+0xb4`) y `0x437a9d30` (cero) son constructores de etapa distintos. Qué constructor atiende a los modos `0x0B/0x2F`: **NO VERIFICADO**.

## Clasificación obligatoria de estados

| Nivel | Qué hay |
|---|---|
| SINTÉTICO | entradas `obj+0x2be..` y `G[0x168/0x16A]` inyectadas. |
| PERMITIDO | `analysis/s61/e3_chain.json`: P0→B con código real, sin stubs, 6.º par con tabla BK4 real → bloque `1108110c3e003f003f0440040034000000050009a02e2860`. |
| ALCANZABLE | **ninguno**: no hay ruta verificada de inicialización/captura que fije `obj+0x2be..`, `G+0x168/16A`, `stage+0x3a` ni `G[0xD]`. |

## Tupla `(modo, M, Tv, clk, N, svr, VdNum, flags, svd, shd, spl)` con procedencia

**No obtenida.** Bloqueantes exactos: (1) escritor de `obj+0x2be..0x2d0` (candidatos con los 9 campos: `0x4383075c`, `0x437f1414`, `0x43ae9e92`, `0x43894524`, `0x438f171c`); (2) escritor de `G+0x168/0x16A` y de `G[0xD]`; (3) qué constructor de etapa (`0x437a9d30` ó `0x437aa65c`) y qué valor de `src+0xb4` gobiernan `stage+0x3a`; (4) vínculo M ↔ Tv/clk: ninguna ruta enlaza los pares con los productores AE (`0x4383d4d0`, `0x4383c9dc`) — **sin evidencia** de que los pares sean entradas de esos productores. No se declara ningún estado alcanzable.

## Límites

REA no reconoce `0x437ab474`, `0x437ad52a`, `0x43b00ed8`, `0x43792a0c`, `0x4379fc9e` (Thumb sin sembrar): se verificaron en bytes. mypy no resuelve los módulos añadidos por `sys.path` (patrón heredado). No hay ejecución en cámara.
