/* S41: read-only exports. */

/* 43ae8eae */

void FUN_43ae8eae(undefined4 param_1,undefined4 param_2)

{
  FUN_43ae8d56();
  FUN_43ae8e2c(param_1,param_2);
  FUN_43ae8e44(param_1,param_2);
  FUN_43ae8e5c(param_1,param_2);
  FUN_43ae8e74(param_1,param_2);
  FUN_43ae8e84(param_1,param_2);
  FUN_43ae8e9a(param_1,param_2);
  FUN_43ae8ea4(param_1,param_2);
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


/* 436d6118 */

undefined4 FUN_436d6118(void)

{
  return *(undefined4 *)(DAT_436d6124 + 0x436d6120 + DAT_436d6128);
}


/* 43795dec */

void FUN_43795dec(undefined4 param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_24;
  undefined1 uStack_20;
  undefined2 uStack_1e;
  int iStack_1c;
  
  if (param_3 == 0) {
    uStack_24 = FUN_43ae9332(*(undefined4 *)(param_2 + 0x1c));
    uStack_1e = *(undefined2 *)(param_2 + 0x14);
    uStack_20 = 0;
    iStack_1c = param_3;
    iVar1 = FUN_43b04604(param_2,&uStack_24,0);
    if (iVar1 != 0) {
      FUN_43795c48(1,1,1,DAT_43795e54 + 0x43795e2c,iVar1);
      FUN_43902718(DAT_43795e58 + 0x43795e36,iVar1);
    }
  }
  uVar2 = FUN_436c2270();
  FUN_43ad3b92(uVar2,param_1,param_2,param_3,param_4,param_5);
  return;
}

