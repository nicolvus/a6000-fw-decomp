# S71 — recorrido de los 12 puntos abiertos con REA/capstone (21-10-2026)

Método: desensamblado Thumb lineal (capstone) sobre `av-cam.bin` A6000 fw3.21 (base `0x43541000`) y A7S fw3.20; REA no aportó (funciones Thumb sin reconocer). Scripts en esta carpeta; 3 tests en `tests/test_s101_pending.py`.

| # | Punto | Estado | Resultado |
|---|---|---|---|
| 1 | Escritor del bloque de 12 u16 `0x437876dc()+0xdd0` | **CERRADO (escritor)** | Lo escribe el constructor **`0x437b1048`** (llamadores `0x437b4938`, `0x438404ce`), byte a byte: `dd0←r8+0x2eb`, `dd1..dd6←r8+0x3f0..0x3f5`, `dd7..dda←r8+0x2ec..0x2ef`, `ddb..de0←r7+0x6af`, `de1..de7←r0+0xa..0x10`. Son datos de estado de captura, no constantes. **NO VERIFICADO:** el significado físico de cada byte. `block_dd0_sources.py`. |
| 2 | Consumidor de P4C en el BIONZ | **SIN AVANCE** | 45 `gpio_get` y 43 `gpio_cfg` con pin variable; S55 ya mostró que `GPIO_9` no tiene lector GPIO. El consumo probable es por interrupción o hardware del CIS, fuera de lo que REA ve. `gpio_calls.py` (heurística gruesa). |
| 3 | Bandera `0x800000` de `+0x740` (A6000) vs `+0x748` (A7S) | **SIGUE ABIERTO (rectificado)** | La copia en bloque `0x438acc24` (A6000) / `0x4389efc2` (A7S) es de un bloque de parámetros `0x730–0x75f` con **mapa idéntico en ambos modelos** (`copy_map.py`: `0x740←0x133`, `0x748←0x13d` en los dos). No es la estructura de captura desplazada +8 de S52, así que **no contradice S52**: el `+0x740` de captura de A6000 sigue sin escritor directo. El escritor de `r4+0x133` en el origen (`0x438de020`, evento `r5+0xb==1` ⇒ `0x133=1`, `0x124=2`) y su homólogo A7S (`0x438cae1e`, escribe `0x137`/`0x128`) son del mismo bloque de parámetros. |
| 4 | Puntero guardado del bloque `0x43edf684` | **CERRADO (S70)** | Sin lectores de `+0x238/+0x280` ni vía accesores ni copia. Ver `analysis/s101_shutter_type/block238/`. |
| 5 | Llamadora `0x437881a8` y handler `0x43802614` | **CERRADO** | `0x437881a8` es la *instrucción* `bl 0x43804610` dentro de la secuencia de inicialización de módulos (tras `0x437e18b4`, antes de `0x4378f9b4`): se ejecuta **una vez al arrancar**. El handler `0x43802614` es el comando **`0x402e`** (tabla `0x43fff4c0`), que guarda `[r0+8]` en `+0x280`. |
| 6 | Productor del payload (`0x43789cc0`, ID `0x301d7`) | **PARCIAL** | `0x43789cc0` **no tiene llamadores directos** (se invoca por tabla/callback). El literal `0x301d7` está en pools `0x4378a030` y `0x4378a4a8` (registro de ID). Falta seguir el registro. `backup_and_producers.py`. |
| 7 | Lectores de `Backup_read` para `0x3e0005` | **CERRADO** | Solo **2 llamadores**: `0x437dbed4` y `0x437dbff4`. Leen un buffer de `0x18` B tratado como **cadena terminada en NUL** (longitud por `strlen` manual) y alimentan `0x437dca84`: parece un identificador/nombre, **no** un ajuste de obturador. NO VERIFICADO el contenido. |
| 8 | Cadena JPEG/DCF/rollback tras `WriteStill` | **NO ABORDADO** | Sin relación con el obturador; sigue como en S20–S21. |
| 9 | Frontera DMM/OSAL (S35–S38) | **NO ABORDADO / BLOQUEADO** | S48 ya determinó que los slots `+0x1e8/+0x1ec/+0x200` los rellena el cargador/host, no `av-cam.bin`; REA no puede ir más allá. |
| 10 | Grafo de dependencias entre módulos | **NO ABORDADO** | Datos disponibles (`analysis/s79_modules/module_map.json`), falta construir el grafo. |
| 11 | Siglas pendientes (ADF, IDT, VDF…) | **NO ABORDADO** | Requiere documentación externa; no se deduce de los binarios. |
| 12 | Categorías/IDs de `libBizFw.so` | **YA CUBIERTO por otros agentes** | S98 (`analysis/s98_bizfw`) y S100 (`analysis/s100_adf_contract`) lo resolvieron tras la nota «sin tocar» de PROGRESS. |

