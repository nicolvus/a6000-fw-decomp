# FILM-PB-1 · parche C — el sector FBM `0x31` se crea **por la vía de consola** en cada arranque y **persiste**

**Fecha:** 2026-11-26 · **Binario:** `libmpr.so` 3.21 de fábrica (sha256 `9a74a3bb…4c30`) ·
**Salida:** `build/cfw_fbm_sector31_c/libmpr.so` sha256 **`831142ae9a0c1598c179c684200d86d57a1209f4ab0349e357d7e25b016e378e`** ·
**Evidencia:** [`reports/evidence/fbm-sector31-c-20261126/`](evidence/fbm-sector31-c-20261126/README.md) ·
Todo QEMU sobre **copias** de los volcados; la cámara no se ha tocado y no se ha usado `mcp_rea`.

## Resumen (≤20 líneas)

1. **Sí persiste.** Con `build/cfw_fbm_sector31_c/libmpr.so` el primer arranque crea el sector `0x31` y escribe **1 300 B** en `nflasha4`; un **segundo arranque con el `libmpr` de fábrica** (sin parche: `gancho@7126e6=a2 f7 9b f0`, `cueva=00 00…`) lo registra **solo**: `idx 10 = 0x31 / handle 1 / +8=1 / om 6`, `CheckExistSector(0x31)=0x45`, `ReadFirstPackData(0x04,3)` y `(0x21,3) = 0x10100003` y **0 B escritos**.
2. **El parche hace exactamente lo de la consola** (`FBM EWBDFD 4 3 0` + `FBM InitB 6 3`): la imagen resultante es **byte a byte idéntica** a la que dejó la vía de consola: sha256 `6d2ab43a…dca51`, 1 300 B, y la página de control `0x9D400` es **la misma** que `run3/ctrl_page_9d400.bin` (sha256 `56c0b96d…69507`).
3. Cueva de **82 B** en `0x93B000` + gancho de 4 B en `0x7126E6` (**88 B previstos, 81 cambian de valor**); tamaño, cabecera, 5 `PT_*`, 25 secciones y las 132 021 relocaciones, intactas.
4. **Diseño** (ver §1): `FBM::Init` → si `0xA3699C[10].handle != 0` **sale** → si no: `EntryWriteBaseDataFunction(4, stub, 0, 3)` y `(0x21, stub, 0, 3)` (lo que hace `LTC 1`/`EWBDFD`) y **`InitBackupData(6,3)`** (lo que hace `InitB 6 3`) = `WriteBaseData` → `CreateSector32` → `TermSectorData` (página de datos base `0x380000`) → `Sync`.
5. **Firma real de `0x2B1DEC` medida**: `(u32 userID=r0, void *fn=r1, void *arg=r2, u32 mediaID=r3)`; escribe `fn` en `+0x10` y `arg` en `+0x14` de la fila de `0x9D23FC` y devuelve 0. `EWBDFD` pasa `fn=0x2B5185` (literal `0x2B5204`) y `arg` = 3.er argumento.
6. **`fn` SÍ se llama** (no estaba documentado en las notas previas): `0x2B3F7C`, llamada por `WriteBaseData` en `0x2B4130`, hace `blx r3` con `r0 = arg` y trata `r0 != 0` como error. Con el dummy de fábrica `0x2B5185` el arranque **se cae**: `pc=addr=base+0x2B5186` (2.ª instrucción del dummy), `lr=base+0x2B3FCB` (justo tras el `blx r3`), `EXIT=132` y **394 B** escritos (control sin página de datos) — medido en `runX-control-fn-dummy/`.
7. Por eso el parche C registra un **stub propio de 4 B** (`movs r0,#0 ; bx lr`, `0x93B04E`) que no toca memoria ni llama a nada: devuelve 0 = «sin error». Efecto idéntico al `EWBDFD` de consola, sin ejecutar código de test de fábrica.
8. **Riesgo (medido):** cuando el sector **ya existe**, la guarda sale antes de cualquier llamada → **0 escrituras por arranque** (`runC3`: `NF4DIFF bytes_distintos=0`, con el parche cargado).
9. **Riesgo (deducido del código, no forzado en el arnés):** si el FBM aborta, `WriteBaseData` devuelve `0x10800010` y `CreateSector` se niega antes de escribir (`0x9E484C`=0 → **`0x4F`**; `0x9E598C`≠0 → **`0x40`**); la cueva ignora el retorno, no escribe nada y **reintenta una vez por arranque**.
10. No se ha construido `.dat` (lo hará otro) y **no hay prueba en cámara**.

---

## 1. Diseño de la cueva (y por qué cada instrucción)

