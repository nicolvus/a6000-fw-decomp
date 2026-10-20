/* S41: read-only exports. */

/* 436d6118 */

undefined4 FUN_436d6118(void)

{
  return *(undefined4 *)(DAT_436d6124 + 0x436d6120 + DAT_436d6128);
}


/* 43841070 */

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
  byte *pbStack_84;
  undefined1 auStack_54 [26];
  undefined1 uStack_3a;
  undefined1 uStack_39;
  ushort uStack_2c;
  undefined2 auStack_2a [3];
  
  iVar29 = DAT_438418d4 + 0x43841088;
  if (*(int *)(param_2 + 0x1b8) == 0) {
    FUN_437b3a24(param_6);
  }
  pcVar22 = *(char **)(iVar29 + DAT_438418d8);
  if (*pcVar22 == '\0') {
    if (pcVar22[0x15] == '\0') {
      return;
    }
    pbStack_84 = (byte *)0x0;
  }
  else if (param_5 == (byte *)0x0) {
    pbStack_84 = param_5;
  }
  else {
    pbStack_84 = (byte *)(uint)(param_4 != (byte *)0x0);
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
  if (pbStack_84 == (byte *)0x0) {
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
    uStack_39 = 0;
    FUN_438fb1c4(auStack_54);
  }
  FUN_4385c868(param_1,param_6,param_2,param_4,iVar19,iVar25);
  uVar5 = FUN_4382dcfc(iVar19,*(undefined1 *)(param_1 + 0x2be));
  *(undefined1 *)(iVar19 + 0x3dc) = uVar5;
  FUN_439c5a04(auStack_54,0,0x28);
  if (((*(int *)(iVar19 + 0x294) != 9) && (*(char *)(iVar25 + 0x124) != '\x01')) &&
     ((*(int *)(iVar19 + 0x294) != 0x12 || (*(int *)(iVar19 + 0x650) != 5)))) {
    uStack_3a = *(undefined1 *)(iVar25 + 2);
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
  if (pbStack_84 == (byte *)0x1) {
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
      uStack_2c = (ushort)(uVar17 + iVar18);
      auStack_2a[0] =
           FUN_4355faf0((iVar9 * ((uVar17 + iVar18 & 0xffff) - uVar17) - iVar16) * 1000 +
                        iVar15 + -1,iVar15);
    }
    else {
      auStack_2a[0] = 0;
      uStack_2c = uVar4;
    }
    FUN_43aebe32(uVar2,uVar4,&uStack_2c);
    FUN_43aebe32(uVar1,0,auStack_2a);
    *(undefined1 *)(puVar14 + 0x36) = 0;
    puVar14[0x34] = 0;
    *(char *)((int)puVar14 + 0x6d) = (char)uVar21;
    puVar14[0x35] = 0;
    puVar14[0x39] = 0;
    puVar14[0x37] = auStack_2a[0];
    puVar14[0x6d] = 0;
    puVar14[0x6e] = 0;
    iVar9 = DAT_43841924;
    *(uint *)(puVar14 + 0x32) = uVar17;
    puVar14[0x38] = uStack_2c;
    puVar14[0x6c] = 1;
    *(uint *)(puVar14 + 0x78) = uStack_2c - uVar17;
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
  if (pbStack_84 == (byte *)0x1) {
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


/* 43792a0c */

void FUN_43792a0c(int param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  undefined4 uVar17;
  int iVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  undefined4 uVar22;
  undefined4 uVar23;
  undefined4 uVar24;
  short sVar25;
  int extraout_r1;
  undefined4 uVar26;
  undefined4 uVar27;
  undefined4 uVar28;
  undefined4 uVar29;
  undefined4 uVar30;
  undefined4 uVar31;
  undefined1 uVar32;
  char cVar33;
  byte bVar34;
  undefined1 *puVar35;
  undefined4 uVar36;
  undefined4 *puVar37;
  short *psVar38;
  int iVar39;
  int iVar40;
  undefined4 uVar41;
  char *pcVar42;
  int iVar43;
  int iVar44;
  undefined2 *puVar45;
  int iVar46;
  ushort *puVar47;
  uint uVar48;
  int iVar49;
  int *piVar50;
  uint *puVar51;
  int *piVar52;
  uint uVar53;
  undefined4 *puVar54;
  undefined4 uVar55;
  bool bVar56;
  bool bVar57;
  undefined1 *puVar58;
  undefined1 *puVar59;
  undefined1 *puVar60;
  undefined4 uStack_3b8;
  undefined4 uStack_3b4;
  undefined4 uStack_3b0;
  undefined4 uStack_3ac;
  undefined1 auStack_3a8 [96];
  undefined1 auStack_348 [96];
  undefined4 uStack_2e8;
  undefined4 uStack_2e4;
  undefined1 auStack_2e0 [96];
  undefined1 auStack_280 [96];
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined1 auStack_218 [272];
  undefined1 auStack_108 [20];
  undefined1 auStack_f4 [20];
  undefined1 auStack_e0 [20];
  undefined1 auStack_cc [20];
  undefined1 auStack_b8 [20];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [2];
  undefined2 uStack_52;
  undefined1 uStack_4c;
  undefined1 auStack_48 [4];
  undefined4 uStack_44;
  undefined1 auStack_40 [4];
  byte bStack_3c;
  undefined1 auStack_38 [4];
  byte bStack_34;
  undefined4 uStack_30;
  undefined1 auStack_2c [8];
  
  iVar43 = DAT_43792c44 + 0x43792a1e;
  iVar44 = *(int *)(iVar43 + DAT_43792c48);
  if ((*(byte *)(iVar44 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43792c4c + 0x43792a2e);
  }
  uVar13 = FUN_437876dc();
  if (*(char *)(iVar44 + 0xaa) != '\0') {
    *(int *)(DAT_43792c50 + 0x43792a42) = *(int *)(DAT_43792c50 + 0x43792a42) + 1;
    FUN_4355fd4c();
    if (extraout_r1 == 0) {
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_4378eb78(5,2,1,DAT_43792c54 + 0x43792a68,uVar14,uVar15,uVar16);
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_43902718(DAT_43792c58 + 0x43792a8c,uVar14,uVar15,uVar16);
    }
  }
  cVar33 = *(char *)(iVar44 + 0x1b);
  if (cVar33 != '\0') {
    puVar35 = (undefined1 *)(DAT_43792c5c + 0x43792a97);
    puVar37 = DAT_43792c38;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c3c);
    puVar35 = (undefined1 *)(DAT_43792c60 + 0x43792aad);
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c40);
    if (cVar33 == '\x01') {
      FUN_4378ec60();
      *(undefined1 *)(iVar44 + 0x1b) = 0;
    }
  }
  if (*(byte *)(iVar44 + 0x11) != 0) {
    uVar53 = (uint)*(byte *)(iVar44 + 0x11) * 100;
    iVar46 = *(int *)(*(int *)(DAT_43792c64 + 0x43792adc) + 8);
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c68)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c6c + 0x43792af8,uVar48);
      FUN_43902718(DAT_43792c70 + 0x43792b04,uVar48);
      FUN_43561540(DAT_43792c74 + 0x43792b0c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c78)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c7c + 0x43792b28,uVar48);
      FUN_43902718(DAT_43792c80 + 0x43792b34,uVar48);
      FUN_43561540(DAT_43792c84 + 0x43792b3c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c88)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c8c + 0x43792b58,uVar48);
      FUN_43902718(DAT_43792c90 + 0x43792b64,uVar48);
      FUN_43561540(DAT_43792c94 + 0x43792b6c);
    }
  }
  iVar46 = DAT_43792c98;
  if (param_1 != **(int **)(DAT_43792c98 + 0x43792b7a)) {
    iVar43 = thunk_FUN_436cd00c();
    puVar37 = *(undefined4 **)(iVar46 + 0x43792b7a);
    uVar48 = (uint)(iVar43 - puVar37[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43792c9c + 0x43792b96,param_1,*puVar37,uVar48);
    FUN_43902718(DAT_43792ca0 + 0x43792bac,param_1,**(undefined4 **)(iVar46 + 0x43792b7a),uVar48);
    FUN_4378f988(3,0,uVar48);
    if ((*(byte *)(iVar44 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43792ca4 + 0x43792bc8);
    }
    if ((*(byte *)(iVar44 + 0x1b) & 2) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar46 = FUN_43ae8d4e();
  if (iVar46 == 0) {
    FUN_43901778();
    if (*(char *)(DAT_43792ca8 + 0x43792bf2) != '\0') {
      *(undefined1 *)(DAT_43792cac + 0x43792bfc) = 1;
    }
    uVar32 = 0;
    puVar35 = (undefined1 *)(DAT_43792cb0 + 0x43792c04);
  }
  else {
    uVar32 = 1;
    puVar35 = (undefined1 *)(DAT_43792cb4 + 0x43792c0c);
  }
  *puVar35 = uVar32;
  if (*(byte *)(iVar44 + 0x20) == 0) {
    psVar38 = (short *)(DAT_437935f4 + 0x43792ccc);
    sVar25 = 0;
  }
  else {
    uVar48 = *(int *)(*(int *)(DAT_43792cb8 + 0x43792c1e) + 0x14) - 1;
    if (uVar48 < 2) {
      sVar25 = *(short *)(DAT_43792cbc + 0x43792c28 + uVar48 * 2);
    }
    else {
      sVar25 = 0x3c;
    }
    sVar25 = sVar25 * (ushort)*(byte *)(iVar44 + 0x20);
    psVar38 = (short *)(&UNK_43792c36 + DAT_43792cc0);
  }
  *psVar38 = sVar25;
  *(int *)(DAT_437935f8 + 0x43792cd8) = *(int *)(DAT_437935f8 + 0x43792cd8) + 1;
  *(undefined1 *)(DAT_437935fc + 0x43792ce6) = 0;
  FUN_4378f7a0(0x708);
  iVar46 = FUN_437999e4(1,1);
  if (((iVar46 != 0) || (iVar46 = FUN_437999e4(1,2), iVar46 != 0)) &&
     ((iVar46 = DAT_43793608, *(ushort *)(DAT_43793600 + 0x43793376) < 2 ||
      (*(int *)(*(int *)(DAT_43793604 + 0x43792d18) + 0xc) != 0)))) {
    iVar49 = DAT_4379360c + 0x43792d26;
    FUN_43aef52c(iVar49,DAT_43793608 + 0x43793fb4);
    FUN_437d9a04((int)&DAT_437946b4 + iVar46,iVar49);
    if (((*(byte *)(iVar44 + 0x16) & 5) == 4) && (*(int *)(iVar46 + 0x43793598) != 0)) {
      FUN_43ad53b8(iVar46 + 0x4379359c,*(int *)(iVar46 + 0x43793598),0);
    }
  }
  iVar46 = DAT_43793610;
  FUN_43a0cb54();
  FUN_43b2a04a();
  puVar47 = (ushort *)(iVar46 + 0x43792d68);
  FUN_437fdf5c();
  uVar12 = *(undefined2 *)(iVar46 + 0x43792d7a);
  uVar1 = *puVar47;
  uVar2 = *(undefined2 *)(iVar46 + 0x43792d6c);
  uVar3 = *(undefined2 *)(iVar46 + 0x43792d78);
  uVar4 = *(undefined2 *)(iVar46 + 0x43792d74);
  uVar8 = *(undefined2 *)(iVar46 + 0x43792d76);
  uVar5 = *(undefined2 *)(iVar46 + 0x43792d7c);
  uVar6 = *(undefined2 *)(iVar46 + 0x43792d6a);
  uVar9 = *(undefined2 *)(iVar46 + 0x43792d70);
  uVar7 = *(undefined2 *)(iVar46 + 0x43792d7e);
  uVar10 = *(undefined2 *)(iVar46 + 0x43792d6e);
  uVar11 = *(undefined2 *)(iVar46 + 0x43792d72);
  FUN_43804c5c(puVar47);
  *(undefined2 *)(iVar46 + 0x43792d6a) = uVar6;
  *(undefined2 *)(iVar46 + 0x43792d6c) = uVar2;
  *(undefined2 *)(iVar46 + 0x43792d74) = uVar4;
  *(undefined2 *)(iVar46 + 0x43792d7e) = uVar7;
  iVar49 = DAT_43793614;
  *(undefined2 *)(iVar46 + 0x43792d76) = uVar8;
  *(undefined2 *)(iVar46 + 0x43792d7a) = uVar12;
  piVar50 = (int *)(iVar49 + 0x43792dca);
  *(undefined2 *)(iVar46 + 0x43792d78) = uVar3;
  *(undefined2 *)(iVar46 + 0x43792d7c) = uVar5;
  *puVar47 = uVar1;
  *(undefined2 *)(iVar46 + 0x43792d70) = uVar9;
  *(undefined2 *)(iVar46 + 0x43792d6e) = uVar10;
  *(undefined2 *)(iVar46 + 0x43792d72) = uVar11;
  FUN_43ae8fa2();
  FUN_43ae8f98();
  FUN_437fc404(piVar50);
  FUN_437fc54c(1);
  FUN_4375dd04();
  iVar46 = FUN_437fc54c(0);
  FUN_4380c7f8(iVar46,auStack_38);
  bVar56 = false;
  if ((bStack_34 & 0x20) != 0) {
    iVar49 = *(int *)(iVar49 + 0x43792dd6);
    if (*(uint *)(iVar49 + 0xc) < 2) {
      bVar56 = false;
      if (*(char *)(iVar49 + 0x11) != '\0') {
        bVar56 = *(int *)(*piVar50 + 0x2c4) != 0;
      }
    }
    else {
      bVar56 = false;
    }
  }
  iVar49 = FUN_43b00cb4(uVar13);
  if ((((iVar49 == 1) && (iVar46 == 0x110)) &&
      (sVar25 = *(short *)(*(int *)(DAT_43793618 + 0x43792e4a) + 0x240), sVar25 != 0x110)) &&
     (sVar25 != 0x101)) {
    bVar57 = sVar25 != 0x100;
  }
  else {
    bVar57 = false;
  }
  if ((((*(int *)(*(int *)(DAT_4379361c + 0x43792e6c) + 0xc) == 1) ||
       (*(uint *)(DAT_43793620 + 0x43793446) < 2)) || (bVar56)) && (!bVar57)) {
    uVar12 = FUN_437fc54c();
    iVar46 = DAT_43793624;
    *(undefined2 *)(DAT_43793624 + 0x43792e90) = uVar12;
    uVar12 = FUN_437fc54c(2);
    *(undefined2 *)(iVar46 + 0x43792e92) = uVar12;
    uVar12 = FUN_437fc54c(1);
    *(undefined2 *)(iVar46 + 0x43792e94) = uVar12;
    uVar12 = FUN_437fc54c(3);
    *(undefined2 *)(iVar46 + 0x43792e96) = uVar12;
    uVar12 = FUN_437fc54c(5);
    *(undefined2 *)(iVar46 + 0x43792e9a) = uVar12;
    uVar12 = FUN_437fc54c(4);
    *(undefined2 *)(iVar46 + 0x43792e98) = uVar12;
    uVar12 = FUN_437fc54c(6);
    *(undefined2 *)(iVar46 + 0x43792e9c) = uVar12;
    uVar12 = FUN_437fc54c(8);
    *(undefined2 *)(iVar46 + 0x43792e9e) = uVar12;
    uVar12 = FUN_437fc54c(10);
    *(undefined2 *)(iVar46 + 0x43792ea2) = uVar12;
    uVar12 = FUN_437fc54c(9);
    *(undefined2 *)(iVar46 + 0x43792ea0) = uVar12;
    uVar12 = FUN_437fc54c(0xc);
    iVar49 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x14);
    iVar39 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x34);
    *(undefined2 *)(iVar46 + 0x43792ea6) = uVar12;
    if (iVar49 == iVar39) {
      uVar12 = FUN_437fc54c(0xb);
      *(undefined2 *)(iVar46 + 0x43792ea4) = uVar12;
    }
    FUN_4380c7f8(*(undefined2 *)(DAT_4379362c + 0x43792f00),(int)&DAT_43793708 + DAT_4379362c);
  }
  iVar49 = DAT_43793638;
  iVar46 = DAT_43793634;
  iVar39 = *(int *)(DAT_43793630 + 0x43792f1a);
  if (*(int *)(*(int *)(DAT_43793630 + 0x43792f12) + 0xb4) == 1) {
    puVar35 = (undefined1 *)(DAT_43793634 + 0x43792f2a);
    *(undefined1 *)(DAT_43793638 + 0x43792f2c) = *puVar35;
    *(undefined1 *)(iVar49 + 0x43792f2d) = *(undefined1 *)(iVar46 + 0x43792f2b);
    FUN_43796044(puVar35);
    iVar40 = 0;
    if (*(char *)(iVar46 + 0x43792f2b) != '\0') {
      if (*(char *)(iVar49 + 0x43792f2d) != '\0') goto LAB_43792f54;
      iVar46 = FUN_4378f9b4();
      iVar40 = **(int **)(iVar46 + 4) + 5;
    }
    *(int *)(iVar39 + 0x204) = iVar40;
  }
LAB_43792f54:
  iVar49 = FUN_43b00cba(uVar13);
  iVar46 = DAT_4379363c;
  if (iVar49 != 0) {
    FUN_43b00dd4(uVar13);
    FUN_43805b04(uVar13,iVar46 + 0x43792f6e,DAT_43793640 + 0x43792f72,DAT_43793640 + 0x43793516);
    FUN_43b00e40(uVar13,iVar46 + 0x43792f6e);
  }
  iVar46 = DAT_43793648;
  piVar50 = (int *)(DAT_43793648 + 0x43792f96);
  iVar49 = (int)&DAT_43794dfc + DAT_43793644;
  FUN_437da078(piVar50,iVar49);
  FUN_43ae7564(piVar50,iVar49);
  iVar49 = *piVar50;
  if (*(int *)(iVar49 + 0xb4) == 2) {
    iVar46 = *(int *)(iVar46 + 0x43792f9e);
    *(undefined4 *)(iVar46 + 0x204) = *(undefined4 *)(iVar46 + 0x238);
    *(undefined1 *)(iVar46 + 0x202) = *(undefined1 *)(iVar46 + 0x234);
  }
  bVar34 = *(byte *)(DAT_4379364c + 0x437937d9) & 0x40;
  if (((*(byte *)(DAT_4379364c + 0x437937d9) & 0x40) != 0) &&
     (bVar34 = 1, *(int *)(iVar49 + 0x30) != 1)) {
    bVar34 = 0;
  }
  *(byte *)(DAT_4379364c + 0x4379378c) = bVar34;
  if ((*(char *)(DAT_43793654 + 0x43792fee) != *(char *)(DAT_43793650 + 0x437937ac)) ||
     (*(int *)(DAT_43793658 + 0x43793000) != *(int *)(iVar49 + 0x34))) {
    FUN_43901a8c(4,0x203e,*(char *)(DAT_43793650 + 0x437937ac),*(undefined4 *)(iVar49 + 0x34));
    *(undefined1 *)(DAT_43793660 + 0x4379301e) = *(undefined1 *)(DAT_4379365c + 0x437937dc);
    *(undefined4 *)(DAT_43793668 + 0x43793032) =
         *(undefined4 *)(*(int *)(DAT_43793664 + 0x4379302e) + 0x34);
  }
  iVar49 = DAT_4379368c;
  iVar46 = DAT_43793688;
  if ((*(byte *)(*(int *)(DAT_4379366c + 0x43793044) + 0x266) & 0x20) == 0) {
    *(undefined4 *)(DAT_43793690 + 0x437938aa) = 0;
  }
  else {
    psVar38 = (short *)(DAT_43793670 + 0x43793052);
    if ((ushort)(*psVar38 - 0x148U) < 2) {
      if (*(int *)(DAT_43793670 + 0x43793116) - 8U < 4) {
                    /* WARNING: Could not recover jumptable at 0x43793066. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_43793066::switchdataD_4379306a +
                  (uint)*(byte *)(*(int *)(DAT_43793670 + 0x43793116) + 0x43793062) * 2))();
        return;
      }
    }
    else {
      if ((*(char *)(DAT_43793670 + 0x43793812) == '\0') ||
         (*(int *)(*(int *)(DAT_4379366c + 0x4379303c) + 0x34) != 0)) {
        uVar14 = 0;
        psVar38 = (short *)(DAT_43793684 + 0x437930c6);
      }
      else if (*(int *)(DAT_43793670 + 0x43793116) == 8) {
        uVar14 = 1;
      }
      else {
        uVar14 = 0;
        if (*(int *)(DAT_43793670 + 0x43793116) == 9) {
          uVar14 = 2;
        }
      }
      *(undefined4 *)(psVar38 + 0x3d6) = uVar14;
      iVar39 = *(int *)(iVar46 + 0x4379387c);
      if (*(int *)(iVar49 + 0x437930d6) != iVar39) {
        FUN_43901a8c(4,0x203f,iVar39,0);
        *(int *)(iVar49 + 0x437930d6) = *(int *)(iVar46 + 0x4379387c);
      }
    }
  }
  iVar49 = DAT_437936a0;
  iVar46 = DAT_4379369c;
  if (((*(uint *)(DAT_43793694 + 0x43793910) & 0xf8000) == 0x38000) &&
     (*(int *)(*(int *)(DAT_43793698 + 0x4379311c) + 0x474) == 2)) {
    uVar32 = 1;
  }
  else {
    uVar32 = 0;
  }
  *(undefined1 *)(DAT_43793694 + 0x437938f1) = uVar32;
  cVar33 = *(char *)(iVar46 + 0x4379391f);
  if (*(char *)(iVar49 + 0x4379313c) != cVar33) {
    FUN_43901a8c(4,0x2043,cVar33,0);
    *(char *)(iVar49 + 0x4379313c) = *(char *)(iVar46 + 0x4379391f);
  }
  iVar46 = DAT_437936a8;
  uVar48 = *(byte *)(DAT_437936a4 + 0x4379396a) & 7;
  if (uVar48 - 1 < 6) {
                    /* WARNING: Could not recover jumptable at 0x43793170. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43793170::switchdataD_43793174 + (uint)*(byte *)(uVar48 + 0x43793173) * 2))
              ();
    return;
  }
  *(undefined4 *)(DAT_437936a8 + 0x43793908) = 0;
  *(undefined4 *)(iVar46 + 0x437938fc) = *(undefined4 *)(*(int *)(DAT_437936ac + 0x43793192) + 0x30)
  ;
  *(undefined4 *)(iVar46 + 0x4379390c) = 1;
  iVar49 = DAT_437936e4;
  iVar46 = DAT_437936e0;
  piVar50 = (int *)(DAT_437936e4 + 0x437932b4);
  iVar39 = FUN_43ae8c50(*(undefined4 *)(DAT_437936e0 + 0x43793a2a));
  iVar49 = *(int *)(*(int *)(iVar49 + 0x437932b8) + 0x14);
  *(int *)(iVar46 + 0x43793a2e) = iVar39;
  *(bool *)(iVar46 + 0x43793a32) = iVar39 != iVar49;
  iVar49 = FUN_436e9234();
  iVar40 = *piVar50;
  iVar39 = *(int *)(iVar40 + 0x178);
  uVar14 = *(undefined4 *)(DAT_437936e8 + 0x437932e2 + (iVar49 * 3 + *(int *)(iVar40 + 0x174)) * 4);
  *(int *)(iVar46 + 0x43793a62) = iVar39;
  *(undefined4 *)(iVar46 + 0x43793a66) = uVar14;
  bVar34 = *(byte *)(iVar40 + 0x17c);
  iVar49 = *(int *)(DAT_437936ec + 0x43793300);
  *(uint *)(iVar46 + 0x43793a6a) = (uint)bVar34;
  iVar46 = DAT_437936f4;
  if ((iVar49 != iVar39) || (*(uint *)(DAT_437936f0 + 0x4379330e) != (uint)bVar34)) {
    FUN_439d88c4();
    FUN_43901a8c(4,0x2030,*(undefined4 *)(iVar46 + 0x43793ad2),0xff);
    uVar15 = *(undefined4 *)(*(int *)(DAT_437936f8 + 0x43793330) + 0x174);
    uVar14 = FUN_436e9234();
    FUN_43901a8c(4,0x2031,uVar15,uVar14);
    FUN_43901a8c(4,0x203c,*(undefined4 *)(iVar46 + 0x43793386),*(undefined4 *)(iVar46 + 0x43793ada))
    ;
    *(undefined4 *)(DAT_437936fc + 0x43793360) = *(undefined4 *)(iVar46 + 0x43793ad2);
    *(undefined4 *)(DAT_43793700 + 0x4379336a) = *(undefined4 *)(iVar46 + 0x43793ada);
  }
  if ((*(char *)(DAT_43793704 + 0x43793370) == '\0') &&
     ((((sVar25 = *(short *)(DAT_43793708 + 0x4379337a), sVar25 == 0x11a || (sVar25 == 0x118)) ||
       (sVar25 == 0x102)) || (((sVar25 == 0x11b || (sVar25 == 0x119)) || (sVar25 == 0x107)))))) {
    if (*(int *)(*(int *)(DAT_4379370c + 0x437933a6) + 0x174) == 1) {
      FUN_439c5a04(auStack_54,0,9);
      uStack_52 = 0x40d4;
      uStack_4c = (undefined1)*(undefined4 *)(DAT_43793710 + 0x43793b7e);
      auStack_54[0] = 5;
      FUN_435aa02c(auStack_2c);
      FUN_435a92e0(auStack_218);
      iVar46 = FUN_43a49628(auStack_218,DAT_437935f0);
      if (iVar46 == 0) {
        iVar46 = FUN_435a9304(auStack_218,auStack_54,9);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_4379371c + 0x43793428,iVar46);
          iVar49 = DAT_43793720 + 0x43793430;
          goto LAB_43793456;
        }
        iVar46 = FUN_435aa20c(auStack_2c,DAT_437935f0,auStack_218);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_43793724 + 0x43793450,iVar46);
          iVar49 = DAT_43793728 + 0x43793458;
          goto LAB_43793456;
        }
      }
      else {
        FUN_4378eb78(3,9,1,DAT_43793714 + 0x43793400,iVar46);
        iVar49 = DAT_43793718 + 0x43793408;
LAB_43793456:
        FUN_43902718(iVar49,iVar46);
      }
      FUN_435a92c8(auStack_218);
      FUN_435aa014(auStack_2c);
    }
    *(undefined1 *)(DAT_4379372c + 0x43793474) = 1;
  }
  iVar49 = DAT_43793734;
  iVar46 = DAT_43793730;
  piVar50 = (int *)(DAT_43793734 + 0x43793480);
  FUN_437c1740(piVar50,DAT_43793730 + 0x43794bae);
  uVar48 = (*(byte *)(iVar46 + 0x43793c86) & 0x3f) >> 4;
  if (uVar48 == 1) {
    *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
    *(undefined4 *)(iVar46 + 0x43793bea) = *(undefined4 *)(iVar46 + 0x437938e6);
    *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
    *(undefined1 *)(iVar46 + 0x43793a46) = 0;
    *(undefined4 *)(iVar46 + 0x43793a4a) = 0;
    *(undefined4 *)(iVar46 + 0x437934c6) = 0;
    iVar49 = FUN_43794a44(piVar50);
    if (iVar49 != 0) {
      if (*(uint *)(iVar46 + 0x437938d6) < 4) {
                    /* WARNING: Could not recover jumptable at 0x437935c4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_437935c4::switchdataD_437935c8 +
                  (uint)(&switchD_437935c4::switchdataD_437935c8)[*(uint *)(iVar46 + 0x437938d6)] *
                  2))();
        return;
      }
      iVar46 = DAT_437942c0 + 0x43793788;
      FUN_4378eb78(5,0,1,DAT_437942bc + 0x43793786,iVar46,0x93c);
      FUN_43902718(DAT_437942c4 + 0x437937a0,iVar46,0x93c);
    }
    goto LAB_437937a2;
  }
  if (uVar48 == 2) {
    iVar39 = *piVar50;
    if (*(int *)(*(int *)(iVar49 + 0x43793484) + 0x10) == *(int *)(iVar39 + 0x20)) {
      uVar14 = *(undefined4 *)(iVar39 + 0x24);
      *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar39 + 0x1c);
      iVar49 = *(int *)(iVar39 + 0x28);
      *(undefined4 *)(iVar46 + 0x43793a4a) = uVar14;
      *(int *)(iVar46 + 0x43793a42) = iVar49;
      if ((*(ushort *)(iVar46 + 0x43793c86) & 0x1c0) == 0) {
        *(byte *)(iVar46 + 0x43793a46) =
             (byte)(((uint)*(ushort *)(iVar46 + 0x43793c86) << 0x17) >> 0x1d);
        if (((iVar49 == 1) &&
            ((*(int *)(iVar39 + 0x538) != 1 || (*(int *)(iVar46 + 0x43793bf6) != 0)))) &&
           (*(char *)(DAT_43793738 + 0x43793ccf) == '\0')) {
          *(undefined1 *)(DAT_43793738 + 0x43793aae) = 1;
        }
      }
      else {
        *(undefined1 *)(iVar46 + 0x43793a46) = 0;
      }
    }
    iVar46 = DAT_4379373c + 0x437934fe;
    uVar14 = *(undefined4 *)(DAT_4379373c + 0x4379396e);
    goto LAB_43793588;
  }
  *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
  *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
  *(undefined1 *)(iVar46 + 0x43793a46) = 0;
  iVar49 = FUN_43794a44(piVar50);
  if (iVar49 == 0) {
    uVar14 = *(undefined4 *)(iVar46 + 0x437934c6);
  }
  else {
    uVar14 = *(undefined4 *)(iVar46 + 0x437938d6);
  }
  switch(uVar14) {
  case 0:
    uVar14 = 0;
    iVar46 = DAT_43793740 + 0x43793538;
    break;
  case 1:
    iVar46 = DAT_43793748 + 0x43793546;
    goto LAB_4379357a;
  case 2:
    uVar14 = 2;
    iVar46 = DAT_43793744 + 0x43793540;
    break;
  case 3:
    uVar14 = 4;
    iVar46 = DAT_4379374c + 0x4379354e;
    break;
  default:
    iVar46 = DAT_43793754 + 0x4379355e;
    FUN_4378eb78(5,0,1,DAT_43793750 + 0x4379355a,iVar46,0x91e);
    FUN_43902718(DAT_43793758 + 0x43793574,iVar46,0x91e);
    iVar46 = DAT_4379375c + 0x4379357c;
LAB_4379357a:
    uVar14 = 1;
  }
  *(undefined4 *)(iVar46 + 0x5cc) = uVar14;
  iVar46 = DAT_43793760 + 0x43793586;
  uVar14 = *(undefined4 *)(DAT_43793760 + 0x437939ee);
LAB_43793588:
  *(undefined4 *)(iVar46 + 0x76c) = uVar14;
LAB_437937a2:
  puVar51 = (uint *)(DAT_437942cc + 0x437937b6);
  FUN_4380f440(DAT_437942d0 + 0x437937bc,puVar51,DAT_437942c8 + 0x43793d54,0);
  if (*(byte *)(iVar44 + 0xb3) != 0) {
    *puVar51 = (uint)*(byte *)(iVar44 + 0xb3);
  }
  iVar46 = DAT_437942dc;
  iVar39 = DAT_437942dc + 0x437937de;
  FUN_4380e0cc(DAT_437942d4 + 0x437937da,DAT_437942d8 + 0x437937dc);
  FUN_4380e138(iVar39);
  iVar49 = DAT_437942e4;
  if ((uint)*(byte *)(DAT_437942e0 + 0x437937f0) != (int)(char)*(byte *)(iVar46 + 0x437937e3)) {
    *(byte *)(DAT_437942e0 + 0x437937f0) = *(byte *)(iVar46 + 0x437937e3);
    FUN_43ae913c(auStack_68,iVar49 + 0x43793804);
    FUN_439018b0(DAT_437942e8 + 0x43793814,auStack_68,iVar39,0);
  }
  iVar46 = DAT_437942ec;
  if ((1 < *(uint *)(DAT_437942ec + 0x43793df0)) &&
     (uVar48 = *(uint *)(*(int *)(DAT_437942f0 + 0x43793836) + 0xc),
     (*(uint *)(DAT_437942ec + 0x43793fac) & 1) != uVar48)) {
    if (uVar48 == 0) {
      uVar14 = 2;
    }
    else {
      uVar14 = 1;
    }
    *(undefined4 *)(DAT_437942ec + 0x43793fac) = uVar14;
    *(undefined4 *)(iVar46 + 0x43793fbc) = uVar14;
    FUN_4378ea78(0);
  }
  iVar49 = DAT_437942f8;
  iVar46 = DAT_437942f4;
  if (*(int *)(DAT_437942f4 + 0x43793fd2) == *(int *)(DAT_437942f4 + 0x43793dea)) {
    uVar48 = *(uint *)(*(int *)(DAT_437942f8 + 0x43793872) + 0x3c);
    if (uVar48 == 0) {
      iVar39 = FUN_43b00cba(uVar13);
      if ((((iVar39 == 0) || (*(int *)(iVar46 + 0x43793912) != 1)) ||
          ((*(byte *)(iVar46 + 0x4379401e) & 1) == 0)) ||
         (*(int *)(*(int *)(iVar49 + 0x43793872) + 0xc) != 0)) {
        iVar49 = FUN_43b039fc(DAT_43794624 + 0x437945c4,DAT_43794628 + 0x437945c6);
        iVar46 = DAT_43794308;
        if (iVar49 == 0) {
          if (bVar56) {
            FUN_4378ea78();
            iVar46 = DAT_43794304;
            *(undefined4 *)(DAT_43794304 + 0x437940aa) = 0;
            *(undefined4 *)(iVar46 + 0x437940ba) = 0;
          }
          else if ((*(short *)(DAT_43794308 + 0x43793932) == 0x121) ||
                  (*(short *)(DAT_43794308 + 0x43793932) == 300)) {
            FUN_4378ea78(0);
            iVar46 = DAT_4379430c;
            *(undefined4 *)(DAT_4379430c + 0x437940d8) = 0;
            *(undefined4 *)(iVar46 + 0x437940e8) = 0;
          }
          else if (*(uint *)(DAT_43794308 + 0x43793f02) < 2) {
            if (*(int *)(*(int *)(DAT_43794310 + 0x43793968) + 0xc) == 0) {
              uVar14 = 0;
LAB_43793978:
              FUN_4378ea78();
              *(undefined4 *)(iVar46 + 0x437940be) = uVar14;
              *(undefined4 *)(iVar46 + 0x437940ce) = uVar14;
            }
          }
          else {
            uVar14 = 1;
            if (*(int *)(*(int *)(DAT_43794314 + 0x43793976) + 0xc) == 1) goto LAB_43793978;
          }
        }
        else {
          FUN_4380c7f8(uVar1,auStack_40);
          iVar46 = DAT_43794318;
          if (((bVar56) && (uVar48 = bStack_3c & 0x20, (bStack_3c & 0x20) == 0)) &&
             (*(int *)(DAT_43794318 + 0x43794132) != 0)) {
            FUN_4378ea78(uVar48);
            *(uint *)(iVar46 + 0x43794132) = uVar48;
            *(uint *)(iVar46 + 0x43794142) = uVar48;
          }
        }
      }
      else {
        FUN_4378ea78(0);
        *(undefined4 *)(iVar46 + 0x43793fe6) = 0;
        *(undefined4 *)(iVar46 + 0x43793ff6) = 0;
        *(byte *)(iVar46 + 0x4379401e) = *(byte *)(iVar46 + 0x4379401e) & 0xfe;
      }
    }
    else {
      uVar53 = *(int *)(*(int *)(DAT_437942f8 + 0x43793876) + 0x1e8) + 1;
      if (uVar48 <= uVar53) {
        if (uVar48 == uVar53) {
          iVar49 = FUN_43b039fc(DAT_437942fc + 0x43793892,DAT_43794300 + 0x43793894);
          if (iVar49 == 0) {
            *(undefined4 *)(iVar46 + 0x43793ff6) = *(undefined4 *)(iVar46 + 0x43793fe6);
            FUN_4378ea78();
          }
        }
        else {
          FUN_4378ea78(0);
          iVar49 = *(int *)(*(int *)(iVar49 + 0x43793872) + 0x3c) + -1;
          *(int *)(iVar46 + 0x43793fe6) = iVar49;
          *(int *)(iVar46 + 0x43793ff6) = iVar49;
        }
      }
    }
  }
  iVar46 = DAT_43794324;
  uVar48 = *(uint *)(DAT_4379431c + 0x43793ece);
  if (*(byte *)(iVar44 + 1) - 1 < 4) {
                    /* WARNING: Could not recover jumptable at 0x437939ca. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_437939ca::switchdataD_437939ce +
              (uint)*(byte *)(*(byte *)(iVar44 + 1) + 0x437939cd) * 2))();
    return;
  }
  if (((uint)*(byte *)(DAT_43794320 + 0x43794150) != (uVar48 & 3) >> 1) ||
     ((uint)*(byte *)(DAT_43794320 + 0x43794151) != (uVar48 & 1))) {
    *(byte *)(DAT_43794324 + 0x4379416a) = (byte)((uVar48 << 0x1e) >> 0x1f);
    *(char *)(iVar46 + 0x4379416b) = (char)(uVar48 & 1);
    FUN_4378ea78(0);
  }
  iVar44 = FUN_43ae8d4e();
  if ((iVar44 == 0) || (*(char *)(DAT_43794328 + 0x43793a22) != '\0')) {
    FUN_4378ea78(1);
    *(undefined1 *)(DAT_4379432c + 0x43793a34) = 0;
  }
  uVar14 = *(undefined4 *)(iVar43 + DAT_43794330);
  iVar44 = FUN_43ae8cc8(uVar14);
  if (iVar44 != 0) {
    *(undefined4 *)(DAT_43794334 + 0x437941e6) = *(undefined4 *)(DAT_43794334 + 0x437941d6);
  }
  iVar44 = DAT_43794338;
  uVar48 = *(uint *)(DAT_43794338 + 0x437941e6);
  cVar33 = '\x01' - (char)uVar48;
  if (1 < uVar48) {
    cVar33 = '\0';
  }
  *(bool *)(DAT_43794338 + 0x437941ea) = 1 >= uVar48;
  *(char *)(iVar44 + 0x437941eb) = cVar33;
  cVar33 = '\x01' - (char)*(uint *)(iVar44 + 0x437941f6);
  if (1 < *(uint *)(iVar44 + 0x437941f6)) {
    cVar33 = '\0';
  }
  *(char *)(iVar44 + 0x437941fa) = cVar33;
  uVar32 = FUN_43ae8ccc(uVar14);
  *(undefined1 *)(iVar44 + 0x4379553b) = uVar32;
  if ((*(byte *)(iVar44 + 0x43794264) & 0x10) == 0) {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_43794340 + 0x43793abc) + 4);
  }
  else {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_4379433c + 0x43793ab0) + 0xc);
  }
  iVar44 = FUN_43b00cba(uVar13);
  if ((iVar44 != 0) && (*(int *)(*(int *)(DAT_43794344 + 0x43793ac6) + 0xb8) == 1)) {
    FUN_43b00e4c(uVar13,(int *)(DAT_43794344 + 0x43793ac6),&uStack_30);
  }
  iVar46 = DAT_4379434c;
  iVar44 = DAT_43794348;
  uVar13 = FUN_4380e15c(DAT_43794348 + 0x43793ae4,uStack_30,DAT_43794350 + 0x43793b00,
                        *(int *)(DAT_4379434c + 0x43794276) +
                        *(int *)(*(int *)(DAT_43794348 + 0x43793ae8) + 0xc) & 1);
  *(undefined4 *)(iVar46 + 0x437940ca) = uVar13;
  iVar49 = FUN_437955ec();
  iVar39 = *(int *)(iVar43 + DAT_43794354);
  if (iVar49 == 1) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    if (*(char *)(iVar46 + 0x4379428a) != '\0') {
      *(char *)(iVar46 + 0x43794282) = *(char *)(iVar46 + 0x43794282) + '\x01';
    }
  }
  else if (iVar49 == 2) {
    if (((*(byte *)(iVar39 + 0x22) & 1) == 0) &&
       (uVar48 = *(uint *)(*(int *)(iVar44 + 0x43793af0) + 8), *(ushort *)(iVar46 + 0x4379415a) < 2)
       ) {
      if (*(char *)(iVar46 + 0x4379427b) == '\0') {
        iVar44 = *(int *)(iVar46 + 0x437940ba);
      }
      else {
        iVar44 = *(int *)(iVar46 + 0x437940ca);
      }
      if (iVar44 != 0) {
        if (iVar44 == 1) {
          uVar53 = 1;
        }
        else {
          uVar53 = 2;
        }
        if (uVar48 < uVar53) {
          uVar48 = uVar53;
        }
      }
      if ((1 < uVar48) &&
         (uVar48 = FUN_43acf19e(uVar48,2),
         (*(int *)((int)&DAT_43794338 + DAT_4379435c) +
          *(int *)(*(int *)(DAT_43794358 + 0x43793b9e) + 0xc) & 1U) != 0)) {
        uVar48 = 1;
      }
      *(uint *)((int)&DAT_43794348 + DAT_43794360 + 2) = uVar48;
    }
    else {
      *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    }
    if (*(char *)((int)&DAT_43794360 + DAT_43794364) != '\0') {
      *(char *)((int)&DAT_43794358 + DAT_43794364) =
           *(char *)((int)&DAT_43794358 + DAT_43794364) + '\x01';
    }
  }
  else if (iVar49 == 0) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
  }
  iVar44 = DAT_43794368;
  if (*(int *)(DAT_43794368 + 0x437941be) != 0x11) {
    uVar13 = *(undefined4 *)((int)&DAT_43794338 + DAT_43794368 + 2);
    if (*(int *)((int)&DAT_437943d4 + DAT_43794368 + 2) != 0) {
      uVar13 = 10;
    }
    uVar13 = FUN_43acc1a6(*(int *)(DAT_43794368 + 0x437941be),uVar13);
    *(undefined4 *)((int)&DAT_4379433c + iVar44 + 2) = uVar13;
  }
  iVar46 = DAT_4379436c + 0x43793bfc;
  iVar44 = *(int *)(DAT_4379436c + 0x437941e4);
  if ((iVar44 == 0x12) || (iVar44 == 0x3f)) {
    uVar13 = 1;
    iVar46 = DAT_43794370 + 0x43793c18;
  }
  else if (iVar44 == 8) {
    uVar13 = 2;
  }
  else {
    uVar13 = *(undefined4 *)(*(int *)(iVar43 + DAT_43794374) + 0x40);
  }
  *(undefined4 *)(iVar46 + 0x5a4) = uVar13;
  if (*(char *)(*(int *)(iVar43 + DAT_43794378) + 0x43) == '\x01') {
    iVar44 = DAT_4379437c + 0x43793c3a;
    bVar34 = 1;
  }
  else {
    bVar34 = 0;
    if (*(char *)(DAT_43794380 + 0x43793d1e) != '\0') {
      bVar34 = (byte)FUN_43795a08[DAT_43794380 + 2] ^ 1;
    }
    iVar44 = DAT_43794384 + 0x43793c58;
  }
  *(byte *)(iVar44 + 0x770) = bVar34;
  if (*(char *)(DAT_43794388 + 0x43795a2a) == '\0') {
    uVar13 = *(undefined4 *)(*(int *)(DAT_4379438c + 0x43793c74) + 0xbc);
  }
  else {
    uVar13 = 1;
  }
  *(undefined4 *)((int)&DAT_437943d4 + DAT_43794388 + 2) = uVar13;
  cVar33 = *(char *)(DAT_43794390 + 0x43794258);
  if (*(char *)((int)&DAT_43794414 + DAT_43794390 + 1) != '\0') {
    cVar33 = cVar33 + '\x01';
  }
  *(char *)(DAT_43794390 + 0x43794269) = cVar33;
  uVar13 = FUN_43ae8d10(uVar14);
  iVar44 = DAT_43794394;
  piVar52 = (int *)(DAT_43794398 + 0x43793ca6);
  *(undefined4 *)(DAT_43794394 + 0x43794510) = uVar13;
  uVar13 = FUN_43ae8d14(uVar14);
  iVar46 = *piVar52;
  *(undefined4 *)(iVar44 + 0x43794514) = uVar13;
  piVar50 = (int *)(DAT_4379439c + 0x43793cbc);
  if (*piVar50 != iVar46) {
    FUN_43901a8c(4,0x203d);
    *piVar52 = *piVar50;
  }
  iVar40 = DAT_437943ac;
  iVar49 = DAT_437943a8;
  iVar46 = DAT_437943a4;
  iVar44 = DAT_437943a0;
  if ((*(byte *)(iVar39 + 3) & 1) != 0) {
    puVar45 = (undefined2 *)(DAT_437943a4 + 0x43793cec);
    puVar37 = (undefined4 *)(DAT_437943a8 + 0x43793cf4);
    uVar26 = *(undefined4 *)(DAT_437943a4 + 0x43794478);
    puVar54 = (undefined4 *)(DAT_437943ac + 0x43793cfa);
    uVar13 = *(undefined4 *)((int)&DAT_437942cc + DAT_437943a4);
    uVar36 = **(undefined4 **)(DAT_437943a0 + 0x43793cea);
    uVar41 = (*(undefined4 **)(DAT_437943a0 + 0x43793cea))[3];
    uVar55 = *(undefined4 *)((int)&DAT_437942bc + DAT_437943a4);
    uVar15 = FUN_437955ec();
    uVar27 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar46 + 0x43794488);
    iVar18 = *(int *)(iVar44 + 0x43793cea);
    uVar28 = *(undefined4 *)(iVar18 + 0x10);
    uVar29 = *(undefined4 *)(iVar18 + 0x30);
    uVar19 = *(undefined4 *)(iVar18 + 0x3c);
    uVar12 = *puVar45;
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar20 = *puVar37;
    uVar30 = *puVar54;
    uVar21 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar31 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar22 = FUN_43ae8cd0(uVar14);
    uVar23 = FUN_43ae8cc8(uVar14);
    uVar24 = FUN_43ae8ccc(uVar14);
    FUN_4378eb78(3,9,1,DAT_437943b0 + 0x43793dcc,uVar36,uVar41,uVar55,uVar13,uVar26,uVar15,uVar16,
                 uVar27,uVar17,uVar28,uVar29,uVar19,uVar12,uVar2,uVar20,uVar30,uVar21,uVar31,uVar22,
                 uVar23,uVar24);
    uVar22 = *(undefined4 *)((int)&DAT_437942bc + iVar46);
    uVar26 = *(undefined4 *)((int)&DAT_437942cc + iVar46);
    uVar13 = **(undefined4 **)(iVar44 + 0x43793cea);
    uVar28 = (*(undefined4 **)(iVar44 + 0x43793cea))[3];
    uVar29 = *(undefined4 *)(iVar46 + 0x43794478);
    uVar15 = FUN_437955ec();
    iVar44 = *(int *)(iVar44 + 0x43793cea);
    uVar23 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar27 = *(undefined4 *)(iVar46 + 0x43794488);
    uVar55 = *puVar54;
    uVar24 = *(undefined4 *)(iVar44 + 0x10);
    uVar12 = *puVar45;
    uVar41 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar44 + 0x30);
    uVar30 = *(undefined4 *)(iVar44 + 0x3c);
    uVar31 = *puVar37;
    uVar36 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar19 = FUN_43ae8cd0(uVar14);
    uVar20 = FUN_43ae8cc8(uVar14);
    uVar21 = FUN_43ae8ccc(uVar14);
    FUN_43902718(DAT_437943b4 + 0x43793e92,uVar13,uVar28,uVar22,uVar26,uVar29,uVar15,uVar16,uVar23,
                 uVar27,uVar24,uVar17,uVar30,uVar12,uVar2,uVar31,uVar55,uVar36,uVar41,uVar19,uVar20,
                 uVar21);
  }
  iVar46 = DAT_437943c4;
  iVar44 = DAT_437943c0;
  uVar13 = FUN_43b039fc(DAT_437943b8 + 0x43793ea0,DAT_437943bc + 0x43793ea6);
  iVar49 = iVar44 + 0x43795d1c;
  FUN_43780080(iVar46 + 0x43793eb6,iVar49,uVar13);
  FUN_4380db04(iVar46 + 0x43793eb6,iVar49);
  FUN_4378c4d0(iVar44 + 0x43794454);
  FUN_4378f7a0(0xb2a);
  iVar44 = FUN_43ae8cd0(uVar14);
  if (iVar44 == 0) {
    FUN_43ae8cda(uVar14);
  }
  iVar46 = DAT_437943cc;
  iVar44 = DAT_437943c8;
  iVar49 = DAT_437943c8 + 0x43793ef4;
  iVar40 = DAT_437943cc + 0x43793ef8;
  FUN_4377e0e8(iVar49);
  FUN_437217f8(*(undefined4 *)(*(int *)(iVar44 + 0x43793ef8) + 0x18));
  FUN_437b4db8(iVar49,iVar46 + 0x43795188);
  FUN_437c194c(iVar49,iVar46 + 0x43795628);
  thunk_FUN_437d0e5c(iVar49,(int)&DAT_437957cc + iVar46);
  FUN_4378f754(iVar40,iVar46 + 0x437959d4);
  FUN_43af6784((int)&DAT_43795888 + iVar46,iVar49);
  FUN_4378f7a0(0xb51);
  pcVar42 = *(char **)(iVar44 + 0x43793f08);
  if (*pcVar42 == '\0') {
    uVar13 = 0;
    if (*(char *)(iVar39 + 0xec) == '\0') {
      uVar13 = *(undefined4 *)(pcVar42 + 4);
    }
  }
  else {
    uVar13 = 0;
  }
  uVar14 = FUN_43814138();
  iVar44 = DAT_437943d0;
  iVar46 = FUN_43799a38(1,1,**(undefined4 **)(DAT_437943d0 + 0x43793f68),0);
  if (iVar46 == 0) {
    iVar44 = FUN_43799a38(1,2,**(undefined4 **)(iVar44 + 0x43793f68),0);
    bVar56 = iVar44 != 0;
  }
  else {
    bVar56 = true;
  }
  uVar13 = FUN_43b03c62(uVar14,uVar13,bVar56);
  *(undefined4 *)(FUN_43794784 + DAT_437943d4 + 4) = uVar13;
  iVar44 = DAT_437943d8;
  if ((*(char *)(iVar39 + 0xed) == '\0') &&
     ((iVar46 = *(int *)(*(int *)(iVar43 + DAT_43794374) + 0x44), iVar46 == 3 || (iVar46 == 4)))) {
    if ((*(ushort *)(*(int *)(DAT_437943d8 + 0x43793fc8) + 0x264) & 0x1ff) >> 6 != 0) {
      uVar13 = FUN_438148f0();
      iVar46 = DAT_437943e0 + 0x43794058;
      uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
      goto LAB_4379405e;
    }
    iVar46 = DAT_437943dc + 0x43793fdc;
    auStack_48[0] = *(undefined1 *)(DAT_437943dc + 0x4379481a);
    uStack_44 = *(undefined4 *)(&UNK_4379459c + DAT_437943dc);
    thunk_FUN_438aaab8(auStack_48,auStack_3a8);
    uVar13 = FUN_438148f0();
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
    puVar58 = auStack_348;
    puVar35 = auStack_3a8;
    puVar59 = auStack_2e0;
    puVar60 = auStack_280;
  }
  else {
    uVar13 = FUN_438148f0();
    iVar46 = DAT_43794630 + 0x437945e4;
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(DAT_4379462c + 0x437945e6),0);
LAB_4379405e:
    puVar35 = (undefined1 *)0x0;
    uStack_2e8 = 0;
    puVar58 = (undefined1 *)0x0;
    uStack_2e4 = 0;
    puVar59 = (undefined1 *)0x0;
    uStack_220 = 0;
    puVar60 = (undefined1 *)0x0;
    uStack_21c = 0;
  }
  FUN_4381493c(&uStack_3b8,uVar13,puVar35,uStack_2e8,puVar58,uStack_2e4,puVar59,uStack_220,puVar60,
               uStack_21c,uVar14);
  iVar44 = DAT_437943e8;
  iVar49 = DAT_437943e4 + 0x4379408a;
  *(undefined4 *)(iVar46 + 0x7f0) = uStack_3b8;
  *(undefined4 *)(iVar46 + 0x7f4) = uStack_3b4;
  *(undefined4 *)(iVar46 + 0x7f8) = uStack_3b0;
  *(undefined4 *)(iVar46 + 0x7fc) = uStack_3ac;
  iVar46 = DAT_437943ec;
  FUN_43ae8faa(iVar49,DAT_437943ec + 0x43794096);
  FUN_43ae8eae(iVar49,iVar44 + 0x43794090);
  if ((*(uint *)(iVar46 + 0x4379489a) & 4) == 0) {
    FUN_43560da8(0x11,4);
    FUN_43ae9148(auStack_7c,DAT_437943f0 + 0x437940bc);
    FUN_437b4f2c(iVar44 + 0x43794090,auStack_7c,4);
  }
  if ((*(uint *)(DAT_437943f4 + 0x437948d2) & 2) == 0) {
    FUN_43560da8(0x11,2);
    FUN_43ae9148(auStack_90,DAT_437943f8 + 0x437940e6);
    FUN_437c297c(DAT_437943fc + 0x437940f2,auStack_90,2);
  }
  if ((*(uint *)(DAT_43794400 + 0x437948fe) & 0x80) == 0) {
    FUN_43560da8(0x11,0x80);
    FUN_43ae9148(auStack_a4,DAT_43794404 + 0x43794112);
    FUN_437b66e0(DAT_43794408 + 0x4379411e,auStack_a4,0x80);
  }
  if ((*(uint *)(DAT_4379440c + 0x4379492a) & 8) == 0) {
    FUN_43560da8(0x11,8);
    FUN_43ae9148(auStack_b8,DAT_43794410 + 0x4379413e);
    FUN_4379fd58(DAT_43794414 + 0x4379414a,auStack_b8,8);
  }
  if ((*(uint *)(DAT_43794418 + 0x43794956) & 0x40) == 0) {
    FUN_43560da8(0x11,0x40);
    FUN_43ae9148(auStack_cc,DAT_4379441c + 0x4379416a);
    FUN_437d9e00(DAT_43794420 + 0x43794176,auStack_cc,0x40);
  }
  if ((*(uint *)(DAT_43794424 + 0x43794982) & 0x20) == 0) {
    FUN_43560da8(0x11,0x20);
    FUN_43ae9148(auStack_e0,DAT_43794428 + 0x43794196);
    FUN_437d0c90(DAT_4379442c + 0x437941a2,auStack_e0,0x20);
  }
  if ((*(uint *)((int)&DAT_437949ac + DAT_43794430 + 2) & 0x200) == 0) {
    FUN_43560da8(0x11,0x200);
    uVar13 = FUN_4378dd84();
    FUN_43ae9148(auStack_f4,DAT_43794434 + 0x437941c6);
    FUN_437b82d8(DAT_43794438 + 0x437941d6,uVar13,auStack_f4,0x200);
  }
  iVar44 = DAT_43794448;
  bVar56 = (*(byte *)((int)&DAT_437949ec + DAT_4379443c + 2) & 0x40) != 0;
  if (bVar56) {
    iVar46 = *(int *)(*(int *)(DAT_43794444 + 0x43794204) + 0x10);
  }
  else {
    iVar46 = *(int *)(*(int *)(DAT_43794440 + 0x437941f8) + 0x10);
  }
  psVar38 = (short *)(DAT_43794448 + 0x4379420e);
  thunk_FUN_43721e60(!bVar56,iVar46 == 3);
  if (*(int *)(iVar44 + 0x43794822) == 0) {
    if ((*(byte *)(iVar44 + 0x43794a1a) & 0x40) != 0) {
      FUN_43795bf0();
      goto LAB_437944b8;
    }
    FUN_43ae93ce();
    uVar32 = 0;
  }
  else {
    if (uVar1 == 0x103) {
      if (*psVar38 != 0x14a) goto LAB_437944be;
      FUN_43ae93dc();
      FUN_4378f3f8(1);
      uVar32 = 1;
LAB_437944a2:
      *(undefined1 *)((int)&DAT_437949f4 + iVar44 + 2) = uVar32;
      goto LAB_437944be;
    }
    if (uVar1 < 0x104) {
      if (uVar1 < 0x100) goto LAB_437944be;
      if (uVar1 < 0x102) {
        if (1 < (ushort)(*psVar38 - 0x105U)) goto LAB_437944be;
        FUN_43795c14();
        uVar32 = 0;
        goto LAB_437944ba;
      }
    }
    else {
      if (uVar1 == 0x10e) {
        sVar25 = *psVar38;
        if (((((sVar25 == 0x102) || (sVar25 == 0x107)) || (sVar25 == 0x11a)) ||
            ((sVar25 == 0x11b || (sVar25 == 0x118)))) || ((sVar25 == 0x119 || (sVar25 == 0x132)))) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
        }
        goto LAB_437944be;
      }
      if (uVar1 < 0x10f) {
        if (uVar1 != 0x107) goto LAB_437944be;
      }
      else if (uVar1 != 0x132) {
        if ((uVar1 != 0x14a) || (1 < (ushort)(*psVar38 - 0x102U))) goto LAB_437944be;
        FUN_43ae93ea();
        FUN_4378f3f8(0);
        FUN_436d6118();
        FUN_43ad913e();
        uVar32 = 0;
        goto LAB_437944a2;
      }
    }
    if (*(short *)(DAT_437945fc + 0x437944ae) != 0x10e) goto LAB_437944be;
    FUN_43ae93dc();
LAB_437944b8:
    uVar32 = 1;
  }
LAB_437944ba:
  FUN_4378f3f8(uVar32);
LAB_437944be:
  if ((*(char *)(iVar39 + 0x70) == '\0') && (iVar44 = FUN_437999e4(1,0xe), iVar44 != 0)) {
    FUN_43b71948();
  }
  if ((**(uint **)(DAT_43794600 + 0x437944dc) & 0xfffff) == 0) {
    FUN_43728be0();
  }
  FUN_4378f7a0(0xc39);
  if (*(char *)(iVar39 + 0xbf) != '\0') {
    FUN_43ae9124(auStack_108,*(undefined4 *)(iVar43 + DAT_43794604));
    FUN_439018b0(DAT_43794608 + 0x4379450a,auStack_108,2,0);
  }
  iVar43 = DAT_4379460c;
  FUN_43560da8(0x1a,0x40);
  FUN_43ae129a(4);
  if (param_1 != **(int **)(iVar43 + 0x4379451c)) {
    iVar44 = thunk_FUN_436cd00c();
    uVar48 = (uint)(iVar44 - (*(undefined4 **)(iVar43 + 0x4379451c))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43794610 + 0x4379454c,param_1,**(undefined4 **)(iVar43 + 0x4379451c),
                 uVar48);
    FUN_43902718(DAT_43794614 + 0x4379455a,param_1,**(undefined4 **)(iVar43 + 0x4379451c),uVar48);
    FUN_4378f988(4,0,uVar48);
    if ((*(byte *)(iVar39 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43794618 + 0x43794578);
    }
    if ((*(byte *)(iVar39 + 0x1b) & 2) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(byte *)(iVar39 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_4379461c + 0x43794598);
  }
  return;
}


/* 436d6f34 */

undefined * FUN_436d6f34(int param_1,uint param_2)

{
  if (param_2 < *(uint *)(param_1 + 4)) {
    return (undefined *)(param_2 * 0x30 + *(int *)(param_1 + 0x18));
  }
  return &UNK_436d6f4a + DAT_436d6f4c;
}


/* 43ad9a40 */

void FUN_43ad9a40(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4,
                 undefined1 param_5,undefined1 param_6)

{
  *(undefined2 *)(param_1 + 0x50) = param_2;
  *(undefined2 *)(param_1 + 0x52) = param_3;
  *(undefined2 *)(param_1 + 0x54) = param_4;
  *(undefined1 *)(param_1 + 0x57) = param_5;
  *(undefined1 *)(param_1 + 0x56) = param_6;
  return;
}


/* 43ad99d4 */

void FUN_43ad99d4(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined1 uStack_5;
  
  *(char *)(param_1 + 0x11) = (char)param_2;
  *(char *)(param_1 + 0x13) = (char)((uint)param_2 >> 0x10);
  *(char *)(param_1 + 0x15) = (char)param_3;
  uStack_5 = (undefined1)((uint)param_3 >> 0x18);
  *(char *)(param_1 + 0x10) = (char)((uint)param_2 >> 8);
  *(char *)(param_1 + 0x12) = (char)((uint)param_2 >> 0x18);
  *(char *)(param_1 + 0x14) = (char)((uint)param_3 >> 8);
  *(undefined1 *)(param_1 + 0x16) = uStack_5;
  return;
}

