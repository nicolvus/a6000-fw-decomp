# E25-27 — Construcción offline del firmware integrado EFCS / Electronic

> **Actualización E26:** el usuario informa que este 3.25 fue instalado y la cámara dejó de arrancar. El resultado offline no demuestra arranque ni seguridad. Ver [investigación de recuperación](e26-recovery.md).


29-10-2026. Construcción reproducible sobre los originales de Sony 3.21. Sin cámara,
sin instalación, sin RAM/NVRAM/MMIO y sin firmware ejecutado. El resultado es un
candidato **experimental** identificado como **CONSTRUIDO OFFLINE — INSTALACIÓN NO
AUTORIZADA**.

Este informe documenta solo la construcción: qué se integró, qué se verificó, qué
falló y qué falta antes de instalar. La investigación previa está en
[E25-24b](e25-24b-implementacion-selector.md), [E25-25](e25-25-validacion-carga-caves.md)
y [E25-26](e25-26-c3b-exposicion-electronica.md).

---

## 1. Entradas verificadas

| Entrada | SHA-256 | Tamaño | Comprobación |
|---|---|---|---|
| `firmware.tar` 3.21 | `970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8` | 212 011 520 B | identidad exigida por el constructor |
| `updater.img` | `b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c` | 4 079 616 B | identidad exigida |
| `av-cam.bin` (FAT de `nflasha3`) | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` | 11 427 236 B | extraído del FAT y verificado |
| `darwin_core.bin` | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` | 157 276 B | miembro del tar |

El constructor **rechaza** cualquier otra imagen, cualquier `av-cam.bin` ya parcheado
y cualquier Darwin tipo 0/B1a. No usa la versión declarada como sustituto de la
identidad binaria.

## 2. Qué se construyó

| Componente | Cambio | Bytes |
|---|---|---|
| Selector BIONZ | `0x4384133e`/`0x43841342`/`0x43841476` + cueva `0x43541800` | 20 B de cueva; rama y store originales neutralizados |
| C3-B | `bl` de `0x438c82fe` + cueva `0x43541840` | 58 B |
| Darwin | `0x20c78` y `0x1fe6c` → cueva `0x4318`; literal `0x4330` | 14 B de cueva + 4 B de literal |
| `nflasha3` | 3 bloques TPZL recompuestos (0, 48, 57) | +83 440 B |
| `part_image.sum` | CRC-32 y tamaño de `dev/nflasha3` | `f5e75c34` / `0x00b09500` |
| `darwin.sum` | CRC-32 del core integrado | `d55a54b5` / `0x0002665c` |
| `firmware.tar` | 4 miembros sustituidos, resto byte a byte | 212 094 976 B |

La disposición de cuevas es la validada en E25-25:

```text
0x43541800  selector (20 B)  -> 0x43541814
0x43541840  C3-B     (58 B)  -> 0x4354187a
0x435418d8  cola de metadatos de la cabecera LIRO (protegida)
```

No hay solapamiento, no se toca `0x43541900` (objeto de 512 B con GOT) y las
regiones protegidas de BIONZ y Darwin conservan su SHA-256.

### Semántica

```text
EFCS ON  (+0x210 = 0) -> cap+0x41c = 0 -> pkt[0x0e] = 0
    -> Darwin: 0x20c74/0x1fe66 ejecutan 0x1b080 (bobinas y motor originales)
    -> C3-B: no actúa; SetExposure conserva shd/svd/ShutMode de Sony

EFCS OFF (+0x210 = 1) -> cap+0x41c = 1 -> pkt[0x0e] = 1
    -> Darwin: ambas compuertas devuelven 0 (sin P4D/P4E ni rearme)
    -> C3-B: solo paso 0, svd <= 1, VTS != 0, shd > VTS
       shd' = shd - VTS; svd' = 0; ShutMode = 0
```

P4B/P4C no se bloquean. La operación 5 conserva su apagado original. No se toca
`InitCom`, `Upd`, reset, watchdog, GPIO ni las tablas de vectores usadas.

## 3. Construcción del contenedor

`nflasha3` es un TPZL (LZPT) que descomprime a una imagen FAT12 de 24 182 784 B;
`av-cam.bin` ocupa la cadena de clústeres que empieza en el 3 (offset absoluto
`0x9600`). El constructor:

1. localiza y verifica `AV-CAM.BIN` en la FAT;
2. sobrescribe en sitio los bytes parcheados (misma cadena y tamaño);
3. recompone **solo** los bloques TPZL 0, 48 y 57 con un segmento de literales
   válido y determinista, alineado a 256 B;
4. actualiza CRC-32 y tamaño en `part_image.sum`;
5. reescribe las cabeceras de los cuatro miembros del tar conservando orden,
   modos, mtime y el resto de bytes;
6. empaqueta FDAT/DAT con `fwtool` (AES-ECB doble CXD90014) y verifica la
   extracción inversa.

No se firma nada: el `av-cam.bin` no tiene firma interna demostrada y el guard del
actualizador es CRC + modelo + región + versión. **El guard no se ha ejercitado con
este contenedor.**

