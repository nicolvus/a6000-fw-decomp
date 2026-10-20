# S20 — Stage_RawPlayInit y reutilización de etapas

Alcance: Sony A6000 FW 3.21, `av-cam.bin` (base LIRO `0x43541000`), proyecto
Ghidra local `analysis/ghidra/silent-liro` (solo lectura). Herramientas:
`scripts/ghidra_dec.sh` (decompilación real vía Ghidra 12.1.4) y
`QuerySilentReferences.java` (referencias registradas por el proyecto). Sin
Codex, sin subagentes — investigación directa de Claude en esta sesión. No se
modificó ningún binario, no se usó Ghidra sobre hardware real, no se conectó
ni flasheó una cámara.

## Estado: PARCIAL — cadena RawPlay/DevLater cerrada (lee `.ARW` de tarjeta, no YC en memoria); mecanismo general de descriptor sigue abierto

Esta tarea retoma S19-14, que nunca llegó a ejecutarse (cuota de Codex
agotada antes de empezar). Es la primera investigación técnica profunda de
esta sesión.

## 1. Las cadenas `Stage_RawPlayInit`/`ycc_rawplay`/`sds_ycc_handle` existen pero no tienen referencias de código registradas

**VERIFICADO** — Las tres cadenas existen literalmente en `av-cam.bin`:

| Cadena | Offset archivo | VA LIRO |
|---|---|---|
| `Stage_RawPlayInit` | `0x76c51b` | `0x43cad51b` |
| `ycc_rawplay: %x` | `0x76c4dc` | `0x43cad4dc` |
| `sds_ycc_handle: %x` | `0x76c508` | `0x43cad508` |

**VERIFICADO** — Consulta de referencias (`QuerySilentReferences.java`,
`analysis/session20/evidence/rawplay-string-refs.json`) contra el proyecto
Ghidra persistente: **0 referencias registradas** a las tres direcciones. Por
contraste, cadenas vecinas en el mismo clúster de diagnóstico sí tienen
referencias reales: `Stage_DevLater.cpp` (`0x43cac51b`, 2 refs, función
`0x437edaf8`), `Stage_Notify.cpp` (`0x43caccd6`, 8 refs, funciones
`0x437ef8cc`/`0x43b1ad32`/`0x43b1bb4c`), `Stage_SACC`/`Stage_SACC.cpp`
(`0x43c9ee6c`/`0x43c9f18a`, 34 refs, función `0x43b196c8`),
`Stage_NotifyLongExpNRCapturing` (`0x43caccb7`, 4 refs, función `0x43b1ae2a`).

