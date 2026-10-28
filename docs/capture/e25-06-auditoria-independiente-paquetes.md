# E25-06 — Auditoría independiente de B1a 3.23 y recuperación 3.24 (27-10-2026)

Auditoría **100 % offline** del commit `67fd3a40` (E25-05, construido por DeepSeek V4.1 Flash). No se
conectó la cámara, no hubo USB, no se ejecutó ninguna actualización, no se escribió RAM/NVRAM/NAND y no
se flasheó. Los paquetes se abrieron con `mmap` de solo lectura; sus SHA-256 son los mismos antes y
después (§2). No se modificó B1a ni ningún paquete, y no se creó ninguna versión nueva.

## 0. Resultado en una frase

**No hay ningún defecto binario: los dos paquetes son exactamente lo que dicen ser** (145
comprobaciones independientes, 0 fallos; 21 pruebas, 15 de ellas negativas). Eso no hace segura la
instalación: la aceptación por la cámara, la recuperación independiente de Darwin y el efecto físico de
B1a siguen sin demostrarse. **N = SÍ y R = NO.** Las pruebas de E25-05 tienen puntos ciegos demostrados
(§8), pero ninguno oculta un error en los artefactos.

## 1. Método e independencia

| Aspecto | E25-05 | E25-06 (esta auditoría) |
|---|---|---|
| Contenedor `.dat`, DEND, UDID | `fwtool` (`readDat`) | Parser propio (`struct`, `zlib`) |
| Descifrado y sumas por bloque | `fwtool` + `Cryptodome` | Descifrador propio con AES de `cryptography`; de `fwtool` solo se leen las dos claves como literales (`ast`) |
| Validación del descifrador | Ninguna: el mismo `fwtool` crea y verifica | **Control positivo**: el descifrador propio reproduce byte a byte el `firmware.fdat` de Sony a partir del `.dat` original (`29aef21a…`; 207 996 bloques) |
| Cabecera FDAT | `FdatHeader` de `fwtool` (sin offsets ni tabla de FS) | Parser propio: los 512 B, campos reservados, tabla de 28 FS, offsets, BCD |
| tar | `tarfile`, solo ficheros regulares | Parser ustar propio: cabeceras crudas, sumas, tipos, padding, bloques de cierre |
| Sumas del actualizador | Solo `darwin.sum` | Se reproduce `uc_crc32sum -c` (tamaño, CRC, permisos) sobre los 7 `*.sum` del tar |
| Semántica de B1a | Capstone/REA (E25, E25-02) | **Emulación con Unicorn** con control diferencial original / tipo 0 / B1a |
| Valores esperados | Constantes del propio script | Tecleados aparte desde la orden E25-06 y cruzados con los commits que los registraron por primera vez |

Herramienta: [`scripts/e25_06/audit_packages.py`](../../scripts/e25_06/audit_packages.py) → `analysis/e25-06/audit.json`.
Pruebas: [`tests/test_e25_06_auditoria.py`](../../tests/test_e25_06_auditoria.py).

## 2. Hashes obtenidos directamente

| Fichero | SHA-256 real | Tamaño | Esperado (orden) | Manifiesto E25-05 | `SHA256SUMS` |
|---|---|---|---|---|---|
| `experimental-323/firmware_packed.dat` | `4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542` | 212 988 056 | = | = | = |
| `experimental-323/firmware_packed.fdat` | `268621fb70948fc58676bb19bcf82e7d73a2634d0085e3032d64833b04fc6e49` | 212 155 392 | = | = | = |
| `recuperacion-324/firmware_packed.dat` | `e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22` | 212 988 056 | = | = | = |
| `recuperacion-324/firmware_packed.fdat` | `24ee9b42e9fae29c7a86ec5f17d85d9a5076a8a36698a3766e0b13801126b2c2` | 212 155 392 | = | = | = |

Contenido extraído (por el parser propio, no por `fwtool`):

| | Experimental 3.23 | Recuperación 3.24 |
|---|---|---|
| `firmware.tar` interno | `ae6d76eae9ff9363…` = esperado | `970246492293e917…` = oficial, idéntico byte a byte |
| `darwin_core.bin` | `55a366a5fc95f01c…` = B1a; CRC-32 `cf930ac9` | `5f2be06d9885d154…` = oficial; CRC-32 `9ff7148c` |
| `updater.img` | `b6d5175245c8fb26…` = oficial, byte a byte | igual |
| CRC-32 de cabecera FDAT | `cc61c53c` (almacenado = calculado) | `ede492ca` (almacenado = calculado) |
| CRC DEND | `1e8cbc86` (almacenado = calculado) | `b7c6243b` (almacenado = calculado) |

