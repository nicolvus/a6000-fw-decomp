# Informe F2: página «Fecha/Hora» muestra `31-12-2037 0:00` (conversor `PAS_BtnDateTime`)

**Proyecto:** Sony A6000 / harness GUI (G22-B)  
**Subagente:** 2 de 2  
**Fecha:** 18-11-2026  
**Binario analizado:** `analysis/camera-extract/usr/lib/viewUnified2.so` (fw 3.21, sha256 `7fbfa853…`, ELF32 ARM, `VirtAddr == Offset` en el primer segmento LOAD).  
**Método:** análisis estático con `llvm-objdump --triple=thumbv7-none-eabi` sobre bytes reales del `.so`. REA/Ghidra **no disponible** para este binario (ver §Estado de REA).

---

## 1. Contexto ya conocido (no re-investigado)

- `ModelClock` entrega datos correctos (§5.18z¹¹, VERIFICADO en ejecución):
  - `get_date` (`0x90013d`, ord 2) → fecha/hora actual del host (2026-11-13…).
  - `INFO_INITIAL_DATE_TIME` (`0x4f1584`, info 1) → `2014,1,1,0,0,0`, área `0`, verano `0` (fecha inicial de fábrica, NVRAM `0x90000e/0x90000f`…).
- El shim ya atiende `0x90013d` ord 2, `0x900141` ord 3 y `0x90013e` (ver sonyshim.c, `direct_service`). `0x90013d` da `2026-11-12 6:37:32 tipo 1` (medido con `WAITLOG`/`WLALL`).
- Conclusión previa (F1, §2.2): `ModelClock` es correcto; el `31-12-2037` se genera en la conversión a pantalla del widget `PAS_BtnDateTime`, no en el modelo.
- Dirección previamente reportada (F1 §2.3, sin verificación de bytes): cast en `+0x2e2964`, conversor `PAS_BtnDateTimeConverter` en `+0x3a9506` (string), ID de clase en `+0x3b26b7`, string en `+0x3cf884`.

---

## 2. Dirección exacta de la función de conversión (VERIFICADO sobre bytes)

### 2.1 `PAS_BtnDateTime::cast` — RTTI, NO es la conversión

Símbolo exportado en `.dynsym` (índice 1390): `_ZN15PAS_BtnDateTime4castEPN2ux6wgtsys6WidgetE` en **`viewUnified2+0x2e2965`** (Thumb; base `0x2e2964`), tamaño 44 bytes.

Instrucciones relevantes (desensamblado real, `llvm-objdump`, direcciones = offsets de archivo):

```
2e2964: push   {r4, r5, r7, lr}
2e2966: mov    r5, r0                 ; r5 = widget*
2e2968: ldr    r4, [pc, #0x1c]        ; literal -> 0x2e2988
2e296a: add    r7, sp, #0
2e296c: add    r4, pc                 ; r4 = pc + literal (tipo de clase)
2e296e: cbz    r0, 0x2e2986           ; si widget==0, retornar null
2e2970: ldr    r3, [r0]               ; r3 = vtable del widget
2e2972: ldr.w  r3, [r3, #0x190]       ; r3 = vtable[0x190] (método virtual de tipo)
2e2976: blx    r3                     ; llamar al método
2e2978: ldr    r3, [pc, #0x10]        ; literal -> 0x2e298c
2e297a: ldr    r3, [r4, r3]           ; r3 = *(r4 + literal)
2e297c: cmp    r3, r0                 ; comparar resultado con el id esperado
2e297e: ite    eq
2e2980: moveq  r0, r5                 ; si igual -> devolver widget* (cast OK)
2e2982: movne  r0, #0                 ; si no -> devolver null
2e2984: pop    {r4, r5, r7, pc}
```

Etiqueta: **VERIFICADO** (símbolo exportado + bytes reales).  
Valor: es un chequeo de tipo (RTTI/`dynamic_cast` equivalente), **no** convierte fecha a pantalla. Se descarta como origen del `2037`.

### 2.2 Conversor real de fecha: `~viewUnified2+0x2e2e10` (VERIFICADO)

