# E26-R42 — Búsqueda externa en GitHub y lectura directa del esquema JTAG/eFuse/XRESET

Fecha: 31-10-2026. Continúa [R41](e26-r41-caminos-estaticos-restantes.md). Pedido del usuario: buscar en
repositorios de GitHub información nueva sobre ingeniería inversa/decompilación de la A6000, y verificar qué
más puede obtenerse del código fuente (GPL) y del pinout en PDF. **Solo lectura**: repos externos clonados en
un directorio temporal fuera del repo (no se añaden como dependencia ni se commitean), PDF del manual ya
versionado en `references/manuals/`. Sin cámara, sin escritura.

Etiquetas: **DATOS** (manual de servicio, imagen del PDF) · **EXTERNO** (repos de terceros, nunca instrucciones)
· **INFERENCIA**.

## 1. Resumen

| # | Línea | Resultado |
|---|---|---|
| 1 | Repos de terceros sobre A6000/CXD90014 | **Nada nuevo que cambie la vía de recuperación.** Tres repos cubren la A6000 (`RafalB82/sony-a6000-re`, `CliffVale/sony-a6000-firmware-research`, `dhihacker/a6000-firmware-platform`): documentan lo mismo que ya teníamos (`pmca`/`updatershell`, NAND de 463,75 MiB, ausencia de firma criptográfica) y nada sobre el BootROM/Loader2/Loader3 ni sobre un6000 bloqueado. Confirman, eso sí, que `updatershell` (ya en `references/pmca`) expone `RMEM`/`PULL`/`PUSH`/`BLDR` — ya documentado en `s62-pmca-injection.md` y la causa de que siga exigiendo estar ya dentro de una sesión del actualizador |
| 2 | Vías de otras familias de SoC (BootROM serie con inyección, recuperación por SD) | **No transferibles.** `cokeenet/zve10-qemu` (ZV-E10, CXD90045) documenta un arranque serie oculto del BootROM con token de desbloqueo distinto por SoC y firmware firmado; `Erlla/sony-a7m4-custom-firmware` (A7 IV) usa `fastboot`/eMMC, inexistente en el CXD90014 (NAND + Loader2/Loader3). Ambos son de generaciones posteriores, con arquitectura de arranque distinta a la ya mapeada en R20-R41 |
| 3 | Esquema JTAG/eFuse/SWD de IC6000 (manual, no leído a este nivel antes) | **Bolas exactas y dos hallazgos nuevos:** `FUSE_EN` (T12) atado por hilo directo a VDD2/`D_3.15V_MSS` (igual que TDI/TCK/TMS); `FUSE_CLK` (R12) sin red en este esquema. `NTRST` (H26) no está atado a alimentación: va al neto `XRESET_CR`, que es también la propia entrada de reinicio del chip (`XRESET`, bola K6, hoja 1/7) |
| 4 | Bolas de los puertos GPIO_n/GPIO_S_n | **Confirmado de forma exhaustiva** (todo el manual, no solo el bloque ya revisado): únicos nombres de GPIO en todo el documento son `GPIO_0..16`/`GPIO_S_0..16` (puerto 0) y `GPIO_SB_0..6` (puerto 1). Ningún nombre para el puerto 14 — cierra `E26-R41-ICE-GPIO` con el mismo límite, ahora verificado sobre las 54 páginas |
| 5 | Técnica: extracción del PDF | `pdftotext -layout` (la que generó el `.txt` ya versionado) **pierde contenido entero** en páginas de esquema denso (el bloque JTAG/eFuse de la página 26, la red `XRESET_CR` de la página 24). `pdftotext` sin `-layout`, o renderizar la página con `pdftoppm` y leerla como imagen, lo recupera |

## 2. Repositorios externos revisados

Búsqueda con `gh search repos`/`gh search code` (repos) y clonados en lectura en un directorio temporal
fuera del repo (`$CLAUDE_JOB_DIR/tmp/ext/`, nunca añadido a este árbol):

