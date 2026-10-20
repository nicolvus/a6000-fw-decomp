# S56-F — Sincronización (20-10-2026)

Verificado: el lote de registros usa `SyncMode 2` del P2S (flag de espera `0x18`, `SIFSyncCode` en el log) y lleva el SSB de ID1; la cadena **no** lee P4C/GPIO. Inferido: el modo 2 aplica el lote en el siguiente VD (VD ya conocido: `0xf3120220` desde `0x43ad2bd6`); la semántica de `bloque1+0` no está documentada.
Orden lógico (código): SetExposure → SetRead → SSB → Execute → `msg 0x107` a Darwin (tiempos) ; orden físico no inferible (sin duraciones). Darwin recibe CAIF ev1 y mueve cortinas (S53); BIONZ no muestra consumo de `CA_1ST_CURTAIN_START`.
Cronologías: A6000 mecánica/EFCS y A7S: como S52–S54; no se añade ninguna relación nueva P4C↔sensor. A6000 «tipo 0» (modelo estático) conserva la misma cadena de registros: ningún cambio de P2S depende del tipo (no hay lectura del tipo en 0x436d5800–0x436d9400, ver test de GPIO; lectura de tipo no auditada en este rango: límite).
**H56-7 INFERENCIA** (P4C no participa en el camino de registros; VD sí vía P2S). Frontera: traza pasiva de VD, XPI, CIS0 y P4C.
