/* S38: existing functions, no memory changes. */

/* 43561260 */

void FUN_43561260(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561274 + 0x43561268 + DAT_43561278) + 0x14) + 0x1e0))();
  return;
}


/* 43561524 */

void FUN_43561524(void)

{
  (**(code **)(*(int *)(*(int *)(DAT_43561538 + 0x4356152e + DAT_4356153c) + 0x14) + 0x2e4))();
  return;
}


/* 435676fc */

undefined4 FUN_435676fc(int param_1,undefined4 *param_2,int param_3)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_1a8 [272];
  undefined2 uStack_98;
  undefined2 uStack_96;
  undefined4 uStack_94;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined2 uStack_84;
  undefined2 uStack_82;
  undefined2 auStack_28 [2];
  undefined4 uStack_24;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined1 auStack_1c [4];
  uint uStack_18;
  undefined4 *puStack_14;
  int iStack_10;
  
  uVar1 = *(ushort *)(param_2 + 1);
  uStack_18 = param_1;
  if (uVar1 == 0) {
    puStack_14 = param_2;
    iStack_10 = param_3;
    FUN_435ab880(DAT_43567740 + 0x4356770c);
    uVar3 = FUN_4356b648();
    uStack_18 = (uint)uVar1;
    FUN_43a3cad4(uVar3,DAT_4356773c,0,0);
    *(undefined2 *)(param_3 + 2) = 0xfffb;
    return 0;
  }
  FUN_439c5a04(&uStack_98,0,0x70);
  uStack_88 = *(undefined4 *)(param_1 + 0x18);
  uStack_98 = 4;
  uStack_84 = *(undefined2 *)(param_1 + 0x14);
  uStack_94 = *param_2;
  uStack_96 = *(undefined2 *)(param_2 + 1);
  uStack_82 = *(undefined2 *)((int)param_2 + 6);
  uStack_8c = param_2[2];
  FUN_435a92e0(auStack_1a8);
  FUN_435aa02c(auStack_1c);
  FUN_435a9304(auStack_1a8,&uStack_98,0x70);
  FUN_43a49628(auStack_1a8,DAT_435676f4);
  iVar2 = FUN_435aa068(auStack_1c,DAT_435676f8,auStack_1a8);
  if ((iVar2 == 0) && (iVar2 = FUN_435a9348(auStack_1a8,&uStack_98,0x70), iVar2 == 0)) {
    FUN_43a3b3a6(param_1,param_3,&uStack_98);
    FUN_439c5a04(auStack_28,0,0xc);
    uStack_24 = *param_2;
    auStack_28[0] = 4;
    uStack_1e = *(undefined2 *)((int)param_2 + 6);
    uStack_20 = FUN_43a3b452(param_1,4,param_2,param_3);
    FUN_43a3b5ae(param_1,auStack_28,(int)*(short *)(param_3 + 2));
    uVar3 = 0;
  }
  else {
    uVar3 = 0xe002;
  }
  FUN_435aa014(auStack_1c);
  FUN_435a92c8(auStack_1a8);
  return uVar3;
}


/* 43591e50 */

void FUN_43591e50(int param_1)

{
  *(undefined4 *)(param_1 + -4) = DAT_43591e58;
  return;
}


/* 43591ea4 */

undefined8
FUN_43591ea4(undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4,
            byte param_5)

{
  int iVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  int iVar4;
  int iStack_30;
  undefined1 *puStack_2c;
  undefined4 uStack_28;
  
  iVar4 = param_5 + 1;
  iStack_30 = iVar4;
  puStack_2c = param_2;
  uStack_28 = param_3;
  iVar1 = FUN_43591dec(1,&iStack_30);
  iVar1 = FUN_435612d0(DAT_43591fc8,&puStack_2c,iVar1 + 1,1);
  if (iVar1 == 0) {
    FUN_43591e50(puStack_2c);
    puStack_2c[2] = 1;
    *puStack_2c = 1;
    puStack_2c[3] = 0;
    puStack_2c[1] = 0;
    puVar2 = (undefined1 *)FUN_43a4620a(puStack_2c,&iStack_30,0);
    *puVar2 = (char)param_2;
    puVar2[8] = (char)iVar4;
    puVar2[9] = (char)((uint)iVar4 >> 8);
    puVar2[1] = (char)((uint)param_2 >> 8);
    puVar2[10] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2[0xb] = 0;
    puVar2[0xc] = (char)param_3;
    FUN_439c5320(puVar2 + 0xd,param_4,(uint)param_5);
    iVar1 = FUN_4356120c(DAT_43591fc8,puStack_2c);
    if (iVar1 == 0) {
      iVar1 = FUN_43561260(DAT_43591fcc,&puStack_2c,0xffffffff,0);
      if (iVar1 == 0) {
        if (*(int *)(puStack_2c + -4) != DAT_43591fc8) {
          FUN_43a46c48(param_1,10,0xa5,0);
        }
        if (*(int *)(puStack_2c + 4) != 0) {
          FUN_43a46c48(param_1,10,0xb1);
        }
        iVar1 = FUN_435612ec(DAT_43591fcc,puStack_2c);
        if (iVar1 == 0) goto LAB_43591fc2;
        uVar3 = 0xb7;
      }
      else {
        uVar3 = 0x9e;
      }
    }
    else {
      FUN_43a46c48(param_1,10,0x8e);
      iVar1 = FUN_435612ec(DAT_43591fc8,puStack_2c);
      if (iVar1 == 0) goto LAB_43591fc2;
      uVar3 = 0x94;
    }
  }
  else {
    uVar3 = 0x72;
  }
  FUN_43a46c48(param_1,10,uVar3,iVar1);
LAB_43591fc2:
  return CONCAT44(iStack_30,iVar1);
}


/* 4359321c */

int FUN_4359321c(undefined4 param_1,undefined4 param_2,undefined2 *param_3)

{
  undefined1 auStack_154 [272];
  undefined1 auStack_44 [2];
  short sStack_42;
  undefined2 uStack_40;
  undefined2 auStack_2c [2];
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined1 auStack_14 [8];
  
  FUN_435a92e0(auStack_154);
  FUN_435aa02c(auStack_14);
  auStack_2c[0] = 1;
  uStack_24 = 0;
  uStack_20 = 0xffffffff;
  uStack_18 = 0;
  uStack_16 = 0;
  uStack_28 = param_2;
  FUN_43a49628(auStack_154,DAT_435932a0);
  FUN_435a9304(auStack_154,auStack_2c,0x18);
  FUN_435aa068(auStack_14,DAT_435932a4,auStack_154);
  FUN_435a9348(auStack_154,auStack_44,0x18);
  *param_3 = uStack_40;
  FUN_435aa014(auStack_14);
  FUN_435a92c8(auStack_154);
  return (int)sStack_42;
}


/* 435932a8 */

void FUN_435932a8(undefined4 param_1,undefined2 param_2)

{
  undefined1 auStack_14c [272];
  undefined1 auStack_3c [24];
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined1 auStack_c [4];
  
  FUN_435a92e0(auStack_14c);
  FUN_435aa02c(auStack_c);
  uStack_24 = 4;
  uStack_10 = 0;
  uStack_e = 2;
  uStack_22 = param_2;
  FUN_43a49628(auStack_14c,DAT_43593318);
  FUN_435a9304(auStack_14c,&uStack_24,0x18);
  FUN_435aa068(auStack_c,DAT_4359331c,auStack_14c);
  FUN_435a9348(auStack_14c,auStack_3c,0x18);
  FUN_435aa014(auStack_c);
  FUN_435a92c8(auStack_14c);
  return;
}


/* 43593320 */

void FUN_43593320(undefined4 param_1,undefined1 param_2,undefined2 param_3)

{
  int iVar1;
  undefined1 auStack_13c [272];
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined1 uStack_28;
  undefined4 uStack_24;
  undefined1 uStack_1c;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined1 auStack_14 [8];
  
  FUN_435aa02c(auStack_14);
  FUN_435a92e0(auStack_13c);
  uStack_2c = 1;
  uStack_2a = 1;
  uStack_28 = 1;
  uStack_24 = 0;
  uStack_18 = 0;
  uStack_1c = param_2;
  uStack_1a = param_3;
  iVar1 = FUN_43a49628(auStack_13c,DAT_43593394);
  if ((iVar1 == 0) && (iVar1 = FUN_435a9304(auStack_13c,&uStack_2c,0x18), iVar1 == 0)) {
    FUN_435aa20c(auStack_14,DAT_43593398,auStack_13c);
  }
  FUN_435a92c8(auStack_13c);
  FUN_435aa014(auStack_14);
  return;
}


/* 43593460 */

void FUN_43593460(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined2 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_12c [272];
  undefined1 auStack_1c [4];
  
  FUN_435aa02c(auStack_1c);
  FUN_435a92e0(auStack_12c);
  iVar1 = FUN_43a49628(auStack_12c,DAT_43593514);
  if (iVar1 == 0) {
    iVar1 = FUN_435a9304(auStack_12c,param_3,param_4);
    if (iVar1 == 0) {
      iVar1 = FUN_435aa20c(auStack_1c,param_2,auStack_12c);
      if (iVar1 == 0) goto LAB_435934f0;
      FUN_43a46c48(param_1,8,0x243,param_2);
      uVar2 = 0x244;
    }
    else {
      FUN_43a46c48(param_1,8,0x23a,param_2);
      uVar2 = 0x23b;
    }
  }
  else {
    FUN_43a46c48(param_1,8,0x232,param_2);
    uVar2 = 0x233;
  }
  FUN_43a46c48(param_1,8,uVar2,iVar1);
LAB_435934f0:
  FUN_435a92c8(auStack_12c);
  FUN_435aa014(auStack_1c);
  return;
}


/* 43593518 */

void FUN_43593518(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined2 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_12c [272];
  undefined1 auStack_1c [4];
  
  FUN_435aa02c(auStack_1c);
  FUN_435a92e0(auStack_12c);
  iVar1 = FUN_435a941c(auStack_12c,DAT_435935f0);
  if (iVar1 == 0) {
    iVar1 = FUN_43a49628(auStack_12c,DAT_435935f0);
    if (iVar1 == 0) {
      iVar1 = FUN_435a9460(auStack_12c,param_3,param_4);
      if (iVar1 == 0) {
        iVar1 = FUN_435aa20c(auStack_1c,param_2,auStack_12c);
        if (iVar1 == 0) goto LAB_435935cc;
        FUN_43a46c48(param_1,8,0x218,param_2);
        uVar2 = 0x219;
      }
      else {
        FUN_43a46c48(param_1,8,0x20f,param_2);
        uVar2 = 0x210;
      }
    }
    else {
      FUN_43a46c48(param_1,8,0x207,param_2);
      uVar2 = 0x208;
    }
  }
  else {
    FUN_43a46c48(param_1,8,0x1ff,param_2);
    uVar2 = 0x200;
  }
  FUN_43a46c48(param_1,8,uVar2,iVar1);
LAB_435935cc:
  FUN_435a92c8(auStack_12c);
  FUN_435aa014(auStack_1c);
  return;
}


/* 4359463c */

undefined4
FUN_4359463c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined2 param_4,
            undefined4 param_5,undefined2 param_6)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_12c [272];
  undefined1 auStack_1c [8];
  
  FUN_435aa02c(auStack_1c);
  FUN_435a92e0(auStack_12c);
  iVar1 = FUN_43a49628(auStack_12c,DAT_435946d4);
  if (iVar1 == 0) {
    iVar1 = FUN_435a9304(auStack_12c,param_3,param_4,0);
    if (iVar1 == 0) {
      iVar1 = FUN_435aa068(auStack_1c,param_2,auStack_12c,0);
      if (iVar1 == 0) {
        FUN_435a9348(auStack_12c,param_5,param_6,0);
        uVar2 = 1;
        goto LAB_435946b0;
      }
      uVar2 = 0x42e;
    }
    else {
      uVar2 = 0x427;
    }
  }
  else {
    uVar2 = 0x421;
  }
  FUN_43a46c48(param_1,7,uVar2);
  uVar2 = 0;
LAB_435946b0:
  FUN_435a92c8(auStack_12c);
  FUN_435aa014(auStack_1c);
  return uVar2;
}


/* 435946d8 */

undefined4 FUN_435946d8(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_2b8 [576];
  undefined1 auStack_78 [2];
  short sStack_76;
  undefined2 uStack_60;
  undefined2 uStack_5e;
  short sStack_4c;
  undefined1 auStack_48 [2];
  short sStack_46;
  undefined2 uStack_44;
  undefined4 uStack_38;
  int iStack_34;
  undefined2 auStack_30 [2];
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  
  auStack_30[0] = 1;
  uStack_2c = 0x206;
  uStack_24 = 0xffffffff;
  uStack_1a = 1;
  uStack_28 = 0;
  uStack_1c = 0;
  iVar1 = FUN_4359463c(param_1,DAT_43594818,auStack_30,0x18,auStack_48,0x18);
  if (iVar1 == 0) {
    uVar2 = 0x3be;
    iStack_34 = 0;
    goto LAB_43594786;
  }
  if (sStack_46 == 0) {
    *(undefined2 *)(param_1 + 0x5ea) = uStack_44;
    iVar1 = FUN_43594494(param_1,auStack_2b8);
    if (iVar1 == 0) {
      uVar2 = 0x3cf;
    }
    else {
      iVar1 = FUN_43a3a9b4(uStack_38,0x10,2);
      if (iVar1 == 0) {
        FUN_43a46c48(param_1,7,0x3e1,iStack_34);
        return 0;
      }
      if (iStack_34 != 0x240) {
        FUN_43a46c48(param_1,7,0x3d6,0x240);
        uVar2 = 0x3d7;
LAB_43594786:
        FUN_43a46c48(param_1,7,uVar2,iStack_34);
        return 0;
      }
      FUN_439c5a04(iVar1,0,0x240);
      FUN_439c5320(iVar1,auStack_2b8,0x240);
      FUN_43a46c34(param_1,7,0x3dd,0x240);
      uStack_60 = 6;
      uStack_5e = *(undefined2 *)(param_1 + 0x5ea);
      sStack_4c = sStack_46;
      iVar1 = FUN_4359463c(param_1,DAT_43594818,&uStack_60,0x18,auStack_78,0x18);
      if (iVar1 != 0) {
        if (sStack_76 == 0) {
          return 1;
        }
        uVar2 = 0x40a;
        iStack_34 = (int)sStack_76;
        goto LAB_43594786;
      }
      uVar2 = 0x405;
    }
    iVar1 = 0;
  }
  else {
    uVar2 = 0x3c3;
    iVar1 = (int)sStack_46;
  }
  FUN_43a46c48(param_1,7,uVar2,iVar1);
  return 0;
}


/* 4359481c */

void FUN_4359481c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  _uStack_20 = CONCAT22(*(undefined2 *)(param_1 + 0x5ea),4);
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_43593460(param_1,DAT_43594844,&uStack_20,0x18);
  return;
}


/* 43594880 */

void FUN_43594880(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_4c0 [272];
  undefined1 auStack_3b0 [272];
  undefined1 auStack_2a0 [272];
  undefined2 uStack_190;
  undefined2 uStack_18e;
  undefined2 uStack_18c;
  undefined2 uStack_18a;
  undefined2 uStack_188;
  undefined2 uStack_184;
  undefined2 uStack_182;
  undefined2 uStack_180;
  undefined2 uStack_17e;
  undefined1 uStack_17b;
  undefined4 uStack_178;
  undefined2 uStack_174;
  undefined4 uStack_170;
  undefined4 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  undefined2 uStack_15c;
  undefined2 uStack_15a;
  undefined1 uStack_158;
  undefined1 uStack_157;
  undefined2 uStack_154;
  undefined2 uStack_152;
  undefined2 uStack_150;
  undefined2 uStack_14e;
  undefined1 uStack_14c;
  undefined1 uStack_14b;
  undefined1 uStack_14a;
  undefined1 uStack_149;
  undefined1 uStack_148;
  undefined1 uStack_147;
  undefined1 uStack_146;
  undefined4 uStack_144;
  undefined2 uStack_140;
  undefined4 uStack_13c;
  undefined1 auStack_138 [76];
  undefined1 auStack_ec [40];
  undefined1 auStack_c4 [36];
  undefined1 auStack_a0 [28];
  undefined1 auStack_84 [2];
  short sStack_82;
  undefined2 uStack_6c;
  undefined2 uStack_6a;
  undefined2 uStack_58;
  undefined1 auStack_54 [2];
  short sStack_52;
  short sStack_4c;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined2 uStack_3c;
  undefined2 uStack_3a;
  undefined4 uStack_30;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined4 auStack_24 [2];
  undefined4 auStack_1c [2];
  undefined1 auStack_14 [4];
  
  FUN_435a92e0(auStack_2a0);
  FUN_435aa02c(auStack_14);
  iVar1 = FUN_4359321c(param_1,DAT_43594b28,param_1 + 0x632);
  if ((iVar1 != 0) || (iVar1 = FUN_4359321c(param_1,DAT_43594b2c,param_1 + 0x630), iVar1 != 0))
  goto LAB_43594bfa;
  uStack_3a = *(undefined2 *)(param_1 + 0x630);
  uStack_28 = 0;
  uStack_26 = 0;
  uStack_3c = 5;
  uStack_30 = 0xffffffff;
  FUN_435a92e0(auStack_3b0);
  FUN_43a49628(auStack_3b0,DAT_43594b30);
  FUN_435a9304(auStack_3b0,&uStack_3c,0x18);
  FUN_435aa068(auStack_14,DAT_43594b34,auStack_3b0);
  iVar1 = FUN_435a9348(auStack_3b0,auStack_54,0x18);
  if ((iVar1 == 0) && ((sStack_52 == 0 && (sStack_4c == 1)))) {
    uVar2 = FUN_43a3a9b4(uStack_44,0x10,2);
    FUN_439c5a04(uVar2,0,0x20);
    FUN_435a9288(auStack_c4,uVar2,uStack_40,0);
    FUN_435a91d0(auStack_138);
    FUN_43a4945e(auStack_138,1);
    FUN_43a49462(auStack_138,DAT_43594b28);
    FUN_43a4946c(auStack_138,*(undefined2 *)(param_1 + 0x632));
    FUN_43a49476(auStack_138,0);
    FUN_43a4948c(auStack_138,0x280);
    FUN_43a49490(auStack_138,0x1e0);
    FUN_43a49494(auStack_138,0x280);
    FUN_43a4949e(auStack_138,0x1e0);
    FUN_43a494a8(auStack_138,0);
    FUN_43a494b2(auStack_138,0);
    FUN_43a494bc(auStack_138,0x280);
    FUN_43a494c6(auStack_138,0x1e0);
    FUN_43a494d0(auStack_138,0);
    FUN_43a494da(auStack_138,0);
    FUN_43a494e4(auStack_138,0x280);
    FUN_43a494ee(auStack_138,0x1e0);
    FUN_43a494f8(auStack_138,0);
    FUN_43a49504(auStack_138,0);
    FUN_43a46c34(param_1,4,0x1d9,0);
    iVar1 = thunk_FUN_43a49ba4(auStack_c4,auStack_138);
    if (iVar1 == 0) {
      FUN_435a922c(auStack_a0);
      FUN_43a4955e(auStack_a0,1);
      FUN_43a49562(auStack_a0,0);
      FUN_43a49566(auStack_a0,0);
      iVar1 = thunk_FUN_43a49ba4(auStack_c4,auStack_a0);
      if (iVar1 == 0) {
        FUN_435a9174(auStack_ec);
        auStack_1c[0] = 0xffffffff;
        auStack_24[0] = 0xffffffff;
        FUN_43a493f0(auStack_ec,auStack_1c);
        FUN_43a493fc(auStack_ec,auStack_24);
        iVar1 = thunk_FUN_43a49ba4(auStack_c4,auStack_ec);
        if (iVar1 == 0) {
          uStack_6a = *(undefined2 *)(param_1 + 0x630);
          uStack_58 = 0;
          uStack_6c = 6;
          FUN_435a92e0(auStack_4c0);
          FUN_43a49628(auStack_4c0,DAT_43594b30);
          iVar1 = FUN_435a9304(auStack_4c0,&uStack_6c,0x18);
          if ((((iVar1 == 0) &&
               (iVar1 = FUN_435aa068(auStack_14,DAT_43594b34,auStack_4c0), iVar1 == 0)) &&
              (iVar1 = FUN_435a9348(auStack_4c0,auStack_84,0x18), iVar1 == 0)) && (sStack_82 == 0))
          {
            FUN_435a92c8(auStack_4c0);
            FUN_435a9154(auStack_ec);
            FUN_435a920c(auStack_a0);
            FUN_435a91b0(auStack_138);
            FUN_435a9268(auStack_c4);
            uStack_190 = 0x2000;
            uStack_18e = 5;
            uStack_18c = 0x58;
            uStack_188 = 7;
            uStack_184 = 0x2000;
            uStack_180 = 0x2000;
            uStack_17e = 0x8301;
            uStack_144 = DAT_43594c58;
            uStack_140 = *(undefined2 *)(param_1 + 0x630);
            uStack_178 = DAT_43594c5c;
            uStack_174 = *(undefined2 *)(param_1 + 0x634);
            uStack_18a = 0;
            uStack_182 = 0;
            uStack_17b = 0;
            uStack_170 = 0;
            uStack_168 = 0x5000;
            uStack_164 = 0;
            uStack_160 = 0x5000;
            uStack_158 = 0;
            uStack_15c = 0x280;
            uStack_157 = 0;
            uStack_15a = 0x1e0;
            uStack_154 = 0;
            uStack_152 = 0;
            uStack_150 = 0x280;
            uStack_14b = 0;
            uStack_14e = 0x1e0;
            uStack_14a = 0;
            uStack_14c = 1;
            uStack_149 = 0;
            uStack_148 = 0;
            uStack_147 = 0;
            uStack_146 = 0;
            uStack_13c = 0;
            FUN_43593518(param_1,DAT_43594c60,&uStack_190,0x58);
            goto LAB_43594bf4;
          }
          FUN_435a92c8(auStack_4c0);
        }
        FUN_435a9154(auStack_ec);
      }
      FUN_435a920c(auStack_a0);
    }
    FUN_435a91b0(auStack_138);
    FUN_435a9268(auStack_c4);
  }
LAB_43594bf4:
  FUN_435a92c8(auStack_3b0);
LAB_43594bfa:
  FUN_435aa014(auStack_14);
  FUN_435a92c8(auStack_2a0);
  return;
}


