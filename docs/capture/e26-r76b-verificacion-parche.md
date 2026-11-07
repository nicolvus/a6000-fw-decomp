# Verificación estática del parche Darwin R76 (07-11-2026, sin cámara, sin tocar archivos versionados)

Entrada: `darwin_core.bin` fw321 (157 276 B, base `0x4200`, fin `0x2a85c`). Salida: `e26_r76_parche_darwin_tabla_v2.py` (autotest pasa: `python e26_r76_parche_darwin_tabla_v2.py selftest`). Etiquetas: VERIFICADO (bytes/emulación), CORREGIDO (v1 estaba mal), CÁMARA (solo se decide en cámara).

## Resumen

| Punto | Estado |
|---|---|
| 1. Nadie lee `G+0x44..0x7f` | **CORREGIDO**: Darwin sí lee `G+0x44..0x47` (rama dormante). Tabla movida a `G+0x48..0x7f` (VERIFICADO libre) |
| 2a. Anexar tras `0x2a85c` | **No necesario / no verificable**: el scatter-load no se desplaza, pero el límite de tamaño del cargador no consta (CÁMARA). Descartado |
| 2b. Cave en la imagen | **VERIFICADO**: función muerta `0x13d5a..0x13dc0` (102 B, cave de 54 B). Tamaño de imagen intacto |
| 3. Ramas por velocidad | **VERIFICADO** para la escala 1/3, 1/2 y 1 EV; **CORREGIDO** un tramo continuo (T 1995–2193 µs) que caía en la rama intermedia |
| Extra: compuerta del cave | **CORREGIDO**: debe ser `(S+0x31 & 3) != 0`, no solo bit 1 |

## 1. Lectores de G (`0x20000480`)

Método: (a) barrido Capstone de toda la imagen con seguimiento lineal de registros (literales `ldr pc`, `movw/movt`, `add`, `ldr/str` con offset inmediato e indexado, `ldm/stm`, argumentos a `bl`), ventana de interés `0x20000300..0x20000600`; (b) revisión manual de cada sitio; (c) las tablas de bloques.

* La palabra `0x20000480` solo está como literal cargado en **5 sitios**: `0x182da` (fn `0x182d8`), `0x18398`, `0x18a30` (fn `0x18a2e`), `0x18daa` (fn `0x18d6e`), `0x18fbc`. Ninguna otra instrucción de la imagen la carga (las otras apariciones de la palabra, `0x164ea` y `0x2a180`, son datos: la primera está desalineada, la segunda es el descriptor de bloque).
* Lecturas reales (VERIFICADO leyendo las ramas):
  * `G+0x40/0x41` (s16): `0x18a2e` con `S+0x31&3 == 0`; `0x18398` copia `G+0x40..0x43` a `[r0+0x54]`/`[r0+0x56]` (respuesta al BIONZ).
  * `G+0x42/0x43` (u16): `0x182d8` (si `B+0xcd&3 == 0`), `0x18a2e`, `0x18d6e` (`0x18db0`), `0x18fbc`, `0x18398`.
  * **`G+0x44..0x47`**: `0x182d8` (`0x18300`, u16 `+0x44`), `0x18d6e` (`0x18de0`: `+0x44` y `+0x46`, u16+u16), `0x18fbc` (`0x18ff4`: `+0x44..+0x47`). Se ejecutan cuando `B+0xcd & 3 ∈ {2,3}` (con `==1` usan `B+0x12a..0x12d`). Hoy `B+0xcd = 0` (R66/R70) ⇒ rama dormante, pero **no es "no leído"**: v1 ponía la tabla justo ahí y, si `B+0xcd&3 ≥ 2`, los pares {Tmax, c} se interpretarían como retardos.
  * Nada lee ni escribe `G+0x48..0x7f`. El barrido no halla ningún `str`/`stm` sobre G (solo escribe el BIONZ).
* Accesos en bloque: no hay memcpy/checksum de Darwin sobre G. Lo único que toca G entero es el mecanismo de ventana de memoria BIONZ↔Darwin:
  * tabla de descriptores `0x2a160` (apuntada por `0x2a194`): `{0x20280,0x180,0x20000300}` (B), `{0x30100,0x100,0x20000600}`, `{0x10100,0x80,0x20000480}` (G); `0x24204/0x242b0` la usan en `0x241f4` (traducción de dirección) y `0x2429e` (validación), y `0x1b53e` (llamador único `0x12362`, handler de lectura/escritura de hasta `0x78` B por comando, copia por `0x255a6`). **Solo comprueban rango, nunca leen contenido; no hay suma ni CRC de G** en Darwin.
  * `0x2a124` es la tabla análoga de los bloques `S` (`0x200036d8`...).
  * Argumentos a `bl` con punteros a B/G: los pocos hallados (`0x25738` = lectura u32 LE de `0x20000470`, `0x20000420`, `0x20000394`) leen 4 B; el resto eran falsos positivos de r1 obsoleto.
