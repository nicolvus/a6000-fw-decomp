"""Muestreo E25-22 con RAM de solo lectura y fotografías normales."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import threading
import time
from datetime import datetime
from pathlib import Path

from adb_shell.adb_device import AdbDeviceTcp  # type: ignore[import-untyped]
from e25_19_readonly import HOST, Telnet, now, verify_originals
from e25_19_test import Camera
from e25_19b_cap import muestra

PAIRS = [(0x44025918, 0x4401C7E0), (0x4401F468, 0x4401C678),
         (0x44026688, 0x4401C744), (0x44022CCC, 0x4401C684),
         (0x440237DC, 0x4401C698), (0x44025FB4, 0x4401C764)]
OFFSET = 0x40000000


def decode_shadows(data: list[bytes]) -> list[int]:
    if len(data) != 6 or any(len(b) != 4 or struct.unpack_from('<H', b)[0] != i
                             for i, b in enumerate(data, 3)):
        raise ValueError('identificadores de sombras inesperados')
    return [b[2] for b in data]


def shadows(tr: Telnet) -> dict:
    start = time.time()
    raw = tr.read_many([(v + OFFSET, 4) for _, v in PAIRS])
    return {'t_epoch': start, 'latency_ms': round(1000 * (time.time() - start), 1),
            'hex': [b.hex() for b in raw], 'values': decode_shadows(raw)}


def files(adb: AdbDeviceTcp) -> set[str]:
    folders = adb.shell('ls /mnt/sdcard/DCIM').split()
    folder = max((x for x in folders if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {folder + '/' + x for x in adb.shell('ls /mnt/sdcard/DCIM/' + folder).split()
            if x.startswith('DSC')}


def run() -> None:
    out = Path('analysis/camera-dumps') / (datetime.now().strftime('%Y%m%d-%H%M%S') + '-E25-22')
    out.mkdir(parents=True, exist_ok=False)
    camera = Camera(HOST)
    result: dict = {'start_utc': now(), 'shots': [], 'abort': None}
    control = Telnet(timeout=20)
    time.sleep(2)
    sample_tr = Telnet(timeout=20)
    time.sleep(2)
    adb = AdbDeviceTcp(HOST, 5555, default_transport_timeout_s=60)
    try:
        if not adb.connect(rsa_keys=None, auth_timeout_s=10):
            raise RuntimeError('ADB no disponible')
        result['baseline_params'] = camera.get('/params')
        result['baseline_info'] = camera.info()['raw']
        if 'getPictureStorageFormat=rawjpeg' not in result['baseline_params']:
            raise RuntimeError('RAW+JPEG no está activo')
        if 'bursting=false' not in result['baseline_info']:
            raise RuntimeError('cámara ocupada')
        result['firmware_md5'] = control.run('busybox md5sum /system/av-cam.bin').strip()
        if not result['firmware_md5'].startswith('ef2e3003ddad7185b5398cb76287c5aa '):
            raise RuntimeError('firmware diferente')
        result['originals_initial'] = verify_originals(control)
        if not result['originals_initial']['ok']:
            raise RuntimeError('originales diferentes')
        got = control.read_many([(a + OFFSET, 4) for a, _ in PAIRS])
        if [struct.unpack('<I', x)[0] for x in got] != [v for _, v in PAIRS]:
            raise RuntimeError('GOT de sombras diferente')
        result['shadow_got_hex'] = [x.hex() for x in got]
        result['initial_shadows'] = shadows(sample_tr)
        for n, d in [(1, 1000), (4, 1)]:
            before = files(adb)
            rec: dict = {'requested': f'{n}/{d}', 'samples': [], 'status': []}
            result['shots'].append(rec)
            rec['set'] = camera.get(f'/ss?n={n}&d={d}', t=60)
            if not rec['set'].startswith('ss-ok'):
                raise RuntimeError('velocidad no aceptada: ' + rec['set'])
            count = int(camera.info()['count'])
            stop = threading.Event()

            def poll(stop: threading.Event = stop, rec: dict = rec) -> None:
                while not stop.is_set():
                    try:
                        s: dict = {'shadows': shadows(sample_tr)}
                        start = time.time()
                        s['capture'] = muestra(sample_tr)
                        s['capture_latency_ms'] = round(1000 * (time.time() - start), 1)
                        rec['samples'].append(s)
                    except Exception as exc:  # noqa: BLE001 - se conserva el error de muestreo
                        rec['samples'].append({'error': repr(exc), 't_epoch': time.time()})
                        stop.set()

            thread = threading.Thread(target=poll, daemon=True)
            thread.start()
            time.sleep(1)
            if stop.is_set():
                raise RuntimeError('muestreo falló antes de disparar')
            rec['shoot_time'] = time.time()
            rec['shoot_reply'] = camera.get('/shoot')
            done = False
            while time.time() - rec['shoot_time'] < 90:
                status = camera.status()
                rec['status'].append([time.time(), status])
                if 'error' in status:
                    break
                if int(camera.info()['count']) > count and status.startswith('done'):
                    done = True
                    break
                time.sleep(0.2)
            time.sleep(2)
            stop.set()
            thread.join(timeout=30)
            if thread.is_alive():
                raise RuntimeError('muestreo no terminó')
            rec['post_shadows'] = shadows(sample_tr)
            rec['log'] = camera.get('/log')
            rec['originals_after'] = verify_originals(control)
            if not done or not rec['originals_after']['ok'] or any('error' in x for x in rec['samples']):
                raise RuntimeError('captura o controles no concluyentes')
            time.sleep(2)
            new = sorted(files(adb) - before)
            rec['new_files'] = new
            raw = [x for x in new if x.upper().endswith('.ARW')]
            if len(raw) != 1:
                raise RuntimeError('no se identificó un RAW único: ' + repr(new))
            dst = out / f'{n}_{d}.ARW'
            adb.pull('/mnt/sdcard/DCIM/' + raw[0], str(dst))
            rec['raw_sha256'] = hashlib.sha256(dst.read_bytes()).hexdigest()
            rec['raw_path'] = str(dst)
            print('done', rec['requested'], 'samples', len(rec['samples']), 'raw', dst, flush=True)
            (out / 'evidence.json').write_text(json.dumps(result, indent=2) + '\n')
    except Exception as exc:  # noqa: BLE001 - se conserva la causa del aborto
        result['abort'] = repr(exc)
        print('abort', repr(exc), flush=True)
    finally:
        try:
            result['originals_final'] = verify_originals(control)
        except Exception as exc:  # noqa: BLE001 - se conserva el error de comprobación
            result['originals_final_error'] = repr(exc)
        result['end_utc'] = now()
        (out / 'evidence.json').write_text(json.dumps(result, indent=2) + '\n')
        adb.close()
        control.close()
        sample_tr.close()
        print('evidence', out, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-fresh-app', action='store_true', required=True,
                        help='Confirmar que RemoteShutter se reinició y no se activó su modo silent')
    parser.parse_args()
    run()
