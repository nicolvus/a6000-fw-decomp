/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43b122fe" */

void FUN_43b122fe(undefined4 *param_1)

{
  undefined2 uVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  int iVar9;
  undefined4 uVar10;
  
  uVar3 = FUN_4387a4dc();
  puVar4 = (undefined1 *)FUN_4387b7dc();
  puVar5 = (undefined1 *)FUN_4387b7e8();
  puVar6 = (undefined1 *)FUN_4387b7f4();
  puVar7 = (undefined4 *)FUN_4387b7c4();
  puVar8 = (undefined4 *)FUN_4387b83c();
  iVar9 = FUN_4387b848();
  *param_1 = puVar7[0x18];
  *(char *)(param_1 + 0x18) = (char)puVar7[0xb];
  *(char *)((int)param_1 + 0x61) = (char)puVar7[0x12];
  *(char *)((int)param_1 + 0x62) = (char)puVar7[0x13];
  uVar1 = *(undefined2 *)(iVar9 + 0x24);
  *(char *)((int)param_1 + 0x66) = (char)*puVar7;
  uVar10 = *puVar8;
  *(undefined2 *)(param_1 + 0x19) = uVar1;
  *(char *)((int)param_1 + 0x67) = (char)uVar10;
  FUN_43b126cc(uVar3,param_1 + 1);
  *(undefined1 *)(param_1 + 7) = puVar4[1];
  *(undefined1 *)((int)param_1 + 0x1d) = *puVar4;
  *(undefined1 *)((int)param_1 + 0x1e) = puVar4[3];
  *(undefined1 *)((int)param_1 + 0x1f) = puVar4[2];
  *(undefined1 *)(param_1 + 8) = puVar4[5];
  *(undefined1 *)((int)param_1 + 0x21) = puVar4[4];
  *(undefined1 *)((int)param_1 + 0x22) = puVar4[7];
  *(undefined1 *)((int)param_1 + 0x23) = puVar4[6];
  *(undefined1 *)(param_1 + 9) = puVar4[9];
  *(undefined1 *)((int)param_1 + 0x25) = puVar4[8];
  *(undefined1 *)((int)param_1 + 0x26) = puVar4[0xb];
  *(undefined1 *)((int)param_1 + 0x27) = puVar4[10];
  *(undefined1 *)(param_1 + 10) = puVar4[0xd];
  *(undefined1 *)((int)param_1 + 0x29) = puVar4[0xc];
  *(undefined1 *)((int)param_1 + 0x2a) = puVar4[0xf];
  *(undefined1 *)((int)param_1 + 0x2b) = puVar4[0xe];
  *(undefined1 *)(param_1 + 0xb) = puVar4[0x11];
  *(undefined1 *)((int)param_1 + 0x2d) = puVar4[0x10];
  *(undefined1 *)((int)param_1 + 0x2e) = puVar4[0x13];
  *(undefined1 *)((int)param_1 + 0x2f) = puVar4[0x12];
  *(undefined1 *)(param_1 + 0x11) = puVar5[1];
  *(undefined1 *)((int)param_1 + 0x45) = *puVar5;
  *(undefined1 *)((int)param_1 + 0x46) = puVar5[3];
  *(undefined1 *)((int)param_1 + 0x47) = puVar5[2];
  *(undefined1 *)(param_1 + 0x12) = puVar5[5];
  *(undefined1 *)((int)param_1 + 0x49) = puVar5[4];
  *(undefined1 *)((int)param_1 + 0x4a) = puVar5[7];
  *(undefined1 *)((int)param_1 + 0x4b) = puVar5[6];
  *(undefined1 *)(param_1 + 0x13) = puVar5[9];
  *(undefined1 *)((int)param_1 + 0x4d) = puVar5[8];
  *(undefined1 *)((int)param_1 + 0x4e) = puVar5[0xb];
  *(undefined1 *)((int)param_1 + 0x4f) = puVar5[10];
  *(undefined1 *)(param_1 + 0x14) = puVar5[0xd];
  *(undefined1 *)((int)param_1 + 0x51) = puVar5[0xc];
  *(undefined1 *)((int)param_1 + 0x52) = puVar5[0xf];
  *(undefined1 *)((int)param_1 + 0x53) = puVar5[0xe];
  *(undefined1 *)(param_1 + 0x15) = puVar5[0x11];
  *(undefined1 *)((int)param_1 + 0x55) = puVar5[0x10];
  *(undefined1 *)((int)param_1 + 0x56) = puVar5[0x13];
  *(undefined1 *)((int)param_1 + 0x57) = puVar5[0x12];
  *(undefined1 *)(param_1 + 0xc) = puVar6[1];
  *(undefined1 *)((int)param_1 + 0x31) = *puVar6;
  *(undefined1 *)((int)param_1 + 0x32) = puVar6[3];
  *(undefined1 *)((int)param_1 + 0x33) = puVar6[2];
  *(undefined1 *)(param_1 + 0xd) = puVar6[5];
  *(undefined1 *)((int)param_1 + 0x35) = puVar6[4];
  *(undefined1 *)((int)param_1 + 0x36) = puVar6[7];
  *(undefined1 *)((int)param_1 + 0x37) = puVar6[6];
  *(undefined1 *)(param_1 + 0xe) = puVar6[9];
  *(undefined1 *)((int)param_1 + 0x39) = puVar6[8];
  *(undefined1 *)((int)param_1 + 0x3a) = puVar6[0xb];
  *(undefined1 *)((int)param_1 + 0x3b) = puVar6[10];
  *(undefined1 *)(param_1 + 0xf) = puVar6[0xd];
  *(undefined1 *)((int)param_1 + 0x3d) = puVar6[0xc];
  *(undefined1 *)((int)param_1 + 0x3e) = puVar6[0xf];
  *(undefined1 *)((int)param_1 + 0x3f) = puVar6[0xe];
  *(undefined1 *)(param_1 + 0x10) = puVar6[0x11];
  *(undefined1 *)((int)param_1 + 0x41) = puVar6[0x10];
  *(undefined1 *)((int)param_1 + 0x42) = puVar6[0x13];
  *(undefined1 *)((int)param_1 + 0x43) = puVar6[0x12];
  uVar2 = FUN_43acb89a(uVar3);
  *(undefined1 *)(param_1 + 0x16) = uVar2;
  uVar2 = FUN_43acb888(uVar3);
  *(undefined1 *)((int)param_1 + 0x59) = uVar2;
  uVar3 = FUN_4387a650();
  param_1[0x17] = uVar3;
  return;
}


