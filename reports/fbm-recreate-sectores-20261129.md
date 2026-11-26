# FBM · cómo se recrean los sectores que faltan en `nflasha4`

**Fecha:** 2026-11-29 · **Evidencia:** `reports/evidence/fbm-recreate-20261129/` · **Binario:** `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21, sha256 `9a74a3bb…`) · **Volcados:** D1 `nand-20261020`, D3 `nand-20261105-total`.

## Resumen (19 líneas)

1. **`0x9D2380` no es geometría**: es una lista de **30 `u32` de fileType** terminada en `0xFFFFFFFF` (`0x9D2380`–`0x9D23F7`, 30 entradas de **4 B**). La usan `FBM::Init` (`0x2B4936`) y nadie más como tabla de sectores.
2. Los **tamaños por fileType** están en `m_fileTypeSizeInfo` `0x9D2794`: **39 registros de 16 B** `{u32 fileType, u32 idCheckFlag, u32 baseLen, u32 maxLen}` (hasta `0x9D2A03`).
3. Un **“sector” FBM/FlashLib = 128 KiB (`0x20000`)**, no 1 KiB: `CreateSector_Body` divide `baseLen/maxLen` entre `[0x9E5588]`, valor efectivo `0x20000` y topa a 7 (`0x2A88D4`–`0x2A8900`). La unidad de 1 KiB (`0x400`) es la **página de control** del FBS (`DFA::FlashWrite` exige `0x400`, `0x2A4D…`).
4. Cabecera real de página de control (381 páginas con `+4=+6=0x4A` en D3; la 382.ª que pasa el checksum (índice 7169, `0x700400`) es una página de ceros del área de datos: cks(0)=0)): `+0x000 u32 0`, `+0x004 u16 0x004A`, `+0x006 u16 0x004A`, `+0x008` tabla de **18 entradas de 8 B**, `+0x3F8 u32 secuencia`, `+0x3FC u32 checksum` (algoritmo `0x2B05B0`, sobre `0x000..0x3FB`). Comprobado byte a byte en D1 y D3.
5. **`0x2B6E40` NO es `CreateSector32`**: es `FlashLib::ForceDeleteSector`; `0x2B6EDC` es `DeleteSector`. `CreateSector32` es **`0x2B7080`** (thunk a `0x11E000`); `CreateSector` es `0x2B708C` (→ `CreateSector_Body` `0x2B6F80`).
6. Crear: `CreateSector` → `CreateSector_Body` → `0x2B1080` (mutex) → **`DvdFlashBackupLib::CreateSector` `0x2A8750`** → selector FBS **`0x2B0E70`** (18 slots de 8 B) → `0x2B089C/0x2B08AE/0x2B08FE` (tabla `+0x98` por fileType).
7. **Nadie crea los 30 fileTypes de golpe.** `FBM::Init` sólo *abre* los existentes; el único camino que crea uno que falta es **`BackupMgr::WriteBaseData` `0x2B3F7C`, llamada `CreateSector32` en `0x2B40C8`**, y sólo cuando el userID/mediaID no tiene handle.
8. Consola FBM real: tabla en **`0x7E7FAC`** (29 entradas × 12 B `{name, handler, help}`): `Destroy`, `Close`, `Delete`, `DeleteAll`, `ReadAllPD`, `ReadPD`, `WritePack`, `InitB`, `ChgSec`, `SetOM`, `SetSMI`, `View`, `ASV`, `GASI`, `WDS`, `Flush`, `SSS`, `GSS`, `ARB`, `Quit`, `GetAlignSize`, `INRFB`, **`CRFB`**, `DFT`, `DRWBI`, **`LTC`**, `EWBDFD`, `CWBDF`, `WBI`. **No hay `CreateSector` ni `Format`.**
9. Consola DFB (otra tabla, **`0x7DFF40`**, 14 × 12 B): `sss`, `apd`, `add`, `ExecEMP`, **`pabe`**, `cisd`, `ciic`, `gcd`, `scdaf`, `sbuc`, `sbs`, `pfs`, `lld`, `sync`. **`pabe` = “partition all block ERASE (DANGER cmd)” → `0x2ABA28`**: cierra handles, `AllDeleteFileType` `0x2A8DF8`, borra los 80 bloques (`0x2A4F38`), `DisableAllFunction`. Es el formateo total del FBS.
10. **`CRFB` (`0x2B58EC`) → `CheckAndRepairFlashBackup` `0x2B89C0`**: si el flag `0x9E598C` está a 1, llama a `0x2B1074` = **`AllDeleteFileType` `0x2A8DF8`** (borra tablas y reconstruye una página vacía). No crea fileTypes.
11. **`IsFlashAllCleared` `0x2B8B7C`** → `0x2B13F2` → `0x2AAE24`: devuelve si el área está toda borrada. No crea nada.
12. **`MprIf::ExecMprUtility(n)` `0x722BCC`** → `0x4500CC` → `0x436408`: es la utilidad de **formateo de la tarjeta**: `n=0 quickFormat`, `1 init`, `2 flush`, `3 fullFormat`, `4 check` (mapeo en `MprIfMcmd` `0x72DD98`, cadenas `0x92CABA`…). **No toca el FBS.**
13. **Página de control**: anillo de **6 bloques × 128 páginas = 768 slots** (bloque = 128 KiB; D1 tiene 706 páginas con seq 0…705 a la vez, imposible con 384). Mapa: **`bloque = seq%6`, `página = seq/6`** (página 0..127). Última de D3: **seq 380, índice 319, offset `0x4FC00`** (bloque 2, página 63). Siguiente slot: **seq 381 → bloque 3, página 63 = `0x6FC00`** (a `0xFF`); después 382→`0x8FC00`, 383→`0xAFC00`, 384→bloque 0/pág 64 = `0x10000`.
14. Entrada de fileType en la página: **8 B** `{u32 fileType LE, u8 status=0, u8 bloquesBase, u8 bloquesMax, u8 0xFF}`. Verificado: `0x62→6/7`, `0x30→5/7`, `0xA0→1/1`, `0xB2→5/7`, `0x81→1/3` = exactamente `ceil(baseLen/0x20000)`/`ceil(maxLen/0x20000)`.
15. **Offset de destino**: no está en `0x9D2380` ni en ningún sitio fijo; lo elige `0x2B0E70` sobre el área de datos (**74 bloques de 128 KiB**; `+4=+6=0x4A` = 74). Para un fileType que falta hoy: **sin offset y 0 bloques**; al crearlo, 5/6/7 bloques de cuota (640/768/896 KiB), no una región contigua reservada.
16. **Un sector todo `0xFF` es válido como “NO_USE”**: `0x2B061E` devuelve “blank” si `*(u32*)buf==0xFFFFFFFF`; `WarmBootInit` lo registra (“[DFB]Blank was discovered…”, `0x7DF3BD`). Pero **no atribuye fileType**: FBM no lo abre.
17. **Sí se puede crear vacío y que la cámara lo rellene**: `CreateSector32` sólo reserva el fileID y los bloques; no escribe datos. La página de control se escribe al crear; los 128 KiB de datos quedan `0xFF` hasta el primer `WritePack` (`0x2B7A50`). Es el arreglo más simple *si se puede disparar `WriteBaseData`*.
18. **Desde la UI: no.** Desde consola DFB (`pabe`): sí pero **borra todo**. Desde shell root/USB: sí, escribiendo **1 KiB** en `0x6FC00` (D3). Por SWD no hay ruta NAND probada.
19. Bytes exactos en §7. La página `ctrl_seq381.bin` generada está en la evidencia y su checksum verifica (`0xF105B82A`).

---

## 1. Correcciones al enunciado (medidas, no interpretadas)

| enunciado | realidad | prueba |
|---|---|---|
| `CreateSector32` en `0x2B6E40`/`0x2B6EDC` | `0x2B6E40` = `FlashLib::ForceDeleteSector` (156 B), `0x2B6EDC` = `FlashLib::DeleteSector` (164 B) | `.dynsym`; `reports/evidence/…/dis/forcedel.txt`, `del.txt` |
| `CreateSector` `0x2B708C` | wrapper de 36 B: `blx 0x11E004` = `CreateSector_Body` | `dis/create.txt` |
| `CreateSector32` | `0x2B7080`, 12 B: `b.w 0x11E000` | `dis/create32.txt` |
| `OpenSector32` | `0x2B6764`, 12 B: `b.w 0x11DCE4` (`FlashLib::OpenSector32`) → `DFB::OpenSector 0x2A81E8` | `dis/opensb.txt` |
| `SetSectorManagerInfo` `0x2B208C` | escribe `0xA3699C[i*0x14] = {sector, handle, r3, stack}`; `i<=0x1D` | `dis/setsm.txt` |
| `FBM::Init` `0x2B4820` | recorre `0x9D2380` hasta `0xFFFFFFFF`; `CheckExistSector` → si `0x45` (`FBS_EXISTED`) `OpenSector32`; si no, deja handle 0 | `dis/init.txt` |
| `0x9D2380` = geometría con 30 entradas | **lista de 30 fileType de 4 B**; la geometría viene del driver por `ioctl 0xC0045321`/`0x80046D0B` en `DFA::Init` (`0x2A532C`, `0x2A5396`) | `filetypes.txt`, volcado de `0x9D2380` |

`0xA3699C` sí es la tabla de 30 × `0x14` que ya conocías: `+0` fileType, `+4` handle, `+8` válido, `+0xC` operationMode (`SetSectorManagerInfo` `0x2B208C`; `FBM::Init` `0x2B48D8`–`0x2B4930`).

## 2. Qué es un “sector” y dónde vive

Geometría del FBS: **bloque = 128 KiB (`0x20000`)**, página = 1 KiB (`0x400`), 80 bloques = 10 MiB. El anillo de control son **6 bloques × 128 páginas = 768 slots** (768 KiB); el área de datos son **74 bloques** (`+4=+6=0x004A` = 74, en todas las páginas de control).

```
nflasha4 (10 MiB = 80 bloques de 128 KiB)
0x00000..0xBFFFF  control: 6 bloques x 128 paginas de 1 KiB (768 slots)
0xC0000..0x9FFFFF datos: 74 bloques de 128 KiB (9.25 MiB)
   D1: datos en bloque 7 (0xE0000) y 74 (0x940000..)
   D3: datos en bloque 7 (0xE0000) y 47,54,55,56
