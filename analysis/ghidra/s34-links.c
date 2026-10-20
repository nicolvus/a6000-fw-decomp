/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43796690" */

void FUN_437965ec(int param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_43ae916c();
  if (iVar1 != 0) {
    FUN_4379bb68(0,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 3) >> 1);
    FUN_4379bb68(1,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 7) >> 2);
    FUN_4379bb68(2,(*(byte *)(*(int *)(param_3 + 8) + 0x268) & 7) >> 2);
    FUN_4379bb68(3,0);
  }
  if (param_1 != 0) {
    FUN_43b04914(&DAT_43e9d810);
  }
  if (*(int *)(*(int *)(param_3 + 8) + 0x2c) == 0) {
    FUN_43796284(param_3 + 8,param_1);
  }
  if (param_2 != 0) {
    if (*(int *)(*(int *)(param_3 + 8) + 0x44) != 0x11) {
      FUN_43795d44(*(int *)(param_3 + 8) + 0xb8);
    }
    uVar2 = FUN_4380d708(param_2 + 0x18,param_2 + 0x2c,0);
    iVar1 = FUN_4381bd4c(param_2,uVar2,
                         (uint)*(byte *)(*(int *)(param_3 + 8) + 0x30) * 0x100 +
                         (uint)*(byte *)(*(int *)(param_3 + 0x20) + 1));
    if (iVar1 != 0) {
      FUN_43b04730();
    }
  }
  FUN_4381bf38(&DAT_43e9d810);
  return;
}


/* query "436d47e0" */

undefined4 FUN_43ad6d74(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  undefined4 extraout_r2;
  int extraout_r3;
  undefined4 extraout_r3_00;
  undefined4 extraout_r3_01;
  undefined4 uVar4;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  uint uVar5;
  undefined4 unaff_r6;
  
  piVar2 = (int *)FUN_436d41e0();
  if (piVar2 == (int *)0x0) {
    uVar1 = 3;
  }
  else {
    iVar3 = FUN_436d02cc();
    uVar4 = extraout_r3_00;
    if ((iVar3 == 0) ||
       (iVar3 = FUN_43ad6ca2(piVar2), uVar1 = 0, uVar4 = extraout_r3_01, iVar3 != 0)) {
      uVar1 = FUN_436d039c();
      FUN_436d5478(uVar1,piVar2);
      iVar3 = *piVar2;
      if (iVar3 != param_1) {
        return 3;
      }
      uVar1 = 0xffffff;
      if (iVar3 == 0xffffff) {
        uVar1 = 3;
      }
      else {
        if (param_2 != 0) {
          iVar3 = FUN_43ad8be4(piVar2,0,0xffffff,iVar3,uVar4,unaff_r4,unaff_r5,unaff_r6);
          if (iVar3 == 0) {
            uVar5 = 0;
          }
          else {
            uVar5 = 0x10;
          }
          iVar3 = FUN_43ad8be4(piVar2,1);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 0x20;
          }
          iVar3 = FUN_43ad87c4(piVar2,0);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 1;
          }
          iVar3 = FUN_43ad87c4(piVar2,1);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 2;
          }
          FUN_436cfae0(uVar5,param_2);
          uVar1 = extraout_r2;
          iVar3 = extraout_r3;
        }
        iVar3 = FUN_43ad8be4(piVar2,0,uVar1,iVar3,uVar4,unaff_r4,unaff_r5,unaff_r6);
        if (iVar3 != 0) {
          FUN_43ad828c(DAT_44023400);
        }
        iVar3 = FUN_43ad8be4(piVar2,1);
        if (iVar3 != 0) {
          FUN_43ad828c(DAT_44024d10);
        }
        iVar3 = FUN_43ad87e0(piVar2,0);
        if (iVar3 != 0) {
          FUN_43ad8036(DAT_4402500c);
        }
        iVar3 = FUN_43ad87c4(piVar2,0);
        if (iVar3 != 0) {
          FUN_43ad79ae(DAT_44021914);
        }
        iVar3 = FUN_43ad87c4(piVar2,1);
        uVar1 = 0;
        if (iVar3 != 0) {
          FUN_43ad79ae(DAT_4402603c);
          return 0;
        }
      }
      return uVar1;
    }
  }
  return uVar1;
}


/* query "43ad6d74" */

