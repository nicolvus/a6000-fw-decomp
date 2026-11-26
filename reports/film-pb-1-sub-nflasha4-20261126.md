# FILM-PB-1 · sub · Auditoría de la partición `nflasha4` (FBS de libmpr)

**Fecha:** 2026-11-26 · **Evidencia:** `reports/evidence/film-pb-1-sub-nflasha4-20261126/`
**Volcados auditados** (todos 10 485 760 B, sha256 comprobados en esta sesión):

| id | fichero | sha256 |
|---|---|---|
| D1 | `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` | `a5ab15ca…9ac7247` |
| D2 | `analysis/camera-dumps/nand-20261105/dev_nflasha4.bin` | `d5510bcb…d9f56931` |
| D3 | `analysis/camera-dumps/nand-20261105-total/dev_nflasha4.bin` | `bbe0ae1f…e9383909fcf` |

---

## Resumen

1. La partición **no está corrupta**: los tres volcados son coherentes (sector de 1 KiB, cabecera, tablas de 8 B y trailer iguales; ninguna escritura a medias ni registro fuera de rango).
2. Geometría real del FBS, sacada del binario y confirmada con los datos: **sectorSize 1024 B, sectorNum 128 por bloque, blockNum 80 → 80 × 128 KiB = 10 MiB**.
3. Los tres están **casi vacíos**: sólo el 6.9 % (D1), 2.2 % (D2) y 3.7 % (D3) de los 10 240 sectores están formateados; el resto es `0xFF`.
4. **D2 ⊂ D3 al 100 %**: los 229 sectores de D2 son idénticos en D3, que sólo añade ~25 por bloque y áreas de carga nuevas. Es crecimiento, no daño.
5. **D1 no comparte ni un sector con D3** (0 de 706): es otra BD, de otra época (118 sectores/bloque y carga en el bloque 74, no en el 6).
6. Todas las diferencias son **de datos de uso**; **ninguna estructural** (cabecera, geometría termina en 128, límites de bloque). Única rareza: los 5 primeros sectores de bloque de D2/D3 no llevan trailer y en D1 sí — mismo patrón en D2 y D3, se atribuye al escritor, no a daño.
7. El más sano es **D3**: superset de D2 y el único con índice AVCHD (`INDX0100`/`MPLS0100`/`HDMV0100`, `CAO_DATA`) y `MP_ROOT/152ANV01`.
8. El defecto visible no es corrupción, es **vacío**: D3 no tiene ni una ruta `ms:/DCIM/…`; D2 tiene 29 y D1 sólo 5.
9. `nflasha4` **puede** ser la causa (la tabla de 30 readers depende al 100 % de ella), pero los bytes no prueban daño: si falla, es por «DFB sin inicializar» (geometría 0,0,0) y eso no se ve en un volcado, hay que leer el log del arranque.
10. Restaurar **sí** es posible con D3, pero no arregla el síntoma por sí solo: una BD vacía restaurada sigue vacía y la tarjeta se formateó después.
11. Escribirla exige `dd` crudo a `/dev/nflasha4` (el repo sólo tiene PULL); el riesgo alto es dejar la BD incoherente y perder también las miniaturas.

---

## 1. Método

* Censo sector a sector de los tres volcados con `census.py` (evidencia): mapa de bytes ≠ `0xFF`,
  entropía Shannon por bloque de 4 KiB, firmas repetidas, cadenas ASCII, regiones contiguas,
  diferencias por bloque de 1 KiB y contención entre volcados.
* Desensamblado de `libmpr.so` (`analysis/camera-extract/usr/lib/libmpr.so`, ELF32 ARM,
  VA == offset en el primer `PT_LOAD`) con capstone en Thumb-2, por descenso recursivo
  (`recdesc.py`) y con resolución automática de literales (`ann.py`).
  Los nombres de función/variable **no** son inferidos: salen de `.dynsym`
  (`dynsyms-flash.txt`), que exporta `FlashLib::*` y `DvdFlashBackupLib::*`.
* No se ha tocado la cámara ni se ha escrito nada en NAND.

---

## 2. Estructura real de un «sector FBS» (medida en el volcado)

