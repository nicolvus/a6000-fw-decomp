/* S41: read-only exports. */

/* 43869cd4 */

void FUN_43869cd4(int param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5)

{
  undefined2 *puVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  undefined2 uVar8;
  int iVar9;
  undefined4 uVar10;
  uint uVar11;
  uint uVar12;
  short sVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  undefined4 *puVar17;
  char cVar18;
  int iVar19;
  int iVar20;
  uint uVar21;
  undefined1 *puVar22;
  int iVar23;
  char cVar24;
  int iVar25;
  uint *puVar26;
  uint uVar27;
  int iVar28;
  uint uStack_4c;
  int iStack_44;
  
  iVar15 = DAT_4386a588 + 0x43869cec;
  FUN_43857f40(0x85,*(undefined4 *)(param_2 + 0x1b8));
  iVar19 = *(int *)(param_2 + 0x90);
  if (((*(int *)(param_1 + 0x20) == 5) ||
      (((iVar9 = FUN_4383fb00(), iVar9 != 0 && (*(int *)(param_1 + 0x20) != 0x18)) &&
       (*(char *)(*(int *)(iVar15 + DAT_4386a58c) + 4) != '\0')))) && (param_5 != 0)) {
    if (*(int *)(param_2 + 0x1b8) == 0) {
      *(undefined2 *)(param_5 + 0xb7c) = *(undefined2 *)(param_1 + 0x16ec);
      iVar9 = 0;
      do {
        iVar20 = iVar9;
        *(undefined4 *)(param_5 + iVar20 + 0xb80) = *(undefined4 *)(param_1 + iVar20 + 0xb04);
        iVar9 = iVar20 + 4;
      } while (iVar20 + 4 != 0x20);
      iVar20 = iVar20 + -0x1c;
      iVar9 = param_1;
      iVar23 = param_5;
      do {
        iVar14 = 0;
        iVar16 = iVar14;
        do {
          iVar28 = iVar9 + iVar16;
          iVar25 = iVar23 + iVar16;
          iVar16 = iVar16 + 0xc;
          *(undefined4 *)(iVar25 + 0xba4) = *(undefined4 *)(iVar28 + 0xe3c);
          iVar28 = param_1 + iVar20 + iVar14;
          iVar25 = param_5 + iVar20 + iVar14;
          iVar14 = iVar14 + 2;
          *(undefined1 *)(iVar25 + 0x1044) = *(undefined1 *)(iVar28 + 0x1468);
        } while (iVar16 != 0x84);
        iVar20 = iVar20 + 0x16;
        iVar9 = iVar9 + 0x84;
        iVar23 = iVar23 + 0x84;
      } while (iVar20 != 0xc6);
      iVar9 = 0;
      do {
        iVar20 = param_1 + iVar9;
        iVar23 = param_5 + iVar9;
        iVar9 = iVar9 + 4;
        *(undefined4 *)(iVar23 + 0x1114) = *(undefined4 *)(iVar20 + 0xa60);
      } while (iVar9 != 0xa0);
      uVar8 = *(undefined2 *)(param_1 + 0x982);
      uVar2 = *(undefined2 *)(param_1 + 0x984);
      uVar3 = *(undefined2 *)(param_1 + 0x986);
      uVar4 = *(undefined2 *)(param_1 + 0x988);
      *(undefined2 *)(param_5 + 0x110a) = *(undefined2 *)(param_1 + 0x980);
      *(undefined2 *)(param_5 + 0x110c) = uVar8;
      *(undefined2 *)(param_5 + 0x110e) = uVar2;
      *(undefined2 *)(param_5 + 0x1110) = uVar3;
      *(undefined2 *)(param_5 + 0x1112) = uVar4;
    }
    else {
      *(undefined2 *)(param_1 + 0x16ec) = *(undefined2 *)(param_5 + 0xb7c);
      iVar9 = 0;
      do {
        iVar20 = iVar9;
        *(undefined4 *)(param_1 + iVar20 + 0xb04) = *(undefined4 *)(param_5 + iVar20 + 0xb80);
        iVar9 = iVar20 + 4;
      } while (iVar20 + 4 != 0x20);
      iVar20 = iVar20 + -0x1c;
      iVar9 = param_5;
      iVar23 = param_1;
      do {
        iVar14 = 0;
        iVar16 = iVar14;
        do {
          iVar28 = iVar9 + iVar16;
          iVar25 = iVar23 + iVar16;
          iVar16 = iVar16 + 0xc;
          *(undefined4 *)(iVar25 + 0xe3c) = *(undefined4 *)(iVar28 + 0xba4);
          iVar28 = param_5 + iVar20 + iVar14;
          iVar25 = param_1 + iVar20 + iVar14;
          iVar14 = iVar14 + 2;
          *(undefined1 *)(iVar25 + 0x1468) = *(undefined1 *)(iVar28 + 0x1044);
        } while (iVar16 != 0x84);
        iVar20 = iVar20 + 0x16;
        iVar9 = iVar9 + 0x84;
        iVar23 = iVar23 + 0x84;
      } while (iVar20 != 0xc6);
      iVar9 = 0;
      do {
        iVar20 = param_5 + iVar9;
        iVar23 = param_1 + iVar9;
        iVar9 = iVar9 + 4;
        *(undefined4 *)(iVar23 + 0xa60) = *(undefined4 *)(iVar20 + 0x1114);
      } while (iVar9 != 0xa0);
      uVar8 = *(undefined2 *)(param_5 + 0x110c);
      uVar2 = *(undefined2 *)(param_5 + 0x110e);
      uVar3 = *(undefined2 *)(param_5 + 0x1110);
      uVar4 = *(undefined2 *)(param_5 + 0x1112);
      *(undefined2 *)(param_1 + 0x980) = *(undefined2 *)(param_5 + 0x110a);
      *(undefined2 *)(param_1 + 0x982) = uVar8;
      *(undefined2 *)(param_1 + 0x984) = uVar2;
      *(undefined2 *)(param_1 + 0x986) = uVar3;
      *(undefined2 *)(param_1 + 0x988) = uVar4;
    }
  }
  iVar23 = param_1 + 4;
  iVar9 = param_1 + 0x96c;
  iVar20 = DAT_4386a590 + 0x43869e7c;
  FUN_43869040(iVar23,iVar9,iVar20);
  FUN_43842c08(iVar23,iVar9,iVar20);
  if (*(char *)(param_1 + 0x2be) == '\0') {
    cVar24 = 0x14e7 < *(ushort *)(param_1 + 0x160);
  }
  else {
    cVar24 = true;
  }
  iVar20 = *(int *)(param_1 + 0x20);
  if (((((iVar20 == 9) || (iVar20 == 1)) ||
       ((iVar20 == 0x1a || ((iVar20 == 5 || (iVar20 == 0x13)))))) || (iVar20 == 0x1f)) ||
     (iVar20 == 0x20)) {
    cVar24 = false;
  }
  else if (iVar20 == 0x18) {
    cVar24 = false;
  }
  if (((iVar20 - 2U < 2) || (iVar20 == 0x17)) && (*(int *)(param_1 + 0x8c) != 1)) {
    cVar24 = false;
  }
  if ((*(int *)(param_1 + 0x8c) == 1) && (*(int *)(param_2 + 0x1b8) == 1)) {
    cVar24 = false;
  }
  if ((*(char *)(param_1 + 0x2be) == '\0') && (*(char *)(param_1 + 0xf2) == '\x01')) {
    cVar24 = false;
  }
  if (*(char *)(param_1 + 0x55) == '\0') {
    cVar24 = false;
  }
  if ((((iVar20 == 8) || (iVar20 == 0x14)) || (iVar20 == 0x1b)) || (iVar20 == 10)) {
    cVar24 = '\x02';
  }
  else if (iVar20 == 0x10) {
    cVar24 = '\x02';
  }
  if ((*(short *)(param_1 + 0x16ec) == 0) || (*(char *)(param_1 + 0xf1) != '\x01')) {
    iVar20 = 0;
    cVar18 = '\0';
  }
  else {
    iVar20 = FUN_43b096ae(param_1 + 0xb04);
    if (*(char *)(param_1 + 0x2be) == '\x01') {
      iVar20 = (uint)*(byte *)(param_1 + 0x72) * iVar20;
      cVar18 = '\x01';
    }
    else {
      cVar18 = '\x01';
    }
  }
  iVar16 = DAT_4386a594;
  *(char *)(param_1 + 0x1940) = cVar18;
  *(int *)(param_1 + 0x1944) = iVar20;
  puVar17 = *(undefined4 **)(iVar15 + iVar16);
  *(char *)((int)puVar17 + 0x1a) = cVar18;
  cVar18 = *(char *)(param_1 + 0x2be);
  uVar8 = *(undefined2 *)(param_1 + 0x16ec);
  *(short *)(puVar17 + 6) = (short)iVar20;
  *(undefined2 *)(puVar17 + 7) = uVar8;
  iVar20 = *(int *)(iVar15 + DAT_4386a598);
  *(undefined2 *)(iVar20 + 700) = 0xffff;
  *(undefined2 *)(iVar20 + 0x2c2) = 0xffff;
  *(undefined2 *)(iVar20 + 0x2be) = 0xffff;
  if (cVar18 == '\x01') {
    uVar10 = FUN_4385c0f4(param_1 + 700,iVar23,iVar9);
    iVar9 = *(int *)(iVar15 + DAT_4386a59c);
    sVar5 = FUN_43902784(uVar10,*(undefined2 *)(iVar9 + 8));
    if (*(char *)(param_1 + 0x1940) == '\x01') {
      uVar11 = FUN_43b096ae(param_1 + 0xb04,*(undefined1 *)(param_1 + 0x2be));
      uVar21 = 0xffff;
      if (uVar11 < 0xffff) {
        uVar21 = uVar11;
      }
      sVar6 = FUN_43902784(uVar21 & 0xffff,*(undefined2 *)(iVar9 + 8));
      sVar7 = sVar5 + *(short *)(iVar9 + 0x14);
      sVar13 = sVar5 + *(short *)(iVar9 + 0x16);
      *(short *)(iVar20 + 0x2be) = (short)uVar21;
      if (sVar7 <= sVar6) {
        sVar7 = sVar6;
      }
      sVar5 = sVar7;
      if (sVar13 <= sVar7) {
        sVar5 = sVar13;
      }
    }
    if ((*(char *)(param_1 + 0x4ce) == '\x01') && (*(char *)(param_1 + 0x4d0) != '\x01')) {
      FUN_438d6d6c(param_1 + 700,uVar10);
    }
    if (*(char *)(*(int *)(iVar15 + DAT_4386a5a0) + 0x5e) == '\x01') {
      FUN_438d4d3c(param_1 + 0xb04);
    }
    *(short *)(iVar20 + 0x2c2) = sVar5;
    *(short *)(iVar20 + 700) = (short)uVar10;
  }
  else {
    iVar23 = 0;
    sVar5 = *(short *)(param_1 + 0x1934);
    iVar9 = iVar20;
    do {
      iVar16 = 0;
      iVar14 = iVar23 * 0x6c + param_1 + 0xb44;
      do {
        iVar25 = iVar9 + iVar16;
        puVar1 = (undefined2 *)(iVar14 + 8);
        iVar16 = iVar16 + 2;
        iVar14 = iVar14 + 0xc;
        *(undefined2 *)(iVar25 + 0x23e) = *puVar1;
      } while (iVar16 != 0x12);
      iVar23 = iVar23 + 1;
      iVar9 = iVar9 + 0x12;
    } while (iVar23 != 7);
    if (*(char *)(*(int *)(iVar15 + DAT_4386a5a0) + 0x5d) == '\x01') {
      FUN_438d4864(param_1 + 0xb04);
    }
    sVar5 = sVar5 - *(short *)(param_1 + 0xee);
  }
  iVar9 = *(int *)(iVar15 + DAT_4386a5a4);
  sVar7 = *(short *)(iVar9 + 0x60);
  sVar13 = *(short *)(iVar9 + 0x62);
  if (*(char *)(param_1 + 0x2be) == '\x01') {
    sVar6 = *(short *)(iVar9 + 100);
    if (*(short *)(iVar9 + 100) == 0) {
      sVar6 = sVar7;
    }
    sVar7 = sVar6;
    if (*(short *)(iVar9 + 0x66) != 0) {
      sVar13 = *(short *)(iVar9 + 0x66);
    }
  }
  uVar8 = FUN_43aeb0d4((int)sVar7,(int)sVar13,(int)sVar5);
  *(short *)((int)puVar17 + 0x16) = sVar5;
  if (cVar24 == '\0') {
    uVar8 = 0;
  }
  else if (cVar24 == '\x02') {
    if (param_5 == 0) {
      uVar8 = 0;
    }
    else if (*(int *)(param_2 + 0x1b8) == 0) {
      *(undefined2 *)(param_5 + 0x4b8) = uVar8;
    }
    else {
      uVar8 = *(undefined2 *)(param_5 + 0x4b8);
    }
  }
  *(char *)((int)puVar17 + 0x1f) = cVar24;
  uVar2 = *(undefined2 *)(param_1 + 0x1936);
  puVar17[1] = *(undefined4 *)(param_1 + 0x1930);
  uVar10 = *(undefined4 *)(param_1 + 0x192c);
  *(undefined2 *)((int)puVar17 + 10) = uVar2;
  uVar2 = *(undefined2 *)(param_1 + 0x1934);
  *puVar17 = uVar10;
  uVar10 = *(undefined4 *)(param_1 + 0xb08);
  *(undefined2 *)(puVar17 + 2) = uVar2;
  *(undefined2 *)(param_1 + 0x1938) = uVar8;
  puVar17[3] = uVar10;
  *(undefined2 *)(puVar17 + 5) = uVar8;
  puVar17[4] = *(undefined4 *)(param_1 + 0x108c);
  *(undefined1 *)((int)puVar17 + 0x1e) = *(undefined1 *)(param_1 + 0xf0);
  puVar17[8] = *(undefined4 *)(param_1 + 0x20);
  puVar17[9] = *(undefined4 *)(param_1 + 0x8c);
  iVar9 = FUN_43b09ccc(param_2);
  if (iVar9 != 0) {
    FUN_439c5320(iVar9 + 0x896,iVar20 + 0x23e,0x12);
    FUN_439c5320(iVar9 + 0x8a8,iVar20 + 0x250,0x12);
    FUN_439c5320(iVar9 + 0x8ba,iVar20 + 0x262,0x12);
    FUN_439c5320(iVar9 + 0x8cc,iVar20 + 0x274,0x12);
    FUN_439c5320(iVar9 + 0x8de,iVar20 + 0x286,0x12);
    FUN_439c5320(iVar9 + 0x8f0,iVar20 + 0x298,0x12);
    FUN_439c5320(iVar9 + 0x902,iVar20 + 0x2aa,0x12);
    *(undefined1 *)(iVar9 + 0x914) = *(undefined1 *)(iVar20 + 700);
    *(undefined1 *)(iVar9 + 0x915) = *(undefined1 *)(iVar20 + 0x2bd);
    *(undefined1 *)(iVar9 + 0x918) = *(undefined1 *)(iVar20 + 0x2c2);
    *(undefined1 *)(iVar9 + 0x919) = *(undefined1 *)(iVar20 + 0x2c3);
    *(undefined1 *)(iVar9 + 0x916) = *(undefined1 *)(iVar20 + 0x2be);
    *(undefined1 *)(iVar9 + 0x917) = *(undefined1 *)(iVar20 + 0x2bf);
    *(undefined1 *)(iVar9 + 0xaab) = *(undefined1 *)(param_1 + 0x1930);
    *(undefined1 *)(iVar9 + 0xaac) = *(undefined1 *)(param_1 + 0x1931);
    *(undefined1 *)(iVar9 + 0xaad) = *(undefined1 *)(param_1 + 0x1932);
    *(undefined1 *)(iVar9 + 0xaae) = *(undefined1 *)(param_1 + 0x1933);
    *(undefined1 *)(iVar9 + 0xaaf) = *(undefined1 *)(param_1 + 0x1936);
    *(undefined1 *)(iVar9 + 0xab0) = *(undefined1 *)(param_1 + 0x1937);
    *(undefined1 *)(iVar9 + 0xab1) = *(undefined1 *)(param_1 + 0x192c);
    *(undefined1 *)(iVar9 + 0xab2) = *(undefined1 *)(param_1 + 0x192d);
    *(undefined1 *)(iVar9 + 0xab3) = *(undefined1 *)(param_1 + 0x192e);
    *(undefined1 *)(iVar9 + 0xab4) = *(undefined1 *)(param_1 + 0x192f);
    *(undefined1 *)(iVar9 + 0xab5) = *(undefined1 *)(param_1 + 0x1934);
    *(undefined1 *)(iVar9 + 0xab6) = *(undefined1 *)(param_1 + 0x1935);
    *(undefined1 *)(iVar9 + 0xab7) = *(undefined1 *)(param_1 + 0xb08);
    *(undefined1 *)(iVar9 + 0xab8) = *(undefined1 *)(param_1 + 0xb09);
    *(undefined1 *)(iVar9 + 0xab9) = *(undefined1 *)(param_1 + 0xb0a);
    *(undefined1 *)(iVar9 + 0xaba) = *(undefined1 *)(param_1 + 0xb0b);
    *(undefined1 *)(iVar9 + 0xabb) = *(undefined1 *)(param_1 + 0x108c);
    *(undefined1 *)(iVar9 + 0xabc) = *(undefined1 *)(param_1 + 0x108d);
    *(undefined1 *)(iVar9 + 0xabd) = *(undefined1 *)(param_1 + 0x108e);
    *(undefined1 *)(iVar9 + 0xabe) = *(undefined1 *)(param_1 + 0x108f);
    *(undefined1 *)(iVar9 + 0xac1) = *(undefined1 *)(param_1 + 0x1938);
    *(undefined1 *)(iVar9 + 0xac2) = *(undefined1 *)(param_1 + 0x1939);
    *(undefined1 *)(iVar9 + 0xac3) = *(undefined1 *)((int)puVar17 + 0x16);
    *(undefined1 *)(iVar9 + 0xac4) = *(undefined1 *)((int)puVar17 + 0x17);
    *(char *)(iVar9 + 0xac0) = cVar24;
    *(undefined1 *)(iVar9 + 0x172) = *(undefined1 *)(param_1 + 0x16ec);
    *(undefined1 *)(iVar9 + 0x173) = *(undefined1 *)(param_1 + 0x16ed);
    *(undefined1 *)(iVar9 + 0x174) = *(undefined1 *)(param_1 + 0xf1);
    *(undefined1 *)(iVar9 + 0x175) = *(undefined1 *)(param_1 + 0x2be);
    *(undefined1 *)(iVar9 + 0x196) = *(undefined1 *)(param_1 + 0x72);
    *(undefined1 *)(iVar9 + 0x197) = *(undefined1 *)(param_1 + 0x1940);
    *(undefined1 *)(iVar9 + 0x198) = *(undefined1 *)(param_1 + 0x1944);
    *(undefined1 *)(iVar9 + 0x199) = *(undefined1 *)(param_1 + 0x1945);
    *(undefined1 *)(iVar9 + 0x19a) = *(undefined1 *)(param_1 + 0x1946);
    *(undefined1 *)(iVar9 + 0x19b) = *(undefined1 *)(param_1 + 0x1947);
    iVar20 = 0;
    do {
      iVar23 = param_1 + iVar20 * 4;
      iVar16 = iVar20 + 0x5c;
      iVar20 = iVar20 + 1;
      iVar16 = iVar9 + iVar16 * 4;
      *(undefined1 *)(iVar16 + 6) = *(undefined1 *)(iVar23 + 0xb04);
      *(undefined1 *)(iVar16 + 7) = *(undefined1 *)(iVar23 + 0xb05);
      *(undefined1 *)(iVar16 + 8) = *(undefined1 *)(iVar23 + 0xb06);
      *(undefined1 *)(iVar16 + 9) = *(undefined1 *)(iVar23 + 0xb07);
    } while (iVar20 != 8);
  }
  iVar9 = *(int *)(param_1 + 0x20);
  if (((((iVar9 != 8) && (iVar9 != 0x1b)) && (iVar9 != 0x14)) && ((iVar9 != 10 && (iVar9 != 0x10))))
     || (*(int *)(param_2 + 0x1b8) == 0)) {
    FUN_438695bc(param_1,param_2);
  }
  if (*(int *)(param_1 + 0x180) != 0) {
    FUN_4382eb98(param_1,param_2,param_5);
  }
  *(undefined4 *)(param_1 + 0x1998) = 0xff;
  if (((*(char *)(*(int *)(iVar15 + DAT_4386a5a8) + 10) != '\0') && (iVar19 == 6)) &&
     (*(int *)(param_2 + 0x4860) == 6)) {
    uVar21 = (uint)*(byte *)(param_2 + 0x11ea) << 3;
    iVar19 = *(int *)(iVar15 + DAT_4386a5ac);
    if (*(int *)(param_2 + 0x484c) == 0) {
      iVar9 = *(int *)(param_2 + 0x4850);
      if ((((iVar9 == 5) || (iVar9 == 2)) || (iVar9 == 1)) || (iVar9 == 3)) {
        uVar11 = (uint)*(byte *)(iVar19 + 0x41);
        uStack_4c = (uint)*(byte *)(iVar19 + 0x40) << 4;
      }
      else if (iVar9 - 7U < 2) {
        uVar11 = (uint)*(byte *)(iVar19 + 0x45);
        uStack_4c = (uint)*(byte *)(iVar19 + 0x44) << 4;
      }
      else {
        uVar11 = (uint)*(byte *)(iVar19 + 0x47);
        uStack_4c = (uint)*(byte *)(iVar19 + 0x46) << 4;
      }
    }
    else {
      uVar11 = (uint)*(byte *)(iVar19 + 0x43);
      uStack_4c = (uint)*(byte *)(iVar19 + 0x42) << 4;
    }
    if (*(int *)(param_2 + 0x1b8) == 0) {
      iVar19 = *(int *)(iVar15 + DAT_4386a5b0);
      puVar22 = (undefined1 *)(iVar19 + 0xb);
      do {
        iVar9 = 0;
        puVar22 = puVar22 + 1;
        *puVar22 = 0;
      } while (puVar22 != (undefined1 *)(iVar19 + 0x17));
      iVar19 = DAT_4386a5b4 + 0x4386a482;
      do {
        iVar20 = 0;
        puVar26 = (uint *)(iVar9 * 0x84 + param_1 + 0xe3c);
        do {
          uVar11 = *puVar26;
          if (uVar11 <= uVar21) {
            *(uint *)(iVar19 + iVar20) = uVar21;
          }
          if (uVar11 > uVar21) {
            *(uint *)(iVar19 + iVar20) = uVar11;
          }
          iVar20 = iVar20 + 4;
          puVar26 = puVar26 + 3;
        } while (iVar20 != 0x2c);
        iVar9 = iVar9 + 1;
        iVar19 = iVar19 + 0x2c;
      } while (iVar9 != 9);
      uVar10 = 0xff;
    }
    else {
      iVar19 = 0;
      iVar9 = 0;
      uVar27 = 0;
      iStack_44 = 0;
      do {
        iVar20 = 0;
        puVar26 = (uint *)(iVar9 * 0x84 + param_1 + 0xe3c);
        puVar17 = (undefined4 *)(DAT_4386a5b8 + 0x4386a524 + iVar19 * 4);
        do {
          uVar12 = uVar21;
          if (uVar21 < *puVar26) {
            uVar12 = *puVar26;
          }
          iVar23 = FUN_43902784(uVar12,*puVar17);
          if (iVar23 < 0) {
            iVar23 = FUN_43902784(uVar12,*puVar17);
            uVar12 = -iVar23;
          }
          else {
            uVar12 = FUN_43902784(uVar12,*puVar17);
          }
          iVar20 = iVar20 + 1;
          if (uVar27 < uVar12) {
            uVar27 = uVar12;
          }
          puVar26 = puVar26 + 3;
          iStack_44 = iStack_44 + uVar12;
          puVar17 = puVar17 + 1;
        } while (iVar20 != 0xb);
        iVar9 = iVar9 + 1;
        iVar19 = iVar19 + 0xb;
      } while (iVar9 != 9);
      uVar21 = FUN_4355faf0(iStack_44,99);
      if (uVar21 < uVar27) {
        uVar27 = uVar27 - uVar21;
      }
      else {
        uVar27 = 0;
      }
      if (uVar27 < uStack_4c) {
        if (uVar27 < uVar11 << 4) {
          uVar10 = 0xff;
        }
        else {
          uVar10 = 1;
        }
      }
      else {
        uVar10 = 0;
      }
    }
    if (*(uint *)(param_2 + 0x1b8) < 0xc) {
      *(char *)(*(int *)(iVar15 + DAT_4386a5b0) + *(uint *)(param_2 + 0x1b8) + 0xc) = (char)uVar10;
    }
    *(undefined4 *)(param_1 + 0x1998) = uVar10;
  }
  FUN_43859944(0x46,param_1,param_2 + 0x1b8);
  return;
}


