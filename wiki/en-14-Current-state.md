# 14. Current state and limits

State as of **2026-11-25**. Linked reports are in Spanish; the operational source for agents is
[knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md).

| Aspect | State |
|---|---|
| Camera | CFW of the **3.93/4.0x** series on the Silent base; the stock 3.21 roll-back package is verified. Recovered on 2026-11-03 over SWD ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)); the probe is still soldered |
| Electronic shutter | **Works since 3.30** (inline `pkt[0x0e]` + Darwin gate, [R54](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r54-paquete-330-envio-pkt0e.md)); exposure was calibrated in 3.35 ([R56](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r56-paquete-333-envio-inline.md) §7) and Silent has been levelled **in the firmware** since 3.77 ([R87](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r87-disparo-remoto-y-recalibracion.md)). First milestone: 3.23 (T040, mechanical shutter merely idle) |
| EFCS on | **Black from 1/1000**: ≈1.27 ms are lost, also with Sony's firmware ([R57](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r57-paquete-336-darwin-eq1.md) §5). Firmware, NVRAM and Darwin are ruled out as causes: it is physical ([R74](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r74-conclusion-final-efcs-negro.md), [R83](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r83-informe-final-efcs-negro.md)). Open; a physical measurement is missing (E26-R74-FISICO) |
| GUI | **QEMU harness**: boots `im.elf` 3.21 with the A6000's keypad, draws the menu and runs keys without touching the camera; CFWs with new features are built on top of it ([GUI lane](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/README.md), [G22](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g22-arnes-ui-qemu.md)) |
| 3.93 series | **One build per feature** on the Silent base: `base`, `film`, `pp`, `exfine`, `iso`. Installed and tested one by one ([G105](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g105-builds-por-funcion.md)). `iso` leaves the camera in a boot loop; Film sticks the buttons (cause not isolated); Extra Fine claims there is no room on the card |
| 4.0x series | 4.01 and 4.02 installed to bisect the video bug; 4.03 (4.02 core + Sony's `/usr`) and 4.04 (stock 3.21 minus `nflasha5`) built and audited, **not installed** |
| Video (FILM-PB-1) | **Open**: clips record and play on a PC, the camera shows “Cannot display.”. Patched code was ruled out ([audit](https://github.com/nicolvus/a6000-fw-decomp/blob/main/reports/film-pb-1-auditoria-cfw-20261127.md)); the likely cause is the **PAL/NTSC selector** against the clip frame rate ([report](https://github.com/nicolvus/a6000-fw-decomp/blob/main/reports/film-pb-1-causa-sistema-tv-20261127.md)), a setting **not exposed in this model's menu** |
| 3.25 incident | Cause identified offline (TPZL format of `nflasha3`, [R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)), fixed in 3.25c, **installed as 3.27** ([R51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md) §5) and replaced by 3.30 |
| Recovery | **Solved over SWD** ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)): one CPU register is forced and the factory updater installs over USB, with no NAND write. Procedure and limits in [15](en-15-SWD-recovery-experimental) |
| USB charging while on | Under investigation: the command reaches Darwin but a wall charger does not apply it ([report](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/usb-carga-encendida.md)) |
| Video open gate | Recording at 6000×4000 is **ruled out** (the sensor delivers 14.98 Hz); the only firmware path would be 1440×960 ([G112](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g112-opengate-video-3-2.md)) |

## Limits and risks

- **No independent recovery** ([E24-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e24-04-dictamen-seguridad.md), [E25-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-04-recuperabilidad-y-decision.md)): Darwin also controls power. What is proven is BIONZ recovery over SWD, not recovery of the Darwin firmware.
- **Being verified offline does not guarantee booting:** 3.25 passed every check and bricked the camera ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)).
- **With EFCS on, black from 1/1000**; the electronic shutter is measured on one camera and one sensor unit.
- **CFWs of the 3.93/4.0x series do not play video** (FILM-PB-1) and `iso` does not boot.
- **Backup:** the external copy of the backup (R1) is still unverified.
- Dashboard figures (modules, sessions, tests) measure documentation and verifiers, not camera behaviour.

See also [Results and limits](en-9-Results-and-limits), [Requirements and risks](en-1-Requirements-and-risks),
[Goals](en-16-Goals) and the [progress board](https://nicolvus.github.io/a6000-fw-decomp/progress/).
