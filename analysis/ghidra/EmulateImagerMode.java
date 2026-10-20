// Ejecuta solo el selector puro de modo; no emula sensor, MMIO ni cámara.
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

public class EmulateImagerMode extends GhidraScript {
    public void run() throws Exception {
        if (getScriptArgs().length != 1) throw new IllegalArgumentException("output JSON required");
        int size = Math.toIntExact(currentProgram.getMemory().getSize());
        byte[] original = new byte[size];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), original);
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original));
        boolean a6300 = digest.equals("6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16");
        if (!a6300 && !digest.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))
            throw new IllegalArgumentException("unknown original firmware");
        long entry = a6300 ? 0x438be684L : 0x437f7f98L;
        java.util.Set<Long> epilogues = a6300
            ? java.util.Set.of(0x438be6aaL, 0x438be6baL, 0x438be6ccL,
                              0x438be6d0L, 0x438be6d4L, 0x438be6d8L)
            : java.util.Set.of(0x437f7fe0L);
        // Modo, recorte, tipo Silent, resultado esperado. Sin ramas de diagnóstico.
        int[][] cases = {
            {1, 0, 0, 0x0b}, {1, 1, 0, 0x35}, {1, 2, 0, 0x17},
            {1, 0, 2, a6300 ? 0x4e : 0x0b},
            {1, 1, 2, a6300 ? 0x4f : 0x35},
            {5, 0, 2, 0x0c}, {0x1b, 0, 2, 0x1b}
        };
        JsonArray results = new JsonArray();
        boolean passed = true;
        for (int[] test : cases) {
            EmulatorHelper emu = new EmulatorHelper(currentProgram);
            JsonObject row = new JsonObject();
            try {
                emu.writeRegister("pc", entry);
                emu.setContextRegister(currentProgram.getRegister("TMode"), BigInteger.ONE);
                emu.writeRegister("cpsr", 0x20);
                emu.writeRegister("TB", 1);
                emu.writeRegister("sp", 0x45001000L);
                emu.writeRegister("lr", 0x45002001L);
                emu.writeMemory(toAddr(0x45000f00L), new byte[256]);
                emu.writeRegister("r0", test[0]);
                emu.writeRegister("r1", test[1]);
                emu.writeRegister("r2", test[2]);
                int steps = 0;
                boolean ok = true;
                JsonArray trace = new JsonArray();
                while (!epilogues.contains(emu.getExecutionAddress().getOffset()) && steps < 512) {
                    // Ambas funciones son Thumb puro; fijar contexto también tras cada salto.
                    emu.setContextRegister(emu.getContextRegister().combineValues(
                        new RegisterValue(currentProgram.getRegister("TMode"), BigInteger.ONE)));
                    if (steps < 32) trace.add(emu.getExecutionAddress().toString());
                    if (!emu.step(monitor)) { ok = false; break; }
                    steps++;
                }
                long actual = emu.readRegister("r0").longValue() & 0xffffffffL;
                boolean reachedEpilogue = epilogues.contains(emu.getExecutionAddress().getOffset());
                long savedReturn = reachedEpilogue
                    ? emu.readStackValue(a6300 ? 4 : 20, 4, false).longValue() & 0xffffffffL : 0;
                boolean valid = ok && reachedEpilogue && savedReturn == 0x45002001L && actual == test[3];
                row.addProperty("mode_input", test[0]);
                row.addProperty("crop_input", test[1]);
                row.addProperty("silent_type_r2", test[2]);
                row.addProperty("expected", test[3]);
                row.addProperty("actual", actual);
                row.addProperty("instructions", steps);
                row.addProperty("reached_epilogue", reachedEpilogue);
                row.addProperty("saved_return_address", Long.toHexString(savedReturn));
                row.addProperty("passed", valid);
                row.addProperty("error", emu.getLastError());
                row.add("instruction_addresses", trace);
                passed &= valid;
            } finally { emu.dispose(); }
            results.add(row);
        }
        JsonObject output = new JsonObject();
        output.addProperty("source_sha256", digest);
        output.addProperty("entry", Long.toHexString(entry));
        output.addProperty("method", "Ghidra ARM instruction emulation; Thumb explicitly selected at each step; maximum 512 instructions per case");
        output.addProperty("limitation", "Stops before verified POP-to-PC epilogues; checks R0 and saved return address. No return-ISA transition, sensor, peripheral, timing, firmware patch or camera validation");
        output.addProperty("passed", passed);
        output.add("cases", results);
        Files.writeString(Path.of(getScriptArgs()[0]), output + "\n");
        println("Mode emulation passed=" + passed);
    }
}
