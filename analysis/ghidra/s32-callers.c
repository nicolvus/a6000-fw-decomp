/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43549e48" */

undefined4 FUN_43549e48(undefined4 param_1)

{
  byte *pbVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  undefined4 uVar7;
  char *pcVar8;
  int iVar9;
  uint uVar10;
  int *piVar11;
  undefined1 uVar12;
  int iVar13;
  uint in_fpscr;
  double dVar14;
  uint uVar15;
  double dVar16;
  double dVar17;
  int iStack_1c8;
  int iStack_1c4;
  int iStack_1c0;
  undefined4 uStack_1bc;
  int *piStack_1b8;
  undefined4 uStack_1b4;
  int iStack_1b0;
  undefined1 uStack_1ac;
  undefined1 uStack_1ab;
  undefined2 uStack_1aa;
  undefined2 uStack_1a8;
  undefined2 uStack_1a6;
  undefined2 uStack_1a4;
  undefined2 uStack_1a2;
  undefined2 uStack_1a0;
  undefined2 uStack_19e;
  undefined2 uStack_19c;
  undefined2 uStack_19a;
  undefined2 uStack_198;
  undefined2 uStack_196;
  undefined2 uStack_194;
  int iStack_190;
  char cStack_18c;
  undefined1 uStack_18b;
  undefined1 uStack_18a;
  undefined4 uStack_188;
  int iStack_184;
  int iStack_180;
  int iStack_17c;
  undefined1 uStack_178;
  undefined4 uStack_174;
  undefined4 uStack_170;
  int iStack_16c;
  int iStack_168;
  undefined1 uStack_164;
  undefined1 uStack_120;
  undefined1 uStack_100;
  undefined4 uStack_e4;
  undefined2 uStack_e0;
  undefined2 uStack_de;
  undefined2 uStack_dc;
  undefined2 uStack_da;
  undefined1 uStack_d8;
  undefined4 uStack_d4;
  int iStack_d0;
  int iStack_cc;
  undefined1 uStack_c8;
  undefined1 uStack_c7;
  undefined1 auStack_c4 [20];
  undefined4 uStack_b0;
  undefined4 uStack_84;
  undefined1 uStack_80;
  uint uStack_7c;
  undefined1 uStack_78;
  undefined1 uStack_77;
  byte bStack_76;
  int iStack_74;
  undefined1 uStack_6c;
  undefined1 uStack_6b;
  int iStack_68;
  int iStack_64;
  int iStack_60;
  undefined1 uStack_5b;
  byte bStack_59;
  byte bStack_58;
  byte bStack_56;
  byte bStack_55;
  uint uStack_54;
  byte bStack_50;
  undefined1 auStack_4c [20];
  uint uStack_38;
  int aiStack_34 [2];
  
  iVar4 = FUN_4378f9b4();
  iVar9 = **(int **)(iVar4 + 4);
  iVar4 = FUN_4378f9b4();
  uVar10 = (uint)*(byte *)(*(int *)(iVar4 + 0x20) + 1);
  if (*(int *)(DAT_44020e90 + 0x40) == 1) {
    iVar4 = 2;
  }
  else {
    iVar4 = 1;
  }
  piVar5 = (int *)FUN_43ae75dc(param_1);
  if ((char)piVar5[0x35c] != '\0') {
    return 5;
  }
  iVar6 = FUN_43afdf16(param_1);
  if (iVar6 == 0) {
    iVar6 = FUN_43795b04();
    if (iVar6 == 0) {
      return 5;
    }
    iVar6 = FUN_43799a94(1,0,piVar5[0x7f],iVar9,uVar10,0,1,0,iVar4 + 1,piVar5 + 0x35a,0);
    uVar7 = DAT_44025f5c;
    if (iVar6 == 0) {
      return 5;
    }
    iVar6 = FUN_43ae8cc8(DAT_44025f5c);
    pbVar1 = DAT_4402546c;
    if (iVar6 != 0) {
      if (*DAT_4402546c != 0) {
        iVar4 = FUN_43799a94(1,1,0,iVar9,uVar10,0,1,0,iVar4 + 1,piVar5 + 0x35a,piVar5 + 0x147);
        if (iVar4 == 0) {
          return 5;
        }
        FUN_43728c18(piVar5 + 0x142,piVar5 + 0x143,piVar5 + 0x144);
        FUN_43acc282(piVar5[0x147],*pbVar1 - 1,piVar5 + 0xf9,0xfff,0xfff,0xfff);
      }
      FUN_4378e5ac(uVar7);
    }
    FUN_4381106c(piVar5);
    return 0;
  }
  if (iVar6 == 1) {
    piVar5[0x315] = piVar5[0x313];
    uVar7 = FUN_4378f9b4();
    iVar6 = FUN_4378e6a0(DAT_44025f5c,uVar7);
    if (iVar6 == 0) {
      return 5;
    }
    if ((piVar5[0x6c] - 2U < 2) &&
       (iVar6 = FUN_4378f9b4(), *(int *)(*(int *)(iVar6 + 4) + 0xc) != 1)) {
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
    iVar13 = iVar4 + 1;
    piVar11 = piVar5 + 0x35a;
    iVar6 = FUN_43799a94(1,1,0,iVar9,uVar10,0,1,0,iVar13,piVar11,piVar5 + 0x147);
    if (iVar6 == 0) {
      return 5;
    }
    FUN_43728c18(piVar5 + 0x142,piVar5 + 0x143,piVar5 + 0x144);
    pbVar1 = DAT_4402546c;
    uVar12 = *(undefined1 *)((int)piVar5 + 0x3fa);
    if (DAT_4402546c[0x4e] == 0xff) {
      uVar12 = 0;
    }
    else if (DAT_4402546c[0x4e] != 0) {
      uVar12 = 1;
    }
    iVar6 = piVar5[0x147];
    uVar7 = FUN_437d9d08();
    FUN_43acc2ee(iVar6,uVar12,uVar7);
    if ((char)piVar5[0x149] != '\0') {
      iVar6 = FUN_43799a94(1,0x10,0x42,iVar9,uVar10,0,1,0,iVar13,piVar11,aiStack_34);
      if (iVar6 == 0) {
        return 5;
      }
      iVar6 = FUN_43799a94(1,6,0,iVar9,uVar10,0,1,0,iVar13,piVar11,piVar5 + 0x308);
      if (iVar6 == 0) {
        return 5;
      }
      FUN_43b0417e(0xffffffff,0xffffffff,0,0);
      FUN_43b0419c(0,0);
      iVar6 = FUN_43ae8c4a(iVar9 + 1);
      uStack_38 = 0;
      FUN_43ad2dfc(0xfff,&uStack_38);
      if ((char)piVar5[0x306] == '\0') {
        uVar7 = 1;
      }
      else if (DAT_43f9b2aa < 0x3c) {
        uVar7 = 0x11;
      }
      else {
        uVar7 = 1;
      }
      iVar6 = FUN_439035e0(piVar5 + 7,piVar5[99],iVar6 * 0x100 + (uStack_38 >> 4),uVar7,0,5);
      if (iVar6 == 0) {
        if ((pbVar1[2] & 1) == 0) {
          iVar6 = 10;
        }
        else {
          iVar6 = 7;
        }
        piVar5[0x166] = iVar6;
        piVar5[0x167] = 2;
        piVar5[0x172] = 0;
        piVar5[0x173] = 0;
        piVar5[0x168] = aiStack_34[0];
        piVar5[0x175] = 1;
        piVar5[0x17f] = 0;
        piVar5[0x1ce] = 0;
        piVar5[0x176] = piVar5[9];
        piVar5[0x1d9] = 0;
        piVar5[0x177] = piVar5[10];
        piVar5[0x17e] = (uint)((char)piVar5[100] != '\0');
        FUN_439c5320(piVar5 + 0x19a,piVar5 + 0x166,0x68);
        DAT_43f9b2aa = 0;
      }
      else {
        *(undefined1 *)(piVar5 + 0x83) = 0;
        *(undefined1 *)(piVar5 + 0x149) = 0;
        DAT_43f9b2aa = DAT_43f9b2aa + 1;
      }
    }
    iVar6 = FUN_43799a94(1,0xe,0,iVar9,uVar10,0,1,0,iVar13,piVar11,0);
    if (iVar6 != 0) {
      bVar3 = pbVar1[0x70];
      if (bVar3 == 0) {
        iVar6 = FUN_43affc8a(piVar5[0x142]);
        uStack_78 = *(undefined1 *)((int)piVar5 + 0x20e);
        uStack_77 = *(undefined1 *)((int)piVar5 + 0x20f);
        iStack_74 = piVar5[0x82];
        uStack_6c = (undefined1)piVar5[0x7f];
        uStack_6b = (undefined1)piVar5[0x313];
        uStack_7c = (uint)(iVar6 == 1);
        iStack_68 = piVar5[0x7b];
        iStack_64 = piVar5[0x7c];
        iStack_60 = piVar5[0x7d];
        uStack_5b = (undefined1)piVar5[0xf8];
        bStack_76 = bVar3;
        bStack_59 = bVar3;
        bStack_58 = bVar3;
        bStack_56 = bVar3;
        bStack_55 = bVar3;
        uStack_54 = (uint)bVar3;
        bStack_50 = bVar3;
        FUN_439e34d4(&uStack_7c);
      }
      FUN_43799a94(1,0xf,0,iVar9,uVar10,0,1,0,iVar13,piVar11,0);
      iVar6 = FUN_43799a94(1,0xd,piVar5[0x7f],iVar9,uVar10,0,1,0,iVar13,piVar11,piVar5 + 0x148);
      if (iVar6 == 0) {
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
      if (uVar10 == 1) {
        FUN_43b03a74(auStack_4c,DAT_440259b4);
        FUN_4379704c(param_1,auStack_4c,piVar5);
      }
      iVar6 = FUN_4378f9b4();
      if (((*(byte *)(*(int *)(iVar6 + 8) + 0x26a) & 1) != 0) &&
         (iVar6 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar6 + 8) + 0x268) & 4) != 0)) {
        iVar6 = FUN_4378f9b4();
        *(undefined2 *)((int)piVar5 + 0xd26) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x96);
        iVar6 = FUN_4378f9b4();
        *(undefined2 *)(piVar5 + 0x34a) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x98);
        iVar6 = FUN_4378f9b4();
        *(undefined2 *)((int)piVar5 + 0xd2a) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x9a);
        iVar6 = FUN_4378f9b4();
        *(undefined2 *)(piVar5 + 0x34b) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x9c);
        iVar6 = FUN_4378f9b4();
        if (*(int *)(*(int *)(iVar6 + 0x2c) + 0xa4) != 0) {
          iVar6 = FUN_4378f9b4();
          dVar14 = (double)VectorUnsignedToFloat
                                     ((uint)*(ushort *)(*(int *)(iVar6 + 0x38) + 0x38),
                                      (byte)(in_fpscr >> 0x16) & 3);
          iVar6 = FUN_4378f9b4();
          dVar16 = (double)VectorUnsignedToFloat
                                     (*(undefined4 *)(*(int *)(iVar6 + 0x2c) + 0xa0),
                                      (byte)(in_fpscr >> 0x16) & 3);
          iVar6 = FUN_4378f9b4();
          dVar17 = (double)VectorUnsignedToFloat
                                     (*(undefined4 *)(*(int *)(iVar6 + 0x2c) + 0xa4),
                                      (byte)(in_fpscr >> 0x16) & 3);
          dVar17 = (dVar14 * 100.0 * dVar16) / dVar17;
          if (((int)((uint)(dVar17 < 126500.0) << 0x1f) < 0) &&
             (uVar15 = VectorFloatToUnsigned(dVar17,3), uVar15 != 0)) {
            if (uVar15 < 0x31ce) {
              cVar2 = FUN_4355faf0(uVar15 + 0x32,100);
              bVar3 = cVar2 << 1;
            }
            else {
              cVar2 = FUN_4355faf0(uVar15 + 500,1000);
              bVar3 = cVar2 << 1 | 1;
            }
            *(byte *)((int)piVar5 + 0xd2e) = bVar3;
            goto LAB_4354a3de;
          }
        }
        *(undefined1 *)((int)piVar5 + 0xd2e) = 0xff;
      }
