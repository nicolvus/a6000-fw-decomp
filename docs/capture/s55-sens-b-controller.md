# S55-C — `SENS_B` y controlador dedicado (20-10-2026)

Método: cadenas y censo de literales MMIO (`analysis/s55/events_mmio.py` → `events_mmio.json`) sobre `av-cam.bin` A6000/A7S; esquemas A6000/A7S.

## Lo establecido
- `SENS_B` (AA13) está en el bloque de mecánica de BIONZ junto a `SENS_A`, `IRIS0`, `ND_DIR_*`, `AS_PWM*`, `STRB_ON*` (esquema, línea 4101): es una función **dedicada**, no `GPIO_n`.
- `av-cam.bin` (ambos modelos) **no contiene** las cadenas `SENS_A/B`, `MSHUT`, `curtain` (búsqueda por patrón: 0 aciertos). Los nombres de control mecánico del esquema no aparecen como símbolos.
- Censo de literales MMIO (`0xf2xxxxxx/0xf3xxxxxx`), ambos modelos casi idéntico: dominan APL/DFE (`0xf3850000/0xf3950000/0xf3a50000`, `0xf3120000`=VD/imager, `0xf3c30000`=CAMERA_MAIN_SYNC),
  `0xf2800000`, `0xf3020000`, `0xf3420000`, `0xf2400000`; GPIO `0xf2910000` (18 literales). **Ningún bloque se asocia por código o cadena a obturador/cortina.**
- Diferencias de censo A7S↔A6000: A7S añade `0xf3e00000` (26), `0xf2d20000`, `0xf3e80000`; no hay bloque exclusivo de A6000. Su semántica es **NO VERIFICADO** (podrían ser el segundo sensor/módulos de A7S).

## Lo no establecido (frontera exacta)
- Qué registro/IRQ de BIONZ, si alguno, muestrea `SENS_B`; el bloque puede ser configurado por una escritura única (p. ej. dentro de tablas MMIO de arranque) y no llevar cadena alguna.
- Pista a seguir: el escritor de `0xf2a1…0xf2a3` y `0xf2400000` (39/66 literales) y sus lectores; no se atribuyeron a SENS_B por no tener evidencia.
- Medición no destructiva suficiente: analizador lógico en `GPIO_9`/P4C con foto mecánica vs EFCS (¿activa el flanco algún registro de BIONZ? implica además registrar `0xf2a1xxxx`).

**H55-3:** NO VERIFICADO (ni refutada). No se declara ausencia: una cobertura por cadenas/literales no demuestra inexistencia.
