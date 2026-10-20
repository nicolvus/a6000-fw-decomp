/* S41: read-only exports. */

/* 43b00d1a */

void FUN_43b00d1a(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  switch(*(undefined4 *)(param_2 + 4)) {
  case 0:
    iVar1 = 0x5c0;
    break;
  case 1:
    thunk_FUN_439c5320(param_1 + 0x5d0,param_2 + 8,0x8c);
    return;
  case 2:
    *(undefined4 *)(param_1 + 0x664) = *(undefined4 *)(param_2 + 8);
    return;
  case 3:
    iVar1 = 0x670;
    break;
  default:
    return;
  case 5:
    *(undefined4 *)(param_1 + 0x68c) = *(undefined4 *)(param_2 + 8);
    return;
  case 6:
    uVar2 = *(undefined4 *)(param_2 + 0xc);
    uVar3 = *(undefined4 *)(param_2 + 0x10);
    uVar4 = *(undefined4 *)(param_2 + 0x14);
    *(undefined4 *)(param_1 + 0x698) = *(undefined4 *)(param_2 + 8);
    *(undefined4 *)(param_1 + 0x69c) = uVar2;
    *(undefined4 *)(param_1 + 0x6a0) = uVar3;
    *(undefined4 *)(param_1 + 0x6a4) = uVar4;
    uVar2 = *(undefined4 *)(param_2 + 0x1c);
    uVar3 = *(undefined4 *)(param_2 + 0x20);
    *(undefined4 *)(param_1 + 0x6a8) = *(undefined4 *)(param_2 + 0x18);
    *(undefined4 *)(param_1 + 0x6ac) = uVar2;
    *(undefined4 *)(param_1 + 0x6b0) = uVar3;
    return;
  }
  uVar2 = *(undefined4 *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + iVar1) = *(undefined4 *)(param_2 + 8);
  ((undefined4 *)(param_1 + iVar1))[1] = uVar2;
  return;
}


/* 438069f0 */

void FUN_438069f0(int param_1,undefined1 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar3 = DAT_43806dd0 + 0x43806a00;
  switch(*param_2) {
  case 0:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806dd8 + 0x43806a34);
    }
    FUN_438066d4(param_1,param_2);
    FUN_43b01026(param_1);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806ddc + 0x43806a56;