Paquetes y entradas anteriores, comparados con el SHA-256 registrado en git **antes** de E25-05:

| Artefacto | SHA-256 actual | Registrado en |
|---|---|---|
| 3.22 instalado `.dat` / `.fdat` (T024) | `c19a1463…` / `ddc2d5db…` | `210e9d21` (informe de T024) |
| Recuperación 3.23 antigua `.dat` / `.fdat` | `5f108901…` / `cfb65c8a…` | `f5de42b0` (E24-03) |
| Darwin tipo 0 | `ca41b46c…` | `f5de42b0` |
| Darwin, tar y `updater.img` oficiales 3.21 | `5f2be06d…`, `97024649…`, `b6d51752…` | `ac94c961` |
| `.dat` original de Sony | `29aef21a…` | `firmware/hashes/sha256.json` |
| B1a | `55a366a5…` | `d26f687c` (E25) |

Todos coinciden. `firmware_tipo0.tar` no tiene hash en git, pero es idéntico byte a byte al tar
contenido en el `.fdat` 3.22 (cuyo hash sí está registrado). El experimental solo difiere de él en los
2 bytes de B1a y en el CRC del sum (§4).

## 3. Integridad estructural (primera auditoría)

| Comprobación | Experimental 3.23 | Recuperación 3.24 |
|---|---|---|
| Magia `.dat`; chunks `DATV, PROV, UDID, FDAT, DEND`; 0 B tras DEND | PASS | PASS |
| `DATV` = `0x100`, `isLens` = 0 (no es objetivo); `PROV` = `0x100` | PASS | PASS |
| UDID byte a byte = `.dat` de Sony y = 3.22 (10 descriptores normales + `054c:03e2` actualizador) | PASS | PASS |
| Disposición de chunks (offsets y tamaños) = Sony = 3.22 (FDAT en 140, 212 987 904 B) | PASS | PASS |
| 207 996 bloques: suma de 16 bits, bandera de último bloque solo en el último, longitud 1020 salvo el último | PASS | PASS |
| `.fdat` descifrado del `.dat` = `.fdat` del directorio (streaming, byte a byte) | PASS | PASS |
| `UDTRFIRM`, formato `0100`, modo `U`, LUW `N`, reservados a cero | PASS | PASS |
| Modelo `0x41030035`, región 0, fuera de la familia `0xA0xxxx` de accesorios | PASS | PASS |
| Versión mayor 3; menor `0x23` / `0x24` (BCD válido) | PASS | PASS |
| Tabla de FS: `U`@512+143 360, `P`@512+0, 26 vacías; tar en [143 872, 212 155 392) | PASS | PASS |
| Cabecera FDAT frente a la de Sony y a la del 3.22: solo difieren `[8,12)` (CRC) y `[32,33)` (versión) | PASS | PASS |
| tar: 105 entradas, sumas de cabecera, padding nulo, 2 bloques nulos de cierre | PASS | PASS |
| Los 7 `*.sum` (config, backup, partconf, darwin, prfile, part_image, appli; 80 entradas) cuadran en tamaño, CRC y permisos | PASS | PASS |

La cabecera de ambos paquetes es la de Sony con solo la versión y su CRC cambiados: `fwtool pack` no
introduce ningún campo distinto del original.

## 4. Comparación de los `firmware.tar` (segunda auditoría)

Orden, nombres, tipos, permisos, propietarios, `mtime`, cabeceras crudas de 512 B, padding y tamaño
total (212 011 520 B) son **idénticos** al tar oficial en los dos paquetes. Diferencias calculadas byte
a byte (no tomadas de la lista de E25-05):

