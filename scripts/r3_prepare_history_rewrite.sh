#!/usr/bin/env bash
# R3: prepara, en un clon aparte, el historial sin analysis/ghidra/s37-input/libmprctrl.so. No toca origin ni el repositorio actual.
# Uso: scripts/r3_prepare_history_rewrite.sh DIRECTORIO_NUEVO   (requiere git-filter-repo)
set -euo pipefail
dest=${1:?directorio destino que no exista}
path=analysis/ghidra/s37-input/libmprctrl.so
git clone -q --no-local "$(git rev-parse --show-toplevel)" "$dest"
cd "$dest"
git filter-repo --path "$path" --invert-paths --force
test "$(git log --all --oneline -- "$path" | wc -l)" -eq 0
echo "Listo en $dest: $(git rev-list --count HEAD) commits, sin $path. Publicar con: git remote add origin <url> && git push --force origin main"