Gancho `0x7126E6`, que es el `bl 0x2B4820` (`FBM::Init`) de `MprIf::Create` (`0x7126EA` es el `bl` siguiente, **no se toca**). La cueva vive en los **129 B a cero** de `0x93B000..0x93B080` (en `0x93B081` empieza el literal `0x0000186A`, que queda fuera: el parche exige que la zona intermedia siga a cero y no escribe ahí). Desensamblado real (de `auditoria-parche-c.txt`):

```
0093b000  push  {r4, r5, lr}            ; r4/r5 son callee-saved
0093b002  bl    #0x2b4820               ; FBM::Init (efecto original del gancho)
0093b006  mov   r4, pc                  ; }
0093b008  bic   r4, r4, #3              ; } r4 = base+0xA36A64 = &0xA3699C[10]
0093b00c  movw  r1, #0xba5c             ; }   (PC-relativo: libmpr NO se carga en base 0)
0093b010  movt  r1, #0xf                ; }
0093b014  add   r4, r1                  ; }
0093b016  ldr   r0, [r4, #4]            ; GUARDA: handle de idx 10
0093b018  cbnz  r0, #0x93b048           ; si ya existe → 0 llamadas, 0 escrituras
0093b01a  movw  r1, #0xba16             ; }
0093b01e  movt  r1, #0xf                ; } r5 = base+0x93B04E = stub `movs r0,#0; bx lr`
0093b022  sub.w r5, r4, r1              ; }
0093b026  adds  r5, #1                  ; bit0 = Thumb
0093b028  movs  r0, #4                  ; (userID 0x04, mediaID 3) ← misma fila que `LTC 1`
0093b02a  mov   r1, r5                  ; fn
0093b02c  movs  r2, #0                  ; arg 0 (como `EWBDFD 4 3 0`)
0093b02e  movs  r3, #3                  ;
0093b030  bl    #0x2b1dec               ; EntryWriteBaseDataFunction
0093b034  movs  r0, #0x21               ; (userID 0x21, mediaID 3)
0093b036  mov   r1, r5
0093b038  movs  r2, #0
0093b03a  movs  r3, #3
0093b03c  bl    #0x2b1dec               ; EntryWriteBaseDataFunction
0093b040  movs  r0, #6                  ; (OM 6, mediaID 3) ← `InitB 6 3`
0093b042  movs  r1, #3
0093b044  bl    #0x2b43f0               ; BackupMgr::InitBackupData
0093b048  pop   {r4, r5, pc}            ; vuelve a 0x7126EA
0093b04a  nop / nop                     ; relleno
0093b04e  movs  r0, #0                  ; STUB registrado como `fn`
0093b050  bx    lr                      ;
```

La dirección de la tabla va **PC-relativa** (`mov r4,pc` + delta de enlace `0xFBA5C`) porque la biblioteca se carga con base ≠ 0 (medido: `base=0xae364000` en `runC1`, `0xae330000` en `runC2`). Un `movw/movt` con `0xA36A64` sería una VA absoluta y apuntaría a memoria no mapeada; por eso el primer intento se corrigió antes de medir.

### 1.1 Hechos de código en los que se apoya (desensamblado propio, `dis-funciones-c.txt`)

| VA | qué es | lo que importa |
|---|---|---|
| `0x2B1DEC` | `EntryWriteBaseDataFunction` | **firma real** `(userID r0, fn r1, arg r2, mediaID r3)`; recorre las 37 filas de `0x9D23FC` (0x18 B) y en la que casa escribe `+0x10=fn`, `+0x14=arg`; **devuelve 0** |
| `0x2B5198` | handler de consola `EWBDFD` | `r1 = [0x2B5204] = 0x2B5185` (dummy), `r2` = 3.er argumento hex, `r3 = mediaID` |
| `0x2B3000` | `GetSectorHandleFromOperatioModeAndMediaID` | `0x2B301A cbz r2` **salta las filas con `fn == 0`**; si no encuentra fila con (OM,mediaID,fn≠0) → `0x10800010` (es el `0x2B4072` de `WriteBaseData`) |
| `0x2B2F48`, `0x2B2B18` | `…Idx` / `userID→fileType` | **no llaman a `fn`**: sólo resuelven el índice de `0xA3699C` |
| `0x2B3F7C` | llamado en `0x2B4130` | **sí llama a `fn`**: `ldr r3,[r4,#0x10]; cbz r3; ldr r0,[r4,#0x14]; blx r3` (`0x2B3FC6..0x2B3FC8`), `r0!=0` ⇒ error (`0x2B3FD4`) |
| `0x2B43F0` | `BackupMgr::InitBackupData(OM, mediaID)` | mutex → `InvalidateSync 0x11D924` → `WriteBaseData` → `ValidateSync 0x1201E0` → `Sync 0x11EE08` (esto es lo que hace **persistente** el sector) |
| `0x2B4030` | `WriteBaseData(OM, mediaID)` | `0x2B3000` → si handle 0: `CreateSector32 0x2B7080` (`0x2B40C8`) → alta en `0xA3699C` (`0x2B40DA..0x2B40EA`: `+0=sector,+4=handle,+8=1,+0xC=OM`) → `0x2B3F7C` → `ChangeSectorToValid`/`…RelocateComp` → **`TermSectorData 0x2B4164`** |
| `0x2A8750` | `DvdFlashBackupLib::CreateSector` | rechazos: `0x2A8798 [0x9E484C]==0` → **`0x4F`**; `0x2A87AC [0x9E598C]!=0` → **`0x40`** |

## 2. Medidas en el arnés (`NFLASH4=1`, perfil `nf4`, imagen D1 `a5ab15ca…`)

| pasada | `libmpr` | imagen de partida | idx 10 de `0xA3699C` | `CheckExistSector(0x31)` | `ReadFirstPackData(4,3)` / `(0x21,3)` | bytes escritos | imagen resultante |
|---|---|---|---|---|---|---|---|
| **C1** `runC1/` | **parche C** (`gancho=28 f2 8b fc`) | D1 prístina | `0x31 / h2 / 1 / om6` | `0x45` | `0x10100003` / `0x10100003` | **1 300** | `6d2ab43a…dca51` |
| **C2** `runC2/` | **de fábrica** (`gancho=a2 f7 9b f0`, `cueva=00…`) | la de C1 | `0x31 / h1 / 1 / om6` | `0x45` | `0x10100003` / `0x10100003` | **0** | idéntica |
| **C3** `runC3/` | **parche C** | la de C1 | `0x31 / h1 / 1 / om6` | `0x45` | `0x10100003` / `0x10100003` | **0** | idéntica |
| X `runX-control-fn-dummy/` | control negativo: `fn = 0x2B5185` | D1 prístina | — (se cae) | — | — | 394 (sólo control) | — |

`im.elf` sigue vivo en C1/C2/C3 (`alive=208/205/202 threads=121`); en X muere (`EXIT`≠0, `alive= threads=0`).

### 2.1 La imagen de C1 es *la misma* que la de la consola

`imagen-diferencias.txt` (salida de `resumen_imagen.py` sobre la imagen que escribió C1): **1 300 B** distintos en 3 páginas de 1 KiB —

| offset | contenido | sha256 |
|---|---|---|
| `0x09D400..0x09D7FF` | página de control: `seq=706`, `cks=0xAC06D58F`, entradas `0x81 (1/3)`, `0xA0 (1/1)`, **`0x31 (status 0, 5/7)`** | `56c0b96d…69507` = **la de la vía de consola** (`run3/ctrl_page_9d400.bin`) |
| `0x0BD400..0x0BD7FF` | la misma tabla, copia/asignación: `seq=707`, `cks=0xAD06D599` | `5fcfc28d…bc82a` |
| `0x380000..0x3803FF` | **página de datos base** (`80 00 00 00 02 00 06 03 …`, 512 B) | `6a7121c0…5abffaf` |

Y la imagen completa coincide **byte a byte** con la que produjo `FBM EWBDFD 4 3 0` + `FBM InitB 6 3` en la sesión de consola: `6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51` (misma cifra que
`reports/evidence/fbm-sector31-consola-20261126/README.md` §imágenes). Es decir: **el parche no inventa nada nuevo, replica el camino bueno**.

### 2.2 La prueba que importa: persistencia con el `libmpr` de fábrica (`runC2`)

```
[shim] FBMTAB libmpr base=0xae330000 tabla=0xaed6699c gancho@7126e6=a2 f7 9b f0 cueva@93b000=00 00 00 00 00 00 00 00
[shim] FBMTAB t=5s  llena=30 nh=2 lst: 0x31 0xa0
[shim] PROBE   t=25s idx=10 sector=0x0031 handle=0x00000001 valido=1 om=6
[shim] PROBE   CheckExistSector(0x31) -> 0x45  (0x45 = existe)
[shim] PROBE   ReadFirstPackData(userID=0x21,mediaID=3) -> ret=0x10100003
[shim] PROBE   ReadFirstPackData(userID=0x4,mediaID=3)  -> ret=0x10100003
NF4DIFF bytes_distintos=0
```

Los 4 B del gancho (`a2 f7 9b f0`) y los 16 B de la cueva (`00…`) leídos de la biblioteca **cargada** demuestran que ese arranque **no lleva parche**: quien registra `idx 10` es `FBM::Init` leyendo `nflasha4`. `0x10100001` (sector ausente) **ya no aparece**. Antes del arreglo, la misma imagen sin sector daba `CheckExistSector=0x48` y `0x10100001` (`reports/evidence/film-pb-1-sub-fbm-create-20261126/run-r0/`).

## 3. Riesgo

1. **Escrituras por arranque cuando ya existe: 0.** La guarda (`ldr r0,[r4,#4]; cbnz`) sale antes de las tres llamadas y no toca el DFB. Medido en `runC3` con el parche cargado sobre la imagen ya escrita: `NF4DIFF bytes_distintos=0`. En el pre-vuelo Unicorn, con `handle=1` y `handle=3`, la lista de llamadas es sólo `FBM::Init()`.
2. **No hay rotación de página de control.** La v3 rotaba 1 KiB por arranque (`0x9D400`→`0x3D800`) porque creaba siempre; la C sólo escribe la primera vez (1 300 B, `seq` 706/707 fijos medidos).
3. **Si el FBM aborta** (deducido del desensamblado, **no forzado** en el arnés): `CreateSector` se niega **antes de escribir** — `0x9E484C == 0` (FlashLib/FBS sin inicializar) ⇒ `0x4F`; `0x9E598C != 0` (reparación pendiente) ⇒ `0x40`; y `0x4B` (`0x2A8A86`) si el fileType ya está en el FBS sin handle — este último según [fbm-initb §8](fbm-initb-20261130.md), no remedido aquí. En los tres casos `WriteBaseData` devuelve `0x10800010`/código, `InitBackupData` lo propaga, la cueva **ignora `r0`** (no hay bucle ni reintento dentro del arranque) y el sector queda sin crear: **0 B escritos y un intento por arranque**. Consecuencia: en ese estado el arreglo no empeora nada y se reintenta al siguiente arranque.
4. **Estado parcial**: la guarda mira **sólo el handle**. Si `handle != 0` pero `+8 == 0` (p. ej. imagen sin la página de datos `0x380000`, medido en `runF-sin-pagina-datos/`: `+8=0`), el parche **no** repara; no se ha probado qué haría falta (`TermSectorData`) y no se afirma nada.
5. **Efecto colateral en RAM**: el parche escribe `fn`/`arg` en las filas 13 y 14 de `0x9D23FC` (sólo memoria, se pierde al reiniciar) y sólo en el arranque en que crea. Con `fn = stub` cualquier otro consumidor de esa fila obtendría «0 = sin error» sin escribir datos; el único consumidor medido es `0x2B3F7C` dentro de `WriteBaseData`.
6. **No probado en cámara** y **sin `.dat`** (a petición: lo construye otro). El parche es de 3.21; empaquetarlo para 3.95 requiere comprobar que el `libmpr` de base es el mismo (`9a74a3bb…`).

## 4. Ficheros

| fichero | qué es |
|---|---|
| `build/cfw_fbm_sector31_c/libmpr.so` | **libmpr final**: 10 321 204 B (tamaño intacto), sha256 `831142ae9a0c1598c179c684200d86d57a1209f4ab0349e357d7e25b016e378e`; 88 B previstos en 2 rangos (81 cambian de valor) |
| `reports/evidence/fbm-sector31-c-20261126/parche_fbm31_c.py` | constructor + auditoría (sha del original, semántica del `bl`, cabecera/`PT_*`/secciones, relocaciones, `ldr/adr` pc-relativos, punteros a la cueva, diff exacto, desensamblado) |
| `…/auditoria-parche-c.txt` · `…/auditoria-control-fn-dummy.txt` | salidas de las auditorías (final y control negativo) |
| `…/emula_cueva_c.py` · `…/emulacion-cueva-c.txt` | pre-vuelo Unicorn: llamadas y argumentos exactos, guarda estricta, `fn` = stub |
| `…/runC1/` · `…/runC2/` · `…/runC3/` · `…/runX-control-fn-dummy/` | `consola.log` de cada pasada |
| `…/pagina-{9D400,BD400,380000}.bin` · `…/reconstruye_imagen.py` · `…/reconstruccion.txt` | las **3 páginas de 1 KiB** que escribe C1 y la reconstrucción verificada de la imagen completa (`6d2ab43a…`); los 10 MiB no se versionan |
| `…/dis_evidencia.py` · `…/dis-funciones-c.txt` | desensamblados citados en §1.1 |
| `…/resumen_imagen.py` · `…/imagen-diferencias.txt` | diff por páginas, entradas de fileType, comparación con la página de la consola |
| `…/comando.sh` | repetición completa (build + C1 + C2 + C3 + control) |
