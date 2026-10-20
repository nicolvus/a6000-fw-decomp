# S21 (Claude): pulsación del disparador → orden de movimiento de cortinas

Análisis estático de Sony A6000 3.21. No se usó la cámara, no se flasheó nada y no se
modificaron binarios. Direcciones LIRO = VA de `av-cam.bin`, con base `0x43541000`;
el ELF de vista tiene `.text` en el offset `0x1F0`. Darwin = ROM con base `0x4200`.
libObj y `input.ko` usan VA/offset ELF. **SilentShutter no se declara funcional.**

Evidencia reproducible: `analysis/session21/evidence/claude-button-to-shutter.py`. Valida
SHA-256 y comprueba cada hecho con un `assert`, y escribe `claude-button-to-shutter.json`.
Resultado: PASS; ruff y mypy sin avisos.

## 0. Reutilizado frente a verificado ahora contra el binario

| Fuente previa | Uso en S21 |
|---|---|
| `shutter-trigger-state-machine.md` (C-01..C-05), `shutter-trigger-chain-0x3011.md` | RelMgr `0x4379d838`, `0x4379e6a8`, `0x4379eba0`, CaptureStart. **Re-verificado**: `0x3011`, BL y literales. **Corregido**: cola destino |
| `s19-s2-domain-bridge.md`, `s19-mechanical-shutter-decision-points.md` | dispatcher `0x43807f4c`→`0x43807d80`→`0x43809ed8`. **Re-verificado**: BL y GOT `0x44021ed0=0x437df641`. **Corregido**: dirección de la tabla de estado |
| `s20-p1-mailbox40193-rpc-pattern.md`, `s20-mailbox40193-osal-architecture.md` | tabla de 35 filas. **Corregido**: dirección real y receptor localizado (se retira «no reconstruible») |
| `s18-main-init-437ebed8.md`, `a6000-all-exposure-sequences.json` | filas de `0x43edccf8`, pseudocódigo de las 17 secuencias. **Verificado**: tabla `0x43eddd08` y su selector |
| `efcs-capture-selector.md`, CONTEXT (puente EFCS→paquete, parser Darwin `0x17f8c`, bit `0x20` A6300) | Reutilizado sin repetir la emulación. Clasificación heredada |
| `fm3-gpio-shutter-mapping.md`, `darwin-state-machine.md` | P4D/P4E. **Re-verificado**: puerta `0x20c74` y escrituras `0x20c90/0x20cb2/0x20cd4/0x20d00` |
| `scripts/schematic_pin_nets.py` (método) y manual `a6000_service_L3.pdf` | Redes nuevas S1/S2 y MSS_S2_REQ_CA |
| Desensamblado libObj previo (scratchpad) | Productores de `0x4042..0x4045` y receptor InfraInput |

Herramientas: llvm-objdump (Thumb), Python stdlib y pdftotext. No se abrió ni modificó Ghidra.

## 1. Correcciones a documentos previos (VERIFICADO)

1. **El mensaje `{tipo 2, 0x3011}` de RelMgr NO va a la cola `0x40193`.**
   - `0x4379eba0` llama `0x43aeaf18(msg, r1=0x30001, r2=0x40193)`.
   - `0x43aeaf18` hace `Alloc(r1)` y `0x43aeaedc(buf, r2)`, copia 24 B y ejecuta `Send(r5=r1)`.
   - El **destino es `0x30001`** (cola de CamMgr). `0x40193` es el campo de origen/respuesta.
   - Afecta a `shutter-trigger-chain-0x3011.md`, `shutter-trigger-state-machine.md` C-01 y `s19-*`.
2. **Tabla de 35 filas: dirección real `0x44000174`, no `0x43ffff84`.**
   - La dirección anterior tenía un desfase de −`0x1F0`: se leyó el ELF de vista por offset de archivo.
   - El puntero `0x43aeaa4b` solo aparece en `0x44000178`.
   - En la misma tanda, la tabla de estado citada como `0x43fcd5b4/0x43fcd5d0` es en realidad
     **`0x43fcd3c4/0x43fcd3e0`**. La tabla de 220 filas `0x43fff30c` sí era correcta: tiene una referencia PIC en `0x438052f2`.
