/* S41: read-only exports. */

/* 438565a8 */

void FUN_438565a8(int param_1,int param_2,int param_3,int param_4)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  short sVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  undefined1 *puVar10;
  undefined2 *puVar11;
  uint uVar12;
  char cVar13;
  int iVar14;
  byte bVar15;
  int iVar16;
  int iVar17;
  uint uVar18;
  uint uVar19;
  int iStack_f8;
  uint uStack_f4;
  int iStack_e4;
  undefined2 uStack_e0;
  ushort uStack_de;
  undefined2 uStack_dc;
  undefined2 uStack_da;
  undefined2 uStack_d8;
  undefined2 uStack_d6;
  undefined2 uStack_d4;
  undefined2 uStack_d2;
  undefined2 uStack_d0;
  undefined2 uStack_ce;
  undefined2 uStack_cc;
  undefined2 uStack_ca;
  undefined2 uStack_c8;
  undefined2 uStack_c6;
  undefined2 uStack_c4;
  undefined2 uStack_c2;
  undefined2 uStack_c0;
  undefined2 uStack_be;
  undefined2 uStack_bc;
  undefined2 uStack_ba;
  undefined2 uStack_b8;
  undefined2 uStack_b6;
  undefined2 uStack_b4;
  undefined2 uStack_b2;
  undefined2 uStack_b0;
  undefined2 uStack_ae;
  undefined2 uStack_ac;
  undefined2 uStack_aa;
  undefined2 uStack_a8;
  undefined2 uStack_a6;
  undefined2 uStack_a4;
  undefined2 uStack_a2;
  undefined2 uStack_a0;
  undefined2 uStack_9e;
  undefined2 uStack_9c;
  undefined2 uStack_9a;
  undefined2 uStack_98;
  undefined2 uStack_96;
  undefined1 auStack_94 [8];
  undefined1 auStack_8c [8];
  undefined1 auStack_84 [8];
  undefined1 auStack_7c [8];
  undefined1 auStack_74 [38];
  undefined2 uStack_4e;
  undefined2 uStack_4c;
  undefined4 uStack_48;
  undefined1 uStack_44;
  undefined1 uStack_43;
  undefined1 uStack_42;
  byte bStack_40;
  byte bStack_3f;
  byte bStack_3e;
  byte bStack_3d;
  byte bStack_3c;
  byte bStack_3b;
  byte bStack_3a;
  undefined1 uStack_39;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  int aiStack_2c [2];
  
  aiStack_2c[0] = 0;
  iVar17 = DAT_43856d30 + 0x438565c0;
  iVar16 = *(int *)(iVar17 + DAT_43856d34);
  if ((*(char *)(iVar16 + 0x10) == '\0') && (aiStack_2c[0] = FUN_439e25a4(), aiStack_2c[0] == 1)) {
    FUN_43857f40(0x24,1);
  }
  if (*(int *)(param_1 + 700) - 1U < 3) {
    cVar13 = *(char *)(**(int **)(iVar17 + DAT_43856d38) + 4);
LAB_4385666e:
    *(char *)(param_4 + 0xc35) = cVar13;
  }
  else {
    iVar7 = **(int **)(iVar17 + DAT_43856d38);
    *(undefined1 *)(param_4 + 0xc35) = *(undefined1 *)(iVar7 + 5);
    if ((*(char *)(iVar7 + 0x9c) != '\0') && (*(char *)(param_3 + 0xbd9) == '\n')) {
      *(char *)(param_4 + 0xc35) = *(char *)(iVar7 + 0x9c);
    }
    if ((*(char *)(iVar7 + 0x9d) != '\0') && (*(char *)(param_3 + 0xbd9) == '\x16')) {
      *(char *)(param_4 + 0xc35) = *(char *)(iVar7 + 0x9d);
    }
    if ((*(char *)(iVar7 + 0x9e) != '\0') &&
       ((*(char *)(param_3 + 0xbd9) == '\x18' || (*(char *)(param_3 + 0xbd9) == '\x14')))) {
      *(char *)(param_4 + 0xc35) = *(char *)(iVar7 + 0x9e);
    }
    if ((*(char *)(iVar7 + 0x9f) != '\0') &&
       ((*(char *)(param_3 + 0xbd9) == '\x19' || (*(char *)(param_3 + 0xbd9) == '\x15')))) {
      *(char *)(param_4 + 0xc35) = *(char *)(iVar7 + 0x9f);
    }
    if ((*(char *)(iVar7 + 0xa0) != '\0') && (*(char *)(param_3 + 0xbd9) == '\x1a')) {
      *(char *)(param_4 + 0xc35) = *(char *)(iVar7 + 0xa0);
    }
    cVar13 = *(char *)(iVar7 + 0xa1);
    if ((cVar13 != '\0') && (*(char *)(param_3 + 0xbd9) == '\x1b')) goto LAB_4385666e;
  }
  if ((*(int *)(param_1 + 0x2b4) == 0x1f) || (*(int *)(param_1 + 0x2b4) == 0x26)) {
    uVar12 = *(byte *)(iVar16 + 0x20) - 0x10 & 0xff;
    if (uVar12 < 4) {
      bVar15 = *(byte *)(DAT_43856d3c + 0x43856692 + uVar12);
    }
    else {
      bVar15 = 4;
    }
  }
  else {
    bVar15 = 0;
  }
  if (*(char *)(param_2 + 0x16) != '\0') {
    bVar15 = *(byte *)(param_2 + 0x17);
  }
  if (*(char *)(param_1 + 0xa6) == '\x01') {
    bVar15 = 3;
  }
  iVar16 = *(int *)(iVar17 + DAT_43856d40);
  if ((*(byte *)(iVar16 + 0x49) & 0x10) != 0) {
    bVar15 = *(byte *)(iVar16 + 0x49) & 0xf;
  }
  if (*(byte *)(param_4 + 0xc4c) < 3) {
    *(byte *)(param_4 + 0xc4c) = *(byte *)(param_4 + 0xc4c) + 1;
  }
  if (*(char *)(param_4 + 0xc4c) == '\x02') {
    *(uint *)(param_4 + 0xc40) = (uint)*(ushort *)(param_1 + 0x5b8) << 8;
    *(uint *)(param_4 + 0xc44) = (uint)*(ushort *)(param_1 + 0x5ba) << 8;
    *(uint *)(param_4 + 0xc48) = (uint)*(ushort *)(param_1 + 0x5bc) << 8;
  }
  FUN_43b09b26(&uStack_30,*(undefined4 *)(param_4 + 0xc40),*(undefined2 *)(param_1 + 0x5b8));
  FUN_43b09b26(&uStack_34,*(undefined4 *)(param_4 + 0xc44),*(undefined2 *)(param_1 + 0x5ba));
  FUN_43b09b26(&uStack_38,*(undefined4 *)(param_4 + 0xc48),*(undefined2 *)(param_1 + 0x5bc));
  *(undefined4 *)(param_4 + 0xc40) = uStack_30;
  *(undefined4 *)(param_4 + 0xc44) = uStack_34;
  *(undefined4 *)(param_4 + 0xc48) = uStack_38;
  switch(bVar15) {
  case 0:
    *(short *)(param_4 + 0xc38) = (short)((uint)uStack_30 >> 8);
    sVar5 = (short)((uint)uStack_38 >> 8);
    *(short *)(param_4 + 0xc3a) = (short)((uint)uStack_34 >> 8);
    break;
  case 1:
    uVar4 = *(undefined2 *)(param_1 + 0x5c0);
    sVar5 = *(short *)(param_1 + 0x5c2);
    *(undefined2 *)(param_4 + 0xc38) = *(undefined2 *)(param_1 + 0x5be);
    *(undefined2 *)(param_4 + 0xc3a) = uVar4;
    break;
  case 2:
    uVar4 = *(undefined2 *)(param_1 + 0x5b4);
    uVar2 = *(undefined2 *)(param_1 + 0x5b6);
    *(undefined2 *)(param_4 + 0xc38) = *(undefined2 *)(param_1 + 0x5b2);
    *(undefined2 *)(param_4 + 0xc3a) = uVar4;
    *(undefined2 *)(param_4 + 0xc3c) = uVar2;
    goto LAB_438567ac;
  default:
    sVar5 = *(short *)(param_1 + 0x5c4);
    *(short *)(param_4 + 0xc38) = sVar5;
    *(short *)(param_4 + 0xc3a) = sVar5;
    break;
  case 4:
    *(ushort *)(param_4 + 0xc38) = (ushort)*(byte *)(iVar16 + 0x28) << 3;
    *(ushort *)(param_4 + 0xc3a) = (ushort)*(byte *)(iVar16 + 0x29) << 3;
    sVar5 = (ushort)*(byte *)(iVar16 + 0x2a) << 3;
  }
  *(short *)(param_4 + 0xc3c) = sVar5;
