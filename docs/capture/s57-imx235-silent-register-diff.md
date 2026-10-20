# S57-D — Configuración efectiva IMX235 normal/Silent y comparación con IMX210 (20-10-2026)

**Resultado:** el Silent de la A7S **no añade una operación de fin de integración al sensor**: selecciona dos modos de lectura dedicados (`0x4e`, `0x4f`) cuya columna es una variante mínima de los modos `0x4c/0x4d` (1–4 registros de diferencia) y distinta del modo foto `0x0b` en 33–35 de 35 registros. La diferencia funcional que «permite operar sin segunda cortina» no es recuperable del firmware a nivel de sensor; la frontera es la semántica de la dirección `0x000C` y del modo de lectura (datasheet IMX235). Pruebas: `tests/test_s57_imx210_exposure.py::Imx235Silent`; script `analysis/s57/imx235_matrix.py`; matriz S57-14, 23–26.

## 1. Estructura recuperada (VERIFICADO, bytes de A7S 3.20, sha `b857d338…103e`)
* Tabla de modos `0x43fee370`: 34 modos (`0b 37 35 38 13 1f 05 18 10 1a 07 19 32 34 33 46 01 30 03 31 0a 36 0f 12 3f 44 45 4c 4d 4e 4f 50 51 08`); IMX210 solo 13 y sin `0x4e/0x4f` (SetMode devuelve error 2).
* Matriz `0x43fee598`: filas de 40 B = `{u32 ptr, 34 valores (uno por modo), 2 relleno}`; el registro está en `ptr-4`: `{dev 0x81|0x83, 0, dirección u16 LE, dato}`. **35 registros** (34 de dispositivo `0x81` y 1 de `0x83`); la lectura lineal arrastra una 36.ª «fila» con puntero a código (`0x43de7590`, `dev 0x00`) que se excluye. S52/S56 citaron «45/69 campos» con otro criterio de recuento; aquí se cuenta registro por registro.
* Selector A7S `0x43826d58(modo, sub, tipo)`: `tipo==2` ⇒ sub 0 → **`0x4e`**, sub 1 → **`0x4f`**; sin Silent: sub 0 → `0x0b`, sub 1 → `0x35`, sub 2 → `0x17`; modo 5 → `0x0c`.
* La configuración que se transmite = (matriz por modo) + registros de SetExposure/SetRead. SetExposure A7S (`0x436f4a94`) no admite ShutMode 2 y su formateador es distinto; **no se emuló** (límite).

## 2. Columnas relevantes (valores por dirección de registro)
| dir | dev | 0x0b | 0x4c | 0x4d | **0x4e** | **0x4f** | 0x50 | 0x51 |
|---|---|---|---|---|---|---|---|---|
| 0x0000 | 81 | 14 | 00 | 01 | **00** | **01** | 00 | 00 |
| 0x0008 | 81 | 00 | 00 | 01 | **00** | **01** | 00 | 00 |
| 0x000a | 81 | 00 | 00 | 02 | **00** | **01** | 00 | 00 |
| 0x000c | 81 | 64 | 20 | 20 | **10** | **20** | 02 | 02 |
| 0x0011 | 81 | 03 | 0f | 0f | 0f | 0f | 0f | 00 |
| 0x0014 | 81 | 00 | 01 | 01 | 01 | 01 | 01 | 00 |
| 0x001c | 81 | 08 | 81 | 81 | 81 | 81 | 81 | 81 |
| 0x001f | 81 | 0c | 01 | 01 | 01 | 01 | 01 | 01 |
| 0x0029 | 81 | 00 | 23 | 23 | 23 | 23 | 2d | 23 |
| 0x002b | 81 | 14 | 46 | 46 | 46 | 46 | 42 | 46 |
| 0x002f | 81 | 36 | 3e | 3e | 3e | 3e | 3c | 3e |
| 0x0031 | 81 | 40 | 1f | 1f | 1f | 1f | 1d | 1f |
| 0x003c | 81 | 40 | 48 | 48 | 48 | 48 | 44 | 48 |
| 0x0040 | 81 | 36 | 4a | 4a | 4a | 4a | 44 | 4a |
| 0x0042 | 81 | 4c | 52 | 52 | 52 | 52 | 4a | 52 |
| 0x0045 | 81 | 4c | 32 | 32 | 32 | 32 | 1e | 32 |
| 0x0049 | 81 | 31 | 4c | 4c | 4c | 4c | cc | 4c |
| 0x0054 | 81 | 40 | 58 | 58 | 58 | 58 | 50 | d0 |
| 0x0056 | 81 | 03 | 5c | 5c | 5c | 5c | 2c | 5c |
| 0x0094 | 81 | ad | 1d | 1d | 1d | 1d | 0c | 1d |
| 0x0095 | 81 | cd | 46 | 46 | 46 | 46 | 6a | 46 |
| 0x0017 | 83 | 4a | 00 | 00 | 00 | 00 | 00 | 00 |
(Se omiten filas idénticas entre todas las columnas; la matriz completa se regenera con `python3 analysis/s57/imx235_matrix.py`.)