LAB_43806dc4:
      FUN_43561540(iVar3);
      return;
    }
    break;
  case 1:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806de0 + 0x43806a6a);
    }
    FUN_438066d4(param_1,param_2);
    *(undefined4 *)(param_2 + 0xb8) = *(undefined4 *)(param_1 + 0x568);
    FUN_43b00cd0(param_1,param_2 + 4);
    FUN_43806668(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806de4 + 0x43806a9e;
      goto LAB_43806dc4;
    }
    break;
  case 2:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806de8 + 0x43806ab2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0x578) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0x574) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806dec + 0x43806ade;
      goto LAB_43806dc4;
    }
    break;
  case 3:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e08 + 0x43806bf2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00fe6(param_1);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00fa4(param_1);
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e0c + 0x43806c28;
      goto LAB_43806dc4;
    }
    break;
  case 4:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e10 + 0x43806c3c);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00dac(param_1,param_2 + 4);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00d94(param_1,param_2 + 4);
    }
    FUN_438065fc(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e14 + 0x43806c7e;
      goto LAB_43806dc4;
    }
    break;
  case 5:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e18 + 0x43806c92);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0xd5c) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0xd58) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e1c + 0x43806cbe;
      goto LAB_43806dc4;
    }
    break;
  case 6:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806df0 + 0x43806af2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00e74(param_1,*(undefined4 *)(param_2 + 4));
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00e9a(param_1,*(undefined4 *)(param_2 + 4));
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806df4 + 0x43806b2c;
      goto LAB_43806dc4;
    }
    break;
  case 7:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806df8 + 0x43806b40);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00d78(param_1,param_2);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00d1a(param_1,param_2);
    }
    if (((*(char *)(iVar3 + 0x49) == '\0') || (*(int *)(param_2 + 4) == 7)) ||
       (*(int *)(param_2 + 4) == 6)) {
      FUN_43b00ec0(param_1,*(undefined2 *)(param_2 + 2),*(undefined4 *)(param_2 + 4));
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806dfc + 0x43806b94;
      goto LAB_43806dc4;
    }
    break;
  case 8:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e00 + 0x43806ba8);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + (*(int *)(param_2 + 4) + 0x2d4) * 2) == *(short *)(param_2 + 8)) {
      *(undefined4 *)(param_1 + (*(int *)(param_2 + 4) + 0x162) * 4) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e04 + 0x43806bde;
      goto LAB_43806dc4;
    }
    break;
  case 9:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e20 + 0x43806cd2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00f62(param_1);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00f22(param_1);
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e24 + 0x43806d06;
      goto LAB_43806dc4;
    }
    break;
  case 10:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e28 + 0x43806d1a);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      *(undefined4 *)(param_1 + 0x6bc) = *(undefined4 *)(param_2 + 0xc);
      FUN_43b00dac(param_1,param_2 + 0x14);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      *(undefined4 *)(param_2 + 0xbc) = 2;
      FUN_43b00cd0(param_1,param_2 + 8);
      uVar1 = *(undefined4 *)(param_2 + 0x574);
      uVar2 = *(undefined4 *)(param_2 + 0x578);
      uVar4 = *(undefined4 *)(param_2 + 0x57c);
      *(undefined4 *)(param_1 + 0x698) = *(undefined4 *)(param_2 + 0x570);
      *(undefined4 *)(param_1 + 0x69c) = uVar1;
      *(undefined4 *)(param_1 + 0x6a0) = uVar2;
      *(undefined4 *)(param_1 + 0x6a4) = uVar4;
      uVar1 = *(undefined4 *)(param_2 + 0x584);
      uVar2 = *(undefined4 *)(param_2 + 0x588);
      *(undefined4 *)(param_1 + 0x6a8) = *(undefined4 *)(param_2 + 0x580);
      *(undefined4 *)(param_1 + 0x6ac) = uVar1;
      *(undefined4 *)(param_1 + 0x6b0) = uVar2;
      FUN_43b00d94(param_1,param_2 + 0x590);
    }
    FUN_43806590(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e2c + 0x43806d88;
      goto LAB_43806dc4;
    }
    break;
  case 0xb:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e30 + 0x43806d9c);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0x570) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0x56c) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e34 + 0x43806dc6;
      goto LAB_43806dc4;
    }
  }
  return;
}


/* 438069f0 */

void FUN_438069f0(int param_1,undefined1 *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar3 = DAT_43806dd0 + 0x43806a00;
  switch(*param_2) {
  case 0:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806dd8 + 0x43806a34);
    }
    FUN_438066d4(param_1,param_2);
    FUN_43b01026(param_1);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806ddc + 0x43806a56;
