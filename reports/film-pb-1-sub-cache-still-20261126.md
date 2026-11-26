# FILM-PB-1 — Sub-auditoría: los dos fallos de lectura de foto (`[CACHE]` y `[StillCache]`)

Fecha: 26-11-2026. Estático sobre `libmpr.so` de fw 3.21
(`firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/lib/libmpr.so`, Thumb-2, **VA = offset
de fichero** en el primer LOAD, literales con VA absoluta). Fuente del log: anillo MPR del
20-10-2026, `reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt`, líneas
108-125 (copiadas en `08-anillo-108-125.txt`). Sin cámara y sin flashear; no se ha usado
`mcp_rea` para binarios.

## Resumen (≤20 líneas)

1. `[CACHE]BUFFER SIZE TOO SMALL : 00000000` lo emite **`StreamCache::SetArea`** (`0x7594e0`), no el StillCache.
2. Compara el **tamaño pedido** (`r1`, guardado en `r4`) contra un **mínimo global** `[0xad4f68]` (`0x75955c-0x759564`, `cmp r4,sb` / `bhs`).
3. Ese mínimo se carga al arrancar desde **NVRAM/EEPROM 0x3C0057** en KiB: `GetEepData(0x3c0057) << 10 → [0xad4f68]` (`0x756ed6-0x756ee4`).
4. El `00000000` que se imprime **es el tamaño pedido**, no el mínimo: `mov r1,r4` antes de `0x75a560` (`0x759572`).
5. Ese tamaño sale de un **descriptor de área de memoria (MemInfo)**: `[desc+0x138]=dirección`, `[desc+0x140]=tamaño` (`0x330120-0x330128`, `0x4392d2-0x43945c`). Es decir: **un área no reservada**, no un tamaño de fichero.
6. Código devuelto: **`0xC1000002`** (`0x7595b0`, retorno en `0x7596e8`).
7. `0xC1000010` es **`"STREAMCACHE NOT SET AREA"`** (`0x756c84-0x756c88`): consecuencia directa de que el `SetArea` anterior fallara (el flag `[0xad4f94]` solo se pone a 1 si `SetArea` tuvo éxito, `0x7596cc`).
8. `StillCacheRead::StartRead` (`0x75dc8c`) hace `dfs::seek(handle=[this+0x10], off=[this+0x18], SEEK_SET)` (`0x75dd50-0x75dd56`).
9. `dfs::File::Seek` es el **slot `+0x160` de la vtable `0x9d3f84`** = `0x3b49b8` (`0x9d40e4 → 0x003b49b9`).
10. `0x3b49b8` **no toca el medio**: valida `dev`, que el handle esté en la lista de abiertos (`0x3b49a2 → 0x3ca768`) y que `[handle+0x1c]==2`; si no, devuelve **`0x0E100001`** (`0x3b49c6-0x3b49d0`, `0x3b49e8`).
11. Por eso `0x0E100001` = **handle DFS no abierto / no válido**; el nombre `INT_ERCD_NOT_OPENED` existe en la tabla de nombres de `libmpr` (`0x7c97ad`), pero la correspondencia código→nombre exacta queda **NO_VERIFICADO**.
12. `0x0049CE00` es el **offset dentro del fichero** que se pasa a `seek` (whence 0), ya alineado a la unidad de acceso (`0x75dcbe-0x75dce0`); es múltiplo de 512, no de 4096. No es una LBA del volumen ni una dirección de memoria.
13. `C3000101` lo fabrica **`StartRead`** (`0x75dd6c`) traduciendo *cualquier* error de `dfs::seek`; `0xC3000102` es el equivalente para `dfs::read` (`0x75ddf4`).
14. **El tamaño 0 no es la causa**: ocurre antes (línea 112) y en otro subsistema; el seek falla en la comprobación de estado del handle, sin I/O. Tampoco es consecuencia del seek.
15. La secuencia del anillo encaja con el **primer sondeo de caché con handle sin abrir**: el DCF abre el fichero tras el fallo **si el handle es 0** (`0x386b12`, `0x386b16-0x386b24`) y reintenta (`0x386b8a`); no hay `Err Open ec` ni segundo error, y después se imprimen `pAddr/readSize` de un `ReadCache` que ya devolvió 0 (`0x38746e`, `0x38747e`, `0x387492`).
16. **Conclusión**: el log demuestra un **estado de inicialización incompleto** (área de memoria del reproductor sin reservar + handle DFS aún sin abrir), **no** un daño de la tarjeta ni del volumen; el medio no llegó a leerse en el intento fallido.

## 0. Las dos líneas, en orden

