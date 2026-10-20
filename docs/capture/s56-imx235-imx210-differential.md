# S56-D — IMX235 (A7S) frente a IMX210 (A6000) (20-10-2026)

Hechos de bytes (SHA A7S `b857d338…5103`, A6000 `b60c845c…6bb9`):
- **Mismo hardware P2S**: tabla de canales A7S `0x43bbce80` ≡ A6000 (`0xf3c00300`, `0xfc088300`, `0xfc089300`) y misma programación de bloque (`0x436f2630` ≡ `0x436d5e58`). Diferencias están en el protocolo/registros, no en el transporte.
- **Formato de registro**: A7S `{u8 dispositivo, 0, u16 dir, u8 dato}` (5 B), lista principal `0x43fee3f8`: 95 registros, 94 con dispositivo 0x81 y 1 con 0x83, IDs hasta 0xFC; dos formateadores (`0x43ad94fe`, `0x43ad9666`) con argumento de cabecera. A6000: cabecera fija 0x81, 16/8 bit, mapa 0..0x155. ID 1 está duplicado en ambos (patrón de pulso).
- **ShutMode**: A7S admite 0,1,3,4 y rechaza 2 (`ShutMode:%d is not supported.`, destino tbb `0x436f42fc`); A6000 admite 0–4. Codificación de bits distinta (A7S: bits 2/6/4 de un registro + bit3 de otro; A6000: bits 2/7/4/6 de ID1). Sin mapeo 1:1.
- **Pulso**: A7S `[O+0x3d7]` → bit `0x10` del byte +4 de un registro (`0x436f459c`); A6000 `[O+0x268]` → bit3 de ID1.
- **Silent A7S** = modos de arrastre `0x4e/0x4f` (columnas propias, S52/S53) + política de clase; en nivel sensor no aparece un comando nuevo de «terminar integración»: la diferencia está en los **valores** de las columnas de modo (IMX235-específicos) y en Darwin/LIRO. No se copian valores a IMX210.
**H56-5 NO VERIFICADA:** no hay operación Silent específica identificada con equivalente IMX210 demostrable. Para sustituir una función se exigiría semántica, parámetros, efecto y restricciones: ninguna cumplida.