/* 43869a3c */

void FUN_43869a3c(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined2 uStack_4c;
  undefined2 uStack_4a;
  byte bStack_40;
  
  iVar2 = DAT_43869ac8 + 0x43869a4e;
  iVar3 = *(int *)(iVar2 + DAT_43869acc);
  if (((*(char *)(iVar3 + 0x5c) == '\x01') || (*(char *)(iVar3 + 0x5d) == '\x01')) ||
     (*(char *)(iVar3 + 0x5e) == '\x01')) {
    FUN_43b71890(&uStack_4c);
    if (*(char *)(iVar3 + 0x5c) == '\x01') {
      iVar1 = *(int *)(iVar2 + DAT_43869ad0);
      *(undefined2 *)(iVar1 + 0xf8) = uStack_4c;
      *(undefined2 *)(iVar1 + 0xfa) = uStack_4a;
      *(byte *)(iVar1 + 0xfc) = bStack_40;
      FUN_438d5bf0(param_1);
    }
    if ((*(char *)(iVar3 + 0x5d) == '\x01') || (*(char *)(iVar3 + 0x5e) == '\x01')) {
      iVar2 = *(int *)(iVar2 + DAT_43869ad4);
      *(undefined2 *)(iVar2 + 0x88) = uStack_4c;
      *(undefined2 *)(iVar2 + 0x8a) = uStack_4a;
      *(uint *)(iVar2 + 0x8c) = (uint)bStack_40 << 7;
      FUN_438d48c0(param_1,param_2);
    }
  }
  return;
}


