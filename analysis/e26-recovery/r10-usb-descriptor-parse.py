"""E26-R10: Parse the USB Charger (054c:0994) descriptor embedded in darwin_core.bin.

Validates that the descriptor found in Darwin's firmware (darwin_core.bin)
matches the descriptor observed on the physical camera via `lsusb -v -d 054c:0994`.

Offline-only: reads local firmware files, does not touch the camera.
"""

import struct
import sys
from pathlib import Path

DARWIN_CORE = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)

# Observed from the physical camera (`lsusb -v -d 054c:0994`), E26-R10 §3.2.
OBSERVED = {
    "bcdUSB": 0x0200,
    "bDeviceClass": 0,
    "bDeviceSubClass": 0,
    "bDeviceProtocol": 0,
    "bMaxPacketSize0": 64,
    "idVendor": 0x054C,
    "idProduct": 0x0994,
    "bcdDevice": 0x0100,
    "bNumConfigurations": 1,
    "bConfigurationValue": 1,
    "bmAttributes": 0x80,
    "MaxPower_mA": 500,
    "bInterfaceClass": 3,  # HID
    "bInterfaceSubClass": 0,
    "bInterfaceProtocol": 0,
    "bNumEndpoints": 1,
    "bcdHID": 0x0111,
    "wDescriptorLength": 19,
    "ep_address": 0x81,
    "ep_attr": 0x03,  # Interrupt
    "ep_max_packet": 8,
    "ep_interval": 1,
    "manufacturer": "Sony",
    "product": "USB Charger",
}


def find_vidpid(data: bytes, vidpid: bytes = b"\x4c\x05\x94\x09") -> int:
    """Return the offset of the VID/PID little-endian pair in data."""
    pos = data.find(vidpid)
    if pos < 0:
        raise FileNotFoundError("VID/PID 054c:0994 not found in darwin_core.bin")
    return pos


def parse_descriptors(data: bytes, desc_start: int):
    """Walk USB descriptors starting at desc_start (must point at bLength)."""
    descs = []
    off = desc_start
    end = len(data)
    while off + 2 <= end:
        bLength = data[off]
        if bLength == 0 or off + bLength > end:
            break
        bType = data[off + 1]
        payload = data[off + 2 : off + bLength]
        descs.append({"off": off, "bLength": bLength, "bType": bType, "payload": payload})
        off += bLength
    return descs


def le16(b: bytes) -> int:
    return struct.unpack("<H", b)[0]


