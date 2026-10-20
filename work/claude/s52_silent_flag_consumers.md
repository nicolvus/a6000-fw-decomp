# S52 A1/A2 — `captura+0x748` y clase de obturación: productores y consumidores (A7S 3.20 vs A6000 3.21)

19-10-2026, Agente A (Claude). Solo estático. Binarios y hashes: los de `analysis/s52-hashes.initial.sha256`
(A7S `b857d338…`, A6000 `b60c845c…`, base `0x43541000`, Thumb). Desensamblado lineal LLVM completo en
`work/claude/s52/dis/{a7s,a6000}.dis`; REA propia (`work/claude/run/rea.sock`, cerrada con `--shutdown`) en
`s52/rea{1,2,3}.jsonl`. Todo lo marcado VERIFICADO lo comprueba `tests/test_s52_curtain_facts.py` (14/14 OK).

## 1. Respuesta P1 — qué es `captura+0x748`

**VERIFICADO:** `captura+0x748` (u32) **no es un campo nuevo de la A7S**. Es el campo que en la A6000 está en
`captura+0x740`: la estructura de captura A7S está desplazada **+8 bytes** a partir de ≈`+0x73b`
(A6000 `+0x73b/+0x740/+0x744/+0x748/+0x74f` = A7S `+0x743/+0x748/+0x74c/+0x750/+0x757`). Prueba: secuencias idénticas
instrucción a instrucción, p. ej. A7S `0x43b1d99a..9a2` (`ldr [r4,#0x748]; cbnz; ldrb [r4,#0x743]`) = A6000
`0x43b1e7b0..7b6` (`#0x740`, `#0x73b`); A7S `0x438b74a4 str [r4,#0x750]` = A6000 `0x438c7fc6 str [r5,#0x748]`.

| | A7S (`+0x748`) | A6000 (`+0x740`) |
|---|---|---|
| Escritores directos (STR.W imm 0x748/0x740, todo el binario) | **solo** `0x43813ea2` (`=1` si tipo Silent==2) | ninguno en captura (solo `0x4373662a/0x43736738`, otra estructura) |
| Escritores por puntero ajustado (`add rX,rY,#K` + `[rX,#o]`, K+o=objetivo; `s52/adjscan.py`) | ninguno | ninguno |
| Lectores en código de captura | 16 (lista abajo) | 13 |
| Origen del valor normal | NO VERIFICADO (no se halló reset; constructor/memset no localizado) | íd.; sin escritor ⇒ previsiblemente constante (INFERENCIA) |

Consecuencia (**INFERENCIA fuerte**): el firmware común ya contenía una bandera de captura con lectores `==1` / `==0`
(código latente en la A6000, sin productor) y la A7S la activa para Silent. Su efecto no es «informativo»: cambia
qué esperas/eventos CAIF se ejecutan y temporizadores (abajo). **No** está copiada al secuenciador ni al paquete CAIF:
el paquete lee el tipo Silent `captura+0x78c` (vía `r6=captura+0x20`, `+0x76c`), no `+0x748`.

Escritor (A7S `0x43813e94..ea2`, VERIFICADO):
```
43813e94 bl 0x4379ec04            ; conversor ajuste->tipo {0,2}
43813e98 cmp r0,#2 ; 43813e9a str.w r0,[r4,#0x78c] ; 43813e9e bne 0x43813ea6
43813ea0 movs r3,#1 ; 43813ea2 str.w r3,[r4,#0x748]   ; solo pone 1; no lo borra
```

## 2. Lectores de `+0x748` (A7S) y equivalencia A6000

Método: alineación por **ID de traza** de captura (`mov r1,#ID; bl 0x43ae826e` A7S / `bl 0x43ae769a` A6000;
`s52/traceid.py`, 207 de 220 IDs emparejados) + difflib (`s52/fdiff.py`) + lectura de instrucciones. «Nuevo» = la
condición sobre +0x748 no existe en la función homóloga A6000.

