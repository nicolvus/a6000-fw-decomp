#!/usr/bin/env fish
# S51 fase 1 — prueba real de DeepSeek Flash usando REA + knowledge MCP, en modo no interactivo (-p).
# Orquestado por Claude (este proceso), no por el usuario a mano: así se puede leer el resultado como texto.
# Aislado: --bare evita leer la sesión claude.ai normal; solo usa ANTHROPIC_API_KEY de este proceso.

set PROJECT /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
set MCPCFG /home/nicolas/Documents/a6000/.mcp.json
set OUTDIR $PROJECT/analysis/s51/deepseek
set LOGFILE $OUTDIR/balance_log.txt
mkdir -p $OUTDIR

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

set PROMPT "Estás investigando el firmware de la Sony A6000 (obturador electrónico). Tarea de validación, fase 1 de S51: 1) Abre libmprctrl.so con las herramientas REA disponibles. 2) Localiza la función DmmCloseAndFree y analízala (decompilación, instrucciones, xrefs/llamadas). 3) Consulta el MCP de conocimiento (sony-a6000-knowledge) por evidencia histórica relacionada con DmmCloseAndFree, en particular el informe S37. 4) Compara tu análisis con lo que diga S37: coincide, difiere o no hay evidencia suficiente. No inventes información; si una consulta no da resultados, dilo explícitamente. Responde de forma breve y estructurada: Paso 1 (REA usado: sí/no + qué tool), Paso 2 (hallazgos de DmmCloseAndFree), Paso 3 (qué dijo el MCP de conocimiento), Paso 4 (comparación con S37)."

echo ""
echo "Lanzando Claude Code (--print, no interactivo) contra DeepSeek-V4.1-Flash-1017..."
echo ""

env ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic ANTHROPIC_API_KEY=$DEEPSEEK_API_KEY \
    claude -p "$PROMPT" \
    --bare \
    --model deepseek-flash \
    --add-dir $PROJECT \
    --mcp-config $MCPCFG \
    --strict-mcp-config \
    --permission-mode bypassPermissions \
    --allowedTools "mcp__rea mcp__sony-a6000-knowledge Read Glob Grep" \
    --disallowedTools "Bash Write Edit NotebookEdit" \
    --output-format json \
    | tee $OUTDIR/phase1_result.json

echo ""
echo "--- Saldo final ---"
set balance_after (get_balance)
echo $balance_after
echo (date -Iseconds)" FIN    "$balance_after >> $LOGFILE

echo ""
echo "Resultado guardado en $OUTDIR/phase1_result.json"
set -e DEEPSEEK_API_KEY
