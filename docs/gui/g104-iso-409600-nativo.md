# G104 — ISO nativo hasta 409600: mapa de la cadena y viabilidad (23-11-2026; EN CURSO, sin parche, sin CFW)

Petición: añadir el ISO aumentado hasta 409600 al CFW Film 3.92. El usuario eligió el camino **nativo**: valores en la lista ISO real y EXIF correcto, no un empuje digital.
Continúa G41–G48 (51200). Fuentes: bytes de `av-cam.bin` (3.21/3.38 iguales en estas zonas) y de `libObj.so`/`viewUnified2.so`/`viewUnified4.so` del 3.21, REA sobre av-cam y el arnés G22.

## 1. Quién construye la lista ISO de la interfaz (resuelve G46)
- La pantalla ISO es `ViewIsoSensitivity` de `viewUnified4.so` (`ViewIsoSensitivityToInstance` `0xee9ff`). Importa `WrapperIso::getIso(cur, min, max)`, `setIso` e `isInhOn`.
- En `im.elf` esas funciones las da la **copia estática de `WrapperIso` dentro de `viewUnified2.so`**: `getIso` `0x1c11e9` (2104 B), `setIso` `0x1c1c45`, `isInhOn` `0x1c1bfb`. `wrapperIso.so` no se carga (G47).
- Por eso G46 no veía cambios al parchear `CautionConfig.so`: la lista sale del rango mínimo–máximo que devuelve `getIso`, no de `cmnViewSettingNodesISOSensitivity*`.
- **Arnés (MEDIDO, perfil `iso1`, fábrica 3.21):** MENU → cámara p. 4 → ISO abre la lista (…10000, 12800, 16000, 20000, 25600). Al elegir 20000, la pantalla de disparo muestra «ISO 20000». No llega ninguna orden nueva a av-cam (`avcam.jsonl`): el ISO manual no viaja como orden suelta en el arnés. Cómo llega a av-cam: **pendiente**.

## 2. Códigos de modelo e ids de valor (`libObj`, VERIFICADO en bytes)
- Tabla de nombres `VALUEID_*` en `0xfdd65c` (id = (dirección − `0xfdd65c`) / 4).
  - `ISO_AUTO` = `0x21`, `ISO_10` = `0x22` … `ISO_10000` = `0x3f`.
  - `ISO_12800` = `0x274`, `ISO_25600` = `0x275`, `ISO_51200` = `0x276`, `ISO_102400` = `0x277`.
  - `ISO_128000`/`160000`/`204800` = `0x3fd`/`0x3fe`/`0x3ff`.
  - **No existen** ids para 256000, 320000 ni 409600: hay que crearlos.
- Conversor av-cam → `libObj` del ISO actual (`0x9aa134`, `tbh` por el byte `+0x14`, ≤ `0x3b`):
  - código `k` = índice de la tabla ISO de av-cam: `0` AUTO, `0xb` 100 … `0x29` 102400, `0x2a`–`0x2c` 128000–204800;
  - `0x2d`–`0x3b` = `VALUEID_DB_*` (ganancia en dB del vídeo).
- Conversor de valor/mín./máx. (`0x4e0ea8`, ≤ `0x4a`): igual hasta `0x29`. Pero `0x2a` no es válido, `0x2b`–`0x38` son dB y `0x3a`–`0x48` los ISO con NR multifotograma.
- App2Obj del ISO (VALUEID → código, `0x4e42b4`; llamado desde `0x4e7d52/0x4e7d98/0x4e7eee/0x4e7f2a`): mapea hasta `ISO_102400` → `0x29`; `0x3fd`–`0x3ff` (128000–204800) y cualquier otro id dan `0x2a` (no válido). Prueba: Unicorn sobre la función real.
- **Choque (y salida):** los índices 256000/320000/409600 (`0x2d`–`0x2f`) ya significan dB en los dos conversores. Hay dos salidas: códigos nuevos libres en ambos conversores (≥ `0x4b`) que av-cam traduzca a esos índices, o reutilizar `0x2d`–`0x2f`. La segunda vale si la A6000 no usa la ganancia en dB, porque `WrapperIso::getIso` solo conoce los códigos `8`–`0x26` (INFERENCIA, por comprobar). Es la más simple: el código sigue siendo el índice de la tabla y es lineal con Sv en av-cam.

