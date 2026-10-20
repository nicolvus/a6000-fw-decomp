/* S39: existing functions; no project modifications. */

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


/* 4378f9b4 */

undefined * FUN_4378f9b4(void)

{
  return &UNK_4378f9ba + DAT_4378f9bc;
}


/* 43814d24 */

undefined8 FUN_43814d24(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  switch(param_1) {
  case 0:
  case 3:
  case 5:
    uVar1 = 0;
    break;
  case 2:
    uVar1 = 2;
    break;
  case 4:
    uVar1 = 3;
    break;
  default:
    iVar2 = DAT_43814d6c + 0x43814d44;
    param_1 = iVar2;
    FUN_43814c78(5,0,1,DAT_43814d68 + 0x43814d42,iVar2,0xd5,param_3);
    FUN_43902718(DAT_43814d70 + 0x43814d56,iVar2,0xd5);
  case 1:
    uVar1 = 1;
  }
  return CONCAT44(param_1,uVar1);
}


/* 43814ea0 */

void FUN_43814ea0(int param_1,undefined4 param_2,int param_3,int param_4,undefined4 param_5,
                 undefined4 param_6,undefined4 param_7)

{
  undefined1 *puVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  undefined1 *puVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 *puVar10;
  int iVar11;
  int iVar12;
  undefined4 auStack_188 [2];
  ushort uStack_180;
  ushort uStack_17e;
  undefined4 uStack_17c;
  uint uStack_178;
  undefined2 uStack_172;
  undefined2 uStack_170;
  undefined4 uStack_16c;
  undefined1 uStack_168;
  undefined1 uStack_167;
  undefined4 uStack_164;
  undefined1 uStack_160;
  undefined4 uStack_15c;
  undefined4 uStack_158;
  undefined1 uStack_154;
  undefined1 uStack_153;
  undefined4 uStack_150;
  undefined1 uStack_14c;
  undefined2 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined1 auStack_dc [4];
  undefined2 uStack_d8;
  byte bStack_d6;
  undefined2 uStack_d4;
  byte bStack_d2;
  undefined2 uStack_d0;
  byte bStack_ce;
  undefined2 uStack_cc;
  byte bStack_ca;
  undefined2 uStack_c8;
  byte bStack_c6;
  undefined2 uStack_c4;
  byte bStack_c2;
  undefined1 auStack_c0 [20];
  undefined1 auStack_ac [20];
  undefined1 auStack_98 [20];
  char cStack_84;
  char cStack_83;
  undefined4 uStack_80;
  undefined1 uStack_7c;
  undefined1 uStack_7b;
  undefined1 uStack_7a;
  undefined2 uStack_78;
  undefined1 uStack_76;
  undefined1 uStack_75;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_68;
  uint uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  uint uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined2 uStack_2c;
  
  uStack_17e = *(ushort *)(param_1 + 0x1a0);
  uStack_180 = *(ushort *)(param_1 + 0x19e);
  auStack_188[0] = param_2;
  uStack_17c = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_178 = (uint)*(byte *)(param_1 + 0xc18);
  iVar12 = 0;
  uStack_172 = *(undefined2 *)(param_1 + 0xc76);
  uStack_170 = *(undefined2 *)(param_1 + 0xc74);
  iVar11 = DAT_438151f0 + 0x43814ee4;
  uStack_154 = *(undefined1 *)(param_1 + 0xc88);
  uStack_153 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_16c = FUN_43814d74(*(undefined4 *)(*(int *)(param_3 + 4) + 0x14));
  uStack_168 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_167 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_164 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_160 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_15c = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),*(undefined1 *)(param_1 + 0x191));
  uStack_158 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_150 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  iVar4 = FUN_439fd844();
  uStack_14c = (undefined1)*(undefined4 *)(iVar4 + 0x1c);
  uVar7 = (uint)uStack_180;
  iVar5 = *(int *)(iVar4 + 0x1c);
  uVar8 = (uint)uStack_17e;
  puVar10 = auStack_188;
  while( true ) {
    if (iVar12 == iVar5) break;
    uVar2 = *(ushort *)(iVar4 + 0x28);
    iVar12 = iVar12 + 1;
    uVar3 = FUN_4355faf0(uVar7 * ((uint)*(ushort *)(iVar4 + 0x24) + (uint)(uVar2 >> 1)),0x280);
    *(undefined2 *)(puVar10 + 0x10) = uVar3;
    uVar3 = FUN_4355faf0(uVar8 * ((uint)*(ushort *)(iVar4 + 0x26) +
                                 (uint)(*(ushort *)(iVar4 + 0x2a) >> 1)),0x1e0);
    *(undefined2 *)((int)puVar10 + 0x42) = uVar3;
    uVar3 = FUN_4355faf0(uVar7 * uVar2,0x280);
    puVar10[0x12] = *(undefined4 *)(iVar4 + 0x20);
    *(undefined2 *)(puVar10 + 0x11) = uVar3;
    iVar4 = iVar4 + 0x54;
    puVar10 = puVar10 + 3;
  }
  uStack_e4 = *(undefined4 *)(param_1 + 0xc30);
  uStack_e8 = *(undefined2 *)(param_1 + 0xc78);
  uStack_e0 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_188,auStack_dc,param_3);
  uStack_74 = 3;
  uStack_70 = param_5;
  iVar4 = *(int *)(iVar11 + DAT_438151f4);
  if (*(char *)(iVar4 + 0xef) == '\0') {
    uVar2 = *(ushort *)(param_1 + 0x15c);
    uStack_5c = *(undefined4 *)(param_1 + 0x160);
  }
  else {
    uVar2 = *(ushort *)(param_1 + 0x1c);
    uStack_5c = *(undefined4 *)(param_1 + 0x20);
  }
  uStack_68 = 0;
  uStack_60 = (uint)uVar2;
  uStack_4c = 0;
  uStack_58 = 0;
  uStack_50 = 0;
  uStack_3c = *(undefined4 *)(param_1 + 0xc4);
  uStack_44 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_40 = *(undefined4 *)(param_1 + 0x24);
  uStack_38 = param_6;
  uStack_34 = param_7;
  iVar5 = FUN_436be554(param_2,&uStack_74);
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,DAT_438151f8 + 0x4381506a,iVar5);
    FUN_43902718(DAT_438151fc + 0x43815074,iVar5);
  }
  uStack_30 = 0;
  uStack_2c = 0;
  iVar5 = FUN_436bdbfc(param_2,0,&uStack_30);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_30;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_30._2_2_;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_2c;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_2c;
  if (iVar5 != 0) {
    FUN_43814c78(3,9,1,DAT_43815200 + 0x438150b4,iVar5);
    FUN_43902718(DAT_43815204 + 0x438150be,iVar5);
  }
  if ((*(byte *)(iVar4 + 0xc) & 8) != 0) {
    FUN_43814c78(3,9,1,DAT_43815208 + 0x438150d6);
    FUN_43902718(DAT_4381520c + 0x438150de);
  }
  *(undefined1 *)(param_4 + 100) = 1;
  puVar6 = auStack_dc;
  iVar5 = 0;
  *(undefined4 *)(param_4 + 0x68) = *(undefined4 *)(param_1 + 0x1f0);
  iVar4 = param_4;
  do {
    iVar5 = iVar5 + 1;
    *(undefined1 *)(iVar4 + 0x6c) = puVar6[0x1c];
    *(undefined1 *)(iVar4 + 0x80) = puVar6[0x30];
    puVar1 = puVar6 + 0x44;
    puVar6 = puVar6 + 1;
    *(undefined1 *)(iVar4 + 0x94) = *puVar1;
    iVar4 = iVar4 + 1;
  } while (iVar5 != 0x14);
  if (cStack_84 == '\0') {
    *(undefined1 *)(param_4 + 0xa8) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 0xa8) = 1;
    *(undefined4 *)(param_4 + 0xac) = uStack_80;
    *(undefined2 *)(param_4 + 0xb4) = uStack_d4;
    *(undefined2 *)(param_4 + 0xb0) = uStack_d8;
    *(undefined2 *)(param_4 + 0xbc) = uStack_cc;
    *(ushort *)(param_4 + 0xb2) = (ushort)bStack_d6;
    *(undefined2 *)(param_4 + 0xc4) = uStack_c4;
    *(ushort *)(param_4 + 0xb6) = (ushort)bStack_d2;
    *(undefined2 *)(param_4 + 0xb8) = uStack_d0;
    *(ushort *)(param_4 + 0xba) = (ushort)bStack_ce;
    *(ushort *)(param_4 + 0xbe) = (ushort)bStack_ca;
    *(undefined2 *)(param_4 + 0xc0) = uStack_c8;
    *(ushort *)(param_4 + 0xc2) = (ushort)bStack_c6;
    *(ushort *)(param_4 + 0xc6) = (ushort)bStack_c2;
  }
  if (cStack_83 == '\0') {
    *(undefined1 *)(param_4 + 200) = 0;
  }
  else {
    *(undefined1 *)(param_4 + 200) = 1;
    uVar9 = *(undefined4 *)(param_1 + 0x1f0);
    *(int *)(param_4 + 0xd4) = param_1 + 0xbc;
    *(undefined4 *)(param_4 + 0xcc) = uVar9;
    *(undefined1 *)(param_4 + 0xd0) = auStack_dc[0];
  }
  *(undefined1 *)(param_4 + 0xd8) = uStack_7c;
  *(undefined1 *)(param_4 + 0xd9) = uStack_7b;
  *(undefined1 *)(param_4 + 0xda) = uStack_7a;
  *(undefined2 *)(param_4 + 0xdc) = uStack_78;
  *(undefined1 *)(param_4 + 0xde) = uStack_76;
  *(undefined1 *)(param_4 + 0xdf) = uStack_75;
  *(undefined2 *)(param_4 + 0xe0) = uStack_172;
  return;
}


