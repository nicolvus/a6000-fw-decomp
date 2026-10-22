# S313 — Síntesis del carril B: qué distingue el silent shutter de la A7S (estado actual)

Sesión de consolidación. Reúne los resultados de S300–S312 (todos con evidencia en
`analysis/`) y separa lo demostrado de lo que queda abierto. **No introduce afirmaciones
nuevas**: cada fila remite a su informe.

## 1. Lo que queda demostrado

| # | Afirmación | Evidencia | Sesión |
|---|---|---|---|
| 1 | El objeto de estado de la A6000 es `0x43f72d02` (slot GOT `0x4401f990`); el de la A7S es `0x43f7bce6` (slot `0x440251e4`), ambos en el índice 18 de su tabla de punteros | bytes + REA | S300, S301 |
| 2 | En la A6000 hay **67** referencias al estado; **ninguna** escribe `+3`/`+6`; los gates se leen como bitfield de 7 bits + signo (8 lectores cada uno) | 67 sitios re-decodificados | S300 |
| 3 | En la A7S hay **79** referencias; los gates `+3`/`+6` son **idénticos** (mismo código, mismas máscaras, cero escritores) | diff de instrucciones + 79 sitios | S301 |
| 4 | Los únicos stores al estado A6000 son a `+0x00` (1) y `+0x02` (4) | instrucciones + bytes | S300 |
| 5 | La A7S añade escrituras a `+0xde` y `+0xe6/+0xe8/+0xea` y lecturas de 11 campos que la A6000 no usa | 79 sitios | S301 |
| 6 | La función de comprobación de parámetros desplaza **todos** sus offsets (ctx +8, `VdNum` +0xc, `svr_num` +0x10) y copia 3 palabras en vez de 4 | instrucciones en ambos blobs | S302 |
| 7 | La A7S usa una indirección modo→columna (34 códigos `0x43fee370`, mapa `0x43c9c5b5`) sobre 69 filas×16 B; la A6000 usa columna directa sobre 59 filas (`0x43fe9b74`) | bytes | S302 |
| 8 | Los modos `0x4e/0x4f` comparten **columna 1** con `0x4c/0x4d` en el accesor de registros: la matriz no distingue el silent | mapa de bytes | S302 |
| 9 | La tabla `0x43ff3200` tiene **148** entradas (no 60), estado en índice 18; su único literal es el slot GOT `0x4401f080` | recorrido + bytes | S303 |
| 10 | El dumper de gates tiene **2** callers directos (`0x43859868/92` en `0x43859710`); éste recibe 10 llamadas de 7 funciones; `FUN_43859944` tiene 35 | escaneo BL exhaustivo + REA | S303 |
| 11 | Las escrituras A7S `+0xde` y `+0xe6..+0xea` están en funciones cuya firma de store **no existe** en la A6000 | firmas de 24 B | S307 |
| 12 | El bloque de tiempos es `FUN_438645bc` (no `…be`) con un único caller `0x43861be4` | instrucciones | S307, S308 |
| 13 | El resultado del selector va a un **thunk de llamada virtual** (`vtable+0x64`), no a un mensaje | desensamblado | S308, S310 |
| 14 | Las **7** funciones de la cadena silent/config A7S tienen 0 coincidencias (24 B) en la A6000 | firmas | S309 |
| 15 | La ruta de configuración A6000 también es propia: 2 de sus 4 writers no están en la A7S | firmas | S311 |
| 16 | Los **6** consumidores del cluster A7S son también código exclusivo | firmas | S312 |

## 2. Lectura de conjunto

El silent shutter de la A7S **no** se activa por los gates `+3`/`+6` del estado (idénticos y
sin escritor en ambas cámaras) ni por la matriz de registros por modo (los modos silent
comparten columna con `0x4c/0x4d`). Lo que la A7S tiene y la A6000 no es:

1. un **selector de drive mode** con el parámetro `tipo` (`0x43826d58`: `tipo==2` → `0x4e/0x4f`);
2. un **subsistema de tiempos/configuración** (`0x43548c70` → `0x43861a58` → `0x438645bc`
   → escritores del cluster `+0xae/+0xde..+0xea`), con consumidores propios;
3. una **matriz de registros** con indirección modo→columna y 34 códigos.

Esto es coherente con S204 (silent = drive mode + tabla de timings) y con S169 (sin capa
`CheckSet*`). **No demuestra** que el cluster sea el mecanismo físico ni que el IMX210 no
pueda hacerlo: S51 sigue en A=NO, B=NO, C=NO.

## 2b. Sesiones paralelas y correcciones

Durante el carril corrieron dos procesos del agente B sobre la misma cola. Las sesiones
`S304` y `S305` (rev.1) quedaron **supersedidas**: usaban direcciones desplazadas +0x58
(`0x438581e8` por `0x43858190`, `0x43858390` por `0x43858338`) y contaban 60 entradas en la
tabla `0x43ff3200`. S303 rev.2 y S309 corrigen ambas cosas con evidencia de bytes. `S306`
quedó absorbida en S303 §2b (usuarios del slot `0x4401f080`).

## 3. Lo que queda abierto (NO_VERIFICADO)

| Pregunta | Por qué no se cerró |
|---|---|
| ¿Qué objeto/vtable es `r0` en `0x43549084` y qué hace el slot `0x64`? | requiere resolver el objeto (constructor/RTTI) y el despacho virtual |
| ¿El modo `0x4e/0x4f` llega al bloque de tiempos? | no hay llamada directa; podría ir por valor en una estructura intermedia |
| ¿Qué contiene la tabla de tiempos `0x43fee3f8` (19 filas)? | no se identificó su índice ni su consumidor |
| ¿La A6000 puede hacer silent con otro código? | no hay equivalente identificado; la ausencia de firma no prueba incapacidad |
| Semántica física de `+0xae/+0xde/+0xe6/+0xe8/+0xea` | sin datasheet ni traza |

## 4. Reproducción

```sh
for d in s300_state_xref_sweep s301_a7s_state_xref_sweep s302_drive_modes s303_ref_tree \
         s307_a7s_writers s308_silent_flow s309_chain_presence s310_vtable_thunk \
         s311_a6000_config s312_cluster_consumers; do
  python3 analysis/$d/*verify*.py || exit 1
done
python3 -m unittest tests.test_s300_state_xref_sweep tests.test_s301_a7s_state_xref_sweep \
  tests.test_s302_drive_modes tests.test_s303_ref_tree tests.test_s307_a7s_writers \
  tests.test_s308_silent_flow tests.test_s309_chain_presence tests.test_s310_vtable_thunk \
  tests.test_s311_a6000_config tests.test_s312_cluster_consumers
```

**Límite global:** todo es análisis estático de los blobs; sin firmware ejecutado, sin
cámara, sin flasheo y sin pruebas físicas.

---

## Actualización posterior (S314)

La pregunta abierta «¿Qué contiene la tabla de tiempos `0x43fee3f8` (19 filas)?» queda
**corregida por S314** (`docs/capture/s314-selector-object.md`): en la A7S `0x43fee3f8` es un
array terminado en NULL de **95** punteros a registros de 6 B (`u8 dev | u8 0 | u16 reg |
u8 data | u8 0`), no una tabla de 19 filas; en la A6000 la misma VA pertenece a otra tabla.
También se corrige que el thunk del slot `0x64` es `0x43ad96f8` (no `0x43ad9704`).
