# FILM-PB-1 / sub-arnés-orden — ejecutar 0x437BC0 por debajo de la UI (26-11-2026)

Estado: **manejador ejecutado en el arnés QEMU con el FeaCore real, por la vía real (orden 0x4000001D
encolada por `FeaIf::PlayMovie`) y por llamada directa**. Cámara no usada (ni red, ni USB, ni `adb`;
nada flasheado). Espacio de direcciones: **VA del ELF** de `libmpr.so` 3.21 del arnés
(`fw321/.../dev/nflasha15_unpacked_unpacked/lib/libmpr.so`). Perfil propio y corto:
`analysis/gui/g22/harness/live/pbo/` (sólo el `sonyshim.so` instrumentado). No se ha tocado el shim del
arnés, ni `docs/`, ni `knowledge/`, ni `build/`, ni ficheros de otros subagentes.

## 0. Resultado en una tabla

| Puerta del manejador | Cuándo se evalúa | Medición en el arnés | Código final |
|---|---|---|---|
| `[core+0x1F0] == 5` | 1.ª instrucción útil (`0x437BDE`) | **estado real tras `MprCtrl::Init` = 2**; con la orden real y el estado real contesta aquí | **`0x0A`** (`0x437BE8`), sin tocar las guardas |
| guarda A `0x447A1E` («dsm get») | `0x437BFA`, con estado 5 y `ctrl != NULL` | `0x447810(ent=0x1F68518, **media=0**, mask=0)` → error → guarda A = 0 | **`0x1A`** (`0x437C0A`) |
| guarda B `0x447F26` («unsupported content») | `0x437C2C` | **no se ejecuta** (A falla antes) | — |

**Discriminante medido: salta la guarda A, no la B.** El manejador llega a `0x437BFA` con
`[core+0xDC0] = 0` (handle de media) y `[core+0xDB8] = 0` (máscara); `0x447810` devuelve error, la guarda
A devuelve 0, se registra `" Pb Disable!! ref) dsm get"` y el código final es **`0x1A`**. Ese handle sólo
lo rellena `EnterMoviePb` (`0x437A28`, orden `0x40000017`; comprobado en la búsqueda binaria del
despachador: `0x429D24 → 0x42A2F2 → 0x437A28`), que exige estado 2 y un bloque de parámetros con la media
ya enumerada. Es decir: **el fallo del arnés está antes del contenido**; la lista vacía y la
guarda A son el mismo cuello de botella.

## 1. Cómo se ha ejecutado

Shim propio `reports/evidence/film-pb-1-sub-arnes-orden-20261126/sonyshim-orden.c` (copia del del arnés +
un hilo `PBINJECT`), compilado con los mismos flags de `shim/build.sh` pero apuntando a esa copia e
instalado como `OVERLAY2` en el perfil `pbo` (sustituye a `/usr/lib/sonyshim.so` sin tocar el overlay
compartido).

`PBINJECT=N` hace, en un hilo del shim:

1. Espera N s y sondea cada segundo `MprIfMcmd::mp_feaCore` (`libmpr+0xAD489C`) hasta que existe; espera
   10 s más (deja terminar el arranque).
2. Resuelve los objetos reales por símbolo dinámico:
   - `MprIfMcmd::mp_mprIf` (`libmpr+0xAD3D90`) → `MprIf*`; `[MprIf]` = `FeaIf*`; **`[FeaIf+4] == FeaCore`**
     (comprobado en ejecución: `0x1F68470+4 = 0x8DEDC008`).
   - `MprIfMcmd::mp_feaCore` = `FeaCore*`.
   - `ctrl`: el objeto estático que usa la propia UI (`MprIfMcmd::PlayMovie`, `0x737FBA` →
     `libmpr+0xAD3CB4`), copiado a pila: `00000001 00000000 00000001 00000000 …`.
3. **Vía (a)**: llama al `FeaIf::PlayMovie` real (`dlsym` → `base+0x44EE9D`) con
   `(regionId=0, MPR::EntryId a ceros, RSMPoint=NULL, ctrl)` — la misma firma que usa `MprIf::PlayMovie`
   (`0x7229E0`). Es el código que arma el mensaje de 0x8C y encola la orden `0x4000001D`; no se fabrica
   el mensaje a mano.
4. **Vía (b)**: si (a) devuelve != 0, o si 2 s después el FeaCore sigue fuera del estado 5, escribe
   `[core+0x1F0]=5` y llama directamente a `0x437BC0` con los mismos argumentos que le pasa el
   despachador (`0x42A346–0x42A37A`): `(core, region, EntryId[6], RSMPoint*, ctrl*)`.
   `PBFORCE=1` fuerza el estado 5 **antes** de la vía (a), para medir la guarda con la orden real.

Instrumentación (armada **al cargar** la biblioteca, nunca en caliente; `TRACEREP=1`):
`TRACELIB=libmpr.so TRACEFN2=437bc0,437bfa,437c0a,437c10,437c2c,437c3c,437c70,437d1a,437d2c,447810,44ee9c`.
Los puntos no-entrada elegidos (`437c0a`, `437d1a`, …) son cabeceras de bloque cuya instrucción siguiente
se ejecuta siempre (no son ramas condicionales): es la condición real para que el paso de `TRACEREP`
rearme la trampa; el resto son entradas de función o `bl` que retornan.

```
PBINJECT=30 PBFORCE=1 python3 reports/evidence/film-pb-1-sub-arnes-orden-20261126/pb_run.py 420 \
  reports/evidence/film-pb-1-sub-arnes-orden-20261126/runF
# sin PBFORCE (estado real 2): …/pb_run.py 420 …/runD
```

