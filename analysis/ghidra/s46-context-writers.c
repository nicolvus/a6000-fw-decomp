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


/* 43afa4ca */

undefined8 FUN_43afa4ca(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  int iStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  *(undefined4 *)(param_1 + 0x4b70) = 0;
  *(undefined4 *)(param_1 + 0x4b68) = 1;
  *(undefined4 *)(param_1 + 0x4b6c) = 1;
  *(undefined1 *)(param_1 + 0x4b95) = 1;
  *(undefined4 *)(param_1 + 0x4b64) = 0;
  *(undefined4 *)(param_1 + 0x4b7c) = 0;
  *(undefined4 *)(param_1 + 0x4b60) = 0;
  *(undefined4 *)(param_1 + 0x4b90) = 0;
  *(undefined4 *)(param_1 + 0x1e0) = 0;
  *(undefined4 *)(param_1 + 0x4ef4) = 0;
  *(undefined4 *)(param_1 + 0x1d8) = 0;
  *(undefined4 *)(param_1 + 0x1dc) = 0;
  *(undefined1 *)(param_1 + 0x77d) = 0;
  *(undefined1 *)(param_1 + 0x77e) = 0;
  *(undefined1 *)(param_1 + 0x73c) = 0;
  *(undefined1 *)(param_1 + 0x4fcd) = 0;
  *(undefined4 *)(param_1 + 0x4fd0) = 0;
  *(undefined4 *)(param_1 + 0x4ad0) = 0;
  iStack_30 = param_1;
  uStack_2c = param_2;
  uStack_28 = param_3;
  uStack_24 = param_4;
  FUN_437f7ce0();
  iVar2 = 0;
  do {
    iVar3 = iVar2;
    *(undefined2 *)(param_1 + iVar3 + 0x4aec) = 0xffff;
    iVar2 = iVar3 + 2;
  } while (iVar3 + 2 != 0x66);
  iVar3 = iVar3 + -100;
  uVar1 = (undefined1)iVar3;
  *(undefined1 *)(param_1 + 0x4e50) = uVar1;
  *(int *)(param_1 + 0x4b88) = iVar3;
  *(int *)(param_1 + 0x5484) = iVar3;
  FUN_437fb64c(&iStack_30,*(undefined4 *)(param_1 + 0x1e0));
  *(int *)(param_1 + 0x4e58) = iVar3;
  *(int *)(param_1 + 0x4fe8) = iVar3;
  *(int *)(param_1 + 0x4e68) = iVar3;
  *(int *)(param_1 + 0x5488) = iStack_30;
  *(undefined4 *)(param_1 + 0x548c) = uStack_2c;
  *(undefined4 *)(param_1 + 0x5490) = uStack_28;
  *(int *)(param_1 + 0x4ec0) = iVar3;
  *(int *)(param_1 + 0x4a80) = iVar3;
  *(int *)(param_1 + 0x4ec4) = iVar3;
  *(int *)(param_1 + 0x4ec8) = iVar3;
  *(int *)(param_1 + 0x4a74) = iVar3;
  *(int *)(param_1 + 0x4a78) = iVar3;
  *(int *)(param_1 + 0x4a7c) = iVar3;
  *(int *)(param_1 + 0x4a84) = iVar3;
  *(int *)(param_1 + 0x4a88) = iVar3;
  *(int *)(param_1 + 0x4a8c) = iVar3;
  *(int *)(param_1 + 0x4a90) = iVar3;
  *(int *)(param_1 + 0x5494) = iVar3;
  *(int *)(param_1 + 0x5498) = iVar3;
  *(int *)(param_1 + 0x549c) = iVar3;
  *(int *)(param_1 + 0x54a0) = iVar3;
  *(undefined1 *)(param_1 + 0x54a4) = uVar1;
  *(int *)(param_1 + 0x5474) = iVar3;
  *(undefined1 *)(param_1 + 0x4b78) = 1;
  *(int *)(param_1 + 0x4b74) = iVar3;
  *(undefined1 *)(param_1 + 0x4b97) = uVar1;
  *(undefined1 *)(param_1 + 0x5350) = uVar1;
  *(undefined1 *)(param_1 + 0x4b96) = uVar1;
  *(undefined1 *)(param_1 + 0x5332) = uVar1;
  *(undefined1 *)(param_1 + 0x5333) = uVar1;
  *(int *)(param_1 + 0x774) = iVar3;
  *(int *)(param_1 + 0x4ad4) = iVar3;
  *(undefined1 *)(param_1 + 0x54a5) = 1;
  return CONCAT44(uStack_2c,iStack_30);
}


/* 43afaa3a */

int FUN_43afaa3a(int param_1,int param_2)

