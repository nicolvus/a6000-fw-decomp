/* S41: read-only exports. */

/* 436d6224 */

undefined4 FUN_436d6224(undefined4 *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_2 == 0) || (param_3 == 0)) {
    iVar2 = DAT_436d625c + 0x436d623a;
    FUN_436d6020(0xbc,0,1,DAT_436d6258 + 0x436d6238,iVar2,param_2);
    FUN_43902718(DAT_436d6260 + 0x436d6246,iVar2);
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x4c))();
  }
  return uVar1;
}


/* 4380e2e8 */

void FUN_4380e2e8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8,
                 undefined4 param_9,undefined4 param_10,int param_11)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined1 auStack_3c [24];
  
  iVar1 = param_11;
  iVar3 = DAT_4380e350 + 0x4380e2fc;
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
    FUN_43b03a3c(iVar1 + 0x30,*(undefined4 *)(iVar3 + DAT_4380e354));
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


/* 4380df30 */

undefined1 FUN_4380df30(int param_1,int param_2,int param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x10c) == 1) {
    if (param_2 != 0) {
      if (*(int *)(*(int *)(DAT_4380dfac + 0x4380df42 + DAT_4380dfb0) + 0x30) == 1) {
        uVar1 = 0;
      }
      else {
        uVar1 = 2;
      }
      return uVar1;
    }
    return 2;
  }
  if (param_2 == 0) {
    iVar2 = thunk_FUN_43700528();
    if (iVar2 == 0) {
      if ((param_3 != 1) || (iVar2 = 0, *(int *)(param_1 + 0x354) == 2)) {
        iVar2 = *(int *)(param_1 + 0xec);
      }
    }
    else {
      iVar2 = 1;
    }
    if (*(int *)(param_1 + 0xf0) != 1) {
      return false;
    }
    if (*(char *)(param_1 + 0x17c) == '\x02') {
      return false;
    }
  }
  else {
    if (*(int *)(*(int *)(DAT_4380dfac + 0x4380df42 + DAT_4380dfb0) + 0x30) == 1) {
      return false;
    }
    iVar2 = *(int *)(param_1 + 0xf0);
  }
  return iVar2 == 1;
}


/* 43795a60 */

void FUN_43795a60(undefined4 param_1,byte param_2,byte param_3,undefined4 *param_4)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  
  bVar1 = *(byte *)(DAT_43795a88 + 0x43795aa6);
  bVar2 = *(byte *)(DAT_43795a88 + 0x43795aa7);
  *param_4 = param_1;
  uVar3 = FUN_437959b8();
  *(byte *)((int)param_4 + 6) = param_2 ^ bVar1;
  *(byte *)((int)param_4 + 5) = param_3 ^ bVar2;
  *(undefined1 *)(param_4 + 1) = uVar3;
  return;
}


/* 436d72e8 */

int * FUN_436d72e8(int *param_1,int param_2)

{
  int iVar1;
  
  iVar1 = DAT_436d7470;
  FUN_436d93d0();
  iVar1 = iVar1 + 0x436d72fc;
  *param_1 = *(int *)(iVar1 + DAT_436d7474) + 8;
  FUN_43ad8cb2(param_1 + 0xa6,0,0x10,8,*(undefined4 *)(DAT_436d7478 + 0x436d730e + param_2 * 4));
  FUN_436d8774(param_1 + 0xd4,0xd,*(undefined4 *)(iVar1 + DAT_436d74b0),
               *(undefined4 *)(iVar1 + DAT_436d74b4),*(undefined4 *)(iVar1 + DAT_436d747c),
               *(undefined4 *)(iVar1 + DAT_436d7480),*(undefined4 *)(iVar1 + DAT_436d7484),
               DAT_436d7488 + 0x436d7336,DAT_436d748c + 0x436d733c,DAT_436d7490 + 0x436d7342,
               DAT_436d7494 + 0x436d7348,DAT_436d7498 + 0x436d734e,DAT_436d7498 + 0x436d73ea,
               DAT_436d749c + 0x436d7358,DAT_436d74a0 + 0x436d735e,
               *(undefined4 *)(iVar1 + DAT_436d74a4),*(undefined4 *)(iVar1 + DAT_436d74a8),
               DAT_436d74ac + 0x436d7370);
  *(undefined2 *)(param_1 + 0x6d) = 0x36;
  *(undefined2 *)(param_1 + 0x78) = 0x1f;
  iVar1 = DAT_436d746c;
  *(undefined1 *)((int)param_1 + 0x181) = 0;
  param_1[0x61] = 3;
  param_1[0x62] = 5;
  param_1[99] = 3;
  param_1[0x6c] = 0;
  *(undefined2 *)(param_1 + 0x68) = 0xfef;
  param_1[0x6e] = 0;
  param_1[0x70] = 0;
  param_1[0x71] = 0;
  param_1[0x72] = 2;
  *(undefined2 *)((int)param_1 + 0x1d2) = 0x1000;
  *(undefined2 *)(param_1 + 0x75) = 0x1000;
  param_1[0x76] = 0;
  *(undefined2 *)((int)param_1 + 0x1de) = 0;
  param_1[0x79] = iVar1;
  *(undefined1 *)(param_1 + 0xd2) = 2;
  *(undefined2 *)(param_1 + 0x7a) = 0x187;
  *(undefined1 *)((int)param_1 + 0x34a) = 0;
  *(undefined2 *)((int)param_1 + 0x1ea) = 0x92a;
  *(undefined1 *)(param_1 + 0x60) = 1;
  *(undefined2 *)(param_1 + 0x7b) = 0x61c;
  *(undefined1 *)((int)param_1 + 0x182) = 1;
  param_1[0x69] = 1;
  param_1[0x6a] = 1;
  param_1[0x6b] = 1;
  param_1[100] = 1;
  *(undefined1 *)((int)param_1 + 0x1b6) = 1;
  param_1[0x73] = 1;
  *(undefined2 *)(param_1 + 0x74) = 1;
  *(undefined2 *)((int)param_1 + 0x1ee) = 0xb03;
  *(undefined1 *)((int)param_1 + 0x349) = 1;
  *(undefined1 *)((int)param_1 + 0x34b) = 2;
  *(undefined1 *)(param_1 + 0xd3) = 0;
  *(undefined2 *)(param_1 + 0xe8) = 0;
  param_1[0x9b] = param_2;
  *(undefined1 *)((int)param_1 + 0x3a2) = 0xff;
  *(undefined1 *)((int)param_1 + 0x3a3) = 0;
  param_1[0xea] = -1;
  param_1[0xeb] = -1;
  *(undefined1 *)(param_1 + 0xe9) = 0;
  param_1[0xa5] = (int)(param_1 + 0xd4);
  return param_1;
}

