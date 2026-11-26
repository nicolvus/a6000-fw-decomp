# FILM-PB-1 · Guarda A (capacidades): `GetPlayMovieStatus` + «dsm get»

27-11-2026. **VA = VA del ELF** (`libmpr.so` 3.21 `9a74a3bb…4c30`, `libObj.so` 3.21). En libmpr
**REA = ELF + 0x10000** (`0x60945C`→REA `0x61945C`; `0x437C0A`→REA `0x447C0A`); en libObj directas.
Capstone 5 local sobre `…/dev/nflasha15_unpacked_unpacked/lib/`. Cámara no accesible: todo estático.
Evidencia: [getplaymoviestatus.dis](evidence/film-pb-1-sub-guardaa-20261127/guardaa-getplaymoviestatus.dis.txt),
[cadena-mascara.dis](evidence/film-pb-1-sub-guardaa-20261127/guardaa-cadena-mascara.dis.txt).
## 1. La guarda A, entera (`FUN_00447A1E`, 0x447A1E–0x447AE8, 0xCA B)
Cuatro llamadores: `0x437BFA` (PlayMovie), `0x43570C` (`FeaHighlight::PlayHighlightMovie`), `0x435AB0`,
`0x43897E` (cb RegeneLastTimeCode). Los cuatro con el mismo triplete y **el mismo log**
`" Pb Disable!! ref) dsm get"` (`0x85A51C`) + `0x1A` (`0x437C0A`, `0x43571E`, `0x435AB8`, `0x43898E`).
En PlayMovie: `r0=[core+0x1EC]` (**no se usa**), `r1=[core+0xDC0]` (referencia), `r2=[core+0xDB8]` (máscara).
`0x447A28 bl 0x447810(r1,&obj)`; si falla → `0x447ADC movs r0,#0` ⇒ **devuelve 0 sin consultar nada**.
Si resuelve, por bit de `r2`:

| bit | 0 | 1 | 2 | 3 | 4 | 5 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| llama | `vt+0x60()` | `vt+0x5C(6)` | `vt+0x5C(6)` | `+0x5C(8)` | `+0x5C(0x10)` | `+0x5C(0x20)` | `+0x5C(0x80)` | `+0x5C(0x100)` | `+0x5C(0x200)` |
| ret 0 ⇒ | `0x447AE2` (0) | idem | idem | idem | idem | idem | idem | idem | idem |
Bit 6 (`0x40`) no se prueba; máscara 0 ⇒ devuelve 1 (pasa). **Valor exacto del `0x1A`: la guarda
devuelve 0** (`0x437BFE cbnz r0` → `0x437C00` log → `0x437C0A movs r3,#0x1a`). `GetPlayMovieStatus`
sólo puede devolver **0 o 1** (`0x60976C mov r0,r6`, `r6`∈{0,1}).
## 2. `GetPlayMovieStatus` (0x60945C–0x6097B4, 0x358 B)
`AviMMgr::GetPlayMovieStatus(MPR::ContentType ct)` = slot **`vt+0x5C`** de la vtable **0x8E6E58**
(+0x58 `0x61A8F1` isSupportContent, **+0x5C `0x60945D`**, +0x60 `0x603DBD` GetPlayStillStatus,
+0xB4 `0x608699` MovieReadStart). Entrada: log incondicional `"GetPlayMovieStatus : contentType[%x]"`
(`0x8DEF1D`, nivel = byte **`0x9DF25C`=0x01** de `.data`). Despacho `0x609474`: 8→`0x6094B2`,
0x10→`0x609792`, 6→`0x609550`, 0x80 y 0x200→`0x609776` (luego `0x609580`/`0x6095B2`), 0x100→`0x6097A4`,
**resto→`0x609498` error `0x31000001` y `return 0`**. Consulta al subobjeto **`[this+8]`**
(`vt+0x144/0x14C/0x154/0x158/0x15C/0x160/0x164/0x174/0x178/0x184/0x188/0x18C` y `vt+0x1E0(id)` = estado
por tipo) y a cinco accesores por tipo en `[this+0x778…0x790]`, con el handle en `[this+0x7B0]`:

