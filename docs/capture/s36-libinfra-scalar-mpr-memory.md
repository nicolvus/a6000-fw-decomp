# S36 — libInfraScalarMpr: memoria SysV y frontera DMM

## Resultado clasificado

| Validación | Estado | Evidencia / alcance |
|---|---|---|
| ACEPTO: biblioteca ARM con nombres C++ conservados | VERIFICADO | SHA-256 `b56b4c6172a60b879ebf405bc64e19e7456d230ff6125a21bbd4469e35c0d2c9`; `file` dice **stripped**, pero `.dynsym` conserva nombres. |
| RECHAZO: contiene los cuerpos de AllocDmmMemory/FreeDmmMemory | VERIFICADO | Ambos son `U`/`UND`, con relocaciones `R_ARM_JUMP_SLOT`; la firma es `unsigned short*`, no `short*`. Solo existen stubs PLT locales. |
| ACEPTO: `AllocSharedMemory` devuelve una dirección virtual utilizable | VERIFICADO | `GetSharedMem` llama `shmget`/`shmat`; un consumidor la usa como destino de `MemCpy8`. No es una dirección física numérica recuperable estáticamente. |
| RECHAZO: ese puntero cierra el productor físico YC de S33 | NO_VERIFICADO | Es una ruta SysV de intercambio/copia; sin identidad de handle/clave ni enlace al sensor/DMA. |
| RECHAZO: protocolo DMM idéntico al de av-cam confirmado | NO_VERIFICADO | Los cuerpos que podrían construir ese protocolo están fuera de este ELF. |

## VERIFICADO — método, integridad y direcciones

Se auditaron los antecedentes S33/S35 con `search.py claim` y se leyeron los
dos informes solicitados. No se repiten aquí sus protocolos ni productores.
La búsqueda previa por `DmmAccess` devuelve antecedentes de otras bibliotecas;
no se usa eso para afirmar exhaustivamente que nadie examinó este ELF en S1–S35.

Se importó **únicamente una copia** `/tmp/s36-input/libInfraScalarMpr.so`, modo
0444, al nuevo proyecto `analysis/ghidra/s36-project/libinfra-scalar-mpr.gpr`.
La creación y autoanálisis inicial necesariamente escriben la base nueva;
la exportación final reabre con **`-readOnly -noanalysis`**. No se abrió
`silent-liro.gpr`, no se cargaron dependencias (log: cero archivos adicionales),
ni se ejecutó código ARM. No hay cámara, flasheo, instalaciones ni push.

Ghidra eligió base **0x10000** para este ET_DYN. En este informe `G:` significa
VA Ghidra; `E:` VA ELF sin sumar esa base. Los símbolos Thumb tienen bit 0=1;
las entradas de instrucción de la tabla siguiente lo eliminan.

| Función | E: entrada | G: entrada |
|---|---|---|
| SharedMemory constructor | 0x17ee8 | 0x27ee8 |
| GetSharedMemoryInfo | 0x17f28 | 0x27f28 |
| AllocSharedMemory | 0x17f64 | 0x27f64 |
| FreeSharedMemory | 0x17ffc | 0x27ffc |
| FreeAllSharedMemory | 0x18090 | 0x28090 |
| FreeSharedMem | 0x20700 | 0x30700 |
| GetSharedMem | 0x2076c | 0x3076c |
| GetMemoryForEdit | 0x20cbc | 0x30cbc |
| FreeMemoryForEdit | 0x20d04 | 0x30d04 |

## VERIFICADO — decompilación completa de SharedMemory y auxiliares

El pseudocódigo íntegro y listing están en `s36-library.json/.c` (buscar por
entrada G:); el export contiene 1439 entradas, incluyendo PLT y externos
sintéticos, **no 1439 implementaciones semánticamente verificadas**.

