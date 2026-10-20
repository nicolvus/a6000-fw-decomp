/* S40: existing snapshot functions; read-only export. */

/* 43b00b48 */

undefined4 * FUN_43b00b48(undefined4 *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 0;
  param_1[0x15a] = 0;
  param_1[0x15b] = 0;
  *(undefined2 *)(param_1 + 0x15c) = 0;
  param_1[0x15d] = 0;
  *(undefined2 *)(param_1 + 0x15e) = 0;
  *(undefined2 *)((int)param_1 + 0x57a) = 0;
  *(undefined1 *)(param_1 + 0x15f) = 0;
  *(undefined1 *)((int)param_1 + 0x57d) = 0;
  *(undefined1 *)((int)param_1 + 0x57e) = 0;
  *(undefined2 *)(param_1 + 0x160) = 0;
  *(undefined2 *)((int)param_1 + 0x582) = 0;
  *(undefined1 *)(param_1 + 0x161) = 0;
  param_1[0x356] = 0;
  *(undefined2 *)(param_1 + 0x357) = 0;
  *(undefined1 *)(param_1 + 0x3a5) = 0;
  *(undefined1 *)((int)param_1 + 0xe95) = 0;
  param_1[0x3a8] = 0;
  *(undefined1 *)(param_1 + 0x3a9) = 0;
  param_1[0x3aa] = 0;
  puVar1 = param_1;
  iVar2 = 0;
  do {
    iVar3 = iVar2 + 2;
    puVar1[0x162] = 0;
    puVar1 = puVar1 + 1;
    *(undefined2 *)((int)param_1 + iVar2 + 0x5a8) = 0;
    iVar2 = iVar3;
  } while (iVar3 != 0x10);
  FUN_439c5a04(param_1 + 1,0,0x564);
  FUN_439c5a04(param_1 + 0x16e,0,0x10);
  FUN_439c5a04(param_1 + 0x172,0,0x94);
  FUN_439c5a04(param_1 + 0x197,0,0xc);
  FUN_439c5a04(param_1 + 0x19a,0,0x10);
  FUN_439c5a04(param_1 + 0x19e,0,0xc);
  FUN_439c5a04(param_1 + 0x1a1,0,0xc);
  FUN_439c5a04(param_1 + 0x1a4,0,0x24);
  FUN_439c5a04(param_1 + 0x1ad,0,0xc);
  FUN_439c5a04(param_1 + 0x358,0,0x54);
  FUN_439c5a04(param_1 + 0x36d,0,0x50);
  FUN_439c5a04(param_1 + 0x381,0,0x50);
  FUN_439c5a04(param_1 + 0x395,0,0x18);
  FUN_439c5a04(param_1 + 0x39b,0,0x14);
  FUN_439c5a04(param_1 + 0x3a0,0,0x14);
  param_1[0x3a7] = 0;
  param_1[0x3a6] = 0;
  FUN_439c5a04(param_1 + 0x1b0,0,0x5e0);
  FUN_439c5a04(param_1 + 0x328,0,0x28);
  iVar2 = 0;
  do {
    iVar3 = iVar2 + 1;
    FUN_439c5a04(param_1 + iVar2 * 9 + 0x332,0);
    iVar2 = iVar3;
  } while (iVar3 != 4);
  return param_1;
}


/* 43b00cb4 */

undefined4 FUN_43b00cb4(int param_1)

{
  return *(undefined4 *)(param_1 + 0x568);
}


/* 43b00cba */

undefined1 FUN_43b00cba(int param_1)

{
  return *(undefined1 *)(param_1 + 0x57c);
}


/* 43b00cc0 */

undefined1 FUN_43b00cc0(int param_1)

