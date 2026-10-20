# S39 — enum de imagen: discriminador APL y origen configurable

18-10-2026. Análisis estático de av-cam, sin ejecutar firmware, cámara,
flasheo, instalaciones ni push. **PARCIAL:** se cierra la ruta directa del
resultado convertido como discriminador de cambio; no se identifica un
formato de píxel ni un pitch real.

## VERIFICADO — método e integridad

Leídos CURRENT, CONTEXT, frontera S38 y secciones pertinentes S33/S34;
`search.py claim` sin correcciones registradas para S33/S34/S38. La ausencia
de relaciones no garantiza ausencia de correcciones en prosa.
Original de 11427236 bytes, base lógica `0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Cada export compara hash y todos los bytes cargados antes de escribir.

Único proyecto: `analysis/ghidra/silent-liro.gpr`, `-readOnly -noanalysis`.
`S39Export.java` consulta funciones/instrucciones existentes: no define
funciones, cambia contexto, divide memoria ni abre transacciones. Los pools
PIC permanecen mutables; el pseudocódigo conserva expresiones DAT que se
contrastan con los literales del blob y el listado. No se toman tipos de
Ghidra como ABI demostrado. Los manifiestos S38 coinciden antes de abrir
el proyecto y se vuelven a comprobar al terminar.

## VERIFICADO — consumidores directos del resultado APL

Evidencia primaria: `analysis/ghidra/s39-initial.json/.c`,
`s39-consumers.json/.c`, `s39-format.json/.c` y `s39-registers.json/.c`.

| Paso | Sitio exacto | Operación |
|---|---|---|
| Tres llamadores del conversor | `43814ec8`, `438153b8`, `43815738` | Resultado bajo R0 en config temporal `+0xc`; funciones `43814ea0`, `43815210`, `43815560` |
| Preparación común | `4387a1fc→4387a758` | Se entrega ese bloque antes de configurar direcciones |
| Copia anterior | `4387a776/4387a77a` | `[43ef71a0]=[43ef71a4]` |
| Copia actual | `4387a7a2/4387a7a8` | `[43ef71a4]=[config+0xc]` |
| Único lector adicional recuperado | `4387a23c→4387a6c4`, lectura `4387a6ca` | Traduce grupos APL `0/1/2/3` a `0/1/2/4` |
| Caché por unidad | `4387a6ee→436bec28` | Compara y actualiza `[43e77ccc+unidad*4]`; devuelve 0 si cambió, 1 si igual o estado/propietario inválido |
| Cambio aceptado | `4387a244→43acb7be` | Solo si retorno 0: `436bd3f4` y `436bd7d8`, invalidación/reinicialización de estado |

La TBB `4387a6d0` tiene bytes `02 04 06 08` en `4387a6d4`;
destinos `4387a6d8/dc/e0/e4`, instrucciones `movs r3,#0/1/2/4`.
El descompilador no resuelve la tabla; el listado y los bytes sí.
`436bec54/5c` comparan/escriben el valor cacheado. `43acb7be` no recibe
el enum como argumento: recibe el propietario APL.

| Enum P+1b4 | input+38 (remapeo S33) | Grupo APL | Caché | Píxel / pitch |
|---|---|---|---|---|
| 0, 3, 5 | 2, 5, 4 respectivamente | 0 | 0 | NO_VERIFICADO |
| 1 | 0 | 1 | 1 | NO_VERIFICADO |
| 2 | 1 | 2 | 2 | NO_VERIFICADO |
| 4 | 3 | 3 | 4 | NO_VERIFICADO |

El conversor APL lee P directamente: sus índices no son los ya remapeados
en input+38. Son dos conversiones distintas desde el mismo origen.

`436bd3f4` pone un byte de estado a cero. `436bd7d8` selecciona perfiles
con el **otro** selector `[43e78bfc+unidad*4]`, llama `436bf360`,
`436bf588` y `436bf43c`. El primero copia un par de palabras de una tabla
por perfil; el segundo cierra/desactiva referencias DMM; el tercero limpia
flags. No se observa que el valor cacheado sea un índice de esa tabla.
`43acb946` calcula el otro selector a partir de dimensiones y una condición
auxiliar; `436bef2c` lo conserva. Compartir números 0/1/2 no los identifica.

