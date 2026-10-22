# S116 — `[SFRS]`: 117 trazas del subsistema en A6000 fw3.21

> Hito de la **línea de ingeniería inversa general**. Todo lo que sigue sale de los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B, sha256
> `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`), con la convención
> verificada **vaddr = 0x43541000 + file_offset**. Sin REA, sin Ghidra, sin ejecutar firmware.
> Cada afirmación lleva su dirección y, cuando aplica, la cita literal del texto o de la
> instrucción. Lo que no se ha podido comprobar está marcado **NO VERIFICADO** (§11).

## 1. Qué es `[SFRS]` (sin expandir la sigla)

`[SFRS]` es **la etiqueta de módulo de 117 cadenas de traza**. Las siglas **no aparecen
expandidas en ningún byte del binario**: lo único que hay es el prefijo literal `[SFRS]`. La
cadena `SfrYc.cpp` (`0x43ce73ec`) y el resto de nombres de fichero citados por el propio
módulo (§8) son los únicos indicios de nomenclatura; **no se ha verificado** que `Sfr` + `Yc`
componga la sigla.

Lo que las trazas sí dicen, en su propio vocabulario:

| grupo de nombres | citas literales (vaddr) |
|---|---|
| pines y datos YC | `[SFRS][DEBUG][SETPIN] YccOut(false): file=%s line=%d` (`0x43ce8cde`), `[SFRS][PINSEND]  YC FREE at async task: file=%s line=%d` (`0x43ce962d`) |
| secuencia SA | `[SFRS] ***SA_ACK` (`0x43ce97f4`), `[SFRS] ***SA_OPEN_CMP` (`0x43ce9805`) |
| máquina de estado del path | `[SFRS][CMD] ***SET_PATH(0x%02x)***` (`0x43ce9ab9`), `[SFRS] BEGIN_TRANS_WAIT` (`0x43ce9b67`) |
| tres modos de grabación | `EFFECTMOVIEREC` (`0x43ce9c58`), `MOTIONSHOTVIDEO` (`0x43ce99ab`), `SUPERSTABLEMOVIE` (`0x43ceabc3`) |

> Lectura de conjunto (**interpretación**, no decodificación): el módulo instrumenta el
> transporte de datos YC por pines, la secuencia SA que lo acompaña y tres modos de grabación
> que consumen ese transporte. El firmware no dice más.

## 2. Cifras verificadas

| magnitud | valor | cómo se obtiene |
|---|---:|---|
| cadenas `[SFRS]` distintas | **117** | `data.find(b"[SFRS]")` sobre la imagen; toda aparición inicia racha imprimible |
| rango de las cadenas | `0x43ce7661` – `0x43ceb8c4` | primera / última aparición (16 995 B de intervalo, ≈17 KB) |
| puntos de emisión (`ldr`+`add` PC-relativo) | **131** | pares PIC verificados (§6) |
| sitios sin cadena resuelta | **0** | el script aborta si alguno queda sin referencia |
| funciones que emiten trazas | **52** | prólogo Thumb más cercano por delante, hueco ≤ 0x8000 |
| rango del código | `0x439a6be8` – `0x439b1cb2` | primera / última función (≈44 KB) |
| sitios `add` fuera del clúster `0x439a0000`–`0x439c0000` | **0** | mínimo `0x439a6dc8`, máximo `0x439b2034` |
| cadenas emitidas por más de una función | **3** | `0x43ce9407` (2 funciones, 3 sitios), `0x43ce9436` (7), `0x43ce9a69` (3) |

Etiquetas internas de las 117 cadenas (conteo directo sobre el texto): `[ERR]` 54, sin etiqueta
37, `[CMP]` 13, `[PINSEND]` 5, `[DEBUG]` 4, `[ERROR]` 1, `[FUNC]` 1, `[CMD]` 1, `[INFO]` 1.
60 de las 117 llevan especificadores de formato y 9 llevan `file=%s line=%d`.

`[SFRS][ERR][PINSEND]  ERROR!!` (`0x43ce9407`) y `[SFRS][ERROR][PINSEND]  ERROR!!`
(`0x43ce9436`) son **dos cadenas distintas** (dos espacios tras `!!`, `ERR` vs `ERROR`); se
cuentan por separado.

## 3. Sub-bloques (clasificación por subcadena, no semántica)

La clasificación la hace `classify()` en `scan_sfrs.py` con reglas de subcadena sobre el texto
(`SUPERSTABLEMOVIE`, `MOTIONSHOTVIDEO`, `EFFECT`/`SEND_MSG_TO_EXECUTER`/`ExecSRC canvas`,
`PINSEND`/`[SETPIN]`/`[GETPIN]`/`Send RecPin`/`Send EEPin`, `***SA_`, `MultiplexTrigger`,
`SET_PATH`/`STATUS_`/`SETRECSTATE`/`NowVfc`, `RC_CALLBACK`/`CtSetAicParam`/`SendExecTrigger`).
Es una agrupación **por nombre de mensaje**, no una decodificación de comportamiento; los rangos
se solapan porque son primera y última aparición, no bloques contiguos.

