"""S93 — El bus de mensajes OSAL del userland: grupos (GID) y colas (LID).

Anclas verificadas contra las .so del userland fw3.21.
Ver analysis/s93_osal_bus/osal_message_bus.md
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
              "nflasha15_unpacked_unpacked/lib")


def blob_text(name):
    return (LIB / name).read_bytes().decode("latin-1")


def all_so():
    for f in sorted(LIB.glob("*.so")):
        yield f.name, f.read_bytes().decode("latin-1")


class OsalBus(unittest.TestCase):
    def test_gid_and_lid_inventories(self):
        gid, lid = set(), set()
        for _, t in all_so():
            gid |= set(re.findall(r"OSAL_MSGQ_GID_[A-Z0-9_]+", t))
            lid |= set(re.findall(r"OSAL_MSGQ_LID_[A-Z0-9_]+", t))
        self.assertEqual(len(gid), 16)
        self.assertEqual(len(lid), 13)
        for name in ("OSAL_MSGQ_GID_DETECT_FACE", "OSAL_MSGQ_GID_DMM_CTRL",
                     "OSAL_MSGQ_GID_SADRIVER", "OSAL_MSGQ_GID_TASK_ADC",
                     "OSAL_MSGQ_GID_WLAN_RSRC_DBG", "OSAL_MSGQ_GID_NETSERVICE_SCALAR_API",
                     "OSAL_MSGQ_GID_INFRA_VDF", "OSAL_MSGQ_GID_APP_VIEW_SCALAR",
                     "OSAL_MSGQ_GID_GPS_GET", "OSAL_MSGQ_GID_CAMERA_RAW_DEVELOP",
                     "OSAL_MSGQ_GID_NET_BACKUP_SERVER", "OSAL_MSGQ_GID_AIRPLANE_MODE_SCALAR_API",
                     "OSAL_MSGQ_GID_AIRPLANE_MODE_TEST", "OSAL_MSGQ_GID_NETSERVICE_SYNC_EMU",
                     "OSAL_MSGQ_GID_NETSERVICE_TEST"):
            self.assertIn(name, gid, name)
        for name in ("OSAL_MSGQ_LID_DLNACONTROL_CP", "OSAL_MSGQ_LID_DLNACONTROL_MAIN",
                     "OSAL_MSGQ_LID_DLNACONTROL_MEDIASVR", "OSAL_MSGQ_LID_MDNS_CONTROL_MAIN",
                     "OSAL_MSGQ_LID_WEBAPI_MAIN", "OSAL_MSGQ_LID_NETSERVICE_SYNC_REQ",
                     "OSAL_MSGQ_LID_NETSERVICE_ASYNC_REQ", "OSAL_MSGQ_LID_WLAN_RSRC_API",
                     "OSAL_MSGQ_LID_R_HOTSHOE_API", "OSAL_MSGQ_LID_GPS_GET",
                     "OSAL_MSGQ_LID_AIRPLANE_MODE_API", "OSAL_MSGQ_LID_NETFUNCTIONMGR_MAIN",
                     "OSAL_MSGQ_LID_NET_BACKUP_SERVER_INFRA_NET_SERVICE_CMP"):
            self.assertIn(name, lid, name)

    def test_detect_face_queue_lives_in_bizfw(self):
        t = blob_text("libBizFw.so")
        self.assertIn("OSAL_MSGQ_GID_DETECT_FACE", t)
        self.assertIn("OSAL_MSGQ_GID_SADRIVER", t)
        self.assertIn("OSAL_MSGQ_GID_DMM_CTRL", t)

    def test_hotshoe_and_wlan_queues(self):
        self.assertIn("OSAL_MSGQ_GID_TASK_ADC", blob_text("libRsrcHotshoe.so"))
        self.assertIn("OSAL_MSGQ_LID_R_HOTSHOE_API", blob_text("libRsrcHotshoe.so"))
        self.assertIn("OSAL_MSGQ_GID_WLAN_RSRC_DBG", blob_text("libWlanResource.so"))
        self.assertIn("OSAL_MSGQ_LID_WLAN_RSRC_API", blob_text("libWlanResource.so"))

    def test_dlna_and_mdns_and_webapi(self):
        t = blob_text("libInfraDlnaControl.so")
        for n in ("OSAL_MSGQ_LID_DLNACONTROL_CP", "OSAL_MSGQ_LID_DLNACONTROL_MAIN",
                  "OSAL_MSGQ_LID_DLNACONTROL_MEDIASVR"):
            self.assertIn(n, t, n)
        self.assertIn("OSAL_MSGQ_LID_MDNS_CONTROL_MAIN", blob_text("libInfraMDnsControl.so"))
        self.assertIn("OSAL_MSGQ_LID_WEBAPI_MAIN", blob_text("libInfraWebApi.so"))

    def test_gps_support_is_present_in_a6000(self):
        """La A6000 incluye GPS en el firmware (lo hereda de la A7S) aunque no tenga hardware."""
        self.assertIn("OSAL_MSGQ_GID_GPS_GET", blob_text("libmpr.so"))
        self.assertTrue((LIB / "libgps_rsrc.so").exists())

    def test_view_and_display_bridges_in_libobj(self):
        t = blob_text("libObj.so")
        for n in ("OSAL_MSGQ_GID_APP_VIEW_SCALAR", "OSAL_MSGQ_GID_INFRA_VDF",
                  "OSAL_MSGQ_GID_CAMERA_RAW_DEVELOP", "OSAL_MSGQ_GID_NET_BACKUP_SERVER"):
            self.assertIn(n, t, n)


if __name__ == "__main__":
    unittest.main()
