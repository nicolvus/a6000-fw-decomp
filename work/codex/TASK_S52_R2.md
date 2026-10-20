# S52 — Agente B (Codex), ronda 2: profundizar (el coordinador considera la ronda 1 insuficiente)

Mismas reglas, entradas y prohibiciones que `work/codex/TASK_S52.md`. Parte de tus entregables de ronda 1 (no los borres; amplíalos).
La ronda 1 no usó REA ni Unicorn y dejó B2/B4 a nivel de resumen. Esta ronda debe producir evidencia nueva sustancial.
Tiempo esperado: investigación larga; no termines hasta agotar cada punto o documentar su frontera exacta.

## 1. REA obligatorio
Abre tu sesión REA A7S con el daemon (`work/codex/run/rea.sock`, ver TASK_S52.md). Claude ya tiene otra abierta: comprueba
`free -g` (≥3 GiB disponibles) antes; si no, espera y avanza con LLVM. Registra en `s52_evidence.json` qué consultas REA hiciste.

## 2. B1 — cerrar o acotar clase → `param+9` (prioridad)
Pista propia: la política `0x438649bc` guarda la clase con `str r1,[r2,#0x5c]` donde r2 ∈ destinos PC-relativos `0x43f06d5c..0x43f06d98`.
a) Determina exactamente qué estructura/global es (¿array por instancia/canal?, ¿qué índice elige cuál?).
b) Encuentra TODOS los lectores de `<esa estructura>+0x5c` (escáner PC-relativo `work/claude/scripts/pcrel_scan.py` sobre todo el binario
   para cada base 0x43f06d5c..98 y para la base de la estructura; `ldst_imm_scan.py` para `#0x5c`; REA `xrefs`/`procedure_references`).
c) Encuentra todos los llamadores del slot virtual `+0x28` (SetExposure) de los objetos `C_ImagerCtrl_*` en A7S: patrones
   `ldr rX,[obj]; ldr rY,[rX,#0x28]; blx rY` y wrappers equivalentes al A6000 `0x436d6320`; identifica quién construye el struct
   cuyo byte +9 es ShutMode y de dónde sale ese byte. Haz lo mismo en A6000 y compara.
d) Resultado: cadena de instrucciones completa, o la frontera exacta (qué función/indirección no se pudo resolver y por qué).

## 3. B2 — emulación offline con Unicorn (`~/.venvs/re/bin/python`)
Emula SetExposure IMX235 `0x436f4168` y IMX210 `0x436d6f6c` sobre copias en memoria de los blobs (mapear el blob en 0x43541000,
RAM simulada para globals/objeto/param, hooks que devuelven en llamadas externas registrando argumentos). Para cada ShutMode
(IMX235: 0,1,2,3,4; IMX210: 0..4) y para 2–3 valores de SHR/tiempo, registra TODAS las escrituras de memoria (dirección, tamaño, valor)
y las llamadas salientes con argumentos. Produce `s52_shutmode_emulation.json` y una tabla diferencial 0 vs 1 vs 3 en
`s52_imx235_imx210_comparison.md` (ampliado), con las instrucciones que causan cada diferencia. Script reproducible en `s52/`.
Sigue después las llamadas salientes (aplicadores/transporte, p. ej. `0x43ada042`) hasta el punto donde los bytes se empaquetan para
el sensor (cola, buffer de comandos, MMIO del SoC): esa es la frontera de B5.

## 4. B4 — clasificación de los 45 campos
Para cada campo distinto col 0 vs col 12 (y col 13), localiza qué funciones leen esa dirección de campo (ptr de la fila de la matriz,
`work/claude/out/a7s-imx235-setmode-matrix.json`) y qué hacen con él (p. ej. lo combina SetExposure con SHR → temporización/integración;
lo usa el cálculo de líneas/HMAX/VMAX → velocidad de lectura; geometría → ventana). Clasifica solo con evidencia de uso; el resto
NO VERIFICADO. Completa `s52_sensor_register_trace.csv` con columnas: fila, campo, valores col0/col12/col13, función lectora, uso, clase.
Repite para IMX210: qué columnas/campos difieren entre sus modos `0x0b` y `0x2f`, y si alguno de sus 13 modos tiene geometría de
resolución completa con el patrón que en IMX235 distingue col 12 de col 0.

## 5. B3 — quién invoca ShutMode 0 en A6000
Con los llamadores de (2c) en A6000: ¿alguna ruta (vídeo, LV, AF, ráfaga, bracketing, modo servicio) produce param+9 = 0? Demuéstralo
o acota.

## 6. Salida
Actualiza los seis entregables, `s52/test_s52_shutmode_facts.py` (añade comprobaciones de lo nuevo VERIFICADO: bytes, destinos de salto,
lectores de +0x5c, llamadores de +0x28, resultados de emulación reproducibles) y `s52/CHECKPOINT.md`. Cierra REA con `--shutdown`.
