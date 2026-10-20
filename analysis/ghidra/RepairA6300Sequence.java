// Reparación puntual de límites inferidos; no borra instrucciones ni bytes.
import ghidra.app.script.GhidraScript;
import java.security.MessageDigest;
import java.util.HexFormat;

public class RepairA6300Sequence extends GhidraScript {
    public void run() throws Exception {
        byte[] original = new byte[13382836];
        currentProgram.getMemory().getBytes(toAddr(0x43541000L), original);
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original));
        if (!digest.equals("6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16"))
            throw new IllegalArgumentException("A6300 original required");
        String repair = getScriptArgs().length == 0 ? "sequence" : getScriptArgs()[0];
        long entryValue = switch (repair) {
            case "sequence" -> 0x438afc0cL;
            case "exposure-interior" -> 0x43717df8L;
            case "capture-prelude" -> 0x438bfcdeL;
            case "flag-consumer" -> 0x438bc9f4L;
            case "timed-command" -> 0x43ba72baL;
            default -> throw new IllegalArgumentException("unknown repair: " + repair);
        };
        var entry = toAddr(entryValue);
        var function = getFunctionAt(entry);
        if (function == null || !function.getName().equals("candidate_" + entry) ||
            (repair.equals("sequence") && !function.getBody().contains(toAddr(0x43bbaf2eL))) ||
            (repair.equals("flag-consumer") && !function.getBody().contains(toAddr(0x43919c04L))) ||
            (repair.equals("timed-command") && !function.getBody().contains(toAddr(0x4380fc78L))))
            throw new IllegalStateException("expected erroneous inferred body not found");
        // La rutina y su thunk tienen prólogos/retornos independientes verificados con LLVM.
        currentProgram.getFunctionManager().removeFunction(entry);
        println("Removed only erroneous inferred function metadata at " + entry);
    }
}
