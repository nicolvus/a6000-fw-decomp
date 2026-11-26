# G22-PBVISTA — el registro de vistas y el cargador bajo demanda (`viewUnified2.so` + `libObj.so`)

**Estado (26-11-2026, sesión G22-PBVISTA, sin cámara): el cargador está IDENTIFICADO y MEDIDO; no es el eslabón que
falta.** La vista de reproducción **sí** se instancia y **sí** se carga su módulo bajo demanda: con
`O view/INDEX_PLAYBACK 0` el invitado llama `dlopen(viewUnified3.so)` (handle válido), abre `Vn 03F_viewUnified3.so`
y ejecuta su constructor `ViewIndexPbToInstance` (VERIFICADO, §6). Lo que falta para que **se pinte** es el **modelo
de contenidos**: en la misma apertura la vista pide `getModelInfo(@M00A = model/MEDIA, 0) -> 0` y `…, 64) -> 0`
(VERIFICADO) mientras `model/ROOT, 6 -> 1` sí responde, y la SD emulada usada **no tiene un solo fichero**
(`/tmp/final/sd/DCIM/100MSDCF` vacío y sin `AVF_INFO/`; VERIFICADO). Que ese 0 sea *consecuencia* de la tarjeta vacía
es INFERENCIA (§7). Resultado en pantalla: 0 listas, 0,0 % de píxeles opacos y 0,29 % de píxeles distintos frente al
fotograma anterior (el ruido del fotograma fijo): no hay repintado, medido.

Además, esta sesión **corrige una premisa del repo**: la zona `.rodata 0x391a18…0x3a2bea` de `viewUnified2.so` **no**
es una tabla de tripletes `{view/NOMBRE, viewX.so, ViewXToInstance}`; es un **pozo de cadenas ordenado** en el que la
vecindad de tres cadenas no significa nada, y `viewIndexPb.so` (vecino de `view/INDEX_PLAYBACK`) **no existe** en el
`/usr/lib` de la cámara. El registro se construye **en código**, en dos pasadas, y la segunda lo sobrescribe con el
bundle que sí existe. Ver §2 y §3.

§1–§5 son estáticos (`readelf`/`capstone` sobre los ELF 3.21 que el arnés copia en
`analysis/gui/g22/harness/stage/cam/usr/lib`; en estos ficheros VA = desplazamiento de fichero). §6–§8 son medidos en
el invitado con `qemu-system-arm` y `scripts/gui/harness/live.py`, sin cámara. Evidencia:
`reports/evidence/g22-pbvista-20261126/`.

---

## 1. Qué NO es la tabla (la premisa que había que tirar)

`docs/PENDIENTES.md` (fila G22-REPRO) y `tests/test_g22_repro.py` describían «la tabla del `ViewManager` (tripletes
`nombre de vista, biblioteca, símbolo` en `.rodata`)». Los bytes dicen otra cosa:

| comprobación | resultado |
|---|---|
| ¿hay algún puntero de 4 B a `view/INDEX_PLAYBACK` (`0x3a14c1`)? | **no** (0 apariciones en todo el fichero) |
| ¿a `viewIndexPb.so` (`0x3a14d5`)? | **no** (0) |
| ¿a `ViewIndexPbToInstance` (`0x3a14e4`)? | **no** (0) |
| ¿a la lista de bundles (`0x3a2b8a`)? | **no** (0) |

Y el pozo está **ordenado por nombre de clase**, no por tripletes: alrededor de la entrada de reproducción se lee

```
3a1466 view/GROUP_SELECTION_FOLDER
3a1482 viewGroupSelectionFolder.so
3a149e ViewGroupSelectionFolderToInstance
3a14c1 view/INDEX_PLAYBACK            <- el nombre de vista cae ENTRE el módulo anterior y el suyo
3a14d5 viewIndexPb.so                 <- módulo de ANTES de la fusión: no existe en /usr/lib
3a14e4 ViewIndexPbToInstance
3a1500 viewInitialSetting.so
3a151d ViewInitialSettingToInstance
3a1530 view/IREDIT
3a153d viewIREditOne.so
3a1555 ViewIREditOneToInstance
```

