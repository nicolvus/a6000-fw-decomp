/* S41: read-only exports. */

/* 4385ca3c */

void FUN_4385ca3c(undefined1 *param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  char cVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  char cVar6;
  uint uVar7;
  byte bVar8;
  char *pcVar9;
  undefined1 *puVar10;
  int iVar11;
  int iVar12;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  undefined1 auStack_3d [4];
  undefined1 auStack_39 [5];
  undefined2 auStack_34 [2];
  undefined2 uStack_30;
  byte bStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  param_1[0x1db] = 0;
  param_1[0x1fc] = 0;
  param_1[0x1fe] = 0;
  param_1[0x70] = 0;
  param_1[2] = 0;
  iVar11 = DAT_4385ce24;
  param_1[0x212] = *(undefined1 *)(param_4 + 0x52);
  iVar11 = iVar11 + 0x4385ca72;
  param_1[0x213] = *(undefined1 *)(param_4 + 0x58e);
  param_1[0x214] = *(undefined1 *)(param_4 + 0x590);
  param_1[1] = *(undefined1 *)(param_3 + 0xd0);
  *param_1 = *(undefined1 *)(param_3 + 0xa5);
  FUN_438fab10();
  pcVar9 = *(char **)(iVar11 + DAT_4385ce28);
  if (pcVar9[0x1c] == '\x01') {
    uVar3 = FUN_4383fca0(param_2,param_3);
    FUN_43b6d442(7,1);
    FUN_43b6d442(6,1);
    if (*(uint *)(param_2 + 0x348) < 7) {
      cVar6 = *(char *)(DAT_4385ce2c + 0x4385cace + *(uint *)(param_2 + 0x348));
    }
    else {
      cVar6 = '\0';
    }
    uVar7 = (uint)*(byte *)(param_3 + 0xec);
    if (*(char *)(param_3 + 2) == '\x01') {
      if (uVar7 == 1) {
        cVar6 = '\0';
      }
      else {
        if (uVar7 != 2) goto LAB_4385cb30;
        if (*(char *)(param_3 + 0xf8) == '\x01') {
          if (*(char *)(param_3 + 0xf7) == '\0') {
            cVar6 = '\x03';
          }
          else {
LAB_4385cb04:
            if (cVar6 == '\0') {
              cVar6 = '\x01';
            }
            else if (*(ushort *)(param_1 + 0x92) < 0x1297) {
              cVar6 = '\x02';
            }
            else {
              cVar6 = '\x01';
            }
          }
        }
        else {
          if ((*(char *)(param_3 + 0xf8) != '\0') || (*(char *)(param_3 + 0xf7) != '\x01'))
          goto LAB_4385cb04;
          cVar6 = '\x04';
        }
      }
    }
    else if (uVar7 < 3) {
      cVar6 = *(char *)(DAT_4385ce30 + 0x4385cb22 + uVar7);
    }
    else {
LAB_4385cb30:
      cVar6 = '\x06';
    }
    cVar1 = **(char **)(iVar11 + DAT_4385ce34);
    if ((cVar1 != '\0') && (cVar6 = cVar1, cVar1 == -1)) {
      cVar6 = '\0';
    }
    uVar2 = *(undefined1 *)(param_3 + 0xec);
    param_1[0x8d] = uVar3;
    param_1[0x94] = cVar6;
    param_1[0x95] = 8;
    param_1[0x8c] = uVar2;
    param_1[0xa0] = 2;
    param_1[0x96] = 0;
    param_1[0x97] = 0;
    param_1[0x98] = 0;
    param_1[0x99] = 0;
    param_1[0x9a] = 0;
    param_1[0x9b] = 0;
    param_1[0x9c] = 0;
    param_1[0x9d] = 0;
    param_1[0x9e] = 0;
    param_1[0x9f] = 0;
    FUN_438febd0(&uStack_40);
    param_1[0x19a] = uStack_40;
    param_1[0x19b] = uStack_3f;
    puVar10 = param_1;
    iVar5 = 0;
    do {
      iVar12 = iVar5 + 1;
      puVar10[0x19d] = auStack_3d[iVar5];
      puVar10[0x1a1] = auStack_39[iVar5];
      puVar10 = puVar10 + 1;
      iVar5 = iVar12;
    } while (iVar12 != 4);
    uVar4 = FUN_438feadc();
    FUN_438feaf4(param_1 + 0xa1,uVar4);
    FUN_438feaf4(param_1 + 0xb5,uVar4);
    uVar4 = FUN_438feae8();
    FUN_439c5a04(param_1 + 0xc9,0,uVar4);
    *(undefined4 *)(param_1 + 0xf4) = 0;
    *(undefined2 *)(param_1 + 0xf8) = 0;
    *(undefined2 *)(param_1 + 0xfa) = 0;
    param_1[0x10a] = 0;
    param_1[0x10b] = 0;
    param_1[0x10c] = 0;
    param_1[0x10e] = 0;
    param_1[0x10d] = 0;
    param_1[0x10f] = 0;
    param_1[0x111] = 0;
    param_1[0x110] = 0;
    param_1[0x112] = 0;
    param_1[0x113] = 0;
    param_1[0x114] = 0;
    param_1[0x115] = 0;
    param_1[0x116] = 0;
    param_1[0x117] = 0;
    *(undefined4 *)(param_1 + 0x11c) = 0;
    *(undefined4 *)(param_1 + 0x120) = 0;
    *(undefined4 *)(param_1 + 0x118) = 0;
    *(undefined4 *)(param_1 + 0x128) = 0;
    *(undefined4 *)(param_1 + 0x124) = 0;
    FUN_438feb4c(&bStack_2c);
    if ((byte)param_1[0x94] - 3 < 2) {
      if ((bStack_2c & 1) == 0) {
        bVar8 = param_1[300] & 0xfe | bStack_2c & 1;
      }
      else {
        bVar8 = param_1[300] | 1;
      }
    }
    else {
      bVar8 = param_1[300] & 0xfe;
    }
    param_1[300] = bVar8;
    param_1[0x133] = 0;
    param_1[300] = param_1[300] & 0xf1 | bStack_2c & 2 | bStack_2c & 4 | bStack_2c & 8;
    param_1[0x134] = 0;
    param_1[0x12d] = uStack_2b;
    param_1[0x12e] = uStack_2a;
    param_1[0x12f] = uStack_29;
    uVar3 = FUN_438feae8();
    param_1[0x130] = 0;
    param_1[0x131] = 0;
    param_1[0x135] = uVar3;
    uVar3 = FUN_438feadc();
    param_1[0x132] = uVar3;
    FUN_438feb10(auStack_34);
    *(undefined2 *)(param_1 + 0x8e) = uStack_30;
    *(undefined2 *)(param_1 + 0x90) = auStack_34[0];
    param_1[0x136] = 0;
    param_1[0x137] = 0;
    param_1[0x138] = 0;
    param_1[0x139] = 0;
    *(undefined2 *)(param_1 + 0x13a) = 0;
    *(undefined2 *)(param_1 + 0x16a) = 0;
    FUN_43857ecc(0x280,param_1[0x8d]);
    FUN_43857ecc(0x281,param_1[0x94]);
    uVar3 = param_1[0x8d];
    param_1[0x1a5] = *(undefined1 *)(param_3 + 0xfd);
    param_1[0x1a6] =
         *(byte *)(param_3 + 0xeb) & 7 | (*(byte *)(param_3 + 0xee) & 3) << 3 |
         (*(byte *)(param_3 + 0xef) & 1) << 5 | (*(byte *)(param_3 + 0xf1) & 1) << 6 |
         *(char *)(param_3 + 0xf2) << 7;
    if (*(char *)(param_3 + 2) == '\x01') {
      if (*(char *)(param_2 + 0x38e) == '\x03') {
        uVar4 = 2;
      }
      else if (*(char *)(param_2 + 0x38e) == '\x02') {
        uVar4 = 3;
      }
      else {
        iVar5 = FUN_43b0a4ee(uVar3);
        if ((iVar5 == 1) || (iVar5 = FUN_43b0a4fa(uVar3), iVar5 == 1)) {
          uVar4 = 1;
        }
        else {
          FUN_43b0a4ca(param_6,param_2);
          uVar4 = 1;
        }
      }
    }
    else {
      uVar4 = 0;
    }
    cVar6 = **(char **)(iVar11 + DAT_4385ce38);
    if (cVar6 != '\0') {
      if ((cVar6 == '\x01') || (cVar6 == '\x02')) {
        uVar4 = 0;
      }
      else if (cVar6 == '\x03') {
        uVar4 = 1;
      }
      else if (cVar6 == '\x04') {
        uVar4 = 2;
      }
      else if (cVar6 == '\x05') {
        uVar4 = 3;
      }
    }
    *(undefined4 *)(param_5 + 0x10) = uVar4;
  }
  else if (*(int *)(param_2 + 0x4f8) != 2) {
    *(uint *)(param_5 + 0x10) = (uint)(*(char *)(param_6 + 0x6fd) != '\0');
  }
  if (*pcVar9 == '\0') {
    if ((pcVar9[0x1c] != '\0') || (iVar5 = FUN_438fb300(), iVar5 == 0)) {
      if (pcVar9[0x1c] == '\x01') goto LAB_4385cdf8;
LAB_4385ce06:
      uVar3 = 0;
      goto LAB_4385ce08;
    }
  }
  else if (*(char *)(param_3 + 0xfb) != '\x01') {
LAB_4385cdf8:
    iVar5 = FUN_4384a190(param_3);
    if (iVar5 != 1) goto LAB_4385ce06;
  }
  uVar3 = 1;
LAB_4385ce08:
  *(undefined1 *)(*(int *)(iVar11 + DAT_4385ce3c) + 0x23d) = uVar3;
  *(undefined1 *)(param_5 + 0x15) = uVar3;
  return;
}


/* 4385cf2c */

void FUN_4385cf2c(char *param_1,short *param_2,int param_3,int param_4,int param_5)

{
  char cVar1;
  uint uVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined1 auStack_100 [4];
  uint uStack_fc;
  int iStack_8c;
  undefined2 uStack_88;
  undefined2 uStack_86;
  char cStack_79;
  char cStack_78;
  char cStack_77;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 uStack_5c;
  undefined1 uStack_5b;
  char cStack_5a;
  undefined1 uStack_59;
  undefined1 uStack_58;
  char cStack_57;
  undefined4 uStack_54;
  undefined4 uStack_50;
  int iStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  char cStack_34;
  char cStack_33;
  undefined4 uStack_30;
  char cStack_2c;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined4 uStack_24;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  int iStack_1c;
  
  if (*(char *)(*(int *)(DAT_4385d270 + 0x4385cf3c + DAT_4385d274) + 0x1c) != '\x01')
  goto LAB_4385d1ae;
  if ((byte)param_1[0x8c] < 2) {
    if (param_1[3] == '\0') {
      if (*(char *)(param_5 + 0x562) == '\0') {
        sVar3 = *(short *)(param_3 + 0x68);
        if ((sVar3 != 0) && (sVar3 != 1)) {
          if (*(ushort *)(param_1 + 0x92) < 0x1001) {
LAB_4385cfc2:
            sVar3 = 3;
          }
          else {
            sVar3 = 2;
          }
        }
      }
      else {
        sVar3 = 0xb;
      }
    }
    else if (*(char *)(param_5 + 0x562) == '\0') {
LAB_4385cfcc:
      if (*(ushort *)(param_1 + 0x92) < 0x1297) {
        sVar3 = 5;
      }
      else {
        sVar3 = 4;
      }
    }
    else {
      sVar3 = 0xc;
    }
LAB_4385cfe2:
    param_1[0x95] = (char)sVar3;
  }
  else if (param_1[0x8c] == 2) {
    cVar1 = *(char *)(param_5 + 0x562);
    if (param_1[2] == '\x01') {
      if (param_1[3] == '\0') {
        if (cVar1 == '\0') {
          sVar3 = *(short *)(param_3 + 0x68);
          if ((sVar3 != 0) && (sVar3 != 1)) {
            if (*(ushort *)(param_1 + 0x92) < 0x1001) goto LAB_4385cfc2;
            param_1[0x95] = '\x02';
            goto LAB_4385cfe6;
          }
        }
        else {
          sVar3 = 6;
        }
      }
      else {
        if (cVar1 == '\0') goto LAB_4385cfcc;
        sVar3 = 7;
      }
    }
    else if (cVar1 == '\0') {
      if (*(ushort *)(param_3 + 0x68) < 2) {
        sVar3 = 8;
      }
      else {
        sVar3 = 0xd;
      }
    }
    else {
      sVar3 = 0xe;
    }
    goto LAB_4385cfe2;
  }
LAB_4385cfe6:
  if ((*(int *)(param_5 + 8) == 0x19) || (*param_2 == 0x313)) {
    param_1[0x95] = '\b';
  }
  iVar5 = *(int *)(param_3 + 0xe4);
  iVar6 = *(int *)(param_3 + 0x104) * *(int *)(*(int *)(param_4 + 4) + 4) +
          *(int *)(param_3 + 0x100) + 0x1e00;
  uStack_fc = (uint)(byte)param_1[0x95];
  iVar4 = iVar5 + *(int *)(param_3 + 0xe8);
  if (uStack_fc < 0xd) {
    uVar2 = 1 << (uint)(byte)param_1[0x95];
    if ((uVar2 & 0x14b0) == 0) {
      if ((uVar2 & 0xa4e) != 0) {
        *(int *)(param_1 + 0x118) = iVar6;
        param_1[0x120] = '\0';
        param_1[0x121] = '\0';
        param_1[0x122] = '\0';
        param_1[0x123] = '\0';
        *(int *)(param_1 + 0x11c) = iVar4;
        goto LAB_4385d094;
      }
      if ((uVar2 & 1) == 0) goto LAB_4385d086;
      *(int *)(param_1 + 0x118) = iVar6;
      *(int *)(param_1 + 0x120) = iVar4;
      param_1[0x11c] = '\0';
      param_1[0x11d] = '\0';
      param_1[0x11e] = '\0';
      param_1[0x11f] = '\0';
      param_1[0x128] = '\0';
      param_1[0x129] = '\0';
      param_1[0x12a] = '\0';
      param_1[299] = '\0';
      iVar4 = 0;
    }
    else {
      iVar4 = *(int *)(param_3 + 0xe8) + -0xfa000;
      param_1[0x118] = '\0';
      param_1[0x119] = '\0';
      param_1[0x11a] = '\0';
      param_1[0x11b] = '\0';
      param_1[0x120] = '\0';
      param_1[0x121] = '\0';
      param_1[0x122] = '\0';
      param_1[0x123] = '\0';
      param_1[0x11c] = '\0';
      param_1[0x11d] = '\0';
      param_1[0x11e] = '\0';
      param_1[0x11f] = '\0';
      *(int *)(param_1 + 0x128) = iVar5 + 0xfa000;
    }
    *(int *)(param_1 + 0x124) = iVar4;
  }
  else {
LAB_4385d086:
    param_1[0x118] = '\0';
    param_1[0x119] = '\0';
    param_1[0x11a] = '\0';
    param_1[0x11b] = '\0';
    param_1[0x120] = '\0';
    param_1[0x121] = '\0';
    param_1[0x122] = '\0';
    param_1[0x123] = '\0';
    param_1[0x11c] = '\0';
    param_1[0x11d] = '\0';
    param_1[0x11e] = '\0';
    param_1[0x11f] = '\0';
LAB_4385d094:
    param_1[0x128] = '\0';
    param_1[0x129] = '\0';
    param_1[0x12a] = '\0';
    param_1[299] = '\0';
    param_1[0x124] = '\0';
    param_1[0x125] = '\0';
    param_1[0x126] = '\0';
    param_1[0x127] = '\0';
  }
  cStack_79 = param_1[0x115];
  uStack_88 = *(undefined2 *)(param_3 + 0x68);
  cStack_78 = param_1[0x116];
  iStack_8c = (uint)*(ushort *)(param_3 + 0xd8) * *(int *)(param_3 + 0xc);
  param_1[0xfa] = '\0';
  param_1[0xfb] = '\0';
  cStack_77 = param_1[0x117];
  param_1[0x133] = '\0';
  param_1[0x134] = '\0';
  uStack_70 = *(undefined4 *)(param_1 + 0x11c);
  param_1[0x130] = '\0';
  param_1[0x131] = '\0';
  uStack_6c = *(undefined4 *)(param_1 + 0x120);
  param_1[0x136] = '\0';
  param_1[0x137] = '\0';
  uStack_74 = *(undefined4 *)(param_1 + 0x118);
  uStack_86 = 0;
  uStack_59 = 0;
  uStack_64 = *(undefined4 *)(param_1 + 0x128);
  *(undefined2 *)(param_1 + 0xf8) = uStack_88;
  uStack_68 = *(undefined4 *)(param_1 + 0x124);
  *(int *)(param_1 + 0xf4) = iStack_8c;
  uStack_58 = 0;
  cStack_57 = param_1[0x135];
  cStack_5a = param_1[0x132];
  uStack_5c = 0;
  uStack_5b = 0;
  uStack_54 = 0;
  uStack_50 = 0;
  FUN_438feab4(&cStack_34,auStack_100);
  param_1[0xfc] = cStack_34;
  param_1[0xfd] = cStack_33;
  *(undefined4 *)(param_1 + 0x100) = uStack_30;
  param_1[0x104] = cStack_2c;
  FUN_43857ecc(0x284,param_1[0x95]);
  FUN_43857ecc(0x28a,param_1[0x112]);
  FUN_43857ecc(0x28b,param_1[0x113]);
  FUN_43857ecc(0x28c,param_1[0x114]);
  FUN_43857ecc(0x28d,param_1[0x115]);
  FUN_43857ecc(0x28e,param_1[0x116]);
  FUN_43857ecc(0x28f,param_1[0x117]);
LAB_4385d1ae:
  if (param_1[2] == '\x01') {
    uStack_28 = *(undefined2 *)(param_1 + 0x208);
    uStack_26 = *(undefined2 *)(param_1 + 0x3c);
    if (param_1[3] == '\0') {
      iStack_1c = *(int *)(param_3 + 0x104) * *(int *)(*(int *)(param_4 + 4) + 4) +
                  *(int *)(param_3 + 0x100) + 0x1e00;
      uStack_20 = uStack_28;
      uStack_1e = uStack_26;
      FUN_438fef9c(&uStack_20,&iStack_40);
    }
    else {
      uStack_24 = *(undefined4 *)(param_3 + 0xe8);
      FUN_438fef30(&uStack_28,&iStack_40);
    }
    if (*param_1 == '\x01') {
      iStack_40 = *(int *)(param_3 + 0x104) * *(int *)(*(int *)(param_4 + 4) + 4) +
                  *(int *)(param_3 + 0x100) + 0x1e00;
      uStack_3c = 0x1f400;
    }
    *(undefined4 *)(param_3 + 0x144) = 0;
    *(undefined4 *)(param_3 + 0x150) = 0;
    *(int *)(param_3 + 0x13c) = iStack_40;
    *(undefined4 *)(param_3 + 0x140) = uStack_3c;
    *(undefined4 *)(param_1 + 0x240) = uStack_3c;
    *(undefined4 *)(param_1 + 0x244) = uStack_38;
    *(short *)(param_1 + 0x248) = (short)((uint)uStack_3c >> 8);
    *(short *)(param_1 + 0x24a) = (short)((uint)uStack_38 >> 8);
  }
  else {
    *(undefined4 *)(param_3 + 0x13c) = 0;
    *(undefined4 *)(param_3 + 0x140) = 0;
    *(undefined4 *)(param_3 + 0x144) = 0;
    param_1[0x240] = '\0';
    param_1[0x241] = '\0';
    param_1[0x242] = '\0';
    param_1[0x243] = '\0';
    param_1[0x244] = '\0';
    param_1[0x245] = '\0';
    param_1[0x246] = '\0';
    param_1[0x247] = '\0';
    param_1[0x248] = '\0';
    param_1[0x249] = '\0';
    param_1[0x24a] = '\0';
    param_1[0x24b] = '\0';
  }
  return;
}


