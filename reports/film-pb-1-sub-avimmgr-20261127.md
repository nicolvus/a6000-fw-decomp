# FILM-PB-1 (sub) — `AviMMgr::MovieReadStart` y el paso asíncrono de reproducción

27-11-2026 · `libmpr.so` 3.21 (SHA-256 `9a74a3bb…4c30`) · **todo estático**, cámara no accesible.
**Espacio:** VA del ELF; **REA = ELF + 0x10000**. Evidencia: `reports/evidence/film-pb-1-sub-avimmgr-20261127/`.

## 1. `MovieReadStart` (ELF `0x608698` / REA `0x618698`): 154 bytes, una sola epílogo

| VA | bytes | instrucción | lectura |
|---|---|---|---|
| `0x6086a2`/`0x6086a8` | `4068`/`47f076f9` | `ldr r0,[r0,#4]`+`bl 0x64f998` | `TRACE_BEGIN([this+4], 0xDC, 0x2AE5)` |
| `0x6086b0`/`b4` | `43f0f2fd`/`60b1` | `bl 0x64c298`+`cbz` | `CheckState(this,**0x24**)`; **no cumple → ER_SEQUENCE** |
| `0x6086bc`/`c0`/`c2` | `e1f542fe`/`0128`/`05d0` | `bl 0x3ea344`… | `[*(this+0x7E4)+0x1C]`; **== 1 → ER_SEQUENCE** |
| `0x6086c6`/`ce` | `43f0affd`/`20d0` | `bl 0x64c228`+`beq 0x608712` | `([this+0x144]!=0)`; sigue sólo si `==0` |
| `0x608712`-`728` | `cdf792f6`/`d4f84831 0133 c4f84831`/`cdf791f6` | lock `+0x124`, `[this+0x148] += 1`, unlock | contador de lecturas en curso (`0x1d6440`/`0x1d644e`) |
| `0x60872c` | `f7f7a8fe` | `bl 0x600480` | `UpmCtrl::SetFullPower` (DFS); **retorno descartado** |
| `0x608730` | `d5e7` | `b 0x6086de` | epílogo común con `r5 = 0` |
| `0x6086d4`/`dc` | `1849`/`174d` | `ldr r1,[pc]`/`ldr r5,[pc]` | `0x8decd3` «MovieReadStart : ER_SEQUENCE» / `0x31000007` |
| `0x6086e8`/`706` | — | `bl 0x64fb28`/`bl 0x64e27c` | `TRACE_ERROR(…,0x2B0B)` + macro de error (`"avimmgr/AviMMgr.cpp"`, id `0x2B0C`) |

**Qué abre: nada.** No hay `open`, ni ruta, ni `EntryId`, ni lectura del MP4 ni de `AVF_INFO`; no usa
ningún parámetro de contenido. Su único efecto externo es `0x600480` (gobernador de energía: `0x8dcefe`
«UPM is full power», `0x8dcf2b` «DFS_ng») y ese valor **se ignora** (`r5` sigue 0). El motor real no está aquí.

**Retornos: exactamente dos**, `0` y `0x31000007` (una sola epílogo; `r5` sólo toma ese literal o 0).
Emulado con el `0x7111b0` real (Unicorn): `0x31000007 → 0x0A`, `0x31000002 → 0x1A`, `0x1c00001a → 0x1A`,
`0x88000002 → 0x1A`, `0x30000005 → 0x1A`, `0x1c000003 → 0x08` ⇒ **`MovieReadStart` no puede producir `0x1A`.**

## 2. Precondiciones exactas

`0x64c298(this,mask)` lee bajo lock `[this+0x140]` (estado), `[this+0x148]` (lecturas) y `[this+0x14c]`, y da 1 si el estado casa con **algún** bit de la máscara. `0x24 = 0x04|0x20`: bit `0x04` (`0x64c2d0`) es `estado==4 && [0x148]==0 && [0x14c]==0` y bit `0x20` (`0x64c306`) lo mismo con `[0x148]!=0` ⇒ `0x24` ≡ **`[this+0x140]==4 && [this+0x14c]==0`** (el contador `0x148` es indiferente).

