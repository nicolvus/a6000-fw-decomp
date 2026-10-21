# Tema 3 — Control físico de cortinas y puente físico Darwin/MCU (P4C / 1ST_CURTAIN_MG / 2ND_CURTAIN_MG)

Sony A6000 (fw 3.21). Foco: obturador completamente electrónico. Análisis estático únicamente; sin cámara, sin flasheo, sin ejecución de firmware.

## Fuentes y base de direcciones

- `av-cam.bin` (BIONZ), base `0x43541000`, SHA `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`; REA/Ghidra 12.1.4 (sesiones del proyecto, efímeras).
- Darwin (FM3, base ROM `0x4200`), A6000 3.21 `5f2be06d…0bf4` y A7S 3.20 `241f5d31…6174cf`; verificación estática con capstone + bytes sobre binarios con SHA verificado (suites: `test_s54_p4c` 21/21, `test_s53_darwin_caif` 10/10, `test_s55_bionz_sync` 16/16, `test_s52_curtain_facts` 14/14).
- Contradicciones: `search.py claim` sobre S52–S55 y sobre este informe → sin correcciones registradas en el grafo actual.

## Nota sobre la sesión REA propia (obligatoria)

Se arrancó el demonio en `analysis/rea-independent/run/rea-tema3.sock` y se hizo polling hasta ~12 min; el análisis en frío no liberó el socket (contendía con la instancia `rea.sock` concurrente; el proceso terminó sin evento `analysis_ready`). **No se atendieron llamadas del lote `/tmp/opencode/tema3-calls.json`**. Las marcas «REA» de este informe usan el log de sesión previa del proyecto sobre el **mismo binario** (`analysis/rea-independent/out/exp2-session-log.jsonl`, mismo SHA y Ghidra 12.1.4): `xrefs(0x43e77298)` → 8 lecturas, sin escritor. Próximo paso exacto: §5 (relanzar el daemon en solitario y ejecutar ese lote).

---

## 1. Escritor/localizador de P4C en A6000 y consumidor de P4C

### Escritor de P4C (Darwin, base 0x4200) — VERIFICADO

P4C = `CA_1ST_CURTAIN_START` = bit 12 de `PDOR4`, alias bit-band `0x42668230`. Escritor único:

- `0x51c0` (A6000) / `0x5200` (A7S): `ldr r2,=0x42668000; str r1,[r0,r2]`, bytes idénticos en ambos modelos. Lector `0x51c6`/`0x5206` (+6) sobre `0x42666000` (PDIR).

9 sitios de escritura P4C por ROM, todos con valor **0** (`movs r1,#0` justo antes del `bl` al escritor), nunca `P4C←1` (barrido de 177 `bl` A6000):

| Función | Sitios (A6000) | Valor |
|---|---|---|
| `0x20d26` | `0x20d8a`, `0x20dba`, `0x20df6` | 0 |
| `0x20e0e` | `0x20e30`, `0x20e64`, `0x20e96→0x20e6e` | 0 |
| `0x20e98` | `0x20ece`, `0x20f14`, `0x20f34` | 0 |

Otras vías a `PDOR4`:

- `0x51f2(4, 0x4000, 0x9fff)`: máscara que **conserva b12** (nunca la pone a 1); único llamador `0x20e3e`.
- `0x584c` (inicialización GPIO): `DDR4=0x7e3f` (b12 = salida), `PDOR4=0` (`0x58f6/0x58fa`); perfiles de pin vía `0x55d0` (`0x25bfc+n·0x98`). Vuelto a ejecutar solo desde arranque `0x47fa` y cambio de energía `0x87ba` (llamador `0x8a42`). **Rearme de P4C: NO_VERIFICADO.**

Conclusión 1a: **sí existe escritor de P4C en Darwin A6000** (`0x51c0`, 9 sitios), pero siempre escribe 0; **no existe escritura `P4C←1`** en el código recorrido. Escritores de bobinas `0x20c90` (P4D=1), `0x20cb2` (P4D=0), `0x20cd4` (P4E=0), `0x20d00` (P4E=1): todos pasan por el filtro `0x20c74` = `0x1b080(0)&7 ∈ {1,2,3}` (§3).

### Consumidor de P4C (BIONZ / av-cam.bin) — NO localizado

Primitivas GPIO de BIONZ en `av-cam.bin` (VERIFICADO, S54-B):

