# S56-E — SENS_B y MMIO candidatos (20-10-2026)

Método: literales MMIO (`analysis/s56/xr.py`) + contexto de cadenas. Resultado: **no hay consumidor de SENS_B localizado.**
- `av-cam.bin` (ambos) no contiene `SENS_B`, `CA_1ST`, `SHT_RST` (test).
- Clúster `0xf2a0xxxx–0xf2a3xxxx`: funciones `0x43932346…0x439327c6/0x4393298c` (conmutación por identificador de dominio con máscaras `0x20/0x1000` y llamada `0x43b4a6fa`): **control de dominios/relojes** (INFERENCIA por forma). `0xf2403000–0xf2406040`: `0x439910c2…0x439917xx`, `0x4398ec7e` junto a la cadena `TSK_ADC`: **ADC/otros** (INFERENCIA). Ninguno referenciado desde imager (`0x436d5800–0x436d9400`) ni captura (`0x438c…`).
- A7S: censo ya diferenciado en S55 (`0xf3e00000`…); sin relación demostrada.
- La cadena de registros del sensor no lee GPIO (`gpio_get/cfg` ausentes; solo `gpio_set(15,5)` en el ctor).
- Esquema: `CIS0_SHT_RST` (BIONZ) → `XPI` del sensor es una línea discreta; ligarla a P4C/SENS_B es hipótesis (H56-6/7 NO VERIFICADA).
**Próximo estático:** buscar tablas de arranque que escriban bloques de captura de flancos con REA `trace_native_values` sobre literales `0xf24xxxxx` restantes; **pasivo:** analizador lógico en GPIO_9/P4C + XPI.
