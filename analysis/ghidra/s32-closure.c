/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43b03a48" */

void FUN_43b03a48(int param_1,undefined4 param_2)

{
  (**(code **)(param_1 + 8))(param_2);
  return;
}


/* query "43ad60cc" */

undefined4 s32_candidate_43ad60cc(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = thunk_FUN_43ad2e90(param_1 + 3);
  if (iVar1 == 0) {
    uVar2 = func_0x436cd1ec(*param_1);
    thunk_FUN_43ad6034(param_1 + 3,uVar2);
    return 1;
  }
  return 0;
}


/* query "43549380" */

undefined4 s32_candidate_43549380(undefined4 param_1)

{
  byte *pbVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  undefined1 uVar10;
  uint uVar11;
  int iVar12;
  undefined4 uVar13;
  int iVar14;
  int iVar15;
  uint in_fpscr;
  double dVar16;
  double dVar17;
  double dVar18;
  undefined4 uStack_2b4;
  undefined4 uStack_2b0;
  undefined4 uStack_2ac;
  undefined4 uStack_2a8;
  int iStack_2a4;
  int iStack_2a0;
  undefined4 uStack_29c;
  undefined1 uStack_298;
  undefined1 uStack_297;
  undefined2 uStack_296;
  undefined2 uStack_294;
  undefined2 uStack_292;
  undefined2 uStack_290;
  undefined2 uStack_28e;
  undefined2 uStack_28c;
  undefined2 uStack_28a;
  undefined2 uStack_288;
  undefined2 uStack_286;
  undefined2 uStack_284;
  undefined2 uStack_282;
  undefined2 uStack_280;
  undefined4 uStack_27c;
  char cStack_278;
  undefined1 uStack_277;
  undefined1 uStack_276;
  undefined4 uStack_274;
  undefined4 uStack_270;
  undefined4 uStack_26c;
  undefined4 uStack_268;
  undefined1 uStack_264;
  undefined4 uStack_260;
  undefined4 uStack_25c;
  undefined4 uStack_258;
  undefined4 uStack_254;
  undefined1 uStack_250;
  undefined1 uStack_20c;
  undefined1 uStack_1ec;
  undefined4 uStack_1d0;
  undefined2 uStack_1cc;
  undefined2 uStack_1ca;
  undefined2 uStack_1c8;
  undefined2 uStack_1c6;
  undefined1 uStack_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined4 uStack_1b8;
  undefined1 uStack_1b4;
  undefined1 uStack_1b3;
  undefined1 auStack_1b0 [20];
  undefined4 uStack_19c;
  undefined4 uStack_170;
  undefined1 uStack_16c;
  uint uStack_168;
  undefined1 uStack_164;
  undefined1 uStack_163;
  undefined1 uStack_162;
  undefined4 uStack_160;
  undefined1 uStack_158;
  undefined1 uStack_157;
  undefined4 uStack_154;
  undefined4 uStack_150;
  undefined4 uStack_14c;
  undefined1 uStack_147;
  undefined1 uStack_145;
  undefined1 uStack_144;
  undefined1 uStack_142;
  undefined1 uStack_141;
  int iStack_140;
  undefined1 uStack_13c;
  undefined1 auStack_138 [40];
  undefined1 auStack_110 [20];
  undefined1 auStack_fc [20];
  undefined1 auStack_e8 [20];
  undefined1 auStack_d4 [20];
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [16];
  uint uStack_38;
  undefined4 auStack_34 [2];
  
  iVar4 = FUN_4378f9b4();
  iVar12 = **(int **)(iVar4 + 4);
  iVar4 = FUN_4378f9b4();
  cVar2 = *(char *)(*(int *)(iVar4 + 8) + 0x33);
  iVar4 = FUN_43ae75dc(param_1);
  if (*(char *)(iVar4 + 0xd70) != '\0') {
    return 5;
  }
  uVar5 = FUN_43afdf16(param_1);
  switch(uVar5) {
  case 0:
    iVar8 = FUN_43795b04();
    if (iVar8 == 0) {
      return 5;
    }
    iVar8 = FUN_43799a94(1,0,*(undefined4 *)(iVar4 + 0x1fc),iVar12,0,1,0,2,0,iVar4 + 0xd68,0);
    uVar5 = DAT_44025f5c;
    if (iVar8 == 0) {
      return 5;
    }
    iVar8 = FUN_43ae8cc8(DAT_44025f5c);
    pbVar1 = DAT_4402546c;
    if (iVar8 != 0) {
      if (*DAT_4402546c != 0) {
        iVar8 = FUN_43799a94(1,1,0,iVar12,0,1,0,2,0,iVar4 + 0xd68,iVar4 + 0x51c);
        if (iVar8 == 0) {
          return 5;
        }
        FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
        FUN_43acc282(*(undefined4 *)(iVar4 + 0x51c),*pbVar1 - 1,iVar4 + 0x3e4,0xfff,0xfff,0xfff);
      }
      FUN_4378e5ac(uVar5);
    }
    if (*(int *)(iVar4 + 0xd60) != 1) {
      FUN_43b0419c(1,iVar12);
    }
    iVar8 = *(int *)(iVar4 + 0xd5c);
    if (iVar8 == 1) {
      uVar5 = 0xc;
LAB_435494d6:
      FUN_43b0417e(uVar5,0xffffffff,1,iVar12);
    }
    else {
      if (iVar8 == 3) {
        uVar5 = 8;
        goto LAB_435494d6;
      }
      if (iVar8 == 0) {
        uVar5 = 0xe;
        goto LAB_435494d6;
      }
    }
    FUN_43b03a74(auStack_5c,DAT_4402110c);
    FUN_43796910(param_1,auStack_5c,iVar4);
switchD_435493c6_caseD_2:
    return 0;
  case 1:
    *(undefined4 *)(iVar4 + 0xc54) = *(undefined4 *)(iVar4 + 0xc4c);
    iVar8 = FUN_4378f9b4();
    if ((*(int *)(*(int *)(iVar8 + 8) + 0x1e8) != 0) && (*(int *)(iVar4 + 0x1fc) != 9)) {
      return 1;
    }
    uVar5 = FUN_4378f9b4();
    iVar8 = FUN_4378e6a0(DAT_44025f5c,uVar5);
    if (iVar8 == 0) {
      return 5;
    }
    iVar14 = iVar4 + 0xd68;
    iVar8 = FUN_43799a94(1,1,0,iVar12,0,1,0,*(int *)(iVar4 + 0xc4c) + 1,0,iVar14,iVar4 + 0x51c);
    if (iVar8 == 0) {
      return 5;
    }
    FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
    pbVar1 = DAT_4402546c;
    uVar10 = *(undefined1 *)(iVar4 + 0x3fa);
    if (DAT_4402546c[0x4e] == 0xff) {
      uVar10 = 0;
    }
    else if (DAT_4402546c[0x4e] != 0) {
      uVar10 = 1;
    }
    uVar13 = *(undefined4 *)(iVar4 + 0x51c);
    uVar5 = FUN_437d9d08();
    FUN_43acc2ee(uVar13,uVar10,uVar5);
    iVar8 = FUN_43799a94(1,0x10,0x43,iVar12,0,1,0,*(int *)(iVar4 + 0xc4c) + 1,0,iVar14,auStack_34);
    if (iVar8 == 0) {
      return 5;
    }
    iVar8 = FUN_43799a94(1,6,0,iVar12,0,1,0,*(int *)(iVar4 + 0xc4c) + 1,0,iVar14,iVar4 + 0xc20);
    if (iVar8 == 0) {
      return 5;
    }
    FUN_43b0417e(0xffffffff,0xffffffff,0,0);
    FUN_43b0419c(0,0);
    if (*(char *)(iVar4 + 0xc18) == '\0') {
      uVar5 = 1;
    }
    else if (DAT_43f9b2a9 < 0x3c) {
      uVar5 = 0x11;
    }
    else {
      uVar5 = 1;
    }
    iVar15 = iVar4 + 0x1c;
    iVar8 = FUN_43ae8c4a(iVar12 + 1);
    iVar6 = FUN_439035e0(iVar15,*(undefined4 *)(iVar4 + 0x18c),iVar8 << 8,uVar5,0,5);
    if (iVar6 == 0) {
      DAT_43f9b2a9 = 0;
    }
    else {
      *(undefined1 *)(iVar4 + 0x524) = 0;
      *(undefined1 *)(iVar4 + 0x20c) = 0;
      DAT_43f9b2a9 = DAT_43f9b2a9 + 1;
    }
    iVar6 = FUN_4378f9b4();
    if (*(char *)(*(int *)(iVar6 + 0x50) + 0x1c) != '\0') {
      FUN_43780188(iVar15);
    }
    FUN_4381c04c(0,*(undefined4 *)(iVar4 + 0x184),auStack_48);
    FUN_4381c228(0);
    if (*(char *)(iVar4 + 0xd4c) != '\0') {
      *(int *)(iVar4 + 0xd50) = iVar12;
      *(undefined1 *)(iVar4 + 0xd4c) = 0;
    }
    if ((pbVar1[2] & 1) == 0) {
      uVar5 = 10;
    }
    else {
      uVar5 = 0xb;
    }
    *(undefined4 *)(iVar4 + 0x598) = uVar5;
    *(undefined4 *)(iVar4 + 0x59c) = 2;
    *(undefined4 *)(iVar4 + 0x5c8) = 0;
    *(undefined4 *)(iVar4 + 0x5cc) = 0;
    *(undefined4 *)(iVar4 + 0x5a0) = auStack_34[0];
    *(undefined4 *)(iVar4 + 0x5d4) = 1;
    *(undefined4 *)(iVar4 + 0x5fc) = 0;
    *(undefined4 *)(iVar4 + 0x738) = 0;
    *(undefined4 *)(iVar4 + 0x5d8) = *(undefined4 *)(iVar4 + 0x24);
    *(undefined4 *)(iVar4 + 0x764) = 0;
    *(undefined4 *)(iVar4 + 0x5dc) = *(undefined4 *)(iVar4 + 0x28);
    *(uint *)(iVar4 + 0x5f8) = (uint)(*(char *)(iVar4 + 400) != '\0');
    FUN_439c5320(iVar4 + 0x668,iVar4 + 0x598,0x68);
    if (((*(int *)(iVar4 + 0x1b0) - 2U < 2) &&
        (iVar6 = FUN_4378f9b4(), *(int *)(*(int *)(iVar6 + 4) + 0xc) != 0)) &&
       (*(int *)(iVar4 + 0x1fc) != 9)) {
      *(undefined1 *)(iVar4 + 0x1ee) = 0;
      *(undefined1 *)(iVar4 + 0x20c) = 0;
    }
    else {
      if ((*(char *)(iVar4 + 0xd40) == '\0') || (*(char *)(iVar4 + 0xd41) == '\0')) {
        iVar6 = FUN_4378f9b4();
        bVar3 = *(byte *)(*(int *)(iVar6 + 8) + 0x268);
        bVar9 = bVar3 & 2;
        if ((bVar3 & 2) != 0) goto LAB_4354976a;
      }
      else {
        bVar9 = 0;
      }
      *(byte *)(iVar4 + 0x20c) = bVar9;
    }
LAB_4354976a:
    iVar6 = FUN_43799a94(1,0xe,0,iVar12,0,1,0,*(int *)(iVar4 + 0xc4c) + 1,0,iVar14,0);
    if (iVar6 != 0) {
      if ((pbVar1[0x70] == 0) && (iVar6 = FUN_4378003c(), iVar6 == 0)) {
        iVar7 = FUN_43affc8a(*(undefined4 *)(iVar4 + 0x508));
        uStack_164 = *(undefined1 *)(iVar4 + 0x20e);
        uStack_162 = 0;
        uStack_145 = 0;
        uStack_163 = *(undefined1 *)(iVar4 + 0x20f);
        uStack_144 = 0;
        uStack_142 = 0;
        uStack_160 = *(undefined4 *)(iVar4 + 0x208);
        uStack_141 = 0;
        uStack_13c = 0;
        uStack_158 = (undefined1)*(undefined4 *)(iVar4 + 0x1fc);
        uStack_157 = (undefined1)*(undefined4 *)(iVar4 + 0xc4c);
        uStack_168 = (uint)(iVar7 == 1);
        uStack_154 = *(undefined4 *)(iVar4 + 0x1ec);
        uStack_150 = *(undefined4 *)(iVar4 + 0x1f0);
        uStack_14c = *(undefined4 *)(iVar4 + 500);
        uStack_147 = (undefined1)*(undefined4 *)(iVar4 + 0x3e0);
        iStack_140 = iVar6;
        FUN_439e34d4(&uStack_168);
      }
      FUN_43799a94(1,0xf,0,iVar12,0,1,0,*(int *)(iVar4 + 0xc4c) + 1,0,iVar14,0);
      iVar14 = FUN_43799a94(1,0xd,*(undefined4 *)(iVar4 + 0x1fc),iVar12,0,1,0,
                            *(int *)(iVar4 + 0xc4c) + 1,0,iVar14,iVar4 + 0x520);
      if (iVar14 != 0) {
        FUN_43728c4c(iVar4 + 0x514,iVar4 + 0x518);
        FUN_437956a4(*(undefined4 *)(iVar4 + 0x520));
        FUN_43814008(iVar4);
        FUN_4381061c(iVar4);
        FUN_43b03a74(auStack_70,DAT_44022cc8);
        FUN_43796910(param_1,auStack_70,iVar4);
        FUN_438106ec(iVar4);
        FUN_43b03a74(auStack_84,DAT_44023820);
        FUN_43797090(param_1,auStack_84,iVar4);
        if (cVar2 == '\0') {
          FUN_43b03a74(auStack_ac,DAT_44021e0c);
          FUN_43796910(param_1,auStack_ac,iVar4);
        }
        else {
          FUN_43b03a74(auStack_98,DAT_44021e0c);
          FUN_43797090(param_1,auStack_98,iVar4);
        }
        FUN_43b03a74(auStack_c0,DAT_44024a24);
        FUN_43796910(param_1,auStack_c0,iVar4);
        FUN_43b03a74(auStack_d4,DAT_440259b4);
        FUN_4379704c(param_1,auStack_d4,iVar4);
        iVar14 = FUN_4378f9b4();
        if (((*(byte *)(*(int *)(iVar14 + 8) + 0x26a) & 1) != 0) &&
           (iVar14 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar14 + 8) + 0x268) & 4) != 0)) {
          iVar14 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd26) = *(undefined2 *)(*(int *)(iVar14 + 0x2c) + 0x96);
          iVar14 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd28) = *(undefined2 *)(*(int *)(iVar14 + 0x2c) + 0x98);
          iVar14 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd2a) = *(undefined2 *)(*(int *)(iVar14 + 0x2c) + 0x9a);
          iVar14 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd2c) = *(undefined2 *)(*(int *)(iVar14 + 0x2c) + 0x9c);
          iVar14 = FUN_4378f9b4();
          if (*(int *)(*(int *)(iVar14 + 0x2c) + 0xa4) != 0) {
            iVar14 = FUN_4378f9b4();
            dVar16 = (double)VectorUnsignedToFloat
                                       ((uint)*(ushort *)(*(int *)(iVar14 + 0x38) + 0x38),
                                        (byte)(in_fpscr >> 0x16) & 3);
            iVar14 = FUN_4378f9b4();
            dVar17 = (double)VectorUnsignedToFloat
                                       (*(undefined4 *)(*(int *)(iVar14 + 0x2c) + 0xa0),
                                        (byte)(in_fpscr >> 0x16) & 3);
            iVar14 = FUN_4378f9b4();
            dVar18 = (double)VectorUnsignedToFloat
                                       (*(undefined4 *)(*(int *)(iVar14 + 0x2c) + 0xa4),
                                        (byte)(in_fpscr >> 0x16) & 3);
            dVar18 = (dVar16 * 100.0 * dVar17) / dVar18;
            if (((int)((uint)(dVar18 < 126500.0) << 0x1f) < 0) &&
               (uVar11 = VectorFloatToUnsigned(dVar18,3), uVar11 != 0)) {
              if (uVar11 < 0x31ce) {
                cVar2 = FUN_4355faf0(uVar11 + 0x32,100);
                bVar3 = cVar2 << 1;
              }
              else {
                cVar2 = FUN_4355faf0(uVar11 + 500,1000);
                bVar3 = cVar2 << 1 | 1;
              }
              *(byte *)(iVar4 + 0xd2e) = bVar3;
              goto LAB_43549a18;
            }
          }
          *(undefined1 *)(iVar4 + 0xd2e) = 0xff;
        }
