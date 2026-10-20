/* S41: read-only exports. */

/* 436d74b8 */

undefined4 vtable_436d74b8(int param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined1 auStack_1e [6];
  
  iVar4 = DAT_436d75d8 + 0x436d74ce;
  *(undefined1 *)(param_1 + 0x3a4) = 1;
  if (*(int *)(param_1 + 0x170) == 0x11) {
    iVar4 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar4 != 0) {
      FUN_436d6738(0xbc,0,3,DAT_436d75dc + 0x436d74f2,*(undefined4 *)(param_1 + 0x170));
    }
    uVar3 = 2;
  }
  else {
    uStack_24 = *param_2;
    uVar1 = FUN_43ad9438(param_1 + 0x18,*(int *)(param_1 + 0x170),
                         *(undefined4 *)(iVar4 + DAT_436d75e0),0xd);
    iVar2 = (**(code **)(**(int **)(param_1 + 0x294) + 0x10))(*(int **)(param_1 + 0x294),uVar1);
    uStack_22 = *(undefined2 *)(iVar2 + 0x1a);
    iVar2 = (**(code **)(**(int **)(param_1 + 0x294) + 0x10))(*(int **)(param_1 + 0x294),uVar1);
    uStack_20 = *(undefined2 *)(iVar2 + 0x1c);
    FUN_439c5320(auStack_1e,DAT_436d75e4 + 0x436d7536,6);
    uVar1 = FUN_436d8a90(param_1 + 0x18,&uStack_24);
    FUN_43ad9262(param_1,*(undefined4 *)(iVar4 + DAT_436d75e8),*(undefined4 *)(iVar4 + DAT_436d75ec)
                 ,uVar1);
    iVar4 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar4 != 0) {
      iVar4 = *(int *)(param_1 + 0x174);
      if ((iVar4 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar4)) {
        FUN_436d6738(0xbc,0,3,DAT_436d75f0 + 0x436d7598,*(int *)(param_1 + 0x178),iVar4,
                     *(int *)(param_1 + 0x170),uStack_24,uVar1);
      }
    }
    iVar4 = FUN_436d9f70(param_1 + 0xfc,8);
    uVar3 = 0;
    if (iVar4 != 0) {
      FUN_436d6738(0xbc,0,3,DAT_436d75f4 + 0x436d75ca,*(undefined4 *)(param_1 + 0x178),
                   *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),uStack_24,uVar1
                  );
      uVar3 = 0;
    }
  }
  return uVar3;
}


/* 436d7e08 */

undefined4 candidate_436d7e08(int param_1,ushort *param_2)

{
  bool bVar1;
  short sVar2;
  ushort uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  ushort uStack_30;
  undefined2 uStack_2e;
  short sStack_2c;
  undefined1 auStack_2a [8];
  undefined2 uStack_22;
  
  iVar7 = DAT_436d8008 + 0x436d7e20;
  *(undefined1 *)(param_1 + 0x3a3) = 1;
  if (*(int *)(param_1 + 0x170) == 0x11) {
    iVar7 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar7 != 0) {
      FUN_436d6738(0xbc,0,3,DAT_436d800c + 0x436d7e46,*(undefined4 *)(param_1 + 0x170));
    }
    uVar6 = 2;
  }
  else {
    uStack_30 = *param_2;
    iVar8 = param_1 + 0x18;
    uVar4 = FUN_43ad9438(iVar8,*(int *)(param_1 + 0x170),*(undefined4 *)(iVar7 + DAT_436d8010),0xd);
    uVar6 = *(undefined4 *)(param_1 + 0x294);
    iVar5 = FUN_436d6f34(uVar6,uVar4);
    uStack_2e = *(undefined2 *)(iVar5 + 0x1a);
    iVar5 = FUN_436d6f34(uVar6,uVar4);
    sVar2 = *(short *)(iVar5 + 0x1c);
    sStack_2c = sVar2;
    FUN_439c5320(auStack_2a,DAT_436d8014 + 0x436d7e86,6);
    uVar3 = uStack_30;
    if (0x1000 < uStack_30) {
      uStack_30 = (uStack_30 + 0x1000) - sVar2;
    }
    bVar1 = 0x1000 < uVar3;
    uVar4 = FUN_436d8a90(iVar8,&uStack_30);
    FUN_43ad9262(param_1,*(undefined4 *)(iVar7 + DAT_436d8018),*(undefined4 *)(iVar7 + DAT_436d801c)
                 ,uVar4);
    FUN_43ad9262(param_1,*(undefined4 *)(iVar7 + DAT_436d8020),*(undefined4 *)(iVar7 + DAT_436d8024)
                 ,uVar4);
    FUN_43ad9262(param_1,*(undefined4 *)(iVar7 + DAT_436d8028),*(undefined4 *)(iVar7 + DAT_436d802c)
                 ,uVar4);
    FUN_43ad9262(param_1,*(undefined4 *)(iVar7 + DAT_436d8030),*(undefined4 *)(iVar7 + DAT_436d8034)
                 ,uVar4);
    FUN_436d7de8(param_1,bVar1);
    iVar7 = FUN_436d8a74(iVar8,*(undefined4 *)(param_1 + 0x170));
    if (iVar7 != 0) {
      *(short *)(param_1 + 0xc) = (short)uVar4;
      *(ushort *)(param_1 + 0xe) = uStack_30;
      *(bool *)(param_1 + 0x16) = bVar1;
      uVar6 = FUN_436d6118();
      iVar7 = FUN_436d6450(uVar6,&uStack_22);
      if (iVar7 != 0) {
        uStack_22 = 0xffff;
      }
      *(undefined2 *)(param_1 + 6) = uStack_22;
    }
    iVar5 = param_1 + 0xfc;
    FUN_43ad9a60(iVar5,*param_2,uVar4,uStack_30,bVar1);
    FUN_43ad9a0a(iVar5,*(undefined4 *)(param_1 + 0x162),*(undefined4 *)(param_1 + 0x166),
                 *(undefined4 *)(param_1 + 0x16a));
    iVar7 = FUN_436d9f70(iVar5,1);
    if (iVar7 != 0) {
      iVar7 = *(int *)(param_1 + 0x174);
      if ((iVar7 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar7)) {
        FUN_436d6738(0xbc,0,3,DAT_436d8038 + 0x436d7fc2,*(int *)(param_1 + 0x178),iVar7,
                     *(int *)(param_1 + 0x170),*param_2,uStack_30,uVar4);
      }
    }
    iVar7 = FUN_436d9f70(iVar5,8);
    uVar6 = 0;
    if (iVar7 != 0) {
      FUN_436d6738(0xbc,0,3,DAT_436d803c + 0x436d7ffa,*(undefined4 *)(param_1 + 0x178),
                   *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),*param_2,
                   uStack_30,uVar4);
      uVar6 = 0;
    }
  }
  return uVar6;
}


/* 43ad909c */

void FUN_43ad909c(undefined4 *param_1)

{
  (**(code **)(*(int *)*param_1 + 0x94))();
  return;
}


/* 436d8774 */

int * FUN_436d8774(int *param_1)

{
  int iVar1;
  int in_stack_0000002c;
  int in_stack_00000030;
  int in_stack_00000034;
  
  iVar1 = DAT_436d87d0 + 0x436d8782;
  FUN_436d99b8();
  *param_1 = *(int *)(iVar1 + DAT_436d87d4) + 8;
  param_1[0x12] = in_stack_00000034;
  param_1[0x10] = in_stack_0000002c;
  param_1[0x11] = in_stack_00000030;
  *(undefined1 *)(param_1 + 0x13) = 0;
  return param_1;
}