| sub-bloque | cadenas | primer vaddr | último vaddr | funciones |
|---|---:|---|---|---:|
| `RC_AIC_TRIGGER` | 3 | `0x43ce7661` | `0x43ce78ec` | 3 |
| `PINSEND` | 12 | `0x43ce8cde` | `0x43ce962d` | 11 |
| `SA` | 6 | `0x43ce9795` | `0x43ce9831` | 2 |
| `MOTIONSHOTVIDEO` | 25 | `0x43ce99ab` | `0x43ceaa56` | 11 |
| `SET_PATH_STATUS` | 9 | `0x43ce99ed` | `0x43ce9b67` | 7 |
| `EFFECTMOVIEREC` | 23 | `0x43ce9c58` | `0x43cea384` | 7 |
| `MULTIPLEXTRIGGER` | 2 | `0x43ceab13` | `0x43ceab3a` | 2 |
| `SUPERSTABLEMOVIE` | 37 | `0x43ceabc3` | `0x43ceb8c4` | 9 |
| **total** | **117** | | | |

Las 23 de `EFFECTMOVIEREC` incluyen `[SFRS][INFO] ***SEND_MSG_TO_EXECUTER, cateID:0x%x
msgID:0x%x err:0x%x` (`0x43cea29b`) y `[SFRS]ExecSRC canvas:0x%x, time:0x%x, nowVfc:0x%x
configNum:0x%x` (`0x43cea2e1`): ninguna de las dos contiene `EFFECT`, entran por las reglas
`SEND_MSG_TO_EXECUTER` / `ExecSRC canvas`.

## 4. Las 52 funciones y sus trazas

Cada fila es un prólogo `push {…,lr}` / `push.w {…,lr}` detectado en el clúster; «sitios» es el
número de pares `ldr`+`add` dentro de esa función que resuelven a una cadena `[SFRS]`.