LAB_4354a3de:
      if ((char)piVar5[0x83] != '\0') {
        FUN_43b03a5e(&iStack_1c8);
        uStack_1bc = 0;
        iStack_1c8 = piVar5[0x7b];
        iStack_1c4 = piVar5[0x7c];
        iStack_1c0 = piVar5[0x7d];
        piStack_1b8 = piVar5 + 7;
        uStack_1b4 = FUN_43ae8c4a(iVar9 + 2);
        iStack_1b0 = piVar5[0x313];
        uStack_1ab = 0;
        uStack_1ac = (undefined1)piVar5[0x7e];
        uStack_1aa = (undefined2)piVar5[0x6e];
        uStack_1a8 = *(undefined2 *)((int)piVar5 + 0x1ba);
        iVar6 = piVar5[100];
        if ((char)iVar6 == '\0') {
          uStack_1a6 = FUN_43ae9e86(*(undefined2 *)((int)piVar5 + 0x19e),0x40);
        }
        else {
          uStack_1a6 = FUN_43ae98f8();
        }
        uStack_1a4 = (undefined2)piVar5[0x68];
        uStack_19e = *(undefined2 *)((int)piVar5 + 0x19e);
        iStack_190 = piVar5[0x6d];
        iStack_184 = piVar5[0x13f];
        uStack_1a2 = 0;
        uStack_1a0 = 0;
        iStack_180 = piVar5[0x140];
        uStack_19a = 0;
        uStack_198 = 0;
        iStack_17c = piVar5[0x141];
        uStack_18b = 0;
        uStack_18a = 0;
        uStack_188 = 0;
        uStack_164 = 0;
        uStack_178 = piVar5[0x2f5] == 1;
        iStack_16c = piVar5[0x355];
        uStack_174 = 0xffffffff;
        iStack_168 = piVar5[0x356];
        uStack_170 = 0xffffffff;
        uStack_120 = 0;
        uStack_100 = 0;
        uStack_e0 = *(undefined2 *)((int)piVar5 + 0xd26);
        uStack_d4 = 0xffffffff;
        uStack_e4 = 0;
        uStack_de = (undefined2)piVar5[0x34a];
        uStack_c8 = 0;
        uStack_c7 = 0;
        uStack_dc = *(undefined2 *)((int)piVar5 + 0xd2a);
        uStack_da = (undefined2)piVar5[0x34b];
        uStack_d8 = *(undefined1 *)((int)piVar5 + 0xd2e);
        iStack_d0 = piVar5[0x6c];
        iStack_cc = piVar5[0x361];
        uStack_19c = uStack_1a4;
        uStack_196 = uStack_19e;
        uStack_194 = uStack_1a4;
        cStack_18c = (char)iVar6;
        FUN_4379b44c(0,&iStack_1c8);
        iVar6 = FUN_4378f9b4();
        iVar6 = FUN_4355faf0(*(int *)(*(int *)(iVar6 + 4) + 0x1c) + 0x3e7ff,0x3e800);
        if (*(char *)((int)piVar5 + 0x20d) == '\0') {
          for (uVar10 = uVar10 + 2 + iVar4; iVar4 = FUN_4378f9b4(),
              **(byte **)(iVar4 + 0x20) <= uVar10; uVar10 = uVar10 - 4) {
            iVar9 = iVar9 + 1;
          }
          iVar4 = FUN_4378f9b4();
          uStack_38 = *(ushort *)(*(int *)(iVar4 + 4) + 0x22) * uVar10;
          iVar4 = 2;
        }
        else {
          iVar9 = iVar9 + piVar5[0x313] + 1 + piVar5[0x318];
          iVar4 = FUN_4378f9b4();
          uStack_38 = (int)(uint)*(ushort *)(*(int *)(iVar4 + 4) + 0x20) >> 2;
          iVar4 = piVar5[0x313] + piVar5[0x318] + 1;
        }
        FUN_43ad2dfc(0xfff,&uStack_38);
        iVar9 = FUN_43ae8c4a(iVar9);
        iVar4 = FUN_43b2a2d0(piVar5 + 7,iVar9 * 0x100 + (uStack_38 >> 4),iVar6 * iVar4,0,5);
        if (iVar4 != 0) {
          return 5;
        }
      }
      if (((char)piVar5[0x83] != '\0') && (*(char *)((int)piVar5 + 0x20d) != '\0')) {
        FUN_43afb42e(auStack_c4);
        FUN_43afb476(auStack_c4,DAT_44021030);
        uStack_b0 = 0;
        uStack_80 = 2;
        uStack_84 = FUN_43afbf44(param_1);
        (**(code **)(*piVar5 + 8))(piVar5);
        iVar4 = FUN_4381bbf0(param_1,auStack_c4,piVar5);
        if (iVar4 != 0) {
          FUN_43b04730();
        }
      }
      return 5;
    }
    FUN_4380f5fc(3,9,1,&DAT_43cb0f3e);
    pcVar8 = s_SyncResMgr__Get_IDT_OPD_failure_43cb0f52;
  }
  else {
    FUN_4380f5fc(3,9,1,&DAT_43cb0f14);
    pcVar8 = s_Sequence_Stage_Error__43cb0f28;
  }
  FUN_43902718(pcVar8);
  return 5;
}


/* query "4354fad8" */

undefined4 FUN_4354fad8(undefined4 param_1)

