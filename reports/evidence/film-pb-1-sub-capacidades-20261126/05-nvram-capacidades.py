"""Lee los ids EEPROM que alimentan MprCtrl::GetSupportContentTypes (libmprctrl 0x11DDC)
y MprCtrl::GetTvSystem (0x11D74) en los volcados backup_flash.bin del proyecto."""
import sys, glob, os
sys.path.insert(0, '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/references/pmca')
from pmca.backup import BackupFile

IDS = [(0x3C0368, 0x9), (0x3C036C, 0x10), (0x3C036D, 0x4),
       (0x3C0409, 0x100), (0x3C044D, 0x200), (0x3C0408, 0x80)]

for f in sorted(glob.glob(sys.argv[1] + '/*/backup_flash.bin')):
    p = {i: bytes(pr.data) for i, pr in BackupFile(open(f, 'rb')).listProperties()}
    vals, mask = [], 0
    for cid, bit in IDS:
        v = p.get(cid)
        v = int.from_bytes(v, 'little') if v else None
        vals.append(v)
        if v == 1:
            mask |= bit
    model = (p.get(0x3E0005) or b'').split(b'\0')[0].decode('latin1')
    tv = p.get(0x010704FD)
    tv = int.from_bytes(tv, 'little') if tv else None
    print('%-38s mask=0x%03X eep=%s model=%r eep_tv=%s -> TvSystem=%s'
          % (os.path.basename(os.path.dirname(f)), mask, vals, model, tv,
             {0: 1, 1: 0}.get(tv, 0)))

