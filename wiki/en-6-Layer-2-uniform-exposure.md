# 6. Layer 2: uniform exposure (RAM patch)

With 3.23 alone the shutter does not move, but without a rear curtain row `i` integrates **T + ≈7 ms + 15.2 µs·i**: the bottom can
get up to 3.7× more light than the top. Layer 2 sets `ShutMode 0` and an `r5` register computed from the shutter speed so the sensor
controls the exposure of each row: (4219 − `r5`) × 15.2 µs.

- It lives **in RAM only**: it does not touch flash, NVRAM or `nflasha3`. A reboot clears it.
- A **watchdog** on the camera reverts it on its own after 25 s if the PC stops responding.
- Tested in T050: 12 shots and a burst of 4 between 1/4000 and 1/30, always reverted. From 1/15 it falls back to normal shooting; 1/8000 has only been emulated.

## Camera requirements

1. **Camera on 3.23** ([step 5](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-5-Installing-3.23)) and Wi-Fi connected to your local network.
2. **OpenMemories Tweak** ([upstream](https://github.com/ma1co/OpenMemories-Tweak), source in `references/tweak/`): install it with
   `pmca-console install` following the "Installing Android apps" section of [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE). In the app tick
   **Enable Telnet** (port 23, root, no login) and **Enable ADB** (port 5555).
3. **RemoteShutter** (the project's app, HTTP server on port 8080; endpoints `/shoot`, `/ss`, `/status`, `/info`, `/log`, `/jpg`):
   build it with `tools/remote-shutter/build.sh` (needs JDK 17 and build-tools in `~/.local/android-build`) and install it over ADB:
   ```sh
   python scripts/camera_install_apk.py tools/remote-shutter/out/RemoteShutter.apk 192.168.1.29
   ```
   Open it on the camera before shooting. Install and control scripts: [Tools](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-12-Tools).

## Using it from the PC

The patch is applied from the PC over telnet, once per shot or burst, with a watchdog on the camera that reverts it on its own after 25 s.
Steps, scripts and commands: [Tools](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-12-Tools). For every shot or burst:

1. Check that the RAM bytes are the original ones (if not, **do not patch**).
2. Start the watchdog on the camera.
3. Write `ShutMode` (`0x836d6fb6`) and `r5` (`0x836d7000`) in **a single** telnet command and verify.
4. Shoot while watching the app (no answer in 12 s or 45 s ⇒ revert and abort).
5. Revert in a single command, notify the watchdog and verify.

Wait for the shutter speed to settle before computing `r5`. Calculation details (Spanish): `docs/capture/e25-11-r5-bionz-analisis.md` §10.

## Doing it all from the camera (idea, not implemented)

Today a PC is needed over telnet. Removing it is possible in principle, because the app already knows the shutter speed (`CameraEx.getShutterSpeed()`) and `/dev/mem`
is accessible to the app user. **None of this has been tested on the full camera**; what is known:

- **It was already tried from the app (T049):** it worked on 6 shots (1/4000, 1/1000, 1/250 ×2), with patch and revert verified, but failed in two places:
  `RandomAccessFile` cannot address `/dev/mem` above 2 GiB, and `Runtime.exec("dd")` from a ≈100 MB process with ≈8 MB free hung the `fork`
  **between the two writes**, leaving the patch half applied. That is why the app must not use `Runtime.exec`.
- **Recommended idea:** have the app talk to the local `telnetd` (`127.0.0.1:23`, no `fork` of its own) and send the same commands as the PC:
  (1) start the 25 s watchdog *inside the camera*, (2) apply both patches in **a single command**, (3) shoot, (4) revert in a single command and notify the watchdog.
  The watchdog is an `sh` independent of the app: if the app hangs or closes, the RAM goes back to the original bytes on its own.
- **Alternative:** a pre-opened helper process (or a small native helper) that does both writes in one operation, without creating processes during the shot.
- **Interface:** a "uniform" switch and the current shutter speed are enough: the app computes `r5 = 4219 − µs/15.2` and, if `r5 < 10` (T > ≈ 64 ms), shoots normally.
- **Safety conditions:** `ShutMode 0` applies to every call while patched (Live View already uses it); AF, video and long bursts are untested;
  the feature must be **off by default** and always revert in a `finally` block.
- **Making it persistent is experimental:** 3.25 put it into firmware and bricked the author's camera because of an `nflasha3` format error;
  [3.25c](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) fixes that but has never been installed. The tested path is still the RAM patch.

## Limits

- Absolute scale: the level falls ≈ 22 % below target with one reference and ±1 % with another (±25 % uncertainty).
- Rolling effect: readout takes ≈ 61 ms; moving objects come out skewed.
- Not measured: flash, video and Live View with the patches active.
- Long electronic exposure not implemented.
- Do not apply the patch from the app with `Runtime.exec`: in T049 it hung between the two writes and left `ShutMode 0` forced. Use telnet (see above).