/* 43594ce8 */

void FUN_43594ce8(int param_1)

{
  undefined1 auStack_270 [272];
  undefined1 auStack_160 [272];
  undefined1 auStack_50 [2];
  short sStack_4e;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined1 uStack_18;
  undefined1 uStack_15;
  undefined1 uStack_14;
  undefined1 auStack_c [4];
  
  FUN_435aa02c(auStack_c);
  uStack_38 = 4;
  uStack_36 = *(undefined2 *)(param_1 + 0x634);
  uStack_24 = 0;
  uStack_22 = 0;
  FUN_435a92e0(auStack_160);
  FUN_43a49628(auStack_160,DAT_43594db4);
  FUN_435a9304(auStack_160,&uStack_38,0x18);
  FUN_435aa068(auStack_c,DAT_43594db8,auStack_160);
  FUN_435a9348(auStack_160,auStack_50,0x18);
  if (sStack_4e == 0) {
    *(undefined1 *)(param_1 + 0x679) = 1;
  }
  FUN_435a92e0(auStack_270);
  uStack_20 = 0x2001;
  uStack_1e = 0x400;
  uStack_1c = 0x14;
  uStack_1a = 1;
  uStack_18 = 0;
  uStack_15 = 0;
  uStack_14 = 0;
  FUN_43593518(param_1,DAT_43594dbc,&uStack_20,0x14);
  FUN_435a92c8(auStack_270);
  FUN_435a92c8(auStack_160);
  FUN_435aa014(auStack_c);
  return;
}


/* 435a4c34 */

undefined4 FUN_435a4c34(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_190 [272];
  undefined1 auStack_80 [2];
  short sStack_7e;
  short sStack_7a;
  
  FUN_435a92e0(auStack_190);
  FUN_435a9304(auStack_190,param_2,0x70);
  FUN_43a49628(auStack_190,*(undefined4 *)(param_1 + 8));
  iVar1 = FUN_435aa068(param_1 + 0xc,DAT_435a4cc4,auStack_190);
  if (iVar1 == 0) {
    FUN_439c5a04(auStack_80,0,0x70);
    iVar1 = FUN_435a9348(auStack_190,auStack_80,0x70);
    if ((iVar1 == 0) && (sStack_7a == 0x1111)) {
      FUN_43a4912c(param_1,auStack_80,param_3);
      uVar2 = 0;
      if (sStack_7e != 0) {
        if (sStack_7e < 0) {
          uVar2 = 0xfffffffc;
        }
        else {
          uVar2 = 0xfffffffe;
        }
      }
      goto LAB_435a4cac;
    }
  }
  uVar2 = 0xfffffffc;
LAB_435a4cac:
  FUN_435a92c8(auStack_190);
  return uVar2;
}


/* 435a4cc8 */

undefined4 FUN_435a4cc8(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_138 [272];
  undefined1 auStack_28 [2];
  short sStack_26;
  short sStack_22;
  
  FUN_435a92e0(auStack_138);
  FUN_435a9304(auStack_138,param_2,0x18);
  FUN_43a49628(auStack_138,*(undefined4 *)(param_1 + 8));
  iVar1 = FUN_435aa20c(param_1 + 0xc,DAT_435a4d68,auStack_138);
  if (iVar1 == 0) {
    FUN_439c5a04(auStack_28,0,0x18);
    iVar1 = FUN_435a9f4c(param_1 + 0x10,DAT_435a4d6c,auStack_138,0xffffffff);
    if (((iVar1 == 0) && (iVar1 = FUN_435a9348(auStack_138,auStack_28,0x18), iVar1 == 0)) &&
       (sStack_22 == 0x1111)) {
      FUN_43a49226(param_1,auStack_28,param_3);
      uVar2 = 0;
      if (sStack_26 != 0) {
        if (sStack_26 < 0) {
          uVar2 = 0xfffffffc;
        }
        else {
          uVar2 = 0xfffffffe;
        }
      }
      goto LAB_435a4d52;
    }
  }
  uVar2 = 0xfffffffc;
LAB_435a4d52:
  FUN_435a92c8(auStack_138);
  return uVar2;
}


/* 435a5ca4 */

int FUN_435a5ca4(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined2 uStack_80;
  short sStack_7e;
  uint uStack_7c;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  
  uVar1 = FUN_435a5c60();
  *(undefined4 *)(param_1 + 0x14) = 0;
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_7c = *(uint *)(param_1 + 0xc);
  uStack_80 = 1;
  uStack_74 = *(undefined4 *)(param_1 + 8);
  uStack_6c = CONCAT22(1,(short)uVar1);
  iVar2 = FUN_435a9070(DAT_435a5d28,DAT_435a5d2c,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7c >> 0x10 != uVar1) {
      return 1;
    }
    *(undefined2 *)(param_1 + 0x10) = (undefined2)uStack_7c;
    *(short *)(param_1 + 0x20) = sStack_7e;
    *(undefined4 *)(param_1 + 0x28) = uStack_70;
    *(undefined4 *)(param_1 + 0x2c) = uStack_6c;
    *(undefined4 *)(param_1 + 0x14) = 0x1122;
    if (sStack_7e == 0) {
      return 0;
    }
    uVar3 = 0x112a;
  }
  else {
    *(undefined4 *)(param_1 + 0x28) = 0;
    *(undefined4 *)(param_1 + 0x2c) = 0;
    *(short *)(param_1 + 0x20) = sStack_7e;
    uVar3 = 8;
  }
  *(undefined4 *)(param_1 + 0x14) = uVar3;
  return iVar2;
}


/* 435a5d30 */

int FUN_435a5d30(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined2 uStack_80;
  short sStack_7e;
  uint uStack_7c;
  undefined2 uStack_6c;
  
  uVar1 = FUN_435a5c60();
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_80 = 2;
  uStack_7c = *(uint *)(param_1 + 0xc);
  sStack_7e = *(short *)(param_1 + 0x10);
  uStack_6c = (short)uVar1;
  iVar2 = FUN_435a9070(DAT_435a5da8,DAT_435a5dac,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7c >> 0x10 != uVar1) {
      return 1;
    }
    uVar1 = *(uint *)(param_1 + 0x14);
    *(uint *)(param_1 + 0x14) = uVar1 | 0x2002;
    if (sStack_7e == 0) goto LAB_435a5d9a;
    uVar1 = uVar1 | 0x200a;
  }
  else {
    uVar1 = *(uint *)(param_1 + 0x14) | 8;
  }
  *(uint *)(param_1 + 0x14) = uVar1;
LAB_435a5d9a:
  *(short *)(param_1 + 0x20) = sStack_7e;
  return iVar2;
}


/* 435a5db0 */

int FUN_435a5db0(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined2 uStack_80;
  short sStack_7e;
  undefined2 uStack_7c;
  ushort uStack_7a;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  
  uVar1 = FUN_435a5c60();
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_80 = 5;
  sStack_7e = *(short *)(param_1 + 0x10);
  uStack_74 = *(undefined4 *)(param_1 + 8);
  uStack_6c = CONCAT22(uStack_6c._2_2_,(short)uVar1);
  iVar2 = FUN_435a9070(DAT_435a5e34,DAT_435a5e38,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7a != uVar1) {
      return 1;
    }
    *(undefined2 *)(param_1 + 0x10) = uStack_7c;
    *(short *)(param_1 + 0x20) = sStack_7e;
    *(undefined4 *)(param_1 + 0x28) = uStack_70;
    *(undefined4 *)(param_1 + 0x2c) = uStack_6c;
    uVar1 = *(uint *)(param_1 + 0x14) & 0xffffffef;
    *(uint *)(param_1 + 0x14) = uVar1 | 0x122;
    if (sStack_7e == 0) {
      return 0;
    }
    uVar1 = uVar1 | 0x12a;
  }
  else {
    *(undefined4 *)(param_1 + 0x28) = 0;
    *(undefined4 *)(param_1 + 0x2c) = 0;
    *(short *)(param_1 + 0x20) = sStack_7e;
    uVar1 = 8;
  }
  *(uint *)(param_1 + 0x14) = uVar1;
  return iVar2;
}


/* 435a5e3c */

undefined4 FUN_435a5e3c(undefined4 *param_1)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  
  FUN_439c5a04(&uStack_20,0,0x18);
  uStack_20 = 4;
  uVar1 = FUN_435a5c60();
  uStack_1e = *(undefined2 *)(param_1 + 4);
  uStack_a = 0;
  param_1[5] = param_1[5] & 0xffffbefc | 0x4001;
  iVar3 = DAT_435a5ea4 + 0x435a5e7c;
  uStack_c = (undefined2)uVar1;
  *(undefined2 *)(param_1 + 1) = uStack_c;
  *(undefined4 **)(iVar3 + (uVar1 & 0x3f) * 4) = param_1;
  if (param_1[6] == 0) {
    uVar2 = FUN_435a8fd8(DAT_435a5ea0,*param_1,&uStack_20,0x18);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}


/* 435a5ea8 */

int FUN_435a5ea8(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined2 uStack_80;
  short sStack_7e;
  ushort uStack_7a;
  undefined2 uStack_6c;
  
  uVar1 = FUN_435a5c60();
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_80 = 4;
  sStack_7e = *(short *)(param_1 + 0x10);
  uStack_6c = (short)uVar1;
  iVar2 = FUN_435a9070(DAT_435a5f20,DAT_435a5f24,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7a != uVar1) {
      return 1;
    }
    uVar1 = *(uint *)(param_1 + 0x14) & 0xfffffeff | 0x4002;
    *(uint *)(param_1 + 0x14) = uVar1;
    if (sStack_7e == 0) goto LAB_435a5f0a;
  }
  else {
    uVar1 = *(uint *)(param_1 + 0x14);
  }
  *(uint *)(param_1 + 0x14) = uVar1 | 8;
LAB_435a5f0a:
  *(short *)(param_1 + 0x20) = sStack_7e;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  return iVar2;
}


/* 435a5f28 */

int FUN_435a5f28(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined2 uStack_80;
  short sStack_7e;
  ushort uStack_7a;
  undefined2 uStack_6c;
  undefined2 uStack_6a;
  
  uVar1 = FUN_435a5c60();
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_80 = 4;
  sStack_7e = *(short *)(param_1 + 0x10);
  uStack_6a = 2;
  uStack_6c = (short)uVar1;
  iVar2 = FUN_435a9070(DAT_435a5fa4,DAT_435a5fa8,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7a != uVar1) {
      return 1;
    }
    uVar1 = *(uint *)(param_1 + 0x14) & 0xfffffe9f | 0x4002;
    *(uint *)(param_1 + 0x14) = uVar1;
    if (sStack_7e == 0) goto LAB_435a5f90;
  }
  else {
    uVar1 = *(uint *)(param_1 + 0x14);
  }
  *(uint *)(param_1 + 0x14) = uVar1 | 8;
LAB_435a5f90:
  *(short *)(param_1 + 0x20) = sStack_7e;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  return iVar2;
}


/* 435a5fac */

int FUN_435a5fac(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined2 uStack_80;
  short sStack_7e;
  ushort uStack_7a;
  undefined2 uStack_6c;
  
  uVar1 = FUN_435a5c60();
  *(undefined2 *)(param_1 + 0x20) = 0;
  *(short *)(param_1 + 4) = (short)uVar1;
  FUN_439c5a04(&uStack_80,0,0x70);
  uStack_80 = 6;
  sStack_7e = *(short *)(param_1 + 0x10);
  uStack_6c = (short)uVar1;
  iVar2 = FUN_435a9070(DAT_435a6020,DAT_435a6024,&uStack_80,0x70);
  if (iVar2 == 0) {
    if (uStack_7a != uVar1) {
      return 1;
    }
    uVar1 = *(uint *)(param_1 + 0x14) & 0xffffff9f | 0x12;
    *(uint *)(param_1 + 0x14) = uVar1;
    if (sStack_7e == 0) goto LAB_435a600a;
  }
  else {
    uVar1 = *(uint *)(param_1 + 0x14);
  }
  *(uint *)(param_1 + 0x14) = uVar1 | 8;
LAB_435a600a:
  *(short *)(param_1 + 0x20) = sStack_7e;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  return iVar2;
}


/* 435a9e74 */

undefined8 FUN_435a9e74(undefined4 param_1,undefined4 param_2,int param_3,uint param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint *puVar5;
  int iVar6;
  int iVar7;
  undefined4 uStack_1c;
  int iStack_18;
  
  uStack_1c = param_2;
  iStack_18 = param_3;
  if (*(int *)(param_3 + 0x10) == 0) {
    iVar7 = -0x14;
    FUN_435aa628(DAT_435a9f38,0x8a,0xffffffec);
  }
  else {
    if (((param_4 == 0) || (param_4 == 0xffffffff)) || (param_4 <= DAT_435a9f3c)) {
      FUN_43561260(param_2,&uStack_1c);
      iVar7 = FUN_435a9df0();
      uVar1 = uStack_1c;
      if (iVar7 == 0) {
        uVar2 = FUN_43a49ac4(uStack_1c);
        *(undefined4 *)(param_3 + 0xc) = uVar2;
        uVar3 = FUN_43561340(uVar1);
        uVar4 = FUN_43a49702(param_3);
        if (uVar4 < uVar3) {
          uVar3 = FUN_43a49702(param_3);
        }
        FUN_439c5320(*(undefined4 *)(param_3 + 0x10),uStack_1c,uVar3);
        iVar6 = *(int *)(param_3 + 0xc);
        puVar5 = *(uint **)(param_3 + 0x10);
        if (((iVar6 == DAT_435a9f40) || (iVar6 == DAT_435a9f40 + 0x7a)) ||
           ((iVar6 == DAT_435a9f44 || ((iVar6 == DAT_435a9f48 || (puVar5[1] != 0xa0a0a0a0)))))) {
          *(short *)(param_3 + 8) = (short)uVar3;
          *(undefined4 *)(param_3 + 4) = 2;
        }
        else {
          *(undefined4 *)(param_3 + 4) = 1;
          if (iVar6 < 0) {
            *puVar5 = *puVar5 | 0x80000000;
          }
        }
        FUN_435612ec(param_2,uStack_1c);
        goto LAB_435a9f34;
      }
    }
    else {
      iVar7 = -0x20;
    }
    FUN_435aa628(DAT_435a9f38,0xde,iVar7);
  }
LAB_435a9f34:
  return CONCAT44(param_1,iVar7);
}


/* 435a9f4c */

undefined8 FUN_435a9f4c(undefined4 param_1,undefined4 param_2,int param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uStack_24;
  int iStack_20;
  
  uStack_24 = param_2;
  iStack_20 = param_3;
  if (((param_4 == 0) || (param_4 == 0xffffffff)) || (param_4 <= DAT_435aa000)) {
    FUN_43561260(param_2,&uStack_24);
    iVar2 = FUN_435a9df0();
    uVar1 = uStack_24;
    if (iVar2 == 0) {
      uVar3 = FUN_43a49ac4(uStack_24);
      *(undefined4 *)(param_3 + 0xc) = uVar3;
      uVar4 = FUN_43561340(uVar1);
      uVar1 = uStack_24;
      if (0xff < uVar4) {
        uVar4 = 0x100;
      }
      FUN_439c5320(param_3 + 0x10,uStack_24,uVar4);
      iVar5 = *(int *)(param_3 + 0xc);
      if (((iVar5 == DAT_435aa004) || (iVar5 == DAT_435aa004 + 0x7a)) ||
         ((iVar5 == DAT_435aa008 ||
          ((iVar5 == DAT_435aa00c || (*(int *)(param_3 + 0x14) != -0x5f5f5f60)))))) {
        *(short *)(param_3 + 8) = (short)uVar4;
        *(undefined4 *)(param_3 + 4) = 2;
      }
      else {
        *(undefined4 *)(param_3 + 4) = 1;
        if (iVar5 < 0) {
          *(uint *)(param_3 + 0x10) = *(uint *)(param_3 + 0x10) | 0x80000000;
        }
      }
      FUN_435612ec(param_2,uVar1);
      goto LAB_435a9ff8;
    }
  }
  else {
    iVar2 = -0x20;
  }
  FUN_435aa628(DAT_435aa010,0x77,iVar2);
LAB_435a9ff8:
  return CONCAT44(param_1,iVar2);
}


/* 435aa068 */

