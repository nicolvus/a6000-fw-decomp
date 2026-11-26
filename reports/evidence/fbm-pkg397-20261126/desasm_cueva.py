import hashlib
from pathlib import Path

f = Path('build/cfw_fbm31_pkg397/libmpr.so').read_bytes()
try:
    import capstone
except ImportError:
    print('capstone no disponible; bytes crudos')
    print(f[0x93B000:0x93B052].hex())
    raise SystemExit
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
print('gancho 0x7126E6 (4 B):', f[0x7126E6:0x7126EA].hex(), ' (fábrica: a2f79bf0)')
print('vecino 0x7126EA (no se toca):', f[0x7126EA:0x7126EE].hex())
print()
for i in md.disasm(f[0x93B000:0x93B052], 0x93B000):
    print(f'{i.address:08x}  {i.bytes.hex():<8} {i.mnemonic:<8} {i.op_str}')
print()
print('sha256 del binario empaquetado:', hashlib.sha256(f).hexdigest())
