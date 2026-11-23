# G100 — CFW 3.90 «Film»: los 39 looks en una sola lista horizontal del menú Fn (23-11-2026)

Petición: con el 3.89 funcionando, elegir el look con un botón entre **todas** las opciones, en una lista larga horizontal como la de los pasos de
diafragma o velocidad, y no por categorías.
Código: `scripts/lut/film_userland.py` (`ajuste_todas`), `scripts/lut/userland/films.c` (`sincroniza`, `NCAT`), `scripts/gui/build_cfw_film.py`
(`FN_TREES`); tests `tests/test_g97_films.py` (15).

## 1. Vía elegida: la franja del menú Fn (la de G86)
- **Interfaz:** al pulsar **Fn**, ponerse sobre una casilla y girar la rueda, la cámara abre la **franja nativa** (`PAS_MenuSelectBelt`, G86 §1):
  una fila horizontal ◄ ► con la opción actual resaltada, que se desplaza cuando hay más opciones de las que caben (como la ISO).
- **Por qué no el menú:** el tope de 7 opciones (G36) es de la lista vertical del menú (clase Normal), por eso el menú partió los looks en 8 filas por categoría.
  La franja no tiene ese tope.
- **El 3.90 reutiliza la infraestructura de G86, ya verificada offline:**
  - en `viewUnified4.so`, el hijo 39 de la raíz Fn y el valor de asignación `0x26` → SRNum `0x27`;
  - en `CautionConfig.so`, las 12 listas de asignación `…CustomFunctionNType08`, con «Film» antes de «No definido»;
  - en `viewUnified2.so`, la tabla opción → valor.
- **El nodo es «Film»:** Off y los 38 looks en el orden del menú. Guarda 1 B en el Backup `0x1070219` (id libre 9 de G56) con su propio pid `0xF1`.
  No aparece en las páginas del menú.

## 2. Una sola selección, con las filas sincronizadas
- **El hilo userland trata la lista única como una fila más** (la última, base 0, 39 opciones).
- **Manda la última fila que cambió**, y el hilo deja todas las filas en ese look: la de su categoría y la lista única lo muestran, las demás quedan en Off.
- **Off en cualquiera = Off.** Antes, al poner Off en una fila mandaba la primera que siguiera con look. Ahora solo hay un look activo, y el menú y la franja Fn dicen lo mismo.
- **Restos de otros CFW:** el id `0x1070219` era Color Chrome en otros CFW. Al arrancar se ignora su valor y se reescribe con el look activo.
- **Todo lo demás, como en el 3.89:** la receta nativa de RecipeLab, la LUT, la curva y la devolución de tus ajustes en Off.

**Evidencia:**
- Unicorn sobre el hilo compilado:
  - elegir en la lista única pone la fila de su categoría;
  - elegir por categoría actualiza la lista única;
  - Off en la lista apaga todo;
  - el valor ajeno en el id se corrige al arrancar.
- Ficheros reales del 3.90:
  - el hijo 39 de la raíz Fn apunta a un nodo «Film» con 39 opciones (textos Off + 38, `0xf` = 0…38) y el pid de la lista única;
  - en las 12 ranuras, la opción «Film» va al valor `0x26`, que el despachador de `viewUnified4.so` lleva a SRNum `0x27`.
- Suites G86/G87/G89/G92/G97: 50 tests en verde.

**CFW 3.90:**
- Fichero: `build/cfw_film390/pkg-3.90/package-3.90/firmware_packed.dat`, sha256 `6ca05acbef80f295b77685b84c29cfa46151a418b6633a278a2550580102b25f`.
- Auditoría `--darwin-v3 --sin-wbi --bionz-g22`: `todo_ok`.
- Sin instalar.

## 3. Uso
1. MENU → Ajustes personalizados → **Ajustes menú función** → elegir una casilla → **Film**.
2. Pulsar **Fn**, ponerse sobre «Film» y girar la rueda de control (o el dial): la franja horizontal pasa por Off y los 38 looks.

## 4. Límites y siguiente paso
- **Nada de G86 se ha probado en la cámara** (FN-LUT-1/5): ni que la franja abra el nodo 39 ni que la asignación persista. Tampoco se ha medido la franja con 39 opciones; con la ISO desplaza unas 27.
- **Tecla personalizada directa (C1, AEL, botones de la rueda):** las listas `cmnViewSettingNodeCustomButton…` de `CautionConfig.so` son otra familia (estilo creativo, modo de avance, etc.).
  - Añadir «Film» ahí exige el mismo trabajo que G86 §4 para esas listas, más saber qué pantalla abre la tecla para un nodo de 39 opciones.
  - Queda como FILM-8.