undefined4 FUN_435aa068(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_24;
  
  iVar2 = *(int *)(param_3 + 4);
  uStack_24 = param_4;
  if (iVar2 == 1) {
    uVar1 = *(undefined2 *)(param_3 + 0x1a);
  }
  else {
    if (iVar2 != 2) {
      uVar3 = 0xffff;
      if (iVar2 == 0) {
        uVar3 = 0xffffffe5;
      }
      FUN_435aa628(DAT_435aa150,0xb1,uVar3);
      return uVar3;
    }
    uVar1 = *(undefined2 *)(param_3 + 8);
  }
  iVar2 = FUN_435612d0(param_2,&uStack_24,uVar1,1,param_1,param_2,param_3);
  if (iVar2 == 0) {
    FUN_439c5320(uStack_24,param_3 + 0x10,uVar1);
    FUN_43a49adc(uStack_24,*(undefined4 *)(param_3 + 0xc));
    iVar2 = FUN_43561228(param_2,uStack_24);
    if (iVar2 != 0) {
      FUN_435aa5c4(10,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
    }
    uVar3 = uStack_24;
    FUN_439c5320(param_3 + 0x10,uStack_24,uVar1);
    if ((((param_2 == DAT_435aa154) || (param_2 == DAT_435aa154 + 0x7a)) ||
        (param_2 == DAT_435aa158)) || (*(int *)(param_3 + 0x14) != -0x5f5f5f60)) {
      *(undefined2 *)(param_3 + 8) = uVar1;
      *(undefined4 *)(param_3 + 4) = 2;
    }
    else {
      *(undefined4 *)(param_3 + 4) = 1;
    }
    FUN_435612ec(param_2,uVar3);
    uVar3 = FUN_435aa044(param_1,iVar2);
    FUN_435aa628(DAT_435aa150,0xe3,uVar3);
  }
  else {
    FUN_435aa5c4(8,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
  }
  uVar3 = FUN_435aa044(param_1,iVar2);
  return uVar3;
}


/* 435aa20c */

undefined4 FUN_435aa20c(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_1c;
  
  iVar2 = *(int *)(param_3 + 4);
  uStack_1c = param_4;
  if (iVar2 == 1) {
    uVar1 = *(undefined2 *)(param_3 + 0x1a);
  }
  else {
    if (iVar2 != 2) {
      uVar3 = 0xffff;
      if (iVar2 == 0) {
        uVar3 = 0xffffffe5;
      }
      FUN_435aa628(DAT_435aa2a8,0x3c,uVar3);
      return uVar3;
    }
    uVar1 = *(undefined2 *)(param_3 + 8);
  }
  iVar2 = FUN_435612d0(param_2,&uStack_1c,uVar1,1,param_1,param_2,param_3);
  if (iVar2 == 0) {
    FUN_439c5320(uStack_1c,param_3 + 0x10,uVar1);
    FUN_43a49adc(uStack_1c,*(undefined4 *)(param_3 + 0xc));
    iVar2 = FUN_4356120c(param_2,uStack_1c);
    if (iVar2 == 0) {
      return 0;
    }
    FUN_435aa5c4(9,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
    FUN_435612ec(param_2,uStack_1c);
  }
  else {
    FUN_435aa5c4(8,*(undefined4 *)(param_3 + 0xc),param_2,uVar1,iVar2);
  }
  uVar3 = FUN_435aa044(param_1,iVar2);
  return uVar3;
}


/* 435c6430 */

undefined4 FUN_435c6430(int param_1,undefined2 *param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_220 [272];
  undefined2 uStack_110;
  undefined2 uStack_10e;
  undefined2 uStack_10c;
  undefined2 uStack_10a;
  undefined2 uStack_108;
  undefined2 uStack_106;
  undefined4 uStack_100;
  undefined4 uStack_fc;
  undefined2 uStack_a0;
  undefined2 uStack_9e;
  undefined4 uStack_9c;
  undefined4 uStack_94;
  undefined2 uStack_8c;
  undefined2 uStack_8a;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  FUN_439c5a04(&uStack_30,0,0x18);
  FUN_439c5a04(&uStack_a0,0,0x70);
  FUN_439c5a04(&uStack_110,0,0x70);
  FUN_435a92e0(auStack_220);
  uStack_a0 = *param_2;
  uVar2 = *(undefined4 *)(param_1 + 0x11c);
  uStack_9c = *(undefined4 *)(param_2 + 2);
  uStack_94 = *(undefined4 *)(param_2 + 6);
  uStack_8c = param_2[10];
  uStack_9e = param_2[1];
  uStack_8a = param_2[0xb];
  FUN_435a9304(auStack_220,&uStack_a0,0x70);
  FUN_43a49628(auStack_220,uVar2);
  iVar1 = FUN_435aa068(param_1 + 8,DAT_435c6548,auStack_220);
  if (iVar1 == 0) {
    FUN_435a9348(auStack_220,&uStack_110,0x70);
    uStack_30 = uStack_110;
    uStack_2e = uStack_10e;
    uStack_2c = uStack_10c;
    uStack_2a = uStack_10a;
    uStack_28 = uStack_108;
    uStack_26 = uStack_106;
    uStack_1c = uStack_fc;
    uStack_20 = uStack_100;
    if (param_3 == (undefined4 *)0x0) {
      FUN_43a495f2(auStack_220);
      FUN_435a9304(auStack_220,&uStack_30,0x18);
      FUN_43a49628(auStack_220,DAT_435c6548);
      iVar1 = FUN_435aa20c(param_1 + 8,uVar2,auStack_220);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 0x21;
      }
    }
    else {
      (**(code **)*param_3)(param_3,&uStack_30,0x18);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0x21;
  }
  FUN_435a92c8(auStack_220);
  return uVar2;
}


/* 43620a90 */

undefined4 FUN_43620a90(int param_1,short *param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_198 [272];
  undefined1 auStack_88 [2];
  ushort uStack_86;
  short sStack_82;
  
  FUN_435a92e0(auStack_198);
  FUN_435a9304(auStack_198,param_2,0x70);
  FUN_43a49628(auStack_198,*(undefined4 *)(param_1 + 4));
  iVar1 = FUN_435aa068(param_1 + 8,DAT_43620c14,auStack_198);
  if (iVar1 == 0) {
    FUN_439c5a04(auStack_88,0,0x70);
    iVar1 = FUN_435a9348(auStack_198,auStack_88,0x70);
    if (iVar1 == 0) {
      if (sStack_82 == 0x1111) {
        FUN_43a8321a(param_1,auStack_88,param_3);
        uVar2 = 0;
        if (uStack_86 != 0) {
          if ((uStack_86 & 0x8000) == 0) {
            uVar2 = FUN_435b3040();
            FUN_43a4e534(uVar2,0x10,0,DAT_43620c3c + 0x43620ba2,DAT_43620c38 + 0x43620b8a,0x114,
                         0xfffffffe,(int)(short)uStack_86);
            uVar2 = 0xfffffffe;
          }
          else {
            uVar2 = FUN_435b3040();
            FUN_43a4e4e8(uVar2,0x10,2,DAT_43620c34 + 0x43620b78,DAT_43620c30 + 0x43620b60,0x111,
                         0xfffffffc,(int)(short)uStack_86);
            uVar2 = 0xfffffffc;
          }
        }
        uVar5 = FUN_435b3040();
        FUN_43a4e534(uVar5,0x10,0,DAT_43620c40 + 0x43620bcc,*param_2,param_2[1],
                     *(undefined4 *)(param_2 + 2),param_2[0xb]);
        if (*param_2 == 0xd) {
          uVar5 = FUN_435b3040();
          FUN_43a4e534(uVar5,0x10,0,DAT_43620c44 + 0x43620bf4,param_2[2],
                       *(undefined4 *)(param_2 + 4),*(undefined4 *)(param_2 + 6),
                       (int)(short)uStack_86);
        }
        goto LAB_43620bfc;
      }
      uVar2 = FUN_435b3040();
      iVar3 = DAT_43620c28 + 0x43620b28;
      uVar5 = 0x103;
      iVar1 = 0;
      iVar4 = DAT_43620c2c + 0x43620b38;
    }
    else {
      uVar2 = FUN_435b3040();
      iVar3 = DAT_43620c20 + 0x43620b04;
      uVar5 = 0xfa;
      iVar4 = DAT_43620c24 + 0x43620b0e;
    }
  }
  else {
    uVar2 = FUN_435b3040();
    iVar3 = DAT_43620c18 + 0x43620ad2;
    uVar5 = 0xf0;
    iVar4 = DAT_43620c1c + 0x43620adc;
  }
  FUN_43a4e4e8(uVar2,0x10,2,iVar4,iVar3,uVar5,iVar1);
  uVar2 = 0xfffffffc;
LAB_43620bfc:
  FUN_435a92c8(auStack_198);
  return uVar2;
}


/* 43629bdc */

void FUN_43629bdc(int param_1,short *param_2,int param_3,undefined4 param_4)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  if (param_3 == DAT_43629c44) {
    FUN_43a89394();
    return;
  }
  if ((((param_3 != DAT_43629c48) && (param_3 != DAT_43629c48 + 0x7a)) && (*param_2 != 0x2006)) &&
     ((*param_2 != 0x1000 || ((param_2[1] != 0x102 && (param_2[1] != -0x7efe)))))) {
    FUN_43a893d8(param_1,param_2,param_3,param_4);
    return;
  }
  FUN_43a89362(param_1,param_1 + 0x6f8,0x14,param_4,param_4);
  sVar1 = *param_2;
  iVar4 = param_1 + *(int *)(param_1 + 0x6f8) * 0x10;
  iVar3 = (*(int *)(param_1 + 0x6f8) + 2) * 0x10;
  *(short *)(iVar4 + 0x1a) = param_2[1];
  *(short *)(iVar4 + 0x18) = sVar1;
  *(int *)(param_1 + iVar3) = param_3;
  *(undefined4 *)(iVar4 + 0x1c) = param_4;
  uVar2 = FUN_43a89370(param_1);
  *(undefined4 *)(param_1 + iVar3 + 4) = uVar2;
  return;
}


/* 43651694 */

int FUN_43651694(undefined4 param_1,undefined2 *param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined1 auStack_1f0 [272];
  short sStack_e0;
  short sStack_de;
  ushort uStack_da;
  undefined2 uStack_70;
  undefined2 uStack_6e;
  int iStack_60;
  ushort uStack_5c;
  undefined1 auStack_20 [6];
  ushort uStack_1a;
  
  FUN_435aa02c(auStack_20);
  FUN_435a92e0(auStack_1f0);
  FUN_439c5a04(&uStack_70,0,0x50);
  FUN_439c5a04(&sStack_e0,0,0x70);
  iVar1 = FUN_43651530(param_1,&uStack_1a);
  if (iVar1 == 0) {
    uStack_6e = *param_2;
    uStack_70 = 6;
    uStack_5c = uStack_1a;
    iStack_60 = iVar1;
    iVar1 = FUN_43a49628(auStack_1f0,DAT_436519b0);
    iVar2 = FUN_435a9304(auStack_1f0,&uStack_70,0x50);
    if (iVar1 == 0 && iVar2 == 0) {
      uVar3 = FUN_435aa068(auStack_20,DAT_436519b4,auStack_1f0);
      if (uVar3 == 0) {
        iVar1 = FUN_43a9759a(param_1,auStack_1f0,&sStack_e0);
        if (iVar1 == 0) {
          if (sStack_e0 == -0x7ffa) {
            if (uStack_1a == uStack_da) {
              iVar2 = FUN_43651648(param_1,(int)sStack_de);
              if (iVar2 == 0) goto LAB_43651988;
              FUN_43651574(param_1,(int)sStack_de);
              FUN_435ab880(DAT_436519b8 + 0x43651906,uStack_6e);
              FUN_435ab880(DAT_436519bc + 0x4365190e);
              FUN_43639190(0x40,0,0x8000,0x50,6,0x1000,0,0x5d8);
              FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5d9);
              FUN_43639204(0x80,0,0x8000,0x8006,uStack_da,0,0x5da);
              uVar4 = 0x5db;
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x4f,6,0x1000,0,0x5cd);
              FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5ce);
              FUN_43639204(0x80,0,0x8000,0x8006,uStack_da,0,0x5cf);
              uVar4 = 0x5d0;
            }
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x4e,6,0x1000,0,0x5c4);
            FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5c5);
            FUN_43639204(0x80,0,0x8000,sStack_e0,uStack_da,0,0x5c6);
            uVar4 = 0x5c7;
          }
          FUN_43639204(0x80,0,0x8000,(int)sStack_de,0,0,uVar4);
          iVar1 = 0x1000;
        }
        else {
          FUN_43639190(0x40,0,0x8000,0x4d,6,iVar1,0,0x5b9);
        }
        goto LAB_43651988;
      }
      FUN_43639190(0x40,0,0x8000,0x4c,6,0x200,0,0x5b2);
      uVar4 = 0x5b3;
    }
    else {
      FUN_43639190(0x40,0,0x8000,0x4b,6,0x200,0,0x5a6);
      FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x5a7);
      uVar3 = (uint)uStack_5c;
      uVar4 = 0x5a8;
    }
    FUN_43639204(0x80,0,0x8000,uVar3,0,0,uVar4);
    iVar1 = 0x200;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x4a,6,iVar1,0,0x598);
    FUN_43639204(0x80,0,0x8000,uStack_1a,0,0,0x599);
  }
LAB_43651988:
  FUN_435a92c8(auStack_1f0);
  FUN_435aa014(auStack_20);
  return iVar1;
}


/* 436519c0 */

int FUN_436519c0(undefined4 param_1,undefined2 *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 *puVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 auStack_270 [272];
  short sStack_160;
  short sStack_15e;
  ushort uStack_15a;
  ushort uStack_158;
  undefined4 auStack_150 [24];
  undefined1 auStack_f0 [16];
  undefined4 auStack_e0 [24];
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined4 uStack_74;
  int iStack_70;
  ushort uStack_6c;
  undefined2 uStack_6a;
  undefined1 auStack_30 [4];
  ushort uStack_2c;
  undefined2 auStack_2a [3];
  
  FUN_435aa02c(auStack_30);
  FUN_435a92e0(auStack_270);
  FUN_439c5a04(&uStack_80,0,0x50);
  FUN_439c5a04(auStack_f0,0,0x70);
  FUN_439c5a04(&sStack_160,0,0x70);
  iVar1 = FUN_43a97568(param_1,*(undefined4 *)(param_2 + 2),auStack_2a);
  if (iVar1 == 0) {
    iVar1 = FUN_43651530(param_1,&uStack_2c);
    if (iVar1 == 0) {
      uStack_80 = 5;
      uStack_74 = 0xffffffff;
      uStack_7e = *param_2;
      uStack_6c = uStack_2c;
      uStack_6a = auStack_2a[0];
      iStack_70 = iVar1;
      iVar1 = FUN_43a49628(auStack_270,DAT_43651d78);
      iVar2 = FUN_435a9304(auStack_270,&uStack_80,0x50);
      if (iVar1 == 0 && iVar2 == 0) {
        uVar4 = FUN_435aa068(auStack_30,DAT_43651d7c,auStack_270);
        if (uVar4 == 0) {
          iVar1 = FUN_43a9759a(param_1,auStack_270,&sStack_160);
          if (iVar1 == 0) {
            uVar4 = 0;
            puVar3 = auStack_150;
            puVar5 = auStack_e0;
            while( true ) {
              if (uStack_158 <= uVar4) break;
              uVar4 = uVar4 + 1;
              *puVar5 = *puVar3;
              puVar5[1] = puVar3[1];
              puVar3 = puVar3 + 2;
              puVar5 = puVar5 + 2;
            }
            if (sStack_160 == -0x7ffb) {
              if (uStack_2c == uStack_15a) {
                iVar2 = FUN_43651648(param_1,(int)sStack_15e);
                if (iVar2 == 0) {
                  param_3[2] = 0;
                  param_3[4] = 0;
                  param_3[6] = 0;
                  param_3[8] = 0;
                  param_3[10] = 0;
                  param_3[0xc] = 0;
                  param_3[0xe] = 0;
                  param_3[0x10] = 0;
                  *(char *)param_3 = (char)uStack_158;
                  uVar4 = 0;
                  puVar3 = auStack_e0;
                  while( true ) {
                    if (uStack_158 <= uVar4) break;
                    uVar4 = uVar4 + 1;
                    param_3[1] = *puVar3;
                    param_3[2] = puVar3[1];
                    param_3 = param_3 + 2;
                    puVar3 = puVar3 + 2;
                  }
                  goto LAB_43651d8c;
                }
                FUN_43651574(param_1,(int)sStack_15e);
                FUN_435ab880(DAT_43651d80 + 0x43651cc4,uStack_7e);
                FUN_435ab880(DAT_43651d84 + 0x43651ccc);
                FUN_43639190(0x40,0,0x8000,0x42,6,0x1000,0,0x507);
                FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x508);
                FUN_43639204(0x80,0,0x8000,0x8005,uStack_15a,0,0x509);
                uVar7 = 0x50a;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x41,6,0x1000,0,0x4fc);
                FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4fd);
                FUN_43639204(0x80,0,0x8000,0x8005,uStack_15a,0,0x4fe);
                uVar7 = 0x4ff;
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x40,6,0x1000,0,0x4f3);
              FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4f4);
              FUN_43639204(0x80,0,0x8000,sStack_160,uStack_15a,0,0x4f5);
              uVar7 = 0x4f6;
            }
            FUN_43639204(0x80,0,0x8000,(int)sStack_15e,0,0,uVar7);
            iVar1 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x3f,6,iVar1,0,0x4e3);
          }
          goto LAB_43651d8c;
        }
        FUN_43639190(0x40,0,0x8000,0x3e,6,0x200,0,0x4dc);
        uVar7 = 0x4dd;
        uVar6 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x3d,6,0x200,0,0x4cf);
        FUN_43639204(0x80,0,0x8000,uStack_7e,0,0,0x4d0);
        uVar4 = (uint)uStack_6c;
        uVar7 = 0x4d1;
        uVar6 = uStack_6a;
      }
      FUN_43639204(0x80,0,0x8000,uVar4,uVar6,0,uVar7);
      iVar1 = 0x200;
      goto LAB_43651d8c;
    }
    FUN_43639190(0x40,0,0x8000,0x3c,6,iVar1,0,0x4bf);
    uVar4 = (uint)uStack_2c;
    uVar7 = 0x4c0;
    auStack_2a[0] = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x3b,6,iVar1,0,0x4b8);
    uVar7 = 0x4b9;
    uVar4 = *(uint *)(param_2 + 2);
  }
  FUN_43639204(0x80,0,0x8000,uVar4,auStack_2a[0],0,uVar7);
LAB_43651d8c:
  FUN_435a92c8(auStack_270);
  FUN_435aa014(auStack_30);
  return iVar1;
}


/* 43651db4 */

int FUN_43651db4(undefined4 param_1,undefined2 *param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  undefined1 auStack_1f0 [272];
  short sStack_e0;
  short sStack_de;
  ushort uStack_da;
  undefined2 uStack_70;
  undefined2 uStack_6e;
  int iStack_60;
  ushort uStack_5c;
  undefined2 uStack_5a;
  undefined1 auStack_20 [4];
  ushort uStack_1c;
  undefined2 uStack_1a;
  
  FUN_435aa02c(auStack_20);
  FUN_435a92e0(auStack_1f0);
  FUN_439c5a04(&uStack_70,0,0x50);
  FUN_439c5a04(&sStack_e0,0,0x70);
  iVar1 = FUN_43a97568(param_1,*(undefined4 *)(param_2 + 2),&uStack_1a);
  if (iVar1 == 0) {
    iVar1 = FUN_43651530(param_1,&uStack_1c);
    if (iVar1 == 0) {
      uStack_70 = 4;
      uStack_6e = *param_2;
      uStack_5c = uStack_1c;
      uStack_5a = uStack_1a;
      iStack_60 = iVar1;
      iVar1 = FUN_43a49628(auStack_1f0,DAT_43652120);
      iVar2 = FUN_435a9304(auStack_1f0,&uStack_70,0x50);
      if (iVar1 == 0 && iVar2 == 0) {
        uVar3 = FUN_435aa068(auStack_20,DAT_43652124,auStack_1f0);
        if (uVar3 == 0) {
          iVar1 = FUN_43a9759a(param_1,auStack_1f0,&sStack_e0);
          if (iVar1 == 0) {
            if (sStack_e0 == -0x7ffc) {
              if (uStack_1c == uStack_da) {
                iVar2 = FUN_43651648(param_1,(int)sStack_de);
                if (iVar2 == 0) goto LAB_436520fa;
                FUN_43651574(param_1,(int)sStack_de);
                FUN_435ab880(DAT_43652128 + 0x43652078,uStack_6e);
                FUN_435ab880(DAT_4365212c + 0x43652080);
                FUN_43639190(0x40,0,0x8000,0x32,6,0x1000,0,0x413);
                FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x414);
                FUN_43639204(0x80,0,0x8000,0x8004,uStack_da,0,0x415);
                uVar5 = 0x416;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x31,6,0x1000,0,0x408);
                FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x409);
                FUN_43639204(0x80,0,0x8000,0x8004,uStack_da,0,0x40a);
                uVar5 = 0x40b;
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x30,6,0x1000,0,0x3ff);
              FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x400);
              FUN_43639204(0x80,0,0x8000,sStack_e0,uStack_da,0,0x401);
              uVar5 = 0x402;
            }
            FUN_43639204(0x80,0,0x8000,(int)sStack_de,0,0,uVar5);
            iVar1 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x2f,6,iVar1,0,0x3f4);
          }
          goto LAB_436520fa;
        }
        FUN_43639190(0x40,0,0x8000,0x2e,6,0x200,0,0x3ed);
        uVar5 = 0x3ee;
        uVar4 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x2d,6,0x200,0,0x3e0);
        FUN_43639204(0x80,0,0x8000,uStack_6e,0,0,0x3e1);
        uVar3 = (uint)uStack_5c;
        uVar5 = 0x3e2;
        uVar4 = uStack_5a;
      }
      FUN_43639204(0x80,0,0x8000,uVar3,uVar4,0,uVar5);
      iVar1 = 0x200;
      goto LAB_436520fa;
    }
    FUN_43639190(0x40,0,0x8000,0x2c,6,iVar1,0,0x3d1);
    uVar3 = (uint)uStack_1c;
    uVar5 = 0x3d2;
    uStack_1a = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x2b,6,iVar1,0,0x3ca);
    uVar5 = 0x3cb;
    uVar3 = *(uint *)(param_2 + 2);
  }
  FUN_43639204(0x80,0,0x8000,uVar3,uStack_1a,0,uVar5);
LAB_436520fa:
  FUN_435a92c8(auStack_1f0);
  FUN_435aa014(auStack_20);
  return iVar1;
}


/* 43652130 */

int FUN_43652130(undefined4 param_1,undefined2 *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 *puVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 auStack_270 [272];
  short sStack_160;
  short sStack_15e;
  undefined2 uStack_15c;
  ushort uStack_15a;
  ushort uStack_158;
  undefined4 auStack_150 [24];
  undefined1 auStack_f0 [16];
  undefined4 auStack_e0 [24];
  undefined2 uStack_80;
  undefined2 uStack_7e;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  int iStack_70;
  ushort uStack_6c;
  undefined2 uStack_6a;
  undefined1 auStack_30 [4];
  ushort uStack_2c;
  undefined2 auStack_2a [3];
  
  FUN_435aa02c(auStack_30);
  FUN_435a92e0(auStack_270);
  FUN_439c5a04(&uStack_80,0,0x50);
  FUN_439c5a04(auStack_f0,0,0x70);
  FUN_439c5a04(&sStack_160,0,0x70);
  iVar1 = FUN_43a97568(param_1,*(undefined4 *)(param_2 + 6),auStack_2a);
  if (iVar1 == 0) {
    iVar1 = FUN_43651530(param_1,&uStack_2c);
    if (iVar1 == 0) {
      uStack_7c = *(undefined4 *)(param_2 + 2);
      uStack_80 = 2;
      uStack_78 = *(undefined4 *)(param_2 + 4);
      uStack_7e = *param_2;
      uStack_6a = auStack_2a[0];
      uStack_6c = uStack_2c;
      iStack_70 = iVar1;
      iVar1 = FUN_43a49628(auStack_270,DAT_436524f0);
      iVar2 = FUN_435a9304(auStack_270,&uStack_80,0x50);
      if (iVar1 == 0 && iVar2 == 0) {
        uVar4 = FUN_435aa068(auStack_30,DAT_436524f4,auStack_270);
        if (uVar4 == 0) {
          iVar1 = FUN_43a9759a(param_1,auStack_270,&sStack_160);
          if (iVar1 == 0) {
            uVar4 = 0;
            puVar3 = auStack_150;
            puVar5 = auStack_e0;
            while( true ) {
              if (uStack_158 <= uVar4) break;
              uVar4 = uVar4 + 1;
              *puVar5 = *puVar3;
              puVar5[1] = puVar3[1];
              puVar3 = puVar3 + 2;
              puVar5 = puVar5 + 2;
            }
            if (sStack_160 == -0x7ffe) {
              if (uStack_2c == uStack_15a) {
                iVar2 = FUN_43651648(param_1,(int)sStack_15e);
                if (iVar2 == 0) {
                  uVar4 = *(uint *)(param_2 + 6);
                  *(undefined2 *)param_3 = uStack_15c;
                  if ((uVar4 & 3) == 0) {
                    *(undefined1 *)(param_3 + 1) = 0;
                  }
                  else {
                    param_3[3] = 0;
                    param_3[5] = 0;
                    param_3[7] = 0;
                    param_3[9] = 0;
                    param_3[0xb] = 0;
                    param_3[0xd] = 0;
                    param_3[0xf] = 0;
                    param_3[0x11] = 0;
                    *(char *)(param_3 + 1) = (char)uStack_158;
                    uVar4 = 0;
                    puVar3 = auStack_e0;
                    while( true ) {
                      if (uStack_158 <= uVar4) break;
                      uVar4 = uVar4 + 1;
                      param_3[2] = *puVar3;
                      param_3[3] = puVar3[1];
                      param_3 = param_3 + 2;
                      puVar3 = puVar3 + 2;
                    }
                  }
                  goto LAB_43652528;
                }
                FUN_43651574(param_1,(int)sStack_15e);
                FUN_435ab880(DAT_436524f8 + 0x43652450,uStack_7e);
                FUN_435ab880(DAT_436524fc + 0x43652458);
                FUN_43639190(0x40,0,0x8000,0x2a,6,0x1000,0,0x35f);
                FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,0x360);
                FUN_43639204(0x80,0,0x8000,0x8002,uStack_15a,0,0x361);
                uVar7 = 0x362;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x29,6,0x1000,0,0x354);
                FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,0x355);
                FUN_43639204(0x80,0,0x8000,0x8002,uStack_15a,0,0x356);
                uVar7 = 0x357;
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x28,6,0x1000,0,0x34b);
              FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,0x34c);
              FUN_43639204(0x80,0,0x8000,sStack_160,uStack_15a,0,0x34d);
              uVar7 = 0x34e;
            }
            FUN_43639204(0x80,0,0x8000,(int)sStack_15e,0,0,uVar7);
            iVar1 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x27,6,iVar1,0,0x33a);
          }
          goto LAB_43652528;
        }
        FUN_43639190(0x40,0,0x8000,0x26,6,0x200,0,0x333);
        uVar7 = 0x334;
        uVar6 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x25,6,0x200,0,0x324);
        FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_7e,0,0x325);
        FUN_43639204(0x80,0,0x8000,uStack_78,0,0,0x326);
        uVar4 = (uint)uStack_6c;
        uVar7 = 0x327;
        uVar6 = uStack_6a;
      }
      FUN_43639204(0x80,0,0x8000,uVar4,uVar6,0,uVar7);
      iVar1 = 0x200;
      goto LAB_43652528;
    }
    FUN_43639190(0x40,0,0x8000,0x24,6,iVar1,0,0x313);
    uVar4 = (uint)uStack_2c;
    uVar7 = 0x314;
    auStack_2a[0] = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x23,6,iVar1,0,0x30c);
    uVar7 = 0x30d;
    uVar4 = *(uint *)(param_2 + 6);
  }
  FUN_43639204(0x80,0,0x8000,uVar4,auStack_2a[0],0,uVar7);
