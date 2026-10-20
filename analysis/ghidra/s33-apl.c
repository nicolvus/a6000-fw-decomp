/* S32: pseudocódigo Ghidra; evidencia estática, no ejecución. */

/* query "43814d24" */

undefined8 FUN_43814d24(char *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  switch(param_1) {
  case (char *)0x0:
  case (char *)0x3:
  case (char *)0x5:
    uVar1 = 0;
    break;
  case (char *)0x2:
    uVar1 = 2;
    break;
  case (char *)0x4:
    uVar1 = 3;
    break;
  default:
    param_1 = s_EnumConverter_h_43cb0bbf;
    FUN_43814c78(5,0,1,&DAT_43c9b47c,s_EnumConverter_h_43cb0bbf,0xd5,param_3);
    FUN_43902718(s_FATAL___s__d_43c9b487,s_EnumConverter_h_43cb0bbf,0xd5);
  case (char *)0x1:
    uVar1 = 1;
  }
  return CONCAT44(param_1,uVar1);
}


/* query "4387a1fc" */

void FUN_4387a1fc(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_58 [56];
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  FUN_4387a758(param_1,param_3);
  uVar1 = FUN_4387a4dc();
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
  FUN_436befd8(*DAT_44025de0);
  return;
}


/* query "436be554" */

