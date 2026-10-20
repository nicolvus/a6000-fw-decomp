
void FUN_437b0810(undefined2 *param_1,int param_2,int param_3,int param_4,int param_5,
                 undefined2 *param_6,int param_7,int param_8,int param_9,int param_10,int param_11,
                 int param_12,int param_13,int param_14,char param_15)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  short sVar7;
  short sVar8;
  undefined4 uVar9;
  int iVar10;
  undefined1 uVar11;
  ushort uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  undefined2 local_3c;
  undefined2 local_3a;
  undefined2 local_38;
  undefined4 local_34;
  undefined2 local_2e;
  undefined2 local_2c;
  undefined2 local_2a [3];
  
  local_2c = 0x168;
  iVar16 = DAT_437b1038 + 0x437b0836;
  local_2a[0] = 1;
  local_34 = 1;
  FUN_4384a5a0(param_2,param_1);
  uVar9 = FUN_43aef21c(*(undefined4 *)(param_1 + 0x15e));
  FUN_4384a608(&local_3c,uVar9);
  if ((*(char *)(param_1 + 0x44) == '\x01') && (param_1[0x357] == 0)) {
    uVar6 = param_1[0x4c];
  }
  else {
    uVar6 = *(undefined2 *)(param_2 + 0x152);
  }
  iVar13 = *(int *)(param_1 + 0x27c);
  if (*(int *)(param_1 + 0x14a) == 9) {
    uVar6 = *(undefined2 *)(param_10 + 0x9e);
  }
  if (param_15 == '\x01') {
    if (iVar13 != 1) {
      uVar6 = param_1[0x8e];
      goto LAB_437b08b4;
    }
  }
  else {
LAB_437b08b4:
    local_38 = uVar6;
    if (((iVar13 != 0) && (iVar13 != 1)) && (iVar13 = *(int *)(param_1 + 0x17a), iVar13 == 3)) {
      iVar13 = 1;
    }
  }
  FUN_4384a068(param_1,local_38,local_2a,&local_34,&local_2c,iVar13,param_2);
  *(undefined4 *)(param_12 + 0x18) = *(undefined4 *)(param_1 + 0x148);
  *(undefined4 *)(param_12 + 0x1c) = *(undefined4 *)(param_1 + 0x14a);
  *(undefined4 *)(param_12 + 0x20) = *(undefined4 *)(param_1 + 0x14c);
  *(char *)(param_12 + 0x24) = (char)*(undefined4 *)(param_1 + 0x6a);
  uVar6 = *(undefined2 *)(param_2 + 0x164);
  *(undefined4 *)(param_12 + 0x28) = *(undefined4 *)(param_1 + 0x1a4);
  uVar4 = *(undefined2 *)(param_3 + 0x1c0);
  *(undefined2 *)(param_12 + 0x2e) = uVar6;
  *(undefined2 *)(param_12 + 0x2c) = uVar4;
  uVar12 = (ushort)*(byte *)(param_13 + 2);
  uVar6 = *(undefined2 *)(param_3 + 0x50);
  if (uVar12 == 1) {
    *(undefined2 *)(param_12 + 0x2e) = *(undefined2 *)(param_13 + 0x210);
  }
  uVar4 = param_1[0x178];
  if (param_15 == '\x01') {
    uVar12 = param_1[0x8f];
  }
  uVar5 = param_1[0x357];
  *(undefined2 *)(param_12 + 0x30) = uVar6;
  if (param_15 == '\x01') {
    *(ushort *)(param_12 + 0x2e) = uVar12;
  }
  *(undefined4 *)(param_12 + 0x34) = *(undefined4 *)(param_1 + 0x1de);
  uVar9 = *(undefined4 *)(param_1 + 0x1e0);
  *(undefined2 *)(param_12 + 0x3c) = uVar4;
  *(undefined2 *)(param_12 + 0x3e) = uVar5;
  *(undefined4 *)(param_12 + 0x38) = uVar9;
  *(undefined2 *)(param_12 + 0x40) = param_1[0x1b];
  *(undefined4 *)(param_12 + 0x44) = *(undefined4 *)(param_1 + 0x14e);
  *(undefined4 *)(param_12 + 0x48) = *(undefined4 *)(param_1 + 0x154);
  *(undefined1 *)(param_12 + 0x4c) = *(undefined1 *)(param_1 + 0x1eb);
  *(undefined1 *)(param_12 + 0x4d) = *(undefined1 *)(param_1 + 0x1ea);
  if (*(int *)(param_1 + 0x20c) == 1) {
    *(undefined1 *)(param_12 + 0x4e) = *(undefined1 *)(param_5 + 0xbd0);
    *(undefined1 *)(param_12 + 0x4f) = *(undefined1 *)(param_5 + 0xbd2);
    *(undefined1 *)(param_12 + 0x50) = *(undefined1 *)(param_5 + 0xbd4);
    *(undefined1 *)(param_12 + 0x52) = *(undefined1 *)(param_5 + 0xbd7);
    *(undefined1 *)(param_12 + 0x54) = *(undefined1 *)(param_5 + 0xbda);
    *(undefined1 *)(param_12 + 0x55) = *(undefined1 *)(param_5 + 0xbdc);
    *(undefined1 *)(param_12 + 0x56) = *(undefined1 *)(param_5 + 0xbde);
    *(undefined1 *)(param_12 + 0x57) = *(undefined1 *)(param_5 + 0xbe0);
    *(undefined1 *)(param_12 + 0x140) = *(undefined1 *)(param_5 + 0xc7a);
    uVar9 = *(undefined4 *)(param_5 + 0xc7c);
  }
  else {
    *(undefined1 *)(param_12 + 0x4e) = *(undefined1 *)(param_5 + 0xbd1);
    *(undefined1 *)(param_12 + 0x4f) = *(undefined1 *)(param_5 + 0xbd3);
    *(undefined1 *)(param_12 + 0x50) = *(undefined1 *)(param_5 + 0xbd5);
    *(undefined1 *)(param_12 + 0x52) = *(undefined1 *)(param_5 + 0xbd9);
    *(undefined1 *)(param_12 + 0x54) = *(undefined1 *)(param_5 + 0xbdb);
    *(undefined1 *)(param_12 + 0x55) = *(undefined1 *)(param_5 + 0xbdd);
    *(undefined1 *)(param_12 + 0x56) = *(undefined1 *)(param_5 + 0xbdf);
    *(undefined1 *)(param_12 + 0x57) = *(undefined1 *)(param_5 + 0xbe1);
    *(undefined1 *)(param_12 + 0x140) = *(undefined1 *)(param_5 + 0xc7b);
    uVar9 = *(undefined4 *)(param_5 + 0xc80);
  }
  *(undefined4 *)(param_12 + 0x144) = uVar9;
  iVar14 = *(int *)(iVar16 + DAT_437b103c);
  if (((*(char *)(iVar14 + 0x51) != '\0') && (*(int *)(param_1 + 0x138) == 1)) &&
     (*(ushort *)(param_3 + 0x50) < *(ushort *)(iVar14 + 0x52))) {
    *(undefined1 *)(param_12 + 0x4e) = 1;
    *(undefined1 *)(param_12 + 0x54) = 4;
  }
  iVar15 = *(int *)(iVar16 + DAT_437b1040);
  if (*(char *)(iVar15 + 0x4c) != '\0') {
    bVar3 = *(byte *)(param_5 + 0xbdb);
    if (((*(char *)(param_5 + 0xbd9) == '\0') &&
        (*(ushort *)(param_2 + 0x15e) < *(ushort *)(iVar15 + 0x4e))) &&
       ((*(char *)(param_12 + 0x50) == '\0' &&
        (bVar3 = bVar3 + *(char *)(iVar15 + 0x4d), bVar3 = bVar3 & ~((char)bVar3 >> 0x1f),
        '\x05' < (char)bVar3)))) {
      bVar3 = 6;
    }
    *(byte *)(param_12 + 0x54) = bVar3;
    *(bool *)(param_12 + 0x4e) = bVar3 != 3;
  }
  *(undefined4 *)(param_12 + 0x14c) = *(undefined4 *)(param_5 + 0xc84);
  *(undefined4 *)(param_12 + 0x148) = *(undefined4 *)(param_5 + 0xc88);
  if (*(char *)(**(int **)(iVar16 + DAT_437b1044) + 0x1c8) == '\0') {
    uVar11 = *(undefined1 *)(param_5 + 0xbd6);
  }
  else if (*(char *)(param_8 + 0x30) == '\0') {
    *(bool *)(param_12 + 0x51) =
         (int)(uint)*(byte *)(**(int **)(iVar16 + DAT_437b1044) + 0x180) <=
         *(int *)(param_1 + 0x194);
    if (*(int *)(param_1 + 0x194) != 0) goto LAB_437b0aee;
    uVar11 = 1;
  }
  else {
    uVar11 = 1;
  }
  *(undefined1 *)(param_12 + 0x51) = uVar11;
