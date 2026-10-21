# S85 — `CLK_CTRL` (control de reloj) y `VPH_API` (API del procesado de vídeo del visor)

**Alcance:** línea de ingeniería inversa **general** de la cámara: los dos módulos **nuevos en la
fw3.21 de la A6000** que gobiernan el reloj y la señal de vídeo del visor: `CLK_CTRL` (66 trazas) y
`VPH_API` (106 trazas). No es la línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD, ni
ZPD (S75), ni ZIT (S80), ni ADF (S81), ni el API del motor de imagen (S84), ni el wireless (S72).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s85_clk_vph.py`.

---

## 1. Hecho principal: son **nuevos en la fw3.21** (VERIFICADO)

| módulo | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| `[CLK_CTRL]` | **66 trazas** (`0x43c3a1df`–`0x43c3b09c`) | **0** |
| `[VPH_API]` | **106 trazas** (`0x43ce32e7`–`0x43ce3dfc`) | **0** |

Ninguno de los dos existe en el firmware de la A7S fw3.20 → son **novedad de la fw3.21** (y explica
parte del salto de 348 frente a 277 prefijos de módulo que se mide en S79).

## 2. `[CLK_CTRL]` — control de reloj y de la señal de sincronización (VERIFICADO)

### 2.1 La API que llama (12 funciones `ddl_clkctrl_*`)

`get_clk_chg_enable` (`0x43c3a1df`), `unlock_sync_signal` (`0x43c3a220`), `lock_sync_signal`
(`0x43c3a261`), `set_sysv_delay_changing` (`0x43c3a2a6`), `set_sysv_delay` (`0x43c3a2f2`),
`set_sync_signal` (`0x43c3a335`), `set_sync_initial_signal` (`0x43c3a379`), `set_sysv_initial_delay`
(`0x43c3a3bf`), `close_dly` (`0x43c3a40a`), `open_dly` (`0x43c3a442`), `close_clk` (`0x43c3a479`),
`open_clk` (`0x43c3a4b1`).

### 2.2 La máquina de estados (VERIFICADO)

`STATE_INIT1(InitDelay)` (`0x43c3a534`) → `STATE_NORMAL(InitSignal)` (`0x43c3a55d`) → `STATE_LOCK`
(`0x43c3a588`), más `STATE_CHANGE_CLK` (`0x43c3a6e9`) y `STATE_CHANGE_CLK_LOCKING` (`0x43c3a768`).
Tarea propia: `Tsk ClkCtrl Initial` (`0x43c3a5ff`), `Main routine start!!` (`0x43c3a61f`).

### 2.3 Gestión por subsistema (VERIFICADO)

`open subsytem = 0x%04x` (`0x43c3a91a`), `close subsytem = 0x%04x` (`0x43c3a97e`),
`Busy!! 0x%04x already opened, 0x%04x can't open` (`0x43c3a93d`),
`0x%04x request open... CLK already opend by 0x%04x` (`0x43c3a9e4`),
`lock_sync_signal subsystem = %x` (`0x43c3a5a5`), `unlock_sync_signal subsystem = %x` (`0x43c3a5d1`),
`set sysv delay subsystem = %x , delay = %d` (`0x43c3af89`).

### 2.4 Cambio de reloj y de retardo (VERIFICADO)

`CHANGE_CLK dly 0x%x -> 0x%x , clk 0x%x -> 0x%x : change_vfc=0x%x` (`0x43c3a71b`),
`CHANGE_CLK2 dly %x -> %x , clk %x -> %x` (`0x43c3a7a2`),
`ClkChgExec at %x clk=%x, delay=%x->%x` (`0x43c3a811`), `DelayChgExec at 0x%x, delay=%x`
(`0x43c3a8c3`), `clk_now=%d, clk_next=%d, change_vfc=0x%0x` (`0x43c3a7d6`).
**VFC** = *vertical frequency counter* (INFERENCIA por el uso): el módulo lleva **dos VFC**,
`m_vfc.main=0x%0x, m_vfc.sub=0x%0x` (`0x43c3ac2f`) → los dos canales de vídeo (línea y panel).

### 2.5arquitectura maestro/esclavo (VERIFICADO)

`Receive Message from Master src=0x%0x` (`0x43c3abd0`), `Send Message to Slave 0x%0x`
(`0x43c3ac86`), `Send HTP at 0x%08x` (`0x43c3aae7`), `targetVfc=0x%0x, delay_req=0x%0x`
(`0x43c3ac02`), `vph stat:%d,mode:%d` (`0x43c3aa69`) → el módulo **coordina con VPH** (el procesado de
vídeo, §3) y es **esclavo de un "master"** que le manda el VFC objetivo.

## 3. `[VPH_API]` — el vocabulario de comandos del procesado de vídeo (VERIFICADO)

106 trazas: **49 comandos** + **46 comandos con sufijo `_sub`** (el segundo canal) + 3 de modo de
display + `=v_command_comp=` / `=imm_command_comp=` + **11 salidas de estado**.

### 3.1 Comandos (VERIFICADO)

