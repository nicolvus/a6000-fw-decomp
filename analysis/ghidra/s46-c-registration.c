/* S41: read-only exports. */

/* 437da100 */

void FUN_437da100(ushort *param_1,uint param_2,uint param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = param_3;
  if (*(char *)(*(int *)(DAT_437da278 + 0x437da114 + DAT_437da27c) + 0x9b) == '\0') {
    param_1[300] = 0;
    param_1[0x12d] = 0;
    if (param_3 == 0) {
      iVar2 = DAT_437da280 + 0x437da12a;
LAB_437da1d0:
      uVar3 = 0xa6;
      goto LAB_437da19e;
    }
    iVar2 = DAT_437da284 + 0x437da130;
LAB_437da25c:
    uVar3 = 0xb8;
    goto LAB_437da260;
  }
  param_1[300] = 0;
  param_1[0x12d] = 0;
  if (param_2 != 0x404) {
    if (param_2 == 0x490) {
      uVar3 = 6;
      iVar2 = DAT_437da2c0 + 0x437da23c;
      goto LAB_437da260;
    }
    if (param_2 < 0x491) {
      if (param_2 != 0x460) {
        if (param_2 < 0x461) {
          if (param_2 == 0x450) {
            uVar3 = 2;
            iVar2 = DAT_437da2b0 + 0x437da220;
            goto LAB_437da260;
          }
        }
        else {
          if (param_2 == 0x470) {
            iVar2 = DAT_437da2b8 + 0x437da22c;
LAB_437da240:
            uVar3 = 1;
            goto LAB_437da260;
          }
          if (param_2 == 0x480) {
            iVar2 = DAT_437da2bc + 0x437da232;
            goto LAB_437da230;
          }
        }
        goto LAB_437da256;
      }
      iVar2 = DAT_437da2b4 + 0x437da226;
    }
    else if (param_2 == 0x4b0) {
      iVar2 = DAT_437da2c8 + 0x437da24a;
    }
    else {
      if (param_2 < 0x4b1) {
        if (param_2 == 0x4a0) {
          iVar2 = DAT_437da2c4 + 0x437da242;
          goto LAB_437da240;
        }
LAB_437da256:
        iVar2 = DAT_437da2d4 + 0x437da25e;
        goto LAB_437da25c;
      }
      if (param_2 == 0x4c0) {
        iVar2 = DAT_437da2cc + 0x437da250;
      }
      else {
        if (param_2 != 0x4d0) goto LAB_437da256;
        iVar2 = DAT_437da2d0 + 0x437da256;
      }
    }
LAB_437da230:
    uVar3 = 3;
    goto LAB_437da260;
  }
  if (param_3 != 0) goto LAB_437da256;
  uVar1 = param_1[1];
  if (uVar1 == 0x490) {
    uVar3 = 6;
    iVar2 = DAT_437da298 + 0x437da1b0;
    goto LAB_437da19e;
  }
  if (uVar1 < 0x491) {
    if (uVar1 == 0x460) {
      iVar2 = DAT_437da28c + 0x437da198;
      goto LAB_437da1c6;
    }
    if (uVar1 < 0x461) {
      if (uVar1 != 0x450) goto LAB_437da1ca;
      uVar3 = 2;
      iVar2 = DAT_437da288 + 0x437da192;
    }
    else {
      if (uVar1 != 0x470) {
        if (uVar1 != 0x480) goto LAB_437da1ca;
        iVar2 = DAT_437da294 + 0x437da1a8;
        goto LAB_437da1c6;
      }
      iVar2 = DAT_437da290 + 0x437da19e;
LAB_437da19c:
      uVar3 = 1;
    }
  }
  else {
    if (uVar1 == 0x4b0) {
      iVar2 = DAT_437da2a0 + 0x437da1bc;
    }
    else {
      if (uVar1 < 0x4b1) {
        if (uVar1 == 0x4a0) {
          iVar2 = DAT_437da29c + 0x437da1b6;
          goto LAB_437da19c;
        }
LAB_437da1ca:
        iVar2 = DAT_437da2ac + 0x437da1d2;
        goto LAB_437da1d0;
      }
      if (uVar1 == 0x4c0) {
        iVar2 = DAT_437da2a4 + 0x437da1c2;
      }
      else {
        if (uVar1 != 0x4d0) goto LAB_437da1ca;
        iVar2 = DAT_437da2a8 + 0x437da1c8;
      }
    }
LAB_437da1c6:
    uVar3 = 3;
  }
LAB_437da19e:
  uVar4 = (uint)*param_1;
LAB_437da260:
  FUN_43af6870(param_1,iVar2,uVar3,uVar4);
  *param_1 = (ushort)param_3;
  param_1[1] = (ushort)param_2;
  FUN_439c5320(param_1 + 2,param_4,0x124);
  return;
}


/* 437d9ea8 */

undefined4 FUN_437d9ea8(uint param_1,uint param_2)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = 0;
  if (*(char *)(*(int *)(DAT_437d9f68 + 0x437d9eb2 + DAT_437d9f6c) + 0x9b) == '\0') {
    do {
      if (*(ushort *)(DAT_437d9f70 + 0x437d9ec2 + iVar2 * 8) == param_2) {
        return *(undefined4 *)(DAT_437d9f70 + 0x437d9ec2 + iVar2 * 8 + 4);
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 != 0x24);
    return 0xa000;
  }
  if (param_1 == 0x490) {
    puVar1 = (ushort *)(DAT_437d9f84 + 0x437d9f40);
  }
  else if (param_1 < 0x491) {
    if (param_1 == 0x460) {
      puVar1 = (ushort *)(DAT_437d9f78 + 0x437d9f2a);
    }
    else if (param_1 < 0x461) {
      if (param_1 != 0x450) {
LAB_437d9f5a:
        iVar2 = 0x24;
        puVar1 = (ushort *)(DAT_437d9f98 + 0x437d9f62);
        goto LAB_437d9f60;
      }
      puVar1 = (ushort *)(DAT_437d9f74 + 0x437d9f24);
    }
    else {
      if (param_1 != 0x470) {
        if (param_1 == 0x480) {
          iVar2 = 3;
          puVar1 = (ushort *)(DAT_437d9f80 + 0x437d9f3a);
          goto LAB_437d9f60;
        }
        goto LAB_437d9f5a;
      }
      puVar1 = (ushort *)(DAT_437d9f7c + 0x437d9f32);
    }
  }
  else if (param_1 == 0x4b0) {
    puVar1 = (ushort *)(DAT_437d9f8c + 0x437d9f4c);
  }
  else if (param_1 < 0x4b1) {
    if (param_1 != 0x4a0) goto LAB_437d9f5a;
    puVar1 = (ushort *)(DAT_437d9f88 + 0x437d9f46);
  }
  else {
    if (param_1 == 0x4c0) {
      iVar2 = 2;
      puVar1 = (ushort *)(DAT_437d9f90 + 0x437d9f54);
      goto LAB_437d9f60;
    }
    if (param_1 != 0x4d0) goto LAB_437d9f5a;
    puVar1 = (ushort *)(DAT_437d9f94 + 0x437d9f5a);
  }
  iVar2 = 1;
LAB_437d9f60:
  iVar3 = 0;
  while( true ) {
    if (iVar2 <= iVar3) {
      return 0xa000;
    }
    if (*puVar1 == param_2) break;
    iVar3 = iVar3 + 1;
    puVar1 = puVar1 + 4;
  }
  return *(undefined4 *)(puVar1 + 2);
}

