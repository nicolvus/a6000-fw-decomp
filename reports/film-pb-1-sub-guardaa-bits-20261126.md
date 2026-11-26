# FILM-PB-1 · Guarda A, 2ª parte: los bits de `MMgrMp4IfoAcsr::GetInhInfo`

27-11-2026. **VA = VA del ELF** (`libmpr.so` 3.21 `9a74a3bb…4c30`; en libmpr **REA = ELF + 0x10000**).
Desensamblado local con Capstone 5 desde `…/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`. Estático.
Evidencia: [guardaa-bits-getinhinfo.dis.txt](evidence/film-pb-1-sub-guardaa-bits-20261126/guardaa-bits-getinhinfo.dis.txt).

## 1. Contrato de la función (0x67B6E0, `mmgrifoacsr/MMgrMp4IfoAcsr.cpp`)

`u32 GetInhInfo(InhInfo* out, u32 h)` — `out` = 15 palabras (0x3C B, `memset` en `0x67B6F2`→`0x67B3D8`
→`b.w 0x11F708` = `memset`). La guarda A de vídeo lee **sólo `out[1]`** (`0x60967C ldr.w r5,[r7,#0x104]`,
buffer en `0x609660 r7+0x100`), no `out[0]`. Cada campo sale de un campo homólogo de la tabla que
devuelve **`Mp4IfoIf::GetEnableFuncTbl`** (wrapper `0x6E9624`, `mp4Ifo_If.cpp:0x899`, `vt+0x9C` del
objeto en `[this+0x48]`) y se **recodifica** con `0x677AC4` (ver §2). Retorno: **0 = OK**, ≠0 = error
(el valor sale por `0x677B8E`→`0x64E300`, que despacha por `código & 0xFF000000` en `0x64E308`).

## 2. Todos los bits que puede llevar la máscara (codificador `0x677AC4`, 0xC8 B)

`r1 == 0` ⇒ devuelve 0 (`0x677B8A`). Si no, recorre **20 reglas** (19 `tst`/`orrne` + el bit de signo), una por bit interno:

| # | instr. | bit interno | bit público | | # | instr. | bit interno | bit público |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x677ACC` | `0x1` | `0x80000000` | | 11 | `0x677B26` | `0x10000` | `0x10000000` |
| 2 | `0x677AD6` | `0x2` | `0x00004000` | | 12 | `0x677B30` | `0x20000` | `0x01000000` |
| 3 | `0x677AE0` | `0x4` | `0x00400000` | | 13 | `0x677B3A` | `0x40000` | `0x02000000` |
| 4 | `0x677AEA` | `0x8` | `0x00000004` | | 14 | `0x677B44` | `0x80000` | `0x80000000` |
| 5 | `0x677AF4` | `0x10` | `0x00000001` | | 15 | `0x677B4E` | `0x1000000` | `0x40000000` |
| 6 | `0x677AFE` | `0x20` | `0x00200000` | | 16 | `0x677B58` | `0x2000000` | `0x80000000` |
| 7 | `0x677B08` | `0x40` | `0x80000000` | | 17 | `0x677B62` | `0x4000000` | `0x80000000` |
| 8 | `0x677B12` | `0x80` | `0x00000010` | | 18 | `0x677B6C` | `0x8000000` | `0x02000000` |
| 9 | `0x677B1C` | `0x100` | `0x00000010` | | 19 | `0x677B76` | `0x10000000` | `0x80000000` |
| | | | | | 20 | `0x677B80` | bit 31 de `r1` | `0x80000000` |

Bits públicos posibles: **`0x80000000`, `0x40000000`, `0x10000000`, `0x02000000`, `0x01000000`,
`0x00400000`, `0x00200000`, `0x00004000`, `0x00000010`, `0x00000004`, `0x00000001`**. La guarda de
vídeo **ignora `0x40000000`** (`0x609680 bic r5,r5,#0x40000000`); cualquier otro bit ⇒ inhibido.
`0x80000000` es el cajón «genérico» (lo producen 7 bits internos distintos).

**Condición verificada dentro de `GetInhInfo`** (única que el propio acsr añade): `0x67B768 bl 0x1EEFDC`
(TvSystem = `[0xAD28F8]+0x28`); si `TvSystem==0` y `vt+0x124()==1` (`0x67B774`–`0x67B780`) **o**
`TvSystem==1` y `vt+0x124()==0` (`0x67B784`–`0x67B78E`) ⇒ `0x677B90/94/98 orr r3,#4 / str`:
**`out[0] |= 0x00000004`**. Es un desacuerdo TvSystem↔`vt+0x124` y **cae en `out[0]`, no en `out[1]`**:
no llega a la guarda de vídeo. El resto de condiciones de bits son **internas a
`GetEnableFuncTbl`** (tabla de «enable/reason» del IFO MP4): fuente = el IFO/BD, **NO_VERIFICADO** el
mapeo bit↔causa (no se ha localizado la clase que implementa `vt+0x9C`; ver §7).

## 3. ¿Puede devolver bits ≠ 0 por un FALLO? Tres caminos, y qué deja en `out`