| A7S | Función (ID traza) | Condición y efecto | A6000 | Estado |
|---|---|---|---|---|
| `0x438b1cba` | etapa `0xc8` (caso 10 de la máquina `FUN_43b19e56`, REA) | `if 748==0: 0x438be5f8(cap)` = **esperar respuesta CAIF 3** | `0x438c28ac` llama `0x438d08e8` **incondicional** | **NUEVO** VERIFICADO |
| `0x43b1c92e` | etapa `0xc9` (`0x43b1c920`, referida desde 9 filas de tabla de etapas `0x43b1be2c…0x43b1c52e`, REA) | `if 748==1: 0x438be5f8(cap)` (espera CAIF 3) y luego `0x438be6e8` (envía CAIF 5) | `0x43b1d962` solo `0x438d0a2c` (envía CAIF 5) | **NUEVO** VERIFICADO |
| `0x438b726c` | ReadExecuteBase `0x438b6d70` (=A6000 `0x438c7800`) | `if param[8]!=0 && 748==0 && !param[5]: 0x438be76c(cap)` = **esperar bandera 0x800000** del grupo 0x13 | `0x438c7d56`: solo `!param[5]` → `0x438d0acc` | **NUEVO** VERIFICADO (REA pseudocódigo coincide) |
| `0x438b7ec2` | caso 6 (`0xfd`) | evento `0x102` solo si `748==0 && cap+0x4bb0`; si Silent `0x100` | `0x438c89c0`: `0x102` si `cap+0x4b9c` | **NUEVO** VERIFICADO |
| `0x438b8054` | caso 6, cola (`0x108`) | `if 748==0 { if +743: post(2,1); 0x43b1d5de(cap) }` | `0x438c8b4e`: **incondicional** (`+73b`, `0x43b1e474`) | **NUEVO** VERIFICADO |
| `0x438b75a4` | `0x1cb` | `if 748==1: post(2)`; después `0x43b1d5de` | `0x438c8104` lee `+0x740` | compartido (VERIFICADO lectura; detalle no comparado) |
| `0x438b76fc` | `0x1ca` | resultado de ReadExecuteBase combinado con `748==1` | `0x438c825e` (`+0x740`) | compartido |
| `0x438b77e4`, `0x438b786c` | SetExposure caller `0x438b7728` (ID `0xe`) | tiempos `+0x570/+0x574`; `if 748==0: +0x64c=0` | `0x438c8344`, `0x438c83be` | compartido |
| `0x438b69f4/6a6e/6a94` | `0xde` | cálculo de temporizador (×1000, ×31) y `+0x730` | `0x438c74da/7544/756e` | compartido |
| `0x438b6ffc` | ReadExecuteBase | `748==1 && param[5]` ⇒ duplica tiempo | `0x438c7af2` | compartido |
| `0x438b7fce` | `0x108` | `748==1` ⇒ temporizador 0 con `0xffffffff` y callback `0x43b1d5b1`; si no, tiempo calculado y callback `0x43b1d649` (pone bandera 0x100000) | `0x438c8ac8` (`+0x740`, misma forma) | compartido |
| `0x43b1d99a`, `0x43b1d9be` | `0x14` | parámetros de la petición ReadExecute | `0x43b1e7b0/7d4` | compartido |
| `0x43549636` | — | otra estructura | — | no captura |

A6000 tiene además un lector latente sin homólogo A7S: `0x438c240e` (ID `0x109`: `if 740==1 && 0x436e8328()==1 →
0x438d08c8`); en A7S la función `0x109` (`0x43b1c858`) ya no lo contiene. VERIFICADO.

## 3. A2 — clase de obturación: almacenamiento y TODOS los consumidores localizados (A7S)

Política `0x438649bc` (llamada solo desde el constructor de paquete `0x43862e24` en `0x438630a8`, a su vez llamado
desde `0x4382822c`; REA). Bloque global **G = `0x43f06bc8`** (resuelto por literal PIC; Codex citó `0x43f06d8a`: no
coincide con los bytes).

