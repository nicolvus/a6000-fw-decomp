# E26-RECOVERY R6 — BLDR, BIONZ y recuperación conservando la placa

Fecha: 29-10-2026. Continúa `c17bd856` y [R5](e26-r5-loader3-servicio.md). Solo análisis de archivos y fuentes públicas, estas últimas autorizadas expresamente durante R6. Sin conectar, encender, depurar ni modificar la cámara. No se genera firmware ni imagen para escritura.

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

## 3. Loader3 y UPDATER: resultado de las fases 2/3

**VERIFICADO OFFLINE / EN BINARIO:** se aisló exclusivamente el prefijo de 88064 B, SHA `bda777a220447fc6f67d1d4f52c38a491043b1efcff570fdfc78969c47c2d8e5`, sin completar ni rellenar la cola. Es idéntico a las primeras 43 páginas del candidato R5. REA reconoce de nuevo `0xc01f159a`, `0xc01f1de6`, `0xc01f1312`, `0xc01f1378` y `0xc01f068a`; sus instrucciones y literales permanecen dentro del prefijo. Esto confirma esas **rutinas estáticas**, no un Loader3 completo ni ejecutable. Evidencia: [REA prefijo/UART](../../analysis/e26-recovery/r6-prefix-uart-rea.json), [Capstone y literales independientes](../../analysis/e26-recovery/r6-prefix-bytechecks.json).

La reconstrucción completa queda bloqueada exactamente por INFO6: `(die0,plane1,block2,pages0–20)`, runtime `0xc0205800–0xc0210000`. Allí caen `0xc020e090`, `0xc020e024`, formateadores/divisores y tabla de inicialización esperada `0xc020fd5c–0xc020fd7c`. No se corrigieron esas referencias, no se verificaron sus cuerpos y no se sustituyeron por páginas de otra cámara. No se encontró otra copia de Loader3 entre los respaldos y archivos de bootloader identificados. Los dos respaldos históricos de RAM consultados en offset `0xc00` no identifican la tabla de bloques: no se presupone que sus direcciones físicas equivalgan a la virtual kernel `0xc0000c00`.

| Pregunta de ruta UPDATER | Resultado y clasificación |
|---|---|
| ¿Se conserva el selector? | **VERIFICADO EN BINARIO:** el prefijo sin cambios comprueba existencia de `\\updater\\mode`, dispositivo2; prioridad modo3. La imagen completa correcta sigue ausente |
| ¿Qué necesita antes? | **VERIFICADO EN BINARIO, R5:** Sync, energía, UDIF, BOSS, DDR, MuMin/BlockDev, FAT, Backup/configuración y Power2. Varias rutinas necesitan la cola ausente para funcionar |
| ¿Backup? | La excepción por fallo de SwitchBackup no elimina otras dependencias: parámetros MuMin, puertos y modo. No se demuestra arranque independiente de todos los datos de fábrica |
| ¿Dispositivo1/2 = nflasha1/2? | **INFERENCIA RESPALDADA** por contenido histórico kernel/initrd y Backup/setting. Sigue sin cerrarse toda traducción física MuMin; no elevar a equivalencia inequívoca para escribir |
| ¿Puede quedar mode tras cierre incompleto? | **INFERENCIA RESPALDADA:** si se creó y el cierre no llegó a borrarlo; no se ha leído el estado posterior al incidente |
| ¿Qué impide montar 2? | Error BlockDev/BOSS, geometría o PBR/FAT corruptos, falta de memoria/configuración. `0xc01f3e54` exige firma `55 aa`, sectores512 y cluster32 sectores; `0xc01f3d8a` rechaza tipos no admitidos. El booleano del selector no distingue estas causas de archivo ausente |
| ¿Otra entrada al modo3? | **NO DEMOSTRADO** para la configuración A6000. REIO de R5 sigue condicionado; no se descubrió una condición legítima adicional habilitada ni una entrada de botones/USB que sustituya la bandera |
| ¿Recuperación automática universal? | **NO ENCONTRADA** en la ruta examinada; no es prueba de inexistencia en todo el SoC |
| ¿Carga de kernel? | **CONDICIONADA:** exige montar dispositivo1, resolver boot/loadaddr.txt, vmlinux.bin e initrd.img, memoria y direcciones válidas. Retorno cero de la envoltura no valida todas las lecturas |
| ¿Independiente de Linux normal? | **DEMOSTRADA estáticamente:** selección en Loader3, antes de Linux normal, **si la bandera existe y sus dependencias funcionan**. **NO DEMOSTRADA:** activación externa sin bandera y sin escribir el sistema/Backup |

### Nuevo límite para un futuro diagnóstico UART

