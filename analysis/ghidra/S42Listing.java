import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;

/** Desensambla temporalmente rangos Thumb, sin guardar instrucciones. */
public class S42Listing extends GhidraScript {
 public void run() throws Exception {
  JsonArray rows=new JsonArray();var dis=ghidra.program.disassemble.Disassembler.getDisassembler(currentProgram,false,false,false,monitor,null);
  var mode=new ghidra.program.model.lang.RegisterValue(currentProgram.getRegister("TMode"),java.math.BigInteger.ONE).getBaseRegisterValue();
  for(int i=1;i<getScriptArgs().length;i+=2){long a=Long.decode(getScriptArgs()[i]),end=Long.decode(getScriptArgs()[i+1]);JsonObject row=new JsonObject();row.addProperty("start",Long.toHexString(a));JsonArray ls=new JsonArray();
   while(a<end){byte[] b=new byte[16];currentProgram.getMemory().getBytes(toAddr(a),b);var block=dis.pseudoDisassembleBlock(new ghidra.program.model.mem.ByteMemBufferImpl(toAddr(a),b,false),mode,1);var ins=block.getInstructionAt(toAddr(a));if(ins==null)throw new Exception("Invalid instruction "+Long.toHexString(a));ls.add(ins.getAddress()+" "+ins);a+=ins.getLength();}
   row.add("temporary_listing",ls);rows.add(row);
  }Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(rows));
 }
}
