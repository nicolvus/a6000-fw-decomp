// S53: siembra vectores, tabla de despacho 0x4300 y punteros Thumb a prólogos push. Bytes intactos.
import ghidra.app.script.GhidraScript;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Set;

public class S53SeedDarwin extends GhidraScript {
    static final Set<String> KNOWN = Set.of(
        "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4",
        "241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf",
        "6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac");

    void seed(long p, String name, long size) throws Exception {
        if ((p & 1) == 0 || p < 0x4200 || p >= 0x4200 + size) return;
        var a = toAddr(p & ~1L);
        if (getFunctionAt(a) == null && getInstructionContaining(a) == null) {
            disassemble(a);
        }
        if (getFunctionAt(a) == null) createFunction(a, null);
    }

    public void run() throws Exception {
        var base = toAddr(0x4200);
        var block = currentProgram.getMemory().getBlock(base);
        if (block == null || !block.getStart().equals(base)) throw new IllegalArgumentException("base 4200");
        long size = block.getSize();
        byte[] b = new byte[(int) size];
        currentProgram.getMemory().getBytes(base, b);
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));
        if (!KNOWN.contains(sha)) throw new IllegalArgumentException("ROM desconocida " + sha);
        block.setWrite(false);
        for (int off = 4; off < 0x100; off += 4) seed(Integer.toUnsignedLong(getInt(base.add(off))), null, size);
        for (int k = 0; k < 64; k++) seed(Integer.toUnsignedLong(getInt(toAddr(0x4300 + 4 * k))), null, size);
        int n = 0;
        for (int off = 0; off + 4 <= size; off += 4) {
            long p = Integer.toUnsignedLong(getInt(base.add(off)));
            if ((p & 1) == 0 || p < 0x4200 || p >= 0x4200 + size - 2) continue;
            int o = (int) ((p & ~1L) - 0x4200);
            int hw = (b[o] & 0xff) | ((b[o + 1] & 0xff) << 8);
            boolean push16 = (hw & 0xff00) == 0xb500 || (hw & 0xff00) == 0xb400;
            boolean push32 = hw == 0xe92d;
            if (push16 || push32) { seed(p, null, size); n++; }
        }
        println("S53 seed sha=" + sha + " candidatos=" + n);
    }
}
