/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43b03a74" */

undefined4 FUN_43b03a74(undefined4 param_1)

{
  FUN_4380f5b4();
  return param_1;
}


/* query "43b03abe" */

void s32_candidate_43b03abe(void)

{
  FUN_43560da8(0x1a,0x20);
  return;
}


/* query "43811324" */

void FUN_43811324(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  
  if (*(char *)(param_1 + 0xd70) == '\0') {
    iVar1 = FUN_43728d28(*(undefined4 *)(param_1 + 0xd68),*(undefined4 *)(param_1 + 0xd6c));
    iVar6 = DAT_4402546c;
    if (iVar1 == 0) {
      *(undefined1 *)(param_1 + 0xd70) = 1;
      return;
    }
    if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
      FUN_43561540(s_StSyncDvlpPrm_S_43cb12ce);
    }
    uVar2 = FUN_4378f9b4();
    uVar3 = FUN_4378f9e0();
    uVar4 = FUN_4378f9f0();
    uVar5 = FUN_4378f9d0();
    FUN_43aef4e8(uVar2,uVar5);
    FUN_43aeaf4e(uVar2,uVar3);
    FUN_437d9ae0(uVar4,uVar2);
    if ((*(byte *)(iVar6 + 0x16) & 5) == 4) {
      iVar6 = FUN_4378f9c0();
      if (*(int *)(iVar6 + 0x2d0) != 0) {
        FUN_43ad5396(iVar6 + 0x2d4,*(int *)(iVar6 + 0x2d0),0);
        return;
      }
    }
  }
  return;
}


/* query "438106ec" */

void FUN_438106ec(int param_1)

{
  char cVar1;
  int iVar2;
  int *piVar3;
  uint uVar4;
  undefined4 uVar5;
  char *pcVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined2 *puVar9;
  int iVar10;
  undefined1 uVar11;
  int iVar12;
  undefined4 uVar13;
  undefined1 *puVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined4 uVar17;
  int iVar18;
  int iVar19;
  undefined *puVar20;
  undefined *puVar21;
  undefined *puVar22;
  undefined1 auStack_350 [44];
  undefined4 uStack_324;
  uint uStack_320;
  undefined4 uStack_31c;
  undefined4 uStack_318;
  undefined4 uStack_2f0;
  undefined1 auStack_1b8 [48];
  undefined4 uStack_188;
  undefined1 auStack_158 [44];
  undefined4 uStack_12c;
  undefined4 uStack_128;
  undefined1 auStack_f8 [4];
  uint uStack_f4;
  uint uStack_f0;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_c4;
  undefined4 uStack_c0;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  int iStack_8c;
  undefined4 uStack_88;
  int iStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  int iStack_48;
  undefined4 uStack_44;
  int iStack_40;
  int iStack_3c;
  int iStack_38;
  undefined1 auStack_34 [4];
  short sStack_30;
  short sStack_2e;
  short sStack_2c;
  short asStack_2a [3];
  
  if (*(char *)(param_1 + 0xd70) != '\0') {
    return;
  }
  iVar2 = FUN_43728d28(*(undefined4 *)(param_1 + 0xd68),*(undefined4 *)(param_1 + 0xd6c));
  iVar7 = DAT_4402546c;
  if (iVar2 == 0) goto LAB_43810c6e;
  if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
    FUN_43561540(s_Cam_Sttng_S_43cb10eb);
  }
  iVar2 = FUN_437999e4(1,4);
  if (iVar2 == 0) {
    *(undefined1 *)(param_1 + 0xc39) = 0;
    *(undefined1 *)(param_1 + 0xc3a) = 0;
  }
  else {
    *(undefined1 *)(param_1 + 0xc39) = 1;
  }
  piVar3 = (int *)FUN_4378f9b4();
  if (((*(int *)(param_1 + 0x1f8) == 0) && (*(char *)(piVar3[8] + 2) == '\0')) &&
     (uVar4 = FUN_43ae8c4a(*(int *)piVar3[1] - DAT_43eea5f0), uVar4 < 2)) {
    *(undefined1 *)(param_1 + 0xc38) = 0;
  }
  else {
    *(undefined1 *)(param_1 + 0xc38) = 1;
  }
  FUN_4364d404(auStack_f8);
  FUN_4364d404(auStack_158);
  FUN_4380ca2c(auStack_350);
  cVar1 = *(char *)(param_1 + 0x524);
  if (cVar1 != '\0') {
    uStack_cc = 2;
    uStack_c8 = *(undefined4 *)(param_1 + 0x5a0);
    uStack_f4 = 0;
    uStack_f0 = 0;
  }
  if ((*(char *)(param_1 + 0xd40) == '\0') || (cVar1 == '\0')) {
    if (*(char *)(param_1 + 0xd41) == '\0') {
      iVar2 = FUN_43ae9674(param_1 + 0xe4);
      if (iVar2 != 0) {
        uStack_2f0 = 1;
        if (*(char *)(DAT_44024a14 + 0x1d) == '\x01') {
          uStack_2f0 = 2;
        }
        uStack_324 = 0;
        uStack_320 = (uint)*(byte *)(param_1 + 0xe6);
        uStack_31c = *(undefined4 *)(param_1 + 0xec);
        uStack_318 = *(undefined4 *)(param_1 + 0xf0);
      }
    }
    else {
      uStack_320 = 1;
      uStack_31c = *(undefined4 *)(param_1 + 0xd44);
      uStack_324 = 0;
      uStack_2f0 = 0;
      uStack_318 = *(undefined4 *)(param_1 + 0xd48);
    }
    puVar15 = (undefined *)0x0;
    if (cVar1 != '\0') goto LAB_4381082c;
  }
  else {
    uStack_cc = 0;
    uStack_c8 = 1;
    uStack_c4 = *(undefined4 *)(param_1 + 0xd44);
    uStack_c0 = *(undefined4 *)(param_1 + 0xd48);
    uStack_f4 = (uint)*(ushort *)(param_1 + 0x19a);
    uStack_f0 = (uint)*(ushort *)(param_1 + 0x19c);
LAB_4381082c:
    puVar15 = auStack_f8;
  }
  uStack_12c = 2;
  iVar2 = param_1 + 0x3e4;
  uStack_128 = 0xff;
  uVar4 = (uint)*(byte *)(DAT_44026920 + 0x81);
  if (DAT_43f9b2ab != uVar4) {
    if (uVar4 == 0) {
      iVar10 = 0xff;
      iVar12 = 0xfff;
      iVar18 = 0xfff;
      iVar19 = 0xfff;
    }
    else {
      iVar12 = (uint)*(byte *)(DAT_44026920 + 0x84) * 0x100 + (uint)*(byte *)(DAT_44026920 + 0x85);
      if (iVar12 == 0) {
        iVar12 = 0xfff;
      }
      iVar18 = (uint)*(byte *)(DAT_44026920 + 0x86) * 0x100 + (uint)*(byte *)(DAT_44026920 + 0x87);
      if (iVar18 == 0) {
        iVar18 = 0xfff;
      }
      iVar19 = (uint)*(byte *)(DAT_44026920 + 0x88) * 0x100 + (uint)*(byte *)(DAT_44026920 + 0x89);
      if (iVar19 == 0) {
        iVar19 = 0xfff;
      }
      iVar10 = uVar4 - 1;
    }
    DAT_43f9b2ab = *(byte *)(DAT_44026920 + 0x81);
    FUN_43acc282(*(undefined4 *)(param_1 + 0x51c),iVar10,iVar2,iVar12,iVar18,iVar19);
  }
  if (((*(char *)(iVar7 + 0x70) == '\0') && (iVar10 = FUN_4378003c(), iVar10 == 0)) &&
     ((*(char *)(param_1 + 0x20f) != '\0' ||
      ((*(char *)(param_1 + 0x20e) != '\0' || (*(char *)(param_1 + 0x210) != '\0')))))) {
    puVar20 = auStack_158;
  }
  else {
    puVar20 = (undefined *)0x0;
  }
  iVar10 = FUN_43ae9674(param_1 + 0xe4);
  if ((iVar10 == 0) && (*(char *)(param_1 + 0xd41) == '\0')) {
    puVar16 = (undefined *)0x0;
  }
  else {
    FUN_43b0319a((undefined *)(param_1 + 0x218),auStack_350);
    puVar16 = (undefined *)(param_1 + 0x218);
    if (*(char *)(param_1 + 0xd41) != '\0') {
      puVar16 = auStack_350;
    }
  }
  iVar10 = FUN_4378f9b4();
  iVar10 = *(int *)(iVar10 + 0x14);
  iVar12 = *(int *)(iVar10 + 0x20);
  cVar1 = *(char *)(iVar10 + 1);
  uVar17 = *(undefined4 *)(iVar10 + 8);
  uVar13 = *(undefined4 *)(iVar10 + 0x14);
  iVar18 = *(int *)(iVar10 + 0x24);
  iVar10 = *(int *)(iVar10 + 0x28);
  if (*(char *)(param_1 + 0x3da) == '\0') {
    if (*(char *)(iVar7 + 0x18) == '\0') {
      iVar19 = FUN_4378f9b4();
      if ((*(int *)(*(int *)(iVar19 + 8) + 0x248) == 0) || (cVar1 != '\0')) {
        uStack_94 = 0;
      }
      else {
        uStack_94 = 2;
        iStack_8c = iVar18 + iVar10 + iVar12;
        uStack_90 = uVar17;
        uStack_88 = uVar13;
        iStack_84 = iStack_8c;
      }
      uStack_98 = 1;
      puVar8 = &uStack_98;
    }
    else {
      puVar8 = (undefined4 *)0x0;
    }
  }
  else {
    puVar8 = (undefined4 *)0x0;
  }
  if ((*(char *)(param_1 + 0x213) != '\0') && (iVar10 = FUN_437dfa44(), iVar10 != 0)) {
    FUN_43797de8(2);
  }
  asStack_2a[0] = 0;
  sStack_2c = 0;
  if (*(int *)(param_1 + 0xc3c) != 0) {
    iVar10 = *piVar3;
    if (*(int *)(param_1 + 0xc3c) != 3) {
      uVar13 = FUN_4380fd58(*(undefined4 *)(iVar10 + 0x48));
      FUN_439c5320(auStack_34,&DAT_43bf37fc,4);
      sStack_2e = 0;
      sStack_30 = 0;
      uVar17 = FUN_43affda2(*(undefined4 *)(param_1 + 0x1e8));
      uVar5 = FUN_436d6118();
      FUN_43ad9170(uVar5,(int)*(short *)(*piVar3 + 0x454),(int)*(short *)(*piVar3 + 0x456),
                   &sStack_2e,&sStack_30,uVar13,uVar17);
      iStack_38 = (int)sStack_2e << 8;
      iStack_3c = (int)sStack_30 << 8;
      iVar10 = FUN_436ea50c(&DAT_43eea76c,auStack_34,&iStack_38,&iStack_3c);
      if (iVar10 != 0) {
        FUN_4380fcac(3,9,1,&DAT_43cb10f7);
        FUN_43902718(s_Sync_Cam_Setting__DIST_RSLT_NG_C_43cb110b);
      }
      FUN_43aef9fa(piVar3,(int)(short)((uint)iStack_38 >> 8),(int)(short)((uint)iStack_3c >> 8),
                   asStack_2a,&sStack_2c,uVar13,uVar17);
      FUN_436d6118();
      pcVar6 = (char *)FUN_43ad918e();
      if (*pcVar6 != '\0') {
        *(undefined1 *)(param_1 + 0x20c) = 0;
      }
      if (*(char *)(param_1 + 0x20c) == '\0') goto LAB_43810a72;
      iVar10 = *piVar3;
    }
    FUN_437964e4(*(undefined2 *)(iVar10 + 0x454),*(undefined2 *)(iVar10 + 0x456));
  }
