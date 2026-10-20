/* S41: read-only exports. */

/* 437a9d30 */

void FUN_437a9d30(int *param_1,undefined2 *param_2,int param_3,int param_4)

{
  undefined2 *puVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  byte bVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  ushort uVar7;
  ushort uVar8;
  short sVar9;
  short sVar10;
  undefined2 *puVar11;
  int iVar12;
  undefined1 uVar13;
  undefined1 uVar14;
  int *piVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  char cVar19;
  char cVar20;
  bool bVar21;
  undefined1 auStack_54 [20];
  undefined2 uStack_40;
  undefined2 uStack_3c;
  ushort uStack_2c;
  ushort auStack_2a [3];
  
  piVar15 = (int *)param_1[1];
  iVar18 = DAT_437aa634 + 0x437a9d44;
  if (piVar15 != (int *)0x0) {
    piVar15[7] = param_3;
    *piVar15 = param_3 + 0x170;
    piVar15[8] = param_4;
    piVar15[4] = 0;
    piVar15[5] = 0;
    piVar15[6] = 0;
    piVar15[9] = 0;
    piVar15[1] = 0;
    piVar15[2] = 0;
  }
  iVar16 = DAT_437aa63c;
  if (*param_1 == 0) goto LAB_437aa622;
  *(bool *)*param_1 = *(char *)(DAT_437aa638 + 0x437a9d76) == '\x01';
  *(undefined1 *)(*param_1 + 1) = 1;
  *(undefined1 *)(*param_1 + 2) = 0;
  *(undefined1 *)(*param_1 + 3) = *(undefined1 *)(*(int *)(iVar18 + iVar16) + 0x6c);
  iVar16 = *param_1;
  uVar2 = *param_2;
  *(undefined4 *)(iVar16 + 4) = 0;
  *(undefined2 **)(iVar16 + 8) = param_2;
  *(int *)(iVar16 + 0xc) = param_3;
  *(int *)(iVar16 + 0x10) = param_4;
  *(undefined2 *)(iVar16 + 0x14) = uVar2;
  *(undefined1 *)(iVar16 + 0x16) = 0;
  if (*(int *)(param_2 + 0x48) - 5U < 3) {
    bVar21 = *(int *)(param_2 + 0xd8) == 2;
  }
  else {
    bVar21 = *(int *)(param_2 + 0x60) == 0x12;
  }
  *(bool *)(*param_1 + 0x83) = bVar21;
  iVar16 = *param_1;
  *(undefined4 *)(iVar16 + 0x84) = *(undefined4 *)(param_2 + 0xd8);
  uVar13 = *(undefined1 *)(param_2 + 0x48);
  switch(uVar13) {
  case 0x26:
    uVar13 = 0x1f;
    break;
  case 0x27:
  case 0x28:
    uVar13 = 0x20;
    break;
  case 0x29:
    uVar13 = 0x23;
  }
  *(undefined1 *)(iVar16 + 0x17) = uVar13;
  *(char *)(*param_1 + 0x18) = (char)*(undefined4 *)(param_2 + 0x4a);
  *(bool *)(*param_1 + 0x19) = *(int *)(param_2 + 0x48) == 0x1f || *(int *)(param_2 + 0x48) == 0x26;
  cVar19 = *(char *)(param_2 + 0x60);
  if (*(char *)(param_2 + 0x58) == '\x01') {
    cVar20 = '\0';
  }
  else {
    cVar20 = cVar19;
    if (cVar19 == '\x12') {
      cVar20 = '\0';
    }
  }
  *(char *)(*param_1 + 0x6d) = cVar19;
  *(char *)(*param_1 + 0x1a) = cVar20;
  *(bool *)(*param_1 + 0x6e) = *(int *)(param_2 + 0x62) == 1;
  *(undefined1 *)(*param_1 + 0x1b) = *(undefined1 *)(param_2 + 0x66);
  *(undefined1 *)(*param_1 + 0x1c) = *(undefined1 *)((int)param_2 + 0xcd);
  *(char *)(*param_1 + 0x1d) = (char)*(undefined4 *)(param_2 + 200);
  uVar13 = *(undefined1 *)((int)param_2 + 0x11f);
  uVar14 = *(undefined1 *)(param_2 + 0x90);
  if (*(char *)(*param_1 + 0x19) == '\x01') {
    uVar14 = 0;
    uVar13 = 0;
    cVar20 = '\0';
    cVar19 = '\0';
  }
  else if (*(int *)(param_2 + 0x92) == 0) {
    cVar19 = *(char *)((int)param_2 + 0x11d) + *(char *)(param_2 + 0x65) + *(char *)(param_2 + 100);
    cVar20 = *(char *)((int)param_2 + 0xcb) + *(char *)((int)param_2 + 0xc9) +
             *(char *)(param_2 + 0x8f);
    uVar13 = 0;
    uVar14 = 0;
  }
  else {
    cVar20 = '\0';
    cVar19 = '\0';
  }
  *(char *)(*param_1 + 0x1e) = cVar19;
  *(char *)(*param_1 + 0x1f) = cVar20;
  *(undefined1 *)(*param_1 + 0x20) = uVar13;
  *(undefined1 *)(*param_1 + 0x21) = uVar14;
  iVar16 = *(int *)(param_2 + 0x72);
  iVar12 = *(int *)(param_2 + 0x8c);
  if (*(int *)(param_2 + 0x68) == 0) {
    if (iVar12 == 0) {
      if (iVar16 == 0) {
        uVar13 = 0;
      }
      else {
        if (iVar16 - 1U < 2) {
          iVar12 = DAT_437aa644 + 0x437a9f02 + iVar16;
          goto LAB_437a9f02;
        }
        uVar13 = 0;
      }
    }
    else {
      uVar13 = 0;
      if (iVar12 - 1U < 7) {
        iVar12 = DAT_437aa640 + 0x437a9ef0 + iVar12;
LAB_437a9f02:
        uVar13 = *(undefined1 *)(iVar12 + -1);
      }
    }
  }
  else {
    uVar13 = (undefined1)*(int *)(param_2 + 0x68);
  }
  *(undefined1 *)(*param_1 + 0x22) = uVar13;
  if (*(int *)(param_2 + 0x8c) == 0) {
    uVar13 = 8;
  }
  else {
    uVar13 = *(undefined1 *)(param_2 + 0x8e);
  }
  *(undefined1 *)(*param_1 + 0x23) = uVar13;
  *(char *)(*param_1 + 0x24) = *(char *)(param_2 + 0x97) + *(char *)((int)param_2 + 0xd5);
  *(undefined1 *)(*param_1 + 0x25) = *(undefined1 *)((int)param_2 + 0x12f);
  *(undefined1 *)(*param_1 + 0x26) = *(undefined1 *)(param_2 + 0x6a);
  *(char *)(*param_1 + 0x27) = (char)*(undefined4 *)(param_2 + 0x70);
  *(char *)(*param_1 + 0x28) = (char)*(undefined4 *)(param_2 + 0x6e);
  *(char *)(*param_1 + 0x2a) = *(char *)(param_2 + 0x74) + *(char *)(param_2 + 0x94);
  *(char *)(*param_1 + 0x2c) = *(char *)((int)param_2 + 0xe9) + *(char *)((int)param_2 + 0x129);
  *(char *)(*param_1 + 0x2e) = *(char *)(param_2 + 0x75) + *(char *)(param_2 + 0x95);
  *(char *)(*param_1 + 0x2d) = *(char *)((int)param_2 + 0xeb) + *(char *)((int)param_2 + 299);
  *(char *)(*param_1 + 0x2f) = *(char *)(param_2 + 0x76) + *(char *)(param_2 + 0x96);
  *(char *)(*param_1 + 0x2b) = *(char *)((int)param_2 + 0xed) + *(char *)((int)param_2 + 0x12d);
  iVar16 = *param_1;
  if ((*(char *)(iVar16 + 0x2a) == '\0') && (*(int *)(iVar16 + 0x2c) == 0)) {
    bVar21 = *(char *)(iVar16 + 0x2b) != '\0';
  }
  else {
    bVar21 = true;
  }
  *(bool *)(iVar16 + 0x29) = bVar21;
  *(undefined1 *)(*param_1 + 0x30) = *(undefined1 *)((int)param_2 + 0x133);
  *(char *)(*param_1 + 0x31) = (char)*(undefined4 *)(param_2 + 0x8c);
  iVar16 = *param_1;
  *(undefined1 *)(iVar16 + 0x32) = *(undefined1 *)(param_2 + 0x81);
  *(undefined1 *)(iVar16 + 0x33) = *(undefined1 *)((int)param_2 + 0x103);
  *(undefined1 *)(iVar16 + 0x34) = *(undefined1 *)(param_2 + 0x82);
  *(char *)(iVar16 + 0x35) = (char)*(undefined4 *)(param_2 + 0x84) + -10;
  *(char *)(*param_1 + 0x37) = (char)*(undefined4 *)(param_2 + 0x86);
  iVar16 = *param_1;
  *(undefined1 *)(iVar16 + 0x36) = *(undefined1 *)(param_2 + 0x88);
  *(undefined1 *)(iVar16 + 0x38) = *(undefined1 *)((int)param_2 + 0x111);
  *(undefined1 *)(*param_1 + 0x39) = 0;
  *(undefined1 *)(*param_1 + 0x3a) = 0;
  *(char *)(*param_1 + 0x3b) = (char)*(undefined4 *)(param_2 + 0x28);
  iVar16 = *param_1;
  *(undefined4 *)(iVar16 + 0x3c) = *(undefined4 *)(param_2 + 0x2a);
  *(undefined1 *)(iVar16 + 0x40) = *(undefined1 *)(param_2 + 0x2c);
  iVar16 = *param_1;
  *(undefined4 *)(iVar16 + 0x44) = *(undefined4 *)(param_2 + 0x42);
  *(undefined1 *)(iVar16 + 0x48) = *(undefined1 *)((int)param_2 + 0x187);
  *(char *)(*param_1 + 0x49) = (char)*(undefined4 *)(param_2 + 0xe);
  *(undefined1 *)(*param_1 + 0x4a) = 0;
  *(char *)(*param_1 + 0x4b) = (char)*(undefined4 *)(param_2 + 0xd0);
  *(char *)(*param_1 + 0x4c) = (char)*(undefined4 *)(param_2 + 0x18);
  *(char *)(*param_1 + 0x4d) = (char)*(undefined4 *)(param_2 + 0x1a);
  *(char *)(*param_1 + 0x4e) = (char)*(undefined4 *)(param_2 + 0x20);
  *(char *)(*param_1 + 0x4f) = (char)*(undefined4 *)(param_2 + 0x22);
  *(char *)(*param_1 + 0x50) = (char)*(undefined4 *)(param_2 + 0x36);
  *(char *)(*param_1 + 0x52) = (char)*(undefined4 *)(param_2 + 0xaa);
  *(char *)(*param_1 + 0x53) = (char)*(undefined4 *)(param_2 + 0xac);
  iVar16 = *param_1;
  *(undefined2 *)(iVar16 + 0x54) = param_2[0xae];
  *(undefined1 *)(iVar16 + 0x58) = *(undefined1 *)(param_2 + 0xaf);
  *(undefined1 *)(*param_1 + 0x5a) = *(undefined1 *)((int)param_2 + 0x15f);
  *(undefined1 *)(*param_1 + 0x5c) = *(undefined1 *)(param_2 + 0xb0);
  *(undefined1 *)(*param_1 + 0x5e) = *(undefined1 *)((int)param_2 + 0x161);
  iVar16 = *param_1;
  *(undefined2 *)(iVar16 + 0x56) = param_2[0xb1];
  *(undefined1 *)(iVar16 + 0x59) = *(undefined1 *)(param_2 + 0xb2);
  *(undefined1 *)(*param_1 + 0x5b) = *(undefined1 *)((int)param_2 + 0x165);
  *(undefined1 *)(*param_1 + 0x5d) = *(undefined1 *)(param_2 + 0xb3);
  *(undefined1 *)(*param_1 + 0x5f) = *(undefined1 *)((int)param_2 + 0x167);
  iVar17 = 3;
  iVar12 = *param_1;
  puVar11 = param_2;
  iVar16 = iVar12;
  do {
    *(undefined2 *)(iVar16 + 0x70) = puVar11[0x77];
    *(undefined2 *)(iVar16 + 0x72) = puVar11[0x78];
    puVar1 = puVar11 + 0x79;
    puVar11 = puVar11 + 3;
    *(undefined2 *)(iVar16 + 0x74) = *puVar1;
    iVar16 = iVar16 + 6;
    iVar17 = iVar17 + -1;
  } while (iVar17 != 0);
  *(undefined1 *)(iVar12 + 0x82) = *(undefined1 *)(param_2 + 0x80);
  *(undefined1 *)(*param_1 + 0x88) = 0;
  iVar16 = *param_1;
  *(undefined1 *)(iVar16 + 0x8c) = *(undefined1 *)((int)param_2 + 0x6fd);
  *(char *)(iVar16 + 0x8d) = (char)*(undefined4 *)(param_2 + 0x254);
  *(undefined1 *)(*param_1 + 0x8e) = *(undefined1 *)(DAT_437aa648 + 0x437aa16c);
  iVar16 = *param_1;
  uVar13 = *(undefined1 *)(param_2 + 0x37f);
  *(undefined4 *)(iVar16 + 0x90) = 0;
  *(undefined1 *)(iVar16 + 0x94) = uVar13;
  *(char *)(iVar16 + 0x95) = (char)*(undefined4 *)(param_2 + 0x376);
  *(char *)(*param_1 + 0x96) = (char)*(undefined4 *)(param_2 + 0x37a);
  iVar16 = *param_1;
  *(undefined2 **)(iVar16 + 0xbc) = param_2 + 0x3b2;
  *(undefined2 **)(iVar16 + 0xc0) = param_2 + 0x680;
  *(undefined2 **)(iVar16 + 0xc4) = param_2 + 0x804;
  *(undefined1 *)(iVar16 + 0x97) = 0;
  *(undefined2 **)(iVar16 + 200) = param_2 + 0x884;
  *(undefined1 *)(*param_1 + 0x98) = 0;
  *(undefined1 *)(*param_1 + 0x99) = 0;
  iVar16 = *param_1;
  *(undefined1 *)(iVar16 + 0x9a) = 0;
  *(undefined1 *)(iVar16 + 0x9c) = 0;
  *(char *)(*param_1 + 0x9b) = (char)*(undefined4 *)(param_2 + 0xe0);
  iVar16 = *param_1;
  *(undefined4 *)(iVar16 + 0xa0) = *(undefined4 *)(param_2 + 0xdc);
  *(uint *)(iVar16 + 0xa4) = (uint)*(byte *)((int)param_2 + 0x701);
  *(undefined1 *)(iVar16 + 0xa8) = *(undefined1 *)(param_1[4] + 0x24);
  *(char *)(*param_1 + 0xa9) = (char)*(undefined4 *)(param_2 + 0x3a6);
  iVar12 = *param_1;
  iVar16 = *(int *)(param_2 + 0x352);
  *(undefined1 *)(iVar12 + 0xaa) = 0;
  *(undefined1 *)(iVar12 + 0xb5) = *(undefined1 *)(param_2 + 0x38d);
  if (iVar16 == 0) {
    *(undefined2 *)(iVar12 + 0xb6) = 0;
    *(undefined2 *)(iVar12 + 0xb8) = 0;
  }
  else {
    FUN_43ae92ee(iVar16,auStack_54);
    iVar16 = *param_1;
    *(undefined2 *)(iVar16 + 0xb6) = uStack_40;
    *(undefined2 *)(iVar16 + 0xb8) = uStack_3c;
  }
  iVar12 = *param_1;
  uVar5 = param_2[0x967];
  uVar2 = param_2[0x966];
  *(ushort *)(iVar12 + 0xcc) =
       (ushort)((ushort)param_2[0x973] - 0x3000) &
       ~(ushort)((int)((ushort)param_2[0x973] - 0x3000) >> 0x1f);
  uVar3 = param_2[0x969];
  *(undefined2 *)(iVar12 + 0xd0) = uVar5;
  uVar5 = param_2[0x96c];
  *(undefined2 *)(iVar12 + 0xce) = uVar3;
  *(undefined2 *)(iVar12 + 0xd2) = uVar3;
  uVar3 = param_2[0x96a];
  *(undefined2 *)(iVar12 + 0xf8) = uVar2;
  *(undefined2 *)(iVar12 + 0xd6) = uVar5;
  uVar2 = param_2[0x96d];
  uVar6 = param_2[0x972];
  *(undefined2 *)(iVar12 + 0xd4) = uVar3;
  uVar3 = param_2[0x971];
  uVar5 = param_2[0x96b];
  *(undefined2 *)(iVar12 + 0xd8) = uVar2;
  *(undefined2 *)(iVar12 + 0xda) = uVar3;
  *(undefined2 *)(iVar12 + 0xe0) = uVar5;
  iVar16 = DAT_437aa64c;
  *(undefined2 *)(iVar12 + 0xdc) = uVar6;
  *(undefined2 *)(iVar12 + 0xde) = 0x1000;
  if (*(char *)(*(int *)(iVar18 + iVar16) + 0x6f) == '\x01') {
    uVar3 = param_2[0xa0e];
    uVar2 = param_2[0xa0f];
    *(undefined2 *)(iVar12 + 0xee) = param_2[0xa0d];
    *(undefined2 *)(iVar12 + 0xf0) = uVar3;
    *(undefined2 *)(iVar12 + 0xf2) = uVar2;
    *(undefined2 *)(iVar12 + 0xf4) = param_2[0xa10];
  }
  *(undefined1 *)(iVar12 + 0xe2) = 0;
  iVar16 = *param_1;
  *(undefined4 *)(iVar16 + 0xe4) = 0;
  *(undefined4 *)(iVar16 + 0xe8) = 0;
  *(undefined2 *)(iVar16 + 0xec) = 0;
  *(undefined1 *)(iVar16 + 0xfc) = *(undefined1 *)(param_3 + 0x4af);
  iVar16 = *param_1;
  uVar2 = param_2[0x19b5];
  uVar7 = param_2[0x19b4];
  *(undefined2 *)(iVar16 + 0xfe) = 0;
  *(undefined1 *)(iVar16 + 0x104) = 0;
  *(short *)(iVar16 + 0x102) = (short)((int)(uint)uVar7 >> 4);
  *(undefined2 *)(iVar16 + 0x100) = uVar2;
  *(char *)(iVar16 + 0x106) = (char)*(undefined4 *)(param_2 + 0x2428);
  iVar16 = *param_1;
  *(undefined2 *)(iVar16 + 0x108) = 0;
  *(char *)(iVar16 + 0x10a) = (char)*(undefined4 *)(param_2 + 0x2426);
  *(char *)(*param_1 + 0x10b) = (char)*(undefined4 *)(param_2 + 0x242e);
  *(undefined2 *)(*param_1 + 0x10c) = param_2[0x1975];
  FUN_43723654(auStack_2a,&uStack_2c);
  uVar7 = *(ushort *)(*(int *)(iVar18 + DAT_437aa650) + 0x304);
  if ((((auStack_2a[0] <= uVar7) ||
       (uVar8 = *(ushort *)(*(int *)(iVar18 + DAT_437aa650) + 0x302), uVar8 <= auStack_2a[0])) ||
      (uStack_2c <= uVar7)) || (uVar8 <= uStack_2c)) {
    auStack_2a[0] = 0x100;
    uStack_2c = 0x100;
  }
  if (*(char *)(*param_1 + 0xa8) == '\x01') {
    iVar16 = FUN_437a1514();
    auStack_2a[0] = *(ushort *)(iVar16 + 4);
    uStack_2c = *(ushort *)(iVar16 + 6);
  }
  *(ushort *)(*param_1 + 0x110) = auStack_2a[0];
  *(ushort *)(*param_1 + 0x112) = uStack_2c;
  sVar10 = *(short *)(*(int *)(iVar18 + DAT_437aa654) + 0xc);
  bVar4 = *(byte *)(*(int *)(iVar18 + DAT_437aa654) + 0xb);
  iVar18 = FUN_436ef7d8();
  if (iVar18 == 0) {
    *(undefined1 *)(*param_1 + 0x114) = 0;
    *(undefined1 *)(*param_1 + 0x115) = 0;
  }
  else {
    sVar9 = *(short *)(iVar18 + ((bVar4 & 0xf) + 0x20) * 2);
    if (sVar9 == 0) {
      *(undefined1 *)(*param_1 + 0x114) = 0;
      *(undefined1 *)(*param_1 + 0x115) = 0;
    }
    else {
      iVar16 = (int)sVar9;
      if (iVar16 < 1) {
        iVar16 = 1;
      }
      sVar10 = FUN_4355fd68((int)sVar10,iVar16);
      if (sVar10 < -0x7f) {
        uVar13 = 0x80;
      }
      else if (sVar10 < 0x7f) {
        uVar13 = (undefined1)sVar10;
      }
      else {
        uVar13 = 0x7f;
      }
      *(undefined1 *)(*param_1 + 0x114) = uVar13;
      *(undefined1 *)(*param_1 + 0x115) = *(undefined1 *)(iVar18 + 0x393);
    }
  }
  *(undefined1 *)(*param_1 + 0x118) = *(undefined1 *)(param_3 + 0x4ae);
  *(undefined1 *)(*param_1 + 0x11c) = *(undefined1 *)(DAT_437aa658 + 0x437aa418);
  *(char *)(*param_1 + 0x124) = (char)*(undefined4 *)(param_2 + 0x2418);
  iVar18 = *param_1;
  *(undefined4 *)(iVar18 + 0x128) = *(undefined4 *)(param_2 + 0x241a);
  *(undefined1 *)(iVar18 + 300) = *(undefined1 *)(param_2 + 0x241c);
  iVar18 = *param_1;
  *(undefined4 *)(iVar18 + 0x130) = *(undefined4 *)(param_2 + 0x2410);
  *(undefined4 *)(iVar18 + 0x134) = *(undefined4 *)(param_2 + 0x2412);
  *(undefined1 *)(iVar18 + 0x138) = *(undefined1 *)(param_2 + 0x2420);
  *(undefined1 *)(*param_1 + 0x139) = *(undefined1 *)((int)param_2 + 0x4841);
  *(undefined2 *)(*param_1 + 0x13c) = 0;
  *(undefined2 *)(*param_1 + 0x13e) = 0;
  *(undefined2 *)(*param_1 + 0x144) = 0;
  *(undefined2 *)(*param_1 + 0x146) = 0;
  *(undefined2 *)(*param_1 + 0x148) = 0;
  *(undefined2 *)(*param_1 + 0x14a) = 0;
  *(undefined2 *)(*param_1 + 0x14c) = 0;
  *(undefined2 *)(*param_1 + 0x14e) = 0;
  *(undefined2 *)(*param_1 + 0x150) = 0;
  *(undefined2 *)(*param_1 + 0x152) = 0;
  iVar18 = *param_1;
  uVar2 = param_2[0xa21];
  *(undefined2 *)(iVar18 + 0x154) = param_2[0xa20];
  uVar3 = param_2[0xa22];
  *(undefined2 *)(iVar18 + 0x156) = uVar2;
  uVar2 = param_2[0xa23];
  *(undefined2 *)(iVar18 + 0x158) = uVar3;
  uVar3 = param_2[0xa24];
  uVar5 = param_2[0xa25];
  *(undefined2 *)(iVar18 + 0x15a) = uVar2;
  *(undefined2 *)(iVar18 + 0x15c) = uVar3;
  *(undefined2 *)(iVar18 + 0x15e) = uVar5;
  uVar2 = param_2[0x96a];
  *(undefined2 *)(iVar18 + 0x160) = param_2[0x967];
  uVar3 = param_2[0x96c];
  uVar5 = param_2[0x96d];
  *(undefined2 *)(iVar18 + 0x162) = uVar2;
  *(undefined2 *)(iVar18 + 0x164) = uVar3;
  *(undefined2 *)(iVar18 + 0x166) = uVar5;
  uVar2 = param_2[0xb28];
  *(undefined2 *)(iVar18 + 0x168) = param_2[0xb27];
  *(undefined2 *)(iVar18 + 0x16a) = uVar2;
  uVar2 = param_2[0xb2a];
  *(undefined2 *)(iVar18 + 0x16c) = param_2[0xb29];
  uVar3 = param_2[0xb2e];
  *(undefined2 *)(iVar18 + 0x16e) = uVar2;
  uVar2 = param_2[0xb2f];
  *(undefined2 *)(iVar18 + 0x170) = uVar3;
  uVar3 = param_2[0xb30];
  *(undefined2 *)(iVar18 + 0x172) = uVar2;
  uVar2 = param_2[0xb2d];
  *(undefined2 *)(iVar18 + 0x174) = uVar3;
  uVar3 = param_2[0xb31];
  *(undefined2 *)(iVar18 + 0x178) = uVar2;
  *(undefined2 *)(iVar18 + 0x176) = uVar3;
  *(undefined2 *)(iVar18 + 0x17a) = param_2[0xb40];
  *(undefined2 *)(iVar18 + 0x17c) = param_2[0xb32];
  *(undefined2 *)(iVar18 + 0x17e) = param_2[0xb33];
  uVar2 = param_2[0xb43];
  *(undefined2 *)(iVar18 + 0x180) = param_2[0xb41];
  *(undefined2 *)(iVar18 + 0x182) = uVar2;
  *(short *)(iVar18 + 0x184) = (short)((uint)*(undefined4 *)(param_2 + 0xb3a) >> 8);
  *(short *)(iVar18 + 0x186) = (short)((uint)*(undefined4 *)(param_2 + 0xb34) >> 8);
  *(short *)(iVar18 + 0x188) = (short)((uint)*(undefined4 *)(param_2 + 0xb36) >> 8);
  *(short *)(iVar18 + 0x18a) = (short)((uint)*(undefined4 *)(param_2 + 0xb3c) >> 8);
  *(undefined1 *)(iVar18 + 0x18c) = *(undefined1 *)((int)param_2 + 0x1671);
  *(undefined1 *)(*param_1 + 0x18d) = *(undefined1 *)(param_2 + 0xb38);
  *(undefined1 *)(*param_1 + 0x18e) = *(undefined1 *)(param_2 + 0xb39);
  *(undefined1 *)(*param_1 + 399) = *(undefined1 *)((int)param_2 + 0x1417);
  *(undefined1 *)(*param_1 + 400) = *(undefined1 *)(param_2 + 0xa0b);
  iVar18 = *param_1;
  *(undefined2 **)(iVar18 + 0x194) = param_2 + 0x2290;
  *(int *)(iVar18 + 0x19c) = param_3 + 0x164;
  *(undefined2 **)(iVar18 + 0x1a0) = param_2 + 0x1c2e;
  *(int *)(iVar18 + 0x198) = param_3;
  *(undefined1 *)(iVar18 + 0x1a8) = 0;
  *(undefined2 **)(iVar18 + 0x1a4) = param_2 + 0x20fa;
  iVar18 = *param_1;
  if (param_4 == 0) {
    *(undefined4 *)(iVar18 + 0x1ac) = 0;
    *(undefined1 *)(iVar18 + 0x1b0) = 0;
    *(undefined1 *)(*param_1 + 0x1b1) = 0;
  }
  else {
    *(int *)(iVar18 + 0x1ac) = param_4;
    *(undefined1 *)(iVar18 + 0x1b0) = *(undefined1 *)(param_4 + 0x134);
    *(undefined1 *)(*param_1 + 0x1b1) = *(undefined1 *)(param_4 + 0x135);
  }
  iVar18 = *param_1;
  *(int *)(iVar18 + 0x1b4) = param_3 + 0x170;
  if (*(char *)(param_2 + 0x2421) != '\0') {
    *(char *)(iVar18 + 0x1a) = *(char *)(param_2 + 0x2421);
  }
  if (*(char *)((int)param_2 + 0x4845) != '\0') {
    *(char *)(*param_1 + 0x1b) = *(char *)((int)param_2 + 0x4845);
  }
  if (*(char *)((int)param_2 + 0x4843) != '\0') {
    *(char *)(*param_1 + 0x1e) = *(char *)((int)param_2 + 0x4843);
  }
  if (*(char *)(param_2 + 0x2422) != '\0') {
    *(char *)(*param_1 + 0x1f) = *(char *)(param_2 + 0x2422);
  }
LAB_437aa622:
  if (*(char *)(*param_1 + 3) != '\0') {
    FUN_437a9a7c(param_1);
  }
  return;
}


