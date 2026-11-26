# G22-FECHA — «Ajuste fecha/hora → Fecha/Hora»: del `31-12-2037` a la hora del anfitrión

Rama `harness/g22-fecha` (worktree `/home/nicolas/h-fecha`), 26-11-2026. Arnés de la UI de G22
([g22-arnes-ui-qemu.md](g22-arnes-ui-qemu.md), §5.18z¹⁰–¹¹ es el estado anterior) con firmware Sony 3.21.

**Resumen.** La página mostraba una fecha que no es la del anfitrión por **tres eslabones encadenados**, los tres
medidos:

1. `ModelClock` (`model/CLOCK`, id `0x18`) **no existe** en el arnés —el arranque de modelos se queda dentro de
   `Mi 00A`, `ModelSalvage`—, así que la vista recibe ceros.
2. La vista `ViewDateSet` (`viewUnified6.so`) recorta los campos contra dos extremos: el máximo sale de la NVRAM real
   (`0x107004d` = `2037-12-31 23:59:59` empaquetado) y el mínimo de la **info 1** de `model/CLOCK`. El recorte es
   **campo a campo y satura al extremo contrario** (`v < mínimo → v = máximo`), así que cualquier campo fuera de rango
   acaba en el máximo de la NVRAM.
3. La info 1 que entregaba el arnés era la hora del instante de la consulta (o la primera «T» del arranque), siempre
   *por encima* de algún campo de la fecha ya leída → ese campo saltaba al máximo: `31-12-2037 23:59` (o `0:00` con la
   NVRAM de fábrica, las medidas de 13-11-2026).

Arreglado en el **dato que entrega el arnés** (`scripts/gui/harness/shim/sonyshim.c`), sin parchear ningún binario de
Sony: el shim responde `ViewBase::getModelInfo("@M018"/"model/CLOCK", 0/1)` **sólo cuando la llamada real falla**, con
la hora del anfitrión (info 0) y la **medianoche de ese mismo día** (info 1), usando las mismas claves y los mismos
constructores de parámetros que `ModelClock::onGetInfo` — incluido que `0x100` es un `PrmBool` (tipo 5) y no un
`Param<int>`. Resultado medido: `26 - 11 - 2026  2 : 15` con el anfitrión a las `02:15:39`, también tras restaurar un
estado guardado.

## 1. Cómo se abre la página (receta reproducida)

`MENU` → pestaña del **maletín** (`derecha` ×11: 1 cámara, 2 engranaje, 3 red, 4 aplicaciones, 5 reproducción,
6 maletín) → página **4** (`derecha` ×3) → `abajo` ×3 hasta «Ajuste fecha/hora» → `intro` → `abajo` («Fecha/Hora») →
`intro`. Secuencia verificada (la de §6.2, sobre un arranque en frío ya dibujado):

```sh
python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir fecha-h11 --puerto 8731
python scripts/gui/harness/e2e_drv.py 8731 menu esp=4 "derecha*8" esp=1.5 "derecha*3" esp=2 "derecha*3" esp=2 \
       "abajo*3" esp=1.2 intro esp=3 abajo esp=1.2 intro esp=4 png=fecha-hora.png
```

(14 `derecha` en total; con 11 se llega al maletín página 1 y las 3 últimas cambian de página. Si el arranque aún no ha
dibujado el menú, las teclas se pierden: esperar a que `/estado` muestre fotogramas y `último:` con «listas».)

## 2. Síntoma medido

| Estado del árbol | Lo que muestra la página | Evidencia |
|---|---|---|
| `HEAD` (shim compartido del arnés) | `0 - 0 - 0  0 : 00` | `img/g22-fecha-hora-antes.png`; widget con `r1=0` (todo ceros) |
| con el reloj del anfitrión en el shim (§4) | `31 - 12 - 2037  23 : 59` | `img/g22-fecha-hora-2037.png`; `TRACE 2e2e10 … r1=1f0c07f5` |
| **arreglado** | **`26 - 11 - 2026  2 : 15`** (anfitrión `02:15:39`) | `img/g22-fecha-hora-despues.png`; `TRACE 2e2e10 … r1=1a0b07ea` |

