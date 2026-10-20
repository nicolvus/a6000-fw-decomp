/* S41: read-only exports. */

/* 436c7950 */

void FUN_436c7950(int param_1,undefined4 param_2,undefined4 param_3,int param_4,undefined4 param_5)

{
  ushort uVar1;
  undefined4 uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined1 auStack_94 [20];
  undefined1 auStack_80 [20];
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  iVar6 = DAT_436c7b24;
  iVar4 = param_1 + 4;
  FUN_43acee66(iVar4);
  iVar5 = *(int *)(param_4 + 0x30);
  iVar6 = iVar6 + 0x436c7970;
  *(undefined4 *)(param_1 + 0xc) = param_3;
  *(undefined4 *)(param_1 + 0x10) = 1;
  *(undefined4 *)(param_1 + 0x14) = 1;
  *(undefined4 *)(param_1 + 0x18) = 1;
  *(undefined4 *)(param_1 + 0x1c) = 1;
  *(undefined4 *)(param_1 + 0x20) = 4;
  *(undefined4 *)(param_1 + 0x24) = 1;
  *(undefined4 *)(param_1 + 0x28) = 1;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  if (iVar5 == 0) {
    FUN_43932394(0xb);
  }
  else if (iVar5 == 1) {
    FUN_43932394(8);
    FUN_43932490(1);
  }
  else {
    FUN_43932394(0xb);
    FUN_436c7238(8,0,1,DAT_436c7b28 + 0x436c79c2,*(undefined4 *)(param_4 + 0x30));
    FUN_43902718(DAT_436c7b2c + 0x436c79cc,*(undefined4 *)(param_4 + 0x30));
  }
  uVar1 = *(ushort *)(param_4 + 0x34);
  puVar3 = *(uint **)(iVar6 + DAT_436c7b30);
  *(undefined4 *)(param_1 + 0x34) = 1;
  *(undefined4 *)(param_1 + 0x38) = 1;
  *puVar3 = (uint)uVar1;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined4 *)(param_1 + 0x40) = 0;
  *(undefined4 *)(param_1 + 0x4c) = param_5;
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0;
  FUN_43ad3d70(&uStack_44);
  *(undefined4 *)(param_1 + 0x50) = uStack_44;
  *(undefined4 *)(param_1 + 0x54) = uStack_40;
  *(undefined4 *)(param_1 + 0x58) = uStack_3c;
  *(undefined4 *)(param_1 + 0x5c) = uStack_38;
  *(undefined4 *)(param_1 + 0x60) = uStack_34;
  FUN_43ad3d70(&uStack_58);
  *(undefined4 *)(param_1 + 100) = uStack_58;
  *(undefined4 *)(param_1 + 0x68) = uStack_54;
  *(undefined4 *)(param_1 + 0x6c) = uStack_50;
  *(undefined4 *)(param_1 + 0x70) = uStack_4c;
  *(undefined4 *)(param_1 + 0x74) = uStack_48;
  FUN_43ad3d70(&uStack_6c);
  *(undefined4 *)(param_1 + 0x78) = uStack_6c;
  *(undefined4 *)(param_1 + 0x7c) = uStack_68;
  *(undefined4 *)(param_1 + 0x80) = uStack_64;
  *(undefined4 *)(param_1 + 0x84) = uStack_60;
  uVar2 = DAT_436c7b20;
  *(undefined4 *)(param_1 + 0x88) = uStack_5c;
  FUN_43ad385c(uVar2,1);
  FUN_43ad3858(DAT_436c7b20,1);
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad38aa(uVar2,1);
  FUN_43ad3886(DAT_436c7b20,0,0,0,0,0,0,0);
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad2bca(uVar2,1);
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad2be6(uVar2,*(undefined4 *)(param_4 + 8),*(undefined4 *)(param_4 + 4));
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad2bf0(uVar2,*(undefined4 *)(param_4 + 0xc));
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad3952(uVar2,0x3ffe,0x3ffe);
  uVar2 = FUN_43acee62(iVar4);
  FUN_43ad395c(uVar2,0x3ffe,0x3ffe);
  FUN_43ad3ade(param_1,0);
  FUN_43ad3b6a(param_1,0);
  uStack_28 = *(undefined4 *)(iVar6 + DAT_436c7b34);
  uStack_24 = 0;
  FUN_43ad3dfa(auStack_80,uStack_28,0,param_1);
  FUN_43ace9b8(param_1,auStack_80);
  uStack_30 = *(undefined4 *)(iVar6 + DAT_436c7b38);
  uStack_2c = 0;
  FUN_43ad3dfa(auStack_94,uStack_30,0,param_1);
  FUN_43ad3830(param_1,auStack_94);
  return;
}


/* 436c6e64 */

int * FUN_436c6e64(int *param_1)

