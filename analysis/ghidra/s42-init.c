/* S41: read-only exports. */

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


/* 436d60e4 */

int * FUN_436d60e4(int *param_1)

{
  *param_1 = *(int *)(DAT_436d6110 + 0x436d60ec + DAT_436d6114) + 8;
  FUN_436d86a8(param_1 + 0xd4);
  FUN_436d60cc(param_1);
  return param_1;
}


/* 43ad909c */

void FUN_43ad909c(undefined4 *param_1)

{
  (**(code **)(*(int *)*param_1 + 0x94))();
  return;
}

