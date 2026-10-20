// Ejecuta segmentos puros de copia: no entra en esperas, MMIO ni llamadas.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import ghidra.program.model.lang.RegisterValue;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class EmulateDarwinCaptureBits extends GhidraScript {
    public void run() throws Exception {
        if (getScriptArgs().length != 1) throw new IllegalArgumentException("output JSON required");
        var block = currentProgram.getMemory().getBlock(toAddr(0x4200));
        if (block == null || block.getStart().getOffset() != 0x4200)
            throw new IllegalArgumentException("ROM base 4200 required");
        byte[] source = new byte[Math.toIntExact(block.getSize())];
        currentProgram.getMemory().getBytes(toAddr(0x4200), source);
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(source));
        boolean newer = sha.equals("6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac");
        if (!newer && !sha.equals("5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"))
            throw new IllegalArgumentException("unknown original ROM");
        long state = newer ? 0x200034e4L : 0x200036d8L;
        long start = newer ? 0x194c8L : 0x17fc0L;
        long stop = newer ? 0x1956eL : 0x18056L;
        long stack = 0x20007000L;
        int payloadOffset = newer ? 0 : 4;
        JsonArray examples = new JsonArray();
        JsonArray failures = new JsonArray();
        int passed = 0;
        // Ambos estados previos permiten distinguir copia, preservación y borrado.
        for (int initial : new int[] {0x84, 0xa4}) {
            for (int input = 0; input < 256; input++) {
                EmulatorHelper emu = new EmulatorHelper(currentProgram);
                try {
                    byte[] payload = new byte[36];
                    for (int i = 0; i < 32; i++) payload[payloadOffset + i] = (byte)i;
                    payload[payloadOffset + 0x12] = (byte)input;
                    emu.writeMemory(toAddr(stack), payload);
                    emu.writeMemory(toAddr(state), new byte[0x200]);
                    emu.writeMemoryValue(toAddr(state + 0xd0), 1, initial);
                    emu.writeRegister("pc", start);
                    emu.writeRegister("sp", stack);
                    emu.writeRegister("r4", state);
                    emu.writeRegister("CY", 0);
                    emu.setContextRegister(currentProgram.getRegister("TMode"), BigInteger.ONE);
                    int instructions = 0;
                    boolean ok = true;
                    while (emu.getExecutionAddress().getOffset() != stop && instructions < 128) {
                        emu.setContextRegister(emu.getContextRegister().combineValues(
                            new RegisterValue(currentProgram.getRegister("TMode"), BigInteger.ONE)));
                        if (!emu.step(monitor)) { ok = false; break; }
                        instructions++;
                    }
                    int actual = emu.readMemory(toAddr(state + 0xd0), 1)[0] & 255;
                    int mask = newer ? 0x21 : 1;
                    int expected = (initial & ~mask) | (input & mask);
                    int otherFlag = emu.readMemory(toAddr(state + 0x42), 1)[0] & 255;
                    byte[] tail = emu.readMemory(toAddr(state + 0xd1), 3);
                    boolean valid = ok && emu.getExecutionAddress().getOffset() == stop
                        && actual == expected && otherFlag == (input & 8)
                        && tail[0] == 0x13 && tail[1] == 0x14 && tail[2] == 0x15;
                    JsonObject row = new JsonObject();
                    row.addProperty("initial_d0", initial);
                    row.addProperty("payload_byte_12", input);
                    row.addProperty("actual_d0", actual);
                    row.addProperty("expected_d0", expected);
                    row.addProperty("instructions", instructions);
                    row.addProperty("passed", valid);
                    if (!valid) {
                        row.addProperty("error", emu.getLastError());
                        row.addProperty("pc", emu.getExecutionAddress().toString());
                        failures.add(row);
                    } else passed++;
                    if (input == 0 || input == 1 || input == 0x20 || input == 0x21 || input == 255)
                        examples.add(row);
                } finally { emu.dispose(); }
            }
        }
        JsonObject result = new JsonObject();
        result.addProperty("source_sha256", sha);
        result.addProperty("model", newer ? "A6300 2.01" : "A6000 3.21");
        result.addProperty("start", Long.toHexString(start));
        result.addProperty("stop_before", Long.toHexString(stop));
        result.addProperty("passed_cases", passed);
        result.addProperty("total_cases", 512);
        result.addProperty("passed", passed == 512);
        result.addProperty("limitation", "CPU emulation of an isolated copy segment with synthetic RAM and stack. Stops before calls; no transport, peripheral, sensor, physical timing, patch or camera validation.");
        result.add("examples", examples);
        result.add("failures", failures);
        Files.writeString(Path.of(getScriptArgs()[0]), result + "\n");
        println("Capture bit emulation: " + passed + "/512");
    }
}
