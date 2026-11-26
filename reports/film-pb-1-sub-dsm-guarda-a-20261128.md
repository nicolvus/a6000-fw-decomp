# FILM-PB-1 · Guarda A agotada: «Pb Disable!! ref) dsm get», GetInhInfo y el 0x1A

28-11-2026. Todo **estático** sobre `firmware/extracted/fw321/.../dev/nflasha15_unpacked_unpacked/`
(/usr 3.21) y, para el origen de TvSystem, `lib/libmprctrl.so`, `lib/libObj.so`.
Herramientas: `python3 /tmp/elfhelper.py` (Capstone 5) y `.venv/bin/python3` para los barridos.
**VA = VA del ELF** de cada `.so` (en libmpr el primer `PT_LOAD` tiene `p_offset = p_vaddr = 0`,
`p_filesz = 0x9BB1C8`: **offset de fichero == VA** para `.text` y `.rodata`; ver §1).
Evidencia: `reports/evidence/film-pb-1-sub-dsm-20261128/` (índice al final).

## 0. Resumen en cinco líneas

1. **«dsm get» no es nada ejecutable**: no hay proceso, `.so`, socket ni símbolo `dsm` en todo el /usr 3.21
   (ni en las 3.20/2.01 de a7s/a6300). Es una nota del ingeniero en un `log` compartido por 4 entradas de
   reproducción; el «`get`» al que remite es la cadena de getters `GetPlayMovieStatus` → `GetInhInfo`.
2. **La guarda A** (`0x447A1E`) es un *dispatcher de máscara*: con la máscara que deja `PlayMovie` (6)
   hace exactamente **dos** llamadas idénticas, `AviMMgr::GetPlayMovieStatus(CONTENT_MP4=6)`; si alguna
   devuelve **0** ⇒ `0x437C0A movs r3,#0x1a` ⇒ **0x1A** (con el log `" Pb Disable!! ref) dsm get"`).
3. **El 1.er argumento de la guarda no se usa y el 2.º es un PUNTERO**, no un `mmgrId` (corrige el informe
   `film-pb-1-sub-guardaa-20261127.md`): `0x447810` hace `mov r0,r1` y `0x66D0C8` lo desreferencia
   (`[ptr+0x24]->vt[0x18]()` = *self* del `AviMMgr`). Un `mmgrId` entero haría *data abort*.
4. **`GetPlayMovieStatus(6)` tiene tres salidas a 0** y todas nacen de **estado en RAM**, ninguna de la
   tarjeta ni del MP4 en sí: `[AviMMgr+8]->vt[0x154]()==0` (código `0x31000003`, AviMMgr.cpp:9775),
   `GetInhInfo()!=0` (`"MP4 No exist."` / `"It is not loaded."` / fallo de la consulta `mp4Ifo_If`), o
   `playMovieInh = vt[0x1E0](0x28) | (info[+4] & ~0x40000000) != 0`.
5. **TvSystem (NVRAM) no inhibe MP4**: la comparación de TvSystem en `GetInhInfo` (0x67B768) escribe en
   `info[0]`, y `GetPlayMovieStatus(6)` sólo mira `info[+4]`. TvSystem viaja por
   `Backup_read(0x010704FD)` → `MprCtrl::GetTvSystem` → `MprIf::SnapShotBootInit` → global `0xAD28F8+0x28`.

## 1. La cadena, su VA y sus 17 referencias

```
$ grep -a -b -o "Pb Disable[^\"]\{0,60\}" libmpr.so
8758557:Pb Disable!! ref) dsm get
$ grep -rla "Pb Disable" <usr 3.21>      -> lib/libmpr.so   (único fichero)
$ grep -rla "dsm get"    <usr 3.21>      -> lib/libmpr.so   (único fichero)
```

| dato | valor |
|---|---|
| primera `PT_LOAD` de `libmpr.so` | `p_offset=0x0`, `p_vaddr=0x0`, `p_filesz=0x9BB1C8` ⇒ off==VA |
| offset/VA de la cadena | **`0x85A51C`** (`grep` da `8758557 = 0x85A51D`, el `P` tras el espacio) ⇒ `0x85A51C` = `" Pb Disable!! ref) dsm get"` |
| sección | `.rodata` (`0x7A3E90..0x956750`) |
| literales `u32 == 0x85A51C` en `.text` | **17** (16 en *literal pools*) |