Esta función (método virtual, referenciada desde la vtable en `0x47f5a0 = 0x2e2e11`) recibe `(this, r1, r2)` donde `r1`/`r2` van empaquetados los campos `0x101…0x106` (año, mes, día, hora, min, seg) y los convierte a etiquetas numéricas de pantalla. Desensamblado real (extracto clave):

```
2e2e10: push.w  {r4, r5, r6, r7, r8, r9, lr}
2e2e14: sub     sp, #0xc
2e2e16: add     r7, sp, #0
2e2e18: add.w   r3, r7, #0x8          ; r3 = sp+8
2e2e1c: mov     r4, r0                ; r4 = this
2e2e1e: stmdb   r3, {r1, r2}          ; [sp+8]=r1 (empacado), [sp+12]=r2 (empacado)
2e2e22: ldrb.w  r3, [r0, #0x1ac]      ; r3 = this->byte[0x1ac] (flag fecha)
2e2e26: cmp     r3, #0
2e2e28: beq     0x2e2ed6              ; si flag==0 -> SALTAR (no actualiza display)
2e2e2a: ldrh.w  r9, [r7]              ; r9 = year = low16(r1)  [u16, sin signo]
2e2e2e: movw    r3, #0x833            ; r3 = 2099
2e2e34: cmp     r9, r3                ; comparar año vs 2099 (unsigned)
2e2e3e: bhi     0x2e2ed6              ; si año > 2099 -> SALTAR (año inválido)
2e2e32: ldrb    r1, [r7, #2]          ; r1 = mes  (byte 2 de r1)
2e2e36: ldrb.w  r8, [r7, #3]          ; r8 = día  (byte 3 de r1)
2e2e3a: ldrb    r5, [r7, #4]          ; r5 = hora (byte 0 de r2)
2e2e3c: ldrb    r6, [r7, #5]          ; r6 = seg  (byte 1 de r2)
2e2e40: cmp.w   r8, #0x1f             ; día vs 31
2e2e44: bhi     0x2e2ed6              ; si día > 31 -> SALTAR
2e2e46: cmp     r6, #0x3c             ; seg vs 60
2e2e48: bhi     0x2e2ed6              ; si seg > 60 -> SALTAR
...
2e2e9a: add.w   r0, r4, #0x3700       ; label de año
2e2e9e: ldr     r1, [pc, #0x40]
2e2ea0: adds    r0, #0x78
2e2ea2: blx     GEN_Label::setTextEj   ; setText(year=r9)
2e2ea6: ldr     r3, [r4]
2e2ea8: mov     r0, r4
2e2eaa: mov     r1, r9
2e2eac: ldr.w   r3, [r3, #0x1bc]      ; vtable[0x1bc] -> setLabel(year)
2e2eb0: blx     r3
2e2ebe: ldr     r3, [r4]
2e2ec0: mov     r0, r4
2e2ec2: mov     r1, r8
2e2ec4: ldr.w   r3, [r3, #0x1c8]      ; vtable[0x1c8] -> setLabel(día)
2e2ebc: blx     r3
2e2ec8: ldr     r3, [r4]
2e2ed0: mov     r0, r4
2e2ed2: mov     r1, r5
2e2ed4: ldr.w   r3, [r3, #0x1cc]      ; vtable[0x1cc] -> setLabel(hora/min)
2e2ed4: blx     r3
```

Etiqueta: **VERIFICADO** (desensamblado de bytes reales).  
Conclusión clave: **este conversor funciona correctamente para entrada válida**. Año 2014 pasa `cmp r9,#2099; bhi skip` (2014 ≤ 2099) y se mostraría como `2014`. Día 1 ≤ 31, seg 0 ≤ 60 pasan. Por tanto, si la pantalla muestra `31-12-2037 0:00`, es porque al conversor le llegan **valores empaquetados erróneos**: año=`0x07F5`=2037, mes=`0x0C`=12, día=`0x1F`=31, hora/min/seg=0 (todos los campos de fecha en su máximo y la hora en cero — firma clásica de un **desbordamiento underflow sin signo** en el empaquetado/ajuste de zona horaria upstream).

