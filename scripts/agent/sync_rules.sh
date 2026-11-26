#!/usr/bin/env bash
# Trae las reglas vigentes de nicolvus/a6000-handoff-context (privado) y las compara
# con las copias locales. Salida: si difiere algo, 1; si todo está al día, 0.
# Uso: scripts/agent/sync_rules.sh
set -euo pipefail
REPO=nicolvus/a6000-handoff-context
ROOT=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
DEST=$ROOT/.handoff-rules
FILTER='^(home/\.(vibe|claude)/|workspace/Documents/a6000/).*\.md$|^estado/(ORDEN|ORDER)\.md$'

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

# Las copias de las reglas (estado/ORDEN.md, estado/ORDER.md) llevan una linea de nota
# de espejo; se ignora al compararlas con la fuente canonica del repositorio del proyecto.
igual() {
  case $1 in
    *ORDEN.md|*ORDER.md) diff -q -B <(grep -v '^> ' "$1") <(grep -v '^> ' "$2") >/dev/null ;;
    *) cmp -s "$1" "$2" ;;
  esac
}

DIF=0
while read -r p; do
  case $p in
    home/*) copy=$HOME/${p#home/} ;;
    workspace/Documents/a6000/*) copy=$ROOT/../${p#workspace/Documents/a6000/} ;;
    estado/ORDEN.md|estado/ORDER.md) copy=$ROOT/${p#estado/} ;;
  esac
  copy=$(realpath -m -- "$copy")
  if [ ! -f "$copy" ]; then
    echo "SOLO-EN-GITHUB  $p"; DIF=1
  elif ! igual "$DEST/$p" "$copy"; then
    echo "CAMBIADO        $p  ->  $copy"; DIF=1
  fi
done < "$DEST/.paths"

echo "reglas en $DEST ($(wc -l < "$DEST/.paths") ficheros, rama $BRANCH)"
[ "$DIF" -eq 0 ] && echo "AL DÍA: las copias locales coinciden con el repo" ||
  echo "DIFIEREN: aplica de GitHub lo que falte; un snapshot más antiguo no borra la regla local"
exit "$DIF"
