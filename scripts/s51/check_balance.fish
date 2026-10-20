#!/usr/bin/env fish
# S51 — diagnóstico aislado: solo verifica la key y el saldo, sin lanzar Claude Code.
echo "Pega la API key de DeepSeek (no se mostrará en pantalla):"
read -s DEEPSEEK_API_KEY

echo "Longitud de la key pegada: "(string length "$DEEPSEEK_API_KEY")" caracteres"

curl -s -o /tmp/s51_balance_response.json -w "HTTP status: %{http_code}\n" \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    https://api.deepseek.com/user/balance

echo "--- Respuesta ---"
cat /tmp/s51_balance_response.json
echo ""
set -e DEEPSEEK_API_KEY