### 2.3 `Check_PAS_BtnDateTime` — otro RTTI, no conversión

`viewUnified2+0x2e3858` (`_Z21Check_PAS_BtnDateTimePN2ux6wgtsys6WidgetE`). Chequeo de tipo, no conversión. NO_VERIFICADO como origen del 2037 (no toca campos de fecha).

---

## 3. Qué cálculo produce `31-12-2037 0:00` y por qué

### Hechos (VERIFICADO)
- `ModelClock` da `2014-01-01 0:00` (fecha inicial) y hora actual correcta (§5.18z¹¹).
- El conversor `0x2e2e10` lee `year = low16(r1)` como **u16 sin signo**, valida `año ≤ 2099` (`0x833`), `día ≤ 31`, `seg ≤ 60`, y pone etiquetas. Año 2014 pasa y mostraría `2014`.
- Por tanto `31-12-2037` no puede salir de `2014` dentro de este conversor: el valor `2037` (`0x07F5`) llega ya empaquetado en `r1` (low16), con mes `0x0C`=12 y día `0x1F`=31.

### Inferencia del cálculo (INFERENCIA, no verificado contra bytes del caller)
El patrón `año=máximo, mes=12, día=31, hora=0:00` es la firma de un **desbordamiento underflow sin signo** al ajustar la fecha por el área horaria:
- El área horaria está en NVRAM `0x1070140` = `−300` min (registrada en `bk.tbl`, `0x90000a` → `h[15]` en `osal_get_init_date`).
- Si el código de empaquetado (caller del conversor, no localizado) resta el área horaria con **conversión signed/unsigned incorrecta** (p..g. interpreta `−300` como `+300` u32, o resta sobre un valor ya cerca de cero), el resultado bajo cero se interpreta como **u32/u16 grande**, y al descomponer en campos de fecha cae por debajo del mínimo representable y **da la vuelta al máximo** (`2037-12-31 0:00`).

Etiqueta: **INFERENCIA**. La hipótesis del área −300 min fue **descartada para el conversor mismo** (§5.18z¹¹: con `0x90000a`=0 en el perfil sigue dando `31-12-2037`), pero no se descartó para el **empaquetado upstream** (no localizado). No se verificó el caso `23:59` (cuando la fecha inicial era la del host).

### Límite de fecha (máximo 2037)
El conversor impone `año ≤ 2099` (`0x833`), no 2037. No hay constante `0x7f5` (2037) en el widget (búsqueda estática en `.text`: negativa). El `2037` es un valor calculado, no un límite hardcodeado. Etiqueta del límite: **INFERENCIA**.

---

## 4. Corrección propuesta

### Opción (a) PATCHFN en `sonyshim.c` — NO viable hoy
Requiere identificar la instrucción exacta problemática de `viewUnified2.so` (el caller que empaqueta año=2037, o una instrucción de signo dentro del conversor). No se localizó estáticamente (el caller es una llamada indirecta por vtable; no hay `bl` directo a `0x2e2e10`).  
**Etiqueta: NO_VERIFICADO.** Requiere REA (xrefs a `0x2e2e10` / decompilación del caller) para parchear con precisión.

### Opción (b) Proveer desde el shim una fecha que el conversor convierta correctamente — VIABLE PARA PROBAR
El conversor `0x2e2e10` es correcto para entrada válida (año ≤ 2099, día ≤ 31, seg ≤ 60). Si se asegura que llegue al widget una fecha ya empaquetada correctamente (ej. `2014-01-01 0:00`, año `0x07DE` ≤ 2099), el conversor mostraría `2014-01-01 0:00`.  
Mecanismo posible: el shim ya sirve `osal_get_date` (`0x90013d` ord 2) y `osal_get_init_date` (`0x900141` ord 3) con datos correctos; el desbordamiento ocurre al empaquetar hacia el widget. Probar `DATETYPE=3` y verificar que la página Fecha/Hora reciba y muestre `2014-01-01`.  
**Etiqueta: INFERENCIA (pendiente de prueba en arnés).**

