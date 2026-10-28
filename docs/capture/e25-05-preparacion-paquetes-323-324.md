# E25-05 — Preparación offline de B1a 3.23 y recuperación 3.24 (27-10-2026)

Sesión **100 % offline**: no se conectó la cámara, no se emitió ningún comando USB, no se ejecutó
firmware, no se escribió RAM/NVRAM/NAND y no se flasheó. Base: `f4bb7f50` (E25-04). No se modificó
ningún paquete existente: el 3.22 instalado, el tar tipo 0 y la recuperación 3.23 conservan sus
SHA-256 (comprobado antes y después).

Este informe **corrige el plan de versiones de [E25-04 §3.2](e25-04-recuperabilidad-y-decision.md)** y entrega los dos paquetes pedidos, sus
manifiestos y la verificación binaria. **No cambia la decisión de instalación**: B1a sigue sin ser
instalable (E25-04 G = NO); preparar un paquete no es autorizar un flasheo.

## 0. Resultado en una frase

**El par correcto con 3.22 instalada es prueba 3.23 (tipo 0 + B1a) y recuperación 3.24 (Darwin
oficial), y ambos paquetes están construidos y verificados offline** (69 comprobaciones, 0 fallos);
la recuperación 3.24 reutiliza el contenido ya verificado de la recuperación 3.23 y **solo funciona
si la cámara conserva acceso al actualizador**, por lo que no equivale a una recuperación
independiente del MCU.

## 1. Corrección del plan de versiones

E25-04 reservó el 3.23 ya verificado como **recuperación** y, por tanto, subió la prueba a 3.24 y la
recuperación a 3.25. La instrucción de esta sesión reasigna los números: el 3.23 pasa a ser la
**prueba** y el 3.24 la **recuperación**. El plan corregido es coherente con la única regla medida del
guard —solo acepta versiones **estrictamente mayores** que la instalada— porque `3.22 < 3.23 < 3.24`:

| Paso | Versión | Darwin | Función | Aceptación por el guard |
|---|---|---|---|---|
| 0 | 3.22 (instalada, T024) | tipo 0 | estado de partida | — |
| 1 | **3.23** | tipo 0 + B1a | prueba experimental | 3.23 > 3.22 · INFERENCIA (regla medida con 3.21) |
| 2 | **3.24** | oficial 3.21 | recuperación | 3.24 > 3.23 · INFERENCIA (misma regla) |

Consecuencias que hay que tener presentes:

1. **Hay dos paquetes con versión 3.23**: el antiguo `recuperacion-323` (Darwin oficial) y el nuevo
   `experimental-323` (B1a). Solo uno puede instalarse. Tras instalar la experimental 3.23, el
   `recuperacion-323` es **inútil** (misma versión → rechazado); la recuperación válida es el 3.24.
   El paquete antiguo se conserva intacto como artefacto histórico, no se borra ni se modifica.
2. El 3.24 consume el número de recuperación. Cualquier prueba posterior exigirá **3.25** y su
   recuperación **≥3.26** (tope BCD 3.99). No se debe gastar una versión sin la siguiente preparada.
3. La recuperación 3.24 restaura el **Darwin oficial (3.21)**, no el tipo 0. Volver al tipo 0 exigiría
   otro paquete ≥3.25.
4. La regla del guard con 3.22 instalada sigue siendo **INFERENCIA**: se midió con 3.21 (M2 de E24-04).

## 2. Paquetes preparados

Cada paquete vive en su propio directorio, con su `config`, su `SHA256SUMS` y los dos contenedores
(`.fdat` sin cifrar y `.dat` cifrado que consume el actualizador). Los directorios están bajo
`analysis/darwin-patch/fdat/`, ignorado por git (firmware de Sony); los manifiestos sí se versionan.

| | Experimental 3.23 | Recuperación 3.24 |
|---|---|---|
| Directorio | `analysis/darwin-patch/fdat/experimental-323/` | `analysis/darwin-patch/fdat/recuperacion-324/` |
| Darwin | tipo 0 + B1a (`55a366a5…`) | oficial 3.21 (`5f2be06d…`) |
| `firmware_packed.fdat` | `268621fb70948fc58676bb19bcf82e7d73a2634d0085e3032d64833b04fc6e49` · 212 155 392 B | `24ee9b42e9fae29c7a86ec5f17d85d9a5076a8a36698a3766e0b13801126b2c2` · 212 155 392 B |
| `firmware_packed.dat` | `4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542` · 212 988 056 B | `e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22` · 212 988 056 B |
| `config` | `config-323.yaml` · `1fb2da70…` | `config-324.yaml` · `ce4d286b…` |
| Cabecera FDAT (CRC-32) | `0xcc61c53c` | `0xede492ca` |
| `firmware.tar` interno | `ae6d76ea…` (oficial + 2 ficheros Darwin) | `97024649…` (oficial byte a byte) |
| `updater.img` | `b6d51752…` (oficial) | `b6d51752…` (oficial) |
| Modelo / región | `0x41030035` / 0 | `0x41030035` / 0 |
| Versión de cabecera | 3.23 (`versionMinor 0x23`) | 3.24 (`versionMinor 0x24`) |
| `isAccessory` / modo / LUW | `False` / `U` / `N` | `False` / `U` / `N` |

