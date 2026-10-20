/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43ad6980" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_43ad6980(void)

{
  FUN_436cfd20(2);
  _DAT_fc01f010 = 0x200000;
  return;
}


/* query "43ad6a96" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_43ad6a96(void)

{
  FUN_436cfd20(0);
  _DAT_fc01f014 = 0x200000;
  return;
}


/* query "43ad6e42" */

undefined4 FUN_43ad6e42(undefined4 *param_1)

{
  return *param_1;
}


/* query "436d30c8" */

uint FUN_436d30c8(int param_1)

{
  return *(uint *)(param_1 + 0xa1610) & 1;
}


/* query "436d3284" */

uint FUN_436d3284(int param_1)

{
  return *(uint *)(param_1 + 0xa1710) & 1;
}


/* query "436d26c4" */

uint FUN_436d26c4(int param_1)

{
  return *(uint *)(param_1 + 0xa1210) & 1;
}


/* query "436d23c0" */

uint FUN_436d23c0(int param_1)

{
  return *(uint *)(param_1 + 0xa1310) & 1;
}


/* query "436c85a8" */

void FUN_436c85a8(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = FUN_43ad3ec2(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_1 + (param_3 + 0x6c) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 1) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x30c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 8) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x324;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x10) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x7b) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x20) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x7e) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x40) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x72) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x200) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x78) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 2) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_3 * 0xc + param_1 + 0x33c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x400) == 0)) {
      FUN_43acee66(iVar5,uVar2);
      uVar3 = FUN_43ad3ec2(param_2);
      FUN_43ad42b2(iVar5,uVar3);
    }
    iVar5 = param_1 + (param_3 + 0x75) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x100) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x2f4;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x800) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x6f) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 4) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x2dc;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x80) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  iVar1 = FUN_43ad3ec6(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_1 + param_3 * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x20000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 3) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x40000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 6) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x80000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 9) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x10000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  iVar1 = FUN_43ad3eca(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_3 * 0xc + param_1 + 0x60;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x100000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
      FUN_43ad429e(iVar5,param_2);
    }
  }
  iVar1 = FUN_43ad3ece(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_1 + param_3 * 8 + 0x114;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x200000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  iVar1 = FUN_43ad3ed2(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_1 + param_3 * 8 + 0x84;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x4000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0xfc;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x8000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x9c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x10000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0xb4;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x20000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0xcc;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x1000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0xe4;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + param_3 * 4 + 0x4a4) & 0x2000000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  iVar1 = FUN_43ad3ed6(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_1 + (param_3 + 0x87) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x10) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x84) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 8) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x81) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 4) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x8d) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 2) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + (param_3 + 0x8a) * 8;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 1) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  iVar1 = FUN_43ad3eda(param_2);
  if (iVar1 != 0) {
    if (param_3 == 2) {
      uVar2 = 0xf3200000;
    }
    else {
      uVar2 = FUN_43acee62(iVar1 + 4);
    }
    iVar5 = param_3 * 0x38 + param_1 + 0x1bc;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x4000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x144;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x100) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x174;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x800) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x18c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x400) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x294;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x1000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x15c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x80000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x2c4;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x40000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 300;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x2000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x264;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x200) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x27c;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x10000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x1a4;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x8000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
    iVar5 = param_1 + param_3 * 8 + 0x2ac;
    uVar3 = FUN_43acee62(iVar5);
    iVar1 = FUN_43ad4ab8(param_1,uVar3);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + (param_3 + 300) * 4) & 0x20000) == 0)) {
      FUN_43acee66(iVar5,uVar2);
    }
  }
  if (((param_3 == 2) && (uVar4 = FUN_43ad3ebe(param_2), uVar4 < 0x17)) &&
     ((1 << (uVar4 & 0xff) & 0x700400U) != 0)) {
    uVar2 = FUN_43acee62(param_1 + 0x480);
    iVar1 = FUN_43ad4ab8(param_1,uVar2);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + 0x4b8) & 0x8000000) == 0)) {
      FUN_43acee66(param_1 + 0x480,0xf300c000);
    }
    uVar2 = FUN_43acee62(param_1 + 0x488);
    iVar1 = FUN_43ad4ab8(param_1,uVar2);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + 0x4b8) & 0x2000000) == 0)) {
      FUN_43acee66(param_1 + 0x488,0xf300d1c0);
    }
    uVar2 = FUN_43acee62(param_1 + 0x490);
    iVar1 = FUN_43ad4ab8(param_1,uVar2);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + 0x4b8) & 0x4000000) == 0)) {
      FUN_43acee66(param_1 + 0x490,0xf300c9d0);
    }
    uVar2 = FUN_43acee62(param_1 + 0x498);
    iVar1 = FUN_43ad4ab8(param_1,uVar2);
    if ((iVar1 == 0) && ((*(uint *)(param_1 + 0x4b8) & 0x1000000) == 0)) {
      FUN_43acee66(param_1 + 0x498,0xf3020f38);
      return;
    }
  }
  return;
}


