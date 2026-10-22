# S159 — `0x4386001c` también derrama el puntero, no escribe el estado

S159 clasifica otro xref de `0x43f72d02`. **VERIFICADO localmente:**
`FUN_4385fff0` lee el slot GOT `0x4401f990` (`0x43f72d02`) y en
`0x4386001c` ejecuta `str r3,[sp,#0x1c]`, guardando el puntero en stack. La
referencia DATA a la base no representa un store sobre el objeto. El cuerpo
lee varios campos, incluidos `+0x00`, `+0x1c` y `+0xa2`, y escribe a otros
destinos. No toca `+3/+6` en este procedimiento.

## Evidencia

- Cuerpo REA no contiguo `FUN_4385fff0`: `ev_5b0f148005650c3e22de895825765d726859466967149bcff370c3d43ddd1f73`.
- Instrucción `0x4386001c` y bytes `07 93`: `ev_3c2f0fbe550810719bf22e531025709d7c0ca323e91ab8635e60f9afca166181`.
- Referencias tipadas del cuerpo (`DATA` a valor de estado; WRITE real a stack/otros objetos): `ev_eb099b43bb1c2559ab27672e7a60d390533927b72af8b8a486614aaee8090843`.
- El slot `0x4401f990` contiene `02 2d f7 43` = `0x43f72d02` (`ev_ef0ae04fe4e640945736ea7bd40211f7cbdc4dbc7865e58ec0051c994f67bc7f`).
- Un caller estático `FUN_437b5d30` pasa un segundo argumento `0x43e17aa0`, no la base del estado (`ev_834e1efc6cdb2d2fc89e38963b8bea30d8c8fc2958eb176451469ce09f63fa3f`). Por ello un `param_2+6` observado en esta ruta no es `state+6`.

No se infiere ausencia global: el análisis se limita a este cuerpo y a su
caller observado; otros aliases, copias de bloque o writers permanecen
posibles. Tampoco se conoce el valor runtime del objeto BSS ni el efecto físico
de sus campos. S51 no cambia.

```sh
python3 analysis/s159_imager_state_ref/verify_state_spill.py
python3 -m unittest tests.test_s159_imager_state_ref -v
```
