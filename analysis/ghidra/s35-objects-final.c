/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "436cf818" */

void FUN_436cf818(void)

{
  FUN_43ad690c(0xfc000000,1);
  FUN_436cf0c8(9,0x436cf955);
  FUN_436cf0c8(10,&LAB_436cf780_1);
  return;
}


/* query "436cfd20" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cfd20(undefined4 param_1)

{
  _DAT_fc01f154 = param_1;
  return;
}


/* query "436cf7dc" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf7dc(undefined4 param_1)

{
  _DAT_fc0a0014 = param_1;
  return;
}


/* query "436cf7e8" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_436cf7e8(void)

{
  return _DAT_fc0a0018;
}


/* query "436cfae0" */

void FUN_436cfae0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = FUN_43ad68e0();
  iVar2 = 0;
  FUN_43560e1c(0x16);
  do {
    if ((&DAT_43e7ec2c)[iVar2 * 2] == 0) {
      if (iVar2 < 4) {
        (&DAT_43e7ec28)[iVar2 * 2] = uVar1;
        (&DAT_43e7ec2c)[iVar2 * 2] = param_2;
        DAT_43e7ec4c = DAT_43e7ec4c & ~uVar1;
        FUN_436cf844(uVar1);
        FUN_43560e38(0x16);
        if ((*(byte *)(DAT_44024944 + 0xf) & 1) == 0) {
          return;
        }
        FUN_436cf6d4(0x165,1,1,&DAT_43c9208a,param_1,iVar2,uVar1,param_4);
        FUN_43902718(s_setComplexCallBack_cond__x_No__d_43c92095,param_1,iVar2,uVar1);
        return;
      }
      break;
    }
    iVar2 = iVar2 + 1;
  } while (iVar2 != 4);
  FUN_436cf6d4(0x165,1,1,&DAT_43c92046,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,DAT_43e7ec44);
  FUN_43902718(s_DfeCoreErr_setComplexCallBack_Ca_43c92051,DAT_43e7ec2c,DAT_43e7ec34,DAT_43e7ec3c,
               DAT_43e7ec44);
  return;
}


/* query "43ad68e0" */

uint FUN_43ad68e0(uint param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((param_1 & 1) != 0) {
    uVar1 = 0x80000;
  }
  if ((param_1 & 2) != 0) {
    uVar1 = uVar1 | 0x100000;
  }
  if ((param_1 & 0x10) != 0) {
    uVar1 = uVar1 | 0x1000000;
  }
  if ((param_1 & 0x20) != 0) {
    uVar1 = uVar1 | 0x2000000;
  }
  return uVar1;
}


/* query "438267f2" */