Los 4 sitios que **usan** la cadena son los 4 llamadores de `0x447A1E` (barrido `calls 0x447a1e`):

| llamador | función | 3 args |
|---|---|---|
| `0x437BFA` | handler de la orden `0x4000001D` (`PlayMovie`) | `[core+0x1EC]`, `[core+0xDC0]`, `[core+0xDB8]` |
| `0x43570C` | `FeaHighlight::PlayHighlightMovie` (feaHighlightApi.cpp) | `[core+0x9C]`, `[core+0xB0]`, `[core+0xA8]` |
| `0x435AB0` | idem, 2.ª rama | `[core+0x9C]`, `[core+0xB0]`, `[core+0xA8]` |
| `0x43897E` | callback `RegeneLastTimeCode` (etapa 1) | `[core+0x1EC]`, `[core+0xDC0]`, `[core+0xDB8]` |

El resto de literales (`0x43580C`, `0x439AF4`, `0x439C04`, `0x439E7C`, `0x43A038…0x43A6C4`) están en
`FeaCore::PlayStillSingle` / `ReadStillSingle` / `PlayStillMulti` y en pools de las mismas funciones:
misma frase, guardas hermanas (`0x447AEA`, `0x447B10`, `0x447F6E`, `0x447F92`). **NO_VERIFICADO** cuál
usa cada una.

La cadena hermana `" Rec Disable!! ref) pParam->mmgrId is null"` (`0x85BC3E`) confirma el estilo:
`ref)` = «mira lo que devolvió …».

## 2. `FUN_00437BC0` completa (0x437BC0–0x437D38, 0x178 B)

Marco: `sub sp,#8` + `push {r4,r5,r6,r7,r8,sb,lr}` + `sub sp,#0x94`; `r4 = core`, `r7 = sp+0x50`,
`r5 = [r7,#0x7C]` (6.º argumento = puntero a `PlayMovieCtrl`), `r8 = [r7,#0x78]`, `status = [r7,#0x3C] = 0`.

| # | dir | instrucción | condición | destino | qué hace |
|---|---|---|---|---|---|
| 1 | `0x437BDE` | `ldr r3,[r4,#0x1F0]` ; `cmp r3,#5` | `[core+0x1F0] != 5` | `0x437C0C` | `status = 0xA` ⇒ epílogo (log+orden). **No es 0x1A** |
| 2 | `0x437BEC` | `cbz r5` | 6.º arg == NULL | `0x437C0C` | `status = 0xA` |
| 3 | `0x437BFA` | `bl 0x447A1E(r0=[core+0x1EC], r1=[core+0xDC0], r2=[core+0xDB8])` | **ret == 0** | `0x437C00` | log `0x712938(core->log, 0x85A51C, 1)` + `status = 0x1A` ⇒ epílogo |
| | | | ret != 0 | `0x437C10` | sigue |
| 4 | `0x437C2C` | `bl 0x447F26(core+0x1EC, core+0xDC0, {r7+0x60..r7+0x6C})` | **ret == 0** | `0x437C32` | log `" Detect UnSupported Content "` (`0x85A7D8`) + `status = 0x1A`; si `[r5+0x24] != 0` ⇒ `0x447EE2(...)` + log `" ResumeInfo is updated "` (`0x85A7F5`) ⇒ epílogo |
| | | | ret != 0 | `0x437C70` | sigue |
| 5 | `0x437C78` | `bl 0x447DA8(core+0x1EC, core+0xDC0)` | **ret != 0** | `0x437C7E` | `bl 0x7111B0(ret)` = **traductor de código** (conmuta por `code & 0xFF000000 == 0x1C000000`) ⇒ `status` ⇒ epílogo |
| | | | ret == 0 | `0x437C86` | monta el `PlayMovieParam` (copia 0x3C B desde `r8` si `r8!=0`, campos de `r5`) |
| 6 | `0x437CF6` | `bl 0x307F54(...)` | **ret == 0** | `0x437D2C` | **retorno 0 sin notificar la orden** (arranque correcto) |
| | | | ret != 0 | `0x437CFC` | `status = 0x7111B0(ret)`; `bl 0x447DC8(core+0x1EC, core+0xDC0)` ⇒ epílogo |
| — | `0x437D0E` | epílogo | — | — | `0x712960(core->log, "PlayMovie()", status)` — imprime además `", ErrorCode = "` (`0x920D04`) — y `vt[[core]]+0x1C(0x4000001D, &status, 4)` = **notifica el código al peticionario** |

