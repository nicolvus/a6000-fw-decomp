# S19-11 — Copia de ejecución

Artefactos autocontenidos de la investigación estática de los modos ObjEffect
2–5: informe, evidencia JSON y los dos registros de orquestación ya
actualizados. Resultado: `PARTIAL`; sólo el modo efectivo 3 intenta
`ObjMsg(0x3900,0x0002)`. No prueba compatibilidad Camera/PbCap/EncodeStill ni
supresión de obturación mecánica.

Método: `llvm-objdump -d --triple=thumbv7-linux-gnueabi` sobre el `libObj.so`
de A6000 FW 3.21, SHA-256
`8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.
