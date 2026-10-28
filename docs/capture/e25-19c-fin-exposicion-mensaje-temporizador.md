# E25-19c — Qué termina la espera de sub 9 y qué mide `cap+0x728`

**Fecha:** 28-10-2026 · **Cámara:** 192.168.1.29 (solo lectura; 2 fotos normales + 1 lectura en reposo) · **Commit base:** `3b6fccba`
**Etiquetas:** V = bytes de `av-cam.bin`; F = lectura física; I = inferencia. No se escribió RAM, firmware, NVRAM ni NAND; originales T050 íntegros antes y después de cada prueba.

## 1. Resultado

**Criterio A con límite.** El mensaje que desbloquea sub 9 es **Darwin → BIONZ, ID `0x0e` (3,3) «ExposureReady»**: lo envía el MCU Darwin, no un componente de BIONZ. La duración la fija Darwin (con cortina mecánica); BIONZ solo la **cronometra** (`cap+0x728`). Lo que sigue sin demostrarse es la parte interna de Darwin (no está en `av-cam.bin`) y la llamada real a `SetExposure`.

## 2. Cadena emisor → sub 9 (P0)

| Eslabón | Dirección / dato | Evidencia |
|---|---|---|
| Espera | `0x437db9f0(sub=3, tabla=[cap+0x4ad8])` → `osal_rcv_msg_tmo` (`0x43561260`, `r2=-1`) en `0x437dba34` | V |
| Qué acepta | `[msg+1]==3` (clase) y `[msg+2]==r6==3` (subclase) (`0x437dba64`, `0x437dba90`); guarda el bloque en `tabla[0x20+4·idx]` y retorna 0; subclase errónea → libera y `-4` | V |
| Cola | id en `[[0x44023068]]` = variable `0x43ed4cb0`; el receptor publica en `0x43e77284`. **En vivo ambas valen `0x00056118`** → misma cola | V + F (`emisor-vivo.json`) |
| Objeto `[cap+0x4ad8]=0x43ed4908` | tabla de huecos de la fase (`+0x20…+0x3c`, 8 ranuras), no la cola | V + F |
| Envío | receptor `0x436b8ef0` (fila (3,3) de `0x43fe87f0`): `0x436b8838` valida buzón → copia 8 B → `osal_snd_msg` `0x4356120c` en `0x436b8f1e` con `[0x43e77284]` | V |
| Emisor | Darwin, ID `0x0e` (2 B, traza `0x129`), estado de captura 31 → FSM `0x296f0` estado 5 (op `0x16e92`) | V (E24-05d/f; lado Darwin estático) |
| Reciclado | `0x435612ec` libera el bloque cuando una fase lo sustituye (`0x437dbb6a`) | V |

**Cómo llega la duración a Darwin (nuevo, F):** BIONZ envía el `0x0c` CaptureStartRes con `pkt[2..3] = settings+0x162` = Tv (`Tv = 4096 − 256·log2 t`). Tras la foto de «8 s» el paquete en `[0x43ed4908]+0x40` contiene `00 02 ab 0c …`: `pkt[2..3]=0x0cab=3243` → **10,07 s**. Darwin convierte Tv→µs (`0x19a12`, E24-05h-3: `0x1600`→15 625 µs) y espera; al terminar emite `0x0e`.

## 3. Temporizador y `cap+0x728` (P1/P2)

**Qué es `cap+0x728` en la rama observada (`cap+0x74f=1`):** un **cronómetro de 32 µs**, no un plazo.
* Arranque `0x438c8ac2..0x438c8b18` (V): con `74f≠0` o `740==1` → `r5=-1` (sin plazo) y `0x43b1f1ec(0,-1,cb)` arma el temporizador 0; `cap+0x4ef1=1`.
* Lectura: sub 10 (`0x43b1e878`) llama a `0x43b1e492` (`0x43b1e8ca`) → `0x43b1f22c` lee el contador y `str [cap+0x728]` (`0x43b1e4b4`) si `cap+0x4b84==0`. Por eso `728` es 0 durante la exposición y salta **al llegar el mensaje** (F).
* Rama `74f=0` (V, no observada): `ticks = 0x43840f7c()/32 + 1` (`lsrs r0,#5`, `0x438c8ad8`) → `cap+0x728` → `0x43b1f1ec(0,ticks,0x43b1e4c0)`; el callback pone `0x13:0x100000`.

| Pedido | `728` (F) | ×32 µs | Tv equivalente | Tv real |
|---|---:|---:|---:|---|
| 2 s | 49 553 | 1,586 s | 3926 | **no leído**; coherente con 1,6 s (1/3 EV) (I) |
| 4 s | 125 045 | 4,001 s | 3584 | 4 s exactos (I) |
| 8 s | 314 771 | 10,073 s | 3243 | **3243 leído en `pkt[2..3]`** (F) → 10,07 s |