LAB_43549a18:
        FUN_43b03a5e(&uStack_2b4);
        if ((*(char *)(iVar4 + 0x20c) != '\0') && (iVar14 = FUN_437286bc(), iVar14 != 0)) {
          uStack_2b4 = *(undefined4 *)(iVar4 + 0x1ec);
          uStack_2b0 = *(undefined4 *)(iVar4 + 0x1f0);
          uStack_2ac = *(undefined4 *)(iVar4 + 500);
          uStack_297 = 0;
          uStack_2a8 = 0;
          uStack_29c = *(undefined4 *)(iVar4 + 0xc4c);
          uStack_298 = (undefined1)*(undefined4 *)(iVar4 + 0x1f8);
          uStack_296 = *(undefined2 *)(iVar4 + 0x1b8);
          uStack_294 = *(undefined2 *)(iVar4 + 0x1ba);
          cVar2 = *(char *)(iVar4 + 400);
          iStack_2a4 = iVar15;
          iStack_2a0 = iVar8;
          if (cVar2 == '\0') {
            uStack_292 = FUN_43ae9e86(*(undefined2 *)(iVar4 + 0x19e),0x40);
          }
          else {
            uStack_292 = FUN_43ae98f8();
          }
          uStack_290 = *(undefined2 *)(iVar4 + 0x1a0);
          uStack_28a = *(undefined2 *)(iVar4 + 0x19e);
          uStack_27c = *(undefined4 *)(iVar4 + 0x1b4);
          uStack_270 = *(undefined4 *)(iVar4 + 0x4fc);
          uStack_28e = 0;
          uStack_28c = 0;
          uStack_26c = *(undefined4 *)(iVar4 + 0x500);
          uStack_286 = 0;
          uStack_284 = 0;
          uStack_268 = *(undefined4 *)(iVar4 + 0x504);
          uStack_277 = 0;
          uStack_276 = 0;
          uStack_274 = 0;
          uStack_264 = *(int *)(iVar4 + 0xbd4) == 1;
          uStack_250 = 0;
          uStack_258 = *(undefined4 *)(iVar4 + 0xd54);
          uStack_260 = 0xffffffff;
          uStack_254 = *(undefined4 *)(iVar4 + 0xd58);
          uStack_25c = 0xffffffff;
          uStack_20c = 0;
          uStack_1ec = 0;
          uStack_1cc = *(undefined2 *)(iVar4 + 0xd26);
          uStack_1c0 = 0xffffffff;
          uStack_1d0 = 0;
          uStack_1ca = *(undefined2 *)(iVar4 + 0xd28);
          uStack_1b4 = 0;
          uStack_1b3 = 0;
          uStack_1c8 = *(undefined2 *)(iVar4 + 0xd2a);
          uStack_1c6 = *(undefined2 *)(iVar4 + 0xd2c);
          uStack_1c4 = *(undefined1 *)(iVar4 + 0xd2e);
          uStack_1bc = *(undefined4 *)(iVar4 + 0x1b0);
          uStack_1b8 = *(undefined4 *)(iVar4 + 0xd84);
          uStack_288 = uStack_290;
          uStack_282 = uStack_28a;
          uStack_280 = uStack_290;
          cStack_278 = cVar2;
          FUN_4379b44c(0,&uStack_2b4);
        }
        iVar8 = FUN_4378f9b4();
        if ((*(byte *)(*(int *)(iVar8 + 8) + 0x267) & 0x80) != 0) {
          FUN_437fe4d4();
        }
        iVar14 = *(int *)(iVar4 + 0xc4c);
        iVar8 = FUN_4378f9b4();
        iVar14 = iVar12 + iVar14 + 1;
        uStack_38 = (int)(uint)*(ushort *)(*(int *)(iVar8 + 4) + 0x20) >> 2;
        FUN_43ad2dfc(0xfff,&uStack_38);
        iVar8 = *(int *)(iVar4 + 0xc4c) + 2;
        iVar12 = FUN_4378f9b4();
        iVar12 = FUN_4355faf0(*(int *)(*(int *)(iVar12 + 4) + 0x18) + 0x3e7ff,0x3e800);
        if (*(char *)(iVar4 + 0x20d) == '\0') {
          iVar4 = FUN_43ae8c4a(iVar14);
          iVar4 = iVar4 * 0x100 + (uStack_38 >> 4);
        }
        else {
          iVar8 = iVar8 + *(int *)(iVar4 + 0xc60);
          iVar4 = FUN_43ae8c4a(iVar14 + *(int *)(iVar4 + 0xc60));
          iVar4 = iVar4 * 0x100 + (uStack_38 >> 4);
        }
        iVar4 = FUN_43b2a2d0(iVar15,iVar4,iVar12 * iVar8,0,5);
        if (iVar4 != 0) {
          return 5;
        }
        return 0;
      }
    }
    break;
  case 2:
    goto switchD_435493c6_caseD_2;
  case 3:
    if (*(char *)(iVar4 + 0x20c) != '\0') {
      uVar11 = *(int *)(iVar4 + 0xc50) + 1;
      *(uint *)(iVar4 + 0xc50) = uVar11;
      if (uVar11 < *(uint *)(iVar4 + 0xc4c)) {
        return 1;
      }
      if ((*(char *)(iVar4 + 0x20d) != '\0') && (iVar8 = FUN_437999e4(1,6), iVar8 != 0)) {
        *(undefined1 *)(iVar4 + 0xd22) = 0;
        iVar8 = thunk_FUN_439dce54();
        *(char *)(iVar4 + 0xd72) = (char)iVar8;
        if (iVar8 != 0) {
          FUN_43ae7558(auStack_138);
          iVar8 = FUN_43903558(iVar4 + 0x94,0x30700,0x11,0,5);
          if (iVar8 == 0) {
            *(int *)(iVar4 + 0xd74) = iVar12;
            DAT_43f9b2a8 = 0;
            if (*(char *)(iVar4 + 0xc18) == '\0') {
              uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1e);
            }
            else if (cVar2 == '\0') {
              uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1c);
            }
            else {
              uVar10 = *(undefined1 *)(DAT_4401f1d0 + 0x1d);
            }
            *(undefined1 *)(iVar4 + 0x212) = uVar10;
            bVar3 = *(byte *)(iVar4 + 0x212) & 0x7f;
            if (bVar3 == 0x40) {
              FUN_43560dc4(0x1a,0xffffffdf);
              FUN_43b03a74(auStack_e8,DAT_44020ee4);
              FUN_4379704c(param_1,auStack_e8,iVar4);
            }
            else if (bVar3 == 0x41) {
              FUN_43560dc4(0x1a,0xffffffdf);
              FUN_43b03a74(auStack_fc,DAT_44020ee4);
              FUN_43796910(param_1,auStack_fc,iVar4);
            }
            else {
              FUN_43560da8(0x1a,0x20);
            }
            FUN_43afb42e(auStack_1b0);
            FUN_43afb476(auStack_1b0,DAT_44021fc8);
            uStack_19c = 4;
            uStack_16c = 0;
            uStack_170 = FUN_43afbf44(param_1);
            FUN_43b03a80(auStack_110,DAT_44022af4);
            uVar5 = FUN_43b03a70(iVar4);
            uVar5 = FUN_4380d708(auStack_110,uVar5,iVar4);
            iVar12 = FUN_4381bbf0(param_1,auStack_1b0,uVar5);
            if (iVar12 != 0) {
              FUN_43b04730();
            }
            FUN_43ae7542(iVar4 + 0x1c);
            FUN_43ae7542(iVar4 + 0x94);
          }
          else {
            DAT_43f9b2a8 = DAT_43f9b2a8 + 1;
            if (0x3b < DAT_43f9b2a8) {
              FUN_4380f508(3,9,1,&DAT_43cb0ee4,DAT_43f9b2a8);
              FUN_43902718(s_Face_Memory_Alloc_Error___d_43cb0ef8,DAT_43f9b2a8);
            }
          }
          FUN_43ae7534(auStack_138);
        }
      }
    }
    break;
  default:
    FUN_4380f508(3,9,1,&DAT_43cb0f14);
    FUN_43902718(s_Sequence_Stage_Error__43cb0f28);
  }
  return 5;
}


