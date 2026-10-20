/* S41: read-only exports. */

/* 436d839c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d839c(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 in_stack_ffffffc8;
  undefined2 uVar9;
  
  uVar9 = (undefined2)((uint)in_stack_ffffffc8 >> 0x10);
  piVar5 = param_1 + 0x3f;
  iVar6 = _DAT_436d864c + 0x436d83b2;
  iVar1 = FUN_436d9f70(piVar5,1);
  if (iVar1 != 0) {
    iVar3 = param_1[0x5d];
    iVar1 = param_1[0x5c];
    if ((iVar3 != iVar1) || (param_1[0x5e] != iVar3)) {
      FUN_436d6738(0xbc,0,3,_DAT_436d8650 + 0x436d83e8,param_1[0x5e],iVar3,iVar1,(char)param_1[0x9a]
                   ,*(undefined1 *)((int)param_1 + 0x267));
      uVar9 = (undefined2)((uint)iVar1 >> 0x10);
    }
  }
  iVar1 = FUN_436d9f70(piVar5,8);
  if (iVar1 != 0) {
    iVar1 = param_1[0x9a];
    iVar3 = param_1[0x5c];
    iVar7 = param_1[0x5d];
    iVar8 = param_1[0x5e];
    uVar2 = (**(code **)(*param_1 + 0xac))(param_1);
    FUN_436d6738(0xbc,0,3,_DAT_436d8654 + 0x436d8414,iVar8,iVar7,iVar3,(char)iVar1,uVar2);
    uVar9 = (undefined2)((uint)iVar3 >> 0x10);
  }
  if (*(char *)(*(int *)(iVar6 + _DAT_436d8658) + 0x60) == '\0') {
    FUN_436d6738(0xbc,0,1,_DAT_436d865c + 0x436d846e,param_1[0x5e],param_1[0x5d],param_1[0x5c],
                 (char)param_1[0x9a],*(undefined1 *)((int)param_1 + 0x3a3),(char)param_1[0xe9],
                 param_1[0xea],param_1[0xeb]);
    uVar4 = (uint)*(byte *)(param_1 + 0xe9);
    FUN_43902718(_DAT_436d8660 + 0x436d8480,param_1[0x5e],param_1[0x5d],param_1[0x5c],
                 (char)param_1[0x9a],*(undefined1 *)((int)param_1 + 0x3a3),uVar4,param_1[0xea],
                 param_1[0xeb]);
    uVar9 = (undefined2)(uVar4 >> 0x10);
  }
  *(undefined1 *)((int)param_1 + 0x3a3) = 0;
  *(undefined1 *)(param_1 + 0xe9) = 0;
  param_1[0xea] = -1;
  param_1[0xeb] = -1;
  iVar1 = FUN_436d9f70(piVar5,0x10);
  if (iVar1 != 0) {
    if (param_1[0x5c] == 0xb) {
      func_0x43ad8d86(param_1 + 0xa6,1);
    }
    else {
      FUN_43ad926a(param_1);
    }
  }
  if (param_1[0x5d] != param_1[0x5c]) {
    *(undefined2 *)(param_1 + 0xa0) = 0;
    *(undefined2 *)((int)param_1 + 0x282) = 0;
  }
  func_0x436d79c4(param_1);
  func_0x436d7b34(param_1);
  func_0x436d8040(param_1);
  func_0x436d7c08(param_1);
  func_0x436d7c58(param_1);
  func_0x436d7c94(param_1);
  func_0x436d7db4(param_1);
  func_0x436d7cb0(param_1);
  func_0x436d7cf0(param_1);
  func_0x43ad92d0(param_1);
  func_0x436d8244(param_1);
  func_0x436d8064(param_1);
  (**(code **)(*param_1 + 0x9c))(param_1);
  iVar1 = func_0x43ad96ba(param_1);
  if (iVar1 != 0) {
    func_0x436d8f00(param_1 + 6,*(undefined1 *)((int)param_1 + 0x17d),param_1[0x9b]);
    FUN_436d6738(0xbc,0,3,_DAT_436d8664 + 0x436d8566);
  }
  if ((param_1[0x5c] != 0x11) || ((param_1[0x5d] != 0x11 && (param_1[0x5d] != 0)))) {
    uVar2 = candidate_436d79b0(param_1);
    candidate_436d75f8(param_1,2,uVar2);
    FUN_436d5bcc(param_1 + 0xa6);
    candidate_436d75f8(param_1,0,*(undefined4 *)(iVar6 + _DAT_436d8668));
  }
  param_1[0x5e] = param_1[0x5d];
  param_1[0x5d] = param_1[0x5c];
  *(char *)((int)param_1 + 0x17d) = (char)param_1[0x5f];
  func_0x43ad99ba(piVar5);
  func_0x436d9ec8(piVar5);
  iVar1 = func_0x436d9f48(piVar5,1);
  if ((iVar1 != 0) || (param_1[0x5c] == 0xb)) {
    FUN_43ad9a78(piVar5,param_1[0x53],param_1[0x54],param_1[0x55],param_1[0x56],param_1[0x57],
                 CONCAT22(uVar9,(short)param_1[0x58]));
    FUN_43ad9ab2(piVar5,*(undefined4 *)((int)param_1 + 0x162),*(undefined4 *)((int)param_1 + 0x166),
                 *(undefined4 *)((int)param_1 + 0x16a));
  }
  if (param_1[0x5c] == 0x11) {
    iVar1 = FUN_436d9f70(piVar5,1);
    if (iVar1 != 0) {
      FUN_436d6738(0xbc,0,3,_DAT_436d866c + 0x436d863c,param_1[0x5c]);
    }
    uVar2 = 2;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}


/* 436d839c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d839c(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 in_stack_ffffffc8;
  undefined2 uVar9;
  
  uVar9 = (undefined2)((uint)in_stack_ffffffc8 >> 0x10);
  piVar5 = param_1 + 0x3f;
  iVar6 = _DAT_436d864c + 0x436d83b2;
  iVar1 = FUN_436d9f70(piVar5,1);
  if (iVar1 != 0) {
    iVar3 = param_1[0x5d];
    iVar1 = param_1[0x5c];
    if ((iVar3 != iVar1) || (param_1[0x5e] != iVar3)) {
      FUN_436d6738(0xbc,0,3,_DAT_436d8650 + 0x436d83e8,param_1[0x5e],iVar3,iVar1,(char)param_1[0x9a]
                   ,*(undefined1 *)((int)param_1 + 0x267));
      uVar9 = (undefined2)((uint)iVar1 >> 0x10);
    }
  }
  iVar1 = FUN_436d9f70(piVar5,8);
  if (iVar1 != 0) {
    iVar1 = param_1[0x9a];
    iVar3 = param_1[0x5c];
    iVar7 = param_1[0x5d];
    iVar8 = param_1[0x5e];
    uVar2 = (**(code **)(*param_1 + 0xac))(param_1);
    FUN_436d6738(0xbc,0,3,_DAT_436d8654 + 0x436d8414,iVar8,iVar7,iVar3,(char)iVar1,uVar2);
    uVar9 = (undefined2)((uint)iVar3 >> 0x10);
  }
  if (*(char *)(*(int *)(iVar6 + _DAT_436d8658) + 0x60) == '\0') {
    FUN_436d6738(0xbc,0,1,_DAT_436d865c + 0x436d846e,param_1[0x5e],param_1[0x5d],param_1[0x5c],
                 (char)param_1[0x9a],*(undefined1 *)((int)param_1 + 0x3a3),(char)param_1[0xe9],
                 param_1[0xea],param_1[0xeb]);
    uVar4 = (uint)*(byte *)(param_1 + 0xe9);
    FUN_43902718(_DAT_436d8660 + 0x436d8480,param_1[0x5e],param_1[0x5d],param_1[0x5c],
                 (char)param_1[0x9a],*(undefined1 *)((int)param_1 + 0x3a3),uVar4,param_1[0xea],
                 param_1[0xeb]);
    uVar9 = (undefined2)(uVar4 >> 0x10);
  }
  *(undefined1 *)((int)param_1 + 0x3a3) = 0;
  *(undefined1 *)(param_1 + 0xe9) = 0;
  param_1[0xea] = -1;
  param_1[0xeb] = -1;
  iVar1 = FUN_436d9f70(piVar5,0x10);
  if (iVar1 != 0) {
    if (param_1[0x5c] == 0xb) {
      func_0x43ad8d86(param_1 + 0xa6,1);
    }
    else {
      FUN_43ad926a(param_1);
    }
  }
  if (param_1[0x5d] != param_1[0x5c]) {
    *(undefined2 *)(param_1 + 0xa0) = 0;
    *(undefined2 *)((int)param_1 + 0x282) = 0;
  }
  func_0x436d79c4(param_1);
  func_0x436d7b34(param_1);
  func_0x436d8040(param_1);
  func_0x436d7c08(param_1);
  func_0x436d7c58(param_1);
  func_0x436d7c94(param_1);
  func_0x436d7db4(param_1);
  func_0x436d7cb0(param_1);
  func_0x436d7cf0(param_1);
  func_0x43ad92d0(param_1);
  func_0x436d8244(param_1);
  func_0x436d8064(param_1);
  (**(code **)(*param_1 + 0x9c))(param_1);
  iVar1 = func_0x43ad96ba(param_1);
  if (iVar1 != 0) {
    func_0x436d8f00(param_1 + 6,*(undefined1 *)((int)param_1 + 0x17d),param_1[0x9b]);
    FUN_436d6738(0xbc,0,3,_DAT_436d8664 + 0x436d8566);
  }
  if ((param_1[0x5c] != 0x11) || ((param_1[0x5d] != 0x11 && (param_1[0x5d] != 0)))) {
    uVar2 = candidate_436d79b0(param_1);
    candidate_436d75f8(param_1,2,uVar2);
    FUN_436d5bcc(param_1 + 0xa6);
    candidate_436d75f8(param_1,0,*(undefined4 *)(iVar6 + _DAT_436d8668));
  }
  param_1[0x5e] = param_1[0x5d];
  param_1[0x5d] = param_1[0x5c];
  *(char *)((int)param_1 + 0x17d) = (char)param_1[0x5f];
  func_0x43ad99ba(piVar5);
  func_0x436d9ec8(piVar5);
  iVar1 = func_0x436d9f48(piVar5,1);
  if ((iVar1 != 0) || (param_1[0x5c] == 0xb)) {
    FUN_43ad9a78(piVar5,param_1[0x53],param_1[0x54],param_1[0x55],param_1[0x56],param_1[0x57],
                 CONCAT22(uVar9,(short)param_1[0x58]));
    FUN_43ad9ab2(piVar5,*(undefined4 *)((int)param_1 + 0x162),*(undefined4 *)((int)param_1 + 0x166),
                 *(undefined4 *)((int)param_1 + 0x16a));
  }
  if (param_1[0x5c] == 0x11) {
    iVar1 = FUN_436d9f70(piVar5,1);
    if (iVar1 != 0) {
      FUN_436d6738(0xbc,0,3,_DAT_436d866c + 0x436d863c,param_1[0x5c]);
    }
    uVar2 = 2;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

