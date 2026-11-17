# G84 — Informe intermedio E2E-12 / 12b / 12c: emulación del objetivo y barrera del guion de av-cam (17-11-2026)

**Estado:** intermedio, para retomar. Pendientes: [E2E-12c en PENDIENTES](../PENDIENTES.md). Detalle por tarea: [G75 T35–T37](g75-arnes-e2e-objetivos.md). Commits: `9217b721`, `c96b3c40`, `73b2e0bd`, `87590d63`, `c3edaa66`, `eca60a27`, `b22bf5be`, `35063a5e`.

## 1. Objetivo y estado

Emular en la LIRO VM (QEMU + sonyshim) el objetivo de kit E PZ 16-50 mm para probar de punta a punta, en el arnés de objetivos del backoffice, las funciones que dependen de av-cam.

| Hito | Estado |
|---|---|
| E2E-12 (T35): montura `[0x43e81240]` llega a 5; módulo 11 → `0xC01` | **Cerrado** (VM; 7/7 tests `tests/test_avcam_montura.py`) |
| E2E-12b (T36): localizar la barrera del guion tras la montura | **Cerrado con límite** |
| E2E-12c (T37): hallar el productor de la barrera | **Abierto** |
| Meta: `[0x43ede338]`=2 sin escribir estado a mano; av-cam contesta `0x3003/0x3000/0x3024`; módulo 11 en `0xC02` | **No alcanzada** |

## 2. Lo establecido (MEDIDO salvo indicación)

1. **Montura (T35).** El invocador del cierre de RX es la irq `0x7e` = GPIO_S(5), flanco de subida de DATA_IN. El objetivo contesta CS_CHECK_CMD, ATTACH_INFO1/2, UART_HZ, CS_POWER, STARTUP_INFO, SYSTEM_HZ, CS_RESET, CS_CREDIT y el régimen (ID 5/6). `[0x43e81240]`: 0→4→1→5.
2. **Corrección al informe previo.** «Posición 28» es el **índice** de la lista `0x43ede340` (tabla `0x43bf2208`, 43 entradas), no `[0x43ede338]`. Los «literales fuera de rango» (`0x43792058/5a`) eran literales pc-relativos mal leídos; `[0x43f9a4bc]` es un contador de HS_Main 0→5, correcto.
3. **Mecanismo del guion.** Cada V (`0x43790730…`) copia los estados de módulo a «actual» (`+0x5c`); `0x437fc748` los compara con los «deseados» (`+0x1c`) según la máscara de la entrada; `0x437fc580` copia `[0x43ede320]`→`[0x43ede338]` solo al agotar la lista. `0x437fc1b0(0x3003)` solo contesta con `[0x43ede338]` ∈ {2, 0x3f, 0x68}.
4. **Barrera.** La lista avanza sola 28→30 (módulo 3 `0x300→0x320→0x323→0x325`, escritor `0x43b09f6a`/`0x43859b88`) y se detiene en idx 30: el módulo 3 debe pasar a `0x326` (`0x43859d2a`), que exige `[0x43eaee84+0x49]`==1 (`0x43eaeecd`), hoy 0. Con ese byte a 1 el guion llega al final (idx 42) y `[0x43ede338]`=2 (diagnóstico: `test_barrera_del_guion_es_el_byte_0x43eaeecd`; no es solución).
5. **Origen del byte.** `0x43eaee84..+0x92c` es una copia por V (`memcpy 0x439c5320`, desde `0x4384420d`) del bloque `0x43eb2680`; el byte es el flag `+0x49` del slot 0 (8 slots × 0x18 desde `+0x48`) que mantiene `0x4384fb7c`. Esa función sale pronto por dos guardas: `[0x43eaf7b0+0xc34]`≠0 (copia del global `0x43fa4ba3`, que solo pone a 1 el init del OPD `0x439e2888`) y `[0x43eb2680+0xb]`==1 (cambio de `[0x43eaf7b0+0xbdd]`).
6. **Init del OPD.** `0x439e2888` se llama desde `SyncResMgr::Get` (`0x437298e8`, ruta de fallo «IDT_OPD_TOP_Sync_OPDAcquire error!») con el recurso 22 (caso 22 del `tbh` `0x43729a76`), pedido por el slot 14 de la tabla `0x43fcc700` desde el manejador `0x43549e48` (por GOT). La VM solo pide el slot 0.
7. **`0x43549e48`** no lo despacha una orden del cuerpo: es un callback registrado por `0x4380ea14` (máquina por V) solo cuando el módulo 0 está en clase 5 (`0x0c/0x11`); el guion 0→2 no lo pide, así que no es la causa.
8. **Orden de arranque `0x3006`** (formato inferido de `0x3024`) entregada antes de las 14 de EE_START lleva la VM al paso 1 y el módulo 3 por `0x301` (como la RAM real); no abre la barrera. Test: `test_orden_de_arranque_0x3006…`. `0x3000` deja la VM en el paso 0.

