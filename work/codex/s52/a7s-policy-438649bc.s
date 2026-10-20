
work/claude/input/a7s-av-cam-view.elf:	file format elf32-littlearm

Disassembly of section .text:

43541000 <_binary_input_a7s_av_cam_bin_start>:
438649bc:      	push.w	{r4, r5, r6, r7, r8, lr}
438649c0:      	mov	r7, r2
438649c2:      	ldrh.w	r2, [r2, #0x4c4]
438649c6:      	mov	r5, r0
438649c8:      	ldr	r4, [pc, #0x1e4]        @ 0x43864bb0 <_binary_input_a7s_av_cam_bin_start+0x323bb0>
438649ca:      	mov	r6, r1
438649cc:      	tst.w	r2, #0x60
438649d0:      	add	r4, pc
438649d2:      	bne	0x438649da <_binary_input_a7s_av_cam_bin_start+0x3239da> @ imm = #0x4
438649d4:      	ands	r1, r2, #0x80
438649d8:      	beq	0x438649f0 <_binary_input_a7s_av_cam_bin_start+0x3239f0> @ imm = #0x14
438649da:      	tst.w	r2, #0x20
438649de:      	beq	0x438649e8 <_binary_input_a7s_av_cam_bin_start+0x3239e8> @ imm = #0x6
438649e0:      	ldr	r2, [pc, #0x1d0]        @ 0x43864bb4 <_binary_input_a7s_av_cam_bin_start+0x323bb4>
438649e2:      	movs	r1, #0x5
438649e4:      	add	r2, pc
438649e6:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x5e
438649e8:      	ldr	r2, [pc, #0x1cc]        @ 0x43864bb8 <_binary_input_a7s_av_cam_bin_start+0x323bb8>
438649ea:      	movs	r1, #0x1
438649ec:      	add	r2, pc
438649ee:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x56
438649f0:      	ldr.w	r2, [r7, #0x404]
438649f4:      	cmp	r2, #0x2
438649f6:      	bne	0x438649fe <_binary_input_a7s_av_cam_bin_start+0x3239fe> @ imm = #0x4
438649f8:      	ldr	r2, [pc, #0x1c0]        @ 0x43864bbc <_binary_input_a7s_av_cam_bin_start+0x323bbc>
438649fa:      	add	r2, pc
438649fc:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x48
438649fe:      	ldr.w	r1, [r7, #0x424]
43864a02:      	cmp	r1, #0x1
43864a04:      	bne	0x43864a42 <_binary_input_a7s_av_cam_bin_start+0x323a42> @ imm = #0x3a
43864a06:      	ldrb	r2, [r3, #0x2]
43864a08:      	cbnz	r2, 0x43864a24 <_binary_input_a7s_av_cam_bin_start+0x323a24> @ imm = #0x18
43864a0a:      	ldr	r2, [pc, #0x1b4]        @ 0x43864bc0 <_binary_input_a7s_av_cam_bin_start+0x323bc0>
43864a0c:      	ldrh.w	r0, [r6, #0x166]
43864a10:      	ldr	r2, [r4, r2]
43864a12:      	ldrh	r2, [r2]
43864a14:      	cmp	r0, r2
43864a16:      	bls	0x43864a1e <_binary_input_a7s_av_cam_bin_start+0x323a1e> @ imm = #0x4
43864a18:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc4 <_binary_input_a7s_av_cam_bin_start+0x323bc4>
43864a1a:      	add	r2, pc
43864a1c:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x28
43864a1e:      	ldr	r2, [pc, #0x1a8]        @ 0x43864bc8 <_binary_input_a7s_av_cam_bin_start+0x323bc8>
43864a20:      	add	r2, pc
43864a22:      	b	0x43864a46 <_binary_input_a7s_av_cam_bin_start+0x323a46> @ imm = #0x20
43864a24:      	cmp	r2, #0x1
43864a26:      	bne	0x43864a3c <_binary_input_a7s_av_cam_bin_start+0x323a3c> @ imm = #0x12
43864a28:      	ldrb.w	r1, [r7, #0x38c]
43864a2c:      	cmp	r1, #0x1
43864a2e:      	bne	0x43864a36 <_binary_input_a7s_av_cam_bin_start+0x323a36> @ imm = #0x4
43864a30:      	ldr	r2, [pc, #0x198]        @ 0x43864bcc <_binary_input_a7s_av_cam_bin_start+0x323bcc>
43864a32:      	add	r2, pc
43864a34:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x10
43864a36:      	ldr	r2, [pc, #0x198]        @ 0x43864bd0 <_binary_input_a7s_av_cam_bin_start+0x323bd0>
43864a38:      	add	r2, pc
43864a3a:      	b	0x43864a46 <_binary_input_a7s_av_cam_bin_start+0x323a46> @ imm = #0x8
43864a3c:      	ldr	r2, [pc, #0x194]        @ 0x43864bd4 <_binary_input_a7s_av_cam_bin_start+0x323bd4>
43864a3e:      	add	r2, pc
43864a40:      	b	0x43864a48 <_binary_input_a7s_av_cam_bin_start+0x323a48> @ imm = #0x4
43864a42:      	ldr	r2, [pc, #0x194]        @ 0x43864bd8 <_binary_input_a7s_av_cam_bin_start+0x323bd8>
43864a44:      	add	r2, pc
43864a46:      	movs	r1, #0x3
43864a48:      	str	r1, [r2, #0x5c]
43864a4a:      	ldr	r2, [pc, #0x190]        @ 0x43864bdc <_binary_input_a7s_av_cam_bin_start+0x323bdc>
43864a4c:      	ldr	r1, [r4, r2]
43864a4e:      	mov	r8, r1
43864a50:      	ldrb.w	r2, [r1, #0x7e]
43864a54:      	cmp	r2, #0x0
43864a56:      	beq	0x43864abe <_binary_input_a7s_av_cam_bin_start+0x323abe> @ imm = #0x64
43864a58:      	cmp	r2, #0x1
43864a5a:      	bne	0x43864a64 <_binary_input_a7s_av_cam_bin_start+0x323a64> @ imm = #0x6
43864a5c:      	ldr	r2, [pc, #0x180]        @ 0x43864be0 <_binary_input_a7s_av_cam_bin_start+0x323be0>
43864a5e:      	movs	r1, #0x0
43864a60:      	add	r2, pc
43864a62:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x56
43864a64:      	cmp	r2, #0x2
43864a66:      	bne	0x43864a6e <_binary_input_a7s_av_cam_bin_start+0x323a6e> @ imm = #0x4
43864a68:      	ldr	r2, [pc, #0x178]        @ 0x43864be4 <_binary_input_a7s_av_cam_bin_start+0x323be4>
43864a6a:      	add	r2, pc
43864a6c:      	b	0x43864aba <_binary_input_a7s_av_cam_bin_start+0x323aba> @ imm = #0x4a
43864a6e:      	cmp	r2, #0x3
43864a70:      	bne	0x43864a7a <_binary_input_a7s_av_cam_bin_start+0x323a7a> @ imm = #0x6
43864a72:      	ldr	r2, [pc, #0x174]        @ 0x43864be8 <_binary_input_a7s_av_cam_bin_start+0x323be8>
43864a74:      	movs	r1, #0x2
43864a76:      	add	r2, pc
43864a78:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x40
43864a7a:      	cmp	r2, #0x4
43864a7c:      	bne	0x43864a86 <_binary_input_a7s_av_cam_bin_start+0x323a86> @ imm = #0x6
43864a7e:      	ldr	r2, [pc, #0x16c]        @ 0x43864bec <_binary_input_a7s_av_cam_bin_start+0x323bec>
43864a80:      	movs	r1, #0x3
43864a82:      	add	r2, pc
43864a84:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x34
43864a86:      	cmp	r2, #0x5
43864a88:      	bne	0x43864a92 <_binary_input_a7s_av_cam_bin_start+0x323a92> @ imm = #0x6
43864a8a:      	ldr	r2, [pc, #0x164]        @ 0x43864bf0 <_binary_input_a7s_av_cam_bin_start+0x323bf0>
43864a8c:      	movs	r1, #0x4
43864a8e:      	add	r2, pc
43864a90:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x28
43864a92:      	cmp	r2, #0x6
43864a94:      	bne	0x43864a9e <_binary_input_a7s_av_cam_bin_start+0x323a9e> @ imm = #0x6
43864a96:      	ldr	r2, [pc, #0x15c]        @ 0x43864bf4 <_binary_input_a7s_av_cam_bin_start+0x323bf4>
43864a98:      	movs	r1, #0x5
43864a9a:      	add	r2, pc
43864a9c:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x1c
43864a9e:      	cmp	r2, #0x7
43864aa0:      	bne	0x43864aaa <_binary_input_a7s_av_cam_bin_start+0x323aaa> @ imm = #0x6
43864aa2:      	ldr	r2, [pc, #0x154]        @ 0x43864bf8 <_binary_input_a7s_av_cam_bin_start+0x323bf8>
43864aa4:      	movs	r1, #0x6
43864aa6:      	add	r2, pc
43864aa8:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x10
43864aaa:      	cmp	r2, #0x8
43864aac:      	bne	0x43864ab6 <_binary_input_a7s_av_cam_bin_start+0x323ab6> @ imm = #0x6
43864aae:      	ldr	r2, [pc, #0x14c]        @ 0x43864bfc <_binary_input_a7s_av_cam_bin_start+0x323bfc>
43864ab0:      	movs	r1, #0x7
43864ab2:      	add	r2, pc
43864ab4:      	b	0x43864abc <_binary_input_a7s_av_cam_bin_start+0x323abc> @ imm = #0x4
43864ab6:      	ldr	r2, [pc, #0x148]        @ 0x43864c00 <_binary_input_a7s_av_cam_bin_start+0x323c00>
43864ab8:      	add	r2, pc
43864aba:      	movs	r1, #0x1
43864abc:      	str	r1, [r2, #0x5c]
43864abe:      	ldrb	r0, [r3, #0x2]
43864ac0:      	cmp	r0, #0x1
43864ac2:      	bne	0x43864aca <_binary_input_a7s_av_cam_bin_start+0x323aca> @ imm = #0x4
43864ac4:      	ldrb.w	r3, [r7, #0x38c]
43864ac8:      	cbz	r3, 0x43864acc <_binary_input_a7s_av_cam_bin_start+0x323acc> @ imm = #0x0
43864aca:      	movs	r0, #0x0
43864acc:      	bl	0x438642e4 <_binary_input_a7s_av_cam_bin_start+0x3232e4> @ imm = #-0x7ec
43864ad0:      	ldr.w	r3, [r7, #0x404]
43864ad4:      	cmp	r3, #0x2
43864ad6:      	bne	0x43864ae0 <_binary_input_a7s_av_cam_bin_start+0x323ae0> @ imm = #0x6
43864ad8:      	ldr	r3, [pc, #0x128]        @ 0x43864c04 <_binary_input_a7s_av_cam_bin_start+0x323c04>
43864ada:      	movs	r2, #0x0
43864adc:      	add	r3, pc
43864ade:      	b	0x43864b00 <_binary_input_a7s_av_cam_bin_start+0x323b00> @ imm = #0x1e
43864ae0:      	ldr.w	r2, [r7, #0x424]
43864ae4:      	cmp	r2, #0x1
43864ae6:      	bne	0x43864aee <_binary_input_a7s_av_cam_bin_start+0x323aee> @ imm = #0x4
43864ae8:      	ldr	r3, [pc, #0x11c]        @ 0x43864c08 <_binary_input_a7s_av_cam_bin_start+0x323c08>
43864aea:      	add	r3, pc
43864aec:      	b	0x43864b00 <_binary_input_a7s_av_cam_bin_start+0x323b00> @ imm = #0x10
43864aee:      	ldr	r3, [pc, #0x11c]        @ 0x43864c0c <_binary_input_a7s_av_cam_bin_start+0x323c0c>
43864af0:      	movs	r2, #0x0
43864af2:      	add	r3, pc
43864af4:      	strb.w	r2, [r3, #0x60]
43864af8:      	ldrb.w	r2, [r8, #0x10f]
43864afc:      	cmp	r2, #0x1
43864afe:      	bne	0x43864b04 <_binary_input_a7s_av_cam_bin_start+0x323b04> @ imm = #0x2
43864b00:      	strb.w	r2, [r3, #0x60]
43864b04:      	ldrb.w	r2, [r8, #0xf9]
43864b08:      	cmp	r2, #0x1
43864b0a:      	bne	0x43864b22 <_binary_input_a7s_av_cam_bin_start+0x323b22> @ imm = #0x14
43864b0c:      	ldr	r3, [pc, #0x100]        @ 0x43864c10 <_binary_input_a7s_av_cam_bin_start+0x323c10>
43864b0e:      	add	r3, pc
43864b10:      	ldr	r1, [r3, #0x5c]
43864b12:      	cmp	r1, #0x3
43864b14:      	bne	0x43864b22 <_binary_input_a7s_av_cam_bin_start+0x323b22> @ imm = #0xa
43864b16:      	ldrh.w	r0, [r6, #0x166]
43864b1a:      	ldrh.w	r1, [r8, #0xfc]
43864b1e:      	cmp	r0, r1