`AllocSharedMemory(bytes,&id,&ptr)` inicializa salidas a `-1/NULL`. Si
`this+4` (cantidad) alcanza `this+0` (capacidad), devuelve 7. Usa la tabla
`this+8`, registros de **12 bytes**, y llama `GetSharedMem(bytes,&rec.id,&rec.ptr)`.
En éxito guarda bytes en `rec+8`, publica ID/puntero y aumenta cantidad;
devuelve 0. En error propaga el estado y no aumenta cantidad.

`GetSharedMem` hace `shmget(0,bytes,0x3b6)`, guarda su ID y comprueba `-1`.
Después hace `shmat(id,NULL,0)`, guarda el retorno en `*void**` y comprueba
`(void*)-1`; normaliza el puntero a NULL y devuelve 7 al fallar, 0 en éxito.
El listing confirma los argumentos en G:0x3076c–0x307d0. Es una llamada a
memoria compartida SysV, no un empaquetador de mensajes DMM. No hay `mmap`,
dirección física o pitch en esta cadena. La dirección concreta depende del
retorno de `shmat`, no de una constante del firmware.

`GetSharedMemoryInfo(id,&ptr,&bytes)` busca por ID y devuelve el mismo puntero
y tamaño; inicializa salidas a cero y devuelve 2 si no encuentra ID.
`FreeSharedMemory` busca ID, llama `FreeSharedMem`, compacta intercambiando el
último registro y decrementa cantidad solo en éxito. `FreeAllSharedMemory`
recorre los registros y llama al mismo auxiliar. `FreeSharedMem` llama
`shmdt(ptr)` si no es NULL y `shmctl(id,0,NULL)` si ID!=-1; devuelve 7 ante
fallos. La rama de fallo de `shmat` no elimina por sí misma el ID recién creado;
no se presume limpieza ulterior ni éxito en ejecución real.

## PARCIAL — rama DMM: cuerpos ausentes, consumidores completos

`nm -D -C`, relocaciones y desensamblado concuerdan:

| Importación | PLT E: / G: | GOT E: | Cuerpo local |
|---|---|---|---|
| `_ZN9DmmAccess14AllocDmmMemoryEiPt` | 0x168c0 / 0x268c0 | 0x3dbd4 | No; salto indirecto PLT |
| `_ZN9DmmAccess13FreeDmmMemoryEi` | 0x16020 / 0x26020 | 0x3d908 | No; salto indirecto PLT |

Por ello **no se puede decompilar completamente esas dos implementaciones
en este `.so`**, ni decidir si el proveedor asigna memoria física/lógica,
abre un mapeo o solo devuelve un identificador. Un stub no es el backend.
`DT_NEEDED` incluye `libMWF.so`, pero no prueba qué objeto resuelve cada símbolo;
no se importó ni analizó ninguna otra biblioteca en S36.

`GetMemoryForEdit` G:0x30cbc llama a AllocDmmMemory con **0x0c** y la dirección
de un `ushort` local (G:0x30cd0–0x30cd4); guarda **r0** en la salida `uint*`,
devuelve error 4 si r0==0 y 0 si no. El ushort no se usa después.
`FreeMemoryForEdit` G:0x30d04 llama FreeDmmMemory(0x0c), ignora su retorno y
devuelve 0. **No interpretar 0x0c como bytes, cmd Rendezvous o tipo de unidad
sin el proveedor.** No se ve cmd/id/longitud del transporte DMM en estas llamadas.

Los consumidores G:0x29288 `CallMprDeleteContentList`, 0x29468
`CallMprDeleteContent` y 0x29e94 `CallMprChangeRotationAngle` pasan ese valor
a `MprIf::Delete` / `ChangeRotationAngle` y liberan por FreeMemoryForEdit.
No lo desreferencian como píxeles. Esto preserva el valor hasta MPR, pero no
resuelve si es puntero o ID. No aparece un símbolo compartido que enlace
estas importaciones C++ al slot resuelto en carga de av-cam.

