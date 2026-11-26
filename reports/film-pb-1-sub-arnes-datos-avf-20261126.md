# FILM-PB-1 — datos del invitado: volumen, `AVF_INFO/AVIN0001.INP` y hasta dónde llega el IFO MP4 en el arnés

26-11-2026 (reloj del anfitrión durante la sesión: 25-11-2026 23:31 → 26-11 00:xx, −03). Cámara **no usada**.
Todo ocurre en `qemu-system-arm` (`scripts/gui/harness/live.py`) y en lectura estática de `libmpr.so` 3.21.
Direcciones = **VA del ELF** de `libmpr.so` (en REA/Ghidra: +0x10000).
Evidencia cruda: [`reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/`](evidence/film-pb-1-sub-arnes-datos-avf-20261126/) ·
comando reproducible: [`comando.sh`](evidence/film-pb-1-sub-arnes-datos-avf-20261126/comando.sh).

**Contexto que cambia la pregunta**: el usuario formateó la tarjeta en la cámara y el vídeo sigue sin reproducirse ⇒
el índice `AVF_INFO` y el volumen quedan **descartados como causa**. Esta parte se limita a dejar el arnés con datos
válidos y medir si el arnés entra en la cadena del IFO.

---

## 0. Resumen (20 líneas)

1. La imagen FAT32 del invitado la construye `scripts/gui/harness/sd_image.py` desde la carpeta `~/A6000-SD`
   (`sd_emu.SD_DEFECTO`): `mkfs.vfat -F 32` sobre un superflojo de 4 GiB (fábrica SD), `mmd`/`mcopy` del árbol y
   **cabeza** (solo hasta el último dato) → `live.py:207` la mete en el initrd como `/cam/usr/share/sd.head`.
2. El shim (`sonyshim.c:131`) crea `/sd.img` de `SDSECT` sectores y copia la cabeza encima; el invitado lo monta como
   `/dev/mmca`. **Verificado**: el volcado de `/sd.img` del invitado es la cabeza byte a byte (22 986 752 B).
3. El índice AV que consume `libmpr` es `AVF_INFO/AVIN0001.INP` (descriptor `.data` 0x9D1270; constructor de rutas
   0x12C5C8 con `+0xBC = 0x7A912C`). El invitado **sí** recorre ese directorio: sus trazas nombran
   `A:\AVF_INFO\PRV00001 BIN` y `A:\AVF_INFO\AVIN0001 BNP` con la etiqueta `A6000SD` de mi imagen; el `.INP` no se nombra.
4. Generé `AVIN0001.INP` con la rejilla verificada (registro 0x80 B) y `cDirPath=MP_ROOT/100ANV01`, la ruta de la
   plantilla del propio binario (`0x7ACAEC` `/MP_ROOT/100ANV01/MAH%05ld.MP4`), y puse el clip **en esa misma ruta real**
   de la imagen (antes se usaba `103ANV01`, que no sale de ninguna plantilla).
5. La tarjeta final lleva `AVF_INFO` coherente: `AVIN0001.INP` = `AVIN0001.BNP` (384 B idénticos) + `AVIN0001.INT` y
   `PRV00001.BIN` (los cuatro nombres que el invitado sondea), y un MP4 sintético pero bien formado (14 540 590 B,
   `mvhd` 9,5095 s, 1440×1080, `avc1`).
6. Auditoría sobre copia extraída de la imagen: **0 avisos** (`mvhd` 9,51 s vs índice 9510 ms; tamaño igual; bValid=1).
7. El auditor del repo **revienta con más de un fichero en `AVF_INFO`** (`sorted()` sobre `dict`s): con el `.INP` solo
   pasa; con el juego coherente hay que usar la copia arreglada de la evidencia (un cambio de 3 líneas, documentado).
