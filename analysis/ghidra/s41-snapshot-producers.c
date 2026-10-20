/* S41: read-only exports. */

/* 438061c4 */

undefined4 FUN_438061c4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 auStack_1c [2];
  
  iVar1 = FUN_435612d0(DAT_4380626c,auStack_1c,param_3,0);
  if (iVar1 == 0) {
    FUN_43b00b42(auStack_1c[0],DAT_4380626c);
    FUN_439c5320(auStack_1c[0],param_2,param_3);
    iVar1 = FUN_4356120c(DAT_4380626c,auStack_1c[0]);
    if (iVar1 == 0) {
      FUN_43805ea8(param_1,param_2);
      uVar2 = 1;
    }
    else {
      FUN_435612ec(DAT_4380626c,auStack_1c[0]);
      iVar3 = DAT_43806280 + 0x43806244;
      FUN_43805604(3,0xd,1,DAT_4380627c + 0x43806242,iVar1,iVar3,0x7ed);
      FUN_43902718(DAT_43806284 + 0x43806258,iVar1,iVar3,0x7ed);
      uVar2 = 0;
    }
  }
  else {
    iVar3 = DAT_43806274 + 0x438061ee;
    FUN_43805604(3,0xd,1,DAT_43806270 + 0x438061ea,iVar1,iVar3,0x7de);
    FUN_43902718(DAT_43806278 + 0x43806204,iVar1,iVar3,0x7de);
    uVar2 = 0;
  }
  return uVar2;
}


/* 43806400 */

undefined4 FUN_43806400(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 auStack_1c [2];
  
  iVar1 = FUN_435612d0(DAT_438064a8,auStack_1c,param_3,0);
  if (iVar1 == 0) {
    FUN_43b00b42(auStack_1c[0],DAT_438064ac);
    FUN_439c5320(auStack_1c[0],param_2,param_3);
    iVar1 = FUN_4356120c(DAT_438064a8,auStack_1c[0]);
    if (iVar1 == 0) {
      FUN_43805ea8(param_1,param_2);
      uVar2 = 1;
    }
    else {
      FUN_435612ec(DAT_438064a8,auStack_1c[0]);
      iVar3 = DAT_438064c0 + 0x43806480;
      FUN_43805604(3,0xd,1,DAT_438064bc + 0x4380647e,iVar1,iVar3,0x7bf);
      FUN_43902718(DAT_438064c4 + 0x43806494,iVar1,iVar3,0x7bf);
      uVar2 = 0;
    }
  }
  else {
    iVar3 = DAT_438064b4 + 0x4380642a;
    FUN_43805604(3,0xd,1,DAT_438064b0 + 0x43806426,iVar1,iVar3,0x7b0);
    FUN_43902718(DAT_438064b8 + 0x43806440,iVar1,iVar3,0x7b0);
    uVar2 = 0;
  }
  return uVar2;
}


/* 438064c8 */

undefined4 FUN_438064c8(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 auStack_1c [2];
  
  iVar1 = FUN_435612d0(DAT_43806570,auStack_1c,param_3,1);
  if (iVar1 == 0) {
    FUN_43b00b42(auStack_1c[0],DAT_43806574);
    FUN_439c5320(auStack_1c[0],param_2,param_3);
    iVar1 = FUN_4356120c(DAT_43806570,auStack_1c[0]);
    if (iVar1 == 0) {
      FUN_43805ea8(param_1,param_2);
      uVar2 = 1;
    }
    else {
      FUN_435612ec(DAT_43806570,auStack_1c[0]);
      iVar3 = DAT_43806588 + 0x43806548;
      FUN_43805604(3,0xd,1,DAT_43806584 + 0x43806546,iVar1,iVar3,0x791);
      FUN_43902718(DAT_4380658c + 0x4380655c,iVar1,iVar3,0x791);
      uVar2 = 0;
    }
  }
  else {
    iVar3 = DAT_4380657c + 0x438064f2;
    FUN_43805604(3,0xd,1,DAT_43806578 + 0x438064ee,iVar1,iVar3,0x782);
    FUN_43902718(DAT_43806580 + 0x43806508,iVar1,iVar3,0x782);
    uVar2 = 0;
  }
  return uVar2;
}


/* 43b00b42 */

void FUN_43b00b42(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + -4) = param_2;
  return;
}


/* 43795054 */

void FUN_43795054(void)

{
  int iVar1;
  int iVar2;
  undefined2 *puVar3;
  undefined1 auStack_28 [2];
  undefined2 uStack_26;
  
  iVar1 = DAT_437950b4;
  iVar2 = FUN_43819b08(4);
  if (iVar2 == 0) {
    FUN_439c5a04(auStack_28,0,0x18);
    puVar3 = *(undefined2 **)(iVar1 + 0x43795064 + DAT_437950b8);
    uStack_26 = *puVar3;
    FUN_4381a138(DAT_437950b0,auStack_28,0x18);
    FUN_43901a8c(4,0x200e,*puVar3,0);
    FUN_43901a8c(4,0x200e,**(undefined2 **)(iVar1 + 0x43795064 + DAT_437950bc),0);
    FUN_43794ce4(DAT_437950c0 + 0x437950aa);
  }
  return;
}


/* 437950c4 */

void FUN_437950c4(int param_1)

{
  int iVar1;
  undefined2 uVar2;
  int iVar3;
  undefined2 *puVar4;
  undefined1 auStack_28 [2];
  undefined2 uStack_26;
  
  iVar1 = FUN_43819b08(4);
  iVar3 = DAT_43795144 + 0x437950d6;
  if (iVar1 == 0) {
    FUN_439c5a04(auStack_28,0,0x18);
    puVar4 = *(undefined2 **)(iVar3 + DAT_43795148);
    if (param_1 == 0) {
      uVar2 = 0x3021;
    }
    else if ((param_1 == 1) || (param_1 != 2)) {
      uVar2 = 0x3020;
    }
    else {
      uVar2 = 0x3022;
    }
    *puVar4 = uVar2;
    uStack_26 = *puVar4;
    FUN_4381a138(DAT_43795140,auStack_28,0x18);
    FUN_43901a8c(4,0x200e,*puVar4,0);
    FUN_43901a8c(4,0x200e,**(undefined2 **)(iVar3 + DAT_4379514c),0);
    FUN_43794ce4(DAT_43795150 + 0x43795138);
  }
  return;
}


/* 4380e43c */

void FUN_4380e43c(int *param_1,int param_2,int param_3)