LAB_438567ac:
  uVar1 = *(ushort *)(param_1 + 0x5c4);
  if (uVar1 == 0) {
    *(undefined2 *)(param_4 + 0xc38) = 0x100;
    *(undefined2 *)(param_4 + 0xc3a) = 0x100;
    *(undefined2 *)(param_4 + 0xc3c) = 0x100;
  }
  else {
    if (uVar1 < 0x101) {
      sVar5 = FUN_4355fd68(0x100);
      *(short *)(param_4 + 0xc38) = sVar5 * *(short *)(param_4 + 0xc38);
      *(short *)(param_4 + 0xc3a) = sVar5 * *(short *)(param_4 + 0xc3a);
      sVar5 = *(short *)(param_4 + 0xc3c) * sVar5;
    }
    else {
      uVar1 = uVar1 >> 8;
      uVar4 = FUN_4355faf0(*(undefined2 *)(param_4 + 0xc38),uVar1);
      *(undefined2 *)(param_4 + 0xc38) = uVar4;
      uVar4 = FUN_4355faf0(*(undefined2 *)(param_4 + 0xc3a),uVar1);
      *(undefined2 *)(param_4 + 0xc3a) = uVar4;
      sVar5 = FUN_4355faf0(*(undefined2 *)(param_4 + 0xc3c),uVar1);
    }
    *(short *)(param_4 + 0xc3c) = sVar5;
  }
  if (*(char *)(iVar16 + 0x2c) != '\0') {
    *(ushort *)(param_4 + 0xc38) = (ushort)*(byte *)(iVar16 + 0x28) << 3;
    *(ushort *)(param_4 + 0xc3a) = (ushort)*(byte *)(iVar16 + 0x29) << 3;
    *(ushort *)(param_4 + 0xc3c) = (ushort)*(byte *)(iVar16 + 0x2a) << 3;
  }
  if (*(char *)(param_2 + 0x6a) == '\x01') {
    *(undefined2 *)(param_4 + 0xc38) = 0;
    *(undefined2 *)(param_4 + 0xc3c) = 0;
  }
  *(byte *)(param_4 + 0xc36) = bVar15;
  uStack_48 = 0;
  uStack_44 = 0;
  uVar6 = FUN_439e2958();
  iVar7 = FUN_438563f4();
  iVar14 = *(int *)(iVar17 + DAT_43856d44);
  *(char *)(iVar14 + 0x8f0) = (char)uVar6;
  *(char *)(iVar14 + 0x8f1) = (char)iVar7;
  uVar3 = FUN_43856328(*(undefined1 *)(param_1 + 0x3b4),*(undefined1 *)(param_1 + 0x2b4));
  uStack_e0._0_1_ = 0x10;
  uStack_d6 = *(undefined2 *)(param_4 + 0xc3c);
  *(undefined1 *)(param_4 + 0xc4d) = uVar3;
  uStack_dc = *(undefined2 *)(param_4 + 0xc38);
  uStack_de = (ushort)*(byte *)(param_1 + 0x254);
  uStack_da = *(undefined2 *)(param_4 + 0xc3a);
  uStack_43 = *(undefined1 *)(param_4 + 0xc35);
  uStack_d8 = uStack_da;
  FUN_438563ac(iVar7,3,&uStack_d4);
  if (*(char *)(iVar16 + 0x10) == '\0') {
    uStack_d4 = *(undefined2 *)(iVar16 + 8);
    uStack_d2 = *(undefined2 *)(iVar16 + 10);
    uStack_d0 = *(undefined2 *)(iVar16 + 0xc);
    uStack_ce = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_43856344(iVar7,0,0,&uStack_cc);
  if (*(char *)(iVar16 + 0x10) == '\x01') {
    uStack_cc = *(undefined2 *)(iVar16 + 8);
    uStack_ca = *(undefined2 *)(iVar16 + 10);
    uStack_c8 = *(undefined2 *)(iVar16 + 0xc);
    uStack_c6 = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_43856344(iVar7,*(undefined1 *)(param_4 + 0xc4d),0,&uStack_c4);
  if (*(char *)(iVar16 + 0x10) == '\x02') {
    uStack_c4 = *(undefined2 *)(iVar16 + 8);
    uStack_c2 = *(undefined2 *)(iVar16 + 10);
    uStack_c0 = *(undefined2 *)(iVar16 + 0xc);
    uStack_be = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_43856344(iVar7,*(undefined1 *)(param_4 + 0xc4d),1,&uStack_bc);
  if (*(char *)(iVar16 + 0x10) == '\x03') {
    uStack_bc = *(undefined2 *)(iVar16 + 8);
    uStack_ba = *(undefined2 *)(iVar16 + 10);
    uStack_b8 = *(undefined2 *)(iVar16 + 0xc);
    uStack_b6 = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_43856344(iVar7,*(undefined1 *)(param_4 + 0xc4d),2,&uStack_b4);
  if (*(char *)(param_4 + 0xc4d) == '\x03') {
    FUN_43856408(uVar6,&uStack_b4);
  }
  cVar13 = *(char *)(iVar16 + 0x10);
  if (cVar13 == '\x04') {
    uStack_b4 = *(undefined2 *)(iVar16 + 8);
    uStack_b2 = *(undefined2 *)(iVar16 + 10);
    uStack_b0 = *(undefined2 *)(iVar16 + 0xc);
    uStack_ae = *(undefined2 *)(iVar16 + 0xe);
  }
  if (iVar7 == 0) {
    iStack_e4 = 0xf0;
    iStack_f8 = 0x140;
  }
  else if (iVar7 == 1) {
    iStack_e4 = 0xf0;
    iStack_f8 = 0x160;
  }
  else {
    iStack_e4 = 0xd0;
    iStack_f8 = 0x180;
  }
  uStack_f4 = (uint)*(ushort *)(param_1 + 0x2e0);
  uVar18 = (uint)*(ushort *)(param_1 + 0x2de);
  uVar12 = iStack_f8 * 0x33;
  if (((*(int *)(param_1 + 0x634) != 0) &&
      (uVar8 = FUN_4355faf0(*(int *)(param_1 + 0x630) << 8), 0x100 < uVar8)) &&
     (*(int *)(param_1 + 0x4f8) == 2)) {
    uVar12 = FUN_4355faf0(iStack_f8 * 0x3300,uVar8);
    if (uVar18 < 0x140) {
      iVar14 = FUN_4355faf0((0x140 - uVar18) * 0x100,uVar8);
      iVar14 = -iVar14;
    }
    else {
      iVar14 = FUN_4355faf0((uVar18 - 0x140) * 0x100,uVar8);
    }
    uVar18 = iVar14 + 0x140U & 0xffff;
    if (uStack_f4 < 0xf0) {
      sVar5 = FUN_4355faf0((0xf0 - uStack_f4) * 0x100,uVar8);
      sVar5 = -sVar5;
    }
    else {
      sVar5 = FUN_4355faf0((uStack_f4 - 0xf0) * 0x100,uVar8);
    }
    uStack_f4 = (uint)(ushort)(sVar5 + 0xf0);
  }
  uVar19 = uVar12 >> 1;
  iStack_f8 = iStack_f8 * 0x100;
  uVar18 = FUN_4355fd68(iStack_f8 * uVar18,0x280);
  iStack_e4 = iStack_e4 * 0x100;
  uVar8 = FUN_4355fd68(iStack_e4 * uStack_f4,0x1e0);
  if (uVar18 < uVar19) {
    iVar14 = 0;
  }
  else {
    if (iStack_f8 - uVar19 < uVar18) {
      iStack_f8 = iStack_f8 - uVar12;
    }
    else {
      iStack_f8 = uVar18 - uVar19;
    }
    iVar14 = FUN_43b09b36(iStack_f8);
  }
  if (uVar8 < uVar19) {
    iVar9 = 0;
  }
  else {
    if (iStack_e4 - uVar19 < uVar8) {
      iStack_e4 = iStack_e4 - uVar12;
    }
    else {
      iStack_e4 = uVar8 - uVar19;
    }
    iVar9 = FUN_43b09b36(iStack_e4);
  }
  uStack_ac = (undefined2)((uint)iVar14 >> 8);
  uStack_aa = (undefined2)((uint)iVar9 >> 8);
  uStack_a6 = (undefined2)(iVar9 + uVar12 >> 8);
  uStack_a8 = (undefined2)(iVar14 + uVar12 >> 8);
  if (cVar13 == '\x05') {
    uStack_ac = *(undefined2 *)(iVar16 + 8);
    uStack_aa = *(undefined2 *)(iVar16 + 10);
    uStack_a8 = *(undefined2 *)(iVar16 + 0xc);
    uStack_a6 = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_438563ac(iVar7,1,&uStack_a4);
  if (*(char *)(param_2 + 0x68) == '\x02') {
    FUN_438564ac(*(undefined4 *)(param_1 + 0x3f0),&uStack_a4);
  }
  if (*(char *)(param_2 + 0x35) != '\0') {
    FUN_438563ac(iVar7,2,&uStack_a4);
  }
  if (*(char *)(iVar16 + 0x10) == '\x06') {
    uStack_a4 = *(undefined2 *)(iVar16 + 8);
    uStack_a2 = *(undefined2 *)(iVar16 + 10);
    uStack_a0 = *(undefined2 *)(iVar16 + 0xc);
    uStack_9e = *(undefined2 *)(iVar16 + 0xe);
  }
  if ((*(char *)(param_2 + 0x68) == '\x01') || (**(char **)(iVar17 + DAT_43856d48) == '\x01')) {
    FUN_438563ac(iVar7,0,&uStack_9c);
    FUN_438564ac(*(undefined4 *)(param_1 + 0x3f0),&uStack_9c);
  }
  else {
    FUN_43856344(iVar7,3,2,&uStack_9c);
    FUN_43856408(uVar6,&uStack_9c);
  }
  if (*(char *)(iVar16 + 0x10) == '\a') {
    uStack_9c = *(undefined2 *)(iVar16 + 8);
    uStack_9a = *(undefined2 *)(iVar16 + 10);
    uStack_98 = *(undefined2 *)(iVar16 + 0xc);
    uStack_96 = *(undefined2 *)(iVar16 + 0xe);
  }
  FUN_43856344(iVar7,2,1,auStack_94);
  FUN_43856344(iVar7,2,1,auStack_8c);
  FUN_43856344(iVar7,2,1,auStack_84);
  FUN_43856344(iVar7,2,1,auStack_7c);
  FUN_43856344(iVar7,2,1,auStack_74);
  puVar11 = &uStack_e0;
  do {
    puVar11[0x3a] = 0x30;
    puVar11[0x3b] = 0x50;
    puVar11[0x3c] = 0x50;
    puVar11 = puVar11 + 3;
  } while (puVar11 != &uStack_c2);
  uStack_4e = 0x7aa;
  uStack_4c = 0x10;
  uVar12 = (uint)**(byte **)(iVar17 + DAT_43856d4c);
  if (uVar12 == 0) {
    uVar12 = (uint)*(byte *)(iVar16 + 0x38);
  }
  bStack_40 = (byte)uVar12 & 1;
  bStack_3f = (byte)((int)uVar12 >> 1) & 1;
  bStack_3e = (byte)((int)uVar12 >> 2) & 1;
  bStack_3d = (byte)((int)uVar12 >> 3) & 1;
  bStack_3c = (byte)((int)uVar12 >> 4) & 1;
  bStack_3b = (byte)((int)uVar12 >> 5) & 1;
  uStack_39 = (undefined1)(uVar12 >> 7);
  bStack_3a = (byte)((int)uVar12 >> 6) & 1;
  if ((*(char *)(iVar16 + 0x58) != '\0') || (**(char **)(iVar17 + DAT_43856d50) != '\0')) {
    thunk_FUN_439ecaac(&bStack_40);
  }
  uStack_42 = (undefined1)*(undefined4 *)(param_1 + 0x3b4);
  uVar6 = *(undefined4 *)(iVar17 + DAT_43856d54);
  FUN_439c5320(uVar6,&uStack_e0,0xa0);
  thunk_FUN_439ec7e8(uVar6);
  uVar3 = *(undefined1 *)(param_4 + 0xc35);
  bVar15 = *(byte *)(param_1 + 0x254);
  if ((*(byte *)(iVar16 + 0x39) & 0x10) != 0) {
    thunk_FUN_439eaeb0(*(byte *)(iVar16 + 0x39) & 3);
  }
  puVar10 = *(undefined1 **)(iVar17 + DAT_43856d58);
  *puVar10 = uVar3;
  puVar10[1] = 0;
  *(uint *)(puVar10 + 4) = (uint)bVar15;
  thunk_FUN_439ead50();
  uVar4 = *(undefined2 *)(param_4 + 0xc3c);
  puVar11 = *(undefined2 **)(iVar17 + DAT_43856d5c);
  bVar15 = *(byte *)(param_1 + 0x254);
  uVar2 = *(undefined2 *)(param_4 + 0xc38);
  puVar11[1] = *(undefined2 *)(param_4 + 0xc3a);
  puVar11[2] = uVar4;
  *puVar11 = uVar2;
  *(uint *)(puVar11 + 4) = (uint)bVar15;
  thunk_FUN_439ead14();
  FUN_439e2740(aiStack_2c);
  return;
}


/* 4384b268 */

void FUN_4384b268(undefined4 param_1,uint *param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7,undefined1 *param_8,undefined4 param_9,undefined4 param_10,int param_11
                 ,int param_12,int param_13,short *param_14,int param_15,undefined4 param_16,
                 short *param_17)

{
  byte bVar1;
  char cVar2;
  ushort uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  int iVar6;
  undefined1 uVar7;
  char cVar8;
  short sVar9;
  short sVar10;
  undefined2 uVar11;
  uint uVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  undefined4 *puVar16;
  undefined2 *puVar17;
  byte bVar18;
  byte bVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  byte bVar23;
  byte bVar24;
  byte bVar25;
  byte bVar26;
  byte bVar27;
  ushort uVar28;
  uint uVar29;
  undefined4 uVar30;
  ushort *puVar31;
  byte bVar32;
  char cVar33;
  ushort uVar34;
  int iVar35;
  undefined4 uVar36;
  undefined1 *puVar37;
  uint uVar38;
  uint uVar39;
  uint uVar40;
  uint uVar41;
  uint uVar42;
  uint uVar43;
  uint uVar44;
  uint uVar45;
  uint uVar46;
  uint uVar47;
  uint uVar48;
  undefined4 uVar49;
  char cVar50;
  int *piVar51;
  char *pcVar52;
  int iVar53;
  uint uVar54;
  bool bVar55;
  uint uStack_510;
  uint uStack_50c;
  uint uStack_508;
  uint uStack_504;
  uint uStack_500;
  uint uStack_4fc;
  uint uStack_4f8;
  uint uStack_4f4;
  int iStack_4f0;
  int iStack_4ec;
  uint uStack_4e8;
  uint uStack_4e0;
  uint uStack_4dc;
  uint uStack_4d4;
  uint uStack_4cc;
  uint uStack_4a8;
  undefined1 auStack_47c [776];
  undefined1 auStack_174 [112];
  undefined1 auStack_104 [36];
  int iStack_e0;
  int iStack_d0;
  int iStack_c8;
  undefined1 auStack_bc [28];
  undefined1 uStack_a0;
  short asStack_74 [2];
  short sStack_70;
  ushort uStack_6e;
  ushort uStack_6c;
  undefined1 uStack_6a;
  char cStack_69;
  undefined1 uStack_68;
  undefined1 uStack_67;
  char cStack_66;
  undefined1 uStack_65;
  undefined1 uStack_64;
  undefined1 uStack_63;
  undefined1 uStack_62;
  undefined1 uStack_61;
  undefined1 uStack_60;
  undefined1 uStack_5f;
  undefined1 uStack_5e;
  undefined1 uStack_5d;
  undefined1 uStack_5c;
  undefined1 uStack_5b;
  undefined1 uStack_5a;
  char cStack_59;
  undefined1 uStack_57;
  undefined1 uStack_56;
  undefined1 uStack_55;
  byte bStack_54;
  byte bStack_53;
  char cStack_52;
  undefined1 uStack_51;
  bool bStack_50;
  byte bStack_4f;
  bool bStack_4e;
  undefined1 auStack_4c [12];
  int iStack_40;
  undefined4 *puStack_3c;
  uint uStack_38;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  ushort uStack_2c;
  ushort auStack_2a [3];
  
  iVar53 = DAT_4384bda8 + 0x4384b284;
  sVar9 = *(short *)((int)param_2 + 0x52);
  *(uint *)(param_17 + 2) = *param_2;
  uVar12 = param_2[0x15];
  uVar29 = param_2[0x47];
  *param_17 = (short)param_2[0x14];
  param_17[10] = 0x4000;
  param_17[0xb] = sVar9;
  param_17[0xc] = (short)uVar12;
  param_17[0xd] = (short)uVar29;
  FUN_439c5320(param_17 + 0xe,(int)param_2 + 0x56,0xc6);
  sVar9 = *(short *)((int)param_2 + 0x3a);
  uVar12 = param_2[0xf];
  *(uint *)(param_17 + 0x74) = param_2[0x10];
  param_17[4] = 0;
  *(undefined1 *)(param_17 + 5) = 0;
  *(undefined1 *)((int)param_17 + 0xb) = 0;
  iVar20 = DAT_4384bdac;
  param_17[0x72] = sVar9;
  param_17[0x73] = (short)uVar12;
  iVar20 = *(int *)(iVar53 + iVar20);
  cVar33 = *(char *)(iVar20 + 0x86);
  if ((cVar33 == '\x01') || ((cVar33 != '\0' && (cVar33 == '\x02')))) {
    *(char *)(param_17 + 6) = cVar33;
  }
  else {
    *(undefined1 *)(param_17 + 6) = 0;
  }
  if (*(char *)(iVar20 + 5) == '\x01') {
    if ((*(char *)(*(int *)(iVar53 + DAT_4384bdb0) + 0x1c) == '\x01') &&
       (*(char *)(param_5 + 0xec) != '\x01')) {
LAB_4384b31a:
      uVar7 = 0;
    }
    else {
      if (*(char *)(param_5 + 0xd4) != '\x01') goto LAB_4384b35a;
      uVar7 = 1;
      if (*(char *)(param_5 + 0xd0) == '\x01') goto LAB_4384b31a;
    }
    *(undefined1 *)(param_17 + 5) = uVar7;
  }
  else if (*(char *)(iVar20 + 5) == '\x02') {
    if (*(char *)(param_5 + 0xd4) == '\x01') {
      *(bool *)(param_17 + 5) = *(char *)(param_5 + 0xd0) != '\x01';
    }
    *(bool *)((int)param_17 + 0xb) = *(char *)(param_5 + 0xd1) != '\x01';
  }
LAB_4384b35a:
  *(char *)((int)param_14 + 0x6b1) = (char)param_17[5];
  iVar21 = DAT_4384bdb4;
  param_17[0x76] = *(short *)(param_7 + 0x434);
  piVar51 = *(int **)(iVar53 + iVar21);
  sVar9 = FUN_43b074e4(*(undefined1 *)(*piVar51 + 0x180));
  iVar21 = DAT_4384bdb8;
  param_17[0x3cf] = sVar9;
  *(undefined1 *)(param_17 + 0x3e6) = *(undefined1 *)(*(int *)(iVar53 + iVar21) + 0x9e);
  sVar9 = *(short *)(param_8 + 0x4c2);
  param_17[0x3db] = *(short *)(param_8 + 0x4c4);
  param_17[0x3dc] = sVar9;
  uVar7 = FUN_438d7a6c();
  *(undefined1 *)((int)param_17 + 0x7bd) = uVar7;
  uVar7 = FUN_43b07384(param_14);
  iVar21 = DAT_4384bdbc;
  *(undefined1 *)(param_17 + 0x3df) = uVar7;
  uVar12 = FUN_43b074ac(*(undefined1 *)(*(int *)(iVar53 + iVar21) + 0x48));
  *(bool *)(param_17 + 0x3dd) = *(ushort *)(param_3 + 0x164) < uVar12;
  *(char *)((int)param_17 + 0x7bb) = (char)param_14[0x36a];
  *(char *)(param_17 + 0x3de) = (char)param_14[0x36f];
  FUN_439c5320(param_17 + 0x78,param_15 + 0x334,0x4a4);
  *(undefined1 *)(param_17 + 0x3e2) = *(undefined1 *)((int)param_14 + 0xb);
  if ((char)param_14[0x351] == '\0') {
    if (0xfd < *(byte *)((int)param_14 + 0x6d7)) {
      uVar7 = 1;
      goto LAB_4384b422;
    }
  }
  else if (*(byte *)((int)param_14 + 0x6d7) < 0xef) {
    uVar7 = 0;
LAB_4384b422:
    *(undefined1 *)(param_14 + 0x351) = uVar7;
  }
  *(char *)((int)param_17 + 0x7bf) = (char)param_14[0x351];
  if (*(char *)(param_5 + 0x11d) == '\x01') {
    uVar12 = (uint)*(byte *)(param_5 + 0xeb);
    if (uVar12 == 1) {
      if (*(int *)(param_14 + 0x1a6) == 0) {
        uVar12 = 0;
      }
    }
    else {
LAB_4384b464:
      if (uVar12 != 2) goto LAB_4384b468;
    }
  }
  else {
    if ((*(char *)(param_5 + 0xec) == '\x01') &&
       (*(char *)(*(int *)(iVar53 + DAT_4384bdc0) + 8) == '\x01')) {
      uVar12 = (uint)*(byte *)(param_5 + 0xeb);
      goto LAB_4384b464;
    }
LAB_4384b468:
    uVar12 = 0;
  }
  *(uint *)(param_17 + 0x3e0) = uVar12;
  sVar9 = *(short *)(param_15 + 0xc3c);
  param_17[0x3e3] = *(short *)(param_15 + 0xc38);
  param_17[0x3e4] = sVar9;
  FUN_439c5320(param_17 + 0x2ca,param_8 + 4,0x80);
  FUN_439c5320(param_17 + 0x30a,param_8 + 0xa4,0x80);
  FUN_439c5320(param_17 + 0x38a,param_8 + 0x2b0,0x80);
  FUN_439c5320(param_17 + 0x34a,param_8 + 0x350,0x80);
  *(undefined1 *)((int)param_17 + 0x7cb) = *(undefined1 *)(param_5 + 0xec);
  uVar12 = param_2[0x4e];
  sVar9 = *(short *)((int)param_2 + 0x12e);
  uVar29 = param_2[0x13];
  uVar13 = param_2[0x12];
  *(char *)(param_17 + 0x3e5) = (char)*(undefined4 *)(param_14 + 0x15e);
  iVar21 = DAT_4384bdc4;
  param_17[0x3d5] = (short)uVar12;
  param_17[0x3d6] = sVar9;
  param_17[0x3d8] = (short)uVar29;
  param_17[7] = (short)uVar13;
  if (**(char **)(iVar53 + iVar21) == '\0') {
    uVar12 = FUN_43b07522(*(undefined2 *)(param_3 + 0x164));
    if ((*(int *)(param_14 + 0x15a) == 6) && (*(char *)(iVar20 + 9) == '\0')) {
      if (uVar12 < 0xe00) {
        uVar7 = 4;
      }
      else if ((uVar12 - 0xe00 & 0xffff) < 0x100) {
        uVar7 = 2;
      }
      else {
        uVar7 = 1;
      }
    }
    else if (*(int *)(param_14 + 0x19e) == 1) {
      uVar7 = 0xc;
    }
    else {
      uVar7 = 4;
    }
    *(undefined1 *)(param_17 + 0x3ca) = uVar7;
    cVar33 = **(char **)(iVar53 + DAT_4384bdc8);
    if (cVar33 != '\0') goto LAB_4384b55a;
  }
  else {
    cVar33 = '\x04';
LAB_4384b55a:
    *(char *)(param_17 + 0x3ca) = cVar33;
  }
  *(char *)(param_14 + 0x358) = (char)param_17[0x3ca];
  iVar21 = DAT_4384bdcc;
  iVar35 = *piVar51;
  *(bool *)((int)param_17 + 0x795) = *(ushort *)(param_3 + 0x164) <= *(ushort *)(iVar35 + 0xb0);
  uVar7 = *(undefined1 *)((int)param_17 + 0x795);
  iVar21 = *(int *)(iVar53 + iVar21);
  *(undefined1 *)(iVar21 + 0x608) = uVar7;
  *(undefined1 *)(param_14 + 0x136) = uVar7;
  if (*(ushort *)(iVar35 + 0x17e) == 0) {
    uVar7 = *(undefined1 *)((int)param_17 + 0x795);
  }
  else if (*(ushort *)(iVar35 + 0x17e) + 0x100 < (uint)*(ushort *)(param_3 + 0x164)) {
    uVar7 = 0;
  }
  else {
    uVar7 = 1;
  }
  *(undefined1 *)(param_17 + 0x3ce) = uVar7;
  *(char *)(iVar21 + 0x60a) = (char)param_17[0x3ce];
  uVar34 = *(ushort *)(iVar35 + 0xb0);
  if ((((*(ushort *)(iVar35 + 0x17e) == 0) ||
       (*(ushort *)(iVar35 + 0x17e) < *(ushort *)(param_3 + 0x164))) || (uVar34 == 0)) ||
     (*(ushort *)(param_3 + 0x164) <= uVar34)) {
    if ((uVar34 == 0) || (uVar34 < *(ushort *)(param_3 + 0x164))) {
      uVar36 = 0;
    }
    else {
      uVar36 = 1;
    }
  }
  else {
    uVar36 = 2;
  }
  *(undefined4 *)(param_17 + 0x3cc) = uVar36;
  uVar36 = *(undefined4 *)(param_17 + 0x3cc);
  *(char *)(iVar21 + 0x609) = (char)uVar36;
  sVar9 = param_14[0x115];
  sVar10 = param_14[0x30e];
  uVar11 = *(undefined2 *)(param_3 + 0x18a);
  *(undefined4 *)(param_14 + 0x138) = uVar36;
  uVar7 = FUN_43b095b0((char)sVar9,(char)sVar10,uVar11,*(undefined4 *)(param_4 + 700));
  *(undefined1 *)((int)param_14 + 0x61d) = uVar7;
  uVar7 = FUN_43b095b0((char)sVar9,(char)sVar10,*(undefined2 *)(param_3 + 0x192),
                       *(undefined4 *)(param_4 + 700));
  *(undefined1 *)(param_14 + 0x30f) = uVar7;
  if (*param_14 == 0x389) {
    param_14[0x2e3] = param_14[0x8c];
    param_14[0x2e4] = param_14[0x8d];
    param_14[0x2e5] = param_14[0x8e];
    param_14[0x2e6] = param_14[0x8f];
  }
  uVar12 = (uint)(ushort)param_2[0x49] - (uint)*(ushort *)((int)param_2 + 0x126);
  if ((int)uVar12 < 0) {
    uVar12 = -uVar12;
  }
  uVar29 = (uint)(ushort)param_2[0x4b] - (uint)(ushort)param_2[0x4d];
  uVar7 = (undefined1)param_14[0x366];
  if ((int)uVar29 < 0) {
    uVar29 = -uVar29;
  }
  if (((uVar12 & 0xffff) < 0x2a) && ((uVar29 & 0xffff) < 0x2a)) {
    if (*(char *)((int)param_14 + 0x6cd) != -1) {
      *(char *)((int)param_14 + 0x6cd) = *(char *)((int)param_14 + 0x6cd) + '\x01';
    }
    if (0x45 < *(byte *)((int)param_14 + 0x6cd)) {
      uVar7 = 1;
    }
  }
  else {
    uVar7 = 0;
    *(undefined1 *)((int)param_14 + 0x6cd) = 0;
  }
  *(undefined1 *)(param_14 + 0x366) = uVar7;
  *(undefined1 *)((int)param_17 + 0x79d) = uVar7;
  *(short *)(iVar21 + 0x362) = (short)uVar12;
  *(short *)(iVar21 + 0x364) = (short)uVar29;
  FUN_439c5320(param_14 + 0x28,param_3 + 0x124,0x12);
  uVar7 = FUN_43b09634(param_14);
  *(undefined1 *)(param_14 + 0x2e) = uVar7;
  if (*(int *)(param_14 + 0x27c) == 2) {
    bVar55 = *(char *)((int)param_14 + 0x54f) == '\x01';
    iVar35 = FUN_436e8328();
    if ((iVar35 == 2) && (iVar35 = FUN_43b09420(param_14), iVar35 == 0)) {
      bVar55 = *(char *)(param_3 + 0x127) == '\0' || bVar55;
    }
  }
  else {
    bVar55 = false;
  }
  *(bool *)((int)param_14 + 0x5d) = bVar55;
  iVar35 = FUN_43b09420(param_14);
  if (iVar35 == 0) {
LAB_4384b7a2:
    uVar7 = 1;
  }
  else if (*(char *)((int)param_14 + 0x54f) == '\x01') {
    uVar7 = 0;
  }
  else {
    if (((char)param_14[0x2c4] == '\0') && (iVar35 = FUN_436e8328(), iVar35 != 2))
    goto LAB_4384b7a2;
    cVar33 = *(char *)(param_3 + 0x125);
    if ((cVar33 == '\x04') &&
       ((*(char *)((int)param_14 + 0x30f) != '\0' || (*(char *)((int)param_14 + 0x85) != '\0')))) {
      puVar37 = (undefined1 *)(DAT_4384bdd0 + 0x4384b74c);
LAB_4384b76c:
      uVar7 = 0;
LAB_4384b780:
      *puVar37 = uVar7;
    }
    else {
      if ((char)param_14[0x42] == '\x01') {
        uVar7 = 0;
        puVar37 = (undefined1 *)(DAT_4384bdd4 + 0x4384b75e);
        goto LAB_4384b780;
      }
      if ((byte)(cVar33 - 5U) < 2) {
        puVar37 = (undefined1 *)(DAT_4384bdd8 + 0x4384b76e);
        goto LAB_4384b76c;
      }
      if ((cVar33 != '\x01') && (cVar33 != '\x03')) {
        uVar7 = 1;
        puVar37 = (undefined1 *)(DAT_4384bddc + 0x4384b782);
        goto LAB_4384b780;
      }
    }
    uVar7 = *(undefined1 *)(DAT_4384bde0 + 0x4384b78a);
    iVar35 = FUN_436e8328();
    if ((iVar35 == 2) && (*(char *)(iVar20 + 0x18) == '\0')) {
      uVar7 = 1;
    }
  }
  *(undefined1 *)(param_14 + 0x2f) = uVar7;
  if ((*(int *)(param_14 + 0x27c) == 1) && (*(int *)(param_14 + 0x280) == 5)) {
    sVar9 = FUN_436f0174();
    param_17[0x3d0] = sVar9 + 0x1000;
    sVar9 = FUN_436f01f8();
    param_17[0x3d2] = 0x1155;
    param_17[0x3d3] = 0x1000;
    param_17[0x3d1] = sVar9;
  }
  param_17[0x3d4] = *(short *)(param_3 + 0x29c);
  if (*(uint *)(param_14 + 0x27c) < 2) {
    uVar7 = *(undefined1 *)(param_3 + 0x1a);
  }
  else {
    uVar7 = (undefined1)param_14[0x2f];
  }
  *(undefined1 *)(param_14 + 0x25) = uVar7;
  cVar33 = (char)param_14[4];
  if ((byte)(cVar33 - 2U) < 2) {
LAB_4384b842:
    iVar35 = param_3 + 0x19e;
LAB_4384b848:
    FUN_439c5320(param_14 + 0x71,iVar35,8);
  }
  else {
    if (cVar33 != '\x04') {
      if (cVar33 == '\x05') goto LAB_4384b82e;
      if ((cVar33 != '\x06') && (cVar33 != '\f')) goto LAB_4384b842;
      iVar35 = param_3 + 0x13e;
      goto LAB_4384b848;
    }
    FUN_439c5320(param_14 + 0x71,param_3 + 0x1a6,8);
    if (*(char *)((int)param_14 + 0x625) == '\0') {
      if (*(char *)(iVar20 + 0x7b) == '\x01') goto LAB_4384b842;
LAB_4384b82e:
      iVar35 = param_3 + 0x1ae;
      goto LAB_4384b848;
    }
  }
  FUN_439c5320(param_14 + 0x3ba,param_14 + 0x71,8);
  if (*(char *)(iVar20 + 0xca) == '\x01') {
    cVar33 = (char)param_14[4];
    if ((byte)(cVar33 - 2U) < 2) {
LAB_4384b89c:
      iVar20 = param_3 + 0x218;
    }
    else if (cVar33 == '\x04') {
      iVar20 = param_3 + 0x220;
    }
    else {
      if (((cVar33 != '\x05') && (cVar33 != '\x06')) && (cVar33 != '\f')) goto LAB_4384b89c;
      iVar20 = param_3 + 0x228;
    }
    FUN_439c5320(param_14 + 0x3ba,iVar20 + 6,8);
  }
  uVar36 = *(undefined4 *)(param_14 + 0x3bc);
  *(undefined4 *)(iVar21 + 0xcc4) = *(undefined4 *)(param_14 + 0x3ba);
  *(undefined4 *)(iVar21 + 0xcc8) = uVar36;
  *(undefined1 *)(param_14 + 0x226) = *(undefined1 *)(param_3 + 0x11c);
  *(bool *)((int)param_14 + 0x47d) = *(short *)(param_3 + 0xe6) != 0;
  if ((char)param_14[0x21a] == '\x01') {
    if ((char)param_14[0x115] == '\0') {
      uVar12 = 0x3c;
    }
    else {
      uVar12 = 0x32;
    }
    if ((uint)*(byte *)((int)param_14 + 0x2d9) < uVar12 >> 1) {
      *(undefined1 *)((int)param_14 + 0x44d) = 1;
    }
    else if ((uVar12 <= *(byte *)((int)param_14 + 0x2d9)) ||
            (((char)param_14[0x16d] == '\x01' && ((char)param_2[0x50] != '\0')))) {
      *(undefined1 *)((int)param_14 + 0x44d) = 0;
    }
    if (((char)param_14[4] != '\x03') && (*(char *)((int)param_14 + 0x44d) == '\x01'))
    goto LAB_4384b922;
  }
  else {
LAB_4384b922:
    *(undefined1 *)((int)param_14 + 0x44d) = 0;
  }
  uVar34 = *(ushort *)(param_3 + 0x6c);
  uVar28 = *(ushort *)(param_3 + 0x6e);
  uVar12 = param_2[0x4c];
  iVar20 = FUN_43b07780(*(undefined4 *)(param_14 + 0x15a),*(undefined4 *)(param_14 + 0x194));
  if (iVar20 == 2) {
    iVar20 = 0x1d6;
  }
  else {
    iVar20 = 0x80;
  }
  if (((int)(uint)(ushort)uVar12 < (int)((uint)uVar34 - iVar20)) ||
     (iVar20 + (uint)uVar28 < (uint)(ushort)uVar12)) {
    uVar7 = 1;
  }
  else {
    uVar7 = 0;
  }
  *(undefined1 *)(param_14 + 0x239) = uVar7;
  if ((*(int *)(param_14 + 0x15a) == 0x17) ||
     (iVar20 = FUN_4382fe08(*(undefined2 *)(param_3 + 0x152)), iVar20 == 1)) {
    *(undefined1 *)(param_14 + 0x239) = 0;
  }
  if (((char)param_14[4] != '\x05') || (*(char *)(param_5 + 0xd4) != '\0')) {
    *(undefined1 *)(param_14 + 0x239) = 0;
  }
  *(char *)(iVar21 + 0x3e9) = (char)param_14[0x239];
  *(undefined1 *)((int)param_14 + 0x473) = 0;
  *(undefined1 *)(param_14 + 0x23a) = 0;
  *(undefined1 *)((int)param_14 + 0x475) = 0;
  if ((*(int *)(param_14 + 0x14a) == 9) ||
     ((*(int *)(param_14 + 0x14a) == 0x12 &&
      ((*(int *)(param_14 + 0x328) == 5 || (*(int *)(param_14 + 0x328) == 7)))))) {
    bVar55 = *(short *)(param_12 + 0x90) != 0;
    iVar20 = FUN_43b07780(*(undefined4 *)(param_14 + 0x15a),*(undefined4 *)(param_14 + 0x194));
    if (iVar20 == 0) {
      if ((((ushort)param_2[0x4c] < *(ushort *)(param_3 + 0x6c)) ||
          (*(ushort *)(param_3 + 0x6e) < (ushort)param_2[0x4c])) || (bVar55)) {
switchD_4384ba74_caseD_4:
LAB_4384baa8:
        *(undefined1 *)((int)param_14 + 0x473) = 1;
        goto LAB_4384baac;
      }
    }
    else if (bVar55) {
      *(undefined1 *)((int)param_14 + 0x473) = 1;
      *(undefined1 *)(param_14 + 0x23a) = 1;
    }
    goto LAB_4384bab0;
  }
  iVar20 = FUN_43b09420(param_14);
  if (iVar20 == 0) {
    uVar34 = *(ushort *)(param_3 + 0x28e);
    uVar28 = *(ushort *)(param_3 + 0x6c);
    uVar3 = *(ushort *)(param_3 + 0x6e);
  }
  else {
    uVar34 = *(ushort *)(param_3 + 0x290);
    uVar28 = *(ushort *)(param_3 + 0x60);
    uVar3 = *(ushort *)(param_3 + 0x62);
  }
  if ((uVar28 <= uVar34) && (uVar34 <= uVar3)) goto LAB_4384bab0;
  iVar20 = *(int *)(param_14 + 0x15a);
  if (*(char *)(param_5 + 2) == '\x01') {
    if (iVar20 == 2) {
      if (uVar3 <= uVar34) {
        *(undefined1 *)((int)param_14 + 0x473) = 1;
      }
    }
    else if (iVar20 == 5) {
      if (((char)param_14[0x171] != '\0') && (uVar3 <= uVar34)) {
        *(undefined1 *)(param_14 + 0x23a) = 1;
      }
    }
    else if ((iVar20 == 1) && (uVar3 <= uVar34)) {
      *(undefined1 *)(param_14 + 0x23a) = 1;
    }
    goto LAB_4384bab0;
  }
  switch(iVar20) {
  case 1:
    goto LAB_4384baac;
  case 2:
    *(undefined1 *)((int)param_14 + 0x473) = 1;
    break;
  case 3:
    iVar20 = FUN_43b07780(iVar20,*(undefined4 *)(param_14 + 0x194));
    if (iVar20 == 1) {
      *(undefined1 *)((int)param_14 + 0x475) = 1;
    }
    break;
  default:
    goto switchD_4384ba74_caseD_4;
  case 5:
    if ((char)param_14[0x171] == '\0') goto LAB_4384baa8;
LAB_4384baac:
    *(undefined1 *)(param_14 + 0x23a) = 1;
  }
LAB_4384bab0:
  if ((*(int *)(param_14 + 0x15a) == 0x17) ||
     (iVar20 = FUN_4382fe08(*(undefined2 *)(param_3 + 0x152)), iVar20 == 1)) {
    *(undefined1 *)((int)param_14 + 0x473) = 0;
    *(undefined1 *)(param_14 + 0x23a) = 0;
    *(undefined1 *)((int)param_14 + 0x475) = 0;
  }
  *(undefined1 *)(iVar21 + 0x5df) = *(undefined1 *)((int)param_14 + 0x473);
  *(char *)(iVar21 + 0x5e0) = (char)param_14[0x23a];
  *(undefined1 *)(iVar21 + 0x5e1) = *(undefined1 *)((int)param_14 + 0x475);
  if ((char)param_14[0x1ee] == '\x01') {
    *(undefined1 *)(param_14 + 0x23f) = *(undefined1 *)(DAT_4384bde4 + 0x4384baf8);
  }
  else {
    sVar9 = 0;
    *(undefined1 *)(param_14 + 0x23f) = 0;
    uVar34 = (ushort)param_2[0x4b];
    uVar28 = *(ushort *)(param_3 + 0x5c);
    if ((uVar34 < uVar28) || (uVar28 = *(ushort *)(param_3 + 0x5e), uVar28 < uVar34)) {
      sVar9 = uVar34 - uVar28;
    }
    if ((short)param_2[0x12] == -0x800) {
LAB_4384bbbc:
      if (*(char *)(param_5 + 2) == '\0') {
LAB_4384bbcc:
        *(undefined1 *)(param_14 + 0x23f) = 1;
      }
    }
    else {
      if ((short)param_2[0x12] == 0x800) goto LAB_4384bbcc;
      iVar20 = FUN_43b07780(*(undefined4 *)(param_14 + 0x15a),*(undefined4 *)(param_14 + 0x194));
      if (iVar20 == 2) {
        sVar9 = *(short *)(param_3 + 0x120);
      }
      else if ((*(int *)(param_14 + 0x20a) == 0) || (*(char *)(param_5 + 2) == '\0')) {
        sVar10 = *(short *)(param_3 + 0x122);
        if (sVar10 < 1) {
          if ((sVar10 != 0) && (*(ushort *)(param_3 + 0x5c) < *(ushort *)(param_3 + 0x6c))) {
            sVar9 = sVar10;
          }
        }
        else if (*(ushort *)(param_3 + 0x6e) < *(ushort *)(param_3 + 0x5e)) {
          sVar9 = sVar10;
        }
      }
      iVar20 = sVar9 * 0x18;
      if (iVar20 < 0) {
        iVar20 = iVar20 + 0xff;
      }
      iVar35 = FUN_43b07780(*(undefined4 *)(param_14 + 0x15a),*(undefined4 *)(param_14 + 0x194));
      if (iVar35 == 2) {
        uVar29 = 0x38;
        uVar12 = 0x38;
      }
      else {
        uVar12 = (uint)*(byte *)(*(int *)(iVar53 + DAT_4384bde8) + 0xc);
        uVar29 = (uint)*(byte *)(*(int *)(iVar53 + DAT_4384bde8) + 0xd);
        if (uVar12 == 0) {
          uVar12 = 0x20;
        }
        if (uVar29 == 0) {
          uVar29 = 0x20;
        }
      }
      iVar20 = (int)(short)((uint)iVar20 >> 8);
      if (iVar20 < (int)-uVar12) goto LAB_4384bbbc;
      if ((int)uVar29 < iVar20) goto LAB_4384bbcc;
    }
    if ((*(int *)(param_14 + 0x15a) == 0x17) ||
       (iVar20 = FUN_4382fe08(*(undefined2 *)(param_3 + 0x152)), iVar20 == 1)) {
      *(undefined1 *)(param_14 + 0x23f) = 0;
    }
    sVar9 = param_14[0x23f];
    puVar37 = (undefined1 *)(DAT_4384bdec + 0x4384bbf4);
    *(char *)(iVar21 + 1000) = (char)sVar9;
    *puVar37 = (char)sVar9;
  }
  if (*(int *)(param_14 + 0x27c) == 1) {
    if ((char)param_14[0x43] == '\0') {
      iVar20 = FUN_43b09420(param_14);
      uVar34 = param_14[0x286];
      if (iVar20 == 0) {
        if (uVar34 < *(ushort *)(param_3 + 0x4c)) {
          uVar34 = *(ushort *)(param_3 + 0x4c);
        }
        param_14[0x244] = uVar34;
        param_14[0x245] = *(short *)(param_3 + 0x4e);
      }
      else {
        if (uVar34 < *(ushort *)(param_3 + 0x1c)) {
          uVar34 = *(ushort *)(param_3 + 0x1c);
        }
        sVar9 = *(short *)(param_3 + 0x1e);
        param_14[0x244] = uVar34;
        param_14[0x245] = sVar9;
      }
    }
    else {
      param_14[0x245] = param_14[0x5a];
      uVar34 = param_14[0x5b];
      if ((ushort)param_14[0x5b] <= (ushort)param_14[0x286]) {
        uVar34 = param_14[0x286];
      }
      param_14[0x244] = uVar34;
    }
    if ((char)param_14[0x44] == '\0') {
      iVar20 = FUN_43b09420(param_14);
      if (iVar20 == 0) {
        sVar9 = *(short *)(param_3 + 0x56);
        param_14[0x242] = *(short *)(param_3 + 0x54);
        param_14[0x243] = sVar9;
      }
      else {
        sVar9 = *(short *)(param_3 + 0x26);
        param_14[0x242] = *(short *)(param_3 + 0x24);
        param_14[0x243] = sVar9;
      }
    }
    else {
      param_14[0x242] = param_14[0x61];
      param_14[0x243] = param_14[0x60];
    }
    if ((((*(char *)(param_5 + 2) == '\x01') && (1 < *(int *)(param_14 + 0x1a4) - 3U)) &&
        ((char)param_14[0x44] != '\x01')) && ((ushort)param_14[0x242] < *(ushort *)(param_5 + 0x70))
       ) {
      param_14[0x242] = *(ushort *)(param_5 + 0x70);
    }
  }
  else if (*(int *)(param_14 + 0x27c) == 0) {
    if ((char)param_14[0x43] == '\0') {
      uStack_30 = 0xffff;
      uStack_2e = 0xffff;
      uStack_2c = 0xffff;
      auStack_2a[0] = 0xffff;
      iVar20 = FUN_43b09420(param_14);
      if (iVar20 == 0) {
        FUN_43b07a06(*(undefined2 *)(param_3 + 0x4c),param_14,param_3,&uStack_30,&uStack_2c);
        uVar11 = *(undefined2 *)(param_3 + 0x4e);
      }
      else {
        FUN_43b07a06(*(undefined2 *)(param_3 + 0x1c),param_14,param_3,&uStack_30,&uStack_2c);
        uVar11 = *(undefined2 *)(param_3 + 0x1e);
      }
      FUN_43b07a06(uVar11,param_14,param_3,&uStack_2e,auStack_2a);
      param_14[0x245] = uStack_2e;
      uVar34 = uStack_30;
      if (uStack_30 <= (ushort)param_14[0x286]) {
        uVar34 = param_14[0x286];
      }
      param_14[0x244] = uVar34;
    }
    else {
      param_14[0x245] = param_14[0x5a];
      uVar34 = param_14[0x5b];
      if ((ushort)param_14[0x5b] <= (ushort)param_14[0x286]) {
        uVar34 = param_14[0x286];
      }
      param_14[0x244] = uVar34;
    }
  }
  FUN_4384a86c(param_3,param_14,param_17 + 0x71);
  iVar20 = *(int *)(param_14 + 0x15e);
  if (iVar20 == 0) {
    uVar12 = (uint)(ushort)param_14[0xcb];
    cVar33 = *(char *)(*piVar51 + 0x3d1);
  }
  else if (iVar20 == 4) {
    uVar12 = (uint)(ushort)param_14[0xcb];
    cVar33 = *(char *)(*piVar51 + 0x3d3);
  }
  else {
    uVar12 = (uint)(ushort)param_14[0xcc];
    if (iVar20 == 3) {
      cVar33 = *(char *)(*piVar51 + 0x3d2);
    }
    else {
      cVar33 = *(char *)(*piVar51 + 0x3d0);
    }
  }
  uVar29 = (uint)(ushort)param_14[0x1a2];
  if ((ushort)param_14[0x1a2] <= uVar12) {
    uVar29 = uVar12;
  }
  if (*(int *)(param_14 + 0x27c) == 2) {
    uVar13 = (uint)*(ushort *)(*(int *)(iVar53 + DAT_4384c930) + 8);
    uVar29 = uVar29 + uVar13 & 0xffff;
    uVar12 = uVar12 + uVar13 & 0xffff;
  }
  iVar20 = -uVar29 + 0x1140;
  if (iVar20 < 0) {
    iVar20 = -uVar29 + 0x11bf;
  }
  cVar8 = (char)(iVar20 >> 7) * '\x03' + -6;
  iVar20 = -uVar12 + 0x1140;
  if (iVar20 < 0) {
    iVar20 = -uVar12 + 0x11bf;
  }
  *(char *)((int)param_14 + 0x47f) = cVar8;
  *(char *)(param_14 + 0x240) = (-6 - cVar33) + (char)(iVar20 >> 7) + (char)((iVar20 >> 7) << 1);
  *(undefined1 *)((int)param_14 + 0x481) = 0;
  *(char *)(iVar21 + 0x61e) = cVar8;
  *(char *)(iVar21 + 0x61f) = (char)param_14[0x240];
  *(undefined1 *)(iVar21 + 0x620) = *(undefined1 *)((int)param_14 + 0x481);
  *(char *)(iVar21 + 0x626) = (char)param_14[0x241];
  *(undefined1 *)(iVar21 + 0x621) = *(undefined1 *)((int)param_14 + 0x341);
  *(char *)(iVar21 + 0x622) = (char)param_14[0x1a1];
  sVar9 = param_14[0x22c];
  iVar20 = *(int *)(param_14 + 0x17a);
  *(short *)(iVar21 + 0x624) = param_14[0x1a2];
  *(bool *)(param_14 + 0x23b) = sVar9 != -1;
  if (iVar20 == 0) {
    *(undefined1 *)((int)param_14 + 0x479) = 0;
    iVar20 = 4;
  }
  else if (iVar20 == 1) {
    *(undefined1 *)((int)param_14 + 0x479) = 1;
    iVar20 = 3;
  }
  else if (iVar20 == 2) {
    *(undefined1 *)((int)param_14 + 0x479) = 2;
    iVar20 = 2;
  }
  else {
    iVar20 = 2;
    *(undefined1 *)((int)param_14 + 0x479) = 2;
  }
  FUN_4382dbcc(auStack_104);
  if (iStack_e0 == 1) {
    bVar55 = true;
  }
  else {
    bVar55 = true;
    if (iStack_d0 != 1) {
      bVar55 = iStack_c8 == 1;
    }
  }
  if (*(char *)(*(int *)(iVar53 + DAT_4384c934) + 0x19) == '\x01') {
    if ((char)param_14[4] == '\x03') {
LAB_4384bf06:
      iVar35 = iVar20 * *(short *)(param_3 + 0x120);
      if (iVar35 < 0) {
        iVar35 = iVar35 + 0xff;
      }
      uVar7 = (undefined1)((uint)iVar35 >> 8);
      *(undefined1 *)(param_14 + 0x23c) = uVar7;
      *(undefined1 *)((int)param_14 + 0x477) = uVar7;
    }
  }
  else if (!bVar55) goto LAB_4384bf06;
  FUN_4382dbcc(auStack_bc);
  *(undefined1 *)(param_14 + 0x23d) = uStack_a0;
  iVar20 = iVar20 * (short)(((((param_14[0x76] + param_14[0x75] + param_14[0x77] + param_14[0x78] +
                               *(short *)((int)param_2 + 0x4e)) - *(short *)(param_3 + 0x15e)) -
                             *(short *)(param_3 + 0x160)) - *(short *)(param_3 + 0x162)) -
                           *(short *)(param_3 + 0x164));
  if (iVar20 < 0) {
    iVar20 = iVar20 + 0xff;
  }
  uVar7 = (undefined1)((uint)iVar20 >> 8);
  *(undefined1 *)((int)param_14 + 0x47b) = uVar7;
  *(undefined1 *)(iVar21 + 0x3ea) = uVar7;
  pcVar52 = *(char **)(iVar53 + DAT_4384c938);
  iVar20 = *(int *)(iVar53 + DAT_4384c93c);
  if (*pcVar52 == '\x04') {
    bVar19 = *(byte *)(iVar20 + 0x1b);
    if (*(char *)((int)param_14 + 0xb) == '\x01') {
      uVar12 = param_2[1] + *(uint *)(DAT_4384c940 + 0x4384bf9c) * 7 >> 3;
      *(uint *)(DAT_4384c940 + 0x4384bf9c) = uVar12;
      cVar33 = (char)param_14[4];
      if (((((cVar33 != '\x10') && (cVar33 != '\x02')) &&
           ((cVar33 != '\x03' && ((cVar33 != '\x04' && (cVar33 != '\x05')))))) && (cVar33 != '\x06')
          ) && ((cVar33 != '\f' && (cVar33 != '\a')))) goto LAB_4384c00e;
      if (bVar19 < 0x20) {
        uVar29 = 0;
        uVar13 = (uint)bVar19;
        do {
          uVar22 = uVar13 + 1 & 0xff;
          uVar29 = uVar29 + (byte)param_8[uVar13 + 0x3f0];
          uVar13 = uVar22;
        } while (uVar22 != 0x20);
      }
      else {
        uVar29 = 0;
      }
      if (*(ushort *)(iVar20 + 0x1c) < uVar29) {
        uVar7 = 2;
      }
      else if (*(ushort *)(iVar20 + 0x1e) < uVar12) {
        uVar7 = 2;
      }
      else {
        uVar7 = 1;
      }
      *(undefined1 *)((int)param_14 + 0x483) = uVar7;
    }
    else {
LAB_4384c00e:
      uVar29 = 0;
    }
    iVar35 = DAT_4384c948;
    iVar14 = *(int *)(iVar53 + DAT_4384c944);
    *(uint *)(iVar14 + 0x648) = uVar29;
    *(undefined4 *)(iVar14 + 0x644) = *(undefined4 *)(iVar35 + 0x4384c024);
  }
  else {
    *(undefined1 *)((int)param_14 + 0x483) = 0;
  }
  *(char *)(iVar21 + 0x640) = *pcVar52;
  if ((**(byte **)(iVar53 + DAT_4384c94c) & 0x80) == 0) {
    bVar19 = *(byte *)(param_14 + 4);
  }
  else {
    bVar19 = **(byte **)(iVar53 + DAT_4384c94c) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c950) & 0x80) == 0) {
    bVar18 = *(byte *)(param_14 + 0x1ec);
  }
  else {
    bVar18 = **(byte **)(iVar53 + DAT_4384c950) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c954) & 0x80) == 0) {
    bVar32 = *(byte *)(param_14 + 0x115);
  }
  else {
    bVar32 = **(byte **)(iVar53 + DAT_4384c954) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c958) & 0x80) == 0) {
    bVar23 = *(byte *)((int)param_14 + 0x241);
  }
  else {
    bVar23 = **(byte **)(iVar53 + DAT_4384c958) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c95c) & 0x80) == 0) {
    bVar24 = *(byte *)(param_14 + 0x43);
  }
  else {
    bVar24 = **(byte **)(iVar53 + DAT_4384c95c) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c960) & 0x80) == 0) {
    bVar25 = *(byte *)(param_14 + 0x44);
  }
  else {
    bVar25 = **(byte **)(iVar53 + DAT_4384c960) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c964) & 0x80) == 0) {
    bVar26 = *(byte *)((int)param_14 + 0x89);
  }
  else {
    bVar26 = **(byte **)(iVar53 + DAT_4384c964) & 0x7f;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c968) & 0x8000) == 0) {
    uStack_508 = (uint)(ushort)param_14[0x4e];
  }
  else {
    uStack_508 = **(ushort **)(iVar53 + DAT_4384c968) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c96c) & 0x8000) == 0) {
    uStack_504 = (uint)(ushort)param_14[0x4f];
  }
  else {
    uStack_504 = **(ushort **)(iVar53 + DAT_4384c96c) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c970) & 0x8000) == 0) {
    uVar12 = (uint)(ushort)param_14[0x50];
  }
  else {
    uVar12 = **(ushort **)(iVar53 + DAT_4384c970) & 0x7fff;
  }
  uVar29 = (uint)**(ushort **)(iVar53 + DAT_4384c974);
  bVar55 = (**(ushort **)(iVar53 + DAT_4384c974) & 0x8000) != 0;
  if (bVar55) {
    uVar29 = uVar29 << 0x11;
  }
  if (bVar55) {
    uVar29 = uVar29 >> 0x11;
  }
  else {
    uVar29 = (uint)*(ushort *)(param_3 + 0x1c);
  }
  if ((**(ushort **)(iVar53 + DAT_4384c978) & 0x8000) == 0) {
    uStack_4fc = (uint)*(ushort *)(param_3 + 0x1e);
  }
  else {
    uStack_4fc = **(ushort **)(iVar53 + DAT_4384c978) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c97c) & 0x8000) == 0) {
    uStack_500 = (uint)*(ushort *)(iVar20 + 0x16);
  }
  else {
    uStack_500 = **(ushort **)(iVar53 + DAT_4384c97c) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c980) & 0x8000) == 0) {
    uVar13 = (uint)*(ushort *)(param_3 + 0x24);
  }
  else {
    uVar13 = **(ushort **)(iVar53 + DAT_4384c980) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c984) & 0x8000) == 0) {
    uStack_50c = (uint)*(ushort *)(param_3 + 0x26);
  }
  else {
    uStack_50c = **(ushort **)(iVar53 + DAT_4384c984) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c988) & 0x8000) == 0) {
    uStack_4d4 = (uint)*(ushort *)(param_3 + 0x2a);
  }
  else {
    uStack_4d4 = **(ushort **)(iVar53 + DAT_4384c988) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c98c) & 0x8000) == 0) {
    uVar22 = (uint)*(ushort *)(param_3 + 0x19e);
  }
  else {
    uVar22 = **(ushort **)(iVar53 + DAT_4384c98c) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c990) & 0x8000) == 0) {
    uStack_4e0 = (uint)*(ushort *)(param_3 + 0x1a2);
  }
  else {
    uStack_4e0 = **(ushort **)(iVar53 + DAT_4384c990) & 0x7fff;
  }
  if ((**(ushort **)(iVar53 + DAT_4384c994) & 0x8000) == 0) {
    uStack_4dc = (uint)*(ushort *)(param_3 + 0x1a4);
  }
  else {
    uStack_4dc = **(ushort **)(iVar53 + DAT_4384c994) & 0x7fff;
  }
  if (**(char **)(iVar53 + DAT_4384c998) == '\x01') {
    uStack_4a8 = (uint)**(ushort **)(iVar53 + DAT_4384c99c);
    uStack_4e8 = (uint)**(ushort **)(iVar53 + DAT_4384c9a0);
  }
  else {
    uStack_4e8 = 0x500;
    uStack_4a8 = (uint)(ushort)param_2[0x49] - (uint)(ushort)param_2[0x4a] & 0xffff;
  }
  if ((**(byte **)(iVar53 + DAT_4384c9a4) & 0x80) == 0) {
    bVar27 = 0x3c;
  }
  else {
    bVar27 = **(byte **)(iVar53 + DAT_4384c9a4) & 0x7f;
  }
  if (*(char *)(iVar20 + 0x12) < '\0') {
    iStack_4f0 = FUN_43b07724(1,*(undefined2 *)(param_3 + 0x1a0));
    iStack_4ec = FUN_43b07724(2,*(undefined2 *)(param_3 + 0x1a0));
    iVar20 = FUN_43b07724(3,*(undefined2 *)(param_3 + 0x1a0));
  }
  else {
    iStack_4f0 = FUN_43830044(1);
    iStack_4ec = FUN_43830044(2);
    iVar20 = FUN_43830044(3);
  }
  if (bVar24 == 0) {
    uVar15 = uStack_500;
    if (uStack_4fc <= uStack_500) {
      uVar15 = uStack_4fc;
    }
    uStack_4f4 = uVar29;
    uStack_4cc = uVar29;
    if (uVar29 <= uVar15) {
      uStack_4f4 = uVar15;
    }
  }
  else {
    uStack_4f4 = uStack_508;
    uStack_4cc = uStack_508;
  }
  uVar15 = FUN_4382fdb8(1,bVar32,bVar23);
  if (bVar25 == 0) {
    uVar54 = uVar13;
    uStack_4f8 = uVar13;
    if ((uVar13 < uVar15) && (uVar54 = uVar15, uStack_50c < uVar15)) {
      uVar54 = uStack_50c;
    }
  }
  else {
    uStack_4f8 = uStack_504;
    uVar54 = uStack_504;
  }
  uVar15 = uVar12;
  if (bVar26 == 0) {
    uVar15 = uStack_4d4;
  }
  uVar38 = uVar15 + uStack_4f8 + uStack_4cc;
  uVar39 = uVar38 & 0xffff;
  uVar40 = uVar15 + uVar54 + uStack_4f4;
  uVar41 = uVar40 & 0xffff;
  uVar42 = uVar39 + iStack_4f0 & 0xffff;
  uVar43 = uVar41 + iStack_4f0 & 0xffff;
  uVar44 = uVar39 + iStack_4ec & 0xffff;
  uVar45 = uVar41 + iStack_4ec & 0xffff;
  uVar46 = uVar39 + iVar20 & 0xffff;
  FUN_43b09580(uVar42,uVar41,auStack_2a,&uStack_2c);
  FUN_43b09580(uVar44,uVar43,&uStack_2e,&uStack_30);
  FUN_43b09580(uVar46,uVar45,&uStack_32,&uStack_34);
  sVar9 = (short)uStack_4a8;
  sVar10 = (short)uStack_4e8;
  if ((int)sVar10 < (int)sVar9) {
    uStack_510 = uStack_4e8;
  }
  else if ((int)sVar9 < -(int)sVar10) {
    uStack_510 = -uStack_4e8 & 0xffff;
  }
  else {
    uStack_510 = uStack_4a8;
  }
  uVar47 = uStack_4dc + uStack_4e0 + uVar22 + uStack_510;
  uVar48 = uVar47 & 0xffff;
  uVar11 = (undefined2)uVar47;
  switch(bVar18) {
  case 0:
    if (uVar48 < uStack_2c) {
LAB_4384c4d2:
      cVar33 = '\x01';
    }
    else if (uVar48 < uVar43) {
LAB_4384c4d6:
      cVar33 = '\x02';
    }
    else if (uVar48 < uVar45) {
      if (uVar48 < uVar44) {
        cVar33 = '\x02';
      }
      else {
        cVar33 = '\x03';
      }
    }
    else {
LAB_4384c462:
      uVar11 = (undefined2)uVar48;
      if (uVar48 < uVar46) {
        cVar33 = '\x03';
      }
      else {
        cVar33 = '\x04';
      }
    }
    break;
  case 1:
    uVar42 = uVar48 + iStack_4f0;
    uVar48 = uVar42 & 0xffff;
    uVar11 = (undefined2)uVar42;
    if (uVar48 <= auStack_2a[0]) goto LAB_4384c4d2;
    if (uVar48 < uStack_30) goto LAB_4384c4d6;
    if (uVar45 <= uVar48) goto LAB_4384c462;
LAB_4384c4de:
    cVar33 = '\x03';
    break;
  case 2:
    uVar43 = uVar48 + iStack_4ec & 0xffff;
    uVar11 = (undefined2)(uVar48 + iStack_4ec);
    if (uVar43 < uStack_34) {
      if (uStack_2e < uVar43) goto LAB_4384c4de;
      if (uVar42 < uVar43) goto LAB_4384c4d6;
      if (uVar41 < uVar43) {
        cVar33 = '\x02';
      }
      else {
        cVar33 = '\x01';
      }
    }
    else {
LAB_4384c4da:
      cVar33 = '\x04';
    }
    break;
  case 3:
    uVar45 = uVar48 + iVar20 & 0xffff;
    uVar11 = (undefined2)(uVar48 + iVar20);
    if (uStack_32 < uVar45) goto LAB_4384c4da;
    if (uVar44 < uVar45) goto LAB_4384c4de;
    if (uVar42 < uVar45) {
      if (uVar43 < uVar45) {
        cVar33 = '\x03';
      }
      else {
        cVar33 = '\x02';
      }
    }
    else if (uVar41 < uVar45) {
      cVar33 = '\x02';
    }
    else {
      cVar33 = '\x01';
    }
    break;
  default:
    cVar33 = '\0';
  }
  if (cVar33 == *(char *)(DAT_4384c9a8 + 0x4384c4e8)) {
    bVar1 = *(byte *)(DAT_4384c9ac + 0x4384c4f8);
    cVar8 = cVar33;
    if (bVar1 <= bVar27) {
      *(byte *)(DAT_4384c9ac + 0x4384c4f8) = bVar1 + 1;
      cVar8 = '\0';
    }
  }
  else {
    *(undefined1 *)(DAT_4384c9b0 + 0x4384c510) = 0;
    cVar8 = '\0';
  }
  *(char *)(DAT_4384c9b4 + 0x4384c522) = cVar33;
  if (*(byte *)(DAT_4384c9b8 + 0x4384c52e) != bVar18) {
    cVar8 = '\0';
    *(undefined1 *)(DAT_4384c9bc + 0x4384c53c) = 0;
  }
  *(byte *)(DAT_4384c9c0 + 0x4384c546) = bVar18;
  if ((bVar24 == 1) || ((char)param_14[0x21a] == '\x01')) {
    cVar8 = '\0';
    *(undefined1 *)(DAT_4384c9c4 + 0x4384c55e) = 0;
  }
  if (bVar19 != 3) {
    cVar8 = '\0';
    *(undefined1 *)(DAT_4384c9c8 + 0x4384c572) = 0;
  }
  iVar21 = *(int *)(iVar53 + DAT_4384c93c);
  if (((bVar18 == 5) || (*(int *)(param_14 + 0x15e) != 1)) || ((*(byte *)(iVar21 + 0x12) & 1) == 0))
  {
    cVar8 = '\0';
    *(undefined1 *)(DAT_4384c9cc + 0x4384c59a) = 0;
    *(undefined1 *)(DAT_4384c9d0 + 0x4384c5a2) = 0;
    *(undefined1 *)(DAT_4384c9d4 + 0x4384c5aa) = 0;
  }
  uVar42 = *(uint *)(iVar53 + DAT_4384c944);
  *(byte *)(uVar42 + 0x3eb) = bVar19;
  *(short *)(uVar42 + 0x3fe) = (short)uVar13;
  *(byte *)(uVar42 + 0x3ec) = bVar18;
  *(short *)(uVar42 + 0x400) = (short)uStack_50c;
  *(byte *)(uVar42 + 0x3ed) = bVar32;
  *(short *)(uVar42 + 0x3f8) = (short)uVar29;
  *(short *)(uVar42 + 0x404) = (short)uVar22;
  *(byte *)(uVar42 + 0x3ee) = bVar23;
  *(byte *)(uVar42 + 0x3ef) = bVar24;
  *(byte *)(uVar42 + 0x3f0) = bVar25;
  *(byte *)(uVar42 + 0x3f1) = bVar26;
  *(short *)(uVar42 + 0x3f2) = (short)uStack_508;
  *(short *)(uVar42 + 0x3f4) = (short)uStack_504;
  *(short *)(uVar42 + 0x3f6) = (short)uVar12;
  *(short *)(uVar42 + 0x3fa) = (short)uStack_4fc;
  *(short *)(uVar42 + 0x3fc) = (short)uStack_500;
  *(short *)(uVar42 + 0x402) = (short)uStack_4d4;
  *(short *)(uVar42 + 0x406) = (short)uStack_4e0;
  *(short *)(uVar42 + 0x416) = (short)uVar54;
  *(short *)(uVar42 + 0x408) = (short)uStack_4dc;
  *(short *)(uVar42 + 0x40a) = sVar9;
  *(short *)(uVar42 + 0x40c) = sVar10;
  *(byte *)(uVar42 + 0x40e) = bVar27;
  *(short *)(uVar42 + 0x410) = (short)uStack_4cc;
  *(short *)(uVar42 + 0x412) = (short)uStack_4f4;
  *(short *)(uVar42 + 0x414) = (short)uStack_4f8;
  *(short *)(uVar42 + 0x418) = (short)uVar15;
  *(short *)(uVar42 + 0x41a) = (short)uVar15;
  *(short *)(uVar42 + 0x41c) = (short)uVar38;
  uVar5 = (undefined2)uVar40;
  *(undefined2 *)(uVar42 + 0x41e) = uVar5;
  *(undefined2 *)(uVar42 + 0x420) = uVar5;
  *(short *)(uVar42 + 0x422) = (short)(uVar39 + iStack_4f0);
  *(short *)(uVar42 + 0x424) = (short)(uVar41 + iStack_4f0);
  *(short *)(uVar42 + 0x426) = (short)(uVar39 + iStack_4ec);
  *(short *)(uVar42 + 0x428) = (short)(uVar41 + iStack_4ec);
  *(short *)(uVar42 + 0x42a) = (short)(uVar39 + iVar20);
  *(ushort *)(uVar42 + 0x42c) = auStack_2a[0];
  *(undefined2 *)(uVar42 + 0x440) = uVar11;
  puVar37 = (undefined1 *)(DAT_4384c9d8 + 0x4384c698);
  *(char *)((int)param_17 + 0xa63) = cVar8;
  uVar7 = *puVar37;
  *(ushort *)(uVar42 + 0x42e) = uStack_2c;
  *(ushort *)(uVar42 + 0x430) = uStack_2e;
  *(undefined1 *)(uVar42 + 0x444) = uVar7;
  puVar37 = (undefined1 *)(DAT_4384c9dc + 0x4384c6b6);
  *(char *)(uVar42 + 0x443) = cVar8;
  uVar7 = *puVar37;
  *(ushort *)(uVar42 + 0x432) = uStack_30;
  *(ushort *)(uVar42 + 0x434) = uStack_32;
  *(undefined1 *)(uVar42 + 0x445) = uVar7;
  puVar37 = (undefined1 *)(DAT_4384c9e0 + 0x4384c6d6);
  *(ushort *)(uVar42 + 0x436) = uStack_34;
  *(short *)(uVar42 + 0x438) = (short)iStack_4f0;
  uVar7 = *puVar37;
  *(short *)(uVar42 + 0x43a) = (short)iStack_4ec;
  *(short *)(uVar42 + 0x43c) = (short)iVar20;
  *(undefined1 *)(uVar42 + 0x446) = uVar7;
  iVar20 = DAT_4384c9e4;
  *(short *)(uVar42 + 0x43e) = (short)uStack_510;
  *(char *)(uVar42 + 0x442) = cVar33;
  bVar55 = (**(byte **)(iVar53 + iVar20) & 0x80) != 0;
  uVar12 = uVar42;
  if (bVar55) {
    uVar12 = **(byte **)(iVar53 + iVar20) & 0x7f;
  }
  bVar19 = *(byte *)(iVar21 + 0x12);
  if (!bVar55) {
    uVar12 = (uint)*(byte *)((int)param_14 + 0x8b);
  }
  bVar32 = bVar19 & 2;
  bVar18 = bVar32;
  if ((bVar19 & 2) != 0) {
    if (uVar12 == 1) {
      bVar18 = 1;
    }
    else {
      bVar18 = 2;
    }
  }
  *(char *)(uVar42 + 0x447) = (char)uVar12;
  iVar20 = DAT_4384c950;
  *(byte *)(param_17 + 0x532) = bVar18;
  *(byte *)(uVar42 + 0x448) = bVar18;
  if ((**(byte **)(iVar53 + iVar20) & 0x80) == 0) {
    uVar12 = (uint)*(byte *)(param_14 + 0x1ec);
  }
  else {
    uVar12 = **(byte **)(iVar53 + iVar20) & 0x7f;
  }
  if ((**(byte **)(iVar53 + DAT_4384c9e8) & 0x80) == 0) {
    bVar18 = *(byte *)(param_14 + 0x48);
  }
  else {
    bVar18 = **(byte **)(iVar53 + DAT_4384c9e8) & 0x7f;
  }
  if ((bVar19 & 2) != 0) {
    if (uVar12 == 5) {
      if (bVar18 == 0) {
        bVar32 = 1;
      }
      else if (bVar18 == 1) {
        bVar32 = 2;
      }
      else {
        bVar32 = 0;
      }
    }
    else if (uVar12 < 4) {
      bVar32 = (byte)*(undefined4 *)(DAT_4384c9ec + 0x4384c77e + uVar12 * 4);
    }
    else {
      bVar32 = 0;
    }
  }
  *(char *)(uVar42 + 0x3ec) = (char)uVar12;
  *(byte *)(uVar42 + 0x44a) = bVar32;
  *(byte *)((int)param_17 + 0xa65) = bVar32;
  *(byte *)(uVar42 + 0x449) = bVar18;
  *(bool *)((int)param_14 + 0x25) = *(short *)(param_3 + 0x11a) == -1;
  uVar7 = FUN_4382fe44((int)*(short *)((int)param_2 + 0x12a),*(undefined1 *)((int)param_14 + 0xb),
                       0x40,0x14,(int)param_14 + 0x1f);
  *(undefined1 *)(param_14 + 0xf) = uVar7;
  uVar34 = *(ushort *)((int)param_2 + 0x12a);
  uVar12 = param_2[0x4b];
  uVar28 = *(ushort *)(param_3 + 0x5c);
  uVar3 = *(ushort *)(param_3 + 0x5e);
  if ((ushort)(*param_14 - 0x380U) < 2) {
    bVar19 = *(char *)((int)param_14 + 0x1d) + 1;
    *(byte *)((int)param_14 + 0x1d) = bVar19;
    if (bVar19 < 0x17) {
      if (*(char *)((int)param_14 + 0xb) == '\x01') {
        bVar55 = true;
        if ((0xfe < (ushort)(uVar34 + 0x7f)) &&
           ((uVar28 < (ushort)uVar12 || ((uVar34 & 0x8000) == 0)))) {
          if ((ushort)uVar12 < uVar3) goto LAB_4384c822;
          bVar55 = 0 < (short)uVar34;
        }
      }
      else {
LAB_4384c822:
        bVar55 = false;
      }
    }
    else {
      bVar55 = true;
    }
  }
  else {
    bVar55 = false;
    *(undefined1 *)((int)param_14 + 0x1d) = 0;
  }
  *(bool *)(param_14 + 0xe) = bVar55;
  uVar7 = FUN_43b096ee(param_14,param_2,param_3,param_10);
  *(undefined1 *)(param_14 + 0x364) = uVar7;
  uVar36 = FUN_43b09642(param_14,param_5);
  *(undefined4 *)(param_14 + 0x18) = uVar36;
  if (*param_14 == 0x386) {
    cVar33 = '\0';
LAB_4384c890:
    *(char *)((int)param_14 + 0x2f) = cVar33;
  }
  else if ((*param_14 == 0x387) && (*(char *)((int)param_14 + 0xb) == '\x01')) {
    uVar12 = (uint)*(ushort *)(*(int *)(iVar53 + DAT_4384c9f0) + 0x28);
    if (uVar12 == 0) {
      uVar12 = 0x300;
    }
    if ((((int)uVar12 < (int)*(short *)((int)param_2 + 0x12a)) ||
        ((int)*(short *)((int)param_2 + 0x12a) < (int)-uVar12)) &&
       (*(byte *)((int)param_14 + 0x2f) < 0x15)) {
      cVar33 = *(byte *)((int)param_14 + 0x2f) + 1;
    }
    else {
      *(undefined1 *)(param_14 + 0x17) = 1;
      cVar33 = '\0';
    }
    goto LAB_4384c890;
  }
  if (((*(int *)(param_14 + 0x27c) != 0) || (1 < *(int *)(param_14 + 0x168) - 1U)) ||
     (uVar7 = 0, *(short *)(param_3 + 0x1a4) == *(short *)(param_3 + 0x28))) {
    uVar7 = 1;
  }
  *(undefined1 *)((int)param_14 + 99) = uVar7;
  *(undefined1 *)(param_17 + 0x534) = *(undefined1 *)(param_6 + 100);
  *(char *)((int)param_17 + 0xa69) = (char)param_2[0x50];
  param_17[0x535] = *(short *)(param_6 + 0x62);
  if (*(char *)(param_6 + 0x5d) == '\x01') {
    sVar9 = *(short *)(param_6 + 0x5e2);
    param_17[0x536] = *(short *)(param_6 + 0x5e0);
    param_17[0x537] = sVar9;
  }
  else if (*(char *)(param_6 + 0x5e) == '\x01') {
    sVar9 = *(short *)(param_6 + 0x5f8);
    param_17[0x536] = *(short *)(param_6 + 0x5f6);
    param_17[0x537] = sVar9;
  }
  if (*param_14 == 0x386) {
    *(undefined1 *)(param_17 + 0x3ec) = 0;
    if ((799 < *(ushort *)(param_7 + 0x558)) && (0x18 < *(ushort *)(param_7 + 0x55a))) {
      uVar7 = *(undefined1 *)(param_7 + 0xc);
      goto LAB_4384c9fa;
    }
  }
  else {
    uVar7 = *(undefined1 *)(param_7 + 0xc);
LAB_4384c9fa:
    *(undefined1 *)(param_17 + 0x3ec) = uVar7;
  }
  *(undefined1 *)(param_17 + 0x3fe) = *(undefined1 *)(param_7 + 0x30);
  sVar9 = *(short *)(param_7 + 0x2be);
  param_17[0x40d] = *(short *)(param_7 + 0x2c6);
  param_17[0x409] = sVar9;
  FUN_439c5320(param_17 + 0x459,param_7 + 0x35e,0x38);
  FUN_439c5320(param_17 + 0x475,param_7 + 0x396,0x38);
  uVar36 = *(undefined4 *)(param_7 + 0x4e8);
  uVar30 = *(undefined4 *)(param_7 + 0x4ec);
  uVar49 = *(undefined4 *)(param_7 + 0x4f0);
  *(undefined4 *)(param_17 + 0x51c) = *(undefined4 *)(param_7 + 0x4e4);
  *(undefined4 *)(param_17 + 0x51e) = uVar36;
  *(undefined4 *)(param_17 + 0x520) = uVar30;
  param_17[0x522] = (short)uVar49;
  *(undefined1 *)(param_17 + 0x530) = *param_8;
  *(undefined1 *)((int)param_17 + 0xa61) = param_8[1];
  iVar20 = (uint)*(byte *)(*(int *)(iVar53 + DAT_4384cf9c) + 0xff) * -0x10;
  bVar55 = iVar20 - *(short *)((int)param_2 + 0x4a) != 0 &&
           *(short *)((int)param_2 + 0x4a) <= iVar20;
  *(bool *)(param_17 + 0x3d7) = bVar55;
  *(bool *)(param_17 + 0x3d9) = bVar55;
  *(bool *)(uVar42 + 0x341) = bVar55;
  bVar55 = (short)param_2[0x13] < (short)iVar20;
  *(bool *)((int)param_17 + 0x7b3) = bVar55;
  *(bool *)(uVar42 + 0x342) = bVar55;
  FUN_438565a8(param_14,param_6,param_13,param_15);
  uVar36 = FUN_436d6118();
  FUN_436d61e4(uVar36,uVar42 + 0x4dc);
  FUN_43ae0e36(auStack_47c);
  FUN_43ae119e(auStack_174);
  FUN_4383c6ec(auStack_47c,auStack_174);
  FUN_4383b520(0x81,0);
  FUN_43ae1292(0x20);
  iVar20 = FUN_437284b4();
  uVar36 = FUN_43728564();
  iVar21 = *(int *)(iVar53 + DAT_4384cfa0);
  if ((iVar20 == 0) &&
     ((((*(char *)(iVar21 + 0x40) != '\x01' || (*(int *)(param_14 + 0x15e) == 0)) ||
       (*(int *)(param_14 + 0x15e) == 4)) || ((*param_14 == 0x309 || (*param_14 == 0x30e)))))) {
    FUN_437b03c8(param_14);
    FUN_437b03e8(param_3);
    FUN_437b0408(param_2);
    FUN_437b0428(param_1);
    FUN_437b0440(param_5);
    FUN_437b0480(param_6);
    FUN_437b04b8(param_7);
    FUN_437b04d8(param_15);
    FUN_437b0518(param_9);
    FUN_437b0538(param_10);
    FUN_437b0558(param_12);
    FUN_437b0574(param_11);
    FUN_437b0460(param_4);
    FUN_437b0598(param_16);
    FUN_437b05b4(0,uVar36);
  }
  FUN_43ae129a(0x20);
  FUN_4383b520(0x81,1);
  iVar20 = *(int *)(param_14 + 0x1fa);
  if (iVar20 == 1) {
    sVar9 = param_14[0x379];
    *param_17 = param_14[0x378];
    param_17[0xb] = sVar9;
  }
  uVar36 = *(undefined4 *)(DAT_4384cfa4 + 0x4384cbd2);
  if ((*(int *)(param_14 + 0x1f8) == 1) && (iVar20 == 1)) {
    puVar16 = (undefined4 *)FUN_43ae84e8();
    *puVar16 = uVar36;
  }
  iVar20 = FUN_43b09510(param_14);
  if (iVar20 != 0) {
    uVar36 = *(undefined4 *)(DAT_4384cfa8 + 0x4384cbee);
    iVar20 = FUN_43ae8444();
    *(undefined4 *)(iVar20 + 0x88) = uVar36;
    *(short *)(uVar42 + 0x366) = (short)uVar36;
    puVar17 = (undefined2 *)FUN_43ae8444();
    uVar11 = *(undefined2 *)(param_3 + 0x1e0);
    uVar5 = *(undefined2 *)(param_3 + 0x1e2);
    uVar4 = *(undefined2 *)(param_3 + 0x1e4);
    *puVar17 = *(undefined2 *)(param_3 + 0x1de);
    puVar17[1] = uVar11;
    puVar17[2] = uVar5;
    sVar9 = param_17[7];
    uVar11 = *(undefined2 *)((int)param_2 + 0x52);
    uVar12 = param_2[0x48];
    puVar17[3] = uVar4;
    uVar29 = param_2[0x14];
    iVar20 = FUN_43ae8444();
    *(undefined2 *)(iVar20 + 0xc) = uVar11;
    *(short *)(iVar20 + 10) = (short)uVar29;
    *(short *)(iVar20 + 8) = sVar9;
    *(short *)(iVar20 + 0xe) = (short)uVar12;
    iVar20 = FUN_43ae8444();
    FUN_439c5320(iVar20 + 0x80,param_11 + 0xe,7);
    iVar20 = FUN_43ae8444();
    FUN_439c5320(iVar20 + 0x10,param_7 + 0x35e,0x38);
    FUN_439c5320(iVar20 + 0x48,param_7 + 0x396,0x38);
    iVar20 = FUN_43b09510(param_14);
    if (iVar20 != 0) {
      FUN_43ae8450();
    }
  }
  *(int *)(DAT_4384cfac + 0x4384cc80) = *(int *)(DAT_4384cfac + 0x4384cc80) + 1;
  if ((((char)param_14[0x43] == '\0') || ((char)param_14[0x44] == '\0')) ||
     (*(char *)((int)param_14 + 0x89) == '\0')) {
    bVar55 = 6 < *(byte *)((int)param_14 + 0x1f);
  }
  else {
    bVar55 = true;
  }
  *(bool *)(param_17 + 0x3da) = bVar55;
  *(undefined1 *)(param_14 + 0x2c0) = *(undefined1 *)(param_3 + 0x13);
  iVar20 = FUN_43b09420(param_14);
  if (iVar20 == 0) {
    uVar7 = FUN_4384a470(param_14,param_3,param_2);
  }
  else {
    uVar7 = FUN_4384a288(param_14,param_3,param_2);
  }
  *(undefined1 *)((int)param_14 + 0x57f) = uVar7;
  if (*(char *)((int)param_14 + 0x6ab) != *(char *)(param_5 + 0xee)) {
    *(char *)((int)param_14 + 0x6ab) = *(char *)(param_5 + 0xee);
    iVar35 = FUN_435612d0(DAT_4384cf90,&puStack_3c,0x10,1);
    if (iVar35 == 0) {
      FUN_43b094ea(puStack_3c,DAT_4384cf94);
      uVar30 = DAT_4384cf98;
      uVar36 = DAT_4384cf94;
      puStack_3c[2] = 0;
      puStack_3c[3] = 0;
      *puStack_3c = uVar30;
      puStack_3c[1] = uVar36;
      FUN_43561228(DAT_4384cf90);
      FUN_435612ec(DAT_4384cf90,puStack_3c);
    }
  }
  FUN_439c5a04(asStack_74,0,0x28);
  if (iVar20 == 0) {
    sVar9 = *(short *)(param_3 + 0x152);
    uVar11 = *(undefined2 *)(param_3 + 0x154);
    param_14[0x112] = *(short *)(param_3 + 0x14e);
    param_14[0x113] = sVar9;
    sVar9 = FUN_43b07522(uVar11);
    param_14[0x114] = sVar9;
  }
  asStack_74[0] = param_14[0x112];
  sVar9 = param_14[0x114];
  sStack_70 = param_14[0x113];
  uStack_6e = sVar9;
  sVar10 = FUN_4385e598(param_14);
  uStack_6e = sVar9 - sVar10;
  if (iVar20 == 0) {
    uVar12 = (uint)(ushort)param_14[0x2be];
    *(char *)(param_14 + 0x369) = (char)param_14[0x368];
    if (uVar12 == 0) {
      uVar12 = (uint)(ushort)param_14[699];
      uVar11 = FUN_4355fd68(uVar12 + 5,10);
      uVar7 = FUN_43ada770(uVar11);
      *(undefined1 *)(param_14 + 0x369) = uVar7;
    }
    if ((*(byte *)(param_5 + 0xfd) < 8) && (*(int *)(param_14 + 0x140) != 0)) {
      uVar34 = param_14[0x142];
      if (uVar34 != 0) {
        iVar20 = 0x10d1;
LAB_4384cdc8:
        uVar29 = FUN_4355faf0(iVar20 * uVar12 + (uint)(uVar34 >> 1));
        uVar12 = 0xffff;
        if (uVar29 < 0xffff) {
          uVar12 = uVar29;
        }
        uVar12 = uVar12 & 0xffff;
      }
    }
    else {
      if (*(int *)(param_14 + 0x140) != 2) goto LAB_4384cdee;
      uVar34 = param_14[0x142];
      if (uVar34 != 0) {
        iVar20 = 0xb03;
        goto LAB_4384cdc8;
      }
    }
    uVar11 = FUN_4355fd68(uVar12 + 5,10);
    uVar7 = FUN_43ada770(uVar11);
    *(undefined1 *)(param_14 + 0x369) = uVar7;
  }
