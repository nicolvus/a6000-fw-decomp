/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43a3a9b4" */

int FUN_43a3a9b4(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = param_1;
  if (param_2 == 0x11) {
    iVar1 = FUN_43560934(param_1,1);
    if (param_3 == 2) {
LAB_43a3aa2e:
      iVar1 = FUN_43561604();
      goto LAB_43a3aa38;
    }
    if (param_3 == 3) {
LAB_43a3aa34:
      iVar1 = FUN_435615e8();
      goto LAB_43a3aa38;
    }
    if (param_3 != 0) {
      return param_1;
    }
    uVar3 = 1;
LAB_43a3aa28:
    iVar2 = FUN_43560978(iVar2,uVar3);
  }
  else {
    if (param_2 != 0x12) {
      if (param_2 != 0x10) {
        return param_1;
      }
      if (param_3 == 2) goto LAB_43a3aa2e;
      if (param_3 == 3) goto LAB_43a3aa34;
      if (param_3 != 1) {
        return param_1;
      }
      iVar1 = FUN_43560934(param_1,0);
LAB_43a3aa02:
      uVar3 = 0;
      goto LAB_43a3aa28;
    }
    iVar1 = param_1;
    switch(param_3) {
    case 0:
      iVar1 = FUN_43561620();
      break;
    case 1:
      uVar3 = FUN_43561620();
      iVar1 = FUN_43560934(uVar3,0);
      iVar2 = FUN_43561620(param_1);
      goto LAB_43a3aa02;
    case 2:
      iVar1 = FUN_43561658();
      break;
    case 3:
      iVar1 = FUN_4356163c();
      break;
    default:
      goto switchD_43a3a9e2_default;
    }
LAB_43a3aa38:
    iVar2 = 0;
  }
  if ((iVar1 == 0) && (iVar2 == 0)) {
    iVar1 = param_1;
  }
switchD_43a3a9e2_default:
  return iVar1;
}


/* query "436bd834" */

undefined4 FUN_436bd834(uint *param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 auStack_88 [16];
  undefined4 uStack_78;
  
  if (*param_1 == 3) {
    uVar3 = 0;
    uVar2 = (param_1[1] & 0xf) << 0x18 | 0x60000000;
  }
  else {
    iVar1 = FUN_43903280((short)param_1[2],0,0,auStack_88,10);
    if (iVar1 == 0) {
      uVar3 = 0;
    }
    else {
      FUN_436bd72c(10,0,1,&DAT_43c901b9,iVar1);
      uVar3 = 7;
      FUN_43902718(s__Error__MemOpen___X__43c901cb,iVar1);
    }
    uVar2 = FUN_43a3a9b4(uStack_78,0x10,1);
    if (*param_1 == 2) {
      uVar2 = uVar2 & 0xffffff | 0x40000000;
    }
    else {
      uVar2 = (*param_1 & 1) << 0x1e | uVar2 & 0x3fffffff;
    }
  }
  *param_2 = uVar2;
  return uVar3;
}


/* query "43acb888" */

bool FUN_43acb888(void)

{
  int iVar1;
  
  FUN_43acb0a0();
  iVar1 = FUN_436bd404();
  return iVar1 != 0;
}


/* query "436bf500" */

undefined4 FUN_436bf500(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  char acStack_2c [4];
  undefined2 uStack_28;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  bVar1 = (&DAT_43f92393)[param_1];
  FUN_436bf4c4(bVar1 - 1,acStack_2c,param_1);
  if (param_2 == 0) {
    if (acStack_2c[0] == '\0') {
      return 1;
    }
    iVar2 = FUN_43903118(uStack_28,uStack_20,2,uStack_1c,10);
    if (iVar2 != 0) {
      FUN_436bf098(10,0,1,&DAT_43c90527,iVar2);
      FUN_43902718(s__Error__APL_Base_DDR_Free___X__43c90539,iVar2);
      return 0;
    }
  }
  else if (acStack_2c[0] == '\0') {
    return 1;
  }
  acStack_2c[0] = '\0';
  FUN_436bf498(bVar1 - 1,acStack_2c,param_1);
  return 1;
}


/* query "436bf6dc" */

undefined4 FUN_436bf6dc(undefined4 param_1)

{
  int iVar1;
  char acStack_24 [4];
  undefined2 uStack_20;
  
  FUN_436bf6ac(1,acStack_24,param_1);
  if (acStack_24[0] != '\0') {
    iVar1 = FUN_43902fbc(uStack_20,2,10);
    if (iVar1 != 0) {
      FUN_436bf098(10,0,1,&DAT_43c90558,iVar1);
      FUN_43902718(s__Error__APL_TAR_DDR_Free___X__43c9056a,iVar1);
      return 0;
    }
    acStack_24[0] = '\0';
    FUN_436bf67c(1,acStack_24,param_1);
  }
  return 1;
}


/* query "436bf3a8" */

void FUN_436bf3a8(int param_1)

{
  char cVar1;
  
  param_1 = param_1 * 0xc;
  cVar1 = (&DAT_43e78d4c)[param_1];
  (&DAT_43e78d4c)[param_1] = cVar1 + 1U;
  if ((byte)(&DAT_43e78d44)[param_1] <= (byte)(cVar1 + 1U)) {
    (&DAT_43e78d4c)[param_1] = 0;
  }
  return;
}


/* query "43acb2e8" */

void FUN_43acb2e8(undefined4 param_1)

{
  FUN_436c019c(0,param_1);
  FUN_436c019c(1,param_1);
  return;
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