Notas verificadas: `0x437C0A` **no es una llamada**, es `movs r3,#0x1A`; `0x437BF6` carga la máscara de
`[core+0xDB8]`; el modo `[core+0x1F0]` vale 5 para entrar (si no, 0xA). Cadena literal de esta función:
`0x85E965 "PlayMovie()"`.

## 3. Guarda A `0x447A1E` (0x447A1E–0x447AE8) — semántica exacta

```
0x447A24 r4 = r2 (máscara)            0x447A26 r2 = &local
0x447A28 bl 0x447810(r0, r1, &local)  ; NO usa r0: dentro hace 0x447822 mov r0,r1
0x447A2C cmp r0,#0 / bne 0x447ADC      ; error ⇒ 0x447ADC movs r0,#0  => devuelve 0 (inhibe)
```

`0x447810(r0, r1, &out)` = resolvedor:

| dir | código | efecto |
|---|---|---|
| `0x447814` | `*out = 0` | |
| `0x447816..0x447820` | `subs r3,r1,#1; cmn r3,#3; bhi 0x447836` | **r1 == 0 (NULL) ⇒ `0x31000006`** (en la práctica: chequeo de nulo) |
| `0x447822` | `mov r0,r1` | se **descarta el r0** que venía de PlayMovie |
| `0x447824` | `bl 0x66D0C8` | `return r0->[0x24]->vt[0x18]()` |
| `0x447828..0x447834` | `*out = r0`; 0 ⇒ `0x31000006`, ≠0 ⇒ 0 | |

Identidades verificadas: el *factory* `AviMMgrIf::NewFlashAviMMgr` guarda el `AviMMgr` en
`wrapper[+0x24]` (`0x66B55E str.w r6,[sb,#0x24]`), y `vt[0x18]` de la vtable del `AviMMgr`
(`0x8E6E58+0x18 = 0x603BE0`) es `return r0` (*self*). Es decir: **la guarda acaba operando sobre el
`AviMMgr` del slot**, el mismo objeto que crea `AviMMgrIf::New*`.

Tabla de bits de la máscara (verificada instrucción a instrucción):

| bit | llamada sobre el `AviMMgr` | si devuelve 0 |
|---|---|---|
| 0 (`0x001`) | `vt+0x60()` = `GetPlayStillStatus` (`0x603DBD`) | ⇒ 0 |
| 1 (`0x002`) | `vt+0x5C(6)` = **`GetPlayMovieStatus(CONTENT_MP4)`** (`0x60945D`) | ⇒ 0 |
| 2 (`0x004`) | `vt+0x5C(6)` (**la misma**) | ⇒ 0 |
| 3 (`0x008`) | `vt+0x5C(8)` = AVCHD | ⇒ 0 |
| 4 (`0x010`) | `vt+0x5C(0x10)` = PS | ⇒ 0 |
| 5 (`0x020`) | `vt+0x5C(0x20)` = DVD | ⇒ 0 |
| 7 (`0x080`) | `vt+0x5C(0x80)` | ⇒ 0 |
| 8 (`0x100`) | `vt+0x5C(0x100)` | ⇒ 0 |
| 9 (`0x200`) | `vt+0x5C(0x200)` | ⇐ **invertido**: devuelve lo que devuelva la llamada |

`PlayMovie` deja la máscara **6** (`0x437A52 str.w r3,[r0,#0xDB8]`, con `r3 = payload[4]`, y
`0x437A3E ldr r1,[r1]` + `0x437A4E str.w r1,[r0,#0xDC0]` = **payload[0], puntero**). Máscara 6 ⇒ **dos
llamadas idénticas a `GetPlayMovieStatus(6)`**; con que una devuelva 0 ya hay `" Pb Disable!!"` + `0x1A`.

## 4. `AviMMgr::GetPlayMovieStatus` (0x60945C) con ct = 6

Entrada: log incondicional `"GetPlayMovieStatus : contentType[%x]"` (`0x8DEF1D`, nivel `[0x9DF25C]`).
Despacho: 8→`0x6094B2`, 0x10→`0x609792`, **6→`0x609550`**, 0x80/0x200→`0x609776`, 0x100→`0x6097A4`,
resto→`0x609498` (`0x31000001`, AviMMgr.cpp:0x2610) y **return 0**.

