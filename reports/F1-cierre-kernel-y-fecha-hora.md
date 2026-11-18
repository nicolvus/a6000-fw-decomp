# Cierre F1: servicios de kernel sin responder y página Fecha/Hora

**Proyecto:** Sony A6000 / harness GUI (scripts/gui/harness/)  
**Subagente:** 2 de 2  
**Fecha:** 18-11-2026  
**Metodología:** Análisis estático (llvm-objdump / readelf / strings / grep). REA no disponible (sesión_daemon no responde en este subagente). REA primero no aplicable.

---

## 1. Parte A — Servicios de kernel (criterio F1)

**Criterio de cierre F1 (§7 de docs/gui/g22-arnes-ui-qemu.md):**
> "Arranque sin ninguna línea 'descartado'/'sin modelar'"

El shim registra dos tipos de línea problemática:
- `"descartado"` — `ioctl_in` case 4 (snd_msg), línea 715 de sonyshim.c: cola de kernel sin acuse ni buzón.
- `"sin modelar"` — `backup_service` default (línea 215) y op=5 fallido (línea 214).

### 1.1 `0x7a0020` — input.ko

| | |
|---|---|
| **Qué hace el shim hoy** | `KEYINIT` (envía estados iniciales de tecla vía `mbx_post_raw`, activado por `KEYINITON`/`KEYINITAFTER`) y `INJECT` funcionan. Caso especial `FRONTRM` con orden `0x0c000003` atendido en las líneas 705–709 (reenvía al lector de entrada). Pero cualquier `snd_msg` genérico a `0x7a0020` cae al `default` del `switch` de `case 4` y emite **línea 715: `(descartado)`**. |
| **Qué respuesta falta** | Un `snd_msg` síncrono a `0x7a0020` necesita un acuse o un buzón donde dejar la respuesta, igual que las colas de `ACKQ`. Los clientes (`libObj` `I-InputMain` en `libObj+0x806f88`) leen mensajes de 0x18 B `{w0 clave, w1, w2 valor, w3, w4 índice físico, w5 indicadores}`; el driver responde con estado en `w2`. |
| **Estado** | **NO_VERIFICADO** (sin REA, no se confirmó el formato exacto de respuesta que espera `I-InputMain`). |
| **Código propuesto** | Añadir `0x7a0020` a `ACKQ` por defecto (línea 290: `"d9016e,7a0029,61003c"` → `"d9016e,7a0029,61003c,7a0020"`) o bien un `case` específico antes del `default` que haga `mbx_post(0x7a0020, m, 0)` y retorne 0. Si la primera palabra del cuerpo es una cola dinámica, usar ese buzón; si no, acuse genérico con estado 0. |

### 1.2 `0x5700f9`

| | |
|---|---|
| **Qué hace el shim hoy** | No aparece en ningún `case` del `switch` de `ioctl_in` (case 4) ni en `ACKQ`. Cualquier envío cae al `default` → **línea 715: `(descartado)`**. |
| **Qué respuesta falta** | Sin documentación de qué cliente lo usa ni qué espera. Hipótesis (INFERENCIA): cola de servicio del kernel que espera acuse genérico como `0x61003c`. |
| **Estado** | **NO_VERIFICADO** (no se halló referencia en `libObj.so` ni en `libBizFw.so` por análisis estático disponible). |
| **Código propuesto** | Añadir a `ACKQ` por defecto: `"d9016e,7a0029,61003c,7a0020,5700f9"`. O un `case` específico que haga `mbx_post(0x5700f9, m, 0)` si el cuerpo contiene una cola dinámica en las primeras 6 palabras. |

### 1.3 `0x5a0048`

| | |
|---|---|
| **Qué hace el shim hoy** | Igual que `0x5700f9`: sin `case` ni `ACKQ` → **línea 715: `(descartado)`**. |
| **Qué respuesta falta** | Igual: sin información del cliente. INFERENCIA: acuse genérico. |
| **Estado** | **NO_VERIFICADO**. |
| **Código propuesto** | Añadir a `ACKQ`: `"...,5700f9,5a0048"` o `case` con `mbx_post(0x5a0048, m, 0)`. |

### 1.4 `0x16f4010`

| | |
|---|---|
| **Qué hace el shim hoy** | Igual: sin `case` ni `ACKQ` → **línea 715: `(descartado)`**. |
| **Qué respuesta falta** | Igual. |
| **Estado** | **NO_VERIFICADO**. |
| **Código propuesto** | Añadir a `ACKQ`: `"...,5a0048,16f4010"` o `case` con `mbx_post(0x16f4010, m, 0)`. |

### 1.5 `0x61003c`

