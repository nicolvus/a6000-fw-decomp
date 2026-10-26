# Runbook para un agente de IA: empezar desde cero

Plantilla ejecutable. Entrada: clon de `github.com/nicolvus/a6000-fw-decomp` + firmware 3.21.
Salida: entorno equivalente al del autor, listo para continuar la investigación.

## 1. Ejecutar

```sh
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter
cd sony-a6000-electronic-shutter
scripts/agent/bootstrap.sh --dry-run   # muestra los pasos sin tocar nada
scripts/agent/bootstrap.sh             # idempotente; puede relanzarse tras un fallo
```

Descarga ~800 MB (Ghidra 570 MB + JDK 207 MB + firmware) y la extracción tarda minutos.
Si el script falla, **no improvises parches al repo**: lee el mensaje `FALLO:`/`AVISO:`, mira
§ Límites, corrige el entorno y relanza.

## 2. Verificar (criterios de éxito)

| Comprobación | Esperado |
|---|---|
| SHA-256 del `.dmg` | `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e` |
| SHA-256 de `firmware/extracted/fw321/firmware.fdat` | `603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90` |
| ELF ARM en el atlas | 679 |
| `python scripts/agent/check_env.py --sha` | código 0 (2 = solo avisos) |
| `./scripts/rea doctor --client codex --provider ghidra --json` | `ghidra*` healthy |
| `python -m pytest tests -q` | sin fallos nuevos (anotar los previos) |

## 3. Orientarse (en este orden, sin releer todo el repo)

1. `knowledge/CURRENT.md` (estado operativo) → `docs/STATE.md` (restricciones y política de RE).
2. `docs/OPEN-QUESTIONS.md` y los «Próximo» al final de `knowledge/PROGRESS.md`: qué falta.
3. Buscar con las skills `knowledge-navigation` / MCP `sony-a6000-knowledge` antes de explorar a mano.
4. Antes de reutilizar un hallazgo: `contradiction-audit`. Tras editar `.md`: `knowledge-maintenance`.
5. Si hay otros agentes activos: leer el mapa de temas en vuelo de `knowledge/PROGRESS.md` y hacer
   `git pull --rebase` antes de cada ola, para no colisionar.

## 4. Trabajar con REA (caro: ~8 min en frío)

```sh
SOCK=analysis/rea-independent/run/rea.sock
ls $SOCK analysis/rea-independent/run/*.ready 2>/dev/null     # ¿ya hay demonio? reutilízalo
python3 analysis/rea-independent/bin/session_daemon.py $SOCK \
  "$(sed "s#/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter#$PWD#" analysis/rea-independent/exp2-open-args.json)" &
python3 analysis/rea-independent/bin/q.py $SOCK guion.json     # consultas por lotes
python3 analysis/rea-independent/bin/q.py $SOCK --shutdown     # al cerrar el hito
```

Una consulta vacía de REA **no prueba ausencia**: verifica lo decisivo contra bytes/instrucciones
(Ghidra histórico `silent-liro.gpr`, solo lectura, como respaldo).

## 5. Ciclo de cada fase

1. Elegir un hito abierto; escribir primero la regresión (test) que falla.
2. Informe en `analysis/sNN_*/` + test en `tests/`; marcar VERIFICADO / PARCIAL / NO_VERIFICADO.
3. `knowledge-maintenance`; actualizar `docs/PENDIENTES.md`, `docs/STATE.md` si cambió una conclusión y `knowledge/CURRENT.md` si cambió el contexto mínimo; el README no se toca por sesión.
4. `ruff`/`mypy` sin avisos nuevos; tests relevantes en verde.
5. Commit Conventional Commits; `git pull --rebase`; `git push` a `main` (orden permanente del autor para este repo).

## 6. Límites (qué NO hacer y qué puede fallar)

**Prohibido por el proyecto:** ejecutar firmware, flashear, tocar la cámara sin backup de NVRAM
(ver `docs/STATE.md`), modificar `firmware/` o proyectos Ghidra históricos, subir binarios Sony
(`firmware/`, `*.bin`, `*.elf`, `*.tar.gz` están en `.gitignore`), exponer secretos.

**Puede fallar:**
- URL de Sony caída o archivo cambiado → el hash del `.dmg` no coincide: parar y avisar al usuario.
- `fwtool` falla en la sección WBI anidada → procedimiento alterno en `docs/firmware-analysis.md`.
- REA en Windows no abre ELF/ARM (solo Linux; ver `docs/agent/README.md`).
- Sandbox: Java desde Node puede dar EPERM; no confundir con JDK ausente.
- RAM: Ghidra necesita ~3 GB; el demonio se autotermina por memoria (`REA_DAEMON_RSS_MAX_MB`).
- Pruebas con cámara real (telnet/adb) requieren hardware y autorización del usuario; sin él, solo análisis estático.
- No hay `requirements.txt` del proyecto: si un script pide un paquete, `.venv/bin/pip install` y anótalo aquí.

**Conclusión vigente (no re-litigar sin evidencia nueva):** obturador electrónico en A6000, categoría E
(evidencia insuficiente), no parchear (S51); ni viabilidad ni imposibilidad demostradas.