## 3. av-cam: ISO → Sv → ganancia (REA + Capstone)
- **Sv y código** (1 paso = 1/3 EV, `0x100` por EV):
  - `0x43b074ba`: código = (`0x3b7e` − 3·Sv) >> 8;
  - `0x43b074d2`: código + desplazamiento global − `0xb`;
  - `0x43b074e4`: **tope de código `0x2c`** (`cmp r0,#0x2c; movhs`).
- **EXIF** (`FUN_437b3cec`, `0x437b403e`): código desde Sv, **tope `0x2c`** y tabla `0x43bc48e0` (10 … 204800, 45 entradas) → ISOSpeedRatings (16 bit, satura en 65535) y RecommendedExposureIndex (32 bit, tipo 2). Para 409600 hacen falta 3 entradas más (la tabla va seguida de otros datos: reubicarla) y el tope `0x2f`.
- **Control de exposición** (`FUN_438d07f8`): Sv de `[prog+0x164]` o `[+0x1664]`. Si Sv < MinCap (`+0x58`) solo registra «EC::CapISO Error», sin recortar.
- **Reparto de ganancia** (`FUN_437b061c`):
  - analógica hasta los límites de la tabla de configuración (`+0x38`/`+0x3a`), el resto en digital;
  - la digital está acotada por `0x4383c7a8` = **`0x1800`** (máximo) y `0x4383c7c4` = `0x801` (mínimo), con unidad `0x1000` = ×1;
  - hay además un tope de configuración en `+0x5a` (valor en tiempo de ejecución, sin leer);
  - registro «a_gain:%04X, d_gain:%04X» en `FUN_43810fa8`.
- Lectura: con `0x100` por EV, el máximo digital `0x1800` deja hasta +8 EV de ganancia digital. 409600 = 25600 + 4 EV, así que entraría si 25600 usa ≤ 4 EV de digital. INFERENCIA, NO_VERIFICADO: depende del máximo analógico de la tabla de configuración y del tope `+0x5a`.

### 3.1 Entrada del ISO manual en av-cam
- `0x43b074e4`: código del ajuste → Sv = (`0x3b` − código)·`0x100`/3; `0xff` = valor por defecto, `0` → 1, **tope `0x2c`**. Lo llaman `0x437b0eee`, `0x4384b37a` y `0x4385f7da`, que leen el código de `[objeto de ajustes + 0x180]`.
- Ese byte lo escribe una copia de estructura en bloque (`FUN_4382e718`, `0x4382ea68`): el ISO manual llega dentro de un bloque de ajustes, no en una orden propia. Qué orden lo trae: **pendiente** (en el arnés, cambiar el ISO no envía ninguna orden a av-cam, ni con semipulsación).
- Con `0x100` por EV y códigos de 1/3 EV, el código `0x2f` (409600) da Sv = `0x400`, dentro del rango de la aritmética; no hay desbordamiento.

## 4. Qué hay que cambiar (plan)
1. **av-cam:**
   - topes de código `0x2c` → `0x2f` (`0x43b074e4`, `0x437b403e` y los demás que aparezcan);
   - tabla ISO reubicada con 256000/320000/409600;
   - traducir los códigos nuevos (≥ `0x4b`) a los índices `0x2d`–`0x2f` en la entrada del ajuste ISO (orden aún por localizar);
   - comprobar el tope digital `0x1800` y el de `+0x5a`.
2. **`libObj`:**
   - 3 `VALUEID` nuevos;
   - los conversores `0x9aa134`, `0x4e0ea8`, `0x4e41c4` y el inverso (App2Obj del ISO) con los códigos nuevos;
   - el máximo (`iso_max_patch`) hasta el código de 409600.
3. **UI (`viewUnified2` `WrapperIso`, `viewUnified4` `ViewIsoSensitivity`):**
   - `getIso`/`setIso`/`convertValueToProcessValueId` con enums `WRAPPER_ISO` nuevos (> `0x4e`; `0x4f` = «sin valor»);
   - textos 128000/160000/256000/320000/409600 en los `.uxc` (64000/80000/102400/204800 ya existen);
   - la pantalla de disparo.
4. **Pruebas teóricas:** Unicorn sobre cada conversor y tope, VM de av-cam con la orden del ISO, y el arnés para la lista.

## 5. Estado
Sin parches todavía. Abierto en PENDIENTES como **ISO-409**.
