# S27 — recableado de `State_IntelligentActivePostProcess`

Actualización S28: [semántica y registro resueltos](s28-osal-pin-contract-closure.md).
La transición conecta VEF YC salida 0/2 con InfraImaging YC entrada 0/1,
tras desconectar VEF salida 0/2 y ScalarInfra salida 0/1.
El registro y receptor descritos como pendientes abajo ya están identificados.

Fecha: 2026-10-17. Análisis estático de `libObj.so` y `libBizFw.so` de A6000
FW 3.21. Este avance no cierra la ruta sensor → YC.

## Hallazgo

**VERIFICADO:** la rutina `0x15d6c0..0x15d7c4` pertenece al slot virtual 4 de
`OBJEFFECT::State_IntelligentActivePostProcess` (vtable `0xfee988`). No es un
constructor ni una tabla pasiva: ejecuta una transición completa de
desconexión, consulta y reconexión de infraestructura para dos perfiles
(`r4=0,1`).

Para cada perfil:

```c
disconnect(0x005a0048, profile_kind);
disconnect(0x01670464, profile_kind);
a = infraGetPin(0x005a0048, profile_kind);
b = infraGetPin(0x00050004, profile_kind);
infraConnectPin(a, b);
```

Los tres identificadores son literales del propio bloque:
`0x15d7d4=0x005a0048`, `0x15d7d8=0x01670464` y
`0x15d7dc=0x00050004`. En la primera vuelta los selectores locales son cero;
en la segunda se usan los valores 2 y 1. Cada fallo abandona con retorno 1;
el éxito sólo ocurre tras las dos vueltas y la destrucción del canal temporal.

**VERIFICADO:** `infraGetPin` no devuelve un callback embebido: en
`libBizFw.so:0x35a74..0x35ba2` envía `_MSG_PIN_GET` opcode `0x1000`, espera
respuesta y copia una descripción de 0x20 B, incluido `reply+0x20`.
`infraConnectPin` construye a continuación una petición de conexión con los
dos descriptores retornados (`0x35744..0x3578a`).

## Alcance y límite

Esto amplía S24: `0x50004` participa en una transición de estado concreta de
ObjEffect y se conecta con un segundo endpoint, no sólo se "reconecta" de
forma indeterminada. Aun así, las etiquetas semánticas de los tres IDs, el
registro que devuelve los descriptores, el callback del opcode `0x1000` y los
píxeles siguen **NO_VERIFICADOS**. No se puede afirmar que el par sea
Camera.YC0 → productor de captura, ni que produzca un descriptor apto para
StillRecorder. SilentShutter continúa **NO_VERIFICADO**.

## Reproducción

```sh
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x15d6c0 --stop-address=0x15d7e0 \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so

python3 -I scripts/func_owner.py /tmp/libobj-full.dis \
  analysis/session20/evidence/libobj-rtti-vtables.json \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so \
  0x15d6c0
```

## Veredicto

**VEREDICTO: PARCIAL.** Se recuperó una transición funcional larga de ObjEffect
que incluye desmontaje, búsqueda, reconexión y propagación de error. Queda
bloqueada en el registro Dataflow que materializa los dos extremos.

**Única siguiente investigación recomendada:** seguir `sndAsyncDataflowMsg`
de `libBizFw.so` hasta la cola/servicio que atiende `_MSG_PIN_GET` y enumerar
su dispatcher de opcode `0x1000`.