| función | sitios | cadenas | primera cadena |
|---|---:|---:|---|
| `0x439a6be8` | 1 | 1 | `0x43ce7661` `[SFRS]RC_CALLBACK result:0x%x` |
| `0x439a6dd4` | 2 | 1 | `0x43ce767f` `[SFRS][ERR]ERR at CtSetAicParam` |
| `0x439a8350` | 1 | 1 | `0x43ce78ec` `[SFRS]SendExecTrigger TriggerType 0x%02x` |
| `0x439aad92` | 1 | 1 | `0x43ce8cde` `[SFRS][DEBUG][SETPIN] YccOut(false): file=%s line=%d` |
| `0x439aae20` | 1 | 1 | `0x43ce8d2f` `[SFRS][DEBUG][GETPIN] ReqYccAsap(true): file=%s line=%d` |
| `0x439ab7fc` | 2 | 1 | `0x43ce9407` `[SFRS][ERR][PINSEND]  ERROR!!: file=%s line=%d` |
| `0x439ab93a` | 1 | 1 | `0x43ce9436` `[SFRS][ERROR][PINSEND]  ERROR!!: file=%s line=%d` |
| `0x439ab9a2` | 1 | 1 | `0x43ce9436` idem |
| `0x439abbfe` | 3 | 3 | `0x43ce9436` idem, `0x43ce9467` `Send RecPin`, `0x43ce94af` `Send EEPin` |
| `0x439ac09e` | 1 | 1 | `0x43ce9436` idem |
| `0x439ac26e` | 1 | 1 | `0x43ce9436` idem |
| `0x439ac2fa` | 5 | 5 | `0x43ce9511` `IP trans`, `0x43ce955e` `shutter mute thru`, `0x43ce9591` `kari review thru`, `0x43ce95c3` `kari review free`, `0x43ce95f5` `ACTIVATE_DONE` |
| `0x439ac742` | 3 | 3 | `0x43ce9407` idem, `0x43ce9436` idem, `0x43ce962d` `YC FREE at async task` |
| `0x439aca46` | 1 | 1 | `0x43ce9436` idem |
| `0x439ace92` | 2 | 2 | `0x43ce9795` `***SA_CALC_CMP errCode:0x%x errStatus:0x%x`, `0x43ce97c7` `***SA_ERR` |
| `0x439acf1a` | 4 | 4 | `0x43ce97f4` `***SA_ACK`, `0x43ce9805` `***SA_OPEN_CMP`, `0x43ce981b` `***SA_CALC_CMP`, `0x43ce9831` `***SA_CLOSE_CMP` |
| `0x439ad42c` | 1 | 1 | `0x43ce99ab` `***FUNC_CMD_SET_MOTIONSHOTVIDEO_PARAM_PARAMETER_ERROR` |
| `0x439ad548` | 1 | 1 | `0x43ce99ed` `[SFRS][FUNC]********************FUNCCMD_SETRECSTATE 0x%x********************` |
| `0x439ad86e` | 1 | 1 | `0x43ce9a69` `[SFRS][DEBUG] NowVfc=%d, lastSendTime=%d` |
| `0x439ad942` | 1 | 1 | `0x43ce9a69` idem |
| `0x439ada02` | 1 | 1 | `0x43ce9a69` idem |
| `0x439adc20` | 1 | 1 | `0x43ce9a92` `[SFRS][CMP] ***SET_PATH_CMP(0x%02x)***` |
| `0x439adcd2` | 2 | 2 | `0x43ce9ab9` `[SFRS][CMD] ***SET_PATH(0x%02x)***`, `0x43ce9adc` `[SFRS] PATH_STATUS_ERR` |
| `0x439addea` | 4 | 4 | `0x43ce9af3` `ScalarInfraPathCmdSetPath::Execute() msg->GetStatus()=0x%08x`, `0x43ce9b37` `STATUS_INIT`, `0x43ce9b4a` `STATUS_END_TRANS_WAIT`, `0x43ce9b67` `BEGIN_TRANS_WAIT` |
| `0x439ae280` | 1 | 1 | `0x43ce9c58` `***EFFECTMOVIEREC_EXECUTER_EXEC_POST …` |
| `0x439ae43a` | 4 | 3 | `0x43ce9cae` `…_EXEC_SA …`, `0x43ce9d02` `EFFECT_MOVIE_REC_SAOUT_BUFFER_ALLOC_FAILED`, `0x43ce9d3c` `…_EXEC_SA_SA_BUSY` |
| `0x439ae8b2` | 2 | 2 | `0x43ce9d6e` `…_EXEC_VFX currentCanvasHandle:0x%x…`, `0x43ce9ddc` `…_EXEC_VFX0 …` |
| `0x439aec00` | 9 | 7 | `0x43ce9f11` `SET_PATH_EFFECTMOVIEREC_MANAGER_SRC_ACQUIRE_DONE` … `0x43cea06f` `SET_PATH_EFFECTMOVIEREC_Initialize_COMP` |
| `0x439aef20` | 5 | 5 | `0x43cea0a6` `…_MANAGER_SRC_RELEASE_DONE` … `0x43cea1aa` `…_MANAGER_FINALIZE_COMP` |
| `0x439af1fc` | 1 | 1 | `0x43cea29b` `[SFRS][INFO] ***SEND_MSG_TO_EXECUTER, cateID:0x%x msgID:0x%x err:0x%x` |
| `0x439af2ee` | 4 | 4 | `0x43cea2e1` `[SFRS]ExecSRC canvas:0x%x, time:0x%x, nowVfc:0x%x configNum:0x%x`, `0x43cea322` `EFFECTMOVIEREC_OPEN_FAILED`, `0x43cea34c`, `0x43cea384` |
| `0x439af55e` | 2 | 2 | `0x43cea43f` `SET_PATH_MOTIONSHOTVIDEO_WORKBUFFER_ALLOC_FAILED`, `0x43cea47f` `MOTIONSHOTVIDEO_WORKBUFFER_ALLOC_FAILED` |
| `0x439af706` | 8 | 8 | `0x43cea4b6` `SET_PATH_MOTIONSHOTVIDEO_Finalize` … `0x43cea65e` `…_Finalize_COMP` |
| `0x439afb84` | 1 | 1 | `0x43cea798` `MOTIONSHOTVIDEO_BUFFER_FREE_FAILED` |
| `0x439afc78` | 1 | 1 | `0x43cea7ca` `MOTIONSHOTVIDEO_EXEC_WAIT_SA_COMP_WAIT` |
| `0x439afd0c` | 1 | 1 | `0x43cea7fb` `MOTIONSHOTVIDEO_RCOUTBUFFER_ALLOC_FAILED` |
| `0x439afd9e` | 4 | 4 | `0x43cea833` `…_EXEC_RC_SET_PARAM_FAILED`, `0x43cea86b` `…_EXEC_RC_BOTTOM`, `0x43cea899` `…_EXEC_RC_RC_KICK_FAILED`, `0x43cea8cf` `***RC_OUT_BUFFER_FULL` |
| `0x439affb4` | 1 | 1 | `0x43cea8f1` `MOTIONSHOTVIDEO_SRCOUTBUFFER_ALLOC_FAILED` |
| `0x439b0052` | 2 | 2 | `0x43cea92a` `…_EXEC_SRC_SET_PARAM_FAILED`, `0x43cea963` `…_EXEC_SRC_SRC_KICK_FAILED err:0x%0x` |
| `0x439b01a4` | 3 | 3 | `0x43cea9a5` `…_SA_OUT_BUFFER_ALLOC_FAILED`, `0x43cea9df` `…_PARAM_BUFFER_ALLOC_FAILED`, `0x43ceaa18` `…_PARAM_MMU_OPEN_FAILED err:0x%x` |
| `0x439b033e` | 1 | 1 | `0x43ceaa56` `MOTIONSHOTVIDEO_SET_SA_PARAM_FAILED` |
| `0x439b047c` | 1 | 1 | `0x43ceab13` `[SFRS]MultiplexTriggerExecuterActivate` |
| `0x439b04e6` | 1 | 1 | `0x43ceab3a` `[SFRS]MultiplexTriggerExecuterClose` |
| `0x439b05fc` | 1 | 1 | `0x43ceabc3` `SUPERSTABLEMOVIE_SETMAILBOX_DRIVE_FAILED,err=0x%08x` |
| `0x439b06a4` | 1 | 1 | `0x43ceac06` `SUPERSTABLEMOVIE_GETMAILBOX_DRIVE_FAILED,err=0x%08x` |
| `0x439b07c2` | 15 | 15 | `0x43ceacb8` `SET_PATH_SUPERSTABLEMOVIE::Initialize_SaOpen` … `0x43ceb04f` `…_Initialize_COMP` |
| `0x439b0f16` | 9 | 9 | `0x43ceb0d1` `…::Finalize_SetMailBox` … `0x43ceb2b6` `…_Finalize_COMP` |
| `0x439b16c0` | 1 | 1 | `0x43ceb5db` `SUPERSTABLEMOVIE_EXEC_SRC_SRC_KICK_FAILED err:0x%0x` |
| `0x439b1824` | 1 | 1 | `0x43ceb61e` `SUPERSTABLEMOVIE_RECORDSIZE x:%d y:%d` |
| `0x439b1936` | 1 | 1 | `0x43ceb653` `SUPERSTABLEMOVIE_EXEC_RC_RC_KICK_FAILED err:0x%0x` |
| `0x439b1b30` | 1 | 1 | `0x43ceb694` `SUPERSTABLEMOVIE_EXEC_VFX_VFX_KICK_FAILED err:0x%0x` |
| `0x439b1cb2` | 7 | 7 | `0x43ceb6d7` `SRCINPUTMEM_ALLOC_FAILED` … `0x43ceb8c4` `VFXOUTPUTMEM_FREE_FAILED` |

