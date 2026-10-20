43b00d94 add.w r0, r0, #0xd60
43b00d98 movs r2, #0x50
43b00d9a adds r0, #4
43b00d9c b.w #0x43b7f878
43b00da0 add.w r0, r0, #0xda0
43b00da4 movs r2, #0x50
43b00da6 adds r0, #0x14
43b00da8 b.w #0x43b7f878
43b00dac push {r4, r5, lr}
43b00dae mov r5, r1
43b00db0 add.w r4, r0, #0xe40
43b00db4 ldm r5!, {r0, r1, r2, r3}
43b00db6 adds r4, #0x18
43b00db8 stm r4!, {r0, r1, r2, r3}
43b00dba ldr r2, [r5]
43b00dbc str r2, [r4]
43b00dbe pop {r4, r5, pc}
43b00dc0 push {r4, r5, lr}
43b00dc2 mov r5, r1
43b00dc4 add.w r4, r0, #0xe60
43b00dc8 ldm r5!, {r0, r1, r2, r3}
43b00dca adds r4, #0xc
43b00dcc stm r4!, {r0, r1, r2, r3}
43b00dce ldr r2, [r5]
43b00dd0 str r2, [r4]
43b00dd2 pop {r4, r5, pc}
43b00dd4 ldrb.w r3, [r0, #0x57c]
43b00dd8 push {r4, r5, r6, lr}
43b00dda mov r4, r0
43b00ddc cmp r3, #0
43b00dde beq #0x43b00e3e
43b00de0 add.w r6, r0, #0xd60
43b00de4 add.w r5, r4, #0xe40
43b00de8 adds r1, r6, #4
43b00dea bl #0x43b00da0
43b00dee mov r0, r4
43b00df0 add.w r1, r5, #0x18
43b00df4 bl #0x43b00dc0
43b00df8 ldr.w r3, [r4, #0x568]
43b00dfc cmp r3, #1
43b00dfe bne #0x43b00e1e
43b00e00 add.w r1, r4, #0xe00
43b00e04 mov r0, r4
43b00e06 adds r1, #4
43b00e08 bl #0x43b00d94
43b00e0c add.w r0, r4, #0xc40
43b00e10 adds r0, #0xc
43b00e12 mov r1, r6
43b00e14 movs r2, #0x54
43b00e16 pop.w {r4, r5, r6, lr}
43b00e1a b.w #0x43b7f878
43b00e1e cmp r3, #2
43b00e20 bne #0x43b00e3e
43b00e22 adds r5, #0x14
43b00e24 mov r0, r4
43b00e26 add.w r1, r4, #0xe80
43b00e2a add.w r4, r4, #0xcb0
43b00e2e bl #0x43b00dac
43b00e32 ldm r5!, {r0, r1, r2, r3}
43b00e34 stm r4!, {r0, r1, r2, r3}
43b00e36 ldm.w r5, {r0, r1}
43b00e3a stm.w r4, {r0, r1}
43b00e3e pop {r4, r5, r6, pc}