El `31-12-2037` que documenta la fila G22-E se reproduce **byte a byte**: el widget recibe
`r1 = 0x1F0C07F5` = año `0x07F5` (2037), mes `0x0C` (12), día `0x1F` (31) y `r2` = hora `0x17` (23), min `0x3B` (59).

## 3. Dónde se decide la fecha (estático, VERIFICADO sobre bytes)

Cadena completa, cada eslabón comprobado con `llvm-objdump -d --triple=thumbv7-none-eabi`:

| Pieza | Dirección | Qué hace |
|---|---|---|
| `ModelClock::onGetInfo` | `libObj+0x4f1250` | `switch` por info (0 = hora actual vía `osal_get_date` `0x4f10dc`; 1 = fecha inicial guardada en `+0x84…+0x8e`). Rellena la lista con `ParamList::add` y las claves `0x100` (marca) y `0x101…0x106` (año, mes, día, hora, min, seg) — instrucciones en `0x4f20da…0x4f2128` |
| `ViewDateSet` (vista, `viewUnified6.so`) | `+0x28560` (`ViewDateSetToInstance`), objeto con los campos en `+0x12c` (año), `+0x130` (mes), `+0x134` (día), `+0x13c` (hora), `+0x140` (min) | constructor `0x26b94` pone los campos a cero |
| `ViewDateSet::reload` | `+0x28d48` → `+0x28c80` | `getModelInfo("model/CLOCK", 0)` y copia `0x101…0x106` a los campos; **aborta** si `0x100` falta o vale 0 (`0x28cb0…0x28cba`) |
| `ViewDateSet` (rango) | `+0x29260` | `BackupManager::Bkup_Read(0x107004d)` y **desempaqueta** un valor de 64 bits: año = `(lo>>26)\|(hi<<6)`, mes = `(lo&0x3C00000)>>22`, día = `(lo&0x3E0000)>>17`, hora = `(lo&0x1F000)>>12`, min = `(lo&0xFC0)>>6`, seg = `lo&0x3F` |
| `ViewDateSet` (recorte) | `+0x29558` | recorta **campo a campo** (año, mes, día, hora, min) y **satura al extremo contrario**: `if (v > NVRAM) v = inicial; else if (v < inicial) v = NVRAM` (`0x29588…0x29594`; mismo patrón para la hora `0x295cc…0x295d8` y el minuto `0x295e0…0x295ec`). Los extremos salen de `+0x292ec` → `+0x29260` = NVRAM `0x107004d` y de `+0x292f8` → `+0x28e14` = **info 1** de `model/CLOCK` |
| llamada al widget | `+0x29360` (retorno `+0x293e2`) | empaqueta los campos (`0x293b0…0x293ce`) y llama la ranura `+0x1b0` del widget: **medido**, `r1` = año u16 \| mes<<16 \| día<<24 (`0x1A0B07EA` = 2026-11-26) y `r2` = hora \| min<<8 (`…0F02` = 02:15) |
| `PAS_BtnDateTime` (widget, `viewUnified2.so`) | `+0x2e2e10` | recibe esos dos registros (`r1/r2`), acota año ≤ `0x833` (2099), día ≤ `0x1f` y min ≤ `0x3c`, y pinta los campos |

## 4. Causa raíz (VERIFICADO, medida)