/* 43815210 */

void FUN_43815210(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 auStack_198 [2];
  undefined2 uStack_190;
  undefined2 uStack_18e;
  undefined4 uStack_18c;
  uint uStack_188;
  undefined2 uStack_182;
  undefined2 uStack_180;
  undefined4 uStack_17c;
  undefined1 uStack_178;
  undefined1 uStack_177;
  undefined4 uStack_174;
  undefined1 uStack_170;
  undefined4 uStack_16c;
  undefined4 uStack_168;
  undefined1 uStack_164;
  undefined1 uStack_163;
  undefined4 uStack_160;
  undefined1 uStack_15c;
  undefined2 uStack_f8;
  undefined4 uStack_f4;
  undefined4 uStack_f0;
  undefined1 auStack_ec [104];
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_78;
  uint uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  uint uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined2 uStack_24;
  
  uStack_38 = 0x80;
  uStack_40 = 4;
  uStack_34 = 0;
  uStack_3c = 7;
  uStack_30 = 0;
  uStack_2c = 0;
  uStack_36 = 0;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815510 + 0x43815254,iVar1);
    FUN_43902718(DAT_43815514 + 0x4381525e,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),1,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815518 + 0x4381527e,iVar1);
    FUN_43902718(DAT_4381551c + 0x43815288,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0xb,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815520 + 0x438152a8,iVar1);
    FUN_43902718(DAT_43815524 + 0x438152b2,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),3,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815528 + 0x438152d2,iVar1);
    FUN_43902718(DAT_4381552c + 0x438152dc,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),4,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815530 + 0x438152fc,iVar1);
    FUN_43902718(DAT_43815534 + 0x43815306,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x11,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815538 + 0x43815326,iVar1);
    FUN_43902718(DAT_4381553c + 0x43815330,iVar1);
  }
  uStack_36 = 0x11a;
  uStack_2c = 1;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815540 + 0x43815360,iVar1);
    FUN_43902718(DAT_43815544 + 0x4381536a,iVar1);
  }
  uStack_36 = 0x234;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815548 + 0x43815392,iVar1);
    FUN_43902718(DAT_4381554c + 0x4381539c,iVar1);
  }
  auStack_198[0] = *(undefined4 *)(param_1 + 0xc6c);
  uStack_18e = *(undefined2 *)(param_1 + 0x1a0);
  uStack_190 = *(undefined2 *)(param_1 + 0x19e);
  uStack_18c = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_188 = (uint)*(byte *)(param_1 + 0xc18);
  uStack_180 = *(undefined2 *)(param_1 + 0xc74);
  uStack_182 = *(undefined2 *)(param_1 + 0xc76);
  uStack_164 = *(undefined1 *)(param_1 + 0xc88);
  uStack_163 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_17c = FUN_43814d74(*(undefined4 *)(*(int *)(param_2 + 4) + 0x14));
  uStack_178 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_177 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_174 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_170 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_16c = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),*(undefined1 *)(param_1 + 0x191));
  uStack_168 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_160 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  uStack_15c = 0;
  uStack_f8 = *(undefined2 *)(param_1 + 0xc78);
  uStack_f4 = *(undefined4 *)(param_1 + 0xc30);
  uStack_f0 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_198,auStack_ec,param_2);
  uStack_70 = (uint)*(ushort *)(param_1 + 0x15c);
  uStack_78 = 0;
  uStack_6c = *(undefined4 *)(param_1 + 0x160);
  uStack_5c = 0;
  uStack_68 = 0;
  uStack_54 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_60 = 0;
  uStack_84 = 3;
  uStack_50 = *(undefined4 *)(param_1 + 0x24);
  uStack_4c = *(undefined4 *)(param_1 + 0xc4);
  uStack_44 = param_5;
  uStack_80 = param_3;
  uStack_48 = param_4;
  iVar1 = FUN_436be554(*(undefined4 *)(param_1 + 0xc6c),&uStack_84);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815550 + 0x438154b0,iVar1);
    FUN_43902718(DAT_43815554 + 0x438154ba,iVar1);
  }
  uStack_28 = 0;
  uStack_24 = 0;
  iVar1 = FUN_436bdbfc(*(undefined4 *)(param_1 + 0xc6c),0,&uStack_28);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_28;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_24;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_24;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_28._2_2_;
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815558 + 0x438154fc,iVar1);
    FUN_43902718(DAT_4381555c + 0x43815506,iVar1);
  }
  return;
}


/* 43815560 */

