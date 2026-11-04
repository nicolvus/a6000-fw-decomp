# 15. SWD recovery (EXPERIMENTAL): how I recovered a bricked Sony A6000 with an RP2040

Linked reports are in Spanish.

<img width="720" height="1280" alt="Overview of the setup" src="https://github.com/user-attachments/assets/52e7fec3-ee1a-40ab-97e3-f0b8ef6e70d0" />

**Summary:** My A6000 was bricked (error LED, no USB connection) after I installed a modified firmware of my own. I recovered it by connecting an RP2040 to two pads on the board over SWD and forcing a single register during startup, which made the camera load Sony's factory updater. I then installed the official firmware over USB.

**Before you start:** This page is highly technical and specific. If you don't understand everything, don't worry; there are plenty of things I don't fully understand either. I hope it helps explain how this Sony camera's update system works. This is not a guide to follow blindly: soldering to the board can damage it, and this worked on only one individual camera.

## How the firmware is organized

The A6000 stores its firmware in a NAND memory chip of about 473 MiB, divided into partitions that Linux sees as `/dev/nflasha1`, `nflasha2`, `nflasha3`, and so on. I know about these partitions from a complete dump I made on October 20, 2026, while the camera was running firmware 3.21.

That dump came from Sony's own updater mode. With the camera in that mode, one of my scripts read each `/dev/nflasha*` partition over USB, using the same protocol that pmca uses (the open-source tool for communicating with Sony cameras over USB). It was read-only. The total came to about 916 MB. I also dumped the BootROM (24 KB) and the bootloaders (`bootloader.bin`, which contains Loader2 and Loader3). The copy wasn't useful for restoring anything, but it did let me analyze everything offline.

The three partitions that matter:

- `nflasha1` is the factory updater: a small FAT12 partition containing a Linux kernel, an initrd, and the programs used to install firmware over USB. The 3.2x packages don't include an updater image, so no firmware update rewrites it.
- `nflasha2` stores settings and state: the installed version (`\updater\dat4`) and the updater flags, including the `\updater\mode` file.
- `nflasha3` contains the main firmware (`av-cam.bin` and other files).

## The brick

A few days later, I installed a modified firmware I had created through reverse engineering on my A6000: version 3.25. The updater reached 100% and displayed `Done`. After rebooting, the camera was dead. It had no USB connection and would not enter recovery mode. The only sign of life was the LED flashing three long times and then two short times.

With the camera inaccessible, I statically analyzed Sony's bootloaders (Loader2 and Loader3) using REA, a reverse-engineering tool, with Claude's help. The LED pattern corresponded to Loader3 error code −302. My hypothesis was that the cause was in `nflasha3`, which I had recompressed using a format that the hardware decompressor could not read (this was an inference from analysis, not a measurement; I'll explain below what I was and wasn't able to confirm). My firmware had passed all the checks on the PC, and it still bricked the camera.

There was one piece of good news: the factory updater (`nflasha1`) had not been touched. The problem was that Loader3 never got as far as launching it.

Using the dump, I opened `nflasha1`, extracted its initrd (a CRAMFS), and disassembled its programs. Its `UdtrMain.sh` script checks for files named `mode1`, `mode2`, `mode3`, or `mode6`. If it doesn't find any of them, it defaults to user mode and waits for firmware over USB. In other words, the updater doesn't need a flag to run. I just needed to get Loader3 to launch it.

## Why SWD

I needed a way into the camera, and the usual access paths were unavailable:

- USB was impossible because Loader3 never gets far enough to expose it.
- Writing to the NAND externally wasn't an option: I hadn't identified the chip and didn't have the BootROM key at that point (I read it over SWD later, [R51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md)).
- Conventional JTAG was ruled out: according to the schematic, TDI, TCK, and TMS are tied to 3.15 V.

That left SWD, the two-wire version of the debug interface. In the service manual, SWCLK (Serial Wire Clock) comes from ball W25 of the BIONZ processor (IC6000), and SWDIO (Serial Wire Data I/O) comes from W26. Both signals run to connector CN4906 through two resistors, R4911 and R4912. On my camera, those resistors and the connector are not populated; only the footprints are present. There was nowhere to plug in, so I had to solder directly to the pads. There was also an unknown: an eFuse might have disabled debugging, and there was no way to know until I tried.

<img width="1600" height="1200" alt="Board and schematic of the SWD area (1 of 4)" src="https://github.com/user-attachments/assets/765d2a89-0d2d-4157-abff-4025e1dbfeed" />
<img width="998" height="827" alt="Board and schematic of the SWD area (2 of 4)" src="https://github.com/user-attachments/assets/601be974-1db5-4fc5-bb9c-50544645ba3f" />
<img width="1565" height="827" alt="Board and schematic of the SWD area (3 of 4)" src="https://github.com/user-attachments/assets/39ab2c04-9576-4e65-a0e4-778afc8e23f6" />
<img width="790" height="950" alt="Board and schematic of the SWD area (4 of 4)" src="https://github.com/user-attachments/assets/69279de0-8e73-4c85-a2fe-ead7ad08fb14" />

