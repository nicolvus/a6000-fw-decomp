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
