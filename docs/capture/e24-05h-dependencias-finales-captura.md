# E24-05h — Dependencias finales de la captura sin rearme: P29, P4E, BIONZ, modos Darwin y FAIL (27-10-2026)

Sesión 100 % estática: sin cámara, sin USB, sin escrituras de RAM/NAND/NVRAM, sin FDAT ni flasheo, sin tocar el watchdog ni protecciones físicas, sin parche instalable. Base `470f5180`. Continúa [E24-05g](e24-05g-ajustes-modo-ocupacion.md). **No autoriza parche ni flasheo; E24-04 no cambia. No se inicia E24-06.**

Binarios: `darwin_core.bin` 3.21 (SHA-256 `5f2be06d…0bf4`, base `0x4200`) y `av-cam.bin` (BIONZ, base `0x43541000`). Método: Capstone propio (decisivo) más una ejecución simbólica por ramas de las primitivas de GPIO (`Sym` en el script; el valor de `0x20c74` se modela como `T`, podado a 0 o libre). No se abrió sesión REA: el desensamblado propio resolvió todo lo decisivo. Reproducible: `python scripts/e24_05h/dependencias_finales.py` (→ `analysis/e24-05h/dependencias.json`, 2,4 s) y `pytest tests/test_e24_05h_dependencias.py` (19 pruebas nuevas; las de E24-05f/g no se duplican y siguen pasando: 50 en total).

## Veredictos A–I

| | Pregunta | Resp. | Naturaleza del NO / alcance exacto |
|---|---|---|---|
| **A** | ¿Red física y significado funcional de P29? | **NO** | *Evidencia insuficiente.* La red está identificada por nombre: `MSS_S2_REQ_CA`, de IC6000 (BIONZ) al pin `P29/INT05` de IC5700 (Darwin MB9AF004). Faltan polaridad eléctrica y qué condición de IC6000 la conduce; el pin del lado IC6000 es ambiguo en el manual (S21). §1 |
| **B** | ¿La espera del estado 31 termina sin rearme? | **NO** | *Evidencia insuficiente.* Hay **dos** variantes (corrige E24-05g). `S+0x32=0`: sale solo con P29 bajo, sin plazo. `S+0x32≠0` (la observada en T022: `0x1600`): sale cuando la FSM ADC-B (`0x29dc8`) termina, por temporizadores, sin leer P29. Ninguna lee el rearme; falta quién baja P29 y si ADC-B se arranca (`0x19b9e`). §1.3 |
| **C** | ¿Se evita la escritura a P4E en captura con `0x1fe66=0` y `0x20c74=0`? | **SÍ** (escritura estática) | Con `0x20c74=0` ningún cierre (estado 31, modos 0/1/2, manejadores de las FSM ADC) contiene una escritura a P4E ni a P4D; la compuerta `0x1fe66` es irrelevante para P4E. P4C sí se escribe. Límites: llamadas por puntero y estado inicial de arranque. §2 |
| **D** | ¿El modo 2 puede activar el mecanismo con el rearme omitido? | **NO** (con tipo 0) | Su cierre directo no escribe bobinas ni motor; llega (arista de baja confianza) a arrancar la FSM ADC-A, cuyos manejadores con tipo 0 solo escriben P4B y P56. Con tipo ≠ 0 esa FSM sí escribe P4D/P4E. §4 |
| **E** | ¿BIONZ y Darwin coinciden en cuándo transmitir `0x11/0x14`? | **NO** | *Evidencia insuficiente.* Se identifica el constructor BIONZ del `0x0c` pero no el del bloque 10 de la trama `0x31` ni la correspondencia modo Darwin ↔ tipo BIONZ (`[obj+0x23]`). §3 |
| **F** | ¿Semántica de FAIL y reintentos reconstruida? | **SÍ** (con límite de plazos) | FAIL no avanza la posición y se reintenta; no envía nada a BIONZ; no lleva por sí mismo a la operación 5. §5 |
| **G** | ¿Una foto individual completa estáticamente sin perder respuesta obligatoria? | **NO** | *Evidencia insuficiente* (eslabones de B y E; productor de `pkt[1]`, `pkt[2..3]`) |
| **H** | ¿Lo mismo en ráfaga? | **NO** | *Evidencia insuficiente:* G más clase 1 del `0x0b` (bit 24) |
| **I** | ¿Queda una dependencia de posición física que impida afirmar que el mecanismo puede permanecer inactivo? | **SÍ** | *No hay contradicción.* Sin bloqueo real demostrado; tampoco se demuestra su ausencia (§6) |

