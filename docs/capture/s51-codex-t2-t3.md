# S51 Codex — T2 y T3

19-10-2026. Investigación estática de `av-cam.bin`; sin firmware ejecutado,
cámara, flasheo, Ghidra histórico ni sesión REA propia. La sesión REA compartida
no publicó `analysis/s51/shared/run/rea.sock.ready` durante este hito, por lo que
las conclusiones se verificaron con LLVM/bytes de `analysis/s51/shared/av.dis`.

## T2 — ID1/ID100/ID101

**Respuesta: dato físico faltante.** No se obtuvo la traducción de los IDs a una
dirección de registro IMX210 ni a un campo SIO, por lo que su significado eléctrico
es **NO_VERIFICADO**.

| Hecho | Evidencia | Estado |
|---|---|---|
| Selector de `SetExposure` | `0x436d6fb6` carga `LDRB r9,[r1,#9]`; `0x436d70be..70c6` limita 0..4 y despacha | VERIFICADO |
| Caso 2 | `0x436d7114..7132` aplica la máscara al destino lógico; `0x436d7136..713e` copia `param+8` y `0x436d7142..714a` copia `param+14` | VERIFICADO |
| Tabla S44 | `0x43fe995c` contiene 119 punteros, no registros en línea; cada destino apunta a `{id:u16, dato:u8}`. `0x436d5ed0` carga datos a la estructura backend y `0x436d5f60` pulsa su `+8` | VERIFICADO |
| Dirección IMX210/SIO de ID1/100/101 | Ninguna de las rutas anteriores la codifica ni la documenta | NO_VERIFICADO |

En captura fija, el llamador `0x438c828c` construye el parámetro en
`captura+0x64c`, lo pasa con `r1=captura+0x64c` a `0x436d6320`
(`0x438c82fe..830c`) y el virtual llega a `0x436d6f6c`. Esta es la fuente
inmediata del selector `param+9`; su productor semántico anterior no queda
identificado por esta cadena.

El dato exacto necesario es un mapa de registros del IMX210 aplicable a la A6000
o una traza pasiva que relacione los tres IDs/bytes con la trama SIO o la dirección
del sensor. La búsqueda pública no halló un documento IMX210 legítimo: el portal
oficial actual entrega recursos bajo registro y los PDFs accesibles eran de otros
sensores. No se asigna significado por analogía.

## T3 — emisión de P4E / segunda cortina

**Respuesta: NO.** En la ruta identificada no existe una guarda dependiente del
modo configurable `0..7`, `C+0x94`, EFCS o una opción normal `captura+0x74f` que
suprima selectivamente el cierre P4E.

| Tramo y guardas | Evidencia | Estado |
|---|---|---|
| Entrada MMIO | `0x43b5e2b0`: `CMP r0,#0x11; BHI return`; fija `r2=0` y salta a `0x4398f9a4`. Esta escribe `1<<bit` en `0xf2910048+banco*0x100` en `0x4398f9bc..f9c8` | VERIFICADO |
| Tag de emisión | `0x436bc140` despacha tag `0x12` a `0x436b93b0` (`0x436bc212`); el TBB de `0x436b93c0` alcanza `0x436b940e`, que carga banco/bit de `+0xc/+0x10` y llama `0x43b5e2b0` en `0x436b9416..941a` | VERIFICADO |
| Reintento/cancelación | `0x438d033c..0348` exige `captura+0x74f != 0`; entonces envía evento 3 en `0x438d0382..038c` | VERIFICADO |
| Petición inicial | `0x438d0420..042a` exige `captura+0x74f != 0`; evento 3 solo si `43ae7648(captura)==1` (`0x438d0466..047a`) | VERIFICADO |
| Bypass | `0x438c254e..2562`: `D+0x7e!=0 && D+0x7f==captura+0x1d8` borra `captura+0x74f`; `D=0x43e95950`. La rama `0x438c26d4..2724` propaga estados diagnósticos | VERIFICADO; no es selector de foto normal |

La única guarda local del MMIO es el límite de banco. Las guardas anteriores
`+0x74f` y estado condicionan que se genere el evento 3, pero no leen ninguno de
los cuatro flags solicitados; el único escritor de `+0x74f` analizado como bypass
es diagnóstico y produce estado no normal. Por tanto no hay instrucción que
autorice una ruta de foto fija sin cierre mecánico basada en `0..7`, `C+0x94`,
EFCS o ese bypass.

El enlace eléctrico final tag/MMIO → fase Darwin → P4E es **PARCIAL**: S21 verifica
P4E como `2ND_CURTAIN_MG`, pero la semántica banco/bit de `0xf2910048` no se
renombra como P4E sin prueba adicional. Esto no altera el NO de las guardas
observadas.

## Rutas descartadas y recursos

- No se usó `0xb6`, ni se reinterpretaron las cantidades de callbacks `1/2/3/6`.
- No se infirió identidad eléctrica desde los IDs lógicos ni desde una dirección MMIO.
- Tiempo de análisis: ~55 min; REA adicional: 0 min; memoria adicional: 0 MB.

**VEREDICTO: CAMBIOS.** T2 sigue requiriendo mapa/traza del sensor; T3 no ofrece
un flag configurable que elimine selectivamente el cierre de segunda cortina.
