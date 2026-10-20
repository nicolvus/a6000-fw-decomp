
work/claude/input/a6000-av-cam-view.elf:	file format elf32-littlearm

Disassembly of section .text:

43541000 <_binary_input_a6000_av_cam_bin_start>:
437f8900:      	lsls	r2, r0, #0xc
437f8902:      	bne	0x437f8952 <_binary_input_a6000_av_cam_bin_start+0x2b7952> @ imm = #0x4c
437f8904:      	add.w	r2, r0, #0x4b00
437f8908:      	strb.w	r3, [sp, #0x14]
437f890c:      	add.w	r3, r0, #0x640
437f8910:      	ldrh.w	r2, [r2, #0x54]
437f8914:      	adds	r3, #0xc
437f8916:      	str	r3, [sp, #0x18]
437f8918:      	add.w	r3, r0, #0x4a00
437f891c:      	strh.w	r2, [sp, #0xc]
437f8920:      	ldrh.w	r2, [r0, #0x1d8]
437f8924:      	ldr.w	r3, [r3, #0xd0]
437f8928:      	strh.w	r2, [sp, #0xe]
437f892c:      	add.w	r2, r0, #0x5c8
437f8930:      	str	r2, [sp, #0x10]
437f8932:      	cbz	r3, 0x437f8936 <_binary_input_a6000_av_cam_bin_start+0x2b7936> @ imm = #0x0
437f8934:      	adds	r3, #0x20
437f8936:      	add.w	r5, r4, #0x20
437f893a:      	add.w	r0, r4, #0x1180
437f893e:      	str	r3, [sp]
437f8940:      	adds	r0, #0x18
437f8942:      	mov	r1, r5
437f8944:      	add	r2, sp, #0xc
437f8946:      	add	r3, sp, #0x18
437f8948:      	bl	0x437b43b4 <_binary_input_a6000_av_cam_bin_start+0x2733b4> @ imm = #-0x44598
437f894c:      	mov	r0, r5
437f894e:      	bl	0x43b109bc <_binary_input_a6000_av_cam_bin_start+0x5cf9bc> @ imm = #0x31806a
437f8952:      	ldrb.w	r3, [r6, #0xc1]
437f8956:      	tst.w	r3, #0x8
437f895a:      	bne	0x437f897a <_binary_input_a6000_av_cam_bin_start+0x2b797a> @ imm = #0x1c
437f895c:      	add.w	r3, r4, #0x4a00
437f8960:      	ldr.w	r2, [r3, #0xd0]
437f8964:      	cbz	r2, 0x437f896c <_binary_input_a6000_av_cam_bin_start+0x2b796c> @ imm = #0x4
437f8966:      	add.w	r2, r2, #0x1440
437f896a:      	adds	r2, #0x8
437f896c:      	add.w	r0, r4, #0x2c00
437f8970:      	add.w	r1, r4, #0x20
437f8974:      	adds	r0, #0x2c
437f8976:      	bl	0x4379ed34 <_binary_input_a6000_av_cam_bin_start+0x25dd34> @ imm = #-0x59c46
437f897a:      	add.w	r0, r4, #0x20
437f897e:      	bl	0x437d331c <_binary_input_a6000_av_cam_bin_start+0x29231c> @ imm = #-0x25666
437f8982:      	add	sp, #0x20
437f8984:      	pop	{r4, r5, r6, pc}
437f8986:      	nop
437f8988:      	str	r0, [r6, #0x5c]
437f898a:      	lsls	r2, r0, #0x2
437f898c:      	str	r0, [r1, #0x58]
437f898e:      	movs	r0, r0
437f8990:      	ldr	r3, [pc, #0xb4]         @ 0x437f8a48 <_binary_input_a6000_av_cam_bin_start+0x2b7a48>
437f8992:      	ldr	r2, [pc, #0xb8]         @ 0x437f8a4c <_binary_input_a6000_av_cam_bin_start+0x2b7a4c>
437f8994:      	add	r3, pc
437f8996:      	push	{r4, r5, r6, r7, lr}
437f8998:      	mov	r4, r0
437f899a:      	ldr	r6, [r3, r2]
437f899c:      	sub	sp, #0x24
437f899e:      	ldr	r3, [r6, #0x24]
437f89a0:      	cmp	r3, #0x0
437f89a2:      	bne	0x437f8a14 <_binary_input_a6000_av_cam_bin_start+0x2b7a14> @ imm = #0x6e
437f89a4:      	bl	0x43affdbe <_binary_input_a6000_av_cam_bin_start+0x5bedbe> @ imm = #0x307416
437f89a8:      	add.w	r3, r4, #0x4b00
437f89ac:      	ldrh.w	r3, [r3, #0x54]
437f89b0:      	strh.w	r3, [sp, #0x8]
437f89b4:      	ldrh.w	r3, [r4, #0x1d8]
437f89b8:      	strh.w	r3, [sp, #0xa]
437f89bc:      	add.w	r3, r4, #0x5c8
437f89c0:      	str	r3, [sp, #0xc]
437f89c2:      	add.w	r3, r4, #0x640
437f89c6:      	adds	r3, #0xc
437f89c8:      	str	r3, [sp, #0x14]
437f89ca:      	add.w	r3, r4, #0x4a00
437f89ce:      	ldr.w	r3, [r3, #0xd0]
437f89d2:      	mov	r5, r0
437f89d4:      	strb.w	r0, [sp, #0x10]
437f89d8:      	cbz	r3, 0x437f89dc <_binary_input_a6000_av_cam_bin_start+0x2b79dc> @ imm = #0x0
437f89da:      	adds	r3, #0x20
437f89dc:      	add.w	r0, r4, #0x1180
437f89e0:      	str	r3, [sp]
437f89e2:      	adds	r0, #0x18
437f89e4:      	add.w	r1, r4, #0x20
437f89e8:      	add	r2, sp, #0x8
437f89ea:      	add	r3, sp, #0x14
437f89ec:      	bl	0x437b43b4 <_binary_input_a6000_av_cam_bin_start+0x2733b4> @ imm = #-0x4463c
437f89f0:      	cbnz	r5, 0x437f8a14 <_binary_input_a6000_av_cam_bin_start+0x2b7a14> @ imm = #0x20
437f89f2:      	mov	r1, r5
437f89f4:      	mov	r0, r4
437f89f6:      	bl	0x437f9a64 <_binary_input_a6000_av_cam_bin_start+0x2b8a64> @ imm = #0x106a
437f89fa:      	add.w	r3, r4, #0x12c0
437f89fe:      	movs	r0, #0x4
437f8a00:      	movs	r1, #0x2a
437f8a02:      	ldrh	r5, [r3, #0x38]
437f8a04:      	ldrh	r2, [r3, #0x2e]
437f8a06:      	add.w	r3, r4, #0x1300
437f8a0a:      	orr.w	r2, r2, r5, lsl #16
437f8a0e:      	ldrh	r3, [r3, #0x4]
437f8a10:      	bl	0x43901a8c <_binary_input_a6000_av_cam_bin_start+0x3c0a8c> @ imm = #0x109078
437f8a14:      	ldr	r3, [r6, #0x24]
437f8a16:      	cbnz	r3, 0x437f8a1e <_binary_input_a6000_av_cam_bin_start+0x2b7a1e> @ imm = #0x4
437f8a18:      	ldrb.w	r5, [sp, #0x18]
437f8a1c:      	b	0x437f8a20 <_binary_input_a6000_av_cam_bin_start+0x2b7a20> @ imm = #0x0
437f8a1e:      	movs	r5, #0x0
437f8a20:      	add.w	r7, r4, #0x20
437f8a24:      	mov	r0, r7
437f8a26:      	bl	0x43af64d6 <_binary_input_a6000_av_cam_bin_start+0x5b54d6> @ imm = #0x2fdaac
437f8a2a:      	mov	r1, r7
437f8a2c:      	mov	r6, r0
437f8a2e:      	add.w	r0, r4, #0x3080
437f8a32:      	adds	r0, #0x60
437f8a34:      	bl	0x43af641e <_binary_input_a6000_av_cam_bin_start+0x5b541e> @ imm = #0x2fd9e6
437f8a38:      	movs	r0, #0x0
437f8a3a:      	bfi	r0, r5, #0, #8
437f8a3e:      	bfi	r0, r6, #8, #8
437f8a42:      	add	sp, #0x24
437f8a44:      	pop	{r4, r5, r6, r7, pc}
437f8a46:      	nop
437f8a48:      	str	r4, [r1, #0x54]
437f8a4a:      	lsls	r2, r0, #0x2
437f8a4c:      	subs	r4, r5, #0x6
437f8a4e:      	movs	r0, r0
437f8a50:      	push	{r4, r5, r6, r7, lr}
437f8a52:      	sub	sp, #0x8c
437f8a54:      	add.w	r3, r0, #0x640
437f8a58:      	mov	r4, r0
437f8a5a:      	adds	r3, #0xc
437f8a5c:      	str	r3, [sp, #0x4]
437f8a5e:      	add.w	r3, r0, #0x4b00
437f8a62:      	ldr	r5, [pc, #0xc8]         @ 0x437f8b2c <_binary_input_a6000_av_cam_bin_start+0x2b7b2c>
437f8a64:      	add.w	r6, r4, #0x20
437f8a68:      	ldrh.w	r2, [r3, #0x54]
437f8a6c:      	add	r5, pc
437f8a6e:      	ldrh.w	r3, [r3, #0x9c]
437f8a72:      	strh.w	r2, [sp, #0x6c]
437f8a76:      	strh.w	r3, [sp, #0x70]
437f8a7a:      	ldrh.w	r3, [r0, #0x1d8]
437f8a7e:      	strh.w	r3, [sp, #0x6e]
437f8a82:      	bl	0x43affdbe <_binary_input_a6000_av_cam_bin_start+0x5bedbe> @ imm = #0x307338
437f8a86:      	ldr	r3, [pc, #0xa8]         @ 0x437f8b30 <_binary_input_a6000_av_cam_bin_start+0x2b7b30>
437f8a88:      	strb.w	r0, [sp, #0x78]
437f8a8c:      	ldr	r7, [r5, r3]
437f8a8e:      	add.w	r5, r4, #0x1180
437f8a92:      	add.w	r5, r5, #0x18
437f8a96:      	ldr	r3, [r7, #0x24]
437f8a98:      	cmp	r3, #0x1
437f8a9a:      	bne	0x437f8adc <_binary_input_a6000_av_cam_bin_start+0x2b7adc> @ imm = #0x3e
437f8a9c:      	add	r3, sp, #0x6c
437f8a9e:      	mov	r0, r5
437f8aa0:      	mov	r1, r6
437f8aa2:      	add	r2, sp, #0x4
437f8aa4:      	bl	0x4383fd6c <_binary_input_a6000_av_cam_bin_start+0x2fed6c> @ imm = #0x472c4
437f8aa8:      	add	r2, sp, #0x4
437f8aaa:      	mov	r0, r5
437f8aac:      	mov	r1, r6
437f8aae:      	bl	0x43840150 <_binary_input_a6000_av_cam_bin_start+0x2ff150> @ imm = #0x4769e
437f8ab2:      	ldrh.w	r3, [sp, #0xa]
437f8ab6:      	ldrh.w	r2, [sp, #0x8]
437f8aba:      	strh.w	r3, [r4, #0x6be]
437f8abe:      	ldrh.w	r3, [sp, #0x10]
437f8ac2:      	strh.w	r2, [r4, #0x6bc]
437f8ac6:      	ldrh.w	r2, [sp, #0xe]
437f8aca:      	strh.w	r3, [r4, #0x65e]
437f8ace:      	ldrb.w	r3, [sp, #0x12]
437f8ad2:      	strh.w	r2, [r4, #0x65c]
437f8ad6:      	strb.w	r3, [r4, #0x660]
437f8ada:      	b	0x437f8af8 <_binary_input_a6000_av_cam_bin_start+0x2b7af8> @ imm = #0x1a
437f8adc:      	add	r2, sp, #0x6c
437f8ade:      	add	r3, sp, #0x7c
437f8ae0:      	mov	r0, r5
437f8ae2:      	mov	r1, r6
437f8ae4:      	bl	0x437b21b8 <_binary_input_a6000_av_cam_bin_start+0x2711b8> @ imm = #-0x46930
437f8ae8:      	ldrh.w	r2, [sp, #0x7e]
437f8aec:      	ldrh.w	r3, [sp, #0x80]
437f8af0:      	strh.w	r2, [r4, #0x6bc]
437f8af4:      	strh.w	r3, [r4, #0x6be]
437f8af8:      	add.w	r3, r4, #0x12c0
437f8afc:      	ldrh	r0, [r3, #0x38]
437f8afe:      	bl	0x43b7b350 <_binary_input_a6000_av_cam_bin_start+0x63a350> @ imm = #0x38284e
437f8b02:      	mov	r0, r4
437f8b04:      	bl	0x437f9b48 <_binary_input_a6000_av_cam_bin_start+0x2b8b48> @ imm = #0x1040
437f8b08:      	ldr	r3, [r7, #0x24]
437f8b0a:      	cmp	r3, #0x1
437f8b0c:      	bne	0x437f8b18 <_binary_input_a6000_av_cam_bin_start+0x2b7b18> @ imm = #0x8
437f8b0e:      	ldr	r0, [sp, #0x4]
437f8b10:      	add.w	r1, sp, #0xe
437f8b14:      	bl	0x43ae9462 <_binary_input_a6000_av_cam_bin_start+0x5a8462> @ imm = #0x2f094a
437f8b18:      	ldr	r3, [r7, #0x24]
437f8b1a:      	cmp	r3, #0x1
437f8b1c:      	ite	eq
437f8b1e:      	ldrheq.w	r0, [sp, #0x6a]
437f8b22:      	ldrhne.w	r0, [sp, #0x7c]
437f8b26:      	add	sp, #0x8c
437f8b28:      	pop	{r4, r5, r6, r7, pc}
437f8b2a:      	nop
437f8b2c:      	str	r4, [r6, #0x44]
437f8b2e:      	lsls	r2, r0, #0x2
437f8b30:      	subs	r4, r5, #0x6
437f8b32:      	movs	r0, r0
437f8b34:      	push	{r0, r1, r2, r3, r4, lr}
437f8b36:      	mov	r4, r0
437f8b38:      	ldr	r3, [pc, #0x40]         @ 0x437f8b7c <_binary_input_a6000_av_cam_bin_start+0x2b7b7c>
437f8b3a:      	ldr	r2, [pc, #0x44]         @ 0x437f8b80 <_binary_input_a6000_av_cam_bin_start+0x2b7b80>
437f8b3c:      	add	r3, pc
437f8b3e:      	ldr	r3, [r3, r2]
437f8b40:      	ldr	r3, [r3, #0x24]
437f8b42:      	cbnz	r3, 0x437f8b7a <_binary_input_a6000_av_cam_bin_start+0x2b7b7a> @ imm = #0x34
437f8b44:      	add.w	r3, r0, #0x4b00
437f8b48:      	ldrh.w	r2, [r3, #0x54]
437f8b4c:      	ldrh.w	r3, [r3, #0x9c]
437f8b50:      	strh.w	r2, [sp, #0x4]
437f8b54:      	strh.w	r3, [sp, #0x8]
437f8b58:      	ldrh.w	r3, [r0, #0x1d8]
437f8b5c:      	strh.w	r3, [sp, #0x6]
437f8b60:      	bl	0x43affdbe <_binary_input_a6000_av_cam_bin_start+0x5bedbe> @ imm = #0x30725a
437f8b64:      	add.w	r1, r4, #0x20
437f8b68:      	add	r2, sp, #0x4
437f8b6a:      	add	r3, sp, #0xc
437f8b6c:      	strb.w	r0, [sp, #0xa]
437f8b70:      	add.w	r0, r4, #0x1180
437f8b74:      	adds	r0, #0x18
437f8b76:      	bl	0x437b3860 <_binary_input_a6000_av_cam_bin_start+0x272860> @ imm = #-0x4531a
437f8b7a:      	pop	{r0, r1, r2, r3, r4, pc}
437f8b7c:      	str	r4, [r4, #0x38]
437f8b7e:      	lsls	r2, r0, #0x2
437f8b80:      	subs	r4, r5, #0x6
437f8b82:      	movs	r0, r0
437f8b84:      	ldr	r3, [pc, #0x50]         @ 0x437f8bd8 <_binary_input_a6000_av_cam_bin_start+0x2b7bd8>
437f8b86:      	ldr	r2, [pc, #0x54]         @ 0x437f8bdc <_binary_input_a6000_av_cam_bin_start+0x2b7bdc>
437f8b88:      	add	r3, pc
437f8b8a:      	push	{r4, r5, r6, r7, lr}
437f8b8c:      	mov	r5, r0
437f8b8e:      	ldr	r4, [r3, r2]
437f8b90:      	sub	sp, #0x14
437f8b92:      	ldr	r7, [r4, #0x24]
437f8b94:      	cbnz	r7, 0x437f8bc8 <_binary_input_a6000_av_cam_bin_start+0x2b7bc8> @ imm = #0x30
437f8b96:      	add.w	r6, r0, #0x20
437f8b9a:      	mov	r0, r6
437f8b9c:      	bl	0x437d331c <_binary_input_a6000_av_cam_bin_start+0x29231c> @ imm = #-0x25884
437f8ba0:      	add.w	r3, r5, #0x4b00
437f8ba4:      	add.w	r0, r5, #0x1180
437f8ba8:      	mov	r1, r6
437f8baa:      	ldrh.w	r3, [r3, #0x54]
437f8bae:      	adds	r0, #0x18
437f8bb0:      	add	r2, sp, #0x4
437f8bb2:      	strb.w	r7, [sp, #0x8]
437f8bb6:      	strh.w	r3, [sp, #0x4]
437f8bba:      	ldrh.w	r3, [r5, #0x1d8]
437f8bbe:      	strh.w	r3, [sp, #0x6]
437f8bc2:      	add	r3, sp, #0xc
437f8bc4:      	bl	0x437b252c <_binary_input_a6000_av_cam_bin_start+0x27152c> @ imm = #-0x4669c
437f8bc8:      	ldr	r3, [r4, #0x24]
437f8bca:      	cbnz	r3, 0x437f8bd2 <_binary_input_a6000_av_cam_bin_start+0x2b7bd2> @ imm = #0x4
437f8bcc:      	ldrb.w	r0, [sp, #0xc]