LAB_4384cdee:
  uStack_6c = (ushort)*(byte *)(param_14 + 0x369);
  uStack_6a = *(undefined1 *)((int)param_14 + 0x2e9);
  cStack_69 = (char)param_14[0x176];
  if (cStack_69 == '\0') {
    uStack_68 = 4;
  }
  else if (cStack_69 == '\x02') {
    uStack_68 = 2;
  }
  else {
    uStack_68 = 3;
  }
  uStack_67 = (undefined1)param_14[0x1ae];
  cStack_66 = (char)param_14[0x1b0];
  if (cStack_66 == '\0') {
    uStack_65 = 4;
  }
  else if (cStack_66 == '\x02') {
    uStack_65 = 2;
  }
  else {
    uStack_65 = 3;
  }
  uStack_5b = FUN_4382fe08(sStack_70);
  uStack_64 = 0;
  uStack_63 = 0;
  uStack_62 = (undefined1)*(undefined4 *)(param_14 + 0x15a);
  uStack_60 = (undefined1)*(undefined4 *)(param_14 + 0x1a6);
  uStack_61 = (undefined1)*(undefined4 *)(param_14 + 0x148);
  uStack_5f = (undefined1)*(undefined4 *)(param_14 + 0x1c2);
  if (*(char *)(*(int *)(iVar53 + DAT_4384cfb0) + 0x1c) != '\x01') {
    cVar8 = *(char *)(param_5 + 0xd4);
    cVar50 = *(char *)((int)param_14 + 0x365);
    cVar33 = **(char **)(iVar53 + DAT_4384cfb4);
    if (cVar33 != '\0') {
      if (cVar33 == '\x01') {
        cVar8 = '\x01';
      }
      else if (cVar33 == '\x02') {
        cVar50 = '\x01';
      }
      else if (cVar33 == '\x03') {
        cVar8 = '\x01';
        cVar50 = cVar8;
      }
      else if (cVar33 == '\x04') {
        cVar8 = '\x01';
        cVar50 = '\0';
      }
      else if (cVar33 == '\x05') {
        cVar8 = '\0';
        cVar50 = '\x01';
      }
      else if (cVar33 == '\x06') {
        *(undefined1 *)(DAT_4384cfb8 + 0x4384ceae) = 0;
      }
      else {
        cVar8 = '\0';
        cVar50 = cVar8;
      }
    }
    iVar20 = FUN_438fb29c();
    cVar33 = **(char **)(iVar53 + DAT_4384cfbc);
    if (cVar33 == '\0') {
      if ((*(char *)(iVar21 + 0xa5) == '\0') && (*(char *)(param_5 + 0xec) == '\x01')) {
        if (*(char *)(param_5 + 0xeb) == '\x01') {
          if (cVar50 != '\0') {
            FUN_437ff038(0);
          }
          iVar35 = DAT_4384cfc0;
          cVar50 = '\0';
          *(undefined1 *)(param_14 + 0x354) = 0;
          *(undefined1 *)((int)param_14 + 0x6a9) = 0;
          *(undefined2 *)(iVar35 + 0x4384cf1e) = 0;
          *(undefined1 *)(DAT_4384cfc4 + 0x4384cf28) = 0;
          iVar35 = 0x20;
          goto LAB_4384d290;
        }
        if (cVar50 == '\0') {
          if ((((((*(uint *)(param_14 + 0x15a) < 3) ||
                 (iVar35 = FUN_43b07780(*(uint *)(param_14 + 0x15a),
                                        *(undefined4 *)(param_14 + 0x194)), iVar35 != 0)) ||
                (*(int *)(param_14 + 0x15a) == 0x2b)) ||
               ((*(int *)(param_14 + 0x15a) == 0x2c || (1 < (ushort)(*param_14 - 0x303U))))) ||
              (((iVar35 = *(int *)(param_14 + 0x160), 2 < iVar35 - 1U &&
                ((iVar35 != 0x10 && (iVar35 != 0x11)))) &&
               ((iVar35 != 0xd && ((iVar35 != 0xe && (iVar35 != 4)))))))) ||
             ((cVar8 != '\x01' || (*(char *)(DAT_4384d7e0 + 0x4384d054) != '\0')))) {
            iVar14 = DAT_4384d82c;
            if ((*(int *)(param_14 + 0x21c) == 0) || (*(char *)(DAT_4384d80c + 0x4384d106) != '\0'))
            {
              iVar35 = 0;
              cVar8 = '\0';
              *(undefined1 *)(param_14 + 0x354) = 0;
              *(undefined1 *)((int)param_14 + 0x6a9) = 0;
              *(undefined2 *)(iVar14 + 0x4384d1ae) = 0;
              *(undefined1 *)(DAT_4384d830 + 0x4384d1ba) = 0;
            }
            else if (cVar8 == '\x01') {
              *(byte *)(DAT_4384d810 + 0x4384d116) = *(byte *)(DAT_4384d810 + 0x4384d116) | 4;
              iVar14 = DAT_4384d828;
              iVar35 = DAT_4384d820;
              if (iVar20 == 0) {
                if (*(char *)(DAT_4384d814 + 0x4384d126) != '\0') {
LAB_4384d152:
                  if (*(char *)(DAT_4384d81c + 0x4384d15a) == '\x01') goto LAB_4384d15e;
                  *(undefined1 *)(param_14 + 0x354) = 0;
                  puVar37 = (undefined1 *)(iVar14 + 0x4384d18c);
                  *(undefined1 *)((int)param_14 + 0x6a9) = 1;
                  goto LAB_4384d18e;
                }
                puVar31 = (ushort *)(DAT_4384d818 + 0x4384d138);
                uVar34 = *puVar31;
                if (*(byte *)(*(int *)(iVar53 + DAT_4384d7e8) + 0x28) <= uVar34) goto LAB_4384d152;
                *(undefined1 *)(param_14 + 0x354) = 1;
                *puVar31 = uVar34 + 1;
                *(undefined1 *)((int)param_14 + 0x6a9) = 0;
              }
              else {
                if (iVar20 != 1) goto LAB_4384d152;
LAB_4384d15e:
                *(undefined1 *)((int)param_14 + 0x6a9) = 0;
                *(undefined1 *)(iVar35 + 0x4384d16e) = 1;
                *(undefined1 *)(param_14 + 0x354) = 2;
                puVar37 = (undefined1 *)(DAT_4384d824 + 0x4384d17c);
LAB_4384d18e:
                cVar8 = '\0';
                *puVar37 = 1;
              }
              iVar35 = 0x10;
            }
            else {
              *(char *)(DAT_4384d80c + 0x4384d106) = '\x01';
              iVar35 = 0;
              cVar8 = '\0';
            }
          }
          else {
            *(byte *)(DAT_4384d8b8 + 0x4384d8a8) = *(byte *)(DAT_4384d8b8 + 0x4384d8a8) | 2;
            iVar6 = DAT_4384d808;
            iVar14 = DAT_4384d800;
            if (iVar20 == 0) {
              if (*(char *)(DAT_4384d7e4 + 0x4384d06c) == '\0') {
                if (iVar35 == 0xd) {
                  bVar19 = *(byte *)(*(int *)(iVar53 + DAT_4384d7e8) + 0x2f);
                  uVar34 = *(ushort *)(DAT_4384d7f0 + 0x4384d094);
                }
                else {
                  bVar19 = *(byte *)(*(int *)(iVar53 + DAT_4384d7e8) + 0x28);
                  uVar34 = *(ushort *)(DAT_4384d7ec + 0x4384d086);
                }
                if (bVar19 <= uVar34) goto LAB_4384d0bc;
                *(short *)(DAT_4384d7f4 + 0x4384d0a0) = *(short *)(DAT_4384d7f4 + 0x4384d0a0) + 1;
                *(undefined1 *)((int)param_14 + 0x6a9) = 0;
                iVar35 = DAT_4384d7f8;
                *(undefined1 *)(param_14 + 0x354) = 1;
                puVar37 = (undefined1 *)(iVar35 + 0x4384d0b8);
              }
              else {
LAB_4384d0bc:
                if (*(char *)(DAT_4384d7fc + 0x4384d0c4) == '\x01') goto LAB_4384d0c8;
                cVar8 = '\0';
                *(undefined1 *)(param_14 + 0x354) = 0;
                *(undefined1 *)((int)param_14 + 0x6a9) = 1;
                puVar37 = (undefined1 *)(iVar6 + 0x4384d0fe);
              }
            }
            else {
              if (iVar20 != 1) goto LAB_4384d0bc;
LAB_4384d0c8:
              cVar8 = '\0';
              *(undefined1 *)((int)param_14 + 0x6a9) = 0;
              *(undefined1 *)(iVar14 + 0x4384d0d8) = 1;
              *(undefined1 *)(param_14 + 0x354) = 2;
              puVar37 = (undefined1 *)(DAT_4384d804 + 0x4384d0e6);
            }
            *puVar37 = 1;
            iVar35 = 8;
          }
        }
        else {
          *(byte *)(DAT_4384cfc8 + 0x4384cf36) = *(byte *)(DAT_4384cfc8 + 0x4384cf36) | 1;
          iVar35 = DAT_4384cfdc;
          if (iVar20 == 0) {
            if (*(char *)(DAT_4384cfcc + 0x4384cf44) == '\0') {
              puVar31 = (ushort *)(DAT_4384cfd4 + 0x4384cf52);
              uVar34 = *puVar31;
              if (uVar34 < *(byte *)(*(int *)(iVar53 + DAT_4384cfd0) + 0x28)) {
                *(undefined1 *)(param_14 + 0x354) = 1;
                *puVar31 = uVar34 + 1;
                *(undefined1 *)((int)param_14 + 0x6a9) = 0;
                iVar35 = 4;
                cVar8 = '\x01';
                goto LAB_4384d1ba;
              }
            }
LAB_4384cf70:
            if (*(char *)(DAT_4384cfd8 + 0x4384cf76) == '\x01') goto LAB_4384cf7a;
            *(undefined1 *)(param_14 + 0x354) = 0;
            *(undefined1 *)((int)param_14 + 0x6a9) = 1;
          }
          else {
            if (iVar20 != 1) goto LAB_4384cf70;
LAB_4384cf7a:
            *(undefined1 *)((int)param_14 + 0x6a9) = 0;
            *(undefined1 *)(iVar35 + 0x4384cf88) = 1;
            *(undefined1 *)(param_14 + 0x354) = 2;
          }
          cVar8 = '\0';
          FUN_437ff038(0);
          iVar35 = 4;
        }
LAB_4384d1ba:
        if (((((*(int *)(param_14 + 0x21c) == 0) &&
              (iVar14 = *(int *)(param_14 + 0x160), iVar14 != 1)) && (iVar14 != 2)) &&
            ((iVar14 != 3 && (iVar14 != 0x11)))) && (iVar14 != 0x10)) {
          *(undefined1 *)(DAT_4384d834 + 0x4384d1e0) = 0;
          *(undefined1 *)(DAT_4384d838 + 0x4384d1e8) = 0;
        }
        iVar14 = DAT_4384d83c;
        cVar50 = cVar8;
        if (*(char *)((int)param_14 + 0x91f) != '\0') {
          cVar50 = '\0';
          *(undefined1 *)(param_14 + 0x354) = 0;
          *(undefined1 *)((int)param_14 + 0x6a9) = 0;
          *(undefined2 *)(iVar14 + 0x4384d1fc) = 0;
          *(undefined1 *)(DAT_4384d840 + 0x4384d208) = 0;
        }
        *(undefined1 *)(param_14 + 0x355) = *(undefined1 *)(DAT_4384d844 + 0x4384d210);
      }
      else {
LAB_4384d21a:
        cVar2 = *(char *)(iVar21 + 0xa5);
        if (cVar2 == '\x01') {
          iVar35 = 0;
          cVar50 = '\x01';
        }
        else {
          if ((cVar33 != '\x02') && (cVar2 != '\x02')) {
            if ((cVar33 == '\x03') || (cVar2 == '\x03')) {
LAB_4384d28e:
              iVar35 = 0;
              goto LAB_4384d290;
            }
            cVar50 = cVar8;
            if ((cVar33 == '\x04') || (cVar2 == '\x04')) {
              if ((ushort)(*param_14 - 0x303U) < 2) {
LAB_4384d276:
                if (cVar8 == '\x01') goto LAB_4384d28e;
              }
            }
            else {
              if ((cVar33 == '\x05') || (cVar2 == '\x05')) goto LAB_4384d28e;
              if (((cVar33 == '\x06') || (cVar2 == '\x06')) && (*param_14 == 0x385))
              goto LAB_4384d276;
            }
          }
          cVar50 = '\0';
          iVar35 = 0;
        }
      }
    }
    else {
      if (cVar33 != '\x01') goto LAB_4384d21a;
      iVar35 = 0;
      cVar50 = '\x01';
    }
LAB_4384d290:
    cVar33 = *(char *)(DAT_4384d848 + 0x4384d298);
    if ((byte)(cVar33 - 1U) < 0xfe) {
      *(char *)(DAT_4384d848 + 0x4384d298) = cVar33 + '\x01';
    }
    cVar33 = *(char *)(*(int *)(iVar53 + DAT_4384d7e8) + 0x29);
    if (cVar33 == '\x02') {
      bVar19 = *(char *)(DAT_4384d84c + 0x4384d2c6) << 3 | *(char *)((int)param_14 + 0x6a9) << 2 |
               *(byte *)(param_14 + 0x354) | *(char *)(DAT_4384d850 + 0x4384d2da) << 4 |
               (byte)(iVar20 << 5) | cVar50 << 7;
LAB_4384d378:
      *(byte *)(param_14 + 0x367) = bVar19;
    }
    else {
      if (cVar33 == '\x03') {
        bVar19 = *(byte *)(DAT_4384d854 + 0x4384d2f8);
        *(byte *)(param_14 + 0x367) = bVar19;
        if (*(char *)((int)param_14 + 0x365) == '\0') {
          bVar19 = bVar19 & 0xf7;
        }
        else {
          bVar19 = bVar19 | 8;
        }
        *(byte *)(param_14 + 0x367) = bVar19;
        if (*(char *)(param_5 + 0xd4) == '\0') {
          bVar19 = *(byte *)(param_14 + 0x367) & 0xef;
        }
        else {
          bVar19 = *(byte *)(param_14 + 0x367) | 0x10;
        }
        *(byte *)(param_14 + 0x367) = bVar19;
        if ((ushort)(*param_14 - 0x303U) < 2) {
          bVar19 = *(byte *)(param_14 + 0x367) | 0x20;
        }
        else {
          bVar19 = *(byte *)(param_14 + 0x367) & 0xdf;
        }
        *(byte *)(param_14 + 0x367) = bVar19;
        if (*(int *)(param_14 + 0x162) == 0) {
          bVar19 = *(byte *)(param_14 + 0x367) & 0xbf;
        }
        else {
          bVar19 = *(byte *)(param_14 + 0x367) | 0x40;
        }
        *(byte *)(param_14 + 0x367) = bVar19;
        if (*(int *)(param_14 + 0x21c) == 0) {
          bVar19 = *(byte *)(param_14 + 0x367) & 0x7f;
        }
        else {
          bVar19 = *(byte *)(param_14 + 0x367) | 0x80;
        }
        goto LAB_4384d378;
      }
      if (cVar33 == '\x04') {
        bVar19 = (byte)*(undefined4 *)(param_14 + 0x160);
        goto LAB_4384d378;
      }
    }
    if (cVar50 == '\x01') {
      iVar35 = iVar35 + 1;
    }
    if (iVar20 != 0) {
      iVar35 = iVar35 + 2;
    }
    uVar12 = iVar35 + *(int *)(param_14 + 0x160) * 0x100;
    uVar29 = uVar12 & 0xffff;
    if ((*(char *)(*(int *)(iVar53 + DAT_4384d858) + 0xbc) == '\0') &&
       (*(ushort *)(DAT_4384d85c + 0x4384d3aa) != uVar29)) {
      FUN_43857f04(0x301,uVar29);
    }
    *(short *)(DAT_4384d860 + 0x4384d3c8) = (short)uVar12;
    cStack_59 = cVar50;
  }
  iVar20 = FUN_437284b4();
  if (iVar20 != 0) {
    cStack_59 = '\0';
  }
  uStack_57 = *(undefined1 *)(param_5 + 0x11e);
  if (*param_14 == 0x370) {
    uStack_5e = *(undefined1 *)((int)param_14 + 0x38d);
    uStack_5d = (undefined1)param_14[0x1c6];
    uStack_5c = (undefined1)param_14[0x1c7];
  }
  else {
    uStack_5e = FUN_4384a190(param_5);
    *(undefined1 *)((int)param_14 + 0x38d) = uStack_5e;
    uStack_5d = FUN_4384a1c0(sStack_70,param_5);
    *(undefined1 *)(param_14 + 0x1c6) = uStack_5d;
    uStack_5c = FUN_4384a1fc(param_14,param_5);
    *(undefined1 *)(param_14 + 0x1c7) = uStack_5c;
  }
  uStack_56 = *(undefined1 *)(param_5 + 0x10a);
  uStack_55 = *(undefined1 *)(param_5 + 0x10b);
  iVar20 = FUN_436e8328();
  if (iVar20 == 2) {
    bStack_54 = thunk_FUN_436f97a0();
    bStack_53 = thunk_FUN_436f97ac();
    uStack_6c = thunk_FUN_436f9794();
  }
  else {
    iVar20 = FUN_436e8328();
    if (iVar20 == 1) {
      iVar20 = FUN_436e8700();
      if (iVar20 != 0) {
        iVar20 = FUN_436e8398();
        if (iVar20 < 4) {
          bStack_54 = 0;
          uStack_6c = 0;
          puVar37 = (undefined1 *)(DAT_4384d868 + 0x4384d498);
        }
        else {
          bStack_54 = 1;
          if ((char)param_14[0x368] == '\0') goto LAB_4384d498;
          puVar37 = (undefined1 *)(DAT_4384d864 + 0x4384d488);
        }
        *puVar37 = 1;
      }
LAB_4384d498:
      bStack_53 = *(byte *)(DAT_4384d86c + 0x4384d49e);
    }
    else {
      bStack_54 = *(byte *)(param_14 + 0x2a7);
      bStack_53 = 1;
    }
  }
  sVar9 = param_14[0x24b];
  sVar10 = *(short *)((int)param_2 + 0x2ce);
  param_17[999] = sVar9;
  param_17[1000] = sVar10;
  *(short *)(uVar42 + 0xb78) = sVar9;
  *(short *)(uVar42 + 0xb7a) = sVar10;
  uVar36 = *(undefined4 *)(param_13 + 0xc88);
  *(undefined4 *)(param_17 + 0x3ea) = uVar36;
  *(undefined4 *)(uVar42 + 0xb7c) = uVar36;
  uStack_51 = *(char *)(param_5 + 0x11f) != '\0';
  bStack_50 = *(char *)(param_5 + 0x108) == '\0' && *(char *)(param_5 + 0x107) != '\0';
  iVar20 = *(int *)(param_5 + 0xb8);
  if (iVar20 == 0x404) {
    bStack_4f = 2;
  }
  else if ((iVar20 == DAT_4384d7d4) || (iVar20 == DAT_4384d7d8)) {
    bStack_4f = 1;
  }
  else {
    bStack_4f = 0;
  }
  iVar20 = *(int *)(param_5 + 0xb8);
  if ((iVar20 == DAT_4384d7d8) || (iVar20 == DAT_4384d7d4)) {
    bStack_4e = true;
  }
  else if ((iVar20 != 0x404) || (bStack_4e = true, *(char *)(param_5 + 0xa0) != '\x01')) {
    bStack_4e = false;
  }
  bVar19 = *(byte *)(*(int *)(iVar53 + DAT_4384d870) + 0xb);
  if ((bVar19 != 0) && (bStack_4e = bVar19 < 3, bStack_4f = bVar19, !bStack_4e)) {
    bStack_4f = 0;
  }
  if ((*(char *)(*(int *)(iVar53 + DAT_4384d870) + 0x30) == '\x01') &&
     (iVar20 = FUN_43b09420(param_14), iVar20 != 0)) {
    bStack_4e = false;
  }
  if ((*(char *)(iVar21 + 0x42) == '\0') || ((char)param_14[0x2b7] == '\0')) {
    FUN_43adcd7e(0);
    FUN_43adcd8c(0);
    FUN_43adcd9a(0);
    FUN_43adcda8(0);
    FUN_43adcdb6(0);
    FUN_43adcdc4(0);
    sVar9 = 0;
  }
  else {
    FUN_43adcd7e(1);
    uVar36 = 0;
    if ((*(char *)(param_6 + 0x6b) != '\0') && (uVar36 = 0, *(char *)(param_6 + 0x6c) != '\0')) {
      uVar36 = 1;
    }
    FUN_43adcd8c(uVar36);
    uVar36 = 0;
    if ((*(char *)(param_3 + 0x15) != '\0') && (uVar36 = 0, *(char *)(param_3 + 0x17) != '\0')) {
      uVar36 = 1;
    }
    FUN_43adcd9a(uVar36);
    FUN_43adcda8((char)param_14[0x239]);
    uStack_38 = *param_2;
    FUN_43aec180(0xffff,&uStack_38);
    FUN_43adcdb6(uStack_38 & 0xffff);
    FUN_43adcdc4(param_14[0x8e]);
    sVar9 = param_14[0x8f];
  }
  FUN_43adcdd2(sVar9);
  cStack_52 = *(char *)(*(int *)(iVar53 + DAT_4384d7e8) + 0x29);
  if (cStack_52 == '\x01') {
    uStack_6c = param_14[0x28e];
  }
  else {
    if (cStack_52 == '\x02') {
      uStack_6c = param_14[699];
      asStack_74[0] = *param_14;
      sStack_70 = param_14[3];
    }
    else {
      if (1 < (byte)(cStack_52 - 3U)) goto LAB_4384d66c;
      asStack_74[0] = *param_14;
      sStack_70 = param_14[3];
    }
    uStack_6e = (ushort)*(byte *)(param_14 + 0x367);
  }