/* 438407a0 */

void FUN_438407a0(int param_1,int param_2,int param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  char *pcVar4;
  int iVar5;
  bool bVar6;
  
  iVar5 = DAT_43840874 + 0x438407b2;
  pcVar4 = *(char **)(iVar5 + DAT_43840878);
  if (*pcVar4 == '\0') {
    if (pcVar4[0x15] == '\0') {
      return;
    }
    bVar6 = false;
  }
  else if (param_3 == 0) {
    bVar6 = false;
  }
  else {
    bVar6 = param_4 != 0;
  }
  FUN_43857f40(0x38a,*(undefined4 *)(param_2 + 0x1b8));
  if (bVar6) {
    uVar3 = FUN_43b09ce6(param_2);
    FUN_43b09cf2(param_4,uVar3);
  }
  *(char *)(param_1 + 0x29e) = (char)*(undefined4 *)(param_1 + 0x314);
  iVar2 = DAT_4384087c;
  if (bVar6) {
    *(undefined1 *)(param_1 + 0x29f) = *(undefined1 *)(param_4 + 0x1f);
    *(ushort *)(iVar2 + 0x43840810) =
         (ushort)*(byte *)(param_4 + 0x19) * 0x100 + (ushort)*(byte *)(param_4 + 0x18);
    *(ushort *)(iVar2 + 0x43840812) =
         (ushort)*(byte *)(param_4 + 0x1b) * 0x100 + (ushort)*(byte *)(param_4 + 0x1a);
    *(ushort *)(iVar2 + 0x43840814) =
         (ushort)*(byte *)(param_4 + 0x1d) * 0x100 + (ushort)*(byte *)(param_4 + 0x1c);
    iVar2 = DAT_43840880;
    bVar1 = *(byte *)(param_4 + 0x17);
    *(byte *)(DAT_43840880 + 0x43840834) = bVar1 & 1;
    *(byte *)(iVar2 + 0x43840835) = (byte)((int)(uint)bVar1 >> 1) & 1;
    *(byte *)(iVar2 + 0x43840836) = (byte)((int)(uint)bVar1 >> 2) & 1;
    *(undefined1 *)(DAT_43840884 + 0x43840850) = *(undefined1 *)(param_4 + 0x1e);
    if (*(char *)(*(int *)(iVar5 + DAT_43840888) + 0x5d) == '\x01') {
      FUN_438d48a8();
    }
  }
  else {
    *(undefined1 *)(param_1 + 0x29f) = 0;
  }
  FUN_43859944(0x17,param_1,param_2 + 0x1b8);
  return;
}


