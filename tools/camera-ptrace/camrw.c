/* camrw — peek/poke de /proc por ptrace para la A6000 (patrón de filmpb1bp: attach + waitpid).
 * uso: camrw PID TID peek ADDR LEN
 *      camrw PID TID poke ADDR bb bb ...
 *      camrw PID TID call VA [a0 a1 a2 a3]     (llama en el hilo detenido y devuelve r0)
 * imprime "0x%08x: bb bb ..." por línea (mismo formato que ptcall peek).
 */
typedef unsigned long ulong;
typedef unsigned short ushort;
static long sc4(long n,long a,long b,long c,long d){
  register long r7 __asm__("r7")=n; register long r0 __asm__("r0")=a;
  register long r1 __asm__("r1")=b; register long r2 __asm__("r2")=c; register long r3 __asm__("r3")=d;
  __asm__ volatile("svc 0":"+r"(r0):"r"(r7),"r"(r1),"r"(r2),"r"(r3):"memory"); return r0;
}
static long s2(long n,long a,long b){return sc4(n,a,b,0,0);}
static long s4(long n,long a,long b,long c,long d){return sc4(n,a,b,c,d);}
#define SYS_write 4
#define SYS_ptrace 26
#define SYS_wait4 114
#define WALL 0x40000000L
#define PT_PEEKTEXT 1
#define PT_POKETEXT 4
#define PT_ATTACH 16
#define PT_GETREGS 12
#define PT_SETREGS 13
#define PT_CONT 7
#define SYS_nanosleep 162
#define UDF 0xde00
#define PT_DETACH 17
static char b[2048], *P;
static char *ps(char *p,const char*s){while(*s)*p++=*s++;return p;}
static char *hx(char*p,ulong v){char t[16];int i=0;*p++='0';*p++='x';if(!v){*p++='0';return p;}
 while(v){t[i++]="0123456789abcdef"[v&15];v>>=4;}while(i)*p++=t[--i];return p;}
static char *h2(char*p,ulong v){*p++="0123456789abcdef"[(v>>4)&15];*p++="0123456789abcdef"[v&15];return p;}
static void out(void){s4(SYS_write,1,(long)b,(long)(P-b),0);}
static long dec(const char*s){long v=0;while(*s>='0'&&*s<='9')v=v*10+(*s++-'0');return v;}
static long ph(const char*s){ulong v=0;if(s[0]=='0'&&(s[1]=='x'||s[1]=='X'))s+=2;
 for(;;){char c=*s;if(c>='0'&&c<='9')v=(v<<4)|(c-'0');else if(c>='a'&&c<='f')v=(v<<4)|(c-'a'+10);
 else if(c>='A'&&c<='F')v=(v<<4)|(c-'A'+10);else break;s++;}return (long)v;}
