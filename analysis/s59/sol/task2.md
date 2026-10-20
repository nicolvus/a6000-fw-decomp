SILENCIO ABSOLUTO: no emitas comentarios, narraciones, mensajes de progreso, reflexiones ni explicaciones para el usuario durante la ejecución. Trabaja mediante herramientas, guarda tus hallazgos en archivos y proporciona únicamente el resultado final solicitado. No anuncies acciones entre herramientas.

# S59 — Revisión cruzada (solo lectura) de las conclusiones de Claude sobre A7S/IMX235

Sandbox read-only: NO modifiques archivos. Tu único resultado es el mensaje final (≤60 líneas).

Revisa críticamente: docs/capture/s59-claude.md, tests/test_s59_claude.py, analysis/s59/claude/{ctor_emu,real_scen,modediff,p2s59,diverge}.py y modediff_*.json / real_scenarios.json. Contexto: docs/capture/s58-imx235-full-emulation.md, s58-a7s-silent-effective-diff.md. Firmware A7S: firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin (base 0x43541000). Herramientas: analysis/s58/tdis.py (dis), python3 con Capstone/Unicorn; puedes ejecutar los tests y scripts leyendo (no escribas en el repo; si un script escribe, ejecútalo copiando a /tmp).

Busca y reporta, citando dirección/instrucciones y clasificando VERIFICADO/PARCIAL/INFERENCIA/HIPÓTESIS/NO VERIFICADO/DESCARTADO:
1. Errores de interpretación (p.ej. constructor 0x436f3fc0, lista blanca {0x0b,0x35,0x37,0x38} en 0x436f5b84–0x436f5b96, base P2S 0xfc088300 vs 0xf3c00300, único llamador 0x436f459c).
2. Dependencias artificiales (objeto/ctor, stubs, página 0 mapeada, ambito de ejecución, entradas fijas).
3. Problemas de alcanzabilidad (¿los modos 0x4c-0x4f se alcanzan realmente con ese estado? ¿el byte de depuración [dbg+0xc] puede cambiar la lista blanca?).
4. Hipótesis alternativas (p.ej. 0x1000/0x1001 como tráfico de trazas vs control; por qué los mensajes faltan en Silent).
5. Contradicciones con S58 o con tu propio informe s59-sol.md.
6. Evidencia insuficiente o sobreafirmada.
Verifica por tu cuenta al menos: el llamador único de 0x436f459c (barrido), la lista blanca, y la afirmación «solo difieren los emisores de mensajes» entre 0x0b y 0x4e/0x4c en Execute. Indica qué afirmaciones confirmas, cuáles corriges y qué pruebas ejecutaste realmente. No atribuyas verificaciones no realizadas.