{
  byte *pbVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  undefined1 uVar13;
  int iVar14;
  uint in_fpscr;
  double dVar15;
  double dVar16;
  double dVar17;
  undefined4 uStack_198;
  undefined4 uStack_194;
  undefined4 uStack_190;
  int iStack_18c;
  int iStack_188;
  undefined4 uStack_184;
  undefined4 uStack_180;
  undefined1 uStack_17c;
  undefined1 uStack_17b;
  undefined2 uStack_17a;
  undefined2 uStack_178;
  undefined2 uStack_176;
  undefined2 uStack_174;
  undefined2 uStack_172;
  undefined2 uStack_170;
  undefined2 uStack_16e;
  undefined2 uStack_16c;
  undefined2 uStack_16a;
  undefined2 uStack_168;
  undefined2 uStack_166;
  undefined2 uStack_164;
  undefined4 uStack_160;
  char cStack_15c;
  undefined1 uStack_15b;
  undefined1 uStack_15a;
  undefined4 uStack_158;
  undefined4 uStack_154;
  undefined4 uStack_150;
  undefined4 uStack_14c;
  undefined1 uStack_148;
  undefined4 uStack_144;
  undefined4 uStack_140;
  undefined4 uStack_13c;
  undefined4 uStack_138;
  undefined1 uStack_134;
  undefined1 uStack_f0;
  undefined1 uStack_d0;
  undefined4 uStack_b4;
  undefined2 uStack_b0;
  undefined2 uStack_ae;
  undefined2 uStack_ac;
  undefined2 uStack_aa;
  undefined1 uStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined4 uStack_9c;
  undefined1 uStack_98;
  undefined1 uStack_97;
  uint uStack_94;
  undefined1 uStack_90;
  char cStack_8f;
  undefined1 uStack_8e;
  undefined4 uStack_8c;
  undefined1 uStack_84;
  undefined1 uStack_83;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined1 uStack_73;
  undefined1 uStack_71;
  undefined1 uStack_70;
  undefined1 uStack_6e;
  undefined1 uStack_6d;
  undefined4 uStack_6c;
  undefined1 uStack_68;
  undefined1 auStack_64 [20];
  undefined1 auStack_50 [8];
  undefined4 uStack_48;
  undefined4 uStack_44;
  uint uStack_40;
  uint uStack_3c;
  uint uStack_38;
  uint auStack_34 [2];
  
  iVar4 = FUN_4378f9b4();
  iVar11 = **(int **)(iVar4 + 4);
  iVar4 = FUN_4378f9b4();
  uVar8 = (uint)*(byte *)(*(int *)(iVar4 + 0x20) + 1);
  iVar4 = FUN_43ae75dc(param_1);
  iVar5 = FUN_4378f9b4();
  uVar9 = (uint)*(byte *)(iVar4 + 0xd70);
  if (**(int **)(iVar5 + 8) == 2) {
    iVar5 = 1;
  }
  else {
    iVar5 = 2;
  }
  if (uVar9 == 0) {
    iVar6 = FUN_43afdf16(param_1);
    if (iVar6 == 1) {
      uVar7 = FUN_4378f9b4();
      iVar6 = FUN_4378e6a0(DAT_44025f5c,uVar7);
      if (iVar6 != 0) {
        iVar5 = iVar5 + 1;
        iVar12 = iVar4 + 0xd68;
        iVar6 = FUN_43799a94(1,1,0,iVar11,uVar8,0,1,0,iVar5,iVar12,iVar4 + 0x51c);
        if (iVar6 != 0) {
          FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
          pbVar1 = DAT_4402546c;
          uVar13 = *(undefined1 *)(iVar4 + 0x3fa);
          if (DAT_4402546c[0x4e] == 0xff) {
            uVar13 = 0;
          }
          else if (DAT_4402546c[0x4e] != 0) {
            uVar13 = 1;
          }
          uVar10 = *(undefined4 *)(iVar4 + 0x51c);
          uVar7 = FUN_437d9d08();
          FUN_43acc2ee(uVar10,uVar13,uVar7);
          iVar6 = FUN_43799a94(1,0x10,0x43,iVar11,uVar8,0,1,0,iVar5,iVar12,auStack_34);
          if ((iVar6 != 0) &&
             (iVar6 = FUN_43799a94(1,4,0,iVar11,uVar8,0,1,0,iVar5,iVar12,iVar4 + 0xc20), iVar6 != 0)
             ) {
            iVar6 = FUN_4381c04c(0,*(undefined4 *)(iVar4 + 0x184),auStack_50);
            if (iVar6 == 0) {
              *(undefined1 *)(iVar4 + 0x524) = 0;
              *(undefined1 *)(iVar4 + 0x20c) = 0;
            }
            *(undefined4 *)(iVar4 + 0x598) = 10;
            *(undefined4 *)(iVar4 + 0x59c) = 2;
            *(undefined4 *)(iVar4 + 0x5c8) = 0;
            *(undefined4 *)(iVar4 + 0x5cc) = 0;
            *(uint *)(iVar4 + 0x5a0) = auStack_34[0];
            *(undefined4 *)(iVar4 + 0x5d4) = 1;
            *(undefined4 *)(iVar4 + 0x5d8) = uStack_48;
            *(undefined4 *)(iVar4 + 0x5dc) = uStack_44;
            *(uint *)(iVar4 + 0x5f8) = (uint)(*(char *)(iVar4 + 0x188) != '\0');
            if (*(int *)(iVar4 + 0xd5c) == 5) {
              uVar7 = 5;
            }
            else {
              uVar7 = 0;
            }
            *(undefined4 *)(iVar4 + 0x5fc) = uVar7;
            iVar6 = FUN_43799a94(1,0xe,0,iVar11,uVar8,0,1,0,iVar5,iVar12,0);
            if (iVar6 != 0) {
              if (((pbVar1[0x70] == 0) && (iVar6 = FUN_4378003c(), iVar6 == 0)) &&
                 ((cVar2 = *(char *)(iVar4 + 0x20f), cVar2 != '\0' ||
                  ((*(char *)(iVar4 + 0x20e) != '\0' || (*(char *)(iVar4 + 0x210) != '\0')))))) {
                iVar6 = FUN_43affc8a(*(undefined4 *)(iVar4 + 0x508));
                uStack_94 = (uint)(iVar6 == 1);
                uStack_90 = *(undefined1 *)(iVar4 + 0x20e);
                uStack_8e = 0;
                uStack_8c = *(undefined4 *)(iVar4 + 0x208);
                uStack_71 = 0;
                uStack_70 = 0;
                uStack_6e = 0;
                uStack_6d = 0;
                uStack_84 = (undefined1)*(undefined4 *)(iVar4 + 0x1fc);
                uStack_6c = 0;
                uStack_83 = (undefined1)*(undefined4 *)(iVar4 + 0xc4c);
                uStack_80 = *(undefined4 *)(iVar4 + 0x1ec);
                uStack_7c = *(undefined4 *)(iVar4 + 0x1f0);
                uStack_78 = *(undefined4 *)(iVar4 + 500);
                uStack_73 = (undefined1)*(undefined4 *)(iVar4 + 0x3e0);
                uStack_68 = *(int *)(iVar4 + 0xd78) == 1;
                cStack_8f = cVar2;
                FUN_439e34d4(&uStack_94);
              }
              FUN_43799a94(1,0xf,0,iVar11,uVar8,0,1,0,iVar5,iVar12,0);
              iVar5 = FUN_43799a94(1,0xd,*(undefined4 *)(iVar4 + 0x1fc),iVar11,uVar8,0,1,0,iVar5,
                                   iVar12,iVar4 + 0x520);
              if (iVar5 != 0) {
                FUN_43728c4c(iVar4 + 0x514,iVar4 + 0x518);
                FUN_437956a4(*(undefined4 *)(iVar4 + 0x520));
                FUN_43814008(iVar4);
                FUN_4381061c(iVar4);
                FUN_438106ec(iVar4);
                FUN_4354a678(iVar4);
                FUN_43810e7c(iVar4);
                FUN_43810fa8(iVar4);
                FUN_4381127c(iVar4);
                if (uVar8 == 1) {
                  FUN_43b03a74(auStack_64,DAT_440259b4);
                  FUN_4379704c(param_1,auStack_64,iVar4);
                }
                if (*(char *)(iVar4 + 0x20c) == '\0') {
                  return 5;
                }
                return 0;
              }
            }
          }
        }
      }
    }
    else if (iVar6 == 0) {
      iVar6 = FUN_43795b04();
      if (iVar6 != 0) {
        iVar6 = FUN_43799a94(1,0,*(undefined4 *)(iVar4 + 0x1fc),iVar11,uVar8,0,1,0,iVar5 + 1,
                             iVar4 + 0xd68,0);
        uVar7 = DAT_44025f5c;
        if (iVar6 != 0) {
          iVar6 = FUN_43ae8cc8(DAT_44025f5c);
          pbVar1 = DAT_4402546c;
          if (iVar6 != 0) {
            if (*DAT_4402546c != 0) {
              iVar5 = FUN_43799a94(1,1,0,iVar11,uVar8,0,1,0,iVar5 + 1,iVar4 + 0xd68,iVar4 + 0x51c);
              if (iVar5 == 0) {
                return 5;
              }
              FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
              FUN_43acc282(*(undefined4 *)(iVar4 + 0x51c),*pbVar1 - 1,iVar4 + 0x3e4,0xfff,0xfff,
                           0xfff);
            }
            FUN_4378e5ac(uVar7);
          }
          FUN_4381106c(iVar4);
          return 0;
        }
      }
    }
    else if (iVar6 == 2) {
      if (*(char *)(iVar4 + 0x20c) != '\0') {
        iVar14 = iVar5 + 1;
        iVar12 = iVar4 + 0xd68;
        iVar6 = FUN_43799a94(1,5,0,iVar11,uVar8,0,1,0,iVar14,iVar12,iVar4 + 0xc28);
        if (iVar6 != 0) {
          FUN_43b041dc(*(int *)(iVar4 + 0xd5c) != 5,iVar11);
          uStack_38 = uVar9;
          auStack_34[0] = uVar9;
          if ((*(int *)(iVar4 + 0xd5c) == 5) &&
             ((iVar6 = FUN_43799a94(1,0x11,0x43,iVar11,uVar8,0,1,0,iVar14,iVar12,auStack_34),
              iVar6 == 0 ||
              (iVar6 = FUN_43799a94(1,8,0,iVar11,uVar8,0,1,0,iVar14,iVar12,&uStack_38), iVar6 == 0))
             )) {
            return 5;
          }
          if (uVar8 == 3) {
            uStack_3c = 0;
            iVar6 = iVar11 + 1;
          }
          else {
            iVar6 = FUN_4378f9b4();
            uStack_3c = (uint)*(ushort *)(*(int *)(iVar6 + 4) + 0x22) * (uVar8 + 1);
            FUN_43ad2dfc(0xfff,&uStack_3c);
            iVar6 = iVar11;
          }
          iVar12 = iVar4 + 0x1c;
          iVar6 = FUN_439035e0(iVar12,*(undefined4 *)(iVar4 + 0x18c),
                               iVar6 * 0x100 + (uStack_3c >> 4),1,0,5);
          if (iVar6 != 0) {
            return 5;
          }
          if (*(char *)(iVar4 + 0xd4c) != '\0') {
            *(int *)(iVar4 + 0xd50) = iVar11;
            *(undefined1 *)(iVar4 + 0xd4c) = 0;
          }
          iVar6 = FUN_4378f9b4();
          if (((*(byte *)(*(int *)(iVar6 + 8) + 0x26a) & 1) != 0) &&
             (iVar6 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar6 + 8) + 0x268) & 4) != 0)) {
            iVar6 = FUN_4378f9b4();
            *(undefined2 *)(iVar4 + 0xd26) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x96);
            iVar6 = FUN_4378f9b4();
            *(undefined2 *)(iVar4 + 0xd28) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x98);
            iVar6 = FUN_4378f9b4();
            *(undefined2 *)(iVar4 + 0xd2a) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x9a);
            iVar6 = FUN_4378f9b4();
            *(undefined2 *)(iVar4 + 0xd2c) = *(undefined2 *)(*(int *)(iVar6 + 0x2c) + 0x9c);
            iVar6 = FUN_4378f9b4();
            if (*(int *)(*(int *)(iVar6 + 0x2c) + 0xa4) != 0) {
              iVar6 = FUN_4378f9b4();
              dVar15 = (double)VectorUnsignedToFloat
                                         ((uint)*(ushort *)(*(int *)(iVar6 + 0x38) + 0x38),
                                          (byte)(in_fpscr >> 0x16) & 3);
              iVar6 = FUN_4378f9b4();
              dVar16 = (double)VectorUnsignedToFloat
                                         (*(undefined4 *)(*(int *)(iVar6 + 0x2c) + 0xa0),
                                          (byte)(in_fpscr >> 0x16) & 3);
              iVar6 = FUN_4378f9b4();
              dVar17 = (double)VectorUnsignedToFloat
                                         (*(undefined4 *)(*(int *)(iVar6 + 0x2c) + 0xa4),
                                          (byte)(in_fpscr >> 0x16) & 3);
              dVar17 = (dVar15 * 100.0 * dVar16) / dVar17;
              if (((int)((uint)(dVar17 < 126500.0) << 0x1f) < 0) &&
                 (uVar9 = VectorFloatToUnsigned(dVar17,3), uVar9 != 0)) {
                if (uVar9 < 0x31ce) {
                  cVar2 = FUN_4355faf0(uVar9 + 0x32,100);
                  bVar3 = cVar2 << 1;
                }
                else {
                  cVar2 = FUN_4355faf0(uVar9 + 500,1000);
                  bVar3 = cVar2 << 1 | 1;
                }
                *(byte *)(iVar4 + 0xd2e) = bVar3;
                goto LAB_435500c6;
              }
            }
            *(undefined1 *)(iVar4 + 0xd2e) = 0xff;
          }