static int bad(long r){return (ulong)r>0xfffff000UL;}
static int eq(const char*a,const char*c){while(*a&&*c){if(*a++!=*c++)return 0;}return *a==*c;}
static int peekw(long t,ulong a,ulong*out){
  ulong w=0; long r=s4(SYS_ptrace,PT_PEEKTEXT,t,(long)(a&~3UL),(long)&w);
  if(bad(r))return -1; *out=w; return 0;
}
static int pokew(long t,ulong a,ulong v){
  long r=s4(SYS_ptrace,PT_POKETEXT,t,(long)(a&~3UL),(long)v);
  return bad(r)?-1:0;
}
__attribute__((used)) static int main_c(long *sp){
  long argc=sp[0]; char **av=(char**)(sp+1); long pid,st,r; int i;
  if(argc<5){P=ps(b,"uso: camrw PID TID peek|poke ADDR [LEN|bb bb ..] | call VA [a0..a3]\n");out();return 2;}
  pid=dec(av[1]);
  r=s4(SYS_ptrace,PT_ATTACH,pid,0,0);
  if(bad(r)){P=ps(b,"ATTACH falló err=");P=hx(P,(ulong)(-r));*P++='\n';out();return 1;}
  if(bad(s4(SYS_wait4,pid,(long)&st,WALL,0))){P=ps(b,"WAIT falló\n");out();s4(SYS_ptrace,PT_DETACH,pid,0,0);return 1;}
  if(eq(av[3],"peek")){
    ulong a=(ulong)ph(av[4]); long n=(argc>5)?ph(av[5]):4;
    for(i=0;i<n;){
      ulong base=a&~3UL,w=0;
      if(peekw(pid,base,&w)<0){P=ps(b,"PEEK falló err\n");out();break;}
      P=hx(b,(ulong)base);*P++=':';
      for(int k=0;k<4&&i<n;k++,i++){ *P++=' '; P=h2(P,(w>>(8*k))&0xff); }
      *P++='\n';out();
      a+=4;
    }
  } else if(eq(av[3],"poke")){
    ulong a=(ulong)ph(av[4]); long n=argc-5; long k=0;
    for(k=0;k<n;){
      ulong base=a&~3UL,w=0;
      if(peekw(pid,base,&w)<0){P=ps(b,"PEEK falló err\n");out();break;}
      for(int q=0;q<4&&k<n;q++,k++){
        ulong byte=(ulong)ph(av[5+k]); int sh=((int)(a&3)+q)*8;
        w=(w&~(0xffUL<<sh))|((byte&0xff)<<sh); a++;
      }
      if(pokew(pid,base,w)<0){P=ps(b,"POKE falló err\n");out();break;}
    }
    P=ps(b,"poke ok\n");out();
  } else if(eq(av[3],"call")){
    /* llama a VA en el hilo detenido: lr -> UDF 0xde00 en su propio stack; al volver, SIGILL.
     * Restaura los registros originales antes del detach. */
    ulong va=(ulong)ph(av[4]); long regs[18]; int q; ulong stk; ulong w0=0;
    long ret=-1; int ok=0;
    if(bad(s4(SYS_ptrace,PT_GETREGS,pid,0,(long)regs))){P=ps(b,"GETREGS falló\n");out();goto fin;}
    { long orig[18]; for(q=0;q<18;q++) orig[q]=regs[q];
      /* 0x100 de margen: el push de la función no debe pisar el UDF */
      stk=((ulong)regs[13]-0x400)&~7UL;
      if(peekw(pid,stk,&w0)<0){P=ps(b,"PEEK stack falló\n");out();goto fin;}
      if(pokew(pid,stk,(w0&0xffff0000UL)|UDF)<0){P=ps(b,"POKE stack falló\n");out();goto fin;}
      regs[0]=(argc>5)?ph(av[5]):0; regs[1]=(argc>6)?ph(av[6]):0;
      regs[2]=(argc>7)?ph(av[7]):0; regs[3]=(argc>8)?ph(av[8]):0;
      /* lr necesita el bit Thumb, o el retorno al UDF 0xde00 no da SIGILL */
      regs[14]=(long)(stk|1UL); regs[13]=(long)(stk+0x100); regs[15]=(long)(va|1UL);
      if(bad(s4(SYS_ptrace,PT_SETREGS,pid,0,(long)regs))){P=ps(b,"SETREGS falló\n");out();goto fin;}
      s4(SYS_ptrace,PT_CONT,pid,0,0);
      for(q=0;q<200;q++){
        long st2=0, wr;
        { long ts[2]; ts[0]=0; ts[1]=10000000L; s2(SYS_nanosleep,(long)ts,0); }
        wr=s4(SYS_wait4,pid,(long)&st2,WALL|1,0);
        if(wr==pid){
          long rr[18];
          if(!bad(s4(SYS_ptrace,PT_GETREGS,pid,0,(long)rr))){ ret=rr[0];
            P=ps(b,"parada st=");P=hx(P,(ulong)st2);P=ps(P," pc=");P=hx(P,(ulong)rr[15]);
            P=ps(P," lr=");P=hx(P,(ulong)rr[14]);P=ps(P," udf=");P=hx(P,stk);*P++='\n';out();
          }
          ok=1; break;
        }
      }
      pokew(pid,stk,w0);
      for(q=0;q<18;q++) regs[q]=orig[q];
      s4(SYS_ptrace,PT_SETREGS,pid,0,(long)regs);
    }
    P=ps(b,ok?"r0=":"SIN RETORNO (¿bloqueada?) r0=");P=hx(P,(ulong)ret);*P++='\n';out();
  } else { P=ps(b,"modo desconocido\n");out(); }
  goto fin;
 fin:
  s4(SYS_ptrace,PT_DETACH,pid,0,0);
  return 0;
}
__attribute__((naked)) void _start(void){__asm__ volatile("mov r0, sp\n bl main_c\n mov r7, #1\n svc 0");}
