# S111 — Módulo `[TRK]`: 215 trazas, 288 sitios y 47 funciones

**Hito de la línea de ingeniería inversa general** (no afecta a la decisión del obturador
electrónico: S51 sigue con A/B/C = NO).
Informe: [analysis/s111_trk/trk.md](../../analysis/s111_trk/trk.md) ·
Datos: `trk.json`, `refs.json`, `a7s_diff.json` · Test: `tests/test_s111_trk.py`.

## Hallazgo central

`[TRK]` es el módulo de trazas del **tracking** (caras/objetos, saliencia, similitud de
toque/color y vectores de movimiento). Sus **215 cadenas**
(`0x43cebceb`–`0x43cfe31c`) se referencian desde **288 sitios PIC** en **47 funciones**;
**284 sitios / 43 funciones** están en una única región, `0x43a30000`–`0x43a39000`, y los
4 restantes son wrappers de sesión en `0x439c0000`–`0x439d0000` (`[CAM INIT/CLOSE]`,
`[VSYNC OPEN/CLOSE]`).

## Qué se ha reconstruido (verificado contra bytes)

1. **216 ocurrencias / 215 inicios** (207 textos; 8 mensajes `[STK] PARAM ERR - box` ×2):
   la ocurrencia extra es el segundo `[TRK` de `0x43cfda0e` `"[TRK]: [TRK] cb_func == NULL"`.
2. **17 sub-bloques**: STK 76 cadenas/145 sitios, BT 44/48, EDTSA 19/19, PMV 16/16,
   IRO2G 13/13, DETSA 9/9, VAE/VAT/VOT 3/3 cada uno, STK_AUTO_SAL 4/4,
   STK_COLOR_SIM 3/3, STK_TOUCH_SIM 3/3, STK_C_SIM 1/1, STK_T_SIM 1/1, sesión 4/4,
   motor 5/5, TIMER 8/8.
3. **Funciones dominantes**: `0x43a36a06` (STK TouchSim, 53), `0x43a3588e` (STK AutoSal, 48),
   `0x43a36156` (STK ColorSim, 45), `0x43a380ac` (BT, 34/38), `0x43a3059c` (EDTSA, 15/16),
   `0x43a34f5c` (PMV, 13), `0x43a347d8` (IRO2G, 8), `0x43a301e4` (DETSA, 6).
4. **Corrección metodológica**: cada `add rX, pc` solo puede usar el **último** `ldr rX`.
   La primera pasada (ventana `0x1000`) daba 330 sitios/214 cadenas; la regla
   nearest-`ldr` (`MAX_GAP=0x40`) da **288/213** y elimina **42 sitios espurios**.
   `sa_stubs`, `fc` y `apl_osal` quedan con **0 sitios**.
5. **Caso demostrativo**: `0x43a37c06` **no** carga `"[BT] cmn.af_rect_thres:%d"`
   (`0x43cfe135`), que sale de `0x43a38720` (`ldr` `0x43a3871c`) en `0x43a380ac`. El
   `add` de `0x43a37c06` usa `0x43a37c00` y calcula `0x43f61264`, que no es cadena.
6. **Dos cadenas sin referencia PIC** (`0x43cfb3e9`, `0x43cfc7ea`, ambas
   `Stop Message Alloc Error`): sin literal absoluto ni `adr`; no se aceptan los pares que
   recargan el registro (`0x43a32a4c`, `0x43a32b5c`). Posible código muerto, **no demostrado**.
7. **99 nombres de fuente `FC/*.cpp`** en `0x43cef12a`–`0x43cf707a`, entre ellos
   `FC/Api/fc_api_tracking.cpp` `0x43cefa43`, `FC/Drv/fc_drv_stk.cpp` `0x43cf627a`,
   `FC/Drv/fc_drv_bt.cpp` `0x43cf603a`, `FC/Drv/fc_drv_pmv.cpp` `0x43cf707a`. La
   correspondencia fichero↔función **no** está verificada.
8. **Diferencial A7S fw3.20**: mismos 215 inicios y mismo multiconjunto de textos; **288
   sitios y 47 funciones en ambas**. A6000 283 `strict`/5 `relaxed`; A7S 284/4. Cambian las
   direcciones (sesión `0x439ce7d8` vs `0x439bcbd4`; última función `0x43a389f0` vs
   `0x43a1dbe4`), no la estructura.
## Relación con otros hitos

S71 ya fijó la semántica de DETSA/EDTSA/IRO2G/PMV/STK/BT. S111 no la repite: aporta el
inventario exacto, la pareja `ldr`→`add`, la función dueña y la zona. Sin solapamiento con
`[IMAGING_CAP]` (S106), en `0x43c9b335`–`0x43ccab72`.

## Abierto / NO VERIFICADO

- Límites exactos de `0x43a376d8`/`0x43a37734` (prólogo anidado) y de las funciones
  `relaxed` `0x43a37ea4`/`0x43a375d8`.
- Que las dos cadenas sin referencia sean realmente inalcanzables.
- Identidad de `sa_stubs` (zona ZIT de S80): 0 sitios, no se afirma pertenencia.
- Unidad de compilación de cada función y semántica de VAE/VAT/VOT más allá de
  `Alloc`/`Free`/`RefMap`.
- Nada verificado en cámara ni en emulador.
