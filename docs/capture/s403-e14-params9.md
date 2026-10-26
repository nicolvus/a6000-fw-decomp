# S403 · E14/E3 — origen de los valores 2 y 3 de `params[+9]` (SetExposure IMX210)

Estado: **cerrado con límite** (E14, E3). Script: [e14_writers.py](../../analysis/s403_pendientes/e14_writers.py) → [e14_writers.json](../../analysis/s403_pendientes/e14_writers.json); prueba `tests/test_s403_e14_writers.py`.

## Resultado
Los 14 `str`/`strh` de ancho de palabra con desplazamiento `0x654` (palabra que contiene `+0x655` = `params[+9]`) se clasifican por el valor que guardan y por la forma del objeto (desplazamientos vecinos de la misma base):

| Clase | Escritores | Valor guardado |
|---|---|---|
| Bloque de parámetros (10) | `0x435c116c` (constructor `0x435c10e0`) | argumento de pila `[sp,#0x50]` |
| | `0x437d83ee`, `0x437d952c`, `0x43b1414a` | copia de `[otro_bloque+0x654]` (tres clonadores con el mismo diseño `0x63c..0x660`) |
| | `0x43b14866` | `[[this+8]+8]` (construido desde un objeto de petición) |
| | `0x438551f4`, `0x43855206` | media palabra de pila / registro sin definir en la ventana |
| | `0x43869248` | media palabra cargada de `[r2+0x20]` |
| | `0x438691ba`, `0x43b0b8ac` | 0 (reinicio del bloque) |
| Estado de FSM (4) | `0x43a471ec` (setter, estados 1/5/6/7), `0x4364af66`, `0x4364afc8`, `0x4364c27e` | otro objeto: solo usa `+0x650`/`+0x654` como «estado previo/estado» |

Ningún escritor guarda la constante 2 ni la 3 en `+0x654`, y los únicos `strb` a `+0x655` (E3) guardan 0, 1 y 4. Los valores 2 y 3 solo pueden entrar por flujo de datos desde cuatro fuentes
enumeradas: la pila del constructor `0x435c10e0` (llamado desde `0x435c4b04`), el objeto de petición de `0x43b14866`, la media palabra de `0x43854fec` y el campo `[r2+0x20]`
de `0x438690dc`. Son valores de ejecución (parámetros del disparo), no constantes del firmware.

## Límites
- La clasificación por vecinos es heurística; no se demostró tipo de objeto con RTTI.
- No se siguió el origen de las cuatro fuentes más allá del primer salto; podrían contener 2/3 solo si algún productor externo (UI/menú/ajuste) los entrega.
- `0x43855206` y `0x4364afc8` quedan sin definición local del registro guardado.
