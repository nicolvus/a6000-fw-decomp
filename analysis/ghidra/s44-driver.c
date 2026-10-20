/* S41: read-only exports. */

/* 436d99b8 */

void FUN_436d99b8(int *param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7,int param_8,int param_9,int param_10,int param_11,int param_12,
                 int param_13,int param_14,int param_15)

{
  int iVar1;
  
  iVar1 = *(int *)(DAT_436d9a00 + 0x436d99c4 + DAT_436d9a04);
  param_1[4] = param_4;
  param_1[1] = param_2;
  *param_1 = iVar1 + 8;
  param_1[5] = param_5;
  *(undefined1 *)(param_1 + 3) = 0;
  param_1[2] = param_3;
  param_1[6] = param_6;
  param_1[7] = param_7;
  param_1[8] = param_8;
  param_1[9] = param_9;
  param_1[10] = param_14;
  param_1[0xb] = param_15;
  param_1[0xc] = param_10;
  param_1[0xd] = param_11;
  param_1[0xe] = param_12;
  param_1[0xf] = param_13;
  return;
}


/* 43ad9322 */

int FUN_43ad9322(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  FUN_43ad9aec();
  FUN_43ad9af8(param_1 + 1);
  FUN_43ad9af0(param_1 + 4);
  FUN_43ad9aee(param_1 + 0xc);
  FUN_43ad9ae4(param_1 + 0xd);
  FUN_43ad9ae6(param_1 + 0x10);
  *(undefined2 *)(param_1 + 100) = 0;
  *(undefined4 *)(param_1 + 0x68) = 1;
  iVar2 = 0;
  iVar3 = param_1;
  do {
    iVar4 = iVar2;
    iVar2 = iVar4 + 1;
    *(undefined1 *)(iVar3 + 0x14) = 0;
    *(undefined1 *)(iVar3 + 0x15) = 0;
    *(undefined1 *)(iVar3 + 0x2c) = 0;
    *(undefined1 *)(iVar3 + 0x2d) = 0;
    iVar3 = iVar3 + 2;
  } while (iVar2 != 0xc);
  *(undefined1 *)(param_1 + 0x6c) = 3;
  *(undefined1 *)(param_1 + 0x7c) = 3;
  *(undefined1 *)(param_1 + 0x93) = 1;
  cVar1 = (char)iVar4 + 'E';
  *(undefined1 *)(param_1 + 0x9d) = 1;
  *(undefined4 *)(param_1 + 0x70) = 0;
  *(undefined4 *)(param_1 + 0x74) = 0;
  *(undefined1 *)(param_1 + 0x78) = 0;
  *(undefined1 *)(param_1 + 0x79) = 0;
  *(undefined4 *)(param_1 + 0x80) = 0;
  *(undefined4 *)(param_1 + 0x84) = 0;
  *(undefined1 *)(param_1 + 0x88) = 0;
  *(undefined1 *)(param_1 + 0x89) = 0;
  *(undefined1 *)(param_1 + 0x8c) = 0;
  *(undefined1 *)(param_1 + 0x8e) = 0;
  *(char *)(param_1 + 0x8f) = cVar1;
  *(undefined1 *)(param_1 + 0x90) = 0;
  *(undefined1 *)(param_1 + 0x91) = 0;
  *(undefined1 *)(param_1 + 0x92) = 0;
  *(undefined1 *)(param_1 + 0x94) = 0;
  *(undefined1 *)(param_1 + 0x95) = 0;
  *(undefined1 *)(param_1 + 0x96) = 0;
  *(undefined1 *)(param_1 + 0x98) = 0;
  *(char *)(param_1 + 0x99) = cVar1;
  *(undefined1 *)(param_1 + 0x9a) = 0;
  *(undefined1 *)(param_1 + 0x9b) = 0;
  *(undefined1 *)(param_1 + 0x9c) = 0;
  *(undefined1 *)(param_1 + 0x9e) = 0;
  *(undefined1 *)(param_1 + 0x9f) = 0;
  *(undefined1 *)(param_1 + 0xa0) = 0;
  iVar2 = param_1;
  iVar3 = 0;
  do {
    iVar4 = iVar3;
    *(undefined1 *)(iVar2 + 0x44) = 1;
    *(char *)(iVar2 + 0x45) = (char)iVar4;
    *(undefined1 *)(iVar2 + 0x54) = 1;
    *(char *)(iVar2 + 0x55) = (char)iVar4;
    iVar2 = iVar2 + 2;
    iVar3 = iVar4 + 1;
  } while (iVar4 + 1 != 8);
  iVar4 = iVar4 + -7;
  *(short *)(param_1 + 0xd4) = (short)iVar4;
  *(int *)(param_1 + 0xd8) = iVar4;
  *(short *)(param_1 + 0xdc) = (short)iVar4;
  *(int *)(param_1 + 0xe0) = iVar4;
  iVar2 = param_1;
  do {
    iVar4 = iVar4 + 1;
    *(undefined1 *)(iVar2 + 0xa1) = 0;
    *(undefined1 *)(iVar2 + 0xa2) = 0;
    *(undefined1 *)(iVar2 + 0xb9) = 0;
    *(undefined1 *)(iVar2 + 0xba) = 0;
    iVar2 = iVar2 + 2;
  } while (iVar4 != 0xc);
  return param_1;
}


/* 436d6118 */

undefined4 FUN_436d6118(void)

{
  return *(undefined4 *)(DAT_436d6124 + 0x436d6120 + DAT_436d6128);
}


/* 436d6450 */

undefined4 FUN_436d6450(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == 0) {
    iVar2 = DAT_436d6484 + 0x436d6462;
    FUN_436d6020(0xbc,0,1,DAT_436d6480 + 0x436d6460,iVar2,0);
    FUN_43902718(DAT_436d6488 + 0x436d646e,iVar2);
    uVar1 = 1;
  }
  else {
    uVar1 = (**(code **)(*(int *)*param_1 + 0x68))();
  }
  return uVar1;
}

