/* S41: read-only exports. */

/* 436d5cdc */

undefined4 FUN_436d5cdc(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 uStack_18;
  undefined1 uStack_14;
  undefined3 uStack_13;
  
  if (*(int *)(param_1 + 0x10) == param_1 + 0x28) {
    uVar2 = 0;
  }
  else {
    uVar3 = param_4 & 0x80 | *(byte *)(param_1 + 0xa8) & 3 | (*(byte *)(param_1 + 0xa9) & 1) << 2 |
            (*(byte *)(param_1 + 0xaa) & 1) << 3 | (*(byte *)(param_1 + 0xab) & 7) << 4;
    _uStack_14 = CONCAT31((int3)(param_4 >> 8),(char)uVar3);
    uStack_18 = param_3;
    FUN_436d5e58(&uStack_14,*(undefined4 *)(param_1 + 4),(uint)*(byte *)(param_1 + 0xab),uVar3,
                 param_1,param_2);
    FUN_436d5eb0(*(undefined1 *)(param_1 + 0xac),*(undefined4 *)(param_1 + 4));
    FUN_436d5ed0(param_1 + 0x28,*(undefined1 *)(param_1 + 0x14),*(undefined4 *)(param_1 + 4));
    iVar1 = FUN_43560de0(0x18,*(undefined4 *)(param_1 + 8),1,&uStack_18,1);
    if (iVar1 != 0) {
      FUN_436d5ac8(0xbc,0,1,DAT_436d5d94 + 0x436d5d54,iVar1,uStack_18);
      FUN_43902718(DAT_436d5d98 + 0x436d5d60,iVar1,uStack_18);
    }
    FUN_43560dc4(0x18,~*(uint *)(param_1 + 8));
    FUN_43ad8c80(*(undefined4 *)(param_1 + 4));
    FUN_436d594c(param_1,*(undefined4 *)(param_1 + 4));
    FUN_436d5f60(*(undefined1 *)(param_1 + 0xab),*(undefined4 *)(param_1 + 4));
    FUN_43ad8d8c(param_1);
    uVar2 = 1;
  }
  return uVar2;
}


/* 436d5e58 */

void FUN_436d5e58(byte *param_1,int param_2)

{
  uint *puVar1;
  int iVar2;
  uint *puVar3;
  
  iVar2 = *(int *)(DAT_436d5ea8 + 0x436d5e60 + DAT_436d5eac);
  puVar3 = *(uint **)(iVar2 + param_2 * 0xc);
  puVar1 = *(uint **)(iVar2 + param_2 * 0xc + 4);
  puVar3[3] = puVar3[3] & 0xffffff00;
  *puVar1 = *param_1 & 3;
  puVar1[2] = (*param_1 & 7) >> 2;
  puVar3[1] = puVar3[1] & 0xfffffffe | (*param_1 & 0xf) >> 3;
  puVar3[2] = puVar3[2] & 0xfffffff8 | (*param_1 & 0x7f) >> 4;
  *puVar3 = *puVar3 | 1;
  return;
}


/* 436d5eb0 */

void FUN_436d5eb0(uint param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(*(int *)(DAT_436d5ec8 + 0x436d5eb8 + DAT_436d5ecc) + param_2 * 0xc);
  *(uint *)(iVar1 + 0xc) = *(uint *)(iVar1 + 0xc) & 0xffffff00 | param_1 & 0xff;
  return;
}


/* 436d5ed0 */

void FUN_436d5ed0(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = *(int *)(*(int *)(DAT_436d5ef8 + 0x436d5ed8 + DAT_436d5efc) + param_3 * 0xc);
  for (iVar2 = 0; iVar2 < param_2; iVar2 = iVar2 + 1) {
    *(uint *)(iVar1 + (iVar2 + 0x10) * 4) = (uint)*(byte *)(param_1 + iVar2);
  }
  return;
}


/* 436d5f60 */

void FUN_436d5f60(undefined4 param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_2 * 0xc + *(int *)(DAT_436d5f7c + 0x436d5f68 + DAT_436d5f80) + 4);
  *(undefined4 *)(iVar1 + 8) = 1;
  *(undefined4 *)(iVar1 + 8) = 0;
  *(undefined4 *)(iVar1 + 8) = 1;
  return;
}


/* 43ad8d8c */

void FUN_43ad8d8c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (*(char *)(param_1 + 0xad) != '\0') {
    uVar3 = 0;
    do {
      uVar2 = uVar3 & 0xff;
      iVar1 = uVar3 * 0x10;
      uVar3 = uVar3 + 1;
      FUN_436d5c0c(param_1,uVar2,*(undefined1 *)(param_1 + 0x14),param_1 + 0x28 + iVar1,param_4);
    } while (uVar3 != 8);
  }
  return;
}


/* 43ad8db2 */

void FUN_43ad8db2(int param_1)

{
  FUN_43ad8d38();
  FUN_436d5cdc(param_1);
  *(int *)(param_1 + 0x10) = param_1 + 0x28;
  *(undefined1 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined1 *)(param_1 + 0x15) = 0x81;
  *(undefined1 *)(param_1 + 0x20) = 1;
  *(undefined4 *)(param_1 + 0x24) = 1;
  return;
}


/* 43ad8fe0 */

byte FUN_43ad8fe0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = FUN_436d5d9c();
  if (iVar2 != 0) {
    bVar1 = FUN_43ad8fa2(param_1,param_2,param_3);
    return bVar1 ^ 1;
  }
  return 2;
}


/* 43ad8e4a */

void FUN_43ad8e4a(undefined4 *param_1,undefined4 param_2)

{
  *param_1 = param_2;
  return;
}


/* 436d5b74 */

void FUN_436d5b74(int param_1,char *param_2)

{
  if (*param_2 != '\x02') {
    FUN_436d5ac8(0xbc,0,1,DAT_436d5bc4 + 0x436d5b8c);
    FUN_43902718(DAT_436d5bc8 + 0x436d5b94);
    return;
  }
  FUN_43560dc4(0x18,~*(uint *)(param_1 + 0xc));
  FUN_43560da8(0x18,*(undefined4 *)(param_1 + 8));
  FUN_439c5320(param_1 + 0xa8,param_2,5);
  *(int *)(param_1 + 0x10) = param_1 + 0x28;
  *(undefined1 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined1 *)(param_1 + 0x15) = 0x81;
  *(undefined1 *)(param_1 + 0x20) = 1;
  *(undefined4 *)(param_1 + 0x24) = 1;
  return;
}