LAB_435500c6:
          FUN_43b03a5e(&uStack_198);
          FUN_43811484(iVar4,iVar11);
          uStack_198 = *(undefined4 *)(iVar4 + 0x1ec);
          uStack_194 = *(undefined4 *)(iVar4 + 0x1f0);
          uStack_190 = *(undefined4 *)(iVar4 + 500);
          if (iVar5 == 1) {
            if (uVar8 == 0) {
              iVar6 = FUN_4378de7c();
              if (iVar6 == 0) {
                iStack_18c = 0xc;
              }
              else {
                iStack_18c = 0xf;
              }
            }
            else {
              iVar6 = FUN_4378de7c();
              if (iVar6 == 0) {
                iStack_18c = (uVar8 + 0x3fffffff) * 4;
              }
              else {
                iStack_18c = uVar8 * 5 + -5;
              }
            }
          }
          else if (uVar8 == 3) {
            iStack_18c = 0;
          }
          else {
            iVar6 = FUN_4378de7c();
            if (iVar6 == 0) {
              iStack_18c = 8;
            }
            else {
              iStack_18c = 10;
            }
          }
          iVar6 = iVar11;
          if (uVar8 == 3) {
            iVar6 = iVar11 + 1;
          }
          iStack_188 = iVar12;
          uStack_184 = FUN_43ae8c4a(iVar6);
          uStack_180 = *(undefined4 *)(iVar4 + 0xc54);
          uStack_17c = (undefined1)*(undefined4 *)(iVar4 + 0x1f8);
          uStack_17b = FUN_43ae8c4a(iVar11 - *(int *)(iVar4 + 0xd50));
          uStack_17a = *(undefined2 *)(iVar4 + 0x1b8);
          uStack_178 = *(undefined2 *)(iVar4 + 0x1ba);
          cVar2 = *(char *)(iVar4 + 400);
          if (cVar2 == '\0') {
            uStack_176 = FUN_43ae9e86(*(undefined2 *)(iVar4 + 0x19e),0x40);
          }
          else {
            uStack_176 = FUN_43ae98f8();
          }
          uStack_174 = *(undefined2 *)(iVar4 + 0x1a0);
          uStack_16e = *(undefined2 *)(iVar4 + 0x19e);
          uStack_160 = *(undefined4 *)(iVar4 + 0x1b4);
          uStack_172 = 0;
          uStack_170 = 0;
          uStack_154 = *(undefined4 *)(iVar4 + 0x4fc);
          uStack_16a = 0;
          uStack_150 = *(undefined4 *)(iVar4 + 0x534);
          uStack_168 = 0;
          uStack_14c = *(undefined4 *)(iVar4 + 0x504);
          uStack_15b = 1;
          uStack_15a = 0;
          uStack_158 = 1;
          uStack_148 = *(int *)(iVar4 + 0xbd4) == 1;
          uStack_134 = 0;
          uStack_13c = *(undefined4 *)(iVar4 + 0xd54);
          uStack_144 = 0xffffffff;
          uStack_138 = *(undefined4 *)(iVar4 + 0xd58);
          uStack_140 = 0xffffffff;
          uStack_f0 = 0;
          uStack_d0 = 0;
          uStack_b4 = *(undefined4 *)(iVar4 + 0xd78);
          uStack_a4 = 0xffffffff;
          uStack_98 = 0;
          uStack_b0 = *(undefined2 *)(iVar4 + 0xd26);
          uStack_97 = 0;
          uStack_ae = *(undefined2 *)(iVar4 + 0xd28);
          uStack_ac = *(undefined2 *)(iVar4 + 0xd2a);
          uStack_aa = *(undefined2 *)(iVar4 + 0xd2c);
          uStack_a8 = *(undefined1 *)(iVar4 + 0xd2e);
          uStack_a0 = *(undefined4 *)(iVar4 + 0x1b0);
          uStack_9c = *(undefined4 *)(iVar4 + 0xd84);
          uStack_16c = uStack_174;
          uStack_166 = uStack_16e;
          uStack_164 = uStack_174;
          cStack_15c = cVar2;
          if (*(int *)(iVar4 + 0xd5c) == 5) {
            *(undefined4 *)(iVar4 + 0x6c8) = 0;
            *(undefined4 *)(iVar4 + 0x69c) = 2;
            *(uint *)(iVar4 + 0x6a0) = auStack_34[0];
            *(undefined4 *)(iVar4 + 0x6d0) = 10;
            *(undefined4 *)(iVar4 + 0x738) = 0;
            *(undefined4 *)(iVar4 + 0x6cc) = 0;
            FUN_43815e94(iVar4,uStack_38,auStack_34[0],0,1,uStack_16e,0);
          }
          else {
            *(undefined4 *)(iVar4 + 0x69c) = 0;
            *(undefined4 *)(iVar4 + 0x6a4) = 1;
            *(undefined4 *)(iVar4 + 0x6a8) = *(undefined4 *)(iVar4 + 0x24);
            *(undefined4 *)(iVar4 + 0x738) = 1;
            *(undefined4 *)(iVar4 + 0x6cc) = 0;
            *(undefined4 *)(iVar4 + 0x6ac) = *(undefined4 *)(iVar4 + 0x28);
            *(uint *)(iVar4 + 0x6c8) = (uint)(cVar2 != '\0');
          }
          FUN_43815a28(iVar4,*(undefined4 *)(iVar4 + 0xc28),0);
          FUN_435564e0(iVar4,iVar5,0);
          iVar4 = FUN_437286bc();
          if (iVar4 != 0) {
            if (uVar8 == 1) {
              FUN_4379b44c(0,&uStack_198);
            }
            FUN_4379b44c(1,&uStack_198);
          }
          uStack_40 = 0;
          iVar4 = FUN_4378f9b4();
          iVar4 = FUN_4355faf0(*(int *)(*(int *)(iVar4 + 4) + 0x1c) + 0x3e7ff,0x3e800);
          for (uVar8 = iVar5 + uVar8 + 2; iVar5 = FUN_4378f9b4(), **(byte **)(iVar5 + 0x20) <= uVar8
              ; uVar8 = uVar8 - 4) {
            iVar11 = iVar11 + 1;
          }
          iVar5 = FUN_4378f9b4();
          uStack_40 = *(ushort *)(*(int *)(iVar5 + 4) + 0x22) * uVar8;
          FUN_43ad2dfc(0xfff,&uStack_40);
          iVar5 = FUN_43ae8c4a(iVar11);
          FUN_43b2a2d0(iVar12,iVar5 * 0x100 + (uStack_40 >> 4),iVar4 << 1,0,5);
          return 5;
        }
      }
    }
    else {
      FUN_43813c00(3,9,1,&DAT_43cb0f14);
      FUN_43902718(s_Sequence_Stage_Error__43cb0f28);
    }
  }
  return 5;
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


/* query "4354d740" */

undefined4 FUN_4354d740(undefined4 param_1)