- **Ruta de vídeo**: `<mode>` (`0x43ce32e7`), `<line_out>o/f:%d` (`0x43ce32f7`),
  `<panel_out>o/f:%d` (`0x43ce3311`), `<dualpanel_out>o/f:%d` (`0x43ce3c84`),
  `<update_yuv>s:%d` (`0x43ce332c`), `<mix_mode>` (`0x43ce3346`), `<force_out>` (`0x43ce3ce4`).
- **OSD**: `<osd_on>` (`0x43ce335a`), `<osdarea_on>` (`0x43ce336c`), `<osdarea>` (`0x43ce3382`),
  `<update_osd>s:%d` (`0x43ce3395`).
- **Cara**: `<faceframe_on>` (`0x43ce33af`), `<update_faceframe>` (`0x43ce33c7`),
  `<faceframe_color>` (`0x43ce35e3`) → **el visor dibuja el marco de la cara detectada** (conecta con
  S71: `update_faceframe`).
- **Texto**: `<timecode_on>` (`0x43ce33e3`), `<update_timecode>` (`0x43ce33fa`).
- **Mute / imagen**: `<yuv_mute>o/f:%d,s:%d` (`0x43ce3415`), `<yuv_mute_param>` (`0x43ce3434`),
  `<yuv_mute_immediately>` (`0x43ce3614`), `<chroma_mute>` (`0x43ce344e`),
  `<shutter_mute_param>` (`0x43ce3634`).
- **Señal de línea**: `<line_closedcaption>` (`0x43ce3465`), `<line_macrovision>` (`0x43ce3483`),
  `<line_vbidwss>` (`0x43ce349f`), `<line_sync_setup>` (`0x43ce34b7`), `<line_fchr>` (`0x43ce3652`),
  `<line_hdmi_still_range>` (`0x43ce3667`).
- **Panel**: `<panel_brightness>` (`0x43ce34d2`), `<panel_cabc>` (`0x43ce34ee`, CABC = control
 -adaptativo de retroiluminación), `<panel_depth>` (`0x43ce3504`), `<panel_reverse>` (`0x43ce351b`),
  `<panel_ysetup>` (`0x43ce3534`), `<set_panel_osd_luminance>` (`0x43ce3728`).
- **Ayudas de visualización**: `<pictureeffect>` (`0x43ce354c`), `<ylevel_caution>` (`0x43ce3565`),
  `<zebra>` (`0x43ce357f`), `<peaking>` (`0x43ce3590`), `<gridline>` (`0x43ce35a3`),
  `<histogram>` (`0x43ce35b7`), `<testpattern>` (`0x43ce35cc`), `<diceic_arb>` (`0x43ce35fe`).
- **Corrección de paralaje y color**: `<parallax_adjust>` (`0x43ce3688`),
  `<set_extblackframe>` (`0x43ce36a3`), `<set_extblackframe_livedemo>` (`0x43ce3702`),
  `<set_color_temperature>` (`0x43ce36c0`), `<set_eomainsub_inverse>` (`0x43ce36e1`).
- **Display**: `<laxo>` (`0x43ce3ca3`), `<panel_display>` (`0x43ce3cb3`), `<line_display>`
  (`0x43ce3ccc`).

Cada comando tiene su gemelo con sufijo `_sub` (p. ej. `<update_yuv_sub>` `0x43ce37d2`,
`<panel_brightness_sub>` `0x43ce39bc`, `<set_panel_osd_luminance_sub>` `0x43ce3c1f`): son los **dos
canales** (línea y panel), coherente con los dos VFC de `CLK_CTRL` (§2.4).

### 3.2 Salidas de estado (VERIFICADO)

`>hw_status<` (`0x43ce3cf9`), `>mode_status<` (`0x43ce3d0e`), `>preset_area<` (`0x43ce3d25`),
`>histogram_result<` (`0x43ce3d3c`), `>yuv_delay<` (`0x43ce3d58`), `>osdmix_size_panel<`
(`0x43ce3d6d`), `>osdmix_size_line<` (`0x43ce3d8a`), `>black_frame<` (`0x43ce3da6`),
`>panel_brightness_status<s:%d` (`0x43ce3dbd`), `>shutter_mute<` (`0x43ce3de4`),
`>shutter_mute_status<o/f:%d` (`0x43ce3dfc`).

## 4. Abierto (NO_VERIFICADO)

- Qué significan exactamente `laxo`, `diceic_arb`, `ylevel_caution`, `vbidwss`, `fchr`,
  `extblackframe`, `eomainsub`, `htp`, `vfc` (salvo lo deducido del uso).
- La correspondencia entre cada comando `<x>` y su gemelo `<x>_sub` (¿línea vs panel?).
- Quién es el "master" de `CLK_CTRL` y qué protocolo usa.
- Si `VPH_API` es un contrato con un bloque de hardware externo (VPH = *Video Processing Hardware*)
  o con el subsistema VDF (S85←S79: `VDF` 243 trazas).
- Por qué la fw3.21 introduce ambos módulos (¿soporte de un panel OLED nuevo?).

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s85_clk_vph.py -q
```