| Comparación | Miembros distintos | Bytes distintos (offset dentro del miembro) |
|---|---|---|
| Experimental vs oficial | `0640_darwin/darwin_core.bin`, `0641_darwin_sum/darwin.sum` | core: `[0x1bc6a,0x1bc6c)` (B1a), `[0x1ca78,0x1ca7c)` y `[0x1ca7d,0x1ca80)` (tipo 0); sum: `[2,3)` y `[4,10)` (CRC; el 4.º carácter coincide) |
| Experimental vs 3.22 instalado | los mismos dos | core: solo `[0x1bc6a,0x1bc6c)`; sum: CRC `0e2620b4 → cf930ac9` |
| Recuperación vs oficial | ninguno | idéntico byte a byte |

No hay entradas añadidas ni eliminadas, y `updater.img` es el oficial en ambos.

**Reproducibilidad:** reconstruí el experimental desde las entradas oficiales con mi propio parcheo del
tar (sobrescribiendo solo los datos de los dos miembros) y `fwtool pack`: salen exactamente
`4c21353d…`/`268621fb…`. La reconstrucción del 3.24 ya la cubre `test_recovery_324_rebuilds_byte_for_byte`.

## 5. Parche B1a (tercera auditoría)

| # | Comprobación | Resultado | Método |
|---|---|---|---|
| 1 | Exactamente 2 bytes distintos del tipo 0: ROM `0x1fe6a/0x1fe6b`, fichero `113770/113771`, `28 46 → 0a e0` | PASS | comparación |
| 2 | `0xe00a` es `B.N`; destino `0x1fe6a + 4 + 10·2 = 0x1fe82` | PASS | decodificación manual |
| 3 | Retorno: `push {r4,r5,r6,lr}` / `mov r0,r5; pop {r4,r5,r6,pc}` intactos; r4–r7 y SP preservados, vuelve a LR | PASS | emulación |
| 4 | No se ejecuta `0x1b080`: 0 llamadas en 259 ejecuciones | PASS | emulación |
| 5 | `0x1fe66` devuelve 0 para los 256 valores del byte y para `0x100`, `0x1234` y `0xffffffff`. **Control:** el tipo 0 devuelve el nibble alto 1..5 y 0 en el resto | PASS | emulación diferencial |
| 6 | Los tres arrancadores (`0x1fee2`, `0x1ff72`, `0x1ffce`) toman en la rama `cbz r0` el puntero `0x29cd8` → `[0,7,8,9,10]` (L0); r0 no se toca entre `bl 0x1f5a2` y `cbz` | PASS | Capstone + literales |
| 7 | Tipo 0 intacto en `0x20c78` (`09 e0 00 bf 00 bf 00 bf`) | PASS | bytes |
| 8 | Los 4 escritores P4D/P4E (`0x20c90`, `0x20cb2`, `0x20cd4`, `0x20d00`) no llegan a `0x51c0` para ningún tipo 0..7. **Control:** el original sí escribe `0x234`/`0x238` con tipo 1/2/3 | PASS | emulación diferencial |
| 9 | Regiones críticas idénticas al original: reinicio, scatter, buzón, `InitCom`, `0x51c0`, `Upd`, `Off`, CRC `0xa1dc`, watchdog, tarea COM, manejadores y tabla de energía; vectores SP/reset intactos; `VER0.78` presente | PASS | bytes |
| 10 | El core integrado es el fichero B1a auditado en E25/E25-02 (`55a366a5…`, registrado en `d26f687c`) | PASS | SHA-256 + igualdad |

Frente al **original oficial**: 9 bytes distintos = 7 del tipo 0 (`0x20c78..0x20c7f`; `0x20c7c` coincide)
+ 2 de B1a. No hay más.

**Consumidores:** un barrido propio de todas las codificaciones BL/B.W da exactamente los 12 sitios
directos de E25 (`0x1f4ba`, `0x1f4de`, `0x1f576`, `0x1f5a2`, `0x1f5a8`, `0x1f896`, `0x1f908`, `0x1fa40`,
`0x1fe88`, `0x1fe90`, `0x1fe98`, `0x201bc`), 6 llamadas al thunk `0x1f5a2` (los 3 arrancadores y
`0x20032`, `0x20092`, `0x200aa`) y ningún puntero literal a `0x1fe66` o `0x1f5a2`.

**Consecuencias semánticas, emuladas:**

- **Comprobación de leva `0x1f4ce`:** con la leva fuera de posición, el tipo 0 emite el error 6
  (`0x16558`) y B1a no. B1a **suprime** esa protección: si el mecanismo queda en una posición anómala,
  Darwin ya no lo detecta por esta vía. Es una consecuencia buscada, pero elimina un diagnóstico.
