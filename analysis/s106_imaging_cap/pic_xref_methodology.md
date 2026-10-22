# Metodología de las referencias a cadenas (esquema PIC) — regla canónica y calibración

> Nota metodológica del hito S106, **actualizada tras S118 y S121**. Es la referencia que
> deben usar los hitos siguientes: qué es una "referencia PIC", por qué el número depende
> de la regla de emparejamiento, cuál es la regla canónica y qué cifras son defendibles.

## 1. El esquema

En este firmware **no hay punteros absolutos** a las cadenas. El código hace:

```
ldr  rX, [pc, #inm]      ; W = desplazamiento guardado en el pool de literales
...
add  rX, pc              ; destino = W + (dirección_de_la_instrucción_add + 4)
```

Verificado con dos casos independientes (S106):

| ldr | pool | W | add | destino |
|---|---|---|---|---|
| `0x437284da` `ldr r3,[pc,#0x2c]` | `0x43728508` | `0x572e4f` | `0x437284e2` | `0x43c9b335` = `[IMAGING_CAP]: EnterCapturing %d` |
| `0x437f5b4a` `ldr.w r3,[pc,#0x954]` | `0x437f64a0` | `0x4b7dea` | `0x437f5b4e` | `0x43cad93c` = `[IMAGING_CAP]: Raw Addr[…]` |

Detalles de decodificación:

- `ldr` de 16 bits (`0x48xx`): literal = `((addr+4) & ~3) + imm*4`, `Rt = (h>>8)&7`.
- `ldr.w` de 32 bits (`0xF8DF`): literal = `((addr+4) & ~3) + imm12`, con
  `imm12 = ((h2>>8)&0xF)<<8 | (h2&0xFF)` y `Rt = h2>>12`.
- `add rX, pc` de 16 bits (`0x44xx`): `Rm = PC` (`(h>>3)&0xF == 15`),
  `Rd = ((h>>7)&1)<<3 | (h&7)`.
- El **PC que se suma es el de la instrucción `add`** (dirección + 4), no el del `ldr`.

## 2. El problema: el registro se reutiliza

Entre el `ldr` y el `add` puede haber código que **vuelva a escribir ese registro**; entonces
el `add` ya no suma el valor que cargó ese `ldr`. De ahí que el emparejamiento sea ambiguo y
que **el número de referencias dependa de la regla**:

| regla | qué hace | sesgo | script |
|---|---|---|---|
| **estricta** *(canónica)* | empareja cada `add` con el `ldr` **más cercano** del mismo registro (ventana 4 KB) | puede **perder** referencias (cuando el `ldr` válido no es el más cercano) | `analysis/s106_imaging_cap/scan_pic_refs_strict.py` |
| kill analysis | como la anterior, pero descarta el par si alguien escribe el registro entre `ldr` y `add` | con la implementación **corregida** (ver §3.1) coincide con la estricta en el conjunto de cadenas y en los sitios verificados | `analysis/s106_imaging_cap/scan_pic_refs_v2.py` |
| **ancha** | prueba **todos** los `ldr` del registro en 4 KB | **inventa** referencias | `analysis/s106_imaging_cap/scan_pic_refs.py` (v1) |

### 3.1 Un bug de la kill analysis (encontrado por S120) y su corrección

`scan_pic_refs_v2.py` **no mataba nada**: no tenía `md.detail = True` (con `detail` apagado,
`ins.operands` lanza `CsError` y la función devolvía siempre `False`) y además mapeaba los
registros con `op.reg & 0xF`, que en Capstone es inválido (`ARM_REG_R0 = 66`, así que
`& 0xF` confunde r1 con r3). Corregido (detail activado + mapeo explícito
`_reg_index`), la kill analysis da:

| módulo | cadenas | referenciadas (estricta) | referenciadas (kill corregida) | sitios (kill corregida) |
|---|---|---|---|---|
| `[IMAGING_CAP]` | 697 | 690 | 690 | 996 |
| `[CAMERA_MAIN_YC]` | 968 | 954 | 954 | 1 090 |
| `[SFRA]` | 100 | 100 | 100 | **118** (= verdad medida a mano) |
| `[AIP]` | 37 | 37 | 37 | **37** (= verdad medida a mano) |
| `[TRK]` | 215 | 213 | 213 | **288** (= recuento del subagente) |
| `[IDT_OPD]` | 273 | 271 | 271 | 356 |

→ **la kill analysis corregida coincide con la regla estricta** en el conjunto de cadenas
referenciadas y en los recuentos de sitios de los módulos con verdad medida; lo que hace es
**eliminar los sitios falsos** de las reglas más laxas (327 en `[IDT_OPD]`). La regla canónica
sigue siendo la estricta por simplicidad, y la kill analysis corregida queda como la
herramienta de **auditoría** (cuántos sitios son espurios).

