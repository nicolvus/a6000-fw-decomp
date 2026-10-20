# S51 — plan prerregistrado (decisión SÍ/NO)

Fecha: 2026-10-19. Escrito ANTES de investigar. No se modifica después salvo sección «Desviaciones».

## Presupuesto

- Tiempo de trabajo: Claude ≤ 75 min, Codex ≤ 60 min (corte duro 70 min de reloj).
- REA: **un solo** arranque en frío, sesión compartida `analysis/s51/shared/run/rea.sock` (Claude y Codex como clientes
  de `q.py`). Watchdog: RSS ≤ 6000 MB, corte si MemAvailable < 1000 MB. Ghidra histórico solo lectura y solo si una
  función Thumb decisiva no la cubre REA ni LLVM.
- LLVM: `analysis/s51/shared/av.dis` (sección `.text`, direcciones absolutas) para barridos baratos.
- Prohibido: ejecutar/modificar/flashear firmware, tocar `silent-liro.gpr/.rep`, git push.

## Pruebas decisivas (cada una cierra con SÍ/NO, o con el dato exacto que falta)

### T1 (Claude) — ¿El modo `0..7` / B / G llega al sensor?
Pregunta: ¿existe una cadena de datos, con instrucciones, desde `[0x43eefb1c+0x60]` (o `B+0x36/37`, G) hasta un
argumento de `ModeRsvParam`, `C_Imager::SetMode`, `SetExposure` o `SetRead`?
- SÍ si hay al menos un lector cuyo valor (o derivado) alcanza un argumento de esas llamadas.
- NO si todos los lectores enumerados (literal `0x43eefb1c` + desplazamiento `0x60`, y copias de B/G) terminan en
  exportadores de estado o en ramas sin llamada al imager.
- Efecto: NO ⇒ la configuración `CURTAINMODE`/`C+0x94` no gobierna el sensor ⇒ se descarta como base de parche.

### T2 (Codex) — ¿Qué es eléctricamente ID1/ID100/ID101?
Pregunta: ¿a qué dirección de registro del IMX210 (o campo de trama serie) se traduce cada ID, y qué selector/caso de
`SetExposure` (0–4) los escribe en captura fija?
- Resultado aceptable: la dirección física/campo de cada ID + la fuente del selector. El **significado** eléctrico solo
  se da como VERIFICADO si hay documento legítimo; en otro caso se declara el dato exacto que falta.
- Efecto: sin significado, no hay fin electrónico demostrado (A=NO por falta de demostración, no por imposibilidad).

### T3 (Codex) — ¿La 2ª cortina es incondicional en foto fija?
Pregunta: ¿la emisión del cierre de 2ª cortina (Darwin P4E `2ND_CURTAIN_MG` / evento LIRO) en la secuencia de foto
fija tiene alguna condición dependiente de un flag configurable (modo `0..7`, `C+0x94`, EFCS, `+74f`)?
- SÍ-condicionada ⇒ existe una rama de serie sin cierre mecánico (candidata a ruta).
- NO (incondicional en toda foto fija) ⇒ el firmware de serie siempre cierra mecánicamente ⇒ A=NO firme para el
  firmware actual; un parche tendría que suprimirla y depender de un fin electrónico no demostrado.

### Criterio de C (imposibilidad física)
C=SÍ solo con evidencia concreta: p. ej. el sensor no admite reset/lectura por filas a resolución completa sin
obturador, o el hardware fuerza la cortina. No se buscará activamente salvo que aparezca en T1–T3.

## Regla de parada
Cada prueba termina al cumplir su criterio o agotar presupuesto. No se amplían referencias. Si queda una prueba
decisiva accesible dentro del presupuesto, no se cierra.

## Desviaciones
(ninguna aún)
