/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43e9d7a8" */

/* query "43e9d7e4" */

/* query "43ae96d4" */

undefined4 FUN_43ae96d4(undefined4 param_1)

{
  FUN_43ae96d0();
  return param_1;
}


/* query "43ae96e0" */

undefined8 FUN_43ae96e0(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  uStack_c = param_2;
  uStack_8 = param_3;
  FUN_43ae96d4(&uStack_c,*param_1);
  return CONCAT44(param_1,uStack_c);
}


/* query "43ae96f0" */

undefined8 FUN_43ae96f0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  uStack_c = param_2;
  uStack_8 = param_3;
  FUN_43ae96d4(&uStack_c,param_1);
  return CONCAT44(param_1,uStack_c);
}


/* query "43ae968e" */

bool FUN_43ae968e(int *param_1,int *param_2)

{
  return *param_1 != *param_2;
}


/* query "43ae969a" */

int FUN_43ae969a(int *param_1)

{
  return *param_1 + 8;
}


/* query "43ae9708" */

undefined4 FUN_43ae9708(undefined4 param_1)

{
  FUN_43ae96fe();
  return param_1;
}


/* query "43ae973c" */

void FUN_43ae973c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  int iStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  iStack_18 = param_1;
  uStack_14 = param_2;
  uStack_10 = param_3;
  uStack_14 = FUN_43ae96e0();
  while( true ) {
    iStack_18 = FUN_43ae96f0(param_1);
    iVar2 = FUN_43ae968e(&uStack_14,&iStack_18);
    uVar1 = uStack_14;
    if (iVar2 == 0) break;
    FUN_43ae9708(&uStack_14);
    FUN_43ae9714(*(undefined4 *)(param_1 + 0xc),uVar1);
  }
  *(int *)param_1 = param_1;
  *(int *)(param_1 + 4) = param_1;
  *(undefined4 *)(param_1 + 8) = 0;
  return;
}


/* query "43796848" */

void FUN_43796848(int param_1,undefined4 param_2)

{
  int iVar1;
  int iStack_10;
  undefined4 uStack_c;
  
  if (*(char *)(*(int *)(param_1 + 0x20) + 2) != '\0') {
    iStack_10 = param_1;
    uStack_c = param_2;
    FUN_43ae96d4(&uStack_c,0);
    uStack_c = FUN_43ae96e0(&DAT_43e9d7d4);
    while( true ) {
      iStack_10 = FUN_43ae96f0(&DAT_43e9d7d4);
      iVar1 = FUN_43ae968e(&uStack_c,&iStack_10);
      if (iVar1 == 0) break;
      iVar1 = FUN_43ae969a(&uStack_c);
      thunk_FUN_43ad6034(iVar1,*(undefined4 *)(iVar1 + 0x14));
      iVar1 = FUN_43ae969a(&uStack_c);
      if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
        (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
      }
      FUN_43ae9708(&uStack_c);
    }
    FUN_43ae973c(&DAT_43e9d7d4);
  }
  return;
}


/* query "43796740" */

void FUN_4379671c(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  FUN_43ae96d4(&uStack_c,0);
  uStack_c = FUN_43ae96e0(&DAT_43e9d7a8);
  while( true ) {
    uStack_10 = FUN_43ae96f0(&DAT_43e9d7a8);
    iVar1 = FUN_43ae968e(&uStack_c,&uStack_10);
    if (iVar1 == 0) break;
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7a8);
  return;
}


/* query "43796794" */

void FUN_43796770(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  FUN_43ae96d4(&uStack_c,0);
  uStack_c = FUN_43ae96e0(&DAT_43e9d7e4);
  while( true ) {
    uStack_10 = FUN_43ae96f0(&DAT_43e9d7e4);
    iVar1 = FUN_43ae968e(&uStack_c,&uStack_10);
    if (iVar1 == 0) break;
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7e4);
  return;
}


/* query "43796904" */

