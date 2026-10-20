# S22 — sensor nuevo → descriptor YC consumible por StillRecorder

> **Corrección S30:** `0x436d6118` es un getter y `0x437f7ff0` selecciona
> drive/relación de tamaño; no prueban inicio ni fin DMA. `+0x4b54` procede
> de `CapIdTblMgr::GetCaptureID`, RPC `0xd008`, y no es un descriptor YC.
> Queda retirada la investigación siguiente que proponía buscar completion
> en ese getter. Detalle: [S30](s30-pipelines-capture-encode.md).

Alcance: firmware ILCE-6000 3.21, análisis estático local. No se ejecutó código
en la cámara ni se modificó un binario original.

## Bases de dirección y reproducibilidad

- **VERIFICADO:** `av-cam.bin` se trata como imagen plana con base VA
  `0x43541000`; SHA-256
  `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
  `QuerySilentLiro.java` verifica ese hash antes de decompilar.
- **VERIFICADO:** `libObj.so` es ELF32 ARM little-endian, `ET_DYN`; su segmento
  ejecutable tiene `p_vaddr=0`. Las direcciones de este informe para la
  biblioteca son VA ELF. El proyecto Ghidra local las representa con `+0x10000`;
  no se mezclan ambas convenciones.
- Reproducible: `python3 -I analysis/session22/evidence/s22_sensor_yc_audit.py`.
  El auditor comprueba el hash, la serialización LIRO y el precontrato de
  `EncodeStill`; no convierte el resultado en una prueba de adquisición.

## Flujo recuperado y frontera real

```text
LIRO fila 0x78: 0x43b1bdb4
  -> selector IMX210 0x437f7ff0                    [VERIFICADO]
  -> (fin de lectura/DMA y productor YC)           [NO_VERIFICADO]
  -> contexto de captura +0x4b54/+0x4b58/+0x4b5c  [NO_VERIFICADO: origen]
  -> Stage_Notify, sitio 0x437efe78                [VERIFICADO]
  -> copia StillInfo de 0x28c B y mensaje 0x2a8    [VERIFICADO]
  -> consumidor LIRO                               [VERIFICADO: entrega; no raster]

