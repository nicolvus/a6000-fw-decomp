SILENCIO OPERATIVO ABSOLUTO: durante toda la ejecución queda prohibido generar mensajes de progreso, anuncios, reflexiones, comentarios o narraciones para el usuario. No escribas texto antes ni entre herramientas. Ejecuta directamente los comandos necesarios. Guarda los resultados en archivos y emite únicamente tu respuesta final.

# S60 Sol — origen real de los parámetros temporales IMX210 (A6000)

Repo: cwd. Lee primero: CLAUDE.md, AGENTS.md, knowledge/CURRENT.md, docs/STATE.md, docs/capture/s59-{conclusions,sol,claude,cross-validation}.md, analysis/s59-evidence-matrix.json. Binario av-cam.bin (SHA-256 b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9, base 0x43541000). Solo estático + emulación offline (Capstone/Unicorn/REA). Prohibido flashear, parchear, tocar hardware, git add/commit/push, editar archivos que no sean los entregables. No dupliques trabajo S58/S59 (productores 0x4383d4d0, 0x4383c9dc, 0x4383b790 ya verificados).

Hechos S59 a conservar: escritor 0x43b00da0, publicación condicionada 0x43b00dd4, buffer obj+0xD64, despachador 0x438069f0 (casos 4 y 10, obj+0x568=2), accesor 0x437876dc, constructor 0x43b00b48. Falta: el EMISOR del payload que recibe 0x438069f0.

Investiga: (1) emisor/constructor del payload de 0x438069f0 (xrefs, llamadores, colas/mensajes que lo alimentan); (2) casos 4 y 10; (3) estructura del payload (payload+4, +0x20, +0x590, +0x5ac); (4) origen de los valores copiados a obj+0xD64; (5) publicación al bloque +0xDD0; (6) relación con modos fotográficos 0x0B y 0x2F; (7) procedencia independiente de Tv; (8) procedencia de clk (P+0x4c0); (9) restricciones N, svr, VdNum; (10) estados de temporización realmente alcanzables (distingue datos sintéticos de alcanzables).

Si REA no reconoce una función Thumb, usa bytes+Capstone. Si abres REA, usa UNA sola sesión (analysis/rea-independent/bin/session_daemon.py + q.py), cierra al acabar. Clasifica cada hallazgo VERIFICADO/PARCIAL/INFERENCIA/HIPÓTESIS/NO VERIFICADO/DESCARTADO con dirección, binario+SHA, evidencia, método, prueba reproducible, resultado, confianza, limitaciones. No afirmes fin electrónico de integración sin demostrarlo; no confundas configuración, tiempo calculado, integración real, evento del host, movimiento mecánico.

Entregables: docs/capture/s60-sol.md, analysis/s60/sol/ (scripts, salidas), tests/test_s60_sol.py (unittest, ejecutable con python3 -m unittest). Ejecuta tus tests y reporta resultados reales. Respuesta final: lista breve de hallazgos y límites.