{
  char cVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  int *piVar9;
  undefined4 *puVar10;
  bool bVar11;
  short *psVar12;
  int iVar13;
  int iVar14;
  bool bVar15;
  undefined4 auStack_348 [5];
  undefined4 uStack_334;
  undefined4 uStack_330;
  undefined4 uStack_32c;
  undefined4 uStack_328;
  undefined4 uStack_324;
  undefined4 auStack_320 [5];
  undefined4 uStack_30c;
  undefined4 uStack_308;
  undefined4 uStack_304;
  undefined4 uStack_300;
  undefined4 uStack_2fc;
  undefined4 auStack_2f8 [5];
  undefined4 uStack_2e4;
  undefined4 uStack_2e0;
  undefined4 uStack_2dc;
  undefined4 uStack_2d8;
  undefined4 uStack_2d4;
  undefined4 auStack_2d0 [5];
  undefined4 uStack_2bc;
  undefined4 uStack_2b8;
  undefined4 uStack_2b4;
  undefined4 uStack_2b0;
  undefined4 uStack_2ac;
  undefined4 auStack_2a8 [5];
  undefined4 uStack_294;
  undefined4 uStack_290;
  undefined4 uStack_28c;
  undefined4 uStack_288;
  undefined4 uStack_284;
  undefined4 auStack_280 [5];
  undefined4 uStack_26c;
  undefined4 uStack_268;
  undefined4 uStack_264;
  undefined4 uStack_260;
  undefined4 uStack_25c;
  undefined4 auStack_258 [5];
  undefined4 uStack_244;
  undefined4 uStack_240;
  undefined4 uStack_23c;
  undefined4 uStack_238;
  undefined4 uStack_234;
  undefined4 auStack_230 [10];
  undefined4 auStack_208 [5];
  undefined4 auStack_1f4 [5];
  undefined4 auStack_1e0 [5];
  undefined4 auStack_1cc [5];
  undefined4 auStack_1b8 [10];
  undefined4 auStack_190 [5];
  undefined4 auStack_17c [5];
  undefined4 auStack_168 [5];
  undefined4 auStack_154 [5];
  undefined4 auStack_140 [5];
  undefined4 auStack_12c [5];
  undefined4 auStack_118 [4];
  undefined4 uStack_108;
  undefined4 uStack_104;
  undefined4 uStack_100;
  undefined4 uStack_fc;
  undefined4 uStack_f8;
  undefined4 uStack_f4;
  undefined4 auStack_f0 [4];
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined4 auStack_c8 [4];
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 auStack_a0 [4];
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 auStack_78 [4];
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 auStack_50 [4];
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  psVar12 = (short *)(DAT_4380ef3c + 0x4380e452);
  iVar8 = DAT_4380ef40 + 0x4380e45c;
  if ((*(short *)*param_1 != *psVar12) &&
     ((*(byte *)(*(int *)(iVar8 + DAT_4380ef44) + 0x2a) & 1) != 0)) {
    uVar3 = FUN_43ae0c38();
    *(undefined1 *)(DAT_4380ef48 + 0x4380e47e) = uVar3;
    *psVar12 = *(short *)*param_1;
  }
  iVar13 = *param_1;
  uVar4 = FUN_43b039e6(param_1);
  uVar4 = FUN_4380df30(iVar13,uVar4,0);
  iVar13 = param_1[2];
  iVar5 = *param_1;
  *(undefined4 *)(param_2 + 0x218) = uVar4;
  iVar13 = FUN_437c1be4(*(undefined4 *)(iVar5 + 0x2c4),*(undefined4 *)(iVar5 + 0x398),
                        *(undefined4 *)(iVar5 + 0x394),(*(byte *)(iVar13 + 0x268) & 0xf) >> 3,
                        (*(uint *)(iVar13 + 0x264) & 0xfffff) >> 0xf == 7);
  bVar11 = iVar13 == 1 || iVar13 == 3;
  bVar15 = *(int *)(*param_1 + 0x354) == 2;
  if (param_3 == 0) {
    uVar4 = FUN_437fe4f4();
    **(undefined4 **)(iVar8 + DAT_4380ef4c) = uVar4;
    uVar3 = FUN_43728564();
    *(undefined1 *)(DAT_4380ef50 + 0x4380e512) = uVar3;
  }
  iVar6 = param_1[2];
  iVar5 = *(int *)(iVar6 + 0x20c);
  switch((*(uint *)(iVar6 + 0x264) & 0xfffff) >> 0xf) {
  case 0:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_43794a44(param_1);
    if (iVar13 == 0) {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380ef58 + 0x4380e598));
      *(undefined4 *)(DAT_4380ef5c + 0x4380e5a4) = uVar4;
    }
    else {
      *(undefined4 *)(DAT_4380ef54 + 0x4380e58a) = 0xf;
    }
    piVar9 = (int *)(DAT_4380ef60 + 0x4380e5ae);
    iVar13 = FUN_4380de20(param_3,*piVar9);
    *piVar9 = iVar13;
    iVar13 = FUN_43794a44(param_1);
    if (iVar13 != 0) {
      puVar7 = auStack_348;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
      FUN_4380e2a8(&uStack_334);
      goto LAB_4380f390;
    }
    goto LAB_4380ea46;
  case 1:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    piVar9 = (int *)(DAT_4380ef6c + 0x4380e620);
    uVar3 = *(undefined1 *)(DAT_4380ef68 + 0x4380e61e);
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4380de60(param_1,bVar11,uVar3);
    *piVar9 = iVar13;
    FUN_4380dfe4(piVar9);
    iVar13 = FUN_4380de20(param_3,*piVar9);
    goto LAB_4380e772;
  case 2:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = *param_1;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4386be30(*(undefined4 *)(iVar13 + 0x2c4),*(undefined4 *)(iVar13 + 0x398),
                          *(undefined4 *)(iVar13 + 0x394),0,1);
    if ((iVar13 == 1) || (*(char *)(param_1[0x14] + 0x2c) != '\0')) {
      puVar7 = (undefined4 *)(DAT_4380ef70 + 0x4380e690);
LAB_4380e6f4:
      uVar4 = 1;
LAB_4380e6c0:
      *puVar7 = uVar4;
    }
    else {
      if (iVar13 == 2) {
        if (*(char *)(param_1[0xe] + 0x84) != '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x44);
          if (iVar13 != 0) {
            uVar4 = 0x44;
            puVar7 = (undefined4 *)(DAT_4380f424 + 0x4380f344);
            goto LAB_4380e6c0;
          }
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,3);
        if (iVar13 == 0) {
          if ((*(int *)(DAT_4380ef78 + 0x4380e6cc) != 1) &&
             (*(int *)(DAT_4380ef78 + 0x4380e6cc) != 0x30)) {
            FUN_4380e020(3,9,1,DAT_4380ef7c + 0x4380e6e2);
            FUN_43902718(DAT_4380ef80 + 0x4380e6ec);
          }
          puVar7 = (undefined4 *)(DAT_4380ef84 + 0x4380e6f6);
          goto LAB_4380e6f4;
        }
        puVar7 = (undefined4 *)(DAT_4380ef74 + 0x4380e6c0);
LAB_4380e6be:
        uVar4 = 3;
        goto LAB_4380e6c0;
      }
      if (iVar13 - 3U < 2) {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x39);
        if (iVar13 != 0) {
          uVar4 = 0x39;
          puVar7 = (undefined4 *)(DAT_4380ef88 + 0x4380e714);
          goto LAB_4380e6c0;
        }
        *(undefined4 *)(DAT_4380ef8c + 0x4380e71c) = 1;
      }
      else {
        if ((*(int *)(*(int *)(iVar8 + DAT_4380ef90) + 0x3c) == 0) &&
           (*(int *)(*param_1 + 0x2c4) != 0)) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,3);
          if (iVar13 != 0) {
            puVar7 = (undefined4 *)(DAT_4380f428 + 0x4380f34c);
            goto LAB_4380e6be;
          }
        }
        uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380ef94 + 0x4380e74e));
        *(undefined4 *)(DAT_4380ef98 + 0x4380e75a) = uVar4;
      }
    }
    piVar9 = (int *)(DAT_4380ef9c + 0x4380e764);
    uVar4 = FUN_4380de20(param_3,*piVar9);
    iVar13 = FUN_43b03958(iVar5 != 0,uVar4);