**(a) `ModelClock` no existe en el arnés.** El id `0x18` (`@M018`) no se instancia nunca: el arranque de modelos
publica `Tc 100` y crea `Mi FFE/001/0E7/038/06B/00A`, pero **`Mi 00A` no termina** (`B Mi 00A_libObj.so` sin su `E`;
`ModelSalvage` espera la notificación «información de salvamento estable», §5.18s) y el bucle `Ts`→`Md/Ms` que en la
cámara real define y arranca **todos** los modelos —incluido `Md 018`/`Ms 018` de las líneas 3790-3793 del registro
real `analysis/camera-dumps/mem-20261020-log/log.txt`— no llega a correr. Consecuencia medida: `getModelInfo(@M018, 4/5/0/1) -> 0`
en todas las aperturas de la página, y `PRECREATE`/`M model/CLOCK` → `-1` (no está en el mapa de `ModelManager`).

**(b) Cuando el dato llega, la vista lo satura a `2037-12-31 23:59`.** Con el shim entregando la hora del anfitrión,
`ViewDateSet` recorta cada campo contra `[info 1, NVRAM 0x107004d]`. La NVRAM real del perfil contiene
`0x107004d = fb 7e 3f d7 1f 00 00 00`, que con el desempaquetado de `+0x29260` es exactamente
**2037-12-31 23:59:59** (comprobado con esos bytes). La info 1 que entregaba el arnés era la hora actual *en el momento
de la consulta*: medida `info 0 = 01:28:51` y `info 1 = 01:28:56`, es decir la «fecha inicial» quedaba **5 s por
encima** de la fecha actual → cada campo pasaba al máximo de la NVRAM. Los campos del objeto en el momento de
pintar el widget (medidos con `TRACEDEREF=d0:12c:6`) eran `000007f5 0000000c 0000001f 00000000 00000017 0000003b` =
2037-12-31 23:59.

El recorte es **campo a campo y satura al extremo contrario** (`0x29582…0x29594`, VERIFICADO sobre bytes):

```
29582: ldr  r1, [r4]       ; v = campo actual
29584: ldr  r3, [r7,#0x1c] ; NVRAM (máximo)  <- +0x292ec -> +0x29260 (desempaqueta 0x107004d)
29586: ldr  r2, [r7]       ; inicial (info 1) <- +0x292f8 -> +0x28e14 (getModelInfo info 1)
29588: cmp  r1, r3
2958a: ble  0x29590
2958c: str  r2, [r4]       ; v > máximo  -> v = INICIAL
29590: cmp  r1, r2
29592: it   lt
29594: strlt r3, [r4]      ; v < inicial -> v = MÁXIMO
```

**Basta que un solo campo** del reloj actual quede por debajo del mismo campo de la fecha inicial para que ese campo
salte al máximo. Medido con la primera versión del arreglo (info 1 = primera «T», `01:50:17`, y el reloj del anfitrión
a las `02:07`): el minuto `7 < 50` -> la página mostraba `26 - 11 - 2026  2 : 59` (el minuto 59 de la NVRAM) y la traza
del widget daba `r1=1a0b07ea` (año/mes/día correctos) con `r2=…3b02` (hora 2, min 59). Con los campos a cero (cuando
`reload` aborta) sale `31-12-2037 0:00` —la cifra de la fila G22-E— porque con la fecha inicial a medianoche el `0` no
es menor que `0` en hora/min/seg y sólo saturan año, mes y día (prueba
`test_el_recorte_de_la_vista_satura_al_extremo_contrario`).

**(c bis) El tipo del parámetro `0x100` no es decorativo.** La vista no pide `get(0x100)` a secas: pide **tipo 5**
(`PrmBool`) y lee el byte de valor con un segundo salto. VERIFICADO sobre bytes en `viewUnified6+0x28ca6…0x28cb8`:

```
28ca6: mov   r0, r7
28ca8: mov.w r1, #0x100
28cac: bl    0x12260        ; trampolín: push {r7,lr}; movs r2,#5; pop {r7,lr}; b.w <ParamList::get@plt>
28cb0: cmp   r0, #0x0
28cb2: beq   0x28d28        ; sin 0x100 (o tipo distinto) → abandona el relleno
28cb4: bl    0x12258        ; trampolín: ldrb r0,[r0,#0xc] → valor del PrmBool
```