Las direcciones de función son **puntos de prólogo heurísticos** (el `push` más cercano por
delante, a ≤ 32 KB): sirven para agrupar sitios, no son símbolos del firmware.

## 5. Puntos de emisión y regla PIC (corrección metodológica)

El patrón es el habitual de este firmware: `ldr rX,[pc,#imm]` carga una **palabra literal**
offset desde el módulo, y `add rX,pc` le suma el PC. Reglas aplicadas en `scan_sfrs.py`:

1. **Barrido con fronteras Thumb**: se avanza 4 bytes si el halfword es prefijo de instrucción
   de 32 bits (`(h >> 11) in (0x1d,0x1e,0x1f)`), si no 2. Sin esto se interpreta como
   `add rX,pc` el segundo halfword de otra instrucción.
2. **Solo el `ldr` inmediatamente anterior del mismo registro**, con hueco ≤ 0x20 bytes y sin
   retroceder a `ldr` más antiguos (la reutilización de registro produce falsos positivos).
3. **PC sin alinear**: `destino = palabra_literal + (addr_add + 4)`. La variante alineada
   (`(addr_add + 4) & ~3`) cae **2 bytes antes** del inicio de la cadena y se descartó por
   evidencia (§6).
4. El destino debe coincidir **exactamente** con el inicio de una racha imprimible.

Corrección respecto al borrador anterior de S116: con la regla laxa (retroceder al último
`ldr` del registro aunque estuviera lejos, y PC alineado) se obtenían pares que no cuadraban
con el texto de la cadena. La regla actual resuelve **117/117 cadenas** y **131/131 sitios**
atribuidos a función; el script aborta si aparece una cadena sin referencia o un sitio sin
función.

## 6. Evidencia de bytes: `SETPIN`, `GETPIN` y `EXECUTE_PIN_SEND`

`SETPIN` — función `0x439aad92` (`push {r4,r5,r6,lr}` en `0x439aad92`):

| addr | instrucción | lectura |
|---|---|---|
| `0x439aada2` | `ldr r1,[r0,#0x10]` | campo del objeto |
| `0x439aada4` | `cmp r1,#1` | compara con 1 |
| `0x439aada6` | `bne #0x439aadb2` | si **no** es 1, va al camino que registra |
| `0x439aada8`–`0x439aadb0` | `ldr.w r3,[r3,#0x88]` / `blx r3` / `b #0x439aadca` | camino «igual»: llama y **se salta** el log |
| `0x439aadb4` | `movs r1,#0` | argumento `false` |
| `0x439aadbc`–`0x439aadc0` | `ldr r0,[pc,#0x24]` / `ldr r1,[pc,#0x28]` / `movs r2,#0x3a` | formato, fichero y **línea 58** |
| `0x439aadc2`/`0x439aadc4` | `add r0,pc` / `add r1,pc` | resuelven a `0x43ce8cde` y `0x43ce8d13` |

- `0x439aadc6 + 0x33df18 = 0x43ce8cde` → `[SFRS][DEBUG][SETPIN] YccOut(false): file=%s line=%d`.
- `0x439aadc8 + 0x33df4b = 0x43ce8d13` → literal `SystemCmdAsyncCmdSetPin.cpp`.
- `0x3a` = 58 coincide con el `line=%d` del texto.

