# Extracción y análisis estático

Fuente descargada: https://support.d-imaging.sony.co.jp/download/NEX/AcicwqgUEQ/Update_ILCE6000V321.dmg?fm=am

DMG: 214920547 bytes; SHA-256 `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e`.
DAT: `29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f`, coincide con la referencia publicada; no es una firma de autenticidad independiente. Procedencia HTTPS Sony y cabecera FDAT sustentan la identificación 3.21.

| Partición | Bytes medidos | SHA-256 |
|---|---:|---|
| nflasha15 | 84042977 | e3530a89b8bd24813ab790ec33a429f06e22b4d3b0c5d140fbffbfcd115871f4 |
| nflasha16 | 59013103 | ac344399db69b8c25595a7fb34bd87b39e3c35baf31178e0cd74d8b60d78e35a |
| nflasha3 | 11489040 | 93d4a1f089e306d14a9c48732a0be33427951966db88b30ec48af24a92963765 |
| nflasha5 | 42293120 | fe080cda9f330537f36d7e9e283ecd69e4e8096d974dbdd16d598a8cbdcf3f04 |
| nflasha7 | 3324495 | 58d34dd16ad5d90e126098dd36f6e60eeb11b094f4a97bc89c64370469aaa04f |

Los tamaños reales difieren de las cifras byte-alineadas publicadas en la referencia. No se dispone de NAND para comprobar igualdad; no reutilizar offsets publicados como direcciones de carga.

Inventario del árbol: 1398 archivos; 679 candidatos ELF ARM; firmas: 4 LZPT, 56 ZIP candidatos, 2 gzip candidatos, 657 desconocidos. APK/JAR requieren comprobar contenido ZIP. Responsabilidades desconocidas salvo evidencia adicional; el nombre no determina función.
Inventario total: 3794 entradas, incluidos contenedores y secciones WBI, dos errores de permisos del diario HFS del DMG. `reports/duplicates.json` agrupa SHA-256 iguales.

## WBI: fallo y alternativa

La extracción automática inicial no procesa WBI incrustado. La CLI explícita para nflasha5 falla por `AttributeError: 'NoneType' object has no attribute 'blocks'` al reconocer un fragmento como ext2. Registro: `reports/wbi-unpack.log`. No se reparó ni alteró la fuente externa.

Alternativa ejecutada con el Python existente de PMCA:

```python
import sys
from pathlib import Path
sys.path.insert(0, 'references/fwtool')
from fwtool.sony import wbi
source = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5')
out = Path('firmware/extracted/wbi-sections')
out.mkdir(exist_ok=True)
with source.open('rb') as stream:
    for index, chunk in enumerate(wbi.readWbi(stream)):
        data = chunk.contents.read()
        (out / f'{index:04d}-{chunk.physicalAddr:08x}.bin').write_bytes(data)
```

Recuperadas 1164 secciones, 172998656 bytes. El manifiesto conserva hashes, direcciones físicas/virtuales declaradas y tamaños esperados/reales. No se ha reconstruido un espacio de memoria completo ni validado checksum WBI por un segundo parser. La búsqueda devuelve 71 cadenas en 33 secciones; contiene duplicados del contenido nativo y falsos positivos.

## Herramientas y REA

Linux x86_64; Node 26.10.0, npm 12.2.0, Python 3.14.7; ~68 GiB disponibles al inicio. Presentes: 7z, readelf, objdump, strings, file, debugfs y llvm-objdump. Python PMCA preexistente aporta PyYAML y Cryptodome. Sony-PMCA-RE preexistente en `~/.local/share/Sony-PMCA-RE`; no se ejecutó USB.

Java/JDK, Ghidra, REA, Binwalk, Unblob y JADX no encontrados en PATH. REA fuente 6.5.0 descargado; intento doctor falló por runtime compilado ausente (`reports/rea-doctor.log`). No se instalaron paquetes por instrucción del usuario. No se configuró MCP funcional.

REA documenta Node 26+, Ghidra 12.1.x/JDK compatible (validado upstream con 12.1.4/JDK21), Binwalk 3.1.x, Unblob 26.6.x, `ps` y `prlimit`. Firmware bruto limitado a 128 MiB; DMG y DAT exceden el límite: preparar particiones/ELF primero. Binwalk y Unblob no están incluidos. La admisión nativa no acepta bytes arbitrarios. Decompilación, xrefs y grafos dependen del proveedor disponible.

LLVM se utilizó como análisis parcial porque Ghidra falta y GNU objdump instalado no ofrece ARM. No reemplaza la decompilación solicitada. Los valores de símbolos Thumb tienen bit 0 activo: `0x1080b5` corresponde a instrucciones en `0x1080b4`. El primer intento en ARM decodificó mal Thumb; fue descartado y regenerado con `--triple=thumbv7-linux-gnueabi`.

Fuentes completas y revisiones: `references/` y `reports/source-revisions.json`. Se revisaron docs y tres scripts del proyecto base, README/código pertinente de fwtool, PMCA y Tweak, y guías REA. No se afirma auditoría íntegra de todos los códigos fuente de esos otros proyectos.

## Actualización: REA habilitado por petición posterior

Instalado paquete oficial rea-agents 6.5.0 local con --ignore-scripts --omit=optional; no se compiló el checkout. Se descargaron Ghidra 12.1.4 y Temurin JDK 21 de sus releases oficiales, verificando SHA-256 contra metadatos del distribuidor. `scripts/rea` define sus rutas. `rea doctor --client codex --provider ghidra` pasa, y `rea analyze` procesa libcamera.so como ELF ARM. Registros en reports/rea-*.json. La CLI fuente fallida se conserva como evidencia histórica; no describe la instalación actual. MCP para Codex registrado con respaldo; falta reiniciar el cliente para descubrirlo en su sesión.
