#!/usr/bin/env bash
# Relanza un agente opencode cuando termina o se detiene. Uso: run-forever.sh <A|B|C> [provider/model]
# Parar: crear docs/agents/STOP (o Ctrl+C).
set -u
id=${1:?uso: run-forever.sh <A|B|C> [modelo]}
cd "$(dirname "$0")/../.."
extra=""; [ "$id" = B ] && extra=" y docs/agentes-opencode-deepseek.md"
msg="Eres el agente $id. Lee docs/agentes-opencode.md$extra y tu cola docs/agents/queue-$id.md. No hagas preguntas: decide tú y anota dudas en knowledge/agents/NEEDS-HUMAN.md. No termines el turno hasta vaciar la cola; luego regénerala y sigue. Continúa donde lo dejaste."
while [ ! -e docs/agents/STOP ]; do
  git pull -q --rebase --autostash origin main || true
  opencode run --auto -s "a6000-$id" ${2:+-m "$2"} "$msg"
  sleep 20
done
