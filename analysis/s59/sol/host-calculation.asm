438110be ldr.w r0, [r4, #0x1f8]
438110c2 cmp r0, #0
438110c4 beq #0x4381112a
438110c6 ldr.w sl, [r7, #8]
438110ca ldr.w r6, [r4, #0x1fc]
438110ce ldrh.w sb, [sl, #0xcc]
438110d2 cmp r6, #9
438110d4 ite ne
438110d6 movne r6, r0
438110d8 moveq r6, #1
438110da cmp.w sb, #1
438110de bhi #0x438110e8
438110e0 ldrb.w r0, [sl, #0x14e]
438110e4 muls r0, r6, r0
438110e6 b #0x438110f0
438110e8 mov r0, r6
438110ea mov r1, sb
438110ec bl #0x4355faf0
438110f0 subs r0, #1
438110f2 uxth r0, r0
438110f4 tst.w r0, #0x8000
438110f8 beq #0x4381112a
438110fa str r6, [sp]
438110fc movs r0, #3
438110fe ldrb.w r3, [sl, #0x14e]
43811102 movs r1, #9
43811104 movs r2, #1
43811106 str.w sb, [sp, #8]
4381110a str r3, [sp, #4]
4381110c ldr r3, [pc, #0x150] ; lit=0x4a00c0
4381110e add r3, pc
43811110 bl #0x4380fcac
43811114 ldr r3, [r7, #8]
43811116 ldr r0, [pc, #0x14c] ; lit=0x4a00c8
43811118 mov r1, r6
4381111a add r0, pc
4381111c ldrb.w r2, [r3, #0x14e]
43811120 ldrh.w r3, [r3, #0xcc]
43811124 bl #0x43902718
43811128 movs r0, #0
4381112a ldrb.w r3, [r8, #0x1d]
4381112e tst.w r3, #1
43811132 beq #0x43811146
43811134 movs r3, #9
43811136 strh.w r0, [sp, #0x1c]
4381113a str r3, [sp, #0x18]
4381113c movs r3, #0
4381113e strh.w r3, [sp, #0x1e]
43811142 strb.w r3, [sp, #0x20]
43811146 ldrh.w r3, [sp, #0x1c]
4381114a uxth r7, r0
4381114c cmp r3, r7
4381114e beq #0x4381118e