/* 4385d278 */

void FUN_4385d278(int param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined1 uVar1;
  undefined1 auStack_dc [4];
  uint uStack_d8;
  int iStack_68;
  undefined2 uStack_64;
  undefined2 uStack_62;
  undefined1 uStack_38;
  undefined1 uStack_37;
  undefined1 uStack_36;
  undefined1 uStack_35;
  undefined1 uStack_34;
  undefined1 uStack_33;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined4 uStack_18;
  undefined1 uStack_14;
  
  if (*(char *)(*(int *)(DAT_4385d348 + 0x4385d284 + DAT_4385d34c) + 0x1c) != '\x01') {
    return;
  }
  if (*(char *)(param_1 + 0x8c) == '\x02') {
    if (*(char *)(param_4 + 0x562) != '\0') {
      uVar1 = 0xe;
      goto LAB_4385d2b2;
    }
    if (1 < *(ushort *)(param_2 + 0x68)) {
      uVar1 = 0xd;
      goto LAB_4385d2b2;
    }
  }
  else if (*(char *)(param_4 + 0x562) != '\0') {
    uVar1 = 0xf;
    goto LAB_4385d2b2;
  }
  uVar1 = 8;
LAB_4385d2b2:
  *(undefined1 *)(param_1 + 0x95) = uVar1;
  iStack_68 = (uint)*(ushort *)(param_2 + 0xd8) * *(int *)(param_2 + 0xc);
  uStack_64 = *(undefined2 *)(param_2 + 0x68);
  uStack_36 = *(undefined1 *)(param_1 + 0x132);
  uStack_d8 = (uint)*(byte *)(param_1 + 0x95);
  *(undefined2 *)(param_1 + 0xf8) = uStack_64;
  uStack_33 = *(undefined1 *)(param_1 + 0x135);
  *(int *)(param_1 + 0xf4) = iStack_68;
  *(undefined2 *)(param_1 + 0xfa) = 0;
  *(undefined1 *)(param_1 + 0x133) = 0;
  *(undefined1 *)(param_1 + 0x134) = 0;
  *(undefined1 *)(param_1 + 0x130) = 0;
  *(undefined1 *)(param_1 + 0x131) = 0;
  *(undefined1 *)(param_1 + 0x136) = 0;
  *(undefined1 *)(param_1 + 0x137) = 0;
  uStack_62 = 0;
  uStack_35 = 0;
  uStack_34 = 0;
  uStack_38 = 0;
  uStack_37 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  FUN_438feab4(&uStack_1c,auStack_dc);
  *(undefined1 *)(param_1 + 0xfc) = uStack_1c;
  *(undefined1 *)(param_1 + 0xfd) = uStack_1b;
  *(undefined4 *)(param_1 + 0x100) = uStack_18;
  *(undefined1 *)(param_1 + 0x104) = uStack_14;
  return;
}


/* 438631c4 */

void FUN_438631c4(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7,int param_8,short *param_9)