/* query "43796518" */

int s32_candidate_43796518(void)

{
  uint uVar1;
  int iVar2;
  
  func_0x43728870();
  func_0x43ae128a();
  FUN_43b2a162(&DAT_43e9d790);
  FUN_43b2a162(&DAT_43e9d76c);
  FUN_43b2a162(&DAT_43e9d7b8);
  FUN_43b2a162(&DAT_43e9d844);
  FUN_43b2a162(&DAT_43e9dd08);
  FUN_43b2a162(&DAT_43e9ddf8);
  FUN_43b2a162(&DAT_43e9d74c);
  FUN_43b2a162(&DAT_43e9d724);
  FUN_43b2a162(&DAT_43e9d7f4);
  FUN_43b2a162(&DAT_43e9d824);
  uVar1 = FUN_43560bb0(uRam43e9dd00,&DAT_43e9dcec);
  iVar2 = 1 - uVar1;
  if (1 < uVar1) {
    iVar2 = 0;
  }
  return iVar2;
}


/* query "43796910" */

void FUN_43796910(int param_1,undefined4 *param_2,undefined4 param_3)

{
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  int *piStack_1c;
  
  FUN_43ae9682(&uStack_34);
  uStack_34 = *param_2;
  uStack_30 = param_2[1];
  uStack_2c = param_2[2];
  uStack_28 = param_2[3];
  uStack_24 = param_2[4];
  uStack_20 = param_3;
  if (param_1 == 0) {
    piStack_1c = (int *)0x0;
  }
  else {
    piStack_1c = (int *)FUN_43ae75dc(param_1);
    (**(code **)(*piStack_1c + 8))();
  }
  FUN_43ae98d0(&DAT_43e9d7d4,&uStack_34);
  return;
}


