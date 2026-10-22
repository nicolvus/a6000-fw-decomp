# S154 — el xref `0x438363e6` carga el objeto de gates, no lo escribe

S154 clasifica uno de los xrefs directos a la base de estado `0x43f72d02` que
S153 dejó como candidato. **VERIFICADO:** `0x438363e6` carga el puntero desde el
slot GOT `0x4401f990`; el edge hacia la base es tipo DATA (el valor cargado), no
un write ni un acceso de memoria a esa base. El procedimiento contenedor lee
otros bytes del estado y modifica objetos/buffers distintos; no tiene stores a
`+3` ni `+6` demostrados. Esto elimina **este sitio**, no todos los escritores.

## Instrucción y resolución

`FUN_438363cc`, cuerpo no contiguo `0x438363cc..0x4383648b` y
`0x43836490..0x438364f3` (Evidence `ev_ba11d58bc35a846b8fcafce749d1cdcbc39722c2b6a6906b01e0f3d406f4a122`),
resuelve el literal al GOT `0x4401eee4`; añade `0xaac` y ejecuta
`ldr r0,[r5,r3]` en `0x438363e6`. El slot `0x4401f990` contiene bytes
`02 2d f7 43`, es decir puntero little-endian `0x43f72d02`. Bytes de la
instrucción y del slot: `ev_c9939d01d34e5b049db673e8fa458d42de0943ca729f1af0a281f99ab317f3ee`,
`ev_ef0ae04fe4e640945736ea7bd40211f7cbdc4dbc7865e58ec0051c994f67bc7f`.

REA `procedure_references` conserva dos edges en ese mismo sitio
(`ev_e8a264c61f10ca8c40c32e8171a4b743ec4bfa571f23898386dd5ab4a8ec7efa`):

1. `0x438363e6 → 0x4401f990`: READ, `read=true`, `write=false` (slot GOT leído).
2. `0x438363e6 → 0x43f72d02`: DATA, `read=false`, `write=false` (referencia al
   valor que representa la base del objeto; no un acceso a esa VA).

## Campos y stores del procedimiento

Con el puntero cargado en `r0`, el cuerpo lee `[r0+0x3a]`, `[r0+0x39]`,
`[r0+0x3b]` y `[r0+0x38]` (lecturas en `0x438363e8`, `0x43836404`,
`0x43836412`, `0x4383647e`). Son campos distintos a los flags `+3/+6` de
S153. Los stores del cuerpo van a otras bases/objetos (`0x43e19290..`), al
buffer de salida `param_2`, y a contadores globales `0x43f9b4dd/de`; las
referencias tipadas del procedimiento no muestran writes a `0x43f72d05` ni a
`0x43f72d08`. Listing completo de este cuerpo en
`ev_98aa775d3c95df94438bb40d89c729bddd5b0493c30968d146bfee6243fb3c63`.

La ruta además llama a `memcpy` `0x439c5320` sobre una tabla de 20 bytes hacia
stack local; no es una copia sobre el objeto de flags. El caller estático
observado es `0x4383a82c`, pero su estado de ejecución no se infiere.

## Conclusión y límite

**VERIFICADO localmente:** este xref adquiere el puntero por GOT y es lector de
`+0x38..+0x3b` únicamente; no escribe `+3/+6`. **PARCIAL global:** quedan los
otros xrefs a la base, escrituras de bloque/alias y posibles rutas no
decodificadas. El valor slot/estado de la imagen no prueba su valor runtime.
No se cambia S51 ni se asigna semántica física a los flags.

```sh
python3 analysis/s154_imager_state_ref/verify_state_ref.py
python3 -m unittest tests.test_s154_imager_state_ref -v
```
