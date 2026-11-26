# 4. Construir los paquetes

**No hay `.dat` publicados:** ni en el árbol de git ni como GitHub Releases. Los paquetes se construyen aquí desde el firmware
oficial 3.21, que es lo que permite comprobar qué contienen.

## Paquetes 3.23 y 3.24 (parche mínimo de Darwin)

```sh
source .venv/bin/activate
python scripts/replicar/generar_nucleos.py        # 1. parchea el darwin_core.bin OFICIAL (tipo 0 y B1a) y comprueba sus SHA-256
python scripts/e25_05/build_packages.py           # 2. construye y verifica los paquetes (≈ 85 s, 69 comprobaciones)
python -m pytest -q tests/test_e25_05_paquetes.py # 3. tests de los paquetes
```

| Archivo | SHA-256 de referencia |
|---|---|
| `analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (3.23) | `4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542` |
| `analysis/darwin-patch/fdat/recuperacion-324/firmware_packed.dat` (3.24) | `e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22` |

Fuente de los hashes: [E25-06](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-06-auditoria-independiente-paquetes.md).
El paso 1 solo cambia bytes de `darwin_core.bin` (2–9 bytes, ver [Cómo funciona](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche));
`build_packages.py` los recompone en el `firmware.tar` oficial, recalcula CRC y suma de Darwin, cifra con `CXD90014` y empaqueta el `.dat`.
Las salidas están ignoradas por git porque derivan de firmware de Sony.

## CFW de la serie 3.93 (una build por función)

Las builds con función nueva se construyen sobre la **base Silent** con un solo script; `--funciones` sirve para aislar un fallo
instalando una función cada vez ([G105](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g105-builds-por-funcion.md)).

```sh
python scripts/gui/build_cfw_film.py build/cfw_func393/pp --version 3.93 --funciones pp
python scripts/gui/build_cfw_film.py build/cfw_func393/base --version 3.93 --funciones ''   # solo Silent
python scripts/gui/build_cfw_film.py build/cfw_func393/film --version 3.93 --pp              # CFW Film completo
python scripts/gui/audit_package_nflasha15.py --darwin-v3 --sin-wbi --bionz-g22 build/cfw_func393/pp
```

- Funciones disponibles en `--funciones`: `base`, `film`, `pp`, `exfine`, `iso` (el script las lista si se le pasa un valor inválido).
- `--iconos` / `--iconos-nativos`: iconos propios para el menú Fn o los de Sony (CAM-394).
- Antes de instalar conviene probar la build en el arnés de la interfaz: `scripts/gui/harness/setup.sh`
  ([G22](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g22-arnes-ui-qemu.md)).
- Los CFW van **sin `nflasha5`** (arranque en frío) y con Darwin v3: es la diferencia que estudia FILM-PB-1
  ([Estado actual](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual)).

## 3.25c (histórico)

```sh
python scripts/e25_27/build.py --out analysis/e25-27/artifacts-325c --package   # ≈ 45 s, determinista
python scripts/e25_27/verify_325c.py                                            # 30 comprobaciones + emulación del cargador
```

SHA-256 esperado del `.dat`: `d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752`. El verificador necesita como control negativo
el paquete 3.25 que bloqueó la cámara y el `bootloader.bin` de los volcados del autor; sin ellos solo se comprueba la evidencia versionada
(`tests/test_e25_27_325c.py`). El 3.25c se instaló como 3.27 ([página 7](https://github.com/nicolvus/a6000-fw-decomp/wiki/7-Volver-atras-y-recuperacion)).

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

El 01-11-2026 se ejecutaron estos pasos desde cero sobre el firmware oficial y los dos `.dat` resultantes tienen **exactamente** los SHA-256
de la tabla, con 69/69 comprobaciones.