{
  int iVar1;
  short sVar2;
  ushort uVar3;
  byte bVar4;
  byte bVar5;
  short sVar6;
  ushort uVar7;
  short sVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  ushort uVar11;
  int *piVar12;
  int iVar13;
  short *psVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  short sVar18;
  undefined4 uVar19;
  int iVar20;
  uint uVar21;
  short *psVar22;
  int *piVar23;
  ushort *puVar24;
  char cVar25;
  undefined1 uVar26;
  short sVar27;
  int iVar28;
  int iVar29;
  uint uVar30;
  int iVar31;
  uint *puVar32;
  undefined4 uVar33;
  int iVar34;
  uint uVar35;
  int iVar36;
  uint uVar37;
  undefined1 uVar38;
  int iVar39;
  undefined4 *puVar40;
  uint uStack_84;
  int iStack_68;
  int aiStack_64 [14];
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  uVar33 = *(undefined4 *)(param_1 + 0x3c0);
  iVar31 = DAT_43863dc8 + 0x438631da;
  uVar19 = *(undefined4 *)(param_1 + 0x3bc);
  *(undefined4 *)(param_9 + 8) = uVar19;
  *(undefined4 *)(param_9 + 10) = uVar33;
  *(undefined1 *)(param_9 + 0x10) = *(undefined1 *)(param_1 + 0x3d6);
  *(undefined1 *)((int)param_9 + 0x21) = *(undefined1 *)(param_6 + 0x42);
  *(undefined1 *)(param_9 + 0x11) = *(undefined1 *)(param_6 + 0x32);
  sVar6 = *(short *)(param_1 + 0x2f0);
  sVar8 = *(short *)(param_1 + 0x11e);
  param_9[0x12] = *(short *)(param_2 + 0x1c6);
  sVar2 = *(short *)(param_2 + 0x54);
  param_9[0x13] = sVar6;
  param_9[0x16] = sVar8;
  param_9[0x17] = sVar2;
  *(undefined1 *)(param_9 + 0x1a) = *(undefined1 *)(param_4 + 2);
  iVar34 = *(int *)(iVar31 + DAT_43863dcc);
  *(undefined1 *)((int)param_9 + 0x35) = *(undefined1 *)(iVar34 + 0x22);
  iVar28 = 0;
  *(undefined1 *)((int)param_9 + 0x37) = 0;
  *(undefined1 *)((int)param_9 + 0x31) = *(undefined1 *)(param_1 + 0x22a);
  *(undefined1 *)(param_9 + 0x1e) = *(undefined1 *)(param_1 + 0x432);
  *(undefined1 *)((int)param_9 + 0x3d) = *(undefined1 *)(param_1 + 0x433);
  piVar12 = *(int **)(iVar31 + DAT_43863dd0);
  *(undefined1 *)(param_9 + 0x1f) = *(undefined1 *)(*piVar12 + 0x286);
  param_9[0x20] = *(short *)(param_2 + 0x1e4);
  *(undefined1 *)(param_9 + 0x232) = *(undefined1 *)(param_1 + 0x657);
  *(undefined1 *)((int)param_9 + 0x465) = *(undefined1 *)(param_1 + 0x658);
  sVar6 = *(short *)(param_7 + 0x4c4);
  param_9[0x235] = *(short *)(param_7 + 0x4c2);
  uVar33 = *(undefined4 *)(param_1 + 0x640);
  param_9[0x236] = sVar6;
  *(undefined4 *)(param_9 + 0x248) = uVar33;
  *(undefined1 *)((int)param_9 + 0x495) = *(undefined1 *)(param_5 + 0xbd9);
  *(undefined1 *)(param_9 + 0x24b) = *(undefined1 *)(param_5 + 0xbd6);
  param_9[0x16b] = *(short *)(param_5 + 0xc6a);
  psVar14 = param_9;
  do {
    iVar13 = param_7 + iVar28;
    iVar28 = iVar28 + 4;
    psVar14[0x237] = *(short *)(iVar13 + 4);
    psVar14 = psVar14 + 1;
  } while (iVar28 != 0x38);
  if ((*(int *)(param_1 + 700) == 0) || (*(int *)(param_1 + 700) == 4)) {
    uVar26 = 0;
  }
  else {
    uVar26 = 1;
  }
  *(undefined1 *)(param_9 + 0x18) = uVar26;
  sVar6 = *(short *)(param_1 + 0x576);
  sVar8 = *(short *)(param_1 + 0x512);
  sVar2 = *(short *)(param_1 + 0x514);
  sVar18 = *(short *)(param_1 + 0x578);
  param_9[0x279] = *(short *)(param_1 + 0x510);
  param_9[0x282] = sVar6;
  sVar6 = *(short *)(param_1 + 0x57a);
  uVar33 = *(undefined4 *)(param_1 + 0x4f8);
  param_9[0x27a] = sVar8;
  param_9[0x27b] = sVar2;
  param_9[0x283] = sVar18;
  param_9[0x284] = sVar6;
  *(char *)(param_9 + 0x285) = (char)uVar33;
  iVar28 = FUN_4382ffe0((char)param_9[0x18],uVar19);
  if (iVar28 == 0) {
    param_9[0x19] = 0;
  }
  else if (*(char *)(param_8 + 1) == '\x01') {
    param_9[0x19] = 1;
  }
  else {
    param_9[0x19] = 0;
  }
  FUN_4386208c(param_9);
  FUN_43b0ad1c(param_9);
  sVar6 = FUN_439027ec((int)param_9[0x13],0x100);
  iVar28 = (int)param_9[0x13];
  param_9[0x14] = sVar6;
  if (iVar28 < 0) {
    cVar25 = -(char)(iVar28 + 0x3f >> 6);
  }
  else {
    cVar25 = (char)(iVar28 >> 6);
  }
  *(char *)(param_9 + 0x15) = cVar25;
  if (0x1f < *(byte *)(param_9 + 0x15)) {
    *(undefined1 *)(param_9 + 0x15) = 0x1f;
  }
  iVar28 = DAT_43863dd4;
  *(undefined1 *)(param_9 + 6) = 1;
  iVar28 = *(int *)(iVar31 + iVar28);
  if ((*(int *)(param_9 + 8) == 0) && (*(char *)(iVar28 + 0x49) == '\0')) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x924) == 1) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((*(char *)(iVar28 + 0x49) == '\x01') && (*(int *)(param_1 + 0x40c) != 0)) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x2b4) == 0x1f) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  cVar25 = *(char *)(iVar34 + 2);
  if ((cVar25 == '\x01') || (cVar25 == '\x02')) {
    *(char *)(param_9 + 6) = cVar25 + -1;
  }
  if (*(char *)((int)param_9 + 0x21) != '\0') {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((char)param_9[0x11] != '\0') {
    *(undefined1 *)(param_9 + 6) = 1;
  }
  uVar26 = 0;
  if ((char)param_9[6] == '\0') {
LAB_43863652:
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
  }
  else {
    sVar6 = param_9[0x14];
    iVar29 = 0;
    iVar13 = param_3;
    iVar39 = param_3;
    do {
      iVar17 = 0;
      puVar32 = (uint *)(param_9 + iVar29 * 2 + 0x20);
      iVar20 = iVar17;
      do {
        iVar36 = iVar39 + iVar17;
        iVar17 = iVar17 + 0xc;
        iVar1 = iVar20 * 2;
        puVar32 = puVar32 + 1;
        *puVar32 = (uint)(*(int *)(iVar36 + 0x338) * (int)sVar6) >> 8;
        iVar36 = iVar20 + iVar29;
        iVar20 = iVar20 + 1;
        *(undefined1 *)((int)param_9 + iVar36 + 0x1d0) = *(undefined1 *)(iVar13 + iVar1 + 0x964);
      } while (iVar20 != 0xb);
      iVar29 = iVar29 + 0xb;
      iVar13 = iVar13 + 0x16;
      iVar39 = iVar39 + 0x84;
    } while (iVar29 != 99);
    iVar13 = 0;
    psVar14 = param_9;
    do {
      iVar13 = iVar13 + 1;
      uVar21 = 0;
      psVar14[0x11a] = 0;
      psVar14[0x11b] = 0;
      psVar14 = psVar14 + 2;
    } while (iVar13 != 0x20);
    uVar30 = (uint)*(byte *)(param_9 + 0x15);
    iVar13 = 0;
    if (uVar30 == 0) {
      do {
        iVar39 = iVar13 + 4;
        *(undefined4 *)((int)param_9 + iVar13 + 0x234) = *(undefined4 *)(param_7 + iVar13 + 0xa4);
        iVar13 = iVar39;
      } while (iVar39 != 0x80);
    }
    else {
      iVar13 = param_7;
      if (param_9[0x13] < 0) {
        for (; uVar21 <= uVar30; uVar21 = uVar21 + 1) {
          *(int *)(param_9 + 0x11a) = *(int *)(iVar13 + 0xa4) + *(int *)(param_9 + 0x11a);
          iVar13 = iVar13 + 4;
        }
        puVar40 = (undefined4 *)(param_7 + uVar30 * 4 + 0xa4);
        uVar21 = 1;
        psVar14 = param_9;
        while( true ) {
          uVar35 = 0x20 - uVar30;
          if (uVar35 <= uVar21) break;
          puVar40 = puVar40 + 1;
          uVar21 = uVar21 + 1;
          *(undefined4 *)(psVar14 + 0x11c) = *puVar40;
          psVar14 = psVar14 + 2;
        }
        psVar14 = param_9 + uVar35 * 2 + 0x118;
        for (; uVar35 < 0x20; uVar35 = uVar35 + 1) {
          psVar14 = psVar14 + 2;
          psVar14[0] = 0;
          psVar14[1] = 0;
        }
      }
      else {
        uVar21 = 0;
        psVar14 = param_9;
        while( true ) {
          iVar13 = 0;
          uVar35 = uVar30;
          if (uVar30 <= uVar21) break;
          psVar14[0x11a] = 0;
          psVar14[0x11b] = 0;
          uVar21 = uVar21 + 1;
          psVar14 = psVar14 + 2;
        }
        for (; uVar35 < 0x1f; uVar35 = uVar35 + 1) {
          iVar29 = param_7 + iVar13;
          iVar39 = iVar13 + uVar30 * 4;
          iVar13 = iVar13 + 4;
          *(undefined4 *)((int)param_9 + iVar39 + 0x234) = *(undefined4 *)(iVar29 + 0xa4);
        }
        uVar30 = 0x20 - uVar30;
        piVar23 = (int *)(param_7 + uVar30 * 4 + 0xa0);
        for (; uVar30 < 0x20; uVar30 = uVar30 + 1) {
          piVar23 = piVar23 + 1;
          *(int *)(param_9 + 0x158) = *(int *)(param_9 + 0x158) + *piVar23;
        }
      }
    }
    iVar13 = *(int *)(param_7 + 0x4bc);
    if (iVar13 == 0) {
      iVar13 = 0x10000;
    }
    *(int *)(param_9 + 0x15a) = iVar13;
    FUN_43b0abd8(param_9);
    sVar6 = *param_9;
    if (sVar6 == 0) {
      sVar6 = param_9[0x160];
    }
    sVar8 = param_9[1];
    if (sVar8 == 0) {
      sVar8 = param_9[0x161];
    }
    sVar2 = param_9[2];
    if (sVar2 == 0) {
      sVar2 = param_9[0x162];
    }
    sVar18 = param_9[3];
    if (sVar18 == 0) {
      sVar18 = param_9[0x161];
    }
    uVar7 = param_9[4];
    if ((ushort)param_9[5] < (ushort)param_9[4]) {
      uVar7 = param_9[5];
    }
    param_9[0x168] = uVar7;
    sVar27 = param_9[0x13] * 4;
    param_9[0x167] = sVar18 + sVar27;
    param_9[0x164] = sVar6 + sVar27;
    param_9[0x165] = sVar8 + sVar27;
    param_9[0x166] = sVar2 + sVar27;
    if ((param_9[0x19] == 0) || (*(char *)(param_3 + 0xc35) == '\0')) {
      param_9[0x16c] = 0;
      param_9[0x169] = 0;
      param_9[0x16a] = 0;
    }
    else {
      uVar7 = FUN_4355faf0(*(undefined4 *)(param_8 + 4));
      param_9[0x169] = uVar7;
      if (0x3ff < uVar7) {
        param_9[0x169] = 0x3ff;
      }
      sVar6 = FUN_438625d0(((ushort)param_9[0x169] & 0x3fff) << 2);
      param_9[0x16a] = sVar6 + param_9[0x13] * 4;
      sVar6 = FUN_438625d0(((ushort)param_9[0x16b] & 0x3fff) << 2);
      param_9[0x16c] = sVar6;
    }
    if (param_9[0x19] == 0) {
      if (((char)param_9[0x10] == '\x01') && (*(char *)(iVar28 + 0x49) == '\x01')) {
        uVar26 = 7;
      }
      else {
        uVar26 = 1;
      }
    }
    else {
      uVar26 = 5;
    }
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
    if ((((char)param_9[0x1f] != '\0') && (*(char *)(iVar28 + 0x49) == '\x01')) &&
       ((char)param_9[0x10] == '\x01')) {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if ((char)param_9[0x11] != '\0') {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if (*(char *)((int)param_9 + 0x35) != '\0') {
      uVar26 = 8;
      goto LAB_43863652;
    }
  }
  if ((char)param_9[6] == '\0') goto LAB_43863fe2;
  if (*(char *)(param_1 + 0xc) == '\x04') {
    FUN_439c5320(param_9 + 0x187,param_9 + 0x19b,0x14);
    FUN_439c5320(param_9 + 0x191,param_9 + 0x1a5,0x14);
    goto LAB_43863fe2;
  }
  FUN_43861ed0(param_9);
  FUN_43865254(param_9);
  if (((char)param_9[0x1f] == '\0') || ((char)param_9[0x10] != '\x01')) {
    iVar13 = *(int *)(param_9 + 8);
    if (((iVar13 == 1) || (iVar13 == 8)) || ((iVar13 == 0 && (*(char *)(iVar28 + 0x49) == '\x01'))))
    {
      FUN_438621bc(param_9);
    }
    FUN_43b0acee(param_9);
    FUN_43b0ad9a(param_9);
    FUN_43b0ace4(param_9);
    if ((char)param_9[0x11] == '\0') {
      if (*(char *)((int)param_9 + 0x31) == '\0') {
        bVar4 = *(byte *)(iVar34 + 0xcb);
      }
      else {
        bVar4 = *(byte *)(iVar34 + 0xcc);
      }
      uVar11 = (ushort)bVar4 * 2;
      uVar7 = param_9[0x21c];
      if (param_9[0x19] == 0) {
        uVar26 = 0;
        if (uVar7 != 0) {
          param_9[0x21c] = uVar7 - 1;
          goto LAB_438636fa;
        }
LAB_438636fc:
        *(undefined1 *)(param_9 + 0x21d) = uVar26;
      }
      else {
        if (uVar11 <= uVar7) {
LAB_438636fa:
          uVar26 = 1;
          goto LAB_438636fc;
        }
        if ((char)param_9[0x21d] == '\0') {
          uVar3 = (ushort)*(byte *)(iVar34 + 0xcd);
        }
        else {
          uVar3 = 1;
        }
        param_9[0x21c] = uVar7 + uVar3;
      }
      if (uVar11 < (ushort)param_9[0x21c]) {
        param_9[0x21c] = uVar11;
      }
      if ((char)param_9[0x21d] == '\0') {
        if (*(char *)(iVar34 + 0xca) == '\0') goto LAB_4386372a;
        uVar26 = *(undefined1 *)(iVar34 + 0xce);
      }
      else if (*(char *)(iVar34 + 0xca) == '\0') {
LAB_4386372a:
        uVar26 = *(undefined1 *)(iVar34 + 0xd0);
      }
      else {
        uVar26 = *(undefined1 *)(iVar34 + 0xcf);
      }
      param_9[0x187] = 0;
      param_9[0x191] = 0;
      param_9[0x1e8] = 0;
      param_9[0x1e9] = 0;
      param_9[0x1fc] = 0;
      param_9[0x1fd] = 0;
      param_9[400] = 0x3400;
      param_9[0x19a] = 0x3400;
      param_9[0x1fa] = 0x3400;
      param_9[0x1fb] = 0;
      param_9[0x20e] = 0x3400;
      param_9[0x20f] = 0;
      if (*(char *)(iVar34 + 0x55) == '\0') {
        if ((char)param_9[0x24a] == '\0') {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar26 = 0;
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,0,0,0);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,0,0,0);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
        else {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar38 = *(undefined1 *)(DAT_43863dd8 + 0x438637d2);
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,uVar26,uVar26,uVar38);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,uVar26,uVar26,uVar38);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
      }
      *(undefined1 *)(param_9 + 0x24a) = 1;
      *(undefined1 *)(DAT_43863ddc + 0x43863822) = uVar26;
      psVar14 = param_9;
      iVar28 = 0;
      do {
        iVar13 = iVar28;
        uVar30 = (uint)(ushort)psVar14[0x187];
        uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
        uVar21 = (uint)(ushort)psVar14[0x191];
        uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
        iVar28 = 0;
        psVar22 = param_9 + iVar13 + 0x1ae;
        do {
          iVar28 = iVar28 + 1;
          psVar22[1] = (short)uVar30;
          psVar22[0x1d] = (short)uVar21;
          uVar30 = uVar30 + uVar7 & 0xffff;
          uVar21 = uVar21 + uVar11 & 0xffff;
          psVar22 = psVar22 + 1;
        } while (iVar28 != 3);
        psVar14 = psVar14 + 1;
        iVar28 = iVar13 + 3;
      } while (iVar13 + 3 != 0x18);
      iVar13 = iVar13 + -0x14;
      psVar14 = param_9;
      do {
        uVar7 = psVar14[0x1cd];
        iVar13 = iVar13 + 1;
        sVar6 = FUN_43b07560(((uint)(ushort)psVar14[0x1b2] - (uint)(ushort)psVar14[0x1b1]) *
                             ((uint)(ushort)psVar14[0x1cf] - (uint)uVar7),
                             (uint)(ushort)psVar14[0x1b3] - (uint)(ushort)psVar14[0x1b1]);
        psVar14[0x1ce] = sVar6 + uVar7;
        psVar14 = psVar14 + 3;
      } while (iVar13 != 8);
      uVar7 = param_9[399];
      param_9[0x1af] = param_9[0x187];
      uVar11 = param_9[0x19a];
      uVar3 = param_9[0x199];
      param_9[0x1c7] = uVar7;
      param_9[0x1e3] = uVar3;
      param_9[0x1ca] = param_9[400];
      param_9[0x1cb] = param_9[0x191];
      param_9[0x1e6] = uVar11;
      sVar6 = FUN_4355fd68((uint)(ushort)param_9[400] - (uint)uVar7,3);
      sVar8 = FUN_4355fd68((uint)uVar11 - (uint)uVar3,3);
      param_9[0x1c8] = sVar6 + uVar7;
      param_9[0x1c9] = uVar7 + sVar6 * 2;
      param_9[0x1e4] = sVar8 + uVar3;
      param_9[0x1e5] = uVar3 + sVar8 * 2;
      if ((char)param_9[0x18] == '\x01') {
        piVar23 = *(int **)(iVar31 + DAT_43863dd0);
        iVar28 = *piVar23;
        if (*(char *)(iVar28 + 0x229) != '\0') {
          uVar21 = *(byte *)(param_5 + 0xbd9) - 0x14 & 0xff;
          if (uVar21 < 4) {
            uVar33 = *(undefined4 *)(DAT_43863de0 + 0x4386395e + uVar21 * 4);
          }
          else {
            uVar33 = 0;
          }
          if (*(char *)(iVar28 + 0x22b) == '\x01') {
            switch(uVar33) {
            case 1:
              uVar30 = (uint)*(byte *)(iVar28 + 0x275);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x276) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x277));
              break;
            case 2:
              uVar30 = (uint)*(byte *)(iVar28 + 0x278);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x279) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27a));
              break;
            case 3:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27b);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27c) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27d));
              break;
            case 4:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27e);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27f) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x280));
              break;
            default:
              uVar30 = (uint)*(byte *)(iVar28 + 0x272);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x273) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x274));
            }
            uVar30 = uVar30 * 0x10 + 0x2000;
          }
          else if (*(char *)(iVar28 + 0x22b) == '\x02') {
            switch(uVar33) {
            case 1:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x23e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x23f);
              uVar26 = *(undefined1 *)(iVar28 + 0x23d);
              uVar38 = *(undefined1 *)(iVar28 + 0x23c);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x240),
                                      *(undefined1 *)(iVar28 + 0x241));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x242) * 0x100 + (ushort)*(byte *)(iVar28 + 0x243);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x23b);
              uVar21 = (uint)*(byte *)(iVar28 + 0x23a);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x244),
                                      *(undefined1 *)(iVar28 + 0x245));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x246),
                                      *(undefined1 *)(iVar28 + 0x247));
              break;
            case 2:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x24c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x24d);
              uVar26 = *(undefined1 *)(iVar28 + 0x24b);
              uVar38 = *(undefined1 *)(iVar28 + 0x24a);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x24e),
                                      *(undefined1 *)(iVar28 + 0x24f));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x250) * 0x100 + (ushort)*(byte *)(iVar28 + 0x251);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x249);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x252),
                                      *(undefined1 *)(iVar28 + 0x253));
              uVar21 = (uint)*(byte *)(iVar28 + 0x248);
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x254),
                                      *(undefined1 *)(iVar28 + 0x255));
              break;
            case 3:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x25a) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25b);
              uStack_84 = (uint)*(byte *)(iVar28 + 599);
              uVar26 = *(undefined1 *)(iVar28 + 0x259);
              uVar38 = *(undefined1 *)(iVar28 + 600);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x25c),
                                      *(undefined1 *)(iVar28 + 0x25d));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x25e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25f);
              uVar21 = (uint)*(byte *)(iVar28 + 0x256);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x260),
                                      *(undefined1 *)(iVar28 + 0x261));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x262),
                                      *(undefined1 *)(iVar28 + 0x263));
              break;
            case 4:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x268) * 0x100 + (ushort)*(byte *)(iVar28 + 0x269);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x265);
              uVar26 = *(undefined1 *)(iVar28 + 0x267);
              uVar38 = *(undefined1 *)(iVar28 + 0x266);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26a),
                                      *(undefined1 *)(iVar28 + 0x26b));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x26c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x26d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x264);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26e),
                                      *(undefined1 *)(iVar28 + 0x26f));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x270),
                                      *(undefined1 *)(iVar28 + 0x271));
              break;
            default:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x230) * 0x100 + (ushort)*(byte *)(iVar28 + 0x231);
              uVar26 = *(undefined1 *)(iVar28 + 0x22f);
              uVar38 = *(undefined1 *)(iVar28 + 0x22e);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x232),
                                      *(undefined1 *)(iVar28 + 0x233));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x234) * 0x100 + (ushort)*(byte *)(iVar28 + 0x235);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x22d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x22c);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x236),
                                      *(undefined1 *)(iVar28 + 0x237));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x238),
                                      *(undefined1 *)(iVar28 + 0x239));
            }
            iVar28 = (uVar35 - uVar30) * 0x400;
            uVar7 = FUN_43b07560(iVar28,uVar37 - uVar30);
            if (uVar7 < 0x401) {
              uVar9 = FUN_43b07560(iVar28,uVar37 - uVar30);
            }
            else {
              uVar9 = 0x400;
            }
            uVar15 = FUN_43b0af46(uVar38,0,0x1f);
            uVar16 = FUN_43b0af46(uVar26,0,0x1f);
            iVar28 = 0;
            for (; uVar15 < uVar16; uVar15 = uVar15 + 1 & 0xff) {
              iVar28 = iVar28 + (uint)*(byte *)(param_7 + uVar15 + 0x3f0);
            }
            uVar15 = 0;
            for (; uVar16 < 0x20; uVar16 = uVar16 + 1 & 0xff) {
              uVar15 = uVar15 + *(byte *)(param_7 + uVar16 + 0x3f0) & 0xffff;
            }
            iVar13 = *(int *)(iVar31 + DAT_43863de4);
            *(short *)(iVar13 + 0x59e) = (short)iVar28;
            *(short *)(iVar13 + 0x5a0) = (short)uVar15;
            uVar33 = FUN_43b084e8(iVar28 * uVar21 * 0x80,uVar15 + iVar28);
            bVar4 = FUN_43b0af60(uVar33,0,0x80);
            bVar5 = FUN_43b0af60((int)(uStack_84 * (uVar15 + iVar28)) >> 7,0,0x80);
            uVar21 = 0x4000 - (uint)bVar4 * (uint)bVar5;
            uVar21 = uVar21 & ~((int)uVar21 >> 0x1f);
            uVar10 = FUN_43b0aee8(uVar21,0,0x4000,uVar30,sVar8);
            *(byte *)(iVar13 + 0x5a3) = bVar5;
            *(byte *)(iVar13 + 0x5a2) = bVar4;
            *(uint *)(iVar13 + 0x5a8) = uVar21;
            *(short *)(iVar13 + 0x5a4) = (short)((uint)bVar4 * (uint)bVar5);
            uVar30 = FUN_43862554(uVar10,param_9 + 0x286);
            uVar7 = FUN_43b084e8((uVar35 - uVar30) * 0x400,uVar37 - uVar30);
            *(short *)(iVar13 + 0x596) = (short)uVar35;
            *(short *)(iVar13 + 0x598) = (short)uVar37;
            if (0x3ff < uVar7) {
              uVar7 = 0x400;
            }
            *(ushort *)(iVar13 + 0x594) = uVar7;
            uVar21 = FUN_43b0af2c(uVar7,sVar6,uVar9);
            *(short *)(iVar13 + 0x59a) = sVar6;
            *(undefined2 *)(iVar13 + 0x59c) = uVar9;
          }
          else {
            uVar21 = 0x400;
            uVar30 = 0;
          }
          iVar28 = *piVar23;
          if ((*(byte *)(iVar28 + 0x281) & 2) != 0) {
            uVar30 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x284) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x285));
          }
          if ((*(byte *)(iVar28 + 0x281) & 1) != 0) {
            uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x282) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x283));
          }
          iVar28 = *(int *)(iVar31 + DAT_43863de4);
          *(short *)(iVar28 + 0x590) = (short)uVar30;
          *(short *)(iVar28 + 0x592) = (short)uVar21;
          puVar24 = (ushort *)(param_9 + 0x1cb);
          uVar35 = 0;
          do {
            uVar37 = uVar35;
            if (uVar30 < *puVar24) {
              uVar37 = uVar37 & 0xff;
              goto LAB_43863dbc;
            }
            puVar24 = puVar24 + 1;
            uVar35 = uVar37 + 1;
          } while (uVar37 + 1 != 0x1c);
          uVar37 = uVar37 - 0x1b;