## VERIFICADO / PARCIAL — punteros de datos y geometría

El barrido demangled no encontró nombres con `pitch`, `stride`, `width`,
`height`, `format` o `rendezvous`. Esto acota la superficie nominal, no prueba
ausencia de campos anónimos. Se exportó toda la biblioteca para revisar también
consumidores y auxiliares sin depender solo de nombres.

**VERIFICADO:** `MprCb_GetStillData`, E:0x1a410 / G:0x2a410, reserva un bloque
SysV de 0x808 bytes y, en otra rama del callback, un bloque de tamaño leído de
`local_24[3]+0x150`. Copia a este último con
`MemUtil::MemCpy8(local_34,*(void**)(local_24[3]+0x14c),iVar9)`.
Es evidencia estática de un **puntero real de destino de copia de datos still**,
no de una dirección de adquisición YC ni del formato del contenido copiado.
El callback no permite llamar a 0x808 «plano YC» ni al tamaño variable «pitch».

**PARCIAL:** `Api_GetBufferThumbnail` G:0x2e098 también muestra reserva y copia,
pero Ghidra representa origen/tamaño con `pvRam00000000/iRam00000004`;
la procedencia de esos valores no queda recuperada con fiabilidad. No se usa
esa decompilación para afirmar una dirección raster concreta.
`Api_GetAviData` G:0x2e668 reutiliza ID/puntero de SharedMemory y los entrega a
`MprIf::GetAVIndexContentInfoList`; no hay equivalencia demostrada con YC.

**INFERENCIA:** la ruta SysV es un buffer de intercambio/copia hacia clientes
MPR. La inferencia se apoya en `shmat`, la tabla de IDs y las copias; no implica
contigüidad física, coherencia de caché DMA ni adquisición desde sensor.

## NO_VERIFICADO — cierre físico y próximo paso exacto

S36 **no cierra, ni siquiera parcialmente por identidad, el productor físico YC**:
el nuevo puntero SysV no se enlaza a `P+0x18c/P+0x194`, al secundario `P+0xbc`
ni a un AllocRendezvous equivalente. El cmd 2/id 0x55/longitud 0x70 y la
resolución de `base+0x14/+0x2e4` siguen sin correspondencia con este ELF.
No se han demostrado ancho/alto/pitch/formato ni fin sensor/DMA.

Próximo paso: localizar el **definidor** de los dos nombres mangled exactos
de la tabla, contrastar su `STT_FUNC` definido y decompilar la cadena de
asignación/mapeo/mensajes en un alcance separado. Resolver independientemente
el proveedor del slot av-cam y solo unirlos con símbolo/relocación/ABI o
protocolo inequívoco. No repetir SharedMemory como si fuera DMM.

## Evidencia y validación

- [Hallazgos JSON](../../analysis/ghidra/s36-findings.json),
  [export JSON](../../analysis/ghidra/s36-library.json),
  [pseudocódigo completo](../../analysis/ghidra/s36-library.c).
- `s36-symbols.txt`, `s36-relocations.txt`, `s36-objdump.txt`; el objdump usa
  `--triple=thumbv7-linux-gnueabi`, mientras PLT ARM se contrasta con Ghidra.
- `s36-import.log` y `s36-readonly.log`; script `S36Export.java`.
- [Auditor](../../analysis/ghidra/s36-audit.py): fallo inicial por export ausente;
  luego PASS de SHA original/importación, huella del proyecto av-cam, seis
  funciones completas, llamadas SysV e importaciones UND.
- Ruff del auditor sin avisos nuevos; `ruff check src tests` conserva nueve
  avisos ajenos preexistentes. Mypy src/auditor PASS. No existe `.git`:
  cambios sin commit.

**VEREDICTO: CAMBIOS** respecto de confirmar backend DMM/productor físico YC;
la investigación local y la delimitación de cuerpos ausentes quedan completadas.