| Camino | Condición exacta | Log | `out[]` | Retorno |
|---|---|---|---|---|
| **A** | `[this+0x48] == 0` (`0x67B6F6/FC`) = no hay IFO | `"GetInhInfo : MP4 No exist."` `0x67B702` | todo **0** (memset) | `0x018000FF` (`0x67B736`) |
| **B** | `[[this+0xC]] vt+0x154() == 0` (`0x67B710/16`) = no cargado | `"GetInhInfo : It is not loaded."` `0x67B71C` + assert `0x677BB2` (línea `0x25D`) | todo **0** | `0x018000FF` (literal en `0x67B8C4`, cargado en `0x67B736`) |
| **C** | la llamada al IFO devuelve ≠0 (`0x67B750`,`0x67B758 bne`) | — | **`0x80000000` × 15 palabras** (`0x67B854`–`0x67B890`) | código del IFO |

No hay cuarto camino: el `memset` de `0x67B6F2` precede a todo, y cada `out[k]` se escribe **sólo si** su
origen es ≠0 (`cbz r1` en `0x67B75C`, `0x67B79E`, `0x67B7AC`, … hasta `0x67B846`). **Ninguna ruta deja
`out` sin inicializar.** Un fallo duro **no** produce bits: produce retorno ≠0 (A/B) o el relleno
`0x80000000` (C).

## 4. El valor basura exacto y quién lo consume

Camino C: `out[0]…out[0x38]` = **`0x80000000`** (15 `str.w r3,[r8,#k]` con `r3 = 1<<31`, `0x67B854`).
- La guarda de vídeo **no lo lee**: `0x609674 bl 0x67B6E0` → `0x609678 cmp r0,#0; bne 0x609766` (sale con 0).
- **Sí lo leen 3 llamadores que ignoran el retorno**: `0x61F3BC`, `0x61F578`, `0x61F7CE` hacen
  `bl 0x67B6E0` y acto seguido `ldr r3,[r7,#0x2E0]` (= `out[0]`) `orr r3,r3,#0x10` (`0x61F3CA`, `0x61F588`,
  `0x61F7DC`). Con el relleno quedaría **`0x80000010`**. `0x609304` y `0x617BC0` sí comprueban el retorno.

## 5. Quién escribe `[ctrl+0xDB8]` y con qué arranca

Escritores en todo libmpr: **8 `str`** — `0x437A52` (payload del mensaje `0x40000017`, `[core+0xDC0]` =
`mmgrId` y `[core+0xDB8]` = `contentTypes`), `0x438188`, `0x4381EC`, `0x438C98`, `0x438DE4`, `0x438F96`
(los cinco, payloads homólogos de otras entradas), y los **ceros** `0x437B06`, `0x437B68` (+ `0x437AFA`).
Ningún inicializador estático. **Arranca a 0** y, sobre todo: **máscara 0 ⇒ la guarda devuelve 1 y pasa**
(`0x447AE0 movs r0,#1`, ningún bit que probar). Por tanto una máscara obsoleta o sin escribir **no puede**
provocar el `0x1A`; el `0x1A` exige que `0x437A28` haya escrito la máscara en ese mismo request.

## 6. Consecuencia para el clip propio de la cámara

El fallo con un clip propio no necesita «bits de contenido»: si el acsr MP4 no tiene IFO (A) o no está
cargado (B), `GetInhInfo` devuelve ≠0 y `GetPlayMovieStatus(6)` sale por `0x609766` con **0 pero SIN
imprimir `playMovieInh`** ⇒ guarda A ⇒ `0x1A`. Distinguible en el log: `"GetInhInfo : MP4 No exist."` o
`"GetInhInfo : It is not loaded."` **en lugar de** `playMovieInh[...]`. `"Recuperar BD imág."` reconstruye
`AVF_INFO` pero no recarga el acsr: coherente con que no lo arregle. Si en cambio aparece `playMovieInh`,
el bit es un reason real del IFO/BD (o `vt[0x1E0](0x28)` de `[AviMMgr+8]`) y su causa está en §2/§8.

## 7. Límites (NO_VERIFICADO)

- **NO_VERIFICADO** qué causa activa cada bit interno de `GetEnableFuncTbl` (`vt+0x9C`): no se localizó la
  clase que implementa la interfaz `Mp4IfoIf` (la cadena `mp4Ifo_If` sólo aparece en libmpr; ni libObj ni
  el rootfs tienen otra copia). Sin ese mapeo no se puede atribuir un `playMovieInh` concreto a «IFO
  ilegible» o «BD inconsistente» por lectura del binario.
- **NO_VERIFICADO** el significado de `vt+0x1E0(0x28)` de `[AviMMgr+8]` (el otro sumando de la máscara, OR
  en `0x609684`) y de `vt+0x124` de `[this+0xC]`.
- **NO_VERIFICADO** que el allocator ponga a 0 `[ctrl+0xDB8]` (no hay escritor estático; irrelevante porque
  máscara 0 ⇒ la guarda pasa).
- `memset` identificado por el stub `0x11F708`→`.plt` `memset` `0x11F70C` (desfase de 4 del helper).