LAB_43863dbc:
          puVar24 = (ushort *)(param_9 + uVar37 + 0x1cb);
          while ((int)uVar37 < 0x1c) {
            uVar7 = *puVar24;
            uVar37 = uVar37 + 1;
            uVar35 = (uVar7 - uVar30) * uVar21 + uVar30 * 0x400 >> 10;
            if ((uVar35 & 0xffff) < (uint)uVar7) {
              uVar7 = (ushort)uVar35;
            }
            *puVar24 = uVar7;
            puVar24 = puVar24 + 1;
          }
        }
      }
    }
    FUN_43b0ad9a(param_9);
    FUN_439c5320(param_9 + 0x19b,param_9 + 0x187,0x14);
    FUN_439c5320(param_9 + 0x1a5,param_9 + 0x191,0x14);
  }
  else {
    FUN_4386261c(param_9);
  }
  if ((char)param_9[0x18] != '\0') {
    if (*(char *)((int)param_9 + 0x3f) == '\x01') {
      iVar28 = 0;
      do {
        *(undefined4 *)((int)aiStack_64 + iVar28) = 0x20;
        iVar28 = iVar28 + 4;
      } while (iVar28 != 0x38);
    }
    else {
      if ((byte)(*(char *)((int)param_9 + 0x495) - 0x14U) < 2) {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x340);
        uStack_2b = *(undefined1 *)(iVar28 + 0x341);
        uStack_2a = *(undefined1 *)(iVar28 + 0x342);
        uStack_29 = *(undefined1 *)(iVar28 + 0x343);
        uVar26 = *(undefined1 *)(iVar28 + 0x344);
        uVar38 = *(undefined1 *)(iVar28 + 0x345);
      }
      else {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x33a);
        uStack_2b = *(undefined1 *)(iVar28 + 0x33b);
        uStack_2a = *(undefined1 *)(iVar28 + 0x33c);
        uStack_29 = *(undefined1 *)(iVar28 + 0x33d);
        uVar26 = *(undefined1 *)(iVar28 + 0x33e);
        uVar38 = *(undefined1 *)(iVar28 + 0x33f);
      }
      FUN_43b0af7a(&uStack_2c,uVar26,uVar38,aiStack_64);
    }
    piVar12 = &iStack_68;
    iVar28 = 0;
    psVar14 = param_9;
    do {
      piVar12 = piVar12 + 1;
      iVar31 = FUN_43b075da(*piVar12 << 8,*(undefined4 *)(psVar14 + 0x256),4);
      iVar13 = iVar28 + 1;
      *(int *)(psVar14 + 0x256) = iVar31;
      psVar14 = psVar14 + 2;
      *(char *)((int)param_9 + iVar28 + 0x4e4) = (char)((uint)(iVar31 + 0x80) >> 8);
      iVar28 = iVar13;
    } while (iVar13 != 0xe);
  }
  if ((char)param_9[0x11] != '\0') {
    param_9[0x196] = 0x3400;
    param_9[0x197] = 0x3400;
    param_9[0x198] = 0x3400;
    param_9[0x199] = 0x3400;
    param_9[0x19a] = 0x3400;
    sVar6 = *(short *)(iVar34 + 0x38);
    iVar28 = 0;
    param_9[0x191] = 0;
    param_9[0x192] = 0;
    param_9[0x193] = 0;
    param_9[0x194] = 0;
    param_9[0x195] = 0;
    param_9[0x187] = 0;
    param_9[0x189] = sVar6;
    param_9[0x18a] = sVar6;
    param_9[0x18b] = sVar6;
    param_9[0x18c] = sVar6;
    param_9[0x18d] = sVar6;
    param_9[0x18e] = sVar6;
    param_9[0x188] = sVar6 + -0x80;
    param_9[399] = sVar6 + 0x80;
    param_9[400] = 0x3400;
    psVar14 = param_9;
    do {
      uVar30 = (uint)(ushort)psVar14[0x187];
      uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
      uVar21 = (uint)(ushort)psVar14[0x191];
      uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
      iVar31 = 0;
      psVar22 = param_9 + iVar28 + 0x1ae;
      do {
        iVar31 = iVar31 + 1;
        psVar22[1] = (short)uVar30;
        psVar22[0x1d] = (short)uVar21;
        uVar30 = uVar30 + uVar7 & 0xffff;
        uVar21 = uVar21 + uVar11 & 0xffff;
        psVar22 = psVar22 + 1;
      } while (iVar31 != 3);
      iVar28 = iVar28 + 3;
      psVar14 = psVar14 + 1;
    } while (iVar28 != 0x1b);
    param_9[0x1ca] = 0x3400;
    param_9[0x1e6] = 0x3400;
  }
LAB_43863fe2:
  iVar28 = FUN_43859ab8();
  sVar6 = param_9[6];
  *(char *)(iVar28 + 0x7a) = (char)sVar6;
  if ((char)sVar6 == '\0') {
    *(undefined1 *)(iVar28 + 0x7b) = 0;
    uVar26 = 0xff;
    *(undefined1 *)(iVar28 + 0x7c) = 0xff;
    *(undefined1 *)(iVar28 + 0x7d) = 0xff;
    *(undefined1 *)(iVar28 + 0x7e) = 0xff;
    *(undefined1 *)(iVar28 + 0x7f) = 0xff;
    *(undefined1 *)(iVar28 + 0x80) = 0xff;
    *(undefined1 *)(iVar28 + 0x81) = 0xff;
    *(undefined1 *)(iVar28 + 0x82) = 0xff;
    *(undefined1 *)(iVar28 + 0x83) = 0xff;
    *(undefined1 *)(iVar28 + 0x84) = 0xff;
    *(undefined1 *)(iVar28 + 0x85) = 0xff;
    *(undefined1 *)(iVar28 + 0x86) = 0xff;
    *(undefined1 *)(iVar28 + 0x87) = 0xff;
    *(undefined1 *)(iVar28 + 0x88) = 0xff;
    *(undefined1 *)(iVar28 + 0x89) = 0xff;
    *(undefined1 *)(iVar28 + 0x8a) = 0xff;
    *(undefined1 *)(iVar28 + 0x8b) = 0xff;
    *(undefined1 *)(iVar28 + 0x8c) = 0xff;
    *(undefined1 *)(iVar28 + 0x8d) = 0xff;
    *(undefined1 *)(iVar28 + 0x8e) = 0xff;
    *(undefined1 *)(iVar28 + 0x8f) = 0xff;
    *(undefined1 *)(iVar28 + 0x90) = 0xff;
    *(undefined1 *)(iVar28 + 0x91) = 0xff;
    *(undefined1 *)(iVar28 + 0x92) = 0xff;
    *(undefined1 *)(iVar28 + 0x93) = 0xff;
    *(undefined1 *)(iVar28 + 0x94) = 0xff;
    *(undefined1 *)(iVar28 + 0x95) = 0xff;
    *(undefined1 *)(iVar28 + 0x96) = 0xff;
    *(undefined1 *)(iVar28 + 0x97) = 0xff;
    *(undefined1 *)(iVar28 + 0x98) = 0xff;
    *(undefined1 *)(iVar28 + 0x99) = 0xff;
    *(undefined1 *)(iVar28 + 0x9a) = 0xff;
    *(undefined1 *)(iVar28 + 0x9b) = 0xff;
    *(undefined1 *)(iVar28 + 0x9c) = 0xff;
    *(undefined1 *)(iVar28 + 0x9d) = 0xff;
    *(undefined1 *)(iVar28 + 0x9e) = 0xff;
    *(undefined1 *)(iVar28 + 0x9f) = 0xff;
    *(undefined1 *)(iVar28 + 0xa0) = 0xff;
    *(undefined1 *)(iVar28 + 0xa1) = 0xff;
    *(undefined1 *)(iVar28 + 0xa2) = 0xff;
    *(undefined1 *)(iVar28 + 0xa3) = 0xff;
    *(undefined1 *)(iVar28 + 0xa4) = 0xff;
    *(undefined1 *)(iVar28 + 0xa5) = 0xff;
    *(undefined1 *)(iVar28 + 0xa6) = 0xff;
    *(undefined1 *)(iVar28 + 0xa7) = 0xff;
    *(undefined1 *)(iVar28 + 0xa8) = 0xff;
    *(undefined1 *)(iVar28 + 0xa9) = 0xff;
    *(undefined1 *)(iVar28 + 0xaa) = 0xff;
    *(undefined1 *)(iVar28 + 0xab) = 0xff;
    *(undefined1 *)(iVar28 + 0xac) = 0xff;
    *(undefined1 *)(iVar28 + 0xad) = 0xff;
    *(undefined1 *)(iVar28 + 0xae) = 0xff;
    *(undefined1 *)(iVar28 + 0xaf) = 0xff;
    *(undefined1 *)(iVar28 + 0xb0) = 0xff;
    *(undefined1 *)(iVar28 + 0xb1) = 0xff;
    *(undefined1 *)(iVar28 + 0xb2) = 0xff;
    *(undefined1 *)(iVar28 + 0xb3) = 0xff;
    *(undefined1 *)(iVar28 + 0xb4) = 0xff;
    *(undefined1 *)(iVar28 + 0xb5) = 0xff;
    *(undefined1 *)(iVar28 + 0xb6) = 0xff;
    *(undefined1 *)(iVar28 + 0xb7) = 0xff;
    *(undefined1 *)(iVar28 + 0xb8) = 0xff;
    *(undefined1 *)(iVar28 + 0xb9) = 0xff;
    *(undefined1 *)(iVar28 + 0xba) = 0xff;
    *(undefined1 *)(iVar28 + 0xbb) = 0xff;
    *(undefined1 *)(iVar28 + 0xbc) = 0xff;
    *(undefined1 *)(iVar28 + 0xbd) = 0xff;
    *(undefined1 *)(iVar28 + 0xbe) = 0xff;
    *(undefined1 *)(iVar28 + 0xbf) = 0xff;
    *(undefined1 *)(iVar28 + 0xc0) = 0xff;
    *(undefined1 *)(iVar28 + 0xc1) = 0xff;
    *(undefined1 *)(iVar28 + 0xc2) = 0xff;
    *(undefined1 *)(iVar28 + 0xc3) = 0xff;
    *(undefined1 *)(iVar28 + 0xc4) = 0xff;
    *(undefined1 *)(iVar28 + 0xc5) = 0xff;
    *(undefined1 *)(iVar28 + 0xc6) = 0xff;
    *(undefined1 *)(iVar28 + 199) = 0xff;
    *(undefined1 *)(iVar28 + 200) = 0xff;
    *(undefined1 *)(iVar28 + 0xc9) = 0xff;
    *(undefined1 *)(iVar28 + 0xca) = 0xff;
    *(undefined1 *)(iVar28 + 0xcb) = 0xff;
    *(undefined1 *)(iVar28 + 0xcc) = 0xff;
    *(undefined1 *)(iVar28 + 0xcd) = 0xff;
    *(undefined1 *)(iVar28 + 0xce) = 0xff;
    *(undefined1 *)(iVar28 + 0xcf) = 0xff;
    *(undefined1 *)(iVar28 + 0xd0) = 0xff;
    *(undefined1 *)(iVar28 + 0xd1) = 0xff;
    *(undefined1 *)(iVar28 + 0xd2) = 0xff;
    *(undefined1 *)(iVar28 + 0xd3) = 0xff;
    *(undefined1 *)(iVar28 + 0xd4) = 0xff;
    *(undefined1 *)(iVar28 + 0xd5) = 0xff;
    *(undefined1 *)(iVar28 + 0xd6) = 0xff;
    *(undefined1 *)(iVar28 + 0xd7) = 0xff;
    *(undefined1 *)(iVar28 + 0xd8) = 0xff;
    *(undefined1 *)(iVar28 + 0xd9) = 0xff;
    *(undefined1 *)(iVar28 + 0xda) = 0xff;
    *(undefined1 *)(iVar28 + 0xdb) = 0xff;
    *(undefined1 *)(iVar28 + 0xdc) = 0xff;
    *(undefined1 *)(iVar28 + 0xdd) = 0xff;
    *(undefined1 *)(iVar28 + 0xde) = 0xff;
    *(undefined1 *)(iVar28 + 0xdf) = 0xff;
    *(undefined1 *)(iVar28 + 0xe0) = 0xff;
    *(undefined1 *)(iVar28 + 0xe1) = 0xff;
    *(undefined1 *)(iVar28 + 0xe2) = 0xff;
    *(undefined1 *)(iVar28 + 0xe3) = 0xff;
    *(undefined1 *)(iVar28 + 0xe4) = 0xff;
    *(undefined1 *)(iVar28 + 0xe5) = 0xff;
    *(undefined1 *)(iVar28 + 0xe6) = 0xff;
    *(undefined1 *)(iVar28 + 0xe7) = 0xff;
    *(undefined1 *)(iVar28 + 0xe8) = 0xff;
    *(undefined1 *)(iVar28 + 0xe9) = 0xff;
    *(undefined1 *)(iVar28 + 0xea) = 0xff;
    *(undefined1 *)(iVar28 + 0xeb) = 0xff;
    *(undefined1 *)(iVar28 + 0xec) = 0xff;
    *(undefined1 *)(iVar28 + 0xed) = 0xff;
  }
  else {
    *(undefined1 *)(iVar28 + 0x7b) = *(undefined1 *)((int)param_9 + 0xd);
    *(char *)(iVar28 + 0x7c) = (char)param_9[7];
    *(undefined1 *)(iVar28 + 0x7d) = *(undefined1 *)((int)param_9 + 0x21);
    *(char *)(iVar28 + 0x7e) = (char)param_9[0x11];
    *(char *)(iVar28 + 0x7f) = (char)param_9[0x13];
    *(undefined1 *)(iVar28 + 0x80) = *(undefined1 *)((int)param_9 + 0x27);
    *(char *)(iVar28 + 0x81) = (char)param_9[0x16];
    *(undefined1 *)(iVar28 + 0x82) = *(undefined1 *)((int)param_9 + 0x2d);
    *(char *)(iVar28 + 0x83) = (char)param_9[0x17];
    *(undefined1 *)(iVar28 + 0x84) = *(undefined1 *)((int)param_9 + 0x2f);
    *(char *)(iVar28 + 0x85) = (char)param_9[0x18];
    *(char *)(iVar28 + 0x86) = (char)param_9[0x19];
    *(undefined1 *)(iVar28 + 0x87) = *(undefined1 *)((int)param_9 + 0x33);
    *(char *)(iVar28 + 0x88) = (char)param_9[0x1a];
    *(undefined1 *)(iVar28 + 0x89) = *(undefined1 *)((int)param_9 + 0x35);
    *(char *)(iVar28 + 0x8a) = (char)param_9[0x232];
    *(undefined1 *)(iVar28 + 0x8b) = *(undefined1 *)((int)param_9 + 0x465);
    *(char *)(iVar28 + 0x8c) = (char)param_9[0x15e];
    *(char *)(iVar28 + 0x8d) = (char)param_9[0x164];
    *(undefined1 *)(iVar28 + 0x8e) = *(undefined1 *)((int)param_9 + 0x2c9);
    *(char *)(iVar28 + 0x8f) = (char)param_9[0x165];
    *(undefined1 *)(iVar28 + 0x90) = *(undefined1 *)((int)param_9 + 0x2cb);
    *(char *)(iVar28 + 0x91) = (char)param_9[0x166];
    *(undefined1 *)(iVar28 + 0x92) = *(undefined1 *)((int)param_9 + 0x2cd);
    *(char *)(iVar28 + 0x93) = (char)param_9[0x167];
    *(undefined1 *)(iVar28 + 0x94) = *(undefined1 *)((int)param_9 + 0x2cf);
    *(char *)(iVar28 + 0x95) = (char)param_9[0x168];
    *(undefined1 *)(iVar28 + 0x96) = *(undefined1 *)((int)param_9 + 0x2d1);
    *(char *)(iVar28 + 0x97) = (char)param_9[0x18a];
    *(undefined1 *)(iVar28 + 0x98) = *(undefined1 *)((int)param_9 + 0x315);
    *(char *)(iVar28 + 0x99) = (char)param_9[0x18b];
    *(undefined1 *)(iVar28 + 0x9a) = *(undefined1 *)((int)param_9 + 0x317);
    *(char *)(iVar28 + 0x9b) = (char)param_9[0x18c];
    *(undefined1 *)(iVar28 + 0x9c) = *(undefined1 *)((int)param_9 + 0x319);
    *(char *)(iVar28 + 0x9d) = (char)param_9[0x18d];
    *(undefined1 *)(iVar28 + 0x9e) = *(undefined1 *)((int)param_9 + 0x31b);
    *(char *)(iVar28 + 0x9f) = (char)param_9[0x18e];
    *(undefined1 *)(iVar28 + 0xa0) = *(undefined1 *)((int)param_9 + 0x31d);
    *(char *)(iVar28 + 0xa1) = (char)param_9[0x194];
    *(undefined1 *)(iVar28 + 0xa2) = *(undefined1 *)((int)param_9 + 0x329);
    *(char *)(iVar28 + 0xa3) = (char)param_9[0x195];
    *(undefined1 *)(iVar28 + 0xa4) = *(undefined1 *)((int)param_9 + 0x32b);
    *(char *)(iVar28 + 0xa5) = (char)param_9[0x196];
    *(undefined1 *)(iVar28 + 0xa6) = *(undefined1 *)((int)param_9 + 0x32d);
    *(char *)(iVar28 + 0xa7) = (char)param_9[0x197];
    *(undefined1 *)(iVar28 + 0xa8) = *(undefined1 *)((int)param_9 + 0x32f);
    *(char *)(iVar28 + 0xa9) = (char)param_9[0x198];
    *(undefined1 *)(iVar28 + 0xaa) = *(undefined1 *)((int)param_9 + 0x331);
    *(char *)(iVar28 + 0xab) = (char)param_9[0x188];
    *(undefined1 *)(iVar28 + 0xac) = *(undefined1 *)((int)param_9 + 0x311);
    *(char *)(iVar28 + 0xad) = (char)param_9[399];
    *(undefined1 *)(iVar28 + 0xae) = *(undefined1 *)((int)param_9 + 799);
    *(char *)(iVar28 + 0xaf) = (char)param_9[0x16d];
    *(undefined1 *)(iVar28 + 0xb0) = *(undefined1 *)((int)param_9 + 0x2db);
    *(char *)(iVar28 + 0xb1) = (char)param_9[0x254];
    *(undefined1 *)(iVar28 + 0xb2) = *(undefined1 *)((int)param_9 + 0x4a9);
    *(char *)(iVar28 + 0xb3) = (char)param_9[0x21a];
    *(undefined1 *)(iVar28 + 0xb4) = *(undefined1 *)((int)param_9 + 0x435);
    *(char *)(iVar28 + 0xb5) = (char)param_9[0x16f];
    *(undefined1 *)(iVar28 + 0xb6) = *(undefined1 *)((int)param_9 + 0x2df);
    *(char *)(iVar28 + 0xb7) = (char)param_9[0x171];
    *(undefined1 *)(iVar28 + 0xb8) = *(undefined1 *)((int)param_9 + 0x2e3);
    *(char *)(iVar28 + 0xb9) = (char)param_9[0x172];
    *(undefined1 *)(iVar28 + 0xba) = *(undefined1 *)((int)param_9 + 0x2e5);
    *(undefined1 *)(iVar28 + 0xbb) = *(undefined1 *)((int)param_9 + 0x519);
    *(char *)(iVar28 + 0xbc) = (char)param_9[0x210];
    *(undefined1 *)(iVar28 + 0xbd) = *(undefined1 *)((int)param_9 + 0x421);
    *(char *)(iVar28 + 0xbe) = (char)param_9[0x211];
    *(undefined1 *)(iVar28 + 0xbf) = *(undefined1 *)((int)param_9 + 0x423);
    *(char *)(iVar28 + 0xc0) = (char)param_9[0x212];
    *(undefined1 *)(iVar28 + 0xc1) = *(undefined1 *)((int)param_9 + 0x425);
    *(char *)(iVar28 + 0xc2) = (char)param_9[0x213];
    *(undefined1 *)(iVar28 + 0xc3) = *(undefined1 *)((int)param_9 + 0x427);
    *(char *)(iVar28 + 0xc4) = (char)param_9[0x214];
    *(undefined1 *)(iVar28 + 0xc5) = *(undefined1 *)((int)param_9 + 0x429);
    *(char *)(iVar28 + 0xc6) = (char)param_9[0x215];
    *(undefined1 *)(iVar28 + 199) = *(undefined1 *)((int)param_9 + 0x42b);
    *(char *)(iVar28 + 200) = (char)param_9[0x216];
    *(undefined1 *)(iVar28 + 0xc9) = *(undefined1 *)((int)param_9 + 0x42d);
    *(char *)(iVar28 + 0xca) = (char)param_9[0x217];
    *(undefined1 *)(iVar28 + 0xcb) = *(undefined1 *)((int)param_9 + 0x42f);
    *(char *)(iVar28 + 0xcc) = (char)param_9[0x218];
    *(undefined1 *)(iVar28 + 0xcd) = *(undefined1 *)((int)param_9 + 0x431);
    *(char *)(iVar28 + 0xce) = (char)param_9[0x219];
    *(undefined1 *)(iVar28 + 0xcf) = *(undefined1 *)((int)param_9 + 0x433);
    *(char *)(iVar28 + 0xd0) = (char)param_9[0x174];
    *(undefined1 *)(iVar28 + 0xd1) = *(undefined1 *)((int)param_9 + 0x2e9);
    *(char *)(iVar28 + 0xd2) = (char)param_9[0x175];
    *(undefined1 *)(iVar28 + 0xd3) = *(undefined1 *)((int)param_9 + 0x2eb);
    *(char *)(iVar28 + 0xd4) = (char)param_9[0x176];
    *(undefined1 *)(iVar28 + 0xd5) = *(undefined1 *)((int)param_9 + 0x2ed);
    *(char *)(iVar28 + 0xd6) = (char)param_9[0x177];
    *(undefined1 *)(iVar28 + 0xd7) = *(undefined1 *)((int)param_9 + 0x2ef);
    *(char *)(iVar28 + 0xd8) = (char)param_9[0x178];
    *(undefined1 *)(iVar28 + 0xd9) = *(undefined1 *)((int)param_9 + 0x2f1);
    *(char *)(iVar28 + 0xda) = (char)param_9[0x179];
    *(undefined1 *)(iVar28 + 0xdb) = *(undefined1 *)((int)param_9 + 0x2f3);
    *(char *)(iVar28 + 0xdc) = (char)param_9[0x15a];
    *(undefined1 *)(iVar28 + 0xdd) = *(undefined1 *)((int)param_9 + 0x2b5);
    *(char *)(iVar28 + 0xde) = (char)param_9[0x15b];
    *(undefined1 *)(iVar28 + 0xdf) = *(undefined1 *)((int)param_9 + 0x2b7);
    *(char *)(iVar28 + 0xe0) = (char)param_9[0x15c];
    *(undefined1 *)(iVar28 + 0xe1) = *(undefined1 *)((int)param_9 + 0x2b9);
    *(char *)(iVar28 + 0xe2) = (char)param_9[0x17a];
    *(undefined1 *)(iVar28 + 0xe3) = *(undefined1 *)((int)param_9 + 0x2f5);
    *(char *)(iVar28 + 0xe4) = (char)param_9[0x17b];
    *(undefined1 *)(iVar28 + 0xe5) = *(undefined1 *)((int)param_9 + 0x2f7);
    *(char *)(iVar28 + 0xe6) = (char)param_9[0x17c];
    *(undefined1 *)(iVar28 + 0xe7) = *(undefined1 *)((int)param_9 + 0x2f9);
    *(char *)(iVar28 + 0xe8) = (char)param_9[0x28b];
    *(undefined1 *)(iVar28 + 0xe9) = *(undefined1 *)((int)param_9 + 0x517);
    *(char *)(iVar28 + 0xea) = (char)param_9[0x169];
    *(undefined1 *)(iVar28 + 0xeb) = *(undefined1 *)((int)param_9 + 0x2d3);
    *(char *)(iVar28 + 0xec) = (char)param_9[0x16a];
    *(undefined1 *)(iVar28 + 0xed) = *(undefined1 *)((int)param_9 + 0x2d5);
    uVar26 = 0;
  }
  *(undefined1 *)(iVar28 + 0xee) = uVar26;
  return;
}