/* 437aa65c */

void FUN_437aa65c(int *param_1,int *param_2,int param_3)

{
  byte bVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  ushort uVar6;
  ushort uVar7;
  short sVar8;
  undefined1 uVar9;
  short sVar10;
  undefined2 *puVar11;
  int iVar12;
  undefined1 *puVar13;
  undefined4 *puVar14;
  undefined1 uVar15;
  int iVar16;
  undefined4 uVar17;
  int *piVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  char cVar23;
  int iVar24;
  int iVar25;
  char cVar26;
  bool bVar27;
  ushort uStack_2c;
  ushort auStack_2a [3];
  
  piVar18 = (int *)param_1[1];
  iVar20 = DAT_437aafd4 + 0x437aa670;
  if (piVar18 != (int *)0x0) {
    piVar18[4] = param_3;
    *piVar18 = param_3 + 500;
    piVar18[5] = param_3 + 0xf10;
    piVar18[6] = param_3 + 0x2cc;
    piVar18[9] = 0;
    piVar18[7] = 0;
    piVar18[8] = 0;
    piVar18[1] = param_3 + 0x5e8;
    piVar18[2] = param_3 + 0x9d0;
  }
  iVar16 = DAT_437aafd8;
  if (*param_1 == 0) goto LAB_437aafc0;
  *(bool *)*param_1 = *(int *)(param_2[1] + 0x14) == 1;
  *(char *)(DAT_437aafdc + 0x437aa6bc) = (char)*(undefined4 *)(param_2[1] + 0x14);
  *(undefined1 *)(*param_1 + 1) = 0;
  *(undefined1 *)(*param_1 + 2) = 0;
  *(undefined1 *)(*param_1 + 3) = *(undefined1 *)(*(int *)(iVar20 + iVar16) + 0x6c);
  iVar21 = *param_1;
  *(undefined4 *)(iVar21 + 8) = 0;
  *(undefined4 *)(iVar21 + 0xc) = 0;
  *(undefined4 *)(iVar21 + 0x10) = 0;
  iVar19 = *param_2;
  *(int **)(iVar21 + 4) = param_2;
  uVar2 = *(undefined2 *)(iVar19 + 6);
  *(char *)(iVar21 + 0x16) = (char)*(undefined4 *)(iVar19 + 0x1c);
  iVar16 = *(int *)(iVar19 + 0xe0);
  *(undefined2 *)(iVar21 + 0x14) = uVar2;
  if (iVar16 - 5U < 3) {
    bVar27 = *(int *)(iVar19 + 0x52c) == 2;
  }
  else {
    bVar27 = *(int *)(iVar19 + 0x3c8) == 0x12;
  }
  *(bool *)(iVar21 + 0x83) = bVar27;
  *(undefined4 *)(iVar21 + 0x84) = *(undefined4 *)(iVar19 + 0x52c);
  uVar9 = *(undefined1 *)(iVar19 + 0xe0);
  switch(uVar9) {
  case 0x26:
    uVar9 = 0x1f;
    break;
  case 0x27:
  case 0x28:
    uVar9 = 0x20;
    break;
  case 0x29:
    uVar9 = 0x23;
  }
  *(undefined1 *)(iVar21 + 0x17) = uVar9;
  *(char *)(iVar21 + 0x18) = (char)*(undefined4 *)(iVar19 + 0xe4);
  if ((*(int *)(iVar19 + 0xe0) == 0x1f) || (*(int *)(iVar19 + 0xe0) == 0x26)) {
    bVar27 = true;
  }
  else {
    bVar27 = (byte)(*(char *)(param_2[7] + 3) - 1U) < 3;
  }
  *(undefined1 *)(param_1[5] + 0x25c) = *(undefined1 *)(param_2[7] + 3);
  *(bool *)(iVar21 + 0x19) = bVar27;
  if (*(char *)(iVar19 + 0x1a4) == '\x01') {
    uVar9 = 0;
  }
  else {
    uVar9 = (undefined1)*(uint *)(iVar19 + 0x3c8);
    if ((*(uint *)(iVar19 + 0x3c8) & 0xff) == 0x12) {
      uVar9 = 0;
    }
  }
  *(undefined1 *)(iVar21 + 0x1a) = uVar9;
  *(char *)(iVar21 + 0x6d) = (char)*(undefined4 *)(iVar19 + 0x3c8);
  *(bool *)(iVar21 + 0x6e) = *(int *)(iVar19 + 0x3ec) == 1;
  *(undefined1 *)(iVar21 + 0x1b) = *(undefined1 *)(iVar19 + 0x3d0);
  *(undefined1 *)(iVar21 + 0x1c) = *(undefined1 *)(iVar19 + 0x3d1);
  *(char *)(iVar21 + 0x1d) = (char)*(undefined4 *)(iVar19 + 0x4f8);
  uVar9 = *(undefined1 *)(iVar19 + 0x13f);
  uVar15 = *(undefined1 *)(iVar19 + 0x140);
  if (bVar27) {
    uVar15 = 0;
    uVar9 = 0;
    cVar26 = '\0';
    cVar23 = '\0';
  }
  else if (*(int *)(iVar19 + 0x144) == 0) {
    cVar23 = *(char *)(iVar19 + 0x13d) + *(char *)(iVar19 + 0x3ce) + *(char *)(iVar19 + 0x3cc);
    cVar26 = *(char *)(iVar19 + 0x13e) + *(char *)(iVar19 + 0x3cf) + *(char *)(iVar19 + 0x3cd);
    uVar9 = 0;
    uVar15 = 0;
  }
  else {
    cVar26 = '\0';
    cVar23 = '\0';
  }
  *(char *)(iVar21 + 0x1e) = cVar23;
  *(char *)(iVar21 + 0x1f) = cVar26;
  *(undefined1 *)(iVar21 + 0x20) = uVar9;
  *(undefined1 *)(iVar21 + 0x21) = uVar15;
  iVar16 = *(int *)(iVar19 + 1000);
  iVar12 = *(int *)(iVar19 + 0x138);
  if (*(int *)(iVar19 + 0x3d4) == 0) {
    if (iVar12 == 0) {
      if (iVar16 == 0) {
        uVar9 = 0;
      }
      else {
        if (iVar16 - 1U < 2) {
          iVar12 = DAT_437aafe4 + 0x437aa834 + iVar16;
          goto LAB_437aa834;
        }
        uVar9 = 0;
      }
    }
    else {
      uVar9 = 0;
      if (iVar12 - 1U < 7) {
        iVar12 = DAT_437aafe0 + 0x437aa822 + iVar12;
LAB_437aa834:
        uVar9 = *(undefined1 *)(iVar12 + -1);
      }
    }
  }
  else {
    uVar9 = (undefined1)*(int *)(iVar19 + 0x3d4);
  }
  *(undefined1 *)(iVar21 + 0x22) = uVar9;
  if (*(int *)(iVar19 + 0x138) == 0) {
    uVar9 = 8;
  }
  else {
    uVar9 = *(undefined1 *)(iVar19 + 0x13c);
  }
  *(undefined1 *)(iVar21 + 0x23) = uVar9;
  *(char *)(iVar21 + 0x24) = *(char *)(iVar19 + 0x14e) + *(char *)(iVar19 + 0x3d9);
  *(undefined1 *)(iVar21 + 0x25) = *(undefined1 *)(iVar19 + 0x14f);
  *(undefined1 *)(iVar21 + 0x26) = *(undefined1 *)(iVar19 + 0x3d8);
  *(char *)(iVar21 + 0x27) = (char)*(undefined4 *)(iVar19 + 0x3e4);
  *(char *)(iVar21 + 0x28) = (char)*(undefined4 *)(iVar19 + 0x3e0);
  cVar23 = *(char *)(iVar19 + 0x3f0) + *(char *)(iVar19 + 0x148);
  *(char *)(iVar21 + 0x2a) = cVar23;
  *(char *)(iVar21 + 0x2c) = *(char *)(iVar19 + 0x3f1) + *(char *)(iVar19 + 0x149);
  *(char *)(iVar21 + 0x2e) = *(char *)(iVar19 + 0x3f2) + *(char *)(iVar19 + 0x14a);
  *(char *)(iVar21 + 0x2d) = *(char *)(iVar19 + 0x3f3) + *(char *)(iVar19 + 0x14b);
  *(char *)(iVar21 + 0x2f) = *(char *)(iVar19 + 0x3f4) + *(char *)(iVar19 + 0x14c);
  cVar26 = *(char *)(iVar19 + 0x3f5) + *(char *)(iVar19 + 0x14d);
  *(char *)(iVar21 + 0x2b) = cVar26;
  if ((cVar23 == '\0') && (*(int *)(iVar21 + 0x2c) == 0)) {
    bVar27 = cVar26 != '\0';
  }
  else {
    bVar27 = true;
  }
  *(bool *)(iVar21 + 0x29) = bVar27;
  *(undefined1 *)(iVar21 + 0x30) = *(undefined1 *)(iVar19 + 0x153);
  *(char *)(iVar21 + 0x31) = (char)*(undefined4 *)(iVar19 + 0x138);
  *(undefined1 *)(iVar21 + 0x32) = *(undefined1 *)(iVar19 + 0x40a);
  *(undefined1 *)(iVar21 + 0x33) = *(undefined1 *)(iVar19 + 0x40b);
  *(undefined1 *)(iVar21 + 0x34) = *(undefined1 *)(iVar19 + 0x40c);
  *(char *)(iVar21 + 0x35) = (char)*(undefined4 *)(iVar19 + 0x410) + -10;
  *(char *)(iVar21 + 0x37) = (char)*(undefined4 *)(iVar19 + 0x418);
  *(undefined1 *)(iVar21 + 0x36) = *(undefined1 *)(iVar19 + 0x41c);
  *(undefined1 *)(iVar21 + 0x38) = *(undefined1 *)(iVar19 + 0x41d);
  *(bool *)(iVar21 + 0x39) = *(short *)(iVar19 + 6) == 0x40d;
  *(char *)(iVar21 + 0x3a) = (char)*(undefined4 *)(iVar19 + 0xb4);
  *(char *)(iVar21 + 0x3b) = (char)*(undefined4 *)(iVar19 + 0xa4);
  *(undefined4 *)(iVar21 + 0x3c) = *(undefined4 *)(iVar19 + 0xa8);
  *(undefined1 *)(iVar21 + 0x40) = *(undefined1 *)(iVar19 + 0xac);
  *(undefined4 *)(iVar21 + 0x44) = *(undefined4 *)(iVar19 + 0x114);
  *(undefined1 *)(iVar21 + 0x48) = *(undefined1 *)(iVar19 + 0x4eb);
  *(char *)(iVar21 + 0x49) = (char)*(undefined4 *)(iVar19 + 0x50);
  *(undefined1 *)(iVar21 + 0x4a) = *(undefined1 *)(iVar19 + 0x19b);
  uVar17 = *(undefined4 *)(iVar19 + 0x354);
  *(undefined1 *)(iVar21 + 0x4c) = 0;
  *(undefined1 *)(iVar21 + 0x4d) = 0;
  *(undefined1 *)(iVar21 + 0x4e) = 0;
  *(undefined1 *)(iVar21 + 0x4f) = 0;
  *(char *)(iVar21 + 0x4b) = (char)uVar17;
  *(char *)(iVar21 + 0x50) = (char)*(undefined4 *)(iVar19 + 0xb8);
  *(char *)(iVar21 + 0x52) = (char)*(undefined4 *)(iVar19 + 0x424);
  *(char *)(iVar21 + 0x53) = (char)*(undefined4 *)(iVar19 + 0x428);
  *(undefined2 *)(iVar21 + 0x54) = *(undefined2 *)(iVar19 + 0x42c);
  *(undefined1 *)(iVar21 + 0x58) = *(undefined1 *)(iVar19 + 0x42e);
  *(undefined1 *)(iVar21 + 0x5a) = *(undefined1 *)(iVar19 + 0x42f);
  *(undefined1 *)(iVar21 + 0x5c) = *(undefined1 *)(iVar19 + 0x430);
  *(undefined1 *)(iVar21 + 0x5e) = *(undefined1 *)(iVar19 + 0x431);
  *(undefined2 *)(iVar21 + 0x56) = *(undefined2 *)(iVar19 + 0x432);
  *(undefined1 *)(iVar21 + 0x59) = *(undefined1 *)(iVar19 + 0x434);
  *(undefined1 *)(iVar21 + 0x5b) = *(undefined1 *)(iVar19 + 0x435);
  *(undefined1 *)(iVar21 + 0x5d) = *(undefined1 *)(iVar19 + 0x436);
  *(undefined1 *)(iVar21 + 0x5f) = *(undefined1 *)(iVar19 + 0x437);
  uVar2 = *(undefined2 *)(iVar19 + 0x3f8);
  uVar3 = *(undefined2 *)(iVar19 + 0x3fa);
  uVar4 = *(undefined2 *)(iVar19 + 0x3fc);
  *(undefined2 *)(iVar21 + 0x70) = *(undefined2 *)(iVar19 + 0x3f6);
  uVar5 = *(undefined2 *)(iVar19 + 0x3fe);
  *(undefined2 *)(iVar21 + 0x72) = uVar2;
  *(undefined2 *)(iVar21 + 0x74) = uVar3;
  uVar2 = *(undefined2 *)(iVar19 + 0x400);
  uVar3 = *(undefined2 *)(iVar19 + 0x402);
  *(undefined2 *)(iVar21 + 0x76) = uVar4;
  *(undefined2 *)(iVar21 + 0x78) = uVar5;
  uVar4 = *(undefined2 *)(iVar19 + 0x404);
  uVar5 = *(undefined2 *)(iVar19 + 0x406);
  *(undefined2 *)(iVar21 + 0x7a) = uVar2;
  *(undefined2 *)(iVar21 + 0x7c) = uVar3;
  *(undefined2 *)(iVar21 + 0x80) = uVar5;
  *(undefined2 *)(iVar21 + 0x7e) = uVar4;
  *(undefined1 *)(iVar21 + 0x82) = *(undefined1 *)(iVar19 + 0x408);
  uVar2 = *(undefined2 *)(iVar19 + 0x438);
  uVar3 = *(undefined2 *)(iVar19 + 0x43a);
  *(undefined1 *)(iVar21 + 0x6c) = *(undefined1 *)(iVar19 + 0x43c);
  uVar17 = *(undefined4 *)(iVar19 + 0x18);
  *(undefined2 *)(iVar21 + 0x6a) = uVar3;
  *(undefined2 *)(iVar21 + 0x68) = uVar2;
  *(undefined4 *)(iVar21 + 0x60) = uVar17;
  *(undefined4 *)(iVar21 + 100) = *(undefined4 *)(iVar19 + 0x55c);
  *(char *)(iVar21 + 0x88) = (char)*(undefined4 *)(iVar19 + 0x510);
  iVar16 = param_2[2];
  iVar22 = *param_1;
  uVar17 = *(undefined4 *)(iVar16 + 0xd8);
  *(undefined1 *)(iVar22 + 0x8c) = 0;
  *(char *)(iVar22 + 0x8d) = (char)uVar17;
  uVar9 = *(undefined1 *)(iVar16 + 0x8c);
  puVar13 = (undefined1 *)(DAT_437aafe8 + 0x437aaaa4);
  *(undefined1 *)(iVar22 + 0x8e) = uVar9;
  *puVar13 = uVar9;
  uVar17 = *(undefined4 *)(iVar16 + 0x2c);
  *(undefined1 *)(iVar22 + 0x96) = 0;
  *(undefined1 *)(iVar22 + 0x94) = 0;
  *(undefined4 *)(iVar22 + 0x90) = uVar17;
  *(undefined1 *)(iVar22 + 0x95) = 9;
  *(undefined1 *)(iVar22 + 0x97) = *(undefined1 *)(iVar16 + 0x30);
  *(char *)(iVar22 + 0x98) = (char)*(undefined4 *)(iVar16 + 0x44);
  *(char *)(iVar22 + 0x99) = (char)*(undefined4 *)(iVar16 + 0x1c0);
  uVar9 = FUN_43780068();
  *(undefined1 *)(iVar22 + 0x9a) = uVar9;
  uVar9 = *(undefined1 *)(iVar16 + 0x1ff);
  *(undefined1 *)(iVar22 + 0x9b) = 0;
  *(undefined1 *)(iVar22 + 0xa8) = 0;
  *(undefined1 *)(iVar22 + 0x9c) = uVar9;
  *(undefined1 *)(iVar22 + 0xa9) = 0;
  uVar2 = *(undefined2 *)(iVar16 + 0x28c);
  uVar3 = *(undefined2 *)(iVar16 + 0x28e);
  *(undefined1 *)(iVar22 + 0xaa) = *(undefined1 *)(iVar16 + 0xcf);
  uVar4 = *(undefined2 *)(iVar16 + 0x288);
  *(undefined2 *)(iVar22 + 0xac) = uVar2;
  *(undefined2 *)(iVar22 + 0xae) = uVar3;
  uVar2 = *(undefined2 *)(iVar16 + 0x28a);
  uVar3 = *(undefined2 *)(iVar16 + 0x2b4);
  *(undefined2 *)(iVar22 + 0xb0) = uVar4;
  uVar4 = *(undefined2 *)(iVar16 + 0x2b8);
  *(undefined1 *)(iVar22 + 0xb4) = 0;
  iVar25 = param_2[0xd];
  *(undefined4 *)(iVar22 + 0xa0) = 0;
  *(undefined4 *)(iVar22 + 0xa4) = 0;
  *(undefined2 *)(iVar22 + 0xb8) = uVar4;
  *(undefined1 *)(iVar22 + 0xb5) = 0;
  uVar6 = *(ushort *)(iVar25 + 0x16);
  iVar24 = *param_1;
  *(int *)(iVar22 + 0xc0) = iVar16 + 0x870;
  iVar16 = uVar6 - 0x3000;
  iVar12 = param_2[3];
  *(ushort *)(iVar24 + 0xcc) = (ushort)iVar16 & ~(ushort)(iVar16 >> 0x1f);
  *(undefined2 *)(iVar22 + 0xb2) = uVar2;
  uVar2 = *(undefined2 *)(iVar12 + 0x18);
  *(undefined2 *)(iVar22 + 0xb6) = uVar3;
  *(undefined2 *)(iVar24 + 0xce) = uVar2;
  *(undefined2 *)(iVar24 + 0xd0) = uVar2;
  uVar3 = *(undefined2 *)(iVar12 + 0x3a);
  uVar4 = *(undefined2 *)(iVar12 + 0x4c);
  *(undefined2 *)(iVar24 + 0xd4) = *(undefined2 *)(iVar12 + 0x1c);
  uVar2 = *(undefined2 *)(iVar12 + 0x32);
  *(undefined2 *)(iVar24 + 0xd2) = uVar3;
  *(undefined2 *)(iVar24 + 0xf8) = uVar4;
  uVar4 = *(undefined2 *)(iVar12 + 0x1e);
  uVar3 = *(undefined2 *)(iVar12 + 0x20);
  *(undefined2 *)(iVar24 + 0xda) = uVar2;
  uVar2 = *(undefined2 *)(iVar12 + 0x48);
  *(undefined2 *)(iVar24 + 0xd6) = uVar4;
  uVar4 = *(undefined2 *)(iVar12 + 0x26);
  *(undefined2 *)(iVar24 + 0xe0) = uVar2;
  iVar16 = param_2[9];
  *(undefined2 *)(iVar24 + 0xd8) = uVar3;
  *(undefined2 *)(iVar24 + 0xdc) = uVar4;
  *(undefined2 *)(iVar24 + 0xde) = 0x1000;
  *(undefined1 *)(iVar24 + 0xe2) = *(undefined1 *)(iVar16 + 0x28);
  uVar2 = *(undefined2 *)(iVar12 + 0x106);
  *(undefined4 *)(iVar24 + 0xe4) = *(undefined4 *)(iVar12 + 4);
  *(undefined2 *)(iVar24 + 0xec) = uVar2;
  uVar2 = *(undefined2 *)(iVar25 + 0x7a8);
  *(int *)(iVar24 + 0xe8) = iVar25 + 0x694;
  *(undefined2 *)(iVar24 + 0xf6) = uVar2;
  if (*(char *)(*(int *)(iVar20 + DAT_437aafec) + 0x6f) == '\x01') {
    uVar2 = *(undefined2 *)(iVar25 + 0x7a2);
    uVar3 = *(undefined2 *)(iVar25 + 0x7a4);
    uVar4 = *(undefined2 *)(iVar25 + 0x7a6);
    *(undefined2 *)(iVar24 + 0xee) = *(undefined2 *)(iVar25 + 0x7a0);
    *(undefined2 *)(iVar24 + 0xf0) = uVar2;
    *(undefined2 *)(iVar24 + 0xf2) = uVar3;
    *(undefined2 *)(iVar24 + 0xf4) = uVar4;
  }
  *(undefined1 *)(*param_1 + 0xfc) = *(undefined1 *)(param_2[0x12] + 5);
  iVar16 = param_2[10];
  iVar12 = *param_1;
  uVar2 = *(undefined2 *)(iVar16 + 0x26);
  uVar3 = *(undefined2 *)(iVar16 + 0x22);
  *(undefined2 *)(iVar12 + 0xfe) = *(undefined2 *)(iVar16 + 4);
  *(undefined2 *)(iVar12 + 0x100) = uVar2;
  *(undefined2 *)(iVar12 + 0x102) = uVar3;
  *(undefined1 *)(iVar12 + 0x104) = *(undefined1 *)(param_2[0xe] + 0x74);
  puVar14 = (undefined4 *)param_2[6];
  *(char *)(iVar12 + 0x106) = (char)puVar14[1];
  uVar2 = *(undefined2 *)(puVar14 + 8);
  *(char *)(iVar12 + 0x10a) = (char)*puVar14;
  uVar17 = puVar14[9];
  *(undefined2 *)(iVar12 + 0x108) = uVar2;
  *(char *)(iVar12 + 0x10b) = (char)uVar17;
  *(undefined2 *)(*param_1 + 0x10c) = *(undefined2 *)(param_2[0xc] + 10);
  FUN_43723654(auStack_2a,&uStack_2c);
  uVar6 = *(ushort *)(*(int *)(iVar20 + DAT_437aaff0) + 0x304);
  if ((((auStack_2a[0] <= uVar6) ||
       (uVar7 = *(ushort *)(*(int *)(iVar20 + DAT_437aaff0) + 0x302), uVar7 <= auStack_2a[0])) ||
      (uStack_2c <= uVar6)) || (uVar7 <= uStack_2c)) {
    auStack_2a[0] = 0x100;
    uStack_2c = 0x100;
  }
  *(ushort *)(*param_1 + 0x110) = auStack_2a[0];
  *(ushort *)(*param_1 + 0x112) = uStack_2c;
  sVar10 = *(short *)(*(int *)(iVar20 + DAT_437aaff4) + 0xc);
  bVar1 = *(byte *)(*(int *)(iVar20 + DAT_437aaff4) + 0xb);
  iVar20 = FUN_436ef7d8();
  if (iVar20 == 0) {
    *(undefined1 *)(*param_1 + 0x114) = 0;
    *(undefined1 *)(*param_1 + 0x115) = 0;
  }
  else {
    sVar8 = *(short *)(iVar20 + ((bVar1 & 0xf) + 0x20) * 2);
    if (sVar8 == 0) {
      *(undefined1 *)(*param_1 + 0x114) = 0;
      iVar16 = *param_1;
      uVar9 = 0;
    }
    else {
      iVar16 = (int)sVar8;
      if (iVar16 < 1) {
        iVar16 = 1;
      }
      sVar10 = FUN_4355fd68((int)sVar10,iVar16);
      if (sVar10 < -0x7f) {
        uVar9 = 0x80;
      }
      else if (sVar10 < 0x7f) {
        uVar9 = (undefined1)sVar10;
      }
      else {
        uVar9 = 0x7f;
      }
      *(undefined1 *)(*param_1 + 0x114) = uVar9;
      iVar16 = *param_1;
      uVar9 = *(undefined1 *)(iVar20 + 0x393);
    }
    *(undefined1 *)(iVar16 + 0x115) = uVar9;
  }
  *(undefined1 *)(*param_1 + 0x118) = *(undefined1 *)(param_2[7] + 5);
  *(char *)(*param_1 + 0x11c) = (char)*(undefined4 *)(param_2[1] + 0x14);
  iVar20 = *param_1;
  *(undefined4 *)(iVar20 + 0x120) = *(undefined4 *)param_2[1];
  iVar16 = param_2[0x14];
  *(char *)(iVar20 + 0x124) = (char)*(undefined4 *)(iVar16 + 0xac);
  *(undefined4 *)(iVar20 + 0x128) = *(undefined4 *)(iVar16 + 0xb0);
  *(undefined1 *)(iVar20 + 300) = *(undefined1 *)(iVar16 + 0xb4);
  *(undefined4 *)(iVar20 + 0x130) = *(undefined4 *)(iVar16 + 8);
  *(undefined4 *)(iVar20 + 0x134) = *(undefined4 *)(iVar16 + 0x10);
  *(undefined1 *)(iVar20 + 0x138) = *(undefined1 *)(iVar16 + 0xbc);
  *(undefined1 *)(iVar20 + 0x139) = *(undefined1 *)(iVar16 + 0xbd);
  iVar20 = *param_1;
  if (*(int *)(iVar19 + 0xb4) == 0) {
    *(undefined2 *)(iVar20 + 0x13c) = 0;
    *(undefined2 *)(iVar20 + 0x13e) = 0;
    *(undefined2 *)(iVar20 + 0x140) = 0;
    *(undefined2 *)(iVar20 + 0x142) = 0;
    *(undefined2 *)(iVar20 + 0x144) = 0;
    *(undefined2 *)(iVar20 + 0x146) = 0;
    *(undefined2 *)(iVar20 + 0x148) = 0;
    *(undefined2 *)(iVar20 + 0x14a) = 0;
    *(undefined2 *)(iVar20 + 0x14c) = 0;
    *(undefined2 *)(iVar20 + 0x14e) = 0;
    *(undefined2 *)(iVar20 + 0x150) = 0;
    *(undefined2 *)(iVar20 + 0x152) = 0;
  }
  else {
    puVar11 = (undefined2 *)FUN_43ae84c0();
    *(undefined2 *)(iVar20 + 0x13c) = *puVar11;
    *(undefined2 *)(iVar20 + 0x13e) = puVar11[1];
    *(undefined2 *)(iVar20 + 0x140) = puVar11[2];
    *(undefined2 *)(iVar20 + 0x142) = puVar11[3];
    *(undefined2 *)(iVar20 + 0x144) = puVar11[4];
    *(undefined2 *)(iVar20 + 0x146) = puVar11[5];
    *(undefined2 *)(iVar20 + 0x148) = puVar11[6];
    *(undefined2 *)(iVar20 + 0x14a) = puVar11[7];
    *(undefined2 *)(iVar20 + 0x14c) = puVar11[8];
    *(undefined2 *)(iVar20 + 0x14e) = puVar11[9];
    *(undefined2 *)(iVar20 + 0x150) = puVar11[10];
    *(undefined2 *)(iVar20 + 0x152) = puVar11[0xb];
  }
  iVar20 = *param_1;
  *(undefined2 *)(iVar20 + 0x154) = 0;
  *(undefined2 *)(iVar20 + 0x156) = 0;
  *(undefined2 *)(iVar20 + 0x158) = 0;
  *(undefined2 *)(iVar20 + 0x15a) = 0;
  *(undefined2 *)(iVar20 + 0x15c) = 0;
  *(undefined2 *)(iVar20 + 0x15e) = 0;
  uVar9 = *(undefined1 *)(iVar25 + 0x7cb);
  *(undefined1 *)(iVar20 + 0x18c) = 0;
  *(undefined1 *)(iVar20 + 0x18d) = 0;
  *(undefined1 *)(iVar20 + 400) = uVar9;
  *(undefined1 *)(iVar20 + 0x18e) = 0;
  *(undefined1 *)(iVar20 + 399) = 0;
  *(undefined2 *)(iVar20 + 0x160) = 0;
  iVar12 = *param_1;
  *(undefined2 *)(iVar20 + 0x162) = 0;
  *(undefined2 *)(iVar20 + 0x164) = 0;
  *(undefined2 *)(iVar20 + 0x166) = 0;
  *(undefined2 *)(iVar20 + 0x168) = 0;
  *(undefined2 *)(iVar20 + 0x16a) = 0;
  *(undefined2 *)(iVar20 + 0x16c) = 0;
  *(undefined2 *)(iVar20 + 0x16e) = 0;
  *(undefined2 *)(iVar20 + 0x178) = 0;
  *(undefined2 *)(iVar20 + 0x17a) = 0;
  *(undefined2 *)(iVar20 + 0x17c) = 0;
  *(undefined2 *)(iVar20 + 0x17e) = 0;
  *(undefined2 *)(iVar20 + 0x180) = 0;
  *(undefined2 *)(iVar20 + 0x182) = 0;
  *(undefined2 *)(iVar20 + 0x184) = 0;
  *(undefined2 *)(iVar20 + 0x186) = 0;
  *(undefined2 *)(iVar20 + 0x188) = 0;
  *(undefined2 *)(iVar20 + 0x18a) = 0;
  uVar17 = FUN_439fd844();
  iVar20 = *param_1;
  *(undefined4 *)(iVar12 + 0x198) = 0;
  *(undefined4 *)(iVar12 + 0x19c) = 0;
  *(undefined4 *)(iVar12 + 0x1a0) = 0;
  *(undefined4 *)(iVar12 + 0x1a4) = 0;
  *(undefined4 *)(iVar12 + 0x194) = uVar17;
  uVar9 = *(undefined1 *)param_2[0x25];
  *(undefined1 *)(iVar20 + 0x1b0) = 0;
  *(undefined1 *)(iVar20 + 0x1b1) = 0;
  *(undefined1 *)(iVar20 + 0x1a8) = uVar9;
  *(undefined4 *)(iVar20 + 0x1ac) = 0;
  iVar20 = *(int *)(iVar19 + 0x20c);
  *(undefined4 *)(*param_1 + 0x1b4) = 0;
  if (iVar20 == 1) {
    *(undefined1 *)(iVar21 + 0x1a) = 0;
    *(undefined1 *)(iVar21 + 0x1c) = 0;
    *(undefined1 *)(iVar21 + 0x1e) = 0;
    *(undefined1 *)(iVar21 + 0x1f) = 0;
    *(undefined1 *)(iVar21 + 0x20) = 0;
    *(undefined1 *)(iVar21 + 0x21) = 0;
    *(undefined1 *)(iVar21 + 0x22) = 0;
    *(undefined1 *)(iVar21 + 0x23) = 8;
    *(undefined1 *)(iVar21 + 0x24) = 0;
    *(undefined1 *)(iVar21 + 0x25) = 0;
    *(undefined1 *)(iVar21 + 0x26) = 0;
    *(undefined1 *)(iVar21 + 0x27) = 0;
    *(undefined1 *)(iVar21 + 0x28) = 0;
    *(undefined1 *)(iVar21 + 0x2a) = 0;
    *(undefined1 *)(iVar21 + 0x2b) = 0;
    *(undefined1 *)(iVar21 + 0x2c) = 0;
    *(undefined1 *)(iVar21 + 0x2d) = 0;
    *(undefined1 *)(iVar21 + 0x2e) = 0;
    *(undefined1 *)(iVar21 + 0x2f) = 0;
    *(undefined1 *)(iVar21 + 0x29) = 0;
    *(undefined1 *)(iVar21 + 0x3b) = 0;
  }
  if (*(char *)(iVar16 + 0xbe) != '\0') {
    *(char *)(iVar21 + 0x1a) = *(char *)(iVar16 + 0xbe);
  }
  if (*(char *)(iVar16 + 0xc1) != '\0') {
    *(char *)(iVar21 + 0x1b) = *(char *)(iVar16 + 0xc1);
  }
  if (*(char *)(iVar16 + 0xbf) != '\0') {
    *(char *)(iVar21 + 0x1e) = *(char *)(iVar16 + 0xbf);
  }
  if (*(char *)(iVar16 + 0xc0) != '\0') {
    *(char *)(iVar21 + 0x1f) = *(char *)(iVar16 + 0xc0);
  }
  *(undefined1 *)(param_1[5] + 0x243) = 0;
  *(undefined1 *)(param_1[5] + 0x244) = 0;
  *(undefined1 *)(param_1[5] + 0x245) = 0;
  *(undefined1 *)(param_1[5] + 0x246) = 0;
  *(char *)(param_1[5] + 0x247) = (char)((ushort)*(undefined2 *)(iVar22 + 0xb6) >> 8);
  *(char *)(param_1[5] + 0x248) = (char)*(undefined2 *)(iVar22 + 0xb6);
  *(char *)(param_1[5] + 0x249) = (char)((ushort)*(undefined2 *)(iVar22 + 0xb8) >> 8);
  *(char *)(param_1[5] + 0x24a) = (char)*(undefined2 *)(iVar22 + 0xb8);
  *(char *)(param_1[5] + 0x24f) =
       (char)((uint)*(ushort *)(iVar24 + 0xd0) - (uint)*(ushort *)(iVar24 + 0xf8) >> 8);
  *(char *)(param_1[5] + 0x250) = *(char *)(iVar24 + 0xd0) - *(char *)(iVar24 + 0xf8);
  *(undefined1 *)(param_1[5] + 0x251) = *(undefined1 *)(*param_1 + 0x114);
  *(undefined1 *)(param_1[5] + 0x252) = *(undefined1 *)(*param_1 + 0x115);
LAB_437aafc0:
  if (*(char *)(*param_1 + 3) != '\0') {
    FUN_437a9a7c(param_1);
  }
  return;
}


