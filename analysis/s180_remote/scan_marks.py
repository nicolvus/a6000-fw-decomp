#!/usr/bin/env python3
"""S180 - marcas textuales del sub-modo REMOTE en los tres firmware."""
import os, re, json

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
MARKS = [
    b"AccyUmDeviceRemote", b"AccyUmDeviceBase", b"AccyUmKeyStatusMgr",
    b"AccyMiDeviceBase", b"AccyMiDeviceLight",
    b"[ACCY]", b"[REMOTE]", b"AccyUart", b"NotifyInput", b"NotifyDial",
    b"RemoteClose", b"Tally", b"Zoom", b"Spinal", b"EventKey",
    b"NotifyUartCommand", b"NotifyUartResponse", b"NotifyUartTimedOut",
    b"SaveInfo", b"RestoreInfo", b"AccyCmdClr", b"ExecUartCommand",
    b"To Input KEY", b"CallForTransaction", b"NotifyApiRequest",
    b"GUIDE FRAME", b"START STOP", b"PHOTO FREEZE", b"PHOTO REC", b"ZOOM OFF",
    b"AccyUartOpen", b"AccyUartClose", b"AccyUartSend",
    b"aisatsu", b"AISATSU", b"UNSUPPORTED", b"JIRO", b"LANC", b"HELLO",
    b"UMMAIN", b"WaterHousing", b"AvOut", b"LANC-AVR",
]
out = {}
for k, p in BINS.items():
    d = open(p, "rb").read()
    r = {m.decode(): d.count(m) for m in MARKS}
    out[k] = r
    print(f"== {k}")
    for m in MARKS:
        print(f"   {m.decode():<24} {d.count(m)}")
json.dump(out, open("analysis/s180_remote/marks.json", "w"), indent=1)