{
  byte *pbVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  char *pcVar10;
  int iVar11;
  uint uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined1 uVar15;
  uint in_fpscr;
  double dVar16;
  uint uVar17;
  double dVar18;
  double dVar19;
  undefined4 uStack_234;
  undefined4 uStack_230;
  undefined4 uStack_22c;
  undefined4 uStack_228;
  int iStack_224;
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined1 uStack_218;
  undefined1 uStack_217;
  undefined2 uStack_216;
  undefined2 uStack_214;
  undefined2 uStack_212;
  undefined2 uStack_210;
  undefined2 uStack_20e;
  undefined2 uStack_20c;
  undefined2 uStack_20a;
  undefined2 uStack_208;
  undefined2 uStack_206;
  undefined2 uStack_204;
  undefined2 uStack_202;
  undefined2 uStack_200;
  undefined4 uStack_1fc;
  undefined1 uStack_1f8;
  undefined1 uStack_1f7;
  undefined1 uStack_1f6;
  undefined4 uStack_1f4;
  undefined4 uStack_1f0;
  undefined4 uStack_1ec;
  undefined4 uStack_1e8;
  undefined1 uStack_1e4;
  undefined4 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined4 uStack_1d4;
  undefined1 uStack_1d0;
  undefined1 uStack_18c;
  undefined1 uStack_16c;
  undefined4 uStack_150;
  undefined2 uStack_14c;
  undefined2 uStack_14a;
  undefined2 uStack_148;
  undefined2 uStack_146;
  undefined1 uStack_144;
  undefined4 uStack_140;
  undefined4 uStack_13c;
  undefined4 uStack_138;
  undefined1 uStack_134;
  undefined1 uStack_133;
  undefined1 auStack_130 [20];
  undefined4 uStack_11c;
  undefined4 uStack_f0;
  undefined1 uStack_ec;
  uint uStack_e8;
  undefined1 uStack_e4;
  undefined1 uStack_e3;
  byte bStack_e2;
  undefined4 uStack_e0;
  undefined1 uStack_d8;
  undefined1 uStack_d7;
  undefined4 uStack_d4;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined1 uStack_c7;
  byte bStack_c5;
  byte bStack_c4;
  byte bStack_c2;
  byte bStack_c1;
  uint uStack_c0;
  byte bStack_bc;
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined1 auStack_80 [20];
  undefined1 auStack_6c [20];
  undefined1 auStack_58 [8];
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined1 auStack_48 [8];
  undefined1 auStack_40 [8];
  uint uStack_38;
  undefined4 auStack_34 [2];
  
  iVar4 = FUN_4378f9b4();
  iVar11 = **(int **)(iVar4 + 4);
  iVar4 = FUN_4378f9b4();
  bVar3 = *(byte *)(*(int *)(iVar4 + 0x20) + 1);
  uVar12 = (uint)bVar3;
  iVar4 = FUN_43ae75dc(param_1);
  if (*(char *)(iVar4 + 0xd70) != '\0') {
    return 5;
  }
  uVar5 = FUN_43afdf16(param_1);
  pbVar1 = DAT_4402546c;
  switch(uVar5) {
  case 0:
    if ((DAT_4402546c[0x1c] & 0x40) != 0) {
      puVar6 = (undefined4 *)FUN_4378f9b4();
      if ((*(short *)*puVar6 != 0x127) &&
         (puVar6 = (undefined4 *)FUN_4378f9b4(), *(short *)*puVar6 != 0x129)) {
        return 5;
      }
      iVar4 = FUN_4379a898();
      *(undefined1 *)(iVar4 + 0x5c) = 1;
      iVar4 = FUN_4379a320();
      *(undefined1 *)(iVar4 + 0xae5) = 1;
      iVar4 = FUN_4379a320();
      if (*(int *)(iVar4 + 0xae8) != 0) {
        return 5;
      }
      iVar4 = FUN_4379a320();
      *(int *)(iVar4 + 0xae8) = iVar11;
      return 5;
    }
    puVar6 = (undefined4 *)FUN_4378f9b4();
    if ((*(short *)*puVar6 == 0x129) && (iVar8 = FUN_4379a320(), *(char *)(iVar8 + 0xab7) == '\0'))
    {
      iVar8 = FUN_4379a320();
      *(undefined1 *)(iVar8 + 0xab7) = 1;
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_brchAdfStpAnalyze_43cb2821);
      }
      FUN_43afb42e(auStack_130);
      FUN_43afb476(auStack_130,DAT_4402418c);
      uStack_11c = 4;
      uStack_ec = 0;
      uStack_f0 = FUN_43afbf44(param_1);
      FUN_4381339c(auStack_6c);
      uVar5 = FUN_43b03a70(iVar4);
      uVar5 = FUN_4380d708(auStack_6c,uVar5,iVar4);
      iVar8 = FUN_4381bbf0(param_1,auStack_130,uVar5);
      if (iVar8 != 0) {
        FUN_43b04730();
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_brchAdfStpAnalyze_43cb2838);
      }
    }
    iVar8 = FUN_43795b04();
    if (iVar8 == 0) {
      return 5;
    }
    iVar8 = FUN_43799a94(1,0,*(undefined4 *)(iVar4 + 0x1fc),iVar11,uVar12,0,1,0,2,iVar4 + 0xd68,0);
    uVar5 = DAT_44025f5c;
    if (iVar8 == 0) {
      return 5;
    }
    iVar8 = FUN_43ae8cc8(DAT_44025f5c);
    if (iVar8 != 0) {
      iVar8 = FUN_43799a38(1,7,iVar11,0);
      if (iVar8 != 0) {
        return 5;
      }
      iVar8 = FUN_43799a38(1,9,iVar11,0);
      if (iVar8 != 0) {
        return 5;
      }
      iVar8 = FUN_43799a38(1,10,iVar11,0);
      if (iVar8 != 0) {
        return 5;
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_ResMgrFree_43cb284f);
      }
      FUN_43b0417e(0xe,0xffffffff,0,0);
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_ResMgrFree_43cb285f);
      }
      FUN_43b0419c(1,iVar11);
      FUN_4379a898();
      iVar8 = FUN_43ae9674();
      if (iVar8 == 0) {
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_JpgRBInit_43cb286f);
        }
        piVar7 = (int *)FUN_4378f9b4();
        FUN_4379a838(*(undefined4 *)(*piVar7 + 0xc0));
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_JpgRBInit_43cb287e);
        }
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_JpgRBAlloc_43cb288d);
        }
        uVar14 = FUN_4379a898();
        iVar8 = FUN_43903558(uVar14,0x172f17,1,0,5);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_JpgRBAlloc_43cb289d);
        }
        if (iVar8 != 0) {
          FUN_4381234c(3,9,1,&DAT_43cb28ad,0x172f17,iVar8);
          FUN_43902718(s_dmm_AllocNew_Err__JPGRINGBUF_uni_43cb28c1,0x172f17,iVar8);
          return 5;
        }
      }
      iVar8 = FUN_4379a898();
      iVar8 = FUN_43ae9674(iVar8 + 0x28);
      if (iVar8 == 0) {
        iVar8 = FUN_4379a898();
        iVar8 = FUN_43903558(iVar8 + 0x28,0x2d2,1,0,5);
        if (iVar8 != 0) {
          FUN_4381234c(3,9,1,&DAT_43cb28f9,0x2d2,iVar8);
          FUN_43902718(s_dmm_AllocNew_Err__JPG_INFO_BUF_u_43cb290d,0x2d2,iVar8);
          return 5;
        }
        iVar8 = FUN_4379a898();
        if (*(uint *)(iVar8 + 0x34) < 88000) {
          iVar8 = FUN_4379a898();
          FUN_4381234c(3,9,1,&DAT_43cb2947,*(undefined4 *)(iVar8 + 0x34),88000);
          iVar8 = FUN_4379a898();
          FUN_43902718(s_JpgImageInfo_buffer_size_error___43cb295b,*(undefined4 *)(iVar8 + 0x34),
                       88000);
          FUN_4381234c(5,0,1,&DAT_43c9b47c,s_Sequence_HSRecGolfshot_cpp_43cb2245,0xdf);
          FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_HSRecGolfshot_cpp_43cb2245,0xdf);
        }
        iVar8 = FUN_4379a898();
        iVar9 = FUN_4379a898();
        uVar14 = FUN_43561604(*(undefined4 *)(iVar9 + 0x30));
        *(undefined4 *)(iVar8 + 0x60) = uVar14;
      }
      if (*pbVar1 != 0) {
        iVar11 = FUN_43799a94(1,1,0,iVar11,uVar12,0,1,0,2,iVar4 + 0xd68,iVar4 + 0x51c);
        if (iVar11 == 0) {
          return 5;
        }
        FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
        FUN_43acc282(*(undefined4 *)(iVar4 + 0x51c),*pbVar1 - 1,iVar4 + 0x3e4,0xfff,0xfff,0xfff);
      }
      FUN_4378e5ac(uVar5);
    }
    if ((char)pbVar1[0x1c] < '\0') {
      FUN_43561540(s_b_ee_StrExp_43cb2986);
    }
    FUN_4381106c(iVar4);
    if (-1 < (char)pbVar1[0x1c]) {
      return 0;
    }
    pcVar10 = s_e_ee_StrExp_43cb2992;
    break;
  case 1:
    uVar5 = FUN_4378f9b4();
    iVar8 = FUN_4378e6a0(DAT_44025f5c,uVar5);
    pbVar1 = DAT_4402546c;
    if (iVar8 == 0) {
      return 5;
    }
    if ((char)DAT_4402546c[0x1c] < '\0') {
      FUN_43561540(s_b_ee_GetCAMDEV_43cb299e);
    }
    iVar9 = iVar4 + 0xd68;
    iVar8 = FUN_43799a94(1,1,0,iVar11,uVar12,0,1,0,2,iVar9,iVar4 + 0x51c);
    if (iVar8 == 0) {
      if (-1 < (char)pbVar1[0x1c]) {
        return 5;
      }
      pcVar10 = s_e_ee_GetCAMDEV_43cb29ad;
    }
    else {
      FUN_43728c18(iVar4 + 0x508,iVar4 + 0x50c,iVar4 + 0x510);
      uVar15 = *(undefined1 *)(iVar4 + 0x3fa);
      if (pbVar1[0x4e] == 0xff) {
        uVar15 = 0;
      }
      else if (pbVar1[0x4e] != 0) {
        uVar15 = 1;
      }
      uVar14 = *(undefined4 *)(iVar4 + 0x51c);
      uVar5 = FUN_437d9d08();
      FUN_43acc2ee(uVar14,uVar15,uVar5);
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_GetCAMDEV_43cb29ad);
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_GetIIB_C2RCH_43cb29bc);
      }
      iVar8 = FUN_43799a94(1,0x10,0x42,iVar11,uVar12,0,1,0,2,iVar9,auStack_34);
      if (iVar8 == 0) {
        if (-1 < (char)pbVar1[0x1c]) {
          return 5;
        }
        pcVar10 = s_e_ee_GetIIB_C2RCH_43cb29ce;
      }
      else {
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_GetIIB_C2RCH_43cb29ce);
        }
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_GetRCH_43cb29e0);
        }
        iVar8 = FUN_43799a94(1,4,0,iVar11,uVar12,0,1,0,2,iVar9,iVar4 + 0xc20);
        if (iVar8 != 0) {
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_GetRCH_43cb29ec);
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_CamMGetRCH_43cb29f8);
          }
          iVar8 = FUN_4381c04c(0,*(undefined4 *)(iVar4 + 0x184),auStack_58);
          if (iVar8 == 0) {
            *(undefined1 *)(iVar4 + 0x524) = 0;
            *(undefined1 *)(iVar4 + 0x20c) = 0;
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_CamMGetRCH_43cb2a08);
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_RCHParamSet_43cb2a18);
          }
          if ((pbVar1[2] & 1) == 0) {
            uVar5 = 10;
          }
          else {
            uVar5 = 7;
          }
          *(undefined4 *)(iVar4 + 0x5d4) = 1;
          *(undefined4 *)(iVar4 + 0x598) = uVar5;
          *(undefined4 *)(iVar4 + 0x59c) = 2;
          *(undefined4 *)(iVar4 + 0x5d8) = uStack_50;
          *(undefined4 *)(iVar4 + 0x5dc) = uStack_4c;
          *(undefined4 *)(iVar4 + 0x5a0) = auStack_34[0];
          *(undefined4 *)(iVar4 + 0x5c8) = 0;
          *(undefined4 *)(iVar4 + 0x5cc) = 0;
          *(undefined4 *)(iVar4 + 0x5fc) = 0;
          bVar3 = pbVar1[0x1c];
          *(uint *)(iVar4 + 0x5f8) = (uint)(*(char *)(iVar4 + 0x188) != '\0');
          if ((char)bVar3 < '\0') {
            FUN_43561540(s_e_ee_RCHParamSet_43cb2a29);
          }
          iVar8 = FUN_43799a94(1,0xe,0,iVar11,uVar12,0,1,0,2,iVar9,0);
          if (iVar8 == 0) {
            FUN_4381234c(3,9,1,&DAT_43cb0f3e);
            pcVar10 = s_SyncResMgr__Get_IDT_OPD_failure_43cb0f52;
            goto LAB_4354ea1a;
          }
          bVar3 = pbVar1[0x70];
          uVar17 = (uint)bVar3;
          if (uVar17 == 0) {
            iVar8 = FUN_43affc8a(*(undefined4 *)(iVar4 + 0x508));
            uStack_e4 = *(undefined1 *)(iVar4 + 0x20e);
            uStack_e3 = *(undefined1 *)(iVar4 + 0x20f);
            uStack_e0 = *(undefined4 *)(iVar4 + 0x208);
            uStack_d8 = (undefined1)*(undefined4 *)(iVar4 + 0x1fc);
            uStack_d7 = (undefined1)*(undefined4 *)(iVar4 + 0xc4c);
            uStack_e8 = (uint)(iVar8 == 1);
            uStack_d4 = *(undefined4 *)(iVar4 + 0x1ec);
            uStack_d0 = *(undefined4 *)(iVar4 + 0x1f0);
            uStack_cc = *(undefined4 *)(iVar4 + 500);
            uStack_c7 = (undefined1)*(undefined4 *)(iVar4 + 0x3e0);
            bStack_e2 = bVar3;
            bStack_c5 = bVar3;
            bStack_c4 = bVar3;
            bStack_c2 = bVar3;
            bStack_c1 = bVar3;
            uStack_c0 = uVar17;
            bStack_bc = bVar3;
            if ((char)pbVar1[0x1c] < '\0') {
              FUN_43561540(s_b_ee_IDT_OPD_TOP_Sync_SetFOPD_43cb2a3a);
            }
            FUN_439e34d4(&uStack_e8);
            if ((char)pbVar1[0x1c] < '\0') {
              FUN_43561540(s_e_ee_IDT_OPD_TOP_Sync_SetFOPD_43cb2a58);
            }
          }
          FUN_43799a94(1,0xf,0,iVar11,uVar12,0,1,0,2,iVar9,0);
          iVar11 = FUN_43799a94(1,0xd,*(undefined4 *)(iVar4 + 0x1fc),iVar11,uVar12,0,1,0,2,iVar9,
                                iVar4 + 0x520);
          if (iVar11 == 0) {
            return 5;
          }
          FUN_43728c4c(iVar4 + 0x514,iVar4 + 0x518);
          FUN_437956a4(*(undefined4 *)(iVar4 + 0x520));
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_EndExpose_43cb2a76);
          }
          FUN_43814008(iVar4);
          FUN_4381061c(iVar4);
          FUN_438106ec(iVar4);
          FUN_4354a678(iVar4);
          FUN_43810e7c(iVar4);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_EndExpose_43cb2a85);
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_ImagerKick_43cb2a94);
          }
          FUN_43810fa8(iVar4);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_ImagerKick_43cb2aa4);
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_CamStart_43cb2ab4);
          }
          FUN_4381127c(iVar4);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_CamStart_43cb2ac2);
          }
          if (uVar12 == 0) {
            if ((char)pbVar1[0x1c] < '\0') {
              FUN_43561540(s_b_ee_SetVDDrvCallback_43cb2ad0);
            }
            FUN_43b03a74(auStack_80,DAT_440259b4);
            FUN_4379704c(param_1,auStack_80,iVar4);
            if ((char)pbVar1[0x1c] < '\0') {
              FUN_43561540(s_e_ee_SetVDDrvCallback_43cb2ae6);
            }
          }
          piVar7 = (int *)FUN_4378f9b4();
          iVar4 = FUN_4379a8a4(*(undefined4 *)(*piVar7 + 0xc0));
          if (iVar4 == 0) {
            return 0;
          }
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_JpgRBUpdate_43cb2afc);
          }
          FUN_4379a8bc();
          if (-1 < (char)pbVar1[0x1c]) {
            return 0;
          }
          pcVar10 = s_e_ee_JpgRBUpdate_43cb2b0d;
          break;
        }
        if (-1 < (char)pbVar1[0x1c]) {
          return 5;
        }
        pcVar10 = s_e_ee_GetRCH_43cb29ec;
      }
    }
    goto LAB_4354e3b2;
  case 2:
    if (*(char *)(iVar4 + 0x20c) == '\0') {
      return 5;
    }
    if ((char)DAT_4402546c[0x1c] < '\0') {
      FUN_43561540(s_b_ee_GetRCV_43cb2b1e);
    }
    iVar8 = FUN_43799a94(1,5,0,iVar11,uVar12,0,1,0,2,iVar4 + 0xd68,iVar4 + 0xc28);
    if (iVar8 == 0) {
      if (-1 < (char)pbVar1[0x1c]) {
        return 5;
      }
      pcVar10 = s_e_ee_GetRCV_43cb2b2a;
    }
    else {
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_GetRCV_43cb2b2a);
      }
      iVar8 = FUN_4378f9b4();
      if (*(char *)(*(int *)(iVar8 + 0x20) + 1) == '\0') {
        iVar8 = FUN_4378f9b4();
        uStack_38 = (uint)*(ushort *)(*(int *)(iVar8 + 4) + 0x22) * (uVar12 + 1);
        FUN_43ad2dfc(0xfff,&uStack_38);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_AllocRendezvous_43cb2b36);
        }
        iVar8 = FUN_439035e0(iVar4 + 0x1c,*(undefined4 *)(iVar4 + 0x18c),
                             iVar11 * 0x100 + (uStack_38 >> 4),1,0,5);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_AllocRendezvous_43cb2b4b);
        }
        if (iVar8 != 0) {
          return 5;
        }
        *(undefined4 *)(iVar4 + 0x6a8) = *(undefined4 *)(iVar4 + 0x24);
        *(undefined4 *)(iVar4 + 0x6ac) = *(undefined4 *)(iVar4 + 0x28);
        iVar8 = FUN_4378f9b4();
        if (((*(byte *)(*(int *)(iVar8 + 8) + 0x26a) & 1) != 0) &&
           (iVar8 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar8 + 8) + 0x268) & 4) != 0)) {
          iVar8 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd26) = *(undefined2 *)(*(int *)(iVar8 + 0x2c) + 0x96);
          iVar8 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd28) = *(undefined2 *)(*(int *)(iVar8 + 0x2c) + 0x98);
          iVar8 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd2a) = *(undefined2 *)(*(int *)(iVar8 + 0x2c) + 0x9a);
          iVar8 = FUN_4378f9b4();
          *(undefined2 *)(iVar4 + 0xd2c) = *(undefined2 *)(*(int *)(iVar8 + 0x2c) + 0x9c);
          iVar8 = FUN_4378f9b4();
          if (*(int *)(*(int *)(iVar8 + 0x2c) + 0xa4) != 0) {
            iVar8 = FUN_4378f9b4();
            dVar16 = (double)VectorUnsignedToFloat
                                       ((uint)*(ushort *)(*(int *)(iVar8 + 0x38) + 0x38),
                                        (byte)(in_fpscr >> 0x16) & 3);
            iVar8 = FUN_4378f9b4();
            dVar18 = (double)VectorUnsignedToFloat
                                       (*(undefined4 *)(*(int *)(iVar8 + 0x2c) + 0xa0),
                                        (byte)(in_fpscr >> 0x16) & 3);
            iVar8 = FUN_4378f9b4();
            dVar19 = (double)VectorUnsignedToFloat
                                       (*(undefined4 *)(*(int *)(iVar8 + 0x2c) + 0xa4),
                                        (byte)(in_fpscr >> 0x16) & 3);
            dVar19 = (dVar16 * 100.0 * dVar18) / dVar19;
            if (((int)((uint)(dVar19 < 126500.0) << 0x1f) < 0) &&
               (uVar17 = VectorFloatToUnsigned(dVar19,3), uVar17 != 0)) {
              if (uVar17 < 0x31ce) {
                cVar2 = FUN_4355faf0(uVar17 + 0x32,100);
                bVar3 = cVar2 << 1;
              }
              else {
                cVar2 = FUN_4355faf0(uVar17 + 500,1000);
                bVar3 = cVar2 << 1 | 1;
              }
              *(byte *)(iVar4 + 0xd2e) = bVar3;
              goto LAB_4354e22e;
            }
          }
          *(undefined1 *)(iVar4 + 0xd2e) = 0xff;
        }