- **Operación 5 `0x1fcb8`:** la secuencia `0x51cc(4, v, 0xfffc)` es `v = 0, 3, 0` tanto en el tipo 0 como
  en B1a: B1a **no cambia** la operación 5. Sigue escribiendo P40=P41=1 (XOR 0, apagado según E25-02
  §3.6); que el motor frene o gire libre no está medido.

## 6. `darwin.sum` (cuarta auditoría)

| Comprobación | Experimental | Recuperación |
|---|---|---|
| Línea exacta | `0,cf930ac9,0002665c,000001a4,00000000,000003e8,root,root,-1,-1,darwin_core.bin,` + LF | `0,9ff7148c,…` = oficial byte a byte |
| CRC-32 (`zlib`) = core real | `cf930ac9` | `9ff7148c` |
| Tamaño = core real | `0x2665c` = 157 276 | igual |
| ASCII, una línea, LF sin CR, coma final, 12 campos | PASS | PASS |
| Permisos `0x1a4` = modo del miembro tar (`0644`, root/root, fichero regular) | PASS | PASS |
| Campos distintos de CRC y tamaño = oficial | PASS | PASS |

**Consumidor real.** `config.xml` ejecuta `us_crc32sum.sh darwin file` → `uc_crc32sum.elf -c` antes de
`us_darwin_firm.sh`. Sus cadenas muestran que comprueba **tamaño, CRC, permisos y tipo de entrada**
(«size mismatch», «crc mismatch», «permission mismatch», «not directory», «not link»). E25-05 no verificaba
permisos ni tipo; aquí se reproducen los cuatro sobre los 7 ficheros `.sum` y todos cuadran. Que el CRC
es el CRC-32 estándar lo confirman el sum oficial (`9ff7148c` = `zlib.crc32` del core oficial) y T024
(sum tipo 0 `0e2620b4`, mismo formato, aceptado e instalado).

**Otras comprobaciones del actualizador** (sin cambio respecto a lo que ya pasó T024): `chkfirm.sh`
(LSI principal: no hay `0100_config/sub.conf`), `chknandcapa.elf` sobre `partinf.conf` (idéntico) y el
guard de versión, batería y `uincomp` (en tiempo de ejecución; no verificables offline). Si el arranque
del MCU valida la imagen de Darwin sigue NO_VERIFICADO; T024 demuestra que aceptó un core con 7 bytes
cambiados y sin ninguna suma interna recalculada.

## 7. Recuperación 3.24 frente a la 3.23 antigua (quinta auditoría)

| Afirmación de DeepSeek | Real | Explicación verificada |
|---|---|---|
| `.fdat`: solo `[8,12)` y `[32,33)` | `[[8,12],[32,33]]` | CRC-32 de cabecera recalculado y `versionMinor 0x23 → 0x24` |
| `.dat`: `[140,156)`, `[172,188)`, `[212988052,212988056)` | Idéntico | Predicción independiente: el FDAT empieza en 140; el byte *p* de la cabecera va al offset *p*+4 del primer bloque, cuya suma ocupa `[0,2)`. Bloques AES de 16 B afectados: 0 (suma + CRC) y 2 (versión) → `[140,156)` y `[172,188)`; más el CRC DEND. **Predicho = real** |

El resto de los 212 MB es idéntico: la 3.24 es la antigua 3.23 con la versión subida, sin datos
recalculados. Los paquetes anteriores siguen intactos (§2).

**Confusión de artefactos (R7, comprobado):**

- Hay **cuatro** `firmware_packed.dat` bajo `analysis/darwin-patch/fdat/`: raíz (3.22 instalado),
  `recuperacion-323` (3.23, Darwin oficial), `experimental-323` (3.23, B1a) y `recuperacion-324` (3.24).
- `experimental-323/config-323.yaml` y `recuperacion-323/config-323.yaml` son **idénticos byte a byte**.
  Las dos cabeceras dicen 3.23, y `pmca-console` mostraría el mismo «Updating from version 3.22 to
  version 3.23» con cualquiera de ellos. **Solo el directorio y el SHA-256 los distinguen.**
