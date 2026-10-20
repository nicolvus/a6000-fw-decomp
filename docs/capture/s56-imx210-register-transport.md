# S56-A — Transporte de registros del IMX210 (20-10-2026)

**Pregunta:** ¿cómo se convierte un parámetro de `SetExposure` en una transacción física? **Resultado:** la cadena queda cerrada hasta la RAM de datos del bloque P2S(DFE0) (`0xfc088340…`). Código: `analysis/s56/{p2s_emu,setexp_emu,rec_users,xr}.py`; tests: `tests/test_s56_imx210_transport.py` (26/26); matriz `analysis/s56-evidence-matrix.json`. Binario: `av-cam.bin` A6000 fw 3.21, SHA `b60c845c…6bb9` (intacto).

## Cadena verificada
```
SetExposure 0x436d6f6c (vtable C_Imager+0x28)      escribe SOLO registros sombra (byte +2 de un registro {u16 id, u8 dato, 0})
  → SetRead 0x436d7e08 / SetMode / deriva de modo 0x436d79c4   idem
  → pulso SSB 0x43ad9116 → [O+0x268]=1 ; Execute 0x436d839c (vtable+0x38 vía 0x43ad911c(img,1))
Execute: 0x436d7c08 (aplica pulso) … consumidor 0x436d75f8
  modo 2 : 0x436d5b74(cfg) ; por registro 0x436d5e04(P,id,dato) ; 0x43ad8dca(flush)    lista 0x43fe995c (119)  → P2S SyncMode 2, espera fin (flag 0x18)
  modo 0 : 0x43ad8d1c ; 0x43ad9004 por registro ; 0x43ad8d38 ; 0x43ad8de4          lista 0x43fe9b50 (8) → carga sin pulso de inicio
  Execute_sleep 0x436d7bc8 → lista 0x43fe9b3c (4: 0x00,0x126,0x127,0x128)
formateador 0x43ad8fa2 → buffer P+0x28 (128 B) → 0x436d5cdc: config bloque (0x436d5e58/5eb0), copia a RAM de datos 0x436d5ed0, pulso 1,0,1 en bloque1+8 (0x436d5f60), IRQ, espera 0x436d5bcc
```
REA (`procedure_pseudo_code 0x436d75f8`, `procedure_callers 0x43ad9116`) coincide con el desensamblado. REA **no** reconoce `0x436d6f6c` (Thumb): verificado por Capstone/emulación.

## A.1 Qué son los IDs
Los 119 punteros de `0x43fe995c` apuntan a registros `{u16 id; u8 dato; u8 0}` (118 IDs distintos, rango `0x000–0x155`; **ID 1 aparece dos veces**: `0x4401ca2c`, `0x4401c734`). **H56-1 verificada con matiz:** no son identificadores opacos: el ID es literalmente la **dirección de 16 bits big-endian** de la trama. Que el sensor (y no el DFE) interprete esa dirección como registro propio es NO VERIFICADO.
Mapa de lo que escribe `SetExposure` (emulado con valores conocidos): palabras u16 `@+4,@+0,@+6` = `svd`, `shd`, `spl` (nombres de la cadena `SetExps: … [svd][shd][spl][shut]`) → IDs `3/4` (svd lo, hi4), `5/6` (shd lo, hi6), `7/8` (spl lo, hi4); espejo condicional (si `[0x4f24+0x7f]!=0xff`) `0x144–0x149`; selector `shut` (byte @+9, 0..4) → bits de ID 1; solo `shut=2` carga `0x100`/`0x101` desde `arg+8/+0x14`.

## A.3 Formato de la transacción (emulación Unicorn del código real)
Objeto P2S (`O+0x298`, ctor `0x43ad8cb2`): `P[0]=0` (sin byte extra), `P[1]=0x10` (dirección 16 bit), `P[2]=8` (dato 8 bit), `P[3]=0x81` (cabecera). Trama: `81 | len | 81 | AH AL | d0 d1…`; registros consecutivos se agrupan (dirección autoincremental, `CheckAddrOrder 0x436d5d9c`); uno no consecutivo abre otra trama. Ej.: ID1=0x40 → `81 04 81 00 01 40`; `0x100=0,0x101=0x38,0x102=0` → `81 06 81 01 00 00 38 00`.
Los 119 registros salen en **2 transmisiones** (127 y 87 B; RAM de 128 B) y la decodificación inversa reproduce exactamente los pares de entrada (**ID lógico → dirección=ID, valor=dato**). Instancia 0 de `C_Imager` → canal 1 (`tabla 0x43bc16d4={1,2,0}`) = **P2S(DFE0)**: bloques `0xfc088300` (cfg `+0x0/4/8/0xc`, RAM `+0x40…`), `0xfc088800` (modo `+0`, disparo `+8`), `0xfc088900`. Canal 0 `0xf3c00300`, canal 2 `0xfc089300`.
SyncMode: 2 → `bloque1+0=2` y pulso 1,0,1 en `+8`; 0 → sin pulso (lista inmediata). Datos preparados en RAM ≠ señal eléctrica: la conversión RAM→SCK/SI/XCS la hace el hardware P2S (fuera del firmware).

## Pulso SSB (nuevo)
`[O+0x268]` ("SSBRK_ON" en `0x43c940d7`) lo pone `0x43ad9116` (5 llamadores: `0x438c7a0a, 0x438c8326, 0x438c883c, 0x438cc5ce, 0x43ae936c`: captura, prelight y StrtExps). `0x436d7c08` hace `A(ID1)|=8; B(ID1)=copia&~8`: **ID1 se envía dos veces en el mismo lote, primero con bit3=1 y luego con 0** (verificado: `0xc4/0xcc → 0xc4`, etc.). Acompaña cambios de modo/exposición; no es específico del fin de exposición.

## Frontera exacta
Falta (1) cómo el bloque P2S serializa la RAM (bits/reloj; hardware), (2) cuál es la semántica de ID1 (bits 2,3,4,6,7), `3–8`, `0x100/0x101` en el IMX210 (sin datasheet), (3) que DFE0 = CIS0 (SCK/SI/XCS): INFERENCIA por nombres. Resultado que avanzaría: traza pasiva de CIS0 decodificable con el formato de arriba.