/* query "43ae96b8" */

void FUN_43ae96b8(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0xc) = param_2;
  *(int *)param_1 = param_1;
  *(int *)(param_1 + 4) = param_1;
  *(undefined4 *)(param_1 + 8) = 0;
  return;
}


/* query "43aef4e8" */

void FUN_43aef4e8(undefined4 param_1,undefined4 param_2)

{
  FUN_4383b520(0x1a,0);
  FUN_43aef67a(param_1,param_2);
  FUN_4383b520(0x1a,1);
  return;
}


/* query "43aeaf4e" */

void FUN_43aeaf4e(undefined4 param_1,undefined4 param_2)

{
  undefined1 auStack_208 [440];
  undefined1 auStack_50 [40];
  undefined1 *puStack_28;
  undefined1 *puStack_24;
  
  FUN_439c5a04(&puStack_28,0,0x18);
  puStack_24 = auStack_50;
  puStack_28 = auStack_208;
  FUN_437a995c(&puStack_28,param_1,param_2);
  FUN_4381d400(&puStack_28);
  return;
}


/* query "437d9ae0" */

void FUN_437d9ae0(int param_1,undefined4 param_2)

{
  byte *pbVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  int *piVar12;
  
  piVar12 = DAT_44025a3c;
  uVar11 = DAT_44024e7c;
  uVar10 = DAT_44024138;
  uVar9 = DAT_44023b98;
  uVar8 = DAT_44023b54;
  uVar7 = DAT_440239b0;
  uVar6 = DAT_440229ec;
  uVar5 = DAT_44021e50;
  uVar4 = DAT_44021e40;
  uVar3 = DAT_44020f7c;
  iVar2 = DAT_440202e4;
  FUN_438968c4(param_2,DAT_44025a3c,DAT_440229ec,DAT_4401f258,DAT_44023b54,DAT_4401f7c0,DAT_44021e40
               ,DAT_440223c8,DAT_44021e50,DAT_44026178,DAT_440239b0,DAT_44023ac8,DAT_44024e7c,
               DAT_440201fc,DAT_440202a0,DAT_4401fe6c,DAT_44023b98,DAT_4401f99c,DAT_44026a70,
               DAT_44021bc4,DAT_4402116c,DAT_44022d08,DAT_44024138,DAT_4401f684,DAT_44020f7c,
               DAT_440262d4,DAT_440202e4);
  FUN_43888268(uVar6,uVar11,param_2);
  pbVar1 = DAT_4401f6ac;
  if (*piVar12 != 8) {
    FUN_43b158d8(param_1 + 0x135,param_2);
    FUN_43b14ff4(param_2,uVar10);
    FUN_43b14b0e(uVar6,uVar3);
    FUN_43b13a02(param_2,uVar4);
    FUN_43b16676(param_2);
    FUN_43b15cf4(param_1 + 0x134,param_2);
    FUN_4387d590(uVar6,param_2);
    FUN_43b13020(uVar6,uVar7,param_2);
    FUN_43b13984(param_2);
    FUN_43b15212(param_2,iVar2 + 2);
    FUN_43898a2c(uVar6,uVar5,param_2);
    FUN_438a4ec8(uVar6,uVar8,param_2);
    if (pbVar1[0x3a] == 0xff) {
      FUN_438b0854(param_2,iVar2 + 0xa8);
    }
    else {
      FUN_438b1a44(uVar6,uVar9,param_2);
    }
  }
  if ((*pbVar1 & 0x40) != 0) {
    **(undefined4 **)(pbVar1 + 0x20) = *(undefined4 *)(pbVar1 + 0x28);
  }
  if ((*pbVar1 & 4) != 0) {
    FUN_437d9884(3,7,1,&DAT_43ca8bc3,*(undefined4 **)(pbVar1 + 0x20),
                 **(undefined4 **)(pbVar1 + 0x20));
    FUN_43902718(s_SetSyncDevelopParam__addr___0x_x_43ca8bd5,*(undefined4 **)(pbVar1 + 0x20),
                 **(undefined4 **)(pbVar1 + 0x20));
    return;
  }
  return;
}