LAB_43652528:
  FUN_435a92c8(auStack_270);
  FUN_435aa014(auStack_30);
  return iVar1;
}


/* 43652550 */

int FUN_43652550(undefined4 param_1,undefined4 *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 *puVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  undefined1 auStack_270 [272];
  short sStack_160;
  short sStack_15e;
  undefined2 uStack_15c;
  ushort uStack_15a;
  ushort uStack_158;
  undefined4 auStack_150 [24];
  undefined1 auStack_f0 [16];
  undefined4 auStack_e0 [24];
  undefined2 auStack_80 [2];
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  int iStack_70;
  ushort uStack_6c;
  undefined2 uStack_6a;
  undefined1 auStack_30 [4];
  ushort uStack_2c;
  undefined2 auStack_2a [3];
  
  FUN_435aa02c(auStack_30);
  FUN_435a92e0(auStack_270);
  FUN_439c5a04(auStack_80,0,0x50);
  FUN_439c5a04(auStack_f0,0,0x70);
  FUN_439c5a04(&sStack_160,0,0x70);
  iVar1 = FUN_43a97568(param_1,param_2[2],auStack_2a);
  if (iVar1 == 0) {
    iVar1 = FUN_43651530(param_1,&uStack_2c);
    if (iVar1 == 0) {
      uStack_7c = *param_2;
      auStack_80[0] = 1;
      uStack_78 = param_2[1];
      uStack_74 = 0xffffffff;
      uStack_6c = uStack_2c;
      uStack_6a = auStack_2a[0];
      iStack_70 = iVar1;
      iVar1 = FUN_43a49628(auStack_270,DAT_43652900);
      iVar2 = FUN_435a9304(auStack_270,auStack_80,0x50);
      if (iVar1 == 0 && iVar2 == 0) {
        uVar4 = FUN_435aa068(auStack_30,DAT_43652904,auStack_270);
        if (uVar4 == 0) {
          iVar1 = FUN_43a9759a(param_1,auStack_270,&sStack_160);
          if (iVar1 == 0) {
            uVar4 = 0;
            puVar3 = auStack_150;
            puVar5 = auStack_e0;
            while( true ) {
              if (uStack_158 <= uVar4) break;
              uVar4 = uVar4 + 1;
              *puVar5 = *puVar3;
              puVar5[1] = puVar3[1];
              puVar3 = puVar3 + 2;
              puVar5 = puVar5 + 2;
            }
            if (sStack_160 == -0x7fff) {
              if (uStack_2c == uStack_15a) {
                iVar2 = FUN_43651648(param_1,(int)sStack_15e);
                if (iVar2 == 0) {
                  uVar4 = param_2[2];
                  *(undefined2 *)param_3 = uStack_15c;
                  if ((uVar4 & 3) == 0) {
                    *(undefined1 *)(param_3 + 1) = 0;
                  }
                  else {
                    param_3[3] = 0;
                    param_3[5] = 0;
                    param_3[7] = 0;
                    param_3[9] = 0;
                    param_3[0xb] = 0;
                    param_3[0xd] = 0;
                    param_3[0xf] = 0;
                    param_3[0x11] = 0;
                    *(char *)(param_3 + 1) = (char)uStack_158;
                    uVar4 = 0;
                    puVar3 = auStack_e0;
                    while( true ) {
                      if (uStack_158 <= uVar4) break;
                      uVar4 = uVar4 + 1;
                      param_3[2] = *puVar3;
                      param_3[3] = puVar3[1];
                      param_3 = param_3 + 2;
                      puVar3 = puVar3 + 2;
                    }
                  }
                  goto LAB_43652938;
                }
                FUN_43651574(param_1,(int)sStack_15e);
                FUN_435ab880(DAT_43652908 + 0x4365285a,uStack_7c);
                FUN_435ab880(DAT_4365290c + 0x43652862);
                if (sStack_15e != 6) {
                  FUN_43639190(0x40,0,0x8000,0x22,6,0x1000,0,0x2d1);
                }
                FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,0x2d3);
                FUN_43639204(0x80,0,0x8000,0x8001,uStack_15a,0,0x2d4);
                uVar7 = 0x2d5;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x21,6,0x1000,0,0x2c4);
                FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,0x2c5);
                FUN_43639204(0x80,0,0x8000,0x8001,uStack_15a,0,0x2c6);
                uVar7 = 0x2c7;
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x20,6,0x1000,0,699);
              FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_15c,0,700);
              FUN_43639204(0x80,0,0x8000,sStack_160,uStack_15a,0,0x2bd);
              uVar7 = 0x2be;
            }
            FUN_43639204(0x80,0,0x8000,(int)sStack_15e,0,0,uVar7);
            iVar1 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x1f,6,iVar1,0,0x2aa);
          }
          goto LAB_43652938;
        }
        FUN_43639190(0x40,0,0x8000,0x1e,6,0x200,0,0x2a3);
        uVar7 = 0x2a4;
        uVar6 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x1d,6,0x200,0,0x296);
        FUN_43639204(0x80,0,0x8000,uStack_7c,uStack_78,0,0x297);
        uVar4 = (uint)uStack_6c;
        uVar7 = 0x298;
        uVar6 = uStack_6a;
      }
      FUN_43639204(0x80,0,0x8000,uVar4,uVar6,0,uVar7);
      iVar1 = 0x200;
      goto LAB_43652938;
    }
    FUN_43639190(0x40,0,0x8000,0x1c,6,iVar1,0,0x285);
    uVar4 = (uint)uStack_2c;
    uVar7 = 0x286;
    auStack_2a[0] = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x1b,6,iVar1,0,0x27e);
    uVar7 = 0x27f;
    uVar4 = param_2[2];
  }
  FUN_43639204(0x80,0,0x8000,uVar4,auStack_2a[0],0,uVar7);
LAB_43652938:
  FUN_435a92c8(auStack_270);
  FUN_435aa014(auStack_30);
  return iVar1;
}


/* 43652960 */

int FUN_43652960(undefined4 param_1,int param_2,undefined4 *param_3,undefined4 *param_4)

{
  short sVar1;
  short sVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined2 uVar9;
  undefined4 uVar10;
  undefined1 auStack_28 [4];
  ushort uStack_24;
  undefined2 uStack_22;
  
  FUN_435aa02c(auStack_28);
  iVar5 = FUN_43a97568(param_1,param_3[2],&uStack_22);
  if (iVar5 == 0) {
    iVar5 = FUN_43651530(param_1,&uStack_24);
    if (iVar5 == 0) {
      *(undefined2 *)(param_2 + 0x110) = 1;
      uVar10 = DAT_43652cf8;
      *(undefined4 *)(param_2 + 0x114) = *param_3;
      uVar8 = param_3[1];
      *(undefined4 *)(param_2 + 0x120) = 0;
      *(undefined4 *)(param_2 + 0x118) = uVar8;
      *(undefined4 *)(param_2 + 0x11c) = 0xffffffff;
      *(ushort *)(param_2 + 0x124) = uStack_24;
      *(undefined2 *)(param_2 + 0x126) = uStack_22;
      iVar5 = FUN_43a49628(param_2,uVar10);
      iVar6 = FUN_435a9304(param_2,param_2 + 0x110,0x50);
      if (iVar5 == 0 && iVar6 == 0) {
        uVar7 = FUN_435aa068(auStack_28,DAT_43652cfc,param_2);
        if (uVar7 == 0) {
          iVar5 = FUN_43a9759a(param_1,param_2,param_2 + 0x1d0);
          if (iVar5 == 0) {
            sVar1 = *(short *)(param_2 + 0x1d0);
            sVar2 = *(short *)(param_2 + 0x1d2);
            uVar3 = *(ushort *)(param_2 + 0x1d6);
            uVar4 = *(ushort *)(param_2 + 0x1d8);
            *(undefined2 *)(param_2 + 0x164) = *(undefined2 *)(param_2 + 0x1d4);
            *(short *)(param_2 + 0x160) = sVar1;
            *(short *)(param_2 + 0x162) = sVar2;
            *(ushort *)(param_2 + 0x166) = uVar3;
            *(ushort *)(param_2 + 0x168) = uVar4;
            iVar6 = param_2;
            for (uVar7 = 0; uVar7 < uVar4; uVar7 = uVar7 + 1) {
              *(undefined4 *)(iVar6 + 0x170) = *(undefined4 *)(iVar6 + 0x1e0);
              *(undefined4 *)(iVar6 + 0x174) = *(undefined4 *)(iVar6 + 0x1e4);
              iVar6 = iVar6 + 8;
            }
            if (sVar1 == -0x7fff) {
              if (uStack_24 == uVar3) {
                iVar6 = FUN_43651648(param_1,(int)sVar2);
                if (iVar6 == 0) {
                  *(undefined2 *)param_4 = *(undefined2 *)(param_2 + 0x164);
                  if ((param_3[2] & 3) == 0) {
                    *(undefined1 *)(param_4 + 1) = 0;
                  }
                  else {
                    uVar9 = *(undefined2 *)(param_2 + 0x168);
                    param_4[3] = 0;
                    param_4[5] = 0;
                    *(char *)(param_4 + 1) = (char)uVar9;
                    param_4[7] = 0;
                    param_4[9] = 0;
                    param_4[0xb] = 0;
                    param_4[0xd] = 0;
                    param_4[0xf] = 0;
                    param_4[0x11] = 0;
                    uVar3 = *(ushort *)(param_2 + 0x168);
                    uVar7 = 0;
                    while( true ) {
                      if (uVar3 <= uVar7) break;
                      uVar7 = uVar7 + 1;
                      param_4[2] = *(undefined4 *)(param_2 + 0x170);
                      param_4[3] = *(undefined4 *)(param_2 + 0x174);
                      param_4 = param_4 + 2;
                      param_2 = param_2 + 8;
                    }
                  }
                  goto LAB_43652d5a;
                }
                FUN_43651574(param_1,(int)*(short *)(param_2 + 0x162));
                FUN_435ab880(DAT_43652d00 + 0x43652c6c,*(undefined4 *)(param_2 + 0x114));
                FUN_435ab880(DAT_43652d04 + 0x43652c74);
                if (*(short *)(param_2 + 0x162) != 6) {
                  FUN_43639190(0x40,0,0x8000,0x1a,6,0x1000,0,0x244);
                }
                FUN_43639204(0x80,0,0x8000,*(undefined4 *)(param_2 + 0x114),
                             *(undefined2 *)(param_2 + 0x164),0,0x246);
                FUN_43639204(0x80,0,0x8000,*(undefined2 *)(param_2 + 0x160),
                             *(undefined2 *)(param_2 + 0x166),0,0x247);
                sVar1 = *(short *)(param_2 + 0x162);
                uVar10 = 0x248;
              }
              else {
                FUN_43639190(0x40,0,0x8000,0x19,6,0x1000,0,0x237);
                FUN_43639204(0x80,0,0x8000,*(undefined4 *)(param_2 + 0x114),
                             *(undefined2 *)(param_2 + 0x164),0,0x238);
                FUN_43639204(0x80,0,0x8000,*(undefined2 *)(param_2 + 0x160),
                             *(undefined2 *)(param_2 + 0x166),0,0x239);
                uVar10 = 0x23a;
                sVar1 = *(short *)(param_2 + 0x162);
              }
            }
            else {
              FUN_43639190(0x40,0,0x8000,0x18,6,0x1000,0,0x22e);
              FUN_43639204(0x80,0,0x8000,*(undefined4 *)(param_2 + 0x114),
                           *(undefined2 *)(param_2 + 0x164),0,0x22f);
              FUN_43639204(0x80,0,0x8000,*(undefined2 *)(param_2 + 0x160),
                           *(undefined2 *)(param_2 + 0x166),0,0x230);
              sVar1 = *(short *)(param_2 + 0x162);
              uVar10 = 0x231;
            }
            FUN_43639204(0x80,0,0x8000,(int)sVar1,0,0,uVar10);
            iVar5 = 0x1000;
          }
          else {
            FUN_43639190(0x40,0,0x8000,0x17,6,iVar5,0,0x21d);
          }
          goto LAB_43652d5a;
        }
        FUN_43639190(0x40,0,0x8000,0x16,6,0x200,0,0x216);
        uVar10 = 0x217;
        uVar9 = 0;
      }
      else {
        FUN_43639190(0x40,0,0x8000,0x15,6,0x200,0,0x209);
        FUN_43639204(0x80,0,0x8000,*(undefined4 *)(param_2 + 0x114),*(undefined4 *)(param_2 + 0x118)
                     ,0,0x20a);
        uVar9 = *(undefined2 *)(param_2 + 0x126);
        uVar7 = (uint)*(ushort *)(param_2 + 0x124);
        uVar10 = 0x20b;
      }
      FUN_43639204(0x80,0,0x8000,uVar7,uVar9,0,uVar10);
      iVar5 = 0x200;
      goto LAB_43652d5a;
    }
    FUN_43639190(0x40,0,0x8000,0x14,6,iVar5,0,0x1f8);
    uVar7 = (uint)uStack_24;
    uVar10 = 0x1f9;
    uStack_22 = 0;
  }
  else {
    FUN_43639190(0x40,0,0x8000,0x13,6,iVar5,0,0x1f1);
    uVar10 = 0x1f2;
    uVar7 = param_3[2];
  }
  FUN_43639204(0x80,0,0x8000,uVar7,uStack_22,0,uVar10);
LAB_43652d5a:
  FUN_435aa014(auStack_28);
  return iVar5;
}


/* 4366f260 */

int FUN_4366f260(undefined4 param_1,undefined4 param_2,undefined4 *param_3)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_2c [16];
  undefined2 *puStack_1c;
  
  puVar4 = (undefined4 *)FUN_43672b80();
  *(undefined2 *)((int)param_3 + 6) = 0;
  *(undefined2 *)(param_3 + 1) = 0;
  FUN_435612d0(DAT_4366f318,&puStack_1c,0x50,1);
  puVar3 = puStack_1c;
  *puStack_1c = 1;
  *(undefined4 *)(puStack_1c + 2) = param_1;
  *(undefined4 *)(puStack_1c + 6) = 0xffffffff;
  *(undefined4 *)(puStack_1c + 4) = param_2;
  puStack_1c[10] = 0;
  puStack_1c[0xb] = 0;
  FUN_4366f254(puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f320 + 0x4366f2ba);
  FUN_43561228(DAT_4366f318,puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f324 + 0x4366f2ce);
  *(undefined2 *)((int)param_3 + 6) = 0;
  uVar1 = puVar3[2];
  sVar2 = puVar3[1];
  *param_3 = param_1;
  *(undefined2 *)(param_3 + 1) = uVar1;
  FUN_435612ec(DAT_4366f318,puStack_1c);
  iVar5 = FUN_43aafb5a((int)sVar2);
  if (iVar5 != 0) {
    uVar6 = FUN_4366fed0();
    FUN_43aaf49e(auStack_2c,DAT_4366f31c,1,sVar2,param_1,param_2);
    FUN_43aaf4d8(uVar6,auStack_2c);
  }
  return iVar5;
}


/* 4366f3f8 */

int FUN_4366f3f8(int param_1)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_2c [16];
  undefined2 *puStack_1c;
  
  puVar4 = (undefined4 *)FUN_43672b80();
  FUN_435612d0(DAT_4366f488,&puStack_1c,0x50,1);
  puVar3 = puStack_1c;
  *puStack_1c = 6;
  uVar1 = *(undefined2 *)(param_1 + 4);
  puStack_1c[10] = 0;
  puStack_1c[1] = uVar1;
  FUN_4366f254(puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f490 + 0x4366f436);
  FUN_43561228(DAT_4366f488,puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f494 + 0x4366f44a);
  sVar2 = puVar3[1];
  FUN_435612ec(DAT_4366f488,puStack_1c);
  iVar5 = FUN_43aafb5a((int)sVar2);
  if (iVar5 != 0) {
    uVar6 = FUN_4366fed0();
    FUN_43aaf49e(auStack_2c,DAT_4366f48c,1,sVar2,0,*(undefined2 *)(param_1 + 4));
    FUN_43aaf4d8(uVar6,auStack_2c);
  }
  return iVar5;
}


/* 4366f498 */

int FUN_4366f498(int param_1)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined1 auStack_2c [16];
  undefined2 *puStack_1c;
  
  puVar4 = (undefined4 *)FUN_43672b80();
  *(undefined2 *)(param_1 + 6) = 0;
  FUN_435612d0(DAT_4366f554,&puStack_1c,0x50,1);
  puVar3 = puStack_1c;
  *puStack_1c = 5;
  uVar1 = *(undefined2 *)(param_1 + 4);
  *(undefined4 *)(puStack_1c + 6) = 0;
  puStack_1c[10] = 0;
  puStack_1c[1] = uVar1;
  puStack_1c[0xb] = 0;
  FUN_4366f254(puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f55c + 0x4366f4d8);
  FUN_43561228(DAT_4366f554,puStack_1c);
  (**(code **)*puVar4)(puVar4,DAT_4366f560 + 0x4366f4ec);
  *(undefined2 *)(param_1 + 6) = puVar3[4];
  uVar6 = *(undefined4 *)(puVar3 + 10);
  uVar7 = *(undefined4 *)(puVar3 + 0xc);
  uVar8 = *(undefined4 *)(puVar3 + 0xe);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(puVar3 + 8);
  *(undefined4 *)(param_1 + 0x10) = uVar6;
  *(undefined4 *)(param_1 + 0x14) = uVar7;
  *(undefined4 *)(param_1 + 0x18) = uVar8;
  uVar6 = *(undefined4 *)(puVar3 + 0x12);
  uVar7 = *(undefined4 *)(puVar3 + 0x14);
  uVar8 = *(undefined4 *)(puVar3 + 0x16);
  *(undefined4 *)(param_1 + 0x1c) = *(undefined4 *)(puVar3 + 0x10);
  *(undefined4 *)(param_1 + 0x20) = uVar6;
  *(undefined4 *)(param_1 + 0x24) = uVar7;
  *(undefined4 *)(param_1 + 0x28) = uVar8;
  uVar6 = *(undefined4 *)(puVar3 + 0x1a);
  uVar7 = *(undefined4 *)(puVar3 + 0x1c);
  uVar8 = *(undefined4 *)(puVar3 + 0x1e);
  *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(puVar3 + 0x18);
  *(undefined4 *)(param_1 + 0x30) = uVar6;
  *(undefined4 *)(param_1 + 0x34) = uVar7;
  *(undefined4 *)(param_1 + 0x38) = uVar8;
  uVar6 = *(undefined4 *)(puVar3 + 0x22);
  uVar7 = *(undefined4 *)(puVar3 + 0x24);
  uVar8 = *(undefined4 *)(puVar3 + 0x26);
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(puVar3 + 0x20);
  *(undefined4 *)(param_1 + 0x40) = uVar6;
  *(undefined4 *)(param_1 + 0x44) = uVar7;
  *(undefined4 *)(param_1 + 0x48) = uVar8;
  sVar2 = puVar3[1];
  FUN_435612ec(DAT_4366f554,puStack_1c);
  iVar5 = FUN_43aafb5a((int)sVar2);
  if (iVar5 != 0) {
    uVar6 = FUN_4366fed0();
    FUN_43aaf49e(auStack_2c,DAT_4366f558,1,sVar2,0,*(undefined2 *)(param_1 + 4));
    FUN_43aaf4d8(uVar6,auStack_2c);
  }
  return iVar5;
}


/* 4366f624 */

int FUN_4366f624(undefined4 param_1,undefined4 param_2,undefined4 *param_3)

