4383deb0 mov r7, r6
4383deb2 bne #0x4383deba
4383deb4 add.w r7, r4, #0xc8
4383deb8 b #0x4383ded4
4383deba cmp r3, #6
4383debc beq #0x4383dec2
4383debe cmp r3, #0xc
4383dec0 bne #0x4383ded0
4383dec2 add.w r6, r4, #0xdc
4383dec6 ldm r6!, {r0, r1, r2, r3}
4383dec8 stm r7!, {r0, r1, r2, r3}
4383deca mov r3, r7
4383decc ldr r2, [r6]
4383dece b #0x4383dedc
4383ded0 add.w r7, r4, #0xa0
4383ded4 ldm r7!, {r0, r1, r2, r3}
4383ded6 stm r6!, {r0, r1, r2, r3}
4383ded8 mov r3, r6
4383deda ldr r2, [r7]
4383dedc str r2, [r3]
4383dede ldrh r2, [r5]
4383dee0 add.w r6, r4, #0x48
4383dee4 ldrb.w r0, [r5, #0xa0]
4383dee8 mov r1, r4
4383deea ldrb r3, [r5, #2]
4383deec stm.w sp, {r2, r6}
4383def0 add.w r2, r4, #0x20
4383def4 bl #0x4383d3c0
4383def8 ldr.w r3, [pc, #0x414] ; lit=0x75d5f5
4383defc ldrh r2, [r5]
4383defe add.w r1, r4, #0x78
4383df02 add r3, pc
4383df04 ldrb.w r0, [r5, #0xa0]
4383df08 ldrb r3, [r3]
4383df0a str r2, [sp]
4383df0c add.w r2, r4, #0xf0
4383df10 str r2, [sp, #4]
4383df12 add.w r2, r4, #0x98
4383df16 bl #0x4383d3c0
4383df1a movs r0, #0xf0
4383df1c mov r1, r6
4383df1e bl #0x4383b3b0
4383df22 movs r0, #0xf0
4383df24 add.w r1, r4, #0xf8
4383df28 bl #0x4383b458
4383df2c ldrb.w r1, [r5, #0x2d]
4383df30 ldrb.w r2, [r5, #0x2e]
4383df34 ldrh.w r0, [r4, #0x4c]
4383df38 bl #0x4382fd88
4383df3c str.w r0, [r4, #0x334]
4383df40 ldrh.w r0, [r4, #0x4c]
4383df44 bl #0x4382fe08
4383df48 cmp r0, #1
4383df4a bne #0x4383df5e
4383df4c ldrh r0, [r4, #0x14]
4383df4e ldrb.w r1, [r5, #0x2d]
4383df52 ldrb.w r2, [r5, #0x2e]
4383df56 bl #0x4382fd88
4383df5a str.w r0, [r4, #0x334]
4383df5e ldrb.w r3, [r5, #0x13f]
4383df62 cmp r3, #1
4383df64 beq #0x4383df6e
4383df66 ldrb.w r3, [r5, #0x140]
4383df6a cmp r3, #1
4383df6c bne #0x4383df74
4383df6e movs r3, #2
4383df70 str.w r3, [r4, #0x334]
4383df74 ldrh r3, [r5]
4383df76 movw r2, #0x305
4383df7a cmp r3, r2
4383df7c beq #0x4383df84
4383df7e adds r2, #0xe
4383df80 cmp r3, r2
4383df82 bne #0x4383df92
4383df84 ldr.w r2, [r4, #0x334]
4383df88 cmp r2, #1
4383df8a bls #0x4383df92
4383df8c movs r2, #1
4383df8e str.w r2, [r4, #0x334]
4383df92 movw r2, #0x306
4383df96 cmp r3, r2
4383df98 bne #0x4383dfb6
4383df9a ldr r3, [pc, #0x334] ; lit=0x5f74
4383df9c ldr r1, [sp, #0x10]
4383df9e ldr.w r2, [r4, #0x334]
4383dfa2 ldr r3, [r1, r3]
4383dfa4 ldrb.w r3, [r3, #0x104]
4383dfa8 cmp r3, #0
4383dfaa it eq
4383dfac moveq r3, #1
4383dfae cmp r3, r2
4383dfb0 it lo
4383dfb2 strlo.w r3, [r4, #0x334]
4383dfb6 add.w r8, r4, #0xfc
4383dfba mov r7, r4
4383dfbc str r4, [sp, #0x4c]
4383dfbe movs r6, #0
4383dfc0 mov r4, r8
4383dfc2 mov r8, r7
4383dfc4 ldrb.w r3, [r5, #0x13f]
4383dfc8 cmp r3, #1
4383dfca beq #0x4383dfd4
4383dfcc ldrb.w r3, [r5, #0x140]
4383dfd0 cmp r3, #1
4383dfd2 bne #0x4383dfe4
4383dfd4 bl #0x436f05b0
4383dfd8 cbnz r0, #0x4383dfe4
4383dfda ldr.w r3, [r5, #0x164]
4383dfde str.w r3, [r7, #0x338]
4383dfe2 b #0x4383dfee
4383dfe4 ldrh r0, [r4]
4383dfe6 bl #0x4382fa94
4383dfea str.w r0, [r7, #0x338]
4383dfee add.w r2, r6, #0xd6
4383dff2 add.w r3, r6, #0xd2
4383dff6 add.w r1, r5, #0x60
4383dffa adds r4, #2
4383dffc add.w r2, r8, r2, lsl #2
4383e000 str r2, [sp]
4383e002 add.w r2, r6, #0xda
4383e006 add.w r3, r8, r3, lsl #2
4383e00a adds r6, #1
4383e00c add.w r2, r8, r2, lsl #2
4383e010 str r2, [sp, #4]
4383e012 ldr.w r0, [r7, #0x338]
4383e016 adds r7, #4
4383e018 ldr r2, [r5, #0x5c]
4383e01a bl #0x4383d4d0
4383e01e cmp r6, #4
4383e020 bne #0x4383dfc4
