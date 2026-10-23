# Productor del YC de SFRA y condiciones de operación (línea F, Claude; parcial)

Ver además `sfra-linux-client.md` (ISS→buzones 0x1670464/0x167046a, handle u16 DMM, propiedad, anchos 320/640/1024 desde ISS; SFRA acepta hasta 1920). GET_JPEG saca el READY del ring y libera el resto.

## VERIFICADO (cadenas + decompilado)

SFRA no «tira» del sensor: recibe YC por **pines** de un sistema «SFRS» (`SystemCmdPinConnect/Disconnect/Get/RequestConnect/RequestDisconnect/PinSend`). `PinSend` (función `0x439abbfe`, export `sfra-pinsend.json`) manipula objetos pin con contadores (`GetCounter`, `nowVfc`, `osalID`, `Handle`) y registra «Send **RecPin**» (grabación) y «Send **EEPin**» (EE = visor/Live View); emite un mensaje `0x2009/0xb012` (longitud 0x28, handle de pin, índice de path) hacia el siguiente eslabón y libera el YC con `FUN_43b63566(handle,-1,-1)`.

**Strings SystemCmdPinConnect encontrados:**
- `0x43c83f8e`, `0x43c83fa3`, `0x43c83fef`, `0x43c85e0c`, `0x43c8d6c3`, `0x43c8d70b`, `0x43c8d75f`, `0x43ce8fbc`
- **Strings SystemCmdPinDisconnect:** `0x43c85e25`, `0x43c85e5a`, `0x43c85eb1`, `0x43c85ed0`, `0x43c8d77f`, `0x43c8d7b1`, `0x43c8d808`, `0x43ce90e9`

**Strings PinSend encontrados:**
- `0x43c799c6`, `0x43c79a48`, `0x43c79ac1`, `0x43c7cc58`, `0x43c8412a`, `0x43c841a8`, `0x43c84224`, `0x43c84293`, `0x43c842b7`, `0x43c8433b`, `0x43c843b5`, `0x43c84485`, `0x43c84513`, `0x43c84590`, `0x43c8606e`, `0x43c87fc9`, `0x43c8d9d7`, `0x43c8da0a`, `0x43c8db23`, `0x43c8db74`, `0x43ce9682`

**Strings PinConnect encontrados:**
- `0x43c7a046`, `0x43c7cbd0`

**VERIFICADO:** Existe un modo «**shutter mute thru**» (`0x439ac2fa`..., cadena `0x43ce955e`) y «kari review thru/free»: durante el apagón de obturador/revisión rápida, SFRA decide si deja pasar (thru) los fotogramas según una máscara de tipo de fotograma (`0x20`, `0x01`, `0x30/0x31`).

**VERIFICADO:** El JPEG se produce en SFRA con YC recibido por pin; `GET_JPEG` solo recoge READY (ver otros documentos). La entrada YC real viene del flujo EE/Rec del sistema de imagen (ADF: `DefDataflowInfraPin.h`).

## NO VERIFICADO

- **Quién entrega YC a SFRA 'pin' (Autoexec_pin, 0x439a5xxx):** No se han encontrado BL directos a PinSend (0x439abbfe) desde fuera de la propia función. Se llama probablemente vía tabla de funciones virtuales o puntero de función.
- **Llamantes indirectos/GOT/mensajes del productor (CamCore/ISP/DFE/Imaging):** No identificados estáticamente.
- **Qué tarea y qué mensaje entrega YC:** Pendiente.
- **¿El path SFRA se abre en modo foto normal sin cliente Wi-Fi?** Pendiente.
- **Quién emite SET_PATH(OPEN) además de ISS:** Pendiente (libObj, libInfraPtpControl, ScalarDaemon, PTP/remote).
- **Estados LIRO requeridos (modos 0x01/0x03, SetMode 0x436d6b54):** Pendiente.
- **¿SFRA/LV usa exposición de LV (rolling) o pueden fijarse tiempo/ISO para el frame?** Pendiente (SetExposure 0x436d6f6c).
- **Resolución máxima real en SFRA (tamaños 0x500/0x5a0/0x780):** Pendiente.
- **¿SDF/ddl_jpeg pueden generar mini JPEG (THMEnc/SCNEnc) del mismo YC?** Pendiente (tarea F-05).

## INFERENCIA

Por tanto, el productor del YC es el pipeline de vídeo/EE (DFE/CamCore → ADF pin EE) y SFRA depende de que el path esté abierto (`SET_PATH(OPEN)`, ISS lo hace con anchos 320/640/1024) **y** de que haya LV activo; no depende de una captura fotográfica ni emite CAIF.

## Efecto en S51

Ninguno directo. SFRA es un camino alternativo para obtener JPEG, no está relacionado con el obturador electrónico de foto fija.

## Archivos relacionados

- `docs/capture/sfra-electronic-frame-source.md` (este documento)
- `docs/capture/sfra-linux-client.md` (buzones, DMM, propiedad)
- `docs/capture/sony-dcf-playback.md` (ruta MakeWriteStillImage)
