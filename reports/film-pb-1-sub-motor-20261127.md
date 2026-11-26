# FILM-PB-1 — vía del motor: los seis `0x1A` de `FUN_007211B0` (27-11-2026)

Cierra la pregunta «¿puede el `0x1A` venir del arranque del motor por hardware, DMM o av-cam?».
**Espacio de direcciones:** todas las VA son del ELF (`libmpr.so` 3.21, SHA-256 `9a74a3bb…4c30`); *REA = ELF + 0x10000*.
Método: desensamblado local con Capstone 5 y **emulación Unicorn** del traductor completo (barrido de 65 536 entradas
`(familia<<24)|código`, 256×256), más lectura de vtables resueltas por `R_ARM_RELATIVE`. Nada de `mcp_rea`, nada de cámara.
Evidencia: [tabla-0x1a](evidence/film-pb-1-sub-motor-20261127-tabla-0x1a.txt),
[desasm](evidence/film-pb-1-sub-motor-20261127-desasm.txt), [emu](evidence/film-pb-1-sub-motor-20261127-emu711.py).

## 1. Los seis sitios: código que traducen y de dónde sale

`FUN_007211B0` no lee ningún «último error» global: es un traductor puro `r0 = f(código interno)`; los dos `bl` del
manejador le pasan el valor de retorno de la llamada anterior. Sólo **seis** de las 65 536 entradas dan `0x1A`:

| # | Sitio ELF (REA) | Código interno | Qué comprueba el sitio | Quién produce ese código | Dato consultado |
|---:|---|---|---|---|---|
| 1 | `0x711314` (`0x721314`) | `0x1C00001A` | igualdad con el «fallo genérico MPR» | **catch-all**: rama por defecto del normalizador `0x300D50` y ~cientos de sitios de `libmpr` | estado interno de cada módulo MPR |
| 2 | `0x711350` (`0x721350`) | `0x1C000033` | igualdad con «error 2 normalizado» | `0x300D54` ← `0x53000002` / `0x6B00000B` / `0x85000002` (`0x300CFC`,`0x300D0E`,`0x300D14`) | «error 2» de los módulos `0x53/0x6B/0x85` |
| 3 | `0x71153C` (`0x72153C`) | `0x31000002` | igualdad con «error 2» de MMGR | 57 sitios; p. ej. `0x60A6D6` (chequeo de ruta/nombre) | resultado de una orden al gestor de medios (MMGR), en RAM |
| 4 | `0x7116D2` (`0x7216D2`) | `0x0F000005` | igualdad con «error 5» del wrapper thread/IOCTL | **sólo** dos stubs constantes: `0x75E6F4` y `0x75E700` (pool `0x75E6FC`/`0x75E708`) | constante; su único consumidor es `0x4365FE` (`CheckExtDeviceFirmUpConditions`, `0x436602` traduce) |
| 5 | `0x711716` (`0x721716`) | `0x30000005` | igualdad con «error 5» de FeaCore | `0x4439AA` (+ `0x443368`,`0x443A28`,`0x443AE0`,`0x443C28`), log `"NEED_THUMBNAIL But I have not Thumbnail!"` `0x4439C2` | miniatura del clip para el índice: catálogo/BD de la tarjeta |
| 6 | `0x7118F4` (`0x7218F4`) | `0x88000002` | igualdad con «error 2» del namespace media | `0x3CB178` convierte `0x31002011`→`0x88000002`; 15 sitios en `libmpr` + 13 en `libObj` | resultado de órdenes MMGR (`0x310020xx`) |

Las familias `0x31` y `0x88` comparten tabla de códigos bajos (`0x01…0x1B` dan lo mismo en [tabla, líneas 15–18]):
son dos prefijos del mismo enumerado del gestor de medios, no dos causas distintas.
**Ninguno de los seis productores lee `nflasha2`, `nflasha3` ni `nflasha15`** (los únicos `/dev/nflasha*` de `libmpr`
están en `0x7DD572` —DFB, `nflasha0p4`— y en un pool de datos en `0x9D20F4` —`nflasha4`—, fuera de estas rutas), así
que **la presencia o ausencia de los cinco tipos AVC en el mapa externo es irrelevante para los seis**.

## 2. Quién llama al traductor dentro del manejador de `PlayMovie`

El manejador `0x437BC0` tiene **exactamente dos** `bl 0x7111B0`:

- `0x437CFC` ← retorno de `MoviePlayerIf::PbStart` (`0x307F54`). `PbStart` es sólo log (`"[MoviePlayerIf] PbStart Param"`,
  `0x307F72`) y delega en `0x3079AA` (`0x308194`), que termina en `0x307A48` `movs r0,#0` ⇒ **devuelve 0 siempre** ⇒
  la rama `cbz r0, 0x437D2C` (`0x437CFA`) siempre se toma y **la vía PbStart→0x1A es código muerto en 3.21**. El punto
  `0x437CFC` del plan de la auditoría nunca saltará.
- `0x437C7E` ← retorno de `FUN_00447DA8` (guarda previa al motor), que es el método **`vtable+0xB4`** de la entidad
  obtenida por `id=[core+0x1EC]` (`0x447810` → `0x66D0C8` → «MMGRIF»). La clase es **AviMMgr** (vtable `0x8E6E58`):
  `+0x58 = 0x61A8F0` (`isSupportContent`), `+0x5C = 0x60945C` (`GetPlayMovieStatus`), `+0x60 = 0x603DBC`
  (`GetPlayStillStatus`) y **`+0xB4 = 0x608698` (`MovieReadStart`)**.
  `MovieReadStart` sólo puede devolver **0** o **`0x31000007`** (`0x6086DC`: estado `[this+0x140]&0x24` falla, `0x3EA344`
  =1 o `sub_64C228`≠0), y `0x31000007 → 0x0A` (ER_SEQUENCE), **no `0x1A`**.