LAB_43810a72:
  uVar13 = FUN_43acea8a(*(undefined4 *)(param_1 + 0x508));
  FUN_43b03a96(uVar13,(int)asStack_2a[0],0);
  uVar13 = FUN_43acc0c4(*(undefined4 *)(param_1 + 0x508));
  FUN_43affa0a(uVar13,0,(int)sStack_2c);
  uVar13 = FUN_43acc0c4(*(undefined4 *)(param_1 + 0x508));
  FUN_43b03aa4(uVar13,0,(int)sStack_2c);
  if (((*(uint *)(iVar7 + 0x50) & 0xff00ff00) != 0) || (*(char *)(iVar7 + 0x55) != '\0')) {
    uVar13 = FUN_43acc0c4(*(undefined4 *)(param_1 + 0x508));
    if (*(char *)(iVar7 + 0x50) == '\0') {
      iVar10 = 1;
    }
    else {
      iVar10 = -1;
    }
    if (*(char *)(iVar7 + 0x52) == '\0') {
      iVar12 = 1;
    }
    else {
      iVar12 = -1;
    }
    FUN_43affa0a(uVar13,(uint)*(byte *)(iVar7 + 0x51) * iVar10,
                 iVar12 * ((uint)*(byte *)(iVar7 + 0x55) * 0x100 + (uint)*(byte *)(iVar7 + 0x53)));
  }
  FUN_43acc308(*(undefined4 *)(param_1 + 0x51c),0,0,0,0);
  if (*(char *)(param_1 + 0x525) == '\0') {
    iVar10 = 0;
    if ((*(char *)(param_1 + 0x211) != '\0') &&
       (iVar10 = 1 - (uint)*(byte *)(iVar7 + 0x2e), 1 < *(byte *)(iVar7 + 0x2e))) {
      iVar10 = 0;
    }
    iVar12 = FUN_43aeb6b6(*(undefined4 *)(param_1 + 0x510));
    if (iVar12 == 0) {
      uVar17 = 1;
      uVar13 = *(undefined4 *)(param_1 + 0x51c);
      puVar21 = puVar16;
      puVar22 = puVar15;
      goto LAB_43810c48;
    }
    FUN_4364d404(auStack_1b8);
    if (puVar15 == (undefined *)0x0) {
      puVar14 = (undefined1 *)0x0;
    }
    else {
      FUN_43acdd52(auStack_1b8,puVar15);
      uStack_188 = *(undefined4 *)(param_1 + 0x608);
      puVar14 = auStack_1b8;
    }
    if ((*(byte *)(iVar7 + 0xab) & 2) == 0) {
      uVar11 = *(undefined1 *)(param_1 + 0x210);
    }
    else {
      uVar11 = 0;
    }
    iVar7 = FUN_43acc5d0(*(undefined4 *)(param_1 + 0x51c),iVar2,puVar8,iVar10,uVar11,puVar20,puVar16
                         ,puVar15,puVar14);
  }
  else {
    FUN_43acdd52(&DAT_43eea7f8,auStack_158);
    FUN_43afa606(&DAT_43e18a68,auStack_350);
    FUN_43acdd52(&DAT_43eea798,auStack_f8);
    DAT_43eea734 = uStack_98;
    DAT_43eea738 = uStack_94;
    DAT_43eea73c = uStack_90;
    DAT_43eea740 = iStack_8c;
    DAT_43eea744 = uStack_88;
    DAT_43eea748 = iStack_84;
    DAT_43eea74c = uStack_80;
    DAT_43eea750 = uStack_7c;
    DAT_43eea754 = uStack_78;
    DAT_43eea758 = uStack_74;
    DAT_43eea75c = uStack_70;
    DAT_43eea760 = uStack_6c;
    DAT_43eea764 = uStack_68;
    DAT_43eea768 = puVar20;
    if (puVar20 == auStack_158) {
      DAT_43eea768 = &DAT_43eea7f8;
    }
    DAT_43eea5fc = puVar16;
    if (puVar16 == auStack_350) {
      DAT_43eea5fc = &DAT_43e18a68;
    }
    DAT_43eea794 = puVar15;
    if (puVar15 == auStack_f8) {
      DAT_43eea794 = &DAT_43eea798;
    }
    DAT_43eea5f4 = puVar8;
    if (puVar8 == &uStack_98) {
      DAT_43eea5f4 = &DAT_43eea734;
    }
    uVar13 = *(undefined4 *)(param_1 + 0x51c);
    iVar10 = 0;
    puVar20 = (undefined *)0x0;
    puVar21 = (undefined *)0x0;
    puVar22 = (undefined *)0x0;
    uVar17 = 0;
LAB_43810c48:
    iVar7 = FUN_43acc61c(uVar13,iVar2,puVar8,iVar10,puVar20,puVar21,puVar22,uVar17);
  }
  if (iVar7 != 0) {
    FUN_4380fcac(3,9,1,&DAT_43cb1153,iVar7);
    FUN_43902718(s_CamCore_ParamSetError_0x_x_43cb1167,iVar7);
    FUN_437964d4();
LAB_43810c6e:
    *(undefined1 *)(param_1 + 0xd70) = 1;
    return;
  }
  if (*(char *)(param_1 + 0x525) != '\0') {
    FUN_43aceab6(*(undefined4 *)(param_1 + 0x508));
    puVar8 = (undefined4 *)FUN_43acd102();
    DAT_43eea704 = *puVar8;
    DAT_43eea708 = puVar8[1];
    DAT_43eea70c = puVar8[2];
    DAT_43eea710 = puVar8[3];
    DAT_43eea714 = puVar8[4];
    DAT_43eea718 = puVar8[5];
    DAT_43eea71c = puVar8[6];
    DAT_43eea720 = puVar8[7];
    DAT_43eea724 = puVar8[8];
    DAT_43eea728 = puVar8[9];
    if (puVar15 != (undefined *)0x0) {
      *(undefined4 *)(puVar15 + 4) = DAT_43eea704;
      *(undefined4 *)(puVar15 + 8) = DAT_43eea708;
    }
  }
  uVar13 = thunk_FUN_436cd00c();
  *DAT_44022084 = uVar13;
  FUN_43a944d8(&uStack_64);
  if (*(char *)(param_1 + 0x525) == '\0') {
    iVar7 = FUN_43aeb6b6(*(undefined4 *)(param_1 + 0x510));
    if (iVar7 == 0) {
      FUN_43aceaaa(*(undefined4 *)(param_1 + 0x508));
      puVar8 = (undefined4 *)FUN_43acd0d4();
    }
    else {
      (**(code **)(**(int **)(param_1 + 0x508) + 0x18))();
      puVar8 = (undefined4 *)FUN_43b03ab2();
    }
    uStack_64 = *puVar8;
    uStack_60 = puVar8[1];
    uStack_5c = puVar8[2];
    uStack_58 = puVar8[3];
    uStack_54 = puVar8[4];
    uStack_50 = puVar8[5];
    uStack_4c = puVar8[6];
    iStack_48 = puVar8[7];
    uStack_44 = puVar8[8];
    iStack_40 = puVar8[9];
  }
  else {
    FUN_43acc0c4(*(undefined4 *)(param_1 + 0x508));
    puVar8 = (undefined4 *)FUN_43ad02b4();
    uStack_64 = *puVar8;
    uStack_60 = puVar8[1];
    uStack_5c = puVar8[2];
    uStack_58 = puVar8[3];
    uStack_54 = puVar8[4];
    uStack_50 = puVar8[5];
    uStack_4c = puVar8[6];
    iStack_48 = puVar8[7];
    uStack_44 = puVar8[8];
    iStack_40 = puVar8[9];
    if (*(int *)(param_1 + 0x3e0) == 1) {
      iStack_40 = iStack_40 << 1;
      iStack_48 = iStack_48 << 1;
    }
  }
  *(undefined4 *)(param_1 + 0x1bc) = uStack_64;
  *(undefined4 *)(param_1 + 0x1c0) = uStack_60;
  *(undefined4 *)(param_1 + 0x1c4) = uStack_5c;
  *(undefined4 *)(param_1 + 0x1c8) = uStack_58;
  *(undefined4 *)(param_1 + 0x1cc) = uStack_54;
  *(undefined4 *)(param_1 + 0x1d0) = uStack_50;
  *(undefined4 *)(param_1 + 0x1d4) = uStack_4c;
  *(int *)(param_1 + 0x1d8) = iStack_48;
  *(undefined4 *)(param_1 + 0x1dc) = uStack_44;
  *(int *)(param_1 + 0x1e0) = iStack_40;
  if (*(char *)(param_1 + 0x524) == '\0') {
    FUN_43aceab6(*(undefined4 *)(param_1 + 0x508));
    puVar9 = (undefined2 *)FUN_43b03ab4();
    *(undefined2 *)(param_1 + 0x19a) = *puVar9;
  }
  else {
    uVar13 = *(undefined4 *)(param_1 + 0x510);
    iVar7 = FUN_43aeb6b6(uVar13);
    if (iVar7 == 0) {
      *(undefined2 *)(param_1 + 0x19a) = (undefined2)uStack_f4;
      *(undefined2 *)(param_1 + 0x19c) = (undefined2)uStack_f0;
      goto LAB_43810da6;
    }
    FUN_43b03ab8(uVar13);
    puVar9 = (undefined2 *)FUN_43acea82();
    *(undefined2 *)(param_1 + 0x19a) = *puVar9;
    FUN_43b03ab8(uVar13);
    puVar9 = (undefined2 *)FUN_43acea82();
  }
  *(undefined2 *)(param_1 + 0x19c) = puVar9[2];
