/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814cc0" */

void FUN_43814c78(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  iVar2 = FUN_435612d0(0x8f0139,&puStack_30,0x9a,0);
  puVar1 = puStack_30;
  if (iVar2 == 0) {
    puStack_30[1] = param_1;
    *puStack_30 = 1;
    *(undefined4 *)(puStack_30 + 2) = param_2;
    *(undefined4 *)(puStack_30 + 4) = 0;
    *(undefined4 *)(puStack_30 + 6) = 0;
    puStack_30[8] = param_3;
    FUN_439c5a04(auStack_50,0,0x20);
    auStack_50[0] = 0x20;
    FUN_43561244(0x910042,auStack_50);
    *(undefined4 *)(puVar1 + 4) = uStack_38;
    *(undefined4 *)(puVar1 + 6) = uStack_34;
    iVar2 = FUN_439c5004(puVar1 + 10,0x81,param_4,&stack0x00000000);
    if (iVar2 < 0) {
      FUN_435612ec(0x8f0139,puStack_30);
    }
    else {
      if (0x7f < iVar2) {
        iVar2 = 0x80;
      }
      puVar1[9] = (short)iVar2 + 1;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x14) = 10;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x15) = 0;
      *(undefined4 *)(puStack_30 + -2) = 0x8f0139;
      FUN_4356120c();
    }
  }
  return;
}


/* query "43814cb0" */

void FUN_43814c78(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  iVar2 = FUN_435612d0(0x8f0139,&puStack_30,0x9a,0);
  puVar1 = puStack_30;
  if (iVar2 == 0) {
    puStack_30[1] = param_1;
    *puStack_30 = 1;
    *(undefined4 *)(puStack_30 + 2) = param_2;
    *(undefined4 *)(puStack_30 + 4) = 0;
    *(undefined4 *)(puStack_30 + 6) = 0;
    puStack_30[8] = param_3;
    FUN_439c5a04(auStack_50,0,0x20);
    auStack_50[0] = 0x20;
    FUN_43561244(0x910042,auStack_50);
    *(undefined4 *)(puVar1 + 4) = uStack_38;
    *(undefined4 *)(puVar1 + 6) = uStack_34;
    iVar2 = FUN_439c5004(puVar1 + 10,0x81,param_4,&stack0x00000000);
    if (iVar2 < 0) {
      FUN_435612ec(0x8f0139,puStack_30);
    }
    else {
      if (0x7f < iVar2) {
        iVar2 = 0x80;
      }
      puVar1[9] = (short)iVar2 + 1;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x14) = 10;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x15) = 0;
      *(undefined4 *)(puStack_30 + -2) = 0x8f0139;
      FUN_4356120c();
    }
  }
  return;
}


/* query "43814d00" */

void FUN_43814c78(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 auStack_50 [6];
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined2 *puStack_30;
  
  iVar2 = FUN_435612d0(0x8f0139,&puStack_30,0x9a,0);
  puVar1 = puStack_30;
  if (iVar2 == 0) {
    puStack_30[1] = param_1;
    *puStack_30 = 1;
    *(undefined4 *)(puStack_30 + 2) = param_2;
    *(undefined4 *)(puStack_30 + 4) = 0;
    *(undefined4 *)(puStack_30 + 6) = 0;
    puStack_30[8] = param_3;
    FUN_439c5a04(auStack_50,0,0x20);
    auStack_50[0] = 0x20;
    FUN_43561244(0x910042,auStack_50);
    *(undefined4 *)(puVar1 + 4) = uStack_38;
    *(undefined4 *)(puVar1 + 6) = uStack_34;
    iVar2 = FUN_439c5004(puVar1 + 10,0x81,param_4,&stack0x00000000);
    if (iVar2 < 0) {
      FUN_435612ec(0x8f0139,puStack_30);
    }
    else {
      if (0x7f < iVar2) {
        iVar2 = 0x80;
      }
      puVar1[9] = (short)iVar2 + 1;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x14) = 10;
      *(undefined1 *)((int)puVar1 + iVar2 + 0x15) = 0;
      *(undefined4 *)(puStack_30 + -2) = 0x8f0139;
      FUN_4356120c();
    }
  }
  return;
}


/* query "43b045e8" */

void FUN_43b045e8(undefined4 param_1,int param_2)

{
  FUN_43ad6da2(param_1,*(undefined1 *)(param_2 + 1),*(undefined4 *)(param_2 + 4));
  FUN_43ad6dc2(param_1);
  FUN_43b0453c();
  return;
}


/* query "43b0453c" */

bool FUN_43b0453c(int param_1)

{
  return param_1 != 0;
}


/* query "43cb3b20" */
