# G21 — Informe: Picture Profile y Silent Shooting en la A6000 (08-11-2026)

Resumen de G15–G20. El CFW 3.56 está construido y auditado (25/25), **sin instalar** (requiere autorización expresa). El menú de
Picture Profile **no está construido**: está investigado y diseñado, sin código. Nada de esto se ha probado en cámara.

## 1. Construido

**CFW 3.56** (`.dat` SHA-256 `ebb7ee825b87a07f4afc485f2681a2b0df52d7333b33a0e21943c98237926728`, auditoría [`audit-3.56.json`](../../analysis/gui/audit-3.56.json)).
- Base: el 3.53 instalado (menú, Darwin v3, sin `nflasha5`). Solo cambian `nflasha15` y `part_image.sum`; `nflasha3`/`av-cam` quedan como en Sony.
- **Selector Silent Shooting**: `CautionConfig.so` del 3.54 (On = obturador electrónico, Off = EFCS).
- **Curvas PP desde la propia cámara**: `s_start_android.sh` lanza `pp_ram.sh` en cada arranque. Escribe por `/dev/mem` 7 curvas de vídeo de la A7S,
  5 punteros y 7 entradas de la tabla selector→gamma. Antes comprueba con `md5sum` los 19 sitios (si alguno difiere, no escribe); después relee y
  repite la comprobación a los 60, 600 y 3600 s. No es persistente. Modo de prueba: a los 20 s fuerza Cine1.
- Verificado sin cámara: emulación Unicorn de la selección de gamma (3 → `0x16`, 6–9 → `0x18`–`0x1b`) y `pp_ram.sh` con el busybox de la cámara bajo qemu (19/19 rangos; una segunda pasada se niega a escribir).
- Qué mirar tras instalar: arranque como el 3.53; selector Silent On/Off; `/android/data/pp_ram.log` = «pp_ram: OK» sin «alterada»; en vídeo, contraste más suave de Cine1; fotos sin cambios.

## 2. Investigado

| Tema | Conclusión | Informe |
|---|---|---|
| A6000 frente a A6300 | La A6000 no tiene nada de la interfaz PP (29 ajustes, 25 clases, 2 vistas); la `libObj` sí | [G15](g15-picture-profile.md) |
| Núcleo `av-cam` | Aplica curvas por número de gamma como la A7S; faltan 7 curvas de vídeo y la tabla; solo `0x1c`/`0x1d` necesitan código | [G16](g16-picture-profile-nucleo.md), [G17](g17-picture-profile-plan-c.md) |
| Espacio para las curvas | Ampliar `av-cam.bin` descartado; hueco de 40 KB sin referencias estáticas (límite: acceso calculado en ejecución); elegida escritura en RAM desde la cámara | [G18](g18-pp-espacio-y-cfw-355t.md) |
| Capa de modelo | `@M00B` 0x40 aplica el PP (10 perfiles × 31 parámetros) y la consulta 0x49 lo lee; claves `0x1f8 + 4·i` (gamma `0x214` escritura, `0x216` lectura) iguales que en A6300 y A7S | [G19](g19-menu-pp-capa-modelo.md) |
| Gammas admitidas | Movie, Still, ITU709, Cine1–4. ITU709(800%) y S-Log2 no existen en la `libObj` de la A6000 | G19 §2c, [G20](g20-menu-pp-construccion.md) |
| Fuente del port | La A7S tiene la misma organización que la A6000, pero su clase base tiene 24 ranuras virtuales frente a 22: **no se trasplanta el binario** | G20 |
| Código propio | Una biblioteca C++ compilada con clang carga y se ejecuta con el cargador de la cámara (glibc 2.11) en qemu | G20 |

## 3. Pendiente del menú

Diseño: biblioteca propia `libpp.so` (ajustes + entradas de menú), cargada como dependencia de `cmn_view_processDataMgr.so`
(hay que mover su tabla de dependencias a un segmento nuevo), con la tabla de ajustes ampliada (`0xe8`) y las entradas colocadas con
`add_menu_entry.py`. Orden: Gamma, resto de parámetros, PP1–PP9 y Copy/Reset, pantallas propias.

Sin resolver: qué curva es cada número de gamma; si la `libObj` reenvía el 0x4066 y deshace la gamma forzada; si el núcleo escribe en el hueco de 40 KB.

## 4. Enlaces

Índice de pendientes: [`PENDIENTES.md`](../PENDIENTES.md) (G15-A … G20-A). Scripts: `scripts/gui/` y `analysis/gui/g17`–`g20`.