```
+0x000  u32  estado/lógico        = 0x00000000 en los 1 316 sectores formateados de los 3 volcados
+0x004  u32  firma               = 0x004A004A  (bytes 4A 00 4A 00; como dos u16: 0x004A, 0x004A)
+0x008  8·N  tabla de registros  = { u32 longitud, u8, u8, u8, u8 = 0xFF }
+...          0xFF hasta el final
+0x3AB  8 B  trailer             = "draCNV4'"  + 8 bytes a cero   (offset 939, idéntico en los 1 306)
```

* **No hay comprobación de magic a nivel de sector.** El único test es «¿está en blanco?»:
  `0x2B061E` lee los 4 primeros bytes como u32 LE y devuelve 0 sólo si valen `0xFFFFFFFF`.
  Es lo que usa el barrido de `DvdFlashBackupLib::Init` (`[DFB]init()- blank find`,
  `[DFB]init():::NOblank find!`, `[DFB]Blank was discovered. However, it is ReadErrorSector.`).
  Consecuencia: para el FBS, cualquier sector cuyo primer u32 ≠ `0xFFFFFFFF` «existe».
* La firma `0x004A004A` y el trailer `draCNV4'` **no son constantes de libmpr** ni de ningún
  binario del userland extraído (`draCNV`: 0 apariciones; `4A004A00`: 3 apariciones en libmpr,
  las tres dentro de la tabla de saltos `tbh` de `0x4245DA`). Son marcadores de la capa de
  contenido que escribe dentro del sector; **su productor no está identificado** (pendiente).
* Los sectores con datos densos y **sin** cabecera (p. ej. 7040–7042 de D3, con
  `INDX0100`/`MPLS0100`/`HDMV0100`) son **carga útil** almacenada por el FBS, no sectores de
  índice: el FBS los direcciona por `índice << 10` sin exigirles cabecera.

---

## 3. Mapa, entropía y firmas

### 3.1 Recuento por volcado (10 240 sectores de 1 024 B cada uno)

| | D1 20261020 | D2 20261105 | D3 20261105-total |
|---|---|---|---|
| sectores con cabecera FBS | **706** | **229** | **381** |
| … de ellos con trailer en `+0x3AB` | 706 (100 %) | 224 (97.8 %) | 376 (98.7 %) |
| … sin trailer = 1.er sector de cada bloque usado | 0 | 5 (`0,128,256,384,512`) | 5 (`0,128,256,384,512`) |
| sectores de carga útil sin cabecera | 59 | 150 | 33 |
| sectores borrados (`0xFF`) | 9 475 | 9 861 | 9 826 |
| bytes ≠ `0xFF` | 344 067 (**3.28 %**) | 244 547 (**2.33 %**) | 185 155 (**1.77 %**) |
| entropía por bloque de 4 KiB (mediana, no borrados) | 1.70 bit/B | 1.33 | 1.45 |
| entropía máx. observada | 1.78 | 1.54 | 3.49 |

Ningún sector queda «a medias»: no hay cabecera sin cola de tabla, ni tablas truncadas, ni
registros que apunten fuera de la partición. La entropía baja (< 2 bit/B) es la esperada en
tablas con relleno `0xFF`; el máximo 3.49 de D3 corresponde a los bloques con índice AVCHD.

### 3.2 Mapa de bloques de 128 KiB (`.` = todo `0xFF`; cada carácter = 4 KiB)

```
D1  b0-b5  ##############################..   (118+118+118+118+117+117 sectores FBS)
    b7     #...............................   (sector 896, carga útil)
    b74    ###############.................   (9472-9529, carga útil)
D2  b0-b5  ##########......................   (39+38+38+38+38+38 sectores FBS)
    b6     ################################  (768-895, carga útil densa, 128 KiB enteros)
    b7     #...............................  (sector 896)
    b34    ######..........................  (4352-4372, carga útil)
D3  b0-b5  ################................ (64+64+64+63+63+63 sectores FBS)
    b7     #...............................  (sector 896)
    b47    ####............................  (6016-6031)
    b54-b56                                 (6912-6918 AVCHD, 7040-7042 INDX/MPLS/M2TS,
                                             7168-7173 MP_ROOT/152ANV01)
```