8. Con el volumen montado en el invitado (corrida 1: invitado 44–530 s, 49 535 líneas de registro) **no aparece ni una
   línea de `mp4Ifo` / `CreateAndLoad` / `LoadSub` / `RcsBackup` / `FlashLoad` / `CheckSalvage`**, y las trampas dan
   mutex 0x5BAD00 ≥16 y ctor `mp4Ifo_If` 0x6E80A4 = 2, como en sesiones anteriores; 0x6E8430/0x61A8F0/0x608698 = 0.
9. `mp4Ifo_General::Load` está localizado en esta sesión: **0x698FB8** (literales `0x914FA6`/`0x914FC8` en el pool
   0x699008/0x699018). Se llama desde 0x6EC1E6, 0x6EE006 y 0x6EE13A; `FlashLoadMp4` (0x627BEC) desde seis sitios del
   despachador de `AviMMgrCmd` (0x62A326…0x6307E6), y `CreateAndLoad` (0x67CA6C) desde 0x627C60 y otros tres.
10. Veredicto: en el arnés **no se ejecuta el camino del IFO MP4** porque no arranca el gestor de vídeo (`AviMMgr`/`MMgr`),
    no porque falten datos: el volumen monta, el índice está y el clip existe.
11. El arnés es **inestable en frío**: de 4 arranques, 1 llegó a la pantalla de disparo (17 fotogramas a 307 s), 1 pintó
    2 fotogramas y se quedó a medias, y 2 no pintaron nada — los malos acaban en el bucle `uipc snd_sync_msg qid=0x720018`
    hacia los ~215–500 s. Cualquier medida de la cadena de vídeo necesita un arranque bueno (subir `LIVE_ARRANQUE_MAX`).
12. Lo que falta (siguiente): que el `MMgr` de vídeo reciba su primera orden (`MprCtrl::Init` → cola de `AviMMgrCmd`) para
    que `CreateAndLoad`/`Load` se ejecuten; ahí sí se podrá decir qué rechaza el IFO. La tarjeta ya no es el eslabón.
13. **Entregado**: la tarjeta del arnés (`$HOME/A6000-SD`, la de `estable.sh`) queda con el MP4 en
    `MP_ROOT/100ANV01/MAH04198.MP4` (+ copia en `PRIVATE/M4ROOT/CLIP/C0001.MP4`), el índice de 2 registros que también
    cubre la copia `MP_ROOT/103ANV01` que ya había, e `AVF_INFO` coherente; imagen de 54 034 432 B y auditoría
    **0 avisos** sobre la copia extraída de la imagen y sobre la carpeta de origen (§8).

---

## 1. Dónde se construye la imagen del invitado y dónde vive el `AVF_INFO`

Cadena completa, con la línea que lo hace:

| Paso | Dónde | Qué hace |
|---|---|---|
| 1 | `scripts/gui/harness/sd_emu.py:25` | `SD_DEFECTO = Path.home()/"A6000-SD"` — la tarjeta de origen es una carpeta del anfitrión |
| 2 | `scripts/gui/harness/sd_image.py:36` `construye()` | `mkfs.vfat -F 32` sobre 4 GiB, 512 B/sector, sin tabla de particiones (norma SD); `mmd` de `DCIM`, `DCIM/100MSDCF`, `PRIVATE`, `PRIVATE/M4ROOT`, `PRIVATE/M4ROOT/CLIP`, `PRIVATE/AVCHD` (+ `SUB/THMBNL/GENERAL/AVF_INFO` solo con `SD_ESTRUCTURA=1`); `mcopy -s` de cada carpeta de la raíz; escribe **solo la cabeza** hasta el último dato |
| 3 | `scripts/gui/harness/live.py:207-208` | con `SDIMG=1` (va en `TARJETA_ENV`) construye la cabeza y la pasa a `run.build_initrd` |
| 4 | `scripts/gui/harness/run.py:48` | la cabeza viaja al initrd como `/cam/usr/share/sd.head` |
| 5 | `scripts/gui/harness/shim/sonyshim.c:131-133` | al abrir `/dev/mmca`: `ftruncate(4 GiB)`, copia la cabeza a `/sd.img`; `ioctl 0x104/0x10f/0x110` sirven geometría y sectores |
| 6 | `libInfraFsys` del invitado | lee la FAT32 y resuelve `ms:/…` como unidad **A:** (`[ObjMedia]Fsys_GetDriveInfo('A') OK`) |