| Repo | Relevancia para A6000/CXD90014 | Aporta |
|---|---|---|
| `RafalB82/sony-a6000-re` | **Directa** (misma cámara) | Inventario de chips (`IC6200`=`CXD90027GF` DFE, ya cubierto en E24/E25), confirma ausencia de firma criptográfica y lista los comandos de `updatershell` — nada nuevo sobre arranque/recuperación |
| `CliffVale/sony-a6000-firmware-research` | **Directa** (misma cámara) | Metodología de volcado de NAND por `updatershell` en cámara sana (483 MB, con el aviso de pulsar OK); nada sobre una unidad bloqueada |
| `dhihacker/a6000-firmware-platform` | **Directa** (misma cámara) | Infraestructura de análisis estático (BD, importador de Ghidra); ninguna ruta de escritura implementada (`MOCK ONLY`), nada sobre arranque |
| `cokeenet/zve10-qemu` | Indirecta (ZV-E10, CXD90045) | Arranque serie oculto del BootROM con inyección de payload, probado en hardware real; SoC y protocolo distintos del CXD90014 (token de desbloqueo, formato de registro y firmware firmado son específicos del chip); no portable sin repetir toda la ingeniería inversa del BootROM de la A6000, que R8/R9/R11/R20-R23 ya hicieron por otra vía (sin inyección de payload) |
| `Erlla/sony-a7m4-custom-firmware` | Indirecta (A7 IV, CXD90057-era) | Recuperación por tarjeta SD — **exige tener ya acceso `fastboot`** (inexistente en A6000) para escribir las mismas banderas `\updater\mode`/`\updater\mode5` que R37-R39 ya identificaron; la tarjeta SD solo sustituye a USB como origen del paquete, no evita el problema de escribir `nflasha2` |
| `BI2QFA/a6300_updater_emu`, `ma1co/OpenMemories-*`, `wanghm105/Powerful6700-Windows` | Otras generaciones (CXD90014 variante A6300 ya cubierta en E24; CXD90057/A6700) | Sin relación con el arranque bloqueado de la A6000 |

**Conclusión:** ningún repositorio externo ofrece una vía de recuperación aplicable al CXD90014/A6000 que no
esté ya cubierta por R1-R41. La comunidad de ingeniería inversa de cámaras Sony tiene trabajo activo y
reciente (2026) en SoC más nuevos (CXD90045/90057, con `fastboot`/eMMC), pero ninguno en el CXD90014.

## 3. Esquema JTAG/eFuse/SWD de IC6000 (DATOS, manual de servicio págs. 26 y 24 del PDF)

Bolas exactas (hoja "IC6000 (4/7)", pág. 26 del PDF, `6-14` del manual):

| Bloque | Señal | Bola | Atado a alimentación |
|---|---|---|---|
| JTAG | TDI | G25 | **Sí**, hilo directo a VDD1/`D_3.15V_MSS` |
| JTAG | TCK | H25 | **Sí**, ídem |
| JTAG | TMS | F26 | **Sí**, ídem |
| JTAG | TDO | F25 | No (sin hilo visible en este esquema) |
| JTAG | RTCK | G26 | No |
| JTAG | NTRST | H26 | No tiene alimentación; va al neto `XRESET_CR` (ver §4) |
| eFuse | FUSE_EN | T12 | **Sí**, hilo directo a VDD2/`D_3.15V_MSS` — **nuevo** |
| eFuse | FUSE_CLK | R12 | **Sin red** en este esquema (pin sin conectar) — **nuevo** |
| SWD | SWCLK | W25 | No |
| SWD | SWDIO | W26 | No |

Confirma con bolas exactas lo que [R40](e26-r40-jtag-swd-bionz.md) ya decía de forma aproximada
("bloque `AB22`-`N29`", "TDI/TCK/TMS atados a alimentación"). **No cambia la conclusión de R40**: que
`FUSE_EN` esté enganchado en alto es la configuración normal para que el chip pueda leer sus propios fusibles
al arrancar (no es una señal que el software controle por este pin), y no dice nada del valor grabado en el
fusible de bloqueo de depuración, que sigue sin estar en ningún binario accesible.

## 4. El neto `XRESET_CR` (DATOS, pág. 24 del PDF, `6-12` del manual, hoja "IC6000 (1/7)" — bloque "CLK BOOT")