LAB_4354e22e:
        FUN_43b03a5e(&uStack_234);
        uStack_234 = *(undefined4 *)(iVar4 + 0x1ec);
        uStack_230 = *(undefined4 *)(iVar4 + 0x1f0);
        uStack_22c = *(undefined4 *)(iVar4 + 500);
        uStack_228 = 0;
        iStack_224 = iVar4 + 0x1c;
        uStack_220 = FUN_43ae8c4a(iVar11 + 1);
        uStack_21c = *(undefined4 *)(iVar4 + 0xc54);
        uStack_218 = 0;
        uStack_217 = 0;
        uStack_214 = *(undefined2 *)(iVar4 + 0x1ba);
        uStack_216 = *(undefined2 *)(iVar4 + 0x1b8);
        if (*(char *)(iVar4 + 400) == '\0') {
          uStack_212 = FUN_43b03ae6(*(undefined2 *)(iVar4 + 0x19e));
        }
        else {
          uStack_212 = FUN_43ae98f8();
        }
        uStack_20a = *(undefined2 *)(iVar4 + 0x19e);
        uStack_210 = *(undefined2 *)(iVar4 + 0x1a0);
        uStack_1fc = *(undefined4 *)(iVar4 + 0x1b4);
        uStack_20e = 0;
        uStack_20c = 0;
        uStack_1f7 = 1;
        uStack_1f4 = 1;
        uStack_1f0 = *(undefined4 *)(iVar4 + 0x4fc);
        uStack_206 = 0;
        uStack_204 = 0;
        uStack_1ec = *(undefined4 *)(iVar4 + 0x500);
        uStack_1f8 = 0;
        uStack_1f6 = 0;
        uStack_1e8 = *(undefined4 *)(iVar4 + 0x504);
        uStack_1e4 = *(int *)(iVar4 + 0xbd4) == 1;
        uStack_1d8 = *(undefined4 *)(iVar4 + 0xd54);
        uStack_1e0 = 0xffffffff;
        uStack_1d4 = *(undefined4 *)(iVar4 + 0xd58);
        uStack_1dc = 0xffffffff;
        uStack_1d0 = 0;
        uStack_18c = 0;
        uStack_16c = 0;
        uStack_150 = 0;
        uStack_14c = *(undefined2 *)(iVar4 + 0xd26);
        uStack_140 = 0xffffffff;
        uStack_134 = 0;
        uStack_14a = *(undefined2 *)(iVar4 + 0xd28);
        uStack_133 = 0;
        uStack_148 = *(undefined2 *)(iVar4 + 0xd2a);
        uStack_146 = *(undefined2 *)(iVar4 + 0xd2c);
        uStack_144 = *(undefined1 *)(iVar4 + 0xd2e);
        uStack_13c = *(undefined4 *)(iVar4 + 0x1b0);
        uStack_138 = *(undefined4 *)(iVar4 + 0xd84);
        uStack_208 = uStack_210;
        uStack_202 = uStack_20a;
        uStack_200 = uStack_210;
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_Write_Seq_43cb2b60);
        }
        FUN_4379b44c(0,&uStack_234);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_Write_Seq_43cb2b6f);
        }
LAB_4354e3da:
        if ((pbVar1[2] & 1) == 0) {
          *(undefined4 *)(iVar4 + 0x668) = 10;
        }
        else {
          *(undefined4 *)(iVar4 + 0x598) = 7;
        }
        *(undefined4 *)(iVar4 + 0x66c) = 0;
        *(undefined4 *)(iVar4 + 0x69c) = 0;
        *(undefined4 *)(iVar4 + 0x678) = *(undefined4 *)(iVar4 + 0x5d8);
        *(undefined4 *)(iVar4 + 0x6cc) = 0;
        *(undefined4 *)(iVar4 + 0x764) = 0;
        *(undefined4 *)(iVar4 + 0x67c) = *(undefined4 *)(iVar4 + 0x5dc);
        *(undefined4 *)(iVar4 + 0x674) = 1;
        *(uint *)(iVar4 + 0x698) = (uint)(*(char *)(iVar4 + 0x188) != '\0');
        *(undefined4 *)(iVar4 + 0x6a4) = 1;
        *(uint *)(iVar4 + 0x6c8) = (uint)(*(char *)(iVar4 + 400) != '\0');
        *(undefined4 *)(iVar4 + 0x738) = 1;
        if (*(char *)(iVar4 + 0xc18) == '\0') {
          if (*(char *)(iVar4 + 0xc19) == '\0') {
            uVar5 = 0;
          }
          else {
            uVar5 = 2;
          }
        }
        else {
          uVar5 = 2;
        }
        if ((pbVar1[0x23] & 1) == 0) {
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_EIS_RC1V_SetPower_43cb2b9e);
          }
          FUN_43704d90(*(undefined4 *)(iVar4 + 0xc28),uVar5);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_EIS_RC1V_SetPower_43cb2bb5);
          }
        }
        uStack_94 = 0x80;
        uStack_8c = 0;
        uStack_9c = 4;
        uStack_98 = 7;
        uStack_88 = 1;
        uVar5 = FUN_43b03bf8(*(undefined2 *)(iVar4 + 0x19e),*(undefined2 *)(iVar4 + 0x19c),
                             *(undefined1 *)(iVar4 + 0x188));
        uStack_90 = FUN_43556490(uVar5,uStack_94,1,0);
        uStack_b0 = 0x80;
        uStack_a8 = 0;
        uStack_84 = 1;
        uStack_b8 = 4;
        uStack_b4 = 7;
        uStack_a4 = 1;
        uVar5 = FUN_43b03bf8(*(undefined2 *)(iVar4 + 0x19e),*(undefined2 *)(iVar4 + 0x1a0),
                             *(undefined1 *)(iVar4 + 400));
        uStack_ac = FUN_43556490(uVar5,uStack_b0,1,0);
        uStack_a0 = 1;
        iVar8 = FUN_43940f2c(*(undefined4 *)(iVar4 + 0xc28),&uStack_9c,&uStack_b8);
        if (iVar8 != 0) {
          FUN_4381234c(3,9,1,&DAT_43cb2bcc,iVar8);
          FUN_43902718(s_Sequence_HS__RC_ERR_0x_02x_rcct__43cb2be0,iVar8);
        }
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_RCVDataSet_43cb2c17);
        }
        FUN_43798ccc(*(undefined4 *)(iVar4 + 0xc28),iVar4 + 0x668,iVar4 + 0x73c,iVar4 + 0xbd8,
                     iVar4 + 0xbdc,iVar4 + 0x19a,iVar4 + 0x19e,*(undefined4 *)(iVar4 + 0xbd4),
                     *(undefined4 *)(iVar4 + 0x738),0,*(undefined1 *)(iVar4 + 0x525),0,0);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_RCVDataSet_43cb2c27);
        }
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_b_ee_SyncStblzRCV_43cb2c37);
        }
        FUN_438113c4(iVar4);
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_SyncStblzRCV_43cb2c49);
        }
        iVar8 = FUN_43ae9674(iVar4 + 0x1c);
        if (iVar8 != 0) {
          iVar8 = FUN_4378f9b4();
          uVar12 = uVar12 + 4;
          iVar8 = FUN_4355faf0(*(int *)(*(int *)(iVar8 + 4) + 0x1c) + 0x3e7ff,0x3e800);
          iVar9 = FUN_4378f9b4();
          if (**(byte **)(iVar9 + 0x20) <= uVar12) {
            iVar9 = FUN_4378f9b4();
            iVar11 = iVar11 + 1;
            uVar12 = uVar12 - **(byte **)(iVar9 + 0x20);
          }
          iVar9 = FUN_4378f9b4();
          uStack_38 = *(ushort *)(*(int *)(iVar9 + 4) + 0x22) * uVar12;
          FUN_43ad2dfc(0xfff,&uStack_38);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_b_ee_FreeRendezvous_43cb2c5b);
          }
          iVar11 = FUN_43ae8c4a(iVar11);
          iVar4 = FUN_43b2a2d0(iVar4 + 0x1c,iVar11 * 0x100 + (uStack_38 >> 4),iVar8 << 2,1,5);
          if ((char)pbVar1[0x1c] < '\0') {
            FUN_43561540(s_e_ee_FreeRendezvous_43cb2c6f);
          }
          if (iVar4 != 0) {
            return 5;
          }
          return 0;
        }
        return 0;
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_CamMGetRCV_43cb2b7e);
      }
      iVar8 = FUN_4381c04c(2,*(undefined4 *)(iVar4 + 0x18c),auStack_58);
      if (iVar8 != 0) {
        if ((char)pbVar1[0x1c] < '\0') {
          FUN_43561540(s_e_ee_CamMGetRCV_43cb2b8e);
        }
        FUN_4381c228(2);
        *(undefined4 *)(iVar4 + 0x6a8) = uStack_50;
        *(undefined4 *)(iVar4 + 0x6ac) = uStack_4c;
        goto LAB_4354e3da;
      }
      if (-1 < (char)pbVar1[0x1c]) {
        return 5;
      }
      pcVar10 = s_e_ee_CamMGetRCV_43cb2b8e;
    }
LAB_4354e3b2:
    FUN_43561540(pcVar10);