{
  short sVar1;
  undefined2 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined1 auStack_2c [16];
  undefined2 *puStack_1c;
  
  puVar3 = (undefined4 *)FUN_43672b80();
  *(undefined2 *)((int)param_3 + 6) = 0;
  *(undefined2 *)(param_3 + 1) = 0;
  FUN_435612d0(DAT_4366f6f0,&puStack_1c,0x50,1);
  puVar2 = puStack_1c;
  *puStack_1c = 1;
  *(undefined4 *)(puStack_1c + 2) = param_1;
  *(undefined4 *)(puStack_1c + 6) = 0xffffffff;
  *(undefined4 *)(puStack_1c + 4) = param_2;
  puStack_1c[10] = 0;
  puStack_1c[0xb] = 1;
  FUN_4366f254(puStack_1c);
  (**(code **)*puVar3)(puVar3,DAT_4366f6f8 + 0x4366f674);
  FUN_43561228(DAT_4366f6f0,puStack_1c);
  (**(code **)*puVar3)(puVar3,DAT_4366f6fc + 0x4366f688);
  *(undefined2 *)((int)param_3 + 6) = puVar2[4];
  *(undefined2 *)(param_3 + 1) = puVar2[2];
  *param_3 = param_1;
  uVar5 = *(undefined4 *)(puVar2 + 10);
  uVar6 = *(undefined4 *)(puVar2 + 0xc);
  uVar7 = *(undefined4 *)(puVar2 + 0xe);
  param_3[3] = *(undefined4 *)(puVar2 + 8);
  param_3[4] = uVar5;
  param_3[5] = uVar6;
  param_3[6] = uVar7;
  uVar5 = *(undefined4 *)(puVar2 + 0x12);
  uVar6 = *(undefined4 *)(puVar2 + 0x14);
  uVar7 = *(undefined4 *)(puVar2 + 0x16);
  param_3[7] = *(undefined4 *)(puVar2 + 0x10);
  param_3[8] = uVar5;
  param_3[9] = uVar6;
  param_3[10] = uVar7;
  uVar5 = *(undefined4 *)(puVar2 + 0x1a);
  uVar6 = *(undefined4 *)(puVar2 + 0x1c);
  uVar7 = *(undefined4 *)(puVar2 + 0x1e);
  param_3[0xb] = *(undefined4 *)(puVar2 + 0x18);
  param_3[0xc] = uVar5;
  param_3[0xd] = uVar6;
  param_3[0xe] = uVar7;
  uVar5 = *(undefined4 *)(puVar2 + 0x22);
  uVar6 = *(undefined4 *)(puVar2 + 0x24);
  uVar7 = *(undefined4 *)(puVar2 + 0x26);
  param_3[0xf] = *(undefined4 *)(puVar2 + 0x20);
  param_3[0x10] = uVar5;
  param_3[0x11] = uVar6;
  param_3[0x12] = uVar7;
  sVar1 = puVar2[1];
  FUN_435612ec(DAT_4366f6f0,puStack_1c);
  iVar4 = FUN_43aafb4e((int)sVar1);
  if (iVar4 != 0) {
    uVar5 = FUN_4366fed0();
    FUN_43aaf49e(auStack_2c,DAT_4366f6f4,1,sVar1,param_1,param_2);
    FUN_43aaf4d8(uVar5,auStack_2c);
  }
  return iVar4;
}


/* 4366f700 */

int FUN_4366f700(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined1 auStack_48 [16];
  undefined1 auStack_38 [16];
  undefined1 auStack_28 [4];
  undefined4 uStack_24;
  undefined2 *puStack_20;
  undefined1 auStack_1c [2];
  ushort uStack_1a;
  
  puVar4 = (undefined4 *)FUN_43672b80();
  FUN_435612d0(DAT_4366f850,&puStack_20,0x50,1);
  puVar3 = puStack_20;
  if ((param_2 == -1) || (param_3 == -1)) {
    *puStack_20 = 4;
    puStack_20[1] = *(undefined2 *)(param_1 + 4);
    puStack_20[10] = 0;
    puStack_20[0xb] = 2;
    FUN_4366f254(puStack_20);
    (**(code **)*puVar4)(puVar4,DAT_4366f860 + 0x4366f7f6);
    FUN_43561228(DAT_4366f850,puStack_20);
    (**(code **)*puVar4)(puVar4,DAT_4366f864 + 0x4366f80a);
    sVar2 = puVar3[1];
    FUN_435612ec(DAT_4366f850,puStack_20);
    iVar5 = FUN_43aafb4e((int)sVar2);
    if (iVar5 == 0) goto LAB_4366f842;
    uVar6 = FUN_4366fed0();
    FUN_43aaf49e(auStack_48,DAT_4366f854,2,sVar2,param_2,*(undefined2 *)(param_1 + 4));
    register0x00000054 = (BADSPACEBASE *)&stack0xfffffff0;
  }
  else {
    uStack_24 = 0;
    FUN_4366c224(&uStack_24,&uStack_1a,auStack_1c,auStack_28);
    if (0x1000 < uStack_1a) {
      uStack_1a = 0xfff;
    }
    iVar7 = param_2 * 0x100 + ((int)(uint)uStack_1a >> 4 & 0xffU);
    *puVar3 = 0xd;
    uVar1 = *(undefined2 *)(param_1 + 4);
    *(int *)(puVar3 + 6) = param_3;
    *(int *)(puVar3 + 4) = iVar7;
    puVar3[1] = uVar1;
    puVar3[10] = 0;
    puVar3[2] = 0;
    puVar3[0xb] = 2;
    FUN_4366f254(puStack_20);
    (**(code **)*puVar4)(puVar4,DAT_4366f858 + 0x4366f788);
    FUN_43561228(DAT_4366f850,puStack_20);
    (**(code **)*puVar4)(puVar4,DAT_4366f85c + 0x4366f79c);
    sVar2 = puVar3[1];
    FUN_435612ec(DAT_4366f850,puStack_20);
    iVar5 = FUN_43aafb4e((int)sVar2);
    if (iVar5 == 0) goto LAB_4366f842;
    uVar6 = FUN_4366fed0();
    FUN_43aaf49e(auStack_38,DAT_4366f854,1,sVar2,iVar7,*(undefined2 *)(param_1 + 4));
  }
  FUN_43aaf4d8(uVar6,(undefined1 *)((int)register0x00000054 + -0x38));
LAB_4366f842:
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
  return iVar5;
}


/* 436abb34 */

void FUN_436abb34(undefined4 param_1,undefined2 *param_2,undefined4 *param_3)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined2 *puStack_1c;
  
  *(undefined2 *)((int)param_3 + 6) = 0;
  *(undefined2 *)(param_3 + 1) = 0;
  puStack_1c = param_2;
  FUN_435612d0(DAT_436abba0,&puStack_1c,0x50,1,param_1);
  puVar3 = puStack_1c;
  *puStack_1c = 1;
  *(undefined4 *)(puStack_1c + 2) = param_1;
  *(undefined4 *)(puStack_1c + 6) = 0xffffffff;
  *(undefined2 **)(puStack_1c + 4) = param_2;
  puStack_1c[10] = 0;
  puStack_1c[0xb] = 0;
  FUN_436abb28(puStack_1c);
  FUN_43561228(DAT_436abba0,puStack_1c);
  uVar1 = puVar3[2];
  *(undefined2 *)((int)param_3 + 6) = 0;
  *param_3 = param_1;
  *(undefined2 *)(param_3 + 1) = uVar1;
  sVar2 = puVar3[1];
  FUN_435612ec(DAT_436abba0,puStack_1c);
  FUN_43ac5f3a((int)sVar2);
  return;
}


/* 436abc1c */

void FUN_436abc1c(int param_1,undefined2 *param_2,undefined4 param_3)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined2 *puStack_14;
  undefined4 uStack_10;
  
  puStack_14 = param_2;
  uStack_10 = param_3;
  FUN_435612d0(DAT_436abc5c,&puStack_14,0x50,1,param_1);
  puVar3 = puStack_14;
  uVar1 = *(undefined2 *)(param_1 + 4);
  *puStack_14 = 6;
  puStack_14[1] = uVar1;
  puStack_14[10] = 0;
  FUN_436abb28(puStack_14);
  FUN_43561228(DAT_436abc5c,puStack_14);
  sVar2 = puVar3[1];
  FUN_435612ec(DAT_436abc5c,puStack_14);
  FUN_43ac5f3a((int)sVar2);
  return;
}


/* 436abcbc */

void FUN_436abcbc(undefined4 *param_1,undefined2 *param_2,undefined2 *param_3)

{
  short sVar1;
  undefined2 *puVar2;
  undefined4 uVar3;
  undefined2 *puStack_1c;
  undefined2 *puStack_18;
  
  puStack_1c = param_2;
  puStack_18 = param_3;
  FUN_435612d0(DAT_436abd0c,&puStack_1c,0x50,1,param_1);
  puVar2 = puStack_1c;
  *puStack_1c = 2;
  puStack_1c[1] = *(undefined2 *)(param_1 + 1);
  uVar3 = *param_1;
  *(undefined2 **)(puStack_1c + 4) = param_2;
  *(undefined4 *)(puStack_1c + 2) = uVar3;
  puStack_1c[10] = 0;
  puStack_1c[0xb] = 0;
  FUN_436abb28(puStack_1c);
  FUN_43561228(DAT_436abd0c,puStack_1c);
  uVar3 = DAT_436abd0c;
  *param_3 = puVar2[2];
  sVar1 = puVar2[1];
  FUN_435612ec(uVar3,puStack_1c);
  FUN_43ac5f3a((int)sVar1);
  return;
}


/* 436abd7c */

void FUN_436abd7c(undefined4 param_1,undefined4 param_2,undefined4 *param_3)

{
  short sVar1;
  undefined2 *puVar2;
  undefined4 uVar3;
  undefined2 *apuStack_1c [2];
  
  *(undefined2 *)((int)param_3 + 6) = 0;
  *(undefined2 *)(param_3 + 1) = 0;
  FUN_435612d0(DAT_436abdec,apuStack_1c,0x50,1);
  puVar2 = apuStack_1c[0];
  *apuStack_1c[0] = 1;
  *(undefined4 *)(apuStack_1c[0] + 2) = param_1;
  *(undefined4 *)(apuStack_1c[0] + 4) = param_2;
  *(undefined4 *)(apuStack_1c[0] + 6) = 0xffffffff;
  apuStack_1c[0][10] = 0;
  apuStack_1c[0][0xb] = 1;
  FUN_436abb28(apuStack_1c[0]);
  FUN_43561228(DAT_436abdec,apuStack_1c[0]);
  *(undefined2 *)((int)param_3 + 6) = puVar2[4];
  *(undefined2 *)(param_3 + 1) = puVar2[2];
  *param_3 = param_1;
  uVar3 = *(undefined4 *)(puVar2 + 10);
  param_3[3] = *(undefined4 *)(puVar2 + 8);
  param_3[4] = uVar3;
  sVar1 = puVar2[1];
  FUN_435612ec(DAT_436abdec,apuStack_1c[0]);
  FUN_43ac5f1a((int)sVar1);
  return;
}


/* 436abdf0 */

void FUN_436abdf0(undefined4 param_1,int param_2,undefined4 *param_3,uint param_4)

{
  undefined2 uVar1;
  short sVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uStack_28;
  int iStack_24;
  undefined4 *puStack_20;
  undefined4 uStack_1c;
  
  *(undefined2 *)((int)param_3 + 6) = 0;
  *(undefined2 *)(param_3 + 1) = 0;
  uStack_28 = param_1;
  iStack_24 = param_2;
  puStack_20 = param_3;
  uStack_1c = param_4;
  FUN_435612d0(DAT_436abe94,&puStack_20,0x50,1);
  puVar3 = puStack_20;
  iStack_24 = 0;
  FUN_4366c224(&iStack_24,(int)&uStack_1c + 2,&uStack_1c,&uStack_28);
  puVar3[1] = param_1;
  if (0x1000 < uStack_1c._2_2_) {
    uStack_1c = CONCAT22(0xfff,(undefined2)uStack_1c);
  }
  *(undefined2 *)puVar3 = 0xc;
  *(undefined2 *)((int)puVar3 + 2) = 0;
  *(undefined2 *)(puVar3 + 5) = 0;
  puVar3[2] = param_2 * 0x100 + ((int)(uStack_1c >> 0x10) >> 4 & 0xffU);
  puVar3[3] = 0xffffffff;
  *(undefined2 *)((int)puVar3 + 0x16) = 1;
  FUN_436abb28(puStack_20);
  FUN_43561228(DAT_436abe94,puStack_20);
  uVar1 = *(undefined2 *)(puVar3 + 2);
  *(undefined2 *)(param_3 + 1) = *(undefined2 *)(puVar3 + 1);
  *(undefined2 *)((int)param_3 + 6) = uVar1;
  *param_3 = param_1;
  uVar4 = puVar3[5];
  param_3[3] = puVar3[4];
  param_3[4] = uVar4;
  sVar2 = *(short *)((int)puVar3 + 2);
  FUN_435612ec(DAT_436abe94,puStack_20);
  FUN_43ac5f1a((int)sVar2);
  return;
}


/* 436abe98 */

void FUN_436abe98(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  int iVar2;
  undefined2 *puVar3;
  short sVar4;
  int iStack_28;
  int iStack_24;
  undefined2 *puStack_20;
  ushort uStack_1c;
  ushort auStack_1a [3];
  
  if (*(short *)(param_1 + 4) == 0) {
    return;
  }
  FUN_435612d0(DAT_436abfc8,&puStack_20,0x50,1);
  puVar3 = puStack_20;
  if (param_2 == -1) {
    uVar1 = *(undefined2 *)(param_1 + 4);
    *puStack_20 = 4;
    puStack_20[10] = 0;
    puStack_20[1] = uVar1;
    puStack_20[0xb] = 2;
  }
  else {
    if (param_3 == -1) {
      iStack_24 = 0;
      FUN_4366c224(&iStack_24,auStack_1a,&uStack_1c,&iStack_28);
      if (0x1000 < auStack_1a[0]) {
        auStack_1a[0] = 0xfff;
      }
      *puVar3 = 0xd;
      uVar1 = *(undefined2 *)(param_1 + 4);
      *(uint *)(puVar3 + 4) = param_2 * 0x100 + ((int)(uint)auStack_1a[0] >> 4 & 0xffU);
      puVar3[1] = uVar1;
      puVar3[10] = 0;
      puVar3[2] = 0;
      *(uint *)(puVar3 + 6) =
           *(int *)(DAT_436abfd0 + iStack_28 * 8 + 0x436abf72) * (param_2 - iStack_24 & 0xffffffU);
      puVar3[0xb] = 2;
      FUN_436abb28(puStack_20);
      FUN_43561228(DAT_436abfc8,puStack_20);
      sVar4 = puVar3[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
      goto LAB_436abfb6;
    }
    iStack_24 = 0;
    FUN_4366c224(&iStack_24,&uStack_1c,auStack_1a,&iStack_28);
    if (0x1000 < uStack_1c) {
      uStack_1c = 0xfff;
    }
    puVar3[1] = *(undefined2 *)(param_1 + 4);
    *puVar3 = 0xd;
    puVar3[10] = 0;
    puVar3[2] = 0;
    iVar2 = DAT_436abfcc;
    *(uint *)(puVar3 + 4) = param_2 * 0x100 + ((int)(uint)uStack_1c >> 4 & 0xffU);
    puVar3[0xb] = 2;
    *(int *)(puVar3 + 6) = *(int *)(iVar2 + iStack_28 * 8 + 0x436abf14) * param_3;
  }
  FUN_436abb28(puStack_20);
  FUN_43561228(DAT_436abfc8,puStack_20);
  sVar4 = puVar3[1];
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
LAB_436abfb6:
  FUN_435612ec(DAT_436abfc8,puStack_20);
  FUN_43ac5f1a((int)sVar4);
  return;
}


/* 436abfd4 */

undefined4 FUN_436abfd4(int param_1,int param_2,undefined2 *param_3,uint param_4)

{
  undefined2 uVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  short sVar5;
  int iStack_28;
  int iStack_24;
  undefined2 *puStack_20;
  undefined4 uStack_1c;
  
  iStack_28 = param_1;
  iStack_24 = param_2;
  puStack_20 = param_3;
  uStack_1c = param_4;
  iVar3 = FUN_435612d0(DAT_436ac11c,&puStack_20,0x50,0);
  puVar2 = puStack_20;
  if (iVar3 == 0) {
    if (param_2 == -1) {
      uVar1 = *(undefined2 *)(param_1 + 4);
      puStack_20[10] = 0;
      *puStack_20 = 4;
      puStack_20[1] = uVar1;
      puStack_20[0xb] = 0;
      FUN_436abb28(puStack_20);
      FUN_43561228(DAT_436ac11c,puStack_20);
      sVar5 = puVar2[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
    }
    else {
      iStack_24 = iVar3;
      if (param_3 == (undefined2 *)0xffffffff) {
        FUN_4366c224(&iStack_24,(int)&uStack_1c + 2,&uStack_1c,&iStack_28);
        if (0x1000 < uStack_1c._2_2_) {
          uStack_1c = CONCAT22(0xfff,(undefined2)uStack_1c);
        }
        *puVar2 = 0xd;
        uVar1 = *(undefined2 *)(param_1 + 4);
        *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uStack_1c >> 0x10) >> 4 & 0xffU);
        puVar2[1] = uVar1;
        puVar2[10] = 0;
        puVar2[2] = 0;
        *(uint *)(puVar2 + 6) =
             *(int *)(DAT_436ac124 + iStack_28 * 8 + 0x436ac0be) * (param_2 - iStack_24 & 0xffffffU)
        ;
        puVar2[0xb] = 0;
        FUN_436abb28(puStack_20);
        FUN_43561228(DAT_436ac11c,puStack_20);
        sVar5 = puVar2[1];
        *(undefined2 *)(param_1 + 6) = 0;
        *(undefined2 *)(param_1 + 4) = 0;
      }
      else {
        FUN_4366c224(&iStack_24,&uStack_1c,(int)&uStack_1c + 2,&iStack_28);
        if (0x1000 < (uStack_1c & 0xffff)) {
          uStack_1c = CONCAT22(uStack_1c._2_2_,0xfff);
        }
        puVar2[1] = *(undefined2 *)(param_1 + 4);
        *puVar2 = 0xd;
        puVar2[10] = 0;
        puVar2[2] = 0;
        iVar3 = DAT_436ac120;
        *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uStack_1c & 0xffff) >> 4 & 0xffU);
        puVar2[0xb] = 0;
        *(int *)(puVar2 + 6) = *(int *)(iVar3 + iStack_28 * 8 + 0x436ac04c) * (int)param_3;
        FUN_436abb28(puStack_20);
        FUN_43561228(DAT_436ac11c,puStack_20);
        sVar5 = puVar2[1];
        *(undefined2 *)(param_1 + 6) = 0;
        *(undefined2 *)(param_1 + 4) = 0;
      }
    }
    FUN_435612ec(DAT_436ac11c,puStack_20);
    uVar4 = FUN_43ac5f1a((int)sVar5);
  }
  else {
    uVar4 = 0xffff;
  }
  return uVar4;
}


/* 436e540c */

undefined8 FUN_436e540c(uint param_1,undefined4 param_2,undefined4 param_3,undefined2 *param_4)

{
  undefined2 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined2 *puStack_14;
  
  iVar4 = DAT_436e548c + 0x436e5418;
  puStack_14 = param_4;
  if (param_1 < 6) {
    *(uint *)(DAT_436e5490 + 0x436e5422) = param_1;
    uVar1 = *(undefined2 *)(DAT_436e5494 + 0x436e542a);
    iVar3 = FUN_435612d0(DAT_436e5484,&puStack_14,0x70,1);
    if (iVar3 == 0) {
      FUN_43ada13c(puStack_14,DAT_436e5488);
      uVar2 = DAT_436e5484;
      *puStack_14 = 4;
      puStack_14[1] = uVar1;
      *(undefined4 *)(puStack_14 + 8) = 0;
      puStack_14[10] = 0;
      puStack_14[0xb] = 2;
      FUN_4356120c(uVar2,puStack_14);
    }
    *(undefined2 *)(DAT_436e5498 + 0x436e545c) = 0;
    iVar4 = *(int *)(iVar4 + DAT_436e549c);
    *(undefined4 *)(iVar4 + 0x34) = *(undefined4 *)(iVar4 + 0x30);
    uVar5 = param_1;
  }
  else {
    uVar5 = param_1;
    FUN_436e41e4(0x125,0,1,DAT_436e54a0 + 0x436e5476,param_1,param_2,param_3);
    FUN_43902718(DAT_436e54a4 + 0x436e5480,param_1);
  }
  return CONCAT44(param_2,uVar5);
}


/* 436fe070 */

void FUN_436fe070(int param_1)

{
  char cVar1;
  undefined2 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  short sVar7;
  int iVar8;
  uint *puVar9;
  undefined2 *unaff_r5;
  int *piVar10;
  short *psVar11;
  int iVar12;
  
  iVar5 = DAT_436fe14c;
  psVar11 = (short *)(DAT_436fe14c + 0x436fe082);
  iVar12 = DAT_436fe14c + 0x436fe086;
  FUN_439c5a04(iVar12,0,0x100);
  iVar3 = DAT_436fe15c;
  cVar1 = *(char *)(param_1 + 2);
  iVar8 = **(int **)(param_1 + 8);
  if (cVar1 == '\x04') {
    if (iVar8 == 0) {
      sVar7 = *psVar11 + 1;
      piVar10 = (int *)(DAT_436fe15c + 0x436fe0e0);
      *psVar11 = sVar7;
      *(bool *)(iVar5 + 0x436fe084) = *(int *)(iVar3 + 0x436fe0e8) + -1 <= (int)sVar7;
      FUN_439c5320(iVar12,sVar7 * 0x100 + *piVar10,0x100);
      *(int *)(iVar3 + 0x436fe0ec) = sVar7 + 1;
      iVar5 = FUN_436ba2c8(9,5,0x104,psVar11);
      if (iVar5 == 0) {
        return;
      }
      FUN_436fdfc4(0x125,0,1,DAT_436fe160 + 0x436fe122);
      iVar5 = DAT_436fe164 + 0x436fe12a;
      goto LAB_436fe128;
    }
LAB_436fe134:
    if (iVar8 == 3) {
      uVar6 = 5;
      goto LAB_436fe13e;
    }
  }
  else {
    if (cVar1 == '\x06') {
      if (iVar8 == 0) {
        uVar6 = 0;
        goto LAB_436fe13e;
      }
      goto LAB_436fe134;
    }
    if (cVar1 != '\0') {
      return;
    }
    *psVar11 = -1;
    iVar5 = FUN_436ba2c8(9,1,4,DAT_436fe150 + 0x436fe0b2);
    if (iVar5 == 0) {
      return;
    }
    FUN_436fdfc4(0x125,0,1,DAT_436fe154 + 0x436fe0c4);
    iVar5 = DAT_436fe158 + 0x436fe0cc;
LAB_436fe128:
    FUN_43902718(iVar5);
  }
  uVar6 = 2;
LAB_436fe13e:
  if (uVar6 < 6) {
    *(uint *)(DAT_436fea40 + 0x436fe9a8) = uVar6;
    uVar2 = *(undefined2 *)(DAT_436fea44 + 0x436fe9b0);
    iVar5 = FUN_435612d0(DAT_436fea38,&stack0xffffffec,0x70,1);
    if (iVar5 == 0) {
      FUN_43adc1ea(unaff_r5,DAT_436fea3c);
      uVar4 = DAT_436fea38;
      *unaff_r5 = 4;
      unaff_r5[1] = uVar2;
      *(undefined4 *)(unaff_r5 + 8) = 0;
      unaff_r5[10] = 0;
      unaff_r5[0xb] = 2;
      FUN_4356120c(uVar4,unaff_r5);
    }
    *(undefined2 *)(DAT_436fea48 + 0x436fe9e2) = 0;
    iVar5 = FUN_436e8328();
    if ((iVar5 != 1) && (iVar5 = FUN_436e8328(), iVar5 == 2)) {
      FUN_436fe36c();
    }
    puVar9 = (uint *)(DAT_436fea4c + 0x436fe9fc);
    uVar6 = *puVar9;
    if (uVar6 == 0) {
      return;
    }
    FUN_436fe410(0x125,0,1,DAT_436fea50 + 0x436fea0e,uVar6);
    uVar6 = *puVar9;
    iVar5 = DAT_436fea54 + 0x436fea18;
  }
  else {
    FUN_436fe410(0x125,0,1,DAT_436fea58 + 0x436fea28,uVar6);
    iVar5 = DAT_436fea5c + 0x436fea32;
  }
  FUN_43902718(iVar5,uVar6);
  return;
}


