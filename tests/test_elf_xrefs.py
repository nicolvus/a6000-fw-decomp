import sys

sys.path.insert(0, "scripts")
import elf_string_xrefs as sx  # noqa: E402
import elf_thumb_callers as tc  # noqa: E402

L = "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
b = open(L, "rb").read()
# RecordStill (ObjStillRecorderCore) lo llama una sola vez, desde 0x90bbdc
assert [a for a, _ in tc.callers(b, {0x908AFC})] == [0x90BBDC]
# el error de CapCmp de SeqStillCap tiene una referencia en 0xa3b376
s = b"[CAMUSER]: SeqStillCap) ####### ERROR !!!! CapCmp is NON SUPPORT"
addr = b.find(s)
assert 0xA3B376 in sx.xrefs(b, {addr})[addr]
print("ok")
