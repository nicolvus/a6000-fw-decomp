# S142 — inicialización directa y lector indirecto del banco S

S142 resuelve únicamente las dos referencias REA directas al objeto
`S=0x43eb35d0`. **VERIFICADO:** una referencia limpia todo el struct; la otra
lee un campo `u16` y lo consume fuera del objeto. Ninguna demuestra el escritor
runtime del selector `S[0]` ni la producción de filas. S51 no cambia.

## VERIFICADO — xrefs directos al objeto S

REA `xrefs(0x43eb35d0)` devolvió dos sitios (`ev_c003561cd210577dc1bc7acc5d8edee0f20991a28f194009e2bd8d4f278b19ab`):

1. **`0x437b56b4` (`FUN_437b5614`) — inicialización por cero.** Carga el puntero
   S desde GOT slot `0x44020c9c` (el literal vale `0x43eb35d0`); inmediatamente
   se prepara `r1=0`, `r2=0x148` y se llama al llenador `0x439c5a04`. REA
   documenta en ese helper un bucle de stores del byte `r1` sobre `r2` bytes.
   Así queda probado el borrado de `0x148` bytes de S, incluido `S[0]`; no es
   evidencia de un valor no cero elegido por modo. Evidencias: instrucción
   `ev_e0b62a63903160cf0bf90805dd0357b627a3fe81a3e40ac39ca1739873d08c11`,
   inmediato `0x148` `ev_d8d71e4de5483568c3c036c1bce06f11f75bc6d9407bb5d521adef1c4dc60524`,
   helper `ev_8a45cdfbf6e32572561030a07c080dafe97ef7547eff2e4b01c12d8c92704548`.

2. **`0x437b59ce` (`FUN_437b59b8`) — consumo de `S+0xda`.** Carga el mismo
   puntero y llama al thunk `0x43b08748`, que ejecuta `ldrh.w r0,[r0,#0xda]`
   y salta a `0x4383c638`. Ese valor se almacena en campos de otros objetos,
   no en S. Evidencias: sitio `ev_fad95d45f02ce9fefe4c781e6171f24f2d92a4837d020112acf9eef306fd0fe1`,
   lectura `ev_c838a9880024f08cb29f6c88ee8b3f44fed6de73710f575e59e165f87b1dbd85`,
   salto `ev_c341096bc3b0eefcca95026fb741cbbca30a92426edc6a7d3585bdddf836e80a`,
   stores consumidores `ev_073858f61d433701988ad11013df278a67348acbf8f5e9d7fd09a23837ef915c` /
   `ev_10ba471a7361a6992a7e8495be9c1e438e4b885c5e82653b898052612ff9ea8f`.

REA lista los mismos dos puntos para el slot GOT `0x44020c9c`
(`ev_560e05d9e5c35f5e81e8989aa153111798f1de7b045480af0712ca8f3212860d`).
La ausencia de más xrefs **no** prueba que no haya escritores: las funciones
que reciben `S` por argumento no tienen por qué referenciar el GOT.

## PARCIAL — conexión con S140/S141

Esto confirma el reset a cero de S, pero no contradice la selección de fila
verificada en S141: el reset explica el estado inicial observado; no establece
el valor posterior del selector. `0x43b08750` recibe S como argumento, lee
`S[0]` y llama al selector/copier, así que el acceso no aparece como xref de
GOT. Del mismo modo, `0x43843a44` sigue siendo solo un candidato de staging:
REA no lo resolvió como función en la sesión y su contenido runtime permanece
abierto.

```sh
python3 analysis/s142_imager_s_init/verify_s_accesses.py
python3 -m unittest tests.test_s142_imager_s_init -v
```

La reproducción recorta bytes del binario A6000 fw3.21 por
`file_offset=VA−0x43541000`, desensambla Thumb y fija el SHA-256 esperado; los
rangos están en `analysis/s142_imager_s_init/s_accesses.json`. Los xrefs
estáticos son observaciones del análisis REA/Ghidra, no de ejecución. Pendiente:
seguir los escritores que reciben S como parámetro, sin inferir ausencia por
xrefs vacíos y sin atribuir significado físico a `S+0xda`.