**Decisión de la sesión:** no se encontró ningún bloqueo real *demostrado* del protocolo ni del hardware para la captura sin rearme, y tampoco se demostró que no exista. Quedan tres eslabones que dependen de señales físicas o de BIONZ (§6). El análisis estático de terminación no es funcionamiento físico.

## 1. Mapa físico y lógico de P29

### 1.1 Red física (esquema `a6000_service_L3`)

| Dato | Valor | Fuente / estado |
|---|---|---|
| Pin | IC5700 (MB9AF004BGL «Darwin») `E5 = P29/INT05` | manual, texto vectorial (líneas con `P29/IINT05`); VERIFICADO por coordenadas |
| Red | `MSS_S2_REQ_CA` | idem; coincide con S21 H4 |
| Otro extremo | IC6000 (MHZ4G8G01A, BIONZ), pin ambiguo | S21: «pin IC6000 ambiguo» |
| Dirección | BIONZ → Darwin (el nombre `…_CA` agrupa también `CA_RELEASE_LOCK_MSS` P4B y `CA_1ST_CURTAIN_START` P4C, que salen de Darwin hacia IC6000: la familia `_CA` se refiere al lado «CA» y no fija el sentido por sí sola) | INFERENCIA (nombre) — el sentido BIONZ→Darwin viene de S21 |
| Origen: sensor/obturador/circuito propio | **No consta**; el esquema no lo asigna a un sensor del obturador | NO_VERIFICADO |
| Polaridad eléctrica | **No demostrable offline** | NO_VERIFICADO |

Código: `PDIR2.9` = bit-band `0x124` (`puerto = off//0x80`, `bit = (off%0x80)//4`). Lectores directos de ese literal: solo `0x1ec9c` y `0x7c8a`. No hay lector de interrupción (`INT05`) localizado: el código sondea por PDIR. La configuración de P29 en la inicialización (tabla de funciones `0x2675c`, rutina `0x5512`) no se decodificó: límite.

### 1.2 Lectores y nivel (VERIFICADO por bytes)

`0x16c44` y `0x16c54` devuelven **1 si y solo si P29 está bajo** (`cbz/cbnz` sobre `0x1ec9c`; bytes en la prueba). Lectores:

| Contexto | Sitio | Uso del nivel bajo |
|---|---|---|
| Espera del estado 31 con `S+0x32=0` | `0x1905e` (`0x18fa0`) | **condición de salida** |
| Espera del estado 31 con `S+0x32≠0` | `0x18f10` (`0x18d6e`) | solo evento: ejecuta `0x1a910/0x1a936/0x19960` (→ `0x20492` consulta de ADC-B). No es salida |
| Tarea de captura, cada toma | `0x1819a` (`0x1811a`) | elige el código de estado 0x81 (bajo, y `0x1ec52(2)=0`) o 0x80 que se publica con `0x1e5f2(0x90,…)` |
| Arranque de la tarea `0x7de2` | `0x7ed2` | bucle hasta P29 bajo antes de seguir el arranque |
| Tarea de modo/trama `0x7c8a` | `0x7d12` | con P29 bajo y `0x11852()=0` llama `0xe1a2` (secuencia de potencia, tabla `0x20002c14`) |