- `recuperacion-323` y el directorio raíz no tienen `SHA256SUMS`; la nota de `scripts/recovery/r1_inventory.json`
  sigue llamando al 3.23 antiguo «FDAT de recuperación» sin marcarlo como obsoleto.

Efecto de un error de selección: si se instala por error `recuperacion-323` en lugar del experimental,
se queda Darwin oficial con 3.23 instalada. No daña la cámara, pero quema el número 3.23: B1a tendría que
reempaquetarse con ≥3.24 y su recuperación con ≥3.25. Si, tras instalar B1a, se intenta recuperar con
`recuperacion-323`, el guard lo rechazaría (misma versión). No es grave, pero hace perder tiempo en
plena recuperación. La corrección es procedimental (§11), no del paquete.

## 8. Puntos ciegos de las pruebas de E25-05 (demostrados)

Ninguno de ellos oculta un error en los artefactos (esta auditoría los cubre), pero reducen el valor
probatorio de «69 comprobaciones, 0 fallos»:

1. **Las pruebas pasan sin paquetes.** Con un árbol que solo tiene los JSON y `fwtool`,
   `tests/test_e25_05_paquetes.py` da **2 passed, 9 skipped, 0 failed**: `_need()` omite la prueba y no
   la hace fallar. `test_manifests_describe_the_pair` y `test_version_order_and_guard_rule` aprueban sin
   leer ningún paquete.
2. **El manifiesto no puede registrar un FAIL**: `check()` aborta con `SystemExit` antes de escribirlo,
   así que «0 fallos» sale por construcción.
3. **Comprobaciones que solo validan constantes:** `versions.order`, `versions.experimental_gt_installed`
   y `versions.recovery_gt_experimental` (aritmética sobre cadenas fijas); `differences.tar_vs_official` y
   `experimental_vs_recovery_tar_members_changed` en `diferencias-binarias.json` son `list(DARWIN_FILES)`
   escrito tal cual, no calculado. Por otro lado, `exp.input.official_sum_crc` dice «coincide con
   darwin.sum», pero compara el CRC del core con una constante y nunca lee `darwin.sum`.
4. **Circularidad:** `exp.sum_crc`/`exp.sum_size` buscan subcadenas en la salida de la misma función
   que las generó (no comprueban la posición del campo), y `verify_package` valida DEND, CRC y bloques con
   el mismo `fwtool` que construyó el paquete.
5. **Demasiado permisivas:** `diff.recovery_dat_header_and_dend` acepta cualquier cambio en los primeros
   512 B del FDAT cifrado (pasaría con el modelo o la región alterados); `exp.tar_changed_only_darwin`
   solo compara ficheros regulares por hash (no cabeceras, directorios ni miembros eliminados);
   `dat_descriptors` solo mira el descriptor del actualizador.
6. **Sin referencia histórica:** `existing.unchanged` compara antes/después de la ejecución y
   `snapshot()` ignora los ficheros ausentes; `firmware_tipo0.tar` y el `.fdat` 3.23 antiguo no se cotejan
   con ningún hash registrado.

