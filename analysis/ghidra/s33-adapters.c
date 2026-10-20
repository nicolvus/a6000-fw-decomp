/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

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


/* query "437de944" */

void FUN_437de944(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  FUN_43acabf4();
  uVar1 = DAT_44020894;
  param_1[2] = param_2;
  *param_1 = uVar1;
  param_1[1] = 0;
  return;
}


/* query "4380f5fc" */

void FUN_4380f5fc(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  iVar2 = FUN_435612d0(0x8f0139,&puStack_30,0x9a,0);
  puVar1 = puStack_30;
  if (iVar2 == 0) {
    puStack_30[1] = param_1;
    *puStack_30 = 1;
    *(undefined4 *)(puStack_30 + 2) = param_2;
    *(undefined4 *)(puStack_30 + 4) = 0;
    *(undefined4 *)(puStack_30 + 6) = 0;
    puStack_30[8] = param_3;
    FUN_439c5a04(auStack_50,0,0x20);
    auStack_50[0] = 0x20;
    FUN_43561244(0x910042,auStack_50);
    *(undefined4 *)(puVar1 + 4) = uStack_38;
    *(undefined4 *)(puVar1 + 6) = uStack_34;
    iVar2 = FUN_439c5004(puVar1 + 10,0x81,param_4,&stack0x00000000);
    if (iVar2 < 0) {
      FUN_435612ec(0x8f0139,puStack_30);
    }
    else {
      if (0x7f < iVar2) {
        iVar2 = 0x80;
      }
      puVar1[9] = (short)iVar2 + 1;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x14) = 10;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x15) = 0;
      *(undefined4 *)(puStack_30 + -2) = 0x8f0139;
      FUN_4356120c();
    }
  }
  return;
}


/* query "4380e2a8" */

undefined4 FUN_4380e2a8(undefined4 param_1)

{
  FUN_4380e284(param_1,DAT_44025530);
  return param_1;
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


/* query "4381bbf0" */

undefined8 FUN_4381bbf0(uint param_1,int *param_2,int param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int iVar7;
  
  uVar5 = param_1;
  piVar6 = param_2;
  iVar7 = param_3;
  piVar1 = (int *)FUN_43b0473e(&DAT_43eeaf5c);
  if (piVar1 == (int *)0x0) {
    if (4 < DAT_43eeaf58) goto LAB_4381bd16;
    DAT_43eeaf58 = DAT_43eeaf58 + 1;
    uVar5 = DAT_43eeaf58;
    FUN_4381b9d0(5,3,1,&DAT_43cb43d0,DAT_43eeaf58,piVar6,iVar7);
    FUN_43902718(s_Image__Branch_Image_NULL__d_43cb43df,DAT_43eeaf58);
    if (DAT_43eeaf58 == 1) {
      FUN_43901a8c(3,0,2,0x77);
    }
    if (DAT_43eeaf58 == 5) {
      FUN_4381b9d0(5,3,1,&LAB_43cb437e_1,uVar5,piVar6,iVar7);
      FUN_43902718(s_Image_NULL_log_end_43cb438e);
    }
  }
  else {
    *piVar1 = param_3;
    iVar2 = param_2[0x11];
    *(undefined1 *)((int)piVar1 + 0x22) = 1;
    *(char *)((int)piVar1 + 0x23) = (char)iVar2;
    *(undefined2 *)(piVar1 + 8) = *(undefined2 *)(param_1 + 0x20);
    iVar2 = param_2[1];
    iVar3 = param_2[2];
    iVar4 = param_2[3];
    piVar1[2] = *param_2;
    piVar1[3] = iVar2;
    piVar1[4] = iVar3;
    piVar1[5] = iVar4;
    piVar1[6] = param_2[4];
    iVar2 = param_2[5];
    piVar1[7] = param_2[0x10];
    FUN_437965ac(piVar1,iVar2);
    piVar1[0xe] = *(int *)(param_1 + 0x38);
    piVar1[0xf] = *(int *)(param_1 + 0x3c);
    iVar2 = *(int *)(param_1 + 0x28);
    iVar3 = *(int *)(param_1 + 0x2c);
    iVar4 = *(int *)(param_1 + 0x30);
    piVar1[9] = *(int *)(param_1 + 0x24);
    piVar1[10] = iVar2;
    piVar1[0xb] = iVar3;
    piVar1[0xc] = iVar4;
    piVar1[0xd] = *(int *)(param_1 + 0x34);
    if (*piVar1 != 0) goto LAB_4381bd16;
    if (DAT_43eeaf58 < 5) {
      DAT_43eeaf58 = DAT_43eeaf58 + 1;
      uVar5 = DAT_43eeaf58;
      FUN_4381b9d0(5,3,1,&DAT_43cb43fb,DAT_43eeaf58,piVar6,iVar7);
      FUN_43902718(s_Image__Branch_ImageParam_NULL__d_43cb440a,DAT_43eeaf58);
      if (DAT_43eeaf58 == 1) {
        FUN_43901a8c(3,0,3,0x93);
      }
      if (DAT_43eeaf58 == 5) {
        FUN_4381b9d0(5,3,1,&LAB_43cb437e_1);
        FUN_43902718(s_Image_NULL_log_end_43cb438e);
      }
    }
    FUN_4381ba7c(piVar1);
  }
  piVar1 = (int *)0x0;
LAB_4381bd16:
  return CONCAT44(uVar5,piVar1);
}


/* query "4381b82c" */

undefined4 FUN_4381b82c(void)

{
  return DAT_43eeaf40;
}


/* query "4401fc84" */