Los cuatro contextos tratan el nivel bajo como la condición «esperada»; eso **no** prueba el significado (el nombre sugiere una petición de S2 originada en BIONZ, pero un estado de reposo/listo daría el mismo código).

### 1.3 Dos variantes de la espera del estado 31 (corrige E24-05g)

Selector: `0x1911e ldrh [S+0x32]` → `0==` `0x18fa0`, `≠0` `0x18d6e`. `S+0x32` = `pkt[2..3]` del `0x0c` (§3). **En T022 (RAM, después de un disparo real) el paquete contiene `pkt[2..3] = 00 16` → `S+0x32 = 0x1600`**; con `S+0x32 ≥ 0x1400` la espera es la rama `0x18f88` (bucle puro `0x203ae`). Es una sola muestra posterior al disparo; no prueba qué valor tenía durante la captura.

| | `0x18fa0` (`S+0x32=0`) | `0x18d6e` (`S+0x32≠0`) |
|---|---|---|
| Condición de salida | P29 bajo (`0x1905e → 0x190da`): único salto que abandona el bucle (prueba) | `0x203ae` ≠ 0 (`0x18f86→0x18f90`): FSM ADC-B (`0x29dc8`) en su estado final 7 (`0x1e16e`) |
| Depende de P29 | Sí | No (solo evento) |
| Acciones previas | `0x198bc` (si `0x19b9e≠0`: arranca ADC-B, `0x202f2`), `0x93e6` marcas | `0x19948 → 0x2041e(r8)` (`r8` = duración derivada de `S+0x32`), `0x198bc`, y paso de bobina `0x19978 → 0x20544` si el tiempo cae en `≤ 0xc8` |
| Umbrales (unidad del tick `0x93e6` **no medida**) | 5000 (referencia de `0x941e`), 50000 (reinicia `r7`, sin otro uso), **250000 y 25000**: petición de modo 2 (`0xd34e(0)`) + `0xd35a` repetida; **500000** desde la entrada: una vez, `0x1667e`(cola a `0x1e060`) condicionado y `0x2418c` (indicador `0x20002eb4`=2) | 50000/60000 (reparto del tiempo), 250000 y 25000: petición de modo 1 (`0xd34e(1)`) repetida; contador `r4` |
| Plazo final | **Ninguno**: ni 500000 ni los demás salen del bucle | Ninguno propio; termina si ADC-B termina |
| Tras salir | `0x1b308`, `0x1a7e8`, `0x19932` (→ `0x2041e(0)` si `0x19b9e≠0`), `0x2419c`: si el indicador es 2 lo pasa a 4 | similar, más `0x16932` hasta 0 |

**Qué pasa si P29 queda indefinidamente en cada nivel (variante `S+0x32=0`):** bajo → sale al instante (nivel esperado). Alto → no sale nunca; cada 250000 ticks reitera la petición de modo 2/`0xd35a`; BIONZ queda en `caif_recv` sin plazo (E24-05d). No hay escalado a operación 5 ni FAIL en este bucle (§5). En la variante `S+0x32≠0` el nivel de P29 es irrelevante para salir.

**¿Omitir el rearme impide el cambio de P29?** No hay nada en Darwin que lo ligue: la rutina de rearme no escribe ningún pin que alimente IC6000 salvo `P4B/P4C` (señales `CA_*` hacia IC6000, igual en ambas rutas). Una dependencia indirecta (IC6000 conduce P29 según algo que ve del obturador) **no se puede excluir** (A/B/I).

## 2. Escrituras a P4E (2ND_CURTAIN_MG, `0x238`)

Todas las escrituras `bl 0x51c0` con `r0=0x238` están en cinco funciones (únicos inmediatos `0x238` del core: `0x20ce4, 0x20d10, 0x20d4c, 0x20e6a, 0x20ec0, 0x20f70`; ningún literal `0x238`; única escritura por máscara PDOR `0x51f2`: `0x20e3e`). Resultado de la ejecución simbólica (`p4e` en el JSON):