3. **El receptor de `0x40193` SÍ es localizable estáticamente: `0x4381d16c`.**
   - El literal en `0x4381d1d8` vale `0x00040193`; s20 lo había clasificado como emisor.
   - Ejecuta `Receive(0x40193,-1)`, compara el id u16 de `msg+2` con las 35 filas (`cmp r4,#0x23`) y llama al
     manejador como puntero a miembro. Al terminar ejecuta `Free(0x40193)`.
   - Queda retirada la conclusión de s20 de que el receptor era «no reconstruible sin traza dinámica».

## 2. Cadena pulsación → orden de cortina

| # | Etapa | VA / archivo | Clasificación |
|---|---|---|---|
| H1 | Interruptor S0019: `XS_1` (1st) y `XS_2` (2nd), `S1S2_GND` | manual pág. 48, flex pines 32/31 | VERIFICADO (texto vectorial) |
| H2 | `XS_1`→IC6000 `GPIO_S_11` (L15, vía D1100); `XS_2`→IC6000 `GPIO_S_13` (L14) | pág. 26 | VERIFICADO por coordenadas; inspección visual pendiente |
| H3 | `XS_1` también llega a Darwin IC5700 `P32/INT10` | pág. 23 | VERIFICADO por coordenadas; uso en firmware NO_VERIFICADO |
| H4 | `MSS_S2_REQ_CA` (IC6000→Darwin `P29/INT05`), `DWN_IN_RELEASE` (→`P06/INT30`), `CA_RELEASE_LOCK_MSS` (Darwin P4B→IC6000 `GPIO_S_7`) | págs. 23/24/26 | VERIFICADO por coordenadas (pin IC6000 de MSS_S2_REQ_CA ambiguo); productor y consumidor en firmware NO_VERIFICADOS |
| K1 | `input.ko` (`getkey_gpio` → `gpio_get_data_bit`) envía eventos `{type,code,value,opt}` a la cola `0x7a0020` | `input.ko` `.text+0xb24..0xba8`, literal `+0xc44` | VERIFICADO (cola y cadena de log). Asignación GPIO→código: tabla `key_tbl` en Backup, NO_VERIFICADA |
| K2 | libObj `InfraInput` recibe `0x7a0020` (`osal_rcv_msg_tmo`) | libObj `0x806b24`, literal `0x806dac` | VERIFICADO |
| K3 | libObj envía a LIRO `{tipo 5, id 0x4042/0x4043/0x4044/0x4045, +8 = índice 0x0b/0x14/0x0c o 0x0a/0x06}` → cola `0x40193` | libObj `0xaf927c..0xaf93f2` | VERIFICADO (envíos). Unión K2→K3 por la lógica interna de libObj: INFERENCIA |
| L1 | Receptor `0x4381d16c` → tabla `0x44000174`: `0x4042→0x4379e47c` (RelMgr ev. 3), `0x4043→0x4379e3fc` (ev. 4), `0x4044→0x43aeaa4a` (ev. 1), `0x4045→0x43aea9f0` (ev. 2) | av-cam | VERIFICADO (tabla y BL a `0x4379d838`). Valores de evento: lectura de `movs` previos, INFERENCIA fuerte |
| L2 | RelMgr `0x4379d838` → admisión `0x4379e6a8` → `0x4379eba0` `{2,0x3011,corr,idx}` → **cola `0x30001`** | av-cam | VERIFICADO |
| L3 | Bucle CamMgr `0x437fee08`: `Receive(0x30001)`. Tipo 0/2 → `0x43809148`; tipo 5 → tabla de 220 filas `0x438052d8` | av-cam | VERIFICADO |
| L4 | `0x43809148`: TBH sobre `id−0x3000`. **`0x3011` → `0x43809254`**: envía aviso `0x8202` y después el **código local `0x100`**, ambos a la cola `0x302d9` (`0x438090e0`). `0x3012→0x101`, `0x3013→0x102`, `0x3014→0x8204+0x104`, `0x3015→0x8201+0x103` | av-cam | **VERIFICADO (puente S2 que faltaba)** |
| L5 | Receptor `0x302d9` en `0x43809908` → `0x43807008(sm,msg)` = `sm[msg[0]]->vtbl[0](msg+4)` → estado con handler `0x43807f4c` (puntero en `0x43fcd3e0`) | av-cam | VERIFICADO (bucle, despacho y registro). Que el estado activo sea ese en tiempo de ejecución: INFERENCIA |
| L6 | `0x43807f4c` caso `0x100` → `0x43807d80` → guardas → `0x43809ed8` → callback `0x437df641` (CaptureStart) por `0x439018b0` | av-cam | VERIFICADO |
| L7 | CaptureStart `0x437df640` → `0x437df338` → **selector externo `0x437eabfc`** (tabla `0x43edccf8`) → `0x43b04730(Image)` | av-cam | VERIFICADO |
| L8 | `0x437eabfc` solo devuelve las filas `+0xa0,+0xb4,+0xc8,+0xdc,+0xf0,+0x104,+0x118` (y `+0x12c` si `cap+0x4b70==7`) | av-cam `0x437eac0e..0x437eac86` | VERIFICADO |
| L9 | Las 7 filas `+0xa0..+0x118` hacen **BL a `0x438c2538` (Stage_CaComm)** | `0x43b1be54/beb6/bf22/bf84/bfe6/c052/c0b2` | VERIFICADO |
| L10 | `0x438c2538` → `0x438d033c` (si `cap+0x74f≠0`) → **CAIF evento 1** (`0x436b8a50`: 22 B de parámetros, cabecera `03 01`, `0x436ba234`) y **evento 3** (mensaje interno tag `0x12` a la cola de la tarea CA `0x1502c7`). Reintentos `CA_CaptureReq_RETRY`/`Capture_Cancel` en `Stage_CaComm.cpp` | av-cam | VERIFICADO (BL, TBB `0x437db89e`, literales). Semántica «petición de disparo» por cadenas: INFERENCIA fuerte |
| L11 | Tarea CA: `Receive(0x1502c7)` en `0x436ba0fc` → máquina `0x436bc140` → SIO3 hacia Darwin (protocolo CAIF previo) | av-cam | VERIFICADO (receptor). Codificación tag→trama: NO_VERIFICADA |
| L12 | Selector de exposición `0x437ea8cc` → tabla `0x43eddd08`, que contiene las 17 secuencias `0x43b1ae02..0x43b1b30e` (inicializador `0x437ebed8`) | av-cam | **VERIFICADO (nuevo)**: la tabla que llena el inicializador es `0x43eddd08` |
| D1 | Darwin: parser `0x17f8c` (22 B) → planificador/fases | darwin | Reutilizado (CONTEXT, emulación 512/512) |
| D2 | **Orden eléctrica de cortina**: `0x20c90/0x20cb2` → `0x42668234` (P4D, `1ST_CURTAIN_MG`) y `0x20d00/0x20cd4` → `0x42668238` (P4E, `2ND_CURTAIN_MG`), mediante `0x51c0` | darwin | VERIFICADO |
| D3 | Puerta `0x20c74 = 0x1b080(0)&7 ∈ {1,2,3}`. P4D se escribe solo con los tipos 1/2 (el tipo 3 queda excluido); P4E con 1/2/3; con el tipo 0 no hay ninguna escritura | darwin | VERIFICADO |