y para el año, `0x28cbe: movw r1,#0x101` + `bl 0x12276` (trampolín con `movs r2,#1` → `Param<int>`). Por eso el relleno
del shim crea `0x100` con el constructor de **`PrmBool`** (`libObj+0xe50e8`) y `0x101…0x106` con `Param<int>`
(`libObj+0xf0fb0`): con `0x100` creado como `Param<int>`, `get(0x100, 5)` devuelve NULL, la vista abandona en `0x28cb2`
y la página vuelve a `31-12-2037` (medido).

**(c) El widget recibe bien lo que le dan.** `0x2e2e10` sólo acota y pinta; con fecha válida del anfitrión muestra la
fecha del anfitrión (§5). No hay ningún defecto propio del conversor: el `2037` no nace ahí, nace en el rango de la
vista (§4b) y, antes, en la ausencia del modelo (§4a).

## 5. Arreglo (sólo el shim; ningún binario de Sony parcheado)

`scripts/gui/harness/shim/sonyshim.c`, en el gancho que ya existía de `ViewBase::getModelInfo`:

- Si la llamada real **falla** (`!r`) y el nombre es `@M018`/`model/CLOCK` y la info es **0 o 1**, se rellena la misma
  lista con las claves del modelo (`0x100` + `0x101…0x106`) usando los **mismos constructores de `libObj`** que
  `ModelClock::onGetInfo`: `Param<int>` (`libObj+0xf0fb0`, tipo 1) para `0x101…0x106` y **`PrmBool` (`libObj+0xe50e8`,
  tipo 5)** para `0x100` —la vista pide `get(0x100, tipo 5)`, así que un `Param<int>` ahí **no** sirve: medido, con tipo 1
  la vista no rellena y la página vuelve a `31-12-2037`—, y se añaden con `ParamList::add` (exportado). Si `ModelClock`
  existiera, la llamada real devolvería 1 y este relleno no se ejecutaría.
- **info 0** = hora local del anfitrión (misma fuente que la orden 2 de `0x90013d`: `date_local()`, alimentada por la
  línea «T» de `live.py` cada 30 s). **info 1** = **medianoche del día del anfitrión** (mismo año/mes/día; hora, min y
  seg a 0). Es la fecha con la que la vista recorta (§4b): al ser campo a campo menor o igual que la fecha actual,
  ningún campo salta al máximo de la NVRAM. (La primera versión entregaba aquí la **primera** «T» —el arranque—, que
  basta que tenga un campo mayor que el actual —p. ej. el minuto— para que ése salte a 59; medido.)
- `0x100` = `PrmBool` con valor 1 (la vista exige que no sea nulo, `0x28cb0…0x28cba`); `RELOJ100=n` lo cambia para medir.
  `RELOJEMU=0` apaga todo el respaldo; `RELOJINIT=1` da la fecha inicial de la NVRAM (`0x90000e + 0x90000f`, …) como la
  orden 3 de `0x900141`.
- Diagnóstico: cada relleno deja `G22-FECHA reloj del anfitrión para la vista (info N): AAAA-MM-DD HH:MM:SS` (por
  `efp`, visible con `WAITLOG`), y la traza de entrada de función imprime ahora **la biblioteca y el desplazamiento del
  llamante** (`dladdr(lr)`), que es lo que permitió localizar `viewUnified6.so+0x293e2`.

## 6. Verificación

Todas las capturas están en `docs/gui/img/`; los perfiles y los `shim.log` completos, en
`analysis/gui/g22/harness/live/fecha-h8…h11/` (ignorados por git).

### 6.1 Antes (reproducido con el árbol de partida)

