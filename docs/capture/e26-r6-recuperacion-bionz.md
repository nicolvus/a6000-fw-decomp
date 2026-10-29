# E26-RECOVERY R6 — BLDR, BIONZ y recuperación conservando la placa

Fecha: 29-10-2026. Continúa `946dd198` y [R5](e26-r5-loader3-servicio.md). Solo análisis de archivos y fuentes públicas, estas últimas autorizadas expresamente durante R6. Sin conectar, encender, depurar ni modificar la cámara. No se genera firmware ni imagen para escritura.

## 1. BLDR: implementación recuperada y alcance real

**VERIFICADO OFFLINE:** el payload `CXD90014.dat`, su cabecera ILCE-6000, `usbshell.cpp` y el backend Python locales coinciden byte a byte con upstream. El último cambio del payload corresponde a Sony-PMCA-RE `0ce3c7e8fed88bcd855a80a75eadc518c2e324cb`, cuyo gitlink de plataforma es `85bcb5454bc68a971b674d3b9e93eeedbf35cf3c`. No se está suponiendo equivalencia con una implementación moderna: se extrajo el ELF del FDAT **local**, SHA-256 `dff9ccc0306cd52f7552ea1dee5610aa224e635875222a875bcab5f074f4cdf4`, y se cotejó con código e instrucciones. El registro de adquisición no conserva hash del payload enviado: su uso exacto es una **INFERENCIA RESPALDADA** por `updater_info_dump.py` y su importación de ese checkout, no una atestación de la transferencia histórica.