* Límite: lo que el **BIONZ** haga con la propiedad `0x1850000` (CRC de propiedad NVRAM, validación del bloque) no está en `darwin_core`; NO VERIFICADO aquí (CÁMARA / estudio de `av-cam.bin`).
* Acción: v2 usa `TAB_OFF = 0x48` (`0x200004c8`), 56 B = 13 entradas + terminador. La tabla actual tiene 11 entradas.

## 2. Hueco para el cave

### (a) Anexar tras `0x2a85c`

* Scatter-load: tabla en `0x2a744` (referenciada por la palabra relativa de `0x4430`), dos entradas de 16 B: `{0x2a764 → 0x20002a00, 0x4d0, descompresor 0x4438}` y `{0x2a85c → 0x20002ed0, 0xf8c, 0x4494}`. `0x4494` es puesta a cero (no lee origen); el `0x2a85c` es el origen sin uso (= fin de imagen). Los datos comprimidos son `0x2a764..0x2a85c`. Anexar no desplaza nada de lo anterior; el puntero de la 2ª entrada seguiría válido (ignorado).
* Lo que NO consta: el límite de tamaño. `darwin_core` se carga con el arranque FM3 (`0x0..0x41ff`, sin binario; E24-02 §3: "si el arranque verifica la imagen" NO_VERIFICADO). `ud_darwin_firmup.elf` envía el tamaño (`0x14 [5..8]`) y atiende lo que el arranque pida; en el ELF no hay comparación con un máximo. `darwin.sum` solo lleva CRC-32+tamaño (`0002665c` = 157 276). Todos los paquetes propios previos (R53–R57, 3.29–3.38, `scripts/e25_27/build.py`, `PD.SIZE`, `darwin_fdat_build.py`) mantienen el tamaño exacto (parche en sitio, `assert len(...) == m.size`). **Nunca se ha probado un `darwin_core` más largo.** Capacidad de flash del MB9AF004B: no está en el repo.
* Decisión: **no anexar** (riesgo sin necesidad, solo se decidiría en cámara).

### (b) Dentro de la imagen

* Precedente: R53–R57 usan una cueva de 14–16 B en `0x4318` (vector 70 libre). Zona de ceros contigua en `0x4316` = 18 B: no basta para 54 B.
* Rutas de relleno (`0x00` en tablas) descartadas: están dentro de tablas de datos.
* Funciones sin referencias (barrido de 1334 funciones, `push {…,lr}`): una función cuenta como muerta solo si **ninguna** instrucción de fuera de su rango la referencia (ramas `b/bl/b.w/cond/cbz`, `adr`, `ldr pc-rel` a su interior) y ninguna **palabra** de 32 bits de la imagen (cualquier alineación a 2 B, con o sin bit 0) apunta a ella (cubre vectores, tablas de estados `0x25b50`, tablas de acciones de los descriptores `0x28dd4/0x28fdc/0x296f0/0x2a094` —cuyos primeros campos `0x28df0`, `0x28ff8`, `0x2970c`, `0x2a0cc` son la tabla de acciones con punteros Thumb— y los `{tabla,n,&idx,&acción,&ptr}`). Quedan 12; las ≥ 60 B:

| Rango | B | Nota |
|---|---|---|
| `0x13d5a..0x13dc0` | 102 | **elegida**; termina en `pop {r4,pc}`; precede un `pop` |
| `0x14fd4..0x1502a` | 86 | alternativa 1 |
| `0xaba2..0xabf6` | 84 | alternativa 2 (acaba en `b.w`) |
| `0x1d2c8..0x1d31c` | 84 | su predecesor es dato; descartada |
| `0x11d6c..0x11db0` | 68 | alternativa 3 |
| `0x13808..0x13848` | 64 | alternativa 4 |

  Descartada `0x251a8` (210 B): parecía muerta pero es el cuerpo de `__aeabi_uldivmod` al que se llega por *fall-through* desde `0x251a0` (`beq 0x2527a` no tomado). Por eso el criterio exige además que el predecesor termine en `bx/pop pc/b`.
* **Elegida `0x13d5a`**: el cave de v2 mide 54 B (`ensamblar_cave(0x13d5a)`; con el literal alineado a 4 B), cabe en 102 B y el literal `ldr` cae en `0x13d88` (alineado). `bl 0x18d7c → 0x13d5a` alcanza (distancia 0x5022). El autotest (VERIFICADO): `sha256(0x13d5a..0x13dc0)` coincide con el original, no hay ninguna referencia externa (ramas, palabras, `pc-rel`) hacia el rango, y los **únicos** bytes distintos de la imagen son los 4 del gancho y los 54 del cave (tamaño 157 276 intacto).
* Límite: "muerta" es estático. Una función invocada por una dirección fabricada en tiempo de ejecución (aritmética de punteros, sin palabra literal) no se detectaría; la imagen solo usa `movt #0x2000` en `0x454a/0x456a/0x458c` (dirección de datos). Para cerrar el último resquicio: marcar con REA (xrefs) las cinco candidatas en una sesión (no hecho aquí por coste de 8 min en frío).

