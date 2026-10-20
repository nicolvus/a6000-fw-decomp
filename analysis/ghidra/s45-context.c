/* S41: read-only exports. */

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


/* 4382dd78 */

undefined8 FUN_4382dd78(int param_1,short *param_2,undefined2 *param_3,undefined4 param_4)

{
  bool bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  short sVar6;
  short sVar7;
  undefined2 uVar8;
  int iVar9;
  undefined4 uVar10;
  char cVar11;
  char cVar12;
  uint uVar13;
  undefined2 *puVar14;
  int iVar15;
  undefined1 *puVar16;
  int iVar17;
  char acStack_28 [4];
  undefined2 uStack_24;
  ushort uStack_22;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  uStack_24 = SUB42(param_2,0);
  uStack_22 = (ushort)((uint)param_2 >> 0x10);
  acStack_28[0] = (char)param_1;
  acStack_28[1] = (char)((uint)param_1 >> 8);
  acStack_28[2] = (char)((uint)param_1 >> 0x10);
  acStack_28[3] = (char)((uint)param_1 >> 0x18);
  iVar9 = *(int *)(param_1 + 0x50);
  iVar17 = DAT_4382e6cc + 0x4382dd90;
  uVar13 = *(uint *)(iVar9 + 0x60);
  *(uint *)(*(int *)(iVar17 + DAT_4382e6d0) + 0x5f0) = uVar13;
  if (uVar13 == 0x55) {
    *(undefined1 *)(param_3 + 0x29) = 1;
    *(undefined1 *)(param_3 + 0x2c7) = 5;
    iVar9 = *(int *)(param_1 + 0x50);
    param_3[0x2ca] = *(undefined2 *)(iVar9 + 0x8e);
LAB_4382dece:
    param_3[0x2cb] = *(undefined2 *)(iVar9 + 0x90);
    goto LAB_4382e602;
  }
  uStack_20 = param_3;
  uStack_1c = param_4;
  if (uVar13 < 0x56) {
    if (uVar13 == 0x3f) {
      *(undefined1 *)((int)param_3 + 0x53) = 1;
      iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
      acStack_28[1] = *(byte *)(iVar9 + 1);
      acStack_28[2] = *(undefined1 *)(iVar9 + 2);
      *(uint *)(param_3 + 0x1f0) = (uint)(byte)acStack_28[1];
      *(char *)(param_3 + 0x1f2) = acStack_28[2];
    }
    else if (uVar13 < 0x40) {
      if (uVar13 == 0x3c) {
        *(undefined1 *)(param_3 + 0x25) = 1;
        iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
        iVar15 = 0;
        do {
          *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
          iVar15 = iVar15 + 2;
        } while (iVar15 != 0x10);
        param_3[0x6a] = CONCAT11(acStack_28[1],acStack_28[0]);
        param_3[0x6b] = CONCAT11(acStack_28[3],acStack_28[2]);
        param_3[0x6c] = uStack_24;
        param_3[0x6d] = uStack_22;
        param_3[0x6e] = (undefined2)uStack_20;
        param_3[0x6f] = uStack_20._2_2_;
        param_3[0x70] = (undefined2)uStack_1c;
        param_3[0x71] = uStack_1c._2_2_;
      }
      else if (uVar13 < 0x3d) {
        if (uVar13 == 8) {
          *(undefined1 *)(param_3 + 0x29) = 1;
          *(undefined1 *)(param_3 + 0x2c7) = 4;
          iVar9 = *(int *)(param_1 + 0x50);
          param_3[0x2ca] = *(undefined2 *)(iVar9 + 0x8e);
          goto LAB_4382dece;
        }
        if (uVar13 == 9) {
          *(undefined1 *)((int)param_3 + 0x4d) = 1;
          iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
          iVar15 = 0;
          do {
            *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
            iVar15 = iVar15 + 2;
          } while (iVar15 != 0xc);
          *(char *)((int)param_3 + 0x585) = acStack_28[0];
          *(char *)(param_3 + 0x2c2) = acStack_28[1];
          *(char *)((int)param_3 + 0x587) = acStack_28[2];
          *(char *)(param_3 + 0x2c3) = acStack_28[3];
          *(char *)((int)param_3 + 0x589) = (char)uStack_24;
          *(char *)(param_3 + 0x2c4) = (char)((ushort)uStack_24 >> 8);
          *(char *)((int)param_3 + 0x58b) = (char)uStack_22;
          *(char *)(param_3 + 0x2c5) = (char)(uStack_22 >> 8);
          *(char *)(param_3 + 0x2c6) = (char)((uint)uStack_20 >> 0x10);
          goto LAB_4382e602;
        }
LAB_4382e2c8:
        uVar8 = *(undefined2 *)(iVar9 + 0x66);
        *param_3 = *(undefined2 *)(iVar9 + 100);
        uVar5 = *(undefined2 *)(iVar9 + 0x68);
        param_3[1] = uVar8;
        uVar8 = *(undefined2 *)(iVar9 + 0x6a);
        param_3[2] = uVar5;
        uVar5 = *(undefined2 *)(iVar9 + 0x6c);
        param_3[3] = uVar8;
        uVar8 = *(undefined2 *)(iVar9 + 0x6e);
        param_3[4] = uVar5;
        uVar5 = *(undefined2 *)(iVar9 + 0x70);
        param_3[7] = uVar8;
        uVar8 = *(undefined2 *)(iVar9 + 0x72);
        param_3[8] = uVar5;
        uVar5 = *(undefined2 *)(iVar9 + 0x74);
        param_3[9] = uVar8;
        param_3[10] = uVar5;
        *(undefined1 *)((int)param_3 + 0x19) = *(undefined1 *)(iVar9 + 0x7c);
        *(undefined1 *)((int)param_3 + 0x1b) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x7d);
        *(undefined1 *)(param_3 + 0xe) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x7e);
        *(undefined1 *)((int)param_3 + 0x1d) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x7f);
        *(undefined1 *)(param_3 + 0xf) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x80);
        *(undefined1 *)((int)param_3 + 0x1f) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x81);
        *(undefined1 *)(param_3 + 0x10) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x82);
        *(undefined1 *)((int)param_3 + 0x21) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x83);
        *(undefined1 *)(param_3 + 0x11) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x84);
        iVar9 = *(int *)(param_1 + 0x50);
        param_3[0x1c] = *(undefined2 *)(iVar9 + 0x9e);
        *(undefined1 *)(param_3 + 0x1d) = *(undefined1 *)(iVar9 + 0xa0);
        *(undefined1 *)((int)param_3 + 0x23) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x92);
        *(undefined1 *)(param_3 + 0x12) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x93);
        *(undefined1 *)(param_3 + 0x19) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x8b);
        *(undefined1 *)(param_3 + 0x18) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x87);
        iVar9 = *(int *)(param_1 + 0x50);
        param_3[5] = *(undefined2 *)(iVar9 + 0x76);
        *(undefined1 *)((int)param_3 + 0x31) = *(undefined1 *)(iVar9 + 0x88);
        iVar9 = *(int *)(param_1 + 0x50);
        param_3[6] = *(undefined2 *)(iVar9 + 0x78);
        *(undefined1 *)((int)param_3 + 0x35) = *(undefined1 *)(iVar9 + 0x8d);
        *(undefined1 *)(param_3 + 0x1b) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x94);
        *(undefined1 *)((int)param_3 + 0x37) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0x95);
        *(undefined1 *)((int)param_3 + 0x3b) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0xa1);
        *(undefined1 *)(param_3 + 0x1e) = *(undefined1 *)(*(int *)(param_1 + 0x50) + 0xa2);
        *(undefined1 *)((int)param_3 + 0x6b) = 0;
        *(undefined1 *)(param_3 + 0x36) = 0;
        *(undefined1 *)(param_3 + 0x34) = 0;
        cVar12 = *(char *)(*(int *)(param_1 + 0x50) + 0x7b);
        *(char *)(param_3 + 0xc) = cVar12;
        if (cVar12 != '\0') {
          *(undefined1 *)(param_3 + 0xe) = 1;
          uVar8 = FUN_436ef8f8();
          *(undefined1 *)(param_3 + 0xf) = 1;
          param_3[4] = 0x1000;
          *(undefined1 *)((int)param_3 + 0x33) = 1;
          param_3[2] = uVar8;
        }
        cVar12 = *(char *)(*(int *)(param_1 + 0x50) + 0x8c);
        if ((char)param_2[4] == '\x0f') {
          if ((*(int *)(param_2 + 0x27c) == 2) && (**(char **)(iVar17 + DAT_4382e6d4) != '\0')) {
            *(undefined1 *)(param_3 + 0x10) = 1;
            param_3[8] = param_2[0x380];
          }
          else {
            *(undefined1 *)(param_3 + 0x10) = 1;
            sVar6 = param_2[0x214];
            *(undefined1 *)(param_3 + 0x11) = 1;
            sVar7 = param_2[0x215];
            param_3[8] = sVar6;
            param_3[10] = sVar7;
          }
          cVar12 = '\x01';
          *(undefined1 *)((int)param_3 + 0x1f) = 1;
          uVar8 = FUN_43a12b94();
          *(undefined1 *)((int)param_3 + 0x21) = 1;
          param_3[7] = uVar8;
          uVar8 = FUN_43a12bc8();
          param_3[9] = uVar8;
        }
        if (*param_2 == 0x343) {
          *(undefined1 *)(param_3 + 0x10) = 1;
          sVar6 = param_2[0x214];
          *(undefined1 *)(param_3 + 0x11) = 1;
          sVar7 = param_2[0x215];
          param_3[8] = sVar6;
          param_3[10] = sVar7;
        }
        uVar10 = 0;
        *(undefined1 *)(param_3 + 0x1a) = 0;
        iVar9 = *(int *)(param_2 + 0x27e);
        *(undefined4 *)(param_3 + 0x16) = 0;
        if (iVar9 == 2) {
          *(char *)(param_3 + 0x1a) = cVar12;
          *(undefined4 *)(param_3 + 0x14) = 0;
        }
        else {
          cVar11 = *(char *)((int)param_3 + 0x71);
          if (cVar11 == '\x01') {
            uVar10 = 2;
            if (cVar12 == '\x01') {
LAB_4382e4b6:
              *(undefined4 *)(param_3 + 0x14) = uVar10;
            }
            else {
              *(undefined4 *)(param_3 + 0x14) = 1;
LAB_4382e4c6:
              cVar11 = (char)uVar10;
            }
          }
          else if (cVar11 == '\0') {
            if (cVar12 != '\x01') goto LAB_4382e4b6;
            *(undefined4 *)(param_3 + 0x14) = 2;
            cVar11 = '\x01';
          }
          else if ((cVar11 != '\x02') || ((char)param_2[0x2a6] != '\0')) {
            *(undefined4 *)(param_3 + 0x14) = 0;
            goto LAB_4382e4c6;
          }
          *(char *)((int)param_3 + 0x71) = cVar11;
        }
        if (*(char *)(*(int *)(param_1 + 0x50) + 0x7a) == '\0') {
          *(undefined1 *)(param_3 + 0xb) = 0;
          cVar12 = '\0';
LAB_4382e4f4:
          *(char *)((int)param_3 + 0x17) = cVar12;
        }
        else {
          *(undefined1 *)(param_3 + 0xb) = 1;
          cVar12 = *(char *)(*(int *)(param_1 + 0x50) + 0x7a);
          if ((cVar12 == '\x02') || ((cVar12 != '\x03' && (cVar12 == '\x01')))) goto LAB_4382e4f4;
          *(undefined1 *)((int)param_3 + 0x17) = 0;
        }
        bVar1 = *(char *)(*(int *)(param_1 + 0x50) + 0x8a) != '\0';
        *(bool *)(param_3 + 0x20) = bVar1;
        *(bool *)((int)param_3 + 0x41) = bVar1;
        *(bool *)(param_3 + 0x21) = bVar1;
        *(bool *)((int)param_3 + 0x43) = bVar1;
        *(bool *)((int)param_3 + 0x45) = bVar1;
        *(bool *)(param_3 + 0x23) = bVar1;
        *(bool *)((int)param_3 + 0x47) = bVar1;
        *(bool *)(param_3 + 0x24) = bVar1;
        *(bool *)((int)param_3 + 0x49) = bVar1;
        if ((*(char *)(*(int *)(iVar17 + DAT_4382e6d8) + 0x42) != '\0') &&
           ((char)param_2[0x2b7] != '\0')) {
          uVar8 = FUN_436ef8f8();
          *(undefined1 *)(param_3 + 0xe) = 1;
          param_3[2] = uVar8;
          if ((char)param_2[0x2b8] == '\0') {
            *(undefined1 *)((int)param_3 + 0x1b) = 1;
            sVar6 = param_2[0x2b9];
            *(undefined1 *)((int)param_3 + 0x1d) = 1;
            sVar7 = param_2[0x2ba];
            param_3[1] = sVar6;
            param_3[3] = sVar7;
          }
          if (*(char *)((int)param_2 + 0x56f) == '\x01') {
            *(undefined1 *)((int)param_3 + 0x6b) = 1;
            *(undefined1 *)(param_3 + 0x36) = 1;
          }
          *(undefined1 *)(param_3 + 0x34) = 2;
          *(undefined1 *)(param_3 + 0x20) = 1;
          *(undefined1 *)((int)param_3 + 0x41) = 1;
          *(undefined1 *)(param_3 + 0x21) = 1;
          *(undefined1 *)((int)param_3 + 0x43) = 1;
          *(undefined1 *)((int)param_3 + 0x45) = 1;
          *(undefined1 *)(param_3 + 0x23) = 1;
          *(undefined1 *)((int)param_3 + 0x47) = 1;
          *(undefined1 *)(param_3 + 0x24) = 1;
        }
        *(undefined1 *)(param_3 + 0x29) = 0;
        *(undefined1 *)((int)param_3 + 0x51) = 0;
        *(undefined1 *)(param_3 + 0x27) = 0;
        *(undefined1 *)(param_3 + 0x28) = 0;
        *(undefined1 *)((int)param_3 + 0x4f) = 0;
        *(undefined1 *)(param_3 + 0x25) = 0;
        *(undefined1 *)((int)param_3 + 0x4b) = 0;
        *(undefined1 *)(param_3 + 0x26) = 0;
        *(undefined1 *)((int)param_3 + 0x4d) = 0;
        *(undefined1 *)((int)param_3 + 0x53) = 0;
        *(undefined1 *)(param_3 + 0x2a) = 0;
        *(undefined1 *)((int)param_3 + 0x55) = 0;
        *(undefined1 *)(param_3 + 0x2b) = 0;
        *(undefined1 *)((int)param_3 + 0x5b) = 0;
        *(undefined1 *)(param_3 + 0x2e) = 0;
        *(undefined1 *)(param_3 + 0x30) = 0;
        *(undefined1 *)((int)param_3 + 0x61) = 0;
        param_3[0x31] = 0;
        *(undefined1 *)(param_3 + 0x32) = 0;
        *(undefined1 *)((int)param_3 + 0x57) = 0;
        *(undefined1 *)(param_3 + 0x2c) = 0;
        *(undefined1 *)((int)param_3 + 0x59) = 0;
        *(undefined1 *)(param_3 + 0x2d) = 0;
        *(undefined1 *)((int)param_3 + 0x5d) = 0;
        *(undefined1 *)(param_3 + 0x2e5) = 0;
        *(undefined1 *)((int)param_3 + 0x5cd) = 0;
        *(undefined1 *)(param_3 + 0x2f) = 0;
        *(undefined1 *)(param_3 + 0x2f2) = 0;
        *(undefined1 *)((int)param_3 + 0x5e7) = 0;
      }
      else if (uVar13 == 0x3d) {
        *(undefined1 *)(param_3 + 0x26) = 1;
      }
      else {
        if (uVar13 != 0x3e) goto LAB_4382e2c8;
        *(undefined1 *)((int)param_3 + 0x4f) = 1;
      }
    }
    else if (uVar13 == 0x43) {
      *(undefined1 *)(param_3 + 0x27) = 1;
      puVar14 = *(undefined2 **)(*(int *)(param_1 + 0x50) + 8);
      uVar8 = puVar14[7];
      uVar5 = *puVar14;
      param_3[0x2bf] = puVar14[6];
      param_3[0x2c0] = uVar8;
      param_3[0x2bd] = uVar5;
    }
    else if (uVar13 < 0x44) {
      if (uVar13 == 0x40) {
        *(undefined1 *)(param_3 + 0x27) = 1;
        puVar14 = *(undefined2 **)(*(int *)(param_1 + 0x50) + 8);
        uVar8 = puVar14[2];
        uVar5 = puVar14[3];
        uVar4 = *puVar14;
        param_3[0x2bf] = puVar14[1];
        param_3[0x2c0] = uVar8;
        param_3[0x2bd] = uVar4;
        param_3[0x2c1] = uVar5;
      }
      else {
        if (uVar13 != 0x41) goto LAB_4382e2c8;
        *(undefined1 *)(param_3 + 0x28) = 1;
        iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
        iVar15 = 0;
        do {
          *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
          iVar15 = iVar15 + 2;
        } while (iVar15 != 0xc);
        param_3[0x3d] = CONCAT11(acStack_28[1],acStack_28[0]);
        param_3[0x48] = CONCAT11(acStack_28[3],acStack_28[2]);
        param_3[0x49] = uStack_24;
        param_3[0x46] = uStack_22;
        param_3[0x47] = (undefined2)uStack_20;
        param_3[0x4b] = uStack_20._2_2_;
      }
    }
    else if (uVar13 == 0x49) {
      *(undefined1 *)((int)param_3 + 0x55) = 1;
    }
    else if (uVar13 == 0x4d) {
      *(undefined1 *)(param_3 + 0x2a) = 1;
      *(undefined1 *)(param_3 + 0x1f2) = 0;
      iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
      uStack_24 = *(undefined2 *)(iVar9 + 4);
      uStack_22 = *(ushort *)(iVar9 + 6);
      param_3[0x1e4] = uStack_24;
      *(uint *)(param_3 + 0x1f0) = (uint)uStack_22;
    }
    else {
      if (uVar13 != 0x46) goto LAB_4382e2c8;
      puVar14 = *(undefined2 **)(iVar9 + 8);
      acStack_28[0] = (char)*puVar14;
      acStack_28[1] = (char)((ushort)*puVar14 >> 8);
      uVar8 = puVar14[1];
      acStack_28[2] = (char)uVar8;
      acStack_28[3] = (char)((ushort)uVar8 >> 8);
      uStack_24 = puVar14[2];
      *(char *)(param_3 + 0x2c7) = acStack_28[0];
      param_3[0x2ca] = uVar8;
      param_3[0x2cb] = uStack_24;
      if (acStack_28[0] == -1) {
        *(undefined1 *)(param_3 + 0x29) = 0;
        *(undefined1 *)((int)param_3 + 0x51) = 1;
        *(undefined1 *)(param_3 + 0x2cc) = *(undefined1 *)(*(int *)(param_1 + 0x1c) + 7);
        *(undefined1 *)((int)param_3 + 0x599) = *(undefined1 *)(*(int *)(param_1 + 0x1c) + 8);
      }
      else {
        *(undefined1 *)(param_3 + 0x29) = 1;
        *(undefined1 *)((int)param_3 + 0x51) = 0;
      }
    }
  }
  else if (uVar13 == 0x99) {
LAB_4382e16a:
    *(undefined1 *)(param_3 + 0x2d) = 1;
  }
  else if (uVar13 < 0x9a) {
    if (uVar13 == 0x82) {
      *(undefined1 *)(param_3 + 0x2b) = 1;
      puVar16 = *(undefined1 **)(*(int *)(param_1 + 0x50) + 8);
      uVar2 = puVar16[2];
      uVar3 = *puVar16;
      *(undefined1 *)((int)param_3 + 0x59b) = puVar16[1];
      *(undefined1 *)(param_3 + 0x2ce) = uVar2;
      *(undefined1 *)(param_3 + 0x2cd) = uVar3;
    }
    else if (uVar13 < 0x83) {
      if (uVar13 == 0x80) {
        *(undefined1 *)(param_3 + 0x1a) = 1;
        param_3[3] = 0x1000;
      }
      else {
        if (uVar13 != 0x81) goto LAB_4382e2c8;
        *(undefined1 *)(param_3 + 0x1a) = 1;
        param_3[3] = param_2[0xcc];
      }
      *(undefined1 *)((int)param_3 + 0x1d) = 1;
      *(undefined1 *)(param_3 + 0x23) = 1;
    }
    else if (uVar13 == 0x91) {
      *(undefined1 *)((int)param_3 + 0x57) = 1;
    }
    else if (uVar13 == 0x93) {
      if (*(char *)((int)param_3 + 0x59) == '\0') {
        uVar8 = **(undefined2 **)(iVar9 + 8);
        acStack_28[0] = (char)uVar8;
        acStack_28[1] = (char)((ushort)uVar8 >> 8);
        param_3[0x2e2] = uVar8;
      }
      *(undefined1 *)((int)param_3 + 0x59) = 1;
    }
    else {
      if (uVar13 != 0x83) goto LAB_4382e2c8;
      *(undefined1 *)((int)param_3 + 0x5b) = 1;
      puVar14 = *(undefined2 **)(*(int *)(param_1 + 0x50) + 8);
      uVar8 = *puVar14;
      param_3[0x2e4] = puVar14[1];
      param_3[0x2e3] = uVar8;
    }
  }
  else if (uVar13 == 0xb7) {
    *(undefined1 *)(param_3 + 0x2e) = 1;
    iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
    iVar15 = 0;
    do {
      *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
      iVar15 = iVar15 + 2;
    } while (iVar15 != 0x10);
    *(char *)(param_3 + 0x590) = acStack_28[0];
    if (acStack_28[0] == '\0') {
      *(char *)((int)param_3 + 0xb21) = acStack_28[1];
LAB_4382e292:
      *(undefined1 *)(param_3 + 0x591) = 0;
    }
    else {
      if (acStack_28[0] != '\x01') {
        *(undefined1 *)((int)param_3 + 0xb21) = 0;
        goto LAB_4382e292;
      }
      *(undefined1 *)((int)param_3 + 0xb21) = 0;
      *(char *)(param_3 + 0x591) = acStack_28[1];
    }
    *(char *)((int)param_3 + 0xb23) = acStack_28[2];
    *(char *)(param_3 + 0x592) = (char)uStack_24;
    param_3[0x593] = uStack_22;
    param_3[0x594] = (undefined2)uStack_20;
    param_3[0x595] = uStack_20._2_2_;
    param_3[0x596] = (undefined2)uStack_1c;
  }
  else if (uVar13 < 0xb8) {
    if (uVar13 == 0x9a) goto LAB_4382e16a;
    if (uVar13 != 0xb5) goto LAB_4382e2c8;
    if (*(char *)((int)param_3 + 0x5d) == '\0') {
      *(undefined1 *)(param_3 + 0x2e5) = 1;
    }
    *(undefined1 *)((int)param_3 + 0x5d) = 1;
    iVar9 = *(int *)(param_1 + 0x50);
    uVar8 = *(undefined2 *)(iVar9 + 0x98);
    param_3[0x2e7] = *(undefined2 *)(iVar9 + 0x96);
    uVar5 = *(undefined2 *)(iVar9 + 0x6e);
    param_3[0x2e8] = uVar8;
    param_3[7] = uVar5;
    *(undefined1 *)((int)param_3 + 0x1f) = *(undefined1 *)(iVar9 + 0x81);
    iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
    iVar15 = 0;
    do {
      *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
      iVar15 = iVar15 + 2;
    } while (iVar15 != 0x10);
    param_3[0x2eb] = uStack_22;
    param_3[0x2ec] = (undefined2)uStack_20;
    param_3[0x2ed] = uStack_20._2_2_;
    param_3[0x2ee] = (undefined2)uStack_1c;
    param_3[0x2ef] = uStack_1c._2_2_;
  }
  else if (uVar13 == 0xd0) {
    *(undefined1 *)(param_3 + 0x2c) = 1;
    iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
    iVar15 = 0;
    do {
      *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
      iVar15 = iVar15 + 2;
    } while (iVar15 != 10);
    param_3[0x598] = CONCAT11(acStack_28[1],acStack_28[0]);
    param_3[0x599] = CONCAT11(acStack_28[3],acStack_28[2]);
    param_3[0x59a] = uStack_24;
    param_3[0x59b] = uStack_22;
    param_3[0x59c] = (undefined2)uStack_20;
  }
  else if (uVar13 == 0xe9) {
    *(undefined1 *)((int)param_3 + 0x4b) = 1;
    iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
    iVar15 = 0;
    do {
      *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
      iVar15 = iVar15 + 2;
    } while (iVar15 != 0x10);
    *(uint *)(param_3 + 0x602) = (uint)CONCAT11(acStack_28[1],acStack_28[0]);
    param_3[0x604] = CONCAT11(acStack_28[3],acStack_28[2]);
    param_3[0x605] = uStack_24;
    param_3[0x606] = uStack_22;
    param_3[0x607] = (undefined2)uStack_20;
    param_3[0x608] = uStack_20._2_2_;
  }
  else {
    if (uVar13 != 0xba) goto LAB_4382e2c8;
    if (*(char *)(param_3 + 0x2f) == '\0') {
      *(undefined1 *)(param_3 + 0x2f2) = 1;
    }
    *(undefined1 *)(param_3 + 0x2f) = 1;
    iVar9 = *(int *)(param_1 + 0x50);
    uVar8 = *(undefined2 *)(iVar9 + 0x98);
    param_3[0x2f4] = *(undefined2 *)(iVar9 + 0x96);
    uVar5 = *(undefined2 *)(iVar9 + 0x6e);
    param_3[0x2f5] = uVar8;
    param_3[7] = uVar5;
    *(undefined1 *)((int)param_3 + 0x1f) = *(undefined1 *)(iVar9 + 0x81);
    iVar9 = *(int *)(*(int *)(param_1 + 0x50) + 8);
    iVar15 = 0;
    do {
      *(undefined2 *)(acStack_28 + iVar15) = *(undefined2 *)(iVar9 + iVar15);
      iVar15 = iVar15 + 2;
    } while (iVar15 != 0xc);
    param_3[0x2f8] = uStack_22;
    param_3[0x2f9] = (undefined2)uStack_20;
    param_3[0x2fa] = uStack_20._2_2_;
  }