```

Anillo de control, verificado en D1 y D3: `bloque = seq%6`, `pagina = seq/6`, offset `bloque*0x20000 + pagina*0x400`; p. ej. seq 0 → bloque 0/pág 0 (`0x00000`), seq 379 → bloque 1/pág 63 (`0x2FC00`), seq 380 → bloque 2/pág 63 (`0x4FC00`), seq 705 (D1) → bloque 3/pág 117 (`0x7D400`). D3: **381 páginas** de control (seq 0…380); D1: **706** (seq 0…705). Las 381 de D3 pasan el checksum `0x2B05B0`.

### Formato de una página de control (1 KiB)

| offset | tamaño | contenido |
|---|---|---|
| `+0x000` | u32 | estado = `0x00000000` en las 381 páginas de control |
| `+0x004` | u16 | `0x004A` (381/381 páginas de control) |
| `+0x006` | u16 | `0x004A` |
| `+0x008` | 18 × 8 B | tabla de ficheros: `{u32 fileType, u8 status, u8 bloquesBase, u8 bloquesMax, u8 0xFF}` |
| `+0x098` | 152 × 4 B | tabla por fileType `{u16, u8, u8}` (accesores `0x2B08FE`, `0x2B0932`; en D3 toda a `0xFFFF/0/0`) |
| `+0x2F8` | 0x100 B | reservado/generación |
| `+0x3F8` | u32 | secuencia (`seq`) |
| `+0x3FC` | u32 | checksum de `0x000..0x3FB` |

Checksum ( `0x2B05B0`, llamado por `0x2B05DA`; verificado en 382+706 páginas):

```c
uint32_t cks(const uint8_t *p) {
  uint32_t x=0, s=0;
  for (int i=0;i<0x3FC;i++){ x^=p[i]; s += p[i] << (i&3); }
  return (s & 0x00FFFFFF) | (x << 24);
}
```

`0x2B05DA` construye la página: pone `+0x000..3 = 0`, `+0x3F8 = seq`, `+0x3FC = cks`; **no escribe `+4/+6`** (vienen de la página anterior). `0x2B061E` = test de “página en blanco” (`*(u32*)p != 0xFFFFFFFF`).

## 3. Qué hace cada función pedida

- **`FlashLib::CreateSector` `0x2B708C`** (36 B): `CreateSector_Body(fileType, flag, &local, &out_id)`; devuelve `out_id` por `u16*`.
- **`CreateSector_Body` `0x2B6F80`**: comprueba `m_enableFlag` `0xA36C78`; `GetIdCheckFlag` (`0x2B6000`), `GetFileTypeBaseLength` (`0x2B6054`), `GetFileTypeMaxLength` (`0x2B6028`) leyendo `0x9D2794`; llama `0x2B1080(fileType,idCheck,base,max,flag,&id)`; en éxito `GetIDEmm`; apunta la operación en `m_packWriteInfo` `0xA36C88` (entradas de 17 B).
- **`CreateSector32` `0x2B7080`**: idéntico con `fileType` de 32 bits (thunk `0x11E000`).
- **`OpenSector32` `0x2B6764`** → `0x2A81E8` (`DFB::OpenSector`): busca el fileID en la tabla de 48 entradas `0x9E452C` (16 B/entrada, `+0` fileID, `0xFFFFFFFF` = libre); si no está, `0x49` (`FBS_FILE_NOT_FOUND`). `CheckExistFile` `0x2A6690` sólo acepta estados 2/7.
- **`SetSectorManagerInfo` `0x2B208C`**: `index>0x1D → 1`; si no, `0xA3699C[index*0x14] = {r1, r2, r3, [sp+0x18]}`.
- **`FBM::Init` `0x2B4820`**: para cada fileType de `0x9D2380`: `CheckExistSector` (`0x2B8B48` → `0x2A6690`); si existe, `OpenSector32` y, si el `FBS_INFO.us_SectorStatus` (`0x2B2480`) es 3/4, rellena `0xA3699C`; si no, `+4/+8/+0xC = 0`. No crea nada.

## 4. `0x9D2380` y `0x9D2794`: fileTypes, tamaños y offsets

Lista (`0x9D2380`, 30 × u32): `10 11 12 20 21 28 29 2c 2d 30 31 38 39 40 60 61 68 6c 62 63 90 91 92 a0 b1 b2 b3 b8 bc bd` + `0xFFFFFFFF` en `0x9D23F8`.

Tamaños (`0x9D2794`, 39 × 16 B) y bloques de 128 KiB (`ceil(x/0x20000)`):

| fileType | base | max | bloques | nombre `GetIdString` `0x2B7300` (tabla `0x7E95DC`) |
|---|---|---|---|---|
| `0x10` | `0x09D800` | `0x0DC800` | 5/7 | DVD AVCHD |
| `0x11` | `0x09D800` | `0x0DC800` | 5/7 | DVD VF |
| `0x12` | `0x09D800` | `0x0DC800` | 5/7 | DVD +VR |
| `0x20` | `0x09D800` | `0x0DC800` | 5/7 | HDD AVCHD |
| `0x21` | `0x09D800` | `0x0DC800` | 5/7 | HDD M2PS+HDM |
| `0x28` | `0x09D800` | `0x0DC800` | 5/7 | FLH AVCHD |
| `0x29` | `0x09D800` | `0x0DC800` | 5/7 | FLH M2PS+HDM |
| `0x2C` | `0x09D800` | `0x0DC800` | 5/7 | SSD AVCHD |
| `0x2D` | `0x09D800` | `0x0DC800` | 5/7 | SSD M2PS+HDM |
| `0x30` | `0x09D800` | `0x0DC800` | 5/7 | MS1 AVCHD *(existe)* |
| `0x31` | `0x09D800` | `0x0DC800` | 5/7 | MS1 M2PS+HDM |
| `0x38` | `0x09D800` | `0x0DC800` | 5/7 | MS2 AVCHD |
| `0x39` | `0x09D800` | `0x0DC800` | 5/7 | MS2 M2PS+HDM |
| `0x40` | `0x01F800` | `0x0DC800` | 1/7 | VF/tmpVMGI |
| `0x60` | `0x0BD000` | `0x0DC800` | 6/7 | DVD DCF |
| `0x61` | `0x0BD000` | `0x0DC800` | 6/7 | HDD DCF |
| `0x68` | `0x0BD000` | `0x0DC800` | 6/7 | FLASH DCF |
| `0x6C` | `0x0BD000` | `0x0DC800` | 6/7 | SSD DCF |
| `0x62` | `0x0BD000` | `0x0DC800` | 6/7 | MS1 DCF *(existe)* |
| `0x63` | `0x0BD000` | `0x0DC800` | 6/7 | MS2 DCF |
| `0x90` | `0x09D800` | `0x0DC800` | 5/7 | — (no está en `0x7E95DC`) |
| `0x91` | `0x09D800` | `0x0DC800` | 5/7 | — |
| `0x92` | `0x0BD000` | `0x0DC800` | 6/7 | — |
| `0xA0` | `0x01F800` | `0x01F800` | 1/1 | — *(existe)* |
| `0xB1` | `0x09D800` | `0x0DC800` | 5/7 | — |
| `0xB2` | `0x09D800` | `0x0DC800` | 5/7 | — *(existe)* |
| `0xB3` | `0x09D800` | `0x0DC800` | 5/7 | — |
| `0xB8` | `0x09D800` | `0x0DC800` | 5/7 | — |
| `0xBC` | `0x09D800` | `0x0DC800` | 5/7 | — |
| `0xBD` | `0x09D800` | `0x0DC800` | 5/7 | — |

**Offset:** no hay offset fijo por fileType. El asignador `0x2B0E70` busca un slot de la tabla de 18 entradas (`0x2B07D6`), escribe `fileType` en `+0x008+8*slot` (`0x2B07B8`) y los bloques se eligen al escribir, dentro de los 74 bloques de datos (0xC0000..0xFFFFF). Prueba: la página de control sólo guarda fileType y tamaños; ningún campo es un offset. Páginas de datos no-FF en D3: bloque 7 (`0xE0000`, idéntica en D1) y bloques 47/54/55/56; en D1: bloque 7 y bloque 74 (`0x940000`).

**Qué hay hoy en D3** (última página de control, índice 319, offset `0x4FC00`, seq 380): sólo **5 entradas** `0x81 (AVI2, 1/3)`, `0xA0 (1/1)`, `0x62 (MS1 DCF, 6/7)`, `0x30 (MS1 AVCHD, 5/7)`, `0xB2 (5/7)`. Faltan las otras 25, entre ellas `0x90/0x91/0x92` y las de vídeo `0x60/0x61/0x68/0x6C/0x63/0x31/0x38/0x39`.

## 5. Caminos de recreación que existen en el firmware

| camino | dirección | qué hace | ¿crea fileTypes que faltan? |
|---|---|---|---|
| `BackupMgr::WriteBaseData` | `0x2B3F7C`; `CreateSector32` en `0x2B40C8` | si el userID/mediaID no tiene handle, saca su fileType de `0xA3699C[i*0x14]`, `CreateSector32(fileType,0,&handle)`, guarda handle/válido/OM | **sí, uno por userID** (es el camino normal) |
| consola FBM `Destroy` | `0x7E7FAC`; handler `0x2B5EA0` | `Destroy(void)` `0x2B3794`: recorre las 30 entradas y `DeleteSector` de las válidas | no; borra |
| consola FBM `DeleteAll` | handler `0x2B5E20` → `0x2B29CC` | borra todos los sectores | no |
| consola FBM `CRFB` | `0x2B58EC` → `0x2B89C0` → `0x2B1304`/`0x2B1074` | si `0x9E598C==1`, `AllDeleteFileType` `0x2A8DF8` (reset de tablas + página nueva vacía) | no; resetea |
| consola DFB `pabe` | `0x7DFF40`; handler `0x2ABA28` | “partition all block ERASE”: cierra 1..0x30, `AllDeleteFileType`, `0x2A4F38(0,80)` borra los 80 bloques, `DisableAllFunction` | no; **formatea** |
| `CheckAndRepairFlashBackup` | `0x2B89C0` | igual que CRFB | no |
| `ForceDeleteSector` | `0x2B6E40` → `0x2B13BA` | borra el sector marcado para borrado | no |
| `IsFlashAllCleared` | `0x2B8B7C` → `0x2AAE24` | consulta si todo está borrado | no |
| `FlashLib::CreateSector/32` | `0x2B708C`/`0x2B7080` | crea *un* fileType si se le da el fileType | **sí** (pero no está expuesto en consola) |
| `MprIf::ExecMprUtility(n)` | `0x722BCC` | `0 quickFormat`, `1 init`, `2 flush`, `3 fullFormat`, `4 check` sobre la tarjeta | **no** (es la utilidad de formato de medio) |

**No existe** un comando de consola “CreateSector”. El `LTC` (`0x2B57F0`) despacha 12 tests locales del FBM (`0x2B5598`…`0x2B5214`) que tampoco crean fileTypes. El test DFB `0x2AF35A` (tabla de strings `0x7E33D9`: “FlashLib::CreateSector(FBS_UDF,FBS_REMOVAL,…)”) sí llama a `CreateSector(0x50,…)` en el test 2 (`0x2AF198`), pero es un test de depuración, no una ruta de usuario.

## 6. Conclusión: ¿UI, consola o SWD/USB?

- **UI:** no. Ninguna pantalla expone `CreateSector`; “Recuperar BD imág.” es `CRFB`/`Destroy`, que **borra o resetea**, no crea los fileTypes que faltan. (Además ya probaste que no cambiaba el síntoma.)
- **Consola DFB/FBM:** `pabe` sí formatea y deja el FBS coherente, pero **borra todo**; después `WriteBaseData` vuelve a crear los fileTypes que la cámara vaya necesitando (fotos, AVCHD, etc.). Es la vía “limpia” sin escribir a mano, si tienes acceso a esa consola de depuración.
- **Shell root / USB:** se puede escribir **una página de control de 1 KiB** en el siguiente slot del anillo. Es la vía mínima y no borra nada.
- **SWD:** no hay ruta NAND probada en este repo (sólo RAM y arranque del actualizador, R47–R49). No lo recomiendo.

## 7. Bytes exactos (para D3; `nand-20261105-total`)

Última página válida: **índice 319, offset `0x4FC00`, seq 380**. Siguiente slot del anillo: **seq 381 → bloque 3, página 63 → índice 447, offset `0x6FC00`** (comprobado: esos 1024 B están a `0xFF`; también lo están `0x8FC00` y `0xAFC00`).

### 7.1 Las tres primeras zonas de la página (1 KiB)

```
+0x000  00 00 00 00            ; estado
+0x004  4a 00 4a 00            ; constante de las 381 páginas de control
+0x008  <18 entradas de 8 B>    ; tabla de ficheros
+0x3F8  <seq u32 LE>            ; 381 = 7d 01 00 00
+0x3FC  <checksum u32 LE>       ; cks(0x000..0x3FB)
```

Entrada de un fileType que falta (8 B):

```
+0  u32 fileType LE
+4  00                 ; status (0 en 0xA0/0x62/0x30/0xB2)
+5  <bloquesBase>       ; 5 o 6
+6  <bloquesMax>        ; 7 (0xA0: 1)
+7  FF                 ; padding
```

Bytes por fileType (calculados de `0x9D2794`, verificados contra las 4 entradas existentes):

| fileType | 8 bytes |
|---|---|
| `0x90` | `90 00 00 00 00 05 07 FF` |
| `0x91` | `91 00 00 00 00 05 07 FF` |
| `0x92` | `92 00 00 00 00 06 07 FF` |
| `0x60` | `60 00 00 00 00 06 07 FF` |
| `0x61` | `61 00 00 00 00 06 07 FF` |
| `0x68` | `68 00 00 00 00 06 07 FF` |
| `0x6C` | `6c 00 00 00 00 06 07 FF` |
| `0x63` | `63 00 00 00 00 06 07 FF` |
| `0x31` | `31 00 00 00 00 05 07 FF` |
| `0x38` | `38 00 00 00 00 05 07 FF` |
| `0x39` | `39 00 00 00 00 05 07 FF` |

La página completa generada (`make_ctrl.py`) está en `reports/evidence/fbm-recreate-20261129/ctrl_seq381.bin`; cabecera y cola:

```
000  00 00 00 00 4a 00 4a 00 81 00 00 00 01 01 03 ff
010  a0 00 00 00 00 01 01 ff 62 00 00 00 00 06 07 ff
020  30 00 00 00 00 05 07 ff b2 00 00 00 00 05 07 ff
030  90 00 00 00 00 05 07 ff 91 00 00 00 00 05 07 ff
040  92 00 00 00 00 06 07 ff 60 00 00 00 00 06 07 ff
…
3F8  7d 01 00 00   ; seq 381
3FC  2a b8 05 f1   ; cks = 0xF105B82A
```

### 7.2 ¿Y los 128 KiB del sector?

No llevan cabecera FBS: el FBS sólo indexa el fileType en la página de control; los bloques de datos se escriben en crudo (en D3, los bloques 47/54/55/56 no tienen `0x4A004A` ni checksum). Por eso **un bloque de datos a `0xFF` es válido**: `0x2B061E` lo considera “blank” y `WarmUp` lo salta. Lo que **no** es válido es una página de control a `0xFF` para un fileType que quieres que FBM abra: sin entrada en `+0x008`, `OpenSector32` devuelve `0x49`.

## 8. ¿Se puede crear vacío y que la cámara lo rellene?

**Sí.** `CreateSector32` sólo reserva el fileID (`0x2A8750`) y los bloques (`0x2B0E70`); no escribe datos. La página de control se escribe al crear (o al primer flush), y los 128 KiB quedan a `0xFF` hasta el primer `WritePack` (`0x2B7A50`). Es exactamente lo que hace `WriteBaseData` (`0x2B40C8`) cuando falta el handle. Si consigues disparar `WriteBaseData` para el userID de vídeo, el sector se crea vacío y la cámara lo llena sola: **es el arreglo más simple**.

El problema es *disparar* ese camino sin grabar: la UI ni `CRFB` lo hacen para los userID de vídeo. La alternativa mínima es la página de control de §7.

## 9. Riesgos y límites

1. **No probado en cámara.** Todo es estático + volcados; no se ha escrito nada.
2. El driver `cnflasha4` puede remapear bloques malos: el offset `0x6FC00` es lógico, no físico.
3. El checksum es el del FBS (`0x2B05B0`), pero no he verificado que `WarmBootInit` lo *valide* en la página de control; sí está en las 381 páginas de control y `0x2B05DA` lo escribe.
4. La tabla de ficheros tiene **18 slots**; sólo caben 13 fileTypes nuevos. No se pueden meter los 25 que faltan a la vez.
5. `0x81` tiene status 1 en la última página (no 0); las 4 buenas tienen 0. Para los nuevos uso 0.
6. Si el FBS tiene el flag `0x9E598C=1` (repair needed), `CRFB`/`pabe` borrarán la página nueva.

## Evidencia

- `reports/evidence/fbm-recreate-20261129/README.md` (índice y reproducción).
- `dis/*.txt`: desensamblados anotados de `0x2B4820`, `0x2B208C`, `0x2B6F80`, `0x2B7080`, `0x2B708C`, `0x2B6E40`, `0x2B6EDC`, `0x2B6688`, `0x2B89C0`, `0x2B8B7C`, `0x2B8B48`, `0x2A8750`, `0x2A81E8`, `0x2A9AD8`, `0x2A6880`, `0x2B3F7C`, `0x2ABA28`.
- `filetypes.txt`, `idnames.txt`, `ctrl-pages.txt`, `verify-entries.txt`: tablas y comprobaciones.
- `make_ctrl.py`, `ctrl_seq381.bin`, `callgraph.py`: reproducción y página parcheada.