Rama 6, instrucción a instrucción:

| dir | condición | salida |
|---|---|---|
| `0x609552` | `[this+8]->vt[0x154]()` | si **== 0** ⇒ log de error `0x64E27C` con `0x31000003`, **AviMMgr.cpp:0x262F** ⇒ `0x60976C` **return 0** (sin línea `playMovieInh`) |
| `0x609660..0x609674` | `memset(buf,0,0x3C)`; `GetInhInfo([this+0x780], buf, [this+0x7B0])` | si **r0 != 0** ⇒ `0x609766` **return 0** |
| `0x60967C` | `r5 = buf[+4] & ~0x40000000` | |
| `0x609684` | `r5 \|= vt[0x1E0](0x28)` | |
| `0x60973E` | `if (r5 == 0)` | `r6 = 1` ⇒ **return 1** |
| `0x609740` | si `r5 != 0` | log `"GetPlayMovieStatus : playMovieInh[%x]"` (`0x8DEF43`, nivel `[0x9DF25A]`) + `0x64F8E6(..., AviMMgr.cpp:0x26E6)` ⇒ **return 0** |

`[this+8]` = el "core"/propietario del `AviMMgr`: `AviMMgr::Init` (`0x60B0C4`) crea logger en `+4` y los
acsr, pero **no** escribe `+8`; `AviMMgrIf` (vtable `0x9067A8`) tampoco (su `+0x144`=`GetMovieMediaInfo`,
`+0x154`=`SetStillRemainCalculateMode`: no encajan con las llamadas sin argumentos de esta ruta). La
**clase concreta de `[this+8]` sigue NO_VERIFICADA**; su comportamiento sí: `vt[0x154]` es un predicado
sin argumentos (≠0 = listo) y `vt[0x1E0](id)` un getter por índice (0x14/0x1E/0x28/0x32/0x3C/0x46 para
still/PS/MP4/0x80/0x100/0x200).

## 5. `MMgrMp4IfoAcsr::GetInhInfo` (0x67B6E0) completa

Entrada `r0 = acsr`, `r1 = handle ([AviMMgr+0x7B0])`, `r2 = buf` (0x3C B ya a cero).

| # | dir | condición | efecto |
|---|---|---|---|
| A | `0x67B6F6` | `[acsr+0x48] == 0` | log **`"GetInhInfo : MP4 No exist."`** (`0x90D28C`); `sb = 0x018000FF` ⇒ salto al final ⇒ **devuelve ≠ 0** |
| B | `0x67B70C` | `[acsr+0xC]->vt[0x154]() == 0` | log **`"GetInhInfo : It is not loaded."`** (`0x90A6DC`) + `0x677BB2(...)` con `0x018000FF` (línea 0x25D) ⇒ **devuelve ≠ 0** |
| C | `0x67B750` | `bl 0x6E9624([acsr+0x48], handle!=0, &tmp)` | si **≠ 0** ⇒ `0x67B854`: **todas las palabras de `buf[0..0x38] = 0x80000000`** y salto al final |
| D | `0x67B768` | `TvSystem = [0xAD28F8+0x28]` (getter `0x1EEFDC`); `vt[0x124]()` (TvSystem del contenido: **inferido**) | **`!=` ⇒ `buf[0] \|= 4`** (`0x67B790`) |
| E | `0x67B75A..0x67B7C2` | `tmp[i] != 0` | `buf[0] = 0x677AC4(tmp[0])`; **`buf[+4] = 0x677AC4(tmp[1])`**; `buf[+8] = …(tmp[2])`, `+0xC`, `+0x10`, `+0x18`… `+0x38` |
| F | `0x67B894` | fin | `0x677B8E(acsr, 0x74, sb, 0x2DF, "mmgrifoacsr/MMgrMp4IfoAcsr.cpp", "GetInhInfo")` ⇒ **return = código** (`0` si todo fue bien) |

`0x6E9624` es un envoltorio de traza de **`mp4Ifo_If.cpp:0x899/0x8B5`**: `vt[[[acsr+0x48]]+0x9C](r1,r2)`
= la consulta real de metadatos MP4.

Conversor `0x677AC4(factores) → máscara de inhibición` (tabla completa, 24 casos):

