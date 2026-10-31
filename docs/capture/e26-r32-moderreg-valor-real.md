# E26-R32 — Valor real de `MODEREG` en la cámara: bit 0 (`BOOT_MAIN`/`CL1000`) = 1 en arranque normal (31-10-2026)

Responde «¿en qué estado está siempre `CL1000`?» con datos ya existentes, sin tocar la cámara. **Corrige R20 §1.6 y R23 §1** («bit 0 = 0 en uso normal», «almacenamiento sano → Loader2»). Test: `tests/test_e26_r32_moderreg_backup.py`.

Etiquetas: **BINARIO** · **DATO DE CÁMARA** (volcados ya tomados) · **INFERENCIA**.

## 1. Loader3 guarda `MODEREG` en el backup en cada arranque (BINARIO)

- `0xc01f4ef8` (`LD3:read MISCREG`, archivo `0x276f8`) lee TYPEID (`[0xf2915000]`), `[0xf2912b10]` y `MODEREG` (`[0xf2915010]`) y escribe cada valor con `0xc01f4aa0` (escritura de backup, error `LBK_E:Can't Write`) en los IDs `0x3e0003`, `0x3e0009` y `0x3e000a`.
- Se llama sin condición al final de la inicialización de Loader3 (`bl` en `0xc01f11e4`), tras `Init Pwr2nd`.
- Las tres entradas del backup miden 2 bytes: se conserva la mitad baja de cada registro.

## 2. Valores en los volcados (DATO DE CÁMARA)

Leídos con `analysis/s55/bk4.py` en los 23 `backup*.bin` de `analysis/camera-dumps/` (20-10 a 26-10, incluidos los volcados posteriores al incidente y a la restauración). Son idénticos en todos:

| ID | Valor | Plantilla de fábrica (`0110_backup`) | Lectura |
|---|---|---|---|
| `0x3e0003` | `0x0500` | `0x00ff` | `TYPEID & 0xff00` = `TYPEID_CXD90014` (fuente Sony): confirma que el registro lo escribe Loader3 en esta cámara |
| `0x3e0009` | `0x0010` | `0x0000` | `[0xf2912b10] & 0xff` |
| `0x3e000a` | **`0x0003`** | `0x0000` | **`MODEREG[15:0]`: bit 0 = 1, bit 1 = 1** |

- **bit 1 = 1** (`BOOT_SERIAL_IN`) cuadra con una línea UART en reposo (nivel alto): sirve de control de cordura.
- **bit 0 = 1**: con `CL1000` sin conexión externa (R19/R20), el nivel lo da el pull interno del IC6000. Que el bit lea 1 en reposo apunta a pull-up (**INFERENCIA**, suponiendo que el bit refleja el pin sin invertir).

## 3. Consecuencia en el BootROM (BINARIO, `main` `0xffff1062`)

Con bit 0 = 1 el BootROM **no** usa la carga directa de Loader2 (`0x28c → 0x2c6 → 0x13c`), sino:

`0x10de` → `0x554` (perfil serie) → GPIO4.22 = 0 → `0x28c` → `0x332` (cabecera) → `0x39c` (busca clave en `0xc0001200`) → **clave presente** → `0x876` (ventana de recepción serie) → **`0x3001` (sin sincronismo)** → `0x1226`: `load_payload` (`0x3de`), `0x44e`, `0x486` y salto (`0x144`).

Es la fila de R20 «bit0=1, clave presente, sin datos serie → arranque alternativo de payload». **Ese es el arranque normal de esta cámara.**

## 4. Qué cambia

| Antes | Ahora |
|---|---|
| R20 §1.6: bit 0 = 0 en uso normal | **bit 0 = 1 en uso normal** (dato de la cámara) |
| R23 §1: «almacenamiento sano → Loader2» | con bit 0 = 1, almacenamiento sano y clave → ventana serie y carga de payload |
| `E26-R20-BOOTMAIN-NIVEL`: nivel no determinable | **nivel lógico en reposo = 1**; la tensión exacta no hace falta |
| Plan SERIE: «llevar `CL1000` a 1» | **innecesario: ya está a 1**. El BootROM abre la ventana serie en cada arranque |
| `E26-R20-KEYTABLE`: vacía o con clave, indeterminado | **INFERENCIA fuerte: con clave**. Sin clave (`0x39c` = 1) iría a `serial_entry` y no arrancaría sola (emulación R20) |

**Efecto práctico:** para entrar por serie basta con enviar el tren de sincronismo y el paquete por `BOOT_SERIAL_IN` (Multi pin 9) durante la ventana. Pero si el paquete llega correcto, el BootROM compara la clave recibida con la guardada (`0x11ea`): si coincide → `serial_entry`; si no → LED `0x2002`. La clave sigue en `nflasha0`, que no se ha volcado. Llevar `CL1000` a **masa** pasaría a la carga directa de Loader2, sin ventana serie ni clave (**INFERENCIA**: supone que el bit no está invertido respecto al pin; no se ha probado).

## 5. Límites

- El valor lo lee Loader3, no el BootROM. Si el bit fuera un strap muestreado solo en el reset y cambiara después, no coincidiría. Con `CL1000` sin conexión no hay nada que lo mueva.
- Solo se guarda la mitad baja (16 bits) del registro.
- Ningún otro binario se identificó como escritor de `0x3e000a` (los literales `0x003e000a` encontrados en fuentes, librerías y `.uxc` son datos sin relación); la coincidencia de `0x3e0003` = `0x0500` con el TYPEID de Sony respalda la atribución a Loader3.
- Que la clave exista se deduce del flujo (§3) y de la emulación de R20; su valor sigue sin conocerse.