**Rectificación (punto 3):** en una primera versión de este informe se afirmó que A6000 «sí escribe `+0x740`» y que S52 era incompleta. Es falso: el bloque copiado tiene los mismos desplazamientos en ambos modelos, por lo que no es la estructura de captura de S52. S52 sigue vigente. Lo verificado es solo el mapa de copia y el escritor de estado `0x438de020`.

**Límites:** análisis lineal con capstone (puede perder código tras datos); no se ha usado REA en la sesión; sin cámara. S51 se mantiene.

## Cierre (misma fecha)

| # | Estado final | Detalle |
|---|---|---|
| 2 | **CERRADO como bloqueado** | 45 `gpio_get`, 43 `gpio_cfg`, 3 `gpio_set`, todos con pin en variable; S55: ningún par con bit 9 fuera del banco 0 ⇒ `GPIO_9` sin lector GPIO. El consumo de P4C no pasa por estas primitivas; hace falta traza pasiva (hardware). |
| 6 | **CERRADO** | `0x301d7` se registra en dos funciones de arranque: `0x43789fde` (servicio vía `0x43561298`) y `0x4378a3d0` (vía `0x435612b4`), ambas envoltorios del servicio importado `+0x1ec` que, según S48, rellena el cargador/host. El productor original queda fuera de `av-cam.bin`. |
| 8 | **CERRADO como fuera de alcance** | Cadena JPEG/DCF/rollback sin relación con el obturador; se mantiene el estado de S20–S21. |
| 9 | **CERRADO como bloqueado** | Slots `+0x1e8/+0x1ec/+0x200` rellenados por el cargador (S48); no ampliable con REA. |
| 10 | **CERRADO** | `analysis/s101_shutter_type/graph/module_graph.md` (348 módulos, 340 aristas; INFERENCIA por menciones en trazas). |
| 11 | **CERRADO como no resoluble** | Sin expansiones creíbles en los binarios; `analysis/s101_shutter_type/graph/siglas.py`. |
| 12 | **CERRADO** | Cubierto por S98/S100. |

## Continuación: cómo se decide el «tipo» de mecanismo en A6000 y A7S (misma fecha)

**VERIFICADO (bytes):**
- **A7S** `0x43813e8c…0x43813ea2`: `cap+0x78c = 0x4379ec04([G+0x250], cap)`; si el resultado es `2` ⇒ `cap+0x748 = 1`. La función `0x4379ec04` devuelve `2` cuando un byte `[X+0x7a]` (X vía GOT) es distinto de cero (registra un aviso con `0x438f7114(…, 2)`), devuelve `0` si `[cap+0x4b84]` ya está fijado o `cap+0x785` es 0, y en otro caso una tabla de 2 entradas indexada por `[G+0x250]`.
- **A6000** `0x4379316a…0x43793296`: **sí existe un selector de tipo**, pero distinto: con `v = [G+0x808] & 7`, `tbb` (tabla `0d 1c 60 7b 83 8e`) ⇒ `v=1` ⇒ `cap+0x784 = 2` (`0x43793196`); `v=2..6` ⇒ `cap+0x784 = 1`; en otro caso `0`. Tras asignar el tipo no hay almacenamiento de bandera `+0x740` (los `str [..,#0x740]` de A6000 en `0x4373662a/0x43736738` son desplazamientos de un historial de pasos `+0x73c→+0x740`).
- La A6000 **no tiene el camino «byte `+0x7a` ≠ 0 ⇒ tipo 2 ⇒ bandera»**: el tipo 2 de A6000 depende de `[G+0x808]&7 == 1`, no de ese byte.

