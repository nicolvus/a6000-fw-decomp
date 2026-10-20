436d6f6c:      	ldr.w	r3, [r0, #0x170]
436d6f70:      	push.w	{r4, r5, r6, r7, r8, r9, r10, r11, lr}
436d6f74:      	cmp	r3, #0x11
436d6f76:      	ldr.w	r8, [pc, #0x320]        @ 0x436d7298 
436d6f7a:      	sub	sp, #0x44
436d6f7c:      	mov	r4, r0
436d6f7e:      	mov	r10, r1
436d6f80:      	add	r8, pc
436d6f82:      	bne	0x436d6faa  @ imm = #0x24
436d6f84:      	add.w	r0, r0, #0xfc
436d6f88:      	movs	r1, #0x1
436d6f8a:      	bl	0x436d9f70  @ imm = #0x2fe2
436d6f8e:      	cmp	r0, #0x0
436d6f90:      	beq.w	0x436d728a  @ imm = #0x2f6
436d6f94:      	ldr.w	r3, [r4, #0x170]
436d6f98:      	movs	r0, #0xbc
436d6f9a:      	movs	r1, #0x0
436d6f9c:      	movs	r2, #0x3
436d6f9e:      	str	r3, [sp]
436d6fa0:      	ldr	r3, [pc, #0x2f8]        @ 0x436d729c 
436d6fa2:      	add	r3, pc
436d6fa4:      	bl	0x436d6738  @ imm = #-0x870
436d6fa8:      	b	0x436d728a  @ imm = #0x2de
436d6faa:      	ldrh	r6, [r1, #0x4]
436d6fac:      	ldr	r3, [pc, #0x2f0]        @ 0x436d72a0 
436d6fae:      	ldrh	r5, [r1]
436d6fb0:      	ldrh	r7, [r1, #0x6]
436d6fb2:      	uxtb.w	r11, r6
436d6fb6:      	ldrb.w	r9, [r1, #0x9]
436d6fba:      	str.w	r6, [r0, #0x3a8]
436d6fbe:      	ldr.w	lr, [r8, r3]
436d6fc2:      	ldr	r3, [pc, #0x2e0]        @ 0x436d72a4 
436d6fc4:      	ldr.w	r0, [r8, r3]
436d6fc8:      	ldr	r3, [pc, #0x2dc]        @ 0x436d72a8 
436d6fca:      	ldr.w	r12, [r8, r3]
436d6fce:      	ldr	r3, [pc, #0x2dc]        @ 0x436d72ac 
436d6fd0:      	ldr.w	r2, [r8, r3]
436d6fd4:      	ldr	r3, [pc, #0x2d8]        @ 0x436d72b0 
436d6fd6:      	ldr.w	r3, [r8, r3]
436d6fda:      	str	r3, [sp, #0x30]
436d6fdc:      	ldr	r3, [pc, #0x2d4]        @ 0x436d72b4 
436d6fde:      	ldr.w	r3, [r8, r3]
436d6fe2:      	strb.w	r11, [lr, #0x2]
436d6fe6:      	asr.w	lr, r6, #0x8
436d6fea:      	and	lr, lr, #0xf
436d6fee:      	str.w	lr, [sp, #0x2c]
436d6ff2:      	ldr	r1, [sp, #0x2c]
436d6ff4:      	ldrb.w	lr, [r0, #0x2]
436d6ff8:      	bfi	lr, r1, #0, #4
436d6ffc:      	strb.w	lr, [r0, #0x2]
436d7000:      	asrs	r0, r5, #0x8
436d7002:      	uxtb.w	lr, r5
436d7006:      	and	r0, r0, #0x3f
436d700a:      	strb.w	lr, [r12, #0x2]
436d700e:      	str	r0, [sp, #0x24]
436d7010:      	asrs	r1, r7, #0x8
436d7012:      	ldrb.w	r12, [r2, #0x2]
436d7016:      	and	r1, r1, #0xf
436d701a:      	bfi	r12, r0, #0, #6
436d701e:      	strb.w	r12, [r2, #0x2]
436d7022:      	ldr	r0, [sp, #0x30]
436d7024:      	uxtb	r2, r7
436d7026:      	strb	r2, [r0, #0x2]
436d7028:      	str	r1, [sp, #0x30]
436d702a:      	ldr.w	r12, [sp, #0x30]
436d702e:      	ldrb	r1, [r3, #0x2]
436d7030:      	bfi	r1, r12, #0, #4
436d7034:      	strb	r1, [r3, #0x2]
436d7036:      	ldr	r3, [pc, #0x280]        @ 0x436d72b8 
436d7038:      	ldr.w	r3, [r8, r3]
436d703c:      	ldrb.w	r3, [r3, #0x7f]
436d7040:      	cmp	r3, #0xff
436d7042:      	beq	0x436d70a6  @ imm = #0x60
436d7044:      	ldr	r3, [pc, #0x274]        @ 0x436d72bc 
436d7046:      	ldr.w	r3, [r8, r3]
436d704a:      	str	r3, [sp, #0x34]
436d704c:      	ldr	r3, [pc, #0x270]        @ 0x436d72c0 
436d704e:      	ldr	r0, [sp, #0x34]
436d7050:      	ldr.w	r12, [r8, r3]
436d7054:      	ldr	r3, [pc, #0x26c]        @ 0x436d72c4 
436d7056:      	ldr.w	r3, [r8, r3]
436d705a:      	str	r3, [sp, #0x38]
436d705c:      	ldr	r3, [pc, #0x268]        @ 0x436d72c8 
436d705e:      	ldr.w	r1, [r8, r3]
436d7062:      	ldr	r3, [pc, #0x268]        @ 0x436d72cc 
436d7064:      	ldr.w	r3, [r8, r3]
436d7068:      	str	r3, [sp, #0x3c]
436d706a:      	ldr	r3, [pc, #0x264]        @ 0x436d72d0 
436d706c:      	ldr.w	r3, [r8, r3]
436d7070:      	strb.w	r11, [r0, #0x2]
436d7074:      	ldr	r0, [sp, #0x2c]
436d7076:      	ldrb.w	r11, [r12, #0x2]
436d707a:      	bfi	r11, r0, #0, #4
436d707e:      	strb.w	r11, [r12, #0x2]
436d7082:      	ldr	r0, [sp, #0x38]
436d7084:      	strb.w	lr, [r0, #0x2]
436d7088:      	ldr.w	r12, [sp, #0x24]
436d708c:      	ldrb.w	lr, [r1, #0x2]
436d7090:      	bfi	lr, r12, #0, #6
436d7094:      	strb.w	lr, [r1, #0x2]
436d7098:      	ldr	r0, [sp, #0x3c]
436d709a:      	strb	r2, [r0, #0x2]
436d709c:      	ldr	r1, [sp, #0x30]
436d709e:      	ldrb	r2, [r3, #0x2]
436d70a0:      	bfi	r2, r1, #0, #4
436d70a4:      	strb	r2, [r3, #0x2]
436d70a6:      	add.w	r0, r4, #0x18
436d70aa:      	ldr.w	r1, [r4, #0x170]
436d70ae:      	bl	0x436d8a74  @ imm = #0x19c2
436d70b2:      	cbz	r0, 0x436d70b8  @ imm = #0x2
436d70b4:      	strh	r6, [r4, #0x10]
436d70b6:      	strh	r5, [r4, #0x12]
436d70b8:      	ldr	r3, [pc, #0x218]        @ 0x436d72d4 
436d70ba:      	ldr.w	r3, [r8, r3]
436d70be:      	cmp.w	r9, #0x4
436d70c2:      	bhi.w	0x436d728e  @ imm = #0x1c8
436d70c6:      	tbb	[pc, r9]
436d70ca:      	lsrs	r3, r0, #0xc
436d70cc:      	ldr	r5, [r4, r0]
436d70ce:      	lsls	r2, r6, #0x1
436d70d0:      	ldrb	r2, [r3, #0x2]
436d70d2:      	bfc	r2, #2, #1
436d70d6:      	strb	r2, [r3, #0x2]
436d70d8:      	ldrb	r2, [r3, #0x2]
436d70da:      	bfc	r2, #7, #1
436d70de:      	b	0x436d71bc  @ imm = #0xda
436d70e0:      	ldrb	r2, [r3, #0x2]
436d70e2:      	orr	r2, r2, #0x4
436d70e6:      	strb	r2, [r3, #0x2]
436d70e8:      	ldrb	r2, [r3, #0x2]
436d70ea:      	orr	r2, r2, #0x80
436d70ee:      	strb	r2, [r3, #0x2]
436d70f0:      	ldrb	r2, [r3, #0x2]
436d70f2:      	bfc	r2, #4, #1
436d70f6:      	strb	r2, [r3, #0x2]
436d70f8:      	ldrb	r2, [r3, #0x2]
436d70fa:      	orr	r2, r2, #0x40
436d70fe:      	strb	r2, [r3, #0x2]
436d7100:      	ldr.w	r0, [r4, #0x294]
436d7104:      	ldrb.w	r1, [r4, #0x17c]
436d7108:      	bl	0x436d6f34  @ imm = #-0x1d8
436d710c:      	ldr	r0, [r0, #0x4]
436d710e:      	lsrs	r0, r0, #0x8
436d7110:      	muls	r0, r5, r0
436d7112:      	b	0x436d719e  @ imm = #0x88
436d7114:      	ldrb	r2, [r3, #0x2]
436d7116:      	orr	r2, r2, #0x4
436d711a:      	strb	r2, [r3, #0x2]
436d711c:      	ldrb	r2, [r3, #0x2]
436d711e:      	orr	r2, r2, #0x80
436d7122:      	strb	r2, [r3, #0x2]
436d7124:      	ldrb	r2, [r3, #0x2]
436d7126:      	orr	r2, r2, #0x10
436d712a:      	strb	r2, [r3, #0x2]
436d712c:      	ldrb	r2, [r3, #0x2]
436d712e:      	bfc	r2, #6, #1
436d7132:      	strb	r2, [r3, #0x2]
436d7134:      	ldr	r3, [pc, #0x1a0]        @ 0x436d72d8 
436d7136:      	ldrb.w	r2, [r10, #0x8]
436d713a:      	ldr.w	r3, [r8, r3]
436d713e:      	strb	r2, [r3, #0x2]
436d7140:      	ldr	r3, [pc, #0x198]        @ 0x436d72dc 
436d7142:      	ldrb.w	r2, [r10, #0x14]
436d7146:      	ldr.w	r3, [r8, r3]
436d714a:      	strb	r2, [r3, #0x2]
436d714c:      	ldrb.w	r1, [r4, #0x17c]
436d7150:      	ldr.w	r0, [r4, #0x294]
436d7154:      	bl	0x436d6f34  @ imm = #-0x224
436d7158:      	mov.w	r1, #0x3e8
436d715c:      	ldr	r0, [r0, #0x4]
436d715e:      	lsrs	r0, r0, #0x8
436d7160:      	bl	0x4355faf0  @ imm = #-0x177674
436d7164:      	ldrb.w	r3, [r10, #0x14]
436d7168:      	movw	r2, #0x26aa
436d716c:      	adds	r3, #0x1
436d716e:      	muls	r3, r2, r3
436d7170:      	muls	r0, r5, r0
436d7172:      	adds	r0, #0x1
436d7174:      	add.w	r3, r0, r3, lsr #16
436d7178:      	b	0x436d71e0  @ imm = #0x64
436d717a:      	ldrb	r2, [r3, #0x2]
436d717c:      	orr	r2, r2, #0x4
436d7180:      	strb	r2, [r3, #0x2]
436d7182:      	ldrb	r2, [r3, #0x2]
436d7184:      	orr	r2, r2, #0x80
436d7188:      	strb	r2, [r3, #0x2]
436d718a:      	ldrb	r2, [r3, #0x2]
436d718c:      	orr	r2, r2, #0x10
436d7190:      	strb	r2, [r3, #0x2]
436d7192:      	ldrb	r2, [r3, #0x2]
436d7194:      	orr	r2, r2, #0x40
436d7198:      	strb	r2, [r3, #0x2]
436d719a:      	ldrh.w	r0, [r10, #0x10]
436d719e:      	mov.w	r1, #0x3e8
436d71a2:      	bl	0x4355faf0  @ imm = #-0x1776b6
436d71a6:      	adds	r0, #0x1
436d71a8:      	strh.w	r0, [r4, #0x3a0]
436d71ac:      	b	0x436d71e4  @ imm = #0x34
436d71ae:      	ldrb	r2, [r3, #0x2]
436d71b0:      	bfc	r2, #2, #1
436d71b4:      	strb	r2, [r3, #0x2]
436d71b6:      	ldrb	r2, [r3, #0x2]
436d71b8:      	orr	r2, r2, #0x80
436d71bc:      	strb	r2, [r3, #0x2]
436d71be:      	ldrb	r2, [r3, #0x2]
436d71c0:      	bfc	r2, #4, #1
436d71c4:      	strb	r2, [r3, #0x2]
436d71c6:      	ldrb	r2, [r3, #0x2]
436d71c8:      	orr	r2, r2, #0x40
436d71cc:      	strb	r2, [r3, #0x2]
436d71ce:      	ldr.w	r0, [r4, #0x294]
436d71d2:      	ldrb.w	r1, [r4, #0x17c]
436d71d6:      	bl	0x436d6f50  @ imm = #-0x28a
436d71da:      	ldrh	r3, [r0]
436d71dc:      	asrs	r3, r3, #0x8
436d71de:      	adds	r3, #0x1