| bit entrada | salida | bit entrada | salida |
|---|---|---|---|
| 0 | `0x80000000` | 0x10000 | `0x10000000` |
| 1 | `0x00004000` | 0x20000 | `0x01000000` |
| 2 | `0x00400000` | 0x40000 | `0x02000000` |
| 3 | `0x00000004` | 0x80000 | `0x80000000` |
| 4 | `0x00000001` | 0x1000000 | **`0x40000000`** (único que `GetPlayMovieStatus` **ignora**) |
| 5 | `0x00200000` | 0x2000000 | `0x80000000` |
| 6 | `0x80000000` | 0x4000000 | `0x80000000` |
| 7 | `0x00000010` | 0x8000000 | `0x02000000` |
| 8 | `0x00000010` | 0x10000000 | `0x80000000` |
| — | — | bit 31 | `0x80000000` |

⇒ Con factores `0` la máscara es `0` y la guarda pasa; **cualquier** otro factor inhibe (salvo el
`0x40000000` que se enmascara en `0x609680`).

## 6. De dónde sale cada inhibición (la pregunta del enunciado)

| dato que decide | dirección | naturaleza | quién lo escribe |
|---|---|---|---|
| `[core+0xDC0]` (puntero `AviMMgrIf`) | `0x437A4E` | **RAM** (payload de la orden `0x40000017`) | `FeaCore` desde `MprIf::EnterMoviePb`→`FeaIf::EnterMoviePb` |
| `[core+0xDB8]` (máscara = 6) | `0x437A52` | **RAM** (payload) | idem |
| `[AviMMgr+8]->vt[0x154]()` | `0x609552` | **estado de sesión** del core | **NO_VERIFICADO** (clase de `[+8]`) |
| `[acsr+0x48]` (objeto `Mp4Ifo_If`) | `0x67B6F6` | **estado de servicio**: acsr creado pero ifo no adjuntado | ctor/`Load` del acsr (creación en `AviMMgr::Init`, `0x60B8D0 str.w r0,[r4,#0x780]` vía `0x60AC74(this,2)` = `"AviMMgr : create MP4 Acsr instance"`) |
| `[acsr+0xC]->vt[0x154]()` | `0x67B716` | **estado de sesión** («loaded») | ídem |
| consulta `mp4Ifo_If` (`vt+0x9C`) | `0x67B750` | **RAM** (metadatos MP4) | parser MP4; si falla, todo `0x80000000` |
| `vt[0x1E0](0x28)` | `0x609684` | **estado de reproducción por tipo** (RAM) | subsistema de play |
| `buf[+4]` = conv(factores) | `0x67B7A6` | **metadatos del clip** (protección/códec) | consulta `mp4Ifo_If` |
| `TvSystem` comparado | `0x67B768` | **NVRAM** (EEPROM/backup) | `BackupLib::GetEepData(0x010704FD,1B)` → `Backup_read`; `MprCtrl::GetTvSystem` invierte en tabla `{1,0}` (`0x2180C`); `MprIf::SnapShotBootInit` (`0x71CE64`) → global **`0xAD28F8`**; llamador libObj `0x7E6ED6` |
| hardware (tarjeta/decoder) | — | **no aparece** en la ruta de la guarda A: ningún acceso a `/dev/*`, ni `mount`, ni `stat` entre `0x437BC0` y `0x60976C` | — |

## 7. Qué es «dsm get» (respuesta corta: **nada** del firmware)

Barridos hechos (todos reproducibles):

```
grep -rla "dsm get"                              <usr 3.21>  -> lib/libmpr.so
grep -rla "Pb Disable"                           <usr 3.21>  -> lib/libmpr.so
python os.walk + re '(?i)dsm' en los 5.000+ ficheros de /usr -> solo:
   libmpr.so  0x85A51C " Pb Disable!! ref) dsm get"   y  0x863D9C "dsmTrickModeFlag" (campo PES MPEG)
   libnl-route-3.so  rtnl_*_dsmark_*   (token de QoS, ajeno)
   wpa_supplicant    bytes sueltos "dsmcd"
   viewUnified2.so / libInfraStreamingServer.so / fuentes .ltt / string_swedish.uxc  (bytes sueltos)
find <usr> -iname "*dsm*"                        -> 0 resultados
grep -a "(?i)dsm" en av-cam.bin (nflasha3)       -> 3 aciertos, todos "DECAUDSMPL"/"ENCAUDSMPL"
mismo barrido en a6300-fw201 y a7s-fw320         -> solo la misma cadena en su libmpr.so
```