Es decir: `view/INDEX_PLAYBACK` está *entre* `ViewGroupSelectionFolderToInstance` y `viewIndexPb.so` porque el pozo va
ordenado por la clave lógica (el nombre de clase), no porque forme un triplete con sus vecinos. `./usr/lib` de la
cámara 3.21 sólo tiene `viewUnified2.so … viewUnified8.so` (**no** hay `viewIndexPb.so`, ni `viewSinglePb.so`, ni
ninguno de los ~240 módulos que cita el pozo): el build fusionó los módulos y el pozo conserva los nombres viejos.

## 2. Dónde está el registro de verdad: una función que llama a `IdSoTable::add`

El registro son **dos cadenas de código** dentro de una única función Thumb cuya entrada está en `.ARM.exidx`:
**`viewUnified2+0x194844`** (`cmp r2,#1` + `push.w {r4-r11,lr}`; con `r2 == 1` salta a `+0x1960e8`, la segunda
pasada). Cada entrada es el idioma PIC del firmware, `ldr rX,[pc,#imm]` + `add rX, pc`, seguido de dos llamadas:

```asm
; entrada típica (view/INDEX_PLAYBACK, 2.ª pasada)
196780  ldr.w r0,[pc,#0x880]      ; slot 0x197004 = 0x0020ad39
196784  add   r0, pc              ; r0 = 0x3a14c1  "view/INDEX_PLAYBACK"
196786  blx   0xe71b8             ; IdGenerator::Get(nombre)  -> id (int)
19678a  ldr.w r3,[pc,#0x87c]      ; slot 0x197008 = 0x0020ad50
19678e  mov   r2, sb              ; r2 = bundle (registro cargado en el prólogo de la pasada)
196790  add   r3, pc              ; r3 = 0x3a14e4  "ViewIndexPbToInstance"
196792  mov   r1, r0              ; r1 = id
196794  mov   r0, r4              ; r0 = ViewIdSoTable::getInstance()
196796  blx   0xe5b4c             ; IdSoTable::add(id, "<modulo>.so", "<Clase>ToInstance")
```

Símbolos (tabla dinámica): `IdGenerator::Get(char const*)` → PLT `0xe71b8` de `viewUnified2.so`;
`IdSoTable::add(int, char const*, char const*)` → PLT `0xe5b4c`; `ViewIdSoTable`/`ModelIdSoTable` son **clases de
`libObj.so`** (`_ZN13ViewIdSoTable11getInstanceEv`, `_ZN14ModelIdSoTable11getInstanceEv`, `_ZN9IdSoTable3addEiPKcS1_`)
y `viewUnified2.so` las importa. Volcado de las 278 entradas que se pueden leer con un barrido lineal (154 de la 1.ª pasada y 124 de la 2.ª; el barrido de la 2.ª se corta en `view/SETTINGMENUX` porque el compilador intercala un pozo de literales en medio del código y desalinea el desensamblado, así que el número real de entradas de la 2.ª pasada es mayor):
`reports/evidence/g22-pbvista-20261126/registro-vistas-estatico.txt`.

**Ojo con la aritmética**: para `add rX, pc` (Thumb, ADD de registro con PC) el PC vale **dirección + 4 sin alinear**;
con la base alineada a 4 los literales de `sb`/`sl`/`r8` del prólogo caen 2 B antes y devuelven la cola de la cadena
anterior (`'o'`, el último carácter de `viewUnified8.so`). Es la trampa que hace que un barrido ingenuo «vea» módulos
equivocados; está fijada en `tests/test_g22_pbvista.py::_pool_target`.