Perfil propio `live/fecha-h8`, puerto 8728, `RELOJEMU=0` para medir el «antes» en la misma sesión: la página, abierta con
la receta de §1, muestra **`0 - 0 - 0  0 : 00`** (`img/g22-fecha-hora-antes.png`). El defecto de la fila G22-E
(**`31 - 12 - 2037  23 : 59`**, `img/g22-fecha-hora-2037.png`) se reproduce en cuanto el reloj del anfitrión llega a la
vista con la info 1 mal servida: el widget recibe `r1 = 0x1F0C07F5` (`TRACE 2e2e10 … r1=1f0c07f5 r2=…3b17`) = año
`0x07F5` (2037), mes 12, día 31, hora 23, min 59, es decir **byte a byte** el valor de la NVRAM `0x107004d`.

### 6.2 Después — arranque en frío (perfil nuevo `fecha-h11`, puerto 8731)

`RELOJEMU=1`, `TRACELIB=viewUnified2.so TRACEFN2=2e2e10 TRACEMAX=3`, arranque en frío (sin `estado.zst`). Página abierta
con la receta de §1 mientras el anfitrión marcaba **`2026-11-26T02:15:39-03:00`**:

| Medida | Valor |
|---|---|
| pantalla | **`26 - 11 - 2026  2 : 15`** (`img/g22-fecha-hora-despues.png`) |
| fecha/hora real del anfitrión | `2026-11-26 02:15:39` → diferencia **< 1 min** |
| widget `PAS_BtnDateTime` (traza) | `r1=1a0b07ea` → año `0x07EA` = 2026, mes `0x0B` = 11, día `0x1A` = 26; `r2=…0f02` → hora 2, min `0x0F` = 15 |

```
 97.51 [shim] G22-FECHA reloj del anfitrión para la vista (info 0): 2026-11-26 02:14:57
119.93 [shim] G22-FECHA reloj del anfitrión para la vista (info 0): 2026-11-26 02:15:19
119.93 [shim] G22-FECHA reloj del anfitrión para la vista (info 1): 2026-11-26 00:00:00
119.95 [shim] TRACE 2e2e10 n=1 r0=560e0c18 r1=1a0b07ea r2=56ec0f02 r3=1 lr=56ec13e3 (viewUnified6.so+0x293e2)
```

El `lr` confirma la cadena de §3: la llamada al widget está en `viewUnified6+0x29360` y vuelve a `+0x293e2`. (La corrida
anterior, `fecha-h9`, con `TRACEFN2=29360 TRACEDEREF=d0:12c:6`, dejó los seis campos del objeto de la vista:
`000007ea 0000000b 0000001a 00000000 00000001 0000002d` = 2026-11-26 01:45, y la traza resolvió el llamante con
`dladdr`: `viewUnified2.so+0x198eca`, retorno de `blx r3` en `viewUnified2+0x198ec8`.)

### 6.3 Después — restaurar un estado guardado

`POST /salir` en 8731 (guarda `estado.zst`, 118 MiB) y relanzar el mismo perfil: `/estado` responde
**«restaurado, 25 s · 1 fotogramas»** (no arranque en frío, sin pasar por el arranque de modelos). La vista sigue
abierta con la fecha del guardado (`2 : 15`); al salir y volver a entrar (menú → «Fecha/Hora», que fuerza `reload`) la
página muestra **`26 - 11 - 2026  2 : 18`** (`img/g22-fecha-hora-restaurado.png`, anfitrión a las `02:19:04`):

```
324.64 [shim] G22-FECHA reloj del anfitrión para la vista (info 0): 2026-11-26 02:18:44
324.64 [shim] G22-FECHA reloj del anfitrión para la vista (info 1): 2026-11-26 00:00:00
```

### 6.4 Una iteración descartada, y por qué (medición que cambió el arreglo)

La primera versión entregaba en la info 1 la **primera «T** del anfitrión (el arranque). Con el reloj a las `02:07` y la
inicial a las `01:50:17` la página mostraba **`26 - 11 - 2026  2 : 59`** (`r1` correcto, minuto 59 = el máximo de la
NVRAM): el minuto actual (`7`) quedaba por debajo del minuto de la inicial (`50`) y el recorte de `+0x29558` lo saturaba
al extremo contrario (§4b). Es un fallo del arreglo, no del emulador. La info 1 pasó a ser la **medianoche del día del
anfitrión**, que es campo a campo ≤ que la fecha actual, y la medición de §6.2/§6.3 ya sale con el minuto correcto.