`pb_run.py` construye el initrd como `run.py`/`live.py` (overlay del arnés + `pbo` + cabeza FAT32 de
`~/A6000-SD`) y arranca QEMU con `-serial file:consola.log`; el shim escribe su traza también en
`/dev/console`, así que el resultado se ve sin esperar al volcado final de `im.sh` y la VM se corta en
cuanto aparece `PBINJ FIN`. Con la carga de esta sesión el invitado va a ~0,4×: cada pasada ~4 min.

## 2. Traza medida (runF: vía (a) con estado 5)

```
PBINJ core=0x8DEDC008 mprIf=0x1F68460 [mprIf]=0x1F68470 [feaIf+4]=0x8DEDC008
PBINJ core: estado=0x2 ent=0x1F68518 id=0 mask=0 motor=0
PBINJ PBFORCE: estado 2 -> 5
PBINJ ctrl estatico 0xAD3CB4: 00000001 00000000 00000001 00000000 …
TRACE 44ee9c n=1 r0=1F68470 r1=0 r2=0 r3=0          ← FeaIf::PlayMovie(this, region=0, EntryId=0, rsm=0, ctrl)
PBINJ FeaIf::PlayMovie -> 0                          ← la cola ACEPTA la orden 0x4000001D
TRACE 437bc0 n=1 r0=8DEDC008 … lr=AE79C37F          ← lr = base+0x42A37F: la llamó el despachador real
TRACE 437bfa n=1 r0=1F68518 r1=0 r2=0 r3=5           ← guarda A: (entidad, media=0, máscara=0)
TRACE 447810 n=1 r0=1F68518 r1=0 …                   ← resolución de la media: puntero 0 ⇒ error 0x31000006
TRACE 437c0a n=1                                     ← rama « Pb Disable!! ref) dsm get » (movs r3,#0x1a)
TRACE 437d1a n=1 r2=1A                               ← código final 0x1A
TRACE 437d2c n=1                                     ← finalización (vtable+0x1c) y retorno
PBINJ tras 2 s: estado=5                             ← no hace falta la vía (b)
```

runD (sin `PBFORCE`) dio el contraste: la misma orden real, con el estado real 2, ejecutó `0x437BC0`
(`lr = base+0x42A37F`) y terminó en **`0x0A`** sin pasar por `0x437BFA`; la llamada directa posterior con
el estado forzado reprodujo la guarda A y el **`0x1A`**. runC (primera pasada) sirvió para descartar que
`MprIfMcmd::mp_owner` (`libmpr+0xAD4000`) sea el MprIf: **no lo es** (`[mp_owner]` cae fuera de libmpr);
el bueno es `mp_mprIf` (`+0xAD3D90`).

## 3. Lectura

- **La orden 0x4000001D llega al manejador real por la vía real**: `FeaIf::PlayMovie` → mensaje de 0x8C →
  cola del FeaCore → despachador `0x42A37A` → `0x437BC0`, con el FeaCore real. No hace falta la galería
  ni la UI.
- El **primer discriminante no es una guarda**: es el estado del FeaCore (`[core+0x1F0]`). En el arnés
  vale **2** y el manejador contesta **`0x0A`** en `0x437BE8`. Los únicos `ChangeState(5)` de libmpr están
  en callbacks del motor (`0x438160`, `0x4382E6`, `0x438332`, `0x438C12`), es decir, **después** de
  `EnterMoviePb` (`0x437A28`, orden `0x40000017`), que exige estado 2 y rellena `[core+0xDC0]` (media) y
  `[core+0xDB8]` (máscara). El caso `0x4000001D → 0x437BC0` también está comprobado en el mismo
  despachador (`0x429D10 → 0x42A346`).
- Con estado 5, salta **la guarda A**: `0x447810` recibe `media = 0`, devuelve `0x31000006`; `0x447A1E`
  devuelve 0; log `" Pb Disable!! ref) dsm get"`; **`0x1A`** en `0x437C0A`. La guarda B (`0x447F26`) no se
  ejecuta ni una vez (su punto `0x437C2C` no aparece en la traza).
- Consecuencia para el proyecto: el fallo del arnés es **falta de contexto de reproducción**
  (`EnterMoviePb`/media), no «contenido no soportado». Para pasar la guarda A hace falta ejecutar antes
  `0x437A28` con un handle de media real — y ese handle sale de la lista de contenidos que hoy está vacía.

## 4. Límites de la medición

- `MPR::EntryId` va a ceros y `RSMPoint=NULL` (la UI no ha enumerado nada). No afecta a la guarda A, que
  sólo usa `[core+0x1EC/0xDB8/0xDC0]`; sí dejaría la guarda B sin contenido real aunque se llegara.
- El estado 5 es **una precondición inyectada** en runF/runD-fase-b (se escribe `[core+0x1F0]=5`); se
  documenta como tal. La vía (a) sin forzar (runD) se ejecutó con el estado real 2.
- El `ctrl` es copia del objeto estático real (`libmpr+0xAD3CB4`); sus campos no influyen en la guarda A.

## 5. Reproducción

- Shim: `reports/evidence/film-pb-1-sub-arnes-orden-20261126/sonyshim-orden.c`; el comando exacto de
  compilación y ejecución está en `…/comando.sh` (deja el `.so` en
  `analysis/gui/g22/harness/live/pbo/overlay/cam/usr/lib/`).
- Lanzador: `…/pb_run.py` (usa `HOME` real: la SD es `~/A6000-SD`; con otro `HOME` la tarjeta sale vacía).
- Registros: `…/runC/consola.log`, `…/runD/consola.log`, `…/runE/consola.log`, `…/runF/consola.log`
  (consola serie completa de cada arranque; `runD` y `runF` son las pasadas buenas).
