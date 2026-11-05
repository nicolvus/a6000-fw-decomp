# Lectura SWD del BIONZ con la cámara encendida (05-11-2026, solo lectura)

Sonda `debugprobe-zero` (serie `…3936`) al SWD del BIONZ (DPIDR `0x3ba02477`), AP0, 1 MHz, sin `halt`. RAM física = dirección virtual + `0x40000000` (validado: `0x83deb360` = bloque NVRAM `0xbc0005`, 0 bytes distintos).

* `bionz_idle.txt`: reposo. `bionz_shot1.txt`: tras disparo EFCS ≈1/500. `bionz_shot2.txt`: tras disparo EFCS ≈1/125. `desc.txt`: descriptores de modo `0x83ea04bc` y `0x83ea13dc`.
* Paquete `0x0c` (`0x83ed4948`): 1/500 → `pkt[2..3]=0x1900` (1/512 s), duración 1953 µs; 1/125 → `0x1700` (1/128 s), 7812 µs. `pkt[1]=02`, `pkt[0xc]=00`, `pkt[0xd]=40` y el resto del paquete **idénticos** en ambos.
* Los dos descriptores de modo son idénticos en sus primeros 160 B.