| ct | gate previo (0 ⇒ `return 0`) | `vt+0x1E0` | accesor | campo |
|---|---|---|---|---|
| **6** | `vt+0x154()` (línea 0x262F) | `(0x28)` | **`[+0x780]` = `MMgrMp4IfoAcsr::GetInhInfo` `0x67B6E0`** | `+4` |
| 8 | `vt+0x144()` y (`0x164`≠0 ó `0x174`=0) (0x261A) | `0x14` | `[+0x778]` `0x670CEC` | `+4` |
| 0x10 | `vt+0x14C()` y (`0x164`≠0 ó `0x178`=0) (0x2621) | `0x1E` | `[+0x77C]` `0x679B30` | `+4` |
| 0x80 | `vt+0x158()` y (`0x164`≠0 ó `vt+0x184(0x84)`=0) (0x2636) | `0x32` | `[+0x788]` `0x675FC8` | `+4` |
| 0x100 | `vt+0x15C()` (0x2628) | `0x3C` | `[+0x78C]` `0x67E728` | `+4` |
| 0x200 | como 0x80 | `0x46` | `[+0x790]` `0x67D210` | `+4` |
Cierre común `0x60973C`: `r5 = vt[0x1E0](id) | (info[+4] & 0x3FFFFFFF)`; `0x60973E cbz r5` ⇒ **devuelve
1**; si `r5≠0` imprime `"GetPlayMovieStatus : playMovieInh[%x]"` (`0x8DEF43`, nivel **`0x9DF25A`=0x01**)
+ AviMMgr.cpp `0x26E6` y **devuelve 0**. Los gates previos salen por `0x64E27C` con
`"avimmgr/AviMMgr.cpp"` y línea `0x2610/0x261A/0x2621/0x2628/0x262F/0x2636`. **Ninguna ruta abre
fichero ni `/dev/nflasha*`**: los cinco accesores no tienen ni una llamada a la PLT (sólo internas
`0x677AC4/0x677B8E/0x677BB2`, `0x1EEFDC`); aquí sólo hay logs, `memset` (`0x1202E2`) y accesores.
**MP4/AVC (ct=6)** = tres gates: `vt+0x154()`≠0 · `GetInhInfo()=0` · (`vt[0x1E0](0x28)` |
`info[+4]&0x3FFFFFFF`) = 0. Los dos últimos son **palabras de inhibición**.
## 3. Origen del dato: mensaje en RAM, **no** tabla de firmware
`[core+0xDC0]`/`[core+0xDB8]` se escriben **sólo** desde payloads de mensaje: `0x437A4E/0x437A52`
(handler de `0x40000017`), `0x438184/188`, `0x4381E8/1EC`, `0x438C94/98`, `0x438F92/96`, `0x438DE4`
(sólo máscara), y se ponen a 0 en `0x437AFA`, `0x437B06`, `0x437B68`. Barrido completo de libmpr:
**8 `str` a `+0xDB8`, todos en `0x437A52–0x438F96`**; ninguno lee memoria no volátil. Cadena:
1. `libObj 0x8627FC` (mensaje MWF, param `0x10001009`) → `0x859D24`, tabla de 6 casos:
   `1→1 CONTENT_STILL`, `2→8 CONTENT_AVCHD`, `4→0x10 PS`, `8→0x20 CONTENT_DVD_MOVIE`,
   **`0x20→6 "CONTENT_MP4(AVC)"`**, `0x40→0x40 CONTENT_BGM`, resto→`0 CONTENT_UNKNOWN`.
2. `MprIf::EnterMoviePb` `0x7231B0` (r2 = ContentType) → `FeaIf::EnterMoviePb` `0x44F2F4`: payload 0x18 B
   en `r7+4`, `[0]=mmgrId`, **`[+4]=contentTypes`**, `[+8]=byte VMuteColor≠0`.
3. `0x4296D0` encola opcode **`0x40000017`**; FeaCore `0x429D26 beq 0x42A2F2` → `0x437A28` guarda
   `[core+0xDC0]=mmgrId`, `[core+0xDB8]=6`. `PlayMovie` (`0x4000001D`, handler `0x437BC0`) usa esa máscara.
