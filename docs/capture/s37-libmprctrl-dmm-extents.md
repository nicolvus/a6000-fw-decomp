# S37 — libmprctrl: definidor DMM, extents y límite físico YC

## Resultado clasificado

| Validación | Estado | Evidencia / alcance |
|---|---|---|
| ACEPTO: definidor real de AllocDmmMemory/FreeDmmMemory | VERIFICADO | `.dynsym` definido, cuerpos locales en libmprctrl.so; SHA coincide. |
| RECHAZO: los getters citados pertenecen a DmmAccess | VERIFICADO | Los símbolos originales son **DmmAccessPLA**; no existen sus equivalentes DmmAccess en este ELF. |
| ACEPTO: getter de dirección separado del handle y del tamaño | VERIFICADO | Dirección `u32(R+0x10+8*i)`, tamaño `u32(R+0x14+8*i)`, handle `u16(R+4)`. |
| RECHAZO: dirección física/lógica efectiva y tamaño numérico recuperados | NO_VERIFICADO | Valores llegan de respuesta OSAL; getter no traduce ni desreferencia el valor leído. |
| RECHAZO: protocolo idéntico byte a byte a S33 | VERIFICADO | Payload OSAL de 0x18, correlación 0; S33 usa envoltura 0x78, unidad, correlación 0x55 y longitud 0x70. |
| ACEPTO: familia de campos DMM compatible con S33 | PARCIAL | Coinciden offsets relativos de comando/ID/clave/open; no demuestra identidad del proveedor de tabla+0x2e4. |
| ACEPTO: DmmCloseAndFree de S30 corresponde al símbolo definido aquí | VERIFICADO | PLT libObj 0xdc180, JUMP_SLOT 0x102d024, UND exacto y DT_NEEDED libmprctrl.so. No es otra implementación local de libObj. |
| RECHAZO: productor físico YC cerrado | NO_VERIFICADO | Sin identidad de claves/handles con P, sin enlace a APL, píxeles, pitch ni fin DMA. |

## VERIFICADO — alcance e integridad

Fecha: 18-10-2026. Se leyeron CURRENT, CONTEXT y los informes S36/S33/S30;
se ejecutó `search.py claim` para esos tres informes antes de reutilizarlos.
No se da por comprobado que ninguna sesión previa examinara este ELF:
la novedad comprobable aquí es la definición de los símbolos y su análisis.