`GETPIN` — función `0x439aae20` (`push {r3,r4,r5,lr}` en `0x439aae20`):

| addr | instrucción | lectura |
|---|---|---|
| `0x439aae3a` | `ldr r1,[r0,#0x10]` | mismo campo |
| `0x439aae3c` | `cmp r1,#1` | |
| `0x439aae3e` | `bne #0x439aae58` | si no es 1, no registra |
| `0x439aae42` | `ldr.w r3,[r3,#0x80]` | otro método virtual (`+0x80` vs `+0x88`) |
| `0x439aae48`–`0x439aae4c` | `ldr r0,[pc,#0x1c]` / `ldr r1,[pc,#0x20]` / `movs r2,#0x38` | formato, fichero y **línea 56** |
| `0x439aae4e`/`0x439aae50` | `add r0,pc` / `add r1,pc` | resuelven a `0x43ce8d2f` y `0x43ce8d67` |

- `0x439aae52 + 0x33dedd = 0x43ce8d2f` → `[SFRS][DEBUG][GETPIN] ReqYccAsap(true): file=%s line=%d`.
- `0x439aae54 + 0x33df13 = 0x43ce8d67` → literal `SystemCmdAsyncGetPin.cpp`.
- `0x38` = 56 coincide con el `line=%d` del texto.

Conclusión verificada: **el argumento `file=%s` no es la cadena `[SFRS]`**, es un segundo
literal que apunta al nombre del `.cpp` del punto de llamada, y `line=%d` es una constante
inmediata en el mismo bloque. (Que eso venga de `__FILE__`/`__LINE__` es **inferencia**, no
byte verificado.) Efecto práctico: los literales `.cpp` permiten atribuir fichero fuente a las
funciones que emiten trazas con `file=%s` (§8).

`EXECUTE_PIN_SEND` — cola de la función `0x439b1cb2`, log final en `0x439b1f68`:

```
0x439b1f4c: ldrb.w r2,[r4,#0x3f5]
0x439b1f50: ldrb.w r1,[r4,#0x3f6]
0x439b1f54: movs   r3,#1
0x439b1f56: str.w  r3,[r4,#0x410]
0x439b1f5a: ldrb.w r3,[r4,#0x3f4]
0x439b1f5e: str.w  r0,[r4,#0x40c]     ; r0 = retorno de bl 0x43b64a7a
0x439b1f62: ldrb.w r0,[r4,#0x3ff]
0x439b1f66: str    r0,[sp]            ; 4.º vararg (stack)
0x439b1f68: ldr    r0,[pc,#0x108]
0x439b1f6a: add    r0,pc              ; -> 0x43ceb80d
0x439b1f6c: bl     #0x435ab880
```

Los cuatro argumentos variables del texto `[SFRS][ERR]
***SUPERSTABLEMOVIE_EXECUTE_PIN_SEND, dataContent:0x%x, dataPlacement:0x%x,
dataTransfer:0x%x, scanline:0x%x` (`0x43ceb80d`) salen, en orden, de `[r4,#0x3f6]`,
`[r4,#0x3f5]`, `[r4,#0x3f4]` y `[r4,#0x3ff]`; antes de registrar se escribe
`[r4,#0x410]=1` y `[r4,#0x40c]=` el retorno de `bl 0x43b64a7a`. Es decir: los cuatro nombres
del texto son **etiquetas de cuatro campos contiguos de un mismo objeto** (offsets `0x3f4`,
`0x3f5`, `0x3f6`, `0x3ff`), no cuatro estructuras distintas.

## 7. Cadenas repetidas y funciones compartidas

Solo tres cadenas se emiten desde más de una función:

| cadena | vaddr | funciones |
|---|---|---|
| `[SFRS][ERR][PINSEND]  ERROR!!: file=%s line=%d` | `0x43ce9407` | `0x439ab7fc`, `0x439ac742` |
| `[SFRS][ERROR][PINSEND]  ERROR!!: file=%s line=%d` | `0x43ce9436` | `0x439ab93a`, `0x439ab9a2`, `0x439abbfe`, `0x439ac09e`, `0x439ac26e`, `0x439ac742`, `0x439aca46` |
| `[SFRS][DEBUG] NowVfc=%d, lastSendTime=%d` | `0x43ce9a69` | `0x439ad86e`, `0x439ad942`, `0x439ada02` |

Las dos primeras son el mismo mensaje con distinto nivel (`ERR`/`ERROR`) y el `file=%s` los
distingue en ejecución; la tercera se repite en tres funciones del bloque `SET_PATH_STATUS`.
`0x43ce767f` (`[SFRS][ERR]ERR at CtSetAicParam`) tiene **dos** sitios dentro de la misma
función `0x439a6dd4`: `ldr`/`add` en `0x439a6e14`/`0x439a6e16` y en `0x439a6e76`/`0x439a6e78`.