switchD_4354d782_caseD_5:
    return 5;
  case 3:
    iVar8 = FUN_4379a898();
    iVar8 = *(int *)(iVar8 + 100);
    if (iVar8 < 0x7ce) {
      iVar8 = iVar8 + 2;
    }
    else {
      iVar8 = iVar8 + -0x7ce;
    }
    iVar9 = FUN_4379a898();
    iVar8 = iVar8 * 0x2c;
    *(undefined2 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x14) = *(undefined2 *)(iVar4 + 0xc76);
    iVar9 = FUN_4379a898();
    *(undefined2 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x16) = *(undefined2 *)(iVar4 + 0xc74);
    iVar9 = FUN_4379a898();
    *(undefined2 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x18) = *(undefined2 *)(iVar4 + 0xc78);
    iVar9 = FUN_4379a898();
    *(undefined4 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x1c) = *(undefined4 *)(iVar4 + 0xc30);
    iVar9 = FUN_4379a898();
    *(undefined4 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x20) = *(undefined4 *)(iVar4 + 0xc34);
    iVar9 = FUN_4379a898();
    *(undefined4 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x24) = *(undefined4 *)(iVar4 + 0xd54);
    iVar9 = FUN_4379a898();
    *(undefined4 *)(*(int *)(iVar9 + 0x60) + iVar8 + 0x28) = *(undefined4 *)(iVar4 + 0xd58);
    uVar5 = FUN_4379ada0();
    pbVar1 = DAT_4402546c;
    switch(uVar5) {
    case 0:
    case 2:
      goto switchD_4354d782_caseD_5;
    case 1:
      puVar6 = (undefined4 *)FUN_4378f9b4();
      if ((*(short *)*puVar6 == 0x127) &&
         (iVar11 = FUN_4379a320(), *(char *)(iVar11 + 0xac1) == '\0')) {
        return 0;
      }
      iVar11 = FUN_4378f9b4();
      FUN_4379aa3c(*(undefined4 *)(*(int *)(iVar11 + 4) + 0x14));
      pbVar1 = DAT_4402546c;
      if ((char)DAT_4402546c[0x1c] < '\0') {
        FUN_43561540(s_b_ee_EncFirst_43cb2c83);
      }
      uVar5 = FUN_4379a898();
      uVar13 = *(undefined4 *)(iVar4 + 0x6a8);
      uVar14 = *(undefined4 *)(iVar4 + 0x6ac);
      iVar11 = FUN_4379a898();
      FUN_4379b180(uVar5,iVar4 + 0x19e,uVar13,uVar14,*(undefined2 *)(iVar11 + 0x88));
      if (-1 < (char)pbVar1[0x1c]) {
        return 0;
      }
      pcVar10 = s_e_ee_EncFirst_43cb2c91;
      break;
    case 3:
      if ((char)DAT_4402546c[0x1c] < '\0') {
        FUN_43561540(s_b_ee_EncNext1st_43cb2c9f);
      }
      uVar14 = *(undefined4 *)(iVar4 + 0x6a8);
      uVar5 = *(undefined4 *)(iVar4 + 0x6ac);
      iVar11 = FUN_4379a898();
      FUN_4379b058(iVar4 + 0x19e,uVar14,uVar5,*(undefined2 *)(iVar11 + 0x88));
      if (-1 < (char)pbVar1[0x1c]) {
        return 0;
      }
      pcVar10 = s_e_ee_EncNext1st_43cb2caf;
      break;
    case 4:
      puVar6 = (undefined4 *)FUN_4378f9b4();
      if (((*(short *)*puVar6 != 0x120) &&
          (puVar6 = (undefined4 *)FUN_4378f9b4(), *(short *)*puVar6 != 0x127)) &&
         (puVar6 = (undefined4 *)FUN_4378f9b4(), *(short *)*puVar6 != 0x129)) {
        iVar4 = FUN_4379a898();
        if (1 < *(ushort *)(iVar4 + 0x86)) {
          return 0;
        }
        iVar4 = FUN_4379a898();
        *(short *)(iVar4 + 0x86) = *(short *)(iVar4 + 0x86) + 1;
        FUN_4379ae68(auStack_40);
        FUN_4379a998(auStack_40,1);
        return 0;
      }
      if (uVar12 == 3) {
        iVar8 = FUN_4379a898();
        iVar9 = *(int *)(iVar8 + 0x60);
        iVar8 = FUN_4379a898();
        *(int *)(*(int *)(iVar8 + 100) * 0x2c + iVar9 + 0xc) = iVar11;
        iVar11 = FUN_4379a898();
        iVar8 = *(int *)(iVar11 + 0x60);
        iVar11 = FUN_4379a898();
        *(undefined2 *)(*(int *)(iVar11 + 100) * 0x2c + iVar8 + 0x10) = 0;
      }
      else {
        iVar8 = FUN_4379a898();
        iVar9 = *(int *)(iVar8 + 0x60);
        iVar8 = FUN_4379a898();
        uVar5 = FUN_43ae8c4a(iVar11 + -1);
        *(undefined4 *)(*(int *)(iVar8 + 100) * 0x2c + iVar9 + 0xc) = uVar5;
        iVar11 = FUN_4379a898();
        iVar8 = *(int *)(iVar11 + 0x60);
        iVar11 = FUN_4379a898();
        *(ushort *)(*(int *)(iVar11 + 100) * 0x2c + iVar8 + 0x10) = bVar3 + 1;
      }
      pbVar1 = DAT_4402546c;
      if ((char)DAT_4402546c[0x1c] < '\0') {
        FUN_43561540(s_b_ee_EncGetParam_43cb2cbf);
      }
      FUN_4379ae68(auStack_48);
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_EncGetParam_43cb2cd0);
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_AddEncParam_43cb2ce1);
      }
      iVar11 = FUN_4378f9b4();
      uVar5 = *(undefined4 *)(*(int *)(iVar11 + 4) + 0x14);
      iVar11 = FUN_4378f9b4();
      FUN_4379aaf4(auStack_48,uVar5,*(undefined1 *)(*(int *)(iVar11 + 0x20) + 1));
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_e_ee_AddEncParam_43cb2cf2);
      }
      if ((char)pbVar1[0x1c] < '\0') {
        FUN_43561540(s_b_ee_EncNext_43cb2d03);
      }
      uVar14 = *(undefined4 *)(iVar4 + 0x6a8);
      uVar5 = *(undefined4 *)(iVar4 + 0x6ac);
      iVar11 = FUN_4379a898();
      FUN_4379b058(iVar4 + 0x19e,uVar14,uVar5,*(undefined2 *)(iVar11 + 0x88));
      if (-1 < (char)pbVar1[0x1c]) {
        return 0;
      }
      pcVar10 = s_e_ee_EncNext_43cb2d10;
      break;
    default:
      FUN_4381234c(5,0,1,&DAT_43c9b47c,s_Sequence_HSRecGolfshot_cpp_43cb2245,0x3b7);
      FUN_43902718(s_FATAL___s__d_43c9b487,s_Sequence_HSRecGolfshot_cpp_43cb2245,0x3b7);
      return 0;
    }
    break;
  case 4:
    goto switchD_4354d782_caseD_4;
  case 5:
    goto switchD_4354d782_caseD_5;
  default:
    FUN_4381234c(3,9,1,&DAT_43cb0f14);
    pcVar10 = s_Sequence_Stage_Error__43cb0f28;
LAB_4354ea1a:
    FUN_43902718(pcVar10);
    goto switchD_4354d782_caseD_5;
  }
  FUN_43561540(pcVar10);
switchD_4354d782_caseD_4:
  return 0;
}


/* query "435498ca" */

undefined4 s32_candidate_435498ca(void)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  undefined4 uVar4;
  int unaff_r4;
  int unaff_r5;
  int unaff_r6;
  int iVar5;
  uint in_fpscr;
  double dVar6;
  uint uVar7;
  double dVar8;
  double dVar9;
  int in_stack_00000024;
  undefined4 in_stack_00000034;
  undefined4 in_stack_00000038;
  undefined4 in_stack_0000003c;
  undefined4 in_stack_00000040;
  
  FUN_43797090();
  if (in_stack_00000024 == 0) {
    FUN_43b03a74(&stack0x0000023c,*(undefined4 *)(unaff_r5 + 0x2f28));
    FUN_43796910();
  }
  else {
    FUN_43b03a74(&stack0x00000250,*(undefined4 *)(unaff_r5 + 0x2f28));
    FUN_43797090();
  }
  FUN_43b03a74(&stack0x00000228,*(undefined4 *)(unaff_r5 + 0x5b40));
  FUN_43796910();
  FUN_43b03a74(&stack0x00000214,*(undefined4 *)(unaff_r5 + 0x6ad0));
  FUN_4379704c();
  iVar3 = FUN_4378f9b4();
  if (((*(byte *)(*(int *)(iVar3 + 8) + 0x26a) & 1) != 0) &&
     (iVar3 = FUN_4378f9b4(), (*(byte *)(*(int *)(iVar3 + 8) + 0x268) & 4) != 0)) {
    iVar3 = FUN_4378f9b4();
    *(undefined2 *)(unaff_r4 + 0xd26) = *(undefined2 *)(*(int *)(iVar3 + 0x2c) + 0x96);
    iVar3 = FUN_4378f9b4();
    *(undefined2 *)(unaff_r4 + 0xd28) = *(undefined2 *)(*(int *)(iVar3 + 0x2c) + 0x98);
    iVar3 = FUN_4378f9b4();
    *(undefined2 *)(unaff_r4 + 0xd2a) = *(undefined2 *)(*(int *)(iVar3 + 0x2c) + 0x9a);
    iVar3 = FUN_4378f9b4();
    *(undefined2 *)(unaff_r4 + 0xd2c) = *(undefined2 *)(*(int *)(iVar3 + 0x2c) + 0x9c);
    iVar3 = FUN_4378f9b4();
    if (*(int *)(*(int *)(iVar3 + 0x2c) + 0xa4) != 0) {
      iVar3 = FUN_4378f9b4();
      dVar6 = (double)VectorUnsignedToFloat
                                ((uint)*(ushort *)(*(int *)(iVar3 + 0x38) + 0x38),
                                 (byte)(in_fpscr >> 0x16) & 3);
      iVar3 = FUN_4378f9b4();
      dVar8 = (double)VectorUnsignedToFloat
                                (*(undefined4 *)(*(int *)(iVar3 + 0x2c) + 0xa0),
                                 (byte)(in_fpscr >> 0x16) & 3);
      iVar3 = FUN_4378f9b4();
      dVar9 = (double)VectorUnsignedToFloat
                                (*(undefined4 *)(*(int *)(iVar3 + 0x2c) + 0xa4),
                                 (byte)(in_fpscr >> 0x16) & 3);
      dVar9 = (dVar6 * 100.0 * dVar8) / dVar9;
      if (((int)((uint)(dVar9 < 126500.0) << 0x1f) < 0) &&
         (uVar7 = VectorFloatToUnsigned(dVar9,3), uVar7 != 0)) {
        if (uVar7 < 0x31ce) {
          cVar1 = FUN_4355faf0(uVar7 + 0x32,100);
          bVar2 = cVar1 << 1;
        }
        else {
          cVar1 = FUN_4355faf0(uVar7 + 500,1000);
          bVar2 = cVar1 << 1 | 1;
        }
        *(byte *)(unaff_r4 + 0xd2e) = bVar2;
        goto LAB_43549a18;
      }
    }
    *(undefined1 *)(unaff_r4 + 0xd2e) = 0xff;
  }