LAB_4380e772:
    *piVar9 = iVar13;
LAB_4380ea46:
    iVar13 = *param_1;
    goto LAB_4380eace;
  case 3:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      uVar4 = FUN_436d6118();
      iVar5 = FUN_43ad909c(uVar4,3);
      iVar13 = DAT_4380efa8;
      if ((iVar5 == 0) || (*(char *)(*(int *)(iVar8 + DAT_4380efa0) + 0x88) == '\x01')) {
        uVar4 = 1;
        puVar7 = (undefined4 *)(DAT_4380f42c + 0x4380f356);
      }
      else {
        uVar4 = 3;
        puVar7 = (undefined4 *)(DAT_4380efa4 + 0x4380e7cc);
      }
      *puVar7 = uVar4;
      puVar7 = (undefined4 *)(iVar13 + 0x4380e7d4);
      FUN_4380dfe4(puVar7);
      uVar4 = FUN_4380de20(param_3,*puVar7);
      *puVar7 = uVar4;
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380efac + 0x4380e7f4));
      *(undefined4 *)(DAT_4380efb0 + 0x4380e800) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380efb4 + 0x4380e810);
    goto LAB_4380eace;
  case 4:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      puVar7 = (undefined4 *)(DAT_4380efb8 + 0x4380e844);
      *puVar7 = 1;
      FUN_4380dfe4(puVar7);
      uVar4 = FUN_4380de20(param_3,*puVar7);
      *puVar7 = uVar4;
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380efbc + 0x4380e868));
      *(undefined4 *)(DAT_4380efc0 + 0x4380e874) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380efc4 + 0x4380e884);
    goto LAB_4380eace;
  case 5:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    iVar14 = *(int *)(iVar8 + DAT_4380ef44);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(iVar14 + 0x44));
    iVar13 = *param_1;
    iVar6 = param_1[3];
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar13 = FUN_4386be30(*(undefined4 *)(iVar13 + 0x2c4),*(undefined4 *)(iVar13 + 0x398),
                          *(undefined4 *)(iVar13 + 0x394),*(undefined4 *)(iVar6 + 0xc),0);
    if (iVar13 == 1) {
      iVar13 = FUN_4380dfb4(param_1[3],*(undefined1 *)(DAT_4380efc8 + 0x4380e8d2),param_3);
      if (iVar13 != 0) {
        uVar4 = FUN_4380df00();
        puVar7 = (undefined4 *)(DAT_4380efcc + 0x4380e8e4);
        goto LAB_4380e9b8;
      }
      *(undefined4 *)(DAT_4380efd0 + 0x4380e8ec) = 1;
    }
    else {
      if (iVar13 == 2) {
        if (*(char *)(param_1[0xe] + 0x84) == '\0') {
LAB_4380e90c:
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,3);
          if (iVar13 == 0) {
            if ((*(int *)(DAT_4380efd8 + 0x4380e92c) != 1) &&
               (*(int *)(DAT_4380efd8 + 0x4380e92c) != 0x30)) {
              FUN_4380e020(3,9,1,DAT_4380efdc + 0x4380e942);
              FUN_43902718(DAT_4380efe0 + 0x4380e94c);
            }
            puVar7 = (undefined4 *)(DAT_4380efe4 + 0x4380e956);
            goto LAB_4380e99c;
          }
          uVar4 = 3;
          puVar7 = (undefined4 *)(DAT_4380efd4 + 0x4380e922);
        }
        else {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x44);
          if (iVar13 == 0) goto LAB_4380e90c;
          uVar4 = 0x44;
          puVar7 = (undefined4 *)(DAT_4380f430 + 0x4380f360);
        }
      }
      else {
        if (1 < iVar13 - 3U) {
          uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380eff8 + 0x4380e9ae));
          puVar7 = (undefined4 *)(DAT_4380effc + 0x4380e9ba);
LAB_4380e9b8:
          *puVar7 = uVar4;
          goto LAB_4380e9ba;
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x39);
        if (iVar13 != 0) {
          uVar4 = 0x39;
          puVar7 = (undefined4 *)(DAT_4380efe8 + 0x4380e976);
          goto LAB_4380f35e;
        }
        iVar13 = FUN_4380dfb4(param_1[3],*(undefined1 *)(DAT_4380efec + 0x4380e984),param_3);
        if (iVar13 != 0) {
          uVar4 = FUN_4380df00();
          puVar7 = (undefined4 *)(DAT_4380eff0 + 0x4380e996);
          goto LAB_4380e9b8;
        }
        puVar7 = (undefined4 *)(DAT_4380eff4 + 0x4380e99e);
LAB_4380e99c:
        uVar4 = 1;
      }
LAB_4380f35e:
      *puVar7 = uVar4;
    }