LAB_4384d66c:
  FUN_438e5c58(param_3,param_14);
  FUN_438fb0cc(asStack_74);
  if (*(char *)(param_5 + 0x124) == '\x01') {
    uStack_5a = *param_14 == 0x370;
    FUN_438fb1a0(asStack_74);
  }
  sVar9 = (*(byte *)(param_5 + 0x10a) & 3) * 4 + (bStack_50 & 1) * 0x10 +
          (*(byte *)((int)param_14 + 0x38d) & 3) + (*(byte *)(param_5 + 2) & 1) * 0x20 +
          (*(byte *)(param_5 + 0x11e) & 1) * 0x40 + (*(byte *)(param_5 + 0x11f) & 1) * 0x80 +
          (*(byte *)(param_5 + 0x10b) & 1) * 0x100 + (bStack_54 & 1) * 0x200 +
          (bStack_53 & 1) * 0x400;
  if (uStack_6c != 0) {
    sVar9 = sVar9 + 0x800;
  }
  if ((*(char *)(*(int *)(iVar53 + DAT_4384d858) + 0xbc) == '\0') &&
     (*(short *)(DAT_4384d874 + 0x4384d726) != sVar9)) {
    FUN_43857f04(0x304,sVar9);
  }
  *(short *)(DAT_4384d878 + 0x4384d73a) = sVar9;
  if (((((short)param_2[0x14] != 0) && (iVar20 = FUN_435611f0(DAT_4384d7dc,auStack_4c), iVar20 == 0)
       ) && (iStack_40 != 0)) &&
     (iVar20 = FUN_435612d0(DAT_4384d7dc,&puStack_3c,2,0), uVar36 = DAT_4384d7dc, iVar20 == 0)) {
    *(short *)puStack_3c = (short)param_2[0x14];
    FUN_43561228(uVar36);
    FUN_435612ec(DAT_4384d7dc,puStack_3c);
  }
  sVar9 = param_17[0xb];
  iVar20 = *(int *)(iVar53 + DAT_4384d87c);
  *(short *)(iVar20 + 0x3e2) = *param_17;
  *(short *)(iVar20 + 0x3e4) = sVar9;
  if (0x1b < **(byte **)(iVar53 + DAT_4384d880)) {
    **(byte **)(iVar53 + DAT_4384d880) = 0x1b;
  }
  if (0x1b < **(byte **)(iVar53 + DAT_4384d884)) {
    **(byte **)(iVar53 + DAT_4384d884) = 0x1b;
  }
  iVar20 = FUN_436ef7cc();
  *(int *)(iVar20 + 8) = param_15 + 0x33c;
  FUN_43840f88(param_14,param_3);
  return;
}

