/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

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


/* query "436cf844" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf844(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_436cf7e8();
  if ((uVar1 & param_1) != 0) {
    FUN_436cf6d4(0x165,0,3,s__DFECore____setCamIntEnable0__al_43c91e9f,uVar1,param_1,param_3);
  }
  FUN_436cf7dc(param_1);
  _DAT_fc0a0018 = uVar1 | param_1;
  return;
}


/* query "436cfd38" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cfd38(undefined4 param_1)

{
  _DAT_fc01f15c = param_1;
  return;
}


/* query "436cfd44" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cfd44(undefined4 param_1)

{
  _DAT_fc01f160 = param_1;
  return;
}


/* query "436cf7f4" */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_436cf844(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = FUN_436cf7e8();
  if ((uVar1 & param_1) != 0) {
    FUN_436cf6d4(0x165,0,3,s__DFECore____setCamIntEnable0__al_43c91e9f,uVar1,param_1,param_3);
  }
  FUN_436cf7dc(param_1);
  _DAT_fc0a0018 = uVar1 | param_1;
  return;
}


/* query "43ad690c" */

void FUN_43ad690c(int param_1,int param_2)

{
  *(int *)(param_1 + 0xa0008) = param_2 << 0x11;
  return;
}


/* query "436ccd9c" */

undefined4 FUN_436ccd9c(uint param_1)

{
  if (param_1 < 10) {
    FUN_43ad6006(&DAT_43e7e934 + param_1 * 0x1c);
    return 0;
  }
  return 1;
}


/* query "436bda34" */

undefined4 FUN_436bda34(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 auStack_50 [4];
  undefined4 uStack_40;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  iVar1 = FUN_43acb0a0();
  if (iVar1 == 0) {
    uVar6 = 0x12;
  }
  else {
    if (iVar1 != 1) {
      return 4;
    }
    uVar6 = 0x18;
  }
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 != 1) {
    return 2;
  }
  iVar2 = FUN_436bd274(0,iVar1);
  if (iVar2 != param_1) {
    return 4;
  }
  FUN_436bd288(0,iVar1);
  (&DAT_43f92319)[iVar1] = 0;
  FUN_436bd298(&LAB_436bd410_1,iVar1);
  FUN_436c0264(1,iVar1);
  if (iVar1 == 0) {
    uVar3 = 0x10;
  }
  else {
    uVar3 = 0x26;
  }
  uStack_28 = 7;
  uStack_24 = 2;
  FUN_43b4c0c4(uVar3,&uStack_28);
  FUN_436c019c(0,iVar1);
  FUN_43acb320(iVar1);
  if (*(int *)(&DAT_43e786cc + iVar1 * 0x44) == 3) {
    FUN_436c2150(*(undefined4 *)(&DAT_43e786d0 + iVar1 * 0x44),0);
  }
  iVar2 = 0;
  do {
    FUN_439c5a04(auStack_50,0,0x28);
    auStack_50[0] = 0x28;
    uStack_40 = 1;
    uStack_38 = 1;
    uStack_34 = 0;
    uStack_30 = 1;
    FUN_43561244(0x910041,auStack_50);
    iVar4 = FUN_436c1fc4(iVar1);
    if (iVar4 == 0) goto LAB_436bdb08;
    iVar2 = iVar2 + 1;
    FUN_43acb320(iVar1);
  } while (iVar2 != 200);
  FUN_436bd72c(10,0,1,&DAT_43c901e0);
  FUN_43902718(s__Error__sapl_mov_stop___TIMEOUT_43c901f2);
  (&DAT_43f9229c)[iVar1] = (&DAT_43f9229c)[iVar1] + '\x01';
LAB_436bdb08:
  FUN_43acb300(iVar1);
  if (iVar1 == 0) {
    uVar7 = 1;
    uVar3 = 0;
  }
  else {
    uVar3 = 2;
    uVar7 = 3;
  }
  FUN_43b4a618(iVar1 != 0);
  FUN_43b4a656(uVar3);
  FUN_43b4a656(uVar7);
  iVar2 = iVar1 * 0x44;
  if ((*(int *)(&DAT_43e786cc + iVar2) == 3) &&
     (iVar4 = FUN_436c20c4(*(undefined4 *)(&DAT_43e786d0 + iVar2)), iVar4 != 0)) {
    FUN_436c2150(*(undefined4 *)(&DAT_43e786d0 + iVar2),1);
  }
  FUN_43b4a8ac(uVar6);
  FUN_436c1298(0,iVar1);
  FUN_436bd260(0,0,iVar1);
  iVar2 = FUN_436bf250(iVar1);
  iVar4 = FUN_436bf588(iVar1,(&DAT_43f9229a)[iVar1]);
  iVar5 = FUN_436bf73c(iVar1);
  if (((iVar2 != 0) && (iVar4 != 0)) && (iVar5 != 0)) {
    FUN_43acb914(iVar1);
    (&DAT_43f9229a)[iVar1] = 0;
    if (iVar1 == 1) {
      DAT_43e78c00 = 0;
      return 0;
    }
    return 0;
  }
  return 7;
}


/* query "43acb70a" */

undefined4 FUN_43acb70a(int param_1,int *param_2,int *param_3,int *param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iStack_28;
  int *piStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  iStack_28 = param_1;
  piStack_24 = param_2;
  uStack_20 = param_3;
  uStack_1c = param_4;
  uVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(2,uVar1);
  if (iVar2 == 1) {
    iVar2 = FUN_436bd274(2,uVar1);
    if (iVar2 == param_1) {
      FUN_436bd288(param_5,uVar1);
      iStack_28 = *param_4;
      piStack_24 = (int *)param_4[1];
      if (*param_2 == 3) {
        uStack_20 = (int *)(uint)*(ushort *)(param_4 + 2);
      }
      else {
        uStack_20 = (int *)CONCAT22(*(undefined2 *)((int)param_4 + 10),*(ushort *)(param_4 + 2));
      }
      if (*param_3 == 3) {
        uStack_1c = (int *)((uint)uStack_1c._2_2_ << 0x10);
      }
      else {
        uStack_1c = (int *)CONCAT22(uStack_1c._2_2_,(short)param_4[3]);
      }
      FUN_436c16f4(&iStack_28,uVar1);
      uVar3 = FUN_43acb340(param_2);
      FUN_436c06d0(uVar3,uVar1);
      uVar3 = FUN_43acb340(param_3);
      FUN_436c06fc(uVar3,uVar1);
      FUN_43acb2e8(uVar1);
      uVar1 = 0;
    }
    else {
      uVar1 = 4;
    }
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}


/* query "44024944" */

/* query "43e7ebf0" */