```
112 [CACHE]BUFFER SIZE TOO SMALL : 00000000
113 [CACHE]ERROR(C1000002h)
114 [MprIf] Callback EnterStillPb
115 [MprIf] Callback GetStillAttrInfo
116 [CACHE]ERROR(C1000010h)
117 [StillCache]ERROR:StillCacheRead::StartRead> Failed to dfs::seek offset=0x0049CE00 errcode=0x0E100001
118 [StillCache]ERROR:StillCacheFile::Read> Failed to read errcd=0xC3000101
119 [StillCache]ERROR:StillCache::Read> Failed to Read errcd=C3000101
120 [DCF][MS1]ReadScreenNailImage pAddr = [117AE000]
121 [DCF][MS1]ReadScreenNailImage readSize = [000605EC]
```

El anillo no ha dado la vuelta (empieza por `**** EX-PC Monitor Program ****`), así que estas
líneas son **contiguas**: no falta un `Err Open ec` ni un segundo error entre 119 y 120.

## 1. Quién emite `BUFFER SIZE TOO SMALL` y qué compara

Función **`StreamCache::SetArea`**, VA `0x7594e0` (firma usada por los llamadores:
`r0=addr`, `r1=size`, `r2=saveCache`). Prólogo y traza verbosa:

```
7594e8  mov r6,r2          ; saveCache
7594ea  mov r4,r1          ; size   <-- el valor que se imprimirá
7594ec  mov r5,r0          ; addr
...
7594f4  ldr r0,=0x93e839 "CMD(SET_AREA): Addr "
75950e  mov r1,r4 / 759512 bl 0x75a86c   ; imprime addr
759518  ldr r0,=0x93e858 "h, SaveCache "
759528-759542  0x756bf8(0x20,{1,2,3},{addr,size,save})
75955c  ldr r3,=0xad4f68
75955e  ldr.w sb,[r3]      ; MINIMO configurado
759562  cmp r4,sb
759564  bhs 0x759586       ; size >= min -> OK
75956a  movs r1,#0
75956c  ldr r0,=0x93e866 "BUFFER SIZE TOO SMALL : "
75956e  bl 0x759928        ; prefijo "[CACHE]" + texto
759572  mov r1,r4
759574  movs r2,#1
759576  movs r0,#8
759578  bl 0x75a560        ; imprime r4 en 8 dígitos hex  -> "00000000"
...
7595b0  ldr r6,=0xc1000002
7596e8  mov r0,r6 / return
```

El prefijo `[CACHE]` sale de `0x7598d0` (cadena `0x93ea5c`), y `[CACHE]ERROR(` de `0x7598ec`
(cadena `0x93ea64`, código a 8 dígitos en `0x759902`). Por eso el par 112/113 es **una sola
llamada**: mensaje + código.

**Qué NO es el 0**: no es el mínimo, ni el tamaño del fichero, ni lo que queda por leer. Es el
argumento `size` que el llamador pasó a `SetArea`.

## 2. De dónde sale el mínimo (`[0xad4f68]`)

En la inicialización del stream cache (`0x756e80-0x756f14`):

```
756ed6  ldr r0,=0x003c0057
756ed8  bl  0x756b00        ; [NBL] GetEepData(id)  -> 1 byte
756edc  ldr r3,=0x00ad4f68
756ee2  lsls r0,r0,#0xa     ; KiB -> bytes
756ee4  str r0,[r3]         ; MINIMO
756f0c  ldr r3,=0x00ad4f88
756f12  strb r2,[r3]        ; flag "inicializado" = 1
```

`0x756b00` acaba en `0x2b1468` (`[NBL] GetEepData()`, cadenas en `0x7e5e74`/`0x7e5ea7`), que lee
de la EEPROM/NVRAM vía `Backup_read`. Los otros parámetros del mismo bloque son `0x3C0056`
(`[0xad4f84]`), `0x3C0058` (`[0xad4f70]`) y `0x3C033F` (`[0xad4f78]`). Es decir: el mínimo es
**configuración de fábrica**, no algo que dependa de la tarjeta.

## 3. De dónde sale el tamaño pedido (por qué puede ser 0)

`SetArea` tiene 10 llamadas en `libmpr` (ver `07-llamadores-setarea.txt`). Las dos que encajan
con entrar en reproducción de foto leen el par **dirección/tamaño de un descriptor de memoria
(`MemInfo`)**:

- **`SetUpPlayerInstance`** (función `0x43910c`, cadenas `" SetUpPlayerInstance ..."`,
  `"+ mmgrIdForStill :0x"`): `sb=[r5+0x138]`, `r8=[r5+0x140]` (`0x4392d2-0x4392d6`) y
  `SetArea(sb,r8,1)` en `0x439456-0x43945c`.