## Materials used

- Probe: RP2040 Zero with `debugprobe-zero` v2.3.0.
- AWG30 enamelled wire, solder, soldering iron, UV-curable solder mask and Kapton tape.
- Multimeter.
- Software: OpenOCD 0.12.0 and `pmca-console`, plus the official 3.26 package.
- For the analysis: REA and Claude.
- Recommended in [R46](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r46-procedimiento-fisico-swd.md) (I am not confirming which ones I used): a magnifier or microscope, gel flux, desoldering braid and a supply limited to 1 A or a charged NP-FW50 battery.

## The setup

Before connecting anything, I took measurements with a multimeter. With the camera powered off, I checked that there were no shorts between the pads and ground or the power rails. I did not check continuity between each pad and the BIONZ; I relied on the service manual schematic. With the camera powered on and no probe connected, I measured 3.09 V on both pads, which was compatible with a 3.3 V probe. If I had measured 1.8 V, I would not have connected it.

I soldered an AWG30 wire to the lower pad of R4911 (SWCLK, on the BIONZ side), another to the lower pad of R4912 (SWDIO, also on the BIONZ side), and a third to ground. I secured them with UV-curable solder mask and Kapton tape. I also took a ground connection from the shell of the micro HDMI port.

<img width="720" height="1280" alt="Wires soldered to the R4911 and R4912 pads" src="https://github.com/user-attachments/assets/40c0214c-a9df-4865-9a94-b295395daa86" />