| Función | Efecto con tipo ≠ 0 | Con `0x20c74 = 0` | Alcanzable desde |
|---|---|---|---|
| `0x20cd4` | P4E=0 | nada (`beq` a `ret`) | `0x1f68a, 0x206ec, 0x207be, 0x207e8` |
| `0x20d00` | P4E=1 | nada | `0x2041e`, `0x203b2`, `0x20aa4` (ADC-B estado 4) |
| `0x20d26` (paso `−n`) | P4E=1, P4D, P4C | **solo P4C=0** (`0x20df6`) | `0x20544` ← `0x19978` |
| `0x20e0e` (paso 0) | P4E=1 (`0x20e6e`), P4E/P4D por `0x20e3e`, P4D | **solo P4C=0** (`0x20e6e`, entra con `r0=0x230`) | `0x20544` |
| `0x20e98` (paso `+n`) | P4E=1 (`0x20ef6`), P4D, P4C | **solo P4C=0** (`0x20f34`) | `0x20544` |

* **Condición para alcanzar `0x2041e`:** `0x19932`/`0x19948` la llaman solo si `0x19b9e() ≠ 0` (`0x165c8(0x10)`: bit 4 de `S+0x444` a 0, y bit 0 de `S+0x170` a 0). Con `0x2041e(0)`: `0x20d00` + arranque de ADC-A; con `≠0`: arranque de ADC-B (`0x20484`).
* **Qué decide `0x20c74`:** `T = [0x20000050+canal] & 7` si `[0x200002c0+canal]≠0` (`0x1b080`); `1..3` pasan, otro valor → 0. El FDAT tipo 0 de T024 reescribe esa decisión: siempre 0.
* **Otros caminos que escriben P4E:** ninguno en captura, fin ni recuperación según los cierres. Los escritores genéricos de `0x51c0` con `r0` variable que aparecen en los cierres están resueltos por constantes internas (`0x2b8`, `0x190`, `0x194`, `0x230`…), ninguno `0x238`; `genericos_sin_resolver = []` en todos.
* **Cierres con tipo 0:** el estado 31 (ambas esperas), los modos 0/1/2 y los manejadores de ADC-A/B/C **no escriben P4D ni P4E** (P4E/P4D solo con tipo ≠ 0). Siguen escribiéndose: **P4C** (`0x1ecec`; se fija a **1** en cada toma, `0x17cee`, y en `0x175ea`; se borra en `0x16e68`), **P4B** (máscaras de ocupación, `0xd116/0xd18e`) y salidas ajenas al obturador (P0C, P35, P5E…).
* **Condiciones que dejarían una bobina accionada:** solo con tipo ≠ 0: `0x20d00` pone P4E=1 y la liberación es `0x20cd4` (estado 3 de ADC-B `0x20a8a`) o el siguiente paso de bobina. la liberación P4E=0 es `0x20cd4` (llamada desde `0x1f68a` y las rutinas de ADC-A `0x206ec/0x207be/0x207e8`) o el siguiente paso de bobina; si no se ejecutara tras `0x20d00`, quedaría a 1 hasta entonces. Con tipo 0 no aplica.
* **¿Depende de P29?** La escritura a P4E en `0x2041e` ocurre *al salir* de la espera P29 (variante 0), de modo que el nivel de P29 gobierna *cuándo*, no *si* (el «si» lo gobierna `0x20c74`). **¿Restablece automáticamente la salida?** No hay restauración por cambio de estado en el código estático; la salida a 0 la escriben `0x20cd4/0x20d26/0x20e98` según la secuencia.
* **Escritura de GPIO ≠ movimiento físico:** el sentido eléctrico del `1` y el movimiento real de la cortina no están demostrados. T024–T039 (tipo 0 instalado, 40+ disparos con `done`) muestran que el firmware tipo 0 completa capturas con el rearme **activo**: no prueban funcionamiento sin rearme. Estado inicial de P4E tras el arranque: **no analizado**.