undefined4 FUN_436be554(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  char cVar8;
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
  FUN_439c5320(&DAT_43e786cc + iVar1 * 0x44,param_2);
  iVar2 = FUN_436bd834(param_2,&DAT_43e77b7c + iVar1 * 0x38);
  if (iVar2 == 0) {
    abStack_44[0] = *param_2 != 3;
    if (abStack_44[0]) {
      iStack_40 = param_2[2];
      uStack_3c = *(undefined4 *)(&DAT_43e77b7c + iVar1 * 0x38);
    }
    FUN_436bf67c(0,abStack_44,iVar1);
  }
  else {
    FUN_436bd72c(10,0,1,&DAT_43c90212);
    FUN_43902718(s__Error__sapl_SetDmaAddrTar___MEM_43c90224);
  }
  cVar8 = (&DAT_43f9229a)[iVar1];
  FUN_436bf4c4(0,acStack_6c,iVar1);
  if (*(int *)(&DAT_43e78c04 + iVar1 * 4) == 0) {
    if (acStack_6c[0] == '\0') {
      if (cVar8 == '\0') {
        if (param_2[3] == 0) {
          iVar3 = FUN_43902df8(param_2[6],(short)param_2[5],1,auStack_12c,10);
          if (iVar3 == 0) {
            iVar2 = 0;
          }
          else {
            FUN_436bd72c(10,0,1,&DAT_43c901b9,iVar3);
            iVar2 = 7;
            FUN_43902718(s__Error__MemOpen___X__43c901cb,iVar3);
          }
          uVar4 = FUN_43a3a9b4(uStack_11c,0x10,1);
          uVar4 = (param_2[3] & 1U) << 0x1e | uVar4 & 0x3fffffff;
        }
        else {
          iVar2 = 7;
          uVar4 = 0;
        }
        *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uVar4;
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          iStack_60 = param_2[0xf];
          iStack_5c = param_2[0x10];
          uStack_64 = uVar4;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c9024f);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c90261;
      }
      else {
        FUN_436bf4c4(1,acStack_80);
        if (acStack_80[0] != '\0') {
          iStack_68 = iStack_7c;
          iStack_60 = iStack_74;
          iStack_5c = iStack_70;
LAB_436be784:
          uStack_64 = iStack_78 + 0x780;
          acStack_6c[0] = '\x01';
          *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uStack_64;
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c90291);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c902a3;
      }
LAB_436be736:
      FUN_43902718(pcVar5);
    }
    else {
LAB_436be78c:
      FUN_436bf498(0,acStack_6c,iVar1);
    }
  }
  else {
    if (acStack_6c[0] == '\0') {
      if (cVar8 == '\0') {
        iStack_28 = param_2[5];
        iStack_30 = param_2[3];
        iStack_2c = param_2[4];
        iVar2 = FUN_436bd834(&iStack_30,&DAT_43e77b90 + iVar1 * 0x38);
        if (iVar2 == 0) {
          acStack_6c[0] = '\x01';
          iStack_68 = param_2[5];
          uStack_64 = *(uint *)(&DAT_43e77b90 + iVar1 * 0x38);
          goto LAB_436be78c;
        }
        FUN_436bd72c(10,0,1,&DAT_43c9024f);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c90261;
      }
      else {
        FUN_436bf4c4(1,acStack_94);
        if (acStack_94[0] != '\0') {
          iStack_68 = iStack_90;
          iStack_78 = iStack_8c;
          goto LAB_436be784;
        }
        FUN_436bd72c(10,0,1,&DAT_43c90291);
        pcVar5 = s__Error__sapl_SetDmaAddrMEOut___M_43c902a3;
      }
      goto LAB_436be736;
    }
    *(uint *)(&DAT_43e77b90 + iVar1 * 0x38) = uStack_64;
  }
  iVar2 = FUN_436bf4f0(iVar1);
  FUN_436bf4c4(1,acStack_58,iVar1);
  if (acStack_58[0] == '\0') {
    uVar4 = 0;
LAB_436be80a:
    *(uint *)(&DAT_43e77ba4 + iVar1 * 0x38) = uVar4;
  }
  else {
    uVar4 = uStack_50;
    if ((&DAT_43f9229a)[iVar1] == '\0') goto LAB_436be80a;
    if (uStack_50 < 0x81) {
      *(undefined4 *)(&DAT_43e77ba4 + iVar1 * 0x38) = 0;
      FUN_436bd72c(10,0,1,&DAT_43c902de);
      FUN_43902718(s__Error__sapl_SetDmaAddrOut___FMT_43c902f0);
    }
    else {
      *(uint *)(&DAT_43e77ba4 + iVar1 * 0x38) = uStack_50 - 0x80;
    }
  }
  if (iVar2 == 2) {
    FUN_436bf4c4(2,acStack_58,iVar1);
    if (acStack_58[0] == '\0') {
      *(undefined4 *)(&DAT_43e77ba8 + iVar1 * 0x38) = 0;
    }
    else {
      *(uint *)(&DAT_43e77ba8 + iVar1 * 0x38) = uStack_50;
    }
  }
  if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
    if ((&DAT_43f9229a)[iVar1] == '\0') {
      cVar8 = '\0';
      if (param_2[10] == 3) {
        uVar4 = (param_2[0xb] & 0xfU) << 0x18 | 0x60000000;
      }
      else {
        if (param_2[0xd] == 0) {
          iVar2 = FUN_43903280((short)param_2[0xc],0,0,auStack_19c,10);
          if (iVar2 != 0) {
            FUN_436bd72c(10,0,1,&DAT_43c901b9,iVar2);
            cVar8 = '\a';
            FUN_43902718(s__Error__MemOpen___X__43c901cb,iVar2);
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
      *(uint *)(&DAT_43e77bac + iVar1 * 0x38) = uVar4;
      if (cVar8 == '\0') {
        iStack_a4 = param_2[0xc];
        uStack_a0 = uVar4;
LAB_436be94c:
        auStack_a8[0] = 1;
        FUN_436bf7e8(0,auStack_a8,iVar1);
        goto LAB_436be956;
      }
      FUN_436bd72c(10,0,1,&DAT_43c90327);
      pcVar5 = s__Error__sapl_SetDmaAddrMBLOut___M_43c90339;
    }
    else {
      FUN_436bf818(1,acStack_bc,0);
      if (acStack_bc[0] != '\0') {
        iStack_a4 = iStack_b8;
        uStack_a0 = iStack_b4 + 0x780;
        *(uint *)(&DAT_43e77bac + iVar1 * 0x38) = uStack_a0;
        goto LAB_436be94c;
      }
      FUN_436bd72c(10,0,1,&DAT_43c9036a);
      pcVar5 = s__Error__sapl_SetDmaAddrMBLOut___M_43c9037c;
    }
    FUN_43902718(pcVar5);
  }
LAB_436be956:
  if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
    if ((&DAT_43f9229a)[iVar1] != '\0') {
      iVar2 = iVar1 * 0x38;
      if (*(uint *)(&DAT_43e77b90 + iVar2) < 0x81) {
        *(undefined4 *)(&DAT_43e77b9c + iVar2) = 0;
        FUN_436bd72c(10,0,1,&DAT_43c903b8);
        FUN_43902718(s__Error__sapl_SetDmaAddrOut___HME_43c903ca);
      }
      else {
        *(uint *)(&DAT_43e77b9c + iVar2) = *(uint *)(&DAT_43e77b90 + iVar2) - 0x80;
      }
      goto LAB_436be9b8;
    }
    uVar7 = *(undefined4 *)(&DAT_43e77b90 + iVar1 * 0x38);
  }
  else {
    iVar2 = iVar1 * 0x38;
    uVar7 = *(undefined4 *)(&DAT_43e77b90 + iVar2);
    *(undefined4 *)(&DAT_43e77b90 + iVar2) = 0;
    *(undefined4 *)(&DAT_43e77bac + iVar2) = uVar7;
  }
  *(undefined4 *)(&DAT_43e77b9c + iVar1 * 0x38) = uVar7;
LAB_436be9b8:
  uVar7 = FUN_43a3a9b4(param_2[0xe],0x10,1);
  iVar2 = iVar1 * 0x38;
  *(undefined4 *)(&DAT_43e77ba0 + iVar2) = uVar7;
  iVar3 = FUN_436bf3cc(0,auStack_24,iVar1);
  if (iVar3 == 0) {
    FUN_436bd72c(10,0,1,&DAT_43c90401);
    FUN_43902718(s__Error__sapl_SetDmaAddrParamBuff_43c90413);
    *(undefined4 *)(&DAT_43e77b98 + iVar2) = 0;
    uVar7 = 7;
  }
  else {
    uVar7 = 0;
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)(&DAT_43e77b98 + iVar2) = uVar6;
  }
  iVar2 = FUN_436bf3cc(1,auStack_24,iVar1);
  if (iVar2 == 0) {
    uVar7 = 7;
    FUN_436bd72c(10,0,1,&DAT_43c90401);
    FUN_43902718(s__Error__sapl_SetDmaAddrParamBuff_43c90413);
    *(undefined4 *)(&DAT_43e77b88 + iVar1 * 0x38) = 0;
  }
  else {
    if ((&DAT_43f9229a)[iVar1] == '\0') {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    }
    else {
      iVar2 = FUN_43a3a9b4(auStack_24[0],0x10,1);
      iVar2 = iVar2 + -0x100;
    }
    *(int *)(&DAT_43e77b88 + iVar1 * 0x38) = iVar2;
  }
  iVar2 = FUN_436bf3cc(2,auStack_24,iVar1);
  if (iVar2 == 0) {
    uVar6 = 0;
  }
  else {
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
  }
  *(undefined4 *)(&DAT_43e77b8c + iVar1 * 0x38) = uVar6;
  if (*(int *)(&DAT_43e78bf4 + iVar1 * 4) == 1) {
    FUN_436bf42c(auStack_24,iVar1);
    uVar6 = FUN_43a3a9b4(auStack_24[0],0x10,1);
    *(undefined4 *)(&DAT_43e77bb0 + iVar1 * 0x38) = uVar6;
  }
  else {
    *(undefined4 *)(&DAT_43e77bb0 + iVar1 * 0x38) = 0;
  }
  return uVar7;
}


