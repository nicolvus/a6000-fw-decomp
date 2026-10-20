/* S41: read-only exports. */

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


/* 436d5e04 */

void FUN_436d5e04(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_14;
  
  uStack_14 = param_2;
  FUN_43ad8e4a(&uStack_14,param_1,param_3,param_4,param_1);
  iVar1 = FUN_43ad8fe0(&uStack_14,param_2,param_3);
  if (iVar1 == 2) {
    FUN_43ad8db2(param_1);
    iVar1 = FUN_43ad8fe0(&uStack_14,param_2,param_3);
    if (iVar1 == 2) {
      FUN_436d5ac8(0xbc,0,1,DAT_436d5e50 + 0x436d5e42);
      FUN_43902718(DAT_436d5e54 + 0x436d5e4a);
    }
  }
  return;
}


/* 43ad8dca */

void FUN_43ad8dca(int param_1)

{
  FUN_43ad8d38();
  FUN_436d5cdc(param_1);
  FUN_43560da8(0x18,*(undefined4 *)(param_1 + 0xc));
  return;
}


/* 43ad9004 */

void candidate_43ad9004(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_14 = param_2;
  uStack_10 = param_3;
  FUN_43ad8e4a(&uStack_14,param_1,param_3,param_1,param_1);
  FUN_43ad8fe0(&uStack_14,param_2,param_3);
  return;
}


/* 43ad8de4 */

undefined4 candidate_43ad8de4(int param_1,byte *param_2)

{
  undefined4 uVar1;
  uint uVar2;
  undefined1 uStack_14;
  undefined3 uStack_13;
  
  if (*(int *)(param_1 + 0x10) == param_1 + 0x28) {
    uVar1 = 0;
  }
  else {
    uVar2 = (uint)param_2 & 0x80 | *param_2 & 3 | (param_2[1] & 1) << 2 | (param_2[2] & 1) << 3 |
            (param_2[3] & 7) << 4;
    _uStack_14 = CONCAT31((int3)((uint)param_2 >> 8),(char)uVar2);
    FUN_436d5e58(&uStack_14,*(undefined4 *)(param_1 + 4),(uint)param_2[3],uVar2,param_1);
    FUN_436d5eb0(param_2[4],*(undefined4 *)(param_1 + 4));
    FUN_436d5ed0(param_1 + 0x28,*(undefined1 *)(param_1 + 0x14),*(undefined4 *)(param_1 + 4));
    if (*param_2 == 2) {
      FUN_436d5f60(param_2[3],*(undefined4 *)(param_1 + 4));
    }
    FUN_43ad8d8c(param_1);
    uVar1 = 1;
  }
  return uVar1;
}


/* 43ad8d38 */

void FUN_43ad8d38(int param_1)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = *(byte **)(param_1 + 0x10);
  if (pbVar1 != (byte *)(param_1 + 0x28)) {
    if (*(char *)(param_1 + 0x20) == '\0') {
      *pbVar1 = *pbVar1 & 0xf;
      *(byte **)(param_1 + 0x10) = pbVar1 + 1;
      *(undefined1 *)(param_1 + 0x20) = 1;
    }
    **(char **)(param_1 + 0x1c) =
         ((char)*(undefined4 *)(param_1 + 0x10) + -1) - (char)*(char **)(param_1 + 0x1c);
    **(undefined1 **)(param_1 + 0x10) = 0;
    iVar2 = *(int *)(param_1 + 0x10) + 1;
    *(int *)(param_1 + 0x10) = iVar2;
    *(char *)(param_1 + 0x14) = (char)iVar2 - (char)(byte *)(param_1 + 0x28);
  }
  return;
}


/* 436d58f4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_436d58f4(int param_1)

{
  undefined2 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  if (param_1 == 1) {
    puVar2 = (undefined4 *)(_DAT_436d5940 + 0x436d5916);
  }
  else {
    if (param_1 != 2) {
      if (param_1 != 0) {
        iVar3 = _DAT_436d5948 + 0x436d592c;
        iVar4 = FUN_435612d0(DAT_436d58ec,&puStack_30,0x9a,0);
        puVar1 = puStack_30;
        if (iVar4 == 0) {
          puStack_30[1] = 0xbc;
          *puStack_30 = 1;
          *(undefined4 *)(puStack_30 + 2) = 0;
          *(undefined4 *)(puStack_30 + 4) = 0;
          *(undefined4 *)(puStack_30 + 6) = 0;
          puStack_30[8] = 3;
          FUN_439c5a04(auStack_50,0,0x20);
          auStack_50[0] = 0x20;
          FUN_43561244(DAT_436d58f0,auStack_50);
          *(undefined4 *)(puVar1 + 4) = uStack_38;
          *(undefined4 *)(puVar1 + 6) = uStack_34;
          iVar4 = FUN_439c5004(puVar1 + 10,0x81,iVar3,&stack0x00000000);
          if (iVar4 < 0) {
            FUN_435612ec(DAT_436d58ec,puStack_30);
          }
          else {
            if (0x7f < iVar4) {
              iVar4 = 0x80;
            }
            puVar1[9] = (short)iVar4 + 1;
            *(undefined1 *)((int)puVar1 + iVar4 + 0x14) = 10;
            *(undefined1 *)((int)puVar1 + iVar4 + 0x15) = 0;
            *(undefined4 *)(puStack_30 + -2) = DAT_436d58ec;
            FUN_4356120c();
          }
        }
        return;
      }
      *(undefined4 *)(_DAT_436d593c + 0x436d5908) = 0;
      FUN_43561110(0x26);
      goto LAB_436d5932;
    }
    puVar2 = (undefined4 *)(_DAT_436d5944 + 0x436d591c);
  }
  *puVar2 = 0;
LAB_436d5932:
  iVar4 = *(int *)(param_1 * 0xc + *(int *)(_DAT_436d5fa8 + 0x436d5f8c + _DAT_436d5fac) + 8);
  *(uint *)(iVar4 + 4) = *(uint *)(iVar4 + 4) | 1;
  *(uint *)(iVar4 + 8) = *(uint *)(iVar4 + 8) & 0xfffffffe;
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