| Salida | Escritor | Valor en Silent (tipo 2, `banco+0x404==2`, `banco+0x4c4&0xe0==0`) |
|---|---|---|
| `G+0x5c` clase | `0x43864a48 str r1,[r2,#0x5c]` (`r1=0` de `ands r1,r2,#0x80`) | **0** |
| `G+0x60` | `0x43864ad0..ade` → `0x43864b00 strb r2,[r3,#0x60]` con `r2=0` | **0** (EFCS=1 daría 1) |
| `G+0x61` | `0x43864b28` | depende de `[D]+0xf9`, clase 3 y umbral; con clase 0 → 0 |
| Anulaciones | diagnóstico `D=0x43ea4d68` `+0x7e` (1..8 → clase 0..7) y primer arg `+0x36/+0x37` | pueden sobrescribir; no vinculadas a Silent |
| Copias de salida | clase → `*(0x43e1f048)+0x9ac` y byte `0x43fab15b`; EFCS → `0x43fab0db`; `G+0x60` → `0x43fab0a7`; `G+0x61` → `0x43fab155` | — |

Consumidores (REA xrefs + escáner PIC; cobertura parcial, REA no ve todo Thumb):

| Consumidor | Qué hace con la clase | Clase 0 vs 1/3 |
|---|---|---|
| Getter `0x43864c74` → único llamador `0x43861bfc` | copia a **`0x43f04c8c`** (y `G+0x60/61` a `0x43faba61/5f`) | — |
| `0x438627d2` | `if clase==1 || (clase==3 && *0x43faba61==1) && …: 0x43aed4ba(x162,x166,1)` → `0x437c3114(0xa..0x12)` = mensaje tipo 3/0x22 por cola; segunda llamada solo si tipo≠2 | **Clase 0 omite** este envío (y Silent omite también el segundo). Receptor del mensaje: NO VERIFICADO |
| `0x43863146` (constructor CAIF) | byte **+1** del paquete del evento 1: clase 1 → 0/0x40; **clase 0 y 3 → 2/0x42** | Clase 0 **se trata igual que 3**; A6000 `0x4384137c` daría 0 con clase 0 (cambio A7S VERIFICADO) |
| `0x43863478` | registro de fotograma `+0x69` (= A6000 `+0x6d`) | — |
| `0x43862158` (= A6000 `0x4383fd6c`) | copia registro `+0x60..+0x6b` a `*param`; clase → `param+9` = `captura+0x651`; `0x43b1c8e2` la guarda también en `captura+0x4cc` | — |
| `0x438b7728` → `0x436f2938(img, captura+0x648)` | SetExposure; IMX235 `0x436f4168` selecciona por `param+9` (ShutMode 0 ≠ 1/3; tabla en `a7s_shutter_modes_comparison.md`) | bits distintos al sensor |
| `0x438b775c` | fuerza `captura+0x651=0` si `0x439fb708()∈{2,3}` (igual que A6000 `0x438c82bc`) | ShutMode 0 también existe fuera de Silent |
| `0x43864ddc`, exportador `0x43864e0a..e16` | estado `obj+0xef/0xf0/0xf1` | registro de estado |

Con esto se cierra la INFERENCIA previa «clase→`param+9`» (H52-3 de Codex): **VERIFICADO** en A7S por la copiadora
`0x43862158` y su llamador `0x43b1c8e2` + SetExposure `0x438b77ac`.

## Límites

- No se recuperó quién inicializa `captura+0x748` (constructor/memset/copias de estructura completas): el valor 0 en
  modo normal es INFERENCIA. La A6000 no lo escribe nunca por offset directo.
- Índices PIC y por puntero ajustado heurísticos; REA no reconoce varias funciones Thumb (p. ej. `0x43b1c920`,
  `0x43b1d648` sin llamadores). Ausencia de lectores ≠ inexistencia.
- `0x43eaaac0` (tipo Silent copiado por VD_Pre, ver `s52_vd_sequence_comparison.md`): sin lectores hallados.
