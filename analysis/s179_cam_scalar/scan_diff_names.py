#!/usr/bin/env python3
"""S179 - diferencial de nombres y del bloque de cadenas."""
import json, os
BASE=0x43541000
BINS={
 "A6000":"analysis/rea-independent/input/av-cam.bin",
 "A7S":"firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300":"firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
D={k:open(v,'rb').read() for k,v in BINS.items()}
NAMES=["req_sequence_create_stream","req_tool_get_image_info","req_filter_develop","req_filter_miniature",
"req_filter_face_nr","req_filter_soft_focus","req_image_destruct","req_image_clone","req_image_extract",
"req_image_insert","req_image_parse","req_raw_image_parse","HAPI_Filter_TBOX.cpp","Start_Develop",
"Start_FaceNr","Start_SoftFocus","Start_Miniature","Start_Extract","Start_Insert","Start_Parse",
"Start_RawParse","Start_Clone","Start_CreateStream","CheckMemory","CheckDMMforClone","ShareDMMforClone",
"ConvertAspectForStill","SetSpecialSequence","copyStdYc","ToolGetImageInfo","CS_Command.cpp",
"HAPI Manager","Open Error","AllocNewWait error","Free error","RecordCount","ExposureCount",
"CAP_SINGLE","DMM_HANDLE_YCC_FULL","RAW_FULL","YCC_FULL","sdsYC","SdsYc","NR Level",
]
print(f"{'nombre':34s} A6000   A7S    A6300")
for n in NAMES:
    b=n.encode()
    print(f"{n:34s} {D['A6000'].count(b):5d}  {D['A7S'].count(b):5d}  {D['A6300'].count(b):5d}")
