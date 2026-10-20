# S52 A3 — control de cortinas: qué cambia la A7S en Silent (prueba central)

19-10-2026, Agente A (Claude). Estático. Evidencia y reproducción al final; hechos VERIFICADOS en
`tests/test_s52_curtain_facts.py` (14/14). Documento hermano: `s52_silent_flag_consumers.md` (A1/A2).

## 0. Arquitectura del control de cortina (lo que el código permite afirmar)

| Pieza | Evidencia | Estado |
|---|---|---|
| LIRO no mueve cortinas: habla con el microcontrolador de obturador por **CAIF** (cola de la tarea CA) | Emisor `0x4379b590(ev,…)`: ev0 → `0x436d8270` (tag `0x13`), ev1 → `0x436d8354` (copia **22 B** de `captura+0x4ae8→+0x40`), ev3 → `0x436d82e4` (**tag `0x12`**), ev2/4..7/9..b otros. Receptor de respuestas `0x4379b6ac(ev,…)` (cola, comprueba `msg[2]==ev`) | VERIFICADO (instr. + REA) |
| Tag `0x12` → GPIO | A6000 S50/S51: `0x436bc140→0x436b93b0→0x43b5e2b0` → `1<<bit` en `0xf2910048+banco*0x100`. Homólogos A7S: helpers GPIO `0x43b585aa` (`r2=1`, registro `+4`) / `0x43b585b6` (`r2=0`, `+0x48`) → `0x4397d4c0` (= A6000 `0x4398f9a4`, bytes idénticos) | VERIFICADO helpers; **es un helper GPIO genérico** (≈150 llamadas en cada binario), no un driver de cortina |
| Microcontrolador del obturador | A7S trae su propia ROM `0640_darwin/darwin_core.bin` (SHA `241f5d31…`, reset `0x45f9`, base `0x4200`). Selector de tipo de mecanismo `0x216e8`: acepta 1/2/3 (igual que A6000 `0x20c74`); **no** acepta 4 como A6300 `0x24700` | VERIFICADO bytes; parser CAIF en Darwin NO localizado (tampoco en A6000/A6300, docs previos) |
| Bobinas P4D/P4E (`1ST/2ND_CURTAIN_MG`) | Heredado A6000 (S21, esquema) | no reverificado aquí; enlace GPIO→Darwin→bobina PARCIAL |

## 1. Prueba central — ¿la ruta de clase 0 omite llamadas/eventos/MMIO que 1/3 ejecutan?

Hay que separar **dos** variables, porque en A7S Silent produce ambas a la vez: la **clase** (`G+0x5c`, `0x438649bc`)
y el **tipo Silent** (`captura+0x78c==2`, y su bandera `captura+0x748=1`).

### 1a. Diferencias que dependen de la clase (0 frente a 1/3) — VERIFICADO

| # | Función / condición | Ruta clase 0 | Ruta clase 1/3 | Destino |
|---|---|---|---|---|
| C1 | `0x438627d2`: `clase==1 \|\| (clase==3 && *0x43faba61==1)` | **no** llama `0x43aed4ba` | llama `0x43aed4ba(x162,x166,1)` → `0x437c3114(0xa..0x12)` | mensaje tipo 3 / `0x22` a una cola OSAL (`ldr r0,[pc]` en `0x437c311c`); receptor **NO VERIFICADO** |
| C2 | `0x43863146..3174`: byte +1 del paquete CAIF ev1 | `2` (o `0x42`) — **igual que clase 3** | clase 1: `0`/`0x40`; clase 3: `2`/`0x42` | MCU de obturador vía CAIF ev1 |
| C3 | `0x43862158` → `param+9` → SetExposure `0x436f2938` → IMX235 `0x436f4168` | ShutMode 0 (bits `0x440220a8` b2,b4,b6=0; `0x44021fee\|=8`) | ShutMode 1/3 | **sensor** (registros lógicos; transporte serie NO VERIFICADO) |
| C4 | `G+0x60` | 0 (forzado por tipo 2) | EFCS=1 ⇒ 1 | copias `0x43fab0a7`, `0x43faba61` (esta última usada por C1 y C2) |

**Conclusión 1a:** la clase 0 **no** omite ninguna llamada a CAIF ni a GPIO; su único efecto directo hacia el
mecanismo (C2) es que el byte +1 vale lo mismo que en la clase mecánica 3. La clase solo cambia el modo del sensor (C3)
y omite un mensaje interno de destino desconocido (C1). **La clase 0 por sí sola no prueba cortina inmóvil.**

