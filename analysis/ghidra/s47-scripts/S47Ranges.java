import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

/** Listados Thumb temporales y bytes, incluyendo regiones sin funciones. */
public class S47Ranges extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();
  var dis=ghidra.program.disassemble.Disassembler.getDisassembler(currentProgram,false,false,false,monitor,null);
  var mode=new ghidra.program.model.lang.RegisterValue(currentProgram.getRegister("TMode"),java.math.BigInteger.ONE).getBaseRegisterValue();
  for(int n=1;n<getScriptArgs().length;n+=2) {
   long start=Long.decode(getScriptArgs()[n]),end=Long.decode(getScriptArgs()[n+1]);
   JsonObject row=new JsonObject();row.addProperty("start",Long.toHexString(start));JsonArray nodes=new JsonArray();
   for(long a=start;a<end;) {
    byte[] b=new byte[16];currentProgram.getMemory().getBytes(toAddr(a),b);
    var block=dis.pseudoDisassembleBlock(new ghidra.program.model.mem.ByteMemBufferImpl(toAddr(a),b,false),mode,1);
    var ins=block.getInstructionAt(toAddr(a));if(ins==null)throw new Exception("Invalid Thumb "+Long.toHexString(a));
    JsonObject node=new JsonObject();node.addProperty("address",ins.getAddress().toString());
    node.addProperty("instruction",ins.toString());node.addProperty("bytes",HexFormat.of().formatHex(Arrays.copyOf(b,ins.getLength())));
    nodes.add(node);a+=ins.getLength();
   }
   row.add("nodes",nodes);rows.add(row);
  }
  Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
