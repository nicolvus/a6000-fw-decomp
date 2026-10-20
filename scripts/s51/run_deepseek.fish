#!/usr/bin/env fish
# S51 — sesión aislada de Claude Code contra DeepSeek Flash (api.deepseek.com/anthropic).
# No toca ~/.claude ni la sesión normal: solo exporta vars para este proceso hijo.
# shortcut: el gasto se mide por diferencia de saldo (antes/después), no por cálculo propio de tokens*tarifa — DeepSeek no expone costo por request en la API; si lo expone en el futuro, usar eso.

set LOGDIR /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/s51/deepseek
set LOGFILE $LOGDIR/balance_log.txt
mkdir -p $LOGDIR

function get_balance
    curl -s -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/user/balance
end

echo "Pega la API key de DeepSeek (no se mostrará en pantalla):"
read -s DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY

if test -z "$DEEPSEEK_API_KEY"
    echo "Key vacía, abortando."
    exit 1
end

echo "--- Saldo inicial ---"
set balance_before (get_balance)
echo $balance_before
echo (date -Iseconds)" INICIO "$balance_before >> $LOGFILE

echo ""
echo "Presupuesto máximo: USD 1.00 | Umbral preventivo: USD 0.85"
echo "Lanzando Claude Code contra DeepSeek-V4.1-Flash-1017 (proceso aislado)..."
echo ""

env \
    ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic \
    ANTHROPIC_API_KEY=$DEEPSEEK_API_KEY \
    ANTHROPIC_MODEL=deepseek-flash \
    ANTHROPIC_SMALL_FAST_MODEL=deepseek-flash \
    claude

echo ""
echo "--- Saldo final ---"
set balance_after (get_balance)
echo $balance_after
echo (date -Iseconds)" FIN    "$balance_after >> $LOGFILE

echo ""
echo "Compara balance_before/balance_after arriba (o en $LOGFILE) para el gasto real de esta sesión."
set -e DEEPSEEK_API_KEY