| # | Comprobación | Campo | Pasa si | Si falla |
|---|---|---|---|---|
| P1 | `0x64c298(this,0x24)` @ `0x6086b0` | `[this+0x140]`, `[this+0x14c]` | `0x140==4` **y** `0x14c==0` | `0x31000007` → `0x0A` |
| P2 | `0x3ea344(this+0x7e4)` @ `0x6086bc` | `[*(this+0x7E4)+0x1C]` | `!=1` (init 0, `0x3ea35a`) | idem `0x0A` |
| P3 | `0x64c228(this)` @ `0x6086c6` | `[this+0x144]` error pegajoso | `==0` | idem `0x0A` |
| P4 | `0x447810`→`0x66d0c8` (GetById de `[MprIf+0x1ec]`) | tabla de entidades | entidad hallada | `0x31000006` → `0x08` |

Estados del setter `0x64c5dc(this,id,newState)` (`str.w r3,[r4,#0x140]` en `0x64c60a`): `2` Init/PowerOff,
`4`, `8` Unmount, `0x10`, `0x80`, `0x100`, `0x200` Disconnected, `0x400`, `0x158`; arranque en `2`
(`0x60ab92`, `0x60b592`). `MovieReadEnd` (`0x608e1c`) exige `mask 0x20` y decrementa `0x148`.
*NO_VERIFICADO* el nombre del estado `4` (el volcado `0x64f93a` es numérico).

## 3. El llamador y el paso asíncrono

`0x447da8` = `if (0x447810(…)==0) return (*(*[sp+4]+0xB4))(); else return err;` (`blx r3` en `0x447dbe`).
La vtable `0x8e6e58` (`+0xB4 = 0x608699`) es la **única** palabra con esa referencia (`0x8e6f0c`);
`+0x58=0x61a8f0`, `+0x5c=0x60945c`, `+0x60=0x603dbc`.

`MoviePlayerIf::PbStart` (`0x307f54` → `0x308194` → **`0x3079aa`**): llama `[*[this+0x30]]->[+0x1c]`
(`0x307a38`), **publica el paso `0x102`** (`4ff48171` = `mov.w r1,#0x102`, `0x307a3e`; `d0f76cf9` =
`bl 0x2d7d20`, `0x307a44`) y **devuelve 0 siempre** (`0020`, `0x307a48`), sin mirar `r0`.

Cadena: `0x2d7d20` (BaseCc::Post) → `0x5fdd20` (ring con mutex/cond de `[this+0x18]`) → `0x5fdc84` (kick de `[this+0x14]`) → worker saca con `0x23ff04`→`0x5fdf94` → despacho `0x30908e` (cmdId de `+0xC`, parámetro de `+0x10`) → **`0x3156ec`**, que convierte comando en evento de la máquina de estados (`0x2f99ba` → `0x5bb83c`, `evento|0x1000`):

| cmd | handler | evento | cmd | handler | evento |
|---|---|---|---|---|---|
| `0x100` CmdEnterPbStandby | `0x315890` | `0x421` | `0x180` | `0x3158f6` | `0x443` |
| `0x101` | `0x3158ba` | `0x431` | `0x280` | `0x315986` | `0x5b5` |
| **`0x102` CmdPbStart** | `0x3158cc` | **`0x441`** | **`0x2f0`** | `0x315998` | **`0x885` «READ ERROR»** |
| `0x103` | `0x315948` | `0x461` | `0x300/0x301` | `0x3159be` | `0x581` |
| `0x104` | `0x31592c` | `0x471` | `0x3f0/0x3f2` | `0x3159d2` | `0x8a5`/`0x915` |
| `0x106` | `0x31593c` | `0xa01` | `0x407` | `0x315a2c` | `0x591` |

Errores del lector entran por **`0x2f0`** (`0x3159a6`: `"!!! READ ERROR !!!   ErrorCode: 0x"` `0x80a814`,
más `0x3048d2(8,código)` = `0x2fb628`); el filtro los convierte con su tabla (`"Mp4MovieReader ErrCnv"`
`0x874388`) y viajan **como parámetro de evento**, no como retorno. **Ningún `bl 0x7111b0` cae en
`0x300000-0x32ffff`** (334 sitios en `libmpr`, 0 en el módulo del reproductor) ⇒ el asíncrono **no** pasa
por el traductor y no puede fabricar el `0x1A` que devuelve `PlayMovie`.