## 3. Ramas de `0x18d6e` con la tabla

Emulación Unicorn de la imagen parcheada (`emular_18d6e`, `0x19a12` real para Tv→T, `0x1b308/0x1a738/0x19932/0x203ae/0x19948/0x198bc/0x93e6/0x19978` sustituidos; EFCS `S+0x31 = 0x02`, G42 = 3407, B+0x84.. = 6/6/−22/−21 de R66). La rama intermedia es el `bl 0x19978` de `0x18e9e` (−150 ≤ `S+0x48` ≤ 50), que llega a `0x20544`.

Tabla v2 (Tmax µs, c µs): `(347,1264) (551,1287) (1752,1310) (1953,1263) (2099,1117) (2245,1398) (3504,1252) (4411,1050) (5560,825) (7008,535) (9834,169)` (T > 9834: terminador, c = 0).

Escala 1/3 EV (T → rama parcheada / original; `S+0x48 = T + c − 3407`):

| T µs (≈) | rama | orig | S+0x48 |
|---|---|---|---|
| 244 (1/4000) … 1953 (1/500) | corta | corta | −1899 … −191 |
| 2458 (1/400), 3102 (1/320) | larga | corta | +303, +947 |
| 3906 (1/250) … 31250 (≈1/30) | larga | larga | +1549 … +27843 |

* Medios EV (T 244…31250) y 1 EV: sin intermedia (corta hasta 1953, larga desde 2761/3906).
* **La rama intermedia no se alcanza en ninguna velocidad de las escalas 1/3, 1/2 y 1 EV.** Margen más estrecho: 1/500 (T = 1953): `S+0x48 = −191`, 41 µs bajo el umbral −150.
* Pero el barrido de **todos** los códigos Tv (1/256 EV, T 200..45000 µs, 1866 códigos): con la tabla v1 había 36 códigos en la intermedia, **T = 1995–2193 µs (Tv `0x18d5..0x18f8`)** (c ≈ 1263 hace T′ ∈ [3257,3457]). Sin parche, la intermedia son T 3257–3448 µs (Tv 6190–6211), tampoco en las escalas. Aparecería solo si la AE usa un Tv fuera de escala (no consta; CÁMARA).
* Ajuste v2 (`_guardas`): ese tramo se parte en `(1953,2099] c=1117` y `(2099,2245] c=1398`, de modo que T′ salta la ventana ±40 µs de margen. Coste: error modelado hasta ≈ 9 % (−0,13 EV) solo para 1953 < T ≤ 2245 µs (entre 1/500 y 1/440, **sin velocidades de la escala**); fuera de ese tramo ≤ 4,3 %; en la escala ≤ 1,7 %. Resultado emulado: 998 `larga`, 868 `corta`, 0 `intermedia`.
* Límites: G42 (3407), B+0x84..0x8a y las constantes son los de **esta** unidad (R66); otra unidad o un NVRAM recalibrado mueve la ventana (la tabla y la ventana dependen de G42). `S+0x94 ≠ 0` (override en `0x18d82`) no se modela. El 0x20544 y la curva δ(B−A) siguen siendo MODELO/INFERENCIA de R74.

## 4. Corrección adicional: compuerta del cave

`0x18a2e` entra a la resta de `G+0x42` si `(S+0x31 & 3) != 0` y `S+0x60` bit 1 = 0 (flags de `lsls r3,r1,#30` + `bne`); `0x18d96` hace igual (`ubfx r0,#0,#2 ; cbnz`). El cave de v1 probaba solo el bit 1 (`bpl`), de modo que con `S+0x31 = 1` o `3` el original restaba G42 y el cave no sumaba `c`. v2 usa `beq done` (equivale a `&3 != 0`). Autotest: `S+0x31 ∈ {1,2,3}` da el mismo resultado; EFCS off y `S+0x60` bit 1 quedan idénticos al original; con tabla a ceros el parche es neutro en todas las velocidades.

## 5. Qué solo se decide en cámara

1. Que el BIONZ acepte escribir `G+0x48..0x7f` por la propiedad `0x1850000` sin invalidar CRC/formato (el código es de `av-cam.bin`).
2. Que `B+0xcd&3` sea 0 en todos los modos (la rama `G+0x44` es dormante hoy).
3. Que el cargador FM3 admita `darwin_core` más largo (por eso se evita) y que la función `0x13d5a` esté realmente muerta en ejecución (estático: 0 referencias).
4. Que la AE no use Tv fuera de la escala y que `0x20544` se comporte como supone R74; la curva δ(B−A).
5. Paquete: seguir el flujo de `scripts/e25_27/build.py` (`PD.apply_bytes`/`allowed_addresses` deberían ampliarse con `0x18d7c..0x18d7f` y `0x13d5a..0x13d8f`; `darwin.sum` con CRC-32 y tamaño `0x2665c` nuevos vía `sums.update`; tamaño de imagen y de miembro del tar intactos).