{
  undefined1 uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  FUN_43afa5ea();
  FUN_43afa916(param_1 + 0x20,param_2 + 0x20);
  *(undefined4 *)(param_1 + 0x4ad0) = *(undefined4 *)(param_2 + 0x4ad0);
  *(undefined4 *)(param_1 + 0x4ad4) = *(undefined4 *)(param_2 + 0x4ad4);
  *(undefined4 *)(param_1 + 0x4ad8) = *(undefined4 *)(param_2 + 0x4ad8);
  *(undefined4 *)(param_1 + 0x4adc) = *(undefined4 *)(param_2 + 0x4adc);
  uVar4 = *(undefined4 *)(param_2 + 0x4ae4);
  uVar5 = *(undefined4 *)(param_2 + 0x4ae8);
  *(undefined4 *)(param_1 + 0x4ae0) = *(undefined4 *)(param_2 + 0x4ae0);
  *(undefined4 *)(param_1 + 0x4ae4) = uVar4;
  *(undefined4 *)(param_1 + 0x4ae8) = uVar5;
  FUN_439c5320(param_1 + 0x4aec,param_2 + 0x4aec,0x66);
  uVar4 = *(undefined4 *)(param_2 + 0x4b58);
  uVar5 = *(undefined4 *)(param_2 + 0x4b5c);
  *(undefined4 *)(param_1 + 0x4b54) = *(undefined4 *)(param_2 + 0x4b54);
  uVar6 = *(undefined4 *)(param_2 + 0x4b80);
  *(undefined4 *)(param_1 + 0x4b58) = uVar4;
  *(undefined4 *)(param_1 + 0x4b5c) = uVar5;
  *(undefined4 *)(param_1 + 0x4b60) = *(undefined4 *)(param_2 + 0x4b60);
  *(undefined4 *)(param_1 + 0x4b64) = *(undefined4 *)(param_2 + 0x4b64);
  *(undefined4 *)(param_1 + 0x4b68) = *(undefined4 *)(param_2 + 0x4b68);
  *(undefined4 *)(param_1 + 0x4b6c) = *(undefined4 *)(param_2 + 0x4b6c);
  *(undefined4 *)(param_1 + 0x4b70) = *(undefined4 *)(param_2 + 0x4b70);
  *(undefined4 *)(param_1 + 0x4b74) = *(undefined4 *)(param_2 + 0x4b74);
  *(undefined1 *)(param_1 + 0x4b78) = *(undefined1 *)(param_2 + 0x4b78);
  *(undefined4 *)(param_1 + 0x4b7c) = *(undefined4 *)(param_2 + 0x4b7c);
  *(undefined4 *)(param_1 + 0x4b80) = uVar6;
  *(undefined1 *)(param_1 + 0x4b84) = *(undefined1 *)(param_2 + 0x4b84);
  *(undefined4 *)(param_1 + 0x4b88) = *(undefined4 *)(param_2 + 0x4b88);
  *(undefined1 *)(param_1 + 0x4b8c) = *(undefined1 *)(param_2 + 0x4b8c);
  *(undefined1 *)(param_1 + 0x4b8d) = *(undefined1 *)(param_2 + 0x4b8d);
  *(undefined4 *)(param_1 + 0x4b90) = *(undefined4 *)(param_2 + 0x4b90);
  *(undefined1 *)(param_1 + 0x4b94) = *(undefined1 *)(param_2 + 0x4b94);
  *(undefined1 *)(param_1 + 0x4b95) = *(undefined1 *)(param_2 + 0x4b95);
  *(undefined1 *)(param_1 + 0x4b96) = *(undefined1 *)(param_2 + 0x4b96);
  *(undefined1 *)(param_1 + 0x4b97) = *(undefined1 *)(param_2 + 0x4b97);
  uVar4 = *(undefined4 *)(param_2 + 0x4b9c);
  uVar5 = *(undefined4 *)(param_2 + 0x4ba0);
  uVar6 = *(undefined4 *)(param_2 + 0x4ba4);
  *(undefined4 *)(param_1 + 0x4b98) = *(undefined4 *)(param_2 + 0x4b98);
  *(undefined4 *)(param_1 + 0x4b9c) = uVar4;
  *(undefined4 *)(param_1 + 0x4ba0) = uVar5;
  *(undefined4 *)(param_1 + 0x4ba4) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x4bac);
  *(undefined4 *)(param_1 + 0x4ba8) = *(undefined4 *)(param_2 + 0x4ba8);
  *(undefined4 *)(param_1 + 0x4bac) = uVar4;
  FUN_439c5320(param_1 + 0x4bb0,param_2 + 0x4bb0,0x2a0);
  uVar4 = *(undefined4 *)(param_2 + 0x4e60);
  uVar5 = *(undefined4 *)(param_2 + 0x4e64);
  *(undefined1 *)(param_1 + 0x4e50) = *(undefined1 *)(param_2 + 0x4e50);
  *(undefined4 *)(param_1 + 0x4e54) = *(undefined4 *)(param_2 + 0x4e54);
  *(undefined4 *)(param_1 + 0x4e58) = *(undefined4 *)(param_2 + 0x4e58);
  *(undefined4 *)(param_1 + 0x4e5c) = *(undefined4 *)(param_2 + 0x4e5c);
  *(undefined4 *)(param_1 + 0x4e60) = uVar4;
  *(undefined4 *)(param_1 + 0x4e64) = uVar5;
  uVar4 = *(undefined4 *)(param_2 + 0x4e70);
  uVar5 = *(undefined4 *)(param_2 + 0x4e74);
  *(undefined4 *)(param_1 + 0x4e68) = *(undefined4 *)(param_2 + 0x4e68);
  *(undefined4 *)(param_1 + 0x4e6c) = *(undefined4 *)(param_2 + 0x4e6c);
  *(undefined4 *)(param_1 + 0x4e70) = uVar4;
  *(undefined4 *)(param_1 + 0x4e74) = uVar5;
  uVar4 = *(undefined4 *)(param_2 + 0x4e7c);
  *(undefined4 *)(param_1 + 0x4e78) = *(undefined4 *)(param_2 + 0x4e78);
  *(undefined4 *)(param_1 + 0x4e7c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e84);
  *(undefined4 *)(param_1 + 0x4e80) = *(undefined4 *)(param_2 + 0x4e80);
  *(undefined4 *)(param_1 + 0x4e84) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e8c);
  *(undefined4 *)(param_1 + 0x4e88) = *(undefined4 *)(param_2 + 0x4e88);
  *(undefined4 *)(param_1 + 0x4e8c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e94);
  *(undefined4 *)(param_1 + 0x4e90) = *(undefined4 *)(param_2 + 0x4e90);
  *(undefined4 *)(param_1 + 0x4e94) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4e9c);
  *(undefined4 *)(param_1 + 0x4e98) = *(undefined4 *)(param_2 + 0x4e98);
  *(undefined4 *)(param_1 + 0x4e9c) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4ea4);
  *(undefined4 *)(param_1 + 0x4ea0) = *(undefined4 *)(param_2 + 0x4ea0);
  *(undefined4 *)(param_1 + 0x4ea4) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x4eac);
  uVar5 = *(undefined4 *)(param_2 + 0x4eb0);
  uVar6 = *(undefined4 *)(param_2 + 0x4eb4);
  *(undefined4 *)(param_1 + 0x4ea8) = *(undefined4 *)(param_2 + 0x4ea8);
  *(undefined4 *)(param_1 + 0x4eac) = uVar4;
  *(undefined4 *)(param_1 + 0x4eb0) = uVar5;
  *(undefined4 *)(param_1 + 0x4eb4) = uVar6;
  *(undefined4 *)(param_1 + 0x4eb8) = *(undefined4 *)(param_2 + 0x4eb8);
  uVar2 = *(undefined2 *)(param_2 + 0x4ebc);
  *(undefined2 *)(param_1 + 0x4ebe) = *(undefined2 *)(param_2 + 0x4ebe);
  uVar4 = *(undefined4 *)(param_2 + 0x4ec0);
  *(undefined2 *)(param_1 + 0x4ebc) = uVar2;
  *(undefined4 *)(param_1 + 0x4ec0) = uVar4;
  *(undefined4 *)(param_1 + 0x4ec4) = *(undefined4 *)(param_2 + 0x4ec4);
  *(undefined4 *)(param_1 + 0x4ec8) = *(undefined4 *)(param_2 + 0x4ec8);
  *(undefined4 *)(param_1 + 0x4ecc) = *(undefined4 *)(param_2 + 0x4ecc);
  *(undefined4 *)(param_1 + 0x4ed0) = *(undefined4 *)(param_2 + 0x4ed0);
  *(undefined4 *)(param_1 + 0x4ed4) = *(undefined4 *)(param_2 + 0x4ed4);
  uVar4 = *(undefined4 *)(param_2 + 0x4edc);
  *(undefined4 *)(param_1 + 0x4ed8) = *(undefined4 *)(param_2 + 0x4ed8);
  *(undefined4 *)(param_1 + 0x4edc) = uVar4;
  *(undefined1 *)(param_1 + 0x4ee0) = *(undefined1 *)(param_2 + 0x4ee0);
  *(undefined4 *)(param_1 + 0x4ee4) = *(undefined4 *)(param_2 + 0x4ee4);
  *(undefined1 *)(param_1 + 0x4ee8) = *(undefined1 *)(param_2 + 0x4ee8);
  *(undefined4 *)(param_1 + 0x4eec) = *(undefined4 *)(param_2 + 0x4eec);
  *(undefined1 *)(param_1 + 0x4ef0) = *(undefined1 *)(param_2 + 0x4ef0);
  *(undefined1 *)(param_1 + 0x4ef1) = *(undefined1 *)(param_2 + 0x4ef1);
  *(undefined4 *)(param_1 + 0x4ef4) = *(undefined4 *)(param_2 + 0x4ef4);
  *(undefined1 *)(param_1 + 0x4ef8) = *(undefined1 *)(param_2 + 0x4ef8);
  *(undefined1 *)(param_1 + 0x4ef9) = *(undefined1 *)(param_2 + 0x4ef9);
  FUN_439c5320(param_1 + 0x4efa,param_2 + 0x4efa,0x3c);
  FUN_439c5320(param_1 + 0x4f36,param_2 + 0x4f36,0x88);
  *(undefined4 *)(param_1 + 0x4fc0) = *(undefined4 *)(param_2 + 0x4fc0);
  *(undefined4 *)(param_1 + 0x4fc4) = *(undefined4 *)(param_2 + 0x4fc4);
  *(undefined4 *)(param_1 + 0x4fc8) = *(undefined4 *)(param_2 + 0x4fc8);
  *(undefined1 *)(param_1 + 0x4fcc) = *(undefined1 *)(param_2 + 0x4fcc);
  *(undefined1 *)(param_1 + 0x4fcd) = *(undefined1 *)(param_2 + 0x4fcd);
  *(undefined4 *)(param_1 + 0x4fd0) = *(undefined4 *)(param_2 + 0x4fd0);
  uVar4 = *(undefined4 *)(param_2 + 0x4fd8);
  uVar5 = *(undefined4 *)(param_2 + 0x4fdc);
  uVar6 = *(undefined4 *)(param_2 + 0x4fe0);
  *(undefined4 *)(param_1 + 0x4fd4) = *(undefined4 *)(param_2 + 0x4fd4);
  *(undefined4 *)(param_1 + 0x4fd8) = uVar4;
  *(undefined4 *)(param_1 + 0x4fdc) = uVar5;
  *(undefined4 *)(param_1 + 0x4fe0) = uVar6;
  *(undefined4 *)(param_1 + 0x4fe4) = *(undefined4 *)(param_2 + 0x4fe4);
  *(undefined4 *)(param_1 + 0x4fe8) = *(undefined4 *)(param_2 + 0x4fe8);
  FUN_439c5320(param_1 + 0x4fec,param_2 + 0x4fec,0x6c);
  *(undefined4 *)(param_1 + 0x5058) = *(undefined4 *)(param_2 + 0x5058);
  uVar4 = *(undefined4 *)(param_2 + 0x5060);
  uVar5 = *(undefined4 *)(param_2 + 0x5064);
  uVar6 = *(undefined4 *)(param_2 + 0x5068);
  *(undefined4 *)(param_1 + 0x505c) = *(undefined4 *)(param_2 + 0x505c);
  *(undefined4 *)(param_1 + 0x5060) = uVar4;
  *(undefined4 *)(param_1 + 0x5064) = uVar5;
  *(undefined4 *)(param_1 + 0x5068) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x5070);
  uVar5 = *(undefined4 *)(param_2 + 0x5074);
  uVar6 = *(undefined4 *)(param_2 + 0x5078);
  *(undefined4 *)(param_1 + 0x506c) = *(undefined4 *)(param_2 + 0x506c);
  *(undefined4 *)(param_1 + 0x5070) = uVar4;
  *(undefined4 *)(param_1 + 0x5074) = uVar5;
  *(undefined4 *)(param_1 + 0x5078) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x5080);
  uVar5 = *(undefined4 *)(param_2 + 0x5084);
  uVar6 = *(undefined4 *)(param_2 + 0x5088);
  *(undefined4 *)(param_1 + 0x507c) = *(undefined4 *)(param_2 + 0x507c);
  *(undefined4 *)(param_1 + 0x5080) = uVar4;
  *(undefined4 *)(param_1 + 0x5084) = uVar5;
  *(undefined4 *)(param_1 + 0x5088) = uVar6;
  *(undefined4 *)(param_1 + 0x508c) = *(undefined4 *)(param_2 + 0x508c);
  uVar4 = *(undefined4 *)(param_2 + 0x5094);
  uVar5 = *(undefined4 *)(param_2 + 0x5098);
  uVar6 = *(undefined4 *)(param_2 + 0x509c);
  *(undefined4 *)(param_1 + 0x5090) = *(undefined4 *)(param_2 + 0x5090);
  *(undefined4 *)(param_1 + 0x5094) = uVar4;
  *(undefined4 *)(param_1 + 0x5098) = uVar5;
  *(undefined4 *)(param_1 + 0x509c) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50a4);
  uVar5 = *(undefined4 *)(param_2 + 0x50a8);
  uVar6 = *(undefined4 *)(param_2 + 0x50ac);
  *(undefined4 *)(param_1 + 0x50a0) = *(undefined4 *)(param_2 + 0x50a0);
  *(undefined4 *)(param_1 + 0x50a4) = uVar4;
  *(undefined4 *)(param_1 + 0x50a8) = uVar5;
  *(undefined4 *)(param_1 + 0x50ac) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50b4);
  uVar5 = *(undefined4 *)(param_2 + 0x50b8);
  uVar6 = *(undefined4 *)(param_2 + 0x50bc);
  *(undefined4 *)(param_1 + 0x50b0) = *(undefined4 *)(param_2 + 0x50b0);
  *(undefined4 *)(param_1 + 0x50b4) = uVar4;
  *(undefined4 *)(param_1 + 0x50b8) = uVar5;
  *(undefined4 *)(param_1 + 0x50bc) = uVar6;
  *(undefined4 *)(param_1 + 0x50c0) = *(undefined4 *)(param_2 + 0x50c0);
  uVar4 = *(undefined4 *)(param_2 + 0x50c8);
  uVar5 = *(undefined4 *)(param_2 + 0x50cc);
  uVar6 = *(undefined4 *)(param_2 + 0x50d0);
  *(undefined4 *)(param_1 + 0x50c4) = *(undefined4 *)(param_2 + 0x50c4);
  *(undefined4 *)(param_1 + 0x50c8) = uVar4;
  *(undefined4 *)(param_1 + 0x50cc) = uVar5;
  *(undefined4 *)(param_1 + 0x50d0) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50d8);
  uVar5 = *(undefined4 *)(param_2 + 0x50dc);
  uVar6 = *(undefined4 *)(param_2 + 0x50e0);
  *(undefined4 *)(param_1 + 0x50d4) = *(undefined4 *)(param_2 + 0x50d4);
  *(undefined4 *)(param_1 + 0x50d8) = uVar4;
  *(undefined4 *)(param_1 + 0x50dc) = uVar5;
  *(undefined4 *)(param_1 + 0x50e0) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x50e8);
  uVar5 = *(undefined4 *)(param_2 + 0x50ec);
  uVar6 = *(undefined4 *)(param_2 + 0x50f0);
  *(undefined4 *)(param_1 + 0x50e4) = *(undefined4 *)(param_2 + 0x50e4);
  *(undefined4 *)(param_1 + 0x50e8) = uVar4;
  *(undefined4 *)(param_1 + 0x50ec) = uVar5;
  *(undefined4 *)(param_1 + 0x50f0) = uVar6;
  *(undefined4 *)(param_1 + 0x50f4) = *(undefined4 *)(param_2 + 0x50f4);
  uVar4 = *(undefined4 *)(param_2 + 0x50fc);
  uVar5 = *(undefined4 *)(param_2 + 0x5100);
  uVar6 = *(undefined4 *)(param_2 + 0x5104);
  *(undefined4 *)(param_1 + 0x50f8) = *(undefined4 *)(param_2 + 0x50f8);
  *(undefined4 *)(param_1 + 0x50fc) = uVar4;
  *(undefined4 *)(param_1 + 0x5100) = uVar5;
  *(undefined4 *)(param_1 + 0x5104) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x510c);
  uVar5 = *(undefined4 *)(param_2 + 0x5110);
  uVar6 = *(undefined4 *)(param_2 + 0x5114);
  *(undefined4 *)(param_1 + 0x5108) = *(undefined4 *)(param_2 + 0x5108);
  *(undefined4 *)(param_1 + 0x510c) = uVar4;
  *(undefined4 *)(param_1 + 0x5110) = uVar5;
  *(undefined4 *)(param_1 + 0x5114) = uVar6;
  uVar4 = *(undefined4 *)(param_2 + 0x511c);
  uVar5 = *(undefined4 *)(param_2 + 0x5120);
  uVar6 = *(undefined4 *)(param_2 + 0x5124);
  *(undefined4 *)(param_1 + 0x5118) = *(undefined4 *)(param_2 + 0x5118);
  *(undefined4 *)(param_1 + 0x511c) = uVar4;
  *(undefined4 *)(param_1 + 0x5120) = uVar5;
  *(undefined4 *)(param_1 + 0x5124) = uVar6;
  *(undefined4 *)(param_1 + 0x5128) = *(undefined4 *)(param_2 + 0x5128);
  FUN_439c5320(param_1 + 0x512c,param_2 + 0x512c,0x206);
  uVar2 = *(undefined2 *)(param_2 + 0x5334);
  *(undefined2 *)(param_1 + 0x5332) = *(undefined2 *)(param_2 + 0x5332);
  uVar1 = *(undefined1 *)(param_2 + 0x5336);
  *(undefined2 *)(param_1 + 0x5334) = uVar2;
  uVar2 = *(undefined2 *)(param_2 + 0x533e);
  *(undefined1 *)(param_1 + 0x5336) = uVar1;
  uVar4 = *(undefined4 *)(param_2 + 0x5338);
  *(undefined2 *)(param_1 + 0x533e) = uVar2;
  *(undefined4 *)(param_1 + 0x5338) = uVar4;
  *(undefined2 *)(param_1 + 0x533c) = *(undefined2 *)(param_2 + 0x533c);
  *(undefined4 *)(param_1 + 0x5340) = *(undefined4 *)(param_2 + 0x5340);
  *(undefined4 *)(param_1 + 0x5344) = *(undefined4 *)(param_2 + 0x5344);
  *(undefined4 *)(param_1 + 0x5348) = *(undefined4 *)(param_2 + 0x5348);
  *(undefined4 *)(param_1 + 0x534c) = *(undefined4 *)(param_2 + 0x534c);
  FUN_439c5320(param_1 + 0x5350,param_2 + 0x5350,0x102);
  uVar3 = *(undefined2 *)(param_2 + 0x5452);
  uVar2 = *(undefined2 *)(param_2 + 0x5480);
  *(undefined2 *)(param_1 + 0x5454) = *(undefined2 *)(param_2 + 0x5454);
  *(undefined2 *)(param_1 + 0x5452) = uVar3;
  uVar4 = *(undefined4 *)(param_2 + 0x5458);
  uVar5 = *(undefined4 *)(param_2 + 0x545c);
  uVar6 = *(undefined4 *)(param_2 + 0x5460);
  *(undefined1 *)(param_1 + 0x5456) = *(undefined1 *)(param_2 + 0x5456);
  *(undefined4 *)(param_1 + 0x5458) = uVar4;
  *(undefined4 *)(param_1 + 0x545c) = uVar5;
  *(undefined4 *)(param_1 + 0x5460) = uVar6;
  uVar3 = *(undefined2 *)(param_2 + 0x547a);
  *(undefined4 *)(param_1 + 0x5464) = *(undefined4 *)(param_2 + 0x5464);
  uVar4 = *(undefined4 *)(param_2 + 0x5468);
  *(undefined2 *)(param_1 + 0x547a) = uVar3;
  uVar3 = *(undefined2 *)(param_2 + 0x547e);
  *(undefined4 *)(param_1 + 0x5468) = uVar4;
  uVar4 = *(undefined4 *)(param_2 + 0x546c);
  *(undefined2 *)(param_1 + 0x547e) = uVar3;
  *(undefined4 *)(param_1 + 0x546c) = uVar4;
  *(undefined4 *)(param_1 + 0x5470) = *(undefined4 *)(param_2 + 0x5470);
  *(undefined4 *)(param_1 + 0x5474) = *(undefined4 *)(param_2 + 0x5474);
  *(undefined2 *)(param_1 + 0x5478) = *(undefined2 *)(param_2 + 0x5478);
  *(undefined2 *)(param_1 + 0x547c) = *(undefined2 *)(param_2 + 0x547c);
  *(undefined2 *)(param_1 + 0x5480) = uVar2;
  *(undefined2 *)(param_1 + 0x5482) = *(undefined2 *)(param_2 + 0x5482);
  uVar4 = *(undefined4 *)(param_2 + 0x5488);
  uVar5 = *(undefined4 *)(param_2 + 0x548c);
  uVar6 = *(undefined4 *)(param_2 + 0x5490);
  *(undefined4 *)(param_1 + 0x5484) = *(undefined4 *)(param_2 + 0x5484);
  *(undefined4 *)(param_1 + 0x5488) = uVar4;
  *(undefined4 *)(param_1 + 0x548c) = uVar5;
  *(undefined4 *)(param_1 + 0x5490) = uVar6;
  *(undefined4 *)(param_1 + 0x5494) = *(undefined4 *)(param_2 + 0x5494);
  *(undefined4 *)(param_1 + 0x5498) = *(undefined4 *)(param_2 + 0x5498);
  *(undefined4 *)(param_1 + 0x549c) = *(undefined4 *)(param_2 + 0x549c);
  *(undefined4 *)(param_1 + 0x54a0) = *(undefined4 *)(param_2 + 0x54a0);
  *(undefined1 *)(param_1 + 0x54a4) = *(undefined1 *)(param_2 + 0x54a4);
  *(undefined1 *)(param_1 + 0x54a5) = *(undefined1 *)(param_2 + 0x54a5);
  *(undefined4 *)(param_1 + 0x54a8) = *(undefined4 *)(param_2 + 0x54a8);
  *(undefined4 *)(param_1 + 0x54ac) = *(undefined4 *)(param_2 + 0x54ac);
  uVar4 = *(undefined4 *)(param_2 + 0x54b4);
  uVar5 = *(undefined4 *)(param_2 + 0x54b8);
  uVar6 = *(undefined4 *)(param_2 + 0x54bc);
  *(undefined4 *)(param_1 + 0x54b0) = *(undefined4 *)(param_2 + 0x54b0);
  *(undefined4 *)(param_1 + 0x54b4) = uVar4;
  *(undefined4 *)(param_1 + 0x54b8) = uVar5;
  *(undefined4 *)(param_1 + 0x54bc) = uVar6;
  *(undefined4 *)(param_1 + 0x54c0) = *(undefined4 *)(param_2 + 0x54c0);
  uVar4 = *(undefined4 *)(param_2 + 0x54c8);
  uVar5 = *(undefined4 *)(param_2 + 0x54cc);
  *(undefined1 *)(param_1 + 0x54c4) = *(undefined1 *)(param_2 + 0x54c4);
  *(undefined4 *)(param_1 + 0x54c8) = uVar4;
  *(undefined4 *)(param_1 + 0x54cc) = uVar5;
  return param_1;
}


