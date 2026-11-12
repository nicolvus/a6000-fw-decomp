# G36-A — Causa del cuelgue del 3.78 en `libObj+0x5b6242` (12-11-2026)

Análisis estático (llvm-objdump, `readelf -r`, bytes) de `analysis/gui/g22/pkg-378w/files/lib/libObj.so` (sha256 `7937a86e…`, la misma que corre el arnés `pkg378`) y del volcado del arnés `analysis/gui/g22/harness/w378/guest.log` (líneas 12775–12802). Sin REA, sin VM, sin cámara.

## 1. Qué hay en `0x5b6242` (VERIFICADO)

- Es `ux::wgtsys::Widget::calcWorldClipArea(float&, float&, float&, float&)` (`0x5b6224`, 74 B): si el bit 1 de `[this+0x20]` (región pasiva, `setPassiveRegion`) está activo, escribe 0 en los cuatro `float&`; `0x5b6242` es `str.w r3,[r9]`, con `r9` = 5.º argumento leído de la pila.
- Registros del fallo: `pc=…242`, `lr=…23d` (vuelta del `bl` interno de `0x5b6238`: la función se ejecutó desde su entrada), `addr=0x2`, **`r1=0x0205cb2f`**. Un `float&` válido es una dirección de pila alineada; `0x0205cb2f` es impar y `0x2` no es puntero: **los argumentos no son los de `calcWorldClipArea`**.
- Ningún código de `libObj` llama a `0x5b6224` directamente; solo aparece en vtables (`R_ARM_ABS32` en `0xfe6ad4`, `0xfe6b8c`, … 10 clases). En la vtable de `Widget` (punto de dirección `0xfe6a88`, typeinfo `0xfe6b28`) es la **ranura `+0x4c`** (`setMode` virtual es `+0x18`, `reset` `+0x48`).

Conclusión: el cuelgue es una **llamada virtual mal despachada**: alguien llama a la ranura `+0x4c` de un objeto que espera de otra clase (con un `ID`/valor en `r1`, p. ej. `0x0205cb2f`), y el objeto real es un `Widget` simple. Es la firma de un índice fuera de rango o de un `static_cast` sobre un widget hijo que no existe con el tipo esperado; no de un desbordamiento de datos de `libObj`.

## 2. Lo que no se pudo localizar (NO_VERIFICADO)

- El llamador. La pila del arnés es un barrido de palabras (no una cadena de marcos): `0x5b623d` es el `lr` interno, `0x5b5f97` (vuelta del `blx [vt+0x18]` de `Widget::setMode`) y `0x1221c7` (`ViewBase::onLayoutChanged`, `blx [vt+0x98]`) pueden ser restos. `libObj` tiene 3 318 cargas `[rX,#0x4c]`; sin `sp`/`r4–r11` ni contenido de pila no se puede elegir.
- Qué arreglo concreto (tamaño de array, número de widgets de página) evita el fallo con 13 páginas. Hipótesis principal sin cambios (G36 §7): la plantilla de la carpeta crea un número fijo de widgets de página/fila y la página ≥ 7 indexa uno que no existe. No hay parche de `libObj` seguro sin el llamador: **no se construye**.

## 3. Arreglo mínimo para las 13 gammas: ya está en el 3.79

No hace falta tocar `libObj`: el 3.79 (G36 §8, 6 páginas, ≤ 7 opciones por fila) parte Gamma en `Movie/Cine3` y `Cine4/S-Log3` (Cine4, ITU709, ITU709(800 %), S-Log2, S-Log3), así que las 13 gammas son elegibles sin pasar de 6 páginas, y el arnés abre su carpeta PP sin fallo (G22 §5.18z″). Falta instalarlo (requiere autorización) y comprobar en cámara la elección de S-Log3 (G32-C).

## 4. Siguiente paso para la causa exacta

En el arnés (otro agente, VM): volcar en la señal 11 `sp`, `r4–r11` y 256 B de pila, o poner un punto de parada en `0x5b6224` con el 3.78 y leer `lr` real; con el llamador, buscar el array/tope de páginas y decidir si merece parchearse (solo si se quieren > 6 páginas).
