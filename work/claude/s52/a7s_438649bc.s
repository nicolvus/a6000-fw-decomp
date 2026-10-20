438649bc:      	push.w	{r4, r5, r6, r7, r8, lr}
438649c0:      	mov	r7, r2
438649c2:      	ldrh.w	r2, [r2, #0x4c4]
438649c6:      	mov	r5, r0
438649c8:      	ldr	r4, [pc, #0x1e4]        @ 0x43864bb0 
438649ca:      	mov	r6, r1
438649cc:      	tst.w	r2, #0x60
438649d0:      	add	r4, pc
438649d2:      	bne	0x438649da  @ imm = #0x4
438649d4:      	ands	r1, r2, #0x80
438649d8:      	beq	0x438649f0  @ imm = #0x14
438649da:      	tst.w	r2, #0x20
438649de:      	beq	0x438649e8  @ imm = #0x6
438649e0:      	ldr	r2, [pc, #0x1d0]        @ 0x43864bb4 
438649e2:      	movs	r1, #0x5
438649e4:      	add	r2, pc
438649e6:      	b	0x43864a48  @ imm = #0x5e
438649e8:      	ldr	r2, [pc, #0x1cc]        @ 0x43864bb8 
438649ea:      	movs	r1, #0x1
438649ec:      	add	r2, pc
438649ee:      	b	0x43864a48  @ imm = #0x56
438649f0:      	ldr.w	r2, [r7, #0x404]
438649f4:      	cmp	r2, #0x2
438649f6:      	bne	0x438649fe  @ imm = #0x4
438649f8:      	ldr	r2, [pc, #0x1c0]        @ 0x43864bbc 
438649fa:      	add	r2, pc
438649fc:      	b	0x43864a48  @ imm = #0x48
438649fe:      	ldr.w	r1, [r7, #0x424]
43864a02:      	cmp	r1, #0x1
43864a04:      	bne	0x43864a42  @ imm = #0x3a
43864a06:      	ldrb	r2, [r3, #0x2]
43864a08:      	cbnz	r2, 0x43864a24  @ imm = #0x18
43864a0a:      	ldr	r2, [pc, #0x1b4]        @ 0x43864bc0 
43864a0c:      	ldrh.w	r0, [r6, #0x166]
43864a10:      	ldr	r2, [r4, r2]
43864a12:      	ldrh	r2, [r2]
43864a14:      	cmp	r0, r2
43864a16:      	bls	0x43864a1e  @ imm = #0x4
43864a18:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc4 
43864a1a:      	add	r2, pc
43864a1c:      	b	0x43864a48  @ imm = #0x28
43864a1e:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc8 
43864a20:      	add	r2, pc
43864a22:      	b	0x43864a46  @ imm = #0x20
43864a24:      	cmp	r2, #0x1
43864a26:      	bne	0x43864a3c  @ imm = #0x12
43864a28:      	ldrb.w	r1, [r7, #0x38c]
43864a2c:      	cmp	r1, #0x1
43864a2e:      	bne	0x43864a36  @ imm = #0x4
43864a30:      	ldr	r2, [pc, #0x198]        @ 0x43864bcc 
43864a32:      	add	r2, pc
43864a34:      	b	0x43864a48  @ imm = #0x10
43864a36:      	ldr	r2, [pc, #0x198]        @ 0x43864bd0 
43864a38:      	add	r2, pc
43864a3a:      	b	0x43864a46  @ imm = #0x8
43864a3c:      	ldr	r2, [pc, #0x194]        @ 0x43864bd4 
43864a3e:      	add	r2, pc
43864a40:      	b	0x43864a48  @ imm = #0x4
43864a42:      	ldr	r2, [pc, #0x194]        @ 0x43864bd8 
43864a44:      	add	r2, pc
43864a46:      	movs	r1, #0x3
43864a48:      	str	r1, [r2, #0x5c]
43864a4a:      	ldr	r2, [pc, #0x190]        @ 0x43864bdc 
43864a4c:      	ldr	r1, [r4, r2]
43864a4e:      	mov	r8, r1
43864a50:      	ldrb.w	r2, [r1, #0x7e]
43864a54:      	cmp	r2, #0x0
43864a56:      	beq	0x43864abe  @ imm = #0x64
43864a58:      	cmp	r2, #0x1
43864a5a:      	bne	0x43864a64  @ imm = #0x6
43864a5c:      	ldr	r2, [pc, #0x180]        @ 0x43864be0 
43864a5e:      	movs	r1, #0x0
43864a60:      	add	r2, pc
43864a62:      	b	0x43864abc  @ imm = #0x56
43864a64:      	cmp	r2, #0x2
43864a66:      	bne	0x43864a6e  @ imm = #0x4
43864a68:      	ldr	r2, [pc, #0x178]        @ 0x43864be4 
43864a6a:      	add	r2, pc
43864a6c:      	b	0x43864aba  @ imm = #0x4a
43864a6e:      	cmp	r2, #0x3
43864a70:      	bne	0x43864a7a  @ imm = #0x6
43864a72:      	ldr	r2, [pc, #0x174]        @ 0x43864be8 
43864a74:      	movs	r1, #0x2
43864a76:      	add	r2, pc
43864a78:      	b	0x43864abc  @ imm = #0x40
43864a7a:      	cmp	r2, #0x4
43864a7c:      	bne	0x43864a86  @ imm = #0x6
43864a7e:      	ldr	r2, [pc, #0x16c]        @ 0x43864bec 
43864a80:      	movs	r1, #0x3
43864a82:      	add	r2, pc
43864a84:      	b	0x43864abc  @ imm = #0x34
43864a86:      	cmp	r2, #0x5
43864a88:      	bne	0x43864a92  @ imm = #0x6
43864a8a:      	ldr	r2, [pc, #0x164]        @ 0x43864bf0 
43864a8c:      	movs	r1, #0x4
43864a8e:      	add	r2, pc
43864a90:      	b	0x43864abc  @ imm = #0x28
43864a92:      	cmp	r2, #0x6
43864a94:      	bne	0x43864a9e  @ imm = #0x6
43864a96:      	ldr	r2, [pc, #0x15c]        @ 0x43864bf4 
43864a98:      	movs	r1, #0x5
43864a9a:      	add	r2, pc
43864a9c:      	b	0x43864abc  @ imm = #0x1c
43864a9e:      	cmp	r2, #0x7
43864aa0:      	bne	0x43864aaa  @ imm = #0x6
43864aa2:      	ldr	r2, [pc, #0x154]        @ 0x43864bf8 
43864aa4:      	movs	r1, #0x6
43864aa6:      	add	r2, pc
43864aa8:      	b	0x43864abc  @ imm = #0x10
43864aaa:      	cmp	r2, #0x8
43864aac:      	bne	0x43864ab6  @ imm = #0x6
43864aae:      	ldr	r2, [pc, #0x14c]        @ 0x43864bfc 
43864ab0:      	movs	r1, #0x7
43864ab2:      	add	r2, pc
43864ab4:      	b	0x43864abc  @ imm = #0x4
43864ab6:      	ldr	r2, [pc, #0x148]        @ 0x43864c00 
43864ab8:      	add	r2, pc
43864aba:      	movs	r1, #0x1
43864abc:      	str	r1, [r2, #0x5c]
43864abe:      	ldrb	r0, [r3, #0x2]
43864ac0:      	cmp	r0, #0x1
43864ac2:      	bne	0x43864aca  @ imm = #0x4
43864ac4:      	ldrb.w	r3, [r7, #0x38c]
43864ac8:      	cbz	r3, 0x43864acc  @ imm = #0x0
43864aca:      	movs	r0, #0x0
43864acc:      	bl	0x438642e4  @ imm = #-0x7ec
43864ad0:      	ldr.w	r3, [r7, #0x404]
43864ad4:      	cmp	r3, #0x2
43864ad6:      	bne	0x43864ae0  @ imm = #0x6
43864ad8:      	ldr	r3, [pc, #0x128]        @ 0x43864c04 
43864ada:      	movs	r2, #0x0
43864adc:      	add	r3, pc
43864ade:      	b	0x43864b00  @ imm = #0x1e
43864ae0:      	ldr.w	r2, [r7, #0x424]
43864ae4:      	cmp	r2, #0x1
43864ae6:      	bne	0x43864aee  @ imm = #0x4
43864ae8:      	ldr	r3, [pc, #0x11c]        @ 0x43864c08 
43864aea:      	add	r3, pc
43864aec:      	b	0x43864b00  @ imm = #0x10
43864aee:      	ldr	r3, [pc, #0x11c]        @ 0x43864c0c 
43864af0:      	movs	r2, #0x0
43864af2:      	add	r3, pc
43864af4:      	strb.w	r2, [r3, #0x60]
43864af8:      	ldrb.w	r2, [r8, #0x10f]
43864afc:      	cmp	r2, #0x1
43864afe:      	bne	0x43864b04  @ imm = #0x2
43864b00:      	strb.w	r2, [r3, #0x60]
43864b04:      	ldrb.w	r2, [r8, #0xf9]
43864b08:      	cmp	r2, #0x1
43864b0a:      	bne	0x43864b22  @ imm = #0x14
43864b0c:      	ldr	r3, [pc, #0x100]        @ 0x43864c10 
43864b0e:      	add	r3, pc
43864b10:      	ldr	r1, [r3, #0x5c]
43864b12:      	cmp	r1, #0x3
43864b14:      	bne	0x43864b22  @ imm = #0xa
43864b16:      	ldrh.w	r0, [r6, #0x166]
43864b1a:      	ldrh.w	r1, [r8, #0xfc]
43864b1e:      	cmp	r0, r1
43864b20:      	bhs	0x43864b28  @ imm = #0x4
43864b22:      	ldr	r3, [pc, #0xf0]         @ 0x43864c14 
43864b24:      	movs	r2, #0x0
43864b26:      	add	r3, pc
43864b28:      	strb.w	r2, [r3, #0x61]
43864b2c:      	ldrb.w	r0, [r5, #0x36]
43864b30:      	cmp	r0, #0x1
43864b32:      	bne	0x43864b76  @ imm = #0x40
43864b34:      	ldr	r3, [pc, #0xe0]         @ 0x43864c18 
43864b36:      	movs	r1, #0x0
43864b38:      	add	r3, pc
43864b3a:      	strb.w	r1, [r3, #0x61]
43864b3e:      	strb.w	r1, [r3, #0x60]
43864b42:      	ldrb.w	r2, [r5, #0x37]
43864b46:      	cbnz	r2, 0x43864b4c  @ imm = #0x2
43864b48:      	str	r0, [r3, #0x5c]
43864b4a:      	b	0x43864b76  @ imm = #0x28
43864b4c:      	cmp	r2, #0x1
43864b4e:      	bne	0x43864b54  @ imm = #0x2
43864b50:      	adds	r2, #0x2
43864b52:      	b	0x43864b74  @ imm = #0x1e
43864b54:      	cmp	r2, #0x2
43864b56:      	beq	0x43864b74  @ imm = #0x1a
43864b58:      	cmp	r2, #0x3
43864b5a:      	bne	0x43864b60  @ imm = #0x2
43864b5c:      	str	r1, [r3, #0x5c]
43864b5e:      	b	0x43864b76  @ imm = #0x14
43864b60:      	cmp	r2, #0x4
43864b62:      	beq	0x43864b74  @ imm = #0xe
43864b64:      	cmp	r2, #0x5
43864b66:      	beq	0x43864b74  @ imm = #0xa
43864b68:      	cmp	r2, #0x6
43864b6a:      	beq	0x43864b74  @ imm = #0x6
43864b6c:      	cmp	r2, #0x7
43864b6e:      	ite	ne
43864b70:      	movne	r2, #0x1
43864b72:      	moveq	r2, #0x7
43864b74:      	str	r2, [r3, #0x5c]
43864b76:      	ldr	r3, [pc, #0xa4]         @ 0x43864c1c 
43864b78:      	ldr	r1, [pc, #0xa4]         @ 0x43864c20 
43864b7a:      	add	r3, pc
43864b7c:      	ldr	r1, [r4, r1]
43864b7e:      	ldrb.w	r2, [r3, #0x5c]
43864b82:      	strb.w	r2, [r1, #0x9ac]
43864b86:      	ldr	r1, [pc, #0x9c]         @ 0x43864c24 
43864b88:      	ldr	r1, [r4, r1]
43864b8a:      	strb	r2, [r1]
43864b8c:      	ldr	r2, [pc, #0x98]         @ 0x43864c28 
43864b8e:      	ldr.w	r1, [r7, #0x424]
43864b92:      	ldr	r2, [r4, r2]
43864b94:      	strb	r1, [r2]
43864b96:      	ldr	r2, [pc, #0x94]         @ 0x43864c2c 
43864b98:      	ldrb.w	r1, [r3, #0x60]
43864b9c:      	ldrb.w	r3, [r3, #0x61]
43864ba0:      	ldr	r2, [r4, r2]
43864ba2:      	strb	r1, [r2]
43864ba4:      	ldr	r2, [pc, #0x88]         @ 0x43864c30 
43864ba6:      	ldr	r2, [r4, r2]
43864ba8:      	strb	r3, [r2]
43864baa:      	pop.w	{r4, r5, r6, r7, r8, pc}
43864bae:      	nop
43864bb0:      	<unknown>
43864bb4:      	movs	r1, #0xe0
43864bb6:      	lsls	r2, r5, #0x1
43864bb8:      	movs	r1, #0xd8
43864bba:      	lsls	r2, r5, #0x1
43864bbc:      	movs	r1, #0xca
43864bbe:      	lsls	r2, r5, #0x1
43864bc0:      	strh	r0, [r5, #0x18]
43864bc2:      	movs	r0, r0
43864bc4:      	movs	r1, #0xaa
43864bc6:      	lsls	r2, r5, #0x1
43864bc8:      	movs	r1, #0xa4
43864bca:      	lsls	r2, r5, #0x1
43864bcc:      	movs	r1, #0x92
43864bce:      	lsls	r2, r5, #0x1
43864bd0:      	movs	r1, #0x8c
43864bd2:      	lsls	r2, r5, #0x1
43864bd4:      	movs	r1, #0x86
43864bd6:      	lsls	r2, r5, #0x1
43864bd8:      	movs	r1, #0x80
43864bda:      	lsls	r2, r5, #0x1
43864bdc:      	orrs	r4, r5
43864bde:      	movs	r0, r0
43864be0:      	movs	r1, #0x64
43864be2:      	lsls	r2, r5, #0x1
43864be4:      	movs	r1, #0x5a
43864be6:      	lsls	r2, r5, #0x1
43864be8:      	movs	r1, #0x4e
43864bea:      	lsls	r2, r5, #0x1
43864bec:      	movs	r1, #0x42
43864bee:      	lsls	r2, r5, #0x1
43864bf0:      	movs	r1, #0x36
43864bf2:      	lsls	r2, r5, #0x1
43864bf4:      	movs	r1, #0x2a
43864bf6:      	lsls	r2, r5, #0x1
43864bf8:      	movs	r1, #0x1e
43864bfa:      	lsls	r2, r5, #0x1
43864bfc:      	movs	r1, #0x12
43864bfe:      	lsls	r2, r5, #0x1
43864c00:      	movs	r1, #0xc
43864c02:      	lsls	r2, r5, #0x1
43864c04:      	movs	r0, #0xe8
43864c06:      	lsls	r2, r5, #0x1
43864c08:      	movs	r0, #0xda
43864c0a:      	lsls	r2, r5, #0x1
43864c0c:      	movs	r0, #0xd2
43864c0e:      	lsls	r2, r5, #0x1
43864c10:      	movs	r0, #0xb6
43864c12:      	lsls	r2, r5, #0x1
43864c14:      	movs	r0, #0x9e
43864c16:      	lsls	r2, r5, #0x1
43864c18:      	movs	r0, #0x8c
43864c1a:      	lsls	r2, r5, #0x1
43864c1c:      	movs	r0, #0x4a
43864c1e:      	lsls	r2, r5, #0x1
43864c20:      	ldrb	r4, [r6, #0x1d]
43864c22:      	movs	r0, r0
43864c24:      	str	r0, [r3, #0x64]
43864c26:      	movs	r0, r0
43864c28:      	adds	r2, #0x70
43864c2a:      	movs	r0, r0
43864c2c:      	str	r0, [r2, #0x10]
43864c2e:      	movs	r0, r0
43864c30:      	subs	r2, #0x50
43864c32:      	movs	r0, r0
43864c34:      	ldr	r3, [pc, #0x34]         @ 0x43864c6c 
43864c36:      	mov	r1, r0
43864c38:      	push	{r4, lr}
43864c3a:      	add	r3, pc
43864c3c:      	ldrh	r2, [r3]
43864c3e:      	ldrb	r3, [r3, #0x2]
43864c40:      	strh	r2, [r0]
43864c42:      	movs	r2, #0x0
43864c44:      	strb	r3, [r1, #2]!
43864c48:      	ldr	r3, [pc, #0x24]         @ 0x43864c70 
43864c4a:      	add	r3, pc
43864c4c:      	adds	r4, r3, r2
43864c4e:      	adds	r2, #0x2
43864c50:      	cmp	r2, #0x52
43864c52:      	ldrh	r4, [r4, #0x4]
43864c54:      	strh	r4, [r1, #2]!
43864c58:      	bne	0x43864c48  @ imm = #-0x14
43864c5a:      	ldrh.w	r2, [r3, #0x56]
43864c5e:      	ldrh.w	r3, [r3, #0x58]
43864c62:      	strh.w	r2, [r0, #0x56]
43864c66:      	strh.w	r3, [r0, #0x58]
43864c6a:      	pop	{r4, pc}
43864c6c:      	subs	r2, r1, #0x6
43864c6e:      	lsls	r2, r5, #0x1
43864c70:      	subs	r2, r7, #0x5
43864c72:      	lsls	r2, r5, #0x1
43864c74:      	ldr	r3, [pc, #0x4]          @ 0x43864c7c 
43864c76:      	add	r3, pc
43864c78:      	ldr	r0, [r3, #0x5c]
43864c7a:      	bx	lr
43864c7c:      	subs	r6, r1, #0x5
43864c7e:      	lsls	r2, r5, #0x1