def verify(descs):
    failures = []

    # --- Device descriptor (type 0x01) ---
    # payload = descriptor bytes 2..17 (16 bytes); descriptor offset N -> payload[N-2]
    dev = next((d for d in descs if d["bType"] == 0x01), None)
    if dev is None:
        failures.append("no device descriptor")
    else:
        p = dev["payload"]
        checks = {
            "bLength": (dev["bLength"] == 0x12, dev["bLength"]),
            "bcdUSB": (le16(p[0:2]) == OBSERVED["bcdUSB"], hex(le16(p[0:2]))),
            "bDeviceClass": (p[2] == OBSERVED["bDeviceClass"], p[2]),
            "bDeviceSubClass": (p[3] == OBSERVED["bDeviceSubClass"], p[3]),
            "bDeviceProtocol": (p[4] == OBSERVED["bDeviceProtocol"], p[4]),
            "bMaxPacketSize0": (p[5] == OBSERVED["bMaxPacketSize0"], p[5]),
            "idVendor": (le16(p[6:8]) == OBSERVED["idVendor"], hex(le16(p[6:8]))),
            "idProduct": (le16(p[8:10]) == OBSERVED["idProduct"], hex(le16(p[8:10]))),
            "bcdDevice": (le16(p[10:12]) == OBSERVED["bcdDevice"], hex(le16(p[10:12]))),
            "bNumConfigurations": (
                p[15] == OBSERVED["bNumConfigurations"],
                p[15],
            ),
        }
        # bDescriptorType is verified separately via dev["bType"] (not in payload).
        for name, (ok, got) in checks.items():
            expected = OBSERVED.get(name, "n/a")
            if not ok:
                failures.append(f"device.{name}: expected {expected} got {got}")

    # --- Configuration descriptor (type 0x02) ---
    # payload = desc bytes [2..8] (7 bytes): p[0..1]=wTotalLen, p[2]=bNumIf,
    # p[3]=bCfgValue, p[4]=iCfg, p[5]=bmAttributes, p[6]=bMaxPower
    cfg = next((d for d in descs if d["bType"] == 0x02), None)
    if cfg is None:
        failures.append("no config descriptor")
    else:
        p = cfg["payload"]
        checks = {
            "bNumInterfaces": (p[2] == 1, p[2]),
            "bmAttributes": (p[5] == OBSERVED["bmAttributes"], hex(p[5])),
            "MaxPower_mA": (p[6] * 2 == OBSERVED["MaxPower_mA"], p[6] * 2),
        }
        for name, (ok, got) in checks.items():
            if not ok:
                failures.append(f"config.{name}: expected {OBSERVED[name]} got {got}")

    # --- Interface descriptor (type 0x04) ---
    intf = next((d for d in descs if d["bType"] == 0x04), None)
    if intf is None:
        failures.append("no interface descriptor")
    else:
        p = intf["payload"]
        checks = {
            "bInterfaceClass": (p[3] == OBSERVED["bInterfaceClass"], p[3]),
            "bInterfaceSubClass": (p[4] == OBSERVED["bInterfaceSubClass"], p[4]),
            "bInterfaceProtocol": (p[5] == OBSERVED["bInterfaceProtocol"], p[5]),
            "bNumEndpoints": (p[2] == OBSERVED["bNumEndpoints"], p[2]),
        }
        for name, (ok, got) in checks.items():
            if not ok:
                failures.append(f"interface.{name}: expected {OBSERVED[name]} got {got}")

    # --- HID descriptor (type 0x21) ---
    hid = next((d for d in descs if d["bType"] == 0x21), None)
    if hid is None:
        failures.append("no HID descriptor")
    else:
        p = hid["payload"]
        checks = {
            "bcdHID": (le16(p[0:2]) == OBSERVED["bcdHID"], hex(le16(p[0:2]))),
            "wDescriptorLength": (
                le16(p[5:7]) == OBSERVED["wDescriptorLength"],
                le16(p[5:7]),
            ),
        }
        # Report descriptor type byte at descriptor offset 6 -> payload[4]
        if len(p) > 4 and p[4] != 0x22:
            failures.append(f"hid.report_type: expected 0x22 got 0x{p[4]:02x}")
        for name, (ok, got) in checks.items():
            if not ok:
                failures.append(f"hid.{name}: expected {OBSERVED[name]} got {got}")

    # --- Endpoint descriptor (type 0x05) ---
    eps = [d for d in descs if d["bType"] == 0x05]
    if not eps:
        failures.append("no endpoint descriptor")
    else:
        p = eps[0]["payload"]
        checks = {
            "ep_address": (p[0] == OBSERVED["ep_address"], hex(p[0])),
            "ep_attr": (p[1] == OBSERVED["ep_attr"], hex(p[1])),
            "ep_max_packet": (le16(p[2:4]) == OBSERVED["ep_max_packet"], le16(p[2:4])),
            "ep_interval": (p[4] == OBSERVED["ep_interval"], p[4]),
        }
        for name, (ok, got) in checks.items():
            if not ok:
                failures.append(f"endpoint.{name}: expected {OBSERVED[name]} got {got}")

    # --- String descriptors: "Sony" and "USB Charger" ---
    # payload = desc bytes [2..bLength] (the UTF-16LE text, no header).
    strings = [d for d in descs if d["bType"] == 0x03]
    found_strings = []
    for s in strings:
        p = s["payload"]
        try:
            text = p.decode("utf-16-le")
            found_strings.append(text)
        except UnicodeDecodeError:
            found_strings.append(f"<undecodable:{p.hex()}>")
    if OBSERVED["manufacturer"] not in found_strings:
        failures.append(f'string missing manufacturer "{OBSERVED["manufacturer"]}"')
    if OBSERVED["product"] not in found_strings:
        failures.append(f'string missing product "{OBSERVED["product"]}"')

    # --- Capability summary ---
    hid_num_desc = None
    if hid is not None and len(hid["payload"]) > 3:
        hid_num_desc = hid["payload"][3]
    output_declared = hid_num_desc is not None and hid_num_desc > 1
    feature_declared = False  # no feature report descriptor observed

    return {
        "failures": failures,
        "descriptor_count": len(descs),
        "types_found": sorted({d["bType"] for d in descs}),
        "strings": found_strings,
        "output_report_declared": output_declared,
        "feature_report_declared": feature_declared,
        "hid_num_descriptors": hid_num_desc,
    }


def main():
    if not DARWIN_CORE.exists():
        print(f"ERROR: {DARWIN_CORE} not found", file=sys.stderr)
        return 1

    data = DARWIN_CORE.read_bytes()
    pos = find_vidpid(data)
    # The VID/PID pair is at offset pos; the device descriptor starts 10 bytes
    # earlier (idVendor at off+8, idProduct at off+10) => desc start = pos - 8.
    desc_start = pos - 8
    descs = parse_descriptors(data, desc_start)
    result = verify(descs)

    print("=== E26-R10 USB Charger descriptor validation ===")
    print(f"darwin_core.bin: {DARWIN_CORE}")
    print(f"VID/PID 054c:0994 at file offset 0x{pos:06x}")
    print(f"Device descriptor starts at 0x{desc_start:06x}")
    print(f"Descriptors walked: {result['descriptor_count']}")
    print(f"Descriptor types found: {[hex(t) for t in result['types_found']]}")
    print(f"String descriptors: {result['strings']}")
    print(f"HID num descriptors: {result['hid_num_descriptors']}")
    print(f"Output report declared: {result['output_report_declared']}")
    print(f"Feature report declared: {result['feature_report_declared']}")
    print()
    if result["failures"]:
        print("MISMATCHES vs observed lsusb -v:")
        for f in result["failures"]:
            print(f"  - {f}")
        print("\nRESULT: DESCRIPTOR DOES NOT MATCH OBSERVED (unexpected)")
        return 1
    print("All descriptor fields match the observed `lsusb -v -d 054c:0994` output.")
    print("RESULT: Darwin (darwin_core.bin) contains the USB Charger descriptor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
