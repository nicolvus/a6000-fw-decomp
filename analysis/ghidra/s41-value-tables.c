/* S41: read-only exports. */

/* 43b00f22 */

void FUN_43b00f22(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 2) {
    *(undefined1 *)(param_1 + 0xca0) = 10;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 0xca2) = sVar1;
    *(short *)(param_1 + 0x570) = sVar1;
    *(undefined1 *)(param_1 + 0xca1) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 0xca0,0x28);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0x56c) = 0;
    }
  }
  return;
}


/* 43b00f62 */

void FUN_43b00f62(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    *(undefined1 *)(param_1 + 0x6c0) = 10;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 0x6c2) = sVar1;
    *(short *)(param_1 + 0x570) = sVar1;
    *(undefined1 *)(param_1 + 0x6c1) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 0x6c0,0x5e0);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0x56c) = 0;
    }
  }
  return;
}


/* 43b01026 */

void FUN_43b01026(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    *(undefined1 *)(param_1 + 4) = 1;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 6) = sVar1;
    *(short *)(param_1 + 0x578) = sVar1;
    *(undefined1 *)(param_1 + 5) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 4,0x564);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0x574) = 0;
    }
  }
  return;
}


/* 43b00cd0 */

void FUN_43b00cd0(undefined4 *param_1,int param_2)

{
  if (param_1[0x15a] == 1) {
    *(undefined4 *)(param_2 + 0xb8) = *param_1;
    FUN_439c5320(param_1 + 0x1b1,param_1 + 1,0x564);
  }
  thunk_FUN_439c5320(param_1 + 2,param_2,0x560);
  return;
}


/* 435aa20c */

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
      FUN_435aa628(DAT_435aa2a8,0x3c,uVar3);
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


/* 43a49628 */

undefined4 FUN_43a49628(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0xc) = param_2;
  return 0;
}


/* 4380a050 */

void FUN_4380a050(int *param_1)

{
  *param_1 = *(int *)(DAT_4380a064 + 0x4380a058 + DAT_4380a068) + 8;
  param_1[1] = 0;
  return;
}


/* 4372a3c4 */

void FUN_4372a3c4(undefined4 *param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined1 auStack_44 [12];
  undefined4 uStack_38;
  undefined1 uStack_34;
  undefined1 auStack_30 [8];
  undefined1 auStack_28 [2];
  undefined2 uStack_26;
  undefined4 uStack_24;
  undefined1 auStack_1c [8];
  
  FUN_43560de0(0x12,1,0,auStack_1c,0xffffffff);
  auStack_28[0] = 5;
  uStack_26 = 0xd008;
  uStack_24 = 0;
  FUN_43ae12c4(auStack_28,auStack_44,DAT_4372a414,0xffffffff);
  *param_1 = uStack_38;
  *param_2 = uStack_34;
  FUN_439c5320(param_3,auStack_30,8);
  return;
}