## 3. Diagrama del tramo

```text
[S0019] XS_1 ──┬─> IC6000 GPIO_S_11 ─┐                       (H1-H3)
               └─> Darwin P32/INT10   │ (uso NO_VERIFICADO)
        XS_2 ────> IC6000 GPIO_S_13 ─┤
                                     v
 input.ko getkey_gpio ──osal──> cola 0x7a0020                (K1)
                                     v
 libObj InfraInput 0x806b24 ··(INFERENCIA)··> envía 0x4042/43/44/45 → cola 0x40193   (K2-K3)
                                     v
 LIRO receptor 0x4381d16c → tabla 0x44000174 → RelMgr 0x4379d838 (ev 1/2/3/4)    (L1)
   └─ admisión 0x4379e6a8 → 0x4379eba0 {2,0x3011} ──> cola 0x30001                (L2)
 CamMgr 0x437fee08 → 0x43809148 [0x3011→0x100] ──> cola 0x302d9                   (L3-L4)
 0x43809908 → 0x43807008 → estado 0x43807f4c [0x100] → 0x43807d80 → 0x43809ed8   (L5-L6)
   └─ CaptureStart 0x437df640 → 0x437df338 → selector 0x437eabfc                  (L7-L8)
        └─ fila +0xa0..+0x118 → Stage_CaComm 0x438c2538 → 0x438d033c              (L9-L10)
             ├─ CAIF ev1: paquete 22 B (clase EFCS en byte 12) → 0x436ba234
             └─ CAIF ev3: tag 0x12 → tarea CA 0x1502c7 → SIO3                     (L11)
                         v
 Darwin parser 0x17f8c → fases/planificador → 0x20c74 (tipo HW)                   (D1-D3)
   ├─ P4D 0x42668234 (1ST_CURTAIN_MG, tipos 1/2) → Q6832 → bobina 1C
   └─ P4E 0x42668238 (2ND_CURTAIN_MG, tipos 1/2/3) → bobina 2C
 Línea paralela: IC6000 ─MSS_S2_REQ_CA─> Darwin P29/INT05 (función NO_VERIFICADA)
```