## 4. Resultados de la construcción

| Artefacto | SHA-256 | Tamaño |
|---|---|---|
| `av-cam.integrated.bin` | `45a5ab350c356d6d76f5ee79ed51d98fadf920f64ce75c387f6358f11225190e` | 11 427 236 B |
| `darwin_core.integrated.bin` | `9771c0508ee17e7984a619479c1f69cc4e8b71f0091fb5f9dfde66bbd19fb177` | 157 276 B |
| `nflasha3.integrated.bin` | `bb9ce25a073d1ccc990d8ee1fdd75322c703d5d2a4020ab5e7daeaf8d23d546c` | 11 572 480 B |
| `firmware.integrated.tar` | `440b70b1b1afaed2a80e03679728b26917336cc2aed30052e7906d638a6d52e1` | 212 094 976 B |
| `firmware_packed.fdat` | `87145e1b06c01564dbebbb40d98acb084aa8ff8d044e6bf93e8cf79cae1a8d9f` | 212 238 848 B |
| `firmware_packed.dat` | `42c02504f42d2126c362e2bc1023c0285276a97dcfb67ca544bb3934739f7cae` | 213 072 024 B |

Cabecera FDAT: `UDTRFIRM`, formato `0100`, versión `3.25`, modelo `0x41030035`,
región 0, modo `U`, LUW `N`, 2 sistemas de ficheros, CRC `0x6facbbf7` (almacenado =
calculado). DAT: DEND `fae7ef16` (almacenado = calculado) y descriptor de
actualizador `[0x54c, 0x3e2]`.

### Auditoría independiente (parsers propios de E25-06)

| Comprobación | Resultado |
|---|---|
| Bloques descifrados | 208 078 |
| Sumas de bloque / bandera de último / longitudes | 0 errores, 0 errores, 0 errores |
| Texto plano vs `.fdat` | idéntico (212 238 848 B) |
| CRC de cabecera FDAT | `6facbbf7` = `6facbbf7` |
| DEND | `fae7ef16` = `fae7ef16` |
| Miembros del tar | 105, `problems = []` |
| `part_image.sum` | verifica CRC-32 y tamaño |

La extracción inversa recupera exactamente el tar construido, el `av-cam.bin`
integrado, el Darwin integrado y el `part_image.sum` previsto.

## 5. Emulación integrada

Cadena ejecutada: selector BIONZ real → `pkt[0x0e]` → compuertas Darwin reales →
`StartExposure` real (C3-B) → argumentos de `SetExposure`. El IMX210 no se modela.

| Caso | EFCS | Electronic |
|---|---|---|
| `pkt[0x0e]` | 0 | 1 |
| Bobinas (Darwin) | 3 (original) | 0 |
| Motor (Darwin) | 4 (original) | 0 |
| `shd` en SetExposure (1/4000) | 8422 | 4203 |
| `svd` | 1 | 0 |
| `ShutMode` | 3 | 0 |
| ¿Idéntico al original? | sí (ramas `r1=0` y `r1=1`) | normalizado |

Alternancia `EFCS → Electronic → EFCS → Electronic → EFCS`: los cinco paquetes
quedan congelados con su modalidad; un cambio de selector durante la captura se
rechaza y no altera el paquete ya emitido.

Errores: VTS 0, `shd <= VTS` y ruta larga (`svd=2`) no se tocan; modalidad distinta
de 0/1 se rechaza con `InvalidSelection`.

### Matriz de velocidades (Electronic)

| Velocidad | Tv | VTS | Período Q8 | `shd` nativo | `shd` C3-B | `svd` | `ShutMode` | `r5` | Estado |
|---|---|---|---|---|---|---|---|---|---|
| 1/8000 | 7415 | 4219 | 3891 | 8430 | 4211 | 0 | 0 | 4211 | VERIFICADO OFFLINE |
| 1/4000 | 7159 | 4219 | 3891 | 8422 | 4203 | 0 | 0 | 4203 | VERIFICADO OFFLINE |
| 1/1000 | 6647 | 4219 | 3891 | 8373 | 4154 | 0 | 0 | 4154 | VERIFICADO OFFLINE |
| 1/250 | 6135 | 4219 | 3891 | 8175 | 3956 | 0 | 0 | 3956 | VERIFICADO OFFLINE |
| 1/125 | 5879 | 4219 | 3891 | 7912 | 3693 | 0 | 0 | 3693 | VERIFICADO OFFLINE |
| 1/60 | 5608 | 4219 | 3891 | 7341 | 3122 | 0 | 0 | 3122 | VERIFICADO OFFLINE |
| 1/30 | 5352 | 4219 | 3891 | 6244 | 2025 | 0 | 0 | 2025 | VERIFICADO OFFLINE |
| ≥ 1/15 | — | — | — | — | no actúa | — | 3 | — | RUTA LARGA NO VALIDADA |

`r5 = VTS − líneas` es el valor nativo; la emulación no mide exposición física.
La ruta de 30 s sigue fuera del alcance.

## 6. `cap+0x73b` (E25-28)

Barrido lineal de la imagen original (8 instrucciones):