/* query "436be62a" */

undefined4 FUN_436be554(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  char cVar8;
  undefined1 auStack_19c [16];
  undefined4 uStack_18c;
  undefined1 auStack_12c [16];
  undefined4 uStack_11c;
  char acStack_bc [4];
  int iStack_b8;
  int iStack_b4;
  undefined1 auStack_a8 [4];
  int iStack_a4;
  uint uStack_a0;
  char acStack_94 [4];
  int iStack_90;
  int iStack_8c;
  char acStack_80 [4];
  int iStack_7c;
  int iStack_78;
  int iStack_74;
  int iStack_70;
  char acStack_6c [4];
  int iStack_68;
  uint uStack_64;
  int iStack_60;
  int iStack_5c;
  char acStack_58 [8];
  uint uStack_50;
  bool abStack_44 [4];
  int iStack_40;
  undefined4 uStack_3c;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  undefined4 auStack_24 [2];
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 != param_1) {
    return 4;
  }
  FUN_439c5320(&DAT_43e786cc + iVar1 * 0x44,param_2);
  iVar2 = FUN_436bd834(param_2,&DAT_43e77b7c + iVar1 * 0x38);
  if (iVar2 == 0) {
    abStack_44[0] = *param_2 != 3;
    if (abStack_44[0]) {
      iStack_40 = param_2[2];
      uStack_3c = *(undefined4 *)(&DAT_43e77b7c + iVar1 * 0x38);
    }
    FUN_436bf67c(0,abStack_44,iVar1);
  }
  else {
    FUN_436bd72c(10,0,1,&DAT_43c90212);
    FUN_43902718(s__Error__sapl_SetDmaAddrTar___MEM_43c90224);
  }
  cVar8 = (&DAT_43f9229a)[iVar1];
  FUN_436bf4c4(0,acStack_6c,iVar1);
  if (*(int *)(&DAT_43e78c04 + iVar1 * 4) == 0) {
    if (acStack_6c[0] == '\0') {
      if (cVar8 == '\0') {
        if (param_2[3] == 0) {
          iVar3 = FUN_43902df8(param_2[6],(short)param_2[5],1,auStack_12c,10);
          if (iVar3 == 0) {
            iVar2 = 0;
          }
          else {
            FUN_436bd72c(10,0,1,&DAT_43c901b9,iVar3);
            iVar2 = 7;
            FUN_43902718(s__Error__MemOpen___X__43c901cb,iVar3);
          }
          uVar4 = FUN_43a3a9b4(uStack_11c,0x10,1);
          uVar4 = (param_2[3] & 1U) << 0x1e | uVar4 & 0x3fffffff;
        }
        else {
          iVar2 = 7;
          uVar4 = 0;
        }
        *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uVar4;
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          iStack_60 = param_2[0xf];
          iStack_5c = param_2[0x10];
          uStack_64 = uVar4;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c9024f);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c90261;
      }
      else {
        FUN_436bf4c4(1,acStack_80);
        if (acStack_80[0] != '\0') {
          iStack_68 = iStack_7c;
          iStack_60 = iStack_74;
          iStack_5c = iStack_70;
LAB_436be784:
          uStack_64 = iStack_78 + 0x780;
          acStack_6c[0] = '\x01';
          *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uStack_64;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c90291);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c902a3;
      }
LAB_436be736:
      FUN_43902718(pcVar5);
    }
    else {
LAB_436be78c:
      FUN_436bf498(0,acStack_6c,iVar1);
    }
  }
  else {
    if (acStack_6c[0] == '\0') {
      if (cVar8 == '\0') {
        iStack_28 = param_2[5];
        iStack_30 = param_2[3];
        iStack_2c = param_2[4];
        iVar2 = FUN_436bd834(&iStack_30,&DAT_43e77b90 + iVar1 * 0x38);
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          uStack_64 = *(uint *)(&DAT_43e77b90 + iVar1 * 0x38);
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c9024f);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c90261;
      }
      else {
        FUN_436bf4c4(1,acStack_94);
        if (acStack_94[0] != '\0') {
          iStack_68 = iStack_90;
          iStack_78 = iStack_8c;
          goto LAB_436be784;
        }
        FUN_436bd72c(10,0,1,&DAT_43c90291);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c902a3;
      }
      goto LAB_436be736;
    }
    *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uStack_64;
  }
  iVar2 = FUN_436bf4f0(iVar1);
  FUN_436bf4c4(1,acStack_58,iVar1);
  if (acStack_58[0] == '\0') {
    uVar4 = 0;
LAB_436be80a:
    *(uint *)(&DAT_43e77ba4 + iVar1 * 0x38) = uVar4;
  }
  else {
    uVar4 = uStack_50;
    if ((&DAT_43f9229a)[iVar1] == '\0') goto LAB_436be80a;
    if (uStack_50 < 0x81) {
      *(undefined4 *)(&DAT_43e77ba4 + iVar1 * 0x38) = 0;
      FUN_436bd72c(10,0,1,&DAT_43c902de);
      FUN_43902718(s__Error__sapl_SetDmaAddrOut___FMT_43c902f0);
    }
    else {
      *(uint *)(&DAT_43e77ba4 + iVar1 * 0x38) = uStack_50 - 0x80;
    }
  }
  if (iVar2 == 2) {
    FUN_436bf4c4(2,acStack_58,iVar1);
    if (acStack_58[0] == '\0') {
      *(undefined4 *)(&DAT_43e77ba8 + iVar1 * 0x38) = 0;
    }
    else {
      *(uint *)(&DAT_43e77ba8 + iVar1 * 0x38) = uStack_50;
    }
  }
  if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
    if ((&DAT_43f9229a)[iVar1] == '\0') {
      cVar8 = '\0';
      if (param_2[10] == 3) {
        uVar4 = (param_2[0xb] & 0xfU) << 0x18 | 0x60000000;
      }
      else {
        if (param_2[0xd] == 0) {
          iVar2 = FUN_43903280((short)param_2[0xc],0,0,auStack_19c,10);
          if (iVar2 != 0) {
            FUN_436bd72c(10,0,1,&DAT_43c901b9,iVar2);
            cVar8 = '\a';
            FUN_43902718(s__Error__MemOpen___X__43c901cb,iVar2);
          }
          uVar4 = FUN_43a3a9b4(uStack_18c,0x10,1);
        }
        else {
          uVar4 = FUN_43a3a9b4(param_2[0xd],0x10,1);
        }
        if (param_2[10] == 2) {
          uVar4 = uVar4 & 0xffffff | 0x40000000;
        }
        else {
          uVar4 = (param_2[10] & 1U) << 0x1e | uVar4 & 0x3fffffff;
        }
      }
      *(uint *)(&DAT_43e77bac + iVar1 * 0x38) = uVar4;
      if (cVar8 == '\0') {
        iStack_a4 = param_2[0xc];
        uStack_a0 = uVar4;
LAB_436be94c:
        auStack_a8[0] = 1;
        FUN_436bf7e8(0,auStack_a8,iVar1);
        goto LAB_436be956;
      }
      FUN_436bd72c(10,0,1,&DAT_43c90327);
      pcVar5 = s__Error__sapl_SetDmaAddrMBLOut___M_43c90339;
    }
    else {
      FUN_436bf818(1,acStack_bc,0);
      if (acStack_bc[0] != '\0') {
        iStack_a4 = iStack_b8;
        uStack_a0 = iStack_b4 + 0x780;
        *(uint *)(&DAT_43e77bac + iVar1 * 0x38) = uStack_a0;
        goto LAB_436be94c;
      }
      FUN_436bd72c(10,0,1,&DAT_43c9036a);
      pcVar5 = s__Error__sapl_SetDmaAddrMBLOut___M_43c9037c;
    }
    FUN_43902718(pcVar5);
  }
