/* S41: read-only exports. */

/* 437b4df0 */

void FUN_437b4df0(undefined4 param_1,undefined4 param_2)

{
  short *psVar1;
  
  psVar1 = *(short **)(DAT_437b4e20 + 0x437b4df8 + DAT_437b4e24);
  *psVar1 = *psVar1 + 1;
  FUN_4383b520(0x13,0);
  FUN_437b5b14(param_1,param_2);
  FUN_4383b520(0x13,1);
  return;
}


/* 4383f8f8 */

void FUN_4383f8f8(uint param_1,int param_2,int param_3)

{
  undefined1 uVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  
  iVar2 = DAT_4383fa2c;
  iVar5 = 0;
  iVar4 = 0;
  *(uint *)(param_2 + 0x50) = param_1;
  iVar2 = iVar2 + 0x4383f906;
  do {
    if ((uint)*(byte *)(DAT_4383fa30 + 0x4383f90c + iVar5) == (param_1 & 0xff)) {
      iVar4 = iVar4 * 0x1c + DAT_4383fa30 + 0x4383f90c;
      *(uint *)(param_2 + 0x54) = (uint)*(byte *)(iVar4 + 1);
      *(uint *)(param_2 + 0x58) = (uint)*(byte *)(iVar4 + 2);
      *(uint *)(param_2 + 0x5c) = (uint)*(byte *)(iVar4 + 3);
      *(uint *)(param_2 + 0x60) = (uint)*(byte *)(iVar4 + 4);
      uVar1 = *(undefined1 *)(iVar4 + 6);
      *(uint *)(param_2 + 100) = (uint)*(byte *)(iVar4 + 5);
      *(undefined1 *)(param_2 + 0x68) = uVar1;
      break;
    }
    iVar4 = iVar4 + 1;
    iVar5 = iVar5 + 0x1c;
  } while (iVar4 != 0x11);
  if ((((*(int *)(param_3 + 900) != 0) ||
       (*(char *)(*(int *)(iVar2 + DAT_4383fa34) + 0xf1) == '\x01')) ||
      (*(char *)(*(int *)(iVar2 + DAT_4383fa34) + 0xfc) == '\x01')) ||
     (*(char *)(param_3 + 0x6e9) != '\x01')) {
    *(undefined1 *)(param_2 + 0x68) = 0;
  }
  if (*(char *)(param_2 + 0x8a) == '\x01') {
    *(undefined1 *)(param_2 + 0x68) = 0;
  }
  switch(param_1) {
  case 0:
  case 3:
    *(undefined2 *)(param_2 + 0x6a) = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa38) + 0x32);
    uVar3 = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 0x44);
    break;
  case 1:
  case 0x10:
  case 0x11:
  case 0x12:
  case 0x14:
  case 0x16:
  case 0x17:
  case 0x20:
  case 0x22:
    uVar3 = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 0x46);
    *(undefined2 *)(param_2 + 0x6a) = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 2);
    break;
  case 2:
  case 0x13:
  case 0x15:
  case 0x21:
  case 0x23:
    uVar3 = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 0x48);
    *(undefined2 *)(param_2 + 0x6a) = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 4);
    break;
  default:
    uVar3 = 0;
    *(undefined2 *)(param_2 + 0x6a) = 0;
  }
  *(undefined2 *)(param_2 + 0x6e) = uVar3;
  if (((param_1 == 2) || (param_1 == 0x13)) || ((param_1 == 0x15 || (param_1 == 0x21)))) {
    *(undefined2 *)(param_2 + 0x6c) = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 0x4a);
  }
  else {
    *(undefined2 *)(param_2 + 0x6c) = 0xffff;
  }
  if ((*(char *)(param_2 + 0x8a) == '\x01') &&
     (((param_1 - 0x12 < 4 || (param_1 == 0x20)) || (param_1 == 0x21)))) {
    *(undefined4 *)(param_2 + 0x5c) = 1;
    *(undefined4 *)(param_2 + 100) = 1;
    *(undefined2 *)(param_2 + 0x6c) = *(undefined2 *)(*(int *)(iVar2 + DAT_4383fa3c) + 0x4a);
  }
  return;
}


