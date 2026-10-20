# Mensajes BIONZ X ↔ DFE ↔ sensor (Agente A)

- userland → LIRO: comando `0x40e3`, paquete 9 B `05 00 e3 40 rr rr rr rr mm` (mm=0/1). Receptor A7S `0x437a9cb0`,
  A6000 `0x438032d4`. VERIFICADO receptor; formato del paquete VERIFICADO en A6300/A6000, INFERENCIA en A7S.
- LIRO → sensor: SetMode/SetExposure IMX235 escriben campos sombra en RAM `0x4402xxxx` (lista de punteros
  `0x43fee3f8`/`0x43fee598`). El transporte de esos campos al sensor (DFE/serie) **no se trazó** en esta ronda.
- DFE: la A7S 3.20 no incluye `dfe.bin` separado (búsqueda por patrón de vectores en todo el árbol, sin resultado);
  la A6000 sí (`/usr/dfe/dfe.bin`). Detalle DFE: `work/codex/`.