LAB_436be956:
  if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
    if ((&DAT_43f9229a)[iVar1] != '\0') {
      iVar2 = iVar1 * 0x38;
      if (*(uint *)(&DAT_43e77b90 + iVar2) < 0x81) {
        *(undefined4 *)(&DAT_43e77b9c + iVar2) = 0;
        FUN_436bd72c(10,0,1,&DAT_43c903b8);
        FUN_43902718(s__Error__sapl_SetDmaAddrOut___HME_43c903ca);
      }
      else {
        *(uint *)(&DAT_43e77b9c + iVar2) = *(uint *)(&DAT_43e77b90 + iVar2) - 0x80;
      }
      goto LAB_436be9b8;
    }
    uVar7 = *(undefined4 *)(&DAT_43e77b90 + iVar1 * 0x38);
  }
  else {
    iVar2 = iVar1 * 0x38;
    uVar7 = *(undefined4 *)(&DAT_43e77b90 + iVar2);
    *(undefined4 *)(&DAT_43e77b90 + iVar2) = 0;
    *(undefined4 *)(&DAT_43e77bac + iVar2) = uVar7;
  }
  *(undefined4 *)(&DAT_43e77b9c + iVar1 * 0x38) = uVar7;
LAB_436be9b8:
  uVar7 = FUN_43a3a9b4(param_2[0xe],0x10,1);
  iVar2 = iVar1 * 0x38;
  *(undefined4 *)(&DAT_43e77ba0 + iVar2) = uVar7;
  iVar3 = FUN_436bf3cc(0,auStack_24,iVar1);
  if (iVar3 == 0) {
    FUN_436bd72c(10,0,1,&DAT_43c90401);
    FUN_43902718(s__Error__sapl_SetDmaAddrParamBuff_43c90413);
    *(undefined4 *)(&DAT_43e77b98 + iVar2) = 0;
    uVar7 = 7;
  }
  else {
    uVar7 = 0;
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)(&DAT_43e77b98 + iVar2) = uVar6;
  }
  iVar2 = FUN_436bf3cc(1,auStack_24,iVar1);
  if (iVar2 == 0) {
    uVar7 = 7;
    FUN_436bd72c(10,0,1,&DAT_43c90401);
    FUN_43902718(s__Error__sapl_SetDmaAddrParamBuff_43c90413);
    *(undefined4 *)(&DAT_43e77b88 + iVar1 * 0x38) = 0;
  }
  else {
    if ((&DAT_43f9229a)[iVar1] == '\0') {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    }
    else {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
      iVar2 = iVar2 + -0x100;
    }
    *(int *)(&DAT_43e77b88 + iVar1 * 0x38) = iVar2;
  }
  iVar2 = FUN_436bf3cc(2,auStack_24,iVar1);
  if (iVar2 == 0) {
    uVar6 = 0;
  }
  else {
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
  }
  *(undefined4 *)(&DAT_43e77b8c + iVar1 * 0x38) = uVar6;
  if (*(int *)(&DAT_43e78bf4 + iVar1 * 4) == 1) {
    FUN_436bf42c(auStack_24,iVar1);
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)(&DAT_43e77bb0 + iVar1 * 0x38) = uVar6;
  }
  else {
    *(undefined4 *)(&DAT_43e77bb0 + iVar1 * 0x38) = 0;
  }
  return uVar7;
}

