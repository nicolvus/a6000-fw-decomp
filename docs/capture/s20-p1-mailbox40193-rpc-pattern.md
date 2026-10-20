# S20 — P1: patrón RPC real del buzón `0x40193` y el cliente CapIdTblMgr

Continuación directa del bloqueo más citado de sesiones 18-19
(`shutter-trigger-chain-0x3011.md`: "NO VERIFICADO: la tarea receptora de la
cola `0x40193`"). Alcance: `av-cam.bin`, proyecto Ghidra `silent-liro`
(solo lectura). Sin Codex, sin subagentes. Herramienta nueva de esta sesión:
`analysis/ghidra/FindScalarUses.java` (búsqueda de escalares inmediatos —
resultó con 0 aciertos para `0x40193` porque se carga desde literal pool,
no como inmediato de instrucción; se sustituyó por búsqueda de bytes crudos
+ `QuerySilentReferences.java`, que sí funcionó).

## Método

1. Búsqueda de la palabra de 4 bytes `0x40193` en todo `av-cam.bin`: **57
   ocurrencias** en direcciones `0x4372a414..0x4381d1d8` (literal pool).
2. `QuerySilentReferences.java` sobre esas 57 direcciones → **55 funciones
   distintas** las referencian; 53 con una sola referencia (wrappers
   triviales), y **2 con múltiples referencias**: `0x4381cc7c` (5) y
   `0x43794d40` (2). Estas dos son las únicas candidatas a contener lógica
   real (no un simple envío de una sola línea).

## Hallazgo principal: `0x40193` es un buzón de **servicio síncrono** (RPC), no un simple sumidero

**VERIFICADO** (decompilación completa, `analysis/session20/evidence/s20-mbx-primitives-dec.json`):

`FUN_43b04cd4(param_1, param_2, param_3=0x40193, param_4=0xffffffff)` —la
función que varios sitios llaman literalmente con `0x40193` como tercer
argumento— implementa el patrón RPC síncrono clásico:

```
si param_4 == -1:
    iStack_1c = CrearBuzonTemporal()        # FUN_43561324(0x2a, 5, &iStack_1c, -1, param_1)
msg = AsignarMensaje(pool = 0x40193, tam=8)  # FUN_435612d0
EscribirCampoReplyTo(msg, iStack_1c)         # FUN_43b04bfa
CopiarPayload(msg, param_1)
Enviar(a = 0x40193, msg)                     # FUN_4356120c
RecibirBloqueante(de = iStack_1c, 0xffffffff) # FUN_43561260  <- espera la RESPUESTA en el buzón temporal propio
CopiarRespuesta(param_2, ...)
Liberar(iStack_1c, ...)                      # FUN_435612ec
si param_4 == -1:
    DestruirBuzonTemporal(iStack_1c)         # FUN_43561324(0x4a, 0, iStack_1c)
```

Es decir: **quien llama a `FUN_43b04cd4(..., 0x40193, ...)` es un CLIENTE**
que envía una petición al buzón `0x40193` con un buzón de respuesta propio
(temporal o fijo) y espera la contestación ahí — **no recibe directamente de
`0x40193`**. `FUN_43b04ca2` (la variante sin espera, usada para
«re-armarse») hace lo mismo pero sin la fase de recepción: solo
`Enviar(a=0x40193, msg con reply_to=buzón_propio)`.

**Esto invierte la hipótesis más simple**: `0x40193` no es "la cola que algo
recibe para llegar a CaptureStart", sino **el buzón de un servicio al que
varias tareas (al menos RelMgr y CapIdTblMgr) envían peticiones/eventos**,
cada una indicando su propio buzón de respuesta. El verdadero receptor de
`0x40193` (la tarea servidora) sigue sin localizarse — pero ahora se sabe
**qué forma tiene su contrato**: debe contener un `FUN_43561260(0x40193, ...)`
en un bucle propio, análogo al de `CapIdTblMgr`.

## Cliente nuevo identificado: `CapIdTblMgr` (`FUN_4381cc7c`)

**VERIFICADO**: `FUN_4381cc7c` es el bucle de tarea completo de
**CapIdTblMgr** (nombre confirmado por sus propias cadenas de log:
`CapIdTblMgrIf::GetTblAddr_Req/Cmp`, `::StartAccess_Req/Cmp`,
`::StopAccess_Req/Cmp`, `::Init_End`, `::pop_queue_StartAc...`). Estructura:

```
bucle infinito:
    msg = Recibir(de = 0x4015e, 0xffffffff)      # buzón PROPIO de CapIdTblMgr
    si msg.id == 0x40193: manejo especial directo
    sino: busca msg.campo en tabla de 4 filas (0x43bf3800, 6 B/fila)
          -> despacha 0xd010/0xd011/0xd012/0xd013 (ver abajo)
    re-arme: Enviar(a=0x40193, reply_to=0x4015e)   # FUN_43b04ca2
    Liberar(0x4015e, msg)
```

La tabla `0x43bf3800` **es la misma región `0x43bf3xxx`** que
`shutter-trigger-chain-0x3011.md` ya había citado como destino de los
punteros de registro constante de la tabla de despacho `0x3011`
(`0x43ffdd30`) — **esto conecta por primera vez la tabla de despacho de
`0x3011` con el bucle de tarea real de CapIdTblMgr**, cerrando parte de la
ambigüedad que dejó esa nota de sesión 18/19 ("la «función» 0x437fd0e0 solo
devuelve el puntero 0x43bf3626").

Comandos despachados por CapIdTblMgr (claves `0xd010..0xd013`):
- `0xd010` GetTblAddr: hace un RPC síncrono hacia `0x40193` (`FUN_43b04cd4`)
  y llama `FUN_4381cc5c` con el resultado.
- `0xd011` StartAccess: llama `FUN_4381c9e0`/`FUN_4381cb2c` (no decompiladas
  en esta tarea).
- `0xd012` StopAccess: mismo patrón RPC que `0xd010`, además limpia un flag
  (`*DAT_44024130 = 0`).
- `0xd013` Init_End: solo re-arma (`FUN_43b04ca2`, sin espera).

## Lo que NO se cerró

**NO_VERIFICADO**: la identidad de la tarea servidora real de `0x40193`
(quien ejecuta `FUN_43561260(0x40193, ...)` en su propio bucle). No se
encontró entre las 55 funciones referenciadas (todas son clientes/wrappers
de envío). Es posible que el servidor reciba por un mecanismo distinto
(p. ej. un buzón "ancla" fijo cuyo ID se resuelve en tiempo de ejecución, no
como literal `0x40193` en el código del propio servidor) — **no se puede
descartar ni confirmar sin más búsqueda**.

**NO_VERIFICADO**: si alguno de los campos reply_to usados por OTROS clientes
de `0x40193` (fuera de CapIdTblMgr y RelMgr) coincide con el dominio `0x100`
que alcanza `CaptureStart` (`0x43809ed8`). Es el paso concreto que cerraría
el bloqueo: enumerar TODOS los sitios que llaman `FUN_43b04ca2`/`FUN_43b04cd4`
con destino `0x40193` (no solo los dos con múltiples refs) y extraer su
buzón de respuesta (`reply_to`) en cada caso.

## Clasificación

- **VERIFICADO**: `0x40193` es el buzón de entrada de un servicio RPC
  síncrono; `FUN_43b04cd4`/`FUN_43b04ca2` son los helpers cliente genéricos.
- **VERIFICADO**: `CapIdTblMgr` (`0x4381cc7c`) es un cliente de ese
  servicio, con su propio buzón `0x4015e`, y despacha 4 comandos reales
  (`0xd010..0xd013`) vía la tabla `0x43bf3800`.
- **VERIFICADO**: la tabla `0x43bf3800` es la misma región que
  `shutter-trigger-chain-0x3011.md` ya había señalado como destino de
  punteros constantes de la tabla de despacho `0x3011`.
- **NO_VERIFICADO**: identidad del servidor real de `0x40193`; si algún
  `reply_to` de otro cliente llega al dominio `0x100`/CaptureStart.
- **DESCARTADO**: que `CapIdTblMgr` sea el puente hacia `CaptureStart` — es
  un cliente del servicio, no su receptor, y sus comandos (`GetTblAddr`,
  `StartAccess`, `StopAccess`, `Init_End`) son de gestión de tabla de
  identificadores de captura, no de instalación de callback.

## Hallazgo adicional, más significativo: un llamador directo real de RelMgr clasifica eventos de la familia `0x40193`

Entre los 52 sitios de referencia única, `FUN_4379d2ec` resultó ser una
**función clasificadora**, no un simple envío:

```c
undefined4 FUN_4379d2ec(undefined4 param_1, undefined1 *param_2) {
  if (param_2 == 0x1502c7)              return 1;
  if (param_2 < 0x1502c8) {
    if (param_2 == &DAT_00020002)       return 2;
    if (param_2 == 0x40193)             return 1;   // <- misma clase que 0x1502c7
  } else if (param_2 - 0x260185 < 2)    return 3;
  return 4;
}
```

**VERIFICADO**: agrupa `0x1502c7` y `0x40193` en la **misma clase (1)**.
`0x1502c7` no es una dirección referenciada en ningún otro lugar del binario
(0 referencias) — es un valor numérico puro, probablemente otro identificador
de mensaje/dominio, no una dirección de memoria.

**Su único llamador registrado es `FUN_43aeaa4a`**, que es, él mismo, **un
llamador directo y real de RelMgr** (`FUN_4379d838`, la dirección ya
conocida desde sesión 16 como el emisor raíz de `0x3011`):

```c
void FUN_43aeaa4a(undefined4 param_1, int param_2, undefined4 param_3) {
  uint campo = *(byte *)(param_2 + 8);
  clase  = FUN_4379d2ec(param_1, param_3);               // 1/2/3/4
  corr_id = FUN_4379d328(param_1, clase, *(param_2+4));   // contador de correlación por clase
  // empaqueta {1, corr_id, param_3, 1} y registra diagnóstico 0x3003
  FUN_4379d838(param_1, &paquete);                        // == RelMgr
}
```

`FUN_4379d328` resultó ser un **generador de ID de correlación monotónico
por clase** (clase 1 incrementa un contador en `ctx+0xc80`, clase 3 en
`ctx+0xc84`; clases 2/4 no incrementan nada) — no una tabla de ruteo. Es
decir: **`FUN_43aeaa4a` recibe un evento, lo clasifica (agrupando `0x40193`
con `0x1502c7`), le asigna un correlativo, y llama directamente a RelMgr**.

**VERIFICADO**: `FUN_43aeaa4a` no tiene ningún llamador directo registrado
por Ghidra (0 referencias) — es alcanzado solo por despacho indirecto
(puntero a función / callback registrado), consistente con ser el
**manejador invocado cuando ocurre un evento de la familia `0x40193`/
`0x1502c7`**, no una función llamada estáticamente desde un único sitio
conocido.

**Límite honesto de esta cadena**: no se determinó la **dirección** del
enlace. Dos lecturas son compatibles con la evidencia:
(a) `FUN_43aeaa4a` es el callback que CapIdTblMgr/otro cliente registra
    como `reply_to` de su petición a `0x40193`, y al llegar la respuesta
    reenvía el evento a RelMgr (un bucle de retroalimentación hacia RelMgr,
    no la entrada original de S2); o
(b) es un manejador de un evento EXTERNO (físico/hardware) cuyo ID coincide
    numéricamente con `0x40193`/`0x1502c7`, y esta es la verdadera entrada
    de S2 hacia RelMgr.
No se decidió entre (a) y (b) en esta tarea — es el bloqueo concreto
siguiente. Esto **no se declara como el puente S2→CaptureStart cerrado**;
es la pista más fuerte encontrada hasta ahora de un camino directo y real
hacia `FUN_4379d838` (RelMgr) desde el dominio de `0x40193`.

## Hallazgo adicional: `FUN_43aeaa4a` SÍ está registrado estáticamente — tabla propia de 35 filas en `0x43ffff84`, distinta de la ya conocida en `0x43fff30c`

**VERIFICADO** (búsqueda de bytes crudos + lectura directa de `av-cam.bin`,
sin modificar el binario): el valor de 4 bytes `0x43aeaa4b` (puntero Thumb,
bit 0 = 1, a `FUN_43aeaa4a`) aparece **exactamente una vez** en todo el
blob, en la dirección `0x43ffff88`. Es la fila de una tabla real
`{id:4, fn_ptr:4, pad:4}` de 12 bytes/fila que empieza en `0x43ffff84` y
tiene **35 filas válidas** hasta `0x4400012c`:

```
0x43ffff84  id=0x4044  fn=0x43aeaa4a   <- nuestro handler
0x43ffff90  id=0x4042  fn=0x4379e47c
0x43ffff9c  id=0x4049  fn=0x4379e500
0x43ffffa8  id=0x4045  fn=0x43aea9f0
...
0x44000014  id=0xd003  fn=0x43aea90c
0x44000020  id=0xd000  fn=0x43aea9b2
...                                    (23 filas 0xd0xx en total)
0x4400011c  id=0xd015  fn=0x43aea838
```

Todas las 35 entradas son punteros Thumb reales (bit 0 = 1) en rangos de
código ya vistos (`0x4379exxx` = RelMgr, `0x43aeaxxx` = el mismo clúster de
`FUN_43aeaa4a`). **Esta tabla confirma que `FUN_43aeaa4a` es un handler
registrado declarativamente para el ID `0x4044`**, no una función huérfana
alcanzable solo por casualidad — coherente con, y más fuerte que, el
"0 llamadores directos" ya documentado arriba.

**Corrección importante — esta tabla NO es la tabla de 220 filas ya
conocida** (`silent-shutter-status.md`, fila "Tabla": offset
`[0xabe30c,0xabed5c)` = dirección `[0x43fff30c,0x43fffd5c)`, leída por el
despachador ya documentado `FUN_438052d8`). Se decompiló `FUN_438052d8`
para confirmarlo:

```c
undefined4 candidate_438052d8(int param_1,undefined4 param_2) {
  *DAT_4401f060 = param_2;
  iVar1 = 0; iVar2 = 0;
  do {
    if (*(short *)((int)&DAT_43fff30c + iVar1) == *(short *)(param_1 + 2)) {
      (*(code *)(&DAT_43fff310)[iVar2 * 3])();
      if ((&DAT_43fff314)[iVar2 * 0xc] != '\0') return 1;
      FUN_4375dcd4();
      return 1;
    }
    iVar2 = iVar2 + 1; iVar1 = iVar1 + 0xc;
  } while (iVar2 != 0xdc);
  return 1;
}
```

**VERIFICADO**: está cableado (hardcoded) a `DAT_43fff30c` y a `0xdc`=220
iteraciones — no recibe la tabla como parámetro, no es genérico, y **no
toca** la tabla nueva en `0x43ffff84`. Se inspeccionó también el hueco
intermedio `[0x43fffd5c, 0x43ffff84)`: contiene una estructura densa y
repetitiva (`0x438096ad` repetido, clúster `0x43b01c77..0x43b01cb9`,
clúster `0x43cb0xxx/0x43cb3xxx/0x43cb4xxx`) que **no** tiene forma de fila
`{id,fn,pad}` — es otra estructura (no identificada) completamente distinta,
no una continuación. La tabla de 35 filas empieza limpiamente justo después
de ese hueco. **Conclusión**: hay como mínimo **dos tablas de despacho
independientes con el mismo formato de fila**, cada una con su propio
lector — la de 220 filas (dueño: `FUN_438052d8`) y esta nueva de 35 filas
(dueño: NO IDENTIFICADO). Esto también refina el hallazgo de sesión 18/19
sobre IDs `0x40e3`/`0x4099` (Silent/EFCS): confirma que el espacio de IDs
`0x40xx`/`0xd0xx` se reutiliza en **tablas privadas distintas** de varios
subsistemas, no en una tabla global única — ningún ID de esta tabla nueva
(`0x4042,0x4044,0x4045,0x4049,0x404a-0x404c,0x4081,0x4092,0x40d3,0x40d6`,
`0xd000-0xd017`) coincide con `0x40e3`/`0x4099`.

**DESCARTADO** (lección metodológica, coherente con la ya documentada para
`FindScalarUses.java`): se intentó buscar "quién ENVÍA el comando `0x4044`"
mediante búsqueda cruda del valor literal de 4 bytes `0x4044` en el blob.
Apareció en `0x435c1904` (además de la propia tabla y una tercera
coincidencia en `0x43b867b6`, no investigada). Se corrigió el desfase de
direccionamiento del envoltorio `analysis/av-cam-analysis-view.elf` frente
a la convención de direcciones del proyecto (**hallazgo de herramienta
nuevo**: el ELF se generó con `llvm-objcopy -I binary` SIN saltar la
cabecera de 0x1F0 bytes del blob, por lo que una dirección Ghidra/script `W`
corresponde al offset `W+0x1F0` dentro del ELF, no a `W` directamente — se
verificó empíricamente comparando bytes crudos). Al desensamblar
correctamente ese sitio, resultó ser un **desplazamiento GOT** (`ldr
r1,[pc,#...]` seguido de `ldr r1,[r4,r1]`, patrón de resolución GOT ya
visto en los inicializadores de sesión 18) dentro de una función
inicializadora de objetos sin relación con mensajería — **coincidencia
numérica pura, no un enlace funcional**. Se abandona esta vía de búsqueda
para encontrar remitentes; no se decompiló `0x43b867b6` (sin tiempo
suficiente, candidato pendiente si se retoma esta vía).

## Cierre de la ambigüedad (a)/(b): confirmado — es retroalimentación de RelMgr, no la entrada de S2

Se decompilaron los 52 sitios de referencia única restantes del literal
`0x40193` (lote completo, `s20-mbx-remaining51-dec.json`). **Todos son
wrappers delgados** que construyen un payload (`{0x05, id_u16, 0x0}` o
variantes) y lo envían a `0x40193` vía `FUN_43ae12c4`/`FUN_43ae1354`/
`FUN_43ae15f4` — confirmando que `0x40193` recibe una **familia completa de
comandos `0xd0xx`/`0x40xx`** desde múltiples sitios, no solo desde
CapIdTblMgr.

**Hallazgo decisivo**: `0x4379e6a8` —la puerta de admisión de RelMgr, ya
conocida desde sesiones previas— **es uno de esos remitentes**: envía el
comando `0x4045` a `0x40193` (payload `{5, 0x4045, 0, iStack_30}`,
`FUN_43ae15f4(..., 0x40193, 0x30001)` — el mismo ID de cola `0x30001` ya
documentado en `silent-shutter-status.md` para el bucle de espera de
mensajes LIRO). Esto ocurre **condicionalmente**, solo cuando una
comprobación por vtable (`param_1[1]+0x18`) devuelve 0 y se cumple
`iStack_30==3 || iStack_30==9 || *(DAT_4402546c+0xd8)=='\0'`. Justo después
registra el diagnóstico **`0x3012`** (`FUN_43901a8c(4,0x3012,...)`) — un
código **nunca antes documentado**, adyacente a la familia ya conocida
`0x3011/0x3013/0x3015`. En la rama donde la condición NO se cumple (ya hay
resultado), la misma función llama directamente a **`FUN_4379eba0`**, el
emisor final de RelMgr ya conocido desde sesión 16.

Se decompiló el handler de la tabla para el ID `0x4045` (`0x43aea9f0`) y
resultó **estructuralmente idéntico** al handler de `0x4044`
(`FUN_43aeaa4a`): clasifica con `FUN_4379d2ec`, correla con `FUN_4379d328`,
empaqueta `{tag, corr_id, param_3, pad}` (tag=2 para `0x4045`, tag=1 para
`0x4044`) y llama directamente a `FUN_4379d838` (RelMgr):

```c
void candidate_43aea9f0(undefined4 param_1,int param_2,undefined4 param_3) {
  uStack_28 = 2;                                      // tag distinto de 0x4044 (tag=1)
  uStack_18 = *(byte*)(param_2+8);
  uStack_20 = FUN_4379d2ec(param_1,param_3);           // mismo clasificador
  uStack_1c = FUN_4379d328(param_1,uStack_20,*(param_2+4)); // misma correlacion
  FUN_43901a8c(4,0x3004,*(param_2+8),uStack_1c);        // diagnostico distinto (0x3004 vs 0x3003)
  FUN_4379d838(param_1,&uStack_28);                     // == RelMgr, igual que 0x4044
}
```

**VERIFICADO y decisivo**: esta es una **plantilla genérica repetida** para
(al menos) dos entradas de la tabla de 35 filas (`0x4044` y `0x4045`), que
RelMgr mismo activa enviándose un comando a `0x40193` y recibiendo la
"respuesta" como una llamada a uno de estos handlers, que simplemente
reempaqueta y se devuelve a sí mismo vía `FUN_4379d838`. **Esto decide la
ambigüedad (a)/(b) a favor de (a): es un bucle de retroalimentación interno
de RelMgr (pide algo a un servicio asíncrono y se notifica a sí mismo
cuando responde), NO la entrada original del evento físico S2.** Se
**descarta** la lectura (b) para esta familia concreta de handlers
(`0x4044`/`0x4045`, y por extensión probable el resto de IDs `0x40xx` de la
misma tabla con la misma forma — no verificado individualmente para cada
uno).

La entrada real de S2 hacia RelMgr sigue sin localizarse: debe estar
**antes** de `0x4379e6a8` (su llamador) o en otro punto de entrada de
`FUN_4379d838` no relacionado con esta familia `0x40193`/tabla `0x43ffff84`.

**Corrección/precisión frente a `shutter-trigger-chain-0x3011.md`**: ese
documento (sesión previa) ya registraba que `0x4379eba0` (emisor final)
envía **tipo 2, id `0x3011`** a la cola `0x40193` — y marcaba como
NO_VERIFICADO quién la recibe. **Se confirma que son dos formatos de
mensaje distintos hacia el mismo buzón, no la misma ruta**: (i) el evento
final real `{tipo=2, id=0x3011, correlación, índice_disparador}` que
representa el disparo S2 ya arbitrado, enviado una sola vez por
`0x4379eba0`; (ii) la familia de **autoconsultas internas** `{tag=5,
id_u16∈{0x40xx,0xd0xx}, 0}` que descubre esta tarea, con **respuesta
dirigida de vuelta a un handler de la tabla `0x43ffff84` que llama otra vez
a `FUN_4379d838`** — un bucle interno de RelMgr, no el camino del evento
`0x3011`. **Se consultó quién llama a `0x4379e6a8`**: únicamente
`FUN_4379d838` (RelMgr) mismo, desde **5 sitios internos distintos**
(`0x4379dce6/db4e/e052/dd5c/de10`) — confirma que `0x4379e6a8` es un
sub-helper interno de RelMgr invocado desde varias ramas de su propio
cuerpo, no una entrada externa. **El bloqueo original de
`shutter-trigger-chain-0x3011.md` (receptor real de la cola `0x40193` y
ruta hasta `0x43809ed8`) sigue exactamente igual de abierto** para el
mensaje tipo (i) — esta tarea solo cerró el mensaje tipo (ii), que resultó
ser un mecanismo interno no relacionado con el bridge CaptureStart.

## Siguiente paso concreto

1. Identificar al llamador real de `0x4379e6a8` (la puerta de admisión) —
   es el candidato más directo para encontrar la entrada real de S2, ahora
   que se sabe que su propio envío a `0x40193` es retroalimentación interna,
   no la entrada.
2. Identificar al lector/dueño real de la tabla nueva de 35 filas en
   `0x43ffff84` (análogo a `FUN_438052d8` pero para esta tabla). Como no hay
   referencia de Ghidra a la dirección `0x43ffff84` (0 refs registradas —
   región no desensamblada todavía por el proyecto), el camino más directo
   es buscar funciones con la misma forma de bucle (`do { cmp id; call cada
   entry+4; } while (contador != 35)`) cerca de funciones ya decompiladas
   del clúster RelMgr/`0x43aeaxxx`, en vez de repetir búsqueda de literales.
2. Decidir la dirección del enlace `FUN_43aeaa4a → RelMgr` (lectura (a) vs
   (b), ver arriba) ahora que se sabe que `0x4044` es su ID de registro:
   buscar quién puede recibir/enviar un mensaje con ese ID específico hacia
   esta tabla (no mediante búsqueda de literal, que ya demostró ser poco
   fiable — usar decompilación dirigida de candidatos con `QuerySilentReferences`/`DecompAt` en el clúster `0x43aeaxxx`/`0x4379dxxx`).
3. Decompilar los 51 sitios de referencia única restantes de `0x40193` (de
   los 52 — ya se revisó una muestra de 4: `0x4372a3c4`, `0x4379d2ec`,
   `0x4379e9a0`, `0x4381c824`) para extraer su `reply_to`/buzón de origen y
   confirmar si alguno hace `Recibir(de=0x40193, ...)` en vez de
   `Enviar(a=0x40193, ...)`.

## Archivos

- `analysis/session20/evidence/s20-mbx40193-callers.json` — 55 funciones
  que referencian las 57 direcciones de literal pool de `0x40193`.
- `analysis/session20/evidence/s20-mbx-multiref-dec.json` — decompilación
  real de `CapIdTblMgr` (`0x4381cc7c`) y `FUN_43794d40`.
- `analysis/session20/evidence/s20-mbx-primitives-dec.json` — decompilación
  real de `FUN_43b04ca2`, `FUN_43b04cd4` (helpers RPC) y las primitivas OSAL
  de bajo nivel `FUN_43561260`/`FUN_435612ec` (despacho por vtable en
  `DAT_440205c0+0x14`, slots `+0x1e0`/`+500`).
- `analysis/session20/evidence/s20-scalar-40193.json` — intento con
  `FindScalarUses.java` (0 aciertos, documentado como limitación de método:
  el valor se carga vía literal pool, no como inmediato de instrucción).

SilentShutter no se declara funcional.