## 3. Contrato BIONZ/Darwin del paquete `0x0c` (22 B)

Constructor BIONZ: `0x438d0064` (`obj`=r4), llamado desde `0x438d034a` (envío por `0x438d033c`, subclase 1, carga `[obj+0x4ad8]`) y `0x438d042c`; se ejecuta **en cada envío** (también en cada reintento de la clase 1 del `0x0b`), es decir, **por fotografía**, no en la inicialización. Darwin lo copia en cada admisión (`0x17f8c`).

| `pkt[]` | Productor BIONZ (`0x438d0064`) | Copia Darwin (`0x17f8c`) | Uso Darwin | Estado |
|---|---|---|---|---|
| 0 | `*[carga+0x20]` (byte) | `S+0x30` | admisión (`pkt[0]=0`) | VERIFICADO |
| 1 (clase) | **no escrito aquí**; T022: `2` | `S+0x31` | bits 0–1 reescritos por `0x19b5e` según el tipo; bits `0x30` y bit 7 del arrancador por disparo | productor NO localizado |
| 2–3 (`u16`) | **no escrito aquí**; T022: `0x1600` | `S+0x32` | **selecciona variante de espera** (§1.3) y fuerza `S+0x3c=0` si es 0 | productor NO localizado |
| 7 | `obj[0x1e0]` (id de estado/modo BIONZ, 0–0x20) | `S+0x37` | — | VERIFICADO |
| 8–9 | `u16 [obj+0x1450]` | `S+0x38` | — | VERIFICADO |
| 0xc | tipo `r6` ∈ {1,2,3,4} (0 si estado no mapeado) `\| 0x80` si estado 0x20, `\| 0x40` si estado 0x1f o `obj[0x6c8]=1` | `S+0x3c = pkt & 0x3f` (si `S+0x44.b0=0`; cero si `S+0x32=0`) y bits 6–7 → `S+0x46` bits 2–3 | **elige la lista de la máquina de 49 estados** (`0x1961c`: 1→listas «tipo 1», 2/3/4→«tipo 2–4», otro→lista por defecto `0x28f88`) | VERIFICADO |
| 0xd | bit 0 = `obj[0x4b80]∈{1,2}` (consulta de modo del obturador `0x437f9a64`); bit 1 = condición con `obj[0x4b8d]`, `[…+0x61]==2`, `0x43ae7648` | `S+0x3d` | T022: `0x40` | bit 0 INFERENCIA (nombre del dato no consta) |
| 0xe | `obj[0x4b68]−obj[0x1d8]` (u8), `0xff` si `obj[0x4b68]=0`; 0 si el tipo es 0 | `S+0x3e` | — | VERIFICADO |
| 0x12 bit 3 | `¬0x43af0b7c()` | `S+0x42` bit 3 | — | VERIFICADO |

Mapa BIONZ `obj[0x1e0]` → tipo `r6` (`tbb` de `0x438d0084`): estado 1 → 1 ó 2 según `obj[0x4b95]`; 2 → 2 ó 1 según `0x436e8328()`; **7 → 4**; **8, 20, 27 → 3**; **5, 9, 19, 24, 31, 32 → 2**; 0, 3, 23, 25, 26, 28 → 0; 4, 6, 10–18, 21, 22, 29, 30 → 0 con traza de error. Qué componente BIONZ fija `obj[0x1e0]` no se trazó.

* **Solicitudes de ajustes:** el bloque 10 de la trama `0x31` (gancho `0x1c04c`) y el arranque por disparo siguen sin productor BIONZ localizado; el correspondiente a `0x11/0x14` queda **sin cerrar** (E).
* **EFCS:** ningún campo del `0x0c` está identificado como EFCS ON/OFF; `pkt[1]` (clase) y `pkt[0xd]` son candidatos. No se asignan valores no medidos.
* **Campos que seleccionan la secuencia mecánica:** `pkt[0xc]&0x3f` (tipo → lista), `pkt[2..3]` (variante de espera y habilitación del tipo), `pkt[1]` (reescritura de clase), y los datos `[0x20000050+canal]`/`[0x200002c0+canal]` (compuerta `0x1fe66` y tipo `0x20c74`), que no vienen del `0x0c`.

