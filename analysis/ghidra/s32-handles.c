/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4390366c" */

int FUN_4390366c(undefined2 *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_88 [4];
  undefined2 uStack_84;
  byte bStack_80;
  undefined4 auStack_78 [25];
  
  iVar2 = FUN_43ae9674(param_2);
  if (iVar2 == 0) {
    iVar2 = -6;
    FUN_43902984(5,1,1,&DAT_43cceb98);
    FUN_43902718(s_MemoryHandle__AllocShare__DMM_UN_43cceba3);
  }
  else {
    iVar2 = FUN_43902df8(*(undefined4 *)(param_2 + 2),*param_2,param_3,auStack_88,param_4);
    if (iVar2 == 0) {
      *param_1 = uStack_84;
      *(undefined4 *)(param_1 + 2) = *(undefined4 *)(param_2 + 2);
      *(byte *)(param_1 + 1) = bStack_80;
      if (4 < bStack_80) {
        FUN_43902984(5,1,1,&DAT_43ccebcf,bStack_80,4);
        FUN_43902718(s_MemoryHandle__AllocShare__ERR_EX_43ccebda,*(undefined1 *)(param_1 + 1),4);
        *(undefined1 *)(param_1 + 1) = 4;
      }
      bVar1 = *(byte *)(param_1 + 1);
      puVar4 = auStack_78;
      puVar5 = param_1;
      for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
        *(undefined4 *)(puVar5 + 4) = *puVar4;
        *(undefined4 *)(puVar5 + 6) = puVar4[1];
        puVar5 = puVar5 + 4;
        puVar4 = puVar4 + 2;
      }
      *(undefined1 *)((int)param_1 + 3) = 1;
    }
  }
  return iVar2;
}


/* query "43b2a252" */

void FUN_43b2a252(undefined4 *param_1)

{
  FUN_43561604(*param_1);
  return;
}


/* query "43b2a258" */

undefined4 FUN_43b2a258(undefined2 *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_43ae9674();
  if ((iVar1 == 0) || (iVar1 = FUN_43b0662c(param_1), iVar1 == 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0;
    if (*(char *)((int)param_1 + 3) != '\0') {
      uVar2 = FUN_43903414(*param_1,param_2);
    }
    *(undefined1 *)(param_1 + 1) = 0;
    FUN_439c5a04(param_1 + 4,0,0x20);
  }
  return uVar2;
}


/* query "43903558" */

int FUN_43903558(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined2 param_5)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined2 *puVar5;
  undefined1 auStack_80 [4];
  undefined2 uStack_7c;
  byte bStack_78;
  undefined4 auStack_70 [24];
  
  iVar2 = FUN_43902a34(param_2,param_3,param_4,auStack_80,param_5);
  if (iVar2 == 0) {
    *(undefined4 *)(param_1 + 2) = param_2;
    *param_1 = uStack_7c;
    *(byte *)(param_1 + 1) = bStack_78;
    if (4 < bStack_78) {
      FUN_43902984(5,1,1,&DAT_43cceb07,bStack_78,4);
      FUN_43902718(s_MemoryHandle__AllocNew__ERR_EXTE_43cceb12,*(undefined1 *)(param_1 + 1),4);
      *(undefined1 *)(param_1 + 1) = 4;
    }
    bVar1 = *(byte *)(param_1 + 1);
    puVar4 = auStack_70;
    puVar5 = param_1;
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1) {
      *(undefined4 *)(puVar5 + 4) = *puVar4;
      *(undefined4 *)(puVar5 + 6) = puVar4[1];
      puVar5 = puVar5 + 4;
      puVar4 = puVar4 + 2;
    }
    *(undefined1 *)((int)param_1 + 3) = 1;
  }
  return iVar2;
}


/* query "43b2a296" */

undefined4 FUN_43b2a296(undefined2 *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_43ae9674();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    if (*(char *)((int)param_1 + 3) == '\0') {
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_43b0662c(param_1);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 2;
      }
      uVar2 = FUN_43902fbc(*param_1,uVar2,param_2);
    }
    FUN_43ae7542(param_1);
  }
  return uVar2;
}


/* query "43ae9674" */

bool FUN_43ae9674(short *param_1)

{
  return *param_1 != -1;
}


/* query "43a49ba4" */

undefined4 FUN_43a49ba4(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  if (*(int *)(param_1 + 0x18) == 0) {
    uVar1 = 0xfffffff0;
  }
  else {
    uStack_24 = *(undefined4 *)(param_1 + 0xc);
    uStack_20 = FUN_43a49b06(param_2);
    uStack_1c = FUN_43a49b0a(param_2);
    uStack_18 = FUN_43a49b0e(param_2);
    uStack_14 = FUN_43a49b12(param_2);
    uVar1 = FUN_43a49ca8(*(int *)(param_1 + 0x1c) + *(int *)(param_1 + 0x18),
                         *(undefined4 *)(param_1 + 0x20),&uStack_24);
  }
  return uVar1;
}


/* query "43a49986" */

undefined4 FUN_43a49986(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (param_2 == (undefined4 *)0x0) {
    uVar3 = 0xffffffeb;
    FUN_43a49eec(4,0,(undefined4 *)(param_1 + 0x18),param_1 + 8,0xffffffeb,
                 *(undefined4 *)(param_1 + 0x28));
  }
  else {
    uVar3 = *(undefined4 *)(param_1 + 0x1c);
    uVar1 = *(undefined4 *)(param_1 + 0x20);
    uVar2 = *(undefined4 *)(param_1 + 0x24);
    *param_2 = *(undefined4 *)(param_1 + 0x18);
    param_2[1] = uVar3;
    param_2[2] = uVar1;
    param_2[3] = uVar2;
    uVar3 = 0;
  }
  return uVar3;
}


/* query "43a49980" */

void FUN_43a49980(int param_1,undefined4 *param_2)

{
  *param_2 = *(undefined4 *)(param_1 + 0x28);
  return;
}

