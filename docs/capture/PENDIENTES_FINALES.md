# PENDIENTES FINALES — estado de cierre (22-10-2026, corregido)

Este es un informe histórico de alcance parcial, no una lista integral ni una
declaración de que la investigación esté cerrada. La [cola vigente y evidencia
faltante](repo-audit-2026-10-24.md) incluye las preguntas técnicas, S176 y los
límites de los censos y del triaje.

> **Actualización 24-10-2026:** [trazado de 0x40193](queue-40193-flow-2026-10-23.md).
> Se verifican literales en `.text`, emisores, receptor LIRO `0x4381d16c` e
> instalador `0x4379e93c`. La entrada de cabecera LIRO alcanza el bucle de 372
> inicializadores `0x4356082c`. `0x4379e8f4 → 0x43b2a162 → 0x43560bb0`
> consume el descriptor `0x43ea048c`. Pendientes: destino/efecto del servicio
> indirecto, callback OSAL Linux y enlace Linux↔LIRO. El supuesto bloqueo estático de §2
> y los «nueve falsos positivos» de §3 quedan invalidados.

> **Corrección del 23-10-2026:** las secciones 2–4 conservan conclusiones históricas
> superadas. La búsqueda MOVW/MOVT de `0x40193` era inválida y el flujo del ID
> sigue pendiente de análisis estático; `libObj.so` sí contiene el código local de
> `RecordStill::Execute` y llamadas candidatas a registradores OSAL. El censo
> vigente es 133/372 etiquetas documentadas, con 226 pendientes y 13 descartadas. Véase la
> [auditoría actual](../auditoria-2026-10-23.md) y S380–S385 antes de reutilizar
> cualquier conclusión de esas secciones.

## 1. B — canales MMIO CONFIRMADOS en av-cam.bin (corrige informe previo)

**VERIFICADO:** Los canales MMIO de B SÍ están en av-cam.bin del A6000 fw3.21:

| Dirección MMIO | Sitios | Tabla literal | Funciones |
|----------------|--------|---------------|-----------|
| 0xf3122300 | 36 | 0x436db000-0x436db0fc | Acceso a registro B (casos 0-5 del dispatcher TBB) |
| 0xf3122200 | 27 | 0x436db230-0x436db2fc | Acceso a registro B |
| 0xf3123200 | varios | 0x436db700-0x436db7fc | Acceso a registro B |
| 0xfc0a3100 | 41 | 0x436db7ac-0x436db7fc | Acceso a registro B |
| 0xf292b000 | 1 | 0x436dbe18 | Bloque base de escritura B |

**Dispatcher TBB en `0x436daf18`:** 6 casos (0-5) que saltan a:
- caso 0 → 0x436db214
- caso 1 → 0x436db3bc
- caso 2 → 0x436db5e8
- caso 3 → 0x436db790
- caso 4 → 0x436db9cc
- caso 5 → 0x436dbc08

Cada función usa `bfi` (bit field insert) sobre el valor leído del MMIO, confirmando que son accesos de registro a hardware.

**Efecto en S51:** Ninguno directo. Los canales MMIO existen pero no demuestran una ruta de exposición totalmente electrónica.

## 2. Cola `0x40193` — consumo comprobado; instalación incompleta

En `av-cam.bin`, `0x4381d16c` recibe de `0x40193`, consulta una tabla de
35 comandos y despacha el handler correspondiente. El inicializador
`0x4379e93c` instala su puntero en un descriptor; la entrada de cabecera LIRO
alcanza el bucle que llama ese inicializador. En `libObj.so` hay nueve palabras
del ID en `.text` usadas por cargas LDR, cuatro wrappers de envío y un
adaptador OSAL local. Véase el [flujo verificado](queue-40193-flow-2026-10-23.md).

**Pendiente:** destino y efecto del servicio indirecto que recibe el descriptor,
invocación concreta del registrador OSAL con `0x40193` y enlace completo
Linux↔LIRO. La ausencia de
MOVW/MOVT en un barrido no descarta cargas desde literal pool.

## 3. `libObj.so` — identidad de RecordImage y RecordStill

El `0x90b248` ELF de `libObj.so` se identifica como **RecordImage**, no como
`RecordStill::Execute`; `RecordStill` es un helper local llamado desde aquel.
La equivalencia histórica con A7S `0x847e1c` está rechazada por comparar dos
niveles distintos del flujo. El [contrato auditado](recordstill-contract-audit-2026-10-23.md)
documenta las parejas y los límites. La presencia de los emisores de `0x40193`
no resuelve por sí sola la ejecución efectiva de la captura electrónica.

## 4. Cobertura documental de módulos

El censo vigente tiene **133/372** etiquetas documentadas, **226 pendientes**
y **13 descartadas**; no mide funciones o capacidades verificadas. Consultar
el [censo detallado](../../analysis/s178_census/) antes de asignar nuevas tareas.

## 5. Decisión S51 — SIN CAMBIOS

**A=NO, B=NO, C=NO.** Ningún hallazgo de esta sesión altera la decisión. Los canales MMIO de B existen pero no demuestran una ruta de exposición totalmente electrónica.

## 6. Pruebas físicas P1-P8 (diferidas)

Son propuestas históricas. La decisión del usuario del 24-10-2026 difiere toda
prueba física hasta completar la decompilación o ingeniería inversa necesaria.

| Prueba | Objetivo | Riesgo |
|--------|----------|--------|
| P1 | Observar `0x83e9bd50` (G+0x808) en cambios de menú | Bajo |
| P2 | Forzar `0x808`=1 sin disparar | Bajo-medio |
| P7 | Prueba objetiva (hélice/LED) | Medio |

## Archivos generados/actualizados en la sesión histórica del 22-10-2026

- `docs/capture/PENDIENTES_FINALES.md` (este documento, corregido)
- `docs/capture/shutter-trigger-chain-0x3011.md` (C2 chain, actualizado)
- `docs/capture/capture-stage-reuse.md` (tabla de secuencias, actualizado)
- `docs/capture/sfra-electronic-frame-source.md` (productor YC SFRA)
- `docs/capture/sony-dcf-playback.md` (DCF/reproducción)
- `docs/capture/s134-svrnum-vdnum-status.md` (S134 writers)
- `analysis/rea-independent/out/C2_CHAIN_ANALYSIS.md` (C2 analysis)
- `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt` (desensamblado dispatcher C2)
- `analysis/rea-independent/out/c2_handlers_0x43808100.txt` (handlers dispatcher)
- `analysis/rea-independent/out/c2_handlers2_0x43808400.txt` (handlers adicionales)

Las conclusiones vigentes y sus límites están en las secciones 2–6 anteriores.