/* 437b0480 */

void FUN_437b0480(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  iVar2 = DAT_437b04ac + 0x437b0492;
  FUN_439c5320(*(undefined4 *)(iVar2 + DAT_437b04b0),param_1,0xc14,DAT_437b04b0,param_4);
  puVar1 = *(undefined4 **)(iVar2 + DAT_437b04b4);
  *puVar1 = *(undefined4 *)(param_1 + 0x28);
  puVar1[1] = *(undefined4 *)(param_1 + 0x2c);
  *(undefined1 *)(puVar1 + 2) = *(undefined1 *)(param_1 + 0x34);
  return;
}


/* 437b3b08 */

void FUN_437b3b08(int param_1,int param_2,undefined4 param_3,undefined1 *param_4,int param_5)

{
  char cVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  iVar9 = DAT_437b3ccc + 0x437b3b1e;
  if (*(int *)(param_2 + 0x1b8) == 0) {
    FUN_437b3a24(param_5);
  }
  FUN_439c5a04(param_1 + 700,0,0x6b0);
  FUN_439c5a04(param_1 + 4,0,0x2b8);
  iVar7 = *(int *)(iVar9 + DAT_437b3cd0);
  *(bool *)(param_1 + 0x18) = *(int *)(iVar7 + 0x504) == 3;
  cVar1 = *(char *)(*(int *)(iVar9 + DAT_437b3cd4) + 0x8c);
  uVar6 = 1;
  if (cVar1 != '\x01') {
    if (cVar1 != '\x02') goto LAB_437b3b7a;
    uVar6 = 0;
  }
  *(undefined1 *)(param_1 + 0x18) = uVar6;
LAB_437b3b7a:
  FUN_43857ecc(0x290,*(undefined1 *)(param_2 + 0x1b8));
  if (*(char *)(*(int *)(iVar9 + DAT_437b3cd8) + 0x23) != '\0') {
    uVar3 = FUN_437b0604();
    *(undefined4 *)(param_1 + 8) = uVar3;
    uVar3 = FUN_437b0610();
    uVar5 = *(undefined4 *)(param_2 + 0x1b8);
    *(undefined4 *)(param_1 + 0xc) = uVar3;
    FUN_438408b8(*(undefined4 *)(param_2 + 0x1c0),uVar5,param_1 + 4,param_5);
    if (param_5 != 0) {
      *(undefined4 *)(param_5 + 0xb6c) = *(undefined4 *)(param_1 + 0xc);
    }
  }
  *param_4 = 0;
  param_4[1] = *(char *)(param_1 + 0x2be) << 4;
  iVar8 = *(int *)(iVar9 + DAT_437b3cdc);
  iVar4 = FUN_4382fe08(*(undefined2 *)(iVar8 + 0x162));
  uVar6 = 0;
  if (iVar4 == 1) {
    param_4[2] = 0;
  }
  else {
    param_4[2] = (char)*(undefined2 *)(iVar8 + 0x162);
    uVar6 = (undefined1)((ushort)*(undefined2 *)(iVar8 + 0x162) >> 8);
  }
  param_4[3] = uVar6;
  param_4[4] = (char)*(undefined2 *)(iVar8 + 0x15e);
  param_4[5] = (char)((ushort)*(undefined2 *)(iVar8 + 0x15e) >> 8);
  param_4[6] = (char)*(undefined2 *)(iVar8 + 0x164);
  uVar2 = *(undefined2 *)(iVar8 + 0x164);
  param_4[8] = 0xa0;
  param_4[10] = 0xa0;
  param_4[7] = (char)((ushort)uVar2 >> 8);
  param_4[9] = 0;
  param_4[0xb] = 0;
  param_4[0xc] = 0;
  param_4[0xd] = 0;
  param_4[0xe] = 0;
  *(undefined4 *)(iVar7 + 0x294) = *(undefined4 *)(param_2 + 0x1c0);
  FUN_43859a78(param_2);
  thunk_FUN_437d0b9c(param_2);
  iVar4 = *(int *)(iVar9 + DAT_437b3ce4);
  if (*(char *)(*(int *)(iVar9 + DAT_437b3ce0) + 0x1c) == '\x01') {
    *(undefined2 *)(param_1 + 0x34e) = *(undefined2 *)(iVar8 + 0x162);
    *(undefined1 *)(param_1 + 5) = *(undefined1 *)(iVar4 + 0xec);
    if (*(char *)(iVar4 + 0xeb) == '\x01') {
      *(undefined1 *)(param_1 + 6) = 1;
    }
    else {
      *(undefined1 *)(param_1 + 6) = 0;
    }
  }
  FUN_4385ca3c(param_1 + 700,iVar7,iVar4,*(undefined4 *)(iVar9 + DAT_437b3ce8),param_1 + 4,param_2);
  if (((*(int *)(iVar7 + 0x4f8) == 0) && (*(int *)(iVar7 + 0x4fc) == 2)) &&
     (iVar9 = FUN_436efe10(), iVar9 == 0)) {
    FUN_43721854();
    uVar3 = FUN_436c2270();
    FUN_43ad3ade(uVar3,1);
  }
  FUN_436ef7a4(0);
  FUN_437b215c(param_1,param_5,param_2);
  *(undefined2 *)(param_1 + 0x2ae) = *(undefined2 *)(iVar8 + 4);
  *(undefined1 *)(param_1 + 0x2b0) = *(undefined1 *)(iVar8 + 0x14);
  *(undefined4 *)(param_1 + 0x2b4) = *(undefined4 *)(iVar7 + 0x448);
  FUN_43859944(1,param_1,param_2 + 0x1b8);
  return;
}


/* 437b43b4 */

void FUN_437b43b4(int param_1,int param_2,undefined2 *param_3,undefined4 *param_4,int param_5)

