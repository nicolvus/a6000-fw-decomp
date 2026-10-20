/* S41: read-only exports. */

/* 437fefb8 */

void FUN_437fefb8(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 auStack_1c [2];
  
  iVar1 = FUN_4390406c(DAT_437ff024,auStack_1c);
  if (iVar1 != 0) {
    FUN_437fed58(3,9,1,DAT_437ff028 + 0x437fefdc,iVar1);
    FUN_43902718(DAT_437ff02c + 0x437fefe6,iVar1);
  }
  FUN_43b0091c(auStack_1c[0],param_1);
  FUN_439c5320(auStack_1c[0],param_2,param_3);
  iVar1 = FUN_4356120c(DAT_437ff024,auStack_1c[0]);
  if (iVar1 != 0) {
    FUN_437fed58(3,9,1,DAT_437ff030 + 0x437ff014,iVar1);
    FUN_43902718(DAT_437ff034 + 0x437ff01e,iVar1);
  }
  return;
}


/* 43806e68 */

void FUN_43806e68(void)

{
  int iVar1;
  undefined1 auStack_1c [20];
  
  iVar1 = DAT_43806e8c + 0x43806e76;
  FUN_43acac1a(auStack_1c,*(undefined4 *)(iVar1 + DAT_43806e90));
  FUN_43acac02(*(undefined4 *)(iVar1 + DAT_43806e94),0x69,auStack_1c);
  return;
}


/* 43805930 */

void FUN_43805930(int *param_1,char *param_2,undefined4 param_3)

{
  char cVar1;
  int iVar2;
  undefined1 auStack_30 [2];
  undefined2 uStack_2e;
  
  if (param_1[0x15a] != 1) {
    return;
  }
  if ((*(byte *)(*(int *)(DAT_43805adc + 0x43805946 + DAT_43805ae0) + 0x42) & 1) != 0) {
    return;
  }
  if ((char)param_1[0x3a9] != '\0') {
    return;
  }
  cVar1 = *param_2;
  if ((cVar1 == '\0') || (cVar1 == '\x02')) {
    iVar2 = FUN_4378f9b4();
    if ((*(short *)(*(int *)(iVar2 + 8) + 0x26c) == 0x142) && (*(short *)(param_2 + 2) == 0x301b)) {
      *(undefined1 *)((int)param_1 + 0x57e) = 1;
    }
    switch(*(short *)(param_2 + 2)) {
    case 0x3000:
    case 0x3003:
    case 0x300a:
    case 0x300c:
    case 0x3020:
    case 0x3021:
      if (((short)param_1[0x160] != *(short *)(param_2 + 2)) &&
         (*(short *)((int)param_1 + 0x582) != 0x3006)) {
        *(undefined1 *)(param_1 + 0x161) = 1;
      }
      FUN_439c5320(auStack_30,param_2,0x18);
      uStack_2e = 0x3006;
      *param_1 = 0;
      FUN_43805870(param_1,auStack_30,0x18);
      *(undefined2 *)((int)param_1 + 0x582) = uStack_2e;
      break;
    case 0x3001:
    case 0x3002:
    case 0x3004:
    case 0x3005:
    case 0x3006:
    case 0x3007:
    case 0x3008:
    case 0x3009:
    case 0x300b:
    case 0x300d:
    case 0x3010:
    case 0x3011:
    case 0x3012:
    case 0x3013:
    case 0x3014:
    case 0x3015:
    case 0x3016:
    case 0x3017:
    case 0x3018:
    case 0x3019:
    case 0x301a:
    case 0x301c:
    case 0x301d:
    case 0x301e:
    case 0x301f:
    case 0x3023:
    case 0x3024:
    case 0x3025:
    case 0x3026:
    case 0x3027:
    case 0x3028:
    case 0x3029:
    case 0x302a:
    case 0x302b:
    case 0x302c:
    case 0x302d:
    case 0x302e:
    case 0x3030:
      if (*param_1 != 1) break;
    case 0x300e:
      FUN_43805870(param_1,param_2,param_3);
      *(undefined2 *)((int)param_1 + 0x582) = *(undefined2 *)(param_2 + 2);
      break;
    default:
      iVar2 = DAT_43805ae4 + 0x43805a6a;
      FUN_43805604(3,0xd,1,DAT_43805ae8 + 0x43805a70,*param_2,iVar2,0x5c8);
      FUN_43902718(DAT_43805aec + 0x43805a80,*param_2,iVar2,0x5c8);
      FUN_43805604(5,0,1,DAT_43805af0 + 0x43805a8e,iVar2,0x5c9);
      FUN_43902718(DAT_43805af4 + 0x43805aa0,iVar2,0x5c9);
      break;
    case 0x301b:
    case 0x3022:
      FUN_43805870(param_1,param_2,param_3);
      *(undefined2 *)((int)param_1 + 0x582) = *(undefined2 *)(param_2 + 2);
      *param_1 = 1;
    }
  }
  else {
    iVar2 = DAT_43805afc + 0x43805aba;
    FUN_43805604(3,0xd,1,DAT_43805af8 + 0x43805ab6,cVar1,iVar2,0x5ce);
    FUN_43902718(DAT_43805b00 + 0x43805ac8,*param_2,iVar2,0x5ce);
  }
  *(undefined2 *)(param_1 + 0x160) = *(undefined2 *)(param_2 + 2);
  return;
}


/* 437949f8 */

void FUN_437949f8(int param_1,undefined4 param_2,undefined4 param_3)

{
  ushort uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uStack_c;
  undefined4 uStack_8;
  
  uVar1 = *(ushort *)(*(int *)(DAT_43794a3c + 0x43794a0e + DAT_43794a40) + 0x14);
  uVar3 = (uint)uVar1;
  uStack_c = *(ushort *)(*(int *)(param_1 + 8) + 0xc6) + 100;
  if ((uVar1 & 0x8000) != 0) {
    uVar3 = uVar3 & 0xffff7fff;
    uStack_c = uVar3;
  }
  uStack_8 = param_3;
  FUN_43ae915a(0x1004,500,&uStack_c,uVar3,param_1);
  uVar2 = FUN_43ae9154(uStack_c);
  thunk_FUN_43b4a69c(0x203c,uVar2);
  return;
}