For the probe, I used an RP2040 Zero running the `debugprobe-zero` v2.3.0 firmware (https://github.com/inindev/debugprobe-zero), which turns it into a CMSIS-DAP adapter. SWCLK goes to GPIO 10, SWDIO to GPIO 11, and ground to GND. On the PC, I used OpenOCD, with Claude's assistance.

<img width="720" height="1280" alt="RP2040 Zero probe and its wiring (1 of 2)" src="https://github.com/user-attachments/assets/5bb2619a-3f21-44a5-9ea3-7404ec95e46c" />
<img width="720" height="1280" alt="RP2040 Zero probe and its wiring (2 of 2)" src="https://github.com/user-attachments/assets/3e5011f3-3d56-450b-ad7b-6e5205763d1d" />
https://github.com/user-attachments/assets/6345ec01-d72f-49fd-8cec-93e6734b30ae

## First contact

With the wires soldered in place, the first thing I did was check whether the processor responded. I launched OpenOCD using the `cmsis-dap` driver and SWD transport at 100 kHz to be cautious. The DPIDR was `0x3ba02477`, a valid value.

That answered one of the biggest questions: SWD read access was not blocked by any protection mechanism that prevented access to the DAP. I did not test writing at that point. I increased the speed to 1 MHz and checked that 256 test words matched the values read at 100 kHz; I performed the larger dumps at that speed.

When I explored the DAP (the chip's debug access block), I found three access ports. Based on their identifiers, I inferred that one was for physical memory, another for debugging, and the third for JTAG. Through the debug port, I reached a ROM table containing four Cortex-A5 cores. I worked only with the first one.

Using the memory access port, I read the boot vectors and dumped the RAM: one megabyte first, followed by another two. I made each dump twice and they were identical, byte for byte. In RAM, I found the running Loader3, identical to Sony's original. I also found the bootloader's internal log and the file table it was trying to load.

Then I halted the CPU and saw where it was: in the LED loop, with the registers showing error code −302. By chaining breakpoints from the Loader3 entry point (I'll explain the technique shortly), I determined that the error occurred while loading `\sabin\idt_cam.bin`, which is in partition 3. That matches my theoretical diagnosis, which pointed to `nflasha3`. What this measurement cannot prove is the exact reason: the compression format remains an inference.

## How to halt a boot process that takes seconds

The camera's startup passes through three successive stages: BootROM, Loader2, and Loader3. It all happens within a few seconds (Loader3 takes less than one), so there isn't enough time to connect and inspect what is happening. You have to halt the CPU almost as soon as it starts and prepare the breakpoints at the locations you want to inspect.

My first attempt was to set breakpoints in Loader2 so they would trigger later, in Loader3. It didn't work: they did not survive into that stage. I confirmed that a breakpoint in the LED routine, which runs on every failed boot, never triggered. I don't know why the breakpoints are lost. I only know that they are.

What worked was proceeding in stages. As soon as the SWD connection responds, I halt the CPU and set a single breakpoint at the Loader3 entry point. When it triggers, I remove that breakpoint, set the next one in the chain, and continue until I reach the point I want to inspect.

There is an important detail at each halt. Before resuming, I remove the current breakpoints, advance by one instruction, and then set the next ones. If I don't advance that instruction, the CPU remains halted right on the breakpoint I just set, and when I resume it immediately triggers again, over and over.

The second trap is the registers. The processor has separate copies of `sp` (stack pointer) and `lr` (link register, or return address) for each operating mode. Loader3 runs in Supervisor mode. On this core, OpenOCD's generic `sp` and `lr` names do not refer to those banked registers and return 0 even when the CPU is perfectly fine. I saw `lr = 0` and thought execution had jumped to a null address, which would have meant a serious failure. When I requested the mode-specific registers, `sp_svc` and `lr_svc`, the stack and return address were healthy. If you read registers over SWD on this chip, make sure you use the registers for the current mode.

## The idea: don't write anything, just change a register

With the chained breakpoints working, I could inspect the boot process from the inside. My first idea was to use them to write to the NAND, for example by creating the `\updater\mode` file in `nflasha2`. I looked at how Loader3 handles this, and it wasn't viable. Its block layer accepts write requests and reports success without actually transferring anything. The functions that really write to the NAND are in RAM, but Loader3 doesn't use them. Calling them myself without the NAND controller's context could damage the translation layer for the entire NAND.

The way forward came from somewhere else. I read the `bootloader.bin` dump (480 KiB), disassembled Loader3, and looked for what determines the boot mode. There are several modes. Normal mode (11), where my camera had crashed, loads `nflasha3`. Only mode 3 launches the updater in `nflasha1`, bypassing `nflasha3`, and Loader3 selects it only if it finds the `\updater\mode` file in `nflasha2`.

The check is in a function I named `chk updater`. It mounts `nflasha2`, calls a routine that looks for `\updater\mode`, and compares the result with zero:

```asm
c01f15c0:  cmp r0, #0
           bge → file exists → returns 1 → mode 3
```

If `r0` is greater than or equal to zero, the file exists and mode 3 is selected. On my bricked camera, `r0` contained `0xfffffed2`, a negative number meaning “does not exist.” (It's the same number as the LED error code; I have not demonstrated that they share the same cause.)

I set a breakpoint right at that comparison and, at that moment, forced `r0 = 0`. I modified only the `r0` register while the CPU was halted immediately before executing that comparison.

I didn't write anything to memory or the NAND. Loader3 thought the file existed and selected the updater mode. That function is called from eight places, but the boot path goes through it twice. I set `r0 = 0` at both points and read it back to verify the change. From the Loader3 entry point to the updater starting, 696 milliseconds elapsed.

## Installation and verification
<img width="720" height="1280" alt="Installing firmware 3.26" src="https://github.com/user-attachments/assets/cb369a75-3c27-4cb6-b993-0e51495df575" />

The factory updater booted, and the PC detected Sony's USB device in updater mode. I started installing the official 3.26 firmware using `pmca-console`. The Sony updater wrote to the NAND, not me.

The first attempt stopped at 45% with error `0x1063`. According to previous documentation in my project, this code usually indicates that Darwin (the power-management microcontroller) is not responding, but I could not confirm the cause in this case. I turned the camera off and on again. The updater started on its own, without repeating the SWD trick: the `\updater\mode` file was already there, created by Sony's updater when the installation began (this mechanism was anticipated in my analysis; I did not verify it by reading the NAND). The second attempt reached 100%.

To verify the recovery, I removed the battery for ten seconds and turned the camera on with OpenOCD closed. It appeared as `ILCE-6000` in Mass Storage mode, running firmware 3.26, with no error LED.
<img width="720" height="1280" alt="Final check of the camera" src="https://github.com/user-attachments/assets/479e0f95-1ecd-46cc-aa53-a91235362123" />

## After the recovery

With the probe still soldered I installed 3.27 (the 3.25c content with a 3.27 header), read the `nflasha0` key over SWD and built a 3.28 fallback package ([R50](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r50-paquete-327.md), [R51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md)). The first physical test of the electronic-shutter selector ([R52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r52-prueba-fisica-selector-327.md)) showed that it works inside BIONZ, but the value is never seen in the packet sent to Darwin. This is work in progress and is not validated.

## Practical tips

- Launch OpenOCD with `nohup … & disown` so it doesn't exit with the shell.
- Don't run two OpenOCD instances against the same probe.
- Avoid `kill -9`: it can leave the debug state dirty and force you to restart the camera.
- When you insert the battery with the power switch set to OFF, the camera starts up and shuts itself down in less than a second. That's not a fault.

## When to stop

- A short circuit, an abnormal reading or an unexpected voltage.
- A smell, heat or current draw above 1 A.
- The DAP reports that debugging is disabled.
- Any doubt about what will be written or where: do not write.

## Limitations and risks

- This worked on one camera, with one specific failure and one specific probe. It is not a guarantee.
- Soldering to 0402 pads is irreversible and can lift traces. The wrong voltage on SWCLK/SWDIO can damage the BIONZ.
- The cause of error `0x1063` is still unknown; it could have been an isolated failure or interference from the probe.
- The probe is still soldered to my board; I have not removed it yet.
- I have not verified that the exact script, `analysis/e26-recovery/r48_updater_swd.cfg`, will work as-is on another camera.
- Full technical details: [R46](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r46-procedimiento-fisico-swd.md) (planned procedure), [R47](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md) (first contact), [R48](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md) (plan) and [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md) (closing report).