/* 437abd3c */

undefined8 FUN_437abd3c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  undefined1 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  short sVar10;
  int iVar11;
  short sVar12;
  short sVar13;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined2 uStack_2e;
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uStack_2c = (undefined1)param_2;
  uStack_2b = (undefined1)((uint)param_2 >> 8);
  uStack_2a = (undefined1)((uint)param_2 >> 0x10);
  uStack_29 = (undefined1)((uint)param_2 >> 0x18);
  uStack_30 = SUB41(param_1,0);
  uStack_2f = (undefined1)((uint)param_1 >> 8);
  uStack_2e = (undefined2)((uint)param_1 >> 0x10);
  iVar9 = *(int *)param_1[1];
  iVar11 = DAT_437ac0ac + 0x437abd4c;
  uVar2 = *(ushort *)(*param_1 + 0x10c);
  iVar7 = *(int *)(iVar11 + DAT_437ac0b0);
  if (*(char *)(param_1[2] + 2) == '\0') {
    cVar1 = *(char *)(iVar7 + 0x10);
    sVar10 = *(short *)(iVar7 + 0x16);
    sVar12 = *(short *)(iVar7 + 0x14);
    sVar13 = *(short *)(iVar7 + 0x12);
  }
  else {
    cVar1 = *(char *)(iVar7 + 0x11);
    sVar10 = *(short *)(iVar7 + 0x1c);
    sVar12 = *(short *)(iVar7 + 0x1a);
    sVar13 = *(short *)(iVar7 + 0x18);
  }
  uStack_28 = param_3;
  uStack_24 = param_4;
  if (cVar1 == '\x03') {
    iVar7 = FUN_43aeb0cc(*(undefined1 *)(*(int *)(iVar11 + DAT_437ac0b4) + 3),4);
    if (iVar7 == 0) goto LAB_437abd90;
  }
  else {
    uVar3 = 1;
    if (cVar1 == '\x01') goto LAB_437abdba;
    if (cVar1 != '\x02') {
      sVar10 = 0x7ff;
      sVar12 = 0x3ff;
      sVar13 = 0x7ff;
      uVar3 = 0;
      goto LAB_437abdba;
    }
LAB_437abd90:
    uVar2 = uVar2 >> 2;
    sVar13 = sVar13 - uVar2;
    sVar12 = sVar12 - uVar2;
    sVar10 = sVar10 - uVar2;
  }
  uVar3 = 1;
LAB_437abdba:
  *(undefined1 *)(iVar9 + 0x32) = uVar3;
  *(short *)(iVar9 + 0x34) = sVar13;
  *(short *)(iVar9 + 0x36) = sVar12;
  *(short *)(iVar9 + 0x38) = sVar10;
  FUN_437abb14(iVar9 + 0x3a,param_1);
  iVar7 = param_1[2];
  iVar8 = 0;
  do {
    iVar4 = iVar7 + iVar8;
    iVar5 = iVar9 + iVar8;
    iVar8 = iVar8 + 2;
    *(undefined2 *)(iVar5 + 0x4c) = *(undefined2 *)(iVar4 + 0xae);
  } while (iVar8 != 0x10);
  *(undefined1 *)(iVar9 + 0x5c) = *(undefined1 *)(iVar7 + 0xd1);
  *(undefined1 *)(iVar9 + 0x5d) = *(undefined1 *)(param_1[2] + 0xd0);
  *(undefined1 *)(iVar9 + 0x5e) = *(undefined1 *)(param_1[2] + 2);
  *(undefined1 *)(iVar9 + 0x5f) = *(undefined1 *)(param_1[2] + 4);
  FUN_43827594(&uStack_30,param_1);
  *(undefined1 *)(iVar9 + 0x8b) = uStack_2f;
  *(undefined2 *)(iVar9 + 0x8c) = uStack_2e;
  *(undefined1 *)(iVar9 + 0x8a) = uStack_30;
  *(undefined1 *)(iVar9 + 0x8e) = uStack_2c;
  *(undefined1 *)(iVar9 + 0x8f) = uStack_2b;
  *(undefined1 *)(iVar9 + 0x90) = uStack_2a;
  FUN_43827800(&uStack_28,param_1);
  *(undefined1 *)(iVar9 + 0x92) = (undefined1)uStack_28;
  *(undefined1 *)(iVar9 + 0x93) = uStack_28._1_1_;
  *(undefined1 *)(iVar9 + 0x97) = uStack_24._1_1_;
  *(undefined1 *)(iVar9 + 0x94) = uStack_28._2_1_;
  *(undefined1 *)(iVar9 + 0x95) = uStack_28._3_1_;
  *(undefined1 *)(iVar9 + 0x96) = (undefined1)uStack_24;
  *(undefined1 *)(iVar9 + 0x98) = uStack_24._2_1_;
  *(undefined1 *)(iVar9 + 0x99) = 0;
  *(undefined1 *)(iVar9 + 0x9a) = *(undefined1 *)(param_1[2] + 0xa9);
  *(undefined1 *)(iVar9 + 0x9b) = *(undefined1 *)(param_1[2] + 0xa8);
  *(undefined1 *)(iVar9 + 0xae) = *(undefined1 *)(param_1[2] + 0xac);
  *(undefined1 *)(iVar9 + 0xad) = *(undefined1 *)(param_1[2] + 0xaa);
  *(undefined1 *)(iVar9 + 0xac) = *(undefined1 *)(param_1[2] + 0xab);
  *(undefined1 *)(iVar9 + 0x9e) = *(undefined1 *)(param_1[2] + 0x99);
  *(undefined1 *)(iVar9 + 0x9f) = *(undefined1 *)(param_1[2] + 0x98);
  *(undefined1 *)(iVar9 + 0x9c) = *(undefined1 *)(param_1[2] + 0x9f);
  *(undefined1 *)(iVar9 + 0x9d) = *(undefined1 *)(param_1[2] + 0x9e);
  *(undefined1 *)(iVar9 + 0xa4) = *(undefined1 *)(param_1[2] + 0x9d);
  *(undefined1 *)(iVar9 + 0xa5) = *(undefined1 *)(param_1[2] + 0x9c);
  *(undefined1 *)(iVar9 + 0xa6) = *(undefined1 *)(param_1[2] + 0x9b);
  *(undefined1 *)(iVar9 + 0xa7) = *(undefined1 *)(param_1[2] + 0x9a);
  *(undefined1 *)(iVar9 + 0xa0) = *(undefined1 *)(param_1[2] + 0xa3);
  *(undefined1 *)(iVar9 + 0xa1) = *(undefined1 *)(param_1[2] + 0xa2);
  *(undefined1 *)(iVar9 + 0xa2) = *(undefined1 *)(param_1[2] + 0xa1);
  *(undefined1 *)(iVar9 + 0xa3) = *(undefined1 *)(param_1[2] + 0xa0);
  *(undefined1 *)(iVar9 + 0xaa) = *(undefined1 *)(param_1[2] + 0xa5);
  *(undefined1 *)(iVar9 + 0xab) = *(undefined1 *)(param_1[2] + 0xa4);
  *(undefined1 *)(iVar9 + 0xa8) = *(undefined1 *)(param_1[2] + 0xa7);
  *(undefined1 *)(iVar9 + 0xa9) = *(undefined1 *)(param_1[2] + 0xa6);
  *(undefined1 *)(iVar9 + 0xaf) = *(undefined1 *)(param_1[2] + 0x84);
  *(undefined1 *)(iVar9 + 0xb0) = *(undefined1 *)(param_1[2] + 0x88);
  iVar7 = *(int *)(iVar11 + DAT_437ac0b8);
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),5);
  *(undefined1 *)(iVar9 + 0xb1) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),4);
  *(undefined1 *)(iVar9 + 0xb2) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),3);
  *(undefined1 *)(iVar9 + 0xb3) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),2);
  *(undefined1 *)(iVar9 + 0xb4) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),1);
  *(undefined1 *)(iVar9 + 0xb5) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),0);
  *(undefined1 *)(iVar9 + 0xb6) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f9),3);
  *(undefined1 *)(iVar9 + 0xb7) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f9),2);
  *(undefined1 *)(iVar9 + 0xb8) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f9),1);
  *(undefined1 *)(iVar9 + 0xb9) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f9),0);
  *(undefined1 *)(iVar9 + 0xba) = uVar3;
  *(undefined1 *)(iVar9 + 0xbb) = *(undefined1 *)(param_1[2] + 0x85);
  *(undefined1 *)(iVar9 + 0xbc) = *(undefined1 *)(param_1[2] + 0x86);
  if (*(char *)(param_1[2] + 0x87) == '\x01') {
    *(undefined1 *)(iVar9 + 0xbd) = 0;
  }
  else {
    *(undefined1 *)(iVar9 + 0xbd) = 1;
  }
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),7);
  *(undefined1 *)(iVar9 + 0xbf) = 0;
  *(undefined1 *)(iVar9 + 0xbe) = uVar3;
  uVar3 = FUN_43aeb0cc(*(undefined1 *)(iVar7 + 0x2f8),6);
  *(undefined1 *)(iVar9 + 0xc0) = uVar3;
  iVar7 = param_1[2];
  uVar6 = *(undefined4 *)(iVar7 + 0x90);
  *(undefined4 *)(iVar9 + 0xc4) = *(undefined4 *)(iVar7 + 0x8c);
  *(undefined4 *)(iVar9 + 200) = uVar6;
  *(undefined1 *)(iVar9 + 0xcc) = *(undefined1 *)(iVar7 + 0x1e4);
  iVar7 = param_1[2];
  *(undefined2 *)(iVar9 + 0xce) = *(undefined2 *)(iVar7 + 0x1e6);
  *(undefined2 *)(iVar9 + 0xd0) = *(undefined2 *)(iVar7 + 0x1e8);
  *(undefined1 *)(iVar9 + 0xd2) = *(undefined1 *)(iVar7 + 0x1ea);
  if (*(char *)(*param_1 + 3) != '\0') {
    iVar11 = *(int *)(iVar11 + DAT_437ac0bc);
    iVar7 = FUN_43aeb0cc(*(undefined1 *)(iVar11 + 0x38),0);
    if (iVar7 == 1) {
      *(undefined1 *)(iVar9 + 0xaf) = 0;
    }
    if (*(short *)(iVar11 + 0x3a) != 0) {
      *(undefined1 *)(iVar9 + 0xaf) = 0;
    }
  }
  return CONCAT17(uStack_29,
                  CONCAT16(uStack_2a,
                           CONCAT15(uStack_2b,
                                    CONCAT14(uStack_2c,
                                             CONCAT22(uStack_2e,CONCAT11(uStack_2f,uStack_30))))));
}


