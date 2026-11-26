#!/usr/bin/env bash
# Trae la copia de lectura de las reglas de nicolvus/a6000-handoff-context (privado) y lista
# qué difiere de las copias locales. ORDEN.md §12: si difieren, manda este repositorio.
# Salida: 0 si todo coincide, 1 si hay diferencias, 2 si no hay acceso.
# Uso: scripts/agent/sync_rules.sh
set -euo pipefail
REPO=nicolvus/a6000-handoff-context
ROOT=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
DEST=$ROOT/.handoff-rules
FILTER='^(estado/|home/\.(vibe|claude)/|workspace/Documents/a6000/).*\.md$'
NOTA_COPIA='^> (Copia de lectura|Read-only copy)'

command -v gh >/dev/null || { echo "falta gh (github-cli)"; exit 2; }
gh auth switch -u nicolvus >/dev/null 2>&1 || true
BRANCH=$(gh api "repos/$REPO" --jq .default_branch) ||
  { echo "no puedo leer $REPO: ¿gh auth switch -u nicolvus?"; exit 2; }

rm -rf "$DEST"
mkdir -p "$DEST"
gh api "repos/$REPO/git/trees/$BRANCH?recursive=1" --jq '.tree[] | select(.type=="blob") | .path' > "$DEST/.all" ||
  { echo "no puedo listar $REPO (rama $BRANCH)"; exit 2; }
grep -E "$FILTER" "$DEST/.all" > "$DEST/.paths" ||
  { echo "sin reglas .md en $REPO"; exit 2; }
while read -r p; do
  mkdir -p "$DEST/$(dirname "$p")"
  gh api "repos/$REPO/contents/$p?ref=$BRANCH" -H "Accept: application/vnd.github.raw" > "$DEST/$p"
done < "$DEST/.paths"

DIF=0
while read -r p; do
  copy=
  case $p in
    estado/ORDEN.md) copy=$ROOT/ORDEN.md ;;
    estado/ORDER.md) copy=$ROOT/ORDER.md ;;
    estado/*) continue ;;  # estado/CONTEXTO.md y auditorías son del handoff, no copias de este repo
    home/*) copy=$HOME/${p#home/} ;;
    workspace/Documents/a6000/*) copy=$ROOT/../${p#workspace/Documents/a6000/} ;;
  esac
  copy=$(realpath -m -- "$copy")
  # La copia del handoff lleva una nota de cabecera que aquí no existe; -B ignora el hueco que deja.
  grep -v -E "$NOTA_COPIA" "$DEST/$p" > "$DEST/.cmp" || true
  if [ ! -f "$copy" ]; then
    echo "SOLO-EN-HANDOFF  $p"; DIF=1
  elif ! diff -q -B "$DEST/.cmp" "$copy" >/dev/null; then
    echo "CAMBIADO         $p  ->  $copy"; DIF=1
  fi
done < "$DEST/.paths"
rm -f "$DEST/.cmp"

echo "reglas en $DEST ($(wc -l < "$DEST/.paths") ficheros, rama $BRANCH)"
[ "$DIF" -eq 0 ] && echo "AL DÍA: las copias coinciden con este repo" ||
  echo "DIFIEREN: manda este repo (ORDEN.md §12); actualiza la copia del handoff en el mismo cambio"
exit "$DIF"