/* 438631c4 */

void FUN_438631c4(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 int param_7,int param_8,short *param_9)

{
  int iVar1;
  short sVar2;
  ushort uVar3;
  byte bVar4;
  byte bVar5;
  short sVar6;
  ushort uVar7;
  short sVar8;
  undefined2 uVar9;
  undefined2 uVar10;
  ushort uVar11;
  int *piVar12;
  int iVar13;
  short *psVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  short sVar18;
  undefined4 uVar19;
  int iVar20;
  uint uVar21;
  short *psVar22;
  int *piVar23;
  ushort *puVar24;
  char cVar25;
  undefined1 uVar26;
  short sVar27;
  int iVar28;
  int iVar29;
  uint uVar30;
  int iVar31;
  uint *puVar32;
  undefined4 uVar33;
  int iVar34;
  uint uVar35;
  int iVar36;
  uint uVar37;
  undefined1 uVar38;
  int iVar39;
  undefined4 *puVar40;
  uint uStack_84;
  int iStack_68;
  int aiStack_64 [14];
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  
  uVar33 = *(undefined4 *)(param_1 + 0x3c0);
  iVar31 = DAT_43863dc8 + 0x438631da;
  uVar19 = *(undefined4 *)(param_1 + 0x3bc);
  *(undefined4 *)(param_9 + 8) = uVar19;
  *(undefined4 *)(param_9 + 10) = uVar33;
  *(undefined1 *)(param_9 + 0x10) = *(undefined1 *)(param_1 + 0x3d6);
  *(undefined1 *)((int)param_9 + 0x21) = *(undefined1 *)(param_6 + 0x42);
  *(undefined1 *)(param_9 + 0x11) = *(undefined1 *)(param_6 + 0x32);
  sVar6 = *(short *)(param_1 + 0x2f0);
  sVar8 = *(short *)(param_1 + 0x11e);
  param_9[0x12] = *(short *)(param_2 + 0x1c6);
  sVar2 = *(short *)(param_2 + 0x54);
  param_9[0x13] = sVar6;
  param_9[0x16] = sVar8;
  param_9[0x17] = sVar2;
  *(undefined1 *)(param_9 + 0x1a) = *(undefined1 *)(param_4 + 2);
  iVar34 = *(int *)(iVar31 + DAT_43863dcc);
  *(undefined1 *)((int)param_9 + 0x35) = *(undefined1 *)(iVar34 + 0x22);
  iVar28 = 0;
  *(undefined1 *)((int)param_9 + 0x37) = 0;
  *(undefined1 *)((int)param_9 + 0x31) = *(undefined1 *)(param_1 + 0x22a);
  *(undefined1 *)(param_9 + 0x1e) = *(undefined1 *)(param_1 + 0x432);
  *(undefined1 *)((int)param_9 + 0x3d) = *(undefined1 *)(param_1 + 0x433);
  piVar12 = *(int **)(iVar31 + DAT_43863dd0);
  *(undefined1 *)(param_9 + 0x1f) = *(undefined1 *)(*piVar12 + 0x286);
  param_9[0x20] = *(short *)(param_2 + 0x1e4);
  *(undefined1 *)(param_9 + 0x232) = *(undefined1 *)(param_1 + 0x657);
  *(undefined1 *)((int)param_9 + 0x465) = *(undefined1 *)(param_1 + 0x658);
  sVar6 = *(short *)(param_7 + 0x4c4);
  param_9[0x235] = *(short *)(param_7 + 0x4c2);
  uVar33 = *(undefined4 *)(param_1 + 0x640);
  param_9[0x236] = sVar6;
  *(undefined4 *)(param_9 + 0x248) = uVar33;
  *(undefined1 *)((int)param_9 + 0x495) = *(undefined1 *)(param_5 + 0xbd9);
  *(undefined1 *)(param_9 + 0x24b) = *(undefined1 *)(param_5 + 0xbd6);
  param_9[0x16b] = *(short *)(param_5 + 0xc6a);
  psVar14 = param_9;
  do {
    iVar13 = param_7 + iVar28;
    iVar28 = iVar28 + 4;
    psVar14[0x237] = *(short *)(iVar13 + 4);
    psVar14 = psVar14 + 1;
  } while (iVar28 != 0x38);
  if ((*(int *)(param_1 + 700) == 0) || (*(int *)(param_1 + 700) == 4)) {
    uVar26 = 0;
  }
  else {
    uVar26 = 1;
  }
  *(undefined1 *)(param_9 + 0x18) = uVar26;
  sVar6 = *(short *)(param_1 + 0x576);
  sVar8 = *(short *)(param_1 + 0x512);
  sVar2 = *(short *)(param_1 + 0x514);
  sVar18 = *(short *)(param_1 + 0x578);
  param_9[0x279] = *(short *)(param_1 + 0x510);
  param_9[0x282] = sVar6;
  sVar6 = *(short *)(param_1 + 0x57a);
  uVar33 = *(undefined4 *)(param_1 + 0x4f8);
  param_9[0x27a] = sVar8;
  param_9[0x27b] = sVar2;
  param_9[0x283] = sVar18;
  param_9[0x284] = sVar6;
  *(char *)(param_9 + 0x285) = (char)uVar33;
  iVar28 = FUN_4382ffe0((char)param_9[0x18],uVar19);
  if (iVar28 == 0) {
    param_9[0x19] = 0;
  }
  else if (*(char *)(param_8 + 1) == '\x01') {
    param_9[0x19] = 1;
  }
  else {
    param_9[0x19] = 0;
  }
  FUN_4386208c(param_9);
  FUN_43b0ad1c(param_9);
  sVar6 = FUN_439027ec((int)param_9[0x13],0x100);
  iVar28 = (int)param_9[0x13];
  param_9[0x14] = sVar6;
  if (iVar28 < 0) {
    cVar25 = -(char)(iVar28 + 0x3f >> 6);
  }
  else {
    cVar25 = (char)(iVar28 >> 6);
  }
  *(char *)(param_9 + 0x15) = cVar25;
  if (0x1f < *(byte *)(param_9 + 0x15)) {
    *(undefined1 *)(param_9 + 0x15) = 0x1f;
  }
  iVar28 = DAT_43863dd4;
  *(undefined1 *)(param_9 + 6) = 1;
  iVar28 = *(int *)(iVar31 + iVar28);
  if ((*(int *)(param_9 + 8) == 0) && (*(char *)(iVar28 + 0x49) == '\0')) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x924) == 1) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((*(char *)(iVar28 + 0x49) == '\x01') && (*(int *)(param_1 + 0x40c) != 0)) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if (*(int *)(param_1 + 0x2b4) == 0x1f) {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  cVar25 = *(char *)(iVar34 + 2);
  if ((cVar25 == '\x01') || (cVar25 == '\x02')) {
    *(char *)(param_9 + 6) = cVar25 + -1;
  }
  if (*(char *)((int)param_9 + 0x21) != '\0') {
    *(undefined1 *)(param_9 + 6) = 0;
  }
  if ((char)param_9[0x11] != '\0') {
    *(undefined1 *)(param_9 + 6) = 1;
  }
  uVar26 = 0;
  if ((char)param_9[6] == '\0') {
LAB_43863652:
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
  }
  else {
    sVar6 = param_9[0x14];
    iVar29 = 0;
    iVar13 = param_3;
    iVar39 = param_3;
    do {
      iVar17 = 0;
      puVar32 = (uint *)(param_9 + iVar29 * 2 + 0x20);
      iVar20 = iVar17;
      do {
        iVar36 = iVar39 + iVar17;
        iVar17 = iVar17 + 0xc;
        iVar1 = iVar20 * 2;
        puVar32 = puVar32 + 1;
        *puVar32 = (uint)(*(int *)(iVar36 + 0x338) * (int)sVar6) >> 8;
        iVar36 = iVar20 + iVar29;
        iVar20 = iVar20 + 1;
        *(undefined1 *)((int)param_9 + iVar36 + 0x1d0) = *(undefined1 *)(iVar13 + iVar1 + 0x964);
      } while (iVar20 != 0xb);
      iVar29 = iVar29 + 0xb;
      iVar13 = iVar13 + 0x16;
      iVar39 = iVar39 + 0x84;
    } while (iVar29 != 99);
    iVar13 = 0;
    psVar14 = param_9;
    do {
      iVar13 = iVar13 + 1;
      uVar21 = 0;
      psVar14[0x11a] = 0;
      psVar14[0x11b] = 0;
      psVar14 = psVar14 + 2;
    } while (iVar13 != 0x20);
    uVar30 = (uint)*(byte *)(param_9 + 0x15);
    iVar13 = 0;
    if (uVar30 == 0) {
      do {
        iVar39 = iVar13 + 4;
        *(undefined4 *)((int)param_9 + iVar13 + 0x234) = *(undefined4 *)(param_7 + iVar13 + 0xa4);
        iVar13 = iVar39;
      } while (iVar39 != 0x80);
    }
    else {
      iVar13 = param_7;
      if (param_9[0x13] < 0) {
        for (; uVar21 <= uVar30; uVar21 = uVar21 + 1) {
          *(int *)(param_9 + 0x11a) = *(int *)(iVar13 + 0xa4) + *(int *)(param_9 + 0x11a);
          iVar13 = iVar13 + 4;
        }
        puVar40 = (undefined4 *)(param_7 + uVar30 * 4 + 0xa4);
        uVar21 = 1;
        psVar14 = param_9;
        while( true ) {
          uVar35 = 0x20 - uVar30;
          if (uVar35 <= uVar21) break;
          puVar40 = puVar40 + 1;
          uVar21 = uVar21 + 1;
          *(undefined4 *)(psVar14 + 0x11c) = *puVar40;
          psVar14 = psVar14 + 2;
        }
        psVar14 = param_9 + uVar35 * 2 + 0x118;
        for (; uVar35 < 0x20; uVar35 = uVar35 + 1) {
          psVar14 = psVar14 + 2;
          psVar14[0] = 0;
          psVar14[1] = 0;
        }
      }
      else {
        uVar21 = 0;
        psVar14 = param_9;
        while( true ) {
          iVar13 = 0;
          uVar35 = uVar30;
          if (uVar30 <= uVar21) break;
          psVar14[0x11a] = 0;
          psVar14[0x11b] = 0;
          uVar21 = uVar21 + 1;
          psVar14 = psVar14 + 2;
        }
        for (; uVar35 < 0x1f; uVar35 = uVar35 + 1) {
          iVar29 = param_7 + iVar13;
          iVar39 = iVar13 + uVar30 * 4;
          iVar13 = iVar13 + 4;
          *(undefined4 *)((int)param_9 + iVar39 + 0x234) = *(undefined4 *)(iVar29 + 0xa4);
        }
        uVar30 = 0x20 - uVar30;
        piVar23 = (int *)(param_7 + uVar30 * 4 + 0xa0);
        for (; uVar30 < 0x20; uVar30 = uVar30 + 1) {
          piVar23 = piVar23 + 1;
          *(int *)(param_9 + 0x158) = *(int *)(param_9 + 0x158) + *piVar23;
        }
      }
    }
    iVar13 = *(int *)(param_7 + 0x4bc);
    if (iVar13 == 0) {
      iVar13 = 0x10000;
    }
    *(int *)(param_9 + 0x15a) = iVar13;
    FUN_43b0abd8(param_9);
    sVar6 = *param_9;
    if (sVar6 == 0) {
      sVar6 = param_9[0x160];
    }
    sVar8 = param_9[1];
    if (sVar8 == 0) {
      sVar8 = param_9[0x161];
    }
    sVar2 = param_9[2];
    if (sVar2 == 0) {
      sVar2 = param_9[0x162];
    }
    sVar18 = param_9[3];
    if (sVar18 == 0) {
      sVar18 = param_9[0x161];
    }
    uVar7 = param_9[4];
    if ((ushort)param_9[5] < (ushort)param_9[4]) {
      uVar7 = param_9[5];
    }
    param_9[0x168] = uVar7;
    sVar27 = param_9[0x13] * 4;
    param_9[0x167] = sVar18 + sVar27;
    param_9[0x164] = sVar6 + sVar27;
    param_9[0x165] = sVar8 + sVar27;
    param_9[0x166] = sVar2 + sVar27;
    if ((param_9[0x19] == 0) || (*(char *)(param_3 + 0xc35) == '\0')) {
      param_9[0x16c] = 0;
      param_9[0x169] = 0;
      param_9[0x16a] = 0;
    }
    else {
      uVar7 = FUN_4355faf0(*(undefined4 *)(param_8 + 4));
      param_9[0x169] = uVar7;
      if (0x3ff < uVar7) {
        param_9[0x169] = 0x3ff;
      }
      sVar6 = FUN_438625d0(((ushort)param_9[0x169] & 0x3fff) << 2);
      param_9[0x16a] = sVar6 + param_9[0x13] * 4;
      sVar6 = FUN_438625d0(((ushort)param_9[0x16b] & 0x3fff) << 2);
      param_9[0x16c] = sVar6;
    }
    if (param_9[0x19] == 0) {
      if (((char)param_9[0x10] == '\x01') && (*(char *)(iVar28 + 0x49) == '\x01')) {
        uVar26 = 7;
      }
      else {
        uVar26 = 1;
      }
    }
    else {
      uVar26 = 5;
    }
    *(undefined1 *)(param_9 + 0x15e) = uVar26;
    if ((((char)param_9[0x1f] != '\0') && (*(char *)(iVar28 + 0x49) == '\x01')) &&
       ((char)param_9[0x10] == '\x01')) {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if ((char)param_9[0x11] != '\0') {
      *(undefined1 *)(param_9 + 0x15e) = 7;
    }
    if (*(char *)((int)param_9 + 0x35) != '\0') {
      uVar26 = 8;
      goto LAB_43863652;
    }
  }
  if ((char)param_9[6] == '\0') goto LAB_43863fe2;
  if (*(char *)(param_1 + 0xc) == '\x04') {
    FUN_439c5320(param_9 + 0x187,param_9 + 0x19b,0x14);
    FUN_439c5320(param_9 + 0x191,param_9 + 0x1a5,0x14);
    goto LAB_43863fe2;
  }
  FUN_43861ed0(param_9);
  FUN_43865254(param_9);
  if (((char)param_9[0x1f] == '\0') || ((char)param_9[0x10] != '\x01')) {
    iVar13 = *(int *)(param_9 + 8);
    if (((iVar13 == 1) || (iVar13 == 8)) || ((iVar13 == 0 && (*(char *)(iVar28 + 0x49) == '\x01'))))
    {
      FUN_438621bc(param_9);
    }
    FUN_43b0acee(param_9);
    FUN_43b0ad9a(param_9);
    FUN_43b0ace4(param_9);
    if ((char)param_9[0x11] == '\0') {
      if (*(char *)((int)param_9 + 0x31) == '\0') {
        bVar4 = *(byte *)(iVar34 + 0xcb);
      }
      else {
        bVar4 = *(byte *)(iVar34 + 0xcc);
      }
      uVar11 = (ushort)bVar4 * 2;
      uVar7 = param_9[0x21c];
      if (param_9[0x19] == 0) {
        uVar26 = 0;
        if (uVar7 != 0) {
          param_9[0x21c] = uVar7 - 1;
          goto LAB_438636fa;
        }
LAB_438636fc:
        *(undefined1 *)(param_9 + 0x21d) = uVar26;
      }
      else {
        if (uVar11 <= uVar7) {
LAB_438636fa:
          uVar26 = 1;
          goto LAB_438636fc;
        }
        if ((char)param_9[0x21d] == '\0') {
          uVar3 = (ushort)*(byte *)(iVar34 + 0xcd);
        }
        else {
          uVar3 = 1;
        }
        param_9[0x21c] = uVar7 + uVar3;
      }
      if (uVar11 < (ushort)param_9[0x21c]) {
        param_9[0x21c] = uVar11;
      }
      if ((char)param_9[0x21d] == '\0') {
        if (*(char *)(iVar34 + 0xca) == '\0') goto LAB_4386372a;
        uVar26 = *(undefined1 *)(iVar34 + 0xce);
      }
      else if (*(char *)(iVar34 + 0xca) == '\0') {
LAB_4386372a:
        uVar26 = *(undefined1 *)(iVar34 + 0xd0);
      }
      else {
        uVar26 = *(undefined1 *)(iVar34 + 0xcf);
      }
      param_9[0x187] = 0;
      param_9[0x191] = 0;
      param_9[0x1e8] = 0;
      param_9[0x1e9] = 0;
      param_9[0x1fc] = 0;
      param_9[0x1fd] = 0;
      param_9[400] = 0x3400;
      param_9[0x19a] = 0x3400;
      param_9[0x1fa] = 0x3400;
      param_9[0x1fb] = 0;
      param_9[0x20e] = 0x3400;
      param_9[0x20f] = 0;
      if (*(char *)(iVar34 + 0x55) == '\0') {
        if ((char)param_9[0x24a] == '\0') {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar26 = 0;
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,0,0,0);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,0,0,0);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
        else {
          iVar28 = 1;
          psVar14 = param_9;
          do {
            uVar38 = *(undefined1 *)(DAT_43863dd8 + 0x438637d2);
            sVar6 = FUN_43b0ac28(psVar14[0x188],param_9 + iVar28 * 2 + 0x1e8,uVar26,uVar26,uVar38);
            iVar13 = iVar28 * 2;
            iVar28 = iVar28 + 1;
            psVar14[0x188] = sVar6;
            sVar6 = FUN_43b0ac28(psVar14[0x192],param_9 + iVar13 + 0x1fc,uVar26,uVar26,uVar38);
            psVar14[0x192] = sVar6;
            psVar14 = psVar14 + 1;
          } while (iVar28 != 9);
        }
      }
      *(undefined1 *)(param_9 + 0x24a) = 1;
      *(undefined1 *)(DAT_43863ddc + 0x43863822) = uVar26;
      psVar14 = param_9;
      iVar28 = 0;
      do {
        iVar13 = iVar28;
        uVar30 = (uint)(ushort)psVar14[0x187];
        uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
        uVar21 = (uint)(ushort)psVar14[0x191];
        uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
        iVar28 = 0;
        psVar22 = param_9 + iVar13 + 0x1ae;
        do {
          iVar28 = iVar28 + 1;
          psVar22[1] = (short)uVar30;
          psVar22[0x1d] = (short)uVar21;
          uVar30 = uVar30 + uVar7 & 0xffff;
          uVar21 = uVar21 + uVar11 & 0xffff;
          psVar22 = psVar22 + 1;
        } while (iVar28 != 3);
        psVar14 = psVar14 + 1;
        iVar28 = iVar13 + 3;
      } while (iVar13 + 3 != 0x18);
      iVar13 = iVar13 + -0x14;
      psVar14 = param_9;
      do {
        uVar7 = psVar14[0x1cd];
        iVar13 = iVar13 + 1;
        sVar6 = FUN_43b07560(((uint)(ushort)psVar14[0x1b2] - (uint)(ushort)psVar14[0x1b1]) *
                             ((uint)(ushort)psVar14[0x1cf] - (uint)uVar7),
                             (uint)(ushort)psVar14[0x1b3] - (uint)(ushort)psVar14[0x1b1]);
        psVar14[0x1ce] = sVar6 + uVar7;
        psVar14 = psVar14 + 3;
      } while (iVar13 != 8);
      uVar7 = param_9[399];
      param_9[0x1af] = param_9[0x187];
      uVar11 = param_9[0x19a];
      uVar3 = param_9[0x199];
      param_9[0x1c7] = uVar7;
      param_9[0x1e3] = uVar3;
      param_9[0x1ca] = param_9[400];
      param_9[0x1cb] = param_9[0x191];
      param_9[0x1e6] = uVar11;
      sVar6 = FUN_4355fd68((uint)(ushort)param_9[400] - (uint)uVar7,3);
      sVar8 = FUN_4355fd68((uint)uVar11 - (uint)uVar3,3);
      param_9[0x1c8] = sVar6 + uVar7;
      param_9[0x1c9] = uVar7 + sVar6 * 2;
      param_9[0x1e4] = sVar8 + uVar3;
      param_9[0x1e5] = uVar3 + sVar8 * 2;
      if ((char)param_9[0x18] == '\x01') {
        piVar23 = *(int **)(iVar31 + DAT_43863dd0);
        iVar28 = *piVar23;
        if (*(char *)(iVar28 + 0x229) != '\0') {
          uVar21 = *(byte *)(param_5 + 0xbd9) - 0x14 & 0xff;
          if (uVar21 < 4) {
            uVar33 = *(undefined4 *)(DAT_43863de0 + 0x4386395e + uVar21 * 4);
          }
          else {
            uVar33 = 0;
          }
          if (*(char *)(iVar28 + 0x22b) == '\x01') {
            switch(uVar33) {
            case 1:
              uVar30 = (uint)*(byte *)(iVar28 + 0x275);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x276) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x277));
              break;
            case 2:
              uVar30 = (uint)*(byte *)(iVar28 + 0x278);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x279) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27a));
              break;
            case 3:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27b);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27c) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x27d));
              break;
            case 4:
              uVar30 = (uint)*(byte *)(iVar28 + 0x27e);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x27f) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x280));
              break;
            default:
              uVar30 = (uint)*(byte *)(iVar28 + 0x272);
              uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x273) * 0x100 +
                                     (ushort)*(byte *)(iVar28 + 0x274));
            }
            uVar30 = uVar30 * 0x10 + 0x2000;
          }
          else if (*(char *)(iVar28 + 0x22b) == '\x02') {
            switch(uVar33) {
            case 1:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x23e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x23f);
              uVar26 = *(undefined1 *)(iVar28 + 0x23d);
              uVar38 = *(undefined1 *)(iVar28 + 0x23c);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x240),
                                      *(undefined1 *)(iVar28 + 0x241));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x242) * 0x100 + (ushort)*(byte *)(iVar28 + 0x243);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x23b);
              uVar21 = (uint)*(byte *)(iVar28 + 0x23a);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x244),
                                      *(undefined1 *)(iVar28 + 0x245));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x246),
                                      *(undefined1 *)(iVar28 + 0x247));
              break;
            case 2:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x24c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x24d);
              uVar26 = *(undefined1 *)(iVar28 + 0x24b);
              uVar38 = *(undefined1 *)(iVar28 + 0x24a);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x24e),
                                      *(undefined1 *)(iVar28 + 0x24f));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x250) * 0x100 + (ushort)*(byte *)(iVar28 + 0x251);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x249);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x252),
                                      *(undefined1 *)(iVar28 + 0x253));
              uVar21 = (uint)*(byte *)(iVar28 + 0x248);
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x254),
                                      *(undefined1 *)(iVar28 + 0x255));
              break;
            case 3:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x25a) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25b);
              uStack_84 = (uint)*(byte *)(iVar28 + 599);
              uVar26 = *(undefined1 *)(iVar28 + 0x259);
              uVar38 = *(undefined1 *)(iVar28 + 600);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x25c),
                                      *(undefined1 *)(iVar28 + 0x25d));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x25e) * 0x100 + (ushort)*(byte *)(iVar28 + 0x25f);
              uVar21 = (uint)*(byte *)(iVar28 + 0x256);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x260),
                                      *(undefined1 *)(iVar28 + 0x261));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x262),
                                      *(undefined1 *)(iVar28 + 0x263));
              break;
            case 4:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x268) * 0x100 + (ushort)*(byte *)(iVar28 + 0x269);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x265);
              uVar26 = *(undefined1 *)(iVar28 + 0x267);
              uVar38 = *(undefined1 *)(iVar28 + 0x266);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26a),
                                      *(undefined1 *)(iVar28 + 0x26b));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x26c) * 0x100 + (ushort)*(byte *)(iVar28 + 0x26d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x264);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x26e),
                                      *(undefined1 *)(iVar28 + 0x26f));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x270),
                                      *(undefined1 *)(iVar28 + 0x271));
              break;
            default:
              sVar6 = (ushort)*(byte *)(iVar28 + 0x230) * 0x100 + (ushort)*(byte *)(iVar28 + 0x231);
              uVar26 = *(undefined1 *)(iVar28 + 0x22f);
              uVar38 = *(undefined1 *)(iVar28 + 0x22e);
              uVar30 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x232),
                                      *(undefined1 *)(iVar28 + 0x233));
              sVar8 = (ushort)*(byte *)(iVar28 + 0x234) * 0x100 + (ushort)*(byte *)(iVar28 + 0x235);
              uStack_84 = (uint)*(byte *)(iVar28 + 0x22d);
              uVar21 = (uint)*(byte *)(iVar28 + 0x22c);
              uVar37 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x236),
                                      *(undefined1 *)(iVar28 + 0x237));
              uVar35 = (uint)CONCAT11(*(undefined1 *)(iVar28 + 0x238),
                                      *(undefined1 *)(iVar28 + 0x239));
            }
            iVar28 = (uVar35 - uVar30) * 0x400;
            uVar7 = FUN_43b07560(iVar28,uVar37 - uVar30);
            if (uVar7 < 0x401) {
              uVar9 = FUN_43b07560(iVar28,uVar37 - uVar30);
            }
            else {
              uVar9 = 0x400;
            }
            uVar15 = FUN_43b0af46(uVar38,0,0x1f);
            uVar16 = FUN_43b0af46(uVar26,0,0x1f);
            iVar28 = 0;
            for (; uVar15 < uVar16; uVar15 = uVar15 + 1 & 0xff) {
              iVar28 = iVar28 + (uint)*(byte *)(param_7 + uVar15 + 0x3f0);
            }
            uVar15 = 0;
            for (; uVar16 < 0x20; uVar16 = uVar16 + 1 & 0xff) {
              uVar15 = uVar15 + *(byte *)(param_7 + uVar16 + 0x3f0) & 0xffff;
            }
            iVar13 = *(int *)(iVar31 + DAT_43863de4);
            *(short *)(iVar13 + 0x59e) = (short)iVar28;
            *(short *)(iVar13 + 0x5a0) = (short)uVar15;
            uVar33 = FUN_43b084e8(iVar28 * uVar21 * 0x80,uVar15 + iVar28);
            bVar4 = FUN_43b0af60(uVar33,0,0x80);
            bVar5 = FUN_43b0af60((int)(uStack_84 * (uVar15 + iVar28)) >> 7,0,0x80);
            uVar21 = 0x4000 - (uint)bVar4 * (uint)bVar5;
            uVar21 = uVar21 & ~((int)uVar21 >> 0x1f);
            uVar10 = FUN_43b0aee8(uVar21,0,0x4000,uVar30,sVar8);
            *(byte *)(iVar13 + 0x5a3) = bVar5;
            *(byte *)(iVar13 + 0x5a2) = bVar4;
            *(uint *)(iVar13 + 0x5a8) = uVar21;
            *(short *)(iVar13 + 0x5a4) = (short)((uint)bVar4 * (uint)bVar5);
            uVar30 = FUN_43862554(uVar10,param_9 + 0x286);
            uVar7 = FUN_43b084e8((uVar35 - uVar30) * 0x400,uVar37 - uVar30);
            *(short *)(iVar13 + 0x596) = (short)uVar35;
            *(short *)(iVar13 + 0x598) = (short)uVar37;
            if (0x3ff < uVar7) {
              uVar7 = 0x400;
            }
            *(ushort *)(iVar13 + 0x594) = uVar7;
            uVar21 = FUN_43b0af2c(uVar7,sVar6,uVar9);
            *(short *)(iVar13 + 0x59a) = sVar6;
            *(undefined2 *)(iVar13 + 0x59c) = uVar9;
          }
          else {
            uVar21 = 0x400;
            uVar30 = 0;
          }
          iVar28 = *piVar23;
          if ((*(byte *)(iVar28 + 0x281) & 2) != 0) {
            uVar30 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x284) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x285));
          }
          if ((*(byte *)(iVar28 + 0x281) & 1) != 0) {
            uVar21 = (uint)(ushort)((ushort)*(byte *)(iVar28 + 0x282) * 0x100 +
                                   (ushort)*(byte *)(iVar28 + 0x283));
          }
          iVar28 = *(int *)(iVar31 + DAT_43863de4);
          *(short *)(iVar28 + 0x590) = (short)uVar30;
          *(short *)(iVar28 + 0x592) = (short)uVar21;
          puVar24 = (ushort *)(param_9 + 0x1cb);
          uVar35 = 0;
          do {
            uVar37 = uVar35;
            if (uVar30 < *puVar24) {
              uVar37 = uVar37 & 0xff;
              goto LAB_43863dbc;
            }
            puVar24 = puVar24 + 1;
            uVar35 = uVar37 + 1;
          } while (uVar37 + 1 != 0x1c);
          uVar37 = uVar37 - 0x1b;