undefined4 FUN_43ad6d74(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  undefined4 extraout_r2;
  int extraout_r3;
  undefined4 extraout_r3_00;
  undefined4 extraout_r3_01;
  undefined4 uVar4;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  uint uVar5;
  undefined4 unaff_r6;
  
  piVar2 = (int *)FUN_436d41e0();
  if (piVar2 == (int *)0x0) {
    uVar1 = 3;
  }
  else {
    iVar3 = FUN_436d02cc();
    uVar4 = extraout_r3_00;
    if ((iVar3 == 0) ||
       (iVar3 = FUN_43ad6ca2(piVar2), uVar1 = 0, uVar4 = extraout_r3_01, iVar3 != 0)) {
      uVar1 = FUN_436d039c();
      FUN_436d5478(uVar1,piVar2);
      iVar3 = *piVar2;
      if (iVar3 != param_1) {
        return 3;
      }
      uVar1 = 0xffffff;
      if (iVar3 == 0xffffff) {
        uVar1 = 3;
      }
      else {
        if (param_2 != 0) {
          iVar3 = FUN_43ad8be4(piVar2,0,0xffffff,iVar3,uVar4,unaff_r4,unaff_r5,unaff_r6);
          if (iVar3 == 0) {
            uVar5 = 0;
          }
          else {
            uVar5 = 0x10;
          }
          iVar3 = FUN_43ad8be4(piVar2,1);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 0x20;
          }
          iVar3 = FUN_43ad87c4(piVar2,0);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 1;
          }
          iVar3 = FUN_43ad87c4(piVar2,1);
          if (iVar3 != 0) {
            uVar5 = uVar5 | 2;
          }
          FUN_436cfae0(uVar5,param_2);
          uVar1 = extraout_r2;
          iVar3 = extraout_r3;
        }
        iVar3 = FUN_43ad8be4(piVar2,0,uVar1,iVar3,uVar4,unaff_r4,unaff_r5,unaff_r6);
        if (iVar3 != 0) {
          FUN_43ad828c(DAT_44023400);
        }
        iVar3 = FUN_43ad8be4(piVar2,1);
        if (iVar3 != 0) {
          FUN_43ad828c(DAT_44024d10);
        }
        iVar3 = FUN_43ad87e0(piVar2,0);
        if (iVar3 != 0) {
          FUN_43ad8036(DAT_4402500c);
        }
        iVar3 = FUN_43ad87c4(piVar2,0);
        if (iVar3 != 0) {
          FUN_43ad79ae(DAT_44021914);
        }
        iVar3 = FUN_43ad87c4(piVar2,1);
        uVar1 = 0;
        if (iVar3 != 0) {
          FUN_43ad79ae(DAT_4402603c);
          return 0;
        }
      }
      return uVar1;
    }
  }
  return uVar1;
}


/* query "436cfbcc" */

void FUN_436cfbcc(undefined4 param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = DAT_44024944;
  if ((*(byte *)(DAT_44024944 + 0xf) & 1) != 0) {
    FUN_436cf6d4(0x165,1,1,&DAT_43c920be,param_1);
    FUN_43902718(s_clearComplexCallBack__x_43c920c9,param_1);
  }
  iVar3 = 0;
  uVar2 = FUN_43ad68e0(param_1);
  iVar4 = 0;
  FUN_43560e1c(0x16);
  do {
    if ((uVar2 & *(uint *)((int)&DAT_43e7ec28 + iVar3)) != 0) {
      FUN_436cf91c();
      *(undefined4 *)((int)&DAT_43e7ec28 + iVar3) = 0;
      *(undefined4 *)((int)&DAT_43e7ec2c + iVar3) = 0;
      if ((*(byte *)(iVar1 + 0xf) & 1) != 0) {
        FUN_436cf6d4(0x165,1,1,&DAT_43c920e1,param_1,iVar4,uVar2);
        FUN_43902718(s_clearComplexCallBack_cond__x_No__43c920ec,param_1,iVar4,uVar2);
      }
    }
    iVar4 = iVar4 + 1;
    iVar3 = iVar3 + 8;
  } while (iVar4 != 4);
  FUN_43560e38(0x16);
  return;
}


/* query "436cf7dc" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf7dc(undefined4 param_1)

{
  _DAT_fc0a0014 = param_1;
  return;
}


/* query "436cf7d0" */

/* query "4380e358" */

void FUN_4380e358(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 auStack_68 [4];
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 auStack_40 [4];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  iVar3 = *(int *)(param_1 + 100);
  iVar1 = FUN_437d2424();
  if ((((iVar1 == 0) || (*param_3 != 0)) || (iVar3 - 0x1fU < 2)) ||
     ((param_2 != 0 || (*(char *)(DAT_4401f1d0 + 0x45) != '\0')))) {
    puVar2 = auStack_40;
    FUN_43afb46a(puVar2,DAT_44020064);
    FUN_4380e2a8(&uStack_2c);
    uStack_58 = uStack_30;
    uStack_54 = uStack_2c;
    uStack_50 = uStack_28;
    uStack_4c = uStack_24;
    uStack_48 = uStack_20;
    uStack_44 = uStack_1c;
  }
  else {
    puVar2 = auStack_68;
    FUN_43afb46a(puVar2,DAT_44021030);
    FUN_4380e2a8(&uStack_54);
  }
  FUN_4380e2e8(*puVar2,puVar2[1],puVar2[2],puVar2[3],uStack_58,uStack_54,uStack_50,uStack_4c,
               uStack_48,uStack_44,param_4);
  return;
}