void FUN_43815560(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 auStack_208 [2];
  undefined2 uStack_200;
  undefined2 uStack_1fe;
  undefined4 uStack_1fc;
  uint uStack_1f8;
  undefined2 uStack_1f2;
  undefined2 uStack_1f0;
  undefined4 uStack_1ec;
  undefined1 uStack_1e8;
  undefined1 uStack_1e7;
  undefined4 uStack_1e4;
  undefined1 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined1 uStack_1d4;
  undefined1 uStack_1d3;
  undefined4 uStack_1d0;
  undefined1 uStack_1cc;
  undefined2 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  undefined1 auStack_15c [4];
  ushort uStack_158;
  undefined1 auStack_ec [104];
  undefined4 auStack_84 [2];
  uint uStack_7c;
  undefined4 uStack_78;
  uint uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  uint uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined2 uStack_24;
  
  uStack_38 = 0x80;
  uStack_40 = 4;
  uStack_3c = 7;
  uStack_34 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  uStack_36 = 0;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),7,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158cc + 0x438155a4,iVar1);
    FUN_43902718(DAT_438158d0 + 0x438155ae,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),1,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158d4 + 0x438155ce,iVar1);
    FUN_43902718(DAT_438158d8 + 0x438155d8,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0xb,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158dc + 0x438155f8,iVar1);
    FUN_43902718(DAT_438158e0 + 0x43815602,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),3,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158e4 + 0x43815622,iVar1);
    FUN_43902718(DAT_438158e8 + 0x4381562c,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),4,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158ec + 0x4381564c,iVar1);
    FUN_43902718(DAT_438158f0 + 0x43815656,iVar1);
  }
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x11,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158f4 + 0x43815676,iVar1);
    FUN_43902718(DAT_438158f8 + 0x43815680,iVar1);
  }
  uStack_36 = 0x7d;
  uStack_2c = 1;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_438158fc + 0x438156ae,iVar1);
    FUN_43902718(DAT_43815900 + 0x438156b8,iVar1);
  }
  uStack_36 = 0x56a;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),0x10,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815904 + 0x438156e0,iVar1);
    FUN_43902718(DAT_43815908 + 0x438156ea,iVar1);
  }
  uStack_36 = 0x268;
  iVar1 = FUN_43acb8ae(*(undefined4 *)(param_1 + 0xc6c),6,&uStack_40);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_4381590c + 0x43815712,iVar1);
    FUN_43902718(DAT_43815910 + 0x4381571c,iVar1);
  }
  auStack_208[0] = *(undefined4 *)(param_1 + 0xc6c);
  uStack_200 = *(undefined2 *)(param_1 + 0x19e);
  uStack_1fe = *(undefined2 *)(param_1 + 0x1a0);
  uStack_1fc = FUN_43814d24(*(undefined4 *)(param_1 + 0x1b4));
  uStack_1f8 = (uint)*(byte *)(param_1 + 0xc18);
  uStack_1f2 = *(undefined2 *)(param_1 + 0xc76);
  uStack_1f0 = *(undefined2 *)(param_1 + 0xc74);
  uStack_1d4 = *(undefined1 *)(param_1 + 0xc88);
  uStack_1d3 = *(undefined1 *)(param_1 + 0xc8a);
  uStack_1ec = FUN_43814d74(*(undefined4 *)(*(int *)(param_2 + 4) + 0x14));
  uStack_1e8 = FUN_43814e84(*(undefined4 *)(param_1 + 0xc7c));
  uStack_1e7 = *(char *)(param_1 + 0xc80) == '\x01';
  uStack_1e4 = *(undefined4 *)(param_1 + 0x1f0);
  uStack_1e0 = FUN_43b04042(*(undefined4 *)(param_1 + 0xc84));
  uStack_1dc = FUN_43814db4(*(undefined4 *)(param_1 + 0x1b0),0);
  uStack_1d8 = FUN_43814e04(*(undefined4 *)(param_1 + 0xc8c));
  uStack_1d0 = FUN_43814e44(*(undefined4 *)(param_1 + 0x1e8));
  uStack_1cc = 0;
  uStack_164 = *(undefined4 *)(param_1 + 0xc30);
  uStack_168 = *(undefined2 *)(param_1 + 0xc78);
  uStack_160 = *(undefined4 *)(param_1 + 0xc34);
  thunk_FUN_4387a1fc(auStack_208,auStack_ec,param_2);
  iVar1 = FUN_43902df8(DAT_438158c8,param_3,0,auStack_15c,5);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815914 + 0x43815800);
    FUN_43902718(DAT_43815918 + 0x43815808);
  }
  uStack_7c = (uint)uStack_158;
  auStack_84[0] = 0;
  uStack_78 = 0;
  uStack_70 = (uint)*(ushort *)(param_1 + 0x15c);
  uStack_5c = 0;
  uStack_68 = 0;
  uStack_6c = *(undefined4 *)(param_1 + 0x160);
  uStack_60 = 0;
  uStack_4c = *(undefined4 *)(param_1 + 0xc4);
  uStack_54 = (uint)*(ushort *)(param_1 + 0x1c);
  uStack_50 = *(undefined4 *)(param_1 + 0xd10);
  uStack_44 = param_5;
  uStack_48 = param_4;
  iVar1 = FUN_436be554(*(undefined4 *)(param_1 + 0xc6c),auStack_84);
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_4381591c + 0x4381585c,iVar1);
    FUN_43902718(DAT_43815920 + 0x43815866,iVar1);
    FUN_43902fbc(uStack_158,2,5);
  }
  uStack_28 = 0;
  uStack_24 = 0;
  iVar1 = FUN_436bdbfc(*(undefined4 *)(param_1 + 0xc6c),0,&uStack_28);
  *(undefined2 *)(param_1 + 0x1a6) = (undefined2)uStack_28;
  *(undefined2 *)(param_1 + 0x1aa) = uStack_28._2_2_;
  *(undefined2 *)(param_1 + 0x1a8) = uStack_24;
  *(undefined2 *)(param_1 + 0x1ac) = uStack_24;
  if (iVar1 != 0) {
    FUN_43814c78(3,9,1,DAT_43815924 + 0x438158b4,iVar1);
    FUN_43902718(DAT_43815928 + 0x438158be,iVar1);
  }
  return;
}


/* 4387a1fc */