| Dirección | Tipo | Instrucción |
|---|---|---|
| `0x438acbfc` | escritura | copia `cap+0x12e` a `plan+0x73b` |
| `0x43b1e556` | escritura | 0 (r5) |
| `0x43b1e55e` | escritura | 1 / 0 según el cálculo |
| `0x438c8b4e` | lectura | dispara `0x43aff79a(2,1)` si ≠ 0 |
| `0x43b1e448` | lectura | |
| `0x43b1e474` | lectura | |
| `0x43b1e7b6` | lectura | |
| `0x4394efd0` | `movw r3,#0x73b` | construcción de un id, no acceso |

`0x43b1e520` decide el valor con `cap+0x73a`, `cap+0x655` (ShutMode), el retorno de
`0x43ad90c2` (`0xffff`) y `cap+0x12f8`; no es simplemente una copia del ShutMode.
C3-B no lo modifica. **No hay una corrección verificada** que aplicar sin alterar la
condición de Sony; se conserva el valor nativo y el límite queda documentado. La
parte de vídeo/Live View sigue abierta en E25-28.

## 7. Reversión

- BIONZ: `PC.restore_bytes` → `PB.restore_bytes` → SHA-256 `b60c845c…e56bb9`.
- Darwin: `PD.restore_bytes` → SHA-256 `5f2be06d…0bf4`.
- El tar original no se modifica: se conserva como entrada verificada.
- `build.py --restore` escribe `av-cam.restored.bin` y `darwin_core.restored.bin` y
  comprueba ambos SHA-256; `restore.verified = true`.

La reversión binaria es necesaria pero **no** es recuperación de una cámara
bloqueada. E24-04 sigue vigente: no hay recuperación independiente de Darwin
demostrada.

## 8. Seguridad y límites

| Aspecto | Estado |
|---|---|
| Identidad de las entradas | VERIFICADO OFFLINE |
| Parches y cuevas | VERIFICADO OFFLINE |
| Reversión de los binarios | VERIFICADO OFFLINE |
| Estructura del contenedor | VERIFICADO OFFLINE |
| Extracción inversa | VERIFICADO OFFLINE |
| Aceptación por el guard del actualizador | PENDIENTE (no ejercitado) |
| Arranque de BIONZ con las cuevas | PENDIENTE / NO EVALUABLE sin cámara |
| Recuperación de un Darwin que no arranque | BLOQUEADO POR DEPENDENCIA DEMOSTRADA (E24-04) |
| Exposición electrónica real / uniformidad | PENDIENTE (E25-27 físico) |
| Vídeo / Live View | NO EVALUABLE con la evidencia actual (E25-28) |

No se declara el firmware seguro para instalar.

## 9. Reproducción

```bash
.venv/bin/python scripts/e25_27/build.py --package
.venv/bin/python scripts/e25_27/build_evidence.py
.venv/bin/python -m pytest tests/test_e25_27_build.py -q
```

Los artefactos quedan en `analysis/e25-27/artifacts/` (ignorado por Git: deriva de
firmware de Sony). La evidencia versionable es `analysis/e25-27/evidence.json`.
El constructor es determinista: dos ejecuciones producen los mismos SHA-256.

## 10. Criterios de finalización

| Criterio | Resultado | Evidencia |
|---|---|---|
| BIONZ integrado | VERIFICADO OFFLINE | `45a5ab35…`, diff 111 B, regiones protegidas intactas |
| Darwin integrado | VERIFICADO OFFLINE | `9771c050…`, compuertas y literal |
| Selector EFCS / Electronic | VERIFICADO OFFLINE | `+0x210` 0/1, paquete congelado por captura |
| Bloqueo de bobinas | VERIFICADO OFFLINE (emulación) | Darwin 3 → 0 |
| Bloqueo de rearme | VERIFICADO OFFLINE (emulación) | Darwin 4 → 0; L0 documentado en E25-02 |
| Recuperación de EFCS | VERIFICADO OFFLINE (emulación) | idéntico al original en ambas ramas |
| C3-B integrado | VERIFICADO OFFLINE (emulación) | 4203/0/0; 7 velocidades |
| Compatibilidad de cuevas | VERIFICADO OFFLINE | sin solapamiento; `0x4354187a < 0x435418d8` |
| Reversión exacta | VERIFICADO OFFLINE | SHA-256 originales |
| Emulación integrada | VERIFICADO OFFLINE | `all_ok = true` |
| Tests | VERIFICADO OFFLINE | 16 nuevos + 182 de regresión dirigida |
| Construcción de contenedor | VERIFICADO OFFLINE (estructura/roundtrip) | 208 078 bloques, DEND y CRC |
| Extracción inversa | VERIFICADO OFFLINE | tar, av-cam, Darwin y sum exactos |
| Seguridad de arranque | PENDIENTE / NO EVALUABLE | sin cámara |
| Recuperabilidad física | BLOQUEADO POR DEPENDENCIA DEMOSTRADA | E24-04 |
| Instalación en cámara | NO REALIZADA | prohibida en esta fase |

**Clasificación global: CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA.**