LAB_4380e9ba:
    piVar9 = (int *)(DAT_4380f000 + 0x4380e9c4);
    uVar4 = FUN_4380de20(param_3,*piVar9);
    iVar13 = FUN_43b03958(iVar5 != 0,uVar4);
    *piVar9 = iVar13;
    if (((iVar13 != 8) && (iVar13 != 0x12)) && (iVar13 != 0x3f)) goto LAB_4380ea46;
    iVar5 = *(int *)(*param_1 + 100);
    iVar13 = FUN_437d2424();
    if (((iVar13 == 0) || (*(int *)(param_2 + 0x218) != 0)) ||
       ((iVar5 - 0x1fU < 2 || ((*(char *)(iVar14 + 0x45) != '\0' || (bVar15)))))) {
      puVar7 = auStack_2f8;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f434));
      FUN_4380e2a8(&uStack_2e4);
      piVar9 = (int *)(DAT_4380f438 + 0x4380f390);
      uStack_334 = uStack_2e4;
      uStack_330 = uStack_2e0;
      uStack_32c = uStack_2dc;
      uStack_328 = uStack_2d8;
      uStack_324 = uStack_2d4;
    }
    else {
      puVar7 = auStack_320;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f004));
      FUN_4380e2a8(&uStack_30c);
      piVar9 = (int *)(DAT_4380f008 + 0x4380ea44);
      uStack_334 = uStack_30c;
      uStack_330 = uStack_308;
      uStack_32c = uStack_304;
      uStack_328 = uStack_300;
      uStack_324 = uStack_2fc;
    }
    goto LAB_4380f390;
  case 6:
    iVar13 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar13,uVar4,*(undefined1 *)(*(int *)(iVar8 + DAT_4380ef44) + 0x44));
    iVar13 = DAT_4380ef90;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(*(int *)(iVar8 + iVar13) + 0x3c) == 0) {
      if (*(char *)(param_1[3] + 0x16) == '\x01') {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x44);
        if (iVar13 == 0) goto LAB_4380ea92;
        uVar4 = 0x44;
        puVar7 = (undefined4 *)(DAT_4380f43c + 0x4380f39c);
      }
      else {
LAB_4380ea92:
        uVar4 = 1;
        puVar7 = (undefined4 *)(DAT_4380f00c + 0x4380ea9c);
      }
      iVar13 = DAT_4380f010;
      *puVar7 = uVar4;
      FUN_4380dfe4(iVar13 + 0x4380eaa4);
    }
    else {
      uVar4 = FUN_4380de60(param_1,bVar11,*(undefined1 *)(DAT_4380f014 + 0x4380eab4));
      *(undefined4 *)(DAT_4380f018 + 0x4380eac0) = uVar4;
    }
    iVar13 = *param_1;
    piVar9 = (int *)(DAT_4380f01c + 0x4380ead0);
LAB_4380eace:
    FUN_4380e358(iVar13,bVar15,param_2 + 0x218,piVar9);
    goto LAB_4380f270;
  case 7:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(iVar6 + 0x1d4) == 3) {
        if (*(int *)(*param_1 + 0x34) == 1) {
          uVar4 = 0x22;
          puVar7 = (undefined4 *)(DAT_4380f020 + 0x4380eaf6);
        }
        else {
          uVar4 = 0x41;
          puVar7 = (undefined4 *)(DAT_4380f024 + 0x4380eb00);
        }
      }
      else if (*(int *)(*param_1 + 0x34) == 1) {
        uVar4 = 0x20;
        puVar7 = (undefined4 *)(DAT_4380f028 + 0x4380eb12);
      }
      else {
        iVar13 = *(int *)(iVar6 + 0x208);
        if (iVar13 == 1) {
          uVar4 = 0x43;
          puVar7 = (undefined4 *)(DAT_4380f02c + 0x4380eb2c);
        }
        else if (iVar13 == 2) {
          uVar4 = 0x42;
          puVar7 = (undefined4 *)(DAT_4380f030 + 0x4380eb36);
        }
        else {
          if (iVar13 == 0) {
            puVar7 = (undefined4 *)(DAT_4380f034 + 0x4380eb3e);
          }
          else {
            FUN_4380e020(3,9,1,DAT_4380f038 + 0x4380eb4e,iVar13);
            FUN_43902718(DAT_4380f03c + 0x4380eb5e,*(undefined4 *)(param_1[2] + 0x208));
            puVar7 = (undefined4 *)(DAT_4380f040 + 0x4380eb68);
          }
          uVar4 = 0x40;
        }
      }
      goto LAB_4380eafe;
    }
    if ((*(char *)(iVar6 + 0x1cc) != '\0') && ((*(byte *)(iVar6 + 0x26a) & 1) != 0)) {
      uVar4 = 0x16;
      puVar7 = (undefined4 *)(DAT_4380f044 + 0x4380eb84);
      goto LAB_4380eafe;
    }
    switch(*(undefined4 *)(iVar6 + 0x1d4)) {
    case 2:
      if (*(int *)(*param_1 + 0x548) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f04c + 0x4380ec0e);
LAB_4380ecc2:
        uVar4 = 0x20;
        break;
      }
      cVar1 = *(char *)(param_1[0xb] + 0xb1);
      if (*(int *)(iVar6 + 0x1c) == 4) {
        uVar4 = 0x13;
      }
      else if (iVar5 == 0) {
        if (iVar13 == 1) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3d);
          if (iVar13 != 0) {
            uVar4 = 0x3d;
            goto LAB_4380ec9c;
          }
        }
        else if (iVar13 == 3) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3e);
          if (iVar13 != 0) {
            uVar4 = 0x3e;
            goto LAB_4380ec9c;
          }
        }
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x10);
        if (iVar13 == 0) {
          if (cVar1 == '\0') {
            uVar4 = FUN_436d6118();
            iVar13 = FUN_43ad909c(uVar4,0x18);
            if (iVar13 != 0) {
              uVar4 = 0x18;
              goto LAB_4380ec9c;
            }
          }
          uVar4 = 5;
        }
        else {
          if (cVar1 == '\0') {
            uVar4 = FUN_436d6118();
            iVar13 = FUN_43ad909c(uVar4,0x1a);
            if (iVar13 != 0) {
              uVar4 = 0x1a;
              goto LAB_4380ec9c;
            }
          }
          uVar4 = 0x10;
        }
      }
      else {
        uVar4 = FUN_436d6118();
        iVar13 = FUN_43ad909c(uVar4,0x34);
        if (iVar13 == 0) {
          uVar4 = 0x32;
        }
        else {
          uVar4 = 0x34;
        }
      }
LAB_4380ec9c:
      *(undefined4 *)(DAT_4380f050 + 0x4380eca2) = uVar4;
      goto LAB_4380ecf0;
    case 3:
      cVar1 = *(char *)(param_1[0xb] + 0xb1);
      if (*(int *)(iVar6 + 0x1c) == 4) {
        uVar4 = 0x1f;
      }
      else if (iVar5 == 0) {
        if (iVar13 == 1) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3b);
          if (iVar13 != 0) {
            uVar4 = 0x3b;
            goto LAB_4380ebf4;
          }
        }
        else if (iVar13 == 3) {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x3c);
          if (iVar13 != 0) {
            uVar4 = 0x3c;
            goto LAB_4380ebf4;
          }
        }
        if (cVar1 == '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x19);
          if (iVar13 != 0) {
            uVar4 = 0x19;
            goto LAB_4380ebf4;
          }
        }
        uVar4 = 7;
      }
      else {
        uVar4 = 0x33;
      }