`0xc01f3670` filtra por nivel y llama `0xc01f50c0` para UART o `0xc01f3640` para memoria; no toda cadena de log se transmite. `0xc01f35c0` consulta `0x510015` mediante `0xc01f4edc`: si no vale 1, pone el nivel de salida serie a cero. Si está habilitado, toma el puerto de `0x510000`. Las copias históricas BK4 examinadas dan `510015=00`, `510000=00`, `510003=00`; estado actual **PENDIENTE DE HARDWARE**. No se propone cambiar esos valores. Una UART sin texto después de esa inicialización es compatible con logging desactivado y no prueba que Loader3 no se ejecute.

`0xc01f5008` acepta puerto0/1, base `0xf2000000 + puerto×0x1000`; escribe `+0x24=0x1a`, `+0x28=3`, `+0x2c=0x70`, `+0x30=0x701`. `0xc01f505a` espera bit5 del estado `+0x18` y escribe `+0`. Son registros compatibles con PL011; [definiciones del kernel Linux](https://github.com/torvalds/linux/blob/master/include/linux/amba/serial.h) respaldan interpretar 8 bits, sin paridad, un stop y FIFO. **INFERENCIA RESPALDADA**, no datasheet Sony: el divisor equivale aproximadamente a115200 solo con reloj UART48MHz. No se verificó ese reloj en todas las etapas, ni UART0 activa si la depuración no se habilita. El multiplexado procede además de configuración de puertos `0xc01f3108`; continuidad de red no certifica que el mux esté seleccionado.

Validación de esta fase: comparación exacta del prefijo, instrucciones Thumb independientes, literales y REA sin interpretar cola ausente. El sistema de conocimiento pasa 73 pruebas excluyendo las seis de servidor MCP: la ejecución completa quedó esperando su primera prueba; por separado las 12 de triage pasan tras regenerar sus referencias. No se modificó el servidor para resolver ese bloqueo de entorno. Próximo paso: identificación documental de huella, diagnóstico pasivo y límites de SWD/NAND.

## 4. CN4906: orientación documental y fotografía pendiente

**VERIFICADO EN PDF:** CN4906 está en **SIDE A** (manual L3, lámina 6-38). En la orientación impresa, sus 16 contactos funcionales forman una hilera vertical: **pin 1 arriba y pin 16 abajo**; 17/18 son anclajes mecánicos al lado izquierdo de esa hilera. El entorno inmediato dibujado es CL4911 arriba, R4915/R4911 a la derecha-superior, R4916/R4912 a la derecha-inferior y R4927 abajo-derecha. El esquema identificativo es [CN4906/SIDE A](assets/e26-r6-cn4906-map.svg).

Esto sitúa el objetivo de una fotografía, no autoriza una conexión: una macro perpendicular debe incluir CN4906, serigrafía, CL4911, R4911/12/15/16 y R4927; una segunda toma abierta debe mostrar conectores/flex y orientación del cuerpo. No hay fotografía de la placa en los adjuntos disponibles, por lo que accesibilidad, población de la huella y continuidad siguen **PENDIENTES DE HARDWARE**. La relación funcional ya documentada por R5 no cambia: BIONZ UART0 es 4/5; BIONZ SWD aparece solo a través de R4911/R4912 marcadas XX en 11/12; 6/7 y la mayor parte del debug pertenecen a Darwin. El rail `EVER_3.15V` de pin 3 no certifica el dominio I/O ni autoriza alimentar una señal.

## 5. SWD BIONZ: acceso posible en esquema, no vía de recuperación demostrada

**VERIFICADO EN ESQUEMA:** IC6000 expone SWCLK W25 y SWDIO W26 hacia CN4906 11/12 únicamente si R4911/R4912 están pobladas. **NO DEMOSTRADO:** población en esta unidad, orientación física efectiva, tensión, mux, identificación de DP/AP, política de depuración, efecto de un attach o acceso a RAM/NAND. El JTAG convencional BIONZ no queda trazado a TDI/TDO/NTRST de CN4906 y no debe confundirse con el SWD opcional.

Por tanto SWD no es una alternativa aprobada para recuperar o reprogramar `nflasha3`: aun si un futuro diagnóstico acreditara un puerto, faltaría una primitiva de almacenamiento que conserve ECC/OOB, remapeos, Backup y calibraciones. Una prueba de attach tampoco es pasiva y puede cambiar ejecución, tiempos o energía. Queda fuera de cualquier futura captura UART y exige autorización física nueva, objetivo de solo lectura, herramienta identificada y evaluación explícita de sus efectos antes de usarla.

## 6. Almacenamiento BIONZ/MuMin y alternativas reales

El detalle BLDR confirma que el almacenamiento de arranque se direcciona por die/plane/block/page y que el controlador puede informar ECC corregible. No entrega geometría total, OOB, ECC, defectos ni el mapeo lógico de `nflasha3`. MuMin/BOSS sirve las imágenes lógicas respaldadas, pero no se ha identificado una interfaz externa física o una operación de restauración selectiva verificable. Una NAND cruda, un adaptador SPI genérico o sustituir el encapsulado no están justificados: podrían destruir precisamente los metadatos y calibraciones que se pretende conservar.

Las únicas vías que permanecen técnicamente coherentes son: (a) Loader3/UPDATER, si una futura traza demuestra que llega a él y cómo seleccionarlo sin inventar una bandera; (b) una interfaz de servicio BIONZ cuya lectura y efectos se demuestren primero; o (c) diagnóstico profesional de placa que preserve la original y produzca una lectura repetible antes de cualquier escritura. Ninguna está demostrada hoy. UART Darwin puede separar actividad del MCU de actividad BIONZ, pero no restaura directamente la NAND BIONZ; Serial Writer/SWD Darwin tampoco queda validado para esta placa ni resolvería por sí solo una imagen BIONZ dañada.

## 7. Secuencia pasiva propuesta, no ejecutada

La siguiente secuencia requiere una autorización física separada y personal competente; en esta sesión no se conectó, encendió ni midió la cámara.

1. Fotografiar e identificar SIDE A/SIDE B y CN4906 contra el mapa documental.
2. Confirmar únicamente la accesibilidad y población visibles; no puentear enlaces XX.
3. Con instrumentación de alta impedancia y referencia ya identificada, observar —sin transmisor, VCC, reset ni straps— la salida BIONZ UART0; el formato aproximado 115200 8N1 es una hipótesis a contrastar, no un ajuste que aplicar a ciegas.
4. Si hay traza, clasificar el último marcador: Loader2/Loader3, BOSS/FAT, kernel o Linux. Si no la hay, no concluir apagado: `Backup[0x510015]` podía silenciar el logger.
5. Solo si esa evidencia lo exige, evaluar actividad Darwin y rails definidos por esquema. SWD queda posterior y fuera del alcance pasivo.

Una traza es evidencia de etapa, no de causa única; el LED, USB ausente o silencio UART no bastan para atribuir el bloqueo a Darwin, BIONZ, NAND o Loader3.

## 8. Matriz de decisión de recuperación

| Escenario observado en una futura evaluación | Qué discrimina | Acción segura siguiente | Lo que sigue prohibido por falta de evidencia |
|---|---|---|---|
| BIONZ UART llega a Loader3 y falla FAT/BOSS | Arranque BIONZ y punto de fallo antes de Linux | Conservar traza; revisar la ruta UPDATER solo como hipótesis | Crear `mode`, reflashear o escribir particiones |
| BIONZ UART llega a kernel/Linux | Loader3 y almacenamiento inicial superados | Diagnosticar capa Linux/aplicación de forma no invasiva | Atribuirlo a NAND/Loader3 o usar SWD |
| Darwin activo, BIONZ sin señal/rails | Hipótesis de energía o arranque BIONZ gana peso | Medición profesional de enables/rails definidos | Alimentar BIONZ externamente o resetear/strapear |
| Darwin sin actividad y rails ausentes | Hipótesis Darwin/energía gana peso | Diagnóstico de placa y conservación de MCU/flash | Serial Writer, erase o desbloqueo automático |
| SWD no poblado/protegido | No hay servicio BIONZ por CN4906 demostrado | Volver a UART/diagnóstico profesional | Forzar pads, puentear R4911/R4912 o asumir JTAG |
| Lectura profesional identifica almacenamiento y produce imagen repetible | Base para estudiar restauración lógica | Comparar lectura con respaldos y documentar ECC/metadatos | Escribir NAND antes de validar lectura, mapa y preservación |

## 9. Cierre R6

1. **BLDR:** reconstruido como adquisición parcial, no como imagen NAND física.
2. **Trama perdida:** puede corresponder a advertencia ECC que Loader2 tolera; no prueba daño.
3. **Loader3:** solo 43 páginas iniciales están respaldadas; INFO6 requiere 21 páginas plane1 no adquiridas.
4. **Selector UPDATER:** existe estáticamente, pero su activación externa independiente no está demostrada.
5. **UART:** BIONZ tiene ruta de salida documentada; el logger puede estar deshabilitado por Backup.
6. **CN4906:** orientación documental resuelta; accesibilidad y población física no.
7. **SWD BIONZ:** posible solo por enlaces opcionales; no verificado ni equivalente a recuperación NAND.
8. **Darwin:** su UART/debug es un diagnóstico separado, no una reparación de BIONZ.
9. **NAND:** no hay componente, bus, ECC/OOB ni procedimiento físico de escritura validado.
10. **Calibraciones:** no se autoriza sustituir placa, borrar, reballing ni escritura cruda; la prioridad es preservar la placa original.
11. **Vía conservadora:** foto identificada → UART pasiva → clasificación de etapa → evaluación profesional solo si aporta lectura repetible.
12. **Resultado actual:** no se fabrica firmware, no se rellena Loader3 y no se propone una conexión activa.

R6 cierra el análisis offline con una frontera clara: la siguiente evidencia útil ya no es otra reconstrucción estática, sino una observación física pasiva autorizada que discrimine la etapa de arranque. Los pendientes E26-R5/R6 continúan abiertos en `docs/PENDIENTES.md` hasta contar con esa evidencia.