LAB_43863dbc:
          puVar24 = (ushort *)(param_9 + uVar37 + 0x1cb);
          while ((int)uVar37 < 0x1c) {
            uVar7 = *puVar24;
            uVar37 = uVar37 + 1;
            uVar35 = (uVar7 - uVar30) * uVar21 + uVar30 * 0x400 >> 10;
            if ((uVar35 & 0xffff) < (uint)uVar7) {
              uVar7 = (ushort)uVar35;
            }
            *puVar24 = uVar7;
            puVar24 = puVar24 + 1;
          }
        }
      }
    }
    FUN_43b0ad9a(param_9);
    FUN_439c5320(param_9 + 0x19b,param_9 + 0x187,0x14);
    FUN_439c5320(param_9 + 0x1a5,param_9 + 0x191,0x14);
  }
  else {
    FUN_4386261c(param_9);
  }
  if ((char)param_9[0x18] != '\0') {
    if (*(char *)((int)param_9 + 0x3f) == '\x01') {
      iVar28 = 0;
      do {
        *(undefined4 *)((int)aiStack_64 + iVar28) = 0x20;
        iVar28 = iVar28 + 4;
      } while (iVar28 != 0x38);
    }
    else {
      if ((byte)(*(char *)((int)param_9 + 0x495) - 0x14U) < 2) {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x340);
        uStack_2b = *(undefined1 *)(iVar28 + 0x341);
        uStack_2a = *(undefined1 *)(iVar28 + 0x342);
        uStack_29 = *(undefined1 *)(iVar28 + 0x343);
        uVar26 = *(undefined1 *)(iVar28 + 0x344);
        uVar38 = *(undefined1 *)(iVar28 + 0x345);
      }
      else {
        iVar28 = *piVar12;
        uStack_2c = *(undefined1 *)(iVar28 + 0x33a);
        uStack_2b = *(undefined1 *)(iVar28 + 0x33b);
        uStack_2a = *(undefined1 *)(iVar28 + 0x33c);
        uStack_29 = *(undefined1 *)(iVar28 + 0x33d);
        uVar26 = *(undefined1 *)(iVar28 + 0x33e);
        uVar38 = *(undefined1 *)(iVar28 + 0x33f);
      }
      FUN_43b0af7a(&uStack_2c,uVar26,uVar38,aiStack_64);
    }
    piVar12 = &iStack_68;
    iVar28 = 0;
    psVar14 = param_9;
    do {
      piVar12 = piVar12 + 1;
      iVar31 = FUN_43b075da(*piVar12 << 8,*(undefined4 *)(psVar14 + 0x256),4);
      iVar13 = iVar28 + 1;
      *(int *)(psVar14 + 0x256) = iVar31;
      psVar14 = psVar14 + 2;
      *(char *)((int)param_9 + iVar28 + 0x4e4) = (char)((uint)(iVar31 + 0x80) >> 8);
      iVar28 = iVar13;
    } while (iVar13 != 0xe);
  }
  if ((char)param_9[0x11] != '\0') {
    param_9[0x196] = 0x3400;
    param_9[0x197] = 0x3400;
    param_9[0x198] = 0x3400;
    param_9[0x199] = 0x3400;
    param_9[0x19a] = 0x3400;
    sVar6 = *(short *)(iVar34 + 0x38);
    iVar28 = 0;
    param_9[0x191] = 0;
    param_9[0x192] = 0;
    param_9[0x193] = 0;
    param_9[0x194] = 0;
    param_9[0x195] = 0;
    param_9[0x187] = 0;
    param_9[0x189] = sVar6;
    param_9[0x18a] = sVar6;
    param_9[0x18b] = sVar6;
    param_9[0x18c] = sVar6;
    param_9[0x18d] = sVar6;
    param_9[0x18e] = sVar6;
    param_9[0x188] = sVar6 + -0x80;
    param_9[399] = sVar6 + 0x80;
    param_9[400] = 0x3400;
    psVar14 = param_9;
    do {
      uVar30 = (uint)(ushort)psVar14[0x187];
      uVar7 = FUN_4355fd68((ushort)psVar14[0x188] - uVar30,3);
      uVar21 = (uint)(ushort)psVar14[0x191];
      uVar11 = FUN_4355fd68((ushort)psVar14[0x192] - uVar21,3);
      iVar31 = 0;
      psVar22 = param_9 + iVar28 + 0x1ae;
      do {
        iVar31 = iVar31 + 1;
        psVar22[1] = (short)uVar30;
        psVar22[0x1d] = (short)uVar21;
        uVar30 = uVar30 + uVar7 & 0xffff;
        uVar21 = uVar21 + uVar11 & 0xffff;
        psVar22 = psVar22 + 1;
      } while (iVar31 != 3);
      iVar28 = iVar28 + 3;
      psVar14 = psVar14 + 1;
    } while (iVar28 != 0x1b);
    param_9[0x1ca] = 0x3400;
    param_9[0x1e6] = 0x3400;
  }
