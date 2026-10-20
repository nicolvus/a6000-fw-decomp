## Cambio de alcance (19-10-2026)
El requisito 2 original ("sin facturación adicional ni procedimientos de evasión") se
modifica: se autoriza el stacking de múltiples cuentas gratuitas (ej. varias keys de
Gemini de distintas cuentas personales) como estrategia habitual de respaldo en
OmniRoute para este proyecto, no solo como excepción puntual. Decisión explícita del
usuario, 19-10-2026, tras pedírselo como cambio de alcance en vez de excepción ad-hoc.
Sigue excluido: scopes OAuth amplios tipo `cloud-platform` sin revisar, y cuentas
corporativas/de terceros (ya vimos el ban de GitHub Copilot Enterprise).

# Prompt de prueba aislada OmniRoute (S46 ya verificado)

Ejecutar con:
```bash
OMNIROUTE_API_KEY=sk-... codex -p test-omniroute
```

Prompt a pegar en la sesión:

```
Usa el MCP `rea` sobre el proyecto Ghidra persistente de av-cam para decompilar
0x43acee66 y sus llamadores inmediatos (0x436c6f3c, 0x436c7950).
Confirma si escribe 0xf3120000 en 0x43e16d2c.
No modifiques el proyecto Ghidra ni crees anotaciones nuevas.
Consulta también el MCP `sony-a6000-knowledge` para contrastar con el hallazgo S46 ya indexado en CONTEXT.md.
```

## Criterios de aceptación
- Invoca realmente `rea` y `sony-a6000-knowledge` (revisar transcript, no solo la respuesta).
- El resultado coincide con S46 (CONTEXT.md:33): `0x436c6f3c → 0x436c7950 → 0x43acee66` escribe `0x43e16d2c = 0xf3120000`.
- Sin escrituras/anotaciones nuevas en el proyecto Ghidra (comparar timestamp/tamaño del proyecto antes/después).
- Registrar: proveedor+modelo real que respondió (dashboard OmniRoute / logs pino) y qué tool_calls emitió Codex.

## Prueba de fallback por cuota (separada, no mezclar con la de arriba)
Forzar agotamiento del proveedor primario (key de prueba con límite bajo, o simulación 429 si el dashboard la ofrece) a mitad de turno.
- Fallback real = ocurre dentro del mismo turno/petición, el proceso Codex sigue vivo.
- Si en vez de eso el proceso muere y hace falta `codex resume`, eso es reanudación de Codex, no fallback de OmniRoute — no cuenta como válido para este criterio.

## Pendiente antes de ejecutar
1. Instalar y arrancar OmniRoute (tú, no yo — regla del proyecto):
   ```bash
   npm install -g omniroute
   omniroute serve &
   ```
2. En `/dashboard/free-tiers`: elegir proveedor gratis con API key propia (no scraping/stealth) y modelo con tool-calling confirmado. Escribir ese modelo en `~/.codex/test-omniroute.config.toml` (campo `model`).
3. En el dashboard de routing: forzar combo de compresión a "none"/passthrough antes de correr el prompt.