**INFERENCIA:** en A7S el byte `+0x7a` es la opción SilentShutter ON (S53: opciones On/Off identificadas en `CautionConfig.so`); A6000 la omite en el selector. **NO VERIFICADO:** qué ajuste es `[G+0x808]&7` (candidato: modo de obturación mecánico/EFCS), y si `cap+0x784 = 2` en A6000 cambia algo físico (Darwin A6000 valida tipos 1/2/3, S52).

Siguiente: identificar `G+0x808` (escritores y el menú que lo fija) y comprobar si el camino de A6000 para `cap+0x784 == 2` coincide con el de A7S aguas abajo.

## `G+0x808`: el campo que decide el tipo en A6000 (`pic_field_users.py`)

**VERIFICADO (bytes):**
- `G = 0x43e9b548` (resuelto del literal PIC de `0x4379315a`): es la **instantánea «actual»** de S64 (raíz `R` de S39–S47). El campo es `0x43e9bd50` (RAM `0x83e9bd50`) y el tipo se guarda en `0x43e9bccc` (`G+0x784`).
- En la imagen ambos valen `0` ⇒ por defecto `([G+0x808]&7)=0` ⇒ **tipo 0** (rama sin mecanismo, S54).
- Lectores PIC de `G+0x808`: solo la función `0x43792a0c` (`0x43793106`, `0x43793160`, `0x43793202`, `0x4379348a`, `0x437934b8`); lectores de `G+0x784`: `0x4378f5bc/c8`. **Ningún escritor PIC** de `G+0x808`: se rellena en tiempo de ejecución por copia indirecta (la copia de 0x560 B de S64 no lo cubre: `0x808 > 0x560`).
- Los `strb [..,#0x808]` del resto del binario (`0x43868ae4`, `0x4395bf9a`, `0x4395d6d0`…) son de otras instancias del mismo tipo de objeto (tabla de campos `0x644/0x704/0x754/0x7b0/0x808/0x8d8`), no de `G`.

**INFERENCIA:** `([G+0x808]&7)==1` ⇒ `cap+0x784=2` en A6000. Un experimento mínimo en cámara sería escribir `1` en `0x83e9bd50` y ver si cambia el tipo (`0x83e9bccc`→2) y el comportamiento del obturador; **no se ha hecho**: requiere tu autorización, backup de NVRAM previo y comprobar que `0x83e9bd50` está viva. S64 ya forzó otros campos de la misma instantánea sin efecto, pero no consta `+0x808` entre ellos.

Siguiente (estático): localizar quién rellena `G+0x808..0x80d` (copia de la instantánea desde un mensaje de menú, `0x43868ae4`/`0x43868c5e` son manejadores de comando con campos `+0x80b/+0x80c`).

## ¿Quién rellena `G+0x808..0x80d`? (estático, parcial)