Los huecos **siempre** empiezan en múltiplos de 128 → el bloque físico del FBS es de 128 sectores.
La ocupación de los 6 primeros bloques es homogénea (118 / 38 / 64), es decir la BD crece
repartiendo entradas entre los bloques de control, como describe el propio código.

### 3.3 Cadenas ASCII

| | cadenas distintas | contenido |
|---|---|---|
| D1 | 6 | `draCNV4'` ×706 + 5 rutas `ms:/DCIM/141MSDCF/DSC0000{3,10}.JPG`, `14240101/DSC0304{3,4,5}.JPG` |
| D2 | 30 | `draCNV4'` ×224 + 29 rutas `ms:/DCIM/15140101/DSC034xx.{ARW,JPG}` y **`ms:/MP_ROOT/151ANV01/MAH03477.MP4`** |
| D3 | 18 | `draCNV4'` ×376 + fecha `15261105` + `INDX0100`, `MPLS0100`, `HDMV0100`, `00000M2TS`, `CAO_DATA`, `MP_ROOT`/`152ANV01`/`104ANV01`, `0002DSLR-00002G_MC1` |

D3 **no contiene ninguna ruta `ms:/DCIM/…`**: no tiene entradas de fichero, sólo el índice AVCHD
y el directorio `MP_ROOT`. D2 sí tiene un MP4 y 28 ficheros de foto. D1 sólo 5 JPG.

---

## 4. Comparación entre los tres volcados

| par | bloques de 1 KiB distintos | reparto |
|---|---|---|
| D1 ↔ D2 | **913** / 10 240 (8.9 %) | b0–b5: **706**, todos los sectores que usa D1 (los de D2 caen en esas mismas posiciones y también difieren) + b6 (128, carga de D2) + b34 (21, carga de D2) + b74 (58, carga de D1) |
| D1 ↔ D3 | **796** / 10 240 (7.8 %) | b0–b5: **706** (mismo caso; las 381 posiciones de D3 están dentro de las 706 de D1) + b47 (16) + b54 (7) + b55 (3) + b56 (6) de D3 + b74 (58) de D1 |
| D2 ↔ D3 | **333** / 10 240 (3.3 %) | 152 sectores nuevos de D3 en b0–b5 (25/26/26/25/25/25) + b6 (128) + b34 (21) borrados en D3 + b47/b54/b55/b56 de D3 (32) |

* **D2 ⊂ D3 exacto al 100 %**: los 229 sectores formateados de D2 son idénticos en D3.
  D3 = D2 + ~25 sectores por bloque + áreas de carga nuevas − las dos áreas de carga de D2
  (b6 y b34) que en D3 aparecen borradas. **Es evolución normal de la BD.**
* **D1 y D3 no comparten nada** (0 de 706): D1 es una BD anterior y distinta, con otro reparto
  de bloques (ocupa 118 sectores/bloque y guarda su carga en b74, no en b6).
* Diferencia estructural única y sistemática: en D2 y D3 el **primer sector de cada bloque usado**
  no lleva el trailer `draCNV4'`; en D1 sí lo llevan los 706. Es una diferencia de *escritor*
  (dos versiones de firmware / dos rutinas de control), coherente consigo misma en D2 y D3
  (mismo patrón, exactamente 5 sectores en ambos) → **no es corrupción**, pero conviene
  confirmarlo en cámara si alguna vez se restaura D1.

**Más sano: D3.** Es superset de D2, está completo estructuralmente (98.7 % con trailer; los 5
que faltan son los sectores de control, igual que en D2) y es el único con índice de vídeo.

---

## 5. Geometría del FBS en `libmpr.so` y validación de los volcados

### 5.1 Lo que dice el binario (ver `libmpr-geometria.txt`)