/* 43af0072 */

void FUN_43af0072(undefined4 *param_1)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puVar6;
  int iVar7;
  uint uVar8;
  byte abStack_2c [16];
  
  iVar2 = FUN_437bc52c(1);
  if (iVar2 != 0) {
    iVar3 = FUN_43aeffec();
    iVar7 = 0;
    FUN_43af0020(iVar2,abStack_2c);
    *(undefined2 *)((int)param_1 + 0x7e) = *(undefined2 *)(iVar2 + 0x1ee);
    *(undefined2 *)(param_1 + 0x20) = *(undefined2 *)(iVar2 + 0x1f0);
    iVar5 = iVar2;
    puVar6 = param_1;
    do {
      uVar8 = (uint)abStack_2c[iVar7];
      if ((iVar3 < iVar7) || ((*(ushort *)(iVar5 + 0x24) & 1) != 0)) {
        uVar4 = 0;
        *(undefined1 *)((int)param_1 + 0x82) = 0;
        *(undefined1 *)((int)param_1 + 0x83) = 0;
        *(undefined1 *)(param_1 + 0x25) = 0;
        *(undefined1 *)((int)param_1 + 0x95) = 0;
        *(undefined2 *)(param_1 + 0x1b) = 0;
        *puVar6 = 0;
        puVar6[9] = 0;
LAB_43af0122:
        puVar6[0x12] = uVar4;
      }
      else {
        *(char *)((int)param_1 + 0x82) = (char)*(undefined2 *)(iVar5 + 0x28);
        *(char *)((int)param_1 + 0x83) = (char)*(undefined2 *)(iVar5 + 0x2a);
        *(char *)(param_1 + 0x25) = (char)*(undefined2 *)(iVar5 + 0x2c);
        *(char *)((int)param_1 + 0x95) = (char)*(undefined2 *)(iVar5 + 0x2e);
        if (uVar8 < 2) {
          uVar1 = FUN_437bb088((int)*(short *)(iVar2 + ((iVar7 * 0x10 - uVar8) + 9) * 2));
          uVar4 = *(undefined4 *)(iVar2 + (uVar8 + iVar7 * 8) * 4 + 0x14);
          *puVar6 = uVar4;
          puVar6[9] = uVar4;
          uVar4 = *(undefined4 *)(iVar5 + 0x1c);
          *(undefined2 *)(param_1 + 0x1b) = uVar1;
          goto LAB_43af0122;
        }
      }
      iVar7 = iVar7 + 1;
      param_1 = (undefined4 *)((int)param_1 + 2);
      puVar6 = puVar6 + 1;
      iVar5 = iVar5 + 0x20;
    } while (iVar7 != 9);
  }
  return;
}


