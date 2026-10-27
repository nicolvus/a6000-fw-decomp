# E25 — Desactivación del accionamiento normal del obturador mecánico (27-10-2026)

Sesión **100 % offline**: no se conectó la cámara, no se emitió ningún comando USB, no se escribió
RAM/NVRAM/NAND, no se flasheó, no se generó ningún FDAT/DAT y no se modificó ningún firmware original
in situ. El candidato se produce en `analysis/e25/` (binarios ignorados por Git) y **no se instala**.

Base: `6a7739f195f790ae125ecdad4c2d53309941209f` (más los commits documentales de E24-05e/h-5).
Binarios de trabajo:

| Papel | Ruta local | SHA-256 | Tamaño |
|---|---|---|---|
| Darwin 3.21 oficial | `firmware/extracted/fw321/.../0640_darwin/darwin_core.bin` | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` | 157 276 B |
| Tipo 0 instalado (T024, empaquetado 3.22) | `analysis/darwin-patch/darwin_core_tipo0.bin` | `ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc` | 157 276 B |
| **Candidato E25 (tipo 0 + compuerta 0)** | `analysis/e25/darwin_core_tipo0_sin_rearme.bin` (ignorado) | **`55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d`** | 157 276 B |
| Control original + compuerta 0 (no M0) | `analysis/e25/darwin_core_original_sin_rearme.bin` (ignorado) | `f0e7ebeed1a48d74d6a6366fea9c2122a6c650eb6434a4d7d90f7d81e4c24868` | 157 276 B |

Base ROM `0x4200`; dirección ROM = offset de archivo + `0x4200`. La cadena de versión `VER0.78`
está en `0x25b3c` en las dos entradas aceptadas.

## 1. Veredictos obligatorios

| | Pregunta | Respuesta | Alcance exacto |
|---|---|---|---|
| **A** | ¿Existe una vía volátil **demostrada** para seleccionar L0? | **NO** | El lado Darwin tiene una escritura selectiva posible por `InitCom 0x16` (1 B en `0x20000050`, modelo en §3.3), pero **falta el emisor BIONZ** y el disparo fuera de `Seton`; `0x12` exige bloque de `0x78 B`; la SRAM de Darwin no es alcanzable por T022/T023. Detalle y eslabón exacto en §3. |
| **B** | ¿Se implementó un candidato offline que seleccione L0? | **SÍ** | `0x1fe6a: 28 46 → 0a e0` sobre el tipo 0: `0x1fe66` retorna 0 sin leer la compuerta; los tres arrancadores eligen `0x29cd8 = [0,7,8,9,10]`. 2 bytes, SHA `55a366a5…`. §4–§5. |
| **C** | ¿Se conserva el tipo 0 de las bobinas? | **SÍ** | `0x20c78..0x20c7f = 09 e0 00 bf 00 bf 00 bf` intacto; `0x20c74` sigue devolviendo 0 (`b 0x20c8e`). El candidato se genera **desde** el tipo 0; el control desde el original no es M0 (§5.2). |
| **D** | ¿El candidato evita las activaciones normales de P40/P41 durante captura y rearme? | **SÍ (estático)** | Con compuerta 0 los cierres de `load`, `0x19998`, `0x199b8`, `0x199d8`, los tres estados 4/5/0x1f y la tarea de captura/ráfaga no alcanzan `0x1fe50/0x1fe86/0x1feb6`. `0x1f5a6` retorna en `0x1f5ae`. No es una medida física. §6. |
| **E** | ¿Se evitan activaciones de P4D/P4E en las rutas auditadas? | **SÍ (estático, con tipo 0)** | Los cuatro escritores (`0x20c90/0x20cb2/0x20cd4/0x20d00`) consultan `0x20c74` y no llegan a `0x51c0` con tipo 0. P4C y P4B **siguen activos**. §6.4. |
| **F** | ¿Quedan caminos excepcionales que podrían mover el mecanismo? | **SÍ** | Operación 5: `0x1f600 → 0x1fcb8 → 0x1feb6` sin compuerta (P40/P41=3, XOR=0; no es orden de movimiento, efecto físico no medido). P4B/P4C activos y su consumidor físico no está demostrado. `0x1989c` (error 6 de ADC) puede encolar la operación 5. §6.3–§6.5. |
| **G** | ¿El candidato es reversible byte a byte y pasa las regresiones? | **SÍ (offline)** | `restore` reproduce el SHA de entrada (`ca41b46c…`); 54 pruebas E25 + 304 pruebas E24/GPIO/Darwin; 1 fallo preexistente de entorno en E24-03 (falta `Cryptodome` en `/usr/bin/python`, no es regresión). §7. |
| **H** | ¿Se ha demostrado una recuperación independiente si un Darwin modificado no arranca? | **NO** | E24-04 sigue abierto: no hay vía independiente de la aplicación Darwin demostrada, ni caso de restauración de un Darwin defectuoso. El candidato **no es instalable**. §8. |
| **I** | ¿Existe un candidato técnicamente concreto para alcanzar M0 sin ejecutar pruebas físicas? | **SÍ** | Tipo 0 + compuerta 0, 2 bytes, manifiesto y reversión; M0 queda demostrado solo para captura/rearme normal. M0 en escenarios de error sigue **pendiente** (operación 5). §8. |
| **J** | Condiciones exactas para autorizar una prueba física controlada | — | §9: recuperación demostrada o aceptación expresa del riesgo, FDAT > instalada, instrumentación de P40/P41/P4D/P4E/P4B/P4C/P29, criterios de captura y rollback. |

## 2. Resultado en una frase

Seleccionada **B1a**: sobre el Darwin tipo 0 ya instalado, dos bytes en `0x1fe6a` convierten
`0x1fe66` en un retorno constante 0. Esa función es la **única** compuerta que consultan los tres
arrancadores de la máquina exterior, `0x1f5a6` (rearme directo) y los demás consumidores del motor.
Con 0, los tres arrancadores eligen L0 `[0,7,8,9,10]`; la máquina interior de 27 estados no se
arranca desde L0; el estado 7 sigue llamando a `0x20c90` (P4D=1) pero el tipo 0 lo filtra; el estado 9
libera la ocupación y el 10 termina. El freno de la operación 5 no se toca y queda como excepción
documentada. No se afirma que BIONZ acepte el fin de L0 ni que el mecanismo esté físicamente inmóvil:
eso exige la prueba de §9.

## 3. Implementación A — vía volátil (NO demostrada)

### 3.1 La compuerta y su escritor

- `0x1fe66` lee `[0x20000050 + canal]` a través de `0x1b080`; el nibble alto es la compuerta (0–5;
  ≥6 → 0) y el nibble bajo (bits 0–2) es el tipo de bobina que filtra `0x20c74`. La lectura se hace
  **en cada llamada** (sin caché): `0x1b080` comprueba `[0x200002c0+canal]` y hace
  `ldrb.w r0,[r0,#0x50]`.
- **No hay escritor estático** de `0x20000050` en `darwin_core`: no existe el literal
  `0x20000050` ni el alias de bit `0x22000a00`, y el barrido de `ldr rX,=0x20000000` seguido de
  `str [rX,#0x50]` no encuentra ninguna instrucción real (los únicos hits aparentes son datos/cadenas
  o periféricos `0x4276xxxx`). Evidencia: `analysis/e25/route-a-volatile.json`,
  `tests/test_e25_desactivacion.py::test_no_static_writer_of_the_gate`.
- `0x43841070` construye el paquete BIONZ `0x0c` de 22 B en `carga+0x40`; **la compuerta no es un
  campo de ese paquete**. `pkt[0xc]` elige la lista de la máquina de 49 estados (`0x1961c`), no
  `0x1fe66`.

### 3.2 `InitCom 0x12` (bloque de 0x78 B)

`InitCom 0x4bca` solo existe en la tarea COM `0xece4`, creada en `Seton`. El comando `0x12`
(`0x4d40`) exige que el destino sea `0x20000000 + n·0x78` (resto 0) y copia el payload con
`0x255a6`. Para tocar `+0x50` hay que enviar desde la base del bloque 0 y **al menos 0x51 B**; el
bloque incluye `+0x31/+0x32` y `+0x40..+0x43` (watchdog), `+0x10` (log) y el resto de campos. El
modelo de `analysis/e25/route-a-volatile.json` muestra que un payload de `0x78 B` con solo `+0x50`
a 0 cambia 1 byte **solo si el resto del payload coincide con la SRAM actual**, dato que no se
conoce y que el emisor BIONZ controla. No es una modificación selectiva demostrada y puede alterar
el watchdog; **descartado**.

### 3.3 `InitCom 0x16` (escritura absoluta) — prototipo parcial

El comando `0x16` (`0x4cec`) acepta una dirección en `0x20000000..0x20004000` y una longitud con el
bit 7 como indicador de escritura absoluta; con `dirección = 0x20000050` y longitud 1, el lado
Darwin escribiría **solo** la compuerta (modelo: `accepted: true`, `bytes_changed: 1`,
`changed_offsets: ["0x50"]`). Es la única vía volátil selectiva que existe en el código, pero:

1. **No hay emisor BIONZ demostrado** de esa trama con esa dirección/longitud. El protocolo se
   reconstruyó desde el lado Darwin/actualizador; el emisor normal no está leído.
2. **Solo existe en `Seton`**: la tarea COM y `InitCom` no existen durante `On`/captura. La escritura
   tendría que ocurrir en el arranque y persistir en SRAM hasta la captura.
3. **T022/T023 no alcanzan la SRAM de Darwin**: leen DRAM de BIONZ
   (`0x83f91e20..0x83f91f30`), no `0x2000xxxx`; no hay una vía de lectura/escritura demostrada.
4. **Reversión**: la SRAM de Darwin está siempre alimentada (E24-05 §5); un apagado normal no la
   borra. Habría que reescribir el byte original por la misma vía o resetear Darwin; ninguna de las
   dos está demostrada.

**Eslabón exacto que falta:** un emisor BIONZ de `0x16` con `dirección=0x20000050`, `longitud=1` y
un disparo en `Seton`; además, una vía de lectura/verificación y un método de reversión. Sin eso,
A = **NO**. No se implementa una escritura de RAM ni un script que la toque.

## 4. Implementación B — modificación mínima de Darwin

### 4.1 Comparación de alternativas

| Alternativa | Bytes | Qué cubre | Qué deja vivo | Veredicto |
|---|---|---|---|---|
| **B1a** `0x1fe6a: mov r0,r5 → b 0x1fe82` | **2** (`28 46` → `0a e0`) | Los 12 consumidores de `0x1fe66`: tres arrancadores, `0x1f5a6`, `0x1f4b6`, `0x1f4ce`, `0x1f572`, `0x1f896`, `0x1f908`, `0x1fa3a`, `0x1fe86`, `0x201bc` | Operación 5 (`0x1fcb8→0x1feb6`) y P4B/P4C | **SELECCIONADA** |
| B1b `0x1fe70: lsrs r4,r0,#4 → movs r4,#0` | 2 | Igual que B1a (fuerza el índice 0 de la tabla) | Igual; depende de la tabla TBB | Equivalente; no se elige por dependencia extra |
| B2 `0x1f5a2` (thunk) → `movs r0,#0; bx lr` | 4 | Los 3 arrancadores y los 3 pulsos de servicio | **`0x1f5a6` llama a `0x1fe66` directamente**: la operación 5/rearme directo seguiría con la compuerta real (4) y podría mover el motor; `0x1f4b6/0x1f4ce/0x1f572/0x1f896/0x1f908/0x1fa3a/0x1fe86/0x201bc` también | **RECHAZADA** (cobertura incompleta) |
| B3 cambiar el dato `[0x20000050]` por `InitCom` | 1 dato | La compuerta y el tipo | Sin escritor estático; `0x12` bloque; `0x16` sin emisor; solo `Seton` | **RECHAZADA** (A=NO) |

B1a es la modificación más pequeña que cubre **todos** los consumidores de la compuerta con una
sola semántica: retorno 0. No se parchea el selector de listas por separado porque el problema no
es solo la lista exterior: `0x1f5a6` y `0x1fe86` consultan la compuerta directamente.

### 4.2 Bytes exactos

```text
Antes (tipo 0, 0x1fe66):
0x1fe66: 70 b5        push {r4,r5,r6,lr}
0x1fe68: 00 25        movs r5,#0
0x1fe6a: 28 46        mov r0,r5          <-- se parchea
0x1fe6c: fb f7 08 f9  bl 0x1b080
0x1fe70: 04 09        lsrs r4,r0,#4
0x1fe72: 06 2c        cmp r4,#6
0x1fe74: 05 d2        bhs 0x1fe82
0x1fe76: df e8 04 f0  tbb [pc,r4]
0x1fe7a: 04 03 03 03 03 03
0x1fe82: 28 46        mov r0,r5
0x1fe84: 70 bd        pop {r4,r5,r6,pc}

Después (E25):
0x1fe66: 70 b5        push {r4,r5,r6,lr}
0x1fe68: 00 25        movs r5,#0
0x1fe6a: 0a e0        b 0x1fe82          <-- 2 bytes cambiados
0x1fe82: 28 46        mov r0,r5          ; r5 = 0
0x1fe84: 70 bd        pop {r4,r5,r6,pc}
```

El salto va al epílogo; no se ejecuta `0x1b080`, ni la tabla, ni el `mov r5,r4`. `r5` sigue valiendo
0 y el marco de pila se conserva (`push`/`pop` intactos). El offset de archivo es `0x1fe6a − 0x4200
= 0x1bc6a = 113770`.

### 4.3 Funciones afectadas (los 12 consumidores)

| Sitio | Función | Efecto con retorno 0 |
|---|---|---|
| `0x1f4ba` | `0x1f4b6` (pulso de servicio) | Exige 4; no ejecuta el pulso |
| `0x1f4de` | `0x1f4ce` (comprobación de leva) | Se salta el error 6 `0x1f518` |
| `0x1f576` | `0x1f572` (lectura de leva) | Devuelve 0 sin leer P25–P27 |
| `0x1f5a2` | thunk de los 3 arrancadores + 3 pulsos | Los 3 eligen L0; los pulsos no actúan |
| `0x1f5a8` | `0x1f5a6` (rearme directo) | Retorna en `0x1f5ae`; no enciende el motor |
| `0x1f896` | `0x1f88a` (interior) | No llama a `0x20c90`; inalcanzable desde L0 |
| `0x1f908` | `0x1f8fc` (interior) | **Sí llama a `0x20c90`** (0 no es 1 ni 2); el tipo 0 impide la escritura P4D. Inalcanzable desde L0 |
| `0x1fa40` | `0x1fa3a` (timeout interior) | Emite error 6 si se alcanza; **no se alcanza desde L0** |
| `0x1fe88/90/98` | `0x1fe86` (motor=2) | No ejecuta `0x1fe32/0x51cc` |
| `0x201bc` | `0x201b0` (guarda de `S+0x150`) | Con tipo 0 ya no llegaba; con 0 tampoco |

Esto explica por qué el **tipo 0 es obligatorio**: `0x1f908` y el estado 7 de L0 siguen llamando a
`0x20c90`; la compuerta 0 no filtra las bobinas, solo evita el motor. Sin el parche tipo 0, el
estado 7 de L0 podría escribir P4D. El candidato se genera desde la copia tipo 0 y el manifiesto
marca `requires_tipo0: true`.

No hay ningún consumidor de `0x1fe66` en `InitCom` (`0x4bca–0x5000`), `Upd` (`0x8da8`), reset
(`0x45c8–0x4638`), watchdog (`0xa4ac–0xa540`), tabla de energía (`0x28c6c`) ni `Off` (`0x8908`). El
parche son 2 bytes dentro de `0x1fe66`; el manifiesto compara las regiones protegidas por SHA-256.

## 5. Implementación reproducible

### 5.1 Herramienta

`scripts/e25/patch_darwin.py`:

```bash
python scripts/e25/patch_darwin.py inspect  INPUT
python scripts/e25/patch_darwin.py apply    INPUT OUTPUT [--manifest JSON]
python scripts/e25/patch_darwin.py verify   INPUT PATCHED [--manifest JSON]
python scripts/e25/patch_darwin.py restore  PATCHED OUTPUT --manifest JSON
```

- Acepta **solo** las variantes con SHA-256/tamaño/`VER0.78`/bytes de tipo esperados:
  `original_321` y `tipo0_322`; rechaza cualquier otra.
- `apply` exige que `OUTPUT != INPUT`, que la salida sea `.bin` y que no exista ya el parche;
  genera un binario separado y un manifiesto JSON con offset, dirección ROM, bytes antes/después,
  SHA-256 de salida, hashes de las regiones protegidas y el diff completo.
- `verify` comprueba que el binario solo difiere en las posiciones autorizadas.
- `restore` verifica el SHA del parcheado contra el manifiesto, repone los 2 bytes y exige que el
  SHA-256 resultante sea exactamente el de entrada.
- `m0_candidate` es `true` solo si la entrada ya lleva el tipo 0. Con el original se genera un
  control `gate0` pero **no** es M0: el estado 7 de L0 llama a `0x20c90` y, sin tipo 0, ese escritor
  sí llegaría a P4D.

### 5.2 Manifiestos y diff

`analysis/e25/manifest_tipo0_sin_rearme.json` y `manifest_original_sin_rearme.json` (versionados).
El diff del candidato tipo 0 es exactamente:

```text
rom 0x1fe6a / file 113770: 28 -> 0a
rom 0x1fe6b / file 113771: 46 -> e0
```

`analysis/e25/route-a-volatile.json`, `mechanical-reachability.json` y `patched-bytes.json` son los
resultados reproducibles de `python scripts/e25/analyze.py --write`. Los `.bin` derivados están en
`analysis/e25/` y Git los ignora (`*.bin`); **no se genera FDAT/DAT**.

## 6. Auditoría mecánica

### 6.1 Selección de listas

| Arrancador | Compuerta 4 | Compuerta 0 |
|---|---|---|
| `0x1fee2` (load) | `0x29cdd` = `[0,2,3,6,9,10]` (L1) | `0x29cd8` = `[0,7,8,9,10]` (L0) |
| `0x1ff72` (captura 4) | `0x29ce3` = `[0,4,5,6,9,10]` (L2) | L0 |
| `0x1ffce` (captura 5/0x1f) | `0x29ce9` = `[0,1,4,5,6,9,10]` (L3) | L0 |

L0 ejecuta los manejadores `0x20100` (marca ocupado, espera `0x8ca0`), `0x2014c` (llama a
`0x20c90`, espera `0x5dc0`), `0x200e2` (espera/termina), `0x200e6` (`0xd18e(0x1000000)` libera la
ocupación) y `0x200fc` (termina). La máquina interior de 27 estados solo se arranca en los estados
exteriores 2 y 4 (`0x20126/0x2013a`); L0 no los contiene.

### 6.2 Cobertura por escenario

| Escenario | Ruta | Resultado estático con tipo 0 + compuerta 0 |
|---|---|---|
| Arranque / `On init` | `0x75f0 → 0x1b260 → 0xcee6 → 0x1984e(0)` | Elige L0; no motor. `0x1984e` puede seguir emitiendo error 6 `0x1989c` si el ADC de posición no está en el estado esperado; eso encola operación 5 (freno), no rearme. |
| Disparo normal | `0x19998`/`0x199b8` → `0x1ff72`/`0x1ffce` | L0; sin primitivas del motor |
| Ráfaga | `0x17cee` (preparación), `0x17a44`, tarea `0x1811a` | L0; sin motor |
| Estados 4/5/0x1f de los 49 | `0x18636/0x1865a/0x190fc` | L0; sin motor |
| Cancelación | COM `0xed18` / `0x4ed8` | No contiene consumidores de `0x1fe66`; no cambia |
| Error de posición | `0x1f4ce` | Compuerta 0 → no error 6; `0x1989c` sigue siendo independiente |
| Timeout | `0x1fa3a` | Solo dentro de la máquina interior; L0 no la arranca |
| Apagado | `Off main 0x8908` | Sin consumidores de `0x1fe66`; regiones protegidas intactas |
| Servicio BIONZ | pulsos `0x90/0x91` (`0x2008e/0x200a6`) | Con 0 no ejecutan `0x1fe50/0x1fe86/0x1feb6` |
| Operación 5 | `0xd46e → 0x1f600 → 0x1fcb8 → 0x1feb6` | **Excepción**: freno P40/P41=3 sin compuerta |

### 6.3 Operación 5 — el freno

`0x1feb6` hace `0x1fe32` (P40=P41=0) y escribe `r1=3` con `r2=0xfffc` en `PDOR4` (`0x51cc`);
`0x1fcb8` espera `0x7a120` y después llama a `0x1fe32` para apagar. En el circuito documentado
(manual de servicio), Q6801 se excita por la XOR IC6800 con entradas P40 y P41:

| Valor | P40 | P41 | XOR | Interpretación |
|---|---|---|---|---|
| 0 (`0x1fe32`) | 0 | 0 | 0 | apagado |
| 1 (`0x1fe50`) | 1 | 0 | 1 | movimiento |
| 2 (`0x1fe86`) | 0 | 1 | 1 | movimiento |
| 3 (`0x1feb6`) | 1 | 1 | 0 | freno/pasivo, **no orden de movimiento** |

Por tanto el freno de la operación 5 no es una orden de movimiento en el modelo del circuito; su
efecto físico (corto/frenado dinámico) **no está medido**. No se anula: es la protección de
emergencia. **M0 en escenarios de error queda pendiente** hasta medir si el freno produce
movimiento o esfuerzo mecánico.

### 6.4 P4D/P4E, P4B y P4C

- **P4D/P4E** (`0x234/0x238`): cuatro escritores (`0x20c90/0x20cb2/0x20cd4/0x20d00`) consultan
  `0x20c74`; con tipo 0 no llegan a `0x51c0`. L0 no contiene ninguna escritura a P4D/P4E.
- **P4C** (`0x230`): `0x1ecec` escribe 1 o 0 a través de `0x51c0(0x230, r1)`; se fija a 1 en cada
  toma (`0x16e7a` desde `0x17cee` y `0x175ea`) y se borra en `0x16e68`. **Corrige `rea-tema3`**:
  sí existe `P4C←1`; los 9 sitios con literal solo escriben 0, pero `0x1ecec` usa el alias variable
  `r0=0x230`. Sigue activo con tipo 0.
- **P4B** (`0x22c`, bit 11): `0xd116/0xd18e` con máscara `0x800` (ocupación). Sigue cambiando
  durante la captura; no es el motor de rearme.
- El consumidor físico de P4B/P4C (IC6000) no está localizado; **no se puede afirmar** que su
  actividad no mueva nada. Es un riesgo residual, no una prueba de movimiento.

### 6.5 Errores de categoría 6

Cinco sitios: `0x1989c`, `0x1f518`, `0x1fab8`, `0x20878`, `0x20894`.

| Sitio | Con tipo 0 + compuerta 0 |
|---|---|
| `0x1989c` (ADC de posición en `0x1984e`) | **Sigue vivo**; puede encolar la operación 5 (freno). No es rearme. |
| `0x1f518` (leva) | No se alcanza (compuerta 0) |
| `0x1fab8` (timeout interior) | Solo si se arranca la máquina interior; L0 no la arranca |
| `0x20878/0x20894` (fase ADC) | Solo con tipo ≠ 0 |

## 7. Pruebas

- **Nuevas E25:** `python -m pytest -q tests/test_e25_desactivacion.py` → **54 passed** (≈12 s).
  Cubren integridad de entrada, variantes, rechazo de SHA/tamaño/versión, aplicación determinista,
  diff autorizado, reversión exacta, preservación del tipo 0, selección de las tres listas, L0
  completo, liberación de ocupación, ausencia de primitivas en captura/ráfaga/load, operación 5,
  errores 6, P4D/P4E/P4B/P4C, InitCom 0x12/0x16, T022/T023, emisores MSS y regiones protegidas.
- **Regresión relevante:** `tests/test_e24_*.py` (todos), `test_darwin.py`,
  `test_fm3_gpio_literals.py`, `test_s135_elec_shutter.py`, `test_s172_elec_shutter_a6300.py`,
  `test_s401_a7s_caif.py`, `test_s402_static_closure.py` → **304 passed, 4 skipped, 1 failed**.
  El fallo es **preexistente y de entorno**: `test_e24_03_recovery.py::test_recovery_323_rebuilds_byte_for_byte`
  invoca `/usr/bin/python` para `fwtool` y ese intérprete no tiene `Cryptodome`/`Crypto`
  (`ModuleNotFoundError`). No se tocó `fwtool` ni el paquete 3.23. Reproducible:
  `/usr/bin/python references/fwtool/fwtool.py ...` falla por la misma causa.
- **Suite completa:** no es concluyente por errores de colección preexistentes
  (`tests/knowledge/test_mcp_server.py` sin `mcp`; `tests/test_s300_state_xref_sweep.py` con
  colisión de módulo; tests de `tools/providers/ghidra...` sin `jpype`/`pyghidra`). No son
  regresiones de E25.

## 8. Riesgos, bloqueantes y M0

1. **E24-04 sigue abierto:** no hay recuperación independiente demostrada si Darwin no arranca. El
   candidato es offline; **no instalar**.
2. **M0 normal (captura/rearme):** demostrado estáticamente para el motor y P4D/P4E. **M0 en error:**
   pendiente por el freno de la operación 5 (`P40/P41=3`, XOR=0, efecto físico no medido) y por
   P4B/P4C.
3. **BIONZ:** no está demostrado que acepte el fin de L0 (`0x8ca0+0x5dc0` unidades) ni que la captura
   complete sin esperar un mensaje que Darwin no envía. E24-05a C/D y E24-05d/e/f/g/h siguen
   abiertos en sus eslabones BIONZ.
4. **`0x1989c`:** puede emitir error 6 en `load(0)` y encolar la operación 5; no mueve el motor por
   sí mismo, pero puede producir un freno y un registro de error.
5. **SRAM de Darwin:** si en el futuro se usara una vía volátil, un apagado normal no la borra; la
   reversión exige reescribir el byte o resetear Darwin.
6. **P4B/P4C:** siguen activos; su efecto físico no está medido. No se afirma inmovilidad total.
7. **Watchdog/alimentación/Upd:** el parche no los toca (2 bytes y hashes de región), pero no se ha
   medido que el watchdog tolere la duración de L0. E24-05b sigue abierto.
8. **Instalación:** requiere un FDAT de versión mayor que la instalada (3.24) y una recuperación
   ≥3.25; no se genera en esta sesión.

## 9. Condiciones para una prueba física controlada (no ejecutada)

1. **Autorización expresa** del usuario para flashear y **E24-04 resuelto** (recuperación
   independiente demostrada) o aceptación explícita y documentada del riesgo residual.
2. **Paquete:** FDAT 3.24 con el candidato, CRC-32 recalculado, `VER` correcta, y recuperación 3.25
   preparada y verificada offline. No usar el 3.23 actual (guard de versión).
3. **Instrumentación pasiva:** corriente del motor (CM+/CM−), P40, P41, P4D, P4E, P4B, P4C, P29,
   P25–P27 y CAIF. Sin instrumentación no se puede distinguir «sin orden» de «sin movimiento».
4. **Matriz mínima:** arranque, reposo, 1 disparo, ráfaga de 3, cancelación, error de posición
   (desconectar/forzar leva), timeout, apagado. En cada caso: corriente del motor, flancos de
   P40/P41, P4D/P4E, P4B/P4C, P29 y mensajes MSS/CAIF.
5. **Criterios de aceptación:** `done` incrementa en cada disparo; no hay corriente en CM+/CM− ni
   flancos de movimiento en P40/P41; P4D/P4E no se activan; el watchdog no reinicia; la cámara
   arranca y el actualizador sigue siendo alcanzable; el error 6/operación 5 no se repite en cada
   disparo.
6. **Rollback:** restaurar el tipo 0 original (`ca41b46c…`) o el oficial 3.23/3.25 con el
   procedimiento verificado; backup NVRAM previo; verificar el arranque y el `done` tras la
   restauración.
7. **Cierre de M0 en error:** decidir si el freno de la operación 5 se mantiene (protección) o se
   condiciona; no anularlo sin medir su efecto.

## 10. Reproducción

```bash
# 1) Identificar y aplicar el candidato (offline)
python scripts/e25/patch_darwin.py inspect analysis/darwin-patch/darwin_core_tipo0.bin
python scripts/e25/patch_darwin.py apply analysis/darwin-patch/darwin_core_tipo0.bin \
  analysis/e25/darwin_core_tipo0_sin_rearme.bin \
  --manifest analysis/e25/manifest_tipo0_sin_rearme.json
python scripts/e25/patch_darwin.py verify analysis/darwin-patch/darwin_core_tipo0.bin \
  analysis/e25/darwin_core_tipo0_sin_rearme.bin \
  --manifest analysis/e25/manifest_tipo0_sin_rearme.json
python scripts/e25/patch_darwin.py restore analysis/e25/darwin_core_tipo0_sin_rearme.bin \
  /tmp/restaurado.bin --manifest analysis/e25/manifest_tipo0_sin_rearme.json

# 2) Análisis y tablas
python scripts/e25/analyze.py --write

# 3) Pruebas
python -m pytest -q tests/test_e25_desactivacion.py
python -m pytest -q tests/test_e24_*.py tests/test_darwin.py tests/test_fm3_gpio_literals.py \
  tests/test_s135_elec_shutter.py tests/test_s172_elec_shutter_a6300.py \
  tests/test_s401_a7s_caif.py tests/test_s402_static_closure.py
```

## 11. Límites de la evidencia

- Todo es estático o modelo: no se ejecutó firmware ni se midió la cámara. «Sin primitivas» significa
  que el cierre de llamadas/ramas no las alcanza, no que el hardware esté quieto.
- El cierre de alcanzabilidad usa poda por constantes de la compuerta/tipo y expansión de tablas;
  las llamadas indirectas abiertas se listan en `reach.open_indirect` (una por escenario principal).
- La duración de L0 (`0x8ca0 + 0x5dc0` unidades) y la unidad del tick no están medidas; la
  compatibilidad con las esperas de BIONZ no está demostrada.
- El freno de la operación 5 se modela por la XOR del circuito; el efecto físico no se midió.
- P4B/P4C no tienen consumidor localizado; su efecto mecánico es un riesgo residual.
- **Un binario parcheado que pasa las pruebas no es un binario seguro de instalar.** E24-04 sigue
  siendo el bloqueante.
