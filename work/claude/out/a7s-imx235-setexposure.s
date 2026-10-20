436f4168:      	push.w	{r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, lr}
436f416c:      	mov	r4, r0
436f416e:      	ldr.w	r3, [r0, #0x1ac]
436f4172:      	mov	r10, r1
436f4174:      	ldr	r5, [pc, #0x20c]        @ 0x436f4384 
436f4176:      	cmp	r3, #0x11
436f4178:      	add	r5, pc
436f417a:      	bne	0x436f418a  @ imm = #0xc
436f417c:      	add.w	r0, r0, #0x13c
436f4180:      	movs	r1, #0x1
436f4182:      	bl	0x436f5db8  @ imm = #0x1c32
436f4186:      	movs	r0, #0x2
436f4188:      	b	0x436f437c  @ imm = #0x1f0
436f418a:      	ldr	r3, [pc, #0x1fc]        @ 0x436f4388 
436f418c:      	ldrh.w	r8, [r1, #0x4]
436f4190:      	ldr	r1, [r1]
436f4192:      	ldr	r3, [r5, r3]
436f4194:      	ldrh.w	r9, [r10, #0x6]
436f4198:      	ldrb.w	r6, [r10, #0x9]
436f419c:      	ldrb.w	r2, [r3, #0x2d]
436f41a0:      	ldrb.w	r7, [r3, #0x2e]
436f41a4:      	ldrb.w	r3, [r3, #0x2f]
436f41a8:      	cmp	r2, #0xff
436f41aa:      	it	ne
436f41ac:      	movne	r8, r2
436f41ae:      	cmp	r7, #0xff
436f41b0:      	it	eq
436f41b2:      	uxtheq	r7, r1
436f41b4:      	cmp	r3, #0xff
436f41b6:      	it	ne
436f41b8:      	movne	r9, r3
436f41ba:      	ldr	r3, [pc, #0x1d0]        @ 0x436f438c 
436f41bc:      	lsl.w	r8, r8, #0x14
436f41c0:      	lsl.w	r9, r9, #0x14
436f41c4:      	lsr.w	r8, r8, #0x14
436f41c8:      	ldr	r1, [r5, r3]
436f41ca:      	lsr.w	r9, r9, #0x14
436f41ce:      	ldr	r3, [pc, #0x1c0]        @ 0x436f4390 
436f41d0:      	ldr	r2, [r5, r3]
436f41d2:      	mov	r3, r8
436f41d4:      	bl	0x43ad9ec6  @ imm = #0x3e5cee
436f41d8:      	ldr	r3, [pc, #0x1b8]        @ 0x436f4394 
436f41da:      	mov	r0, r4
436f41dc:      	ldr	r1, [r5, r3]
436f41de:      	ldr	r3, [pc, #0x1b8]        @ 0x436f4398 
436f41e0:      	ldr	r2, [r5, r3]
436f41e2:      	mov	r3, r9
436f41e4:      	bl	0x43ad9ec6  @ imm = #0x3e5cde
436f41e8:      	cbnz	r6, 0x436f41f8  @ imm = #0xc
436f41ea:      	cbnz	r7, 0x436f41f8  @ imm = #0xa
436f41ec:      	ldr	r0, [pc, #0x1ac]        @ 0x436f439c 
436f41ee:      	mov	r1, r7
436f41f0:      	adds	r7, #0x1
436f41f2:      	add	r0, pc
436f41f4:      	bl	0x438f7114  @ imm = #0x202f1c
436f41f8:      	ldr	r3, [pc, #0x1a4]        @ 0x436f43a0 
436f41fa:      	lsls	r7, r7, #0x12
436f41fc:      	mov	r0, r4
436f41fe:      	lsrs	r7, r7, #0x12
436f4200:      	ldr	r1, [r5, r3]
436f4202:      	ldr	r3, [pc, #0x1a0]        @ 0x436f43a4 
436f4204:      	ldr	r2, [r5, r3]
436f4206:      	mov	r3, r7
436f4208:      	bl	0x43ad9ec6  @ imm = #0x3e5cba
436f420c:      	add.w	r0, r4, #0x1c
436f4210:      	ldr.w	r1, [r4, #0x1ac]
436f4214:      	bl	0x43ada2a0  @ imm = #0x3e6088
436f4218:      	cbz	r0, 0x436f4236  @ imm = #0x1a
436f421a:      	ldrb	r3, [r4, #0x19]
436f421c:      	cbz	r3, 0x436f422c  @ imm = #0xc
436f421e:      	cmp	r6, #0x4
436f4220:      	beq	0x436f422c  @ imm = #0x8
436f4222:      	ldr	r0, [pc, #0x184]        @ 0x436f43a8 
436f4224:      	add	r0, pc
436f4226:      	bl	0x438f7114  @ imm = #0x202eea
436f422a:      	b	0x436f4236  @ imm = #0x8
436f422c:      	movs	r3, #0x1
436f422e:      	strh.w	r8, [r4, #0x10]
436f4232:      	strh	r7, [r4, #0x12]
436f4234:      	strb	r3, [r4, #0x19]
436f4236:      	ldr	r3, [pc, #0x174]        @ 0x436f43ac 
436f4238:      	ldr	r2, [r5, r3]
436f423a:      	ldr	r3, [pc, #0x174]        @ 0x436f43b0 
436f423c:      	ldr	r3, [r5, r3]
436f423e:      	cmp	r6, #0x4
436f4240:      	bhi	0x436f42fc  @ imm = #0xb8
436f4242:      	tbb	[pc, r6]
436f4246:      	lsrs	r3, r0, #0xc
436f4248:      	movs	r5, #0x5b
436f424a:      	movs	r7, r7
436f424c:      	ldrb	r1, [r3, #0x4]
436f424e:      	bfc	r1, #2, #1
436f4252:      	strb	r1, [r3, #0x4]
436f4254:      	ldrb	r1, [r3, #0x4]
436f4256:      	bfc	r1, #6, #1
436f425a:      	b	0x436f42d2  @ imm = #0x74
436f425c:      	ldrb	r1, [r3, #0x4]
436f425e:      	orr	r1, r1, #0x4
436f4262:      	strb	r1, [r3, #0x4]
436f4264:      	ldrb	r1, [r3, #0x4]
436f4266:      	bfc	r1, #6, #1
436f426a:      	strb	r1, [r3, #0x4]
436f426c:      	ldrb	r1, [r3, #0x4]
436f426e:      	bfc	r1, #4, #1
436f4272:      	strb	r1, [r3, #0x4]
436f4274:      	ldrb	r3, [r2, #0x4]
436f4276:      	orr	r3, r3, #0x8
436f427a:      	strb	r3, [r2, #0x4]
436f427c:      	ldr.w	r0, [r4, #0x2d8]
436f4280:      	ldrb.w	r1, [r4, #0x1b8]
436f4284:      	bl	0x436f2cf4  @ imm = #-0x1594
436f4288:      	ldr	r0, [r0, #0x4]
436f428a:      	lsrs	r0, r0, #0x8
436f428c:      	muls	r0, r7, r0
436f428e:      	b	0x436f42b4  @ imm = #0x22
436f4290:      	ldrb	r1, [r3, #0x4]
436f4292:      	orr	r1, r1, #0x4
436f4296:      	strb	r1, [r3, #0x4]
436f4298:      	ldrb	r1, [r3, #0x4]
436f429a:      	bfc	r1, #6, #1
436f429e:      	strb	r1, [r3, #0x4]
436f42a0:      	ldrb	r1, [r3, #0x4]
436f42a2:      	orr	r1, r1, #0x10
436f42a6:      	strb	r1, [r3, #0x4]
436f42a8:      	ldrb	r3, [r2, #0x4]
436f42aa:      	orr	r3, r3, #0x8
436f42ae:      	strb	r3, [r2, #0x4]
436f42b0:      	ldrh.w	r0, [r10, #0xc]
436f42b4:      	mov.w	r1, #0x3e8
436f42b8:      	bl	0x4355de98  @ imm = #-0x196424
436f42bc:      	adds	r0, #0x1
436f42be:      	strh.w	r0, [r4, #0x3d4]
436f42c2:      	b	0x436f430a  @ imm = #0x44
436f42c4:      	ldrb	r1, [r3, #0x4]
436f42c6:      	bfc	r1, #2, #1
436f42ca:      	strb	r1, [r3, #0x4]
436f42cc:      	ldrb	r1, [r3, #0x4]
436f42ce:      	orr	r1, r1, #0x40
436f42d2:      	strb	r1, [r3, #0x4]
436f42d4:      	ldrb	r1, [r3, #0x4]
436f42d6:      	bfc	r1, #4, #1
436f42da:      	strb	r1, [r3, #0x4]
436f42dc:      	ldrb	r3, [r2, #0x4]
436f42de:      	orr	r3, r3, #0x8
436f42e2:      	strb	r3, [r2, #0x4]
436f42e4:      	ldr.w	r0, [r4, #0x2d8]
436f42e8:      	ldrb.w	r1, [r4, #0x1b8]
436f42ec:      	bl	0x436f2d10  @ imm = #-0x15e0
436f42f0:      	ldrh	r3, [r0]
436f42f2:      	asrs	r3, r3, #0x8
436f42f4:      	adds	r3, #0x1
436f42f6:      	strh.w	r3, [r4, #0x3d4]
436f42fa:      	b	0x436f430a  @ imm = #0xc
436f42fc:      	ldr	r0, [pc, #0xb4]         @ 0x436f43b4 
436f42fe:      	mov	r1, r6
436f4300:      	add	r0, pc
436f4302:      	bl	0x438f7114  @ imm = #0x202e0e
436f4306:      	movs	r0, #0x1
436f4308:      	b	0x436f437c  @ imm = #0x70
436f430a:      	add.w	r5, r4, #0x13c
436f430e:      	movs	r3, #0x0
436f4310:      	mov	r0, r5
436f4312:      	str	r3, [sp, #0x4]
436f4314:      	mov	r1, r8
436f4316:      	mov	r2, r7
436f4318:      	mov	r3, r9
436f431a:      	str	r6, [sp]
436f431c:      	bl	0x43ada042  @ imm = #0x3e5d22
436f4320:      	ldr.w	r3, [r4, #0x198]
436f4324:      	mov	r0, r5
436f4326:      	str	r3, [sp]
436f4328:      	add.w	r3, r4, #0x18c
436f432c:      	ldm	r3, {r1, r2, r3}
436f432e:      	bl	0x43ad9fd6  @ imm = #0x3e5ca4
436f4332:      	mov	r0, r5
436f4334:      	movs	r1, #0x1
436f4336:      	bl	0x436f5db8  @ imm = #0x1a7e
436f433a:      	cbz	r0, 0x436f4358  @ imm = #0x1a
436f433c:      	ldr.w	r1, [r4, #0x1b0]
436f4340:      	ldr.w	r2, [r4, #0x1ac]
436f4344:      	cmp	r1, r2
436f4346:      	beq	0x436f4358  @ imm = #0xe
436f4348:      	ldr	r0, [pc, #0x6c]         @ 0x436f43b8 
436f434a:      	mov	r3, r8
436f434c:      	stm.w	sp, {r7, r9}
436f4350:      	add	r0, pc
436f4352:      	str	r6, [sp, #0x8]
436f4354:      	bl	0x438f7114  @ imm = #0x202dbc
436f4358:      	mov	r0, r5
436f435a:      	movs	r1, #0x8
436f435c:      	bl	0x436f5db8  @ imm = #0x1a58
436f4360:      	cbz	r0, 0x436f437c  @ imm = #0x18
436f4362:      	ldr	r0, [pc, #0x58]         @ 0x436f43bc 
436f4364:      	mov	r3, r8
436f4366:      	ldr.w	r1, [r4, #0x1b0]
436f436a:      	add	r0, pc
436f436c:      	ldr.w	r2, [r4, #0x1ac]
436f4370:      	stm.w	sp, {r7, r9}
436f4374:      	str	r6, [sp, #0x8]
436f4376:      	bl	0x438f7114  @ imm = #0x202d9a
436f437a:      	movs	r0, #0x0
436f437c:      	add	sp, #0x10
436f437e:      	pop.w	{r4, r5, r6, r7, r8, r9, r10, pc}
436f4382:      	nop
436f4384:      	lsls	r4, r0, #0xf
436f4386:      	lsls	r3, r2, #0x2
436f4388:      	ldrsh	r0, [r0, r2]
436f438a:      	movs	r0, r0
436f438c:      	movs	r5, #0xcc
436f438e:      	movs	r0, r0
436f4390:      	ldrb	r4, [r1, #0x1e]
436f4392:      	movs	r0, r0
436f4394:      	adds	r7, #0xc4
436f4396:      	movs	r0, r0
436f4398:      	ldr	r7, [pc, #0xd0]         @ 0x436f446c 
436f439a:      	movs	r0, r0
436f439c:      	strh	r4, [r0, #0x34]
436f439e:      	lsls	r2, r3, #0x1
436f43a0:      	movs	r4, #0x54
436f43a2:      	movs	r0, r0
436f43a4:      	bics	r4, r6
436f43a6:      	movs	r0, r0
436f43a8:      	strh	r0, [r5, #0x32]
436f43aa:      	lsls	r2, r3, #0x1
436f43ac:      	asrs	r4, r4, #0x1c
436f43ae:      	movs	r0, r0
436f43b0:      	cmp	r4, #0xac
436f43b2:      	movs	r0, r0
436f43b4:      	strh	r7, [r6, #0x2c]
436f43b6:      	lsls	r2, r3, #0x1
436f43b8:      	strh	r5, [r0, #0x2c]
436f43ba:      	lsls	r2, r3, #0x1
436f43bc:      	strh	r4, [r2, #0x2e]
436f43be:      	lsls	r2, r3, #0x1
436f43c0:      	ldr.w	r3, [r0, #0x3dc]
436f43c4:      	push	{r4, lr}
436f43c6:      	mov	r4, r0
436f43c8:      	cbz	r3, 0x436f43d0  @ imm = #0x4
436f43ca:      	cmp	r3, #0x1
436f43cc:      	bne	0x436f43e8  @ imm = #0x18
436f43ce:      	b	0x436f43dc  @ imm = #0xa
436f43d0:      	ldr	r0, [pc, #0x18]         @ 0x436f43ec 
436f43d2:      	add	r0, pc
436f43d4:      	pop.w	{r4, lr}
436f43d8:      	b.w	0x438f7114  @ imm = #0x202d38
436f43dc:      	movs	r0, #0xe
436f43de:      	bl	0x43b73044  @ imm = #0x47ec62
436f43e2:      	movs	r3, #0x2
436f43e4:      	str.w	r3, [r4, #0x3dc]
436f43e8:      	pop	{r4, pc}
436f43ea:      	nop
436f43ec:      	strh	r4, [r1, #0x2e]
436f43ee:      	lsls	r2, r3, #0x1
436f43f0:      	ldr.w	r3, [r0, #0x3dc]
436f43f4:      	push	{r4, lr}
436f43f6:      	mov	r4, r0
436f43f8:      	cbz	r3, 0x436f4400  @ imm = #0x4
436f43fa:      	cmp	r3, #0x2
436f43fc:      	bne	0x436f4418  @ imm = #0x18
436f43fe:      	b	0x436f440c  @ imm = #0xa
436f4400:      	ldr	r0, [pc, #0x18]         @ 0x436f441c 
436f4402:      	add	r0, pc
436f4404:      	pop.w	{r4, lr}
436f4408:      	b.w	0x438f7114  @ imm = #0x202d08
436f440c:      	movs	r0, #0xe
436f440e:      	bl	0x43b73014  @ imm = #0x47ec02
436f4412:      	movs	r3, #0x1
436f4414:      	str.w	r3, [r4, #0x3dc]
436f4418:      	pop	{r4, pc}
436f441a:      	nop
436f441c:      	strh	r6, [r6, #0x2c]
436f441e:      	lsls	r2, r3, #0x1
