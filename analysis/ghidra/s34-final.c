/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814e04" */

undefined8 FUN_43814e04(char *param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  
  pcVar1 = param_1;
  if ((param_1 != (char *)0x0) && (param_1 != (char *)0x1)) {
    pcVar1 = s_EnumConverter_h_43cb0bbf;
    FUN_43814c78(5,0,1,&DAT_43c9b47c,s_EnumConverter_h_43cb0bbf,0x10c,param_3);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_EnumConverter_h_43cb0bbf,0x10c);
    param_1 = (char *)0x0;
  }
  return CONCAT44(pcVar1,param_1);
}


/* query "43814e44" */

undefined8 FUN_43814e44(char *param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  
  pcVar1 = param_1;
  if ((param_1 != (char *)0x0) && (param_1 != (char *)0x1)) {
    pcVar1 = s_EnumConverter_h_43cb0bbf;
    FUN_43814c78(5,0,1,&DAT_43c9b47c,s_EnumConverter_h_43cb0bbf,0x119,param_3);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_EnumConverter_h_43cb0bbf,0x119);
    param_1 = (char *)0x0;
  }
  return CONCAT44(pcVar1,param_1);
}


/* query "43814e84" */

char FUN_43814e84(int param_1)

{
  if (param_1 - 0x20U < 9) {
    return s__SHARE_ERR__APL_INPUT_JPEG_DEC__43cb3ef8[param_1];
  }
  return '\0';
}


/* query "4380f440" */

void FUN_4380f440(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  if ((DAT_43eea2d8 & 1) == 0) {
    FUN_43afb46a(&uStack_3c,DAT_4402176c);
    FUN_43b03a2e(&uStack_50);
    FUN_43afb43a(&uStack_64,0);
    FUN_439c5a04(&DAT_43eea2e4,0,0x44);
    DAT_43eea2e8 = uStack_3c;
    DAT_43eea2ec = uStack_38;
    DAT_43eea2f0 = uStack_34;
    DAT_43eea2f4 = uStack_30;
    DAT_43eea2f8 = uStack_2c;
    DAT_43eea300 = uStack_50;
    DAT_43eea304 = uStack_4c;
    DAT_43eea308 = uStack_48;
    DAT_43eea30c = uStack_44;
    DAT_43eea310 = uStack_40;
    DAT_43eea314 = uStack_64;
    DAT_43eea318 = uStack_60;
    DAT_43eea31c = uStack_5c;
    DAT_43eea320 = uStack_58;
    DAT_43eea324 = uStack_54;
    DAT_43eea2d8 = 1;
  }
  iVar1 = FUN_437c1d38(*(undefined2 *)(*param_1 + 4));
  if ((iVar1 == 0) || (DAT_43eea2e4 == 0)) {
    FUN_4380e43c(param_1,param_3,param_4);
  }
  FUN_439c5320(param_2,&DAT_43eea2e4,0x44);
  return;
}


/* query "4379140c" */

void s32_candidate_4379140c(void)

{
  undefined4 uVar1;
  undefined1 auStack_1c [20];
  
  uVar1 = *DAT_43e9920c;
  FUN_43ae8c7a(uVar1,&DAT_43e9baa8);
  FUN_43ada220(auStack_1c,0x4379210d);
  FUN_439018b0(&DAT_43e9b528,auStack_1c,uVar1,0);
  return;
}


/* query "436be554" */

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


/* query "436c0354" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c0354(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50420 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0x20) = param_1;
  return;
}


/* query "436c041c" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c041c(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50434 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0x34) = param_1;
  return;
}


/* query "436c04e4" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c04e4(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a50450 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0x50) = param_1;
  return;
}


/* query "436c06fc" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436c06fc(undefined4 param_1,int param_2)

{
  undefined1 *puVar1;
  
  if (param_2 == 1) {
    puVar1 = &DAT_f3950400;
  }
  else {
    if (param_2 != 0) {
      if (param_2 == 2) {
        _DAT_f3a504a4 = param_1;
      }
      return;
    }
    puVar1 = &DAT_f3850400;
  }
  *(undefined4 *)(puVar1 + 0xa4) = param_1;
  return;
}


/* query "43eea2e4" */

/* query "fc0a0014" */

/* query "fc0a0018" */

/* query "fc01f15c" */

/* query "fc01f160" */