`AVF_INFO` es la carpeta del **índice AV de `libmpr`**, no de `libInfraFsys`:

- Descriptor en `.data` **0x9D1270**: `"AVIN0001.INP"`, `0x80` (registro), `0x2710` (máx. 10000), centinela `0xFFFFFFFF`,
  y el **file-ID de 16 B** `ff067581 fa7be290 452784b0 5e6110ad` (ver `film-pb-1-sub-avin-20261127.md` §1-2).
- Constructor de rutas **0x12C5C8** (`film-pb-1-sub-rcsbackup-20261126.md` §4.1): `ldr r0,=0x7A912C` = `"AVIN0001.INP"`
  y `bl 0x1D238C` compone `<pref>[AVF_INFO]<sep>[AVIN0001].INP`; el volcado de la clase imprime `Prefix`/`Separator`
  (`0x7A6120`) ⇒ `cDirPath` va **relativa al prefijo**, sin barra inicial.

Que el invitado lo usa de verdad está medido en §4.

## 2. El `.INP`: rejilla verificada, cabecera **no** verificada y ruta elegida

Generador: [`gen_tarjeta.py`](evidence/film-pb-1-sub-arnes-datos-avf-20261126/gen_tarjeta.py) (solo stdlib).

Registro de 0x80 B — rejilla **verificada** en bytes de `libmpr` (`film-pb-1-sub-avin-20261127.md` §3):

| Off | Tipo | Campo | Puesto a |
|---|---|---|---|
| +0x00 | `char[0x12]` | `cDirPath` | `MP_ROOT/100ANV01` |
| +0x12 | `char[0x0E]` | `cFileName` | `MAH04198.MP4` |
| +0x20 | `u32` | `nFileSize` | 14 540 590 (= tamaño real del fichero en la imagen) |
| +0x24 | `u8` | `bValid` | 1 |
| +0x28/+0x2C | `u32`×2 | `nWidth`/`nHeight` | 1440 / 1080 |
| +0x30 | `u32` | `nDuration` (ms) | 9510 |
| +0x34 | `u32` | `Duration90kHz` | 855 900 |
| +0x38 | `u32` | `emVideoCodec` | 4 (AVC) |
| +0x3C | `u32` | `emProfileIndication` | 2 (MAIN) |

Cabecera 0x100 B: **NV** (file-ID de 16 B + versión 1 + 0x80 + 0x2710 + nº de contenidos 1). Es la única pieza que no
sale de bytes del binario; el lector del repo no la necesita (ancla en el nombre ASCII) y el invitado no la ha rechazado
de forma visible (§4).

Ruta elegida: la **plantilla del propio binario** `0x7ACAEC` `/MP_ROOT/100ANV01/MAH%05ld.MP4` (junto a
`0x7ACD2C` `/M4ROOT/CLIP/C%04ld.MP4` para XAVC). El clip está en esa ruta dentro de la imagen, así que índice y volumen
coinciden; `103ANV01` (usado en la sesión del 25-11) no sale de ninguna plantilla.

Clip: MP4 sintético mínimo (`ftyp` MSNV + `mdat` + `moov` con `mvhd` a 90 kHz y un `trak` de vídeo `avc1`), porque en el
repo **no hay ningún `.mp4`**. `mvhd` = 855 855/90 000 = 9,5095 s ⇒ índice 9510 ms (delta 0,5 ms).

## 3. Auditoría sobre una copia extraída de la imagen

