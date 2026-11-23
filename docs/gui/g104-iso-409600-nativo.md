# G104 — ISO nativo hasta 409600: mapa de la cadena, parche de av-cam hecho y UI/libObj pendientes (23-11-2026; EN CURSO, sin CFW)

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

## 5. Parche de av-cam (HECHO, 23-11-2026)
- `scripts/gui/iso_avcam_patch.py` (integrado al final de `bionz` y `bionz_pp` de `build_cfw_film`): topes `0x2c` → `0x2f` en `0x43b074f2/f6` y `0x437b403e`; tabla de EXIF de 48 entradas (… 204800, **256000, 320000, 409600**) en `ZONA_B[0]` (`0x43C1FF24`, 3432 B libres en el av-cam Film+PP) y literal `0x437b4124` repuntado. Único acceso a la tabla (barrido de literales PC-relativos: los otros dos accesos cercanos apuntan a tablas distintas).
- `tests/test_g104_iso_avcam.py` (4 verdes, Unicorn sobre el av-cam real): los 48 códigos → ISO de EXIF; código `0x2f` → Sv `0x400`, `0x2c` → `0x500`, sin cambios de `0` a `0x2c`; Sv `0x400` → `0x2f`; idempotente; cadena real de las dos funciones del CFW (3.38 base). g102/g103 siguen en verde.
- Seguro por sí solo: ningún código ≥ `0x2d` llega a av-cam mientras la UI y `libObj` no los emitan.

## 6. Hallazgos nuevos (mismo día)
### 6.1 Ganancia: ¿hay otro amplificador? (pregunta del usuario: doble ISO base)
- Cadena en av-cam: **un solo PGA analógico** + ganancia digital. Analógico: `FUN_436d7e08` (módulo `CAM_IMAGER`, sensor `IMX21019C_ImagerCtrl_IMX210E`) convierte la ganancia pedida con una tabla exp de 256 entradas (`0x43bdbe9a`, `FUN_436d8a90`) a un código de registro (`AGainCont`, `AGainCont_EC`, `AGainDrv` por modo de captura, 13 modos); lo que no cabe lo toma la digital de `FUN_437b061c` (rango `0x801…0x1800` = ±8 EV, G104 §3).
- **No hay ninguna cadena ni ruta de conversión dual** (sin `DCG/HCG/LCG/ConvGain/GainSw` en av-cam; los `Dual*` son DualRec y `itp_*dcgain` es el DC del demosaico, no un amplificador). `PGACont/PGAContLinear` son tablas de OB. Conclusión: con este firmware no hay un segundo amplificador conmutable que dé un segundo ISO base; solo se podría emular cambiando el reparto analógico/digital (p. ej. `+0x5a`), sin ganancia de ruido real. NO_VERIFICADO: los registros que escribe el controlador del sensor (`ImagerCtrl`, vtable) no se han leído; ahí estaría una conmutación de ganancia de conversión si existiera.
- El máximo analógico real (`[cfg+0x3a]`, `+0x5a`) es de ejecución (cero en el fichero): sigue sin leer; la cabida de 409600 (12 EV = analógico + 8 EV digitales) es INFERENCIA.
- `FUN_4381a3f4` (ISO numérico → código, usado por `SetGainBI`, mensaje `0x4032`) también topa: comprobar su cola antes de dar el av-cam por completo.

### 6.2 `libObj`: dominios de código (VERIFICADO en bytes)
- Directos (código → id), todos por tabla, parcheables en sitio: `0x9aa134` (actual, ya mapea `0x2a…0x2c` a `0x3fd…0x3ff` y `0x2d…` a ids DB `0x1e5…`), `0x4e0ea8` (valor/mín/máx: `0x2a` inválido, `0x2b…0x38` = DB, ids `0x1e5…0x1f2`), `0x4e41c4` (rango estándar, `tbb` ≤ `0x2a`, y **`0x2a` = AUTO `0x21`**).
- Inversos (id → código): `0x4e42b4` y `0x4e10b8` son árboles de `cmp` sobre ids `0x21…0x49` y `0x274…0x277`; todo lo demás devuelve el **centinela `0x2a`**. Añadir 128000…409600 exige cuevas (segmento R+X añadido, como `lut_sd_vu2`).
- Los códigos `0x2a/0x2d…` significan cosas distintas según la función, así que reutilizar el índice de av-cam como código único no vale: hay que fijar códigos libres (≥ `0x4b`) con traducción en av-cam, o recolocar los centinelas. Sitios del MAX: `0x4db86e` (`0x1f0` → `0x96ff`, G42) **y** `0x4db954` (`0x377` → `0x98a1`, rango estándar, el que manda en la lista normal): mismo patrón de 14 B con `[r7+0x38]`/`[r7+0x28]`, variante `sub.w r2,r1,#0x23; cmp r2,#0xd; movlo r1,#0x2f`.
- `libObj` no tiene hueco en `.text`: cuevas en segmento nuevo (`b.w` desde el sitio; alcance ±16 MB, `libObj` 16 MB).
- Un parche parcial de `libObj`/UI rompería la pantalla ISO (G42: `getIso` cae a error con códigos > `0x26`): **no se integra nada de eso hasta tener la cadena completa**.