## 3. Las dos pasadas: el módulo de fábrica y el bundle que existe

| pasada | sitio | nombre | módulo | constructor |
|---|---|---|---|---|
| 1.ª | `viewUnified2+0x194fdc` | `view/INDEX_PLAYBACK` | `viewIndexPb.so` (**no existe**) | `ViewIndexPbToInstance` |
| 2.ª | `viewUnified2+0x196796` | `view/INDEX_PLAYBACK` | **`viewUnified3.so`** | `ViewIndexPbToInstance` |
| 1.ª | `viewUnified2+0x195cd4` | `view/SINGLEPB` | `viewSinglePb.so` (**no existe**) | `ViewSinglePbToInstance` |
| medida | invitado, §6 | `view/SINGLEPB` | **`viewUnified2.so`** | — |

La 1.ª pasada registra 154 vistas con el nombre *de antes de la fusión*; la 2.ª vuelve a llamar a `IdSoTable::add`
con **el mismo id** y el bundle que de verdad está en `/usr/lib`, de modo que el segundo `add` **sobrescribe** al
primero. El prólogo de la 2.ª pasada carga los siete bundles en registros, en el mismo orden que la lista de
`.rodata`:

```asm
1960e8  ldr.w r0,[pc,#0xd00]   ; slot 0x196dec = 0x0020a3d4 -> 0x3a04c8 "view/_KKILLALL"   (primera entrada)
1960ec  ldr.w sb,[pc,#0xd00]   ; slot 0x196df0 = 0x0020ca98 -> 0x3a2b9a "viewUnified3.so"
1960f0  add   r0, pc
1960f2  ldr.w r5,[pc,#0xd00]   ; slot 0x196df4 = 0x0020caa6 -> 0x3a2baa "viewUnified4.so"
1960f6  blx   0xe71b8
1960fa  ldr.w r3,[pc,#0xcfc]   ; slot 0x196df8 = 0x0020ca84 -> 0x3a2b8a "viewUnified8.so"
1960fe  add   sb, pc
196100  add   r5, pc
196102  add   r3, pc
...
19610c  ldr.w sl,[pc,#0xcf0]   ; -> 0x3a2bba "viewUnified7.so"
196112  ldr.w fp,[pc,#0xcf0]   ; -> 0x3a2bca "viewUnified6.so"
196118  ldr.w r8,[pc,#0xcec]   ; -> 0x3a2bda "viewUnified2.so"
19611e  ldr.w r6,[pc,#0xcec]   ; -> 0x3a2bea "viewUnified5.so"
```

y la lista de `.rodata` (7 nombres, **16 B de paso**, el orden 8-3-4-7-6-2-5 de arriba):

```
3a2b8a viewUnified8.so \0   3a2b9a viewUnified3.so \0   3a2baa viewUnified4.so \0   3a2bba viewUnified7.so \0
3a2bca viewUnified6.so \0   3a2bda viewUnified2.so \0   3a2bea viewUnified5.so \0
```

(La fila `viewUnified5.so` ocupa `0x3a2bea…0x3a2bf9`: el final que citaba el encargo, `0x3a2bea`, es el **principio**
del último nombre, no el final de la lista.)

## 4. Quién hace el `dlopen`: el cargador por vista de `libObj.so`

`viewUnified2.so` **no llama a `dlopen`**: importa `dlopen`/`dlsym`/`dlclose` pero **ningún** `bl`/`blx` de su `.text`
apunta a esos *stubs* (0 de 4500 `bl` ARM y 0 de 3054 `blx` Thumb; comprobado también con la tabla `.rel.plt`). El
`dlopen` lo hace `libObj.so`, en el método de carga de la ficha de una vista (`this`):