/* 437d8a80 */

undefined4 FUN_437d8a80(int param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  int iVar5;
  int aiStack_1c [2];
  
  iVar1 = FUN_43b1531e();
  if (iVar1 == 1) {
    iVar1 = FUN_43899f3c(param_1);
    if (iVar1 == 0) {
      uVar4 = 0x40;
      uVar3 = 2;
    }
    else {
      uVar4 = 0xc0;
      uVar3 = 4;
    }
  }
  else if (iVar1 == 2) {
    iVar1 = FUN_43899f3c(param_1);
    if (iVar1 == 0) {
      uVar4 = 0x20;
      uVar3 = 1;
    }
    else {
      uVar4 = 0xa0;
      uVar3 = 3;
    }
  }
  else if (iVar1 == 0) {
    uVar4 = 0x10;
    uVar3 = 0;
  }
  else {
    iVar5 = DAT_437d8bb8 + 0x437d8ad8;
    FUN_437d7d90(3,7,1,DAT_437d8bb4 + 0x437d8ad4,iVar5,iVar1);
    uVar4 = 0;
    uVar3 = 0;
    FUN_43902718(DAT_437d8bbc + 0x437d8ae8,iVar5,iVar1);
  }
  aiStack_1c[0] = 0;
  iVar1 = FUN_438b7f8c(aiStack_1c,*(undefined4 *)(*(int *)(param_1 + 0x38) + 8));
  if (iVar1 != 0) {
    FUN_437d7d90(3,7,1,DAT_437d8bc0 + 0x437d8b12,iVar1);
    FUN_43902718(DAT_437d8bc4 + 0x437d8b1c,iVar1);
    return uVar3;
  }
  if (*(int *)(param_1 + 0x10) == 9) {
    switch(*(undefined4 *)(param_1 + 0x28)) {
    case 0:
      uVar2 = 1;
      break;
    case 1:
    case 4:
      uVar2 = 3;
      break;
    case 2:
    case 5:
      uVar2 = 4;
      break;
    case 3:
      goto switchD_437d8b30_caseD_3;
    case 6:
      uVar2 = 2;
      break;
    default:
      iVar1 = DAT_437d8bcc + 0x437d8b56;
      FUN_437d7d90(3,7,1,DAT_437d8bc8 + 0x437d8b54,iVar1,*(undefined4 *)(param_1 + 0x28));
      FUN_43902718(DAT_437d8bd0 + 0x437d8b64,iVar1,*(undefined4 *)(param_1 + 0x28));
    case 7:
      uVar2 = 5;
    }
  }
  else {
    uVar2 = *(int *)(param_1 + 8) - *(int *)(param_1 + 0xc);
    if (uVar2 != 0) {
      if (4 < uVar2) {
        uVar2 = 5;
      }
      goto LAB_437d8b9e;
    }
switchD_437d8b30_caseD_3:
    uVar2 = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x788) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x789) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x9a) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x94) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x95) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x96) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x97) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x98) = 0;
    *(undefined1 *)(aiStack_1c[0] + 0x99) = 0;
  }
LAB_437d8b9e:
  *(undefined1 *)(aiStack_1c[0] + uVar2 + 0x94) = uVar4;
  return uVar3;
}


/* 437edaf8 */

void FUN_437edaf8(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  char cVar5;
  undefined1 auStack_40 [32];
  
  cVar5 = *(char *)(*(int *)(DAT_437edcf0 + 0x437edb06 + DAT_437edcf4) + 0x74);
  if ((cVar5 != '\0') && (cVar5 != '\x01')) {
    iVar4 = DAT_437edcfc + 0x437edb2c;
    cVar5 = '\0';
    FUN_437ed9f8(5,0,1,DAT_437edcf8 + 0x437edb2a,iVar4,0x11d);
    FUN_43902718(DAT_437edd00 + 0x437edb46,iVar4,0x11d);
  }
  iVar4 = param_1 + 0x20;
  FUN_43b17190(iVar4,param_2,cVar5,param_3);
  FUN_43b17480(param_1 + 0x1d8,param_2 + 0x200,cVar5,param_3);
  FUN_4379fae0(param_1 + 0x2c2c,iVar4,param_2 + 0x600,cVar5,param_3);
  thunk_FUN_43b13aca(param_1 + 0x30e0,iVar4,param_2 + 0xa00,cVar5,param_3);
  FUN_43affc8e(iVar4,auStack_40);
  uVar1 = FUN_43affcde(param_3);
  FUN_43b72542(param_1 + 0x37c4,param_2 + 0xa48,uVar1);
  FUN_43b0c7d4(param_1 + 0x1198,iVar4,param_2 + 0x1284,cVar5,param_3);
  FUN_43af0b5e(param_1 + 0x3388,iVar4,param_2 + 0x268c,cVar5,param_3);
  FUN_43b10928(param_1 + 0x486c,param_2 + 0x269c,cVar5,param_3);
  if (param_3 == 0) {
    *(undefined4 *)(param_1 + 0x4b70) = *(undefined4 *)(param_2 + 0x27e4);
    *(undefined1 *)(param_1 + 0x4b8c) = *(undefined1 *)(param_2 + 0x27f0);
    uVar1 = *(undefined4 *)(param_2 + 0x28c4);
    uVar2 = *(undefined4 *)(param_2 + 0x28c8);
    uVar3 = *(undefined4 *)(param_2 + 0x28cc);
    *(undefined4 *)(param_1 + 0x4b98) = *(undefined4 *)(param_2 + 0x28c0);
    *(undefined4 *)(param_1 + 0x4b9c) = uVar1;
    *(undefined4 *)(param_1 + 0x4ba0) = uVar2;
    *(undefined4 *)(param_1 + 0x4ba4) = uVar3;
    uVar1 = *(undefined4 *)(param_2 + 0x28d4);
    *(undefined4 *)(param_1 + 0x4ba8) = *(undefined4 *)(param_2 + 0x28d0);
    *(undefined4 *)(param_1 + 0x4bac) = uVar1;
    uVar1 = *(undefined4 *)(param_2 + 0x28dc);
    uVar2 = *(undefined4 *)(param_2 + 0x28e0);
    uVar3 = *(undefined4 *)(param_2 + 0x28e4);
    *(undefined4 *)(param_1 + 0x4fd4) = *(undefined4 *)(param_2 + 0x28d8);
    *(undefined4 *)(param_1 + 0x4fd8) = uVar1;
    *(undefined4 *)(param_1 + 0x4fdc) = uVar2;
    *(undefined4 *)(param_1 + 0x4fe0) = uVar3;
    if (cVar5 == '\0') {
      *(undefined4 *)(param_1 + 0x4b68) = *(undefined4 *)(param_2 + 0x27dc);
      *(undefined4 *)(param_1 + 0x4b6c) = *(undefined4 *)(param_2 + 0x27e0);
      *(undefined4 *)(param_1 + 0x4b60) = *(undefined4 *)(param_2 + 0x27e8);
      *(undefined4 *)(param_1 + 0x4b88) = *(undefined4 *)(param_2 + 0x27ec);
      *(undefined4 *)(param_1 + 0x4b90) = *(undefined4 *)(param_2 + 0x27f4);
      *(undefined1 *)(param_1 + 0x4b94) = *(undefined1 *)(param_2 + 0x27f8);
      *(undefined1 *)(param_1 + 0x4b95) = *(undefined1 *)(param_2 + 0x27f9);
      FUN_439c5320(param_1 + 0x4efa,param_2 + 0x27fa,0x3c);
      FUN_439c5320(param_1 + 0x4f36,param_2 + 0x2836,0xc);
      FUN_439c5320(param_1 + 0x4f42,param_2 + 0x2842,0xc);
      FUN_439c5320(param_1 + 0x4f76,param_2 + 0x2876,0xc);
      FUN_439c5320(param_1 + 0x4f82,param_2 + 0x2882,0xc);
      FUN_439c5320(param_1 + 0x4f8e,param_2 + 0x288e,0xc);
      FUN_439c5320(param_1 + 0x4f9a,param_2 + 0x289a,0xc);
      FUN_439c5320(param_1 + 0x4fa6,param_2 + 0x28a6,0xc);
      FUN_439c5320(param_1 + 0x4fb2,param_2 + 0x28b2,0xc);
    }
  }
  return;
}


/* 438631c4 */

void FUN_438631c4(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7,int param_8,short *param_9)