LAB_4382e602:
  if ((*(char *)(*(int *)(iVar17 + DAT_4382e6dc) + 0xdf) != '\0') &&
     (*(int *)(*(int *)(param_1 + 0x50) + 0x60) == 0x3c)) {
    param_2[0x1ec] = 5;
    param_2[0x1ed] = 0;
  }
  if (*(char *)(*(int *)(param_1 + 0x50) + 0x85) == '\x01') {
    switch(*(undefined1 *)(*(int *)(param_1 + 0x50) + 0x86)) {
    case 0:
      uVar10 = 0;
      break;
    case 1:
      uVar10 = 1;
      break;
    case 2:
      uVar10 = 2;
      break;
    case 3:
      uVar10 = 3;
      break;
    default:
      goto switchD_4382e62c_default;
    }
    *(undefined4 *)(param_2 + 0x1ec) = uVar10;
  }
switchD_4382e62c_default:
  iVar9 = *(int *)(iVar17 + DAT_4382e6e0);
  if ((*(byte *)(iVar9 + 0x102) & 2) != 0) {
    *(undefined1 *)(param_3 + 0xe) = 0;
    *(undefined1 *)(param_3 + 0x10) = 0;
    *(undefined1 *)(param_3 + 0xf) = 0;
    *(undefined1 *)(param_3 + 0x11) = 0;
    *(undefined1 *)((int)param_3 + 0x1b) = 0;
    *(undefined1 *)((int)param_3 + 0x1f) = 0;
    *(undefined1 *)((int)param_3 + 0x1d) = 0;
    *(undefined1 *)((int)param_3 + 0x21) = 0;
  }
  if ((*(byte *)(iVar9 + 0x102) & 4) != 0) {
    *(undefined1 *)(param_3 + 0xe) = 1;
    *(undefined1 *)(param_3 + 0x10) = 1;
    *(undefined1 *)(param_3 + 0xf) = 1;
    *(undefined1 *)(param_3 + 0x11) = 1;
    param_3[2] = 0x1400;
    param_3[8] = 0x1400;
    param_3[4] = 0x1000;
    param_3[10] = 0x1000;
  }
  if ((*(byte *)(iVar9 + 0x102) & 8) != 0) {
    *(undefined1 *)((int)param_3 + 0x1b) = 1;
    *(undefined1 *)((int)param_3 + 0x1f) = 1;
    param_3[1] = 0x1555;
    param_3[7] = 0x1555;
  }
  if ((*(byte *)(iVar9 + 0x102) & 0x10) != 0) {
    *(undefined1 *)((int)param_3 + 0x1d) = 1;
    *(undefined1 *)((int)param_3 + 0x21) = 1;
    param_3[3] = 0x1000;
    param_3[9] = 0x1000;
  }
  return CONCAT26(uStack_22,
                  CONCAT24(uStack_24,
                           CONCAT13(acStack_28[3],
                                    CONCAT12(acStack_28[2],CONCAT11(acStack_28[1],acStack_28[0])))))
  ;
}