LAB_43810da6:
  if (*(char *)(param_1 + 0xc39) == '\0') {
    if (*(ushort *)(param_1 + 0x19c) < *(ushort *)(param_1 + 0x1a0)) {
      *(ushort *)(param_1 + 0x1a0) = *(ushort *)(param_1 + 0x19c);
    }
  }
  if (*(char *)(param_1 + 0x525) != '\0') {
    return;
  }
  FUN_43acdd52(param_1 + 0x538,auStack_158);
  if (*(char *)(param_1 + 0xd40) != '\0') {
    FUN_4380fbf0(param_1);
  }
  if (*(char *)(param_1 + 0xd41) == '\0') {
    return;
  }
  FUN_4380fc40(param_1,puVar16);
  return;
}


/* query "43810e7c" */

void FUN_43810e7c(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_38 [12];
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  short sStack_28;
  undefined2 uStack_26;
  undefined1 auStack_24 [12];
  undefined2 uStack_18;
  undefined2 uStack_16;
  short sStack_14;
  undefined2 uStack_12;
  
  if (*(char *)(param_1 + 0xd70) == '\0') {
    iVar1 = FUN_43728d28(*(undefined4 *)(param_1 + 0xd68),*(undefined4 *)(param_1 + 0xd6c));
    if (iVar1 == 0) {
      *(undefined1 *)(param_1 + 0xd70) = 1;
    }
    else {
      if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
        FUN_43561540(s_IDT_Wk_Set_S_43cb1182);
      }
      uVar2 = FUN_4378f9b4();
      if (*(char *)(param_1 + 0xc38) != '\0') {
        FUN_43af67a2(*(undefined1 *)(param_1 + 0x3e0),uVar2);
        sStack_14 = *(short *)(param_1 + 0x19a);
        if ((DAT_43f7bed6 == sStack_14) && (DAT_43f7bed0 == *(short *)(param_1 + 0x19c))) {
          uStack_18 = DAT_43f7bed2;
          uStack_16 = DAT_43f7bed4;
          sStack_14 = DAT_43f7bce8;
          uStack_26 = DAT_43f7bcea;
        }
        else {
          uStack_16 = 0;
          uStack_18 = 0;
          uStack_26 = *(undefined2 *)(param_1 + 0x19c);
        }
        uStack_2c = uStack_18;
        uStack_2a = uStack_16;
        sStack_28 = sStack_14;
        uStack_12 = uStack_26;
        iVar1 = FUN_437999e4(1,1);
        if (((iVar1 != 0) || (iVar1 = FUN_437999e4(2,1), iVar1 != 0)) ||
           (iVar1 = FUN_437999e4(1,2), iVar1 != 0)) {
          FUN_438653dc(auStack_24,uVar2);
          FUN_438673ec(auStack_38,*(undefined4 *)(param_1 + 0x50c),*(undefined4 *)(param_1 + 0x510))
          ;
          FUN_437d9d1c(uVar2);
        }
      }
    }
  }
  return;
}


