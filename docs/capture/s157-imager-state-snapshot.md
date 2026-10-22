# S157 — `0x43859954` carga el estado para un snapshot

S157 clasifica otro xref a `0x43f72d02`. **VERIFICADO localmente:**
`0x43859954` carga el puntero desde el slot GOT `0x4401f990`; el xref a la base
es un edge `PARAM` (valor del puntero), no un acceso de escritura. `FUN_43859944`
lee `+5` y, cuando `r1 != 0`, `+0x0f`; sus stores del cuerpo van a otro global,
buffer y objetos distintos. No escribe `+3/+6` en este procedimiento.

## Instrucción y campos

Procedimiento contenedor `FUN_43859944`, cuerpo `0x43859944..0x438599cd`
(`ev_ec6f97762141815f395c4f95495973ab27f5327ae5c1aab1c33e5f7593780ece`).
En `0x4385994a/4e/52` forma `0x4401eee4`, suma `0xaac` y en `0x43859954`
ejecuta `ldr r2,[r4,r3]`, bytes `e2 58`, obteniendo `0x43f72d02`. El slot GOT
contiene `02 2d f7 43` (`ev_a2be1dc38d7278043336827bd87c0991eeccbd13742659906de531563db077dd`).

Las refs tipadas de `0x43859954` son: READ al slot `0x4401f990`, y PARAM/DATA
al valor `0x43f72d02` (`ev_34d9295f6218a4ff16b071ff3c48aabd51ee2f8280c09aeb46d5ca2e438bfc4d`).
El procedimiento luego:

- lee `[state+5]` y retorna temprano si el byte vale 1
  (`ev_7881d9e7228dfb57cfc851cb6d4882c6825f2ef1e8a9b2f54a0fcc10d8e5b7cf`);
- si `r1 != 0`, lee `[state+0x0f]` y evalúa bits `0x10/0x20/0x40`
  (`ev_26139718bebfe0c0ce0c3fb0e15c67f4f50a01ee534688889d39b746b96c0ca7`);
- guarda `arg0` en `0x43ef3f84` y produce/copias de bloques hacia el buffer
  `arg1`; ningún store del cuerpo usa `state+3` o `state+6` como destino.

La función aparenta preparar un snapshot/volcado condicionado por bytes de
estado; no se atribuye efecto sobre la programación del sensor ni se demuestra
que se ejecute en una captura. Esto elimina solo este procedimiento como
escritor de los dos gates.

```sh
python3 analysis/s157_imager_state_snapshot/verify_snapshot_ref.py
python3 -m unittest tests.test_s157_imager_state_snapshot -v
```

La salida contiene instrucciones Thumb decodificadas de los rangos originales,
con `file_offset=VA−0x43541000`. No es una afirmación global de ausencia:
copias de bloque, alias o writers en otros xrefs siguen abiertos.
