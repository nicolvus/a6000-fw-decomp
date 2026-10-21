#!/bin/bash
# Publica el trabajo local en GitHub integrándolo con lo que haya subido otro agente.
#
# Procedimiento (mantiene SIEMPRE las dos partes: lo que ya está en origin/main y lo
# que subimos nosotros):
#   1. fetch + rebase de la rama local sobre origin/main;
#   2. en conflicto, los ficheros DERIVADOS (docs/CORRECTIONS.md, docs/OPEN-QUESTIONS.md)
#      se toman de origin/main y se regeneran después con knowledge-maintenance;
#   3. el resto de conflictos (README.md, knowledge/CURRENT.md, .gitignore, docs/...)
#      se resuelven a mano conservando las dos versiones;
#   4. knowledge-maintenance (reindexa + regenera derivados) y commit;
#   5. push; si el remoto avanza otra vez, se repite.
#
# Uso: scripts/publish.sh            (rebase + push)
#      scripts/publish.sh --no-push  (solo rebase + commit)
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PUSH=1
[ "${1:-}" = "--no-push" ] && PUSH=0

echo "== estado =="
git status -sb | head -3
git log --oneline -1

echo "== fetch =="
git fetch origin 2>&1 | tail -2

echo "== rebase sobre origin/main =="
# el demonio REA sigue escribiendo el log de sesion: se aparta (stash) para poder rebasar
STASHED=0
if ! git diff --quiet || ! git diff --cached --quiet; then
  git stash push -q -m "publish-autostash" && STASHED=1
  echo "-- cambios sin commit apartados en un stash --"
fi
if ! git rebase origin/main; then
  echo "-- conflictos: se resuelven los derivados con la version de origin/main --"
  for f in docs/CORRECTIONS.md docs/OPEN-QUESTIONS.md; do
    if git diff --name-only --diff-filter=U | grep -qx "$f"; then
      git checkout --ours "$f" && git add "$f" && echo "   (tomado de origin/main: $f)"
    fi
  done
  # el resto de conflictos se listan para resolverse a mano (union de ambas versiones)
  pending=$(git diff --name-only --diff-filter=U)
  if [ -n "$pending" ]; then
    echo "   CONFLICTOS PENDIENTES (resolver a mano, mantener ambos lados):"
    echo "$pending" | sed 's/^/     - /'
    echo "$pending" > /tmp/publish_conflicts.txt
    exit 2
  fi
  GIT_EDITOR=true git rebase --continue 2>&1 | tail -3
fi

echo "== knowledge-maintenance (derivan con ambas partes) =="
if [ -x .venv/bin/python ]; then
  .venv/bin/python scripts/knowledge/index_docs.py 2>&1 | tail -1
  .venv/bin/python scripts/knowledge/build_graph.py 2>&1 | tail -1
  .venv/bin/python scripts/knowledge/export_corrections.py 2>&1 | tail -2
  .venv/bin/python scripts/knowledge/index_docs.py 2>&1 | tail -1
  .venv/bin/python scripts/knowledge/build_graph.py 2>&1 | tail -1
  git add docs/CORRECTIONS.md docs/OPEN-QUESTIONS.md 2>/dev/null
  if ! git diff --cached --quiet; then
    git commit -q -m "chore(knowledge): regenera derivados tras integrar con origin/main" && echo "   commit de derivados hecho"
  fi
fi

if [ "$PUSH" = "1" ]; then
  echo "== push =="
  for i in 1 2 3; do
    if git push origin HEAD:main 2>&1 | tail -2; then
      break
    fi
    echo "-- el remoto ha avanzado: reintento (rebase) --"
    git fetch origin 2>&1 | tail -1
    STASHED=0
    if ! git diff --quiet || ! git diff --cached --quiet; then
      git stash push -q -m "publish-autostash" && STASHED=1
    fi
    git rebase origin/main 2>&1 | tail -2
    pending=$(git diff --name-only --diff-filter=U)
    if [ -n "$pending" ]; then
      echo "   CONFLICTOS PENDIENTES:"; echo "$pending" | sed 's/^/     - /'; exit 2
    fi
  done
fi

# restaurar lo apartado (el log de sesion puede haber cambiado: se prioriza el estado actual)
if [ "$STASHED" = "1" ]; then
  git stash pop -q 2>/dev/null || { echo "-- el stash no se reaplica limpio (log de sesion en movimiento); se conserva el estado actual --"; git stash drop -q; }
fi

echo "== final =="
git status -sb | head -2
git log --oneline -3
