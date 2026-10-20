struct FdatHeader { char magic[8]; u32 crc; char ver[4]; u32 f0; u32 f1; };
FdatHeader h @ 0x00;
#include <std/io.pat>
std::print("magic={} ver={} f0={:#x} f1={:#x}", h.magic, h.ver, h.f0, h.f1);
