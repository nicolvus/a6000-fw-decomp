# S24 — Camera.YC0 → endpoint Dataflow de ObjEffect

Fecha: 2026-10-17. Análisis estático de `libObj.so` A6000 FW 3.21; ELF32 ARM
ET_DYN, SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.

## Resultado

**VERIFICADO:** el constructor de `ObjCamera` crea el parser de `PIN_YC#0`
en `0x987eb6..0x987ec6`: reserva `0x54` bytes, le entrega el objeto Camera y
el pin ubicado en `ObjCamera+0x58`, y llama al constructor `0xa281dc`.
Guarda la instancia en `ObjCamera+0xa0`.

**VERIFICADO:** el constructor `CamUser::PinParserYcOut0` en `0xa281dc` fija
un destino Dataflow constante:

```c
PinParserYcOut0::PinParserYcOut0(ObjCamera *camera, ObjPin *yc0) {
    PinParserBase::PinParserBase(camera, yc0);  // 0x9581a4
    InfraPinParseSupBase::InfraPinParseSupBase(); // 0x97ec80, en +0x0c
    this->dataflow_destination = 0x00050004;     // +0x10
    this->request_field1 = 0;                    // +0x14
    this->request_field2 = 2;                    // +0x18
    // inicializa los campos restantes de estado
}
```

Por tanto, el request `0x1000` de S23 no se envía a un identificador producido
por la adquisición actual: siempre se dirige a `0x00050004` desde este parser.

**VERIFICADO:** `0x00050004` se usa en código de configuración Dataflow
`0x15d6c0..0x15d7a2`: construye `OBJAVBBCBASECLASS::DataflowInfraCh`, ejecuta
`infraDisconnectPin`, recupera dos pines con `infraGetPin` y los conecta con
`infraConnectPin`. La recuperación RTTI sitúa este bloque junto a
`OBJEFFECT::State_IntelligentActivePostProcess` (`destructor 0x15d63c`,
vtable `0xfee988`) y el estado constructor inmediato de ObjEffect.

**INFERENCIA FUERTE:** el endpoint `0x50004` pertenece a la configuración del
dominio ObjEffect durante *IntelligentActive*. La topología conocida Camera
`YC#0` → Effect.in0 es coherente con esa arista.

**NO_VERIFICADO:** que `0x15d6c0` sea por sí mismo el handler de payload
`0x1000`, el destinatario final después de la conexión, o que cualquier
respuesta sea una imagen nueva del sensor. El nombre del estado no autoriza a
clasificarlo como Live View ni a excluir por sí solo fotografía fija.

## Impacto

Esto cierra el tramo de inicialización:

```text
ObjCamera constructor
  → crea PinParserYcOut0 para PIN_YC#0
  → fija destination = 0x50004
  → Dataflow request/reply de S23
  → conexión/reconfiguración Dataflow en dominio ObjEffect
```

La ruta sigue sin alcanzar `ObjStillRecorder::Execute` ni su `ycBufferInfo`.
No se demuestra formato, dirección, caché, propiedad, sincronización o vida
útil del buffer. SilentShutter permanece **NO_VERIFICADO**.

## Reproducción

```sh
python3 -I analysis/session22/evidence/s24_yc_endpoint_audit.py
```

El auditor sólo desensambla los rangos `0x987eb6..0x987ec8`,
`0xa281dc..0xa28220` y `0x15d6c0..0x15d7a6`.

## Veredicto

**VEREDICTO: PARCIAL.** Se identifica el destino constante de Camera.YC0 y su
configuración Dataflow en el dominio ObjEffect. Falta localizar el receptor de
payload asociado a `0x50004` y seguir su respuesta hasta un descriptor DMM o
probar que no produce uno.

**Única siguiente investigación recomendada:** resolver `infraGetPin` para
los dos pines de `0x50004` en `0x15d6c0` y recuperar el callback que consume
su mensaje Dataflow `0x1000`.