## 3. Lo que muestran los volcados reales

- RAM `ram-servicio-20261020` (reposo): `[0x43ede338]`=`[0x43ede320]`=1, lista `0x43bf162c` (retorno a reposo), última petición `0x3006`; módulos `0x101/0x301/0x501/0x401/0x960`; `0x43fa4ba3`=0, `0x43f9b398`=0. El reposo real **ya recorrió 0→2→0x1b→1** (lista `0x43bf3648`) y reinició el OPD al volver.
- Regiones con datos en la real y a cero en la VM (salida del arranque del pipeline, no del binario): `0x43f0f000–0x43f14000`, `0x43f8c000–0x43f8f000`, `0x43e0d000–0x43e12000`.
- Búfer de consola (`0x83400000`, anillo envuelto, 263 líneas): `[CAMUSER] ExcConf … ID:[17] Type:[1]` (t=53,47 s) → `ExcBase) DIADEM` (53,48 s) → `[DFECore] DrvSGC0: Last frame is not started` (53,82 s). Orden real: configuración de extensión → DFE → pipeline. Hay además `[MOUNT_ERROR] CAM_INFO2_RCV_WAIT_TIMEOUT_ERR` (50,5 y 55,5 s).
- Resto de volcados (`silent-ram-*`, `mem-*`, T004/T006, klog SWD `20261110-swd-369/371`): sin trazas de arranque de av-cam. No aportan la orden.

## 4. Hipótesis y descartes

- **Más probable (INFERIDO):** falta un estímulo del pipeline sensor/ISP/OPD (arranque del DFE/OPD), no una orden concreta del cuerpo; el código estático no lo enlaza con ninguna orden.
- **Descartado:** esperar 30 s virtuales tras `0x3003`; que `0x43549e48` abra la barrera; que `0x43853460` escriba `[0x43eaf7b0+0xbdd]` (reinicia otro objeto, `0x43eac66c`).
- **Sin probar:** órdenes de LV/S1 como estímulo (llegan tras la barrera); las rutas `0x437ee398` (tarea de procesado de cuadro) y `0x439e2490` (pueden pedir el recurso 22, sin referencias estáticas, nunca corren en la VM).

## 5. Límites reales

Sin cámara física; todo es VM. El arnés **no** puede validar de punta a punta el parche de objetivos hasta superar la barrera; sí valida montura a 5 y módulo 11 a `0xC01`. Con el byte forzado a mano av-cam contesta `0x3003` (solo diagnóstico). El formato de `0x3006` es inferido. `av-cam.bin` y los volcados grandes no están versionados.

## 6. Cómo retomar

1. **Vía A (captura, requiere autorización del usuario):** registrar en la cámara real la secuencia completa ObjCamera→av-cam del arranque (antes de EE_START; ExcConf ID 17) y entregarla a la VM; comprobar `[0x43ede338]`=2 sin escritura manual.
2. **Vía B (sin cámara):** modelar el arranque del pipeline sensor/ISP/OPD en la VM (qué hace `0x43b7170c()`, quién llama a `0x437ee398`/`0x439e2490`, escritores de `[0x43eaf7b0+0xbdd]`), guiándose por la secuencia ExcConf→DFE de la consola real.
3. Cierre: test normal (no diagnóstico) que pase sin escribir estado a mano; luego `0x3000/0x3024` y módulo 11 `0xC02`; actualizar E2E-12c y G75.

Entorno útil: sesión REA del binario (`analysis/rea-independent/bin/session_daemon.py`, ≈8 min en frío; estaba caída al redactar); capstone sobre `analysis/rea-independent/input/av-cam.bin` (base `0x43541000`, Thumb); ganchos Unicorn vía `_corre(pre=…)` de `tests/test_avcam_ee_start.py`.