```asm
7f11ca  push {r4,r7,lr} · sub sp,#0xc · mov r4,r0 · add r7,sp,#8
7f11d2  movw  r1,#0x101          ; 40 f2 01 11  = RTLD_LAZY(1) | RTLD_GLOBAL(0x100)
7f11d6  ldr   r0,[r0,#0x10]      ; 00 69        = this-><nombre del módulo>
7f11d8  blx   dlopen@plt         ; 40 f4 88 e5
7f11dc  str   r0,[r4,#0x18]      ; a0 61        = this-><handle>
7f11de  cmp   r0,#0 · beq 0x7f1238
7f11e2  ldr   r1,[r4,#0x14]      ; this-><símbolo constructor, p.ej. "ViewIndexPbToInstance">
7f11e6  blx   dlsym@plt          ; ee f4 74 e6
7f11ea  mov r3,r0 · cbz r0,0x7f1238
7f11ee  ldr   r0,[r4,#0]         ; argumento 1 del constructor
7f11f0  ldr   r1,[r4,#0x20]      ; argumento 2
7f11f2  blx   r3                 ; ViewXxxToInstance(...)
7f11f4  str   r0,[r4,#0x1c]      ; this-><instancia>
```

Layout de la ficha: `+0x00`/`+0x04` argumentos, `+0x10` **nombre del módulo**, `+0x14` **símbolo del constructor**,
`+0x18` handle de `dlopen`, `+0x1c` instancia, `+0x20` parámetros. Si el `dlopen` o el `dlsym` fallan, el método
devuelve `-1` (`0x7f123e`) y llama a su ruta de error (`0x7f117a`, que cierra el handle). Hay un segundo cargador
mínimo, `DlModule`-like, en `libObj+0x7e1ff6`: `dlopen(nombre, 1)` con el nombre en su primer argumento.

## 5. La condición que dispara la carga

**No es un modo ni una variable global: es la apertura de una vista cuyo id tiene ficha en `IdSoTable`.** La cadena
completa, con lo medido:

```
tecla / orden anfitrión
   └─ viewManagerIf::openView("view/INDEX_PLAYBACK", modo)      libObj+0x1251fd (thunk) -> libObj+0xdc3a4
        └─ ViewIdSoTable::getInstance()->find(id)              libObj+0x7f22d1 (singleton)
             └─ ficha de la vista: {+0x10 = "viewUnified3.so", +0x14 = "ViewIndexPbToInstance"}
                  └─ libObj+0x7f11ca: dlopen("viewUnified3.so", 0x101) -> dlsym -> ctor  [MEDIDO, §6]
```

En el arranque del arnés **sí** se cargan módulos de vista por esta vía en cuanto la UI abre vistas que no viven en
`viewUnified2.so` (la vista de disparo). Medido en el perfil `pbv2`: `dlopen(viewUnified2.so)` (varias veces),
`dlopen(viewUnified8.so)` y, al abrir reproducción, `dlopen(viewUnified3.so)`. Lo que **no** hace falta es ningún
interruptor nuevo del shim: no se ha añadido ninguno porque el cargador ya dispara (ver §6 y §9).

## 6. Medido en el invitado (perfil `pbv2`, puerto 8692)

```sh
SHIMEXTRA='SETLOG=1 WAITLOG=3000 WLALL=1' \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir pbv2 --puerto 8692 --config /tmp/final/cfg.json
# ... 234 s: 2 fotogramas, 2 listas, opacos 0.0046 (ver §8: el arranque no llega a la OSD)
.venv/bin/python scripts/gui/harness/e2e_drv.py 8692 "linea=E GMILOG=1" \
  "linea=O view/INDEX_PLAYBACK 0" esp=8 png=/tmp/pbv/02-index.png esp=2 \
  "linea=O view/SINGLEPB 0" esp=6 png=/tmp/pbv/03-single.png esp=2
```

Traza del invitado (`shim.log`, extracto en `reports/evidence/g22-pbvista-20261126/pbv2-trazas.txt`):