```
$ MTOOLS_SKIP_CHECK=1 mcopy -i /tmp/fpb1-datos2/img/sd.head -s -m -Q ::/AVF_INFO ::/MP_ROOT ::/DCIM ::/PRIVATE copia/
$ .venv/bin/python3 reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/audita_tarjeta_copia.py copia
raíz: /tmp/fpb1-datos2/copia
AVF_INFO: ['AVIN0001.BNP', 'AVIN0001.INP', 'AVIN0001.INT', 'PRV00001.BIN']
  MAH04198.MP4   dir=MP_ROOT/100ANV01 indice=   9510 ms mvhd=9.51 s tam=14540590 disco=14540590 bValid=1
avisos: 0
```

Dos defectos encontrados en el camino (ninguno del dato):

1. **`scripts/filmpb1_audita_tarjeta.py` revienta con ≥2 ficheros en `AVF_INFO`**:
   `TypeError: '<' not supported between instances of 'dict' and 'dict'` en el `sorted(...)` del listado (§línea 81).
   Con la tarjeta real (`.INP`+`.BNP`+`.INT`+`PRV…`) siempre revienta ⇒ nunca se ha ejecutado contra una tarjeta real.
   Arreglo de una línea (`sorted(..., key=lambda d: d["fichero"])`). **No** se ha tocado el fichero del repo: la copia
   arreglada está en la evidencia ([`audita_tarjeta_copia.py`](evidence/film-pb-1-sub-arnes-datos-avf-20261126/audita_tarjeta_copia.py), con `diff` en `07-…txt`).
2. El propio auditor detecta bien un `mvhd` mal escrito: con la primera versión del MP4 (campos desplazados) dio
   `índice 9510 ms / mvhd 77 ms` y salida 1; corregido el `mvhd`, 0 avisos. Sirve de control positivo.

## 4. Qué ve el invitado (medido en la corrida 1)

Corrida 1 (`live/datos-avf`, tarjeta con **solo** `AVIN0001.INP`, `HOME=/tmp/fpb1-datos`, `SDIMG=1`,
`SHIMEXTRA='WAITLOG=6000 WLALL=1 TRACELIB=libmpr.so TRACEFN2=… TRACEREP=1'`), registro del invitado 44,3–530,0 s,
49 535 líneas:

```
471.84 110.39 LOG 31 B  MediaMount /dev/mmca
474.38 112.83 TRAZA [ObjMedia]Fsys_GetDeviceInfo("/dev/mmca") OK
474.45 112.99 LOG 31 B  FsysMount /dev/mmca
474.90 113.45 TRAZA fufsys_SetDeviceInformation() ans = 0
474.91 113.46 TRAZA [ObjMedia]Fsys_GetDriveInfo('A') OK
542.80 180.40 TRAZA 0   A:\AVF_INFO\PRV00001 BIN A6000SD -
542.81 180.63 TRAZA 0 2 A:\AVF_INFO\AVIN0001 BNP A6000SD -
565.36 203.91 TRAZA 0 c' A:\AVF_INFO\AVIN0001 BNP A6000SD -
```

- El volumen **monta** y el invitado lo llama unidad **A**; `A6000SD` es la etiqueta FAT de mi imagen, así que esas
  rutas son la tarjeta emulada, no otra cosa.
- 37 lecturas de sector (`SDIO leer fd=55 a=… b=…`) de `libInfraFsys` sobre la imagen.
- Sondea `PRV00001.BIN` y `AVIN0001.BNP` **por nombre**; `AVIN0001.INP` no aparece nombrado en ninguna línea.
- El volcado del `/sd.img` del invitado (`POST /sd-volcado`, 22 986 752 B) tiene el mismo `mdir` y los mismos ficheros
  que la cabeza construida: lo que lee el invitado es exactamente lo que se sembró (`05-…txt`).