/* query "436bdbfc" */

undefined4 FUN_436bdbfc(int param_1,undefined4 param_2,undefined2 *param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_30 [2];
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined1 auStack_28 [12];
  
  iVar1 = FUN_43acb0a0();
  iVar2 = FUN_436bd24c(0,iVar1);
  if (iVar2 == 1) {
    iVar2 = FUN_436bd274(0,iVar1);
    if (iVar2 == param_1) {
      FUN_436bd288(param_2,iVar1);
      iVar2 = iVar1 * 0xac;
      FUN_436bfa88(*(undefined4 *)(&DAT_43e78a9c + iVar2),iVar1);
      FUN_436bfab0(*(undefined4 *)(&DAT_43e78aa0 + iVar2),iVar1);
      FUN_436bfad8(*(undefined4 *)(&DAT_43e78aa4 + iVar2),iVar1);
      FUN_436bfb00(*(undefined4 *)(&DAT_43e78aa8 + iVar2),iVar1);
      FUN_436bfb28(*(undefined4 *)(&DAT_43e78aac + iVar2),iVar1);
      FUN_436bfb50(*(undefined4 *)(&DAT_43e78ab0 + iVar2),iVar1);
      FUN_436bfb78(*(undefined4 *)(&DAT_43e78ab4 + iVar2),iVar1);
      FUN_436bfba0(*(undefined4 *)(&DAT_43e78ab8 + iVar2),iVar1);
      FUN_436bfbc8(*(undefined4 *)(&DAT_43e78abc + iVar2),iVar1);
      FUN_436bfbf0(*(undefined4 *)(&DAT_43e78ac0 + iVar2),iVar1);
      FUN_436bfc18(*(undefined4 *)(&DAT_43e78ac4 + iVar2),iVar1);
      FUN_436bfc40(*(undefined4 *)(&DAT_43e78ac8 + iVar2),iVar1);
      FUN_436bfc68(*(undefined4 *)(&DAT_43e78acc + iVar2),iVar1);
      FUN_436bfc90(*(undefined4 *)(&DAT_43e78ad0 + iVar2),iVar1);
      FUN_436bfcb8(*(undefined4 *)(&DAT_43e78ad4 + iVar2),iVar1);
      FUN_436bfce0(*(undefined4 *)(&DAT_43e78ad8 + iVar2),iVar1);
      FUN_436bfd08(*(undefined4 *)(&DAT_43e78adc + iVar2),iVar1);
      FUN_436bfd30(*(undefined4 *)(&DAT_43e78ae0 + iVar2),iVar1);
      FUN_436bfd58(*(undefined4 *)(&DAT_43e78ae4 + iVar2),iVar1);
      FUN_436bfd80(*(undefined4 *)(&DAT_43e78ae8 + iVar2),iVar1);
      FUN_436bfda8(*(undefined4 *)(&DAT_43e78aec + iVar2),iVar1);
      FUN_436bfdd4(*(undefined4 *)(&DAT_43e78af0 + iVar2),iVar1);
      FUN_436bfe00(*(undefined4 *)(&DAT_43e78af4 + iVar2),iVar1);
      FUN_436bfe2c(*(undefined4 *)(&DAT_43e78af8 + iVar2),iVar1);
      FUN_436bfe58(*(undefined4 *)(&DAT_43e78afc + iVar2),iVar1);
      FUN_436bfe84(*(undefined4 *)(&DAT_43e78b00 + iVar2),iVar1);
      FUN_436bfeb0(*(undefined4 *)(&DAT_43e78b04 + iVar2),iVar1);
      FUN_436bfedc(*(undefined4 *)(&DAT_43e78b08 + iVar2),iVar1);
      FUN_436bff08(*(undefined4 *)(&DAT_43e78b0c + iVar2),iVar1);
      FUN_436bff34(*(undefined4 *)(&DAT_43e78b10 + iVar2),iVar1);
      FUN_436bff60(*(undefined4 *)(&DAT_43e78b14 + iVar2),iVar1);
      FUN_436bff8c(*(undefined4 *)(&DAT_43e78b18 + iVar2),iVar1);
      iVar4 = iVar1 * 0x38;
      FUN_436bffb8(*(undefined4 *)(&DAT_43e78b1c + iVar2),iVar1);
      FUN_436bffe4(*(undefined4 *)(&DAT_43e78b20 + iVar2),iVar1);
      FUN_436c0010(*(undefined4 *)(&DAT_43e78b24 + iVar2),iVar1);
      FUN_436c003c(*(undefined4 *)(&DAT_43e78b28 + iVar2),iVar1);
      FUN_436c0068(*(undefined4 *)(&DAT_43e78b2c + iVar2),iVar1);
      FUN_436c0094(*(undefined4 *)(&DAT_43e78b30 + iVar2),iVar1);
      FUN_436c00c0(*(undefined4 *)(&DAT_43e78b34 + iVar2),iVar1);
      FUN_436c00ec(*(undefined4 *)(&DAT_43e78b38 + iVar2),iVar1);
      FUN_436c0118(*(undefined4 *)(&DAT_43e78b3c + iVar2),iVar1);
      FUN_436c0144(*(undefined4 *)(&DAT_43e78b40 + iVar2),iVar1);
      FUN_436c0170(*(undefined4 *)(&DAT_43e78b44 + iVar2),iVar1);
      iVar6 = iVar1 * 0x1a4;
      uVar3 = *(undefined4 *)(&DAT_43e77b7c + iVar4);
      param_3[1] = *(undefined2 *)(&DAT_43e78ab0 + iVar2);
      FUN_436c028c(uVar3,iVar1);
      FUN_436c02b4(0,iVar1);
      FUN_436c02dc(0x29c00,iVar1);
      FUN_436c0304(*(undefined4 *)(&DAT_43e77b88 + iVar4),iVar1);
      FUN_436c032c(*(undefined4 *)(&DAT_43e77b8c + iVar4),iVar1);
      FUN_436c0354(*(undefined4 *)(&DAT_43e77b90 + iVar4),iVar1);
      FUN_436c037c(0,iVar1);
      FUN_436c03a4(*(undefined4 *)(&DAT_43e77b98 + iVar4),iVar1);
      FUN_436c03cc(*(undefined4 *)(&DAT_43e77b9c + iVar4),iVar1);
      FUN_436c03f4(0,iVar1);
      FUN_436c041c(*(undefined4 *)(&DAT_43e77ba0 + iVar4),iVar1);
      FUN_436c0444(0,iVar1);
      FUN_436c046c(0,iVar1);
      FUN_436c0494(0,iVar1);
      FUN_436c04bc(0,iVar1);
      FUN_436c04e4(*(undefined4 *)(&DAT_43e77ba4 + iVar4),iVar1);
      FUN_436c050c(*(undefined4 *)(&DAT_43e77ba8 + iVar4),iVar1);
      FUN_436c06d0(0,iVar1);
      FUN_436c06fc(*(undefined4 *)(&DAT_43e77bac + iVar4),iVar1);
      FUN_436c0780(*(undefined4 *)(&DAT_43e77bb0 + iVar4),iVar1);
      iVar2 = iVar1 * 0x34;
      FUN_436c0534(*(undefined4 *)(&DAT_43e77c64 + iVar2),iVar1);
      FUN_436c055c(*(undefined4 *)(&DAT_43e77c68 + iVar2),iVar1);
      FUN_436c0584(*(undefined4 *)(&DAT_43e77c6c + iVar2),iVar1);
      FUN_436c05ac(*(undefined4 *)(&DAT_43e77c70 + iVar2),iVar1);
      FUN_436c05d4(*(undefined4 *)(&DAT_43e77c74 + iVar2),iVar1);
      FUN_436c05fc(*(undefined4 *)(&DAT_43e77c78 + iVar2),iVar1);
      FUN_436c0624(*(undefined4 *)(&DAT_43e77c7c + iVar2),iVar1);
      FUN_436c064c(*(undefined4 *)(&DAT_43e77c80 + iVar2),iVar1);
      FUN_436c0678(*(undefined4 *)(&DAT_43e77c84 + iVar2),iVar1);
      FUN_436c06a4(*(undefined4 *)(&DAT_43e77c88 + iVar2),iVar1);
      FUN_436c0728(*(undefined4 *)(&DAT_43e77c8c + iVar2),iVar1);
      FUN_436c0754(*(undefined4 *)(&DAT_43e77c90 + iVar2),iVar1);
      FUN_436c07ac(*(undefined4 *)(&DAT_43e77c94 + iVar2),iVar1);
      iVar2 = iVar1 * 0x9c;
      FUN_436c07d8(*(undefined4 *)(&DAT_43e783b4 + iVar2),iVar1);
      FUN_436c0800(*(undefined4 *)(&DAT_43e783b8 + iVar2),iVar1);
      FUN_436c0828(*(undefined4 *)(&DAT_43e783bc + iVar2),iVar1);
      FUN_436c0850(*(undefined4 *)(&DAT_43e783c0 + iVar2),iVar1);
      FUN_436c0878(*(undefined4 *)(&DAT_43e783c4 + iVar2),iVar1);
      FUN_436c08a0(*(undefined4 *)(&DAT_43e783c8 + iVar2),iVar1);
      FUN_436c08c8(*(undefined4 *)(&DAT_43e783cc + iVar2),iVar1);
      FUN_436c08f0(*(undefined4 *)(&DAT_43e783d0 + iVar2),iVar1);
      FUN_436c0918(*(undefined4 *)(&DAT_43e783d4 + iVar2),iVar1);
      FUN_436c0940(*(undefined4 *)(&DAT_43e783d8 + iVar2),iVar1);
      FUN_436c0968(*(undefined4 *)(&DAT_43e783dc + iVar2),iVar1);
      FUN_436c0990(*(undefined4 *)(&DAT_43e783e0 + iVar2),iVar1);
      FUN_436c09b8(*(undefined4 *)(&DAT_43e783e4 + iVar2),iVar1);
      FUN_436c09e0(*(undefined4 *)(&DAT_43e783e8 + iVar2),iVar1);
      FUN_436c0a08(*(undefined4 *)(&DAT_43e783ec + iVar2),iVar1);
      FUN_436c0a30(*(undefined4 *)(&DAT_43e783f0 + iVar2),iVar1);
      FUN_436c0a58(*(undefined4 *)(&DAT_43e783f4 + iVar2),iVar1);
      FUN_436c0a80(*(undefined4 *)(&DAT_43e783f8 + iVar2),iVar1);
      FUN_436c0aa8(*(undefined4 *)(&DAT_43e783fc + iVar2),iVar1);
      FUN_436c0ad0(*(undefined4 *)(&DAT_43e78400 + iVar2),iVar1);
      FUN_436c0af8(*(undefined4 *)(&DAT_43e78404 + iVar2),iVar1);
      FUN_436c0b20(*(undefined4 *)(&DAT_43e78408 + iVar2),iVar1);
      FUN_436c0b48(*(undefined4 *)(&DAT_43e7840c + iVar2),iVar1);
      FUN_436c0b70(*(undefined4 *)(&DAT_43e78410 + iVar2),iVar1);
      FUN_436c0b98(*(undefined4 *)(&DAT_43e78414 + iVar2),iVar1);
      FUN_436c0e00(*(undefined4 *)(&DAT_43e78418 + iVar2),iVar1);
      FUN_436c0e2c(*(undefined4 *)(&DAT_43e7841c + iVar2),iVar1);
      FUN_436c0e58(*(undefined4 *)(&DAT_43e78420 + iVar2),iVar1);
      FUN_436c0e84(*(undefined4 *)(&DAT_43e78424 + iVar2),iVar1);
      FUN_436c0eb0(*(undefined4 *)(&DAT_43e78428 + iVar2),iVar1);
      FUN_436c0edc(*(undefined4 *)(&DAT_43e7842c + iVar2),iVar1);
      FUN_436c0f08(*(undefined4 *)(&DAT_43e78430 + iVar2),iVar1);
      FUN_436c0f34(*(undefined4 *)(&DAT_43e78434 + iVar2),iVar1);
      FUN_436c0f60(*(undefined4 *)(&DAT_43e78438 + iVar2),iVar1);
      FUN_436c0f8c(*(undefined4 *)(&DAT_43e7843c + iVar2),iVar1);
      FUN_436c0fb8(*(undefined4 *)(&DAT_43e78440 + iVar2),iVar1);
      FUN_436c0fe4(*(undefined4 *)(&DAT_43e78444 + iVar2),iVar1);
      FUN_436c1010(*(undefined4 *)(&DAT_43e78448 + iVar2),iVar1);
      FUN_436c103c(*(undefined4 *)(&DAT_43e7844c + iVar2),iVar1);
      iVar2 = iVar1 * 0x14;
      FUN_436c14c8(iVar2 + 0x43f9236b,iVar1);
      FUN_436c1510(iVar2 + 0x43f9231b,iVar1);
      FUN_436c155c(iVar2 + 0x43f92343,iVar1);
      FUN_436c15a8(iVar2 + 0x43f922c7,iVar1);
      FUN_436c15f0(iVar2 + 0x43f922f1,iVar1);
      FUN_436c163c(iVar2 + 0x43f9229e,iVar1);
      FUN_436c1750(*(undefined4 *)(&DAT_43e78754 + iVar6),iVar1);
      FUN_436c1778(*(undefined4 *)(&DAT_43e78758 + iVar6),iVar1);
      FUN_436c17a0(*(undefined4 *)(&DAT_43e7875c + iVar6),iVar1);
      FUN_436c17c8(*(undefined4 *)(&DAT_43e78760 + iVar6),iVar1);
      FUN_436c17f0(*(undefined4 *)(&DAT_43e78764 + iVar6),iVar1);
      FUN_436c1818(*(undefined4 *)(&DAT_43e78768 + iVar6),iVar1);
      FUN_436c1840(*(undefined4 *)(&DAT_43e7876c + iVar6),iVar1);
      FUN_436c1868(*(undefined4 *)(&DAT_43e78770 + iVar6),iVar1);
      FUN_436c1890(*(undefined4 *)(&DAT_43e78774 + iVar6),iVar1);
      FUN_436c18b8(*(undefined4 *)(&DAT_43e78778 + iVar6),iVar1);
      FUN_436c18e0(*(undefined4 *)(&DAT_43e7877c + iVar6),iVar1);
      FUN_436c1908(*(undefined4 *)(&DAT_43e78780 + iVar6),iVar1);
      FUN_436c1930(*(undefined4 *)(&DAT_43e78784 + iVar6),iVar1);
      FUN_436c1958(*(undefined4 *)(&DAT_43e78788 + iVar6),iVar1);
      FUN_436c1980(*(undefined4 *)(&DAT_43e7878c + iVar6),iVar1);
      FUN_436c19a8(*(undefined4 *)(&DAT_43e78790 + iVar6),iVar1);
      FUN_436c19d0(*(undefined4 *)(&DAT_43e78794 + iVar6),iVar1);
      FUN_436c19f8(*(undefined4 *)(&DAT_43e78798 + iVar6),iVar1);
      FUN_436c1a20(*(undefined4 *)(&DAT_43e7879c + iVar6),iVar1);
      FUN_436c1a4c(*(undefined4 *)(&DAT_43e787a0 + iVar6),iVar1);
      FUN_436c1a78(*(undefined4 *)(&DAT_43e787a4 + iVar6),iVar1);
      FUN_436c1aa4(*(undefined4 *)(&DAT_43e787a8 + iVar6),iVar1);
      FUN_436c1ad0(*(undefined4 *)(&DAT_43e787ac + iVar6),iVar1);
      FUN_436c1afc(*(undefined4 *)(&DAT_43e787b0 + iVar6),iVar1);
      FUN_436c1b28(*(undefined4 *)(&DAT_43e787b4 + iVar6),iVar1);
      FUN_436c1b54(*(undefined4 *)(&DAT_43e787b8 + iVar6),iVar1);
      FUN_436c1b80(*(undefined4 *)(&DAT_43e787bc + iVar6),iVar1);
      FUN_436c1bac(*(undefined4 *)(&DAT_43e787c0 + iVar6),iVar1);
      FUN_436c1bd8(*(undefined4 *)(&DAT_43e787c4 + iVar6),iVar1);
      FUN_436c1c04(*(undefined4 *)(&DAT_43e787c8 + iVar6),iVar1);
      FUN_436c1c30(*(undefined4 *)(&DAT_43e787cc + iVar6),iVar1);
      FUN_436c1c5c(*(undefined4 *)(&DAT_43e787d0 + iVar6),iVar1);
      FUN_436c1c88(*(undefined4 *)(&DAT_43e787d4 + iVar6),iVar1);
      FUN_436c1cb4(*(undefined4 *)(&DAT_43e787d8 + iVar6),iVar1);
      FUN_436c1ce0(*(undefined4 *)(&DAT_43e787dc + iVar6),iVar1);
      FUN_436c1d0c(*(undefined4 *)(&DAT_43e787e0 + iVar6),iVar1);
      FUN_436c1d38(*(undefined4 *)(&DAT_43e787e4 + iVar6),iVar1);
      FUN_436c1d64(*(undefined4 *)(&DAT_43e787e8 + iVar6),iVar1);
      FUN_436c1d90(*(undefined4 *)(&DAT_43e787ec + iVar6),iVar1);
      FUN_436c1dbc(*(undefined4 *)(&DAT_43e787f0 + iVar6),iVar1);
      FUN_436c1de8(*(undefined4 *)(&DAT_43e787f4 + iVar6),iVar1);
      FUN_436c1e14(iVar6 + 0x43e787f8,iVar1);
      FUN_436c1e70(iVar6 + 0x43e78838,iVar1);
      FUN_436c1ecc(iVar6 + 0x43e78878,iVar1);
      FUN_436c1f48(iVar6 + 0x43e788b8,iVar1);
      FUN_436bd420(&DAT_43e784ec + iVar1 * 0xf0,iVar1);
      FUN_436c133c(&DAT_43e77cd4 + iVar1 * 0x370,iVar1);
      FUN_436c1068(*(undefined4 *)(&DAT_43e77bec + iVar4),iVar1);
      FUN_436c1090(*(undefined4 *)(&DAT_43e77bf0 + iVar4),iVar1);
      FUN_436c10b8(*(undefined4 *)(&DAT_43e77bf4 + iVar4),iVar1);
      FUN_436c10e0(*(undefined4 *)(&DAT_43e77bf8 + iVar4),iVar1);
      FUN_436c1108(*(undefined4 *)(&DAT_43e77bfc + iVar4),iVar1);
      FUN_436c1130(*(undefined4 *)(&DAT_43e77c00 + iVar4),iVar1);
      FUN_436c1158(*(undefined4 *)(&DAT_43e77c04 + iVar4),iVar1);
      FUN_436c1180(*(undefined4 *)(&DAT_43e77c08 + iVar4),iVar1);
      FUN_436c11a8(*(undefined4 *)(&DAT_43e77c0c + iVar4),iVar1);
      FUN_436c11d0(*(undefined4 *)(&DAT_43e77c10 + iVar4),iVar1);
      FUN_436c11f8(*(undefined4 *)(&DAT_43e77c14 + iVar4),iVar1);
      FUN_436c1220(*(undefined4 *)(&DAT_43e77c18 + iVar4),iVar1);
      FUN_436c1248(*(undefined4 *)(&DAT_43e77c1c + iVar4),iVar1);
      FUN_436c1270(*(undefined4 *)(&DAT_43e77c20 + iVar4),iVar1);
      FUN_436c1460(0,0,iVar1);
      FUN_436c13c0(0,iVar1);
      FUN_436c13e8(0,iVar1);
      FUN_436c1410(0,iVar1);
      FUN_436c1438(0,iVar1);
      FUN_436c14a0(0,iVar1);
      FUN_436bf95c(*(undefined4 *)(&DAT_43e78bfc + iVar1 * 4),(&DAT_43f922ef)[iVar1],auStack_28);
      thunk_FUN_439321ac(iVar1 != 0,auStack_28);
      if (iVar1 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 2;
      }
      if (iVar1 == 0) {
        uVar5 = 1;
      }
      else {
        uVar5 = 3;
      }
      FUN_436bfa50(*(undefined4 *)(&DAT_43e78bfc + iVar1 * 4),auStack_30);
      FUN_43b4a64e(uVar3,auStack_30);
      uVar3 = *(undefined4 *)(&DAT_43e78bfc + iVar1 * 4);
      param_3[2] = uStack_2c;
      *param_3 = uStack_2e;
      FUN_436bfa6c(uVar3,auStack_30);
      FUN_43b4a64e(uVar5,auStack_30);
      if ((*(int *)(&DAT_43e78bfc + iVar1 * 4) == 0) ||
         (*(int *)(&DAT_43e78bfc + iVar1 * 4) == 0x11)) {
        param_3[1] = 0xf00;
        *param_3 = 0xf00;
      }
      if (*(int *)(&DAT_43e78c04 + iVar1 * 4) == 0) {
        iVar2 = FUN_436bf500(iVar1,(&DAT_43f9229a)[iVar1]);
      }
      else {
        iVar2 = 1;
      }
      iVar4 = FUN_436bf6dc(iVar1);
      FUN_436bf470(iVar1);
      FUN_436bf664(iVar1);
      if (*(int *)(&DAT_43e77c5c + iVar1 * 4) == 1) {
        FUN_43acb8ea(iVar1);
        FUN_436bf7d0(iVar1);
      }
      FUN_436bf3a8(iVar1);
      if (((iVar2 != 0) && (iVar4 != 0)) && ((byte)(&DAT_43f922ef)[iVar1] < 2)) {
        (&DAT_43f922ef)[iVar1] = (&DAT_43f922ef)[iVar1] + 1;
      }
      FUN_43acb2e8(iVar1);
      uVar3 = 0;
    }
    else {
      uVar3 = 4;
    }
  }
  else {
    uVar3 = 2;
  }
  return uVar3;
}