## 3. Diferencias (D.3, clasificación sustentada solo en comparación de bytes)
| Comparación | Filas distintas | Detalle |
|---|---|---|
| `0x4e` vs `0x0b` | 33/35 | solo coinciden dir `0x0008` y `0x000a` (=0) |
| `0x4f` vs `0x0b` | 35/35 | — |
| `0x4e` vs `0x4c` | **1** | dir `0x000C`: `0x10` frente a `0x20` |
| `0x4f` vs `0x4d` | **1** | dir `0x000A`: `0x01` frente a `0x02` |
| `0x4e` vs `0x4f` | 4 | dir `0x0000`, `0x0008`, `0x000A`, `0x000C` (bit 0 / selección sub 0 frente a sub 1) |
Vecino más próximo de `0x0b`: `0x37` (1 registro) y `0x35` (5): modos de fotografía alternativos, **no** los Silent. Clasificación: los modos Silent son *variantes de los modos de lectura 0x4c/0x4d*; el único registro que los distingue de `0x4c` es la dirección `0x000C`; las filas `0x0000/0x0008/0x000A` distinguen sub 0 de sub 1. Sin consumidores ni relaciones matemáticas identificadas, **no se asigna significado** (cambio de resolución/frecuencia/formato/temporización/sincronización: función desconocida). Antecedente: en el modo foto `0x0b`, `0x000C=0x64` (valor distinto de 0x20/0x10): el registro cambia en todos los modos de lectura.

## 4. Pulso de configuración (D.4)
La petición de pulso A7S se genera dentro de SetExposure cuando `arg+2 > 0x1000` ([informe B](s57-ssb-pulse-analysis.md)). Los modos Silent usan ShutMode 0 (S52, INFERENCIA) y la misma ruta. No se observó diferencia de orden de transmisión ni de registros repetidos entre modos (no se emuló A7S).

## 5. Comparación con IMX210 (D.5)
IMX210: 59 filas × 13 modos con direcciones `0x000–0x155`; IMX235: 35 registros × 34 modos con direcciones `0x0000–0x00CF`. **No hay correspondencia por dirección** (p. ej. IMX210 `0x01` = ID1 de modo/ShutMode; IMX235 `0x0000` es otra función) y no se copia ningún valor. Grupos funcionales equivalentes: ninguno demostrable. Cada familia tiene su propio conjunto de modos de lectura; el IMX210 no define modos «Silent».

## 6. Pregunta central (D.6)
**¿Qué diferencia funcional concreta permite a la A7S operar sin segunda cortina?** Con el firmware: (1) selecciona los modos de lectura `0x4e/0x4f` (columnas dedicadas, 33–35 registros distintos de la foto normal); (2) política de clase 0 y marca CAIF `+0x12 bit 0x20` hacia Darwin (S52/S53), que detiene el movimiento de cortinas; (3) no existe en la matriz ni en el pulso un comando adicional de «terminar integración». **Hasta aquí llega la evidencia recuperable**: no se puede decir si el IMX235 finaliza la integración por temporización interna ni qué registro lo provoca; falta el datasheet IMX235 y SetExposure/SetRead A7S emulados.

## 7. Límites
Solo estático/lectura de bytes; sin emulación del formateador/SetMode A7S; los nombres de modos `0x4c/0x4d` no se identificaron (S52 no los describe).