/* query "4380e43c" */

void FUN_4380e43c(int *param_1,int param_2,int param_3)

{
  char cVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  bool bVar9;
  int iVar10;
  undefined4 *puVar11;
  bool bVar12;
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
  
  if ((*(short *)*param_1 != DAT_4401d36c) && ((*(byte *)(DAT_4401f1d0 + 0x2a) & 1) != 0)) {
    DAT_43f9b2a6 = FUN_43ae0c38();
    DAT_4401d36c = *(short *)*param_1;
  }
  iVar10 = *param_1;
  uVar4 = FUN_43b039e6(param_1);
  uVar4 = FUN_4380df30(iVar10,uVar4,0);
  iVar10 = param_1[2];
  iVar5 = *param_1;
  *(undefined4 *)(param_2 + 0x218) = uVar4;
  iVar10 = FUN_437c1be4(*(undefined4 *)(iVar5 + 0x2c4),*(undefined4 *)(iVar5 + 0x398),
                        *(undefined4 *)(iVar5 + 0x394),(*(byte *)(iVar10 + 0x268) & 0xf) >> 3,
                        (*(uint *)(iVar10 + 0x264) & 0xfffff) >> 0xf == 7);
  bVar9 = iVar10 == 1 || iVar10 == 3;
  bVar12 = *(int *)(*param_1 + 0x354) == 2;
  if (param_3 == 0) {
    uVar4 = FUN_437fe4f4();
    *DAT_44025cd4 = uVar4;
    DAT_43f9b2a7 = FUN_43728564();
  }
  iVar6 = param_1[2];
  iVar5 = *(int *)(iVar6 + 0x20c);
  switch((*(uint *)(iVar6 + 0x264) & 0xfffff) >> 0xf) {
  case 0:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar10 = FUN_43794a44(param_1);
    if (iVar10 == 0) {
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
    else {
      DAT_43eea2e4 = 0xf;
    }
    DAT_43eea2e4 = FUN_4380de20(param_3,DAT_43eea2e4);
    iVar10 = FUN_43794a44(param_1);
    if (iVar10 == 0) goto LAB_4380ea46;
    puVar8 = auStack_348;
    FUN_43afb46a(puVar8,DAT_44020064);
    FUN_4380e2a8(&uStack_334);
    goto LAB_4380f390;
  case 1:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    uVar3 = DAT_43f9b2a7;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,uVar3);
    FUN_4380dfe4(&DAT_43eea2e4);
    DAT_43eea2e4 = FUN_4380de20(param_3,DAT_43eea2e4);
    goto LAB_4380ea46;
  case 2:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    iVar10 = *param_1;
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar10 = FUN_4386be30(*(undefined4 *)(iVar10 + 0x2c4),*(undefined4 *)(iVar10 + 0x398),
                          *(undefined4 *)(iVar10 + 0x394),0,1);
    if ((iVar10 == 1) || (*(char *)(param_1[0x14] + 0x2c) != '\0')) {
LAB_4380e6f4:
      DAT_43eea2e4 = 1;
    }
    else if (iVar10 == 2) {
      if (*(char *)(param_1[0xe] + 0x84) != '\0') {
        uVar4 = FUN_436d6118();
        iVar10 = FUN_43ad909c(uVar4,0x44);
        if (iVar10 != 0) {
          DAT_43eea2e4 = 0x44;
          goto LAB_4380e75a;
        }
      }
      uVar4 = FUN_436d6118();
      iVar10 = FUN_43ad909c(uVar4,3);
      if (iVar10 == 0) {
        if ((DAT_43eea2e4 != 1) && (DAT_43eea2e4 != 0x30)) {
          FUN_4380e020(3,9,1,&DAT_43cb0cd2);
          FUN_43902718(s_UnExp_LC_Req_ImgMode_43cb0ce6);
        }
        goto LAB_4380e6f4;
      }
LAB_4380e6be:
      DAT_43eea2e4 = 3;
    }
    else if (iVar10 - 3U < 2) {
      uVar4 = FUN_436d6118();
      iVar10 = FUN_43ad909c(uVar4,0x39);
      if (iVar10 == 0) {
        DAT_43eea2e4 = 1;
      }
      else {
        DAT_43eea2e4 = 0x39;
      }
    }
    else {
      if ((*(int *)(DAT_44020e90 + 0x3c) == 0) && (*(int *)(*param_1 + 0x2c4) != 0)) {
        uVar4 = FUN_436d6118();
        iVar10 = FUN_43ad909c(uVar4,3);
        if (iVar10 != 0) goto LAB_4380e6be;
      }
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
LAB_4380e75a:
    uVar4 = FUN_4380de20(param_3,DAT_43eea2e4);
    DAT_43eea2e4 = FUN_43b03958(iVar5 != 0,uVar4);
LAB_4380ea46:
    iVar10 = *param_1;
    goto LAB_4380eace;
  case 3:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(DAT_44020e90 + 0x3c) == 0) {
      uVar4 = FUN_436d6118();
      iVar10 = FUN_43ad909c(uVar4,3);
      if ((iVar10 == 0) || (*(char *)(DAT_4402546c + 0x88) == '\x01')) {
        DAT_43eea2e4 = 1;
      }
      else {
        DAT_43eea2e4 = 3;
      }
      FUN_4380dfe4(&DAT_43eea2e4);
      DAT_43eea2e4 = FUN_4380de20(param_3,DAT_43eea2e4);
    }
    else {
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
    iVar10 = *param_1;
    goto LAB_4380eace;
  case 4:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(DAT_44020e90 + 0x3c) == 0) {
      DAT_43eea2e4 = 1;
      FUN_4380dfe4(&DAT_43eea2e4);
      DAT_43eea2e4 = FUN_4380de20(param_3,DAT_43eea2e4);
    }
    else {
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
    iVar10 = *param_1;
    goto LAB_4380eace;
  case 5:
    iVar6 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    iVar10 = DAT_4401f1d0;
    uVar4 = FUN_4380df30(iVar6,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    iVar6 = *param_1;
    iVar7 = param_1[3];
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    iVar6 = FUN_4386be30(*(undefined4 *)(iVar6 + 0x2c4),*(undefined4 *)(iVar6 + 0x398),
                         *(undefined4 *)(iVar6 + 0x394),*(undefined4 *)(iVar7 + 0xc),0);
    if (iVar6 == 1) {
      iVar6 = FUN_4380dfb4(param_1[3],DAT_43f9b2a6,param_3);
      if (iVar6 == 0) {
        DAT_43eea2e4 = 1;
      }
      else {
        DAT_43eea2e4 = FUN_4380df00();
      }
    }
    else if (iVar6 == 2) {
      if (*(char *)(param_1[0xe] + 0x84) != '\0') {
        uVar4 = FUN_436d6118();
        iVar6 = FUN_43ad909c(uVar4,0x44);
        if (iVar6 != 0) {
          DAT_43eea2e4 = 0x44;
          goto LAB_4380e9ba;
        }
      }
      uVar4 = FUN_436d6118();
      iVar6 = FUN_43ad909c(uVar4,3);
      if (iVar6 == 0) {
        if ((DAT_43eea2e4 != 1) && (DAT_43eea2e4 != 0x30)) {
          FUN_4380e020(3,9,1,&DAT_43cb0cd2);
          FUN_43902718(s_UnExp_LC_Req_ImgMode_43cb0ce6);
        }
LAB_4380e99c:
        DAT_43eea2e4 = 1;
      }
      else {
        DAT_43eea2e4 = 3;
      }
    }
    else if (iVar6 - 3U < 2) {
      uVar4 = FUN_436d6118();
      iVar6 = FUN_43ad909c(uVar4,0x39);
      if (iVar6 == 0) {
        iVar6 = FUN_4380dfb4(param_1[3],DAT_43f9b2a6,param_3);
        if (iVar6 == 0) goto LAB_4380e99c;
        DAT_43eea2e4 = FUN_4380df00();
      }
      else {
        DAT_43eea2e4 = 0x39;
      }
    }
    else {
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
LAB_4380e9ba:
    uVar4 = FUN_4380de20(param_3,DAT_43eea2e4);
    DAT_43eea2e4 = FUN_43b03958(iVar5 != 0,uVar4);
    if (((DAT_43eea2e4 != 8) && (DAT_43eea2e4 != 0x12)) && (DAT_43eea2e4 != 0x3f))
    goto LAB_4380ea46;
    iVar6 = *(int *)(*param_1 + 100);
    iVar5 = FUN_437d2424();
    if (((iVar5 == 0) || (*(int *)(param_2 + 0x218) != 0)) ||
       ((iVar6 - 0x1fU < 2 || ((*(char *)(iVar10 + 0x45) != '\0' || (bVar12)))))) {
      puVar8 = auStack_2f8;
      FUN_43afb46a(puVar8,DAT_44023410);
      FUN_4380e2a8(&uStack_2e4);
      uStack_334 = uStack_2e4;
      uStack_330 = uStack_2e0;
      uStack_32c = uStack_2dc;
      uStack_328 = uStack_2d8;
      uStack_324 = uStack_2d4;
    }
    else {
      puVar8 = auStack_320;
      FUN_43afb46a(puVar8,DAT_44024fdc);
      FUN_4380e2a8(&uStack_30c);
      uStack_334 = uStack_30c;
      uStack_330 = uStack_308;
      uStack_32c = uStack_304;
      uStack_328 = uStack_300;
      uStack_324 = uStack_2fc;
    }
    goto LAB_4380f390;
  case 6:
    iVar10 = *param_1;
    uVar4 = FUN_43b039e6(param_1);
    uVar4 = FUN_4380df30(iVar10,uVar4,*(undefined1 *)(DAT_4401f1d0 + 0x44));
    *(undefined4 *)(param_2 + 0x218) = uVar4;
    if (*(int *)(DAT_44020e90 + 0x3c) == 0) {
      if (*(char *)(param_1[3] + 0x16) == '\x01') {
        uVar4 = FUN_436d6118();
        iVar10 = FUN_43ad909c(uVar4,0x44);
        if (iVar10 == 0) goto LAB_4380ea92;
        DAT_43eea2e4 = 0x44;
      }
      else {
LAB_4380ea92:
        DAT_43eea2e4 = 1;
      }
      FUN_4380dfe4(&DAT_43eea2e4);
    }
    else {
      DAT_43eea2e4 = FUN_4380de60(param_1,bVar9,DAT_43f9b2a7);
    }
    iVar10 = *param_1;
LAB_4380eace:
    FUN_4380e358(iVar10,bVar12,param_2 + 0x218,&DAT_43eea2e4);
    goto LAB_4380f270;
  case 7:
    if (*(char *)(iVar6 + 0x21c) == '\0') {
      if ((*(char *)(iVar6 + 0x1cc) == '\0') || ((*(byte *)(iVar6 + 0x26a) & 1) == 0)) {
        switch(*(undefined4 *)(iVar6 + 0x1d4)) {
        case 2:
          if (*(int *)(*param_1 + 0x548) == 1) {
LAB_4380ecc2:
            DAT_43eea2e4 = 0x20;
          }
          else {
            cVar1 = *(char *)(param_1[0xb] + 0xb1);
            if (*(int *)(iVar6 + 0x1c) == 4) {
              DAT_43eea2e4 = 0x13;
            }
            else if (iVar5 == 0) {
              if (iVar10 == 1) {
                uVar4 = FUN_436d6118();
                iVar10 = FUN_43ad909c(uVar4,0x3d);
                if (iVar10 != 0) {
                  DAT_43eea2e4 = 0x3d;
                  break;
                }
              }
              else if (iVar10 == 3) {
                uVar4 = FUN_436d6118();
                iVar10 = FUN_43ad909c(uVar4,0x3e);
                if (iVar10 != 0) {
                  DAT_43eea2e4 = 0x3e;
                  break;
                }
              }
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x10);
              if (iVar10 == 0) {
                if (cVar1 == '\0') {
                  uVar4 = FUN_436d6118();
                  iVar10 = FUN_43ad909c(uVar4,0x18);
                  if (iVar10 != 0) {
                    DAT_43eea2e4 = 0x18;
                    break;
                  }
                }
                DAT_43eea2e4 = 5;
              }
              else {
                if (cVar1 == '\0') {
                  uVar4 = FUN_436d6118();
                  iVar10 = FUN_43ad909c(uVar4,0x1a);
                  if (iVar10 != 0) {
                    DAT_43eea2e4 = 0x1a;
                    break;
                  }
                }
                DAT_43eea2e4 = 0x10;
              }
            }
            else {
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x34);
              if (iVar10 == 0) {
                DAT_43eea2e4 = 0x32;
              }
              else {
                DAT_43eea2e4 = 0x34;
              }
            }
          }
          break;
        case 3:
          cVar1 = *(char *)(param_1[0xb] + 0xb1);
          if (*(int *)(iVar6 + 0x1c) == 4) {
            DAT_43eea2e4 = 0x1f;
          }
          else if (iVar5 == 0) {
            if (iVar10 == 1) {
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x3b);
              if (iVar10 != 0) {
                DAT_43eea2e4 = 0x3b;
                break;
              }
            }
            else if (iVar10 == 3) {
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x3c);
              if (iVar10 != 0) {
                DAT_43eea2e4 = 0x3c;
                break;
              }
            }
            if (cVar1 == '\0') {
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x19);
              if (iVar10 != 0) {
                DAT_43eea2e4 = 0x19;
                break;
              }
            }
            DAT_43eea2e4 = 7;
          }
          else {
            DAT_43eea2e4 = 0x33;
          }
          break;
        case 4:
          DAT_43eea2e4 = 0x12;
          break;
        case 5:
          DAT_43eea2e4 = 8;
          break;
        default:
          if (*(int *)(*param_1 + 0x548) == 1) goto LAB_4380ecc2;
          if (iVar5 == 0) {
            if (*(char *)(param_1[0xb] + 0xb1) == '\0') {
              uVar4 = FUN_436d6118();
              iVar10 = FUN_43ad909c(uVar4,0x18);
              if (iVar10 != 0) {
                DAT_43eea2e4 = 0x18;
                break;
              }
            }
            DAT_43eea2e4 = 5;
          }
          else {
            DAT_43eea2e4 = 0x32;
          }
        }
      }
      else {
        DAT_43eea2e4 = 0x16;
      }
    }
    else if (*(int *)(iVar6 + 0x1d4) == 3) {
      if (*(int *)(*param_1 + 0x34) == 1) {
        DAT_43eea2e4 = 0x22;
      }
      else {
        DAT_43eea2e4 = 0x41;
      }
    }
    else if (*(int *)(*param_1 + 0x34) == 1) {
      DAT_43eea2e4 = 0x20;
    }
    else {
      iVar10 = *(int *)(iVar6 + 0x208);
      if (iVar10 == 1) {
        DAT_43eea2e4 = 0x43;
      }
      else if (iVar10 == 2) {
        DAT_43eea2e4 = 0x42;
      }
      else {
        if (iVar10 != 0) {
          FUN_4380e020(3,9,1,&DAT_43cb0cfb,iVar10);
          FUN_43902718(s_2KSuperSlowMotion_error__IMAGE_F_43cb0d0f,
                       *(undefined4 *)(param_1[2] + 0x208));
        }
        DAT_43eea2e4 = 0x40;
      }
    }
    if (*(int *)(param_1[2] + 0x1d4) - 4U < 2) {
      puVar8 = auStack_2d0;
      FUN_43afb46a(puVar8,DAT_44020ae0);
      FUN_4380e2a8(&uStack_2bc);
      uStack_334 = uStack_2bc;
      uStack_330 = uStack_2b8;
      uStack_32c = uStack_2b4;
      uStack_328 = uStack_2b0;
      uStack_324 = uStack_2ac;
    }
    else {
      iVar10 = FUN_43794a78(param_1);
      if (iVar10 == 0) {
        puVar8 = auStack_2a8;
        FUN_43afb46a(puVar8,DAT_44020064);
        FUN_4380e2a8(&uStack_294);
        uStack_334 = uStack_294;
        uStack_330 = uStack_290;
        uStack_32c = uStack_28c;
        uStack_328 = uStack_288;
        uStack_324 = uStack_284;
      }
      else {
        puVar8 = auStack_280;
        FUN_43afb46a(puVar8,DAT_44020e70);
        FUN_4380e2a8(&uStack_26c);
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
      DAT_43eea2e4 = 0x32;
    }
    else {
      DAT_43eea2e4 = 5;
    }
    puVar8 = auStack_258;
    FUN_43afb46a(puVar8,DAT_44020064);
    FUN_4380e2a8(&uStack_244);
    uStack_334 = uStack_244;
    uStack_330 = uStack_240;
    uStack_32c = uStack_23c;
    uStack_328 = uStack_238;
    uStack_324 = uStack_234;
    goto LAB_4380f390;
  case 9:
    puVar8 = auStack_208;
    puVar11 = auStack_1f4;
    DAT_43eea2e4 = 8;
    FUN_43afb46a(puVar8,DAT_4401f6bc);
    break;
  case 10:
    puVar8 = auStack_1e0;
    puVar11 = auStack_1cc;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_44022478);
    break;
  case 0xb:
    puVar8 = auStack_230;
    puVar2 = &stack0x00000130;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_44023da0);
    goto LAB_4380ee2e;
  case 0xc:
    puVar8 = auStack_190;
    puVar11 = auStack_17c;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_4401f058);
    break;
  case 0xd:
    puVar8 = auStack_1b8;
    puVar2 = &stack0x000001a8;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_44023840);