void FUN_4387a1fc(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_58 [56];
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  FUN_4387a758(param_1,param_3);
  uVar1 = FUN_4387a4dc();
  iVar4 = DAT_4387a2c8 + 0x4387a21a;
  uStack_20 = FUN_4387b3ec();
  uVar2 = FUN_4387a4f4();
  FUN_43acb946(uVar1,uVar2,&uStack_20,&uStack_1c);
  FUN_436bef2c(uVar1,uStack_1c);
  iVar3 = FUN_4387a6c4(uVar1);
  if (iVar3 == 0) {
    FUN_43acb7be(uVar1);
  }
  FUN_4387a30c(uVar1,uStack_1c);
  FUN_4387b784(uVar1,uStack_1c);
  FUN_4387bb18(uVar1,uStack_1c);
  FUN_4387bc58(uVar1,uStack_1c);
  FUN_4387c120(uVar1,uStack_1c);
  FUN_4387c570(uVar1,uStack_1c,param_3);
  FUN_4387b9c0(uVar1,uStack_1c);
  FUN_436bf8e8(uStack_1c,auStack_58);
  FUN_436beed8(uVar1,auStack_58);
  FUN_4387c20c();
  uVar2 = FUN_4387b848();
  FUN_436bf864(uStack_1c,uVar2);
  FUN_436bebd8(uVar1,uVar2);
  FUN_43b122fe(param_2);
  FUN_4387a34c();
  FUN_436befd8(**(undefined1 **)(iVar4 + DAT_4387a2cc));
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


/* 4387b784 */

undefined4 FUN_4387b784(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar2 = FUN_4387b7d0();
  iVar3 = DAT_4387b7bc + 0x4387b796;
  FUN_436bf88c(param_2,uVar2);
  if ((*(byte *)(*(int *)(iVar3 + DAT_4387b7c0) + 1) & 0x44) != 0) {
    FUN_43b122ec(uVar2);
  }
  iVar3 = FUN_43acb0a0();
  iVar1 = FUN_436bd24c(0,iVar3);
  if (iVar1 == 1) {
    iVar1 = FUN_436bd274(0,iVar3);
    if (iVar1 == param_1) {
      FUN_439c5320(iVar3 * 0x9c + DAT_436becb4 + 0x436beca2,uVar2);
      return 0;
    }
    return 4;
  }
  return 2;
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


/* 4387bb18 */

undefined4 FUN_4387bb18(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  uVar2 = FUN_4387b7dc();
  iVar5 = DAT_4387bb6c + 0x4387bb2a;
  uVar3 = FUN_4387b7e8();
  uVar4 = FUN_4387b7f4();
  if ((*(byte *)(*(int *)(iVar5 + DAT_4387bb70) + 1) & 0x48) == 0) {
    FUN_4387bcb4(uVar2,uVar3,uVar4);
  }
  else {
    thunk_FUN_4387ba00(uVar2,uVar3,uVar4);
  }
  iVar5 = FUN_43acb0a0();
  iVar1 = FUN_436bd24c(0,iVar5);
  if (iVar1 == 1) {
    iVar1 = FUN_436bd274(0,iVar5);
    if (iVar1 == param_1) {
      iVar5 = iVar5 * 0x14;
      FUN_439c5320(DAT_436bed24 + 0x436becee + iVar5,uVar2,0x14);
      FUN_439c5320(DAT_436bed28 + 0x436becfe + iVar5,uVar3,0x14);
      FUN_439c5320(DAT_436bed2c + 0x436bed0c + iVar5,uVar4,0x14);
      return 0;
    }
    return 4;
  }
  return 2;
}


/* 4387bc58 */

undefined4 FUN_4387bc58(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  uVar2 = FUN_4387b800();
  iVar5 = DAT_4387bcac + 0x4387bc6a;
  uVar3 = FUN_4387b80c();
  uVar4 = FUN_4387b818();
  if ((*(byte *)(*(int *)(iVar5 + DAT_4387bcb0) + 1) & 0xc0) == 0) {
    FUN_4387bcb4(uVar2,uVar3,uVar4);
  }
  else {
    thunk_FUN_4387bb74(uVar2,uVar3,uVar4);
  }
  iVar5 = FUN_43acb0a0();
  iVar1 = FUN_436bd24c(0,iVar5);
  if (iVar1 == 1) {
    iVar1 = FUN_436bd274(0,iVar5);
    if (iVar1 == param_1) {
      iVar5 = iVar5 * 0x14;
      FUN_439c5320(DAT_436bed9c + 0x436bed66 + iVar5,uVar2,0x14);
      FUN_439c5320(DAT_436beda0 + 0x436bed76 + iVar5,uVar3,0x14);
      FUN_439c5320(DAT_436beda4 + 0x436bed84 + iVar5,uVar4,0x14);
      return 0;
    }
    return 4;
  }
  return 2;
}


/* 4387c120 */

undefined1 FUN_4387c120(int param_1,undefined4 param_2)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  iVar3 = FUN_4387b824();
  iVar5 = DAT_4387c158 + 0x4387c132;
  FUN_436bf8a8(param_2,iVar3);
  if ((*(byte *)(*(int *)(iVar5 + DAT_4387c15c) + 1) & 0x50) != 0) {
    FUN_43b126b4(iVar3);
  }
  iVar5 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar5);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar5);
  if (iVar2 == param_1) {
    iVar2 = iVar5 * 0x1a4 + DAT_436bee24 + 0x436bedda;
    FUN_439c5320(iVar2,iVar3);
    if (*(char *)(DAT_436bee28 + 0x436bede8 + iVar5) == '\0') {
      *(undefined4 *)(iVar2 + 0x54) = 0;
      *(undefined4 *)(iVar2 + 0x58) = 0;
      *(undefined4 *)(iVar2 + 0x7c) = 1;
    }
    else {
      uVar4 = *(undefined4 *)(iVar3 + 0x7c);
      *(undefined4 *)(iVar2 + 0x54) = 1;
      *(undefined4 *)(iVar2 + 0x58) = 1;
      *(undefined4 *)(iVar2 + 0x7c) = uVar4;
    }
    uVar1 = 0;
    if ((*(byte *)(DAT_436bee2c + 0x436bee00) & 2) != 0) {
      *(undefined4 *)(iVar5 * 0x1a4 + DAT_436bee30 + 0x436bee90) = 1;
      return 0;
    }
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}


/* 4387c570 */

