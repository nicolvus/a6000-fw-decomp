#!/usr/bin/env python3
"""Genera (NO instala) el FDAT fw321 con Darwin tipo 0 y lo verifica descifrándolo.
Uso: darwin_fdat_build.py [VERSION=3.22]   salida en analysis/darwin-patch/fdat/ (ignorada por git)"""
import os, subprocess, sys, tarfile, tempfile, zlib

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FW, PATCH = f'{R}/firmware/extracted/fw321', f'{R}/analysis/darwin-patch'
OUT, FWTOOL = f'{PATCH}/fdat', [sys.executable, f'{R}/references/fwtool/fwtool.py']
ver = sys.argv[1] if len(sys.argv) > 1 else '3.22'  # 3.21 sobre 3.21 lo rechaza el updater («Invalid version»)
rep = {'0640_darwin/darwin_core.bin': open(f'{PATCH}/darwin_core_tipo0.bin', 'rb').read(),
       '0641_darwin_sum/darwin.sum': open(f'{PATCH}/darwin.sum.tipo0', 'rb').read()}
assert '%08x' % zlib.crc32(rep['0640_darwin/darwin_core.bin']) == '0e2620b4'
os.makedirs(OUT, exist_ok=True)

# Parche en sitio del tar oficial (mismos tamaños): cabeceras, orden y relleno intactos
tar = bytearray(open(f'{FW}/firmware.tar', 'rb').read())
for m in tarfile.open(f'{FW}/firmware.tar').getmembers():
    if m.name in rep:
        d = rep.pop(m.name)
        assert len(d) == m.size, m.name
        tar[m.offset_data:m.offset_data + m.size] = d
assert not rep
open(f'{OUT}/firmware_tipo0.tar', 'wb').write(tar)
cfg = open(f'{FW}/config.yaml').read()
assert "version: '3.21'" in cfg
open(f'{OUT}/config-{ver.replace(".", "")}.yaml', 'w').write(cfg.replace("version: '3.21'", f"version: '{ver}'"))
subprocess.run(FWTOOL + ['pack', '-c', f'{OUT}/config-{ver.replace(".", "")}.yaml', '-u', f'{FW}/updater.img',
                         '-f', f'{OUT}/firmware_tipo0.tar', '-o', OUT], check=True)

# Verificación: fwtool comprueba CRC-32 de cabecera y suma de cada bloque al descifrar
with tempfile.TemporaryDirectory() as t:
    subprocess.run(FWTOOL + ['unpack', '-f', f'{OUT}/firmware_packed.fdat', '-o', t], check=True, capture_output=True)
    assert open(f'{t}/firmware.tar', 'rb').read() == bytes(tar), 'tar descifrado distinto'
    assert open(f'{t}/updater.img', 'rb').read() == open(f'{FW}/updater.img', 'rb').read()
    assert f"version: '{ver}'" in open(f'{t}/config.yaml').read()
print('OK: FDAT descifrado y verificado ->', f'{OUT}/firmware_packed.fdat')