| | |
|---|---|
| **Qué hace el shim hoy** | Ya está en `ACKQ` por defecto (línea 290). Recibe acuse genérico vía `mbx_post(m, w[0]==0x61003c)`, que pone `body[-1]=0x61003c` y estado 0 en la media palabra alta. |
| **Qué respuesta falta** | El comentario en la línea 671–673 advierte: "a `0x61003c` la misma respuesta hace saltar la aserción de `0x6a25d2`; modelarla cuando se conozca su formato". Es decir, el acuse genérico **no es suficiente** para `0x61003c` (`dmpNative::InternalCmd`). La respuesta real debe llevar `req_id` en `+6`, `phys` en `+0x10` y `tamaño` en `+0x14` (§5.18z⁸/⁹ de la doc). |
| **Estado** | **INFERENCIA** (documentado en §5.18z⁸/⁹ pero sin verificación de bytes de respuesta real). |
| **Código propuesto** | Sustituir el acuse genérico por el formato específico de `InternalCmd`: `body[4] = next_phys` (desde `0xa0000000` en adelante), `body[5] = req[1]`, `((unsigned short *)body)[3] = req[5] & 0xffff`, `body[-1] = 0x61003c`. Esto ya está parcialmente implementado en `mbx_post` (líneas 273–286) pero solo se usa cuando `req_id0` es verdad; para `0x61003c` se debería forzar ese camino. |

### 1.6 backup `op 1`

| | |
|---|---|
| **Qué hace el shim hoy** | No hay `case 1` en `backup_service` (líneas 185–218). Cae al `default` → **línea 215: `(sin modelar)`**. |
| **Qué respuesta falta** | Según `libbackup.so` (strings), `op 1` corresponde probablemente a `Backup_get_datasize_multi` (obtener tamaño de varios registros). `m[0]=op, m[1]=resultado, m[2]=nº, m[6+]=ids`. Debería devolver en `m[1]` el tamaño total o por registro. |
| **Estado** | **INFERENCIA** (por orden de los símbolos en `libbackup.so`: `get_datasize`=0, `get_datasize_multi`=2, `get_attribute`=3…; el shim usa índices desplazados, ver §5.18z¹⁰). |
| **Código propuesto** | Añadir `case 1:` en `backup_service` que recorra los `id[]` en `m[6..]`, sume los `len` de cada `bk_find(id[k])` y devuelva el total en `m[1]`; o bien devuelva `0` si no hay registros (evitando la línea de error). |

### 1.7 backup `op 5`

| | |
|---|---|
| **Qué hace el shim hoy** | Hay `case 5` (líneas 205–214) que implementa `read_multi`, pero solo funciona si `BKMULTI=1` o si ambos punteros son legibles. En cualquier otro camino emite **línea 214: `(sin modelar)`** y retorna sin poner `m[1]`. |
| **Qué respuesta falta** | `libObj` (`InfraMediaConfig`, `libObj+0x13cf18`) llama a `Backup_read_multi` con 64 ids de 1 B y espera `m[1] = nº de ids leídos` (ver comentario en línea 213: "retorno = nº de ids leídos"). Sin `BKV` o sin punteros legibles, no devuelve nada. |
| **Estado** | **INFERENCIA** (documentado en el shim, sin verificación contra bytes reales de la llamada). |
| **Código propuesto** | Hacer que `case 5` siempre intente leer los ids disponibles (sin exigir `BKMULTI=1`), rellenando el búfer destino con los datos de cada `bk_find` y devolviendo el contador en `m[1]`. Si algún id no está en la tabla, parar y devolver lo leído hasta entonces (como sugiere el comentario: "la lista acaba en el primer id que no está en la tabla"). |

### 1.8 `snd_sync_direct 0x910042`

| | |
|---|---|
| **Qué hace el shim hoy** | Atendido en `direct_service` (líneas 231–236): devuelve hora en µs (`CLOCK_MONOTONIC`) en `m[6..7]` para `qid=0x910042`, y duerme hasta plazo absoluto para `0x910041`. |
| **Qué respuesta falta** | Nada. **VERIFICADO** (funciona, no emite líneas de error). |
| **Estado** | **VERIFICADO**. |

---

## 2. Parte B — Página Fecha/Hora

### 2.1 Síntoma

La página «Ajuste fecha/hora → Fecha/Hora» muestra `31-12-2037 0:00` (capturas `img/g22-fecha-hora-nvram.png` y `img/g22-fecha-hora-fecha-actual.png` en el repositorio) en vez de `2014-01-01` (fecha inicial de fábrica) o la hora real del anfitrión.

### 2.2 Datos del modelo (VERIFICADO, §5.18z¹¹)