{
  int iVar1;
  short sVar2;
  ushort uVar3;
  byte bVar4;
  byte bVar5;
  short sVar6;
  ushort uVar7;
  short sVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  ushort uVar11;
  int *piVar12;
  int iVar13;
  short *psVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  short sVar18;
  undefined4 uVar19;
  int iVar20;
  uint uVar21;
  short *psVar22;
  int *piVar23;
  ushort *puVar24;
  char cVar25;
  undefined1 uVar26;
  short sVar27;
  int iVar28;
  int iVar29;
  uint uVar30;
  int iVar31;
  uint *puVar32;
  undefined4 uVar33;
  int iVar34;
  uint uVar35;
  int iVar36;
  uint uVar37;
  undefined1 uVar38;
  int iVar39;
  undefined4 *puVar40;
  uint uStack_84;
  int iStack_68;
  int aiStack_64 [14];
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  uVar33 = *(undefined4 *)(param_1 + 0x3c0);
  iVar31 = DAT_43863dc8 + 0x438631da;
  uVar19 = *(undefined4 *)(param_1 + 0x3bc);
  *(undefined4 *)(param_9 + 8) = uVar19;
  *(undefined4 *)(param_9 + 10) = uVar33;
  *(undefined1 *)(param_9 + 0x10) = *(undefined1 *)(param_1 + 0x3d6);
  *(undefined1 *)((int)param_9 + 0x21) = *(undefined1 *)(param_6 + 0x42);
  *(undefined1 *)(param_9 + 0x11) = *(undefined1 *)(param_6 + 0x32);
  sVar6 = *(short *)(param_1 + 0x2f0);
  sVar8 = *(short *)(param_1 + 0x11e);
  param_9[0x12] = *(short *)(param_2 + 0x1c6);
  sVar2 = *(short *)(param_2 + 0x54);
  param_9[0x13] = sVar6;
  param_9[0x16] = sVar8;
  param_9[0x17] = sVar2;
  *(undefined1 *)(param_9 + 0x1a) = *(undefined1 *)(param_4 + 2);
  iVar34 = *(int *)(iVar31 + DAT_43863dcc);
  *(undefined1 *)((int)param_9 + 0x35) = *(undefined1 *)(iVar34 + 0x22);
  iVar28 = 0;
  *(undefined1 *)((int)param_9 + 0x37) = 0;
  *(undefined1 *)((int)param_9 + 0x31) = *(undefined1 *)(param_1 + 0x22a);
  *(undefined1 *)(param_9 + 0x1e) = *(undefined1 *)(param_1 + 0x432);
  *(undefined1 *)((int)param_9 + 0x3d) = *(undefined1 *)(param_1 + 0x433);
  piVar12 = *(int **)(iVar31 + DAT_43863dd0);
  *(undefined1 *)(param_9 + 0x1f) = *(undefined1 *)(*piVar12 + 0x286);
  param_9[0x20] = *(short *)(param_2 + 0x1e4);
  *(undefined1 *)(param_9 + 0x232) = *(undefined1 *)(param_1 + 0x657);
  *(undefined1 *)((int)param_9 + 0x465) = *(undefined1 *)(param_1 + 0x658);
  sVar6 = *(short *)(param_7 + 0x4c4);
  param_9[0x235] = *(short *)(param_7 + 0x4c2);
  uVar33 = *(undefined4 *)(param_1 + 0x640);
  param_9[0x236] = sVar6;
  *(undefined4 *)(param_9 + 0x248) = uVar33;
  *(undefined1 *)((int)param_9 + 0x495) = *(undefined1 *)(param_5 + 0xbd9);
  *(undefined1 *)(param_9 + 0x24b) = *(undefined1 *)(param_5 + 0xbd6);
  param_9[0x16b] = *(short *)(param_5 + 0xc6a);
  psVar14 = param_9;
  do {
    iVar13 = param_7 + iVar28;
    iVar28 = iVar28 + 4;
    psVar14[0x237] = *(short *)(iVar13 + 4);
    psVar14 = psVar14 + 1;
  } while (iVar28 != 0x38);
  if ((*(int *)(param_1 + 700) == 0) || (*(int *)(param_1 + 700) == 4)) {
    uVar26 = 0;
  }
  else {
    uVar26 = 1;
  }
  *(undefined1 *)(param_9 + 0x18) = uVar26;
  sVar6 = *(short *)(param_1 + 0x576);
  sVar8 = *(short *)(param_1 + 0x512);
  sVar2 = *(short *)(param_1 + 0x514);
  sVar18 = *(short *)(param_1 + 0x578);
  param_9[0x279] = *(short *)(param_1 + 0x510);
  param_9[0x282] = sVar6;
  sVar6 = *(short *)(param_1 + 0x57a);
  uVar33 = *(undefined4 *)(param_1 + 0x4f8);
  param_9[0x27a] = sVar8;
  param_9[0x27b] = sVar2;
  param_9[0x283] = sVar18;
  param_9[0x284] = sVar6;
  *(char *)(param_9 + 0x285) = (char)uVar33;
  iVar28 = FUN_4382ffe0((char)param_9[0x18],uVar19);
  if (iVar28 == 0) {
    param_9[0x19] = 0;
  }
  else if (*(char *)(param_8 + 1) == '\x01') {
    param_9[0x19] = 1;
  }
  else {
    param_9[0x19] = 0;
  }
  FUN_4386208c(param_9);
  FUN_43b0ad1c(param_9);
  sVar6 = FUN_439027ec((int)param_9[0x13],0x100);
  iVar28 = (int)param_9[0x13];
  param_9[0x14] = sVar6;
  if (iVar28 < 0) {
    cVar25 = -(char)(iVar28 + 0x3f >> 6);
  }
  else {
    cVar25 = (char)(iVar28 >> 6);
  }
  *(char *)(param_9 + 0x15) = cVar25;
  if (0x1f < *(byte *)(param_9 + 0x15)) {
    *(undefined1 *)(param_9 + 0x15) = 0x1f;
  }
  iVar28 = DAT_43863dd4;
  *(undefined1 *)(param_9 + 6) = 1;
  iVar28 = *(int *)(iVar31 + iVar28);
  if ((*(int *)(param_9 + 8) == 0) && (*(char *)(iVar28 + 0x49) == '\0')) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x924) == 1) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((*(char *)(iVar28 + 0x49) == '\x01') && (*(int *)(param_1 + 0x40c) != 0)) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x2b4) == 0x1f) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  cVar25 = *(char *)(iVar34 + 2);
  if ((cVar25 == '\x01') || (cVar25 == '\x02')) {
    *(char *)(param_9 + 6) = cVar25 + -1;
  }
  if (*(char *)((int)param_9 + 0x21) != '\0') {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((char)param_9[0x11] != '\0') {
    *(undefined1 *)(param_9 + 6) = 1;
  }
  uVar26 = 0;
  if ((char)param_9[6] == '\0') {
LAB_43863652:
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
  }
  else {
    sVar6 = param_9[0x14];
    iVar29 = 0;
    iVar13 = param_3;
    iVar39 = param_3;
    do {
      iVar17 = 0;
      puVar32 = (uint *)(param_9 + iVar29 * 2 + 0x20);
      iVar20 = iVar17;
      do {
        iVar36 = iVar39 + iVar17;
        iVar17 = iVar17 + 0xc;
        iVar1 = iVar20 * 2;
        puVar32 = puVar32 + 1;
        *puVar32 = (uint)(*(int *)(iVar36 + 0x338) * (int)sVar6) >> 8;
        iVar36 = iVar20 + iVar29;
        iVar20 = iVar20 + 1;
        *(undefined1 *)((int)param_9 + iVar36 + 0x1d0) = *(undefined1 *)(iVar13 + iVar1 + 0x964);
      } while (iVar20 != 0xb);
      iVar29 = iVar29 + 0xb;
      iVar13 = iVar13 + 0x16;
      iVar39 = iVar39 + 0x84;
    } while (iVar29 != 99);
    iVar13 = 0;
    psVar14 = param_9;
    do {
      iVar13 = iVar13 + 1;
      uVar21 = 0;
      psVar14[0x11a] = 0;
      psVar14[0x11b] = 0;
      psVar14 = psVar14 + 2;
    } while (iVar13 != 0x20);
    uVar30 = (uint)*(byte *)(param_9 + 0x15);
    iVar13 = 0;
    if (uVar30 == 0) {
      do {
        iVar39 = iVar13 + 4;
        *(undefined4 *)((int)param_9 + iVar13 + 0x234) = *(undefined4 *)(param_7 + iVar13 + 0xa4);
        iVar13 = iVar39;
      } while (iVar39 != 0x80);
    }
    else {
      iVar13 = param_7;
      if (param_9[0x13] < 0) {
        for (; uVar21 <= uVar30; uVar21 = uVar21 + 1) {
          *(int *)(param_9 + 0x11a) = *(int *)(iVar13 + 0xa4) + *(int *)(param_9 + 0x11a);
          iVar13 = iVar13 + 4;
        }
        puVar40 = (undefined4 *)(param_7 + uVar30 * 4 + 0xa4);
        uVar21 = 1;
        psVar14 = param_9;
        while( true ) {
          uVar35 = 0x20 - uVar30;
          if (uVar35 <= uVar21) break;
          puVar40 = puVar40 + 1;
          uVar21 = uVar21 + 1;
          *(undefined4 *)(psVar14 + 0x11c) = *puVar40;
          psVar14 = psVar14 + 2;
        }
        psVar14 = param_9 + uVar35 * 2 + 0x118;
        for (; uVar35 < 0x20; uVar35 = uVar35 + 1) {
          psVar14 = psVar14 + 2;
          psVar14[0] = 0;
          psVar14[1] = 0;
        }
      }
      else {
        uVar21 = 0;
        psVar14 = param_9;
        while( true ) {
          iVar13 = 0;
          uVar35 = uVar30;
          if (uVar30 <= uVar21) break;
          psVar14[0x11a] = 0;
          psVar14[0x11b] = 0;
          uVar21 = uVar21 + 1;
          psVar14 = psVar14 + 2;
        }
        for (; uVar35 < 0x1f; uVar35 = uVar35 + 1) {
          iVar29 = param_7 + iVar13;
          iVar39 = iVar13 + uVar30 * 4;
          iVar13 = iVar13 + 4;
          *(undefined4 *)((int)param_9 + iVar39 + 0x234) = *(undefined4 *)(iVar29 + 0xa4);
        }
        uVar30 = 0x20 - uVar30;
        piVar23 = (int *)(param_7 + uVar30 * 4 + 0xa0);
        for (; uVar30 < 0x20; uVar30 = uVar30 + 1) {
          piVar23 = piVar23 + 1;
          *(int *)(param_9 + 0x158) = *(int *)(param_9 + 0x158) + *piVar23;
        }
      }
    }
    iVar13 = *(int *)(param_7 + 0x4bc);
    if (iVar13 == 0) {
      iVar13 = 0x10000;
    }
    *(int *)(param_9 + 0x15a) = iVar13;
    FUN_43b0abd8(param_9);
    sVar6 = *param_9;
    if (sVar6 == 0) {
      sVar6 = param_9[0x160];
    }
    sVar8 = param_9[1];
    if (sVar8 == 0) {
      sVar8 = param_9[0x161];
    }
    sVar2 = param_9[2];
    if (sVar2 == 0) {
      sVar2 = param_9[0x162];
    }
    sVar18 = param_9[3];
    if (sVar18 == 0) {
      sVar18 = param_9[0x161];
    }
    uVar7 = param_9[4];
    if ((ushort)param_9[5] < (ushort)param_9[4]) {
      uVar7 = param_9[5];
    }
    param_9[0x168] = uVar7;
    sVar27 = param_9[0x13] * 4;
    param_9[0x167] = sVar18 + sVar27;
    param_9[0x164] = sVar6 + sVar27;
    param_9[0x165] = sVar8 + sVar27;
    param_9[0x166] = sVar2 + sVar27;
    if ((param_9[0x19] == 0) || (*(char *)(param_3 + 0xc35) == '\0')) {
      param_9[0x16c] = 0;
      param_9[0x169] = 0;
      param_9[0x16a] = 0;
    }
    else {
      uVar7 = FUN_4355faf0(*(undefined4 *)(param_8 + 4));
      param_9[0x169] = uVar7;
      if (0x3ff < uVar7) {
        param_9[0x169] = 0x3ff;
      }
      sVar6 = FUN_438625d0(((ushort)param_9[0x169] & 0x3fff) << 2);
      param_9[0x16a] = sVar6 + param_9[0x13] * 4;
      sVar6 = FUN_438625d0(((ushort)param_9[0x16b] & 0x3fff) << 2);
      param_9[0x16c] = sVar6;
    }
    if (param_9[0x19] == 0) {
      if (((char)param_9[0x10] == '\x01') && (*(char *)(iVar28 + 0x49) == '\x01')) {
        uVar26 = 7;
      }
      else {
        uVar26 = 1;
      }
    }
    else {
      uVar26 = 5;
    }
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
    if ((((char)param_9[0x1f] != '\0') && (*(char *)(iVar28 + 0x49) == '\x01')) &&
       ((char)param_9[0x10] == '\x01')) {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if ((char)param_9[0x11] != '\0') {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if (*(char *)((int)param_9 + 0x35) != '\0') {
      uVar26 = 8;
      goto LAB_43863652;
    }
  }
  if ((char)param_9[6] == '\0') goto LAB_43863fe2;
  if (*(char *)(param_1 + 0xc) == '\x04') {
    FUN_439c5320(param_9 + 0x187,param_9 + 0x19b,0x14);
    FUN_439c5320(param_9 + 0x191,param_9 + 0x1a5,0x14);
    goto LAB_43863fe2;
  }
  FUN_43861ed0(param_9);
  FUN_43865254(param_9);
  if (((char)param_9[0x1f] == '\0') || ((char)param_9[0x10] != '\x01')) {
    iVar13 = *(int *)(param_9 + 8);
    if (((iVar13 == 1) || (iVar13 == 8)) || ((iVar13 == 0 && (*(char *)(iVar28 + 0x49) == '\x01'))))
    {
      FUN_438621bc(param_9);
    }
    FUN_43b0acee(param_9);
    FUN_43b0ad9a(param_9);
    FUN_43b0ace4(param_9);
    if ((char)param_9[0x11] == '\0') {
      if (*(char *)((int)param_9 + 0x31) == '\0') {
        bVar4 = *(byte *)(iVar34 + 0xcb);
      }
      else {
        bVar4 = *(byte *)(iVar34 + 0xcc);
      }
      uVar11 = (ushort)bVar4 * 2;
      uVar7 = param_9[0x21c];
      if (param_9[0x19] == 0) {
        uVar26 = 0;
        if (uVar7 != 0) {
          param_9[0x21c] = uVar7 - 1;
          goto LAB_438636fa;
        }
LAB_438636fc:
        *(undefined1 *)(param_9 + 0x21d) = uVar26;
      }
      else {
        if (uVar11 <= uVar7) {
LAB_438636fa:
          uVar26 = 1;
          goto LAB_438636fc;
        }
        if ((char)param_9[0x21d] == '\0') {
          uVar3 = (ushort)*(byte *)(iVar34 + 0xcd);
        }
        else {
          uVar3 = 1;
        }
        param_9[0x21c] = uVar7 + uVar3;
      }
      if (uVar11 < (ushort)param_9[0x21c]) {
        param_9[0x21c] = uVar11;
      }
      if ((char)param_9[0x21d] == '\0') {
        if (*(char *)(iVar34 + 0xca) == '\0') goto LAB_4386372a;
        uVar26 = *(undefined1 *)(iVar34 + 0xce);
      }
      else if (*(char *)(iVar34 + 0xca) == '\0') {
LAB_4386372a:
        uVar26 = *(undefined1 *)(iVar34 + 0xd0);
      }
      else {
        uVar26 = *(undefined1 *)(iVar34 + 0xcf);
      }
      param_9[0x187] = 0;
      param_9[0x191] = 0;
      param_9[0x1e8] = 0;
      param_9[0x1e9] = 0;
      param_9[0x1fc] = 0;
      param_9[0x1fd] = 0;
      param_9[400] = 0x3400;
      param_9[0x19a] = 0x3400;
      param_9[0x1fa] = 0x3400;
      param_9[0x1fb] = 0;
      param_9[0x20e] = 0x3400;
      param_9[0x20f] = 0;
      if (*(char *)(iVar34 + 0x55) == '\0') {
        if ((char)param_9[0x24a] == '\0') {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar26 = 0;
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,0,0,0);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,0,0,0);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
        else {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar38 = *(undefined1 *)(DAT_43863dd8 + 0x438637d2);
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,uVar26,uVar26,uVar38);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,uVar26,uVar26,uVar38);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
      }
      *(undefined1 *)(param_9 + 0x24a) = 1;
      *(undefined1 *)(DAT_43863ddc + 0x43863822) = uVar26;
      psVar14 = param_9;
      iVar28 = 0;
      do {
        iVar13 = iVar28;
        uVar30 = (uint)(ushort)psVar14[0x187];
        uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
        uVar21 = (uint)(ushort)psVar14[0x191];
        uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
        iVar28 = 0;
        psVar22 = param_9 + iVar13 + 0x1ae;
        do {
          iVar28 = iVar28 + 1;
          psVar22[1] = (short)uVar30;
          psVar22[0x1d] = (short)uVar21;
          uVar30 = uVar30 + uVar7 & 0xffff;
          uVar21 = uVar21 + uVar11 & 0xffff;
          psVar22 = psVar22 + 1;
        } while (iVar28 != 3);
        psVar14 = psVar14 + 1;
        iVar28 = iVar13 + 3;
      } while (iVar13 + 3 != 0x18);
      iVar13 = iVar13 + -0x14;
      psVar14 = param_9;
      do {
        uVar7 = psVar14[0x1cd];
        iVar13 = iVar13 + 1;
        sVar6 = FUN_43b07560(((uint)(ushort)psVar14[0x1b2] - (uint)(ushort)psVar14[0x1b1]) *
                             ((uint)(ushort)psVar14[0x1cf] - (uint)uVar7),
                             (uint)(ushort)psVar14[0x1b3] - (uint)(ushort)psVar14[0x1b1]);
        psVar14[0x1ce] = sVar6 + uVar7;
        psVar14 = psVar14 + 3;
      } while (iVar13 != 8);
      uVar7 = param_9[399];
      param_9[0x1af] = param_9[0x187];
      uVar11 = param_9[0x19a];
      uVar3 = param_9[0x199];
      param_9[0x1c7] = uVar7;
      param_9[0x1e3] = uVar3;
      param_9[0x1ca] = param_9[400];
      param_9[0x1cb] = param_9[0x191];
      param_9[0x1e6] = uVar11;
      sVar6 = FUN_4355fd68((uint)(ushort)param_9[400] - (uint)uVar7,3);
      sVar8 = FUN_4355fd68((uint)uVar11 - (uint)uVar3,3);
      param_9[0x1c8] = sVar6 + uVar7;
      param_9[0x1c9] = uVar7 + sVar6 * 2;
      param_9[0x1e4] = sVar8 + uVar3;
      param_9[0x1e5] = uVar3 + sVar8 * 2;
      if ((char)param_9[0x18] == '\x01') {
        piVar23 = *(int **)(iVar31 + DAT_43863dd0);
        iVar28 = *piVar23;
        if (*(char *)(iVar28 + 0x229) != '\0') {
          uVar21 = *(byte *)(param_5 + 0xbd9) - 0x14 & 0xff;
          if (uVar21 < 4) {
            uVar33 = *(undefined4 *)(DAT_43863de0 + 0x4386395e + uVar21 * 4);
          }
          else {
            uVar33 = 0;
          }
          if (*(char *)(iVar28 + 0x22b) == '\x01') {
            switch(uVar33) {
            case 1:
              uVar30 = (uint)*(byte *)(iVar28 + 0x275);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x276) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x277));
              break;
            case 2:
              uVar30 = (uint)*(byte *)(iVar28 + 0x278);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x279) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27a));
              break;
            case 3:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27b);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27c) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27d));
              break;
            case 4:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27e);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27f) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x280));
              break;
            default:
              uVar30 = (uint)*(byte *)(iVar28 + 0x272);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x273) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x274));
            }
            uVar30 = uVar30 * 0x10 + 0x2000;
          }
          else if (*(char *)(iVar28 + 0x22b) == '\x02') {
            switch(uVar33) {
            case 1:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x23e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x23f);
              uVar26 = *(undefined1 *)(iVar28 + 0x23d);
              uVar38 = *(undefined1 *)(iVar28 + 0x23c);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x240),
                                      *(undefined1 *)(iVar28 + 0x241));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x242) * 0x100 + (ushort)*(byte *)(iVar28 + 0x243);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x23b);
              uVar21 = (uint)*(byte *)(iVar28 + 0x23a);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x244),
                                      *(undefined1 *)(iVar28 + 0x245));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x246),
                                      *(undefined1 *)(iVar28 + 0x247));
              break;
            case 2:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x24c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x24d);
              uVar26 = *(undefined1 *)(iVar28 + 0x24b);
              uVar38 = *(undefined1 *)(iVar28 + 0x24a);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x24e),
                                      *(undefined1 *)(iVar28 + 0x24f));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x250) * 0x100 + (ushort)*(byte *)(iVar28 + 0x251);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x249);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x252),
                                      *(undefined1 *)(iVar28 + 0x253));
              uVar21 = (uint)*(byte *)(iVar28 + 0x248);
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x254),
                                      *(undefined1 *)(iVar28 + 0x255));
              break;
            case 3:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x25a) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25b);
              uStack_84 = (uint)*(byte *)(iVar28 + 599);
              uVar26 = *(undefined1 *)(iVar28 + 0x259);
              uVar38 = *(undefined1 *)(iVar28 + 600);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x25c),
                                      *(undefined1 *)(iVar28 + 0x25d));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x25e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25f);
              uVar21 = (uint)*(byte *)(iVar28 + 0x256);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x260),
                                      *(undefined1 *)(iVar28 + 0x261));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x262),
                                      *(undefined1 *)(iVar28 + 0x263));
              break;
            case 4:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x268) * 0x100 + (ushort)*(byte *)(iVar28 + 0x269);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x265);
              uVar26 = *(undefined1 *)(iVar28 + 0x267);
              uVar38 = *(undefined1 *)(iVar28 + 0x266);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26a),
                                      *(undefined1 *)(iVar28 + 0x26b));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x26c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x26d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x264);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26e),
                                      *(undefined1 *)(iVar28 + 0x26f));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x270),
                                      *(undefined1 *)(iVar28 + 0x271));
              break;
            default:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x230) * 0x100 + (ushort)*(byte *)(iVar28 + 0x231);
              uVar26 = *(undefined1 *)(iVar28 + 0x22f);
              uVar38 = *(undefined1 *)(iVar28 + 0x22e);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x232),
                                      *(undefined1 *)(iVar28 + 0x233));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x234) * 0x100 + (ushort)*(byte *)(iVar28 + 0x235);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x22d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x22c);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x236),
                                      *(undefined1 *)(iVar28 + 0x237));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x238),
                                      *(undefined1 *)(iVar28 + 0x239));
            }
            iVar28 = (uVar35 - uVar30) * 0x400;
            uVar7 = FUN_43b07560(iVar28,uVar37 - uVar30);
            if (uVar7 < 0x401) {
              uVar9 = FUN_43b07560(iVar28,uVar37 - uVar30);
            }
            else {
              uVar9 = 0x400;
            }
            uVar15 = FUN_43b0af46(uVar38,0,0x1f);
            uVar16 = FUN_43b0af46(uVar26,0,0x1f);
            iVar28 = 0;
            for (; uVar15 < uVar16; uVar15 = uVar15 + 1 & 0xff) {
              iVar28 = iVar28 + (uint)*(byte *)(param_7 + uVar15 + 0x3f0);
            }
            uVar15 = 0;
            for (; uVar16 < 0x20; uVar16 = uVar16 + 1 & 0xff) {
              uVar15 = uVar15 + *(byte *)(param_7 + uVar16 + 0x3f0) & 0xffff;
            }
            iVar13 = *(int *)(iVar31 + DAT_43863de4);
            *(short *)(iVar13 + 0x59e) = (short)iVar28;
            *(short *)(iVar13 + 0x5a0) = (short)uVar15;
            uVar33 = FUN_43b084e8(iVar28 * uVar21 * 0x80,uVar15 + iVar28);
            bVar4 = FUN_43b0af60(uVar33,0,0x80);
            bVar5 = FUN_43b0af60((int)(uStack_84 * (uVar15 + iVar28)) >> 7,0,0x80);
            uVar21 = 0x4000 - (uint)bVar4 * (uint)bVar5;
            uVar21 = uVar21 & ~((int)uVar21 >> 0x1f);
            uVar10 = FUN_43b0aee8(uVar21,0,0x4000,uVar30,sVar8);
            *(byte *)(iVar13 + 0x5a3) = bVar5;
            *(byte *)(iVar13 + 0x5a2) = bVar4;
            *(uint *)(iVar13 + 0x5a8) = uVar21;
            *(short *)(iVar13 + 0x5a4) = (short)((uint)bVar4 * (uint)bVar5);
            uVar30 = FUN_43862554(uVar10,param_9 + 0x286);
            uVar7 = FUN_43b084e8((uVar35 - uVar30) * 0x400,uVar37 - uVar30);
            *(short *)(iVar13 + 0x596) = (short)uVar35;
            *(short *)(iVar13 + 0x598) = (short)uVar37;
            if (0x3ff < uVar7) {
              uVar7 = 0x400;
            }
            *(ushort *)(iVar13 + 0x594) = uVar7;
            uVar21 = FUN_43b0af2c(uVar7,sVar6,uVar9);
            *(short *)(iVar13 + 0x59a) = sVar6;
            *(undefined2 *)(iVar13 + 0x59c) = uVar9;
          }
          else {
            uVar21 = 0x400;
            uVar30 = 0;
          }
          iVar28 = *piVar23;
          if ((*(byte *)(iVar28 + 0x281) & 2) != 0) {
            uVar30 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x284) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x285));
          }
          if ((*(byte *)(iVar28 + 0x281) & 1) != 0) {
            uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x282) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x283));
          }
          iVar28 = *(int *)(iVar31 + DAT_43863de4);
          *(short *)(iVar28 + 0x590) = (short)uVar30;
          *(short *)(iVar28 + 0x592) = (short)uVar21;
          puVar24 = (ushort *)(param_9 + 0x1cb);
          uVar35 = 0;
          do {
            uVar37 = uVar35;
            if (uVar30 < *puVar24) {
              uVar37 = uVar37 & 0xff;
              goto LAB_43863dbc;
            }
            puVar24 = puVar24 + 1;
            uVar35 = uVar37 + 1;
          } while (uVar37 + 1 != 0x1c);
          uVar37 = uVar37 - 0x1b;
LAB_43863dbc:
          puVar24 = (ushort *)(param_9 + uVar37 + 0x1cb);
          while ((int)uVar37 < 0x1c) {
            uVar7 = *puVar24;
            uVar37 = uVar37 + 1;
            uVar35 = (uVar7 - uVar30) * uVar21 + uVar30 * 0x400 >> 10;
            if ((uVar35 & 0xffff) < (uint)uVar7) {
              uVar7 = (ushort)uVar35;
            }
            *puVar24 = uVar7;
            puVar24 = puVar24 + 1;
          }
        }
      }
    }
    FUN_43b0ad9a(param_9);
    FUN_439c5320(param_9 + 0x19b,param_9 + 0x187,0x14);
    FUN_439c5320(param_9 + 0x1a5,param_9 + 0x191,0x14);
  }
  else {
    FUN_4386261c(param_9);
  }
  if ((char)param_9[0x18] != '\0') {
    if (*(char *)((int)param_9 + 0x3f) == '\x01') {
      iVar28 = 0;
      do {
        *(undefined4 *)((int)aiStack_64 + iVar28) = 0x20;
        iVar28 = iVar28 + 4;
      } while (iVar28 != 0x38);
    }
    else {
      if ((byte)(*(char *)((int)param_9 + 0x495) - 0x14U) < 2) {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x340);
        uStack_2b = *(undefined1 *)(iVar28 + 0x341);
        uStack_2a = *(undefined1 *)(iVar28 + 0x342);
        uStack_29 = *(undefined1 *)(iVar28 + 0x343);
        uVar26 = *(undefined1 *)(iVar28 + 0x344);
        uVar38 = *(undefined1 *)(iVar28 + 0x345);
      }
      else {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x33a);
        uStack_2b = *(undefined1 *)(iVar28 + 0x33b);
        uStack_2a = *(undefined1 *)(iVar28 + 0x33c);
        uStack_29 = *(undefined1 *)(iVar28 + 0x33d);
        uVar26 = *(undefined1 *)(iVar28 + 0x33e);
        uVar38 = *(undefined1 *)(iVar28 + 0x33f);
      }
      FUN_43b0af7a(&uStack_2c,uVar26,uVar38,aiStack_64);
    }
    piVar12 = &iStack_68;
    iVar28 = 0;
    psVar14 = param_9;
    do {
      piVar12 = piVar12 + 1;
      iVar31 = FUN_43b075da(*piVar12 << 8,*(undefined4 *)(psVar14 + 0x256),4);
      iVar13 = iVar28 + 1;
      *(int *)(psVar14 + 0x256) = iVar31;
      psVar14 = psVar14 + 2;
      *(char *)((int)param_9 + iVar28 + 0x4e4) = (char)((uint)(iVar31 + 0x80) >> 8);
      iVar28 = iVar13;
    } while (iVar13 != 0xe);
  }
  if ((char)param_9[0x11] != '\0') {
    param_9[0x196] = 0x3400;
    param_9[0x197] = 0x3400;
    param_9[0x198] = 0x3400;
    param_9[0x199] = 0x3400;
    param_9[0x19a] = 0x3400;
    sVar6 = *(short *)(iVar34 + 0x38);
    iVar28 = 0;
    param_9[0x191] = 0;
    param_9[0x192] = 0;
    param_9[0x193] = 0;
    param_9[0x194] = 0;
    param_9[0x195] = 0;
    param_9[0x187] = 0;
    param_9[0x189] = sVar6;
    param_9[0x18a] = sVar6;
    param_9[0x18b] = sVar6;
    param_9[0x18c] = sVar6;
    param_9[0x18d] = sVar6;
    param_9[0x18e] = sVar6;
    param_9[0x188] = sVar6 + -0x80;
    param_9[399] = sVar6 + 0x80;
    param_9[400] = 0x3400;
    psVar14 = param_9;
    do {
      uVar30 = (uint)(ushort)psVar14[0x187];
      uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
      uVar21 = (uint)(ushort)psVar14[0x191];
      uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
      iVar31 = 0;
      psVar22 = param_9 + iVar28 + 0x1ae;
      do {
        iVar31 = iVar31 + 1;
        psVar22[1] = (short)uVar30;
        psVar22[0x1d] = (short)uVar21;
        uVar30 = uVar30 + uVar7 & 0xffff;
        uVar21 = uVar21 + uVar11 & 0xffff;
        psVar22 = psVar22 + 1;
      } while (iVar31 != 3);
      iVar28 = iVar28 + 3;
      psVar14 = psVar14 + 1;
    } while (iVar28 != 0x1b);
    param_9[0x1ca] = 0x3400;
    param_9[0x1e6] = 0x3400;
  }
