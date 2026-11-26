# FILM-PB-1 / sub-arnés-índice — ¿enumera el clip el `AVIN0001.INP` del arnés? (26-11-2026)

26-11-2026 (reloj del anfitrión durante la sesión: 25-11-2026 23:06–23:45, −03).
Cámara **no usada** (ni red, ni USB, ni `adb`, ni flasheo): todo ocurre en `qemu-system-arm`.
**Direcciones = VA del ELF** de `libmpr.so` 3.21 (`SHA-256 9a74a3bb…5e4c30`); REA/Ghidra = ELF + 0x10000.
Evidencia: [`evidence/film-pb-1-sub-arnes-indice-20261126/`](evidence/film-pb-1-sub-arnes-indice-20261126/) ·
comando reproducible: [`comando.sh`](evidence/film-pb-1-sub-arnes-indice-20261126/comando.sh) ·
generador del `.INP`: [`gen_avin.py`](evidence/film-pb-1-sub-arnes-indice-20261126/gen_avin.py).
Etiquetas: **V** = medido/verificado en esta sesión · **D** = deducido · **NV** = no verificado.

> **Contexto que cambia el encuadre (dato del usuario, 26-11-2026):** formateó la tarjeta **en la cámara** y el vídeo
> sigue sin reproducirse. Con la tarjeta recién formateada la cámara **crea su propio** `AVF_INFO\`, así que el índice
> AV queda **DESCARTADO como causa** del fallo. Este informe cierra la línea «¿el `.INP` sintético del arnés enumeraba el
> clip?» y **no** abre ninguna otra: lo que sigue es lo que faltaba medir de esa línea.

## 0. Veredicto

| Pregunta | Respuesta | Cómo |
|---|---|---|
| ¿Qué `.INP` usaba el arnés? | copia byte a byte del sintético del 27-11 (`sha256 7f10bc80…573b`, 1408 B) | `leer_avin.py`, §1 |
| ¿Enumeraba ese `.INP` el clip de la tarjeta emulada? | **NO**: 8 registros para rutas y tamaños que **no** son los de la imagen | §1 (comparado con `mdir`) |
| ¿Con un `.INP` correcto (1 registro, ruta/tamaño reales) se enumera el clip? | **NO** | §3: **0** peticiones de `MP_ROOT/…`/`MAH04198.MP4` en toda la sesión |
| ¿Llega el invitado al índice AV? | **SÍ**: `Fsys_FindFirst` de `ms:/AVF_INFO`, `…/PRV00001.BIN` y `…/AVIN0001.INP`, y **3** constructores de gestor AV | §3 (trazas + `DEREF` ASCII) |
| ¿Hay alguna línea de enumeración del MMgr/IFO? | **NO**: 0 líneas con `AVIMMGR`, `MP4IFO`, `ContentCount`, `AccessPath` | §3 (`LOGMARK`) |
| ¿Se pide la lista de contenidos a MPR? | **NO**: `MprIf::GetAVIndexContentInfoList` y `AviMMgr::GetIndexFilteringInfo` = **0 disparos** | §3 |
| ¿El índice AV es la causa del fallo de reproducción? | **NO** (descartado: tarjeta formateada en cámara y sigue fallando) | dato del usuario |

## 1. El `.INP` que usaba el arnés y qué contiene (V)

El arnés monta **`$HOME/A6000-SD`** (`sd_emu.raiz_sd()` = `Path.home()/"A6000-SD"`) y `sd_image.py` lo convierte en la
FAT32 del invitado. El `.INP` era la copia de `reports/evidence/film-pb-1-sub-avin-20261127/AVIN0001_sintetico.INP`:

```
fichero: AVIN0001.INP  1408 B (0x580)   cabecera 0x100 + 9 registros de 0x80
  #  base    nombre         nFileSize   WxH         dur_ms        dur_90kHz       bValid?
  0  000100  MAH04198.MP4   24641536    1440x1080   9510=9.510s   855900=9.510s   0x01
  1  000180  MAH04200.MP4   12984320    1440x1080   5005=5.005s   450450=5.005s   0x01
  …  (MAH04201/04202/04203/04204/04205, todos bValid=1)
  7  000480  MAH04199.MP4   24641536    1440x1080   2000=2.000s   180000=2.000s   0x00
