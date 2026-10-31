# S59 — Investigación colaborativa Claude + GPT-6.1 Sol

20-10-2026. Baseline S58 `abb78218`. SHA A6000 `b60c845c…6bb9`, A7S `b857d338…5103`. **Resultado: avance parcial en ambas líneas; fin electrónico del IMX210 sigue NO VERIFICADO. S51: A=NO, B=NO, C=NO.**

## Descubrimientos de GPT (IMX210, A6000) — [informe](s59-sol.md)

- **Escritor del bloque `0x437876dc()+0xDD0` recuperado** (VERIFICADO): `0x43b00da0` copia 80 B a `obj+0xdb4` (cubre `+0xdd0..0xde7`), publicado por `0x43b00dd4` si `obj+0x57c≠0`; fuente `obj+0xd64`, alimentada (PARCIAL) por `0x438069f0` casos 4/10 con `obj+0x568=2`. El constructor lo deja a cero: **los valores de M no son constantes de construcción**; vienen de un payload externo cuyo emisor no se localizó.
- Corrección a S58: `clk` **no** se puede atribuir al objeto de histogramas (objetos distintos `0x43eb121c` vs `0x43eaee84`).
- VdNum local = `max(0, raw−0x3000)`; productor y host coinciden (modo=0,f=0) solo con VdNum=1 o svr=1; el host normaliza N=0, estado 9, bit15.
- M/Tv/clk/N/svr/VdNum alcanzables para `0x0B/0x2F`: **NO VERIFICADO**.

## Descubrimientos de Claude (IMX235, A7S) — [informe](s59-claude.md)

- **Constructor real de C_Imager `0x436f3fc0`** emulado; los 12 escenarios reproducen las mismas 100 escrituras: S58 no se invalida en contenido de registros.
- **Corrección de S58-C:** base P2S real `0xfc088300`, 3 tramas (no 5); lo anterior eran artefactos sintéticos.
- **Mensajes `0x1000/0x1001`:** lista blanca de modos `{0x0b,0x35,0x37,0x38}` (no estado sin inicializar); naturaleza probable de eventos/diagnóstico (INFERENCIA); receptor sin localizar.
- Execute no tiene ramas de registros exclusivas de Silent (con depuración `0xff`); las diferencias son mensajes y lectores de sustituciones de depuración por grupo de modo (CORREGIDO por GPT).
- Consumidor de ganancia: único llamador `0x436f5b40` (Execute).

## Viabilidad de Silent Shooting

Sin cambio: la A7S distingue Silent por modo (`0x4e/0x4f`, otra columna de la matriz) y por Darwin/CAIF (S53), y su cadena de C_Imager no añade orden de «fin»; en el IMX210 el bloque de temporización se alimenta desde un payload cuyo origen sigue abierto, y no hay evidencia de un mecanismo de fin electrónico. Ausencia de comando de fin ≠ autonomía. Física del sensor (reset/lectura/obturación electrónica): requiere datasheet o traza pasiva CIS0+XPI+VD (no autorizada). **No parchear.**

## Hipótesis descartadas / límites

Descartadas: clk por alias de histogramas; mensajes por estado sin inicializar; «solo difieren los emisores». Límites: depuración en `0xff` es supuesto del arnés; servicios Darwin/OSAL stub (nulo en `[[GOT+0x1b3c]+0x14]+0x98..0xa0`); entradas fijas; sin medición eléctrica. Matriz: [`analysis/s59-evidence-matrix.json`](../../analysis/s59-evidence-matrix.json) (17 evidencias, 7 hipótesis). Validación: [cruzada](s59-cross-validation.md).

## Reproducción

```sh
python3 -m unittest tests/test_s59_claude.py tests/test_s59_sol.py -q   # 9 + 11
python3 -m unittest discover -s tests -p 'test_s5[678]*.py' -q          # 83 regresiones
python3 analysis/s59/build_matrix.py
```

## Próxima investigación de mayor valor

Localizar el **emisor del payload** de `0x438069f0` (casos 4/10, `obj+0x568=2`) —de dónde nacen M/Tv/clk reales— y los **receptores de `0x1000/0x1001`** sembrando Thumb a mano; para física, traza pasiva autorizada.
