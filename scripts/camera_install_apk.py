#!/usr/bin/env python3
"""Instala un APK en la cámara por ADB (puerto 5555) con adb-shell: push a /data/local/tmp y pm install -r.
Uso: camera_install_apk.py APK [HOST]"""
import sys
from adb_shell.adb_device import AdbDeviceTcp

apk, host = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else '192.168.1.29')
d = AdbDeviceTcp(host, 5555, default_transport_timeout_s=60)
d.connect(rsa_keys=None, auth_timeout_s=10)
d.push(apk, '/data/local/tmp/rs.apk')
print(d.shell('pm install -r /data/local/tmp/rs.apk', timeout_s=120).strip())