### Opción (c) Forzar `DATETYPE=3` por defecto — VIABLE, pero síntomas distintos
Hoy el defecto es `DATETYPE=1`; con `3` la página «Ajuste fecha/hora» no queda desactivada («Función desactivada actualmente»). Esto afecta al **estado habilitado** del elemento, no al valor `2037`. Ver §5.18z⁵: con tipo 3 la página siguió en ceros (no concluyente, no se comprobó reapertura).  
**Etiqueta: INFERENCIA; no corrige el `2037` por sí sola.**

### Corrección recomendada (esta sesión)
No se implementó parche de instrucción (falta la dirección exacta del caller, REA bloqueado). Se documenta el punto de intervención exacto: **`viewUnified2+0x2e2e10` (conversor) y su caller (empaquetado de `r1`/`r2` con año/mes/día)**. Cuando REA esté disponible, aplicar:
- `xrefs` a `0x2e2e10` para hallar el caller,
- verificar qué instrucción produce `year=0x07F5`,
- `PATCHFN="viewUnified2.so:<off>=<valor>"` o corrección del empaquetado en el shim.

---

## 5. Estado de REA (bloqueado)

Se intentó abrir UNA sesión REA sobre `viewUnified2.so` con `session_daemon.py` + `q.py`:
- `open_binary` devolvió correctamente (`format=elf, kind=executable, architecture=arm`, 0.04–0.06 s).
- `inspect_native_load_image` (autoanálisis Ghidra) **no completó**: el daemon muere/bloquea sin crear `viewunified2.sock.ready` ni levantar `java` (nodo rea inactivo a 1.6 MB, sin crecer).
- En el entorno sí hay Ghidra funcionando para otros binarios (`libobj.bin` PID 92611, `av-cam.bin` PID 96526/96528), lo que sugiere límite de instancia/recurso para `viewUnified2.so`.
- Las consultas de función (`address_name`, `procedure_info`, `xrefs` sobre `0x2e2964`) de una sesión previa devolvieron `target_unavailable` / "No app is open".

Etiqueta: **REA no aplicable en esta sesión** (una consulta vacía no prueba ausencia; se agotaron varios intentos genuinos). Se verificó contra bytes reales con `llvm-objdump` en su lugar.

---

## 6. Resultado de la prueba en el arnés

No se realizó: no se identificó la instrucción exacta a parchear ni se implementó corrección de sonyshim.c, por lo que no hay cambio que probar con `live.py`. La página Fecha/Hora sigue mostrando `31-12-2037 0:00` (capturas ya existentes: `img/g22-fecha-hora-nvram.png`, `img/g22-fecha-hora-fecha-actual.png`, `img/g22-fecha-hora-area0.png`).

---

## 7. Conclusión y siguiente paso

- **Función de conversión localizada:** `viewUnified2+0x2e2e10` (VERIFICADO sobre bytes); `cast` en `0x2e2964` es solo RTTI (descartado).
- **Causa del 2037:** INFERENCIA — el caller empaqueta `año=0x07F5`=2037, `mes=0x0C`=12, `día=0x1F`=31, `hora=0:00`; firma de underflow sin signo en el ajuste de área horaria (−300 min, NVRAM `0x1070140`) upstream del conversor.
- **Bloqueo:** REA/Ghidra no disponible para `viewUnified2.so` en esta sesión; no se rastreó el caller ni la instrucción exacta.
- **Siguiente tarea:** reintentar REA sobre `viewUnified2.so` (una vez liberada Ghidra), hacer `xrefs` a `0x2e2e10`, identificar la instrucción que genera `year=0x07F5` y aplicar `PATCHFN` en `sonyshim.c` o corregir el empaquetado desde el shim, luego validar con `live.py` (página Fecha/Hora → `2014-01-01 0:00` o fecha actual coherente).

---

**Etiquetas usadas:** VERIFICADO = confirmado sobre bytes reales / símbolo; INFERENCIA = deducción lógica sin verificación contra bytes del caller; NO_VERIFICADO = no comprobado.