LAB_4380ee2e:
    puVar11 = (undefined4 *)(puVar2 + -0x34c);
    FUN_43b03a2e(puVar11);
    goto LAB_4380ee88;
  case 0xe:
    puVar8 = auStack_168;
    puVar11 = auStack_154;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_44022d28);
    break;
  case 0xf:
    puVar8 = auStack_140;
    puVar11 = auStack_12c;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_44025204);
    break;
  case 0x10:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) == 1) {
        if (*(int *)(iVar6 + 0x208) == 1) {
          DAT_43eea2e4 = 0x21;
          goto LAB_4380f10c;
        }
        FUN_4380e020(3,9,1,&DAT_43cb0d43,*(int *)(iVar6 + 0x208));
        FUN_43902718(s_4KSuperSlowMotion_Buffering__err_43cb0d57,*(undefined4 *)(param_1[2] + 0x208)
                    );
      }
      else {
        FUN_4380e020(3,9,1,&DAT_43cb0d96,*(int *)(*param_1 + 0x34));
        FUN_43902718(s_4KSuperSlowMotion_Buffering__err_43cb0daa,*(undefined4 *)(*param_1 + 0x34));
      }
      DAT_43eea2e4 = 0x21;
      goto LAB_4380f10c;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
      goto LAB_4380f10a;
    case 2:
      DAT_43eea2e4 = 0x25;
      break;
    case 3:
      DAT_43eea2e4 = 0x2b;
      break;
    case 4:
      DAT_43eea2e4 = 0x2c;
      break;
    default:
      FUN_4380e020(3,9,1,&DAT_43cb0ded,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(s_SuperSlowMotion_Buffering__error_43cb0e01,*(undefined4 *)(param_1[2] + 0x208));
LAB_4380f10a:
      DAT_43eea2e4 = 0x26;
    }
