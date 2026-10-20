/* S39: existing functions; no project modifications. */

/* 4365dde0 */

int FUN_4365dde0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar1 = *(int *)(param_1 + 0x458);
  iVar2 = *(int *)(param_1 + 0x44c);
  iVar4 = (iVar1 + 2) - iVar2;
  if ((*(int *)(param_1 + iVar4 * 4 + 0x47c) != 1) && (*(int *)(param_1 + iVar4 * 4 + 0x46c) != 1))
  {
    if (iVar1 + 1 == iVar2) {
      iVar2 = *(int *)(param_2 + 0x10);
      *(int *)(param_1 + 0x458) = iVar1 + 1;
      if (*(int *)(*(int *)(iVar2 + 8) + 0x9c) == 1) {
        iVar1 = FUN_4365d550();
        if (iVar1 != 0) {
          FUN_435ab880(DAT_4365df94 + 0x4365de3e,iVar1,DAT_4365df98 + 0x4365de42,
                       DAT_4365df9c + 0x4365de44,0xbb0);
          FUN_435ab880(DAT_4365dfa0 + 0x4365de4c);
          uVar5 = 0xbb2;
          uVar3 = 0x4bf;
          goto LAB_4365df1a;
        }
        *(undefined4 *)(param_1 + 0x484) = 1;
      }
      else {
        *(undefined4 *)(param_1 + 0x484) = 3;
      }
    }
    else {
      if (iVar1 != iVar2) {
        FUN_43639190(0x40,0,0x6012,0x4da,4,0x80000000,0,0xbc0);
        uVar3 = *(undefined4 *)(param_1 + 0x458);
        uVar5 = 0xbc1;
        goto LAB_4365df76;
      }
      *(undefined4 *)(param_1 + 0x488) = 4;
    }
    iVar1 = *(int *)(param_1 + 0x454) + 1;
    if (iVar1 == *(int *)(param_1 + 0x44c)) {
      iVar2 = *(int *)(param_2 + 0x10);
      *(int *)(param_1 + 0x454) = iVar1;
      if (*(int *)(*(int *)(iVar2 + 8) + 0x80) == 1) {
        iVar1 = FUN_4365cfcc(param_1,param_2);
        if (iVar1 == 0) {
          iVar1 = *(int *)(param_2 + 0x10);
          *(undefined4 *)(param_1 + 0x474) = 1;
          *(undefined4 *)(param_1 + 0x438) = *(undefined4 *)(*(int *)(iVar1 + 8) + 0x88);
          return 0;
        }
        FUN_435ab880(DAT_4365dfa4 + 0x4365def0,iVar1,DAT_4365dfa8 + 0x4365def4,
                     DAT_4365dfac + 0x4365def6,0xbcf);
        FUN_435ab880(DAT_4365dfb0 + 0x4365defe);
        uVar5 = 0xbd1;
        uVar3 = 0x4c0;
LAB_4365df1a:
        FUN_43639190(0x40,0,0x6012,uVar3,4,iVar1,0,uVar5);
        return iVar1;
      }
      *(undefined4 *)(param_1 + 0x474) = 3;
    }
    else {
      if (*(int *)(param_1 + 0x454) != *(int *)(param_1 + 0x44c)) {
        FUN_43639190(0x40,0,0x6012,0x4db,4,0x80000000,0,0xbe2);
        uVar3 = *(undefined4 *)(param_1 + 0x454);
        uVar5 = 0xbe3;
LAB_4365df76:
        FUN_43639204(0x80,0,0x6012,*(undefined4 *)(param_1 + 0x44c),uVar3,0,uVar5);
        return -0x80000000;
      }
      *(undefined4 *)(param_1 + 0x478) = 4;
    }
  }
  return 0;
}


/* 4365e424 */

int FUN_4365e424(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (*(int *)(param_1 + 0x484) == 0) {
    *(int *)(param_1 + 0x458) = *(int *)(param_1 + 0x458) + 1;
    if (*(int *)(*(int *)(*(int *)(param_2 + 0x10) + 8) + 0x9c) == 1) {
      iVar1 = FUN_4365d550();
      if (iVar1 != 0) {
        FUN_435ab880(DAT_4365e7d0 + 0x4365e468,iVar1,DAT_4365e7d4 + 0x4365e46c,
                     DAT_4365e7d8 + 0x4365e46e,0x85b);
        FUN_435ab880(DAT_4365e7dc + 0x4365e476);
        uVar3 = 0x85d;
        uVar2 = 0x4b5;
        goto LAB_4365e502;
      }
      *(undefined4 *)(param_1 + 0x484) = 1;
    }
    else {
      *(undefined4 *)(param_1 + 0x484) = 3;
    }
  }
  if (*(int *)(param_1 + 0x494) == 0) {
    *(int *)(param_1 + 0x45c) = *(int *)(param_1 + 0x45c) + 1;
    if (*(int *)(*(int *)(*(int *)(param_2 + 0x10) + 8) + 0x9c) != 1) {
      *(undefined4 *)(param_1 + 0x494) = 3;
      goto LAB_4365e514;
    }
    iVar1 = FUN_4365d630(param_1,param_2);
    if (iVar1 == 0) {
      *(undefined4 *)(param_1 + 0x494) = 1;
      goto LAB_4365e514;
    }
    FUN_435ab880(DAT_4365e7e0 + 0x4365e4da,iVar1,DAT_4365e7e4 + 0x4365e4de,DAT_4365e7e8 + 0x4365e4e0
                 ,0x873);
    FUN_435ab880(DAT_4365e7ec + 0x4365e4e8);
    uVar3 = 0x875;
LAB_4365e4f4:
    uVar2 = 0x4b6;
    goto LAB_4365e502;
  }
LAB_4365e514:
  if (*(int *)(param_1 + 0x4a4) == 0) {
    *(int *)(param_1 + 0x460) = *(int *)(param_1 + 0x460) + 1;
    iVar1 = *(int *)(*(int *)(param_2 + 0x10) + 8);
    if ((*(int *)(iVar1 + 0x9c) == 1) && (*(int *)(iVar1 + 0xc4) - 2U < 2)) {
      iVar1 = FUN_4365d374(param_1,param_2);
      if (iVar1 != 0) {
        FUN_435ab880(DAT_4365e7f0 + 0x4365e55a,iVar1,DAT_4365e7f4 + 0x4365e55e,
                     DAT_4365e7f8 + 0x4365e560,0x88d);
        FUN_435ab880(DAT_4365e7fc + 0x4365e568);
        uVar3 = 0x88f;
        uVar2 = 0x4b7;
        goto LAB_4365e502;
      }
      *(undefined4 *)(param_1 + 0x4a4) = 1;
    }
    else {
      *(undefined4 *)(param_1 + 0x4a4) = 3;
    }
  }
  if (*(int *)(param_1 + 0x4c4) == 0) {
    *(int *)(param_1 + 0x468) = *(int *)(param_1 + 0x468) + 1;
    if ((*(int *)(param_1 + 0x448) == 3) &&
       (iVar1 = *(int *)(*(int *)(param_2 + 0x10) + 8), *(int *)(iVar1 + 0xe4) == 1)) {
      iVar1 = FUN_4364d074(param_1 + 0x43c,iVar1 + 0xe4,*(undefined4 *)(param_1 + 100),
                           param_2 + 0xa8,*(undefined4 *)(param_1 + 600),
                           *(undefined4 *)(param_1 + 0x25c),*(undefined4 *)(param_2 + 0x5c));
      if (iVar1 != 0) {
        FUN_435ab880(DAT_4365e800 + 0x4365e5ee,iVar1,DAT_4365e804 + 0x4365e5f2,
                     DAT_4365e808 + 0x4365e5f4,0x8aa);
        FUN_435ab880(DAT_4365e80c + 0x4365e5fc);
        uVar3 = 0x8ac;
        goto LAB_4365e4f4;
      }
      *(undefined4 *)(param_1 + 0x4c4) = 1;
    }
    else {
      *(undefined4 *)(param_1 + 0x4c4) = 3;
    }
  }
  if (*(int *)(param_1 + 0x4b4) == 0) {
    *(int *)(param_1 + 0x464) = *(int *)(param_1 + 0x464) + 1;
    iVar1 = *(int *)(*(int *)(param_2 + 0x10) + 8);
    if ((*(int *)(iVar1 + 0x9c) == 1) &&
       ((iVar1 = *(int *)(iVar1 + 0xc4), iVar1 == 1 || (iVar1 == 3)))) {
      if (*(int *)(param_1 + 0x4cc) == 1) {
        iVar1 = FUN_4365db00(param_1,param_2,param_3);
        if (iVar1 != 0) {
          FUN_435ab880(DAT_4365e810 + 0x4365e66c,iVar1,DAT_4365e814 + 0x4365e670,
                       DAT_4365e818 + 0x4365e672,0x8c9);
          FUN_435ab880(DAT_4365e81c + 0x4365e67a);
          uVar3 = 0x8cb;
          uVar2 = 0x4b8;
          goto LAB_4365e502;
        }
      }
      else {
        iVar1 = FUN_4365dc3c(param_1,param_2,param_3);
        if (iVar1 != 0) {
          FUN_435ab880(DAT_4365e820 + 0x4365e6b6,iVar1,DAT_4365e824 + 0x4365e6ba,
                       DAT_4365e828 + 0x4365e6bc,0x8d3);
          FUN_435ab880(DAT_4365e82c + 0x4365e6c4);
          uVar3 = 0x8d5;
          uVar2 = 0x4b9;
          goto LAB_4365e502;
        }
        iVar1 = FUN_43aa2be8(param_1,*(undefined4 *)(param_1 + 0x464));
      }
      *(undefined4 *)(param_1 + 0x4b4) = 1;
      *(int *)(param_1 + 0x4cc) = *(int *)(param_1 + 0x4cc) + 1;
      if (iVar1 != 0) {
        FUN_435ab880(DAT_4365e830 + 0x4365e710,iVar1,DAT_4365e834 + 0x4365e714,
                     DAT_4365e838 + 0x4365e716,0x8e7);
        FUN_435ab880(DAT_4365e83c + 0x4365e71e);
        uVar3 = 0x8e9;
        uVar2 = 0x6cb;
        goto LAB_4365e502;
      }
    }
    else {
      *(undefined4 *)(param_1 + 0x4b4) = 3;
    }
  }
  if (*(int *)(param_1 + 0x474) != 0) {
    return 0;
  }
  *(int *)(param_1 + 0x454) = *(int *)(param_1 + 0x454) + 1;
  if (*(int *)(*(int *)(*(int *)(param_2 + 0x10) + 8) + 0x80) != 1) {
    *(undefined4 *)(param_1 + 0x474) = 3;
    return 0;
  }
  iVar1 = FUN_4365cfcc(param_1,param_2);
  if (iVar1 == 0) {
    iVar1 = *(int *)(param_2 + 0x10);
    *(undefined4 *)(param_1 + 0x474) = 1;
    *(undefined4 *)(param_1 + 0x438) = *(undefined4 *)(*(int *)(iVar1 + 8) + 0x88);
    return 0;
  }
  FUN_435ab880(DAT_4365e840 + 0x4365e77e,iVar1,DAT_4365e844 + 0x4365e782,DAT_4365e848 + 0x4365e784,
               0x900);
  FUN_435ab880(DAT_4365e84c + 0x4365e78c);
  uVar3 = 0x902;
  uVar2 = 0x4ba;
LAB_4365e502:
  FUN_43639190(0x40,0,0x6012,uVar2,4,iVar1,0,uVar3);
  return iVar1;
}


/* 43660d64 */

int FUN_43660d64(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_24 [4];
  
  iVar2 = 0;
  FUN_43651208(auStack_24);
  *(undefined1 *)(param_1 + 0x1e4) = 0;
  if (*(int *)(param_1 + 0x1e0) == 2) {
    iVar2 = FUN_43a972cc(auStack_24,param_1 + 0x1b4,param_1 + 0x218);
    if (iVar2 == 0) {
      iVar2 = FUN_43a974bc(auStack_24,param_1 + 0x218);
      if (iVar2 == 0) {
        *(undefined1 *)(param_1 + 0x1e4) = 1;
        *(undefined2 *)(param_1 + 0x1ec) = *(undefined2 *)(param_1 + 0x238);
        *(uint *)(param_1 + 0x20c) = (uint)*(byte *)(param_1 + 0x229);
        *(int *)(param_1 + 0x210) = param_1 + 0x244;
        *(undefined2 *)(param_1 + 0x1ee) = *(undefined2 *)(param_1 + 0x23a);
        *(undefined4 *)(param_1 + 0x1f0) = *(undefined4 *)(param_1 + 0x23c);
        *(undefined4 *)(param_1 + 0x1e8) = *(undefined4 *)(param_1 + 8);
        *(undefined2 *)(param_1 + 0x1f8) = *(undefined2 *)(param_1 + 0x218);
        *(undefined4 *)(param_1 + 500) = *(undefined4 *)(param_1 + 0x240);
        *(undefined2 *)(param_1 + 0x1fa) = *(undefined2 *)(param_1 + 0x21a);
        *(undefined2 *)(param_1 + 0x1fc) = *(undefined2 *)(param_1 + 0x21c);
        *(undefined2 *)(param_1 + 0x1fe) = *(undefined2 *)(param_1 + 0x21e);
        *(undefined2 *)(param_1 + 0x200) = *(undefined2 *)(param_1 + 0x220);
        *(undefined2 *)(param_1 + 0x202) = *(undefined2 *)(param_1 + 0x222);
        *(undefined2 *)(param_1 + 0x204) = *(undefined2 *)(param_1 + 0x224);
        *(undefined2 *)(param_1 + 0x206) = *(undefined2 *)(param_1 + 0x226);
        *(uint *)(param_1 + 0x208) = (uint)*(byte *)(param_1 + 0x228);
        *(undefined4 *)(param_1 + 0x214) = 0;
        *(undefined4 *)(param_1 + 0x458) = *(undefined4 *)(param_1 + 0x230);
        *(undefined4 *)(param_1 + 0x45c) = *(undefined4 *)(param_1 + 0x234);
        goto LAB_43660eae;
      }
      FUN_435ab880(DAT_43660ed8 + 0x43660de8,iVar2,DAT_43660edc + 0x43660dec,
                   DAT_43660ee0 + 0x43660dee,0x81);
      FUN_435ab880(DAT_43660ee4 + 0x43660df6);
      uVar3 = 0x83;
      uVar1 = 0x2d2;
    }
    else {
      FUN_435ab880(DAT_43660ec8 + 0x43660da4,iVar2,DAT_43660ecc + 0x43660da8,
                   DAT_43660ed0 + 0x43660daa,0x78);
      FUN_435ab880(DAT_43660ed4 + 0x43660db2);
      uVar3 = 0x7a;
      uVar1 = 0x2d1;
    }
    FUN_43639190(0x40,0,0x6013,uVar1,4,iVar2,0,uVar3);
  }
LAB_43660eae:
  FUN_436511e8(auStack_24);
  return iVar2;
}


/* 436bdbfc */

undefined4 FUN_436bdbfc(int param_1,undefined4 param_2,undefined2 *param_3)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  undefined1 auStack_30 [2];
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined1 auStack_28 [12];
  
  iVar2 = FUN_43acb0a0();
  iVar3 = FUN_436bd24c(0,iVar2);
  if (iVar3 == 1) {
    iVar3 = FUN_436bd274(0,iVar2);
    if (iVar3 == param_1) {
      FUN_436bd288(param_2,iVar2);
      iVar6 = DAT_436be3b8 + 0x436bdc3e + iVar2 * 0xac;
      FUN_436bfa88(*(undefined4 *)(DAT_436be3b8 + 0x436bdc3e + iVar2 * 0xac),iVar2);
      iVar3 = DAT_436be3bc;
      FUN_436bfab0(*(undefined4 *)(iVar6 + 4),iVar2);
      FUN_436bfad8(*(undefined4 *)(iVar6 + 8),iVar2);
      FUN_436bfb00(*(undefined4 *)(iVar6 + 0xc),iVar2);
      FUN_436bfb28(*(undefined4 *)(iVar6 + 0x10),iVar2);
      FUN_436bfb50(*(undefined4 *)(iVar6 + 0x14),iVar2);
      FUN_436bfb78(*(undefined4 *)(iVar6 + 0x18),iVar2);
      FUN_436bfba0(*(undefined4 *)(iVar6 + 0x1c),iVar2);
      FUN_436bfbc8(*(undefined4 *)(iVar6 + 0x20),iVar2);
      FUN_436bfbf0(*(undefined4 *)(iVar6 + 0x24),iVar2);
      FUN_436bfc18(*(undefined4 *)(iVar6 + 0x28),iVar2);
      FUN_436bfc40(*(undefined4 *)(iVar6 + 0x2c),iVar2);
      FUN_436bfc68(*(undefined4 *)(iVar6 + 0x30),iVar2);
      FUN_436bfc90(*(undefined4 *)(iVar6 + 0x34),iVar2);
      FUN_436bfcb8(*(undefined4 *)(iVar6 + 0x38),iVar2);
      FUN_436bfce0(*(undefined4 *)(iVar6 + 0x3c),iVar2);
      FUN_436bfd08(*(undefined4 *)(iVar6 + 0x40),iVar2);
      FUN_436bfd30(*(undefined4 *)(iVar6 + 0x44),iVar2);
      FUN_436bfd58(*(undefined4 *)(iVar6 + 0x48),iVar2);
      FUN_436bfd80(*(undefined4 *)(iVar6 + 0x4c),iVar2);
      FUN_436bfda8(*(undefined4 *)(iVar6 + 0x50),iVar2);
      FUN_436bfdd4(*(undefined4 *)(iVar6 + 0x54),iVar2);
      FUN_436bfe00(*(undefined4 *)(iVar6 + 0x58),iVar2);
      FUN_436bfe2c(*(undefined4 *)(iVar6 + 0x5c),iVar2);
      FUN_436bfe58(*(undefined4 *)(iVar6 + 0x60),iVar2);
      FUN_436bfe84(*(undefined4 *)(iVar6 + 100),iVar2);
      FUN_436bfeb0(*(undefined4 *)(iVar6 + 0x68),iVar2);
      FUN_436bfedc(*(undefined4 *)(iVar6 + 0x6c),iVar2);
      FUN_436bff08(*(undefined4 *)(iVar6 + 0x70),iVar2);
      FUN_436bff34(*(undefined4 *)(iVar6 + 0x74),iVar2);
      FUN_436bff60(*(undefined4 *)(iVar6 + 0x78),iVar2);
      FUN_436bff8c(*(undefined4 *)(iVar6 + 0x7c),iVar2);
      iVar7 = iVar2 * 0x38;
      FUN_436bffb8(*(undefined4 *)(iVar6 + 0x80),iVar2);
      FUN_436bffe4(*(undefined4 *)(iVar6 + 0x84),iVar2);
      FUN_436c0010(*(undefined4 *)(iVar6 + 0x88),iVar2);
      FUN_436c003c(*(undefined4 *)(iVar6 + 0x8c),iVar2);
      FUN_436c0068(*(undefined4 *)(iVar6 + 0x90),iVar2);
      FUN_436c0094(*(undefined4 *)(iVar6 + 0x94),iVar2);
      FUN_436c00c0(*(undefined4 *)(iVar6 + 0x98),iVar2);
      FUN_436c00ec(*(undefined4 *)(iVar6 + 0x9c),iVar2);
      FUN_436c0118(*(undefined4 *)(iVar6 + 0xa0),iVar2);
      FUN_436c0144(*(undefined4 *)(iVar6 + 0xa4),iVar2);
      FUN_436c0170(*(undefined4 *)(iVar6 + 0xa8),iVar2);
      iVar5 = DAT_436be3c0 + 0x436bddc6;
      uVar4 = *(undefined4 *)(iVar5 + iVar7);
      param_3[1] = *(undefined2 *)(iVar6 + 0x14);
      iVar5 = iVar5 + iVar7;
      FUN_436c028c(uVar4,iVar2);
      FUN_436c02b4(0,iVar2);
      FUN_436c02dc(0x29c00,iVar2);
      FUN_436c0304(*(undefined4 *)(iVar5 + 0xc),iVar2);
      FUN_436c032c(*(undefined4 *)(iVar5 + 0x10),iVar2);
      FUN_436c0354(*(undefined4 *)(iVar5 + 0x14),iVar2);
      FUN_436c037c(0,iVar2);
      FUN_436c03a4(*(undefined4 *)(iVar5 + 0x1c),iVar2);
      FUN_436c03cc(*(undefined4 *)(iVar5 + 0x20),iVar2);
      FUN_436c03f4(0,iVar2);
      FUN_436c041c(*(undefined4 *)(iVar5 + 0x24),iVar2);
      FUN_436c0444(0,iVar2);
      FUN_436c046c(0,iVar2);
      FUN_436c0494(0,iVar2);
      FUN_436c04bc(0,iVar2);
      FUN_436c04e4(*(undefined4 *)(iVar5 + 0x28),iVar2);
      FUN_436c050c(*(undefined4 *)(iVar5 + 0x2c),iVar2);
      FUN_436c06d0(0,iVar2);
      FUN_436c06fc(*(undefined4 *)(iVar5 + 0x30),iVar2);
      FUN_436c0780(*(undefined4 *)(iVar5 + 0x34),iVar2);
      iVar5 = DAT_436be3c4 + 0x436bde78 + iVar2 * 0x34;
      FUN_436c0534(*(undefined4 *)(DAT_436be3c4 + 0x436bde78 + iVar2 * 0x34),iVar2);
      FUN_436c055c(*(undefined4 *)(iVar5 + 4),iVar2);
      FUN_436c0584(*(undefined4 *)(iVar5 + 8),iVar2);
      FUN_436c05ac(*(undefined4 *)(iVar5 + 0xc),iVar2);
      FUN_436c05d4(*(undefined4 *)(iVar5 + 0x10),iVar2);
      FUN_436c05fc(*(undefined4 *)(iVar5 + 0x14),iVar2);
      FUN_436c0624(*(undefined4 *)(iVar5 + 0x18),iVar2);
      FUN_436c064c(*(undefined4 *)(iVar5 + 0x1c),iVar2);
      FUN_436c0678(*(undefined4 *)(iVar5 + 0x20),iVar2);
      FUN_436c06a4(*(undefined4 *)(iVar5 + 0x24),iVar2);
      FUN_436c0728(*(undefined4 *)(iVar5 + 0x28),iVar2);
      FUN_436c0754(*(undefined4 *)(iVar5 + 0x2c),iVar2);
      FUN_436c07ac(*(undefined4 *)(iVar5 + 0x30),iVar2);
      iVar5 = DAT_436be3c8 + 0x436bdeec + iVar2 * 0x9c;
      FUN_436c07d8(*(undefined4 *)(DAT_436be3c8 + 0x436bdeec + iVar2 * 0x9c),iVar2);
      FUN_436c0800(*(undefined4 *)(iVar5 + 4),iVar2);
      FUN_436c0828(*(undefined4 *)(iVar5 + 8),iVar2);
      FUN_436c0850(*(undefined4 *)(iVar5 + 0xc),iVar2);
      FUN_436c0878(*(undefined4 *)(iVar5 + 0x10),iVar2);
      FUN_436c08a0(*(undefined4 *)(iVar5 + 0x14),iVar2);
      FUN_436c08c8(*(undefined4 *)(iVar5 + 0x18),iVar2);
      FUN_436c08f0(*(undefined4 *)(iVar5 + 0x1c),iVar2);
      FUN_436c0918(*(undefined4 *)(iVar5 + 0x20),iVar2);
      FUN_436c0940(*(undefined4 *)(iVar5 + 0x24),iVar2);
      FUN_436c0968(*(undefined4 *)(iVar5 + 0x28),iVar2);
      FUN_436c0990(*(undefined4 *)(iVar5 + 0x2c),iVar2);
      FUN_436c09b8(*(undefined4 *)(iVar5 + 0x30),iVar2);
      FUN_436c09e0(*(undefined4 *)(iVar5 + 0x34),iVar2);
      FUN_436c0a08(*(undefined4 *)(iVar5 + 0x38),iVar2);
      FUN_436c0a30(*(undefined4 *)(iVar5 + 0x3c),iVar2);
      FUN_436c0a58(*(undefined4 *)(iVar5 + 0x40),iVar2);
      FUN_436c0a80(*(undefined4 *)(iVar5 + 0x44),iVar2);
      FUN_436c0aa8(*(undefined4 *)(iVar5 + 0x48),iVar2);
      FUN_436c0ad0(*(undefined4 *)(iVar5 + 0x4c),iVar2);
      FUN_436c0af8(*(undefined4 *)(iVar5 + 0x50),iVar2);
      FUN_436c0b20(*(undefined4 *)(iVar5 + 0x54),iVar2);
      FUN_436c0b48(*(undefined4 *)(iVar5 + 0x58),iVar2);
      FUN_436c0b70(*(undefined4 *)(iVar5 + 0x5c),iVar2);
      FUN_436c0b98(*(undefined4 *)(iVar5 + 0x60),iVar2);
      FUN_436c0e00(*(undefined4 *)(iVar5 + 100),iVar2);
      FUN_436c0e2c(*(undefined4 *)(iVar5 + 0x68),iVar2);
      FUN_436c0e58(*(undefined4 *)(iVar5 + 0x6c),iVar2);
      FUN_436c0e84(*(undefined4 *)(iVar5 + 0x70),iVar2);
      FUN_436c0eb0(*(undefined4 *)(iVar5 + 0x74),iVar2);
      FUN_436c0edc(*(undefined4 *)(iVar5 + 0x78),iVar2);
      FUN_436c0f08(*(undefined4 *)(iVar5 + 0x7c),iVar2);
      FUN_436c0f34(*(undefined4 *)(iVar5 + 0x80),iVar2);
      FUN_436c0f60(*(undefined4 *)(iVar5 + 0x84),iVar2);
      FUN_436c0f8c(*(undefined4 *)(iVar5 + 0x88),iVar2);
      FUN_436c0fb8(*(undefined4 *)(iVar5 + 0x8c),iVar2);
      FUN_436c0fe4(*(undefined4 *)(iVar5 + 0x90),iVar2);
      FUN_436c1010(*(undefined4 *)(iVar5 + 0x94),iVar2);
      FUN_436c103c(*(undefined4 *)(iVar5 + 0x98),iVar2);
      iVar5 = iVar2 * 0x14;
      FUN_436c14c8(DAT_436be3cc + 0x436be03c + iVar5,iVar2);
      FUN_436c1510(DAT_436be3d0 + 0x436be04a + iVar5,iVar2);
      FUN_436c155c(DAT_436be3d4 + 0x436be056 + iVar5,iVar2);
      FUN_436c15a8(DAT_436be3d8 + 0x436be062 + iVar5,iVar2);
      FUN_436c15f0(DAT_436be3dc + 0x436be06e + iVar5,iVar2);
      iVar6 = iVar3 + 0x436bdc5e + iVar2 * 0x1a4;
      FUN_436c163c(DAT_436be3e0 + 0x436be07a + iVar5,iVar2);
      FUN_436c1750(*(undefined4 *)(iVar3 + 0x436bdc5e + iVar2 * 0x1a4),iVar2);
      FUN_436c1778(*(undefined4 *)(iVar6 + 4),iVar2);
      FUN_436c17a0(*(undefined4 *)(iVar6 + 8),iVar2);
      FUN_436c17c8(*(undefined4 *)(iVar6 + 0xc),iVar2);
      FUN_436c17f0(*(undefined4 *)(iVar6 + 0x10),iVar2);
      FUN_436c1818(*(undefined4 *)(iVar6 + 0x14),iVar2);
      FUN_436c1840(*(undefined4 *)(iVar6 + 0x18),iVar2);
      FUN_436c1868(*(undefined4 *)(iVar6 + 0x1c),iVar2);
      FUN_436c1890(*(undefined4 *)(iVar6 + 0x20),iVar2);
      FUN_436c18b8(*(undefined4 *)(iVar6 + 0x24),iVar2);
      FUN_436c18e0(*(undefined4 *)(iVar6 + 0x28),iVar2);
      FUN_436c1908(*(undefined4 *)(iVar6 + 0x2c),iVar2);
      FUN_436c1930(*(undefined4 *)(iVar6 + 0x30),iVar2);
      FUN_436c1958(*(undefined4 *)(iVar6 + 0x34),iVar2);
      FUN_436c1980(*(undefined4 *)(iVar6 + 0x38),iVar2);
      FUN_436c19a8(*(undefined4 *)(iVar6 + 0x3c),iVar2);
      FUN_436c19d0(*(undefined4 *)(iVar6 + 0x40),iVar2);
      FUN_436c19f8(*(undefined4 *)(iVar6 + 0x44),iVar2);
      FUN_436c1a20(*(undefined4 *)(iVar6 + 0x48),iVar2);
      FUN_436c1a4c(*(undefined4 *)(iVar6 + 0x4c),iVar2);
      FUN_436c1a78(*(undefined4 *)(iVar6 + 0x50),iVar2);
      FUN_436c1aa4(*(undefined4 *)(iVar6 + 0x54),iVar2);
      FUN_436c1ad0(*(undefined4 *)(iVar6 + 0x58),iVar2);
      FUN_436c1afc(*(undefined4 *)(iVar6 + 0x5c),iVar2);
      FUN_436c1b28(*(undefined4 *)(iVar6 + 0x60),iVar2);
      FUN_436c1b54(*(undefined4 *)(iVar6 + 100),iVar2);
      FUN_436c1b80(*(undefined4 *)(iVar6 + 0x68),iVar2);
      FUN_436c1bac(*(undefined4 *)(iVar6 + 0x6c),iVar2);
      FUN_436c1bd8(*(undefined4 *)(iVar6 + 0x70),iVar2);
      FUN_436c1c04(*(undefined4 *)(iVar6 + 0x74),iVar2);
      FUN_436c1c30(*(undefined4 *)(iVar6 + 0x78),iVar2);
      FUN_436c1c5c(*(undefined4 *)(iVar6 + 0x7c),iVar2);
      FUN_436c1c88(*(undefined4 *)(iVar6 + 0x80),iVar2);
      FUN_436c1cb4(*(undefined4 *)(iVar6 + 0x84),iVar2);
      FUN_436c1ce0(*(undefined4 *)(iVar6 + 0x88),iVar2);
      FUN_436c1d0c(*(undefined4 *)(iVar6 + 0x8c),iVar2);
      FUN_436c1d38(*(undefined4 *)(iVar6 + 0x90),iVar2);
      FUN_436c1d64(*(undefined4 *)(iVar6 + 0x94),iVar2);
      FUN_436c1d90(*(undefined4 *)(iVar6 + 0x98),iVar2);
      FUN_436c1dbc(*(undefined4 *)(iVar6 + 0x9c),iVar2);
      FUN_436c1de8(*(undefined4 *)(iVar6 + 0xa0),iVar2);
      FUN_436c1e14(iVar6 + 0xa4,iVar2);
      FUN_436c1e70(iVar6 + 0xe4,iVar2);
      FUN_436c1ecc(iVar6 + 0x124,iVar2);
      FUN_436c1f48(iVar6 + 0x164,iVar2);
      FUN_436bd420(iVar2 * 0xf0 + DAT_436be3e4 + 0x436be210,iVar2);
      FUN_436c133c(iVar2 * 0x370 + DAT_436be3e8 + 0x436be222,iVar2);
      iVar5 = DAT_436be3ec + 0x436be230 + iVar7;
      FUN_436c1068(*(undefined4 *)(DAT_436be3ec + 0x436be230 + iVar7),iVar2);
      FUN_436c1090(*(undefined4 *)(iVar5 + 4),iVar2);
      FUN_436c10b8(*(undefined4 *)(iVar5 + 8),iVar2);
      FUN_436c10e0(*(undefined4 *)(iVar5 + 0xc),iVar2);
      FUN_436c1108(*(undefined4 *)(iVar5 + 0x10),iVar2);
      FUN_436c1130(*(undefined4 *)(iVar5 + 0x14),iVar2);
      FUN_436c1158(*(undefined4 *)(iVar5 + 0x18),iVar2);
      FUN_436c1180(*(undefined4 *)(iVar5 + 0x1c),iVar2);
      FUN_436c11a8(*(undefined4 *)(iVar5 + 0x20),iVar2);
      FUN_436c11d0(*(undefined4 *)(iVar5 + 0x24),iVar2);
      FUN_436c11f8(*(undefined4 *)(iVar5 + 0x28),iVar2);
      FUN_436c1220(*(undefined4 *)(iVar5 + 0x2c),iVar2);
      FUN_436c1248(*(undefined4 *)(iVar5 + 0x30),iVar2);
      iVar3 = DAT_436be3f0;
      FUN_436c1270(*(undefined4 *)(iVar5 + 0x34),iVar2);
      FUN_436c1460(0,0,iVar2);
      iVar3 = iVar3 + 0x436be2b2;
      FUN_436c13c0(0,iVar2);
      FUN_436c13e8(0,iVar2);
      FUN_436c1410(0,iVar2);
      FUN_436c1438(0,iVar2);
      FUN_436c14a0(0,iVar2);
      FUN_436bf95c(*(undefined4 *)(iVar3 + iVar2 * 4),
                   *(undefined1 *)(DAT_436be3f4 + 0x436be2e0 + iVar2),auStack_28);
      thunk_FUN_439321ac(iVar2 != 0,auStack_28);
      if (iVar2 == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 2;
      }
      if (iVar2 == 0) {
        uVar8 = 1;
      }
      else {
        uVar8 = 3;
      }
      FUN_436bfa50(*(undefined4 *)(iVar3 + iVar2 * 4),auStack_30);
      FUN_43b4a64e(uVar4,auStack_30);
      uVar4 = *(undefined4 *)(iVar3 + iVar2 * 4);
      param_3[2] = uStack_2c;
      *param_3 = uStack_2e;
      FUN_436bfa6c(uVar4,auStack_30);
      FUN_43b4a64e(uVar8,auStack_30);
      iVar3 = *(int *)(iVar3 + iVar2 * 4);
      if ((iVar3 == 0) || (iVar3 == 0x11)) {
        param_3[1] = 0xf00;
        *param_3 = 0xf00;
      }
      if (*(int *)(DAT_436be3f8 + 0x436be348 + iVar2 * 4) == 0) {
        iVar3 = FUN_436bf500(iVar2,*(undefined1 *)(DAT_436be3fc + 0x436be354 + iVar2));
      }
      else {
        iVar3 = 1;
      }
      iVar5 = FUN_436bf6dc(iVar2);
      FUN_436bf470(iVar2);
      FUN_436bf664(iVar2);
      if (*(int *)(DAT_436be400 + 0x436be378 + iVar2 * 4) == 1) {
        FUN_43acb8ea(iVar2);
        FUN_436bf7d0(iVar2);
      }
      FUN_436bf3a8(iVar2);
      if ((iVar3 != 0) && (iVar5 != 0)) {
        bVar1 = *(byte *)(DAT_436be404 + 0x436be39a + iVar2);
        if (bVar1 < 2) {
          *(byte *)(DAT_436be404 + 0x436be39a + iVar2) = bVar1 + 1;
        }
      }
      FUN_43acb2e8(iVar2);
      uVar4 = 0;
    }
    else {
      uVar4 = 4;
    }
  }
  else {
    uVar4 = 2;
  }
  return uVar4;
}


/* 436be554 */

undefined4 FUN_436be554(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  char cVar7;
  undefined4 *puVar8;
  undefined1 auStack_19c [16];
  undefined4 uStack_18c;
  undefined1 auStack_12c [16];
  undefined4 uStack_11c;
  char acStack_bc [4];
  int iStack_b8;
  int iStack_b4;
  undefined1 auStack_a8 [4];
  int iStack_a4;
  uint uStack_a0;
  char acStack_94 [4];
  int iStack_90;
  int iStack_8c;
  char acStack_80 [4];
  int iStack_7c;
  int iStack_78;
  int iStack_74;
  int iStack_70;
  char acStack_6c [4];
  int iStack_68;
  uint uStack_64;
  int iStack_60;
  int iStack_5c;
  char acStack_58 [8];
  uint uStack_50;
  bool abStack_44 [4];
  int iStack_40;
  undefined4 uStack_3c;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  undefined4 auStack_24 [2];
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 != param_1) {
    return 4;
  }
  FUN_439c5320(iVar1 * 0x44 + DAT_436beae4 + 0x436be590,param_2);
  puVar8 = (undefined4 *)(iVar1 * 0x38 + DAT_436beae8 + 0x436be5a0);
  iVar2 = FUN_436bd834(param_2,puVar8);
  if (iVar2 == 0) {
    abStack_44[0] = *param_2 != 3;
    if (abStack_44[0]) {
      iStack_40 = param_2[2];
      uStack_3c = *puVar8;
    }
    FUN_436bf67c(0,abStack_44,iVar1);
  }
  else {
    FUN_436bd72c(10,0,1,DAT_436beaec + 0x436be5b8);
    FUN_43902718(DAT_436beaf0 + 0x436be5c2);
  }
  cVar7 = *(char *)(DAT_436beaf4 + 0x436be5f6 + iVar1);
  FUN_436bf4c4(0,acStack_6c,iVar1);
  if (*(int *)(DAT_436beaf8 + 0x436be602 + iVar1 * 4) == 0) {
    if (acStack_6c[0] == '\0') {
      if (cVar7 == '\0') {
        if (param_2[3] == 0) {
          iVar3 = FUN_43902df8(param_2[6],(short)param_2[5],1,auStack_12c,10);
          if (iVar3 == 0) {
            iVar2 = 0;
          }
          else {
            FUN_436bd72c(10,0,1,DAT_436beafc + 0x436be642,iVar3);
            iVar2 = 7;
            FUN_43902718(DAT_436beb00 + 0x436be650,iVar3);
          }
          uVar4 = FUN_43a3a9b4(uStack_11c,0x10,1);
          uVar4 = (param_2[3] & 1U) << 0x1e | uVar4 & 0x3fffffff;
        }
        else {
          iVar2 = 7;
          uVar4 = 0;
        }
        *(uint *)(iVar1 * 0x38 + DAT_436beb04 + 0x436be68c) = uVar4;
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          iStack_60 = param_2[0xf];
          iStack_5c = param_2[0x10];
          uStack_64 = uVar4;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,DAT_436beb08 + 0x436be68c);
        iVar2 = DAT_436beb0c + 0x436be696;
      }
      else {
        FUN_436bf4c4(1,acStack_80);
        if (acStack_80[0] != '\0') {
          iStack_68 = iStack_7c;
          iStack_60 = iStack_74;
          iStack_5c = iStack_70;
          iVar2 = DAT_436beb18 + 0x436be6f2;
LAB_436be784:
          uStack_64 = iStack_78 + 0x780;
          acStack_6c[0] = '\x01';
          *(uint *)(iVar1 * 0x38 + iVar2 + 0x14) = uStack_64;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,DAT_436beb10 + 0x436be6c6);
        iVar2 = DAT_436beb14 + 0x436be6d0;
      }
LAB_436be736:
      FUN_43902718(iVar2);
    }
    else {
LAB_436be78c:
      FUN_436bf498(0,acStack_6c,iVar1);
    }
  }
  else {
    if (acStack_6c[0] == '\0') {
      if (cVar7 == '\0') {
        iStack_28 = param_2[5];
        iStack_30 = param_2[3];
        iVar3 = DAT_436beb1c + 0x436be714;
        iStack_2c = param_2[4];
        iVar2 = FUN_436bd834(&iStack_30,iVar3 + iVar1 * 0x38 + 0x14);
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          uStack_64 = *(uint *)(iVar3 + iVar1 * 0x38 + 0x14);
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,DAT_436beb20 + 0x436be730);
        iVar2 = DAT_436beb24 + 0x436be738;
      }
      else {
        FUN_436bf4c4(1,acStack_94);
        if (acStack_94[0] != '\0') {
          iStack_68 = iStack_90;
          iVar2 = DAT_436beb30 + 0x436be786;
          iStack_78 = iStack_8c;
          goto LAB_436be784;
        }
        FUN_436bd72c(10,0,1,DAT_436beb28 + 0x436be766);
        iVar2 = DAT_436beb2c + 0x436be76e;
      }
      goto LAB_436be736;
    }
    *(uint *)(iVar1 * 0x38 + DAT_436beb34 + 0x436be7b4) = uStack_64;
  }
  iVar2 = FUN_436bf4f0(iVar1);
  FUN_436bf4c4(1,acStack_58,iVar1);
  if (acStack_58[0] == '\0') {
    iVar3 = DAT_436beb50 + 0x436be80c;
    uVar4 = 0;
LAB_436be80a:
    *(uint *)(iVar1 * 0x38 + iVar3 + 0x28) = uVar4;
  }
  else {
    if (*(char *)(DAT_436beb38 + 0x436be7c6 + iVar1) == '\0') {
      iVar3 = DAT_436beb3c + 0x436be7ce;
      uVar4 = uStack_50;
      goto LAB_436be80a;
    }
    if (uStack_50 < 0x81) {
      *(undefined4 *)(iVar1 * 0x38 + DAT_436beb44 + 0x436be816) = 0;
      FUN_436bd72c(10,0,1,DAT_436beb48 + 0x436be7fa);
      FUN_43902718(DAT_436beb4c + 0x436be802);
    }
    else {
      *(uint *)(iVar1 * 0x38 + DAT_436beb40 + 0x436be806) = uStack_50 - 0x80;
    }
  }
  if (iVar2 == 2) {
    FUN_436bf4c4(2,acStack_58,iVar1);
    if (acStack_58[0] == '\0') {
      *(undefined4 *)(iVar1 * 0x38 + DAT_436beb58 + 0x436be868) = 0;
    }
    else {
      *(uint *)(iVar1 * 0x38 + DAT_436beb54 + 0x436be85c) = uStack_50;
    }
  }
  if (*(int *)(DAT_436beb5c + 0x436be848 + iVar1 * 4) == 1) {
    if (*(char *)(DAT_436beb60 + 0x436be84a + iVar1) == '\0') {
      cVar7 = '\0';
      if (param_2[10] == 3) {
        uVar4 = (param_2[0xb] & 0xfU) << 0x18 | 0x60000000;
      }
      else {
        if (param_2[0xd] == 0) {
          iVar2 = FUN_43903280((short)param_2[0xc],0,0,auStack_19c,10);
          if (iVar2 != 0) {
            FUN_436bd72c(10,0,1,DAT_436beb64 + 0x436be8a8,iVar2);
            cVar7 = '\a';
            FUN_43902718(DAT_436beb68 + 0x436be8b4,iVar2);
          }
          uVar4 = FUN_43a3a9b4(uStack_18c,0x10,1);
        }
        else {
          uVar4 = FUN_43a3a9b4(param_2[0xd],0x10,1);
        }
        if (param_2[10] == 2) {
          uVar4 = uVar4 & 0xffffff | 0x40000000;
        }
        else {
          uVar4 = (param_2[10] & 1U) << 0x1e | uVar4 & 0x3fffffff;
        }
      }
      *(uint *)(iVar1 * 0x38 + DAT_436beb6c + 0x436be912) = uVar4;
      if (cVar7 == '\0') {
        iStack_a4 = param_2[0xc];
        uStack_a0 = uVar4;
LAB_436be94c:
        auStack_a8[0] = 1;
        FUN_436bf7e8(0,auStack_a8,iVar1);
        goto LAB_436be956;
      }
      FUN_436bd72c(10,0,1,DAT_436beb70 + 0x436be8f4);
      iVar2 = DAT_436beb74 + 0x436be8fc;
    }
    else {
      FUN_436bf818(1,acStack_bc,0);
      if (acStack_bc[0] != '\0') {
        iStack_a4 = iStack_b8;
        uStack_a0 = iStack_b4 + 0x780;
        *(uint *)(iVar1 * 0x38 + DAT_436beb80 + 0x436be978) = uStack_a0;
        goto LAB_436be94c;
      }
      FUN_436bd72c(10,0,1,DAT_436beb78 + 0x436be924);
      iVar2 = DAT_436beb7c + 0x436be92c;
    }
    FUN_43902718(iVar2);
  }
LAB_436be956:
  if (*(int *)(DAT_436beb84 + 0x436be95c + iVar1 * 4) == 1) {
    if (*(char *)(DAT_436beb88 + 0x436be968 + iVar1) != '\0') {
      iVar2 = iVar1 * 0x38 + DAT_436beb90 + 0x436be97e;
      if (*(uint *)(iVar2 + 0x14) < 0x81) {
        *(undefined4 *)(iVar2 + 0x20) = 0;
        FUN_436bd72c(10,0,1,DAT_436beb94 + 0x436be998);
        FUN_43902718(DAT_436beb98 + 0x436be9a0);
      }
      else {
        *(uint *)(iVar2 + 0x20) = *(uint *)(iVar2 + 0x14) - 0x80;
      }
      goto LAB_436be9b8;
    }
    iVar2 = iVar1 * 0x38 + DAT_436beb8c + 0x436be972;
    uVar6 = *(undefined4 *)(iVar2 + 0x14);
  }
  else {
    iVar2 = iVar1 * 0x38 + DAT_436beb9c + 0x436be9ae;
    uVar6 = *(undefined4 *)(iVar2 + 0x14);
    *(undefined4 *)(iVar2 + 0x14) = 0;
    *(undefined4 *)(iVar2 + 0x30) = uVar6;
  }
  *(undefined4 *)(iVar2 + 0x20) = uVar6;
LAB_436be9b8:
  uVar6 = FUN_43a3a9b4(param_2[0xe],0x10,1);
  iVar3 = iVar1 * 0x38 + DAT_436beba0 + 0x436be9ce;
  *(undefined4 *)(iVar3 + 0x24) = uVar6;
  iVar2 = FUN_436bf3cc(0,auStack_24,iVar1);
  if (iVar2 == 0) {
    FUN_436bd72c(10,0,1,DAT_436beba4 + 0x436be9f8);
    FUN_43902718(DAT_436beba8 + 0x436bea00);
    *(undefined4 *)(iVar3 + 0x1c) = 0;
    uVar6 = 7;
  }
  else {
    uVar6 = 0;
    uVar5 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)(iVar3 + 0x1c) = uVar5;
  }
  iVar2 = FUN_436bf3cc(1,auStack_24,iVar1);
  if (iVar2 == 0) {
    uVar6 = 7;
    FUN_436bd72c(10,0,1,DAT_436bebb8 + 0x436bea5a);
    FUN_43902718(DAT_436bebbc + 0x436bea64);
    *(undefined4 *)(iVar1 * 0x38 + DAT_436bebc0 + 0x436bea7a) = 0;
  }
  else {
    if (*(char *)(DAT_436bebac + 0x436bea1a + iVar1) == '\0') {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
      iVar3 = iVar1 * 0x38 + DAT_436bebb0 + 0x436bea2e;
    }
    else {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
      iVar3 = iVar1 * 0x38 + DAT_436bebb4 + 0x436bea44;
      iVar2 = iVar2 + -0x100;
    }
    *(int *)(iVar3 + 0xc) = iVar2;
  }
  iVar2 = FUN_436bf3cc(2,auStack_24,iVar1);
  if (iVar2 == 0) {
    iVar2 = DAT_436bebc8 + 0x436bea94;
    uVar5 = 0;
  }
  else {
    uVar5 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    iVar2 = DAT_436bebc4 + 0x436bea8e;
  }
  *(undefined4 *)(iVar1 * 0x38 + iVar2 + 0x10) = uVar5;
  if (*(int *)(DAT_436bebcc + 0x436beaa0 + iVar1 * 4) == 1) {
    FUN_436bf42c(auStack_24,iVar1);
    uVar5 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)((int)&DAT_436beaf4 + iVar1 * 0x38 + DAT_436bebd0) = uVar5;
  }
  else {
    *(undefined4 *)((int)&DAT_436beb00 + iVar1 * 0x38 + DAT_436bebd4 + 2) = 0;
  }
  return uVar6;
}


/* 436bebd8 */

undefined4 FUN_436bebd8(int param_1,undefined4 *param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 == param_1) {
    puVar6 = (undefined4 *)(iVar1 * 0x34 + DAT_436bec24 + 0x436bec04);
    uVar3 = param_2[1];
    uVar4 = param_2[2];
    uVar5 = param_2[3];
    *puVar6 = *param_2;
    puVar6[1] = uVar3;
    puVar6[2] = uVar4;
    puVar6[3] = uVar5;
    uVar3 = param_2[5];
    uVar4 = param_2[6];
    uVar5 = param_2[7];
    puVar6[4] = param_2[4];
    puVar6[5] = uVar3;
    puVar6[6] = uVar4;
    puVar6[7] = uVar5;
    uVar3 = param_2[9];
    uVar4 = param_2[10];
    uVar5 = param_2[0xb];
    puVar6[8] = param_2[8];
    puVar6[9] = uVar3;
    puVar6[10] = uVar4;
    puVar6[0xb] = uVar5;
    puVar6[0xc] = param_2[0xc];
    return 0;
  }
  return 4;
}


/* 436bec28 */

undefined4 FUN_436bec28(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 1;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 == param_1) {
    if (*param_2 != *(int *)(DAT_436bec70 + 0x436bec56 + iVar1 * 4)) {
      *(int *)(DAT_436bec70 + 0x436bec56 + iVar1 * 4) = *param_2;
      return 0;
    }
    return 1;
  }
  return 1;
}


/* 4378e938 */

int FUN_4378e938(void)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = *(int *)(DAT_4378e9bc + 0x4378e946);
  iVar4 = *(int *)(iVar5 + 0x28) * (*(byte *)(DAT_4378e9c0 + 0x43790424) - 1) + *(int *)(iVar5 + 8);
  iVar3 = *(int *)(DAT_4378e9c4 + 0x4378e94e + DAT_4378e9c8);
  if (*(char *)(DAT_4378e9c0 + 0x4378ef1d) == '\0') {
    if ((*(byte *)(*(int *)(DAT_4378e9bc + 0x4378e94a) + 0x264) & 8) == 0) {
      if (*(int *)(DAT_4378e9c0 + 0x4378ef16) == 0) {
        uVar2 = (uint)*(byte *)(iVar3 + 0x1a);
      }
      else {
        uVar2 = (uint)*(byte *)(iVar3 + 0x19);
      }
    }
    else {
      if (*(int *)(DAT_4378e9c0 + 0x4378ef16) == 0) {
        return (uint)*(byte *)(iVar3 + 0x18) * -200 + iVar4;
      }
      if (*(int *)(iVar5 + 0xc) != 1) {
        return (uint)*(byte *)(iVar3 + 0x15) * -200 + iVar4;
      }
      uVar2 = (uint)*(byte *)(iVar3 + 0x14);
    }
  }
  else {
    if (*(int *)(iVar5 + 0xc) == 1) {
      bVar1 = *(byte *)(iVar3 + 0x16);
    }
    else {
      bVar1 = *(byte *)(iVar3 + 0x17);
    }
    uVar2 = (uint)bVar1;
  }
  return uVar2 * -200 + iVar4;
}


/* 4378ea78 */

void FUN_4378ea78(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iStack_28;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined4 uStack_14;
  
  iVar1 = DAT_4378eb60;
  puVar4 = (undefined4 *)(DAT_4378eb58 + 0x4378ea88);
  FUN_439c5320(puVar4,DAT_4378eb5c + 0x4378ea8e,0x44);
  iVar2 = DAT_4378eb64;
  uVar3 = *puVar4;
  *(undefined1 *)(DAT_4378eb64 + 0x4378f07e) = 4;
  *(undefined4 *)(iVar2 + 0x4378f082) = uVar3;
  FUN_437957ec(uVar3,*(undefined1 *)(iVar2 + 0x4378f1fa),*(undefined1 *)(iVar2 + 0x4378f1fb),
               iVar2 + 0x4378f0f6,iVar2 + 0x4378f2de);
  FUN_4378e334(*(undefined4 *)(iVar1 + 0x4378ea9c + DAT_4378eb68),DAT_4378eb6c + 0x4378eac8,param_1)
  ;
  iStack_28 = FUN_437955ec();
  iVar1 = DAT_4378eb70;
  if (((iStack_28 != 1) && (iStack_28 != 2)) && (iStack_28 != 0)) {
    iStack_28 = 0;
  }
  uStack_24 = *(undefined2 *)(DAT_4378eb70 + 0x4378f32e);
  uStack_22 = *(undefined2 *)(DAT_4378eb70 + 0x4378f332);
  uStack_20 = *(undefined2 *)((int)&DAT_4378f350 + DAT_4378eb70 + 2);
  uStack_1e = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f6);
  uStack_1c = *(undefined2 *)(DAT_4378eb70 + 0x4378f1f8);
  uStack_1a = *(undefined2 *)(DAT_4378eb70 + 0x4378f1fa);
  uStack_18 = *(undefined2 *)(DAT_4378eb70 + 0x4378f240);
  uStack_16 = *(undefined2 *)(DAT_4378eb70 + 0x4378f242);
  thunk_FUN_43ae6916(&iStack_28,&uStack_14);
  FUN_43795d38(uStack_14);
  if ((*(ushort *)(*(int *)(DAT_4378eb74 + 0x4378eb40) + 0x264) & 0x1c0) == 0) {
    uVar3 = FUN_43794a78();
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = uVar3;
  }
  else {
    *(undefined4 *)(&LAB_4378f2ea + iVar1) = 0;
  }
  return;
}


/* 4378f9b4 */

undefined * FUN_4378f9b4(void)

{
  return &UNK_4378f9ba + DAT_4378f9bc;
}


/* 4378fa70 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void candidate_4378fa70(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined2 *puVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined1 auStack_134 [68];
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_30;
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  
  iVar1 = _DAT_4378fd64;
  iVar8 = _DAT_4378fd5c + 0x4378fa84;
  iVar6 = *(int *)(iVar8 + _DAT_4378fd60);
  puVar5 = (undefined2 *)(_DAT_4378fd64 + 0x4378fa90);
  *(undefined4 *)(_DAT_4378fd64 + 0x43790050) = 0;
  uVar4 = *(undefined4 *)(iVar6 + 0x40);
  *(undefined4 *)(iVar1 + 0x4379005c) = 0;
  *(undefined1 *)(iVar1 + 0x43790058) = 0;
  *(undefined4 *)(iVar1 + 0x43790034) = uVar4;
  *(int *)(iVar1 + 0x43790d1c) = _DAT_4378fd68 + 0x4378fab0;
  *(undefined4 *)(_DAT_4378fd6c + 0x4378fab6) = param_2;
  *(undefined4 *)(iVar1 + 0x43790054) = 2;
  uStack_30 = 0xb;
  uStack_2c = FUN_4378de7c();
  uStack_2a = 0;
  uStack_2b = 0;
  uVar4 = FUN_436d6118();
  FUN_436d61a4(uVar4,&uStack_30,auStack_134);
  *(undefined4 *)(iVar1 + 0x43790060) = 1;
  *(undefined4 *)(iVar1 + 0x4379003c) = uStack_cc;
  *(undefined1 *)(iVar1 + 0x43791570) = 1;
  *(undefined4 *)(iVar1 + 0x43790070) = 1;
  *(undefined4 *)(iVar1 + 0x43790038) = uStack_d0;
  *(undefined4 *)(iVar1 + 0x4379021c) = 0;
  *(undefined1 *)(iVar1 + 0x43790065) = 1;
  *(undefined4 *)(iVar1 + 0x43790040) = uStack_c8;
  *(undefined1 *)(iVar1 + 0x43790220) = 1;
  *(undefined1 *)(iVar1 + 0x43790221) = 1;
  *(undefined4 *)(iVar1 + 0x43790048) = uStack_ec;
  *(undefined1 *)(iVar1 + 0x43790064) = 0;
  *(undefined1 *)(iVar1 + 0x43790075) = 0;
  *(undefined4 *)(iVar1 + 0x43790044) = uStack_f0;
  *(undefined2 *)(iVar1 + 0x43791572) = 0;
  *(undefined2 *)(iVar1 + 0x43791574) = 0;
  *(undefined4 *)(iVar1 + 0x4379004c) = uStack_e8;
  *(undefined4 *)(iVar1 + 0x43790068) = 1;
  *(undefined1 *)(iVar1 + 0x4379156e) = 4;
  *(undefined1 *)(iVar1 + 0x43790074) = 4;
  *(undefined4 *)(iVar1 + 0x43790224) = 1;
  *(undefined4 *)(iVar1 + 0x4379022c) = 0;
  *(undefined1 *)(iVar1 + 0x4379006d) = 1;
  *(undefined1 *)(iVar1 + 0x43790230) = 1;
  *(undefined1 *)(iVar1 + 0x4379006c) = 0;
  *(undefined1 *)(iVar1 + 0x43790228) = 0;
  *(undefined2 *)(iVar1 + 0x43791576) = 0;
  *(undefined2 *)(iVar1 + 0x43791578) = 0;
  *(undefined4 *)(iVar1 + 0x43790078) = 0x11;
  *(undefined1 *)(iVar1 + 0x437901f0) = 0;
  *(undefined1 *)(iVar1 + 0x437901f1) = 0;
  FUN_439c5320(iVar1 + 0x4379007c,param_1,0x70);
  iVar2 = _DAT_4378fd70;
  *(undefined4 *)(iVar1 + 0x43790208) = *(undefined4 *)(iVar6 + 0x50);
  uVar4 = FUN_43ae8c50();
  *(undefined1 *)(iVar1 + 0x43790210) = 0;
  *(undefined4 *)(iVar1 + 0x43790214) = 0;
  *(undefined4 *)(iVar1 + 0x43790218) = 1;
  *(undefined1 *)(iVar1 + 0x43790066) = 0;
  *(undefined4 *)(iVar1 + 0x4379023c) = 0;
  *(undefined1 *)(iVar1 + 0x437902c4) = 0;
  *(undefined2 *)(iVar1 + 0x437902c6) = 0;
  *(undefined2 *)(iVar1 + 0x437902c8) = 0;
  *(undefined2 *)(iVar1 + 0x437902ca) = 0;
  *(undefined2 *)(iVar1 + 0x437902cc) = 0;
  *(undefined4 *)(iVar1 + 0x4379027c) = 0;
  *(undefined4 *)(iVar1 + 0x43790240) = 0;
  *(undefined4 *)(iVar1 + 0x43790244) = 0;
  *(undefined4 *)(iVar1 + 0x4379020c) = uVar4;
  uVar3 = FUN_437fc54c(0);
  *puVar5 = uVar3;
  uVar3 = FUN_437fc54c(0);
  *(undefined1 *)(iVar1 + 0x43790278) = 0;
  *(undefined1 *)(iVar1 + 0x43791a5c) = 1;
  *(undefined1 *)(iVar1 + 0x43790279) = 0;
  *(undefined1 *)(iVar1 + 0x43791949) = 0;
  *(undefined4 *)(iVar1 + 0x43790290) = 0;
  *(undefined1 *)(iVar1 + 0x43791958) = 1;
  *(undefined1 *)(iVar1 + 0x437902ce) = 0;
  *(undefined4 *)(iVar1 + 0x437902a4) = 1;
  *(undefined4 *)(iVar1 + 0x437902a8) = 1;
  *(undefined2 *)(iVar1 + 0x437902ac) = 0;
  *(undefined2 *)(iVar1 + 0x437902ae) = 0;
  *(undefined2 *)(iVar1 + 0x437902b0) = 0;
  *(undefined2 *)(iVar1 + 0x437902b2) = 0;
  *(undefined2 *)(iVar1 + 0x437902b4) = 0;
  *(undefined2 *)(iVar1 + 0x437902b6) = 0;
  *(undefined2 *)(iVar1 + 0x437902b8) = 0;
  *(undefined2 *)(iVar1 + 0x437902ba) = 0;
  *(undefined2 *)(iVar1 + 0x437902bc) = 0;
  *(undefined2 *)(iVar1 + 0x437902be) = 0;
  *(undefined2 *)(iVar1 + 0x437902c0) = 0;
  *(undefined2 *)(iVar1 + 0x437902c2) = 0;
  *(undefined2 *)(iVar1 + 0x437902a0) = uVar3;
  *(undefined2 *)(iVar1 + 0x43790258) = uVar3;
  *(undefined2 *)(iVar1 + 0x43790274) = uVar3;
  uVar4 = FUN_4377fdf8();
  *(undefined4 *)(iVar1 + 0x437918dc) = uVar4;
  uVar4 = FUN_437b4d64();
  *(undefined4 *)(iVar1 + 0x437918e0) = uVar4;
  uVar4 = FUN_437c1440();
  *(undefined4 *)(iVar1 + 0x437918e4) = uVar4;
  uVar4 = FUN_4379fc20();
  *(undefined4 *)(iVar1 + 0x437918e8) = uVar4;
  uVar4 = FUN_437d0bc8();
  *(undefined4 *)(iVar1 + 0x437918ec) = uVar4;
  uVar4 = FUN_437d9930();
  *(undefined4 *)(&LAB_437918f0 + iVar1) = uVar4;
  uVar4 = FUN_437b6614();
  *(undefined4 *)(iVar1 + 0x437918f4) = uVar4;
  uVar4 = FUN_437b8230();
  *(undefined4 *)(iVar1 + 0x437918f8) = uVar4;
  iVar6 = _DAT_4378fd74;
  FUN_43ae8eae(puVar5,iVar2 + 0x4378fb8e);
  puVar7 = (undefined4 *)(iVar6 + 0x4378fc90);
  candidate_4380e3f4(puVar7);
  FUN_439c5320(_DAT_4378fd78 + 0x4378fca2,puVar7,0x44);
  FUN_439c5320(_DAT_4378fd7c + 0x4378fcb6,puVar7,0x44);
  uVar4 = *puVar7;
  *(undefined1 *)(iVar1 + 0x43790074) = 4;
  *(undefined4 *)(iVar1 + 0x43790078) = uVar4;
  FUN_437957ec(uVar4,*(undefined1 *)(iVar1 + 0x437901f0),*(undefined1 *)(iVar1 + 0x437901f1),
               iVar1 + 0x437900ec,iVar1 + 0x437902d4);
  FUN_4378e334(*(undefined4 *)(iVar8 + _DAT_4378fd80),iVar2 + 0x4378fb8e,1);
  *(undefined1 *)(iVar1 + 0x43791571) = 0;
  *(undefined4 *)(iVar1 + 0x437901f4) = 0;
  *(undefined4 *)(iVar1 + 0x437901f8) = 0;
  *(undefined4 *)(iVar1 + 0x437902d0) = 1;
  FUN_43560da8(0x1a,_DAT_4378fd58);
  FUN_43560dc4(0x11,0);
  func_0x43901788();
  func_0x437fe208();
  FUN_4378c4d0(iVar1 + 0x43790034);
  FUN_43b2a162(_DAT_4378fd84 + 0x4378fd26);
  FUN_43b2a162(_DAT_4378fd88 + 0x4378fd2e);
  FUN_43b2a162(_DAT_4378fd8c + 0x4378fd36);
  FUN_43b2a162(_DAT_4378fd90 + 0x4378fd3e);
  FUN_43b2a162(_DAT_4378fd94 + 0x4378fd46);
  FUN_43b2a162(_DAT_4378fd98 + 0x4378fd4e);
  return;
}


/* 4378fef4 */

void candidate_4378fef4(uint param_1)

{
  byte bVar1;
  char cVar2;
  ushort uVar3;
  byte bVar4;
  undefined1 uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  short sVar9;
  short sVar10;
  uint uVar11;
  undefined1 *puVar12;
  int iVar13;
  uint uVar14;
  short *psVar15;
  int iVar16;
  undefined1 auStack_50 [20];
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 auStack_30 [4];
  uint uStack_2c;
  undefined1 auStack_28 [4];
  int aiStack_24 [2];
  
  iVar16 = DAT_437908e8 + 0x4378ff08;
  iVar13 = *(int *)(iVar16 + DAT_437908ec);
  if (((*(byte *)(iVar13 + 0x12) & 1) != 0) &&
     (uVar11 = (uint)*(byte *)((int)&DAT_437919f8 + DAT_437908f0 + 1), uVar11 < 4)) {
                    /* WARNING: Could not recover jumptable at 0x4378ff22. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_4378ff22::switchdataD_4378ff26 +
              (uint)(&switchD_4378ff22::switchdataD_4378ff26)[uVar11] * 2))();
    return;
  }
  uVar11 = param_1 >> 8;
  param_1 = param_1 & 0xff;
  if ((uVar11 != **(uint **)(DAT_43790904 + 0x4378ff60)) ||
     (param_1 != *(byte *)(DAT_43790908 + 0x43791a49))) {
    iVar6 = thunk_FUN_436cd00c();
    iVar7 = DAT_43790910;
    iVar16 = DAT_4379090c;
    uVar14 = (uint)(iVar6 - (*(undefined4 **)(DAT_4379090c + 0x4378ff88))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43790914 + 0x4378ffa6,uVar11,param_1,
                 **(undefined4 **)(DAT_4379090c + 0x4378ff88),
                 *(undefined1 *)(DAT_43790910 + 0x43791a67),uVar14);
    FUN_43902718(DAT_43790918 + 0x4378ffc4,uVar11,param_1,**(undefined4 **)(iVar16 + 0x4378ff88),
                 *(undefined1 *)(iVar7 + 0x43791a67),uVar14);
    if (param_1 < 4) {
      uVar8 = *(undefined4 *)(DAT_4379091c + 0x4378ffd6 + param_1 * 4);
    }
    else {
      uVar8 = 7;
    }
    FUN_4378f988(3,uVar8,uVar14);
    if ((*(byte *)(iVar13 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43790920 + 0x4378fff4);
    }
    if ((*(byte *)(iVar13 + 0x1b) & 0x20) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  if (*(char *)(DAT_43790908 + 0x43791a4a) != '\0') {
    FUN_43acad44();
  }
  FUN_43ae1292(4);
  iVar7 = FUN_43ae8d4e();
  if (iVar7 == 0) {
    FUN_43901778();
    if (*(char *)(DAT_43790924 + 0x4379002c) != '\0') {
      *(undefined1 *)(DAT_43790928 + 0x43790038) = 1;
    }
    uVar5 = 0;
    puVar12 = (undefined1 *)(DAT_4379092c + 0x43790042);
  }
  else {
    uVar5 = 1;
    puVar12 = (undefined1 *)(DAT_43790930 + 0x4379004c);
  }
  iVar7 = DAT_43790934;
  *puVar12 = uVar5;
  FUN_4378f7a0(0xf7c);
  if (*(char *)(iVar7 + 0x43791b38) != '\0') {
    FUN_43560e00(0x11,auStack_30);
    if ((uStack_2c & 2) == 0) {
      uVar8 = FUN_437c1440();
      iVar6 = DAT_43790938 + 0x43790086;
      *(undefined4 *)(iVar7 + 0x43791eac) = uVar8;
      FUN_43ae8e44(iVar7 + 0x43790058,iVar6);
    }
    if (*(char *)(DAT_4379093c + 0x43790094) == '\0') {
      *(uint *)(DAT_43790940 + 0x437908a4) =
           uStack_2c & 2 | *(uint *)(DAT_43790940 + 0x437908a4) & 0xfffffffd;
      if (*(short *)(DAT_43790944 + 0x437900ba) != 0) {
        if ((uStack_2c & 2) == 0) {
          iVar7 = DAT_43790948 + 0x437900ca;
          sVar9 = 0;
        }
        else {
          *(short *)(DAT_4379094c + 0x437900d4) = *(short *)(DAT_4379094c + 0x437900d4) + 1;
          iVar7 = DAT_43790950 + 0x437900de;
          sVar9 = *(short *)(DAT_43790950 + 0x437900e0) + 1;
        }
        *(short *)(iVar7 + 2) = sVar9;
      }
    }
    sVar9 = *(short *)(DAT_43790954 + 0x437900ea);
    if ((sVar9 != 0) || (*(char *)(iVar13 + 0xe) != '\0')) {
      if (*(short *)(DAT_43790958 + 0x437900fc) != sVar9) {
        iVar7 = 0;
        do {
          *(undefined2 *)(DAT_4379095c + 0x4379010c + iVar7) = 0;
          *(undefined2 *)(DAT_43790960 + 0x43790114 + iVar7) = 0;
          *(undefined2 *)(DAT_43790964 + 0x4379011c + iVar7) = 0;
          iVar7 = iVar7 + 2;
        } while (iVar7 != 0x1a);
        *(short *)(DAT_43790968 + 0x4379012a) = sVar9;
      }
      iVar7 = DAT_43790970;
      if ((sVar9 != 0) && (*(short *)(DAT_4379096c + 0x43790136) == sVar9)) {
        if ((*(byte *)(iVar13 + 0xe) & 1) != 0) {
          FUN_4378eb78(3,9,1,DAT_43790974 + 0x43790174,sVar9,
                       *(undefined2 *)(DAT_43790970 + 0x4379015e),
                       *(undefined2 *)(DAT_43790970 + 0x43790154),
                       *(undefined2 *)(DAT_43790970 + 0x43790152),
                       *(undefined2 *)(DAT_43790970 + 0x43790156),
                       *(undefined2 *)(DAT_43790970 + 0x4379015c),
                       *(undefined2 *)(DAT_43790970 + 0x4379015a),
                       *(undefined2 *)(DAT_43790970 + 0x43790162));
          FUN_43902718(DAT_4379097c + 0x4379019e,*(undefined2 *)(DAT_43790978 + 0x43790180),
                       *(undefined2 *)(iVar7 + 0x4379015e),*(undefined2 *)(iVar7 + 0x43790154),
                       *(undefined2 *)(iVar7 + 0x43790152),*(undefined2 *)(iVar7 + 0x43790156),
                       *(undefined2 *)(iVar7 + 0x4379015c),*(undefined2 *)(iVar7 + 0x4379015a),
                       *(undefined2 *)(iVar7 + 0x43790162));
        }
        iVar7 = DAT_43790980;
        FUN_43900368(0,(uint)*(ushort *)(DAT_43790980 + 0x437901ae) * 0x10000 +
                       (uint)*(ushort *)(DAT_43790980 + 0x437901ac));
        FUN_43900368(1,(uint)*(ushort *)(iVar7 + 0x437901b0) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x437901b6));
        FUN_43900368(2,(uint)*(ushort *)(iVar7 + 0x437901b4) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x437901bc));
        FUN_43900368(3,(uint)*(ushort *)(iVar7 + 0x437901b8) << 0x10);
      }
      iVar7 = 0;
      do {
        uVar3 = *(ushort *)(DAT_43790984 + 0x437901e4 + iVar7);
        if (*(ushort *)(DAT_43790988 + 0x437901ec + iVar7) < uVar3) {
          *(ushort *)(DAT_43790988 + 0x437901ec + iVar7) = uVar3;
        }
        iVar6 = DAT_43790994;
        iVar7 = iVar7 + 2;
      } while (iVar7 != 0x1a);
      psVar15 = (short *)(DAT_4379098c + 0x43790200);
      sVar9 = *psVar15;
      if ((sVar9 != 0) && (*(short *)(DAT_43790990 + 0x4379020c) == sVar9)) {
        if ((*(byte *)(iVar13 + 0xe) & 2) != 0) {
          FUN_4378eb78(3,9,1,DAT_43790998 + 0x4379024a,*(short *)(DAT_43790990 + 0x4379020c),
                       *(undefined2 *)(DAT_43790994 + 0x43790234),
                       *(undefined2 *)(DAT_43790994 + 0x4379022a),
                       *(undefined2 *)(DAT_43790994 + 0x43790228),
                       *(undefined2 *)(DAT_43790994 + 0x4379022c),
                       *(undefined2 *)(DAT_43790994 + 0x43790232),
                       *(undefined2 *)(DAT_43790994 + 0x43790230),
                       *(undefined2 *)(DAT_43790994 + 0x43790238));
          FUN_43902718(DAT_4379099c + 0x4379026e,*psVar15,*(undefined2 *)(iVar6 + 0x43790234),
                       *(undefined2 *)(iVar6 + 0x4379022a),*(undefined2 *)(iVar6 + 0x43790228),
                       *(undefined2 *)(iVar6 + 0x4379022c),*(undefined2 *)(iVar6 + 0x43790232),
                       *(undefined2 *)(iVar6 + 0x43790230),*(undefined2 *)(iVar6 + 0x43790238));
        }
        iVar7 = DAT_437909a0;
        FUN_43900368(4,(uint)*(ushort *)(DAT_437909a0 + 0x4379027e) * 0x10000 +
                       (uint)*(ushort *)(DAT_437909a0 + 0x4379027c));
        FUN_43900368(5,(uint)*(ushort *)(iVar7 + 0x43790280) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x43790286));
        FUN_43900368(6,(uint)*(ushort *)(iVar7 + 0x43790284) * 0x10000 +
                       (uint)*(ushort *)(iVar7 + 0x4379028c));
        FUN_43900368(7,(uint)*(ushort *)(iVar7 + 0x43790288) << 0x10);
      }
      iVar7 = DAT_437909a4;
      if ((((*(byte *)(iVar13 + 0xe) & 4) != 0) &&
          (uVar14 = *(uint *)((int)&DAT_43790abc + DAT_437909a4 + 2), uVar14 != 0)) &&
         ((uVar14 & 0x6e) != 0)) {
        FUN_4378eb78(3,9,1,DAT_437909a8 + 0x437902d4,uVar14);
        FUN_43902718(DAT_437909ac + 0x437902e2,*(undefined4 *)((int)&DAT_43790abc + iVar7 + 2));
      }
    }
    FUN_439c5320(DAT_437909b0 + 0x437902f2,DAT_437909b4 + 0x437902f4,0x44);
  }
  uVar5 = FUN_43ae8ccc(*(undefined4 *)(iVar16 + DAT_437909b8));
  iVar16 = DAT_437909bc;
  bVar4 = *(byte *)(DAT_437909bc + 0x437908de);
  sVar9 = *(short *)(DAT_437909bc + 0x43791dec);
  sVar10 = (ushort)bVar4 * 0x100;
  *(short *)(DAT_437909bc + 0x43791dec) = sVar10;
  *(undefined1 *)(iVar16 + 0x43791deb) = uVar5;
  iVar7 = *(int *)(DAT_437909c0 + 0x4379032a);
  if (*(int *)(iVar7 + 0x2c) == 0) {
    bVar1 = *(byte *)(iVar16 + 0x43791de9);
    if (*(int *)(iVar16 + 0x437908ae) == 1) {
      bVar1 = bVar1 >> 1;
    }
    *(ushort *)(iVar16 + 0x43791dec) = sVar10 + (ushort)bVar1;
  }
  if ((*(char *)(iVar7 + 0x1ed) == '\0') ||
     (*(char *)(*(int *)(DAT_437909c4 + 0x4379036c) + 2) == '\0')) {
    if (*(int *)(iVar7 + 0x2c) == 0) {
      iVar16 = DAT_437909cc + 0x43791e2e;
      if (*(int *)((int)&DAT_43790910 + DAT_437909cc + 2) == 1) {
        sVar10 = sVar10 + (short)(*(byte *)(DAT_437909cc + 0x43791e4d) + 1 >> 1);
      }
      else {
        sVar10 = sVar10 + *(byte *)(DAT_437909cc + 0x43791e4d) + 1;
      }
    }
    else {
      iVar16 = DAT_437909d0 + 0x43791e52;
    }
    *(short *)(iVar16 + 0x24) = sVar10;
  }
  else {
    *(ushort *)(DAT_437909c8 + 0x43791e3e) = (bVar4 + 1) * 0x100;
  }
  iVar6 = FUN_437955ec();
  iVar7 = DAT_437909d8;
  iVar16 = DAT_437909d4;
  if (iVar6 == 0) {
    sVar10 = (ushort)*(byte *)((int)&DAT_43790980 + DAT_437909d4) << 8;
    *(short *)(DAT_437909d4 + 0x43791e8a) = sVar10;
    *(short *)(iVar16 + 0x43791e8c) = sVar10;
  }
  else {
    iVar16 = *(int *)((int)&DAT_43790990 + DAT_437909d8 + 2);
    sVar10 = (ushort)*(byte *)((int)&DAT_43790994 + DAT_437909d8 + 2) * 0x100;
    *(short *)(DAT_437909d8 + 0x43791ea0) = sVar10;
    if (iVar16 == 0) {
      bVar4 = *(byte *)(iVar7 + 0x43791e99);
      if (*(int *)((int)&DAT_4379095c + iVar7 + 2) == 1) {
        bVar4 = bVar4 >> 1;
      }
      *(ushort *)(iVar7 + 0x43791ea0) = sVar10 + (ushort)bVar4;
    }
    if ((*(char *)(DAT_437909dc + 0x43790b84) == '\0') ||
       (*(char *)(DAT_437909dc + 0x43791ec4) == '\0')) {
      iVar16 = DAT_437909e0 + 0x43791ec2;
      if (*(int *)((int)&DAT_437909d8 + DAT_437909e0 + 2) != 0) {
        bVar4 = *(byte *)((int)&DAT_437909dc + DAT_437909e0 + 2);
        goto LAB_43790430;
      }
      bVar4 = *(byte *)((int)&DAT_437909dc + DAT_437909e0 + 2);
      if (*(int *)((int)&DAT_437909a4 + DAT_437909e0 + 2) == 1) {
        sVar10 = (ushort)bVar4 * 0x100 + (short)(*(byte *)(DAT_437909e0 + 0x43791ee1) + 1 >> 1);
      }
      else {
        sVar10 = *(byte *)(DAT_437909e0 + 0x43791ee1) + 1 + (ushort)bVar4 * 0x100;
      }
    }
    else {
      iVar16 = DAT_437909dc + 0x43791ea4;
      bVar4 = *(byte *)(DAT_437909dc + 0x43790b7c);
LAB_43790430:
      sVar10 = (ushort)bVar4 << 8;
    }
    *(short *)(iVar16 + 0x28) = sVar10;
  }
  iVar16 = DAT_437909e4;
  sVar10 = *(short *)(DAT_437909e4 + 0x43791f1e);
  if ((sVar9 != sVar10) && (*(char *)(iVar13 + 0x70) == '\0')) {
    FUN_439c5a04(&uStack_3c,0,0xc);
    uStack_38 = **(undefined4 **)(DAT_437909e8 + 0x4379046e);
    uStack_3c._0_3_ = CONCAT12(1,sVar10);
    uStack_34 = *(undefined4 *)((int)&DAT_43790a0c + iVar16);
    FUN_43b71696(uStack_3c,uStack_38,uStack_34);
  }
  iVar16 = DAT_437909ec;
  FUN_437999e4(1,0xd);
  FUN_437957a0();
  FUN_4378f7a0(0x105e);
  iVar7 = DAT_437909f0;
  if (*(char *)(*(int *)(iVar16 + 0x437904b2) + 2) != '\0') {
    if (((*(byte *)(DAT_437909f0 + 0x43790cba) & 1) != 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,DAT_437909f4 + 0x437904f2,**(undefined4 **)(iVar16 + 0x43790496),
                   *(undefined1 *)(iVar7 + 0x43791f8b),uStack_2c);
      FUN_43902718(DAT_437909f8 + 0x43790502,**(undefined4 **)(iVar16 + 0x43790496),
                   *(undefined1 *)(iVar7 + 0x43791f8b),uStack_2c);
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_437909fc + 0x4379051e);
    }
    thunk_FUN_43ae74ca(DAT_43790a04 + 0x4379052e,DAT_43790a00 + 0x4379226c);
  }
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a08 + 0x43790544);
  }
  FUN_437d99a4(DAT_43790a10 + 0x43790558,DAT_43790a0c + 0x4379238e);
  FUN_4378f7a0(0x1073);
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a14 + 0x43790574);
  }
  iVar7 = DAT_43790a1c;
  iVar16 = DAT_43790a18;
  FUN_437b4e88(DAT_43790a1c + 0x43790584,DAT_43790a18 + 0x4379206e);
  FUN_4378f7a0(0x1078);
  iVar6 = thunk_FUN_43adaaf6();
  if (((iVar6 != 0) && ((*(byte *)(iVar16 + 0x43790d8e) & 0x40) == 0)) &&
     (iVar6 = FUN_43560de0(0x1a,1,0,auStack_28,1), iVar6 != 0)) {
    FUN_43560e00(0x1a,auStack_30);
    FUN_4378eb78(3,9,1,DAT_43790a20 + 0x437905e0,**(undefined4 **)(iVar7 + 0x43790588),
                 *(undefined1 *)((int)&DAT_43792060 + iVar16 + 1),uStack_2c);
    FUN_43902718(DAT_43790a24 + 0x437905f2,**(undefined4 **)(iVar7 + 0x43790588),
                 *(undefined1 *)((int)&DAT_43792060 + iVar16 + 1),uStack_2c);
    FUN_43560da8(0x1a,3);
  }
  if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
    FUN_43561540(DAT_43790a28 + 0x4379060e);
  }
  iVar16 = DAT_43790a30;
  aiStack_24[0] = DAT_43790a34 + 0x4379062a;
  FUN_437c1fcc(DAT_43790a30 + 0x43790624,DAT_43790a2c + 0x437921ee,aiStack_24);
  if (*(char *)(*(int *)(iVar16 + 0x43790644) + 2) != '\0') {
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_43790a38 + 0x4379064a);
    }
    iVar16 = DAT_43790a3c;
    FUN_43721840();
    if (((*(uint *)(iVar16 + 0x43790e64) & DAT_437908e4) == 0) &&
       (iVar6 = FUN_43560de0(0x1a,2,0,auStack_28,1), iVar7 = DAT_43790a40, iVar6 != 0)) {
      FUN_43560e00(0x1a,auStack_30);
      FUN_4378eb78(3,9,1,DAT_43790a44 + 0x4379069e,**(undefined4 **)(iVar7 + 0x43790686),
                   *(undefined1 *)(iVar16 + 0x43792137),uStack_2c);
      FUN_43902718(DAT_43790a48 + 0x437906ac,**(undefined4 **)(iVar7 + 0x43790686),
                   *(undefined1 *)(iVar16 + 0x43792137),uStack_2c);
      FUN_43560da8(0x1a,3);
    }
    if ((*(byte *)(iVar13 + 0x12) & 8) != 0) {
      FUN_43561540(DAT_43790a4c + 0x437906c6);
    }
    thunk_FUN_4377f210(DAT_43790a54 + 0x437906d2,DAT_43790a50 + 0x43792410);
  }
  iVar7 = DAT_43790a5c;
  iVar16 = DAT_43790a58;
  if (*(char *)(*(int *)(DAT_43790a58 + 0x437906fe) + 2) != '\0') {
    FUN_437fc56c(0,*(undefined2 *)(*(int *)(DAT_43790a58 + 0x437906e6) + 0x26c));
    FUN_437fc56c(2,**(undefined2 **)(iVar16 + 0x437906ea));
    FUN_437fc56c(1,*(undefined2 *)(*(int *)(iVar16 + 0x43790716) + 0x14));
    FUN_437fc56c(3,**(undefined2 **)(iVar16 + 0x4379071a));
    FUN_437fc56c(4,**(undefined2 **)(iVar16 + 0x4379070a));
    FUN_437fc56c(6,*(undefined2 *)(*(int *)(iVar16 + 0x437906f2) + 0x2c));
    FUN_437fc56c(8,**(undefined2 **)(iVar16 + 0x437906fa));
    FUN_437fc56c(10,*(undefined2 *)(iVar7 + 0x437921cc));
    FUN_437fc56c(9,**(undefined2 **)(iVar16 + 0x4379072a));
    uVar8 = FUN_4377e500();
    FUN_437fc56c(0xb,uVar8);
    FUN_437fc56c(5,*(undefined2 *)(iVar7 + 0x437906fc));
    FUN_437fc56c(0xc,*(undefined2 *)(iVar7 + 0x437921ce));
    FUN_43b007ae();
    FUN_437fc580();
    FUN_43ae9130(auStack_50,DAT_43790a60 + 0x43790776);
    FUN_439018b0(DAT_43790a64 + 0x43790782,auStack_50,0,0);
  }
  if (*(char *)(DAT_43790a68 + 0x4379226b) == '\x01') {
    uVar8 = FUN_437876dc();
    iVar16 = FUN_43b00cba();
    if (iVar16 != 0) {
      FUN_43b00ed8(uVar8,DAT_43790a6c + 0x437907a8);
    }
  }
  FUN_43ae129a(4);
  if ((uVar11 != **(uint **)(DAT_43790a70 + 0x437907ba)) ||
     (param_1 != *(byte *)(DAT_43790a74 + 0x437922a1))) {
    iVar6 = thunk_FUN_436cd00c();
    iVar7 = DAT_43790a7c;
    iVar16 = DAT_43790a78;
    uVar14 = (uint)(iVar6 - (*(undefined4 **)(DAT_43790a78 + 0x437907de))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43790a80 + 0x437907fa,uVar11,param_1,
                 **(undefined4 **)(DAT_43790a78 + 0x437907de),
                 *(undefined1 *)(DAT_43790a7c + 0x437922bd),uVar14);
    FUN_43902718(DAT_43790a84 + 0x43790816,uVar11,param_1,**(undefined4 **)(iVar16 + 0x437907de),
                 *(undefined1 *)(iVar7 + 0x437922bd),uVar14);
    if (param_1 < 4) {
      uVar8 = *(undefined4 *)(DAT_43790a88 + 0x43790826 + param_1 * 4);
    }
    else {
      uVar8 = 7;
    }
    FUN_4378f988(4,uVar8,uVar14);
    if ((*(byte *)(iVar13 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43790a8c + 0x43790842);
    }
    if ((*(byte *)(iVar13 + 0x1b) & 0x20) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(char *)(DAT_43790a90 + 0x43792336) == '\0') ||
     (*(int *)(*(int *)(DAT_43790a94 + 0x43790866) + 0x14) != 0)) {
    FUN_4378d3b4();
  }
  cVar2 = *(char *)(DAT_43790a98 + 0x4379234f);
  if (cVar2 == '\x01') {
    if (*(int *)(DAT_43790a98 + 0x43790e40) == 0) goto LAB_437908b0;
    uVar8 = 2;
  }
  else if (cVar2 == '\0') {
    if ((*(int *)(DAT_43790a98 + 0x43790e40) == 0) && (*(int *)(DAT_43790a98 + 0x43790e14) != 1))
    goto LAB_437908b0;
    uVar8 = 1;
  }
  else {
    if ((cVar2 != '\x02') ||
       ((*(int *)(DAT_43790a98 + 0x43790e40) == 0 && (*(int *)(DAT_43790a98 + 0x43790e14) != 1))))
    goto LAB_437908b0;
    uVar8 = 3;
  }
  FUN_43901480(uVar8);
LAB_437908b0:
  if (((*(byte *)(iVar13 + 0x12) & 1) != 0) && (*(byte *)(DAT_43790a9c + 0x4379239f) < 4)) {
                    /* WARNING: Could not recover jumptable at 0x437908ca. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_437908ca::switchdataD_437908ce +
              (uint)(&switchD_437908ca::switchdataD_437908ce)[*(byte *)(DAT_43790a9c + 0x4379239f)]
              * 2))();
    return;
  }
  return;
}


/* 4379155c */

void FUN_4379155c(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  undefined1 *puVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  undefined4 uStack_44;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  uint uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [8];
  
  iVar9 = DAT_43791830 + 0x4379156c;
  iVar8 = *(int *)(iVar9 + DAT_43791834);
  if ((*(byte *)(iVar8 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43791838 + 0x4379157a);
  }
  iVar3 = DAT_4379183c;
  if (param_1 == **(int **)(DAT_4379183c + 0x43791586)) {
    iVar2 = FUN_43560de0(0x1a,0x40,0,auStack_24,4);
    if (iVar2 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,DAT_4379184c + 0x4379161e,**(undefined4 **)(iVar3 + 0x43791586),uStack_30);
      FUN_43902718(DAT_43791850 + 0x4379162a,**(undefined4 **)(iVar3 + 0x43791586),uStack_30);
    }
    FUN_43560dc4(0x1a,0xffffffbf);
    FUN_43ae1292(1);
    iVar3 = FUN_43ae8d4e();
    if (iVar3 == 0) {
      FUN_43901778();
      if (*(char *)(DAT_43791854 + 0x4379164e) != '\0') {
        *(undefined1 *)(DAT_43791858 + 0x43791658) = 1;
      }
      uVar5 = 0;
      puVar6 = (undefined1 *)(DAT_4379185c + 0x43791660);
    }
    else {
      uVar5 = 1;
      puVar6 = (undefined1 *)(DAT_43791860 + 0x43791668);
    }
    *puVar6 = uVar5;
    iVar3 = DAT_43791864;
    FUN_43560dc4(0x1a,0xfffffeff);
    iVar2 = FUN_43b039fc(iVar3 + 0x4379167a,DAT_43791868 + 0x4379167e);
    if (iVar2 == 0) {
      iVar3 = 0;
    }
    else if (*(int *)(iVar3 + 0x43791692) == 0) {
      if (*(char *)(DAT_4379186c + 0x4379168c) == '\0') {
        if (*(char *)(DAT_43791870 + 0x43791e25) == '\0') {
          iVar3 = 0;
        }
        else {
          iVar3 = iVar3 + 0x4379167e;
        }
      }
      else {
        iVar3 = 0;
      }
    }
    else {
      iVar3 = 0;
    }
    puVar6 = (undefined1 *)FUN_4379ce18();
    iVar2 = DAT_43791874;
    iVar7 = DAT_43791874 + 0x437916b8;
    thunk_FUN_43af2858(*(undefined4 *)(DAT_43791874 + 0x437916e0),puVar6);
    *puVar6 = 0;
    uVar4 = FUN_43ae8cd0(*(undefined4 *)(iVar9 + DAT_43791878));
    iVar9 = DAT_4379187c;
    uVar1 = FUN_43796954(uVar4,iVar3,iVar7);
    *(undefined2 *)(iVar9 + 0x43791eee) = uVar1;
    iVar7 = FUN_437999e4(1,0xd);
    iVar3 = DAT_43791880;
    if (((iVar7 != 0) && (*(int *)(iVar9 + 0x43791cae) != 0)) &&
       ((*(short *)(iVar9 + 0x43791d4e) == 1 || (*(int *)(*(int *)(iVar2 + 0x437916bc) + 0xc) == 0))
       )) {
      uStack_44 = FUN_43ae9332(*(undefined4 *)(DAT_43791880 + 0x43791cf0));
      uStack_40 = 0;
      uStack_3f = 0;
      iVar9 = FUN_43795610(*(undefined1 *)(iVar3 + 0x43791e99));
      if (((iVar9 != 0) && (*(char *)(DAT_43791884 + 0x4379172a) == '\0')) &&
         (*(char *)(iVar3 + 0x43791ea8) != '\0')) {
        uStack_3f = 1;
      }
      uStack_3c = (uint)(*(int *)(*(int *)(DAT_43791888 + 0x4379173e) + 0x548) != 0);
      uStack_38 = *(undefined4 *)(*(int *)(DAT_43791888 + 0x4379173e) + 0x54c);
      iVar9 = FUN_437956c8(DAT_4379188c + 0x43791dae,&uStack_44);
      if (iVar9 != 0) {
        FUN_4378eb78(3,9,1,DAT_43791890 + 0x43791770,iVar9);
        FUN_43902718(DAT_43791894 + 0x4379177a,iVar9);
      }
    }
    FUN_43900380();
    iVar9 = DAT_43791898;
    FUN_439cdbc8();
    uStack_28 = 0;
    uStack_2c = 0;
    FUN_43728c18(0,&uStack_28,&uStack_2c);
    FUN_43b6d334(uStack_28,uStack_2c);
    FUN_43560da8(0x1a,0x100);
    FUN_43ae129a(1);
    if ((param_1 != **(int **)(iVar9 + 0x43791796)) && (iVar3 = FUN_43ae8d4e(), iVar3 != 0)) {
      iVar3 = thunk_FUN_436cd00c();
      uVar10 = (uint)(iVar3 - (*(undefined4 **)(iVar9 + 0x43791796))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_4379189c + 0x437917d4,param_1,**(undefined4 **)(iVar9 + 0x43791796),
                   uVar10);
      FUN_43902718(DAT_437918a0 + 0x437917ea,param_1,**(undefined4 **)(iVar9 + 0x43791796),uVar10);
      FUN_4378f988(4,1,uVar10);
      if ((*(byte *)(iVar8 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_437918a4 + 0x43791806);
      }
      if ((*(byte *)(iVar8 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43791528();
    if ((*(byte *)(iVar8 + 0x12) & 1) != 0) {
      FUN_43561540(DAT_437918a8 + 0x43791826);
    }
  }
  else {
    iVar9 = FUN_43ae8d4e();
    if (iVar9 != 0) {
      iVar9 = thunk_FUN_436cd00c();
      uVar10 = (uint)(iVar9 - (*(undefined4 **)(iVar3 + 0x43791586))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_43791840 + 0x437915aa,param_1,**(undefined4 **)(iVar3 + 0x43791586),
                   uVar10);
      FUN_43902718(DAT_43791844 + 0x437915c0,param_1,**(undefined4 **)(iVar3 + 0x43791586),uVar10);
      FUN_4378f988(3,1,uVar10);
      if ((*(byte *)(iVar8 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_43791848 + 0x437915dc);
      }
      if ((*(byte *)(iVar8 + 0x1b) & 4) != 0) {
        FUN_4378ec60();
      }
    }
  }
  return;
}


/* 43791a7c */

void FUN_43791a7c(int param_1)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  byte *pbVar11;
  uint *puVar12;
  undefined4 uVar13;
  undefined4 *puVar14;
  char *pcVar15;
  ushort *puVar16;
  uint *puVar17;
  int iVar18;
  undefined4 *puVar19;
  int iVar20;
  int *piVar21;
  undefined4 *puVar22;
  undefined4 uStack_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined1 uStack_d8;
  undefined1 auStack_d4 [20];
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  ushort uStack_2c;
  ushort uStack_2a;
  
  iVar10 = DAT_43791fe4;
  iVar7 = DAT_43791fe0;
  FUN_43795e7c();
  FUN_43796424();
  iVar10 = iVar10 + 0x43791a9a;
  if (*(char *)(iVar7 + 0x43791a94) == '\0') {
    FUN_43ae863c(auStack_48,*(undefined4 *)(iVar10 + DAT_43791fe8));
    FUN_436ccee4(0x1e,1,auStack_48);
    FUN_43ae863c(auStack_5c,*(undefined4 *)(iVar10 + DAT_43791fec));
    FUN_436ccee4(0x17,1,auStack_5c);
    *(char *)(iVar7 + 0x43791a94) = '\x01';
  }
  iVar7 = *(int *)(iVar10 + DAT_43791ff0);
  if ((*(byte *)(iVar7 + 0xc) & 1) != 0) {
    FUN_4378eb78(3,9,1,DAT_43791ff4 + 0x43791aea);
    FUN_43902718(DAT_43791ff8 + 0x43791af4);
  }
  thunk_FUN_4386116c();
  thunk_FUN_436e06f4();
  if ((*(byte *)(iVar7 + 4) & 1) != 0) {
    piVar21 = *(int **)(iVar10 + DAT_43791ffc);
    iVar18 = *piVar21;
    puVar22 = *(undefined4 **)(iVar10 + DAT_43792000);
    uVar13 = *puVar22;
    uVar3 = FUN_43795d2c();
    puVar19 = *(undefined4 **)(iVar10 + DAT_43792004);
    puVar14 = *(undefined4 **)(iVar10 + DAT_43792008);
    FUN_4378eb78(3,9,1,DAT_4379200c + 0x43791b4c,iVar18,uVar13,uVar3,*puVar19,*puVar14);
    iVar18 = *piVar21;
    uVar13 = *puVar22;
    uVar3 = FUN_43795d2c();
    FUN_43902718(DAT_43792010 + 0x43791b72,iVar18,uVar13,uVar3,*puVar19,*puVar14);
    *piVar21 = param_1;
    *puVar22 = 0;
    *puVar19 = 0;
    *puVar14 = 0;
  }
  FUN_43904008();
  FUN_43901638(0);
  FUN_43901638(4);
  FUN_43901638(8);
  FUN_43901638(5);
  iVar18 = *(int *)(iVar10 + DAT_43792014);
  if (((*(byte *)(iVar18 + 0x29) & 0xf) != 0xf) &&
     (pcVar15 = *(char **)(iVar10 + DAT_43792018), *pcVar15 != '\0')) {
    FUN_43901638(9);
    *pcVar15 = '\0';
  }
  if (((*(byte *)(iVar18 + 0x29) & 0xf0) != 0xf0) &&
     (pcVar15 = *(char **)(iVar10 + DAT_4379201c), *pcVar15 != '\0')) {
    FUN_43901638(10);
    *pcVar15 = '\0';
  }
  iVar8 = DAT_43792020;
  FUN_43901768();
  FUN_43901748();
  FUN_43903f18();
  uVar1 = *(undefined1 *)(iVar8 + 0x437921da);
  *(undefined1 *)((int)&DAT_437936d4 + iVar8) = uVar1;
  FUN_4378e1a4(param_1,uVar1,iVar8 + 0x43792156);
  iVar4 = FUN_437fe4f4();
  *(bool *)(iVar8 + 0x437921cd) = iVar4 != 0;
  piVar21 = (int *)(DAT_43792024 + 0x43791c22);
  iVar8 = *piVar21;
  if (iVar8 != 7) {
    FUN_4378eb78(3,9,1,DAT_43792028 + 0x43791c36,param_1,iVar8);
    FUN_43902718(DAT_4379202c + 0x43791c42,param_1,*piVar21);
  }
  iVar8 = DAT_43792030;
  *(undefined1 *)((int)&DAT_43793728 + DAT_43792030 + 3) = 0;
  *(undefined1 *)((int)&DAT_4379372c + iVar8) = 0;
  *(undefined4 *)(DAT_43792034 + 0x43791c5c) = 0;
  *(undefined4 *)(DAT_43792038 + 0x43791c64) = 1;
  iVar20 = **(int **)(DAT_4379203c + 0x43791c6e);
  iVar4 = FUN_4379a898();
  *(undefined1 *)(iVar8 + 0x43792222) = *(undefined1 *)(iVar4 + 0x5c);
  *(char *)(iVar8 + 0x43792221) = *(char *)(iVar8 + 0x437923dd);
  if (*(char *)(iVar8 + 0x437923dd) != '\0') {
    *(char *)(iVar8 + 0x43792220) = *(char *)(iVar8 + 0x43792220) + '\x01';
    *(undefined4 *)(iVar8 + 0x4379221c) = *(undefined4 *)(iVar8 + 0x4379222c);
    *(undefined4 *)(iVar8 + 0x437923d8) = *(undefined4 *)(iVar8 + 0x4379222c);
    FUN_43ae8cd4(*(undefined4 *)(iVar10 + DAT_43792040));
  }
  if (*(int *)(DAT_43792044 + 0x43792432) != 0) {
    *(int *)(DAT_43792044 + 0x43792432) = *(int *)(DAT_43792044 + 0x43792432) + -1;
  }
  iVar10 = DAT_43792048;
  pcVar15 = (char *)(DAT_43792048 + 0x43792456);
  *(char *)(DAT_43792048 + 0x43792293) = *pcVar15;
  if (*pcVar15 != '\0') {
    *(undefined1 *)(iVar10 + 0x43792292) = *(undefined1 *)(iVar10 + 0x4379244e);
    *(undefined4 *)(iVar10 + 0x4379228e) = *(undefined4 *)(iVar10 + 0x4379244a);
    *(undefined4 *)(iVar10 + 0x43792452) = *(undefined4 *)(iVar10 + 0x4379244a);
  }
  if (*(int *)(DAT_4379204c + 0x43792474) != 0) {
    *(int *)(DAT_4379204c + 0x43792474) = *(int *)(DAT_4379204c + 0x43792474) + -1;
  }
  if (*(int *)(DAT_43792050 + 0x43791cea) == *(int *)(DAT_43792054 + 0x43791cee)) {
    pbVar11 = (byte *)(DAT_43792058 + 0x43791cf8);
    if (*pbVar11 < 5) {
      bVar6 = *pbVar11 + 1;
      puVar16 = (ushort *)(DAT_4379205c + 0x43791d08);
      uVar9 = (uint)bVar6;
      *pbVar11 = bVar6;
      uVar5 = (uint)*puVar16;
      FUN_4378eb78(3,9,1,DAT_43792060 + 0x43791d18,uVar5,uVar9);
      FUN_43902718(DAT_43792064 + 0x43791d22,*puVar16,*pbVar11);
      if (*pbVar11 == 1) {
        FUN_43901a8c(3,1,*puVar16,0);
      }
      if (*(char *)(DAT_43792068 + 0x43791d3c) == '\x05') {
        FUN_4378eb78(3,9,1,DAT_4379206c + 0x43791d4c,uVar5,uVar9);
        FUN_43902718(DAT_43792070 + 0x43791d54);
      }
    }
  }
  piVar21 = (int *)(DAT_43792078 + 0x43791d62);
  *(undefined4 *)(DAT_43792074 + 0x43791d5e) = *(undefined4 *)(DAT_4379207c + 0x43791d64);
  if (*piVar21 != 0) {
    uStack_f0 = *(undefined4 *)(DAT_43792080 + 0x43791d70);
    iVar10 = FUN_4378f9b4();
    uStack_ec = *(undefined4 *)(*(int *)(iVar10 + 8) + 0x1e8);
    iVar10 = FUN_4378f9b4();
    uStack_e8 = *(undefined4 *)(*(int *)(iVar10 + 8) + 0x3c);
    iVar10 = FUN_4378f9b4();
    uStack_dc = *(undefined4 *)(*(int *)(iVar10 + 4) + 0x18);
    iVar10 = FUN_4378f9b4();
    uStack_e0 = *(undefined4 *)(*(int *)(iVar10 + 0xc) + 0x5c);
    uStack_d8 = FUN_43ae1252();
    (*(code *)*piVar21)(&uStack_f0);
  }
  iVar8 = DAT_43792088 + 0x43791db6;
  FUN_43ada220(auStack_70,DAT_43792084 + 0x43791db4);
  FUN_439018b0(iVar8,auStack_70,iVar20,0);
  FUN_43ada220(auStack_84,DAT_4379208c + 0x43791dcc);
  iVar10 = DAT_43792090;
  FUN_439018b0(iVar8,auStack_84,iVar20 << 8,0);
  iVar8 = *(int *)(*(int *)(iVar10 + 0x43791de0) + 0x2c);
  FUN_43ae863c(auStack_98,DAT_43792094 + 0x43791de8);
  FUN_436ccd9c(1,param_1 + iVar8,1,auStack_98);
  if ((*(byte *)(iVar7 + 0x1f) & 1) == 0) {
    FUN_4378d818(param_1,*(undefined4 *)(*(int *)(iVar10 + 0x43791de0) + 0x24));
  }
  if ((*(byte *)(iVar7 + 0x1f) & 2) == 0) {
    FUN_4378db0c(param_1,*(undefined4 *)(*(int *)(DAT_43792098 + 0x43791e24) + 0x24));
  }
  *(undefined1 *)(DAT_4379209c + 0x43791e2e) = 0;
  iVar10 = FUN_436e8328();
  if (iVar10 == 1) {
    FUN_43ae72f6(&uStack_34);
    iVar10 = *(int *)(*(int *)(DAT_437920a8 + 0x43791e58) + 0x14);
    if (iVar10 == 1) {
      *(uint *)(DAT_437920b4 + 0x43791e86) = (uint)uStack_30;
      *(uint *)(DAT_437920b8 + 0x43791e8c) = (uint)uStack_2e;
    }
    else if (iVar10 == 2) {
      *(uint *)(DAT_437920bc + 0x43791e94) = (uint)uStack_2c;
      *(uint *)(DAT_437920c0 + 0x43791e9a) = (uint)uStack_2a;
    }
    else {
      *(uint *)(DAT_437920ac + 0x43791e78) = (uint)uStack_34;
      *(uint *)(DAT_437920b0 + 0x43791e7e) = (uint)uStack_32;
    }
    puVar12 = (uint *)(DAT_437920c4 + 0x43791ea2);
    puVar17 = (uint *)(DAT_437920c8 + 0x43791ea4);
    uVar9 = *puVar12;
    uVar5 = *puVar17;
    *puVar12 = uVar9 << 1;
    *puVar17 = uVar5 << 1;
    uVar5 = FUN_43ae8c60();
    if (((uVar9 << 1 < uVar5) ||
        (uVar5 = *puVar17, uVar9 = *puVar12, iVar10 = FUN_43ae8c60(), uVar5 < iVar10 + uVar9)) ||
       (*(uint *)(*(int *)(DAT_437920cc + 0x43791ed2) + 0x24) < *puVar17)) {
      iVar7 = DAT_437920d8;
      puVar19 = (undefined4 *)(DAT_437920d0 + 0x43791ee0);
      puVar14 = (undefined4 *)(DAT_437920d4 + 0x43791ee4);
      FUN_4378eb78(3,9,1,DAT_437920dc + 0x43791efa,*puVar19,*puVar14,
                   *(undefined4 *)(*(int *)(DAT_437920d8 + 0x43791eee) + 0x24));
      FUN_43902718(DAT_437920e0 + 0x43791f08,*puVar19,*puVar14,
                   *(undefined4 *)(*(int *)(iVar7 + 0x43791eee) + 0x24));
      *puVar19 = 0;
      *puVar14 = 0;
    }
    else if ((*(byte *)(iVar7 + 0x1f) & 4) == 0) {
      uVar5 = *puVar12;
      FUN_43ae863c(auStack_ac,DAT_437920e4 + 0x43791f20);
      FUN_436ccd9c(5,param_1 + uVar5,1,auStack_ac);
      *(undefined1 *)(DAT_437920e8 + 0x43791f36) = 1;
      iVar7 = FUN_4378e90c();
      if (iVar7 != 0) {
        uVar9 = (uint)*(byte *)(iVar18 + 0x28) * -200 + *puVar12;
        puVar17 = (uint *)(DAT_437920ec + 0x43791f52);
        *puVar17 = uVar9;
        uVar5 = FUN_43ae8c60();
        iVar7 = DAT_437920f4;
        if ((uVar9 < uVar5) || (*puVar12 <= *puVar17)) {
          puVar14 = (undefined4 *)(DAT_437920f0 + 0x43791f6e);
          FUN_4378eb78(3,9,1,DAT_437920f8 + 0x43791f80,*puVar14,
                       *(undefined4 *)(*(int *)(DAT_437920f4 + 0x43791f76) + 0x24));
          FUN_43902718(DAT_437920fc + 0x43791f8c,*puVar14,
                       *(undefined4 *)(*(int *)(iVar7 + 0x43791f76) + 0x24));
          uVar3 = FUN_43ae8c60();
          *puVar14 = uVar3;
        }
        param_1 = param_1 + *(int *)(DAT_43792100 + 0x43791fa0);
        FUN_43ae863c(auStack_c0,DAT_43792104 + 0x43791fa6);
        puVar2 = &stack0x0000002c;
        goto LAB_43791fca;
      }
    }
  }
  else {
    *(undefined4 *)(DAT_437920a0 + 0x43791e3c) = 0;
    *(undefined4 *)(DAT_437920a4 + 0x43791e42) = 0;
  }
  param_1 = FUN_4378e938();
  FUN_43ae863c(auStack_d4,DAT_43792108 + 0x43791fbc);
  puVar2 = &stack0x00000018;
LAB_43791fca:
  FUN_436ccd9c(0,param_1,1,puVar2 + -0xec);
  return;
}


/* 4379210c */

void FUN_4379210c(int param_1)

{
  ushort uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined1 uVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  ushort *puVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  byte bVar16;
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [4];
  uint uStack_28;
  undefined1 auStack_24 [4];
  
  iVar13 = DAT_437925f8 + 0x43792120;
  iVar12 = *(int *)(iVar13 + DAT_437925fc);
  if ((*(byte *)(iVar12 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43792600 + 0x43792130);
  }
  iVar4 = DAT_43792604;
  if (param_1 == **(int **)(DAT_43792604 + 0x4379213e)) {
    FUN_43ae1292(4);
    iVar4 = FUN_43ae8d4e();
    if (iVar4 == 0) {
      FUN_43901778();
      if (*(char *)(DAT_43792614 + 0x437921ba) != '\0') {
        *(undefined1 *)(DAT_43792618 + 0x437921c6) = 1;
      }
      uVar8 = 0;
      puVar10 = (undefined1 *)(DAT_4379261c + 0x437921d0);
    }
    else {
      uVar8 = 1;
      puVar10 = (undefined1 *)(DAT_43792620 + 0x437921da);
    }
    *puVar10 = uVar8;
    FUN_43728c70();
    FUN_4378f7a0(0xd35);
    iVar4 = DAT_43792624;
    uVar5 = FUN_4377fdf8();
    *(undefined4 *)(iVar4 + 0x43794040) = uVar5;
    FUN_43560e00(0x11,auStack_2c);
    iVar6 = FUN_4378e90c();
    if (iVar6 != 0) {
      uStack_28 = uStack_28 & 0xfffffffb | *(uint *)(iVar4 + 0x437929f8) & 4;
    }
    *(uint *)(iVar4 + 0x437929f8) = uStack_28;
    uVar1 = *(ushort *)(DAT_43792628 + 0x43792220);
    if (uVar1 != 0) {
      puVar11 = (ushort *)(DAT_4379262c + 0x4379222a);
      uVar2 = *puVar11;
      *puVar11 = uVar2 + 1;
      if (uVar1 < (ushort)(uVar2 + 1)) {
        *puVar11 = 1;
        iVar4 = 0;
        do {
          *(undefined2 *)(DAT_43792630 + 0x43792242 + iVar4) = 0;
          *(undefined2 *)(DAT_43792634 + 0x43792248 + iVar4) = 0;
          *(undefined2 *)(DAT_43792638 + 0x4379224e + iVar4) = 0;
          iVar4 = iVar4 + 2;
        } while (iVar4 != 0x1a);
      }
    }
    iVar6 = FUN_4378e90c();
    iVar4 = DAT_4379263c;
    if (iVar6 == 0) {
      iVar6 = DAT_4379263c + 0x43792262;
      if ((*(uint *)(DAT_4379263c + 0x43792a66) & 4) == 0) {
        uVar5 = FUN_437b4d64();
        iVar7 = DAT_43792640 + 0x43792278;
        *(undefined4 *)(iVar4 + 0x437940b2) = uVar5;
        FUN_43ae8e2c(iVar6,iVar7);
        *(undefined2 *)(DAT_43792644 + 0x43792288) = 0;
      }
      else {
        *(short *)(DAT_43792648 + 0x43792290) = *(short *)(DAT_43792648 + 0x43792290) + 1;
        *(short *)(DAT_4379264c + 0x4379229a) = *(short *)(DAT_4379264c + 0x4379229a) + 1;
      }
    }
    iVar4 = DAT_43792650;
    iVar6 = DAT_43792650 + 0x437922a2;
    if ((*(uint *)(DAT_43792650 + 0x43792aa6) & 8) == 0) {
      uVar5 = FUN_4379fc20();
      iVar7 = DAT_43792654 + 0x437922b8;
      *(undefined4 *)(iVar4 + 0x437940fa) = uVar5;
      FUN_43ae8e5c(iVar6,iVar7);
      *(undefined2 *)(DAT_43792658 + 0x437922ca) = 0;
    }
    else {
      *(short *)(DAT_4379265c + 0x437922d2) = *(short *)(DAT_4379265c + 0x437922d2) + 1;
      *(short *)(DAT_43792660 + 0x437922dc) = *(short *)(DAT_43792660 + 0x437922dc) + 1;
    }
    iVar4 = DAT_43792664;
    iVar6 = DAT_43792664 + 0x437922e2;
    if ((*(uint *)(DAT_43792664 + 0x43792ae6) & 0x20) == 0) {
      uVar5 = FUN_437d0bc8();
      iVar7 = DAT_43792668 + 0x437922f8;
      *(undefined4 *)(iVar4 + 0x4379413e) = uVar5;
      FUN_43ae8e74(iVar6,iVar7);
      *(undefined2 *)(DAT_4379266c + 0x4379230e) = 0;
    }
    else {
      *(short *)(DAT_43792670 + 0x43792316) = *(short *)(DAT_43792670 + 0x43792316) + 1;
      *(short *)(DAT_43792674 + 0x43792320) = *(short *)(DAT_43792674 + 0x43792320) + 1;
    }
    iVar4 = DAT_43792678;
    iVar6 = DAT_43792678 + 0x43792322;
    if ((*(uint *)(DAT_43792678 + 0x43792b26) & 0x40) == 0) {
      uVar5 = FUN_437d9930();
      iVar7 = DAT_4379267c + 0x43792338;
      *(undefined4 *)(iVar4 + 0x43794182) = uVar5;
      FUN_43ae8e84(iVar6,iVar7);
      *(undefined2 *)(DAT_43792680 + 0x43792350) = 0;
    }
    else {
      *(short *)(DAT_43792684 + 0x43792358) = *(short *)(DAT_43792684 + 0x43792358) + 1;
      *(short *)(DAT_43792688 + 0x43792362) = *(short *)(DAT_43792688 + 0x43792362) + 1;
    }
    iVar4 = DAT_4379268c;
    iVar6 = DAT_4379268c + 0x43792362;
    if ((*(uint *)(DAT_4379268c + 0x43792b66) & 0x80) == 0) {
      uVar5 = FUN_437b6614();
      iVar7 = DAT_43792690 + 0x43792378;
      *(undefined4 *)(iVar4 + 0x437941c6) = uVar5;
      FUN_43ae8e9a(iVar6,iVar7);
      *(undefined2 *)(DAT_43792694 + 0x43792392) = 0;
    }
    else {
      *(short *)(DAT_43792698 + 0x4379239a) = *(short *)(DAT_43792698 + 0x4379239a) + 1;
      *(short *)(DAT_4379269c + 0x437923a4) = *(short *)(DAT_4379269c + 0x437923a4) + 1;
    }
    iVar4 = DAT_437926a0;
    iVar6 = DAT_437926a0 + 0x437923a2;
    if ((*(uint *)(DAT_437926a0 + 0x43792ba6) & 0x200) == 0) {
      uVar5 = FUN_437b8230();
      iVar7 = DAT_437926a4 + 0x437923b8;
      *(undefined4 *)(iVar4 + 0x4379420a) = uVar5;
      FUN_43ae8ea4(iVar6,iVar7);
      *(undefined2 *)(DAT_437926a8 + 0x437923d6) = 0;
    }
    else {
      *(short *)(DAT_437926ac + 0x437923de) = *(short *)(DAT_437926ac + 0x437923de) + 1;
      *(short *)(DAT_437926b0 + 0x437923e8) = *(short *)(DAT_437926b0 + 0x437923e8) + 1;
    }
    FUN_4378f7a0(0xd96);
    iVar4 = FUN_4378e90c();
    if (iVar4 == 0) {
      FUN_4378f7a0(0xda0);
      FUN_437b4e28(DAT_437926b4 + 0x437923f6);
      FUN_4378f7a0(0xda2);
    }
    iVar4 = DAT_437926bc;
    iVar7 = DAT_437926b8 + 0x4379240a;
    FUN_437c1bb4(iVar7);
    thunk_FUN_43b7c7da(iVar7);
    FUN_437b0244(iVar7,iVar4 + 0x43793ee8);
    iVar6 = FUN_4378e90c();
    if (iVar6 == 0) {
      FUN_4378f7a0(0xda9);
      FUN_43aef444(iVar7,iVar4 + 0x4379369e);
      FUN_4378f7a0(0xdad);
    }
    iVar6 = DAT_437926c4;
    iVar4 = DAT_437926c0;
    iVar7 = DAT_437926c4 + 0x43792450;
    FUN_437c1b98(iVar7,DAT_437926c0 + 0x43793b7e);
    thunk_FUN_43b7c7dc(iVar7,iVar4 + 0x43793d1f);
    iVar4 = FUN_43560de0(0x1a,0x100,0,auStack_24,4);
    if (iVar4 != 0) {
      FUN_43560e00(0x1a,auStack_34);
      FUN_4378eb78(3,9,1,DAT_437926c8 + 0x43792498,**(undefined4 **)(iVar6 + 0x43792454),uStack_30);
      FUN_43902718(DAT_437926cc + 0x437924a4,**(undefined4 **)(iVar6 + 0x43792454),uStack_30);
      FUN_43560da8(0x1a,0x100);
    }
    if (*(char *)(iVar12 + 0x70) == '\0') {
      iVar4 = FUN_437999e4(1,0xe);
      if (iVar4 != 0) {
        if ((*(char *)(DAT_437926d0 + 0x43792a9f) == '\0') ||
           (*(int *)(*(int *)(DAT_437926d4 + 0x437924d6) + 0xc) != 0)) {
          FUN_439e21c0();
        }
        FUN_439e2184();
      }
      FUN_439fd76c();
    }
    iVar4 = DAT_437926d8;
    FUN_4378f7a0(0xdd0);
    FUN_437967e8(iVar4 + 0x437924f0);
    FUN_4378f7a0(0xdd3);
    FUN_43ada220(auStack_48,DAT_437926dc + 0x43792504);
    FUN_439018b0(DAT_437926e0 + 0x43792510,auStack_48,param_1,0);
    bVar16 = *(byte *)(iVar12 + 0x1f) & 8;
    if (((*(byte *)(iVar12 + 0x1f) & 8) == 0) && (iVar6 = FUN_436e8328(), iVar6 != 0)) {
      iVar6 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 0x24);
      iVar7 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 8);
      iVar15 = *(int *)(iVar13 + DAT_437926e4);
      uVar3 = *(undefined2 *)(iVar15 + 0x2e);
      FUN_43ae863c(auStack_5c,bVar16);
      FUN_436ccd9c(6,iVar6 + iVar7,uVar3,auStack_5c);
      iVar6 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 0x24);
      iVar4 = *(int *)(*(int *)(iVar4 + 0x437924f4) + 8);
      iVar13 = FUN_43ada230();
      uVar3 = *(undefined2 *)(iVar15 + 0x2c);
      FUN_43ae863c(auStack_70,bVar16);
      FUN_436ccd9c(7,iVar6 + iVar4 + iVar13 * 2,uVar3,auStack_70);
    }
    iVar13 = DAT_437926e8;
    FUN_43ae129a(4);
    if (param_1 != **(int **)(iVar13 + 0x43792582)) {
      iVar4 = thunk_FUN_436cd00c();
      uVar14 = (uint)(iVar4 - (*(undefined4 **)(iVar13 + 0x43792582))[2]) >> 1;
      FUN_4378eb78(3,9,1,DAT_437926ec + 0x4379259c,param_1,**(undefined4 **)(iVar13 + 0x43792582),
                   uVar14);
      FUN_43902718(DAT_437926f0 + 0x437925b2,param_1,**(undefined4 **)(iVar13 + 0x43792582),uVar14);
      FUN_4378f988(4,2,uVar14);
      if ((*(byte *)(iVar12 + 0x12) & 4) != 0) {
        FUN_43561540(DAT_437926f4 + 0x437925ce);
      }
      if ((*(byte *)(iVar12 + 0x1b) & 8) != 0) {
        FUN_4378ec60();
      }
    }
    FUN_43901480(0);
    if ((*(byte *)(iVar12 + 0x12) & 1) != 0) {
      FUN_43561540(DAT_437926f8 + 0x437925f0);
    }
  }
  else {
    iVar13 = thunk_FUN_436cd00c();
    puVar9 = *(undefined4 **)(iVar4 + 0x4379213e);
    uVar14 = (uint)(iVar13 - puVar9[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43792608 + 0x4379215a,param_1,*puVar9,uVar14);
    FUN_43902718(DAT_4379260c + 0x43792172,param_1,**(undefined4 **)(iVar4 + 0x4379213e),uVar14);
    FUN_4378f988(3,2,uVar14);
    if ((*(byte *)(iVar12 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43792610 + 0x43792190);
    }
    if ((*(byte *)(iVar12 + 0x1b) & 8) != 0) {
      FUN_4378ec60();
    }
  }
  return;
}


/* 437927c4 */

void FUN_437927c4(int param_1)

{
  char cVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  byte bVar4;
  uint uVar5;
  int *piVar6;
  uint *puVar7;
  uint *puVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined4 uStack_a0;
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined1 uStack_88;
  undefined1 auStack_84 [20];
  undefined1 auStack_70 [20];
  undefined1 auStack_5c [20];
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [24];
  
  iVar11 = DAT_43792974 + 0x437927da;
  uVar5 = *(uint *)(DAT_43792970 + 0x437927ce) + 1;
  *(uint *)(DAT_43792970 + 0x437927ce) = uVar5;
  if ((uVar5 & 1) != 0) goto LAB_43792826;
  cVar1 = *(char *)((int)&DAT_437942c4 + DAT_43792978 + 3);
  if (cVar1 == '\x01') {
    uVar3 = 2;
LAB_43792802:
    FUN_43901638(uVar3);
  }
  else {
    if (cVar1 == '\0') {
      uVar3 = 1;
      goto LAB_43792802;
    }
    if (cVar1 == '\x02') {
      uVar3 = 3;
      goto LAB_43792802;
    }
  }
  iVar9 = DAT_4379297c;
  bVar4 = *(char *)((int)&DAT_437942e8 + DAT_4379297c + 3) + 1;
  *(byte *)((int)&DAT_437942e8 + DAT_4379297c + 3) = bVar4;
  if ((uint)*(byte *)((int)&DAT_437942e8 + iVar9 + 2) <= bVar4 + 1) {
    *(undefined1 *)((int)&DAT_437942ec + iVar9) = 1;
  }
LAB_43792826:
  iVar9 = DAT_437929a0;
  puVar8 = (uint *)(DAT_43792984 + 0x43792832);
  piVar6 = *(int **)(DAT_43792980 + 0x43792832);
  puVar7 = (uint *)(DAT_43792988 + 0x43792836);
  iVar10 = *piVar6;
  bVar4 = *(byte *)((int)&DAT_43794318 + DAT_4379298c + 3);
  uVar5 = *puVar8;
  if (uVar5 == *puVar7) {
    if (uVar5 < 7) {
      *puVar7 = uVar5 + 1;
      iVar11 = piVar6[0xb];
      FUN_43ae863c(auStack_48,iVar9 + 0x43792898);
      FUN_436ccd9c(1,iVar11 + param_1,1,auStack_48);
    }
    piVar6 = (int *)(DAT_437929a4 + 0x437928ae);
    if (*piVar6 != 0) {
      uStack_a0 = *(undefined4 *)(DAT_437929a8 + 0x437928b6);
      iVar11 = FUN_4378f9b4();
      uStack_9c = *(undefined4 *)(*(int *)(iVar11 + 8) + 0x1e8);
      iVar11 = FUN_4378f9b4();
      uStack_98 = *(undefined4 *)(*(int *)(iVar11 + 8) + 0x3c);
      iVar11 = FUN_4378f9b4();
      uStack_8c = *(undefined4 *)(*(int *)(iVar11 + 4) + 0x18);
      iVar11 = FUN_4378f9b4();
      uStack_90 = *(undefined4 *)(*(int *)(iVar11 + 0xc) + 0x5c);
      uStack_88 = FUN_43ae1252();
      (*(code *)*piVar6)(&uStack_a0);
    }
    if ((*(uint *)(DAT_437929ac + 0x437928f6) & 1) == 0) {
      iVar9 = (uint)bVar4 + iVar10 * 0x100;
      iVar11 = DAT_437929b4 + 0x4379290c;
      FUN_43ada220(auStack_5c,DAT_437929b0 + 0x43792908);
      FUN_439018b0(iVar11,auStack_5c,iVar9,0);
      if (*(int *)(DAT_437929b8 + 0x43792ef0) == 0) {
        if (*(int *)(DAT_437929b8 + 0x43792ec4) != 1) {
          return;
        }
        if ((*(byte *)((int)&DAT_437943fc + DAT_437929b8 + 3) & 1) == 0) {
          return;
        }
        FUN_43ada220(auStack_84,DAT_437929c0 + 0x4379295c);
        puVar2 = &stack0x00000008;
      }
      else {
        if (*(char *)((int)&DAT_43794400 + DAT_437929b8) == '\0') {
          return;
        }
        FUN_43ada220(auStack_70,DAT_437929bc + 0x43792934);
        puVar2 = &stack0x0000001c;
      }
      FUN_439018b0(iVar11,puVar2 + -0x8c,iVar9,0);
    }
  }
  else {
    FUN_43ae9130(auStack_34,*(undefined4 *)(iVar11 + DAT_43792990));
    FUN_439018b0(DAT_43792994 + 0x43792860,auStack_34,0,0);
    FUN_4378eb78(3,9,1,DAT_43792998 + 0x43792876,*puVar7,*puVar8);
    FUN_43902718(DAT_4379299c + 0x43792880,*puVar7,*puVar8);
  }
  return;
}


/* 43792a0c */

void FUN_43792a0c(int param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  undefined4 uVar17;
  int iVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  undefined4 uVar22;
  undefined4 uVar23;
  undefined4 uVar24;
  short sVar25;
  int extraout_r1;
  undefined4 uVar26;
  undefined4 uVar27;
  undefined4 uVar28;
  undefined4 uVar29;
  undefined4 uVar30;
  undefined4 uVar31;
  undefined1 uVar32;
  char cVar33;
  byte bVar34;
  undefined1 *puVar35;
  undefined4 uVar36;
  undefined4 *puVar37;
  short *psVar38;
  int iVar39;
  int iVar40;
  undefined4 uVar41;
  char *pcVar42;
  int iVar43;
  int iVar44;
  undefined2 *puVar45;
  int iVar46;
  ushort *puVar47;
  uint uVar48;
  int iVar49;
  int *piVar50;
  uint *puVar51;
  int *piVar52;
  uint uVar53;
  undefined4 *puVar54;
  undefined4 uVar55;
  bool bVar56;
  bool bVar57;
  undefined1 *puVar58;
  undefined1 *puVar59;
  undefined1 *puVar60;
  undefined4 uStack_3b8;
  undefined4 uStack_3b4;
  undefined4 uStack_3b0;
  undefined4 uStack_3ac;
  undefined1 auStack_3a8 [96];
  undefined1 auStack_348 [96];
  undefined4 uStack_2e8;
  undefined4 uStack_2e4;
  undefined1 auStack_2e0 [96];
  undefined1 auStack_280 [96];
  undefined4 uStack_220;
  undefined4 uStack_21c;
  undefined1 auStack_218 [272];
  undefined1 auStack_108 [20];
  undefined1 auStack_f4 [20];
  undefined1 auStack_e0 [20];
  undefined1 auStack_cc [20];
  undefined1 auStack_b8 [20];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [20];
  undefined1 auStack_7c [20];
  undefined1 auStack_68 [20];
  undefined1 auStack_54 [2];
  undefined2 uStack_52;
  undefined1 uStack_4c;
  undefined1 auStack_48 [4];
  undefined4 uStack_44;
  undefined1 auStack_40 [4];
  byte bStack_3c;
  undefined1 auStack_38 [4];
  byte bStack_34;
  undefined4 uStack_30;
  undefined1 auStack_2c [8];
  
  iVar43 = DAT_43792c44 + 0x43792a1e;
  iVar44 = *(int *)(iVar43 + DAT_43792c48);
  if ((*(byte *)(iVar44 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_43792c4c + 0x43792a2e);
  }
  uVar13 = FUN_437876dc();
  if (*(char *)(iVar44 + 0xaa) != '\0') {
    *(int *)(DAT_43792c50 + 0x43792a42) = *(int *)(DAT_43792c50 + 0x43792a42) + 1;
    FUN_4355fd4c();
    if (extraout_r1 == 0) {
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_4378eb78(5,2,1,DAT_43792c54 + 0x43792a68,uVar14,uVar15,uVar16);
      uVar14 = FUN_43728564();
      uVar15 = FUN_437284b4();
      uVar16 = FUN_43ae0c38();
      FUN_43902718(DAT_43792c58 + 0x43792a8c,uVar14,uVar15,uVar16);
    }
  }
  cVar33 = *(char *)(iVar44 + 0x1b);
  if (cVar33 != '\0') {
    puVar35 = (undefined1 *)(DAT_43792c5c + 0x43792a97);
    puVar37 = DAT_43792c38;
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c3c);
    puVar35 = (undefined1 *)(DAT_43792c60 + 0x43792aad);
    do {
      puVar37 = puVar37 + 1;
      puVar35 = puVar35 + 1;
      *puVar35 = (char)*puVar37;
    } while (puVar37 != DAT_43792c40);
    if (cVar33 == '\x01') {
      FUN_4378ec60();
      *(undefined1 *)(iVar44 + 0x1b) = 0;
    }
  }
  if (*(byte *)(iVar44 + 0x11) != 0) {
    uVar53 = (uint)*(byte *)(iVar44 + 0x11) * 100;
    iVar46 = *(int *)(*(int *)(DAT_43792c64 + 0x43792adc) + 8);
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c68)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c6c + 0x43792af8,uVar48);
      FUN_43902718(DAT_43792c70 + 0x43792b04,uVar48);
      FUN_43561540(DAT_43792c74 + 0x43792b0c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c78)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c7c + 0x43792b28,uVar48);
      FUN_43902718(DAT_43792c80 + 0x43792b34,uVar48);
      FUN_43561540(DAT_43792c84 + 0x43792b3c);
    }
    uVar48 = (uint)(iVar46 - **(int **)(iVar43 + DAT_43792c88)) >> 1;
    if (uVar48 < uVar53) {
      FUN_4378eb78(3,9,1,DAT_43792c8c + 0x43792b58,uVar48);
      FUN_43902718(DAT_43792c90 + 0x43792b64,uVar48);
      FUN_43561540(DAT_43792c94 + 0x43792b6c);
    }
  }
  iVar46 = DAT_43792c98;
  if (param_1 != **(int **)(DAT_43792c98 + 0x43792b7a)) {
    iVar43 = thunk_FUN_436cd00c();
    puVar37 = *(undefined4 **)(iVar46 + 0x43792b7a);
    uVar48 = (uint)(iVar43 - puVar37[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43792c9c + 0x43792b96,param_1,*puVar37,uVar48);
    FUN_43902718(DAT_43792ca0 + 0x43792bac,param_1,**(undefined4 **)(iVar46 + 0x43792b7a),uVar48);
    FUN_4378f988(3,0,uVar48);
    if ((*(byte *)(iVar44 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43792ca4 + 0x43792bc8);
    }
    if ((*(byte *)(iVar44 + 0x1b) & 2) == 0) {
      return;
    }
    FUN_4378ec60();
    return;
  }
  FUN_43ae1292(4);
  iVar46 = FUN_43ae8d4e();
  if (iVar46 == 0) {
    FUN_43901778();
    if (*(char *)(DAT_43792ca8 + 0x43792bf2) != '\0') {
      *(undefined1 *)(DAT_43792cac + 0x43792bfc) = 1;
    }
    uVar32 = 0;
    puVar35 = (undefined1 *)(DAT_43792cb0 + 0x43792c04);
  }
  else {
    uVar32 = 1;
    puVar35 = (undefined1 *)(DAT_43792cb4 + 0x43792c0c);
  }
  *puVar35 = uVar32;
  if (*(byte *)(iVar44 + 0x20) == 0) {
    psVar38 = (short *)(DAT_437935f4 + 0x43792ccc);
    sVar25 = 0;
  }
  else {
    uVar48 = *(int *)(*(int *)(DAT_43792cb8 + 0x43792c1e) + 0x14) - 1;
    if (uVar48 < 2) {
      sVar25 = *(short *)(DAT_43792cbc + 0x43792c28 + uVar48 * 2);
    }
    else {
      sVar25 = 0x3c;
    }
    sVar25 = sVar25 * (ushort)*(byte *)(iVar44 + 0x20);
    psVar38 = (short *)(&UNK_43792c36 + DAT_43792cc0);
  }
  *psVar38 = sVar25;
  *(int *)(DAT_437935f8 + 0x43792cd8) = *(int *)(DAT_437935f8 + 0x43792cd8) + 1;
  *(undefined1 *)(DAT_437935fc + 0x43792ce6) = 0;
  FUN_4378f7a0(0x708);
  iVar46 = FUN_437999e4(1,1);
  if (((iVar46 != 0) || (iVar46 = FUN_437999e4(1,2), iVar46 != 0)) &&
     ((iVar46 = DAT_43793608, *(ushort *)(DAT_43793600 + 0x43793376) < 2 ||
      (*(int *)(*(int *)(DAT_43793604 + 0x43792d18) + 0xc) != 0)))) {
    iVar49 = DAT_4379360c + 0x43792d26;
    FUN_43aef52c(iVar49,DAT_43793608 + 0x43793fb4);
    FUN_437d9a04((int)&DAT_437946b4 + iVar46,iVar49);
    if (((*(byte *)(iVar44 + 0x16) & 5) == 4) && (*(int *)(iVar46 + 0x43793598) != 0)) {
      FUN_43ad53b8(iVar46 + 0x4379359c,*(int *)(iVar46 + 0x43793598),0);
    }
  }
  iVar46 = DAT_43793610;
  FUN_43a0cb54();
  FUN_43b2a04a();
  puVar47 = (ushort *)(iVar46 + 0x43792d68);
  FUN_437fdf5c();
  uVar12 = *(undefined2 *)(iVar46 + 0x43792d7a);
  uVar1 = *puVar47;
  uVar2 = *(undefined2 *)(iVar46 + 0x43792d6c);
  uVar3 = *(undefined2 *)(iVar46 + 0x43792d78);
  uVar4 = *(undefined2 *)(iVar46 + 0x43792d74);
  uVar8 = *(undefined2 *)(iVar46 + 0x43792d76);
  uVar5 = *(undefined2 *)(iVar46 + 0x43792d7c);
  uVar6 = *(undefined2 *)(iVar46 + 0x43792d6a);
  uVar9 = *(undefined2 *)(iVar46 + 0x43792d70);
  uVar7 = *(undefined2 *)(iVar46 + 0x43792d7e);
  uVar10 = *(undefined2 *)(iVar46 + 0x43792d6e);
  uVar11 = *(undefined2 *)(iVar46 + 0x43792d72);
  FUN_43804c5c(puVar47);
  *(undefined2 *)(iVar46 + 0x43792d6a) = uVar6;
  *(undefined2 *)(iVar46 + 0x43792d6c) = uVar2;
  *(undefined2 *)(iVar46 + 0x43792d74) = uVar4;
  *(undefined2 *)(iVar46 + 0x43792d7e) = uVar7;
  iVar49 = DAT_43793614;
  *(undefined2 *)(iVar46 + 0x43792d76) = uVar8;
  *(undefined2 *)(iVar46 + 0x43792d7a) = uVar12;
  piVar50 = (int *)(iVar49 + 0x43792dca);
  *(undefined2 *)(iVar46 + 0x43792d78) = uVar3;
  *(undefined2 *)(iVar46 + 0x43792d7c) = uVar5;
  *puVar47 = uVar1;
  *(undefined2 *)(iVar46 + 0x43792d70) = uVar9;
  *(undefined2 *)(iVar46 + 0x43792d6e) = uVar10;
  *(undefined2 *)(iVar46 + 0x43792d72) = uVar11;
  FUN_43ae8fa2();
  FUN_43ae8f98();
  FUN_437fc404(piVar50);
  FUN_437fc54c(1);
  FUN_4375dd04();
  iVar46 = FUN_437fc54c(0);
  FUN_4380c7f8(iVar46,auStack_38);
  bVar56 = false;
  if ((bStack_34 & 0x20) != 0) {
    iVar49 = *(int *)(iVar49 + 0x43792dd6);
    if (*(uint *)(iVar49 + 0xc) < 2) {
      bVar56 = false;
      if (*(char *)(iVar49 + 0x11) != '\0') {
        bVar56 = *(int *)(*piVar50 + 0x2c4) != 0;
      }
    }
    else {
      bVar56 = false;
    }
  }
  iVar49 = FUN_43b00cb4(uVar13);
  if ((((iVar49 == 1) && (iVar46 == 0x110)) &&
      (sVar25 = *(short *)(*(int *)(DAT_43793618 + 0x43792e4a) + 0x240), sVar25 != 0x110)) &&
     (sVar25 != 0x101)) {
    bVar57 = sVar25 != 0x100;
  }
  else {
    bVar57 = false;
  }
  if ((((*(int *)(*(int *)(DAT_4379361c + 0x43792e6c) + 0xc) == 1) ||
       (*(uint *)(DAT_43793620 + 0x43793446) < 2)) || (bVar56)) && (!bVar57)) {
    uVar12 = FUN_437fc54c();
    iVar46 = DAT_43793624;
    *(undefined2 *)(DAT_43793624 + 0x43792e90) = uVar12;
    uVar12 = FUN_437fc54c(2);
    *(undefined2 *)(iVar46 + 0x43792e92) = uVar12;
    uVar12 = FUN_437fc54c(1);
    *(undefined2 *)(iVar46 + 0x43792e94) = uVar12;
    uVar12 = FUN_437fc54c(3);
    *(undefined2 *)(iVar46 + 0x43792e96) = uVar12;
    uVar12 = FUN_437fc54c(5);
    *(undefined2 *)(iVar46 + 0x43792e9a) = uVar12;
    uVar12 = FUN_437fc54c(4);
    *(undefined2 *)(iVar46 + 0x43792e98) = uVar12;
    uVar12 = FUN_437fc54c(6);
    *(undefined2 *)(iVar46 + 0x43792e9c) = uVar12;
    uVar12 = FUN_437fc54c(8);
    *(undefined2 *)(iVar46 + 0x43792e9e) = uVar12;
    uVar12 = FUN_437fc54c(10);
    *(undefined2 *)(iVar46 + 0x43792ea2) = uVar12;
    uVar12 = FUN_437fc54c(9);
    *(undefined2 *)(iVar46 + 0x43792ea0) = uVar12;
    uVar12 = FUN_437fc54c(0xc);
    iVar49 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x14);
    iVar39 = *(int *)(*(int *)(DAT_43793628 + 0x43792eea) + 0x34);
    *(undefined2 *)(iVar46 + 0x43792ea6) = uVar12;
    if (iVar49 == iVar39) {
      uVar12 = FUN_437fc54c(0xb);
      *(undefined2 *)(iVar46 + 0x43792ea4) = uVar12;
    }
    FUN_4380c7f8(*(undefined2 *)(DAT_4379362c + 0x43792f00),(int)&DAT_43793708 + DAT_4379362c);
  }
  iVar49 = DAT_43793638;
  iVar46 = DAT_43793634;
  iVar39 = *(int *)(DAT_43793630 + 0x43792f1a);
  if (*(int *)(*(int *)(DAT_43793630 + 0x43792f12) + 0xb4) == 1) {
    puVar35 = (undefined1 *)(DAT_43793634 + 0x43792f2a);
    *(undefined1 *)(DAT_43793638 + 0x43792f2c) = *puVar35;
    *(undefined1 *)(iVar49 + 0x43792f2d) = *(undefined1 *)(iVar46 + 0x43792f2b);
    FUN_43796044(puVar35);
    iVar40 = 0;
    if (*(char *)(iVar46 + 0x43792f2b) != '\0') {
      if (*(char *)(iVar49 + 0x43792f2d) != '\0') goto LAB_43792f54;
      iVar46 = FUN_4378f9b4();
      iVar40 = **(int **)(iVar46 + 4) + 5;
    }
    *(int *)(iVar39 + 0x204) = iVar40;
  }
LAB_43792f54:
  iVar49 = FUN_43b00cba(uVar13);
  iVar46 = DAT_4379363c;
  if (iVar49 != 0) {
    FUN_43b00dd4(uVar13);
    FUN_43805b04(uVar13,iVar46 + 0x43792f6e,DAT_43793640 + 0x43792f72,DAT_43793640 + 0x43793516);
    FUN_43b00e40(uVar13,iVar46 + 0x43792f6e);
  }
  iVar46 = DAT_43793648;
  piVar50 = (int *)(DAT_43793648 + 0x43792f96);
  iVar49 = (int)&DAT_43794dfc + DAT_43793644;
  FUN_437da078(piVar50,iVar49);
  FUN_43ae7564(piVar50,iVar49);
  iVar49 = *piVar50;
  if (*(int *)(iVar49 + 0xb4) == 2) {
    iVar46 = *(int *)(iVar46 + 0x43792f9e);
    *(undefined4 *)(iVar46 + 0x204) = *(undefined4 *)(iVar46 + 0x238);
    *(undefined1 *)(iVar46 + 0x202) = *(undefined1 *)(iVar46 + 0x234);
  }
  bVar34 = *(byte *)(DAT_4379364c + 0x437937d9) & 0x40;
  if (((*(byte *)(DAT_4379364c + 0x437937d9) & 0x40) != 0) &&
     (bVar34 = 1, *(int *)(iVar49 + 0x30) != 1)) {
    bVar34 = 0;
  }
  *(byte *)(DAT_4379364c + 0x4379378c) = bVar34;
  if ((*(char *)(DAT_43793654 + 0x43792fee) != *(char *)(DAT_43793650 + 0x437937ac)) ||
     (*(int *)(DAT_43793658 + 0x43793000) != *(int *)(iVar49 + 0x34))) {
    FUN_43901a8c(4,0x203e,*(char *)(DAT_43793650 + 0x437937ac),*(undefined4 *)(iVar49 + 0x34));
    *(undefined1 *)(DAT_43793660 + 0x4379301e) = *(undefined1 *)(DAT_4379365c + 0x437937dc);
    *(undefined4 *)(DAT_43793668 + 0x43793032) =
         *(undefined4 *)(*(int *)(DAT_43793664 + 0x4379302e) + 0x34);
  }
  iVar49 = DAT_4379368c;
  iVar46 = DAT_43793688;
  if ((*(byte *)(*(int *)(DAT_4379366c + 0x43793044) + 0x266) & 0x20) == 0) {
    *(undefined4 *)(DAT_43793690 + 0x437938aa) = 0;
  }
  else {
    psVar38 = (short *)(DAT_43793670 + 0x43793052);
    if ((ushort)(*psVar38 - 0x148U) < 2) {
      if (*(int *)(DAT_43793670 + 0x43793116) - 8U < 4) {
                    /* WARNING: Could not recover jumptable at 0x43793066. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_43793066::switchdataD_4379306a +
                  (uint)*(byte *)(*(int *)(DAT_43793670 + 0x43793116) + 0x43793062) * 2))();
        return;
      }
    }
    else {
      if ((*(char *)(DAT_43793670 + 0x43793812) == '\0') ||
         (*(int *)(*(int *)(DAT_4379366c + 0x4379303c) + 0x34) != 0)) {
        uVar14 = 0;
        psVar38 = (short *)(DAT_43793684 + 0x437930c6);
      }
      else if (*(int *)(DAT_43793670 + 0x43793116) == 8) {
        uVar14 = 1;
      }
      else {
        uVar14 = 0;
        if (*(int *)(DAT_43793670 + 0x43793116) == 9) {
          uVar14 = 2;
        }
      }
      *(undefined4 *)(psVar38 + 0x3d6) = uVar14;
      iVar39 = *(int *)(iVar46 + 0x4379387c);
      if (*(int *)(iVar49 + 0x437930d6) != iVar39) {
        FUN_43901a8c(4,0x203f,iVar39,0);
        *(int *)(iVar49 + 0x437930d6) = *(int *)(iVar46 + 0x4379387c);
      }
    }
  }
  iVar49 = DAT_437936a0;
  iVar46 = DAT_4379369c;
  if (((*(uint *)(DAT_43793694 + 0x43793910) & 0xf8000) == 0x38000) &&
     (*(int *)(*(int *)(DAT_43793698 + 0x4379311c) + 0x474) == 2)) {
    uVar32 = 1;
  }
  else {
    uVar32 = 0;
  }
  *(undefined1 *)(DAT_43793694 + 0x437938f1) = uVar32;
  cVar33 = *(char *)(iVar46 + 0x4379391f);
  if (*(char *)(iVar49 + 0x4379313c) != cVar33) {
    FUN_43901a8c(4,0x2043,cVar33,0);
    *(char *)(iVar49 + 0x4379313c) = *(char *)(iVar46 + 0x4379391f);
  }
  iVar46 = DAT_437936a8;
  uVar48 = *(byte *)(DAT_437936a4 + 0x4379396a) & 7;
  if (uVar48 - 1 < 6) {
                    /* WARNING: Could not recover jumptable at 0x43793170. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43793170::switchdataD_43793174 + (uint)*(byte *)(uVar48 + 0x43793173) * 2))
              ();
    return;
  }
  *(undefined4 *)(DAT_437936a8 + 0x43793908) = 0;
  *(undefined4 *)(iVar46 + 0x437938fc) = *(undefined4 *)(*(int *)(DAT_437936ac + 0x43793192) + 0x30)
  ;
  *(undefined4 *)(iVar46 + 0x4379390c) = 1;
  iVar49 = DAT_437936e4;
  iVar46 = DAT_437936e0;
  piVar50 = (int *)(DAT_437936e4 + 0x437932b4);
  iVar39 = FUN_43ae8c50(*(undefined4 *)(DAT_437936e0 + 0x43793a2a));
  iVar49 = *(int *)(*(int *)(iVar49 + 0x437932b8) + 0x14);
  *(int *)(iVar46 + 0x43793a2e) = iVar39;
  *(bool *)(iVar46 + 0x43793a32) = iVar39 != iVar49;
  iVar49 = FUN_436e9234();
  iVar40 = *piVar50;
  iVar39 = *(int *)(iVar40 + 0x178);
  uVar14 = *(undefined4 *)(DAT_437936e8 + 0x437932e2 + (iVar49 * 3 + *(int *)(iVar40 + 0x174)) * 4);
  *(int *)(iVar46 + 0x43793a62) = iVar39;
  *(undefined4 *)(iVar46 + 0x43793a66) = uVar14;
  bVar34 = *(byte *)(iVar40 + 0x17c);
  iVar49 = *(int *)(DAT_437936ec + 0x43793300);
  *(uint *)(iVar46 + 0x43793a6a) = (uint)bVar34;
  iVar46 = DAT_437936f4;
  if ((iVar49 != iVar39) || (*(uint *)(DAT_437936f0 + 0x4379330e) != (uint)bVar34)) {
    FUN_439d88c4();
    FUN_43901a8c(4,0x2030,*(undefined4 *)(iVar46 + 0x43793ad2),0xff);
    uVar15 = *(undefined4 *)(*(int *)(DAT_437936f8 + 0x43793330) + 0x174);
    uVar14 = FUN_436e9234();
    FUN_43901a8c(4,0x2031,uVar15,uVar14);
    FUN_43901a8c(4,0x203c,*(undefined4 *)(iVar46 + 0x43793386),*(undefined4 *)(iVar46 + 0x43793ada))
    ;
    *(undefined4 *)(DAT_437936fc + 0x43793360) = *(undefined4 *)(iVar46 + 0x43793ad2);
    *(undefined4 *)(DAT_43793700 + 0x4379336a) = *(undefined4 *)(iVar46 + 0x43793ada);
  }
  if ((*(char *)(DAT_43793704 + 0x43793370) == '\0') &&
     ((((sVar25 = *(short *)(DAT_43793708 + 0x4379337a), sVar25 == 0x11a || (sVar25 == 0x118)) ||
       (sVar25 == 0x102)) || (((sVar25 == 0x11b || (sVar25 == 0x119)) || (sVar25 == 0x107)))))) {
    if (*(int *)(*(int *)(DAT_4379370c + 0x437933a6) + 0x174) == 1) {
      FUN_439c5a04(auStack_54,0,9);
      uStack_52 = 0x40d4;
      uStack_4c = (undefined1)*(undefined4 *)(DAT_43793710 + 0x43793b7e);
      auStack_54[0] = 5;
      FUN_435aa02c(auStack_2c);
      FUN_435a92e0(auStack_218);
      iVar46 = FUN_43a49628(auStack_218,DAT_437935f0);
      if (iVar46 == 0) {
        iVar46 = FUN_435a9304(auStack_218,auStack_54,9);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_4379371c + 0x43793428,iVar46);
          iVar49 = DAT_43793720 + 0x43793430;
          goto LAB_43793456;
        }
        iVar46 = FUN_435aa20c(auStack_2c,DAT_437935f0,auStack_218);
        if (iVar46 != 0) {
          FUN_4378eb78(3,9,1,DAT_43793724 + 0x43793450,iVar46);
          iVar49 = DAT_43793728 + 0x43793458;
          goto LAB_43793456;
        }
      }
      else {
        FUN_4378eb78(3,9,1,DAT_43793714 + 0x43793400,iVar46);
        iVar49 = DAT_43793718 + 0x43793408;
LAB_43793456:
        FUN_43902718(iVar49,iVar46);
      }
      FUN_435a92c8(auStack_218);
      FUN_435aa014(auStack_2c);
    }
    *(undefined1 *)(DAT_4379372c + 0x43793474) = 1;
  }
  iVar49 = DAT_43793734;
  iVar46 = DAT_43793730;
  piVar50 = (int *)(DAT_43793734 + 0x43793480);
  FUN_437c1740(piVar50,DAT_43793730 + 0x43794bae);
  uVar48 = (*(byte *)(iVar46 + 0x43793c86) & 0x3f) >> 4;
  if (uVar48 == 1) {
    *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
    *(undefined4 *)(iVar46 + 0x43793bea) = *(undefined4 *)(iVar46 + 0x437938e6);
    *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
    *(undefined1 *)(iVar46 + 0x43793a46) = 0;
    *(undefined4 *)(iVar46 + 0x43793a4a) = 0;
    *(undefined4 *)(iVar46 + 0x437934c6) = 0;
    iVar49 = FUN_43794a44(piVar50);
    if (iVar49 != 0) {
      if (*(uint *)(iVar46 + 0x437938d6) < 4) {
                    /* WARNING: Could not recover jumptable at 0x437935c4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)(&switchD_437935c4::switchdataD_437935c8 +
                  (uint)(&switchD_437935c4::switchdataD_437935c8)[*(uint *)(iVar46 + 0x437938d6)] *
                  2))();
        return;
      }
      iVar46 = DAT_437942c0 + 0x43793788;
      FUN_4378eb78(5,0,1,DAT_437942bc + 0x43793786,iVar46,0x93c);
      FUN_43902718(DAT_437942c4 + 0x437937a0,iVar46,0x93c);
    }
    goto LAB_437937a2;
  }
  if (uVar48 == 2) {
    iVar39 = *piVar50;
    if (*(int *)(*(int *)(iVar49 + 0x43793484) + 0x10) == *(int *)(iVar39 + 0x20)) {
      uVar14 = *(undefined4 *)(iVar39 + 0x24);
      *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar39 + 0x1c);
      iVar49 = *(int *)(iVar39 + 0x28);
      *(undefined4 *)(iVar46 + 0x43793a4a) = uVar14;
      *(int *)(iVar46 + 0x43793a42) = iVar49;
      if ((*(ushort *)(iVar46 + 0x43793c86) & 0x1c0) == 0) {
        *(byte *)(iVar46 + 0x43793a46) =
             (byte)(((uint)*(ushort *)(iVar46 + 0x43793c86) << 0x17) >> 0x1d);
        if (((iVar49 == 1) &&
            ((*(int *)(iVar39 + 0x538) != 1 || (*(int *)(iVar46 + 0x43793bf6) != 0)))) &&
           (*(char *)(DAT_43793738 + 0x43793ccf) == '\0')) {
          *(undefined1 *)(DAT_43793738 + 0x43793aae) = 1;
        }
      }
      else {
        *(undefined1 *)(iVar46 + 0x43793a46) = 0;
      }
    }
    iVar46 = DAT_4379373c + 0x437934fe;
    uVar14 = *(undefined4 *)(DAT_4379373c + 0x4379396e);
    goto LAB_43793588;
  }
  *(undefined4 *)(iVar46 + 0x43793a3e) = *(undefined4 *)(iVar46 + 0x4379349a);
  *(undefined4 *)(iVar46 + 0x43793a42) = *(undefined4 *)(iVar46 + 0x437934a6);
  *(undefined1 *)(iVar46 + 0x43793a46) = 0;
  iVar49 = FUN_43794a44(piVar50);
  if (iVar49 == 0) {
    uVar14 = *(undefined4 *)(iVar46 + 0x437934c6);
  }
  else {
    uVar14 = *(undefined4 *)(iVar46 + 0x437938d6);
  }
  switch(uVar14) {
  case 0:
    uVar14 = 0;
    iVar46 = DAT_43793740 + 0x43793538;
    break;
  case 1:
    iVar46 = DAT_43793748 + 0x43793546;
    goto LAB_4379357a;
  case 2:
    uVar14 = 2;
    iVar46 = DAT_43793744 + 0x43793540;
    break;
  case 3:
    uVar14 = 4;
    iVar46 = DAT_4379374c + 0x4379354e;
    break;
  default:
    iVar46 = DAT_43793754 + 0x4379355e;
    FUN_4378eb78(5,0,1,DAT_43793750 + 0x4379355a,iVar46,0x91e);
    FUN_43902718(DAT_43793758 + 0x43793574,iVar46,0x91e);
    iVar46 = DAT_4379375c + 0x4379357c;
LAB_4379357a:
    uVar14 = 1;
  }
  *(undefined4 *)(iVar46 + 0x5cc) = uVar14;
  iVar46 = DAT_43793760 + 0x43793586;
  uVar14 = *(undefined4 *)(DAT_43793760 + 0x437939ee);
LAB_43793588:
  *(undefined4 *)(iVar46 + 0x76c) = uVar14;
LAB_437937a2:
  puVar51 = (uint *)(DAT_437942cc + 0x437937b6);
  FUN_4380f440(DAT_437942d0 + 0x437937bc,puVar51,DAT_437942c8 + 0x43793d54,0);
  if (*(byte *)(iVar44 + 0xb3) != 0) {
    *puVar51 = (uint)*(byte *)(iVar44 + 0xb3);
  }
  iVar46 = DAT_437942dc;
  iVar39 = DAT_437942dc + 0x437937de;
  FUN_4380e0cc(DAT_437942d4 + 0x437937da,DAT_437942d8 + 0x437937dc);
  FUN_4380e138(iVar39);
  iVar49 = DAT_437942e4;
  if ((uint)*(byte *)(DAT_437942e0 + 0x437937f0) != (int)(char)*(byte *)(iVar46 + 0x437937e3)) {
    *(byte *)(DAT_437942e0 + 0x437937f0) = *(byte *)(iVar46 + 0x437937e3);
    FUN_43ae913c(auStack_68,iVar49 + 0x43793804);
    FUN_439018b0(DAT_437942e8 + 0x43793814,auStack_68,iVar39,0);
  }
  iVar46 = DAT_437942ec;
  if ((1 < *(uint *)(DAT_437942ec + 0x43793df0)) &&
     (uVar48 = *(uint *)(*(int *)(DAT_437942f0 + 0x43793836) + 0xc),
     (*(uint *)(DAT_437942ec + 0x43793fac) & 1) != uVar48)) {
    if (uVar48 == 0) {
      uVar14 = 2;
    }
    else {
      uVar14 = 1;
    }
    *(undefined4 *)(DAT_437942ec + 0x43793fac) = uVar14;
    *(undefined4 *)(iVar46 + 0x43793fbc) = uVar14;
    FUN_4378ea78(0);
  }
  iVar49 = DAT_437942f8;
  iVar46 = DAT_437942f4;
  if (*(int *)(DAT_437942f4 + 0x43793fd2) == *(int *)(DAT_437942f4 + 0x43793dea)) {
    uVar48 = *(uint *)(*(int *)(DAT_437942f8 + 0x43793872) + 0x3c);
    if (uVar48 == 0) {
      iVar39 = FUN_43b00cba(uVar13);
      if ((((iVar39 == 0) || (*(int *)(iVar46 + 0x43793912) != 1)) ||
          ((*(byte *)(iVar46 + 0x4379401e) & 1) == 0)) ||
         (*(int *)(*(int *)(iVar49 + 0x43793872) + 0xc) != 0)) {
        iVar49 = FUN_43b039fc(DAT_43794624 + 0x437945c4,DAT_43794628 + 0x437945c6);
        iVar46 = DAT_43794308;
        if (iVar49 == 0) {
          if (bVar56) {
            FUN_4378ea78();
            iVar46 = DAT_43794304;
            *(undefined4 *)(DAT_43794304 + 0x437940aa) = 0;
            *(undefined4 *)(iVar46 + 0x437940ba) = 0;
          }
          else if ((*(short *)(DAT_43794308 + 0x43793932) == 0x121) ||
                  (*(short *)(DAT_43794308 + 0x43793932) == 300)) {
            FUN_4378ea78(0);
            iVar46 = DAT_4379430c;
            *(undefined4 *)(DAT_4379430c + 0x437940d8) = 0;
            *(undefined4 *)(iVar46 + 0x437940e8) = 0;
          }
          else if (*(uint *)(DAT_43794308 + 0x43793f02) < 2) {
            if (*(int *)(*(int *)(DAT_43794310 + 0x43793968) + 0xc) == 0) {
              uVar14 = 0;
LAB_43793978:
              FUN_4378ea78();
              *(undefined4 *)(iVar46 + 0x437940be) = uVar14;
              *(undefined4 *)(iVar46 + 0x437940ce) = uVar14;
            }
          }
          else {
            uVar14 = 1;
            if (*(int *)(*(int *)(DAT_43794314 + 0x43793976) + 0xc) == 1) goto LAB_43793978;
          }
        }
        else {
          FUN_4380c7f8(uVar1,auStack_40);
          iVar46 = DAT_43794318;
          if (((bVar56) && (uVar48 = bStack_3c & 0x20, (bStack_3c & 0x20) == 0)) &&
             (*(int *)(DAT_43794318 + 0x43794132) != 0)) {
            FUN_4378ea78(uVar48);
            *(uint *)(iVar46 + 0x43794132) = uVar48;
            *(uint *)(iVar46 + 0x43794142) = uVar48;
          }
        }
      }
      else {
        FUN_4378ea78(0);
        *(undefined4 *)(iVar46 + 0x43793fe6) = 0;
        *(undefined4 *)(iVar46 + 0x43793ff6) = 0;
        *(byte *)(iVar46 + 0x4379401e) = *(byte *)(iVar46 + 0x4379401e) & 0xfe;
      }
    }
    else {
      uVar53 = *(int *)(*(int *)(DAT_437942f8 + 0x43793876) + 0x1e8) + 1;
      if (uVar48 <= uVar53) {
        if (uVar48 == uVar53) {
          iVar49 = FUN_43b039fc(DAT_437942fc + 0x43793892,DAT_43794300 + 0x43793894);
          if (iVar49 == 0) {
            *(undefined4 *)(iVar46 + 0x43793ff6) = *(undefined4 *)(iVar46 + 0x43793fe6);
            FUN_4378ea78();
          }
        }
        else {
          FUN_4378ea78(0);
          iVar49 = *(int *)(*(int *)(iVar49 + 0x43793872) + 0x3c) + -1;
          *(int *)(iVar46 + 0x43793fe6) = iVar49;
          *(int *)(iVar46 + 0x43793ff6) = iVar49;
        }
      }
    }
  }
  iVar46 = DAT_43794324;
  uVar48 = *(uint *)(DAT_4379431c + 0x43793ece);
  if (*(byte *)(iVar44 + 1) - 1 < 4) {
                    /* WARNING: Could not recover jumptable at 0x437939ca. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_437939ca::switchdataD_437939ce +
              (uint)*(byte *)(*(byte *)(iVar44 + 1) + 0x437939cd) * 2))();
    return;
  }
  if (((uint)*(byte *)(DAT_43794320 + 0x43794150) != (uVar48 & 3) >> 1) ||
     ((uint)*(byte *)(DAT_43794320 + 0x43794151) != (uVar48 & 1))) {
    *(byte *)(DAT_43794324 + 0x4379416a) = (byte)((uVar48 << 0x1e) >> 0x1f);
    *(char *)(iVar46 + 0x4379416b) = (char)(uVar48 & 1);
    FUN_4378ea78(0);
  }
  iVar44 = FUN_43ae8d4e();
  if ((iVar44 == 0) || (*(char *)(DAT_43794328 + 0x43793a22) != '\0')) {
    FUN_4378ea78(1);
    *(undefined1 *)(DAT_4379432c + 0x43793a34) = 0;
  }
  uVar14 = *(undefined4 *)(iVar43 + DAT_43794330);
  iVar44 = FUN_43ae8cc8(uVar14);
  if (iVar44 != 0) {
    *(undefined4 *)(DAT_43794334 + 0x437941e6) = *(undefined4 *)(DAT_43794334 + 0x437941d6);
  }
  iVar44 = DAT_43794338;
  uVar48 = *(uint *)(DAT_43794338 + 0x437941e6);
  cVar33 = '\x01' - (char)uVar48;
  if (1 < uVar48) {
    cVar33 = '\0';
  }
  *(bool *)(DAT_43794338 + 0x437941ea) = 1 >= uVar48;
  *(char *)(iVar44 + 0x437941eb) = cVar33;
  cVar33 = '\x01' - (char)*(uint *)(iVar44 + 0x437941f6);
  if (1 < *(uint *)(iVar44 + 0x437941f6)) {
    cVar33 = '\0';
  }
  *(char *)(iVar44 + 0x437941fa) = cVar33;
  uVar32 = FUN_43ae8ccc(uVar14);
  *(undefined1 *)(iVar44 + 0x4379553b) = uVar32;
  if ((*(byte *)(iVar44 + 0x43794264) & 0x10) == 0) {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_43794340 + 0x43793abc) + 4);
  }
  else {
    uStack_30 = *(undefined4 *)(*(int *)(DAT_4379433c + 0x43793ab0) + 0xc);
  }
  iVar44 = FUN_43b00cba(uVar13);
  if ((iVar44 != 0) && (*(int *)(*(int *)(DAT_43794344 + 0x43793ac6) + 0xb8) == 1)) {
    FUN_43b00e4c(uVar13,(int *)(DAT_43794344 + 0x43793ac6),&uStack_30);
  }
  iVar46 = DAT_4379434c;
  iVar44 = DAT_43794348;
  uVar13 = FUN_4380e15c(DAT_43794348 + 0x43793ae4,uStack_30,DAT_43794350 + 0x43793b00,
                        *(int *)(DAT_4379434c + 0x43794276) +
                        *(int *)(*(int *)(DAT_43794348 + 0x43793ae8) + 0xc) & 1);
  *(undefined4 *)(iVar46 + 0x437940ca) = uVar13;
  iVar49 = FUN_437955ec();
  iVar39 = *(int *)(iVar43 + DAT_43794354);
  if (iVar49 == 1) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    if (*(char *)(iVar46 + 0x4379428a) != '\0') {
      *(char *)(iVar46 + 0x43794282) = *(char *)(iVar46 + 0x43794282) + '\x01';
    }
  }
  else if (iVar49 == 2) {
    if (((*(byte *)(iVar39 + 0x22) & 1) == 0) &&
       (uVar48 = *(uint *)(*(int *)(iVar44 + 0x43793af0) + 8), *(ushort *)(iVar46 + 0x4379415a) < 2)
       ) {
      if (*(char *)(iVar46 + 0x4379427b) == '\0') {
        iVar44 = *(int *)(iVar46 + 0x437940ba);
      }
      else {
        iVar44 = *(int *)(iVar46 + 0x437940ca);
      }
      if (iVar44 != 0) {
        if (iVar44 == 1) {
          uVar53 = 1;
        }
        else {
          uVar53 = 2;
        }
        if (uVar48 < uVar53) {
          uVar48 = uVar53;
        }
      }
      if ((1 < uVar48) &&
         (uVar48 = FUN_43acf19e(uVar48,2),
         (*(int *)((int)&DAT_43794338 + DAT_4379435c) +
          *(int *)(*(int *)(DAT_43794358 + 0x43793b9e) + 0xc) & 1U) != 0)) {
        uVar48 = 1;
      }
      *(uint *)((int)&DAT_43794348 + DAT_43794360 + 2) = uVar48;
    }
    else {
      *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
    }
    if (*(char *)((int)&DAT_43794360 + DAT_43794364) != '\0') {
      *(char *)((int)&DAT_43794358 + DAT_43794364) =
           *(char *)((int)&DAT_43794358 + DAT_43794364) + '\x01';
    }
  }
  else if (iVar49 == 0) {
    *(undefined4 *)(iVar46 + 0x4379427e) = *(undefined4 *)(iVar46 + 0x437940ca);
  }
  iVar44 = DAT_43794368;
  if (*(int *)(DAT_43794368 + 0x437941be) != 0x11) {
    uVar13 = *(undefined4 *)((int)&DAT_43794338 + DAT_43794368 + 2);
    if (*(int *)((int)&DAT_437943d4 + DAT_43794368 + 2) != 0) {
      uVar13 = 10;
    }
    uVar13 = FUN_43acc1a6(*(int *)(DAT_43794368 + 0x437941be),uVar13);
    *(undefined4 *)((int)&DAT_4379433c + iVar44 + 2) = uVar13;
  }
  iVar46 = DAT_4379436c + 0x43793bfc;
  iVar44 = *(int *)(DAT_4379436c + 0x437941e4);
  if ((iVar44 == 0x12) || (iVar44 == 0x3f)) {
    uVar13 = 1;
    iVar46 = DAT_43794370 + 0x43793c18;
  }
  else if (iVar44 == 8) {
    uVar13 = 2;
  }
  else {
    uVar13 = *(undefined4 *)(*(int *)(iVar43 + DAT_43794374) + 0x40);
  }
  *(undefined4 *)(iVar46 + 0x5a4) = uVar13;
  if (*(char *)(*(int *)(iVar43 + DAT_43794378) + 0x43) == '\x01') {
    iVar44 = DAT_4379437c + 0x43793c3a;
    bVar34 = 1;
  }
  else {
    bVar34 = 0;
    if (*(char *)(DAT_43794380 + 0x43793d1e) != '\0') {
      bVar34 = (byte)FUN_43795a08[DAT_43794380 + 2] ^ 1;
    }
    iVar44 = DAT_43794384 + 0x43793c58;
  }
  *(byte *)(iVar44 + 0x770) = bVar34;
  if (*(char *)(DAT_43794388 + 0x43795a2a) == '\0') {
    uVar13 = *(undefined4 *)(*(int *)(DAT_4379438c + 0x43793c74) + 0xbc);
  }
  else {
    uVar13 = 1;
  }
  *(undefined4 *)((int)&DAT_437943d4 + DAT_43794388 + 2) = uVar13;
  cVar33 = *(char *)(DAT_43794390 + 0x43794258);
  if (*(char *)((int)&DAT_43794414 + DAT_43794390 + 1) != '\0') {
    cVar33 = cVar33 + '\x01';
  }
  *(char *)(DAT_43794390 + 0x43794269) = cVar33;
  uVar13 = FUN_43ae8d10(uVar14);
  iVar44 = DAT_43794394;
  piVar52 = (int *)(DAT_43794398 + 0x43793ca6);
  *(undefined4 *)(DAT_43794394 + 0x43794510) = uVar13;
  uVar13 = FUN_43ae8d14(uVar14);
  iVar46 = *piVar52;
  *(undefined4 *)(iVar44 + 0x43794514) = uVar13;
  piVar50 = (int *)(DAT_4379439c + 0x43793cbc);
  if (*piVar50 != iVar46) {
    FUN_43901a8c(4,0x203d);
    *piVar52 = *piVar50;
  }
  iVar40 = DAT_437943ac;
  iVar49 = DAT_437943a8;
  iVar46 = DAT_437943a4;
  iVar44 = DAT_437943a0;
  if ((*(byte *)(iVar39 + 3) & 1) != 0) {
    puVar45 = (undefined2 *)(DAT_437943a4 + 0x43793cec);
    puVar37 = (undefined4 *)(DAT_437943a8 + 0x43793cf4);
    uVar26 = *(undefined4 *)(DAT_437943a4 + 0x43794478);
    puVar54 = (undefined4 *)(DAT_437943ac + 0x43793cfa);
    uVar13 = *(undefined4 *)((int)&DAT_437942cc + DAT_437943a4);
    uVar36 = **(undefined4 **)(DAT_437943a0 + 0x43793cea);
    uVar41 = (*(undefined4 **)(DAT_437943a0 + 0x43793cea))[3];
    uVar55 = *(undefined4 *)((int)&DAT_437942bc + DAT_437943a4);
    uVar15 = FUN_437955ec();
    uVar27 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar46 + 0x43794488);
    iVar18 = *(int *)(iVar44 + 0x43793cea);
    uVar28 = *(undefined4 *)(iVar18 + 0x10);
    uVar29 = *(undefined4 *)(iVar18 + 0x30);
    uVar19 = *(undefined4 *)(iVar18 + 0x3c);
    uVar12 = *puVar45;
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar20 = *puVar37;
    uVar30 = *puVar54;
    uVar21 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar31 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar22 = FUN_43ae8cd0(uVar14);
    uVar23 = FUN_43ae8cc8(uVar14);
    uVar24 = FUN_43ae8ccc(uVar14);
    FUN_4378eb78(3,9,1,DAT_437943b0 + 0x43793dcc,uVar36,uVar41,uVar55,uVar13,uVar26,uVar15,uVar16,
                 uVar27,uVar17,uVar28,uVar29,uVar19,uVar12,uVar2,uVar20,uVar30,uVar21,uVar31,uVar22,
                 uVar23,uVar24);
    uVar22 = *(undefined4 *)((int)&DAT_437942bc + iVar46);
    uVar26 = *(undefined4 *)((int)&DAT_437942cc + iVar46);
    uVar13 = **(undefined4 **)(iVar44 + 0x43793cea);
    uVar28 = (*(undefined4 **)(iVar44 + 0x43793cea))[3];
    uVar29 = *(undefined4 *)(iVar46 + 0x43794478);
    uVar15 = FUN_437955ec();
    iVar44 = *(int *)(iVar44 + 0x43793cea);
    uVar23 = *(undefined4 *)(iVar46 + 0x43794480);
    uVar27 = *(undefined4 *)(iVar46 + 0x43794488);
    uVar55 = *puVar54;
    uVar24 = *(undefined4 *)(iVar44 + 0x10);
    uVar12 = *puVar45;
    uVar41 = *(undefined4 *)(iVar40 + 0x43793d06);
    uVar2 = *(undefined2 *)(iVar46 + 0x437944fc);
    uVar16 = *(undefined4 *)((int)&DAT_437942c4 + iVar46);
    uVar17 = *(undefined4 *)(iVar44 + 0x30);
    uVar30 = *(undefined4 *)(iVar44 + 0x3c);
    uVar31 = *puVar37;
    uVar36 = *(undefined4 *)(iVar49 + 0x43793d00);
    uVar19 = FUN_43ae8cd0(uVar14);
    uVar20 = FUN_43ae8cc8(uVar14);
    uVar21 = FUN_43ae8ccc(uVar14);
    FUN_43902718(DAT_437943b4 + 0x43793e92,uVar13,uVar28,uVar22,uVar26,uVar29,uVar15,uVar16,uVar23,
                 uVar27,uVar24,uVar17,uVar30,uVar12,uVar2,uVar31,uVar55,uVar36,uVar41,uVar19,uVar20,
                 uVar21);
  }
  iVar46 = DAT_437943c4;
  iVar44 = DAT_437943c0;
  uVar13 = FUN_43b039fc(DAT_437943b8 + 0x43793ea0,DAT_437943bc + 0x43793ea6);
  iVar49 = iVar44 + 0x43795d1c;
  FUN_43780080(iVar46 + 0x43793eb6,iVar49,uVar13);
  FUN_4380db04(iVar46 + 0x43793eb6,iVar49);
  FUN_4378c4d0(iVar44 + 0x43794454);
  FUN_4378f7a0(0xb2a);
  iVar44 = FUN_43ae8cd0(uVar14);
  if (iVar44 == 0) {
    FUN_43ae8cda(uVar14);
  }
  iVar46 = DAT_437943cc;
  iVar44 = DAT_437943c8;
  iVar49 = DAT_437943c8 + 0x43793ef4;
  iVar40 = DAT_437943cc + 0x43793ef8;
  FUN_4377e0e8(iVar49);
  FUN_437217f8(*(undefined4 *)(*(int *)(iVar44 + 0x43793ef8) + 0x18));
  FUN_437b4db8(iVar49,iVar46 + 0x43795188);
  FUN_437c194c(iVar49,iVar46 + 0x43795628);
  thunk_FUN_437d0e5c(iVar49,(int)&DAT_437957cc + iVar46);
  FUN_4378f754(iVar40,iVar46 + 0x437959d4);
  FUN_43af6784((int)&DAT_43795888 + iVar46,iVar49);
  FUN_4378f7a0(0xb51);
  pcVar42 = *(char **)(iVar44 + 0x43793f08);
  if (*pcVar42 == '\0') {
    uVar13 = 0;
    if (*(char *)(iVar39 + 0xec) == '\0') {
      uVar13 = *(undefined4 *)(pcVar42 + 4);
    }
  }
  else {
    uVar13 = 0;
  }
  uVar14 = FUN_43814138();
  iVar44 = DAT_437943d0;
  iVar46 = FUN_43799a38(1,1,**(undefined4 **)(DAT_437943d0 + 0x43793f68),0);
  if (iVar46 == 0) {
    iVar44 = FUN_43799a38(1,2,**(undefined4 **)(iVar44 + 0x43793f68),0);
    bVar56 = iVar44 != 0;
  }
  else {
    bVar56 = true;
  }
  uVar13 = FUN_43b03c62(uVar14,uVar13,bVar56);
  *(undefined4 *)(FUN_43794784 + DAT_437943d4 + 4) = uVar13;
  iVar44 = DAT_437943d8;
  if ((*(char *)(iVar39 + 0xed) == '\0') &&
     ((iVar46 = *(int *)(*(int *)(iVar43 + DAT_43794374) + 0x44), iVar46 == 3 || (iVar46 == 4)))) {
    if ((*(ushort *)(*(int *)(DAT_437943d8 + 0x43793fc8) + 0x264) & 0x1ff) >> 6 != 0) {
      uVar13 = FUN_438148f0();
      iVar46 = DAT_437943e0 + 0x43794058;
      uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
      goto LAB_4379405e;
    }
    iVar46 = DAT_437943dc + 0x43793fdc;
    auStack_48[0] = *(undefined1 *)(DAT_437943dc + 0x4379481a);
    uStack_44 = *(undefined4 *)(&UNK_4379459c + DAT_437943dc);
    thunk_FUN_438aaab8(auStack_48,auStack_3a8);
    uVar13 = FUN_438148f0();
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(iVar44 + 0x43793fc4),0);
    puVar58 = auStack_348;
    puVar35 = auStack_3a8;
    puVar59 = auStack_2e0;
    puVar60 = auStack_280;
  }
  else {
    uVar13 = FUN_438148f0();
    iVar46 = DAT_43794630 + 0x437945e4;
    uVar14 = FUN_43799a38(1,10,**(undefined4 **)(DAT_4379462c + 0x437945e6),0);
LAB_4379405e:
    puVar35 = (undefined1 *)0x0;
    uStack_2e8 = 0;
    puVar58 = (undefined1 *)0x0;
    uStack_2e4 = 0;
    puVar59 = (undefined1 *)0x0;
    uStack_220 = 0;
    puVar60 = (undefined1 *)0x0;
    uStack_21c = 0;
  }
  FUN_4381493c(&uStack_3b8,uVar13,puVar35,uStack_2e8,puVar58,uStack_2e4,puVar59,uStack_220,puVar60,
               uStack_21c,uVar14);
  iVar44 = DAT_437943e8;
  iVar49 = DAT_437943e4 + 0x4379408a;
  *(undefined4 *)(iVar46 + 0x7f0) = uStack_3b8;
  *(undefined4 *)(iVar46 + 0x7f4) = uStack_3b4;
  *(undefined4 *)(iVar46 + 0x7f8) = uStack_3b0;
  *(undefined4 *)(iVar46 + 0x7fc) = uStack_3ac;
  iVar46 = DAT_437943ec;
  FUN_43ae8faa(iVar49,DAT_437943ec + 0x43794096);
  FUN_43ae8eae(iVar49,iVar44 + 0x43794090);
  if ((*(uint *)(iVar46 + 0x4379489a) & 4) == 0) {
    FUN_43560da8(0x11,4);
    FUN_43ae9148(auStack_7c,DAT_437943f0 + 0x437940bc);
    FUN_437b4f2c(iVar44 + 0x43794090,auStack_7c,4);
  }
  if ((*(uint *)(DAT_437943f4 + 0x437948d2) & 2) == 0) {
    FUN_43560da8(0x11,2);
    FUN_43ae9148(auStack_90,DAT_437943f8 + 0x437940e6);
    FUN_437c297c(DAT_437943fc + 0x437940f2,auStack_90,2);
  }
  if ((*(uint *)(DAT_43794400 + 0x437948fe) & 0x80) == 0) {
    FUN_43560da8(0x11,0x80);
    FUN_43ae9148(auStack_a4,DAT_43794404 + 0x43794112);
    FUN_437b66e0(DAT_43794408 + 0x4379411e,auStack_a4,0x80);
  }
  if ((*(uint *)(DAT_4379440c + 0x4379492a) & 8) == 0) {
    FUN_43560da8(0x11,8);
    FUN_43ae9148(auStack_b8,DAT_43794410 + 0x4379413e);
    FUN_4379fd58(DAT_43794414 + 0x4379414a,auStack_b8,8);
  }
  if ((*(uint *)(DAT_43794418 + 0x43794956) & 0x40) == 0) {
    FUN_43560da8(0x11,0x40);
    FUN_43ae9148(auStack_cc,DAT_4379441c + 0x4379416a);
    FUN_437d9e00(DAT_43794420 + 0x43794176,auStack_cc,0x40);
  }
  if ((*(uint *)(DAT_43794424 + 0x43794982) & 0x20) == 0) {
    FUN_43560da8(0x11,0x20);
    FUN_43ae9148(auStack_e0,DAT_43794428 + 0x43794196);
    FUN_437d0c90(DAT_4379442c + 0x437941a2,auStack_e0,0x20);
  }
  if ((*(uint *)((int)&DAT_437949ac + DAT_43794430 + 2) & 0x200) == 0) {
    FUN_43560da8(0x11,0x200);
    uVar13 = FUN_4378dd84();
    FUN_43ae9148(auStack_f4,DAT_43794434 + 0x437941c6);
    FUN_437b82d8(DAT_43794438 + 0x437941d6,uVar13,auStack_f4,0x200);
  }
  iVar44 = DAT_43794448;
  bVar56 = (*(byte *)((int)&DAT_437949ec + DAT_4379443c + 2) & 0x40) != 0;
  if (bVar56) {
    iVar46 = *(int *)(*(int *)(DAT_43794444 + 0x43794204) + 0x10);
  }
  else {
    iVar46 = *(int *)(*(int *)(DAT_43794440 + 0x437941f8) + 0x10);
  }
  psVar38 = (short *)(DAT_43794448 + 0x4379420e);
  thunk_FUN_43721e60(!bVar56,iVar46 == 3);
  if (*(int *)(iVar44 + 0x43794822) == 0) {
    if ((*(byte *)(iVar44 + 0x43794a1a) & 0x40) != 0) {
      FUN_43795bf0();
      goto LAB_437944b8;
    }
    FUN_43ae93ce();
    uVar32 = 0;
  }
  else {
    if (uVar1 == 0x103) {
      if (*psVar38 != 0x14a) goto LAB_437944be;
      FUN_43ae93dc();
      FUN_4378f3f8(1);
      uVar32 = 1;
LAB_437944a2:
      *(undefined1 *)((int)&DAT_437949f4 + iVar44 + 2) = uVar32;
      goto LAB_437944be;
    }
    if (uVar1 < 0x104) {
      if (uVar1 < 0x100) goto LAB_437944be;
      if (uVar1 < 0x102) {
        if (1 < (ushort)(*psVar38 - 0x105U)) goto LAB_437944be;
        FUN_43795c14();
        uVar32 = 0;
        goto LAB_437944ba;
      }
    }
    else {
      if (uVar1 == 0x10e) {
        sVar25 = *psVar38;
        if (((((sVar25 == 0x102) || (sVar25 == 0x107)) || (sVar25 == 0x11a)) ||
            ((sVar25 == 0x11b || (sVar25 == 0x118)))) || ((sVar25 == 0x119 || (sVar25 == 0x132)))) {
          FUN_43ae93ea();
          FUN_4378f3f8(0);
          FUN_436d6118();
          FUN_43ad913e();
        }
        goto LAB_437944be;
      }
      if (uVar1 < 0x10f) {
        if (uVar1 != 0x107) goto LAB_437944be;
      }
      else if (uVar1 != 0x132) {
        if ((uVar1 != 0x14a) || (1 < (ushort)(*psVar38 - 0x102U))) goto LAB_437944be;
        FUN_43ae93ea();
        FUN_4378f3f8(0);
        FUN_436d6118();
        FUN_43ad913e();
        uVar32 = 0;
        goto LAB_437944a2;
      }
    }
    if (*(short *)(DAT_437945fc + 0x437944ae) != 0x10e) goto LAB_437944be;
    FUN_43ae93dc();
LAB_437944b8:
    uVar32 = 1;
  }
LAB_437944ba:
  FUN_4378f3f8(uVar32);
LAB_437944be:
  if ((*(char *)(iVar39 + 0x70) == '\0') && (iVar44 = FUN_437999e4(1,0xe), iVar44 != 0)) {
    FUN_43b71948();
  }
  if ((**(uint **)(DAT_43794600 + 0x437944dc) & 0xfffff) == 0) {
    FUN_43728be0();
  }
  FUN_4378f7a0(0xc39);
  if (*(char *)(iVar39 + 0xbf) != '\0') {
    FUN_43ae9124(auStack_108,*(undefined4 *)(iVar43 + DAT_43794604));
    FUN_439018b0(DAT_43794608 + 0x4379450a,auStack_108,2,0);
  }
  iVar43 = DAT_4379460c;
  FUN_43560da8(0x1a,0x40);
  FUN_43ae129a(4);
  if (param_1 != **(int **)(iVar43 + 0x4379451c)) {
    iVar44 = thunk_FUN_436cd00c();
    uVar48 = (uint)(iVar44 - (*(undefined4 **)(iVar43 + 0x4379451c))[2]) >> 1;
    FUN_4378eb78(3,9,1,DAT_43794610 + 0x4379454c,param_1,**(undefined4 **)(iVar43 + 0x4379451c),
                 uVar48);
    FUN_43902718(DAT_43794614 + 0x4379455a,param_1,**(undefined4 **)(iVar43 + 0x4379451c),uVar48);
    FUN_4378f988(4,0,uVar48);
    if ((*(byte *)(iVar39 + 0x12) & 4) != 0) {
      FUN_43561540(DAT_43794618 + 0x43794578);
    }
    if ((*(byte *)(iVar39 + 0x1b) & 2) != 0) {
      FUN_4378ec60();
    }
  }
  if ((*(byte *)(iVar39 + 0x12) & 1) != 0) {
    FUN_43561540(DAT_4379461c + 0x43794598);
  }
  return;
}


/* 438020c0 */

undefined4 dispatch_438020c0(int param_1)

{
  *(uint *)(DAT_438020d0 + 0x4380218a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438020d4 */

undefined4 dispatch_438020d4(int param_1)

{
  bool bVar1;
  int iVar2;
  
  bVar1 = *(char *)(param_1 + 8) != '\0';
  if (bVar1) {
    iVar2 = DAT_438020f0 + 0x438020e6;
  }
  else {
    iVar2 = DAT_438020ec + 0x438020de;
  }
  *(bool *)(iVar2 + 0xdc) = bVar1;
  return 1;
}


/* 438020f4 */

undefined4 dispatch_438020f4(int param_1)

{
  *(uint *)(DAT_43802104 + 0x438021ba) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802108 */

undefined4 dispatch_43802108(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802124;
  dispatch_438023e4[DAT_43802124 + 4] = *(code *)(param_1 + 9);
  *(uint *)(iVar1 + 0x438023ec) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438023f0) = (uint)*(byte *)(param_1 + 10);
  return 1;
}


/* 43802128 */

undefined4 dispatch_43802128(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar4 = DAT_438021d4;
  iVar3 = DAT_438021d0;
  iVar2 = DAT_438021cc;
  cVar1 = *(char *)(param_1 + 8);
  if (cVar1 == '\0') {
    dispatch_438025c8[DAT_438021cc + 6] = (code)0x0;
    *(undefined4 *)(iVar2 + 0x438025d2) = 0;
    dispatch_4380231c[iVar2 + 6] = (code)0x0;
    dispatch_438023fc[iVar2 + 6] = (code)0x0;
    dispatch_43802500[iVar2 + 4] = (code)0x0;
    *(undefined1 *)(iVar2 + 0x438025d0) = 0;
    dispatch_43802458[iVar2 + 2] = (code)0x0;
  }
  else if (cVar1 == '\x05') {
    dispatch_438025f4[DAT_438021d0 + 2] = (code)0x0;
    *(undefined4 *)(iVar3 + 0x438025fa) = 0;
    dispatch_43802344[iVar3 + 6] = (code)0x0;
    (&UNK_4380242a)[iVar3] = 0;
    dispatch_43802528[iVar3 + 4] = (code)0x0;
    *(undefined1 *)(iVar3 + 0x438025f8) = 1;
    dispatch_43802480[iVar3 + 2] = (code)0x1;
  }
  else {
    *(undefined1 *)((int)&DAT_4380261c + DAT_438021d4) = 1;
    *(undefined1 *)((int)&DAT_43802370 + iVar4) = 1;
    *(undefined1 *)(iVar4 + 0x43802450) = 1;
    *(undefined1 *)(iVar4 + 0x43802552) = 1;
    *(undefined1 *)((int)&DAT_4380261c + iVar4 + 2) = 0;
    *(undefined1 *)(iVar4 + 0x438024a8) = 0;
    if (cVar1 == '\x01') {
      *(undefined4 *)(dispatch_43802620 + iVar4) = 0;
    }
    else {
      if (cVar1 == '\x02') {
        uVar5 = 2;
      }
      else {
        uVar5 = 1;
      }
      *(undefined4 *)(dispatch_43802620 + iVar4) = uVar5;
    }
  }
  iVar2 = DAT_438021d8;
  *(undefined1 *)(DAT_438021d8 + 0x43802666) = *(undefined1 *)(param_1 + 9);
  *(bool *)(iVar2 + 0x43802667) = *(char *)(param_1 + 10) == '\x01';
  return 1;
}


/* 438021dc */

undefined4 dispatch_438021dc(int param_1)

{
  int iVar1;
  bool bVar2;
  
  bVar2 = *(char *)(param_1 + 8) != '\x01';
  if (bVar2) {
    iVar1 = DAT_438021fc + 0x438021f0;
  }
  else {
    iVar1 = DAT_438021f8 + 0x438021e8;
  }
  *(bool *)(iVar1 + 0x4a4) = !bVar2;
  return 1;
}


/* 43802200 */

undefined4 dispatch_43802200(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802228;
  *(uint *)(DAT_43802228 + 0x438025d0) = (uint)*(byte *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x438025d4) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x438025d5) = *(undefined1 *)(param_1 + 10);
  *(undefined1 *)((int)&DAT_438025d8 + iVar1) = *(undefined1 *)(param_1 + 0xb);
  *(undefined1 *)((int)&DAT_438025d8 + iVar1 + 1) = *(undefined1 *)(param_1 + 0xc);
  return 1;
}


/* 4380222c */

undefined4 dispatch_4380222c(int param_1)

{
  *(uint *)(dispatch_43802620 + DAT_4380223c + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802240 */

undefined4 dispatch_43802240(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802254;
  *(undefined1 *)(DAT_43802254 + 0x43802616) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x43802617) = *(undefined1 *)(param_1 + 9);
  return 1;
}


/* 43802258 */

undefined4 dispatch_43802258(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802280;
  *(uint *)(DAT_43802280 + 0x438022b8) = (uint)*(byte *)(param_1 + 8);
  *(uint *)((int)&DAT_438022bc + iVar1) = (uint)*(byte *)(param_1 + 9);
  *(undefined4 *)(iVar1 + 0x438022b4) = *(undefined4 *)(param_1 + 10);
  return 1;
}


/* 43802284 */

undefined4 dispatch_43802284(int param_1)

{
  *(uint *)(dispatch_438026f0 + DAT_43802294 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802298 */

undefined4 dispatch_43802298(int param_1)

{
  *(uint *)(DAT_438022a8 + 0x4380270e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438022ac */

undefined4 dispatch_438022ac(int param_1)

{
  *(uint *)(&LAB_43802726 + DAT_438022bc) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438022c0 */

undefined4 dispatch_438022c0(int param_1)

{
  *(uint *)(DAT_438022d0 + 0x4380273e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438022d4 */

undefined4 dispatch_438022d4(int param_1)

{
  *(uint *)(DAT_438022e4 + 0x43802756) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438022e8 */

undefined4 dispatch_438022e8(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802304;
  *(uint *)(DAT_43802304 + 0x43802738) = (uint)*(byte *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x4380273c) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x4380273d) = *(undefined1 *)(param_1 + 10);
  return 1;
}


/* 43802308 */

undefined4 dispatch_43802308(int param_1)

{
  *(uint *)((int)&DAT_43802490 + DAT_43802318 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 4380231c */

undefined4 dispatch_4380231c(int param_1)

{
  *(uint *)(DAT_4380232c + 0x438024aa) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802330 */

undefined4 dispatch_43802330(int param_1)

{
  *(uint *)(DAT_43802340 + 0x43802862) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802344 */

undefined4 dispatch_43802344(int param_1)

{
  *(uint *)(dispatch_43802844 + DAT_43802354 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802358 */

undefined4 dispatch_43802358(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802370;
  *(uint *)(dispatch_438025c8 + DAT_43802370 + 2) = (uint)*(byte *)(param_1 + 8);
  *(char *)(iVar1 + 0x438025ce) = *(char *)(iVar1 + 0x438025ce) + '\x01';
  return 1;
}


/* 43802374 */

undefined4 dispatch_43802374(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802398;
  *(undefined1 *)((int)&DAT_43802510 + DAT_43802398 + 2) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x43802515) = *(undefined1 *)(param_1 + 9);
  *(char *)((int)&DAT_43802510 + iVar1 + 3) = *(char *)((int)&DAT_43802510 + iVar1 + 3) + '\x01';
  dispatch_43802514[iVar1] = (code)0x0;
  return 1;
}


/* 4380239c */

void dispatch_4380239c(void)

{
  dispatch_4380253c[DAT_438023a8] = (code)0x1;
  return;
}


/* 438023ac */

undefined4 dispatch_438023ac(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438023c4;
  *(undefined1 *)(DAT_438023c4 + 0x4380256d) = *(undefined1 *)(param_1 + 8);
  *(char *)(iVar1 + 0x4380256e) = *(char *)(iVar1 + 0x4380256e) + '\x01';
  return 1;
}


/* 438023c8 */

undefined4 dispatch_438023c8(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438023e0;
  *(undefined1 *)(DAT_438023e0 + 0x4380255a) = *(undefined1 *)(param_1 + 8);
  *(char *)(iVar1 + 0x4380255b) = *(char *)(iVar1 + 0x4380255b) + '\x01';
  return 1;
}


/* 438023e4 */

undefined4 dispatch_438023e4(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438023f8;
  *(undefined1 *)(DAT_438023f8 + 0x43802660) = *(undefined1 *)(param_1 + 8);
  *(uint *)(iVar1 + 0x43802664) = (uint)*(byte *)(param_1 + 9);
  return 1;
}


/* 438023fc */

undefined4 dispatch_438023fc(int param_1)

{
  *(uint *)(&UNK_43802676 + DAT_4380240c) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802410 */

undefined4 dispatch_43802410(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_4380242c;
  *(undefined1 *)(DAT_4380242c + 0x438025b3) = *(undefined1 *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438025b4) = (uint)*(byte *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x438025b2) = *(undefined1 *)(param_1 + 10);
  return 1;
}


/* 43802430 */

undefined4 dispatch_43802430(int param_1)

{
  *(uint *)((int)&DAT_438025d8 + DAT_43802440 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802444 */

undefined4 dispatch_43802444(int param_1)

{
  *(undefined1 *)(DAT_43802454 + 0x4380263f) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802458 */

undefined4 dispatch_43802458(int param_1)

{
  *(undefined1 *)(DAT_43802468 + 0x43802654) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 4380246c */

undefined4 dispatch_4380246c(int param_1)

{
  *(undefined1 *)(DAT_4380247c + 0x43802669) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802480 */

undefined4 dispatch_43802480(int param_1)

{
  dispatch_4380267c[DAT_43802490 + 2] = *(code *)(param_1 + 8);
  return 1;
}


/* 43802494 */

undefined4 dispatch_43802494(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438024d8;
  *(undefined2 *)(DAT_438024d8 + 0x4380262a) = *(undefined2 *)(param_1 + 8);
  *(undefined2 *)(iVar1 + 0x4380262c) = *(undefined2 *)(param_1 + 10);
  *(char *)((int)&DAT_43802630 + iVar1 + 2) = *(char *)((int)&DAT_43802630 + iVar1 + 2) + '\x01';
  *(undefined4 *)(&UNK_4380262e + iVar1) = *(undefined4 *)(param_1 + 4);
  return 1;
}


/* 438024dc */

undefined4 dispatch_438024dc(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438024fc;
  *(undefined1 *)(DAT_438024fc + 0x438026b8) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x438026b9) = *(undefined1 *)(param_1 + 9);
  *(char *)(iVar1 + 0x438026ba) = *(char *)(iVar1 + 0x438026ba) + '\x01';
  return 1;
}


/* 43802500 */

undefined4 dispatch_43802500(int param_1)

{
  *(undefined1 *)(DAT_43802510 + 0x438026b6) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802514 */

undefined4 dispatch_43802514(int param_1)

{
  *(undefined1 *)(DAT_43802524 + 0x438026d4) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802528 */

undefined4 dispatch_43802528(int param_1)

{
  *(undefined1 *)(DAT_43802538 + 0x438026d6) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 4380253c */

undefined4 dispatch_4380253c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_4380258c;
  *(undefined4 *)(DAT_4380258c + 0x43802828) = 3;
  *(undefined4 *)(dispatch_438027a4 + iVar1) = *(undefined4 *)(param_1 + 4);
  *(undefined2 *)((int)&DAT_4380282c + iVar1) = *(undefined2 *)(param_1 + 8);
  *(undefined2 *)((int)&DAT_4380282c + iVar1 + 2) = *(undefined2 *)(param_1 + 10);
  *(char *)((int)&DAT_438026d8 + iVar1 + 1) = *(char *)((int)&DAT_438026d8 + iVar1 + 1) + '\x01';
  *(undefined4 *)(dispatch_43802808 + iVar1) = 0;
  return 1;
}


/* 43802590 */

undefined4 dispatch_43802590(int param_1)

{
  *(uint *)(DAT_438025a0 + 0x43802a6e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438025a4 */

undefined4 dispatch_438025a4(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438025c4;
  *(uint *)(DAT_438025c4 + 0x43802618) = (uint)*(byte *)(param_1 + 8);
  *(uint *)((int)&DAT_4380261c + iVar1) = (uint)*(byte *)(param_1 + 9);
  dispatch_43802620[iVar1] = *(code *)(param_1 + 10);
  *(uint *)(iVar1 + 0x43802624) = (uint)*(byte *)(param_1 + 0xb);
  *(uint *)(iVar1 + 0x43802628) = (uint)*(byte *)(param_1 + 0xc);
  return 1;
}


/* 438025c8 */

undefined4 dispatch_438025c8(int param_1)

{
  *(uint *)(dispatch_4380264c + DAT_438025d8 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438025dc */

undefined4 dispatch_438025dc(int param_1)

{
  *(bool *)(DAT_438025f0 + 0x43802860) = *(char *)(param_1 + 8) != '\0';
  return 1;
}


/* 438025f4 */

undefined4 dispatch_438025f4(int param_1)

{
  *(bool *)(DAT_43802608 + 0x43802879) = *(char *)(param_1 + 8) != '\0';
  return 1;
}


/* 4380260c */

undefined4 dispatch_4380260c(int param_1)

{
  *(uint *)(dispatch_43802894 + DAT_4380261c + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802620 */

undefined4 dispatch_43802620(int param_1)

{
  *(uint *)(dispatch_438028a8 + DAT_43802630 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802634 */

undefined4 dispatch_43802634(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802648;
  *(uint *)(DAT_43802648 + 0x438028c4) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438028c8) = (uint)*(byte *)(param_1 + 9);
  return 1;
}


/* 4380264c */

undefined4 dispatch_4380264c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802678;
  *(undefined1 *)(DAT_43802678 + 0x43802801) = *(undefined1 *)(param_1 + 8);
  (&UNK_43802802)[iVar1] = (&UNK_43802802)[iVar1] + '\x01';
  *(uint *)((int)&DAT_43802804 + iVar1) = (uint)*(byte *)(param_1 + 9);
  *(undefined2 *)(dispatch_43802808 + iVar1) = *(undefined2 *)(param_1 + 10);
  return 1;
}


/* 4380267c */

undefined4 dispatch_4380267c(int param_1)

{
  *(uint *)((int)&DAT_4380282c + DAT_4380268c + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802690 */

undefined4 dispatch_43802690(int param_1)

{
  int iVar1;
  char cVar2;
  
  iVar1 = DAT_438026c0;
  *(undefined1 *)(DAT_438026c0 + 0x43802984) = *(undefined1 *)(param_1 + 8);
  *(undefined4 *)(iVar1 + 0x43802990) = 1;
  if (*(char *)(param_1 + 9) == '\x01') {
    cVar2 = *(char *)(iVar1 + 0x43802985) + -1;
  }
  else {
    if (*(char *)(param_1 + 9) != '\x02') {
      return 1;
    }
    cVar2 = *(char *)(iVar1 + 0x43802985) + '\x01';
  }
  *(char *)(iVar1 + 0x43802985) = cVar2;
  return 1;
}


/* 438026c4 */

undefined4 dispatch_438026c4(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438026d8;
  *(uint *)((int)&DAT_438029c0 + DAT_438026d8 + 2) = (uint)*(byte *)(param_1 + 8);
  *(undefined4 *)(dispatch_438029c4 + iVar1 + 2) = 0;
  return 1;
}


/* 438026dc */

undefined4 dispatch_438026dc(int param_1)

{
  *(uint *)(&UNK_438029e6 + DAT_438026ec) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438026f0 */

undefined4 dispatch_438026f0(int param_1)

{
  *(uint *)(&UNK_43802a0e + DAT_43802700) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 4380278c */

undefined4 dispatch_4380278c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438027a0;
  *(uint *)((int)&DAT_43802868 + DAT_438027a0) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(dispatch_4380286c + iVar1) = (uint)*(byte *)(param_1 + 9);
  return 1;
}


/* 438027a4 */

undefined4 dispatch_438027a4(int param_1)

{
  *(uint *)((int)&DAT_43802998 + DAT_438027b4 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438027b8 */

undefined4 dispatch_438027b8(int param_1)

{
  *(uint *)(dispatch_43802b9c + DAT_438027c8 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438027cc */

undefined4 dispatch_438027cc(int param_1)

{
  *(uint *)(DAT_438027dc + 0x43802bba) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438027e0 */

undefined4 dispatch_438027e0(int param_1)

{
  *(uint *)(&UNK_43802bbe + DAT_438027f0) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438027f4 */

undefined4 dispatch_438027f4(int param_1)

{
  *(undefined1 *)((int)&DAT_43802bd4 + DAT_43802804 + 2) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802808 */

undefined4 dispatch_43802808(int param_1)

{
  *(undefined1 *)(DAT_43802818 + 0x43802beb) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 4380281c */

undefined4 dispatch_4380281c(int param_1)

{
  *(undefined1 *)(DAT_4380282c + 0x43802c00) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802830 */

undefined4 dispatch_43802830(int param_1)

{
  *(undefined1 *)(DAT_43802840 + 0x43802c15) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802844 */

undefined4 dispatch_43802844(int param_1)

{
  (&UNK_43802c2a)[DAT_43802854] = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802858 */

undefined4 dispatch_43802858(int param_1)

{
  *(uint *)(dispatch_438028e4 + DAT_43802868 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 4380286c */

undefined4 dispatch_4380286c(int param_1)

{
  *(uint *)(DAT_4380287c + 0x43802b42) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802880 */

undefined4 dispatch_43802880(int param_1)

{
  *(uint *)(dispatch_43802db4 + DAT_43802890 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802894 */

undefined4 dispatch_43802894(int param_1)

{
  *(uint *)(DAT_438028a4 + 0x43802bba) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438028a8 */

undefined4 dispatch_438028a8(int param_1)

{
  *(uint *)(&UNK_43802bd2 + DAT_438028b8) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438028e4 */

undefined4 dispatch_438028e4(int param_1)

{
  *(uint *)(DAT_438028f4 + 0x43802e1e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438028f8 */

undefined4 dispatch_438028f8(int param_1)

{
  *(undefined1 *)(DAT_43802908 + 0x43802de2) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 4380290c */

undefined4 dispatch_4380290c(int param_1)

{
  *(uint *)(DAT_4380291c + 0x43802c3a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802920 */

undefined4 dispatch_43802920(int param_1)

{
  *(uint *)(&LAB_43802e0e + DAT_43802930) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802934 */

undefined4 dispatch_43802934(int param_1)

{
  *(uint *)(dispatch_43802e38 + DAT_43802944 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802948 */

undefined4 dispatch_43802948(int param_1)

{
  *(uint *)(DAT_43802958 + 0x43802e56) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 4380299c */

undefined4 dispatch_4380299c(int param_1)

{
  *(uint *)(DAT_438029ac + 0x43802d8e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438029b0 */

undefined4 dispatch_438029b0(int param_1)

{
  *(uint *)(dispatch_43802bb0 + DAT_438029c0 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438029c4 */

undefined4 dispatch_438029c4(int param_1)

{
  *(uint *)(DAT_438029d4 + 0x43802ee2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438029d8 */

undefined4 dispatch_438029d8(int param_1)

{
  *(uint *)((int)&DAT_43802efc + DAT_438029e8 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438029ec */

undefined4 dispatch_438029ec(int param_1)

{
  *(uint *)(&UNK_43802f0e + DAT_438029fc) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802a00 */

undefined4 dispatch_43802a00(int param_1)

{
  *(uint *)(dispatch_43802f28 + DAT_43802a10 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802a14 */

undefined4 dispatch_43802a14(int param_1)

{
  *(uint *)(dispatch_43802f3c + DAT_43802a24 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802a28 */

undefined4 dispatch_43802a28(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802b70;
  *(uint *)(DAT_43802b70 + 0x43802b68) = (uint)*(byte *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x43802b6c) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x43802b6d) = *(undefined1 *)(param_1 + 10);
  *(undefined1 *)(iVar1 + 0x43802b6e) = *(undefined1 *)(param_1 + 0xb);
  *(undefined1 *)(iVar1 + 0x43802b6f) = *(undefined1 *)(param_1 + 0xc);
  *(undefined1 *)((int)&DAT_43802b70 + iVar1) = *(undefined1 *)(param_1 + 0xd);
  *(uint *)(dispatch_43802b74 + iVar1) = (uint)*(byte *)(param_1 + 0xe);
  *(undefined1 *)(iVar1 + 0x43802b78) = *(undefined1 *)(param_1 + 0xf);
  *(undefined1 *)(iVar1 + 0x43802b79) = *(undefined1 *)(param_1 + 0x10);
  *(undefined1 *)(iVar1 + 0x43802b7a) = *(undefined1 *)(param_1 + 0x11);
  *(undefined1 *)(iVar1 + 0x43802b7b) = *(undefined1 *)(param_1 + 0x12);
  *(undefined1 *)(iVar1 + 0x43802b7c) = *(undefined1 *)(param_1 + 0x13);
  *(undefined1 *)(iVar1 + 0x43802b7d) = *(undefined1 *)(param_1 + 0x14);
  *(undefined1 *)(iVar1 + 0x43802b7e) = *(undefined1 *)(param_1 + 0x15);
  *(undefined1 *)(iVar1 + 0x43802b7f) = *(undefined1 *)(param_1 + 0x16);
  *(undefined1 *)(iVar1 + 0x43802b80) = *(undefined1 *)(param_1 + 0x17);
  *(undefined1 *)(iVar1 + 0x43802b81) = *(undefined1 *)(param_1 + 0x18);
  (&UNK_43802b82)[iVar1] = *(undefined1 *)(param_1 + 0x19);
  (&UNK_43802b83)[iVar1] = *(undefined1 *)(param_1 + 0x1a);
  *(undefined1 *)((int)&DAT_43802b84 + iVar1) = *(undefined1 *)(param_1 + 0x1b);
  *(undefined1 *)((int)&DAT_43802b84 + iVar1 + 1) = *(undefined1 *)(param_1 + 0x1c);
  *(undefined1 *)((int)&DAT_43802b84 + iVar1 + 2) = *(undefined1 *)(param_1 + 0x1d);
  *(undefined1 *)((int)&DAT_43802b84 + iVar1 + 3) = *(undefined1 *)(param_1 + 0x1e);
  dispatch_43802b88[iVar1] = *(code *)(param_1 + 0x1f);
  *(undefined1 *)(iVar1 + 0x43802b89) = *(undefined1 *)(param_1 + 0x20);
  *(undefined1 *)(iVar1 + 0x43802b8a) = *(undefined1 *)(param_1 + 0x21);
  *(undefined1 *)(iVar1 + 0x43802b8b) = *(undefined1 *)(param_1 + 0x22);
  *(undefined1 *)(iVar1 + 0x43802b8c) = *(undefined1 *)(param_1 + 0x23);
  *(undefined1 *)(iVar1 + 0x43802b8d) = *(undefined1 *)(param_1 + 0x24);
  *(undefined1 *)(iVar1 + 0x43802b8e) = *(undefined1 *)(param_1 + 0x25);
  *(undefined1 *)(iVar1 + 0x43802b8f) = *(undefined1 *)(param_1 + 0x26);
  *(uint *)(iVar1 + 0x43802b90) = (uint)*(byte *)(param_1 + 0x27);
  *(uint *)(iVar1 + 0x43802b94) = (uint)*(byte *)(param_1 + 0x28);
  *(undefined2 *)((int)&DAT_43802b98 + iVar1) = *(undefined2 *)(param_1 + 0x29);
  *(undefined1 *)((int)&DAT_43802b98 + iVar1 + 2) = *(undefined1 *)(param_1 + 0x2b);
  *(undefined1 *)((int)&DAT_43802b98 + iVar1 + 3) = *(undefined1 *)(param_1 + 0x2c);
  dispatch_43802b9c[iVar1] = *(code *)(param_1 + 0x2d);
  *(undefined1 *)(iVar1 + 0x43802b9d) = *(undefined1 *)(param_1 + 0x2e);
  *(undefined2 *)(iVar1 + 0x43802b9e) = *(undefined2 *)(param_1 + 0x2f);
  *(undefined1 *)(iVar1 + 0x43802ba0) = *(undefined1 *)(param_1 + 0x31);
  *(undefined1 *)(iVar1 + 0x43802ba1) = *(undefined1 *)(param_1 + 0x32);
  *(undefined1 *)(iVar1 + 0x43802ba2) = *(undefined1 *)(param_1 + 0x33);
  *(undefined1 *)(iVar1 + 0x43802ba3) = *(undefined1 *)(param_1 + 0x34);
  *(uint *)(iVar1 + 0x43802b64) = (uint)*(byte *)(param_1 + 0x35);
  return 1;
}


/* 43802b74 */

undefined4 dispatch_43802b74(int param_1)

{
  *(uint *)(&UNK_43802eaa + DAT_43802b84) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802b88 */

undefined4 dispatch_43802b88(int param_1)

{
  *(uint *)(DAT_43802b98 + 0x43802d8e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802b9c */

undefined4 dispatch_43802b9c(int param_1)

{
  *(uint *)((int)&DAT_43802ed4 + DAT_43802bac + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802bb0 */

undefined4 dispatch_43802bb0(int param_1)

{
  *(uint *)(DAT_43802bc0 + 0x43802dda) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802bc4 */

undefined4 dispatch_43802bc4(int param_1)

{
  *(uint *)((int)&DAT_43802df0 + DAT_43802bd4 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802bd8 */

undefined4 dispatch_43802bd8(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802bf0;
  *(undefined1 *)(DAT_43802bf0 + 0x43802de2) = *(undefined1 *)(param_1 + 8);
  *(char *)(iVar1 + 0x43802de3) = *(char *)(iVar1 + 0x43802de3) + '\x01';
  return 1;
}


/* 43802bf4 */

undefined4 dispatch_43802bf4(int param_1)

{
  *(uint *)((int)&DAT_43802e98 + DAT_43802c04 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802c08 */

undefined4 dispatch_43802c08(int param_1)

{
  *(uint *)(DAT_43802c18 + 0x43802f46) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802c1c */

undefined4 dispatch_43802c1c(int param_1)

{
  *(uint *)(dispatch_43802cac + DAT_43802c2c + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802c30 */

undefined4 dispatch_43802c30(int param_1)

{
  *(uint *)(dispatch_43802cc0 + DAT_43802c40 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802c78 */

undefined4 dispatch_43802c78(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802c94;
  *(uint *)(DAT_43802c94 + 0x43802fbc) = (uint)*(byte *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x43802fc0) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x43802fc1) = *(undefined1 *)(param_1 + 10);
  return 1;
}


/* 43802c98 */

undefined4 dispatch_43802c98(int param_1)

{
  *(uint *)(DAT_43802ca8 + 0x43802ea6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802cac */

undefined4 dispatch_43802cac(int param_1)

{
  *(uint *)((int)&DAT_43803000 + DAT_43802cbc + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802cc0 */

undefined4 dispatch_43802cc0(int param_1)

{
  *(uint *)(DAT_43802cd0 + 0x43802d5a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802cd4 */

undefined4 dispatch_43802cd4(int param_1)

{
  *(uint *)(dispatch_43802f78 + DAT_43802ce4 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802ce8 */

undefined4 dispatch_43802ce8(int param_1)

{
  *(uint *)(DAT_43802cf8 + 0x43803036) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802cfc */

undefined4 dispatch_43802cfc(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802d10;
  *(undefined1 *)(DAT_43802d10 + 0x43802f0c) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x43802f0d) = *(undefined1 *)(param_1 + 9);
  return 1;
}


/* 43802d98 */

undefined4 dispatch_43802d98(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802db0;
  dispatch_43803224[DAT_43802db0 + 1] = *(code *)(param_1 + 8);
  *(char *)(iVar1 + 0x43803226) = *(char *)(iVar1 + 0x43803226) + '\x01';
  return 1;
}


/* 43802db4 */

undefined4 dispatch_43802db4(int param_1)

{
  *(uint *)(DAT_43802dc4 + 0x43803246) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e14 */

void dispatch_43802e14(void)

{
  *(undefined1 *)(DAT_43802e20 + 0x43803026) = 1;
  return;
}


/* 43802e24 */

undefined4 dispatch_43802e24(int param_1)

{
  *(uint *)((int)&DAT_43803364 + DAT_43802e34 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e38 */

undefined4 dispatch_43802e38(int param_1)

{
  *(uint *)(DAT_43802e48 + 0x4380304e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e4c */

undefined4 candidate_43802e4c(int param_1)

{
  *(uint *)(DAT_43802e5c + 0x43803066) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e60 */

undefined4 dispatch_43802e60(int param_1)

{
  *(uint *)(dispatch_43803284 + DAT_43802e70 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e74 */

undefined4 dispatch_43802e74(int param_1)

{
  *(uint *)((int)&DAT_4380330c + DAT_43802e84 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e88 */

undefined4 dispatch_43802e88(int param_1)

{
  *(uint *)(&UNK_4380314e + DAT_43802e98) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802e9c */

undefined4 dispatch_43802e9c(int param_1)

{
  *(uint *)(dispatch_438032fc + DAT_43802eac + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802eb0 */

undefined4 dispatch_43802eb0(int param_1)

{
  *(uint *)(DAT_43802ec0 + 0x4380331a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802ec4 */

undefined4 dispatch_43802ec4(int param_1)

{
  *(uint *)(DAT_43802ed4 + 0x43803332) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802ed8 */

undefined4 dispatch_43802ed8(int param_1)

{
  *(undefined1 *)(DAT_43802ee8 + 0x438030d7) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802eec */

undefined4 dispatch_43802eec(int param_1)

{
  *(undefined1 *)(DAT_43802efc + 0x4380310a) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43802f00 */

undefined4 dispatch_43802f00(int param_1)

{
  *(uint *)(&UNK_43802faa + DAT_43802f10) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f14 */

undefined4 dispatch_43802f14(int param_1)

{
  *(uint *)(DAT_43802f24 + 0x43802fce) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f28 */

undefined4 dispatch_43802f28(int param_1)

{
  *(uint *)(DAT_43802f38 + 0x4380305a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f3c */

undefined4 dispatch_43802f3c(int param_1)

{
  *(uint *)(DAT_43802f4c + 0x43803072) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f50 */

undefined4 dispatch_43802f50(int param_1)

{
  *(uint *)(dispatch_43803494 + DAT_43802f60 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f64 */

undefined4 dispatch_43802f64(int param_1)

{
  *(uint *)(dispatch_43803464 + DAT_43802f74 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802f78 */

undefined4 dispatch_43802f78(int param_1)

{
  int iVar1;
  bool bVar2;
  
  bVar2 = *(char *)(param_1 + 8) != '\x01';
  if (bVar2) {
    iVar1 = DAT_43802f98 + 0x43802f8c;
  }
  else {
    iVar1 = DAT_43802f94 + 0x43802f84;
  }
  *(bool *)(iVar1 + 0x4be) = !bVar2;
  return 1;
}


/* 43802f9c */

undefined4 dispatch_43802f9c(int param_1)

{
  *(uint *)(DAT_43802fac + 0x438034ae) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43802fb0 */

undefined4 dispatch_43802fb0(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43802fdc;
  *(undefined4 *)(dispatch_43803450 + DAT_43802fdc + 4) = *(undefined4 *)(param_1 + 8);
  *(char *)(iVar1 + 0x43803458) = *(char *)(iVar1 + 0x43803458) + '\x01';
  return 1;
}


/* 43803004 */

undefined4 dispatch_43803004(int param_1)

{
  *(uint *)(dispatch_43803224 + DAT_43803014 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803018 */

undefined4 dispatch_43803018(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803040;
  *(undefined4 *)(DAT_43803040 + 0x4380338c) = *(undefined4 *)(param_1 + 4);
  *(uint *)(iVar1 + 0x43803390) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803044 */

undefined4 dispatch_43803044(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803084;
  *(undefined4 *)(dispatch_438033d0 + DAT_43803084) = *(undefined4 *)(param_1 + 4);
  *(uint *)(iVar1 + 0x438033d4) = (uint)*(byte *)(param_1 + 8);
  *(undefined4 *)(iVar1 + 0x438033d8) = *(undefined4 *)(param_1 + 9);
  return 1;
}


/* 43803088 */

undefined4 dispatch_43803088(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438030c8;
  *(undefined4 *)(DAT_438030c8 + 0x4380340c) = *(undefined4 *)(param_1 + 4);
  *(uint *)(iVar1 + 0x43803410) = (uint)*(byte *)(param_1 + 8);
  *(undefined4 *)(iVar1 + 0x4380341c) = *(undefined4 *)(param_1 + 9);
  return 1;
}


/* 438030cc */

undefined4 dispatch_438030cc(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803128;
  *(uint *)(DAT_43803128 + 0x438034f8) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438034fc) = (uint)*(byte *)(param_1 + 9);
  *(undefined2 *)((int)&DAT_43803500 + iVar1) = *(undefined2 *)(param_1 + 10);
  *(undefined1 *)((int)&DAT_43803500 + iVar1 + 2) = *(undefined1 *)(param_1 + 0xc);
  *(undefined1 *)((int)&DAT_43803500 + iVar1 + 3) = *(undefined1 *)(param_1 + 0xd);
  dispatch_43803504[iVar1] = *(code *)(param_1 + 0xe);
  *(undefined1 *)(iVar1 + 0x43803505) = *(undefined1 *)(param_1 + 0xf);
  *(undefined2 *)(iVar1 + 0x43803506) = *(undefined2 *)(param_1 + 0x10);
  *(undefined1 *)(iVar1 + 0x43803508) = *(undefined1 *)(param_1 + 0x12);
  *(undefined1 *)(iVar1 + 0x43803509) = *(undefined1 *)(param_1 + 0x13);
  *(undefined1 *)(iVar1 + 0x4380350a) = *(undefined1 *)(param_1 + 0x14);
  *(undefined1 *)(iVar1 + 0x4380350b) = *(undefined1 *)(param_1 + 0x15);
  return 1;
}


/* 4380312c */

undefined4 dispatch_4380312c(int param_1)

{
  *(uint *)(DAT_4380313c + 0x438034be) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803140 */

undefined4 dispatch_43803140(int param_1)

{
  *(uint *)((int)&DAT_438034ec + DAT_43803150 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803154 */

undefined4 dispatch_43803154(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803194;
  *(uint *)(dispatch_43803504 + DAT_43803194) = (uint)*(byte *)(param_1 + 8);
  *(undefined4 *)(iVar1 + 0x43803508) = *(undefined4 *)(param_1 + 9);
  *(undefined4 *)(iVar1 + 0x4380350c) = *(undefined4 *)(param_1 + 0xd);
  return 1;
}


/* 43803198 */

undefined4 dispatch_43803198(void)

{
  *(char *)(DAT_438031ac + 0x4380363a) = *(char *)(DAT_438031ac + 0x4380363a) + '\x01';
  return 1;
}


/* 438031b0 */

undefined4 dispatch_438031b0(int param_1)

{
  *(undefined4 *)(DAT_438031d0 + 0x438033dc) = *(undefined4 *)(param_1 + 8);
  return 1;
}


/* 438031d4 */

undefined4 dispatch_438031d4(int param_1)

{
  *(uint *)((int)&DAT_4380330c + DAT_438031e4 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438031e8 */

undefined4 dispatch_438031e8(int param_1)

{
  *(uint *)(FUN_4380357c + DAT_438031f8 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438031fc */

undefined4 dispatch_438031fc(int param_1)

{
  *(uint *)(DAT_4380320c + 0x4380359a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803210 */

undefined4 dispatch_43803210(int param_1)

{
  *(uint *)(DAT_43803220 + 0x438035b2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803224 */

undefined4 dispatch_43803224(int param_1)

{
  *(uint *)(DAT_43803234 + 0x438035ca) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803238 */

undefined4 dispatch_43803238(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803258;
  *(undefined1 *)(DAT_43803258 + 0x438035e0) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(iVar1 + 0x438035e1) = *(undefined1 *)(param_1 + 9);
  *(char *)(iVar1 + 0x438035e2) = *(char *)(iVar1 + 0x438035e2) + '\x01';
  return 1;
}


/* 4380325c */

undefined4 dispatch_4380325c(int param_1)

{
  *(uint *)(DAT_4380326c + 0x438036e2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803270 */

undefined4 dispatch_43803270(int param_1)

{
  *(uint *)((int)&DAT_43803538 + DAT_43803280 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803284 */

undefined4 dispatch_43803284(int param_1)

{
  *(uint *)((int)&DAT_43803320 + DAT_43803294 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803298 */

undefined4 dispatch_43803298(int param_1)

{
  *(uint *)((int)&DAT_43803338 + DAT_438032a8 + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438032ac */

undefined4 dispatch_438032ac(int param_1)

{
  *(uint *)(dispatch_43803350 + DAT_438032bc + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438032c0 */

undefined4 dispatch_438032c0(int param_1)

{
  *(uint *)(&UNK_438034fe + DAT_438032d0) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438032d4 */

undefined4 candidate_438032d4(int param_1)

{
  *(uint *)(DAT_438032e4 + 0x43803516) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438032e8 */

undefined4 dispatch_438032e8(int param_1)

{
  *(uint *)(DAT_438032f8 + 0x4380364e) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438032fc */

undefined4 dispatch_438032fc(int param_1)

{
  *(uint *)(DAT_4380330c + 0x43803696) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803310 */

undefined4 dispatch_43803310(int param_1)

{
  *(uint *)(dispatch_43803674 + DAT_43803320 + 6) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803324 */

undefined4 dispatch_43803324(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803338;
  *(uint *)(DAT_43803338 + 0x438036e2) = (uint)*(byte *)(param_1 + 8);
  *(undefined4 *)(iVar1 + 0x438036e6) = 0;
  return 1;
}


/* 4380333c */

undefined4 dispatch_4380333c(int param_1)

{
  *(uint *)((int)&DAT_43803704 + DAT_4380334c + 2) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803350 */

undefined4 dispatch_43803350(int param_1)

{
  *(bool *)((int)&DAT_43803654 + DAT_43803364) = *(char *)(param_1 + 8) != '\0';
  return 1;
}


/* 43803368 */

undefined4 dispatch_43803368(int param_1)

{
  *(uint *)(DAT_43803378 + 0x43803736) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 4380337c */

undefined4 dispatch_4380337c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_4380339c;
  *(undefined2 *)(DAT_4380339c + 0x438035ae) = *(undefined2 *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438035b2) = (uint)*(byte *)(param_1 + 10);
  *(uint *)(iVar1 + 0x438035b6) = (uint)*(byte *)(param_1 + 0xb);
  return 1;
}


/* 438033a0 */

undefined4 dispatch_438033a0(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438033cc;
  *(undefined1 *)((int)&DAT_43803798 + DAT_438033cc) = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)((int)&DAT_43803798 + iVar1 + 1) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)((int)&DAT_43803798 + iVar1 + 2) = *(undefined1 *)(param_1 + 10);
  *(undefined1 *)((int)&DAT_43803798 + iVar1 + 3) = *(undefined1 *)(param_1 + 0xb);
  dispatch_4380379c[iVar1] = *(code *)(param_1 + 0xc);
  *(undefined1 *)(iVar1 + 0x4380379d) = *(undefined1 *)(param_1 + 0xd);
  return 1;
}


/* 438033d0 */

undefined4 dispatch_438033d0(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_4380344c;
  *(undefined2 *)(dispatch_438037d0 + DAT_4380344c) = *(undefined2 *)(param_1 + 8);
  *(undefined2 *)(iVar1 + 0x438037d2) = *(undefined2 *)(param_1 + 10);
  *(undefined2 *)(iVar1 + 0x438037d4) = *(undefined2 *)(param_1 + 0xc);
  *(undefined2 *)(iVar1 + 0x438037d6) = *(undefined2 *)(param_1 + 0xe);
  *(undefined2 *)(iVar1 + 0x438037d8) = *(undefined2 *)(param_1 + 0x10);
  *(undefined2 *)(iVar1 + 0x438037da) = *(undefined2 *)(param_1 + 0x12);
  *(undefined2 *)(iVar1 + 0x438037dc) = *(undefined2 *)(param_1 + 0x14);
  *(undefined2 *)(iVar1 + 0x438037de) = *(undefined2 *)(param_1 + 0x16);
  *(undefined2 *)(iVar1 + 0x438037e0) = *(undefined2 *)(param_1 + 0x18);
  *(undefined1 *)(iVar1 + 0x438037e2) = *(undefined1 *)(param_1 + 0x1a);
  return 1;
}


/* 43803450 */

undefined4 dispatch_43803450(int param_1)

{
  *(uint *)(DAT_43803460 + 0x43803696) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803464 */

undefined4 dispatch_43803464(int param_1)

{
  *(undefined2 *)(DAT_43803478 + 0x438036ae) = *(undefined2 *)(param_1 + 8);
  return 1;
}


/* 4380347c */

undefined4 dispatch_4380347c(int param_1)

{
  *(undefined2 *)(DAT_43803490 + 0x438036c8) = *(undefined2 *)(param_1 + 8);
  return 1;
}


/* 43803494 */

undefined4 dispatch_43803494(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438034c0;
  *(uint *)(DAT_438034c0 + 0x438036e0) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x438036e4) = (uint)*(byte *)(param_1 + 9);
  *(undefined4 *)(iVar1 + 0x438036e8) = *(undefined4 *)(param_1 + 10);
  return 1;
}


/* 438034c4 */

undefined4 dispatch_438034c4(int param_1)

{
  *(undefined2 *)(DAT_438034d8 + 0x4380371e) = *(undefined2 *)(param_1 + 8);
  return 1;
}


/* 438034dc */

undefined4 dispatch_438034dc(int param_1)

{
  *(uint *)(DAT_438034ec + 0x4380373a) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 438034f0 */

undefined4 dispatch_438034f0(int param_1)

{
  *(uint *)(DAT_43803500 + 0x43803752) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803504 */

undefined4 dispatch_43803504(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803518;
  *(undefined1 *)(DAT_43803518 + 0x438039fd) = *(undefined1 *)(param_1 + 8);
  *(uint *)(iVar1 + 0x43803a00) = (uint)*(byte *)(param_1 + 9);
  return 1;
}


/* 4380351c */

undefined4 dispatch_4380351c(int param_1)

{
  bool bVar1;
  int iVar2;
  
  bVar1 = *(char *)(param_1 + 8) != '\0';
  if (bVar1) {
    iVar2 = DAT_43803538 + 0x4380352e;
  }
  else {
    iVar2 = DAT_43803534 + 0x43803526;
  }
  *(bool *)(iVar2 + 0x49d) = bVar1;
  return 1;
}


/* 4380353c */

undefined4 dispatch_4380353c(int param_1)

{
  *(uint *)(DAT_4380354c + 0x43803a56) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803550 */

bool FUN_43803550(void)

{
  if (*(int *)(DAT_43803570 + 0x438035bc) == 7) {
    return *(int *)(*(int *)(DAT_43803574 + 0x4380355a + DAT_43803578) + 0x30) != 1;
  }
  return true;
}


/* 4380357c */

void FUN_4380357c(void)

{
  int iVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = DAT_43803650;
  if (*(int *)(DAT_43803650 + 0x43803690) == 1) {
    iVar1 = FUN_43803550();
    if (iVar1 == 0) {
      *(undefined4 *)(iVar4 + 0x43803694) = 0;
    }
    else {
      *(undefined4 *)(iVar4 + 0x43803694) = 2;
    }
    iVar1 = DAT_43803654;
    iVar4 = DAT_43803654 + 0x438035a4;
    *(undefined4 *)(DAT_43803654 + 0x438036b8) = 2;
    *(undefined4 *)(iVar1 + 0x438036bc) = 2;
    uVar2 = 0;
    goto LAB_4380363e;
  }
  if (*(char *)(DAT_43803650 + 0x43803700) == '\x02') {
    *(undefined4 *)(DAT_43803650 + 0x43803694) = 0;
    *(undefined4 *)(iVar4 + 0x43803698) = 0;
    *(undefined4 *)(iVar4 + 0x4380369c) = 0;
    dispatch_4380368c[iVar4] = (code)0x0;
    return;
  }
  if (((*(int *)((int)&DAT_43803670 + DAT_43803650) == 1) &&
      (*(int *)(dispatch_43803674 + DAT_43803650) == 1)) && (iVar1 = FUN_43803550(), iVar1 != 0)) {
    *(undefined4 *)(iVar4 + 0x43803694) = 1;
  }
  else {
    *(undefined4 *)(DAT_43803670 + 0x4380375c) = 0;
  }
  iVar4 = DAT_43803658 + 0x438035ec;
  if ((*(int *)(DAT_43803658 + 0x438036e0) != 1) ||
     (uVar3 = 1, *(int *)(DAT_43803658 + 0x438036e4) != 1)) {
    uVar3 = 0;
    iVar4 = DAT_4380365c + 0x43803602;
  }
  *(undefined4 *)(iVar4 + 0x114) = uVar3;
  iVar4 = *(int *)((int)&DAT_43803704 + DAT_43803660 + 2);
  if ((iVar4 == 1) && (*(int *)(dispatch_43803708 + DAT_43803660 + 2) == 1)) {
    *(undefined4 *)(DAT_43803660 + 0x43803722) = 1;
LAB_4380362c:
    iVar4 = DAT_43803668 + 0x43803632;
    uVar2 = 1;
    if (*(int *)(DAT_43803668 + 0x43803736) == 1) goto LAB_4380363e;
  }
  else {
    *(undefined4 *)(DAT_43803664 + 0x43803740) = 0;
    if (iVar4 == 1) goto LAB_4380362c;
  }
  uVar2 = 0;
  iVar4 = DAT_4380366c + 0x43803640;
LAB_4380363e:
  *(undefined1 *)(iVar4 + 0x108) = uVar2;
  return;
}


/* 43803674 */

undefined4 dispatch_43803674(int param_1)

{
  *(uint *)(DAT_43803688 + 0x4380377a) = (uint)*(byte *)(param_1 + 8);
  FUN_4380357c();
  return 1;
}


/* 4380368c */

undefined4 dispatch_4380368c(int param_1)

{
  *(uint *)(DAT_438036a0 + 0x4380378a) = (uint)*(byte *)(param_1 + 8);
  FUN_4380357c();
  return 1;
}


/* 438036a4 */

undefined4 dispatch_438036a4(int param_1,undefined4 param_2)

{
  uint uVar1;
  undefined1 uStack_14;
  undefined1 auStack_13 [3];
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uVar1 = (uint)(*(char *)(param_1 + 8) == '\x01');
  if (*(char *)(param_1 + 9) == '\x01') {
    uVar1 = uVar1 | 2;
  }
  _uStack_14 = CONCAT31(SUB43((uint)param_2 >> 8,0),1);
  *(uint *)(DAT_43803704 + 0x43803bd4) = uVar1;
  _uStack_14 = CONCAT22(*(undefined2 *)(param_1 + 2),_uStack_14);
  uStack_10 = *(undefined4 *)(param_1 + 4);
  uStack_c = 0xf000;
  FUN_437feef8(&uStack_14,0xc,&DAT_00020002,0xf000,param_1);
  return 1;
}


/* 43803708 */

undefined4 dispatch_43803708(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  
  uVar1 = *(undefined1 *)(param_1 + 8);
  *(undefined1 *)(DAT_43803728 + 0x43803ba9) = uVar1;
  FUN_43901a8c(4,0x202e,uVar1,*(undefined1 *)(param_1 + 8),param_4);
  return 1;
}


/* 4380372c */

undefined4 dispatch_4380372c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803744 + 0x43803736;
  *(uint *)(DAT_43803744 + 0x43803c12) = (uint)*(byte *)(param_1 + 8);
  candidate_437dfba0(iVar1);
  return 1;
}


/* 43803748 */

undefined4 dispatch_43803748(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_4380377c;
  iVar2 = DAT_4380377c + 0x43803752;
  *(uint *)(DAT_4380377c + 0x4380390e) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x43803912) = (uint)*(byte *)(param_1 + 9);
  *(uint *)(iVar1 + 0x43803916) = (uint)*(byte *)(param_1 + 10);
  *(uint *)(iVar1 + 0x4380391a) = (uint)*(byte *)(param_1 + 0xb);
  *(uint *)(iVar1 + 0x4380391e) = (uint)*(byte *)(param_1 + 0xc);
  *(uint *)(iVar1 + 0x43803922) = (uint)*(byte *)(param_1 + 0xd);
  candidate_437dfba0(iVar2);
  return 1;
}


/* 43803780 */

undefined4 dispatch_43803780(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803798 + 0x4380378a;
  *(uint *)(DAT_43803798 + 0x43803c5a) = (uint)*(byte *)(param_1 + 8);
  candidate_437dfba0(iVar1);
  return 1;
}


/* 4380379c */

undefined4 dispatch_4380379c(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438037c8;
  *(uint *)((int)&DAT_43803884 + DAT_438037c8 + 2) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(dispatch_43803888 + iVar1 + 2) = (uint)*(byte *)(param_1 + 9);
  if (*(char *)(iVar1 + 0x4380388e) != -1) {
    *(char *)(iVar1 + 0x4380388e) = *(char *)(iVar1 + 0x4380388e) + '\x01';
  }
  candidate_437dfba0(DAT_438037cc + 0x438037c2);
  return 1;
}


/* 438037d0 */

undefined4 dispatch_438037d0(int param_1)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = FUN_4378f9b4();
  iVar1 = DAT_4380382c;
  if (*(int *)(*(int *)(iVar3 + 8) + 0x6c) == 0) {
    uVar4 = (uint)*(byte *)(param_1 + 8);
    iVar3 = DAT_43803828 + 0x438037ee;
  }
  else {
    uVar4 = 0;
    iVar3 = DAT_43803824 + 0x438037e6;
  }
  *(uint *)(iVar3 + 0x174) = uVar4;
  FUN_43901a8c(4,0x2039,*(undefined4 *)(iVar1 + 0x43803970),0xff);
  uVar2 = FUN_43b00aaa(*(undefined4 *)(iVar1 + 0x43803860),*(undefined4 *)(iVar1 + 0x43803970),
                       *(undefined4 *)(iVar1 + 0x43803974));
  *(undefined1 *)(iVar1 + 0x43803978) = uVar2;
  FUN_4380357c();
  candidate_437dfba0(iVar1 + 0x438037fc);
  return 1;
}


/* 43803830 */

undefined4 dispatch_43803830(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_43803884;
  iVar2 = DAT_43803884 + 0x4380383c;
  *(uint *)((int)&DAT_43803948 + DAT_43803884) = (uint)*(byte *)(param_1 + 8);
  FUN_4380357c();
  *(undefined1 *)(iVar1 + 0x43803d24) = *(undefined1 *)(param_1 + 9);
  *(undefined1 *)(iVar1 + 0x43803d25) = *(undefined1 *)(param_1 + 10);
  *(undefined1 *)(iVar1 + 0x43803d26) = *(undefined1 *)(param_1 + 0xb);
  *(undefined1 *)(iVar1 + 0x43803d27) = *(undefined1 *)(param_1 + 0xc);
  *(undefined1 *)(iVar1 + 0x43803d28) = *(undefined1 *)(param_1 + 0xd);
  *(undefined1 *)(iVar1 + 0x43803d29) = *(undefined1 *)(param_1 + 0xe);
  *(undefined1 *)(iVar1 + 0x43803d2a) = *(undefined1 *)(param_1 + 0xf);
  *(undefined1 *)(iVar1 + 0x43803d2b) = *(undefined1 *)(param_1 + 0x10);
  *(undefined1 *)(iVar1 + 0x43803d2c) = *(undefined1 *)(param_1 + 0x11);
  candidate_437dfba0(iVar2);
  return 1;
}


/* 43803888 */

undefined4 dispatch_43803888(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_438038b4;
  iVar2 = DAT_438038b4 + 0x43803892;
  *(uint *)(DAT_438038b4 + 0x43803982) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x4380398a) = (uint)*(byte *)(param_1 + 9);
  *(uint *)(iVar1 + 0x43803992) = (uint)*(byte *)(param_1 + 10);
  *(uint *)(iVar1 + 0x43803996) = (uint)*(byte *)(param_1 + 0xb);
  FUN_4380357c();
  candidate_437dfba0(iVar2);
  return 1;
}


/* 438038b8 */

undefined4 dispatch_438038b8(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438038d4 + 0x438038c2;
  *(uint *)(DAT_438038d4 + 0x438039ae) = (uint)*(byte *)(param_1 + 8);
  FUN_4380357c();
  candidate_437dfba0(iVar1);
  return 1;
}


/* 438038d8 */

void FUN_438038d8(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar1 = DAT_43803948;
  FUN_437f6d80(DAT_43803948 + 0x43803918,*(undefined4 *)(DAT_43803948 + 0x43803928),
               *(undefined4 *)(DAT_43803948 + 0x4380391c),
               *(undefined4 *)((int)&DAT_43803a58 + DAT_43803948));
  FUN_437f6d80(iVar1 + 0x43803920,*(undefined4 *)(iVar1 + 0x43803928),0,
               *(undefined4 *)((int)&DAT_43803a58 + iVar1));
  if (*(int *)(iVar1 + 0x43803944) == 0x1f) {
    if (*(int *)((int)&DAT_43803a58 + iVar1) == 0) {
      uVar2 = *(undefined4 *)(iVar1 + 0x43803928);
      uVar3 = 1;
      uVar4 = 0;
    }
    else {
      uVar2 = *(undefined4 *)(iVar1 + 0x43803928);
      uVar3 = 0;
      uVar4 = 1;
    }
  }
  else if (*(int *)(iVar1 + 0x43803944) == 0x20) {
    if (*(int *)((int)&DAT_43803a58 + iVar1) == 0) {
      uVar2 = *(undefined4 *)(iVar1 + 0x43803928);
      uVar3 = 2;
      uVar4 = 0;
    }
    else {
      uVar3 = 1;
      uVar2 = *(undefined4 *)(iVar1 + 0x43803928);
      uVar4 = 1;
    }
  }
  else {
    uVar2 = *(undefined4 *)(iVar1 + 0x43803928);
    uVar3 = 0;
    uVar4 = *(undefined4 *)((int)&DAT_43803a58 + iVar1);
  }
  FUN_437f6d80(iVar1 + 0x43803924,uVar2,uVar3,uVar4);
  return;
}


/* 4380394c */

undefined4 dispatch_4380394c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_20 [2];
  undefined2 uStack_1e;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  
  iVar1 = DAT_438039c0;
  iVar2 = DAT_438039c0 + 0x4380395a;
  *(uint *)(DAT_438039c0 + 0x438039a2) = (uint)*(byte *)(param_1 + 9);
  *(uint *)(iVar1 + 0x438039a6) = (uint)*(byte *)(param_1 + 10);
  *(uint *)(iVar1 + 0x43803996) = (uint)*(byte *)(param_1 + 8);
  FUN_438038d8();
  candidate_437dfba0(iVar2);
  uStack_1e = *(undefined2 *)(param_1 + 2);
  auStack_20[0] = 1;
  uStack_1c = *(undefined4 *)(param_1 + 4);
  uStack_18 = 0xf000;
  uStack_14 = *(undefined1 *)(param_1 + 8);
  uStack_13 = *(undefined1 *)(param_1 + 9);
  uStack_12 = *(undefined1 *)(param_1 + 10);
  FUN_437feef8(auStack_20,0x10,&DAT_00020002);
  return 1;
}


/* 438039c4 */

undefined4 dispatch_438039c4(int param_1)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = FUN_4378f9b4();
  iVar1 = DAT_43803a24;
  if (*(int *)(*(int *)(iVar3 + 8) + 0x6c) == 0) {
    uVar4 = (uint)*(byte *)(param_1 + 8);
    iVar3 = DAT_43803a20 + 0x438039e2;
  }
  else {
    uVar4 = 0;
    iVar3 = DAT_43803a1c + 0x438039da;
  }
  *(uint *)(iVar3 + 0x178) = uVar4;
  FUN_43901a8c(4,0x203b,*(undefined4 *)(iVar1 + 0x43803b68),0xff);
  uVar2 = FUN_43b00aaa(*(undefined4 *)(iVar1 + 0x43803a54),*(undefined4 *)(iVar1 + 0x43803b64),
                       *(undefined4 *)(iVar1 + 0x43803b68));
  *(undefined1 *)(iVar1 + 0x43803b6c) = uVar2;
  FUN_438038d8();
  FUN_4380357c();
  candidate_437dfba0(iVar1 + 0x438039f0);
  return 1;
}


/* 43803a28 */

undefined4 dispatch_43803a28(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43803a58;
  *(undefined4 *)(DAT_43803a58 + 0x43803da6) = *(undefined4 *)(param_1 + 4);
  *(uint *)(iVar1 + 0x43803daa) = (uint)*(byte *)(param_1 + 8);
  FUN_43801f3c(0x2060);
  return 1;
}


/* 43803a5c */

undefined4 dispatch_43803a5c(int param_1)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  bVar1 = *(byte *)(param_1 + 8);
  *(uint *)((int)&DAT_43803b08 + DAT_43803af4 + 2) = (uint)bVar1;
  iVar3 = DAT_43803af8;
  switch((uint)bVar1) {
  case 1:
    *(uint *)(DAT_43803af8 + 0x43803b30) = (uint)*(byte *)(param_1 + 0xb);
    *(undefined1 *)(iVar3 + 0x43803b34) = *(undefined1 *)(param_1 + 0x13);
  default:
    goto switchD_43803a6e_caseD_2;
  case 3:
    uVar2 = (uint)*(byte *)(param_1 + 10);
    iVar3 = DAT_43803afc + 0x43803a9a;
    break;
  case 5:
    uVar2 = (uint)*(byte *)(param_1 + 0x12);
    iVar3 = DAT_43803b1c + 0x43803ae6;
    break;
  case 6:
    uVar2 = (uint)*(byte *)(param_1 + 0xc);
    iVar3 = DAT_43803b00 + 0x43803aa2;
    break;
  case 7:
    uVar2 = (uint)*(byte *)(param_1 + 0xd);
    iVar3 = DAT_43803b04 + 0x43803aaa;
    break;
  case 8:
    uVar2 = (uint)*(byte *)(param_1 + 0xe);
    iVar3 = DAT_43803b08 + 0x43803ab2;
    break;
  case 9:
    uVar2 = (uint)*(byte *)(param_1 + 9);
    iVar3 = DAT_43803b0c + 0x43803aba;
    break;
  case 0xb:
    *(uint *)(DAT_43803b10 + 0x43803b6e) = (uint)*(byte *)(param_1 + 0xf);
    FUN_43801f3c(0x2058);
    goto switchD_43803a6e_caseD_2;
  case 0xc:
    uVar2 = (uint)*(byte *)(param_1 + 0x10);
    iVar3 = DAT_43803b14 + 0x43803ad6;
    break;
  case 0xd:
    uVar2 = (uint)*(byte *)(param_1 + 0x11);
    iVar3 = DAT_43803b18 + 0x43803ade;
  }
  *(uint *)(iVar3 + 0xa8) = uVar2;
switchD_43803a6e_caseD_2:
  candidate_437dfba0(DAT_43803b20 + 0x43803aee);
  return 1;
}


/* 43803b24 */

undefined4 dispatch_43803b24(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_43803b54;
  if ((((*(int *)(DAT_43803b54 + 0x43803b8e) == 0) && (iVar2 = FUN_437c1e3c(), iVar2 != 0)) &&
      (*(int *)(iVar1 + 0x43803e76) == 1)) && (*(char *)(param_1 + 8) == '\0')) {
    FUN_43787a90();
  }
  *(uint *)(DAT_43803b58 + 0x43803e98) = (uint)*(byte *)(param_1 + 8);
  return 1;
}


/* 43803b5c */

undefined4 dispatch_43803b5c(int param_1)

{
  byte bVar1;
  int iVar2;
  
  if (*(int *)(DAT_43803b90 + 0x43803bc4) == 0) {
    if ((*(uint *)((int)&DAT_43803e28 + DAT_43803b90) != (uint)*(byte *)(param_1 + 8)) &&
       (*(byte *)(param_1 + 8) != 0)) {
      FUN_43787a90();
    }
  }
  iVar2 = DAT_43803b94;
  bVar1 = *(byte *)(param_1 + 8);
  *(uint *)(DAT_43803b94 + 0x43803ed2) = (uint)bVar1;
  *(uint *)(iVar2 + 0x43803e46) = (uint)bVar1;
  *(uint *)(iVar2 + 0x43803eda) = (uint)*(byte *)(param_1 + 9);
  return 1;
}


/* 43803b98 */

undefined4 dispatch_43803b98(int param_1)

{
  int iVar1;
  
  if (*(int *)(DAT_43803c8c + 0x43803c00) == 0) {
    if (*(uint *)(DAT_43803c8c + 0x43803ea4) == (uint)*(byte *)(param_1 + 8)) {
      if (*(uint *)(DAT_43803c8c + 0x43803ea8) == (uint)*(byte *)(param_1 + 0x11)) {
        if (*(short *)(DAT_43803c8c + 0x43803e88) == *(short *)(param_1 + 9)) {
          if (*(short *)(DAT_43803c8c + 0x43803e8a) == *(short *)(param_1 + 0xb)) {
            if (*(short *)(DAT_43803c8c + 0x43803eac) == *(short *)(param_1 + 0xd)) {
              if (*(short *)(DAT_43803c8c + 0x43803eae) == *(short *)(param_1 + 0xf)) {
                if (*(short *)(DAT_43803c8c + 0x43803eb0) == *(short *)(param_1 + 0x14)) {
                  if (*(short *)(DAT_43803c8c + 0x43803eb2) == *(short *)(param_1 + 0x12)) {
                    if (*(uint *)(DAT_43803c8c + 0x43803f5c) == (uint)*(byte *)(param_1 + 0x16))
                    goto LAB_43803c2a;
                  }
                }
              }
            }
          }
        }
      }
    }
    FUN_43787a90(0);
  }
LAB_43803c2a:
  iVar1 = DAT_43803c90;
  *(uint *)(DAT_43803c90 + 0x43803f38) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(iVar1 + 0x43803f3c) = (uint)*(byte *)(param_1 + 0x11);
  *(undefined2 *)(iVar1 + 0x43803f1c) = *(undefined2 *)(param_1 + 9);
  *(undefined2 *)(iVar1 + 0x43803f1e) = *(undefined2 *)(param_1 + 0xb);
  *(undefined2 *)(iVar1 + 0x43803f40) = *(undefined2 *)(param_1 + 0xd);
  *(undefined2 *)(iVar1 + 0x43803f42) = *(undefined2 *)(param_1 + 0xf);
  *(undefined2 *)(iVar1 + 0x43803f44) = *(undefined2 *)(param_1 + 0x14);
  *(undefined2 *)(iVar1 + 0x43803f46) = *(undefined2 *)(param_1 + 0x12);
  *(uint *)(iVar1 + 0x43803ff0) = (uint)*(byte *)(param_1 + 0x16);
  return 1;
}


/* 43803c94 */

undefined8 dispatch_43803c94(int param_1,undefined4 param_2,undefined4 param_3)

{
  char cVar1;
  undefined1 uStack_c;
  undefined3 uStack_b;
  undefined4 uStack_8;
  
  cVar1 = *(char *)(param_1 + 8);
  *(char *)((int)&DAT_43804158 + DAT_43803cb4 + 3) = cVar1;
  if (cVar1 == '\x02') {
    _uStack_c = CONCAT31((int3)((uint)param_2 >> 8),1);
    uStack_8 = param_3;
    FUN_439d94fc(&uStack_c);
  }
  return CONCAT44(param_1,1);
}


/* 43803e2c */

undefined4 dispatch_43803e2c(int param_1)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  undefined1 auStack_1c [2];
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar5 = DAT_43803f9c + 0x43803e3c;
  if (*(char *)(param_1 + 8) == '\x19') {
    FUN_4372a4e0(0);
    FUN_4372a604(0x1a);
  }
  else {
    if (*(char *)(DAT_43803fa0 + 0x438043a0) == '\0') {
      FUN_4372a4e0(1);
    }
    FUN_4372a5d4(0x1a);
  }
  cVar2 = *(char *)(*(int *)(iVar5 + DAT_43803fa4) + 0xb8);
  if (cVar2 != '\0') {
    *(char *)(param_1 + 8) = cVar2;
    if (cVar2 == '\x17') {
      *(undefined1 *)(param_1 + 10) = 1;
    }
    else if (cVar2 == '\x1c') {
      *(undefined1 *)(param_1 + 0xd) = 0;
      *(undefined1 *)(param_1 + 0xc) = 2;
      *(undefined1 *)(param_1 + 0xe) = 0;
      *(undefined1 *)(param_1 + 0xf) = 0;
    }
    else if (cVar2 == '\x03') {
      *(undefined1 *)(param_1 + 0xc) = 3;
      *(undefined1 *)(param_1 + 0xd) = 0;
      *(undefined1 *)(param_1 + 0xe) = 0;
      *(undefined1 *)(param_1 + 0xf) = 0;
    }
  }
  iVar5 = DAT_43803fb0;
  uVar4 = (uint)*(byte *)(param_1 + 8);
  if ((uVar4 < 0x1e) && ((1 << (uint)*(byte *)(param_1 + 8) & DAT_43803f98) != 0)) {
    uVar7 = 0xf001;
    FUN_43803d80(3,0xd,1,DAT_43803fa8 + 0x43803ee0,uVar4,*(undefined1 *)(param_1 + 9),
                 *(undefined1 *)(param_1 + 10),*(undefined1 *)(param_1 + 0xb),
                 *(undefined4 *)(param_1 + 0xc));
    FUN_43902718(DAT_43803fac + 0x43803f08,*(undefined1 *)(param_1 + 8),*(undefined1 *)(param_1 + 9)
                 ,*(undefined1 *)(param_1 + 10),*(undefined1 *)(param_1 + 0xb),
                 *(undefined4 *)(param_1 + 0xc));
  }
  else {
    uVar7 = 0xf000;
    *(uint *)(DAT_43803fb0 + 0x43803f74) = (uint)*(byte *)(param_1 + 9);
    bVar1 = *(byte *)(param_1 + 10);
    *(uint *)(iVar5 + 0x43803f7c) = uVar4;
    *(uint *)(iVar5 + 0x43803f80) = (uint)bVar1;
    *(uint *)(iVar5 + 0x43803f68) = (uint)*(byte *)(param_1 + 0xb);
    *(undefined4 *)(iVar5 + 0x43803f6c) = *(undefined4 *)(param_1 + 0xc);
  }
  iVar5 = DAT_43803fb4;
  iVar6 = DAT_43803fb4 + 0x43803f3e;
  uVar3 = FUN_43b00aaa(*(undefined4 *)((int)&DAT_43803fa0 + DAT_43803fb4 + 2),
                       *(undefined4 *)(DAT_43803fb4 + 0x438040b2),
                       *(undefined4 *)(DAT_43803fb4 + 0x438040b6));
  *(undefined1 *)(iVar5 + 0x438040ba) = uVar3;
  FUN_438038d8();
  FUN_4380357c();
  candidate_437dfba0(iVar6);
  uStack_1a = *(undefined2 *)(param_1 + 2);
  auStack_1c[0] = 1;
  uStack_18 = *(undefined4 *)(param_1 + 4);
  uStack_14 = uVar7;
  FUN_437feef8(auStack_1c,0xc,&DAT_00020002);
  return 1;
}


/* 43804058 */

undefined4 dispatch_43804058(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint *puVar7;
  int iVar8;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar8 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  iVar4 = FUN_43ae8c66(*(undefined1 *)(param_1 + 9));
  iVar6 = DAT_43804148 + 0x43804068;
  if (iVar4 == 0) {
    FUN_439c5a04(&uStack_1c,0,0xc);
    uStack_1c = CONCAT31(uStack_1c._1_3_,1);
    uStack_1c = CONCAT22(*(undefined2 *)(param_1 + 2),(undefined2)uStack_1c);
    uStack_18 = *(undefined4 *)(param_1 + 4);
    uStack_14 = 0xf001;
    FUN_437feef8(&uStack_1c,0xc,&DAT_00020002,0xf001,iVar8);
  }
  iVar8 = DAT_4380414c;
  bVar1 = *(byte *)(param_1 + 9);
  bVar2 = *(byte *)(param_1 + 0x15);
  *(uint *)(DAT_4380414c + 0x438040d0) = (uint)*(byte *)(param_1 + 8);
  bVar3 = *(byte *)(param_1 + 10);
  *(uint *)(iVar8 + 0x438040d4) = (uint)bVar1;
  *(uint *)(iVar8 + 0x438040d8) = (uint)bVar3;
  *(uint *)(iVar8 + 0x438040dc) = (uint)*(byte *)(param_1 + 0xd);
  uVar5 = (uint)*(byte *)(param_1 + 0xe);
  *(uint *)(iVar8 + 0x438040e4) = (uint)bVar2;
  bVar2 = *(byte *)(param_1 + 0x16);
  *(uint *)(iVar8 + 0x438040e0) = uVar5;
  *(uint *)(iVar8 + 0x438040e8) = (uint)bVar2;
  if (*(char *)(*(int *)(iVar6 + DAT_43804150) + 0x10) != '\0') {
    *(undefined4 *)(iVar8 + 0x438040d0) = 4;
    if (1 < bVar1 - 2) {
      *(undefined4 *)(iVar8 + 0x438040d4) = 2;
    }
    iVar8 = DAT_43804154;
    *(undefined4 *)(DAT_43804154 + 0x4380410e) = 0;
    *(undefined4 *)(iVar8 + 0x43804112) = 6;
  }
  puVar7 = (uint *)(DAT_43804158 + 0x438040f4);
  if (uVar5 != *puVar7) {
    FUN_43901a8c(4,0x2042,uVar5,
                 (uint)*(byte *)(param_1 + 0xf) * 0x1000000 +
                 (uint)*(byte *)(param_1 + 0x10) * 0x10000 + (uint)*(byte *)(param_1 + 0x14) +
                 (uint)*(byte *)(param_1 + 0x11) * 0x100);
    *puVar7 = *(uint *)((int)&DAT_43804148 + DAT_4380415c);
  }
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804160 + 0x43804140);
  return 1;
}


/* 43804164 */

undefined4 dispatch_43804164(int param_1)

{
  byte bVar1;
  int iVar2;
  char acStack_1c [2];
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar2 = DAT_438041e4;
  bVar1 = *(byte *)(param_1 + 8);
  *(uint *)(DAT_438041e4 + 0x438041d2) = (uint)bVar1;
  if (bVar1 == 0) {
    acStack_1c[0] = bVar1 + 1;
    uStack_1a = *(undefined2 *)(param_1 + 2);
    uStack_18 = *(undefined4 *)(param_1 + 4);
    uStack_14 = 0xf000;
    FUN_437feef8(acStack_1c,0xc,&DAT_00020002);
  }
  else {
    FUN_43787a60();
    (&UNK_438046ca)[iVar2] = 0;
    FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438041e8 + 0x438041dc
                );
  }
  return 1;
}


/* 438041ec */

undefined4 dispatch_438041ec(int param_1)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int iVar3;
  
  iVar3 = DAT_43804274;
  *(undefined4 *)((int)&DAT_4380445c + DAT_43804274 + 2) = *(undefined4 *)(param_1 + 4);
  *(undefined4 *)(dispatch_438044dc + iVar3 + 6) = 3;
  uVar1 = *(undefined2 *)(param_1 + 8);
  *(undefined2 *)((int)&DAT_43804460 + iVar3 + 2) = uVar1;
  uVar2 = *(undefined2 *)(param_1 + 10);
  *(undefined2 *)(iVar3 + 0x438044e6) = uVar1;
  *(undefined2 *)(dispatch_43804464 + iVar3) = uVar2;
  *(undefined2 *)(iVar3 + 0x438044e8) = uVar2;
  *(char *)(iVar3 + 0x4380445a) = *(char *)(iVar3 + 0x4380445a) + '\x01';
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804278 + 0x4380425c);
  FUN_43801f3c(0x2002);
  FUN_43801f3c(0x2001);
  return 1;
}


/* 4380427c */

undefined4 dispatch_4380427c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_438042b8;
  (&UNK_43804692)[DAT_438042b8] = 1;
  *(uint *)(&UNK_43804696 + iVar1) = (uint)*(byte *)(param_1 + 8);
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438042bc + 0x438042b0,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 438042c0 */

undefined4 dispatch_438042c0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = DAT_4380430c;
  *(undefined2 *)(&UNK_43804706 + DAT_4380430c) = *(undefined2 *)(param_1 + 8);
  uVar1 = *(undefined2 *)(param_1 + 10);
  (&UNK_4380470a)[iVar2] = 1;
  *(undefined2 *)(&UNK_43804708 + iVar2) = uVar1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804310 + 0x43804306,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 43804314 */

undefined4 dispatch_43804314(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  char *pcVar3;
  
  iVar1 = DAT_43804368;
  pcVar3 = (char *)(DAT_4380436c + 0x43804322);
  (&UNK_4380473c)[DAT_43804368] = 1;
  (&UNK_4380473d)[iVar1] = *pcVar3;
  *(uint *)(&UNK_43804738 + iVar1) = (uint)*(byte *)(param_1 + 8);
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804370 + 0x43804352,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  if (*pcVar3 == -1) {
    cVar2 = '\0';
  }
  else {
    cVar2 = *pcVar3 + '\x01';
  }
  *pcVar3 = cVar2;
  return 1;
}


/* 43804374 */

undefined4 dispatch_43804374(int param_1)

{
  *(uint *)(&UNK_438046b4 + DAT_438043a8) = (uint)*(byte *)(param_1 + 8);
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438043ac + 0x438043a2);
  return 1;
}


/* 438043b0 */

undefined4 dispatch_438043b0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  (&UNK_4380483a)[DAT_438043e4] = 1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438043e8 + 0x438043de,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 438043ec */

undefined4 dispatch_438043ec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  (&UNK_43804877)[DAT_43804420] = 1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804424 + 0x4380441a,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 43804428 */

undefined4 dispatch_43804428(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  (&UNK_438048b4)[DAT_4380445c] = 1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_43804460 + 0x43804456,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 43804464 */

undefined4 dispatch_43804464(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  (&UNK_438048fa)[DAT_43804498] = 1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_4380449c + 0x43804492,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 438044a0 */

undefined4 dispatch_438044a0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  (&UNK_43804937)[DAT_438044d4] = 1;
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438044d8 + 0x438044ce,
               (uint)*(uint3 *)(param_1 + 4),param_4);
  return 1;
}


/* 438044dc */

undefined4 dispatch_438044dc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  bVar1 = *(byte *)(param_1 + 8);
  if (bVar1 == 1) {
    uStack_14 = CONCAT31((int3)((uint)param_2 >> 8),bVar1);
    uStack_14 = CONCAT22(*(undefined2 *)(param_1 + 2),(undefined2)uStack_14);
    uStack_10 = *(undefined4 *)(param_1 + 4);
    uStack_c = 0xf000;
    FUN_437feef8(&uStack_14,0xc,&DAT_00020002);
    *(undefined4 *)(DAT_43804554 + 0x4380453a) = 1;
  }
  else {
    *(uint *)(DAT_43804558 + 0x43804542) = (uint)bVar1;
    uStack_14 = param_2;
    uStack_10 = param_3;
    uStack_c = param_4;
    FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_4380455c + 0x4380454c
                 ,(uint)*(uint3 *)(param_1 + 4),param_1);
  }
  return 1;
}


/* 43804560 */

undefined4 dispatch_43804560(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_438045b4;
  *(uint *)(&UNK_43804aac + DAT_438045b4) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(&UNK_43804ab0 + iVar1) = (uint)*(byte *)(param_1 + 9);
  *(undefined4 *)(&UNK_43804ab4 + iVar1) = *(undefined4 *)(param_1 + 10);
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_438045b8 + 0x438045ac);
  return 1;
}


/* 438045bc */

undefined4 dispatch_438045bc(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_43804608;
  *(uint *)(&UNK_43804688 + DAT_43804608) = (uint)*(byte *)(param_1 + 8);
  *(uint *)(&UNK_4380468c + iVar1) = (uint)*(byte *)(param_1 + 9);
  *(uint *)(&UNK_43804690 + iVar1) = (uint)*(byte *)(param_1 + 10);
  FUN_43801f3c(0x2062);
  FUN_43803fb8(*(undefined2 *)(param_1 + 2),*(undefined4 *)(param_1 + 4),DAT_4380460c + 0x43804600);
  return 1;
}


/* 43804c38 */

undefined * candidate_43804c38(void)

{
  int iVar1;
  
  FUN_437876dc();
  iVar1 = FUN_43b00cba();
  if (iVar1 != 0) {
    iVar1 = FUN_437876dc();
    return (undefined *)(iVar1 + 8);
  }
  return &UNK_43804c56 + DAT_43804c58;
}


/* 43804c5c */

void FUN_43804c5c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  char *pcVar9;
  
  iVar1 = FUN_43560d38(0x17,0,param_3,param_4,param_4);
  if (iVar1 == 0) {
    FUN_437876dc();
    iVar2 = FUN_43b00cba();
    iVar4 = DAT_43804d6c;
    iVar1 = DAT_43804d54;
    if (iVar2 == 0) {
      puVar7 = (undefined4 *)(DAT_43804d6c + 0x43804cdc);
      FUN_439c5320(param_1,DAT_43804d70 + 0x43804cde,0x560);
      if (*(int *)(iVar4 + 0x43804ce4) == 0) {
        puVar8 = (undefined4 *)(DAT_43804d74 + 0x43804cea);
        if (*(int *)(DAT_43804d74 + 0x43804cf2) != 0) {
          uVar3 = *(undefined4 *)(DAT_43804d74 + 0x43804cee);
          uVar5 = *(undefined4 *)(DAT_43804d74 + 0x43804cf2);
          *(undefined4 *)(DAT_43804d74 + 0x43804cf2) = 0;
          *puVar7 = *puVar8;
          *(undefined4 *)(iVar4 + 0x43804ce0) = uVar3;
          *(undefined4 *)(iVar4 + 0x43804ce4) = uVar5;
        }
      }
    }
    else {
      uVar3 = FUN_437876dc();
      pcVar9 = (char *)(iVar1 + 0x43804c84);
      FUN_43b00d06(uVar3,param_1);
      iVar4 = DAT_43804d5c;
      iVar1 = DAT_43804d58;
      if (*pcVar9 == '\0') {
        if ((*(int *)(DAT_43804d60 + 0x43804cae) == 0) && (*(int *)(DAT_43804d64 + 0x43804cb6) != 0)
           ) {
          *pcVar9 = '\x01';
        }
      }
      else {
        puVar7 = (undefined4 *)(DAT_43804d58 + 0x43804c92);
        *pcVar9 = '\0';
        uVar3 = *puVar7;
        uVar5 = *(undefined4 *)(iVar1 + 0x43804c96);
        uVar6 = *(undefined4 *)(iVar1 + 0x43804c9a);
        *(undefined4 *)(iVar1 + 0x43804c9a) = 0;
        *(undefined4 *)(iVar4 + 0x43804c96) = uVar3;
        *(undefined4 *)(iVar4 + 0x43804c9a) = uVar5;
        *(undefined4 *)(iVar4 + 0x43804c9e) = uVar6;
      }
      FUN_437876dc();
      iVar1 = FUN_43b00cb4();
      if (iVar1 == 1) {
        uVar3 = FUN_437876dc();
        FUN_43b00cd0(uVar3,DAT_43804d68 + 0x43804cca);
      }
    }
    FUN_43560d1c(0x17);
  }
  else {
    FUN_437876dc();
    iVar4 = FUN_43b00cba();
    iVar1 = DAT_43804d78;
    if (iVar4 != 0) {
      uVar3 = FUN_437876dc();
      FUN_43b00d06(uVar3,param_1);
      iVar2 = DAT_43804d80;
      iVar4 = DAT_43804d7c;
      if (*(char *)(iVar1 + 0x43804d14) != '\0') {
        uVar3 = *(undefined4 *)(DAT_43804d7c + 0x43804d26);
        uVar5 = *(undefined4 *)(DAT_43804d7c + 0x43804d2a);
        *(undefined4 *)(DAT_43804d80 + 0x43804d24) = *(undefined4 *)(DAT_43804d7c + 0x43804d22);
        *(undefined4 *)(iVar2 + 0x43804d28) = uVar3;
        *(undefined4 *)(iVar2 + 0x43804d2c) = uVar5;
        *(undefined4 *)(iVar4 + 0x43804d2a) = 0;
        *(char *)(iVar1 + 0x43804d14) = '\0';
      }
    }
  }
  if (((*(int *)(param_1 + 0x11c) == 3) || (*(int *)(param_1 + 0x11c) == 0x15)) &&
     (*(int *)(param_1 + 0x2c4) - 3U < 2)) {
    uVar3 = 2;
  }
  else {
    uVar3 = *(undefined4 *)(param_1 + 0x350);
  }
  *(undefined4 *)(param_1 + 0x2c4) = uVar3;
  return;
}


/* 43804de8 */

undefined * FUN_43804de8(void)

{
  return &UNK_43804dee + DAT_43804df0;
}


/* 43804df4 */

undefined4 FUN_43804df4(int param_1)

{
  *(undefined1 *)(DAT_43804e04 + 0x43805299) = *(undefined1 *)(param_1 + 8);
  return 1;
}


/* 43804e08 */

undefined4 dispatch_43804e08(int param_1)

{
  int iVar1;
  char *pcVar2;
  
  dispatch_438020c0(param_1 + 8);
  dispatch_43802128(param_1 + 0x11);
  dispatch_438028a8(param_1 + 0x1c);
  dispatch_4380286c(param_1 + 0x25);
  dispatch_43802200(param_1 + 0x2e);
  dispatch_43802240(param_1 + 0x3b);
  dispatch_43802258(param_1 + 0x45);
  dispatch_43802284(param_1 + 0x53);
  dispatch_43802298(param_1 + 0x5c);
  dispatch_438022ac(param_1 + 0x65);
  dispatch_438022c0(param_1 + 0x6e);
  dispatch_438022d4(param_1 + 0x77);
  dispatch_438022e8(param_1 + 0x80);
  dispatch_43802308(param_1 + 0x8b);
  dispatch_4380231c(param_1 + 0x94);
  dispatch_43802330(param_1 + 0x9d);
  dispatch_43803780(param_1 + 0xa6);
  dispatch_43802590(param_1 + 0xaf);
  dispatch_438025a4(param_1 + 0xb8);
  dispatch_4380379c(param_1 + 0xc6);
  dispatch_43802344(param_1 + 0xd0);
  dispatch_43802a00(param_1 + 0xd9);
  dispatch_43802358(param_1 + 0xe2);
  dispatch_438023e4(param_1 + 0xeb);
  dispatch_438023fc(param_1 + 0xf5);
  dispatch_438026dc(param_1 + 0xfe);
  dispatch_43803b98(param_1 + 0x107);
  dispatch_43803b5c(param_1 + 0x11e);
  dispatch_438025dc(param_1 + 0x128);
  dispatch_438025f4(param_1 + 0x131);
  dispatch_4380260c(param_1 + 0x13a);
  dispatch_43802634(param_1 + 0x143);
  dispatch_43803748(param_1 + 0x14d);
  dispatch_438025c8(param_1 + 0x15b);
  dispatch_438027a4(param_1 + 0x164);
  dispatch_438027e0(param_1 + 0x16d);
  dispatch_438027f4(param_1 + 0x176);
  dispatch_43802808(param_1 + 0x17f);
  dispatch_4380281c(param_1 + 0x188);
  dispatch_43802830(param_1 + 0x191);
  dispatch_43802844(param_1 + 0x19a);
  dispatch_43802858(param_1 + 0x1a3);
  dispatch_43802430(param_1 + 0x1b5);
  dispatch_43802880(param_1 + 0x1be);
  dispatch_438027b8(param_1 + 0x1c7);
  dispatch_438027cc(param_1 + 0x1d0);
  dispatch_43802894(param_1 + 0x1d9);
  dispatch_43802410(param_1 + 0x1e2);
  dispatch_43802920(param_1 + 0x1ed);
  dispatch_4380372c(param_1 + 0x1f6);
  dispatch_438028e4(param_1 + 0x1ff);
  dispatch_4380290c(param_1 + 0x208);
  dispatch_43802444(param_1 + 0x211);
  dispatch_43802458(param_1 + 0x21a);
  dispatch_4380299c(param_1 + 0x223);
  dispatch_438029c4(param_1 + 0x22c);
  dispatch_438029d8(param_1 + 0x235);
  dispatch_43802a28(param_1 + 0x23e);
  dispatch_438024dc(param_1 + 0x274);
  dispatch_43802500(param_1 + 0x27e);
  dispatch_43802514(param_1 + 0x287);
  dispatch_43802528(param_1 + 0x290);
  dispatch_43802934(param_1 + 0x299);
  dispatch_43802948(param_1 + 0x2a2);
  dispatch_438029ec(param_1 + 0x2ab);
  dispatch_43802a14(param_1 + 0x2b4);
  dispatch_43802b88(param_1 + 0x2bd);
  dispatch_43802b74(param_1 + 0x2c6);
  dispatch_43802b9c(param_1 + 0x2cf);
  dispatch_43802bf4(param_1 + 0x2d8);
  dispatch_43802c08(param_1 + 0x2e1);
  dispatch_43802c30(param_1 + 0x2ea);
  dispatch_43802cac(param_1 + 0x2f3);
  dispatch_43802cc0(param_1 + 0x2fc);
  dispatch_43802cd4(param_1 + 0x305);
  dispatch_43802e38(param_1 + 0x30e);
  candidate_43802e4c(param_1 + 0x317);
  dispatch_43803a5c(param_1 + 800);
  dispatch_438021dc(param_1 + 0x33d);
  dispatch_43802e74(param_1 + 0x346);
  dispatch_4380368c(param_1 + 0x34f);
  dispatch_43803674(param_1 + 0x358);
  dispatch_438038b8(param_1 + 0x361);
  dispatch_43802e88(param_1 + 0x36a);
  dispatch_43803c94(param_1 + 0x373);
  dispatch_43802ed8(param_1 + 0x37c);
  dispatch_43802ec4(param_1 + 0x385);
  dispatch_43802f14(param_1 + 0x397);
  dispatch_438020d4(param_1 + 0x3a0);
  dispatch_438020f4(param_1 + 0x3a9);
  dispatch_43802db4(param_1 + 0x3b2);
  dispatch_43802f50(param_1 + 0x3bb);
  dispatch_43802f64(param_1 + 0x3c4);
  dispatch_43802f78(param_1 + 0x3cd);
  dispatch_43802f9c(param_1 + 0x3df);
  dispatch_43802eec(param_1 + 0x38e);
  dispatch_4380267c(param_1 + 0x3d6);
  dispatch_4380312c(param_1 + 0x403);
  dispatch_438031d4(param_1 + 0x40c);
  dispatch_438031e8(param_1 + 0x415);
  dispatch_438037d0(param_1 + 0x41e);
  dispatch_43802bb0(param_1 + 0x427);
  dispatch_43803708(param_1 + 0x3f1);
  dispatch_438031fc(param_1 + 0x430);
  dispatch_43803210(param_1 + 0x439);
  dispatch_43803224(param_1 + 0x442);
  dispatch_43802bc4(param_1 + 1099);
  dispatch_43803140(param_1 + 0x454);
  dispatch_43803154(param_1 + 0x45d);
  dispatch_4380337c(param_1 + 0x480);
  dispatch_4380325c(param_1 + 0x46e);
  dispatch_43803270(param_1 + 0x477);
  dispatch_438032c0(param_1 + 0x48c);
  candidate_438032d4(param_1 + 0x495);
  dispatch_438032e8(param_1 + 0x49e);
  dispatch_438032fc(param_1 + 0x4a7);
  dispatch_43803310(param_1 + 0x4b0);
  dispatch_43803324(param_1 + 0x4b9);
  dispatch_4380333c(param_1 + 0x4c2);
  dispatch_43803350(param_1 + 0x4cb);
  dispatch_43803368(param_1 + 0x4d4);
  dispatch_4380353c(param_1 + 0x4dd);
  FUN_43804df4(param_1 + 0x4e6);
  dispatch_438034dc(param_1 + 0x4ef);
  dispatch_438034f0(param_1 + 0x4f8);
  iVar1 = *(int *)(DAT_438052c8 + 0x4380527a);
  if (iVar1 == -1) {
    iVar1 = 0;
  }
  else {
    iVar1 = iVar1 + 1;
  }
  *(int *)(DAT_438052c8 + 0x4380527a) = iVar1;
  pcVar2 = (char *)(DAT_438052cc + 0x43805292);
  *(undefined4 *)((int)&DAT_438057f0 + DAT_438052d0) = *(undefined4 *)(DAT_438052d4 + 0x43805296);
  if (*pcVar2 != '\0') {
    FUN_4356155c(0x53,1);
    FUN_4356155c(0x51,1);
    FUN_4356155c(0x54,1);
    FUN_4356155c(0x52,1);
    *pcVar2 = '\0';
  }
  return 1;
}


/* 438055c0 */

undefined4 dispatch_438055c0(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [20];
  
  uVar2 = FUN_437de2fc();
  iVar1 = DAT_438055fc;
  *(uint *)(DAT_438055f8 + 0x43805b0e) = (uint)*(byte *)(param_1 + 8);
  FUN_43ada220(auStack_24,*(undefined4 *)(iVar1 + 0x438055da + DAT_43805600));
  FUN_439018b0(uVar2,auStack_24,0,0);
  return 1;
}


/* 43809148 */

undefined4 FUN_43809148(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined1 auStack_9c [4];
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined1 auStack_7c [4];
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined1 auStack_5c [4];
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 auStack_19 [5];
  
  auStack_19[0] = 0;
  FUN_439c5a04(&uStack_3c,0,0x20);
  switch(*(undefined2 *)(param_1 + 2)) {
  case 0x3001:
    uStack_38 = 1;
    break;
  default:
    FUN_43787b70(DAT_43809474 + 0x43809442,0x132,DAT_43809478 + 0x43809444,1,
                 *(undefined2 *)(param_1 + 2),0,0);
    return 1;
  case 0x3003:
    uStack_38 = 2;
  case 0x3000:
    FUN_43561420(3,DAT_4380946c,auStack_19);
    FUN_43900e30();
    break;
  case 0x3006:
    uStack_38 = 3;
    goto LAB_4380920a;
  case 0x3007:
    uStack_38 = 4;
    goto LAB_4380920a;
  case 0x300a:
    uStack_38 = 5;
    break;
  case 0x300b:
    uStack_38 = 6;
    break;
  case 0x300c:
    uStack_38 = 7;
LAB_4380920a:
    FUN_43561420(3,DAT_4380946c,auStack_19);
    break;
  case 0x300e:
    uStack_38 = 8;
    break;
  case 0x3010:
    uStack_38 = 9;
    iVar2 = FUN_43804de8();
    *(bool *)(iVar2 + 0x40a) = *(char *)(param_1 + 8) != '\0';
    uStack_2c = CONCAT31(uStack_2c._1_3_,*(undefined1 *)(param_1 + 9));
    break;
  case 0x3011:
    uVar3 = *(undefined4 *)(param_1 + 4);
    FUN_439c5a04(auStack_5c,0,0x20);
    uStack_58 = 0x8202;
    uStack_54 = uVar3;
    uStack_50 = param_2;
    uVar3 = FUN_43806ef0();
    FUN_438090e0(uVar3,DAT_43809470,auStack_5c,0x20);
    uStack_38 = 0x100;
    goto LAB_4380942a;
  case 0x3012:
    uStack_38 = 0x101;
    break;
  case 0x3013:
    uStack_38 = 0x102;
    goto LAB_4380942a;
  case 0x3014:
    uVar5 = *(undefined4 *)(param_1 + 4);
    uVar3 = *(undefined4 *)(param_1 + 8);
    FUN_439c5a04(auStack_7c,0,0x20);
    uStack_78 = 0x8204;
    uStack_74 = uVar5;
    uStack_70 = param_2;
    uStack_6c = uVar3;
    uVar3 = FUN_43806ef0();
    FUN_438090e0(uVar3,DAT_43809470,auStack_7c,0x20);
    uStack_38 = 0x104;
    goto LAB_4380942a;
  case 0x3015:
    uVar3 = *(undefined4 *)(param_1 + 4);
    FUN_439c5a04(auStack_9c,0,0x20);
    uStack_98 = 0x8201;
    uStack_94 = uVar3;
    uStack_90 = param_2;
    uVar3 = FUN_43806ef0();
    FUN_438090e0(uVar3,DAT_43809470,auStack_9c,0x20);
    uStack_38 = 0x103;
    break;
  case 0x3016:
    uStack_38 = 10;
    break;
  case 0x3017:
    uStack_38 = 0xb;
    break;
  case 0x3018:
    uStack_38 = 0xc;
    break;
  case 0x3019:
    uStack_2c = *(undefined4 *)(param_1 + 8);
    uStack_28 = *(undefined1 *)(param_1 + 0xc);
    uStack_27 = *(undefined1 *)(param_1 + 0xd);
    uStack_38 = 0xd;
    iVar2 = FUN_43804de8();
    *(undefined1 *)(iVar2 + 0x4cc) = 1;
    break;
  case 0x301a:
    uStack_38 = 0x11;
    break;
  case 0x301b:
  case 0x3022:
    uStack_38 = 0xe;
    break;
  case 0x301c:
    uStack_38 = 0x8100;
    break;
  case 0x301e:
    uStack_38 = 0xf;
    break;
  case 0x301f:
    uStack_38 = 0x10;
    break;
  case 0x3020:
    break;
  case 0x3021:
    uStack_38 = 2;
    break;
  case 0x3023:
    uVar4 = (uint)*(byte *)(param_1 + 8);
    if (uVar4 == 0) {
      uStack_38 = 0x13;
    }
    else {
      uStack_38 = 0x12;
      iVar2 = FUN_43804de8();
      *(uint *)(iVar2 + 0x450) = uVar4;
      iVar2 = FUN_43804de8();
      *(undefined2 *)(iVar2 + 0x454) = *(undefined2 *)(param_1 + 10);
      iVar2 = FUN_43804de8();
      *(undefined2 *)(iVar2 + 0x456) = *(undefined2 *)(param_1 + 0xc);
      iVar2 = FUN_43804de8();
      *(uint *)(iVar2 + 0x458) = (uint)*(byte *)(param_1 + 0xe);
      if (uVar4 == 4) {
        iVar2 = FUN_4378f9b4();
        if (*(char *)(*(int *)(iVar2 + 0x28) + 0x46) == '\x01') {
          iVar2 = FUN_43804de8();
          *(undefined4 *)(iVar2 + 0x450) = 1;
          iVar2 = FUN_43804de8();
          iVar1 = FUN_4378f9b4();
          *(undefined2 *)(iVar2 + 0x454) = *(undefined2 *)(*(int *)(iVar1 + 0x28) + 0x80);
          iVar2 = FUN_43804de8();
          iVar1 = FUN_4378f9b4();
          *(undefined2 *)(iVar2 + 0x456) = *(undefined2 *)(*(int *)(iVar1 + 0x28) + 0x82);
        }
        else {
          iVar2 = FUN_43804de8();
          *(undefined4 *)(iVar2 + 0x450) = 3;
          iVar2 = FUN_43804de8();
          *(undefined2 *)(iVar2 + 0x454) = 0x140;
          iVar2 = FUN_43804de8();
          *(undefined2 *)(iVar2 + 0x456) = 0xf0;
        }
      }
    }
    break;
  case 0x3024:
    uStack_2c = CONCAT31(uStack_2c._1_3_,*(undefined1 *)(param_1 + 8));
    uStack_38 = 0x8102;
    break;
  case 0x3026:
    uStack_38 = 0x14;
    break;
  case 0x3027:
    uStack_2c = CONCAT31(uStack_2c._1_3_,*(undefined1 *)(param_1 + 8));
    uStack_38 = 0x15;
    break;
  case 0x3028:
    uStack_38 = 0x16;
    break;
  case 0x3029:
    uStack_38 = 0x17;
    iVar2 = FUN_43804de8();
    *(undefined1 *)(iVar2 + 0xd0) = *(undefined1 *)(param_1 + 8);
    iVar2 = FUN_43804de8();
    *(undefined2 *)(iVar2 + 0xd2) = *(undefined2 *)(param_1 + 10);
    break;
  case 0x302a:
    if (*(char *)(param_1 + 8) == '\x01') {
      uStack_38 = 0x18;
    }
    else {
      uStack_38 = 0x19;
    }
    break;
  case 0x302b:
    uStack_38 = 0x8301;
    goto LAB_4380942a;
  case 0x302c:
    uStack_38 = 0x8302;
    goto LAB_4380942a;
  case 0x302d:
    uStack_38 = 0x8304;
    break;
  case 0x302e:
    uStack_38 = 0x8305;
    break;
  case 0x302f:
    uStack_38 = 0x8306;
    break;
  case 0x3030:
    uStack_38 = 0x8203;
LAB_4380942a:
    uStack_2c = *(undefined4 *)(param_1 + 8);
    break;
  case 0x3031:
    uStack_38 = 0x1a;
    break;
  case 0x3032:
    uStack_38 = 0x1b;
    break;
  case 0x3033:
    uStack_38 = 0x1c;
    break;
  case 0x3034:
    uStack_38 = 0x8307;
  }
  uStack_34 = *(undefined4 *)(param_1 + 4);
  uStack_3c = 0;
  uStack_30 = param_2;
  uVar3 = FUN_43806ef0();
  FUN_438090e0(uVar3,DAT_43809470,&uStack_3c,0x20);
  return 0;
}


/* 438149dc */

void FUN_438149dc(int param_1,undefined4 param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  *(undefined4 *)(param_1 + 0x458) = param_2;
  *(undefined1 *)(param_1 + 0x464) = 1;
  uVar1 = param_3[1];
  uVar2 = param_3[2];
  uVar3 = param_3[3];
  iVar5 = DAT_43814a9c + 0x43814a00;
  *(undefined4 *)(param_1 + 0x468) = *param_3;
  *(undefined4 *)(param_1 + 0x46c) = uVar1;
  *(undefined4 *)(param_1 + 0x470) = uVar2;
  *(undefined4 *)(param_1 + 0x474) = uVar3;
  iVar4 = DAT_43814aa0;
  uVar1 = param_3[5];
  *(undefined4 *)(param_1 + 0x478) = param_3[4];
  *(undefined4 *)(param_1 + 0x47c) = uVar1;
  if ((*(byte *)(*(int *)(iVar5 + iVar4) + 0x1a) & 0x10) != 0) {
    iVar4 = DAT_43814aa4 + 0x43814a26;
    FUN_438146dc(3,9,1,DAT_43814aa8 + 0x43814a58,iVar4,param_2,*(undefined2 *)(param_1 + 0x470),
                 *(undefined4 *)(param_1 + 0x46c),*(undefined4 *)(param_1 + 0x468),
                 *(undefined2 *)(param_1 + 0x478),*(undefined2 *)(param_1 + 0x47a),
                 *(undefined2 *)(param_1 + 0x472),*(undefined2 *)(param_1 + 0x474),
                 *(undefined2 *)(param_1 + 0x476));
    FUN_43902718(DAT_43814aac + 0x43814a6c,iVar4,*(undefined4 *)(param_1 + 0x458),
                 *(undefined2 *)(param_1 + 0x470),*(undefined4 *)(param_1 + 0x46c),
                 *(undefined4 *)(param_1 + 0x468),*(undefined2 *)(param_1 + 0x478),
                 *(undefined2 *)(param_1 + 0x47a),*(undefined2 *)(param_1 + 0x472),
                 *(undefined2 *)(param_1 + 0x474),*(undefined2 *)(param_1 + 0x476));
  }
  return;
}


/* 4387a30c */

undefined4 FUN_4387a30c(int param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  uVar3 = FUN_4387b7c4();
  iVar5 = DAT_4387a344 + 0x4387a31e;
  FUN_436bf848(param_2,uVar3);
  if ((*(byte *)(*(int *)(iVar5 + DAT_4387a348) + 1) & 0x42) != 0) {
    thunk_FUN_4387a2d0(uVar3);
  }
  iVar5 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar5);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar5);
  if (iVar2 != param_1) {
    return 4;
  }
  iVar2 = iVar5 * 0xac + DAT_436be518 + 0x436be436;
  FUN_439c5320(iVar2,uVar3);
  cVar1 = *(char *)(DAT_436be51c + 0x436be444 + iVar5);
  if (cVar1 == '\0') {
    *(undefined4 *)(iVar2 + 0x58) = 0;
  }
  iVar2 = *(int *)(DAT_436be520 + 0x436be44e + iVar5 * 4);
  if (iVar2 - 0xcU < 5) {
    if (cVar1 == '\0') {
      iVar2 = iVar5 * 0xac + DAT_436be524 + 0x436be46c;
      *(undefined4 *)(iVar2 + 0x38) = 1;
    }
    else {
      if (cVar1 != '\x01') {
        iVar2 = iVar5 * 0xac + DAT_436be52c + 0x436be48c;
        *(undefined4 *)(iVar2 + 0x38) = 0;
        *(undefined4 *)(iVar2 + 0x30) = 1;
        goto LAB_436be4d4;
      }
      iVar2 = iVar5 * 0xac + DAT_436be528 + 0x436be47c;
      *(undefined4 *)(iVar2 + 0x38) = 0;
    }
    *(undefined4 *)(iVar2 + 0x30) = 0;
  }
  else {
    if (cVar1 == '\0') {
      iVar4 = iVar5 * 0xac + DAT_436be530 + 0x436be4a0;
      *(undefined4 *)(iVar4 + 0x30) = 0;
      *(undefined4 *)(iVar4 + 0x38) = 1;
    }
    else {
      iVar4 = iVar5 * 0xac + DAT_436be534 + 0x436be4b2;
      *(undefined4 *)(iVar4 + 0x38) = 0;
      *(undefined4 *)(iVar4 + 0x30) = 0;
    }
    if ((iVar2 == 0x11) && (*(char *)(DAT_436be538 + 0x436be4c2 + iVar5) == '\0')) {
      *(undefined4 *)((int)&DAT_436be538 + iVar5 * 0xac + DAT_436be53c) = 0x438;
    }
  }
LAB_436be4d4:
  iVar2 = *(int *)(DAT_436be540 + 0x436be4de + iVar5 * 0xac);
  if (iVar2 == 7) {
    *(undefined4 *)(DAT_436be544 + 0x436be4ea + iVar5 * 4) = 0;
  }
  else {
    *(undefined4 *)(DAT_436be548 + 0x436be4f6 + iVar5 * 4) = 1;
    if (iVar2 == 0) {
      *(undefined4 *)(DAT_436be54c + 0x436be500 + iVar5 * 4) = 1;
      return 0;
    }
  }
  *(undefined4 *)(DAT_436be550 + 0x436be50c + iVar5 * 4) = 0;
  return 0;
}


/* 4387a6c4 */

void FUN_4387a6c4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  uStack_8 = param_3;
  if (*(uint *)(DAT_4387a6f4 + 0x4387a6cc) < 4) {
                    /* WARNING: Could not recover jumptable at 0x4387a6d0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uStack_c = param_2;
    (*(code *)(&switchD_4387a6d0::switchdataD_4387a6d4 +
              (uint)(&switchD_4387a6d0::switchdataD_4387a6d4)[*(uint *)(DAT_4387a6f4 + 0x4387a6cc)]
              * 2))();
    return;
  }
  uStack_c = 6;
  FUN_436bec28(param_1,&uStack_c,param_3,6,param_1);
  return;
}


/* 4387a758 */

void FUN_4387a758(undefined4 *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  ushort uVar2;
  char cVar3;
  int iVar4;
  undefined1 uVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 *puVar8;
  undefined4 *puVar9;
  undefined1 *puVar10;
  undefined4 *puVar11;
  undefined4 uVar12;
  undefined1 *puVar13;
  int *piVar14;
  int iVar15;
  int iVar16;
  undefined4 uVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  
  iVar20 = 0;
  puVar9 = (undefined4 *)(DAT_4387b110 + 0x4387a770);
  uVar6 = *(undefined2 *)(param_1 + 2);
  iVar16 = DAT_4387b118 + 0x4387a77c;
  *(undefined4 *)(DAT_4387b114 + 0x4387a774) = *puVar9;
  puVar11 = (undefined4 *)(DAT_4387b11c + 0x4387a788);
  *(undefined4 *)(DAT_4387b120 + 0x4387a78a) = *puVar11;
  uVar17 = *param_1;
  *(undefined4 *)(DAT_4387b124 + 0x4387a796) = uVar17;
  iVar15 = DAT_4387b128;
  *(undefined2 *)(DAT_4387b128 + 0x4387a79e) = uVar6;
  *(undefined2 *)(iVar15 + 0x4387a7a0) = *(undefined2 *)((int)param_1 + 10);
  uVar5 = *(undefined1 *)(param_1 + 8);
  *puVar9 = param_1[3];
  *(undefined4 *)(DAT_4387b12c + 0x4387a7b4) = param_1[4];
  *(undefined2 *)(DAT_4387b130 + 0x4387a7be) = *(undefined2 *)((int)param_1 + 0x16);
  uVar6 = *(undefined2 *)(param_1 + 6);
  *(undefined2 *)(DAT_4387b134 + 0x4387a7c8) = uVar6;
  *(undefined1 *)(DAT_4387b138 + 0x4387a7d0) = uVar5;
  *(undefined1 *)(DAT_4387b13c + 0x4387a7dc) = *(undefined1 *)((int)param_1 + 0x21);
  iVar18 = param_1[0xb];
  *puVar11 = param_1[9];
  *(undefined1 *)(DAT_4387b140 + 0x4387a7ee) = *(undefined1 *)(param_1 + 10);
  uVar7 = param_1[0xc];
  uVar5 = *(undefined1 *)(param_1 + 0xd);
  *(int *)(DAT_4387b144 + 0x4387a7f8) = iVar18;
  *(undefined4 *)(DAT_4387b148 + 0x4387a804) = uVar7;
  *(undefined1 *)(DAT_4387b14c + 0x4387a80c) = uVar5;
  *(undefined1 *)(DAT_4387b150 + 0x4387a81a) = *(undefined1 *)((int)param_1 + 0x35);
  *(undefined4 *)(DAT_4387b154 + 0x4387a824) = param_1[0xe];
  iVar15 = DAT_4387b158;
  *(undefined2 *)(DAT_4387b158 + 0x4387a82c) = uVar6;
  *(undefined1 *)(iVar15 + 0x4387a82e) = *(undefined1 *)(param_1 + 0xf);
  do {
    iVar4 = DAT_4387b15c;
    iVar15 = iVar20 + 0x40;
    uVar7 = *(undefined4 *)((int)param_1 + iVar20 + 0x44);
    uVar12 = *(undefined4 *)((int)param_1 + iVar20 + 0x48);
    iVar19 = DAT_4387b15c + iVar20;
    iVar20 = iVar20 + 0xc;
    *(undefined4 *)(iVar19 + 0x4387a844) = *(undefined4 *)((int)param_1 + iVar15);
    *(undefined4 *)(iVar19 + 0x4387a848) = uVar7;
    *(undefined4 *)(iVar19 + 0x4387a84c) = uVar12;
  } while (iVar20 != 0x60);
  uVar6 = *(undefined2 *)(param_1 + 0x28);
  *(undefined1 *)(iVar4 + 0x4387a8b0) = uVar5;
  *(undefined2 *)(iVar4 + 0x4387a8a4) = uVar6;
  uVar7 = param_1[0x2a];
  *(undefined4 *)(iVar4 + 0x4387a8a8) = param_1[0x29];
  *(undefined4 *)(iVar4 + 0x4387a8ac) = uVar7;
  bVar1 = **(byte **)(iVar16 + DAT_4387b160);
  if ((bVar1 & 2) != 0) {
    *(ushort *)(DAT_4387b16c + 0x4387a896) =
         (ushort)**(byte **)(iVar16 + DAT_4387b164) * 0x100 +
         (ushort)**(byte **)(iVar16 + DAT_4387b168);
  }
  if ((bVar1 & 1) != 0) {
    *(ushort *)(DAT_4387b178 + 0x4387a8b8) =
         (ushort)**(byte **)(iVar16 + DAT_4387b170) * 0x100 +
         (ushort)**(byte **)(iVar16 + DAT_4387b174);
  }
  if ((bVar1 & 0x10) != 0) {
    *(byte *)(DAT_4387b17c + 0x4387a8d4) = (byte)(((uint)bVar1 << 0x1a) >> 0x1f);
  }
  if ((bVar1 & 0x40) != 0) {
    *(byte *)(DAT_4387b180 + 0x4387a8e6) = bVar1 >> 7;
  }
  if ((bVar1 & 4) != 0) {
    *(byte *)(DAT_4387b184 + 0x4387a8fa) = (byte)(((uint)bVar1 << 0x1c) >> 0x1f);
  }
  if ((**(byte **)(iVar16 + DAT_4387b188) & 8) != 0) {
    *(undefined1 *)(DAT_4387b18c + 0x4387a914) = 0;
    *(undefined4 *)(DAT_4387b190 + 0x4387a91e) = 1;
  }
  iVar15 = DAT_4387b1a0;
  puVar8 = (undefined1 *)(DAT_4387b194 + 0x4387a932);
  puVar10 = (undefined1 *)(DAT_4387b198 + 0x4387a938);
  puVar13 = (undefined1 *)(DAT_4387b19c + 0x4387a93a);
  *puVar8 = 0;
  *puVar10 = 0;
  *puVar13 = 0;
  *(undefined1 *)(iVar15 + 0x4387a940) = 0;
  iVar20 = DAT_4387b1a8;
  if (iVar18 == 0) {
    *puVar8 = 1;
    piVar14 = (int *)(DAT_4387b1a4 + 0x4387a958);
LAB_4387a984:
    *piVar14 = iVar18;
  }
  else {
    if (iVar18 == 1) {
      *puVar10 = 1;
      piVar14 = (int *)(iVar20 + 0x4387a966);
      goto LAB_4387a984;
    }
    if (iVar18 == 2) {
      *puVar13 = 1;
      piVar14 = (int *)(DAT_4387b1ac + 0x4387a976);
      goto LAB_4387a984;
    }
    if (iVar18 == 3) {
      *(undefined1 *)(iVar15 + 0x4387a940) = 1;
      piVar14 = (int *)(DAT_4387b1b0 + 0x4387a986);
      goto LAB_4387a984;
    }
  }
  uVar7 = FUN_4387a4f4();
  piVar14 = (int *)(DAT_4387b1b4 + 0x4387a996);
  FUN_43acb946(uVar17,uVar7,DAT_4387b1b8 + 0x4387a99a,piVar14,param_4);
  iVar15 = *piVar14;
  if ((iVar15 == 0) || (iVar15 == 0x11)) {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1bc + 0x4387a9b2);
  }
  else {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b1c0 + 0x4387a9bc);
  }
  *puVar8 = uVar5;
  if ((((((iVar15 == 1) || (iVar15 == 9)) || (iVar15 == 2)) || ((iVar15 == 3 || (iVar15 == 6)))) ||
      (iVar15 == 7)) ||
     (((iVar15 == 8 || (iVar15 == 10)) ||
      ((iVar15 == 0xb || (((iVar15 == 0xc || (iVar15 == 0xd)) || (iVar15 == 0xe)))))))) {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1c4 + 0x4387a9f6);
  }
  else {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b1c8 + 0x4387aa00);
  }
  *puVar8 = uVar5;
  if (((iVar15 - 4U < 2) || (iVar15 == 0xf)) || (iVar15 == 0x10)) {
    puVar8 = (undefined1 *)(DAT_4387b1cc + 0x4387aa16);
LAB_4387aa2e:
    uVar5 = 1;
  }
  else {
    if ((iVar15 == 1) || (iVar15 == 9)) {
      if (*(int *)(param_2[2] + 0x1c) - 2U < 2) {
        puVar8 = (undefined1 *)(DAT_4387b1d0 + 0x4387aa30);
        goto LAB_4387aa2e;
      }
      puVar8 = (undefined1 *)(DAT_4387b1d4 + 0x4387aa3a);
    }
    else {
      puVar8 = (undefined1 *)(DAT_4387b1d8 + 0x4387aa42);
    }
    uVar5 = 0;
  }
  *puVar8 = uVar5;
  if (iVar15 - 0xcU < 3) {
    *(undefined1 *)(DAT_4387b1dc + 0x4387aa56) = 1;
LAB_4387aa6a:
    if (((iVar15 == 2) || (iVar15 == 3)) || (iVar15 == 0xb)) goto LAB_4387aa76;
    *(undefined1 *)(DAT_4387b1e8 + 0x4387aa90) = 0;
LAB_4387aa9c:
    *(undefined1 *)(DAT_4387b1f0 + 0x4387aaa8) = 0;
    if (iVar15 != 0xd) goto LAB_4387aab6;
    *(undefined1 *)(DAT_4387b1f4 + 0x4387aab4) = 1;
LAB_4387aada:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b200 + 0x4387aae4);
  }
  else {
    *(undefined1 *)(DAT_4387b1e0 + 0x4387aa64) = 0;
    if ((iVar15 != 1) && (iVar15 != 9)) goto LAB_4387aa6a;
LAB_4387aa76:
    *(undefined1 *)(DAT_4387b1e4 + 0x4387aa82) = 1;
    if (iVar15 != 2) goto LAB_4387aa9c;
    *(undefined1 *)(DAT_4387b1ec + 0x4387aa9a) = 1;
LAB_4387aab6:
    *(undefined1 *)(DAT_4387b1f8 + 0x4387aac2) = 0;
    if (((iVar15 != 9) && (iVar15 != 1)) && ((iVar15 != 7 && (iVar15 != 8)))) goto LAB_4387aada;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b1fc + 0x4387aada);
  }
  *puVar8 = uVar5;
  if (iVar15 == 0xc) {
    *(undefined1 *)(DAT_4387b204 + 0x4387aaf2) = 1;
LAB_4387ab0c:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b210 + 0x4387ab16);
  }
  else {
    *(undefined1 *)(DAT_4387b208 + 0x4387ab00) = 0;
    if (iVar15 != 6) goto LAB_4387ab0c;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b20c + 0x4387ab0c);
  }
  *puVar8 = uVar5;
  if ((*(char *)(DAT_4387b214 + 0x4387ab1e) == '\0') &&
     ((*(char *)(DAT_4387b218 + 0x4387ab28) == '\0' ||
      (*(char *)(DAT_4387b21c + 0x4387ab32) == '\0')))) {
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b224 + 0x4387ab48);
  }
  else {
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b220 + 0x4387ab3e);
  }
  *puVar8 = uVar5;
  iVar15 = *(int *)(DAT_4387b228 + 0x4387ab50);
  if (iVar15 == 1) {
    *(undefined1 *)(DAT_4387b22c + 0x4387ab5c) = 1;
LAB_4387ab76:
    uVar5 = 0;
    puVar8 = (undefined1 *)(DAT_4387b238 + 0x4387ab80);
  }
  else {
    *(undefined1 *)(DAT_4387b230 + 0x4387ab6a) = 0;
    if (iVar15 != 2) goto LAB_4387ab76;
    uVar5 = 1;
    puVar8 = (undefined1 *)(DAT_4387b234 + 0x4387ab76);
  }
  *puVar8 = uVar5;
  if ((*(int *)(DAT_4387b23c + 0x4387ab88) == 1) && (*(char *)(DAT_4387b240 + 0x4387ab94) == '\0'))
  {
    *(undefined1 *)(DAT_4387b244 + 0x4387ab9e) = 1;
  }
  else {
    *(undefined1 *)(DAT_4387b248 + 0x4387abaa) = 0;
  }
  uVar7 = FUN_4387a468(param_2);
  iVar20 = param_2[2];
  uVar17 = *(undefined4 *)(param_2[1] + 0x10);
  iVar18 = *param_2;
  cVar3 = *(char *)(iVar20 + 0x29a);
  *(undefined4 *)(DAT_4387b24c + 0x4387abbe) = uVar17;
  *(char *)(DAT_4387b250 + 0x4387abcc) = cVar3;
  iVar15 = DAT_4387b3dc;
  uVar2 = *(ushort *)(iVar18 + 0xc);
  if (uVar2 == 0x708) {
    uVar7 = 2;
    puVar9 = (undefined4 *)(DAT_4387b260 + 0x4387ac2a);
    goto LAB_4387b06a;
  }
  if (0x708 < uVar2) {
    if (uVar2 == 0x714) goto LAB_4387abfa;
    if (uVar2 != 0x715) goto LAB_4387b064;
    if (*(int *)(iVar18 + 0x450) - 1U < 2) {
      uVar7 = 0;
      puVar9 = (undefined4 *)(DAT_4387b258 + 0x4387ac16);
      goto LAB_4387b06a;
    }
    puVar9 = (undefined4 *)(DAT_4387b25c + 0x4387ac1e);
LAB_4387ac1c:
    uVar7 = 1;
    goto LAB_4387b06a;
  }
  if (uVar2 == 0x702) {
LAB_4387abfa:
    puVar9 = (undefined4 *)(DAT_4387b254 + 0x4387ac02);
    goto LAB_4387ac1c;
  }
  if (uVar2 != 0x707) {
LAB_4387b064:
    uVar7 = 0x56;
    puVar9 = (undefined4 *)(DAT_4387b3d8 + 0x4387b06c);
    goto LAB_4387b06a;
  }
  switch(*(undefined4 *)(iVar20 + 0x1c)) {
  case 0:
    if (*(char *)(iVar20 + 0x24) == '\0') {
      switch(uVar17) {
      case 0:
      case 1:
        if (cVar3 == '\0') {
          switch(uVar7) {
          case 0:
            uVar7 = 0x24;
            puVar9 = (undefined4 *)(DAT_4387b31c + 0x4387ae9a);
            break;
          case 1:
            uVar7 = 0x25;
            puVar9 = (undefined4 *)(DAT_4387b320 + 0x4387aea4);
            break;
          case 2:
            uVar7 = 0x26;
            puVar9 = (undefined4 *)(DAT_4387b324 + 0x4387aeae);
            break;
          case 3:
            uVar7 = 0x27;
            puVar9 = (undefined4 *)(DAT_4387b328 + 0x4387aeb8);
            break;
          case 4:
            uVar7 = 0x28;
            puVar9 = (undefined4 *)(DAT_4387b32c + 0x4387aec2);
            break;
          case 5:
            uVar7 = 0x29;
            puVar9 = (undefined4 *)(DAT_4387b330 + 0x4387aecc);
            break;
          case 6:
            uVar7 = 0x2a;
            puVar9 = (undefined4 *)(DAT_4387b334 + 0x4387aed6);
            break;
          case 7:
            puVar9 = (undefined4 *)(DAT_4387b338 + 0x4387aede);
            goto LAB_4387aee4;
          default:
            puVar9 = (undefined4 *)(DAT_4387b33c + 0x4387aee6);
LAB_4387aee4:
            uVar7 = 0x2b;
          }
          goto LAB_4387b06a;
        }
        switch(uVar7) {
        case 0:
          uVar7 = 0x2c;
          puVar9 = (undefined4 *)(DAT_4387b2f8 + 0x4387ae32);
          break;
        case 1:
          uVar7 = 0x2d;
          puVar9 = (undefined4 *)(DAT_4387b2fc + 0x4387ae3c);
          break;
        case 2:
          uVar7 = 0x2e;
          puVar9 = (undefined4 *)(DAT_4387b300 + 0x4387ae46);
          break;
        case 3:
          uVar7 = 0x2f;
          puVar9 = (undefined4 *)(DAT_4387b304 + 0x4387ae50);
          break;
        case 4:
          uVar7 = 0x30;
          puVar9 = (undefined4 *)(DAT_4387b308 + 0x4387ae5a);
          break;
        case 5:
          uVar7 = 0x31;
          puVar9 = (undefined4 *)(DAT_4387b30c + 0x4387ae64);
          break;
        case 6:
          uVar7 = 0x32;
          puVar9 = (undefined4 *)(DAT_4387b310 + 0x4387ae6e);
          break;
        case 7:
          puVar9 = (undefined4 *)(DAT_4387b314 + 0x4387ae76);
          goto LAB_4387ae7c;
        default:
          puVar9 = (undefined4 *)(DAT_4387b318 + 0x4387ae7e);
LAB_4387ae7c:
          uVar7 = 0x33;
        }
        goto LAB_4387b06a;
      case 2:
      case 3:
        goto switchD_4387aeec_switchD;
      default:
        uVar7 = 0x3c;
        puVar9 = (undefined4 *)(DAT_4387b364 + 0x4387af5a);
        goto LAB_4387b06a;
      }
    }
    switch(uVar17) {
    case 0:
    case 1:
      if (cVar3 == '\0') {
        switch(uVar7) {
        case 0:
          uVar7 = 0xb;
          puVar9 = (undefined4 *)(DAT_4387b2ac + 0x4387ad46);
          break;
        case 1:
          uVar7 = 0xc;
          puVar9 = (undefined4 *)(DAT_4387b2b0 + 0x4387ad50);
          break;
        case 2:
          uVar7 = 0xd;
          puVar9 = (undefined4 *)(DAT_4387b2b4 + 0x4387ad5a);
          break;
        case 3:
          uVar7 = 0xe;
          puVar9 = (undefined4 *)(DAT_4387b2b8 + 0x4387ad64);
          break;
        case 4:
          uVar7 = 0xf;
          puVar9 = (undefined4 *)(DAT_4387b2bc + 0x4387ad6e);
          break;
        case 5:
          uVar7 = 0x10;
          puVar9 = (undefined4 *)(DAT_4387b2c0 + 0x4387ad78);
          break;
        case 6:
          uVar7 = 0x11;
          puVar9 = (undefined4 *)(DAT_4387b2c4 + 0x4387ad82);
          break;
        case 7:
          puVar9 = (undefined4 *)(DAT_4387b2c8 + 0x4387ad8a);
          goto LAB_4387ad90;
        default:
          puVar9 = (undefined4 *)(DAT_4387b2cc + 0x4387ad92);
LAB_4387ad90:
          uVar7 = 0x12;
        }
        goto LAB_4387b06a;
      }
      switch(uVar7) {
      case 0:
        uVar7 = 0x13;
        puVar9 = (undefined4 *)(DAT_4387b288 + 0x4387acde);
        break;
      case 1:
        uVar7 = 0x14;
        puVar9 = (undefined4 *)(DAT_4387b28c + 0x4387ace8);
        break;
      case 2:
        uVar7 = 0x15;
        puVar9 = (undefined4 *)(DAT_4387b290 + 0x4387acf2);
        break;
      case 3:
        uVar7 = 0x16;
        puVar9 = (undefined4 *)(DAT_4387b294 + 0x4387acfc);
        break;
      case 4:
        uVar7 = 0x17;
        puVar9 = (undefined4 *)(DAT_4387b298 + 0x4387ad06);
        break;
      case 5:
        uVar7 = 0x18;
        puVar9 = (undefined4 *)(DAT_4387b29c + 0x4387ad10);
        break;
      case 6:
        uVar7 = 0x19;
        puVar9 = (undefined4 *)(DAT_4387b2a0 + 0x4387ad1a);
        break;
      case 7:
        puVar9 = (undefined4 *)(DAT_4387b2a4 + 0x4387ad22);
        goto LAB_4387ad28;
      default:
        puVar9 = (undefined4 *)(DAT_4387b2a8 + 0x4387ad2a);
LAB_4387ad28:
        uVar7 = 0x1a;
      }
      goto LAB_4387b06a;
    case 2:
    case 3:
      goto switchD_4387ad98_switchD;
    default:
      uVar7 = 0x23;
      puVar9 = (undefined4 *)(DAT_4387b2f4 + 0x4387ae06);
      goto LAB_4387b06a;
    }
  case 1:
    goto switchD_4387af5e_switchD;
  case 2:
    switch(uVar7) {
    case 0:
      uVar7 = 0x4d;
      puVar9 = (undefined4 *)(DAT_4387b38c + 0x4387afc8);
      break;
    case 1:
      uVar7 = 0x4e;
      puVar9 = (undefined4 *)(DAT_4387b390 + 0x4387afd0);
      break;
    case 2:
      uVar7 = 0x4f;
      puVar9 = (undefined4 *)(DAT_4387b394 + 0x4387afd8);
      break;
    case 3:
      uVar7 = 0x50;
      puVar9 = (undefined4 *)(DAT_4387b398 + 0x4387afe0);
      break;
    case 4:
      uVar7 = 0x51;
      puVar9 = (undefined4 *)(DAT_4387b39c + 0x4387afe8);
      break;
    case 5:
      uVar7 = 0x52;
      puVar9 = (undefined4 *)(DAT_4387b3a0 + 0x4387aff0);
      break;
    case 6:
      uVar7 = 0x53;
      puVar9 = (undefined4 *)(DAT_4387b3a4 + 0x4387aff8);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b3a8 + 0x4387affe);
      goto LAB_4387b002;
    default:
      puVar9 = (undefined4 *)(DAT_4387b3ac + 0x4387b004);
LAB_4387b002:
      uVar7 = 0x54;
    }
    goto LAB_4387b06a;
  case 3:
    switch(uVar7) {
    case 0:
      uVar7 = 0x45;
      puVar9 = (undefined4 *)(DAT_4387b3b0 + 0x4387b01e);
      break;
    case 1:
      uVar7 = 0x46;
      puVar9 = (undefined4 *)(DAT_4387b3b4 + 0x4387b026);
      break;
    case 2:
      uVar7 = 0x47;
      puVar9 = (undefined4 *)(DAT_4387b3b8 + 0x4387b02e);
      break;
    case 3:
      uVar7 = 0x48;
      puVar9 = (undefined4 *)(DAT_4387b3bc + 0x4387b036);
      break;
    case 4:
      uVar7 = 0x49;
      puVar9 = (undefined4 *)(DAT_4387b3c0 + 0x4387b03e);
      break;
    case 5:
      uVar7 = 0x4a;
      puVar9 = (undefined4 *)(DAT_4387b3c4 + 0x4387b046);
      break;
    case 6:
      uVar7 = 0x4b;
      puVar9 = (undefined4 *)(DAT_4387b3c8 + 0x4387b04e);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b3cc + 0x4387b054);
      goto LAB_4387b058;
    default:
      puVar9 = (undefined4 *)(DAT_4387b3d0 + 0x4387b05a);
LAB_4387b058:
      uVar7 = 0x4c;
    }
    goto LAB_4387b06a;
  case 4:
    switch(uVar7) {
    case 0:
      uVar7 = 3;
      puVar9 = (undefined4 *)(DAT_4387b264 + 0x4387ac5a);
      break;
    case 1:
      uVar7 = 4;
      puVar9 = (undefined4 *)(DAT_4387b268 + 0x4387ac64);
      break;
    case 2:
      uVar7 = 5;
      puVar9 = (undefined4 *)(DAT_4387b26c + 0x4387ac6e);
      break;
    case 3:
      uVar7 = 6;
      puVar9 = (undefined4 *)(DAT_4387b270 + 0x4387ac78);
      break;
    case 4:
      uVar7 = 7;
      puVar9 = (undefined4 *)(DAT_4387b274 + 0x4387ac82);
      break;
    case 5:
      uVar7 = 8;
      puVar9 = (undefined4 *)(DAT_4387b278 + 0x4387ac8c);
      break;
    case 6:
      uVar7 = 9;
      puVar9 = (undefined4 *)(DAT_4387b27c + 0x4387ac96);
      break;
    case 7:
      puVar9 = (undefined4 *)(DAT_4387b280 + 0x4387ac9e);
      goto LAB_4387aca4;
    default:
      puVar9 = (undefined4 *)(DAT_4387b284 + 0x4387aca6);
LAB_4387aca4:
      uVar7 = 10;
    }
    goto LAB_4387b06a;
  default:
    uVar7 = 0x55;
    puVar9 = (undefined4 *)(DAT_4387b3d4 + 0x4387b064);
    goto LAB_4387b06a;
  }
switchD_4387aeec_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x34;
    puVar9 = (undefined4 *)(DAT_4387b340 + 0x4387af02);
    break;
  case 1:
    uVar7 = 0x35;
    puVar9 = (undefined4 *)(DAT_4387b344 + 0x4387af0c);
    break;
  case 2:
    uVar7 = 0x36;
    puVar9 = (undefined4 *)(DAT_4387b348 + 0x4387af16);
    break;
  case 3:
    uVar7 = 0x37;
    puVar9 = (undefined4 *)(DAT_4387b34c + 0x4387af20);
    break;
  case 4:
    uVar7 = 0x38;
    puVar9 = (undefined4 *)(DAT_4387b350 + 0x4387af2a);
    break;
  case 5:
    uVar7 = 0x39;
    puVar9 = (undefined4 *)(DAT_4387b354 + 0x4387af34);
    break;
  case 6:
    uVar7 = 0x3a;
    puVar9 = (undefined4 *)(DAT_4387b358 + 0x4387af3e);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b35c + 0x4387af46);
    goto LAB_4387af4c;
  default:
    puVar9 = (undefined4 *)(DAT_4387b360 + 0x4387af4e);
LAB_4387af4c:
    uVar7 = 0x3b;
  }
  goto LAB_4387b06a;
switchD_4387ad98_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x1b;
    puVar9 = (undefined4 *)(DAT_4387b2d0 + 0x4387adae);
    break;
  case 1:
    uVar7 = 0x1c;
    puVar9 = (undefined4 *)(DAT_4387b2d4 + 0x4387adb8);
    break;
  case 2:
    uVar7 = 0x1d;
    puVar9 = (undefined4 *)(DAT_4387b2d8 + 0x4387adc2);
    break;
  case 3:
    uVar7 = 0x1e;
    puVar9 = (undefined4 *)(DAT_4387b2dc + 0x4387adcc);
    break;
  case 4:
    uVar7 = 0x1f;
    puVar9 = (undefined4 *)(DAT_4387b2e0 + 0x4387add6);
    break;
  case 5:
    uVar7 = 0x20;
    puVar9 = (undefined4 *)(DAT_4387b2e4 + 0x4387ade0);
    break;
  case 6:
    uVar7 = 0x21;
    puVar9 = (undefined4 *)(DAT_4387b2e8 + 0x4387adea);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b2ec + 0x4387adf2);
    goto LAB_4387adf8;
  default:
    puVar9 = (undefined4 *)(DAT_4387b2f0 + 0x4387adfa);
LAB_4387adf8:
    uVar7 = 0x22;
  }
  goto LAB_4387b06a;
switchD_4387af5e_switchD:
  switch(uVar7) {
  case 0:
    uVar7 = 0x3d;
    puVar9 = (undefined4 *)(DAT_4387b368 + 0x4387af72);
    break;
  case 1:
    uVar7 = 0x3e;
    puVar9 = (undefined4 *)(DAT_4387b36c + 0x4387af7a);
    break;
  case 2:
    uVar7 = 0x3f;
    puVar9 = (undefined4 *)(DAT_4387b370 + 0x4387af82);
    break;
  case 3:
    uVar7 = 0x40;
    puVar9 = (undefined4 *)(DAT_4387b374 + 0x4387af8a);
    break;
  case 4:
    uVar7 = 0x41;
    puVar9 = (undefined4 *)(DAT_4387b378 + 0x4387af92);
    break;
  case 5:
    uVar7 = 0x42;
    puVar9 = (undefined4 *)(DAT_4387b37c + 0x4387af9a);
    break;
  case 6:
    uVar7 = 0x43;
    puVar9 = (undefined4 *)(DAT_4387b380 + 0x4387afa2);
    break;
  case 7:
    puVar9 = (undefined4 *)(DAT_4387b384 + 0x4387afa8);
    goto LAB_4387afac;
  default:
    puVar9 = (undefined4 *)(DAT_4387b388 + 0x4387afae);
LAB_4387afac:
    uVar7 = 0x44;
  }
LAB_4387b06a:
  *puVar9 = uVar7;
  if (0x56 < *(int *)(iVar15 + 0x4387b072)) {
    FUN_4387a3c4(3,7,1,DAT_4387b3e0 + 0x4387b082);
    FUN_43902718(DAT_4387b3e4 + 0x4387b08a);
    *(int *)(iVar15 + 0x4387b072) = 0x56;
  }
  uVar5 = FUN_4387a4e8();
  iVar15 = *(int *)(iVar16 + DAT_4387b3e8);
  *(undefined1 *)(iVar15 + 0xca) = uVar5;
  uVar5 = FUN_4387a710();
  *(undefined1 *)(iVar15 + 0xcb) = uVar5;
  uVar5 = FUN_4387a6a0();
  *(undefined1 *)(iVar15 + 0xcc) = uVar5;
  uVar5 = FUN_4387a6ac();
  *(undefined1 *)(iVar15 + 0xcd) = uVar5;
  uVar5 = FUN_4387a6b8();
  *(undefined1 *)(iVar15 + 0xce) = uVar5;
  uVar5 = FUN_4387a6f8();
  *(undefined1 *)(iVar15 + 0xcf) = uVar5;
  uVar5 = FUN_4387a704();
  *(undefined1 *)(iVar15 + 0xd0) = uVar5;
  uVar5 = FUN_4387a71c();
  *(undefined1 *)(iVar15 + 0xd1) = uVar5;
  uVar5 = FUN_4387a528();
  *(undefined1 *)(iVar15 + 0xd2) = uVar5;
  uVar6 = FUN_4387a638();
  *(undefined2 *)(iVar15 + 0xd6) = uVar6;
  uVar6 = FUN_4387a644();
  *(undefined2 *)(iVar15 + 0xd8) = uVar6;
  uVar5 = FUN_4387a728();
  *(undefined1 *)(iVar15 + 0xda) = uVar5;
  uVar5 = FUN_4387a734();
  *(undefined1 *)(iVar15 + 0xdb) = uVar5;
  uVar5 = FUN_4387a740();
  *(undefined1 *)(iVar15 + 0xdc) = uVar5;
  uVar5 = FUN_4387a74c();
  *(undefined1 *)(iVar15 + 0xdd) = uVar5;
  return;
}


/* 4387b9c0 */

undefined1 FUN_4387b9c0(int param_1,undefined4 param_2)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint extraout_r3;
  undefined4 unaff_r4;
  int iVar6;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_lr;
  
  uVar4 = FUN_4387b83c();
  iVar6 = DAT_4387b9f8 + 0x4387b9d2;
  FUN_436bf914(param_2,uVar4);
  bVar1 = *(byte *)(*(int *)(iVar6 + DAT_4387b9fc) + 1);
  uVar5 = (uint)bVar1;
  if ((bVar1 & 0x41) != 0) {
    FUN_43b1251c(uVar4);
    uVar5 = extraout_r3;
  }
  iVar6 = FUN_43acb0a0();
  iVar3 = FUN_436bd24c(0,iVar6);
  if (iVar3 == 1) {
    iVar3 = FUN_436bd274(0,iVar6);
    if (iVar3 == param_1) {
      iVar6 = iVar6 * 0x370 + DAT_436beed0 + 0x436beeaa;
      FUN_439c5320(iVar6,uVar4,0x370,DAT_436beed0 + 0x436beeaa,uVar5,unaff_r4,unaff_r5,unaff_r6,
                   unaff_r7,unaff_lr);
      uVar2 = 0;
      if ((*(byte *)(DAT_436beed4 + 0x436beeb8) & 4) != 0) {
        *(undefined4 *)(iVar6 + 4) = 1;
        return 0;
      }
    }
    else {
      uVar2 = 4;
    }
    return uVar2;
  }
  return 2;
}


/* 43a9c880 */

int FUN_43a9c880(int param_1,undefined4 param_2)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uStack_40;
  undefined2 uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined4 uStack_30;
  undefined1 auStack_2c [8];
  
  FUN_43651208(auStack_2c);
  FUN_43651240(auStack_34);
  uStack_30 = 0;
  FUN_439c5a04(&uStack_40,0,0xc);
  FUN_439c5a04(param_1 + 0x30,0,0xc0);
  FUN_439c5a04(param_1 + 0xf0,0,0xc);
  FUN_439c5a04(param_1 + 0xfc,0,0x38);
  FUN_439c5a04(param_1 + 0x134,0,8);
  FUN_439c5a04(param_1 + 0x13c,0,0xc);
  FUN_439c5a04(param_1 + 0x148,0,0x38);
  FUN_439c5a04(param_1 + 0x180,0,8);
  FUN_439c5a04(param_1 + 0x188,0,0xc);
  FUN_439c5a04(param_1 + 0x194,0,0x20);
  FUN_439c5a04(param_1 + 0x1b4,0,0x120);
  FUN_439c5a04(param_1 + 0x2d4,0,0x120);
  FUN_439c5a04(param_1 + 0x3f4,0,0x24);
  FUN_439c5a04(param_1 + 0x418,0,0x24);
  *(undefined4 *)(param_1 + 0x43c) = 0;
  *(undefined4 *)(param_1 + 0x440) = 0;
  FUN_439c5a04(param_1 + 0x444,0,0xc);
  *(undefined4 *)(param_1 + 0x474) = 0;
  FUN_439c5a04(param_1 + 0x478,0,0xc);
  *(undefined4 *)(param_1 + 0x484) = 0;
  *(undefined1 *)(param_1 + 0x488) = 0;
  *(undefined4 *)(param_1 + 0x48c) = 0;
  FUN_439c5320(param_1 + 0x30,param_2,0xc0);
  uVar1 = FUN_43a8afd2(param_1);
  FUN_43a9c60a(param_1,uVar1,0x208,param_2);
  *(undefined4 *)(param_1 + 0xf0) = *(undefined4 *)(param_1 + 0x60);
  *(undefined2 *)(param_1 + 0xf4) = *(undefined2 *)(param_1 + 100);
  *(undefined4 *)(param_1 + 0xf8) = *(undefined4 *)(param_1 + 0x68);
  iVar2 = FUN_43a9018e(param_1,param_1 + 0xf0,param_1 + 0xfc,param_1 + 0x134);
  if (iVar2 != 0) goto LAB_43a9cb64;
  uStack_40 = *(undefined4 *)(param_1 + 0x100);
  uStack_3c = *(undefined2 *)(param_1 + 0x104);
  uStack_38 = *(undefined4 *)(param_1 + 0x108);
  uVar3 = FUN_43a97630(auStack_34,&uStack_40);
  *(undefined4 *)(param_1 + 0x10c) = uVar3;
  *(undefined4 *)(param_1 + 0x13c) = *(undefined4 *)(param_1 + 0x6c);
  *(undefined2 *)(param_1 + 0x140) = *(undefined2 *)(param_1 + 0x70);
  *(undefined4 *)(param_1 + 0x144) = *(undefined4 *)(param_1 + 0x74);
  iVar2 = FUN_43a9018e(param_1,param_1 + 0x13c,param_1 + 0x148,param_1 + 0x180);
  if (iVar2 != 0) goto LAB_43a9cb64;
  uStack_40 = *(undefined4 *)(param_1 + 0x14c);
  uStack_3c = *(undefined2 *)(param_1 + 0x150);
  uStack_38 = *(undefined4 *)(param_1 + 0x154);
  uVar3 = FUN_43a97630(auStack_34,&uStack_40);
  *(undefined4 *)(param_1 + 0x158) = uVar3;
  *(undefined4 *)(param_1 + 0x188) = *(undefined4 *)(param_1 + 0x78);
  *(undefined2 *)(param_1 + 0x18c) = *(undefined2 *)(param_1 + 0x7c);
  *(undefined4 *)(param_1 + 400) = *(undefined4 *)(param_1 + 0x80);
  iVar4 = FUN_43a971f4(auStack_2c,param_1 + 0x188,param_1 + 0x194);
  iVar2 = iVar4;
  if (iVar4 != 0) goto LAB_43a9cb64;
  uVar5 = (uint)*(byte *)(param_1 + 0x194);
  uVar6 = (uint)*(byte *)(param_1 + 0x1a4);
  *(uint *)(param_1 + 0x450) = (uint)*(byte *)(param_1 + 0xc4);
  *(uint *)(param_1 + 0x43c) = uVar5;
  *(uint *)(param_1 + 0x440) = uVar6;
  *(uint *)(param_1 + 0x454) = (uint)*(byte *)(param_1 + 0xc5);
  *(undefined4 *)(param_1 + 0x458) = *(undefined4 *)(param_1 + 200);
  *(undefined2 *)(param_1 + 0x45c) = *(undefined2 *)(param_1 + 0xcc);
  *(undefined4 *)(param_1 + 0x460) = *(undefined4 *)(param_1 + 0xd0);
  *(undefined2 *)(param_1 + 0x464) = *(undefined2 *)(param_1 + 0xd4);
  *(undefined2 *)(param_1 + 0x466) = *(undefined2 *)(param_1 + 0xd6);
  *(undefined2 *)(param_1 + 0x468) = *(undefined2 *)(param_1 + 0xd8);
  *(undefined2 *)(param_1 + 0x46a) = *(undefined2 *)(param_1 + 0xda);
  *(undefined2 *)(param_1 + 0x46c) = *(undefined2 *)(param_1 + 0xdc);
  *(undefined2 *)(param_1 + 0x46e) = *(undefined2 *)(param_1 + 0xde);
  *(undefined2 *)(param_1 + 0x472) = *(undefined2 *)(param_1 + 0xe2);
  if ((uVar5 == 2) || (uVar6 == 2)) {
    iVar2 = FUN_43a9bb06(param_1);
    if (((iVar2 != 0) || (iVar2 = FUN_43a9bf12(param_1), iVar2 != 0)) ||
       ((*(int *)(param_1 + 0x450) != 0 && (iVar2 = FUN_43a9c3ce(param_1), iVar2 != 0))))
    goto LAB_43a9cb64;
    if (*(short *)(param_1 + 0x94) != -1) {
      uStack_30 = 0;
      goto LAB_43a9cb1c;
    }
  }
  else if ((uVar5 == 0) && (uVar6 == 0)) {
    uStack_30 = 1;
LAB_43a9cb1c:
    iVar2 = FUN_43a9c2e4(param_1,&uStack_30);
    if (iVar2 != 0) goto LAB_43a9cb64;
  }
  if (*(char *)(param_1 + 0x89) == '\x03') {
    FUN_43a9c582(param_1);
  }
  else if (*(char *)(param_1 + 0x89) != '\x04') {
    FUN_43a9c4d2(param_1);
  }
  FUN_43a8b2f8(param_1,0x208,0,*(undefined4 *)(param_1 + 0xf0),*(undefined4 *)(param_1 + 0xf4),
               *(undefined4 *)(param_1 + 0xf8));
  iVar2 = iVar4;
LAB_43a9cb64:
  FUN_43651228(auStack_34);
  FUN_436511e8(auStack_2c);
  return iVar2;
}


/* 43ad069c */

void FUN_43ad069c(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x458) = param_3 * 0x10000 + param_2;
  return;
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


/* 43b3736a */

void FUN_43b3736a(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + 0x458) = param_2;
  *(undefined4 *)(param_1 + 0x45c) = param_3;
  return;
}