LAB_437b0aee:
  *(undefined1 *)(param_12 + 0x53) = *(undefined1 *)(param_5 + 0xbd8);
  uVar6 = *(undefined2 *)(param_5 + 0xbe4);
  uVar4 = *(undefined2 *)(param_5 + 0xc68);
  uVar5 = *(undefined2 *)(param_5 + 0xc6a);
  *(undefined4 *)(param_12 + 0x60) = *(undefined4 *)(param_1 + 0x342);
  uVar9 = *(undefined4 *)(param_5 + 0xc74);
  *(undefined2 *)(param_12 + 0x58) = uVar6;
  *(undefined2 *)(param_12 + 0x5a) = uVar4;
  *(undefined4 *)(param_12 + 100) = uVar9;
  uVar9 = *(undefined4 *)(param_1 + 0x1da);
  *(undefined2 *)(param_12 + 0x5c) = uVar5;
  *(char *)(param_12 + 0x68) = (char)uVar9;
  *(char *)(param_12 + 0x69) = (char)*(undefined4 *)(param_1 + 0x15a);
  uVar6 = param_1[0x170];
  *(undefined2 *)(param_12 + 0x6a) = param_1[0x16f];
  *(undefined2 *)(param_12 + 0x6c) = uVar6;
  *(undefined1 *)(param_12 + 0x6e) = *(undefined1 *)(param_4 + 0xc35);
  uVar6 = *(undefined2 *)(param_4 + 0xc38);
  uVar4 = *(undefined2 *)(param_4 + 0xc3c);
  *(undefined2 *)(param_12 + 0x72) = *(undefined2 *)(param_4 + 0xc3a);
  iVar16 = *(int *)(param_1 + 0x14e);
  *(undefined2 *)(param_12 + 0x70) = uVar6;
  *(undefined2 *)(param_12 + 0x74) = uVar4;
  if ((iVar16 == 3) && (*(int *)(param_1 + 0x14a) == 3)) {
    uVar11 = 1;
  }
  else {
    uVar11 = *(undefined1 *)(param_8 + 0xc);
  }
  *(undefined1 *)(param_12 + 0x76) = uVar11;
  *(undefined1 *)(param_12 + 0x77) = *(undefined1 *)(param_8 + 0x30);
  uVar6 = *(undefined2 *)(param_8 + 0x2c6);
  *(undefined2 *)(param_12 + 0x78) = *(undefined2 *)(param_8 + 0x2be);
  *(undefined2 *)(param_12 + 0x7a) = uVar6;
  *(undefined1 *)(param_12 + 0x7c) = *(undefined1 *)(param_8 + 0x3e);
  *(undefined1 *)(param_12 + 0x7d) = *(undefined1 *)(param_8 + 0x3d);
  *(undefined1 *)(param_12 + 0x7e) = *(undefined1 *)(param_8 + 0x3c);
  *(undefined1 *)(param_12 + 0x7f) = *(undefined1 *)(param_7 + 0x42);
  *(undefined1 *)(param_12 + 0x80) = *(undefined1 *)(param_8 + 0x34);
  *(undefined1 *)(param_12 + 0x81) = *(undefined1 *)((int)param_1 + 0x657);
  *(undefined1 *)(param_12 + 0x82) = *(undefined1 *)(param_1 + 0x32c);
  uVar6 = *(undefined2 *)(param_8 + 0x46c);
  uVar4 = *(undefined2 *)(param_8 + 0x4f2);
  *(undefined2 *)(param_12 + 0x84) = *(undefined2 *)(param_8 + 0x46a);
  uVar9 = *(undefined4 *)(param_1 + 0x328);
  uVar5 = *(undefined2 *)(param_8 + 0x4f4);
  *(undefined2 *)(param_12 + 0x86) = uVar6;
  *(undefined4 *)(param_12 + 0x88) = uVar9;
  uVar9 = *(undefined4 *)(param_1 + 800);
  *(undefined2 *)(param_12 + 0x132) = uVar4;
  *(undefined4 *)(param_12 + 0x8c) = uVar9;
  *(undefined2 *)(param_12 + 0x134) = uVar5;
  uVar6 = *(undefined2 *)(param_8 + 0x504);
  uVar4 = *(undefined2 *)(param_8 + 0x506);
  uVar5 = *(undefined2 *)(param_8 + 0x508);
  *(undefined2 *)(param_12 + 0x136) = *(undefined2 *)(param_8 + 0x4f6);
  *(undefined2 *)(param_12 + 0x138) = uVar6;
  *(undefined2 *)(param_12 + 0x13a) = uVar4;
  *(undefined2 *)(param_12 + 0x13c) = uVar5;
  *(undefined1 *)(param_12 + 0x13e) = *(undefined1 *)(param_8 + 0x50a);
  *(undefined2 *)(param_12 + 0xba) = *(undefined2 *)(param_8 + 0x40);
  iVar16 = 0;
  do {
    iVar15 = param_8 + iVar16;
    iVar10 = param_12 + iVar16;
    iVar16 = iVar16 + 2;
    *(undefined2 *)(iVar10 + 0x116) = *(undefined2 *)(iVar15 + 0x46e);
  } while (iVar16 != 0x1c);
  *(bool *)(param_12 + 0x90) = *(int *)(param_1 + 0x34c) == 1;
  FUN_439c5320(param_12 + 0x92,param_8 + 0x30e,0x14);
  FUN_439c5320(param_12 + 0xa6,param_8 + 0x322,0x14);
  uVar4 = param_1[0x38c];
  uVar6 = *param_6;
  *(undefined2 *)(param_12 + 0x112) = param_1[0x38b];
  *(undefined2 *)(param_12 + 0x114) = uVar4;
  *(undefined2 *)(param_12 + 0xbc) = uVar6;
  *(undefined1 *)(param_12 + 0xbe) = *(undefined1 *)(param_1 + 4);
  *(undefined2 *)(param_12 + 0xc0) = *param_1;
  *(undefined1 *)(param_12 + 0xc2) = *(undefined1 *)(param_9 + 0x3fd);
  *(undefined1 *)(param_12 + 0xc4) = *(undefined1 *)(param_9 + 0x809);
  uVar6 = *(undefined2 *)(param_9 + 0x252);
  *(undefined4 *)(param_12 + 0xd0) = *(undefined4 *)(param_9 + 0x23c);
  uVar4 = *(undefined2 *)(param_3 + 0x48);
  *(undefined4 *)(param_12 + 0xd4) = *(undefined4 *)(param_9 + 0x240);
  *(undefined4 *)(param_12 + 0xd8) = *(undefined4 *)(param_9 + 0x244);
  *(undefined4 *)(param_12 + 0xdc) = *(undefined4 *)(param_9 + 0x248);
  *(undefined4 *)(param_12 + 0xe0) = *(undefined4 *)(param_9 + 0x24c);
  uVar5 = *(undefined2 *)(param_9 + 0x250);
  uVar2 = *(undefined2 *)(param_9 + 0x254);
  *(undefined2 *)(param_12 + 0xe6) = uVar6;
  *(undefined2 *)(param_12 + 0xe4) = uVar5;
  *(undefined2 *)(param_12 + 0xe8) = uVar2;
  *(undefined2 *)(param_12 + 0xea) = uVar4;
  *(undefined1 *)(param_12 + 0xed) = *(undefined1 *)((int)param_1 + 0x3d5);
  *(undefined1 *)(param_12 + 0xf2) = *(undefined1 *)(param_11 + 0xe);
  *(undefined1 *)(param_12 + 0xf1) = *(undefined1 *)(param_11 + 0xf);
  *(undefined1 *)(param_12 + 0xef) = *(undefined1 *)(param_11 + 0x10);
  *(undefined1 *)(param_12 + 0xf0) = *(undefined1 *)(param_11 + 0x13);
  *(undefined1 *)(param_12 + 0xec) = *(undefined1 *)(param_3 + 0x34);
  *(char *)(param_12 + 0xee) = (char)*(undefined4 *)(param_1 + 0x20a);
  uVar6 = *(undefined2 *)(param_10 + 0xa6);
  uVar4 = *(undefined2 *)(param_10 + 0xa8);
  *(undefined2 *)(param_12 + 0xf8) = *(undefined2 *)(param_10 + 0xaa);
  uVar5 = *(undefined2 *)(param_10 + 0x98);
  uVar2 = *(undefined2 *)(param_10 + 0xac);
  *(undefined2 *)(param_12 + 0xf4) = uVar6;
  *(undefined2 *)(param_12 + 0xf6) = uVar4;
  uVar6 = *(undefined2 *)(param_10 + 0x94);
  uVar4 = *(undefined2 *)(param_10 + 0x96);
  *(undefined2 *)(param_12 + 0x100) = uVar5;
  uVar9 = *(undefined4 *)(param_1 + 0x206);
  *(undefined2 *)(param_12 + 0xfa) = uVar2;
  *(undefined2 *)(param_12 + 0xfc) = uVar6;
  *(undefined4 *)(param_12 + 0x10c) = uVar9;
  *(undefined2 *)(param_12 + 0xfe) = uVar4;
  *(undefined1 *)(param_12 + 0x110) = 0;
  *(undefined1 *)(param_12 + 0x111) = 0;
  *(undefined1 *)(param_12 + 0x13f) = *(undefined1 *)(param_1 + 0x1ee);
  if (*(int *)(param_1 + 0x27c) == 2) {
    uVar6 = param_1[0x286];
  }
  else {
    uVar6 = FUN_436ef820(param_1[0x287]);
  }
  sVar7 = *(short *)(param_2 + 0x15e);
  *(undefined2 *)(param_12 + 0x150) = uVar6;
  cVar1 = *(char *)(iVar14 + 0x7c);
  *(short *)(param_12 + 0x152) = sVar7;
  *(short *)(param_12 + 0x154) = sVar7;
  if (cVar1 == '\x01') {
    *(short *)(param_12 + 0x154) = sVar7 + param_1[0x2cc];
  }
  uVar6 = *(undefined2 *)(param_2 + 0x160);
  uVar9 = *(undefined4 *)(param_1 + 0x1ec);
  *(undefined2 *)(param_12 + 0x156) = *(undefined2 *)(param_2 + 0x14e);
  *(undefined2 *)(param_12 + 0x158) = uVar6;
  iVar16 = FUN_43830044(uVar9);
  if (iVar16 != 0) {
    *(short *)(param_12 + 0x158) = (short)iVar16 + 0x1000;
  }
  *(undefined1 *)(param_12 + 0x298) = *(undefined1 *)(param_14 + 0xd6);
  *(undefined1 *)(param_12 + 0x299) = *(undefined1 *)(param_14 + 0xd7);
  uVar4 = FUN_436f070c();
  uVar6 = *(undefined2 *)(param_2 + 0x164);
  *(undefined2 *)(param_12 + 0x15c) = *(undefined2 *)(param_2 + 0x162);
  *(undefined2 *)(param_12 + 0x15e) = uVar6;
  *(undefined2 *)(param_12 + 0x15a) = uVar4;
  sVar7 = *(short *)(param_14 + 0xec);
  if (*(char *)(param_13 + 2) == '\x01') {
    *(undefined2 *)(param_12 + 0x15e) = *(undefined2 *)(param_13 + 0x210);
  }
  uVar4 = FUN_439027ec((int)sVar7,0x100);
  uVar6 = *(undefined2 *)(param_14 + 0x74);
  *(undefined2 *)(param_12 + 0x164) = param_1[0xca];
  sVar7 = *(short *)(param_2 + 0x164);
  *(undefined2 *)(param_12 + 0x162) = uVar6;
  *(short *)(param_12 + 0x166) = 0x1000 - sVar7;
  *(undefined2 *)(param_12 + 0x160) = uVar4;
  *(undefined2 *)(param_12 + 0x2a8) = *(undefined2 *)(param_14 + 0xde);
  if (*(char *)(param_13 + 2) == '\x01') {
    *(short *)(param_12 + 0x166) = 0x1000 - *(short *)(param_13 + 0x210);
  }
  if (*(char *)(param_13 + 2) == '\0') {
    uVar6 = *(undefined2 *)(param_2 + 0x154);
  }
  else {
    uVar6 = *(undefined2 *)(param_13 + 0x210);
  }
  uVar5 = FUN_43b07522(uVar6);
  uVar6 = *(undefined2 *)(param_3 + 0x50);
  *(short *)(param_12 + 0x16e) = (short)local_34;
  *(undefined4 *)(param_12 + 0x170) = local_34;
  uVar4 = *(undefined2 *)(param_2 + 4);
  *(undefined2 *)(param_12 + 0x16a) = uVar6;
  *(undefined2 *)(param_12 + 0x16c) = local_2a[0];
  *(undefined2 *)(param_12 + 0x2aa) = uVar4;
  *(undefined2 *)(param_12 + 0x168) = uVar5;
  *(undefined1 *)(param_12 + 0x2ac) = *(undefined1 *)(param_2 + 0x14);
  uVar6 = *(undefined2 *)(param_2 + 0x14e);
  *(undefined4 *)(param_12 + 0x2b0) = *(undefined4 *)(param_1 + 0x224);
  if ((*(int *)(param_1 + 0x27e) != 0) || (uVar4 = uVar6, *(int *)(param_1 + 0x282) != 1)) {
    uVar4 = *(undefined2 *)(param_2 + 0x15e);
  }
  FUN_4384a710(param_1,uVar6,uVar4,&local_2e,iVar13,1);
  uVar6 = *(undefined2 *)(param_10 + 0x9a);
  *(undefined4 *)(param_12 + 0x178) = *(undefined4 *)(param_1 + 0x194);
  *(undefined2 *)(param_12 + 0x174) = local_2e;
  *(undefined2 *)(param_12 + 0x180) = uVar6;
  FUN_4382fd48();
  uVar6 = FUN_43b074e4();
  *(undefined1 *)(param_12 + 0x186) = *(undefined1 *)(iVar14 + 0x9e);
  *(undefined1 *)(param_12 + 0x29a) = 0;
  *(undefined1 *)(param_12 + 0x29b) = 0;
  iVar16 = *(int *)(param_1 + 0x27c);
  *(undefined2 *)(param_12 + 0x184) = uVar6;
  if ((iVar16 == 1) && (*(int *)(param_1 + 0x280) == 5)) {
    sVar7 = FUN_436f0174();
    *(short *)(param_12 + 0x29e) = sVar7 + 0x1000;
    uVar6 = FUN_436f01f8();
    *(undefined2 *)(param_12 + 0x2a2) = 0x1155;
    *(undefined2 *)(param_12 + 0x2a4) = 0x1000;
    *(undefined2 *)(param_12 + 0x2a0) = uVar6;
  }
  if (param_15 == '\x01') {
    if (*(int *)(param_1 + 0x27c) == 1) {
      *(undefined2 *)(param_12 + 0x152) = param_1[0x8c];
      *(undefined2 *)(param_12 + 0x156) = local_3c;
      *(undefined2 *)(param_12 + 0x158) = local_3a;
    }
    else {
      uVar6 = param_1[0x8c];
      uVar4 = param_1[0x8d];
      *(undefined2 *)(param_12 + 0x152) = uVar6;
      *(undefined2 *)(param_12 + 0x156) = uVar6;
      *(undefined2 *)(param_12 + 0x158) = uVar4;
    }
    iVar16 = FUN_43830044(*(undefined4 *)(param_1 + 0x1ec));
    if (iVar16 != 0) {
      *(short *)(param_12 + 0x158) = (short)iVar16 + 0x1000;
    }
    uVar6 = param_1[0x8f];
    sVar7 = param_1[0x93];
    *(undefined2 *)(param_12 + 0x15c) = param_1[0x8e];
    *(undefined2 *)(param_12 + 0x15e) = uVar6;
    *(short *)(param_12 + 0x166) = 0x1000 - sVar7;
    uVar6 = FUN_43b07522();
    iVar16 = *(int *)(param_1 + 0x27e);
    *(undefined2 *)(param_12 + 0x168) = uVar6;
    if ((iVar16 != 0) || (uVar6 = *(undefined2 *)(param_12 + 0x156), *(int *)(param_1 + 0x282) != 1)
       ) {
      uVar6 = *(undefined2 *)(param_12 + 0x152);
    }
    FUN_4384a710(param_1,*(undefined2 *)(param_12 + 0x156),uVar6,&local_2e,iVar13,1);
    *(undefined2 *)(param_12 + 0x174) = local_2e;
  }
  iVar16 = FUN_43b07418(*(undefined2 *)(param_2 + 0x14e));
  sVar7 = FUN_436ef8f8();
  sVar8 = FUN_436ef9a0(param_1[0x287]);
  uVar9 = FUN_43b07418(sVar7 + sVar8);
  sVar7 = FUN_4355fd68(iVar16 * 400,uVar9);
  *(undefined2 *)(param_12 + 0x182) = 0;
  *(undefined2 *)(param_12 + 0x29c) = 0;
  *(undefined2 *)(param_12 + 0x2b4) = *(undefined2 *)(param_14 + 0x156);
  *(short *)(param_12 + 0x2a6) = sVar7 + -400;
  return;
}