{
  undefined2 uVar1;
  short sVar2;
  undefined1 uVar3;
  short sVar4;
  short sVar5;
  undefined2 uVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  undefined2 *puVar11;
  uint uVar12;
  int iVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  int iVar16;
  undefined4 uVar17;
  int iVar18;
  undefined4 uVar19;
  char cVar20;
  undefined4 uVar21;
  int iVar22;
  undefined4 *puVar23;
  undefined4 uVar24;
  int iVar25;
  undefined2 *puVar26;
  int iVar27;
  short *psVar28;
  int iVar29;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  
  iVar7 = FUN_437b033c();
  iVar27 = DAT_437b4cf8 + 0x437b43ce;
  if (iVar7 != 0) {
    FUN_43859a78(param_2);
  }
  uVar8 = FUN_43b09ccc(param_2);
  iVar9 = FUN_43b09cd4(param_2);
  iVar13 = param_1 + 700;
  iVar16 = param_1 + 4;
  uVar17 = *(undefined4 *)(param_2 + 0x4a54);
  uVar14 = *(undefined4 *)(param_2 + 0x4a58);
  uVar21 = *(undefined4 *)(param_2 + 0x4a5c);
  iVar18 = param_2 + 0x1b8;
  iVar10 = FUN_437b033c();
  puVar26 = *(undefined2 **)(iVar27 + DAT_437b4cfc);
  if (*(char *)(param_3 + 4) == '\0') {
    FUN_439c5a04(puVar26,0,0x158);
  }
  iVar22 = *(int *)(iVar27 + DAT_437b4d00);
  *(undefined1 *)(iVar22 + 0x1268) = 0;
  psVar28 = *(short **)(iVar27 + DAT_437b4d04);
  if ((iVar10 != 0) || (*psVar28 == 0x30e)) {
    *(undefined1 *)(iVar22 + 0x1268) = 1;
    FUN_439c5a04(iVar13,0,0x6b0);
  }
  uVar6 = *param_3;
  puVar26[1] = param_3[1];
  puVar23 = *(undefined4 **)(param_3 + 2);
  *puVar26 = uVar6;
  uVar15 = puVar23[1];
  uVar19 = puVar23[2];
  uVar24 = puVar23[3];
  *(undefined4 *)(puVar26 + 4) = *puVar23;
  *(undefined4 *)(puVar26 + 6) = uVar15;
  *(undefined4 *)(puVar26 + 8) = uVar19;
  *(undefined4 *)(puVar26 + 10) = uVar24;
  uVar15 = puVar23[5];
  uVar19 = puVar23[6];
  uVar24 = puVar23[7];
  *(undefined4 *)(puVar26 + 0xc) = puVar23[4];
  *(undefined4 *)(puVar26 + 0xe) = uVar15;
  *(undefined4 *)(puVar26 + 0x10) = uVar19;
  *(undefined4 *)(puVar26 + 0x12) = uVar24;
  uVar15 = puVar23[9];
  uVar19 = puVar23[10];
  uVar24 = puVar23[0xb];
  *(undefined4 *)(puVar26 + 0x14) = puVar23[8];
  *(undefined4 *)(puVar26 + 0x16) = uVar15;
  *(undefined4 *)(puVar26 + 0x18) = uVar19;
  *(undefined4 *)(puVar26 + 0x1a) = uVar24;
  FUN_43857ecc(0x291,*(undefined1 *)(param_3 + 1));
  if ((char)psVar28[0x35e] != '\0') {
    FUN_437b2144(0);
    FUN_4376980c();
  }
  iVar22 = FUN_4383fb00(*(undefined4 *)(param_2 + 0x1c0));
  if ((iVar22 != 0) && (*(int *)(param_2 + 0x1b8) == 0)) {
    FUN_4382dbec();
  }
  uVar3 = FUN_4382dcfc(psVar28,*(undefined1 *)(param_1 + 0x2be));
  *(undefined1 *)(psVar28 + 0x1ee) = uVar3;
  *(undefined1 *)(param_1 + 4) = 0;
  puVar11 = (undefined2 *)
            FUN_4384088c(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  if (*(int *)(param_2 + 0x1b8) == 0) {
    FUN_439c5a04(puVar11,0,0x1c);
  }
  iVar22 = FUN_4383fc74(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  iVar29 = *(int *)(iVar27 + DAT_437b4d08);
  if (iVar10 == 0) {
    if ((*(char *)(param_3 + 4) == '\0') && (*(char *)(puVar11 + 3) == '\x01')) {
      uVar6 = *puVar11;
      iVar25 = *(int *)(iVar27 + DAT_437b4d0c);
      *(undefined2 *)(iVar25 + 0x36) = puVar11[2];
      uVar1 = puVar11[1];
      *(undefined2 *)(iVar25 + 0x48) = uVar6;
      *(undefined2 *)(iVar25 + 0x4a) = uVar1;
      FUN_43835788(psVar28,*(undefined4 *)(iVar27 + DAT_437b4d18),
                   *(undefined4 *)(iVar27 + DAT_437b4d1c),*(undefined4 *)(iVar27 + DAT_437b4d20),
                   *(undefined4 *)(iVar27 + DAT_437b4d10),iVar29,
                   *(undefined4 *)(iVar27 + DAT_437b4d14),iVar25,iVar22,param_5);
      *(undefined1 *)(param_1 + 4) = 1;
    }
    if (*(char *)(param_3 + 4) == '\0') {
      FUN_437b4340(param_3[1],psVar28,*(undefined4 *)(iVar27 + DAT_437b4d0c),iVar29,
                   *(undefined4 *)(iVar27 + DAT_437b4d24),*(undefined4 *)(iVar27 + DAT_437b4d28),
                   iVar22,*(undefined4 *)(iVar27 + DAT_437b4d10),
                   *(undefined4 *)(iVar27 + DAT_437b4d18));
    }
  }
  sVar5 = *(short *)(iVar29 + 0x164);
  if (*(char *)(param_3 + 4) == '\0') {
    if (iVar10 == 0) {
      if (*(char *)(param_1 + 0x2be) == '\x01') {
        sVar5 = *(short *)(param_1 + 0x4cc);
      }
    }
    else {
      sVar5 = psVar28[0x8f];
    }
    sVar4 = FUN_4382fefc(*(undefined2 *)(iVar29 + 0x15e));
    sVar5 = sVar5 - sVar4;
  }
  if (*(char *)(param_3 + 4) == '\0') {
    if (iVar10 == 0) {
      uVar6 = *(undefined2 *)(iVar29 + 0x136);
      *(char *)(puVar26 + 0x7a) = (char)*(undefined4 *)(psVar28 + 0x27c);
      uVar15 = FUN_43adae98(uVar6);
      *(undefined4 *)(puVar26 + 0x70) = uVar15;
      uVar15 = FUN_436efe24(*(undefined2 *)(iVar29 + 0x136));
      uVar6 = *(undefined2 *)(iVar29 + 0x162);
      uVar1 = *(undefined2 *)(iVar29 + 0x15e);
      puVar26[0x7d] = *(undefined2 *)(iVar29 + 0x160);
      puVar26[0x7b] = uVar6;
      puVar26[0x7c] = uVar1;
      *(undefined4 *)(puVar26 + 0x72) = uVar15;
      uVar6 = FUN_4385cec4(iVar13,param_3);
      puVar26[0xaa] = uVar6;
    }
    else {
      sVar4 = psVar28[0x8c];
      *(char *)(puVar26 + 0x7a) = (char)*(undefined4 *)(psVar28 + 0x27c);
      uVar15 = FUN_43adae98(sVar4);
      *(undefined4 *)(puVar26 + 0x70) = uVar15;
      uVar15 = FUN_436efe24(psVar28[0x8c]);
      sVar4 = psVar28[0x8c];
      puVar26[0x7b] = psVar28[0x8e];
      sVar2 = psVar28[0x8d];
      puVar26[0x7c] = sVar4;
      puVar26[0xaa] = 0;
      puVar26[0x7d] = sVar2;
      *(undefined4 *)(puVar26 + 0x72) = uVar15;
    }
    uVar15 = FUN_436f0778(*(undefined2 *)(iVar29 + 0x162),*(undefined2 *)(iVar29 + 0x15e));
    *(undefined1 *)(puVar26 + 0x9c) = *(undefined1 *)(param_1 + 0x348);
    puVar23 = *(undefined4 **)(param_3 + 2);
    puVar26[0x7e] = sVar5;
    *(undefined4 *)(puVar26 + 0x9a) = uVar15;
    uVar15 = puVar23[1];
    uVar19 = puVar23[2];
    uVar24 = puVar23[3];
    *(undefined4 *)(puVar26 + 4) = *puVar23;
    *(undefined4 *)(puVar26 + 6) = uVar15;
    *(undefined4 *)(puVar26 + 8) = uVar19;
    *(undefined4 *)(puVar26 + 10) = uVar24;
    uVar15 = puVar23[5];
    uVar19 = puVar23[6];
    uVar24 = puVar23[7];
    *(undefined4 *)(puVar26 + 0xc) = puVar23[4];
    *(undefined4 *)(puVar26 + 0xe) = uVar15;
    *(undefined4 *)(puVar26 + 0x10) = uVar19;
    *(undefined4 *)(puVar26 + 0x12) = uVar24;
    uVar15 = puVar23[9];
    uVar19 = puVar23[10];
    uVar24 = puVar23[0xb];
    *(undefined4 *)(puVar26 + 0x14) = puVar23[8];
    *(undefined4 *)(puVar26 + 0x16) = uVar15;
    *(undefined4 *)(puVar26 + 0x18) = uVar19;
    *(undefined4 *)(puVar26 + 0x1a) = uVar24;
    if (*(char *)(param_1 + 0x18) == '\0') {
      FUN_437b5058(param_3,puVar26,psVar28,iVar18);
    }
    else {
      FUN_4383fa40(puVar26,psVar28);
      sVar4 = FUN_43b08d12(puVar26);
      sVar5 = sVar5 - sVar4;
      *(undefined4 *)(puVar26 + 0x82) = *(undefined4 *)(puVar26 + 0x32);
      iVar25 = *(int *)(param_3 + 2);
      puVar26[0x7e] = sVar5;
      *(int *)(puVar26 + 0x80) = *(int *)(iVar25 + 0xc) + *(int *)(iVar25 + 8);
      uVar15 = FUN_4382fa94(puVar26[0x7b]);
      *(uint *)(puVar26 + 0x74) = (uint)(ushort)puVar26[0x6e] * *(int *)(puVar26 + 6);
      *(undefined4 *)(puVar26 + 0x84) = uVar15;
    }
    FUN_437b061c(1,sVar5,*(undefined4 *)(param_3 + 2),psVar28,&uStack_30,param_2 + 0xd00,
                 param_2 + 0x1108);
    puVar26[0x3a] = uStack_30;
    puVar26[0x3b] = uStack_2e;
    puVar26[0x76] = uStack_2c;
    *(undefined1 *)(puVar26 + 0x3c) = 0;
    puVar26[0x6f] = uStack_2a;
    *(undefined1 *)((int)puVar26 + 0x79) = 1;
  }
  FUN_43857f40(0x292,CONCAT22(puVar26[0x7c],puVar26[0x7d]));
  FUN_43857f40(0x292,CONCAT22(puVar26[0x7b],puVar26[0x7e]));
  if (iVar10 == 0) {
    if (*(char *)(param_3 + 4) == '\0') {
      FUN_4385cf2c(iVar13,psVar28,puVar26,param_3,iVar18,iVar16);
    }
    else {
      FUN_4385d278(iVar13,puVar26,param_3,iVar18);
    }
    if (((*(char *)(param_3 + 4) == '\0') &&
        (*(char *)(*(int *)(iVar27 + DAT_437b4d18) + 0x36) != '\0')) &&
       (*(char *)(*(int *)(iVar27 + DAT_437b4d18) + 0x37) == '\x03')) {
      *(undefined1 *)((int)puVar26 + 0x6d) = 0;
    }
    if (*(char *)(param_3 + 4) == '\0') {
      cVar20 = '\0';
      if (*(int *)(psVar28 + 0x27c) == 0) {
        if (*(int *)(psVar28 + 0x27e) == 2) {
          uVar12 = FUN_436efe10();
          cVar20 = '\x01' - (char)uVar12;
          if (1 < uVar12) {
            cVar20 = '\0';
          }
        }
        else {
          cVar20 = '\0';
        }
      }
      if ((*(int *)(psVar28 + 0x27c) == 0) && (iVar25 = FUN_43b077f2(psVar28), iVar25 != 0)) {
        FUN_436ef634(1);
        FUN_43724398();
        cVar20 = '\x01';
      }
    }
    else {
      cVar20 = '\0';
    }
  }
  else {
    cVar20 = '\0';
    *(undefined4 *)(puVar26 + 0x9e) = 0;
    *(undefined4 *)(puVar26 + 0xa0) = 0;
    *(undefined4 *)(puVar26 + 0xa2) = 0;
    *(undefined4 *)(param_1 + 0x4fc) = 0;
    *(undefined4 *)(param_1 + 0x500) = 0;
  }
  if (param_4 != (undefined4 *)0x0) {
    *(char *)(param_4 + 1) = cVar20;
  }
  if ((iVar10 == 0) && (param_4 != (undefined4 *)0x0)) {
    param_4 = (undefined4 *)*param_4;
    uVar15 = *(undefined4 *)(puVar26 + 0x34);
    uVar19 = *(undefined4 *)(puVar26 + 0x36);
    uVar24 = *(undefined4 *)(puVar26 + 0x38);
    *param_4 = *(undefined4 *)(puVar26 + 0x32);
    param_4[1] = uVar15;
    param_4[2] = uVar19;
    param_4[3] = uVar24;
  }
  if ((*(int *)(psVar28 + 0x15a) == 0x1a) && (*(int *)(psVar28 + 0x15e) == 4)) {
    psVar28[0x15a] = 0x21;
    psVar28[0x15b] = 0;
  }
  if (*(char *)(param_3 + 4) == '\0') {
    FUN_437b0810(psVar28,iVar29,*(undefined4 *)(iVar27 + DAT_437b4d0c),
                 *(undefined4 *)(iVar27 + DAT_437b4d20),*(undefined4 *)(iVar27 + DAT_437b4d2c),
                 *(undefined4 *)(iVar27 + DAT_437b4d1c),*(undefined4 *)(iVar27 + DAT_437b4d18),
                 *(undefined4 *)(iVar27 + DAT_437b4d14),*(undefined4 *)(iVar27 + DAT_437b4d10),
                 *(undefined4 *)(iVar27 + DAT_437b4d30),*(undefined4 *)(iVar27 + DAT_437b4d34),
                 iVar16,iVar13,puVar26,iVar10);
  }
  if (*(char *)(param_3 + 4) == '\0') {
    uVar15 = *(undefined4 *)(iVar27 + DAT_437b4d0c);
    if (*(char *)(*(int *)(iVar27 + DAT_437b4d38) + 0x23) != '\0') {
      FUN_4383fbf0(psVar28,uVar15,iVar16);
    }
    FUN_437b3cec(psVar28,iVar29,uVar15,iVar16,iVar13,puVar26,iVar10,uVar17,iVar18);
    FUN_437b1048(psVar28,iVar29,*(undefined4 *)(iVar27 + DAT_437b4d20),
                 *(undefined4 *)(iVar27 + DAT_437b4d2c),*(undefined4 *)(iVar27 + DAT_437b4d10),
                 iVar16,iVar13,puVar26,iVar10,uVar14,uVar21,uVar8);
  }
  if ((((iVar10 == 0) && (*(char *)(param_3 + 4) == '\0')) &&
      (FUN_4384a554(psVar28,iVar29), *(char *)(puVar11 + 3) == '\x01')) &&
     (*(char *)(param_1 + 0x143) == '\0')) {
    FUN_437b5aa8(*(undefined4 *)(iVar27 + DAT_437b4d0c),iVar29);
    FUN_43857f40(0x38c,*(undefined4 *)(param_2 + 0x1b8));
  }
  if (*(char *)(param_3 + 4) == '\0') {
    if ((*(char *)(*(int *)(iVar27 + DAT_437b4d38) + 0x23) != '\0') &&
       (FUN_43b08d80(iVar29,iVar9), iVar9 != 0)) {
      *(undefined1 *)(iVar9 + 0x198) = *(undefined1 *)(puVar11 + 4);
      *(undefined1 *)(iVar9 + 0x199) = *(undefined1 *)((int)puVar11 + 9);
      *(undefined1 *)(iVar9 + 0x19a) = *(undefined1 *)(puVar11 + 5);
      *(undefined1 *)(iVar9 + 0x19b) = *(undefined1 *)((int)puVar11 + 0xb);
      *(undefined1 *)(iVar9 + 0x19c) = *(undefined1 *)(puVar11 + 6);
      *(undefined1 *)(iVar9 + 0x19d) = *(undefined1 *)((int)puVar11 + 0xd);
      *(undefined1 *)(iVar9 + 0x19e) = *(undefined1 *)(puVar11 + 7);
      *(undefined1 *)(iVar9 + 0x19f) = *(undefined1 *)((int)puVar11 + 0xf);
      *(undefined1 *)(iVar9 + 0x1a1) = *(undefined1 *)(param_1 + 4);
      FUN_4382dbfc(iVar9 + 0x1a0);
      if (*(char *)(param_1 + 4) != '\0') {
        *(undefined1 *)(iVar9 + 0x1a2) = *(undefined1 *)(puVar11 + 8);
        *(undefined1 *)(iVar9 + 0x1a3) = *(undefined1 *)(puVar11 + 10);
        *(undefined1 *)(iVar9 + 0x1a4) = *(undefined1 *)((int)puVar11 + 0x15);
        *(undefined1 *)(iVar9 + 0x1a5) = *(undefined1 *)(puVar11 + 0xb);
        *(undefined1 *)(iVar9 + 0x1a6) = *(undefined1 *)((int)puVar11 + 0x17);
        *(undefined1 *)(iVar9 + 0x1a7) = *(undefined1 *)(puVar11 + 0xc);
        *(undefined1 *)(iVar9 + 0x1a8) = *(undefined1 *)((int)puVar11 + 0x19);
        *(undefined1 *)(iVar9 + 0x1a9) = *(undefined1 *)(puVar11 + 0xd);
        *(undefined1 *)(iVar9 + 0x1aa) = *(undefined1 *)((int)puVar11 + 0x1b);
        *(undefined1 *)(iVar9 + 0x1ab) = *(undefined1 *)(puVar11 + 1);
        *(undefined1 *)(iVar9 + 0x1ac) = *(undefined1 *)((int)puVar11 + 3);
        *(undefined1 *)(iVar9 + 0x1ad) = *(undefined1 *)puVar11;
        *(undefined1 *)(iVar9 + 0x1ae) = *(undefined1 *)((int)puVar11 + 1);
        iVar27 = *(int *)(iVar27 + DAT_437b4d0c);
        *(undefined1 *)(iVar9 + 0x1b1) = *(undefined1 *)(iVar27 + 0x48);
        *(undefined1 *)(iVar9 + 0x1b2) = *(undefined1 *)(iVar27 + 0x49);
        *(undefined1 *)(iVar9 + 0x1af) = *(undefined1 *)(iVar27 + 0x4a);
        *(undefined1 *)(iVar9 + 0x1b0) = *(undefined1 *)(iVar27 + 0x4b);
        *(undefined1 *)(iVar9 + 0x1b3) = *(undefined1 *)(iVar27 + 0x36);
        *(undefined1 *)(iVar9 + 0x1b4) = *(undefined1 *)(iVar27 + 0x37);
        *(undefined1 *)(iVar9 + 0x1b5) = *(undefined1 *)(iVar27 + 0x11e);
        *(undefined1 *)(iVar9 + 0x1b6) = *(undefined1 *)(iVar27 + 0x11f);
        *(undefined1 *)(iVar9 + 0x1b7) = *(undefined1 *)(iVar27 + 0x50);
        *(undefined1 *)(iVar9 + 0x1b8) = *(undefined1 *)(iVar27 + 0x51);
        *(undefined1 *)(iVar9 + 0x1b9) = *(undefined1 *)(iVar27 + 0x1d0);
        *(undefined1 *)(iVar9 + 0x1ba) = *(undefined1 *)(iVar27 + 0x1d1);
        *(undefined1 *)(iVar9 + 0x1bb) = *(undefined1 *)(iVar27 + 0x1d2);
        *(undefined1 *)(iVar9 + 0x1bc) = *(undefined1 *)(iVar27 + 0x1d3);
        *(undefined1 *)(iVar9 + 0x1bd) = *(undefined1 *)(iVar27 + 0x1d4);
        *(undefined1 *)(iVar9 + 0x1be) = *(undefined1 *)(iVar27 + 0x1d5);
        *(undefined1 *)(iVar9 + 0x1bf) = *(undefined1 *)(iVar27 + 0x1d8);
        *(undefined1 *)(iVar9 + 0x1c0) = *(undefined1 *)(iVar27 + 0x1d9);
        *(undefined1 *)(iVar9 + 0x1c1) = *(undefined1 *)(iVar27 + 0x1da);
        *(undefined1 *)(iVar9 + 0x1c2) = *(undefined1 *)(iVar27 + 0x1db);
        *(undefined1 *)(iVar9 + 0x1c3) = *(undefined1 *)(iVar27 + 0x1dc);
        *(undefined1 *)(iVar9 + 0x1c4) = *(undefined1 *)(iVar27 + 0x1dd);
        *(undefined1 *)(iVar9 + 0x1c5) = *(undefined1 *)(iVar27 + 0x1de);
        *(undefined1 *)(iVar9 + 0x1c6) = *(undefined1 *)(iVar27 + 0x1df);
        *(undefined1 *)(iVar9 + 0x262) = *(undefined1 *)(iVar27 + 0x1e0);
        *(undefined1 *)(iVar9 + 0x263) = *(undefined1 *)(iVar27 + 0x1e1);
        *(undefined1 *)(iVar9 + 0x1c7) = *(undefined1 *)(iVar27 + 0x1e2);
        *(undefined1 *)(iVar9 + 0x1c8) = *(undefined1 *)(iVar27 + 0x1e3);
        *(undefined1 *)(iVar9 + 0x1c9) = *(undefined1 *)(iVar27 + 0x120);
        *(undefined1 *)(iVar9 + 0x1ca) = *(undefined1 *)(iVar27 + 0x121);
        *(undefined1 *)(iVar9 + 0x1cb) = *(undefined1 *)(iVar27 + 0x124);
        *(undefined1 *)(iVar9 + 0x1cc) = *(undefined1 *)(iVar27 + 0x125);
        if (param_5 == 0) {
          uVar3 = 0xff;
          *(undefined1 *)(iVar9 + 0x1cd) = 0xff;
          *(undefined1 *)(iVar9 + 0x1ce) = 0xff;
        }
        else {
          *(undefined1 *)(iVar9 + 0x1cd) = *(undefined1 *)(param_5 + 0xb72);
          *(undefined1 *)(iVar9 + 0x1ce) = *(undefined1 *)(param_5 + 0xb73);
          uVar3 = *(undefined1 *)(param_5 + 0xb70);
        }
        *(undefined1 *)(iVar9 + 0x1cf) = uVar3;
        *(undefined1 *)(iVar9 + 0x1d0) = *(undefined1 *)(iVar22 + 1);
        *(undefined1 *)(iVar9 + 0x1d1) = *(undefined1 *)(iVar22 + 4);
        *(undefined1 *)(iVar9 + 0x1d2) = *(undefined1 *)(iVar22 + 5);
        *(undefined1 *)(iVar9 + 0x1d3) = *(undefined1 *)(iVar22 + 6);
        *(undefined1 *)(iVar9 + 0x1d4) = *(undefined1 *)(iVar22 + 7);
        *(undefined1 *)(iVar9 + 0x1d5) = *(undefined1 *)(iVar22 + 0x2e);
        *(undefined1 *)(iVar9 + 0x1d6) = *(undefined1 *)(iVar22 + 0x2f);
        *(undefined1 *)(iVar9 + 0x1d7) = *(undefined1 *)(iVar22 + 0xc);
        *(undefined1 *)(iVar9 + 0x1d8) = *(undefined1 *)(iVar22 + 0xd);
        *(undefined1 *)(iVar9 + 0x1d9) = *(undefined1 *)(iVar22 + 0x30);
        *(undefined1 *)(iVar9 + 0x1da) = *(undefined1 *)(iVar22 + 0x31);
        *(undefined1 *)(iVar9 + 0x1db) = *(undefined1 *)(iVar22 + 0xe);
        *(undefined1 *)(iVar9 + 0x1dc) = *(undefined1 *)(iVar22 + 0xf);
        *(undefined1 *)(iVar9 + 0x1dd) = *(undefined1 *)(iVar22 + 0x32);
        *(undefined1 *)(iVar9 + 0x1de) = *(undefined1 *)(iVar22 + 0x33);
        *(undefined1 *)(iVar9 + 0x1df) = *(undefined1 *)(iVar22 + 0x12);
        *(undefined1 *)(iVar9 + 0x1e0) = *(undefined1 *)(iVar22 + 0x13);
        *(undefined1 *)(iVar9 + 0x1e1) = *(undefined1 *)(iVar27 + 0x204);
        *(undefined1 *)(iVar9 + 0x1e2) = *(undefined1 *)(iVar27 + 0x205);
        *(undefined1 *)(iVar9 + 0x1e3) = *(undefined1 *)(iVar27 + 0x206);
        *(undefined1 *)(iVar9 + 0x1e4) = *(undefined1 *)(iVar27 + 0x207);
        *(undefined1 *)(iVar9 + 0x1e5) = *(undefined1 *)(iVar27 + 0x208);
        *(undefined1 *)(iVar9 + 0x1e6) = *(undefined1 *)(iVar27 + 0x209);
        *(undefined1 *)(iVar9 + 0x1e7) = *(undefined1 *)(iVar27 + 0x130);
        *(undefined1 *)(iVar9 + 0x1e8) = *(undefined1 *)(iVar27 + 0x131);
        *(undefined1 *)(iVar9 + 0x1e9) = *(undefined1 *)(iVar27 + 0x132);
        *(undefined1 *)(iVar9 + 0x1ea) = *(undefined1 *)(iVar27 + 0x133);
        *(undefined1 *)(iVar9 + 0x1eb) = *(undefined1 *)(param_1 + 0x156);
        *(undefined1 *)(iVar9 + 0x1ec) = *(undefined1 *)(param_1 + 0x157);
        *(undefined1 *)(iVar9 + 0x1ed) = *(undefined1 *)(param_1 + 0x15c);
        *(undefined1 *)(iVar9 + 0x1ee) = *(undefined1 *)(param_1 + 0x15d);
        *(undefined1 *)(iVar9 + 0x1ef) = *(undefined1 *)(param_1 + 0x160);
        *(undefined1 *)(iVar9 + 0x1f0) = *(undefined1 *)(param_1 + 0x161);
        *(undefined1 *)(iVar9 + 0x1f1) = *(undefined1 *)(param_1 + 0x162);
        *(undefined1 *)(iVar9 + 0x1f2) = *(undefined1 *)(param_1 + 0x163);
      }
    }
    FUN_43aef28a(puVar26[0x7c],puVar26[0x7b],*(undefined4 *)(puVar26 + 0x9a));
  }
  if (iVar7 != 0) {
    FUN_437b215c(param_1,param_5,param_2);
    *(undefined2 *)(param_1 + 0x1938) = 0;
  }
  FUN_43859944(2,param_1,iVar18);
  return;
}


/* 4385ca3c */

void FUN_4385ca3c(undefined1 *param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  char cVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  char cVar6;
  uint uVar7;
  byte bVar8;
  char *pcVar9;
  undefined1 *puVar10;
  int iVar11;
  int iVar12;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  undefined1 auStack_3d [4];
  undefined1 auStack_39 [5];
  undefined2 auStack_34 [2];
  undefined2 uStack_30;
  byte bStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  param_1[0x1db] = 0;
  param_1[0x1fc] = 0;
  param_1[0x1fe] = 0;
  param_1[0x70] = 0;
  param_1[2] = 0;
  iVar11 = DAT_4385ce24;
  param_1[0x212] = *(undefined1 *)(param_4 + 0x52);
  iVar11 = iVar11 + 0x4385ca72;
  param_1[0x213] = *(undefined1 *)(param_4 + 0x58e);
  param_1[0x214] = *(undefined1 *)(param_4 + 0x590);
  param_1[1] = *(undefined1 *)(param_3 + 0xd0);
  *param_1 = *(undefined1 *)(param_3 + 0xa5);
  FUN_438fab10();
  pcVar9 = *(char **)(iVar11 + DAT_4385ce28);
  if (pcVar9[0x1c] == '\x01') {
    uVar3 = FUN_4383fca0(param_2,param_3);
    FUN_43b6d442(7,1);
    FUN_43b6d442(6,1);
    if (*(uint *)(param_2 + 0x348) < 7) {
      cVar6 = *(char *)(DAT_4385ce2c + 0x4385cace + *(uint *)(param_2 + 0x348));
    }
    else {
      cVar6 = '\0';
    }
    uVar7 = (uint)*(byte *)(param_3 + 0xec);
    if (*(char *)(param_3 + 2) == '\x01') {
      if (uVar7 == 1) {
        cVar6 = '\0';
      }
      else {
        if (uVar7 != 2) goto LAB_4385cb30;
        if (*(char *)(param_3 + 0xf8) == '\x01') {
          if (*(char *)(param_3 + 0xf7) == '\0') {
            cVar6 = '\x03';
          }
          else {
LAB_4385cb04:
            if (cVar6 == '\0') {
              cVar6 = '\x01';
            }
            else if (*(ushort *)(param_1 + 0x92) < 0x1297) {
              cVar6 = '\x02';
            }
            else {
              cVar6 = '\x01';
            }
          }
        }
        else {
          if ((*(char *)(param_3 + 0xf8) != '\0') || (*(char *)(param_3 + 0xf7) != '\x01'))
          goto LAB_4385cb04;
          cVar6 = '\x04';
        }
      }
    }
    else if (uVar7 < 3) {
      cVar6 = *(char *)(DAT_4385ce30 + 0x4385cb22 + uVar7);
    }
    else {
LAB_4385cb30:
      cVar6 = '\x06';
    }
    cVar1 = **(char **)(iVar11 + DAT_4385ce34);
    if ((cVar1 != '\0') && (cVar6 = cVar1, cVar1 == -1)) {
      cVar6 = '\0';
    }
    uVar2 = *(undefined1 *)(param_3 + 0xec);
    param_1[0x8d] = uVar3;
    param_1[0x94] = cVar6;
    param_1[0x95] = 8;
    param_1[0x8c] = uVar2;
    param_1[0xa0] = 2;
    param_1[0x96] = 0;
    param_1[0x97] = 0;
    param_1[0x98] = 0;
    param_1[0x99] = 0;
    param_1[0x9a] = 0;
    param_1[0x9b] = 0;
    param_1[0x9c] = 0;
    param_1[0x9d] = 0;
    param_1[0x9e] = 0;
    param_1[0x9f] = 0;
    FUN_438febd0(&uStack_40);
    param_1[0x19a] = uStack_40;
    param_1[0x19b] = uStack_3f;
    puVar10 = param_1;
    iVar5 = 0;
    do {
      iVar12 = iVar5 + 1;
      puVar10[0x19d] = auStack_3d[iVar5];
      puVar10[0x1a1] = auStack_39[iVar5];
      puVar10 = puVar10 + 1;
      iVar5 = iVar12;
    } while (iVar12 != 4);
    uVar4 = FUN_438feadc();
    FUN_438feaf4(param_1 + 0xa1,uVar4);
    FUN_438feaf4(param_1 + 0xb5,uVar4);
    uVar4 = FUN_438feae8();
    FUN_439c5a04(param_1 + 0xc9,0,uVar4);
    *(undefined4 *)(param_1 + 0xf4) = 0;
    *(undefined2 *)(param_1 + 0xf8) = 0;
    *(undefined2 *)(param_1 + 0xfa) = 0;
    param_1[0x10a] = 0;
    param_1[0x10b] = 0;
    param_1[0x10c] = 0;
    param_1[0x10e] = 0;
    param_1[0x10d] = 0;
    param_1[0x10f] = 0;
    param_1[0x111] = 0;
    param_1[0x110] = 0;
    param_1[0x112] = 0;
    param_1[0x113] = 0;
    param_1[0x114] = 0;
    param_1[0x115] = 0;
    param_1[0x116] = 0;
    param_1[0x117] = 0;
    *(undefined4 *)(param_1 + 0x11c) = 0;
    *(undefined4 *)(param_1 + 0x120) = 0;
    *(undefined4 *)(param_1 + 0x118) = 0;
    *(undefined4 *)(param_1 + 0x128) = 0;
    *(undefined4 *)(param_1 + 0x124) = 0;
    FUN_438feb4c(&bStack_2c);
    if ((byte)param_1[0x94] - 3 < 2) {
      if ((bStack_2c & 1) == 0) {
        bVar8 = param_1[300] & 0xfe | bStack_2c & 1;
      }
      else {
        bVar8 = param_1[300] | 1;
      }
    }
    else {
      bVar8 = param_1[300] & 0xfe;
    }
    param_1[300] = bVar8;
    param_1[0x133] = 0;
    param_1[300] = param_1[300] & 0xf1 | bStack_2c & 2 | bStack_2c & 4 | bStack_2c & 8;
    param_1[0x134] = 0;
    param_1[0x12d] = uStack_2b;
    param_1[0x12e] = uStack_2a;
    param_1[0x12f] = uStack_29;
    uVar3 = FUN_438feae8();
    param_1[0x130] = 0;
    param_1[0x131] = 0;
    param_1[0x135] = uVar3;
    uVar3 = FUN_438feadc();
    param_1[0x132] = uVar3;
    FUN_438feb10(auStack_34);
    *(undefined2 *)(param_1 + 0x8e) = uStack_30;
    *(undefined2 *)(param_1 + 0x90) = auStack_34[0];
    param_1[0x136] = 0;
    param_1[0x137] = 0;
    param_1[0x138] = 0;
    param_1[0x139] = 0;
    *(undefined2 *)(param_1 + 0x13a) = 0;
    *(undefined2 *)(param_1 + 0x16a) = 0;
    FUN_43857ecc(0x280,param_1[0x8d]);
    FUN_43857ecc(0x281,param_1[0x94]);
    uVar3 = param_1[0x8d];
    param_1[0x1a5] = *(undefined1 *)(param_3 + 0xfd);
    param_1[0x1a6] =
         *(byte *)(param_3 + 0xeb) & 7 | (*(byte *)(param_3 + 0xee) & 3) << 3 |
         (*(byte *)(param_3 + 0xef) & 1) << 5 | (*(byte *)(param_3 + 0xf1) & 1) << 6 |
         *(char *)(param_3 + 0xf2) << 7;
    if (*(char *)(param_3 + 2) == '\x01') {
      if (*(char *)(param_2 + 0x38e) == '\x03') {
        uVar4 = 2;
      }
      else if (*(char *)(param_2 + 0x38e) == '\x02') {
        uVar4 = 3;
      }
      else {
        iVar5 = FUN_43b0a4ee(uVar3);
        if ((iVar5 == 1) || (iVar5 = FUN_43b0a4fa(uVar3), iVar5 == 1)) {
          uVar4 = 1;
        }
        else {
          FUN_43b0a4ca(param_6,param_2);
          uVar4 = 1;
        }
      }
    }
    else {
      uVar4 = 0;
    }
    cVar6 = **(char **)(iVar11 + DAT_4385ce38);
    if (cVar6 != '\0') {
      if ((cVar6 == '\x01') || (cVar6 == '\x02')) {
        uVar4 = 0;
      }
      else if (cVar6 == '\x03') {
        uVar4 = 1;
      }
      else if (cVar6 == '\x04') {
        uVar4 = 2;
      }
      else if (cVar6 == '\x05') {
        uVar4 = 3;
      }
    }
    *(undefined4 *)(param_5 + 0x10) = uVar4;
  }
  else if (*(int *)(param_2 + 0x4f8) != 2) {
    *(uint *)(param_5 + 0x10) = (uint)(*(char *)(param_6 + 0x6fd) != '\0');
  }
  if (*pcVar9 == '\0') {
    if ((pcVar9[0x1c] != '\0') || (iVar5 = FUN_438fb300(), iVar5 == 0)) {
      if (pcVar9[0x1c] == '\x01') goto LAB_4385cdf8;
LAB_4385ce06:
      uVar3 = 0;
      goto LAB_4385ce08;
    }
  }
  else if (*(char *)(param_3 + 0xfb) != '\x01') {
LAB_4385cdf8:
    iVar5 = FUN_4384a190(param_3);
    if (iVar5 != 1) goto LAB_4385ce06;
  }
  uVar3 = 1;
LAB_4385ce08:
  *(undefined1 *)(*(int *)(iVar11 + DAT_4385ce3c) + 0x23d) = uVar3;
  *(undefined1 *)(param_5 + 0x15) = uVar3;
  return;
}