## 9. Actualizador y compatibilidad (sexta auditoría)

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 1 | ¿Las versiones usan el formato correcto? | Byte 33 = mayor 3, byte 32 = menor BCD `0x23`/`0x24`, igual que el 3.21 de Sony (`0x21`) y el 3.22 (`0x22`). Tras T024, `pmca info` dio 3.22: la versión instalada que se registra es la de la cabecera | VERIFICADO |
| 2 | ¿Modelo, región y configuración? | Idénticos a los del `.dat` y el `.fdat` originales de Sony (cabecera y UDID byte a byte) | VERIFICADO |
| 3 | ¿El `.dat` es el contenedor de T024? | Sí: T024 usó `pmca-console firmware -f firmware_packed.dat`, con la misma disposición de chunks, los mismos offsets y los mismos descriptores | VERIFICADO |
| 4 | ¿Se reescribe todo aunque solo cambie Darwin? | Sí. `config.xml` recorre todos los `*_sum`: `part_image` (`nflasha3/5/7/15/16`, ~200 MB), `partconf` + `us_mkfs.sh`, `backup`, `prfile`, `appli` y Darwin. `nflasha1` (actualizador) **no** está en el paquete | VERIFICADO (estático) |
| 5 | ¿Puede fallar por otra validación? | `uc_crc32sum` (reproducido, OK), `chkfirm.sh` y `chknandcapa` (contenido idéntico al oficial). Quedan el guard con 3.22, la batería y `uincomp`, que solo se ven en ejecución | Parcial: estático OK, ejecución NO_VERIFICADO |
| 6 | ¿Dependencia de `VER0.78`? | Ambos cores llevan `VER0.78`; sin `darwin_boo.bin`, `ud_darwin_firmup` reescribe siempre el core (E24-03 F8, ejercitado en T024) | VERIFICADO |
| 7 | ¿El 3.24 se instala si BIONZ y el actualizador siguen vivos? | Sí: la ruta de T024 es pmca → actualizador → `ud_darwin_firmup`. B1a no toca ningún byte de energía, `InitCom`, `Upd` ni watchdog, y ninguno de ellos consume la compuerta | Estático VERIFICADO; en ejecución NO |
| 8 | ¿Y si se interrumpe? | La escritura no es atómica (M16/F7/F10 de E24-04). La ventana peor es `ud_darwin_firmup` (hilo): un core a medio escribir no tiene recuperación demostrada | INFERENCIA |
| 9 | ¿Coherencia de versiones entre capas? | Cabecera, `config-32x.yaml` y `SHA256SUMS` coinciden. El contenido principal es el oficial 3.21 y `VER0.78` es la versión interna de Darwin, que no depende de la del paquete | VERIFICADO |
| 10 | ¿Efectos de reinstalar el principal 3.21 con versión 3.23/3.24? | Particiones idénticas a las oficiales, pero la cámara pasa a declarar 3.23/3.24, y volver a un número menor (incluido el 3.21 de Sony) exige reempaquetar con un número mayor. Tras T024 se vieron el reloj reiniciado (EXIF 2014-01-01) y wifi/telnet sin respuesta, sin causa aislada | Observado una vez; causa NO_VERIFICADA |

La regla «solo versiones estrictamente mayores» **se midió con 3.21 instalada** (3.20/3.21 rechazadas,
3.22/9.99 aceptadas). Con 3.22 instalada es **INFERENCIA**: 3.23 > 3.22 y 3.24 > 3.23.

## 10. Riesgos específicos (séptima auditoría)

| Riesgo | Clase | Evidencia y alcance |
|---|---|---|
| **R1** Arranque de Darwin con B1a | **Hipotético** | B1a no cambia nada del arranque (bytes y consumidores). Con B1a, el arrancador de carga elige L0 (sin motor). Que BIONZ y Darwin toleren un mecanismo sin rearmar durante el arranque y el disparo no está demostrado (E25-04 F: sin contradicción estática; P29 y el lector BIONZ del fin, abiertos) |
| **R2** Alimentación de BIONZ | **Hipotético, gravedad máxima** | Tabla de energía `0x28c6c`, manejadores y `0x51c0` idénticos byte a byte, sin consumidores de la compuerta. Si en ejecución faltara `DD_ON1/2/3`, no hay recuperación USB demostrada (E25-04 A/B/C = NO) |
| **R3** Actualizador inaccesible | **Hipotético** | `nflasha1` no se reescribe. El 3.24 solo sirve si se llega a `pmca` → actualizador → `InitCom` → `Upd`; sin esa cadena no sirve |
| **R4** Reintroducción del mecanismo | **Comprobado (por diseño)** | El 3.24 instala el Darwin oficial: vuelven las bobinas (sin tipo 0), el motor, la comprobación de leva y el rearme. No restaura el tipo 0; para eso hace falta ≥3.25. Si el mecanismo quedó desarmado o en una posición anómala con B1a, el primer arranque con el Darwin oficial intentará rearmar; ese efecto no está medido |
| **R5** Pérdida de versión | **Comprobado (aritmética)** | Cada instalación consume un número. Tras 3.24, la siguiente prueba exige ≥3.25 y su recuperación ≥3.26. Nunca 9.99 (el guard la aceptó con 3.21 y cerraría la vía). Instalar por error `recuperacion-323` quema el 3.23 (§7) |
| **R6** Integridad del firmware principal | **Comprobado** | Cada paquete reescribe ~200 MB de particiones, formatea según `partconf` y reescribe backup, prfile, appli y Darwin; no solo 2 bytes. Pasa dos veces (3.23 y 3.24). El contenido es el oficial, verificado por CRC en el propio actualizador |
| **R7** Paquetes confundidos | **Comprobado** | §7: dos paquetes 3.23 con `config-323.yaml` idéntico y el mismo nombre de fichero; solo el directorio y el SHA los distinguen |
| **R8** Falta de respaldo externo | **Comprobado (documental)** | R1 sigue PARCIAL: copia externa no hecha ni verificada (E25-04 D = NO; PENDIENTES R1). Además, `r1_inventory.json` no incluye `experimental-323` ni `recuperacion-324` (0 coincidencias). Se pueden regenerar byte a byte desde entradas que sí están en el inventario (§4), pero eso exige el script y `fwtool` |