| símbolo / dirección | valor | qué es |
|---|---|---|
| `FlashLib::Init(MPR::SystemType)` | `0x2B696C` (560 B) | llama a `0x2B0FFC` con `r1=&m_blockNum`, `r2=&m_sectorNum`, `r3=&m_sectorSize`; luego `malloc(m_sectorSize)` |
| `0x2B0FFC` | thunk → `0x2A9AD8` | `DvdFlashBackupLib::Init`: **la geometría son parámetros de salida suyos** |
| `FlashLib::m_blockNum` | `0xA36C7C` | `.bss`, rellenado en runtime |
| `FlashLib::m_sectorNum` | `0xA36C74` | `.bss` |
| `FlashLib::m_sectorSize` | `0xA36C80` | `.bss` |
| `FlashLib::m_packWriteInfo` | `0xA36C89` (833 B) | 49 registros de 17 B, estado de escritura por sector en RAM |
| `FlashLib::m_fileTypeSizeInfo` | `0x9D2794` (624 B) | tabla de longitudes por fileType (52×12 B) |
| `FlashLib::CheckExistSector(u64)` | `0x2B8B48`¹ | devuelve `0x45` sólo si la capa DFB lo tiene indexado |

¹ `.dynsym` guarda `0x2B8B49` con el bit Thumb puesto; aquí se da la dirección par.

**No existe tabla por modelo.** `m_blockNum/m_sectorNum/m_sectorSize` son salidas de
`DvdFlashBackupLib::Init`, que a su vez las deriva del driver (`DFA::Init`, ioctls `MMS_IOC_*`,
`/dev/nflasha4` o `/dev/cnflasha4`) y del offset de partición leído de
`/sys/block/nflasha0/nflasha0p4/start` (`0x7DD572` **es la cadena**, no código).
Queda registrado en log: `[DFB]call api (DvdFlashBackupLib::Init) result:blockNum[%d],sectorNum[%d],sectorSize[%d]`
(`0x7E3CCE`) y `[DFB]AllBlockNum:%d / CtrlInfoBlockNum:%d` (`0x7DF73B`).

### 5.2 Constantes que sí son de compilación

* **`sectorSize = 1024`**: en todo `DvdFlashBackupLib::Init` la dirección de un sector se calcula
  como `índice << 10` (`0x2A9F2E`, `0x2A9F34`, `0x2A9FAA`, `0x2AA00E`, `0x2AA2F0`) y
  un tamaño total se convierte en número de sectores con `>> 0xA` (`0x2A9C64`).
  No se lee de la partición en ningún momento.
* **`CtrlInfoBlockNum` por número de bloques** (`0x2A9C4A`-`0x2A9C7E`):
  `allBlockNum ≤ 0x30 → 2`, `≤ 0x50 → 6`, resto `→ 8`.
* **Sector en blanco = primer u32 `0xFFFFFFFF`** (`0x2B061E`).
* No hay constante de *magic* de sector en `libmpr.so` (§2).

### 5.3 Validación contra los volcados

Con `blockNum = 80`, `sectorNum = 128`, `sectorSize = 1024` → 80 × 128 × 1024 = **10 485 760 B**,
exactamente el tamaño de la partición y de los tres ficheros. Dos comprobaciones independientes:

1. Todos los sectores usados caen en ventanas de 128 y todos los huecos empiezan en múltiplos de
   128 (§3.2) → `sectorNum = 128`.
2. `allBlockNum = 10 MiB / 128 KiB = 80` cae en el tramo `0x30 < 80 ≤ 0x50` → el firmware calcula
   `CtrlInfoBlockNum = 6`, y los tres volcados usan **exactamente 6 bloques FBS (0–5)**.
   Coincidencia no trivial: si `blockNum` fuera > 80 el firmware reservaría 8 y el reparto
   observado no cuadraría.

**Sectores numerados con estado válido** (definición operativa: cabecera presente ⇒ no borrado;
el *handle* de los 30 readers está en RAM, no se puede leer del volcado):

| volcado | 0–127 | 128–255 | 256–383 | 384–511 | 512–639 | 640–767 | con estado válido | válidos **y** completos (trailer) |
|---|---|---|---|---|---|---|---|---|
| D1 | 118 | 118 | 118 | 118 | 117 | 117 | **706** / 10 240 = 6.9 % | 706 |
| D2 | 39 | 38 | 38 | 38 | 38 | 38 | **229** / 10 240 = 2.2 % | 224 |
| D3 | 64 | 64 | 64 | 63 | 63 | 63 | **381** / 10 240 = 3.7 % | 376 |

---

## 6. Conclusión