Con el diagnóstico `GMIDUMP=@M018` al abrir «Fecha/Hora», `ModelClock` entrega datos coherentes:

| Consulta | Parámetros | Valor |
|---|---|---|
| `get_date` (`0x90013d`, orden 2) | `0x101…0x106` | `2026, 11, 13, 2, 50, 33` (hora del anfitrión UTC, vía `date_local()`) |
| `INFO_INITIAL_DATE_TIME` (`0x4f1584`, info 1) | `0x101…0x106` | `2014, 1, 1, 0, 0, 0` (fecha inicial de fábrica) |
| | `0x108` (área) | `0` |
| | `0x109` | `0` |

**Conclusión:** `ModelClock` entrega datos correctos. El `31-12-2037` se genera en la conversión a pantalla del widget `PAS_BtnDateTime`, no en el modelo.

### 2.3 Dirección de la función de conversión

En `viewUnified2.so` (fw 3.21, `analysis/camera-extract/usr/lib/viewUnified2.so`):

| Símbolo | Dirección | Descripción |
|---|---|---|
| `_ZN15PAS_BtnDateTime4castEPN2ux6wgtsys6WidgetE` | `viewUnified2+0x2e2964` | `static_cast` del widget `PAS_BtnDateTime` |
| `_Z21Check_PAS_BtnDateTimePN2ux6wgtsys6WidgetE` | `viewUnified2+0x2e2ed2` (aprox.) | Comprobación/tipo del widget |
| `PAS_BtnDateTimeConverter` (string) | `viewUnified2+0x3a9506` | Nombre del conversor |
| `WIDGET_CLASS_ID_PAS_BTNDATETIME` | `viewUnified2+0x3b26b7` | ID de clase del widget |
| `PAS_BtnDateTime` (string) | `viewUnified2+0x3cf884` | Nombre del widget |

La función que convierte `0x101…0x106` (año, mes, día, hora, min, seg) a pantalla está dentro de `PAS_BtnDateTime` o de su conversor asociado (`PAS_BtnDateTimeConverter`), **no localizada con precisión** (falta REA/Ghidra sobre `viewUnified2.so`).

**Hipótesis del `31-12-2037` (INFERENCIA, §5.18z¹¹):** La widget toma la fecha inicial (`2014-01-01 0:00`) y le resta algo (posiblemente el área horaria o un ajuste de minuto), saliendo por debajo del mínimo representable y dando la vuelta al máximo de `2037-12-31`. Esto cuadra con el `0:00`, pero no se verificó el caso `23:59` (cuando la fecha inicial era la del anfitrión).

### 2.4 `get_date` (`0x90013d`) y `0x900141` — qué falta

| | |
|---|---|
| **`0x90013d` orden 2** (`osal_get_date`) | **Atendido** en `direct_service` (líneas 249–255 de sonyshim.c): rellena `+0x14` año u16, `+0x16` mes, `+0x17` día, `+0x18` hora, `+0x19` min, `+0x1a` seg, `+0x1c` tipo. Devuelve hora del anfitrión avanzada con `CLOCK_MONOTONIC`. **VERIFICADO** (medido con `WAITLOG`/`WLALL`: `get_date -> 2026-11-12 6:37:32 tipo 1`). |
| **`0x900141` orden 3** (`osal_get_init_date`) | **Atendido** (ver §5.18z¹⁰ y `g22-respuestas-59000e-900141.md` §3.2): `direct_service` responde con `date_local()` en `+0x14…+0x1a`, `+0x1c=0`, `+0x1e…+0x23` a cero. Con NVRAM real sale `2014-1-1 0:00, área 0xfed4 (−300), verano 0`. **VERIFICADO** (aparición de línea `direct 0x900141 get_date -> …` confirmada con `FULLLOG=1`). |
| **`0x90013e`** (`osal_reg_datechg_notify_cb`) | **NO modelado.** La cola `0x90013e` aparece en libObj (offsets `0x4470b8`, `0x4470fc`, `0xb58f30`, `0xb58f74`) como parte de una tabla de registros de callback. No hay `case` en `direct_service` ni en `ioctl_in` que la atienda. |
| **Estado «asentado»** (`0x1070140`) | No se modela qué guarda el estado de reloj asentado. `BKSET=1070140=1` lo fuerza por env var, pero no hay persistencia automática. |

### 2.5 Qué falta para que Fecha/Hora muestre coherente

1. **Modelar `osal_reg_datechg_notify_cb` (cola `0x90013e`):** el shim debe entregar los mensajes a `0x90013e` al callback registrado (`libObj+0xb58b90`, ver §5.18z⁸). Hoy `direct_service` no captura `0x90013e` ni lo entrega vía `cb_deliver`.