## 7. Límites y lo que NO está verificado

- **NO_VERIFICADO**: el valor exacto que devuelve la cámara real en el parámetro `0x100` de la info 0 y su semántica
  (el código de `ModelClock` `0x4f1376` lo pone a 1 cuando el campo tipo/área de la fecha es 0). Aquí se entrega 1
  porque la vista exige valor no nulo; con 0, medido, la página se queda en `31-12-2037` (los campos no se rellenan).
- **INFERENCIA**: que en la cámara real el recorte de `+0x29558` no llegue a saturar. Su lógica (campo a campo,
  saturando al extremo contrario) haría que un ajuste de hora a las `HH:50` diera minutos `59` hasta la hora siguiente
  si la fecha inicial guardada (`+0x84…`) tuviera ese minuto por encima; aquí se esquiva entregando la medianoche del
  día como fecha inicial. **NO_VERIFICADO** con reloj real: no se ha podido ver qué guarda `+0x84…` la cámara.
- **INFERENCIA**: que la info 1 de `model/CLOCK` en la cámara real es «la fecha con la que se puso en hora» y que la
  vista la usa sólo como extremo de recorte. El shim la entrega como medianoche del día del anfitrión, que es un valor
  *elegido*, no medido del firmware.
- **NO_VERIFICADO**: el significado exacto del registro NVRAM `0x107004d` (aquí: extremo superior del rango del widget,
  coincide con el máximo de la UI). No se escribe: sólo se lee del `bk.tbl` del perfil.
- El eslabón que falta para que el modelo exista de verdad (desbloquear `Mi 00A`) sigue abierto: es trabajo del arranque
  de modelos (G22-B), no de esta tarea.
- Todo es emulación con kernel ajeno: no demuestra comportamiento de la cámara, sólo que el arnés ya no inventa la
  fecha cuando el modelo no está.

## PARA PENDIENTES.md (fila G22-FECHA)

| G22-FECHA | HECHO (26-11-2026) | **Fecha/Hora muestra la fecha y hora del anfitrión (±1 min)**: causa demostrada en tres eslabones — (1) `ModelClock` (`@M018`, id `0x18`) no se instancia porque `Mi 00A` (`ModelSalvage`) no termina y el bucle `Ts`→`Md/Ms` no corre (el registro real sí tiene `Md 018`); (2) `ViewDateSet` (`viewUnified6+0x29260`) lee el extremo superior del rango de la NVRAM `0x107004d` = `2037-12-31 23:59:59` empaquetado y `+0x29558` recorta **campo a campo saturando al extremo contrario** (`v < inicial → v = máximo`); (3) la info 1 se servía con la hora del instante de la consulta, siempre posterior. Arreglo sólo en el shim (`getModelInfo` responde `@M018`/`model/CLOCK` 0/1 sólo si el modelo falla, con las claves y los constructores de `libObj+0x4f1250`: `0x100` = `PrmBool` tipo 5 **y no** `Param<int>`, `0x101…0x106` = `Param<int>`; info 0 = hora del anfitrión por `date_local()`, info 1 = medianoche del día), sin parchear binarios. Evidencia: `docs/gui/img/g22-fecha-hora-{antes,2037,despues,restaurado}.png`, líneas `G22-FECHA …` y `TRACE 2e2e10 … r1=1a0b07ea` del `shim.log` de `live/fecha-h11`, arranque en frío y restauración de estado; pruebas `tests/test_g22_fecha.py` (7) | `ModelClock` nativo (desbloquear `Mi 00A`) sigue pendiente en G22-B; la semántica real de la info 1 no está verificada con cámara | [g22-fecha-hora.md](g22-fecha-hora.md), `scripts/gui/harness/shim/sonyshim.c` |