/* query "43ae76fe" */

void FUN_43ae76fe(int param_1,undefined2 param_2,uint param_3,undefined2 *param_4,
                 undefined2 *param_5,undefined2 *param_6)

{
  undefined1 uVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  undefined1 auStack_38 [8];
  int iStack_30;
  byte bStack_2a;
  byte abStack_29 [5];
  
  abStack_29[0] = 0;
  bStack_2a = 0;
  FUN_43ae80c2(param_3,abStack_29,&bStack_2a);
  FUN_43787064(abStack_29[0],bStack_2a,param_1 + 0x5332);
  FUN_43901a8c(7,param_2,
               (uint)*(ushort *)(param_1 + 0x1d8) | *(int *)(param_1 + 0x4b68) << 0x18 |
               (uint)*(byte *)(param_1 + 0x4b97) << 0x10,
               (uint)*(ushort *)(param_1 + 0x4b64) | *(int *)(param_1 + 0x1e0) << 0x10);
  FUN_43901a8c(7,0,(uint)*(ushort *)(param_1 + 0x1d8) | *(int *)(param_1 + 0x4b68) << 0x18 |
                   (uint)*(byte *)(param_1 + 0x4b97) << 0x10,
               (uint)bStack_2a << 0x10 | (uint)abStack_29[0] << 0x18 |
               (uint)*(byte *)(param_1 + 0x5333) | (uint)*(byte *)(param_1 + 0x5332) << 8);
  FUN_43901a8c(7,1,CONCAT22(*param_4,param_4[1]),0);
  FUN_43901a8c(7,2,CONCAT22(param_4[2],param_4[3]),CONCAT22(param_4[4],param_4[5]));
  FUN_43901a8c(7,5,CONCAT22(*param_6,param_6[1]),CONCAT22(param_6[2],param_6[3]));
  FUN_43901a8c(7,6,CONCAT22(param_6[4],param_6[5]),CONCAT22(param_6[6],param_6[7]));
  FUN_43901a8c(7,3,CONCAT22(*param_5,param_5[1]),0);
  FUN_43901a8c(7,4,CONCAT22(param_5[2],param_5[3]),CONCAT22(param_5[4],param_5[5]));
  iVar2 = FUN_43ae9226(*(undefined4 *)(param_1 + 0x4a7c),0x9400,auStack_38);
  if (iVar2 == 0) {
    iVar2 = FUN_43ae7c20(param_1);
    bVar4 = *(byte *)(iStack_30 + 0xba) >> 4;
    bVar3 = *(byte *)(iStack_30 + 0xba) & 0xf;
    uVar1 = (undefined1)param_2;
    if ((param_3 & 3) != 0) {
      bVar4 = bVar4 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xbb) = uVar1;
    }
    if ((param_3 & 0x30000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xc1) = uVar1;
    }
    *(byte *)(iStack_30 + 0xba) = bVar3 & 0xf | bVar4 << 4;
    bVar4 = *(byte *)(iStack_30 + 199) >> 4;
    bVar3 = *(byte *)(iStack_30 + 199) & 0xf;
    if ((param_3 & 4) != 0) {
      bVar4 = bVar4 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 200) = uVar1;
    }
    if ((param_3 & 0x40000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xce) = uVar1;
    }
    *(byte *)(iStack_30 + 199) = bVar3 & 0xf | bVar4 << 4;
    bVar4 = *(byte *)(iStack_30 + 0xd4) >> 4;
    bVar3 = *(byte *)(iStack_30 + 0xd4) & 0xf;
    if ((param_3 & 8) != 0) {
      bVar4 = bVar4 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xd5) = uVar1;
    }
    if ((param_3 & 0x80000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xdb) = uVar1;
    }
    *(byte *)(iStack_30 + 0xd4) = bVar3 & 0xf | bVar4 << 4;
    bVar4 = *(byte *)(iStack_30 + 0xe1) >> 4;
    bVar3 = *(byte *)(iStack_30 + 0xe1) & 0xf;
    if ((param_3 & 0x10) != 0) {
      bVar4 = bVar4 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xe2) = uVar1;
    }
    if ((param_3 & 0x100000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xe8) = uVar1;
    }
    *(byte *)(iStack_30 + 0xe1) = bVar3 & 0xf | bVar4 << 4;
    bVar4 = *(byte *)(iStack_30 + 0xee) >> 4;
    bVar3 = *(byte *)(iStack_30 + 0xee) & 0xf;
    if ((param_3 & 0x20) != 0) {
      bVar4 = bVar4 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xef) = uVar1;
    }
    if ((param_3 & 0x200000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xf5) = uVar1;
    }
    *(byte *)(iStack_30 + 0xee) = bVar3 & 0xf | bVar4 << 4;
    bVar4 = *(byte *)(iStack_30 + 0xfb);
    bVar3 = bVar4 & 0xf;
    if ((param_3 & 0x40) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0xfc) = uVar1;
    }
    if ((param_3 & 0x400000) != 0) {
      bVar3 = bVar3 + 1;
      *(undefined1 *)(iStack_30 + iVar2 + 0x102) = uVar1;
    }
    *(byte *)(iStack_30 + 0xfb) = bVar3 & 0xf | bVar4 & 0xf0;
  }
  return;
}