cDirPath de los 8: "MP_ROOT/100ANV01"
```

Contraste con la imagen que se servía (`mdir` de la cabeza FAT32, [`mdir-imagen-nueva.txt`](evidence/film-pb-1-sub-arnes-indice-20261126/mdir-imagen-nueva.txt)):

| Dato | `.INP` sintético | Tarjeta emulada (y tarjeta real del 25-11) |
|---|---|---|
| ruta del clip | `MP_ROOT/100ANV01` | `MP_ROOT/100ANV01` (emulada) · **`MP_ROOT/103ANV01`** en la tarjeta real |
| tamaño declarado de MAH04198 | 24 641 536 B | **14 545 696 B** (el fichero real) |
| nº de registros | 8 (7 clips) | 1 clip |

⇒ El registro 0 **no** describía el fichero que había en la tarjeta (ni tamaño ni carpeta real), y los otros 7
describían clips que no existían en la imagen. Aun así el `.INP` es sintético y su cabecera es **NV** (0x100 B,
inventada; ver §5): no se puede afirmar que la cámara lo hubiera aceptado.

## 2. `.INP` corregido y cómo se comprobó (V)

`gen_avin.py` escribe **cabecera 0x100 + 1 registro de 0x80** con la rejilla verificada del 27-11 y bValid=1:

```
+0x00 "/MP_ROOT/103ANV01"   +0x12 "MAH04198.MP4"   +0x20 14 545 696 (tamaño real)
+0x24 bValid = 1            +0x28 1440   +0x2C 1080   +0x30 9510 ms   +0x34 855 900 (90 kHz)
+0x38 emVideoCodec = 4 (AVC)  +0x3C emProfileIndication = 2
sha256 2a620e96c5554512a72fad9641eaefd60252e5c543fb601fa10f4731dc62fca4   (384 B)
```

- Se eligió **`103ANV01`** porque es donde estaba MAH04198 en la tarjeta real; el clip se movió a esa carpeta en la
  tarjeta emulada. La regla de la rejilla y el lector son los ya publicados; el **tamaño de cabecera sigue NV**.
- El sintético original **no se sobrescribió** (sigue en `reports/evidence/film-pb-1-sub-avin-20261127/`); la copia de
  trabajo anterior quedó en `/tmp/fpb1/backup-avin/`.
- Imagen FAT32 construida con `sd_image.py` (`completa=True`, como `SD_ESTRUCTURA=1`) y comprobada con `mdir`:
  `::/AVF_INFO/AVIN0001.INP 384 B` y `::/MP_ROOT/103ANV01/MAH04198.MP4 14 545 696 B`
  (`/tmp/fpb1/sd-nuevo.head`, `sha256 15d3aaaf…09f4`).

## 3. El único arranque con el `.INP` corregido: qué dice la traza (V)

Perfil propio `analysis/gui/g22/harness/live/arnes-ind/`, puerto 8622, arranque en frío hasta la pantalla de disparo
(27 fotogramas, 315 s; la máquina estaba compartida con otros arneses). Trampas UDF armadas **al arranque** en
`libmpr` (solo **entradas de función**, ver §5) + `TRACEDEREF=d0:0:7`. Extracto íntegro en
[`arnes-ind-trazas.txt`](evidence/film-pb-1-sub-arnes-indice-20261126/arnes-ind-trazas.txt).

| Punto | Qué es | Disparos |
|---|---|---:|
| `0x60c958` | `AviMMgr::Mount` (carga del índice) | **1** |
| `0x14b660` | `avi_man_NewAviFileManager` (crea los gestores AV) | **3** (con la tarjeta sin índice, 1) |
| `0x13e474` | `Fsys_FindFirst` | **5** |
| `0x7203c0` | `MprIf::GetAVIndexContentInfoList` | **0** |
| `0x6146a4` | `AviMMgr::GetIndexFilteringInfo` | **0** |
| `0x6e8430` | `GetPlayThumbnailInfo` | **0** |
| `0x61a8f0` | `AviMMgr::isSupportContent` | **0** |
| `0x5bad00` | `ifoFramework_Semaphore::Acquire` | 6 (todas en el arranque; sin `0xB0100002`) |

Rutas **pedidas a la capa de ficheros** (decodificadas del `DEREF` de `0x13e474`, palabra a palabra):

```
n=1  r0=…  2f3a736d 5f465641 4f464e49                    → "ms:/AVF_INFO"
n=2  r0=…  2f3a736d 5f465641 4f464e49 5652502f 30303030 49422e31 4e
                                                          → "ms:/AVF_INFO/PRV00001.BIN"
