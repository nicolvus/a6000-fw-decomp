/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

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


/* query "4381bd4c" */

int * FUN_4381bd4c(int *param_1,int param_2,undefined2 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iStack_2c;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  int iStack_1c;
  
  piVar1 = (int *)FUN_43b0473e(&DAT_43eeaf5c);
  if (piVar1 == (int *)0x0) {
    if (4 < DAT_43eeaf58) {
      return (int *)0x0;
    }
    DAT_43eeaf58 = DAT_43eeaf58 + 1;
    uVar5 = DAT_43eeaf58;
    FUN_4381b9d0(5,3,1,&DAT_43cb442b,DAT_43eeaf58);
    FUN_43902718(s_Image__Create_Image_NULL__d_43cb443a,DAT_43eeaf58);
    if (DAT_43eeaf58 == 1) {
      FUN_43901a8c(3,0,0,0x2c);
    }
    if (DAT_43eeaf58 == 5) {
      FUN_4381b9d0(5,3,1,&LAB_43cb437e_1,uVar5);
      FUN_43902718(s_Image_NULL_log_end_43cb438e);
    }
  }
  else {
    *(undefined2 *)(piVar1 + 8) = param_3;
    *piVar1 = param_2;
    *(undefined1 *)((int)piVar1 + 0x23) = 0;
    *(undefined1 *)((int)piVar1 + 0x22) = 1;
    iVar2 = param_1[1];
    iVar3 = param_1[2];
    iVar4 = param_1[3];
    piVar1[2] = *param_1;
    piVar1[3] = iVar2;
    piVar1[4] = iVar3;
    piVar1[5] = iVar4;
    piVar1[6] = param_1[4];
    FUN_437965ac(piVar1,param_1[5]);
    piVar1[0xe] = 0;
    piVar1[0xf] = 0;
    FUN_43b02fcc(&iStack_2c,0);
    piVar1[9] = iStack_2c;
    piVar1[10] = iStack_28;
    piVar1[0xb] = iStack_24;
    piVar1[0xc] = iStack_20;
    piVar1[0xd] = iStack_1c;
    if (param_1[5] == 4) {
      piVar1[7] = 5;
    }
    else {
      piVar1[7] = 0;
    }
    if (*piVar1 != 0) {
      return piVar1;
    }
    if (DAT_43eeaf58 < 5) {
      DAT_43eeaf58 = DAT_43eeaf58 + 1;
      uVar5 = DAT_43eeaf58;
      FUN_4381b9d0(5,3,1,&DAT_43cb4456,DAT_43eeaf58);
      FUN_43902718(s_Image__Create_ImageParam_NULL__d_43cb4465,DAT_43eeaf58);
      if (DAT_43eeaf58 == 1) {
        FUN_43901a8c(3,0,1,0x4f);
      }
      if (DAT_43eeaf58 == 5) {
        FUN_4381b9d0(5,3,1,&LAB_43cb437e_1,uVar5);
        FUN_43902718(s_Image_NULL_log_end_43cb438e);
      }
    }
    FUN_4381ba7c(piVar1);
  }
  return (int *)0x0;
}


/* query "4380f754" */

undefined4 FUN_4380f754(undefined4 param_1)

