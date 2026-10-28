
void FUN_43841070(int param_1,int param_2,undefined4 *param_3,byte *param_4,byte *param_5,
                 int param_6)

{
  undefined2 uVar1;
  undefined2 uVar2;
  byte bVar3;
  ushort uVar4;
  undefined1 uVar5;
  byte bVar6;
  char cVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined2 *puVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  uint uVar21;
  char *pcVar22;
  int iVar23;
  undefined2 uVar24;
  int iVar25;
  byte *pbVar26;
  undefined4 uVar27;
  char *pcVar28;
  int iVar29;
  int iVar30;
  bool bVar31;
  byte *local_84;
  undefined1 auStack_54 [26];
  undefined1 local_3a;
  undefined1 local_39;
  ushort local_2c;
  undefined2 local_2a [3];
  
  iVar29 = DAT_438418d4 + 0x43841088;
  if (*(int *)(param_2 + 0x1b8) == 0) {
    FUN_437b3a24(param_6);
  }
  pcVar22 = *(char **)(iVar29 + DAT_438418d8);
  if (*pcVar22 == '\0') {
    if (pcVar22[0x15] == '\0') {
      return;
    }
    local_84 = (byte *)0x0;
  }
  else if (param_5 == (byte *)0x0) {
    local_84 = param_5;
  }
  else {
    local_84 = (byte *)(uint)(param_4 != (byte *)0x0);
  }
  FUN_43857f40(900,*(undefined4 *)(param_2 + 0x1b8));
  bVar31 = false;
  *(undefined1 *)(DAT_438418dc + 0x438410d6) = 0;
  uVar8 = FUN_437b0604();
  *(undefined4 *)(param_1 + 8) = uVar8;
  iVar9 = FUN_437b0610();
  iVar19 = *(int *)(param_2 + 0x1b8);
  *(int *)(param_1 + 0xc) = iVar9;
  if (iVar19 == 0) {
    bVar31 = true;
  }
  else if (param_6 == 0) {
    bVar31 = false;
  }
  else if (*(int *)(param_1 + 8) == 0x11) {
    bVar31 = iVar9 != *(int *)(param_6 + 0xb6c);
  }
  uVar8 = *(undefined4 *)(param_2 + 0x1c0);
  *(bool *)(param_1 + 0x10) = bVar31;
  FUN_438408b8(uVar8,iVar19,param_1 + 4,param_6);
  iVar19 = FUN_4383fc48(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  iVar10 = FUN_4383fbc4(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar8 = FUN_4383fb40(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar11 = FUN_4383fb98(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  uVar12 = FUN_4383fc74(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  *(undefined4 *)(iVar19 + 0x294) = *(undefined4 *)(param_2 + 0x1c0);
  FUN_43844df8(uVar8,iVar10,iVar19);
  FUN_43859a78(param_2);
  thunk_FUN_437d0b9c(param_2);
  iVar9 = DAT_438418e0;
  if (local_84 == (byte *)0x0) {
    *(undefined1 *)(param_1 + 6) = 0;
    *(undefined1 *)(param_1 + 5) = 0;
    *(undefined4 *)(iVar9 + 0x43841186) = 0;
  }
  else {
    *(byte *)(param_1 + 6) = param_4[1] & 1;
    bVar6 = **(byte **)(iVar29 + DAT_438418e4);
    if (bVar6 == 0) {
      bVar6 = param_4[1] >> 6;
    }
    *(byte *)(param_1 + 5) = bVar6;
    *(uint *)(DAT_438418e8 + 0x438411bc) =
         (uint)param_4[5] * 0x1000000 + (uint)param_4[4] * 0x10000 + (uint)param_4[2] +
         (uint)param_4[3] * 0x100;
  }
  iVar9 = DAT_438418f0;
  iVar20 = param_1 + 700;
  iVar23 = param_1 + 4;
  iVar30 = *(int *)(iVar29 + DAT_438418ec);
  *(undefined1 *)(iVar30 + 0x590) = 0;
  iVar25 = *(int *)(iVar29 + iVar9);
  FUN_4385ca3c(iVar20,iVar19,iVar25,iVar30,iVar23,param_2);
  *(undefined1 *)(param_1 + 0x336) = 0;
  *(undefined1 *)(param_1 + 0x346) = 0;
  iVar9 = FUN_437284b4();
  if (iVar9 != 0) {
    local_39 = 0;
    FUN_438fb1c4(auStack_54);
  }
  FUN_4385c868(param_1,param_6,param_2,param_4,iVar19,iVar25);
  uVar5 = FUN_4382dcfc(iVar19,*(undefined1 *)(param_1 + 0x2be));
  *(undefined1 *)(iVar19 + 0x3dc) = uVar5;
  FUN_439c5a04(auStack_54,0,0x28);
  if (((*(int *)(iVar19 + 0x294) != 9) && (*(char *)(iVar25 + 0x124) != '\x01')) &&
     ((*(int *)(iVar19 + 0x294) != 0x12 || (*(int *)(iVar19 + 0x650) != 5)))) {
    local_3a = *(undefined1 *)(iVar25 + 2);
  }
  FUN_438fb1a0(auStack_54);
  uVar13 = FUN_4383fca0(iVar19,iVar25);
  FUN_4383f8f8(uVar13,iVar20,iVar19);
  FUN_437b4340(*(undefined2 *)(param_2 + 0x1b8),iVar19,uVar8,iVar10,iVar25,
               *(undefined4 *)(iVar29 + DAT_438418f4),uVar12,uVar11,iVar30);
  uVar12 = FUN_43b09cd4(param_2);
  FUN_43b08d80(iVar10,uVar12);
  if (pcVar22[0x15] == '\0') {
    FUN_43842158(iVar30,iVar10,iVar19,iVar25,*(undefined2 *)(param_2 + 0x1b8));
    FUN_43adcd2a(*(undefined2 *)(iVar10 + 0x15e));
    FUN_4383f5e4(param_1,*(undefined4 *)(param_2 + 0x1b8),0);
  }
  pcVar28 = *(char **)(iVar29 + DAT_438418f8);
  uVar12 = FUN_4385c974(param_2,iVar19,iVar25,pcVar28,param_6);
  cVar7 = *pcVar28;
  *(undefined4 *)(param_1 + 0x14) = uVar12;
  if (cVar7 == '\x01') {
    uVar24 = *(undefined2 *)(iVar10 + 0x13c);
    *(undefined2 *)(param_1 + 0x2ce) = *(undefined2 *)(iVar10 + 0x15e);
    *(undefined2 *)(param_1 + 0x49a) = uVar24;
    uVar12 = FUN_4385e598(iVar19);
    FUN_43b0a3d4(iVar20,pcVar28,uVar12);
    uVar24 = *(undefined2 *)(pcVar28 + 10);
    uVar1 = *(undefined2 *)(pcVar28 + 0xc);
    *(undefined2 *)(param_1 + 0x4c6) = *(undefined2 *)(pcVar28 + 8);
    *(undefined2 *)(param_1 + 0x4c8) = uVar24;
    *(undefined2 *)(param_1 + 0x4ca) = uVar1;
  }
  if (local_84 == (byte *)0x1) {
    bVar6 = 0;
    *param_5 = 0;
    if ((*(ushort *)(iVar19 + 0x4bc) & 0x20) == 0) {
      if (*(int *)(DAT_43841900 + 0x43841368) != 1) {
        if (*(int *)(DAT_43841900 + 0x43841368) != 3) goto LAB_43841396;
        if (*(char *)(DAT_43841908 + 0x43841388) == '\x01') {
          bVar6 = 0x42;
        }
        else {
          bVar6 = 2;
        }
        goto LAB_43841392;
      }
      if (*(char *)(DAT_43841904 + 0x43841374) == '\x01') {
        bVar6 = 0x40;
        goto LAB_43841392;
      }
LAB_43841396:
      param_5[1] = (byte)*(ushort *)(iVar19 + 0x4bc) & 0x20;
    }
    else {
      if (*(char *)(DAT_438418fc + 0x43841358) == '\x01') {
        bVar6 = 0x40;
      }
LAB_43841392:
      param_5[1] = bVar6;
    }
    if (*(char *)(iVar25 + 2) == '\x01') {
      param_5[1] = param_5[1] + 0x14;
    }
    if (*(int *)(param_1 + 0x14) - 1U < 3) {
      param_5[1] = param_5[1] | 0x80;
    }
    iVar9 = FUN_4382fe08(*(undefined2 *)(iVar10 + 0x162));
    if (iVar9 == 1) {
      bVar6 = 0;
      param_5[2] = 0;
    }
    else {
      param_5[2] = (byte)*(undefined2 *)(iVar10 + 0x162);
      bVar6 = (byte)((ushort)*(undefined2 *)(iVar10 + 0x162) >> 8);
    }
    param_5[3] = bVar6;
    param_5[4] = (byte)*(undefined2 *)(iVar10 + 0x15e);
    param_5[5] = (byte)((ushort)*(undefined2 *)(iVar10 + 0x15e) >> 8);
    if (*(char *)(iVar25 + 2) == '\x01') {
      iVar9 = FUN_43b0a4ee(*(undefined1 *)(param_2 + 0x1484));
      if (iVar9 == 1) {
        if (*(uint *)(iVar19 + 0x420) < 5) {
          bVar6 = *(byte *)(DAT_4384190c + 0x4384140a + *(uint *)(iVar19 + 0x420));
        }
        else {
          bVar6 = 0;
        }
        if (*(byte *)(iVar25 + 0xfe) <= bVar6) goto LAB_4384142e;
        bVar6 = *(byte *)(iVar25 + 0xfe) - bVar6;
      }
      else {
        if (*(int *)(param_1 + 0x14) != 0) goto LAB_4384142e;
        if (param_6 == 0) {
          bVar6 = 0;
        }
        else {
          bVar6 = *(byte *)(param_6 + 0x4ba);
        }
      }
    }
    else {
LAB_4384142e:
      bVar6 = 0;
    }
    param_5[6] = bVar6;
    if (*pcVar28 == '\x01') {
      bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 8));
      param_5[6] = bVar6;
    }
    iVar9 = DAT_43841910;
    param_5[8] = 0xa0;
    param_5[9] = 0;
    uVar24 = *(undefined2 *)(iVar9 + 0x43841452);
    param_5[0xc] = 0;
    param_5[10] = (byte)uVar24;
    param_5[0xb] = (byte)((ushort)uVar24 >> 8);
    cVar7 = *(char *)(iVar19 + 0x38d);
    bVar6 = *(byte *)(iVar19 + 0x38e);
    if (*(int *)(param_2 + 0x1c0) == 0x19) {
      cVar7 = '\x02';
    }
    bVar3 = *(byte *)(iVar19 + 0x38c);
    param_5[0xe] = 0;
    iVar9 = DAT_43841914;
    param_5[0xd] = (bVar3 & 1) * ' ' + (bVar6 & 3) * '\b' + cVar7 * '@';
    pbVar26 = *(byte **)(iVar29 + iVar9);
    if (*pbVar26 == 0) {
      if (*pcVar28 == '\x01') {
        param_5[0x12] = 1;
      }
      else {
        param_5[0x12] = 0;
      }
      iVar9 = *(int *)(param_1 + 0x31c);
      if (*(int *)(param_1 + 0x30c) - 0x12U < 2) {
        if (iVar9 != 1) {
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 0xc));
          param_5[0x13] = bVar6;
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 8));
          param_5[0x14] = bVar6;
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 10));
          param_5[0x15] = bVar6;
          goto LAB_43841576;
        }
        cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 0xc),*(undefined2 *)(param_1 + 0x2d0));
        param_5[0x13] = cVar7 - pcVar28[0x10];
        cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 8),*(undefined2 *)(param_1 + 0x2d0));
        param_5[0x14] = cVar7 - pcVar28[0x10];
        cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 10),*(undefined2 *)(param_1 + 0x2d0));
        bVar6 = cVar7 - pcVar28[0x10];
      }
      else if (*(int *)(param_1 + 0x30c) - 0x14U < 2) {
        if (iVar9 == 1) {
          cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 10),*(undefined2 *)(param_1 + 0x2d0));
          param_5[0x13] = cVar7 - pcVar28[0x10];
          cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 8),*(undefined2 *)(param_1 + 0x2d0));
          param_5[0x14] = cVar7 - pcVar28[0x10];
        }
        else {
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 10));
          param_5[0x13] = bVar6;
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 8));
          param_5[0x14] = bVar6;
        }
        bVar6 = 0;
      }
      else {
        if (iVar9 == 1) {
          cVar7 = FUN_43b076d0(*(undefined2 *)(pcVar28 + 8),*(undefined2 *)(param_1 + 0x2d0));
          param_5[0x13] = cVar7 - pcVar28[0x10];
        }
        else {
          bVar6 = FUN_43b075ec(*(undefined2 *)(pcVar28 + 8));
          param_5[0x13] = bVar6;
        }
        bVar6 = 0;
        param_5[0x14] = 0;
      }
    }
    else {
      param_5[0x12] = 1;
      param_5[0x13] = *pbVar26;
      param_5[0x14] = *pbVar26 + 8;
      bVar6 = *pbVar26 + 0x10;
    }
    param_5[0x15] = bVar6;
  }