Punto ciego: si `0x5fdd20` falla (ring lleno, `r4=1` en `0x5fddb2`), `0x2d7d40` imprime `0x7f65a8` `"[Mpr]### SetCommand Error!! ###"` y `0x2d7d20` devuelve 0, pero **`PbStart` ignora ese 0** ⇒ paso perdido y reproducción que no arranca, sin error hacia arriba.

## 4. Con clip, `AVF_INFO` y fichero correctos: qué estado puede hacer fallar al motor

| # | Condición de estado | Campo / valor esperado | Código final |
|---|---|---|---|
| E1 | AviMMgr no listo (Init=2, Unmount=8, Disconnected=`0x200`…) | `[AviMMgr+0x140] == 4` | `0x0A` |
| E2 | Retención activa | `[AviMMgr+0x14c] == 0` | `0x0A` |
| E3 | Error pegajoso de una reproducción anterior | `[AviMMgr+0x144] == 0` | `0x0A` |
| E4 | Flag del objeto embebido (aborto/ocupado) | `[*(+0x7E4)+0x1C] != 1` (init 0) | `0x0A` |
| E5 | Entidad MMGR no resoluble | `0x447810 == 0` | `0x08` |
| E6 | Modo de MprIf distinto de 5 | `[MprIf+0x1f0] == 5` (`0x437bde`) | `0x0A` literal (`0x437bec`) |
| E7 | Capacidades, guarda A (`0x447a1e`) | `+0x5c`/`+0x60` ≠ 0 por bit de `[MprIf+0xdb8]` | **`0x1A`** (`0x437c0a`) |
| E8 | Contenido soportado, guarda B (`0x447f26`→`0x61a8f0`) | `!= 0` | **`0x1A`** (`0x437c3c`) |
| E9 | Lector: `bEntryId`/`m_mediaType` ilegales (`0x304284`,`0x30428e`) | `MEDIA_SD` y `EntryId` válido | `0x1c000003` → `0x08` |
| E10 | Ring de comandos lleno | `0x5fdd20 == 0` | silencio (paso perdido) |

**Respuesta:** con contenido conforme, el motor sólo falla por **estado interno de AviMMgr** (E1-E4) o por
falta de entidad (E5): todo ello da `0x0A`/`0x08`. Los únicos `0x1A` alcanzables en el manejador son los
dos literales de las guardas (E7/E8); el paso asíncrono no interviene en el valor devuelto.

## 5. Comprobación de un paso
Los objetos son *heap*: **NO_VERIFICADO** su dirección absoluta; se lee el registro en el anclaje.

| Condición | Anclaje (ELF / REA) | Lectura | Esperado |
|---|---|---|---|
| E1-E5 | BP único en `0x447dbe` (`0x457dbe`, el `blx r3`) → `r0`=AviMMgr | `[r0+0x140]`,`[r0+0x14c]`,`[r0+0x144]`,`[r0+0x148]`,`[[r0+0x7e4]+0x1c]` | `4`,`0`,`0`,nº lecturas,`≠1` |
| E6-E8 | BP en `0x437be2` (`0x447be2`) → `r4`=MprIf; golpes en `0x437c0a`/`0x437c3c` | `[r4+0x1f0]`; máscara `[r4+0xdb8]` | `5`; guardas no disparadas |
| E9-E10 | sin depurador, 1 paso: log (`0x9df25a`=`1` de fábrica ⇒ traza activa) | `"MovieReadStart : ER_SEQUENCE"` (`0x6086d4`), `"[Mpr]### SetCommand Error!! ###"` (`0x2d7d40`), `"CmdPbStart "` (`0x3158cc`), `"!!! READ ERROR !!!   ErrorCode: 0x"` (`0x3159a6`) | la que aparezca decide |

## 6. Límites

- *NO_VERIFICADO*: nombre del estado `4`; aceptación del evento `0x441` en la tabla de la máquina de estados (no localizada, sólo el emisor `0x2f99ba`); valores en ejecución de `[MprIf+0x1f0]`, `[MprIf+0xdb8]` y `[AviMMgr+0x140]`; que `[MprIf+0x1ec]` sea `AviMMgr` (se deduce de vtable/cadenas).
- Si el `0x1A` real **no** coincide con E7/E8, este informe es falso: el asíncrono no puede devolverlo, así que habría un tercer productor no visto en `0x437bc0`.
