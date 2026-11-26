# FILM-PB-1 — ¿puede el `libObj.so` parcheado romper la inicialización de medios/IFO? (26-11-2026)

Estado: **verificación ejecutada**, sin cámara (sin red, USB ni `adb`) y sin tocar `docs/`,
`knowledge/`, `build/` ni código existente. Ficheros comparados: `libObj.so` de fábrica 3.21
(`firmware/extracted/fw321/…/nflasha15_unpacked_unpacked/lib/`, SHA-256 `8e8a937a…5b6a`,
17 436 172 B) y el parcheado del CFW 3.93 (`build/cfw_func393/pp/files/lib/`, SHA-256
`db382008…045d0`, 18 127 472 B). **Espacio de direcciones: VA del ELF (base 0)**; *REA = ELF + 0x10000*.
Evidencia y andamios: [evidence/film-pb-1-sub-libobj-init-20261126](evidence/film-pb-1-sub-libobj-init-20261126/).

## 1. Qué arnés del repo sirve para cargar un `.so` ARM y ejecutarlo (VERIFICADO)

| Candidato | Sirve | Por qué |
|---|---|---|
| **`scripts/g22/sim/armlib.py`** | **sí** | Cargador ELF32/ARM sobre Unicorn: mapea los `PT_LOAD`, aplica ABS32/GLOB_DAT/JUMP_SLOT/RELATIVE y resuelve los símbolos indefinidos a stubs con *handler* Python por símbolo (`Machine.handlers`, `Machine.overrides`). Es el que usan `scripts/g22/sim/{libobj,cmnview,avcam}.py` y tests como `tests/test_g22_sim_cadena.py`. |
| `scripts/gui/harness/` (`live.py`, `run.py`, `a6000-emu.sh`, `analysis/gui/g22/harness/stage`) | no para esto | Arranca `im.elf` entero con el `/usr` completo en QEMU; no carga una `.so` suelta y tarda minutos por arranque. |
| `tests/test_*.py` (Unicorn) | no | Mapean *bytes* de una función en una dirección fija; ninguno carga un ELF con sus reubicaciones. |
| Andamio propio `evidence/…/init_emu.py` | sí (usado) | Mismo modelo que `armlib`, con contadores por instrucción y detección de ejecución en los rangos parcheados. |

Invocación (la del cargador del repo, tal como se ha ejecutado):

```python
import sys; sys.path.insert(0, "scripts")
from g22.sim.armlib import Lib, Machine
m = Machine()                      # pila 0x7E100000, montón 0x60000000, stubs 0x7F000000
Lib(m, open(so, "rb").read(), 0)   # base 0 ⇒ VA del fichero = dirección de ejecución
m.call(entrada, 0, 0, 0)           # .init_array[i] (dirección Thumb); r0 = valor de retorno
```

## 2. `.init_array`: **idéntico** en las dos versiones (VERIFICADO)

- VA `0xFD25A4`, tamaño `0x41C` = **263 entradas** (fichero: offset `0xFCA5A4` = inicio del
  segmento RW), `DT_INIT_ARRAY` = `0xFD25A4` y `DT_INIT_ARRAYSZ` = `0x41C` en ambas.
- Los **1 052 B son idénticos** (`estatico.txt`), igual que `.fini_array` (2 entradas). **El parche
  no añade, no quita y no cambia ningún inicializador estático**, ni su orden.
- Las 263 son impares (Thumb) y **ninguna tiene nombre en `.dynsym`** (0/263): libObj viene sin
  `.symtab`, así que la lista se da por dirección.
- Lista completa (263; 10 por línea):