/* 43859944 */

void FUN_43859944(int param_1,int param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_438599d0 + 0x43859956;
  iVar3 = *(int *)(iVar4 + DAT_438599d4);
  if (*(char *)(iVar3 + 5) != '\x01') {
    *(int *)(DAT_438599d8 + 0x43859962) = param_1;
    if (param_2 != 0) {
      bVar1 = *(byte *)(iVar3 + 0xf);
      if ((bVar1 & 0x10) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599dc),param_2 + 700,0x6b0);
      }
      if ((bVar1 & 0x20) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e0),param_2 + 4,0x2b8);
      }
      if ((bVar1 & 0x40) != 0) {
        FUN_439c5320(*(undefined4 *)(iVar4 + DAT_438599e4),param_2 + 0x96c,0x1128);
      }
    }
    if (param_3 != 0) {
      FUN_43afa660(DAT_438599e8 + 0x438599b6,param_3);
    }
    if (param_1 < 0x40) {
      uVar2 = 0x40;
    }
    else {
      uVar2 = 0x80;
    }
    FUN_43859710(uVar2);
    return;
  }
  return;
}


/* 436d6f6c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 candidate_436d6f6c(int param_1,ushort *param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  undefined1 uVar4;
  byte bVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  ushort *puVar10;
  byte bVar11;
  int iVar12;
  short sVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  undefined4 in_stack_ffffffa0;
  undefined2 uVar20;
  
  iVar7 = _DAT_436d72a0;
  uVar20 = (undefined2)((uint)in_stack_ffffffa0 >> 0x10);
  iVar18 = _DAT_436d7298 + 0x436d6f84;
  if (*(int *)(param_1 + 0x170) == 0x11) {
    iVar7 = FUN_436d9f70(param_1 + 0xfc,1);
    if (iVar7 != 0) {
      FUN_436d6738(0xbc,0,3,_DAT_436d729c + 0x436d6fa6,*(undefined4 *)(param_1 + 0x170));
    }
    return 2;
  }
  uVar1 = param_2[2];
  uVar17 = (uint)uVar1;
  uVar2 = *param_2;
  uVar16 = (uint)uVar2;
  uVar3 = param_2[3];
  uVar4 = *(undefined1 *)((int)param_2 + 9);
  *(uint *)(param_1 + 0x3a8) = uVar17;
  iVar8 = *(int *)(iVar18 + _DAT_436d72a4);
  iVar19 = *(int *)(iVar18 + _DAT_436d72a8);
  iVar12 = *(int *)(iVar18 + _DAT_436d72ac);
  iVar14 = *(int *)(iVar18 + _DAT_436d72b0);
  iVar15 = *(int *)(iVar18 + _DAT_436d72b4);
  *(char *)(*(int *)(iVar18 + iVar7) + 2) = (char)uVar1;
  bVar11 = (byte)(uVar1 >> 8) & 0xf;
  *(byte *)(iVar8 + 2) = *(byte *)(iVar8 + 2) & 0xf0 | bVar11;
  bVar5 = (byte)(uVar2 >> 8) & 0x3f;
  *(char *)(iVar19 + 2) = (char)uVar2;
  bVar6 = (byte)(uVar3 >> 8) & 0xf;
  *(byte *)(iVar12 + 2) = *(byte *)(iVar12 + 2) & 0xc0 | bVar5;
  *(char *)(iVar14 + 2) = (char)uVar3;
  *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar6;
  if (*(char *)(*(int *)(iVar18 + _DAT_436d72b8) + 0x7f) != -1) {
    iVar15 = *(int *)(iVar18 + _DAT_436d72c0);
    iVar8 = *(int *)(iVar18 + _DAT_436d72c4);
    iVar7 = *(int *)(iVar18 + _DAT_436d72c8);
    iVar12 = *(int *)(iVar18 + _DAT_436d72cc);
    iVar14 = *(int *)(iVar18 + _DAT_436d72d0);
    *(char *)(*(int *)(iVar18 + _DAT_436d72bc) + 2) = (char)uVar1;
    *(byte *)(iVar15 + 2) = *(byte *)(iVar15 + 2) & 0xf0 | bVar11;
    *(char *)(iVar8 + 2) = (char)uVar2;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xc0 | bVar5;
    *(char *)(iVar12 + 2) = (char)uVar3;
    *(byte *)(iVar14 + 2) = *(byte *)(iVar14 + 2) & 0xf0 | bVar6;
  }
  iVar7 = FUN_436d8a74(param_1 + 0x18,*(undefined4 *)(param_1 + 0x170));
  if (iVar7 != 0) {
    *(ushort *)(param_1 + 0x10) = uVar1;
    *(ushort *)(param_1 + 0x12) = uVar2;
  }
  iVar7 = *(int *)(iVar18 + _DAT_436d72d4);
  switch(uVar4) {
  case 0:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) & 0x7f;
    break;
  case 1:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    uVar9 = uVar16 * (*(uint *)(iVar7 + 4) >> 8);
    goto code_r0x436d719e;
  case 2:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xbf;
    *(char *)(*(int *)(iVar18 + _UNK_436d72d8) + 2) = (char)param_2[4];
    *(char *)(*(int *)(iVar18 + _UNK_436d72dc) + 2) = (char)param_2[10];
    iVar7 = FUN_436d6f34(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
    sVar13 = FUN_4355faf0(*(uint *)(iVar7 + 4) >> 8,1000);
    sVar13 = uVar2 * sVar13 + 1 + (short)(((byte)param_2[10] + 1) * 0x26aa >> 0x10);
    goto code_r0x436d71e0;
  case 3:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 4;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x80;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x10;
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
    uVar9 = (uint)param_2[8];
code_r0x436d719e:
    sVar13 = FUN_4355faf0(uVar9,1000);
    *(short *)(param_1 + 0x3a0) = sVar13 + 1;
    goto code_r0x436d71e4;
  case 4:
    *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xfb;
    bVar11 = *(byte *)(iVar7 + 2) | 0x80;
    break;
  default:
    return 1;
  }
  *(byte *)(iVar7 + 2) = bVar11;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) & 0xef;
  *(byte *)(iVar7 + 2) = *(byte *)(iVar7 + 2) | 0x40;
  puVar10 = (ushort *)
            func_0x436d6f50(*(undefined4 *)(param_1 + 0x294),*(undefined1 *)(param_1 + 0x17c));
  sVar13 = (*puVar10 >> 8) + 1;
code_r0x436d71e0:
  *(short *)(param_1 + 0x3a0) = sVar13;
code_r0x436d71e4:
  iVar18 = param_1 + 0xfc;
  FUN_43ad9a40(iVar18,uVar17,uVar16,uVar3,uVar4,0);
  FUN_43ad99d4(iVar18,*(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x150),
               *(undefined4 *)(param_1 + 0x154),*(undefined4 *)(param_1 + 0x158),
               *(undefined4 *)(param_1 + 0x15c),
               CONCAT22(uVar20,(short)*(undefined4 *)(param_1 + 0x160)));
  iVar7 = FUN_436d9f70(iVar18,1);
  if (iVar7 != 0) {
    iVar7 = *(int *)(param_1 + 0x174);
    if ((iVar7 != *(int *)(param_1 + 0x170)) || (*(int *)(param_1 + 0x178) != iVar7)) {
      FUN_436d6738(0xbc,0,3,&UNK_436d7246 + _UNK_436d72e0,*(int *)(param_1 + 0x178),iVar7,
                   *(int *)(param_1 + 0x170),uVar17,uVar16,uVar3,uVar4);
    }
  }
  iVar7 = FUN_436d9f70(iVar18,8);
  if (iVar7 != 0) {
    FUN_436d6738(0xbc,0,3,&UNK_436d7284 + _UNK_436d72e4,*(undefined4 *)(param_1 + 0x178),
                 *(undefined4 *)(param_1 + 0x174),*(undefined4 *)(param_1 + 0x170),uVar17,uVar16,
                 uVar3,uVar4);
  }
  return 0;
}