**INFERENCIA**: la ausencia de referencias a `Stage_RawPlayInit` no prueba
código muerto ni ausencia de uso (el propio proyecto advierte: "una lista
vacía no demuestra código muerto" — `QuerySilentReferences.java`). El
auto-análisis de este proyecto Ghidra es parcial (ver `analysis/rea/README.md`:
"Autoanálisis amplio limitado a 300s, parcial, con advertencias"). Es posible
que la referencia exista vía un patrón de carga que Ghidra no resolvió
(salto indirecto, tabla de punteros, cálculo de dirección no literal) o que
esta ruta de diagnóstico corresponda a una build/variante no alcanzada por
el flujo de FW 3.21 analizado. **No se puede afirmar ni que exista ni que no
exista una llamada real a esta ruta.**

## 2. El clúster Stage_DevLater/Stage_Notify/Stage_Apollo/Stage_Orientation comparte la misma estructura de contexto que las filas LIRO ya conocidas

**VERIFICADO** (decompilación real, `analysis/session20/evidence/s20-rawplay-dec1.json`):

- `FUN_437edaf8` (Stage_DevLater): con `param_3==0`, copia en bloque los
  campos `ctx2+0x27e4..+0x28e4` del segundo parámetro hacia
  `ctx+0x4b70..+0x4fe0` del primero. **Estos mismos offsets (`+0x4b70` en
  adelante) son los campos de captura ya documentados en S19-12/S19-07** como
  parte del contexto convencional de captura. Esto conecta por primera vez
  Stage_DevLater con la estructura de contexto de captura ordinaria, en vez
  de con una estructura separada exclusiva de RawPlay.
- `FUN_437ef8cc` (helper de Stage_Notify, llamado también desde
  `FUN_43afe9f4`/`FUN_43afe11a`): implementa un mecanismo real de
  **guardar/recuperar un descriptor de 3 palabras** (`ctx+0x4b54/+0x4b58/+0x4b5c`,
  patrón puntero+2 campos) hacia/desde un objeto secundario en `ctx+0x4ad0`,
  en los offsets `+0x16cc/+0x16e0/+0x16e4`:
  - `*(ctx+0x4b60) < 2` (valor 0 o 1): **guarda** el descriptor actual en
    `ctx+0x4ad0`.
  - `*(ctx+0x4b60) == 2`: **recupera** el descriptor desde `ctx+0x4ad0` hacia
    `ctx+0x4b54/+0x4b58/+0x4b5c`.
  - Para `*(ctx+0x1e0)` ∈ `{3,9,0x1c}` (valores de "tipo de captura" ya vistos
    en otras filas), además copia un rango de palabras adicional vía
    `FUN_437e0b88`.
  - **DESCARTADO** interpretar esto como YC real: el descriptor son 3 palabras
    de metadatos (puntero + 2 campos), sin verificar que apunten a un buffer
    YC válido, su tamaño, ni su formato.
- `FUN_43b1ad32` (Stage_Notify, caso 0): lee un anillo circular en
  `ctx+0x4ad4` (tamaño en `+0x20`, cursor en `+0x28`), extrae un triple de
  palabras (`+0x44`/`+0x48` de la entrada) hacia `ctx+0x4b58/+0x4b5c`, y
  **construye y envía el mensaje `0x1003`** con ese descriptor vía
  `FUN_437feef8(...,0x1c,&DAT_00020002)`. El mismo patrón de mensaje
  (`FUN_437feef8` con selector `0x00020002`) ya se documentó en S19-07/S19-12
  como el mecanismo de envío de comandos LIRO.
- `FUN_43b1ad32` (caso 2): llama `FUN_437873a4(...,0xe0b00,1,...)` — **la
  misma unidad SDS `0xe0b00` ya confirmada en S19-05** como el bloque de
  control de 0x800 B de la ruta PbCap/SDF — dentro de una rama etiquetada
  por las cadenas `Stage_ExpandSpicaParam`/`SPICA_PCOEF`/`SPICA_Param`/
  `TAP1_ODL_GetBinaryData`/`TAP2_ODL_GetBinaryData`. **Esto es una conexión
  nueva, no documentada en sesiones 16-19**, entre el clúster
  Stage_Notify/Apollo y la unidad SDS `0xe0b00` ya conocida, a través de una
  ruta de parámetros SPICA/TAP (calibración de ISP), no de reutilización de
  imagen almacenada.
- `FUN_43b1ad32` (caso 4) y el string `Stage_RchRcv_Resize_AutoReview`
  (`0x43cad765`) usan las unidades `0x50b0b` y `0x50b2e` — **una familia de
  unit-types `0x50bXX` distinta del raster `0x50b3f` de S19-05** — vía la
  misma función de lookup `FUN_437873a4`. Confirma que `0x50bXX` es una
  familia de unit-types de raster/resize, no un valor único.
- `FUN_43b1bb4c` (clasificado por su propia cadena de diagnóstico como
  **Stage_Apollo**, nombre no documentado en sesiones previas): opera sobre
  el mismo objeto secundario `ctx+0x4ad0` en los campos `+0x1bfc/+0x1c00/
  +0x16bc/+0x16be/+0x170c`, condicionado a `*(ctx+0x534c)` ∈ `{2,4}`.
- `FUN_43b1ad32` (caso 1) referencia **Stage_Orientation.cpp**
  (`0x43cc97b4`, tampoco documentada antes) y lee `ctx+0x4ad0+0x1c`/`+0x1c0d`.

**VERIFICADO**: los campos `ctx+0x4ad0` (puntero a objeto secundario),
`+0x4ad4` (puntero a arreglo con cursor circular) y `+0x4b54/+0x58/+0x5c`
(descriptor de 3 palabras) son compartidos por Stage_Notify, Stage_Apollo,
Stage_Orientation y por los helpers genéricos `FUN_43afe9f4`/`FUN_43afe11a`
ya citados en S19-07 como llamados desde varias filas de la tabla LIRO.

## 2.1 Cadena real hacia Stage_DevLater

**VERIFICADO** (decompilación de `FUN_43afe192`, caso 0):

```
FUN_43afe192(caso 0)
  si ctx+0x3c == 0:                       # NO_VERIFICADO el nombre del campo;
                                            # el else emite "Change_StillRecMode_to_JPEG"
    FUN_437edd44()
    iVar3 = FUN_437edd1c()
    si iVar3 != 0:
      FUN_437edd04(&buf)
      uVar4 = FUN_43561604(uStack_70)
      FUN_437edaf8(ctx, uVar4, 0)          # == Stage_DevLater, param_3=0
      FUN_43ae7c80(buf_campo & 0xffff, 2)
  si no:
    log "Change_StillRecMode_to_JPEG..."   # ctx+0x3c actúa como gate de modo
```

Esto es la primera cadena de llamada real y verificada hacia Stage_DevLater
encontrada en el proyecto. Es condicional a `ctx+0x3c==0` (un campo cuyo
nombre semántico es NO_VERIFICADO, pero cuya rama alternativa emite
explícitamente el diagnóstico "Change_StillRecMode_to_JPEG", lo que sugiere
que `ctx+0x3c` distingue un modo de grabación) y al resultado no nulo de
`FUN_437edd1c()`. Las funciones `FUN_437edd44`/`FUN_437edd1c`/`FUN_437edd04`
(rango `0x437edXXX`, contiguo a los helpers de Develop ya vistos como
`FUN_437ed568`/`FUN_437ed9f8`/`FUN_437ed4bc`) **no fueron decompiladas en esta
tarea**: son el siguiente paso concreto para determinar qué produce `uVar4`
(el segundo argumento de Stage_DevLater) y si tiene relación con un buffer YC
ya almacenado.

## 3. Bloqueo cerrado: qué hace realmente la cadena hacia Stage_DevLater

**VERIFICADO** (decompilación de `FUN_437edd44`, `FUN_437edd1c`,
`FUN_437edd04`, `FUN_43561604`, `FUN_43ae7648`,
`analysis/session20/evidence/s20-rawplay-dec3.json`):

- `FUN_437edd44` **abre y parsea un archivo `.ARW` real desde la tarjeta
  SD**: construye la ruta `DCIM/100MSDCF/DSC%05d.ARW`
  (`s_DCIM_100MSDCF_DSC_05d_ARW_43cac566`), lo abre con `FUN_439005b8`, y
  busca dentro de su estructura TIFF las etiquetas **`0x111`
  (`StripOffsets`)** y **`0x117` (`StripByteCounts`)** vía `FUN_437edaa4`
  (parser de tags TIFF/EXIF). Verifica el tamaño del strip contra
  `param_1+0x4e64` y, si cabe, copia los bytes crudos del strip a
  `param_1+0x4e60+0x4e58`. Si cualquier paso falla, pone a 0 la bandera
  `DAT_4401eabf` (éxito de carga); si todo tiene éxito, la deja en 1.
- `FUN_437edd1c` es el gate: devuelve 1 solo si `DAT_4401eabf != 0`
  **y** `*(DAT_4402546c+0x73) != 0` (un segundo flag global independiente).
- `FUN_437edd04` copia 0x70 bytes desde `DAT_43ede284` (buffer estático
  llenado en `437edd44` desde el lookup de configuración `0x1c3`) — **esto es
  `uVar4`, el segundo parámetro que llega a Stage_DevLater**. No es un
  descriptor de píxeles: es un bloque de configuración/ruta de 0x70 B.
- `FUN_43ae7648` (gate de `FUN_43afe9f4`/`FUN_43afe11a`): lee bits de
  `ctx+0x4fd0` — bit 0 → devuelve 1 (omite la llamada a `437ef8cc`); bits
  1-4 (`0x1e`) → devuelve 2; si no → 0.

**Conclusión verificada**: la cadena `FUN_43afe192 → FUN_437edd44 →
FUN_437edd1c → FUN_437edd04 → FUN_43561604 (vtable) → FUN_437edaf8
(Stage_DevLater)` es el mecanismo real de **"revelar" (develop) un archivo
`.ARW` ya existente en la tarjeta SD**, no de generar una fotografía nueva a
partir de datos YC de Live View o del sensor. El archivo `.ARW` que esta
ruta lee tuvo que haberse escrito previamente por una captura RAW normal
(mecánica o no). Esto confirma técnicamente la mención de
`silent-integration-design.md` ("revelado de ARW desde tarjeta") pero
**cierra, no abre**, la hipótesis de independencia mecánica por esta vía: no
hay entrada alternativa desde un buffer YC en memoria, solo desde un archivo
`.ARW` en el sistema de archivos.

## 4. Pregunta central: respondida negativamente para esta ruta concreta

**VERIFICADO (negativo para esta ruta)** — Stage_RawPlayInit/Stage_DevLater,
tal como se verificó en esta tarea, **no** es un camino que permita generar
una fotografía sin haber ejecutado antes una adquisición de sensor: opera
sobre un archivo `.ARW` que ya debe existir en la tarjeta SD, escrito por una
captura previa. No se demostró que alguna secuencia LIRO reciba datos YC ya
disponibles en memoria (Live View) y genere componentes fotográficos sin
repetir la adquisición del sensor. Lo que sí se estableció:

1. La ruta de diagnóstico específica `Stage_RawPlayInit`/`ycc_rawplay`/
   `sds_ycc_handle` no tiene una llamada estática localizada en este
   análisis (ni se puede descartar que exista).
2. Existe un mecanismo real de guardar/recuperar un descriptor de 3 palabras
   entre el contexto de captura y un objeto secundario (`ctx+0x4ad0`),
   compartido por varias etapas con nombre (`Stage_Notify`, `Stage_Apollo`,
   `Stage_Orientation`) y por los dispatchers genéricos ya citados en S19-07.
   Este mecanismo es de **metadatos** (puntero + 2 campos), no se verificó
   que transporte píxeles.
3. Existe una cadena real y nueva hacia `Stage_DevLater` desde
   `FUN_43afe192`, condicionada por un campo de modo (`ctx+0x3c`) cuya rama
   alternativa es explícitamente "Change_StillRecMode_to_JPEG". El bloqueo
   concreto siguiente es decompilar `FUN_437edd44`/`FUN_437edd1c`/
   `FUN_437edd04`/`FUN_43561604` para saber qué es `uVar4` y si conecta con
   un YC ya almacenado.
4. Se descubrió una conexión nueva entre el clúster Stage_Notify/Apollo y la
   unidad SDS `0xe0b00` (ya conocida de S19-05) vía una ruta de parámetros
   SPICA/TAP, y una familia de unit-types de raster `0x50b0b`/`0x50b2e`
   distinta de `0x50b3f`.

**DESCARTADO**: afirmar independencia mecánica solo porque estas etapas
procesan datos ya almacenados en memoria (anillo circular, descriptor
guardado). Ninguna de las rutas examinadas en esta tarea toca directamente
Darwin/CAIF ni los controladores físicos de obturador — pero tampoco se probó
que los evite: simplemente no aparecen en el fragmento de código decompilado
en esta tarea.

## Próximo bloqueo concreto

El bloqueo original de `silent-integration-design.md` ("¿Stage_RawPlayInit
permite entrar con un YC de LV?") queda **cerrado negativamente** para esta
ruta: requiere un `.ARW` en tarjeta, no un buffer YC en memoria. El bloqueo
que queda abierto es el mecanismo de guardar/recuperar metadatos de
`FUN_437ef8cc` (independiente de esta cadena RawPlay) — determinar si el
descriptor de 3 palabras que guarda/recupera puede, en algún caso, apuntar a
un buffer YC de Live View en vez de a datos de archivo. Siguiente paso
concreto: decompilar `FUN_43ae75dc` (getter de contexto usado en todas las
etapas) para identificar qué subsistema llena `ctx+0x4b54/+0x4b58/+0x4b5c`
antes de que `437ef8cc` los guarde, y si alguna vía de Live View (no solo
RawPlay/DevLater) escribe esos campos.

## Archivos

- `analysis/session20/evidence/rawplay-string-refs.json` — referencias
  Ghidra a las 8 cadenas de diagnóstico consultadas.
- `analysis/session20/evidence/s20-rawplay-dec1.json` — decompilación real
  de `0x437edaf8, 0x43b1ad32, 0x43b1bb4c, 0x437ef8cc, 0x43b196c8, 0x43b1ae2a`.
- `analysis/session20/evidence/s20-rawplay-dec2.json` — decompilación real
  de `0x43afe9f4, 0x43afe11a, 0x43afe192`.
- `analysis/session20/evidence/s20-rawplay-dec3.json` — decompilación real
  de `0x437edd44, 0x437edd1c, 0x437edd04, 0x43561604, 0x43ae7648` (cierra la
  cadena: lectura de `.ARW` desde tarjeta SD, no de YC en memoria).
- `analysis/session20/evidence/s20-rawplay-callers.json` — llamadores
  registrados de `0x437ef8cc, 0x43b1ad32, 0x43b1bb4c, 0x437edaf8`.

SilentShutter no se declara funcional.
