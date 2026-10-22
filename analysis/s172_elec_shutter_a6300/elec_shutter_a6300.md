# S172 — el módulo `ElecShutter` del A6300: qué hace realmente (control positivo del obturador electrónico)

> Hito de la **línea de ingeniería inversa general** con valor directo para la **línea del
> obturador electrónico**. Solo lectura de bytes: `av-cam.bin` del **A6300 fw2.01**
> (`firmware/extracted/a6300-fw201/.../av-cam.bin`), con la A6000 fw3.21 y la A7S fw3.20 como
> comparación. Convención: `vaddr = 0x43541000 + file_offset`. Regla de referencias:
> **estricta** (canónica del repo), con el mapa del A6300 en
> `analysis/s169_drive_api/pic_refs_strict_a6300.json`.

## 1. Resumen / veredicto

**S135** localizó el subsistema `ElecShutter/` en el HAL del A6300 por sus **nombres de
fichero** (`ElecShutter/EC_ElecShutter_Main.cpp`, `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp`)
y por sus ajustes (`SilentShutterMode`, `shutterType`, `front_eshutter`), pero **sin decodificar
el comportamiento**. Este hito **localiza el código** (los nombres de fichero son cadenas de
`__FILE__` de un `EC_ASSERT %s:%d`) y **caracteriza las dos funciones**:

1. **`EC_ElecShutter_Main.cpp`** — una función que lee un valor de **16 bits** de una tabla
   global y devuelve un **código de modo de obturador**:
   * `0x80` → devuelve **3**
   * `0x100` → devuelve **4**
   * otro valor → `EC_ASSERT` con línea **0x421** (1057) y devuelve 3.

2. **`EC_NonlinearElecShutter_MechShutterTable.cpp`** — la **tabla no lineal de equivalencia
   entre velocidad electrónica y mecánica**:
   * una función de **interpolación por tramos**: lee una fila de la tabla con
     `ldr.w r3,[r2, r6, lsl #2]` (32 bits por fila), compara con el valor pedido y **interpola**
     con escalas **10000** (`0x2710`) y **1000** (`0x3e8`), usando el helper aritmético
     `0x435586f8` y los setters `0x4391da74` / `0x4391da9c`;
   * una segunda función de **búsqueda no lineal en punto fijo 16.16**: escala `0x8000` y **15
     bits fraccionarios** (`mov.w r3,#0x8000` / `movs r2,#0xf`), recorriendo la tabla con
     `add.w lr, r3, r0, lsl #1` + `lsl.w lr, lr, r2`;
   * `EC_ASSERT` con línea **0x23c** (572) y **0x24f** (591).

**Corrección a S135**: los **128 bytes** que S135 identificó como «tabla de índices de velocidad
de obturación» en `0x43dcfa9e` **no tienen ninguna referencia de código** (ni PIC ni puntero
absoluto de 4 B) → esa identificación **no está verificada**. La tabla real es la que consume
el código **por índice de fila** (32 bits por fila), no ese bloque.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** Sigue faltando la prueba física.

## 2. Las cadenas de `__FILE__` y sus sitios

| cadena | A6000 | A7S | A6300 | sitios PIC en el A6300 |
|---|---|---|---|---|
| `ElecShutter/EC_ElecShutter_Main.cpp` | 0 | 0 | **1** (`0x43dcfa41`) | `0x4391d6a2` |
| `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` | 0 | 0 | **1** (`0x43dcfa65`) | `0x4391dd50`, `0x4391ddb0` |
| `EC_ASSERT %s:%d` | **0** | 1 | **1** (`0x43db1a4d`) | (los tres sitios anteriores) |

El **formato** `EC_ASSERT %s:%d` **no existe en la A6000 fw3.21** (0) y sí en la A7S fw3.20 y el A6300 fw2.01 (1/1): lo que el A6300 aporta en este módulo es además los **nombres de fichero** `ElecShutter/...` que se le pasan (0/0/1 y 0/0/1). Los tres sitios usan el mismo patrón `ldr r0,[pc,#..]` + `ldr r1,[pc,#..]` + `add r0,pc` +
`add r1,pc` + `bl 0x43986518` (el logger de `EC`), con `r0` = formato `EC_ASSERT %s:%d`,
`r1` = fichero y `r2` = **número de línea**.