{
  char cVar1;
  byte bVar2;
  byte *pbVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  undefined4 uVar7;
  char *pcVar8;
  int *piVar9;
  undefined4 uVar10;
  undefined1 uVar11;
  undefined1 auStack_c8 [20];
  undefined4 uStack_b4;
  undefined4 uStack_88;
  undefined1 uStack_84;
  uint uStack_80;
  undefined1 uStack_7c;
  undefined1 uStack_7b;
  byte bStack_7a;
  int iStack_78;
  undefined1 uStack_70;
  undefined1 uStack_6f;
  int iStack_6c;
  int iStack_68;
  int iStack_64;
  undefined1 uStack_5f;
  byte bStack_5d;
  byte bStack_5c;
  byte bStack_5a;
  byte bStack_59;
  uint uStack_58;
  byte bStack_54;
  undefined1 auStack_50 [20];
  undefined1 auStack_3c [8];
  int iStack_34;
  int iStack_30;
  int aiStack_2c [2];
  
  iVar4 = FUN_4378f9b4();
  uVar10 = **(undefined4 **)(iVar4 + 4);
  iVar4 = FUN_4378f9b4();
  cVar1 = *(char *)(*(int *)(iVar4 + 0x20) + 1);
  if (*(int *)(DAT_44020e90 + 0x40) == 1) {
    iVar4 = 2;
  }
  else {
    iVar4 = 1;
  }
  piVar5 = (int *)FUN_43ae75dc(param_1);
  if ((char)piVar5[0x35c] == '\0') {
    iVar6 = FUN_43afdf16(param_1);
    if (iVar6 == 0) {
      iVar6 = FUN_43795b04();
      if (iVar6 != 0) {
        iVar6 = FUN_43799a94(1,0,piVar5[0x7f],uVar10,cVar1,0,1,0,iVar4 + 1,piVar5 + 0x35a,0);
        uVar7 = DAT_44025f5c;
        if (iVar6 != 0) {
          iVar6 = FUN_43ae8cc8(DAT_44025f5c);
          pbVar3 = DAT_4402546c;
          if (iVar6 != 0) {
            if (*DAT_4402546c != 0) {
              iVar4 = FUN_43799a94(1,1,0,uVar10,cVar1,0,1,0,iVar4 + 1,piVar5 + 0x35a,piVar5 + 0x147)
              ;
              if (iVar4 == 0) {
                return 5;
              }
              FUN_43728c18(piVar5 + 0x142,piVar5 + 0x143,piVar5 + 0x144);
              FUN_43acc282(piVar5[0x147],*pbVar3 - 1,piVar5 + 0xf9,0xfff,0xfff,0xfff);
            }
            FUN_4378e5ac(uVar7);
          }
          FUN_4381106c(piVar5);
          return 0;
        }
      }
    }
    else {
      if (iVar6 == 1) {
        uVar7 = FUN_4378f9b4();
        iVar6 = FUN_4378e6a0(DAT_44025f5c,uVar7);
        if (iVar6 == 0) {
          return 5;
        }
        if ((piVar5[0x6c] - 2U < 2) &&
           (iVar6 = FUN_4378f9b4(), *(int *)(*(int *)(iVar6 + 4) + 0xc) != 0)) {
          *(undefined1 *)(piVar5 + 0x83) = 0;
        }
        else {
          iVar6 = FUN_4378f9b4();
          if (*(char *)(*(int *)(iVar6 + 0x20) + 2) == '\0') {
            *(undefined1 *)(piVar5 + 0x83) = 0;
          }
        }
        FUN_4381061c(piVar5);
        if ((char)piVar5[0x83] == '\0') {
          *(undefined1 *)(piVar5 + 0x149) = 0;
        }
        iVar4 = iVar4 + 1;
        piVar9 = piVar5 + 0x35a;
        iVar6 = FUN_43799a94(1,1,0,uVar10,cVar1,0,1,0,iVar4,piVar9,piVar5 + 0x147);
        if (iVar6 == 0) {
          return 5;
        }
        FUN_43728c18(piVar5 + 0x142,piVar5 + 0x143,piVar5 + 0x144);
        pbVar3 = DAT_4402546c;
        uVar11 = *(undefined1 *)((int)piVar5 + 0x3fa);
        if (DAT_4402546c[0x4e] == 0xff) {
          uVar11 = 0;
        }
        else if (DAT_4402546c[0x4e] != 0) {
          uVar11 = 1;
        }
        iVar6 = piVar5[0x147];
        uVar7 = FUN_437d9d08();
        FUN_43acc2ee(iVar6,uVar11,uVar7);
        if ((char)piVar5[0x149] != '\0') {
          iVar6 = FUN_43799a94(1,0x10,0x42,uVar10,cVar1,0,1,0,iVar4,piVar9,aiStack_2c);
          if (iVar6 == 0) {
            return 5;
          }
          iVar6 = FUN_43799a94(1,4,0,uVar10,cVar1,0,1,0,iVar4,piVar9,piVar5 + 0x308);
          if (iVar6 == 0) {
            return 5;
          }
          iVar6 = FUN_4381c04c(0,piVar5[0x61],auStack_3c);
          if (iVar6 == 0) {
            *(undefined1 *)(piVar5 + 0x149) = 0;
            *(undefined1 *)(piVar5 + 0x83) = 0;
          }
          else {
            if ((pbVar3[2] & 1) == 0) {
              iVar6 = 10;
            }
            else {
              iVar6 = 7;
            }
            piVar5[0x175] = 1;
            piVar5[0x166] = iVar6;
            piVar5[0x167] = 2;
            piVar5[0x176] = iStack_34;
            piVar5[0x177] = iStack_30;
            piVar5[0x168] = aiStack_2c[0];
            piVar5[0x172] = 0;
            piVar5[0x173] = 0;
            piVar5[0x17e] = (uint)((char)piVar5[0x62] != '\0');
            piVar5[0x17f] = 0;
          }
        }
        iVar6 = FUN_43799a94(1,0xe,0,uVar10,cVar1,0,1,0,iVar4,piVar9,0);
        if (iVar6 != 0) {
          bVar2 = pbVar3[0x70];
          if (bVar2 == 0) {
            iVar6 = FUN_43affc8a(piVar5[0x142]);
            uStack_7c = *(undefined1 *)((int)piVar5 + 0x20e);
            uStack_7b = *(undefined1 *)((int)piVar5 + 0x20f);
            iStack_78 = piVar5[0x82];
            uStack_70 = (undefined1)piVar5[0x7f];
            uStack_6f = (undefined1)piVar5[0x313];
            uStack_80 = (uint)(iVar6 == 1);
            iStack_6c = piVar5[0x7b];
            iStack_68 = piVar5[0x7c];
            iStack_64 = piVar5[0x7d];
            uStack_5f = (undefined1)piVar5[0xf8];
            bStack_7a = bVar2;
            bStack_5d = bVar2;
            bStack_5c = bVar2;
            bStack_5a = bVar2;
            bStack_59 = bVar2;
            uStack_58 = (uint)bVar2;
            bStack_54 = bVar2;
            FUN_439e34d4(&uStack_80);
          }
          FUN_43799a94(1,0xf,0,uVar10,cVar1,0,1,0,iVar4,piVar9,0);
          iVar4 = FUN_43799a94(1,0xd,piVar5[0x7f],uVar10,cVar1,0,1,0,iVar4,piVar9,piVar5 + 0x148);
          if (iVar4 == 0) {
            return 5;
          }
          FUN_43728c4c(piVar5 + 0x145,piVar5 + 0x146);
          FUN_437956a4(piVar5[0x148]);
          FUN_43814008(piVar5);
          FUN_438106ec(piVar5);
          FUN_4354a678(piVar5);
          FUN_43810e7c(piVar5);
          FUN_43810fa8(piVar5);
          FUN_4381127c(piVar5);
          if (cVar1 == '\x01') {
            FUN_43b03a74(auStack_50,DAT_440259b4);
            FUN_4379704c(param_1,auStack_50,piVar5);
          }
          if ((char)piVar5[0x83] == '\0') {
            return 5;
          }
          FUN_43afb42e(auStack_c8);
          FUN_43afb476(auStack_c8,DAT_44020064);
          uStack_b4 = 0;
          uStack_84 = 2;
          uStack_88 = FUN_43afbf44(param_1);
          (**(code **)(*piVar5 + 8))(piVar5);
          iVar4 = FUN_4381bbf0(param_1,auStack_c8,piVar5);
          if (iVar4 == 0) {
            return 5;
          }
          FUN_43b04730();
          return 5;
        }
        FUN_4380f6a8(3,9,1,&DAT_43cb0f3e);
        pcVar8 = s_SyncResMgr__Get_IDT_OPD_failure_43cb0f52;
      }
      else {
        FUN_4380f6a8(3,9,1,&DAT_43cb0f14);
        pcVar8 = s_Sequence_Stage_Error__43cb0f28;
      }
      FUN_43902718(pcVar8);
    }
  }
  return 5;
}


/* query "43b03a74" */

undefined4 FUN_43b03a74(undefined4 param_1)

{
  FUN_4380f5b4();
  return param_1;
}


/* query "43b03a80" */

undefined4 FUN_43b03a80(undefined4 param_1)

{
  FUN_4380f5d8();
  return param_1;
}