## 4. Quién da la orden de cortina y qué decide mecánico, EFCS u otra ruta

- **Orden lógica (VERIFICADO):** la emite la etapa LIRO `Stage_CaComm` (`0x438c2538`). Envía los
  eventos CAIF 0/1/3 por la tarea CA (`0x1502c7`), y esta los manda a Darwin por SIO3.
- **Orden eléctrica (VERIFICADO):** la ejecuta Darwin (FM3, IC5700) al escribir P4D/P4E. Cada pin
  gobierna un FET y una bobina de cortina (`fm3-gpio-shutter-mapping.md`).
- **Mecánico frente a EFCS (reutilizado, INFERENCIA fuerte):**
  - LIRO calcula la clase EFCS en `0x43842158` y la lleva a los bits bajos del byte 12 del paquete del evento 1.
  - En la A6000, Darwin decide qué bobina mover a partir de las fases y del tipo HW (`0x20c74`).
  - No se ha unido cada clase a una secuencia Darwin concreta.
- **Ruta electrónica sin cortinas:** no se encontró una ruta seleccionable por disparo.

## 5. Rutas sin movimiento mecánico presentes en el código y qué las bloquea

| Candidato | Hecho | Bloqueo | Clasificación |
|---|---|---|---|
| Tipo HW 0 en Darwin | Con `0x1b080(0)&7 ∉ {1,2,3}` no se escribe ni P4D ni P4E | Byte de configuración de Backup (`0x20000050`), no se elige por disparo. Forzarlo afecta al mecanismo entero y no prueba lectura válida | VERIFICADO (puerta). Efecto físico: HIPÓTESIS |
| Tipo HW 3 | Mueve P4E pero no P4D, es decir, solo la 2.ª cortina | Igual que arriba. Podría corresponder a otra unidad de obturador o a un modo de 1.ª cortina electrónica | VERIFICADO (código). Semántica: HIPÓTESIS |
| Filas `0x00..0x8c` de `0x43edccf8` | No llaman a `0x438c2538` ni a CAIF en profundidad ≤5 BL | `0x437eabfc` nunca las devuelve en captura fija. Son de otros recorridos (RawPlay/Develop, fila `0x78` con selector de sensor, s20) | VERIFICADO (selector y ausencia de BL directos). Uso: INFERENCIA |
| Fila `+0x12c` (`cap+0x4b70==7`) | Probable función `0x43b1c0e2` (GOT `0x44021cc4`): usa CAIF evento 12 (`0x438d0d34`), no `0x438c2538`. En `0x437ea8cc`, el valor 7 fuerza además la secuencia de exposición 0 | No se demostró la colocación en `+0x12c` ni el significado del valor 7 (RAW develop o reproceso) | INFERENCIA / HIPÓTESIS |
| Secuencias de `0x43eddd08` sin CAIF directo (p. ej. índice 9 `0x43b1b0c8`) | Exponen con `0x438c828c` y SetExposure sin llamar a CAIF | La petición CA ya la hizo la fila externa. No equivale a evitar la cortina | VERIFICADO (BL). DESCARTADO como ruta sin cortina |
| Bit Silent `0x20` del paquete (A6300) | El parser de la A6000 no lo copia (reutilizado) | El firmware Darwin de la A6000 no tiene ese consumidor | Reutilizado (VERIFICADO previo) |

