4383d4d0 push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}
4383d4d4 mov r5, r0
4383d4d6 mov r4, r1
4383d4d8 mov sb, r3
4383d4da ldr.w r8, [sp, #0x28]
4383d4de ldr r7, [sp, #0x2c]
4383d4e0 ldrh r6, [r1, #0x2c]
4383d4e2 cbz r2, #0x4383d4fa
4383d4e4 mov r0, r2
4383d4e6 mov.w r1, #0x3e8
4383d4ea bl #0x4355faf0
4383d4ee mov r1, r0
4383d4f0 ldr r0, [pc, #0xc0] ; lit=0xf424000
4383d4f2 bl #0x4355faf0
4383d4f6 mov sl, r0
4383d4f8 b #0x4383d4fe
4383d4fa movw sl, #0xde3
4383d4fe ldrb r3, [r4, #0x16]
4383d500 mov r0, r5
4383d502 ldr r1, [r4, #0x20]
4383d504 muls r1, r3, r1
4383d506 bl #0x43b0791e
4383d50a str.w r0, [sb]
4383d50e ldrb r3, [r4, #0x16]
4383d510 ldr r2, [r4, #0x20]
4383d512 ldr.w fp, [r4, #8]
4383d516 mul sb, r2, r3
4383d51a mls r5, r0, sb, r5
4383d51e ldr.w sb, [r4]
4383d522 cbz r6, #0x4383d542
4383d524 mul r0, r6, sl
4383d528 mov.w r1, #0x3e8
4383d52c bl #0x4355faf0
4383d530 add.w r3, r0, fp
4383d534 cmp sb, r3
4383d536 bls #0x4383d550
4383d538 rsb sb, fp, sb
4383d53c rsb sb, r0, sb
4383d540 b #0x4383d554
4383d542 rsb r0, fp, sb
4383d546 mov r1, r6
4383d548 bl #0x43b03ac6
4383d54c mov sb, r0
4383d54e b #0x4383d554
4383d550 mov.w sb, #0
4383d554 cmp r5, sb
4383d556 bls #0x4383d564
4383d558 rsb r0, sb, r5
4383d55c ldr r1, [r4, #4]
4383d55e bl #0x43b084e8
4383d562 b #0x4383d566
4383d564 movs r0, #0
4383d566 ldrh r2, [r4, #0x10]
4383d568 ldrh r3, [r4, #0x14]
4383d56a subs r1, r2, r3
4383d56c cmp r1, r0
4383d56e itee lo
4383d570 strlo.w r3, [r8]
4383d574 rsbhs r2, r0, r2
4383d578 strhs.w r2, [r8]
4383d57c cbz r6, #0x4383d5ac
4383d57e ldr r3, [r4, #4]
4383d580 mls r5, r3, r0, r5
4383d584 cmp r5, sb
4383d586 bls #0x4383d59e
4383d588 rsb r5, sb, r5
4383d58c mov.w r0, #0x3e8
4383d590 mov r1, sl
4383d592 muls r0, r5, r0
4383d594 bl #0x43b084e8
4383d598 cmp r6, r0
4383d59a blo #0x4383d5a4
4383d59c b #0x4383d5a0
4383d59e movs r0, #0
4383d5a0 subs r6, r6, r0
4383d5a2 b #0x4383d5ac
4383d5a4 movs r3, #0
4383d5a6 str r3, [r7]
4383d5a8 pop.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}
4383d5ac str r6, [r7]
4383d5ae pop.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}
4383d5b2 nop 
4383d5b4 ands r0, r0
4383d5b6 lsrs r2, r0, #0x1d
