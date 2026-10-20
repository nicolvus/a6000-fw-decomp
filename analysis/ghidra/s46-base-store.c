/* S41: read-only exports. */

/* 43acee66 */

void FUN_43acee66(undefined4 *param_1,undefined4 param_2)

{
  *param_1 = param_2;
  return;
}


/* 436c6b6c */

void FUN_436c6b6c(int *param_1)

{
  *param_1 = *(int *)(DAT_436c6b7c + 0x436c6b74 + DAT_436c6b80) + 8;
  return;
}


/* 43ae8faa */

int FUN_43ae8faa(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  FUN_439c5320(param_1,param_2,0x560,param_4,param_4);
  FUN_439c5320(param_1 + 0x560,param_2 + 0x560,0x44);
  FUN_439c5320(param_1 + 0x5a4,param_2 + 0x5a4,0xcec);
  FUN_439c5320(param_1 + 0x1290,param_2 + 0x1290,0x4a0);
  FUN_43ae4a0c(param_1 + 0x1730,param_2 + 0x1730);
  *(undefined1 *)(param_1 + 0x18d0) = *(undefined1 *)(param_2 + 0x18d0);
  *(undefined1 *)(param_1 + 0x18d1) = *(undefined1 *)(param_2 + 0x18d1);
  FUN_439c5320(param_1 + 0x18d4,param_2 + 0x18d4,0xbc);
  FUN_439c5320(param_1 + 0x1990,param_2 + 0x1990,0x13f);
  uVar1 = *(undefined4 *)(param_2 + 0x1ad4);
  uVar2 = *(undefined4 *)(param_2 + 0x1ad8);
  *(undefined4 *)(param_1 + 0x1ad0) = *(undefined4 *)(param_2 + 0x1ad0);
  *(undefined4 *)(param_1 + 0x1ad4) = uVar1;
  *(short *)(param_1 + 0x1ad8) = (short)uVar2;
  *(undefined2 *)(param_1 + 0x1ada) = *(undefined2 *)(param_2 + 0x1ada);
  *(undefined2 *)(param_1 + 0x1adc) = *(undefined2 *)(param_2 + 0x1adc);
  FUN_439c5320(param_1 + 0x1ade,param_2 + 0x1ade,0xe);
  FUN_439c5320(param_1 + 0x1aec,param_2 + 0x1aec,0xe0);
  FUN_43ae502c(param_1 + 0x1bcc,param_2 + 0x1bcc);
  FUN_439c5320(param_1 + 0x1d40,param_2 + 0x1d40,0xfc);
  uVar1 = *(undefined4 *)(param_2 + 0x1e40);
  uVar2 = *(undefined4 *)(param_2 + 0x1e44);
  uVar3 = *(undefined4 *)(param_2 + 0x1e48);
  *(undefined4 *)(param_1 + 0x1e3c) = *(undefined4 *)(param_2 + 0x1e3c);
  *(undefined4 *)(param_1 + 0x1e40) = uVar1;
  *(undefined4 *)(param_1 + 0x1e44) = uVar2;
  *(short *)(param_1 + 0x1e48) = (short)uVar3;
  uVar1 = *(undefined4 *)(param_2 + 0x1e60);
  *(undefined4 *)(param_1 + 0x1e4c) = *(undefined4 *)(param_2 + 0x1e4c);
  *(undefined4 *)(param_1 + 0x1e50) = *(undefined4 *)(param_2 + 0x1e50);
  *(undefined4 *)(param_1 + 0x1e54) = *(undefined4 *)(param_2 + 0x1e54);
  *(undefined4 *)(param_1 + 0x1e58) = *(undefined4 *)(param_2 + 0x1e58);
  *(undefined4 *)(param_1 + 0x1e5c) = *(undefined4 *)(param_2 + 0x1e5c);
  *(undefined4 *)(param_1 + 0x1e60) = uVar1;
  *(undefined4 *)(param_1 + 0x1e64) = *(undefined4 *)(param_2 + 0x1e64);
  *(undefined4 *)(param_1 + 0x1e68) = *(undefined4 *)(param_2 + 0x1e68);
  FUN_439c5320(param_1 + 0x1e6c,param_2 + 0x1e6c,0x1a4);
  return param_1;
}


/* 43ae8d56 */

void FUN_43ae8d56(int param_1,int *param_2)

{
  int iVar1;
  
  param_2[1] = param_1 + 0x560;
  *param_2 = param_1;
  param_2[2] = param_1 + 0x5a4;
  param_2[3] = param_1 + 0x1290;
  param_2[4] = param_1 + 0x1730;
  param_2[6] = param_1 + 0x18d4;
  param_2[5] = param_1 + 0x1990;
  param_2[7] = param_1 + 0x1ad0;
  param_2[8] = param_1 + 0x1ade;
  param_2[9] = param_1 + 0x1aec;
  param_2[10] = param_1 + 0x1bcc;
  param_2[0xb] = param_1 + 0x1d40;
  param_2[0xc] = param_1 + 0x1e3c;
  param_2[0x14] = param_1 + 0x1e6c;
  iVar1 = *(int *)(param_1 + 0x1e4c);
  param_2[0x1d] = param_1 + 0x1acc;
  param_2[0x1f] = param_1 + 0x1398;
  param_2[0x17] = param_1 + 0x172c;
  param_2[0x20] = param_1 + 0x1b18;
  param_2[0x22] = param_1 + 0x1750;
  param_2[0x19] = param_1 + 0x18cc;
  param_2[0x23] = param_1 + 0x1d3c;
  param_2[0x26] = param_1 + 0x18d1;
  param_2[0x15] = iVar1;
  param_2[0x1b] = param_1 + 0x1e1c;
  param_2[0x25] = param_1 + 0x18d0;
  param_2[0x27] = param_1 + 0x1e18;
  param_2[0x29] = param_1 + 0x197c;
  param_2[0x2b] = param_1 + 0x19e4;
  return;
}