LAB_4380f10c:
    puVar8 = auStack_118;
    FUN_43afb46a(puVar8,DAT_44021a2c);
    FUN_4380e2a8(&uStack_104);
    uStack_90 = uStack_108;
    uStack_8c = uStack_104;
    uStack_88 = uStack_100;
    uStack_84 = uStack_fc;
    uStack_80 = uStack_f8;
    uStack_7c = uStack_f4;
    goto LAB_4380f266;
  case 0x11:
    if (*(char *)(iVar6 + 0x21c) != '\0') {
      if (*(int *)(*param_1 + 0x34) != 1) {
        FUN_4380e020(3,9,1,&DAT_43cb0e3e,*(int *)(*param_1 + 0x34));
        FUN_43902718(s_4KSuperSlowMotion_Transfer__erro_43cb0e52,*(undefined4 *)(*param_1 + 0x34));
      }
      DAT_43eea2e4 = 0x28;
      goto LAB_4380f1c2;
    }
    switch(*(undefined4 *)(iVar6 + 0x208)) {
    case 1:
    case 2:
      goto LAB_4380f1c0;
    case 3:
      DAT_43eea2e4 = 0x2d;
      break;
    case 4:
      DAT_43eea2e4 = 0x2e;
      break;
    default:
      FUN_4380e020(3,9,1,&DAT_43cb0e94,*(undefined4 *)(iVar6 + 0x208));
      FUN_43902718(s_SuperSlowMotion_Transfer__error__43cb0ea8,*(undefined4 *)(param_1[2] + 0x208));
LAB_4380f1c0:
      DAT_43eea2e4 = 0x2a;
    }