LAB_43806dc4:
      FUN_43561540(iVar3);
      return;
    }
    break;
  case 1:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806de0 + 0x43806a6a);
    }
    FUN_438066d4(param_1,param_2);
    *(undefined4 *)(param_2 + 0xb8) = *(undefined4 *)(param_1 + 0x568);
    FUN_43b00cd0(param_1,param_2 + 4);
    FUN_43806668(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806de4 + 0x43806a9e;
      goto LAB_43806dc4;
    }
    break;
  case 2:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806de8 + 0x43806ab2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0x578) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0x574) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806dec + 0x43806ade;
      goto LAB_43806dc4;
    }
    break;
  case 3:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e08 + 0x43806bf2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00fe6(param_1);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00fa4(param_1);
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e0c + 0x43806c28;
      goto LAB_43806dc4;
    }
    break;
  case 4:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e10 + 0x43806c3c);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00dac(param_1,param_2 + 4);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00d94(param_1,param_2 + 4);
    }
    FUN_438065fc(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e14 + 0x43806c7e;
      goto LAB_43806dc4;
    }
    break;
  case 5:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e18 + 0x43806c92);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0xd5c) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0xd58) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e1c + 0x43806cbe;
      goto LAB_43806dc4;
    }
    break;
  case 6:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806df0 + 0x43806af2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00e74(param_1,*(undefined4 *)(param_2 + 4));
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00e9a(param_1,*(undefined4 *)(param_2 + 4));
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806df4 + 0x43806b2c;
      goto LAB_43806dc4;
    }
    break;
  case 7:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806df8 + 0x43806b40);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00d78(param_1,param_2);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00d1a(param_1,param_2);
    }
    if (((*(char *)(iVar3 + 0x49) == '\0') || (*(int *)(param_2 + 4) == 7)) ||
       (*(int *)(param_2 + 4) == 6)) {
      FUN_43b00ec0(param_1,*(undefined2 *)(param_2 + 2),*(undefined4 *)(param_2 + 4));
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806dfc + 0x43806b94;
      goto LAB_43806dc4;
    }
    break;
  case 8:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e00 + 0x43806ba8);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + (*(int *)(param_2 + 4) + 0x2d4) * 2) == *(short *)(param_2 + 8)) {
      *(undefined4 *)(param_1 + (*(int *)(param_2 + 4) + 0x162) * 4) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e04 + 0x43806bde;
      goto LAB_43806dc4;
    }
    break;
  case 9:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e20 + 0x43806cd2);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      FUN_43b00f62(param_1);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      FUN_43b00f22(param_1);
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e24 + 0x43806d06;
      goto LAB_43806dc4;
    }
    break;
  case 10:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e28 + 0x43806d1a);
    }
    FUN_438066d4(param_1,param_2);
    if (*(int *)(param_1 + 0x568) == 1) {
      *(undefined4 *)(param_1 + 0x6bc) = *(undefined4 *)(param_2 + 0xc);
      FUN_43b00dac(param_1,param_2 + 0x14);
    }
    else if (*(int *)(param_1 + 0x568) == 2) {
      *(undefined4 *)(param_2 + 0xbc) = 2;
      FUN_43b00cd0(param_1,param_2 + 8);
      uVar1 = *(undefined4 *)(param_2 + 0x574);
      uVar2 = *(undefined4 *)(param_2 + 0x578);
      uVar4 = *(undefined4 *)(param_2 + 0x57c);
      *(undefined4 *)(param_1 + 0x698) = *(undefined4 *)(param_2 + 0x570);
      *(undefined4 *)(param_1 + 0x69c) = uVar1;
      *(undefined4 *)(param_1 + 0x6a0) = uVar2;
      *(undefined4 *)(param_1 + 0x6a4) = uVar4;
      uVar1 = *(undefined4 *)(param_2 + 0x584);
      uVar2 = *(undefined4 *)(param_2 + 0x588);
      *(undefined4 *)(param_1 + 0x6a8) = *(undefined4 *)(param_2 + 0x580);
      *(undefined4 *)(param_1 + 0x6ac) = uVar1;
      *(undefined4 *)(param_1 + 0x6b0) = uVar2;
      FUN_43b00d94(param_1,param_2 + 0x590);
    }
    FUN_43806590(param_1,*(undefined2 *)(param_2 + 2));
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e2c + 0x43806d88;
      goto LAB_43806dc4;
    }
    break;
  case 0xb:
    iVar3 = *(int *)(iVar3 + DAT_43806dd4);
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      FUN_43561540(DAT_43806e30 + 0x43806d9c);
    }
    FUN_438066d4(param_1,param_2);
    if (*(short *)(param_1 + 0x570) == *(short *)(param_2 + 4)) {
      *(undefined4 *)(param_1 + 0x56c) = 0;
    }
    if ((*(byte *)(iVar3 + 0x40) & 0x40) != 0) {
      iVar3 = DAT_43806e34 + 0x43806dc6;
      goto LAB_43806dc4;
    }
  }
  return;
}

