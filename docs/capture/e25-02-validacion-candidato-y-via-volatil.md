# E25-02 — Última oportunidad de la vía volátil y auditoría independiente de B1a (27-10-2026)

Sesión **100 % offline**: no se conectó la cámara, no se emitió ningún comando USB, no se escribió
RAM/NVRAM/NAND, no se flasheó, no se generó ningún FDAT/DAT y no se modificó ningún firmware original
in situ. No se creó ninguna herramienta que escriba en la cámara. El candidato se leyó de
`analysis/e25/` (binarios ignorados por Git) y **no se instala**.

Base: `d26f687c8fa3084596f1e562729c65006dd33923` (E25). Este informe **no repite** E24 ni E25: cierra
la vía volátil con la evidencia que faltaba y audita B1a con bytes y controles diferenciales propios.
Las pruebas nuevas son [`tests/test_e25_02_auditoria.py`](../../tests/test_e25_02_auditoria.py) (42) y el
generador [`scripts/e25_02/audit.py`](../../scripts/e25_02/audit.py) → [`analysis/e25-02/audit.json`](../../analysis/e25-02/audit.json).

## 0. Resultado en una frase

**A = NO**: no existe en el software oficial de BIONZ un emisor de `InitCom 0x16` con dirección y
longitud controladas; además, el propio handler de Darwin **no es una escritura selectiva de 1 B**
(copia 129 B con `length=0x81`), así que la vía volátil no solo carece de emisor: tampoco tendría una
escritura limpia. **B1a sigue siendo válido estáticamente** (2 bytes, salto al epílogo, L0 en los tres
arrancadores, tipo 0 intacto), pero **no es instalable** mientras E24-04 no demuestre recuperación.

## 1. Binarios y método