void FUN_4387c570(undefined4 param_1,undefined4 param_2,int *param_3)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  ushort uVar4;
  ushort uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined1 uVar8;
  undefined2 uVar9;
  ushort uVar10;
  int iVar11;
  undefined4 uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  int *piVar16;
  uint *puVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  int iVar21;
  char *pcVar22;
  ushort uVar23;
  int iVar24;
  int *piVar25;
  undefined1 *puVar26;
  int iVar27;
  int iVar28;
  uint uVar29;
  uint in_fpscr;
  uint uVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  uint uStack_100;
  uint uStack_fc;
  undefined2 uStack_ec;
  byte bStack_ea;
  int aiStack_e8 [24];
  undefined2 uStack_88;
  int iStack_84;
  int iStack_80;
  char cStack_7c;
  undefined1 auStack_78 [20];
  undefined1 auStack_64 [20];
  undefined1 auStack_50 [20];
  undefined1 auStack_3c [24];
  
  iVar11 = FUN_4387b830();
  iVar28 = DAT_4387d1d0 + 0x4387c588;
  FUN_436bf8c4(param_2,iVar11);
  iVar24 = *(int *)(iVar28 + DAT_4387d1d4);
  uVar8 = 0;
  if (*(char *)(iVar24 + 0xeb2) != '\0') {
    uVar8 = *(undefined1 *)(iVar24 + 0xeb3);
  }
  *(undefined1 *)(iVar11 + 0x10) = uVar8;
  FUN_43b12252(auStack_3c,4);
  FUN_43b12252(auStack_50,4);
  FUN_43b12252(auStack_64,4);
  FUN_4387b404(&uStack_ec);
  uVar29 = (uint)bStack_ea;
  if (cStack_7c == '\x15') {
    uVar20 = 1;
  }
  else {
    uVar20 = (uint)(*(int *)(*param_3 + 0x510) == 1);
  }
  iVar15 = *param_3;
  uVar18 = *(int *)(iVar15 + 0xe0) - 0x20;
  if ((uVar18 < 10) && ((1 << (uVar18 & 0xff) & 0x3c1U) != 0)) {
    if (*(int *)(param_3[2] + 0x20c) == 1) {
      uVar20 = uVar20 ^ 1;
    }
    else if (uVar20 == 0) {
      uVar20 = 3;
    }
    else {
      uVar20 = 2;
    }
  }
  else if (*(int *)(param_3[2] + 0x20c) == 1) {
    if (uVar20 == 0) {
      uVar20 = 5;
    }
    else {
      uVar20 = 4;
    }
  }
  else if (uVar20 == 0) {
    uVar20 = 7;
  }
  else {
    uVar20 = 6;
  }
  uVar10 = *(ushort *)(iVar15 + 0xc);
  if (uVar10 == 0x708) {
    uVar20 = 2;
    goto LAB_4387c782;
  }
  if (uVar10 < 0x709) {
    if (uVar10 == 0x702) {
LAB_4387c66e:
      uVar20 = 1;
    }
    else if (uVar10 == 0x707) {
      iVar15 = param_3[2];
      switch(*(undefined4 *)(iVar15 + 0x1c)) {
      case 0:
        if (*(char *)(iVar15 + 0x24) == '\0') {
          switch(*(undefined4 *)(param_3[1] + 0x10)) {
          case 0:
          case 1:
            if (*(char *)(iVar15 + 0x29a) == '\0') {
              if (uVar20 < 8) {
                iVar15 = DAT_4387d1ec + 0x4387c710;
                goto LAB_4387c6c6;
              }
              uVar20 = 0x2b;
            }
            else {
              if (uVar20 < 8) {
                iVar15 = DAT_4387d1e8 + 0x4387c704;
                goto LAB_4387c6c6;
              }
              uVar20 = 0x33;
            }
            break;
          case 2:
          case 3:
            if (uVar20 < 8) {
              iVar15 = DAT_4387d1f0 + 0x4387c71c;
              goto LAB_4387c6c6;
            }
            uVar20 = 0x3b;
            break;
          default:
            uVar20 = 0x3c;
          }
        }
        else {
          switch(*(undefined4 *)(param_3[1] + 0x10)) {
          case 0:
          case 1:
            if (*(char *)(iVar15 + 0x29a) == '\0') {
              if (uVar20 < 8) {
                iVar15 = DAT_4387d1e0 + 0x4387c6d8;
                goto LAB_4387c6c6;
              }
              uVar20 = 0x12;
            }
            else {
              if (uVar20 < 8) {
                iVar15 = DAT_4387d1dc + 0x4387c6c8;
                goto LAB_4387c6c6;
              }
              uVar20 = 0x1a;
            }
            break;
          case 2:
          case 3:
            if (uVar20 < 8) {
              iVar15 = DAT_4387d1e4 + 0x4387c6e4;
              goto LAB_4387c6c6;
            }
            uVar20 = 0x22;
            break;
          default:
            uVar20 = 0x23;
          }
        }
        break;
      case 1:
        if (uVar20 < 8) {
          iVar15 = DAT_4387d1f4 + 0x4387c728;
LAB_4387c6c6:
          uVar20 = *(uint *)(iVar15 + uVar20 * 4);
          goto LAB_4387c77c;
        }
        uVar20 = 0x44;
        break;
      case 2:
        if (uVar20 < 8) {
          iVar15 = DAT_4387d1f8 + 0x4387c734;
          goto LAB_4387c6c6;
        }
        uVar20 = 0x54;
        break;
      case 3:
        if (uVar20 < 8) {
          iVar15 = DAT_4387d1fc + 0x4387c740;
          goto LAB_4387c6c6;
        }
        uVar20 = 0x4c;
        break;
      case 4:
        if (uVar20 < 8) {
          iVar15 = DAT_4387d1d8 + 0x4387c6a0;
          goto LAB_4387c6c6;
        }
        uVar20 = 10;
        break;
      default:
        uVar20 = 0x55;
      }
    }
    else {
LAB_4387c740:
      uVar20 = 0x56;
    }
  }
  else {
    if (uVar10 == 0x714) goto LAB_4387c66e;
    if (uVar10 != 0x715) goto LAB_4387c740;
    uVar20 = (uint)(1 < *(int *)(iVar15 + 0x450) - 1U);
LAB_4387c77c:
    if (0x55 < (int)uVar20) {
      uVar20 = 0x56;
    }
  }