n=3  r0=…  "ms:/AVF_INFO"                                (segundo objeto/gestor)
n=4  r0=…  … 4956412f 3030304e 4e492e31 50               → "ms:/AVF_INFO/AVIN0001.INP"
n=8  r0=…  idem                                          → "ms:/AVF_INFO/AVIN0001.INP"
```

Y el objeto de `AviMMgr::Mount` lleva `"ms:"` en su prefijo (`DEREF` de `0x60c958`: `… 003a736d …` = `6d 73 3a 00`).

**Lo que NO aparece en toda la sesión** (`grep -c` sobre `shim.log`, 484 líneas):
`MP_ROOT` = 0 · `103ANV` = 0 · `MAH04198` = 0 · `MP4` = 0 · `AVIMMGR` = 0 · `MP4IFO` = 0 · `ContentCount` = 0 ·
`AccessPath` = 0. Es decir: **el invitado busca y abre el índice AV, pero nunca pide la carpeta de clips ni el fichero
del clip, y no hay ninguna línea de enumeración del MMgr/IFO**. Coherente con las 0 llamadas a las dos APIs de lista.

## 4. Qué falta exactamente (para esta línea)

1. **El clip no se enumera** y no es por el `.INP` en sí: con un registro que sí coincide con la imagen (ruta, tamaño,
   1440×1080, 9510 ms, AVC, bValid=1) el invitado **sí** encuentra y abre `ms:/AVF_INFO/AVIN0001.INP` y crea **3**
   gestores AV (antes 1), pero **no** hay ni una lectura de `MP_ROOT/…`.
2. Falta el paso que va de «índice montado» a «lista de contenidos»: nadie llama a
   `MprIf::GetAVIndexContentInfoList` (`0x7203c0`) ni a `AviMMgr::GetIndexFilteringInfo` (`0x6146a4`). O el consumidor
   es otro (libObj/`MprIfMcmd`, que no se puede invocar desde el shim: `O` solo hace `viewManagerIf::openView`), o el
   montaje devuelve error y no llega a publicar contenidos.
3. **NV**: el contenido de la cabecera (0x100 B) y los campos `+0x24`/`+0x34`/`+0x3C` son deducidos; el `.INT`
   (índice interno, descriptor `.data 0x9D12C0`) **no existe** en la tarjeta emulada y podría ser imprescindible para
   que el índice publicado no esté vacío. Con la tarjeta formateada por la cámara ese `.INT` **sí** existe, así que
   esta incógnita **ya no bloquea** la línea: el índice queda descartado como causa.
4. Dato estático útil para quien retome: la plantilla propia del binario es `0x7ACAEC "/MP_ROOT/100ANV01/MAH%05ld.MP4"`
   (separador `/`), y el volcado de `CS_AviAcsr` imprime `Prefix`/`Separator` (`0x7A614B`/`0x7A615E`), es decir la ruta
   del registro puede ir **relativa a un prefijo**.

**Siguiente paso concreto (para la línea de índice, si se reabre):** no tocar el `.INP`; instrumentar solo
`0x7203c0`/`0x6146a4` **y** el retorno del montaje, y si el montaje sale con error, seguirlo por el reportero de
errores `0x64e27c` (entrada de función; `r2` = código, `r3` = cadena de módulo en `.rodata`) — nunca dentro de
`AviMMgr::Mount`.

## 5. Trampas de arnés encontradas (medidas; ahorran tiempo a los demás)

1. **`HOME` decide qué tarjeta se monta.** `sd_emu.raiz_sd("") = Path.home()/"A6000-SD"`. Con `HOME=/tmp/fpb1` la
   tarjeta era `/tmp/fpb1/A6000-SD` (**inexistente** ⇒ imagen con solo las carpetas base, cero ficheros). Seis
   arranques de esta sesión se hicieron así (perfiles `arnes4`…`arnes9`): sus medidas de «vista vacía» siguen valiendo
   como *tarjeta sin contenido*, pero **no** probaron el `.INP`. El arranque válido es con `HOME=/tmp/fpb1/home`.
2. **Nombre de perfil corto**: `live/<perfil>/ui.sock` no puede pasar de 108 B; `arnes-indice` (110 B) hace fallar a
   QEMU (`UNIX socket path … is too long`) y el perfil se queda con el `initrd.gz` a medias. Se usó **`arnes-ind`**.
3. **Trampas solo en entradas de función.** Con `TRACEREP` el shim pone un UDF temporal en la instrucción siguiente;
   si la instrucción trazada está dentro de una función (tras un salto), el flujo se rompe: con trampas en
   `0x60c9ee`/`0x60c9f4` (dentro de `AviMMgr::Mount`) el invitado **se quedó en 2 fotogramas** y no llegó a la UI.
4. **`WLALL=1` frena el arranque** hasta dejarlo en 2 fotogramas a 200 s (medido en `arnes5`); sirve para volcar el
   registro de la cámara, no para medir tiempos. `LOGMARK=<clave>` es el sustituto ligero, pero **no** apareció
   ninguna línea de enumeración con `TRACELIB,AVIMMGR,MP4IFO,ContentCount,AccessPath`.
5. **`live.py` puede morir al salir**: `puente.desde_invitado()` revienta con `ValueError: not enough values to unpack
   (expected 4, got 3)` cuando un mensaje de la cola de av-cam llega con 3 campos (visto en `arnes4/6/ind`); el puente
   av-cam queda muerto el resto de la sesión.

## 6. Límites (NV)

- **El tamaño y la semántica de la cabecera del `.INP` siguen NV**: 0x100 B y `version/recSize/max/count` en
  `+0x10…+0x1C` son invención coherente, no lectura de un fichero real. Que la cámara acepte un índice escrito a mano
  es NV (no hay `.INP` real en el repo).
- Las 4 rutas de §3 están decodificadas del `DEREF`; sus **códigos de retorno no se capturaron** (el shim traza a la
  entrada): no se sabe si `Fsys_FindFirst("ms:/AVF_INFO/AVIN0001.INP")` devolvió 0 o error.
- No se ha mirado ninguna vista ni la UI en esta parte (es de otro subagente); de los arranques tempranos con la
  tarjeta vacía solo se conserva la observación de que `view/SINGLEPB` llegó a pintar «No hay imágenes en esta
  visualización» (captura `capturas/03-singlepb.png`), sin más interpretación.
- No se ha tocado `docs/`, `knowledge/`, `build/` ni código del arnés; solo este informe y
  `reports/evidence/film-pb-1-sub-arnes-indice-20261126/`.
