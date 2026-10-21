# Metodología de las referencias a cadenas (esquema PIC) — y qué regla usar

> Nota metodológica del hito S106/S110, **actualizada tras S118**. Es la referencia que
> deben usar los hitos siguientes: qué es una "referencia PIC", por qué el número depende
> de la regla de emparejamiento, y qué cifras son defendibles.

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

Entre el `ldr` y el `add` puede haber código que **vuelva a escribir ese registro**. Entonces
el `add` ya no suma el valor que cargó ese `ldr`, sino otro. De ahí que **la regla de
emparejamiento**:

| regla | qué hace | sesgo | script |
|---|---|---|---|
| **estricta** | empareja cada `add` con el `ldr` **más cercano** del mismo registro | pierde referencias (cuando el `ldr` válido no es el más cercano) | `analysis/s111_trk/scan_refs.py` |
| **ancha** | prueba **todos** los `ldr` del registro en 4 KB | **inventa** referencias (68 falsos positivos en `[SFRA]`) | `analysis/s106_imaging_cap/scan_pic_refs.py` (v1) |
| **kill analysis** | como la ancha, pero descarta el par si **alguien escribe el registro** entre `ldr` y `add` | mejora, pero sigue having falsos positivos donde el barrido lineal se desincroniza en zonas de datos | `analysis/s106_imaging_cap/scan_pic_refs_v2.py` |

## 3. Calibración con un caso verificado a mano

S118 verificó **a mano** (desensamblando) los puntos de emisión de `[SFRA]`:

| regla | puntos de referencia en `[SFRA]` (100 cadenas) |
|---|---|
| **real (verificado a mano)** | **118** |
| estricta | 118 |
| kill analysis (v2) | 166 |
| ancha (v1) | 186 |

→ la regla estricta acierta en este módulo, la kill analysis se queda a 48 por encima y la
ancha a 68. **Los recuentos de sitios no son publicables sin verificación manual**; los
*cadenas con al menos una referencia* sí lo son, comprobando un sitio.

## 4. Cifras corregidas de los hitos publicados

Aplicando la kill analysis a los módulos ya publicados (y verificando a mano los dos casos
disputados):

| hito | cifra publicada | cifra corregida | nota |
|---|---|---|---|
| **S106** `[IMAGING_CAP]` | 696/697 referenciadas, 1 cadena muerta | **695/697 referenciadas, 2 sin referencia confirmada** (`0x43ca9b12` `ShareMem_StlRaw8 Err…` y `0x43cc839c` `Rch_Rcv_Zima_Base Err…`; ninguna tiene puntero absoluto de 4 B en los 11,4 MB) | la "corrección" de S110 (694→696) estaba basada en la regla ancha: los dos sitios que añadía son **falsos** (el `add` de `0x43785d18` materializa `[IMAGING_CAP]: PreProcessRC: Release_RC error` `0x43ca03e0`, no la cadena que se le atribuía) |
| **S110** `[CAMERA_MAIN_YC]` | 960 de 970 referenciadas | **958 de 968 cadenas** (970 son *ocurrencias* del prefijo; 968 cadenas distintas) | |
| S111 `[TRK]` | 288 sitios (estricta) | el recuento de sitios es **dependiente de la regla** (estricta 288, kill 515, ancha 657) | las **215 cadenas** y el diferencial A7S (idénticos) no cambian |
| S112 `[CAMERA_MAIN_SYNC]` | 430 funciones / 1 407 pares | **330 funciones / 1 122 pares** (kill) | las 429 cadenas y el diferencial (418/429) no cambian |
| S113 `[CAM_DMM]` | 25 funciones | **21 funciones** (kill) | las 54 cadenas y el diferencial no cambian |
| S115 `[CAM_IMAGER]` | 94 funciones | **90 funciones** (kill) | las 371 cadenas y el diferencial no cambian |
| S116 `[SFRS]` | 131 sitios / 52 funciones | 136 / 57 (kill) | verificado a mano por el subagente: 131 sitios |
| S118 `[SFRA]` | 118 sitios / 47 funciones | **118 / 47** (verificado a mano) | |

**Lo que no cambia**: el número de cadenas de cada módulo, su rango, el diferencial A7S/A6300 y
las conclusiones estructurales (tablas, clases, ficheros fuente, secuencias de comandos).

## 5. Regla que se usa a partir de ahora

1. Para un **hito de módulo**: se publica el número de cadenas, el rango y el diferencial
   A7S/A6300 (datos exactos), y el **mapa función→traza** con la regla *kill analysis*
   (`scan_pic_refs_v2.py`), indicando en el informe que el recuento de sitios es heurístico.
2. Para una **cifra puntual** (p. ej. "estas 2 cadenas están muertas", "este sitio referencia
   esta cadena"): se **verifica a mano** desensamblando, como en S118.
3. El **escáner compartido** es `scan_pic_refs_v2.py` (acepta `LO HI RUTA_SALIDA`; el rango de
   cadenas válidas cubre toda la imagen). La v1 queda como referencia histórica.
4. Ningún informe debe afirmar "N sitios" sin indicar la regla usada.

## 6. Reproducir

```bash
# mapa global (≈6 min, 73 336 destinos)
.venv/bin/python analysis/s106_imaging_cap/scan_pic_refs_v2.py 0x43541000 0x44017000 /tmp/pic_v2.json
# mapa por módulo (ejemplo)
.venv/bin/python - <<'PY'
import json,re
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
v2={int(k,16):v for k,v in json.load(open("/tmp/pic_v2.json")).items()}
for m in re.finditer(rb"[\x20-\x7e]+", B):
    t=m.group().decode("latin1")
    if t.startswith("[IMAGING_CAP]") and (BASE+m.start()) in v2:
        pass
PY
```