## 8. Ficheros fuente citados desde el clúster

En la imagen hay **573 literales `*.cpp` distintos** (ningún nombre repetido). **24** de ellos
son citados por código del clúster `0x439a0000`–`0x439c0000`. «sitios» = pares `ldr`+`add` que
resuelven a ese literal en toda la imagen (todos dentro del clúster); «funciones» = funciones
del clúster que lo citan.

| fichero | vaddr del literal | sitios | funciones |
|---|---|---:|---:|
| `MsgAccessor.cpp` | `0x43c81a55` | 36 | 12 |
| `MsgIterator.cpp` | `0x43c81e90` | 47 | 14 |
| `SubsystemMain.cpp` | `0x43c82317` | 19 | 3 |
| `WaitQueue.cpp` | `0x43c8244c` | 12 | 4 |
| `SubsystemFactory.cpp` | `0x43c83b6a` | 9 | 1 |
| `SystemCmdPinConnect.cpp` | `0x43c83fa3` | 6 | 1 |
| `SystemCmdPinRequestConnect.cpp` | `0x43c8403c` | 6 | 1 |
| `SystemCmdPinSend.cpp` | `0x43c843ac` | 33 | 9 |
| `SystemCmdPinDisconnect.cpp` | `0x43c85e25` | 6 | 1 |
| `SystemCmdPinGet.cpp` | `0x43c85eec` | 3 | 1 |
| `SystemCmdPinRequestDisconnect.cpp` | `0x43c85f7b` | 6 | 1 |
| `ScalarInfraAsyncMain.cpp` | `0x43ce59fd` | 3 | 1 |
| `ScalarInfraSequenceJpeg.cpp` | `0x43ce6320` | 3 | 1 |
| `ScalarInfraSequenceJpegStage.cpp` | `0x43ce6693` | 2 | 1 |
| `ScalarInfraSequenceLiveView.cpp` | `0x43ce68e9` | 3 | 2 |
| `ScalarInfraSequenceLiveViewStage.cpp` | `0x43ce6ad9` | 5 | 2 |
| `ScalarInfraSequenceSa.cpp` | `0x43ce6c15` | 10 | 5 |
| `ScalarInfraSequenceSaStage.cpp` | `0x43ce6e16` | 6 | 3 |
| `ScalarInfraSequenceUtility.cpp` | `0x43ce7126` | 4 | 2 |
| `SfrYc.cpp` | `0x43ce73ec` | 2 | 1 |
| `DrvCallRc.cpp` | `0x43ce76fb` | 5 | 1 |
| `SystemCmdAsyncCmdSetPin.cpp` | `0x43ce8d13` | 1 | 1 |
| `SystemCmdAsyncGetPin.cpp` | `0x43ce8d67` | 1 | 1 |
| `ScalarInfraSuperStableMovieManager.cpp` | `0x43ceb0aa` | 1 | 1 |

Solo **12 de las 52 funciones con traza** citan uno de estos literales (las 9 de
`SystemCmdPinSend.cpp`, más `SystemCmdAsyncCmdSetPin.cpp`, `SystemCmdAsyncGetPin.cpp` y
`ScalarInfraSuperStableMovieManager.cpp`). Las otras 40 no pasan `file=%s`, así que **no se les
puede asignar fichero fuente por esta vía**.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20

Blob A7S: `firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/
nflasha3_unpacked_unpacked/av-cam.bin` (sha256
`b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`). Comparación **texto a
texto ignorando especificadores de formato**: cada `%…` (con flags, ancho y longitud) se
sustituye por `%`, de modo que `%04d` y `%d` cuentan como el mismo hueco. La normalización no
toca el texto literal (`0x`, corchetes, espacios).

| magnitud | valor |
|---|---:|
| cadenas `[SFRS]` en A6000 fw3.21 | 117 |
| cadenas `[SFRS]` en A7S fw3.20 | 151 |
| **comunes A6000 ∩ A7S** | **117** |
| exclusivas de A6000 | **0** |
| exclusivas de A7S | **34** |

Las 34 exclusivas de la A7S, agrupadas por lo que dicen:

- **path / máquina de estados**: `ScalarInfraPathCmdSetPath::TransPath` + `Idle`, `Jpeg`,
  `SaThrough`, `SaProc`, `MotionShotVideo`, `SuperStableMovie`, `LiveView`,
  `EffectMovieRec`, `Audio`, `path_id=0x%08x`, `SendComp() err=0x%08x`,
  `SendOpenPathCmdToAsyncTask`, `SendClosePathCmdToAsyncTask`, `msg->GetMsgLength() = %d`,
  `Notify replyId=0x%08x`.