**Consecuencia:** en el camino síncrono del manejador los `0x1A` posibles son únicamente los dos literales de las guardas
(`0x437C0A` «Pb Disable!! ref) dsm get» y `0x437C3C` «Detect UnSupported Content»). Los seis códigos traducidos no son
alcanzables ahí.

## 3. ¿Pueden fallar por arranque en frío (sin WBI) o por la BD de imágenes?

**No por arranque en frío:** ninguno de los seis consulta el WBI, `nflasha5` ni ningún estado de *boot*; son códigos de
estado en RAM, de órdenes al gestor de medios o constantes de stub. Un arranque en frío no los altera por sí mismo.

**Por la BD de imágenes: dos sí son dependientes por naturaleza, pero no en esta ruta.** `0x30000005` nace de
«miniatura ausente» (índice/catálogo) y `0x31000002`/`0x88000002` de resultados MMGR (montaje/estado de la tarjeta);
ambos viven en APIs de índice y de gestor, no en `PlayMovie`.

**DMM:** en `libmpr` «DMM» es el servicio de mensajes de memoria (`[Mem_DmmAccess][SendAndReceiveDmmMsg]`, `0x8DC2C0`),
no el mapa de `nflasha2`; no aparece en las seis rutas ni en las tres guardas.

**Las condiciones que sí gobiernan la reproducción** (y que por eso heredan el `0x1A`):

- **Guarda A** (`0x447A1E`): por cada bit de la máscara `[core+0xDB8]` pregunta a AviMMgr `+0x60` o `+0x5C(tipo)`; si la
  respuesta es 0 → `0x1A`. `GetPlayMovieStatus` devuelve 0/1 (`0x609766`,`0x60976A`) y trabaja con `[this+8]`
  (`vtable+0x144/0x154/0x164/0x174/0x184`), estado en RAM; con tipo desconocido devuelve error `0x31000001` (`0x60949E`).
- **Guarda B** (`0x447F26` → `isSupportContent` `0x61A8F0`): devuelve 0 → `0x1A`. Falla por **(i)** `"Can't get condition"`
  (`0x61A932`/`0x61A93C`, si `sub_3F9C7C([this+0x768],…)` no da condición del contenido: **depende del fichero y del
  catálogo**) y **(ii)** frame rate/TvSystem (`0x61A9EE` TvSystem de `0x1EEFDC`; máscaras `0x2A8`/`0x154`/`3`, mensajes
  «Invalid TvSystem» `0x61AA40`, «Unknown frameRate» `0x61AA52`, rama 24p/23.976p).
  El clip MAH04198 es 29,97 p (285 cuadros / 9,5095 s), así que la rama 24p no aplica: si falla la guarda B, lo esperable
  es (i), es decir, condición de contenido/BD.

**Veredicto:** el `0x1A` observado **no** sale del motor (`PbStart` no puede fallar y el pre-motor sólo da `0x0A`); sale de
una guarda, y de las dos sólo la **guarda B** admite una causa de contenido/BD. La vía «hardware/DMM/av-cam» queda
**descartada** para los seis códigos.

## 4. Comprobación física en un solo paso

**Un paso, sin depurador:** activar `testmode_debugPrint` de MPR y reproducir el clip. La cadena que aparezca decide:

| Cadena en el log | Guarda | Sitio | Conclusión |
|---|---|---|---|
| `Pb Disable!! ref) dsm get` | A (capacidades) | `0x437C0A` | estado de AviMMgr, no BD |
| `Detect UnSupported Content` | B (contenido) | `0x437C3C` | si además hay `isSupportContent : Can't get condition` ⇒ catálogo/BD |
| `MovieReadStart : ER_SEQUENCE` | pre-motor | `0x6086D4` | estado MMgr, código final `0x0A`, no `0x1A` |
| ninguna de las tres | — | — | el `0x1A` llega por la máquina de pasos asíncrona (§5) |

**Si hay que leer memoria/PC:** un *breakpoint* de un solo uso en `0x447C0A` y `0x447C3C` (REA). Predicción falsable:
salta uno de los dos y **`0x447CFC` no salta nunca**; si saltara, esta lectura es falsa. Alternativa de lectura única:
palabra de 32 bits en `0xAE2920` (REA; `[0xAD28F8]+0x28` en ELF, leída por `0x1EEFDC`), que debería valer **1** en una
cámara NTSC — *INFERENCIA*: no he verificado la semántica del valor ni que la guarda B llegue a esa rama con este clip.

## 5. Límites

- **NO_VERIFICADO** que el `0x1A` real venga de la máquina de pasos asíncrona: `PbStart` publica el paso `0x102` por
  `0x2D7D20` (cola `0x5FDD20`/`0x5FDC84`) y vuelve; si esos pasos fallan, pueden emitir la finalización `0x4000001D` con
  otro código. No se ha traído esa ruta; si fuera así, los seis códigos volverían a estar en juego.
- **NO_VERIFICADO** el valor en ejecución de la máscara `[core+0xDB8]` (guarda A) y de `[AviMMgr+0x768]`.
- La identidad de clase (AviMMgr) se deduce del patrón de slots `+0x58/+0x5C/+0x60/+0xB4` y de los literales de cadena
  «isSupportContent»/«MovieReadStart»/«GetPlayMovieStatus» (únicos en el binario); **NO_VERIFICADO** que la instancia
  obtenida por `[core+0x1EC]` sea exactamente ésa en ejecución.
- Alcance: sólo `libmpr.so` y los llamadores directos; no se ha probado reachability completa hacia DMM/av-cam a más
  profundidad.