### 1b. Diferencias que dependen del tipo Silent (A7S nuevas, no existen en A6000) — VERIFICADO

| # | Función | Condición | Ruta Silent | Ruta normal | A6000 |
|---|---|---|---|---|---|
| S1 | Constructor paquete ev1 `0x43862e24` (`0x4386329a..32b4`) | `captura+0x78c==2` | `pkt[+0x12] \|= 0x20` | bit 5 = 0 | `0x4384149c`: solo 0/1 |
| S2 | íd. `0x43863258..3286` | íd. | `pkt[+0xd]` bits 6-7 = **2** | 2 solo si modo `0x19` o `[r7]==0x313` | `0x43841468`: 2 solo si modo `0x19` |
| S3 | Etapa `0xc8` `0x438b1cba` | `captura+0x748==0` | **omite** `0x438be5f8` = esperar respuesta **CAIF 3** | espera | espera siempre (`0x438d08e8`) |
| S4 | Etapa `0xc9` `0x43b1c92e` | `captura+0x748==1` | **añade** espera CAIF 3 antes de enviar CAIF 5 | solo CAIF 5 | solo CAIF 5 |
| S5 | ReadExecuteBase `0x438b726c` | `748==0` (y `param[8]`) | **omite** `0x438be76c` = esperar bandera `0x800000` (puesta por el callback CAIF `0x43b1e3e4`, registrado con `0x4379b7fc(1,…)` en `0x438be592`) | espera | espera si `!param[5]` |
| S6 | caso `0xfd` `0x438b7ec2` | `748==0 && +0x4bb0` | evento de captura `0x100` | `0x102` posible | `0x102` si `+0x4b9c` |
| S7 | cola `0x108` `0x438b8054` | `748==0` | **omite** `post(2,1)` y `0x43b1d5de` (operaciones del imager `0x43ad9780/0x43ad97b4` si `+0x743`) | ejecuta | ejecuta siempre |

**No cambia con Silent:** la bandera de comunicación CA `captura+0x757` (A6000 `+0x74f`; escritores `0x43816544`,
`0x438b1a0e` diagnóstico, `0x43763c9e`, `0x4389f03a`) — ninguno depende de `+0x748/+0x78c`. Por tanto el envío del
evento 1 (paquete) y los demás envíos CAIF siguen ocurriendo; ninguna llamada a un helper CAIF de emisión
(`0x438be16c…0x438be980`) está guardada por `+0x748`/`+0x78c` (barrido `s52/guards.py`: solo S3, S4 y S5, que son esperas).

### 1c. Respuesta a la prueba central

- **¿Omite la ruta de clase 0 llamadas/eventos/MMIO que 1/3 ejecutan?** Solo C1 (mensaje tipo 3/0x22 de destino
  desconocido). No omite ningún envío CAIF ni escritura GPIO/MMIO identificada. VERIFICADO dentro de la cobertura.
- **¿Omite la ruta Silent (tipo 2) algo?** Sí: dos **esperas** de respuestas del mecanismo (S3: respuesta CAIF 3;
  S5: notificación `0x800000`), una llamada al imager y un evento (S7), y reordena la espera CAIF 3 a la etapa `0xc9`
  (S4). **Ninguna** de ellas es una orden de movimiento; son sincronizaciones con el MCU.
- **Destino físico identificado:** el paquete CAIF ev1 (S1/S2/C2) al MCU del obturador; el sensor (C3). Identidad
  eléctrica del canal y efecto en bobinas: NO VERIFICADO.

## 2. P2 — cómo evita la A7S la 2ª cortina (respuesta con su grado de prueba)

1. **VERIFICADO:** LIRO no suprime ningún comando de cortina en Silent. Sigue enviando el evento 1 con el paquete, pero
   **marca Silent dentro del paquete**: bit `0x20` en `+0x12` y modo `2` en `+0xd>>6` (S1/S2), igual que el A6300
   (`silent-caif-transport.md`, `+12`=`0x12`). El byte de clase `+1` es el de clase 3 (C2).
2. **VERIFICADO:** LIRO deja de **esperar** las respuestas del mecanismo que en la toma normal sincronizan la exposición
   (S3, S5), y espera la respuesta CAIF 3 más tarde (S4); el sensor recibe ShutMode 0 y drive mode `0x4e/0x4f`.
3. **INFERENCIA (fuerte):** quien decide no mover las cortinas es el **MCU del obturador** (Darwin A7S) al recibir el
   paquete marcado; LIRO adapta su sincronización a que no habrá eventos mecánicos normales.