Contenido:

- **Experimental 3.23** = tar oficial 3.21 con `0640_darwin/darwin_core.bin` sustituido por B1a y
  `0641_darwin_sum/darwin.sum` recalculado. El resto del tar (cabeceras, orden, tamaño, 212 011 520 B)
  es idéntico al oficial; solo cambian esos dos ficheros.
- **Recuperación 3.24** = tar y `updater.img` **extraídos del `.dat` de la recuperación 3.23** tras
  comprobar que son los oficiales (tar `97024649…`, updater `b6d51752…`), reempaquetados con la
  versión 3.24. No se copió el tar desde `firmware/`: se reutilizó el contenido ya verificado del 3.23.

`darwin.sum` del experimental:

```text
0,cf930ac9,0002665c,000001a4,00000000,000003e8,root,root,-1,-1,darwin_core.bin,
```

CRC-32 y tamaño (`0x2665c` = 157 276 B) coinciden con B1a; el formato y el resto de campos son los del
sum oficial. El paquete no incluye `darwin_boo.bin`: `ud_darwin_firmup` reescribe el core siempre
(E24-03).

## 3. Verificación (69 comprobaciones, 0 fallos)

Herramienta: `scripts/e25_05/build_packages.py` (offline). Cada paquete se descifra con
`fwtool.py unpack`, que valida la magia y el CRC de DEND del `.dat`, el CRC-32 de la cabecera FDAT y
la suma de 16 bits + bandera de último bloque de cada bloque cifrado.

| Comprobación | Resultado |
|---|---|
| Hashes de entrada (tar, updater, tipo 0, B1a, recuperación 3.23) | PASS |
| `.fdat` y `.dat` con magia, tamaño y CRC válidos; `unpack` sin errores | PASS |
| El `.fdat` descifrado del `.dat` coincide con el `.fdat` empaquetado | PASS |
| `firmware.tar` y `updater.img` descifrados = hashes esperados | PASS |
| Modelo `0x41030035`, región 0, `isAccessory=False`, modo `U`, LUW `N`, 2 sistemas de ficheros | PASS |
| Versión de cabecera 3.23 / 3.24 (BCD `0x23` / `0x24`) | PASS |
| Descriptores USB del actualizador `(0x54C, 0x3E2)`; `isLens=False` | PASS |
| Core y `darwin.sum` del 3.23 = B1a y suma recalculada | PASS |
| Core y `darwin.sum` del 3.24 = originales (`5f2be06d…`, `9ff7148c`) | PASS |
| Sin `darwin_boo.bin` ni loader en ningún paquete | PASS |
| Paquetes 3.22 y recuperación 3.23 sin modificar (hashes antes/después) | PASS |

Manifiestos (versionados):

- `analysis/e25-05/manifest-experimental-323.json` — 69 checks, 0 fallos, limitaciones y precondiciones.
- `analysis/e25-05/manifest-recuperacion-324.json` — ídem, con `reused_from` y los rangos de diferencia.
- `analysis/e25-05/diferencias-binarias.json` — diferencias byte a byte descritas abajo.
- `SHA256SUMS` dentro de cada directorio de paquete.

## 4. Diferencias binarias

