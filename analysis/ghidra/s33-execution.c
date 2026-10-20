/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4380e2e8" */

void FUN_4380e2e8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8,
                 undefined4 param_9,undefined4 param_10,int param_11)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined1 auStack_3c [24];
  
  iVar1 = param_11;
  *(undefined4 *)(param_11 + 4) = param_1;
  *(undefined4 *)(param_11 + 8) = param_2;
  *(undefined4 *)(param_11 + 0xc) = param_3;
  *(undefined4 *)(param_11 + 0x10) = param_4;
  *(undefined4 *)(param_11 + 0x14) = param_5;
  *(undefined4 *)(param_11 + 0x1c) = param_6;
  *(undefined4 *)(param_11 + 0x20) = param_7;
  *(undefined4 *)(param_11 + 0x24) = param_8;
  *(undefined4 *)(param_11 + 0x28) = param_9;
  *(undefined4 *)(param_11 + 0x2c) = param_10;
  FUN_43b03a2e(auStack_3c);
  iVar2 = thunk_FUN_43ad2ea8(&param_6,auStack_3c);
  if (iVar2 == 0) {
    FUN_43b03a3c(iVar1 + 0x30,DAT_44025aec);
  }
  else {
    FUN_43afb43a(&uStack_50,0);
    *(undefined4 *)(iVar1 + 0x30) = uStack_50;
    *(undefined4 *)(iVar1 + 0x34) = uStack_4c;
    *(undefined4 *)(iVar1 + 0x38) = uStack_48;
    *(undefined4 *)(iVar1 + 0x3c) = uStack_44;
    *(undefined4 *)(iVar1 + 0x40) = uStack_40;
  }
  return;
}


/* query "43afb46a" */

undefined4 FUN_43afb46a(undefined4 param_1)

{
  FUN_437de944();
  return param_1;
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


/* query "43b048b2" */

uint FUN_43b048b2(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_43b048ae();
  iVar2 = FUN_43b048ae(param_2);
  return (~(iVar1 - iVar2) & 0xffffU) >> 0xf;
}


/* query "4380f5d8" */

void FUN_4380f5d8(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  FUN_43acabf4();
  uVar1 = DAT_4401fc84;
  param_1[2] = param_2;
  *param_1 = uVar1;
  param_1[1] = 0;
  return;
}


/* query "43560d38" */

void FUN_43560d38(void)

{
  (**(code **)(*(int *)(DAT_440205c0 + 0x14) + 0x84))();
  return;
}


/* query "43b04914" */

void FUN_43b04914(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  int iVar2;
  int iStack_10;
  undefined4 uStack_c;
  
  iStack_10 = param_1;
  uStack_c = param_2;
  FUN_43560d38(0x1b,0xffffffff);
  FUN_43afc59c(&uStack_c,0);
  uStack_c = FUN_43afc5b6(param_1 + 4);
  while( true ) {
    iStack_10 = FUN_43afc5a8(param_1 + 4);
    iVar2 = FUN_43b048d4(&uStack_c,&iStack_10);
    if (iVar2 == 0) break;
    puVar1 = (undefined4 *)FUN_43b048e0(&uStack_c);
    FUN_43b048cc(*puVar1);
    FUN_43b04908(&uStack_c);
  }
  FUN_43560d1c(0x1b);
  return;
}


/* query "43903280" */

undefined4
FUN_43903280(undefined4 param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4,
            ushort param_5)

{
  byte *pbVar1;
  uint *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  int iStack_98;
  short sStack_94;
  short sStack_92;
  short sStack_8e;
  short sStack_8c;
  undefined4 uStack_88;
  int iStack_84;
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined2 uStack_24;
  
  FUN_439c5a04(&iStack_98,0,0x78);
  pbVar1 = DAT_44024494;
  iStack_98 = (uint)param_5 << 0x10;
  sStack_94 = 5;
  uStack_80 = 0x55;
  uStack_24 = 0x70;
  sStack_92 = (short)param_1;
  uVar6 = *DAT_44024494 & 1;
  uStack_88 = param_3;
  uStack_7e = param_2;
  if ((*DAT_44024494 & 1) != 0) {
    uVar6 = thunk_FUN_436cd00c();
    puVar2 = DAT_44024eac;
    uVar5 = *DAT_44023818;
    if (uVar5 < 0x20) {
      *DAT_44023818 = uVar5 + 1;
      *puVar2 = 1 << (uVar5 & 0xff) | *puVar2;
    }
  }
  FUN_43561524(&iStack_98);
  puVar2 = DAT_44024eac;
  if ((*pbVar1 & 1) != 0) {
    if (*DAT_44023818 != 0) {
      uVar5 = *DAT_44023818 - 1;
      *DAT_44023818 = uVar5;
      *puVar2 = *puVar2 & ~(1 << (uVar5 & 0xff));
    }
    iVar3 = thunk_FUN_436cd00c();
    if (*(uint *)(DAT_4401f718 + 0x14) < iVar3 - uVar6) {
      *(uint *)(DAT_4401f718 + 0x14) = iVar3 - uVar6;
      *(undefined4 *)(DAT_44020cec + 0x14) = param_1;
    }
  }
  if (sStack_92 == 0) {
    if ((sStack_94 == -0x7ffb) && (sStack_8e == 0x55)) {
      if ((sStack_8c == 0) || (iStack_84 == 0)) {
        FUN_43902984(5,1,1,&DAT_43ccea7a);
        FUN_43902718(s_Open__ERR_DMM_OPEN__43ccea85);
        uVar4 = 0xfffffff9;
      }
      else {
        FUN_439c5320(param_4,&sStack_94,0x70);
        uVar4 = 0;
      }
    }
    else {
      FUN_43902984(5,1,1,&DAT_43ccea39,sStack_94,0x8001);
      FUN_43902718(s_Open__ERR_DMM_DIFFERENT_COMP__ms_43ccea44,sStack_94,0x8001);
      uVar4 = 0xfffffffb;
    }
  }
  else {
    FUN_43902984(5,1,1,&DAT_43ccea0e,(int)sStack_92,param_1);
    FUN_43902718(s_Open__ERR_DMM_RET_CODE____d___x_43ccea19,(int)sStack_92,param_1);
    uVar4 = 0xfffffffc;
  }
  return uVar4;
}