## 4. Modos 0/1/2 de Darwin (parte D)

| | Modo 0 (`0x126b0`) | Modo 1 (`0x1263c`) | Modo 2 (`0x1262e`) |
|---|---|---|---|
| Activación | código 0 de `0x1b290`: estado 27 tras el `0x10` de **cada captura** | código 1: `0x18d6e` (variante `S+0x32≠0`) tras 250000/25000 ticks | código 2: `0x18fa0` (variante `S+0x32=0`), idem |
| Comunicación BIONZ | tramas `0x30/0x31`, **`0x17`** | tramas; no emite `0x17` | `0x1cb0e(1)`, `0x1cebe`, `0xd044` y luego el modo 1; no emite `0x17` |
| Fin | `0x17` publicado | salida `0x126a0` | idem |
| Cierre de llamadas directas | 207 funciones | 216 | 277 |
| GPIO escritos (cierre) | P09, P0C, P3B, **P4B**, P5D, P5E | idem | P0C, **P34** (`0x1c4bc`), P4B |
| ¿Bobinas / motor? | no (P4C/P4D/P4E/P40/P41 ausentes) | no | no; arranca **ADC-A** por una arista de baja confianza (`0x1cb0e→0x1cfc4→0x19798→0x20048→0x1e51a→…→0x2035e`, barrido lineal) |
| Dependencia de tipo / GPIO / ADC | ninguna directa | ninguna | `0xcf14(4)` (presencia) y `0x20c74` |
| Si el modo falla | BIONZ espera `0x17` sin plazo (`0x438d0be4`); Darwin plazo `0x7148` de la trama | se reitera la petición | se reitera |

ADC-A con tipo 0: manejadores solo escriben P4B (`0xd116/0xd18e`) y P56 (`0x24330`); con tipo ≠ 0: P4D y P4E. ADC-B con tipo 0: P0C, P4B, P4C; con tipo ≠ 0 también P4D/P4E. ADC-C: P0B.

## 5. Semántica de FAIL (parte E, motor `0x1e234`/`0x1e33e`)

Estructuras (VERIFICADO por bytes): el contexto es el búfer local de 0x14 B de `0x1e33e` (`ctx+0x10` = halfword de banderas); los manejadores de estado lo rellenan y `0x1e234(desc, ctx)` lo interpreta.

| Bit de `ctx+0x10` | Escritor | Efecto en `0x1e234` / `0x1e33e` |
|---|---|---|
| `0x40` «hecho» | `0x1e4aa` | `0x1e322–0x1e328` → devuelve 1 ⇒ `0x1e3ca/0x1e3cc` **continúa** el bucle (ejecuta el siguiente estado en la misma llamada) |
| `0x80` **FAIL** | `0x1e4c2` | `0x1e25c lsls #0x18; bmi 0x1e2b6` **salta el avance** (`0x1e264–0x1e284`): la posición en la lista no cambia; se procesan los temporizadores del contexto y la función devuelve (0 salvo bit 6) |
| `0x100` salto | escritor no identificado | busca el id destino en la lista (`0x1e294`) |
| `0x1/0x2/0x4` + `0x200/0x400/0x800` | `0x1e3d2`, `0x1e424` | armar/anular temporizadores 0–2 con plazo |