LAB_43863fe2:
  iVar28 = FUN_43859ab8();
  sVar6 = param_9[6];
  *(char *)(iVar28 + 0x7a) = (char)sVar6;
  if ((char)sVar6 == '\0') {
    *(undefined1 *)(iVar28 + 0x7b) = 0;
    uVar26 = 0xff;
    *(undefined1 *)(iVar28 + 0x7c) = 0xff;
    *(undefined1 *)(iVar28 + 0x7d) = 0xff;
    *(undefined1 *)(iVar28 + 0x7e) = 0xff;
    *(undefined1 *)(iVar28 + 0x7f) = 0xff;
    *(undefined1 *)(iVar28 + 0x80) = 0xff;
    *(undefined1 *)(iVar28 + 0x81) = 0xff;
    *(undefined1 *)(iVar28 + 0x82) = 0xff;
    *(undefined1 *)(iVar28 + 0x83) = 0xff;
    *(undefined1 *)(iVar28 + 0x84) = 0xff;
    *(undefined1 *)(iVar28 + 0x85) = 0xff;
    *(undefined1 *)(iVar28 + 0x86) = 0xff;
    *(undefined1 *)(iVar28 + 0x87) = 0xff;
    *(undefined1 *)(iVar28 + 0x88) = 0xff;
    *(undefined1 *)(iVar28 + 0x89) = 0xff;
    *(undefined1 *)(iVar28 + 0x8a) = 0xff;
    *(undefined1 *)(iVar28 + 0x8b) = 0xff;
    *(undefined1 *)(iVar28 + 0x8c) = 0xff;
    *(undefined1 *)(iVar28 + 0x8d) = 0xff;
    *(undefined1 *)(iVar28 + 0x8e) = 0xff;
    *(undefined1 *)(iVar28 + 0x8f) = 0xff;
    *(undefined1 *)(iVar28 + 0x90) = 0xff;
    *(undefined1 *)(iVar28 + 0x91) = 0xff;
    *(undefined1 *)(iVar28 + 0x92) = 0xff;
    *(undefined1 *)(iVar28 + 0x93) = 0xff;
    *(undefined1 *)(iVar28 + 0x94) = 0xff;
    *(undefined1 *)(iVar28 + 0x95) = 0xff;
    *(undefined1 *)(iVar28 + 0x96) = 0xff;
    *(undefined1 *)(iVar28 + 0x97) = 0xff;
    *(undefined1 *)(iVar28 + 0x98) = 0xff;
    *(undefined1 *)(iVar28 + 0x99) = 0xff;
    *(undefined1 *)(iVar28 + 0x9a) = 0xff;
    *(undefined1 *)(iVar28 + 0x9b) = 0xff;
    *(undefined1 *)(iVar28 + 0x9c) = 0xff;
    *(undefined1 *)(iVar28 + 0x9d) = 0xff;
    *(undefined1 *)(iVar28 + 0x9e) = 0xff;
    *(undefined1 *)(iVar28 + 0x9f) = 0xff;
    *(undefined1 *)(iVar28 + 0xa0) = 0xff;
    *(undefined1 *)(iVar28 + 0xa1) = 0xff;
    *(undefined1 *)(iVar28 + 0xa2) = 0xff;
    *(undefined1 *)(iVar28 + 0xa3) = 0xff;
    *(undefined1 *)(iVar28 + 0xa4) = 0xff;
    *(undefined1 *)(iVar28 + 0xa5) = 0xff;
    *(undefined1 *)(iVar28 + 0xa6) = 0xff;
    *(undefined1 *)(iVar28 + 0xa7) = 0xff;
    *(undefined1 *)(iVar28 + 0xa8) = 0xff;
    *(undefined1 *)(iVar28 + 0xa9) = 0xff;
    *(undefined1 *)(iVar28 + 0xaa) = 0xff;
    *(undefined1 *)(iVar28 + 0xab) = 0xff;
    *(undefined1 *)(iVar28 + 0xac) = 0xff;
    *(undefined1 *)(iVar28 + 0xad) = 0xff;
    *(undefined1 *)(iVar28 + 0xae) = 0xff;
    *(undefined1 *)(iVar28 + 0xaf) = 0xff;
    *(undefined1 *)(iVar28 + 0xb0) = 0xff;
    *(undefined1 *)(iVar28 + 0xb1) = 0xff;
    *(undefined1 *)(iVar28 + 0xb2) = 0xff;
    *(undefined1 *)(iVar28 + 0xb3) = 0xff;
    *(undefined1 *)(iVar28 + 0xb4) = 0xff;
    *(undefined1 *)(iVar28 + 0xb5) = 0xff;
    *(undefined1 *)(iVar28 + 0xb6) = 0xff;
    *(undefined1 *)(iVar28 + 0xb7) = 0xff;
    *(undefined1 *)(iVar28 + 0xb8) = 0xff;
    *(undefined1 *)(iVar28 + 0xb9) = 0xff;
    *(undefined1 *)(iVar28 + 0xba) = 0xff;
    *(undefined1 *)(iVar28 + 0xbb) = 0xff;
    *(undefined1 *)(iVar28 + 0xbc) = 0xff;
    *(undefined1 *)(iVar28 + 0xbd) = 0xff;
    *(undefined1 *)(iVar28 + 0xbe) = 0xff;
    *(undefined1 *)(iVar28 + 0xbf) = 0xff;
    *(undefined1 *)(iVar28 + 0xc0) = 0xff;
    *(undefined1 *)(iVar28 + 0xc1) = 0xff;
    *(undefined1 *)(iVar28 + 0xc2) = 0xff;
    *(undefined1 *)(iVar28 + 0xc3) = 0xff;
    *(undefined1 *)(iVar28 + 0xc4) = 0xff;
    *(undefined1 *)(iVar28 + 0xc5) = 0xff;
    *(undefined1 *)(iVar28 + 0xc6) = 0xff;
    *(undefined1 *)(iVar28 + 199) = 0xff;
    *(undefined1 *)(iVar28 + 200) = 0xff;
    *(undefined1 *)(iVar28 + 0xc9) = 0xff;
    *(undefined1 *)(iVar28 + 0xca) = 0xff;
    *(undefined1 *)(iVar28 + 0xcb) = 0xff;
    *(undefined1 *)(iVar28 + 0xcc) = 0xff;
    *(undefined1 *)(iVar28 + 0xcd) = 0xff;
    *(undefined1 *)(iVar28 + 0xce) = 0xff;
    *(undefined1 *)(iVar28 + 0xcf) = 0xff;
    *(undefined1 *)(iVar28 + 0xd0) = 0xff;
    *(undefined1 *)(iVar28 + 0xd1) = 0xff;
    *(undefined1 *)(iVar28 + 0xd2) = 0xff;
    *(undefined1 *)(iVar28 + 0xd3) = 0xff;
    *(undefined1 *)(iVar28 + 0xd4) = 0xff;
    *(undefined1 *)(iVar28 + 0xd5) = 0xff;
    *(undefined1 *)(iVar28 + 0xd6) = 0xff;
    *(undefined1 *)(iVar28 + 0xd7) = 0xff;
    *(undefined1 *)(iVar28 + 0xd8) = 0xff;
    *(undefined1 *)(iVar28 + 0xd9) = 0xff;
    *(undefined1 *)(iVar28 + 0xda) = 0xff;
    *(undefined1 *)(iVar28 + 0xdb) = 0xff;
    *(undefined1 *)(iVar28 + 0xdc) = 0xff;
    *(undefined1 *)(iVar28 + 0xdd) = 0xff;
    *(undefined1 *)(iVar28 + 0xde) = 0xff;
    *(undefined1 *)(iVar28 + 0xdf) = 0xff;
    *(undefined1 *)(iVar28 + 0xe0) = 0xff;
    *(undefined1 *)(iVar28 + 0xe1) = 0xff;
    *(undefined1 *)(iVar28 + 0xe2) = 0xff;
    *(undefined1 *)(iVar28 + 0xe3) = 0xff;
    *(undefined1 *)(iVar28 + 0xe4) = 0xff;
    *(undefined1 *)(iVar28 + 0xe5) = 0xff;
    *(undefined1 *)(iVar28 + 0xe6) = 0xff;
    *(undefined1 *)(iVar28 + 0xe7) = 0xff;
    *(undefined1 *)(iVar28 + 0xe8) = 0xff;
    *(undefined1 *)(iVar28 + 0xe9) = 0xff;
    *(undefined1 *)(iVar28 + 0xea) = 0xff;
    *(undefined1 *)(iVar28 + 0xeb) = 0xff;
    *(undefined1 *)(iVar28 + 0xec) = 0xff;
    *(undefined1 *)(iVar28 + 0xed) = 0xff;
  }
  else {
    *(undefined1 *)(iVar28 + 0x7b) = *(undefined1 *)((int)param_9 + 0xd);
    *(char *)(iVar28 + 0x7c) = (char)param_9[7];
    *(undefined1 *)(iVar28 + 0x7d) = *(undefined1 *)((int)param_9 + 0x21);
    *(char *)(iVar28 + 0x7e) = (char)param_9[0x11];
    *(char *)(iVar28 + 0x7f) = (char)param_9[0x13];
    *(undefined1 *)(iVar28 + 0x80) = *(undefined1 *)((int)param_9 + 0x27);
    *(char *)(iVar28 + 0x81) = (char)param_9[0x16];
    *(undefined1 *)(iVar28 + 0x82) = *(undefined1 *)((int)param_9 + 0x2d);
    *(char *)(iVar28 + 0x83) = (char)param_9[0x17];
    *(undefined1 *)(iVar28 + 0x84) = *(undefined1 *)((int)param_9 + 0x2f);
    *(char *)(iVar28 + 0x85) = (char)param_9[0x18];
    *(char *)(iVar28 + 0x86) = (char)param_9[0x19];
    *(undefined1 *)(iVar28 + 0x87) = *(undefined1 *)((int)param_9 + 0x33);
    *(char *)(iVar28 + 0x88) = (char)param_9[0x1a];
    *(undefined1 *)(iVar28 + 0x89) = *(undefined1 *)((int)param_9 + 0x35);
    *(char *)(iVar28 + 0x8a) = (char)param_9[0x232];
    *(undefined1 *)(iVar28 + 0x8b) = *(undefined1 *)((int)param_9 + 0x465);
    *(char *)(iVar28 + 0x8c) = (char)param_9[0x15e];
    *(char *)(iVar28 + 0x8d) = (char)param_9[0x164];
    *(undefined1 *)(iVar28 + 0x8e) = *(undefined1 *)((int)param_9 + 0x2c9);
    *(char *)(iVar28 + 0x8f) = (char)param_9[0x165];
    *(undefined1 *)(iVar28 + 0x90) = *(undefined1 *)((int)param_9 + 0x2cb);
    *(char *)(iVar28 + 0x91) = (char)param_9[0x166];
    *(undefined1 *)(iVar28 + 0x92) = *(undefined1 *)((int)param_9 + 0x2cd);
    *(char *)(iVar28 + 0x93) = (char)param_9[0x167];
    *(undefined1 *)(iVar28 + 0x94) = *(undefined1 *)((int)param_9 + 0x2cf);
    *(char *)(iVar28 + 0x95) = (char)param_9[0x168];
    *(undefined1 *)(iVar28 + 0x96) = *(undefined1 *)((int)param_9 + 0x2d1);
    *(char *)(iVar28 + 0x97) = (char)param_9[0x18a];
    *(undefined1 *)(iVar28 + 0x98) = *(undefined1 *)((int)param_9 + 0x315);
    *(char *)(iVar28 + 0x99) = (char)param_9[0x18b];
    *(undefined1 *)(iVar28 + 0x9a) = *(undefined1 *)((int)param_9 + 0x317);
    *(char *)(iVar28 + 0x9b) = (char)param_9[0x18c];
    *(undefined1 *)(iVar28 + 0x9c) = *(undefined1 *)((int)param_9 + 0x319);
    *(char *)(iVar28 + 0x9d) = (char)param_9[0x18d];
    *(undefined1 *)(iVar28 + 0x9e) = *(undefined1 *)((int)param_9 + 0x31b);
    *(char *)(iVar28 + 0x9f) = (char)param_9[0x18e];
    *(undefined1 *)(iVar28 + 0xa0) = *(undefined1 *)((int)param_9 + 0x31d);
    *(char *)(iVar28 + 0xa1) = (char)param_9[0x194];
    *(undefined1 *)(iVar28 + 0xa2) = *(undefined1 *)((int)param_9 + 0x329);
    *(char *)(iVar28 + 0xa3) = (char)param_9[0x195];
    *(undefined1 *)(iVar28 + 0xa4) = *(undefined1 *)((int)param_9 + 0x32b);
    *(char *)(iVar28 + 0xa5) = (char)param_9[0x196];
    *(undefined1 *)(iVar28 + 0xa6) = *(undefined1 *)((int)param_9 + 0x32d);
    *(char *)(iVar28 + 0xa7) = (char)param_9[0x197];
    *(undefined1 *)(iVar28 + 0xa8) = *(undefined1 *)((int)param_9 + 0x32f);
    *(char *)(iVar28 + 0xa9) = (char)param_9[0x198];
    *(undefined1 *)(iVar28 + 0xaa) = *(undefined1 *)((int)param_9 + 0x331);
    *(char *)(iVar28 + 0xab) = (char)param_9[0x188];
    *(undefined1 *)(iVar28 + 0xac) = *(undefined1 *)((int)param_9 + 0x311);
    *(char *)(iVar28 + 0xad) = (char)param_9[399];
    *(undefined1 *)(iVar28 + 0xae) = *(undefined1 *)((int)param_9 + 799);
    *(char *)(iVar28 + 0xaf) = (char)param_9[0x16d];
    *(undefined1 *)(iVar28 + 0xb0) = *(undefined1 *)((int)param_9 + 0x2db);
    *(char *)(iVar28 + 0xb1) = (char)param_9[0x254];
    *(undefined1 *)(iVar28 + 0xb2) = *(undefined1 *)((int)param_9 + 0x4a9);
    *(char *)(iVar28 + 0xb3) = (char)param_9[0x21a];
    *(undefined1 *)(iVar28 + 0xb4) = *(undefined1 *)((int)param_9 + 0x435);
    *(char *)(iVar28 + 0xb5) = (char)param_9[0x16f];
    *(undefined1 *)(iVar28 + 0xb6) = *(undefined1 *)((int)param_9 + 0x2df);
    *(char *)(iVar28 + 0xb7) = (char)param_9[0x171];
    *(undefined1 *)(iVar28 + 0xb8) = *(undefined1 *)((int)param_9 + 0x2e3);
    *(char *)(iVar28 + 0xb9) = (char)param_9[0x172];
    *(undefined1 *)(iVar28 + 0xba) = *(undefined1 *)((int)param_9 + 0x2e5);
    *(undefined1 *)(iVar28 + 0xbb) = *(undefined1 *)((int)param_9 + 0x519);
    *(char *)(iVar28 + 0xbc) = (char)param_9[0x210];
    *(undefined1 *)(iVar28 + 0xbd) = *(undefined1 *)((int)param_9 + 0x421);
    *(char *)(iVar28 + 0xbe) = (char)param_9[0x211];
    *(undefined1 *)(iVar28 + 0xbf) = *(undefined1 *)((int)param_9 + 0x423);
    *(char *)(iVar28 + 0xc0) = (char)param_9[0x212];
    *(undefined1 *)(iVar28 + 0xc1) = *(undefined1 *)((int)param_9 + 0x425);
    *(char *)(iVar28 + 0xc2) = (char)param_9[0x213];
    *(undefined1 *)(iVar28 + 0xc3) = *(undefined1 *)((int)param_9 + 0x427);
    *(char *)(iVar28 + 0xc4) = (char)param_9[0x214];
    *(undefined1 *)(iVar28 + 0xc5) = *(undefined1 *)((int)param_9 + 0x429);
    *(char *)(iVar28 + 0xc6) = (char)param_9[0x215];
    *(undefined1 *)(iVar28 + 199) = *(undefined1 *)((int)param_9 + 0x42b);
    *(char *)(iVar28 + 200) = (char)param_9[0x216];
    *(undefined1 *)(iVar28 + 0xc9) = *(undefined1 *)((int)param_9 + 0x42d);
    *(char *)(iVar28 + 0xca) = (char)param_9[0x217];
    *(undefined1 *)(iVar28 + 0xcb) = *(undefined1 *)((int)param_9 + 0x42f);
    *(char *)(iVar28 + 0xcc) = (char)param_9[0x218];
    *(undefined1 *)(iVar28 + 0xcd) = *(undefined1 *)((int)param_9 + 0x431);
    *(char *)(iVar28 + 0xce) = (char)param_9[0x219];
    *(undefined1 *)(iVar28 + 0xcf) = *(undefined1 *)((int)param_9 + 0x433);
    *(char *)(iVar28 + 0xd0) = (char)param_9[0x174];
    *(undefined1 *)(iVar28 + 0xd1) = *(undefined1 *)((int)param_9 + 0x2e9);
    *(char *)(iVar28 + 0xd2) = (char)param_9[0x175];
    *(undefined1 *)(iVar28 + 0xd3) = *(undefined1 *)((int)param_9 + 0x2eb);
    *(char *)(iVar28 + 0xd4) = (char)param_9[0x176];
    *(undefined1 *)(iVar28 + 0xd5) = *(undefined1 *)((int)param_9 + 0x2ed);
    *(char *)(iVar28 + 0xd6) = (char)param_9[0x177];
    *(undefined1 *)(iVar28 + 0xd7) = *(undefined1 *)((int)param_9 + 0x2ef);
    *(char *)(iVar28 + 0xd8) = (char)param_9[0x178];
    *(undefined1 *)(iVar28 + 0xd9) = *(undefined1 *)((int)param_9 + 0x2f1);
    *(char *)(iVar28 + 0xda) = (char)param_9[0x179];
    *(undefined1 *)(iVar28 + 0xdb) = *(undefined1 *)((int)param_9 + 0x2f3);
    *(char *)(iVar28 + 0xdc) = (char)param_9[0x15a];
    *(undefined1 *)(iVar28 + 0xdd) = *(undefined1 *)((int)param_9 + 0x2b5);
    *(char *)(iVar28 + 0xde) = (char)param_9[0x15b];
    *(undefined1 *)(iVar28 + 0xdf) = *(undefined1 *)((int)param_9 + 0x2b7);
    *(char *)(iVar28 + 0xe0) = (char)param_9[0x15c];
    *(undefined1 *)(iVar28 + 0xe1) = *(undefined1 *)((int)param_9 + 0x2b9);
    *(char *)(iVar28 + 0xe2) = (char)param_9[0x17a];
    *(undefined1 *)(iVar28 + 0xe3) = *(undefined1 *)((int)param_9 + 0x2f5);
    *(char *)(iVar28 + 0xe4) = (char)param_9[0x17b];
    *(undefined1 *)(iVar28 + 0xe5) = *(undefined1 *)((int)param_9 + 0x2f7);
    *(char *)(iVar28 + 0xe6) = (char)param_9[0x17c];
    *(undefined1 *)(iVar28 + 0xe7) = *(undefined1 *)((int)param_9 + 0x2f9);
    *(char *)(iVar28 + 0xe8) = (char)param_9[0x28b];
    *(undefined1 *)(iVar28 + 0xe9) = *(undefined1 *)((int)param_9 + 0x517);
    *(char *)(iVar28 + 0xea) = (char)param_9[0x169];
    *(undefined1 *)(iVar28 + 0xeb) = *(undefined1 *)((int)param_9 + 0x2d3);
    *(char *)(iVar28 + 0xec) = (char)param_9[0x16a];
    *(undefined1 *)(iVar28 + 0xed) = *(undefined1 *)((int)param_9 + 0x2d5);
    uVar26 = 0;
  }
  *(undefined1 *)(iVar28 + 0xee) = uVar26;
  return;
}


/* 43892e0c */

void FUN_43892e0c(undefined1 *param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined1 *puStack_18;
  undefined1 *puStack_14;
  undefined4 uStack_10;
  
  puStack_18 = param_1;
  puStack_14 = param_2;
  uStack_10 = param_3;
  FUN_43b13b50(&puStack_14,&puStack_18);
  if (puStack_14 == (undefined1 *)0x0) {
    puStack_18[0x4c] = param_1[2];
    puStack_18[0x4d] = param_1[3];
    puStack_18[0x4e] = *param_1;
    puStack_18[0x4f] = param_1[1];
    puStack_18[0x50] = param_1[6];
    puStack_18[0x51] = param_1[7];
    puStack_18[0x52] = param_1[4];
    puStack_18[0x53] = param_1[5];
    puStack_18[0x54] = param_1[10];
    puStack_18[0x55] = param_1[0xb];
    puStack_18[0x56] = param_1[8];
    puStack_18[0x57] = param_1[9];
    puStack_18[0x58] = param_1[0xe];
    puStack_18[0x59] = param_1[0xf];
    puStack_18[0x5a] = param_1[0xc];
    puStack_18[0x5b] = param_1[0xd];
    puStack_18[0x5c] = param_1[0x12];
    puStack_18[0x5d] = param_1[0x13];
    puStack_18[0x5e] = param_1[0x10];
    puStack_18[0x5f] = param_1[0x11];
    puStack_18[0x60] = param_1[0x16];
    puStack_18[0x61] = param_1[0x17];
    puStack_18[0x62] = param_1[0x14];
    puStack_18[99] = param_1[0x15];
    puStack_18[100] = param_1[0x1a];
    puStack_18[0x65] = param_1[0x1b];
    puStack_18[0x66] = param_1[0x18];
    puStack_18[0x67] = param_1[0x19];
    puStack_18[0x68] = param_1[0x1e];
    puStack_18[0x69] = param_1[0x1f];
    puStack_18[0x6a] = param_1[0x1c];
    puStack_18[0x6b] = param_1[0x1d];
    puStack_18[0x6c] = param_1[0x22];
    puStack_18[0x6d] = param_1[0x23];
    puStack_18[0x6e] = param_1[0x20];
    puStack_18[0x6f] = param_1[0x21];
    puStack_18[0x70] = param_1[0x26];
    puStack_18[0x71] = param_1[0x27];
    puStack_18[0x72] = param_1[0x24];
    puStack_18[0x73] = param_1[0x25];
    puStack_18[0x74] = param_1[0x28];
    puStack_18[0x75] = param_1[0x29];
    puStack_18[0x76] = param_1[0x2c];
    puStack_18[0x77] = param_1[0x2d];
    puStack_18[0x78] = param_1[0x2a];
    puStack_18[0x79] = param_1[0x2b];
    puStack_18[0x7a] = param_1[0x30];
    puStack_18[0x7b] = param_1[0x31];
    puStack_18[0x7c] = param_1[0x2e];
    puStack_18[0x7d] = param_1[0x2f];
    puStack_18[0x7e] = param_1[0x34];
    puStack_18[0x7f] = param_1[0x35];
    puStack_18[0x80] = param_1[0x32];
    puStack_18[0x81] = param_1[0x33];
    puStack_18[0x82] = param_1[0x38];
    puStack_18[0x83] = param_1[0x39];
    puStack_18[0x84] = param_1[0x36];
    puStack_18[0x85] = param_1[0x37];
    puStack_18[0x86] = param_1[0x3c];
    puStack_18[0x87] = param_1[0x3d];
    puStack_18[0x88] = param_1[0x3a];
    puStack_18[0x89] = param_1[0x3b];
    puStack_18[0x8a] = param_1[0x40];
    puStack_18[0x8b] = param_1[0x41];
    puStack_18[0x8c] = param_1[0x3e];
    puStack_18[0x8d] = param_1[0x3f];
    puStack_18[0x8e] = param_1[0x44];
    puStack_18[0x8f] = param_1[0x45];
    puStack_18[0x90] = param_1[0x42];
    puStack_18[0x91] = param_1[0x43];
    puStack_18[0x92] = param_1[0x48];
    puStack_18[0x93] = param_1[0x49];
    puStack_18[0x94] = param_1[0x46];
    puStack_18[0x95] = param_1[0x47];
    puStack_18[0x96] = param_1[0x4c];
    puStack_18[0x97] = param_1[0x4d];
    puStack_18[0x98] = param_1[0x4a];
    puStack_18[0x99] = param_1[0x4b];
    puStack_18[0x9a] = param_1[0x50];
    puStack_18[0x9b] = param_1[0x51];
    puStack_18[0x9c] = param_1[0x4e];
    puStack_18[0x9d] = param_1[0x4f];
    puStack_18[0x9e] = param_1[0x52];
    puStack_18[0x9f] = param_1[0x53];
    puStack_18[0xa1] = *param_2;
  }
  else {
    FUN_43892794(3,7,1,DAT_438930a0 + 0x43892e2a);
    FUN_43902718(DAT_438930a4 + 0x43892e32);
  }
  return;
}


/* 43a231b0 */

undefined4 *
FUN_43a231b0(undefined4 *param_1,undefined4 param_2,int *param_3,undefined4 param_4,int param_5,
            undefined4 param_6,undefined4 param_7,char param_8,char param_9)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  char cStack_bc;
  undefined1 auStack_b4 [128];
  int *piStack_34;
  undefined4 uStack_30;
  undefined1 uStack_2c;
  char cStack_2b;
  char cStack_2a;
  undefined1 uStack_29;
  
  piVar1 = (int *)FUN_43a22744(param_5 + 0x6c);
  uVar2 = FUN_43a2316c(param_5 + 0x6c);
  if ((char)piVar1[7] == '\0') {
    FUN_43a2d700(piVar1);
    uStack_2c = (**(code **)(*piVar1 + 0x18))(piVar1,0x25);
  }
  else {
    uStack_2c = *(undefined1 *)((int)piVar1 + 0x42);
  }
  cStack_2b = param_8;
  cStack_2a = param_9;
  if (param_9 != '\0') {
    cStack_2b = param_9;
    cStack_2a = param_8;
    uStack_29 = 0;
  }
  FUN_43a2ca64(uVar2,auStack_b4,0x80,&uStack_2c,param_7);
  iVar3 = FUN_439c5b1c(auStack_b4);
  cStack_bc = (char)param_4;
  piStack_34 = param_3;
  uStack_30 = param_4;
  if ((cStack_bc == '\0') &&
     (iVar4 = (**(code **)(*param_3 + 0x30))(param_3,auStack_b4,iVar3), iVar3 != iVar4)) {
    cStack_bc = '\x01';
  }
  *param_1 = piStack_34;
  param_1[1] = uStack_30;
  *param_1 = param_3;
  *(char *)(param_1 + 1) = cStack_bc;
  return param_1;
}


/* 43a3c4a2 */

void FUN_43a3c4a2(undefined2 *param_1)