Con la tarjeta coherente (corrida 3, perfil `d3`) el montaje vuelve a salir a los 54 s del invitado ⇒ añadir
`.BNP/.INT/PRV00001.BIN` no rompe el montaje.

## 5. ¿Llega el arnés a `mp4Ifo_General::Load`?

**No hay ni un disparo de la cadena del IFO MP4.** `mp4Ifo_General::Load` = **0x698FB8** (localizado en esta sesión por
sus literales ` mp4Ifo_General::Load IN (device=` `0x914FA6` y `…OUT()` `0x914FC8`, pool en 0x699008/0x699018;
`calls` → 0x6EC1E6, 0x6EE006, 0x6EE13A). La cadena estática es
`AviMMgrCmd::MountCmd 0x626DB8` → `GetDeviceInfo 0x625C4C` → `FlashLoadMp4 0x627BEC`
(`calls` 0x62A326, 0x62C5EE, 0x62D56A, 0x62F002, 0x62FE5E, 0x6307E6) → `MMgrMp4IfoAcsr::CreateAndLoad 0x67CA6C` →
`LoadSub 0x67C8CC` → `Load` → `mp4Ifo_General::Load 0x698FB8` → `FlashLoadForMsv` → `RcsBackupTblData`.

Medido:

| Punto | Trampa | Corrida 1 (volumen montado, 530 s) |
|---|---|---|
| mutex `ifoFramework_Semaphore::Acquire` | 0x5BAD00 | **≥16** (todas con dueño 0: mutex libre) |
| ctor `mp4Ifo_If` | 0x6E80A4 | **2** (el objeto existe) |
| `AviMMgr::MovieReadStart` | 0x608698 | 0 |
| `AviMMgr::isSupportContent` | 0x61A8F0 | 0 |
| `GetPlayThumbnailInfo` | 0x6E8430 | 0 |
| `MMgrMp4IfoAcsr::CreateAndLoad` | 0x67CA6C | **no medido** (corridas 2/3 no llegaron a montar) |
| `LoadSub` / `mp4Ifo_General::Load` | 0x67C8CC / 0x698FB8 | **no medido** (ídem) |
| mensajes `FlashLoadMp4`/`CreateAndLoad`/`LoadSub`/`RcsBackupTblData`/`CheckSalvage` en el registro | — | **0 líneas** en 49 535 líneas |

Es decir: el objeto `mp4Ifo_If` se construye (2 veces) pero **el gestor de vídeo no llega a pedirle nada**; las funciones
que fallan en la cámara (`CreateAndLoad`, `LoadSub`, `mp4Ifo_General::Load`) están **por debajo** del primer comando que
aquí no ocurre. `AviMMgrCmd` es el despachador de `libmpr`: recibe órdenes por cola y solo entonces llama a
`FlashLoadMp4`. En el arnés no hay ninguna orden de ese despachador en 530 s.

Nota de método: las tres corridas con las trampas nuevas (0x67CA6C/0x698FB8/0x627BEC/0x625C4C/0x626DB8) no sirvieron
— dos no llegaron a montar (`08-…txt`) y en la tercera, que sí montó y pintó 2 fotogramas, no disparó **ninguna** trampa
(ni siquiera la del mutex, que en la corrida 1 da ≥16), señal de que el armado en esa corrida no quedó bien; la corrida 1,
que sí montó, no llevaba esas direcciones. El **"no"** de arriba se apoya en el registro completo de la corrida 1
(0 líneas de la cadena) y en los puntos que allí sí estaban armados.

## 6. Qué falta y cómo se sigue

1. **Que arranque el gestor de vídeo en el arnés**: es lo único que separa al invitado de `CreateAndLoad`. Camino:
   `MprCtrl::Init` debe entregar la primera orden a `AviMMgrCmd` (la cola que en la cámara despierta a `HddDcfMMgr` y a
   `MMgrMp4IfoAcsr`). Aquí `HddDcfMMgr` sí espera en su `cond_wait` (`libmpr.so+0x64dd5b`), pero no recibe trabajo de vídeo.