## 3. `EC_ElecShutter_Main.cpp`: el código de modo de obturador

```
0x4391d67c: push   {r3, lr}
0x4391d67e: ldr    r3, [pc, #0x38]     ; puntero a una tabla global
0x4391d680: ldr    r2, [pc, #0x38]     ; indice
0x4391d682: add    r3, pc
0x4391d684: ldr    r3, [r3, r2]        ; entrada de la tabla
0x4391d686: ldrh   r3, [r3]           ; u16 de configuracion
0x4391d688: cmp    r3, #0x80
0x4391d68a: beq    #0x4391d6ac         ; -> devuelve 3
0x4391d68c: cmp.w  r3, #0x100
0x4391d690: beq    #0x4391d6b0         ; -> devuelve 4
0x4391d692: bl     #0x438fae00         ; comprobacion previa
0x4391d696: cbnz   r0, #0x4391d6b4     ; -> devuelve 3
0x4391d698: ldr    r0, [pc, #0x24]     ; "EC_ASSERT %s:%d"
0x4391d69a: movw   r2, #0x421          ; linea 1057
0x4391d69e: ldr    r1, [pc, #0x24]     ; "ElecShutter/EC_ElecShutter_Main.cpp"
0x4391d6a0: add    r0, pc
0x4391d6a2: add    r1, pc
0x4391d6a4: bl     #0x43986518
0x4391d6a8: bl     #0x438fade0
0x4391d6ac: movs   r0, #3              ; codigo 3
0x4391d6b0: movs   r0, #4              ; codigo 4
```

**NO VERIFICADO**: qué significan exactamente los códigos 3 y 4, ni qué tabla global se lee
(`ldr r3,[pc,#0x38]` → puntero + índice), ni qué es `0x438fae00` (comprobación previa) ni
`0x438fade0` (manejador de aserción).

## 4. `EC_NonlinearElecShutter_MechShutterTable.cpp`: la equivalencia no lineal

### 4.1 Interpolación por tramos (sitio `0x4391dd50`)

```
0x4391dbe0: ldrb.w r3, [sb, #0x170]    ; bandera de modo
0x4391dbe4: cmp    r3, #1
0x4391dbe6: bne    #0x4391dcb8
0x4391dbf0: ldrh.w fp, [sb, #0x172]    ; limite 1
0x4391dbf8: ldrh.w r8, [sb, #0x174]    ; limite 2
0x4391dbfc: ldrb.w r6, [sb, #0x171]    ; indice de fila
0x4391dc28: ldr.w  r3, [r2, r6, lsl #2]; VALOR DE LA TABLA (32 bits por fila)
0x4391dc2c: cmp    r3, r7              ; comparar con el pedido
0x4391dc2e: rsb    r3, r7, r3
0x4391dc36: mla    r0, r0, r3, r1      ; r0 = 0x2710 (10000) * delta + base
   (o, si el delta es negativo)
0x4391dc3e: muls   r0, r3, r0          ;   r0 = delta * 0x2710 - base
0x4391dc44: bl     #0x435586f8         ; helper aritmetico
0x4391dc4c: bl     #0x4391da74         ; setter
0x4391dc72: mov.w  r2, #0x3e8          ; escala 1000
0x4391dc80: smlabb r0, r0, r2, r1      ; r0 * 1000 + r1
0x4391dc88: bl     #0x435586f8
```

### 4.2 Búsqueda no lineal en punto fijo 16.16 (sitio `0x4391ddb0` y el lazo en `0x4391dd5e`)