- `0x43b5e2bc(ch,bit)` = `gpio_get` (lee RDATA `+0x10` si DIR=0, si no WDATA `+0x40`; base `0xf2910000`).
- `0x43b5e22e(ch,bit,cfg*)` = configuración de pin (11 puntos de llamada).
- `0x43b5e29a` = `gpio_set(ch,bit,val)`.

97 llamadas totales (50 get, 4 set, 43 cfg); solo 10 con canal inmediato; **ningún `get` con canal inmediato**; el resto lee pares de variables globales.

Variables de pin de los lectores de tarea CA: `0x43e77298…0x43e772cc` (acceso por GOT `0x4402xxxx`). **Escritor localizado:** `0x436bcef4` (A6000) / `0x436dc054` (A7S) (S55, verificado por capstone; el store es indirecto vía GOT, por eso `xrefs` a la dirección exacta no lo proyecta): lee 16 IDs de la base de backup BK4 (`0110_backup/…/CX77500_*.bin`) vía `Backup_read_4Byte` y vuelca a esas celdas. Los 16 pares (canal, bit) son lectores SIO `(3,17),(10,3),(0,12),(0,7),(5,14)`, salidas `(7,15),(7,13)`, sin lectores `(0,16)`. **Ningún par es GPIO_9 (bit 9) ni P4C.**

REA `xrefs(0x43e77298)` sobre `av-cam.bin`: 8 referencias, todas de lectura: `0x436ba68a`, `0x436ba68c`, `0x436ba6c6`, `0x436ba6c8`, `0x436ba736`, `0x436ba738`, `0x436bb9e8`, `0x436bb9ea` (lectores `0x436ba67c`, `0x436bb9d8`… de la tarea CA, trazas «S2REQ HI/LO», «CamSioSnd InRel H»). **Ninguna escritura** en `av-cam.bin` a esa dirección.

Conclusión 1b: **consumidor de P4C NO localizado**. Darwin emite `P4C←0` en todas las capturas; BIONZ tiene las primitivas y el cableado (`SENS_B` AA13 y `GPIO_9` AD21, verificado por esquema, §2), pero ninguna función de `av-cam.bin` se identifica como consumidora de P4C; `ExpStartComp`/`ExposureEndNotify` son etiquetas de mensaje CAIF sin demostración de consumo de P4C.

---

## 2. Puesto Darwin/MCU: parser CAIF, bit no_silent 0x20, clase de obturación 0

### Parser CAIF — VERIFICADO (S53)

- Paquete CAIF ev1 (22 B) → Darwin por MFS5 (P36–P38 = `MSS_*_DWN`) como mensaje mss-async **ID `0x0c`** (código `03 01`, 22 B; `rx 0x2000344c` A6000; tabla de mensajes `0x27c68`, entrada `0x27c78`; estructura destino `S` en `0x200036d8`). Parser: **A6000 `0x17f8c`**, A7S `0x18396`; mismo código salvo inserción Silent. **Recepción real del paquete por Darwin: NO demostrada** (`darwin-shutter-entrypoints.md`); identidad con op `0x10300` de LIRO: inferencia fuerte.
- `pkt[+0x12]`: bit 3 → `S+0x42`; bit 0 → `S+0xd0` b0; **A7S: bit 5 → `S+0xd0` b5** (bytes `0x18460..0x18488`, ausentes en A6000 tras `0x18052`) → predicado `no_silent` `0x19a86` (`!(S+0xd0 & 0x20)`) que **impide escribir P4D/P4E** (`0x2172c`, `0x21786`, `0x217b2…`, diferidos `0x214dc/0x214fa`) y omite seguimiento ADC. **A6000 descarta el bit `0x20`** y sus escritores (`0x20cb2`, `0x20d00`, `0x20d26…`) **no tienen argumento Silent**. Modo 2 de `pkt[+0x0d]`: sin consumidor de bits 6–7 en ninguna ROM (búsqueda negativa, parcial).
- `pkt[+0x01]` = clase de obturación; reescrita según el tipo de mecanismo por `0x202ba`/`0x20c90` (1/2 → `&~3`; 3 → `+1`; 4 → `+2`).

### Clase de obturación 0 — VERIFICADO en A7S; cadena A6000 sin ramas Silent