**Particiones**: `nflasha2` **no existe** en el DAT 3.21 (extraídas 3/5/7/15/16); `nflasha3` =
`vmlinux.bin`+`initrd.img`+`av-cam.bin`+`lensbin_lensproperty` (`grep CONTENT_MP4|CONTENT_AVCHD` = 0);
`nflasha15` = rootfs (las libs). **«dsm» no es un servicio**: en libmpr sólo hay
`" Pb Disable!! ref) dsm get"` y `"dsmTrickModeFlag"` (`0x863D9C`), que es el campo PES
`dsm_trick_mode_flag` de MPEG (vecino de `esRateFlag`, `pesExtensionFlag`); **cero símbolos `Dsm/dsm`**.
El «dsm get» es un comentario del ingeniero = «lo que dijo el getter de estado».
## 4. Veredicto
- **Sí puede fallar con firmware y tarjeta correctos.** El dato es estado en **RAM** del reproductor
  (`vt+0x154`, `vt[0x1E0](0x28)`, `info[+4]` de `MMgrMp4IfoAcsr`); la guarda no mira tarjeta, MP4 ni BD.
  Falla si el accesor MP4 no está cargado o si hay bits de inhibición (`playMovieInh`≠0).
- **Arranque en frío: no** por sí mismo (ni `0x447A1E` ni `0x60945C` leen `nflasha5`, WBI ni modo de boot;
  coincide con [wbi](film-pb-1-sub-wbi-20261127.md)). Sólo *indirecto* si dejó el accesor MP4 sin cargar
  (`GetInhInfo : MP4 No exist.`).
- **Modelo: no.** La máscara para MP4 es la constante de código `6` (`0x859D24`), sin condicionales.
- **Región: sólo indirecta.** `GetInhInfo` → `0x1EEFDC` = `[0xAD28F8]+0x28` (TvSystem) puede fijar bits de
  inhibición; constante para una cámara dada. **NO_VERIFICADO** que el bit venga de ahí.
- El `r0=[core+0x1EC]` que pasa la guarda **no se lee** en `0x447810` (`0x447822 mov r0,r1`): resuelve
  sólo con `[core+0xDC0]` → `0x66D0C8` (`[ref+0x24]`, `vt+0x18`) → AviMMgr.
## 5. Comprobación en un paso (cámara, sin depurador)
Volcar el búfer de `0x83400000` (o `/proc/klog`) tras intentar reproducir y buscar **en orden**:

| Observado | Significa |
|---|---|
| `GetPlayMovieStatus : contentType[6]` | la guarda A llegó a consultar ct=6 (MP4/AVC) |
| + `GetPlayMovieStatus : playMovieInh[XXXXXXXX]` | **inhibición**: `XXXXXXXX` = máscara (`&0x40000000` ignorado) + AviMMgr.cpp:9958 |
| + `avimmgr/AviMMgr.cpp` línea **9775** (`0x262F`) | `vt+0x154()`=0: reproductor de vídeo no listo/cargado |
| + `GetInhInfo : MP4 No exist.` / `It is not loaded.` | accesor MP4 sin objeto / sin cargar |
| ` Pb Disable!! ref) dsm get` **sin** `contentType[6]` | falló el resolvedor `0x447810` (`[core+0xDC0]`=0 o su `vt+0x18`=NULL) ⇒ 0 sin preguntar |
| sin las dos, pero con `PlayMovie(), ErrorCode = 0x1a` | la guarda A **no** es el productor |
Lectura estática de apoyo: `0x9DF25C` (REA `0x9EF25C`) debe valer **0x01** (habilita `contentType[]`); si
valiera 0 la prueba no discrimina. **No hay VA estática para la máscara**: `[core+0xDB8]` es heap; la única
lectura fija relacionada es `[[0xAD28F8]+0x28]` (REA `0xAE2920`), TvSystem.
## 6. Límites (NO_VERIFICADO)
- **NO_VERIFICADO** el nombre de clase del subobjeto `[AviMMgr+8]` (vtable no localizada; su
  comportamiento sí está verificado a nivel de slot), y que el búfer de log recoja los emisores
  `0x65062C/0x64F8E6` (mismo ostream que `0x712938`, sink no traído) ni que `0x9DF25C`=1 no se reescriba.
- **NO_VERIFICADO** el valor en ejecución de `info[+4]`/`vt[0x1E0](0x28)` ni qué bit corresponde a cada
  causa (protección de escritura, medio ocupado…); la asignación `[+0x780]`↔MP4 sí está verificada por
  `"mmgrifoacsr/MMgrMp4IfoAcsr.cpp"` en `0x67B6E0`.
