"""S72 — Wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand").

Anclas verificadas contra los binarios userland del fw3.21 (A6000) y fw3.20 (A7S).
Ver analysis/s72_wlan/wlan_playmem.md

Este archivo sustituye al borrador del subagente (nombres de simbolo y differential
corregidos tras la revision: GetMacAddress, MSGQ_WLAN_RSRC_*, libgps_rsrc.so presente
en la A6000 y la cadena GO mas desarrollada en la A6000, no en la A7S).
"""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A6 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
             "nflasha15_unpacked_unpacked/lib")
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
             "nflasha15_unpacked_unpacked/lib")


def blob(name, base=A6):
    p = base / name
    return p.read_bytes().decode("latin-1") if p.exists() else ""


def mangled(name, base=A6):
    return set(re.findall(r"_Z[A-Za-z0-9_]{4,}", blob(name, base)))


class WlanLibraries(unittest.TestCase):
    def test_all_libraries_present(self):
        for f in ("libWlanAdjust.so", "libWlanControlCommon.so", "libWlanResource.so",
                  "libGOConnectionManager.so", "libInfraDlnaControl.so",
                  "CameraOnDemandSaver.so", "libHapiLib.so"):
            self.assertTrue((A6 / f).exists(), f)

    def test_wlan_adjust(self):
        t = blob("libWlanAdjust.so")
        for s in ("WlanAdjust_Init", "wpa_ctrl", "wlanLoadFirmware", "wlanSetSsid",
                  "wlanSetTxPower", "wlanStartTx", "m_fixed_psk", "SetMacAddress"):
            self.assertIn(s, t, s)

    def test_wlan_control_common(self):
        t = blob("libWlanControlCommon.so")
        for s in ("initializePort", "finalizePort", "setPortToStartWlan",
                  "setPortToStopWlan", "installWlanDrivers", "loadWlanFirmware", "BMI"):
            self.assertIn(s, t, s)

    def test_wlan_resource_mac_address_symbol(self):
        """CORRECCION: el simbolo real es GetMacAddress, no getMacAddress."""
        t = blob("libWlanResource.so")
        self.assertIn("_Z13GetMacAddressPN12WlanResource15ST_MSG_SYNC_REQE", t)
        self.assertNotIn("getMacAddress", t)
        self.assertIn("OSAL_MSGQ_GID_WLAN_RSRC_DBG", t)
        self.assertIn("OSAL_MSGQ_GID_WLAN_RSRC_TEST", t)
        self.assertNotIn("OSAL_MSGQ_GID_WLAN_RSRC_API", t)

    def test_go_connection_manager(self):
        t = blob("libGOConnectionManager.so")
        for s in ("GOConnectionManager", "NetServiceWrapper", "startGO", "stopGO",
                  "StartWpsCmd", "InputPin", "ChangeKey", "authPush",
                  "ProcIdleToAuthReq", "ProcWaitAuthReqToChgKey", "SendReqWpsEvtShowPin"):
            self.assertIn(s, t, s)

    def test_dlna_control(self):
        t = blob("libInfraDlnaControl.so")
        for s in ("dc_statetbl", "dc_evtTbl", "m_lid_Initialize_caller",
                  "m_lid_SetSlideShow_caller", "sendMsgToControlpoint",
                  "sendMsgToMediaServer", "sendMsgToContentHandler"):
            self.assertIn(s, t, s)

    def test_camera_on_demand_saver(self):
        t = blob("CameraOnDemandSaver.so")
        for s in ("/mnt/dcim/100msdcf", "/setting/psd.bin", "%04d_%02X",
                  "cam_ondemand_saver_thread", "CAM_ONDEMAND_SAVER"):
            self.assertIn(s, t, s)

    def test_hapi_library_name(self):
        """El nombre real es libHapiLib.so (no libInfraHapiLib.so)."""
        self.assertTrue((A6 / "libHapiLib.so").exists())
        self.assertFalse((A6 / "libInfraHapiLib.so").exists())


class Netconf(unittest.TestCase):
    def test_netconf_is_a_directory_with_four_files(self):
        d = A6 / "netconf"
        self.assertTrue(d.is_dir())
        self.assertEqual(sorted(p.name for p in d.iterdir() if p.is_file()),
                         ["bss.conf", "dhcpd.conf", "p2p.conf", "pump.conf"])

    def test_bss_conf_wps_identity(self):
        t = (A6 / "netconf" / "bss.conf").read_text()
        for s in ("manufacturer=Sony Corporation", "model_name=SonyImagingDevice",
                  "device_name=WCM-Sample-Device", "device_type=1-0050F204-1",
                  "config_methods=physical_display virtual_push_button",
                  "uuid=12345678-9abc-def0-1234-56789abcdef0",
                  "ctrl_interface=/tmp_network/run/wpa_supplicant",
                  "wps_cred_processing=1"):
            self.assertIn(s, t, s)

    def test_p2p_conf(self):
        t = (A6 / "netconf" / "p2p.conf").read_text()
        for s in ("p2p_go_intent=10", "max_num_sta=1", "p2p_ssid_postfix=-WCM",
                  "device_type=4-0050F204-1",
                  "config_methods=virtual_push_button physical_display keypad"):
            self.assertIn(s, t, s)

    def test_dhcpd_conf(self):
        t = (A6 / "netconf" / "dhcpd.conf").read_text()
        for s in ("subnet 10.0.0.0 netmask 255.255.0.0", "range 10.0.1.1 10.0.1.254",
                  "option routers 10.0.0.1", "default-lease-time 600"):
            self.assertIn(s, t, s)

    def test_netconf_differential(self):
        """3 de los 4 ficheros son identicos; solo dhcpd.conf difiere."""
        for name in ("bss.conf", "p2p.conf", "pump.conf"):
            h6 = hashlib.sha256((A6 / "netconf" / name).read_bytes()).hexdigest()
            h7 = hashlib.sha256((A7 / "netconf" / name).read_bytes()).hexdigest()
            self.assertEqual(h6, h7, name)
        h6 = hashlib.sha256((A6 / "netconf" / "dhcpd.conf").read_bytes()).hexdigest()
        h7 = hashlib.sha256((A7 / "netconf" / "dhcpd.conf").read_bytes()).hexdigest()
        self.assertNotEqual(h6, h7)


class Differential(unittest.TestCase):
    def test_go_scheme_identical_but_a6000_bigger(self):
        m6, m7 = mangled("libGOConnectionManager.so"), mangled("libGOConnectionManager.so", A7)
        self.assertEqual(len(m6), 348)
        self.assertEqual(m6, m7)          # mismo esquema
        self.assertGreater((A6 / "libGOConnectionManager.so").stat().st_size,
                           (A7 / "libGOConnectionManager.so").stat().st_size)

    def test_gps_library_is_present_in_a6000(self):
        """CORRECCION: libgps_rsrc.so SI esta en el firmware de la A6000."""
        self.assertTrue((A6 / "libgps_rsrc.so").exists())
        self.assertTrue((A7 / "libgps_rsrc.so").exists())

    def test_saver_and_dlna_sizes(self):
        self.assertEqual(len(mangled("CameraOnDemandSaver.so")), 28)
        self.assertEqual(len(mangled("CameraOnDemandSaver.so", A7)), 28)
        self.assertGreater(len(mangled("libInfraDlnaControl.so")), 1900)
        self.assertGreater(len(mangled("libInfraDlnaControl.so", A7)), 1900)


if __name__ == "__main__":
    unittest.main()