```
668.96 OPENHOT view/INDEX_PLAYBACK 0 -> 5688664
668.98 dlopen(viewUnified3.so) ...              <- el cargador bajo demanda, disparado por la vista
668.99 dlopen(viewUnified3.so) -> 0x55a67460
668.97 LOG   83 B  Vn 03F_viewUnified3.so       <- vista 0x3F instanciada DESDE el bundle
669.05 dlopen(viewUnified2.so) ...              <- view/ROOT (0x11) ya estaba: reutiliza handle
669.05 LOG   83 B  Vn 011_viewUnified2.so
669.06 LOG   83 B  Vo 0000003B                  <- capa de la vista de disparo
671.00 OPENHOT view/SINGLEPB 0 -> 5688664
671.00 dlopen(viewUnified2.so) -> 0x523930
671.00 LOG   83 B  Vn 080_viewUnified2.so       <- 0x80 = SINGLEPB, en viewUnified2.so
671.02 LOG   83 B  Vo 00000015 / 671.35 Vo 0000003C
```

Y lo que la vista **pide** al modelo en esa misma apertura (`GMILOG=1`):

```
getModelInfo(@M00A, 0) -> 0            <- model/MEDIA: SIN CONTENIDOS
getModelInfo(model/MEDIA, 0) -> 0
getModelInfo(@M00A, 64) -> 0
getModelInfo(model/ROOT, 6) -> 1       <- el modelo de raíz SÍ responde
```

Estado de `/estado` antes y después y comparación de PNG (RGBA 640×480, canal R):

| fichero | píxeles distintos vs `00-antes.png` |
|---|---|
| `01-tras-abrir.png` | 900 px = **0,29 %** |
| `02-index.png` (tras `O view/INDEX_PLAYBACK 0`) | 900 px = **0,29 %** |
| `03-single.png` (tras `O view/SINGLEPB 0`) | 900 px = **0,29 %** |

`/estado`: antes `{"fotogramas":2,"listas":2,"opacos":0.0046}`; después
`{"fotogramas":7,"listas":0,"listas_total":12,"opacos":0.0}` — la vista **sustituye** la pantalla por una vacía.
El 0,29 % es el ruido del fotograma fijo, no un repintado.

## 7. El modelo y la SD: el eslabón que falta para pintar

- La vista **no** pide `model/INDEX_PLAYBACK`: pide **`@M00A` (= `model/MEDIA`)** con las informaciones `0` y `64`, y
  `model/ROOT` con la `6`. `@M00A` es el nombre corto del modelo de medios (`ModelMediaToInstance` =
  `libObj+0x5d8d95`; el `ObjMedia` se arranca en `EE START` con `dlsym(Init)/dlsym(Create) : ObjMedia`).
- `model/MEDIA` devuelve **0** (VERIFICADO). **INFERENCIA**: sin lista de contenidos no hay rejilla ni miniatura que
  dibujar, y de ahí 0 listas y 0 % opaco. Lo que sí está verificado es que la capa de la vista **sí** se crea para
  `view/SINGLEPB` (`Vo 00000015`, `Vo 0000003C`) y **no** para `view/INDEX_PLAYBACK` (entre `Vn 03F` y `Vn 011` no hay
  ningún `Vo` de la 0x3F): el corte está en el contenido, no en el cargador ni en el gestor de vistas.
- La SD emulada que se usó (`/tmp/final/sd`, la del arnés) **no tiene un solo fichero**:
  `DCIM/100MSDCF/` vacío, `PRIVATE/M4ROOT/CLIP/` vacío y **no existe `AVF_INFO/`** (`AVIN0001.INP`, `BNP`, `INT`,
  `PRV00001.BIN`, `STAT0000.BIN`). Con esa tarjeta el modelo de medios no puede enumerar nada.