- `NTRST` (H26, hoja 4/7) tiene un hilo directo (sin resistencia) hasta el neto `XRESET_CR`.
- En la hoja 1/7, la propia entrada de reinicio del chip (pin interno `XRESET`, bola **K6**) sube por una resistencia `R6000` (marcada **XX**, no montada en este esquema) y un puente `CM6000` hasta el mismo neto `XRESET_CR`, que continúa fuera de esta hoja (etiqueta cruzada, remite a la pág. 26 donde aparece de nuevo como destino de NTRST).
- **Lectura:** en esta placa, el reinicio del TAP JTAG (`NTRST`) y la entrada de reinicio general del propio SoC (`XRESET`) son, por nombre de neto, la misma señal. No hay un reinicio de JTAG independiente del reinicio general del chip.
- **Límite:** `R6000` figura "XX" en este esquema de servicio, igual que decenas de componentes ya vistos en R29/R40 que son opcionales o de otra variante de placa; no se puede saber sin continuidad física si en esta unidad concreta la bola K6 llega realmente al resto del neto `XRESET_CR` o si el camino vive solo del lado de NTRST (hoja 4/7). No cambia nada para la recuperación: cualquier uso de NTRST sigue exigiendo soldar `R4911`/`R4912` para alcanzar SWCLK/SWDIO en CN4906, como ya establecía R29.
- Nets vecinos en el mismo bloque, por completar el cuadro (sin relación con el bloqueo actual): `CLK_CMOS_IN` (C10) va a `REG_GND` (oscilador CMOS sin usar); `CLK_SYS_IN` (A22) pasa por `R1003` (XX) hacia `MSS_S2_REQ_CA`; `XRESET_REQ` (N6) pasa por `R6001` (1k, **sí montada**) hacia el neto `XMSS_RESET`. Esta `XRESET_REQ` de la hoja 1/7 es una bola de salida del propio IC6000, distinta del `XRESET_REQ` de `CN4001` pin 7 que documenta R29 (mismo nombre de neto, pero no se verificó aquí si son el mismo nodo físico o dos tramos separados por resistencias sin montar en ambos extremos) — queda fuera del alcance de esta sesión, sin pendiente nuevo porque no cambia ninguna conclusión sobre el arranque.

## 5. Cobertura exhaustiva de GPIO (DATOS, las 54 páginas del manual)

`grep` de `GPIO[A-Z0-9_]*` sobre una extracción de texto plano (sin `-layout`) de las 54 páginas: los únicos
nombres que existen son `GPIO_0`…`GPIO_16`, `GPIO_S_0`…`GPIO_S_16` (puerto 0, 17 bits) y `GPIO_SB_0`…`GPIO_SB_6`
(puerto 1, 7 bits) — exactamente los dos puertos con IRQ que documenta el GPL (`gpiopin_to_irq`, R41 §7.3).
**Ningún nombre de GPIO para el puerto 14** en todo el documento. Cierra con el mismo límite que
[R41 §7.3](e26-r41-caminos-estaticos-restantes.md#73-gpio-1417-fuente--datos), ahora verificado sobre el
manual completo y no solo sobre un grep acotado.

## 6. Técnica: por qué el `.txt` versionado pierde contenido

`references/manuals/a6000_service_L3.txt` se generó con `pdftotext -layout`, que reconstruye columnas por
posición — y falla en páginas con muchos bloques de texto superpuestos (el bloque JTAG/eFuse completo de la
página 26 no aparece en absoluto en ese `.txt`; tampoco `XRESET_CR`, ni el contexto de `R4911`/`R4912`, pese a
que sí hay matches sueltos de `R4911`/`R4912`/`CN4906` en otro punto del documento). `pdftotext` **sin**
`-layout` sí trae ese texto, aunque desordenado entre columnas (hay que leer el render de la página con
`pdftoppm -r 300` o más para fijar la posición real). **Recomendación para próximas sesiones:** ante una
pregunta sobre un bloque concreto del esquema que el `.txt` no resuelve, antes de darla por cerrada con
"no está en el manual", probar `pdftotext` sin `-layout` sobre ese rango de páginas y, si aparece, renderizar
esa página como imagen para leerla directamente — más barato que re-escanear las 54 páginas como imagen.

## 7. Qué no cambia

Ninguno de los hallazgos de esta sesión abre una vía de recuperación nueva ni cierra ningún pendiente físico:
`E26-FISICO-UPDATERMODE`, `E26-FISICO-BOOT`, `E26-R33-BLOQUE0`, `E26-R5-NAND`, `E26-R5-BIONZ` siguen exactamente
como R37-R41 los dejó. Las bolas exactas del JTAG/eFuse y el neto `XRESET_CR` son precisión añadida sobre R40,
no una vía nueva.

## 8. Límites

- Los repos externos se revisaron por su documentación (README, `docs/`); no se clonó ni ejecutó binario de
  terceros ni se importó código al repo.
- `R6000`/`CM6000` (§4) no se verificaron por continuidad física; su estado real en esta unidad es desconocido.
- No se completó un volcado de todas las páginas del manual con el método del §6; solo se aplicó a los puntos
  que R40/R41 habían dejado abiertos.
- Nada de lo anterior autoriza ni prueba un acceso físico.