* **FAIL no detiene, no salta y no completa:** *reintenta el mismo estado en la siguiente invocación del motor*, normalmente por temporizador. Es el idioma de sondeo («no listo»).
* **No envía mensaje a BIONZ** ni activa por sí mismo la operación 5 ni el freno P4=3: esa operación nace del notificador de errores `0x16558` o de la orden BIONZ `0x3e` (`0x1bf38`), vías distintas (E24-05).
* **Estados con FAIL directo** en la máquina interior de 49: 3, 6, 7, 8, 10, 12, 13, 15, 20, 22, 23, 25, 26, 28, 30, 32, 34. **Ninguno** de los 5 ids de la máquina exterior (`0x29cf0`) puede devolver FAIL.
* **Estado 26** (`0x17564`): FAIL + temporizador `0xc8` mientras `S+0x14` no tenga los bits 1 y 2. Bit 2 lo pone `0x17044` (desde el manejador de mensajes `0x1eb92`, o sea, **al llegar un mensaje de BIONZ**); bit 1 lo pone `0x17024` (estado 31 `0x19228` y `0x19370`). Si el mensaje no llega, Darwin sondea indefinidamente y BIONZ queda en `caif_recv` sin plazo: dos esperas mutuas sin plazo propio (watchdog **no cerrado**, E24-04).
* **Primera toma / ráfaga:** los bits de `S+0x14` persisten entre tomas y se reponen (`0x17064` fija el bit 3 en el estado 31); la primera toma y la ráfaga no difieren en el motor. La clase 1 del `0x0b` (E24-05g) añade hasta 19 reintentos de BIONZ.
* **Protecciones:** el camino sin rearme no omite `0x16558`, `0x1e4c2` ni los reintentos; el gate `0x1fe66` solo cambia la lista exterior. Ninguna protección original se desactiva en este análisis.

## 6. Escenarios y diferencias demostradas

| | 1 Convencional (`0x1fe66≠0`, `0x20c74∈1..3`) | 2 Sin rearme (`0x1fe66=0`, `0x20c74=0`) | 3 Sin rearme con fallo (P29 fijo / FAIL / respuesta tardía) |
|---|---|---|---|
| Inicio | `0x17f8c`: `0x0b` (clase) → BIONZ envía `0x0c` → admisión | igual | igual |
| Mensajes Darwin→BIONZ | `0x0b,(0x11,0x14),0x0d,0x15,…,0x0e,0x10,0x17(modo 0)` | **mismo orden** (los cinco primeros no leen la compuerta) | igual hasta donde llegue |
| Máquina de captura (49) | lista por `pkt[0xc]`/`S+0x32` | **idéntica** | estado 26/31 pueden quedar esperando |
| Máquina exterior | `L1/L2/L3\|L0`: rearme, motor | `L0=[0,7,8,9,10]`; sin motor salvo freno de la operación 5 | idem |
| GPIO | P4C=1, P4D/P4E por `0x20d00/0x20d26…`, motor P40/P41, P4B | P4C=1, P4B; **sin P4D/P4E**, sin P40/P41 | idem; P4C=1 ya fijado en cada toma |
| Esperas | estado 31: P29 (si `S+0x32=0`) o ADC-B; estado 26 por mensaje BIONZ; leva/motor en la exterior | estado 31 y 26 **iguales**; desaparecen las esperas de leva/motor | P29 alto: `0x18fa0` no sale (reitera modo 2, `0x2418c`=2); ADC-B no arrancado (`0x19b9e=0`): no demostrado que `0x203ae` termine; mensaje BIONZ tardío: estado 26 sondea cada `0xc8` ticks sin plazo |
| Finalización | `0x17` (modo 0), bit 24 baja en el estado exterior 9 | igual | sin `0x17` ⇒ BIONZ bloqueado en el paso `0x438c2474` |
| Excepciones | op 5 + freno P4=3 (error `0x16558`/orden `0x3e`) | op 5 conserva el freno | sin escalado automático a op 5 por FAIL |
| Estado que recibe BIONZ | clase del `0x0b` (0/1/2) | idéntica (depende del bit 24 y de `S+0x43`) | clase 1 reintenta ≤19 y después error `0x43ae7636(obj,1)` |

