/* S41: read-only exports. */

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