/* query "43ae80c2" */

void FUN_43ae80c2(uint param_1,byte *param_2,byte *param_3)

{
  byte bVar1;
  byte bVar2;
  
  if ((param_1 & 3) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(1);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 4) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(4);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 8) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(8);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 0x10) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(0x10);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 0x20) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(0x20);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 0x40) != 0) {
    bVar1 = *param_2;
    bVar2 = FUN_43786fc0(0x40);
    *param_2 = bVar2 | bVar1;
  }
  if ((param_1 & 0x30000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x10000);
    *param_3 = bVar2 | bVar1;
  }
  if ((param_1 & 0x40000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x40000);
    *param_3 = bVar2 | bVar1;
  }
  if ((param_1 & 0x80000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x80000);
    *param_3 = bVar2 | bVar1;
  }
  if ((param_1 & 0x100000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x100000);
    *param_3 = bVar2 | bVar1;
  }
  if ((param_1 & 0x200000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x200000);
    *param_3 = bVar2 | bVar1;
  }
  if ((param_1 & 0x400000) != 0) {
    bVar1 = *param_3;
    bVar2 = FUN_43786fc0(0x400000);
    *param_3 = bVar2 | bVar1;
  }
  return;
}


/* query "43ae81f4" */

bool FUN_43ae81f4(uint param_1)

{
  uint uVar1;
  
  uVar1 = FUN_43786fc0(0x200000);
  return (uVar1 & (param_1 & 0xffff) >> 8) != 0;
}


/* query "436d7356" */

int * FUN_436d72e8(int *param_1,int param_2)

{
  FUN_436d93d0();
  *param_1 = DAT_44026d1c + 8;
  FUN_43ad8cb2(param_1 + 0xa6,0,0x10,8,*(undefined4 *)(&DAT_43bc16d4 + param_2 * 4));
  FUN_436d8774(param_1 + 0xd4,0xd,DAT_44020c64,DAT_44026804,DAT_4401ff00,DAT_4401f630,DAT_44024e50,
               &DAT_43bc2044,&DAT_43bdbd78,&DAT_43bc1c20,&DAT_43bc16dc,&DAT_43bc1ae8,&DAT_43bc1b84,
               &DAT_43bc1d58,&DAT_43bdbe70,DAT_440206d0,DAT_4402656c,&DAT_43bc1604);
  *(undefined2 *)(param_1 + 0x6d) = 0x36;
  *(undefined2 *)(param_1 + 0x78) = 0x1f;
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
  param_1[0x79] = 54000000;
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


/* query "43bc1d40" */

/* query "43fcbf78" */

/* query "43fcbe68" */
