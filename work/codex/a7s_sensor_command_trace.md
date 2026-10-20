# Traza estática de comandos de sensor A7S

`av-cam.bin` A7S (`b857d338…103e`, base `0x43541000`) conserva las interfaces `C_Imager::SetMode` (file+7712155), `SetExposure` (+7712254), `SetRead` (+7712872) y el tipo `C_ImagerCtrl_IMX235` (+7716309): **VERIFICADO** por cadenas embebidas.

La traza demostrable es solo de interfaz:

`cliente de cámara → C_Imager::{SetMode, SetExposure, SetRead} → C_ImagerCtrl_IMX235 → configuración receptor DFE/PHY`

El último salto, la tabla concreta IMX235 y el transporte serie sensor no se recuperaron: **NO VERIFICADO**. `SetExposure:SHR = %d` muestra que la llamada alcanza un parámetro SHR; no autoriza asignarle dirección de registro, reset global ni shutter electrónico. Los nombres `GCS2RxLink`, `MPHYRx4ch` y `SubLVDS` pertenecen a la ruta de recepción de datos, no prueban ser el bus de control.

Reproducir con el comando `strings` de `a7s_dfe_architecture.md`; para xrefs hace falta completar REA con timeout de arranque >=900000 ms en una sesión temporal.