/* 43ae53a2 */

void FUN_43ae53a2(byte *param_1)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  undefined2 uVar4;
  short sVar5;
  char *pcVar6;
  short *psVar7;
  bool bVar8;
  
  pcVar6 = (char *)thunk_FUN_4377b420();
  bVar3 = *param_1;
  bVar8 = *pcVar6 != '\0';
  *param_1 = bVar3 & 0xfe | bVar8;
  bVar1 = (pcVar6[1] & 1U) << 1;
  *param_1 = bVar3 & 0xfc | bVar8 | bVar1;
  bVar2 = (pcVar6[2] & 1U) << 2;
  *param_1 = bVar3 & 0xf8 | bVar8 | bVar1 | bVar2;
  *param_1 = bVar8 | bVar1 | bVar2 | (*(int *)(pcVar6 + 4) != 0) << 3;
  param_1[1] = (byte)*(undefined4 *)(pcVar6 + 8);
  param_1[4] = pcVar6[0x14];
  param_1[5] = pcVar6[0x15];
  param_1[6] = pcVar6[0x16];
  param_1[7] = pcVar6[0x17];
  param_1[8] = pcVar6[0x18];
  param_1[9] = pcVar6[0x19];
  param_1[10] = pcVar6[0x1a];
  param_1[0xb] = pcVar6[0x1b];
  param_1[0xc] = pcVar6[0x1c];
  param_1[0xd] = pcVar6[0x1d];
  param_1[0xe] = pcVar6[0x1e];
  param_1[0xf] = pcVar6[0x1f];
  param_1[0x10] = pcVar6[0x20];
  param_1[0x11] = pcVar6[0x21];
  param_1[0x12] = pcVar6[0x22];
  param_1[0x13] = pcVar6[0x23];
  param_1[0x14] = pcVar6[0x24];
  param_1[0x15] = pcVar6[0x25];
  uVar4 = *(undefined2 *)(pcVar6 + 0x28);
  param_1[0x16] = (byte)uVar4;
  param_1[0x17] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x2c);
  param_1[0x18] = (byte)uVar4;
  param_1[0x19] = (byte)((ushort)uVar4 >> 8);
  param_1[0x1a] = pcVar6[0x30];
  param_1[0x1b] = pcVar6[0x31];
  param_1[0x1c] = pcVar6[0x32];
  param_1[0x1d] = pcVar6[0x33];
  param_1[0x1e] = pcVar6[0x34];
  param_1[0x1f] = pcVar6[0x35];
  param_1[0x20] = pcVar6[0x36];
  param_1[0x21] = pcVar6[0x37];
  uVar4 = *(undefined2 *)(pcVar6 + 0x38);
  param_1[0x22] = (byte)uVar4;
  param_1[0x23] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x3c);
  param_1[0x24] = (byte)uVar4;
  param_1[0x25] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x40);
  param_1[0x26] = (byte)uVar4;
  param_1[0x27] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x44);
  param_1[0x28] = (byte)uVar4;
  param_1[0x29] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x48);
  param_1[0x2a] = (byte)uVar4;
  param_1[0x2b] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x4c);
  param_1[0x2c] = (byte)uVar4;
  param_1[0x2d] = (byte)((ushort)uVar4 >> 8);
  uVar4 = *(undefined2 *)(pcVar6 + 0x50);
  param_1[0x2e] = (byte)uVar4;
  param_1[0x2f] = (byte)((ushort)uVar4 >> 8);
  param_1[0x30] = pcVar6[0x54];
  param_1[0x31] = 0;
  param_1[0x32] = pcVar6[0x56];
  param_1[0x33] = 0;
  param_1[0x34] = pcVar6[0x58];
  param_1[0x35] = pcVar6[0x59];
  param_1[0x36] = pcVar6[0x5a];
  param_1[0x37] = pcVar6[0x5b];
  param_1[0x38] = pcVar6[0x5c];
  param_1[0x39] = pcVar6[0x5d];
  param_1[0x3a] = pcVar6[0x5e];
  param_1[0x3b] = pcVar6[0x5f];
  param_1[0x3c] = pcVar6[0x6c];
  param_1[0x3d] = pcVar6[0x6d];
  param_1[0x3e] = pcVar6[0x6e];
  param_1[0x3f] = pcVar6[0x6f];
  param_1[0x40] = pcVar6[0x70];
  param_1[0x41] = pcVar6[0x71];
  param_1[0x42] = pcVar6[0x72];
  param_1[0x43] = pcVar6[0x73];
  param_1[0x44] = pcVar6[0x74];
  param_1[0x45] = pcVar6[0x75];
  param_1[0x46] = pcVar6[0x76];
  param_1[0x47] = pcVar6[0x77];
  psVar7 = (short *)thunk_FUN_4377b414();
  sVar5 = *psVar7;
  param_1[0x48] = (byte)sVar5;
  param_1[0x49] = (byte)((ushort)sVar5 >> 8);
                    /* WARNING: Store size is inaccurate */
  *(short *)(param_1 + 0x4a) = sVar5 >> 0xf;
                    /* WARNING: Store size is inaccurate */
  *(short *)(param_1 + 0x4b) = sVar5 >> 0xf;
  param_1[0x4c] = *(byte *)(psVar7 + 2);
  param_1[0x4d] = *(byte *)((int)psVar7 + 5);
  param_1[0x4e] = *(byte *)(psVar7 + 3);
  param_1[0x4f] = *(byte *)((int)psVar7 + 7);
  param_1[0x50] = *(byte *)(psVar7 + 4);
  param_1[0x51] = 0;
  sVar5 = psVar7[6];
  param_1[0x52] = (byte)sVar5;
  param_1[0x53] = (byte)((ushort)sVar5 >> 8);
  param_1[0x54] = *(byte *)(psVar7 + 8);
  param_1[0x55] = *(byte *)((int)psVar7 + 0x11);
  param_1[0x56] = *(byte *)(psVar7 + 9);
  param_1[0x57] = *(byte *)((int)psVar7 + 0x13);
  param_1[0x58] = *(byte *)(psVar7 + 10);
  param_1[0x59] = *(byte *)((int)psVar7 + 0x15);
  param_1[0x5a] = *(byte *)(psVar7 + 0xb);
  param_1[0x5b] = *(byte *)((int)psVar7 + 0x17);
  param_1[0x5c] = *(byte *)(psVar7 + 0xc);
  param_1[0x5d] = *(byte *)((int)psVar7 + 0x19);
  param_1[0x5e] = *(byte *)(psVar7 + 0xd);
  param_1[0x5f] = *(byte *)((int)psVar7 + 0x1b);
  param_1[0x60] = *(byte *)(psVar7 + 0xe);
  param_1[0x61] = *(byte *)((int)psVar7 + 0x1d);
  param_1[0x62] = *(byte *)(psVar7 + 0xf);
  param_1[99] = *(byte *)((int)psVar7 + 0x1f);
  param_1[100] = *(byte *)(psVar7 + 0x10);
  param_1[0x65] = *(byte *)((int)psVar7 + 0x21);
  param_1[0x66] = *(byte *)(psVar7 + 0x11);
  param_1[0x67] = *(byte *)((int)psVar7 + 0x23);
  param_1[0x68] = *(byte *)(psVar7 + 0x12);
  param_1[0x69] = *(byte *)((int)psVar7 + 0x25);
  param_1[0x6a] = *(byte *)(psVar7 + 0x13);
  param_1[0x6b] = *(byte *)((int)psVar7 + 0x27);
  param_1[0x6c] = *(byte *)(psVar7 + 0x14);
  param_1[0x6d] = *(byte *)((int)psVar7 + 0x29);
  param_1[0x6e] = *(byte *)(psVar7 + 0x15);
  param_1[0x6f] = *(byte *)((int)psVar7 + 0x2b);
  param_1[0x70] = *(byte *)(psVar7 + 0x16);
  param_1[0x71] = *(byte *)((int)psVar7 + 0x2d);
  param_1[0x72] = *(byte *)(psVar7 + 0x17);
  param_1[0x73] = *(byte *)((int)psVar7 + 0x2f);
  param_1[0x74] = *(byte *)(psVar7 + 0x18);
  param_1[0x75] = 0;
  param_1[0x76] = *(byte *)((int)psVar7 + 0x31);
  param_1[0x77] = 0;
  sVar5 = psVar7[0x1a];
  param_1[0x78] = (byte)sVar5;
  param_1[0x79] = (byte)((ushort)sVar5 >> 8);
  sVar5 = psVar7[0x1c];
  param_1[0x7a] = (byte)sVar5;
  param_1[0x7b] = (byte)((ushort)sVar5 >> 8);
  param_1[0x7c] = *(byte *)(psVar7 + 0x1e);
  param_1[0x7d] = *(byte *)((int)psVar7 + 0x3d);
  param_1[0x7e] = *(byte *)(psVar7 + 0x1f);
  param_1[0x7f] = *(byte *)((int)psVar7 + 0x3f);
  param_1[0x80] = *(byte *)(psVar7 + 0x20);
  param_1[0x81] = *(byte *)((int)psVar7 + 0x41);
  param_1[0x82] = *(byte *)(psVar7 + 0x21);
  param_1[0x83] = *(byte *)((int)psVar7 + 0x43);
  param_1[0x84] = *(byte *)(psVar7 + 0x22);
  param_1[0x85] = *(byte *)((int)psVar7 + 0x45);
  param_1[0x86] = *(byte *)(psVar7 + 0x23);
  param_1[0x87] = *(byte *)((int)psVar7 + 0x47);
  param_1[0x88] = *(byte *)(psVar7 + 0x24);
  param_1[0x89] = *(byte *)((int)psVar7 + 0x49);
  param_1[0x8a] = *(byte *)(psVar7 + 0x25);
  param_1[0x8b] = *(byte *)((int)psVar7 + 0x4b);
  param_1[0x8c] = *(byte *)(psVar7 + 0x26);
  param_1[0x8d] = *(byte *)((int)psVar7 + 0x4d);
  param_1[0x8e] = *(byte *)(psVar7 + 0x27);
  param_1[0x8f] = *(byte *)((int)psVar7 + 0x4f);
  sVar5 = psVar7[0x28];
  param_1[0x90] = (byte)sVar5;
  param_1[0x91] = (byte)((ushort)sVar5 >> 8);
  param_1[0x92] = *(byte *)(psVar7 + 0x2a);
  param_1[0x93] = *(byte *)((int)psVar7 + 0x55);
  param_1[0x94] = *(byte *)(psVar7 + 0x2c);
  param_1[0x95] = *(byte *)((int)psVar7 + 0x59);
  param_1[0x96] = *(byte *)(psVar7 + 0x2d);
  param_1[0x97] = *(byte *)((int)psVar7 + 0x5b);
  param_1[0x98] = *(byte *)(psVar7 + 0x2e);
  param_1[0x99] = *(byte *)((int)psVar7 + 0x5d);
  param_1[0x9a] = *(byte *)(psVar7 + 0x2f);
  param_1[0x9b] = *(byte *)((int)psVar7 + 0x5f);
  param_1[0x9c] = *(byte *)(psVar7 + 0x30);
  param_1[0x9d] = *(byte *)((int)psVar7 + 0x61);
  param_1[0x9e] = *(byte *)(psVar7 + 0x31);
  param_1[0x9f] = *(byte *)((int)psVar7 + 99);
  param_1[0xa0] = *(byte *)(psVar7 + 0x32);
  param_1[0xa1] = *(byte *)((int)psVar7 + 0x65);
  param_1[0xa2] = *(byte *)(psVar7 + 0x33);
  param_1[0xa3] = *(byte *)((int)psVar7 + 0x67);
  return;
}