/* query "4381061c" */

void FUN_4381061c(int param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
    FUN_43561540(s_JdgBBOut_S_43cb10e0);
  }
  iVar2 = FUN_4378f9b4();
  if ((*(int *)(param_1 + 0x204) == 2) && (*(char *)(*(int *)(iVar2 + 0x30) + 0xc) != '\0')) {
    *(undefined4 *)(param_1 + 0x204) = 3;
    if (*(char *)(param_1 + 0x20c) == '\0') goto LAB_4381067c;
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
    *(undefined1 *)(param_1 + 0x20d) = 0;
    if (*(char *)(param_1 + 0x20c) == '\0') goto LAB_4381067c;
  }
  uVar1 = FUN_4378e824(DAT_44025f5c,iVar2,uVar3);
  *(undefined1 *)(param_1 + 0x20c) = uVar1;
LAB_4381067c:
  iVar5 = *(int *)(iVar2 + 0x3c);
  if (*(char *)(iVar5 + 0x1e1) != '\0') {
    *(undefined1 *)(param_1 + 0x20c) = 0;
  }
  iVar4 = *(int *)(iVar2 + 0xc);
  if (*(char *)(iVar4 + 0x14) != '\0') {
    *(undefined1 *)(param_1 + 0x20c) = 0;
  }
  iVar2 = (uint)*(byte *)(iVar4 + 0x14) * 0x1000 + (uint)*(byte *)(iVar5 + 0x1e1) * 0x100 +
          *(int *)(param_1 + 0x204) + (uint)*(byte *)(*(int *)(iVar2 + 0x30) + 0xc) * 0x10;
  if (iVar2 != DAT_43eea72c) {
    FUN_43901a8c(4,0x2041,(uint)(iVar2 == 0x13) * 0x10000000 + iVar2,0);
    DAT_43eea72c = iVar2;
  }
  return;
}


/* query "44021e0c" */

/* query "440259b4" */

/* query "44026238" */

/* query "440204b4" */

/* query "44020ee4" */

/* query "44023820" */

/* query "43ca51ac" */

/* query "43797344" */

undefined4 FUN_43797344(void)

{
  return *DAT_440212ac;
}


/* query "4379d000" */

void FUN_4379cfe0(void)

{
  undefined4 uVar1;
  
  FUN_43ae7558(&DAT_43e9f0d8);
  FUN_43ae7558(&DAT_43e9f100);
  FUN_43ae7558(&DAT_43e9f128);
  FUN_43ae7558(&DAT_43e9f150);
  uVar1 = DAT_440254cc;
  FUN_439b4244(0,0x4379b3d1,DAT_440254cc);
  FUN_43ae7558(&DAT_43e9f2e8);
  FUN_43ae7558(&DAT_43e9f310);
  FUN_43ae7558(&DAT_43e9f338);
  FUN_43ae7558(&DAT_43e9f360);
  FUN_439b4244(0,0x4379b3ad,uVar1);
  return;
}


/* query "4379cc00" */