Fuentes públicas fijadas: [bootloader.cpp](https://github.com/ma1co/OpenMemories-Platform/blob/85bcb5454bc68a971b674d3b9e93eeedbf35cf3c/api/bootloader.cpp), [nand_ioc.c](https://github.com/ma1co/OpenMemories-Platform/blob/85bcb5454bc68a971b674d3b9e93eeedbf35cf3c/drivers/nand_ioc.c), [usbshell.cpp](https://github.com/ma1co/Sony-PMCA-RE/blob/0ce3c7e8fed88bcd855a80a75eadc518c2e324cb/updatershell/usbshell.cpp). `nand_ioc.c` no cambia desde `46df2adb` (2017); API C++ desde `8f7b8503` (2017), ampliada para BootROM en `1808df88` (2018). Identidades reproducibles: [r6-provenance.json](../../analysis/e26-recovery/r6-provenance.json).

### Enumeración, lecturas y pérdidas

| Operación | Evidencia en ELF PMCA (direcciones REA, sesgo ELF +0x10000) | Resultado y límite |
|---|---|---|
| Enumerar | `0x1230c`, reserva `0x50`, registros de 16 B | Un bloque safe y cuatro normales, en ese orden; sin ordenar por dirección |
| Geometría | `0x12970`, ioctl `0x6e09` | Usa block_size/page_size recibidos; no registra su respuesta en el archivo |
| Identificadores | `0x12998`/`0x129bc`, ioctls `0x6e0b`/`0x6e0c` | Identificadores de bloque devueltos por controlador, no índices USB ni direcciones de archivo |
| Safe | `0x129e4`, ioctl `0x6e02` | Páginas de `0x600` B; entrega log2(páginas/bloque) a PNAND |
| Normal | `0x12a20`, ioctl `0x6e05` | **die=0 y plane=0 constantes**, block del listado, page=0, bloque completo |
| Metadatos | `0x12070`, buffer auxiliar 8 B/página | El controlador los devuelve; el payload los descarta. No conserva OOB/ECC crudo |
| Errores | `0x12070` y `usbshell.cpp:130–138` | Cualquier retorno no cero lanza excepción; catch deja vector vacío y transmite longitud cero |
| Contenedor | `0x12c28`, comando `0x52444c42` | Informa cinco tramas; cada transferencia conserva frontera temporal, no block ID. Python recibe bytes; `b''.join` elimina longitudes y tramas vacías |

**VERIFICADO EN BINARIO, segundo artefacto:** `nand.ko` SHA `2169b84d…` entrega los IDs de `dev+0x58` (safe) y `+0x5c/+0x60/+0x64/+0x68` (normal), `0x28878`/`0x28928`. `muminblk_init` `0x10660` los toma de una tabla heredada en `0xc0000c00`, buscando un terminador de 16 bits cero. El respaldo no conserva esa tabla ni los IDs. No se inventan valores 2/3/4/5 para todos los bloques.

**Hallazgo nuevo sobre ECC:** `nand_ioc_pread_normal` `0x2832c` convierte `-0x20006` en retorno ioctl cero, pero escribe **1** en el campo de estado. La envoltura PMCA retorna ese 1 y lo trata como error, descartando el buffer. Loader2 `0xc00306ce` acepta `-0x20006` si completó las páginas pedidas. Por tanto una omisión BLDR puede deberse a una lectura con advertencia tolerada por Loader2; **no demuestra bloque ilegible ni NAND dañada**. No se conoce qué estado ocurrió en 2026-10-20.

### Mapa reproducible, con incertidumbre explícita

Original intacto: `bootloader.bin`, 491520 B, SHA-256 `eb420385120f2cd7c9b071f67ce5808721b7de44fb78e2884a856e3c438a327f`.

| Intervalo del archivo (fin exclusivo) | Interpretación | Integridad y origen físico |
|---|---|---|
| `0–0x18000` | EXBL, páginas safe de 1536 B; contiene Loader2 en `0x600–0x7200` | Bytes conservados, geometría de 64 páginas compatible; ID safe no registrado |
| `0x18000–0x38000` | INFO; BossFirm, LdrBkup, DGU, MIS y primeras 43 páginas Loader3 | INFO pide die0/plane0/block2; identificación respaldada por contenido, sin encabezado BLDR físico |
| `0x38000–0x58000` | Segundo bloque normal superviviente bajo esa geometría | ID y posición entre las cuatro solicitudes desconocidos |
| `0x58000–0x78000` | Tercer bloque normal superviviente | ID y posición desconocidos |
| Una trama normal vacía | Longitud total compatible con safe64×1536 + **3**, no 4, bloques64×2048 | **INFERENCIA RESPALDADA**, condicionada a geometría/adquisición; no se sabe ordinal, ID ni error |
| INFO 5: `(0,0,2,21,43)` | Prefijo situado en `0x22800–0x38000` | Runtime `0xc01f0000–0xc0205800`; ubicación física inferida |
| INFO 6: `(0,1,2,0,21)` | Cola necesaria de 43008 B | Runtime `0xc0205800–0xc0210000`; **no hay solicitud explícita plane1 en BLDR** ni correspondencia demostrada con bytes del archivo |

El mapa lógico de adquisición está reconstruido; **el mapa físico completo no**. No es una NAND contigua: mezcla safe/normal, omite bloques y metadatos y pierde la identidad de tramas. No se puede usar `offset_archivo / tamaño_bloque` como dirección NAND. Tampoco se prueba que ningún byte de la cola exista en otro respaldo: lo que falta es una adquisición identificada de esas coordenadas o una copia independiente íntegra y compatible.

Reproducir sin mutar el respaldo:

```sh
.venv/bin/python -m scripts.e26_recovery.inspect_bldr analysis/camera-dumps/updater-20261020-175427/bootloader.bin
.venv/bin/python -m pytest tests/test_e26_bldr.py tests/test_e26_loader3.py -q
```

Salida publicada sin firmware: [r6-bldr-map.json](../../analysis/e26-recovery/r6-bldr-map.json). REA con pseudocódigo e instrucciones: [payload BLDR](../../analysis/e26-recovery/r6-bldr-rea.json), [controlador y Loader2](../../analysis/e26-recovery/r6-nand-loader2-rea.json). La regresión exige conservar como desconocida la trama perdida y no asignar la cola a `0x38000` automáticamente. Tres pruebas, ruff y mypy aprobados en esta fase.

## 2. Checkpoint de reconstrucción

**NO DEMOSTRADO:** Loader3 íntegro. El recorte R5 suma `0x05c12355`, INFO registra `0xeda2f689`; suma32 sigue siendo una comparación, no algoritmo certificado. BossFirm y DGU coinciden; LdrBkup y MIS difieren también (estos pueden contener datos modificados). Loader2 `0xc0030d80` comprueba firma INFO, `0xc0030de8` concatena la cadena, y `0xc00306ce` comprueba resultado/páginas. Estas rutinas no comparan el checksum INFO; no se atribuye a Loader2 una comprobación no encontrada.

**Corrección identificable de R5:** su siguiente paso «recuperar implementación BLDR» está resuelto para el payload local. La cola contigua no queda reparada por ese hallazgo: falta establecer contenido de die0/plane1/block2/páginas0–20, más la identidad de las tramas perdidas. No interpretar la cola incoherente ni producir una imagen destinada a escritura.

Próximo paso de esta sesión: delimitar qué funciones verificadas del prefijo siguen respaldando UPDATER y preparar mapa visual documental de CN4906; no sustituir páginas con otro modelo ni fabricar un runtime íntegro.