2. Cuando eso ocurra, las trampas ya están listas: `0x67CA6C` → `0x67C8CC` → `0x698FB8`. El primer punto que dé 0 dice
   dónde se corta; el código de retorno (`0xB0800001` genérico vs. `0xB0400005/0xB0510001/0xB0F30001` específicos) es el
   que distingue "IFO corrupto" de "volumen ilegible" (`film-pb-1-sub-mount-ifo-20261126.md` §0.10-0.11).
3. **No** hace falta más trabajo sobre la tarjeta: el volumen monta, el índice está con la rejilla verificada y el clip
   existe en la ruta que el índice dice, con tamaño y duración coherentes.
4. Arreglar el `sorted()` de `scripts/filmpb1_audita_tarjeta.py` (una línea) para que el auditor sirva con una tarjeta real.
5. Robustez del arnés: 3 de 4 arranques en frío se colgaron en `uipc snd_sync_msg qid=0x720018` (≈215–500 s, sin
   pantalla). Cualquier medida de la cadena de vídeo necesita un arranque que llegue al primer fotograma (el bueno: 307 s).

## 7. Ficheros y comandos

Evidencia (`reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/`):

| Fichero | Qué es |
|---|---|
| `gen_tarjeta.py` | tarjeta + `AVIN0001.INP` (rejilla 0x80 B) + `.BNP/.INT/PRV00001.BIN` + MP4 sintético |
| `audita_tarjeta_copia.py` | copia del auditor del repo con el `sorted(..., key=…)` (diff en `07-…txt`) |
| `comando.sh` | reproducción completa (tarjeta → imagen → copia → auditoría → arnés) |
| `01-tarjeta-origen.txt` … `08-corrida2-sin-montaje.txt` | árbol, `mdir`, auditoría, registro del `.INP`, `/sd-img` del invitado, extractos de las corridas |
| `09-tarjeta-servida-al-arnes.txt` | la tarjeta entregada (`$HOME/A6000-SD`): contenido, `sha256`, `mdir` de la imagen y auditoría |

```
# 1) tarjeta + índice (raíz canónica del arnés: $HOME/A6000-SD); 2) imagen; 3) copia + auditoría; 4) arnés
.venv/bin/python3 reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/gen_tarjeta.py ~/A6000-SD --extra-dir MP_ROOT/103ANV01
LIVE_REINTENTOS=1 LIVE_ARRANQUE_MAX=700 \
SHIMEXTRA='WAITLOG=6000 WLALL=1 TRACELIB=libmpr.so TRACEFN2=5bad00,6e80a4,67ca6c,67c8cc,698fb8,627bec,625c4c,626db8 TRACEMAX=2 TRACEREP=1' \
  .venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir d5 --puerto 8626
# (o, con el arnés estable: sh scripts/gui/harness/estable.sh <perfil> live)
# (perfil corto: el camino de live/<perfil>/mon.sock debe caber en 108 B; «datos-avf2» ya no cabe)
```

`sha256`: `.INP` `7693b1ee708ca623f2e68315a3edeadbaae1a64381981fd4f4a62556a56f4f0a` (384 B) ·
MP4 `6e66e43d3b987c2482a7d3373ec1fffd18c790fe02638ac84264a38d00245d8d` (14 540 590 B) ·
cabeza `94887a71e14b58597a9f124c5f3dfd1538cf137c56c1d31f6f733c92f5b7e65b` (22 999 040 B).
No se ha tocado `docs/`, `knowledge/`, `build/`, `scripts/` ni `tests/`; solo este informe y su carpeta de evidencia.

---

## 8. Entrega: la tarjeta que consume el arnés

Raíz por omisión de `live.py`/`estable.sh` (`sd_emu.SD_DEFECTO = Path.home()/"A6000-SD"`), sin variables de entorno:

