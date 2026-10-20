# S51 Codex — checkpoint T2/T3

## T2 — IDs de `SetExposure`

- **PARCIAL:** `0x436d6f6c` lee el selector desde `param+0x09`
  (`0x436d6fb6`) y el caso `2` (`0x436d7114..714a`) modifica el
  registro lógico ID1 y copia los bytes `param+0x08` y `param+0x14` a
  dos destinos lógicos. La tabla de `0x43fe995c` es un vector de 119
  punteros a registros `{u16 id, u8 dato}`; no es un mapa de direcciones
  de registro IMX210. No se recuperó una traducción de ID1/100/101 a una
  dirección de sensor o campo SIO.
- **NO_VERIFICADO:** significado eléctrico. No hay datasheet público
  legítimo del IMX210 con ese mapa; se requiere el mapa de registros o
  una traza pasiva que relacione esos IDs con el bus del sensor.

## T3 — cierre de segunda cortina

- **VERIFICADO:** evento interno tag `0x12` llega a `0x436b93b0` desde
  `0x436bc140`; su rama llama `0x43b5e2b0` (`0x436b9416..941a`). Esta
  exige solo banco `<=17` y escribe `1<<bit` en
  `0xf2910048 + banco*0x100` (`0x4398f9bc..f9c8`).
- **VERIFICADO:** la ruta de evento 3 está guardada por
  `captura+0x74f != 0` (`0x438d033c..0348`; reintento) y, para la
  petición inicial, además por `43ae7648(captura)==1`
  (`0x438d0420..042a`, `0466..047a`).
- **NO:** ninguna de estas guardas lee modo `0..7`, `C+0x94`, EFCS ni
  convierte el bypass diagnóstico `+0x74f` en un ajuste de captura. El
  bypass `D+0x7e/7f` borra `+0x74f` y marca estado no normal.

REA compartida no creó `rea.sock.ready` durante T2/T3; no se arrancó ni
cerró una sesión adicional. Evidencia primaria: `analysis/s51/shared/av.dis`.
