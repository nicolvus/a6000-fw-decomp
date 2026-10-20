# S61 — conclusiones: origen de los parámetros IMX210 (A6000)

20-10-2026. Análisis estático, emulación Unicorn offline y REA (una sesión, cerrada). Sin firmware en cámara, sin flasheo, sin parche. A6000 `av-cam.bin` SHA `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`. Detalle: [origen de parámetros](s61-imx210-parameter-origin.md) · [flujo de mensajes](s61-message-flow.md) · [matriz](../../analysis/s61-evidence-matrix.json). Scripts: `analysis/s61/`. Pruebas: `tests/test_s61_imx210.py` 22 OK.

## Resultados

1. **Corrección TBH (S60-Sol) cerrada.** Base PC = `0x43806a08`; casos 4/10 → `0x43806c28`/`0x43806d06`; script y test corregidos; destinos verificados contra bytes y prólogo de manejador (`s61-message-flow.md`).
2. **Selección A/B (VERIFICADO):** A exige `bit6(G[0xD])==0` (`G = 0x43e964a4`, **no** el objeto de 0xF20 B: corrige S60); B exige `[[p]+0x3a]==1`. `stage+0x3a` vale 0 en el constructor `0x437a9d30`, copia `src+0xb4` en `0x437aa65c` y se borra si `G[0xD]` bit6==1. Ningún escritor a 1 localizado.
3. **Cadena de B recuperada hasta `obj+0x2be..0x2d0`:** `0x43861ed0` (P0) → `obj+0x314..0x32a` → 5 pares de B; 6.º par desde tabla BK4 `0x300AB` (idéntica en los 5 `CX77500_*`: 18 pares `(0x2EA0,0x6028)`). Ejecutada con el código real (PERMITIDO).
4. **Semántica:** los pares son ventanas lo/hi de 16 bit con márgenes ±0x400 y reordenación, no tiempos demostrados: «M = temporización» queda **debilitada** (INFERENCIA), no descartada.
5. **Petición 9 localizada:** emitida desde el manejador de sincronía `HS_Main` (`0x4378fef4`, call `0x437907a6`) vía `0x43b00ed8`→`0x43806398/0x4380632c`→`0x438061c4` (cola `0x3030f`); publicación por `VD_Pre` (`0x43792a0c`→`0x43b00dd4`). Orden estático: HS_Main → resp. 10 → staging → VD_Pre. **Petición 3: no localizada.** `0x8003030f` ≈ alias de `0x3030f` (INFERENCIA).
6. **Auditoría S60:** emisores `0x43b00fe6/f62`, casos 3/4/9/10, productores A/B y acceso `0x43ae8504` reconfirmados; correcciones: (a) TBH (Sol), (b) `obj+0x168/0x16A` es el global G, (c) «campos de otro objeto» de B = `obj+0x2CC` copiado (familia `0x4379fc9e`); el comentario de `test_s60_claude.py` («Sol: 0x43806c24») describe el valor antiguo y se conserva como histórico.

## Estados alcanzables

**Ninguno (ALCANZABLE = 0).** Existe un estado PERMITIDO (`analysis/s61/e3_chain.json`). No se completa `(modo,M,Tv,clk,N,svr,VdNum,flags,svd,shd,spl)`: faltan escritores de `obj+0x2be..`, `G+0x168/16A`, `G[0xD]`, `stage+0x3a` y el vínculo M↔Tv/clk (`s61-imx210-parameter-origin.md`).

## Silent shooting / fin electrónico de integración

Sin evidencia nueva: los pares no son órdenes ni tiempos; el tráfico de mensajes es de sincronía/estado por V. Hay un hilo nuevo, **solo HIPÓTESIS**: `HS_Main` (`TC::Last1st/Last2nd`, `EC::`, `LC::`, `YC::`, `Lens::`) y `VD_Pre` ordenan por V las subtareas de sincronía; si el fin de exposición se planifica allí, es el sitio donde buscarlo. Ninguna secuencia de registros reescribe nada al terminar (S57 intacto). **S51: A = NO, B = NO, C = NO.**

## Bloqueantes

Escritores de `G+0x168/0x16A`, `G[0xD]`, `stage+0x3a`, `obj+0x2be..`; emisor del tipo 3; semántica del bit 31 (OSAL de `liro.ko`); mapeo constructor de etapa ↔ modos `0x0B/0x2F`; unidad de los pares; servicio `+0x27c` (INFERENCIA).

## Recomendación S62

(1) Sembrar Thumb en `0x4378fef4`, `0x43792a0c`, `0x437ab474`, `0x43b00ed8`, `0x4379fc9e` y trazar con `trace_native_values` las entradas de P0 (`obj+0x2be..`) desde `0x4383075c`/`0x437f1414`; (2) leer `HS_Main` de principio a fin (orden TC/YC/EC/LC/Lens y qué tarea programa el fin de exposición); (3) emular `0x437a9a7c`/constructores con `G[0xD]` y `src+0xb4` derivados de un modo real; (4) traza pasiva (si se autoriza) de VD/CIS0 para fijar unidades.

## Pruebas ejecutadas

`test_s56` 26 OK · `test_s57` 34 OK · `test_s58` 23 OK · `test_s59_claude` 9 OK · `test_s59_sol` 11 OK · `test_s60_claude` 12 OK · `test_s60_sol` 6 OK · `test_s61_imx210` 22 OK (`analysis/s61/test-results.txt`; el último recuento es de la ejecución final). ruff limpio en `analysis/s61` y la prueba nueva; mypy no resuelve los módulos por `sys.path` (patrón heredado).
