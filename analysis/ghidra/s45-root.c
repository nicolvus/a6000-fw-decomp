/* S41: read-only exports. */

/* 43ae8d56 */

void FUN_43ae8d56(int param_1,int *param_2)

{
  int iVar1;
  
  param_2[1] = param_1 + 0x560;
  *param_2 = param_1;
  param_2[2] = param_1 + 0x5a4;
  param_2[3] = param_1 + 0x1290;
  param_2[4] = param_1 + 0x1730;
  param_2[6] = param_1 + 0x18d4;
  param_2[5] = param_1 + 0x1990;
  param_2[7] = param_1 + 0x1ad0;
  param_2[8] = param_1 + 0x1ade;
  param_2[9] = param_1 + 0x1aec;
  param_2[10] = param_1 + 0x1bcc;
  param_2[0xb] = param_1 + 0x1d40;
  param_2[0xc] = param_1 + 0x1e3c;
  param_2[0x14] = param_1 + 0x1e6c;
  iVar1 = *(int *)(param_1 + 0x1e4c);
  param_2[0x1d] = param_1 + 0x1acc;
  param_2[0x1f] = param_1 + 0x1398;
  param_2[0x17] = param_1 + 0x172c;
  param_2[0x20] = param_1 + 0x1b18;
  param_2[0x22] = param_1 + 0x1750;
  param_2[0x19] = param_1 + 0x18cc;
  param_2[0x23] = param_1 + 0x1d3c;
  param_2[0x26] = param_1 + 0x18d1;
  param_2[0x15] = iVar1;
  param_2[0x1b] = param_1 + 0x1e1c;
  param_2[0x25] = param_1 + 0x18d0;
  param_2[0x27] = param_1 + 0x1e18;
  param_2[0x29] = param_1 + 0x197c;
  param_2[0x2b] = param_1 + 0x19e4;
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