ObjCamera.out0 -> ObjEffect.in0                    [VERIFICADO: topología]
ObjScalar.out2 -> ObjStillRecorder (fila 0xb4)     [VERIFICADO: topología condicional]
YC real nuevo del sensor -> cualquiera de esos pines [NO_VERIFICADO]
```

**VERIFICADO:** el estado no cancelado de `0x43b1bdb4` invoca
`0x437f7ff0`, el selector de modo del sensor. Esto une LIRO al selector, pero
no a un fotograma terminado.

**VERIFICADO:** en la función que contiene `0x437efe78` (entrada inferida por
Ghidra `0x43b1939c`), se leen `ctx+0x4b54`, `+0x4b58`, `+0x4b5c` y `+0x4b64`;
`FUN_43afe932` copia `0x28c` bytes, después se reserva/envía un mensaje de
`0x2a8` bytes por `FUN_437feef8(..., &0x00020002)`. La copia no lee píxeles.

Pseudocódigo reducido, extraído de
`analysis/session22/evidence/s22-liro-producer-probe.json`:

```c
still.sequence_id = *(u32 *)(ctx + 0x4b64);
still.capture_id  = *(u32 *)(ctx + 0x4b54);
still.footer[0]   = *(u32 *)(ctx + 0x4b58);
still.footer[1]   = *(u32 *)(ctx + 0x4b5c);
copy_0x28c(message + 0x14, still_info);
send_message(message, 0x2a8, selector = 0x20002);
```

**NO_VERIFICADO:** qué función escribe esos campos desde una terminación DMA,
cuál produce el primer descriptor YC, y si este `StillInfo` refiere una imagen
recién adquirida. El llamado posterior a `0x436d6118` visible en la secuencia
del selector es una pista, no una identificación de productor.

## Contrato exigido por el grabador

**VERIFICADO:** `ObjStillRecorder::Execute` (`libObj.so` ELF `0x90b248`) prepara
`EncodeStill` en `0x90ad20`. Su entrada requiere, entre otros:

| Elemento | Evidencia | Estado |
|---|---|---|
| `ycBufferInfo` | parámetro `0x1018`: 12 B `{handle:u16, unitType:u32, physTop:u32}` | VERIFICADO |
| Buffer de decodificación | `0x1032`, mismo formato | VERIFICADO |
| Geometría | `0x1036` canvas `{w:u16,h:u16}`; región/layout condicionales `0x1038/0x1037` | VERIFICADO |
| Color | colorimetría `0x1072` en `0..3`; rango Y `0x1073` en `0..1`; fondo `0x1034` | VERIFICADO |
| Apertura DMM | se exige que el handle YC abra correctamente | VERIFICADO |
| Formato, pitch, submuestreo, alineación y tamaño mínimo | no se validan en esa ventana | VERIFICADO como ausencia de validación; contrato efectivo NO_VERIFICADO |
| Dirección CPU/DMA, caché, ownership, barrera y liberación final | ninguna arista Camera/sensor→DMM lo demuestra | NO_VERIFICADO |

`StillInfo` transporta descriptores `{handle, offset, size, reuse}` de áreas
JPEG/RAW y metadatos. **INFERENCIA:** puede ser parte de la misma operación de
foto. **RECHAZADO:** tratar por ello sus 0x28c bytes como el descriptor YC de
entrada a `EncodeStill`.

## WriteStill y rutas alternativas

**VERIFICADO:** `ObjStillRecorderCore::WriteStill` (`libObj.so` ELF
`0x909a84`) está después de `Execute`/Pool/Mpr y trabaja con una imagen ya
registrada como `StillInfo`; no es el punto que construye `ycBufferInfo`.
`Execute` llega a `MprCtrl::WriteStill` a través de la preparación nativa de
recording. Por tanto:

- **RECHAZADO:** afirmar que `WriteStill` acepta un YC nuevo sólo porque ambos
  recorridos usan estructuras DMM.
- **HIPÓTESIS:** podría escribir una imagen producida electrónicamente si otra
  ruta crea, valida, registra y conserva un objeto que satisfaga el contrato
  anterior. No hay instancia estática demostrada.

Se comprobó una alternativa antes de detenerse:

- **RECHAZADO:** SFRA/ISS como productor. Su salida comprobada es JPEG DMM,
  no `ycBufferInfo` ni un puente a MPR.
- **RECHAZADO:** RawPlay/DevLater. `0x437edd44` abre un `.ARW` existente de
  tarjeta SD; no adquiere un cuadro nuevo.
- **NO_VERIFICADO:** `ObjCamera.out0` es un pin YC por topología, pero ni su
  productor, ni formato, ni ciclo de vida se recuperaron.

## Lectura electrónica sin accionamiento mecánico

**VERIFICADO:** la captura fija seleccionada por `0x437eabfc` entra en
`Stage_CaComm 0x438c2538` y usa CAIF hacia Darwin. La fila `0x78` llama al
selector IMX210, pero no demuestra que produzca una foto fija independiente de
la secuencia CAIF.

**NO_VERIFICADO:** una lectura electrónica completa sensor → YC → Recorder
sin accionamiento mecánico. `SilentShutter` sigue **NO_VERIFICADO**.

## Veredicto y bloqueo

**VEREDICTO: PARCIAL.** Se cerró la frontera de entrega LIRO: serializa
metadatos/StillInfo, no el raster. Se mantiene abierto el requisito central:
el productor del YC nuevo y su contrato de caché, propiedad, sincronización y
vida útil.

Bloqueo concreto: falta la arista desde la terminación de lectura/DMA del
dominio de sensor (candidato a partir de `0x436d6118`, llamado tras el selector)
hacia el objeto/contexto que llena `ctx+0x4b54..+0x4b64` o hacia un
`ycBufferInfo` DMM de `ObjCamera`/`ObjScalar`.

**Única investigación siguiente recomendada:** decompilar `0x436d6118` y sus
referencias/registro de callback para identificar si publica la terminación de
lectura y qué consumidor recibe el descriptor antes de `Stage_Notify`.
