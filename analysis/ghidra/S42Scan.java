import ghidra.app.script.GhidraScript;
import com.google.gson.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Inventario estático: no modifica memoria, funciones ni tipos. */
public class S42Scan extends GhidraScript {
 public void run() throws Exception {
  byte[] b=Files.readAllBytes(Path.of("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"));
  String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));
  if(!sha.equals("b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"))throw new Exception("SHA mismatch");
  byte[] loaded=new byte[b.length];currentProgram.getMemory().getBytes(toAddr(0x43541000L),loaded);if(!Arrays.equals(b,loaded))throw new Exception("Memory mismatch");
  JsonObject root=new JsonObject();root.addProperty("sha256",sha);JsonArray hits=new JsonArray();
  long[] targets={0x436d6f6cL,0x436d6f6dL,0x43bf37c4L,0x43bf344eL,0x43bf3736L,0x43bf341eL};
  for(int i=0;i<b.length-4;i++) {
   long v=(b[i]&255L)|((b[i+1]&255L)<<8)|((b[i+2]&255L)<<16)|((b[i+3]&255L)<<24);long a=0x43541000L+i;
   for(long t:targets)if(v==t||((v+a)&0xffffffffL)==t){JsonObject h=new JsonObject();h.addProperty("site",Long.toHexString(a));h.addProperty("target",Long.toHexString(t));h.addProperty("kind",v==t?"absolute":"relative_to_word");hits.add(h);}
  }
  root.add("pointer_candidates",hits);JsonArray fields=new JsonArray();var it=currentProgram.getListing().getInstructions(true);
  while(it.hasNext()){var ins=it.next();String s=ins.toString();long a=ins.getAddress().getOffset();
   if(s.contains("#0x5cc]")||((a>=0x43840000L&&a<0x43850000L||s.startsWith("strb"))&&(s.contains("#0x36]")||s.contains("#0x37]")))) {
    JsonObject h=new JsonObject();h.addProperty("instruction",ins.getAddress()+" "+s);var f=getFunctionContaining(ins.getAddress());if(f!=null)h.addProperty("function",f.getEntryPoint().toString());fields.add(h);
   }
  }root.add("field_candidates",fields);Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(root));
 }
}
