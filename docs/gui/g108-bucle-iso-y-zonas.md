# G108 — Causa del bucle de arranque de `iso`, validador ISO de `libObj` y Film/ISO fuera de las tablas vivas (24-11-2026)

Continúa [G107](g107-causas-pp-ids-zonas.md). Por orden del usuario no se ha instalado nada: todo es estático o en el arnés (`live.py` con av-cam en la VM LIRO y la NVRAM del usuario del 22-11, `20261122-lutsd385b`).

## 1. Bucle de `iso`: con un ISO 128000+ guardado, la app no arranca (MEDIDO en el arnés)

**El ajuste ISO se guarda en la NVRAM `0x10700c1`** como código de `libObj` (VERIFICADO):
- el parámetro del modelo se crea en `libObj` `0x4ca972` con id `0x10700c1`, defecto `0x2a` e índice `0x100`;
- en el volcado del 22-11 vale `0x15` (ISO 1000, lo que muestra el arnés);
- 204800 es `0x4d`, y 128000–409600 son `0x4b…0x50`.

**Prueba:**
- Mismo perfil, arranque en frío. Se cambia solo `0x10700c1` y la build.
- Se mide si av-cam recibe órdenes de la app (`0x30001`, con el paquete de ajustes de arranque `0x4074`, que lleva el ISO en `0x4032`).

| NVRAM `0x10700c1` | Build / variante | Arranques con órdenes |
|---|---|---|
| `0x4d` (204800) | `iso` G106 | 0/2 |
| `0x4d` | `iso_ui` G106 | 0/1 |
| `0x4d` | `iso_ui` + validador ISO ampliado (§2) | 0/1 |
| `0x4d` | `iso_ui` con el indicador ISO de vu2 deshecho | 0/1 |
| `0x4d` | `iso_nucleo` (interfaz de fábrica) | 1/1 (43 órdenes, ISO `0x00`) |
| `0x4d` | `iso_ui` con `libObj` de fábrica | 1/1 |
| `0x4d` | `iso_ui` con `viewUnified2` de fábrica | 1/1 |
| `0x4d` | `iso_ui` con solo el gancho `isInhOn` deshecho | 1/1 (pantalla «ISO 204800») |
| `0x4d` | `iso` corregida (§1, §2) | 5/6 |
| `0x15` (1000) | `iso` G106 | 2/3 |

- **Ruido del arnés:** un arranque de cada dos o tres se queda en el estado inhibido ya conocido (G104 §8.5: solo «P», teclas sin efecto, ninguna orden a av-cam), con cualquier build.
- Por eso la prueba es estadística: 0/5 con el gancho original, frente a 11/13 en el resto de combinaciones.

**Causa:** el gancho de `WrapperIso::isInhOn` de `iso_ui_patch` (vu2 `0x1c1bf6`) daba a los enums nuevos (64000–409600) el id de proceso `0x2f`.
- Ese id es el del enum nativo `0x10` (tabla `tbh` de `0x1c1a20`, decodificada).
- Con el ISO actual en 128000+, la app se queda antes de mandar nada a av-cam.
- En la cámara, eso encaja con un bucle de reinicios (INFERENCIA): el arranque nunca termina.
- **Arreglo:** los enums nuevos usan `0x20`, el id de 51200 (enum `0x4e`). Así `isValueGrayedOut` evalúa la misma clave que la fila nativa más alta (`0x38f`).
- Test `tests/test_g104_iso_filas.py::test_vu2_isinhon`.

**Por qué solo `iso`:** `film`, `exfine` y `pp` llevan `WrapperIso` y `libObj` de fábrica.
- El código `0x4d` no se convierte en un valor, la app lo trata como desconocido y arranca: con `iso_nucleo` y la misma NVRAM, el paquete `0x4074` lleva ISO `0x00`.

**Encaja con INC-392 (INFERENCIA):**
- El 3.92 llevaba las filas hasta 204800 con el mismo gancho.
- Si en él se eligió 128000+ (la función ISO-409 pedida), el ajuste quedó en la NVRAM.
- La cámara dejó de encender con el 3.92 y volvió con `film`, sin interfaz ISO. Con `iso` vuelve a ponerse en bucle.
- El valor actual de `0x10700c1` en la cámara no se ha leído.

## 2. Validador de `libObj` para ISO (VERIFICADO con Unicorn) y arreglo

Las listas de [G107 §1](g107-causas-pp-ids-zonas.md) (`0x95aca8`, registros en `0xfde034`) para los PARAMID ISO de la `libObj` 3.21:

| PARAMID | Lista | 128000–204800 (`0x3fd…0x3ff`) | 256000–409600 (`0x50e…0x510`) |
|---|---|---|---|
| `ISO_SPEED_RATE` `0x951e` | 79 | sí | **no** |
| `ISO_SPEED_RATE_SET`/`_ACT` `0x9700`/`0x9703` | 76 | **no** | **no** |
| `ISO_SPEED_RATE_MIN/MAX(_SET/_ACT)` `0x96fe/f`, `0x9701/2`, `0x9704/5` | 46 | **no** | **no** |

- **Explica G104 §8.7 (ISO-409-A):** 256000–409600 «vuelven a 204800» porque `0x951e` rechaza `0x50e…0x510`. La orden con 128000+ (`0x9700`) tampoco pasaba.
- **Arreglo:** `pp_valuecheck_patch.amplia_pids` (generaliza el arreglo de PP de G107) añade los VALUEID de `iso_libobj_patch.VALUEIDS` a esas 9 listas. Lo aplica `iso_libobj_patch.patch`.
- Test `tests/test_g108_iso_valuecheck.py` (2).
- **No era el bucle:** con el validador ampliado y el gancho viejo, la app seguía sin mandar nada (§1).
- **Queda (ISO-409):** con 204800 guardado, el paquete de arranque lleva ISO `0x00`, no `0x4d`. La interfaz muestra 204800, pero al arrancar el núcleo no lo recibe. Sin localizar.

## 3. Film e ISO fuera de `ZONA_A`/`ZONA_B` (ZONA-1, parcial)

**Lo que se sabe (G107 §3):** `ZONA_A` es la tabla T1 y `ZONA_B` las tablas BOKS.
- Hay lectores reales. Por ejemplo, `0x43556c4c…` pasa tres canales (valor >> 4) por T1 y usa el resultado en `0x43b11c2c`.
- **Núcleos que escriben ahí:**
  - `film` (593 B en T1);
  - `iso` (cueva en T1[1012…], tabla EXIF en BOKS);
  - el 3.92 (ambos).
- `pp` y `exfine` no escriben ahí.

**Cambio:**
- `avcam_dinamico.ZONA_G18 = 0x43faf300…0x43fb7400`: las ranuras de curvas de PP del hueco G18. PP ya ejecuta código ahí en la cámara y Silent solo usa `0x43fb7e00…+106`.
- `film_patch` (celdas + código, `0x43faf300…0x43faf59c`) e `iso_avcam_patch` (cueva `0x43faf700`, tabla EXIF `0x43faf720`) van ahí.
- `comprobar_zonas` admite la zona pedida.
- Con PP en el núcleo la zona no está a cero y la build se rechaza (Film/ISO con PP queda en ZONA-1).
- Comprobado en el `av-cam` de las builds nuevas: 0 bytes cambiados en `ZONA_A`/`ZONA_B`.
- Tests: `test_g97_films.py::test_avcam_solo_ganchos_y_zona_g18`, `test_g104_iso_avcam.py::test_cadena_cfw_film`; `test_g103` pasa al núcleo sin PP.

**Lo que NO se pudo probar:** que esto cause o arregle los «botones pegados» de Film.
- Con Film en el arnés, los arranques inhibidos parecían ligados a `ZONA_A`: núcleo con T1 contaminada y sin ganchos 0/1, `film` 0/3.
- Pero la `film` anterior arrancó en otra ronda (1/5 en total) y la reubicada 2/4: es el ruido del arnés, no `ZONA_A`.
- La reubicación se hace porque escribir en tablas que el núcleo lee es un defecto; no por una medida.

## 4. Builds (3.93; `audit_package_nflasha15 --darwin-v3 --sin-wbi --bionz-g22`)

| Build | Cambio | `.dat` sha256 |
|---|---|---|
| `iso` | §1 + §2 + §3 | `fee2bc4fbb644771b779141b618d805de02022e60114d7211aeffa97f86ae5d5` |
| `iso_ui` | §1 + §2 | `4d7083c97c1ead735d5dc9904f097deb2e0b1f8da0de93742e3aa232c6cf3535` |
| `iso_nucleo` | §3 | `103cfaa3c900db38c4574180b502ecb21ee3a434df06c8326dfb3336d53e0f63` |
| `film` | §3 | `727fb352c455ff11bdf1a9d23bf459623691234cbca9897195df0119b67be1d6` |
| `film_nucleo` | §3 | `c860313339cf27ab70ec7c2193569182ab29204a65427c4f1fb13e65109705e9` |

Las cinco dan `todo_ok`. La auditoría ya no aborta al recomponer el núcleo «Film + PP» del 3.92, que ahora se rechaza (`bionz_g22_checks`).

`pp`, `exfine` y `film_ui` no cambian ([G107 §5](g107-causas-pp-ids-zonas.md), [G106 §5](g106-auditoria-estatica-393.md)).

**Sin verificar en cámara:**
- que `iso` arranque con la NVRAM actual;
- que 128000–204800 lleguen al núcleo;
- el efecto de la reubicación en Film.
