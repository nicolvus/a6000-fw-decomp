# G65 — Live ND y acumulador `MULTIEXP-ACC` F1: punto de enganche del YC antes del JPEG (parcial)

Fecha 15-11-2026. REA estático sobre `av-cam.bin` 3.21 (sesión propia, cerrada) + Capstone + Unicorn. Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`. Código: `scripts/g65/jpeg_hook_patch.py`; test `tests/test_g65_jpeg_hook.py`.

## 1. Números de Live ND (ND = N fotogramas promediados; T = 66,8 ms por lectura completa Silent, ≈ 15 fps, techo no medido en ráfaga, g51 F2)
| ND | N | ventana cubierta (N·T) |
|---|---|---|
| ND2 | 2 | 0,13 s |
| ND4 | 4 | 0,27 s |
| ND8 | 8 | 0,53 s |
| ND16 | 16 | 1,07 s |
| ND32 | 32 | 2,14 s |

Hueco relativo = 1 − t/T (t = exposición por fotograma, T = 66,8 ms): 1/60 (16,7 ms) 75 %; 1/45 67 %; 1/30 (33,3 ms) 50 %; 1/20 (50 ms) 25 %; 1/15 (66,7 ms) ≈ 0 %.
Acumulador: 24 MP YC422 = 45,8 MB (1 buffer de 8 bit); sumar en 16 bit por canal = 91,6 MB.
**Condición de utilidad**: movimiento continuo solo con t ≥ 1/20 (hueco ≤ 25 %), idealmente 1/15; con 1/30 o más rápido el resultado es estroboscópico (copias discretas). Es decir, Live ND sirve cuando la escena ya pide ~1/15–1/20 a ISO base (sombra, interior, ocaso con diafragma cerrado); a pleno sol (1/250+) el hueco pasa del 90 % y no sustituye a un ND físico. Además cada ND-N solo promedia: el brillo no baja salvo que se acumule promediando t corto (la exposición efectiva por fotograma es la que fija el diafragma/ISO).

## 2. F1: cadena hasta el codificador JPEG (verificada con bytes)
- `Stage_EncodeJpeg_MainYC`: la cadena `[IMAGING_CAP]: Err: Stage_EncodeJpeg_MainYC` (`0x43cc8828`) se usa en `FUN_43b1aca6` (cuerpo en `0x438c6e90..0x438c6fc5`, máquina de estados `FUN_43afdf16`: caso 1 = codificar, caso 2 = THM, caso 3 = `0x437ed568`). Hermana `…GolfShot_THM`.
- Camino del caso 1: `FUN_43ae8220` (tabla de 10 handles) → `FUN_437faf0c(ctx+0x4ec0, ctx+0x4afa, 0, ctx+0x4efa …)` (`bl` en `0x438c6f0e`) construye la descriptor del YC (`FUN_437fae50` → `FUN_437fac18`, objeto de imagen vía singleton `FUN_43561604`, método vtable `+0x308`) y devuelve un **handle u16** (0xFFFF = fallo) = `r6` → `bl 0x438c6d30` (`0x438c6f68`) arma el mensaje de 0x54 B (estado 0x2000/6/0x54, tamaño máximo `FUN_437f8244`, salida en `ctx+0x4ecc`) y lo envía al motor JPEG (`FUN_43797b60`/`FUN_43797bcc`) → éxito: `FUN_437f4ea4(ctx+0x4bb0, …, dirección JPEG ctx+0x4ecc, tamaño)` guarda dirección/tamaño del JPEG en `ctx+0x4bb0+0x120/0x124` (`0x438c6fa6`) → `FUN_43ae827a(obj, r6)` (`0x438c6fae`) **libera el handle del YC**.
- Datos: el YC no se pasa por puntero sino por handle (id de unidad `ctx+0x4ec0` + índice `ctx+0x4afa`; bloque `ctx+0x4b70..0x4fe0` copiado desde `ctx2+0x27e4` por `Stage_DevLater` `0x437edaf8`, s20). Dirección física, paso de línea y formato (YC422) **NO VERIFICADOS**: están tras `FUN_43561604`+0x308, tabla virtual solo conocible en ejecución.
- **Punto de enganche estable**: `0x438c6f68` (`bl 0x438c6d30`, bytes `fff7e2fe`): el revelado terminó (handle válido en `r6`, `ctx+0x4ecc` ya reservado) y el YC aún no se ha liberado; `0x438c6fae` es el último punto donde existe. 
- Persistencia: el YC se libera por handle tras cada JPEG (`0x438c6fae`) ⇒ **no persiste entre tomas**; el acumulador debe ser memoria propia. Zona reutilizable de 46–92 MB: **no localizada** (pista: reserva RAW `0x437e1e48`, g51; el único llamador arma `0x437df338`). Pendiente.
- Otras etapas YC: `Stage_RchRcv_Resize_AutoReview` `0x43cad765` (xrefs `0x437f462c/0x437f463c`, `FUN_43b1a922`), `Stage_Rcv_DistResize_PreReview` `0x43cc8792` (xrefs `0x438c5af8/0x438c5b00`, `FUN_43b18326`).

## 3. Prueba de concepto
`scripts/g65/jpeg_hook_patch.py`: `bl 0x438c6d30` (`0x438c6f68`) → cueva vacía `0x44018250` (zona a cero, sin uso previo en el repo) que incrementa un contador en `0x44018290` y sale con `b.w 0x438c6d30` (cola: r0/r1/lr intactos, vuelve a `0x438c6f6c`). Unicorn: original = contador 0, parcheado 3 llamadas ⇒ contador 3, r0 conservado y retorno a `0x438c6f6c`; test de bytes originales (`fff7e2fe`) y de cueva a cero. Límite: el destino se sustituye por un stub; la escritura del contador en RAM de código no está comprobada en cámara.

## 4. Veredicto Live ND: PARCIAL (viable con condiciones)
Útil con t ≥ 1/20 s; ráfaga Silent a ≈ 15 fps no medida. F1 de `MULTIEXP-ACC` avanza: enganche y ciclo de vida del YC localizados; faltan dirección/formato (leer el handle en ejecución) y la reserva del acumulador.


> Actualización 15-11-2026 ([g74](g74-auditoria-cuevas-campana.md)): la cueva/contador pasaron de `0x44018250` (memoria viva) a `0x43541700`/`0x43541740`.
