// Exportación estática: las anotaciones temporales se revierten y nunca se guardan.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.math.BigInteger;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.HexFormat;
import com.google.gson.*;

public class S32Export extends GhidraScript {
    private JsonArray refs(Address a) {
        JsonArray out = new JsonArray();
        for (var r : getReferencesTo(a)) {
            JsonObject x = new JsonObject();
            x.addProperty("from", r.getFromAddress().toString());
            x.addProperty("type", r.getReferenceType().toString());
            Function f = getFunctionContaining(r.getFromAddress());
            if (f != null) x.addProperty("function", f.getEntryPoint().toString());
            out.add(x);
        }
        return out;
    }
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Path blob = Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin");
        byte[] original = Files.readAllBytes(blob);
        String expected = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9";
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original));
        byte[] loaded = new byte[original.length];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), loaded);
        if (!digest.equals(expected) || !java.util.Arrays.equals(original, loaded))
            throw new IllegalStateException("blob/project bytes mismatch");
        JsonObject out = new JsonObject();
        out.addProperty("source_sha256", digest);
        out.addProperty("base", "43541000");
        out.addProperty("method", "persistent project -readOnly -noanalysis; temporary function definitions rolled back; no firmware execution");
        JsonArray rows = new JsonArray();
        int tx = currentProgram.startTransaction("S32 temporary export metadata");
        DecompInterface dec = new DecompInterface();
        try {
            // Igual que S31, plegar solo pools de código/PIC, nunca los datos RAM.
            var mem = currentProgram.getMemory();
            var block = mem.getBlock(toAddr(0x43541000L));
            if (block.contains(toAddr(0x43bc0000L))) mem.split(block, toAddr(0x43bc0000L));
            block.setWrite(false);
            DecompileOptions options = new DecompileOptions();
            options.setRespectReadOnly(true);
            dec.setOptions(options);
            dec.openProgram(currentProgram);
            for (int n = 1; n < args.length; n++) {
                boolean dataOnly = args[n].startsWith("@");
                Address a = toAddr(Long.decode(dataOnly ? args[n].substring(1) : args[n]));
                JsonObject row = new JsonObject();
                row.addProperty("query", a.toString());
                row.add("references_before", refs(a));
                JsonArray pointers = new JsonArray();
                long target = a.getOffset();
                for (int i = 0; i + 3 < original.length; i++) {
                    long v = (original[i]&255L)|((original[i+1]&255L)<<8)|((original[i+2]&255L)<<16)|((original[i+3]&255L)<<24);
                    if (v == target || v == (target|1)) pointers.add(Long.toHexString(0x43541000L+i));
                }
                row.add("raw_pointer_hits_unaligned", pointers);
                if (dataOnly) {
                    byte[] b = new byte[128];
                    try { mem.getBytes(a,b); row.addProperty("bytes_128",HexFormat.of().formatHex(b)); }
                    catch (Exception e) { row.addProperty("read_error",e.toString()); }
                    rows.add(row);
                    continue;
                }
                Function f = getFunctionContaining(a);
                if (f == null) {
                    if (getInstructionAt(a) == null) {
                        currentProgram.getProgramContext().setValue(currentProgram.getRegister("TMode"), a, a, BigInteger.ONE);
                        disassemble(a);
                    }
                    f = createFunction(a, "s32_candidate_"+a);
                }
                if (f != null) {
                    row.addProperty("entry", f.getEntryPoint().toString());
                    row.addProperty("body", f.getBody().toString());
                    DecompileResults result = dec.decompileFunction(f, 120, monitor);
                    row.addProperty("status", result.decompileCompleted()?"decompiled":"failed");
                    row.addProperty("error", result.getErrorMessage());
                    if (result.getDecompiledFunction()!=null) row.addProperty("pseudo_code",result.getDecompiledFunction().getC());
                    JsonArray listing = new JsonArray();
                    JsonArray calls = new JsonArray();
                    var it = currentProgram.getListing().getInstructions(f.getBody(), true);
                    while (it.hasNext()) {
                        var ins = it.next();
                        listing.add(ins.getAddress()+" "+ins.toString());
                        for (var r : ins.getReferencesFrom()) {
                            if (r.getReferenceType().isCall() || r.getReferenceType().isJump()) {
                                JsonObject c = new JsonObject();
                                c.addProperty("site",ins.getAddress().toString());
                                c.addProperty("target",r.getToAddress().toString());
                                c.addProperty("type",r.getReferenceType().toString());
                                calls.add(c);
                            }
                        }
                    }
                    row.add("listing", listing);
                    row.add("calls_and_jumps", calls);
                } else row.addProperty("status","no_function");
                row.add("references_after",refs(a));
                rows.add(row);
            }
        } finally {
            dec.dispose();
            currentProgram.endTransaction(tx, false);
        }
        out.add("functions", rows);
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(out)+"\n");
        StringBuilder c = new StringBuilder("/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */\n");
        for (var r : rows) {
            var x=r.getAsJsonObject();
            c.append("\n/* query ").append(x.get("query")).append(" */\n");
            if (x.has("pseudo_code")) c.append(x.get("pseudo_code").getAsString());
        }
        Files.writeString(Path.of(args[0].replace(".json",".c")),c.toString());
        println("S32 exported "+rows.size()+" queries; SHA-256 verified; transaction rolled back");
    }
}