LAB_4380f1c2:
    puVar8 = auStack_f0;
    FUN_43afb46a(puVar8,DAT_44021a2c);
    FUN_4380e2a8(&uStack_dc);
    uStack_90 = uStack_e0;
    uStack_8c = uStack_dc;
    uStack_88 = uStack_d8;
    uStack_84 = uStack_d4;
    uStack_80 = uStack_d0;
    uStack_7c = uStack_cc;
    goto LAB_4380f266;
  case 0x12:
    puVar8 = auStack_c8;
    DAT_43eea2e4 = 1;
    FUN_43afb46a(puVar8,DAT_4401ffa8);
    FUN_4380e2a8(&uStack_b4);
    uStack_90 = uStack_b8;
    uStack_8c = uStack_b4;
    uStack_88 = uStack_b0;
    uStack_84 = uStack_ac;
    uStack_80 = uStack_a8;
    uStack_7c = uStack_a4;
    goto LAB_4380f266;
  default:
    puVar8 = auStack_a0;
    DAT_43eea2e4 = 0x11;
    FUN_43afb46a(puVar8,DAT_4402176c);
    FUN_43b03a2e(&uStack_8c);
    goto LAB_4380f266;
  }
  FUN_4380e2a8(puVar11);
LAB_4380ee88:
  uStack_334 = *puVar11;
  uStack_330 = puVar11[1];
  uStack_32c = puVar11[2];
  uStack_328 = puVar11[3];
  uStack_324 = puVar11[4];
