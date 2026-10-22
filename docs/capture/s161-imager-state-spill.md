# S161 — `0x4384cb0a` es un spill del puntero a estado

S161 clasifica dos xrefs del procedimiento `FUN_4384b268`. En `0x4384cb06` se
carga `0x43f72d02` desde GOT; en `0x4384cb0a` se ejecuta
`str r3,[sp,#0x20]`. El segundo edge a `0x43f72d02` es propagación del valor,
mientras el WRITE tipado efectivo es al stack. No se modifica el objeto en ese
sitio.

## Uso posterior del puntero

El procedimiento recarga el puntero del stack y lee los campos `+0x40`,
`+0xa5` y `+0x42`; no hay load/store a gates `+3/+6` en el cuerpo. Sus stores
registrados se dirigen a `0x43f7d1ca` y otros destinos, no a la base
`0x43f72d02`. En particular, un store relativo `+6` de esta función puede ser
al objeto destino `0x43f7d1ca`, no al bloque de flags.

REA Evidence del procedimiento:
`ev_1e8e048eb0f0141cf4d85e3688d89fe80dba6b0653e5ad1a7171f615be7c3de4`;
typed ref del load `ev_d4025f0b945b5cb7b78c5d9cc83524a9b740a27a939c671a69cd8d903f897061`;
typed ref del spill `ev_92b61d8fa023614fa3a5d727782551016292e79dbeeec8e093567b03cf125a06`;
refs salientes del cuerpo `ev_3303b18d85c46c4e2f17bbd020bc6d05f0c6ea1dcb7fee814e779e672f12ab01`.
Slot `0x4401f990` = `02 2d f7 43` → `0x43f72d02`
(`ev_a2be1dc38d7278043336827bd87c0991eeccbd13742659906de531563db077dd`).

Esta clasificación elimina un xref de la lista como posible writer de los
gates, pero cubre solo `FUN_4384b268`; no excluye copias, alias, DMA u otros
procedimientos. Los valores runtime no se conocen y no se asigna semántica
física. S51 intacto.

```sh
python3 analysis/s161_imager_state_spill/verify_state_spill.py
python3 -m unittest tests.test_s161_imager_state_spill -v
```