- A7S: clase 0 llega a `param+9` por `0x43864c74 → 0x43f04c8c → R+0x69 → cap+0x651 → 0x436f2938 → vtable+0x28`. La clase por sí sola **no omite** envío CAIF ni MMIO (solo mensaje interno `0x22`).
- A6000: política `0x43842158` **sin ramas Silent**; `0x4383fd6c` (≙ `0x43862158`) copia 16 B del registro `+0x64..+0x73` a `*param3`; la clase queda en `destino+9` (`captura+0x651` vía `0x437f8a50` → `captura+0x64c`; segunda llamada `0x43b1d914`, selector también en `captura+0x4cc`); IMX210 `SetExposure` `0x436d6320` → virtual+28 → vtable `0x43fcc090+0x28 = 0x436d6f6d` → `0x436d6fb6 ldrb.w r9,[r1,#9]`. ShutMode real en captura: solo 0 y 1 (S57). IMX210 no tiene modos `0x4e/0x4f` (IMX235 Silent).
- `captura+0x740` (A6000) ≡ `captura+0x748` (A7S): bandera funcional (esperas/eventos/temporizador). A7S: escritor único `0x43813ea2` (`=1` si tipo Silent `cap+0x78c==2`; bytes `8af7b6fe0228c4f88c0702d10123c4f8`). **A6000: lectores existentes** (`0x438c8104` ID `0x1cb`, `0x438c825e` ID `0x1ca`, `0x438c8ac8` ID `0x108`, lector latente `0x438c240e` ID `0x109`: `if 740==1 && 0x436e8328()==1 → 0x438d08c8`, `0x43b1e7b0..7b6` lee `#0x740`/`#0x73b`) y **ningún escritor directo** (barrido `STR.W` imm `0x740` en todo el binario: nada en la estructura de captura). Inicialización del campo: **NO_VERIFICADO** (probablemente constante 0, inferencia).

### ¿Evidencia de que el MCU toma la decisión física?

**Inferencia fuerte, no demostrada.** Darwin gatea las bobinas P4D/P4E vía parser CAIF + tipo de mecanismo, y emite `P4C←0` siempre. Pero: (i) el escritor del byte de tipo `[0x20000050+ch]` no está localizado (§3); (ii) no hay evidencia de que Darwin lea al sensor para decidir; (iii) la recepción CAIF por Darwin no está demostrada; (iv) no hay consenso LIRO+Darwin demostrado. Que la decisión física repose en el MCU Darwin es la hipótesis que mejor encaja el código, pero no es un hecho demostrado.

---

## 3. Tipo de mecanismo: ¿escritor de [0x20000050+ch] localizado? ¿Tipo 0 suprime cortinas físicas?

### Escritor del tipo de mecanismo — NO localizado (VERIFICADO ausente)

- `0x1b080(ch)`: si `[0x200002c0+ch]≠0` devuelve `[0x20000000+0x50+ch]`, es decir `[0x20000050+ch]`, si no 0 (literales `0x1b0e0=0x200002c0`, `0x1b0e4=0x20000000`; `0x1b090`: `ldr r0,[r0,#0x50]`).
- `0x20c74 = 0x1b080(0)&7 ∈ {1,2,3}`; cualquier otro valor (incluido 0) → 0. (A7S: `0x216e8` con `0x1b5e8`, misma forma.)
- Handler `0x1b0b2` = **entrada 33 de la tabla de 48 handlers `0x2a1a0`** (categoría `0x2d`): mensaje `{idx<0x18, 1/0}` pone `[0x200002c0+idx]=1` solo si `[0x20000050+idx]≠0`. Invocado por tabla, **sin llamadores directos**.
- Quién escribe `[0x20000050+ch]`: no hay `strb …,[r,#0x50]` ni literal `0x20000050`; la estructura `0x20000000` se llena por copias/mensajes. Hipótesis: llega de BIONZ por enlace MSS (cadenas `Sens:AdjCmd DwnCamera`, `SaveUsr:Read CAM`, `Sens:BkSyncCb CAIF` de `av-cam` son compatibles) o constante de fábrica/ajuste. **NO_VERIFICADO.**

### ¿Tipo 0 suprime cortinas físicas en A6000? — PARCIAL

