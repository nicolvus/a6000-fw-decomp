#!/usr/bin/env fish
# S51 — prueba mínima de un request real a DeepSeek Flash (endpoint OpenAI-compatible), sin Claude Code.
echo "Pega la API key de DeepSeek (no se mostrará en pantalla):"
read -s DEEPSEEK_API_KEY

curl -s https://api.deepseek.com/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    -d '{
          "model": "deepseek-flash",
          "messages": [{"role": "user", "content": "Responde solo con la palabra: OK"}],
          "max_tokens": 10
        }' | tee /tmp/s51_test_response.json

echo ""
echo "--- usage ---"
python3 -c "import json; d=json.load(open('/tmp/s51_test_response.json')); print(d.get('usage'), d.get('model'))" 2>/dev/null
set -e DEEPSEEK_API_KEY