**Conclusión del tramo:** en el código estático de la A6000 3.21, toda captura fija que pasa por
`0x437eabfc` ejecuta `Stage_CaComm` y, con él, la petición CAIF a Darwin. El único «no mover» que
existe está en Darwin y depende de un byte de tipo de hardware, no de un ajuste por disparo.
El veredicto **A > E > P ≈ E2** no cambia. La nueva evidencia refuerza que una ruta E/Silent en la
A6000 exigiría intervenir antes de `0x438c2538` o en el selector `0x437eabfc`, y mantener los
contratos de C-04.

## 6. Huecos restantes

1. **K2→K3**: falta el código libObj entre `InfraInput` (`0x7a0020`) y los envíos `0x4042/0x4043` (CamUser/RelMgr bridge). También falta asignar `XS_1/XS_2` a códigos (`key_tbl` en Backup).
2. **MSS_S2_REQ_CA / DWN_IN_RELEASE / XS_1→INT10**: falta quién los activa en IC6000 (driver o LIRO) y qué manejadores de interrupción FM3 los atienden. El pin exacto de IC6000 para `MSS_S2_REQ_CA` es ambiguo.
3. **L5**: falta qué estado de la máquina `0x302d9` está activo al llegar `0x100`. El registro de `0x43807f4c` está verificado; su activación, no.
4. **L11**: falta la codificación tag `0x12`/`0x13` → trama CAIF en `0x436bc140` y su correspondencia con el opcode del parser Darwin.
5. **D1**: falta unir la trama de captura recibida → descriptor/fase Darwin → primera escritura P4D/P4E (`0x1f694/0x1f8a2/0x1f914/0x20154`).
6. Falta confirmar la fila `+0x12c` y el valor `cap+0x4b70==7`.
7. Inspección visual de las hojas 23/24/26/48. Hasta ahora solo hay coordenadas de texto.

## 7. Siguiente paso concreto

Decompilar la máquina de la tarea CA `0x436bc140` para los tags `0x12` y `0x13`, y obtener el opcode
y la longitud CAIF que transmite. Después, buscar ese opcode en el despachador de recepción de
Darwin, junto al parser `0x17f8c`, hasta la primera llamada a `0x20c90` o `0x20d00`. Eso cierra la
única arista que queda entre la orden LIRO y la bobina. En paralelo, falta determinar si la línea
`MSS_S2_REQ_CA` (INT05) es la señal de tiempo real del disparo: buscar en Darwin la configuración
del canal EXTI 5 y su vector.
