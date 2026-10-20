/* S41: read-only exports. */

/* 43ae8e2c */

void FUN_43ae8e2c(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x1e50);
  *(int *)(param_2 + 0x34) = iVar1;
  *(int *)(param_2 + 0x58) = iVar1 + 0xa68;
  *(int *)(param_2 + 0x78) = iVar1 + 0x7d8;
  return;
}


/* 43ae8e44 */

void FUN_43ae8e44(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x1e54);
  *(int *)(param_2 + 0x60) = iVar1 + 0x138;
  *(int *)(param_2 + 0x38) = iVar1;
  *(int *)(param_2 + 0x84) = iVar1 + 0x134;
  return;
}


/* 43ae8e5c */

void FUN_43ae8e5c(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x1e58);
  *(int *)(param_2 + 0x68) = iVar1 + 0xf10;
  *(int *)(param_2 + 0x3c) = iVar1;
  *(int *)(param_2 + 0x90) = iVar1 + 500;
  return;
}


/* 43ae8e74 */

void FUN_43ae8e74(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x1e5c);
  *(int *)(param_2 + 0x40) = iVar1;
  *(int *)(param_2 + 0xa0) = iVar1 + 2;
  return;
}


/* 43ae8e84 */

void FUN_43ae8e84(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x1e60);
  *(int *)(param_2 + 0x70) = iVar1 + 0x440;
  *(int *)(param_2 + 0x44) = iVar1;
  *(int *)(param_2 + 0xa8) = iVar1 + 8;
  return;
}


/* 43ae8e9a */

void FUN_43ae8e9a(int param_1,int param_2)

{
  *(undefined4 *)(param_2 + 0x48) = *(undefined4 *)(param_1 + 0x1e64);
  return;
}


/* 43ae8ea4 */

void FUN_43ae8ea4(int param_1,int param_2)

{
  *(undefined4 *)(param_2 + 0x4c) = *(undefined4 *)(param_1 + 0x1e68);
  return;
}


/* 43ad3b92 */

void FUN_43ad3b92(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  FUN_436c74c8(param_1,param_2,*(undefined4 *)(param_3 + 0x24),*(undefined4 *)(param_3 + 0x28),
               (int)*(char *)(param_3 + 0x7c),*(undefined1 *)(param_3 + 0x7d),
               *(undefined1 *)(param_3 + 0x7e),*(undefined1 *)(param_3 + 0x96),
               *(undefined4 *)(param_3 + 0x10),param_4,param_5,param_6);
  return;
}


/* 43b04604 */

void FUN_43b04604(undefined4 param_1,undefined4 *param_2,undefined4 param_3)

{
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_28;
  uint uStack_1c;
  undefined1 uStack_18;
  undefined2 uStack_16;
  undefined4 uStack_14;
  
  FUN_439c5a04(&uStack_34,0,0x24);
  uStack_34 = FUN_437959b8();
  uStack_30 = FUN_4381b3d4(*param_2);
  uStack_28 = 0x1020;
  uStack_1c = (uint)*(byte *)(param_2 + 1);
  uStack_18 = FUN_4381b4a0();
  uStack_16 = *(undefined2 *)((int)param_2 + 6);
  uStack_14 = param_2[2];
  FUN_436d04c0(param_1,&uStack_34,param_3);
  FUN_43b0453c();
  return;
}

