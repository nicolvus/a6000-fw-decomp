// Sembrar únicamente vectores Cortex-M compatibles con el original conocido.
import ghidra.app.script.GhidraScript;
import java.security.MessageDigest;
import java.util.HexFormat;

public class SeedDarwinVectors extends GhidraScript {
    public void run() throws Exception {
        var base = toAddr(0x4200);
        var block = currentProgram.getMemory().getBlock(base);
        if (block == null || !block.getStart().equals(base))
            throw new IllegalArgumentException("Verified Darwin ROM base 4200 required");
        int size = Math.toIntExact(block.getSize());
        byte[] bytes = new byte[size];
        currentProgram.getMemory().getBytes(base, bytes);
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        if (!sha.equals("5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4") &&
            !sha.equals("6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac"))
            throw new IllegalArgumentException("Unknown Darwin image");
        if (!currentProgram.getLanguageID().toString().equals("ARM:LE:32:Cortex"))
            throw new IllegalArgumentException("Cortex-M language required");
        block.setWrite(false);
        for (int offset = 4; offset < 0x100; offset += 4) {
            long pointer = Integer.toUnsignedLong(getInt(base.add(offset)));
            if (pointer == 0 || pointer == 0xffffffffL) continue;
            if ((pointer & 1) == 0 || pointer < 0x4200 || pointer >= 0x4200 + size)
                throw new IllegalStateException("Unverified vector at " + offset);
            var entry = toAddr(pointer & ~1L);
            if (getFunctionAt(entry) == null) {
                // El lenguaje Cortex fija Thumb; no sobrescribir contexto ya analizado.
                disassemble(entry);
                createFunction(entry, "vector_" + Integer.toHexString(offset / 4));
            }
        }
        println("Verified Darwin SHA256 " + sha + "; vectors 1..63 seeded; bytes unchanged");
    }
}
