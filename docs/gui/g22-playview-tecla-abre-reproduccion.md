# G22-PLAYVIEW — pulsar Reproducción abre la vista de reproducción (medido 27-11-2026)

**Estado: MEDIDO. La tecla abre la vista; la vista no tiene contenido que pintar.** Con el interruptor
`PLAYVIEW=1` del shim, una pulsación real de **Reproducción** (`0x1f7` por el driver de entrada) ejecuta
las dos funciones del firmware que en 3.21 no tienen llamante y **la vista de reproducción se instancia**.
La pantalla cambia (la OSD de disparo se destruye) y queda en blanco porque el **modelo de contenidos
está vacío** (G22-PBMEDIA): `getModelInfo(model/MEDIA, 0) = 0`.

## 1. Cómo se midió

```
# shim reconstruido en el DIRECTORIO DE TRABAJO del arnés (no en analysis/…: ver §4)
bash scripts/gui/harness/setup.sh /home/nicolas/hv/harness
cd /home/nicolas/hv/harness && rm -rf live/pv2
SHIMEXTRA='PLAYVIEW=1 WAITLOG=3000 WLALL=1' LIVE_ARRANQUE_MAX=200 LIVE_REINTENTOS=4 \
  /home/nicolas/a6000-arnes/.venv/bin/python /home/nicolas/a6000-arnes/scripts/gui/harness/live.py \
  /home/nicolas/hv/harness --perfil-dir pv2 --puerto 8699 --config /tmp/final/cfg.json
# cuando /estado da opacos ≥ 0,05 y listas ≥ 20:
/home/nicolas/a6000-arnes/.venv/bin/python scripts/gui/harness/e2e_drv.py 8699 \
  png=/tmp/pv2-antes.png esp=1 reproduccion esp=12 png=/tmp/pv2-despues.png
```

## 2. Lo que sale en el registro del invitado

```
194.65 27.18 PLAYVIEW: trampa en libObj+0x1106b8 (InputService::createEvent; el codigo va en r1)
...
402.12 [shim] PLAYVIEW n=1 convertViewEventToAB(0x150100f2) -> 1 accion=4 (tabla libScalarDaemon+0x19db0c)
402.12 [shim] PLAYVIEW n=1 openView(view/INDEX_PLAYBACK,0) -> 33914200
402.36 231.86 LOG   83 B  Vn 03F_viewUnified3.so
402.36 231.87 dlopen(viewUnified3.so) ...
402.36 231.88 dlopen(viewUnified3.so) -> 0x3f759778
```

Es decir, en el mismo instante de la pulsación: (1) el traductor del propio firmware
(`convertViewEventToAB`, `libScalarDaemon+0x13a704`) devuelve **acción 4** para `0x150100f2`; (2)
`viewManagerIf::openView("view/INDEX_PLAYBACK", 0)` acepta; (3) el cargador bajo demanda de `libObj`
hace `dlopen(viewUnified3.so)` y la fábrica `ViewIndexPbToInstance` crea la vista (`Vn 03F_…`).

Antes de esto, la misma pulsación sin `PLAYVIEW` daba **0 disparos** en `libScalarDaemon+0x13a704`,
`libObj+0x1170e8` (`ScalarView::TriggerTableEvent`), `libObj+0x116bd0` y `execAction` (`+0x11817e`)
(§10 de [g22-reproduccion-dispatch](g22-reproduccion-dispatch.md)).

## 3. Medida de la pantalla

| Momento | `/estado` | PNG |
|---|---|---|
| Antes de pulsar | 66 fotogramas · **193 listas** · opacos 0,0902 | `00-antes.png` |
| Después de pulsar | 71 fotogramas · **0 listas** · opacos 0,0 | `01-despues.png` |

- **La pantalla cambia:** 347 de 480 filas del PNG son distintas (`00-antes.png` frente a
  `01-despues.png`). La OSD de disparo se destruye, que es lo que hace un cambio de vista de verdad.
- **Queda en blanco:** 0 píxeles opacos. El fotograma posterior no lleva ni una lista de dibujo: la vista
  de reproducción no tiene nada que componer porque el modelo de contenidos no está
  (`getModelInfo(model/MEDIA, 0) = 0`, [G22-PBMEDIA](g22-pbmedia-indice-avf.md)).

## 4. Trampa de operación que costó una tanda (para no repetirla)

`setup.sh` escribe el shim **en el directorio que se le pasa**, y `live.py` lee el shim y el `initrd` del
**suyo** (`/home/nicolas/hv/harness`), no de `analysis/gui/g22/harness`. Si se reconstruye
`analysis/gui/g22/harness`, el invitado sigue arrancando con el `sonyshim.so` viejo y los interruptores
nuevos **no se arman sin decir nada** (`PLAYVIEW` mira `getenv` y retorna en silencio). Comprobación de una
línea antes de medir: `strings <DIR_TRABAJO>/overlay/cam/usr/lib/sonyshim.so | grep "PLAYVIEW: trampa"`, y
en caliente `linea=P 1106b8 2` debe devolver `00de` (la `UDF` de la trampa), no `f8b5`.

## 5. Qué queda

1. **Contenido** (G22-PBMEDIA): el medio se rechaza a los 65 s (`INH_INVALID_INFO_FS` → `RejectMedia()`)
   porque `FsysMount /dev/mmca` llega 1 s **después** de `DefObjMedia::onStarting`. Es un problema de orden,
   no de formato del índice (el `AVIN0001.INP` ya se genera bien).