4. **NO VERIFICADO:** el consumidor del bit `0x20`/modo 2 en `darwin_core.bin` A7S (búsqueda directa de
   `ldrb #0x12` + `tst #0x20` sin resultado en las tres ROM Darwin; parser CAIF de Darwin nunca localizado), el destino
   del tag `0x12` en A7S (tarea CA no trazada en A7S) y el pin GPIO→Darwin.

## 3. Comparación A6000 (existe / falta / difiere)

| Componente | A6000 | Clasificación |
|---|---|---|
| Bandera `+0x740` (≡ A7S `+0x748`) y 13 lectores | existe, **sin productor** | latente |
| S1/S2 (bits Silent del paquete) | falta | falta |
| S3/S4/S5/S6/S7 (esperas condicionadas) | falta: espera siempre | difiere |
| C2 (clase 0 → byte +1 = 2) | clase 0 → 0 | difiere |
| Paquete ev1 | 22 B (igual que A7S; A6300 31 B) | igual |
| Helpers GPIO `0xf291xxxx` | idénticos | igual |
| Selector de tipo HW Darwin 1/2/3 | igual que A7S (A6300 acepta 4) | igual |

## 4. Hipótesis asignadas

El texto formal de H52-1/2/6 no está en el repositorio (solo sus números en `TASK_S52.md`); se usan estas
definiciones de trabajo, coherentes con A1/A3 y con las de Codex (H52-3/4/5/7). Revisar si difieren del encargo.

| H | Enunciado de trabajo | A favor | En contra / incógnitas | Confianza | Próxima comprobación | Estado |
|---|---|---|---|---|---|---|
| H52-1 | `captura+0x748` es un control con efecto en la secuencia de obturación, no solo informativo | 5 sitios nuevos condicionados (S3–S7): esperas CAIF 3 y `0x800000`, evento `0x100/0x102`, ops del imager; 11 lectores compartidos de temporización | El efecto final es sincronización, no una orden de cortina; inicialización del campo no hallada | alta (efecto en software) | constructor/reset de `captura` | **VERIFICADO** (efecto software); efecto mecánico NO VERIFICADO |
| H52-2 | En Silent la A7S suprime la comunicación con el MCU de cortinas (no envía comandos de cortina) | — | El paquete ev1 se sigue enviando y **lleva** la marca Silent (S1/S2); `+0x757` no cambia; ningún envío CAIF guardado por Silent; solo se omiten esperas | alta | parser CAIF en `darwin_core.bin` A7S | **DESCARTADO** como «supresión»; sustituido por «Silent se señaliza en el paquete y LIRO deja de esperar respuestas mecánicas» (VERIFICADO) |
| H52-6 | La A6000 conserva la lógica Silent dependiente de la bandera (latente, sin productor) | Campo `+0x740` con 13 lectores y ningún escritor; `0x109` A6000 incluso tiene una rama `+0x740==1` | Faltan S1/S2/S3–S7, conversor, rama de política, modos `0x4e/0x4f`, clase 0→byte+1=2 | media | comparar el resto de lectores compartidos en detalle | **PARCIAL**: VERIFICADO que existe la bandera latente; las piezas Silent nuevas faltan (no basta con poner `+0x740=1`) |

Relacionadas (Codex): H52-3 «clase 0 alcanza `param+9=0`» → **VERIFICADO** aquí (`0x43862158`, `0x43b1c8e2`,
`0x438b77ac`). H52-4 «clase 0 inhibe la 2ª cortina» → la clase sola **no** omite envíos CAIF y se codifica igual que
la clase 3 en el byte +1: no la inhibe en LIRO; si hay inhibición, depende de la marca de tipo Silent en el MCU
(NO VERIFICADO).

## 5. Reproducción

```bash
cd work/claude
llvm-objdump --triple=thumbv7-none-eabi -d --no-show-raw-insn input/a7s-av-cam-view.elf > s52/dis/a7s.dis   # ídem a6000
python3 s52/traceid.py c8 c9 1ca 1cb 108           # emparejar funciones por ID de traza
python3 s52/fdiff.py 0x438b6790 0x438b7480 0x438c7290 0x438c7fa0 | grep '#0x74[08]'
python3 s52/guards.py s52/dis/a7s.dis 0x438be5f8,0x438be76c,0x438be6e8
python3 s52/pic.py input/a7s-av-cam.bin 0x43863140 0x43863144   # -> 0x43f04c8c
~/.venvs/re/bin/python -I tests/test_s52_curtain_facts.py
```