- **audio** (ninguna traza de audio existe en la A6000): `[SFRS][CMP]
  ***SET_PATH_AUDIO_Initialize_COMP`, `***SET_PATH_AUDIO_Finalize_COMP`,
  `[SFRS][ERR] ***AUDIO_BUFFER_FREE_FAILED`, `***AUDIO_EXEC_WAIT_SA_COMP_WAIT`,
  `***AUDIO_EXEC_SA_DONE`, `***AUDIO_SA_OUT_BUFFER_ALLOC_FAILED`,
  `***AUDIO_PARAM_BUFFER_ALLOC_FAILED`, `***AUDIO_PARAM_MMU_OPEN_FAILED err:0x%x`.
- **pines y audio-pin**: `[SFRS][PIN] AudioPinFree handle(%#x)`,
  `[SFRS][PIN] AudioPinSend handle(%#x)`, `[SFRS][PIN] PinSendPathAudio WAIT_SA_CREATE`,
  `[SFRS][PIN] PinSendPathAudio WAIT_SAAUDIO_OUT`, `[SFRS][PIN] AUDIO PIN EXECUTE path(%#x)`,
  `[SFRS][PIN] AUDIO PIN ACTIVATE handle(%#x)`, `[SFRS][PINCOUNT]  1:send(%d)`,
  `2:comp(%d)`, `3:vdf(%d)`, y los dos `DEFAULT FREE: file=%s line=%d` (niveles `[DEBUG]` y
  `[PINSEND]`).

Lectura: **el vocabulario `[SFRS]` de la A6000 es un subconjunto estricto del de la A7S**
(117 de 151, cero exclusivas en el otro sentido). Que la A7S tenga 34 trazas más encaja con que
instrumente un path con audio y contadores de pines; **NO VERIFICADO** si esas funciones existen
en la A6000 sin traza o no existen.

## 10. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 117 cadenas y su rango | `scan_sfrs.py` recorre la imagen buscando `b"[SFRS]"` y exige que el byte anterior no sea imprimible |
| 131 sitios y 117/117 resueltos | emparejamiento PIC estricto; `missing` vacío y `atribuidos == sitios` (aborta si no) |
| 52 funciones | prólogos `push {…,lr}` / `push.w` con hueco ≤ 0x8000 |
| ningún sitio fuera del clúster | mínimo `0x439a6dc8`, máximo `0x439b2034` ⊂ `0x439a0000`–`0x439c0000` |
| PC no alineado | `0x33df18 + (0x439aadc2+4) = 0x43ce8cde`; con `&~3` daría `0x43ce8cdc`, que apunta a `'E'` |
| `line=%d` = constante cercana | `movs r2,#0x3a` (58) en SETPIN y `movs r2,#0x38` (56) en GETPIN |
| `file=%s` = literal `.cpp` | los `add` de `r1` resuelven a `0x43ce8d13` y `0x43ce8d67` |
| 8 sub-bloques suman 117 | `classify()` no deja cadenas sin clasificar (aborta) |
| A7S 151 / 117 / 34 | mismo extractor sobre el blob A7S y normalización de `%…` |

## 11. NO VERIFICADO / abierto

- **Significado de las siglas** `SFRS`, `AIC`, `RC`, `VFX`, `IIB` y del identificador
  `PINSEND`: el firmware no las expande en ningún sitio; no se han inventado expansiones.
- **Tipo y estructura de cada campo** (`nowVfc`, `transTime`, `configNum`, `dataContent`,
  `dataPlacement`, `dataTransfer`, `scanline`, `Handle`, `osalID`, `GetCounter`…): solo se sabe
  el **offset** del objeto del que salen en los casos disecados (§6), no su semántica.
- **Tabla de líneas**: no se ha reconstruido la numeración de los `.cpp`; no se ha comprobado
  que `line=%d` corresponda a la línea real del fichero citado en `file=%s`.
- **Fichero fuente de 40 de las 52 funciones**: no pasan `file=%s`, así que no hay atribución.
- **Significado de los modos**: `EFFECTMOVIEREC`, `MOTIONSHOTVIDEO`, `SUPERSTABLEMOVIE` y
  `MULTIPLEXTRIGGER` se agrupan por nombre; no se ha verificado qué hacen ni si se excluyen
  entre sí.
- **Relación con otros módulos** (imager, encoder, gestor de captura): no verificada en este
  hito; aquí solo constan los nombres de fichero que el propio clúster cita.
- La agrupación en sub-bloques y la atribución a función son **heurísticas** (subcadena y
  prólogo), no símbolos del firmware.

## 12. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 117 cadenas con vaddr/offset/texto |
| `pic_refs_sfrs.json` | los 131 pares `(ldr, add)` por cadena |
| `func_map.json` | mapa función → trazas (52 funciones) |
| `sfrs.json` | resumen: recuentos, sub-bloques, funciones, ficheros fuente, diferencial A7S, NO VERIFICADO |
| `scan_sfrs.py` | extractor único y reproducible (regenera los cuatro JSON) |
| `docs/capture/s116-sfrs.md` | nota corta de captura |
| `tests/test_s116_sfrs.py` | tests sobre bytes reales |

Reproducir: `.venv/bin/python analysis/s116_sfrs/scan_sfrs.py` (≈6 s, idempotente) y
`.venv/bin/python -m pytest tests/test_s116_sfrs.py`.

