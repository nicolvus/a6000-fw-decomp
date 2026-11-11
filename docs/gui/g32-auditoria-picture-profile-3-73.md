# G32 — Auditoría del menú Picture Profile del CFW 3.73 (11-11-2026)

Alcance: qué hace cada ajuste PP del 3.73 en cada eslabón (menú → `libObj` → mensaje LIRO `0x4066` → `cfg` del núcleo → consumidor) y por qué varios no tienen efecto visible. **Offline** (cámara no alcanzable; nada instalado). Binarios revisados: `libObj.so` y `av-cam` del paquete `analysis/gui/g22/pkg-373w` / `pkg-370t` (mismo parche PP), `av-cam.bin` (A6000) y `av-cam-a7s.bin` como referencia. Tests de la cadena: 33/33 (`test_g23_pp_menu`, `g25_*`, `g26_*`, `g27_color_core`, `g30_libobj_ppeco`, `g31_base_pp`).

## 1. Qué eslabones están sanos (VERIFICADO con bytes/emulación)

| Eslabón | Comprobación | Resultado |
|---|---|---|
| Menú → validador `pvt_ChangePictureProfileParamApp2Obj` (`0x4b46b8`) | Unicorn sobre el `libObj` del 3.73: los 31 casos (`0x1f8+4i`) con valores −40…+40 | **Los 31 ajustes coinciden** en tipo y rango con el menú (enumerados con su `VALUEID`: Black Gamma Range `0x1b4–6`, Knee Mode `0x1bb/c`, Sensibilidad `0x1bd–f`, Detail Mode `0x1c0/1`, B/W `0x1c2–6`; numéricos: Black Level −15…15, BG Level −7…7, Knee Max 0…4, Point 0…12, Slope −5…5, Detail Level −7…7, V/H −2…2, Limit/Crisp 0…7, Hi-Light 0…4, Color Depth −7…7, Sat −8…7, Fase −7…7, WB −9…9) |
| `libObj` parcheado en el 3.73 | tablas de gamma (`0x4b4784`: `…0x585,0x1ba,0x39c…0x3a1,0x481,0x480`), de Color Mode (`0x504/0x505/0x583/0x584`), `patch_bw` y `patch_actions` presentes | correcto |
| Mensaje `0x4066` (`CamMsgConv`, `0x9b3200`) | cada byte `0x0a…0x26` lee la clave `0x9675+n`; los getters de enumerados (`0xde360` + `cmp #VALUEID`) caen justo en los bytes `0x0e` (filtro WB), `0x18` (BG range), `0x1b` (Knee Mode), `0x1d` (Sens.), `0x20` (Detail Mode), `0x23` (B/W) | el orden byte ↔ ajuste (byte = índice PARAMID + 8) queda confirmado por tipos, no solo por inferencia |
| Desempaquetador del núcleo (`0x43802a28`) | byte → `cfg`: WB `0x13d–0x140`, filtro `0x144`, Color Depth `0x148–0x14d`, Sat `0x14e`, Fase `0x14f`, **Black Level `0x150`, BG Range/Level `0x151/0x152`**, gamma `0x153`, **Knee `0x154–0x158`, Detail `0x159–0x15f`** | todos los campos llegan al `cfg` |
| Medido en cámara (G29/G30) | `cfg+0x138/0x13c/0x14e/0x153` cambian con el menú | la cadena entera funciona para esos cuatro |

## 2. Consumidores en el núcleo: lo que sí y lo que no se aplica

La función que arma el mensaje de colorimetría (`0x43829430` en la A6000, `0x438e7250` en la A7S) lee **solo**: tipo/nivel de Color Mode, WB Shift (`0x13d–0x140`, filtro), Color Depth, Saturación, Fase y gamma. **No lee Black Level, Black Gamma, Knee ni Detail** (ni en la A6000 ni en la A7S).

- **Con consumidor en el núcleo (15 ajustes + gamma):** Color Mode tipo/nivel, WB Shift (4 + filtro), Color Depth (6), Saturación, Fase y la selección de curva.
- **Sin consumidor demostrado (15 ajustes):** Black Level, Black Gamma Range/Level, Knee Mode/Max Point/Sensibilidad/Point/Slope, Detail Mode/Level/V-H/B-W/Limit/Crispening/Hi-Light. El núcleo los **reenvía** a un bloque de parámetros (`0x437b1d0a…`: `cfg+0x150…0x178` → `[bloque+0xa72…0xa92]`, equivalente al `0x437c4930` de la A7S) y a getters de 8 bytes (`0x438e56…`), pero ningún código del núcleo los convierte en registros de imagen; igual que en la A7S, donde G15 tampoco halló marcador. Si algo los aplica, es el front-end (blob «REGULUS» embebido en `av-cam`), que no se ha analizado.
- **Diferencia concreta A6000 ↔ A7S:** la copia de la A6000 **salta `cfg+0x154` (Knee Mode) y `cfg+0x155` (Knee Max Point)** (`0x437b1d22` lee `0x153` y luego `0x156`); la de la A7S copia `0x160…0x171` seguidos. La A6000 termina en `+0xa92`; la A7S sigue hasta `+0xa9e`. Es coherente con un front-end de la A6000 sin esas funciones.

