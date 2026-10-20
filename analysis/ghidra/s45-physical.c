/* S41: read-only exports. */

/* 436c74c8 */

ulonglong FUN_436c74c8(int *param_1,uint param_2,int param_3,int param_4,char param_5,char param_6,
                      char param_7,int param_8,int param_9,undefined1 param_10,int *param_11,
                      int *param_12)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 extraout_r1;
  int iVar5;
  int iVar6;
  uint uVar7;
  int *piVar8;
  int iVar9;
  bool bVar10;
  
  iVar9 = DAT_436c7808;
  iVar3 = param_12[1];
  iVar5 = param_12[2];
  iVar6 = param_12[3];
  param_1[0x14] = *param_12;
  param_1[0x15] = iVar3;
  param_1[0x16] = iVar5;
  param_1[0x17] = iVar6;
  param_1[0x18] = param_12[4];
  iVar3 = param_11[1];
  iVar5 = param_11[2];
  iVar6 = param_11[3];
  param_1[0x19] = *param_11;
  param_1[0x1a] = iVar3;
  param_1[0x1b] = iVar5;
  param_1[0x1c] = iVar6;
  param_1[0x1d] = param_11[4];
  FUN_43ad3b42(param_1,0);
  FUN_43ad3b7e(param_1,param_10);
  FUN_43ad3b56(param_1,param_10);
  if (((((param_1[8] == param_2) && ((uint)param_1[8] < 3)) && (param_1[0xb] == param_8)) &&
      ((param_1[0xc] == param_9 && (param_1[0xd] == param_3 + -1)))) &&
     (param_1[0xe] == param_4 + -1)) {
    uVar1 = 0;
    goto LAB_436c77f4;
  }
  param_1[8] = param_2;
  param_1[0xb] = param_8;
  param_1[0xc] = param_9;
  param_1[0xd] = param_3 + -1;
  uVar1 = DAT_436c7800;
  param_1[0xe] = param_4 + -1;
  uVar1 = FUN_43ad3868(uVar1);
  switch(param_2) {
  case 1:
    uVar7 = param_1[0xb];
    if (1 < uVar7) {
      thunk_FUN_43b4a69c(0x2034,2);
    }
    thunk_FUN_43b4a69c(0x2038,1 < uVar7);
    FUN_43560e1c(0x13);
    if (param_1[9] == 0) {
      iVar9 = 1;
    }
    else {
      iVar9 = 1 - param_1[10];
      if (1 < (uint)param_1[10]) {
        iVar9 = 0;
      }
    }
    FUN_43ad387a(DAT_436c7800,iVar9,1,uVar1);
    iVar9 = 1 - param_1[9];
    if (1 < (uint)param_1[9]) {
      iVar9 = 0;
    }
    FUN_43ad384c(0xf3000000,iVar9,1,uVar1);
    iVar9 = 1 - param_1[10];
    if (1 < (uint)param_1[10]) {
      iVar9 = 0;
    }
    FUN_43ad384c(DAT_436c7804,iVar9,1,uVar1);
    FUN_43560e38(0x13);
    goto LAB_436c7646;
  case 2:
    if ((uint)(param_1[0xe] * param_1[0xd]) <
        (uint)(**(int **)(iVar9 + 0x436c7502 + DAT_436c780c) * 6000)) {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
    thunk_FUN_43b4a69c(0x2034,uVar4);
    thunk_FUN_43b4a69c(0x2038,1);
    FUN_43ad387a(DAT_436c7800,0,1,uVar1);
    iVar9 = thunk_FUN_43b4a694(0x2034);
    FUN_43ad384c(0xf3000000,0,iVar9 != 2,uVar1);
    iVar9 = thunk_FUN_43b4a694(0x2034);
    bVar10 = iVar9 != 2;
    break;
  case 3:
    FUN_436c72e4();
    FUN_43ad381e(0xf3000000);
    FUN_43ad381e(DAT_436c7804);
    uVar1 = FUN_43acee62(param_1 + 1);
    FUN_43ad2bbc(uVar1,1);
    uVar1 = FUN_43acee62(param_1 + 1);
    uVar4 = 0;
    goto LAB_436c7732;
  case 4:
    FUN_436c72e4();
    FUN_43ad381e(0xf3000000);
    FUN_43ad381e(DAT_436c7804);
    uVar1 = FUN_43acee62(param_1 + 1);
    FUN_43ad2bbc(uVar1,0);
    uVar1 = FUN_43acee62(param_1 + 1);
    uVar4 = 1;
LAB_436c7732:
    FUN_43ad2bfc(uVar1,uVar4);
    uVar1 = FUN_43acee62(param_1 + 1);
    FUN_43ad2be0(uVar1,param_1[0xd]);
    iVar9 = 0;
    goto LAB_436c7744;
  default:
    uVar7 = param_1[0xb];
    if (1 < uVar7) {
      thunk_FUN_43b4a69c(0x2034,2);
    }
    thunk_FUN_43b4a69c(0x2038,1 < uVar7);
    FUN_43ad387a(DAT_436c7800,0,1,uVar1);
    FUN_43ad384c(0xf3000000,0,1,uVar1);
    bVar10 = true;
  }
  FUN_43ad384c(DAT_436c7804,0,bVar10,uVar1);
LAB_436c7646:
  piVar8 = param_1 + 1;
  iVar9 = 1;
  uVar1 = FUN_43acee62(piVar8);
  FUN_43ad2bbc(uVar1,0);
  uVar1 = FUN_43acee62(piVar8);
  FUN_43ad2bfc(uVar1,0);
  uVar1 = FUN_43acee62(piVar8);
  FUN_43ad2be0(uVar1,param_1[0xd] + -100);
LAB_436c7744:
  piVar8 = param_1 + 1;
  uVar1 = FUN_43acee62(piVar8);
  FUN_43ad2bd6(uVar1,param_1[0xe],param_1[0xd]);
  if ((param_6 == '\0') || (param_7 == '\0')) {
    uVar1 = FUN_43acee62(piVar8);
    FUN_43ad3982(uVar1,0);
  }
  else {
    uVar1 = FUN_43acee62(piVar8);
    FUN_43ad3990(uVar1,1,(int)param_5 + param_1[0xd]);
    uVar1 = FUN_43acee62(piVar8);
    FUN_43ad39a0(uVar1,param_6,param_7);
  }
  iVar3 = param_1[0xc];
  if (iVar3 == 0) {
    uVar2 = FUN_43acee62(piVar8);
    uVar4 = 0x3ffe;
    uVar1 = 0x3ffe;
  }
  else {
    iVar5 = FUN_436c28d0();
    iVar3 = iVar3 * iVar5;
    uVar2 = FUN_43acee62(piVar8);
    uVar4 = FUN_4355faf0(iVar3,param_3);
    FUN_4355fd4c(iVar3,param_3);
    uVar1 = extraout_r1;
  }
  FUN_43ad3952(uVar2,uVar4,uVar1);
  if ((iVar9 == 0) && (iVar3 = (**(code **)(*param_1 + 0x14))(param_1), iVar3 != 0)) {
    uVar1 = 0x108;
  }
  else {
    uVar1 = 0;
  }
  uVar4 = FUN_43acee62(piVar8);
  FUN_43ad390c(uVar4,1,iVar9,0);
LAB_436c77f4:
  return (ulonglong)CONCAT14(param_7,uVar1);
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


/* 43842158 */

void FUN_43842158(int param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  ushort uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  
  uVar2 = *(ushort *)(param_3 + 0x4bc);
  iVar8 = DAT_43842340 + 0x43842170;
  if (((uVar2 & 0x60) == 0) && ((uVar2 & 0x80) == 0)) {
    if (*(int *)(param_3 + 0x41c) == 1) {
      uVar3 = 1;
      if (*(char *)(param_4 + 2) == '\0') {
        if (*(ushort *)(param_2 + 0x162) <= **(ushort **)(iVar8 + DAT_43842350)) {
          iVar5 = DAT_43842358 + 0x438421c4;
          goto LAB_438421e6;
        }
        iVar5 = DAT_43842354 + 0x438421be;
      }
      else if (*(char *)(param_4 + 2) == '\x01') {
        if (*(char *)(param_3 + 0x38c) != '\x01') {
          iVar5 = DAT_43842360 + 0x438421dc;
          goto LAB_438421e6;
        }
        iVar5 = DAT_4384235c + 0x438421d6;
        uVar3 = 1;
      }
      else {
        iVar5 = DAT_43842364 + 0x438421e2;
      }
    }
    else {
      iVar5 = DAT_43842368 + 0x438421e8;
LAB_438421e6:
      uVar3 = 3;
    }
  }
  else if (((uVar2 & 0x20) == 0) ||
          ((uVar2 = *(ushort *)(*(int *)(iVar8 + DAT_43842344) + 0xb0), uVar2 == 0 ||
           (*(ushort *)(param_2 + 0x162) <= uVar2)))) {
    uVar3 = 1;
    iVar5 = DAT_4384234c + 0x4384219e;
  }
  else {
    uVar3 = 5;
    iVar5 = DAT_43842348 + 0x43842196;
  }
  *(undefined4 *)(iVar5 + 0x60) = uVar3;
  iVar5 = *(int *)(iVar8 + DAT_4384236c);
  cVar1 = *(char *)(iVar5 + 0x7e);
  if (cVar1 != '\0') {
    if (cVar1 == '\x01') {
      uVar3 = 0;
      iVar6 = DAT_43842370 + 0x43842204;
    }
    else if (cVar1 == '\x02') {
      iVar6 = DAT_43842374 + 0x4384220e;
LAB_4384225a:
      uVar3 = 1;
    }
    else if (cVar1 == '\x03') {
      uVar3 = 2;
      iVar6 = DAT_43842378 + 0x4384221a;
    }
    else if (cVar1 == '\x04') {
      uVar3 = 3;
      iVar6 = DAT_4384237c + 0x43842226;
    }
    else if (cVar1 == '\x05') {
      uVar3 = 4;
      iVar6 = DAT_43842380 + 0x43842232;
    }
    else if (cVar1 == '\x06') {
      uVar3 = 5;
      iVar6 = DAT_43842384 + 0x4384223e;
    }
    else if (cVar1 == '\a') {
      uVar3 = 6;
      iVar6 = DAT_43842388 + 0x4384224a;
    }
    else {
      if (cVar1 != '\b') {
        iVar6 = DAT_43842390 + 0x4384225c;
        goto LAB_4384225a;
      }
      uVar3 = 7;
      iVar6 = DAT_4384238c + 0x43842256;
    }
    *(undefined4 *)(iVar6 + 0x60) = uVar3;
  }
  if ((*(char *)(param_4 + 2) != '\x01') || (uVar4 = 1, *(char *)(param_3 + 0x38c) != '\0')) {
    uVar4 = 0;
  }
  FUN_43841aac(uVar4);
  if (*(int *)(param_3 + 0x41c) == 1) {
    iVar6 = DAT_43842394 + 0x4384227e;
LAB_43842290:
    *(undefined1 *)(iVar6 + 100) = 1;
  }
  else {
    iVar6 = DAT_43842398 + 0x43842286;
    *(undefined1 *)(DAT_43842398 + 0x438422ea) = 0;
    if (*(char *)(iVar5 + 0x10f) == '\x01') goto LAB_43842290;
  }
  if (((*(char *)(iVar5 + 0xf9) != '\x01') ||
      (iVar6 = DAT_4384239c + 0x438422a2, *(int *)(DAT_4384239c + 0x43842302) != 3)) ||
     (uVar4 = 1, *(ushort *)(param_2 + 0x162) < *(ushort *)(iVar5 + 0xfc))) {
    uVar4 = 0;
    iVar6 = DAT_438423a0 + 0x438422ba;
  }
  *(undefined1 *)(iVar6 + 0x65) = uVar4;
  iVar5 = DAT_438423a4;
  if (*(char *)(param_1 + 0x36) == '\x01') {
    *(undefined1 *)(DAT_438423a4 + 0x43842331) = 0;
    *(undefined1 *)(iVar5 + 0x43842330) = 0;
    uVar7 = (uint)*(byte *)(param_1 + 0x37);
    if (uVar7 == 0) {
      *(undefined4 *)(iVar5 + 0x4384232c) = 1;
    }
    else {
      if (uVar7 == 1) {
        uVar7 = 3;
      }
      else if (uVar7 != 2) {
        if (uVar7 == 3) {
          *(undefined4 *)(iVar5 + 0x4384232c) = 0;
          goto LAB_43842306;
        }
        if (((uVar7 != 4) && (uVar7 != 5)) && (uVar7 != 6)) {
          if (uVar7 == 7) {
            uVar7 = 7;
          }
          else {
            uVar7 = 1;
          }
        }
      }
      *(uint *)(iVar5 + 0x4384232c) = uVar7;
    }
  }
LAB_43842306:
  iVar5 = DAT_438423a8;
  uVar4 = *(undefined1 *)((int)&DAT_4384236c + DAT_438423a8 + 2);
  *(undefined1 *)(*(int *)(iVar8 + DAT_438423ac) + 0x9b4) = uVar4;
  **(undefined1 **)(iVar8 + DAT_438423b0) = uVar4;
  **(undefined1 **)(iVar8 + DAT_438423b4) = (char)*(undefined4 *)(param_3 + 0x41c);
  uVar4 = *(undefined1 *)((int)&DAT_43842370 + iVar5 + 3);
  **(undefined1 **)(iVar8 + DAT_438423b8) = *(undefined1 *)((int)&DAT_43842370 + iVar5 + 2);
  **(undefined1 **)(iVar8 + DAT_438423bc) = uVar4;
  return;
}