LAB_43841576:
  uVar12 = FUN_4382fac8(*(undefined2 *)(iVar10 + 0x162));
  cVar7 = *(char *)(iVar25 + 2);
  *(undefined4 *)(DAT_43841918 + 0x43841586) = uVar12;
  iVar25 = *(int *)(iVar29 + DAT_4384191c);
  iVar9 = FUN_4382f914(iVar19,cVar7 != '\0',*(undefined2 *)(iVar25 + 0x9a),
                       *(undefined2 *)(iVar10 + 0x164));
  *(undefined2 *)(param_1 + 0x186) = *(undefined2 *)(iVar25 + 0xa4);
  *(int *)(param_1 + 0x180) = iVar9;
  if ((param_6 != 0) && (*(int *)(param_2 + 0x1b8) == 0)) {
    *(int *)(param_6 + 0xb78) = iVar9;
  }
  if (iVar9 == 0) {
    *(undefined2 *)(param_1 + 0x186) = 0;
  }
  puVar14 = (undefined2 *)
            FUN_4383fb6c(*(undefined4 *)(param_2 + 0x1c0),*(undefined4 *)(param_2 + 0x1b8));
  FUN_439c5a04(puVar14,0,0x158);
  uVar24 = *(undefined2 *)(param_2 + 0x1b8);
  param_3 = (undefined4 *)*param_3;
  *puVar14 = *(undefined2 *)(param_2 + 0x1bc);
  puVar14[1] = uVar24;
  uVar12 = param_3[1];
  uVar13 = param_3[2];
  uVar27 = param_3[3];
  *(undefined4 *)(puVar14 + 4) = *param_3;
  *(undefined4 *)(puVar14 + 6) = uVar12;
  *(undefined4 *)(puVar14 + 8) = uVar13;
  *(undefined4 *)(puVar14 + 10) = uVar27;
  uVar12 = param_3[5];
  uVar13 = param_3[6];
  uVar27 = param_3[7];
  *(undefined4 *)(puVar14 + 0xc) = param_3[4];
  *(undefined4 *)(puVar14 + 0xe) = uVar12;
  *(undefined4 *)(puVar14 + 0x10) = uVar13;
  *(undefined4 *)(puVar14 + 0x12) = uVar27;
  uVar12 = param_3[9];
  uVar13 = param_3[10];
  uVar27 = param_3[0xb];
  *(undefined4 *)(puVar14 + 0x14) = param_3[8];
  *(undefined4 *)(puVar14 + 0x16) = uVar12;
  *(undefined4 *)(puVar14 + 0x18) = uVar13;
  *(undefined4 *)(puVar14 + 0x1a) = uVar27;
  uVar4 = *(ushort *)(iVar19 + 0x4bc);
  uVar24 = *(undefined2 *)(iVar10 + 0x162);
  puVar14[0x7b] = uVar24;
  if (((uVar4 & 0x60) == 0) && ((uVar4 & 0x80) == 0)) {
    if (pcVar22[0x15] == '\x01') {
      FUN_4383fa40(puVar14,iVar19);
    }
    else {
      puVar14[0x34] = uVar4 & 0x80;
      puVar14[0x35] = uVar4 & 0x80;
      *(uint *)(puVar14 + 0x32) = (uint)(ushort)puVar14[0xe];
    }
  }
  else {
    uVar4 = puVar14[0x19];
    uVar1 = puVar14[0x1a];
    uVar2 = puVar14[0x18];
    iVar9 = *(int *)(puVar14 + 6);
    if (iVar9 == 0) {
      iVar9 = 1;
    }
    if (*(int *)(puVar14 + 0x2e) == 0) {
      iVar15 = 0xde3;
    }
    else {
      uVar12 = FUN_4355faf0(*(int *)(puVar14 + 0x2e),1000);
      iVar15 = FUN_4355faf0(DAT_438418d0,uVar12);
    }
    iVar16 = FUN_4382fa94(uVar24);
    uVar21 = *(uint *)(DAT_43841920 + 0x4384166e);
    uVar17 = (uint)(ushort)puVar14[0xe];
    if ((uVar21 & 0xff) == 5) {
      iVar18 = FUN_4355faf0(iVar9 + -1 + iVar16,iVar9);
      local_2c = (ushort)(uVar17 + iVar18);
      local_2a[0] = FUN_4355faf0((iVar9 * ((uVar17 + iVar18 & 0xffff) - uVar17) - iVar16) * 1000 +
                                 iVar15 + -1,iVar15);
    }
    else {
      local_2a[0] = 0;
      local_2c = uVar4;
    }
    FUN_43aebe32(uVar2,uVar4,&local_2c);
    FUN_43aebe32(uVar1,0,local_2a);
    *(undefined1 *)(puVar14 + 0x36) = 0;
    puVar14[0x34] = 0;
    *(char *)((int)puVar14 + 0x6d) = (char)uVar21;
    puVar14[0x35] = 0;
    puVar14[0x39] = 0;
    puVar14[0x37] = local_2a[0];
    puVar14[0x6d] = 0;
    puVar14[0x6e] = 0;
    iVar9 = DAT_43841924;
    *(uint *)(puVar14 + 0x32) = uVar17;
    puVar14[0x38] = local_2c;
    puVar14[0x6c] = 1;
    *(uint *)(puVar14 + 0x78) = local_2c - uVar17;
    if (**(byte **)(iVar29 + iVar9) != 0) {
      puVar14[0x34] = (ushort)**(byte **)(iVar29 + iVar9);
    }
    if ((**(byte **)(iVar29 + DAT_43841928) != 0) || (**(byte **)(iVar29 + DAT_4384192c) != 0)) {
      *(uint *)(puVar14 + 0x32) =
           (uint)**(byte **)(iVar29 + DAT_43841928) * 0x100 +
           (uint)**(byte **)(iVar29 + DAT_4384192c);
    }
    if (**(byte **)(iVar29 + DAT_43841930) != 0) {
      puVar14[0x35] = (ushort)**(byte **)(iVar29 + DAT_43841930);
    }
    if ((**(byte **)(iVar29 + DAT_43841934) != 0) || (**(byte **)(iVar29 + DAT_43841938) != 0)) {
      puVar14[0x37] =
           (ushort)**(byte **)(iVar29 + DAT_43841934) * 0x100 +
           (ushort)**(byte **)(iVar29 + DAT_43841938);
    }
    if ((**(byte **)(iVar29 + DAT_4384193c) != 0) || (**(byte **)(iVar29 + DAT_43841940) != 0)) {
      puVar14[0x38] =
           (ushort)**(byte **)(iVar29 + DAT_4384193c) * 0x100 +
           (ushort)**(byte **)(iVar29 + DAT_43841940);
    }
    if ((**(byte **)(iVar29 + DAT_43841944) != 0) || (**(byte **)(iVar29 + DAT_43841948) != 0)) {
      puVar14[0x39] =
           (ushort)**(byte **)(iVar29 + DAT_43841944) * 0x100 +
           (ushort)**(byte **)(iVar29 + DAT_43841948);
    }
  }
  iVar9 = DAT_43841950;
  *(char *)((int)puVar14 + 0x6d) = (char)*(undefined4 *)(DAT_4384194c + 0x438417e0);
  *(undefined1 *)(puVar14 + 0x6b) = *(undefined1 *)(DAT_43841954 + 0x438417ec);
  *(undefined1 *)((int)puVar14 + 0xd7) = *(undefined1 *)(DAT_43841958 + 0x438417f6);
  FUN_439c5320(puVar14 + 0x3d,iVar9 + 0x438417ea,0x5c);
  iVar9 = *(int *)(param_2 + 0x1c0);
  if (iVar9 < 0x15) {
    if (iVar9 < 0x13) {
      if (iVar9 != 7) {
        if (iVar9 < 8) {
          if (iVar9 == 1) {
            if ((*(int *)(param_2 + 0x90) != 7) || (*(int *)(param_2 + 0x4860) != 4)) {
              if (*(int *)(param_2 + 0x28) == 0) {
                if (*(int *)(param_2 + 0x6a8) == 1) {
                  uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xac);
                }
                else {
                  uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xa0);
                }
              }
              else {
                if (*(int *)(param_2 + 0x28) != 1) {
                  puVar14[0xab] = 0;
                  goto LAB_43841966;
                }
                uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xa2);
              }
              goto LAB_43841850;
            }
            iVar9 = *(int *)(iVar29 + DAT_4384195c);
            goto LAB_4384187e;
          }
        }
        else if (iVar9 < 10) goto LAB_43841856;
        goto LAB_43841960;
      }
      if (*(int *)(param_2 + 0x6a8) == 1) {
        uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xb4);
      }
      else {
        uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xaa);
      }
    }
    else {
LAB_43841856:
      iVar9 = *(int *)(iVar29 + DAT_4384195c);
      if (*(int *)(param_2 + 0x6a8) == 1) {
LAB_438418be:
        uVar24 = *(undefined2 *)(iVar9 + 0xa6);
      }
      else {
LAB_4384187e:
        uVar24 = *(undefined2 *)(iVar9 + 0xa4);
      }
    }