**ACEPTO:** agrupación utilizada como discriminador de cambio APL.
**RECHAZO:** interpretar `0/1/2/4` como bits hardware, ancho de palabra,
stride o nombres de formatos basándose en esos números.

## PARCIAL — relación con MMIO, geometría y cobertura

`43814ea0` usa dos bloques diferentes: el config con enum va a
`4387a1fc`; el bloque de direcciones va después a `436be554`, y finalmente
`436bdbfc` programa MMIO. En la ruta recuperada **no se pasa el resultado
de 43814d24 como campo del segundo bloque**. S34 sigue siendo evidencia
de programación de direcciones/kick, no de semántica de píxel.

Los escritores iniciales `436bfa88`, `436bfab0`, `436bfad8` de la secuencia
`436bdbfc` usan bancos `f3850000/f3950000/f3a50000` y offsets `0/10/14`;
sus entradas son campos del bloque `43e78a9c+unidad*ac`. Los bancos de
direcciones `…0400` son otra parte de la configuración. No se recuperó
un enlace del discriminador cacheado a esos campos ni a un cálculo de pitch.

Cobertura: xrefs existentes de globals actual/anterior/caché, referencias
PIC por carga literal seguida de `add reg,pc` a menos de 128 bytes, búsqueda
de bases vecinas `43e77c00..43e77cff` y seguimiento de llamadas recuperadas.
No hay punteros absolutos literales a `43ef71a4`, `43ef71a0` o `43e77ccc`
en el blob, incluso desalineados. La global anterior tiene solo la escritura
referenciada; la caché solo comparación/escritura en el setter recuperado.
Esto **no prueba ausencia universal** de lectores: quedan alias, bases con
desplazamiento, construcciones aritméticas, código no definido y llamadas
indirectas. No se declara agotado todo el análisis estático del enum.

## PARCIAL — cadenas de formatos y tablas vecinas

Barrido ASCII del blob con xrefs Ghidra para YUV, 422/420, RAW, Bayer,
planar/packed y variantes 8/10/12 bit, además de EnumConverter y sapl.
Resultados íntegros en la clave `strings` de los exports; no se buscaron
solo nombres ya esperados en una función.

| Cadena | Dirección / xref | Evaluación |
|---|---|---|
| `./Utility/EnumConverter.h` / sufijo `EnumConverter.h` | `43cb0bb5` / `43cb0bbf`; xrefs del sufijo en `s39-consumers` | El sufijo es compartido por 43814d24 y conversores vecinos 43814d74/db4/e04/e44; nombre de archivo, sin tabla de nombres de píxel |
| `RAW_FULL` | `43cb4c92`, sin xref recuperada | No identifica un índice del conversor |
| `No RAW_FULL handle` | `43cb088a→4380bc02` | Ruta RawParse vecina, sin enlace demostrado al mismo índice APL |
| `Cannot read with skipping when 4bit RAW` | `43c90765→436c2c76` | Otro consumidor; no establece equivalencia con los seis valores |
| `N3VDF28VfxRgba8888ToYuv422ProcessorE` | `43c8bf52`, sin xref recuperada | RTTI de VDF; no tabla APL |
| `[input_yuv.input_main/sub]…` | `43c82b55/2b8b/2bd1/2c06`, sin xrefs recuperadas | Logs de direcciones/geometría; no nombran los índices |

Los logs `sapl_SetDmaAddr…` sí pertenecen a `436be554`, pero nombran
destinos de memoria, no formatos de píxel. Proximidad en ROM y vocabulario
YUV/RAW no demuestran identidad de contexto. **NO_VERIFICADO:** tabla
nombre↔índice, subsampling, orden de bytes, planos y profundidad.

## VERIFICADO / PARCIAL — escritores anteriores al objeto P

