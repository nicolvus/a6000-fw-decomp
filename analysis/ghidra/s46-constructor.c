/* S41: read-only exports. */

/* 436c414c */

undefined4 * FUN_436c414c(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = DAT_436c4164;
  FUN_43ace32e(param_1 + 1);
  *param_1 = *(undefined4 *)(iVar1 + 0x436c415e + DAT_436c4168);
  return param_1;
}


/* 43ace32e */

int FUN_43ace32e(int param_1)

{
  FUN_43ace31c(param_1,param_1 + 0xc,8);
  return param_1;
}


/* 436c6f3c */

void FUN_436c6f3c(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar2 = param_1 + 0xe9c;
  uVar3 = param_2;
  uVar4 = param_3;
  FUN_436c68a8(iVar2);
  iVar1 = param_1 + 0x6bc;
  FUN_436c68c4(param_1 + 0xeac);
  FUN_436c7950(param_1 + 0xe10,DAT_436c71f8,iVar2,param_2,param_3,uVar3,uVar4);
  FUN_436c7b3c(param_1 + 0xec0,param_2);
  FUN_436c5d2c(param_1,DAT_436c71f8,iVar2,param_2,0);
  FUN_43ad08ca(param_1 + 0xb8,0xf3000000,iVar1);
  FUN_436c5288(param_1 + 0x200,0xf3000000,iVar1);
  FUN_43acf71c(param_1 + 0x288,0xf3000000,iVar1);
  FUN_43acfa3a(param_1 + 0x2fc,0xf3000000,iVar1);
  FUN_43ad1964(param_1 + 0x380,0xf3000000,iVar1);
  FUN_43ad299c(param_1 + 0x3f0,0xf3000000,iVar1);
  FUN_43acff8c(param_1 + 0x460,0xf3000000,iVar1);
  FUN_43ad23d6(param_1 + 0x524,0xf3000000);
  FUN_43ad23be(param_1 + 0x544,0xf3000000);
  FUN_43ad23be(param_1 + 0x564,0xf3000000);
  FUN_43acf0cc(param_1 + 0x584,0xf3000000,0,param_1 + 0x524);
  FUN_43acf0cc(param_1 + 0x5b4,0xf3000000,1,0);
  FUN_43acf0cc(param_1 + 0x5e4,0xf3000000,2,0);
  FUN_43acf0cc(param_1 + 0x614,0xf3000000,3,param_1 + 0x544);
  FUN_43acf0cc(param_1 + 0x644,0xf3000000,4,param_1 + 0x564);
  FUN_43acf0cc(param_1 + 0x674,0xf3000000,5,0);
  FUN_43acee7a(param_1 + 0x6a4,0xf3000000);
  FUN_436c68e4(iVar1,0);
  FUN_436c6920(param_1 + 0x6d0,0);
  FUN_436c6970(param_1 + 0x6ec,0);
  iVar1 = param_1 + 0xdc4;
  FUN_436c5d2c(param_1 + 0x708,DAT_436c71fc,iVar2,param_2,1);
  FUN_43ad08ca(param_1 + 0x7c0,DAT_436c7200,iVar1);
  FUN_436c5288(param_1 + 0x908,DAT_436c7200,iVar1);
  FUN_43acf71c(param_1 + 0x990,DAT_436c7200,iVar1);
  FUN_43acfa3a(param_1 + 0xa04,DAT_436c7200,iVar1);
  FUN_43ad1964(param_1 + 0xa88,DAT_436c7200,iVar1);
  FUN_43ad299c(param_1 + 0xaf8,DAT_436c7200,iVar1);
  FUN_43acff8c(param_1 + 0xb68,DAT_436c7200,iVar1);
  FUN_43ad23d6(param_1 + 0xc2c,DAT_436c7200);
  FUN_43ad23be(param_1 + 0xc4c,DAT_436c7200);
  FUN_43ad23be(param_1 + 0xc6c,DAT_436c7200);
  FUN_43acf0cc(param_1 + 0xc8c,DAT_436c7200,6,param_1 + 0xc2c);
  FUN_43acf0cc(param_1 + 0xcbc,DAT_436c7200,7,0);
  FUN_43acf0cc(param_1 + 0xcec,DAT_436c7200,8,0);
  FUN_43acf0cc(param_1 + 0xd1c,DAT_436c7200,9,param_1 + 0xc4c);
  FUN_43acf0cc(param_1 + 0xd4c,DAT_436c7200,10,param_1 + 0xc6c);
  FUN_43acf0cc(param_1 + 0xd7c,DAT_436c7200,0xb,0);
  FUN_43acee7a(param_1 + 0xdac,DAT_436c7200);
  FUN_436c68e4(iVar1,1);
  FUN_436c6920(param_1 + 0xdd8,1);
  FUN_436c6970(param_1 + 0xdf4,1);
  return;
}


/* 43ad37c8 */

int FUN_43ad37c8(int param_1)

{
  FUN_43ad35ee();
  FUN_43ad35ee(param_1 + 0x708);
  FUN_436c6e64(param_1 + 0xe10);
  FUN_436c6ebc(param_1 + 0xe9c);
  FUN_436c6edc(param_1 + 0xeac);
  FUN_436c6efc(param_1 + 0xec0);
  return param_1;
}


/* 436c416c */

int FUN_436c416c(void)

{
  uint *puVar1;
  
  puVar1 = (uint *)(DAT_436c418c + 0x436c4174);
  if ((*puVar1 & 1) == 0) {
    FUN_436c414c(DAT_436c4190 + 0x436c4180);
    *puVar1 = 1;
  }
  return (int)&DAT_436c418c + DAT_436c4194;
}


/* 43859944 */

void FUN_43859944(int param_1,int param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_438599d0 + 0x43859956;
  iVar3 = *(int *)(iVar4 + DAT_438599d4);
  if (*(char *)(iVar3 + 5) != '\x01') {
    *(int *)(DAT_438599d8 + 0x43859962) = param_1;
    if (param_2 != 0) {
      bVar1 = *(byte *)(iVar3 + 0xf);
      if ((bVar1 & 0x10) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599dc),param_2 + 700,0x6b0);
      }
      if ((bVar1 & 0x20) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e0),param_2 + 4,0x2b8);
      }
      if ((bVar1 & 0x40) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e4),param_2 + 0x96c,0x1128);
      }
    }
    if (param_3 != 0) {
      FUN_43afa660(DAT_438599e8 + 0x438599b6,param_3);
    }
    if (param_1 < 0x40) {
      uVar2 = 0x40;
    }
    else {
      uVar2 = 0x80;
    }
    FUN_43859710(uVar2);
    return;
  }
  return;
}