- Esto coincide con lo ya anotado en G22-REPRO («el recuento no sale numérico con `ERROR` de tarjeta») y con
  FILM-PB-1-SUB-LISTA-CONT: el emisor real de la lista es
  `MprIf::GetAVIndexContentInfoList` (`libmpr+0x7203c0`) a través de `libInfraScalarMpr.so`, y lo que falta son las
  **entradas del índice** de la tarjeta, no el cargador de la vista.

Conclusión operativa: **el camino estable del arnés para la vista de reproducción ya existe** (`O view/INDEX_PLAYBACK`
→ `dlopen(viewUnified3.so` → `ViewIndexPbToInstance`), y el siguiente eslabón es **`model/MEDIA` con contenido**
(una SD con `DCIM/100MSDCF/DSCnnnnn.JPG` real más el índice `AVF_INFO/*.INP` que la cámara sepa leer).

## 8. Límite de esta sesión: el arranque no llegó a la OSD

Dos arranques en frío (`pbvista`/8691 con `WAITLOG=3000 WLALL=1` y `pbv2`/8692 con `SETLOG=1 WAITLOG=3000 WLALL=1`)
se quedaron en el fotograma de **2 listas / opacos 0,0046**, que es exactamente la firma del cuelgue de arranque ya
abierto en el repo (G22-CUELGUE, [`g22-cuelgue-navegacion.md`](g22-cuelgue-navegacion.md)). Por eso la medición de
§6 se hizo **sin OSD**: sirve para el cargador y para el modelo (que son independientes del repintado de la pantalla
de disparo) y **no** demuestra que la rejilla se pinte, porque no hay contenido que pintar. La ventana de la
comparación de PNG es la del fotograma vacío, no la de la OSD.

## 9. Por qué no se añade ningún interruptor al shim

El encargo preveía un `PBVIEW=1` que hiciera el `dlopen` del módulo o llamara al cargador antes de `openView`. No
hace falta y no se ha añadido: **el cargador ya dispara solo** en cuanto se pide la vista (§6, `dlopen(viewUnified3.so)`
después de `O view/INDEX_PLAYBACK 0`, con handle válido y constructor ejecutado). Un interruptor que repitiera ese
`dlopen` sólo añadiría una vía paralela a la del firmware, con el riesgo de que el arnés dejara de probar el camino
real. Lo que sí queda fijado en tests es la **estructura** que hace falta para que ese camino no se rompa (§10).

## 10. Tests sin QEMU

`tests/test_g22_pbvista.py` (8 casos, se saltan si faltan los binarios del arnés):

1. la lista de los siete bundles en `.rodata 0x3a2b8a`, de 16 en 16 y en el orden 8-3-4-7-6-2-5;
2. **no hay punteros** a las cadenas del pozo (ni a `view/INDEX_PLAYBACK`, ni a su módulo, ni a su constructor, ni a la
   lista de bundles): si alguien vuelve a introducir una tabla de punteros, el test lo dice;
3. la entrada de la 1.ª pasada (`+0x194fdc`) es `view/INDEX_PLAYBACK → viewIndexPb.so / ViewIndexPbToInstance` y ese
   `.so` no está en `/usr/lib`;
4. la de la 2.ª pasada (`+0x196796`) es `view/INDEX_PLAYBACK → viewUnified3.so / ViewIndexPbToInstance`;
5. el prólogo de la 2.ª pasada carga `sb=viewUnified3.so`, `r5=viewUnified4.so`, `fp=viewUnified6.so`,
   `r6=viewUnified5.so`, y el aritmética del `add rX, pc` es la de `dirección+4` sin alinear;
6. la función de registro es una sola (entrada de `.ARM.exidx` `0x194844`) y llama a las dos PLT del registro
   (`IdGenerator::Get` `0xe71b8`, `IdSoTable::add` `0xe5b4c`);
7. el cargador de `libObj+0x7f11ca`: `ldr r0,[r0,#0x10]` + `movw r1,#0x101` + `blx dlopen@plt`, handle en `+0x18`,
   `dlsym` del constructor en `+0x14`, instancia en `+0x1c`;