```
$HOME/A6000-SD
├── AVF_INFO/AVIN0001.INP     512 B  índice = cabecera 0x100 + 2 registros de 0x80
├── AVF_INFO/AVIN0001.BNP     512 B  idéntico al .INP (respaldo)
├── AVF_INFO/AVIN0001.INT     256 B  file-ID + ceros (el invitado lo sondea por nombre)
├── AVF_INFO/PRV00001.BIN     256 B  idem
├── MP_ROOT/100ANV01/MAH04198.MP4   14 540 590 B  ← ruta que da la plantilla 0x7ACAEC (clip generado aquí)
├── MP_ROOT/103ANV01/MAH04198.MP4   14 545 696 B  ← copia que ya estaba en la tarjeta (otra parte); indexada con SUS
│                                                  valores (1920×1080, 9,5095 s) para no dejar un clip huérfano
├── PRIVATE/M4ROOT/CLIP/C0001.MP4   14 540 590 B  ← copia en la ruta XAVC S (sd_emu.ruta_clip)
└── DCIM/100MSDCF/DSC0000{1,2,3}.JPG  (las tres fotos que ya estaban; no se ha borrado nada)
```

Registros del `.INP` (0x80 B cada uno, rejilla verificada):

| # | `cDirPath` | `cFileName` | `nFileSize` | W×H | `nDuration` | `Duration90kHz` |
|---|---|---|---|---|---|---|
| 0 | `MP_ROOT/100ANV01` | `MAH04198.MP4` | 14 540 590 | 1440×1080 | 9510 ms | 855 900 |
| 1 | `MP_ROOT/103ANV01` | `MAH04198.MP4` | 14 545 696 | 1920×1080 | 9510 ms | 855 900 |

- Imagen resultante (misma función y 4 GiB que usa `live.py`): **8 388 608 sectores**, cabeza de **54 034 432 B**
  (`sha256 10e8e4539bf9…`), por debajo del tope de 256 MiB de `sd_image.py`. Ojo: la cabeza viaja dentro del initrd
  (`/cam/usr/share/sd.head`), así que el initrd crece esos 54 MB.
- **Auditoría: 0 avisos**, sobre la copia extraída de la imagen (`mcopy`) **y** sobre la carpeta de origen:

```
  MAH04198.MP4   dir=MP_ROOT/100ANV01 indice=   9510 ms mvhd=9.51   s tam=14540590 disco=14540590 bValid=1
  MAH04198.MP4   dir=MP_ROOT/103ANV01 indice=   9510 ms mvhd=9.5095 s tam=14545696 disco=14545696 bValid=1
avisos: 0
```

- `C0001.MP4` no lo audita el script (su patrón exige `[A-Z0-9]{4}[0-9]{4}.MP4`, no `C0001`), pero es byte a byte el
  mismo fichero que el de `100ANV01`, así que tamaño y `mvhd` coinciden.
- Repetir desde cero (idempotente; **no** borra los JPG ni la copia de `103ANV01`):

```
.venv/bin/python3 reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/gen_tarjeta.py ~/A6000-SD --extra-dir MP_ROOT/103ANV01
cp ~/A6000-SD/MP_ROOT/100ANV01/MAH04198.MP4 ~/A6000-SD/PRIVATE/M4ROOT/CLIP/C0001.MP4
.venv/bin/python3 reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126/audita_tarjeta_copia.py ~/A6000-SD   # 0 avisos
```

- `estable.sh` reconstruye la cabeza en cada arranque en frío desde esa carpeta y ya cuenta los clips
  (`tarjeta: 3 clip(s) y 3 foto(s)`); **no** hay que copiar la imagen a mano. Si el perfil tiene estado guardado
  (`estado.zst`) y la huella no cambia, el initrd —y por tanto la tarjeta— es el viejo → usar **perfil nuevo** tras
  cambiar la tarjeta.