- **`ThumbnailRecorder::SetMemoryTable`** (función `0x33009c`): tras resolver
  `" type = MemInfo::MEM_TBL_STILL_REC;"` (`0x330108`), `r0=[r5+0x138]`, `r1=[r5+0x140]`,
  `r2=1`, `SetArea` (`0x330120-0x330128`).

Los otros llamadores usan `[desc+0x108]/[desc+0x110]` (`EnterDubbing` `0x42d38e`,
`SetUpRecorderInstance` `0x43f3d0`/`0x43f472`) o `StreamCache::GetArea()` (`0x442562`,
`0x42d7d2`, `0x42d894`), y el comando de depuración `0x759a6c`.

**Por qué 0**: el descriptor existe pero su campo de tamaño vale 0, es decir, **esa área de
memoria no está reservada** en ese estado (tabla de memoria del reproductor / `MEM_TBL_STILL_REC`
sin asignar). No es un fallo de lectura de la tarjeta.

**NO_VERIFICADO**: qué llamada exacta se ejecutó. La línea que lo diría,
`CMD(SET_AREA): Addr ... h / Size ... h, SaveCache ...`, es de nivel verboso y **no está en el
anillo**; por el contexto (justo antes de `Callback EnterStillPb`) el candidato más probable es
`SetUpPlayerInstance` (`0x439456`). Tampoco está verificado *por qué* el área vale 0; la
coincidencia con `MountCmd : Flash Mount Error` / `DEVICE Unmounted` es una hipótesis, no una
prueba.

## 4. `StillCacheRead::StartRead` (`0x75dc8c`) y `StillCacheFile::Read` (`0x75c760`)

`StartRead(this, a1, off, len, alineación, ..., &validLen, &drift)` guarda:

```
75dcb4  str sb,[r4,#0x10]   ; a1 (handle del dfs en esta ruta)
75dcb8  str r6,[r4,#0x18]   ; off
75dcba  str r5,[r4,#0x14]   ; unidad de alineación
75dcbe  str r8,[r4,#0x20]   ; len
75dcc2  cbz r5, 75dce4
75dcc4  uidivmod(off, alin) ; resto -> [r4+0x24] (drift)
75dcd8  add  r3,sb,r8       ; len + resto
75dce0  str  r0,[r4,#0x18]  ; off -= resto  (OFFSET YA ALINEADO)
```

y luego:

```
75dd3c  ldr r2,[r4,#0x18]   ; off alineado
75dd4e  mov r2,r5           ; r5=0 -> whence = SEEK_SET
75dd50  ldr r0,[r4,#0xc]    ; instancia dfs
75dd52  ldr r1,[r4,#0x10]   ; handle
75dd56  bl  0x3bc7da        ; dfs::seek
75dd5a  cmp r0,#0
75dd5c  beq 75ddd8
75dd5e  ... log "Failed to dfs::seek offset=0x%lx errcode=0x%lx"
75dd6c  ldr r5,=0xc3000101  ; <-- C3000101
```

`StillCacheFile::Read` (`0x75c760`) es la capa de páginas: busca la página (`0x75cf2c`), la
reutiliza o pide una nueva (`0x75d4a8`/`0x75d510`), y solo si no está en caché llama a
`StartRead` (`0x75c90c`). **Antes** de `StartRead` ya ha asegurado memoria:

```
75c8ce  bl 0x75d510
75c8d4  cbnz r0, 75c8e4     ; 0 -> "Fatal error !! Not ensured memory!!!" y C3000004
75c8e4  ... log "Start Read"
75c90c  bl 0x75dc8c
```

En nuestro caso se llegó a `StartRead` y el error fue `C3000101`, luego **la página de memoria
existía** (no hubo `C3000004`): el pool de páginas del StillCache es independiente del área
`SetArea` que llegó a 0. El pool es la tabla de `0xad5bb8` (75 entradas × 0x30 B,
`0x75d214-0x75d25e`), no el flag `[0xad4f94]` del stream cache.

## 5. Qué es `0x0049CE00`

Es el **offset dentro del fichero** que se pasa a `dfs::seek` con `whence = SEEK_SET`
(`0x75dd4e`), ya **alineado a la unidad de acceso** en `0x75dce0`. Evidencia:

- El `seek` termina en `dfs::File::Seek` (`0x3b49b8`), que **solo actualiza la posición del
  fichero** (`strd r8,sb,[r4,#0x28]`, `0x3b49ee`): no hay LBA ni dirección física en la
  operación.