LAB_43549a18:
  FUN_43b03a5e(&stack0x00000034);
  if ((*(char *)(unaff_r4 + 0x20c) != '\0') && (iVar3 = FUN_437286bc(), iVar3 != 0)) {
    in_stack_00000034 = *(undefined4 *)(unaff_r4 + 0x1ec);
    in_stack_00000038 = *(undefined4 *)(unaff_r4 + 0x1f0);
    in_stack_0000003c = *(undefined4 *)(unaff_r4 + 500);
    in_stack_00000040 = 0;
    if (*(char *)(unaff_r4 + 400) == '\0') {
      FUN_43ae9e86(*(undefined2 *)(unaff_r4 + 0x19e),0x40);
    }
    else {
      FUN_43ae98f8();
    }
    FUN_4379b44c(0,&stack0x00000034);
  }
  iVar3 = FUN_4378f9b4();
  if ((*(byte *)(*(int *)(iVar3 + 8) + 0x267) & 0x80) != 0) {
    FUN_437fe4d4();
  }
  iVar3 = *(int *)(unaff_r4 + 0xc4c);
  FUN_4378f9b4();
  iVar5 = unaff_r6 + iVar3 + 1;
  FUN_43ad2dfc(0xfff,&stack0x000002b0);
  iVar3 = FUN_4378f9b4();
  FUN_4355faf0(*(int *)(*(int *)(iVar3 + 4) + 0x18) + 0x3e7ff,0x3e800);
  if (*(char *)(unaff_r4 + 0x20d) == '\0') {
    FUN_43ae8c4a(iVar5);
  }
  else {
    FUN_43ae8c4a(iVar5 + *(int *)(unaff_r4 + 0xc60));
  }
  iVar3 = FUN_43b2a2d0();
  if (iVar3 == 0) {
    uVar4 = 0;
  }
  else {
    uVar4 = 5;
  }
  return uVar4;
}


/* query "43549d42" */

undefined4 s32_candidate_43549d42(void)

{
  undefined4 uVar1;
  int iVar2;
  int unaff_r4;
  int unaff_r5;
  undefined4 in_stack_0000014c;
  undefined4 in_stack_00000178;
  undefined1 in_stack_0000017c;
  
  FUN_4379704c();
  FUN_43afb42e(&stack0x00000138);
  FUN_43afb476(&stack0x00000138,*(undefined4 *)(unaff_r5 + 0x30e4));
  in_stack_0000014c = 4;
  in_stack_0000017c = 0;
  in_stack_00000178 = FUN_43afbf44();
  FUN_43b03a80(&stack0x000001d8,*(undefined4 *)(unaff_r5 + 0x3c10));
  uVar1 = FUN_43b03a70();
  FUN_4380d708(&stack0x000001d8,uVar1);
  iVar2 = FUN_4381bbf0();
  if (iVar2 != 0) {
    FUN_43b04730();
  }
  FUN_43ae7542(unaff_r4 + 0x1c);
  FUN_43ae7542();
  FUN_43ae7534(&stack0x000001b0);
  return 5;
}


/* query "43797344" */

undefined4 FUN_43797344(void)

{
  return *DAT_440212ac;
}


/* query "43797370" */

void FUN_43797370(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  piVar1 = DAT_440212ac;
  iVar2 = *DAT_440212ac;
  iVar3 = iVar2 + 1;
  *DAT_440212ac = iVar3;
  if (iVar3 == 0) {
    *piVar1 = iVar2;
  }
  return;
}


/* query "43797390" */

bool FUN_43797390(void)

{
  char cVar1;
  
  cVar1 = *DAT_4402490c;
  if (cVar1 != '\0') {
    *DAT_4402490c = '\0';
  }
  return cVar1 != '\0';
}


/* query "437973c4" */

bool FUN_437973c4(void)

{
  char cVar1;
  
  cVar1 = *DAT_44020ecc;
  if (cVar1 != '\0') {
    *DAT_44020ecc = '\0';
  }
  return cVar1 != '\0';
}


/* query "437973f8" */

void FUN_437973f8(int param_1)

{
  *DAT_44021bc0 = param_1 + 1;
  return;
}


/* query "43796438" */

void FUN_43796438(uint param_1,undefined4 param_2,undefined4 param_3)

{
  if (5 < param_1) {
    FUN_437961d8(5,0,1,&DAT_43c9b47c,s_ImagingMain_cpp_43ca3e60,0x8c,param_3);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_ImagingMain_cpp_43ca3e60,0x8c);
    return;
  }
  DAT_43e9de28 = param_1;
  return;
}


/* query "43b66058" */

void FUN_43b66058(int param_1,undefined4 param_2)

{
  thunk_FUN_439c5320(param_1 + 0x14,param_2,0xe0);
  return;
}


/* query "43a4941e" */

void FUN_43a4941e(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = param_2[1];
  uVar2 = param_2[2];
  uVar3 = param_2[3];
  *(undefined4 *)(param_1 + 0x14) = *param_2;
  *(undefined4 *)(param_1 + 0x18) = uVar1;
  *(undefined4 *)(param_1 + 0x1c) = uVar2;
  *(undefined4 *)(param_1 + 0x20) = uVar3;
  uVar1 = param_2[5];
  uVar2 = param_2[6];
  uVar3 = param_2[7];
  *(undefined4 *)(param_1 + 0x24) = param_2[4];
  *(undefined4 *)(param_1 + 0x28) = uVar1;
  *(undefined4 *)(param_1 + 0x2c) = uVar2;
  *(undefined4 *)(param_1 + 0x30) = uVar3;
  uVar1 = param_2[9];
  uVar2 = param_2[10];
  uVar3 = param_2[0xb];
  *(undefined4 *)(param_1 + 0x34) = param_2[8];
  *(undefined4 *)(param_1 + 0x38) = uVar1;
  *(undefined4 *)(param_1 + 0x3c) = uVar2;
  *(undefined4 *)(param_1 + 0x40) = uVar3;
  uVar1 = param_2[0xd];
  *(undefined4 *)(param_1 + 0x44) = param_2[0xc];
  *(undefined4 *)(param_1 + 0x48) = uVar1;
  return;
}


/* query "43a493cc" */

void FUN_43a493cc(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = param_2[1];
  uVar2 = param_2[2];
  uVar3 = param_2[3];
  *(undefined4 *)(param_1 + 0x14) = *param_2;
  *(undefined4 *)(param_1 + 0x18) = uVar1;
  *(undefined4 *)(param_1 + 0x1c) = uVar2;
  *(undefined4 *)(param_1 + 0x20) = uVar3;
  *(undefined4 *)(param_1 + 0x24) = param_2[4];
  return;
}


/* query "435a9b30" */

int FUN_435a9b30(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined1 auStack_198 [272];
  undefined1 auStack_88 [8];
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  int iStack_60;
  undefined1 auStack_5c [8];
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [8];
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  int iStack_1c;
  
  if (param_3 == 0) {
    FUN_435aa628(0x204e4950,0x55,0xffffffe0);
    return -0x20;
  }
  iVar5 = *(int *)(param_1 + 0x28);
  if (iVar5 == 0) {
    if (((*(int *)(param_2 + 0x18) == *(int *)(param_1 + 8)) &&
        (*(int *)(param_2 + 0x1c) == *(int *)(param_1 + 0xc))) &&
       (*(int *)(param_2 + 0x20) == *(int *)(param_1 + 0x10))) {
      FUN_435a92e0(auStack_198);
      FUN_43a3b8f0(auStack_88);
      uStack_80 = *(undefined4 *)(param_1 + 0x18);
      uStack_7c = *(undefined4 *)(param_1 + 0x1c);
      uStack_78 = *(undefined4 *)(param_1 + 0x20);
      uStack_74 = *(undefined4 *)(param_1 + 0x24);
      uStack_70 = *(undefined4 *)(param_2 + 0x18);
      uStack_6c = *(undefined4 *)(param_2 + 0x1c);
      uStack_68 = *(undefined4 *)(param_2 + 0x20);
      uStack_64 = *(undefined4 *)(param_2 + 0x24);
      iStack_60 = iVar5;
      FUN_435a9460(auStack_198,auStack_88,0x2c);
      FUN_43a49628(auStack_198,*(undefined4 *)(param_1 + 0x14));
      FUN_435aa20c(*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_1 + 0x24),auStack_198);
      uVar1 = *(undefined4 *)(param_2 + 0x18);
      uVar2 = *(undefined4 *)(param_2 + 0x1c);
      uVar3 = *(undefined4 *)(param_2 + 0x20);
      uVar4 = *(undefined4 *)(param_2 + 0x24);
      *(undefined4 *)(param_1 + 0x28) = 2;
      *(undefined4 *)(param_1 + 0x34) = 1;
      *(int *)(param_1 + 0x2c) = param_3;
      *(undefined4 *)(param_1 + 8) = uVar1;
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      *(undefined4 *)(param_1 + 0x10) = uVar3;
      *(undefined4 *)(param_1 + 0x14) = uVar4;
      FUN_43a49eec(1,param_3,param_1 + 0x18,(undefined4 *)(param_2 + 0x18),0,2);
      FUN_435a92c8(auStack_198);
      return 0;
    }
    iVar5 = -0x19;
  }
  else if (iVar5 == 2) {
    iVar5 = -0x18;
  }
  else {
    puVar6 = (undefined4 *)(param_2 + 0x18);
    iVar5 = FUN_435a9ad0(param_1,puVar6);
    if (iVar5 == 0) {
      FUN_435a92e0(auStack_198);
      FUN_43a3b8c6(auStack_5c);
      uStack_54 = *(undefined4 *)(param_1 + 0x18);
      uStack_50 = *(undefined4 *)(param_1 + 0x1c);
      uStack_4c = *(undefined4 *)(param_1 + 0x20);
      uStack_48 = *(undefined4 *)(param_1 + 0x24);
      uStack_44 = *puVar6;
      uStack_40 = *(undefined4 *)(param_2 + 0x1c);
      uStack_3c = *(undefined4 *)(param_2 + 0x20);
      uStack_38 = *(undefined4 *)(param_2 + 0x24);
      FUN_435a9460(auStack_198,auStack_5c,0x28);
      FUN_43a49628(auStack_198,*(undefined4 *)(param_1 + 0x24));
      FUN_435aa20c(*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_2 + 0x24),auStack_198);
      *(undefined4 *)(param_1 + 0x28) = 2;
      *(undefined4 *)(param_1 + 0x34) = 1;
      uVar1 = *puVar6;
      uVar2 = *(undefined4 *)(param_2 + 0x1c);
      uVar3 = *(undefined4 *)(param_2 + 0x20);
      uVar4 = *(undefined4 *)(param_2 + 0x24);
      *(int *)(param_1 + 0x2c) = param_3;
      *(undefined4 *)(param_1 + 8) = uVar1;
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      *(undefined4 *)(param_1 + 0x10) = uVar3;
      *(undefined4 *)(param_1 + 0x14) = uVar4;
      goto LAB_435a9c9c;
    }
  }
  FUN_435a92e0(auStack_198);
  FUN_43a3b9be(auStack_34);
  uStack_2c = *(undefined4 *)(param_1 + 0x18);
  uStack_28 = *(undefined4 *)(param_1 + 0x1c);
  uStack_24 = *(undefined4 *)(param_1 + 0x20);
  uStack_20 = *(undefined4 *)(param_1 + 0x24);
  iStack_1c = iVar5;
  FUN_435a9460(auStack_198,auStack_34,0x1c);
  FUN_43a49628(auStack_198,*(undefined4 *)(param_1 + 0x24));
  FUN_435aa20c(*(undefined4 *)(param_1 + 4),param_3,auStack_198);
LAB_435a9c9c:
  FUN_435a92c8(auStack_198);
  FUN_43a49eec(1,param_3,param_1 + 0x18,param_2 + 0x18,iVar5,*(undefined4 *)(param_1 + 0x28));
  return iVar5;
}

