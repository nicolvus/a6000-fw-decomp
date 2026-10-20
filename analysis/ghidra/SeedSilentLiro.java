// Entradas demostradas por la tabla del receptor; no asigna semántica al hardware.
import ghidra.app.script.GhidraScript;
import java.math.BigInteger;

public class SeedSilentLiro extends GhidraScript {
    public void run() throws Exception {
        for (long row = 0x43fff30cL; row < 0x43fffd5cL; row += 12) {
            long pointer = Integer.toUnsignedLong(getInt(toAddr(row + 4)));
            if ((pointer & 1) == 0 || pointer < 0x43541000L || pointer >= 0x44026da4L)
                throw new IllegalArgumentException("invalid Thumb table entry");
            var address = toAddr(pointer & ~1L);
            if (getInstructionAt(address) == null) {
                currentProgram.getProgramContext().setValue(
                    currentProgram.getRegister("TMode"), address, address, BigInteger.ONE);
                disassemble(address);
            }
            if (getFunctionAt(address) == null) createFunction(address, "dispatch_" + address);
        }
        // La consulta inicial en 43792fb4 era una instrucción interior, no una entrada.
        var interior = getFunctionAt(toAddr(0x43792fb4L));
        if (interior != null && interior.getName().equals("candidate_43792fb4"))
            removeFunction(interior);
        println("Seeded 220 dispatch rows; original bytes unchanged");
    }
}