**VERIFICADO (bytes):**
- `0x43792a0c` (única lectora PIC de `G+0x808`) llama a `0x43804c5c(r6)` en `0x43792d9e`: copia el bloque de ajustes de 0x560 B a la instantánea `G` conservando algunos campos (`+2,+4,+6..+0x16`). Esa copia **no** alcanza `+0x808`.
- No existe ningún `strb/str [..,#0x808]` con base PIC `G` en el binario. Los almacenes a `+0x808` se reparten entre otras instancias del mismo tipo de objeto: tabla de valores por defecto `0x644/0x704/0x754/0x7b0/0x808/0x8d8` (`0x4395bf9a`, `0x4395d6d0`, `0x43b56042`, base `0x43f29454`), contadores (`0x439aeeac`), y **constructores de petición** `0x43868a30` y `0x43868b78`.
- `0x43868a30` (llamada por `0x43868e00`, que a su vez llaman nueve sitios: `0x4385a710`, `0x4385aa66`, `0x4385adce`, `0x438e6874`, `0x438e70f2`, `0x438e71a6`, `0x43b23430`, `0x43b23710`, `0x43b23790`) rellena una estructura destino `r5` con `+0x3f8,+0x3fa,+0x3fc,+0x3fd`, `+0x80a` (2 ó 1 según un `tbb` sobre `ctx+0x2bc`, valores ≤4), `+0x80b`, `+0x80c` (bytes `cmd+0x31/+0x32` si no son 0), y **pone `+0x808` y `+0x80d` a 0**. `args_to_g.py`: ninguno de los 9 llamadores pasa `G` literal por argumento.

**INFERENCIA:** el layout `+0x808..+0x80d` de `G` coincide con el de esa estructura de petición; es probable que `G` sea (o reciba una copia de) un objeto «petición/parámetros» que, mientras no cambie, deja `+0x808=0` (tipo 0), y que el valor 1 solo aparezca por una orden concreta de la ruta de captura (lo que habría que ver con P1 del [plan de pruebas físicas](../../docs/capture/physical-test-plan.md)). **NO VERIFICADO:** que `r5` de `0x43868a30` sea `G` (llega por una variable local de los 9 llamadores), y quién lo copia a `G`.

Siguiente estático: seguir `r5` de `0x43868e00` en `0x4385a710`/`0x438e6874` hasta su origen (variable local o objeto global) y buscar la copia hacia `G`.

## Barrido final de escritores de `G+0x805..0x80e` (`pic_field_users.py`, `big_copies_to_g.py`)

**VERIFICADO (barrido PIC de todo `av-cam.bin`):** no existe ningún `str/strb/strh` con base PIC `G=0x43e9b548` y desplazamiento `0x805..0x80e`; solo hay lecturas: `G+0x809` bits 4–6 (`0x43790ac6`), `G+0x80c` (`0x43790654`, `0x43790ee6` bit `0x40`), `G+0x80e` bit 0 (`0x437904a8`), `G+0x808` (`0x43793106/60/202`, `0x4379348a`) y la palabra de banderas `G+0x804` (que sí se modifica por PIC en `0x4378ea1e` y `0x4379009c`, bit 1). Tampoco hay `memcpy` (`0x439c5320`) con tamaño `0x800..0x2000` y destino PIC dentro de `G`.

**Conclusión (INFERENCIA fuerte):** los bytes `G+0x808..0x80e` no los escribe código de `av-cam.bin` con acceso directo: llegan por un puntero a `G` pasado como argumento (p. ej. el constructor de petición `0x43868a30`, cuyo layout coincide) o por copia de estructura a través de otra función. El valor 0 de la imagen se mantiene hasta que esa ruta lo cambie; por eso **P1 del plan físico** (observar `0x83e9bd50` durante los cambios de menú) es la forma directa de saber qué lo gobierna.

## Nota: los llamadores de `0x43868e00` son etapas de captura

`0x4385a630`, `0x4385a924` y `0x43b2335e` (que llaman a `0x43868e00`) no tienen `bl` directo: aparecen como punteros en tablas de etapas (`0x4400b60c` → etapa id `3`; `0x4400b63c` → etapa `0x10`; `0x4400ef60` → etapa `0x11`; la etapa `2` apunta a `0x438e67c4`). Son, por tanto, las etapas «construir petición» del pipeline de captura (S76/S52: etapas `0xc8`, `0xc9`), con 12+ argumentos por pila. Quien instancia la estructura destino (`r5`) es el motor de etapas, lo que explica que no se vea ninguna escritura directa en `G`. **NO VERIFICADO:** que esa estructura sea `G`; se resuelve con P1.