{
  FUN_436c6b6c();
  *param_1 = *(int *)(DAT_436c6e94 + 0x436c6e76 + DAT_436c6e98) + 8;
  FUN_43ad2f0c(param_1 + 0x14);
  FUN_43ad2f0c(param_1 + 0x19);
  FUN_43ad2f0c(param_1 + 0x1e);
  return param_1;
}


/* 43ad35ee */

int FUN_43ad35ee(int param_1)

{
  FUN_436c6b84();
  FUN_436c6bb4(param_1 + 0xb8);
  FUN_436c6bfc(param_1 + 0x200);
  FUN_436c6c2c(param_1 + 0x288);
  FUN_436c6c5c(param_1 + 0x2fc);
  FUN_436c6c8c(param_1 + 0x380);
  FUN_436c6cbc(param_1 + 0x3f0);
  FUN_436c6cec(param_1 + 0x460);
  FUN_436c6d4c(param_1 + 0x524);
  FUN_436c6d6c(param_1 + 0x544);
  FUN_436c6d8c(param_1 + 0x564);
  FUN_436c6dac(param_1 + 0x584);
  FUN_436c6dac(param_1 + 0x5b4);
  FUN_436c6dac(param_1 + 0x5e4);
  FUN_436c6dac(param_1 + 0x614);
  FUN_436c6dac(param_1 + 0x644);
  FUN_436c6dac(param_1 + 0x674);
  FUN_436c6de4(param_1 + 0x6bc);
  FUN_436c6e24(param_1 + 0x6d0);
  FUN_436c6e44(param_1 + 0x6ec);
  return param_1;
}


/* 43acee7a */

void FUN_43acee7a(int param_1)

{
  FUN_43acee66();
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined4 *)(param_1 + 0x14) = 4;
  return;
}


/* 436c5d2c */

void FUN_436c5d2c(int param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar3 = param_1 + 4;
  iVar4 = param_1;
  uVar1 = param_3;
  iVar5 = param_4;
  FUN_43acee66(iVar3);
  *(undefined4 *)(param_1 + 0xc) = param_3;
  *(int *)(param_1 + 0x8c) = param_5;
  if (param_5 == 0) {
    *(undefined4 *)(param_1 + 0x98) = 2;
    *(undefined4 *)(param_1 + 0x9c) = 2;
    *(undefined4 *)(param_1 + 0x10) = 4;
    *(undefined4 *)(param_1 + 0x14) = 4;
    uVar2 = 6;
  }
  else {
    *(undefined4 *)(param_1 + 0x98) = 0x10;
    *(undefined4 *)(param_1 + 0x9c) = 0x10;
    *(undefined4 *)(param_1 + 0x10) = 0x20;
    *(undefined4 *)(param_1 + 0x14) = 0x20;
    uVar2 = 0x30;
  }
  *(undefined4 *)(param_1 + 0x18) = uVar2;
  *(undefined4 *)(param_1 + 0x1c) = uVar2;
  *(undefined4 *)(param_1 + 0x88) = 0;
  *(undefined4 *)(param_1 + 0xa4) = 0;
  *(undefined4 *)(param_1 + 0xa8) = 2;
  *(undefined4 *)(param_1 + 0x70) = 0;
  *(undefined4 *)(param_1 + 0x74) = 0;
  *(undefined1 *)(param_1 + 0xac) = 1;
  *(undefined4 *)(param_1 + 0xb0) = 0;
  uVar2 = FUN_43acee62(iVar3);
  FUN_43ad2b88(uVar2,1,1,1,iVar4,param_2,uVar1,iVar5);
  if (*(int *)(param_4 + 0x30) == 1) {
    uVar1 = FUN_43acee62(iVar3);
    FUN_43ad2b7a(uVar1,1,0,0);
    FUN_43ad2b62(DAT_436c5e5c,0,0,0,0,0xff00);
    *(undefined4 *)(param_1 + 0x90) = 3;
  }
  else {
    uVar1 = FUN_43acee62(iVar3);
    FUN_43ad2b7a(uVar1,0,1,1);
    FUN_43ad2b62(DAT_436c5e5c,0,0,1,1,0xf000);
    *(undefined4 *)(param_1 + 0x90) = 2;
  }
  uVar1 = FUN_43acee62(iVar3);
  FUN_43ad2b96(uVar1,1,1,1,1,1,1);
  FUN_436c5d20(param_1,0);
  if (*(int *)(param_1 + 0x8c) != 0) {
    uVar1 = FUN_43acee62(iVar3);
    FUN_43ad2bca(uVar1,1);
    uVar1 = FUN_43acee62(iVar3);
    FUN_43ad2be6(uVar1,*(undefined4 *)(param_4 + 8),*(undefined4 *)(param_4 + 4));
    uVar1 = FUN_43acee62(iVar3);
    FUN_43ad2bf0(uVar1,*(undefined4 *)(param_4 + 0xc));
    return;
  }
  return;
}