8. `ViewIndexPbToInstance` la **exporta** `viewUnified3.so` y **no** `viewUnified2.so` (que sólo tiene la cadena en el
   pozo, sin símbolo).

## 11. Comandos reproducibles

```sh
# estático: volcado de las entradas del registro (sitio, nombre, módulo, constructor)
cd analysis/gui/g22/harness/stage/cam/usr/lib && \
  python3 - <<'PY'
import struct, capstone
d = open('viewUnified2.so','rb').read(); md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
def s_at(t):
    e = d.find(b'\0', t); b = d[t:e]
    return b.decode() if b and all(32 <= c < 127 for c in b) and e-t < 100 else None
def scan(lo, hi):
    regs, vals, out = {}, {}, []
    for i in md.disasm(d[lo:hi], lo):
        if i.mnemonic.startswith('ldr') and '[pc,' in i.op_str:
            imm = int(i.op_str.split('#')[-1].rstrip(']'), 16); rt = i.op_str.split(',')[0].strip()
            regs[rt] = struct.unpack_from('<I', d, ((i.address+4) & ~3) + imm)[0]
        elif i.mnemonic == 'add' and i.op_str.endswith(', pc'):
            rd = i.op_str.split(',')[0].strip()
            if rd in regs: vals[rd] = s_at((regs[rd] + i.address + 4) & 0xffffffff)   # PC = dir+4, SIN alinear
        elif i.mnemonic in ('mov','movs') and ',' in i.op_str:
            p = [x.strip() for x in i.op_str.split(',')]
            if len(p) == 2 and p[1] in vals: vals[p[0]] = vals[p[1]]
        if i.mnemonic == 'blx' and i.op_str.strip() == '#0xe5b4c':
            out.append((i.address, vals.get('r0'), vals.get('r2'), vals.get('r3')))
    return out
for a, n, m, c in scan(0x194844, 0x198000):
    if n: print(f'{a:#08x} {n:32s} | {m} | {c}')
PY

# dinámico (sin cámara): dos arranques en frío + apertura de las dos vistas de reproducción
SHIMEXTRA='SETLOG=1 WAITLOG=3000 WLALL=1' .venv/bin/python scripts/gui/harness/live.py \
  analysis/gui/g22/harness --perfil-dir pbv2 --puerto 8692 --config /tmp/final/cfg.json
.venv/bin/python scripts/gui/harness/e2e_drv.py 8692 "linea=E GMILOG=1" \
  "linea=O view/INDEX_PLAYBACK 0" esp=8 png=/tmp/pbv/02-index.png esp=2 \
  "linea=O view/SINGLEPB 0" esp=6 png=/tmp/pbv/03-single.png esp=2
grep -a 'dlopen(view\|OPENHOT\|Vn 03F\|Vn 080\|getModelInfo(' analysis/gui/g22/harness/live/pbv2/shim.log
curl -s http://127.0.0.1:8692/estado
curl -s -X POST http://127.0.0.1:8692/salir
```

## 12. Evidencia

| fichero | qué es |
|---|---|
| [`registro-vistas-estatico.txt`](../../reports/evidence/g22-pbvista-20261126/registro-vistas-estatico.txt) | 278 entradas `IdSoTable::add` de `viewUnified2.so` (154 + 124), con sitio y pasada |
| [`pbv2-trazas.txt`](../../reports/evidence/g22-pbvista-20261126/pbv2-trazas.txt) | `dlopen`, `OPENHOT`, `Vn 03F`/`Vn 080`, `getModelInfo` del invitado |
| [`00-antes.png`](../../reports/evidence/g22-pbvista-20261126/00-antes.png) … [`03-single.png`](../../reports/evidence/g22-pbvista-20261126/03-single.png) | los cuatro fotogramas comparados (0,29 % de píxeles distintos = ruido) |