/* query "43810fa8" */

void FUN_43810fa8(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined2 uStack_14;
  
  if (*(char *)(param_1 + 0xd70) == '\0') {
    iVar2 = FUN_43728d28(*(undefined4 *)(param_1 + 0xd68),*(undefined4 *)(param_1 + 0xd6c));
    iVar1 = DAT_4402546c;
    if (iVar2 == 0) {
      *(undefined1 *)(param_1 + 0xd70) = 1;
    }
    else {
      if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
        FUN_43561540(s_Imgr_Kck_S_43cb118f);
      }
      iVar2 = FUN_4378f9b4();
      uStack_18 = *(uint *)(*(int *)(iVar2 + 0x24) + 0x10);
      uStack_14 = (undefined2)*(undefined4 *)(*(int *)(iVar2 + 0x24) + 0x14);
      if ((*(byte *)(iVar1 + 0x1d) & 2) != 0) {
        uStack_18 = 0xf00;
      }
      if ((*(byte *)(iVar1 + 0x26) & 1) != 0) {
        FUN_4380fcac(3,9,1,&DAT_43cb119a,uStack_18 & 0xffff,uStack_18 >> 0x10);
        FUN_43902718(s_a_gain__04X__d_gain__04X_43cb11ae,uStack_18 & 0xffff,uStack_18._2_2_);
      }
      FUN_43ae9380(&uStack_18);
      FUN_4378e5f0(DAT_44025f5c);
    }
  }
  return;
}


