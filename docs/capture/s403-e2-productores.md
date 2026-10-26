# S403 · E2 — productores del mensaje `0x10000005` (RecordImage/RecordStill)

Estado: **cerrado con límite**. Script: [e2_producers.py](../../analysis/s403_pendientes/e2_producers.py) → [e2_producers.json](../../analysis/s403_pendientes/e2_producers.json); prueba `tests/test_s403_e2_producers.py`.

## Resultado
`libObj.so` construye `MWF::ObjMsg(grupo, 0x10000005)` en cuatro sitios (ctor `0xde540` en la PLT):

| Sitio | Grupo | Publica en cola | Contexto |
|---|---|---|---|
| `0x838e66` | `0x3700` | sí (`[this+4]->vtable[+0xc](msg)`) | gestor `0x8382f8`, un `View`: despacha por código de evento; la rama del evento `0x40000018` construye el mensaje |
| `0x91c214` | `0x3a48` | sí (`[this+0x18]->vtable[+0xc](msg)`) | método `0x91c1c8` de la clase del grabador de imagen fija; llamado desde `0x91c296` y `0x91e04c` (ambos internos) |
| `0x90868a`, `0x919f4a` | `0x3500` | no | los dos constructores ya conocidos (S402): añaden parámetros y consultan `0x813a78`, sin publicar |

Otras cinco cargas del literal (`0x84fe12`, `0x8881b4`, `0x88b2cc`, `0x18b920` y `0x7c970c`, esta última con otro destino de llamada) usan un registro distinto de `r2` o no preceden a la construcción de un `ObjMsg`; no se clasificaron una a una.

El gestor `0x8382f8` compara el código con la familia `0x4000xxxx`/`0x4100000e` (que `libmpr.so` también usa; por su vecindad con las funciones de `MprIf` parecen eventos de medios, no de la tecla de disparo, sin demostrarlo). Ningún productor estático une la pulsación del obturador con `0x10000005`: la
cadena disparo → mensaje → estado 2 solo se completa en ejecución.

## Límites
- La asignación del evento `0x40000018` a una acción de usuario no se demostró; solo se vio su comparación en el gestor y su uso en `libmpr.so`.
- Se buscó el literal en pools Thumb; construcciones por `movw/movt` o por tablas de ids no se enumeraron.
