# S71 — recorrido de los 12 puntos abiertos con REA/capstone (21-10-2026)

Método: desensamblado Thumb lineal (capstone) sobre `av-cam.bin` A6000 fw3.21 (base `0x43541000`) y A7S fw3.20; REA no aportó (funciones Thumb sin reconocer). Scripts en esta carpeta; 3 tests en `tests/test_s71_pending.py`.

| # | Punto | Estado | Resultado |
|---|---|---|---|
| 1 | Escritor del bloque de 12 u16 `0x437876dc()+0xdd0` | **CERRADO (escritor)** | Lo escribe el constructor **`0x437b1048`** (llamadores `0x437b4938`, `0x438404ce`), byte a byte: `dd0←r8+0x2eb`, `dd1..dd6←r8+0x3f0..0x3f5`, `dd7..dda←r8+0x2ec..0x2ef`, `ddb..de0←r7+0x6af`, `de1..de7←r0+0xa..0x10`. Son datos de estado de captura, no constantes. **NO VERIFICADO:** el significado físico de cada byte. `block_dd0_sources.py`. |
| 2 | Consumidor de P4C en el BIONZ | **SIN AVANCE** | 45 `gpio_get` y 43 `gpio_cfg` con pin variable; S55 ya mostró que `GPIO_9` no tiene lector GPIO. El consumo probable es por interrupción o hardware del CIS, fuera de lo que REA ve. `gpio_calls.py` (heurística gruesa). |
| 3 | Bandera `0x800000` de `+0x740` (A6000) vs `+0x748` (A7S) | **CERRADO (corrige S52)** | **Sí hay escritor en A6000:** copia en bloque `0x438acc24` (`strb [r3,#0x740]` ← `ldrb [r4,#0x133]`) ≙ A7S `0x4389efc2` (← `[r4,#0x13d]`), dentro de `0x438ab3e8` (llamada por `0x43af66b8`). La diferencia A6000/A7S está en el **valor de origen**, no en una rama latente. **NO VERIFICADO:** quién escribe `r4+0x133`/`+0x13d` (20 candidatos con `+0x133`). `flag748_writer.py`. |
| 4 | Puntero guardado del bloque `0x43edf684` | **CERRADO (S70)** | Sin lectores de `+0x238/+0x280` ni vía accesores ni copia. Ver `analysis/s70_block238/`. |
| 5 | Llamadora `0x437881a8` y handler `0x43802614` | **CERRADO** | `0x437881a8` es la *instrucción* `bl 0x43804610` dentro de la secuencia de inicialización de módulos (tras `0x437e18b4`, antes de `0x4378f9b4`): se ejecuta **una vez al arrancar**. El handler `0x43802614` es el comando **`0x402e`** (tabla `0x43fff4c0`), que guarda `[r0+8]` en `+0x280`. |
| 6 | Productor del payload (`0x43789cc0`, ID `0x301d7`) | **PARCIAL** | `0x43789cc0` **no tiene llamadores directos** (se invoca por tabla/callback). El literal `0x301d7` está en pools `0x4378a030` y `0x4378a4a8` (registro de ID). Falta seguir el registro. `backup_and_producers.py`. |
| 7 | Lectores de `Backup_read` para `0x3e0005` | **CERRADO** | Solo **2 llamadores**: `0x437dbed4` y `0x437dbff4`. Leen un buffer de `0x18` B tratado como **cadena terminada en NUL** (longitud por `strlen` manual) y alimentan `0x437dca84`: parece un identificador/nombre, **no** un ajuste de obturador. NO VERIFICADO el contenido. |
| 8 | Cadena JPEG/DCF/rollback tras `WriteStill` | **NO ABORDADO** | Sin relación con el obturador; sigue como en S20–S21. |
| 9 | Frontera DMM/OSAL (S35–S38) | **NO ABORDADO / BLOQUEADO** | S48 ya determinó que los slots `+0x1e8/+0x1ec/+0x200` los rellena el cargador/host, no `av-cam.bin`; REA no puede ir más allá. |
| 10 | Grafo de dependencias entre módulos | **NO ABORDADO** | Datos disponibles (`analysis/s79_modules/module_map.json`), falta construir el grafo. |
| 11 | Siglas pendientes (ADF, IDT, VDF…) | **NO ABORDADO** | Requiere documentación externa; no se deduce de los binarios. |
| 12 | Categorías/IDs de `libBizFw.so` | **YA CUBIERTO por otros agentes** | S98 (`analysis/s98_bizfw`) y S100 (`analysis/s100_adf_contract`) lo resolvieron tras la nota «sin tocar» de PROGRESS. |

**Hallazgo principal (punto 3):** la hipótesis «bandera latente sin escritor» de S52 era incompleta. A6000 y A7S **copian** ese byte con el mismo patrón desde una estructura de origen. El interruptor está aguas arriba, en quien escribe `r4+0x133` (A6000) / `r4+0x13d` (A7S), y ese es el siguiente hilo estático con más valor.

**Límites:** análisis lineal con capstone (puede perder código tras datos); no se ha usado REA en la sesión; sin cámara. S51 se mantiene.

## Cierre (misma fecha)

| # | Estado final | Detalle |
|---|---|---|
| 2 | **CERRADO como bloqueado** | 45 `gpio_get`, 43 `gpio_cfg`, 3 `gpio_set`, todos con pin en variable; S55: ningún par con bit 9 fuera del banco 0 ⇒ `GPIO_9` sin lector GPIO. El consumo de P4C no pasa por estas primitivas; hace falta traza pasiva (hardware). |
| 6 | **CERRADO** | `0x301d7` se registra en dos funciones de arranque: `0x43789fde` (servicio vía `0x43561298`) y `0x4378a3d0` (vía `0x435612b4`), ambas envoltorios del servicio importado `+0x1ec` que, según S48, rellena el cargador/host. El productor original queda fuera de `av-cam.bin`. |
| 8 | **CERRADO como fuera de alcance** | Cadena JPEG/DCF/rollback sin relación con el obturador; se mantiene el estado de S20–S21. |
| 9 | **CERRADO como bloqueado** | Slots `+0x1e8/+0x1ec/+0x200` rellenados por el cargador (S48); no ampliable con REA. |
| 10 | **CERRADO** | `analysis/s72_graph/module_graph.md` (348 módulos, 340 aristas; INFERENCIA por menciones en trazas). |
| 11 | **CERRADO como no resoluble** | Sin expansiones creíbles en los binarios; `analysis/s72_graph/siglas.py`. |
| 12 | **CERRADO** | Cubierto por S98/S100. |
