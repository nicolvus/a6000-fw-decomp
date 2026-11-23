# G101 — «Film» en una tecla: la rueda de control abre la franja horizontal; C1/AEL no (23-11-2026, investigación estática)

Petición: poner la lista horizontal de looks (la de G100) en una tecla personalizada como C1 o AEL.
Fuentes: `viewUnified7.so`, `viewUnified2.so` y `CautionConfig.so` del 3.21 (bytes, Capstone y REA/Ghidra sobre `viewUnified7.so`; en REA las direcciones llevan +0x10000).
Sin parche, sin CFW, sin cámara.

## 1. Las dos familias de teclas
| Ajuste (Ajustes de tecla personalizada) | Lista de asignación (`CautionConfig.so`) | Qué abre |
|---|---|---|
| C1, AEL, botones centro/izquierda/derecha/abajo (pids `0xc4…0xc8`, `0xdd…0xdf`, clase `CmnViewProcessDataElementCustomCustomButton`) | `cmnViewSettingNodesCustomButtonType01`: 36 funciones (la del A6000; `Default` = 44, `Type02` = 21) | Una pantalla propia de cada función (`ViewDro`, `ViewWhiteBalance`, `ViewFocusMode`…); no hay una vista genérica para un nodo cualquiera |
| **Rueda de control** (pid `0xdc`, Backup `0x1070c74`) | `cmnViewSettingNodesRearWheelDefault`: ISO, Balance, Estilo creativo, Efecto, No definido (opciones `0xf` = 0…4) | **La franja horizontal `PAS_MenuSelectBeltWheel`**, en la vista de los diales `ViewTriDial`: el mismo tipo de lista larga ◄ ► que la de diafragma y velocidad |

**Conclusión:** la forma nativa de tener una lista larga horizontal con una sola acción (girar) es asignar «Film» a la **rueda de control**.
Para C1/AEL habría que crear una vista nueva, porque cada función abre su pantalla fija; no se propone.

## 2. Cadena de la rueda (VERIFICADO en bytes)
1. **Asignación (`viewUnified2.so`).** El descriptor del pid `0xdc` (`0x4b76ac`, 5 opciones) apunta a un modelo `0x4b9620` = {Backup `0x1070c74`, tabla `0x4b97cc`}.
   La tabla da el valor de cada opción: `[8, 0xb, 0xd, 0xe, 0]` = ISO, Balance, Estilo creativo, Efecto, No definido.
2. **Elección del nodo (`viewUnified7.so`, `ViewTriDial`, evento 5, `0x2100c`).** Lee `0x1070c74` y hace `tbb` sobre `valor − 8` (0…6) con `tbb` = `[10, 13, 13, 4, 13, 6, 8]`:
   - 8, `0xb`, `0xd` y `0xe` cargan el nodo raíz de su función desde el GOT, en `[this+0x130]`;
   - **9, 10 y 12 caen en «sin nodo»**: están libres;
   - con el nodo, `openMenuSelectBelt` (`0x2fa96`) abre la franja Wheel y `setPanelType` elige el panel.
3. **Otros lectores del mismo valor:**
   - `viewUnified7.so`: el selector de panel `0x1ef58`, con tabla `0x42fcc` = `[5, 1, 1, 3, 1, 18, 18]` para 8…14. El 9 ya da 1, el valor por defecto.
   - `viewUnified2.so`: tres vistas con el mismo patrón de nodo (`0x13f622`, `0x3621ba` con `tbb` 8…14; `0x389c34` solo `0xb`/`0xd`).
   - `viewUnified2.so`: el indicador de la pantalla de disparo (`0x287a34`, `tbb` 0…14), con una función de dibujo por cada valor; los demás valores no dibujan nada.

## 3. Parche propuesto (FILM-8)
- **Valor nuevo** 9 = «Film», sin quitar ninguna opción de Sony.
- **`CautionConfig.so`:** lista `RearWheelDefault` de 5 a 6 nodos, con el nodo nuevo «Film» (`0xb = 0`, `0xc = 2`, `0xf = 0x10 = 5`) delante de «No definido».
  Se hace igual que G86 §4: matriz nueva en un segmento RW y GLOB_DAT → RELATIVE.
- **`viewUnified2.so`:**
  - el pid `0xdc` pasa a 6 opciones, con la tabla `[8, 0xb, 0xd, 0xe, 0, 9]` y las precauciones, en un segmento nuevo;
  - en las vistas `0x13f622`/`0x3621ba`, el caso 9 → nodo «Film».
- **`viewUnified7.so`:** en `ViewTriDial`, `subs r3,#8; cmp r3,#6` (`0x21024`) pasa a `bl cueva`. La cueva hace:
  - si el valor es 9: `r3` = nodo «Film», desde una palabra con `R_ARM_ABS32` contra un nodo raíz importado de `CautionConfig.so` + la distancia, y vuelve al `str.w r3,[r4,#0x130]`;
  - si no: las dos instrucciones originales y `bx lr`.
  - `lr` ya está guardado en la pila de la función.
- **El nodo «Film» es el de G100** (Backup `0x1070219`): al girar, la franja escribe el look y el hilo userland lo aplica con su receta, LUT y curva.
- **Pruebas antes de construir:**
  - Unicorn del caso 9 en las tres vistas;
  - que 8/11/13/14/0 sigan dando lo mismo;
  - cadena opción 5 → valor 9;
  - el arnés GUI con la rueda girando, si el perfil lo permite.

## 4. Riesgos y límites
- **Formato del descriptor `0xdc` (clase sin modelo Normal): NO_VERIFICADO.** De dónde saca el elemento el nº de opciones es inferido (byte `+0x15` = 5).
  Es el punto que puede colgar el menú de teclas.
- **Sin indicador:** el indicador de la rueda en la pantalla de disparo (`0x287a34`) no dibuja nada con el valor 9. Funcionaría, pero sin icono.
- **Sin ver en la cámara:** no se sabe si `ViewTriDial` se abre al girar con el valor 9; no se ha visto ningún filtro previo por valor. Tampoco se ha medido la franja Wheel con 39 opciones.