2. Con el medio aceptado, `getModelInfo(model/MEDIA, 0) = 1` y la rejilla debería pintar; ahí se mide el
   diff de PNG contra el fotograma de disparo.
3. `PLAYVIEW` sigue **apagado por omisión**: es un interruptor del arnés (pone fuera del firmware el
   llamante que a 3.21 le falta), no un cambio de la cámara.

## 6. El medio se acepta: el índice va **sin** la cabecera de 0x100 (medido 27-11-2026)

Con `SD_MEDIA=1` (foto JPEG real + `AVF_INFO/AVIN0001.INP` coherente) y `INSHORT=1`, el montaje deja de
llegar tarde (`FsysMount /dev/mmca` a 64,98 s y `ClearInhStatus` a 64,99 s), pero el medio seguía
rechazándose más tarde con `SetInhStatus() [INH_INVALID_INFO_FS]` a los 74 s. La causa era el **formato del
índice**: `AVIN0001.INP` es un **vector puro de registros de 0x80 B**, sin la cabecera de 0x100 B que se le
suponía (el descriptor de `libmpr` `0x9d1270` da como tamaño máximo `0x138800` = 10 000 × 0x80 exacto).

| Tarjeta | `getModelInfo(model/MEDIA, 0)` | Pantalla al abrir la reproducción |
|---|---|---|
| índice con cabecera `0x100` (perfil `md1`) | **0** | 0 listas (en blanco) |
| índice sin cabecera (`SD_MEDIA_CAB=0`, perfil `md2`) | **1** (a los 82,86 s) | 0 listas (en blanco) |

Con el medio aceptado, al abrir `view/INDEX_PLAYBACK` la vista pide **`@M010`** (id de `model/INDEX_PB`,
que solo aparece en `viewUnified3.so` y `viewUnified2.so`) y recibe **0**: ese modelo no lo ha creado
nadie, y por eso la vista sigue sin pintar (0 listas, opacos 0,0, fotograma vacío). Medido con `GMILOG=1`
en el perfil `md2`.

## 7. Lo que queda, en orden

1. **Crear `model/INDEX_PB`** (y `model/CONT_SHOTS_PB`) para que la rejilla tenga contenido: es el único
   eslabón que separa «la vista se abre» de «la vista pinta». Candidatos: los modelos se crean al arrancar
   por un evento del `ModelManager` (como `POSTROOTEV` hizo con `ModelStillRec`), o los crea la propia
   cadena de reproducción cuando el medio cambia (evento de inserción, `INSHORT`).
2. Con la rejilla pintada, medir el diff de PNG contra la pantalla de disparo y cerrar G22-REPRO.
3. Repetir con el índice real de la cámara cuando haya un `AVF_INFO` de fábrica para comparar el registro
   (geometría, fechas, códec) con el que genera `sd_media.py`.

## 8. `@M010` es un modelo con nombre propio y se puede precrear (medido en `md3`)

La orden de diagnóstico `M <nombre>` del shim llama a `ModelManager` por la ruta de *precreación*
(`PRECREATE`) con el id que `IdGenerator::Get(nombre)` da a ese nombre:

```
[shim] PRECREATE id=0x15 -> -1     # M model/INDEX_PB
[shim] PRECREATE id=0x10 ->  0     # M @M010   (se crea)
[shim] PRECREATE id=0x2f -> -1     # M model/CONT_SHOTS_PB
```

Es decir: **`@M010` no es `model/INDEX_PB`** (ese es `0x15`), y el modelo `0x10` **sí se deja crear**
(`PRECREATE -> 0`). Aun así, con el modelo creado, al abrir la vista la petición sigue devolviendo 0:

```
595.33 274.99 getModelInfo(@M010, 1) -> 0   (x5)
```

y el fotograma queda vacío (0 listas, opacos 0,0). Conclusión: el modelo existe pero `info = 1` no tiene
nada que devolver porque **nadie le ha cargado la lista de contenidos**; el siguiente paso es encontrar
quién llena ese modelo (el mismo `GetAVIndexContentInfoList` de `libmpr` que alimenta `model/MEDIA`), no
crearlo.

## 9. Ya está en la autoprueba (regresión permanente)

`autoprueba.py` tiene un paso nuevo, **`reproduccion-abre`**, que solo se ejecuta si el arranque lleva
`PLAYVIEW=1` en `SHIMEXTRA` (si no, lo dice y no lo cuenta). Captura el fotograma, pulsa **Reproducción**
(`0x1f7`) con el mismo camino que el usuario, y exige **≥ 100 filas distintas de 480** entre el antes y el
después:

```
.venv/bin/python scripts/gui/harness/autoprueba.py <work> --perfil-dir <perfil> --puerto <puerto> --config <config>
```

La medida que lo justifica: durante semanas la misma pulsación dejó el fotograma **idéntico** (0 filas);
hoy cambia la vista entera (347 de 480 filas). El umbral de 100 filas separa «la tecla no hizo nada» de
«la vista cambió» sin depender de la traza del invitado (`WLALL`), que no siempre está activa.
El cálculo vive en `_distintas()` con su test sin QEMU (`tests/test_gui_harness.py`).