LAB_4387c782:
  uVar20 = (uint)*(byte *)(iVar24 + uVar20);
  uVar12 = FUN_43b16700(uStack_88,0,0x4000,0,0x80);
  FUN_43b12262(auStack_3c,iVar24 + (uVar20 + 0x1c6) * 8 + 2,uStack_ec);
  iVar27 = *(int *)(iVar28 + DAT_4387d200);
  FUN_43b12262(auStack_50,iVar27 + (uVar20 + 0x1a0) * 8 + 4,uStack_ec);
  iVar21 = *(int *)(iVar28 + DAT_4387d204);
  FUN_43b12262(auStack_64,iVar21 + uVar20 * 8 + 0x11e,uVar12);
  *(uint *)(iVar11 + 0xc) = (uint)*(byte *)(iVar27 + uVar20 + 0x514);
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x80) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x14) = uVar8;
  uVar9 = FUN_4387c4ac(auStack_3c,iVar24 + (uVar20 + 0x48) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x16) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x58) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x18) = uVar9;
  *(undefined2 *)(iVar11 + 0x1a) = *(undefined2 *)(iVar24 + (uVar20 + 0x1a0) * 2 + 2);
  *(undefined2 *)(iVar11 + 0x1c) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x362);
  *(undefined2 *)(iVar11 + 0x1e) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x382);
  *(undefined2 *)(iVar11 + 0x20) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x3a2);
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x78) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x22) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x88) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x24) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x98) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x26) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0xa8) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x28) = uVar9;
  *(undefined2 *)(iVar11 + 0x2a) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x5c2);
  *(undefined2 *)(iVar11 + 0x2c) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x5e2);
  *(undefined2 *)(iVar11 + 0x2e) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x602);
  *(undefined2 *)(iVar11 + 0x30) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x622);
  iVar15 = iVar24 + uVar20;
  *(undefined1 *)(iVar11 + 0x32) = *(undefined1 *)(iVar15 + 0x642);
  *(undefined1 *)(iVar11 + 0x33) = *(undefined1 *)(iVar15 + 0x652);
  *(undefined2 *)(iVar11 + 0x34) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x662);
  *(undefined1 *)(iVar11 + 0x36) = *(undefined1 *)(iVar15 + 0x682);
  *(undefined2 *)(iVar11 + 0x38) = *(undefined2 *)(iVar24 + uVar20 * 2 + 0x692);
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0xd6) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x3a) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0xe6) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x3c) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0xf6) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x3e) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x106) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x40) = uVar9;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x22c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x42) = uVar8;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x23c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x43) = uVar8;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x136) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x46) = uVar9;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x28c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x48) = uVar8;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x29c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x49) = uVar8;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x166) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x4c) = uVar9;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x2ec) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x4e) = uVar8;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x2fc) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x4f) = uVar8;
  uVar9 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x196) * 8 + 2);
  *(undefined2 *)(iVar11 + 0x52) = uVar9;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x34c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x54) = uVar8;
  uVar8 = FUN_4387b520(auStack_3c,iVar24 + (uVar20 + 0x35c) * 4 + 2);
  *(undefined1 *)(iVar11 + 0x55) = uVar8;
  iVar15 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x126) * 8 + 2);
  if ((uint)*(byte *)(iVar11 + 0x43) == (uint)*(byte *)(iVar11 + 0x42)) {
    uStack_100 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)*(byte *)(iVar11 + 0x43) -
                                        (uint)*(byte *)(iVar11 + 0x42),(byte)(in_fpscr >> 0x16) & 3)
    ;
    fVar31 = (float)VectorSignedToFloat((iVar15 - (uint)*(ushort *)(iVar11 + 0x40)) * 0x10,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uStack_100 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  iVar15 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x156) * 8 + 2);
  if ((uint)*(byte *)(iVar11 + 0x49) == (uint)*(byte *)(iVar11 + 0x48)) {
    uStack_fc = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)*(byte *)(iVar11 + 0x49) -
                                        (uint)*(byte *)(iVar11 + 0x48),(byte)(in_fpscr >> 0x16) & 3)
    ;
    fVar31 = (float)VectorSignedToFloat((iVar15 - (uint)*(ushort *)(iVar11 + 0x46)) * 0x10,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uStack_fc = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  iVar15 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x186) * 8 + 2);
  if ((uint)*(byte *)(iVar11 + 0x4f) == (uint)*(byte *)(iVar11 + 0x4e)) {
    uVar18 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)*(byte *)(iVar11 + 0x4f) -
                                        (uint)*(byte *)(iVar11 + 0x4e),(byte)(in_fpscr >> 0x16) & 3)
    ;
    fVar31 = (float)VectorSignedToFloat((iVar15 - (uint)*(ushort *)(iVar11 + 0x4c)) * 0x10,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uVar18 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  iVar24 = FUN_4387b5dc(auStack_3c,iVar24 + (uVar20 + 0x1b6) * 8 + 2);
  if ((uint)*(byte *)(iVar11 + 0x55) == (uint)*(byte *)(iVar11 + 0x54)) {
    uVar30 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)*(byte *)(iVar11 + 0x55) -
                                        (uint)*(byte *)(iVar11 + 0x54),(byte)(in_fpscr >> 0x16) & 3)
    ;
    fVar31 = (float)VectorSignedToFloat((iVar24 - (uint)*(ushort *)(iVar11 + 0x52)) * 0x10,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uVar30 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  if (uStack_100 < 0x800) {
    *(short *)(iVar11 + 0x44) = (short)uStack_100;
  }
  else {
    *(undefined2 *)(iVar11 + 0x44) = 0x7ff;
  }
  if (uStack_fc < 0x800) {
    *(short *)(iVar11 + 0x4a) = (short)uStack_fc;
  }
  else {
    *(undefined2 *)(iVar11 + 0x4a) = 0x7ff;
  }
  if (uVar18 < 0x800) {
    *(short *)(iVar11 + 0x50) = (short)uVar18;
  }
  else {
    *(undefined2 *)(iVar11 + 0x50) = 0x7ff;
  }
  if (uVar30 < 0x800) {
    *(short *)(iVar11 + 0x56) = (short)uVar30;
  }
  else {
    uStack_fc = 0x7ff;
  }
  if (0x7ff < uVar30) {
    *(short *)(iVar11 + 0x56) = (short)uStack_fc;
  }
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x148) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x58) = uVar8;
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x158) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x59) = uVar8;
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x168) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x5a) = uVar8;
  uVar9 = FUN_4387c4ac(auStack_50,iVar27 + (uVar20 + 0xbc) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x5c) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 0xcc) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x5e) = uVar9;
  uVar9 = FUN_4387c4ac(auStack_50,iVar27 + (uVar20 + 0xdc) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x60) = uVar9;
  uVar9 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 0xec) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x62) = uVar9;
  iVar24 = 0;
  do {
    iVar15 = iVar24;
    uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + iVar15 * 0x10 + 0x1f8) * 4 + 4);
    *(undefined1 *)(iVar11 + iVar15 + 100) = uVar8;
    iVar24 = iVar15 + 1;
  } while (iVar15 + 1 != 9);
  uVar9 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 0x144) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x6e) = uVar9;
  if (iStack_80 == 0) {
    FUN_4387c400(3,7,1,DAT_4387d208 + 0x4387cc8e,0);
    uVar18 = iVar15 + 0x38;
    FUN_43902718(DAT_4387d20c + 0x4387cca0,0);
  }
  else {
    uVar10 = FUN_4355faf0(iStack_84 << 6,iStack_80);
    uVar18 = (uint)uVar10;
  }
  FUN_43b12252(auStack_78,4);
  FUN_43b12262(auStack_78,iVar21 + 0x216,uVar18);
  iVar24 = FUN_4387b520(auStack_78,iVar21 + 0x21e);
  iVar15 = FUN_4387b520(auStack_78,iVar21 + 0x222);
  uVar8 = FUN_4387b520(auStack_64,iVar21 + uVar20 * 4 + 0x7e);
  *(undefined1 *)(iVar11 + 0x88) = uVar8;
  iVar13 = FUN_4387b520(auStack_64,iVar21 + uVar20 * 4 + 0xbe);
  uVar30 = (int)((uint)*(byte *)(iVar11 + 0x88) * iVar24) >> 6 & 0xffff;
  *(char *)(iVar11 + 0x89) = (char)iVar13;
  uVar18 = iVar13 * iVar15 >> 6 & 0xffff;
  if (uVar30 < 0x100) {
    *(char *)(iVar11 + 0x88) = (char)uVar30;
  }
  else {
    *(undefined1 *)(iVar11 + 0x88) = 0xff;
  }
  if (uVar18 < 0x100) {
    *(char *)(iVar11 + 0x89) = (char)uVar18;
  }
  else {
    *(undefined1 *)(iVar11 + 0x89) = 0xff;
  }
  *(undefined1 *)(iVar11 + 0x8a) = *(undefined1 *)(iVar21 + uVar20 + 0xfe);
  *(undefined1 *)(iVar11 + 0x8b) = *(undefined1 *)(iVar21 + uVar20 + 0x10e);
  uVar9 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 0x154) * 8 + 4);
  *(undefined2 *)(iVar11 + 0x8c) = uVar9;
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x2c8) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x8e) = uVar8;
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x2d8) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x8f) = uVar8;
  iVar24 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 0x174) * 8 + 4);
  if ((uint)*(byte *)(iVar11 + 0x8f) == (uint)*(byte *)(iVar11 + 0x8e)) {
    uVar18 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)*(byte *)(iVar11 + 0x8f) -
                                        (uint)*(byte *)(iVar11 + 0x8e),(byte)(in_fpscr >> 0x16) & 3)
    ;
    fVar31 = (float)VectorSignedToFloat((iVar24 - (uint)*(ushort *)(iVar11 + 0x8c)) * 0x100,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uVar18 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
    if (0x7ff < uVar18) {
      *(undefined2 *)(iVar11 + 0x90) = 0x7ff;
      goto LAB_4387cdee;
    }
  }
  *(short *)(iVar11 + 0x90) = (short)uVar18;