void FUN_437968b0(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_1;
  uStack_c = param_2;
  FUN_43ae96d4(&uStack_c,0);
  uStack_c = FUN_43ae96e0(&DAT_43e9d7a8);
  while( true ) {
    uStack_10 = FUN_43ae96f0(&DAT_43e9d7a8);
    iVar1 = FUN_43ae968e(&uStack_c,&uStack_10);
    if (iVar1 == 0) break;
    iVar1 = FUN_43ae969a(&uStack_c);
    thunk_FUN_43ad6034(iVar1,*(undefined4 *)(iVar1 + 0x14));
    iVar1 = FUN_43ae969a(&uStack_c);
    if (*(int **)(iVar1 + 0x18) != (int *)0x0) {
      (**(code **)(**(int **)(iVar1 + 0x18) + 0xc))();
    }
    FUN_43ae9708(&uStack_c);
  }
  FUN_43ae973c(&DAT_43e9d7a8);
  return;
}


/* query "435a92e0" */

void FUN_435a92e0(int *param_1)

{
  *param_1 = DAT_44024bd8 + 8;
  *(undefined2 *)(param_1 + 2) = 0;
  param_1[1] = 0;
  param_1[3] = 0;
  *(undefined1 *)(param_1 + 4) = 0;
  return;
}


/* query "435a9460" */

undefined4 FUN_435a9460(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 4);
  if (iVar2 == 2) {
    FUN_435aa628(0x2047534d,0x3b,0xffffffe2);
    return 0xffffffe2;
  }
  if ((iVar2 == 1) && (*(int *)(param_1 + 0x1c) != 0x14)) {
    FUN_435aa628(0x2047534d,0x43,0xffffffe3);
    return 0xffffffe3;
  }
  if ((*(ushort *)(param_2 + 4) != param_3) || (param_3 < 8)) {
    FUN_435aa628(0x2047534d,0x4a,0xffffffe0);
    return 0xffffffe0;
  }
  if (iVar2 == 0) {
    FUN_43a4966c(param_1);
    *(undefined4 *)(param_1 + 4) = 1;
  }
  uVar1 = *(ushort *)(param_2 + 4);
  if (0xff < (uint)uVar1 + (uint)*(ushort *)(param_1 + 0x1a)) {
    FUN_435aa628(0x2047534d,0x56,0xffffffe4);
    return 0xffffffe4;
  }
  *(ushort *)(param_1 + 0x1a) = (short)param_3 + *(ushort *)(param_1 + 0x1a);
  iVar2 = *(ushort *)(param_1 + 0x18) + 1;
  *(short *)(param_1 + 0x18) = (short)iVar2;
  FUN_439c5320(param_1 + *(int *)(param_1 + 0x20) + 0x10,param_2,(uint)uVar1,iVar2,param_4);
  *(uint *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + (uint)*(ushort *)(param_2 + 4);
  return 0;
}


/* query "435aa20c" */

undefined4 FUN_435aa20c(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_1c;
  
  iVar2 = *(int *)(param_3 + 4);
  uStack_1c = param_4;
  if (iVar2 == 1) {
    uVar1 = *(undefined2 *)(param_3 + 0x1a);
  }
  else {
    if (iVar2 != 2) {
      uVar3 = 0xffff;
      if (iVar2 == 0) {
        uVar3 = 0xffffffe5;
      }
      FUN_435aa628(0x444e4553,0x3c,uVar3);
      return uVar3;
    }
    uVar1 = *(undefined2 *)(param_3 + 8);
  }
  iVar2 = FUN_435612d0(param_2,&uStack_1c,uVar1,1,param_1,param_2,param_3);
  if (iVar2 == 0) {
    FUN_439c5320(uStack_1c,param_3 + 0x10,uVar1);
    FUN_43a49adc(uStack_1c,*(undefined4 *)(param_3 + 0xc));
    iVar2 = FUN_4356120c(param_2,uStack_1c);
    if (iVar2 == 0) {
      return 0;
    }
    FUN_435aa5c4(9,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
    FUN_435612ec(param_2,uStack_1c);
  }
  else {
    FUN_435aa5c4(8,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
  }
  uVar3 = FUN_435aa044(param_1,iVar2);
  return uVar3;
}