- `0x49CE00 = 4.837.888` es múltiplo de 512 (`0x49CE00/512 = 9449`) pero **no** de 4096
  (`0x49CE00 & 0xFFF = 0xE00`), coherente con una alineación de sector FAT de 512 B.
- El offset llega desde el campo `off` de la petición de `StillCache::Read`
  (`[req+0x10]`, impreso en `0x75b7d6` como `off=[%lx]`), que a su vez viene del 4.º argumento
  del llamador (`0x386938`/`0x386a64`).

**NO_VERIFICADO**: a qué fichero corresponde y si `0x49CE00` cae dentro de su tamaño. El `seek`
se rechazó **antes** de validar el offset contra el fichero, y la línea verbosa
`dir=[%s] file=[%s] off=[%lx] len=[%lx]` (`0x75b7d6`) no está en el anillo. Por eso no se puede
afirmar que el offset estuviera fuera de rango.

## 6. `0x0E100001`: quién lo genera y qué significa

Cadena: `StartRead` → `0x3bc7da` (wrapper con mutex) → `0x3bc700` → **vtable `+0x160`** en
`0x3bc7b6` (`ldr.w r5,[r3,#0x160]`, `blx r5`).

La vtable del objeto de fichero está en **`0x9d3f84`**; `+0x160 = 0x9d40e4` y su contenido es
**`0x003b49b9`** (= `0x3b49b8` con bit Thumb). Función `0x3b49b8`:

```
3b49c6  bl 0x3b49a2        ; dev!=0, handle!=0 y handle en la lista de abiertos (0x3ca768)
3b49ca  cbz r0, 3b49e8
3b49cc  ldr r3,[r4,#0x1c]  ; estado del handle
3b49ce  cmp r3,#2
3b49d0  bne 3b49e8
3b49e8  ldr r0,=0x0e100001 ; <-- NO_ABIERTO / handle inválido
3b49ea  pop
```

`0x3b49a2` devuelve 0 si `dev==0`, si `handle==0`, o si el handle no está en la lista enlazada
de abiertos del dispositivo (`0x3ca768`). Es decir: **`0x0E100001` es un error de estado, no de
E/S**. No se ha leído ni un byte del medio cuando aparece.

El nombre `INT_ERCD_NOT_OPENED` existe en el bloque de cadenas de `libmpr` (`0x7c97ad`), junto a
`INT_ERCD_INVALID_HANDLE`, `INT_ERCD_NOT_MOUNTED`, etc. **NO_VERIFICADO**: el emparejamiento
exacto número→nombre (no hay tabla numérica en estos binarios).

## 7. `0xC3000101`: quién lo genera

Lo **fabrica el StillCache**, no el dfs:

```
75dd5e  log "Failed to dfs::seek ..."
75dd6c  ldr r5,=0xc3000101   ; se devuelve tal cual a StillCacheFile::Read
```

`StillCacheFile::Read` lo propaga (`0x75c92a`, `"Failed to read errcd=0x%lx"`) y
`StillCache::Read` lo vuelve a registrar (`0x75b860-0x75b866`, `"Failed to Read errcd=%lx"`).
La cadena completa la forman pues tres etiquetas distintas, todas en el mismo anillo
(líneas 117, 118 y 119). Para contexto, la misma función usa:

| código | VA del literal | significado |
|---|---|---|
| `0xC3000002` | `0x75de50` | parámetro fuera de rango / readlen > buffer |
| `0xC3000004` | `0x75c9cc` | no se pudo asegurar memoria de página |
| `0xC3000009` | `0x75b8a0` | pool de páginas lleno |
| `0xC300000A` | `0x75de68` | lectura cancelada |
| `0xC3000101` | `0x75de60` | **`dfs::seek` falló** |
| `0xC3000102` | `0x75ddf4` | **`dfs::read` falló / lectura corta** |

Y en el stream cache: `0xC1000002` = "BUFFER SIZE TOO SMALL" (`0x7595b0`) y `0xC1000010` =
**"STREAMCACHE NOT SET AREA"** (`0x756c84-0x756c88`, con cadena literal). El flag que distingue
ambos estados es `[0xad4f94]`, que `SetArea` pone a 1 solo en el camino de éxito (`0x7596cc`).

## 8. ¿El tamaño 0 es causa o consecuencia del seek/read fallido?

**Ni una cosa ni la otra.** Tres argumentos independientes:

1. **Orden**: el `SetArea(0)` y su `C1000002` son las líneas **112-113**; el `seek` fallido es
   la **117**. Lo primero no puede ser consecuencia de lo segundo.