LAB_43863fe2:
  iVar28 = FUN_43859ab8();
  sVar6 = param_9[6];
  *(char *)(iVar28 + 0x7a) = (char)sVar6;
  if ((char)sVar6 == '\0') {
    *(undefined1 *)(iVar28 + 0x7b) = 0;
    uVar26 = 0xff;
    *(undefined1 *)(iVar28 + 0x7c) = 0xff;
    *(undefined1 *)(iVar28 + 0x7d) = 0xff;
    *(undefined1 *)(iVar28 + 0x7e) = 0xff;
    *(undefined1 *)(iVar28 + 0x7f) = 0xff;
    *(undefined1 *)(iVar28 + 0x80) = 0xff;
    *(undefined1 *)(iVar28 + 0x81) = 0xff;
    *(undefined1 *)(iVar28 + 0x82) = 0xff;
    *(undefined1 *)(iVar28 + 0x83) = 0xff;
    *(undefined1 *)(iVar28 + 0x84) = 0xff;
    *(undefined1 *)(iVar28 + 0x85) = 0xff;
    *(undefined1 *)(iVar28 + 0x86) = 0xff;
    *(undefined1 *)(iVar28 + 0x87) = 0xff;
    *(undefined1 *)(iVar28 + 0x88) = 0xff;
    *(undefined1 *)(iVar28 + 0x89) = 0xff;
    *(undefined1 *)(iVar28 + 0x8a) = 0xff;
    *(undefined1 *)(iVar28 + 0x8b) = 0xff;
    *(undefined1 *)(iVar28 + 0x8c) = 0xff;
    *(undefined1 *)(iVar28 + 0x8d) = 0xff;
    *(undefined1 *)(iVar28 + 0x8e) = 0xff;
    *(undefined1 *)(iVar28 + 0x8f) = 0xff;
    *(undefined1 *)(iVar28 + 0x90) = 0xff;
    *(undefined1 *)(iVar28 + 0x91) = 0xff;
    *(undefined1 *)(iVar28 + 0x92) = 0xff;
    *(undefined1 *)(iVar28 + 0x93) = 0xff;
    *(undefined1 *)(iVar28 + 0x94) = 0xff;
    *(undefined1 *)(iVar28 + 0x95) = 0xff;
    *(undefined1 *)(iVar28 + 0x96) = 0xff;
    *(undefined1 *)(iVar28 + 0x97) = 0xff;
    *(undefined1 *)(iVar28 + 0x98) = 0xff;
    *(undefined1 *)(iVar28 + 0x99) = 0xff;
    *(undefined1 *)(iVar28 + 0x9a) = 0xff;
    *(undefined1 *)(iVar28 + 0x9b) = 0xff;
    *(undefined1 *)(iVar28 + 0x9c) = 0xff;
    *(undefined1 *)(iVar28 + 0x9d) = 0xff;
    *(undefined1 *)(iVar28 + 0x9e) = 0xff;
    *(undefined1 *)(iVar28 + 0x9f) = 0xff;
    *(undefined1 *)(iVar28 + 0xa0) = 0xff;
    *(undefined1 *)(iVar28 + 0xa1) = 0xff;
    *(undefined1 *)(iVar28 + 0xa2) = 0xff;
    *(undefined1 *)(iVar28 + 0xa3) = 0xff;
    *(undefined1 *)(iVar28 + 0xa4) = 0xff;
    *(undefined1 *)(iVar28 + 0xa5) = 0xff;
    *(undefined1 *)(iVar28 + 0xa6) = 0xff;
    *(undefined1 *)(iVar28 + 0xa7) = 0xff;
    *(undefined1 *)(iVar28 + 0xa8) = 0xff;
    *(undefined1 *)(iVar28 + 0xa9) = 0xff;
    *(undefined1 *)(iVar28 + 0xaa) = 0xff;
    *(undefined1 *)(iVar28 + 0xab) = 0xff;
    *(undefined1 *)(iVar28 + 0xac) = 0xff;
    *(undefined1 *)(iVar28 + 0xad) = 0xff;
    *(undefined1 *)(iVar28 + 0xae) = 0xff;
    *(undefined1 *)(iVar28 + 0xaf) = 0xff;
    *(undefined1 *)(iVar28 + 0xb0) = 0xff;
    *(undefined1 *)(iVar28 + 0xb1) = 0xff;
    *(undefined1 *)(iVar28 + 0xb2) = 0xff;
    *(undefined1 *)(iVar28 + 0xb3) = 0xff;
    *(undefined1 *)(iVar28 + 0xb4) = 0xff;
    *(undefined1 *)(iVar28 + 0xb5) = 0xff;
    *(undefined1 *)(iVar28 + 0xb6) = 0xff;
    *(undefined1 *)(iVar28 + 0xb7) = 0xff;
    *(undefined1 *)(iVar28 + 0xb8) = 0xff;
    *(undefined1 *)(iVar28 + 0xb9) = 0xff;
    *(undefined1 *)(iVar28 + 0xba) = 0xff;
    *(undefined1 *)(iVar28 + 0xbb) = 0xff;
    *(undefined1 *)(iVar28 + 0xbc) = 0xff;
    *(undefined1 *)(iVar28 + 0xbd) = 0xff;
    *(undefined1 *)(iVar28 + 0xbe) = 0xff;
    *(undefined1 *)(iVar28 + 0xbf) = 0xff;
    *(undefined1 *)(iVar28 + 0xc0) = 0xff;
    *(undefined1 *)(iVar28 + 0xc1) = 0xff;
    *(undefined1 *)(iVar28 + 0xc2) = 0xff;
    *(undefined1 *)(iVar28 + 0xc3) = 0xff;
    *(undefined1 *)(iVar28 + 0xc4) = 0xff;
    *(undefined1 *)(iVar28 + 0xc5) = 0xff;
    *(undefined1 *)(iVar28 + 0xc6) = 0xff;
    *(undefined1 *)(iVar28 + 199) = 0xff;
    *(undefined1 *)(iVar28 + 200) = 0xff;
    *(undefined1 *)(iVar28 + 0xc9) = 0xff;
    *(undefined1 *)(iVar28 + 0xca) = 0xff;
    *(undefined1 *)(iVar28 + 0xcb) = 0xff;
    *(undefined1 *)(iVar28 + 0xcc) = 0xff;
    *(undefined1 *)(iVar28 + 0xcd) = 0xff;
    *(undefined1 *)(iVar28 + 0xce) = 0xff;
    *(undefined1 *)(iVar28 + 0xcf) = 0xff;
    *(undefined1 *)(iVar28 + 0xd0) = 0xff;
    *(undefined1 *)(iVar28 + 0xd1) = 0xff;
    *(undefined1 *)(iVar28 + 0xd2) = 0xff;
    *(undefined1 *)(iVar28 + 0xd3) = 0xff;
    *(undefined1 *)(iVar28 + 0xd4) = 0xff;
    *(undefined1 *)(iVar28 + 0xd5) = 0xff;
    *(undefined1 *)(iVar28 + 0xd6) = 0xff;
    *(undefined1 *)(iVar28 + 0xd7) = 0xff;
    *(undefined1 *)(iVar28 + 0xd8) = 0xff;
    *(undefined1 *)(iVar28 + 0xd9) = 0xff;
    *(undefined1 *)(iVar28 + 0xda) = 0xff;
    *(undefined1 *)(iVar28 + 0xdb) = 0xff;
    *(undefined1 *)(iVar28 + 0xdc) = 0xff;
    *(undefined1 *)(iVar28 + 0xdd) = 0xff;
    *(undefined1 *)(iVar28 + 0xde) = 0xff;
    *(undefined1 *)(iVar28 + 0xdf) = 0xff;
    *(undefined1 *)(iVar28 + 0xe0) = 0xff;
    *(undefined1 *)(iVar28 + 0xe1) = 0xff;
    *(undefined1 *)(iVar28 + 0xe2) = 0xff;
    *(undefined1 *)(iVar28 + 0xe3) = 0xff;
    *(undefined1 *)(iVar28 + 0xe4) = 0xff;
    *(undefined1 *)(iVar28 + 0xe5) = 0xff;
    *(undefined1 *)(iVar28 + 0xe6) = 0xff;
    *(undefined1 *)(iVar28 + 0xe7) = 0xff;
    *(undefined1 *)(iVar28 + 0xe8) = 0xff;
    *(undefined1 *)(iVar28 + 0xe9) = 0xff;
    *(undefined1 *)(iVar28 + 0xea) = 0xff;
    *(undefined1 *)(iVar28 + 0xeb) = 0xff;
    *(undefined1 *)(iVar28 + 0xec) = 0xff;
    *(undefined1 *)(iVar28 + 0xed) = 0xff;
  }
  else {
    *(undefined1 *)(iVar28 + 0x7b) = *(undefined1 *)((int)param_9 + 0xd);
    *(char *)(iVar28 + 0x7c) = (char)param_9[7];
    *(undefined1 *)(iVar28 + 0x7d) = *(undefined1 *)((int)param_9 + 0x21);
    *(char *)(iVar28 + 0x7e) = (char)param_9[0x11];
    *(char *)(iVar28 + 0x7f) = (char)param_9[0x13];
    *(undefined1 *)(iVar28 + 0x80) = *(undefined1 *)((int)param_9 + 0x27);
    *(char *)(iVar28 + 0x81) = (char)param_9[0x16];
    *(undefined1 *)(iVar28 + 0x82) = *(undefined1 *)((int)param_9 + 0x2d);
    *(char *)(iVar28 + 0x83) = (char)param_9[0x17];
    *(undefined1 *)(iVar28 + 0x84) = *(undefined1 *)((int)param_9 + 0x2f);
    *(char *)(iVar28 + 0x85) = (char)param_9[0x18];
    *(char *)(iVar28 + 0x86) = (char)param_9[0x19];
    *(undefined1 *)(iVar28 + 0x87) = *(undefined1 *)((int)param_9 + 0x33);
    *(char *)(iVar28 + 0x88) = (char)param_9[0x1a];
    *(undefined1 *)(iVar28 + 0x89) = *(undefined1 *)((int)param_9 + 0x35);
    *(char *)(iVar28 + 0x8a) = (char)param_9[0x232];
    *(undefined1 *)(iVar28 + 0x8b) = *(undefined1 *)((int)param_9 + 0x465);
    *(char *)(iVar28 + 0x8c) = (char)param_9[0x15e];
    *(char *)(iVar28 + 0x8d) = (char)param_9[0x164];
    *(undefined1 *)(iVar28 + 0x8e) = *(undefined1 *)((int)param_9 + 0x2c9);
    *(char *)(iVar28 + 0x8f) = (char)param_9[0x165];
    *(undefined1 *)(iVar28 + 0x90) = *(undefined1 *)((int)param_9 + 0x2cb);
    *(char *)(iVar28 + 0x91) = (char)param_9[0x166];
    *(undefined1 *)(iVar28 + 0x92) = *(undefined1 *)((int)param_9 + 0x2cd);
    *(char *)(iVar28 + 0x93) = (char)param_9[0x167];
    *(undefined1 *)(iVar28 + 0x94) = *(undefined1 *)((int)param_9 + 0x2cf);
    *(char *)(iVar28 + 0x95) = (char)param_9[0x168];
    *(undefined1 *)(iVar28 + 0x96) = *(undefined1 *)((int)param_9 + 0x2d1);
    *(char *)(iVar28 + 0x97) = (char)param_9[0x18a];
    *(undefined1 *)(iVar28 + 0x98) = *(undefined1 *)((int)param_9 + 0x315);
    *(char *)(iVar28 + 0x99) = (char)param_9[0x18b];
    *(undefined1 *)(iVar28 + 0x9a) = *(undefined1 *)((int)param_9 + 0x317);
    *(char *)(iVar28 + 0x9b) = (char)param_9[0x18c];
    *(undefined1 *)(iVar28 + 0x9c) = *(undefined1 *)((int)param_9 + 0x319);
    *(char *)(iVar28 + 0x9d) = (char)param_9[0x18d];
    *(undefined1 *)(iVar28 + 0x9e) = *(undefined1 *)((int)param_9 + 0x31b);
    *(char *)(iVar28 + 0x9f) = (char)param_9[0x18e];
    *(undefined1 *)(iVar28 + 0xa0) = *(undefined1 *)((int)param_9 + 0x31d);
    *(char *)(iVar28 + 0xa1) = (char)param_9[0x194];
    *(undefined1 *)(iVar28 + 0xa2) = *(undefined1 *)((int)param_9 + 0x329);
    *(char *)(iVar28 + 0xa3) = (char)param_9[0x195];
    *(undefined1 *)(iVar28 + 0xa4) = *(undefined1 *)((int)param_9 + 0x32b);
    *(char *)(iVar28 + 0xa5) = (char)param_9[0x196];
    *(undefined1 *)(iVar28 + 0xa6) = *(undefined1 *)((int)param_9 + 0x32d);
    *(char *)(iVar28 + 0xa7) = (char)param_9[0x197];
    *(undefined1 *)(iVar28 + 0xa8) = *(undefined1 *)((int)param_9 + 0x32f);
    *(char *)(iVar28 + 0xa9) = (char)param_9[0x198];
    *(undefined1 *)(iVar28 + 0xaa) = *(undefined1 *)((int)param_9 + 0x331);
    *(char *)(iVar28 + 0xab) = (char)param_9[0x188];
    *(undefined1 *)(iVar28 + 0xac) = *(undefined1 *)((int)param_9 + 0x311);
    *(char *)(iVar28 + 0xad) = (char)param_9[399];
    *(undefined1 *)(iVar28 + 0xae) = *(undefined1 *)((int)param_9 + 799);
    *(char *)(iVar28 + 0xaf) = (char)param_9[0x16d];
    *(undefined1 *)(iVar28 + 0xb0) = *(undefined1 *)((int)param_9 + 0x2db);
    *(char *)(iVar28 + 0xb1) = (char)param_9[0x254];
    *(undefined1 *)(iVar28 + 0xb2) = *(undefined1 *)((int)param_9 + 0x4a9);
    *(char *)(iVar28 + 0xb3) = (char)param_9[0x21a];
    *(undefined1 *)(iVar28 + 0xb4) = *(undefined1 *)((int)param_9 + 0x435);
    *(char *)(iVar28 + 0xb5) = (char)param_9[0x16f];
    *(undefined1 *)(iVar28 + 0xb6) = *(undefined1 *)((int)param_9 + 0x2df);
    *(char *)(iVar28 + 0xb7) = (char)param_9[0x171];
    *(undefined1 *)(iVar28 + 0xb8) = *(undefined1 *)((int)param_9 + 0x2e3);
    *(char *)(iVar28 + 0xb9) = (char)param_9[0x172];
    *(undefined1 *)(iVar28 + 0xba) = *(undefined1 *)((int)param_9 + 0x2e5);
    *(undefined1 *)(iVar28 + 0xbb) = *(undefined1 *)((int)param_9 + 0x519);
    *(char *)(iVar28 + 0xbc) = (char)param_9[0x210];
    *(undefined1 *)(iVar28 + 0xbd) = *(undefined1 *)((int)param_9 + 0x421);
    *(char *)(iVar28 + 0xbe) = (char)param_9[0x211];
    *(undefined1 *)(iVar28 + 0xbf) = *(undefined1 *)((int)param_9 + 0x423);
    *(char *)(iVar28 + 0xc0) = (char)param_9[0x212];
    *(undefined1 *)(iVar28 + 0xc1) = *(undefined1 *)((int)param_9 + 0x425);
    *(char *)(iVar28 + 0xc2) = (char)param_9[0x213];
    *(undefined1 *)(iVar28 + 0xc3) = *(undefined1 *)((int)param_9 + 0x427);
    *(char *)(iVar28 + 0xc4) = (char)param_9[0x214];
    *(undefined1 *)(iVar28 + 0xc5) = *(undefined1 *)((int)param_9 + 0x429);
    *(char *)(iVar28 + 0xc6) = (char)param_9[0x215];
    *(undefined1 *)(iVar28 + 199) = *(undefined1 *)((int)param_9 + 0x42b);
    *(char *)(iVar28 + 200) = (char)param_9[0x216];
    *(undefined1 *)(iVar28 + 0xc9) = *(undefined1 *)((int)param_9 + 0x42d);
    *(char *)(iVar28 + 0xca) = (char)param_9[0x217];
    *(undefined1 *)(iVar28 + 0xcb) = *(undefined1 *)((int)param_9 + 0x42f);
    *(char *)(iVar28 + 0xcc) = (char)param_9[0x218];
    *(undefined1 *)(iVar28 + 0xcd) = *(undefined1 *)((int)param_9 + 0x431);
    *(char *)(iVar28 + 0xce) = (char)param_9[0x219];
    *(undefined1 *)(iVar28 + 0xcf) = *(undefined1 *)((int)param_9 + 0x433);
    *(char *)(iVar28 + 0xd0) = (char)param_9[0x174];
    *(undefined1 *)(iVar28 + 0xd1) = *(undefined1 *)((int)param_9 + 0x2e9);
    *(char *)(iVar28 + 0xd2) = (char)param_9[0x175];
    *(undefined1 *)(iVar28 + 0xd3) = *(undefined1 *)((int)param_9 + 0x2eb);
    *(char *)(iVar28 + 0xd4) = (char)param_9[0x176];
    *(undefined1 *)(iVar28 + 0xd5) = *(undefined1 *)((int)param_9 + 0x2ed);
    *(char *)(iVar28 + 0xd6) = (char)param_9[0x177];
    *(undefined1 *)(iVar28 + 0xd7) = *(undefined1 *)((int)param_9 + 0x2ef);
    *(char *)(iVar28 + 0xd8) = (char)param_9[0x178];
    *(undefined1 *)(iVar28 + 0xd9) = *(undefined1 *)((int)param_9 + 0x2f1);
    *(char *)(iVar28 + 0xda) = (char)param_9[0x179];
    *(undefined1 *)(iVar28 + 0xdb) = *(undefined1 *)((int)param_9 + 0x2f3);
    *(char *)(iVar28 + 0xdc) = (char)param_9[0x15a];
    *(undefined1 *)(iVar28 + 0xdd) = *(undefined1 *)((int)param_9 + 0x2b5);
    *(char *)(iVar28 + 0xde) = (char)param_9[0x15b];
    *(undefined1 *)(iVar28 + 0xdf) = *(undefined1 *)((int)param_9 + 0x2b7);
    *(char *)(iVar28 + 0xe0) = (char)param_9[0x15c];
    *(undefined1 *)(iVar28 + 0xe1) = *(undefined1 *)((int)param_9 + 0x2b9);
    *(char *)(iVar28 + 0xe2) = (char)param_9[0x17a];
    *(undefined1 *)(iVar28 + 0xe3) = *(undefined1 *)((int)param_9 + 0x2f5);
    *(char *)(iVar28 + 0xe4) = (char)param_9[0x17b];
    *(undefined1 *)(iVar28 + 0xe5) = *(undefined1 *)((int)param_9 + 0x2f7);
    *(char *)(iVar28 + 0xe6) = (char)param_9[0x17c];
    *(undefined1 *)(iVar28 + 0xe7) = *(undefined1 *)((int)param_9 + 0x2f9);
    *(char *)(iVar28 + 0xe8) = (char)param_9[0x28b];
    *(undefined1 *)(iVar28 + 0xe9) = *(undefined1 *)((int)param_9 + 0x517);
    *(char *)(iVar28 + 0xea) = (char)param_9[0x169];
    *(undefined1 *)(iVar28 + 0xeb) = *(undefined1 *)((int)param_9 + 0x2d3);
    *(char *)(iVar28 + 0xec) = (char)param_9[0x16a];
    *(undefined1 *)(iVar28 + 0xed) = *(undefined1 *)((int)param_9 + 0x2d5);
    uVar26 = 0;
  }
  *(undefined1 *)(iVar28 + 0xee) = uVar26;
  return;
}