{
  undefined1 uVar1;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    uVar1 = *(undefined1 *)(param_1 + 0x584);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
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


/* 43b00d06 */

void FUN_43b00d06(int param_1,undefined4 param_2)

{
  thunk_FUN_439c5320(param_2,param_1 + 8,0x560);
  return;
}


/* 43b00d1a */

void FUN_43b00d1a(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  switch(*(undefined4 *)(param_2 + 4)) {
  case 0:
    iVar1 = 0x5c0;
    break;
  case 1:
    thunk_FUN_439c5320(param_1 + 0x5d0,param_2 + 8,0x8c);
    return;
  case 2:
    *(undefined4 *)(param_1 + 0x664) = *(undefined4 *)(param_2 + 8);
    return;
  case 3:
    iVar1 = 0x670;
    break;
  default:
    return;
  case 5:
    *(undefined4 *)(param_1 + 0x68c) = *(undefined4 *)(param_2 + 8);
    return;
  case 6:
    uVar2 = *(undefined4 *)(param_2 + 0xc);
    uVar3 = *(undefined4 *)(param_2 + 0x10);
    uVar4 = *(undefined4 *)(param_2 + 0x14);
    *(undefined4 *)(param_1 + 0x698) = *(undefined4 *)(param_2 + 8);
    *(undefined4 *)(param_1 + 0x69c) = uVar2;
    *(undefined4 *)(param_1 + 0x6a0) = uVar3;
    *(undefined4 *)(param_1 + 0x6a4) = uVar4;
    uVar2 = *(undefined4 *)(param_2 + 0x1c);
    uVar3 = *(undefined4 *)(param_2 + 0x20);
    *(undefined4 *)(param_1 + 0x6a8) = *(undefined4 *)(param_2 + 0x18);
    *(undefined4 *)(param_1 + 0x6ac) = uVar2;
    *(undefined4 *)(param_1 + 0x6b0) = uVar3;
    return;
  }
  uVar2 = *(undefined4 *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + iVar1) = *(undefined4 *)(param_2 + 8);
  ((undefined4 *)(param_1 + iVar1))[1] = uVar2;
  return;
}


/* 43b00d78 */

void FUN_43b00d78(int param_1,int param_2)

{
  if (*(int *)(param_2 + 4) != 4) {
    if (*(int *)(param_2 + 4) == 7) {
      *(undefined4 *)(param_1 + 0x6bc) = *(undefined4 *)(param_2 + 8);
    }
    return;
  }
  *(undefined4 *)(param_1 + 0x680) = *(undefined4 *)(param_2 + 8);
  return;
}


/* 43b00d94 */

void FUN_43b00d94(int param_1,undefined4 param_2)

{
  thunk_FUN_439c5320(param_1 + 0xd64,param_2,0x50);
  return;
}


/* 43b00da0 */

void FUN_43b00da0(int param_1,undefined4 param_2)

{
  thunk_FUN_439c5320(param_1 + 0xdb4,param_2,0x50);
  return;
}


/* 43b00dac */

void FUN_43b00dac(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = param_2[1];
  uVar2 = param_2[2];
  uVar3 = param_2[3];
  *(undefined4 *)(param_1 + 0xe58) = *param_2;
  *(undefined4 *)(param_1 + 0xe5c) = uVar1;
  *(undefined4 *)(param_1 + 0xe60) = uVar2;
  *(undefined4 *)(param_1 + 0xe64) = uVar3;
  *(undefined4 *)(param_1 + 0xe68) = param_2[4];
  return;
}


/* 43b00dc0 */

void FUN_43b00dc0(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = param_2[1];
  uVar2 = param_2[2];
  uVar3 = param_2[3];
  *(undefined4 *)(param_1 + 0xe6c) = *param_2;
  *(undefined4 *)(param_1 + 0xe70) = uVar1;
  *(undefined4 *)(param_1 + 0xe74) = uVar2;
  *(undefined4 *)(param_1 + 0xe78) = uVar3;
  *(undefined4 *)(param_1 + 0xe7c) = param_2[4];
  return;
}


/* 43b00dd4 */

void FUN_43b00dd4(int param_1)

{
  if (*(char *)(param_1 + 0x57c) != '\0') {
    FUN_43b00da0(param_1,param_1 + 0xd64);
    FUN_43b00dc0(param_1,param_1 + 0xe58);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00d94(param_1,param_1 + 0xe04);
      thunk_FUN_439c5320(param_1 + 0xc4c,param_1 + 0xd60,0x54);
      return;
    }
    if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00dac(param_1,param_1 + 0xe80);
      *(undefined4 *)(param_1 + 0xcb0) = *(undefined4 *)(param_1 + 0xe54);
      *(undefined4 *)(param_1 + 0xcb4) = *(undefined4 *)(param_1 + 0xe58);
      *(undefined4 *)(param_1 + 0xcb8) = *(undefined4 *)(param_1 + 0xe5c);
      *(undefined4 *)(param_1 + 0xcbc) = *(undefined4 *)(param_1 + 0xe60);
      *(undefined4 *)(param_1 + 0xcc0) = *(undefined4 *)(param_1 + 0xe64);
      *(undefined4 *)(param_1 + 0xcc4) = *(undefined4 *)(param_1 + 0xe68);
    }
  }
  return;
}