void FUN_4382678c(undefined1 *param_1,undefined1 *param_2,int *param_3)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  byte bVar7;
  undefined1 uVar8;
  ushort uVar9;
  undefined2 uVar10;
  undefined4 uVar11;
  uint uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  uint uVar16;
  uint uVar17;
  undefined4 uVar18;
  ushort *puVar19;
  int iVar20;
  char cVar21;
  char cVar22;
  int iVar23;
  uint uVar24;
  undefined2 *puVar25;
  short sVar26;
  undefined2 *puStack_3c;
  
  iVar20 = DAT_44021084;
  if (((*(byte *)(DAT_44021084 + 0x202) & 1) == 0) || (*(char *)(*param_3 + 400) == '\x02')) {
    *param_1 = 0;
    if (0x100 < *(ushort *)(*param_3 + 0x182)) {
      FUN_437a6358(0x9d);
    }
    iVar23 = *param_3;
    uVar11 = FUN_43b065c2(0x100,(int)*(short *)(iVar23 + 0x182));
    uVar9 = FUN_43b065a8(0,uVar11);
    uVar12 = (uint)uVar9;
    if (*(char *)(iVar23 + 0x18e) == '\0') {
      bVar7 = FUN_43b06c5e(*(byte *)(iVar20 + 0x230) * uVar12,0x100);
LAB_4382682e:
      uVar12 = (uint)bVar7;
    }
    else {
      puVar19 = (ushort *)0x43bf381e;
      iVar20 = 1;
      do {
        iVar23 = iVar20;
        if ((puVar19[1] <= uVar12) && (uVar12 < puVar19[2])) {
          bVar7 = FUN_43aebbd0();
          goto LAB_4382682e;
        }
        iVar20 = iVar23 + 1;
        puVar19 = puVar19 + 1;
      } while (iVar20 != 9);
      uVar12 = iVar23 + 0x56;
    }
    iVar20 = param_3[5];
    *(undefined2 *)(iVar20 + 0x2a) = *(undefined2 *)(*param_3 + 0x182);
  }
  else {
    uVar11 = FUN_43aec054();
    uVar13 = FUN_43aec04e();
    iVar23 = *param_3;
    sVar1 = *(short *)(iVar23 + 0x166);
    sVar2 = *(short *)(iVar23 + 0x164);
    sVar26 = *(short *)(iVar23 + 0x162) + *(short *)(iVar23 + 0x160);
    sVar3 = *(short *)(iVar23 + 0x16a);
    sVar4 = *(short *)(iVar23 + 0x16e);
    sVar5 = *(short *)(iVar23 + 0x16c);
    sVar6 = *(short *)(iVar23 + 0x168);
    uVar12 = 0;
    uVar14 = FUN_43b06c92((int)(short)((((sVar1 + sVar26 + *(short *)(iVar23 + 0x180)) - sVar6) -
                                       sVar4) - sVar3));
    uVar15 = FUN_43b06c92((int)(short)((((((sVar1 + sVar2) - sVar3) + sVar26) - sVar5) - sVar6) -
                                      sVar4));
    do {
      puVar25 = (undefined2 *)(uVar12 * 0x16 + 0x43f7c2fc);
      uVar24 = uVar12 & 0xff;
      puStack_3c = (undefined2 *)(&DAT_43f7c3c2 + uVar12 * 0x16);
      cVar21 = '\0';
      do {
        FUN_43aec05a(uVar13,uVar24,cVar21);
        uVar16 = FUN_4382632c();
        FUN_43aec05a(uVar11,uVar24,cVar21);
        uVar17 = FUN_4382632c();
        if (uVar16 < uVar17) {
          uVar10 = 0;
        }
        else if (uVar16 - uVar17 < 0xffff) {
          uVar10 = (undefined2)(uVar16 - uVar17);
        }
        else {
          uVar10 = 0xffff;
        }
        uVar10 = FUN_43b06c46(uVar10,uVar14);
        cVar22 = cVar21 + '\x01';
        puVar25 = puVar25 + 1;
        *puVar25 = uVar10;
        FUN_43aec05a(uVar11,uVar24,cVar21);
        uVar18 = FUN_4382632c();
        uVar10 = FUN_43aebfe8(uVar18,0xffff);
        uVar10 = FUN_43b06c46(uVar10,uVar15);
        puStack_3c = puStack_3c + 1;
        *puStack_3c = uVar10;
        cVar21 = cVar22;
      } while (cVar22 != '\v');
      uVar12 = uVar12 + 1;
    } while (uVar12 != 9);
    uVar12 = FUN_4382645c(param_3);
    iVar23 = *param_3;
    iVar23 = (*(ushort *)(param_3[2] + 0x12) + 0x3800) -
             (uint)(ushort)(*(short *)(iVar23 + 0x16a) + *(short *)(iVar23 + 0x168) +
                           *(short *)(iVar23 + 0x16c));
    if (iVar23 < (int)((uint)*(byte *)(iVar20 + 0x24a) * 0x10)) {
      uVar8 = 0;
    }
    else if (iVar23 < (int)((uint)*(byte *)(iVar20 + 0x24b) * 0x10)) {
      uVar8 = FUN_43aebbd0();
    }
    else {
      uVar8 = 100;
    }
    *param_1 = uVar8;
    iVar20 = param_3[5];
  }
  *(char *)(iVar20 + 0x28) = (char)uVar12;
  FUN_43826348(uVar12,param_3);
  *param_2 = (char)uVar12;
  *(undefined1 *)(*(int *)(param_3[1] + 4) + 0x2e3) = *param_1;
  return;
}


/* query "43fe9440" */

/* query "43fe9434" */

/* query "43fe9490" */

/* query "43fe94c0" */

/* query "43fe94e4" */

/* query "43fe94f8" */

/* query "43fe9504" */

/* query "43c9284f" */

/* query "43c92694" */

/* query "43c92998" */

/* query "43c929b6" */

/* query "43c92717" */

/* query "43c923ae" */

/* query "43c92209" */

/* query "43fe91f2" */

/* query "439885ba" */

/* query "43988826" */
