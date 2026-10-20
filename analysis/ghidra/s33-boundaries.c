/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "4380d5b4" */

int * FUN_4380d5b4(int *param_1)

{
  FUN_437dcd10();
  *param_1 = DAT_440231dc + 8;
  FUN_43ae90ee(param_1 + 2);
  FUN_43ae7558(param_1 + 7);
  FUN_43ae7558(param_1 + 0x11);
  FUN_43ae7558(param_1 + 0x1b);
  FUN_43ae7558(param_1 + 0x25);
  FUN_43ae7558(param_1 + 0x2f);
  FUN_43ae7558(param_1 + 0x39);
  FUN_43ae7558(param_1 + 0x43);
  FUN_43ae7558(param_1 + 0x4d);
  FUN_43ae7558(param_1 + 0x57);
  FUN_43a944d8(param_1 + 0x6f);
  FUN_4380ca2c(param_1 + 0x86);
  FUN_4364d404(param_1 + 0x14e);
  return param_1;
}


/* query "43799a94" */

undefined4
FUN_43799a94(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined1 param_5
            ,undefined4 param_6,undefined1 param_7,undefined4 param_8,undefined1 param_9,
            undefined4 param_10,undefined4 param_11)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = FUN_43799958();
  iVar3 = iVar1 + param_2 * 0x20;
  if (*(char *)(iVar1 + param_2 * 0x20) == '\x01') {
    uVar2 = FUN_437298e8(*(undefined4 *)(iVar3 + 4),param_3,param_4,param_5,param_6,param_7,param_8,
                         param_9,param_10,param_11);
    if ((*(byte *)(DAT_4402546c + 0xa6) & 1) != 0) {
      FUN_437998ac(3,9,1,&DAT_43ca4765,param_1,param_2,*(undefined4 *)(iVar3 + 4),uVar2);
      FUN_43902718(s_Wrap__SyncGet___02d___02d__>__02_43ca4779,param_1,param_2,
                   *(undefined4 *)(iVar3 + 4),uVar2);
    }
  }
  else {
    FUN_437998ac(5,0,1,&DAT_43c9b47c,s_Resource_CamResource_cpp_43ca474c,0xd7);
    uVar2 = 0;
    FUN_43902718(s_FATAL___s__d_43c9b487,s_Resource_CamResource_cpp_43ca474c,0xd7);
  }
  return uVar2;
}


/* query "43b0417e" */

void FUN_43b0417e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_43b0404a(2);
  FUN_43b0404a(1,param_1,param_3,param_4);
  return;
}


/* query "43b0419c" */

void FUN_43b0419c(int param_1,undefined4 param_2)

{
  int iVar1;
  
  if ((param_1 != 0) &&
     ((iVar1 = FUN_43799a38(1,0xb,param_2,0), iVar1 != 0 ||
      (iVar1 = FUN_43799a38(1,8,param_2,0), iVar1 != 0)))) {
    return;
  }
  FUN_43799b74(1,0xb);
  FUN_43799b74(1,8);
  FUN_43799b74(1,0x13);
  return;
}


/* query "43944678" */

int FUN_43944678(undefined4 param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  uint uVar4;
  undefined4 uVar5;
  
  iVar1 = FUN_439422b8(param_2);
  if (iVar1 != 0) {
    FUN_4394233c(param_2,0x1010);
    return iVar1;
  }
  uVar2 = FUN_4394d104();
  piVar3 = (int *)FUN_43b514c4(uVar2,param_2);
  if (piVar3 == (int *)0x0) {
    iVar1 = 4;
    FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,4,s_InitVSeqCt_43ce1aa6,
                 s_src_RcDriver_cpp_43ce1b1d,0x68d);
    FUN_435ab880(s__RC__ERROR__execCtrl___NULL_43ce1b9f);
    uVar2 = DAT_44023874;
    FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1010,0x6c,5,4,0,0x68f);
    uVar5 = 0x690;
    uVar4 = param_2;
  }
  else {
    uVar4 = FUN_43b4f986();
    if ((uVar4 & 0x40) != 0) {
      (**(code **)(*piVar3 + 0x18))(piVar3);
      (**(code **)(*piVar3 + 0x24))(piVar3,0);
      iVar1 = 0;
      goto LAB_43944778;
    }
    iVar1 = 5;
    FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,5,s_InitVSeqCt_43ce1aa6,
                 s_src_RcDriver_cpp_43ce1b1d,0x696);
    FUN_435ab880(s__RC__ERROR__43ce1b2e);
    uVar2 = DAT_44023874;
    FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1010,0x6d,4,5,0,0x698);
    uVar5 = 0x699;
    uVar4 = 0;
  }
  FUN_4393ff7c(uVar2,0xc0,0xff,0x1010,uVar4,0,0,uVar5);