/* query "4381127c" */

void FUN_4381127c(int param_1)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 extraout_r1;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  int iStack_94;
  int iStack_90;
  int iStack_8c;
  int iStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  uint uStack_48;
  uint uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined2 auStack_2c [6];
  char *pcStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  
  if (*(char *)(param_1 + 0xd70) == '\0') {
    iStack_18 = param_1;
    iVar4 = FUN_43728d28(*(undefined4 *)(param_1 + 0xd68),*(undefined4 *)(param_1 + 0xd6c));
    if (iVar4 != 0) {
      if ((*(byte *)(DAT_4402546c + 0x12) & 8) != 0) {
        FUN_43561540(s_CamStrt_S_43cb1297);
      }
      iVar4 = FUN_43acc65e(*(undefined4 *)(param_1 + 0x51c));
      if (iVar4 == 0) {
        iVar4 = FUN_4378f9b4();
        if ((*(char *)(param_1 + 0x524) != '\0') && (*(char *)(*(int *)(iVar4 + 0x20) + 2) != '\0'))
        {
          FUN_437964b0(**(undefined4 **)(iVar4 + 4));
        }
        FUN_43aef4ca(iVar4);
        iVar2 = DAT_440229ec;
        pcVar1 = DAT_4402116c;
        pcStack_20 = DAT_4402116c;
        uStack_1c = extraout_r1;
        FUN_43b149ae(iVar4,DAT_44025a3c,DAT_440229ec,DAT_44021bc4);
        iVar3 = DAT_44024e7c;
        iVar12 = *(int *)(iVar4 + 8);
        uVar5 = FUN_43b135c6(iVar12 + 0x870);
        iVar11 = iVar12 + 0x2d4;
        iVar6 = FUN_43aef24a(iVar11);
        if (iVar6 == 0) {
          iStack_94 = FUN_43b13052(iVar11,0);
          iVar6 = FUN_43b13648(iVar11,0);
          iStack_8c = FUN_43b13662(iVar11,0);
          iStack_90 = FUN_43b1362e(iVar11,0);
          iStack_88 = FUN_43affa14(iVar11,0);
          uStack_84 = FUN_43b135cc(iVar11,0);
          uStack_80 = FUN_43b135e2(iVar11,0);
          uStack_7c = FUN_43b135fa(iVar11,0);
          uStack_78 = FUN_43b13614(iVar11,0);
          uVar10 = 0;
        }
        else {
          iStack_94 = FUN_43b13052(iVar11,2);
          iVar6 = FUN_43b13648(iVar11,2);
          iStack_8c = FUN_43b13662(iVar11,2);
          iStack_90 = FUN_43b1362e(iVar11,2);
          iStack_88 = FUN_43affa14(iVar11,2);
          uStack_84 = FUN_43b135cc(iVar11,2);
          uStack_80 = FUN_43b135e2(iVar11,2);
          uStack_7c = FUN_43b135fa(iVar11,2);
          uStack_78 = FUN_43b13614(iVar11,2);
          uVar10 = 2;
        }
        uVar10 = FUN_43b1367a(iVar11,uVar10);
        iVar11 = FUN_436d3b30(iVar12 + 0xb78);
        iVar12 = FUN_436d3bc0(*(int *)(iVar4 + 8) + 0xb78);
        iVar7 = FUN_436d3bf0(*(int *)(iVar4 + 8) + 0xb78);
        iVar8 = FUN_436d3c20(*(int *)(iVar4 + 8) + 0xb78);
        iVar9 = FUN_436d3ce0(*(int *)(iVar4 + 8) + 0xb78);
        iVar4 = FUN_436d3ad4(*(int *)(iVar4 + 8) + 0xb78);
        FUN_43883d38(*(undefined1 *)(iVar2 + 0x54),0,0,*(undefined4 *)(iVar2 + 0x30),1,uVar5,iVar11,
                     0);
        FUN_43883d38(*(undefined1 *)(iVar2 + 0x54),1,0,*(undefined4 *)(iVar2 + 0x30),1,uVar5,iVar11,
                     0);
        FUN_43883d38(*(undefined1 *)(iVar2 + 0x54),2,0,*(undefined4 *)(iVar2 + 0x30),1,uVar5,iVar11,
                     0);
        FUN_43883d38(*(undefined1 *)(iVar2 + 0x54),3,0,*(undefined4 *)(iVar2 + 0x30),1,uVar5,iVar11,
                     0);
        if (iVar4 != 0) {
          FUN_43b79840(iVar4,*DAT_44025748);
        }
        uVar5 = DAT_44026718;
        if (*(char *)(iVar3 + 0x1f8) == '\0') {
          if (iVar11 != 0) {
            FUN_43b7909a(iVar11,DAT_44026718);
            FUN_43b790da(iVar11,uVar5);
            FUN_43b7901a(iVar11,DAT_44022124);
            FUN_43b7905a(iVar11,DAT_44020d44);
            FUN_43b7983e(iVar11,DAT_44020408);
            iVar4 = DAT_44022550;
            FUN_43b79172(iVar11,DAT_44022550);
            FUN_43b791b2(iVar11,iVar4 + 8);
            FUN_43b791f2(iVar11,iVar4 + 0x10);
            FUN_43b79232(iVar11,iVar4 + 0x18);
            iVar4 = DAT_44026278;
            FUN_43b79272(iVar11,DAT_44026278);
            FUN_43b7929e(iVar11,iVar4 + 8);
            FUN_43b792ca(iVar11,iVar4 + 0x10);
            FUN_43b792f6(iVar11,iVar4 + 0x18);
            FUN_43b79322(iVar11,DAT_440225a8);
          }
          if (iVar12 != 0) {
            FUN_43b798cc(iVar12,DAT_44026320);
          }
          if (iVar11 != 0) {
            FUN_43b79000(iVar11,0);
          }
          if (iVar7 != 0) {
            FUN_43b79f26(iVar7,*(undefined2 *)(DAT_44026320 + 2));
          }
          if (iVar8 != 0) {
            auStack_2c[0] = *(undefined2 *)(DAT_44026320 + 2);
            FUN_43b7a6f6(iVar8,auStack_2c);
          }
          if (iVar9 != 0) {
            FUN_43b7a3d2(iVar9,DAT_44022b5c);
          }
          if (iVar6 != 0) {
            FUN_43b69cc0(iVar6,DAT_44024f08);
          }
          if (iStack_8c != 0) {
            FUN_43b6be90(iStack_8c,*DAT_440221d8);
          }
          if (iStack_90 != 0) {
            FUN_43b69c22(iStack_90,DAT_440228c4);
          }
        }
        FUN_43b7196a(DAT_44025d44);
        FUN_43b1354e(iVar11);
        FUN_43887d18(*(undefined1 *)(iVar2 + 0x54),iStack_94,iVar6,iStack_90);
        if (*(int *)(iVar2 + 0x514) != 0x1a) {
          FUN_43888098(*(undefined1 *)(iVar2 + 0x54),uStack_84,uStack_80,uStack_7c,uStack_78,uVar10)
          ;
        }
        if ((*pcVar1 != '\0') && (iStack_94 != 0)) {
          FUN_43b6b0a4(iStack_94,pcVar1 + 0x2f4);
        }
        uStack_48 = uStack_48 & 0xffffff00;
        uStack_38 = uStack_38 & 0xffffff00;
        if (iStack_88 != 0) {
          FUN_43b6b870(iStack_88,*(undefined2 *)(DAT_44021818 + 0x1c),0,0,uStack_48,0,1,0,uStack_38,
                       uStack_34,uStack_30);
        }
        return;
      }
      iStack_18 = iVar4;
      FUN_4380fcac(3,9,1,&DAT_43cb12a1);
      FUN_43902718(s_CamCore_Start_Error_0x_x_43cb12b5,iVar4);
      FUN_437964d4();
    }
    *(undefined1 *)(param_1 + 0xd70) = 1;
  }
  return;
}

