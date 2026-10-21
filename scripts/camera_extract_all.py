#!/usr/bin/env python3
"""Extrae todo lo ejecutable de la cámara: APK/odex/jar/dex y binarios ELF.

Uso: camera_extract_all.py OUTDIR LOADED.txt [HOST]
- Del sistema instalado (idéntico al paquete oficial 3.21, verificado con cmp): copia desde firmware/extracted/fw321/.../0700_part_image/dev/nflasha{3,7,15,16}_unpacked_unpacked
  (nflasha15=/usr, nflasha16=/android/system, nflasha7=rootfs, nflasha3=av-cam.bin/kernel/initrd).
- De la cámara en vivo, por ADB (solo lectura): /data/app/*.apk, /data/lib/** (bibliotecas de apps instaladas) y su dalvik-cache.
- LOADED.txt: rutas con mapeo en memoria de algún proceso (de /proc/*/maps); el manifiesto marca cuáles están cargadas.
Salida: OUTDIR/{apk,android-elf,usr-elf,rootfs-elf,main,live}/..., OUTDIR/manifest.json."""
import hashlib, json, os, shutil, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
T = ROOT + '/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/'
TREES = {'main': ('nflasha3_unpacked_unpacked', ''), 'rootfs': ('nflasha7_unpacked_unpacked', '/'), 'usr': ('nflasha15_unpacked_unpacked', '/usr'),
         'android': ('nflasha16_unpacked_unpacked', '/android/system')}
EXT = ('.apk', '.odex', '.jar', '.dex', '.so', '.elf', '.bin')
out, loaded_file = sys.argv[1], sys.argv[2]; host = sys.argv[3] if len(sys.argv) > 3 else '192.168.1.29'
loaded = {l.strip() for l in open(loaded_file) if l.strip()}
man = []


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()


def kind(p, head):
    if p.endswith('.apk') or head[:4] == b'PK\x03\x04': return 'apk' if p.endswith('.apk') else 'zip/jar'
    if head[:4] == b'\x7fELF': return 'elf'
    if head[:4] in (b'dey\n', b'dex\n'): return 'dex/odex'
    return None


for name, (d, mount) in TREES.items():
    base = T + d
    for dp, _, fs in os.walk(base):
        for f in fs:
            p = os.path.join(dp, f)
            if os.path.islink(p) or not os.path.isfile(p): continue
            try: head = open(p, 'rb').read(4)
            except OSError: continue
            k = kind(p, head)
            if not k: continue
            rel = os.path.relpath(p, base); rt = (mount + '/' + rel).replace('//', '/')
            dst = os.path.join(out, name, rel); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(p, dst)
            man.append({'origen': 'paquete-3.21/' + d, 'ruta_en_camara': rt, 'copia': os.path.relpath(dst, out), 'tipo': k, 'bytes': os.path.getsize(dst),
                        'sha256': sha(dst), 'cargado_en_ejecucion': rt in loaded})

# en vivo por ADB (solo lectura)
try:
    from adb_shell.adb_device import AdbDeviceTcp
    d = AdbDeviceTcp(host, 5555, default_transport_timeout_s=60); d.connect(rsa_keys=None, auth_timeout_s=10)
    files = d.shell('ls /data/app/*.apk /data/lib/*/lib/* /data/dalvik-cache/* 2>/dev/null', timeout_s=60).split()
    for r in files:
        dst = os.path.join(out, 'live', r.lstrip('/')); os.makedirs(os.path.dirname(dst), exist_ok=True)
        try: d.pull(r, dst)
        except Exception as e: print('FALLO pull', r, e); continue
        rt = '/android' + r
        man.append({'origen': 'camara-en-vivo (adb)', 'ruta_en_camara': rt, 'copia': os.path.relpath(dst, out), 'tipo': 'live', 'bytes': os.path.getsize(dst),
                    'sha256': sha(dst), 'cargado_en_ejecucion': rt in loaded})
except Exception as e:
    print('ADB no disponible:', e)

missing = sorted(l for l in loaded if not any(m['ruta_en_camara'] == l for m in man) and not l.startswith(('/android/dev', '/android/data/dalvik', '/android/mnt')))
json.dump({'archivos': man, 'cargados_sin_copia': missing}, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
n = len(man); c = sum(1 for m in man if m['cargado_en_ejecucion'])
print('archivos:', n, ' cargados en ejecución:', c, ' cargados sin copia:', len(missing))