**(a) ¿Puede `nflasha4` ser la causa del fallo?**
Mecánicamente **sí**: la tabla de 30 readers se llena en `BackupMgr::WarmBootInit`/`Init` con
`FlashLib::CheckExistSector` y el campo `+4` es el handle FBS; si el FBS no está inicializado o el
sector no está indexado, las 30 entradas quedan a 0 y *toda* carga de IFO devuelve `0x10100001`
(MSV, DCF y XAVC a la vez) mientras las miniaturas de foto siguen saliendo de la tarjeta.
Pero **los bytes no muestran corrupción**: muestran una base de datos casi vacía y coherente.
La causa inmediata, si es esta partición, sería *DFB no inicializado* (geometría `0,0,0`,
fallo de `open` de `/dev/nflasha4` o `/sys/block/nflasha0/nflasha0p4/start`) — y eso **no se ve
en un volcado**: hay que leer el log del arranque (`[DFB]…`).
Como causa por **contenido** (BD vacía ⇒ no hay índice que cargar) también encaja con el síntoma,
pero entonces es una BD *vacía*, no *dañada*, y el arreglo es regenerarla, no restaurarla.

**(b) ¿Hay un volcado sano para restaurar?**
Sí: **D3** (`nand-20261105-total`). Es el único con índice AVCHD, contiene D2 íntegro y no tiene
ninguna inconsistencia estructural. Con dos reservas: (i) no hay ningún volcado de referencia
*lleno* con el que comparar, así que «sano» = «coherente», no «conocido bueno»; (ii) restaurarlo
no crea metadatos de vídeos que ya no existen (la tarjeta se formateó después).

**(c) ¿Cómo se escribiría y qué riesgo tiene?**

| vía | estado | riesgo |
|---|---|---|
| **Dejar que la cámara regenere la BD** (sin tarjeta, arrancar; luego `Recuperar BD imág.` en Ajustes con la tarjeta puesta) | recomendado primero | nulo; es reversible. Si tras esto vuelve a fallar, la partición queda descartada como causa **de contenido** (quedaría sólo la de inicialización) |
| **`dd` a `/dev/nflasha4`** desde el shell root de la cámara (`scripts/camera_push_file.py` para subir + `scripts/camera_telnet.py` para ejecutar: `dd if=/tmp/d3.bin of=/dev/nflasha4 bs=1024`) | posible; **el repo no tiene PUSH de NAND**, `scripts/updater_nand_dump.py` es sólo PULL | **alto**: se salta el asignador del FBS y su libro de bloques; si la geometría/mapa de bloques malos difiere, se escribe encima de bloques relocalizados; una escritura parcial deja la BD incoherente (peor que ahora); hay que volcar antes el estado actual para poder volver |
| **SWD / BIONZ** | no soportado para NAND en este repo (sólo RAM y el arranque del actualizador, R47–R49) | **muy alto**: no hay ruta probada de escritura NAND por SWD |

Antes de cualquier escritura: volcar el estado actual con `scripts/updater_nand_dump.py` (10 MiB,
sha256 propio) para tener rollback. Y comparar el log de arranque: si sale
`[DFB]call api (DvdFlashBackupLib::Init) result:blockNum[0],sectorNum[0],sectorSize[0]` el
problema no es el contenido de la partición sino la inicialización, y escribir no arreglará nada.

---

## 7. Límites de esta auditoría

Registrado también como `FILM-PB-1-SUB-NFLASHA4` en `docs/PENDIENTES.md`.

* No se ha leído el log de arranque de la cámara: no se puede afirmar que el DFB falle.
* El *handle* por reader (campo `+4` de las 30 entradas) es RAM: no se deduce del volcado; sólo se
  puede inferir si el contenido que el DFB indexa existe.
* El productor de la firma `0x004A004A` y del trailer `draCNV4'` no está identificado (no está en
  libmpr ni en el userland extraído); su ausencia en los 5 sectores de control de D2/D3 queda como
  diferencia de escritor, no como defecto, pero sin prueba en cámara.
* `m_fileTypeSizeInfo` se ha localizado y medido (624 B) pero su semántica exacta (52×12 B) no se
  ha recorrido función a función; no afecta a las conclusiones anteriores.
