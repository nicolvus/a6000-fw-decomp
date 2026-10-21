S82 AutoFraming & control stages (A6000 fw3.21 / A7S fw3.20)

VERIFICADO (bytes 0x43xxxxxx):
- 3 etapas AutoFraming idénticas en A6000/A7S: Stage_AutoFraming (0x43cc71a3 / 0x43cc26ac), Stage_AutoFraming_ResizeRotate (0x43cc71b9 / 0x43cc26c2), Stage_AutoFraming_Branch (0x43cc71d8 / 0x43cc26e1).
- Log framing force: [IMAGING_CAP]: Debug) ResizeRotate Framing size force set: offset[%d,%d] size[%d,%d] rotate[%d] en 0x43cc7143 (A6000) / 0x43cc265b (A7S).
- Validación geométrica 8 direcciones: us_Size_X/Y, canvas_size comparison, alineación a múltiplos de 8/16 pix (0x43cc6e5f a 0x43cc70f2).
- 8 etapas de control conservadas: CaComm (0x43cc7b9c/0x43cc2d53), CameraHAPI (0x43cc7bad/0x43cc2d83), Notify (0x43caccd6/0x43cb07bb), WaitControl (0x43cad784/0x43cb0f69), SACC (0x43c9ee6c/0x43ca484d), Common (0x43cac363/0x43cb0098), DevLater (0x43cac51b/0x43cb01ef), DualRec (0x43cac9f8/0x43cb0591).
- Relación SA por rodata adjacency: CaComm→CONTP, DualRec→DUALREC_BAYER/CLEARVID, SACC→NFLASH. AutoFraming usa parámetros ImageAreaResize, no función SA nombrada.

NO_VERIFICADO (pendiente):
- Origen de datos de encuadre (sensor/AF) y significado de rotación.
- Mapeo parámetros encuadre <-> apc_* motor YC.
- Intercambio CaComm/CameraHAPI ↔ app.
- Desfase posiciones Notify/WaitControl entre modelos.
- Definición exacta SACC.