/* 4379521c */

void FUN_4379521c(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  int *piVar6;
  undefined8 uVar7;
  undefined4 auStack_c8 [4];
  undefined4 uStack_b8;
  undefined4 uStack_b0;
  undefined4 auStack_98 [4];
  undefined4 uStack_88;
  int iStack_84;
  undefined4 uStack_80;
  int iStack_78;
  undefined4 uStack_70;
  undefined4 auStack_68 [5];
  int iStack_54;
  undefined4 uStack_50;
  undefined4 uStack_48;
  undefined1 auStack_38 [2];
  undefined2 uStack_36;
  undefined4 uStack_30;
  undefined4 uStack_28;
  char acStack_21 [5];
  
  iVar5 = DAT_437953fc + 0x4379522a;
  cVar1 = **(char **)(iVar5 + DAT_43795400);
  if ((cVar1 == '\x01') && (iVar2 = FUN_43819b08(2), iVar2 == 0)) {
    acStack_21[0] = cVar1;
    iVar2 = FUN_4377e4e4();
    piVar6 = *(int **)(iVar5 + DAT_43795404);
    if ((*piVar6 == 5) || (*piVar6 == 7)) {
      if (iVar2 != 4) {
        return;
      }
      iVar3 = FUN_43819224(**(undefined2 **)(iVar5 + DAT_43795408),
                           **(undefined2 **)(iVar5 + DAT_4379540c),1,acStack_21);
      if (iVar3 == 0) {
        return;
      }
      FUN_43819868(acStack_21[0]);
    }
    if (*piVar6 == 6) {
      if (iVar2 != 3) {
        return;
      }
      iVar2 = FUN_43819224(**(undefined2 **)(iVar5 + DAT_43795408),
                           **(undefined2 **)(iVar5 + DAT_4379540c),1,acStack_21);
      if (iVar2 == 0) {
        return;
      }
      FUN_43819868(acStack_21[0]);
    }
    if (*piVar6 == 6) {
      iVar2 = 2;
    }
    else {
      iVar2 = 8;
    }
    if (**(char **)(iVar5 + DAT_43795410) == '\0') {
      iVar5 = 0x412b;
    }
    else {
      iVar5 = 20000;
    }
    FUN_439c5a04(auStack_68,0,0x30);
    auStack_68[0] = 0x30;
    iVar3 = FUN_43561244(DAT_437953f0,auStack_68);
    if (iVar3 == 0) {
      iVar3 = iStack_54;
    }
    if (iVar3 == 0) {
      iVar3 = FUN_4356127c(uStack_48,&uStack_28,DAT_43795414 + 0x43795308,0);
      if (iVar3 == 0) {
        FUN_439c5a04(auStack_98,0,0x30);
        iStack_78 = DAT_43795418 + 0x43795322;
        auStack_98[0] = 0x30;
        uStack_80 = uStack_50;
        uStack_88 = 1;
        uStack_70 = uStack_28;
        uVar7 = FUN_43561244(DAT_437953f0,auStack_98);
        if (((int)uVar7 == 0) && (iStack_84 == 0)) {
          puVar4 = (undefined4 *)(DAT_4379541c + 0x43795344);
          *puVar4 = uStack_50;
          iVar5 = FUN_43794bac(puVar4,(int)((ulonglong)uVar7 >> 0x20),iVar2 * iVar5,0,0);
          if (iVar5 != 0) {
            return;
          }
          puVar4 = (undefined4 *)(DAT_43795420 + 0x43795384);
          FUN_439c5a04(auStack_38,0,0xe);
          auStack_38[0] = 5;
          uStack_36 = 0x404b;
          uStack_30 = 0xffffffff;
          iVar5 = FUN_435612d0(DAT_437953f4,puVar4,0xe,1);
          if (iVar5 != 0) {
            iVar2 = DAT_43795428 + 0x437953bc;
            FUN_43794c34(3,0,1,DAT_43795424 + 0x437953b8,iVar5,iVar2,0x20f);
            FUN_43902718(DAT_4379542c + 0x437953d4,iVar5,iVar2,0x20f);
            return;
          }
          FUN_43ae9188(*puVar4,DAT_437953f8);
          FUN_439c5320(*puVar4,auStack_38,0xe);
          return;
        }
        FUN_43561298(uStack_48,uStack_28);
      }
      FUN_439c5a04(auStack_c8,0,0x30);
      auStack_c8[0] = 0x30;
      uStack_b8 = 5;
      uStack_b0 = uStack_50;
      FUN_43561244(DAT_437953f0,auStack_c8);
    }
  }
  return;
}


/* 437e8e68 */

longlong FUN_437e8e68(uint param_1,byte *param_2,undefined4 param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  byte *pbVar4;
  byte *pbStack_1c;
  undefined4 uStack_18;
  
  pbStack_1c = param_2;
  uStack_18 = param_3;
  iVar2 = FUN_435612d0(DAT_437e8ed0,&pbStack_1c,0x50,1);
  pbVar4 = pbStack_1c;
  if (iVar2 == 0) {
    FUN_439c5a04(pbStack_1c,0,0x50);
    FUN_43afd4a4(pbVar4,param_1);
    FUN_43afd484(pbStack_1c,param_3);
    iVar2 = FUN_43561228(DAT_437e8ed0,pbStack_1c);
    if ((iVar2 == 0) && (*(short *)(pbVar4 + 2) == 0)) {
      bVar1 = pbVar4[8];
      *param_2 = bVar1;
      uVar3 = 0;
      while( true ) {
        if (bVar1 <= uVar3) break;
        uVar3 = uVar3 + 1;
        *(undefined4 *)(param_2 + 4) = *(undefined4 *)(pbVar4 + 0x10);
        *(undefined4 *)(param_2 + 8) = *(undefined4 *)(pbVar4 + 0x14);
        param_2 = param_2 + 8;
        pbVar4 = pbVar4 + 8;
      }
    }
    FUN_435612ec(DAT_437e8ed0,pbStack_1c);
  }
  return (ulonglong)param_1 << 0x20;
}


/* 437e8ed4 */

undefined4 FUN_437e8ed4(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uStack_14;
  
  uStack_14 = param_2;
  iVar2 = FUN_435612d0(DAT_437e8f18,&uStack_14,0x50,1,param_1);
  uVar1 = uStack_14;
  if (iVar2 == 0) {
    FUN_439c5a04(uStack_14,0,0x50);
    FUN_43afd4ba(uVar1,param_1);
    FUN_43afd484(uStack_14,param_2);
    FUN_43561228(DAT_437e8f18,uStack_14);
    FUN_435612ec(DAT_437e8f18,uStack_14);
  }
  return 0;
}


/* 437e8f1c */

longlong FUN_437e8f1c(uint param_1,undefined2 *param_2,undefined4 param_3)

{
  undefined2 *puVar1;
  int iVar2;
  undefined2 *puStack_1c;
  undefined4 uStack_18;
  
  puStack_1c = param_2;
  uStack_18 = param_3;
  iVar2 = FUN_435612d0(DAT_437e8f70,&puStack_1c,0x50,1);
  puVar1 = puStack_1c;
  if (iVar2 == 0) {
    FUN_439c5a04(puStack_1c,0,0x50);
    FUN_43afd4d0(puVar1,param_1);
    FUN_43afd484(puStack_1c,param_3);
    iVar2 = FUN_43561228(DAT_437e8f70,puStack_1c);
    if ((iVar2 == 0) && (puVar1[1] == 0)) {
      *param_2 = puVar1[2];
    }
    FUN_435612ec(DAT_437e8f70,puStack_1c);
  }
  return (ulonglong)param_1 << 0x20;
}


/* 437e8f74 */

undefined4 FUN_437e8f74(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uStack_14;
  
  uStack_14 = param_2;
  iVar2 = FUN_435612d0(DAT_437e8fb8,&uStack_14,0x50,1,param_1);
  uVar1 = uStack_14;
  if (iVar2 == 0) {
    FUN_439c5a04(uStack_14,0,0x50);
    FUN_43afd4ec(uVar1,param_1);
    FUN_43afd484(uStack_14,param_2);
    FUN_43561228(DAT_437e8fb8,uStack_14);
    FUN_435612ec(DAT_437e8fb8,uStack_14);
  }
  return 0;
}


/* 4381a138 */

void FUN_4381a138(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  int iVar1;
  undefined1 auStack_124 [272];
  undefined1 auStack_14 [4];
  
  FUN_435aa02c(auStack_14);
  FUN_435a92e0(auStack_124);
  iVar1 = FUN_43a49628(auStack_124,DAT_4381a190);
  if ((iVar1 == 0) && (iVar1 = FUN_435a9304(auStack_124,param_2,param_3), iVar1 == 0)) {
    FUN_435aa20c(auStack_14,param_1,auStack_124);
  }
  FUN_435a92c8(auStack_124);
  FUN_435aa014(auStack_14);
  return;
}


/* 439037c0 */

undefined4
FUN_439037c0(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,undefined4 param_5
            ,undefined2 param_6)

{
  char cVar1;
  short sVar2;
  int iVar3;
  undefined2 *puVar4;
  int iVar5;
  short *psVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  short *psVar10;
  undefined4 uVar11;
  undefined1 auStack_40 [28];
  undefined1 auStack_24 [8];
  undefined2 *puStack_1c;
  
  FUN_43ae071a(auStack_24,2,param_6);
  iVar3 = FUN_43afe4ca(auStack_24);
  if (iVar3 == 0) {
    FUN_43902984(5,1,1,DAT_43903a7c + 0x439037ee,param_1,param_3,param_4);
    FUN_43902718(DAT_43903a80 + 0x43903802,param_1,param_3,param_4);
    uVar11 = 0xffffffff;
  }
  else {
    uVar11 = FUN_43ae0752(auStack_24);
    FUN_43ae0756(auStack_40,uVar11,DAT_43903a74,0x18);
    iVar3 = FUN_43ae8c1e(auStack_40);
    if (iVar3 == 0) {
      FUN_43902984(5,1,1,DAT_43903a84 + 0x4390382c,param_1,param_3,param_4);
      FUN_43902718(DAT_43903a88 + 0x43903840,param_1,param_3,param_4);
      uVar11 = 0xfffffffe;
    }
    else {
      puVar4 = (undefined2 *)FUN_43ae07ae(auStack_40);
      *puVar4 = 1;
      *(undefined4 *)(puVar4 + 2) = param_1;
      *(undefined4 *)(puVar4 + 4) = param_2;
      *(undefined4 *)(puVar4 + 6) = param_4;
      puVar4[10] = 0x55;
      puVar4[0xb] = (short)param_3;
      iVar3 = FUN_43ae07b2(auStack_40);
      if (iVar3 == 0) {
LAB_43903884:
        iVar3 = FUN_43ae07c0(auStack_40);
        if (iVar3 == 0) {
          iVar3 = FUN_43b2a24a(auStack_40);
          if (iVar3 != DAT_43903a74) goto code_r0x439038c4;
          psVar6 = (short *)FUN_43ae07ce(auStack_40);
          sVar2 = psVar6[1];
          if (sVar2 == 0) {
            if ((*psVar6 == -0x7fff) && (psVar6[3] == 0x55)) {
              if (psVar6[2] == -1) {
                FUN_43902984(5,1,1,DAT_43903adc + 0x43903a5a,param_1,param_3,param_4);
                FUN_43902718(DAT_43903ae0 + 0x43903a6e,param_1,param_3,param_4);
                uVar11 = 0xfffffffa;
              }
              else if ((param_3 == 1) && ((psVar6[4] == 0 || (*(int *)(psVar6 + 8) == 0)))) {
                FUN_43902984(5,1,1,DAT_43903b78 + 0x43903afc,param_1,1,param_4);
                FUN_43902718(DAT_43903b7c + 0x43903b10,param_1,1,param_4);
                uVar11 = 0xfffffff9;
              }
              else {
                uVar11 = 0;
                FUN_439c5320(param_5,psVar6,0x70);
              }
            }
            else {
              FUN_43902984(5,1,1,DAT_43903aac + 0x4390394a,*psVar6,*puVar4,param_1,param_3,param_4);
              FUN_43902718(DAT_43903ab0 + 0x4390395a,*psVar6,*puVar4,param_1,param_3,param_4);
              FUN_43902984(5,1,1,DAT_43903ab4 + 0x4390396c);
              FUN_43902718(DAT_43903ab8 + 0x43903974);
              uVar11 = FUN_43b2a24a(auStack_40);
              FUN_43902984(5,1,1,DAT_43903abc + 0x43903986,uVar11);
              uVar11 = FUN_43b2a24a(auStack_40);
              FUN_43902718(DAT_43903ac0 + 0x4390399a,uVar11);
              FUN_43902984(5,1,1,DAT_43903ac4 + 0x439039a8);
              FUN_43902718(DAT_43903ac8 + 0x439039b0);
              iVar3 = 0;
              psVar10 = psVar6;
              do {
                uVar11 = *(undefined4 *)(psVar10 + 2);
                uVar7 = *(undefined4 *)(psVar10 + 4);
                uVar8 = *(undefined4 *)(psVar10 + 6);
                FUN_43902984(5,1,1,DAT_43903acc + 0x439039d2,*(undefined4 *)((int)psVar6 + iVar3),
                             uVar11,uVar7,uVar8);
                uVar9 = *(undefined4 *)(psVar10 + 6);
                FUN_43902718(DAT_43903ad0 + 0x439039de,*(undefined4 *)((int)psVar6 + iVar3),
                             *(undefined4 *)(psVar10 + 2),*(undefined4 *)(psVar10 + 4),uVar9);
                iVar3 = iVar3 + 0x10;
                psVar10 = psVar10 + 8;
              } while (iVar3 != 0x50);
              FUN_43902984(5,1,1,DAT_43903ad4 + 0x439039fa,uVar9,uVar11,uVar7,uVar8);
              FUN_43902718(DAT_43903ad8 + 0x43903a02);
              iVar3 = FUN_435612d0(DAT_43903a78,&puStack_1c,4,1);
              puVar4 = puStack_1c;
              uVar11 = DAT_43903a78;
              if (iVar3 == 0) {
                *(undefined1 *)(puStack_1c + 1) = 0;
                *puStack_1c = 0xe;
                FUN_43b2a244(puStack_1c,uVar11);
                FUN_43561228(DAT_43903a78,puStack_1c);
                cVar1 = *(char *)(puVar4 + 1);
                if (puStack_1c != (undefined2 *)0x0) {
                  FUN_435612ec(DAT_43903a78);
                }
                if (cVar1 != '\0') goto LAB_43903b3a;
                uVar11 = 0xfffffffb;
                Reset = 0;
              }
              else {
LAB_43903b3a:
                uVar11 = 0xfffffffb;
              }
            }
          }
          else if (sVar2 == -2) {
            uVar11 = 0xfffffff8;
          }
          else {
            FUN_43902984(5,1,1,DAT_43903aa4 + 0x43903908,(int)sVar2,param_1,param_3,param_4);
            FUN_43902718(DAT_43903aa8 + 0x43903918,(int)psVar6[1],param_1,param_3,param_4);
            uVar11 = 0xfffffffc;
          }
          goto LAB_43903b4a;
        }
        FUN_43902984(5,1,1,DAT_43903a94 + 0x4390389c,iVar3,param_1,param_3,param_4);
        iVar5 = DAT_43903a98 + 0x439038ac;
      }
      else {
        FUN_43902984(5,1,1,DAT_43903a8c + 0x43903874,iVar3,param_1,param_3,param_4);
        iVar5 = DAT_43903a90 + 0x43903884;
      }
      FUN_43902718(iVar5,iVar3,param_1,param_3,param_4);
      uVar11 = 0xfffffffd;
    }
LAB_43903b4a:
    FUN_43ae078a(auStack_40);
  }
  FUN_43ae073a(auStack_24);
  return uVar11;
code_r0x439038c4:
  FUN_43902984(5,1,1,DAT_43903a9c + 0x439038d2,iVar3);
  FUN_43902718(DAT_43903aa0 + 0x439038dc,iVar3);
  goto LAB_43903884;
}


/* 43903b80 */

undefined4 FUN_43903b80(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  short *psVar4;
  undefined4 uVar5;
  undefined1 auStack_34 [28];
  undefined1 auStack_18 [8];
  
  FUN_43ae071a(auStack_18,2,param_2);
  iVar1 = FUN_43afe4ca(auStack_18);
  if (iVar1 == 0) {
    FUN_43902984(5,1,1,DAT_43903d24 + 0x43903ba4,param_1);
    FUN_43902718(DAT_43903d28 + 0x43903bb0,param_1);
    uVar5 = 0xffffffff;
  }
  else {
    uVar5 = FUN_43ae0752(auStack_18);
    FUN_43ae0756(auStack_34,uVar5,DAT_43903d20,0x18);
    iVar1 = FUN_43ae8c1e(auStack_34);
    if (iVar1 == 0) {
      FUN_43902984(5,1,1,DAT_43903d2c + 0x43903bda,param_1);
      FUN_43902718(DAT_43903d30 + 0x43903be6,param_1);
      uVar5 = 0xfffffffe;
    }
    else {
      puVar2 = (undefined2 *)FUN_43ae07ae(auStack_34);
      *puVar2 = 0x14;
      *(char *)(puVar2 + 1) = (char)param_1;
      puVar2[10] = 0x55;
      puVar2[0xb] = 0;
      iVar1 = FUN_43ae07b2(auStack_34);
      if (iVar1 == 0) {
        while (iVar1 = FUN_43ae07c0(auStack_34), iVar1 == 0) {
          iVar1 = FUN_43b2a24a(auStack_34);
          if (iVar1 == DAT_43903d20) {
            psVar4 = (short *)FUN_43ae07ce(auStack_34);
            if (psVar4[1] == 0) {
              if ((*psVar4 == -0x7fec) && (psVar4[3] == 0x55)) {
                uVar5 = 0;
              }
              else {
                FUN_43902984(5,1,1,DAT_43903d54 + 0x43903cca,*psVar4,*puVar2,param_1);
                FUN_43902718(DAT_43903d58 + 0x43903cd6,*psVar4,*puVar2,param_1);
                uVar5 = 0xfffffffb;
              }
            }
            else {
              FUN_43902984(5,1,1,DAT_43903d4c + 0x43903c94,(int)psVar4[1],param_1);
              FUN_43902718(DAT_43903d50 + 0x43903ca2,(int)psVar4[1],param_1);
              uVar5 = 0xfffffffc;
            }
            goto LAB_43903cf4;
          }
          FUN_43902984(5,1,1,DAT_43903d44 + 0x43903c68,iVar1);
          FUN_43902718(DAT_43903d48 + 0x43903c72,iVar1);
        }
        FUN_43902984(5,1,1,DAT_43903d3c + 0x43903c3a,iVar1,param_1);
        iVar3 = DAT_43903d40 + 0x43903c44;
      }
      else {
        FUN_43902984(5,1,1,DAT_43903d34 + 0x43903c18,iVar1,param_1);
        iVar3 = DAT_43903d38 + 0x43903c22;
      }
      FUN_43902718(iVar3,iVar1,param_1);
      uVar5 = 0xfffffffd;
    }
LAB_43903cf4:
    FUN_43ae078a(auStack_34);
  }
  FUN_43ae073a(auStack_18);
  return uVar5;
}


/* 43903d5c */

undefined4 FUN_43903d5c(undefined4 param_1)