/* 43b00e40 */

void FUN_43b00e40(int param_1,int param_2)

{
  *(undefined1 *)(param_1 + 0xea4) = *(undefined1 *)(*(int *)(param_2 + 0x50) + 0x4c);
  return;
}


/* 43b00e4c */

void FUN_43b00e4c(int param_1,int param_2,undefined4 *param_3)

{
  if (*(int *)(*(int *)(param_2 + 4) + 0xc) == 0) {
    *param_3 = *(undefined4 *)(param_1 + 0xd1c);
  }
  return;
}


/* 43b00e5a */

byte FUN_43b00e5a(int param_1)

{
  int iVar1;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    iVar1 = FUN_43ae8488();
    return *(byte *)(iVar1 + 2) ^ 1;
  }
  return 1;
}


/* 43b00e74 */

void FUN_43b00e74(int param_1,int param_2)

{
  short sVar1;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + (param_2 + 0x2d4) * 2) = sVar1;
  }
  return;
}


/* 43b00e9a */

void FUN_43b00e9a(int param_1,int param_2)

{
  short sVar1;
  
  if (*(int *)(param_1 + 0x568) == 2) {
    FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + (param_2 + 0x2d4) * 2) = sVar1;
  }
  return;
}


/* 43b00ec0 */

void FUN_43b00ec0(int param_1)

{
  FUN_43b00cb4();
  *(short *)(param_1 + 0x57a) = *(short *)(param_1 + 0x57a) + 1;
  return;
}


/* 43b00ed4 */

undefined4 FUN_43b00ed4(void)

{
  return 1;
}


/* 43b00ed8 */

uint FUN_43b00ed8(uint param_1,int param_2)