LAB_4380ebf4:
      puVar7 = (undefined4 *)(DAT_4380f048 + 0x4380ebfc);
      goto LAB_4380ecee;
    case 4:
      uVar4 = 0x12;
      puVar7 = (undefined4 *)(DAT_4380f054 + 0x4380ecac);
      break;
    case 5:
      uVar4 = 8;
      puVar7 = (undefined4 *)(DAT_4380f058 + 0x4380ecb4);
      break;
    default:
      if (*(int *)(*param_1 + 0x548) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f05c + 0x4380ecc4);
        goto LAB_4380ecc2;
      }
      if (iVar5 == 0) {
        if (*(char *)(param_1[0xb] + 0xb1) == '\0') {
          uVar4 = FUN_436d6118();
          iVar13 = FUN_43ad909c(uVar4,0x18);
          if (iVar13 != 0) {
            uVar4 = 0x18;
            goto LAB_4380ecea;
          }
        }
        uVar4 = 5;
      }
      else {
        uVar4 = 0x32;
      }
LAB_4380ecea:
      puVar7 = (undefined4 *)(DAT_4380f060 + 0x4380ecf0);
LAB_4380ecee:
      *puVar7 = uVar4;
      goto LAB_4380ecf0;
    }
LAB_4380eafe:
    *puVar7 = uVar4;
LAB_4380ecf0:
    if (*(int *)(param_1[2] + 0x1d4) - 4U < 2) {
      puVar7 = auStack_2d0;
      FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f064));
      FUN_4380e2a8(&uStack_2bc);
      piVar9 = (int *)(DAT_4380f068 + 0x4380ed28);
      uStack_334 = uStack_2bc;
      uStack_330 = uStack_2b8;
      uStack_32c = uStack_2b4;
      uStack_328 = uStack_2b0;
      uStack_324 = uStack_2ac;
    }
    else {
      iVar13 = FUN_43794a78(param_1);
      if (iVar13 == 0) {
        puVar7 = auStack_2a8;
        FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
        FUN_4380e2a8(&uStack_294);
        piVar9 = (int *)(DAT_4380f06c + 0x4380ed5c);
        uStack_334 = uStack_294;
        uStack_330 = uStack_290;
        uStack_32c = uStack_28c;
        uStack_328 = uStack_288;
        uStack_324 = uStack_284;
      }
      else {
        puVar7 = auStack_280;
        FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f070));
        FUN_4380e2a8(&uStack_26c);
        piVar9 = (int *)(DAT_4380f074 + 0x4380ed88);
        uStack_334 = uStack_26c;
        uStack_330 = uStack_268;
        uStack_32c = uStack_264;
        uStack_328 = uStack_260;
        uStack_324 = uStack_25c;
      }
    }
    goto LAB_4380f390;
  case 8:
    if (iVar5 == 1) {
      uVar4 = 0x32;
      puVar7 = (undefined4 *)(DAT_4380f078 + 0x4380ed94);
    }
    else {
      uVar4 = 5;
      puVar7 = (undefined4 *)(DAT_4380f07c + 0x4380ed9c);
    }
    *puVar7 = uVar4;
    puVar7 = auStack_258;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380ef64));
    FUN_4380e2a8(&uStack_244);
    piVar9 = (int *)(DAT_4380f080 + 0x4380edc8);
    uStack_334 = uStack_244;
    uStack_330 = uStack_240;
    uStack_32c = uStack_23c;
    uStack_328 = uStack_238;
    uStack_324 = uStack_234;
    goto LAB_4380f390;
  case 9:
    puVar7 = auStack_208;
    puVar10 = auStack_1f4;
    piVar9 = (int *)(DAT_4380f08c + 0x4380edf0);
    *piVar9 = 8;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f090));
    break;
  case 10:
    puVar7 = auStack_1e0;
    puVar10 = auStack_1cc;
    piVar9 = (int *)(DAT_4380f094 + 0x4380ee0a);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f098));
    break;
  case 0xb:
    puVar7 = auStack_230;
    puVar2 = &stack0x00000130;
    piVar9 = (int *)(DAT_4380f084 + 0x4380edd6);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f088));
    goto LAB_4380ee2e;
  case 0xc:
    puVar7 = auStack_190;
    puVar10 = auStack_17c;
    piVar9 = (int *)(DAT_4380f0a4 + 0x4380ee44);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0a8));
    break;
  case 0xd:
    puVar7 = auStack_1b8;
    puVar2 = &stack0x000001a8;
    piVar9 = (int *)(DAT_4380f09c + 0x4380ee24);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0a0));
LAB_4380ee2e:
    puVar10 = (undefined4 *)(puVar2 + -0x34c);
    FUN_43b03a2e(puVar10);
    goto LAB_4380ee88;
  case 0xe:
    puVar7 = auStack_168;
    puVar10 = auStack_154;
    piVar9 = (int *)(DAT_4380f0ac + 0x4380ee5e);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0b0));
    break;
  case 0xf:
    puVar7 = auStack_140;
    puVar10 = auStack_12c;
    piVar9 = (int *)(DAT_4380f0b4 + 0x4380ee78);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f0b8));
    break;
  case 0x10:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) == 1) {
        if (*(int *)(iVar6 + 0x208) == 1) {
          uVar4 = 0x21;
          puVar7 = (undefined4 *)(DAT_4380f0bc + 0x4380eec2);
          goto LAB_4380f10c;
        }
        FUN_4380e020(3,9,1,DAT_4380f0c0 + 0x4380eece,*(int *)(iVar6 + 0x208));
        FUN_43902718(DAT_4380f0c4 + 0x4380eedc,*(undefined4 *)(param_1[2] + 0x208));
        puVar7 = (undefined4 *)(DAT_4380f0c8 + 0x4380eee4);
      }
      else {
        FUN_4380e020(3,9,1,DAT_4380f0cc + 0x4380eef2,*(int *)(*param_1 + 0x34));
        FUN_43902718(DAT_4380f0d0 + 0x4380eefe,*(undefined4 *)(*param_1 + 0x34));
        puVar7 = (undefined4 *)(DAT_4380f0d4 + 0x4380ef06);
      }
      uVar4 = 0x21;
      goto LAB_4380f10c;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
      puVar7 = (undefined4 *)(DAT_4380f0d8 + 0x4380ef22);
      goto LAB_4380f10a;
    case 2:
      uVar4 = 0x25;
      puVar7 = (undefined4 *)(DAT_4380f0dc + 0x4380ef2a);
      break;
    case 3:
      uVar4 = 0x2b;
      puVar7 = (undefined4 *)(DAT_4380f0e0 + 0x4380ef32);
      break;
    case 4:
      uVar4 = 0x2c;
      puVar7 = (undefined4 *)(&UNK_4380ef3a + DAT_4380f0e4);
      break;
    default:
      FUN_4380e020(3,9,1,DAT_4380f3b8 + 0x4380f0f6,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(DAT_4380f3bc + 0x4380f104,*(undefined4 *)(param_1[2] + 0x208));
      puVar7 = (undefined4 *)(DAT_4380f3c0 + 0x4380f10c);
LAB_4380f10a:
      uVar4 = 0x26;
    }
