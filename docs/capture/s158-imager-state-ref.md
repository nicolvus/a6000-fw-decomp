# S158 — xref `0x4385b268` es un spill del puntero del estado

S158 clasifica el sitio `0x4385b268` de la lista S153. **VERIFICADO localmente:**
el procedimiento contenedor `FUN_4385b234` carga el objeto de estado desde el
GOT, lee algunos campos de él y en el xref investigado hace `str r3,[sp,#0x20]`:
guarda el puntero en la pila para reusarlo. El edge DATA a `0x43f72d02` es el
valor del registro, no un write a la base. Este procedimiento no escribe los
gates `+3/+6`.

## Resolución del xref

- El cuerpo tiene dos rangos REA `0x4385b234..0x4385b2c9` y
  `0x4385b2fe..0x4385bed9`; Evidence `ev_633b2499c1f64a98ef9dd1dee3a8785a4eb185e877a01886c8f80b10ecfb5551`.
- `0x4385b25e` carga literal `0xaac`; `0x4385b262` carga `[r4+r3]`, que es
  slot `0x4401f990` con valor `0x43f72d02`; luego `0x4385b268` almacena el
  registro en `[sp+0x20]`. Instrucciones completas `ev_6dc087d973990a3aeaf9d67b413d3bff80620de2a4a88e4b9cb9350c82ab0bbb`; refs tipadas `ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d`.
- El edge en `0x4385b268` a `0x43f72d02` es PARAM/DATA (valor cargado); el
  write efectivo de la instrucción es el slot de pila. El GET real al GOT es
  `READ` en `0x4385b262`.

## Campos y stores observados

Después del spill, este cuerpo lee `[state+0x28]`, `[state+0x26]` y
`[state+0x29]`; no carga `state+3` ni `state+6`. Sus stores del camino local
van al objeto de configuración `0x43f7d1ca` (campos `+0,+2,+4,+6,+8,+0xa`),
al buffer temporal y a otros destinos; el `+6` de ese otro objeto no es
`state+6`. No se observan stores a `0x43f72d05/+0x08` en `FUN_4385b234`.

La copia de tabla de 20 B va a un buffer en pila; no se copia sobre el objeto
de gates en este procedimiento. No se siguen todos los callees ni se infiere
una ausencia global. Los 32 B iniciales del objeto están a cero en el blob y
eso tampoco demuestra su valor runtime. **S51 no cambia.**

```sh
python3 analysis/s158_imager_state_ref/verify_gate_accessor.py
python3 -m unittest tests.test_s158_imager_state_ref -v
```
