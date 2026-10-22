# S149 — helpers del builder no rellenan el hueco de cada fila

S149 audita los callees de `0x4383bf2c` y corrige una lectura equivocada de la
primera respuesta S149: **`0x4383c9dc` sí itera cuatro veces y escribe las
cuatro filas** en una invocación (S147 ya tenía el stride y las cuatro vueltas).
La respuesta inicial de este hito confundió el primer cuerpo con el total del
loop; el CFG/bytes del cierre del loop demuestran que no retorna tras la primera
fila.

## VERIFICADO — cuatro filas, no una

REA `read_function_instructions` de `0x4383c9dc`
(`ev_05541f7fa796e9902a584d283765f42028aa618772a3ece2a2b2e519b172211b`) y los
bytes originales comprueban:

- `mov r4,r1` fija la base destino y `movs r0,#4` / `str r0,[sp,#0x10]`
  inicializa contador 4 (`0x4383c9e0..0x4383c9f0`).
- Al final del cuerpo `0x4383cbfc adds r4,#0x10`; luego decrementa y guarda el
  contador, `cmp r3,#0` y `bne.w 0x4383c9f2` (`0x4383cc00..0x4383cc08`).
- El epílogo de retorno ocurre en `0x4383cc0c..0x4383cc10`, después del loop.

Por tanto, se recorren las cuatro bases `filas+0x2c`, `+0x3c`, `+0x4c`, `+0x5c`.
En cada fila esta función tiene stores relativos a `0,4,6,0xa,0xc,0xe`; no hay
store a `+8/+9` dentro de `0x4383c9dc`. Las páginas REA de pseudocódigo son
`ev_d4653d3615add43984db5b04eb31c812b23d2a5865e6038908736caf291fd05a` y
`ev_9caa8366dd8aa3149c26482110e5523aa6132b3fd299d39fb05de95a2003380e`.
La segunda página llevaba a confusión si se leía el `return` decompilado sin el
back-edge de máquina.

## VERIFICADO — gates/efectos de helpers inspeccionados

`0x4383bf2c` pasa `r0/r1` a `0x4383c9dc`, después invoca
`0x4383b790`. Si `0x437284b4()==0`, llama a `0x4383bfd4`; adicionalmente llama
a `0x43b08786` solo si `[G+0x50]==2`. Otro gate, `[GOT+0xca]==1`, llama a
`0x4383c818` (y luego `0x4383bad0`). Evidence del builder:
`ev_5305a4dbabf37e02baec4bd8b258137d9e733c0817ce4b373defe5a8ecc12203`;
assembly view `ev_16b1b13434d0983e1e0a4ae53f4994b39195e15b25b571189089b9bd1b208b3b`.

En los cuatro cuerpos auditados, no se encontró un store dentro de las filas
`+0x2c..+0x6b` por parte de esos helpers:

| Helper | Efecto comprobado respecto a `filas` | Evidencia REA |
|---|---|---|
| `0x4383b790` | stores en cabecera/cola (`+0x28`, `+0x2a`, `+0x6e..+0x92`, etc.); otro helper copia `+0x00..+0x27` y `+0xf4` | `ev_f4e7ee8c49c2a05c87830ae4432cb9f89b76b505c258c1a4187a700113bf407c`, `0x43b0d16e`: `ev_754e831f6b38c1ac43d38480668cd9f8e06ea03645226d749cb771bfcd7deb23` |
| `0x4383bfd4` | no accede al puntero de filas `r1`; su `r0` es G, sin stores sobre filas | `ev_2840e01dbc3ca082d7dfffe4aad87e8760f3f806f2c0d323a950d1f800ce6355` |
| `0x43b08786` | lee campos `filas+0x2c/+0x32`; cuerpo sin stores | `ev_76117d450acd81c363f9fa8b4c4f5284f47263d347df63e76c6e2dec1348c88e` |
| `0x4383c818` | escribe `+0x6c` (tras la 4.ª fila) y `+0xbe/+0xc0/+0xc2`; no el interior de filas | `ev_c681e6e23a4263909564de62cee2a44c081686f7a2f295bec17542c813f643c3` |

Los bytes de fila pueden seguir siendo modificados por **otros escritores no
incluidos en estos cuerpos/gates**. `0x4383bad0` comparte el segundo gate y no
se ha examinado aquí exhaustivamente en todos sus callees. No se atribuyen
efectos físicos a los campos, ni nombre a las posiciones vacías. Silent
Shutter/S51 no cambia.

```sh
python3 analysis/s149_imager_row_helpers/verify_helper_stores.py
python3 -m unittest tests.test_s149_imager_row_helpers -v
```

El JSON contiene bytes y disassembly de Thumb del firmware original
(`offset=VA−0x43541000`). La conclusión se limita a la ruta/callees enumerados;
es estática, no runtime.
