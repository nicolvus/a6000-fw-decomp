# S50 Codex — exposición y cortinas

Inicio: 2026-10-19; hora exacta recuperable en run/metrics.csv y daemon.out.

## Hito 0 — orientación y arranque

- Leídos AGENTS.md, STATE mediante MCP get_current_state, CURRENT y CONTEXT; S40–S49 indexados en context-mode junto con E019/E020, S19 y S21 pertinentes.
- Usadas skills knowledge-navigation, contradiction-audit, session-checkpoint. Las escrituras de mantenimiento global quedan excluidas por instrucción explícita del usuario.
- MCP de conocimiento consultado antes de releer documentos. Las relaciones entrantes sobre E020/S21 no prueban por sí mismas correcciones técnicas; deben cotejarse con instrucciones.
- Arrancado demonio propio S50_NAME=codex, GHIDRA_MAXMEM=4G con flock compartido. No usar socket Claude.
- Distinguir clase de configuración 1/2/3/6 (S49) de selector de exposición IMX210 0–4 y selector de secuencia externo/interno. P/C no equivalentes.

## Pendiente / siguiente paso

1. Esperar run/rea.sock.ready sin abrir otra sesión. Consultar por lotes selectores 43842158, 437eabfc, 437ea8cc, SetExposure 436d6320/436d6f6c, secuencias 43b1b0c8 y Stage_CaComm 438c2538.
2. Verificar hipótesis de rutas sin cierre y clase2 con bytes/instrucciones; si REA omite Thumb, respaldo histórico solo lectura.
3. Seguir fin electrónico, VD/lectura y dependencias sin duplicar configuración de Claude.
4. Informe docs/capture/s50-codex-exposure-curtains.md con estados, contradicciones, tiempo/memoria/fallos; shutdown propio al terminar. Sin commits.

## Hito 1 — antecedentes auditados, lote pendiente

- 2026-10-19 ~19:10 UTC: demonio propio activo (sesión exec81751); cliente pendiente exec5066 ejecutará 01-exposure.json al aparecer .ready. No lanzar otro demonio. El intento inicial nohup no persistió; se corrigió con proceso foreground mantenido por exec.
- Flock compartido esperó a Claude; frío propio comenzó ~19:07 UTC. Métricas hasta ahora <2.4GB RSS; GHIDRA_MAXMEM=4G, sin cambiar swap/kernel.
- Preparados 01-exposure.json y 02-sequence.json; el segundo NO ejecutado. S50Export.java disponible si REA omite funciones: solo lectura, no crea instrucciones.
- Auditoría manifiesto compartido: 1490 archivos protegidos, 0 diferencias (incluidos firmware, .gpr/.rep, antecedentes).
- LLVM preflight: analysis/rea-independent/run/av-cam-view.elf sección.text coincide byte a byte con av-cam.bin. VMA=0: --adjust-vma=0x43541000 imprime direcciones absolutas, pero --start/stop-address deben usar offsets crudos. Ensayo inicial con direcciones absolutas devolvió listado vacío; corregido.
- LLVM436d7114..714a confirma máscara94 y LDRB a parámetros+08/+14. Ninguna semántica eléctrica inferida.
- HYPOTHESES.md contiene H1–H7 y contraevidencia conocida. Mensaje enviado por append al inbox Claude distinguiendo dominios de clases.
- Inbox Claude: b6 no tiene fila callback en43ff7540..43ff8e88; REA omite varios Thumb. No se usó su socket ni sus archivos privados.

Siguiente: al completar 01, resumir identidad/cobertura y ejecutar02. Seguir Stage_CaComm y cap+74f, fila+12c, SetRead/VD. Cerrar sesión REA antes de abrir respaldo histórico si la memoria lo aconseja.

## Hito 2 — REA disponible y bypass diagnóstico identificado

- Lotes01–04 ejecutados, JSONL persistentes. Frío propio ~483s (ver eventoanalysis_ready para espera exacta). Muchos Thumb ausentes; Stage438c2538 absorbida en43b1be98. No asumir que el nombre del contenedor sea la entrada solicitada.
- 02 search_bytes en43541000..43bc0000: STRB.W+74f solo437df5e8,438acc9c,438c2562; LDRB.W enumera27 coincidencias. Cobertura de esa codificación concreta, no todos los escritores por copia/alias.
- 438ab3e8 copia source(param3)+142 a objeto destino+74f (438acc9c); identidad del origen aún abierta. 437df338 borra+74f al marcar cancelación/error.
- Stage438c2538: D=*(4402546c)=43e95950, derivación PIC verificada por bytes; D+7e!=0 y D+7f==captura+1d8 borra captura+74f. D+7e1/2/3 marca cap+4fd0 con1/2/4. Getter43ae7648 devuelve1 si bit0,2 si bits1..4. No es prueba de éxito sin cortina.
- 438d033c gate+74f envía eventos1/3; 438d025c también gatea inicialización. 436b89e0 construye tag12; 436bc140→436b93b0 lo procesa. No interpretar0x13a como opcodeDarwin sin demostrar436b96b4 (posible traza).
- Append a inboxClaude con lo anterior.