LAB_4380f390:
  uStack_90 = puVar8[4];
  uStack_8c = uStack_334;
  uStack_88 = uStack_330;
  uStack_84 = uStack_32c;
  uStack_80 = uStack_328;
  uStack_7c = uStack_324;
LAB_4380f266:
  FUN_4380e2e8(*puVar8,puVar8[1],puVar8[2],puVar8[3],uStack_90,uStack_8c,uStack_88,uStack_84,
               uStack_80,uStack_7c,&DAT_43eea2e4);
LAB_4380f270:
  if ((*(char *)(DAT_44024a14 + 3) == '\0') && (*(char *)(param_1[3] + 0x10) == '\0')) {
    if (*(char *)(param_1[0x14] + 0x2d) == '\0') goto LAB_4380f302;
    puVar8 = auStack_50;
    DAT_43eea2e4 = 5;
    FUN_43afb46a(puVar8,DAT_44020064);
    FUN_4380e2a8(&uStack_3c);
    uStack_68 = uStack_40;
    uStack_64 = uStack_3c;
    uStack_60 = uStack_38;
    uStack_5c = uStack_34;
    uStack_58 = uStack_30;
    uStack_54 = uStack_2c;
  }
  else {
    puVar8 = auStack_78;
    DAT_43eea2e4 = 9;
    FUN_43afb46a(puVar8,DAT_44020064);
    FUN_4380e2a8(&uStack_64);
  }
  FUN_4380e2e8(*puVar8,puVar8[1],puVar8[2],puVar8[3],uStack_68,uStack_64,uStack_60,uStack_5c,
               uStack_58,uStack_54,&DAT_43eea2e4);