```
0x4391dd34: movs   r2, #0xf            ; 15 bits fraccionarios
0x4391dd36: mov.w  r3, #0x8000         ; escala 32768
0x4391dd3a: movs   r0, #0
lazo:
0x4391dd5e: lsrs   r3, r3, #1
0x4391dd60: add.w  lr, r3, r0, lsl #1
0x4391dd64: lsl.w  lr, lr, r2         ; valor = (r3 + r0*2) << r2
0x4391dd68: cmp    r1, lr
0x4391dd6a: blo    #0x4391dd74
0x4391dd6c: adds   r0, r0, r3
0x4391dd6e: rsb    r1, lr, r1
0x4391dd72: uxth   r0, r0
0x4391dd74: subs   r2, #1
0x4391dd76: bhs    #0x4391dd5e
```

Es una **búsqueda por tramos con escala 2^15** sobre la tabla: recorre los puntos de la tabla
bisecando el intervalo.

### 4.3 Errores

| línea | fichero | significado |
|---|---|---|
| **0x421** (1057) | `ElecShutter/EC_ElecShutter_Main.cpp` | valor de configuración no esperado |
| **0x23c** (572) | `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` | punto de tabla fuera de rango (interpolación) |
| **0x24f** (591) | `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` | número de puntos inválido (`ZitDdcDriver: Invalid numPt. [%d][%d]`) |

### 4.4 Colateral: la A6000 no tiene ni `EC_ASSERT` ni `EC_ERR_PRINT`

`EC_ASSERT` (formato `%s:%d`) y `EC_ERR_PRINT %s:%d  Pga Drv Manager Sub Flow Error.`
están en el A6300 fw2.01 (**1** y **5** respectivamente) y en la A7S fw3.20 (`EC_ASSERT` **1**,
`EC_ERR_PRINT` **0**), pero **no existen en la A6000 fw3.21** (**0** y **0**). El motor EC de la
A6000 **no instrumenta sus aserciones** con ese formato: otra diferencia de *logging*, coherente
con el patrón general de S128/S130.

## 5. Corrección a S135 — el bloque de 128 bytes de `0x43dcfa9e`

S135 escribió: «la tabla de **índices de velocidad de obturación**: justo detrás de
`EC_NonlinearElecShutter_MechShutterTable.cpp` (`0x43dcfa9e`: `00 01 03 04 05 06 08 09 0a 0b 0d 0e
0f 10 12 13 14 16 17 18 19 1b 1c 1d 1e 1f 21 22`, es decir, los códigos de velocidad **no
lineales** con su equivalente mecánico)».

**Verificación**: ese bloque de 128 bytes

* **no tiene ninguna referencia PIC** (no está en `pic_refs_strict_a6300.json`), y
* **no tiene ningún puntero absoluto de 4 B** en el binario,

y además es una **tabla byte→byte no decreciente** (los valores se repiten: `54 54`, `60 60`,
`66 66`, `6a 6a`, `6e 6e`, `71 71`, `74 74`, `77 77`, `7b 7b`, `7d 7d`, `7f 7f`), más compatible con
una tabla de **caracteres imprimibles** que con una tabla de velocidades.

→ La identificación de S135 **no está verificada** y queda **corregida**: la tabla de
velocidades que consume el código es la que se indexa **por fila con 32 bits por entrada**
(§4.1), no el bloque de `0x43dcfa9e`. **Lo que S135 acertó** (la existencia del módulo
`ElecShutter/`, sus ficheros y sus ajustes) **se mantiene**.

## 6. Salvedad metodológica (heredada de S130 §4)

El A6300 es de otra **generación de plataforma** (LIRO/CXD) que la A6000 y la A7S: con los tres
blobs disponibles **no** se puede separar «nuevo en el fw2.01» de «propio de la plataforma».

## 7. Qué NO se afirma

- **NO** se afirma que la A6000 sea incapaz de disparar con obturador electrónico: se afirma que
  su fw3.21 **no tiene** este módulo, ni estos parámetros, ni esta tabla.
- **NO** se han decodificado los valores concretos de la tabla (la base de datos está en runtime,
  indexada por fila).
- **NO** se han identificado los códigos de modo 3 y 4.
- **NO** se ha seguido la ruta hasta el driver del obturador.
- **NO** se ha characterized el sentido de la escala 10000/1000/32768 más allá de su valor
  aritmético.

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s172_elec_shutter_a6300.py -q
```

## 9. Revisión del agente principal

_(vacía)_