Siguiente: respaldo histórico para SetExposure436d6f6c, selector437ea8cc, init437ebed8, fila43b1c0e2, CaptureStart437df640 y43af6870 (REA ausentes); LLVM para gates y copiar valores. Antes cerrar REA, consultar getters y funciones adicionales necesarias en lote05. Informe final aún NO escrito.

## Hito 3 — corrección crítica de S49 y cierre de exploración

- REA cerrado con--shutdown; no quedan procesos propios. Lotes01–05:42peticiones de decompilación,33ok/9error (no equivalen a42funciones distintas). read_bytes11/11 contrastadas con firmware.
- Respaldos06/07/08/09 solo-readOnly/noanalysis,31consultas y raw64 verificados. Algunas entradas siguen sin función; resueltas por LLVM, sin sembrar ni modificar proyecto.
- CRÍTICO VERIFICADO: filas de servicio {key,slot,1/2/3/6} contienen CANTIDADES de callbacks, no clases de captura.43af68a4 escribe slot a+25c,43af68a8/aa copia row+8 a+260.437da2f2/f6/f8 compara cursor con+260,437da2fc indexa por4,437da314 llama,437da318..31e incrementa. Ba6punteros/b7tres/ceuno/b8dos comprobados. Append confirmado a Claude. Corrige S49; no modificar su archivo.
- Init437ebed8: base4401eee4; literal437eccb8→GOT44022934→43edccf8; literal437eccf8→GOT44021cc4→43b1c0e3. Call437ebfc0 con tabla+12c. Descriptor437de944 guarda funciónr1 en+8. Specialrow43b1c0e2 estado0→43b1d9dc→438d0d30 (evento12 condicionado+74f), estado1→437f22d4, estado2→437ed568; selector437ea8cc deja secuencia0 con+4b70=7.
- PrecisiónS21: petición inicial Stagecaso2→438d0420 envíaevento1 con+74f!=0; evento3 solo si getterstatus==1.438d033c(1,3) es retry/cancelcaso0. No tratarlos como dos eventos iniciales incondicionales.
- BypassD+7e=1/2/3 también marca status1/2/4. D=43e95950, NO C. El escritor438acc98/9c verifica r4+142→r3+74f; decompilador compartido une cuerpo a438ab3e8, no promover identidad param3/destino sin más prueba.
- audit.py PASS:1490 protegidosintactos,31consultashistóricas,11lecturasREA y19rangosLLVM (se ampliará a22 para tag12MMIO).
- Ruff src/tests mantiene9avisos previos; ninguno propio. Mypy src+audit PASS6archivos. No reformatear ni corregir ajenos.
- MétricasREA104muestras,19:01:36–19:18:46UTC, RSSmáximo2333MB, MemAvailable mínimo2954MB; wait_lock340.9s,cold489.9s. GHIDRA_MAXMEM4G sin aumento. Histórico3G después del shutdown, fuera del watchdogREA.

Siguiente: escribir informe final, revisar correcciones/limitaciones y tiempo; última auditoría si hay cambios de auditor, ruff/mypy solo si justificado, asegurar procesos cerrados. No mantenimiento global, sin commits por orden del usuario.

## Cierre — S50 B terminado, límite físico explícito

- Informe: docs/capture/s50-codex-exposure-curtains.md (138 líneas antes del último ajuste editorial). Respuesta física NO_VERIFICADO, sin afirmar imposibilidad. Corrección principal S49:1/2/3/6 son cantidades, no clases.
- Auditoría final: run/audit.log PASS;1490 protegidos intactos,11lecturasREA,31consultas históricas,22rangosLLVM. Geometría CamCore43bc16dc+28/+60=6000/4000 comprobada; tabla864x4176 en43bc1ae8.
- Tag12 interno:43b5e2b0 verifica banco<=17, r2=0 y B.W4398f9a4;4398f9bc..c8 escribe1<<bit en f2910048+banco*100. No tratarlo como tramaDarwin; mapeo eléctrico banco/bit NO_VERIFICADO.
- Ruff final mantiene9avisos ajenos y0propios; mypyPASS6archivos. Logs enrun/ruff.log yrun/mypy.log.
- Shutdown propio confirmado sin procesos Java propios. Artefactos de socket/ready retirados con unlink comprobando tipos/contenido; un intento rm-f fue rechazado por herramienta y no ejecutó eliminación.
- Sin commits, push ni mantenimiento global. No actualizar README/CURRENT/PROGRESS/grafo: usuario restringe expresamente escrituras.

Próximo paso de investigación (no ejecutado): identificar el efecto eléctrico de ID1/100/101 y los parámetros realizables de clase2, además del vínculo con gatecap+74f y lectura completa. No volver a interpretar cantidades1/2/3/6 como modos. No hay sesiónREA que reanudar; una futura requiere nuevo arranque autorizado por su tarea.