```
0xe2bc9 0xe3699 0xe3af5 0xe4711 0xe5aa9 0xe6541 0xe6e55 0xe70ed 0xe9209 0xe9d4d
0xe9dc9 0xeab61 0xeaf89 0xeb045 0xeb09d 0xec905 0xeccd1 0xee799 0xeeb15 0xeeb6d
0xf0919 0xf0c6d 0xf0ee5 0xf2311 0xf3b09 0xf3d51 0xf4c9d 0xf59cd 0xf7921 0xf8309
0xfa275 0xfc99d 0xfcf65 0xfd96d 0xfe8fd 0xff8e1 0x101431 0x102279 0x1027b5 0x102a3d
0x103c2d 0x104c4d 0x10521d 0x106271 0x1067fd 0x106ee5 0x107109 0x107161 0x107881 0x109d35
0x10a4fd 0x10aab1 0x10af71 0x10ca39 0x10ce29 0x10d075 0x10d9e1 0x10e7fd 0x10f4ed 0x10f569
0x114269 0x115a01 0x115ce5 0x1172d9 0x119c8d 0x11a249 0x11b9cd 0x11c119 0x11d329 0x11e695
0x11f435 0x11f48d 0x11ffd1 0x120739 0x122f19 0x124f95 0x124fdd 0x12520d 0x1255c1 0x127b85
0x1281d5 0x12c4b5 0x12c569 0x12c5f9 0x12cc61 0x12ccbd 0x12dc6d 0x12de31 0x12ea79 0x12ecb5
0x12ed0d 0x130249 0x13057d 0x1319b1 0x131a89 0x133249 0x133801 0x133ba1 0x13462d 0x1347c1
0x136e35 0x137501 0x13b279 0x16fcbd 0x19e35d 0x1a75f9 0x1ab609 0x204e25 0x293a39 0x340ef5
0x346395 0x34970d 0x34a14d 0x34cafd 0x34d7d9 0x34e931 0x3501cd 0x3655b9 0x3aba49 0x40e621
0x41ff61 0x4437c5 0x45e8ed 0x45f3e9 0x45f871 0x45fd7d 0x45ff05 0x45ff5d 0x460f9d 0x461b81
0x461de1 0x461f21 0x462955 0x462a5d 0x462ced 0x4632ad 0x4637f5 0x48c3a5 0x494235 0x496cfd
0x49de59 0x58f0c5 0x58f68d 0x58f761 0x58f8c5 0x5906d9 0x5907a5 0x590a51 0x590d79 0x592dc5
0x59317d 0x59321d 0x593439 0x593849 0x593899 0x594f9d 0x595239 0x595415 0x5956f9 0x595979
0x597015 0x597299 0x5973a1 0x597d45 0x597df5 0x597ead 0x598319 0x598709 0x5aaf7d 0x5abd49
0x5b0079 0x5b0369 0x5b03bd 0x5b29b5 0x5b30a9 0x5b38c1 0x5b38f9 0x5b3ed9 0x5b44bd 0x5b4d21
0x5b5199 0x5b533d 0x5b5535 0x5b5695 0x5b6491 0x5b67e5 0x5b7801 0x5b83d9 0x5ba599 0x5ba8d9
0x5bb1dd 0x5bb319 0x5bb451 0x5bb815 0x5bbc35 0x5bc379 0x5bc5f1 0x5bcea5 0x5bd0a1 0x5c96b9
0x5c995d 0x5c99a1 0x5cf901 0x5d07e5 0x5d4d0d 0x5e599d 0x5e6655 0x5e8995 0x5ee5ad 0x5eeba5
0x61880d 0x6342e1 0x6374b1 0x6a16d9 0x6a6761 0x6ad6cd 0x6adb39 0x6ba44d 0x72d42d 0x72e751
0x73c295 0x73e271 0x76ddfd 0x76e6ad 0x775891 0x781091 0x79f4d1 0x7b4e1d 0x7b97f9 0x7cee21
0x7cfe61 0x7d2475 0x7d6629 0x7d6cd1 0x7d7011 0x7d963d 0x7dc301 0x7e004d 0x7e320d 0x7e5579
0x7e7851 0x7e8759 0x7ea65d 0x7ea8c9 0x7ee275 0x7ef449 0x7f1785 0x7f19ed 0x7f1ba5 0x7f48ad
0x7f5131 0x80a369 0x80aa61 0x80b355 0x814d05 0x81853d 0x81c5cd 0x82ac7d 0x965449 0x978cb5
0xa1f089 0xa425b1 0xb596a1
```

## 3. Las 263 entradas ejecutadas en Unicorn (VERIFICADO)

Dos andamios independientes, mismo modelo (base 0, importaciones a stubs que devuelven 0):

| Medida | `armlib` (repo) | `init_emu.py` (propio, con contadores) |
|---|---|---|
| Entradas ejecutadas | 263 en las dos versiones | 263 en las dos |
| Retornan bien | **262 / 262** | 260 / 260 (+2 que entran en un stub de objeto importado) |
| Fallan | **1: la #251 (`0x80A369`), la misma y en el mismo punto en ambas** | la misma #251 |
| Importaciones llamadas | **194, secuencia idéntica** | 190 llamadas, idénticas |
| Instrucciones ejecutadas | — | **9 222 en cada versión** |
| Escrituras | — | **2 945 en cada versión** |
| Entradas con resultado distinto | **0** | **0** |
| Instrucciones dentro de los 26 rangos `.text` parcheados | — | **0** |
| Bytes distintos en el segmento RW al terminar | **13 rangos**: los 30 B de `.data.rel.ro` + `DT_REL` | los mismos 13 |

Los 13 rangos son exactamente la diferencia estática (§4): los inicializadores **no propagan** el
cambio a ningún otro sitio. Las 263 entradas son ajustes de punteros preenlazados (~35
instrucciones de media; máximo 309, medido sin contar los stubs de importación). **Ninguna de las
263 ejecuta ni escribe** en el semáforo `ifoFramework` (`0x5BAD00`), en
`AviMMgr::GetPlayMovieStatus` (`0x60945C`) ni en `GetPlayThumbnailInfo` (`0x6E8430`): el
`.init_array` de libObj no toca la inicialización de medios/IFO
([medios_check.py](evidence/film-pb-1-sub-libobj-init-20261126/medios_check.py) → `medios.txt`).

