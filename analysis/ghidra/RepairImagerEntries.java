// Entradas obtenidas de la vtable, más fiables que buscar un prólogo PUSH.
import ghidra.app.script.GhidraScript;
import java.math.BigInteger;

public class RepairImagerEntries extends GhidraScript {
    public void run() throws Exception {
        long[][] entries = {{0x436d67ecL, 0x436d67e4L}, {0x436d74bcL, 0x436d74b8L}};
        for (long[] pair : entries) {
            var old = getFunctionAt(toAddr(pair[0]));
            if (old != null && old.getName().startsWith("candidate_")) removeFunction(old);
            var address = toAddr(pair[1]);
            if (getInstructionAt(address) == null) {
                currentProgram.getProgramContext().setValue(
                    currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
                disassemble(address);
            }
            if (getFunctionAt(address) == null) createFunction(address, "vtable_" + address);
        }
        println("Repaired two entries using IMX210 vtable slots 2c/34");
    }
}
