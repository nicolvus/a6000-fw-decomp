436f3b44:      	push	{r0, r1, r4, r5, r6, lr}
436f3b46:      	mov	r4, r0
436f3b48:      	ldr	r6, [pc, #0x130]        @ 0x436f3c7c 
436f3b4a:      	ldr	r3, [r1]
436f3b4c:      	add	r6, pc
436f3b4e:      	cmp	r3, #0x0
436f3b50:      	beq.w	0x436f3c74  @ imm = #0x120
436f3b54:      	cmp	r3, #0x51
436f3b56:      	bgt.w	0x436f3c74  @ imm = #0x11a
436f3b5a:      	str.w	r3, [r0, #0x1ac]
436f3b5e:      	ldrb	r1, [r1, #0x4]
436f3b60:      	cmp	r1, #0x1
436f3b62:      	strb.w	r1, [r0, #0x2b0]
436f3b66:      	bls	0x436f3b76  @ imm = #0xc
436f3b68:      	ldr	r0, [pc, #0x114]        @ 0x436f3c80 
436f3b6a:      	add	r0, pc
436f3b6c:      	bl	0x438f7114  @ imm = #0x2035a4
436f3b70:      	movs	r3, #0x0
436f3b72:      	strb.w	r3, [r4, #0x2b0]
436f3b76:      	ldr.w	r1, [r4, #0x1ac]
436f3b7a:      	ldr.w	r3, [r4, #0x1b0]
436f3b7e:      	cmp	r3, r1
436f3b80:      	beq	0x436f3bb4  @ imm = #0x30
436f3b82:      	ldr	r2, [pc, #0x100]        @ 0x436f3c84 
436f3b84:      	movs	r3, #0x0
436f3b86:      	strb.w	r3, [r4, #0x3f2]
436f3b8a:      	strb.w	r3, [r4, #0x3e4]
436f3b8e:      	strb.w	r3, [r4, #0x3ea]
436f3b92:      	strb.w	r3, [r4, #0x3f0]
436f3b96:      	strb.w	r3, [r4, #0x400]
436f3b9a:      	strb.w	r3, [r4, #0x401]
436f3b9e:      	str.w	r3, [r4, #0x3f8]
436f3ba2:      	ldr	r2, [r6, r2]
436f3ba4:      	ldrb.w	r0, [r2, #0x99]
436f3ba8:      	cmp	r0, #0x1
436f3baa:      	it	ne
436f3bac:      	ldrne.w	r3, [r2, #0x90]
436f3bb0:      	str.w	r3, [r4, #0x3f4]
436f3bb4:      	ldr	r3, [pc, #0xd0]         @ 0x436f3c88 
436f3bb6:      	add.w	r5, r4, #0x1c
436f3bba:      	mov	r0, r5
436f3bbc:      	ldr	r2, [r6, r3]
436f3bbe:      	movs	r3, #0x22
436f3bc0:      	bl	0x43ada284  @ imm = #0x3e66c0
436f3bc4:      	cmp	r0, #0xff
436f3bc6:      	mov	r1, r0
436f3bc8:      	strb.w	r0, [r4, #0x1b8]
436f3bcc:      	beq	0x436f3c78  @ imm = #0xa8
436f3bce:      	ldr	r3, [r4]
436f3bd0:      	mov	r0, r4
436f3bd2:      	ldr.w	r3, [r3, #0xa0]
436f3bd6:      	blx	r3
436f3bd8:      	mov	r0, r5
436f3bda:      	ldrb.w	r1, [r4, #0x1b8]
436f3bde:      	ldr.w	r2, [r4, #0x2b4]
436f3be2:      	bl	0x436f618c  @ imm = #0x25a6
436f3be6:      	mov	r0, r5
436f3be8:      	ldr.w	r1, [r4, #0x1ac]
436f3bec:      	bl	0x43ada2a0  @ imm = #0x3e66b0
436f3bf0:      	cbz	r0, 0x436f3c2c  @ imm = #0x38
436f3bf2:      	ldrb	r3, [r4, #0x18]
436f3bf4:      	cbz	r3, 0x436f3c00  @ imm = #0x8
436f3bf6:      	ldr	r0, [pc, #0x94]         @ 0x436f3c8c 
436f3bf8:      	add	r0, pc
436f3bfa:      	bl	0x438f7114  @ imm = #0x203516
436f3bfe:      	b	0x436f3c2c  @ imm = #0x2a
436f3c00:      	ldr.w	r3, [r4, #0x1b0]
436f3c04:      	strb	r3, [r4, #0xa]
436f3c06:      	ldr.w	r3, [r4, #0x1ac]
436f3c0a:      	strb	r3, [r4, #0xb]
436f3c0c:      	bl	0x436f27e8  @ imm = #-0x1428
436f3c10:      	add.w	r1, sp, #0x6
436f3c14:      	bl	0x436f2a04  @ imm = #-0x1214
436f3c18:      	cbz	r0, 0x436f3c22  @ imm = #0x6
436f3c1a:      	mov.w	r3, #0xffffffff
436f3c1e:      	strh.w	r3, [sp, #0x6]
436f3c22:      	ldrh.w	r3, [sp, #0x6]
436f3c26:      	strh	r3, [r4, #0x4]
436f3c28:      	movs	r3, #0x1
436f3c2a:      	strb	r3, [r4, #0x18]
436f3c2c:      	add.w	r5, r4, #0x13c
436f3c30:      	movs	r1, #0x1
436f3c32:      	mov	r0, r5
436f3c34:      	bl	0x436f5db8  @ imm = #0x2180
436f3c38:      	cbz	r0, 0x436f3c52  @ imm = #0x16
436f3c3a:      	ldr.w	r1, [r4, #0x1b0]
436f3c3e:      	ldr.w	r2, [r4, #0x1ac]
436f3c42:      	cmp	r1, r2
436f3c44:      	beq	0x436f3c52  @ imm = #0xa
436f3c46:      	ldr	r0, [pc, #0x48]         @ 0x436f3c90 
436f3c48:      	ldrb.w	r3, [r4, #0x2b0]
436f3c4c:      	add	r0, pc
436f3c4e:      	bl	0x438f7114  @ imm = #0x2034c2
436f3c52:      	mov	r0, r5
436f3c54:      	movs	r1, #0x8
436f3c56:      	bl	0x436f5db8  @ imm = #0x215e
436f3c5a:      	cbz	r0, 0x436f3c7a  @ imm = #0x1c
436f3c5c:      	ldr	r0, [pc, #0x34]         @ 0x436f3c94 
436f3c5e:      	ldr.w	r1, [r4, #0x1b0]
436f3c62:      	add	r0, pc
436f3c64:      	ldr.w	r2, [r4, #0x1ac]
436f3c68:      	ldrb.w	r3, [r4, #0x2b0]
436f3c6c:      	bl	0x438f7114  @ imm = #0x2034a4
436f3c70:      	movs	r0, #0x0
436f3c72:      	b	0x436f3c7a  @ imm = #0x4
436f3c74:      	movs	r0, #0x1
436f3c76:      	b	0x436f3c7a  @ imm = #0x0
436f3c78:      	movs	r0, #0x2
436f3c7a:      	pop	{r2, r3, r4, r5, r6, pc}
436f3c7c:      	lsrs	r0, r6, #0x7
436f3c7e:      	lsls	r3, r2, #0x2
436f3c80:      	ldrh	r4, [r5, #0x18]
436f3c82:      	lsls	r2, r3, #0x1
436f3c84:      	lsls	r0, r1, #0xb
436f3c86:      	movs	r0, r0
436f3c88:      	cmp	r4, #0xf0
436f3c8a:      	movs	r0, r0
436f3c8c:      	ldrh	r2, [r6, #0x14]
436f3c8e:      	lsls	r2, r3, #0x1
436f3c90:      	ldrh	r5, [r0, #0x14]
436f3c92:      	lsls	r2, r3, #0x1
436f3c94:      	ldrh	r0, [r7, #0x14]
436f3c96:      	lsls	r2, r3, #0x1