{
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  short *psVar4;
  undefined4 uVar5;
  undefined1 auStack_34 [28];
  undefined1 auStack_18 [8];
  
  FUN_43ae071a(auStack_18,2,param_1);
  iVar1 = FUN_43afe4ca(auStack_18);
  if (iVar1 == 0) {
    FUN_43902984(5,1,1,DAT_43903ee0 + 0x43903d7e);
    FUN_43902718(DAT_43903ee4 + 0x43903d86);
    uVar5 = 0xffffffff;
  }
  else {
    uVar5 = FUN_43ae0752(auStack_18);
    FUN_43ae0756(auStack_34,uVar5,DAT_43903edc,0x18);
    iVar1 = FUN_43ae8c1e(auStack_34);
    if (iVar1 == 0) {
      FUN_43902984(5,1,1,DAT_43903ee8 + 0x43903db0);
      FUN_43902718(DAT_43903eec + 0x43903db8);
      uVar5 = 0xfffffffe;
    }
    else {
      puVar2 = (undefined2 *)FUN_43ae07ae(auStack_34);
      *puVar2 = 0x17;
      *(undefined1 *)(puVar2 + 2) = 0;
      puVar2[10] = 0x55;
      iVar1 = FUN_43ae07b2(auStack_34);
      if (iVar1 == 0) {
        while (iVar1 = FUN_43ae07c0(auStack_34), iVar1 == 0) {
          iVar1 = FUN_43b2a24a(auStack_34);
          if (iVar1 == DAT_43903edc) {
            psVar4 = (short *)FUN_43ae07ce(auStack_34);
            if (psVar4[1] == 0) {
              if ((*psVar4 != -0x7fe9) || (uVar5 = 0, psVar4[3] != 0x55)) {
                FUN_43902984(5,1,1,DAT_43903f10 + 0x43903e8e,*psVar4,*puVar2);
                FUN_43902718(DAT_43903f14 + 0x43903e98,*psVar4,*puVar2);
                uVar5 = 0xfffffffb;
              }
            }
            else {
              FUN_43902984(5,1,1,DAT_43903f08 + 0x43903e58,(int)psVar4[1]);
              FUN_43902718(DAT_43903f0c + 0x43903e68,(int)psVar4[1]);
              uVar5 = 0xfffffffc;
            }
            goto LAB_43903eb2;
          }
          FUN_43902984(5,1,1,DAT_43903f00 + 0x43903e32,iVar1);
          FUN_43902718(DAT_43903f04 + 0x43903e3c,iVar1);
        }
        FUN_43902984(5,1,1,DAT_43903ef8 + 0x43903e08,iVar1);
        iVar3 = DAT_43903efc + 0x43903e10;
      }
      else {
        FUN_43902984(5,1,1,DAT_43903ef0 + 0x43903de8,iVar1);
        iVar3 = DAT_43903ef4 + 0x43903df0;
      }
      FUN_43902718(iVar3,iVar1);
      uVar5 = 0xfffffffd;
    }
LAB_43903eb2:
    FUN_43ae078a(auStack_34);
  }
  FUN_43ae073a(auStack_18);
  return uVar5;
}


/* 4390c630 */

undefined4 FUN_4390c630(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_84 [2];
  short sStack_82;
  short sStack_7e;
  int iStack_14;
  
  FUN_439c5a04(auStack_84,0,0x70);
  iVar2 = FUN_435612d0(DAT_4390c6b4,&iStack_14,0x70,1);
  if (iVar2 == 0) {
    FUN_439c5320(iStack_14,param_2,0x70);
    uVar1 = DAT_4390c6b4;
    *(undefined4 *)(iStack_14 + -4) = *(undefined4 *)(param_1 + 0x10);
    iVar2 = FUN_43561228(uVar1);
    if (iVar2 == 0) {
      FUN_439c5320(auStack_84,iStack_14,0x70);
      FUN_435612ec(DAT_4390c6b4,iStack_14);
      if (sStack_7e == 0x1111) {
        FUN_43b2e340(param_1,auStack_84,param_3);
        if (sStack_82 == 0) {
          return 0;
        }
        if (-1 < sStack_82) {
          return 0;
        }
        return 0xffffffff;
      }
    }
  }
  return 0xffffffff;
}


/* 439201f0 */

undefined4 FUN_439201f0(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_8c [6];
  short sStack_86;
  int aiStack_1c [2];
  
  FUN_439c5a04(auStack_8c,0,0x70);
  iVar2 = FUN_435612d0(DAT_43920264,aiStack_1c,0x70,1);
  if (iVar2 == 0) {
    FUN_439c5320(aiStack_1c[0],param_2,0x70);
    uVar1 = DAT_43920264;
    *(undefined4 *)(aiStack_1c[0] + -4) = *(undefined4 *)(param_1 + 4);
    iVar2 = FUN_43561228(uVar1);
    if (iVar2 == 0) {
      FUN_439c5320(auStack_8c,aiStack_1c[0],0x70);
      FUN_435612ec(DAT_43920264,aiStack_1c[0]);
      if (sStack_86 == 0x1111) {
        FUN_43b3ce2c(param_1,auStack_8c,param_3);
        return 0;
      }
    }
  }
  return 0xffffffff;
}


/* 4392d464 */

undefined4 FUN_4392d464(short *param_1)

{
  int iVar1;
  undefined2 uStack_84;
  short sStack_82;
  short sStack_70;
  undefined2 uStack_6e;
  undefined4 uStack_14;
  int iStack_10;
  undefined4 uStack_c;
  
  uStack_14 = 0;
  iStack_10 = 0;
  FUN_439c5a04(&uStack_84,0,0x70);
  iVar1 = FUN_435612d0(DAT_4392d524,&uStack_c,0x70,1);
  if (iVar1 == 0) {
    FUN_43b495d4(uStack_c,DAT_4392d52c);
    uStack_84 = 4;
    sStack_82 = *param_1;
    sStack_70 = param_1[1];
    uStack_6e = 2;
    FUN_439c5320(uStack_c,&uStack_84,0x70);
    iVar1 = FUN_43561228(DAT_4392d524,uStack_c);
    if (iVar1 == 0) {
      FUN_439c5320(&uStack_84,uStack_c,0x70);
      FUN_435612ec(DAT_4392d524,uStack_c);
      if (sStack_82 != 0) {
        iStack_10 = (int)sStack_82;
        uStack_14 = DAT_4392d530;
        FUN_43927d50(1,&uStack_14,8);
        return 0xfffffffd;
      }
      *(char *)(DAT_4392d534 + 0x4392d51a) = *(char *)(DAT_4392d534 + 0x4392d51a) + -1;
      return 0;
    }
    FUN_435612ec(DAT_4392d524,uStack_c);
  }
  iStack_10 = iVar1;
  uStack_14 = DAT_4392d528;
  FUN_43927d50(1,&uStack_14,8);
  return 0xfffffffe;
}


/* 4392dd5c */

int FUN_4392dd5c(byte *param_1)

{
  char *pcVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined1 *puVar8;
  ushort *puVar9;
  char cVar10;
  uint uVar11;
  ushort uVar12;
  int iVar13;
  ushort uVar14;
  ushort uVar15;
  undefined4 *puVar16;
  undefined2 *puVar17;
  undefined2 uStack_100;
  short sStack_fe;
  undefined4 uStack_fc;
  int iStack_f8;
  int iStack_f4;
  undefined4 uStack_f0;
  ushort uStack_ec;
  undefined2 uStack_ea;
  undefined2 uStack_90;
  ushort uStack_8e;
  char acStack_8c [4];
  undefined4 uStack_88;
  undefined4 uStack_30;
  int iStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uVar12 = 0;
  puVar17 = (undefined2 *)(DAT_4392e048 + 0x4392dd70);
  FUN_439c5a04(puVar17,0,0x20);
  uStack_24 = DAT_4392e01c;
  FUN_43927d50(3,&uStack_24,4);
  iVar13 = DAT_4392e04c;
  bVar2 = *param_1;
  *(byte *)(DAT_4392e04c + 0x4392dd92) = bVar2;
  if (bVar2 == 0) {
    iVar13 = 0;
  }
  else {
    bVar3 = param_1[0xf];
    *(byte *)(iVar13 + 0x4392dd93) = bVar3;
    uVar14 = (ushort)bVar3 + (ushort)bVar2;
    uVar15 = uVar14 & 0xff;
    uVar5 = (undefined1)uVar14;
    *(undefined1 *)(iVar13 + 0x4392dd94) = uVar5;
    if (uVar15 < 5) {
      bVar3 = param_1[1];
      *(byte *)(iVar13 + 0x4392dd95) = bVar3;
      if (bVar3 == 0) {
        iVar13 = -6;
        uStack_24 = DAT_4392e024;
        FUN_43927d50(1,&uStack_24,4);
      }
      else {
        *(undefined2 *)(iVar13 + 0x4392dd96) = *(undefined2 *)(param_1 + 2);
        uStack_30 = 0;
        iStack_2c = 0;
        puVar16 = (undefined4 *)(DAT_4392e050 + 0x4392ddf8);
        *(undefined2 *)(DAT_4392e054 + 0x4392de00) = *(undefined2 *)(param_1 + 4);
        *(byte *)(DAT_4392e058 + 0x4392de0c) = bVar2;
        *(undefined1 *)(DAT_4392e05c + 0x4392de14) = uVar5;
        *(undefined1 *)(DAT_4392e060 + 0x4392de1a) = 0;
        *(undefined1 *)(DAT_4392e064 + 0x4392de20) = 0;
        *(undefined1 *)(DAT_4392e068 + 0x4392de26) = 0;
        *(undefined1 *)(DAT_4392e06c + 0x4392de2c) = 0;
        *(undefined1 *)(DAT_4392e070 + 0x4392de32) = 1;
        *(undefined4 *)(DAT_4392e074 + 0x4392de3a) = DAT_4392e028;
        FUN_439c5a04(&uStack_100,0,0x70);
        while ((uVar12 & 0xff) < uVar15) {
          iVar13 = FUN_435612d0(DAT_4392e02c,&uStack_28,0x70,1);
          if (iVar13 != 0) {
            *(undefined1 *)(DAT_4392e078 + 0x4392de5c) = 1;
LAB_4392deaa:
            uStack_30 = DAT_4392e034;
            iStack_2c = iVar13;
            FUN_43927d50(1,&uStack_30,8);
            return -2;
          }
          FUN_43b495d4(uStack_28,DAT_4392e030);
          puVar16 = puVar16 + 1;
          uStack_fc = *puVar16;
          uStack_100 = 1;
          uStack_ea = 1;
          iStack_f8 = iVar13;
          iStack_f4 = iVar13;
          uStack_ec = uVar12;
          FUN_439c5320(uStack_28,&uStack_100,0x70);
          iVar13 = FUN_43561228(DAT_4392e02c,uStack_28);
          uVar6 = uStack_28;
          if (iVar13 != 0) {
            FUN_435612ec(DAT_4392e02c,uStack_28);
            *(undefined1 *)(DAT_4392e07c + 0x4392dea8) = 1;
            goto LAB_4392deaa;
          }
          uVar12 = uVar12 + 1;
          FUN_439c5320(&uStack_100,uStack_28,0x70);
          FUN_435612ec(DAT_4392e02c,uVar6);
          if (sStack_fe != 0) {
            iStack_2c = (int)sStack_fe;
            *(undefined1 *)(DAT_4392e080 + 0x4392deee) = 1;
            uStack_30 = DAT_4392e038;
            FUN_43927d50(1,&uStack_30,8);
            return -3;
          }
          puVar17[1] = uStack_fc._2_2_;
          *puVar17 = (undefined2)uStack_fc;
          *(undefined4 *)(puVar17 + 2) = uStack_f0;
          *(char *)(DAT_4392e084 + 0x4392df1e) = *(char *)(DAT_4392e084 + 0x4392df1e) + '\x01';
          puVar17 = puVar17 + 4;
        }
        uStack_30 = 0;
        iStack_2c = 0;
        FUN_439c5a04(&uStack_90,0,0x60);
        iVar7 = FUN_435612d0(DAT_4392e0e4,&uStack_28,0x60,1);
        if (iVar7 == 0) {
          FUN_43b495d4(uStack_28,DAT_4392e03c);
          uStack_90 = 1;
          uStack_8e = 1;
          cVar4 = *(char *)(DAT_4392e08c + 0x4392df44);
          uStack_88 = 10000;
          puVar9 = (ushort *)(DAT_4392e090 + 0x4392df5a);
          acStack_8c[0] = cVar4;
          for (cVar10 = '\0'; cVar10 != cVar4; cVar10 = cVar10 + '\x01') {
            uVar5 = (undefined1)*puVar9;
            iVar7 = *puVar9 + 2;
            iVar13 = iVar7 * 8;
            *(undefined1 *)(&uStack_90 + iVar7 * 4) = uVar5;
            *(undefined1 *)((int)&uStack_90 + iVar13 + 1) = uVar5;
            *(ushort *)(acStack_8c + iVar13 + -2) = puVar9[-1];
            pcVar1 = acStack_8c + iVar13;
            pcVar1[0] = '\0';
            pcVar1[1] = '\0';
            pcVar1[2] = '\0';
            pcVar1[3] = '\0';
            puVar9 = puVar9 + 4;
          }
          FUN_439c5320(uStack_28,&uStack_90,0x60);
          iVar7 = FUN_4356120c(DAT_4392e040,uStack_28);
          if (iVar7 == 0) {
            FUN_43927ce0(DAT_4392e0e8 + 0x4392e0dc);
            iVar13 = 0;
            uStack_30 = 0;
            iStack_2c = 0;
            for (uVar11 = 0; uVar11 < *(byte *)(DAT_4392e09c + 0x4392dfff);
                uVar11 = uVar11 + 1 & 0xff) {
              iVar7 = FUN_43b495da(*(undefined4 *)
                                    (DAT_4392e098 +
                                     (uVar11 + *(byte *)(DAT_4392e09c + 0x4392dffe)) * 8 +
                                    0x4392dfd8));
              if (iVar7 < 0) {
                iVar13 = -7;
                uStack_30 = DAT_4392e044;
                iStack_2c = iVar7;
                FUN_43927d50(1,&uStack_30,8);
              }
            }
            if (iVar13 != 0) {
              return iVar13;
            }
            iVar13 = FUN_4392d538();
            if (iVar13 == 0) {
              FUN_43927cc8(DAT_4392e0a0 + 0x4392e014);
              return 0;
            }
            return -5;
          }
          FUN_435612ec(DAT_4392e040,uStack_28);
          puVar8 = (undefined1 *)(DAT_4392e094 + 0x4392dfb0);
        }
        else {
          puVar8 = (undefined1 *)(DAT_4392e088 + 0x4392df30);
        }
        *puVar8 = 1;
        FUN_4392dd28();
        uStack_30 = DAT_4392e034;
        iVar13 = -2;
        iStack_2c = iVar7;
        FUN_43927d50(1,&uStack_30,8);
      }
    }
    else {
      iVar13 = -6;
      uStack_24 = DAT_4392e020;
      FUN_43927d50(1,&uStack_24,4);
    }
  }
  return iVar13;
}


/* 439335c0 */

undefined4 FUN_439335c0(int param_1,undefined4 param_2)

{
  undefined2 uVar1;
  undefined2 *puVar2;
  int iVar3;
  int iVar4;
  undefined2 *puStack_20;
  undefined4 uStack_1c;
  
  uStack_1c = 0;
  iVar3 = FUN_43933280(param_2);
  FUN_435612d0(DAT_439336c8,&puStack_20,0x18,1);
  puVar2 = puStack_20;
  iVar4 = FUN_43933280(param_2);
  FUN_439c5a04(puVar2,0,0x18);
  FUN_435611b8(DAT_439336cc,0xffffffff);
  uVar1 = *(undefined2 *)(iVar4 + 0x40);
  *puVar2 = 4;
  puVar2[1] = uVar1;
  if (param_1 == 1) {
    puVar2[0xb] = 2;
  }
  FUN_435611d4(DAT_439336cc);
  FUN_4393325c(puStack_20);
  FUN_43561228(DAT_439336c8,puStack_20);
  if (puVar2[1] == 0) {
    FUN_435611b8(DAT_439336cc,0xffffffff);
    *(undefined2 *)(iVar3 + 0x40) = 0;
    FUN_439c5a04(iVar3 + 0x1c,0,0x1c);
    FUN_435611d4(DAT_439336cc);
  }
  else {
    FUN_43b4c8d4(&uStack_1c,0x2e);
    FUN_435ab880(DAT_439336d0 + 0x43933646,DAT_439336d4 + 0x43933648,0x3cd,DAT_439336d8 + 0x4393364c
                );
    FUN_435ab880(DAT_439336dc + 0x4393365a,DAT_439336e0 + 0x4393365c,uStack_1c,uStack_1c);
    FUN_43938d94(0x40,0,0x1003,0xc,8,uStack_1c,0,0x3ce);
    FUN_43938e0c(0xc0,0,0x1003,(int)(short)puVar2[1],0,0,0x3d0);
  }
  FUN_435612ec(DAT_439336c8,puStack_20);
  return uStack_1c;
}


/* 4393fda0 */

undefined4 FUN_4393fda0(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_8c [6];
  short sStack_86;
  int aiStack_1c [2];
  
  FUN_439c5a04(auStack_8c,0,0x70);
  iVar2 = FUN_435612d0(DAT_4393fe14,aiStack_1c,0x70,1);
  if (iVar2 == 0) {
    FUN_439c5320(aiStack_1c[0],param_2,0x70);
    uVar1 = DAT_4393fe14;
    *(undefined4 *)(aiStack_1c[0] + -4) = *(undefined4 *)(param_1 + 8);
    iVar2 = FUN_43561228(uVar1);
    if (iVar2 == 0) {
      FUN_439c5320(auStack_8c,aiStack_1c[0],0x70);
      FUN_435612ec(DAT_4393fe14,aiStack_1c[0]);
      if (sStack_86 == 0x1111) {
        FUN_43b4f660(param_1,auStack_8c,param_3);
        return 0;
      }
    }
  }
  return 0xffffffff;
}


/* 4394d74c */

undefined8 FUN_4394d74c(undefined4 param_1,undefined2 *param_2,uint *param_3)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 *puStack_1c;
  uint *puStack_18;
  
  uVar1 = DAT_4394d7b0;
  uVar4 = 0;
  *param_3 = 0;
  puStack_1c = param_2;
  puStack_18 = param_3;
  iVar3 = FUN_435612d0(uVar1,&puStack_1c,0x18,1);
  puVar2 = puStack_1c;
  if (iVar3 == 0) {
    FUN_439c5a04(puStack_1c,0,0x18);
    *puVar2 = 1;
    uVar4 = DAT_4394d7b8;
    *(undefined4 *)(puVar2 + 2) = DAT_4394d7b4;
    *(undefined4 *)(puVar2 + 6) = 0;
    puVar2[0xb] = 1;
    FUN_43b51726(puStack_1c,uVar4);
    iVar3 = FUN_43561228(DAT_4394d7b0,puStack_1c);
    if (iVar3 == 0) {
      if (puVar2[1] == 0) {
        *param_3 = (uint)(ushort)puVar2[2];
        uVar4 = *(undefined4 *)(puVar2 + 8);
      }
      else {
        uVar4 = 0;
      }
    }
    else {
      uVar4 = 0;
    }
    FUN_435612ec(DAT_4394d7b0,puStack_1c);
  }
  return CONCAT44(param_1,uVar4);
}


/* 43986a7c */

undefined4 FUN_43986a7c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_8c [6];
  short sStack_86;
  int aiStack_1c [2];
  
  FUN_439c5a04(auStack_8c,0,0x70);
  iVar2 = FUN_435612d0(DAT_43986af0,aiStack_1c,0x70,1);
  if (iVar2 == 0) {
    FUN_439c5320(aiStack_1c[0],param_2,0x70);
    uVar1 = DAT_43986af0;
    *(undefined4 *)(aiStack_1c[0] + -4) = *(undefined4 *)(param_1 + 8);
    iVar2 = FUN_43561228(uVar1);
    if (iVar2 == 0) {
      FUN_439c5320(auStack_8c,aiStack_1c[0],0x70);
      FUN_435612ec(DAT_43986af0,aiStack_1c[0]);
      if (sStack_86 == 0x1111) {
        FUN_43b5c3b0(param_1,auStack_8c,param_3);
        return 0;
      }
    }
  }
  return 0xffffffff;
}


/* 43993318 */