## 13. Revisión del agente principal (correcciones aplicadas)

1. **Siglas inventadas**: el borrador expandía `SFRS` como «Sensor Frame Readout / System
   Framework Sensor», `AIC` como «Image Processing Core» y afirmaba que el módulo «controla la
   lectura del sensor». Nada de eso está en los bytes: eliminado; §11 lo declara NO VERIFICADO.
2. **Sub-bloques**: el borrador daba 15 bloques con recuentos inconsistentes
   (`EFFECTMOVIEREC` 20, `SUPERSTABLEMOVIE` 28, `MOTIONSHOTVIDEO` 23, suma ≠ 117). Conteo
   verificado por reglas reproducibles: **8 bloques que suman 117** (37 + 25 + 23 + 12 + 9 + 6
   + 3 + 2).
3. **Mapa función→traza**: el borrador no lo tenía; ahora son **52 funciones** y **131 sitios**
   con guardas de coherencia en el script.
4. **Regla PIC**: el borrador no documentaba el emparejamiento; se fijó la regla estricta
   (fronteras Thumb, `ldr` inmediato del mismo registro, PC sin alinear) y se validó contra
   `SETPIN`/`GETPIN`.
5. **Ficheros fuente**: el borrador citaba `ScalarInfraPathCmdSetPath.cpp`,
   `ScalarInfraRecorder.cpp`, `ScalarInfraEncoder.cpp` y `ScalarInfraMovieRecorder.cpp` «según
   session19», sin comprobación. Esos cuatro literales **no** están entre los 24 que el clúster
   cita; la lista está ahora medida y con vaddr.
6. **Afirmación sobre la A7S**: el borrador decía que «la A7S no usa el prefijo `[SFRS]`» y
   hablaba de `MOTIONSHOTVIDEO` 24 cadenas y de `NLAP`. Falso: la A7S tiene **151** cadenas con
   el prefijo `[SFRS]`; el diferencial real es 117 comunes / 0 exclusivas A6000 / 34 exclusivas
   A7S (audio, path, pines).
7. **Recuento de la A6300 (212)**: se retira del entregable; no hay `av-cam.bin` de A6300 en
   `firmware/extracted/a6300-fw201/` y la cifra no era reproducible aquí.
8. **Claim de triplicación de literales**: el borrador abierto hablaba de tres regiones
   (`0x4368…`, `0x436a…`, `0x439a…`) citando los mismos `SystemCmdPin*.cpp`. Comprobado: en la
   imagen hay 573 literales `.cpp` y **ningún nombre se repite**; el claim se retira.

---

## Revisión del agente principal (21-10-2026)

**Verificado byte a byte (correcto):**

1. **Recuento y rango**: 117 cadenas `[SFRS]` de `0x43ce7661` a `0x43ceb8c4`; toda aparición abre
   racha imprimible (no haycadenas partidas) ✓.
2. **Sub-bloques**: SUPERSTABLEMOVIE 37, MOTIONSHOTVIDEO 25, EFFECTMOVIEREC 23, PINSEND 12,
   SET_PATH_STATUS 9, SA 6, RC_AIC_TRIGGER 3, MULTIPLEXTRIGGER 2 → suma 117 ✓.
3. **Emisión**: 131 puntos PIC `(ldr rX,[pc,#imm] ; add rX,pc)` y **52 funciones**, todas dentro de
   `0x439a0000`–`0x439c0000`; 0 cadenas sin referencia ✓. Es un módulo **compacto y localizado**,
   a diferencia de `[TRK]` (S111) o `[CAM_IMAGER]` (S115).
4. **Evidencia de código**: `SETPIN` con `cmp r1,#1` en `0x439aada4` y `line=%d`=58 en `0x439aadc0`;
   `GETPIN` con `cmp` en `0x439aae3c` y línea 56 (`movs r2,#0x38` en `0x439aae4c`); cola de
   `EXECUTE_PIN_SEND` en `0x439b1f4c`–`0x439b1f6c` (lee `[r4,#0x3f5]`, `#0x3f6`, `#0x3f4`, `#0x3ff`;
   escribe `[r4,#0x410]=1` y `[r4,#0x40c]`; traza `0x43ceb80d`).
5. **Diferencial A7S fw3.20**: 151 cadenas en la A7S, **117 comunes, 0 exclusivas de la A6000 y
   34 exclusivas de la A7S** → el módulo de la A6000 es un **subconjunto** del de la A7S.

**Acierto del subagente**: detectó y corrigió tres expectativas erróneas de sus propios tests
(nº de sitios `add`, el PC que se suma en el esquema PIC —el del `add`, no el del `ldr`— y el
formato `0x%08x` frente a `%08x` en la normalización), lo que demuestra que los tests se
ejecutaron de verdad contra los bytes.

**Observación**: el 40 % de las funciones (40 de 52) no imprimen `file=%s`, así que no se puede
asignarles fichero fuente; de las 24 clases `.cpp` citadas, solo 12 se pueden localizar en el
código.