/* 438678ac */

undefined1
FUN_438678ac(undefined4 param_1,int param_2,undefined4 param_3,uint param_4,char param_5,
            char param_6,int param_7)

{
  char cVar1;
  undefined1 uVar3;
  int iVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  char cVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  byte bVar2;
  
  iVar8 = DAT_43867abc + 0x438678be;
  iVar10 = param_2;
  iVar4 = FUN_43b09420();
  if (iVar4 == 0) {
    return 0;
  }
  iVar4 = **(int **)(iVar8 + DAT_43867ac0);
  if (*(char *)(iVar4 + 0x1be) == '\x01') {
    param_4 = (uint)*(byte *)(iVar4 + 0x1bf);
  }
  if (*(char *)(iVar4 + 0x1c0) == '\x01') {
    param_5 = *(char *)(iVar4 + 0x1c1);
  }
  if (*(char *)(iVar4 + 0x1c2) == '\x01') {
    param_6 = *(char *)(iVar4 + 0x1c3);
  }
  if (param_2 == 1) {
    if (param_4 < 0x1c) {
      uVar9 = *(undefined4 *)(DAT_43867ac4 + 0x43867908 + param_4 * 4);
      goto LAB_4386797e;
    }
  }
  else {
    if (param_5 == '\x1f') {
      uVar9 = 3;
      goto LAB_4386797e;
    }
    if (param_4 != 0x16) {
      if (0x16 < param_4) {
        if (0x17 < param_4) {
          if (param_4 < 0x1c) goto LAB_4386796c;
          if (param_4 == 0x1e) {
            uVar9 = 0xd;
            goto LAB_4386797e;
          }
        }
LAB_4386794c:
        if (((param_5 == ' ') || (param_5 == '&')) ||
           ((param_5 == '\'' || ((param_5 == '(' || (param_5 == ')')))))) {
          uVar9 = 1;
        }
        else {
          uVar9 = 0;
          if (param_7 != 0) {
            if (param_6 == '\x01') {
              uVar9 = 2;
            }
            else {
              uVar9 = 0;
            }
          }
        }
        goto LAB_4386797e;
      }
      if (param_4 == 0x14) {
        if ((((param_5 == ' ') || (param_5 == '&')) || (param_5 == '\'')) || (param_5 == '(')) {
          uVar9 = 9;
        }
        else if (param_5 == ')') {
          uVar9 = 9;
        }
        else {
          uVar9 = 8;
        }
        goto LAB_4386797e;
      }
      if (0x14 < param_4) {
        uVar9 = 10;
        goto LAB_4386797e;
      }
      if (param_4 != 0) goto LAB_4386794c;
    }
  }
LAB_4386796c:
  uVar9 = 0;
LAB_4386797e:
  *(char *)(*(int *)(iVar8 + DAT_43867ac8) + 0x58e) = (char)uVar9;
  switch(uVar9) {
  case 0:
    cVar1 = *(char *)(iVar4 + 0x199);
    cVar7 = *(char *)(iVar4 + 0x198);
    uVar6 = *(undefined2 *)(iVar4 + 0x196);
    uVar5 = *(undefined2 *)(iVar4 + 0x194);
    break;
  case 1:
    cVar1 = *(char *)(iVar4 + 0x19f);
    cVar7 = *(char *)(iVar4 + 0x19e);
    uVar6 = *(undefined2 *)(iVar4 + 0x19c);
    uVar5 = *(undefined2 *)(iVar4 + 0x19a);
    break;
  case 2:
    cVar1 = *(char *)(iVar4 + 0x1a5);
    cVar7 = *(char *)(iVar4 + 0x1a4);
    uVar6 = *(undefined2 *)(iVar4 + 0x1a2);
    uVar5 = *(undefined2 *)(iVar4 + 0x1a0);
    break;
  case 3:
    cVar1 = *(char *)(iVar4 + 0x1bd);
    cVar7 = *(char *)(iVar4 + 0x1bc);
    uVar6 = *(undefined2 *)(iVar4 + 0x1ba);
    uVar5 = *(undefined2 *)(iVar4 + 0x1b8);
    break;
  case 4:
    cVar1 = *(char *)(iVar4 + 0x399);
    cVar7 = *(char *)(iVar4 + 0x398);
    uVar6 = *(undefined2 *)(iVar4 + 0x396);
    uVar5 = *(undefined2 *)(iVar4 + 0x394);
    break;
  case 5:
    cVar1 = *(char *)(iVar4 + 0x39f);
    cVar7 = *(char *)(iVar4 + 0x39e);
    uVar6 = *(undefined2 *)(iVar4 + 0x39c);
    uVar5 = *(undefined2 *)(iVar4 + 0x39a);
    break;
  case 6:
    cVar1 = *(char *)(iVar4 + 0x3a5);
    cVar7 = *(char *)(iVar4 + 0x3a4);
    uVar6 = *(undefined2 *)(iVar4 + 0x3a2);
    uVar5 = *(undefined2 *)(iVar4 + 0x3a0);
    break;
  case 7:
    cVar1 = *(char *)(iVar4 + 0x3ab);
    cVar7 = *(char *)(iVar4 + 0x3aa);
    uVar6 = *(undefined2 *)(iVar4 + 0x3a8);
    uVar5 = *(undefined2 *)(iVar4 + 0x3a6);
    break;
  case 8:
    cVar1 = *(char *)(iVar4 + 0x1ab);
    cVar7 = *(char *)(iVar4 + 0x1aa);
    uVar6 = *(undefined2 *)(iVar4 + 0x1a8);
    uVar5 = *(undefined2 *)(iVar4 + 0x1a6);
    break;
  case 9:
    cVar1 = *(char *)(iVar4 + 0x1b1);
    cVar7 = *(char *)(iVar4 + 0x1b0);
    uVar6 = *(undefined2 *)(iVar4 + 0x1ae);
    uVar5 = *(undefined2 *)(iVar4 + 0x1ac);
    break;
  case 10:
    cVar1 = *(char *)(iVar4 + 0x1b7);
    cVar7 = *(char *)(iVar4 + 0x1b6);
    uVar6 = *(undefined2 *)(iVar4 + 0x1b4);
    uVar5 = *(undefined2 *)(iVar4 + 0x1b2);
    break;
  case 0xb:
    cVar1 = *(char *)(iVar4 + 0x293);
    cVar7 = *(char *)(iVar4 + 0x292);
    uVar6 = *(undefined2 *)(iVar4 + 0x290);
    uVar5 = *(undefined2 *)(iVar4 + 0x28e);
    break;
  case 0xc:
    cVar1 = *(char *)(iVar4 + 0x3b1);
    cVar7 = *(char *)(iVar4 + 0x3b0);
    uVar6 = *(undefined2 *)(iVar4 + 0x3ae);
    uVar5 = *(undefined2 *)(iVar4 + 0x3ac);
    break;
  case 0xd:
    cVar1 = *(char *)(iVar4 + 0x3cf);
    cVar7 = *(char *)(iVar4 + 0x3ce);
    uVar6 = *(undefined2 *)(iVar4 + 0x3cc);
    uVar5 = *(undefined2 *)(iVar4 + 0x3ca);
    break;
  default:
    cVar1 = '\0';
    cVar7 = '\0';
    uVar6 = 0;
    uVar5 = 0;
  }
  bVar2 = cVar7 + cVar1;
  if (0xe < bVar2) {
    bVar2 = 0xf;
  }
  uVar3 = FUN_43b084f8(param_3,uVar5,uVar6,cVar7,bVar2,iVar10);
  return uVar3;
}


/* 43b3c034 */

undefined4 FUN_43b3c034(int param_1)

{
  return *(undefined4 *)(param_1 + 0x3a0);
}