## 3. Veredicto por ajuste

| Ajuste | Estado | Causa / evidencia |
|---|---|---|
| Selector Off/PP1–PP9 | funciona (usuario, 3.67/3.73) | `getModelInfo 0x4a` clave `0x275` + eco |
| **Gamma Movie / Still** | **sin efecto por construcción** | selector 4 = `(10,10)`, selector 5 = `(0,10)`; la fila original de la A6000 es `(0,10)` (foto 0, vídeo `0x0a`): en vídeo ambos dan la curva `0x0a` = la de siempre; en foto, `0x0a` no tiene puntero (`TAB+8·10 = 0`) y el código salta si es nulo. No hay dato nuevo que aplicar. (Still `(0,0)` de la A7S reinició la cámara, `pp_curves_patch.py:68`) |
| Gamma ITU709, ITU709(800%), S-Log2, Cine1–4 | cadena y curvas correctas (selectores 3, 11, 10, 6–9 → gammas `0x16`, `0x15`, `0x14`, `0x18–0x1b`; curvas con punteros de vídeo no nulos, `y[2047]` = 1727/931/918/957…) | efecto visual no registrado en cámara |
| **Gamma S-Log3** | curva y selector correctos (selector 2 = `(0x17,0x17)`; curva A6300, `y[2047]` = 803; `CamMsgConv` 0x585 → 2 por test), **pero el núcleo no conoce la gamma `0x17`**: las ramas por número de gamma (`0x438677e0`: `0x0a,0x16,0x18–0x1b` y `0x14–0x16`; `0x438678ac`: `0x14–0x16,0x18–0x1b,0x1e`) la tratan como gamma ordinaria, a diferencia de S-Log2 (`0x14`) y de ITU709(800%) (`0x15`) | hipótesis de la diferencia con S-Log2; **no demostrado** que impida aplicar la curva. Prueba decisiva en cámara: tras elegir S-Log3, `cfg+0x153` debe valer 2 y `YC+0xbd9` `0x17` |
| Black Level, Black Gamma Range/Level | **sin efecto** | llegan a `cfg+0x150–0x152`, sin consumidor (§2) |
| Knee Mode / Max Point | **sin efecto** y el núcleo ni los copia al bloque (§2) | `0x437b1d22` |
| Knee Sensibilidad / Point / Slope | **sin efecto** | `cfg+0x156–0x158` reenviados, sin consumidor |
| Detail Mode/Level/V-H/B-W/Limit/Crispening/Hi-Light | **sin efecto** | `cfg+0x159–0x15f` reenviados, sin consumidor |
| Color Mode (Movie, Still, Cinema, Pro, ITU709 Matrix) | consumidor presente (`switch` de ids, G27 §2) | efecto visual sin medir |
| Color Mode B&W | cadena presente (Movie + saturación −8), **pero** depende de `caps[3]` bit 1 = 0 en la NVRAM real (G27 §5) → el indicador monocromo puede no activarse | «B&W no cambia la imagen» (G29 §2) coherente; sin explicar del todo |
| S-Gamut / S-Gamut3 / S-Gamut3.Cine | S-Gamut = Movie (G27 §5); S-Gamut3(.Cine) con parche de ganchos del núcleo, sin prueba en cámara | |
| Color Mode Level, Saturación, Fase, Color Depth ×6, WB Shift ×4 + filtro | consumidor presente (mensaje de colorimetría, `+0x23…+0x30`); Saturación medida en `cfg` | efecto visual sin medir |
| Copy / Reset | menú presente; Reset (evento `0x42`) **inferido**, sin probar | G30-C |

## 4. Límites

- Sin cámara: no se ha leído `cfg`/`YC` en vivo con 3.73, ni se ha mirado la imagen.
- «Sin consumidor» significa que no hay código del núcleo que convierta el campo en registros; el front-end (REGULUS) no se ha desensamblado. La lista de lectores se obtuvo con barrido Capstone de ambos `av-cam` (ruidoso: los desplazamientos `0x150/0x154/0x158/0x15c` coinciden con otras estructuras).
- La asociación caso→`PARAMID` interna de `libObj` (tabla en `this+0x370`) no se reprodujo entera; se apoya en las 4 magnitudes medidas en cámara y en el orden de tipos de §1.

## 5. Siguiente trabajo (ver PENDIENTES G32-*)

1. **G32-A** Gamma Movie/Still: decidir entre quitarlas del menú, o darles efecto (Still en vídeo con gamma 0: hay que explicar antes el reinicio; Movie en foto: punteros de foto para `0x0a`).
2. **G32-B** Black/Knee/Detail: analizar el front-end REGULUS de `av-cam` (A6000 frente a A7S) y los getters `0x438e56…`; alternativa realista: mapear Detail Level a la nitidez de Creative Style y Black Level/Knee a ajustes existentes del núcleo, o retirarlos del menú.
3. **G32-C** S-Log3: con cámara, leer `cfg+0x153`/`YC+0xbd9`; si son correctos, probar a tratar `0x17` como `0x14` en las dos funciones por gamma.
