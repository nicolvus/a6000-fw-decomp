# S148 — el módulo `[DEPTH]` (16 trazas) del firmware A6000 fw3.21

> Bytes de `analysis/rea-independent/input/av-cam.bin`, convención **vaddr =
> 0x43541000 + file_offset**; regla **estricta** canónica del repo, verificada
> **a mano** en los 17 sitios. Informe: `analysis/s148_depth/depth.md` · Datos:
> `analysis/s148_depth/depth.json`.

## VERIFICADO

* **16 trazas** `[DEPTH]` (16 textos distintos) en `0x43C249EC`–`0x43C24C73`:
  11 `INFO`, 2 `DEBUG`, 3 `WARN`. **17 sitios de emisión** (regla estricta) en
  **11 funciones**; **0 cadenas sin referencia** (todas por PIC, ninguna con
  puntero absoluto de 4 B).
* **No es un módulo nuevo**: es la instrumentación de la clase
  **`DepthGaugeMain`** (RTTI `14DepthGaugeMain` `0x43C24B85`, `type_info`
  `0x43FD7C84`, vtable `0x43FB8F50`), que se da de alta con el nombre
  **`depth`** (`0x43C24B46`) en el registro de módulos de `0x435AB6F0`, con su
  **tabla de 6 comandos** (`0x43FD7C30`, 12 B/entrada `{nombre, nombre,
  handler}`): `update` `0x43562454`, `getLiro` `0x43562424`, `getMsg`
  `0x4356230C`, `notifyOn` `0x435623BC`, `notifyOff` `0x43562354`,
  `enableDummyRecv` `0x4356228C`.
* **Transporte**: GID **`0x018B04DC`** (6 apariciones del literal), tabla global
  de servicios `0x4401EEE4`; ids de notificación **1 = GET, 2 = NOTIFY_ON,
  3 = NOTIFY_OFF** (`cmp` en `0x435626D4`); `valueDepth` se recorta a
  **0xFA0 (4000)** en `0x43541B04`.
* **Consumidor verificado**: `CS_ExifMakerNote.cpp` (`0x43CC56DC`) llama a
  `getMsg` en `0x438B900A` y escribe el valor en el MakerNote: tag Exif
  **0x5001** = racional `(valueDepth*10 : 1000)` (`0x438B90A8`) y tag
  **0x5002** = estado (`0`/`1`/`0x80`/`0x81`, `0x438B90B8`); segundo consumidor:
  `[ACCY]` llama a `update` en `0x43564DC0` (`{status=2, valueDepth=0}`) y
  `0x43564ED2`.
* **Los 26 destinos de llamada distintos del módulo no salen de él** (solo
  thunks OSAL, log internos, registro de clases y emisores de mensaje):
  **cero** llamadas a `[CAM_IMAGER]`, `[CAMERA_MAIN*]`, `[IDT_OPD]`,
  `[VPH_API]`/`[VDF]`.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[DEPTH]` / textos interiores coincidentes | **16** / 16/16 | **0** / **0/16** | **0** / **0/16** |
| clase `14DepthGaugeMain` | 1 | **1** | **1** |
| comandos de la tabla (mismos nombres y orden) | 6 | **6** | **6** |
| literal del GID `0x018B04DC` | 6 | **6** | **6** |

⇒ el módulo es **preexistente**; la fw3.21 de la A6000 añade **solo el logging** (S130/S132/S136).

## NO VERIFICADO

* Qué magnitud física mide `valueDepth` (0..4000) y qué significa `status`;
  la sigla `DEPTH` no aparece expandida en ningún byte (no se inventa). No hay
  **ningún nombre de fichero embebido** en el módulo (`0x4356228C`–
  `0x435627B0`): solo se identifica `CS_ExifMakerNote.cpp` como *consumidor*.
* Receptor final del GID `0x018B04DC` fuera de `av-cam.bin`; por qué `[ACCY]`
  publica `update` con `status=2`; quién invoca `notifyOn`/`notifyOff`.

## Línea del obturador electrónico

**0/16** trazas mencionan obturador, sensor, exposición, enfoque, lectura del sensor o distancia (0 ocurrencias de `shut`/`shutter`/`silent`/`electro`/`mech`/`sensor`/`exposure`/`readout`/`focus`/`af`/`dist`/`iso`/`aperture`/`iris`/`zpd`/`imager`/`drv`/`drive`) ⇒ **S51 (A/B/C = NO) intacto**.