**Diferencias demostradas (1 → 2):** solo la lista exterior y, con `0x20c74=0`, la ausencia de P4D/P4E. No difieren: mensajes, orden, máquina de captura, estado 31, estado 26, ni los umbrales de tiempo.

**Eslabones físicos o de BIONZ que quedan** (cerrados *con límite*, sin prolongar el análisis):

1. **Quién conduce `MSS_S2_REQ_CA` (P29) y con qué nivel** (A/B): solo en IC6000 y esquema; no sale del firmware de Darwin ni de `av-cam`. *Experimento mínimo futuro* (no ejecutado, 100 % pasivo): analizador lógico en P29 junto con P4B/P4C y el CAIF durante un disparo normal, sin tocar el firmware.
2. **Valor de `pkt[2..3]` y `pkt[1]` durante la captura y su productor BIONZ** (E/G): lectura de RAM de solo lectura de la carga `[obj+0x4ad8]+0x40..0x55` *durante* el disparo, con el método de T022 (ya autorizado como solo lectura).
3. **Terminación de ADC-B si `0x19b9e()=0`** y estado inicial de P4E tras el arranque (I): no determinables sin ejecución. → ADC-B y P29 cerrados con límite en [E24-05h-3](e24-05h-3-adcb-p29.md).

## 7. Correcciones respecto a E24-05g y anteriores

* E24-05g §2.3: «la salida de la espera del estado 31 es `0x16c44`» solo vale para la variante `S+0x32=0`; la variante `S+0x32≠0` (observada en T022) sale por ADC-B.
* E24-05g §6/§5: el bit 7 de `ctx+0x10` queda resuelto (§5); «FAIL pendiente en `0x1e33e`» deja de estar pendiente.
* P4C se fija a 1 en cada toma (`0x17cee`) con cualquier tipo de bobina: «tipo 0 evita las salidas de cortina» es cierto para P4D/P4E, no para P4C ni P4B.

## 8. Evidencia reproducible

| Hecho | Prueba (`tests/test_e24_05h_dependencias.py`) |
|---|---|
| P29 = PDIR2.9; solo `0x1ec9c`/`0x7c8a` leen el literal | `test_p29_es_pdir2_bit9_…` |
| `0x16c44/0x16c54` = «P29 bajo» | `test_wrappers_de_p29_…` |
| Única salida del bucle `0x18fa0` | `test_espera_estado31_con_s32_cero_…` |
| Variante `S+0x32≠0` sale por ADC-B | `test_espera_estado31_con_s32_distinto_…` |
| Umbrales 5000/25000/50000/250000/500000 | `test_umbrales_de_la_espera_de_p29` |
| P4E/P4D solo con tipo ≠ 0 | `test_p4e_solo_se_escribe_…`, `test_con_tipo0_la_unica_salida_…` |
| Único conjunto de inmediatos `0x238` | `test_no_hay_otro_inmediato_ni_literal_0x238` |
| Cierres sin P4D/P4E con tipo 0 | `test_cierre_del_estado31_…`, `test_modos_0_1_2_…`, `test_modo2_alcanza_la_fsm_adc_a_…` |
| P4C=1 por toma | `test_p4c_se_fija_a_1_…` |
| Semántica de FAIL | `test_fail_no_avanza_…`, `test_estados_interiores_con_fail_…` |
| Constructor BIONZ y `tbb` | `test_constructor_bionz_…`, `test_tipo_bionz_de_darwin_…` |
| Copia Darwin del `0x0c` | `test_darwin_no_copia_pkt_0xc_a_s_0x3c_…` |

Límites: cierres sobre `bl/b.w` directos (barrido lineal; aristas espurias posibles, p. ej. la de modo 2 → ADC-A); no se resuelven llamadas por puntero salvo las tablas de manejadores de las FSM; no se ejecuta ni emula nada; la unidad del tick `0x93e6` no está medida; el constructor del bloque 10 de la trama `0x31` y la configuración inicial de P29/P4E quedan fuera.