Evidencia: `s39-registers` consulta `43793400`, resuelta al contenedor
completo **VD_Pre 43792a0c**. No reutilizar `43792fb4` como nueva entrada:
es consulta interior. El listado fija `r7=43e9b548` en `4379347a` y
`r8=43e99208` en `4379347c`. El getter `4378f9c0` devuelve `43e9baec`;
su `+28` es `43e9bb14`, escrito como `r7+5cc`.

| Rama / escritura | Origen observado | Clasificación |
|---|---|---|
| Selector `(byte[r7+808]>>4)&3` igual a 2; `437934b4` | Si `[context[1]+10]==[context[0]+20]`, copia `[context[0]+24]` a `43e9bb14` | VERIFICADO: valor de contexto, no constante |
| Ramas generales; `4379357c` | Elige `[r7+48]` o `[r7+458]` según `43794a44(context)`; remapea 0→0,1→1,2→2,3→4 | VERIFICADO: selección condicional |
| Selector igual a 1; `437935aa` | Fuerza formato 0 y también `[r7+48]=0` | VERIFICADO: caso fijo local |
| Misma rama, condición 43794a44 verdadera; `437935ea` | Sobrescribe con remapeo de `[r7+458]` | VERIFICADO: puede sustituir el cero |

`43794a44` comprueba bit 7 de `context[2]+269` y rango 1..4 de
`context[0]+450`, consultando una tabla de bytes. Esto prueba dependencia
de estado/modo software; **no** una opción concreta de tamaño de imagen o
FPS elegida por el usuario. Tampoco se ha probado que todas las ramas sean
alcanzables en una A6000 real.

**VERIFICADO — identidad del contexto:** `s39-context` exporta
`43ae8d56(root,context)`: guarda `context[0]=root`,
`context[1]=root+560`, `context[2]=root+5a4`.
`4378fa70→43ae8eae→43ae8d56` lo inicializa con root `43e9b548` y
context `43e99208`; por tanto `context[2]=43e9baec` y el campo es
exactamente `43e9bb14`. Los argumentos se contrastan con los pools
`4378fd64` y `4378fd70`, más PC `4378fa90` y `4378fb8e`.
Los selectores anteriores son `context[0]+48/+458/+24`; sus escritores
finales y copias completas de estructuras siguen **PARCIAL**, sin vínculo
cerrado con una solicitud de usuario ni con FPS.

## Pendiente real y próximo paso exacto

No hay asociación inequívoca valor→formato de píxel/stride. **PARCIAL**
el enum; **NO_VERIFICADO** nombres y contrato raster. La ruta directa del
resultado convertido está cerrada hasta caché/invalidation, sin un campo
hardware encontrado. No es prueba de que el enum carezca de significado
gráfico en otras rutas, ni frontera estática universal agotada.

Próxima acción local: seguir el origen de `context[0]+24`, `43e9b590`
y `43e9b9a0`, incluidas copias masivas, hasta
una tabla/solicitud tipada. Si no aparece nombre inequívoco, conservar los
valores numéricos. Seguir la configuración que genera geometría/pitch real
independientemente del discriminador APL; no reabrir los 26 AllocShare.

La incógnita más relevante de S31–S39 para captura completamente electrónica
sigue siendo **el productor físico de un cuadro y su cierre de integración**:
misma tupla handle/clave/VD desde asignación y adquisición a fin DMA y EC/LM.
El backend DMM necesita resolver el binding LIRO fuera de av-cam (S38);
APL→IRQ/VD necesita evidencia hardware adicional (S35). Dar nombre al enum
no demostraría ese ciclo. No se ejecuta esa salida del alcance en S39.

## Validación

Auditor `analysis/ghidra/s39-audit.py`: primero falla por findings ausente;
después comprueba hash, literales PIC, destinos TBB, estado de los exports y
manifiestos persistentes; imprime tabla clasificada en stdout. Las consultas
sin función conservan solo listado, sin inventar pseudocódigo ni entradas.
Resultados finales de lint, índice e integridad se registran en PROGRESS S39.

**VEREDICTO: CAMBIOS** para cerrar el significado real de píxel; se acepta
la ruta directa de discriminación y las escrituras condicionales demostradas.