Los tiempos desde `/shoot` hasta el cambio (2,61 / 5,36 / 11,35 s) crecen igual. **RemoteShutter redondea 2→≈1,6 s y 8→10 s** (como 1→1,3 y 15→20 en E25-19); `/info` muestra el valor pedido, no el aplicado. Con el Tv real, 728×32 µs coincide con 2^((4096−Tv)/256) dentro de 0,3 %; con el nominal no (0,79× y 1,26×). La coincidencia no es casual (tres puntos, uno con Tv leído de forma independiente).

Respuestas P1: **A** `cap+0x744`=4 en los tres tiempos → **no** son segundos. **B** sí, tick de 32 µs (V+F). **C** se lee tras completar la espera (sub 10). **D** Tv→µs lo hace Darwin (`0x19a12`); en BIONZ la rama B usa `0x43840f7c` (µs). **E** el mismo mecanismo cubre 1,6–10 s; 20/30 s en E25-19. **F** el cronómetro no termina nada: la exposición la termina el mensaje de Darwin.

## 4. Rama bandera `0x100000` (P3) y continuación (P4)

* Rama B (`74f=0`): `0x438d08e8` espera `0x13:0x100000` (`0x43560de0`); lo activa `0x43b1e4c0` armado con `ticks=µs/32+1` → **temporizador de host**. Condiciones de armado V; **no observada** (no sabemos qué pone `cap+0x74f=0`).
* `cap+0x740==1` o `cap+0x4b84≠0` (BULB/largas por tramos): plazo −1; sub 10 espera `0x13:0x108000` (`0x43b1e8a4`) y el bit `0x8000` se consulta.
* Tras la espera: sub 10 `0x43b1e878` → (cronómetro) → `0x437f8b34(cap)`, `0x43b1e448` (usa `cap+0x73b`) y `0x438c867c(0,0)` → sub 11 `0x437ed568` (`0x437e58c4`). **Inicio de lectura**: no fijado entre esas llamadas (NO_VERIFICADO). Sin escritura al IMX210 identificada en la espera; cortina y reset electrónico no distinguidos.

## 5. SetExposure (P5)

No observable sin hook. **Protocolo reversible (no ejecutado):** no existe lectura no intrusiva. Para una sesión futura con autorización expresa: parche en RAM mínimo en la llamada de `0x438c828c` que copie `param` a un búfer libre, copia de seguridad y reversión verificadas contra T050, una sola foto de 4 s y aborto ante cualquier divergencia. Lo ya conocido: `shd=1, svd=0, ShutMode=3, 504=1, 740=0` en `cap`.

## 6. Veredictos

| | Respuesta |
|---|---|
| A emisor tipo 3 | **SÍ, con límite**: Darwin, ID `0x0e` (3,3) |
| B llegada a `0x437db9f0` | **SÍ** (bytes + misma cola en vivo `0x00056118`) |
| C condición de envío | **PARCIAL**: Darwin termina su espera de Tv (estado 31); no ejecutado |
| D temporizador efectivo | **SÍ, con límite**: Darwin; BIONZ solo cronometra (host timer solo en rama `74f=0`) |
| E `744`=segundos | **NO** (4 en 1,6/4/10 s) |
| F `728`=ticks 32 µs | **SÍ** (V+F; 2 s inferido) |
| G 2/4/8 s coherentes | **SÍ con Tv real** (1,59/4,00/10,07); **NO con nominal** |
| H rama del host o del sensor | **Host/`cap`** (`74f` es campo de `cap`); su origen no trazado |
| I rama `0x100000` | **PARCIAL** (armado y callback por bytes; no observada) |
| J inicio de lectura | **PARCIAL** (sub 10→11; llamada exacta no fijada) |
| K fin electrónico de integración | **NO** demostrado |
| L qué recibe `SetExposure` | **NO** |
| M pruebas físicas solo lectura | **SÍ** (2 fotos + 1 lectura en reposo) |
| N cámara modificada | **NO** |

## 7. Decisión

**A con límite + B.** La exposición nativa larga la sostiene Darwin con las cortinas; esto **no** prueba ni descarta una integración electrónica nativa. Para 1/15–30 s con ShutMode 0 sin cortina hace falta la **rama de host (`74f=0`, temporizador 32 µs, flag `0x100000`)**, aún sin observar. Siguiente: **E25-19d** — origen de `cap+0x74f`, y si con `74f=0` Darwin deja de cronometrar (o si BIONZ puede sustituir el `0x0e`). No se implementa E25-20.

## 8. Límites

Tv real de la foto de 2 s no leído (se hizo solo lo autorizado: dos fotos); la lectura `pkt` es posterior al disparo; lado Darwin solo estático; no se probó BULB ni 30 s. Evidencia: `analysis/e25-19b/cap-{2,4,8}s.json`, `analysis/e25-19c/{emisor-vivo,temporizador}.json`; scripts `e25_19c_emisor.py`, `e25_19c_temporizador.py`; tests `tests/test_e25_19c.py` (7) + regresiones E25-19b (11) en verde; ruff y mypy sin avisos en lo nuevo; suite global no ejecutada.