## 11. Pruebas negativas

`tests/test_e25_06_auditoria.py` (21 pruebas, 21 PASS; las mutaciones se hacen sobre copias en memoria
o en `tmp_path`, nunca sobre los paquetes):

| Caso pedido | Prueba | Se detecta por |
|---|---|---|
| Byte de Darwin no autorizado (`Upd main`) | `test_unauthorized_darwin_byte_is_detected` | diff vs tipo 0, diff vs original, regiones críticas |
| Tipo 0 eliminado | `test_removed_tipo0_is_detected_by_bytes_and_emulation` | bytes **y** emulación (los escritores P4D/P4E vuelven a llamar a `0x51c0`) |
| Versiones 3.23/3.24 intercambiadas | `test_swapped_versions_are_detected` | `version_minor`, también con el CRC recalculado |
| B1a por error en la recuperación | `test_b1a_accidentally_in_recovery_is_detected` | tar ≠ oficial y SHA del core |
| Darwin experimental sustituido por el original | `test_original_darwin_instead_of_b1a_is_detected` | 2 bytes, retorno ≠ 0, lectura de `0x1b080`, salto |
| Miembro no Darwin del tar alterado (`nflasha3`) | `test_non_darwin_tar_member_change_is_detected` | `only_authorized_differ` nombra el miembro |
| CRC, tamaño, permisos o CRLF en `darwin.sum` | `test_corrupted_darwin_sum_is_detected` (×3), `test_darwin_sum_crlf_is_detected` | campo correspondiente / formato |
| Cabecera FDAT alterada (modelo, región, mayor, tamaño, FS) | `test_altered_fdat_header_is_detected` (×5), `test_accessory_model_is_rejected` | primero CRC; con CRC recalculado, el campo |
| Contenido de un bloque cifrado alterado | `test_altered_encrypted_block_is_detected` | DEND; con DEND recalculado, la suma del bloque 1000 |
| `.dat` que no corresponde al `.fdat` | `test_dat_not_matching_declared_fdat` | `dat_matches_fdat`, SHA, versión |
| Falta un paquete real | `test_missing_package_is_never_pass` | `MISSING`, ningún PASS |
| Manifiesto en PASS con fichero distinto | `test_manifest_says_pass_but_file_differs` | SHA real ≠ declarado |

Las pruebas **fallan** (no se omiten) si falta un paquete local; en CI el `conftest.py` existente las
convierte en omitidas, como al resto de pruebas con firmware.

## 12. Veredictos