LAB_4380f302:
  if (((DAT_43eea2e4 == 0x12) || (DAT_43eea2e4 == 0x3f)) || (DAT_43eea2e4 == 8)) {
    DAT_43eea2fc = 1;
  }
  else {
    DAT_43eea2fc = 0;
  }
  if ((*(int *)(*param_1 + 0x80) == 1) && (DAT_43eea2e4 == 3)) {
    *DAT_44025520 = 1;
  }
  else {
    *DAT_44025520 = 0;
  }
  return;
}


/* query "437965ac" */

void FUN_437965ac(int param_1,undefined4 param_2)

{
  undefined *puVar1;
  
  switch(param_2) {
  case 0:
    puVar1 = &DAT_43e9de14;
    break;
  case 1:
    puVar1 = &DAT_43e9d810;
    break;
  case 2:
    puVar1 = &DAT_43e9d788;
    break;
  case 3:
    puVar1 = &DAT_43e9d71c;
    break;
  default:
    puVar1 = &DAT_43e9dd24;
  }
  *(undefined **)(param_1 + 4) = puVar1;
  return;
}


/* query "43b047d0" */

void FUN_43b047d0(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_24 [24];
  
  if (*(char *)(param_1 + 0x22) == '\0') {
LAB_43b0483c:
    FUN_4381ba7c(param_1);
    return;
  }
  uVar1 = thunk_FUN_43b0478c(param_1 + 8,param_1);
  switch(uVar1) {
  case 0:
    *(char *)(param_1 + 0x23) = *(char *)(param_1 + 0x23) + '\x01';
    break;
  case 1:
    break;
  case 2:
    FUN_43560cc8(0x32);
    break;
  case 3:
  case 6:
    goto switchD_43b047ec_caseD_3;
  default:
    FUN_43b02fcc(auStack_24,0);
    iVar2 = thunk_FUN_43afb3fa(param_1 + 0x24,auStack_24);
    if ((iVar2 != 0) && (*(int *)(param_1 + 0x1c) != 0x10)) {
      thunk_FUN_43b047ae(param_1 + 0x24,param_1);
    }
  case 4:
    goto LAB_43b0483c;
  }
  (**(code **)**(undefined4 **)(param_1 + 4))(*(undefined4 **)(param_1 + 4),param_1);
switchD_43b047ec_caseD_3:
  return;
}


/* query "43b0478c" */

void FUN_43b0478c(int *param_1)

{
  int iVar1;
  code *pcVar2;
  
  iVar1 = param_1[1] >> 1;
  if ((param_1[1] & 1U) == 0) {
    pcVar2 = (code *)*param_1;
  }
  else {
    pcVar2 = *(code **)(*(int *)((int)param_1 + iVar1) + *param_1);
  }
  (*pcVar2)((int)param_1 + iVar1);
  return;
}


/* query "43afb3ba" */

void s32_candidate_43afb3ba(int param_1,undefined4 param_2)

{
  (**(code **)(param_1 + 8))(param_2);
  return;
}


/* query "43e7e934" */