## 3. Calibración con dos casos verificados a mano

S118 verificó **a mano** (desensamblando) los puntos de emisión de `[SFRA]`; S121 hizo lo
mismo con `[AIP]` y además cuantificó los falsos positivos de la kill analysis:

| módulo | **real (verificado a mano)** | estricta | kill analysis | ancha |
|---|---|---|---|---|
| `[SFRA]` (100 cadenas) | **118 sitios, 47 funciones** | 118 ✓ | 166 | 186 |
| `[AIP]` (37 cadenas) | **37 sitios, 16 funciones** | 37 ✓ | 60 (23 falsos) | — |

→ **la regla estricta coincide con la verdad medida en los dos módulos donde se verificó a
mano**; las otras dos reglas se quedan **por encima** (falsos positivos). Por eso la regla
canónica del repo es la **estricta**, y por eso **ningún informe debe publicar un número de
sitios sin indicar la regla usada**.

## 4. Cifras corregidas de los hitos publicados

Con la regla estricta (canónica) sobre el mapa global de 17 525 destinos:

| hito | cifra publicada | cifra canónica (estricta) | nota |
|---|---|---|---|
| **S106** `[IMAGING_CAP]` | 695/697 (kill) | **690/697 referenciadas, 7 sin referencia** | las 7: `0x43ca05d7`, `0x43ca0603`, `0x43ca069a`, `0x43ca06c6` (DistV/DistH), `0x43ca9b12`, `0x43cc7d5c`, `0x43cc839c`; ninguna tiene puntero absoluto de 4 B en los 11,4 MB |
| **S110** `[CAMERA_MAIN_YC]` | 958/968 (kill), 304 funciones | **954/968 referenciadas**, 251 funciones con la regla estricta (las 970 son *ocurrencias* del prefijo, no cadenas distintas) | |
| **S113** `[CAM_DMM]` | 54 cadenas, 21 funciones (kill) | 54 cadenas, **54 sitios, 14 funciones** (estricta) | |
| **S115** `[CAM_IMAGER]` | 371 cadenas, 90 funciones (kill) | 371 cadenas, 357 referenciadas, **417 sitios, 76 funciones** (estricta) | |
| S111 `[TRK]` | 215 cadenas, 288 sitios, 47 funciones | **coincide** (el subagente ya usaba la regla estricta) | |
| S112 `[CAMERA_MAIN_SYNC]` | 429 cadenas, 430 funciones, 1 407 pares | 428 cadenas, 425 referenciadas, 489 sitios (estricta) | las 429 cadenas y el diferencial (418/429) no cambian |
| S116 `[SFRS]` | 117 cadenas, 131 sitios, 52 funciones | 117 cadenas, 111 referenciadas, 125 sitios (estricta) | el subagente verificó 131 a mano |
| S118 `[SFRA]` | 118 sitios, 47 funciones | **coincide** (verificado a mano) | |
| S121 `[AIP]` | 37 sitios, 16 funciones | **coincide** (verificado a mano) | |

**Lo que no cambia** con ninguna regla: el **número de cadenas** de cada módulo, su rango, el
**diferencial A7S/A6300** y las conclusiones estructurales (tablas, clases, ficheros fuente,
secuencias de comandos, decodificaciones de ids).

## 5. Regla que se usa a partir de ahora

1. Para un **hito de módulo**: se publica el número de cadenas, el rango y el diferencial
   A7S/A6300 (datos exactos) y el **mapa función→traza** calculado con
   `scan_pic_refs_strict.py`, indicando en el informe la regla usada.
2. Para una **cifra puntual** ("estas 2 cadenas están muertas", "este sitio referencia esta
   cadena"): se **verifica a mano** desensamblando, como en S118 y S121.
3. El **escáner canónico** es `analysis/s106_imaging_cap/scan_pic_refs_strict.py`
   (acepta `LO HI RUTA_SALIDA`; el rango de cadenas válidas cubre toda la imagen).
   `scan_pic_refs_v2.py` (kill analysis) y `scan_pic_refs.py` (v1, ancha) quedan como
   referencias históricas y para Auditorías de falsos positivos.
4. Ningún informe debe afirmar "N sitios" sin decir la regla.

## 6. Reproducir

```bash
# mapa global con la regla canónica (≈7 s, 17 525 destinos)
.venv/bin/python analysis/s106_imaging_cap/scan_pic_refs_strict.py 0x43541000 0x44017000 /tmp/pic_strict.json
# auditoría: cuántos pares sobreviven con kill analysis y cuántos con la regla ancha
.venv/bin/python analysis/s106_imaging_cap/scan_pic_refs_v2.py 0x43541000 0x44017000 /tmp/pic_v2.json
```