LAB_4387cdee:
  uVar8 = FUN_4387b520(auStack_50,iVar27 + (uVar20 + 0x308) * 4 + 4);
  *(undefined1 *)(iVar11 + 0x92) = uVar8;
  *(undefined2 *)(iVar11 + 0x94) = *(undefined2 *)(iVar27 + uVar20 * 2 + 0xc64);
  uVar9 = FUN_4387b5dc(auStack_50,iVar27 + (uVar20 + 400) * 8 + 4);
  iVar24 = DAT_4387d210;
  *(undefined2 *)(iVar11 + 0x96) = uVar9;
  iVar15 = *(int *)(iVar28 + iVar24);
  iVar24 = iVar15 + uVar20 * 2;
  *(undefined2 *)(iVar11 + 0x86) = *(undefined2 *)(iVar15 + uVar20 * 2 + 300);
  iVar28 = iVar15 + uVar20;
  bVar1 = *(byte *)(iVar28 + 0x14c);
  *(byte *)(iVar11 + 0x98) = bVar1;
  bVar2 = *(byte *)(iVar28 + 0x15c);
  *(byte *)(iVar11 + 0x99) = bVar2;
  bVar3 = *(byte *)(iVar28 + 0x16c);
  *(byte *)(iVar11 + 0x9a) = bVar3;
  uVar10 = *(ushort *)(iVar24 + 0x19c);
  *(ushort *)(iVar11 + 0x9e) = uVar10;
  uVar4 = *(ushort *)(iVar24 + 0x1bc);
  *(ushort *)(iVar11 + 0xa0) = uVar4;
  uVar5 = *(ushort *)(iVar15 + uVar20 * 2 + 0x1dc);
  *(ushort *)(iVar11 + 0xa2) = uVar5;
  if ((uint)bVar3 == (uint)bVar2) {
    uVar18 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)bVar3 - (uint)bVar2,(byte)(in_fpscr >> 0x16) & 3);
    fVar31 = (float)VectorSignedToFloat(((uint)*(byte *)(iVar28 + 0x17c) - (uint)bVar1) * 0x100,
                                        (byte)(in_fpscr >> 0x16) & 3);
    uVar18 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  if ((uint)uVar5 == (uint)uVar4) {
    uVar30 = 0x400;
  }
  else {
    fVar32 = (float)VectorSignedToFloat((uint)uVar5 - (uint)uVar4,(byte)(in_fpscr >> 0x16) & 3);
    fVar31 = (float)VectorSignedToFloat(((uint)*(ushort *)(iVar15 + uVar20 * 2 + 0x1fc) -
                                        (uint)uVar10) * 0x100,(byte)(in_fpscr >> 0x16) & 3);
    uVar30 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
  }
  uVar10 = *(ushort *)(iVar15 + 0x404);
  if (uVar18 < 0x800) {
    *(short *)(iVar11 + 0x9c) = (short)uVar18;
  }
  else {
    *(undefined2 *)(iVar11 + 0x9c) = 0x7ff;
  }
  if (uVar30 < 0x800) {
    *(short *)(iVar11 + 0xa4) = (short)uVar30;
  }
  else {
    *(undefined2 *)(iVar11 + 0xa4) = 0x7ff;
  }
  uVar4 = *(ushort *)(iVar15 + (uVar20 + 0x244) * 2);
  uVar9 = *(undefined2 *)(iVar15 + 0x3fc);
  *(undefined2 *)(iVar11 + 0xa6) = *(undefined2 *)(iVar15 + uVar20 * 2 + 0x2dc);
  *(undefined2 *)(iVar11 + 0xa8) = *(undefined2 *)(iVar15 + uVar20 * 2 + 0x2fc);
  uVar6 = *(undefined2 *)(iVar15 + uVar20 * 2 + 0x31c);
  uVar7 = *(undefined2 *)(iVar15 + 0x3fe);
  *(undefined2 *)(iVar11 + 0x70) = uVar9;
  *(undefined2 *)(iVar11 + 0xaa) = uVar6;
  uVar9 = *(undefined2 *)(iVar15 + 0x400);
  *(undefined2 *)(iVar11 + 0x72) = uVar7;
  *(undefined2 *)(iVar11 + 0x74) = uVar9;
  if (*(char *)(iVar15 + 0x548) == '\0') {
    uVar20 = 0;
    puVar26 = (undefined1 *)(DAT_4387d220 + 0x4387d076);
    piVar25 = aiStack_e8;
    while( true ) {
      uVar18 = uVar29;
      if (uVar29 <= uVar20) break;
      *puVar26 = 1;
      iVar28 = piVar25[2];
      iVar24 = piVar25[1];
      uVar20 = uVar20 + 1;
      *(int *)(puVar26 + 4) = *piVar25;
      *(int *)(puVar26 + 8) = iVar24;
      *(int *)(puVar26 + 0xc) = iVar28;
      puVar26 = puVar26 + 0x18;
      piVar25 = piVar25 + 3;
    }
  }
  else {
    uVar20 = 0;
    uVar18 = (uint)*(byte *)(iVar15 + 0x549);
    uVar30 = (uint)*(byte *)(iVar15 + 0x54e) + (uint)*(byte *)(iVar15 + 0x54f) + 0x100;
    if (7 < uVar18) {
      uVar18 = 8;
    }
    piVar25 = (int *)(DAT_4387d214 + 0x4387cf88);
    for (; uVar20 != uVar18; uVar20 = uVar20 + 1) {
      if ((char)piVar25[-3] != '\0') {
        piVar16 = (int *)&uStack_ec;
        uVar19 = 0;
        while( true ) {
          uVar14 = uVar18;
          if (uVar29 <= uVar18) {
            uVar14 = uVar29;
          }
          if (uVar14 <= uVar19) {
            if ((uint)*(byte *)(iVar15 + 0x54b) < (uint)piVar25[1]) {
              iVar24 = piVar25[1] - (uint)*(byte *)(iVar15 + 0x54b);
            }
            else {
              iVar24 = 0;
            }
            bVar1 = *(byte *)(iVar15 + 0x54d);
            piVar25[1] = iVar24;
            if ((uint)bVar1 < (uint)piVar25[2]) {
              iVar28 = piVar25[2] - (uint)bVar1;
            }
            else {
              iVar28 = 0;
            }
            piVar25[2] = iVar28;
            if ((iVar24 == 0) && (iVar28 == 0)) {
              *(undefined1 *)(piVar25 + -3) = 0;
              piVar25[1] = 0;
              piVar25[2] = 0;
            }
            goto LAB_4387cff8;
          }
          piVar16 = piVar16 + 3;
          if (*piVar25 == *piVar16) break;
          uVar19 = uVar19 + 1;
        }
        iVar24 = aiStack_e8[uVar19 * 3 + 1];
        iVar28 = aiStack_e8[uVar19 * 3 + 2];
        piVar25[-2] = aiStack_e8[uVar19 * 3];
        piVar25[-1] = iVar24;
        *piVar25 = iVar28;
        uVar19 = (uint)*(byte *)(iVar15 + 0x54a) + piVar25[1];
        bVar1 = *(byte *)(iVar15 + 0x54c);
        if (uVar19 < uVar30) {
          piVar25[1] = uVar19;
        }
        else {
          piVar25[1] = uVar30;
        }
        uVar19 = (uint)bVar1 + piVar25[2];
        if (uVar19 < uVar30) {
          piVar25[2] = uVar19;
        }
        else {
          piVar25[2] = uVar30;
        }
      }
LAB_4387cff8:
      piVar25 = piVar25 + 6;
    }
    piVar25 = aiStack_e8 + 2;
    uVar20 = 0;
    while( true ) {
      uVar30 = uVar18;
      if (uVar29 <= uVar18) {
        uVar30 = uVar29;
      }
      if (uVar30 <= uVar20) break;
      pcVar22 = (char *)(DAT_4387d21c + 0x4387d06a);
      for (uVar30 = 0; uVar30 < uVar18; uVar30 = uVar30 + 1) {
        if ((*pcVar22 != '\0') && (*(int *)(pcVar22 + 0xc) == *piVar25)) goto LAB_4387d052;
        pcVar22 = pcVar22 + 0x18;
      }
      iVar24 = 0;
      for (uVar30 = 0; uVar30 < uVar18; uVar30 = uVar30 + 1) {
        iVar28 = DAT_4387d218 + 0x4387d02a;
        pcVar22 = (char *)(iVar28 + iVar24);
        iVar24 = iVar24 + 0x18;
        if (*pcVar22 == '\0') {
          iVar27 = iVar28 + uVar30 * 0x18;
          *(undefined1 *)(iVar28 + uVar30 * 0x18) = 1;
          iVar24 = piVar25[-2];
          iVar28 = piVar25[-1];
          iVar21 = *piVar25;
          *(undefined4 *)(iVar27 + 0x10) = 0;
          *(undefined4 *)(iVar27 + 0x14) = 0;
          *(int *)(iVar27 + 4) = iVar24;
          *(int *)(iVar27 + 8) = iVar28;
          *(int *)(iVar27 + 0xc) = iVar21;
          break;
        }
      }
LAB_4387d052:
      uVar20 = uVar20 + 1;
      piVar25 = piVar25 + 3;
    }
  }
  iVar24 = 0;
  puVar17 = (uint *)(DAT_4387d224 + 0x4387d0bc);
  for (uVar29 = 0; uVar29 != uVar18; uVar29 = uVar29 + 1) {
    if ((char)puVar17[-5] != '\0') {
      uVar5 = (ushort)puVar17[-3];
      uVar20 = (uint)uVar5;
      if (uVar20 == 0) {
        iVar28 = iVar11 + iVar24 * 2;
        *(ushort *)(iVar28 + 0xac) = uVar5;
        *(ushort *)(iVar28 + 0x76) = uVar5;
      }
      else {
        if ((uint)*(ushort *)(iVar11 + 0xaa) == (uint)*(ushort *)(iVar11 + 0xa8)) {
          *(undefined2 *)(iVar11 + (iVar24 + 0x54) * 2 + 4) = 0x400;
        }
        else {
          fVar32 = (float)VectorSignedToFloat(uVar20 * ((uint)*(ushort *)(iVar11 + 0xaa) -
                                                       (uint)*(ushort *)(iVar11 + 0xa8)),
                                              (byte)(in_fpscr >> 0x16) & 3);
          fVar31 = (float)VectorSignedToFloat(((uint)uVar4 - (uint)*(ushort *)(iVar11 + 0xa6)) *
                                              0x10000,(byte)(in_fpscr >> 0x16) & 3);
          uVar12 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
          *(short *)(iVar11 + (iVar24 + 0x54) * 2 + 4) = (short)uVar12;
        }
        if ((uint)*(ushort *)(iVar11 + 0x74) == (uint)*(ushort *)(iVar11 + 0x72)) {
          *(undefined2 *)(iVar11 + (iVar24 + 0x38) * 2 + 6) = 0x400;
        }
        else {
          fVar32 = (float)VectorSignedToFloat(uVar20 * ((uint)*(ushort *)(iVar11 + 0x74) -
                                                       (uint)*(ushort *)(iVar11 + 0x72)),
                                              (byte)(in_fpscr >> 0x16) & 3);
          fVar31 = (float)VectorSignedToFloat(((uint)uVar10 - (uint)*(ushort *)(iVar11 + 0x70)) *
                                              0x10000,(byte)(in_fpscr >> 0x16) & 3);
          uVar12 = VectorFloatToUnsigned((double)(fVar31 / fVar32) + 0.5,3);
          *(short *)(iVar11 + (iVar24 + 0x38) * 2 + 6) = (short)uVar12;
        }
      }
      fVar31 = DAT_4387d228;
      if (*(char *)(iVar15 + 0x548) != '\0') {
        uVar30 = puVar17[-1];
        uVar20 = (uint)*(byte *)(iVar15 + 0x54e);
        if (uVar30 < uVar20) {
          iVar28 = 0;
        }
        else if (uVar30 < uVar20 + 0x100) {
          iVar28 = uVar30 - uVar20;
        }
        else {
          iVar28 = 0x100;
        }
        uVar30 = *puVar17;
        if (uVar30 < uVar20) {
          iVar21 = 0;
        }
        else if (uVar30 < uVar20 + 0x100) {
          iVar21 = uVar30 - uVar20;
        }
        else {
          iVar21 = 0x100;
        }
        iVar27 = iVar11 + (iVar24 + 0x54) * 2;
        fVar33 = (float)VectorUnsignedToFloat(iVar28,(byte)(in_fpscr >> 0x16) & 3);
        fVar32 = (float)VectorUnsignedToFloat
                                  ((uint)*(ushort *)(iVar27 + 4),(byte)(in_fpscr >> 0x16) & 3);
        uVar12 = VectorFloatToUnsigned(fVar32 * fVar33 * DAT_4387d228,3);
        *(short *)(iVar27 + 4) = (short)uVar12;
        iVar28 = iVar11 + (iVar24 + 0x38) * 2;
        fVar32 = (float)VectorUnsignedToFloat
                                  ((uint)*(ushort *)(iVar28 + 6),(byte)(in_fpscr >> 0x16) & 3);
        fVar33 = (float)VectorUnsignedToFloat(iVar21,(byte)(in_fpscr >> 0x16) & 3);
        uVar12 = VectorFloatToUnsigned(fVar32 * fVar33 * fVar31,3);
        *(short *)(iVar28 + 6) = (short)uVar12;
      }
      iVar28 = iVar11 + (iVar24 + 0x54) * 2;
      uVar23 = *(ushort *)(iVar28 + 4);
      if (0x7fe < uVar23) {
        uVar23 = 0x7ff;
      }
      *(ushort *)(iVar28 + 4) = uVar23;
      iVar28 = iVar11 + (iVar24 + 0x38) * 2;
      uVar23 = *(ushort *)(iVar28 + 6);
      if (0x7fe < uVar23) {
        uVar23 = 0x7ff;
      }
      *(ushort *)(iVar28 + 6) = uVar23;
      iVar28 = iVar11 + iVar24 * 2;
      iVar24 = iVar24 + 1;
      *(short *)(iVar28 + 0xbe) = (short)puVar17[-4];
      uVar9 = *(undefined2 *)((int)puVar17 + -0xe);
      *(ushort *)(iVar28 + 0xde) = uVar5;
      *(undefined2 *)(iVar28 + 0xce) = uVar9;
    }
    puVar17 = puVar17 + 6;
  }
  *(char *)(iVar11 + 0xbc) = (char)iVar24;
  FUN_436bee34(param_1,iVar11);
  return;
}

