# Evaluación comparativa de 8 herramientas (19-10-2026)

Alcance: análisis estático de firmware A6000 3.21 ya extraído en `firmware/`; nada se ejecutó en cámara ni se modificó firmware.
Registro crudo: `results/results.jsonl` + `results/<prueba>.log`. Cronometraje: `rt.py`. Material de laboratorio: `lab/`.
Host: CachyOS, Python 3.14.7, JDK 21.0.12.1. Todas las muestras se leyeron solo en lectura.

## Resumen

| Herramienta | Versión | ¿Funcionó? | Tiempo | Utilidad para entender la captura |
|---|---|---|---|---|
| Ghidra | 12.1.4 | Sí | 5–6 s (copia de proyecto, `-noanalysis`) | **Alta**: única que reproduce el hallazgo S46/S47 (decompilación) |
| REA | 6.5.0 | Sí, vía Ghidra | 20 s por consulta | Media: mismo motor, salida estructurada y verificable, muy verbosa |
| angr | 10.0.4.post1 | Sí | 12.6 s | Baja–media: CFG rápido, pero sin base correcta ni símbolos |
| Binwalk | 3.1.0 (cargo) | Sí | <0,4 s | Media en triaje de contenedores; nula en `av-cam.bin` |
| Kaitai Struct | 0.11 | Sí (compila y parsea) | 0,5 s | Baja hasta conocer el formato; sirve para documentarlo |
| ImHex | 1.38.1 (AppImage) | Sí, solo CLI de patrones | 0,3 s | Baja–media: útil para inspección manual (GUI no probada) |
| Frida | 17.24.3 | Sí, solo programa propio | 2,3 s | Nula sobre el firmware (esperado); valida la metodología |
| JADX | 1.5.6 | Sí | 52 s (F-Droid), 1,9 s (APK Sony) | Baja: el firmware no es Android en el núcleo de captura |

## Evidencia por herramienta

**Ghidra** (`ghidra-persist-copy-*`). Se copió `silent-liro.{gpr,rep}` (329 MB) al scratchpad y se abrió con `-process av-cam.bin -noanalysis -readOnly`: ARM:LE:32:v7, 37 700 funciones. Decompiló `0x437dad78` y `0x43789cc0`; el primero escribe `param_2+0x94 = (u16!=0)` y `+0x95 = low8(segundo u16)`, coincidiendo con lo anotado en `CONTEXT.md` (S46: «escribe C=`0x43e9d3b4`+94/+95»). Segunda prueba con proyecto temporal (`-import … -readOnly -deleteProject`) sobre `a6000-darwin-rom-analysis-view.elf`: 1100 funciones. Límite: dirección base 0x10000 al importar el ELF, no 0x4200 (ya advertido en `docs/STATE.md`).

**REA**. Sin `GHIDRA_INSTALL_DIR` falla (`provider_unavailable`, rc=1). Con él y el JDK local: `analyze` (20 s), `search --kind procedures` y `function 0x144b0 --format json` (236 KB con pseudocódigo, callers y callees). Import `ephemeral-source-immutable`, proyecto en `/tmp/rea-ghidra-*`. Límites: no hay GUI de proyectos, cada consulta relanza Ghidra (~20 s), la salida no admite `--token-limit` con JSON, y direcciones fuera del mapeo se rechazan.

**angr** (`angr-cfg-elf`). CFGFast sobre el mismo ELF: 2843 funciones frente a 1100 de Ghidra (sobredetección heurística); carga en 0x400000 en lugar de la base real. Sin `unicorn` (aviso, irrelevante para CFG estático). No se probó sobre `av-cam.bin` (blob sin cabecera: exige base y arquitectura manuales).

**Binwalk** (`binwalk-*`). `vmlinux.bin`: Linux 3.0.27_nl-rt106 (Sony CE Linux, 24-01-2019) + CPIO; `initrd.img`: ext; `nflasha3_unpacked`: FAT12/16 de 24 MB; `firmware.fdat`: CramFS en 0x200 (143 360 B) y tar en 0x23200 (105 ficheros). `av-cam.bin` (11 MB): **ninguna firma**, es el binario que importa para la captura. Nota: `-q` suprime la salida.

**Kaitai** (`kaitai-compile`). Se compiló `lab/fdat_probe.ksy` y se parseó la cabecera real: `magic=b'UDTRFIRM'`, 56 B restantes. Solo prueba la cadena de herramientas; el esquema útil requiere conocer el formato primero.

**ImHex** (`imhex-pl`, con `-v`). Tras instalar `glfw`/`mbedtls` el paquete Arch no sirvió (pide mbedtls 3.x, el sistema trae 4.x); el AppImage sí. `lab/hdr.hexpat` → `magic=UDTRFIRM ver=0100 f0=0x55 f1=0x4e`. Sin `-v` no imprime nada (rc=0). La GUI no se abrió.

**Frida** (`frida-spawn-hook`). Solo sobre `lab/shutter_lab` (programa propio): intercepta `capture` y `expose`, devolviendo `expose(4000, 200) -> 8000`, etc. No aplicable a firmware Sony (no se ejecuta ni emula).

**JADX**. APK F-Droid (12,6 MB, SHA-256 `19d51fad…3b52`): 11 950 ficheros .java, 147 errores de decompilación (rc=3, normal). APK de firmware `ScalarAUsbDlApp.apk`: solo `R.java` y manifiesto (`com.sony.scalar.dlsys…`), porque el código está en `.odex` que JADX no lee; esto es análisis estático local, no del flujo de captura.

## Integridad de Ghidra
`sha256sum -c` sobre los 1328 ficheros de `analysis/ghidra/` (baseline previo): 0 diferencias, 0 ficheros nuevos. Nunca se abrió `analysis/ghidra` directamente; se usó una copia o proyectos temporales.

## Conclusión
Para entender la coordinación de captura: **Ghidra primero** (decompilación y xrefs, ya con proyectos útiles); **REA** como capa de evidencia reproducible sobre Ghidra; **Binwalk** solo para triaje inicial; ImHex/Kaitai para documentar formatos tras entenderlos. angr, Frida y JADX no aportan aquí, salvo angr como segunda opinión de CFG si se fija la base.

## Limitaciones
- Instalación sin root en el scratchpad (efímero): `pip install angr frida frida-tools kaitaistruct` en venv, `cargo install binwalk`, zips de JADX/Kaitai y AppImage de ImHex. Binwalk/JADX existen en repos oficiales de Arch pero `sudo` no era automatizable.
- Una sola muestra para angr/REA; tiempos de una ejecución, sin repetir.
- Los datos de función de REA y los hallazgos de Ghidra no se contrastaron con hardware.
- Sin hallazgo nuevo sobre el obturador; solo reproducción de S46.