| Elemento | Efecto con tipo 0 | Evidencia |
|---|---|---|
| P4D (`0x20c90`=1, `0x20cb2`=0) | nunca escrito | filtro `0x20c74` |
| P4E (`0x20cd4`=0, `0x20d00`=1) | nunca escrito | id. |
| **P4C** (`0x20d26/0x20e0e/0x20e98`) | **sí se escribe (←0)**, incluso en rama «sin mecanismo» | §1 |
| Temporización `0x93e6` y marca `S+0x180` | se mantienen | `0x20dda`, `0x20e88`, `0x20f2a` |
| Seguimiento ADC de fases (`0x20734`, `0x2083c`) | omitido (`S+0x153←0`) | `0x2077c/0x20780`, `0x20840/0x20844` |
| Rutas de reposición/aborto (`0x203b2`, `0x206ec`, diferidos `0x20a8a/0x20aa4`) | sin acción de bobina | filtro `0x20c74` |

Conclusión 3: tipo 0 suprime P4D/P4E y el seguimiento ADC en **todas** las rutas (más que Silent A7S, que sí actúa bobinas en reposición/aborto con `no_silent=1`), pero **mantiene `P4C←0` y la temporización**. Falta la polaridad/idle de P4C (perfil 3 da nivel inicial 1; qué usa la placa depende de `0xcf3a`/`0x5b36`, sin resolver) y falta el lado sensor. Por tanto no se ha demostrado que «suprima las cortinas físicas» en sentido completo; equivalencia funcional plena con Silent A7S: **NO demostrada**.

---

## 4. Tabla VERIFICADO vs NO_VERIFICADO (direcciones exactas)

### VERIFICADO (hecho: bytes, tests de binarios originales o REA)

| Ítem | Dirección / evidencia | Estado |
|---|---|---|
| Escritor P4C Darwin A6000 | `0x51c0`; 9 sitios `0x20d8a/20dba/20df6`, `0x20e30/20e64/0x20e96→0x20e6e`, `0x20ece/0x20f14/0x20f34`; todos ←0 | VERIFICADO (tests 21/21) |
| Ausencia de escritura P4C←1 | barrido de 177 `bl` A6000 | VERIFICADO |
| `0x51f2` conserva b12 de PDOR4 | llamador `0x20e3e` | VERIFICADO |
| Escritores P4D/P4E gateados por tipo | `0x20c90/0x20cb2/0x20cd4/0x20d00` vía `0x20c74` | VERIFICADO |
| Parser CAIF A6000 | `0x17f8c` (A7S `0x18396`); ID `0x0c`, `rx 0x2000344c`, tabla `0x27c78`, `S=0x200036d8` | VERIFICADO (bytes + tests 10/10) |
| Bit `0x20` de `pkt[+0x12]` = `no_silent` | A7S: `S+0xd0.b5`, `0x19a86`; A6000 lo descarta | VERIFICADO |
| Escritores P4C sin argumento Silent (A6000) | `0x20cb2`, `0x20d00`, `0x20d26` | VERIFICADO |
| Tipo = `[0x20000050+ch]`; validez `[0x200002c0+ch]` | `0x1b080`, literales `0x1b0e0/0x1b0e4`, handler `0x1b0b2` = entrada 33 de `0x2a1a0` (cat `0x2d`) | VERIFICADO |
| Escritor de variables de pin BIONZ | `0x436bcef4` (A6000), store vía GOT, 16 IDs BK4 | VERIFICADO (S55, capstone) |
| Ninguna de las 16 variables es GPIO_9/P4C | pares SIO `(3,17),(10,3),(0,12),(0,7),(5,14),(7,15),(7,13)` | VERIFICADO |
| REA `xrefs(0x43e77298)` | 8 lecturas `0x436ba68a…0x436bb9ea`; sin escritura | VERIFICADO (REA, sesión previa del proyecto, mismo binario/Ghidra) |
| Primitivas GPIO BIONZ | `0x43b5e2bc` get, `0x43b5e22e` cfg, `0x43b5e29a` set, base `0xf2910000` | VERIFICADO |
| Clase 0 → `param+9` (A7S) | `0x43864c74 → 0x43f04c8c → R+0x69 → cap+0x651 → 0x436f2938 → vtable+0x28` | VERIFICADO (S52) |
| Clase → `captura+0x651` (A6000) | `0x4383fd6c` (≙ `0x43862158`) → `*param3`+9; `0x437f8a50` → `captura+0x64c` | VERIFICADO (S52 / efcs-capture-selector) |
| `captura+0x740` A6000 latente | lectores `0x438c8104/825e/8ac8/8240e` y `0x43b1e7b0..7b6`; sin escritor directo | VERIFICADO (ausencia de escritor por barrido) |
| Escritor `captura+0x748` A7S | `0x43813ea2` (`=1` si tipo Silent == 2) | VERIFICADO (S52) |
| Cableado P4C → pines BIONZ | `SENS_B` (AA13), `GPIO_9` (AD21), verificado por esquema | VERIFICADO (esquema; consumo de las líneas, NO) |

