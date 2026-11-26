# Barrido de `[X+0x4088]` / `[X+0x408c]` (userID / mediaID del objeto de fichero)

Fichero: `analysis/camera-extract/usr/lib/libmpr.so` (10 321 204 B, fw 3.21).
`.text` = VA `0x00120228`-`0x007A3E84` (0x683C5C B), capstone Thumb-2 **con `skipdata=True`**
y troceado en bloques de 0x1000 para no perder flujo tras los *literal pools*.

| Barrido | Resultado |
|---|---|
| `str`/`ldr` con desplazamiento inmediato `#0x4088` | **0** |
| `str`/`ldr` con desplazamiento inmediato `#0x408c` | **0** |
| `add.w rX, rY, #0x4000` (para llegar por base+0x88/0x8c) | 372, ninguno seguido de `str [...+0x88/0x8c]` |

⇒ No hay **ningún** store directo al par dentro de `libmpr.so`: el `(userID, mediaID)` se lee del
objeto en `0x35E0EC` / `0x35E0F0` (`ldr.w r0,[sl,#0x88]`, `ldr.w r1,[sl,#0x8c]`, con `sl = obj+0x4000`)
y lo rellena la construcción del objeto de medio en runtime. Confirma el `NO_VERIFICADO` de
`reports/film-pb-1-sub-tabla-readers-20261126.md` §4.

## Lo que sí está en el binario: quién *registra* y *libera* el par

`0x2B1E34` (`ClearWriteBaseDataFunction`, sin traza propia) recorre las 37 filas de `0x9D23FC` y,
para la que casa `+0`=userID y `+4`=mediaID, pone a **0** los campos `+0x10` y `+0x14`:

```
002b1e48  movs r0,#0
002b1e4a  str  r0,[r4,#0x10]
002b1e4c  str  r0,[r4,#0x14]
```

Llamantes con la pareja en constantes/campos del cliente (los 7 llamantes: `0x2b514e`,
`0x388a2e`, `0x388a4c`, `0x3abba2`, `0x3af68a`, `0x520250`, `0x5c9a96`):

```
; cliente DCF/foto (traza "Err DCF ClearWriteBaseDataFunction", 0x827870)
00388a2a  movs r0,#0x20            ; userID = 0x20
00388a2c  ldr  r1,[r5,#0x40]       ; mediaID = [cliente+0x40]
00388a2e  bl   0x2b1e34
00388a48  movs r0,#0x22            ; userID = 0x22
00388a4a  movs r1,#8               ; mediaID = 8 (fijo)
00388a4c  bl   0x2b1e34

; cliente MSV/vídeo (traza "Err MSV ClearWriteBaseDataFunction", 0x835898)
003af686  ldr  r0,[r4,#0x3c]       ; userID  = [cliente+0x3c]
003af688  ldr  r1,[r4,#0x40]       ; mediaID = [cliente+0x40]
003af68a  bl   0x2b1e34
```

⇒ el **mediaID es un campo del objeto de cliente** (`+0x40`), común a foto y vídeo, y el userID
distingue el uso: `0x20`/`0x22` para DCF (foto) y `0x23` para MSV (vídeo). El userID `0x10`,
`0x04`, `0x21` no aparecen en ningún `Clear` de este barrido.

## Layout de fila confirmado por el comando de consola `View`

Cadena en `0x007E6AAA` (usada por el volcado de la tabla, función `0x2B2428`):

```
 [User ID] [MediaID]  [  FileType  ] [OperationMode]  [WriteBaseDataFunction]  [Funciton DATA]
```

⇒ los seis campos de la fila de 0x18 B son: `+0` userID · `+4` mediaID · `+8` fileType (=sector)
· `+0xC` OM · `+0x10` función registrada · `+0x14` dato de esa función. Los dos últimos son
estado de runtime (por eso sólo las filas usadas los tienen no-cero en la copia `0x8BB3E3FC`).