{
  ushort uVar1;
  short sVar2;
  undefined1 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  undefined1 uStack_c;
  undefined1 auStack_b [3];
  
  if (*(int *)(param_1 + 0x568) == 1) {
    uVar5 = *(ushort *)(*(int *)(param_2 + 8) + 0x26c) - 0x120;
    sVar2 = (short)uVar5;
    uVar4 = uVar5 & 0xffff;
    if ((0xe < uVar4) || (uVar5 = 0, (1 << ((int)sVar2 & 0xffU) & 0x7f9bU) == 0)) {
      if ((*(int *)(param_1 + 0x568) == 1) &&
         ((*(int *)(param_1 + 0x56c) == 0 &&
          ((*(byte *)(*(int *)(DAT_438063f8 + 0x438063a6 + DAT_438063fc) + 0x47) & 1) == 0)))) {
        *(undefined4 *)(param_1 + 0x56c) = 1;
        auStack_b = SUB43(uVar5 >> 8,0);
        _uStack_c = CONCAT31(auStack_b,9);
        uVar4 = param_1;
        uVar3 = FUN_43b00cb4();
        uVar1 = *(ushort *)(param_1 + 0x57a);
        iVar6 = uVar1 + 1;
        *(short *)(param_1 + 0x57a) = (short)iVar6;
        _uStack_c = CONCAT11(uVar3,uStack_c);
        _uStack_c = CONCAT22(uVar1,_uStack_c);
        uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
        if (uVar4 == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 0;
          return 0;
        }
        return uVar4;
      }
      return 1;
    }
  }
  else {
    uVar4 = param_1;
    if ((*(int *)(param_1 + 0x568) == 2) && (1 < *(ushort *)(*(int *)(param_2 + 8) + 0x224) - 0x125)
       ) {
      if ((*(int *)(param_1 + 0x568) == 2) && (*(int *)(param_1 + 0x56c) == 0)) {
        if ((*(byte *)(*(int *)(DAT_43806390 + 0x4380633a + DAT_43806394) + 0x47) & 1) == 0) {
          *(undefined4 *)(param_1 + 0x56c) = 1;
          auStack_b = SUB43((uint)param_2 >> 8,0);
          _uStack_c = CONCAT31(auStack_b,9);
          uVar3 = FUN_43b00cb4();
          uVar1 = *(ushort *)(param_1 + 0x57a);
          iVar6 = uVar1 + 1;
          *(short *)(param_1 + 0x57a) = (short)iVar6;
          _uStack_c = CONCAT11(uVar3,uStack_c);
          _uStack_c = CONCAT22(uVar1,_uStack_c);
          uVar4 = FUN_438061c4(param_1,&uStack_c,4,iVar6,uVar4);
          if (uVar4 == 0) {
            *(undefined4 *)(param_1 + 0x56c) = 0;
          }
        }
        else {
          uVar4 = 1;
        }
      }
      else {
        uVar4 = 1;
      }
      return uVar4;
    }
  }
  return uVar4;
}


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


/* 43b00fa4 */

void FUN_43b00fa4(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 2) {
    *(undefined1 *)(param_1 + 0xe54) = 4;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 0xe56) = sVar1;
    *(short *)(param_1 + 0xd5c) = sVar1;
    *(undefined1 *)(param_1 + 0xe55) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 0xe54,0x18);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0xd58) = 0;
    }
  }
  return;
}


/* 43b00fe6 */

void FUN_43b00fe6(int param_1)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x568) == 1) {
    *(undefined1 *)(param_1 + 0xd60) = 4;
    uVar2 = FUN_43b00cb4();
    sVar1 = *(short *)(param_1 + 0x57a);
    *(short *)(param_1 + 0x57a) = sVar1 + 1;
    *(short *)(param_1 + 0xd62) = sVar1;
    *(short *)(param_1 + 0xd5c) = sVar1;
    *(undefined1 *)(param_1 + 0xd61) = uVar2;
    iVar3 = FUN_43806400(param_1,param_1 + 0xd60,0x54);
    if (iVar3 == 0) {
      *(undefined4 *)(param_1 + 0xd58) = 0;
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


/* 43b0105e */

int FUN_43b0105e(int param_1)

{
  FUN_43806ed0(param_1 + 0x44);
  FUN_43806eb0(param_1 + 0x1c);
  return param_1;
}


/* 43b01076 */

int FUN_43b01076(int param_1)

{
  FUN_43806fb4();
  FUN_43808970(param_1 + 0xc);
  FUN_43b01944(param_1 + 0x30);
  FUN_438070a0(param_1 + 0xa0);
  FUN_438072bc(param_1 + 0xb8);
  FUN_43807bf8(param_1 + 0xe4);
  FUN_43809b7c(param_1 + 0x10c);
  FUN_43809f3c(param_1 + 0x13c);
  FUN_4380a050(param_1 + 0x144);
  FUN_4380a2d8(param_1 + 0x14c);
  FUN_4380a4e8(param_1 + 0x154);
  FUN_43806f50(param_1 + 0x158);
  FUN_43806f50(param_1 + 0x27c);
  FUN_4380860c(param_1 + 0x3a0);
  return param_1;
}