| | Pregunta | Respuesta | Evidencia y alcance |
|---|---|---|---|
| **A** | ¿Los cuatro DAT/FDAT coinciden con sus hashes? | **SÍ** | §2: SHA-256 y tamaños reales = orden = manifiestos = `SHA256SUMS` |
| **B** | ¿Integridad estructural válida? | **SÍ** | §3: DEND, 207 996 bloques, cabecera, offsets, tabla de FS, tar, 7 sumas del actualizador; descifrador validado contra el `.dat` de Sony |
| **C** | ¿El experimental contiene exactamente B1a? | **SÍ** | §5: core = `55a366a5…`; 2 bytes vs tipo 0; 9 vs original |
| **D** | ¿Tipo 0 intacto? | **SÍ** | Bytes `0x20c78` + emulación de los 4 escritores con control positivo |
| **E** | ¿Experimental declara 3.23? | **SÍ** | Mayor 3, menor `0x23`, CRC válido, config 3.23 |
| **F** | ¿Recuperación = Darwin original previsto? | **SÍ** | `5f2be06d…`, `9ff7148c`; tar oficial byte a byte |
| **G** | ¿Recuperación declara 3.24? | **SÍ** | Menor `0x24`, CRC válido |
| **H** | ¿`updater.img` oficial intacto en ambos? | **SÍ** | Byte a byte con `b6d51752…` |
| **I** | ¿Solo cambiaron componentes y bytes autorizados? | **SÍ** | §4: exp = 2 miembros (9 B de core + 7 de sum frente al oficial); rec = 0; cabecera = versión + CRC |
| **J** | ¿3.24 = 3.23 antigua salvo versión y comprobaciones dependientes? | **SÍ** | §7: rangos reales = predichos |
| **K** | ¿Paquetes anteriores intactos? | **SÍ** | §2: hashes = los registrados en git antes de E25-05 |
| **L** | ¿Defecto reproducible que obligue a reconstruir? | **NO** | Ninguno encontrado. Los hallazgos (§7 R7, §8, R8) son procedimentales o de prueba, no de los binarios |
| **M** | ¿Las pruebas de E25-05 son suficientemente independientes? | **NO** (puntos ciegos demostrados) | §8: pasan sin paquetes, un manifiesto que no puede fallar, constantes, circularidad. Sin efecto en los artefactos |
| **N** | ¿Binariamente correctos para su propósito? | **SÍ** | A–K |
| **O** | ¿Aceptación física demostrada? | **NO** (evidencia insuficiente) | Nunca probado en cámara. Analogía fuerte con T024 (misma tubería, cabecera y contenedor), pero el guard con 3.22 es inferencia |
| **P** | ¿Recuperación independiente de Darwin demostrada? | **NO** (evidencia insuficiente) | E25-04 A/B/C = NO. El 3.24 depende de Darwin vivo, `DD_ON*`, `InitCom` y `Upd` |
| **Q** | ¿B1a funciona físicamente sin obturador mecánico? | **NO** (evidencia insuficiente) | Solo estático y emulación de funciones aisladas; E25-01 sigue bloqueado |
| **R** | ¿Las evidencias permiten declarar segura la instalación? | **NO** (evidencia insuficiente, no defecto) | O, P y Q = NO; R1 (respaldo) sin cerrar; E25-04 G = NO se mantiene |

## 13. Decisiones

- **Integridad binaria: APROBADA.** Los paquetes `experimental-323` y `recuperacion-324` no necesitan
  reconstruirse.
- **Instalación y recuperación: NO AUTORIZABLES con la evidencia actual.** Esta auditoría no cambia
  E25-04 G = NO: que los paquetes sean correctos no demuestra que la cámara los acepte, que B1a arranque
  o que el 3.24 recupere un Darwin defectuoso.

**Acciones mínimas** (no son defectos de los paquetes; se registran en PENDIENTES):

1. **Antes de cualquier instalación**, comprobar el SHA-256 del fichero exacto que se pasa a
   `pmca-console`: `4c21353d…` para la prueba y `e1345aff…` para la recuperación. No basta con el nombre
   ni con el mensaje de versión.
2. Marcar `recuperacion-323` como obsoleto en la documentación de procedimiento y en la nota de
   `r1_inventory.json`, sin tocar el paquete.
3. Incluir `experimental-323/` y `recuperacion-324/` (o su regeneración documentada) en el respaldo R1
   antes de hacer la copia externa.
4. Opcional (calidad): que las pruebas de E25-05 fallen si falta un paquete. Las de E25-06 ya lo hacen.

## 14. Reproducción

```bash
.venv/bin/python scripts/e25_06/audit_packages.py --write    # 145 comprobaciones (~15 s)
.venv/bin/python -m pytest -q tests/test_e25_06_auditoria.py  # 21 pruebas (~20 s)
```

## 15. Límites

- Todo es offline: emulación de funciones aisladas con stubs, no del firmware completo ni del arranque
  del MCU (`0x0–0x41ff`, sin binario).
- La lógica del guard, `libupdaterbody.so` y el arranque de Darwin no se re-desensamblaron; para ellos
  se usan las conclusiones vigentes de E24-02/E24-03/E24-04.
- Las claves AES salen de `fwtool` (datos). El control positivo contra el `.dat` de Sony prueba que son
  las correctas.
- Que la cámara acepte el paquete, el efecto físico de B1a y la recuperación solo se pueden medir en
  hardware, y aquí no se ha hecho.