/* 43892e0c */

void FUN_43892e0c(undefined1 *param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined1 *puStack_18;
  undefined1 *puStack_14;
  undefined4 uStack_10;
  
  puStack_18 = param_1;
  puStack_14 = param_2;
  uStack_10 = param_3;
  FUN_43b13b50(&puStack_14,&puStack_18);
  if (puStack_14 == (undefined1 *)0x0) {
    puStack_18[0x4c] = param_1[2];
    puStack_18[0x4d] = param_1[3];
    puStack_18[0x4e] = *param_1;
    puStack_18[0x4f] = param_1[1];
    puStack_18[0x50] = param_1[6];
    puStack_18[0x51] = param_1[7];
    puStack_18[0x52] = param_1[4];
    puStack_18[0x53] = param_1[5];
    puStack_18[0x54] = param_1[10];
    puStack_18[0x55] = param_1[0xb];
    puStack_18[0x56] = param_1[8];
    puStack_18[0x57] = param_1[9];
    puStack_18[0x58] = param_1[0xe];
    puStack_18[0x59] = param_1[0xf];
    puStack_18[0x5a] = param_1[0xc];
    puStack_18[0x5b] = param_1[0xd];
    puStack_18[0x5c] = param_1[0x12];
    puStack_18[0x5d] = param_1[0x13];
    puStack_18[0x5e] = param_1[0x10];
    puStack_18[0x5f] = param_1[0x11];
    puStack_18[0x60] = param_1[0x16];
    puStack_18[0x61] = param_1[0x17];
    puStack_18[0x62] = param_1[0x14];
    puStack_18[99] = param_1[0x15];
    puStack_18[100] = param_1[0x1a];
    puStack_18[0x65] = param_1[0x1b];
    puStack_18[0x66] = param_1[0x18];
    puStack_18[0x67] = param_1[0x19];
    puStack_18[0x68] = param_1[0x1e];
    puStack_18[0x69] = param_1[0x1f];
    puStack_18[0x6a] = param_1[0x1c];
    puStack_18[0x6b] = param_1[0x1d];
    puStack_18[0x6c] = param_1[0x22];
    puStack_18[0x6d] = param_1[0x23];
    puStack_18[0x6e] = param_1[0x20];
    puStack_18[0x6f] = param_1[0x21];
    puStack_18[0x70] = param_1[0x26];
    puStack_18[0x71] = param_1[0x27];
    puStack_18[0x72] = param_1[0x24];
    puStack_18[0x73] = param_1[0x25];
    puStack_18[0x74] = param_1[0x28];
    puStack_18[0x75] = param_1[0x29];
    puStack_18[0x76] = param_1[0x2c];
    puStack_18[0x77] = param_1[0x2d];
    puStack_18[0x78] = param_1[0x2a];
    puStack_18[0x79] = param_1[0x2b];
    puStack_18[0x7a] = param_1[0x30];
    puStack_18[0x7b] = param_1[0x31];
    puStack_18[0x7c] = param_1[0x2e];
    puStack_18[0x7d] = param_1[0x2f];
    puStack_18[0x7e] = param_1[0x34];
    puStack_18[0x7f] = param_1[0x35];
    puStack_18[0x80] = param_1[0x32];
    puStack_18[0x81] = param_1[0x33];
    puStack_18[0x82] = param_1[0x38];
    puStack_18[0x83] = param_1[0x39];
    puStack_18[0x84] = param_1[0x36];
    puStack_18[0x85] = param_1[0x37];
    puStack_18[0x86] = param_1[0x3c];
    puStack_18[0x87] = param_1[0x3d];
    puStack_18[0x88] = param_1[0x3a];
    puStack_18[0x89] = param_1[0x3b];
    puStack_18[0x8a] = param_1[0x40];
    puStack_18[0x8b] = param_1[0x41];
    puStack_18[0x8c] = param_1[0x3e];
    puStack_18[0x8d] = param_1[0x3f];
    puStack_18[0x8e] = param_1[0x44];
    puStack_18[0x8f] = param_1[0x45];
    puStack_18[0x90] = param_1[0x42];
    puStack_18[0x91] = param_1[0x43];
    puStack_18[0x92] = param_1[0x48];
    puStack_18[0x93] = param_1[0x49];
    puStack_18[0x94] = param_1[0x46];
    puStack_18[0x95] = param_1[0x47];
    puStack_18[0x96] = param_1[0x4c];
    puStack_18[0x97] = param_1[0x4d];
    puStack_18[0x98] = param_1[0x4a];
    puStack_18[0x99] = param_1[0x4b];
    puStack_18[0x9a] = param_1[0x50];
    puStack_18[0x9b] = param_1[0x51];
    puStack_18[0x9c] = param_1[0x4e];
    puStack_18[0x9d] = param_1[0x4f];
    puStack_18[0x9e] = param_1[0x52];
    puStack_18[0x9f] = param_1[0x53];
    puStack_18[0xa1] = *param_2;
  }
  else {
    FUN_43892794(3,7,1,DAT_438930a0 + 0x43892e2a);
    FUN_43902718(DAT_438930a4 + 0x43892e32);
  }
  return;
}

