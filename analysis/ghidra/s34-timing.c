/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814ea0" */

void FUN_43814ea0(int param_1,undefined4 param_2,int param_3,int param_4,undefined4 param_5,
                 undefined4 param_6,undefined4 param_7)

{
  undefined1 *puVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  undefined1 *puVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 *puVar10;
  int iVar11;
  undefined4 auStack_188 [2];
  ushort uStack_180;
  ushort uStack_17e;
  undefined4 uStack_17c;
  uint uStack_178;
  undefined2 uStack_172;
  undefined2 uStack_170;
  undefined4 uStack_16c;
  undefined1 uStack_168;
  undefined1 uStack_167;
  undefined4 uStack_164;
  undefined1 uStack_160;
  undefined4 uStack_15c;
  undefined4 uStack_158;
  undefined1 uStack_154;
  undefined1 uStack_153;
  undefined4 uStack_150;
  undefined1 uStack_14c;
  undefined2 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined1 auStack_dc [4];
  undefined2 uStack_d8;
  byte bStack_d6;
  undefined2 uStack_d4;
  byte bStack_d2;
  undefined2 uStack_d0;
  byte bStack_ce;
  undefined2 uStack_cc;
  byte bStack_ca;
  undefined2 uStack_c8;
  byte bStack_c6;
  undefined2 uStack_c4;
  byte bStack_c2;
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  char cStack_84;
  char cStack_83;
  undefined4 uStack_80;
  undefined1 uStack_7c;
  undefined1 uStack_7b;
  undefined1 uStack_7a;
  undefined2 uStack_78;
  undefined1 uStack_76;
  undefined1 uStack_75;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_68;
  uint uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  uint uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined2 uStack_2c;
  
  uStack_17e = *(ushort *)(param_1 + 0x1a0);
  uStack_180 = *(ushort *)(param_1 + 0x19e);
  auStack_188[0] = param_2;
  uStack_17c = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_178 = (uint)*(byte *)(param_1 + 0xc18);
  iVar11 = 0;
  uStack_172 = *(undefined2 *)(param_1 + 0xc76);
  uStack_170 = *(undefined2 *)(param_1 + 0xc74);
  uStack_154 = *(undefined1 *)(param_1 + 0xc88);
  uStack_153 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_16c = FUN_43814d74(*(undefined4 *)(*(int *)(param_3 + 4) + 0x14));
  uStack_168 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_167 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_164 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_160 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_15c = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),*(undefined1 *)(param_1 + 0x191));
  uStack_158 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_150 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  iVar4 = FUN_439fd844();
  uStack_14c = (undefined1)*(undefined4 *)(iVar4 + 0x1c);
  uVar7 = (uint)uStack_180;
  iVar5 = *(int *)(iVar4 + 0x1c);
  uVar8 = (uint)uStack_17e;
  puVar10 = auStack_188;
  while( true ) {
    if (iVar11 == iVar5) break;
    uVar2 = *(ushort *)(iVar4 + 0x28);
    iVar11 = iVar11 + 1;
    uVar3 = FUN_4355faf0(uVar7 * ((uint)*(ushort *)(iVar4 + 0x24) + (uint)(uVar2 >> 1)),0x280);
    *(undefined2 *)(puVar10 + 0x10) = uVar3;
    uVar3 = FUN_4355faf0(uVar8 * ((uint)*(ushort *)(iVar4 + 0x26) +
                                 (uint)(*(ushort *)(iVar4 + 0x2a) >> 1)),0x1e0);
    *(undefined2 *)((int)puVar10 + 0x42) = uVar3;
    uVar3 = FUN_4355faf0(uVar7 * uVar2,0x280);
    puVar10[0x12] = *(undefined4 *)(iVar4 + 0x20);
    *(undefined2 *)(puVar10 + 0x11) = uVar3;
    iVar4 = iVar4 + 0x54;
    puVar10 = puVar10 + 3;
  }
  uStack_e4 = *(undefined4 *)(param_1 + 0xc30);
  uStack_e8 = *(undefined2 *)(param_1 + 0xc78);
  uStack_e0 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_188,auStack_dc,param_3);
  iVar4 = DAT_4402546c;
  uStack_74 = 3;
  uStack_70 = param_5;
  if (*(char *)(DAT_4402546c + 0xef) == '\0') {
    uVar2 = *(ushort *)(param_1 + 0x15c);
    uStack_5c = *(undefined4 *)(param_1 + 0x160);
  }
  else {
    uVar2 = *(ushort *)(param_1 + 0x1c);
    uStack_5c = *(undefined4 *)(param_1 + 0x20);
  }
  uStack_68 = 0;
  uStack_60 = (uint)uVar2;
  uStack_4c = 0;
  uStack_58 = 0;
  uStack_50 = 0;
  uStack_3c = *(undefined4 *)(param_1 + 0xc4);
  uStack_44 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_40 = *(undefined4 *)(param_1 + 0x24);
  uStack_38 = param_6;
  uStack_34 = param_7;
  iVar5 = FUN_436be554(param_2,&uStack_74);
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3b28,iVar5);
    FUN_43902718(s_Sequence_Movie__APL_ERR_0x_02x_a_43cb3b3c,iVar5);
  }
  uStack_30 = 0;
  uStack_2c = 0;
  iVar5 = FUN_436bdbfc(param_2,0,&uStack_30);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_30;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_30._2_2_;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_2c;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_2c;
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3b77,iVar5);
    FUN_43902718(s_Sequence_Movie__APL_ERR_0x_02x_a_43cb3b8b,iVar5);
  }
  if ((*(byte *)(iVar4 + 0xc) & 8) != 0) {
    FUN_43814c78(3,9,1,&DAT_43cb3bbf);
    FUN_43902718(s_Apl_Kick_43cb3bd3);
  }
  *(undefined1 *)(param_4 + 100) = 1;
  puVar6 = auStack_dc;
  iVar5 = 0;
  *(undefined4 *)(param_4 + 0x68) = *(undefined4 *)(param_1 + 0x1f0);
  iVar4 = param_4;
  do {
    iVar5 = iVar5 + 1;
    *(undefined1 *)(iVar4 + 0x6c) = puVar6[0x1c];
    *(undefined1 *)(iVar4 + 0x80) = puVar6[0x30];
    puVar1 = puVar6 + 0x44;
    puVar6 = puVar6 + 1;
    *(undefined1 *)(iVar4 + 0x94) = *puVar1;
    iVar4 = iVar4 + 1;
  } while (iVar5 != 0x14);
  if (cStack_84 == '\0') {
    *(undefined1 *)(param_4 + 0xa8) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 0xa8) = 1;
    *(undefined4 *)(param_4 + 0xac) = uStack_80;
    *(undefined2 *)(param_4 + 0xb4) = uStack_d4;
    *(undefined2 *)(param_4 + 0xb0) = uStack_d8;
    *(undefined2 *)(param_4 + 0xbc) = uStack_cc;
    *(ushort *)(param_4 + 0xb2) = (ushort)bStack_d6;
    *(undefined2 *)(param_4 + 0xc4) = uStack_c4;
    *(ushort *)(param_4 + 0xb6) = (ushort)bStack_d2;
    *(undefined2 *)(param_4 + 0xb8) = uStack_d0;
    *(ushort *)(param_4 + 0xba) = (ushort)bStack_ce;
    *(ushort *)(param_4 + 0xbe) = (ushort)bStack_ca;
    *(undefined2 *)(param_4 + 0xc0) = uStack_c8;
    *(ushort *)(param_4 + 0xc2) = (ushort)bStack_c6;
    *(ushort *)(param_4 + 0xc6) = (ushort)bStack_c2;
  }
  if (cStack_83 == '\0') {
    *(undefined1 *)(param_4 + 200) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 200) = 1;
    uVar9 = *(undefined4 *)(param_1 + 0x1f0);
    *(int *)(param_4 + 0xd4) = param_1 + 0xbc;
    *(undefined4 *)(param_4 + 0xcc) = uVar9;
    *(undefined1 *)(param_4 + 0xd0) = auStack_dc[0];
  }
  *(undefined1 *)(param_4 + 0xd8) = uStack_7c;
  *(undefined1 *)(param_4 + 0xd9) = uStack_7b;
  *(undefined1 *)(param_4 + 0xda) = uStack_7a;
  *(undefined2 *)(param_4 + 0xdc) = uStack_78;
  *(undefined1 *)(param_4 + 0xde) = uStack_76;
  *(undefined1 *)(param_4 + 0xdf) = uStack_75;
  *(undefined2 *)(param_4 + 0xe0) = uStack_172;
  return;
}


/* query "435503b0" */

undefined1 FUN_435503b0(undefined4 param_1)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  ushort uVar5;
  undefined2 uVar6;
  byte *pbVar7;
  char cVar8;
  byte bVar9;
  undefined1 uVar10;
  int iVar11;
  undefined4 *puVar12;
  undefined4 uVar13;
  char *pcVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int *piVar19;
  undefined1 *puVar20;
  int iVar21;
  uint uVar22;
  int iVar23;
  int iVar24;
  undefined4 uVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  bool bVar29;
  uint in_fpscr;
  double dVar30;
  double dVar31;
  double dVar32;
  undefined4 uStack_4f0;
  undefined4 uStack_4ec;
  undefined4 uStack_4e8;
  undefined4 uStack_4e4;
  int iStack_4e0;
  int iStack_4dc;
  undefined4 uStack_4d8;
  undefined1 uStack_4d4;
  undefined1 uStack_4d3;
  undefined2 uStack_4d2;
  undefined2 uStack_4d0;
  undefined2 uStack_4ce;
  undefined2 uStack_4cc;
  undefined2 uStack_4ca;
  undefined2 uStack_4c8;
  undefined2 uStack_4c6;
  undefined2 uStack_4c4;
  undefined2 uStack_4c2;
  undefined2 uStack_4c0;
  undefined2 uStack_4be;
  undefined2 uStack_4bc;
  undefined4 uStack_4b8;
  undefined1 uStack_4b4;
  undefined1 uStack_4b3;
  undefined1 uStack_4b2;
  undefined4 uStack_4b0;
  undefined4 uStack_4ac;
  undefined4 uStack_4a8;
  undefined4 uStack_4a4;
  undefined1 uStack_4a0;
  undefined4 uStack_49c;
  undefined4 uStack_498;
  undefined4 uStack_494;
  undefined4 uStack_490;
  undefined1 auStack_48c [68];
  undefined1 uStack_448;
  undefined1 uStack_428;
  undefined4 uStack_40c;
  undefined2 uStack_408;
  undefined2 uStack_406;
  undefined2 uStack_404;
  undefined2 uStack_402;
  undefined1 uStack_400;
  undefined4 uStack_3fc;
  undefined4 uStack_3f8;
  int iStack_3f4;
  undefined1 uStack_3f0;
  undefined1 uStack_3ef;
  undefined4 uStack_3ec;
  undefined4 uStack_3e8;
  undefined4 uStack_3e4;
  undefined4 uStack_3e0;
  undefined4 uStack_3dc;
  int iStack_3d8;
  undefined4 uStack_3ac;
  undefined1 uStack_3a8;
  uint uStack_3a4;
  undefined1 uStack_3a0;
  undefined1 uStack_39f;
  undefined1 uStack_39e;
  undefined4 uStack_39c;
  undefined1 uStack_394;
  undefined1 uStack_393;
  undefined4 uStack_390;
  undefined4 uStack_38c;
  undefined4 uStack_388;
  undefined1 uStack_383;
  undefined1 uStack_381;
  undefined1 uStack_380;
  undefined1 uStack_37e;
  undefined1 uStack_37d;
  int iStack_37c;
  undefined1 uStack_378;
  undefined4 uStack_374;
  undefined4 uStack_370;
  undefined4 uStack_36c;
  undefined4 uStack_368;
  undefined4 uStack_364;
  undefined4 uStack_360;
  undefined4 uStack_35c;
  undefined4 uStack_358;
  undefined4 uStack_354;
  undefined4 uStack_350;
  undefined4 uStack_34c;
  undefined4 uStack_348;
  undefined4 uStack_344;
  undefined4 uStack_340;
  undefined4 uStack_33c;
  undefined4 uStack_338;
  undefined4 uStack_334;
  undefined4 uStack_330;
  undefined4 uStack_32c;
  undefined4 uStack_328;
  undefined4 uStack_324;
  undefined4 uStack_320;
  undefined4 uStack_31c;
  undefined4 uStack_318;
  undefined4 uStack_314;
  undefined4 uStack_310;
  undefined4 uStack_30c;
  undefined4 uStack_308;
  undefined4 uStack_304;
  undefined4 uStack_300;
  undefined4 uStack_2fc;
  undefined4 uStack_2f8;
  undefined4 uStack_2f4;
  undefined4 uStack_2f0;
  undefined4 uStack_2ec;
  undefined4 uStack_2e8;
  undefined4 uStack_2e4;
  undefined4 uStack_2e0;
  undefined4 uStack_2dc;
  undefined4 uStack_2d8;
  undefined4 uStack_2d4;
  undefined4 uStack_2d0;
  undefined4 uStack_2cc;
  undefined4 uStack_2c8;
  undefined4 uStack_2c4;
  undefined4 uStack_2c0;
  undefined4 uStack_2bc;
  undefined4 uStack_2b8;
  undefined4 uStack_2b4;
  undefined4 uStack_2b0;
  undefined4 uStack_2ac;
  undefined4 uStack_2a8;
  undefined4 uStack_2a4;
  undefined4 uStack_2a0;
  undefined4 uStack_29c;
  undefined4 uStack_298;
  undefined2 uStack_294;
  undefined2 uStack_292;
  undefined2 uStack_290;
  undefined2 uStack_28e;
  undefined2 uStack_28c;
  undefined2 uStack_28a;
  undefined1 auStack_284 [20];
  undefined1 auStack_270 [20];
  undefined1 auStack_25c [20];
  undefined1 auStack_248 [20];
  undefined1 auStack_234 [20];
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined4 uStack_218;
  undefined4 uStack_214;
  undefined4 uStack_210;
  undefined1 auStack_20c [20];
  undefined1 auStack_1f8 [20];
  undefined1 auStack_1e4 [20];
  undefined4 uStack_1d0;
  undefined4 uStack_1cc;
  undefined4 uStack_1c8;
  undefined4 uStack_1c4;
  undefined4 uStack_1c0;
  undefined1 auStack_1bc [20];
  undefined1 auStack_1a8 [20];
  undefined1 auStack_194 [20];
  undefined1 auStack_180 [20];
  undefined1 auStack_16c [20];
  undefined1 auStack_158 [20];
  undefined4 uStack_144;
  undefined4 uStack_140;
  undefined4 uStack_13c;
  undefined4 uStack_138;
  undefined4 uStack_134;
  undefined1 auStack_130 [20];
  undefined1 auStack_11c [20];
  undefined1 auStack_108 [20];
  undefined1 auStack_f4 [20];
  undefined1 auStack_e0 [20];
  undefined1 auStack_cc [20];
  undefined1 auStack_b8 [20];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [8];
  undefined4 uStack_4c;
  undefined4 uStack_48;
  uint uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 auStack_34 [2];
  
  iVar11 = FUN_4378f9b4();
  iVar23 = **(int **)(iVar11 + 4);
  iVar11 = FUN_4378f9b4();
  cVar1 = *(char *)(*(int *)(iVar11 + 8) + 0x33);
  iVar11 = FUN_43ae75dc(param_1);
  if (*(char *)(iVar11 + 0xd70) != '\0') {
    return 5;
  }
  puVar12 = (undefined4 *)FUN_4378f9b4();
  if (*(short *)*puVar12 == 0x13e) {
    return 5;
  }
  uVar13 = FUN_43afdf16(param_1);
  switch(uVar13) {
  case 0:
    iVar18 = FUN_43795b04();
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,0,*(undefined4 *)(iVar11 + 0x1fc),iVar23,0,1,0,2,0,iVar11 + 0xd68,0);
    uVar13 = DAT_44025f5c;
    if (iVar18 != 0) {
      iVar18 = FUN_43ae8cc8(DAT_44025f5c);
      pbVar7 = DAT_4402546c;
      if (iVar18 != 0) {
        if (*DAT_4402546c != 0) {
          iVar18 = FUN_43799a94(1,1,0,iVar23,0,1,0,2,0,iVar11 + 0xd68,iVar11 + 0x51c);
          if (iVar18 == 0) {
            return 5;
          }
          FUN_43728c18(iVar11 + 0x508,iVar11 + 0x50c,iVar11 + 0x510);
          FUN_43acc282(*(undefined4 *)(iVar11 + 0x51c),*pbVar7 - 1,iVar11 + 0x3e4,0xfff,0xfff,0xfff)
          ;
        }
        FUN_4378e5ac(uVar13);
      }
      FUN_43b03a74(auStack_68,DAT_4402110c);
      FUN_43796910(param_1,auStack_68,iVar11);
      uVar13 = FUN_438148f0();
      FUN_43b04040(uVar13,*(undefined4 *)(iVar11 + 0x1f0),iVar23,*(undefined4 *)(iVar11 + 0x1f8),
                   *(undefined4 *)(iVar11 + 0xc4c),*(undefined4 *)(iVar11 + 0x1b0));
      return 0;
    }
    return 5;
  case 1:
    iVar18 = FUN_4378f9b4();
    if ((*(int *)(*(int *)(iVar18 + 8) + 0x1e8) != 0) && (*(int *)(iVar11 + 0x1fc) != 9)) {
      return 1;
    }
    uVar13 = FUN_4378f9b4();
    iVar18 = FUN_4378e6a0(DAT_44025f5c,uVar13);
    if (iVar18 == 0) {
      return 5;
    }
    iVar24 = iVar11 + 0xd68;
    iVar18 = FUN_43799a94(1,1,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0x51c);
    if (iVar18 == 0) {
      return 5;
    }
    FUN_43728c18(iVar11 + 0x508,iVar11 + 0x50c,iVar11 + 0x510);
    pbVar7 = DAT_4402546c;
    uVar10 = *(undefined1 *)(iVar11 + 0x3fa);
    if (DAT_4402546c[0x4e] == 0xff) {
      uVar10 = 0;
    }
    else if (DAT_4402546c[0x4e] != 0) {
      uVar10 = 1;
    }
    uVar25 = *(undefined4 *)(iVar11 + 0x51c);
    uVar13 = FUN_437d9d08();
    FUN_43acc2ee(uVar25,uVar10,uVar13);
    iVar18 = FUN_43799a94(1,0x10,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,auStack_34)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,4,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0xc20);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_4381c04c(0,*(undefined4 *)(iVar11 + 0x184),auStack_54);
    if (iVar18 == 0) {
      *(undefined1 *)(iVar11 + 0x524) = 0;
      *(undefined1 *)(iVar11 + 0x20c) = 0;
    }
    if ((pbVar7[2] & 1) == 0) {
      uVar13 = 10;
    }
    else {
      uVar13 = 0xb;
    }
    *(undefined4 *)(iVar11 + 0x598) = uVar13;
    *(undefined4 *)(iVar11 + 0x59c) = 2;
    *(undefined4 *)(iVar11 + 0x5d4) = 1;
    *(undefined4 *)(iVar11 + 0x5a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x5c8) = 0;
    *(undefined4 *)(iVar11 + 0x5d8) = uStack_4c;
    *(undefined4 *)(iVar11 + 0x5cc) = 0;
    *(undefined4 *)(iVar11 + 0x5fc) = 0;
    *(undefined4 *)(iVar11 + 0x5dc) = uStack_48;
    bVar29 = *(char *)(iVar11 + 0x188) != '\0';
    *(uint *)(iVar11 + 0x5f8) = (uint)bVar29;
    if (((bVar29) && (*(int *)(iVar11 + 0xd78) == 1)) && (*(short *)(iVar11 + 0x19e) == 0x5a0)) {
      *(undefined2 *)(iVar11 + 0x19e) = 0x5c0;
    }
    if (((*(int *)(iVar11 + 0x1b0) - 2U < 2) &&
        (iVar18 = FUN_4378f9b4(), *(int *)(*(int *)(iVar18 + 4) + 0xc) != 0)) &&
       (*(int *)(iVar11 + 0x1fc) != 9)) {
      bVar9 = 0;
      *(undefined1 *)(iVar11 + 0x1ee) = 0;
LAB_4355070c:
      *(byte *)(iVar11 + 0x20c) = bVar9;
    }
    else {
      if ((*(char *)(iVar11 + 0xd40) != '\0') && (*(char *)(iVar11 + 0xd41) != '\0')) {
        bVar9 = 0;
        goto LAB_4355070c;
      }
      iVar18 = FUN_4378f9b4();
      bVar2 = *(byte *)(*(int *)(iVar18 + 8) + 0x268);
      bVar9 = bVar2 & 2;
      if ((bVar2 & 2) == 0) goto LAB_4355070c;
    }
    iVar18 = FUN_43799a94(1,0xe,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,0);
    if (iVar18 == 0) {
      return 5;
    }
    if ((pbVar7[0x70] == 0) && (iVar18 = FUN_4378003c(), iVar18 == 0)) {
      iVar26 = FUN_43affc8a(*(undefined4 *)(iVar11 + 0x508));
      uStack_3a0 = *(undefined1 *)(iVar11 + 0x20e);
      uStack_39e = 0;
      uStack_381 = 0;
      uStack_39f = *(undefined1 *)(iVar11 + 0x20f);
      uStack_380 = 0;
      uStack_37e = 0;
      uStack_39c = *(undefined4 *)(iVar11 + 0x208);
      uStack_37d = 0;
      uStack_394 = (undefined1)*(undefined4 *)(iVar11 + 0x1fc);
      uStack_393 = (undefined1)*(undefined4 *)(iVar11 + 0xc4c);
      uStack_3a4 = (uint)(iVar26 == 1);
      uStack_390 = *(undefined4 *)(iVar11 + 0x1ec);
      uStack_38c = *(undefined4 *)(iVar11 + 0x1f0);
      uStack_388 = *(undefined4 *)(iVar11 + 500);
      uStack_383 = (undefined1)*(undefined4 *)(iVar11 + 0x3e0);
      uStack_378 = *(int *)(iVar11 + 0xd78) == 1;
      iStack_37c = iVar18;
      FUN_439e34d4(&uStack_3a4);
    }
    FUN_43799a94(1,0xf,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,0);
    if ((*(char *)(iVar11 + 0x20c) == '\0') && (*(char *)(iVar11 + 0x213) != '\0')) {
      *(undefined1 *)(iVar11 + 0x213) = 0;
    }
    if (*(char *)(iVar11 + 0x213) != '\0') {
      uVar13 = FUN_43799f3c();
      FUN_4379a20c(uVar13,5,iVar11 + 0xe4);
      FUN_43903720(iVar11 + 0xe4,0,0,5);
    }
    iVar23 = FUN_43799a94(1,0xd,*(undefined4 *)(iVar11 + 0x1fc),iVar23,0,1,0,
                          *(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0x520);
    if (iVar23 == 0) {
      return 5;
    }
    FUN_43728c4c(iVar11 + 0x514,iVar11 + 0x518);
    FUN_437956a4(*(undefined4 *)(iVar11 + 0x520));
    piVar19 = (int *)FUN_4378f9b4();
    iVar18 = *(int *)(*piVar19 + 0x544);
    iVar23 = FUN_4378f9c0();
    cVar8 = DAT_43f9b2b1;
    if ((iVar18 != 0) && (iVar18 == *(int *)(iVar23 + 0x29c))) goto switchD_43550884_default;
    switch(iVar18) {
    case 0:
      if (DAT_43f9b2af == '\0') goto switchD_43550884_default;
      piVar19 = (int *)FUN_4378f9b4();
      iVar24 = DAT_43eea89c;
      if (((bool)cVar8 == (*(int *)(*piVar19 + 0x548) != 0)) &&
         (piVar19 = (int *)FUN_4378f9b4(), iVar24 == *(int *)(*piVar19 + 0x54c))) {
LAB_43550912:
        bVar29 = true;
      }
      else {
        if (2 < DAT_43eea8a0) {
          piVar19 = (int *)FUN_4378f9b4();
          DAT_43f9b2b1 = *(int *)(*piVar19 + 0x548) != 0;
          piVar19 = (int *)FUN_4378f9b4();
          DAT_43eea89c = *(int *)(*piVar19 + 0x54c);
          goto LAB_43550912;
        }
        DAT_43eea8a0 = DAT_43eea8a0 + 1;
        bVar29 = false;
      }
      iVar24 = FUN_43ae933a(DAT_43eea8a4);
      if (iVar24 != 0) {
        FUN_43813cac(3,9,1,&DAT_43cb3148);
        pcVar14 = s_______ExternalStorageStart___Err_43cb315c;
        goto LAB_43550978;
      }
      if (!bVar29) goto switchD_43550884_default;
      break;
    case 1:
      if (DAT_43f9b2af == '\0') goto switchD_43550884_default;
      break;
    case 2:
      if (DAT_43f9b2af != '\0') goto switchD_43550884_default;
      uVar13 = FUN_43ae9332(*(undefined4 *)(iVar11 + 0x1fc));
      iVar24 = FUN_43795894(&DAT_43eea8a4,uVar13);
      if (iVar24 == 0) {
        DAT_43f9b2af = '\x01';
        break;
      }
      FUN_43813cac(3,9,1,&DAT_43cb317f);
      pcVar14 = s_______ExternalStorageAcquire___E_43cb3193;
LAB_43550978:
      FUN_43902718(pcVar14);
      goto switchD_43550884_default;
    case 3:
      if (DAT_43f9b2af == '\0') goto switchD_43550884_default;
      iVar24 = FUN_437958cc(DAT_43eea8a4);
      if (iVar24 != 0) {
        FUN_43813cac(3,9,1,&DAT_43cb31b8);
        pcVar14 = s_______ExternalStorageRelease___E_43cb31cc;
        goto LAB_43550978;
      }
      DAT_43f9b2af = '\0';
      break;
    default:
      goto switchD_43550884_default;
    }
    *(int *)(iVar23 + 0x29c) = iVar18;
    DAT_43eea8a0 = 0;
switchD_43550884_default:
    FUN_43814008(iVar11);
    FUN_43b03a74(auStack_7c,DAT_44022cc8);
    FUN_43796910(param_1,auStack_7c,iVar11);
    uVar13 = DAT_44023820;
    if (*(char *)(iVar11 + 0x525) == '\0') {
      FUN_438106ec(iVar11);
      FUN_43b03a74(auStack_90,uVar13);
      puVar20 = auStack_90;
    }
    else {
      FUN_43b03a74(auStack_a4,DAT_44026238);
      FUN_43797090(param_1,auStack_a4,iVar11);
      FUN_43b03a74(auStack_b8,uVar13);
      puVar20 = auStack_b8;
    }
    FUN_43797090(param_1,puVar20,iVar11);
    uVar13 = DAT_44021e0c;
    if (cVar1 == '\0') {
      FUN_43b03a74(auStack_f4,DAT_440204b4);
      FUN_43796910(param_1,auStack_f4,iVar11);
      FUN_43b03a74(auStack_108,uVar13);
      FUN_43796910(param_1,auStack_108,iVar11);
    }
    else {
      FUN_43b03a74(auStack_cc,DAT_440204b4);
      FUN_43797090(param_1,auStack_cc,iVar11);
      FUN_43b03a74(auStack_e0,uVar13);
      FUN_43797090(param_1,auStack_e0,iVar11);
    }
    FUN_43b03a74(auStack_11c,DAT_44024a24);
    FUN_43796910(param_1,auStack_11c,iVar11);
    FUN_43b03a74(auStack_130,DAT_440259b4);
    FUN_4379704c(param_1,auStack_130,iVar11);
    if (*(char *)(iVar11 + 0x20c) == '\0') {
      return 5;
    }
    return 0;
  case 2:
    if (*(char *)(iVar11 + 0x20c) == '\0') {
      return 5;
    }
    uVar22 = *(int *)(iVar11 + 0xc50) + 1;
    *(uint *)(iVar11 + 0xc50) = uVar22;
    if (uVar22 < *(uint *)(iVar11 + 0xc4c)) {
      return 1;
    }
    FUN_439c5a04(&uStack_29c,0,0x18);
    uStack_294 = *(undefined2 *)(iVar11 + 0xc74);
    uStack_28c = *(undefined2 *)(iVar11 + 0x526);
    uStack_28a = *(undefined2 *)(iVar11 + 0x52e);
    uStack_29c = *(undefined4 *)(iVar11 + 0xc30);
    uStack_292 = *(undefined2 *)(iVar11 + 0xd1c);
    uStack_298 = *(undefined4 *)(iVar11 + 0xc34);
    uStack_28e = *(undefined2 *)(iVar11 + 0xd1e);
    uStack_290 = *(undefined2 *)(iVar11 + 0xd20);
    uVar13 = FUN_438148f0();
    FUN_438149dc(uVar13,*(undefined4 *)(iVar11 + 0x1f0),&uStack_29c);
    if (*(int *)(iVar11 + 0x3dc) == 1) {
      FUN_43afb42e(&uStack_3ec);
      FUN_43afb46a(&uStack_144,0);
      uStack_3ac = 5;
      uStack_3ec = uStack_144;
      uStack_3e8 = uStack_140;
      uStack_3e4 = uStack_13c;
      uStack_3e0 = uStack_138;
      uStack_3dc = uStack_134;
      iStack_3d8 = 4;
      uStack_3a8 = 0;
      FUN_43b03af4(auStack_158,DAT_44023534);
      FUN_43afb446(auStack_16c,DAT_44024860);
      uVar13 = FUN_437dcfc8(auStack_158,auStack_16c,iVar11);
      iVar11 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
      if (iVar11 != 0) {
        FUN_437e59dc(iVar11,1);
        return 5;
      }
      return 5;
    }
    if ((*(uint *)(iVar11 + 0xc4c) & 1) == 0) {
      iVar18 = FUN_4378f9b4();
      if (*(int *)(*(int *)(iVar18 + 4) + 0xc) == 0) goto LAB_43550c26;
      *(undefined4 *)(iVar11 + 0xc64) = 0;
    }
    else {
      iVar18 = FUN_4378f9b4();
      uVar13 = 0;
      if (*(int *)(*(int *)(iVar18 + 4) + 0xc) != 0) {
LAB_43550c26:
        uVar13 = 1;
      }
      *(undefined4 *)(iVar11 + 0xc64) = uVar13;
    }
    uVar13 = 0;
    if (*(char *)(iVar11 + 0x191) != '\0') {
      if (*(int *)(iVar11 + 0xc64) == 0) {
        uVar13 = 2;
      }
      else {
        uVar13 = 1;
      }
    }
    if ((*(int *)(iVar11 + 0x1b0) - 2U < 2) && (*(int *)(iVar11 + 0xc64) == 0)) {
      return 1;
    }
    iVar24 = iVar11 + 0xd68;
    iVar18 = FUN_43799a94(1,5,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc28);
    if (iVar18 == 0) {
      return 5;
    }
    if (*(int *)(iVar11 + 0xd60) != 1) {
      FUN_43b0419c(1,iVar23);
    }
    break;
  case 3:
    uVar22 = *(int *)(iVar11 + 0xc58) + 1;
    *(uint *)(iVar11 + 0xc58) = uVar22;
    if (uVar22 < *(uint *)(iVar11 + 0xc54)) {
      return 1;
    }
    if (*(char *)(iVar11 + 0x213) != '\0') {
      FUN_43ae7558(&uStack_34c);
      iVar18 = FUN_43903558(&uStack_34c,0x173425,1,0,5);
      if (iVar18 != 0) {
        FUN_43813cac(3,9,1,&DAT_43cb3273);
        FUN_43902718(s__DualRec__Can_t_Get_CAM_REG_DREC_43cb3287);
        goto LAB_435524dc;
      }
      *(undefined4 *)(iVar11 + 0x10c) = uStack_34c;
      *(undefined4 *)(iVar11 + 0x110) = uStack_348;
      *(undefined4 *)(iVar11 + 0x114) = uStack_344;
      *(undefined4 *)(iVar11 + 0x118) = uStack_340;
      *(undefined4 *)(iVar11 + 0x11c) = uStack_33c;
      *(undefined4 *)(iVar11 + 0x120) = uStack_338;
      *(undefined4 *)(iVar11 + 0x124) = uStack_334;
      *(undefined4 *)(iVar11 + 0x128) = uStack_330;
      *(undefined4 *)(iVar11 + 300) = uStack_32c;
      *(undefined4 *)(iVar11 + 0x130) = uStack_328;
      FUN_43ae7542(&uStack_34c);
      if ((DAT_4402546c[0xc1] & 1) == 0) {
        iVar18 = FUN_43561604(*(undefined4 *)(iVar11 + 0x114));
        FUN_43b0bf32(iVar18 + 0x3800,*(undefined4 *)(iVar11 + 0x510));
      }
      FUN_43b2a258(iVar11 + 0x10c,5);
      FUN_43ae7534(&uStack_34c);
      uVar13 = FUN_43799f3c();
      FUN_43799fa8(uVar13,1);
      FUN_43799fa8(uVar13,0);
      FUN_43799fa8(uVar13,4);
      FUN_43799fa8(uVar13,5);
      FUN_43afb42e(&uStack_3ec);
      FUN_43afb46a(&uStack_1d0,0);
      uStack_3ec = uStack_1d0;
      uStack_3e8 = uStack_1cc;
      uStack_3e4 = uStack_1c8;
      uStack_3e0 = uStack_1c4;
      uStack_3dc = uStack_1c0;
      iStack_3d8 = 4;
      uStack_3a8 = 0;
      uStack_3ac = 5;
      FUN_43b03af4(auStack_1e4,DAT_440204bc);
      FUN_43afb446(auStack_1f8,DAT_44024860);
      uVar13 = FUN_437dcfc8(auStack_1e4,auStack_1f8,iVar11);
      iVar18 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
      if (iVar18 != 0) {
        FUN_437e59dc(iVar18,1);
      }
      FUN_43ae7542(iVar11 + 0xe4);
      FUN_43ae7542(iVar11 + 0x10c);
    }
    if ((*(int *)(iVar11 + 0xd60) != 1) ||
       (iVar18 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar18 + 8) + 0x268) & 4) == 0))
    goto LAB_43552058;
    piVar19 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar19 + 0x2c) == 0) {
      uVar13 = 0;
      if (*(char *)(iVar11 + 0x199) != '\0') {
        if (*(int *)(iVar11 + 0xc64) != 0) {
          *(undefined4 *)(iVar11 + 0x9b0) = 1;
          goto LAB_43551bd4;
        }
        uVar13 = 2;
      }
      *(undefined4 *)(iVar11 + 0x9b0) = uVar13;
    }
    else {
      uVar13 = 0;
      if (*(char *)(iVar11 + 0x191) != '\0') {
        uVar13 = 5;
      }
      *(undefined4 *)(iVar11 + 0x9b0) = uVar13;
      if (*(int *)(iVar11 + 0xc64) == 0) goto LAB_43552058;
    }
LAB_43551bd4:
    iVar24 = iVar11 + 0xd68;
    iVar18 = FUN_43799a94(1,0xb,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_38);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,0x13,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_40)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,8,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_3c);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43ae8c4a(iVar23 + 1);
    iVar24 = FUN_439035e0(iVar11 + 0x44,*(undefined4 *)(iVar11 + 0x194),iVar18 << 8,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    if (*(int *)(iVar11 + 0xc5c) == 2) {
      iVar24 = FUN_4378f9b4();
      if (*(int *)(*(int *)(iVar24 + 4) + 0xc) == 1) {
        uVar13 = 0xc;
      }
      else {
        uVar13 = 0xd;
      }
    }
    else {
      uVar13 = 0xb;
    }
    *(undefined4 *)(iVar11 + 0x6d0) = uVar13;
    *(uint *)(iVar11 + 0x700) = (uint)(*(char *)(iVar11 + 400) != '\0');
    *(undefined4 *)(iVar11 + 0x70c) = 0;
    *(undefined4 *)(iVar11 + 0x6dc) = 1;
    *(undefined4 *)(iVar11 + 0x6e0) = *(undefined4 *)(iVar11 + 0x24);
    *(undefined4 *)(iVar11 + 0x6d4) = 0;
    *(undefined2 *)(iVar11 + 0x994) = 0;
    *(undefined4 *)(iVar11 + 0x6e4) = *(undefined4 *)(iVar11 + 0x28);
    *(undefined2 *)(iVar11 + 0x996) = 0;
    *(undefined2 *)(iVar11 + 0x99c) = 0;
    *(undefined2 *)(iVar11 + 0x99e) = 0;
    *(undefined2 *)(iVar11 + 0x9a0) = 0;
    *(undefined2 *)(iVar11 + 0x9a2) = 0;
    *(undefined4 *)(iVar11 + 0x704) = 2;
    *(undefined4 *)(iVar11 + 0x730) = 0;
    *(undefined4 *)(iVar11 + 0x9a4) = 0;
    *(undefined2 *)(iVar11 + 0x9a8) = 0;
    *(undefined2 *)(iVar11 + 0x9aa) = 0;
    *(undefined2 *)(iVar11 + 0x9ac) = 0;
    *(undefined2 *)(iVar11 + 0x9ae) = 0;
    *(undefined4 *)(iVar11 + 0x708) = uStack_40;
    *(undefined2 *)(iVar11 + 0x998) = *(undefined2 *)(iVar11 + 0x19e);
    *(undefined2 *)(iVar11 + 0x99a) = *(undefined2 *)(iVar11 + 0x1a0);
    if ((*(short *)(iVar11 + 0x1b8) == 0x2d0) && (*(char *)(iVar11 + 0x199) != '\0')) {
      *(undefined4 *)(iVar11 + 0x9a4) = 1;
      *(undefined2 *)(iVar11 + 0x9a8) = 0x80;
      *(undefined2 *)(iVar11 + 0x9aa) = 0x50;
      *(undefined2 *)(iVar11 + 0x9ac) = 0x80;
      *(undefined2 *)(iVar11 + 0x9ae) = 0x50;
    }
    uVar13 = FUN_43b03bf8();
    uStack_2b0 = 0x80;
    uStack_2b8 = 4;
    uStack_2b4 = 7;
    uStack_2ac = FUN_43556490(uVar13,0x80,*(int *)(iVar11 + 0xc5c) << 2,cVar1);
    uStack_2cc = 0x80;
    uStack_2a0 = 1;
    uStack_2a8 = 0;
    uStack_2a4 = 1;
    uStack_2d4 = 4;
    uStack_2d0 = 7;
    uStack_2c8 = 0;
    uStack_2bc = 0;
    uStack_2c4 = 0;
    uStack_2c0 = 1;
    iVar24 = FUN_43940f2c(uStack_38,&uStack_2b8,&uStack_2d4);
    if (iVar24 != 0) {
      FUN_43813cac(3,9,1,&DAT_43cb32af,iVar24);
      FUN_43902718(s_Sequence_Movie__RC_ERR_0x_02x_rc_43cb32c3,iVar24);
    }
    uVar5 = *(ushort *)(iVar11 + 0x1a2);
    if (uVar5 < 0x3c1) {
      uVar25 = 0;
      uVar13 = 0;
    }
    else {
      if (uVar5 != 0x500) {
        FUN_43813cac(3,9,1,&DAT_43cb32fd,uVar5);
        FUN_43902718(s_Sequence_Movie__SRC_>VFX_Strip_P_43cb3311,*(undefined2 *)(iVar11 + 0x1a2));
      }
      uVar25 = 0x280;
      uVar13 = 5;
    }
    FUN_43798490(uStack_38,iVar11 + 0x6d0,iVar11 + 0x988,iVar11 + 0x19e,iVar11 + 0x1a2,
                 *(undefined4 *)(iVar11 + 0xbd4),uVar13,1);
    FUN_43815e94(iVar11,uStack_3c,uStack_40,0,1,*(undefined2 *)(iVar11 + 0x1a2),uVar25);
    iVar24 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar24 + 4) + 0x10) == 3) {
      uVar13 = 3;
    }
    else {
      uVar13 = 2;
    }
    FUN_43b03a5e(&uStack_4f0);
    FUN_43811484(iVar11,iVar23);
    uStack_4f0 = *(undefined4 *)(iVar11 + 0x1ec);
    uStack_4ec = *(undefined4 *)(iVar11 + 0x1f0);
    uStack_4e8 = *(undefined4 *)(iVar11 + 500);
    uStack_4e4 = 0;
    uStack_4d8 = *(undefined4 *)(iVar11 + 0xc5c);
    uStack_4d4 = (undefined1)*(undefined4 *)(iVar11 + 0x1f8);
    iStack_4e0 = iVar11 + 0x44;
    iStack_4dc = iVar18;
    uStack_4d3 = FUN_43ae8c4a((iVar23 - *(int *)(iVar11 + 0xd50)) - *(int *)(iVar11 + 0xc58));
    piVar19 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar19 + 0x2c) == 0) {
      uStack_4d2 = *(undefined2 *)(iVar11 + 0x1b8);
    }
    else {
      uStack_4d2 = *(undefined2 *)(iVar11 + 0x1a2);
    }
    piVar19 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar19 + 0x2c) == 0) {
      uStack_4d0 = *(undefined2 *)(iVar11 + 0x1ba);
    }
    else {
      uStack_4d0 = *(undefined2 *)(iVar11 + 0x1a4);
    }
    uVar6 = *(undefined2 *)(iVar11 + 0x1a2);
    uStack_4ce = FUN_43ae9e86(uVar6,0x40);
    uStack_4cc = *(undefined2 *)(iVar11 + 0x1a4);
    uStack_4ca = 0;
    uStack_4b8 = *(undefined4 *)(iVar11 + 0x1b4);
    uStack_4c8 = 0;
    uStack_4c2 = 0;
    uStack_4b4 = *(undefined1 *)(iVar11 + 0x198);
    uStack_4c0 = 0;
    uStack_4b3 = 1;
    uStack_4b2 = *(undefined1 *)(iVar11 + 0x199);
    uStack_4b0 = *(undefined4 *)(iVar11 + 0xc64);
    uStack_4ac = *(undefined4 *)(iVar11 + 0x4fc);
    uStack_4a8 = *(undefined4 *)(iVar11 + 0x534);
    uStack_4a4 = *(undefined4 *)(iVar11 + 0x504);
    uStack_4a0 = *(int *)(iVar11 + 0xbd4) == 1;
    uStack_3fc = 0xffffffff;
    uStack_49c = 0xffffffff;
    uStack_498 = 0xffffffff;
    uStack_494 = *(undefined4 *)(iVar11 + 0xd54);
    uStack_490 = *(undefined4 *)(iVar11 + 0xd58);
    auStack_48c[0] = 0;
    uStack_448 = 0;
    uStack_428 = 0;
    uStack_40c = *(undefined4 *)(iVar11 + 0xd78);
    uStack_408 = *(undefined2 *)(iVar11 + 0xd26);
    uStack_406 = *(undefined2 *)(iVar11 + 0xd28);
    uStack_404 = *(undefined2 *)(iVar11 + 0xd2a);
    uStack_402 = *(undefined2 *)(iVar11 + 0xd2c);
    uStack_400 = *(undefined1 *)(iVar11 + 0xd2e);
    if (*(char *)(iVar11 + 0xd80) != '\0') {
      uStack_3fc = *(undefined4 *)(iVar11 + 0xd7c);
    }
    uStack_4c6 = uVar6;
    uStack_4c4 = uStack_4cc;
    uStack_4be = uVar6;
    uStack_4bc = uStack_4cc;
    piVar19 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar19 + 0x2c) == 0) {
      uVar13 = *(undefined4 *)(iVar11 + 0x1b0);
    }
    iStack_3f4 = *(int *)(iVar11 + 0xd84);
    uStack_3f0 = iStack_3f4 != 0;
    uStack_3f8 = uVar13;
    puVar12 = (undefined4 *)FUN_4378f9b4();
    uStack_3ef = *(short *)*puVar12 == 0x109;
    FUN_439c5320(auStack_48c,iVar11 + 0xc90,0x80);
    if (DAT_4402546c[0x9d] == 1) {
      FUN_4379b44c(0,&uStack_4f0);
    }
    piVar19 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar19 + 0x2c) == 1) {
      uVar13 = 2;
    }
    else {
      uVar13 = 1;
    }
    FUN_4379b44c(uVar13,&uStack_4f0);
LAB_43552058:
    iVar23 = FUN_43ae8c4a(iVar23 + *(int *)(iVar11 + 0xc5c) + 1);
    iVar18 = FUN_4378f9b4();
    uStack_44 = (int)(uint)*(ushort *)(*(int *)(iVar18 + 4) + 0x20) >> 2;
    FUN_43ad2dfc(0xfff,&uStack_44);
    iVar24 = *(int *)(iVar11 + 0xc5c);
    iVar18 = FUN_4378f9b4();
    iVar18 = FUN_4355faf0(*(int *)(*(int *)(iVar18 + 4) + 0x18) + 0x3e7ff,0x3e800);
    FUN_43b2a2d0(iVar11 + 0xbc,iVar23 * 0x100 + (uStack_44 >> 4),(iVar24 + 2) * iVar18,1,5);
    iVar23 = FUN_43ae8c4a(iVar23 + 1);
    FUN_43b2a2d0(iVar11 + 0x44,iVar23 * 0x100 + (uStack_44 >> 4),iVar18 * (iVar24 + 3),1,5);
    return 0;
  case 4:
    iVar18 = FUN_439fdec4();
    if (iVar18 != 0) {
      DAT_43eea878 = *(undefined2 *)(iVar11 + 0x134);
      DAT_43eea87c = *(undefined4 *)(iVar11 + 0x138);
      if (*(char *)(iVar11 + 400) == '\0') {
        DAT_43eea880 = FUN_43ae9e86(*(undefined2 *)(iVar11 + 0x19e),0x40);
      }
      else {
        DAT_43eea880 = FUN_43ae98f8();
      }
      DAT_43eea882 = *(undefined2 *)(iVar11 + 0x1a0);
      DAT_43eea888 = *(undefined2 *)(iVar11 + 0x19e);
      DAT_43eea884 = 0;
      DAT_43eea88c = (ushort)*(byte *)(iVar11 + 0x136);
      DAT_43eea890 = *(undefined4 *)(iVar11 + 0x13c);
      DAT_43eea886 = 0;
      DAT_43eea894 = *(undefined4 *)(iVar11 + 0x140);
      DAT_43eea88a = DAT_43eea882;
      iVar18 = FUN_439fde5c(&DAT_43eea878);
      if (iVar18 != 0) {
        FUN_43ae7542(iVar11 + 0x134);
      }
    }
    uStack_34c = *(undefined4 *)(iVar11 + 0xbc);
    uStack_348 = *(undefined4 *)(iVar11 + 0xc0);
    uStack_344 = *(undefined4 *)(iVar11 + 0xc4);
    uStack_340 = *(undefined4 *)(iVar11 + 200);
    uStack_33c = *(undefined4 *)(iVar11 + 0xcc);
    uStack_338 = *(undefined4 *)(iVar11 + 0xd0);
    uStack_334 = *(undefined4 *)(iVar11 + 0xd4);
    uStack_330 = *(undefined4 *)(iVar11 + 0xd8);
    uStack_32c = *(undefined4 *)(iVar11 + 0xdc);
    uStack_328 = *(undefined4 *)(iVar11 + 0xe0);
    FUN_43ae7542(iVar11 + 0xbc);
    if (*(char *)(iVar11 + 0xc68) != '\0') {
      FUN_43afb42e(&uStack_3ec);
      FUN_43afb476(&uStack_3ec,DAT_440219a8);
      uStack_3a8 = 0;
      iStack_3d8 = 4;
      uStack_3ac = FUN_43afbf44(param_1);
      FUN_43b0417e(1,10,0,0);
      FUN_43b0417e(2,0xffffffff,0,0);
      uStack_374 = *(undefined4 *)(iVar11 + 0x1c);
      uStack_370 = *(undefined4 *)(iVar11 + 0x20);
      uStack_36c = *(undefined4 *)(iVar11 + 0x24);
      uStack_368 = *(undefined4 *)(iVar11 + 0x28);
      uStack_364 = *(undefined4 *)(iVar11 + 0x2c);
      uStack_360 = *(undefined4 *)(iVar11 + 0x30);
      uStack_35c = *(undefined4 *)(iVar11 + 0x34);
      uStack_358 = *(undefined4 *)(iVar11 + 0x38);
      uStack_354 = *(undefined4 *)(iVar11 + 0x3c);
      uStack_350 = *(undefined4 *)(iVar11 + 0x40);
      FUN_43ae7542(iVar11 + 0x1c);
      FUN_43ae7542(iVar11 + 0x6c);
      FUN_43b03a80(auStack_20c,DAT_44022af4);
      uVar13 = FUN_43b03a70(iVar11);
      uVar13 = FUN_4380d708(auStack_20c,uVar13,iVar11);
      iVar18 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
      if (iVar18 != 0) {
        FUN_43b04730();
      }
      *(undefined4 *)(iVar11 + 0x1c) = uStack_374;
      *(undefined4 *)(iVar11 + 0x20) = uStack_370;
      *(undefined4 *)(iVar11 + 0x24) = uStack_36c;
      *(undefined4 *)(iVar11 + 0x28) = uStack_368;
      *(undefined4 *)(iVar11 + 0x2c) = uStack_364;
      *(undefined4 *)(iVar11 + 0x30) = uStack_360;
      *(undefined4 *)(iVar11 + 0x34) = uStack_35c;
      *(undefined4 *)(iVar11 + 0x38) = uStack_358;
      *(undefined4 *)(iVar11 + 0x3c) = uStack_354;
      *(undefined4 *)(iVar11 + 0x40) = uStack_350;
      FUN_43ae7542(&uStack_374);
      FUN_43ae7534(&uStack_374);
    }
    if (*(int *)(iVar11 + 0x3dc) == 0) {
      if (*(char *)(iVar11 + 0x20d) != '\0') {
        iVar18 = FUN_437999e4(1,5);
        if (iVar18 == 0) goto LAB_435524dc;
        piVar19 = (int *)FUN_4378f9b4();
        uVar10 = FUN_43879534(*(undefined4 *)(*piVar19 + 0xb4));
        *(undefined1 *)(iVar11 + 0xd22) = uVar10;
        iVar18 = thunk_FUN_439dce54();
        *(char *)(iVar11 + 0xd72) = (char)iVar18;
        if ((iVar18 != 0) || (*(char *)(iVar11 + 0xd22) != '\0')) {
          FUN_43ae7558(&uStack_374);
          iVar18 = FUN_43903558(iVar11 + 0x94,0x30700,0x11,0,5);
          if (iVar18 != 0) {
            DAT_43f9b2ae = DAT_43f9b2ae + 1;
            if (0x3b < DAT_43f9b2ae) {
              FUN_43813cac(3,9,1,&DAT_43cb0ee4,DAT_43f9b2ae);
              FUN_43902718(s_Face_Memory_Alloc_Error___d_43cb0ef8,DAT_43f9b2ae);
            }
            FUN_43ae7534(&uStack_374);
            goto LAB_435524dc;
          }
          *(int *)(iVar11 + 0xd74) = iVar23;
          DAT_43f9b2ae = 0;
          if (*(char *)(iVar11 + 0xc18) == '\0') {
            uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1e);
          }
          else if (cVar1 == '\0') {
            uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1c);
          }
          else {
            uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1d);
          }
          *(undefined1 *)(iVar11 + 0x212) = uVar10;
          bVar9 = *(byte *)(iVar11 + 0x212) & 0x7f;
          if (bVar9 == 0x40) {
            FUN_43560dc4(0x1a,0xffffffdf);
            FUN_43b03a74(auStack_25c,DAT_44020ee4);
            FUN_4379704c(param_1,auStack_25c,iVar11);
          }
          else if (bVar9 == 0x41) {
            FUN_43560dc4(0x1a,0xffffffdf);
            FUN_43b03a74(auStack_270,DAT_44020ee4);
            FUN_43796910(param_1,auStack_270,iVar11);
          }
          else {
            FUN_43560da8(0x1a,0x20);
          }
          FUN_43afb42e(&uStack_3ec);
          FUN_43afb476(&uStack_3ec,DAT_44021fc8);
          iStack_3d8 = 4;
          uStack_3a8 = 0;
          uStack_3ac = FUN_43afbf44(param_1);
          FUN_43b03a80(auStack_284,DAT_44022af4);
          uVar13 = FUN_43b03a70(iVar11);
          uVar13 = FUN_4380d708(auStack_284,uVar13,iVar11);
          iVar23 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
          if (iVar23 != 0) {
            FUN_43b04730();
          }
          FUN_43ae7542(iVar11 + 0x1c);
          FUN_43ae7542(iVar11 + 0x94);
          goto LAB_4355249c;
        }
      }
    }
    else {
      uStack_374 = *(undefined4 *)(iVar11 + 0x15c);
      uStack_370 = *(undefined4 *)(iVar11 + 0x160);
      uStack_36c = *(undefined4 *)(iVar11 + 0x164);
      uStack_368 = *(undefined4 *)(iVar11 + 0x168);
      uStack_364 = *(undefined4 *)(iVar11 + 0x16c);
      uStack_360 = *(undefined4 *)(iVar11 + 0x170);
      uStack_35c = *(undefined4 *)(iVar11 + 0x174);
      uStack_358 = *(undefined4 *)(iVar11 + 0x178);
      uStack_354 = *(undefined4 *)(iVar11 + 0x17c);
      uStack_350 = *(undefined4 *)(iVar11 + 0x180);
      FUN_43ae7542(iVar11 + 0x15c);
      FUN_43afb42e(&uStack_3ec);
      FUN_43afb46a(&uStack_220,0);
      uStack_3ec = uStack_220;
      uStack_3e8 = uStack_21c;
      uStack_3e4 = uStack_218;
      uStack_3e0 = uStack_214;
      uStack_3dc = uStack_210;
      iStack_3d8 = 4;
      uStack_3a8 = 0;
      uStack_3ac = 5;
      FUN_43b03af4(auStack_234,DAT_44023534);
      FUN_43afb446(auStack_248,DAT_44024860);
      uVar13 = FUN_437dcfc8(auStack_234,auStack_248,iVar11);
      iVar23 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
      if (iVar23 != 0) {
        FUN_437e59dc(iVar23,1);
      }
      *(undefined4 *)(iVar11 + 0x15c) = uStack_374;
      *(undefined4 *)(iVar11 + 0x160) = uStack_370;
      *(undefined4 *)(iVar11 + 0x164) = uStack_36c;
      *(undefined4 *)(iVar11 + 0x168) = uStack_368;
      *(undefined4 *)(iVar11 + 0x16c) = uStack_364;
      *(undefined4 *)(iVar11 + 0x170) = uStack_360;
      *(undefined4 *)(iVar11 + 0x174) = uStack_35c;
      *(undefined4 *)(iVar11 + 0x178) = uStack_358;
      *(undefined4 *)(iVar11 + 0x17c) = uStack_354;
      *(undefined4 *)(iVar11 + 0x180) = uStack_350;
      FUN_43ae7542(&uStack_374);
LAB_4355249c:
      FUN_43ae7534(&uStack_374);
    }
    if ((*(char *)(iVar11 + 0xd71) != '\0') && (iVar23 = FUN_43560d38(0x20,0), iVar23 == 0)) {
      FUN_43798204(1,1,0);
      FUN_43560d1c(0x20);
    }
    *(undefined4 *)(iVar11 + 0xbc) = uStack_34c;
    *(undefined4 *)(iVar11 + 0xc0) = uStack_348;
    *(undefined4 *)(iVar11 + 0xc4) = uStack_344;
    *(undefined4 *)(iVar11 + 200) = uStack_340;
    *(undefined4 *)(iVar11 + 0xcc) = uStack_33c;
    *(undefined4 *)(iVar11 + 0xd0) = uStack_338;
    *(undefined4 *)(iVar11 + 0xd4) = uStack_334;
    *(undefined4 *)(iVar11 + 0xd8) = uStack_330;
    *(undefined4 *)(iVar11 + 0xdc) = uStack_32c;
    *(undefined4 *)(iVar11 + 0xe0) = uStack_328;
    FUN_43ae7542(&uStack_34c);
LAB_435524dc:
    FUN_43ae7534(&uStack_34c);
    return 5;
  default:
    FUN_43813cac(3,9,1,&DAT_43cb0f14);
    FUN_43902718(s_Sequence_Stage_Error__43cb0f28);
    return 5;
  }
  switch(*(undefined4 *)(iVar11 + 0xd5c)) {
  case 0:
    FUN_43b0417e(0xe,0xffffffff,1,iVar23);
    break;
  case 1:
    FUN_43b0417e(0xc,0xffffffff,1,iVar23);
    iVar18 = *(int *)(iVar11 + 0xc54);
    uVar25 = 0x11;
    puVar12 = auStack_34;
    goto LAB_43550d9e;
  case 2:
    FUN_43b0417e(4,0xffffffff,1,iVar23);
    iVar18 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,7,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_40);
    if (iVar18 == 0) {
      return 5;
    }
    uVar25 = 0x12;
    iVar18 = *(int *)(iVar11 + 0xc54);
    puVar12 = &uStack_3c;
LAB_43550d9e:
    iVar18 = FUN_43799a94(1,uVar25,0x43,iVar23,0,1,0,iVar18 + 1,0,iVar24,puVar12);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,9,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc6c);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43ae8c4a(iVar23 + 1);
    iVar18 = iVar18 << 8;
    iVar24 = FUN_439035e0(iVar11 + 0x15c,0x293,iVar18,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    uVar25 = 0x20221c;
    if (*(char *)(iVar11 + 0xc89) != '\0') {
      uVar25 = 0x20221d;
    }
LAB_435510b4:
    iVar18 = FUN_439035e0(iVar11 + 0xbc,uVar25,iVar18,1,0,5);
    if (iVar18 != 0) {
      return 5;
    }
    break;
  case 3:
    FUN_43b0417e(8,0xffffffff,1,iVar23);
    iVar18 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,10,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xd14);
    if (iVar18 == 0) {
      return 5;
    }
    uVar25 = 0x14;
    iVar18 = *(int *)(iVar11 + 0xc54);
    puVar12 = &uStack_38;
    goto LAB_4355103c;
  case 4:
    iVar18 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,10,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xd14);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,0x14,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_38)
    ;
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,7,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_40);
    if (iVar18 == 0) {
      return 5;
    }
    uVar25 = 0x12;
    iVar18 = *(int *)(iVar11 + 0xc54);
    puVar12 = &uStack_3c;
LAB_4355103c:
    iVar18 = FUN_43799a94(1,uVar25,0x43,iVar23,0,1,0,iVar18 + 1,0,iVar24,puVar12);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43799a94(1,9,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc6c);
    if (iVar18 == 0) {
      return 5;
    }
    iVar18 = FUN_43ae8c4a(iVar23 + 1);
    iVar18 = iVar18 << 8;
    iVar24 = FUN_439035e0(iVar11 + 0x15c,0x293,iVar18,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    uVar25 = 0x20221c;
    goto LAB_435510b4;
  default:
    FUN_43813cac(5,0,1,&DAT_43c9b47c,s_Sequence_Movie_cpp_43cb31f1,0x3dc);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_Movie_cpp_43cb31f1,0x3dc);
  }
  if (*(char *)(iVar11 + 0xc18) == '\0') {
    uVar25 = 1;
  }
  else if (DAT_43f9b2b0 < 0x3c) {
    uVar25 = 0x11;
  }
  else {
    uVar25 = 1;
  }
  iVar24 = iVar11 + 0x1c;
  iVar18 = FUN_43ae8c4a(iVar23 + 1);
  iVar18 = FUN_439035e0(iVar24,*(undefined4 *)(iVar11 + 0x18c),iVar18 << 8,uVar25,0,5);
  if (iVar18 != 0) {
    DAT_43f9b2b0 = DAT_43f9b2b0 + 1;
    return 5;
  }
  DAT_43f9b2b0 = 0;
  iVar18 = FUN_439fdec4();
  if (iVar18 != 0) {
    iVar18 = FUN_4390366c(iVar11 + 0x134,iVar24,1,5);
    if (iVar18 != 0) {
      FUN_43813cac(3,9,1,&DAT_43cb3204);
      FUN_43902718(s____Error___MemMgrWrapper__AllocS_43cb3218);
      FUN_43ae7542(iVar11 + 0x134);
    }
  }
  iVar18 = FUN_4378f9b4();
  if (*(char *)(*(int *)(iVar18 + 0x50) + 0x1c) != '\0') {
    FUN_43780188(iVar24);
  }
  if (*(char *)(iVar11 + 0xd4c) != '\0') {
    *(int *)(iVar11 + 0xd50) = iVar23;
    *(undefined1 *)(iVar11 + 0xd4c) = 0;
  }
  if (*(char *)(iVar11 + 0xc68) != '\0') {
    iVar18 = FUN_4390366c(iVar11 + 0x6c,iVar24,0,5);
    if (iVar18 != 0) {
      FUN_43813cac(3,9,1,&DAT_43cb323f,*(undefined2 *)(iVar11 + 0x1c));
      FUN_43902718(s____Error___AllocShare_uhndl__d__43cb3253,*(undefined2 *)(iVar11 + 0x1c));
      return 5;
    }
    *(undefined2 *)(iVar11 + 0xc6a) = *(undefined2 *)(iVar11 + 0x6c);
  }
  iVar18 = FUN_4378f9b4();
  if (((*(byte *)(*(int *)(iVar18 + 8) + 0x26a) & 1) != 0) &&
     (iVar18 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar18 + 8) + 0x268) & 4) != 0)) {
    iVar18 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd26) = *(undefined2 *)(*(int *)(iVar18 + 0x2c) + 0x96);
    iVar18 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd28) = *(undefined2 *)(*(int *)(iVar18 + 0x2c) + 0x98);
    iVar18 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd2a) = *(undefined2 *)(*(int *)(iVar18 + 0x2c) + 0x9a);
    iVar18 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd2c) = *(undefined2 *)(*(int *)(iVar18 + 0x2c) + 0x9c);
    iVar18 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar18 + 0x2c) + 0xa4) != 0) {
      iVar18 = FUN_4378f9b4();
      dVar30 = (double)VectorUnsignedToFloat
                                 ((uint)*(ushort *)(*(int *)(iVar18 + 0x38) + 0x38),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar18 = FUN_4378f9b4();
      dVar31 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar18 + 0x2c) + 0xa0),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar18 = FUN_4378f9b4();
      dVar32 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar18 + 0x2c) + 0xa4),
                                  (byte)(in_fpscr >> 0x16) & 3);
      dVar32 = (dVar30 * 100.0 * dVar31) / dVar32;
      if (((int)((uint)(dVar32 < 126500.0) << 0x1f) < 0) &&
         (uVar22 = VectorFloatToUnsigned(dVar32,3), uVar22 != 0)) {
        if (uVar22 < 0x31ce) {
          cVar8 = FUN_4355faf0(uVar22 + 0x32,100);
          bVar9 = cVar8 << 1;
        }
        else {
          cVar8 = FUN_4355faf0(uVar22 + 500,1000);
          bVar9 = cVar8 << 1 | 1;
        }
        *(byte *)(iVar11 + 0xd2e) = bVar9;
        goto LAB_435512d4;
      }
    }
    *(undefined1 *)(iVar11 + 0xd2e) = 0xff;
  }
LAB_435512d4:
  FUN_43b03a5e(&uStack_4f0);
  FUN_43811484(iVar11,iVar23);
  FUN_43ae8c4a(iVar23 - *(int *)(iVar11 + 0xd50));
  if (*(char *)(iVar11 + 400) == '\0') {
    FUN_43ae9e86(*(undefined2 *)(iVar11 + 0x19e),0x40);
  }
  else {
    FUN_43ae98f8();
  }
  uStack_3fc = 0xffffffff;
  if (*(char *)(iVar11 + 0xd80) != '\0') {
    uStack_3fc = *(undefined4 *)(iVar11 + 0xd7c);
  }
  uStack_3f8 = *(undefined4 *)(iVar11 + 0x1b0);
  iStack_3f4 = *(int *)(iVar11 + 0xd84);
  uStack_3f0 = iStack_3f4 != 0;
  puVar12 = (undefined4 *)FUN_4378f9b4();
  uStack_3ef = *(short *)*puVar12 == 0x109;
  iVar23 = FUN_43ae8c4a(iVar23 + *(int *)(iVar11 + 0xc54) + 1);
  iVar18 = FUN_4378f9b4();
  uStack_44 = (int)(uint)*(ushort *)(*(int *)(iVar18 + 4) + 0x20) >> 2;
  FUN_43ad2dfc(0xfff,&uStack_44);
  iVar26 = *(int *)(iVar11 + 0xc54) + 2;
  iVar18 = FUN_4378f9b4();
  iVar18 = FUN_4355faf0(*(int *)(*(int *)(iVar18 + 4) + 0x18) + 0x3e7ff,0x3e800);
  switch(*(undefined4 *)(iVar11 + 0xd5c)) {
  case 1:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    if (*(char *)(iVar11 + 0xc89) == '\0') {
      uVar25 = 1;
    }
    else {
      uVar25 = 4;
    }
    *(undefined4 *)(iVar11 + 0x738) = uVar25;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar13,0);
    uVar25 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar13 = FUN_4378f9b4();
    uStack_3c = auStack_34[0];
    break;
  case 2:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    if (*(char *)(iVar11 + 0xc89) == '\0') {
      uVar25 = 1;
    }
    else {
      uVar25 = 4;
    }
    *(undefined4 *)(iVar11 + 0x738) = uVar25;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar13,0);
    uVar6 = *(undefined2 *)(iVar11 + 0x19e);
    uStack_38 = auStack_34[0];
    goto LAB_4355161a;
  case 3:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x738) = 6;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar13);
    uVar25 = *(undefined4 *)(iVar11 + 0xd14);
    uVar13 = FUN_4378f9b4();
    FUN_43815be0(iVar11,uVar25,uVar13,auStack_34[0],uStack_38,*(undefined2 *)(iVar11 + 0x19e));
    uVar25 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar13 = FUN_4378f9b4();
    uStack_3c = uStack_38;
    break;
  case 4:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    *(undefined4 *)(iVar11 + 0x738) = 6;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar13,0);
    uVar25 = *(undefined4 *)(iVar11 + 0xd14);
    uVar13 = FUN_4378f9b4();
    FUN_43815be0(iVar11,uVar25,uVar13,auStack_34[0],uStack_38,*(undefined2 *)(iVar11 + 0x19e));
    uVar6 = *(undefined2 *)(iVar11 + 0x19e);
LAB_4355161a:
    FUN_43815e94(iVar11,uStack_40,uStack_38,uStack_3c,0,uVar6,0);
    uVar25 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar13 = FUN_4378f9b4();
    break;
  default:
    FUN_43813cac(5,0,1,&DAT_43c9b47c,s_Sequence_Movie_cpp_43cb31f1,0x4f9);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_Movie_cpp_43cb31f1,0x4f9);
  case 0:
    *(undefined4 *)(iVar11 + 0x6a4) = 1;
    *(undefined4 *)(iVar11 + 0x738) = 1;
    *(undefined4 *)(iVar11 + 0x6a8) = *(undefined4 *)(iVar11 + 0x24);
    *(undefined4 *)(iVar11 + 0x69c) = 0;
    *(undefined4 *)(iVar11 + 0x6ac) = *(undefined4 *)(iVar11 + 0x28);
    *(uint *)(iVar11 + 0x6c8) = (uint)(*(char *)(iVar11 + 400) != '\0');
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar13);
    goto LAB_435516bc;
  }
  FUN_43814ea0(iVar11,uVar25,uVar13,&uStack_4f0,uStack_3c,iVar23 * 0x100 + (uStack_44 >> 4),
               iVar26 * iVar18);
LAB_435516bc:
  FUN_435564e0(iVar11,*(int *)(iVar11 + 0xc54) << 2,cVar1);
  if (((*(int *)(iVar11 + 0x3dc) == 0) && (iVar15 = FUN_437286bc(), iVar15 != 0)) &&
     (iVar27 = *(int *)(iVar11 + 0x1b4), iVar15 = FUN_4378f9b4(),
     iVar27 == *(int *)(*(int *)(iVar15 + 8) + 0x28))) {
    if ((*(int *)(iVar11 + 0xd60) != 1) || (DAT_4402546c[0x9d] == 0)) {
      FUN_4379b44c(0,&uStack_4f0);
    }
    if ((*(int *)(iVar11 + 0xd60) != 1) ||
       (piVar19 = (int *)FUN_4378f9b4(), *(int *)(*piVar19 + 0x2c) == 1)) {
      FUN_4379b44c(1,&uStack_4f0);
    }
  }
  if (*(int *)(iVar11 + 0xd60) == 1) {
    FUN_439c5320(iVar11 + 0xc90,auStack_48c,0x80);
  }
  FUN_43b03a74(auStack_180,DAT_44023a28);
  FUN_43796910(param_1,auStack_180,iVar11);
  iVar15 = FUN_4378f9b4();
  if ((*(byte *)(*(int *)(iVar15 + 8) + 0x267) & 0x80) != 0) {
    FUN_437fe4d4();
  }
  if (*(int *)(iVar11 + 0x3dc) == 0) {
    iVar15 = iVar23;
    iVar27 = iVar26;
    iVar17 = iVar23;
    iVar28 = iVar26;
    if (*(char *)(iVar11 + 0x20d) != '\0') {
      iVar16 = FUN_43ae9674(iVar11 + 0x15c);
      iVar21 = *(int *)(iVar11 + 0xc60);
      if (iVar16 == 0) {
        iVar15 = FUN_43ae8c4a(iVar23 + iVar21);
        iVar27 = iVar21 + iVar26;
      }
      else {
        iVar17 = FUN_43ae8c4a(iVar23 + iVar21);
        iVar28 = iVar26 + iVar21;
      }
    }
    if (*(int *)(iVar11 + 0xd60) == 1) {
      iVar27 = *(int *)(iVar11 + 0xc5c);
      iVar15 = FUN_43ae8c4a(iVar23 + iVar27);
      iVar27 = iVar27 + iVar26;
    }
    FUN_43b2a2d0(iVar24,iVar15 * 0x100 + (uStack_44 >> 4),iVar18 * iVar27,0,5);
    FUN_43b2a2d0(iVar11 + 0x15c,iVar17 * 0x100 + (uStack_44 >> 4),iVar18 * iVar28,0,5);
  }
  if (*(int *)(iVar11 + 0xd60) != 1) {
    FUN_43b2a2d0(iVar11 + 0xbc,iVar23 * 0x100 + (uStack_44 >> 4),iVar26 * iVar18,1,5);
  }
  iVar23 = *(int *)(iVar11 + 0x3dc);
  if (iVar23 == 0) {
    uStack_2fc = *(undefined4 *)(iVar11 + 0xbc);
    uStack_2f8 = *(undefined4 *)(iVar11 + 0xc0);
    uStack_2f4 = *(undefined4 *)(iVar11 + 0xc4);
    uStack_2f0 = *(undefined4 *)(iVar11 + 200);
    uStack_2ec = *(undefined4 *)(iVar11 + 0xcc);
    uStack_2e8 = *(undefined4 *)(iVar11 + 0xd0);
    uStack_2e4 = *(undefined4 *)(iVar11 + 0xd4);
    uStack_2e0 = *(undefined4 *)(iVar11 + 0xd8);
    uStack_2dc = *(undefined4 *)(iVar11 + 0xdc);
    uStack_2d8 = *(undefined4 *)(iVar11 + 0xe0);
    FUN_43ae7542(iVar11 + 0xbc);
    uStack_324 = *(undefined4 *)(iVar11 + 0x6c);
    uStack_320 = *(undefined4 *)(iVar11 + 0x70);
    uStack_31c = *(undefined4 *)(iVar11 + 0x74);
    uStack_318 = *(undefined4 *)(iVar11 + 0x78);
    uStack_314 = *(undefined4 *)(iVar11 + 0x7c);
    uStack_310 = *(undefined4 *)(iVar11 + 0x80);
    uStack_30c = *(undefined4 *)(iVar11 + 0x84);
    uStack_308 = *(undefined4 *)(iVar11 + 0x88);
    uStack_304 = *(undefined4 *)(iVar11 + 0x8c);
    uStack_300 = *(undefined4 *)(iVar11 + 0x90);
    FUN_43ae7542(iVar11 + 0x6c);
    uStack_374 = *(undefined4 *)(iVar11 + 0xe4);
    uStack_370 = *(undefined4 *)(iVar11 + 0xe8);
    uStack_36c = *(undefined4 *)(iVar11 + 0xec);
    uStack_368 = *(undefined4 *)(iVar11 + 0xf0);
    uStack_364 = *(undefined4 *)(iVar11 + 0xf4);
    uStack_360 = *(undefined4 *)(iVar11 + 0xf8);
    uStack_35c = *(undefined4 *)(iVar11 + 0xfc);
    uStack_358 = *(undefined4 *)(iVar11 + 0x100);
    uStack_354 = *(undefined4 *)(iVar11 + 0x104);
    uStack_350 = *(undefined4 *)(iVar11 + 0x108);
    FUN_43ae7542(iVar11 + 0xe4);
    uStack_34c = *(undefined4 *)(iVar11 + 0x134);
    uStack_348 = *(undefined4 *)(iVar11 + 0x138);
    uStack_344 = *(undefined4 *)(iVar11 + 0x13c);
    uStack_340 = *(undefined4 *)(iVar11 + 0x140);
    uStack_33c = *(undefined4 *)(iVar11 + 0x144);
    uStack_338 = *(undefined4 *)(iVar11 + 0x148);
    uStack_334 = *(undefined4 *)(iVar11 + 0x14c);
    uStack_330 = *(undefined4 *)(iVar11 + 0x150);
    uStack_32c = *(undefined4 *)(iVar11 + 0x154);
    uStack_328 = *(undefined4 *)(iVar11 + 0x158);
    FUN_43ae7542(iVar11 + 0x134);
    uVar10 = *(undefined1 *)(iVar11 + 0xc40);
    uVar3 = *(undefined1 *)(iVar11 + 0x213);
    uVar4 = *(undefined1 *)(iVar11 + 0x20d);
    *(undefined1 *)(iVar11 + 0x213) = 0;
    *(undefined1 *)(iVar11 + 0x20d) = 0;
    *(undefined1 *)(iVar11 + 0xc40) = 0;
    FUN_43afb42e(&uStack_3ec);
    FUN_43afb476(&uStack_3ec,DAT_44020064);
    iStack_3d8 = iVar23;
    uStack_3a8 = FUN_43afdf16(param_1);
    uStack_3ac = FUN_43afbf44(param_1);
    FUN_43b03a80(auStack_194,DAT_44022af4);
    uVar13 = FUN_43b03a70(iVar11);
    uVar13 = FUN_4380d708(auStack_194,uVar13,iVar11);
    iVar23 = FUN_4381bbf0(param_1,&uStack_3ec,uVar13);
    if (iVar23 != 0) {
      FUN_43b04730();
    }
    *(undefined4 *)(iVar11 + 0xbc) = uStack_2fc;
    *(undefined4 *)(iVar11 + 0xc0) = uStack_2f8;
    *(undefined4 *)(iVar11 + 0xc4) = uStack_2f4;
    *(undefined4 *)(iVar11 + 200) = uStack_2f0;
    *(undefined4 *)(iVar11 + 0xcc) = uStack_2ec;
    *(undefined4 *)(iVar11 + 0xd0) = uStack_2e8;
    *(undefined4 *)(iVar11 + 0xd4) = uStack_2e4;
    *(undefined4 *)(iVar11 + 0xd8) = uStack_2e0;
    *(undefined4 *)(iVar11 + 0xdc) = uStack_2dc;
    *(undefined4 *)(iVar11 + 0xe0) = uStack_2d8;
    FUN_43ae7542(&uStack_2fc);
    *(undefined4 *)(iVar11 + 0x6c) = uStack_324;
    *(undefined4 *)(iVar11 + 0x70) = uStack_320;
    *(undefined4 *)(iVar11 + 0x74) = uStack_31c;
    *(undefined4 *)(iVar11 + 0x78) = uStack_318;
    *(undefined4 *)(iVar11 + 0x7c) = uStack_314;
    *(undefined4 *)(iVar11 + 0x80) = uStack_310;
    *(undefined4 *)(iVar11 + 0x84) = uStack_30c;
    *(undefined4 *)(iVar11 + 0x88) = uStack_308;
    *(undefined4 *)(iVar11 + 0x8c) = uStack_304;
    *(undefined4 *)(iVar11 + 0x90) = uStack_300;
    FUN_43ae7542(&uStack_324);
    *(undefined4 *)(iVar11 + 0xe4) = uStack_374;
    *(undefined4 *)(iVar11 + 0xe8) = uStack_370;
    *(undefined4 *)(iVar11 + 0xec) = uStack_36c;
    *(undefined4 *)(iVar11 + 0xf0) = uStack_368;
    *(undefined4 *)(iVar11 + 0xf4) = uStack_364;
    *(undefined4 *)(iVar11 + 0xf8) = uStack_360;
    *(undefined4 *)(iVar11 + 0xfc) = uStack_35c;
    *(undefined4 *)(iVar11 + 0x100) = uStack_358;
    *(undefined4 *)(iVar11 + 0x104) = uStack_354;
    *(undefined4 *)(iVar11 + 0x108) = uStack_350;
    FUN_43ae7542(&uStack_374);
    *(undefined4 *)(iVar11 + 0x134) = uStack_34c;
    *(undefined4 *)(iVar11 + 0x138) = uStack_348;
    *(undefined4 *)(iVar11 + 0x13c) = uStack_344;
    *(undefined4 *)(iVar11 + 0x140) = uStack_340;
    *(undefined4 *)(iVar11 + 0x144) = uStack_33c;
    *(undefined4 *)(iVar11 + 0x148) = uStack_338;
    *(undefined4 *)(iVar11 + 0x14c) = uStack_334;
    *(undefined4 *)(iVar11 + 0x150) = uStack_330;
    *(undefined4 *)(iVar11 + 0x154) = uStack_32c;
    *(undefined4 *)(iVar11 + 0x158) = uStack_328;
    FUN_43ae7542(&uStack_34c);
    *(undefined1 *)(iVar11 + 0x213) = uVar3;
    *(undefined1 *)(iVar11 + 0x20d) = uVar4;
    *(undefined1 *)(iVar11 + 0xc40) = uVar10;
    FUN_43ae7534(&uStack_34c);
    FUN_43ae7534(&uStack_374);
    FUN_43ae7534(&uStack_324);
    FUN_43ae7534(&uStack_2fc);
  }
  if (*(char *)(iVar11 + 0x213) != '\0') {
    FUN_43afb45e(auStack_1a8,DAT_440256e4);
    FUN_43afb43a(auStack_1bc,0);
    uVar13 = FUN_437dcfc8(auStack_1a8,auStack_1bc,0);
    *(undefined4 *)(iVar11 + 0x3b0) = uVar13;
    return 0;
  }
  return 0;
}


/* query "435525c0" */

/* WARNING: Type propagation algorithm not settling */

undefined1 FUN_435525c0(undefined4 param_1)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  ushort uVar4;
  undefined2 uVar5;
  byte *pbVar6;
  char cVar7;
  byte bVar8;
  undefined1 uVar9;
  int iVar10;
  int *piVar11;
  undefined4 uVar12;
  int *piVar13;
  int iVar14;
  undefined4 *puVar15;
  int *piVar16;
  undefined1 *puVar17;
  undefined4 uVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int *piVar23;
  int iVar24;
  undefined4 uVar25;
  int iVar26;
  int iVar27;
  uint in_fpscr;
  double dVar28;
  uint uVar29;
  double dVar30;
  double dVar31;
  uint uStack_5bc;
  int iStack_5a8;
  int iStack_5a4;
  int iStack_5a0;
  undefined4 uStack_59c;
  int *piStack_598;
  int iStack_594;
  int iStack_590;
  undefined1 uStack_58c;
  undefined1 uStack_58b;
  undefined2 uStack_58a;
  undefined2 uStack_588;
  undefined2 uStack_586;
  undefined2 uStack_584;
  undefined2 uStack_582;
  undefined2 uStack_580;
  undefined2 uStack_57e;
  undefined2 uStack_57c;
  undefined2 uStack_57a;
  undefined2 uStack_578;
  undefined2 uStack_576;
  undefined2 uStack_574;
  int iStack_570;
  undefined1 uStack_56c;
  undefined1 uStack_56b;
  undefined1 uStack_56a;
  int iStack_568;
  int iStack_564;
  int iStack_560;
  int iStack_55c;
  undefined1 uStack_558;
  undefined4 uStack_554;
  undefined4 uStack_550;
  int iStack_54c;
  int iStack_548;
  undefined1 auStack_544 [68];
  undefined1 uStack_500;
  undefined1 uStack_4e0;
  int iStack_4c4;
  undefined2 uStack_4c0;
  undefined2 uStack_4be;
  undefined2 uStack_4bc;
  undefined2 uStack_4ba;
  undefined1 uStack_4b8;
  int iStack_4b4;
  int iStack_4b0;
  int iStack_4ac;
  undefined1 uStack_4a8;
  undefined1 uStack_4a7;
  int iStack_4a4;
  int iStack_4a0;
  int iStack_49c;
  undefined4 uStack_498;
  int *piStack_494;
  int iStack_490;
  int iStack_48c;
  undefined1 uStack_488;
  undefined1 uStack_487;
  undefined2 uStack_486;
  undefined2 uStack_484;
  undefined2 uStack_482;
  undefined2 uStack_480;
  undefined2 uStack_47e;
  undefined2 uStack_47c;
  undefined2 uStack_47a;
  undefined2 uStack_478;
  undefined2 uStack_476;
  undefined2 uStack_474;
  undefined2 uStack_472;
  undefined2 uStack_470;
  int iStack_46c;
  char cStack_468;
  undefined1 uStack_467;
  undefined1 uStack_466;
  int iStack_464;
  int iStack_460;
  int iStack_45c;
  int iStack_458;
  undefined1 uStack_454;
  undefined4 uStack_450;
  undefined4 uStack_44c;
  int iStack_448;
  int iStack_444;
  undefined1 auStack_440 [68];
  undefined1 uStack_3fc;
  undefined1 uStack_3dc;
  int iStack_3c0;
  undefined2 uStack_3bc;
  undefined2 uStack_3ba;
  undefined2 uStack_3b8;
  undefined2 uStack_3b6;
  undefined1 uStack_3b4;
  int iStack_3b0;
  int iStack_3ac;
  int iStack_3a8;
  undefined1 uStack_3a4;
  undefined1 uStack_3a3;
  undefined4 uStack_3a0;
  undefined4 uStack_39c;
  undefined4 uStack_398;
  undefined4 uStack_394;
  undefined4 uStack_390;
  undefined4 uStack_38c;
  undefined4 uStack_360;
  undefined1 uStack_35c;
  undefined4 uStack_358;
  undefined1 uStack_354;
  undefined1 uStack_353;
  byte bStack_352;
  int iStack_350;
  undefined1 uStack_348;
  undefined1 uStack_347;
  int iStack_344;
  int iStack_340;
  int iStack_33c;
  undefined1 uStack_337;
  undefined1 uStack_335;
  undefined1 uStack_334;
  undefined1 uStack_332;
  undefined1 uStack_331;
  int iStack_330;
  undefined1 uStack_32c;
  int iStack_328;
  int iStack_324;
  int iStack_320;
  int iStack_31c;
  int iStack_318;
  int iStack_314;
  int iStack_310;
  int iStack_30c;
  int iStack_308;
  int iStack_304;
  int iStack_300;
  int iStack_2fc;
  int iStack_2f8;
  int iStack_2f4;
  int iStack_2f0;
  int iStack_2ec;
  int iStack_2e8;
  int iStack_2e4;
  int iStack_2e0;
  int iStack_2dc;
  int iStack_2d8;
  int iStack_2d4;
  int iStack_2d0;
  int iStack_2cc;
  int iStack_2c8;
  int iStack_2c4;
  int iStack_2c0;
  int iStack_2bc;
  int iStack_2b8;
  int iStack_2b4;
  int iStack_2b0;
  int iStack_2ac;
  int iStack_2a8;
  int iStack_2a4;
  int iStack_2a0;
  int iStack_29c;
  int iStack_298;
  int iStack_294;
  int iStack_290;
  int iStack_28c;
  undefined4 uStack_288;
  undefined4 uStack_284;
  undefined4 uStack_280;
  undefined4 uStack_27c;
  undefined4 uStack_278;
  undefined4 uStack_274;
  undefined4 uStack_270;
  undefined4 uStack_26c;
  undefined4 uStack_268;
  undefined4 uStack_264;
  undefined4 uStack_260;
  undefined4 uStack_25c;
  undefined4 uStack_258;
  undefined4 uStack_254;
  int iStack_250;
  int iStack_24c;
  undefined2 uStack_248;
  undefined2 uStack_246;
  undefined2 uStack_244;
  undefined2 uStack_242;
  undefined2 uStack_240;
  undefined2 uStack_23e;
  undefined1 auStack_238 [20];
  undefined1 auStack_224 [20];
  undefined1 auStack_210 [20];
  undefined1 auStack_1fc [20];
  undefined1 auStack_1e8 [20];
  undefined1 auStack_1d4 [20];
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined4 uStack_1b8;
  undefined4 uStack_1b4;
  undefined4 uStack_1b0;
  undefined1 auStack_1ac [20];
  undefined1 auStack_198 [20];
  undefined1 auStack_184 [20];
  undefined1 auStack_170 [20];
  undefined1 auStack_15c [20];
  undefined1 auStack_148 [20];
  undefined1 auStack_134 [20];
  undefined1 auStack_120 [20];
  undefined1 auStack_10c [20];
  undefined1 auStack_f8 [20];
  undefined1 auStack_e4 [20];
  undefined1 auStack_d0 [20];
  undefined1 auStack_bc [20];
  undefined1 auStack_a8 [20];
  undefined1 auStack_94 [20];
  undefined1 auStack_80 [4];
  int iStack_7c;
  int iStack_78;
  int iStack_74;
  undefined1 auStack_70 [8];
  int iStack_68;
  int iStack_64;
  int aiStack_60 [5];
  undefined1 auStack_4c [4];
  int aiStack_48 [4];
  undefined4 uStack_38;
  undefined4 auStack_34 [2];
  
  iVar10 = FUN_4378f9b4();
  iVar21 = **(int **)(iVar10 + 4);
  iVar10 = FUN_4378f9b4();
  cVar1 = *(char *)(*(int *)(iVar10 + 8) + 0x33);
  piVar11 = (int *)FUN_43ae75dc(param_1);
  if ((char)piVar11[0x35c] != '\0') {
    return 5;
  }
  uVar12 = FUN_43afdf16(param_1);
  switch(uVar12) {
  case 0:
    iVar10 = FUN_43795b04();
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(1,0,piVar11[0x7f],iVar21,0,1,0,2,0,piVar11 + 0x35a,0);
    uVar12 = DAT_44025f5c;
    if (iVar10 != 0) {
      iVar10 = FUN_43ae8cc8(DAT_44025f5c);
      pbVar6 = DAT_4402546c;
      if (iVar10 != 0) {
        if (*DAT_4402546c != 0) {
          iVar10 = FUN_43799a94(1,2,0,iVar21,0,1,0,2,0,piVar11 + 0x35a,piVar11 + 0x147);
          if (iVar10 == 0) {
            return 5;
          }
          FUN_43728c18(piVar11 + 0x142,piVar11 + 0x143,piVar11 + 0x144);
          FUN_43acc282(piVar11[0x147],*pbVar6 - 1,piVar11 + 0xf9,0xfff,0xfff,0xfff);
        }
        FUN_4378e5ac(uVar12);
      }
      FUN_43b03a74(auStack_94,DAT_4402110c);
      FUN_43796910(param_1,auStack_94,piVar11);
      uVar12 = FUN_438148f0();
      FUN_43b04040(uVar12,piVar11[0x7c],iVar21,piVar11[0x7e],piVar11[0x313],piVar11[0x6c]);
      return 0;
    }
    return 5;
  case 1:
    iVar10 = FUN_4378f9b4();
    if ((*(int *)(*(int *)(iVar10 + 8) + 0x1e8) != 0) && (piVar11[0x7f] != 9)) {
      return 1;
    }
    uVar12 = FUN_4378f9b4();
    iVar10 = FUN_4378e6a0(DAT_44025f5c,uVar12);
    if (iVar10 == 0) {
      return 5;
    }
    piVar16 = piVar11 + 0x35a;
    iVar10 = FUN_43799a94(1,2,0,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,piVar11 + 0x147);
    if (iVar10 == 0) {
      return 5;
    }
    FUN_43728c18(piVar11 + 0x142,piVar11 + 0x143,piVar11 + 0x144);
    pbVar6 = DAT_4402546c;
    uVar9 = *(undefined1 *)((int)piVar11 + 0x3fa);
    if (DAT_4402546c[0x4e] == 0xff) {
      uVar9 = 0;
    }
    else if (DAT_4402546c[0x4e] != 0) {
      uVar9 = 1;
    }
    iVar10 = piVar11[0x147];
    uVar12 = FUN_437d9d08();
    FUN_43acc2ee(iVar10,uVar9,uVar12);
    iVar10 = FUN_43799a94(1,0x10,0x43,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,aiStack_48);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(2,0x10,0x43,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,aiStack_48 + 1);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(1,4,0,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,piVar11 + 0x308);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(2,4,0,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,piVar11 + 0x309);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_4381c04c(0,piVar11[0x61],auStack_70);
    if (iVar10 == 0) {
      *(undefined1 *)(piVar11 + 0x149) = 0;
      *(undefined1 *)(piVar11 + 0x83) = 0;
    }
    if ((pbVar6[2] & 1) == 0) {
      iVar10 = 10;
    }
    else {
      iVar10 = 0xb;
    }
    piVar11[0x166] = iVar10;
    piVar11[0x167] = 2;
    piVar11[0x175] = 1;
    iVar10 = piVar11[0x62];
    piVar11[0x168] = aiStack_48[0];
    piVar11[0x176] = iStack_68;
    piVar11[0x172] = 0;
    piVar11[0x173] = 0;
    piVar11[0x177] = iStack_64;
    piVar11[0x17f] = 0;
    piVar11[0x17e] = (uint)((char)iVar10 != '\0');
    FUN_439c5320(piVar11 + 0x180,piVar11 + 0x166,0x68);
    piVar11[0x182] = aiStack_48[1];
    if ((((char)iVar10 != '\0') && (piVar11[0x35e] == 1)) &&
       (*(short *)((int)piVar11 + 0x19e) == 0x5a0)) {
      *(undefined2 *)((int)piVar11 + 0x19e) = 0x5c0;
    }
    if (((piVar11[0x6c] - 2U < 2) &&
        (iVar10 = FUN_4378f9b4(), *(int *)(*(int *)(iVar10 + 4) + 0xc) != 0)) &&
       (piVar11[0x7f] != 9)) {
      bVar8 = 0;
      *(undefined1 *)((int)piVar11 + 0x1ee) = 0;
    }
    else if (((char)piVar11[0x350] == '\0') || (*(char *)((int)piVar11 + 0xd41) == '\0')) {
      iVar10 = FUN_4378f9b4();
      bVar2 = *(byte *)(*(int *)(iVar10 + 8) + 0x268);
      bVar8 = bVar2 & 2;
      if ((bVar2 & 2) != 0) goto LAB_43552998;
    }
    else {
      bVar8 = 0;
    }
    *(byte *)(piVar11 + 0x83) = bVar8;
LAB_43552998:
    iVar10 = FUN_43799a94(1,0xe,0,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,0);
    if (iVar10 == 0) {
      return 5;
    }
    if ((pbVar6[0x70] == 0) && (iVar10 = FUN_4378003c(), iVar10 == 0)) {
      uStack_358 = 2;
      uStack_354 = *(undefined1 *)((int)piVar11 + 0x20e);
      uStack_335 = 0;
      uStack_353 = *(undefined1 *)((int)piVar11 + 0x20f);
      bStack_352 = pbVar6[0xab] & 1 ^ 1;
      uStack_334 = 0;
      iStack_350 = piVar11[0x82];
      uStack_332 = 0;
      uStack_331 = 0;
      *(byte *)(piVar11 + 0x84) = bStack_352;
      uStack_348 = (undefined1)piVar11[0x7f];
      uStack_347 = (undefined1)piVar11[0x313];
      iStack_344 = piVar11[0x7b];
      iStack_340 = piVar11[0x7c];
      iStack_33c = piVar11[0x7d];
      uStack_337 = (undefined1)piVar11[0xf8];
      uStack_32c = piVar11[0x35e] == 1;
      iStack_330 = iVar10;
      FUN_439e34d4(&uStack_358);
    }
    FUN_43799a94(1,0xf,0,iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,0);
    if (((char)piVar11[0x83] == '\0') && (*(char *)((int)piVar11 + 0x213) != '\0')) {
      *(undefined1 *)((int)piVar11 + 0x213) = 0;
    }
    if (*(char *)((int)piVar11 + 0x213) != '\0') {
      uVar12 = FUN_43799f3c();
      FUN_4379a20c(uVar12,5,piVar11 + 0x39);
      FUN_43903720(piVar11 + 0x39,0,0,5);
    }
    iVar10 = FUN_43799a94(1,0xd,piVar11[0x7f],iVar21,0,1,0,piVar11[0x313] + 1,0,piVar16,
                          piVar11 + 0x148);
    if (iVar10 == 0) {
      return 5;
    }
    FUN_43728c4c(piVar11 + 0x145,piVar11 + 0x146);
    FUN_437956a4(piVar11[0x148]);
    FUN_43814008(piVar11);
    FUN_43b03a74(auStack_a8,DAT_44022cc8);
    FUN_43796910(param_1,auStack_a8,piVar11);
    uVar12 = DAT_44023820;
    if (*(char *)((int)piVar11 + 0x525) == '\0') {
      FUN_438106ec(piVar11);
      FUN_43b03a74(auStack_bc,uVar12);
      puVar17 = auStack_bc;
    }
    else {
      FUN_43b03a74(auStack_d0,DAT_44026238);
      FUN_43797090(param_1,auStack_d0,piVar11);
      FUN_43b03a74(auStack_e4,uVar12);
      puVar17 = auStack_e4;
    }
    FUN_43797090(param_1,puVar17,piVar11);
    uVar12 = DAT_44021e0c;
    if (cVar1 == '\0') {
      FUN_43b03a74(auStack_120,DAT_440204b4);
      FUN_43796910(param_1,auStack_120,piVar11);
      FUN_43b03a74(auStack_134,uVar12);
      FUN_43796910(param_1,auStack_134,piVar11);
    }
    else {
      FUN_43b03a74(auStack_f8,DAT_440204b4);
      FUN_43797090(param_1,auStack_f8,piVar11);
      FUN_43b03a74(auStack_10c,uVar12);
      FUN_43797090(param_1,auStack_10c,piVar11);
    }
    FUN_43b03a74(auStack_148,DAT_44024a24);
    FUN_43796910(param_1,auStack_148,piVar11);
    FUN_43b03a74(auStack_15c,DAT_440259b4);
    FUN_4379704c(param_1,auStack_15c,piVar11);
    if ((char)piVar11[0x83] == '\0') {
      return 5;
    }
    if (piVar11[0x359] == 2) {
      return 0;
    }
    FUN_43afb42e(&uStack_3a0);
    FUN_43afb476(&uStack_3a0,DAT_44020064);
    uStack_38c = 0;
    uStack_35c = 2;
    uStack_360 = FUN_43afbf44(param_1);
    (**(code **)(*piVar11 + 8))(piVar11);
    iVar10 = FUN_4381bbf0(param_1,&uStack_3a0,piVar11);
    if (iVar10 == 0) {
      return 5;
    }
    FUN_43b04730();
    return 5;
  case 2:
    break;
  case 3:
    iVar10 = piVar11[0x316];
    piVar11[0x316] = iVar10 + 1U;
    if (iVar10 + 1U < (uint)piVar11[0x315]) {
      return 1;
    }
    if (*(char *)((int)piVar11 + 0x213) != '\0') {
      FUN_43ae7558(&iStack_300);
      iVar10 = FUN_43903558(&iStack_300,0x173425,1,0,5);
      if (iVar10 != 0) {
        FUN_43813d58(3,9,1,&DAT_43cb3273);
        FUN_43902718(s__DualRec__Can_t_Get_CAM_REG_DREC_43cb3287);
        goto LAB_435544d4;
      }
      piVar11[0x43] = iStack_300;
      piVar11[0x44] = iStack_2fc;
      piVar11[0x45] = iStack_2f8;
      piVar11[0x46] = iStack_2f4;
      piVar11[0x47] = iStack_2f0;
      piVar11[0x48] = iStack_2ec;
      piVar11[0x49] = iStack_2e8;
      piVar11[0x4a] = iStack_2e4;
      piVar11[0x4b] = iStack_2e0;
      piVar11[0x4c] = iStack_2dc;
      FUN_43ae7542(&iStack_300);
      if ((DAT_4402546c[0xc1] & 1) == 0) {
        iVar10 = FUN_43561604(piVar11[0x45]);
        FUN_43b0bf32(iVar10 + 0x3800,piVar11[0x144]);
      }
      FUN_43b2a258(piVar11 + 0x43,5);
      FUN_43ae7534(&iStack_300);
      uVar12 = FUN_43799f3c();
      FUN_43799fa8(uVar12,1);
      FUN_43799fa8(uVar12,0);
      FUN_43799fa8(uVar12,4);
      FUN_43799fa8(uVar12,5);
      FUN_43afb42e(&uStack_3a0);
      FUN_43afb46a(&uStack_1c0,0);
      uStack_3a0 = uStack_1c0;
      uStack_39c = uStack_1bc;
      uStack_398 = uStack_1b8;
      uStack_394 = uStack_1b4;
      uStack_390 = uStack_1b0;
      uStack_38c = 4;
      uStack_35c = 0;
      uStack_360 = 5;
      FUN_43b03af4(auStack_1d4,DAT_440204bc);
      FUN_43afb446(auStack_1e8,DAT_44024860);
      uVar12 = FUN_437dcfc8(auStack_1d4,auStack_1e8,piVar11);
      iVar10 = FUN_4381bbf0(param_1,&uStack_3a0,uVar12);
      if (iVar10 != 0) {
        FUN_437e59dc(iVar10,1);
      }
      FUN_43ae7542(piVar11 + 0x39);
      FUN_43ae7542(piVar11 + 0x43);
    }
    if ((piVar11[0x358] != 1) ||
       (iVar10 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar10 + 8) + 0x268) & 4) == 0))
    goto LAB_4355415a;
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 0) {
      iVar10 = 0;
      if (*(char *)((int)piVar11 + 0x199) != '\0') {
        if (piVar11[0x319] != 0) {
          piVar11[0x26c] = 1;
          goto LAB_43553c66;
        }
        iVar10 = 2;
      }
      piVar11[0x26c] = iVar10;
    }
    else {
      iVar10 = 0;
      if (*(char *)((int)piVar11 + 0x191) != '\0') {
        iVar10 = 5;
      }
      piVar11[0x26c] = iVar10;
      if (piVar11[0x319] == 0) goto LAB_4355415a;
    }
LAB_43553c66:
    piVar16 = piVar11 + 0x35a;
    iVar10 = FUN_43799a94(1,0xb,0,iVar21,0,1,0,piVar11[0x317] + 1,0,piVar16,auStack_34);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(1,0x13,0x43,iVar21,0,1,0,piVar11[0x317] + 1,0,piVar16,aiStack_48 + 3);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43799a94(1,8,0x43,iVar21,0,1,0,piVar11[0x317] + 1,0,piVar16,&uStack_38);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43ae8c4a(iVar21 + 1);
    iVar24 = FUN_439035e0(piVar11 + 0x11,piVar11[0x65],iVar10 << 8,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    if (piVar11[0x317] == 2) {
      iVar24 = FUN_4378f9b4();
      if (*(int *)(*(int *)(iVar24 + 4) + 0xc) == 1) {
        iVar24 = 0xc;
      }
      else {
        iVar24 = 0xd;
      }
    }
    else {
      iVar24 = 0xb;
    }
    piVar11[0x1b4] = iVar24;
    piVar11[0x1b5] = 0;
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 1) {
      iVar24 = FUN_43ae9674(piVar11 + 0x57);
      if (iVar24 == 0) {
        FUN_43813d58(5,0,1,&DAT_43c9b47c,s_Sequence_MovieSplit_cpp_43cb334d,0x622);
        FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_MovieSplit_cpp_43cb334d,0x622);
      }
      else {
        piVar11[0x1b8] = piVar11[0x59];
        piVar11[0x1c0] = 1;
        piVar11[0x1b7] = 1;
        piVar11[0x1b9] = piVar11[0x5a];
        *(undefined2 *)(piVar11 + 0x265) = 0;
        *(undefined2 *)((int)piVar11 + 0x996) = 0;
        *(undefined2 *)(piVar11 + 0x266) = *(undefined2 *)((int)piVar11 + 0x1aa);
        *(short *)((int)piVar11 + 0x99a) = (short)piVar11[0x6b];
      }
    }
    else {
      piVar11[0x1c0] = (uint)((char)piVar11[100] != '\0');
      piVar11[0x1b7] = 1;
      *(undefined2 *)(piVar11 + 0x265) = 0;
      piVar11[0x1b8] = piVar11[9];
      *(undefined2 *)((int)piVar11 + 0x996) = 0;
      *(undefined2 *)(piVar11 + 0x266) = *(undefined2 *)((int)piVar11 + 0x19e);
      piVar11[0x1b9] = piVar11[10];
      *(short *)((int)piVar11 + 0x99a) = (short)piVar11[0x68];
    }
    piVar11[0x1c1] = 2;
    *(undefined2 *)(piVar11 + 0x267) = 0;
    *(undefined2 *)((int)piVar11 + 0x99e) = 0;
    *(undefined2 *)(piVar11 + 0x268) = 0;
    *(undefined2 *)((int)piVar11 + 0x9a2) = 0;
    piVar11[0x1c3] = 0;
    piVar11[0x1cc] = 0;
    piVar11[0x1c2] = aiStack_48[3];
    piVar11[0x269] = 0;
    *(undefined2 *)(piVar11 + 0x26a) = 0;
    *(undefined2 *)((int)piVar11 + 0x9aa) = 0;
    *(undefined2 *)(piVar11 + 0x26b) = 0;
    *(undefined2 *)((int)piVar11 + 0x9ae) = 0;
    uVar12 = FUN_43b03bf8(*(undefined2 *)((int)piVar11 + 0x19e),(short)piVar11[0x68],
                          (char)piVar11[100]);
    uStack_26c = 4;
    uStack_268 = 7;
    uStack_264 = 0x80;
    uStack_260 = FUN_43556490(uVar12,0x80,piVar11[0x317] << 2,cVar1);
    uStack_25c = 0;
    uStack_27c = 0;
    uStack_270 = 0;
    uStack_278 = 0;
    uStack_254 = 1;
    uStack_258 = 1;
    uStack_288 = 4;
    uStack_284 = 7;
    uStack_280 = 0x80;
    uStack_274 = 1;
    iVar24 = FUN_43940f2c(auStack_34[0],&uStack_26c,&uStack_288);
    if (iVar24 != 0) {
      FUN_43813d58(3,9,1,&DAT_43cb3365,iVar24);
      FUN_43902718(s_Sequence_MovieSplit__RC_ERR_0x_0_43cb3379,iVar24);
    }
    uVar4 = *(ushort *)((int)piVar11 + 0x1a2);
    if (uVar4 < 0x3c1) {
      uVar25 = 0;
      uVar12 = 0;
    }
    else {
      if (uVar4 != 0x500) {
        FUN_43813d58(3,9,1,&DAT_43cb33b8,uVar4);
        FUN_43902718(s_Sequence_MovieSplit__SRC_>VFX_St_43cb33cc,
                     *(undefined2 *)((int)piVar11 + 0x1a2));
      }
      uVar25 = 0x280;
      uVar12 = 5;
    }
    FUN_43798490(auStack_34[0],piVar11 + 0x1b4,piVar11 + 0x262,(int)piVar11 + 0x19e,
                 (int)piVar11 + 0x1a2,piVar11[0x2f5],uVar12,1);
    FUN_43815e94(piVar11,uStack_38,aiStack_48[3],0,1,*(undefined2 *)((int)piVar11 + 0x1a2),uVar25);
    iVar24 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar24 + 4) + 0x10) == 3) {
      iVar24 = 3;
    }
    else {
      iVar24 = 2;
    }
    FUN_43b03a5e(&iStack_5a8);
    FUN_43811484(piVar11,iVar21);
    iStack_5a8 = piVar11[0x7b];
    iStack_5a4 = piVar11[0x7c];
    iStack_5a0 = piVar11[0x7d];
    uStack_59c = 0;
    iStack_590 = piVar11[0x317];
    uStack_58c = (undefined1)piVar11[0x7e];
    piStack_598 = piVar11 + 0x11;
    iStack_594 = iVar10;
    uStack_58b = FUN_43ae8c4a((iVar21 - piVar11[0x354]) - piVar11[0x316]);
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 0) {
      uStack_58a = (undefined2)piVar11[0x6e];
    }
    else {
      uStack_58a = *(undefined2 *)((int)piVar11 + 0x1a2);
    }
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 0) {
      uStack_588 = *(undefined2 *)((int)piVar11 + 0x1ba);
    }
    else {
      uStack_588 = (undefined2)piVar11[0x69];
    }
    uVar5 = *(undefined2 *)((int)piVar11 + 0x1a2);
    uStack_586 = FUN_43ae9e86(uVar5,0x40);
    uStack_584 = (undefined2)piVar11[0x69];
    uStack_582 = 0;
    iStack_570 = piVar11[0x6d];
    uStack_580 = 0;
    uStack_57a = 0;
    uStack_56c = (undefined1)piVar11[0x66];
    uStack_578 = 0;
    uStack_56b = 1;
    uStack_56a = *(undefined1 *)((int)piVar11 + 0x199);
    iStack_568 = piVar11[0x319];
    iStack_564 = piVar11[0x13f];
    iStack_560 = piVar11[0x14d];
    iStack_55c = piVar11[0x141];
    uStack_558 = piVar11[0x2f5] == 1;
    iStack_4b4 = -1;
    uStack_554 = 0xffffffff;
    uStack_550 = 0xffffffff;
    iStack_54c = piVar11[0x355];
    iStack_548 = piVar11[0x356];
    auStack_544[0] = 0;
    uStack_500 = 0;
    uStack_4e0 = 0;
    iStack_4c4 = piVar11[0x35e];
    uStack_4c0 = *(undefined2 *)((int)piVar11 + 0xd26);
    uStack_4be = (undefined2)piVar11[0x34a];
    uStack_4bc = *(undefined2 *)((int)piVar11 + 0xd2a);
    uStack_4ba = (undefined2)piVar11[0x34b];
    uStack_4b8 = *(undefined1 *)((int)piVar11 + 0xd2e);
    if ((char)piVar11[0x360] != '\0') {
      iStack_4b4 = piVar11[0x35f];
    }
    uStack_57e = uVar5;
    uStack_57c = uStack_584;
    uStack_576 = uVar5;
    uStack_574 = uStack_584;
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 0) {
      iVar24 = piVar11[0x6c];
    }
    iStack_4ac = piVar11[0x361];
    uStack_4a8 = iStack_4ac != 0;
    iStack_4b0 = iVar24;
    puVar15 = (undefined4 *)FUN_4378f9b4();
    uStack_4a7 = *(short *)*puVar15 == 0x109;
    FUN_439c5320(auStack_544,piVar11 + 0x324,0x80);
    if (DAT_4402546c[0x9d] == 1) {
      FUN_4379b44c(0,&iStack_5a8);
    }
    piVar16 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar16 + 0x2c) == 1) {
      uVar12 = 2;
    }
    else {
      uVar12 = 1;
    }
    FUN_4379b44c(uVar12,&iStack_5a8);
LAB_4355415a:
    iVar10 = FUN_43ae8c4a(iVar21 + piVar11[0x317] + 1);
    iVar21 = FUN_4378f9b4();
    aiStack_48[2] = (int)(uint)*(ushort *)(*(int *)(iVar21 + 4) + 0x20) >> 2;
    FUN_43ad2dfc(0xfff,aiStack_48 + 2);
    iVar24 = piVar11[0x317];
    iVar21 = FUN_4378f9b4();
    iVar21 = FUN_4355faf0(*(int *)(*(int *)(iVar21 + 4) + 0x18) + 0x3e7ff,0x3e800);
    FUN_43b2a2d0(piVar11 + 0x2f,iVar10 * 0x100 + ((uint)aiStack_48[2] >> 4),(iVar24 + 2) * iVar21,1,
                 5);
    iVar10 = FUN_43ae8c4a(iVar10 + 1);
    FUN_43b2a2d0(piVar11 + 0x11,iVar10 * 0x100 + ((uint)aiStack_48[2] >> 4),iVar21 * (iVar24 + 3),1,
                 5);
    return 0;
  case 4:
    iVar10 = FUN_439fdec4();
    if (iVar10 != 0) {
      DAT_43eea8a8 = (undefined2)piVar11[0x4d];
      DAT_43eea8ac = piVar11[0x4e];
      if ((char)piVar11[100] == '\0') {
        DAT_43eea8b0 = FUN_43ae9e86(*(undefined2 *)((int)piVar11 + 0x19e),0x40);
      }
      else {
        DAT_43eea8b0 = FUN_43ae98f8();
      }
      DAT_43eea8b2 = (undefined2)piVar11[0x68];
      DAT_43eea8b8 = *(undefined2 *)((int)piVar11 + 0x19e);
      DAT_43eea8b4 = 0;
      DAT_43eea8bc = (ushort)*(byte *)((int)piVar11 + 0x136);
      DAT_43eea8c0 = piVar11[0x4f];
      DAT_43eea8b6 = 0;
      DAT_43eea8c4 = piVar11[0x50];
      DAT_43eea8ba = DAT_43eea8b2;
      iVar10 = FUN_439fde5c(&DAT_43eea8a8);
      if (iVar10 != 0) {
        FUN_43ae7542(piVar11 + 0x4d);
      }
    }
    iStack_300 = piVar11[0x2f];
    iStack_2fc = piVar11[0x30];
    iStack_2f8 = piVar11[0x31];
    iStack_2f4 = piVar11[0x32];
    iStack_2f0 = piVar11[0x33];
    iStack_2ec = piVar11[0x34];
    iStack_2e8 = piVar11[0x35];
    iStack_2e4 = piVar11[0x36];
    iStack_2e0 = piVar11[0x37];
    iStack_2dc = piVar11[0x38];
    FUN_43ae7542(piVar11 + 0x2f);
    if ((char)piVar11[0x31a] != '\0') {
      FUN_43afb42e(&uStack_3a0);
      FUN_43afb476(&uStack_3a0,DAT_440219a8);
      uStack_35c = 0;
      uStack_38c = 4;
      uStack_360 = FUN_43afbf44(param_1);
      FUN_43b0417e(10,10,0,0);
      FUN_43ae7542(piVar11 + 0x1b);
      FUN_43b03a80(auStack_1fc,DAT_44022af4);
      uVar12 = FUN_43b03a70(piVar11);
      uVar12 = FUN_4380d708(auStack_1fc,uVar12,piVar11);
      iVar10 = FUN_4381bbf0(param_1,&uStack_3a0,uVar12);
      if (iVar10 != 0) {
        FUN_43b04730();
      }
    }
    if (*(char *)((int)piVar11 + 0x20d) != '\0') {
      iVar10 = FUN_437999e4(1,5);
      if (iVar10 == 0) goto LAB_435544d4;
      piVar16 = (int *)FUN_4378f9b4();
      uVar9 = FUN_43879534(*(undefined4 *)(*piVar16 + 0xb4));
      *(undefined1 *)((int)piVar11 + 0xd22) = uVar9;
      iVar10 = thunk_FUN_439dce54();
      *(char *)((int)piVar11 + 0xd72) = (char)iVar10;
      if ((iVar10 != 0) || (*(char *)((int)piVar11 + 0xd22) != '\0')) {
        FUN_43ae7558(&iStack_328);
        iVar10 = FUN_43903558(piVar11 + 0x25,0x30700,0x11,0,5);
        if (iVar10 != 0) {
          DAT_43f9b2b2 = DAT_43f9b2b2 + 1;
          if (0x3b < DAT_43f9b2b2) {
            FUN_43813d58(3,9,1,&DAT_43cb0ee4,DAT_43f9b2b2);
            FUN_43902718(s_Face_Memory_Alloc_Error___d_43cb0ef8,DAT_43f9b2b2);
          }
          FUN_43ae7534(&iStack_328);
          goto LAB_435544d4;
        }
        piVar11[0x35d] = iVar21;
        DAT_43f9b2b2 = 0;
        if ((char)piVar11[0x306] == '\0') {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1e);
        }
        else if (cVar1 == '\0') {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1c);
        }
        else {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1d);
        }
        *(undefined1 *)((int)piVar11 + 0x212) = uVar9;
        bVar8 = *(byte *)((int)piVar11 + 0x212) & 0x7f;
        if (bVar8 == 0x40) {
          FUN_43560dc4(0x1a,0xffffffdf);
          FUN_43b03a74(auStack_210,DAT_44020ee4);
          FUN_4379704c(param_1,auStack_210,piVar11);
        }
        else if (bVar8 == 0x41) {
          FUN_43560dc4(0x1a,0xffffffdf);
          FUN_43b03a74(auStack_224,DAT_44020ee4);
          FUN_43796910(param_1,auStack_224,piVar11);
        }
        else {
          FUN_43560da8(0x1a,0x20);
        }
        FUN_43afb42e(&uStack_3a0);
        FUN_43afb476(&uStack_3a0,DAT_44021fc8);
        uStack_38c = 4;
        uStack_35c = 0;
        uStack_360 = FUN_43afbf44(param_1);
        FUN_43b03a80(auStack_238,DAT_44022af4);
        uVar12 = FUN_43b03a70(piVar11);
        uVar12 = FUN_4380d708(auStack_238,uVar12,piVar11);
        iVar10 = FUN_4381bbf0(param_1,&uStack_3a0,uVar12);
        if (iVar10 != 0) {
          FUN_43b04730();
        }
        FUN_43ae7542(piVar11 + 7);
        FUN_43ae7542(piVar11 + 0x25);
        FUN_43ae7534(&iStack_328);
      }
    }
    if ((*(char *)((int)piVar11 + 0xd71) != '\0') && (iVar10 = FUN_43560d38(0x20,0), iVar10 == 0)) {
      FUN_43798204(1,1,0);
      FUN_43560d1c(0x20);
    }
    piVar11[0x2f] = iStack_300;
    piVar11[0x30] = iStack_2fc;
    piVar11[0x31] = iStack_2f8;
    piVar11[0x32] = iStack_2f4;
    piVar11[0x33] = iStack_2f0;
    piVar11[0x34] = iStack_2ec;
    piVar11[0x35] = iStack_2e8;
    piVar11[0x36] = iStack_2e4;
    piVar11[0x37] = iStack_2e0;
    piVar11[0x38] = iStack_2dc;
    FUN_43ae7542(&iStack_300);
LAB_435544d4:
    FUN_43ae7534(&iStack_300);
    return 5;
  default:
    FUN_43813d58(3,9,1,&DAT_43cb0f14);
    FUN_43902718(s_Sequence_Stage_Error__43cb0f28);
    return 5;
  }
  if ((char)piVar11[0x83] == '\0') {
    return 5;
  }
  iVar10 = piVar11[0x314];
  piVar11[0x314] = iVar10 + 1U;
  if (iVar10 + 1U < (uint)piVar11[0x313]) {
    return 1;
  }
  FUN_439c5a04(&iStack_250,0,0x18);
  uStack_248 = (undefined2)piVar11[0x31d];
  uStack_240 = *(undefined2 *)((int)piVar11 + 0x526);
  uStack_23e = *(undefined2 *)((int)piVar11 + 0x52e);
  iStack_250 = piVar11[0x30c];
  uStack_246 = (undefined2)piVar11[0x347];
  iStack_24c = piVar11[0x30d];
  uStack_242 = *(undefined2 *)((int)piVar11 + 0xd1e);
  uStack_244 = (undefined2)piVar11[0x348];
  uVar12 = FUN_438148f0();
  FUN_438149dc(uVar12,piVar11[0x7c],&iStack_250);
  if ((piVar11[0x313] & 1U) == 0) {
    iVar10 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar10 + 4) + 0xc) == 0) goto LAB_43552cfc;
    piVar11[0x319] = 0;
  }
  else {
    iVar24 = FUN_4378f9b4();
    iVar10 = 0;
    if (*(int *)(*(int *)(iVar24 + 4) + 0xc) != 0) {
LAB_43552cfc:
      iVar10 = 1;
    }
    piVar11[0x319] = iVar10;
  }
  uVar12 = 0;
  if (*(char *)((int)piVar11 + 0x191) != '\0') {
    if (piVar11[0x319] == 0) {
      uVar12 = 2;
    }
    else {
      uVar12 = 1;
    }
  }
  if ((piVar11[0x6c] - 2U < 2) && (piVar11[0x319] == 0)) {
    return 1;
  }
  piVar16 = piVar11 + 0x35a;
  iVar10 = FUN_43b03b40(5,0,iVar21,piVar11[0x315] + 1,piVar16,piVar11 + 0x30a,piVar11 + 0x30b);
  if (iVar10 == 0) {
    return 5;
  }
  if (piVar11[0x358] != 1) {
    FUN_43b0419c(1,iVar21);
  }
  switch(piVar11[0x357]) {
  case 0:
    FUN_43b0417e(0xe,0xe,1,iVar21);
    goto LAB_43552f6a;
  case 1:
    FUN_43b0417e(0xc,0xc,1,iVar21);
    iVar10 = piVar11[0x315];
    piVar13 = aiStack_48;
    piVar23 = aiStack_48 + 1;
    uVar25 = 0x11;
    break;
  case 2:
    FUN_43b0417e(4,4,1,iVar21);
    iVar10 = piVar11[0x315];
    piVar13 = aiStack_48;
    piVar23 = aiStack_48;
    uVar25 = 0x11;
    goto LAB_43552eb6;
  case 3:
    FUN_43b0417e(8,8,1,iVar21);
    iVar10 = FUN_43b03b40(0x11,0x43,iVar21,piVar11[0x315] + 1,piVar16,aiStack_48,aiStack_48 + 1);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43b03b40(10,0,iVar21,piVar11[0x315] + 1,piVar16,piVar11 + 0x345,piVar11 + 0x346);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = piVar11[0x315];
    piVar13 = aiStack_60;
    piVar23 = aiStack_60 + 1;
    uVar25 = 0x14;
    break;
  case 4:
    iVar10 = FUN_43b03b40(0x11,0x43,iVar21,piVar11[0x315] + 1,piVar16,aiStack_48,aiStack_48 + 1);
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43b03b40(10,0,iVar21,piVar11[0x315] + 1,piVar16,piVar11 + 0x345,piVar11 + 0x346);
    if (iVar10 == 0) {
      return 5;
    }
    uVar25 = 0x14;
    iVar10 = piVar11[0x315];
    piVar13 = aiStack_60;
    piVar23 = aiStack_60;
LAB_43552eb6:
    iVar10 = FUN_43b03b40(uVar25,0x43,iVar21,iVar10 + 1,piVar16,piVar13,(int *)((int)piVar23 + 4));
    if (iVar10 == 0) {
      return 5;
    }
    iVar10 = FUN_43b03b40(7,0,iVar21,piVar11[0x315] + 1,piVar16,aiStack_60 + 4,auStack_4c);
    if (iVar10 == 0) {
      return 5;
    }
    uVar25 = 0x12;
    iVar10 = piVar11[0x315];
    piVar13 = aiStack_60 + 2;
    piVar23 = aiStack_60 + 3;
    break;
  default:
    FUN_43813d58(5,0,1,&DAT_43c9b47c,s_Sequence_MovieSplit_cpp_43cb334d,0x337);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_MovieSplit_cpp_43cb334d,0x337);
    goto LAB_43552f6a;
  }
  iVar10 = FUN_43b03b40(uVar25,0x43,iVar21,iVar10 + 1,piVar16,piVar13,piVar23);
  if ((iVar10 == 0) ||
     (iVar10 = FUN_43b03b40(9,0,iVar21,piVar11[0x315] + 1,piVar16,piVar11 + 0x31b,piVar11 + 0x31c),
     iVar10 == 0)) {
    return 5;
  }
LAB_43552f6a:
  iVar10 = piVar11[0x357];
  if (iVar10 != 0) {
    if ((iVar10 < 0) || (4 < iVar10)) {
      FUN_43813d58(5,0,1,&DAT_43c9b47c,s_Sequence_MovieSplit_cpp_43cb334d,0x363);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_MovieSplit_cpp_43cb334d,0x363);
      return 5;
    }
    if (*(ushort *)((int)piVar11 + 0x19e) < 0x781) {
      uVar25 = 0x293;
    }
    else {
      uVar25 = 0x2d8;
    }
    iVar10 = FUN_43ae8c4a(iVar21 + 1);
    iVar24 = FUN_439035e0(piVar11 + 0x57,uVar25,iVar10 << 8,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    if (*(char *)((int)piVar11 + 0xc89) == '\0') {
      uVar25 = 0x20221c;
    }
    else {
      uVar25 = 0x20221d;
    }
    iVar10 = FUN_439035e0(piVar11 + 0x2f,uVar25,iVar10 << 8,1,0,5);
    if (iVar10 != 0) {
      return 5;
    }
  }
  if ((char)piVar11[0x306] == '\0') {
    uVar25 = 1;
  }
  else if (DAT_43f9b2b3 < 0x3c) {
    uVar25 = 0x11;
  }
  else {
    uVar25 = 1;
  }
  piVar16 = piVar11 + 7;
  iVar10 = FUN_43ae8c4a(iVar21 + 1);
  iVar24 = FUN_439035e0(piVar16,piVar11[99],iVar10 << 8,uVar25,0,5);
  if (iVar24 != 0) {
    DAT_43f9b2b3 = DAT_43f9b2b3 + 1;
    return 5;
  }
  DAT_43f9b2b3 = 0;
  iVar24 = FUN_439fdec4();
  if (iVar24 != 0) {
    iVar24 = FUN_4390366c(piVar11 + 0x4d,piVar16,1,5);
    if (iVar24 != 0) {
      FUN_43813d58(3,9,1,&DAT_43cb3204);
      FUN_43902718(s____Error___MemMgrWrapper__AllocS_43cb3218);
      FUN_43ae7542(piVar11 + 0x4d);
    }
  }
  iVar24 = FUN_4378f9b4();
  if (*(char *)(*(int *)(iVar24 + 0x50) + 0x1c) != '\0') {
    FUN_43780188(piVar16);
  }
  if ((char)piVar11[0x353] != '\0') {
    piVar11[0x354] = iVar21;
    *(undefined1 *)(piVar11 + 0x353) = 0;
  }
  if ((char)piVar11[0x31a] != '\0') {
    iVar24 = FUN_4390366c(piVar11 + 0x1b,piVar16,0,5);
    if (iVar24 != 0) {
      FUN_43813d58(3,9,1,&DAT_43cb323f,(short)piVar11[7]);
      FUN_43902718(s____Error___AllocShare_uhndl__d__43cb3253,(short)piVar11[7]);
      return 5;
    }
    *(short *)((int)piVar11 + 0xc6a) = (short)piVar11[0x1b];
  }
  iVar24 = FUN_4378f9b4();
  if (((*(byte *)(*(int *)(iVar24 + 8) + 0x26a) & 1) != 0) &&
     (iVar24 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar24 + 8) + 0x268) & 4) != 0)) {
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)((int)piVar11 + 0xd26) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x96);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(piVar11 + 0x34a) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x98);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)((int)piVar11 + 0xd2a) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x9a);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(piVar11 + 0x34b) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x9c);
    iVar24 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar24 + 0x2c) + 0xa4) != 0) {
      iVar24 = FUN_4378f9b4();
      dVar28 = (double)VectorUnsignedToFloat
                                 ((uint)*(ushort *)(*(int *)(iVar24 + 0x38) + 0x38),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar24 = FUN_4378f9b4();
      dVar30 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar24 + 0x2c) + 0xa0),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar24 = FUN_4378f9b4();
      dVar31 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar24 + 0x2c) + 0xa4),
                                  (byte)(in_fpscr >> 0x16) & 3);
      dVar31 = (dVar28 * 100.0 * dVar30) / dVar31;
      if (((int)((uint)(dVar31 < 126500.0) << 0x1f) < 0) &&
         (uVar29 = VectorFloatToUnsigned(dVar31,3), uVar29 != 0)) {
        if (uVar29 < 0x31ce) {
          cVar7 = FUN_4355faf0(uVar29 + 0x32,100);
          bVar8 = cVar7 << 1;
        }
        else {
          cVar7 = FUN_4355faf0(uVar29 + 500,1000);
          bVar8 = cVar7 << 1 | 1;
        }
        *(byte *)((int)piVar11 + 0xd2e) = bVar8;
        goto LAB_4355326a;
      }
    }
    *(undefined1 *)((int)piVar11 + 0xd2e) = 0xff;
  }
LAB_4355326a:
  FUN_43b03a5e(&iStack_4a4);
  FUN_43811484(piVar11,iVar21);
  iStack_4a4 = piVar11[0x7b];
  iStack_4a0 = piVar11[0x7c];
  iStack_49c = piVar11[0x7d];
  uStack_498 = 0;
  iStack_48c = piVar11[0x315];
  uStack_488 = (undefined1)piVar11[0x7e];
  piStack_494 = piVar16;
  iStack_490 = iVar10;
  uStack_487 = FUN_43ae8c4a(iVar21 - piVar11[0x354]);
  uStack_486 = (undefined2)piVar11[0x6e];
  uStack_484 = *(undefined2 *)((int)piVar11 + 0x1ba);
  iVar10 = piVar11[100];
  if ((char)iVar10 == '\0') {
    uStack_482 = FUN_43ae9e86(*(undefined2 *)((int)piVar11 + 0x19e),0x40);
  }
  else {
    uStack_482 = FUN_43ae98f8();
  }
  uStack_480 = (undefined2)piVar11[0x68];
  uStack_47a = *(undefined2 *)((int)piVar11 + 0x19e);
  iStack_46c = piVar11[0x6d];
  uStack_467 = 1;
  uStack_466 = *(undefined1 *)((int)piVar11 + 0x191);
  iStack_448 = piVar11[0x355];
  uStack_47e = 0;
  iStack_464 = piVar11[0x319];
  iStack_444 = piVar11[0x356];
  iStack_460 = piVar11[0x13f];
  uStack_47c = 0;
  uStack_476 = 0;
  iStack_45c = piVar11[0x140];
  uStack_474 = 0;
  iStack_458 = piVar11[0x141];
  uStack_454 = piVar11[0x2f5] == 1;
  iStack_3b0 = -1;
  uStack_450 = 0xffffffff;
  uStack_44c = 0xffffffff;
  auStack_440[0] = 0;
  uStack_3fc = 0;
  uStack_3dc = 0;
  iStack_3c0 = piVar11[0x35e];
  uStack_3bc = *(undefined2 *)((int)piVar11 + 0xd26);
  uStack_3b8 = *(undefined2 *)((int)piVar11 + 0xd2a);
  uStack_3ba = (undefined2)piVar11[0x34a];
  uStack_3b6 = (undefined2)piVar11[0x34b];
  uStack_3b4 = *(undefined1 *)((int)piVar11 + 0xd2e);
  if ((char)piVar11[0x360] != '\0') {
    iStack_3b0 = piVar11[0x35f];
  }
  iStack_3ac = piVar11[0x6c];
  iStack_3a8 = piVar11[0x361];
  uStack_3a4 = iStack_3a8 != 0;
  uStack_478 = uStack_480;
  uStack_472 = uStack_47a;
  uStack_470 = uStack_480;
  cStack_468 = (char)iVar10;
  puVar15 = (undefined4 *)FUN_4378f9b4();
  uStack_3a3 = *(short *)*puVar15 == 0x109;
  iVar10 = FUN_43ae8c4a(iVar21 + piVar11[0x315] + 1);
  iVar21 = FUN_4378f9b4();
  aiStack_48[2] = (int)(uint)*(ushort *)(*(int *)(iVar21 + 4) + 0x20) >> 2;
  FUN_43ad2dfc(0xfff,aiStack_48 + 2);
  iVar24 = piVar11[0x315] + 2;
  iVar21 = FUN_4378f9b4();
  iVar21 = FUN_4355faf0(*(int *)(*(int *)(iVar21 + 4) + 0x18) + 0x3e7ff,0x3e800);
  uVar4 = *(ushort *)((int)piVar11 + 0x19e);
  iStack_78 = FUN_43accc46(uVar4 >> 1,0x40);
  iStack_74 = (uint)uVar4 - iStack_78;
  iStack_7c = iStack_78;
  if (piVar11[0x357] - 1U < 4) {
    iStack_7c = iStack_78 + 0x40;
    iStack_74 = iStack_74 + 0x40;
    iStack_78 = iStack_78 + -0x40;
  }
  piVar23 = piVar11 + 0x31b;
  iVar22 = 0;
  uStack_5bc = 0;
  do {
    iVar19 = 1 - uStack_5bc;
    if (1 < uStack_5bc) {
      iVar19 = 0;
    }
    auStack_80[0] = (undefined1)iVar19;
    iVar27 = iStack_74;
    if (iVar19 != 0) {
      iVar27 = iStack_7c;
    }
    switch(piVar11[0x357]) {
    case 1:
      piVar11[0x1a7] = 2;
      piVar11[0x1a8] = *(int *)((int)aiStack_48 + iVar22);
      piVar11[0x1b2] = 0;
      if (*(char *)((int)piVar11 + 0xc89) == '\0') {
        iVar19 = 1;
      }
      else {
        iVar19 = 4;
      }
      piVar11[0x1ce] = iVar19;
      FUN_4381592c(piVar11,piVar23[-0x11],uVar12,auStack_80);
      iVar19 = *piVar23;
      uVar25 = FUN_4378f9b4();
      uVar18 = *(undefined4 *)((int)aiStack_48 + iVar22);
      goto LAB_435536a4;
    case 2:
      piVar11[0x1a7] = 2;
      piVar11[0x1a8] = *(int *)((int)aiStack_48 + iVar22);
      piVar11[0x1b2] = 0;
      if (*(char *)((int)piVar11 + 0xc89) == '\0') {
        iVar19 = 1;
      }
      else {
        iVar19 = 4;
      }
      piVar11[0x1ce] = iVar19;
      FUN_4381592c(piVar11,piVar23[-0x11],uVar12,auStack_80);
      uVar25 = *(undefined4 *)(auStack_4c + iVar22 + -4);
      uVar18 = *(undefined4 *)((int)aiStack_48 + iVar22);
      break;
    case 3:
      piVar11[0x1a7] = 2;
      piVar13 = aiStack_60;
      piVar11[0x1a8] = *(int *)((int)aiStack_48 + iVar22);
      piVar11[0x1b2] = 0;
      iVar19 = FUN_43b04358((short)piVar11[0x68]);
      iVar20 = piVar23[-0x11];
      piVar11[0x1ce] = iVar19;
      FUN_4381592c(piVar11,iVar20,uVar12,auStack_80);
      iVar19 = piVar23[0x2a];
      uVar25 = FUN_4378f9b4();
      FUN_43815be0(piVar11,iVar19,uVar25,*(undefined4 *)((int)aiStack_48 + iVar22),
                   *(undefined4 *)((int)piVar13 + iVar22),iVar27);
      goto LAB_43553698;
    case 4:
      piVar11[0x1a7] = 2;
      iVar19 = *(int *)((int)aiStack_48 + iVar22);
      piVar11[0x1b2] = 0;
      piVar11[0x1a8] = iVar19;
      iVar19 = FUN_43b04358((short)piVar11[0x68]);
      iVar20 = piVar23[-0x11];
      piVar11[0x1ce] = iVar19;
      FUN_4381592c(piVar11,iVar20,uVar12,auStack_80);
      iVar19 = piVar23[0x2a];
      uVar25 = FUN_4378f9b4();
      FUN_43815be0(piVar11,iVar19,uVar25,*(undefined4 *)((int)aiStack_48 + iVar22),
                   *(undefined4 *)((int)aiStack_60 + iVar22),iVar27);
      uVar25 = *(undefined4 *)(auStack_4c + iVar22 + -4);
      uVar18 = *(undefined4 *)((int)aiStack_60 + iVar22);
      break;
    default:
      FUN_43813d58(5,0,1,&DAT_43c9b47c,s_Sequence_MovieSplit_cpp_43cb334d,0x42a);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_MovieSplit_cpp_43cb334d,0x42a);
    case 0:
      piVar11[0x1a7] = 0;
      piVar11[0x1a9] = 1;
      piVar11[0x1aa] = piVar11[9];
      piVar11[0x1ce] = 1;
      piVar11[0x1ab] = piVar11[10];
      iVar19 = piVar23[-0x11];
      piVar11[0x1b2] = (uint)((char)piVar11[100] != '\0');
      FUN_4381592c(piVar11,iVar19,uVar12,auStack_80);
      goto LAB_435536c2;
    }
    piVar13 = aiStack_60 + 2;
    FUN_43815e94(piVar11,uVar25,uVar18,*(undefined4 *)((int)piVar13 + iVar22),0,iVar27,0);
LAB_43553698:
    iVar19 = *piVar23;
    uVar25 = FUN_4378f9b4();
    uVar18 = *(undefined4 *)((int)piVar13 + iVar22);
LAB_435536a4:
    FUN_43814ea0(piVar11,iVar19,uVar25,&iStack_4a4,uVar18,
                 iVar10 * 0x100 + ((uint)aiStack_48[2] >> 4),iVar24 * iVar21);
LAB_435536c2:
    iVar22 = iVar22 + 4;
    piVar23 = piVar23 + 1;
    uStack_5bc = uStack_5bc + 1;
    if (uStack_5bc == 2) {
      piVar23 = piVar11 + 0x57;
      FUN_435564e0(piVar11,piVar11[0x315] << 2,cVar1);
      FUN_439c5320(&iStack_5a8,&iStack_4a4,0x104);
      iVar22 = FUN_43ae9674(piVar23);
      if (iVar22 != 0) {
        uStack_586 = *(undefined2 *)((int)piVar11 + 0x1a6);
        uStack_584 = (undefined2)piVar11[0x6a];
        uStack_582 = 0;
        uStack_580 = 0;
        uStack_57e = *(undefined2 *)((int)piVar11 + 0x1aa);
        uStack_57c = (undefined2)piVar11[0x6b];
        uStack_57a = 0;
        uStack_578 = 0;
        piStack_598 = piVar23;
        uStack_576 = uStack_57e;
        uStack_574 = uStack_57c;
      }
      iVar22 = FUN_437286bc();
      if (iVar22 != 0) {
        if ((piVar11[0x358] != 1) || (DAT_4402546c[0x9d] == 0)) {
          if (*(ushort *)((int)piVar11 + 0x19e) < 0x781) {
            uVar12 = 0;
          }
          else {
            FUN_4379b44c(0,&iStack_5a8);
            uVar12 = 3;
          }
          FUN_4379b44c(uVar12,&iStack_4a4);
        }
        if ((piVar11[0x358] != 1) ||
           (piVar13 = (int *)FUN_4378f9b4(), *(int *)(*piVar13 + 0x2c) == 1)) {
          FUN_4379b44c(1,&iStack_4a4);
        }
      }
      if (piVar11[0x358] == 1) {
        FUN_439c5320(piVar11 + 0x324,auStack_440,0x80);
      }
      FUN_43b03a74(auStack_170,DAT_44023a28);
      FUN_43796910(param_1,auStack_170,piVar11);
      iVar22 = FUN_4378f9b4();
      if ((*(byte *)(*(int *)(iVar22 + 8) + 0x267) & 0x80) != 0) {
        FUN_437fe4d4();
      }
      iVar22 = iVar10;
      iVar19 = iVar10;
      iVar27 = iVar24;
      iVar20 = iVar24;
      if (*(char *)((int)piVar11 + 0x20d) != '\0') {
        iVar14 = FUN_43ae9674(piVar23);
        iVar26 = piVar11[0x318];
        if (iVar14 == 0) {
          iVar22 = FUN_43ae8c4a(iVar10 + iVar26);
          iVar27 = iVar26 + iVar24;
        }
        else {
          iVar19 = FUN_43ae8c4a(iVar10 + iVar26);
          iVar20 = iVar24 + iVar26;
        }
      }
      if (piVar11[0x358] == 1) {
        iVar27 = piVar11[0x317] + iVar24;
        iVar22 = FUN_43ae8c4a(iVar10 + piVar11[0x317]);
        piVar13 = (int *)FUN_4378f9b4();
        if (*(int *)(*piVar13 + 0x2c) == 1) {
          iVar20 = piVar11[0x317];
          iVar19 = FUN_43ae8c4a(iVar10 + iVar20);
          iVar20 = iVar24 + iVar20;
        }
      }
      FUN_43b2a2d0(piVar16,iVar22 * 0x100 + ((uint)aiStack_48[2] >> 4),iVar21 * iVar27,0,5);
      FUN_43b2a2d0(piVar23,iVar19 * 0x100 + ((uint)aiStack_48[2] >> 4),iVar21 * iVar20,0,5);
      if (piVar11[0x358] != 1) {
        FUN_43b2a2d0(piVar11 + 0x2f,iVar10 * 0x100 + ((uint)aiStack_48[2] >> 4),iVar24 * iVar21,1,5)
        ;
      }
      iStack_2b0 = piVar11[0x2f];
      iStack_2ac = piVar11[0x30];
      iStack_2a8 = piVar11[0x31];
      iStack_2a4 = piVar11[0x32];
      iStack_2a0 = piVar11[0x33];
      iStack_29c = piVar11[0x34];
      iStack_298 = piVar11[0x35];
      iStack_294 = piVar11[0x36];
      iStack_290 = piVar11[0x37];
      iStack_28c = piVar11[0x38];
      FUN_43ae7542(piVar11 + 0x2f);
      iStack_2d8 = piVar11[0x1b];
      iStack_2d4 = piVar11[0x1c];
      iStack_2d0 = piVar11[0x1d];
      iStack_2cc = piVar11[0x1e];
      iStack_2c8 = piVar11[0x1f];
      iStack_2c4 = piVar11[0x20];
      iStack_2c0 = piVar11[0x21];
      iStack_2bc = piVar11[0x22];
      iStack_2b8 = piVar11[0x23];
      iStack_2b4 = piVar11[0x24];
      FUN_43ae7542(piVar11 + 0x1b);
      iStack_328 = piVar11[0x39];
      iStack_324 = piVar11[0x3a];
      iStack_320 = piVar11[0x3b];
      iStack_31c = piVar11[0x3c];
      iStack_318 = piVar11[0x3d];
      iStack_314 = piVar11[0x3e];
      iStack_310 = piVar11[0x3f];
      iStack_30c = piVar11[0x40];
      iStack_308 = piVar11[0x41];
      iStack_304 = piVar11[0x42];
      FUN_43ae7542(piVar11 + 0x39);
      iStack_300 = piVar11[0x4d];
      iStack_2fc = piVar11[0x4e];
      iStack_2f8 = piVar11[0x4f];
      iStack_2f4 = piVar11[0x50];
      iStack_2f0 = piVar11[0x51];
      iStack_2ec = piVar11[0x52];
      iStack_2e8 = piVar11[0x53];
      iStack_2e4 = piVar11[0x54];
      iStack_2e0 = piVar11[0x55];
      iStack_2dc = piVar11[0x56];
      FUN_43ae7542(piVar11 + 0x4d);
      iVar10 = piVar11[0x310];
      uVar9 = *(undefined1 *)((int)piVar11 + 0x213);
      uVar3 = *(undefined1 *)((int)piVar11 + 0x20d);
      *(undefined1 *)((int)piVar11 + 0x213) = 0;
      *(undefined1 *)((int)piVar11 + 0x20d) = 0;
      *(undefined1 *)(piVar11 + 0x310) = 0;
      FUN_43afb42e(&uStack_3a0);
      FUN_43afb476(&uStack_3a0,DAT_44020e70);
      uStack_38c = 0;
      uStack_35c = FUN_43afdf16(param_1);
      uStack_360 = FUN_43afbf44(param_1);
      FUN_43b03a80(auStack_184,DAT_44022af4);
      uVar12 = FUN_43b03a70(piVar11);
      uVar12 = FUN_4380d708(auStack_184,uVar12,piVar11);
      iVar21 = FUN_4381bbf0(param_1,&uStack_3a0,uVar12);
      if (iVar21 != 0) {
        FUN_43b04730();
      }
      piVar11[0x2f] = iStack_2b0;
      piVar11[0x30] = iStack_2ac;
      piVar11[0x31] = iStack_2a8;
      piVar11[0x32] = iStack_2a4;
      piVar11[0x33] = iStack_2a0;
      piVar11[0x34] = iStack_29c;
      piVar11[0x35] = iStack_298;
      piVar11[0x36] = iStack_294;
      piVar11[0x37] = iStack_290;
      piVar11[0x38] = iStack_28c;
      FUN_43ae7542(&iStack_2b0);
      piVar11[0x1b] = iStack_2d8;
      piVar11[0x1c] = iStack_2d4;
      piVar11[0x1d] = iStack_2d0;
      piVar11[0x1e] = iStack_2cc;
      piVar11[0x1f] = iStack_2c8;
      piVar11[0x20] = iStack_2c4;
      piVar11[0x21] = iStack_2c0;
      piVar11[0x22] = iStack_2bc;
      piVar11[0x23] = iStack_2b8;
      piVar11[0x24] = iStack_2b4;
      FUN_43ae7542(&iStack_2d8);
      piVar11[0x39] = iStack_328;
      piVar11[0x3a] = iStack_324;
      piVar11[0x3b] = iStack_320;
      piVar11[0x3c] = iStack_31c;
      piVar11[0x3d] = iStack_318;
      piVar11[0x3e] = iStack_314;
      piVar11[0x3f] = iStack_310;
      piVar11[0x40] = iStack_30c;
      piVar11[0x41] = iStack_308;
      piVar11[0x42] = iStack_304;
      FUN_43ae7542(&iStack_328);
      piVar11[0x4d] = iStack_300;
      piVar11[0x4e] = iStack_2fc;
      piVar11[0x4f] = iStack_2f8;
      piVar11[0x50] = iStack_2f4;
      piVar11[0x51] = iStack_2f0;
      piVar11[0x52] = iStack_2ec;
      piVar11[0x53] = iStack_2e8;
      piVar11[0x54] = iStack_2e4;
      piVar11[0x55] = iStack_2e0;
      piVar11[0x56] = iStack_2dc;
      FUN_43ae7542(&iStack_300);
      *(undefined1 *)((int)piVar11 + 0x213) = uVar9;
      *(undefined1 *)((int)piVar11 + 0x20d) = uVar3;
      *(char *)(piVar11 + 0x310) = (char)iVar10;
      FUN_43ae7534(&iStack_300);
      FUN_43ae7534(&iStack_328);
      FUN_43ae7534(&iStack_2d8);
      FUN_43ae7534(&iStack_2b0);
      if (*(char *)((int)piVar11 + 0x213) != '\0') {
        FUN_43afb45e(auStack_198,DAT_440256e4);
        FUN_43afb43a(auStack_1ac,0);
        iVar10 = FUN_437dcfc8(auStack_198,auStack_1ac,0);
        piVar11[0xec] = iVar10;
        return 0;
      }
      return 0;
    }
  } while( true );
}


/* query "43554590" */

undefined4 FUN_43554590(undefined4 param_1)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  ushort uVar5;
  byte *pbVar6;
  char cVar7;
  byte bVar8;
  undefined1 uVar9;
  undefined2 uVar10;
  int iVar11;
  undefined4 uVar12;
  char *pcVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int *piVar18;
  undefined2 extraout_r1;
  undefined4 extraout_r1_00;
  undefined1 *puVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  int iVar23;
  int iVar24;
  uint uVar25;
  undefined4 uVar26;
  int iVar27;
  int iVar28;
  bool bVar29;
  uint in_fpscr;
  double dVar30;
  double dVar31;
  double dVar32;
  undefined4 *puVar33;
  undefined4 uStack_414;
  undefined4 uStack_410;
  undefined4 uStack_40c;
  undefined4 uStack_408;
  int iStack_404;
  int iStack_400;
  undefined4 uStack_3fc;
  undefined1 uStack_3f8;
  undefined1 uStack_3f7;
  undefined2 uStack_3f6;
  undefined2 uStack_3f4;
  undefined2 uStack_3f2;
  undefined2 uStack_3f0;
  undefined2 uStack_3ee;
  undefined2 uStack_3ec;
  undefined2 uStack_3ea;
  undefined2 uStack_3e8;
  undefined2 uStack_3e6;
  undefined2 uStack_3e4;
  undefined2 uStack_3e2;
  undefined2 uStack_3e0;
  undefined4 uStack_3dc;
  char cStack_3d8;
  undefined1 uStack_3d7;
  undefined1 uStack_3d6;
  undefined4 uStack_3d4;
  undefined4 uStack_3d0;
  undefined4 uStack_3cc;
  undefined4 uStack_3c8;
  undefined1 uStack_3c4;
  undefined4 uStack_3c0;
  int iStack_3bc;
  undefined4 uStack_3b8;
  undefined4 uStack_3b4;
  undefined1 auStack_3b0 [68];
  undefined1 uStack_36c;
  undefined1 uStack_34c;
  undefined4 uStack_330;
  undefined2 uStack_32c;
  undefined2 uStack_32a;
  undefined2 uStack_328;
  undefined2 uStack_326;
  undefined1 uStack_324;
  undefined4 uStack_320;
  undefined4 uStack_31c;
  undefined4 uStack_318;
  undefined1 uStack_314;
  byte bStack_313;
  undefined1 auStack_310 [20];
  undefined4 uStack_2fc;
  undefined4 uStack_2d0;
  undefined1 uStack_2cc;
  uint uStack_2c8;
  undefined1 uStack_2c4;
  undefined1 uStack_2c3;
  undefined1 uStack_2c2;
  undefined4 uStack_2c0;
  undefined1 uStack_2b8;
  undefined1 uStack_2b7;
  undefined4 uStack_2b4;
  undefined4 uStack_2b0;
  undefined4 uStack_2ac;
  undefined1 uStack_2a7;
  undefined1 uStack_2a5;
  undefined1 uStack_2a4;
  undefined1 uStack_2a2;
  undefined1 uStack_2a1;
  int iStack_2a0;
  undefined1 uStack_29c;
  undefined4 uStack_298;
  undefined4 uStack_294;
  undefined4 uStack_290;
  undefined4 uStack_28c;
  undefined4 uStack_288;
  undefined4 uStack_284;
  undefined4 uStack_280;
  undefined4 uStack_27c;
  undefined4 uStack_278;
  undefined4 uStack_274;
  undefined4 uStack_270;
  undefined4 uStack_26c;
  undefined4 uStack_268;
  undefined4 uStack_264;
  undefined4 uStack_260;
  undefined4 uStack_25c;
  undefined4 uStack_258;
  undefined4 uStack_254;
  undefined4 uStack_250;
  undefined4 uStack_24c;
  undefined4 uStack_248;
  undefined4 uStack_244;
  undefined4 uStack_240;
  undefined4 uStack_23c;
  undefined4 uStack_238;
  undefined4 uStack_234;
  undefined4 uStack_230;
  undefined4 uStack_22c;
  undefined4 uStack_228;
  undefined4 uStack_224;
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined4 uStack_218;
  undefined4 uStack_214;
  undefined4 uStack_210;
  undefined4 uStack_20c;
  undefined4 uStack_208;
  undefined4 uStack_204;
  undefined4 uStack_200;
  undefined4 uStack_1fc;
  undefined4 uStack_1f8;
  undefined4 uStack_1f4;
  undefined4 uStack_1f0;
  undefined4 uStack_1ec;
  undefined4 uStack_1e8;
  undefined4 uStack_1e4;
  undefined4 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined4 uStack_1d4;
  undefined4 uStack_1d0;
  undefined4 uStack_1cc;
  undefined4 uStack_1c8;
  undefined4 uStack_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined2 uStack_1b8;
  undefined2 uStack_1b6;
  undefined2 uStack_1b4;
  undefined2 uStack_1b2;
  undefined2 uStack_1b0;
  undefined2 uStack_1ae;
  undefined1 auStack_1a8 [20];
  undefined1 auStack_194 [20];
  undefined1 auStack_180 [20];
  undefined1 auStack_16c [20];
  undefined1 auStack_158 [20];
  undefined1 auStack_144 [20];
  undefined1 auStack_130 [20];
  undefined1 auStack_11c [20];
  undefined1 auStack_108 [20];
  undefined1 auStack_f4 [20];
  undefined1 auStack_e0 [20];
  undefined1 auStack_cc [20];
  undefined1 auStack_b8 [20];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [8];
  undefined4 uStack_4c;
  undefined4 uStack_48;
  uint uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 auStack_34 [2];
  
  iVar11 = FUN_4378f9b4();
  iVar23 = **(int **)(iVar11 + 4);
  iVar11 = FUN_4378f9b4();
  cVar1 = *(char *)(*(int *)(iVar11 + 8) + 0x33);
  iVar11 = FUN_43ae75dc(param_1);
  if (*(char *)(iVar11 + 0xd70) != '\0') {
    return 5;
  }
  uVar12 = FUN_43afdf16(param_1);
  switch(uVar12) {
  case 0:
    iVar17 = FUN_43795b04();
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,0,*(undefined4 *)(iVar11 + 0x1fc),iVar23,0,1,0,2,0,iVar11 + 0xd68,0);
    uVar12 = DAT_44025f5c;
    if (iVar17 != 0) {
      iVar17 = FUN_43ae8cc8(DAT_44025f5c);
      pbVar6 = DAT_4402546c;
      if (iVar17 != 0) {
        if (*DAT_4402546c != 0) {
          iVar17 = FUN_43799a94(1,1,0,iVar23,0,1,0,2,0,iVar11 + 0xd68,iVar11 + 0x51c);
          if (iVar17 == 0) {
            return 5;
          }
          FUN_43728c18(iVar11 + 0x508,iVar11 + 0x50c,iVar11 + 0x510);
          FUN_43acc282(*(undefined4 *)(iVar11 + 0x51c),*pbVar6 - 1,iVar11 + 0x3e4,0xfff,0xfff,0xfff)
          ;
        }
        iVar17 = FUN_43813f0c(*(undefined4 *)(iVar11 + 0x1fc));
        if (iVar17 == 0) {
          puVar19 = &DAT_43f9b2b5;
        }
        else {
          puVar19 = &DAT_43f9b2b4;
        }
        *puVar19 = 1;
        FUN_4378e5ac(uVar12);
      }
      if (((DAT_43f9b2b4 == '\0') &&
          (iVar17 = FUN_4378f9b4(), *(char *)(*(int *)(iVar17 + 8) + 0x290) == '\0')) &&
         (DAT_43f9b2b6 != '\0')) {
        FUN_43ae931e((DAT_43eea8d4 >> 1) + 1,DAT_440259e4);
        DAT_43f9b2b6 = '\0';
      }
      FUN_43b03a74(auStack_68,DAT_4402110c);
      FUN_43796910(param_1,auStack_68,iVar11);
      uVar12 = FUN_438148f0();
      FUN_43b04040(uVar12,*(undefined4 *)(iVar11 + 0x1f0),iVar23,*(undefined4 *)(iVar11 + 0x1f8),
                   *(undefined4 *)(iVar11 + 0xc4c),*(undefined4 *)(iVar11 + 0x1b0));
      return 0;
    }
    return 5;
  case 1:
    uVar12 = FUN_4378f9b4();
    iVar17 = FUN_4378e6a0(DAT_44025f5c,uVar12);
    if (iVar17 == 0) {
      return 5;
    }
    iVar24 = iVar11 + 0xd68;
    iVar17 = FUN_43799a94(1,1,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0x51c);
    if (iVar17 == 0) {
      return 5;
    }
    FUN_43728c18(iVar11 + 0x508,iVar11 + 0x50c,iVar11 + 0x510);
    pbVar6 = DAT_4402546c;
    uVar9 = *(undefined1 *)(iVar11 + 0x3fa);
    if (DAT_4402546c[0x4e] == 0xff) {
      uVar9 = 0;
    }
    else if (DAT_4402546c[0x4e] != 0) {
      uVar9 = 1;
    }
    uVar26 = *(undefined4 *)(iVar11 + 0x51c);
    uVar12 = FUN_437d9d08();
    FUN_43acc2ee(uVar26,uVar9,uVar12);
    iVar17 = FUN_43799a94(1,0x10,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,auStack_34)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,4,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0xc20);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_4381c04c(0,*(undefined4 *)(iVar11 + 0x184),auStack_54);
    if (iVar17 == 0) {
      *(undefined1 *)(iVar11 + 0x524) = 0;
      *(undefined1 *)(iVar11 + 0x20c) = 0;
    }
    if ((pbVar6[2] & 1) == 0) {
      uVar12 = 10;
    }
    else {
      uVar12 = 0xb;
    }
    *(undefined4 *)(iVar11 + 0x598) = uVar12;
    *(undefined4 *)(iVar11 + 0x59c) = 2;
    *(undefined4 *)(iVar11 + 0x5d4) = 1;
    *(undefined4 *)(iVar11 + 0x5a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x5c8) = 0;
    *(undefined4 *)(iVar11 + 0x5d8) = uStack_4c;
    *(undefined4 *)(iVar11 + 0x5cc) = 0;
    *(undefined4 *)(iVar11 + 0x5fc) = 0;
    *(undefined4 *)(iVar11 + 0x5dc) = uStack_48;
    bVar29 = *(char *)(iVar11 + 0x188) != '\0';
    *(uint *)(iVar11 + 0x5f8) = (uint)bVar29;
    if (((bVar29) && (*(int *)(iVar11 + 0xd78) == 1)) && (*(short *)(iVar11 + 0x19e) == 0x5a0)) {
      *(undefined2 *)(iVar11 + 0x19e) = 0x5c0;
    }
    if (((*(int *)(iVar11 + 0x1b0) - 2U < 2) &&
        (iVar17 = FUN_4378f9b4(), *(int *)(*(int *)(iVar17 + 4) + 0xc) != 0)) &&
       (*(int *)(iVar11 + 0x1fc) != 9)) {
      bVar8 = 0;
      *(undefined1 *)(iVar11 + 0x1ee) = 0;
    }
    else if ((*(char *)(iVar11 + 0xd40) == '\0') || (*(char *)(iVar11 + 0xd41) == '\0')) {
      iVar17 = FUN_4378f9b4();
      bVar2 = *(byte *)(*(int *)(iVar17 + 8) + 0x268);
      bVar8 = bVar2 & 2;
      if ((bVar2 & 2) != 0) goto LAB_4355490c;
    }
    else {
      bVar8 = 0;
    }
    *(byte *)(iVar11 + 0x20c) = bVar8;
LAB_4355490c:
    iVar17 = FUN_43799a94(1,0xe,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,0);
    if (iVar17 == 0) {
      return 5;
    }
    if ((pbVar6[0x70] == 0) && (iVar17 = FUN_4378003c(), iVar17 == 0)) {
      iVar27 = FUN_43affc8a(*(undefined4 *)(iVar11 + 0x508));
      uStack_2c4 = *(undefined1 *)(iVar11 + 0x20e);
      uStack_2c2 = 0;
      uStack_2a5 = 0;
      uStack_2c3 = *(undefined1 *)(iVar11 + 0x20f);
      uStack_2a4 = 0;
      uStack_2a2 = 0;
      uStack_2c0 = *(undefined4 *)(iVar11 + 0x208);
      uStack_2a1 = 0;
      uStack_2b8 = (undefined1)*(undefined4 *)(iVar11 + 0x1fc);
      uStack_2b7 = (undefined1)*(undefined4 *)(iVar11 + 0xc4c);
      uStack_2c8 = (uint)(iVar27 == 1);
      uStack_2b4 = *(undefined4 *)(iVar11 + 0x1ec);
      uStack_2b0 = *(undefined4 *)(iVar11 + 0x1f0);
      uStack_2ac = *(undefined4 *)(iVar11 + 500);
      uStack_2a7 = (undefined1)*(undefined4 *)(iVar11 + 0x3e0);
      uStack_29c = *(int *)(iVar11 + 0xd78) == 1;
      iStack_2a0 = iVar17;
      FUN_439e34d4(&uStack_2c8);
    }
    FUN_43799a94(1,0xf,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc4c) + 1,0,iVar24,0);
    iVar23 = FUN_43799a94(1,0xd,*(undefined4 *)(iVar11 + 0x1fc),iVar23,0,1,0,
                          *(int *)(iVar11 + 0xc4c) + 1,0,iVar24,iVar11 + 0x520);
    if (iVar23 == 0) {
      return 5;
    }
    FUN_43728c4c(iVar11 + 0x514,iVar11 + 0x518);
    FUN_437956a4(*(undefined4 *)(iVar11 + 0x520));
    FUN_43814008(iVar11);
    FUN_43b03a74(auStack_7c,DAT_44022cc8);
    FUN_43796910(param_1,auStack_7c,iVar11);
    uVar12 = DAT_44023820;
    if (*(char *)(iVar11 + 0x525) == '\0') {
      FUN_438106ec(iVar11);
      FUN_43b03a74(auStack_90,uVar12);
      puVar19 = auStack_90;
    }
    else {
      FUN_43b03a74(auStack_a4,DAT_44026238);
      FUN_43797090(param_1,auStack_a4,iVar11);
      FUN_43b03a74(auStack_b8,uVar12);
      puVar19 = auStack_b8;
    }
    FUN_43797090(param_1,puVar19,iVar11);
    uVar12 = DAT_44021e0c;
    if (cVar1 == '\0') {
      FUN_43b03a74(auStack_f4,DAT_440204b4);
      FUN_43796910(param_1,auStack_f4,iVar11);
      FUN_43b03a74(auStack_108,uVar12);
      FUN_43796910(param_1,auStack_108,iVar11);
    }
    else {
      FUN_43b03a74(auStack_cc,DAT_440204b4);
      FUN_43797090(param_1,auStack_cc,iVar11);
      FUN_43b03a74(auStack_e0,uVar12);
      FUN_43797090(param_1,auStack_e0,iVar11);
    }
    FUN_43b03a74(auStack_11c,DAT_44024a24);
    FUN_43796910(param_1,auStack_11c,iVar11);
    FUN_43b03a74(auStack_130,DAT_440259b4);
    FUN_4379704c(param_1,auStack_130,iVar11);
    if (*(char *)(iVar11 + 0x20c) == '\0') {
      return 5;
    }
    return 0;
  case 2:
    break;
  case 3:
    uVar22 = *(int *)(iVar11 + 0xc58) + 1;
    *(uint *)(iVar11 + 0xc58) = uVar22;
    if (uVar22 < *(uint *)(iVar11 + 0xc54)) {
      return 1;
    }
    if ((*(int *)(iVar11 + 0xd60) != 1) ||
       (iVar17 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar17 + 8) + 0x268) & 4) == 0))
    goto LAB_4355607c;
    piVar18 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar18 + 0x2c) == 0) {
      uVar12 = 0;
      if (*(char *)(iVar11 + 0x199) != '\0') {
        if (*(int *)(iVar11 + 0xc64) != 0) {
          *(undefined4 *)(iVar11 + 0x9b0) = 1;
          goto LAB_43555c52;
        }
        uVar12 = 2;
      }
      *(undefined4 *)(iVar11 + 0x9b0) = uVar12;
    }
    else {
      uVar12 = 0;
      if (*(char *)(iVar11 + 0x191) != '\0') {
        uVar12 = 5;
      }
      *(undefined4 *)(iVar11 + 0x9b0) = uVar12;
      if (*(int *)(iVar11 + 0xc64) == 0) goto LAB_4355607c;
    }
LAB_43555c52:
    iVar24 = iVar11 + 0xd68;
    iVar17 = FUN_43799a94(1,0xb,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_38);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,0x13,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_40)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,8,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc5c) + 1,0,iVar24,&uStack_3c);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43ae8c4a(iVar23 + 1);
    iVar24 = FUN_439035e0(iVar11 + 0x44,*(undefined4 *)(iVar11 + 0x194),iVar17 << 8,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    if (*(int *)(iVar11 + 0xc5c) == 2) {
      iVar24 = FUN_4378f9b4();
      if (*(int *)(*(int *)(iVar24 + 4) + 0xc) == 1) {
        uVar12 = 0xc;
      }
      else {
        uVar12 = 0xd;
      }
    }
    else {
      uVar12 = 0xb;
    }
    *(undefined4 *)(iVar11 + 0x6d0) = uVar12;
    *(uint *)(iVar11 + 0x700) = (uint)(*(char *)(iVar11 + 400) != '\0');
    *(undefined4 *)(iVar11 + 0x70c) = 0;
    *(undefined4 *)(iVar11 + 0x6dc) = 1;
    *(undefined4 *)(iVar11 + 0x6e0) = *(undefined4 *)(iVar11 + 0x24);
    *(undefined4 *)(iVar11 + 0x6e4) = *(undefined4 *)(iVar11 + 0x28);
    *(undefined4 *)(iVar11 + 0x704) = 2;
    *(undefined4 *)(iVar11 + 0x6d4) = 0;
    *(undefined2 *)(iVar11 + 0x994) = 0;
    *(undefined2 *)(iVar11 + 0x996) = 0;
    *(undefined2 *)(iVar11 + 0x99a) = *(undefined2 *)(iVar11 + 0x1a0);
    *(undefined2 *)(iVar11 + 0x99c) = 0;
    *(undefined2 *)(iVar11 + 0x99e) = 0;
    *(undefined2 *)(iVar11 + 0x9a0) = 0;
    *(undefined2 *)(iVar11 + 0x9a2) = 0;
    *(undefined4 *)(iVar11 + 0x730) = 0;
    *(undefined4 *)(iVar11 + 0x708) = uStack_40;
    *(undefined4 *)(iVar11 + 0x9a4) = 0;
    *(undefined2 *)(iVar11 + 0x9a8) = 0;
    *(undefined2 *)(iVar11 + 0x9aa) = 0;
    *(undefined2 *)(iVar11 + 0x9ac) = 0;
    *(undefined2 *)(iVar11 + 0x9ae) = 0;
    *(undefined2 *)(iVar11 + 0x998) = *(undefined2 *)(iVar11 + 0x19e);
    uVar12 = FUN_43b03bf8();
    uStack_1dc = 4;
    uStack_1d8 = 7;
    uStack_1d4 = 0x80;
    uStack_1d0 = FUN_43556490(uVar12,0x80,*(int *)(iVar11 + 0xc5c) << 2,cVar1);
    uStack_1cc = 0;
    uStack_1ec = 0;
    uStack_1e0 = 0;
    uStack_1e8 = 0;
    uStack_1c4 = 1;
    uStack_1c8 = 1;
    uStack_1f8 = 4;
    uStack_1f4 = 7;
    uStack_1f0 = 0x80;
    uStack_1e4 = 1;
    iVar24 = FUN_43940f2c(uStack_38,&uStack_1dc,&uStack_1f8);
    if (iVar24 != 0) {
      FUN_43813e60(3,9,1,&DAT_43cb34c9,iVar24);
      FUN_43902718(s_Sequence_SuperSlowMotion__RC_ERR_43cb34dd,iVar24);
    }
    uVar5 = *(ushort *)(iVar11 + 0x1a2);
    if (uVar5 < 0x3c1) {
      uVar26 = 0;
      uVar12 = 0;
    }
    else {
      if (uVar5 != 0x500) {
        FUN_43813e60(3,9,1,&DAT_43cb3521,uVar5);
        FUN_43902718(s_Sequence_SuperSlowMotion__SRC_>V_43cb3535,*(undefined2 *)(iVar11 + 0x1a2));
      }
      uVar26 = 0x280;
      uVar12 = 5;
    }
    FUN_43798490(uStack_38,iVar11 + 0x6d0,iVar11 + 0x988,iVar11 + 0x19e,iVar11 + 0x1a2,
                 *(undefined4 *)(iVar11 + 0xbd4),uVar12,1);
    FUN_43815e94(iVar11,uStack_3c,uStack_40,0,1,*(undefined2 *)(iVar11 + 0x1a2),uVar26);
    iVar24 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar24 + 4) + 0x10) == 3) {
      uVar12 = 3;
    }
    else {
      uVar12 = 2;
    }
    FUN_43b03a5e(&uStack_414);
    FUN_43811484(iVar11,iVar23);
    uStack_414 = *(undefined4 *)(iVar11 + 0x1ec);
    uStack_410 = *(undefined4 *)(iVar11 + 0x1f0);
    uStack_40c = *(undefined4 *)(iVar11 + 500);
    uStack_408 = 0;
    uStack_3fc = *(undefined4 *)(iVar11 + 0xc5c);
    uStack_3f8 = (undefined1)*(undefined4 *)(iVar11 + 0x1f8);
    iStack_404 = iVar11 + 0x44;
    iStack_400 = iVar17;
    uStack_3f7 = FUN_43ae8c4a((iVar23 - *(int *)(iVar11 + 0xd50)) - *(int *)(iVar11 + 0xc58));
    piVar18 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar18 + 0x2c) == 0) {
      uStack_3f6 = *(undefined2 *)(iVar11 + 0x1b8);
    }
    else {
      uStack_3f6 = *(undefined2 *)(iVar11 + 0x1a2);
    }
    piVar18 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar18 + 0x2c) == 0) {
      uStack_3f4 = *(undefined2 *)(iVar11 + 0x1ba);
    }
    else {
      uStack_3f4 = *(undefined2 *)(iVar11 + 0x1a4);
    }
    uVar10 = *(undefined2 *)(iVar11 + 0x1a2);
    uStack_3f2 = FUN_43ae9e86(uVar10,0x40);
    uStack_3f0 = *(undefined2 *)(iVar11 + 0x1a4);
    uStack_3ee = 0;
    uStack_3dc = *(undefined4 *)(iVar11 + 0x1b4);
    uStack_3ec = 0;
    uStack_3e6 = 0;
    cStack_3d8 = *(undefined1 *)(iVar11 + 0x198);
    uStack_3e4 = 0;
    uStack_3d7 = 1;
    uStack_3d6 = *(undefined1 *)(iVar11 + 0x199);
    uStack_3d4 = *(undefined4 *)(iVar11 + 0xc64);
    uStack_3d0 = *(undefined4 *)(iVar11 + 0x4fc);
    uStack_3cc = *(undefined4 *)(iVar11 + 0x534);
    uStack_3c8 = *(undefined4 *)(iVar11 + 0x504);
    uStack_3c4 = *(int *)(iVar11 + 0xbd4) == 1;
    uStack_320 = 0xffffffff;
    uStack_3c0 = 0xffffffff;
    iStack_3bc = 0xffffffff;
    uStack_3b8 = *(undefined4 *)(iVar11 + 0xd54);
    uStack_3b4 = *(undefined4 *)(iVar11 + 0xd58);
    auStack_3b0[0] = 0;
    uStack_36c = 0;
    uStack_34c = 0;
    uStack_330 = *(undefined4 *)(iVar11 + 0xd78);
    uStack_32c = *(undefined2 *)(iVar11 + 0xd26);
    uStack_32a = *(undefined2 *)(iVar11 + 0xd28);
    uStack_328 = *(undefined2 *)(iVar11 + 0xd2a);
    uStack_326 = *(undefined2 *)(iVar11 + 0xd2c);
    uStack_324 = *(undefined1 *)(iVar11 + 0xd2e);
    if (*(char *)(iVar11 + 0xd80) != '\0') {
      uStack_320 = *(undefined4 *)(iVar11 + 0xd7c);
    }
    uStack_3ea = uVar10;
    uStack_3e8 = uStack_3f0;
    uStack_3e2 = uVar10;
    uStack_3e0 = uStack_3f0;
    piVar18 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar18 + 0x2c) == 0) {
      uVar12 = *(undefined4 *)(iVar11 + 0x1b0);
    }
    uStack_318 = *(undefined4 *)(iVar11 + 0xd84);
    uStack_314 = 0;
    uStack_31c = uVar12;
    bStack_313 = FUN_43813f0c(*(undefined4 *)(iVar11 + 0x1fc));
    bStack_313 = bStack_313 ^ 1;
    FUN_439c5320(auStack_3b0,iVar11 + 0xc90,0x80);
    if (DAT_4402546c[0x9d] == 1) {
      FUN_4379b44c(0,&uStack_414);
    }
    piVar18 = (int *)FUN_4378f9b4();
    if (*(int *)(*piVar18 + 0x2c) == 1) {
      uVar12 = 2;
    }
    else {
      uVar12 = 1;
    }
    FUN_4379b44c(uVar12,&uStack_414);
LAB_4355607c:
    iVar23 = FUN_43ae8c4a(iVar23 + *(int *)(iVar11 + 0xc5c) + 1);
    iVar17 = FUN_4378f9b4();
    uStack_44 = (int)(uint)*(ushort *)(*(int *)(iVar17 + 4) + 0x20) >> 2;
    FUN_43ad2dfc(0xfff,&uStack_44);
    iVar24 = *(int *)(iVar11 + 0xc5c);
    iVar17 = FUN_4378f9b4();
    iVar17 = FUN_4355faf0(*(int *)(*(int *)(iVar17 + 4) + 0x18) + 0x3e7ff,0x3e800);
    FUN_43b2a2d0(iVar11 + 0xbc,iVar23 * 0x100 + (uStack_44 >> 4),(iVar24 + 2) * iVar17,1,5);
    iVar23 = FUN_43ae8c4a(iVar23 + 1);
    FUN_43b2a2d0(iVar11 + 0x44,iVar23 * 0x100 + (uStack_44 >> 4),iVar17 * (iVar24 + 3),1,5);
    return 0;
  case 4:
    iVar17 = FUN_439fdec4();
    if (iVar17 != 0) {
      DAT_43eea8e0 = *(undefined2 *)(iVar11 + 0x134);
      DAT_43eea8e4 = *(undefined4 *)(iVar11 + 0x138);
      if (*(char *)(iVar11 + 400) == '\0') {
        DAT_43eea8e8 = FUN_43ae9e86(*(undefined2 *)(iVar11 + 0x19e),0x40);
      }
      else {
        DAT_43eea8e8 = FUN_43ae98f8();
      }
      DAT_43eea8ea = *(undefined2 *)(iVar11 + 0x1a0);
      DAT_43eea8f0 = *(undefined2 *)(iVar11 + 0x19e);
      DAT_43eea8f4 = (ushort)*(byte *)(iVar11 + 0x136);
      DAT_43eea8f8 = *(undefined4 *)(iVar11 + 0x13c);
      DAT_43eea8ec = 0;
      DAT_43eea8fc = *(undefined4 *)(iVar11 + 0x140);
      DAT_43eea8ee = 0;
      DAT_43eea8f2 = DAT_43eea8ea;
      iVar17 = FUN_439fde5c(&DAT_43eea8e0);
      if (iVar17 != 0) {
        FUN_43ae7542(iVar11 + 0x134);
      }
    }
    uStack_270 = *(undefined4 *)(iVar11 + 0xbc);
    uStack_26c = *(undefined4 *)(iVar11 + 0xc0);
    uStack_268 = *(undefined4 *)(iVar11 + 0xc4);
    uStack_264 = *(undefined4 *)(iVar11 + 200);
    uStack_260 = *(undefined4 *)(iVar11 + 0xcc);
    uStack_25c = *(undefined4 *)(iVar11 + 0xd0);
    uStack_258 = *(undefined4 *)(iVar11 + 0xd4);
    uStack_254 = *(undefined4 *)(iVar11 + 0xd8);
    uStack_250 = *(undefined4 *)(iVar11 + 0xdc);
    uStack_24c = *(undefined4 *)(iVar11 + 0xe0);
    FUN_43ae7542(iVar11 + 0xbc);
    if (*(char *)(iVar11 + 0xc68) != '\0') {
      FUN_43afb42e(auStack_310);
      FUN_43afb476(auStack_310,DAT_440219a8);
      uStack_2fc = 4;
      uStack_2cc = 0;
      uStack_2d0 = FUN_43afbf44(param_1);
      FUN_43b0417e(10,0xffffffff,1,iVar23);
      FUN_43ae7542(iVar11 + 0x6c);
      FUN_43b03a80(auStack_16c,DAT_44022af4);
      uVar12 = FUN_43b03a70(iVar11);
      uVar12 = FUN_4380d708(auStack_16c,uVar12,iVar11);
      iVar17 = FUN_4381bbf0(param_1,auStack_310,uVar12);
      if (iVar17 != 0) {
        FUN_43b04730();
      }
    }
    if (*(char *)(iVar11 + 0x20d) != '\0') {
      iVar17 = FUN_437999e4(1,5);
      if (iVar17 == 0) goto LAB_43556408;
      piVar18 = (int *)FUN_4378f9b4();
      uVar9 = FUN_43879534(*(undefined4 *)(*piVar18 + 0xb4));
      *(undefined1 *)(iVar11 + 0xd22) = uVar9;
      iVar17 = thunk_FUN_439dce54();
      *(char *)(iVar11 + 0xd72) = (char)iVar17;
      if ((iVar17 != 0) || (*(char *)(iVar11 + 0xd22) != '\0')) {
        FUN_43ae7558(&uStack_298);
        iVar17 = FUN_43903558(iVar11 + 0x94,0x30700,0x11,0,5);
        if (iVar17 != 0) {
          DAT_43f9b2b7 = DAT_43f9b2b7 + 1;
          if (0x3b < DAT_43f9b2b7) {
            FUN_43813e60(3,9,1,&DAT_43cb0ee4,DAT_43f9b2b7);
            FUN_43902718(s_Face_Memory_Alloc_Error___d_43cb0ef8,DAT_43f9b2b7);
          }
          FUN_43ae7534(&uStack_298);
          goto LAB_43556408;
        }
        *(int *)(iVar11 + 0xd74) = iVar23;
        DAT_43f9b2b7 = 0;
        if (*(char *)(iVar11 + 0xc18) == '\0') {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1e);
        }
        else if (cVar1 == '\0') {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1c);
        }
        else {
          uVar9 = *(undefined1 *)(DAT_4401f1d0 + 0x1d);
        }
        *(undefined1 *)(iVar11 + 0x212) = uVar9;
        bVar8 = *(byte *)(iVar11 + 0x212) & 0x7f;
        if (bVar8 == 0x40) {
          FUN_43560dc4(0x1a,0xffffffdf);
          FUN_43b03a74(auStack_180,DAT_44020ee4);
          FUN_4379704c(param_1,auStack_180,iVar11);
        }
        else if (bVar8 == 0x41) {
          FUN_43560dc4(0x1a,0xffffffdf);
          FUN_43b03a74(auStack_194,DAT_44020ee4);
          FUN_43796910(param_1,auStack_194,iVar11);
        }
        else {
          FUN_43560da8(0x1a,0x20);
        }
        FUN_43afb42e(auStack_310);
        FUN_43afb476(auStack_310,DAT_44021fc8);
        uStack_2fc = 4;
        uStack_2cc = 0;
        uStack_2d0 = FUN_43afbf44(param_1);
        FUN_43b03a80(auStack_1a8,DAT_44022af4);
        uVar12 = FUN_43b03a70(iVar11);
        uVar12 = FUN_4380d708(auStack_1a8,uVar12,iVar11);
        iVar23 = FUN_4381bbf0(param_1,auStack_310,uVar12);
        if (iVar23 != 0) {
          FUN_43b04730();
        }
        FUN_43ae7542(iVar11 + 0x1c);
        FUN_43ae7542(iVar11 + 0x94);
        FUN_43ae7534(&uStack_298);
      }
    }
    if ((*(char *)(iVar11 + 0xd71) != '\0') && (iVar23 = FUN_43560d38(0x20,0), iVar23 == 0)) {
      FUN_43798204(1,1,0);
      FUN_43560d1c(0x20);
    }
    *(undefined4 *)(iVar11 + 0xbc) = uStack_270;
    *(undefined4 *)(iVar11 + 0xc0) = uStack_26c;
    *(undefined4 *)(iVar11 + 0xc4) = uStack_268;
    *(undefined4 *)(iVar11 + 200) = uStack_264;
    *(undefined4 *)(iVar11 + 0xcc) = uStack_260;
    *(undefined4 *)(iVar11 + 0xd0) = uStack_25c;
    *(undefined4 *)(iVar11 + 0xd4) = uStack_258;
    *(undefined4 *)(iVar11 + 0xd8) = uStack_254;
    *(undefined4 *)(iVar11 + 0xdc) = uStack_250;
    *(undefined4 *)(iVar11 + 0xe0) = uStack_24c;
    FUN_43ae7542(&uStack_270);
LAB_43556408:
    FUN_43ae7534(&uStack_270);
    return 5;
  default:
    FUN_43813e60(3,9,1,&DAT_43cb0f14);
    FUN_43902718(s_Sequence_Stage_Error__43cb0f28);
    return 5;
  }
  if (DAT_43f9b2b4 != '\0') {
    piVar18 = (int *)FUN_4378f9b4();
    iVar24 = *(int *)(*piVar18 + 200);
    piVar18 = (int *)FUN_4378f9b4();
    DAT_43eea8dc = 0;
    iVar27 = *(int *)(*piVar18 + 0xcc);
    DAT_43eea8d8 = 0;
    DAT_43eea8d4 = 0;
    DAT_43eea8cc = 0;
    DAT_43eea8d0 = 0;
    iVar17 = FUN_4378f9c0();
    *(undefined2 *)(iVar17 + 0x292) = 0;
    iVar17 = FUN_4378f9c0();
    *(undefined2 *)(iVar17 + 0x294) = 0;
    iVar17 = FUN_4378f9c0();
    DAT_43f9b2b6 = '\0';
    *(undefined1 *)(iVar17 + 0x290) = 0;
    iVar17 = FUN_4378f9c0();
    uVar10 = *(undefined2 *)(iVar17 + 0x292);
    iVar17 = FUN_4378f9c0();
    FUN_43901a8c(4,0x2036,uVar10,*(undefined2 *)(iVar17 + 0x294));
    iVar17 = FUN_4378f9c0();
    *(undefined2 *)(iVar17 + 0x296) = 0;
    iVar17 = FUN_4378f9c0();
    *(undefined2 *)(iVar17 + 0x298) = 0;
    DAT_43eea8dc = thunk_FUN_4381b82c();
    if (10 < DAT_43eea8dc) {
      DAT_43eea8dc = DAT_43eea8dc - 10;
    }
    if (iVar27 == 1) {
      DAT_43eea8dc = DAT_43eea8dc >> 1;
    }
    iVar17 = FUN_4378f9b4();
    iVar17 = FUN_4378de64(*(undefined4 *)(*(int *)(iVar17 + 4) + 0x14));
    iVar27 = FUN_4378f9b4();
    uVar22 = DAT_43eea8dc;
    switch(*(undefined4 *)(*(int *)(iVar27 + 8) + 0x208)) {
    case 1:
      uVar25 = iVar17 << 1;
      break;
    case 2:
      uVar25 = iVar17 << 2;
      break;
    case 3:
      uVar25 = iVar17 << 3;
      break;
    case 4:
      uVar25 = iVar17 << 4;
      break;
    default:
      iVar11 = FUN_4378f9b4();
      FUN_43813e60(3,9,1,&DAT_43cb3459,*(undefined4 *)(*(int *)(iVar11 + 8) + 0x208));
      iVar11 = FUN_4378f9b4();
      uVar22 = *(uint *)(*(int *)(iVar11 + 8) + 0x208);
      pcVar13 = s_SuperSlowMotion_BufferingPre_ERR_43cb346d;
      goto LAB_43555340;
    }
    DAT_43eea8d4 = uVar25;
    DAT_43eea8cc = FUN_4355faf0(DAT_43eea8dc,uVar25);
    uVar12 = FUN_4355faf0(uVar22 * 1000,uVar25);
    FUN_4355fd4c(uVar12,1000);
    if (iVar24 == 0) {
      uVar22 = (uVar25 >> 1) + 1;
    }
    DAT_43eea8d0 = extraout_r1_00;
    FUN_43ae931e(uVar22,DAT_440259e4);
    FUN_43901a8c(4,0x2034,DAT_43eea8d4,0);
    DAT_43f9b2b4 = '\0';
  }
  if (DAT_43f9b2b5 != '\0') {
    piVar18 = (int *)FUN_4378f9b4();
    bVar8 = *(byte *)(*piVar18 + 0xd0);
    piVar18 = (int *)FUN_4378f9b4();
    uVar22 = DAT_43eea8d4;
    uVar5 = *(ushort *)(*piVar18 + 0xd2);
    iVar17 = FUN_4355faf0(DAT_43eea8d4 * uVar5,1000);
    DAT_43eea8d8 = uVar22 * bVar8 + iVar17;
    FUN_43ae9328();
    FUN_43901a8c(4,0x2035,(uint)bVar8,(uint)uVar5);
    DAT_43f9b2b5 = '\0';
    *(undefined1 *)(iVar11 + 0x20c) = 0;
  }
  if (*(char *)(iVar11 + 0x20c) == '\0') {
    return 5;
  }
  uVar22 = *(int *)(iVar11 + 0xc50) + 1;
  *(uint *)(iVar11 + 0xc50) = uVar22;
  if (uVar22 < *(uint *)(iVar11 + 0xc4c)) {
    return 1;
  }
  FUN_439c5a04(&uStack_1c0,0,0x18);
  uStack_1b8 = *(undefined2 *)(iVar11 + 0xc74);
  uStack_1b0 = *(undefined2 *)(iVar11 + 0x526);
  uStack_1ae = *(undefined2 *)(iVar11 + 0x52e);
  uStack_1c0 = *(undefined4 *)(iVar11 + 0xc30);
  uStack_1b6 = *(undefined2 *)(iVar11 + 0xd1c);
  uStack_1bc = *(undefined4 *)(iVar11 + 0xc34);
  uStack_1b2 = *(undefined2 *)(iVar11 + 0xd1e);
  uStack_1b4 = *(undefined2 *)(iVar11 + 0xd20);
  uVar12 = FUN_438148f0();
  FUN_438149dc(uVar12,*(undefined4 *)(iVar11 + 0x1f0),&uStack_1c0);
  if ((*(uint *)(iVar11 + 0xc4c) & 1) == 0) {
    iVar17 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar17 + 4) + 0xc) == 0) goto LAB_43554dd0;
    *(undefined4 *)(iVar11 + 0xc64) = 0;
  }
  else {
    iVar17 = FUN_4378f9b4();
    uVar12 = 0;
    if (*(int *)(*(int *)(iVar17 + 4) + 0xc) != 0) {
LAB_43554dd0:
      uVar12 = 1;
    }
    *(undefined4 *)(iVar11 + 0xc64) = uVar12;
  }
  uVar12 = 0;
  if (*(char *)(iVar11 + 0x191) != '\0') {
    if (*(int *)(iVar11 + 0xc64) == 0) {
      uVar12 = 2;
    }
    else {
      uVar12 = 1;
    }
  }
  if ((*(int *)(iVar11 + 0x1b0) - 2U < 2) && (*(int *)(iVar11 + 0xc64) == 0)) {
    return 1;
  }
  iVar24 = iVar11 + 0xd68;
  iVar17 = FUN_43799a94(1,5,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc28);
  if (iVar17 == 0) {
    return 5;
  }
  if (*(int *)(iVar11 + 0xd60) != 1) {
    FUN_43b0419c(1,iVar23);
  }
  switch(*(undefined4 *)(iVar11 + 0xd5c)) {
  case 0:
    FUN_43b0417e(0xe,0xffffffff,1,iVar23);
    break;
  case 1:
    FUN_43b0417e(0xc,1,1,iVar23);
    iVar17 = *(int *)(iVar11 + 0xc54);
    uVar26 = 0x11;
    puVar33 = auStack_34;
    goto LAB_43554f30;
  case 2:
    FUN_43b0417e(4,0xffffffff,1,iVar23);
    iVar17 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,7,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_40);
    if (iVar17 == 0) {
      return 5;
    }
    uVar26 = 0x12;
    iVar17 = *(int *)(iVar11 + 0xc54);
    puVar33 = &uStack_3c;
LAB_43554f30:
    iVar17 = FUN_43799a94(1,uVar26,0x43,iVar23,0,1,0,iVar17 + 1,0,iVar24,puVar33);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,9,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc6c);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43ae8c4a(iVar23 + 1);
    iVar17 = iVar17 << 8;
    iVar24 = FUN_439035e0(iVar11 + 0x15c,0x293,iVar17,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    uVar26 = 0x20221c;
    if (*(char *)(iVar11 + 0xc89) != '\0') {
      uVar26 = 0x20221d;
    }
LAB_4355522c:
    iVar17 = FUN_439035e0(iVar11 + 0xbc,uVar26,iVar17,1,0,5);
    if (iVar17 != 0) {
      return 5;
    }
    break;
  case 3:
    FUN_43b0417e(8,0xffffffff,1,iVar23);
    iVar17 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,10,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xd14);
    if (iVar17 == 0) {
      return 5;
    }
    uVar26 = 0x14;
    iVar17 = *(int *)(iVar11 + 0xc54);
    puVar33 = &uStack_38;
    goto LAB_435551be;
  case 4:
    iVar17 = FUN_43799a94(1,0x11,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,auStack_34)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,10,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xd14);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,0x14,0x43,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_38)
    ;
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,7,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,&uStack_40);
    if (iVar17 == 0) {
      return 5;
    }
    uVar26 = 0x12;
    iVar17 = *(int *)(iVar11 + 0xc54);
    puVar33 = &uStack_3c;
LAB_435551be:
    iVar17 = FUN_43799a94(1,uVar26,0x43,iVar23,0,1,0,iVar17 + 1,0,iVar24,puVar33);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43799a94(1,9,0,iVar23,0,1,0,*(int *)(iVar11 + 0xc54) + 1,0,iVar24,iVar11 + 0xc6c);
    if (iVar17 == 0) {
      return 5;
    }
    iVar17 = FUN_43ae8c4a(iVar23 + 1);
    iVar17 = iVar17 << 8;
    iVar24 = FUN_439035e0(iVar11 + 0x15c,0x293,iVar17,1,0,5);
    if (iVar24 != 0) {
      return 5;
    }
    uVar26 = 0x20221c;
    goto LAB_4355522c;
  default:
    FUN_43813e60(5,0,1,&DAT_43c9b47c,s_Sequence_SuperSlowMotion_cpp_43cb34ac,0x378);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_SuperSlowMotion_cpp_43cb34ac,0x378);
  }
  if (*(char *)(iVar11 + 0xc18) == '\0') {
    uVar26 = 1;
  }
  else if (DAT_43f9b2b8 < 0x3c) {
    uVar26 = 0x11;
  }
  else {
    uVar26 = 1;
  }
  iVar27 = iVar11 + 0x1c;
  iVar17 = FUN_43ae8c4a(iVar23 + 1);
  iVar24 = FUN_439035e0(iVar27,*(undefined4 *)(iVar11 + 0x18c),iVar17 << 8,uVar26,0,5);
  if (iVar24 != 0) {
    DAT_43f9b2b8 = DAT_43f9b2b8 + 1;
    return 5;
  }
  DAT_43f9b2b8 = 0;
  iVar24 = FUN_439fdec4();
  if (iVar24 != 0) {
    iVar24 = FUN_4390366c(iVar11 + 0x134,iVar27,1,5);
    if (iVar24 != 0) {
      FUN_43813e60(3,9,1,&DAT_43cb3204);
      FUN_43902718(s____Error___MemMgrWrapper__AllocS_43cb3218);
      FUN_43ae7542(iVar11 + 0x134);
    }
  }
  iVar24 = FUN_4378f9b4();
  if (*(char *)(*(int *)(iVar24 + 0x50) + 0x1c) != '\0') {
    FUN_43780188(iVar27);
  }
  if (*(char *)(iVar11 + 0xd4c) != '\0') {
    *(int *)(iVar11 + 0xd50) = iVar23;
    *(undefined1 *)(iVar11 + 0xd4c) = 0;
  }
  if (*(char *)(iVar11 + 0xc68) != '\0') {
    iVar24 = FUN_4390366c(iVar11 + 0x6c,iVar27,0,5);
    if (iVar24 != 0) {
      FUN_43813e60(3,9,1,&DAT_43cb323f,*(undefined2 *)(iVar11 + 0x1c));
      uVar22 = (uint)*(ushort *)(iVar11 + 0x1c);
      pcVar13 = s____Error___AllocShare_uhndl__d__43cb3253;
LAB_43555340:
      FUN_43902718(pcVar13,uVar22);
      return 5;
    }
    *(undefined2 *)(iVar11 + 0xc6a) = *(undefined2 *)(iVar11 + 0x6c);
  }
  iVar24 = FUN_4378f9b4();
  if (((*(byte *)(*(int *)(iVar24 + 8) + 0x26a) & 1) != 0) &&
     (iVar24 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar24 + 8) + 0x268) & 4) != 0)) {
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd26) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x96);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd28) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x98);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd2a) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x9a);
    iVar24 = FUN_4378f9b4();
    *(undefined2 *)(iVar11 + 0xd2c) = *(undefined2 *)(*(int *)(iVar24 + 0x2c) + 0x9c);
    iVar24 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar24 + 0x2c) + 0xa4) != 0) {
      iVar24 = FUN_4378f9b4();
      dVar30 = (double)VectorUnsignedToFloat
                                 ((uint)*(ushort *)(*(int *)(iVar24 + 0x38) + 0x38),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar24 = FUN_4378f9b4();
      dVar31 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar24 + 0x2c) + 0xa0),
                                  (byte)(in_fpscr >> 0x16) & 3);
      iVar24 = FUN_4378f9b4();
      dVar32 = (double)VectorUnsignedToFloat
                                 (*(undefined4 *)(*(int *)(iVar24 + 0x2c) + 0xa4),
                                  (byte)(in_fpscr >> 0x16) & 3);
      dVar32 = (dVar30 * 100.0 * dVar31) / dVar32;
      if (((int)((uint)(dVar32 < 126500.0) << 0x1f) < 0) &&
         (uVar22 = VectorFloatToUnsigned(dVar32,3), uVar22 != 0)) {
        if (uVar22 < 0x31ce) {
          cVar7 = FUN_4355faf0(uVar22 + 0x32,100);
          bVar8 = cVar7 << 1;
        }
        else {
          cVar7 = FUN_4355faf0(uVar22 + 500,1000);
          bVar8 = cVar7 << 1 | 1;
        }
        *(byte *)(iVar11 + 0xd2e) = bVar8;
        goto LAB_43555446;
      }
    }
    *(undefined1 *)(iVar11 + 0xd2e) = 0xff;
  }
LAB_43555446:
  FUN_43b03a5e(&uStack_414);
  FUN_43811484(iVar11,iVar23);
  uStack_414 = *(undefined4 *)(iVar11 + 0x1ec);
  uStack_410 = *(undefined4 *)(iVar11 + 0x1f0);
  uStack_40c = *(undefined4 *)(iVar11 + 500);
  uStack_408 = 0;
  uStack_3fc = *(undefined4 *)(iVar11 + 0xc54);
  uStack_3f8 = (undefined1)*(undefined4 *)(iVar11 + 0x1f8);
  iStack_404 = iVar27;
  iStack_400 = iVar17;
  uStack_3f7 = FUN_43ae8c4a(iVar23 - *(int *)(iVar11 + 0xd50));
  uStack_3f6 = *(undefined2 *)(iVar11 + 0x1b8);
  uStack_3f4 = *(undefined2 *)(iVar11 + 0x1ba);
  cVar7 = *(char *)(iVar11 + 400);
  if (cVar7 == '\0') {
    uStack_3f2 = FUN_43ae9e86(*(undefined2 *)(iVar11 + 0x19e),0x40);
  }
  else {
    uStack_3f2 = FUN_43ae98f8();
  }
  uStack_3f0 = *(undefined2 *)(iVar11 + 0x1a0);
  uStack_3ee = 0;
  uStack_3dc = *(undefined4 *)(iVar11 + 0x1b4);
  uStack_3ec = 0;
  uStack_3ea = *(undefined2 *)(iVar11 + 0x19e);
  uStack_3d7 = 1;
  uStack_3d6 = *(undefined1 *)(iVar11 + 0x191);
  uStack_3e6 = 0;
  uStack_3e4 = 0;
  uStack_3d4 = *(undefined4 *)(iVar11 + 0xc64);
  uStack_3d0 = *(undefined4 *)(iVar11 + 0x4fc);
  uStack_3cc = *(undefined4 *)(iVar11 + 0x500);
  uStack_3c8 = *(undefined4 *)(iVar11 + 0x504);
  uStack_3c4 = *(int *)(iVar11 + 0xbd4) == 1;
  uStack_3e8 = uStack_3f0;
  uStack_3e2 = uStack_3ea;
  uStack_3e0 = uStack_3f0;
  cStack_3d8 = cVar7;
  iVar17 = FUN_43813f0c(*(undefined4 *)(iVar11 + 0x1fc));
  if (iVar17 == 0) {
    uStack_3c0 = 0;
    iStack_3bc = DAT_43eea8d8;
  }
  else {
    uStack_3c0 = 0xffffffff;
    iStack_3bc = -1;
  }
  uStack_3b8 = *(undefined4 *)(iVar11 + 0xd54);
  uStack_3b4 = *(undefined4 *)(iVar11 + 0xd58);
  auStack_3b0[0] = 0;
  uStack_36c = 0;
  uStack_34c = 0;
  uStack_32c = *(undefined2 *)(iVar11 + 0xd26);
  uStack_330 = *(undefined4 *)(iVar11 + 0xd78);
  uStack_32a = *(undefined2 *)(iVar11 + 0xd28);
  uStack_328 = *(undefined2 *)(iVar11 + 0xd2a);
  uStack_326 = *(undefined2 *)(iVar11 + 0xd2c);
  uStack_324 = *(undefined1 *)(iVar11 + 0xd2e);
  if (*(char *)(iVar11 + 0xd80) == '\0') {
    uStack_320 = 0xffffffff;
  }
  else {
    uStack_320 = *(undefined4 *)(iVar11 + 0xd7c);
  }
  uStack_31c = *(undefined4 *)(iVar11 + 0x1b0);
  uStack_318 = *(undefined4 *)(iVar11 + 0xd84);
  uStack_314 = 0;
  bStack_313 = FUN_43813f0c(*(undefined4 *)(iVar11 + 0x1fc));
  bStack_313 = bStack_313 ^ 1;
  iVar23 = FUN_43ae8c4a(iVar23 + *(int *)(iVar11 + 0xc54) + 1);
  iVar17 = FUN_4378f9b4();
  uStack_44 = (int)(uint)*(ushort *)(*(int *)(iVar17 + 4) + 0x20) >> 2;
  FUN_43ad2dfc(0xfff,&uStack_44);
  iVar24 = *(int *)(iVar11 + 0xc54);
  iVar17 = FUN_4378f9b4();
  iVar24 = iVar24 + 2;
  iVar17 = FUN_4355faf0(*(int *)(*(int *)(iVar17 + 4) + 0x18) + 0x3e7ff,0x3e800);
  switch(*(undefined4 *)(iVar11 + 0xd5c)) {
  case 0:
    *(undefined4 *)(iVar11 + 0x69c) = 0;
    *(undefined4 *)(iVar11 + 0x6a4) = 1;
    *(undefined4 *)(iVar11 + 0x6a8) = *(undefined4 *)(iVar11 + 0x24);
    *(undefined4 *)(iVar11 + 0x6ac) = *(undefined4 *)(iVar11 + 0x28);
    uVar22 = (uint)(*(char *)(iVar11 + 400) != '\0');
    goto LAB_43555848;
  case 1:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    if (*(char *)(iVar11 + 0xc89) == '\0') {
      uVar26 = 1;
    }
    else {
      uVar26 = 4;
    }
    *(undefined4 *)(iVar11 + 0x738) = uVar26;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar12,0);
    uVar26 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar12 = FUN_4378f9b4();
    uStack_3c = auStack_34[0];
    break;
  case 2:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    if (*(char *)(iVar11 + 0xc89) == '\0') {
      uVar26 = 1;
    }
    else {
      uVar26 = 4;
    }
    *(undefined4 *)(iVar11 + 0x738) = uVar26;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar12,0);
    uVar10 = *(undefined2 *)(iVar11 + 0x19e);
    uStack_38 = auStack_34[0];
    goto LAB_435557ae;
  case 3:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x738) = 6;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar12);
    uVar26 = *(undefined4 *)(iVar11 + 0xd14);
    uVar12 = FUN_4378f9b4();
    FUN_43815be0(iVar11,uVar26,uVar12,auStack_34[0],uStack_38,*(undefined2 *)(iVar11 + 0x19e));
    uVar26 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar12 = FUN_4378f9b4();
    uStack_3c = uStack_38;
    break;
  case 4:
    *(undefined4 *)(iVar11 + 0x69c) = 2;
    *(undefined4 *)(iVar11 + 0x6a0) = auStack_34[0];
    *(undefined4 *)(iVar11 + 0x6c8) = 0;
    *(undefined4 *)(iVar11 + 0x738) = 6;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar12,0);
    uVar26 = *(undefined4 *)(iVar11 + 0xd14);
    uVar12 = FUN_4378f9b4();
    FUN_43815be0(iVar11,uVar26,uVar12,auStack_34[0],uStack_38,*(undefined2 *)(iVar11 + 0x19e));
    uVar10 = *(undefined2 *)(iVar11 + 0x19e);
LAB_435557ae:
    FUN_43815e94(iVar11,uStack_40,uStack_38,uStack_3c,0,uVar10,0);
    uVar26 = *(undefined4 *)(iVar11 + 0xc6c);
    uVar12 = FUN_4378f9b4();
    break;
  default:
    FUN_43813e60(5,0,1,&DAT_43c9b47c,s_Sequence_SuperSlowMotion_cpp_43cb34ac,0x49a);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_SuperSlowMotion_cpp_43cb34ac,0x49a);
    *(undefined4 *)(iVar11 + 0x69c) = 0;
    *(undefined4 *)(iVar11 + 0x6a8) = *(undefined4 *)(iVar11 + 0x24);
    *(undefined4 *)(iVar11 + 0x6a4) = 1;
    *(undefined4 *)(iVar11 + 0x6ac) = *(undefined4 *)(iVar11 + 0x28);
    if (*(char *)(iVar11 + 400) == '\0') {
      uVar22 = 0;
    }
    else {
      uVar22 = 1;
    }
LAB_43555848:
    *(uint *)(iVar11 + 0x6c8) = uVar22;
    *(undefined4 *)(iVar11 + 0x738) = 1;
    FUN_4381592c(iVar11,*(undefined4 *)(iVar11 + 0xc28),uVar12,0);
    goto LAB_4355585c;
  }
  FUN_43814ea0(iVar11,uVar26,uVar12,&uStack_414,uStack_3c,iVar23 * 0x100 + (uStack_44 >> 4),
               iVar24 * iVar17);
LAB_4355585c:
  FUN_435564e0(iVar11,*(int *)(iVar11 + 0xc54) << 2,cVar1);
  iVar14 = FUN_437286bc();
  if (iVar14 != 0) {
    if ((*(int *)(iVar11 + 0xd60) != 1) || (DAT_4402546c[0x9d] == 0)) {
      FUN_4379b44c(0,&uStack_414);
    }
    if ((*(int *)(iVar11 + 0xd60) != 1) ||
       (piVar18 = (int *)FUN_4378f9b4(), *(int *)(*piVar18 + 0x2c) == 1)) {
      FUN_4379b44c(1,&uStack_414);
    }
    iVar14 = FUN_43813f0c(*(undefined4 *)(iVar11 + 0x1fc));
    if (((iVar14 == 0) && (iVar14 = FUN_4378f9b4(), *(short *)(*(int *)(iVar14 + 8) + 0x296) == 0))
       && (iVar14 = FUN_4378f9b4(), *(short *)(*(int *)(iVar14 + 8) + 0x298) == 0)) {
      iVar14 = FUN_4378f9b4();
      uVar12 = FUN_4378de64(*(undefined4 *)(*(int *)(iVar14 + 4) + 0x14));
      iVar14 = FUN_4378f9c0();
      uVar10 = FUN_4355faf0(DAT_43eea8d8,uVar12);
      *(undefined2 *)(iVar14 + 0x296) = uVar10;
      iVar14 = FUN_4378f9c0();
      uVar12 = FUN_4355faf0(DAT_43eea8d8 * 1000,uVar12);
      FUN_4355fd4c(uVar12,1000);
      *(undefined2 *)(iVar14 + 0x298) = extraout_r1;
      iVar14 = FUN_4378f9c0();
      uVar10 = *(undefined2 *)(iVar14 + 0x296);
      iVar14 = FUN_4378f9c0();
      FUN_43901a8c(4,0x2037,uVar10,*(undefined2 *)(iVar14 + 0x298));
    }
  }
  if (*(int *)(iVar11 + 0xd60) == 1) {
    FUN_439c5320(iVar11 + 0xc90,auStack_3b0,0x80);
  }
  FUN_43b03a74(auStack_144,DAT_44023a28);
  FUN_43796910(param_1,auStack_144,iVar11);
  iVar14 = FUN_4378f9b4();
  if ((*(byte *)(*(int *)(iVar14 + 8) + 0x267) & 0x80) != 0) {
    FUN_437fe4d4();
  }
  iVar14 = iVar23;
  iVar21 = iVar24;
  iVar16 = iVar23;
  iVar28 = iVar24;
  if (*(char *)(iVar11 + 0x20d) != '\0') {
    iVar15 = FUN_43ae9674(iVar11 + 0x15c);
    iVar20 = *(int *)(iVar11 + 0xc60);
    if (iVar15 == 0) {
      iVar14 = FUN_43ae8c4a(iVar23 + iVar20);
      iVar21 = iVar24 + iVar20;
    }
    else {
      iVar16 = FUN_43ae8c4a(iVar23 + iVar20);
      iVar28 = iVar24 + iVar20;
    }
  }
  if (*(int *)(iVar11 + 0xd60) == 1) {
    iVar21 = *(int *)(iVar11 + 0xc5c);
    iVar14 = FUN_43ae8c4a(iVar23 + iVar21);
    iVar21 = iVar24 + iVar21;
  }
  FUN_43b2a2d0(iVar27,iVar14 * 0x100 + (uStack_44 >> 4),iVar17 * iVar21,0,5);
  FUN_43b2a2d0(iVar11 + 0x15c,iVar16 * 0x100 + (uStack_44 >> 4),iVar17 * iVar28,0,5);
  if (*(int *)(iVar11 + 0xd60) != 1) {
    FUN_43b2a2d0(iVar11 + 0xbc,iVar23 * 0x100 + (uStack_44 >> 4),iVar24 * iVar17,1,5);
  }
  uStack_220 = *(undefined4 *)(iVar11 + 0xbc);
  uStack_21c = *(undefined4 *)(iVar11 + 0xc0);
  uStack_218 = *(undefined4 *)(iVar11 + 0xc4);
  uStack_214 = *(undefined4 *)(iVar11 + 200);
  uStack_210 = *(undefined4 *)(iVar11 + 0xcc);
  uStack_20c = *(undefined4 *)(iVar11 + 0xd0);
  uStack_208 = *(undefined4 *)(iVar11 + 0xd4);
  uStack_204 = *(undefined4 *)(iVar11 + 0xd8);
  uStack_200 = *(undefined4 *)(iVar11 + 0xdc);
  uStack_1fc = *(undefined4 *)(iVar11 + 0xe0);
  FUN_43ae7542(iVar11 + 0xbc);
  uStack_248 = *(undefined4 *)(iVar11 + 0x6c);
  uStack_244 = *(undefined4 *)(iVar11 + 0x70);
  uStack_240 = *(undefined4 *)(iVar11 + 0x74);
  uStack_23c = *(undefined4 *)(iVar11 + 0x78);
  uStack_238 = *(undefined4 *)(iVar11 + 0x7c);
  uStack_234 = *(undefined4 *)(iVar11 + 0x80);
  uStack_230 = *(undefined4 *)(iVar11 + 0x84);
  uStack_22c = *(undefined4 *)(iVar11 + 0x88);
  uStack_228 = *(undefined4 *)(iVar11 + 0x8c);
  uStack_224 = *(undefined4 *)(iVar11 + 0x90);
  FUN_43ae7542(iVar11 + 0x6c);
  uStack_298 = *(undefined4 *)(iVar11 + 0xe4);
  uStack_294 = *(undefined4 *)(iVar11 + 0xe8);
  uStack_290 = *(undefined4 *)(iVar11 + 0xec);
  uStack_28c = *(undefined4 *)(iVar11 + 0xf0);
  uStack_288 = *(undefined4 *)(iVar11 + 0xf4);
  uStack_284 = *(undefined4 *)(iVar11 + 0xf8);
  uStack_280 = *(undefined4 *)(iVar11 + 0xfc);
  uStack_27c = *(undefined4 *)(iVar11 + 0x100);
  uStack_278 = *(undefined4 *)(iVar11 + 0x104);
  uStack_274 = *(undefined4 *)(iVar11 + 0x108);
  FUN_43ae7542(iVar11 + 0xe4);
  uStack_270 = *(undefined4 *)(iVar11 + 0x134);
  uStack_26c = *(undefined4 *)(iVar11 + 0x138);
  uStack_268 = *(undefined4 *)(iVar11 + 0x13c);
  uStack_264 = *(undefined4 *)(iVar11 + 0x140);
  uStack_260 = *(undefined4 *)(iVar11 + 0x144);
  uStack_25c = *(undefined4 *)(iVar11 + 0x148);
  uStack_258 = *(undefined4 *)(iVar11 + 0x14c);
  uStack_254 = *(undefined4 *)(iVar11 + 0x150);
  uStack_250 = *(undefined4 *)(iVar11 + 0x154);
  uStack_24c = *(undefined4 *)(iVar11 + 0x158);
  FUN_43ae7542(iVar11 + 0x134);
  uVar9 = *(undefined1 *)(iVar11 + 0xc40);
  uVar3 = *(undefined1 *)(iVar11 + 0x213);
  uVar4 = *(undefined1 *)(iVar11 + 0x20d);
  *(undefined1 *)(iVar11 + 0x213) = 0;
  *(undefined1 *)(iVar11 + 0x20d) = 0;
  *(undefined1 *)(iVar11 + 0xc40) = 0;
  FUN_43afb42e(auStack_310);
  FUN_43afb476(auStack_310,DAT_44021a2c);
  uStack_2fc = 0;
  uStack_2cc = FUN_43afdf16(param_1);
  uStack_2d0 = FUN_43afbf44(param_1);
  FUN_43b03a80(auStack_158,DAT_44022af4);
  uVar12 = FUN_43b03a70(iVar11);
  uVar12 = FUN_4380d708(auStack_158,uVar12,iVar11);
  iVar23 = FUN_4381bbf0(param_1,auStack_310,uVar12);
  if (iVar23 != 0) {
    FUN_43b04730();
  }
  *(undefined4 *)(iVar11 + 0xbc) = uStack_220;
  *(undefined4 *)(iVar11 + 0xc0) = uStack_21c;
  *(undefined4 *)(iVar11 + 0xc4) = uStack_218;
  *(undefined4 *)(iVar11 + 200) = uStack_214;
  *(undefined4 *)(iVar11 + 0xcc) = uStack_210;
  *(undefined4 *)(iVar11 + 0xd0) = uStack_20c;
  *(undefined4 *)(iVar11 + 0xd4) = uStack_208;
  *(undefined4 *)(iVar11 + 0xd8) = uStack_204;
  *(undefined4 *)(iVar11 + 0xdc) = uStack_200;
  *(undefined4 *)(iVar11 + 0xe0) = uStack_1fc;
  FUN_43ae7542(&uStack_220);
  *(undefined4 *)(iVar11 + 0x6c) = uStack_248;
  *(undefined4 *)(iVar11 + 0x70) = uStack_244;
  *(undefined4 *)(iVar11 + 0x74) = uStack_240;
  *(undefined4 *)(iVar11 + 0x78) = uStack_23c;
  *(undefined4 *)(iVar11 + 0x7c) = uStack_238;
  *(undefined4 *)(iVar11 + 0x80) = uStack_234;
  *(undefined4 *)(iVar11 + 0x84) = uStack_230;
  *(undefined4 *)(iVar11 + 0x88) = uStack_22c;
  *(undefined4 *)(iVar11 + 0x8c) = uStack_228;
  *(undefined4 *)(iVar11 + 0x90) = uStack_224;
  FUN_43ae7542(&uStack_248);
  *(undefined4 *)(iVar11 + 0xe4) = uStack_298;
  *(undefined4 *)(iVar11 + 0xe8) = uStack_294;
  *(undefined4 *)(iVar11 + 0xec) = uStack_290;
  *(undefined4 *)(iVar11 + 0xf0) = uStack_28c;
  *(undefined4 *)(iVar11 + 0xf4) = uStack_288;
  *(undefined4 *)(iVar11 + 0xf8) = uStack_284;
  *(undefined4 *)(iVar11 + 0xfc) = uStack_280;
  *(undefined4 *)(iVar11 + 0x100) = uStack_27c;
  *(undefined4 *)(iVar11 + 0x104) = uStack_278;
  *(undefined4 *)(iVar11 + 0x108) = uStack_274;
  FUN_43ae7542(&uStack_298);
  *(undefined4 *)(iVar11 + 0x134) = uStack_270;
  *(undefined4 *)(iVar11 + 0x138) = uStack_26c;
  *(undefined4 *)(iVar11 + 0x13c) = uStack_268;
  *(undefined4 *)(iVar11 + 0x140) = uStack_264;
  *(undefined4 *)(iVar11 + 0x144) = uStack_260;
  *(undefined4 *)(iVar11 + 0x148) = uStack_25c;
  *(undefined4 *)(iVar11 + 0x14c) = uStack_258;
  *(undefined4 *)(iVar11 + 0x150) = uStack_254;
  *(undefined4 *)(iVar11 + 0x154) = uStack_250;
  *(undefined4 *)(iVar11 + 0x158) = uStack_24c;
  FUN_43ae7542(&uStack_270);
  *(undefined1 *)(iVar11 + 0x213) = uVar3;
  *(undefined1 *)(iVar11 + 0x20d) = uVar4;
  *(undefined1 *)(iVar11 + 0xc40) = uVar9;
  FUN_43ae7534(&uStack_270);
  FUN_43ae7534(&uStack_298);
  FUN_43ae7534(&uStack_248);
  FUN_43ae7534(&uStack_220);
  return 0;
}


/* query "43792a0c" */

void FUN_43792a0c(uint param_1)

{
  char cVar1;
  uint uVar2;
  ushort uVar3;
  ushort uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  undefined2 uVar15;
  uint uVar16;
  uint uVar17;
  undefined1 uVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  undefined4 uVar22;
  int iVar23;
  int iVar24;
  char *pcVar25;
  int iVar26;
  undefined4 uVar27;
  uint uVar28;
  undefined4 uVar29;
  undefined4 uVar30;
  undefined4 uVar31;
  short sVar32;
  int extraout_r1;
  uint uVar33;
  uint uVar34;
  undefined1 *puVar35;
  uint uVar36;
  undefined4 *puVar37;
  uint uVar38;
  uint uVar39;
  uint uVar40;
  uint uVar41;
  bool bVar42;
  bool bVar43;
  undefined1 *puVar44;
  undefined1 *puVar45;
  undefined1 *puVar46;
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
  
  iVar26 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Pre_S_43ca387e);
  }
  uVar19 = FUN_437876dc();
  if (*(char *)(iVar26 + 0xaa) != '\0') {
    DAT_43e9931c = DAT_43e9931c + 1;
    FUN_4355fd4c();
    if (extraout_r1 == 0) {
      uVar20 = FUN_43728564();
      uVar21 = FUN_437284b4();
      uVar22 = FUN_43ae0c38();
      FUN_4378eb78(5,2,1,&DAT_43ca3887,uVar20,uVar21,uVar22);
      uVar20 = FUN_43728564();
      uVar21 = FUN_437284b4();
      uVar22 = FUN_43ae0c38();
      FUN_43902718(s___d__d__d__43ca3896,uVar20,uVar21,uVar22);
    }
  }
  cVar1 = *(char *)(iVar26 + 0x1b);
  if (cVar1 != '\0') {
    puVar35 = &DAT_43f9a429;
    puVar37 = (undefined4 *)&DAT_f2804000;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != (undefined4 *)0xf2804110);
    puVar35 = &DAT_43f9a46d;
    puVar37 = (undefined4 *)0xf2804110;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != (undefined4 *)0xf28041e8);
    if (cVar1 == '\x01') {
      FUN_4378ec60();
      *(undefined1 *)(iVar26 + 0x1b) = 0;
    }
  }
  if (*(byte *)(iVar26 + 0x11) != 0) {
    uVar41 = (uint)*(byte *)(iVar26 + 0x11) * 100;
    uVar39 = DAT_43e9920c[2];
    uVar40 = uVar39 - *DAT_44024f64 >> 1;
    if (uVar40 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca38a1,uVar40);
      FUN_43902718(s_HS3__process_margin_warning__dus_43ca38b5,uVar40);
      FUN_43561540(s_HS3_Warning_43ca38d6);
    }
    uVar40 = uVar39 - *DAT_44022338 >> 1;
    if (uVar40 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca38e2,uVar40);
      FUN_43902718(s_HS3_IDT__process_margin_warning___43ca38f6,uVar40);
      FUN_43561540(s_HS3_IDT_Warning_43ca391b);
    }
    uVar39 = uVar39 - *DAT_44025cfc >> 1;
    if (uVar39 < uVar41) {
      FUN_4378eb78(3,9,1,&DAT_43ca392b,uVar39);
      FUN_43902718(s_HS3_RCH__process_margin_warning___43ca393f,uVar39);
      FUN_43561540(s_HS3_RCH_Warning_43ca3964);
    }
  }
  if (param_1 != *DAT_43e9920c) {
    iVar23 = thunk_FUN_436cd00c();
    uVar39 = iVar23 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3974,param_1,*DAT_43e9920c,uVar39);
    FUN_43902718(s_VD_Pre__start_delayed__dV__>__dV_43ca3988,param_1,*DAT_43e9920c,uVar39);
    FUN_4378f988(3,0,uVar39);
    if ((*(byte *)(iVar26 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Pre_S_OF_43ca39ae);
    }
    if ((*(byte *)(iVar26 + 0x1b) & 2) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar23 = FUN_43ae8d4e();
  if (iVar23 == 0) {
    FUN_43901778();
    if (DAT_4401e926 != '\0') {
      DAT_43f9a4b8 = '\x01';
    }
    DAT_4401e926 = 0;
  }
  else {
    DAT_4401e926 = 1;
  }
  if (*(byte *)(iVar26 + 0x20) == 0) {
    DAT_43f79b84 = 0;
  }
  else {
    if (DAT_43e9920c[5] - 1 < 2) {
      sVar32 = *(short *)(&DAT_43bef280 + (DAT_43e9920c[5] - 1) * 2);
    }
    else {
      sVar32 = 0x3c;
    }
    DAT_43f79b84 = sVar32 * (ushort)*(byte *)(iVar26 + 0x20);
  }
  DAT_43e9946c = DAT_43e9946c + 1;
  DAT_43f9a4a5 = 0;
  FUN_4378f7a0(0x708);
  iVar23 = FUN_437999e4(1,1);
  if (((iVar23 != 0) || (iVar23 = FUN_437999e4(1,2), iVar23 != 0)) &&
     ((DAT_43e9bbb8 < 2 || (DAT_43e9920c[3] != 0)))) {
    FUN_43aef52c(&DAT_43e99208,&DAT_43e9c7d8);
    FUN_437d9a04(&DAT_43e9ced8,&DAT_43e99208);
    if (((*(byte *)(iVar26 + 0x16) & 5) == 4) && (DAT_43e9bdbc != 0)) {
      FUN_43ad53b8(&DAT_43e9bdc0,DAT_43e9bdbc,0);
    }
  }
  FUN_43a0cb54();
  FUN_43b2a04a();
  FUN_437fdf5c();
  uVar15 = DAT_43e9b55e;
  uVar14 = DAT_43e9b55c;
  uVar13 = DAT_43e9b55a;
  uVar12 = DAT_43e9b558;
  uVar11 = DAT_43e9b556;
  uVar10 = DAT_43e9b554;
  uVar9 = DAT_43e9b552;
  uVar8 = DAT_43e9b550;
  uVar7 = DAT_43e9b54e;
  uVar6 = DAT_43e9b54c;
  uVar5 = DAT_43e9b54a;
  uVar3 = DAT_43e9b548;
  FUN_43804c5c(&DAT_43e9b548);
  DAT_43e9b548 = uVar3;
  DAT_43e9b54a = uVar5;
  DAT_43e9b54c = uVar6;
  DAT_43e9b54e = uVar7;
  DAT_43e9b550 = uVar8;
  DAT_43e9b552 = uVar9;
  DAT_43e9b554 = uVar10;
  DAT_43e9b556 = uVar11;
  DAT_43e9b558 = uVar12;
  DAT_43e9b55a = uVar13;
  DAT_43e9b55c = uVar14;
  DAT_43e9b55e = uVar15;
  FUN_43ae8fa2();
  FUN_43ae8f98();
  FUN_437fc404(&DAT_43e99208);
  FUN_437fc54c(1);
  FUN_4375dd04();
  iVar23 = FUN_437fc54c(0);
  FUN_4380c7f8(iVar23,auStack_38);
  bVar42 = false;
  if ((bStack_34 & 0x20) != 0) {
    if (*(uint *)(DAT_43e99214 + 0xc) < 2) {
      bVar42 = false;
      if (*(char *)(DAT_43e99214 + 0x11) != '\0') {
        bVar42 = *(int *)(DAT_43e99208 + 0x2c4) != 0;
      }
    }
    else {
      bVar42 = false;
    }
  }
  iVar24 = FUN_43b00cb4(uVar19);
  if ((((iVar24 == 1) && (iVar23 == 0x110)) &&
      (sVar32 = *(short *)(DAT_43e99210 + 0x240), sVar32 != 0x110)) && (sVar32 != 0x101)) {
    bVar43 = sVar32 != 0x100;
  }
  else {
    bVar43 = false;
  }
  if ((((DAT_43e9920c[3] == 1) || (DAT_43e9bb18 < 2)) || (bVar42)) && (!bVar43)) {
    DAT_43e9b548 = FUN_437fc54c();
    DAT_43e9b54a = FUN_437fc54c(2);
    DAT_43e9b54c = FUN_437fc54c(1);
    DAT_43e9b54e = FUN_437fc54c(3);
    DAT_43e9b552 = FUN_437fc54c(5);
    DAT_43e9b550 = FUN_437fc54c(4);
    DAT_43e9b554 = FUN_437fc54c(6);
    DAT_43e9b556 = FUN_437fc54c(8);
    DAT_43e9b55a = FUN_437fc54c(10);
    DAT_43e9b558 = FUN_437fc54c(9);
    DAT_43e9b55e = FUN_437fc54c(0xc);
    if (DAT_43e9920c[5] == DAT_43e9920c[0xd]) {
      DAT_43e9b55c = FUN_437fc54c(0xb);
    }
    FUN_4380c7f8(DAT_43e9b548,&DAT_43e9bd50);
  }
  iVar23 = DAT_43e99210;
  if (*(int *)(DAT_43e99208 + 0xb4) == 1) {
    DAT_43f9a4ba = DAT_43f9a427;
    DAT_43f9a4bb = DAT_43f9a428;
    FUN_43796044(&DAT_43f9a427);
    iVar24 = 0;
    if (DAT_43f9a428 != '\0') {
      if (DAT_43f9a4bb != '\0') goto LAB_43792f54;
      iVar24 = FUN_4378f9b4();
      iVar24 = **(int **)(iVar24 + 4) + 5;
    }
    *(int *)(iVar23 + 0x204) = iVar24;
  }
LAB_43792f54:
  iVar23 = FUN_43b00cba(uVar19);
  if (iVar23 != 0) {
    FUN_43b00dd4(uVar19);
    FUN_43805b04(uVar19,&DAT_43e99208,&DAT_43e9b548,&DAT_43e9baec);
    FUN_43b00e40(uVar19,&DAT_43e99208);
  }
  FUN_437da078(&DAT_43e99208,&DAT_43e9d3b4);
  FUN_43ae7564(&DAT_43e99208,&DAT_43e9d3b4);
  iVar24 = DAT_43e99210;
  iVar23 = DAT_43e99208;
  if (*(int *)(DAT_43e99208 + 0xb4) == 2) {
    *(undefined4 *)(DAT_43e99210 + 0x204) = *(undefined4 *)(DAT_43e99210 + 0x238);
    *(undefined1 *)(iVar24 + 0x202) = *(undefined1 *)(iVar24 + 0x234);
  }
  DAT_43e9bd08 = DAT_43e9bd55 & 0x40;
  if (((DAT_43e9bd55 & 0x40) != 0) && (DAT_43e9bd08 = 1, *(int *)(iVar23 + 0x30) != 1)) {
    DAT_43e9bd08 = 0;
  }
  if ((DAT_43f9a4b9 != DAT_43e9bd08) || (DAT_43e99378 != *(int *)(iVar23 + 0x34))) {
    FUN_43901a8c(4,0x203e,DAT_43e9bd08,*(undefined4 *)(iVar23 + 0x34));
    DAT_43f9a4b9 = DAT_43e9bd08;
    DAT_43e99378 = *(int *)(DAT_43e99208 + 0x34);
  }
  if ((*(byte *)(DAT_43e99210 + 0x266) & 0x20) == 0) {
    DAT_43e9bcf4 = 0;
  }
  else if ((ushort)(DAT_43e9b548 - 0x148) < 2) {
    switch(DAT_43e9b60c) {
    case 8:
      DAT_43e9bcf4 = 1;
      break;
    case 9:
      DAT_43e9bcf4 = 2;
      break;
    case 10:
      DAT_43e9bcf4 = 3;
      break;
    case 0xb:
      DAT_43e9bcf4 = 4;
    }
  }
  else {
    if ((DAT_43e9bd08 == 0) || (*(int *)(DAT_43e99208 + 0x34) != 0)) {
      DAT_43e9bcf4 = 0;
    }
    else if (DAT_43e9b60c == 8) {
      DAT_43e9bcf4 = 1;
    }
    else {
      DAT_43e9bcf4 = 0;
      if (DAT_43e9b60c == 9) {
        DAT_43e9bcf4 = 2;
      }
    }
    if (DAT_43e993a0 != DAT_43e9bcf4) {
      FUN_43901a8c(4,0x203f,DAT_43e9bcf4,0);
      DAT_43e993a0 = DAT_43e9bcf4;
    }
  }
  if (((DAT_43e9bd50 & 0xf8000) == 0x38000) && (*(int *)(DAT_43e99208 + 0x474) == 2)) {
    DAT_43e9bd31 = '\x01';
  }
  else {
    DAT_43e9bd31 = '\0';
  }
  if (DAT_43f9a4a8 != DAT_43e9bd31) {
    FUN_43901a8c(4,0x2043,DAT_43e9bd31,0);
    DAT_43f9a4a8 = DAT_43e9bd31;
  }
  switch(DAT_43e9bd50 & 7) {
  case 1:
    DAT_43e9bccc = 2;
    goto LAB_437931a0;
  case 2:
    DAT_43e9bccc = 1;
    DAT_43e9bcc0 = *(uint *)(DAT_44020e90 + 0x50);
    if (DAT_43e9bcc0 == 1) {
      DAT_43e9bcd0 = 1;
    }
    else {
      if ((((((DAT_43e9bd50 & 0x400000) == 0) || (iVar23 = FUN_43728564(), iVar23 != 0)) ||
           (*(int *)(DAT_43e99208 + 0x9c) != 0)) || (*(int *)(DAT_43e99208 + 0x94) != 0)) ||
         (((DAT_43e9bd50 & 0xf8000) == 0x10000 &&
          ((*(char *)(DAT_43e99240 + 0x74) != '\0' || (iVar23 = thunk_FUN_43ae69d6(), iVar23 != 0)))
          ))) goto LAB_437945b6;
      DAT_43e9bcd0 = 0;
    }
    break;
  case 3:
    DAT_43e9bccc = 1;
    if (DAT_43e9bcf4 == 0) {
      DAT_43e9bcc0 = *(uint *)(DAT_43e99208 + 0x20);
    }
    else if ((-1 < DAT_43e9bcf4) && (DAT_43e9bcf4 < 5)) {
      DAT_43e9bcc0 = 0;
    }
    goto LAB_437945b6;
  case 4:
    DAT_43e9bcc0 = 1;
    goto LAB_4379328a;
  case 5:
    DAT_43e9bcc0 = 0;
LAB_4379328a:
    DAT_43e9bccc = 1;
    DAT_43e9bcd0 = 1;
    break;
  case 6:
    DAT_43e9bccc = 1;
    DAT_43e9bcc0 = *(uint *)(DAT_44020e90 + 0x50);
    break;
  default:
    DAT_43e9bccc = 0;
LAB_437931a0:
    DAT_43e9bcc0 = DAT_43e9920c[0xc];
LAB_437945b6:
    DAT_43e9bcd0 = 1;
  }
  DAT_43e9bcc4 = FUN_43ae8c50(DAT_43e9bcc0);
  DAT_43e9bcc8 = DAT_43e9bcc4 != DAT_43e9920c[5];
  iVar23 = FUN_436e9234();
  DAT_43e9bcf8 = *(int *)(DAT_43e99208 + 0x178);
  DAT_43e9bcfc = *(undefined4 *)(&DAT_43bc42e8 + (iVar23 * 3 + *(int *)(DAT_43e99208 + 0x174)) * 4);
  DAT_43e9bd00 = (uint)*(byte *)(DAT_43e99208 + 0x17c);
  if ((DAT_43e99204 != DAT_43e9bcf8) || (DAT_43e992bc != DAT_43e9bd00)) {
    FUN_439d88c4();
    FUN_43901a8c(4,0x2030,DAT_43e9bcf8,0xff);
    uVar21 = *(undefined4 *)(DAT_43e99208 + 0x174);
    uVar20 = FUN_436e9234();
    FUN_43901a8c(4,0x2031,uVar21,uVar20);
    FUN_43901a8c(4,0x203c,DAT_43e9b5ac,DAT_43e9bd00);
    DAT_43e99204 = DAT_43e9bcf8;
    DAT_43e992bc = DAT_43e9bd00;
  }
  if ((DAT_43f9a4a6 == '\0') &&
     ((((DAT_43e9b548 == 0x11a || (DAT_43e9b548 == 0x118)) || (DAT_43e9b548 == 0x102)) ||
      (((DAT_43e9b548 == 0x11b || (DAT_43e9b548 == 0x119)) || (DAT_43e9b548 == 0x107)))))) {
    if (*(int *)(DAT_43e99208 + 0x174) == 1) {
      FUN_439c5a04(auStack_54,0,9);
      uStack_52 = 0x40d4;
      uStack_4c = (undefined1)DAT_43e9bcfc;
      auStack_54[0] = 5;
      FUN_435aa02c(auStack_2c);
      FUN_435a92e0(auStack_218);
      iVar23 = FUN_43a49628(auStack_218,0x30001);
      if (iVar23 == 0) {
        iVar23 = FUN_435a9304(auStack_218,auStack_54,9);
        if (iVar23 != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca39e6,iVar23);
          pcVar25 = s_VD_Pre__SetGlobalMsg_err__d_43ca39fa;
          goto LAB_43793456;
        }
        iVar23 = FUN_435aa20c(auStack_2c,0x30001,auStack_218);
        if (iVar23 != 0) {
          FUN_4378eb78(3,9,1,&DAT_43ca3a16,iVar23);
          pcVar25 = s_VD_Pre__SendASync_err__d_43ca3a2a;
          goto LAB_43793456;
        }
      }
      else {
        FUN_4378eb78(3,9,1,&DAT_43ca39ba,iVar23);
        pcVar25 = s_VD_Pre__SetSrcId_err__d_43ca39ce;
LAB_43793456:
        FUN_43902718(pcVar25,iVar23);
      }
      FUN_435a92c8(auStack_218);
      FUN_435aa014(auStack_2c);
    }
    DAT_43f9a4a6 = '\x01';
  }
  FUN_437c1740(&DAT_43e99208,&DAT_43e9cc78);
  uVar39 = (DAT_43e9bd50 & 0x3f) >> 4;
  if (uVar39 == 1) {
    DAT_43e9bb08 = DAT_43e9b564;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    DAT_43e9bb0c = DAT_43e9b570;
    DAT_43e9bb10 = 0;
    DAT_43e9bb14 = 0;
    DAT_43e9b590 = 0;
    iVar23 = FUN_43794a44(&DAT_43e99208);
    if (iVar23 != 0) {
      switch(DAT_43e9b9a0) {
      case 0:
        DAT_43e9bb14 = 0;
        break;
      case 1:
        DAT_43e9bb14 = 1;
        break;
      case 2:
        DAT_43e9bb14 = 2;
        break;
      case 3:
        DAT_43e9bb14 = 4;
        break;
      default:
        FUN_4378eb78(5,0,1,&DAT_43c9b47c,s_SyncTask_cpp_43ca3a43,0x93c);
        FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncTask_cpp_43ca3a43,0x93c);
      }
    }
    goto LAB_437937a2;
  }
  if (uVar39 == 2) {
    DAT_43e9bcb4 = DAT_43e9b9b8;
    if (DAT_43e9920c[4] == *(uint *)(DAT_43e99208 + 0x20)) {
      DAT_43e9bb08 = *(undefined4 *)(DAT_43e99208 + 0x1c);
      DAT_43e9bb14 = *(undefined4 *)(DAT_43e99208 + 0x24);
      DAT_43e9bb0c = *(int *)(DAT_43e99208 + 0x28);
      if ((DAT_43e9bd50 & 0x1c0) == 0) {
        DAT_43e9bb10 = (byte)((DAT_43e9bd50 << 0x17) >> 0x1d);
        if (((DAT_43e9bb0c == 1) && ((*(int *)(DAT_43e99208 + 0x538) != 1 || (DAT_43e9bcc0 != 0))))
           && (DAT_43e9bd31 == '\0')) {
          DAT_43e9bb10 = 1;
        }
      }
      else {
        DAT_43e9bb10 = 0;
      }
    }
    goto LAB_437937a2;
  }
  DAT_43e9bb08 = DAT_43e9b564;
  DAT_43e9bb0c = DAT_43e9b570;
  DAT_43e9bb10 = 0;
  iVar23 = FUN_43794a44(&DAT_43e99208);
  uVar20 = DAT_43e9b590;
  if (iVar23 != 0) {
    uVar20 = DAT_43e9b9a0;
  }
  switch(uVar20) {
  case 0:
    DAT_43e9bb14 = 0;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  case 1:
    goto LAB_4379357a;
  case 2:
    DAT_43e9bb14 = 2;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  case 3:
    DAT_43e9bb14 = 4;
    DAT_43e9bcb4 = DAT_43e9b9b0;
    break;
  default:
    FUN_4378eb78(5,0,1,&DAT_43c9b47c,s_SyncTask_cpp_43ca3a43,0x91e);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncTask_cpp_43ca3a43,0x91e);
LAB_4379357a:
    DAT_43e9bb14 = 1;
    DAT_43e9bcb4 = DAT_43e9b9b0;
  }
LAB_437937a2:
  FUN_4380f440(&DAT_43e99208,&DAT_43e994d0,&DAT_43e9baec,0);
  if (*(byte *)(iVar26 + 0xb3) != 0) {
    DAT_43e994d0 = (uint)*(byte *)(iVar26 + 0xb3);
  }
  FUN_4380e0cc(&DAT_43e99208,&DAT_43e994d0);
  FUN_4380e138(&DAT_43e99458);
  if ((uint)DAT_43f9a4a7 != (int)(char)DAT_43e9945d) {
    DAT_43f9a4a7 = DAT_43e9945d;
    FUN_43ae913c(auStack_68,&LAB_4378f364_1);
    FUN_439018b0(&DAT_43e992e0,auStack_68,&DAT_43e99458,0);
  }
  if ((1 < DAT_43e9bb18) && ((DAT_43e9bcd4 & 1) != DAT_43e9920c[3])) {
    if (DAT_43e9920c[3] == 0) {
      DAT_43e9bcd4 = 2;
    }
    else {
      DAT_43e9bcd4 = 1;
    }
    DAT_43e9bce4 = DAT_43e9bcd4;
    FUN_4378ea78(0);
  }
  if (DAT_43e9bcc0 == DAT_43e9bad8) {
    uVar39 = DAT_43e9920c[0xf];
    if (uVar39 == 0) {
      iVar23 = FUN_43b00cba(uVar19);
      if ((((iVar23 == 0) || (DAT_43e9b600 != 1)) || ((DAT_43e9bd0c & 1) == 0)) ||
         (DAT_43e9920c[3] != 0)) {
        iVar23 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
        if (iVar23 == 0) {
          if (bVar42) {
            FUN_4378ea78();
            DAT_43e9bcd4 = 0;
            DAT_43e9bce4 = 0;
          }
          else if ((DAT_43e9b548 == 0x121) || (DAT_43e9b548 == 300)) {
            FUN_4378ea78(0);
            DAT_43e9bcd4 = 0;
            DAT_43e9bce4 = 0;
          }
          else if (DAT_43e9bb18 < 2) {
            if (DAT_43e9920c[3] == 0) {
              uVar39 = 0;
LAB_43793978:
              FUN_4378ea78();
              DAT_43e9bcd4 = uVar39;
              DAT_43e9bce4 = uVar39;
            }
          }
          else {
            uVar39 = 1;
            if (DAT_43e9920c[3] == 1) goto LAB_43793978;
          }
        }
        else {
          FUN_4380c7f8(uVar3,auStack_40);
          if (((bVar42) && (uVar39 = bStack_3c & 0x20, (bStack_3c & 0x20) == 0)) &&
             (DAT_43e9bcd4 != 0)) {
            FUN_4378ea78(uVar39);
            DAT_43e9bcd4 = uVar39;
            DAT_43e9bce4 = uVar39;
          }
        }
      }
      else {
        FUN_4378ea78(0);
        DAT_43e9bd0c = DAT_43e9bd0c & 0xfe;
        DAT_43e9bcd4 = 0;
        DAT_43e9bce4 = 0;
      }
    }
    else {
      uVar40 = *(int *)(DAT_43e99210 + 0x1e8) + 1;
      if (uVar39 <= uVar40) {
        if (uVar39 == uVar40) {
          iVar23 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
          if (iVar23 == 0) {
            DAT_43e9bce4 = DAT_43e9bcd4;
            FUN_4378ea78();
          }
        }
        else {
          FUN_4378ea78(0);
          DAT_43e9bcd4 = DAT_43e9920c[0xf] - 1;
          DAT_43e9bce4 = DAT_43e9920c[0xf] - 1;
        }
      }
    }
  }
  uVar39 = DAT_43e9ba54;
  switch(*(undefined1 *)(iVar26 + 1)) {
  case 1:
    uVar39 = 0;
    break;
  case 2:
    uVar39 = 2;
    break;
  case 3:
    uVar39 = 1;
    break;
  case 4:
    uVar39 = 3;
  }
  if (((uint)DAT_43e9bca8 != (uVar39 & 3) >> 1) || ((uint)DAT_43e9bca9 != (uVar39 & 1))) {
    DAT_43e9bca9 = (byte)(uVar39 & 1);
    DAT_43e9bca8 = (byte)((uVar39 << 0x1e) >> 0x1f);
    FUN_4378ea78(0);
  }
  iVar26 = FUN_43ae8d4e();
  if ((iVar26 == 0) || (DAT_43f9a4b8 != '\0')) {
    FUN_4378ea78(1);
    DAT_43f9a4b8 = '\0';
  }
  uVar20 = DAT_44025f5c;
  iVar26 = FUN_43ae8cc8(DAT_44025f5c);
  if (iVar26 != 0) {
    DAT_43e9bce4 = DAT_43e9bcd4;
  }
  DAT_43e9bcd9 = '\x01' - (char)DAT_43e9bcd4;
  if (1 < DAT_43e9bcd4) {
    DAT_43e9bcd9 = '\0';
  }
  DAT_43e9bcd8 = 1 >= DAT_43e9bcd4;
  DAT_43e9bce8 = '\x01' - (char)DAT_43e9bce4;
  if (1 < DAT_43e9bce4) {
    DAT_43e9bce8 = '\0';
  }
  DAT_43e9d029 = FUN_43ae8ccc(uVar20);
  if ((DAT_43e9bd50 & 0x100000) == 0) {
    uStack_30 = *(undefined4 *)(DAT_43e99214 + 4);
  }
  else {
    uStack_30 = *(undefined4 *)(DAT_43e99214 + 0xc);
  }
  iVar26 = FUN_43b00cba(uVar19);
  if ((iVar26 != 0) && (*(int *)(DAT_43e99208 + 0xb8) == 1)) {
    FUN_43b00e4c(uVar19,&DAT_43e99208,&uStack_30);
  }
  DAT_43e9bb28 = FUN_4380e15c(&DAT_43e99208,uStack_30,&DAT_43e99320,
                              DAT_43e9bcd4 + DAT_43e9920c[3] & 1);
  iVar23 = FUN_437955ec();
  iVar26 = DAT_4402546c;
  if (iVar23 == 1) {
    DAT_43e9bcdc = DAT_43e9bb28;
    if (DAT_43e9bce8 != '\0') {
      DAT_43e9bce0 = DAT_43e9bce0 + '\x01';
    }
  }
  else if (iVar23 == 2) {
    if (((*(byte *)(DAT_4402546c + 0x22) & 1) == 0) &&
       (uVar39 = *(uint *)(DAT_43e99214 + 8), DAT_43e9bbb8 < 2)) {
      uVar40 = DAT_43e9bb18;
      if (DAT_43e9bcd9 != '\0') {
        uVar40 = DAT_43e9bb28;
      }
      if (uVar40 != 0) {
        if (uVar40 == 1) {
          uVar40 = 1;
        }
        else {
          uVar40 = 2;
        }
        if (uVar39 < uVar40) {
          uVar39 = uVar40;
        }
      }
      if ((1 < uVar39) &&
         (uVar39 = FUN_43acf19e(uVar39,2), (DAT_43e9bce4 + DAT_43e9920c[3] & 1) != 0)) {
        uVar39 = 1;
      }
    }
    else {
      DAT_43e9bcdc = DAT_43e9bb28;
      uVar39 = DAT_43e9bcdc;
    }
    DAT_43e9bcdc = uVar39;
    if (DAT_43e9bce8 != '\0') {
      DAT_43e9bce0 = DAT_43e9bce0 + '\x01';
    }
  }
  else if (iVar23 == 0) {
    DAT_43e9bcdc = DAT_43e9bb28;
  }
  if (DAT_43e9bb30 != 0x11) {
    uVar19 = DAT_43e9bcac;
    if (DAT_43e9bd48 != 0) {
      uVar19 = 10;
    }
    DAT_43e9bcb0 = FUN_43acc1a6(DAT_43e9bb30,uVar19);
  }
  if ((DAT_43e9bb30 == 0x12) || (DAT_43e9bb30 == 0x3f)) {
    DAT_43e9baec = 1;
  }
  else if (DAT_43e9bb30 == 8) {
    DAT_43e9baec = 2;
  }
  else {
    DAT_43e9baec = *(undefined4 *)(DAT_44020e90 + 0x40);
  }
  if (*(char *)(DAT_4401f1d0 + 0x43) == '\x01') {
    DAT_43e9bcb8 = 1;
  }
  else {
    DAT_43e9bcb8 = 0;
    if (DAT_43e9b624 != '\0') {
      DAT_43e9bcb8 = DAT_43e9d310 ^ 1;
    }
  }
  if (DAT_43e9d310 == 0) {
    DAT_43e9bcbc = *(undefined4 *)(DAT_43e99208 + 0xbc);
  }
  else {
    DAT_43e9bcbc = 1;
  }
  DAT_43e9bb2d = DAT_43e9bb1c;
  if (DAT_43e9bcd9 != '\0') {
    DAT_43e9bb2d = DAT_43e9bb1c + '\x01';
  }
  DAT_43e9bdb4 = FUN_43ae8d10(uVar20);
  DAT_43e9bdb8 = FUN_43ae8d14(uVar20);
  if (DAT_43e99320 != DAT_43e9939c) {
    FUN_43901a8c(4,0x203d);
    DAT_43e9939c = DAT_43e99320;
  }
  uVar41 = DAT_43e9bcd4;
  uVar40 = DAT_43e9bb28;
  uVar39 = DAT_43e9bb18;
  if ((*(byte *)(iVar26 + 3) & 1) != 0) {
    uVar36 = *DAT_43e9920c;
    uVar38 = DAT_43e9920c[3];
    uVar27 = FUN_437955ec();
    uVar5 = DAT_43e9bd58;
    uVar17 = DAT_43e9bce4;
    uVar16 = DAT_43e9bcdc;
    uVar22 = DAT_43e9bb20;
    uVar4 = DAT_43e9b548;
    uVar21 = DAT_43e994dc;
    uVar2 = DAT_43e994d0;
    uVar19 = DAT_43e9932c;
    iVar23 = DAT_43e99320;
    uVar33 = DAT_43e9920c[4];
    uVar34 = DAT_43e9920c[0xc];
    uVar28 = DAT_43e9920c[0xf];
    uVar29 = FUN_43ae8cd0(uVar20);
    uVar30 = FUN_43ae8cc8(uVar20);
    uVar31 = FUN_43ae8ccc(uVar20);
    FUN_4378eb78(3,9,1,&DAT_43ca3a50,uVar36,uVar38,uVar39,uVar40,uVar41,uVar27,uVar22,uVar16,uVar17,
                 uVar33,uVar34,uVar28,uVar4,uVar5,iVar23,uVar2,uVar19,uVar21,uVar29,uVar30,uVar31);
    uVar2 = DAT_43e9bcd4;
    uVar41 = DAT_43e9bb28;
    uVar40 = DAT_43e9bb18;
    uVar28 = *DAT_43e9920c;
    uVar36 = DAT_43e9920c[3];
    uVar27 = FUN_437955ec();
    uVar5 = DAT_43e9bd58;
    uVar17 = DAT_43e9bce4;
    uVar16 = DAT_43e9bcdc;
    uVar22 = DAT_43e9bb20;
    uVar4 = DAT_43e9b548;
    uVar21 = DAT_43e994dc;
    uVar39 = DAT_43e994d0;
    uVar19 = DAT_43e9932c;
    iVar23 = DAT_43e99320;
    uVar34 = DAT_43e9920c[4];
    uVar33 = DAT_43e9920c[0xc];
    uVar38 = DAT_43e9920c[0xf];
    uVar29 = FUN_43ae8cd0(uVar20);
    uVar30 = FUN_43ae8cc8(uVar20);
    uVar31 = FUN_43ae8ccc(uVar20);
    FUN_43902718(s_vfc_d__d__shut_d_>_d__d__zaf__d__43ca3a64,uVar28,uVar36,uVar40,uVar41,uVar2,
                 uVar27,uVar22,uVar16,uVar17,uVar34,uVar33,uVar38,uVar4,uVar5,iVar23,uVar39,uVar19,
                 uVar21,uVar29,uVar30,uVar31);
  }
  uVar19 = FUN_43b039fc(&DAT_43e9948c,&DAT_43e994d0);
  FUN_43780080(&DAT_43e99208,&DAT_43e9d3b4,uVar19);
  FUN_4380db04(&DAT_43e99208,&DAT_43e9d3b4);
  FUN_4378c4d0(&DAT_43e9baec);
  FUN_4378f7a0(0xb2a);
  iVar23 = FUN_43ae8cd0(uVar20);
  if (iVar23 == 0) {
    FUN_43ae8cda(uVar20);
  }
  FUN_4377e0e8(&DAT_43e99208);
  FUN_437217f8(DAT_43e9920c[6]);
  FUN_437b4db8(&DAT_43e99208,&DAT_43e9c7d8);
  FUN_437c194c(&DAT_43e99208,&DAT_43e9cc78);
  thunk_FUN_437d0e5c(&DAT_43e99208,&DAT_43e9ce1c);
  FUN_4378f754(&DAT_43e9b548,&DAT_43e9d024);
  FUN_43af6784(&DAT_43e9ced8,&DAT_43e99208);
  FUN_4378f7a0(0xb51);
  if (*DAT_43e9921c == '\0') {
    uVar19 = 0;
    if (*(char *)(iVar26 + 0xec) == '\0') {
      uVar19 = *(undefined4 *)(DAT_43e9921c + 4);
    }
  }
  else {
    uVar19 = 0;
  }
  uVar20 = FUN_43814138();
  iVar23 = FUN_43799a38(1,1,*DAT_43e9920c,0);
  if (iVar23 == 0) {
    iVar23 = FUN_43799a38(1,2,*DAT_43e9920c,0);
    bVar42 = iVar23 != 0;
  }
  else {
    bVar42 = true;
  }
  DAT_43e9bd34 = FUN_43b03c62(uVar20,uVar19,bVar42);
  if ((*(char *)(iVar26 + 0xed) == '\0') &&
     ((*(int *)(DAT_44020e90 + 0x44) == 3 || (*(int *)(DAT_44020e90 + 0x44) == 4)))) {
    if ((*(ushort *)(DAT_43e99210 + 0x264) & 0x1ff) >> 6 != 0) {
      uVar19 = FUN_438148f0();
      uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
      goto LAB_4379405e;
    }
    auStack_48[0] = DAT_43e9bd86;
    uStack_44 = DAT_43e9bb08;
    thunk_FUN_438aaab8(auStack_48,auStack_3a8);
    uVar19 = FUN_438148f0();
    uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
    puVar44 = auStack_348;
    puVar35 = auStack_3a8;
    puVar45 = auStack_2e0;
    puVar46 = auStack_280;
  }
  else {
    uVar19 = FUN_438148f0();
    uVar20 = FUN_43799a38(1,10,*DAT_43e9920c,0);
LAB_4379405e:
    puVar35 = (undefined1 *)0x0;
    uStack_2e8 = 0;
    puVar44 = (undefined1 *)0x0;
    uStack_2e4 = 0;
    puVar45 = (undefined1 *)0x0;
    uStack_220 = 0;
    puVar46 = (undefined1 *)0x0;
    uStack_21c = 0;
  }
  FUN_4381493c(&uStack_3b8,uVar19,puVar35,uStack_2e8,puVar44,uStack_2e4,puVar45,uStack_220,puVar46,
               uStack_21c,uVar20);
  DAT_43e9bd38 = uStack_3b8;
  DAT_43e9bd3c = uStack_3b4;
  DAT_43e9bd40 = uStack_3b0;
  DAT_43e9bd44 = uStack_3ac;
  FUN_43ae8faa(&DAT_43e99514,&DAT_43e9b548);
  FUN_43ae8eae(&DAT_43e99514,&DAT_43e993a4);
  if ((DAT_43e9bd4c & 4) == 0) {
    FUN_43560da8(0x11,4);
    FUN_43ae9148(auStack_7c,&LAB_43791454_1);
    FUN_437b4f2c(&DAT_43e993a4,auStack_7c,4);
  }
  if ((DAT_43e9bd4c & 2) == 0) {
    FUN_43560da8(0x11,2);
    FUN_43ae9148(auStack_90,&LAB_43ae8d46_1);
    FUN_437c297c(&DAT_43e993a4,auStack_90,2);
  }
  if ((DAT_43e9bd4c & 0x80) == 0) {
    FUN_43560da8(0x11,0x80);
    FUN_43ae9148(auStack_a4,&LAB_43ae8d46_1);
    FUN_437b66e0(&DAT_43e993a4,auStack_a4,0x80);
  }
  if ((DAT_43e9bd4c & 8) == 0) {
    FUN_43560da8(0x11,8);
    FUN_43ae9148(auStack_b8,&LAB_43ae8d46_1);
    FUN_4379fd58(&DAT_43e993a4,auStack_b8,8);
  }
  if ((DAT_43e9bd4c & 0x40) == 0) {
    FUN_43560da8(0x11,0x40);
    FUN_43ae9148(auStack_cc,&LAB_43ae8d46_1);
    FUN_437d9e00(&DAT_43e993a4,auStack_cc,0x40);
  }
  if ((DAT_43e9bd4c & 0x20) == 0) {
    FUN_43560da8(0x11,0x20);
    FUN_43ae9148(auStack_e0,&LAB_43ae8d46_1);
    FUN_437d0c90(&DAT_43e993a4,auStack_e0,0x20);
  }
  if ((DAT_43e9bd4c & 0x200) == 0) {
    FUN_43560da8(0x11,0x200);
    uVar19 = FUN_4378dd84();
    FUN_43ae9148(auStack_f4,&LAB_43ae8d46_1);
    FUN_437b82d8(&DAT_43e993a4,uVar19,auStack_f4,0x200);
  }
  bVar42 = (DAT_43e9bd54 & 0x40) != 0;
  if (bVar42) {
    uVar39 = DAT_43e9920c[4];
  }
  else {
    uVar39 = DAT_43e9920c[4];
  }
  thunk_FUN_43721e60(!bVar42,uVar39 == 3);
  if (DAT_43e9bb5c == 0) {
    if ((DAT_43e9bd54 & 0x40) != 0) {
      FUN_43795bf0();
      goto LAB_437944b8;
    }
    FUN_43ae93ce();
    uVar18 = 0;
  }
  else {
    if (uVar3 == 0x103) {
      if (DAT_43e9b548 == 0x14a) {
        FUN_43ae93dc();
        FUN_4378f3f8(1);
        DAT_43e9bd30 = 1;
      }
      goto LAB_437944be;
    }
    if (uVar3 < 0x104) {
      if (uVar3 < 0x100) goto LAB_437944be;
      if (uVar3 < 0x102) {
        if (1 < (ushort)(DAT_43e9b548 - 0x105)) goto LAB_437944be;
        FUN_43795c14();
        uVar18 = 0;
        goto LAB_437944ba;
      }
    }
    else {
      if (uVar3 == 0x10e) {
        if ((((DAT_43e9b548 == 0x102) || (DAT_43e9b548 == 0x107)) || (DAT_43e9b548 == 0x11a)) ||
           (((DAT_43e9b548 == 0x11b || (DAT_43e9b548 == 0x118)) ||
            ((DAT_43e9b548 == 0x119 || (DAT_43e9b548 == 0x132)))))) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
        }
        goto LAB_437944be;
      }
      if (uVar3 < 0x10f) {
        if (uVar3 != 0x107) goto LAB_437944be;
      }
      else if (uVar3 != 0x132) {
        if ((uVar3 == 0x14a) && ((ushort)(DAT_43e9b548 - 0x102) < 2)) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
          DAT_43e9bd30 = 0;
        }
        goto LAB_437944be;
      }
    }
    if (DAT_43e9b548 != 0x10e) goto LAB_437944be;
    FUN_43ae93dc();
LAB_437944b8:
    uVar18 = 1;
  }
LAB_437944ba:
  FUN_4378f3f8(uVar18);
LAB_437944be:
  if ((*(char *)(iVar26 + 0x70) == '\0') && (iVar23 = FUN_437999e4(1,0xe), iVar23 != 0)) {
    FUN_43b71948();
  }
  if ((*DAT_43e9920c & 0xfffff) == 0) {
    FUN_43728be0();
  }
  FUN_4378f7a0(0xc39);
  if (*(char *)(iVar26 + 0xbf) != '\0') {
    FUN_43ae9124(auStack_108,DAT_4401f7cc);
    FUN_439018b0(&DAT_43e99380,auStack_108,2,0);
  }
  FUN_43560da8(0x1a,0x40);
  FUN_43ae129a(4);
  if (param_1 != *DAT_43e9920c) {
    iVar23 = thunk_FUN_436cd00c();
    uVar39 = iVar23 - DAT_43e9920c[2] >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca3acb,param_1,*DAT_43e9920c,uVar39);
    FUN_43902718(s_VD_Pre__overflow__dV__>__dV__dus_43ca3adf,param_1,*DAT_43e9920c,uVar39);
    FUN_4378f988(4,0,uVar39);
    if ((*(byte *)(iVar26 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Pre_E_OF_43ca3b00);
    }
    if ((*(byte *)(iVar26 + 0x1b) & 2) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(byte *)(iVar26 + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Pre_E_43ca3b0c);
  }
  return;
}


/* query "4379155c" */

void FUN_4379155c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uStack_44;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  uint uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Seq_S_43ca34b3);
  }
  if (param_1 == *DAT_43e9920c) {
    iVar2 = FUN_43560de0(0x1a,0x40,0,auStack_24,4);
    if (iVar2 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3507,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Sequence__VD_Pre_wait_timeout_43ca351b,*DAT_43e9920c,uStack_30);
    }
    FUN_43560dc4(0x1a,0xffffffbf);
    FUN_43ae1292(1);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = '\x01';
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43560dc4(0x1a,0xfffffeff);
    iVar2 = FUN_43b039fc(&DAT_43e99320,&DAT_43e994d0);
    if (iVar2 == 0) {
      uVar6 = 0;
    }
    else if (DAT_43e99338 == 0) {
      if (DAT_43f9a4b8 == '\0') {
        if (DAT_43e9bcd9 == '\0') {
          uVar6 = 0;
        }
        else {
          uVar6 = 0x43e99324;
        }
      }
      else {
        uVar6 = 0;
      }
    }
    else {
      uVar6 = 0;
    }
    puVar3 = (undefined1 *)FUN_4379ce18();
    thunk_FUN_43af2858(DAT_43e99230,puVar3);
    *puVar3 = 0;
    uVar4 = FUN_43ae8cd0(DAT_44025f5c);
    DAT_43e9bd58 = FUN_43796954(uVar4,uVar6,&DAT_43e99208);
    iVar2 = FUN_437999e4(1,0xd);
    if (((iVar2 != 0) && (DAT_43e9bb18 != 0)) && ((DAT_43e9bbb8 == 1 || (DAT_43e9920c[3] == 0)))) {
      uStack_44 = FUN_43ae9332(DAT_43e9bb30);
      uStack_40 = 0;
      uStack_3f = 0;
      iVar2 = FUN_43795610(DAT_43e9bcd9);
      if (((iVar2 != 0) && (DAT_43f9a4b8 == '\0')) && (DAT_43e9bce8 != '\0')) {
        uStack_3f = 1;
      }
      uStack_3c = (uint)(*(int *)(DAT_43e99208 + 0x548) != 0);
      uStack_38 = *(undefined4 *)(DAT_43e99208 + 0x54c);
      iVar2 = FUN_437956c8(&DAT_43e9bba4,&uStack_44);
      if (iVar2 != 0) {
        FUN_4378eb78(3,9,1,&DAT_43ca3309,iVar2);
        FUN_43902718(s__DFE_SetParam_Error_0x_x_43ca331d,iVar2);
      }
    }
    FUN_43900380();
    FUN_439cdbc8();
    uStack_28 = 0;
    uStack_2c = 0;
    FUN_43728c18(0,&uStack_28,&uStack_2c);
    FUN_43b6d334(uStack_28,uStack_2c);
    FUN_43560da8(0x1a,0x100);
    FUN_43ae129a(1);
    if ((param_1 != *DAT_43e9920c) && (iVar2 = FUN_43ae8d4e(), iVar2 != 0)) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca3546,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__overflow__dV__>__dV_43ca355a,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(4,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_E_OF_43ca3580);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43791528();
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Seq_E_43ca358c);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar2 = thunk_FUN_436cd00c();
      uVar5 = (uint)(iVar2 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca34bc,param_1,*DAT_43e9920c,uVar5);
      FUN_43902718(s_VD_Sequence__start_delayed__dV___43ca34d0,param_1,*DAT_43e9920c,uVar5);
      FUN_4378f988(3,1,uVar5);
      if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Seq_S_OF_43ca34fb);
      }
      if ((*(byte *)(iVar1 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* query "4379210c" */

void FUN_4379210c(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  byte bVar8;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [4];
  uint uStack_28;
  undefined1 auStack_24 [4];
  
  iVar2 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Post_S_43ca2f4b);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(4);
    iVar3 = FUN_43ae8d4e();
    if (iVar3 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_43728c70();
    FUN_4378f7a0(0xd35);
    DAT_43e9d394 = FUN_4377fdf8();
    FUN_43560e00(0x11,auStack_2c);
    iVar3 = FUN_4378e90c();
    if (iVar3 != 0) {
      uStack_28 = uStack_28 & 0xfffffffb | DAT_43e9bd4c & 4;
    }
    DAT_43e9bd4c = uStack_28;
    if (DAT_43f79b84 != 0) {
      DAT_43f79b82 = DAT_43f79b82 + 1;
      if (DAT_43f79b84 < DAT_43f79b82) {
        DAT_43f79b82 = 1;
        iVar3 = 0;
        do {
          *(undefined2 *)((int)&DAT_43f79b2e + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b48 + iVar3) = 0;
          *(undefined2 *)((int)&DAT_43f79b66 + iVar3) = 0;
          iVar3 = iVar3 + 2;
        } while (iVar3 != 0x1a);
      }
    }
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      if ((DAT_43e9bd4c & 4) == 0) {
        DAT_43e9d398 = FUN_437b4d64();
        FUN_43ae8e2c(&DAT_43e9b548,&DAT_43e99208);
        DAT_43f79b4c = 0;
      }
      else {
        DAT_43f79b6a = DAT_43f79b6a + 1;
        DAT_43f79b4c = DAT_43f79b4c + 1;
      }
    }
    if ((DAT_43e9bd4c & 8) == 0) {
      DAT_43e9d3a0 = FUN_4379fc20();
      FUN_43ae8e5c(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b4e = 0;
    }
    else {
      DAT_43f79b6c = DAT_43f79b6c + 1;
      DAT_43f79b4e = DAT_43f79b4e + 1;
    }
    if ((DAT_43e9bd4c & 0x20) == 0) {
      DAT_43e9d3a4 = FUN_437d0bc8();
      FUN_43ae8e74(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b52 = 0;
    }
    else {
      DAT_43f79b70 = DAT_43f79b70 + 1;
      DAT_43f79b52 = DAT_43f79b52 + 1;
    }
    if ((DAT_43e9bd4c & 0x40) == 0) {
      DAT_43e9d3a8 = FUN_437d9930();
      FUN_43ae8e84(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b54 = 0;
    }
    else {
      DAT_43f79b72 = DAT_43f79b72 + 1;
      DAT_43f79b54 = DAT_43f79b54 + 1;
    }
    if ((DAT_43e9bd4c & 0x80) == 0) {
      DAT_43e9d3ac = FUN_437b6614();
      FUN_43ae8e9a(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b56 = 0;
    }
    else {
      DAT_43f79b74 = DAT_43f79b74 + 1;
      DAT_43f79b56 = DAT_43f79b56 + 1;
    }
    if ((DAT_43e9bd4c & 0x200) == 0) {
      DAT_43e9d3b0 = FUN_437b8230();
      FUN_43ae8ea4(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b5a = 0;
    }
    else {
      DAT_43f79b78 = DAT_43f79b78 + 1;
      DAT_43f79b5a = DAT_43f79b5a + 1;
    }
    FUN_4378f7a0(0xd96);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda0);
      FUN_437b4e28(&DAT_43e99208);
      FUN_4378f7a0(0xda2);
    }
    FUN_437c1bb4(&DAT_43e99208);
    thunk_FUN_43b7c7da(&DAT_43e99208);
    FUN_437b0244(&DAT_43e99208,&DAT_43e9d022);
    iVar3 = FUN_4378e90c();
    if (iVar3 == 0) {
      FUN_4378f7a0(0xda9);
      FUN_43aef444(&DAT_43e99208,&DAT_43e9c7d8);
      FUN_4378f7a0(0xdad);
    }
    FUN_437c1b98(&DAT_43e99208,&DAT_43e9cc78);
    thunk_FUN_43b7c7dc(&DAT_43e99208,&DAT_43e9ce19);
    iVar3 = FUN_43560de0(0x1a,0x100,0,auStack_24,4);
    if (iVar3 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,&DAT_43ca3777,*DAT_43e9920c,uStack_30);
      FUN_43902718(s_VD_Post__VD_Sequence_wait_timeou_43ca378b,*DAT_43e9920c,uStack_30);
      FUN_43560da8(0x1a,0x100);
    }
    if (*(char *)(iVar2 + 0x70) == '\0') {
      iVar3 = FUN_437999e4(1,0xe);
      if (iVar3 != 0) {
        if ((DAT_43e9bb1f == '\0') || (DAT_43e9920c[3] != 0)) {
          FUN_439e21c0();
        }
        FUN_439e2184();
      }
      FUN_439fd76c();
    }
    FUN_4378f7a0(0xdd0);
    FUN_437967e8(&DAT_43e99208);
    FUN_4378f7a0(0xdd3);
    FUN_43ada220(auStack_48,&LAB_4378f410_1);
    FUN_439018b0(&DAT_43e99380,auStack_48,param_1,0);
    bVar8 = *(byte *)(iVar2 + 0x1f) & 8;
    if (((*(byte *)(iVar2 + 0x1f) & 8) == 0) &&
       (iVar4 = FUN_436e8328(), iVar3 = DAT_4401f1d0, iVar4 != 0)) {
      iVar4 = DAT_43e9920c[9];
      iVar5 = DAT_43e9920c[2];
      uVar1 = *(undefined2 *)(DAT_4401f1d0 + 0x2e);
      FUN_43ae863c(auStack_5c,bVar8);
      FUN_436ccd9c(6,iVar4 + iVar5,uVar1,auStack_5c);
      iVar5 = DAT_43e9920c[9];
      iVar6 = DAT_43e9920c[2];
      iVar4 = FUN_43ada230();
      uVar1 = *(undefined2 *)(iVar3 + 0x2c);
      FUN_43ae863c(auStack_70,bVar8);
      FUN_436ccd9c(7,iVar5 + iVar6 + iVar4 * 2,uVar1,auStack_70);
    }
    FUN_43ae129a(4);
    if (param_1 != *DAT_43e9920c) {
      iVar3 = thunk_FUN_436cd00c();
      uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
      FUN_4378eb78(3,9,1,&DAT_43ca37b7,param_1,*DAT_43e9920c,uVar7);
      FUN_43902718(s_VD_Post__overflow__dV__>__dV__du_43ca37cb,param_1,*DAT_43e9920c,uVar7);
      FUN_4378f988(4,2,uVar7);
      if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
        FUN_43561540(s_VD_Post_E_OF_43ca37ed);
      }
      if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43901480(0);
    if ((*(byte *)(iVar2 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Post_E_43ca2f58);
    }
  }
  else {
    iVar3 = thunk_FUN_436cd00c();
    uVar7 = (uint)(iVar3 - DAT_43e9920c[2]) >> 1;
    FUN_4378eb78(3,9,1,&DAT_43ca372f,param_1,*DAT_43e9920c,uVar7);
    FUN_43902718(s_VD_Post__start_delayed__dV__>__d_43ca3743,param_1,*DAT_43e9920c,uVar7);
    FUN_4378f988(3,2,uVar7);
    if ((*(byte *)(iVar2 + 0x12) & 4) != 0) {
      FUN_43561540(s_VD_Post_S_OF_43ca376a);
    }
    if ((*(byte *)(iVar2 + 0x1b) & 8) != 0) {
      FUN_4378ec60();
    }
  }
  return;
}


/* query "4378f410" */

void s32_candidate_4378f410(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_20 [4];
  undefined1 auStack_1c [8];
  
  iVar1 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
    FUN_43561540(s_VD_Drive_S_43ca2e3d);
  }
  iVar2 = FUN_43560de0(0x1a,0x80,0,auStack_20,5);
  if (iVar2 != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca2e48,*DAT_43e9920c);
    FUN_43902718(s_VD_Drive__wait_timeout__dV_43ca2e5c,*DAT_43e9920c);
  }
  if (param_1 == *DAT_43e9920c) {
    FUN_43ae1292(2);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_437fe7b4();
    if (DAT_43e9bcc8 == '\0') {
      DAT_43f79b80 = 0;
      DAT_4401d33c = 0xffff;
    }
    else {
      FUN_437876dc();
      iVar2 = FUN_43b00e5a();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 1;
      }
      iVar2 = thunk_FUN_436e8334();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 0x800;
      }
      iVar2 = FUN_43af0d5e(&DAT_43e99208);
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 2;
      }
      iVar2 = thunk_FUN_4384a184();
      if (iVar2 != 0) {
        DAT_43f79b80 = DAT_43f79b80 | 4;
      }
      if (DAT_4401d33c != DAT_43f79b80) {
        FUN_43901a8c(4,0x200d,0x807);
        DAT_4401d33c = DAT_43f79b80;
      }
    }
    if ((*(int *)(DAT_43e99208 + 0xb4) == 2) ||
       ((iVar2 = DAT_43e9bcc0, DAT_43e9bcc8 != '\0' && (DAT_43f79b80 != 0x807)))) {
      iVar2 = DAT_43e9920c[0xc];
    }
    FUN_4378dfdc(DAT_43e9bccc,iVar2);
    thunk_FUN_437d8f1c(&DAT_43e99208,&DAT_43e9ced8);
    thunk_FUN_437cf928(&DAT_43e99208,&DAT_43e9d018);
    if (((*(char *)(iVar1 + 0x70) == '\0') && (iVar2 = FUN_437999e4(1,0xe), iVar2 != 0)) &&
       ((DAT_43e9bb1f == '\0' || (DAT_43e9920c[3] != 0)))) {
      auStack_1c[0] = 1;
      FUN_439e3870(auStack_1c);
    }
    FUN_437968b0(&DAT_43e99208);
    if (*(char *)(iVar1 + 0xbf) == '\0') {
      FUN_43ae129a(2);
    }
    FUN_43901480(5);
    if (param_1 == *DAT_43e9920c) {
      iVar2 = FUN_43ae916c();
      if (iVar2 == 0) {
        FUN_4379ce0c();
        thunk_FUN_437b7fe4();
        FUN_4379ce24(&DAT_43e99208);
      }
    }
    else {
      iVar2 = FUN_43ae8d4e();
      if (iVar2 != 0) {
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_4378eb78(3,9,1,&DAT_43ca2eb3,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        iVar3 = *DAT_43e9920c;
        iVar2 = thunk_FUN_436cd00c();
        FUN_43902718(s_Imaging__VD_Drive__overflow__dV___43ca2ec7,param_1,iVar3,
                     (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
        if ((*(byte *)(iVar1 + 0x12) & 4) != 0) {
          FUN_43561540(s_VD_Drive_E_OF_43ca2ef3);
        }
      }
    }
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(s_VD_Drive_E_43ca2f01);
    }
  }
  else {
    iVar2 = FUN_43ae8d4e();
    if (iVar2 != 0) {
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_4378eb78(3,9,1,&DAT_43ca2e77,param_1,iVar3,(uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      iVar3 = *DAT_43e9920c;
      iVar2 = thunk_FUN_436cd00c();
      FUN_43902718(s_VD_Drive__start_delayed__dV__>___43ca2e8b,param_1,iVar3,
                   (uint)(iVar2 - DAT_43e9920c[2]) >> 1);
      if ((*(byte *)(iVar1 + 0x1b) & 0x10) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* query "4378f848" */

void s32_candidate_4378f848(int param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iStack_20;
  uint uStack_1c;
  undefined4 uStack_18;
  
  iVar1 = DAT_4402546c;
  if (DAT_43e992dc != param_1) {
    iStack_20 = param_1;
    uStack_1c = param_2;
    uStack_18 = param_3;
    if ((*(byte *)(DAT_4402546c + 0x12) & 1) != 0) {
      FUN_43561540(&DAT_43ca2f48);
    }
    FUN_43ae1292(4);
    iVar2 = FUN_43ae8d4e();
    if (iVar2 == 0) {
      FUN_43901778();
      if (DAT_4401e926 != '\0') {
        DAT_43f9a4b8 = 1;
      }
      DAT_4401e926 = '\0';
    }
    else {
      DAT_4401e926 = '\x01';
    }
    FUN_4378f7a0(0xe23);
    FUN_43560e00(0x11,&iStack_20);
    DAT_43e9bd4c = uStack_1c & 4 | DAT_43e9bd4c & 0xfffffffb;
    if ((uStack_1c & 4) == 0) {
      DAT_43e9d398 = FUN_437b4d64();
      FUN_43ae8e2c(&DAT_43e9b548,&DAT_43e99208);
      DAT_43f79b4c = 0;
    }
    else {
      DAT_43f79b6a = DAT_43f79b6a + 1;
      DAT_43f79b4c = DAT_43f79b4c + 1;
    }
    FUN_437b4e28(&DAT_43e99208);
    FUN_43aef444(&DAT_43e99208,&DAT_43e9c7d8);
    FUN_4378f7a0(0xe40);
    DAT_43e992dc = param_1;
    FUN_43ae129a(4);
    FUN_43901480(7);
    if ((*(byte *)(iVar1 + 0x12) & 1) != 0) {
      FUN_43561540(&DAT_43ca2f55);
    }
  }
  return;
}


/* query "43792750" */

void s32_candidate_43792750(void)

{
  int iVar1;
  undefined1 auStack_1c [20];
  
  FUN_43901638(7);
  if (DAT_43e992dc == *DAT_43e9920c) {
    iVar1 = DAT_43e99370 + DAT_43e9920c[2];
    FUN_43ae863c(auStack_1c,&LAB_4378ea10_1);
    FUN_436ccd9c(5,iVar1,1,auStack_1c);
    thunk_FUN_436e82ec();
  }
  else {
    FUN_4378eb78(3,9,1,&DAT_43ca37fa);
    FUN_43902718(s_int_LM_Send1st_Handler__EC_VD_Po_43ca380e);
  }
  return;
}


/* query "43791a7c" */

void FUN_43791a7c(int param_1)

{
  undefined1 *puVar1;
  char *pcVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int *piVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  undefined4 uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined1 uStack_d8;
  undefined1 auStack_d4 [20];
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  ushort uStack_2c;
  ushort uStack_2a;
  
  FUN_43795e7c();
  FUN_43796424();
  if (DAT_43f9a429 == '\0') {
    FUN_43ae863c(auStack_48,DAT_44025280);
    FUN_436ccee4(0x1e,1,auStack_48);
    FUN_43ae863c(auStack_5c,DAT_44023b9c);
    FUN_436ccee4(0x17,1,auStack_5c);
    DAT_43f9a429 = '\x01';
  }
  iVar13 = DAT_4402546c;
  if ((*(byte *)(DAT_4402546c + 0xc) & 1) != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca35b6);
    FUN_43902718(&DAT_43ca35ca);
  }
  thunk_FUN_4386116c();
  thunk_FUN_436e06f4();
  piVar6 = DAT_44022438;
  puVar3 = DAT_440216d4;
  if ((*(byte *)(iVar13 + 4) & 1) != 0) {
    iVar14 = *DAT_44022438;
    uVar12 = *DAT_440216d4;
    uVar7 = FUN_43795d2c();
    puVar5 = DAT_44022084;
    puVar4 = DAT_44021cf8;
    FUN_4378eb78(3,9,1,&DAT_43ca35cf,iVar14,uVar12,uVar7,*DAT_44022084,*DAT_44021cf8);
    iVar14 = *piVar6;
    uVar12 = *puVar3;
    uVar7 = FUN_43795d2c();
    FUN_43902718(s_CamV__10d__CamOutV__10d__Blank___43ca35e3,iVar14,uVar12,uVar7,*puVar5,*puVar4);
    *piVar6 = param_1;
    *puVar3 = 0;
    *puVar5 = 0;
    *puVar4 = 0;
  }
  FUN_43904008();
  FUN_43901638(0);
  FUN_43901638(4);
  FUN_43901638(8);
  FUN_43901638(5);
  pcVar2 = DAT_440223fc;
  iVar14 = DAT_4401f1d0;
  if (((*(byte *)(DAT_4401f1d0 + 0x29) & 0xf) != 0xf) && (*DAT_440223fc != '\0')) {
    FUN_43901638(9);
    *pcVar2 = '\0';
  }
  pcVar2 = DAT_44020c34;
  if (((*(byte *)(iVar14 + 0x29) & 0xf0) != 0xf0) && (*DAT_44020c34 != '\0')) {
    FUN_43901638(10);
    *pcVar2 = '\0';
  }
  FUN_43901768();
  FUN_43901748();
  FUN_43903f18();
  DAT_43e9d026 = DAT_43e9bb2c;
  FUN_4378e1a4(param_1,DAT_43e9bb2c,&DAT_43e9baa8);
  iVar8 = FUN_437fe4f4();
  DAT_43e9bb1f = iVar8 != 0;
  if (DAT_43ff36bc != 7) {
    FUN_4378eb78(3,9,1,&DAT_43ca3626,param_1,DAT_43ff36bc);
    FUN_43902718(s_HS_jump__d__d_8V_43ca363a,param_1,DAT_43ff36bc);
  }
  DAT_43e9d027 = 0;
  DAT_43e9d028 = 0;
  DAT_43ff36bc = 0;
  DAT_43e9b544 = 1;
  iVar15 = *DAT_43e9920c;
  iVar8 = FUN_4379a898();
  DAT_43e9bb1e = *(undefined1 *)(iVar8 + 0x5c);
  DAT_43e9bb1d = DAT_43e9bcd9;
  if (DAT_43e9bcd9 != '\0') {
    DAT_43e9bb1c = DAT_43e9bb1c + '\x01';
    DAT_43e9bb18 = DAT_43e9bb28;
    DAT_43e9bcd4 = DAT_43e9bb28;
    FUN_43ae8cd4(DAT_44025f5c);
  }
  if (DAT_43e9bcd4 != 0) {
    DAT_43e9bcd4 = DAT_43e9bcd4 + -1;
  }
  DAT_43e9bb25 = DAT_43e9bce8;
  if (DAT_43e9bce8 != '\0') {
    DAT_43e9bb24 = DAT_43e9bce0;
    DAT_43e9bb20 = DAT_43e9bcdc;
    DAT_43e9bce4 = DAT_43e9bcdc;
  }
  if (DAT_43e9bce4 != 0) {
    DAT_43e9bce4 = DAT_43e9bce4 + -1;
  }
  if ((DAT_43e9946c == DAT_43ff36c8) && (DAT_43f9a4bc < 5)) {
    DAT_43f9a4bc = DAT_43f9a4bc + 1;
    uVar11 = (uint)DAT_43f9a4bc;
    uVar10 = (uint)DAT_43f79b62;
    FUN_4378eb78(3,9,1,&DAT_43ca364b,uVar10,uVar11);
    FUN_43902718(s_TaskHS_is_stopping_after__dLINE___43ca365f,DAT_43f79b62,DAT_43f9a4bc);
    if (DAT_43f9a4bc == 1) {
      FUN_43901a8c(3,1,DAT_43f79b62,0);
    }
    if (DAT_43f9a4bc == 5) {
      FUN_4378eb78(3,9,1,&DAT_43ca3682,uVar10,uVar11);
      FUN_43902718(s_TaskHS_is_stopping_log_end_43ca3696);
    }
  }
  DAT_43ff36c8 = DAT_43e9946c;
  if (DAT_43e99460 != (code *)0x0) {
    uStack_f0 = DAT_43ff36bc;
    iVar8 = FUN_4378f9b4();
    uStack_ec = *(undefined4 *)(*(int *)(iVar8 + 8) + 0x1e8);
    iVar8 = FUN_4378f9b4();
    uStack_e8 = *(undefined4 *)(*(int *)(iVar8 + 8) + 0x3c);
    iVar8 = FUN_4378f9b4();
    uStack_dc = *(undefined4 *)(*(int *)(iVar8 + 4) + 0x18);
    iVar8 = FUN_4378f9b4();
    uStack_e0 = *(undefined4 *)(*(int *)(iVar8 + 0xc) + 0x5c);
    uStack_d8 = FUN_43ae1252();
    (*DAT_43e99460)(&uStack_f0);
  }
  FUN_43ada220(auStack_70,0x43792a0d);
  FUN_439018b0(&DAT_43e9b528,auStack_70,iVar15,0);
  FUN_43ada220(auStack_84,0x4378fef5);
  FUN_439018b0(&DAT_43e9b528,auStack_84,iVar15 << 8,0);
  iVar8 = DAT_43e9920c[0xb];
  FUN_43ae863c(auStack_98,0x437927c5);
  FUN_436ccd9c(1,param_1 + iVar8,1,auStack_98);
  if ((*(byte *)(iVar13 + 0x1f) & 1) == 0) {
    FUN_4378d818(param_1,DAT_43e9920c[9]);
  }
  if ((*(byte *)(iVar13 + 0x1f) & 2) == 0) {
    FUN_4378db0c(param_1,DAT_43e9920c[9]);
  }
  DAT_43f9a426 = 0;
  iVar8 = FUN_436e8328();
  if (iVar8 == 1) {
    FUN_43ae72f6(&uStack_34);
    DAT_43e9936c = (uint)uStack_30;
    DAT_43e99370 = (uint)uStack_2e;
    if ((DAT_43e9920c[5] != 1) &&
       (DAT_43e9936c = (uint)uStack_2c, DAT_43e99370 = (uint)uStack_2a, DAT_43e9920c[5] != 2)) {
      DAT_43e9936c = (uint)uStack_34;
      DAT_43e99370 = (uint)uStack_32;
    }
    uVar16 = DAT_43e9936c << 1;
    DAT_43e99370 = DAT_43e99370 << 1;
    DAT_43e9936c = uVar16;
    uVar9 = FUN_43ae8c60();
    uVar11 = DAT_43e99370;
    uVar10 = DAT_43e9936c;
    if (((uVar16 < uVar9) || (iVar8 = FUN_43ae8c60(), uVar11 < iVar8 + uVar10)) ||
       ((uint)DAT_43e9920c[9] < DAT_43e99370)) {
      FUN_4378eb78(3,9,1,&DAT_43ca36b1,DAT_43e9936c,DAT_43e99370,DAT_43e9920c[9]);
      FUN_43902718(s_LM__GetSendTiming_value_error_1s_43ca36c5,DAT_43e9936c,DAT_43e99370,
                   DAT_43e9920c[9]);
      DAT_43e9936c = 0;
      DAT_43e99370 = 0;
    }
    else if ((*(byte *)(iVar13 + 0x1f) & 4) == 0) {
      iVar13 = param_1 + DAT_43e9936c;
      FUN_43ae863c(auStack_ac,0x43792751);
      FUN_436ccd9c(5,iVar13,1,auStack_ac);
      DAT_43f9a426 = 1;
      iVar13 = FUN_4378e90c();
      if (iVar13 != 0) {
        uVar11 = (uint)*(byte *)(iVar14 + 0x28) * -200 + DAT_43e9936c;
        DAT_43e992b8 = uVar11;
        uVar10 = FUN_43ae8c60();
        if ((uVar11 < uVar10) || (DAT_43e9936c <= DAT_43e992b8)) {
          FUN_4378eb78(3,9,1,&DAT_43ca36f9,DAT_43e992b8,DAT_43e9920c[9]);
          FUN_43902718(s_EC_VD_Post_timing_error__d__vd___43ca370d,DAT_43e992b8,DAT_43e9920c[9]);
          DAT_43e992b8 = FUN_43ae8c60();
        }
        param_1 = param_1 + DAT_43e992b8;
        FUN_43ae863c(auStack_c0,&LAB_437926fc_1);
        puVar1 = &stack0x0000002c;
        goto LAB_43791fca;
      }
    }
  }
  else {
    DAT_43e9936c = 0;
    DAT_43e99370 = 0;
  }
  param_1 = FUN_4378e938();
  FUN_43ae863c(auStack_d4,&LAB_4379140c_1);
  puVar1 = &stack0x00000018;
LAB_43791fca:
  FUN_436ccd9c(0,param_1,1,puVar1 + -0xec);
  return;
}


/* query "437918ac" */

void s32_candidate_437918ac(int param_1)

{
  undefined *puVar1;
  undefined1 *puVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [20];
  undefined1 auStack_40 [20];
  undefined1 auStack_2c [24];
  
  puVar2 = auStack_90;
  iVar4 = DAT_43e9920c[1];
  if (iVar4 != *DAT_43e9920c) {
    DAT_43e99454 = DAT_43e99454 | 2;
  }
  if ((*(byte *)(DAT_4402546c + 0xc) & 4) != 0) {
    FUN_4378eb78(3,9,1,&DAT_43ca3595);
    FUN_43902718(s_DummyCamOutV_43ca35a9);
  }
  if (DAT_43e9bb18 == 0) {
    if (DAT_43e9baec == 1) {
      FUN_43560dc4(0x1a,0xffffff7f);
      iVar3 = DAT_43e9920c[10];
      FUN_43ae863c(auStack_54,&LAB_43ae8d3e_1);
      FUN_436ccd9c(4,param_1 + iVar3 * 2,1,auStack_54);
      FUN_43ada220(auStack_68,0x4379155d);
      puVar2 = auStack_68;
    }
    else {
      if (DAT_43e9baec == 2) {
        iVar3 = DAT_43e9920c[10];
        FUN_43ae863c(auStack_2c,&LAB_43791a10_1);
        FUN_436ccd9c(4,param_1 + iVar3,1,auStack_2c);
        FUN_43560da8(0x1a,0x80);
        FUN_43ada220(auStack_40,&LAB_43790b68_1);
        puVar2 = auStack_40;
        iVar4 = iVar4 << 8;
        puVar1 = &DAT_43e9b528;
        goto LAB_437919bc;
      }
      FUN_43560da8(0x1a,0x80);
      FUN_43ada220(auStack_7c,0x4379155d);
      puVar2 = auStack_7c;
    }
    puVar1 = &DAT_43e992fc;
  }
  else {
    FUN_43560da8(0x1a,0x80);
    FUN_43ada220(auStack_90,0x4379155d);
    puVar1 = &DAT_43e992fc;
  }
LAB_437919bc:
  FUN_439018b0(puVar1,puVar2,iVar4,0);
  return;
}


/* query "43791454" */

void s32_candidate_43791454(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_43560dc4(0x11,~param_1,param_3,param_4,param_1);
  iVar1 = FUN_4378e90c();
  if (iVar1 != 0) {
    FUN_43ada220(&uStack_1c,0x4378f849);
    FUN_439018b0(&DAT_43e9b528,&uStack_1c,*DAT_43e9920c,0);
  }
  return;
}


/* query "437926fc" */

void s32_candidate_437926fc(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined1 auStack_38 [20];
  undefined1 auStack_24 [24];
  
  uVar2 = *DAT_43e9920c;
  uVar1 = FUN_4378e938();
  FUN_43ae863c(auStack_24,&LAB_4379140c_1);
  FUN_436ccd9c(0,uVar1,1,auStack_24);
  FUN_43ada220(auStack_38,0x4378f849);
  FUN_439018b0(&DAT_43e9b528,auStack_38,uVar2,0);
  return;
}


/* query "43796954" */

undefined2 FUN_43796954(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  int iVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  char cVar8;
  undefined2 *puVar9;
  byte bVar10;
  bool bVar11;
  undefined1 auStack_3c [24];
  
  uVar4 = FUN_43799f3c();
  if ((*(short *)*param_3 == 0x138) || (*(short *)*param_3 == 0x144)) {
    iVar5 = FUN_43799f88(uVar4,1);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,1);
    }
    iVar5 = FUN_43799f88(uVar4,0);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,0);
    }
    iVar5 = FUN_43799f88(uVar4,4);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,4);
    }
    iVar5 = FUN_43799f88(uVar4,5);
    if (iVar5 == 0) {
      FUN_4379a140(uVar4,5);
    }
  }
  if (((*(byte *)(param_3[2] + 0x268) & 2) == 0) || (iVar5 = FUN_43ae916c(), iVar5 != 0)) {
    bVar11 = false;
  }
  else {
    bVar11 = true;
  }
  iVar5 = param_3[2];
  bVar1 = *(byte *)(iVar5 + 0x268);
  bVar10 = bVar1 & 2;
  if ((bVar1 & 2) != 0) {
    if ((*(ushort *)(iVar5 + 0x264) & 0x1c0) == 0) {
      bVar10 = *(int *)(iVar5 + 0x1c) == 4;
    }
    else {
      bVar10 = 0;
    }
  }
  if (((bVar1 & 4) == 0) || (iVar5 = FUN_43ae916c(), iVar5 != 0)) {
    iVar5 = 0;
  }
  else {
    iVar5 = 1;
  }
  iVar2 = DAT_4402546c;
  if (((*(char *)(DAT_4402546c + 0x4a) != '\0') && (*(int *)(*param_3 + 0xb8) == 1)) &&
     (*(int *)(*param_3 + 0xb4) - 1U < 2)) {
    if (bVar11 != false) {
      bVar11 = (*(byte *)(param_3[2] + 0x220) & 3) == 2;
    }
    if ((iVar5 != 0) && ((*(byte *)(param_3[2] + 0x220) & 5) != 4)) {
      iVar5 = 0;
    }
  }
  iVar6 = FUN_437286bc();
  bVar1 = *(byte *)(iVar2 + 10);
  if (iVar6 == 0) {
    bVar11 = false;
  }
  if ((bVar1 & 1) == 0) {
    if ((bVar1 & 2) != 0) {
      bVar11 = true;
    }
  }
  else {
    bVar11 = false;
  }
  if ((bVar1 & 4) == 0) {
    if ((bVar1 & 8) != 0) {
      bVar10 = 1;
    }
  }
  else {
    bVar10 = 0;
  }
  if ((bVar1 & 0xf0) == 0x10) {
    iVar5 = 0;
  }
  else if ((bVar1 & 0xf0) == 0x20) {
    iVar5 = 1;
  }
  iVar6 = FUN_43ae916c();
  if (iVar6 == 0) {
    FUN_4379bb68(0,bVar11);
    FUN_4379bb68(1,iVar5);
    FUN_4379bb68(2,iVar5);
    FUN_4379bb68(3,bVar10);
  }
  if (param_1 == 0) {
    iVar5 = FUN_437999e4(1,1);
    if (((iVar5 != 0) || (iVar5 = FUN_437999e4(1,2), iVar5 != 0)) &&
       ((iVar5 = FUN_43ae8c4a(DAT_43e9d744 + 1), iVar5 == *(int *)param_3[1] &&
        (((DAT_43e9d768 != iVar5 && (iVar5 = FUN_43794a44(param_3), iVar5 == 0)) &&
         (*(int *)(param_3[2] + 0xd8) != 1)))))) {
      FUN_437961d8(3,9,1,&DAT_43ca3e70,*(undefined4 *)param_3[1],((undefined4 *)param_3[1])[2],
                   DAT_43e9d768,DAT_43e9d740);
      FUN_43902718(s_Lost_CAMOUT_V_now_vfc__d_frc__d__43ca3e84,*(undefined4 *)param_3[1],
                   ((undefined4 *)param_3[1])[2],DAT_43e9d768,DAT_43e9d740);
      FUN_437964d4();
    }
  }
  else if ((*(byte *)(param_3[2] + 0x268) & 8) == 0) {
    FUN_43b04914(&DAT_43e9de14);
  }
  if (*(int *)(param_3[2] + 0x2c) != 0) {
    FUN_43796284(param_3 + 2,param_1);
  }
  iVar5 = FUN_43798414();
  if (((iVar5 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar5 = FUN_437999e4(1,5), iVar5 != 0)) {
    FUN_43b0417e(1,0xffffffff,0,0);
    FUN_43b0417e(2,0xffffffff,0,0);
    FUN_437961d8(3,9,1,&DAT_43ca3ebd);
    FUN_43902718(s_RCV_overflow_VD_Seq_Refresh__43ca3ed1);
  }
  iVar5 = FUN_43798434();
  if (((iVar5 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar5 = FUN_437999e4(1,0xb), iVar5 != 0)) {
    FUN_43b0419c(0,0);
    FUN_437961d8(3,9,1,&DAT_43ca3eee);
    FUN_43902718(s_SDVGA_SRC_overflow_VD_Seq_Refres_43ca3f02);
  }
  if (param_2 != 0) {
    if (*(int *)(param_3[2] + 0x44) != 0x11) {
      FUN_43ae9786(auStack_3c,DAT_44022a88);
      FUN_43796910(0,auStack_3c,param_3[2] + 0xb8);
      FUN_43795b10();
    }
    uVar7 = FUN_4380d708(param_2 + 0x18,param_2 + 0x2c,0);
    iVar5 = FUN_4381bd4c(param_2,uVar7,(uint)*(byte *)(param_3[2] + 0x30) << 8);
    if (iVar5 != 0) {
      FUN_43b04730();
    }
  }
  FUN_4381bf38(&DAT_43e9de14);
  FUN_43797410();
  iVar5 = FUN_4379742c();
  if (iVar5 != 0) {
    FUN_4372a540(7);
  }
  iVar5 = FUN_43ae916c();
  if (iVar5 == 0) {
    FUN_4379bb90(param_3);
  }
  puVar9 = (undefined2 *)*param_3;
  uVar3 = *puVar9;
  switch(uVar3) {
  case 0x100:
  case 0x101:
  case 0x10e:
  case 0x110:
  case 0x14a:
    goto switchD_43796ca8_caseD_100;
  default:
    if ((*(char *)(param_3[2] + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) {
      return uVar3;
    }
    break;
  case 0x104:
  case 0x141:
    iVar5 = FUN_437284b4();
    goto LAB_43796f38;
  case 0x105:
  case 0x106:
    if (((*(char *)(param_3[2] + 0x1ed) != '\0') &&
        (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) &&
       ((iVar5 = FUN_43ae916c(), iVar5 == 0 || (iVar5 = FUN_43795b04(), iVar5 != 0)))) {
      puVar9 = (undefined2 *)*param_3;
      if ((*(int *)(puVar9 + 0x5a) == 2) &&
         (iVar5 = param_3[2], (ushort)(*(short *)(iVar5 + 0x224) - 0x100U) < 2)) goto LAB_43796ea8;
      goto LAB_43796fc0;
    }
    break;
  case 0x10d:
  case 0x132:
    iVar5 = FUN_437fe4f4();
    if ((iVar5 == 0) && (*(char *)(param_3[2] + 0x1ed) != '\0')) {
      bVar11 = *(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4);
      goto LAB_43796fbc;
    }
    break;
  case 0x10f:
    if (*(int *)(puVar9 + 0x5a) != 2) {
      if (*(int *)(param_3[1] + 0x40) == 2) {
        return 0x10f;
      }
      break;
    }
    iVar5 = param_3[2];
    if (*(char *)(iVar5 + 0x23c) != '\0') {
      return 0x10f;
    }
    goto LAB_43796fda;
  case 0x112:
    iVar5 = FUN_437fe50c();
    goto LAB_43796f38;
  case 0x121:
    iVar5 = FUN_4379ada0();
    bVar11 = iVar5 == 7;
    goto LAB_43796fbc;
  case 0x123:
  case 0x128:
    iVar5 = FUN_4379ad7c();
    if (iVar5 == 0) {
LAB_43796dae:
      FUN_4379a898();
      iVar5 = FUN_43ae9674();
      if (iVar5 == 0) {
        iVar5 = FUN_4379a898();
        iVar5 = FUN_43ae9674(iVar5 + 0x28);
        goto LAB_43796f38;
      }
    }
    break;
  case 0x124:
    iVar5 = FUN_4379ada0();
    bVar11 = iVar5 == 5;
LAB_43796fbc:
    if (!bVar11) break;
    goto LAB_43796fbe;
  case 0x125:
    iVar5 = FUN_4379ad7c();
    if ((iVar5 != 0) && (iVar5 = FUN_4379ad88(), iVar5 == 1)) goto LAB_43796dae;
    break;
  case 0x126:
    iVar5 = FUN_4379ad7c();
    if ((iVar5 != 0) && (iVar5 = FUN_4379ad88(), iVar5 == 1)) {
      FUN_4379a898();
      iVar5 = FUN_43ae9674();
      if (iVar5 == 0) {
        iVar5 = FUN_4379a898();
        iVar5 = FUN_43ae9674(iVar5 + 0x28);
        if (iVar5 == 0) {
          iVar5 = FUN_4379a320();
          cVar8 = *(char *)(iVar5 + 0xac0);
          goto LAB_43796f7c;
        }
      }
    }
    break;
  case 0x129:
    if ((*(char *)(param_3[2] + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) {
      return 0x129;
    }
    break;
  case 0x12a:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab2);
    goto LAB_43796f7c;
  case 299:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab3);
    goto LAB_43796f7c;
  case 300:
    iVar5 = FUN_4379a320();
    cVar8 = *(char *)(iVar5 + 0xab4);
LAB_43796f7c:
    if (cVar8 == '\0') break;
    goto LAB_43796fbe;
  case 0x138:
  case 0x144:
    iVar5 = FUN_43799f88(uVar4,1);
    if (((iVar5 != 0) && (iVar5 = FUN_43799f88(uVar4,0), iVar5 != 0)) &&
       (iVar5 = FUN_43799f88(uVar4,4), iVar5 != 0)) {
      iVar5 = FUN_43799f88(uVar4,5);
      goto LAB_43796fa0;
    }
    break;
  case 0x139:
  case 0x145:
    if (*(char *)(param_3[2] + 0x1ed) != '\0') {
      if (1 < *(int *)(param_3[1] + 0x10) - 2U) {
        return uVar3;
      }
      if (*(int *)(param_3[1] + 0xc) == 1) {
        return uVar3;
      }
      if (1 < *(uint *)(param_3[2] + 0x3c)) {
        return uVar3;
      }
    }
    break;
  case 0x13a:
  case 0x146:
    iVar5 = FUN_43799f88(uVar4,4);
    goto LAB_43796f38;
  case 0x13b:
  case 0x13f:
switchD_43796ca8_caseD_13b:
    iVar5 = FUN_437dfeb4(uVar3);
LAB_43796fa0:
    if (iVar5 == 0) break;
    goto LAB_43796fbe;
  case 0x13c:
    if (*(char *)(param_3[0x15] + 9) == '\x01') {
      return 0x13c;
    }
    break;
  case 0x13d:
    if ((((*(char *)param_3[5] != '\0') || (*(int *)((char *)param_3[5] + 4) == 0)) ||
        (*(int *)(param_3[2] + 0x248) != 0)) || (*(char *)(iVar2 + 0xec) != '\0')) {
      uVar3 = 0x13d;
      goto switchD_43796ca8_caseD_13b;
    }
    break;
  case 0x13e:
    iVar5 = FUN_437dfa2c();
LAB_43796f38:
    if (iVar5 == 0) {
LAB_43796fbe:
      puVar9 = (undefined2 *)*param_3;
LAB_43796fc0:
      return *puVar9;
    }
    break;
  case 0x142:
    iVar5 = param_3[2];
    if ((*(char *)(iVar5 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar5 + 0x1d4))) {
      if ((*(char *)(iVar2 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar5 + 0x220) & 3) == 2)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x142;
        }
        if (*(short *)(iVar5 + 0x240) == 0x142) {
          return 0x142;
        }
      }
LAB_43796ea8:
      return *(undefined2 *)(iVar5 + 0x26c);
    }
    break;
  case 0x143:
    iVar5 = param_3[2];
    if ((*(char *)(iVar5 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar5 + 0x1d4))) {
      if ((*(char *)(iVar2 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar5 + 0x220) & 5) == 4)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x143;
        }
        if (*(short *)(iVar5 + 0x240) == 0x143) {
          return 0x143;
        }
      }
      goto LAB_43796ea8;
    }
  }
  iVar5 = param_3[2];
LAB_43796fda:
  uVar3 = *(undefined2 *)(iVar5 + 0x26c);
switchD_43796ca8_caseD_100:
  return uVar3;
}


/* query "4381bf38" */

void FUN_4381bf38(int param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iVar3 = param_1 + 4;
  iStack_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  FUN_43560d38(0x1b,0xffffffff);
  uStack_1c = FUN_43afc5b6(iVar3);
  iStack_20 = FUN_43afc5a8(iVar3);
  FUN_43b04990(&uStack_1c,&iStack_20,0x43b048b3);
  FUN_43560d1c(0x1b);
  uVar1 = FUN_43afbfc2(iVar3);
  for (uVar4 = 0; uVar4 < uVar1; uVar4 = uVar4 + 1) {
    FUN_43560d38(0x1b,0xffffffff);
    uVar2 = FUN_43afc5c6(iVar3);
    FUN_43560d1c(0x1b);
    FUN_43b047d0(uVar2);
  }
  return;
}


/* query "436bdbfc" */

undefined4 FUN_436bdbfc(int param_1,undefined4 param_2,undefined2 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_30 [2];
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined1 auStack_28 [12];
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 == 1) {
    iVar2 = FUN_436bd274(0,iVar1);
    if (iVar2 == param_1) {
      FUN_436bd288(param_2,iVar1);
      iVar2 = iVar1 * 0xac;
      FUN_436bfa88(*(undefined4 *)(&DAT_43e78a9c + iVar2),iVar1);
      FUN_436bfab0(*(undefined4 *)(&DAT_43e78aa0 + iVar2),iVar1);
      FUN_436bfad8(*(undefined4 *)(&DAT_43e78aa4 + iVar2),iVar1);
      FUN_436bfb00(*(undefined4 *)(&DAT_43e78aa8 + iVar2),iVar1);
      FUN_436bfb28(*(undefined4 *)(&DAT_43e78aac + iVar2),iVar1);
      FUN_436bfb50(*(undefined4 *)(&DAT_43e78ab0 + iVar2),iVar1);
      FUN_436bfb78(*(undefined4 *)(&DAT_43e78ab4 + iVar2),iVar1);
      FUN_436bfba0(*(undefined4 *)(&DAT_43e78ab8 + iVar2),iVar1);
      FUN_436bfbc8(*(undefined4 *)(&DAT_43e78abc + iVar2),iVar1);
      FUN_436bfbf0(*(undefined4 *)(&DAT_43e78ac0 + iVar2),iVar1);
      FUN_436bfc18(*(undefined4 *)(&DAT_43e78ac4 + iVar2),iVar1);
      FUN_436bfc40(*(undefined4 *)(&DAT_43e78ac8 + iVar2),iVar1);
      FUN_436bfc68(*(undefined4 *)(&DAT_43e78acc + iVar2),iVar1);
      FUN_436bfc90(*(undefined4 *)(&DAT_43e78ad0 + iVar2),iVar1);
      FUN_436bfcb8(*(undefined4 *)(&DAT_43e78ad4 + iVar2),iVar1);
      FUN_436bfce0(*(undefined4 *)(&DAT_43e78ad8 + iVar2),iVar1);
      FUN_436bfd08(*(undefined4 *)(&DAT_43e78adc + iVar2),iVar1);
      FUN_436bfd30(*(undefined4 *)(&DAT_43e78ae0 + iVar2),iVar1);
      FUN_436bfd58(*(undefined4 *)(&DAT_43e78ae4 + iVar2),iVar1);
      FUN_436bfd80(*(undefined4 *)(&DAT_43e78ae8 + iVar2),iVar1);
      FUN_436bfda8(*(undefined4 *)(&DAT_43e78aec + iVar2),iVar1);
      FUN_436bfdd4(*(undefined4 *)(&DAT_43e78af0 + iVar2),iVar1);
      FUN_436bfe00(*(undefined4 *)(&DAT_43e78af4 + iVar2),iVar1);
      FUN_436bfe2c(*(undefined4 *)(&DAT_43e78af8 + iVar2),iVar1);
      FUN_436bfe58(*(undefined4 *)(&DAT_43e78afc + iVar2),iVar1);
      FUN_436bfe84(*(undefined4 *)(&DAT_43e78b00 + iVar2),iVar1);
      FUN_436bfeb0(*(undefined4 *)(&DAT_43e78b04 + iVar2),iVar1);
      FUN_436bfedc(*(undefined4 *)(&DAT_43e78b08 + iVar2),iVar1);
      FUN_436bff08(*(undefined4 *)(&DAT_43e78b0c + iVar2),iVar1);
      FUN_436bff34(*(undefined4 *)(&DAT_43e78b10 + iVar2),iVar1);
      FUN_436bff60(*(undefined4 *)(&DAT_43e78b14 + iVar2),iVar1);
      FUN_436bff8c(*(undefined4 *)(&DAT_43e78b18 + iVar2),iVar1);
      iVar4 = iVar1 * 0x38;
      FUN_436bffb8(*(undefined4 *)(&DAT_43e78b1c + iVar2),iVar1);
      FUN_436bffe4(*(undefined4 *)(&DAT_43e78b20 + iVar2),iVar1);
      FUN_436c0010(*(undefined4 *)(&DAT_43e78b24 + iVar2),iVar1);
      FUN_436c003c(*(undefined4 *)(&DAT_43e78b28 + iVar2),iVar1);
      FUN_436c0068(*(undefined4 *)(&DAT_43e78b2c + iVar2),iVar1);
      FUN_436c0094(*(undefined4 *)(&DAT_43e78b30 + iVar2),iVar1);
      FUN_436c00c0(*(undefined4 *)(&DAT_43e78b34 + iVar2),iVar1);
      FUN_436c00ec(*(undefined4 *)(&DAT_43e78b38 + iVar2),iVar1);
      FUN_436c0118(*(undefined4 *)(&DAT_43e78b3c + iVar2),iVar1);
      FUN_436c0144(*(undefined4 *)(&DAT_43e78b40 + iVar2),iVar1);
      FUN_436c0170(*(undefined4 *)(&DAT_43e78b44 + iVar2),iVar1);
      iVar6 = iVar1 * 0x1a4;
      uVar3 = *(undefined4 *)(&DAT_43e77b7c + iVar4);
      param_3[1] = *(undefined2 *)(&DAT_43e78ab0 + iVar2);
      FUN_436c028c(uVar3,iVar1);
      FUN_436c02b4(0,iVar1);
      FUN_436c02dc(0x29c00,iVar1);
      FUN_436c0304(*(undefined4 *)(&DAT_43e77b88 + iVar4),iVar1);
      FUN_436c032c(*(undefined4 *)(&DAT_43e77b8c + iVar4),iVar1);
      FUN_436c0354(*(undefined4 *)(&DAT_43e77b90 + iVar4),iVar1);
      FUN_436c037c(0,iVar1);
      FUN_436c03a4(*(undefined4 *)(&DAT_43e77b98 + iVar4),iVar1);
      FUN_436c03cc(*(undefined4 *)(&DAT_43e77b9c + iVar4),iVar1);
      FUN_436c03f4(0,iVar1);
      FUN_436c041c(*(undefined4 *)(&DAT_43e77ba0 + iVar4),iVar1);
      FUN_436c0444(0,iVar1);
      FUN_436c046c(0,iVar1);
      FUN_436c0494(0,iVar1);
      FUN_436c04bc(0,iVar1);
      FUN_436c04e4(*(undefined4 *)(&DAT_43e77ba4 + iVar4),iVar1);
      FUN_436c050c(*(undefined4 *)(&DAT_43e77ba8 + iVar4),iVar1);
      FUN_436c06d0(0,iVar1);
      FUN_436c06fc(*(undefined4 *)(&DAT_43e77bac + iVar4),iVar1);
      FUN_436c0780(*(undefined4 *)(&DAT_43e77bb0 + iVar4),iVar1);
      iVar2 = iVar1 * 0x34;
      FUN_436c0534(*(undefined4 *)(&DAT_43e77c64 + iVar2),iVar1);
      FUN_436c055c(*(undefined4 *)(&DAT_43e77c68 + iVar2),iVar1);
      FUN_436c0584(*(undefined4 *)(&DAT_43e77c6c + iVar2),iVar1);
      FUN_436c05ac(*(undefined4 *)(&DAT_43e77c70 + iVar2),iVar1);
      FUN_436c05d4(*(undefined4 *)(&DAT_43e77c74 + iVar2),iVar1);
      FUN_436c05fc(*(undefined4 *)(&DAT_43e77c78 + iVar2),iVar1);
      FUN_436c0624(*(undefined4 *)(&DAT_43e77c7c + iVar2),iVar1);
      FUN_436c064c(*(undefined4 *)(&DAT_43e77c80 + iVar2),iVar1);
      FUN_436c0678(*(undefined4 *)(&DAT_43e77c84 + iVar2),iVar1);
      FUN_436c06a4(*(undefined4 *)(&DAT_43e77c88 + iVar2),iVar1);
      FUN_436c0728(*(undefined4 *)(&DAT_43e77c8c + iVar2),iVar1);
      FUN_436c0754(*(undefined4 *)(&DAT_43e77c90 + iVar2),iVar1);
      FUN_436c07ac(*(undefined4 *)(&DAT_43e77c94 + iVar2),iVar1);
      iVar2 = iVar1 * 0x9c;
      FUN_436c07d8(*(undefined4 *)(&DAT_43e783b4 + iVar2),iVar1);
      FUN_436c0800(*(undefined4 *)(&DAT_43e783b8 + iVar2),iVar1);
      FUN_436c0828(*(undefined4 *)(&DAT_43e783bc + iVar2),iVar1);
      FUN_436c0850(*(undefined4 *)(&DAT_43e783c0 + iVar2),iVar1);
      FUN_436c0878(*(undefined4 *)(&DAT_43e783c4 + iVar2),iVar1);
      FUN_436c08a0(*(undefined4 *)(&DAT_43e783c8 + iVar2),iVar1);
      FUN_436c08c8(*(undefined4 *)(&DAT_43e783cc + iVar2),iVar1);
      FUN_436c08f0(*(undefined4 *)(&DAT_43e783d0 + iVar2),iVar1);
      FUN_436c0918(*(undefined4 *)(&DAT_43e783d4 + iVar2),iVar1);
      FUN_436c0940(*(undefined4 *)(&DAT_43e783d8 + iVar2),iVar1);
      FUN_436c0968(*(undefined4 *)(&DAT_43e783dc + iVar2),iVar1);
      FUN_436c0990(*(undefined4 *)(&DAT_43e783e0 + iVar2),iVar1);
      FUN_436c09b8(*(undefined4 *)(&DAT_43e783e4 + iVar2),iVar1);
      FUN_436c09e0(*(undefined4 *)(&DAT_43e783e8 + iVar2),iVar1);
      FUN_436c0a08(*(undefined4 *)(&DAT_43e783ec + iVar2),iVar1);
      FUN_436c0a30(*(undefined4 *)(&DAT_43e783f0 + iVar2),iVar1);
      FUN_436c0a58(*(undefined4 *)(&DAT_43e783f4 + iVar2),iVar1);
      FUN_436c0a80(*(undefined4 *)(&DAT_43e783f8 + iVar2),iVar1);
      FUN_436c0aa8(*(undefined4 *)(&DAT_43e783fc + iVar2),iVar1);
      FUN_436c0ad0(*(undefined4 *)(&DAT_43e78400 + iVar2),iVar1);
      FUN_436c0af8(*(undefined4 *)(&DAT_43e78404 + iVar2),iVar1);
      FUN_436c0b20(*(undefined4 *)(&DAT_43e78408 + iVar2),iVar1);
      FUN_436c0b48(*(undefined4 *)(&DAT_43e7840c + iVar2),iVar1);
      FUN_436c0b70(*(undefined4 *)(&DAT_43e78410 + iVar2),iVar1);
      FUN_436c0b98(*(undefined4 *)(&DAT_43e78414 + iVar2),iVar1);
      FUN_436c0e00(*(undefined4 *)(&DAT_43e78418 + iVar2),iVar1);
      FUN_436c0e2c(*(undefined4 *)(&DAT_43e7841c + iVar2),iVar1);
      FUN_436c0e58(*(undefined4 *)(&DAT_43e78420 + iVar2),iVar1);
      FUN_436c0e84(*(undefined4 *)(&DAT_43e78424 + iVar2),iVar1);
      FUN_436c0eb0(*(undefined4 *)(&DAT_43e78428 + iVar2),iVar1);
      FUN_436c0edc(*(undefined4 *)(&DAT_43e7842c + iVar2),iVar1);
      FUN_436c0f08(*(undefined4 *)(&DAT_43e78430 + iVar2),iVar1);
      FUN_436c0f34(*(undefined4 *)(&DAT_43e78434 + iVar2),iVar1);
      FUN_436c0f60(*(undefined4 *)(&DAT_43e78438 + iVar2),iVar1);
      FUN_436c0f8c(*(undefined4 *)(&DAT_43e7843c + iVar2),iVar1);
      FUN_436c0fb8(*(undefined4 *)(&DAT_43e78440 + iVar2),iVar1);
      FUN_436c0fe4(*(undefined4 *)(&DAT_43e78444 + iVar2),iVar1);
      FUN_436c1010(*(undefined4 *)(&DAT_43e78448 + iVar2),iVar1);
      FUN_436c103c(*(undefined4 *)(&DAT_43e7844c + iVar2),iVar1);
      iVar2 = iVar1 * 0x14;
      FUN_436c14c8(iVar2 + 0x43f9236b,iVar1);
      FUN_436c1510(iVar2 + 0x43f9231b,iVar1);
      FUN_436c155c(iVar2 + 0x43f92343,iVar1);
      FUN_436c15a8(iVar2 + 0x43f922c7,iVar1);
      FUN_436c15f0(iVar2 + 0x43f922f1,iVar1);
      FUN_436c163c(iVar2 + 0x43f9229e,iVar1);
      FUN_436c1750(*(undefined4 *)(&DAT_43e78754 + iVar6),iVar1);
      FUN_436c1778(*(undefined4 *)(&DAT_43e78758 + iVar6),iVar1);
      FUN_436c17a0(*(undefined4 *)(&DAT_43e7875c + iVar6),iVar1);
      FUN_436c17c8(*(undefined4 *)(&DAT_43e78760 + iVar6),iVar1);
      FUN_436c17f0(*(undefined4 *)(&DAT_43e78764 + iVar6),iVar1);
      FUN_436c1818(*(undefined4 *)(&DAT_43e78768 + iVar6),iVar1);
      FUN_436c1840(*(undefined4 *)(&DAT_43e7876c + iVar6),iVar1);
      FUN_436c1868(*(undefined4 *)(&DAT_43e78770 + iVar6),iVar1);
      FUN_436c1890(*(undefined4 *)(&DAT_43e78774 + iVar6),iVar1);
      FUN_436c18b8(*(undefined4 *)(&DAT_43e78778 + iVar6),iVar1);
      FUN_436c18e0(*(undefined4 *)(&DAT_43e7877c + iVar6),iVar1);
      FUN_436c1908(*(undefined4 *)(&DAT_43e78780 + iVar6),iVar1);
      FUN_436c1930(*(undefined4 *)(&DAT_43e78784 + iVar6),iVar1);
      FUN_436c1958(*(undefined4 *)(&DAT_43e78788 + iVar6),iVar1);
      FUN_436c1980(*(undefined4 *)(&DAT_43e7878c + iVar6),iVar1);
      FUN_436c19a8(*(undefined4 *)(&DAT_43e78790 + iVar6),iVar1);
      FUN_436c19d0(*(undefined4 *)(&DAT_43e78794 + iVar6),iVar1);
      FUN_436c19f8(*(undefined4 *)(&DAT_43e78798 + iVar6),iVar1);
      FUN_436c1a20(*(undefined4 *)(&DAT_43e7879c + iVar6),iVar1);
      FUN_436c1a4c(*(undefined4 *)(&DAT_43e787a0 + iVar6),iVar1);
      FUN_436c1a78(*(undefined4 *)(&DAT_43e787a4 + iVar6),iVar1);
      FUN_436c1aa4(*(undefined4 *)(&DAT_43e787a8 + iVar6),iVar1);
      FUN_436c1ad0(*(undefined4 *)(&DAT_43e787ac + iVar6),iVar1);
      FUN_436c1afc(*(undefined4 *)(&DAT_43e787b0 + iVar6),iVar1);
      FUN_436c1b28(*(undefined4 *)(&DAT_43e787b4 + iVar6),iVar1);
      FUN_436c1b54(*(undefined4 *)(&DAT_43e787b8 + iVar6),iVar1);
      FUN_436c1b80(*(undefined4 *)(&DAT_43e787bc + iVar6),iVar1);
      FUN_436c1bac(*(undefined4 *)(&DAT_43e787c0 + iVar6),iVar1);
      FUN_436c1bd8(*(undefined4 *)(&DAT_43e787c4 + iVar6),iVar1);
      FUN_436c1c04(*(undefined4 *)(&DAT_43e787c8 + iVar6),iVar1);
      FUN_436c1c30(*(undefined4 *)(&DAT_43e787cc + iVar6),iVar1);
      FUN_436c1c5c(*(undefined4 *)(&DAT_43e787d0 + iVar6),iVar1);
      FUN_436c1c88(*(undefined4 *)(&DAT_43e787d4 + iVar6),iVar1);
      FUN_436c1cb4(*(undefined4 *)(&DAT_43e787d8 + iVar6),iVar1);
      FUN_436c1ce0(*(undefined4 *)(&DAT_43e787dc + iVar6),iVar1);
      FUN_436c1d0c(*(undefined4 *)(&DAT_43e787e0 + iVar6),iVar1);
      FUN_436c1d38(*(undefined4 *)(&DAT_43e787e4 + iVar6),iVar1);
      FUN_436c1d64(*(undefined4 *)(&DAT_43e787e8 + iVar6),iVar1);
      FUN_436c1d90(*(undefined4 *)(&DAT_43e787ec + iVar6),iVar1);
      FUN_436c1dbc(*(undefined4 *)(&DAT_43e787f0 + iVar6),iVar1);
      FUN_436c1de8(*(undefined4 *)(&DAT_43e787f4 + iVar6),iVar1);
      FUN_436c1e14(iVar6 + 0x43e787f8,iVar1);
      FUN_436c1e70(iVar6 + 0x43e78838,iVar1);
      FUN_436c1ecc(iVar6 + 0x43e78878,iVar1);
      FUN_436c1f48(iVar6 + 0x43e788b8,iVar1);
      FUN_436bd420(&DAT_43e784ec + iVar1 * 0xf0,iVar1);
      FUN_436c133c(&DAT_43e77cd4 + iVar1 * 0x370,iVar1);
      FUN_436c1068(*(undefined4 *)(&DAT_43e77bec + iVar4),iVar1);
      FUN_436c1090(*(undefined4 *)(&DAT_43e77bf0 + iVar4),iVar1);
      FUN_436c10b8(*(undefined4 *)(&DAT_43e77bf4 + iVar4),iVar1);
      FUN_436c10e0(*(undefined4 *)(&DAT_43e77bf8 + iVar4),iVar1);
      FUN_436c1108(*(undefined4 *)(&DAT_43e77bfc + iVar4),iVar1);
      FUN_436c1130(*(undefined4 *)(&DAT_43e77c00 + iVar4),iVar1);
      FUN_436c1158(*(undefined4 *)(&DAT_43e77c04 + iVar4),iVar1);
      FUN_436c1180(*(undefined4 *)(&DAT_43e77c08 + iVar4),iVar1);
      FUN_436c11a8(*(undefined4 *)(&DAT_43e77c0c + iVar4),iVar1);
      FUN_436c11d0(*(undefined4 *)(&DAT_43e77c10 + iVar4),iVar1);
      FUN_436c11f8(*(undefined4 *)(&DAT_43e77c14 + iVar4),iVar1);
      FUN_436c1220(*(undefined4 *)(&DAT_43e77c18 + iVar4),iVar1);
      FUN_436c1248(*(undefined4 *)(&DAT_43e77c1c + iVar4),iVar1);
      FUN_436c1270(*(undefined4 *)(&DAT_43e77c20 + iVar4),iVar1);
      FUN_436c1460(0,0,iVar1);
      FUN_436c13c0(0,iVar1);
      FUN_436c13e8(0,iVar1);
      FUN_436c1410(0,iVar1);
      FUN_436c1438(0,iVar1);
      FUN_436c14a0(0,iVar1);
      FUN_436bf95c(*(undefined4 *)(&DAT_43e78bfc + iVar1 * 4),(&DAT_43f922ef)[iVar1],auStack_28);
      thunk_FUN_439321ac(iVar1 != 0,auStack_28);
      if (iVar1 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 2;
      }
      if (iVar1 == 0) {
        uVar5 = 1;
      }
      else {
        uVar5 = 3;
      }
      FUN_436bfa50(*(undefined4 *)(&DAT_43e78bfc + iVar1 * 4),auStack_30);
      FUN_43b4a64e(uVar3,auStack_30);
      uVar3 = *(undefined4 *)(&DAT_43e78bfc + iVar1 * 4);
      param_3[2] = uStack_2c;
      *param_3 = uStack_2e;
      FUN_436bfa6c(uVar3,auStack_30);
      FUN_43b4a64e(uVar5,auStack_30);
      if ((*(int *)(&DAT_43e78bfc + iVar1 * 4) == 0) ||
         (*(int *)(&DAT_43e78bfc + iVar1 * 4) == 0x11)) {
        param_3[1] = 0xf00;
        *param_3 = 0xf00;
      }
      if (*(int *)(&DAT_43e78c04 + iVar1 * 4) == 0) {
        iVar2 = FUN_436bf500(iVar1,(&DAT_43f9229a)[iVar1]);
      }
      else {
        iVar2 = 1;
      }
      iVar4 = FUN_436bf6dc(iVar1);
      FUN_436bf470(iVar1);
      FUN_436bf664(iVar1);
      if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
        FUN_43acb8ea(iVar1);
        FUN_436bf7d0(iVar1);
      }
      FUN_436bf3a8(iVar1);
      if (((iVar2 != 0) && (iVar4 != 0)) && ((byte)(&DAT_43f922ef)[iVar1] < 2)) {
        (&DAT_43f922ef)[iVar1] = (&DAT_43f922ef)[iVar1] + 1;
      }
      FUN_43acb2e8(iVar1);
      uVar3 = 0;
    }
    else {
      uVar3 = 4;
    }
  }
  else {
    uVar3 = 2;
  }
  return uVar3;
}


/* query "436c019c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c019c(undefined4 param_1,int param_2)

{
  undefined4 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = (undefined4 *)&DAT_f3950500;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50500 = param_1;
      }
      return;
    }
    puVar1 = (undefined4 *)&DAT_f3850500;
  }
  *puVar1 = param_1;
  return;
}


/* query "436cf954" */

void FUN_436cf954(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  code *pcVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_44024944;
  uVar3 = param_1 & 0x3380000;
  uVar4 = param_1;
  if (uVar3 != 0) {
    if ((*(byte *)(DAT_44024944 + 0xf) & 1) != 0) {
      FUN_436cf6d4(0x165,1,1,&DAT_43c91f6e,uVar3,param_2,param_3);
      FUN_43902718(s_judgeComplexCallBack__x_43c91f79,uVar3);
    }
    if ((uVar3 & DAT_43e7ec4c) != 0) {
      param_2 = DAT_43e7ec4c;
      FUN_436cf6d4(0x165,1,1,&DAT_43c91f91,uVar3,DAT_43e7ec4c,param_3);
      FUN_43902718(s_DfeCoreErr_judgeComplexCallBack__43c91f9c,uVar3,DAT_43e7ec4c);
    }
    iVar5 = 0;
    DAT_43e7ec4c = uVar3 | DAT_43e7ec4c;
    do {
      if ((*(int *)((int)&DAT_43e7ec2c + iVar5) != 0) &&
         ((*(uint *)((int)&DAT_43e7ec28 + iVar5) & DAT_43e7ec4c) ==
          *(uint *)((int)&DAT_43e7ec28 + iVar5))) {
        if ((*(byte *)(iVar1 + 0xf) & 1) != 0) {
          FUN_436cf6d4(0x165,1,1,&DAT_43c91fd5,*(int *)((int)&DAT_43e7ec2c + iVar5),param_2,param_3)
          ;
          FUN_43902718(s_CallCallBack__x_43c91fe0,*(undefined4 *)((int)&DAT_43e7ec2c + iVar5));
        }
        FUN_436cf91c(*(undefined4 *)((int)&DAT_43e7ec28 + iVar5));
        pcVar2 = *(code **)((int)&DAT_43e7ec2c + iVar5);
        *(undefined4 *)((int)&DAT_43e7ec28 + iVar5) = 0;
        *(undefined4 *)((int)&DAT_43e7ec2c + iVar5) = 0;
        (*pcVar2)();
      }
      iVar5 = iVar5 + 8;
    } while (iVar5 != 0x20);
    uVar4 = param_1 & ~uVar3;
  }
  if (uVar4 == 0) {
    return;
  }
  FUN_436cf6d4(0x165,1,1,&DAT_43c91ff0,param_1,param_2,param_3);
  FUN_43902718(s_camIntHandler0__fact__x_43c91ffb,param_1);
  return;
}


/* query "436cf780" */

void s32_candidate_436cf780(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int extraout_r1;
  uint uVar1;
  
  uVar1 = DAT_43e7ec48 + 1;
  DAT_43e7ec48 = uVar1;
  if ((9 < uVar1) &&
     (FUN_4355fd4c(uVar1,1000,param_3,&DAT_43e7ec48,param_1,param_2,param_3), extraout_r1 != 0)) {
    return;
  }
  FUN_436cf6d4(0x165,1,1,&DAT_43c91e75,param_1,uVar1);
  FUN_43902718(s_camIntHandler1__fact__x_num__d_43c91e80,param_1,DAT_43e7ec48);
  return;
}


/* query "436cf818" */

void FUN_436cf818(void)

{
  FUN_43ad690c(0xfc000000,1);
  FUN_436cf0c8(9,0x436cf955);
  FUN_436cf0c8(10,0x436cf781);
  return;
}


/* query "436cf0c8" */

undefined4 FUN_436cf0c8(uint param_1,undefined4 param_2)

{
  if (param_1 < 0xe) {
    if (*(int *)(&DAT_43e7ebf0 + param_1 * 4) == 0) {
      *(undefined4 *)(&DAT_43e7ebf0 + param_1 * 4) = param_2;
      switch(param_1) {
      case 1:
        FUN_43ad696c();
        break;
      case 2:
        FUN_43ad6980();
        break;
      case 3:
        FUN_43ad6994();
        break;
      case 4:
        FUN_43ad69a8();
        break;
      case 5:
        FUN_43ad69ba();
        break;
      case 6:
        FUN_43ad69cc();
        break;
      case 7:
        FUN_43ad69de();
        break;
      case 8:
        FUN_43ad69f0();
        break;
      case 9:
        FUN_43ad6a0c();
        break;
      case 10:
        FUN_43ad6a20();
        break;
      case 0xb:
        FUN_43ad6a34();
        break;
      case 0xc:
        FUN_43ad6a48();
        break;
      case 0xd:
        FUN_43ad6a5c();
        break;
      default:
        FUN_43ad695a();
      }
      return 0;
    }
    FUN_436cf01c(0x165,1,1,&DAT_43c916f8,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__already_set_int___43c91703,param_1);
  }
  else {
    FUN_436cf01c(0x165,1,1,&DAT_43c916d1,param_1,param_2);
    FUN_43902718(s__Err__DFE_INT__NOT_SUPPORT_43c916dc);
  }
  return 1;
}


/* query "436cf91c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf91c(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_436cf7e8();
  if ((uVar1 & param_1) != param_1) {
    FUN_436cf6d4(0x165,0,3,s__DFECore____clearCamIntEnable0__a_43c91f38,uVar1,param_1,param_3);
  }
  _DAT_fc0a0018 = uVar1 & ~param_1;
  return;
}


/* query "436cf7e8" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_436cf7e8(void)

{
  return _DAT_fc0a0018;
}


/* query "43ad6a0c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_43ad6a0c(void)

{
  FUN_436cfd38(9);
  _DAT_fc01f010 = 0x800000;
  return;
}


/* query "43ad6a20" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_43ad6a20(void)

{
  FUN_436cfd44(10);
  _DAT_fc01f010 = 0x1000000;
  return;
}


/* query "43e7ec28" */
