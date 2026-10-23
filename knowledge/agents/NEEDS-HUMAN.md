
## 2026-10-22 — autostash conflictivo en `docs/CORRECTIONS.md` / `docs/OPEN-QUESTIONS.md` (carril B)

Durante el `git pull --rebase` de S343 (checkout compartido con otros agentes) el autostash
entró en conflicto en esos dos ficheros (48 marcadores cada uno). Como el carril B tiene
prohibido editarlos, se conservó la versión de `HEAD` (ya publicada por el carril E, S618) y
se descartó la copia del autostash. Si otro agente tenía ediciones locales sin publicar en
esos dos ficheros, hay que regenerarlas. El resto del autostash (4 `docs/capture/*.md`) sí se
re aplicó y sigue como cambio local sin commitear.