/* 43add632 */

uint FUN_43add632(int param_1,uint param_2,uint param_3,int param_4,byte param_5,byte param_6,
                 byte param_7,undefined1 param_8,char param_9,byte param_10,undefined2 param_11,
                 undefined1 param_12,undefined1 param_13,char param_14,char param_15,char param_16)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  byte bVar9;
  
  uVar5 = param_13;
  uVar4 = param_12;
  uVar3 = param_11;
  uVar8 = (uint)param_6;
  iVar6 = FUN_436efa1c();
  *(char *)(iVar6 + 0x7f) = (char)param_3;
  uVar1 = (undefined1)param_2;
  *(undefined1 *)(iVar6 + 0x7e) = uVar1;
  param_3 = param_3 & 0x7f;
  *(char *)(iVar6 + 0x80) = (char)param_4;
  *(byte *)(iVar6 + 0x82) = param_6;
  *(byte *)(iVar6 + 0x83) = param_7;
  *(byte *)(iVar6 + 0x81) = param_5;
  *(short *)(iVar6 + 0x7c) = (short)param_1;
  *(undefined1 *)(iVar6 + 0x84) = param_8;
  *(char *)(iVar6 + 0x85) = param_9;
  *(byte *)(iVar6 + 0x86) = param_10;
  *(undefined1 *)(iVar6 + 0x8a) = uVar4;
  *(undefined2 *)(iVar6 + 0x88) = uVar3;
  *(undefined1 *)(iVar6 + 0x8b) = uVar5;
  *(char *)(iVar6 + 0x8c) = param_14;
  *(char *)(iVar6 + 0x8d) = param_15;
  *(char *)(iVar6 + 0x8e) = param_16;
  iVar7 = FUN_436ef7cc();
  bVar9 = param_10 & 0x3f;
  *(char **)(iVar7 + 0x60) = &param_14;
  *(undefined1 **)(iVar7 + 100) = &param_8;
  *(char **)(iVar7 + 0x68) = &param_9;
  *(char **)(iVar7 + 0x6c) = &param_15;
  *(char **)(iVar7 + 0x70) = &param_16;
  *(byte **)(iVar7 + 0x74) = &param_10;
  uVar2 = (undefined1)param_3;
  if (param_16 == '\x01') {
    if (((param_15 == '\x01') && (param_14 == '\x01')) && (param_9 == '\0')) {
      *(byte *)(iVar6 + 0x8f) = bVar9;
      *(undefined1 *)(iVar6 + 0x90) = uVar2;
      uVar8 = (param_4 + param_2) - (param_5 & 0x1f);
      *(char *)(iVar6 + 0x91) = (char)param_4;
      *(char *)(iVar6 + 0x92) = (char)(param_5 & 0x1f);
      param_2 = uVar8 & 0xff;
      *(undefined1 *)(iVar6 + 0x94) = 0;
      *(char *)(iVar6 + 0x93) = (char)uVar8;
      *(undefined1 *)(iVar6 + 0x95) = 0;
    }
    else if (uVar8 == 0) {
      *(byte *)(iVar6 + 0x8f) = bVar9;
      *(undefined1 *)(iVar6 + 0x90) = uVar2;
      *(byte *)(iVar6 + 0x91) = param_6;
      *(byte *)(iVar6 + 0x92) = param_6;
      *(undefined1 *)(iVar6 + 0x93) = uVar1;
      *(byte *)(iVar6 + 0x94) = param_6;
      *(byte *)(iVar6 + 0x95) = param_6;
    }
    else {
      *(byte *)(iVar6 + 0x8f) = bVar9;
      *(undefined1 *)(iVar6 + 0x90) = uVar2;
      param_2 = (uint)param_7;
      if (param_14 != '\x01') {
        param_2 = param_7 + param_3;
      }
      *(byte *)(iVar6 + 0x94) = param_6;
      if (param_14 != '\x01') {
        param_2 = param_2 & 0xff;
      }
      *(char *)(iVar6 + 0x95) = (char)param_2;
      if (param_2 < uVar8) {
        param_2 = uVar8;
      }
      *(char *)(iVar6 + 0x93) = (char)param_2;
      *(undefined1 *)(iVar6 + 0x91) = 0;
      *(undefined1 *)(iVar6 + 0x92) = 0;
    }
  }
  else {
    if (param_1 == 0x14) {
      param_2 = FUN_43709dfc(param_2,uVar4,param_8,bVar9,uVar3,param_14);
    }
    else {
      if ((((param_1 != 0x6429) && (param_1 != 0x64d3)) && (param_1 != 0x17)) && (param_1 != 9)) {
        *(byte *)(iVar6 + 0x8f) = bVar9;
        *(undefined1 *)(iVar6 + 0x90) = uVar2;
        *(undefined1 *)(iVar6 + 0x91) = 0;
        *(undefined1 *)(iVar6 + 0x92) = 0;
        *(undefined1 *)(iVar6 + 0x93) = uVar1;
        *(undefined1 *)(iVar6 + 0x94) = 0;
        *(undefined1 *)(iVar6 + 0x95) = 0;
        return param_2;
      }
      param_2 = FUN_43709e8c(param_1,uVar5);
      if ((param_1 == 0x17) && (param_14 == '\x01')) {
        param_2 = param_2 + param_3 & 0xff;
      }
    }
    *(byte *)(iVar6 + 0x8f) = bVar9;
    *(undefined1 *)(iVar6 + 0x90) = uVar2;
    *(undefined1 *)(iVar6 + 0x91) = 0;
    *(undefined1 *)(iVar6 + 0x92) = 0;
    *(char *)(iVar6 + 0x93) = (char)param_2;
    *(undefined1 *)(iVar6 + 0x94) = 0;
    *(undefined1 *)(iVar6 + 0x95) = 0;
  }
  return param_2;
}