void FUN_4379bb90(int *param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined1 uVar4;
  char cVar5;
  ushort uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined4 uVar9;
  char *pcVar10;
  int iVar11;
  byte bVar12;
  int iVar13;
  uint uVar14;
  undefined4 uVar15;
  int iVar16;
  uint uVar17;
  undefined2 *puVar18;
  int *piVar19;
  undefined *puVar20;
  int iVar21;
  undefined4 *puVar22;
  int *piVar23;
  uint uVar24;
  uint uVar25;
  int iVar26;
  uint uVar27;
  bool bVar28;
  undefined1 auStack_434 [244];
  undefined1 auStack_340 [216];
  undefined1 auStack_268 [132];
  undefined1 auStack_1e4 [76];
  undefined1 auStack_198 [64];
  undefined1 auStack_158 [44];
  undefined1 auStack_12c [40];
  undefined1 auStack_104 [8];
  undefined1 auStack_fc [4];
  undefined4 uStack_f8;
  undefined1 auStack_dc [36];
  undefined1 auStack_b8 [32];
  undefined1 auStack_98 [32];
  undefined1 auStack_78 [28];
  undefined1 auStack_5c [28];
  undefined1 auStack_40 [28];
  
  iVar21 = 0;
  piVar23 = (int *)&DAT_43e9f7d8;
  do {
    piVar23 = piVar23 + 1;
    if (*piVar23 != 2) {
      FUN_43b2a296(&DAT_43e9f0d8 + iVar21 * 0x28,5);
    }
    iVar21 = iVar21 + 1;
  } while (iVar21 != 4);
  iVar21 = 0;
  while (*(int *)((int)&DAT_43e9f7dc + iVar21) != 2) {
    iVar21 = iVar21 + 4;
    if (iVar21 == 0x10) {
      return;
    }
  }
  iVar21 = FUN_43aea1b6(param_1);
  if (iVar21 != 0) goto LAB_4379c298;
  iVar13 = param_1[0x12];
  DAT_43e9f204 = *(undefined4 *)(iVar13 + 0xc);
  DAT_43e9f208 = *(undefined4 *)(iVar13 + 0x10);
  DAT_43e9f2da = *(undefined1 *)(iVar13 + 0xe2);
  uVar25 = (uint)*(byte *)(param_1[0x12] + 0xe3);
  if (7 < uVar25) {
    uVar25 = 8;
  }
  DAT_43e9f2db = (undefined1)uVar25;
  uVar14 = *(byte *)(param_1[0x12] + 0xe7) - 1 & 0xff;
  if (uVar14 < 3) {
    uVar27 = (uint)*(ushort *)(&DAT_43bef288 + uVar14 * 2);
    uVar14 = (uint)*(ushort *)(&DAT_43bef28e + uVar14 * 2);
  }
  else {
    uVar14 = 0x280;
    uVar27 = 0x1e0;
  }
  puVar22 = &DAT_43e9f204;
  for (uVar24 = 0; iVar13 = param_1[0x12], uVar24 < uVar25; uVar24 = uVar24 + 1) {
    iVar16 = uVar24 * 0x14;
    iVar13 = iVar13 + iVar16;
    uVar4 = *(undefined1 *)(iVar13 + 0x20);
    uVar6 = *(ushort *)(iVar13 + 0x14);
    *(undefined2 *)((int)puVar22 + 10) = *(undefined2 *)(iVar13 + 0x16);
    uVar1 = *(ushort *)(iVar13 + 0x18);
    uVar2 = *(undefined2 *)(iVar13 + 0x1a);
    *(undefined1 *)(puVar22 + 5) = uVar4;
    iVar13 = param_1[0x12];
    *(undefined2 *)((int)puVar22 + 0xe) = uVar2;
    *(ushort *)(puVar22 + 2) = uVar6;
    *(ushort *)(puVar22 + 3) = uVar1;
    uVar4 = *(undefined1 *)(iVar13 + iVar16 + 0x21);
    puVar22[4] = *(undefined4 *)(iVar13 + iVar16 + 0x1c);
    *(undefined1 *)((int)puVar22 + 0x15) = uVar4;
    *(undefined1 *)((int)puVar22 + 0x16) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x22);
    *(undefined1 *)((int)puVar22 + 0x17) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x23);
    *(undefined1 *)(puVar22 + 6) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x24);
    *(undefined1 *)((int)puVar22 + 0x19) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x25);
    *(undefined1 *)((int)puVar22 + 0x1a) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x26);
    *(undefined1 *)((int)puVar22 + 0x1b) = *(undefined1 *)(param_1[0x12] + iVar16 + 0x27);
    uVar17 = (uint)uVar6 + (uint)uVar1;
    if ((uVar14 < uVar17) ||
       (uVar27 < (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10))) {
      FUN_4379b300(3,9,1,&DAT_43ca4df2,uVar17,
                   (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10));
      FUN_43902718(s_PIN_YC_FACE_face_param_error__d__43ca4e06,
                   (uint)*(ushort *)(puVar22 + 2) + (uint)*(ushort *)(puVar22 + 3),
                   (uint)*(ushort *)((int)puVar22 + 0xe) + (uint)*(ushort *)((int)puVar22 + 10));
      *(undefined2 *)(puVar22 + 2) = 0;
      *(undefined2 *)((int)puVar22 + 10) = 0;
      *(undefined2 *)(puVar22 + 3) = 100;
      *(undefined2 *)((int)puVar22 + 0xe) = 100;
    }
    puVar22 = puVar22 + 5;
  }
  DAT_43e9f2ac = *(undefined4 *)(iVar13 + 0xb4);
  DAT_43e9f2b0 = *(undefined4 *)(iVar13 + 0xb8);
  DAT_43e9f2dc = *(undefined1 *)(iVar13 + 0xe4);
  DAT_43e9f2dd = *(undefined1 *)(param_1[0x12] + 0xe5);
  iVar13 = param_1[0x12];
  DAT_43e9f2b4 = *(undefined2 *)(iVar13 + 0xbc);
  DAT_43e9f2b6 = *(undefined2 *)(iVar13 + 0xbe);
  DAT_43e9f2b8 = *(undefined2 *)(iVar13 + 0xc0);
  DAT_43e9f2ba = *(undefined2 *)(iVar13 + 0xc2);
  DAT_43e9f2bc = *(undefined1 *)(iVar13 + 0xc4);
  DAT_43e9f2bd = *(undefined1 *)(param_1[0x12] + 0xc5);
  DAT_43e9f2be = *(undefined1 *)(param_1[0x12] + 0xc6);
  DAT_43e9f2bf = *(undefined1 *)(param_1[0x12] + 199);
  DAT_43e9f2c0 = *(undefined1 *)(param_1[0x12] + 200);
  iVar13 = param_1[0x12];
  DAT_43e9f2c4 = *(undefined4 *)(iVar13 + 0xcc);
  DAT_43e9f2c8 = *(undefined4 *)(iVar13 + 0xd0);
  DAT_43e9f2de = *(undefined1 *)(iVar13 + 0xe6);
  iVar13 = param_1[0x12];
  DAT_43e9f2cc = *(ushort *)(iVar13 + 0xd4);
  DAT_43e9f2ce = *(ushort *)(iVar13 + 0xd6);
  DAT_43e9f2d0 = *(ushort *)(iVar13 + 0xd8);
  DAT_43e9f2d2 = *(ushort *)(iVar13 + 0xda);
  DAT_43e9f2d4 = *(undefined1 *)(iVar13 + 0xdc);
  DAT_43e9f2d5 = *(undefined1 *)(param_1[0x12] + 0xdd);
  DAT_43e9f2d6 = *(undefined1 *)(param_1[0x12] + 0xde);
  DAT_43e9f2d7 = *(undefined1 *)(param_1[0x12] + 0xdf);
  DAT_43e9f2d8 = *(undefined1 *)(param_1[0x12] + 0xe0);
  uVar25 = *(byte *)(param_1[0x12] + 0xe9) - 1 & 0xff;
  if (uVar25 < 3) {
    uVar14 = (uint)*(ushort *)(&DAT_43bef294 + uVar25 * 2);
    uVar25 = (uint)*(ushort *)(&DAT_43bef29a + uVar25 * 2);
  }
  else {
    uVar25 = 0x280;
    uVar14 = 0x1e0;
  }
  if ((uVar25 < (uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc) ||
     (uVar14 < (uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce)) {
    FUN_4379b300(3,9,1,&DAT_43ca4e2a,(uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc,
                 (uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce);
    FUN_43902718(s_PIN_YC_FACE_trackingdata_param_e_43ca4e3e,(uint)DAT_43e9f2d0 + (uint)DAT_43e9f2cc
                 ,(uint)DAT_43e9f2d2 + (uint)DAT_43e9f2ce);
    DAT_43e9f2cc = 0;
    DAT_43e9f2ce = 0;
    DAT_43e9f2d0 = 100;
    DAT_43e9f2d2 = 100;
  }
  DAT_43e9f2df = *(char *)(param_1[0x12] + 0xe7);
  DAT_43e9f2e0 = *(char *)(param_1[0x12] + 0xe8);
  DAT_43e9f2e1 = *(char *)(param_1[0x12] + 0xe9);
  if (DAT_43e9f7e0 == 2) {
    puVar20 = &DAT_43e9f3c0;
LAB_4379cd50:
    cVar5 = puVar20[0x2e];
    if (cVar5 != DAT_43e9f2df) {
      DAT_43e9f2db = 0;
    }
    if (cVar5 != DAT_43e9f2e0) {
      DAT_43e9f2dc = 0;
    }
    if (cVar5 != DAT_43e9f2e1) {
      DAT_43e9f2de = 0;
    }
  }
  else if (DAT_43e9f7dc == 2) {
    puVar20 = &DAT_43e9f388;
    goto LAB_4379cd50;
  }
  DAT_43e9f178 = FUN_43ae8c4a(*(int *)param_1[1] + -1);
  DAT_43e9f17c = 0;
  iVar16 = param_1[3];
  DAT_43e9f180 = (uint)*(ushort *)(iVar16 + 0xe8);
  DAT_43e9f184 = (uint)*(ushort *)(iVar16 + 0xea);
  DAT_43e9f188 = (uint)*(ushort *)(iVar16 + 0xec);
  DAT_43e9f18c = (uint)*(ushort *)(iVar16 + 0xee);
  iVar13 = *(int *)(*param_1 + 0xe0);
  if (iVar13 == 3) {
    DAT_43e9f190 = 0xb;
  }
  else {
    if (iVar13 < 4) {
      if (iVar13 == 1) {
LAB_4379bf04:
        DAT_43e9f190 = 7;
        goto LAB_4379bf2c;
      }
      bVar28 = iVar13 == 2;
    }
    else {
      if (iVar13 == 0x27) goto LAB_4379bf04;
      bVar28 = iVar13 == 0x28;
    }
    if (bVar28) {
      DAT_43e9f190 = 8;
    }
    else if (*(char *)(iVar16 + 0x100) == '\x01') {
      DAT_43e9f190 = 0xb;
    }
    else {
      DAT_43e9f190 = 0;
    }
  }
LAB_4379bf2c:
  DAT_43e9f192 = *(undefined1 *)(iVar16 + 0xf4);
  DAT_43e9f194 = 0;
  DAT_43e9f198 = 0;
  DAT_43e9f19c = (uint)*(ushort *)(param_1[3] + 0xfc);
  DAT_43e9f1a4 = 0;
  DAT_43e9f1a0 = (uint)*(ushort *)(param_1[3] + 0xfe);
  DAT_43e9f1a8 = 0;
  DAT_43e9f1ac = 0x20;
  DAT_43e9f1ae = (ushort)(*(int *)(*param_1 + 0x3d4) != 0);
  switch(*(undefined4 *)(*param_1 + 0x3c8)) {
  case 0:
  case 0x12:
    DAT_43e9f1b0 = 0;
    break;
  case 1:
    DAT_43e9f1b0 = 5;
    break;
  case 2:
    DAT_43e9f1b0 = 6;
    break;
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
  case 0xd:
  case 0xe:
  case 0xf:
    DAT_43e9f1b0 = 10;
    break;
  case 10:
  case 0xb:
  case 0xc:
  case 0x10:
    DAT_43e9f1b0 = 4;
    break;
  default:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,799);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,799);
    DAT_43e9f1b0 = 0;
  }
  DAT_43e9f1b2 = (ushort)*(byte *)(param_1[0xf] + 0x1e0);
  if (0x18 < *(byte *)(param_1[0xf] + 0x1e0)) {
    DAT_43e9f1b2 = 0;
  }
  DAT_43e9f1b4 = 0;
  if (*(uint *)(*param_1 + 0x2c4) < 8) {
    uVar25 = 1 << (*(uint *)(*param_1 + 0x2c4) & 0xff);
    if ((uVar25 & 0xbe) != 0) goto LAB_4379c062;
    if ((uVar25 & 0x41) == 0) goto LAB_4379c032;
    DAT_43e9f1b6 = 1;
  }
  else {
LAB_4379c032:
    FUN_4379b300(5,0,1,&DAT_43c9b47c,s_SyncYCOut_cpp_43ca4de4,0x33a);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_SyncYCOut_cpp_43ca4de4,0x33a);
LAB_4379c062:
    DAT_43e9f1b6 = 0;
  }
  DAT_43e9f1b7 = *(int *)(param_1[2] + 0x1c8) != 1;
  if (*(int *)(param_1[10] + 0x94) < 0) {
    DAT_43e9f1b8 = 0xffffffff;
  }
  else {
    DAT_43e9f1b8 = FUN_4355fd68(*(int *)(param_1[10] + 0x94),10);
  }
  DAT_43e9f1bc = 100;
  DAT_43e9f1c8 = *(uint *)(param_1[3] + 0xf8) & 0x1ffffff;
  DAT_43e9f1cc = (uint)(*(char *)(param_1[0xb] + 0x8c) != '\0');
  if (*(int *)(*param_1 + 0x488) == 1) {
    DAT_43e9f1cc = DAT_43e9f1cc | 0x10;
  }
  bVar12 = 0;
  DAT_43e9f1d0 = 0;
  DAT_43e9f1d1 = 0;
  DAT_43e9f1cc = (*(short *)(param_1[0xb] + 0x92) + 8) * 0x10 & 0xfff00U | DAT_43e9f1cc;
  iVar13 = *param_1;
  iVar16 = param_1[10];
  cVar5 = *(char *)(param_1[0xb] + 0x2c);
  if (*(char *)(iVar16 + 0x34) == '\0') {
    if (*(char *)(iVar16 + 0x33) == '\0') {
      bVar12 = 0;
    }
    else {
LAB_4379c140:
      bVar12 = *(byte *)(iVar16 + 0x35) + 1;
    }
  }
  else {
    if (*(char *)(iVar16 + 0x34) != '\x01') goto LAB_4379c140;
    if (*(char *)(iVar16 + 0x33) != '\x01') {
      bVar12 = ~*(byte *)(iVar16 + 0x35);
    }
  }
  DAT_43e9f1e4 = bVar12 & 0x1f;
  if ((*(int *)(iVar13 + 0x448) != 0) && ((*(uint *)(param_1[0xb] + 0x28) & 0xff) != 0)) {
    if (*(int *)(iVar13 + 0x2dc) == 0) {
      bVar12 = 0;
    }
    else {
      bVar12 = *(char *)(iVar13 + 0x2d8) + 1;
      if ('\a' < (char)bVar12) {
        bVar12 = 8;
      }
      if (*(int *)(iVar13 + 0x2dc) == 2) {
        bVar12 = -bVar12;
      }
    }
    DAT_43e9f1e4 = bVar12 & 0x1f;
    if ((*(char *)(iVar16 + 0x167) != '\0') && (cVar5 == '\x01')) {
      DAT_43e9f1e4 = 0;
    }
    DAT_43e9f1e4 = DAT_43e9f1e4 | 0x40;
  }
  if (*(char *)(iVar16 + 0x166) == '\0') {
    if (*(int *)(iVar13 + 0x448) == 0) {
      if (*(char *)(iVar16 + 0x167) != '\0') goto LAB_4379c1ba;
    }
    else if (cVar5 == '\x01') goto LAB_4379c1ba;
  }
  else {
LAB_4379c1ba:
    DAT_43e9f1e4 = DAT_43e9f1e4 | 0x80;
  }
  DAT_43e9f1e6 = FUN_4355faf0(*(int *)(param_1[0xb] + 0x5c) << 4,
                              *(undefined4 *)(param_1[0xb] + 0x58));
  puVar22 = &DAT_43e9f4c4;
  iVar13 = 0;
  do {
    iVar26 = param_1[0xb];
    *(undefined4 *)((int)&DAT_43e9f4c4 + iVar13) = *(undefined4 *)(param_1[10] + 0x9c);
    iVar16 = iVar13 + 0xc4;
    *(undefined4 *)((int)&DAT_43e9f4c8 + iVar13) = 0;
    puVar22[2] = *(undefined4 *)(iVar26 + 0x58);
    puVar22[3] = *(undefined4 *)(iVar26 + 0x5c);
    uVar9 = FUN_43ae8c4a(*(int *)param_1[1] + -1);
    uVar4 = *(undefined1 *)(iVar26 + 7);
    puVar22[5] = 0;
    *(undefined1 *)(puVar22 + 6) = uVar4;
    puVar18 = (undefined2 *)param_1[0xd];
    uVar15 = *(undefined4 *)(puVar18 + 0x74);
    uVar2 = *puVar18;
    puVar22[8] = 0;
    puVar22[7] = uVar15;
    uVar3 = puVar18[7];
    *(undefined2 *)(puVar22 + 9) = uVar2;
    *(undefined2 *)((int)puVar22 + 0x26) = uVar3;
    puVar22[4] = uVar9;
    uVar2 = puVar18[0x72];
    *(undefined2 *)(puVar22 + 10) = puVar18[0x73];
    *(undefined2 *)((int)puVar22 + 0x2a) = uVar2;
    *(undefined1 *)(puVar22 + 0x2e) = *(undefined1 *)(param_1[0xb] + 0xce);
    *(undefined1 *)((int)puVar22 + 0xb9) = *(undefined1 *)(param_1[0xb] + 0xcf);
    *(undefined1 *)((int)puVar22 + 0xba) = *(undefined1 *)(param_1[0xb] + 0xd0);
    *(undefined1 *)(puVar22 + 0x2f) = *(undefined1 *)(param_1[0xb] + 0xd2);
    uVar4 = *(undefined1 *)(param_1[0xb] + 0xd1);
    *(undefined2 *)((int)puVar22 + 0xbe) = *(undefined2 *)(param_1[0xb] + 0xd4);
    *(undefined1 *)((int)puVar22 + 0xbb) = uVar4;
    *(undefined2 *)(puVar22 + 0x30) = *(undefined2 *)(param_1[10] + 0x10);
    *(char *)((int)puVar22 + 0xc2) = (char)*(undefined4 *)(*param_1 + 0xe0);
    *(char *)((int)puVar22 + 0xc3) = (char)*(undefined4 *)(*param_1 + 0xa4);
    puVar22 = puVar22 + 0x31;
    iVar13 = iVar16;
  } while (iVar16 != 0x310);
LAB_4379c298:
  DAT_43e9f4bc = FUN_43797344();
  if (DAT_43e9f4bc == 0) {
    iVar13 = DAT_43e9f474;
    if (DAT_43e9f3bb == '\x01') {
      iVar13 = DAT_43e9f474 + DAT_43e9f478;
    }
    FUN_43796438((1 - *(int *)param_1[1]) + iVar13);
  }
  iVar13 = 0;
  puVar22 = (undefined4 *)&DAT_43e9f46c;
  puVar20 = &DAT_43e9f388;
  piVar23 = &DAT_43e9f7dc;
  do {
    if (*piVar23 == 2) {
      FUN_43ae7558(auStack_104);
      iVar16 = FUN_43903558(auStack_104,0xe0b00,1,0,5);
      if (iVar16 == 0) {
        uVar9 = FUN_43b2a252(auStack_fc);
        FUN_439c5a04(uVar9,0,0x20);
        FUN_435a9288(auStack_dc,uVar9,uStack_f8,0);
        FUN_435a91d0(auStack_1e4);
        FUN_43a4941e(auStack_1e4,&DAT_43e9f388 + iVar13 * 0x38);
        thunk_FUN_43a49ba4(auStack_dc,auStack_1e4);
        FUN_435a91b0(auStack_1e4);
        FUN_435a922c(auStack_5c);
        FUN_43a49548(auStack_5c,&DAT_43f9a4d5 + iVar13 * 6);
        thunk_FUN_43a49ba4(auStack_dc,auStack_5c);
        FUN_435a920c(auStack_5c);
        FUN_435a9174(auStack_12c);
        FUN_43a493cc(auStack_12c,&DAT_43e9f46c + iVar13 * 0x14);
        thunk_FUN_43a49ba4(auStack_dc,auStack_12c);
        FUN_435a9154(auStack_12c);
        if (iVar21 == 0) {
          FUN_439cc9ec(auStack_340);
          FUN_43b660e0(auStack_340,&DAT_43e9f4c4 + iVar13 * 0x31);
          thunk_FUN_43a49ba4(auStack_dc,auStack_340);
          FUN_439cc9cc(auStack_340);
        }
        if (((*(uint *)(param_1[2] + 0x268) & 0x10004) == 0x10004) &&
           (iVar16 = FUN_43aea1aa(iVar13), iVar16 != 0)) {
          FUN_439cc774(auStack_98);
          iVar16 = FUN_4379b408(iVar13);
          FUN_43b65fe4(auStack_98,&DAT_43f79b86 + iVar16 * 10);
          FUN_43a49ba4(auStack_dc,auStack_98);
          FUN_439cc754(auStack_98);
        }
        if (iVar21 == 0) {
          FUN_439cc884(auStack_434);
          FUN_43b66058(auStack_434,&DAT_43e9f204);
          thunk_FUN_43a49ba4(auStack_dc,auStack_434);
          FUN_439cc864(auStack_434);
          FUN_439cc718(auStack_268);
          FUN_43b65fbc(auStack_268,&DAT_43e9f178);
          thunk_FUN_43a49ba4(auStack_dc,auStack_268);
          FUN_439cc6f8(auStack_268);
          iVar16 = FUN_4379b3f4(iVar13);
          if (iVar16 != 0) {
            FUN_439cc8e0(auStack_198);
            FUN_43b66080(auStack_198,&DAT_43f9a4ee);
            thunk_FUN_43a49ba4(auStack_dc,auStack_198);
            FUN_439cc8c0(auStack_198);
          }
        }
        iVar16 = FUN_43aea1aa(iVar13);
        if ((iVar16 != 0) &&
           ((iVar16 = FUN_4379b408(iVar13), (&DAT_43e9f0c0)[iVar16 * 0xc] == '\x02' ||
            (iVar16 = FUN_4379b408(iVar13), (&DAT_43e9f0c1)[iVar16 * 0xc] == '\x02')))) {
          FUN_439cc990(auStack_b8);
          iVar16 = FUN_4379b408(iVar13);
          FUN_43b660b6(auStack_b8,&DAT_43e9f0c0 + iVar16 * 0xc);
          thunk_FUN_43a49ba4(auStack_dc,auStack_b8);
          FUN_439cc970(auStack_b8);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if (iVar16 != 0) {
          FUN_439cc7d0(auStack_78);
          FUN_43b6600c(auStack_78,&DAT_43e9f4bc);
          thunk_FUN_43a49ba4(auStack_dc,auStack_78);
          FUN_439cc7b0(auStack_78);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if ((iVar16 != 0) && (DAT_43e9f1e8 != -1)) {
          FUN_439cca48(auStack_158);
          FUN_43b66118(auStack_158,&DAT_43e9f1e8);
          thunk_FUN_43a49ba4(auStack_dc,auStack_158);
          FUN_439cca28(auStack_158);
        }
        iVar16 = FUN_4379b3f4(iVar13);
        if ((iVar16 != 0) && (DAT_43e9f1e8 != -1)) {
          FUN_439cc93c(auStack_40);
          FUN_43b6609e(auStack_40,&DAT_43e9f7d8);
          thunk_FUN_43a49ba4(auStack_dc,auStack_40);
          if ((DAT_43e9f0bc == -1) || (DAT_43f9a51a != DAT_43e9f7d8)) {
            FUN_43901a8c(4,0x2040,DAT_43e9f1e8,DAT_43e9f7d8);
            DAT_43e9f0bc = DAT_43e9f1e8;
            DAT_43f9a51a = DAT_43e9f7d8 != 0;
          }
          FUN_439cc91c(auStack_40);
        }
        FUN_43b2a258(auStack_104,5);
        if (iVar13 == 2) {
          iVar16 = FUN_43797b24(auStack_104,0);
        }
        else if (iVar13 == 3) {
          iVar16 = FUN_43797b38(auStack_104,0);
        }
        else if (iVar13 == 1) {
          iVar16 = FUN_43797b10(auStack_104,0);
        }
        else {
          iVar16 = FUN_43797afc(auStack_104,0);
        }
        iVar26 = DAT_4402546c;
        if ((*(byte *)(DAT_4402546c + 3) & 4) != 0) {
          iVar11 = thunk_FUN_436cd00c();
          uVar9 = DAT_43e9f7ec;
          iVar11 = iVar11 - *(int *)(param_1[1] + 8);
          if (iVar13 == 2) {
            FUN_4379b300(3,9,1,&DAT_43ca5011,iVar16,iVar11,DAT_43e9f2e4);
            FUN_43902718(s_PROXY_PIN_send_err_code__d__frc__43ca5025,iVar16,iVar11,DAT_43e9f2e4);
            piVar19 = &DAT_43e9f2e4;
          }
          else if (iVar13 == 3) {
            FUN_4379b300(3,9,1,&DAT_43ca505d,iVar16,iVar11,DAT_43e9f7d4);
            FUN_43902718(s_4K_EE_PIN_send_err_code__d__frc__43ca5071,iVar16,iVar11,DAT_43e9f7d4);
            piVar19 = &DAT_43e9f7d4;
          }
          else if (iVar13 == 1) {
            FUN_4379b300(3,9,1,&DAT_43ca4fc7,iVar16,iVar11,DAT_43e9f200);
            FUN_43902718(s_REC_PIN_send_err_code__d__frc_co_43ca4fdb,iVar16,iVar11,DAT_43e9f200);
            piVar19 = &DAT_43e9f200;
          }
          else {
            uVar15 = FUN_43797344();
            FUN_4379b300(3,9,1,&DAT_43ca4f6f,iVar16,iVar11,uVar9,uVar15);
            uVar9 = DAT_43e9f7ec;
            uVar15 = FUN_43797344();
            FUN_43902718(s_EE_PIN_send_err_code__d__frc_cou_43ca4f83,iVar16,iVar11,uVar9,uVar15);
            piVar19 = &DAT_43e9f7ec;
          }
          *piVar19 = *piVar19 + 1;
        }
        iVar11 = FUN_4379b3f4(iVar13);
        if ((iVar11 != 0) && ((*(byte *)(iVar26 + 3) & 0x40) != 0)) {
          FUN_4379b300(3,9,1,&DAT_43ca50a9,iVar13,*(undefined2 *)(puVar20 + 0x20),
                       *(undefined2 *)(puVar20 + 0x22),*(undefined2 *)(puVar20 + 0x14),
                       *(undefined2 *)(puVar20 + 0x16));
          FUN_43902718(s__EE__d__Pin__vx__d__vy__d__rx__d_43ca50bd,iVar13,
                       *(undefined2 *)(puVar20 + 0x20),*(undefined2 *)(puVar20 + 0x22),
                       *(undefined2 *)(puVar20 + 0x14),*(undefined2 *)(puVar20 + 0x16));
          FUN_4379b300(3,9,1,&DAT_43ca50e6,*puVar22,puVar20[0x10],puVar22[2],puVar22[3],
                       puVar20[0x11]);
          FUN_43902718(s_CRT__d__d__TRS__d__d__DLY__d_43ca50fa,*puVar22,puVar20[0x10],puVar22[2],
                       puVar22[3],puVar20[0x11]);
        }
        iVar11 = FUN_43aea1aa(iVar13);
        if ((iVar11 != 0) && (*(char *)(iVar26 + 3) < '\0')) {
          if (iVar13 == 1) {
            FUN_4379b300(3,9,1,&DAT_43ca5117,DAT_43e9f3e0,DAT_43e9f3e2,DAT_43e9f3d4,DAT_43e9f3d6);
            pcVar10 = s__RECPin__vx__d__vy__d__rx__d__ry_43ca512b;
            uVar7 = DAT_43e9f3e0;
            uVar3 = DAT_43e9f3e2;
            uVar2 = DAT_43e9f3d4;
            uVar8 = DAT_43e9f3d6;
LAB_4379ca92:
            FUN_43902718(pcVar10,uVar7,uVar3,uVar2,uVar8);
          }
          else if (iVar13 == 2) {
            FUN_4379b300(3,9,1,&DAT_43ca5150,DAT_43e9f418,DAT_43e9f41a,DAT_43e9f40c,DAT_43e9f40e);
            pcVar10 = s__PROXYPin__vx__d__vy__d__rx__d__r_43ca5164;
            uVar7 = DAT_43e9f418;
            uVar3 = DAT_43e9f41a;
            uVar2 = DAT_43e9f40c;
            uVar8 = DAT_43e9f40e;
            goto LAB_4379ca92;
          }
          FUN_4379b300(3,9,1,&DAT_43ca50e6,*puVar22,puVar20[0x10],puVar22[2],puVar22[3],
                       puVar20[0x11]);
          FUN_43902718(s_CRT__d__d__TRS__d__d__DLY__d_43ca50fa,*puVar22,puVar20[0x10],puVar22[2],
                       puVar22[3],puVar20[0x11]);
        }
        if (iVar16 < -0x1a) {
LAB_4379cbf4:
          FUN_4379b300(3,9,1,&DAT_43ca51cd,iVar13,iVar16);
          FUN_43902718(s_SendYCPin__d__is_error__x__43ca51e1,iVar13,iVar16);
        }
        else if (-0x18 < iVar16) {
          if (iVar16 != 0) goto LAB_4379cbf4;
          iVar16 = thunk_FUN_436cd00c();
          uVar25 = iVar16 - *(int *)(param_1[1] + 8);
          if (((*(uint *)(param_1[1] + 0x24) >> 1 < uVar25) &&
              (1 < *(int *)(param_1[2] + 0x1d4) - 4U)) && (*(int *)(param_1[2] + 0x1c) != 4)) {
            uVar25 = uVar25 >> 1;
            FUN_4379b300(3,9,1,&DAT_43ca518b,uVar25,iVar13);
            FUN_43902718(s_VD_Sequence__YC_out_window_overf_43ca519f,uVar25,iVar13);
            if (DAT_43e9f468 < 5) {
              DAT_43e9f468 = DAT_43e9f468 + 1;
              FUN_43901a8c(3,4,0xffffffff,uVar25);
            }
          }
          FUN_43ae7542(auStack_104);
          FUN_43ae7542(&DAT_43e9f0d8 + iVar13 * 0x28);
          iVar16 = FUN_43aea1aa(iVar13);
          if (iVar16 != 0) {
            FUN_43ae7542(&DAT_43e9f2e8 + iVar13 * 0x28);
          }
          iVar16 = FUN_4379b3f4(iVar13);
          if (iVar16 != 0) {
            iVar16 = FUN_437973c4();
            if (iVar16 != 0) {
              iVar16 = FUN_43ae8c4a(DAT_43e9f474 - *(int *)param_1[1]);
              iVar16 = iVar16 + (uint)*(byte *)(DAT_4401f1d0 + 0x84);
              if (DAT_43e9f3bb == '\x01') {
                iVar16 = iVar16 + DAT_43e9f478;
              }
              FUN_437973f8(iVar16);
            }
            iVar16 = FUN_43797390();
            if ((iVar16 != 0) || (iVar16 = FUN_43797344(), iVar16 == 0)) {
              FUN_43901a8c(4,0x200f,0,0);
            }
            FUN_43797370();
            if (DAT_43f9a4ed == '\0') {
              FUN_43901a8c(4,0x2002,0,0);
              DAT_43f9a4ed = '\x01';
            }
          }
        }
        *piVar23 = 1;
        FUN_435a9268(auStack_dc);
      }
      else {
        FUN_4379b300(3,9,1,&DAT_43ca4f46,iVar13);
        FUN_43902718(s_Can_t_get_sds_mem__d_43ca4f5a,iVar13);
      }
      FUN_43ae7534(auStack_104);
    }
    else if ((*(byte *)(DAT_4402546c + 3) & 2) != 0) {
      iVar16 = iVar13;
      if (iVar13 == 2) {
        FUN_4379b300(3,9,1,&DAT_43ca4ed6,2);
        pcVar10 = s_PROXY_PIN_OUT_STATE_is_not_READY_43ca4eea;
      }
      else if (iVar13 == 3) {
        FUN_4379b300(3,9,1,&DAT_43ca4f0e,3);
        pcVar10 = s_4K_EE_PIN_OUT_STATE_is_not_READY_43ca4f22;
      }
      else if (iVar13 == 1) {
        FUN_4379b300(3,9,1,&DAT_43ca4ea0,1);
        pcVar10 = s_REC_PIN_OUT_STATE_is_not_READY___43ca4eb4;
      }
      else {
        FUN_4379b300(3,9,1,&DAT_43ca4e6a,0);
        pcVar10 = s_EE_PIN_OUT_STATE_is_not_READY__d_43ca4e7e;
        iVar16 = 0;
      }
      FUN_43902718(pcVar10,iVar16);
    }
    iVar13 = iVar13 + 1;
    puVar22 = puVar22 + 5;
    puVar20 = puVar20 + 0x38;
    piVar23 = piVar23 + 1;
    if (iVar13 == 4) {
      iVar21 = 0;
      do {
        FUN_43b2a296(&DAT_43e9f0d8 + iVar21 * 0x28,5);
        iVar13 = FUN_43aea1aa(iVar21);
        if (iVar13 != 0) {
          FUN_43b2a296(&DAT_43e9f2e8 + iVar21 * 0x28,5);
        }
        iVar21 = iVar21 + 1;
      } while (iVar21 != 4);
      return;
    }
  } while( true );
}


/* query "4379cdb0" */