{
  *param_1 = 0x2004;
  param_1[1] = 0x207;
  param_1[2] = 0xd4;
  param_1[3] = 1;
  *(undefined4 *)(param_1 + 4) = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  *(undefined4 *)(param_1 + 10) = 0;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined1 *)(param_1 + 0xe) = 0;
  *(undefined1 *)((int)param_1 + 0x1d) = 0;
  *(undefined1 *)(param_1 + 0xf) = 0;
  *(undefined1 *)((int)param_1 + 0x1f) = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x16) = 0;
  *(undefined1 *)(param_1 + 0x18) = 0;
  *(undefined1 *)((int)param_1 + 0x31) = 0;
  *(undefined1 *)(param_1 + 0x19) = 0;
  *(undefined1 *)((int)param_1 + 0x33) = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  *(undefined4 *)(param_1 + 0x1e) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0;
  *(undefined1 *)(param_1 + 0x22) = 0;
  *(undefined1 *)((int)param_1 + 0x45) = 0;
  *(undefined1 *)(param_1 + 0x23) = 0;
  *(undefined1 *)((int)param_1 + 0x47) = 0;
  param_1[0x26] = 0;
  param_1[0x27] = 0;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x2a) = 0;
  *(undefined1 *)(param_1 + 0x2c) = 0;
  *(undefined1 *)((int)param_1 + 0x59) = 0;
  *(undefined1 *)(param_1 + 0x2d) = 0;
  *(undefined1 *)((int)param_1 + 0x5b) = 0;
  param_1[0x30] = 0;
  param_1[0x31] = 0;
  *(undefined4 *)(param_1 + 0x32) = 0;
  *(undefined4 *)(param_1 + 0x34) = 0;
  *(undefined1 *)(param_1 + 0x36) = 0;
  *(undefined1 *)((int)param_1 + 0x6d) = 0;
  *(undefined1 *)(param_1 + 0x37) = 0;
  *(undefined1 *)((int)param_1 + 0x6f) = 0;
  param_1[0x3a] = 0;
  param_1[0x3b] = 0;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined4 *)(param_1 + 0x3e) = 0;
  *(undefined1 *)(param_1 + 0x40) = 0;
  *(undefined1 *)((int)param_1 + 0x81) = 0;
  *(undefined1 *)(param_1 + 0x41) = 0;
  *(undefined1 *)((int)param_1 + 0x83) = 0;
  param_1[0x44] = 0;
  param_1[0x45] = 0;
  *(undefined4 *)(param_1 + 0x46) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0;
  *(undefined1 *)(param_1 + 0x4a) = 0;
  *(undefined1 *)((int)param_1 + 0x95) = 0;
  *(undefined1 *)(param_1 + 0x4b) = 0;
  *(undefined1 *)((int)param_1 + 0x97) = 0;
  param_1[0x4e] = 0;
  param_1[0x4f] = 0;
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(undefined4 *)(param_1 + 0x52) = 0;
  *(undefined1 *)(param_1 + 0x54) = 0;
  *(undefined1 *)((int)param_1 + 0xa9) = 0;
  *(undefined1 *)(param_1 + 0x55) = 0;
  *(undefined1 *)((int)param_1 + 0xab) = 0;
  param_1[0x58] = 0;
  param_1[0x59] = 0;
  *(undefined4 *)(param_1 + 0x5a) = 0;
  *(undefined4 *)(param_1 + 0x5c) = 0;
  *(undefined1 *)(param_1 + 0x5e) = 0;
  *(undefined1 *)((int)param_1 + 0xbd) = 0;
  *(undefined1 *)(param_1 + 0x5f) = 0;
  *(undefined1 *)((int)param_1 + 0xbf) = 0;
  param_1[0x62] = 0;
  param_1[99] = 0;
  *(undefined4 *)(param_1 + 100) = 0;
  *(undefined4 *)(param_1 + 0x66) = 0;
  *(undefined1 *)(param_1 + 0x68) = 0;
  *(undefined1 *)((int)param_1 + 0xd1) = 0;
  *(undefined1 *)(param_1 + 0x69) = 0;
  *(undefined1 *)((int)param_1 + 0xd3) = 0;
  return;
}


/* 43ad9322 */

int FUN_43ad9322(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  FUN_43ad9aec();
  FUN_43ad9af8(param_1 + 1);
  FUN_43ad9af0(param_1 + 4);
  FUN_43ad9aee(param_1 + 0xc);
  FUN_43ad9ae4(param_1 + 0xd);
  FUN_43ad9ae6(param_1 + 0x10);
  *(undefined2 *)(param_1 + 100) = 0;
  *(undefined4 *)(param_1 + 0x68) = 1;
  iVar2 = 0;
  iVar3 = param_1;
  do {
    iVar4 = iVar2;
    iVar2 = iVar4 + 1;
    *(undefined1 *)(iVar3 + 0x14) = 0;
    *(undefined1 *)(iVar3 + 0x15) = 0;
    *(undefined1 *)(iVar3 + 0x2c) = 0;
    *(undefined1 *)(iVar3 + 0x2d) = 0;
    iVar3 = iVar3 + 2;
  } while (iVar2 != 0xc);
  *(undefined1 *)(param_1 + 0x6c) = 3;
  *(undefined1 *)(param_1 + 0x7c) = 3;
  *(undefined1 *)(param_1 + 0x93) = 1;
  cVar1 = (char)iVar4 + 'E';
  *(undefined1 *)(param_1 + 0x9d) = 1;
  *(undefined4 *)(param_1 + 0x70) = 0;
  *(undefined4 *)(param_1 + 0x74) = 0;
  *(undefined1 *)(param_1 + 0x78) = 0;
  *(undefined1 *)(param_1 + 0x79) = 0;
  *(undefined4 *)(param_1 + 0x80) = 0;
  *(undefined4 *)(param_1 + 0x84) = 0;
  *(undefined1 *)(param_1 + 0x88) = 0;
  *(undefined1 *)(param_1 + 0x89) = 0;
  *(undefined1 *)(param_1 + 0x8c) = 0;
  *(undefined1 *)(param_1 + 0x8e) = 0;
  *(char *)(param_1 + 0x8f) = cVar1;
  *(undefined1 *)(param_1 + 0x90) = 0;
  *(undefined1 *)(param_1 + 0x91) = 0;
  *(undefined1 *)(param_1 + 0x92) = 0;
  *(undefined1 *)(param_1 + 0x94) = 0;
  *(undefined1 *)(param_1 + 0x95) = 0;
  *(undefined1 *)(param_1 + 0x96) = 0;
  *(undefined1 *)(param_1 + 0x98) = 0;
  *(char *)(param_1 + 0x99) = cVar1;
  *(undefined1 *)(param_1 + 0x9a) = 0;
  *(undefined1 *)(param_1 + 0x9b) = 0;
  *(undefined1 *)(param_1 + 0x9c) = 0;
  *(undefined1 *)(param_1 + 0x9e) = 0;
  *(undefined1 *)(param_1 + 0x9f) = 0;
  *(undefined1 *)(param_1 + 0xa0) = 0;
  iVar2 = param_1;
  iVar3 = 0;
  do {
    iVar4 = iVar3;
    *(undefined1 *)(iVar2 + 0x44) = 1;
    *(char *)(iVar2 + 0x45) = (char)iVar4;
    *(undefined1 *)(iVar2 + 0x54) = 1;
    *(char *)(iVar2 + 0x55) = (char)iVar4;
    iVar2 = iVar2 + 2;
    iVar3 = iVar4 + 1;
  } while (iVar4 + 1 != 8);
  iVar4 = iVar4 + -7;
  *(short *)(param_1 + 0xd4) = (short)iVar4;
  *(int *)(param_1 + 0xd8) = iVar4;
  *(short *)(param_1 + 0xdc) = (short)iVar4;
  *(int *)(param_1 + 0xe0) = iVar4;
  iVar2 = param_1;
  do {
    iVar4 = iVar4 + 1;
    *(undefined1 *)(iVar2 + 0xa1) = 0;
    *(undefined1 *)(iVar2 + 0xa2) = 0;
    *(undefined1 *)(iVar2 + 0xb9) = 0;
    *(undefined1 *)(iVar2 + 0xba) = 0;
    iVar2 = iVar2 + 2;
  } while (iVar4 != 0xc);
  return param_1;
}


/* 43ae53a2 */

void FUN_43ae53a2(byte *param_1)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  undefined2 uVar4;
  short sVar5;
  char *pcVar6;
  short *psVar7;
  bool bVar8;
  
  pcVar6 = (char *)thunk_FUN_4377b420();
  bVar3 = *param_1;
  bVar8 = *pcVar6 != '\0';
  *param_1 = bVar3 & 0xfe | bVar8;
  bVar1 = (pcVar6[1] & 1U) << 1;
  *param_1 = bVar3 & 0xfc | bVar8 | bVar1;
  bVar2 = (pcVar6[2] & 1U) << 2;
  *param_1 = bVar3 & 0xf8 | bVar8 | bVar1 | bVar2;
  *param_1 = bVar8 | bVar1 | bVar2 | (*(int *)(pcVar6 + 4) != 0) << 3;
  param_1[1] = (byte)*(undefined4 *)(pcVar6 + 8);
  param_1[4] = pcVar6[0x14];
  param_1[5] = pcVar6[0x15];
  param_1[6] = pcVar6[0x16];
  param_1[7] = pcVar6[0x17];
  param_1[8] = pcVar6[0x18];
  param_1[9] = pcVar6[0x19];
  param_1[10] = pcVar6[0x1a];
  param_1[0xb] = pcVar6[0x1b];
  param_1[0xc] = pcVar6[0x1c];
  param_1[0xd] = pcVar6[0x1d];
  param_1[0xe] = pcVar6[0x1e];
  param_1[0xf] = pcVar6[0x1f];
  param_1[0x10] = pcVar6[0x20];
  param_1[0x11] = pcVar6[0x21];
  param_1[0x12] = pcVar6[0x22];
  param_1[0x13] = pcVar6[0x23];
  param_1[0x14] = pcVar6[0x24];
  param_1[0x15] = pcVar6[0x25];
  uVar4 = *(undefined2 *)(pcVar6 + 0x28);
  param_1[0x16] = (byte)uVar4;
  param_1[0x17] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x2c);
  param_1[0x18] = (byte)uVar4;
  param_1[0x19] = (byte)((ushort)uVar4 >> 8);
  param_1[0x1a] = pcVar6[0x30];
  param_1[0x1b] = pcVar6[0x31];
  param_1[0x1c] = pcVar6[0x32];
  param_1[0x1d] = pcVar6[0x33];
  param_1[0x1e] = pcVar6[0x34];
  param_1[0x1f] = pcVar6[0x35];
  param_1[0x20] = pcVar6[0x36];
  param_1[0x21] = pcVar6[0x37];
  uVar4 = *(undefined2 *)(pcVar6 + 0x38);
  param_1[0x22] = (byte)uVar4;
  param_1[0x23] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x3c);
  param_1[0x24] = (byte)uVar4;
  param_1[0x25] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x40);
  param_1[0x26] = (byte)uVar4;
  param_1[0x27] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x44);
  param_1[0x28] = (byte)uVar4;
  param_1[0x29] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x48);
  param_1[0x2a] = (byte)uVar4;
  param_1[0x2b] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x4c);
  param_1[0x2c] = (byte)uVar4;
  param_1[0x2d] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x50);
  param_1[0x2e] = (byte)uVar4;
  param_1[0x2f] = (byte)((ushort)uVar4 >> 8);
  param_1[0x30] = pcVar6[0x54];
  param_1[0x31] = 0;
  param_1[0x32] = pcVar6[0x56];
  param_1[0x33] = 0;
  param_1[0x34] = pcVar6[0x58];
  param_1[0x35] = pcVar6[0x59];
  param_1[0x36] = pcVar6[0x5a];
  param_1[0x37] = pcVar6[0x5b];
  param_1[0x38] = pcVar6[0x5c];
  param_1[0x39] = pcVar6[0x5d];
  param_1[0x3a] = pcVar6[0x5e];
  param_1[0x3b] = pcVar6[0x5f];
  param_1[0x3c] = pcVar6[0x6c];
  param_1[0x3d] = pcVar6[0x6d];
  param_1[0x3e] = pcVar6[0x6e];
  param_1[0x3f] = pcVar6[0x6f];
  param_1[0x40] = pcVar6[0x70];
  param_1[0x41] = pcVar6[0x71];
  param_1[0x42] = pcVar6[0x72];
  param_1[0x43] = pcVar6[0x73];
  param_1[0x44] = pcVar6[0x74];
  param_1[0x45] = pcVar6[0x75];
  param_1[0x46] = pcVar6[0x76];
  param_1[0x47] = pcVar6[0x77];
  psVar7 = (short *)thunk_FUN_4377b414();
  sVar5 = *psVar7;
  param_1[0x48] = (byte)sVar5;
  param_1[0x49] = (byte)((ushort)sVar5 >> 8);
                    /* WARNING: Store size is inaccurate */
  *(short *)(param_1 + 0x4a) = sVar5 >> 0xf;
                    /* WARNING: Store size is inaccurate */
  *(short *)(param_1 + 0x4b) = sVar5 >> 0xf;
  param_1[0x4c] = *(byte *)(psVar7 + 2);
  param_1[0x4d] = *(byte *)((int)psVar7 + 5);
  param_1[0x4e] = *(byte *)(psVar7 + 3);
  param_1[0x4f] = *(byte *)((int)psVar7 + 7);
  param_1[0x50] = *(byte *)(psVar7 + 4);
  param_1[0x51] = 0;
  sVar5 = psVar7[6];
  param_1[0x52] = (byte)sVar5;
  param_1[0x53] = (byte)((ushort)sVar5 >> 8);
  param_1[0x54] = *(byte *)(psVar7 + 8);
  param_1[0x55] = *(byte *)((int)psVar7 + 0x11);
  param_1[0x56] = *(byte *)(psVar7 + 9);
  param_1[0x57] = *(byte *)((int)psVar7 + 0x13);
  param_1[0x58] = *(byte *)(psVar7 + 10);
  param_1[0x59] = *(byte *)((int)psVar7 + 0x15);
  param_1[0x5a] = *(byte *)(psVar7 + 0xb);
  param_1[0x5b] = *(byte *)((int)psVar7 + 0x17);
  param_1[0x5c] = *(byte *)(psVar7 + 0xc);
  param_1[0x5d] = *(byte *)((int)psVar7 + 0x19);
  param_1[0x5e] = *(byte *)(psVar7 + 0xd);
  param_1[0x5f] = *(byte *)((int)psVar7 + 0x1b);
  param_1[0x60] = *(byte *)(psVar7 + 0xe);
  param_1[0x61] = *(byte *)((int)psVar7 + 0x1d);
  param_1[0x62] = *(byte *)(psVar7 + 0xf);
  param_1[99] = *(byte *)((int)psVar7 + 0x1f);
  param_1[100] = *(byte *)(psVar7 + 0x10);
  param_1[0x65] = *(byte *)((int)psVar7 + 0x21);
  param_1[0x66] = *(byte *)(psVar7 + 0x11);
  param_1[0x67] = *(byte *)((int)psVar7 + 0x23);
  param_1[0x68] = *(byte *)(psVar7 + 0x12);
  param_1[0x69] = *(byte *)((int)psVar7 + 0x25);
  param_1[0x6a] = *(byte *)(psVar7 + 0x13);
  param_1[0x6b] = *(byte *)((int)psVar7 + 0x27);
  param_1[0x6c] = *(byte *)(psVar7 + 0x14);
  param_1[0x6d] = *(byte *)((int)psVar7 + 0x29);
  param_1[0x6e] = *(byte *)(psVar7 + 0x15);
  param_1[0x6f] = *(byte *)((int)psVar7 + 0x2b);
  param_1[0x70] = *(byte *)(psVar7 + 0x16);
  param_1[0x71] = *(byte *)((int)psVar7 + 0x2d);
  param_1[0x72] = *(byte *)(psVar7 + 0x17);
  param_1[0x73] = *(byte *)((int)psVar7 + 0x2f);
  param_1[0x74] = *(byte *)(psVar7 + 0x18);
  param_1[0x75] = 0;
  param_1[0x76] = *(byte *)((int)psVar7 + 0x31);
  param_1[0x77] = 0;
  sVar5 = psVar7[0x1a];
  param_1[0x78] = (byte)sVar5;
  param_1[0x79] = (byte)((ushort)sVar5 >> 8);
  sVar5 = psVar7[0x1c];
  param_1[0x7a] = (byte)sVar5;
  param_1[0x7b] = (byte)((ushort)sVar5 >> 8);
  param_1[0x7c] = *(byte *)(psVar7 + 0x1e);
  param_1[0x7d] = *(byte *)((int)psVar7 + 0x3d);
  param_1[0x7e] = *(byte *)(psVar7 + 0x1f);
  param_1[0x7f] = *(byte *)((int)psVar7 + 0x3f);
  param_1[0x80] = *(byte *)(psVar7 + 0x20);
  param_1[0x81] = *(byte *)((int)psVar7 + 0x41);
  param_1[0x82] = *(byte *)(psVar7 + 0x21);
  param_1[0x83] = *(byte *)((int)psVar7 + 0x43);
  param_1[0x84] = *(byte *)(psVar7 + 0x22);
  param_1[0x85] = *(byte *)((int)psVar7 + 0x45);
  param_1[0x86] = *(byte *)(psVar7 + 0x23);
  param_1[0x87] = *(byte *)((int)psVar7 + 0x47);
  param_1[0x88] = *(byte *)(psVar7 + 0x24);
  param_1[0x89] = *(byte *)((int)psVar7 + 0x49);
  param_1[0x8a] = *(byte *)(psVar7 + 0x25);
  param_1[0x8b] = *(byte *)((int)psVar7 + 0x4b);
  param_1[0x8c] = *(byte *)(psVar7 + 0x26);
  param_1[0x8d] = *(byte *)((int)psVar7 + 0x4d);
  param_1[0x8e] = *(byte *)(psVar7 + 0x27);
  param_1[0x8f] = *(byte *)((int)psVar7 + 0x4f);
  sVar5 = psVar7[0x28];
  param_1[0x90] = (byte)sVar5;
  param_1[0x91] = (byte)((ushort)sVar5 >> 8);
  param_1[0x92] = *(byte *)(psVar7 + 0x2a);
  param_1[0x93] = *(byte *)((int)psVar7 + 0x55);
  param_1[0x94] = *(byte *)(psVar7 + 0x2c);
  param_1[0x95] = *(byte *)((int)psVar7 + 0x59);
  param_1[0x96] = *(byte *)(psVar7 + 0x2d);
  param_1[0x97] = *(byte *)((int)psVar7 + 0x5b);
  param_1[0x98] = *(byte *)(psVar7 + 0x2e);
  param_1[0x99] = *(byte *)((int)psVar7 + 0x5d);
  param_1[0x9a] = *(byte *)(psVar7 + 0x2f);
  param_1[0x9b] = *(byte *)((int)psVar7 + 0x5f);
  param_1[0x9c] = *(byte *)(psVar7 + 0x30);
  param_1[0x9d] = *(byte *)((int)psVar7 + 0x61);
  param_1[0x9e] = *(byte *)(psVar7 + 0x31);
  param_1[0x9f] = *(byte *)((int)psVar7 + 99);
  param_1[0xa0] = *(byte *)(psVar7 + 0x32);
  param_1[0xa1] = *(byte *)((int)psVar7 + 0x65);
  param_1[0xa2] = *(byte *)(psVar7 + 0x33);
  param_1[0xa3] = *(byte *)((int)psVar7 + 0x67);
  return;
}


/* 43afaa3a */

int FUN_43afaa3a(int param_1,int param_2)

