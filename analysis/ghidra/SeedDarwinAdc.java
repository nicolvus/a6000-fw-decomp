// Definir el lector ADC no descubierto; límites contrastados con LLVM.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.symbol.SourceType;
import java.security.MessageDigest;
import java.util.HexFormat;

public class SeedDarwinAdc extends GhidraScript {
    public void run() throws Exception {
        var block = currentProgram.getMemory().getBlock(toAddr(0x4200));
        if (block == null || !block.getStart().equals(toAddr(0x4200)))
            throw new IllegalArgumentException("Verified Darwin ROM base 4200 required");
        byte[] bytes = new byte[Math.toIntExact(block.getSize())];
        currentProgram.getMemory().getBytes(toAddr(0x4200), bytes);
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        boolean a6300 = sha.equals("6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac");
        if (!a6300 && !sha.equals("5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"))
            throw new IllegalArgumentException("Known Darwin image required");
        var entry = toAddr(a6300 ? 0x1d35c : 0x1b400);
        var end = toAddr(a6300 ? 0x1d38f : 0x1b433);
        var wrapper = toAddr(a6300 ? 0x24da2 : 0x2109c);
        var containing = getFunctionContaining(entry);
        if (getShort(entry) != (short)0xb510 || getShort(end.subtract(1)) != (short)0xbd10 ||
            getShort(wrapper) != (short)0x2008)
            throw new IllegalStateException("Verified ADC and tail-wrapper instructions required");
        if (containing != null) {
            if (!containing.getEntryPoint().equals(wrapper) ||
                containing.getSymbol().getSource() == SourceType.USER_DEFINED)
                throw new IllegalStateException("Only the inferred channel-8 tail wrapper may be separated");
            currentProgram.getFunctionManager().removeFunction(wrapper);
        }
        disassemble(entry);
        currentProgram.getFunctionManager().createFunction("verified_shutter_pi_adc", entry,
            new AddressSet(entry, end), SourceType.ANALYSIS);
        currentProgram.getFunctionManager().createFunction("verified_shutter_pi_channel8", wrapper,
            new AddressSet(wrapper, wrapper.add(5)), SourceType.ANALYSIS);
        println("Separated ADC reader " + entry + " from channel-8 tail wrapper; bytes unchanged");
    }
}