2. **Dependencia**: el `seek` se rechaza en `0x3b49c6-0x3b49d0` por el estado del handle DFS;
   no consulta `[0xad4f94]` ni el área de memoria. Y `StillCacheFile::Read` ya había asegurado
   su página (`0x75d510`, si falla daría `C3000004`) antes de llamar a `StartRead`.
3. **Efecto real del 0**: deja el stream cache sin área (`C1000010`, línea 116) y afecta a las
   APIs de cache que lo consultan, pero no al pool de páginas del StillCache.

Lo que sí comparten es el **momento**: entrar en reproducción de foto antes de que el
subsistema esté listo (área sin registrar y fichero aún sin abrir). Son dos síntomas del mismo
estado de inicialización, no una cadena causal entre ellos.

## 9. Qué demuestra y cómo comprobarlo en cámara sin flashear

**En una frase**: el log demuestra un **estado de inicialización incompleto** (área de memoria
del reproductor sin reservar y handle DFS sin abrir), **no** un daño del almacenamiento: el
`seek` se rechaza antes de tocar el medio, y la secuencia inmediata del anillo (`pAddr`/`readSize`)
indica que la petición se completó después de abrir el fichero.

Comprobaciones propuestas (ninguna requiere flashear; **no ejecutadas aquí**):

1. **Repetir el escenario con dos tarjetas** (una formateada en la cámara y otra distinta) y
   mirar si `BUFFER SIZE TOO SMALL : 00000000` se repite. Si sale con ambas, el 0 no es de la
   tarjeta.
2. **Repetir sin tarjeta** al entrar en reproducción: si el 0 sigue apareciendo, es el área de
   memoria del reproductor (firmware/estado), no el volumen.
3. **Comparar el arranque**: entrar en reproducción nada más encender (antes de grabar) y
   después de grabar; si el 0 solo sale en el primer caso, el área se registra tarde.
4. **Buscar `Err Open ec`** (cadena `0x8254d4`) después del error de StillCache en el mismo
   anillo: si aparece, el `dfs::open` falló (medio); si no aparece, el handle solo estaba sin
   abrir. Es la comprobación más directa y solo necesita volver a volcar el anillo por el mismo
   camino EX-PC usado el 20-10 (VA `0x82DF9300`-`0x82DFC400`), sin escribir nada.
5. **Activar traza verbosa** (nivel 5) si el monitor EX-PC lo permite, para capturar
   `CMD(SET_AREA): Addr ... / Size ...` y `dir=/file=/off=`; con eso se cierran los dos
   NO_VERIFICADO de este informe sin tocar el firmware.

## 10. Límites

- **NO_VERIFICADO**: qué llamada exacta a `SetArea` produjo el 0 (falta la línea verbosa) y por
  qué el descriptor de memoria valía 0.
- **NO_VERIFICADO**: el valor real del mínimo `[0xad4f68]` (depende de la EEPROM de esta unidad;
  no está en los volcados del repo) y el emparejamiento exacto `0x0E100001 = INT_ERCD_NOT_OPENED`.
- **NO_VERIFICADO**: a qué fichero corresponde `0x49CE00` y si estaba dentro de su tamaño (no se
  validó: el seek se rechazó antes).
- La lectura de `pAddr=0x117AE000` / `readSize=0x605EC` como salida de un `ReadCache` correcto
  se apoya en `0x38746e` (`cbz r0`) y en la ausencia de `Err Open ec`; es consistente con el
  anillo, pero no hay traza de nivel 5 que lo cierre al 100 %.

## Evidencia

`reports/evidence/film-pb-1-sub-cache-still-20261126/`

| fichero | contenido |
|---|---|
| `01-setarea-0x7594e0.txt` | desensamblado completo de `SetArea` (comparación, log, `C1000002`) |
| `02-minimo-nvram-0x3c0057.txt` | carga del mínimo desde EEPROM `0x3C0057` |
| `03-startread-0x75dc8c.txt` | `StartRead`: alineación, `dfs::seek`, mapeo a `C3000101` |
| `04-seek-0x3b49b8.txt` | `dfs::File::Seek`: comprobación de estado y `0x0E100001` |
| `05-vtable-slot-0x160.txt` | vtable `0x9d3f84`, slot `+0x160 = 0x003b49b9` |
| `06-codigos-cache.txt` | `C1000010 = STREAMCACHE NOT SET AREA`, `C3000102`, `C3000004` |
| `07-llamadores-setarea.txt` | las 10 llamadas a `SetArea` y el origen `[desc+0x138/0x140]` |
| `08-anillo-108-125.txt` | líneas 108-125 del anillo real |
