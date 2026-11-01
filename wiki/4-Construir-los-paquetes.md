# 4. Construir los paquetes 3.23 y 3.24

Dos opciones: usar los `.dat` ya construidos del [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
o construirlos tú (así compruebas qué contienen). Ambos caminos se verifican con los mismos hashes.

## Hashes esperados

| Archivo | SHA-256 |
|---|---|
| `a6000-custom-fw-3.23-b1a-silent-shutter.dat` | `4c21353d…ccf474542` (completo en el release) |
| `a6000-custom-fw-3.24-recovery-stock-darwin.dat` | `e1345aff…8f22` (completo en el release) |

```sh
sha256sum -c SHA256SUMS.txt   # en la carpeta con los .dat y el SHA256SUMS.txt del release
```

## Construir desde el firmware oficial

```sh
source .venv/bin/activate
python scripts/replicar/generar_nucleos.py        # 1. parchea el darwin_core.bin OFICIAL (tipo 0 y B1a) y comprueba sus SHA-256
python scripts/e25_05/build_packages.py           # 2. construye y verifica los paquetes (≈ 85 s, 69 comprobaciones)
python -m pytest -q tests/test_e25_05_paquetes.py # 3. tests de los paquetes
```

Salidas (ignoradas por git, derivan de firmware de Sony):
`analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (3.23) y `analysis/darwin-patch/fdat/recuperacion-324/firmware_packed.dat` (3.24).

El paso 1 solo cambia bytes de `darwin_core.bin` (2–9 bytes, ver [Cómo funciona](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche)); `build_packages.py` los recompone en el `firmware.tar`
oficial, recalcula CRC y suma de Darwin, cifra con `CXD90014` y empaqueta el `.dat`.

## Construir el 3.25c (experimental)

```sh
python scripts/e25_27/build.py --out analysis/e25-27/artifacts-325c --package   # ≈ 45 s, determinista
python scripts/e25_27/verify_325c.py                                              # 30 comprobaciones + emulación del cargador
```

SHA-256 esperado del `.dat`: `d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752`. El verificador necesita como control negativo
el paquete 3.25 que bloqueó la cámara y el `bootloader.bin` de los volcados del autor; sin ellos solo se comprueba la evidencia versionada
(`tests/test_e25_27_325c.py`).

## Inspeccionar lo construido

```sh
python references/fwtool/fwtool.py unpack -f analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat -o /tmp/exp323
```

## Medir el guard sin flashear

Con la cámara en modo MTP/almacenamiento masivo (no cambia nada en ella):

```sh
python scripts/fdat_guard_probe.py        # debe rechazar la versión instalada y aceptar 3.23 y 3.24
```

## Reproducibilidad comprobada

El 01-11-2026 se ejecutaron estos pasos desde cero sobre el firmware oficial y los dos `.dat` resultantes tienen **exactamente** los SHA-256 del release
(`4c21353d…` y `e1345aff…`), con 69/69 comprobaciones.