## 8. Interfaz: mapa medido y referencia A7S (23-11-2026, segunda sesión)
### 8.1 La A7S 3.20 ya lo hace (mismas bibliotecas, con símbolos)
- `libObj`: `VALUEID_ISO_256000/320000/409600` = `0x50e/0x50f/0x510` (128000–204800 = `0x3fd–0x3ff`, como la A6000). Sus listas de valores válidos (tramos de 16 B desde `0xd06cd8`) incluyen `…0x277, 0x3fd, 0x3fe, 0x3ff, 0x50e…0x513`; las de la A6000 (`0xe383b8`, `0xe384e8`… 16 listas) acaban en `0x277` + ids dB.
- `WrapperIso::getIso` (vu2 A7S `0x19847d`): códigos de modelo **`0x4b…0x50` = 128000…409600** (además de `0x27–0x29`). Es la opción «códigos ≥ `0x4b`» de §2: av-cam tendría que traducirlos a sus índices `0x2a–0x2f`.
- `CautionConfig` A7S: nodos `ISOSensitivity64000…409600` con id de proceso `0x23…0x2b` (su numeración, 2 por encima de la A6000) y textos (`0xf819` 128000, `0xf838` 256000, `0xf834` 409600; no existen en el `.uxc` de la A6000).
### 8.2 La pantalla ISO de la A6000 (VERIFICADO en bytes + arnés)
- La pantalla que abre el botón ISO (y el menú) es `ViewManualControlDial_D` de `viewUnified4` (tipo 3 = ISO, `WrapperIso` en `+0x1cc`), **no** el árbol de nodos de `CautionConfig` (cuadra con G46: `_getSubNode` no influye). Captura de fábrica: lista vertical …10000–25600 y panel «ISO 25600».
- Filas = elementos fijos del diseño. Tabla valor→fila en `0x16c3d8` (función `0xbc138`, ≤ `0x4c`, si no fila `0x31`): `ISO_50…ISO_32000` (`0x30…0x4c`) → filas `0x2f…0x13`. Tabla fila→valor en `0x16c2c4` (`0xbd190`, filas 5…`0x3f`): **filas `0x6…0x12` libres (`0x4f`)**: 13 huecos encima de 32000 = 40000…640000. La A7S tiene la misma tabla.
- Enum `WRAPPER_ISO` (nombres en vu4 `0x1778e3`): MFNR `0…0xe`, AUTO `0xf`, AUTO_MIN `0x10–0x1f`, AUTO_MAX `0x20–0x2f`, `ISO_50…ISO_51200` = `0x30…0x4e`, `ISO_INVALID` `0x4f`. `getIso` modo 0 lee `getModelInfo("@M00B", 0x48)` claves `0x1f4/5/6`; mín./máx. son los límites del ISO AUTO, no los de la lista.
- Disponibilidad por fila: `WrapperIso::isInhOn` → `processDataMgr` elemento `0x15` → `isValueGrayedOut(id de proceso)` (`+0x67ea8`, `tbh` ≤ `0x4a`) → `WrapperSettingUtil::isInhOn(clave)`: `0x1e`→`0x13b` (32000), `0x1f`→`0x13c`, `0x20`→`0x38f`; esas claves las resuelve el motor de inhibiciones de `libObj` (`0xa76540`: campo de 105 palabras por factor, servicio externo), no el MAX.
- Pruebas en el arnés (fábrica 3.21 + overlay; botón ISO = `derecha`), todas con la lista acabando en 25600 (sin ▼ debajo):
  - `x1`: `libObj` con el MAX forzado a `0x26` en `0x4db86e` **y** `0x4db954`;
  - `x3`: + `isValueGrayedOut` de `processDataMgr` sin inhibición para los ids `0x1e–0x20` (32000–51200);
  - `x4`: + `CautionConfig` con la lista `Default` (`iso_list_patch`).
  Así que el tope visible no sale del MAX, ni de la atenuación de `processDataMgr`, ni de los nodos. `x5` (`viewUnified4` con 25600 llevado a la fila libre `0x12`) dejó la pantalla en negro tras restaurar el estado: no concluyente. `SKIPFN=a76540` impide arrancar.
- **Lo que decide el tope visible sigue sin localizar.** Siguiente paso: arreglar `TRACELIB` del shim (no arma trampas en `viewUnified4`) y trazar `ViewManualControlDial_D`/`ViewIsoSensitivity` al abrir la lista.
### 8.3 Envío del ISO manual a av-cam (parte de ISO-409-C)
- `0x4e7c30` (libObj) arma la orden de ajustes: lee `PARAMID_ISO_SPEED_RATE_SET` `0x9700` (y `MIN/MAX_SET` `0x9701/2`, `ACT` `0x9703–5`) y la convierte con `0x4e10b8` (VALUEID → código); `MENU_STD_RANGE_*_SET/ACT` (`0x989f/0x98a2/0x98a0/0x98a3`) con `0x4e42b4`. El código va al mensaje con `0x4a5836`. Nombres de PARAMID verificados en la tabla `0xfdc940 − 4·0x96ff`.
### 8.4 Arnés
- `setup.sh` necesitaba `linux-libc-dev_7.3.5-1` (la 7.3.3 ya no está en Debian). El directorio de trabajo debe ir en una ruta corta (socket de qemu < 108 B); se usó `/tmp/claude-1000/a6k`. `TRACELIB` sigue sin armarse en `viewUnified4` (como G47).

## 7. Estado y lo que falta
Hecho: av-cam. Pendiente (en PENDIENTES ISO-409-A…D): códigos/ids definitivos y conversores de `libObj` (6 funciones + MAX en 2 sitios), `cmn_view_processDataMgr` (`getValue/setValue/convertProcValToModelVal`, tabla `mappingValIsoSensitivity`), `WrapperIso` en `viewUnified2` (`getIso` 3 cadenas, `setIso`, `convertValueToProcessValueId`), nodos y lista en `CautionConfig` + textos, camino real del ajuste manual hasta av-cam (en el arnés no sale ninguna orden) y prueba en el arnés (el directorio de trabajo del arnés ya no existe: rehacer con `setup.sh`).