LAB_43841850:
    puVar14[0xab] = uVar24;
  }
  else {
    if (iVar9 == 0x1b) goto LAB_43841856;
    if (iVar9 < 0x1c) {
      if (iVar9 == 0x18) goto LAB_43841856;
    }
    else {
      if (iVar9 == 0x1f) {
        iVar9 = *(int *)(iVar29 + DAT_4384195c);
        goto LAB_438418be;
      }
      if (iVar9 == 0x20) {
        uVar24 = *(undefined2 *)(*(int *)(iVar29 + DAT_4384195c) + 0xa8);
        goto LAB_43841850;
      }
    }
LAB_43841960:
    puVar14[0xab] = 0;
  }
LAB_43841966:
  FUN_437b0810(iVar19,iVar10,uVar8,*(undefined4 *)(iVar29 + DAT_43841aa8),
               *(undefined4 *)(iVar29 + DAT_43841a98),*(undefined4 *)(iVar29 + DAT_43841a9c),iVar30,
               *(undefined4 *)(iVar29 + DAT_43841aa0),uVar11,iVar25,
               *(undefined4 *)(iVar29 + DAT_43841aa4),iVar23,iVar20,puVar14,0);
  FUN_4383fbf0(iVar19,uVar8,iVar23);
  FUN_43857f40(0x391,*(undefined4 *)(iVar10 + 0x15e));
  FUN_43857f40(0x391,*(undefined4 *)(iVar10 + 0x162));
  if (local_84 == (byte *)0x1) {
    FUN_43857f40(0x391,(uint)param_4[1] << 8 | (uint)*param_5 << 0x10 | (uint)*param_4 |
                       (uint)param_5[1] << 0x18);
    FUN_43857f40(0x391,(uint)param_5[4] << 0x10 | (uint)param_5[5] << 0x18 | (uint)param_5[2] |
                       (uint)param_5[3] << 8);
    FUN_43857f40(0x391,(uint)param_5[0xd] << 0x10 | (uint)param_5[0xe] << 0x18 | (uint)param_5[6] |
                       (uint)param_5[0xc] << 8);
  }
  FUN_43857f40(0x391,*(undefined1 *)(param_1 + 0x2be));
  FUN_43857f40(0x391,(uint)*(byte *)(param_1 + 0x31c) << 8 | (uint)*(byte *)(param_1 + 800) << 0x10
                     | (uint)*(byte *)(param_1 + 0x318));
  FUN_43857f40(0x391,*(undefined4 *)(param_1 + 0x326));
  FUN_43857f04(0x391,*(undefined2 *)(param_1 + 0x32a));
  FUN_43859944(0x10,param_1,param_2 + 0x1b8);
  return;
}

