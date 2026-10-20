/* S41: read-only exports. */

/* 43b71d36 */

undefined4 FUN_43b71d36(int param_1)

{
  *(undefined1 *)(param_1 + 8) = 0x26;
  *(undefined1 *)(param_1 + 9) = 0x3c;
  *(undefined1 *)(param_1 + 10) = 0x24;
  *(undefined1 *)(param_1 + 0xb) = 0x3a;
  *(undefined1 *)(param_1 + 0xc) = 0x28;
  *(undefined1 *)(param_1 + 0xd) = 0x3e;
  *(undefined1 *)(param_1 + 0xe) = 0x2f;
  *(undefined1 *)(param_1 + 0xf) = 0x33;
  *(undefined1 *)(param_1 + 0x10) = 0x24;
  *(undefined1 *)(param_1 + 0x11) = 0x28;
  *(undefined1 *)(param_1 + 0x12) = 0x3a;
  *(undefined1 *)(param_1 + 0x13) = 0x3e;
  *(undefined1 *)(param_1 + 0x14) = 0x23;
  *(undefined1 *)(param_1 + 0x15) = 0x39;
  *(undefined1 *)(param_1 + 0x16) = 0x29;
  *(undefined1 *)(param_1 + 0x17) = 0x3f;
  *(undefined1 *)(param_1 + 0x18) = 0x19;
  *(undefined1 *)(param_1 + 0x19) = 0x1d;
  *(undefined1 *)(param_1 + 0x1c) = 0x19;
  *(undefined1 *)(param_1 + 0x1a) = 0x45;
  *(undefined1 *)(param_1 + 0x1e) = 0x23;
  *(undefined1 *)(param_1 + 0x1b) = 0x49;
  *(undefined1 *)(param_1 + 0x1d) = 0x49;
  *(undefined1 *)(param_1 + 0x1f) = 0x3f;
  *(undefined1 *)(param_1 + 0x20) = 0x26;
  *(undefined1 *)(param_1 + 0x21) = 0x3c;
  *(undefined1 *)(param_1 + 0x22) = 0x24;
  *(undefined1 *)(param_1 + 0x23) = 0x3a;
  *(undefined1 *)(param_1 + 0x24) = 0x28;
  *(undefined1 *)(param_1 + 0x25) = 0x3e;
  *(undefined1 *)(param_1 + 0x26) = 0x2f;
  *(undefined1 *)(param_1 + 0x27) = 0x33;
  *(undefined1 *)(param_1 + 0x28) = 0x24;
  *(undefined1 *)(param_1 + 0x2b) = 0x3e;
  *(undefined1 *)(param_1 + 0x2e) = 0x29;
  *(undefined1 *)(param_1 + 0x2d) = 0x39;
  *(undefined1 *)(param_1 + 0x29) = 0x28;
  *(undefined1 *)(param_1 + 0x2a) = 0x3a;
  *(undefined1 *)(param_1 + 0x2c) = 0x23;
  *(undefined1 *)(param_1 + 0x2f) = 0x3f;
  *(undefined1 *)(param_1 + 0x30) = 0x19;
  *(undefined1 *)(param_1 + 0x31) = 0x1d;
  *(undefined1 *)(param_1 + 0x32) = 0x45;
  *(undefined1 *)(param_1 + 0x33) = 0x49;
  *(undefined1 *)(param_1 + 0x34) = 0x19;
  *(undefined1 *)(param_1 + 0x35) = 0x49;
  *(undefined1 *)(param_1 + 0x36) = 0x23;
  *(undefined1 *)(param_1 + 0x37) = 0x3f;
  return 1;
}


/* 437b5b14 */

void FUN_437b5b14(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  
  FUN_43859710(0x10);
  iVar8 = DAT_437b5ce0;
  FUN_4383b520(0x20,0);
  iVar8 = iVar8 + 0x437b5b34;
  uVar10 = *(undefined4 *)(iVar8 + DAT_437b5ce4);
  iVar9 = *(int *)(iVar8 + DAT_437b5ce8);
  uVar11 = *(undefined4 *)(iVar8 + DAT_437b5cec);
  uVar12 = *(undefined4 *)(iVar8 + DAT_437b5cf0);
  uVar13 = *(undefined4 *)(iVar8 + DAT_437b5cf4);
  uVar15 = *(undefined4 *)(iVar8 + DAT_437b5cf8);
  uVar16 = *(undefined4 *)(iVar8 + DAT_437b5cfc);
  uVar1 = *(undefined4 *)(iVar8 + DAT_437b5d00);
  uVar2 = *(undefined4 *)(iVar8 + DAT_437b5d04);
  uVar3 = *(undefined4 *)(iVar8 + DAT_437b5d08);
  uVar4 = *(undefined4 *)(iVar8 + DAT_437b5d0c);
  FUN_43844e80(param_1,*(undefined4 *)(iVar8 + DAT_437b5d10),*(undefined4 *)(iVar8 + DAT_437b5d14),
               *(int *)(iVar8 + DAT_437b5d18) + 0x290,uVar10,iVar9,uVar11,uVar12,uVar13,uVar15,
               uVar16,uVar1,uVar2,uVar3,uVar4);
  FUN_4383b520(0x20,1);
  FUN_4383b520(0x21,0);
  FUN_43859ae0(iVar9);
  FUN_4383b520(0x21,1);
  FUN_4383b520(0x22,0);
  uVar5 = *(undefined4 *)(iVar8 + DAT_437b5d1c);
  FUN_4382dd78(param_1,iVar9,uVar5);
  FUN_4383b520(0x22,1);
  uVar14 = *(undefined4 *)(iVar8 + DAT_437b5d20);
  uVar6 = *(undefined4 *)(iVar8 + DAT_437b5d24);
  uVar7 = *(undefined4 *)(iVar8 + DAT_437b5d28);
  if (*(int *)(iVar9 + 0x24c) == 0) {
    FUN_4383b520(0x23);
    FUN_43859b34(iVar9,uVar7,uVar11,uVar12,uVar2,uVar13,uVar15,uVar1,uVar14,uVar5,uVar3,uVar16,uVar4
                 ,uVar10,uVar6);
    FUN_4383b520(0x23,1);
  }
  FUN_4383b520(0x35,0);
  FUN_4384b268(uVar7,uVar11,uVar12,uVar13,uVar2,uVar5,uVar3,uVar16,uVar14,uVar1,uVar4,uVar6,uVar10,
               iVar9,uVar15,*(undefined4 *)(iVar8 + DAT_437b5d2c),param_2);
  FUN_4383b520(0x35,1);
  FUN_4383b520(0x36,0);
  FUN_43b08648();
  FUN_4385b234(iVar9);
  FUN_4383a974();
  FUN_43859710(0x20);
  FUN_43859a24();
  FUN_4383b520(0x36,1);
  return;
}

