#!/usr/bin/env python3
"""S179 - tabla tbh del dispatcher HAPI (msg id 0x5001..0x5017)."""
import struct
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
tbh=0x4380a728
base=((tbh+4)&~3)
print("base tabla:", hex(base))
# los handlers: los nombres Start_* y req_* estan referenciados cerca de cada handler
names={0x43cb040f:'req_filter_soft_focus',0x43cb0425:'req_raw_image_parse',0x43cb0439:'req_image_insert',
0x43cb044a:'req_image_clone',0x43cb0515:'req_tool_get_image_info',0x43cb0551:'req_filter_develop',
0x43cb069e:'req_image_extract',0x43cb06b0:'req_image_parse',0x43cb06c0:'req_image_destruct',
0x43cb06d3:'req_filter_miniature',0x43cb068b:'req_filter_face_nr',0x43cb04d6:'req_sequence_create_stream',
0x43cb075e:'Start_Develop',0x43cb078a:'Start_FaceNr',0x43cb0797:'Start_SoftFocus',0x43cb07a7:'Start_Miniature',
0x43cb07cc:'Start_Clone',0x43cb07d8:'Start_Parse',0x43cb07e4:'Start_Insert',0x43cb0988:'Start_Extract',
0x43cb09bd:'Start_RawParse',0x43cb09dd:'Start_CreateStream'}
for i in range(23):
    off=struct.unpack_from("<H",B,base-BASE+2*i)[0]
    tgt=base+2*off
    print(f"  msg 0x{0x5001+i:04x}  off=0x{off:04x}  -> 0x{tgt:08x}")