undefined4 * FUN_43993318(undefined4 *param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined2 uVar5;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 *apuStack_1c [2];
  
  FUN_439c5a04(&uStack_28,0,0xc);
  FUN_43992bb4();
  FUN_43992bb4();
  iVar2 = FUN_435612d0(DAT_43993428,apuStack_1c,0x70,1);
  if (iVar2 == 0) {
    FUN_43992a40(apuStack_1c[0]);
    puVar1 = apuStack_1c[0];
    *apuStack_1c[0] = 0;
    *(undefined2 *)apuStack_1c[0] = 1;
    apuStack_1c[0][3] = 10000;
    uVar4 = DAT_4399342c;
    apuStack_1c[0][1] = param_2;
    apuStack_1c[0][2] = 0;
    apuStack_1c[0][4] = uVar4;
    *(undefined2 *)((int)apuStack_1c[0] + 0x16) = 1;
    iVar2 = DAT_43993430;
    *(undefined2 *)(apuStack_1c[0] + 5) = 0;
    if (*(char *)(iVar2 + 0x43993372) != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    FUN_43994684(0x1c,puVar1,0x18);
    iVar2 = FUN_43561228(DAT_43993428,apuStack_1c[0]);
    FUN_43994684(0x14,puVar1,0x18);
    if (iVar2 == 0) {
      if (*(short *)((int)puVar1 + 2) != 0) {
        FUN_43992bb4();
        goto LAB_439933c0;
      }
      uVar5 = *(undefined2 *)(puVar1 + 1);
      uVar4 = FUN_43a3a9b4(puVar1[4],0x10,3);
      FUN_43992bb4();
      if (*(char *)(DAT_43993434 + 0x439933e0) == '\0') {
        uVar3 = 0;
      }
      else {
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        uVar3 = 0;
      }
    }
    else {
      FUN_43992bb4();
LAB_439933c0:
      uVar4 = 0;
      uVar5 = 0xffff;
      uVar3 = 1;
    }
    iVar2 = FUN_435612ec(DAT_43993428,apuStack_1c[0]);
    if (iVar2 == 0) goto LAB_43993412;
  }
  else {
    FUN_43992bb4();
    uVar4 = 0;
  }
  FUN_43992bb4();
  uVar5 = 0xffff;
  uVar3 = 1;
LAB_43993412:
  *param_1 = uStack_28;
  param_1[1] = uStack_24;
  param_1[2] = uStack_20;
  *param_1 = uVar3;
  *(undefined2 *)((int)param_1 + 6) = uVar5;
  param_1[2] = uVar4;
  return param_1;
}


/* 43993438 */

undefined8 FUN_43993438(undefined4 *param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iStack_1c;
  undefined4 uStack_18;
  
  iStack_1c = param_2;
  uStack_18 = param_3;
  FUN_43992bb4();
  FUN_43992bb4();
  if (param_2 == 0xffff) {
    *param_1 = 1;
    param_1[1] = 0;
    goto LAB_4399351c;
  }
  iVar1 = FUN_435612d0(DAT_43993520,&iStack_1c,0x70,1);
  if (iVar1 == 0) {
    FUN_43992a40(iStack_1c);
    iVar1 = iStack_1c;
    FUN_43992a04(iStack_1c,param_2);
    if (*(char *)(DAT_43993524 + 0x43993482) != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    FUN_43994684(0x1c,iVar1,0x18);
    iVar2 = FUN_43561228(DAT_43993520,iStack_1c);
    FUN_43994684(0x14,iVar1,0x18);
    if (iVar2 == 0) {
      if (*(short *)(iVar1 + 2) != 0) {
        FUN_43992bb4();
        goto LAB_439934ce;
      }
      uVar4 = FUN_43a3a9b4(*(undefined4 *)(iVar1 + 0x10),0x10,3);
      FUN_43992bb4();
      if (*(char *)(DAT_43993528 + 0x439934e8) == '\0') {
        uVar3 = 0;
      }
      else {
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        uVar3 = 0;
      }
    }
    else {
      FUN_43992bb4();
LAB_439934ce:
      uVar4 = 0;
      uVar3 = 1;
    }
    iVar1 = FUN_435612ec(DAT_43993520,iStack_1c);
    if (iVar1 != 0) goto LAB_43993510;
  }
  else {
    FUN_43992bb4();
LAB_43993510:
    FUN_43992bb4();
    uVar4 = 0;
    uVar3 = 1;
  }
  *param_1 = uVar3;
  param_1[1] = uVar4;
LAB_4399351c:
  return CONCAT44(param_1,param_1);
}


/* 4399352c */

undefined8 FUN_4399352c(int param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iStack_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  FUN_43992bb4();
  iVar1 = FUN_435612d0(DAT_4399363c,&iStack_20,0x70,1);
  if (iVar1 == 0) {
    FUN_43992a40(iStack_20);
    iVar1 = iStack_20;
    FUN_43992a20(iStack_20,param_1);
    if (*(char *)(DAT_43993640 + 0x43993560) != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    FUN_43994684(0x1c,iVar1,0x18);
    iVar2 = FUN_43561228(DAT_4399363c,iStack_20);
    if (param_2 == 0xf1) {
      FUN_43992bc0(1);
    }
    FUN_43994684(0x14,iVar1,0x18);
    if ((iVar2 == 0) && (*(short *)(iVar1 + 2) == 0)) {
      FUN_43992bb4();
      if (((param_2 & 0x80) == 0) || (iVar1 = FUN_43b5faea(param_2), iVar1 == 0)) {
        FUN_43998498(param_2,param_1);
        iVar1 = FUN_43992734(param_2,(int)&uStack_1c + 3);
        if (iVar1 == 0) {
          uVar3 = FUN_439984b0(param_2);
LAB_439935fa:
          FUN_4399276c(uStack_1c._3_1_,param_1,uVar3);
        }
      }
      else {
        FUN_43998508(param_2,param_1);
        iVar1 = FUN_43992734(param_2,(int)&uStack_1c + 3);
        if (iVar1 == 0) {
          uVar3 = FUN_4399852c(param_2);
          goto LAB_439935fa;
        }
      }
      uVar3 = 0;
      if (*(char *)(DAT_43993644 + 0x4399360c) != '\0') {
        FUN_43992bb4();
        uVar3 = 0;
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
      }
    }
    else {
      FUN_43992bb4();
      uVar3 = 1;
    }
    iVar1 = FUN_435612ec(DAT_4399363c,iStack_20);
    if (iVar1 == 0) goto LAB_43993638;
  }
  else {
    FUN_43992bb4();
  }
  FUN_43992bb4();
  uVar3 = 1;
LAB_43993638:
  return CONCAT44(iStack_20,uVar3);
}


/* 43993648 */

undefined8 FUN_43993648(undefined4 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iStack_14;
  undefined4 uStack_10;
  
  iStack_14 = param_2;
  uStack_10 = param_3;
  FUN_43992bb4();
  iVar1 = FUN_435612d0(DAT_43993700,&iStack_14,0x70,1);
  if (iVar1 == 0) {
    FUN_43992a40(iStack_14);
    iVar1 = iStack_14;
    FUN_43992a20(iStack_14,param_1);
    if (*(char *)(DAT_43993704 + 0x4399367a) != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    FUN_43994684(0x1c,iVar1,0x18);
    iVar2 = FUN_43561228(DAT_43993700,iStack_14);
    FUN_43994684(0x14,iVar1,0x18);
    if ((iVar2 == 0) && (*(short *)(iVar1 + 2) == 0)) {
      FUN_43992bb4();
      if (*(char *)(DAT_43993708 + 0x439936cc) == '\0') {
        uVar3 = 0;
      }
      else {
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        uVar3 = 0;
      }
    }
    else {
      FUN_43992bb4();
      uVar3 = 7;
    }
    iVar1 = FUN_435612ec(DAT_43993700,iStack_14);
    if (iVar1 == 0) goto LAB_439936fa;
  }
  else {
    FUN_43992bb4();
  }
  FUN_43992bb4();
  uVar3 = 7;
LAB_439936fa:
  return CONCAT44(param_1,uVar3);
}


/* 4399370c */

undefined4 FUN_4399370c(undefined4 param_1,undefined2 *param_2)

{
  char cVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 *puStack_14;
  
  uVar4 = param_1;
  puStack_14 = param_2;
  FUN_43992bb4();
  iVar3 = FUN_435612d0(DAT_439937d0,&puStack_14,0x70,1,uVar4);
  if (iVar3 == 0) {
    FUN_43992a40(puStack_14);
    puVar2 = puStack_14;
    *puStack_14 = 6;
    uVar4 = DAT_439937d4;
    *(undefined4 *)(puStack_14 + 10) = 0;
    *(undefined4 *)(puStack_14 + 2) = 0;
    *(undefined4 *)(puStack_14 + 8) = uVar4;
    iVar3 = DAT_439937d8;
    *(undefined4 *)(puStack_14 + 4) = 0;
    *(undefined4 *)(puStack_14 + 6) = 0;
    puStack_14[1] = (short)param_1;
    cVar1 = *(char *)(iVar3 + 0x43993746);
    puStack_14[10] = 0;
    if (cVar1 != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    FUN_43994684(0x1c,puVar2,0x18);
    iVar3 = FUN_43561228(DAT_439937d0,puStack_14);
    FUN_43994684(0x14,puVar2,0x18);
    if ((iVar3 == 0) && (puVar2[1] == 0)) {
      FUN_43992bb4();
      if (*(char *)(DAT_439937dc + 0x4399379e) == '\0') {
        uVar4 = 0;
      }
      else {
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        uVar4 = 0;
      }
    }
    else {
      FUN_43992bb4();
      uVar4 = 1;
    }
    iVar3 = FUN_435612ec(DAT_439937d0,puStack_14);
    if (iVar3 == 0) {
      return uVar4;
    }
  }
  else {
    FUN_43992bb4();
  }
  FUN_43992bb4();
  return 1;
}


/* 439937e0 */

undefined4 FUN_439937e0(undefined4 param_1,undefined2 *param_2,undefined2 param_3)

{
  char cVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 *puStack_1c;
  
  uVar4 = param_1;
  puStack_1c = param_2;
  FUN_43992bb4();
  FUN_43992bb4();
  FUN_43992bb4();
  iVar3 = FUN_435612d0(DAT_43993870,&puStack_1c,0x18,1,uVar4);
  if (iVar3 == 0) {
    FUN_43992a40(puStack_1c);
    puVar2 = puStack_1c;
    *puStack_1c = 3;
    *(undefined4 *)(puStack_1c + 6) = 5000;
    puStack_1c[0xb] = 0x19;
    iVar3 = DAT_43993874;
    puStack_1c[1] = (short)param_1;
    *(undefined2 **)(puStack_1c + 2) = param_2;
    *(undefined4 *)(puStack_1c + 4) = 0;
    cVar1 = *(char *)(iVar3 + 0x43993824);
    *(undefined4 *)(puStack_1c + 8) = 0;
    puStack_1c[10] = param_3;
    if (cVar1 != '\0') {
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
      FUN_43992bb4();
    }
    iVar3 = FUN_4356120c(DAT_43993870,puStack_1c);
    FUN_43994684(0x1b,puVar2,0x18);
    if (iVar3 == 0) {
      return 0;
    }
  }
  FUN_43992bb4();
  return 1;
}


/* 43993878 */

undefined4 FUN_43993878(undefined4 param_1,int param_2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  uint uVar6;
  undefined4 uStack_8c;
  uint uStack_88;
  undefined4 auStack_84 [24];
  int aiStack_24 [2];
  
  FUN_439c5a04(&uStack_8c,0,0x68);
  FUN_43992bb4();
  FUN_43992bb4();
  if (param_2 == 0xffff) {
    uStack_8c = 1;
  }
  else {
    iVar2 = FUN_435612d0(DAT_43993980,aiStack_24,0x70,1);
    if (iVar2 == 0) {
      FUN_43992a40(aiStack_24[0]);
      iVar2 = aiStack_24[0];
      FUN_43992a04(aiStack_24[0],param_2);
      if (*(char *)(DAT_43993984 + 0x439938cc) != '\0') {
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
        FUN_43992bb4();
      }
      FUN_43994684(0x1c,iVar2,0x18);
      iVar3 = FUN_43561228(DAT_43993980,aiStack_24[0]);
      FUN_43994684(0x14,iVar2,0x18);
      if ((iVar3 == 0) && (*(short *)(iVar2 + 2) == 0)) {
        uVar1 = *(ushort *)(iVar2 + 8);
        uStack_88 = (uint)uVar1;
        FUN_43992bb4();
        uVar6 = 0;
        puVar5 = auStack_84;
        while( true ) {
          if (uVar1 <= uVar6) break;
          uVar6 = uVar6 + 1;
          uVar4 = FUN_43a3a9b4(*(undefined4 *)(iVar2 + 0x10),0x10,3);
          *puVar5 = uVar4;
          puVar5[1] = *(undefined4 *)(iVar2 + 0x14);
          FUN_43992bb4();
          FUN_43992bb4();
          iVar2 = iVar2 + 8;
          puVar5 = puVar5 + 2;
        }
        FUN_4399370c(param_2);
      }
      else {
        FUN_43992bb4();
        uStack_8c = 1;
      }
      iVar2 = FUN_435612ec(DAT_43993980,aiStack_24[0]);
      if (iVar2 == 0) goto LAB_4399396e;
    }
    else {
      FUN_43992bb4();
    }
    FUN_43992bb4();
    uStack_8c = 1;
    uStack_88 = 0;
  }
LAB_4399396e:
  FUN_439c5320(param_1,&uStack_8c,0x68);
  return param_1;
}


/* 439a6804 */

void FUN_439a6804(int param_1,undefined2 *param_2,undefined4 param_3)

{
  short sVar1;
  undefined2 *puVar2;
  undefined2 *puStack_14;
  undefined4 uStack_10;
  
  puStack_14 = param_2;
  uStack_10 = param_3;
  FUN_435612d0(DAT_439a684c,&puStack_14,0x50,1,param_1);
  puVar2 = puStack_14;
  *puStack_14 = 6;
  puStack_14[1] = *(undefined2 *)(param_1 + 4);
  puStack_14[10] = 0;
  FUN_439a66d0(puStack_14);
  FUN_43561228(DAT_439a684c,puStack_14);
  sVar1 = puVar2[1];
  FUN_435612ec(DAT_439a684c,puStack_14);
  FUN_43b63550(param_1,DAT_439a6850 + 0x439a6842);
  FUN_43b63544((int)sVar1);
  return;
}


/* 439a6854 */

void FUN_439a6854(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 *puVar3;
  undefined4 uVar4;
  undefined2 *puStack_14;
  
  *(undefined2 *)(param_1 + 6) = 0;
  puStack_14 = param_2;
  FUN_435612d0(DAT_439a68b8,&puStack_14,0x50,1,param_1);
  puVar3 = puStack_14;
  *puStack_14 = 5;
  uVar1 = *(undefined2 *)(param_1 + 4);
  *(undefined4 *)(puStack_14 + 6) = 0;
  puStack_14[10] = 0;
  puStack_14[1] = uVar1;
  puStack_14[0xb] = 0;
  FUN_439a66d0(puStack_14);
  FUN_43561228(DAT_439a68b8,puStack_14);
  *(undefined2 *)(param_1 + 6) = puVar3[4];
  uVar4 = *(undefined4 *)(puVar3 + 10);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(puVar3 + 8);
  *(undefined4 *)(param_1 + 0x10) = uVar4;
  sVar2 = puVar3[1];
  FUN_435612ec(DAT_439a68b8,puStack_14);
  FUN_43b63550(param_1,DAT_439a68bc + 0x439a68ac);
  FUN_43b63544((int)sVar2);
  return;
}


/* 439a68fc */

void FUN_439a68fc(undefined4 *param_1,undefined2 *param_2,undefined2 *param_3)

{
  short sVar1;
  undefined2 *puVar2;
  undefined4 uVar3;
  undefined2 *puStack_1c;
  undefined2 *puStack_18;
  
  puStack_1c = param_2;
  puStack_18 = param_3;
  FUN_435612d0(DAT_439a6954,&puStack_1c,0x50,1,param_1);
  puVar2 = puStack_1c;
  *puStack_1c = 2;
  puStack_1c[1] = *(undefined2 *)(param_1 + 1);
  uVar3 = *param_1;
  *(undefined2 **)(puStack_1c + 4) = param_2;
  *(undefined4 *)(puStack_1c + 2) = uVar3;
  puStack_1c[10] = 0;
  puStack_1c[0xb] = 0;
  FUN_439a66d0(puStack_1c);
  FUN_43561228(DAT_439a6954,puStack_1c);
  uVar3 = DAT_439a6954;
  *param_3 = puVar2[2];
  sVar1 = puVar2[1];
  FUN_435612ec(uVar3,puStack_1c);
  FUN_43b63550(param_1,DAT_439a6958 + 0x439a694a);
  FUN_43b63544((int)sVar1);
  return;
}


/* 439a6a58 */

undefined4 FUN_439a6a58(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  undefined2 *puVar2;
  undefined4 uVar3;
  int iVar4;
  short sVar5;
  int iStack_28;
  int iStack_24;
  undefined2 *puStack_20;
  ushort uStack_1c;
  ushort auStack_1a [3];
  
  if (*(short *)(param_1 + 4) == 0) {
    FUN_43b63550(param_1,DAT_439a6bd0 + 0x439a6a6c);
    uVar3 = 0;
  }
  else {
    FUN_435612d0(DAT_439a6bcc,&puStack_20,0x50,1);
    puVar2 = puStack_20;
    if (param_2 == -1) {
      uVar1 = *(undefined2 *)(param_1 + 4);
      *puStack_20 = 4;
      puStack_20[10] = 0;
      puStack_20[1] = uVar1;
      puStack_20[0xb] = 2;
      FUN_439a66d0(puStack_20);
      FUN_43561228(DAT_439a6bcc,puStack_20);
      sVar5 = puVar2[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
      FUN_435612ec(DAT_439a6bcc,puStack_20);
      iVar4 = DAT_439a6be4 + 0x439a6bc0;
    }
    else if (param_3 == -1) {
      iStack_24 = 0;
      FUN_4366c224(&iStack_24,auStack_1a,&uStack_1c,&iStack_28);
      if (0x1000 < auStack_1a[0]) {
        auStack_1a[0] = 0xfff;
      }
      *puVar2 = 0xd;
      uVar1 = *(undefined2 *)(param_1 + 4);
      *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uint)auStack_1a[0] >> 4 & 0xffU);
      puVar2[1] = uVar1;
      puVar2[10] = 0;
      puVar2[2] = 0;
      *(uint *)(puVar2 + 6) =
           *(int *)(DAT_439a6bdc + iStack_28 * 8 + 0x439a6b5e) * (param_2 - iStack_24 & 0xffffffU);
      puVar2[0xb] = 2;
      FUN_439a66d0(puStack_20);
      FUN_43561228(DAT_439a6bcc,puStack_20);
      sVar5 = puVar2[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
      FUN_435612ec(DAT_439a6bcc,puStack_20);
      iVar4 = DAT_439a6be0 + 0x439a6b8a;
    }
    else {
      iStack_24 = 0;
      FUN_4366c224(&iStack_24,&uStack_1c,auStack_1a,&iStack_28);
      if (0x1000 < uStack_1c) {
        uStack_1c = 0xfff;
      }
      puVar2[1] = *(undefined2 *)(param_1 + 4);
      *puVar2 = 0xd;
      puVar2[10] = 0;
      puVar2[2] = 0;
      iVar4 = DAT_439a6bd4;
      *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uint)uStack_1c >> 4 & 0xffU);
      puVar2[0xb] = 2;
      *(int *)(puVar2 + 6) = *(int *)(iVar4 + iStack_28 * 8 + 0x439a6ade) * param_3;
      FUN_439a66d0(puStack_20);
      FUN_43561228(DAT_439a6bcc,puStack_20);
      sVar5 = puVar2[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
      FUN_435612ec(DAT_439a6bcc,puStack_20);
      iVar4 = DAT_439a6bd8 + 0x439a6b0a;
    }
    FUN_43b63550(param_1,iVar4);
    uVar3 = FUN_43b63536((int)sVar5);
  }
  return uVar3;
}


/* 439a6be8 */

undefined4 FUN_439a6be8(int param_1,int param_2,undefined2 *param_3,uint param_4)

{
  undefined2 uVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uVar4;
  short sVar5;
  int iStack_28;
  int iStack_24;
  undefined2 *puStack_20;
  undefined4 uStack_1c;
  
  iStack_28 = param_1;
  iStack_24 = param_2;
  puStack_20 = param_3;
  uStack_1c = param_4;
  iVar3 = FUN_435612d0(DAT_439a6d5c,&puStack_20,0x50,0);
  puVar2 = puStack_20;
  if (iVar3 == 0) {
    if (param_2 == -1) {
      uVar1 = *(undefined2 *)(param_1 + 4);
      puStack_20[10] = 0;
      *puStack_20 = 4;
      puStack_20[1] = uVar1;
      puStack_20[0xb] = 0;
      FUN_439a66d0(puStack_20);
      FUN_43561228(DAT_439a6d5c,puStack_20);
      sVar5 = puVar2[1];
      *(undefined2 *)(param_1 + 6) = 0;
      *(undefined2 *)(param_1 + 4) = 0;
      FUN_435612ec(DAT_439a6d5c,puStack_20);
      iVar3 = DAT_439a6d74 + 0x439a6d4c;
    }
    else {
      iStack_24 = iVar3;
      if (param_3 == (undefined2 *)0xffffffff) {
        FUN_4366c224(&iStack_24,(int)&uStack_1c + 2,&uStack_1c,&iStack_28);
        if (0x1000 < uStack_1c._2_2_) {
          uStack_1c = CONCAT22(0xfff,(undefined2)uStack_1c);
        }
        *puVar2 = 0xd;
        uVar1 = *(undefined2 *)(param_1 + 4);
        *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uStack_1c >> 0x10) >> 4 & 0xffU);
        puVar2[1] = uVar1;
        puVar2[10] = 0;
        puVar2[2] = 0;
        *(uint *)(puVar2 + 6) =
             *(int *)(DAT_439a6d6c + iStack_28 * 8 + 0x439a6cec) * (param_2 - iStack_24 & 0xffffffU)
        ;
        puVar2[0xb] = 0;
        FUN_439a66d0(puStack_20);
        FUN_43561228(DAT_439a6d5c,puStack_20);
        sVar5 = puVar2[1];
        *(undefined2 *)(param_1 + 6) = 0;
        *(undefined2 *)(param_1 + 4) = 0;
        FUN_435612ec(DAT_439a6d5c,puStack_20);
        iVar3 = DAT_439a6d70 + 0x439a6d18;
      }
      else {
        FUN_4366c224(&iStack_24,&uStack_1c,(int)&uStack_1c + 2,&iStack_28);
        if (0x1000 < (uStack_1c & 0xffff)) {
          uStack_1c = CONCAT22(uStack_1c._2_2_,0xfff);
        }
        puVar2[1] = *(undefined2 *)(param_1 + 4);
        *puVar2 = 0xd;
        puVar2[10] = 0;
        puVar2[2] = 0;
        iVar3 = DAT_439a6d64;
        *(uint *)(puVar2 + 4) = param_2 * 0x100 + ((int)(uStack_1c & 0xffff) >> 4 & 0xffU);
        puVar2[0xb] = 0;
        *(int *)(puVar2 + 6) = *(int *)(iVar3 + iStack_28 * 8 + 0x439a6c6c) * (int)param_3;
        FUN_439a66d0(puStack_20);
        FUN_43561228(DAT_439a6d5c,puStack_20);
        sVar5 = puVar2[1];
        *(undefined2 *)(param_1 + 6) = 0;
        *(undefined2 *)(param_1 + 4) = 0;
        FUN_435612ec(DAT_439a6d5c,puStack_20);
        iVar3 = DAT_439a6d68 + 0x439a6c98;
      }
    }
    FUN_43b63550(param_1,iVar3);
    uVar4 = FUN_43b63536((int)sVar5);
  }
  else {
    FUN_43b63550(param_1,DAT_439a6d60 + 0x439a6c0a);
    uVar4 = 0x8000;
  }
  return uVar4;
}


/* 43a46312 */

void FUN_43a46312(void)

{
  FUN_43a46c9a();
  FUN_43a46dac();
  return;
}