| Comparación | Diferencia | Estado |
|---|---|---|
| **B1a vs tipo 0** | **Exactamente 2 bytes**: offset de fichero `0x1bc6a`/`0x1bc6b` (ROM `0x1fe6a`): `28 46 → 0a e0`; el filtro tipo 0 (`0x20c78..0x20c7f`) queda intacto | VERIFICADO |
| B1a vs original 3.21 | 9 bytes: los 2 de la compuerta + 7 del filtro tipo 0 (uno de los 8 bytes coincide) | VERIFICADO |
| Tar experimental vs oficial | Solo `0640_darwin/darwin_core.bin` y `0641_darwin_sum/darwin.sum` | VERIFICADO |
| Experimental vs recuperación | Solo esos mismos dos ficheros del tar; el resto del payload es idéntico | VERIFICADO |
| Recuperación 3.24 vs 3.23 (`.fdat`) | Cuerpo idéntico; solo `[8,12)` (CRC de cabecera) y `[32,33)` (`versionMinor` `0x23→0x24`) | VERIFICADO |
| Recuperación 3.24 vs 3.23 (`.dat`) | Solo `[140,156)` y `[172,188)` (los dos bloques AES del primer bloque cifrado que contienen CRC y versión) y los últimos 4 B (CRC DEND) | VERIFICADO |

La recuperación 3.24 es, por tanto, el mismo contenido que el 3.23 ya verificado con la versión
subida: no se reintrodujo ni se recalculó ningún dato del firmware.

## 5. Limitaciones del rollback (obligatorio)

1. **La recuperación 3.24 solo funciona si la cámara conserva acceso al actualizador.** La cadena
   conocida exige que `darwin_core` arranque y ejecute `InitCom → Upd` (o que el actualizador sea
   alcanzable por la vía ya documentada); además, `DD_ON1/2/3` deben alimentar el BIONZ (E24-01).
2. **No equivale a una recuperación independiente del MCU.** Si B1a impide que Darwin arranque o que
   alimente el BIONZ, el 3.24 **no se puede instalar**: no hay recuperación USB ni acceso al bootloader
   sin la aplicación demostrados; el único acceso independiente documentado es físico y no verificado
   (`MD0_DWN`, `XDWN_RESET`, UART, SWD, `CN4906` no montado). E25-04: A=NO, B=NO, C=NO, G=NO.
3. **No hay recuperación de un Darwin defectuoso demostrada.** Un paquete íntegro no es una
   recuperación: niveles 1 (paquete correcto) sí; 2 (aceptado por el guard) es inferencia; 3 (Darwin
   ejecutando el actualizador) solo con Darwin sano; 4 (recuperar un core que no arranca) no.
4. **La escritura no es atómica** (212 MB de particiones + hilo de Darwin). Un corte de energía o de
   cable durante el 3.23 o el 3.24 deja el mismo riesgo que ya describía E24-04 (M16/F7/F10).
5. **El 3.24 restaura el Darwin oficial, no el tipo 0.** Volver al tipo 0 exigiría un paquete ≥3.25.
6. **Presupuesto de versiones:** tras el 3.24, la siguiente prueba necesita 3.25 y su recuperación
   ≥3.26; el formato BCD llega a 3.99 y **9.99 cerraría la vía de recuperación**.
7. **La aceptación del guard con 3.22 es INFERENCIA** (regla medida con 3.21); medirla exige conectar
   la cámara, que esta sesión no ha hecho (E24-06/M2).
8. **Nada se ha probado en cámara.** Los paquetes son artefactos locales verificados por software.

## 6. Decisión y estado

- **Paquetes 3.23 (B1a) y 3.24 (recuperación): preparados y verificados offline.** Integridad, CRC,
  modelo, región, versión y diferencias binarias comprobados.
- **B1a sigue sin ser instalable** con las evidencias actuales (E25-04 G = NO): preparar la recuperación
  3.24 no demuestra que recupere un Darwin defectuoso. La autorización requiere decisión expresa del
  usuario y, para cambiar G, la prueba de recuperación en hardware (E25-04 H).
- **No se ha conectado la cámara, no se ha instalado nada y no se ha flasheado.**

## 7. Reproducción

```bash
source .venv/bin/activate
python scripts/e25_05/build_packages.py          # construye y verifica (≈ 85 s)
python -m pytest -q tests/test_e25_05_paquetes.py
python references/fwtool/fwtool.py unpack -f analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat -o /tmp/opencode/exp
python references/fwtool/fwtool.py unpack -f analysis/darwin-patch/fdat/recuperacion-324/firmware_packed.dat -o /tmp/opencode/rec
```

## 8. Límites

- Todo es estático/documental: no se ejecutó firmware ni se midió la cámara.
- Los paquetes dependen de archivos no versionados (`firmware/extracted/fw321/`, la recuperación 3.23
  y B1a); sin ellos el script y las pruebas se detienen o se omiten.
- El manifiesto incluye fecha de generación; lo reproducible son los SHA-256 de los paquetes, no el
  hash del propio manifiesto.
- La recuperación 3.24 no se ha probado; su utilidad real depende del estado de Darwin y del acceso al
  actualizador en el momento del fallo.
