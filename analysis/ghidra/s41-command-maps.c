/* S41: read-only exports. */

/* 43b027c8 */

void FUN_43b027c8(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined1 *apuStack_24 [3];
  
  if (*(int *)(param_1 + 4) != 0) {
    FUN_43ae85ae(param_2);
    FUN_437876dc();
    iVar1 = FUN_43b00cb4();
    if (iVar1 == 1) {
      uVar2 = FUN_437876dc();
      iVar1 = FUN_43805854(uVar2,0x3034);
      if (iVar1 != 0) {
        FUN_437876dc();
        FUN_43805808();
      }
    }
    iVar1 = FUN_435612d0(*(undefined4 *)(param_1 + 4),apuStack_24,0xc,1);
    if (iVar1 == 0) {
      FUN_4380a044(apuStack_24[0]);
      *apuStack_24[0] = 1;
      *(undefined2 *)(apuStack_24[0] + 2) = 0x3034;
      *(undefined4 *)(apuStack_24[0] + 4) = param_2;
      *(undefined4 *)(apuStack_24[0] + 8) = param_3;
      iVar1 = FUN_4356120c(*(undefined4 *)(param_1 + 4));
      if (iVar1 == 0) {
        return;
      }
      uVar2 = 0xab;
      iVar3 = DAT_4380a110 + 0x4380a0fa;
      iVar4 = DAT_4380a114 + 0x4380a100;
    }
    else {
      uVar2 = 0x99;
      iVar3 = DAT_4380a108 + 0x4380a0c6;
      iVar4 = DAT_4380a10c + 0x4380a0ca;
    }
    FUN_43787b70(iVar3,uVar2,iVar4,1,iVar1,0,0);
  }
  return;
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


/* 438066d4 */

void FUN_438066d4(undefined4 param_1,char *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(DAT_43806988 + 0x438066dc + DAT_4380698c);
  if (((*(byte *)(iVar1 + 0x40) & 1) != 0) && (*param_2 == '\0')) {
    FUN_43805604(3,0xd,1,DAT_43806990 + 0x43806706,0,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_43806994 + 0x43806710,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x40) & 2) != 0) && (*param_2 == '\x01')) {
    FUN_43805604(3,0xd,1,DAT_43806998 + 0x4380673a,1,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_4380699c + 0x43806744,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x40) & 4) != 0) && (*param_2 == '\x02')) {
    FUN_43805604(3,0xd,1,DAT_438069a0 + 0x43806770,2,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069a4 + 0x4380677a,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x43) & 1) != 0) && (*param_2 == '\x06')) {
    FUN_43805604(3,0xd,1,DAT_438069a8 + 0x438067aa,6,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
    FUN_43902718(DAT_438069ac + 0x438067bc,*param_2,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
  }
  if (((*(byte *)(iVar1 + 0x43) & 2) != 0) && (*param_2 == '\a')) {
    FUN_43805604(3,0xd,1,DAT_438069b0 + 0x438067e8,7,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
    FUN_43902718(DAT_438069b4 + 0x438067fa,*param_2,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
  }
  if (((*(byte *)(iVar1 + 0x43) & 4) != 0) && (*param_2 == '\b')) {
    FUN_43805604(3,0xd,1,DAT_438069b8 + 0x43806826,8,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
    FUN_43902718(DAT_438069bc + 0x43806838,*param_2,param_2[1],*(undefined2 *)(param_2 + 2),
                 *(undefined4 *)(param_2 + 4));
  }
  if (((*(byte *)(iVar1 + 0x45) & 1) != 0) && (*param_2 == '\x03')) {
    FUN_43805604(3,0xd,1,DAT_438069c0 + 0x4380685e,3,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069c4 + 0x43806868,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x45) & 2) != 0) && (*param_2 == '\x04')) {
    FUN_43805604(3,0xd,1,DAT_438069c8 + 0x43806894,4,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069cc + 0x4380689e,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x45) & 4) != 0) && (*param_2 == '\x05')) {
    FUN_43805604(3,0xd,1,DAT_438069d0 + 0x438068ca,5,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069d4 + 0x438068d4,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x40) & 1) != 0) && (*param_2 == '\t')) {
    FUN_43805604(3,0xd,1,DAT_438069d8 + 0x43806900,9,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069dc + 0x4380690a,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x40) & 2) != 0) && (*param_2 == '\n')) {
    FUN_43805604(3,0xd,1,DAT_438069e0 + 0x43806936,10,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069e4 + 0x43806940,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
  }
  if (((*(byte *)(iVar1 + 0x40) & 4) != 0) && (*param_2 == '\v')) {
    FUN_43805604(3,0xd,1,DAT_438069e8 + 0x4380696c,0xb,param_2[1],*(undefined2 *)(param_2 + 2));
    FUN_43902718(DAT_438069ec + 0x43806976,*param_2,param_2[1],*(undefined2 *)(param_2 + 2));
    return;
  }
  return;
}