## 4. Lo que sí cambia en el fichero (VERIFICADO): 41 rangos, 506 B + 691 300 B añadidos

| Zona | Cambio |
|---|---|
| `.text` (26 rangos, `0x4A784C…0x9B3744`) | parches de Picture Profile/Silent del proyecto; el mayor (`0x9B325E`, 94 B) sustituye la cadena de `switch` de ValueIds por un bucle sobre una tabla de 12 (`0x1ad…0x584`). Ningún constructor ejecuta estas direcciones (§3) |
| `.data.rel.ro` (6 entradas, 30 B: `0xFDF19C…0xFDF560`) | `{u16 0x0004, u16 n, u32 tabla}`: `n` 8→12 y 12→13; el puntero pasa a `0x1188250` (12 palabras) y `0x1188280` (13) del segmento nuevo. Tablas de ValueIds de PP |
| `.dynamic` (`0x102CB6C`) | `DT_REL` `0x365D0` → **`0x10E8000`**; `DT_RELSZ` **no cambia** (`0xA0248`). La copia en `0x10E8000` es **byte a byte idéntica** ⇒ el cargador aplica las **mismas 81 993 reubicaciones** a los mismos destinos |
| Cabecera (`0x1C`, `0x2C`) | `e_shoff`/`e_shnum` (cola de secciones añadida) |
| `PT_LOAD` nuevos | `0x00FCB000` (`0xA70`, RWX): 2 608 B de código nuevo + copia de 2 `phdr`; y `0x010E8000` (`0xA0380`, RW): copia de `.rel.dyn` + 2 tablas de ValueIds + copia de la tabla de `phdr` |

**Corrección al informe del 27-11**: los 312 B que siguen a la copia de `.rel.dyn` **no** son 39
entradas `R_ARM_GLOB_DAT`. Son relleno y dos tablas de ValueIds (12 y 13 palabras) seguidas de una
copia de la tabla de `phdr`; `DT_RELSZ` no cambia, así que el cargador no las lee como
reubicaciones. (El `.rel.dyn` real ya tenía 39 `GLOB_DAT` en el fichero de fábrica.)

**Loadabilidad** (comprobado con el cargador de §1, que mapea los dos ficheros sin error):
los dos segmentos nuevos están alineados a página (`vaddr % 0x1000 == offset % 0x1000 == 0`), no
solapan con los de fábrica (RX acaba en `0x0FCA5A4`, el nuevo empieza en `0x0FCB000`; RW acaba en
`0x010E2BD0`, el nuevo empieza en `0x010E8000`) y sus permisos son coherentes con su contenido.

## 5. Veredicto

**NO: el `libObj.so` parcheado no puede romper la inicialización estática de medios/IFO.**

- El `.init_array` es **idéntico** (263 entradas, mismos bytes y orden): no hay inicializador
  añadido, quitado ni cambiado.
- Ejecutadas las 263 en las dos versiones: **mismo resultado, mismas importaciones, mismas
  escrituras**; ninguna toca el código parcheado; el estado final difiere solo en los 30 B (6 entradas) de la
  tabla de PP y en `DT_REL` (dato que escribe el cargador, no el código).
- Las direcciones del subsistema de medios no caen en ningún rango modificado.

**Riesgo residual (POSIBLE, no medido aquí)**: (a) el *cargador real de la cámara* no se ha
emulado: el fichero tiene dos `PT_LOAD` más y un segmento RWX que la fábrica no tenía; los
comprobado estático dice que son cargables, pero un rechazo del cargador de Sony no se puede
descartar sin la cámara; (b) 3 de las 263 entradas (la #251 y dos que llaman a `_ZNSsC1Ev` y
`_ZNSt8ios_base4InitC1Ev`, símbolos `.dynsym` sin tipo) se quedan en la frontera del andamio, no
verificadas de punta a punta; (c) el código de PP parcheado, cuando se ejecute *después* del
arranque, queda fuera de esta medida.

## 6. Límites (NO_VERIFICADO)

- No se ha arrancado el arnés QEMU (`im.elf`) ni se ha usado la cámara: todo es carga estática de
  la biblioteca y ejecución de sus inicializadores en Unicorn.
- Las 1 798 importaciones (libc, libstdc++, libmpr…) son stubs que devuelven 0, con dos andamios
  distintos; los valores que la cámara obtendría de ellas no se reproducen.
- `RELATIVE`: con base 0 no se aplica nada (el valor del fichero ya es la VA); en la cámara el
  cargador sumaría la base. Es equivalente para comparar las dos versiones, no para medir la
  cámara.
- No se ha ejecutado `.fini_array` ni los `DT_INIT` (`0xDB3B9`, idéntico en ambas).
- Los scripts de evidencia se ejecutan con el Python del repo (`unicorn` 2.1.4) y no forman parte
  de `tests/`: no se ha añadido ni modificado ninguna prueba del proyecto.