LAB_4380f10c:
    *puVar7 = uVar4;
    puVar7 = auStack_118;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3c4));
    FUN_4380e2a8(&uStack_104);
    piVar9 = (int *)(DAT_4380f3c8 + 0x4380f13a);
    uStack_90 = uStack_108;
    uStack_8c = uStack_104;
    uStack_88 = uStack_100;
    uStack_84 = uStack_fc;
    uStack_80 = uStack_f8;
    uStack_7c = uStack_f4;
    goto LAB_4380f266;
  case 0x11:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) == 1) {
        puVar7 = (undefined4 *)(DAT_4380f3cc + 0x4380f152);
      }
      else {
        FUN_4380e020(3,9,1,DAT_4380f3d0 + 0x4380f160,*(int *)(*param_1 + 0x34));
        FUN_43902718(DAT_4380f3d4 + 0x4380f16c,*(undefined4 *)(*param_1 + 0x34));
        puVar7 = (undefined4 *)(DAT_4380f3d8 + 0x4380f174);
      }
      uVar4 = 0x28;
      goto LAB_4380f1c2;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
    case 2:
      puVar7 = (undefined4 *)(DAT_4380f3dc + 0x4380f18e);
      goto LAB_4380f1c0;
    case 3:
      uVar4 = 0x2d;
      puVar7 = (undefined4 *)(DAT_4380f3e0 + 0x4380f196);
      break;
    case 4:
      uVar4 = 0x2e;
      puVar7 = (undefined4 *)(DAT_4380f3e4 + 0x4380f19e);
      break;
    default:
      FUN_4380e020(3,9,1,DAT_4380f3e8 + 0x4380f1ac,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(DAT_4380f3ec + 0x4380f1ba,*(undefined4 *)(param_1[2] + 0x208));
      puVar7 = (undefined4 *)(DAT_4380f3f0 + 0x4380f1c2);
LAB_4380f1c0:
      uVar4 = 0x2a;
    }
LAB_4380f1c2:
    *puVar7 = uVar4;
    puVar7 = auStack_f0;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3c4));
    FUN_4380e2a8(&uStack_dc);
    piVar9 = (int *)(DAT_4380f3f4 + 0x4380f1f0);
    uStack_90 = uStack_e0;
    uStack_8c = uStack_dc;
    uStack_88 = uStack_d8;
    uStack_84 = uStack_d4;
    uStack_80 = uStack_d0;
    uStack_7c = uStack_cc;
    goto LAB_4380f266;
  case 0x12:
    puVar7 = auStack_c8;
    piVar9 = (int *)(DAT_4380f3f8 + 0x4380f202);
    *piVar9 = 1;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f3fc));
    FUN_4380e2a8(&uStack_b4);
    uStack_90 = uStack_b8;
    uStack_8c = uStack_b4;
    uStack_88 = uStack_b0;
    uStack_84 = uStack_ac;
    uStack_80 = uStack_a8;
    uStack_7c = uStack_a4;
    goto LAB_4380f266;
  default:
    puVar7 = auStack_a0;
    piVar9 = (int *)(DAT_4380f400 + 0x4380f23c);
    *piVar9 = 0x11;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f404));
    FUN_43b03a2e(&uStack_8c);
    goto LAB_4380f266;
  }
  FUN_4380e2a8(puVar10);
LAB_4380ee88:
  uStack_334 = *puVar10;
  uStack_330 = puVar10[1];
  uStack_32c = puVar10[2];
  uStack_328 = puVar10[3];
  uStack_324 = puVar10[4];
LAB_4380f390:
  uStack_90 = puVar7[4];
  uStack_8c = uStack_334;
  uStack_88 = uStack_330;
  uStack_84 = uStack_32c;
  uStack_80 = uStack_328;
  uStack_7c = uStack_324;
LAB_4380f266:
  FUN_4380e2e8(*puVar7,puVar7[1],puVar7[2],puVar7[3],uStack_90,uStack_8c,uStack_88,uStack_84,
               uStack_80,uStack_7c,piVar9);
LAB_4380f270:
  if ((*(char *)(*(int *)(iVar8 + DAT_4380f408) + 3) == '\0') &&
     (*(char *)(param_1[3] + 0x10) == '\0')) {
    if (*(char *)(param_1[0x14] + 0x2d) == '\0') goto LAB_4380f302;
    puVar7 = auStack_50;
    puVar10 = (undefined4 *)(DAT_4380f414 + 0x4380f2ce);
    *puVar10 = 5;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f410));
    FUN_4380e2a8(&uStack_3c);
    uStack_68 = uStack_40;
    uStack_64 = uStack_3c;
    uStack_60 = uStack_38;
    uStack_5c = uStack_34;
    uStack_58 = uStack_30;
    uStack_54 = uStack_2c;
  }
  else {
    puVar7 = auStack_78;
    puVar10 = (undefined4 *)(DAT_4380f40c + 0x4380f28c);
    *puVar10 = 9;
    FUN_43afb46a(puVar7,*(undefined4 *)(iVar8 + DAT_4380f410));
    FUN_4380e2a8(&uStack_64);
  }
  FUN_4380e2e8(*puVar7,puVar7[1],puVar7[2],puVar7[3],uStack_68,uStack_64,uStack_60,uStack_5c,
               uStack_58,uStack_54,puVar10);
LAB_4380f302:
  iVar13 = *(int *)(DAT_4380f418 + 0x4380f308);
  if (((iVar13 == 0x12) || (iVar13 == 0x3f)) || (iVar13 == 8)) {
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  *(undefined4 *)(DAT_4380f41c + 0x4380f338) = uVar4;
  if ((*(int *)(*param_1 + 0x80) == 1) && (iVar13 == 3)) {
    **(undefined4 **)(iVar8 + DAT_4380f420) = 1;
  }
  else {
    **(undefined4 **)(iVar8 + DAT_4380f420) = 0;
  }
  return;
}


/* 43796954 */