| Papel | Ruta local | SHA-256 | Tamaño |
|---|---|---|---|
| Darwin 3.21 oficial | `firmware/extracted/fw321/.../0640_darwin/darwin_core.bin` | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` | 157 276 B |
| Tipo 0 instalado (T024) | `analysis/darwin-patch/darwin_core_tipo0.bin` | `ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc` | 157 276 B |
| **Candidato B1a** | `analysis/e25/darwin_core_tipo0_sin_rearme.bin` | **`55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d`** | 157 276 B |

Base ROM `0x4200`; dirección ROM = offset de archivo + `0x4200`. Método: decodificación Capstone
propia (Thumb/M-class) y un verificador nuevo que **no importa** `scripts/e25/*` ni reutiliza sus JSON.
Los controles diferenciales comparan original ↔ tipo 0 ↔ candidato byte a byte y simulan la compuerta
para los 256 valores posibles de `[0x20000050]`.

## 2. Parte A — vía volátil

### 2.1 Lo que sí existe en Darwin

`InitCom` (`0x4bca`) despacha **solo** cuatro comandos: `0x11`, `0x12`, `0x13` y `0x16`
(bytes `0x4cd8–0x4cea`; `cmp r1,#0x11/#0x12/#0x13/#0x16`). El comando `0x16` (`0x4cec`) usa
`frame[1..4]` como dirección, `frame[5]` como longitud y el **bit 7 de la longitud** como indicador de
escritura:

```text
0x4cfc: ldrb.w r4, [sp, #0x19]     ; r4 = frame[5] (longitud + bit 7)
0x4d02: and r0, r4, #0x7f          ; solo para el chequeo previo
0x4d06: cmp r0, #0x78
0x4d0a: lsls r0, r4, #0x18
0x4d0c: bpl 0x4dd8                 ; bit7=0 -> LECTURA
0x4dc8: mov r2, r4                 ; <-- longitud COMPLETA, con bit 7
0x4dce: bl 0x255a6                 ; memcpy(dest=address, src=frame+6, n=r4)
```

**Corrección a E25 §3.3:** el modelo de `analysis/e25/route-a-volatile.json` asumía que
`longitud=0x81` escribía 1 B. No es así: el `memcpy` recibe `r4` completo (`0x81`), no
`r4 & 0x7f`. Una escritura de 1 B declarada copia **129 B** desde `frame+6` a
`0x20000050..0x200000d0`, invadiendo 128 B más de configuración. El chequeo `& 0x7f` solo sirve para
validar el rango; no se aplica a la copia. El mismo `mov r2,r4` aparece en A7S 3.20 (`0x4e00`) y
A6300 2.01 (`0x4e40`), así que no es una peculiaridad de la A6000. El control está en
`analysis/e25-02/audit.json` (`initcom_write_demo`: `declared_length=1`, `written_bytes=129`,
`end_exclusive=0x200000d1`) y en
`test_initcom_0x16_write_is_not_selective`.

La **lectura** sí es limpia: con bit 7 = 0 y longitud 1, `0x4dd8` hace `memset(frame+6,0x78)` y
`memcpy(dest=frame+6, src=address, n=1)`; la trama de respuesta devuelve el byte. Es el único
mecanismo de lectura/verificación del byte original que existe en el protocolo.

El comando `0x12` (`0x4d40`) escribe un bloque de `0x78 B` en `0x20000000 + n·0x78`; para llegar a
`+0x50` hay que enviar al menos `0x51 B`, y el bloque incluye `+0x31/+0x32` y `+0x40..+0x43`
(watchdog). No es selectivo. El comando `0x13` no se ha analizado; no cambia la conclusión.

### 2.2 Quién produce las tramas en BIONZ

| Candidato | Evidencia | Veredicto |
|---|---|---|
| **Actualizador oficial** (`nflasha1`) | `ud_darwin_init.elf` (`fb9e62b8…504c`): `0x8e1e movs r3,#0x11`, `0x8e24 strb r3,[r6]`, `0x8e26 subs r3,#0xd`, `0x8e28 strb r3,[r6,#1]` → solo `0x11/4`. `ud_darwin_firmup.elf` (`fc1df1b2…4881`): `0x8c68 movs r3,#0x14` + `strb` en `0x8c6a`; `0x8d32 movs r3,#0x15` + `strb` en `0x8d38`; `0x8e88 movs r3,#0x11` + `0x8e8e/0x8e94` → `0x11/4`, `0x14`, `0x15`. `ud_darwin_reboot.elf` (`1982ffd8…2c19`): `0x8d06 movs r3,#0x11`, `0x8d0c/0x8d10` → `0x11/3`. | **No hay `0x16` ni `0x12`/`0x13`**. `0x14/0x15` son del bootloader, no de `InitCom` (E24-02: el core solo despacha `0x11/0x12/0x13/0x16`). |
| **Servicio Senser / Micon** | `libsencore.so` (A6000, `analysis/camera-extract/usr/lib`): tabla `.data.rel.ro` `0x4f3b8` = `{MiconAccessFunc, 0x40}`; `MiconAccessFunc` (`0x14d38`) construye un `NoAction` con 0x80 B; `NoAction::DoExecute` (`0x127e8`) devuelve 0 copiando solo un byte al paquete, sin acceder a Darwin. | **Stub**. El comando Micon 0x40 no accede a Darwin; las cadenas `GET_DARWIN_PARAM_INFO` / `BOO_DWN_FW_ID_GET` / `CORE_DWN_FW_ID_GET` son nombres del protocolo Senser y no tienen en esta librería una ruta de lectura/escritura de RAM de Darwin. |
| **Capa CAIF/mss normal** | Mensaje mss `0x16` (210 B) y `0x0c` (22 B) de E24-05d; `0x0c` no lleva la compuerta (`pkt[0xc]` elige la lista de 49 estados); el handler `0x1b0b2` solo fija la **presencia** `[0x200002c0+idx]` y exige que `[0x20000050+idx]` ya sea distinto de 0. | **No es InitCom** y no escribe el tipo/compuerta. Es otra capa, con otros IDs y otro transporte. |
| **Escritor estático en Darwin** | Sin literal `0x20000050`, sin alias `0x22000a00`, sin `str [0x20000000+0x50]`; `0x1b090` es la única lectura de `+0x50`. | Solo podrían escribirlo `InitCom 0x12/0x16` o el arranque (`0x0–0x41ff`, sin binario). |

El plugin de comandos externos `libInfraScalarExtCmdPlugIn.so` solo expone `Backup_read_wrp` (NVRAM)
y utilidades de `extcmd`; no tiene cadenas ni rutas de Darwin/`InitCom`. No añade un productor.

El único emisor oficial de tramas `InitCom` es el actualizador, y **no envía `0x16`**. El servicio
normal no tiene un emisor; su comando Micon es un `NoAction`. La región de arranque de Darwin
(`0x0–0x41ff`) podría inicializar `0x20000050` desde flash, pero no hay binario y, en todo caso, no es
un emisor BIONZ accesible.

**Modificación temporal de BIONZ:** no hay un buffer de trama `0x16` que se pueda alterar antes de
enviarlo. El actualizador construye sus tramas en una pila local con comandos fijos
(`0x11/0x14/0x15`); el comando Micon 0x40 no llega a construir una trama. Sin un productor, una
modificación temporal de BIONZ no crea la vía: no hay bloque de configuración que reescribir.

### 2.3 Las siete preguntas

| | Pregunta | Respuesta | Evidencia / alcance |
|---|---|---|---|
| 1 | ¿Existe un emisor BIONZ que pueda emitir `0x16` con dirección y longitud controladas? | **NO** | Actualizador: solo `0x11/0x14/0x15`; Senser Micon: `NoAction`; CAIF/mss: otra capa. No hay código oficial que construya una trama `0x16`. |
| 2 | ¿Se ejecuta dentro de `Seton`? | **NO hay emisor que ejecutar** | `InitCom` solo existe en la tarea COM `0xece4`, creada en `Seton` (`0x7462`, literal `0xece5`); su único llamador es `0xecfe`. El actualizador corre en `nflasha1`, no en `Seton`. La captura normal no tiene `InitCom`. |
| 3 | ¿Puede conservarse el resto de la configuración, incluido el watchdog? | **NO** | `0x16` con `length=0x81` copia 129 B (no 1 B); `0x12` escribe 0x78 B e incluye `+0x31/+0x32/+0x40..+0x43` (WDG). Ninguna de las dos es selectiva. |
| 4 | ¿Es posible leer el byte original para una restauración exacta? | **Solo a nivel de protocolo** | `0x16` con bit7=0 y longitud 1 lee 1 B y lo devuelve; **no hay emisor** que envíe esa lectura y T022/T023 leen DRAM de BIONZ (`0x83f91e20..0x83f91f30`), no SRAM de Darwin (`0x2000xxxx`). |
| 5 | ¿Puede restaurarse sin reiniciar la cámara? | **NO demostrado** | No hay canal interactivo en `Seton`; el único emisor no envía `0x16`; la SRAM está siempre alimentada y un apagado normal no la borra. Una segunda escritura `0x16` en la misma ventana sería teóricamente posible, pero no hay quien la emita. |
| 6 | ¿Qué ocurre si se pierde comunicación a mitad de la modificación? | **Riesgo no controlado** | La trama se valida con CRC-16 antes del handler; una trama corrupta se rechaza y se reintenta. Pero la escritura `0x16` copia 129 B (puede clobberar 128 B de config) y, si se pierde la respuesta tras la copia, el emisor no tiene confirmación. La SRAM no se borra con un apagado normal. |
| 7 | ¿Existe una vía conocida para comprobar que Darwin recibió la escritura? | **Solo a nivel de protocolo** | `0x16` bit7=0 permite leer de vuelta; no hay emisor BIONZ ni implementación en el sistema normal. El actualizador solo comprueba CRC de enlace y `com_id`, no el contenido escrito. |

**Eslabón exacto que falta:** un emisor BIONZ de `0x16` con `dirección=0x20000050`, una longitud que
no clobbere el resto de la configuración (imposible con el handler actual: `length=0x81` copia 129 B)
y un disparo en `Seton`, más una lectura/verificación y una reversión. No existe. **A = NO.** No se
implementa ninguna escritura de RAM ni ningún script que la toque.

## 3. Parte B — auditoría independiente de B1a

### 3.1 Bytes, salto, pila y retorno

El candidato difiere del tipo 0 en **exactamente dos bytes**:

```text
rom 0x1fe6a / file 113770: 28 -> 0a
rom 0x1fe6b / file 113771: 46 -> e0
```

`0x0ae0` es un `B.N` incondicional; con `PC=0x1fe6e`, el destino calculado desde la codificación es
`0x1fe82` (no se toma de un JSON). La función queda:

```text
0x1fe66: push {r4,r5,r6,lr}
0x1fe68: movs r5,#0
0x1fe6a: b 0x1fe82
0x1fe82: mov r0,r5      ; r5 = 0
0x1fe84: pop {r4,r5,r6,pc}
```

- **Pila:** `push` y `pop` conservan `r4`, `r5`, `r6` y el retorno (`lr` → `pc`). No hay desbalance.
- **Registros:** el camino ejecutado solo escribe `r5` (a 0) y `r0` (desde `r5`); no toca `r4`, `r6`,
  `lr` ni `sp`.
- **Retorno:** `r0 = 0` siempre.
- **Sin lectura de `0x1b080`:** el `bl 0x1b080` sigue en el cuerpo (`0x1fe6c`), pero el salto lo deja
  fuera; tampoco se ejecuta el `tbb` (`0x1fe76`) ni la tabla (`0x1fe7a`).

El control original (sin parche) devuelve 0 para nibble alto 0 o ≥6, y el nibble alto (1–5) en otro
caso; el candidato devuelve 0 para los 256 valores. La diferencia es exactamente la compuerta forzada.

### 3.2 Los tres arrancadores y L0

Los tres arrancadores llaman al mismo thunk `0x1f5a2` (`b.w 0x1fe66`) y eligen el puntero de lista
según el retorno:

| Arrancador | Gate ≠ 0 | Gate = 0 |
|---|---|---|
| `0x1fee2` (load) | `0x29cdd` = `[0,2,3,6,9,10]` (L1) | `0x29cd8` = `[0,7,8,9,10]` (L0) |
| `0x1ff72` (captura 4) | `0x29ce3` = `[0,4,5,6,9,10]` (L2) | L0 |
| `0x1ffce` (captura 5/0x1f) | `0x29ce9` = `[0,1,4,5,6,9,10]` (L3) | L0 |

La lista L0 se lee de los bytes `0x29cd8..0x29cdc` = `00 07 08 09 0a`. La tabla exterior
`0x29d0c` da los manejadores `0x20100` (0), `0x2014c` (7), `0x200e2` (8), `0x200e6` (9) y `0x200fc`
(10). Los estados **2** (`0x20120`) y **4** (`0x20134`) son los únicos que arrancan la máquina
interior (`0x1f396`/`0x1f3b6`) y **no están en L0**. Las entradas interiores no aparecen en ningún
pool literal ni se construyen con `movw/movt`; sus únicos llamadores directos son `0x20126` y
`0x2013a`. No hay un arranque indirecto de la máquina interior.

### 3.3 Tipo 0

El candidato conserva el parche tipo 0 en `0x20c78..0x20c7f` = `09 e0 00 bf 00 bf 00 bf`:

```text
0x20c74: push {r4,lr}
0x20c76: movs r0,#0
0x20c78: b 0x20c8e        ; 0x20c74 devuelve 0 siempre
0x20c8e: pop {r4,pc}
```

Los cuatro escritores de P4D/P4E (`0x20c90`, `0x20cb2`, `0x20cd4`, `0x20d00`) consultan `0x20c74` y,
con 0, salen antes de `0x51c0`. El estado 7 de L0 sigue llamando a `0x20c90`, pero el tipo 0 impide la
escritura de P4D. El diff candidato ↔ tipo 0 es solo el salto de la compuerta; el tipo 0 no se toca.

### 3.4 Los doce consumidores

| Sitio | Función | Con retorno 0 | Cambio real |
|---|---|---|---|
| `0x1f4ba` | `0x1f4b6` (pulso de servicio) | `cmp #4` falla y retorna | **No ejecuta** el pulso `0x1f474` (motor) |
| `0x1f4de` | `0x1f4ce` (leva) | `cmp #0` → salta a `0x1f51c` | **Suprime** el error 6 `0x1f518`; no lee la leva |
| `0x1f576` | `0x1f572` (lectura de leva) | `cbz r0` → devuelve `r4=0` | No lee P25–P27; el llamador ve “posición 0” |
| `0x1f5a2` | thunk de los tres arrancadores | L0 en los tres | **Selecciona L0** |
| `0x1f5a8` | `0x1f5a6` (rearme directo) | `beq 0x1f5fe` | **No enciende** el motor; retorna |
| `0x1f896` | `0x1f88a` (interior) | `cmp 1/2` fallan → `0x1f8a6` | **No llama** a `0x20c90` |
| `0x1f908` | `0x1f8fc` (interior) | `cmp 1/2` fallan → `0x1f914` | **Sí llama** a `0x20c90`; el tipo 0 filtra P4D |
| `0x1fa40` | `0x1fa3a` (timeout interior) | `cmp #4` falla → `0x1faa8` | **Emite error 6** `0x1fab8` si se alcanza; L0 no la arranca |
| `0x1fe88/90/98` | `0x1fe86` (motor=2) | `cmp 4/1/2` fallan | **No ejecuta** `0x1fe32/0x51cc` |
| `0x201bc` | `0x201b0` (guarda `S+0x150`) | `cbz r0` → escribe 0 | Borra `S+0x150`; suprime el camino de error de `0x1b19e` |

Los doce sitios son exactamente los ya conocidos; no hay un decimotercero. Ninguno está en reset,
`InitCom` (`0x4bca–0x5000`), `Upd` (`0x8da8`) ni `Off` (`0x8900–0x8c90`).

**Riesgos de comportamiento:** `0x1f4ce` ya no valida la posición de la leva; `0x1f572` devuelve 0 sin
leerla; `0x1fa3a` emite error 6 si alguna vía alcanza la máquina interior. La primera y la segunda son
consecuencias buscadas (no hay rearme que validar); la tercera queda fuera de L0, pero es el punto que
debe vigilar la prueba física.

### 3.5 Cancelación real, distinta de COM/InitCom

E25 §6.2 llamó “Cancelación” a `COM 0xed18 / 0x4ed8`. **Es un error de categoría:** `0x4ed8` es la
bandera de parada de `InitCom` (`[0x20002a08+7]=0`), y su único llamador es `0xed1a`, dentro de
`0xed18`; `0xed18` solo se llama desde `0x750c`, el epílogo de `Seton main` (`0x747a–0x755c`). No es
una cancelación de captura.

La cancelación/aborto real que sí está identificada es el **timeout de fase** del estado `0x17`
(`0x189d4` → `0x16e26` → `0x16dc0`): `0x16dc0` llama a `0x16558(2,0x30,...)` (bytes verificados), que
activa la recuperación de error y la operación 5. La operación 5 **no consulta la compuerta** y
escribe `P40/P41=3`; su efecto es un patrón de apagado (XOR=0), no una orden de movimiento (§3.6). El
parche no la toca. No se ha identificado una cancelación de usuario que llame directamente a las
primitivas del motor; si existiera, tendría que pasar por uno de los llamadores enumerados en §3.7,
todos gated salvo la operación 5. **Cobertura real: parcial**; el único hueco es la semántica de
usuario de la cancelación, no una vía nueva al motor.

### 3.6 Operación 5, P40/P41 y efecto eléctrico

`0x1f600` llama a `0x1fcb8`; `0x1fcb8` llama a `0x1feb6`, espera `0x7a120` y llama a `0x1fe32`
(apagado). `0x1feb6` hace:

```text
0x1feb6: push {r4,lr}
0x1feb8: bl 0x1fe32             ; P40=P41=0
0x1febc: movs r1,#3
0x1fec2: movw r2,#0xfffc
0x1fec6: movs r0,#4
0x1fec8: b.w 0x51cc             ; PDOR4 = (PDOR4 & 0xfffc) | 3
```

`0x51cc` escribe `PDOR4` (`0x40033410`) con máscara `0xfffc`; los bits 0/1 son P40/P41. El manual de
servicio (hojas 6-11/6-17) muestra `IC6800` = `TC7SH86FU` (XOR), con `IN_A=SC_M_2` (P41) e
`IN_B=SC_M_1` (P40), y `OUT_Y` → `Q6800` → `Q6801` → `CHARGE MOTOR`:

| Valor | P40 | P41 | XOR | Interpretación |
|---|---|---|---|---|
| 0 (`0x1fe32`) | 0 | 0 | 0 | apagado |
| 1 (`0x1fe50`) | 1 | 0 | 1 | movimiento |
| 2 (`0x1fe86`) | 0 | 1 | 1 | movimiento |
| 3 (`0x1feb6`) | 1 | 1 | 0 | **apagado**, no orden de movimiento |

**Corrección a E25 §6.3:** el valor 3 no es un “freno” demostrado; es el mismo nivel de salida que 0
en la XOR. Que el motor frene dinámicamente o quede en rueda libre depende del entorno de Q6801 y
**no está medido**. Lo que sí se puede afirmar es que 3 no excita Q6801 y no es una orden de
movimiento. La operación 5 es, por tanto, un **apagado** durante `0x7a120` cuentas y no una excepción
de movimiento; el riesgo físico residual es que el motor ya esté girando y se corte (coast/brake no
medido), no que se arranque.

### 3.7 Llamadas indirectas relevantes

Las funciones críticas **no aparecen en ningún pool literal** ni se construyen con `movw/movt`:
`0x1fe66`, `0x1fe50`, `0x1fe86`, `0x1feb6`, `0x1f5a6`, `0x1fcb8`, `0x1f396`, `0x1f3b6`. Por tanto, no
hay una llamada indirecta en el core que pueda saltar directamente a la compuerta, a las primitivas
del motor o a las entradas de la máquina interior. Los únicos llamadores son los directos enumerados
en §3.4 y §3.7; la tabla exterior `0x29d0c` despacha por **id de estado**, y L0 no contiene los ids
2/4. Las llamadas indirectas que sí quedan abiertas en los cierres de E25 son de la máquina de
estados y de utilidades, no de estas direcciones; no cambian el veredicto.

### 3.8 Llamadores del motor y cobertura

| Primitiva | Llamadores | Clasificación |
|---|---|---|
| `0x1fe50` (P40/P41=1) | `0x1f47c`, `0x1f5b8`, `0x1f6e0`, `0x1f730` | pulso gated (`0x1f4b6`), rearme directo gated, máquina interior |
| `0x1fe86` (P40/P41=2) | `0x1f482`, `0x1f65c`, `0x1fc10` | pulso gated, máquina interior, máquina de 6 estados |
| `0x1feb6` (P40/P41=3) | `0x1f49c`, `0x1f686`, `0x1f7be`, `0x1fbdc`, `0x1fc34`, `0x1fcba` | pulso gated, máquina interior, máquina de 6 estados, **operación 5** |

Todas las primitivas están detrás de la compuerta, de la máquina interior (solo arrancada en los
estados 2/4) o de la operación 5. La operación 5 es la única excepción y es un apagado. No hay un
camino de captura/cancelación que arranque el motor fuera de esta tabla.

### 3.9 P4B/P4C

- **P4C** (`0x230`): `0x1ecec` escribe 1/0 vía `0x51c0`; llamadores `0x16e6c`, `0x16e7e`, `0x17096`.
  Sigue fijándose a 1 en cada toma y borrándose en `0x16e68`. El parche no toca la función.
- **P4B** (`0x22c`): `0xd176`/`0xd1e8` escriben 1/0 vía `0x51c0` según la máscara de ocupación
  (`0x800`, bit 11); `0xd276`/`0x1ecdc` lo leen vía `0x51c6`. Sigue activo durante la captura. El
  parche no toca estas funciones.
- **Consumidor físico:** no localizado (IC6000). No se puede afirmar que su actividad no mueva nada.
  Es un **riesgo residual**, no una prueba de movimiento. La prueba física de E25-01 debe incluirlo.

## 4. Parte C — decisión técnica

| Dimensión | Resultado | Evidencia |
|---|---|---|
| **RAM volátil (`InitCom 0x16`)** | **NO DEMOSTRADA** | No hay emisor BIONZ; el servicio Micon es `NoAction`; `0x16` no es selectivo (129 B); solo `Seton`; sin lectura/verificación accesible; SRAM no se borra con apagado. |
| **Darwin B1a** | **VÁLIDO ESTÁTICAMENTE** | 2 bytes, salto al epílogo, pila/registros/retorno conservados, sin `0x1b080`, L0 en los tres arrancadores, tipo 0 intacto, 12 consumidores cubiertos. |
| **Captura normal sin motor** | **SÍ estático para el motor y P4D/P4E; NO para P4B/P4C ni para la captura completa** | Ninguna primitiva `0x1fe50/0x1fe86/0x1feb6` en las rutas de captura/rearme con gate 0+tipo 0; P4B/P4C siguen; BIONZ/M1 no demostrado. |
| **Cancelación y errores** | **Cobertura parcial** | La “cancelación” de E25 era `InitCom`, no captura; el abort real es el timeout 0x17 → op5 (apagado, sin compuerta); `0x1989c` sigue vivo; `0x1f4ce` suprime el error de leva; no hay cancelación de usuario trazada. |
| **Recuperación del MCU** | **NO DEMOSTRADA** | E24-04 sigue abierto: sin vía independiente de la aplicación Darwin, sin caso de restauración de un Darwin defectuoso. |
| **Instalación** | **BLOQUEADA** | Sin recuperación demostrada no se autoriza el flasheo; el candidato es offline y no se genera FDAT 3.24/3.25. |

### 4.1 Distinción obligatoria

| Nivel | Estado | Qué significa |
|---|---|---|
| **M0 normal estático** | **SÍ** | Con B1a, las rutas normales de captura/rearme no alcanzan las primitivas del motor; el tipo 0 filtra P4D/P4E; L0 no arranca la máquina interior. |
| **M0 físico** | **NO MEDIDO** | No se midió corriente del motor, P40/P41, P4D/P4E, P4B/P4C ni P29; no se puede distinguir “sin orden” de “sin movimiento”. |
| **M1 captura completa** | **NO DEMOSTRADO** | Falta el fin de L0 y la aceptación por BIONZ; el orden estricto de mensajes mss y el fin electrónico del IMX210 en foto completa siguen abiertos. |
| **Recuperabilidad** | **NO DEMOSTRADA** | E24-04; el candidato no es instalable y no hay rollback independiente. |

**Watchdog:** los 2 bytes no tocan `+0x31/+0x32/+0x40..+0x43`; el riesgo no es el parche, sino la
duración de L0 (`0x8ca0 + 0x5dc0`) y la planificación del alimentador. No medido; E24-05b sigue
abierto.

### 4.2 Qué cambiaría el veredicto

- **A** solo cambiaría con un emisor BIONZ oficial de `0x16` con dirección/longitud controladas y un
  disparo en `Seton`; además, el handler tendría que corregir el `mov r2,r4` para que una longitud de
  1 B no copie 129 B. No existe ninguno de los dos.
- **B1a** solo se contradiría con una llamada indirecta que alcanzara el motor fuera de la tabla de
  §3.8, o con una prueba física que mostrara movimiento con el candidato. La primera no tiene
  punteros absolutos; la segunda es E25-01 (bloqueada).
- **M1** exige la prueba física instrumentada de E25-01 y el cierre BIONZ de E25-03.
- **Recuperación** exige E24-04 resuelto o aceptación expresa y documentada del riesgo.

## 5. Correcciones a E25

1. **`InitCom 0x16` no es una escritura selectiva de 1 B.** El `memcpy` usa `r4` completo; con
   `length=0x81` copia 129 B (`0x20000050..0x200000d0`). El modelo `route-a-volatile.json` es
   incorrecto en este punto (`bytes_changed: 1`).
2. **La “cancelación” de E25 §6.2 no es una cancelación de captura.** `0x4ed8` es la bandera de parada
   de `InitCom`; su único camino es `Seton main` → `0xed18`. La cancelación real identificada es el
   timeout 0x17 → `0x16558(2,0x30)` → operación 5.
3. **El “freno” de la operación 5 no está demostrado.** El valor 3 da XOR=0, el mismo nivel que 0;
   es un apagado, no una orden de movimiento. El efecto coast/brake no se midió.
4. **P4B no lo escriben `0xd116`/`0xd18e` directamente:** esos actualizan las máscaras de ocupación;
   los escritores de P4B son `0xd176`/`0xd1e8` (`0x51c0(0x22c,...)`). La conclusión (P4B sigue
   activo) no cambia.

## 6. Pruebas y reproducción

```bash
# Auditoría independiente (genera analysis/e25-02/audit.json)
python scripts/e25_02/audit.py --write

# 42 pruebas nuevas (bytes, salto, pila, L0, tipo 0, consumidores, op5, P4B/P4C, InitCom)
python -m pytest -q tests/test_e25_02_auditoria.py

# Regresión E25 (no se tocó el parche)
python -m pytest -q tests/test_e25_desactivacion.py

# Regresión E24/GPIO/Darwin (misma que E25)
python -m pytest -q tests/test_e24_*.py tests/test_darwin.py tests/test_fm3_gpio_literals.py \
  tests/test_s135_elec_shutter.py tests/test_s172_elec_shutter_a6300.py \
  tests/test_s401_a7s_caif.py tests/test_s402_static_closure.py
```

Resultado de esta sesión con `.venv` activado: **42/42** E25-02, **54/54** E25, **255/255 + 3
subtests** E24/GPIO/Darwin y **79/79** `tests/knowledge`. El fallo de entorno de E25
(`/usr/bin/python` sin `Cryptodome`) no se reproduce con el entorno activado; no es una regresión
de este cambio.

Para reproducir la evidencia del actualizador (no versionada, firmware ignorado):

```bash
mcopy -i analysis/camera-dumps/nand-20261020/dev_nflasha1.bin ::/boot/initrd.img /tmp/initrd.img
7z x -o/tmp/ird /tmp/initrd.img
llvm-objdump -d --triple=thumbv7-linux-gnueabi /tmp/ird/usr/bin/ud_darwin_init.elf
llvm-objdump -d --triple=thumbv7-linux-gnueabi /tmp/ird/usr/bin/ud_darwin_firmup.elf
llvm-objdump -d --triple=thumbv7-linux-gnueabi /tmp/ird/usr/bin/ud_darwin_reboot.elf
```

SHA-256 de los ELF: `ud_darwin_init.elf` = `fb9e62b80dda2a8804131f1b543545de9a7b2eca085a5a4361dfea3d0e05504c`;
`ud_darwin_firmup.elf` = `fc1df1b27c191b10971637a97f24e62ea59bccaace7251708aae1e17c9594881`;
`ud_darwin_reboot.elf` = `1982ffd8acef969f462ac29ec44e031ee92c88597936e70d5a0ee25da8192c19`.

## 7. Límites de la evidencia

- Todo es estático o modelo: no se ejecutó firmware ni se midió la cámara. “Sin primitivas” significa
  que el cierre de llamadas/ramas no las alcanza, no que el hardware esté quieto.
- El byte `[0x20000050]` no se ha leído en vivo; su valor real y el de `[0x200002c0]` siguen sin
  medir. El arranque de Darwin (`0x0–0x41ff`) no tiene binario; no se puede demostrar si inicializa
  el byte desde flash.
- La búsqueda de emisores BIONZ cubre los binarios oficiales disponibles (actualizador, `libsencore`,
  `av-cam`, capa CAIF/mss); no cubre código de fábrica no distribuido ni un firmware futuro. El
  kernel normal (`vmlinux.bin`) y un posible `sio.ko` no se han desensamblado; en la cámara ningún
  proceso tenía abierto `/dev/sio*` en modo normal (T013/T014), lo que limita pero no demuestra la
  ausencia de un emisor en el kernel.
- Las llamadas indirectas se descartan por ausencia de punteros literales/inmediatos a las funciones
  críticas; no es un análisis de alias completo.
- La operación 5 se modela por la XOR del circuito; el efecto físico (coast/brake) no se midió.
- P4B/P4C no tienen consumidor localizado; su efecto mecánico es un riesgo residual.
- **Un binario parcheado que pasa las pruebas no es un binario seguro de instalar.** E24-04 sigue
  siendo el bloqueante.
