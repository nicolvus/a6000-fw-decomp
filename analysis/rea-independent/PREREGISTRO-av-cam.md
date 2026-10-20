# Pre-registro del experimento 2 (REA sobre av-cam.bin) — 2026-10-19

Registrado ANTES de ejecutar. Un único intento controlado.

- Entrada: copia 0444 `input/av-cam.bin`, SHA-256 esperado
  b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9.
- Apertura: `open_binary format=raw-binary architecture=arm entry_point=0x43541000 provider_id=ghidra`
  (base lógica histórica; lenguaje REA para arm raw = ARM:LE:32:v7, que admite Thumb).
- Sin REA_GHIDRA_SEED_FILE (preserva independencia; no se inyectan entradas históricas).
- `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000` (15 min de arranque); `GHIDRA_MAXMEM=3G`
  (control de heap documentado de REA; el equipo tiene ~3 GB libres).
- Presupuesto total del experimento: 30 min de reloj. Vigilante: mata el árbol
  si pasa el tiempo, si RSS del árbol > 3.8 GB o MemAvailable < 400 MB.
- Muestreo de recursos cada 10 s en `logs/exp2-resources.csv`.
- Criterio de parada: fallo por tiempo/memoria/incompatibilidad => conservar
  diagnósticos y NO repetir el autoanálisis completo.
- Proyecto Ghidra persistente (`analysis/ghidra/silent-liro.*`) no se usa ni se abre.

## Enmienda 1 (13:55, tras el intento 1)
Intento 1 (guion `exp2a.json`): OK, análisis completo en 459 s (`logs/exp2-resources.csv`,
pico RSS 2,3 GB); la sesión se cerró al terminar el guion. `list_procedures` supera el
presupuesto de respuesta stdio (no es fallo de análisis). Para cumplir "sesión abierta
mientras se investiga" se hace UN segundo arranque en frío con demonio de sesión
(`bin/session_daemon.py`, socket Unix, tope de inactividad 60 min, mismo límite RSS).
Esa es la única repetición del autoanálisis completo; no habrá más.
