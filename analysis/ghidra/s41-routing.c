/* S41: read-only exports. */

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


/* 43816448 */

void FUN_43816448(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_60 [2];
  undefined2 uStack_5e;
  byte bStack_58;
  char cStack_57;
  undefined1 uStack_56;
  undefined1 uStack_55;
  undefined1 uStack_54;
  undefined1 uStack_53;
  undefined1 uStack_52;
  undefined1 uStack_51;
  undefined1 uStack_50;
  undefined1 uStack_4f;
  undefined1 uStack_4e;
  undefined1 uStack_4d;
  undefined1 uStack_4c;
  undefined1 uStack_4b;
  undefined1 uStack_4a;
  undefined1 auStack_48 [2];
  undefined2 uStack_46;
  char cStack_40;
  undefined1 auStack_3c [4];
  undefined1 auStack_38 [4];
  undefined1 auStack_34 [4];
  undefined1 auStack_30 [4];
  undefined1 auStack_2c [5];
  char cStack_27;
  char cStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 auStack_21 [5];
  
  iVar6 = DAT_4381673c + 0x4381645c;
  FUN_439c5a04(auStack_60,0,0x17);
  auStack_21[0] = 2;
  uStack_24 = 0;
  uStack_22 = 1;
  uStack_23 = 1;
  uStack_25 = 1;
  cStack_26 = '\0';
  iVar2 = FUN_438d1c44();
  if (iVar2 == 0) {
    FUN_435613b0(DAT_438166c0,auStack_21);
  }
  else {
    FUN_435613b0(DAT_438166bc,auStack_2c);
    iVar2 = FUN_438d1d10();
    auStack_21[0] = auStack_2c[iVar2];
  }
  iVar2 = FUN_43794f58(auStack_21[0]);
  switch(iVar2) {
  case 2:
    FUN_435613b0(DAT_438166dc,&uStack_22);
    FUN_435613b0(DAT_438166e0,&uStack_23);
    FUN_435613b0(DAT_438166e4,&uStack_25);
    uVar5 = DAT_438166e8;
    break;
  case 3:
    iVar6 = FUN_438d1c44();
    if (iVar6 == 0) {
      FUN_435613b0(DAT_438166cc,&uStack_23);
      FUN_435613b0(DAT_438166d0,&uStack_25);
    }
    else {
      FUN_435613b0(DAT_438166c4,auStack_30);
      FUN_435613b0(DAT_438166c8,auStack_3c);
      iVar6 = FUN_438d1d10();
      uStack_23 = auStack_30[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_25 = auStack_3c[iVar6];
    }
    FUN_435613b0(DAT_438166d4,&uStack_22);
    uVar5 = DAT_438166d8;
    break;
  case 4:
    iVar6 = FUN_438d1c44();
    if (iVar6 == 0) {
      FUN_435613b0(DAT_438166f8,&uStack_22);
      FUN_435613b0(DAT_438166fc,&uStack_25);
      FUN_435613b0(DAT_43816700,&uStack_24);
    }
    else {
      FUN_435613b0(DAT_438166ec,auStack_34);
      FUN_435613b0(DAT_438166f0,auStack_3c);
      FUN_435613b0(DAT_438166f4,auStack_38);
      iVar6 = FUN_438d1d10();
      uStack_22 = auStack_34[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_25 = auStack_3c[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_24 = auStack_38[iVar6];
    }
    puVar4 = &uStack_23;
    uVar5 = DAT_43816704;
    goto LAB_43816548;
  default:
    uStack_22 = 1;
    uStack_23 = 1;
    uStack_24 = 0;
    uStack_25 = 1;
    FUN_43816118(3,0,1,DAT_438168d4 + 0x4381675c,iVar2);
    iVar6 = DAT_438168dc;
    FUN_43902718(DAT_438168d8 + 0x43816782,iVar2);
    iVar6 = iVar6 + 0x43816792;
    FUN_43816118(5,0,1,DAT_438168e0 + 0x43816790,iVar6,0x1ac);
    uVar5 = 0x1ac;
    iVar3 = DAT_438168e4 + 0x438167a4;
    goto LAB_438167a2;
  case 7:
    FUN_435613b0(DAT_43816708,&uStack_22);
    FUN_435613b0(DAT_4381670c,&uStack_23);
    FUN_435613b0(DAT_43816710,&uStack_25);
    uVar5 = DAT_43816714;
    break;
  case 9:
    iVar3 = FUN_438d1c44();
    if (iVar3 != 0) {
      FUN_435613b0(DAT_43816718,auStack_34);
      FUN_435613b0(DAT_4381671c,auStack_30);
      FUN_435613b0(DAT_43816720,auStack_3c);
      FUN_435613b0(DAT_43816724,auStack_38);
      iVar6 = FUN_438d1d10();
      uStack_22 = auStack_34[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_23 = auStack_30[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_25 = auStack_3c[iVar6];
      iVar6 = FUN_438d1d10();
      uStack_24 = auStack_38[iVar6];
      goto LAB_438167a6;
    }
    FUN_435613b0(DAT_43816728,&uStack_22);
    FUN_435613b0(DAT_4381672c,&uStack_23);
    iVar6 = FUN_43794f04(**(undefined4 **)(iVar6 + DAT_43816740));
    if (0 < iVar6) {
      if (iVar6 < 3) {
        FUN_435613b0(DAT_43816730,&uStack_25);
        uStack_24 = 0;
        goto LAB_438167a6;
      }
      if (iVar6 == 3) {
        FUN_435613b0(DAT_43816734,&uStack_25);
        uVar5 = DAT_43816738;
        break;
      }
    }
    iVar6 = DAT_43816748 + 0x438166a8;
    FUN_43816118(5,0,1,DAT_43816744 + 0x438166a6,iVar6,0x1a1);
    uVar5 = 0x1a1;
    iVar3 = (int)&DAT_438166bc + DAT_4381674c;
LAB_438167a2:
    FUN_43902718(iVar3,iVar6,uVar5);
    goto LAB_438167a6;
  }
  puVar4 = &uStack_24;
LAB_43816548:
  FUN_435613b0(uVar5,puVar4);
LAB_438167a6:
  if (param_1 != 0) {
    FUN_435613b0(DAT_438168c0,&uStack_22);
    iVar2 = 3;
    FUN_435613b0(DAT_438168c4,&uStack_23);
  }
  bStack_58 = FUN_4381ad58(uStack_24);
  uStack_53 = FUN_4381adb4(uStack_25);
  uStack_56 = FUN_4381ad40(uStack_22);
  cVar1 = FUN_4381acac(uStack_23);
  cStack_57 = cVar1;
  if ((cVar1 == '\x03') &&
     (FUN_435613b0(DAT_438168c8,&cStack_26), cStack_57 = cVar1, cStack_26 == '\x01')) {
    cStack_57 = '\x02';
  }
  uStack_4c = 1;
  uStack_4b = 0;
  uStack_4a = 0;
  auStack_60[0] = 5;
  uStack_55 = 0;
  uStack_5e = 0x4000;
  uStack_54 = 0;
  uStack_52 = 0;
  uStack_51 = 0;
  uStack_50 = 0;
  uStack_4f = 0;
  uStack_4e = 0;
  uStack_4d = 0;
  FUN_4381a138(DAT_438168cc,auStack_60,0x17);
  FUN_435613b0(DAT_438168d0,&cStack_27);
  if ((iVar2 == 3) && (cStack_27 == '\x01')) {
    cStack_27 = '\x02';
  }
  else {
    cStack_27 = '\0';
  }
  if ((bStack_58 - 2 < 2) && (cStack_27 == '\x02')) {
    cStack_27 = '\0';
  }
  uStack_46 = 0x404e;
  cStack_40 = cStack_27;
  auStack_48[0] = 5;
  FUN_4381a138(DAT_438168cc,auStack_48,9);
  return;
}


/* 43794e0c */

void FUN_43794e0c(void)

{
  int iVar1;
  
  iVar1 = DAT_43794e50;
  FUN_43794ce4(DAT_43794e4c + 0x43794e14);
  iVar1 = **(int **)(iVar1 + 0x43794e1e + DAT_43794e54);
  if (iVar1 - 1U < 6) {
                    /* WARNING: Could not recover jumptable at 0x43794e26. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43794e26::switchdataD_43794e2a + (uint)*(byte *)(iVar1 + 0x43794e29) * 2))()
    ;
    return;
  }
  return;
}


/* 43794e0c */

void FUN_43794e0c(void)

{
  int iVar1;
  
  iVar1 = DAT_43794e50;
  FUN_43794ce4(DAT_43794e4c + 0x43794e14);
  iVar1 = **(int **)(iVar1 + 0x43794e1e + DAT_43794e54);
  if (iVar1 - 1U < 6) {
                    /* WARNING: Could not recover jumptable at 0x43794e26. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&switchD_43794e26::switchdataD_43794e2a + (uint)*(byte *)(iVar1 + 0x43794e29) * 2))()
    ;
    return;
  }
  return;
}


/* 43b00ec0 */

void FUN_43b00ec0(int param_1)

{
  FUN_43b00cb4();
  *(short *)(param_1 + 0x57a) = *(short *)(param_1 + 0x57a) + 1;
  return;
}


/* 43b00d78 */

void FUN_43b00d78(int param_1,int param_2)

{
  if (*(int *)(param_2 + 4) != 4) {
    if (*(int *)(param_2 + 4) == 7) {
      *(undefined4 *)(param_1 + 0x6bc) = *(undefined4 *)(param_2 + 8);
    }
    return;
  }
  *(undefined4 *)(param_1 + 0x680) = *(undefined4 *)(param_2 + 8);
  return;
}