undefined2 FUN_43796954(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  char cVar7;
  int iVar8;
  undefined2 *puVar9;
  int *piVar10;
  undefined4 *puVar11;
  int iVar12;
  byte bVar13;
  bool bVar14;
  undefined1 auStack_3c [24];
  
  uVar3 = FUN_43799f3c();
  iVar12 = DAT_43797014 + 0x43796970;
  if ((*(short *)*param_3 == 0x138) || (*(short *)*param_3 == 0x144)) {
    iVar4 = FUN_43799f88(uVar3,1);
    if (iVar4 == 0) {
      FUN_4379a140(uVar3,1);
    }
    iVar4 = FUN_43799f88(uVar3,0);
    if (iVar4 == 0) {
      FUN_4379a140(uVar3,0);
    }
    iVar4 = FUN_43799f88(uVar3,4);
    if (iVar4 == 0) {
      FUN_4379a140(uVar3,4);
    }
    iVar4 = FUN_43799f88(uVar3,5);
    if (iVar4 == 0) {
      FUN_4379a140(uVar3,5);
    }
  }
  if (((*(byte *)(param_3[2] + 0x268) & 2) == 0) || (iVar4 = FUN_43ae916c(), iVar4 != 0)) {
    bVar14 = false;
  }
  else {
    bVar14 = true;
  }
  iVar4 = param_3[2];
  bVar1 = *(byte *)(iVar4 + 0x268);
  bVar13 = bVar1 & 2;
  if ((bVar1 & 2) != 0) {
    if ((*(ushort *)(iVar4 + 0x264) & 0x1c0) == 0) {
      bVar13 = *(int *)(iVar4 + 0x1c) == 4;
    }
    else {
      bVar13 = 0;
    }
  }
  if (((bVar1 & 4) == 0) || (iVar4 = FUN_43ae916c(), iVar4 != 0)) {
    iVar4 = 0;
  }
  else {
    iVar4 = 1;
  }
  iVar8 = *(int *)(iVar12 + DAT_43797018);
  if (((*(char *)(iVar8 + 0x4a) != '\0') && (*(int *)(*param_3 + 0xb8) == 1)) &&
     (*(int *)(*param_3 + 0xb4) - 1U < 2)) {
    if (bVar14 != false) {
      bVar14 = (*(byte *)(param_3[2] + 0x220) & 3) == 2;
    }
    if ((iVar4 != 0) && ((*(byte *)(param_3[2] + 0x220) & 5) != 4)) {
      iVar4 = 0;
    }
  }
  iVar5 = FUN_437286bc();
  bVar1 = *(byte *)(iVar8 + 10);
  if (iVar5 == 0) {
    bVar14 = false;
  }
  if ((bVar1 & 1) == 0) {
    if ((bVar1 & 2) != 0) {
      bVar14 = true;
    }
  }
  else {
    bVar14 = false;
  }
  if ((bVar1 & 4) == 0) {
    if ((bVar1 & 8) != 0) {
      bVar13 = 1;
    }
  }
  else {
    bVar13 = 0;
  }
  if ((bVar1 & 0xf0) == 0x10) {
    iVar4 = 0;
  }
  else if ((bVar1 & 0xf0) == 0x20) {
    iVar4 = 1;
  }
  iVar5 = FUN_43ae916c();
  if (iVar5 == 0) {
    FUN_4379bb68(0,bVar14);
    FUN_4379bb68(1,iVar4);
    FUN_4379bb68(2,iVar4);
    FUN_4379bb68(3,bVar13);
  }
  if (param_1 == 0) {
    iVar4 = FUN_437999e4(1,1);
    if (((iVar4 != 0) || (iVar4 = FUN_437999e4(1,2), iVar4 != 0)) &&
       ((iVar4 = FUN_43ae8c4a(*(int *)(DAT_43797020 + 0x43796b24) + 1), iVar4 == *(int *)param_3[1]
        && (((piVar10 = (int *)(DAT_43797024 + 0x43796b3a), *piVar10 != iVar4 &&
             (iVar4 = FUN_43794a44(param_3), iVar4 == 0)) && (*(int *)(param_3[2] + 0xd8) != 1))))))
    {
      puVar11 = (undefined4 *)(DAT_43797028 + 0x43796b60);
      FUN_437961d8(3,9,1,DAT_4379702c + 0x43796b76,*(undefined4 *)param_3[1],
                   ((undefined4 *)param_3[1])[2],*piVar10,*puVar11);
      FUN_43902718(DAT_43797030 + 0x43796b86,*(undefined4 *)param_3[1],((undefined4 *)param_3[1])[2]
                   ,*piVar10,*puVar11);
      FUN_437964d4();
    }
  }
  else if ((*(byte *)(param_3[2] + 0x268) & 8) == 0) {
    FUN_43b04914(DAT_4379701c + 0x43796b02);
  }
  if (*(int *)(param_3[2] + 0x2c) != 0) {
    FUN_43796284(param_3 + 2,param_1);
  }
  iVar4 = FUN_43798414();
  if (((iVar4 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar4 = FUN_437999e4(1,5), iVar4 != 0)) {
    FUN_43b0417e(1,0xffffffff,0,0);
    FUN_43b0417e(2,0xffffffff,0,0);
    FUN_437961d8(3,9,1,DAT_43797034 + 0x43796be2);
    FUN_43902718(DAT_43797038 + 0x43796bec);
  }
  iVar4 = FUN_43798434();
  if (((iVar4 != 0) && (*(int *)(param_3[2] + 0x2c) != 0)) &&
     (iVar4 = FUN_437999e4(1,0xb), iVar4 != 0)) {
    FUN_43b0419c(0,0);
    FUN_437961d8(3,9,1,DAT_4379703c + 0x43796c1a);
    FUN_43902718(DAT_43797040 + 0x43796c24);
  }
  if (param_2 != 0) {
    if (*(int *)(param_3[2] + 0x44) != 0x11) {
      FUN_43ae9786(auStack_3c,*(undefined4 *)(iVar12 + DAT_43797044));
      FUN_43796910(0,auStack_3c,param_3[2] + 0xb8);
      FUN_43795b10();
    }
    uVar6 = FUN_4380d708(param_2 + 0x18,param_2 + 0x2c,0);
    iVar12 = FUN_4381bd4c(param_2,uVar6,(uint)*(byte *)(param_3[2] + 0x30) << 8);
    if (iVar12 != 0) {
      FUN_43b04730();
    }
  }
  FUN_4381bf38(DAT_43797048 + 0x43796c7c);
  FUN_43797410();
  iVar12 = FUN_4379742c();
  if (iVar12 != 0) {
    FUN_4372a540(7);
  }
  iVar12 = FUN_43ae916c();
  if (iVar12 == 0) {
    FUN_4379bb90(param_3);
  }
  puVar9 = (undefined2 *)*param_3;
  uVar2 = *puVar9;
  switch(uVar2) {
  case 0x100:
  case 0x101:
  case 0x10e:
  case 0x110:
  case 0x14a:
    goto switchD_43796ca8_caseD_100;
  default:
    if ((*(char *)(param_3[2] + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) {
      return uVar2;
    }
    break;
  case 0x104:
  case 0x141:
    iVar12 = FUN_437284b4();
    goto LAB_43796f38;
  case 0x105:
  case 0x106:
    if (((*(char *)(param_3[2] + 0x1ed) != '\0') &&
        (*(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4))) &&
       ((iVar12 = FUN_43ae916c(), iVar12 == 0 || (iVar12 = FUN_43795b04(), iVar12 != 0)))) {
      puVar9 = (undefined2 *)*param_3;
      if ((*(int *)(puVar9 + 0x5a) == 2) &&
         (iVar12 = param_3[2], (ushort)(*(short *)(iVar12 + 0x224) - 0x100U) < 2))
      goto LAB_43796ea8;
      goto LAB_43796fc0;
    }
    break;
  case 0x10d:
  case 0x132:
    iVar12 = FUN_437fe4f4();
    if ((iVar12 == 0) && (*(char *)(param_3[2] + 0x1ed) != '\0')) {
      bVar14 = *(int *)(param_3[1] + 0x10) == *(int *)(param_3[2] + 0x1d4);
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
    iVar12 = param_3[2];
    if (*(char *)(iVar12 + 0x23c) != '\0') {
      return 0x10f;
    }
    goto LAB_43796fda;
  case 0x112:
    iVar12 = FUN_437fe50c();
    goto LAB_43796f38;
  case 0x121:
    iVar12 = FUN_4379ada0();
    bVar14 = iVar12 == 7;
    goto LAB_43796fbc;
  case 0x123:
  case 0x128:
    iVar12 = FUN_4379ad7c();
    if (iVar12 == 0) {
LAB_43796dae:
      FUN_4379a898();
      iVar12 = FUN_43ae9674();
      if (iVar12 == 0) {
        iVar12 = FUN_4379a898();
        iVar12 = FUN_43ae9674(iVar12 + 0x28);
        goto LAB_43796f38;
      }
    }
    break;
  case 0x124:
    iVar12 = FUN_4379ada0();
    bVar14 = iVar12 == 5;
LAB_43796fbc:
    if (!bVar14) break;
    goto LAB_43796fbe;
  case 0x125:
    iVar12 = FUN_4379ad7c();
    if ((iVar12 != 0) && (iVar12 = FUN_4379ad88(), iVar12 == 1)) goto LAB_43796dae;
    break;
  case 0x126:
    iVar12 = FUN_4379ad7c();
    if ((iVar12 != 0) && (iVar12 = FUN_4379ad88(), iVar12 == 1)) {
      FUN_4379a898();
      iVar12 = FUN_43ae9674();
      if (iVar12 == 0) {
        iVar12 = FUN_4379a898();
        iVar12 = FUN_43ae9674(iVar12 + 0x28);
        if (iVar12 == 0) {
          iVar12 = FUN_4379a320();
          cVar7 = *(char *)(iVar12 + 0xac0);
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
    iVar12 = FUN_4379a320();
    cVar7 = *(char *)(iVar12 + 0xab2);
    goto LAB_43796f7c;
  case 299:
    iVar12 = FUN_4379a320();
    cVar7 = *(char *)(iVar12 + 0xab3);
    goto LAB_43796f7c;
  case 300:
    iVar12 = FUN_4379a320();
    cVar7 = *(char *)(iVar12 + 0xab4);
LAB_43796f7c:
    if (cVar7 == '\0') break;
    goto LAB_43796fbe;
  case 0x138:
  case 0x144:
    iVar12 = FUN_43799f88(uVar3,1);
    if (((iVar12 != 0) && (iVar12 = FUN_43799f88(uVar3,0), iVar12 != 0)) &&
       (iVar12 = FUN_43799f88(uVar3,4), iVar12 != 0)) {
      iVar12 = FUN_43799f88(uVar3,5);
      goto LAB_43796fa0;
    }
    break;
  case 0x139:
  case 0x145:
    if (*(char *)(param_3[2] + 0x1ed) != '\0') {
      if (1 < *(int *)(param_3[1] + 0x10) - 2U) {
        return uVar2;
      }
      if (*(int *)(param_3[1] + 0xc) == 1) {
        return uVar2;
      }
      if (1 < *(uint *)(param_3[2] + 0x3c)) {
        return uVar2;
      }
    }
    break;
  case 0x13a:
  case 0x146:
    iVar12 = FUN_43799f88(uVar3,4);
    goto LAB_43796f38;
  case 0x13b:
  case 0x13f:
switchD_43796ca8_caseD_13b:
    iVar12 = FUN_437dfeb4(uVar2);
LAB_43796fa0:
    if (iVar12 == 0) break;
    goto LAB_43796fbe;
  case 0x13c:
    if (*(char *)(param_3[0x15] + 9) == '\x01') {
      return 0x13c;
    }
    break;
  case 0x13d:
    if ((((*(char *)param_3[5] != '\0') || (*(int *)((char *)param_3[5] + 4) == 0)) ||
        (*(int *)(param_3[2] + 0x248) != 0)) || (*(char *)(iVar8 + 0xec) != '\0')) {
      uVar2 = 0x13d;
      goto switchD_43796ca8_caseD_13b;
    }
    break;
  case 0x13e:
    iVar12 = FUN_437dfa2c();
LAB_43796f38:
    if (iVar12 == 0) {
LAB_43796fbe:
      puVar9 = (undefined2 *)*param_3;
LAB_43796fc0:
      return *puVar9;
    }
    break;
  case 0x142:
    iVar12 = param_3[2];
    if ((*(char *)(iVar12 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar12 + 0x1d4))) {
      if ((*(char *)(iVar8 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar12 + 0x220) & 3) == 2)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x142;
        }
        if (*(short *)(iVar12 + 0x240) == 0x142) {
          return 0x142;
        }
      }
LAB_43796ea8:
      return *(undefined2 *)(iVar12 + 0x26c);
    }
    break;
  case 0x143:
    iVar12 = param_3[2];
    if ((*(char *)(iVar12 + 0x1ed) != '\0') &&
       (*(int *)(param_3[1] + 0x10) == *(int *)(iVar12 + 0x1d4))) {
      if ((*(char *)(iVar8 + 0x4a) == '\0') ||
         ((*(int *)(puVar9 + 0x5a) != 1 || ((*(byte *)(iVar12 + 0x220) & 5) == 4)))) {
        if (*(int *)(puVar9 + 0x5a) != 1) {
          return 0x143;
        }
        if (*(short *)(iVar12 + 0x240) == 0x143) {
          return 0x143;
        }
      }
      goto LAB_43796ea8;
    }
  }
  iVar12 = param_3[2];
LAB_43796fda:
  uVar2 = *(undefined2 *)(iVar12 + 0x26c);
switchD_43796ca8_caseD_100:
  return uVar2;
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