LAB_43944778:
  FUN_43942300(param_2);
  return iVar1;
}


/* query "43944af0" */

int FUN_43944af0(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  uint uVar10;
  
  iVar1 = FUN_439422b8(param_2);
  if (iVar1 != 0) {
    FUN_4394233c(param_2,0x1012);
    return iVar1;
  }
  uVar2 = FUN_4394d104();
  piVar3 = (int *)FUN_43b514c4(uVar2,param_2);
  if (piVar3 == (int *)0x0) {
    iVar1 = 4;
    FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,4,s_ResizeVSeqCt_43ce19cd,
                 s_src_RcDriver_cpp_43ce1b1d,0x72e);
    FUN_435ab880(s__RC__ERROR__execCtrl___NULL_43ce1b9f);
    uVar2 = DAT_44023874;
    FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x74,5,4,0,0x730);
    uVar9 = 0x731;
    uVar10 = param_2;
  }
  else {
    uVar4 = FUN_43b4f986();
    uVar10 = 0;
    if ((uVar4 & 0x40) == 0) {
      iVar1 = 5;
      FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,5,s_ResizeVSeqCt_43ce19cd,
                   s_src_RcDriver_cpp_43ce1b1d,0x737);
      FUN_435ab880(s__RC__ERROR__43ce1b2e);
      uVar2 = DAT_44023874;
      FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x75,4,5,0,0x739);
      uVar9 = 0x73a;
    }
    else {
      uVar2 = FUN_4394c7f0();
      iVar5 = FUN_43b4fc02(piVar3,uVar2);
      if (iVar5 != 0) {
        uVar9 = FUN_43b4fa4e(piVar3);
        uVar6 = FUN_43b50bba(iVar5);
        uVar7 = FUN_43b50bc0(iVar5);
        uVar8 = FUN_43b50bc4(iVar5);
        iVar1 = FUN_4394c8e4(uVar2,uVar9,param_3,param_4,param_5,uVar6,uVar7,uVar8);
        if (iVar1 == 0) {
          iVar1 = FUN_43b4fa9a(piVar3,iVar5);
          if (iVar1 == 0) {
            iVar1 = (**(code **)(*piVar3 + 0x20))(piVar3);
            if (iVar1 == 0) goto LAB_43944db8;
            FUN_43b4fa54(piVar3);
            FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,iVar1,s_ResizeVSeqCt_43ce19cd,
                         s_src_RcDriver_cpp_43ce1b1d,0x763);
            FUN_435ab880(s__RC__ERROR__43ce1b2e);
            uVar2 = DAT_44023874;
            FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x79,4,iVar1,0,0x765);
            uVar9 = 0x766;
          }
          else {
            FUN_43b4fa54(piVar3);
            FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,iVar1,s_ResizeVSeqCt_43ce19cd,
                         s_src_RcDriver_cpp_43ce1b1d,0x758);
            FUN_435ab880(s__RC__ERROR__43ce1b2e);
            uVar2 = DAT_44023874;
            FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x78,4,iVar1,0,0x75a);
            uVar9 = 0x75b;
          }
        }
        else {
          FUN_43b4fa54(piVar3);
          FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,iVar1,s_ResizeVSeqCt_43ce19cd,
                       s_src_RcDriver_cpp_43ce1b1d,0x74e);
          FUN_435ab880(s__RC__ERROR__43ce1b2e);
          uVar2 = DAT_44023874;
          FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x77,4,iVar1,0,0x750);
          uVar9 = 0x751;
        }
        FUN_4393ff7c(uVar2,0xc0,0xff,0x1012,0,0,0,uVar9);
        goto LAB_43944db8;
      }
      iVar1 = 7;
      FUN_435ab880(s__RC__ERROR__ErrCode__0x_x_in__s__43ce159b,7,s_ResizeVSeqCt_43ce19cd,
                   s_src_RcDriver_cpp_43ce1b1d,0x742);
      FUN_435ab880(s__RC__ERROR__request___NULL_43ce1b3f);
      uVar2 = DAT_44023874;
      FUN_4393ff04(DAT_44023874,0x40,param_2 & 0xff,0x1012,0x76,4,7,0,0x744);
      uVar9 = 0x745;
    }
  }
  FUN_4393ff7c(uVar2,0xc0,0xff,0x1012,uVar10,0,0,uVar9);
LAB_43944db8:
  FUN_43942300(param_2);
  return iVar1;
}

