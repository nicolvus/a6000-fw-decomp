# S163 — tercer helper lee `state+0x1c/+0x1e` y genera un mensaje

S163 cierra la referencia `0x438d93aa` que S162 dejó pendiente. `FUN_438d939c`
resuelve el state pointer desde GOT y lee un `u16` en `+0x1c` (`0x438d93aa`)
y un byte en `+0x1e` (`0x438d93ac`). Si son cero, usa defaults 3 y 4 en el
payload del mensaje. El cuerpo escribe resultados a contadores/objetos
`0x43f7c708`, `0x43f7c70a` y `0x43eff43c`, no al estado ni a gates `+3/+6`.

## Uso observado

REA evidencia de las instrucciones: `0x438d93aa` es
`ldrh r7,[r3,#0x1c]` y referencia READ a `0x43f72d1e`
(`ev_3d73989ad3bf9bf698d74295d05425993f61317c5abb3c491511a3a71c5f800e`);
`0x438d93ac` es `ldrb.w r8,[r3,#0x1e]`, READ a `0x43f72d20`
(`ev_acf64d0ce0966ca85e468761ddb57b8dd267b30031d509fc210fabec25001053`). El
state pointer se obtiene del slot `0x4401f990`; después los dos campos se
condicionan individualmente (cero → valores 3/4) y se empaquetan como campos
de mensaje.

El cuerpo usa `FUN_438d9288` y rutas OSAL para publicar el registro de evento.
Que esto sea telemetría diagnóstica de los modos es **INFERENCIA**, no efecto de
control del imager. No se ejecutó el firmware; las llamadas/callers estáticos
no establecen que el mensaje aparezca durante una foto.

## Escrituras y límites

Las referencias salientes de `FUN_438d939c` (`ev_0a887b1bd052d8b3d5b4d678910ef9808acc4c0ec7648dab3c13fc020e0fc190`) sitúan los stores en
`0x43f7c708`, `0x43f7c70a`, `0x43eff43c` y el buffer de mensaje; no en
`0x43f72d02`. Los campos `+0x1c/+0x1e` están a cero en el blob, de modo que sus
valores de ejecución son **NO_VERIFICADOS**. Hay límites en los callers y en
otras rutas/alias; no es una afirmación global sobre writers de estado. S51 sin
cambios.

```sh
python3 analysis/s163_imager_state_event_reader/verify_state_event.py
python3 -m unittest tests.test_s163_imager_state_event_reader -v
```