Original: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/`
`nflasha15_unpacked_unpacked/lib/libmprctrl.so`, SHA-256
`514e14116caa1d15d75bd56641dabfe815f620b6208008929c44d8d70386011d`.
ELF32 ARM EABI5, **stripped**, con nombres C++ conservados en `.dynsym`.
`sha256sum` se ejecutó antes de `nm -D --defined-only`; el auditor verifica de
nuevo original y copia `analysis/ghidra/s37-input/libmprctrl.so`, modo 0444.

Proyecto nuevo `analysis/ghidra/libmprctrl.gpr`; importación/autoanálisis sobre
la copia, cero dependencias cargadas. Crear el proyecto escribe su base nueva;
la exportación final fue **-readOnly -noanalysis**. No se abrió silent-liro.gpr.
Se conservaron huellas de su `.gpr` y de todos los archivos de su `.rep`.
No firmware ejecutado, cámara, flasheo, instalaciones ni push.

Ghidra carga ET_DYN en base **0x10000**. E: significa VA ELF, G: VA Ghidra;
la tabla elimina el bit Thumb de las entradas de instrucción.

| Función original | E: | G: |
|---|---|---|
| DmmAccess::AllocDmmMemory(int,ushort*) | 0x1bc9c | 0x2bc9c |
| DmmAccess::FreeDmmMemory(int) | 0x1bf54 | 0x2bf54 |
| DmmAccess::GetDmmExtList | 0x1b628 | 0x2b628 |
| DmmAccess::DmmAllocateNEWAndOpen_body | 0x1b028 | 0x2b028 |
| DmmAccess::DmmAllocate(uint) | 0x1b58c | 0x2b58c |
| DmmAccess::DmmOpen(ushort) | 0x1b5e4 | 0x2b5e4 |
| DmmAccess::DmmShare(uint,ushort) | 0x1b3fc | 0x2b3fc |
| DmmAccess::DmmCloseAndFree(ushort) | 0x1afe8 | 0x2afe8 |
| DmmAccess::DmmCloseORFree_body | 0x1ada8 | 0x2ada8 |
| DmmAccessPLA::GetExtAdrsFromDmmAlloc | 0x1c620 | 0x2c620 |
| DmmAccessPLA::GetExtSizeFromDmmAlloc | 0x1c638 | 0x2c638 |
| DmmAccessPLA::GetExtAdrsFromDmmOpen | 0x1c62c | 0x2c62c |
| DmmAccessPLA::GetExtSizeFromDmmOpen | 0x1c644 | 0x2c644 |

## VERIFICADO — AllocDmmMemory devuelve un paquete, no una dirección raster

Decompilaciones completas, incluidos errores/limpieza, en
[s37-library.c](../../analysis/ghidra/s37-library.c) y
[s37-library.json](../../analysis/ghidra/s37-library.json); 1066 entradas
exportadas, incluyendo externos/PLT, no 1066 cuerpos semánticamente validados.

`AllocDmmMemory(mode,&handle)` llama `UnitTypeTableSelect(mode)`, registra el
mapa y, si `mode<26` y la tabla existe, llama `GetDmmExtList`, guarda su retorno
en un slot global indexado por modo y lo devuelve. En las otras ramas devuelve
cero. La selección por switch devuelve cero en modos sin tabla, incluidos
negativos; no interpretar el argumento como bytes ni como unidad S33.

`GetDmmExtList` recorre registros de **12 bytes**, hasta `s16(record+10)==-1`.
Para cada tipo no omitido por la condición de still-cache, reserva un mensaje,
pone cmd 1, tipo `record+0`, campos inicializados a cero/ffff, índice de
correlación en `+0x14` y flag **1** en `+0x16`; envía a OSAL **0x61003c**.
Obtiene una cola dinámica de respuesta y la escribe en la palabra **payload-4**.
Recibe respuestas, comprueba estado y cmd 0x8001 en la rama útil, identifica
la solicitud por `reply+6` y toma el handle en `reply+4`.

En éxito reserva una cabecera `(n+1)*4` y paquetes `16+8*count`, copiando los
pares de `reply+0x10`. La cabecera contiene `u16 first_handle`, `u16 pack_count`
y punteros desde `+4`. Cada paquete tiene `u32 subarea` en +0,
`u32 extent_count` en +4, `u16 handle` en +8, tipo en +0xc y pares desde +0x10.
Los setters `SetExtListPackHeaderStatus/OnPackHeader/PackStatus/OnPack` prueban
estos offsets. Hay ramas de fallo y limpieza completas en el export; no se
presume que la operación siempre alcance éxito.

**Distinción necesaria:** ni la cabecera devuelta por AllocDmmMemory ni el
paquete transformado tienen el layout de cabecera de la respuesta DmmAllocate.
Aplicarles directamente `GetUnitHandleFromDmmAlloc` o `GetExtCountFromDmmAlloc`
leerá campos distintos. Primero se debe identificar el tipo de objeto.

La rama S36 `AllocDmmMemory(0x0c,&id)` queda acotada: modo 12 selecciona
E:0x3da5c, primer registro `{type=0x8125b, subarea=3, handle=0, tag=0}` y
terminador siguiente en +12 con `s16(+10)=-1`. La tabla no contiene una
dirección/tamaño de píxeles; contiene un tipo solicitado al servicio remoto.
Esto explica un paquete de listas para el consumidor MPR de S36, sin unirlo
a las claves Rendezvous del YC.

## VERIFICADO / PARCIAL — qué devuelven exactamente los getters

Para un descriptor de respuesta **R**, los cuerpos completos son lecturas:

```c
address_i = *(uint32_t *)(R + 0x10 + 8*i);
size_i    = *(uint32_t *)(R + 0x14 + 8*i);
count     = *(uint16_t *)(R + 8);
handle    = *(uint16_t *)(R + 4);
```

GetExtAdrsFromDmmOpen/GetExtSizeFromDmmOpen tienen exactamente las mismas
expresiones que sus versiones Alloc. En G:0x2c628 y G:0x2c640 se ven los
`LDR [r1,#0x10]` y `LDR [r1,#0x14]`, después de sumar `index<<3`.
No hay comprobación de límite ni conversión de dirección en estos getters.
El count/handle usan LDRH en G:0x2c614/G:0x2c654.

**VERIFICADO:** la palabra llamada Adrs no es el campo handle: ocupa otra
posición y tiene 32 bits. `DmmAllocateNEWAndOpen_body` copia el descriptor
remoto a un `malloc` local: 0x18 bytes si count es cero, `16+8*count` si no.
El puntero de malloc es dirección CPU real del **descriptor**, no prueba de
que sus palabras Adrs sean direcciones CPU accesibles ni memoria física.
Los getters exportados no tienen consumidores locales recuperados que
desreferencien su resultado o lo escriban a un registro DMA.

**INFERENCIA:** los nombres originales y los pares son compatibles con
dirección/longitud de extents; longitud en bytes es plausible. **NO_VERIFICADO:**
dominio físico/virtual/bus, unidad exacta del tamaño, valor numérico del extent,
contigüidad, mapeo CPU, geometría, pitch o contenido YC. El servicio remoto
produce esas palabras en ejecución; no están fijadas por estos getters.

## VERIFICADO — protocolo y comparación por offsets con S33

DmmAllocate llama al cuerpo común con `(type,0,1,0)`;
DmmOpen con `(0,id,5,0)`; DmmShare con `(type,id,2,0)`.
El cuerpo crea cola `osal_dynamic_id(0x2a,199,&reply_id)`, reserva payload
**0x18** con `osal_valloc_msg_wait(0x61003c,...)`, lo borra, construye campos,
envía con `osal_snd_msg` y espera con `osal_rcv_msg_tmo(...,-1)`.
`FUN_0002a9c2` escribe `payload[-4]=reply_id` en todos estos casos.
Después libera respuesta y elimina la cola; no hay espera de fin DMA.

La comparación justa toma `B` como principio de payload libmprctrl y `S`
como principio de la solicitud exterior S33, cuyo comando empieza en S+4:

| Campo de solicitud share | libmprctrl | av-cam S33 | Resultado |
|---|---|---|---|
| Comando | u16 B+0 = 2 | u16 S+4 = 2 | Coincide tras desplazar 4 |
| ID origen | u16 B+2 = id | u16 S+6 = id | Coincide |
| Clave/tipo origen | u32 B+4 = type | u32 S+8 = key | Coincide estructuralmente; misma semántica completa no probada |
| Correlación | u16 B+0x14 = 0 | u16 S+0x18 = 0x55 | **Diferente** |
| open/flag | u16 B+0x16 = 0 | u16 S+0x1a = open | Igual en rama S33 open=0; no en todas |
| Envoltura | cola de retorno en B-4 | unidad en 16 bits altos de S+0 | **Diferente** |
| Tamaño/longitud | reserva payload 0x18 | borra 0x78; u16 S+0x74 = 0x70 | **Diferente** |

En la respuesta libmprctrl acepta cmd 0x8001/0x8005/0x8003/**0x8002**,
valida estado mediante CheckDMMRetCode y copia según count en +8.
No exige correspondencia exacta entre comando solicitado y recibido, tag 0x55,
ID distinto de ffff ni los campos no nulos exigidos por S33 cuando open=1.
S33 sí exige específicamente 0x8002 y esas condiciones de identidad/apertura.

**PARCIAL:** comparten un contrato de payload reconocible. **INFERENCIA:**
pueden ser adaptadores del mismo servicio DMM. **NO_VERIFICADO:** proveedor
real de `av-cam base+0x14/+0x2e4`, traducción entre ambas envolturas y
equivalencia de respuestas concretas. Este ELF es cliente OSAL y definidor
de la API C++; no es por ello el allocator físico ni el receptor demostrado
del slot av-cam. La coincidencia parcial de protocolo no cierra esa identidad.

## VERIFICADO — DmmCloseAndFree y S30

El original libObj.so se verificó por SHA-256
`8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.
`llvm-objdump` identifica E:0xdc180 como
`_ZN9DmmAccess15DmmCloseAndFreeEt@plt`; sus tres instrucciones ARM calculan
el slot GOT **0x102d024**. `readelf -rW` confirma R_ARM_JUMP_SLOT para el
mismo mangled exacto, `nm -D` lo marca UND y DT_NEEDED incluye libmprctrl.so.

La implementación local aquí es E:0x1afe8 (símbolo Thumb 0x1afe9), firma
`DmmAccess::DmmCloseAndFree(unsigned short)`. Registra el handle y llama
`DmmCloseORFree_body(handle,4,2)`. Ese cuerpo envía payload de 0x18 con
cmd 4, ID en +2 y flag 2 en +0x16 al mismo endpoint OSAL, espera respuesta,
valida resultado y libera recursos de mensajería.

**ACEPTO:** enlace importación/definición nominal exacto y dependencia directa;
S30 citaba el PLT, ahora se dispone del cuerpo proveedor. No es una función
hermana por compartir nombre ni una coincidencia de direcciones. Las dos VA
pertenecen a objetos distintos y nunca se comparan como direcciones runtime.
**NO_VERIFICADO:** binding efectivo en presencia de interposición dinámica;
no se observó el loader en ejecución.

## NO_VERIFICADO — relación con P, APL y próximo paso

No se recuperó un mismo handle/respuesta que vincule los pares de este ELF
a las claves `P+0x18c/P+0x194` o al handle secundario `P+0xbc` de S33.
La selección mode12/type 0x8125b tampoco demuestra esa equivalencia.
No se halló flujo desde estos getters a los bancos APL
`0xf3850400/0xf3950400/0xf3a50400` de S34; similitud de pares no identifica
dominio de direcciones, motor que llena memoria ni cuadro de adquisición.

**Pendiente real:** identificar el receptor de OSAL **0x61003c** y el proveedor
del slot av-cam, y recuperar la traducción de solicitud/respuesta hasta quien
escribe `reply+0x10/+0x14`. Después seguir la misma clave/ID hasta Rendezvous
cmd 0x0c, productor YC y configuración APL. Solo entonces decidir físico/bus/
lógico y tamaño en bytes con consumidor o mapeo efectivo. Pitch/formato,
caché/reciclaje y fin DMA siguen abiertos; una dirección sola tampoco los cierra.
La rama local getters→valor físico es irresoluble en este ELF porque devuelve
datos externos sin interpretación local; se continuó con paquete, transporte,
modo12 y enlace S30 para delimitar el siguiente receptor concreto.

## Evidencia y validación

- [JSON clasificado](../../analysis/ghidra/s37-findings.json), export íntegro
  [JSON](../../analysis/ghidra/s37-library.json) y [C](../../analysis/ghidra/s37-library.c).
- `S37Export.java`, `s37-symbols.txt`, `s37-import.log`, `s37-readonly.log`;
  manifiestos `s37-avcam-before.sha256` y `s37-avcam-rep-before.sha256`.
- [Auditor](../../analysis/ghidra/s37-audit.py): fallo inicial por findings
  ausente; después PASS de SHA original/copia, modo 0444, av-cam intacto,
  cuerpos completos, LDR de extents, layout OSAL y conclusiones acotadas.
- No existe `.git`; cambios sin commit.
- Auditor ampliado: PT_LOAD nativo confirma endpoint 0x61003c, tabla mode12,
  terminador y relocación/dependencia S30. Ruff/mypy del auditor PASS;
  mypy src PASS; Ruff src/tests mantiene nueve avisos previos en cuatro tests
  ajenos sin tocar. Tests conocimiento **67 PASS**. Mantenimiento en cinco
  pasos: grafo estable **1455 entidades / 2763 relaciones**.

**VEREDICTO: CAMBIOS** respecto de cerrar productor físico YC e identidad del
slot av-cam. Definidor C++, layouts y vínculo nominal S30 quedan verificados.