Conclusión: **no existe cliente ni servicio DSM** (ni binario, ni `.so`, ni socket declarado, ni símbolo
`Dsm/dsm`), y tampoco existe en 3.20/2.01. La frase es una anotación de ingeniero; el «`get`» al que
remite es el **getter de estado que acaba de devolver 0** (la dupla `GetPlayMovieStatus`/`GetInhInfo`, y
detrás el bloque de identidad de arranque `0xAD28F8` = modelo + TvSystem que fija `SnapShotBootInit`).
**La expansión del acrónimo es NO_VERIFICADA**; lo verificado es que no hay artefacto DSM y que la única
dependencia «de sistema» de esta ruta es el bloque `0xAD28F8` (y TvSystem, que **no** inhibe MP4).

## 8. Conclusión: condición concreta del 0x1A y qué habría que cumplir

**Condición necesaria y suficiente en código**: `0x447A1E` devuelve **0** ⇒ `0x437C0A` pone `0x1A`.
Con máscara 6 eso es `AviMMgr::GetPlayMovieStatus(6) == 0`, y esto ocurre **exactamente** si:

- **(A0)** `[core+0xDC0]` es NULL o su `+0x24` está vacío (`0x447810` → `0x31000006`), o
- **(A1)** `[AviMMgr+8]->vt[0x154]() == 0` (código `0x31000003`, `AviMMgr.cpp:9775`), o
- **(A2)** `GetInhInfo() != 0`: `[acsr+0x48]==0` (`"MP4 No exist."`), o `[acsr+0xC]->vt[0x154]()==0`
  (`"It is not loaded."`), o fallo de la consulta `mp4Ifo_If` (`vt+0x9C`), o
- **(A3)** `vt[0x1E0](0x28) | (info[+4] & ~0x40000000) != 0` (log `playMovieInh[xxxxxxxx]`).

Para que **no** ocurra hay que cumplir, en este orden: (1) la orden `0x4000017` debe haber dejado
`[core+0xDC0]` = `AviMMgrIf` válido y `[core+0xDB8]=6`; (2) `AviMMgr::Init` debe haber creado el acsr MP4
(`[+0x780]`) —si falló, `"Init : CreateIfoAcsrInstance MMGR_MP4_AC…"` (`0x8E0421`)—; (3) el acsr debe
estar *loaded* y con `[+0x48]` (objeto `Mp4Ifo_If`) adjunto; (4) la consulta `vt+0x9C` debe devolver 0
factores de inhibición; (5) `vt[0x1E0](0x28)` debe dar 0. **Nada de eso depende de la tarjeta, del
contenedor MP4 ni del WBI; es estado del propio proceso MPR.**

**Prioridad para el fallo global observado** (clips propios + miniaturas + «Recuperar BD imag.» no ayuda):
la hipótesis que explica *las tres cosas a la vez* es **(A2)**: si falta el acsr MP4 o no está *loaded*,
(i) la guarda A sale por `GetInhInfo != 0` → `" Pb Disable!! ref) dsm get"`, y (ii) la guarda B
(`isSupportContent`, `0x61A8F0`) sale por su rama `GetPlayThumbnailInfo` (`0x61AA5C`/`0x61AA68`) con el
mismo acsr (`0x677FB0`) → `" Detect UnSupported Content "`, y (iii) la miniatura no se genera.
El camino que la produce está en `AviMMgr::Init` (`0x60B8BA..0x60B8D4`): si `0x60AC74(this,2)` falla, el
log es `"Init : CreateIfoAcsrInstance MMGR_MP4_AC"` + `0x31000006`. **Hipótesis priorizada, NO verificada
en cámara** (no hay acceso a la cámara en esta sesión).

Discriminación con el log (un solo volcado basta):

| secuencia observada | productor |
|---|---|
| `Pb Disable!!` **sin** `GetPlayMovieStatus : contentType[6]` | A0 (resolvedor) |
| `contentType[6]` + `avimmgr/AviMMgr.cpp` … `262F` / código `31000003` | A1 |
| `contentType[6]` + `GetInhInfo : MP4 No exist.` | A2 (acsr sin `Mp4Ifo_If`) |
| `contentType[6]` + `GetInhInfo : It is not loaded.` | A2 (acsr no *loaded*) |
| `contentType[6]` + `playMovieInh[……]` | A3 (máscara; `40000000` es el único bit inocuo) |
| `AviMMgr : create MP4 Acsr instance` **sin** `Init : CreateIfoAcsrInstance` detrás | fallo de creación en `Init` (raíz de A2) |