2. **Proveer la fecha inicial (orden 3 de `0x900141`) con datos de NVRAM:** ya implementado, pero hay que verificar que la página la lee y la muestra en vez de ceros.

3. **Arreglar la conversión del widget `PAS_BtnDateTime`:** el `31-12-2037` se produce en `viewUnified2.so`. Opciones:
   - a) Parchear `viewUnified2.so` (`PATCHFN`) en el conversor/limite para no desbordar.
   - b) Proveer desde el shim una fecha que el widget convierta correctamente (por ejemplo, la fecha inicial `2014-01-01` en vez de `0-0-0`).
   - c) Localizar exactamente la instrucción de conversión en `PAS_BtnDateTime` (+0x2e2964) y su conversor, y entender el cálculo que produce `2037`.

4. **Modelar el ajuste de hora desde el menú:** no se llegó a ver la orden de escritura (Backup `op 8` escribe `NV id hex`, pero el cambio de ajuste de fecha viaja por otra ruta no respondida — probable ADF/av-cam).

### 2.6 Código propuesto para sonyshim.c

**A) Añadir `0x90013e` en `direct_service`** (después del bloque de `0x900141`, aprox. línea 258):

```c
    else if (m[0] == 0x28 && qid == 0x90013e) {  /* osal_reg_datechg_notify_cb: aviso de cambio de fecha */
        unsigned short *h = (unsigned short *)m;
        h[9] = 0;  /* resultado 0 en +0x12 */
        /* +0x14: orden (0/1), +0x16: valor. No hay datos que devolver más allá del acuse. */
        LOG("direct 0x90013e datechg_notify orden=%u val=%u", h[8], h[9] /* o m[8]/m[9] según layout */);
    }
```

**B) Asegurar que `0x900141` orden 3 use `bk.tbl` real** (ya implementado per §5.18z¹⁰, verificar que `bk_find` devuelve los ids `0x90000e…0x900005` con los tamaños correctos: 2 B para `0x90000e/0x90000a/0x900005`, 1 B para el resto).

**C) Opcional: forzar `DATETYPE=3` por defecto** para que la página «Ajuste fecha/hora» no aparezca desactivada («Función desactivada actualmente»). Hoy el defecto es `1`.

---

## 3. Resumen de cambios necesarios en sonyshim.c

| Servicio | Línea actual | Problema | Cambio propuesto | Etiqueta |
|---|---|---|---|---|
| `0x7a0020` | Línea 715 (descartado) | snd_msg sin acuse | Añadir a ACKQ o case con `mbx_post` | INFERENCIA |
| `0x5700f9` | Línea 715 (descartado) | Sin case ni ACKQ | Añadir a ACKQ | NO_VERIFICADO |
| `0x5a0048` | Línea 715 (descartado) | Sin case ni ACKQ | Añadir a ACKQ | NO_VERIFICADO |
| `0x16f4010` | Línea 715 (descartado) | Sin case ni ACKQ | Añadir a ACKQ | NO_VERIFICADO |
| `0x61003c` | ACKQ genérico | Formato de respuesta insuficiente | Formato `InternalCmd` específico (phys/tamaño/req_id) | INFERENCIA |
| backup op 1 | Línea 215 (sin modelar) | Sin case 1 | Añadir `case 1` (get_datasize_multi) | INFERENCIA |
| backup op 5 | Línea 214 (sin modelar) | Exige BKMULTI=1 | Hacer read_multi siempre operativo | INFERENCIA |
| `0x910042` | Líneas 231–236 | OK | Ninguno | VERIFICADO |
| `0x90013d` ord 2 | Líneas 249–255 | OK | Ninguno | VERIFICADO |
| `0x900141` ord 3 | Implementado (§5.18z¹⁰) | OK | Verificar con `FULLLOG=1` | VERIFICADO |
| `0x90013e` | No modelado | Falta datechg_notify_cb | Añadir case en `direct_service` | NO_VERIFICADO |

---

## 4. Límites de evidencia

- Todo el análisis es estático sobre `libObj.so` (fw 3.21, md5 `eb12512e…`) y `viewUnified2.so` sin ejecución de firmware ni cámara.
- Las respuestas propuestas para `0x5700f9`, `0x5a0048`, `0x16f4010`, `backup op 1/5` y `0x61003c` son INFERENCIAS basadas en la estructura del shim y la documentación; no se verificaron contra bytes reales de llamadas de cliente.
- La función exacta de conversión de `PAS_BtnDateTime` en `viewUnified2.so` no fue localizada con precisión (falta REA/Ghidra).
- No se tocó `scripts/gui/harness/android/`.