### NO_VERIFICADO / abierta

- Escritor de `[0x20000050+ch]` (origen del tipo de mecanismo) — NO localizado.
- Escritor/inicializador de `captura+0x740` en A6000 — no hay escritor directo.
- Consumidor de P4C en BIONZ (qué hace con `SENS_B`/`GPIO_9`) — NO localizado.
- Rearme de P4C (`0x584c` solo desde arranque/energía) — NO_VERIFICADO.
- Polaridad/idle de P4C (perfil de pin usado por la placa; `0xcf3a`/`0x5b36`) — NO_VERIFICADO.
- Recepción de CAIF ID `0x0c` por Darwin / mensaje tipo 3 «`0x22`» — no demostrado.
- Efecto eléctrico real sobre el sensor / fin de integración — NO_VERIFICADO (S51).

### Separación hecho / inferencia

- **Hecho:** Darwin escribe `P4C←0` siempre (nunca ←1); tipo 0 suprime P4D/P4E y ADC; P4C no tiene consumidor localizado en `av-cam.bin`; el tipo de mecanismo no tiene escritor localizado; cableado P4C→`SENS_B`/`GPIO_9` verificado en esquema.
- **Inferencia fuerte (no demostrada):** la decisión física de accionar o no las cortinas mecánicas la toma el MCU Darwin vía parser CAIF + tipo de mecanismo; el par `SENS_B`+`GPIO_9` es el destino físico de P4C.

---

## 5. Próximo paso exacto concreto

**REA (prioridad 1, en solitario):** no coexistir con `rea.sock`/`rea-tema1`.

```
nohup python3 analysis/rea-independent/bin/session_daemon.py \
  analysis/rea-independent/run/rea-tema3.sock \
  '{"path":"/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin","format":"raw-binary","architecture":"arm","entry_point":"0x43541000","provider_id":"ghidra"}' \
  > /tmp/opencode/tema3-daemon.log 2>&1 &
```

esperar `…/run/rea-tema3.sock.ready`, luego:

```
python3 analysis/rea-independent/bin/q.py analysis/rea-independent/run/rea-tema3.sock /tmp/opencode/tema3-calls.json /tmp/opencode/tema3-out.jsonl
```

Lote ya preparado en `/tmp/opencode/tema3-calls.json`:
- `xrefs(0x43e77298)`
- `analyze_function`: `0x43b5e2bc`, `0x43b5e22e`, `0x43b5e29a`, `0x436bcef4`, `0x438c8104`, `0x438c240e`, `0x4383fd6c`, `0x43842158`
- `xrefs`: `0x43b5e2bc`, `0x43b5e29a`
- `search_bytes("50000020")` (literal `0x20000050` en `av-cam.bin`: se espera ausente; el byte de tipo vive en RAM de Darwin)

Cerrar con `q.py …/run/rea-tema3.sock --shutdown` y verificar que no queden procesos propios.

**Estático:** confirmar en el desensamblado A6000 que `0x436bcef4` escribe `0x43e77298…0x43e772cc` vía GOT y que ninguna de las 16 celdas es canal 9 (ya verificado en S55; repetir si se añaden regiones de código).

**Pasivo autorizado:** analizador lógico (solo lectura) en `GPIO_9`/P4C (CN4900) y `MSS_SO_DWN` durante una foto mecánica y una EFCS: confirma ID `0x0c`, polaridad, flanco y relación con la escritura `P4C←0` de Darwin.

No ejecutar firmware, no flashear, no pruebas físicas.

---
*Elaborado con evidencia estática verificada (S52–S55) y REA previa del proyecto sobre el mismo `av-cam.bin`. Todo en español. No se ejecutó nada en cámara ni se flasheó.*