## 9. Correcciones a lo publicado

1. `[core+0xDC0]` **no es un `mmgrId`**: es el **puntero** al `AviMMgrIf` (payload[0], `0x437A3E`).
   Con un entero la guarda abortaría en `0x66D0C8` (`ldr r0,[r0,#0x24]`).
2. `0x447A1E` **sí** usa la lista completa de bits de la máscara (9 bits, bits 1 y 2 llaman **al mismo**
   `GetPlayMovieStatus(6)`), y el bit 9 (`0x200`) tiene polaridad invertida.
3. La comparación de TvSystem de `GetInhInfo` escribe en **`info[0]`**, no en el `info[+4]` que consulta
   `GetPlayMovieStatus(6)` ⇒ **TvSystem no puede producir el `playMovieInh` de MP4** (sí afecta a las
   ramas de still/PS/AVCHD, cuyo `+4` no revisé aquí: **NO_VERIFICADO**).
4. El «dsm» queda confirmado como **no-componente** (barrido total y comparación con 3.20/2.01).

## 10. Límites (NO_VERIFICADO)

- Clase concreta de `[AviMMgr+8]` (sólo comportamiento: predicado sin argumentos en `+0x154`, getter por
  índice en `+0x1E0`, `+0xF4` en `CreateIfoAcsrInstance`).
- Significado funcional de cada bit de `0x677AC4` (protección, códec, DRM…): la tabla bits→bits es
  verificada, la semántica de cada factor no.
- Que el eslabón `Backup_read(0x010704FD)` lea de `backup.ko`/flash y no de una caché RAM: la llamada es
  a la PLT `Backup_read` (`libmprctrl 0xECB0`), implementación en otra librería (**NO_VERIFICADO**).
- Qué bit de `vt[0x1E0](0x28)` corresponde a qué causa, y el valor real de `0x9DF25A`/`0x9DF25C` en la
  cámara (niveles de log; en fichero valen `0x01`).
- Nada probado en hardware: esta sesión es estática.

---

## Evidencia (`reports/evidence/film-pb-1-sub-dsm-20261128/`)

| fichero | contenido |
|---|---|
| `00-fun-437bc0.dis.txt` | `PlayMovie` completa 0x437BC0–0x437D38 (tabla §2) |
| `01-fun-447a1e.dis.txt`, `02-fun-447810.dis.txt`, `03-fun-66d0c8.dis.txt` | guarda A y resolvedor |
| `04-getplaymoviestatus.dis.txt`, `04b-…-cierre.dis.txt` | `GetPlayMovieStatus` (capstone se corta en el *pool* 0x6096F4: el cierre va aparte) |
| `05…08-avi-vt*.dis.txt` | slots `+0x154/+0x1E0/+0x144/+0x14C` de la vtable `0x8E6E58` |
| `09*,10*,11*,13*,15*` | ctors/factories `AviMMgr`, `AviMMgrIf`, wrapper |
| `12*,12b*` | `GetInhInfo` completa |
| `14*,17*,18*` | `AviMMgr::Init`, creación del acsr MP4, `CreateIfoAcsrInstance` |
| `16-accesos-780-7b0.txt` | accesos validados (capstone) a `+0x780`/`+0x7B0` |
| `19*,21*,22*,24*,25*` | bloque global, `SnapShotBootInit`, arranque de libObj |
| `23-fun-6e9624.dis.txt` | envoltorio `mp4Ifo_If.cpp` |
| `26*`, `28*`, `33*` | TvSystem: PLT, implementación y `GetEepData` → `Backup_read` |
| `29*,31*` | los 4 llamadores de la guarda y sus tres argumentos |
| `30*,30b*`, `37*` | guarda B (`isSupportContent`, `0x447F26`) |
| `34*` | cola del conversor `0x677AC4` |
| `35*`, `36*` | `vt+0x18` = *self*; escritura de `[core+0xDC0]/[0xDB8]` desde el payload |
| `38-otros-usos-cadena.dis.txt` | otros *pools* con la misma cadena |
| `39-log-y-traductor.dis.txt` | `0x7111B0` (traductor de código), `0x712960` (`", ErrorCode = "`), `0x712938` |