{
  undefined1 uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  FUN_43afa5ea();
  FUN_43afa916(param_1 + 0x20,param_2 + 0x20);
  *(undefined4 *)(param_1 + 0x4ad0) = *(undefined4 *)(param_2 + 0x4ad0);
  *(undefined4 *)(param_1 + 0x4ad4) = *(undefined4 *)(param_2 + 0x4ad4);
  *(undefined4 *)(param_1 + 0x4ad8) = *(undefined4 *)(param_2 + 0x4ad8);
  *(undefined4 *)(param_1 + 0x4adc) = *(undefined4 *)(param_2 + 0x4adc);
  uVar4 = *(undefined4 *)(param_2 + 0x4ae4);
  uVar5 = *(undefined4 *)(param_2 + 0x4ae8);
  *(undefined4 *)(param_1 + 0x4ae0) = *(undefined4 *)(param_2 + 0x4ae0);
  *(undefined4 *)(param_1 + 0x4ae4) = uVar4;
  *(undefined4 *)(param_1 + 0x4ae8) = uVar5;
  FUN_439c5320(param_1 + 0x4aec,param_2 + 0x4aec,0x66);
  uVar4 = *(undefined4 *)(param_2 + 0x4b58);
  uVar5 = *(undefined4 *)(param_2 + 0x4b5c);
  *(undefined4 *)(param_1 + 0x4b54) = *(undefined4 *)(param_2 + 0x4b54);
  uVar6 = *(undefined4 *)(param_2 + 0x4b80);
  *(undefined4 *)(param_1 + 0x4b58) = uVar4;
  *(undefined4 *)(param_1 + 0x4b5c) = uVar5;
  *(undefined4 *)(param_1 + 0x4b60) = *(undefined4 *)(param_2 + 0x4b60);
  *(undefined4 *)(param_1 + 0x4b64) = *(undefined4 *)(param_2 + 0x4b64);
  *(undefined4 *)(param_1 + 0x4b68) = *(undefined4 *)(param_2 + 0x4b68);
  *(undefined4 *)(param_1 + 0x4b6c) = *(undefined4 *)(param_2 + 0x4b6c);
  *(undefined4 *)(param_1 + 0x4b70) = *(undefined4 *)(param_2 + 0x4b70);
  *(undefined4 *)(param_1 + 0x4b74) = *(undefined4 *)(param_2 + 0x4b74);
  *(undefined1 *)(param_1 + 0x4b78) = *(undefined1 *)(param_2 + 0x4b78);
  *(undefined4 *)(param_1 + 0x4b7c) = *(undefined4 *)(param_2 + 0x4b7c);
  *(undefined4 *)(param_1 + 0x4b80) = uVar6;
  *(undefined1 *)(param_1 + 0x4b84) = *(undefined1 *)(param_2 + 0x4b84);
  *(undefined4 *)(param_1 + 0x4b88) = *(undefined4 *)(param_2 + 0x4b88);
  *(undefined1 *)(param_1 + 0x4b8c) = *(undefined1 *)(param_2 + 0x4b8c);
  *(undefined1 *)(param_1 + 0x4b8d) = *(undefined1 *)(param_2 + 0x4b8d);
  *(undefined4 *)(param_1 + 0x4b90) = *(undefined4 *)(param_2 + 0x4b90);
  *(undefined1 *)(param_1 + 0x4b94) = *(undefined1 *)(param_2 + 0x4b94);
  *(undefined1 *)(param_1 + 0x4b95) = *(undefined1 *)(param_2 + 0x4b95);
  *(undefined1 *)(param_1 + 0x4b96) = *(undefined1 *)(param_2 + 0x4b96);
  *(undefined1 *)(param_1 + 0x4b97) = *(undefined1 *)(param_2 + 0x4b97);
  uVar4 = *(undefined4 *)(param_2 + 0x4b9c);
  uVar5 = *(undefined4 *)(param_2 + 0x4ba0);
  uVar6 = *(undefined4 *)(param_2 + 0x4ba4);
  *(undefined4 *)(param_1 + 0x4b98) = *(undefined4 *)(param_2 + 0x4b98);
  *(undefined4 *)(param_1 + 0x4b9c) = uVar4;
  *(undefined4 *)(param_1 + 0x4ba0) = uVar5;
  *(undefined4 *)(param_1 + 0x4ba4) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x4bac);
  *(undefined4 *)(param_1 + 0x4ba8) = *(undefined4 *)(param_2 + 0x4ba8);
  *(undefined4 *)(param_1 + 0x4bac) = uVar4;
  FUN_439c5320(param_1 + 0x4bb0,param_2 + 0x4bb0,0x2a0);
  uVar4 = *(undefined4 *)(param_2 + 0x4e60);
  uVar5 = *(undefined4 *)(param_2 + 0x4e64);
  *(undefined1 *)(param_1 + 0x4e50) = *(undefined1 *)(param_2 + 0x4e50);
  *(undefined4 *)(param_1 + 0x4e54) = *(undefined4 *)(param_2 + 0x4e54);
  *(undefined4 *)(param_1 + 0x4e58) = *(undefined4 *)(param_2 + 0x4e58);
  *(undefined4 *)(param_1 + 0x4e5c) = *(undefined4 *)(param_2 + 0x4e5c);
  *(undefined4 *)(param_1 + 0x4e60) = uVar4;
  *(undefined4 *)(param_1 + 0x4e64) = uVar5;
  uVar4 = *(undefined4 *)(param_2 + 0x4e70);
  uVar5 = *(undefined4 *)(param_2 + 0x4e74);
  *(undefined4 *)(param_1 + 0x4e68) = *(undefined4 *)(param_2 + 0x4e68);
  *(undefined4 *)(param_1 + 0x4e6c) = *(undefined4 *)(param_2 + 0x4e6c);
  *(undefined4 *)(param_1 + 0x4e70) = uVar4;
  *(undefined4 *)(param_1 + 0x4e74) = uVar5;
  uVar4 = *(undefined4 *)(param_2 + 0x4e7c);
  *(undefined4 *)(param_1 + 0x4e78) = *(undefined4 *)(param_2 + 0x4e78);
  *(undefined4 *)(param_1 + 0x4e7c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e84);
  *(undefined4 *)(param_1 + 0x4e80) = *(undefined4 *)(param_2 + 0x4e80);
  *(undefined4 *)(param_1 + 0x4e84) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e8c);
  *(undefined4 *)(param_1 + 0x4e88) = *(undefined4 *)(param_2 + 0x4e88);
  *(undefined4 *)(param_1 + 0x4e8c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e94);
  *(undefined4 *)(param_1 + 0x4e90) = *(undefined4 *)(param_2 + 0x4e90);
  *(undefined4 *)(param_1 + 0x4e94) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e9c);
  *(undefined4 *)(param_1 + 0x4e98) = *(undefined4 *)(param_2 + 0x4e98);
  *(undefined4 *)(param_1 + 0x4e9c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4ea4);
  *(undefined4 *)(param_1 + 0x4ea0) = *(undefined4 *)(param_2 + 0x4ea0);
  *(undefined4 *)(param_1 + 0x4ea4) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4eac);
  uVar5 = *(undefined4 *)(param_2 + 0x4eb0);
  uVar6 = *(undefined4 *)(param_2 + 0x4eb4);
  *(undefined4 *)(param_1 + 0x4ea8) = *(undefined4 *)(param_2 + 0x4ea8);
  *(undefined4 *)(param_1 + 0x4eac) = uVar4;
  *(undefined4 *)(param_1 + 0x4eb0) = uVar5;
  *(undefined4 *)(param_1 + 0x4eb4) = uVar6;
  *(undefined4 *)(param_1 + 0x4eb8) = *(undefined4 *)(param_2 + 0x4eb8);
  uVar2 = *(undefined2 *)(param_2 + 0x4ebc);
  *(undefined2 *)(param_1 + 0x4ebe) = *(undefined2 *)(param_2 + 0x4ebe);
  uVar4 = *(undefined4 *)(param_2 + 0x4ec0);
  *(undefined2 *)(param_1 + 0x4ebc) = uVar2;
  *(undefined4 *)(param_1 + 0x4ec0) = uVar4;
  *(undefined4 *)(param_1 + 0x4ec4) = *(undefined4 *)(param_2 + 0x4ec4);
  *(undefined4 *)(param_1 + 0x4ec8) = *(undefined4 *)(param_2 + 0x4ec8);
  *(undefined4 *)(param_1 + 0x4ecc) = *(undefined4 *)(param_2 + 0x4ecc);
  *(undefined4 *)(param_1 + 0x4ed0) = *(undefined4 *)(param_2 + 0x4ed0);
  *(undefined4 *)(param_1 + 0x4ed4) = *(undefined4 *)(param_2 + 0x4ed4);
  uVar4 = *(undefined4 *)(param_2 + 0x4edc);
  *(undefined4 *)(param_1 + 0x4ed8) = *(undefined4 *)(param_2 + 0x4ed8);
  *(undefined4 *)(param_1 + 0x4edc) = uVar4;
  *(undefined1 *)(param_1 + 0x4ee0) = *(undefined1 *)(param_2 + 0x4ee0);
  *(undefined4 *)(param_1 + 0x4ee4) = *(undefined4 *)(param_2 + 0x4ee4);
  *(undefined1 *)(param_1 + 0x4ee8) = *(undefined1 *)(param_2 + 0x4ee8);
  *(undefined4 *)(param_1 + 0x4eec) = *(undefined4 *)(param_2 + 0x4eec);
  *(undefined1 *)(param_1 + 0x4ef0) = *(undefined1 *)(param_2 + 0x4ef0);
  *(undefined1 *)(param_1 + 0x4ef1) = *(undefined1 *)(param_2 + 0x4ef1);
  *(undefined4 *)(param_1 + 0x4ef4) = *(undefined4 *)(param_2 + 0x4ef4);
  *(undefined1 *)(param_1 + 0x4ef8) = *(undefined1 *)(param_2 + 0x4ef8);
  *(undefined1 *)(param_1 + 0x4ef9) = *(undefined1 *)(param_2 + 0x4ef9);
  FUN_439c5320(param_1 + 0x4efa,param_2 + 0x4efa,0x3c);
  FUN_439c5320(param_1 + 0x4f36,param_2 + 0x4f36,0x88);
  *(undefined4 *)(param_1 + 0x4fc0) = *(undefined4 *)(param_2 + 0x4fc0);
  *(undefined4 *)(param_1 + 0x4fc4) = *(undefined4 *)(param_2 + 0x4fc4);
  *(undefined4 *)(param_1 + 0x4fc8) = *(undefined4 *)(param_2 + 0x4fc8);
  *(undefined1 *)(param_1 + 0x4fcc) = *(undefined1 *)(param_2 + 0x4fcc);
  *(undefined1 *)(param_1 + 0x4fcd) = *(undefined1 *)(param_2 + 0x4fcd);
  *(undefined4 *)(param_1 + 0x4fd0) = *(undefined4 *)(param_2 + 0x4fd0);
  uVar4 = *(undefined4 *)(param_2 + 0x4fd8);
  uVar5 = *(undefined4 *)(param_2 + 0x4fdc);
  uVar6 = *(undefined4 *)(param_2 + 0x4fe0);
  *(undefined4 *)(param_1 + 0x4fd4) = *(undefined4 *)(param_2 + 0x4fd4);
  *(undefined4 *)(param_1 + 0x4fd8) = uVar4;
  *(undefined4 *)(param_1 + 0x4fdc) = uVar5;
  *(undefined4 *)(param_1 + 0x4fe0) = uVar6;
  *(undefined4 *)(param_1 + 0x4fe4) = *(undefined4 *)(param_2 + 0x4fe4);
  *(undefined4 *)(param_1 + 0x4fe8) = *(undefined4 *)(param_2 + 0x4fe8);
  FUN_439c5320(param_1 + 0x4fec,param_2 + 0x4fec,0x6c);
  *(undefined4 *)(param_1 + 0x5058) = *(undefined4 *)(param_2 + 0x5058);
  uVar4 = *(undefined4 *)(param_2 + 0x5060);
  uVar5 = *(undefined4 *)(param_2 + 0x5064);
  uVar6 = *(undefined4 *)(param_2 + 0x5068);
  *(undefined4 *)(param_1 + 0x505c) = *(undefined4 *)(param_2 + 0x505c);
  *(undefined4 *)(param_1 + 0x5060) = uVar4;
  *(undefined4 *)(param_1 + 0x5064) = uVar5;
  *(undefined4 *)(param_1 + 0x5068) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x5070);
  uVar5 = *(undefined4 *)(param_2 + 0x5074);
  uVar6 = *(undefined4 *)(param_2 + 0x5078);
  *(undefined4 *)(param_1 + 0x506c) = *(undefined4 *)(param_2 + 0x506c);
  *(undefined4 *)(param_1 + 0x5070) = uVar4;
  *(undefined4 *)(param_1 + 0x5074) = uVar5;
  *(undefined4 *)(param_1 + 0x5078) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x5080);
  uVar5 = *(undefined4 *)(param_2 + 0x5084);
  uVar6 = *(undefined4 *)(param_2 + 0x5088);
  *(undefined4 *)(param_1 + 0x507c) = *(undefined4 *)(param_2 + 0x507c);
  *(undefined4 *)(param_1 + 0x5080) = uVar4;
  *(undefined4 *)(param_1 + 0x5084) = uVar5;
  *(undefined4 *)(param_1 + 0x5088) = uVar6;
  *(undefined4 *)(param_1 + 0x508c) = *(undefined4 *)(param_2 + 0x508c);
  uVar4 = *(undefined4 *)(param_2 + 0x5094);
  uVar5 = *(undefined4 *)(param_2 + 0x5098);
  uVar6 = *(undefined4 *)(param_2 + 0x509c);
  *(undefined4 *)(param_1 + 0x5090) = *(undefined4 *)(param_2 + 0x5090);
  *(undefined4 *)(param_1 + 0x5094) = uVar4;
  *(undefined4 *)(param_1 + 0x5098) = uVar5;
  *(undefined4 *)(param_1 + 0x509c) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50a4);
  uVar5 = *(undefined4 *)(param_2 + 0x50a8);
  uVar6 = *(undefined4 *)(param_2 + 0x50ac);
  *(undefined4 *)(param_1 + 0x50a0) = *(undefined4 *)(param_2 + 0x50a0);
  *(undefined4 *)(param_1 + 0x50a4) = uVar4;
  *(undefined4 *)(param_1 + 0x50a8) = uVar5;
  *(undefined4 *)(param_1 + 0x50ac) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50b4);
  uVar5 = *(undefined4 *)(param_2 + 0x50b8);
  uVar6 = *(undefined4 *)(param_2 + 0x50bc);
  *(undefined4 *)(param_1 + 0x50b0) = *(undefined4 *)(param_2 + 0x50b0);
  *(undefined4 *)(param_1 + 0x50b4) = uVar4;
  *(undefined4 *)(param_1 + 0x50b8) = uVar5;
  *(undefined4 *)(param_1 + 0x50bc) = uVar6;
  *(undefined4 *)(param_1 + 0x50c0) = *(undefined4 *)(param_2 + 0x50c0);
  uVar4 = *(undefined4 *)(param_2 + 0x50c8);
  uVar5 = *(undefined4 *)(param_2 + 0x50cc);
  uVar6 = *(undefined4 *)(param_2 + 0x50d0);
  *(undefined4 *)(param_1 + 0x50c4) = *(undefined4 *)(param_2 + 0x50c4);
  *(undefined4 *)(param_1 + 0x50c8) = uVar4;
  *(undefined4 *)(param_1 + 0x50cc) = uVar5;
  *(undefined4 *)(param_1 + 0x50d0) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50d8);
  uVar5 = *(undefined4 *)(param_2 + 0x50dc);
  uVar6 = *(undefined4 *)(param_2 + 0x50e0);
  *(undefined4 *)(param_1 + 0x50d4) = *(undefined4 *)(param_2 + 0x50d4);
  *(undefined4 *)(param_1 + 0x50d8) = uVar4;
  *(undefined4 *)(param_1 + 0x50dc) = uVar5;
  *(undefined4 *)(param_1 + 0x50e0) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50e8);
  uVar5 = *(undefined4 *)(param_2 + 0x50ec);
  uVar6 = *(undefined4 *)(param_2 + 0x50f0);
  *(undefined4 *)(param_1 + 0x50e4) = *(undefined4 *)(param_2 + 0x50e4);
  *(undefined4 *)(param_1 + 0x50e8) = uVar4;
  *(undefined4 *)(param_1 + 0x50ec) = uVar5;
  *(undefined4 *)(param_1 + 0x50f0) = uVar6;
  *(undefined4 *)(param_1 + 0x50f4) = *(undefined4 *)(param_2 + 0x50f4);
  uVar4 = *(undefined4 *)(param_2 + 0x50fc);
  uVar5 = *(undefined4 *)(param_2 + 0x5100);
  uVar6 = *(undefined4 *)(param_2 + 0x5104);
  *(undefined4 *)(param_1 + 0x50f8) = *(undefined4 *)(param_2 + 0x50f8);
  *(undefined4 *)(param_1 + 0x50fc) = uVar4;
  *(undefined4 *)(param_1 + 0x5100) = uVar5;
  *(undefined4 *)(param_1 + 0x5104) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x510c);
  uVar5 = *(undefined4 *)(param_2 + 0x5110);
  uVar6 = *(undefined4 *)(param_2 + 0x5114);
  *(undefined4 *)(param_1 + 0x5108) = *(undefined4 *)(param_2 + 0x5108);
  *(undefined4 *)(param_1 + 0x510c) = uVar4;
  *(undefined4 *)(param_1 + 0x5110) = uVar5;
  *(undefined4 *)(param_1 + 0x5114) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x511c);
  uVar5 = *(undefined4 *)(param_2 + 0x5120);
  uVar6 = *(undefined4 *)(param_2 + 0x5124);
  *(undefined4 *)(param_1 + 0x5118) = *(undefined4 *)(param_2 + 0x5118);
  *(undefined4 *)(param_1 + 0x511c) = uVar4;
  *(undefined4 *)(param_1 + 0x5120) = uVar5;
  *(undefined4 *)(param_1 + 0x5124) = uVar6;
  *(undefined4 *)(param_1 + 0x5128) = *(undefined4 *)(param_2 + 0x5128);
  FUN_439c5320(param_1 + 0x512c,param_2 + 0x512c,0x206);
  uVar2 = *(undefined2 *)(param_2 + 0x5334);
  *(undefined2 *)(param_1 + 0x5332) = *(undefined2 *)(param_2 + 0x5332);
  uVar1 = *(undefined1 *)(param_2 + 0x5336);
  *(undefined2 *)(param_1 + 0x5334) = uVar2;
  uVar2 = *(undefined2 *)(param_2 + 0x533e);
  *(undefined1 *)(param_1 + 0x5336) = uVar1;
  uVar4 = *(undefined4 *)(param_2 + 0x5338);
  *(undefined2 *)(param_1 + 0x533e) = uVar2;
  *(undefined4 *)(param_1 + 0x5338) = uVar4;
  *(undefined2 *)(param_1 + 0x533c) = *(undefined2 *)(param_2 + 0x533c);
  *(undefined4 *)(param_1 + 0x5340) = *(undefined4 *)(param_2 + 0x5340);
  *(undefined4 *)(param_1 + 0x5344) = *(undefined4 *)(param_2 + 0x5344);
  *(undefined4 *)(param_1 + 0x5348) = *(undefined4 *)(param_2 + 0x5348);
  *(undefined4 *)(param_1 + 0x534c) = *(undefined4 *)(param_2 + 0x534c);
  FUN_439c5320(param_1 + 0x5350,param_2 + 0x5350,0x102);
  uVar3 = *(undefined2 *)(param_2 + 0x5452);
  uVar2 = *(undefined2 *)(param_2 + 0x5480);
  *(undefined2 *)(param_1 + 0x5454) = *(undefined2 *)(param_2 + 0x5454);
  *(undefined2 *)(param_1 + 0x5452) = uVar3;
  uVar4 = *(undefined4 *)(param_2 + 0x5458);
  uVar5 = *(undefined4 *)(param_2 + 0x545c);
  uVar6 = *(undefined4 *)(param_2 + 0x5460);
  *(undefined1 *)(param_1 + 0x5456) = *(undefined1 *)(param_2 + 0x5456);
  *(undefined4 *)(param_1 + 0x5458) = uVar4;
  *(undefined4 *)(param_1 + 0x545c) = uVar5;
  *(undefined4 *)(param_1 + 0x5460) = uVar6;
  uVar3 = *(undefined2 *)(param_2 + 0x547a);
  *(undefined4 *)(param_1 + 0x5464) = *(undefined4 *)(param_2 + 0x5464);
  uVar4 = *(undefined4 *)(param_2 + 0x5468);
  *(undefined2 *)(param_1 + 0x547a) = uVar3;
  uVar3 = *(undefined2 *)(param_2 + 0x547e);
  *(undefined4 *)(param_1 + 0x5468) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x546c);
  *(undefined2 *)(param_1 + 0x547e) = uVar3;
  *(undefined4 *)(param_1 + 0x546c) = uVar4;
  *(undefined4 *)(param_1 + 0x5470) = *(undefined4 *)(param_2 + 0x5470);
  *(undefined4 *)(param_1 + 0x5474) = *(undefined4 *)(param_2 + 0x5474);
  *(undefined2 *)(param_1 + 0x5478) = *(undefined2 *)(param_2 + 0x5478);
  *(undefined2 *)(param_1 + 0x547c) = *(undefined2 *)(param_2 + 0x547c);
  *(undefined2 *)(param_1 + 0x5480) = uVar2;
  *(undefined2 *)(param_1 + 0x5482) = *(undefined2 *)(param_2 + 0x5482);
  uVar4 = *(undefined4 *)(param_2 + 0x5488);
  uVar5 = *(undefined4 *)(param_2 + 0x548c);
  uVar6 = *(undefined4 *)(param_2 + 0x5490);
  *(undefined4 *)(param_1 + 0x5484) = *(undefined4 *)(param_2 + 0x5484);
  *(undefined4 *)(param_1 + 0x5488) = uVar4;
  *(undefined4 *)(param_1 + 0x548c) = uVar5;
  *(undefined4 *)(param_1 + 0x5490) = uVar6;
  *(undefined4 *)(param_1 + 0x5494) = *(undefined4 *)(param_2 + 0x5494);
  *(undefined4 *)(param_1 + 0x5498) = *(undefined4 *)(param_2 + 0x5498);
  *(undefined4 *)(param_1 + 0x549c) = *(undefined4 *)(param_2 + 0x549c);
  *(undefined4 *)(param_1 + 0x54a0) = *(undefined4 *)(param_2 + 0x54a0);
  *(undefined1 *)(param_1 + 0x54a4) = *(undefined1 *)(param_2 + 0x54a4);
  *(undefined1 *)(param_1 + 0x54a5) = *(undefined1 *)(param_2 + 0x54a5);
  *(undefined4 *)(param_1 + 0x54a8) = *(undefined4 *)(param_2 + 0x54a8);
  *(undefined4 *)(param_1 + 0x54ac) = *(undefined4 *)(param_2 + 0x54ac);
  uVar4 = *(undefined4 *)(param_2 + 0x54b4);
  uVar5 = *(undefined4 *)(param_2 + 0x54b8);
  uVar6 = *(undefined4 *)(param_2 + 0x54bc);
  *(undefined4 *)(param_1 + 0x54b0) = *(undefined4 *)(param_2 + 0x54b0);
  *(undefined4 *)(param_1 + 0x54b4) = uVar4;
  *(undefined4 *)(param_1 + 0x54b8) = uVar5;
  *(undefined4 *)(param_1 + 0x54bc) = uVar6;
  *(undefined4 *)(param_1 + 0x54c0) = *(undefined4 *)(param_2 + 0x54c0);
  uVar4 = *(undefined4 *)(param_2 + 0x54c8);
  uVar5 = *(undefined4 *)(param_2 + 0x54cc);
  *(undefined1 *)(param_1 + 0x54c4) = *(undefined1 *)(param_2 + 0x54c4);
  *(undefined4 *)(param_1 + 0x54c8) = uVar4;
  *(undefined4 *)(param_1 + 0x54cc) = uVar5;
  return param_1;
}


/* 43b0621c */

void FUN_43b0621c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iVar2 = **(int **)(param_1 + 4);
  *(undefined1 *)(iVar2 + 0x5c) = 0;
  *(undefined1 *)(iVar2 + 0x5d) = 0;
  *(undefined1 *)(iVar2 + 0x5e) = *(undefined1 *)(*(int *)(param_1 + 8) + 2);
  uVar1 = *(undefined1 *)(*(int *)(param_1 + 8) + 4);
  *(undefined1 *)(iVar2 + 0x90) = 0;
  *(undefined1 *)(iVar2 + 0x5f) = uVar1;
  uStack_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  FUN_43827800(&uStack_20,param_1);
  *(undefined1 *)(iVar2 + 0x97) = uStack_1c._1_1_;
  *(undefined1 *)(iVar2 + 0x98) = uStack_1c._2_1_;
  *(undefined1 *)(iVar2 + 0x92) = (undefined1)uStack_20;
  *(undefined1 *)(iVar2 + 0x93) = uStack_20._1_1_;
  *(undefined1 *)(iVar2 + 0x94) = uStack_20._2_1_;
  *(undefined1 *)(iVar2 + 0x95) = uStack_20._3_1_;
  *(undefined1 *)(iVar2 + 0x96) = (undefined1)uStack_1c;
  *(undefined1 *)(iVar2 + 0x99) = 0;
  *(undefined1 *)(iVar2 + 0x9a) = 0;
  *(undefined1 *)(iVar2 + 0xae) = 0;
  *(undefined1 *)(iVar2 + 0xb0) = 0;
  *(undefined1 *)(iVar2 + 0xaf) = 0;
  *(undefined2 *)(iVar2 + 200) = 0;
  *(undefined4 *)(iVar2 + 0xc4) = 0;
  *(undefined1 *)(iVar2 + 0x32) = 0;
  *(undefined2 *)(iVar2 + 0x34) = 0x7ff;
  *(undefined2 *)(iVar2 + 0x36) = 0x3ff;
  *(undefined2 *)(iVar2 + 0x38) = 0x7ff;
  return;
}


/* 4385d278 */

void FUN_4385d278(int param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined1 uVar1;
  undefined1 auStack_dc [4];
  uint uStack_d8;
  int iStack_68;
  undefined2 uStack_64;
  undefined2 uStack_62;
  undefined1 uStack_38;
  undefined1 uStack_37;
  undefined1 uStack_36;
  undefined1 uStack_35;
  undefined1 uStack_34;
  undefined1 uStack_33;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined4 uStack_18;
  undefined1 uStack_14;
  
  if (*(char *)(*(int *)(DAT_4385d348 + 0x4385d284 + DAT_4385d34c) + 0x1c) != '\x01') {
    return;
  }
  if (*(char *)(param_1 + 0x8c) == '\x02') {
    if (*(char *)(param_4 + 0x562) != '\0') {
      uVar1 = 0xe;
      goto LAB_4385d2b2;
    }
    if (1 < *(ushort *)(param_2 + 0x68)) {
      uVar1 = 0xd;
      goto LAB_4385d2b2;
    }
  }
  else if (*(char *)(param_4 + 0x562) != '\0') {
    uVar1 = 0xf;
    goto LAB_4385d2b2;
  }
  uVar1 = 8;
LAB_4385d2b2:
  *(undefined1 *)(param_1 + 0x95) = uVar1;
  iStack_68 = (uint)*(ushort *)(param_2 + 0xd8) * *(int *)(param_2 + 0xc);
  uStack_64 = *(undefined2 *)(param_2 + 0x68);
  uStack_36 = *(undefined1 *)(param_1 + 0x132);
  uStack_d8 = (uint)*(byte *)(param_1 + 0x95);
  *(undefined2 *)(param_1 + 0xf8) = uStack_64;
  uStack_33 = *(undefined1 *)(param_1 + 0x135);
  *(int *)(param_1 + 0xf4) = iStack_68;
  *(undefined2 *)(param_1 + 0xfa) = 0;
  *(undefined1 *)(param_1 + 0x133) = 0;
  *(undefined1 *)(param_1 + 0x134) = 0;
  *(undefined1 *)(param_1 + 0x130) = 0;
  *(undefined1 *)(param_1 + 0x131) = 0;
  *(undefined1 *)(param_1 + 0x136) = 0;
  *(undefined1 *)(param_1 + 0x137) = 0;
  uStack_62 = 0;
  uStack_35 = 0;
  uStack_34 = 0;
  uStack_38 = 0;
  uStack_37 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  FUN_438feab4(&uStack_1c,auStack_dc);
  *(undefined1 *)(param_1 + 0xfc) = uStack_1c;
  *(undefined1 *)(param_1 + 0xfd) = uStack_1b;
  *(undefined4 *)(param_1 + 0x100) = uStack_18;
  *(undefined1 *)(param_1 + 0x104) = uStack_14;
  return;
}

